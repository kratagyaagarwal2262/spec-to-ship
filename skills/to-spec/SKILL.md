---
name: to-spec
description: Turn the current conversation into a written spec, with an explicit out-of-scope section. Use when /fk-plan has settled a requirement, or when the user asks to write a discussion up as a spec.
---

# To spec

Synthesise what has already been discussed into a spec. Write from the conversation you have; the
interviewing was `grill`'s job, and re-asking here spends the alignment twice. When the conversation
does not contain enough to write a spec, say which sections you cannot fill, then call the Skill tool
with `grill` to settle them rather than inventing the gaps.

Write to the directory `docs/agents/project.md` names for specs (`docs/specs/` by default), as
`docs/specs/<NN>-<slug>.md`. Where `docs/vault/features.md` exists, put the feature's ID in the
spec's header and the spec's path in that row's **Spec** cell. Where the project tracks work in
GitHub, also call the Skill tool with `project-tracker` to file the spec as a ticket linking the
file, its criteria named by number rather than copied, so it can be planned into a sprint.

## Before writing

Read the project's glossary (`GLOSSARY.md`) if it exists and use its terms exactly; a spec that
renames a domain concept teaches the codebase a second word for the same thing. Respect anything in
`docs/adr/` covering the area, and do not re-litigate a recorded decision inside a spec.

Then name the **seams under test** and confirm them with the user before writing. For an app
feature that is usually the state layer's actions and the screen's rendered UI; sometimes the
data-access layer. Prefer seams that already exist. The fewer, the better.

## The document

```markdown
# <NN>: <Feature name>

**Status:** ready to build · **Feature:** <ID from docs/vault/features.md, or none> · **Screens:** <screen IDs from docs/vault/screens/, or none> · **Source:** <the round, questionnaire, or conversation this came from>

## Problem

What the user cannot do today, from the user's side of the screen. No implementation.

## Solution

What they will be able to do, from the same side.

## Acceptance criteria

A numbered list. Every criterion is observable by a person using the app, and every one names its
states, including loading, empty and failure. This list is what `verify` maps proof onto and
what `code-review`'s spec axis reviews against, so an unobservable criterion is unverifiable.

## Implementation decisions

Modules touched, the interfaces that change, the data shape, endpoints and their request/response
association, navigation edges, and anything settled during grilling that the code must honour.

No file paths, no code snippets: they go stale within a round. One exception — a state machine,
enum, or JSON shape that encodes a decision more precisely than prose can. Inline that.

## Testing decisions

Which seams are tested and which are deliberately not. Prior art in the repo to follow. The
verification rung each criterion can actually reach, and which ones cannot be proven until a real
API or a staging environment exists.

## Assumptions

Every place we picked for the client because an answer never came back. Each one is a live risk;
this section is where a wrong guess gets caught in review instead of in a feedback round.

## Out of scope

What we are explicitly not building in this phase, in the client's own words where we have them.

On fixed-scope client work this is the most valuable section in the document. Write it even when
nobody asked, and make it specific: "no offline mode" beats "keeping it simple". A request that
arrives later and is listed here is a change request, not a bug.

## Sketch

<Filled by `plan-change` where the change touches more than a couple of files; deleted otherwise.>
```

## After writing

Show the user the **Acceptance criteria**, **Assumptions** and **Out of scope** sections and get
those three confirmed. The rest is ours to get right; those three are the contract.

With the contract confirmed the product is locked, which is the moment the app's visual language stops
being free to invent per screen. Where `docs/agents/design.md` does not exist yet, call the Skill
tool with `project-stack`, asking for the client component's `design`, to settle it before any
screen is built. Where the feature has screens nobody has drawn yet, call the Skill tool with
`screen-flows` for them, and put their IDs in the header.

Then return the spec path. Inside `/fk-plan` the next step is the sketch; on its own, tell the
user to run `/fk-build` with the spec, which picks the full-feature path when a model and endpoint
exist and the fixture-mode path when they do not.
