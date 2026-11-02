#!/usr/bin/env python3
"""A stand-in for `claude -p` in tests/loop_e2e.py. Builds by committing a file and writing
the pull request body; reviews by answering with the verdict in $FAKE_VERDICT. Prints the JSON
shape `claude --output-format json` does, so cost and model checks run for real."""

import json
import os
import pathlib
import subprocess
import sys

prompt = sys.argv[sys.argv.index("-p") + 1]
model = sys.argv[sys.argv.index("--model") + 1]
cwd = pathlib.Path.cwd()

if prompt.startswith("/fk-build"):
    (cwd / "lib").mkdir(exist_ok=True)
    (cwd / "lib/feature.dart").write_text("// feature\n")
    subprocess.run(["git", "add", "lib/feature.dart"], check=True)
    subprocess.run(["git", "commit", "-qm", "Add the feature"], check=True)
    (cwd / ".kit-loop/pr-body.md").write_text("## Summary\n\nAdds the feature.\n\nCloses #7\n")
    text = "Built and committed."
elif "reviewing pull request" in prompt:
    verdict = os.environ.get("FAKE_VERDICT", "approve")
    text = "Reviewed.\n\n```json\n" + json.dumps({
        "verdict": verdict, "summary": "Does what AC 1 asks.",
        "findings": [] if verdict == "approve" else
        [{"file": "lib/feature.dart", "line": 1, "severity": "major", "criterion": "AC 1",
          "problem": "empty state missing", "fix": "add it"}],
        "one_way_door": False, "one_way_reason": ""}) + "\n```"
elif "fixing pull request" in prompt:
    (cwd / "lib/feature.dart").write_text("// feature\n// empty state\n")
    subprocess.run(["git", "commit", "-qam", "Add the empty state"], check=True)
    text = "Fixed."
else:
    text = "ok"

print(json.dumps({"type": "result", "result": text, "total_cost_usd": 0.02,
                  "modelUsage": {f"claude-{model}-test": {"inputTokens": 10}}}))
