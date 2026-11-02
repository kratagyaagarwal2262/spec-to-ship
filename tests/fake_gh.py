#!/usr/bin/env python3
"""A stateful stand-in for the `gh` calls `kit loop` makes, for tests/loop_e2e.py.

State lives in $FAKE_GH_STATE (JSON): issues, pull requests and comments. Every call is appended
to $FAKE_GH_STATE.log, so the test can assert what the loop did to "GitHub". A pull request's
head is read from the real bare origin with `git ls-remote`, so pushes made by the loop count.
"""

import json
import os
import subprocess
import sys

STATE = os.environ["FAKE_GH_STATE"]
args = sys.argv[1:]
with open(STATE + ".log", "a") as log:
    log.write(json.dumps(args) + "\n")
s = json.load(open(STATE))


def save():
    json.dump(s, open(STATE, "w"), indent=1)


def flag(name, default=None):
    return args[args.index(name) + 1] if name in args else default


def stdin():
    return sys.stdin.read() if flag("--body-file") == "-" or "--input" in args else ""


def head(branch):
    out = subprocess.run(["git", "ls-remote", "origin", f"refs/heads/{branch}"],
                         capture_output=True, text=True).stdout.split()
    return out[0] if out else ""


def labels(names):
    return [{"name": n} for n in names]


def out(obj):
    print(json.dumps(obj))


cmd = args[:2]
if cmd == ["repo", "view"]:
    out({"nameWithOwner": "me/app", "defaultBranchRef": {"name": "main"}})
elif cmd == ["label", "create"]:
    pass
elif cmd == ["issue", "list"]:
    items = [i for i in s["issues"] if i["state"] == "open"]
    if flag("--label"):
        items = [i for i in items if flag("--label") in i["labels"]]
    if "no:assignee" in (flag("--search") or ""):
        items = [i for i in items if not i["assignees"]]
    out([{"number": i["number"], "title": i["title"], "body": i["body"],
          "labels": labels(i["labels"]), "milestone": {"title": i["milestone"]} if i["milestone"] else None}
         for i in items])
elif cmd == ["issue", "edit"]:
    i = next(i for i in s["issues"] if i["number"] == int(args[2]))
    if flag("--add-assignee"):
        i["assignees"].append("me")
    for n in (flag("--add-label") or "").split(","):
        if n and n not in i["labels"]:
            i["labels"].append(n)
    for n in (flag("--remove-label") or "").split(","):
        if n in i["labels"]:
            i["labels"].remove(n)
    save()
elif cmd == ["issue", "comment"]:
    s.setdefault("issue_comments", []).append({"issue": int(args[2]), "body": stdin()})
    save()
elif cmd == ["issue", "view"]:
    i = next(i for i in s["issues"] if i["number"] == int(args[2]))
    out({"title": i["title"], "body": i["body"]})
elif cmd == ["pr", "create"]:
    n = 100 + len(s["prs"])
    s["prs"].append({"number": n, "title": flag("--title"), "state": "OPEN", "body": stdin(),
                     "headRefName": flag("--head"), "labels": [flag("--label")], "comments": []})
    save()
    print(f"https://github.com/me/app/pull/{n}")
elif cmd == ["pr", "list"]:
    out([{**{k: p[k] for k in ("number", "title", "state", "body", "headRefName")},
          "headRefOid": head(p["headRefName"]), "labels": labels(p["labels"]),
          "mergeable": "MERGEABLE", "url": f"https://github.com/me/app/pull/{p['number']}"}
         for p in s["prs"] if flag("--label") in p["labels"]])
elif cmd == ["pr", "view"]:
    p = next(p for p in s["prs"] if p["number"] == int(args[2]))
    out({"comments": [{"body": c["body"], "url": f"https://github.com/me/app/pull/{p['number']}"
                       f"#issuecomment-{c['id']}"} for c in p["comments"]]})
elif cmd == ["pr", "comment"]:
    p = next(p for p in s["prs"] if p["number"] == int(args[2]))
    s["next_comment"] = s.get("next_comment", 5000) + 1
    p["comments"].append({"id": s["next_comment"], "body": stdin()})
    save()
elif cmd == ["pr", "edit"]:
    p = next(p for p in s["prs"] if p["number"] == int(args[2]))
    for n in (flag("--add-label") or "").split(","):
        if n and n not in p["labels"]:
            p["labels"].append(n)
    save()
elif cmd == ["pr", "checks"]:
    out([{"bucket": s.get("ci", "pass"), "name": "ci", "link": ""}])
elif cmd == ["pr", "diff"]:
    print("lib/feature.dart" if "--name-only" in args else "+++ b/lib/feature.dart\n+// feature")
elif args[0] == "api" and flag("-X") == "PATCH":
    cid = int(args[3].rsplit("/", 1)[1])
    body = json.loads(stdin())["body"]
    for p in s["prs"]:
        for c in p["comments"]:
            if c["id"] == cid:
                c["body"] = body
    save()
else:
    sys.exit(f"fake gh: unhandled {args}")
