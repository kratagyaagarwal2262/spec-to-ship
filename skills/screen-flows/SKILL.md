---
name: screen-flows
description: Draw every screen a feature or a phase needs, with its states and the user flow between screens, as short .screens files a script renders into one HTML page for the user and the client to review in a browser, in place of design frames. Use when /fk-plan reaches design and no designer supplies frames, when a feature being specified has screens nobody has drawn, or when the user asks for wireframes, mockups, screen designs or a user flow.
---

# Screen flows

A feature list says what a user can do; it does not show what they will see, and a client agrees to
a list very differently from how they react to a screen. Design frames close that gap, but a project
without a designer has none, and having an agent write HTML for every screen spends far more than
the review is worth.

So the agent writes only a short description of each screen, about a dozen lines, in the format in
[format.md](references/format.md). The `scripts/render.py` beside this file turns every description
into one self-contained page, checks the links and states, and costs nothing to run. The agent never
writes HTML or CSS, and never looks at the page: the renderer's checks are the proof.

## 1. Scope

Take the features in scope: the current phase's when `/fk-plan` is drawing a phase, or the one
feature being specified. Read their rows in `docs/vault/features.md`, and the `.screens` files in
`docs/vault/screens/` for their modules only, where they exist.

Where `docs/vault/screens/00-app.screens` has no `theme` line, write one from the colour roles,
radius and type family in `docs/agents/design.md`. That is the only read of the design language
this skill makes; where it does not exist yet, leave the theme out and the page draws in neutral
grey.

The step is done when you have listed the features in scope by ID, and the screens already drawn
for them.

## 2. Plan each flow

Work flow by flow, in the order of the feature list's **Flow** column, which is the order sprints
build them. For each feature, name the screens a user passes through from where they start to where
the feature is done, by ID, as a line such as `SIGNIN-1 → SIGNIN-2 → HOME-1`. Reuse a screen that exists rather
than drawing a near copy: a screen serving two features lists both.

Then name each screen's states. A screen that loads data has `loading`; one that lists things has
`empty`; one where an action can fail has `error`. Each state the requirement already settled, in
`grill` or the spec, appears as one.

The step is done when every feature in scope has a start screen, an end screen and a link between
each step, and every screen has its states named.

## 3. Write

One file per module, `NN-<module-slug>.screens`, numbered in the proposal's module order. Every
screen gets:

- an `intent` line: one sentence on what the screen puts first and why, such as "one task per
  screen: the user is mid-errand and glancing". This is the design reasoning the reviewer judges.
- the copy a user will actually read, in the glossary's words. Placeholder text hides the decisions
  a review exists to catch.
- only the elements it needs. A screen past about twenty lines is usually two screens.

The step is done when every screen from step 2 is written, with its states and its `->` links.

## 4. Render

Run, from the project root:

```
python3 <this skill's folder>/scripts/render.py docs/vault/screens --features docs/vault/features.md
```

Fix every line it reports and run it again until it exits cleanly. A `no screen:` line for a
feature in scope that has a user interface is a screen step 2 missed; one for a feature with no
interface, such as a pipeline or a store account, is expected.

Commit `index.html` with the `.screens` files, so anyone can open it without running anything. It
is regenerated on every render, so a merge conflict in it is resolved by rendering again.

The step is done when the renderer exits 0.

## 5. Review

Tell the user to open `docs/vault/screens/index.html` in a browser; its Flows section groups the
features under their user flow, in delivery order. In the reply, give each feature's line from
step 2, grouped the same way, and the two or three `intent` decisions most worth
questioning. Where the vault index has no link to the page, add one under **Project**.

Changes come back by screen ID ("SIGNIN-1: social sign-in first"). Edit only that screen's block and
render again; the rest stands. On client work the page is one file with nothing to install, so the
user can send it as it is.

## Completion criterion

The renderer exits 0 with the feature list passed; every feature in scope with a user interface has
its screens, each with an `intent` and the states its data needs; and the user has approved the
screens, or their approval is the step the hand-off waits on.
