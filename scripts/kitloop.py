"""kit loop: drive a project's agent pull requests from ticket to ready-for-human.

    kit loop run [path]                one tick: start ready tickets, then move every agent PR one step
    kit loop run [path] --watch 300    tick every five minutes until stopped
    kit loop run [path] --until-done   tick until every ticket waits on you, then report each one
    kit loop run [path] --dry-run      print what each PR would do next; run and change nothing
    kit loop status [path]             each agent PR, its state and what it has cost

The loop itself is this script: it spends no model tokens. Checking GitHub costs nothing, so it
checks as often as it likes, and starts a model only when there is something new to judge: a
ticket to build, a red CI run to fix, a new commit to review. Each model run is its own short
headless process, with a fresh context, a dollar or time cap, and whichever harness and model
~/.spec-to-ship/models.json gives that role. Its state lives on the pull request (labels and one
marker comment), so any machine, or a CI job, can pick up where another stopped.
"""

from __future__ import annotations

import concurrent.futures
import datetime
import fcntl
import json
import pathlib
import re
import shutil
import subprocess
import sys
import threading
import time

MARK = "<!-- kit-loop "
LOOP_LABEL, STUCK_LABEL, READY_LABEL = "agent-loop", "agent-stuck", "ready-for-human"
DEFAULTS = {"max_parallel": 2, "max_rounds": 3, "max_ci_fixes": 3, "per_pr_usd": 10.0,
            "per_run_usd": 3.0, "timeout_min": 45}
# Paths that make a change a one-way door whatever the reviewer thinks: the app's identity,
# its permissions and its signing. A project adds its own in issue-tracker.md.
ONE_WAY_PATHS = ["android/app/build.gradle*", "android/app/src/main/AndroidManifest.xml",
                 "ios/Runner/Info.plist", "ios/Runner.xcodeproj/project.pbxproj",
                 "ios/Runner/*.entitlements"]


class LoopError(Exception):
    pass


# ---------------------------------------------------------------- decisions (pure, tested)

def decide(pr: dict, ci: str, st: dict, lim: dict) -> tuple:
    """The next step for one agent PR. Pure: the same inputs always give the same step, so the
    validator can test every branch without GitHub or a model.

    pr: {state, labels, head, mergeable}; ci: pass | fail | pending | none;
    st: the PR's marker-comment state; lim: the project's limits."""
    if pr["state"] in ("MERGED", "CLOSED"):
        return ("none",) if st.get("cleaned") else ("cleanup",)
    if READY_LABEL in pr["labels"]:
        return ("none",)  # the human's turn; removing the label hands it back
    if st.get("spent", 0) >= lim["per_pr_usd"]:
        return ("stuck", f"spent ${st['spent']:.2f} of its ${lim['per_pr_usd']:g} budget")
    if pr["mergeable"] == "CONFLICTING":
        if st.get("conflict_fixes", 0) >= 2:
            return ("stuck", "still conflicts with the base branch after two attempts")
        return ("fix", "conflict")
    if ci == "pending":
        return ("wait",)
    if ci == "fail":
        if st.get("ci_fixes", 0) >= lim["max_ci_fixes"]:
            return ("stuck", f"CI still red after {st['ci_fixes']} fixes")
        return ("fix", "ci")
    if st.get("reviewed_sha") != pr["head"]:
        if st.get("rounds", 0) >= lim["max_rounds"]:
            return ("stuck", f"not approved after {st['rounds']} review rounds")
        return ("review", "reviewer")
    if st.get("verdict") == "approve":
        if st.get("one_way") and not st.get("escalated"):
            return ("review", "escalation")
        return ("ready",)
    if st.get("verdict") == "changes":
        if st.get("fix_without_commit"):
            return ("stuck", "the builder disputed every finding and changed nothing")
        return ("fix", "review")
    if st.get("review_failures", 0) >= 2:
        return ("stuck", "the reviewer's answer could not be read twice in a row")
    return ("review", "reviewer")


def settled(open_pr_labels: list[list[str]], startable: int) -> bool:
    """Whether the loop has nothing left to do without a person: every open agent PR is
    labelled theirs, and no ready ticket can start."""
    return startable == 0 and all(READY_LABEL in labels for labels in open_pr_labels)


def builder_level(st: dict, ladder_len: int) -> int:
    """Which rung of the builder's ladder to use: start cheap, climb on evidence of difficulty."""
    level = (1 if st.get("points", 0) >= 8 else 0) + (st.get("ci_fixes", 0) >= 2) \
        + (st.get("rounds", 0) >= 2)
    return min(level, ladder_len - 1)


def parse_verdict(text: str) -> dict | None:
    """The reviewer's last JSON object carrying a verdict, fenced or bare."""
    candidates = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", text or "", re.S)
    candidates += re.findall(r"(\{\s*\"verdict\".*\})", text or "", re.S)
    for c in reversed(candidates):
        try:
            v = json.loads(c)
        except json.JSONDecodeError:
            continue
        if isinstance(v, dict) and v.get("verdict") in ("approve", "changes"):
            v.setdefault("findings", [])
            blocking = [f for f in v["findings"] if f.get("severity") in ("blocker", "major")]
            if v["verdict"] == "approve" and blocking:
                v["verdict"] = "changes"  # an approval that lists a blocker is not one
            return v
    return None


def ci_bucket(checks: list[dict]) -> str:
    buckets = {c.get("bucket") for c in checks}
    if not checks:
        return "none"
    if buckets & {"fail", "cancel"}:
        return "fail"
    if "pending" in buckets:
        return "pending"
    return "pass"


def blocked_by(body: str) -> list[int]:
    return [int(n) for n in re.findall(r"[Bb]locked by #(\d+)", body or "")]


def ticket_of(pr_body: str) -> int | None:
    m = re.search(r"(?:[Cc]loses|[Ff]ixes|[Rr]esolves) #(\d+)", pr_body or "")
    return int(m.group(1)) if m else None


def points_of(labels: list[str]) -> int:
    return max([int(l.split(":")[1]) for l in labels if re.fullmatch(r"points:\d+", l)] or [0])


def slug(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40] or "ticket"


# ---------------------------------------------------------------- the project

class Project:
    def __init__(self, root: pathlib.Path, kit, dry: bool):
        self.root, self.kit, self.dry = root, kit, dry
        self.models = kit.load_models()
        if not self.models or not self.models.get("loop"):
            raise LoopError("no loop models configured: ask your agent to configure models "
                            "(the configure-models skill), which writes ~/.spec-to-ship/models.json")
        errs = kit.check_models(self.models)
        if errs:
            raise LoopError("models.json is invalid:\n  - " + "\n  - ".join(errs))
        info = self.gh_json(["repo", "view", "--json", "nameWithOwner,defaultBranchRef"])
        self.repo = info["nameWithOwner"]
        self.base = info["defaultBranchRef"]["name"]
        self.state_dir = kit.STATE / "loop" / self.repo.replace("/", "__")
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.lim = dict(DEFAULTS)
        self.lim.update({k: v for k, v in (self.models.get("budget") or {}).items()
                         if k in ("per_pr_usd", "per_run_usd")})
        self.one_way = list(ONE_WAY_PATHS)
        self.worktrees = root.parent / f"{root.name}-worktrees"
        self.read_project_settings()
        self.ledger_lock = threading.Lock()

    # -- settings from docs/agents/issue-tracker.md, "## Agent loop" table
    def read_project_settings(self) -> None:
        f = self.root / "docs/agents/issue-tracker.md"
        if not f.exists():
            raise LoopError("docs/agents/issue-tracker.md is missing: run /fk-setup with GitHub as the tracker")
        section = f.read_text().split("## Agent loop", 1)
        if len(section) < 2:
            return
        for line in section[1].split("\n## ", 1)[0].splitlines():
            cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
            if len(cells) != 2:
                continue
            key, val = cells[0].lower(), cells[1]
            num = re.match(r"^\d+(\.\d+)?$", val)
            if key == "max parallel builds" and num:
                self.lim["max_parallel"] = int(float(val))
            elif key == "max review rounds" and num:
                self.lim["max_rounds"] = int(float(val))
            elif key == "max ci fixes" and num:
                self.lim["max_ci_fixes"] = int(float(val))
            elif key == "one-way door paths" and val and not val.startswith("<"):
                self.one_way += [p.strip() for p in val.split(",") if p.strip()]
            elif key == "worktrees" and val and not val.startswith("<"):
                self.worktrees = (self.root / val).resolve()

    # -- shell
    def run(self, argv: list[str], cwd: pathlib.Path | None = None, check: bool = True,
            stdin: str | None = None) -> subprocess.CompletedProcess:
        r = subprocess.run(argv, cwd=cwd or self.root, capture_output=True, text=True, input=stdin)
        if check and r.returncode != 0:
            raise LoopError(f"{' '.join(argv[:4])} failed: {(r.stderr or r.stdout).strip()[:400]}")
        return r

    def gh(self, args: list[str], check: bool = True, stdin: str | None = None) -> str:
        return self.run(["gh", *args], check=check, stdin=stdin).stdout

    def gh_json(self, args: list[str]):
        return json.loads(self.gh(args) or "null")

    def mutate(self, what: str, fn, *a) -> None:
        """Every change to GitHub or the disk goes through here, so --dry-run changes nothing."""
        if self.dry:
            print(f"    would {what}")
            return
        fn(*a)

    # -- marker comment: the PR's loop state, readable by any machine
    def load_state(self, number: int) -> tuple[dict, str | None]:
        comments = self.gh_json(["pr", "view", str(number), "--json", "comments"])["comments"]
        for c in reversed(comments):
            if c["body"].startswith(MARK):
                m = re.match(re.escape(MARK) + r"(\{.*?\}) -->", c["body"], re.S)
                cid = re.search(r"issuecomment-(\d+)", c.get("url", ""))
                if m:
                    return json.loads(m.group(1)), cid.group(1) if cid else None
        return {}, None

    def save_state(self, number: int, st: dict, cid: str | None, line: str) -> None:
        body = (f"{MARK}{json.dumps(st, separators=(',', ':'))} -->\n"
                f"**Agent loop:** {line}\n\nRound {st.get('rounds', 0)} · "
                f"spent ${st.get('spent', 0):.2f}" + (" (some runs unpriced)" if st.get("unpriced") else ""))
        if self.dry:
            print(f"    would record state: {line}")
            return
        if cid:
            self.gh(["api", "-X", "PATCH", f"repos/{self.repo}/issues/comments/{cid}", "--input", "-"],
                    stdin=json.dumps({"body": body}))
        else:
            self.gh(["pr", "comment", str(number), "--body-file", "-"], stdin=body)

    # -- notifications
    def notify(self, title: str, message: str) -> None:
        print(f"  ▶ {title}: {message}")
        cmd = self.models.get("notify")
        if not cmd and sys.platform == "darwin" and shutil.which("osascript"):
            safe = lambda s: s.replace('"', "'").replace("\\", "/")
            cmd = ["osascript", "-e", f'display notification "{safe(message)}" with title "{safe(title)}"']
        elif cmd:
            cmd = [c.replace("{title}", title).replace("{message}", message) for c in cmd]
        if cmd and not self.dry:
            subprocess.run(cmd, capture_output=True)

    # -- one model run
    def run_role(self, loop_role: str, level: int, prompt: str, cwd: pathlib.Path,
                 profile: str, ctx: str) -> dict:
        spec = self.models["loop"].get(loop_role)
        if not spec:
            raise LoopError(f"models.json has no loop.{loop_role}")
        hid, ladder = spec["harness"], spec["ladder"]
        step = ladder[min(level, len(ladder) - 1)]
        model = step if isinstance(step, str) else step["model"]
        effort = (None if isinstance(step, str) else step.get("effort")) or spec.get("effort")
        budget = float(spec.get("budget_usd", self.lim["per_run_usd"]))
        argv = self.kit.headless_argv(hid, model, prompt, profile, budget, effort)
        if self.dry:
            print(f"    would run {loop_role} on {hid}/{model}" + (f" ({effort})" if effort else "")
                  + f" in {cwd.name}, capped at ${budget:g}")
            return {"ok": True, "text": "", "cost": 0.0, "cost_known": True, "dry": True}
        if not shutil.which(argv[0]):
            raise LoopError(f"{argv[0]} is not installed, but models.json runs loop.{loop_role} on it")
        start = time.time()
        try:
            r = subprocess.run(argv, cwd=cwd, capture_output=True, text=True,
                               timeout=int(spec.get("timeout_min", self.lim["timeout_min"])) * 60)
            out, code = r.stdout, r.returncode
        except subprocess.TimeoutExpired as e:
            out, code = (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or ""), -1
        run = self.kit.parse_run(hid, out)
        known = run["cost"] is not None
        cost = float(run["cost"]) if known else float(spec.get("est_cost_usd", 0))
        mismatch = bool(run["models"]) and not any(model.split("/")[-1] in m for m in run["models"])
        entry = {"ts": datetime.datetime.now().isoformat(timespec="seconds"), "ctx": ctx,
                 "role": loop_role, "harness": hid, "model": model, "effort": effort,
                 "ok": code == 0, "secs": int(time.time() - start), "cost": cost,
                 "cost_known": known, "answered_by": run["models"], "model_mismatch": mismatch}
        with self.ledger_lock, open(self.state_dir / "runs.jsonl", "a") as f:
            f.write(json.dumps(entry) + "\n")
        if mismatch:
            print(f"  ! asked for {model}, answered by {', '.join(run['models'])}")
        return {"ok": code == 0, "text": run["text"], "cost": cost, "cost_known": known}

    # -- worktrees
    def worktree(self, branch: str, create_from: str | None = None) -> pathlib.Path:
        path = self.worktrees / branch
        if path.exists():
            if not self.dry:
                self.run(["git", "fetch", "-q", "origin"], cwd=path, check=False)
                self.run(["git", "merge", "-q", "--ff-only", f"origin/{branch}"], cwd=path, check=False)
            return path
        if self.dry:
            return path
        self.worktrees.mkdir(parents=True, exist_ok=True)
        self.run(["git", "fetch", "-q", "origin"])
        if create_from:
            self.run(["git", "worktree", "add", "-q", "-b", branch, str(path), create_from])
        else:
            self.run(["git", "worktree", "add", "-q", "-B", branch, str(path), f"origin/{branch}"])
            self.run(["git", "branch", "-q", "--set-upstream-to", f"origin/{branch}", branch], cwd=path)
        exclude = pathlib.Path(self.run(["git", "rev-parse", "--git-common-dir"], cwd=path).stdout.strip())
        exclude = (path / exclude if not exclude.is_absolute() else exclude) / "info/exclude"
        exclude.parent.mkdir(parents=True, exist_ok=True)
        if ".kit-loop/" not in (exclude.read_text() if exclude.exists() else ""):
            with open(exclude, "a") as f:
                f.write("\n.kit-loop/\n")
        return path

    def prompt(self, name: str, **subs) -> str:
        text = (self.kit.KIT / "loop/prompts" / f"{name}.md").read_text()
        for k, v in subs.items():
            text = text.replace("{{" + k + "}}", str(v))
        return text

    def invoke(self, harness: str, skill: str, args: str) -> str:
        return self.kit.HARNESSES[harness]["headless"]["invoke"].replace("{skill}", skill) \
            .replace("{args}", args)

    # ---------------------------------------------------------------- build tickets

    def frontier(self) -> tuple[list[dict], list[tuple[dict, list[int]]]]:
        """The sprint's ready tickets that can start now, and those still waiting on open ones."""
        open_numbers = {i["number"] for i in self.gh_json(
            ["issue", "list", "--state", "open", "--limit", "1000", "--json", "number"])}
        ready = self.gh_json(["issue", "list", "--state", "open", "--label", "ready-for-agent",
                              "--search", "no:assignee", "--limit", "200",
                              "--json", "number,title,body,labels,milestone"])
        startable, blocked = [], []
        for t in sorted(ready, key=lambda t: t["number"]):
            if not (t.get("milestone") and t["milestone"].get("title", "").startswith("Sprint")):
                continue
            waits = sorted(set(blocked_by(t["body"])) & open_numbers)
            if waits:
                blocked.append((t, waits))
            else:
                startable.append(t)
        return startable, blocked

    def start_tickets(self, active: int) -> None:
        slots = self.lim["max_parallel"] - active
        if slots <= 0:
            return
        picks = self.frontier()[0][:slots]
        if not picks:
            return
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(picks)) as pool:
            for f in [pool.submit(self.build_ticket, t) for t in picks]:
                try:
                    f.result()
                except LoopError as e:
                    print(f"  ! {e}")

    def build_ticket(self, t: dict) -> None:
        n, title = t["number"], t["title"]
        labels = [l["name"] for l in t["labels"]]
        branch = f"{n}-{slug(title)}"
        print(f"  #{n} {title}: build")
        self.mutate(f"assign #{n} to you", self.gh, ["issue", "edit", str(n), "--add-assignee", "@me"])
        wt = self.worktree(branch, create_from=f"origin/{self.base}")
        st = {"ticket": n, "branch": branch, "points": points_of(labels), "rounds": 0, "spent": 0.0}
        body_file = ".kit-loop/pr-body.md"
        if not self.dry:
            (wt / ".kit-loop").mkdir(exist_ok=True)
            (wt / body_file).unlink(missing_ok=True)
        builder = self.models["loop"]["builder"]
        prompt = self.prompt("build", invoke=self.invoke(builder["harness"], "fk-build", f"#{n}"),
                             branch=branch, ticket=n, pr_body=body_file)
        run = self.run_role("builder", builder_level(st, len(builder["ladder"])), prompt, wt,
                            "write", f"#{n} build")
        st["spent"] += run["cost"]
        st["unpriced"] = not run["cost_known"]
        if self.dry:
            return
        body = (wt / body_file).read_text() if (wt / body_file).exists() else ""
        ahead = int(self.run(["git", "rev-list", "--count", f"origin/{self.base}..HEAD"], cwd=wt).stdout or 0)
        if body.startswith("BLOCKED:") or not ahead:
            reason = body.splitlines()[0] if body else "the builder made no commit"
            self.gh(["issue", "comment", str(n), "--body-file", "-"],
                    stdin=f"**Agent loop:** could not build this ticket. {reason}\n\n{(run['text'] or '')[-1500:]}")
            self.gh(["issue", "edit", str(n), "--add-label", f"{READY_LABEL},{STUCK_LABEL}",
                     "--remove-label", "ready-for-agent"])
            self.notify(f"#{n} needs you", reason[:180])
            return
        if f"#{n}" not in body:
            body = (body or f"Builds #{n}.") + f"\n\nCloses #{n}\n"
        self.run(["git", "push", "-q", "-u", "origin", branch], cwd=wt)
        url = self.gh(["pr", "create", "--base", self.base, "--head", branch, "--title",
                       f"{title} (#{n})", "--label", LOOP_LABEL, "--body-file", "-"], stdin=body).strip()
        number = int(url.rstrip("/").split("/")[-1])
        self.save_state(number, st, None, f"built #{n}; waiting for CI")

    # ---------------------------------------------------------------- drive PRs

    def agent_prs(self) -> list[dict]:
        return self.gh_json(["pr", "list", "--label", LOOP_LABEL, "--state", "all", "--limit", "40",
                             "--json", "number,title,state,body,headRefName,headRefOid,labels,mergeable,url"])

    def ci(self, number: int) -> tuple[str, list[dict]]:
        r = self.run(["gh", "pr", "checks", str(number), "--json", "bucket,name,link"], check=False)
        try:
            checks = json.loads(r.stdout or "[]")
        except json.JSONDecodeError:
            checks = []
        return ci_bucket(checks), checks

    def plan(self, p: dict) -> tuple | None:
        """Read one PR's state from GitHub and decide its next step. Costs no model tokens."""
        pr = {"state": p["state"], "labels": [l["name"] for l in p["labels"]],
              "head": p["headRefOid"], "mergeable": p.get("mergeable") or "UNKNOWN"}
        st, cid = self.load_state(p["number"])
        st.setdefault("ticket", ticket_of(p["body"]))
        st.setdefault("branch", p["headRefName"])
        ci, checks = ("none", []) if pr["state"] != "OPEN" else self.ci(p["number"])
        action = decide(pr, ci, st, self.lim)
        if action[0] in ("none", "wait"):
            return None
        print(f"  PR #{p['number']} {p['title']}: {' '.join(action)}")
        return (p, pr, st, cid, checks, action)

    def execute(self, planned: tuple) -> None:
        p, pr, st, cid, checks, action = planned
        getattr(self, f"do_{action[0]}")(p, pr, st, cid, checks, *action[1:])

    def do_cleanup(self, p, pr, st, cid, checks) -> None:
        wt, branch = self.worktrees / st["branch"], st["branch"]
        if wt.exists():
            self.mutate(f"remove worktree {wt.name}", self.run,
                        ["git", "worktree", "remove", "--force", str(wt)])
        self.mutate(f"delete local branch {branch}", self.run, ["git", "branch", "-D", branch], None, False)
        if pr["state"] == "MERGED":
            self.mutate(f"delete remote branch {branch}", self.run,
                        ["git", "push", "-q", "origin", "--delete", branch], None, False)
        st["cleaned"] = True
        self.save_state(p["number"], st, cid, "merged and cleaned up" if pr["state"] == "MERGED"
                        else "closed; worktree removed")

    def do_stuck(self, p, pr, st, cid, checks, reason) -> None:
        self.mutate("label it for you", self.gh, ["pr", "edit", str(p["number"]), "--add-label",
                                                  f"{READY_LABEL},{STUCK_LABEL}"])
        st["stopped"] = reason
        self.save_state(p["number"], st, cid, f"stopped: {reason}. Over to you.")
        self.notify(f"PR #{p['number']} is stuck", f"{reason}. {p['url']}")

    def do_ready(self, p, pr, st, cid, checks) -> None:
        self.mutate("label it ready for you", self.gh, ["pr", "edit", str(p["number"]),
                                                        "--add-label", READY_LABEL])
        self.save_state(p["number"], st, cid, f"approved: {st.get('summary', '')} Ready for you to test and merge.")
        self.notify(f"PR #{p['number']} is ready", f"{p['title']}: {st.get('summary', '')} {p['url']}")

    def do_fix(self, p, pr, st, cid, checks, kind) -> None:
        number, branch = p["number"], st["branch"]
        wt = self.worktree(branch)
        if kind == "ci":
            failed = [c for c in checks if c.get("bucket") in ("fail", "cancel")]
            logs = []
            for c in failed[:2]:
                m = re.search(r"/runs/(\d+)", c.get("link", ""))
                if m:
                    log = self.run(["gh", "run", "view", m.group(1), "--log-failed"], check=False).stdout
                    logs.append(f"### {c['name']}\n\n```\n{log[-6000:]}\n```")
            reason = "## CI failed\n\n" + ("\n\n".join(logs) or "No log could be fetched; run the "
                                           "project's analyze and test commands to reproduce.")
            st["ci_fixes"] = st.get("ci_fixes", 0) + 1
        elif kind == "conflict":
            reason = (f"## The branch conflicts with `{self.base}`\n\nRun `git fetch origin` and "
                      f"`git merge origin/{self.base}`, then call the Skill tool with "
                      f"`merge-conflicts` to resolve every conflict. Commit the merge.")
            st["conflict_fixes"] = st.get("conflict_fixes", 0) + 1
        else:
            reason = "## Review findings to fix\n\n```json\n" + json.dumps(
                [f for f in st.get("findings", []) if f.get("severity") in ("blocker", "major")]
                or st.get("findings", []), indent=1) + "\n```"
        notes = ".kit-loop/notes.md"
        if not self.dry:
            (wt / ".kit-loop").mkdir(exist_ok=True)
            (wt / notes).unlink(missing_ok=True)
        builder = self.models["loop"]["builder"]
        before = "" if self.dry else self.run(["git", "rev-parse", "HEAD"], cwd=wt).stdout.strip()
        run = self.run_role("builder", builder_level(st, len(builder["ladder"])),
                            self.prompt("fix", pr=number, ticket=st.get("ticket"), branch=branch,
                                        reason=reason, notes=notes),
                            wt, "write", f"PR #{number} fix {kind}")
        st["spent"] = st.get("spent", 0) + run["cost"]
        st["unpriced"] = st.get("unpriced") or not run["cost_known"]
        if self.dry:
            return
        after = self.run(["git", "rev-parse", "HEAD"], cwd=wt).stdout.strip()
        if (wt / notes).exists():
            self.gh(["pr", "comment", str(number), "--body-file", "-"],
                    stdin="**Builder disputes a finding:**\n\n" + (wt / notes).read_text())
        if after != before:
            self.run(["git", "push", "-q", "origin", f"HEAD:{branch}"], cwd=wt)
            st["fix_without_commit"] = False
            line = f"fixed {kind}; waiting for CI"
        else:
            st["fix_without_commit"] = kind == "review"
            line = f"tried to fix {kind}; nothing changed"
        self.save_state(number, st, cid, line)

    def do_review(self, p, pr, st, cid, checks, who) -> None:
        number, branch = p["number"], st["branch"]
        wt = self.worktree(branch)
        ticket = st.get("ticket")
        ticket_body = (self.gh_json(["issue", "view", str(ticket), "--json", "title,body"])
                       if ticket else {"title": "", "body": "(no ticket linked)"})
        diff = self.gh(["pr", "diff", str(number)], check=False)
        files = self.gh(["pr", "diff", str(number), "--name-only"], check=False).split()
        if len(diff) > 80000:
            diff = diff[:80000] + f"\n\n[diff truncated; files changed: {', '.join(files)}]"
        hit = [f for f in files if any(pathlib.PurePath(f).match(g) for g in self.one_way)]
        ci = ci_bucket(checks)
        escalation = ""
        if who == "escalation":
            escalation = ("The first reviewer approved this but flagged a one-way door: "
                          f"{st.get('one_way_reason', '')}. Yours is the decision that sticks. "
                          "Check that door hardest.")
        prompt = self.prompt(
            "review", who="escalation reviewer" if who == "escalation" else "reviewer",
            pr=number, ticket=ticket or "?",
            one_way=(f" These paths changed and always count as one: {', '.join(hit)}." if hit else ""),
            escalation=escalation,
            ticket_body=f"#{ticket} {ticket_body['title']}\n\n{ticket_body['body']}",
            ci={"pass": "Green.", "none": "No CI checks ran on this repo. Treat that as a finding "
                "for the human, not a reason to block."}.get(ci, ci), diff=diff)
        role = "escalation" if who == "escalation" else "reviewer"
        run = self.run_role(role, 0, prompt, wt, "read", f"PR #{number} {who}")
        st["spent"] = st.get("spent", 0) + run["cost"]
        st["unpriced"] = st.get("unpriced") or not run["cost_known"]
        if self.dry:
            return
        v = parse_verdict(run["text"])
        if not v:
            st["review_failures"] = st.get("review_failures", 0) + 1
            self.save_state(number, st, cid, "the reviewer's answer could not be read; will retry")
            return
        st.update({"review_failures": 0, "reviewed_sha": pr["head"], "verdict": v["verdict"],
                   "findings": v["findings"], "summary": v.get("summary", "")})
        if who == "escalation":
            st["escalated"] = True
        else:
            st["rounds"] = st.get("rounds", 0) + 1
            st["escalated"] = False
            st["one_way"] = bool(v.get("one_way_door")) or bool(hit)
            st["one_way_reason"] = v.get("one_way_reason") or (f"changes {', '.join(hit)}" if hit else "")
        lines = [f"**{'Escalation review' if who == 'escalation' else 'Review'}: "
                 f"{v['verdict']}.** {v.get('summary', '')}", ""]
        for f in v["findings"]:
            lines.append(f"- **{f.get('severity', '?')}** `{f.get('file', '')}:{f.get('line', '')}` "
                         f"({f.get('criterion', '')}): {f.get('problem', '')} → {f.get('fix', '')}")
        if st.get("one_way") and who != "escalation":
            lines.append(f"\nOne-way door: {st['one_way_reason']}")
        self.gh(["pr", "comment", str(number), "--body-file", "-"], stdin="\n".join(lines))
        self.save_state(number, st, cid, f"{who} said {v['verdict']}")

    # ---------------------------------------------------------------- one tick

    def tick(self, build: bool) -> None:
        prs = self.agent_prs()
        if not self.dry:
            self.gh(["label", "create", LOOP_LABEL, "--color", "5319E7", "--force",
                     "--description", "Driven by kit loop"], check=False)
            self.gh(["label", "create", STUCK_LABEL, "--color", "B60205", "--force",
                     "--description", "The loop stopped; needs a person"], check=False)
        active = [p for p in prs if p["state"] == "OPEN"
                  and READY_LABEL not in [l["name"] for l in p["labels"]]]
        steps = []
        for p in prs:
            try:
                steps.append(self.plan(p))
            except LoopError as e:
                print(f"  ! PR #{p['number']}: {e}")
        steps = [s for s in steps if s]
        # Reviews are short: run them one after another so each after the first reads the prompt
        # cache the previous one wrote, several times cheaper than a cold start. Fixes are long
        # and independent, so they run in parallel meanwhile.
        reviews = [s for s in steps if s[5][0] == "review"]
        others = [s for s in steps if s[5][0] != "review"]
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, self.lim["max_parallel"])) as pool:
            futures = [pool.submit(self.execute, s) for s in others]
            for s in reviews:
                try:
                    self.execute(s)
                except LoopError as e:
                    print(f"  ! PR #{s[0]['number']}: {e}")
            for f in futures:
                try:
                    f.result()
                except LoopError as e:
                    print(f"  ! {e}")
        if build:
            self.start_tickets(len(active))

    def progress(self, build: bool) -> tuple[bool, list[dict], list[tuple[dict, list[int]]]]:
        """Read GitHub after a tick: whether the loop is done, the agent PRs, the blocked tickets."""
        prs = self.agent_prs()
        startable, blocked = self.frontier() if build else ([], [])
        open_labels = [[l["name"] for l in p["labels"]] for p in prs if p["state"] == "OPEN"]
        return settled(open_labels, len(startable)), prs, blocked

    def report(self, since: datetime.datetime, prs: list[dict],
               blocked: list[tuple[dict, list[int]]]) -> None:
        """One entry per ticket the person now has to act on, then what to do next."""
        runs = []
        ledger = self.state_dir / "runs.jsonl"
        if ledger.exists():
            for line in ledger.read_text().splitlines():
                try:
                    e = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if datetime.datetime.fromisoformat(e["ts"]) >= since.replace(microsecond=0):
                    runs.append(e)
        theirs = []
        for p in prs:
            labels = [l["name"] for l in p["labels"]]
            if p["state"] == "OPEN" and READY_LABEL in labels:
                theirs.append((p, self.load_state(p["number"])[0],
                               "stuck" if STUCK_LABEL in labels else "ready"))
        ready = [p for p, _, where in theirs if where == "ready"]
        stuck = [p for p, _, where in theirs if where == "stuck"]
        unbuilt = self.gh_json(["issue", "list", "--state", "open", "--label", STUCK_LABEL,
                                "--json", "number,title"]) or []
        print(f"\nDone: {len(ready)} ready for you, {len(stuck)} stuck, {len(unbuilt)} could not be "
              f"built, {len(blocked)} blocked until you merge. This run: {len(runs)} model runs, "
              f"${sum(e.get('cost', 0) for e in runs):.2f}.\n")
        for p, st, where in sorted(theirs, key=lambda e: e[2] == "stuck"):
            print(f"PR #{p['number']} {where}: {p['title']}")
            print(f"    {st.get('verdict') or 'no verdict'} after {st.get('rounds', 0)} review round(s), "
                  f"{st.get('ci_fixes', 0)} CI fix(es), ${st.get('spent', 0):.2f}")
            if st.get("stopped"):
                print(f"    stopped: {st['stopped']}")
            if st.get("summary"):
                print(f"    {st['summary']}")
            open_findings = [f for f in st.get("findings", []) if f.get("severity") not in ("blocker", "major")]
            if open_findings:
                print(f"    {len(open_findings)} minor finding(s) left for you to judge")
            if st.get("one_way"):
                print(f"    one-way door: {st.get('one_way_reason', '')}")
            print(f"    {p['url']}")
        for t in unbuilt:
            print(f"Ticket #{t['number']} could not be built: {t['title']} (its comments say why)")
        for t, waits in blocked:
            print(f"Ticket #{t['number']} waits on {', '.join(f'#{n}' for n in waits)}: {t['title']}")
        merge = ", ".join(f"#{p['number']}" for p in ready) or "nothing"
        print(f"\nNext:      test and merge the ready pull requests"
              f"\nDoes:      each is reviewed and green; merging closes its ticket"
              f"\nPaste:     {'kit loop run --until-done' if blocked else '/fk-sprint qa'}"
              f"\nNeeds you: merge {merge}" + (", and unstick the stuck ones" if stuck or unbuilt else "")
              + (f"\nThen:      kit loop run --until-done builds the {len(blocked)} they unblock"
                 if blocked else "\nThen:      /fk-sprint qa gates the build before anyone outside sees it"))

    def status(self) -> None:
        for p in self.agent_prs():
            st, _ = self.load_state(p["number"])
            labels = [l["name"] for l in p["labels"]]
            where = ("merged" if p["state"] == "MERGED" else "closed" if p["state"] == "CLOSED"
                     else "stuck" if STUCK_LABEL in labels else "ready for you" if READY_LABEL in labels
                     else st.get("verdict") or "building")
            print(f"#{p['number']:<5} {where:<14} round {st.get('rounds', 0)}  "
                  f"${st.get('spent', 0):.2f}  {p['title']}")


def main(args, kit) -> int:
    root = pathlib.Path(args.path).resolve()
    if not (root / ".git").exists():
        raise SystemExit(f"{root} is not the root of a git repo")
    for tool in ("gh", "git"):
        if not shutil.which(tool):
            raise SystemExit(f"kit loop needs {tool} on PATH")
    try:
        project = Project(root, kit, args.dry_run)
    except LoopError as e:
        raise SystemExit(str(e))
    if args.action == "status":
        project.status()
        return 0
    lock = open(project.state_dir / "lock", "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("another kit loop is already running on this repo")
        return 1
    since = datetime.datetime.now()
    while True:
        print(f"[{datetime.datetime.now():%H:%M}] {project.repo}")
        try:
            project.tick(build=not args.no_build)
            if args.until_done:
                done, prs, blocked = project.progress(build=not args.no_build)
                # A dry run changes nothing, so it would never settle: one tick, then the report.
                if done or args.dry_run:
                    project.report(since, prs, blocked)
                    return 0
        except LoopError as e:
            print(f"  ! {e}")
        if not (args.watch or args.until_done):
            return 0
        time.sleep(args.watch or 300)
