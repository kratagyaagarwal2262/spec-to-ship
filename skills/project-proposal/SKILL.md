---
name: project-proposal
description: Write or revise the project's proposal in docs/vault/proposal.md, covering objective, users, deliverables, modules, technical approach, assumptions, what the client provides, out of scope and timeline, under a revision history, and its feature list in docs/vault/features.md, each feature prioritised and phased. Use when /fk-plan starts a new product or a new phase, when a change request is approved, when a feature is added or reprioritised, or when the user asks for a proposal, a scope document or a feature list.
---

# Project proposal

The proposal is the project's bible. Every later artifact is measured against it: the modules and
tickets are cut from it, a sprint's goal serves it, and a feedback item is a bug or a change request
depending on what it says. That is why it carries revisions. Once agreed, it changes only by adding
one, so "was this in scope?" always has an answer with a date on it.

## 1. Gather

Read `docs/agents/project.md` for the stack and integrations, `GLOSSARY.md` for the project's words,
and `docs/vault/audit.md` where the codebase was inherited. Take the brief from whatever exists: the
conversation, a written brief, a filled questionnaire.

Where a section cannot be written because a decision is missing, settle it before writing around
it. The user can decide it → call the Skill tool with `grill`. Only the client can → call the Skill
tool with `client-questionnaire`, and stop until the answers are back.

The step is done when every section in the template has either an answer or a named owner for the
missing one.

## 2. Write the first revision

Fill [template.md](references/template.md) into `docs/vault/proposal.md`.

**Modules** carry the most weight, because the backlog is cut from them. A module is one capability
a user can name (signing in, onboarding, browsing, paying, settings, an admin panel) or one piece of
work no screen shows (the backend integration, notifications, the release itself). Each gets:

- **Problem**: what the user cannot do today.
- **Existing**: what is there now. "Nothing" on a new project; the audit's finding on an inherited
  one; on the user's own app, what the code does today, read from the code.
- **Proposed**: what will be built, as capabilities a user sees, never as code. One paragraph; the
  features themselves are rows in the feature list.
- **Size**: S (up to 13 points), M (14 to 34) or L (35 to 60). Anything larger is two modules.

**Out of scope** is never empty, and never vague. "No offline mode" commits to something; "keeping
it simple" does not. Write the things the user mentioned and decided against, and the things a
client of this kind of app usually assumes are included.

**Timeline** is points over capacity. Until a sprint has closed, capacity is a guess: write it as
one, and mark the timeline provisional. It firms up in the revision after the second sprint closes.

Sections marked *Client work* exist for an agency building for someone else. On the user's own
product, delete them and say so in the revision note.

## 3. List the features

Fill [features.md](references/features.md) into `docs/vault/features.md`, and link it from the
proposal's Modules section. This list is what sprints are picked from, so every module's Proposed
paragraph becomes rows in it.

A **feature** is one thing a user can do that a client could ask for, or drop, on its own: "a
returning user signs in with email and password", not "authentication". It usually takes one to
four tickets. Number features under their module, `M2.1`, `M2.2`, so each ID also says where it
belongs.

| Priority | Means |
|---|---|
| Must | The phase does not ship without it |
| Should | Expected in the phase; moves to a later one only with the client's agreement |
| Could | Built in the phase only where capacity is left after the Musts and Shoulds |

**Phase** is the release a feature ships in, `1` being the first. Something nobody will build in any
phase is not a row: it goes in the proposal's out of scope, so the list holds only what is agreed.

**Flow** is the user journey the feature belongs to: a path a user completes end to end, named as
they would say it, such as Onboarding (first open to a ready account), Browse, Checkout or
Settings. A feature on two journeys takes the one it is first needed in; work no screen shows takes
the flow it enables. Group the rows flow by flow, in the order a new user meets them, onboarding
first where the product has one, since every later flow starts from a signed-in user. Sprints take
the flows in this order, one per sprint, so the order is a delivery plan the client can read.

Set **Current phase** to the phase being planned now. **Spec** stays `—` until `to-spec` writes
one. **Added** names where the row came from: `Proposal r1`, or the change request that added it.

## 4. Agree it

Show the user the objective, the module list with sizes, out of scope, the assumptions and the
timeline, then the feature list grouped by phase and, within a phase, by flow in delivery order. On client work the
proposal and the feature list are the documents the client approves, so the user sends both and
comes back with the answer; record who agreed and when in the revision table, and set the status
to agreed.

## 5. Revise

An agreed proposal changes only through a new revision:

1. Add a row to the revision table: the number, the date, what changed, why (the change request,
   feedback round or audit finding that caused it), and who agreed it.
2. Edit the affected sections in place, and bump the revision at the top of both the proposal and
   the feature list.
3. A module moving in from out of scope, or growing, carries its points and the effect on the
   timeline in the same revision. A change with no cost attached reads as free.

A feature added or removed is a revision too, its row's **Added** naming it. Moving a feature's
priority or phase is not: edit the row, say what moved in the session's log entry, and on client
work get the client's agreement first, since it changes what they receive and when.

## Completion criteria

Every template section is filled or deliberately removed. Every module has a problem, an existing
state, a proposal, a size and at least one feature. Every feature has an ID, a flow, a priority and
a phase, and the rows run flow by flow in delivery order.
Out of scope lists specific items. Every assumption names who confirms it. The revision table's last
row matches the status line, and the feature list's header names the same revision.
