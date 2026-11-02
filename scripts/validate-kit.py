#!/usr/bin/env python3
"""Check this kit's invariants. Run from the repo root; exits non-zero on any failure.

These are the rules CLAUDE.md states, encoded so they fail a check instead of relying on
memory. Add a rule here whenever you catch yourself writing one down twice.
"""

import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

FAIL: list[str] = []
ROOT = pathlib.Path(__file__).resolve().parent.parent


def check(label: str, ok_msg: str) -> None:
    print(f"{label:<4} {ok_msg}")


def node_strips_types(node: str) -> bool:
    """Whether this node can run a .ts file directly (--experimental-strip-types, 22.6+)."""
    try:
        out = subprocess.run([node, "--version"], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return False
    m = re.match(r"v(\d+)\.(\d+)", out.stdout.strip())
    return bool(m) and (int(m.group(1)), int(m.group(2))) >= (22, 6)


def main() -> int:
    skills: dict[str, bool] = {}  # name -> is_user_invoked
    descs: dict[str, str] = {}  # name -> frontmatter description

    # 1. Frontmatter is valid and name matches the directory.
    for p in sorted((ROOT / "skills").glob("*/SKILL.md")):
        m = re.match(r"^---\n(.*?)\n---\n", p.read_text(), re.S)
        if not m:
            FAIL.append(f"no frontmatter: {p.relative_to(ROOT)}")
            continue
        block = m.group(1)
        name_m = re.search(r"^name:\s*(.+)$", block, re.M)
        desc_m = re.search(r"^description:\s*(.+)$", block, re.M)
        if not name_m:
            FAIL.append(f"no name: {p.relative_to(ROOT)}")
            continue
        if not desc_m:
            FAIL.append(f"no description: {p.relative_to(ROOT)}")
        name = name_m.group(1).strip()
        if name != p.parent.name:
            FAIL.append(f"name/dir mismatch: '{name}' in {p.parent.name}/")
        skills[name] = "disable-model-invocation: true" in block
        if desc_m:
            descs[name] = desc_m.group(1).strip()
    check("1.", f"{len(skills)} skills, frontmatter valid, names match directories")

    # 2. plugin.json registers exactly the skills that exist.
    manifest = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
    registered = {r.rsplit("/", 1)[-1] for r in manifest["skills"]}
    for orphan in sorted(registered - set(skills)):
        FAIL.append(f"registered but missing on disk: {orphan}")
    for unreg in sorted(set(skills) - registered):
        FAIL.append(f"on disk but not in plugin.json: {unreg}")
    check("2.", f"plugin.json registers all {len(registered)} skills, no orphans")

    # 3. Every Skill-tool call resolves, and never targets a user-invoked skill.
    #    Only backticked names count as call sites; prose like "with its name" does not.
    calls = 0
    for p in (ROOT / "skills").glob("*/SKILL.md"):
        for m in re.finditer(r"Skill tool with\s*`([a-z][a-z0-9-]+)`", p.read_text()):
            target, calls = m.group(1), calls + 1
            if target not in skills:
                FAIL.append(f"{p.parent.name} calls unknown skill '{target}'")
            elif skills[target]:
                FAIL.append(f"{p.parent.name} calls user-invoked '{target}' (unreachable)")
    check("3.", f"{calls} Skill-tool call sites, all resolve to model-invoked skills")

    # 4. A cross-skill file link is allowed only when the owner is user-invoked,
    #    since nothing can call one. See CLAUDE.md.
    for p in (ROOT / "skills").glob("*/*.md"):
        for m in re.finditer(r"\]\(\.\./([a-z][a-z0-9-]+)/", p.read_text()):
            owner = m.group(1)
            if owner not in skills:
                FAIL.append(f"{p.parent.name} links to unknown skill dir '{owner}'")
            elif not skills[owner]:
                FAIL.append(
                    f"{p.parent.name} links across to model-invoked '{owner}' — call it instead"
                )
    check("4.", "cross-skill links only target user-invoked (uncallable) skills")

    # 5. The router names every user-invoked skill, or it lies.
    router = (ROOT / "skills/ask-kit/SKILL.md").read_text()
    for name, is_user in skills.items():
        if is_user and name != "ask-kit" and name not in router:
            FAIL.append(f"ask-kit omits user-invoked skill '{name}'")
    check("5.", f"router covers all {sum(skills.values())} user-invoked skills")

    # 6. No unresolved lowercase template tokens leaked out of a template/ into skills.
    #    {{API_KEY}} style uppercase tokens are a deliberate convention, not a leak, and a
    #    skill's own template/ directory is where the lowercase ones belong.
    for p in (ROOT / "skills").rglob("*.md"):
        if "template" in p.relative_to(ROOT / "skills").parts:
            continue
        for m in re.finditer(r"\{\{([a-z][a-z0-9_]*)\}\}", p.read_text()):
            FAIL.append(f"unresolved template token {{{{{m.group(1)}}}}} in {p.relative_to(ROOT)}")
    check("6.", "no unresolved lowercase template tokens in skills")

    # 7. Every agent referenced by a skill actually exists.
    agents = {p.stem for p in (ROOT / "agents").glob("*.md")} - {"README"}
    for p in (ROOT / "skills").glob("*/SKILL.md"):
        for m in re.finditer(r"`(flutter-(?:explore|architect|[a-z]+-engineer))`", p.read_text()):
            if m.group(1) not in agents:
                FAIL.append(f"{p.parent.name} references missing agent '{m.group(1)}'")
    check("7.", f"{len(agents)} agents, all skill references resolve")

    # 8. No client or project name leaks into a portable skill. The kit is written *from*
    #    real projects but must never refer to one.
    #    The terms are themselves client data, so they live in .kit-private/, which is
    #    gitignored and never published. A checkout without that directory configures zero
    #    terms and the check passes: this guards a private working copy on its way out, and
    #    the public repo has nothing to guard.
    PRIVATE = ROOT / ".kit-private"

    def private_terms(filename):
        f = PRIVATE / filename
        if not f.exists():
            return []
        return [ln.strip() for ln in f.read_text().splitlines()
                if ln.strip() and not ln.lstrip().startswith("#")]

    CLIENT_NAMES = [t.lower() for t in private_terms("client-names.txt")]
    for p in list((ROOT / "skills").rglob("*.md")) + list((ROOT / "agents").glob("*.md")) + \
             list((ROOT / "rules").glob("*.md")) + list((ROOT / "template").rglob("*.md")):
        low = p.read_text().lower()
        for nm in CLIENT_NAMES:
            if nm in low:
                FAIL.append(f"client name '{nm}' leaked into {p.relative_to(ROOT)}")
    # Project-specific symbols leak more quietly than the name: a component or feature class
    # that exists in one app but is not part of what the kit scaffolds. Same storage, same
    # reason, matched case-sensitively because these are Dart identifiers.
    PROJECT_SYMBOLS = private_terms("project-symbols.txt")
    for p in list((ROOT / "skills").rglob("*.md")) + list((ROOT / "rules").glob("*.md")) + \
             list((ROOT / "template").rglob("*.md")):
        text = p.read_text()
        for sym in PROJECT_SYMBOLS:
            if sym in text:
                FAIL.append(f"project-specific symbol '{sym}' in {p.relative_to(ROOT)}")
    configured = f"{len(CLIENT_NAMES)} names, {len(PROJECT_SYMBOLS)} symbols" \
        if (CLIENT_NAMES or PROJECT_SYMBOLS) else "no terms configured; see .kit-private/"
    check("8.", f"no client name or project-symbol leakage ({configured})")

    # 9. The README Reference lists every skill, links to its SKILL.md, and describes it in the
    #    skill's own words. The description is the frontmatter one with the trailing model-trigger
    #    sentence ("Use when ...", "Read before ...") cut, so a human reads prose and there is
    #    still one source of truth. Bullets may wrap, so compare on normalised whitespace.
    readme = (ROOT / "README.md").read_text()
    bullets: dict[str, tuple[str, str]] = {}  # name -> (link target, description)
    for m in re.finditer(
        r"^- \*\*\[([a-z][a-z0-9-]+)\]\(([^)]+)\)\*\*:\s*(.+?)(?=\n- |\n\n|\n#|\Z)",
        readme, re.S | re.M,
    ):
        bullets[m.group(1)] = (m.group(2), " ".join(m.group(3).split()))

    for stray in sorted(set(bullets) - set(skills)):
        FAIL.append(f"README references unknown skill '{stray}'")
    for name in sorted(skills):
        if name not in bullets:
            FAIL.append(f"README Reference omits skill '{name}'")
            continue
        link, desc = bullets[name]
        want_link = f"./skills/{name}/SKILL.md"
        if link != want_link: 
            FAIL.append(f"README links '{name}' to '{link}', expected '{want_link}'")
        want = re.split(r"\s+(?:Use|Read)\s+(?:when|before|after)\b", descs.get(name, ""))[0]
        want = " ".join(want.split()).rstrip()
        if desc.rstrip() != want:
            FAIL.append(
                f"README description for '{name}' does not match its frontmatter\n"
                f"      README: {desc}\n"
                f"      SKILL:  {want}"
            )
    check("9.", f"README Reference links and describes all {len(skills)} skills, matching frontmatter")

    # 10. Stack purity. A skill that names a state-management library generates code in that
    #     library's shape, which is wrong on a project using another one. The kit resolves the
    #     stack through `flutter-supabase-conventions` instead, and per-stack code lives in a skill's
    #     templates/ directory where naming a library is the whole point. No skill is exempt: a
    #     new skill needing per-stack code gets a templates/ directory.
    STACK_TOKENS = re.compile(
        r"flutter_bloc|BlocProvider|BlocBuilder|BlocListener|BlocConsumer|blocTest|bloc_test"
    )
    # A detector has to name what it detects, which is the opposite of generating in its shape.
    STACK_DETECTORS = {"flutter-supabase-conventions"}
    exempt = STACK_DETECTORS & set(skills)
    for stale in sorted(exempt - set(skills)):
        FAIL.append(f"stack exemption names missing skill '{stale}' — drop it from the list")
    for p in sorted((ROOT / "skills").rglob("*.md")):
        if p.parent.name == "templates":
            continue
        owner = p.relative_to(ROOT / "skills").parts[0]
        if owner in exempt:
            continue
        for lineno, line in enumerate(p.read_text().splitlines(), 1):
            # A row routing to a per-stack template may name the stack it routes to;
            # that is the resolver pattern working, not a leak.
            if "templates/" in line:
                continue
            if STACK_TOKENS.search(line):
                FAIL.append(
                    f"{p.relative_to(ROOT)}:{lineno} names a state library — resolve it "
                    f"through `flutter-supabase-conventions`, or move the code into {owner}/templates/"
                )
    check("10.", "skills name no state library outside a templates/ directory")

    # 11. The setup skill's AGENTS.md template twins its CLAUDE.md: every harness other than
    #     Claude Code reads AGENTS.md, so it must carry the same sections.
    template = ROOT / "skills/fk-setup/template"
    try:
        agents_md = (template / "AGENTS.md").read_text()
    except FileNotFoundError:
        FAIL.append("fk-setup/template/AGENTS.md missing — the twin of CLAUDE.md")
        agents_md = ""
    if agents_md:
        for section in ("## Project", "## Architecture", "## Hard rules",
                        "## Skills", "## Memory", "## Verification"):
            if section not in agents_md:
                FAIL.append(f"template/AGENTS.md omits section '{section}'")
        if "docs/agents/project.md" not in agents_md:
            FAIL.append("template/AGENTS.md does not point at docs/agents/project.md")
    check("11.", "setup's AGENTS.md template twins its CLAUDE.md")

    # 12. The harness registry is complete. scripts/kit.py installs from it and the site
    #     renders from it, so a harness missing a field breaks one or the other silently.
    try:
        registry = json.loads((ROOT / "install/harnesses.json").read_text())
    except (FileNotFoundError, json.JSONDecodeError) as e:
        FAIL.append(f"install/harnesses.json unreadable: {e}")
        registry = {"harnesses": []}
    ids = [h.get("id") for h in registry["harnesses"]]
    for want in ("claude", "codex", "opencode", "antigravity", "cursor"):
        if want not in ids:
            FAIL.append(f"harness registry omits '{want}'")
    for h in registry["harnesses"]:
        for key in ("id", "name", "detect", "method", "install", "support"):
            if key not in h:
                FAIL.append(f"harness '{h.get('id')}' lacks '{key}'")
        if h.get("method") == "files":
            for key in ("skills_dirs", "agents_dir", "agents_format"):
                if key not in h:
                    FAIL.append(f"file-installed harness '{h.get('id')}' lacks '{key}'")
    check("12.", f"harness registry covers {len(ids)} harnesses with every field")

    # 13. The opencode plugin covers the command hooks it stands in for, on opencode's real
    #     tool ids: the shell tool is `bash` (tool/shell/id.ts keeps ToolID = "bash"; `shell`
    #     is only the filename) and the patch tool is `apply_patch` (apply_patch.ts).
    plugin = ROOT / "opencode/plugins/spec-to-ship.ts"
    if not plugin.exists():
        FAIL.append("opencode/plugins/spec-to-ship.ts missing")
    else:
        plugin_text = plugin.read_text()
        for marker in ("tool.execute.before", "export default", "SECRET_RE"):
            if marker not in plugin_text:
                FAIL.append(f"opencode plugin never mentions '{marker}'")
        if '"apply_patch"' not in plugin_text:
            FAIL.append('opencode plugin does not match the patch tool id "apply_patch"')
        if 'tool === "patch"' in plugin_text:
            FAIL.append('opencode plugin matches non-existent tool id tool === "patch"')
    check("13.", "opencode plugin carries the secrets guard on opencode's real tool ids")

    # 14. The README documents the user-level install for every harness it supports.
    for marker in ("install.sh", "--for", "kit doctor", "INSTALL.md"):
        if marker not in readme:
            FAIL.append(f"README install section never mentions '{marker}'")
    for h in registry["harnesses"]:
        if h.get("name") and h["name"] not in readme:
            FAIL.append(f"README never names harness '{h['name']}'")
    check("14.", "README documents the user-level install for every harness")

    # 15. The remote installer downloads and delegates: it fetches the latest release's tarball
    #     and runs that tree's scripts/kit.py, so it never names a skill and cannot drift from
    #     the kit. Its fallback, used when the lookup fails, is held to the current version.
    installer = ROOT / "install.sh"
    if not installer.exists():
        FAIL.append("install.sh missing")
    elif not os.access(installer, os.X_OK):
        FAIL.append("install.sh is not executable")
    else:
        installer_text = installer.read_text()
        for marker in ("scripts/kit.py", "codeload", "latest_tag", "mktemp", "current"):
            if marker not in installer_text:
                FAIL.append(f"install.sh never mentions '{marker}'")
        plugin_version = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())["version"]
        fallback = re.search(r'^FALLBACK_VERSION="v([\d.]+)"', installer_text, re.M)
        if not fallback or fallback.group(1) != plugin_version:
            FAIL.append(f"install.sh FALLBACK_VERSION is not v{plugin_version} (plugin.json's version)")
        for name in skills:
            if re.search(rf"\b{re.escape(name)}\b", installer_text):
                FAIL.append(f"install.sh names skill '{name}' — it must delegate, not duplicate")
    check("15.", "install.sh downloads and delegates to scripts/kit.py")

    # 16. Functional install test, in a throwaway home. Greps cannot catch a skill missing
    #     from one harness's folder, a hook merged twice, or an uninstall that eats the
    #     user's own settings, so drive the real installer and the real bootstrap.
    with tempfile.TemporaryDirectory() as tmp:
        home = pathlib.Path(tmp) / "home"
        (home / ".config/opencode").mkdir(parents=True)
        (home / ".codex").mkdir(parents=True)
        user_oc = {"model": "x/y", "permission": {"skill": {"retro": "allow"}}}
        user_hook = {"matcher": "Bash", "hooks": [{"type": "command", "command": "mine.sh"}]}
        (home / ".config/opencode/opencode.json").write_text(json.dumps(user_oc))
        (home / ".codex/hooks.json").write_text(json.dumps({"hooks": {"UserPromptSubmit": [user_hook]}}))
        version = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())["version"]
        # KIT_LATEST stands in for the GitHub tag lookup, so nothing here touches the network.
        env = {**os.environ, "HOME": str(home), "SPEC_TO_SHIP_SKIP_CLI": "1",
               "KIT_LATEST": f"v{version}"}
        env.pop("SPEC_TO_SHIP_HOME", None)
        kit = [sys.executable, str(ROOT / "scripts/kit.py")]
        everyone = "codex,opencode,antigravity,cursor"

        def run(*args):
            return subprocess.run([*kit, *args], capture_output=True, text=True, env=env)

        r = run("install", "--for", everyone)
        if r.returncode != 0:
            FAIL.append(f"kit install failed: {r.stderr.strip()[:300]}")
        else:
            run("install", "--for", everyone)  # a second run must change nothing
            for d in (".agents/skills", ".gemini/config/skills", ".gemini/antigravity-cli/skills"):
                found = {p.name for p in (home / d).iterdir()} if (home / d).is_dir() else set()
                if found != set(skills):
                    FAIL.append(f"~/{d} holds {len(found)} of {len(skills)} skills")
            for name, is_user in skills.items():
                yaml = home / ".agents/skills" / name / "agents/openai.yaml"
                if is_user and "allow_implicit_invocation: false" not in (
                        yaml.read_text() if yaml.exists() else ""):
                    FAIL.append(f"Codex would auto-invoke user-invoked '{name}' (no openai.yaml policy)")
            try:
                import tomllib
                for t in (home / ".codex/agents").glob("*.toml"):
                    doc = tomllib.loads(t.read_text())
                    if not {"name", "description", "developer_instructions"} <= set(doc):
                        FAIL.append(f"Codex agent {t.name} lacks a required key")
            except ModuleNotFoundError:
                pass  # tomllib is 3.11+; the shape is still covered by the count below
            if len(list((home / ".codex/agents").glob("*.toml"))) != len(agents):
                FAIL.append("Codex agents not all converted")
            oc = json.loads((home / ".config/opencode/opencode.json").read_text())
            gates = oc.get("permission", {}).get("skill", {})
            if gates.get("retro") != "allow" or oc.get("model") != "x/y":
                FAIL.append("install overwrote the user's own opencode.json values")
            if any(gates.get(n) != "ask" for n, u in skills.items() if u and n != "retro"):
                FAIL.append("opencode does not gate every user-invoked skill")
            codex_pre = json.loads((home / ".codex/hooks.json").read_text())["hooks"]["UserPromptSubmit"]
            if user_hook not in codex_pre or len(codex_pre) != 2:
                FAIL.append(f"Codex prompt hooks wrong after two installs: {len(codex_pre)} entries")
            if run("doctor").returncode != 0:
                FAIL.append("kit doctor reports problems on a clean install")
            run("uninstall")
            leftover = [p for p in home.rglob("*") if p.is_symlink()]
            if leftover:
                FAIL.append(f"uninstall left {len(leftover)} link(s), e.g. {leftover[0]}")
            oc = json.loads((home / ".config/opencode/opencode.json").read_text())
            if oc != user_oc:
                FAIL.append(f"uninstall did not restore the user's opencode.json: {oc}")
            codex_pre = json.loads((home / ".codex/hooks.json").read_text())["hooks"]["UserPromptSubmit"]
            if codex_pre != [user_hook]:
                FAIL.append("uninstall did not restore the user's Codex hooks")

        # The bootstrap, from a tarball of this tree, into a separate kit home.
        tarball = pathlib.Path(tmp) / "kit.tgz"
        subprocess.run(["tar", "-czf", str(tarball), "-C", str(ROOT.parent),
                        "--exclude=.git", "--exclude=_site", "--exclude=.kit-private",
                        ROOT.name], check=True)
        boot_env = {**env, "KIT_TARBALL_URL": tarball.as_uri(),
                    "SPEC_TO_SHIP_HOME": str(pathlib.Path(tmp) / "kithome")}
        r = subprocess.run(["bash", str(installer), "--for", "cursor"],
                           capture_output=True, text=True, env=boot_env)
        kithome = pathlib.Path(tmp) / "kithome"
        if r.returncode != 0:
            FAIL.append(f"install.sh bootstrap failed: {(r.stderr or r.stdout).strip()[:300]}")
        elif not (kithome / "current/scripts/kit.py").exists() or not (kithome / "bin/kit").exists():
            FAIL.append("install.sh did not lay out ~/.spec-to-ship/{current,bin/kit}")
        else:
            # `kit update` reinstalls the newer release for the harnesses already installed,
            # and does nothing when the installed version is the latest.
            launcher = [str(kithome / "bin/kit"), "update"]
            r = subprocess.run(launcher, capture_output=True, text=True,
                               env={**boot_env, "KIT_LATEST": "v99.0.0"})
            record = json.loads((kithome / "installed.json").read_text())
            if r.returncode != 0:
                FAIL.append(f"kit update failed: {(r.stderr or r.stdout).strip()[:300]}")
            elif (kithome / "current").resolve() != (kithome / "versions/v99.0.0").resolve():
                FAIL.append("kit update did not point ~/.spec-to-ship/current at the new release")
            elif list(record["harnesses"]) != ["cursor"]:
                FAIL.append(f"kit update changed the installed harnesses: {list(record['harnesses'])}")
            r = subprocess.run(launcher, capture_output=True, text=True,
                               env={**boot_env, "KIT_LATEST": "v0.0.1"})
            if r.returncode != 0 or "is the latest release" not in r.stdout:
                FAIL.append("kit update did not report an up-to-date install as current")

    # The shared hook answers each harness in its own shape and fails open.
    hook = [sys.executable, str(ROOT / "hooks/spec-to-ship-hook.py")]
    secret = json.dumps({"prompt": "key sk_live_0123456789abcdefghij"})
    for harness, want in (("claude", '"decision": "block"'), ("codex", '"decision": "block"'),
                          ("cursor", '"continue": false')):
        out = subprocess.run([*hook, harness, "secrets"], input=secret,
                             capture_output=True, text=True).stdout
        if want not in out:
            FAIL.append(f"spec-to-ship-hook.py {harness} secrets did not block a pasted key: {out!r}")
    r = subprocess.run([*hook, "claude", "secrets"], input="not json", capture_output=True, text=True)
    if r.returncode != 0 or r.stdout.strip():
        FAIL.append("spec-to-ship-hook.py does not fail open on a garbage payload")
    check("16.", "kit install/update/doctor/uninstall, install.sh and spec-to-ship-hook.py pass a functional test")

    # 17. Functional plugin test. Check 13 only greps for the right tool ids, which
    #     cannot tell whether the hooks fire. The ids are the whole trap: the shell
    #     tool's id is `bash` (tool/shell/id.ts keeps `ToolID = "bash"` until 2.0,
    #     though the file is shell.ts and the registry binds `tool.shell`) and the
    #     patch tool's is `apply_patch` (`Tool.define("apply_patch", ...)`, though the
    #     registry binds `tool.patch`). tests/plugin-hooks.ts drives the real hook
    #     both ways — it must fire on those ids and ignore the plausible wrong ones.
    #     Skipped when node cannot run TypeScript, so the validator still works
    #     without a JS toolchain.
    harness = ROOT / "tests/plugin-hooks.ts"
    node = shutil.which("node")
    if not harness.is_file():
        FAIL.append("tests/plugin-hooks.ts missing — check 13's greps become the only plugin guard")
        check("17.", "opencode plugin hooks fire on opencode's real tool ids")
    elif node is None or not node_strips_types(node):
        check("17.", "plugin hook test SKIPPED (needs node 22.6+ for --experimental-strip-types)")
    else:
        r = subprocess.run([node, "--experimental-strip-types", str(harness)],
                           capture_output=True, text=True, cwd=ROOT)
        if r.returncode != 0:
            bad = [ln.strip() for ln in r.stdout.splitlines() if ln.strip().startswith("FAIL")]
            FAIL.append("plugin hook test failed: "
                        + ("; ".join(bad) if bad else r.stderr.strip()[:400]))
        check("17.", "opencode plugin hooks fire on opencode's real tool ids")

    # 18. Agents follow the rules skills do. An agent reaches a skill by calling the Skill
    #     tool, never by a harness path (`.claude/skills/...` resolves in one install shape
    #     and silently in no other), and names no state library: the layer engineers serve
    #     every stack, so the stack arrives through `flutter-supabase-conventions`.
    HARNESS_PATH = re.compile(r"\.(?:claude|cursor|opencode)/(?:skills|rules)/")
    agent_calls = 0
    for p in sorted((ROOT / "agents").glob("*.md")):
        if p.stem == "README":
            continue
        text = p.read_text()
        for m in re.finditer(r"Skill tool with\s*`([a-z][a-z0-9-]+)`", text):
            target, agent_calls = m.group(1), agent_calls + 1
            if target not in skills:
                FAIL.append(f"agent {p.stem} calls unknown skill '{target}'")
            elif skills[target]:
                FAIL.append(f"agent {p.stem} calls user-invoked '{target}' (unreachable)")
        for lineno, line in enumerate(text.splitlines(), 1):
            if HARNESS_PATH.search(line):
                FAIL.append(f"agents/{p.name}:{lineno} reaches a skill or rule by harness path "
                            f"— call the Skill tool with its name instead")
            if STACK_TOKENS.search(line):
                FAIL.append(f"agents/{p.name}:{lineno} names a state library — resolve it "
                            f"through `flutter-supabase-conventions`")
    check("18.", f"agents: {agent_calls} Skill-tool calls resolve, no harness paths, "
                 f"no state library")

    # 19. The command surface is fixed. Every user-invoked skill is a command a person has to
    #     know about, and the kit's promise is that there are few of them. A new workflow becomes
    #     a step one of these calls; adding a command means changing this list on purpose.
    COMMANDS = {"ask-kit", "fk-setup", "fk-plan", "fk-sprint", "fk-build", "fk-feedback",
                "fk-change", "fk-release", "retro"}
    TOOLS = {"handoff", "unslop", "spec-for-cheap-executor"}
    user_skills = {n for n, u in skills.items() if u}
    for extra in sorted(user_skills - COMMANDS - TOOLS):
        FAIL.append(f"'{extra}' is user-invoked but not a listed command — make it a step a "
                    f"command calls, or add it to COMMANDS on purpose")
    for missing in sorted((COMMANDS | TOOLS) - user_skills):
        FAIL.append(f"command '{missing}' is missing or no longer user-invoked")
    check("19.", f"{len(COMMANDS)} commands and {len(TOOLS)} tools, nothing else user-invoked")

    # 20. The delivery layer is stack-neutral. Memory, tracking, the proposal and the backlog
    #     describe how a project is run, not how its code is written, so they name no framework
    #     and call no engineering skill. The fk- commands are where the two layers meet.
    DELIVERY = {"project-memory", "project-tracker", "project-proposal", "project-backlog"}
    STACK_WORD = re.compile(r"\b(?:flutter|dart|pubspec)\b", re.I)
    for name in sorted(DELIVERY):
        folder = ROOT / "skills" / name
        if not (folder / "SKILL.md").exists():
            FAIL.append(f"delivery skill '{name}' is missing")
            continue
        for f in sorted(folder.rglob("*.md")):
            for lineno, line in enumerate(f.read_text().splitlines(), 1):
                if STACK_WORD.search(line):
                    FAIL.append(f"{f.relative_to(ROOT)}:{lineno} names the stack — the delivery "
                                f"layer is stack-neutral; reach engineering through a command")
    check("20.", f"{len(DELIVERY)} delivery-layer skills name no framework")

    # 21. Models are the user's choice, never the kit's. install/roles.json says what each kind of
    #     work needs and owns every agent exactly once; each harness says how to run one role
    #     headless; and no skill or loop prompt names a model, because a name frozen into the
    #     kit is stale within weeks. An agent's `model:` line is Claude Code's default only.
    roles = json.loads((ROOT / "install/roles.json").read_text())
    owner_of: dict[str, list[str]] = {}
    for role, spec in roles["roles"].items():
        if not spec.get("needs"):
            FAIL.append(f"roles.json: role '{role}' does not say what it needs")
        for a in spec.get("agents", []):
            owner_of.setdefault(a, []).append(role)
    agent_names = {p.stem for p in (ROOT / "agents").glob("*.md") if p.stem != "README"}
    for a in sorted(agent_names):
        if len(owner_of.get(a, [])) != 1:
            FAIL.append(f"roles.json: agent '{a}' belongs to {len(owner_of.get(a, []))} roles, not one")
    for a in sorted(set(owner_of) - agent_names):
        FAIL.append(f"roles.json: names unknown agent '{a}'")
    for key, role in roles["loop"].items():
        if not key.startswith("$") and role not in roles["roles"]:
            FAIL.append(f"roles.json: loop.{key} points at unknown role '{role}'")
    for h in registry["harnesses"]:
        hl = h.get("headless") or {}
        for k in ("argv", "effort", "write", "read", "tail", "invoke"):
            if k not in hl:
                FAIL.append(f"harness '{h['id']}' headless template lacks '{k}'")
        flat = " ".join(hl.get("argv", []) + hl.get("tail", []))
        if "{prompt}" not in flat or "{model}" not in flat:
            FAIL.append(f"harness '{h['id']}' headless template never passes the prompt and model")
    MODEL_NAME = re.compile(r"\b(?:gpt-\d|o\d-|claude-(?:opus|sonnet|haiku|fable)|gemini[- ]\d|"
                            r"deepseek|glm-?\d|haiku|sonnet|opus|composer-\d)\b", re.I)
    for f in sorted(list((ROOT / "skills").rglob("*.md")) + list((ROOT / "loop").rglob("*.md"))):
        for lineno, line in enumerate(f.read_text().splitlines(), 1):
            if MODEL_NAME.search(line):
                FAIL.append(f"{f.relative_to(ROOT)}:{lineno} names a model — say what the work needs "
                            f"and let configure-models choose")
    check("21.", f"{len(roles['roles'])} roles own all {len(agent_names)} agents; no skill names a model")

    # 22. kit loop and kit models work: the decision table, verdict parsing, model pinning into
    #     every harness, and one ticket driven from build through a requested change to merged
    #     and cleaned up, against a fake GitHub and a fake model CLI.
    r = subprocess.run([sys.executable, str(ROOT / "tests/loop_test.py")], capture_output=True, text=True)
    if r.returncode != 0:
        FAIL.extend(ln for ln in r.stdout.splitlines() if ln.startswith("FAIL"))
        if not any(ln.startswith("FAIL") for ln in r.stdout.splitlines()):
            FAIL.append(f"tests/loop_test.py crashed: {(r.stderr or r.stdout).strip()[-400:]}")
    check("22.", "kit loop drives a ticket to merged; kit models pins every harness")

    # 23. Stack-free. spec-to-ship runs a product and its engineering on any stack, so no skill or
    #     agent names one. It reaches a stack only through project-stack, which reads the
    #     project's Components table and calls a stack kit's slot skills by pattern when one is
    #     installed, and falls back to each component's own commands when none is.
    STACK = re.compile(r"(?<![a-z])(?:flutter|dart|pubspec|supabase|widget|gradle|xcode|cocoapod|"
                       r"riverpod|bloc|testflight)s?(?![a-z])", re.I)
    agent_files = sorted(p for p in (ROOT / "agents").glob("*.md") if p.stem != "README")
    stacky = set()
    for f in [*sorted((ROOT / "skills").rglob("*.md")), *agent_files]:
        if STACK.search(f.read_text()):
            stacky.add(str(f.relative_to(ROOT)))
    for n in sorted(stacky):
        FAIL.append(f"{n} names a stack; reach one through project-stack")
    check("23.", f"{len(skills)} skills and {len(agent_files)} agents name no stack")

    # 24. Every command hands off. A finished command that leaves the person to work out what comes
    #     next has handed back the hardest part of the thread, so each one calls next-step, which
    #     writes the next command, what it does and the text to paste. And screen-flows' renderer
    #     works: it is the only proof the drawn screens get, since no agent looks at the page.
    for name in sorted(COMMANDS):
        text = (ROOT / "skills" / name / "SKILL.md").read_text()
        if not re.search(r"Skill\s+tool\s+with\s+`next-step`", text):
            FAIL.append(f"command '{name}' never calls the Skill tool with `next-step`")
    r = subprocess.run([sys.executable, str(ROOT / "tests/screens_test.py")], capture_output=True, text=True)
    if r.returncode != 0:
        FAIL.extend(ln for ln in r.stdout.splitlines() if ln.startswith("FAIL"))
        if not any(ln.startswith("FAIL") for ln in r.stdout.splitlines()):
            FAIL.append(f"tests/screens_test.py crashed: {(r.stderr or r.stdout).strip()[-400:]}")
    check("24.", f"all {len(COMMANDS)} commands end with next-step; the screen renderer passes its tests")

    print()
    if FAIL:
        print(f"{len(FAIL)} FAILURE(S):")
        for f in FAIL:
            print(f"  - {f}")
        return 1
    print("All invariants hold.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
