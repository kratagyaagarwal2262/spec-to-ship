---
name: project-tracker
description: File, move and report on the project's tickets, modules and sprints in its issue tracker, following docs/agents/issue-tracker.md. Use when a command files a ticket, starts one, plans or closes a sprint, or reports status, or when the user asks what is in flight, what is blocked or what is next.
---

# Project tracker

The tracker is the one place a ticket's status lives. The vault links to tickets and never copies
their state; a sprint note lists what was committed, and the tracker says what happened to it. Every
other skill reaches the tracker through this one, so the conventions below hold everywhere.

## Read the conventions first

Read `docs/agents/issue-tracker.md`. It names the repo, the board (or `none`), the sprint length and
the velocity history. Where it is missing:

- `docs/agents/project.md` names the tracker as `none` → use [Without GitHub](#without-github).
- Otherwise → run **Set up**, below, before anything else.

Before the first write in a session, run `gh auth status`. Board operations need the `project`
scope; without it, skip them, say so, and carry on with labels and milestones, which hold everything
the board shows.

The exact commands for every operation are in [github.md](references/github.md).

## The model

| Concept | In GitHub |
|---|---|
| Ticket | an issue, its body in the shape below |
| Module | a `module:<slug>` label, plus a vault note at `docs/vault/modules/<slug>.md` where the module has decisions of its own |
| Feature | a `Feature: M2.3` line in the body, naming a row of `docs/vault/features.md` |
| Story points | a `points:N` label, N in 1, 2, 3, 5, 8 |
| Type | `type:feature`, `type:bug`, `type:change-request` or `type:chore` |
| Intake state | `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix` |
| Sprint | a milestone named `Sprint NN`, its due date the sprint's last day |
| In progress | assigned, and the board's Status set to `In Progress` |
| In review | an open pull request whose body says `Closes #N` |
| Done | closed by that pull request merging |
| Dependency | a `Blocked by #N` line in the body |
| Agent pull request | `agent-loop` while `kit loop` drives it; `agent-stuck` when it stopped and needs a person |

`ready-for-agent` means an agent can take the ticket with nothing but its body. `ready-for-human`
means it needs a person: a credential, a store console, a signing key, a device in hand, or a
decision only the client can make. `needs-info` means a question is open; the ticket says what and
who owns it.

Labels, milestones and the issue's open or closed state are the source of truth. The board is a
view of them; set its Status, never a field the labels do not already say.

## The ticket body

```markdown
## Outcome

What a user can do when this is done, from their side of the screen.

## Acceptance criteria

1. <observable behaviour, naming its loading, empty and failure states where it has them>

<or, where a spec already holds them: "Criteria 1 to 4 of [the spec](docs/specs/07-reset-password.md)">

## Design

<screen IDs from docs/vault/screens/, such as SIGNIN-1 and SIGNIN-2, design frame links, or "none">

## Notes

Blocked by #N.
Out of scope: <what this ticket deliberately leaves out>.
Feature: <the ID from docs/vault/features.md, or none for a chore or a bug>
Source: <proposal module, feedback round, audit finding, or the spec it came from>.
```

Criteria have one home. Where a spec exists for the work, the ticket names the spec's criterion
numbers and links it; otherwise the ticket states them. A ticket that copies a spec's criteria
leaves two lists to drift apart.

A ticket is ready when `/fk-build` could take it, and the spec it links, as its only input. A bug's body replaces Outcome
with **Expected** (quoting the criterion or proposal line it contradicts), **Actual**, **Steps** and
**Build**.

## Operations

**Set up.** Create every label in the model, idempotently. Offer a board: on a yes, create it, link
it to the repo, and tell the user to switch on its built-in workflows (auto-add from this repo, and
Done when an item closes), which only the web UI can do. Write `docs/agents/issue-tracker.md` from
the template `/fk-setup` provides.

**File tickets.** Creating issues notifies everyone watching the repo, so show the list (title,
type, module, points, blocked by, state) and get a yes before filing a batch. File in dependency
order, so each `Blocked by` names a real number, and add each issue to the board where there is one.
Return the numbers.

**Start a ticket.** Assign it to the current user, set board Status to `In Progress`, and name the
branch `<N>-<slug>`. Branch locally; the pull request links it.

**Find the frontier.** Open tickets labelled `ready-for-agent` or `ready-for-human`, unassigned,
with every `Blocked by` closed. This is what can start now and run in parallel, which is what
`kit loop` and parallel builds take from. It is not a sprint's scope: `/fk-sprint plan` takes a
whole flow, including tickets blocked by others in the same sprint.

**Plan a sprint.** Create the `Sprint NN` milestone with its due date and the goal as its
description, then set it on each chosen ticket.

**Report.** For a sprint, a module or a feature: closed, in review, in progress, not started and blocked, each
with points, and the sum of closed points against committed. Write it for someone who has not seen
the code: ticket titles and outcomes, not branch names. A feature is done when every ticket naming it
is closed.

**Close a sprint.** Sum the closed points; that is the sprint's velocity. Move each open ticket to the
next milestone or clear its milestone, as the user chose. Close the milestone. Append the sprint and
its velocity to the table in `issue-tracker.md`.

**Close a ticket by hand** only as `wontfix` or a duplicate, with a comment saying why. Finished work
closes through its pull request, so the record links the code.

## Without GitHub

Where the tracker is `none`, `docs/vault/backlog.md` is the tracker: one table, one row per ticket.

| # | Title | Type | Module | Feature | Points | State | Sprint | Blocked by |
|---|---|---|---|---|---|---|---|---|

Ticket bodies go in `docs/specs/`, one file per ticket, linked from the row. Each operation above
becomes an edit to this table, and State takes `todo`, `in-progress`, `in-review`, `done` or one of
the intake states. A single table has one writer at a time, so it suits one person and one agent;
when parallel agents start, tell the user to move to GitHub with `/fk-setup`.

## Completion criteria

Every ticket filed has a type, a points label (bugs and chores included), an intake state and, where
it has one, a module; every dependency names a real issue number. Every report states closed points
against committed. Nothing was filed, moved or closed without the user seeing the list first.
