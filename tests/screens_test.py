#!/usr/bin/env python3
"""Tests for the screen-flows renderer: the example renders with every screen and link, and each
check the format promises fails naming the file and line.

    python3 tests/screens_test.py      prints one line per failure and exits non-zero on any
"""

import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills/screen-flows"
RENDER = SKILL / "scripts/render.py"
EXAMPLE = SKILL / "references/example.screens"

FAIL: list[str] = []


def expect(label: str, got, want) -> None:
    if got != want:
        FAIL.append(f"{label}: got {got!r}, want {want!r}")


def render(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(RENDER), *map(str, args)], capture_output=True, text=True)


VALID = """\
module M1 "Test"
screen A-1 "A" feature=M1.1
  intent "x"
  button "Go" -> B-1
screen B-1 "B" feature=M1.1
  text "hi"
"""

# label, file body, the line the error must name
BAD = [
    ("unknown kind", VALID + "  buton \"Go\"\n", 7),
    ("duplicate ID", VALID + "screen A-1 \"Again\" feature=M1.1\n", 7),
    ("broken ->", VALID + "  link \"Nowhere\" -> C-9\n", 7),
    ("broken to=", VALID + "  nav \"A\" \"B\" to=A-1,C-9\n", 7),
    ("empty state", VALID + "  state error\n", 7),
    ("children under a leaf", VALID + "  button \"x\"\n    text \"y\"\n", 8),
    ("missing feature", VALID + "screen C-1 \"C\"\n", 7),
    ("odd indentation", VALID + "   text \"three spaces\"\n", 7),
    ("tab indentation", VALID + "\ttext \"tab\"\n", 7),
    ("unknown flag", VALID + "  button primery \"x\"\n", 7),
]


def cases(tmp: pathlib.Path) -> None:
    out = tmp / "out.html"
    r = render(EXAMPLE.parent, "--out", out)
    expect("example: exit", r.returncode, 0)
    expect("example: index.html written", out.exists(), True)
    expect("example: nothing written beside the sources", (EXAMPLE.parent / "index.html").exists(), False)
    page = out.read_text() if out.exists() else ""
    src = EXAMPLE.read_text()
    for sid in re.findall(r"^screen (\S+)", src, re.M):
        expect(f"example: screen {sid} drawn", f'id="{sid}"' in page, True)
    targets = set(re.findall(r"-> (\S+)", src))
    for to in re.findall(r"to=(\S+)", src):
        targets |= set(to.split(","))
    for t in sorted(targets):
        expect(f"example: link to {t}", f'href="#{t}"' in page, True)
    expect("example: state tabs", 'for="st-ITEMS-1-2">empty<' in page, True)
    expect("example: skeleton for loading", "skel" in page, True)
    expect("example: summary line", bool(re.match(r"\d+ screens, \d+ features, \d+ links → ", r.stdout)), True)

    for label, body, line in BAD:
        d = tmp / re.sub(r"\W+", "-", label)
        d.mkdir()
        (d / "t.screens").write_text(body)
        r = render(d)
        expect(f"{label}: exit", r.returncode, 1)
        expect(f"{label}: names t.screens:{line}", f"t.screens:{line}:" in r.stdout, True)
        expect(f"{label}: writes nothing", (d / "index.html").exists(), False)

    d = tmp / "all-errors"
    d.mkdir()
    (d / "t.screens").write_text(VALID + "  buton \"x\"\n  link \"y\" -> C-9\n")
    r = render(d)
    expect("every error reported, not the first", ("t.screens:7:" in r.stdout, "t.screens:8:" in r.stdout),
           (True, True))

    d = tmp / "check"
    d.mkdir()
    (d / "t.screens").write_text(VALID)
    r = render(d, "--check")
    expect("--check: exit", r.returncode, 0)
    expect("--check: writes nothing", (d / "index.html").exists(), False)
    r = render(d)
    expect("default out is <dir>/index.html", (r.returncode, (d / "index.html").exists()), (0, True))

    feats = tmp / "features.md"
    feats.write_text("| ID | Module | Feature |\n|---|---|---|\n"
                     "| M1.1 | Test | A user can go |\n| M1.2 | Test | A user can stop |\n")
    r = render(d, "--check", "--features", feats)
    expect("--features: exit", r.returncode, 0)
    expect("--features: uncovered feature listed", "no screen: M1.2 A user can stop" in r.stdout, True)
    expect("--features: covered feature not listed", "no screen: M1.1" in r.stdout, False)

    flows = tmp / "flows"
    flows.mkdir()
    (flows / "t.screens").write_text(VALID + "screen C-1 \"C\" feature=M1.2\n  text \"c\"\n")
    ff = tmp / "flow-features.md"
    ff.write_text("| ID | Module | Feature | Flow | Priority |\n|---|---|---|---|---|\n"
                  "| M1.2 | Test | A user can stop | Onboarding | Must |\n"
                  "| M1.1 | Test | A user can go | Browse | Must |\n")
    r = render(flows, "--features", ff)
    page = (flows / "index.html").read_text() if r.returncode == 0 else ""
    expect("flows: exit", r.returncode, 0)
    expect("flows: grouped in the feature list's order",
           0 <= page.find(">Onboarding<") < page.find(">Browse<"), True)
    expect("flows: feature text read by header, not position", "A user can go" in page, True)

    d = tmp / "unknown-feature"
    d.mkdir()
    (d / "t.screens").write_text(VALID.replace("B-1 \"B\" feature=M1.1", "B-1 \"B\" feature=M9.9"))
    r = render(d, "--features", feats)
    expect("unknown feature: exit", r.returncode, 1)
    expect("unknown feature: names the screen line", "t.screens:5:" in r.stdout and "M9.9" in r.stdout, True)


tmp = pathlib.Path(tempfile.mkdtemp())
try:
    cases(tmp)
finally:
    shutil.rmtree(tmp, ignore_errors=True)
for f in FAIL:
    print(f"FAIL {f}")
print(f"{'ok' if not FAIL else str(len(FAIL)) + ' failure(s)'}")
sys.exit(1 if FAIL else 0)
