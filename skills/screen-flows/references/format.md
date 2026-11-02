# The `.screens` format

One file per module under `docs/vault/screens/`, plus `00-app.screens` for the theme. The renderer
reads every `*.screens` file in the folder, in name order, and writes one self-contained
`index.html` beside them. A line is one element; two spaces of indentation nest a line under the
one above it. `#` starts a comment.

```
theme primary=#4F46E5 surface=#FFFFFF text=#111827 radius=12 font="Inter"

module M1 "Accounts"

screen SIGNIN-1 "Sign in" feature=M1.2
  intent "One field per line, primary action within thumb reach"
  appbar "Sign in"
  text h1 "Welcome back"
  field "Email" hint="you@example.com"
  field "Password" secure
  button "Sign in" -> HOME-1
  link "Forgot password?" -> SIGNIN-2
  state loading
  state error keep
    banner error "Wrong email or password"
```

## Line shape

`<kind> [words] ["text" ...] [key=value ...] [-> SCREEN-ID]`

- **kind** is one of the keywords below; anything else is an error.
- **words** are bare flags or variants: `secure`, `h1`, `secondary`, `back`.
- **"text"** is a quoted label. Kinds that take several (`tabs`, `chips`, `nav`) take several.
- **key=value** sets an attribute; quote a value with spaces.
- **`-> ID`** makes the element a link to that screen. A link to an ID that no file defines is an
  error, so the flow cannot point at a screen nobody drew.

## Top-level lines

| Line | Means |
|---|---|
| `theme key=value ...` | `primary`, `surface`, `text`, `muted`, `danger`, `radius` (px), `font`. Copy them from the app's design language once; the first `theme` line read wins |
| `module ID "Name"` | Groups the screens that follow, until the next `module` |
| `screen ID "Title" feature=M1.2` | A screen. `ID` is upper-case letters, digits and hyphens. `feature` is the feature-list ID it serves; several are comma-separated |

## Screen-level lines

| Line | Means |
|---|---|
| `intent "..."` | The design reasoning, shown beside the frame, not inside it. One per screen |
| `appbar "Title" [back] [menu] [-> ID]` | Top bar; `->` is where the back arrow goes. Kept in every state |
| `nav "A" "B" "C" selected=1 to=ID,ID,ID` | Bottom navigation; `to` links each item in order. Kept in every state |
| `fab "+" [-> ID]` | Floating action button. Kept in every state |
| `state NAME [keep]` | An alternative body. Its children **replace** the body; with `keep` they go **above** the normal body instead. `state loading` with no children draws the body as skeletons. A state showing a `sheet` or `dialog` takes `keep`, so the overlay sits over the screen rather than over an empty one. `appbar`, `nav` and `fab` stay outside states |

## Body elements

| Kind | Takes | Children |
|---|---|---|
| `text` | `h1` `h2` `body` `caption` `muted`, one "text" | — |
| `field` | "Label", `hint=`, `value=`, `error=`, `secure`, `multiline` | — |
| `select` | "Label", `value=` | — |
| `toggle`, `check` | "Label", `on` | — |
| `button` | "Label", `primary` (default) `secondary` `text` `danger`, `->` | — |
| `link` | "Label", `->` | — |
| `image` | optional "caption", `h=` height in px (default 160) | — |
| `avatar` | optional "Name" | — |
| `row` | "Title", optional "Subtitle", `meta=`, `avatar` or `image`, `->` | — |
| `list` | `rows=` (default 3) | its children are one row, drawn `rows` times |
| `card` | optional "Title", `->` | yes |
| `section` | "Heading" | yes |
| `tabs`, `chips` | several "text", `selected=` (1-based) | — |
| `banner` | `info` `error` `success` `warning`, "text" | — |
| `empty` | "Title", optional "Body" | yes, usually one button |
| `stat` | "Label", "Value" | — |
| `progress` | `value=` 0 to 100 | — |
| `sheet`, `dialog` | "Title", optional "Body" | yes, drawn over the screen |
| `divider`, `spacer` | — | — |

## What the renderer checks

It exits non-zero, naming the file and line of every problem, on an unknown kind, flag or
attribute, a duplicate screen ID, a `->` or `to=` to an undefined screen, a `state` with no children
other than `loading`, children under a kind that takes none, a screen with no `feature`, and any
malformed line: bad indentation, an unclosed quote, a number that is not one, or a screen-level kind
in the wrong place. Given `--features docs/vault/features.md`, it also
fails on a `feature=` ID the list does not have, and prints each feature with no screen.
