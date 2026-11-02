---
name: takeover-audit
description: Audit an inherited codebase before committing to work on it, covering whether it builds, what its tests prove, how far it has drifted, where the risk sits, and what must be stabilised first. Use when /fk-setup finds a project this team did not write, or when the user asks to assess a codebase they are taking over.
---

# Takeover audit

An inherited app arrives with claims ("it works", "it is nearly done", "it only needs one more
feature") and nobody left to ask. The audit replaces the claims with evidence before anyone gives an
estimate. Everything here is observation: record what is broken, and leave the repair to tickets.

Read `docs/agents/project.md` first. `/fk-setup` has already recorded the components, the platforms
and the test baseline; reuse them rather than re-deriving them. Call the Skill tool with
`project-stack` for each component's commands and the stack kit that serves it.

## 1. Does it build

For each component, and each platform it ships to that this machine can build (iOS needs macOS),
run its Build command, as a debug build where the stack has one.

Where a build fails, call the Skill tool with `project-stack`, asking the component's `conventions`
slot for the aspect `debugging tools`, which carries the stack kit's knowledge of build and toolchain
failures. Find the cause with it, and record the cause without fixing it. Then call the Skill tool
with `verify` for the highest rung each component can reach today, and whether the app launches
there.

The step is done when every component and platform has a recorded result: builds, or fails with a
named cause.

## 2. What is there

Call the Skill tool with `explain` for a map of each component: its features, how state and data
flow, how navigation works, what the startup sequence does. Write it as the list of modules the app
actually has, each with what works and what is stubbed, half-built or dead. This becomes the
proposal's **Existing** column.

## 3. What the tests prove

Take the counts from the baseline. Then check what they cover: do the flows that matter most
(sign-in, payment, anything that writes data) have a test at any rung? A suite of passing tests over
the wrong code proves little, so name the critical flows with no test at all.

## 4. Drift

Call the Skill tool with `project-stack`, asking each component's `conventions` slot for the aspect
`dependencies`: the command that lists outdated packages, and where the platform targets are set.
Run it.

Count the packages a major version behind, and any marked discontinued. Compare the language and
framework versions with their current stable releases and, for an app that ships through a store,
the target and minimum OS versions with what each store currently requires for a new release. A
store requirement the app misses blocks the next update, whatever else is true.

## 5. Risk

Call the Skill tool with `security-audit` with the scope `all`. Then check what it does not:

- Who holds the developer accounts, the signing keys and the backend: if nobody on this side does,
  that is the first blocker.
- The version in each shipped component's manifest against the version live in each store.

## 6. Write it up

Write `docs/vault/audit.md` and link it from the vault index:

```markdown
# Audit, YYYY-MM-DD

**Verdict:** <stabilise first | workable as is | rewrite candidate>, because <the deciding evidence>.

## Builds

| Component | Platform | Result | Cause |
|---|---|---|---|

## Modules as found

| Module | Works | Stubbed or broken |
|---|---|---|

## Findings

| # | Severity | Area | Finding | Evidence |
|---|---|---|---|---|
```

Severity is **blocker** (cannot build, sign or ship), **high** (security, store rejection, data
loss), **medium** or **low**. Evidence is a command and its output, or a `file:line`.

A rewrite is a recommendation the user weighs, never the default. Where you make it, give the cost
of both paths in the same terms.

Then show the blockers and highs as tickets, `type:chore` or `type:bug` with points, and on a yes
call the Skill tool with `project-tracker` to file them. Stabilisation goes first in the first
sprint.

## Completion criteria

Every component and platform has a build result. Every finding has evidence and a severity. The
verdict names the evidence it rests on. Every blocker and high finding is filed as a ticket or
explicitly waived by the user.
