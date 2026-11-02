---
name: project-memory
description: Read and keep the project's memory vault in docs/vault/, deciding what to read at the start of a session, which file each kind of fact belongs in, and how to write without overwriting another agent. Use when starting work in a repo that has docs/vault/, when a decision, lesson or outcome should outlive the session, or when the user asks what the project knows.
---

# Project memory

A session starts knowing nothing about the project and ends knowing a lot. The vault is where the
part worth keeping goes, so the next session, or another agent working beside this one, starts where
this one stopped. It is plain linked Markdown at `docs/vault/`, versioned with the code, and any
Markdown editor that treats a folder as a vault (Obsidian, for one) opens it as one.

The vault holds what the code and the tracker cannot: why something was decided, what was agreed,
what went wrong once and will again, what the client actually said. It is never a second copy of the
code or of ticket status, because a copy is a second place to be wrong.

## At the start of a session

Read `docs/vault/index.md`, then `docs/vault/memory.md`. Both are short by design, and they are all
a session reads before it knows its task. Every other note is opened by the step that uses it, and
only the part that step needs: the sprint note when planning or reporting on the sprint, a module
note when working inside that module, the latest feedback round for a fix the client asked for.

Then run `python3 scripts/budget.py <project root>` from this skill's folder. It prints a line for
each vault file or folder over its budget, and nothing when all fit. Where it prints anything, call
the Skill tool with `prune-context`, passing those lines, before the task begins.

The step is done when you can state the current sprint goal, or that there is none, every memory
line that bears on the task in front of you, and that the budget check printed nothing or the
pruning ran.

## Where each fact goes

| Fact | File | Written by |
|---|---|---|
| The map of the vault | `index.md` | whoever creates or deletes a note |
| A durable fact most sessions need: a working agreement, a trap, a pointer | `memory.md` | any session, one line |
| What the project is, its scope, and every revision to it | `proposal.md` | `project-proposal` |
| Every agreed feature, its priority and its phase, and the current phase | `features.md` | `project-proposal`; its **Spec** cell by `to-spec` |
| One module's decisions and open questions, where it has any of its own | `modules/<slug>.md` | `project-backlog`, then any session working in it |
| Every screen of a module, its states and where each action leads | `screens/<NN>-<module>.screens`, drawn to `screens/index.html` | `screen-flows` |
| One sprint: goal, dates, committed tickets, QA, review | `sprints/sprint-NN.md` | `/fk-sprint` |
| One round of client or tester feedback, verbatim, and its triage | `feedback/round-NN.md` | `/fk-feedback` |
| One change to the plan: what it alters, ticket verdicts, its steps | `changes/NN-<slug>.md` | `/fk-change` |
| An inherited codebase's audit | `audit.md` | `takeover-audit` |
| What one session did, decided and left | `log/YYYY-MM-DD-<slug>.md` | the session itself |

These live outside the vault. The index links to them and never copies them:

| Fact | Lives in |
|---|---|
| Ticket status, points, sprint membership | the tracker, through `project-tracker` |
| Stack, flavors, commands, verification surfaces | `docs/agents/project.md` |
| Domain terms | `GLOSSARY.md`, through `domain-glossary` |
| Hard-to-reverse decisions | `docs/adr/`, through `domain-glossary` |
| Requirements for one feature | the specs folder `project.md` names |
| Anything the code, the config or git history already says | there |

A fact that fits no row goes in the narrowest existing note it bears on. Where none fits, it is
probably a log entry.

## Writing

**A log entry** closes every session that changed the code, the plan or a decision. One new file
per entry, never an edit to an existing one, so sessions running in parallel never touch the same
file:

```markdown
---
date: YYYY-MM-DD
ticket: "#N"
---

# <what happened, in one line>

**Done:** what changed, linking the commit or pull request rather than restating the diff.
**Decided:** each decision and its reason.
**Tried and dropped:** what did not work, and why, so nobody tries it again.
**Left:** what is unfinished, and the first step to take on it.
```

Drop a field with nothing in it. Use `ticket: none` where the work had no ticket.

**`memory.md`** takes one line per fact, under the heading it fits, phrased so it reads true out of
context a month from now. When a new line would take it past its budget, call the Skill tool with
`prune-context` first.

**`index.md`** gains a line when you create a note and loses one when you delete one. A note the
index does not link is a note no session will find.

Credentials, keys, tokens and anyone's personal data stay out of the vault entirely: it is committed
to git, and git keeps everything.

## Two agents, one vault

- Change a shared file (`index.md`, `memory.md`, a module or sprint note) with the harness's
  file-edit tool, as a small in-place edit of a file you read in this session. The edit tool refuses
  a write to a file that changed after you read it, and that refusal is what stops one agent
  overwriting another's update. On a refusal, read the file again and re-apply your change to what
  is there now.
- Keep whole-file rewrites and shell redirection away from shared files: both skip that check.
- Agents on separate branches meet at merge. The project's `.gitattributes` gives `memory.md` and
  `index.md` git's union merge, so both sides' lines survive, and the next pruning removes any
  duplicate.

## Completion criteria

At the end of a session: every note created in it is linked from `index.md`; a session that changed
code, plan or a decision has left exactly one log entry; the budget check prints nothing.
