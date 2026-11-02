#!/usr/bin/env python3
"""render: turn a folder of `.screens` files into one self-contained HTML page of phone frames.

    render.py <dir>                        write <dir>/index.html
    render.py <dir> --out FILE             write FILE instead
    render.py <dir> --features FILE        also check every feature= against the feature list,
                                           and print each listed feature that no screen serves
    render.py <dir> --check                validate only; print errors and write nothing

The format is references/format.md. Every `*.screens` file in <dir> is read in name order. Each
mistake prints as `file:line: message`, all of them at once, and the exit is 1; a clean run prints
one summary line. The page needs no network: inline CSS, no script, no external fonts. It spends
no model tokens, and its checks are what let an agent trust the page without opening it.
"""

from __future__ import annotations

import argparse
import copy
import html
import pathlib
import re
import shlex
import sys
from dataclasses import dataclass, field

TOP = {"theme", "module", "screen"}
SCREEN_LEVEL = {"intent", "appbar", "nav", "fab", "state"}
CONTAINERS = {"list", "card", "section", "empty", "sheet", "dialog"}
# kind: (flags, attrs). The first bare word of module, screen and state is its name, not a flag.
VOCAB: dict[str, tuple[set, set]] = {
    "theme": (set(), {"primary", "surface", "text", "muted", "danger", "radius", "font"}),
    "module": (set(), set()),
    "screen": (set(), {"feature"}),
    "intent": (set(), set()),
    "appbar": ({"back", "menu"}, set()),
    "nav": (set(), {"selected", "to"}),
    "fab": (set(), set()),
    "state": ({"keep"}, set()),
    "text": ({"h1", "h2", "body", "caption", "muted"}, set()),
    "field": ({"secure", "multiline"}, {"hint", "value", "error"}),
    "select": (set(), {"value"}),
    "toggle": ({"on"}, set()),
    "check": ({"on"}, set()),
    "button": ({"primary", "secondary", "text", "danger"}, set()),
    "link": (set(), set()),
    "image": (set(), {"h"}),
    "avatar": (set(), set()),
    "row": ({"avatar", "image"}, {"meta"}),
    "list": (set(), {"rows"}),
    "card": (set(), set()),
    "section": (set(), set()),
    "tabs": (set(), {"selected"}),
    "chips": (set(), {"selected"}),
    "banner": ({"info", "error", "success", "warning"}, set()),
    "empty": (set(), set()),
    "stat": (set(), set()),
    "progress": (set(), {"value"}),
    "sheet": (set(), set()),
    "dialog": (set(), set()),
    "divider": (set(), set()),
    "spacer": (set(), set()),
}
BODY = set(VOCAB) - TOP - SCREEN_LEVEL
NUMERIC = {"h", "rows", "selected", "progress.value"}
LINKABLE = BODY | {"appbar", "fab"}
ID_RE = re.compile(r"[A-Z0-9][A-Z0-9-]*")
FEATURE_RE = re.compile(r"M\d+\.\d+")
COLOUR_RE = re.compile(r"#[0-9A-Fa-f]{3,8}|[A-Za-z]+|(?:rgb|rgba|hsl|hsla)\([0-9.,%\s/]+\)")
FONT_RE = re.compile(r"[\w .\-]+")
DEFAULT_THEME = {"primary": "#4F46E5", "surface": "#FFFFFF", "text": "#111827",
                 "muted": "#6B7280", "danger": "#DC2626", "radius": "12", "font": ""}


@dataclass
class Node:
    kind: str
    file: str
    line: int
    level: int = 0
    name: str = ""
    labels: list = field(default_factory=list)
    flags: list = field(default_factory=list)
    attrs: dict = field(default_factory=dict)
    target: str = ""
    children: list = field(default_factory=list)
    bad: bool = False


@dataclass
class Screen:
    node: Node
    id: str
    title: str
    features: list
    module: tuple


class Errors:
    def __init__(self) -> None:
        self.items: list[tuple[int, str, int, str]] = []
        self.order: dict[str, int] = {}

    def add(self, file: str, line: int, msg: str) -> None:
        self.items.append((self.order.get(file, len(self.order)), file, line, msg))

    def lines(self) -> list[str]:
        return [f"{f}:{ln}: {m}" if ln else f"{f}: {m}"
                for _, f, ln, m in sorted(set(self.items))]


# ---------------------------------------------------------------- parsing

def scan(text: str) -> list[str]:
    """Split a line into raw tokens, keeping their quotes, and stop at a `#` that starts a token
    (so `primary=#4F46E5` is a value and `# note` is a comment)."""
    toks, cur, quote, i = [], [], None, 0
    while i < len(text):
        c = text[i]
        if quote:
            cur.append(c)
            if c == "\\" and quote == '"' and i + 1 < len(text):
                cur.append(text[i + 1])
                i += 1
            elif c == quote:
                quote = None
        elif c.isspace():
            if cur:
                toks.append("".join(cur))
                cur = []
        elif c == "#" and not cur:
            break
        else:
            cur.append(c)
            if c in "\"'":
                quote = c
            elif c == "\\" and i + 1 < len(text):
                cur.append(text[i + 1])
                i += 1
        i += 1
    if cur:
        toks.append("".join(cur))
    return toks


def parse_line(toks: list[str], file: str, line: int, err: Errors) -> Node:
    head, target = toks, ""
    for i, t in enumerate(toks):
        if t.startswith("->"):
            head, tail = toks[:i], ([t[2:]] if t != "->" else []) + toks[i + 1:]
            if len(tail) != 1 or not ID_RE.fullmatch(tail[0]):
                err.add(file, line, "`->` takes exactly one screen ID (upper-case letters, digits, hyphens)")
            else:
                target = tail[0]
            break
    try:
        values = [shlex.split(t)[0] if shlex.split(t) else "" for t in head]
    except ValueError:
        err.add(file, line, "unclosed quote")
        return Node("?", file, line, bad=True)
    if not head:
        err.add(file, line, "line starts with `->`; the kind comes first")
        return Node("?", file, line, bad=True)
    if head[0][0] in "\"'" or values[0] not in VOCAB:
        err.add(file, line, f"unknown kind `{values[0]}` (kinds: {', '.join(sorted(VOCAB))})")
        return Node(values[0], file, line, bad=True)
    node = Node(values[0], file, line, target=target)
    for raw, val in zip(head[1:], values[1:]):
        if raw[0] in "\"'":
            node.labels.append(val)
        elif "=" in val:
            k, v = val.split("=", 1)
            node.attrs[k] = v
        else:
            node.flags.append(val)
    return node


def check_vocab(node: Node, err: Errors) -> None:
    k = node.kind
    if k in ("module", "screen", "state"):
        if not node.flags:
            what = {"module": "an ID", "screen": "an ID", "state": "a name"}[k]
            err.add(node.file, node.line, f"`{k}` needs {what} as its first word")
        else:
            node.name = node.flags.pop(0)
    flags, attrs = VOCAB[k]
    for f in node.flags:
        if f not in flags:
            takes = f"takes: {', '.join(sorted(flags))}" if flags else "takes no bare words"
            err.add(node.file, node.line, f"`{k}` does not take `{f}` ({takes})")
    for a, v in node.attrs.items():
        if a not in attrs:
            takes = f"takes: {', '.join(sorted(attrs))}" if attrs else "takes no attributes"
            err.add(node.file, node.line, f"`{k}` does not take `{a}=` ({takes})")
        elif (a in NUMERIC or f"{k}.{a}" in NUMERIC) and not v.isdigit():
            err.add(node.file, node.line, f"`{a}=` must be a whole number, got `{v}`")
    if node.target and k not in LINKABLE:
        hint = "; use to=" if k == "nav" else ""
        err.add(node.file, node.line, f"`{k}` cannot take `->`{hint}")


def parse_file(path: pathlib.Path, label: str, err: Errors) -> Node:
    root = Node("root", label, 0, level=-1)
    stack = [root]
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        toks = scan(raw)
        if not toks:
            continue
        ws = raw[:len(raw) - len(raw.lstrip(" \t"))]
        if "\t" in ws:
            err.add(label, lineno, "tab in indentation; indent with two spaces per level")
        elif len(ws) % 2:
            err.add(label, lineno, f"indented {len(ws)} spaces; indent with two spaces per level")
        level = len(ws.expandtabs(2)) // 2
        node = parse_line(toks, label, lineno, err)
        if not node.bad:
            check_vocab(node, err)
        if level > stack[-1].level + 1:
            err.add(label, lineno, f"indented more than one level past line {stack[-1].line}")
            level = stack[-1].level + 1
        while stack[-1].level >= level:
            stack.pop()
        node.level = level
        stack[-1].children.append(node)
        stack.append(node)
    check_context(root, err)
    return root


def takes_children(kind: str) -> bool:
    return kind in CONTAINERS or kind in ("screen", "state", "root")


def check_context(parent: Node, err: Errors) -> None:
    if not parent.bad and not takes_children(parent.kind) and parent.children:
        c = parent.children[0]
        err.add(c.file, c.line, f"`{parent.kind}` on line {parent.line} takes no children")
        return
    for c in parent.children:
        if not parent.bad and not c.bad:
            if c.kind in TOP and parent.kind != "root":
                err.add(c.file, c.line, f"`{c.kind}` cannot be indented")
            elif c.kind in SCREEN_LEVEL and parent.kind != "screen":
                err.add(c.file, c.line, f"`{c.kind}` goes directly under a screen")
            elif c.kind in BODY and parent.kind == "root":
                err.add(c.file, c.line, f"`{c.kind}` must be inside a screen")
        check_context(c, err)


def walk(node: Node):
    yield node
    for c in node.children:
        yield from walk(c)


def load(files: list[pathlib.Path], err: Errors):
    theme: dict | None = None
    modules: list[tuple] = []
    screens: list[Screen] = []
    seen: dict[str, Node] = {}
    for path in files:
        label = str(path)
        err.order.setdefault(label, len(err.order))
        root = parse_file(path, label, err)
        module = (None, path.stem)
        for top in root.children:
            if top.bad:
                continue
            if top.kind == "theme":
                for k, v in top.attrs.items():
                    ok = (v.isdigit() if k == "radius" else FONT_RE.fullmatch(v) if k == "font"
                          else COLOUR_RE.fullmatch(v) if k in VOCAB["theme"][1] else True)
                    if not ok:
                        err.add(top.file, top.line, f"theme `{k}={v}` is not a value the page can use")
                if theme is None:
                    theme = top.attrs
            elif top.kind == "module":
                module = (top.name or None, top.labels[0] if top.labels else top.name)
            elif top.kind == "screen":
                if module not in modules:
                    modules.append(module)
                screens.append(check_screen(top, module, seen, err))
    ids = set(seen)
    for s in screens:
        for n in walk(s.node):
            if n.bad:
                continue
            if n.target and n.target not in ids:
                err.add(n.file, n.line, f"`-> {n.target}`: no screen has that ID")
            if n.kind == "nav":
                tos = n.attrs.get("to", "").split(",") if n.attrs.get("to") else []
                if len(tos) > len(n.labels):
                    err.add(n.file, n.line, f"`to=` has {len(tos)} targets for {len(n.labels)} items")
                for t in tos:
                    if t.strip() and t.strip() not in ids:
                        err.add(n.file, n.line, f"`to={t.strip()}`: no screen has that ID")
    return theme or {}, modules, screens


def check_screen(node: Node, module: tuple, seen: dict, err: Errors) -> Screen:
    sid = node.name
    if sid and not ID_RE.fullmatch(sid):
        err.add(node.file, node.line, f"screen ID `{sid}` must be upper-case letters, digits and hyphens")
    if sid in seen:
        first = seen[sid]
        err.add(node.file, node.line, f"duplicate screen ID `{sid}` (first at {first.file}:{first.line})")
    elif sid:
        seen[sid] = node
    feats = [f.strip() for f in node.attrs.get("feature", "").split(",") if f.strip()]
    if not feats:
        err.add(node.file, node.line, f"screen `{sid}` has no feature=; name the feature it serves")
    counts: dict[str, int] = {}
    for c in node.children:
        if c.kind in ("intent", "appbar", "nav", "fab"):
            counts[c.kind] = counts.get(c.kind, 0) + 1
            if counts[c.kind] == 2:
                err.add(c.file, c.line, f"second `{c.kind}` in screen `{sid}`; a screen has one")
        if c.kind == "state" and not c.bad and not c.children and c.name not in ("", "loading"):
            err.add(c.file, c.line, f"state `{c.name}` has no children; only `state loading` may be empty")
    return Screen(node, sid, node.labels[0] if node.labels else sid, feats, module)


def read_features(path: pathlib.Path, err: Errors) -> dict[str, tuple[str, str]] | None:
    """Each feature ID's text and user flow, found by column header so the column order is free.
    A list with no Flow column gives every feature an empty flow."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        err.add(str(path), 0, f"cannot read the feature list ({e.strerror})")
        return None
    out: dict[str, tuple[str, str]] = {}
    col = {"feature": 2, "flow": None}
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        names = [c.lower() for c in cells]
        if "id" in names and "feature" in names:
            col = {"feature": names.index("feature"), "flow": names.index("flow") if "flow" in names else None}
            continue
        fid = cells[0].strip("*`") if cells else ""
        if FEATURE_RE.fullmatch(fid):
            get = lambda i: cells[i] if i is not None and i < len(cells) else ""
            out[fid] = (get(col["feature"]), get(col["flow"]))
    return out


# ---------------------------------------------------------------- rendering

def esc(s) -> str:
    return html.escape(str(s), quote=True)


def t(s, cls: str = "") -> str:
    return f'<span class="t{" " + cls if cls else ""}">{esc(s)}</span>'


def lab(n: Node, i: int = 0, default: str = "") -> str:
    return n.labels[i] if len(n.labels) > i else default


def num(n: Node, key: str, default: int) -> int:
    v = n.attrs.get(key, "")
    return int(v) if v.isdigit() else default


def wrap(n: Node, cls: str, inner: str, tag: str = "div") -> str:
    if n.target:
        return f'<a class="{cls}" href="#{esc(n.target)}">{inner}</a>'
    return f'<{tag} class="{cls}">{inner}</{tag}>'


def initials(name: str) -> str:
    return "".join(w[0] for w in name.split()[:2]).upper()


def natural(s: str):
    return [int(p) if p.isdigit() else p for p in re.split(r"(\d+)", s)]


class Ctx:
    def __init__(self, skel: bool = False) -> None:
        self.skel = skel
        self.overlays: list[str] = []


def children(nodes: list[Node], ctx: Ctx) -> str:
    out, stats = [], []
    for n in nodes:
        if n.bad:
            continue
        if n.kind == "stat":
            stats.append(el(n, ctx))
            continue
        if stats:
            out.append(f'<div class="stats">{"".join(stats)}</div>')
            stats = []
        out.append(el(n, ctx))
    if stats:
        out.append(f'<div class="stats">{"".join(stats)}</div>')
    return "".join(out)


def container(n: Node, cls: str, inner: str) -> str:
    # A container that links must not wrap its own links in an <a>, so a cover link sits under them.
    if n.target:
        return f'<div class="{cls} lk"><a class="cover" href="#{esc(n.target)}"></a>{inner}</div>'
    return f'<div class="{cls}">{inner}</div>'


def suffix_first_label(nodes: list[Node], k: int) -> None:
    for root in nodes:
        for n in walk(root):
            if n.labels:
                n.labels[0] = f"{n.labels[0]} {k}"
                return


def el(n: Node, ctx: Ctx) -> str:
    k, f = n.kind, set(n.flags)
    if k == "text":
        variant = next((v for v in ("h1", "h2", "caption", "body") if v in f), "body")
        return wrap(n, f"tx {variant}{' muted' if 'muted' in f else ''}", t(lab(n)), "p")
    if k == "field":
        value, hint = n.attrs.get("value", ""), n.attrs.get("hint", "")
        if "secure" in f and value:
            value = "•" * max(8, len(value))
        shown = t(value) if value else t(hint, "ph") if hint else ""
        eye = '<span class="eye"></span>' if "secure" in f else ""
        error = t(n.attrs["error"], "errt") if n.attrs.get("error") else ""
        inner = (t(lab(n), "lab") + f'<div class="inp{" ml" if "multiline" in f else ""}">{shown}{eye}</div>'
                 + error)
        return wrap(n, f"fld{' err' if error else ''}", inner)
    if k == "select":
        value = n.attrs.get("value", "")
        shown = t(value) if value else t("Select…", "ph")
        return wrap(n, "fld", t(lab(n), "lab") + f'<div class="inp">{shown}<span class="chev">▾</span></div>')
    if k == "toggle":
        return wrap(n, "tg", t(lab(n)) + f'<span class="sw{" on" if "on" in f else ""}"><i></i></span>')
    if k == "check":
        return wrap(n, "tg ck", f'<span class="cb{" on" if "on" in f else ""}"></span>' + t(lab(n)))
    if k == "button":
        variant = next((v for v in ("secondary", "text", "danger") if v in f), "primary")
        return wrap(n, f"btn {variant}", t(lab(n, 0, "Button")))
    if k == "link":
        return wrap(n, "lnk", t(lab(n, 0, "Link")))
    if k == "image":
        cap = t(lab(n), "cap") if n.labels else ""
        img = f'<div class="img" style="height:{num(n, "h", 160)}px"></div>'
        return wrap(n, "fig", img + cap)
    if k == "avatar":
        return wrap(n, "avr", f'<span class="av lg">{esc(initials(lab(n)))}</span>' + (t(lab(n)) if n.labels else ""))
    if k == "row":
        lead = ('<span class="av"></span>' if "avatar" in f
                else '<span class="thumb"></span>' if "image" in f else "")
        text = t(lab(n, 0, "Title"), "rt") + (t(lab(n, 1), "sub") if len(n.labels) > 1 else "")
        meta = t(n.attrs["meta"], "rm") if n.attrs.get("meta") else ""
        chev = '<span class="chev">›</span>' if n.target else ""
        return wrap(n, "row", f'{lead}<span class="rx">{text}</span>{meta}{chev}')
    if k == "list":
        kids = n.children or [Node("row", n.file, n.line, labels=["List item"])]
        reps = []
        for i in range(1, min(num(n, "rows", 3), 50) + 1):
            rep = copy.deepcopy(kids)
            if i > 1:
                suffix_first_label(rep, i)
            reps.append(f'<div class="li">{children(rep, ctx)}</div>')
        rows = all(c.kind == "row" for c in kids)
        return container(n, f"lst{' rows' if rows else ''}", "".join(reps))
    if k == "card":
        title = f'<div class="ct">{t(lab(n))}</div>' if n.labels else ""
        return container(n, "card", title + children(n.children, ctx))
    if k == "section":
        return container(n, "sec", f'<div class="sh">{t(lab(n))}</div>' + children(n.children, ctx))
    if k in ("tabs", "chips"):
        sel = num(n, "selected", 1 if k == "tabs" else 0)
        items = "".join(f'<span class="{k[:-1]}{" sel" if i == sel else ""}">{t(x)}</span>'
                        for i, x in enumerate(n.labels, 1))
        return wrap(n, k, items)
    if k == "banner":
        variant = next((v for v in ("error", "success", "warning") if v in f), "info")
        icon = {"info": "i", "error": "!", "success": "✓", "warning": "!"}[variant]
        return wrap(n, f"ban {variant}", f'<span class="bi">{icon}</span>' + t(lab(n)))
    if k == "empty":
        body = t(lab(n, 1), "eb") if len(n.labels) > 1 else ""
        return container(n, "emp", '<div class="ill"></div>' + t(lab(n, 0, "Nothing here"), "et") + body
                         + children(n.children, ctx))
    if k == "stat":
        return wrap(n, "stat", t(lab(n), "sl") + t(lab(n, 1, "—"), "sv"))
    if k == "progress":
        return wrap(n, "prog", f'<i style="width:{min(num(n, "value", 0), 100)}%"></i>')
    if k in ("sheet", "dialog"):
        body = f'<p class="pb">{t(lab(n, 1))}</p>' if len(n.labels) > 1 else ""
        inner = ('<i class="handle"></i>' if k == "sheet" else "") + f'<div class="pt">{t(lab(n))}</div>' + body
        ctx.overlays.append(f'<div class="ov {k}">{container(n, "panel", inner + children(n.children, ctx))}</div>')
        return ""
    if k == "divider":
        return '<hr class="dv">'
    if k == "spacer":
        return '<div class="sp"></div>'
    return ""


def view(body: list[Node], cls: str, skel: bool = False, above: list[Node] | None = None) -> str:
    ctx = Ctx(skel)
    inner = (children(above, ctx) if above else "") + children(body, ctx)
    overlays = "" if skel else "".join(ctx.overlays)
    return (f'<div class="view {cls}"><div class="scroll{" skel" if skel else ""}">{inner}</div>'
            f"{overlays}</div>")


def appbar(n: Node) -> str:
    f = set(n.flags)
    back = ""
    if "back" in f or n.target:
        back = (f'<a class="ic" href="#{esc(n.target)}">←</a>' if n.target else '<span class="ic">←</span>')
    menu = '<span class="ic">☰</span>' if "menu" in f else ""
    return f'<div class="appbar">{back}{t(lab(n), "ttl")}{menu}</div>'


def nav(n: Node) -> str:
    tos = [x.strip() for x in n.attrs.get("to", "").split(",")] if n.attrs.get("to") else []
    sel = num(n, "selected", 1)
    items = []
    for i, label in enumerate(n.labels, 1):
        cls = f'ni{" sel" if i == sel else ""}'
        inner = f"<i></i>{t(label)}"
        to = tos[i - 1] if i <= len(tos) else ""
        items.append(f'<a class="{cls}" href="#{esc(to)}">{inner}</a>' if to else f'<span class="{cls}">{inner}</span>')
    return f'<div class="nav">{"".join(items)}</div>'


def screen_html(s: Screen) -> str:
    kids = [c for c in s.node.children if not c.bad]
    one = {c.kind: c for c in reversed(kids) if c.kind in ("intent", "appbar", "nav", "fab")}
    states = [c for c in kids if c.kind == "state"]
    body = [c for c in kids if c.kind in BODY]
    sid = esc(s.id)
    views = [view(body, "v0" if states else "solo")]
    for i, st in enumerate(states, 1):
        if not st.children:
            views.append(view(body, f"v{i}", skel=True))
        elif "keep" in st.flags:
            views.append(view(body, f"v{i}", above=st.children))
        else:
            views.append(view(st.children, f"v{i}"))
    radios = tabs = ""
    if states:
        names = ["default"] + [st.name for st in states]
        radios = "".join(f'<input type="radio" class="r r{i}" name="st-{sid}" id="st-{sid}-{i}"'
                         f'{" checked" if i == 0 else ""}>' for i in range(len(names)))
        tabs = '<div class="stabs">' + "".join(f'<label for="st-{sid}-{i}">{esc(nm)}</label>'
                                               for i, nm in enumerate(names)) + "</div>"
    fab = ""
    if "fab" in one:
        n = one["fab"]
        fab = wrap(n, f'fab{" up" if "nav" in one else ""}', esc(lab(n, 0, "+")))
    phone = ('<div class="sbar"><span>9:41</span><span>▴ ▮</span></div>'
             + (appbar(one["appbar"]) if "appbar" in one else "")
             + "".join(views) + (nav(one["nav"]) if "nav" in one else "") + fab)
    feats = "".join(f'<span class="fid">{esc(x)}</span>' for x in s.features)
    intent = (f'<p class="intent"><b>Intent</b>{esc(lab(one["intent"]))}</p>' if "intent" in one else "")
    return (f'<article class="scr" id="{sid}"><div class="meta"><span class="sid">{sid}</span>'
            f'<h3>{esc(s.title)}</h3>{feats}</div><div class="pair"><div class="col">{radios}{tabs}'
            f'<div class="frame"><div class="phone">{phone}</div></div></div>{intent}</div></article>')


def edges(s: Screen) -> list[tuple[str, str, str]]:
    out = []
    for n in walk(s.node):
        if n.target and not n.bad:
            what = lab(n, 0, n.kind) if n.kind != "appbar" else "back"
            if (s.id, what, n.target) not in out:
                out.append((s.id, what, n.target))
    return out


def count_links(screens: list[Screen]) -> int:
    total = 0
    for s in screens:
        for n in walk(s.node):
            if n.bad:
                continue
            total += bool(n.target)
            if n.kind == "nav":
                total += sum(1 for x in n.attrs.get("to", "").split(",") if x.strip())
    return total


def css(theme: dict, max_states: int) -> str:
    th = {**DEFAULT_THEME, **{k: v for k, v in theme.items() if v}}
    font = (f'"{th["font"]}", ' if th["font"] else "") + 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'
    state_rules = "".join(
        f".r{i}:checked~.frame .v{i}{{display:flex}}"
        f".r{i}:checked~.stabs label:nth-of-type({i + 1}){{background:#1F2937;color:#fff;border-color:#1F2937}}"
        for i in range(max_states + 1))
    return f"""
:root{{--primary:{th['primary']};--surface:{th['surface']};--text:{th['text']};--muted:{th['muted']};
--danger:{th['danger']};--radius:{th['radius']}px;--font:{font};--line:#E5E7EB;--fill:#F3F4F6;
--skel:#E2E5E9;--ok:#15803D;--warn:#B45309;--info:#1D4ED8}}
*{{box-sizing:border-box}}
body{{margin:0;background:#F1F2F4;color:#1F2328;font:14px/1.45 var(--font)}}
a{{color:inherit;text-decoration:none}}
.top{{padding:28px 32px 4px}}.top h1{{margin:0;font-size:24px}}.top p{{margin:4px 0 0;color:#5B616B}}
.toc{{padding:12px 32px 0;display:flex;gap:8px;flex-wrap:wrap}}
.toc a{{padding:4px 12px;border-radius:999px;background:#fff;border:1px solid #DADDE2;font-size:13px}}
.flows,.mod{{padding:4px 32px 16px}}
h2{{font-size:18px;margin:24px 0 14px;padding-bottom:6px;border-bottom:1px solid #D9DCE1}}
.flow{{background:#fff;border:1px solid #E3E5E8;border-radius:10px;padding:12px 16px;margin-bottom:10px}}
.fl{{font-size:15px;margin:18px 0 8px;color:#374151}}
.fh b{{font-family:ui-monospace,Menlo,monospace;margin-right:8px}}.fh span{{color:#4B5563}}
.strip{{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin:10px 0 6px}}
.sc{{display:inline-flex;gap:6px;align-items:baseline;padding:4px 10px;border-radius:999px;
background:#F3F4F6;border:1px solid #DADDE2;font-size:13px}}
.sc:hover,.edges a:hover{{border-color:var(--primary);color:var(--primary)}}
.sc code{{font-weight:600}}.arr{{color:#9CA3AF}}
.edges{{margin:0;padding:0;list-style:none;font-size:12.5px;color:#4B5563;columns:2 300px}}
.edges a{{font-family:ui-monospace,Menlo,monospace;font-weight:600;color:#1F2328}}
.grid{{display:flex;flex-wrap:wrap;gap:44px 56px}}
.scr{{scroll-margin-top:16px}}
.meta{{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap;margin-bottom:10px;max-width:620px}}
.sid{{font:600 12px ui-monospace,Menlo,monospace;background:#E2E5E9;padding:2px 7px;border-radius:4px}}
.meta h3{{margin:0;font-size:15px}}
.fid{{font-size:11px;color:#4B5563;border:1px solid #CDD1D6;border-radius:999px;padding:0 7px}}
.pair{{display:flex;gap:20px;align-items:flex-start;flex-wrap:wrap}}
.intent{{width:220px;margin:34px 0 0;font-size:13px;color:#374151;border-left:3px solid #CDD1D6;padding:2px 0 2px 12px}}
.intent b{{display:block;font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:#8B929C;margin-bottom:2px}}
.r{{position:absolute;opacity:0;pointer-events:none}}
.stabs{{display:flex;gap:4px;margin-bottom:8px;flex-wrap:wrap;max-width:380px}}
.stabs label{{font-size:12px;padding:2px 10px;border-radius:999px;border:1px solid #CDD1D6;background:#fff;cursor:pointer}}
.frame{{width:380px;padding:10px;border-radius:46px;background:#1F2937;box-shadow:0 10px 28px rgba(0,0,0,.16);transition:box-shadow .2s}}
.scr:target .frame{{box-shadow:0 0 0 5px var(--primary),0 10px 28px rgba(0,0,0,.2)}}
.scr:target .sid{{background:var(--primary);color:#fff}}
.phone{{position:relative;width:360px;height:740px;border-radius:36px;overflow:hidden;background:var(--surface);
color:var(--text);display:flex;flex-direction:column;font:15px/1.4 var(--font)}}
.sbar{{flex:none;height:30px;display:flex;justify-content:space-between;align-items:flex-end;padding:0 26px 4px;font-size:12px;font-weight:600}}
.appbar{{flex:none;height:52px;display:flex;align-items:center;gap:6px;padding:0 10px;border-bottom:1px solid var(--line)}}
.ttl{{flex:1;padding-left:6px;font-size:17px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.ic{{width:36px;height:36px;display:grid;place-items:center;font-size:19px;border-radius:50%;flex:none}}
a.ic:hover{{background:var(--fill)}}
.view{{display:none;flex:1;min-height:0;flex-direction:column}}.view.solo{{display:flex}}
.scroll{{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:12px}}
.scroll>*,.card>*,.sec>*,.emp>*,.panel>*,.li>*{{flex:none}}
.nav{{flex:none;display:flex;height:64px;border-top:1px solid var(--line);background:var(--surface)}}
.ni{{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;font-size:11px;color:var(--muted)}}
.ni i{{width:22px;height:22px;border-radius:7px;background:currentColor;opacity:.3}}
.ni.sel{{color:var(--primary);font-weight:600}}.ni.sel i{{opacity:1}}
.fab{{position:absolute;right:16px;bottom:24px;width:56px;height:56px;border-radius:16px;background:var(--primary);
color:#fff;display:grid;place-items:center;font-size:24px;box-shadow:0 4px 12px rgba(0,0,0,.25);z-index:3}}
.fab.up{{bottom:80px}}
.tx{{margin:0}}.tx.h1{{font-size:26px;font-weight:700;line-height:1.2}}.tx.h2{{font-size:19px;font-weight:600}}
.tx.caption{{font-size:12px;color:var(--muted)}}.tx.muted{{color:var(--muted)}}
.fld{{display:flex;flex-direction:column;gap:5px}}.lab{{font-size:13px;font-weight:500}}
.inp{{min-height:46px;display:flex;align-items:center;gap:8px;padding:0 12px;border:1px solid #CDD1D6;border-radius:var(--radius)}}
.inp>.t{{flex:1}}.inp.ml{{min-height:96px;align-items:flex-start;padding-top:12px}}
.ph{{color:var(--muted)}}.fld.err .inp{{border-color:var(--danger)}}.errt{{font-size:12px;color:var(--danger)}}
.eye{{width:18px;height:10px;border:2px solid var(--muted);border-radius:50%}}
.chev{{color:var(--muted);margin-left:auto}}
.tg{{display:flex;align-items:center;justify-content:space-between;gap:12px;min-height:40px}}
.tg.ck{{justify-content:flex-start}}
.sw{{width:44px;height:26px;border-radius:13px;background:#CDD1D6;position:relative;flex:none}}
.sw i{{position:absolute;top:3px;left:3px;width:20px;height:20px;border-radius:50%;background:#fff;box-shadow:0 1px 2px rgba(0,0,0,.3)}}
.sw.on{{background:var(--primary)}}.sw.on i{{left:21px}}
.cb{{width:20px;height:20px;border:2px solid #9CA3AF;border-radius:5px;flex:none;display:grid;place-items:center}}
.cb.on{{background:var(--primary);border-color:var(--primary)}}.cb.on::after{{content:"✓";color:#fff;font-size:13px}}
.btn{{display:flex;align-items:center;justify-content:center;min-height:48px;padding:0 18px;border-radius:var(--radius);
font-weight:600;border:1.5px solid transparent;text-align:center}}
.btn.primary{{background:var(--primary);color:#fff}}.btn.secondary{{border-color:var(--primary);color:var(--primary)}}
.btn.text{{color:var(--primary);min-height:40px}}.btn.danger{{background:var(--danger);color:#fff}}
a.btn:hover,a.row:hover,a.ni:hover,.lk:hover{{filter:brightness(.96)}}
.lnk{{color:var(--primary);text-decoration:underline;font-weight:500;align-self:flex-start}}
.img{{border-radius:var(--radius);background:linear-gradient(to top right,transparent calc(50% - 1px),#C3C8CF,transparent calc(50% + 1px)),
linear-gradient(to bottom right,transparent calc(50% - 1px),#C3C8CF,transparent calc(50% + 1px)),var(--fill);border:1px solid var(--line)}}
.fig{{display:flex;flex-direction:column;gap:6px}}.cap{{font-size:12px;color:var(--muted);text-align:center}}
.avr{{display:flex;align-items:center;gap:12px;font-weight:600}}
.av{{width:40px;height:40px;border-radius:50%;background:#D5D9DF;color:#4B5563;display:grid;place-items:center;flex:none;font-size:13px;font-weight:600}}
.av.lg{{width:56px;height:56px;font-size:18px}}
.thumb{{width:48px;height:48px;border-radius:calc(var(--radius) * .6);background:var(--fill);border:1px solid var(--line);flex:none}}
.row{{display:flex;align-items:center;gap:12px;padding:10px 0;min-height:56px}}
.rx{{flex:1;min-width:0;display:flex;flex-direction:column}}.rt{{font-weight:500}}.sub{{font-size:13px;color:var(--muted)}}
.rm{{font-size:12px;color:var(--muted);white-space:nowrap}}.row .chev{{margin-left:0;font-size:20px}}
.lst{{display:flex;flex-direction:column;gap:12px}}.lst.rows{{gap:0}}.lst.rows .li+.li{{border-top:1px solid var(--line)}}
.li{{display:flex;flex-direction:column;gap:8px}}
.card{{border:1px solid var(--line);border-radius:var(--radius);padding:14px;display:flex;flex-direction:column;gap:10px;background:var(--surface);box-shadow:0 1px 2px rgba(0,0,0,.05)}}
.ct{{font-weight:600}}
.lk{{position:relative}}.lk>*:not(.cover){{position:relative;pointer-events:none}}.lk a:not(.cover){{pointer-events:auto}}
.cover{{position:absolute;inset:0;z-index:0;border-radius:inherit}}
.sec{{display:flex;flex-direction:column;gap:10px}}
.sh{{font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin-top:4px}}
.tabs{{display:flex;border-bottom:1px solid var(--line);overflow:hidden}}
.tab{{flex:1;text-align:center;padding:10px 4px;font-size:14px;color:var(--muted);border-bottom:2px solid transparent;white-space:nowrap}}
.tab.sel{{color:var(--primary);border-color:var(--primary);font-weight:600}}
.chips{{display:flex;gap:8px;flex-wrap:wrap}}
.chip{{padding:5px 12px;border-radius:999px;border:1px solid #CDD1D6;font-size:13px}}
.chip.sel{{background:color-mix(in srgb,var(--primary) 14%,transparent);border-color:var(--primary);color:var(--primary);font-weight:500}}
.ban{{display:flex;align-items:flex-start;gap:10px;padding:10px 12px;border-radius:var(--radius);font-size:14px;
background:color-mix(in srgb,var(--c) 10%,var(--surface));border:1px solid color-mix(in srgb,var(--c) 35%,transparent);color:var(--c)}}
.ban.info{{--c:var(--info)}}.ban.error{{--c:var(--danger)}}.ban.success{{--c:var(--ok)}}.ban.warning{{--c:var(--warn)}}
.bi{{width:20px;height:20px;border-radius:50%;background:var(--c);color:#fff;display:grid;place-items:center;font-size:12px;font-weight:700;flex:none}}
.emp{{display:flex;flex-direction:column;align-items:center;text-align:center;gap:10px;padding:28px 8px}}
.ill{{width:96px;height:96px;border-radius:50%;background:var(--fill);border:1px solid var(--line)}}
.et{{font-size:17px;font-weight:600}}.eb{{color:var(--muted);font-size:14px}}.emp>.btn{{align-self:stretch}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px}}
.stat{{border:1px solid var(--line);border-radius:var(--radius);padding:12px;display:flex;flex-direction:column;gap:2px}}
.sl{{font-size:12px;color:var(--muted)}}.sv{{font-size:22px;font-weight:700}}
.prog{{height:8px;border-radius:4px;background:var(--fill);overflow:hidden}}.prog i{{display:block;height:100%;background:var(--primary)}}
.dv{{border:0;border-top:1px solid var(--line);margin:0;width:100%}}.sp{{height:16px}}
.ov{{position:absolute;inset:0;background:rgba(17,24,39,.45);display:flex;z-index:5}}
.ov.sheet{{align-items:flex-end}}.ov.dialog{{align-items:center;justify-content:center;padding:24px}}
.panel{{background:var(--surface);display:flex;flex-direction:column;gap:12px;padding:18px;width:100%;max-height:85%;overflow:auto}}
.sheet .panel{{border-radius:calc(var(--radius) * 1.5) calc(var(--radius) * 1.5) 0 0;padding-bottom:28px}}
.dialog .panel{{border-radius:calc(var(--radius) * 1.5);box-shadow:0 10px 30px rgba(0,0,0,.25)}}
.handle{{width:40px;height:4px;border-radius:2px;background:#CDD1D6;align-self:center}}
.pt{{font-size:18px;font-weight:600}}.pb{{margin:0;color:var(--muted);font-size:14px}}
.skel *{{color:transparent!important;border-color:var(--skel)!important;box-shadow:none!important}}
.skel .t{{background:var(--skel);border-radius:4px}}.skel .rx{{gap:5px;align-items:flex-start}}
.skel .btn,.skel .img,.skel .av,.skel .thumb,.skel .sw,.skel .cb,.skel .chip,.skel .bi,.skel .ill,.skel .prog i{{background:var(--skel)!important}}
.skel .sw i,.skel .eye,.skel .chev{{visibility:hidden}}
.skel{{animation:pulse 1.6s ease-in-out infinite}}
@keyframes pulse{{50%{{opacity:.55}}}}
{state_rules}
"""


def page(theme: dict, modules: list[tuple], screens: list[Screen],
         features: dict[str, tuple[str, str]]) -> str:
    by_feature: dict[str, list[Screen]] = {}
    for s in screens:
        for fid in s.features:
            by_feature.setdefault(fid, []).append(s)
    # User flows in the order the feature list first names them, since that is the order the
    # sprints take them in; features with no flow come last.
    order = list(dict.fromkeys(fl for _, fl in features.values() if fl))
    flow_of = lambda fid: features.get(fid, ("", ""))[1]
    rank = lambda fid: (order.index(flow_of(fid)) if flow_of(fid) in order else len(order), natural(fid))
    flows, current = [], None
    for fid in sorted(by_feature, key=rank):
        if order and flow_of(fid) != current:
            current = flow_of(fid)
            flows.append(f'<h3 class="fl">{esc(current or "No flow")}</h3>')
        strip = '<span class="arr">→</span>'.join(
            f'<a class="sc" href="#{esc(s.id)}"><code>{esc(s.id)}</code>{esc(s.title)}</a>'
            for s in by_feature[fid])
        es = [e for s in by_feature[fid] for e in edges(s)]
        items = "".join(f'<li><a href="#{esc(a)}">{esc(a)}</a> “{esc(w)}” → <a href="#{esc(b)}">{esc(b)}</a></li>'
                        for a, w, b in es)
        text = f"<span>{esc(features[fid][0])}</span>" if features.get(fid, ("",))[0] else ""
        flows.append(f'<div class="flow"><div class="fh"><b>{esc(fid)}</b>{text}</div>'
                     f'<div class="strip">{strip}</div>{"<ul class=edges>" + items + "</ul>" if items else ""}</div>')
    mods, toc = [], []
    for i, (mid, name) in enumerate(modules):
        anchor = f"mod-{i + 1}"
        heading = f"{esc(mid)} · {esc(name)}" if mid and name != mid else esc(name or mid)
        toc.append(f'<a href="#{anchor}">{heading}</a>')
        body = "".join(screen_html(s) for s in screens if s.module == (mid, name))
        mods.append(f'<section class="mod" id="{anchor}"><h2>{heading}</h2><div class="grid">{body}</div></section>')
    max_states = max([sum(1 for c in s.node.children if c.kind == "state") for s in screens] or [0])
    summary = f"{len(screens)} screens · {len(by_feature)} features · {count_links(screens)} links"
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1"><title>Screen flows</title>'
            f"<style>{css(theme, max_states)}</style></head><body>"
            f'<header class="top"><h1>Screen flows</h1><p>{summary}. Click any button, row or tab to follow the flow.</p></header>'
            f'<nav class="toc"><a href="#flows">Flows</a>{"".join(toc)}</nav>'
            f'<section class="flows" id="flows"><h2>Flows</h2>{"".join(flows)}</section>'
            f'{"".join(mods)}</body></html>\n')


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Render *.screens files into one HTML page.")
    ap.add_argument("dir")
    ap.add_argument("--out")
    ap.add_argument("--features")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    src = pathlib.Path(a.dir)
    err = Errors()
    files = sorted(src.glob("*.screens")) if src.is_dir() else []
    if not files:
        print(f"{src}: no .screens files here")
        return 1
    theme, modules, screens = load(files, err)
    features: dict[str, tuple[str, str]] = {}
    if a.features:
        listed = read_features(pathlib.Path(a.features), err)
        if listed is not None:
            features = listed
            for s in screens:
                for fid in s.features:
                    if fid not in features:
                        err.add(s.node.file, s.node.line, f"feature `{fid}` is not in {a.features}")
    if err.items:
        print("\n".join(err.lines()))
        return 1
    served = {fid for s in screens for fid in s.features}
    out = pathlib.Path(a.out) if a.out else src / "index.html"
    head = f"{len(screens)} screens, {len(served)} features, {count_links(screens)} links"
    if a.check:
        print(f"{head}, no errors (--check: nothing written)")
    else:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(theme, modules, screens, features), encoding="utf-8")
        print(f"{head} → {out}")
    for fid, (text, _) in features.items():
        if fid not in served:
            print(f"no screen: {fid} {text}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
