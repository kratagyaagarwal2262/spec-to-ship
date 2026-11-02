---
name: ask-kit
description: Ask where the project stands and which kit command or skill comes next. A router over every skill in the engineering kit.
disable-model-invocation: true
---

# Ask kit

Answer two things, in this order: where the project stands, and what the person wants next. Then
name **one** command or skill in `next-step`'s block, so they get what it does and the text to paste.
If the request is too vague to route, ask the one question that separates the candidates.

Do not do the work, and do not run the routed skill. Where the answer is a command, tell them to
type it; only a human can start one.

## 1. Where the project stands

Call the Skill tool with `next-step` for the project's stage and its default next command.

Say the stage in one line, with the file that decided it. Then:

- **The request fits the stage:** name its command.
- **The request is a later stage:** name the current stage's command first, and say what it leaves
  for the later one. A sprint cannot be planned from features that have no tickets.
- **The request jumps the order on purpose:** route it directly. Feedback from a client or tester
  is `/fk-feedback` at any stage, and shipping is `/fk-release`.
- **The request changes the plan itself:** a detour mid-sprint, a new data store, a rework of the
  design language or of how the app is built. That is `/fk-change`, which maps what the request
  alters and updates each plan and ticket in order.

## 2. The commands

Each calls the right skills in the right order, so the person only has to know where they are.

| Where you are | Command |
|---|---|
| New repo, inherited repo, or kit not configured for this repo yet | `/fk-setup` |
| An idea, a brief, a new phase, a client request, or criteria that are still thin | `/fk-plan` |
| A backlog to schedule, a sprint to check on, a build to gate, a sprint to close, or UAT | `/fk-sprint` |
| A spec, sketch or ticket (`#N`) ready to build, including a new feature from a design | `/fk-build` |
| Feedback has come back from a client or tester | `/fk-feedback` |
| A detour, or a change to how the app is built, that the plan did not foresee | `/fk-change` |
| About to ship: store submission, tester build, or a backend cutover | `/fk-release` |
| A round of work finished, and the next one should be shorter | `/retro` |

## Tools

| Situation | Command |
|---|---|
| Long branch, context about to reset | `/handoff` |
| Handing a task to another team, or a tool someone else runs, with no review before it lands | `/spec-for-cheap-executor` |
| Prose a client will read | `/unslop` |

## 3. Inside the commands

The planning skills look alike because they all deal in requirements, but each writes a different
thing. Tell them apart by what they leave behind, and route to one directly only when the person
names that thing ("revise the proposal", "add a feature", "re-point these tickets"). Otherwise name
the command, which runs them in this order.

| Order | Skill | Leaves behind | Reached through |
|---|---|---|---|
| 1 | `client-questionnaire` | Questions only the client can answer, to send | `/fk-plan` |
| 2 | `grill` | Settled answers and numbered criteria, in the conversation; no file of its own | `/fk-plan`, and any skill that finds a gap |
| 3 | `domain-glossary` | `GLOSSARY.md` and ADRs | `/fk-plan`, whenever a term is doing two jobs |
| 4 | `project-proposal` | `proposal.md` (why, for whom, modules, scope) and `features.md` (every feature, prioritised and phased) | `/fk-plan`, `/fk-feedback` |
| 5 | `screen-flows` | Every screen of the phase or the feature, drawn as one HTML page with its user flows, for review | `/fk-plan` |
| 6 | `project-backlog` | Tickets for the current phase's features, with criteria, points and screen IDs | `/fk-plan`, `/fk-feedback`, `/fk-sprint plan` |
| 7 | `to-spec` | A spec for one feature, in `docs/specs/`, whose criteria its tickets point to | `/fk-plan`, feature path |
| 8 | `plan-change` | A technical sketch: types, signatures, order of work, as a section of the spec | `/fk-plan`, feature path |

A project run for delivery takes rows 1 to 6, then `/fk-sprint plan`. One feature takes rows 2, 5,
7 and 8, then `/fk-build`.

The rest run inside their command too:

| Step | Skill | Reached through |
|---|---|---|
| Audit a codebase you inherited | `takeover-audit` | `/fk-setup` |
| File, move or report on tickets, features and sprints | `project-tracker` | every command |
| What the project remembers, and where a fact goes | `project-memory` | every command |
| Cut docs and agent context back to what is true and read | `prune-context` | `project-memory`'s budget check, `/fk-sprint close` |
| What to run next, with the prompt to paste | `next-step` | the end of every command |
| Which model each kind of agent work runs on, what it costs, or putting builds on a cheaper model | `configure-models` | installing, `/fk-sprint close` |
| One slice, test-first | `tdd` | `/fk-build` |
| Prove it works, and name the rung | `verify` | `/fk-build` |
| Review against conventions and spec | `code-review` | `/fk-build` |
| Opening a pull request | `pr` | `/fk-build` |
| What a release could break | `release-readiness` | `/fk-release` |
| CI pipeline | `setup-ci` | `/fk-setup`, `/fk-release` |
| A component's stack, commands, and the stack kit serving it | `project-stack` | every command that touches code |
| Security review of a change or a release | `security-audit` | `/fk-build`, `/fk-release` |

## Inside one component

Work inside one component's code, such as a screen, a data layer, a build that fails before it
compiles, or a package upgrade, belongs to the stack kit that serves that component. Call the Skill
tool with `project-stack` to name the component, its stack and its kit. That kit's skills fire on
their own when a request names the layer; where no kit is installed, `project-stack` answers from the
component's commands.

## Diagnose

| Situation | Skill |
|---|---|
| Broken, and reading the code has not helped | `diagnose-bug` |
| A merge or rebase is conflicting | `merge-conflicts` |
| Choosing between two shapes rather than behaviours | `engineering-principles` |
| Diagnose bugs in what a cheaper model shipped | `triage-executor-bugs` |
| Human-only setup: keys, signing, provider dashboards | `setup-wizard` |

## Editing the kit

| Situation | Skill |
|---|---|
| Editing any skill in this kit | `writing-for-agents` |

## Not covered by any skill

Say so rather than forcing a fit. A one-file change or a question answerable by reading one file
needs no skill.
