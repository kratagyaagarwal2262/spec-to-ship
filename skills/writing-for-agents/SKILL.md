---
name: writing-for-agents
description: How to write documents agents consume: skills, CLAUDE.md, and any doc reached by a pointer. Use when creating or editing a skill, or modifying CLAUDE.md or the project config.
---

# Writing for agents

The reference for anything an agent reads: a skill, a `CLAUDE.md`, a config file reached by a
pointer. The packaging differs; the writing does not. The same levers make each one predictable,
because the agent takes the same *process* every run rather than producing the same output.

Read this before editing any skill in this kit. It is the standard the kit holds itself to.

## The two budgets

Everything you add spends one of two budgets, and they trade against each other:

- **Context load** is the cost of always-loaded material on the model's window — a skill's
  `description`, a line in `CLAUDE.md`. It is paid on **every turn**, whether or not the skill fires.
- **Cognitive load** is the cost on the human: knowing which documents exist and when to reach for
  each. The human is the index.

Cognitive load is not a cost to minimise blindly. It is the price of human agency: spend it where
human judgement matters, remove it where it does not.

## Invocation: the first decision

Every skill is one of two things, and the choice is a trade between those budgets.

- **Model-invoked** (omit `disable-model-invocation`). The agent can fire it on its own, and other
  skills can reach it by calling the Skill tool with its name. The `description` is a permanent
  context cost in exchange for discoverability. Write it model-facing, carrying the trigger phrases
  that should fire it.
- **User-invoked** (`disable-model-invocation: true`). Only a human typing the name can reach it, and
  **no other skill can call it**. Zero context load. The `description` becomes human-facing: a
  one-line summary with the trigger list stripped.

Pick model-invocation only when the agent must reach the skill on its own, or another skill must. A
heavy orchestrator that should never auto-fire on a vague request is user-invoked. In this kit that
is the seven `fk-` commands, `retro`, the tools (`handoff`, `unslop`, `spec-for-cheap-executor`) and
the router itself, and the list is held fixed: check 19 fails when a command is added outside it.
A new workflow becomes a step one of those commands calls, not a command of its own.

Two consequences worth internalising. Shared reference that two **user-invoked** skills both need can
live in neither — push it to a plain file both point at. And when a step's precondition is a
user-invoked skill, phrase it as an instruction for the human ("tell the user to run
`/fk-setup`"), never as a call.

## Composition: call the tool, do not link the file

Express a dependency as an explicit instruction to **call the Skill tool** with the named skill:

> Call the Skill tool with `project-stack`.

Not a `../other-skill/SKILL.md` link, and not a bare `/skill` mention left for the model to
interpret. Naming the tool is what actually fires it; a slash-name dropped into prose is a hint the
model may read as a label. Router prose that just names skills for a human to choose from is
different — that is not invoking anything, so plain names are correct there.

One skill per call. A step needing two is two calls; say so explicitly rather than "call it with X
and Y", which reads as one call taking both.

The exception is **reading**, not invoking. When the material you need sits in a reference file owned
by a **user-invoked** skill, no call can reach it, so linking to the file is correct. Where the owner
is model-invoked, call it instead of linking.

## Single source of truth

Keep each meaning in exactly one place, so changing the behaviour is a one-place edit. The same rule
restated in ten skills is not emphasis: it is ten places to forget, and it inflates that rule's
apparent importance past its real rank.

The **environment is a source of truth too**. A directory listing, a dependency manifest, a
script's `--help`. A document that restates one is a cache, and it earns its cost only when the lookup is
genuinely expensive. Cache what the agent cannot find by looking: the unwritten convention, the
reason behind a choice, the gotcha no config confesses. Leave the source tree to be read, not listed.

## What a skill writes, and when it reads

Before a skill writes anything, it names who reads it next, and that decides where it goes:

| Read next by | Goes |
|---|---|
| Only the person in this conversation | The reply. No file |
| A later session, another agent, a script, or someone who reads the repo | A file, and the one that reader already opens rather than a new one. The reply still says what it holds |
| Someone outside, once, such as a message to a client | The reply, ready to paste. A file keeps only what was decided |

A file nobody reads next is context some later session loads for nothing, so information that
passes the test is written in full and information that fails it is not written at all.

Reading follows the same rule from the other side. A skill opens a file at the step that uses it,
and only the part that step needs. Before the task is known, a session reads the vault's index and
memory through `project-memory`, and nothing else: a first step that reads every document "to
orient" fills the window before any work starts.

## Steps and completion criteria

Every step ends on a **completion criterion**: the condition telling the agent the work is done. Two
properties make it a lever.

**Clarity.** Can the agent tell done from not-done? A vague bound ("understanding reached") invites
ending the step early, with attention sliding toward *being done*. Sharpen the bound first; it is
cheap and local.

**Demand.** How much the criterion requires. "Every acceptance criterion mapped to a proof" forces
thorough work where "verify the feature" does not. Demand is what produces the digging the agent does
inside a step, and it is not step-bound: "every rule applied" binds a body of flat reference just as
well.

The strongest criteria are both checkable and exhaustive. `verify`'s "name the rung you
stopped on" is one; so is `code-review`'s "quote the criterion for every finding".

## Prompt the positive

Steering by prohibition drags the forbidden thing into context and makes it *more* available, not
less. Say what to do, so the banned behaviour is never spoken: "put every query in the repository
layer" rather than "never query the database from a view". Where a hard guardrail
genuinely cannot be phrased positively, pair it with the positive target so attention lands on the
action.

## Pruning

- **Hunt no-ops.** An instruction the model already follows by default pays context and says nothing.
  The test is model-relative: does it change behaviour versus the default? Two people disagreeing
  about a no-op are disagreeing about the default, and they settle it by running the document, not by
  arguing. When a sentence fails, delete the whole sentence rather than trimming words from it.
- **Check relevance.** Does each line still bear on what the document does? Lines lose relevance by
  going stale as the world changes, and shorter documents are easier to keep true.
- **Resist sediment.** Adding feels safe and removing feels risky, so stale layers settle until
  someone has to dig down through them to find what is still live. Deleting is part of the job.

## Before you commit a skill edit

- Does the `description` match the invocation choice — model-facing with triggers, or human-facing
  one-liner?
- Does every dependency read as a Skill tool call, and is every target model-invoked?
- Is any rule here already stated in `CLAUDE.md`, the skill that owns it, or the project config?
  Delete the copy and point instead.
- Does every step end on something checkable?
- Is anything here a project fact rather than a fact of every project on its stack? Project facts
  belong in `docs/agents/project.md`, or the kit stops being portable.
