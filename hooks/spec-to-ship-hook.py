#!/usr/bin/env python3
"""spec-to-ship's hook, for every harness that runs command hooks.

    spec-to-ship-hook.py <harness> <check>

harness: claude | codex | cursor
check:   secrets - block a prompt that pastes a likely API key, token or JWT

Each harness sends a different stdin payload and reads a different reply, so this file
normalises the input, runs the check once, and answers in that harness's own shape.
opencode runs plugins instead of command hooks: its equivalent is opencode/plugins/spec-to-ship.ts.

The check fails open: an unreadable payload or any error lets the action through, because a
broken guard must never stop work.
"""

import json
import re
import sys

SECRET_RE = re.compile(
    r"sk_(live|test)_[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}"
    r"|eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}"
    r"|Bearer\s+[A-Za-z0-9_\-.=]{20,}"
)
SECRET_REASON = (
    "Prompt appears to contain a secret (API key / token / JWT). Keep secrets out of source and prompts; load them from the environment or a secret store instead."
)


def payload() -> dict:
    try:
        data = json.loads(sys.stdin.read() or "{}")
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def reply(obj: dict) -> None:
    print(json.dumps(obj))


def check_secrets(harness: str, p: dict) -> None:
    if not SECRET_RE.search(str(p.get("prompt") or "")):
        return
    if harness == "cursor":
        reply({"continue": False, "user_message": SECRET_REASON})
    else:  # claude, codex
        reply({"decision": "block", "reason": SECRET_REASON})


CHECKS = {"secrets": check_secrets}


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[2] not in CHECKS:
        return 0
    try:
        CHECKS[sys.argv[2]](sys.argv[1], payload())
    except Exception:  # noqa: BLE001 - fail open, always
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
