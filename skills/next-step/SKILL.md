---
name: next-step
description: Say where the project stands and what to run next, naming the command or skill, what it does, the exact prompt to paste, and what it needs from the person first. Use at the end of every kit command, when a task finishes, or when the user asks what to do next, which command comes next or where the project stands.
---

# Next step

A finished task that leaves the person working out what comes next has handed them the hardest part
of the thread back. This skill ends every command with one block they can act on without reading
anything else: the next command, what it does, the text to paste, and whether it waits on them.

## 1. Where the project stands

Check these in order, stopping at the first that is not done: that is where the project stands, and
its command is the default next step. Stages 1, 2 and 4 are files to read; for stage 3, call the
Skill tool with `project-tracker` for the current phase's Must features.

| # | Stage | Done when | Next |
|---|---|---|---|
| 1 | Set up | `docs/agents/project.md` exists | `/fk-setup` |
| 2 | Scoped | `docs/vault/proposal.md` says agreed, and `docs/vault/features.md` gives every feature a priority and a phase | `/fk-plan` |
| 3 | Backlogged | every Must feature of the current phase has a ticket naming it | `/fk-plan` |
| 4 | Sprint planned | the vault index's **Now** line names a sprint note | `/fk-sprint plan` |
| 5 | In a sprint | (the stage the project stays in) | `/fk-build #N` for its tickets, or `kit loop run --until-done`; `/fk-sprint` for status, QA and close, picking its mode from the dates |

Where `docs/vault/changes/` holds a note whose status is not `done`, the project is mid-change, and
`/fk-change` resumes it before anything else.

A project not run as a delivery project (no `proposal.md`) skips stages 2 to 4: one change goes to
`/fk-plan` or `/fk-build`.

The step is done when you can name the stage and the file or tracker query that decided it.

## 2. Choose the next step

Where the caller finished a piece of work and named its hand-off (a spec ready to build, a sprint
ready for QA, a questionnaire waiting on the client), that is the next step: the stage table is the
check that it is not skipping one. Otherwise the stage's command is.

Fill in the real values the person would otherwise look up: the ticket number, the spec path, the
sprint mode, the feedback round. Where several are equally next, such as tickets with no edge
between them, take the first and list the rest as parallel.

The step is done when one command or skill is chosen, with every argument it needs.

## 3. Write the block

End the reply with this block, and nothing after it:

```
Next:      /fk-build #42
Does:      builds ticket #42 test-first, reviews and verifies it, and stops at a local commit
Paste:     /fk-build #42
Needs you: nothing
Then:      /fk-sprint qa once the sprint's tickets are merged
```

- **Next** is a command the person types, or a skill they ask for by name. Write a command in the
  harness's own syntax: `/name` in Claude Code.
- **Does** is one sentence: what it does and what it leaves behind.
- **Paste** is the exact text to send, arguments filled in. Where it needs more than the command,
  such as the client's answers, write the prompt in full with a placeholder for what only the person
  has.
- **Needs you** is `nothing`, or the one thing that has to happen first: the client's answers, the
  person's approval of the screens, merging pull request #N.
- **Then** is the step after, in one line. Add a **Parallel** line for the others from step 2.

Where the next work is building the sprint's `ready-for-agent` tickets, add an **Unattended** line:
`kit loop run --until-done` builds and reviews every one, then prints a report per ticket.

## Completion criterion

The reply ends with the block, its **Paste** line runs without the person looking anything up, and
**Needs you** names a concrete action or says `nothing`.
