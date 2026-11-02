---
name: fk-change
description: Take a request the planned process does not cover, such as a detour mid-sprint, a new data store or a rework of the design language, map which plans and tickets it changes, and update each through its owner in order so the backlog and the sprint still describe the app being built.
disable-model-invocation: true
---

# Change

The other commands assume the plan holds. This one is for when it does not: a detour to rework the
design language, local data moving into a database, a content library restructured. Such a request
changes the documents that work already in flight was cut from. Handled ad hoc, the code moves and
the plan does not, and the next sprint is planned from tickets describing an app that no longer
exists.

This command owns the impact map and the order. Every document is changed by the skill that owns
it.

Some requests already have a command. Client or tester feedback is `/fk-feedback`, which classifies
it against what was agreed. New work inside the plan (one more feature, one more ticket) is
`/fk-plan`, and a single bug or ticket is `/fk-build`. Where the request is one of those, say which
and stop.

## 0. Resume or start

Read `docs/agents/project.md`, then call the Skill tool with `project-memory` to load the vault.
Where `docs/vault/changes/` holds a note whose status is not `done` and the user named no new
request, resume it at its first unchecked step. On resuming, call the Skill tool with
`project-tracker` for the tickets the note filed; where every one is closed, set the note to `done`
and clear the vault index's **Now** line for it.

The step is done when you have said, in one line, whether this resumes change NN or starts a new
one.

## 1. State the change

Restate the request as what will be true when it is done, in a sentence or two the user confirms:
"saved items move from key-value storage into a local database, read through the existing
repositories", not "add a database". Where you cannot say what will be true, the request is not
settled yet: call the Skill tool with `grill` until you can.

## 2. Map the impact

For each row, decide whether the change alters it, and quote the line or file it alters.

| What | Where it lives | Owner |
|---|---|---|
| Architecture: a data store, a stack choice, a boundary between layers | `docs/adr/`, the Architecture table in `docs/agents/project.md` | `plan-change` |
| Design language | `docs/agents/design.md` | `project-stack`, the client component's `design` slot |
| Words | `GLOSSARY.md` | `domain-glossary` |
| Scope: modules, features, out of scope, technical approach, timeline | `docs/vault/proposal.md`, `docs/vault/features.md` | `project-proposal` |
| Open tickets | the tracker | `project-backlog` and `project-tracker` |
| The current sprint | `docs/vault/sprints/`, its milestone | step 5 of this command |
| Code already built | each component's Path in the Components table | a ticket, built with `/fk-build` |

Then call the Skill tool with `project-tracker` for the open tickets, and give each one the change
touches a verdict:

| Verdict | When |
|---|---|
| Keep | It does not touch what changes |
| Rewrite | Its criteria or design describe the old shape |
| Block | It cannot start until the change's first ticket lands |
| Supersede | The change makes it pointless |

Code already built that the change contradicts gets a rework ticket of its own, so it is replaced on
purpose rather than left running beside the new shape.

Size the change from the map:

| Size | When |
|---|---|
| Detour | Scope and architecture hold; only the design language, words, tickets or code change |
| Re-plan | Scope or architecture changes |

Show the user the map, the verdicts and the size, and get a yes before changing anything. The step
is done when every row has a yes or no with its quote, and every touched open ticket has a verdict.

## 3. Write the change note

Fill [change-note.md](references/change-note.md) into `docs/vault/changes/NN-<slug>.md`, `NN` the
next free number. Its steps are the rows of step 4 the map marked yes, in step 4's order, then the
sprint. Link it from the vault index under **Changes**, adding that heading where the index has
none, and point the index's **Now** line at it
while it is open, so every session that starts finds it.

## 4. Change the documents, in order

Decide, then record, then re-cut. Each document is written from the ones before it, so a ticket is
never cut against a decision not yet made. Take only the rows the map marked yes, and tick each step
in the note as it finishes.

1. **Architecture.** Call the Skill tool with `plan-change` for the sketch and the ADR. Where
   the decision changes a row of the Architecture table, edit that row and name the ADR beside it.
   Where it changes a row `/fk-setup` chooses rules from, such as the logic seam or serialization,
   add a step to the note telling the user to re-run `/fk-setup` once this command ends.
2. **Design language.** Call the Skill tool with `project-stack`, asking for the client
   component's `design` slot.
3. **Words.** Call the Skill tool with `domain-glossary`.
4. **Scope.** Call the Skill tool with `project-proposal` for the revision, or the feature rows. On
   client work, a revision that changes cost or timeline waits for the client: set the note's
   status to `waiting on client`, stop, and tell the user to run `/fk-change` again once it is
   agreed.
5. **Tickets.** Call the Skill tool with `project-backlog` to cut the change's own tickets: the first
   is its tracer, and every ticket marked Block names that tracer in `Blocked by`. Then call the
   Skill tool with `project-tracker` to apply the verdicts: rewrite the criteria of each Rewrite
   ticket, and close each Supersede ticket as `wontfix`, its comment linking the change note.

The step is done when every row the map marked yes has been changed by its owner, or the note says
what that step is waiting on.

## 5. Settle the sprint

Skip this where no sprint is open: the next `/fk-sprint plan` picks the change's tickets up by
priority.

- **Detour.** Make room rather than overfill. Propose tickets to move out, not started and lowest
  priority first, totalling the points the change adds. On a yes, call the Skill tool with
  `project-tracker` to move both sets.
- **Re-plan.** The sprint's goal no longer holds as committed. Recommend one of two: finish what is
  in progress, then close early with `/fk-sprint close` and re-plan with `/fk-sprint plan`; or keep
  the sprint and plan the change into the next. Recommend closing early when an in-progress ticket
  was marked Rewrite, Block or Supersede.

The sprint note's Committed list stays as it was promised. Record the swap or the choice in the
change note, which the sprint's review links.

## 6. Hand off

Tell the user what to type next, in order: `/fk-setup` where step 4 added it, the sprint command step
5 chose, then `/fk-build #N` for the change's tracer. Call the Skill tool with `project-memory` to
leave the session's log entry.

## Next

End every run, including one that stops early, by calling the Skill tool with `next-step`, handing
off the first command step 6 names.

## Completion criteria

The change note states what will be true, the impact map with a quote per row, a verdict per touched
ticket, and every step either ticked or naming what it waits on. Every document the map marked yes
was changed by its owner. Every verdict is applied in the tracker, and the sprint has either a
recorded swap or the user's re-plan choice. Nothing was changed before the user confirmed the map.
