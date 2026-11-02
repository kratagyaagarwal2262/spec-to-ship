---
name: fk-release
description: Get a release ready to ship: find what it could break and prove the fact its safety rests on, confirm CI gates every component, and produce what each component ships, store pack included, through its stack's release steps.
disable-model-invocation: true
---

# Release

Everything between "it works on my machine" and "it is live". A release goes wrong in three
ways: a change breaks something nobody looked at, nothing stopped a broken build, or what ships is
wrong or rejected. Each step below closes one of them, and each calls the skill that owns it.

## 1. Orient

Read `docs/agents/project.md` for the Components table and the environments. Name what is being
released: the version, the commits since the last release, the target (a store, a tester group, a
backend cutover), and the components that ship in it.

Where `docs/vault/proposal.md` exists and this is the first store release, look for the UAT
sign-off in its revision table. A first store release without one is reported in the first line,
whatever else passes: the client has not yet accepted what is about to go live.

## 2. Find what it could break

Call the Skill tool with `release-readiness`. It traces the blast radius past the diff and proves,
by running code, the one fact the release's safety depends on.

Where it finds a failure, stop here. Report it, and leave the fix to `/fk-build`.

## 3. Confirm a gate exists

Look for a CI workflow that runs, on every push, each shipping component's Check and Test commands
from its row in the Components table. Where there is none, or it skips a component, say so and
offer to set one up; on a yes, call the Skill tool with `setup-ci`. A release with no gate is a
finding to report even when this one is clean.

## 4. Produce what ships

For each component that ships, call the Skill tool with `project-stack` for its `release` slot,
passing the component, the target, and what this release adds since the last one: a permission, an
SDK, a data type collected, a subscription, a new market. It returns what was produced, the store
pack among it, and what only a person can do.

Where it reports signing credentials or store accounts that do not exist yet, call the Skill tool
with `setup-wizard` for the steps a person has to take.

## Completion criteria

Report, in this order:

- The release-readiness result: what was proven, by which command, and anything not proven.
- Whether CI gates the build, and what it runs for each component.
- For each component: what was produced, the store pack written, refreshed, or confirmed unchanged
  with every `TODO (client input needed)` item and who owns it, and what only a person can do.

A release with any of these unknown is not ready, and the report says so in its first line.

Then call the Skill tool with `project-memory` to leave a log entry naming the version, the target
and the result, and call the Skill tool with `next-step`, handing off the first thing only a person
can do, or `/fk-feedback` once testers reply.
