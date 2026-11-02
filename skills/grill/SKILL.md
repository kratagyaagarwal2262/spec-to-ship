---
name: grill
description: Interview the user until a feature's requirements are settled. Use before scaffolding when acceptance criteria are thin, a design leaves states undefined, or a client feedback round arrives as prose instead of numbered criteria.
---

# Grill

Interview the user until you reach a shared understanding of what to build. Map the work as a
**design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already
settled, so you can ask it now without guessing at an answer you have not heard yet. Ask the whole
frontier in one round, then wait.

Format a round like this:

```
❓ **Q1 — <title>**: <question, including the options when it is a choice>

➡️ <your recommended answer>

---

❓ **Q2 — <title>**: <question>

➡️ <your recommended answer>
```

Every question carries your recommended answer, so the user can accept a round in one word. Each
round's answers reshape the tree: settled decisions push the frontier outward. Recompute it and ask
the next round. A question whose answer depends on another question still open in this round
belongs to a **later** round.

The session ends when the frontier is empty: every branch visited, nothing silently assumed. Do not
write code until the user confirms the understanding is shared.

## Facts are yours, decisions are theirs

Never ask the user something you could observe. Dispatch `codebase-explorer` for anything in the
codebase (does a constant already exist, what does the existing state layer emit, which route id is
free) and read the design yourself through whatever `docs/agents/project.md` names as the design
source. A running exploration is an unsettled prerequisite: only questions downstream of it wait, so
ask the rest of the frontier now.

Put the **decisions** to the user and wait. What the feature should do, which tradeoff to take, what
an edge case means for the user, is theirs.

## Where the tree branches on a client app

Walk these. They are where client work is underspecified in practice, and each one has produced a
rebuild on a real project.

- **State coverage.** Every criterion implies a status. What does the screen show on `loading`, on
  `failure`, and on success with an empty list? A criterion that names only the happy path is one
  third of a spec. Settle *whether* each state exists here; for what the user should see in one,
  call the Skill tool with `project-stack`, asking for the client component's `design`.
- **The fixture boundary.** Is there a real endpoint now, or is this screen-first? This decides
  whether the feature is scaffolded in real or fixture mode, so settle it in round one.
- **Validation and limits.** Which fields are required, what the bounds are, and what the user sees
  when a bound is hit. Check the project's field-limit constants before asking.
- **Navigation.** Where the screen is reached from, where each terminal action goes, and what the
  back gesture does mid-flow.
- **Persistence.** Does partial input survive backgrounding or a killed app? Multi-step flows
  usually should. Check what the project already stores before proposing new storage.
- **Money, time and units.** Currency, rounding, timezone, and the increment a duration or a time
  picker snaps to. These are the ones that come back as client feedback when guessed.
- **Permissions and offline.** What happens when location, notifications, or camera are denied, and
  what the screen does with no connection. Almost never in the brief; always noticed in review.
- **Auth state.** What a signed-out or guest user sees. If the flow can be started before sign-in,
  what happens to the work in progress at the wall.

## When the input is a client feedback round

Prose from a client ("this bit is confusing", "make the picker simpler") is not a
requirement. The first job is turning it into numbered criteria.

Ask what the user should **see or be able to do**, never what to change in the code. A client
describing a symptom is reporting an outcome they did not get; the change that fixes it is ours to
propose, and theirs to approve. Where their words imply a fix, name the outcome you think they mean
and put it back to them as a recommendation.

## Output

Close with the settled understanding as a numbered acceptance-criteria list, in the shape the
scaffolding skills consume. That list is the deliverable. Write it to `docs/specs/` when the
project's config names that directory.

Once the criteria are settled the states are known, which is the cheapest moment to decide what they
look like everywhere rather than once per screen. Where `docs/agents/design.md` does not exist yet,
call the Skill tool with `project-stack`, asking for the client component's `design`, to settle the
app's design language against this list.

Then hand the criteria back. Inside `/fk-plan` the next step is the spec; on its own, tell the user
that `/fk-build` takes them from here, and picks the full-feature or the fixture-mode path from
whether the endpoint exists.
