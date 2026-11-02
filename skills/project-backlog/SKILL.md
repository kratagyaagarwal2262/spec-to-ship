---
name: project-backlog
description: Break the current phase's features into tickets with acceptance criteria, story points, screen IDs and blocking edges, and file them in the tracker, writing a module note only where a module has decisions of its own. Use when /fk-plan has an agreed proposal or starts a new phase, when an approved change request needs tickets, or when the user asks for a backlog or a ticket breakdown.
---

# Project backlog

Turns features into work that can be picked up without asking a question. A ticket is finished
being written when `/fk-build` could take it as its only input, and a backlog is finished when every
feature of the current phase is covered by tickets like that. Later phases are cut when they start,
so their tickets are written against what the earlier phases taught.

## 1. Read

The proposal's current revision, the feature list in `docs/vault/features.md` and its current
phase, `GLOSSARY.md`, the screen files in `docs/vault/screens/` for the modules being cut, the
module notes already in `docs/vault/modules/`, the specs its rows link, and the open tickets (call
the Skill tool with `project-tracker` for them), so nothing is filed twice.

## 2. Slice each module

Take the current phase's features, module by module, Must first. Cut vertically: every ticket ends in
something a person can see or do, and names the feature it delivers in its `Feature:` line.

- The module's **first ticket is its tracer**: the thinnest path through every layer, from the
  screen to the data and back, so the module's shape is proven before it is widened. Everything
  else in the module is blocked by it.
- Then one ticket per feature, or per state of a feature, the tracer left out.
- A ticket that builds a screen names it by its screen ID in its Design section, so the build
  starts from the drawn screen rather than from a description of it.
- Work no screen shows (pipelines, environments, push setup, store accounts) is `type:chore`. Work
  only a person can do (fetching keys, signing, a store console, a client decision) is
  `ready-for-human`.
- A ticket whose backend does not exist yet is still filed, with a note that it builds on fixture
  data until the endpoint lands, plus a follow-up ticket to move it onto the real endpoint, blocked
  until then.

## 3. Write the criteria

Each ticket gets numbered acceptance criteria a person can observe, each naming its loading, empty
and failure behaviour where it has them, in the glossary's words. Where the feature's row links a
spec, the ticket names which of the spec's criteria it delivers instead, in the shape
`project-tracker` gives. Where a module's behaviour is not settled enough to write them, call the
Skill tool with `grill` for that module rather than inventing an answer.

## 4. Point

Points measure the whole job (the code, its tests, its review and its proof) relative to these
anchors:

| Points | Anchor |
|---|---|
| 1 | Copy, configuration or a constant; no new state |
| 2 | One state or one field added to an existing screen |
| 3 | One screen and its states over a data source that already exists |
| 5 | One slice across every layer: data, state, screen and tests |
| 8 | A slice with an unknown: a new integration, an unfamiliar API, platform code |

Above 8, split. An 8 names its unknown in the ticket; where the unknown is large, a 1- or 2-point
spike in front of it is usually cheaper than the surprise.

## 5. Record the edges

Write `Blocked by #N` wherever a ticket needs another's code or decision. A module whose tickets
form one long chain cannot run in parallel; where that happens, re-slice so the tracer unblocks
several tickets at once.

## 6. Confirm, then file

Show one table per module (title, feature, type, points, blocked by, intake state) with its point
total next to the size the proposal gave it. Where the module's features span phases, compare once
its last phase is cut. A module that comes out more than half again over its size is a finding: either the proposal undersized it and needs a revision, or the slicing is padded. Say which
you think it is.

On a yes, call the Skill tool with `project-tracker` to create the module label and file the
tickets. Where a module has a decision or an open question of its own, which the proposal, the
feature list and the screens do not already hold, write `docs/vault/modules/<slug>.md` for it and
link it from the vault index. A module with nothing of its own gets no note: the label, the feature
list and the screens already describe it.

```markdown
# <Module name>

**Proposal:** M<n>, revision <r> · **Tickets:** label `module:<slug>` · **Screens:** <the module's screens file>

## Purpose

## Decisions

## Open questions
```

## Completion criteria

Every feature of the current phase has tickets. Every ticket has numbered criteria or the spec
criteria it delivers, at most 8 points, a type, an intake state, its feature, and the screen IDs it
builds where it builds a screen. Every dependency is recorded, and each module's total is reported against its
proposed size.
