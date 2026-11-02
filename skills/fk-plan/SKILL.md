---
name: fk-plan
description: Turn an idea, a brief or a client's request into an agreed proposal, a prioritised feature list, drawn screens and a pointed backlog, or a single requirement into a spec and a sketch, settling it before any code exists.
disable-model-invocation: true
---

# Plan

The expensive failure is the right code for the wrong requirement. This command settles the
requirement while it is still a conversation, writes it down including what is *not* being built,
and sketches the shape of the change, so `/fk-build` starts from something it cannot misread.

Each step calls the skill that owns it. This one owns the order, and the rule that no step is
skipped because the answer "seems obvious".

Keep the whole plan in one unbroken session where you can: the interview, the spec and the sketch
build on the same thinking, and a compaction between them loses the reasons behind the decisions.

## 1. Orient

Where `docs/agents/project.md` is missing, stop and tell the user to run `/fk-setup` first: every
later step reads it. Call the Skill tool with `project-memory` to load the vault. Read the rest when
a step needs it, not now: the feature list's row for the work below, the glossary when `grill`
settles a term, and only the file names in the specs folder `project.md` names, to see whether this
was already specified.

Then pick the path, and say which in one line:

| The work | Path |
|---|---|
| A new product, or a new phase of one, that no agreed proposal in `docs/vault/proposal.md` covers | **Product**: step 2, then P1 to P4 below |
| An approved change request, or the next phase of the feature list starting with no tickets yet | Call the Skill tool with `screen-flows` for its features that have no screens, then call the Skill tool with `project-backlog`, then hand off as in P4 |
| One feature, ticket or change | **Feature**: steps 2 to 6 |

On the feature path, where `docs/vault/features.md` exists, find the feature's row first. No row
means new scope. On client work that is a change request: stop, and tell the user to run
`/fk-feedback` with it so it is estimated and agreed. On the user's own product, call the Skill tool
with `project-proposal` to add the row.

The step is done when you can say, in a sentence, what is being planned, what already exists around
it, and which path it takes.

## 2. Questions only someone else can answer

Where the plan depends on a decision nobody in this conversation can make (a client's business
rule, a third party's API, a policy), call the Skill tool with `client-questionnaire`. Then stop:
tell the user to send it and run `/fk-plan` again with the answers. Planning past an unanswered
client question is how a feature gets built twice.

Skip this step when every open question is one the user can answer.

## 3. Settle the requirement

Call the Skill tool with `grill`. It interviews until every acceptance criterion is numbered and
every state the happy path skips (loading, empty, failure, first run, offline) has an answer. Terms
that turn out to mean different things to different people go to `GLOSSARY.md` as they settle.

Where the change has a screen and the app has no `docs/agents/design.md` yet, call the Skill tool
with `project-stack`, asking for the client component's `design` slot, before moving on, so the
screen is planned against a design language rather than invented during the build. Then call the
Skill tool with `screen-flows` for the screens the change adds or alters, and get the user's
approval of the drawn screens before the spec is written.

## 4. Write it down

Call the Skill tool with `to-spec`. The spec carries the numbered criteria from step 3 and an
explicit out-of-scope section.

## 5. Sketch the change

Where the work touches more than a couple of files, call the Skill tool with `plan-change`
for the types, signatures, boundaries and the order the slices land in. It writes the sketch into
the spec. A single-file change needs no sketch.

## 6. Hand off

Call the Skill tool with `next-step`, handing off `/fk-build` with the spec path.

## Product path

**P1. Proposal and features.** Call the Skill tool with `project-proposal`. It writes the proposal
and the feature list, every feature with a priority and a phase. On an inherited codebase it builds
on `docs/vault/audit.md`; where that is missing, tell the user to run `/fk-setup`, which runs the
audit.

**P2. Design.** Where the app has no `docs/agents/design.md`, call the Skill tool with
`project-stack`, asking for the client component's `design` slot, to settle the design language
against the proposal's modules. Then, where the project has no designer's frames for the current
phase, call the Skill tool with `screen-flows` for the current phase's features: every screen they
need, its states, and the user flow between them, drawn to one page the user and the client can
open. Where frames exist, record their links on the proposal's modules instead.

**P3. Agreement.** The proposal, the feature list and the screens are agreed together before
anything is cut from them, so the client approves what they will see, not only a list. On client
work that means the client: stop here, and call the Skill tool with `next-step`, whose hand-off is
`/fk-plan` again once it is agreed.

**P4. Backlog.** Call the Skill tool with `project-backlog`. It cuts tickets for the current phase's
features only, each naming the screens it builds. Then call the Skill tool with `next-step`,
handing off `/fk-sprint plan`.

## Next

End every run, including one that stops early, by calling the Skill tool with `next-step`, handing
off what the path's last step hands off, or, where a step stopped, what the user has to bring
back.

## Completion criteria

**Product path:** the proposal, the feature list and the screens are agreed and the revision
recorded, the design language exists, every screen-bearing feature of the current phase has its
screens drawn or a designer's frame linked, and every feature of the current phase has tickets with
criteria and points in the tracker.

**Feature path:** a spec file exists with numbered acceptance criteria, each naming its loading, empty and failure
behaviour where it has one, and an out-of-scope section. Where a feature list exists, the spec names
its feature and the feature's row links the spec. Where the change has screens, the spec names
their IDs and the user approved them drawn. Either the spec has a sketch or you have said why the
change needs none. Every question that could not be settled is listed, with who owns it.
