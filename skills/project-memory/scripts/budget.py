#!/usr/bin/env python3
"""Measure the docs every session pays to read against their budgets.

    budget.py [project root]     prints one line per file or folder over budget; nothing when all fit

Exits 0 either way: it reports, the agent decides. It is the one place the budgets live, so the
prune-context skill works from what this prints rather than from numbers of its own.
"""

import datetime
import pathlib
import re
import sys

LINES = {
    "docs/vault/memory.md": 60,
    "docs/vault/index.md": 60,
    "CLAUDE.md": 120,
    "AGENTS.md": 120,
}
AGENT_DOC_LINES = 200  # each file in docs/agents/
UNFOLDED_LOGS = 10  # log entries newer than memory.md's Consolidated: date
SPRINT_NOTES = 3  # the open sprint and the two before it


def lines(p: pathlib.Path) -> int:
    try:
        return len(p.read_text(errors="ignore").splitlines())
    except OSError:
        return 0


def main() -> int:
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    over = []
    for rel, cap in LINES.items():
        n = lines(root / rel)
        if n > cap:
            over.append(f"{rel}: {n} lines, budget {cap}")
    for p in sorted((root / "docs/agents").glob("*.md")):
        n = lines(p)
        if n > AGENT_DOC_LINES:
            over.append(f"{p.relative_to(root)}: {n} lines, budget {AGENT_DOC_LINES}")

    memory = root / "docs/vault/memory.md"
    m = re.search(r"Consolidated:\**\s*(\d{4}-\d{2}-\d{2})",
                  memory.read_text(errors="ignore") if memory.is_file() else "")
    since = datetime.date.fromisoformat(m.group(1)) if m else datetime.date.min
    logs = []
    for p in (root / "docs/vault/log").glob("*.md"):
        d = re.match(r"(\d{4}-\d{2}-\d{2})", p.name)
        if d and datetime.date.fromisoformat(d.group(1)) > since:
            logs.append(p)
    if len(logs) > UNFOLDED_LOGS:
        over.append(f"docs/vault/log/: {len(logs)} entries not yet folded into memory.md, "
                    f"budget {UNFOLDED_LOGS}")

    done = [p.name for p in sorted((root / "docs/vault/changes").glob("*.md"))
            if re.search(r"\*\*Status:\*\*\s*done\b", p.read_text(errors="ignore"))]
    if done:
        over.append(f"docs/vault/changes/: {len(done)} done note(s) still kept ({', '.join(done)}), budget 0")

    sprints = sorted((root / "docs/vault/sprints").glob("sprint-*.md"))
    if len(sprints) > SPRINT_NOTES:
        over.append(f"docs/vault/sprints/: {len(sprints)} sprint notes, budget {SPRINT_NOTES}")

    for line in over:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
