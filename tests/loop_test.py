#!/usr/bin/env python3
"""Tests for kit loop and kit models: the pure decision table, verdict parsing, model pinning
into every harness, and one ticket driven end to end against a fake GitHub and a fake model CLI.

    python3 tests/loop_test.py      prints one line per failure and exits non-zero on any
"""

import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import kitloop  # noqa: E402

FAIL: list[str] = []


def expect(label: str, got, want) -> None:
    if got != want:
        FAIL.append(f"{label}: got {got!r}, want {want!r}")


# ---------------------------------------------------------------- decide()

LIM = {"per_pr_usd": 10, "max_rounds": 3, "max_ci_fixes": 3}
OPEN = {"state": "OPEN", "labels": ["agent-loop"], "head": "h2", "mergeable": "MERGEABLE"}
CASES = [
    ("merged, not cleaned", {**OPEN, "state": "MERGED"}, "none", {}, ("cleanup",)),
    ("merged, cleaned", {**OPEN, "state": "MERGED"}, "none", {"cleaned": True}, ("none",)),
    ("human's turn", {**OPEN, "labels": ["agent-loop", "ready-for-human"]}, "fail", {}, ("none",)),
    ("over budget", OPEN, "pass", {"spent": 12}, "stuck"),
    ("conflict", {**OPEN, "mergeable": "CONFLICTING"}, "pass", {}, ("fix", "conflict")),
    ("conflict twice", {**OPEN, "mergeable": "CONFLICTING"}, "pass", {"conflict_fixes": 2}, "stuck"),
    ("ci pending", OPEN, "pending", {}, ("wait",)),
    ("ci red", OPEN, "fail", {"ci_fixes": 1}, ("fix", "ci")),
    ("ci red too often", OPEN, "fail", {"ci_fixes": 3}, "stuck"),
    ("new commit", OPEN, "pass", {"reviewed_sha": "h1", "rounds": 1}, ("review", "reviewer")),
    ("no CI, new commit", OPEN, "none", {}, ("review", "reviewer")),
    ("rounds used up", OPEN, "pass", {"reviewed_sha": "h1", "rounds": 3}, "stuck"),
    ("approved", OPEN, "pass", {"reviewed_sha": "h2", "verdict": "approve"}, ("ready",)),
    ("approved, one-way door", OPEN, "pass",
     {"reviewed_sha": "h2", "verdict": "approve", "one_way": True}, ("review", "escalation")),
    ("escalation approved", OPEN, "pass",
     {"reviewed_sha": "h2", "verdict": "approve", "one_way": True, "escalated": True}, ("ready",)),
    ("changes asked", OPEN, "pass", {"reviewed_sha": "h2", "verdict": "changes"}, ("fix", "review")),
    ("builder disputed all", OPEN, "pass",
     {"reviewed_sha": "h2", "verdict": "changes", "fix_without_commit": True}, "stuck"),
]
for label, pr, ci, st, want in CASES:
    got = kitloop.decide(pr, ci, st, LIM)
    expect(f"decide: {label}", got[0] if isinstance(want, str) else got, want)

expect("ladder: easy ticket", kitloop.builder_level({"points": 3}, 2), 0)
expect("ladder: 8-pointer starts higher", kitloop.builder_level({"points": 8}, 2), 1)
expect("ladder: capped at its top", kitloop.builder_level({"points": 8, "rounds": 2, "ci_fixes": 2}, 2), 1)

v = kitloop.parse_verdict('done\n```json\n{"verdict": "approve", "findings": '
                          '[{"severity": "blocker", "problem": "x"}]}\n```')
expect("verdict: approval listing a blocker becomes changes", v and v["verdict"], "changes")
expect("verdict: bare JSON", (kitloop.parse_verdict('ok {"verdict": "approve"}') or {}).get("verdict"), "approve")
expect("verdict: unreadable", kitloop.parse_verdict("looks fine to me"), None)
expect("ticket from body", kitloop.ticket_of("Adds it.\n\nCloses #42"), 42)
expect("blocked by", kitloop.blocked_by("Blocked by #3.\nblocked by #9"), [3, 9])
expect("ci: one red check", kitloop.ci_bucket([{"bucket": "pass"}, {"bucket": "fail"}]), "fail")
expect("settled: nothing open, nothing to start", kitloop.settled([], 0), True)
expect("settled: every PR is the human's", kitloop.settled([["agent-loop", "ready-for-human"]], 0), True)
expect("settled: a PR still in flight", kitloop.settled([["agent-loop"], ["ready-for-human"]], 0), False)
expect("settled: a ticket could start", kitloop.settled([["ready-for-human"]], 1), False)


# ---------------------------------------------------------------- end to end

def sh(argv, cwd, env=None, check=True):
    r = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, env=env)
    if check and r.returncode != 0:
        raise RuntimeError(f"{' '.join(argv)}: {r.stderr or r.stdout}")
    return r


def e2e() -> None:
    tmp = pathlib.Path(tempfile.mkdtemp())
    try:
        home, origin, repo, fakebin = tmp / "home", tmp / "origin.git", tmp / "app", tmp / "bin"
        for d in (home, fakebin):
            d.mkdir()
        sh(["git", "init", "-q", "--bare", "-b", "main", str(origin)], tmp)
        sh(["git", "clone", "-q", str(origin), str(repo)], tmp)
        for k, v in (("user.email", "t@example.com"), ("user.name", "Test")):
            sh(["git", "config", k, v], repo)
        (repo / "docs/agents").mkdir(parents=True)
        shutil.copy(ROOT / "skills/fk-setup/template/docs/agents/issue-tracker.md",
                    repo / "docs/agents/issue-tracker.md")
        sh(["git", "add", "-A"], repo)
        sh(["git", "commit", "-qm", "init"], repo)
        sh(["git", "push", "-q", "-u", "origin", "main"], repo)

        state = tmp / "gh.json"
        state.write_text(json.dumps({"issues": [
            {"number": 7, "title": "Show the item list", "state": "open", "assignees": [],
             "labels": ["ready-for-agent", "type:feature", "points:3"], "milestone": "Sprint 01",
             "body": "## Acceptance criteria\n\n1. The list shows."},
            {"number": 8, "title": "Blocked one", "state": "open", "assignees": [],
             "labels": ["ready-for-agent", "points:2"], "milestone": "Sprint 01",
             "body": "Blocked by #7."}], "prs": []}))
        for name, target in (("gh", "fake_gh.py"), ("claude", "fake_claude.py")):
            f = fakebin / name
            f.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{ROOT / "tests" / target}" "$@"\n')
            f.chmod(0o755)
        env = {**os.environ, "HOME": str(home), "SPEC_TO_SHIP_HOME": str(home / ".spec-to-ship"),
               "SPEC_TO_SHIP_SKIP_CLI": "1", "FAKE_GH_STATE": str(state),
               "PATH": f"{fakebin}{os.pathsep}{os.environ['PATH']}",
               "GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "t@example.com",
               "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "t@example.com"}
        kit = [sys.executable, str(ROOT / "scripts/kit.py")]

        models = tmp / "models.json"
        models.write_text(json.dumps({"version": 1, "notify": ["true"], "loop": {
            "builder": {"harness": "claude", "ladder": ["sonnet", "opus"]},
            "reviewer": {"harness": "claude", "ladder": ["haiku"]},
            "escalation": {"harness": "claude", "ladder": ["opus"]}}}))
        r = sh(kit + ["models", "set", str(models)], tmp, env, check=False)
        expect("e2e: models set", r.returncode, 0)

        def tick():
            r = sh(kit + ["loop", "run", str(repo)], tmp, env, check=False)
            if r.returncode != 0:
                FAIL.append(f"e2e: tick failed: {r.stderr or r.stdout}")
            return r.stdout

        dry = sh(kit + ["loop", "run", str(repo), "--dry-run"], tmp, env, check=False).stdout
        expect("e2e: dry run names the build", "would run builder on claude/sonnet" in dry, True)
        expect("e2e: dry run changed nothing", json.loads(state.read_text())["prs"], [])

        tick()  # builds #7 (not #8, which #7 blocks) and opens the PR
        s = json.loads(state.read_text())
        expect("e2e: one PR opened", len(s["prs"]), 1)
        pr = s["prs"][0] if s["prs"] else {}
        expect("e2e: PR closes the ticket", "Closes #7" in pr.get("body", ""), True)
        expect("e2e: ticket assigned", s["issues"][0]["assignees"], ["me"])
        expect("e2e: blocked ticket left alone", s["issues"][1]["assignees"], [])
        expect("e2e: branch pushed", bool(sh(["git", "ls-remote", "origin", "refs/heads/7-show-the-item-list"],
                                             repo).stdout.strip()), True)

        env["FAKE_VERDICT"] = "changes"
        tick()  # CI green, new head: the reviewer asks for changes
        tick()  # the builder fixes and pushes
        env["FAKE_VERDICT"] = "approve"
        tick()  # a new head: the reviewer runs again and approves
        tick()  # approved: labelled for the human
        s = json.loads(state.read_text())
        pr = s["prs"][0] if s["prs"] else {"labels": [], "comments": []}
        expect("e2e: ready for human", "ready-for-human" in pr["labels"], True)
        expect("e2e: review posted", any(c["body"].startswith("**Review: approve")
                                         for c in pr["comments"]), True)
        ledger = [json.loads(ln) for ln in (home / ".spec-to-ship/loop/me__app/runs.jsonl")
                  .read_text().splitlines()]
        expect("e2e: build, review, fix, review", [(x["role"], x["ctx"].split()[-1]) for x in ledger],
               [("builder", "build"), ("reviewer", "reviewer"), ("builder", "review"), ("reviewer", "reviewer")])
        expect("e2e: cost read from every run", round(sum(x["cost"] for x in ledger), 2), 0.08)
        expect("e2e: changes requested then approved", [c["body"].split(".")[0] for c in pr["comments"]
                                                        if c["body"].startswith("**Review")],
               ["**Review: changes", "**Review: approve"])
        status = sh(kit + ["loop", "status", str(repo)], tmp, env).stdout
        expect("e2e: status shows it", "ready for you" in status, True)
        done = sh(kit + ["loop", "run", str(repo), "--until-done"], tmp, env, check=False).stdout
        expect("e2e: until-done stops when only the human can act", "Done: 1 ready for you" in done, True)
        expect("e2e: report names the PR", f"PR #{pr.get('number')} ready" in done, True)
        expect("e2e: report names the blocked ticket", "Ticket #8 waits on #7" in done, True)
        expect("e2e: report hands off the next run", "Paste:     kit loop run --until-done" in done, True)

        s["prs"][0]["state"] = "MERGED"
        state.write_text(json.dumps(s))
        tick()  # merged: worktree and branches go
        expect("e2e: worktree removed", (tmp / "app-worktrees/7-show-the-item-list").exists(), False)
        expect("e2e: remote branch deleted", sh(["git", "ls-remote", "origin",
                                                 "refs/heads/7-show-the-item-list"], repo).stdout.strip(), "")
        report = sh(kit + ["models", "report"], tmp, env).stdout
        expect("e2e: report lists the builder", "builder" in report and "sonnet" in report, True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def pinning() -> None:
    """kit models set pins every harness, refuses a bad mapping, and uninstall removes the pins."""
    tmp = pathlib.Path(tempfile.mkdtemp())
    try:
        env = {**os.environ, "HOME": str(tmp), "SPEC_TO_SHIP_HOME": str(tmp / ".spec-to-ship"),
               "SPEC_TO_SHIP_SKIP_CLI": "1"}
        kit = [sys.executable, str(ROOT / "scripts/kit.py")]
        sh(kit + ["install", "--for", "claude,codex,opencode,cursor,antigravity"], tmp, env)
        good = {"version": 1, "roles": {"explore": {
            "claude": {"model": "haiku", "effort": "low"}, "codex": {"model": "cheap-1", "effort": "low"},
            "opencode": {"model": "prov/cheap-1"}, "cursor": {"model": "cheap-c"},
            "antigravity": {"model": "flash"}}}}
        (tmp / "m.json").write_text(json.dumps(good))
        expect("pin: set accepted", sh(kit + ["models", "set", str(tmp / "m.json")], tmp, env,
                                       check=False).returncode, 0)
        toml = (tmp / ".codex/agents/codebase-explorer.toml").read_text()
        expect("pin: codex model", 'model = "cheap-1"' in toml and 'model_reasoning_effort = "low"' in toml, True)
        expect("pin: codex leaves other roles unpinned",
               "\nmodel =" in (tmp / ".codex/agents/solution-architect.toml").read_text(), False)
        expect("pin: opencode model", "model: prov/cheap-1" in
               (tmp / ".config/opencode/agents/codebase-explorer.md").read_text(), True)
        expect("pin: cursor model", "model: cheap-c" in (tmp / ".cursor/agents/codebase-explorer.md").read_text(), True)
        expect("pin: antigravity model", "model: flash" in
               (tmp / ".gemini/config/agents/codebase-explorer.md").read_text(), True)
        claude = tmp / ".claude/agents/codebase-explorer.md"
        text = claude.read_text() if claude.exists() else ""
        expect("pin: claude override", ("model: haiku" in text and "effort: low" in text
                                        and text.count("model:") == 1), True)

        for label, bad in (
            ("antigravity id", {"version": 1, "roles": {"explore": {"antigravity": {"model": "gemini-x"}}}}),
            ("unknown role", {"version": 1, "roles": {"writer": {"codex": {"model": "x"}}}}),
            ("same family", {"version": 1, "loop": {"builder": {"harness": "claude", "ladder": ["a"]},
                                                     "reviewer": {"harness": "claude", "ladder": ["a"]}}}),
            ("unverified loop", {"version": 1, "loop": {"builder": {"harness": "codex", "ladder": ["a"]}}}),
        ):
            (tmp / "bad.json").write_text(json.dumps(bad))
            expect(f"pin: refuses {label}", sh(kit + ["models", "set", str(tmp / "bad.json")], tmp, env,
                                               check=False).returncode, 1)
        sh(kit + ["uninstall"], tmp, env)
        expect("pin: uninstall removes the claude override", claude.exists(), False)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


pinning()
e2e()
for f in FAIL:
    print(f"FAIL {f}")
print(f"{'ok' if not FAIL else str(len(FAIL)) + ' failure(s)'}")
sys.exit(1 if FAIL else 0)
