---
name: fk-build
description: Build a ticket, spec or sketch to a reviewed, verified commit, choosing the path from what it is given: a change to existing code, a new feature from a design and an endpoint, or a screen before its API exists.
disable-model-invocation: true
---

# Build

Take a settled piece of work and drive it to a commit that has been reviewed and proven, rather than
to code that compiles.

Everything here is a call to a skill that owns its part. This skill owns the **route**, the
**order** and the **gates**, which is what goes missing when work is done ad hoc: the review happens
after the claim of doneness, or the suite is run once at the end and its failures attributed to
something else.

## 0. Route

Read what you were given, then take the first row that fits.

| The work | Path |
|---|---|
| A ticket number, such as `#12` | Call the Skill tool with `project-tracker` to read the ticket and start it. Its body is the spec; take the next row that fits it. |
| No spec, sketch or numbered acceptance criteria, or criteria naming only the happy path | Stop. Tell the user to run `/fk-plan` first, or call the Skill tool with `grill` when only a criterion or two is missing. |
| A **new feature**, with or without its API yet; a feature built **before its API**, now that the API exists; or a change to **code that already exists** | Steps 1 to 6 below. Name which of the three it is: the build slot in step 2 takes its shape from that. |

Where the user wants a cheaper model to do the build, take the path above anyway: the stack kit's
build slot hands mechanical slices to its build-role agents, with the brief from step 2. Call the
Skill tool with `configure-models` to choose that role's model. A sprint of tickets built unattended
is `kit loop run`. Suggest `/spec-for-cheap-executor` only for work leaving the session with nobody
reviewing it before it lands, such as another team: it spends hours of the strongest model to stand
in for that review.

The step is done when you have named the path and why, in one line, before writing any code.

## 1. Orient

Call the Skill tool with `project-stack` for the components the work touches, and for each one its
`conventions` and its Check and Test commands. Read `docs/agents/project.md` for the
known-failing-test baseline. Record the baseline **now**, before writing anything, so a pre-existing
failure is never reported later as your own breakage.

Where the work has no sketch and touches more than a couple of files, call the Skill tool with
`plan-change` before writing code.

The step is done when every component the work touches is named with its Check command, its Test
command and its baseline.

## 2. Build, test-first

One vertical slice at a time, each ending green. For each slice in the sequence, write its brief,
then build it:

- Call the Skill tool with `project-stack`, asking for the `build` slot of the components the slice
  touches and passing the slice's acceptance criteria and its brief.
- Where `project-stack` answers that no stack kit builds that component, call the Skill tool with
  `tdd` for the slice instead, against the component's Test command.

The brief carries four things, because they are what a builder gets wrong when it has to infer them,
and a cheaper model most of all. The build slot passes it on unchanged to any agent it delegates to:

| The brief carries | Because the builder otherwise |
|---|---|
| The files to create and modify, and the near-duplicates to leave alone | Tidies code it was not asked to touch |
| Each thing the slice makes obsolete, and an `rg` command that must print nothing once it is gone | Adds the new code and leaves the old in place |
| The test that fails now and passes after the slice, with its current failure message | Reports a no-op as done |
| Which outcomes are normal and which mean failure, such as an empty list or zero rows written | Treats a silent early return as success |

Between slices, run the component's Check and the tests for the files you touched. Not the full
suite: it is slow enough that running it per slice is how people stop running it.

Read the slice's diff, and run its `rg` proof and its tests yourself, before the next slice starts.
Your check catches what the brief did not, which is why the brief can stay this short.

Where a slice turns out to need a shape the sketch did not have, say so and call the Skill tool with
`plan-change` again rather than working around it.

## 3. Gate

Now, for every component the work touched, its Check clean and its full Test suite, with the
commands from step 1.

Compare against the baseline from step 1. Anything worse is yours. A suite reported as green when
the baseline was never zero is the failure this step exists to prevent.

## 4. Review

Call the Skill tool with `code-review`. It reviews on two axes, and both matter here:
whether the code follows the project's conventions, and whether it does what was asked. Code can
pass every convention and implement the wrong requirement.

Act on the findings, then re-run step 3. A review whose findings are noted and not fixed is a review
that cost time and bought nothing.

## 5. Prove

Call the Skill tool with `verify`. Name the rung reached for each acceptance criterion, and
name what is not proven and what rung it would need.

Where the work touched security-sensitive surfaces, meaning secrets, authentication, stored data,
the network, user input or web content loaded into the app, call the Skill tool with
`security-audit` over the change.

## 6. Commit

Only when steps 3 to 5 have all passed. Stage the change, write a message saying what changed and
why, and show it to the user before committing. Never push.

Where the branch is the default branch, branch first.

Where the work goes up as a pull request, call the Skill tool with `pr` for its body. The evidence
from step 5 is what fills it, and a ticket's number goes in as `Closes #N`, so merging closes it.

Then call the Skill tool with `project-memory` to leave the session's log entry.

Under `kit loop`, the prompt names a file for the pull request body. Write the body there and stop
after the commit; the loop pushes and opens the pull request, so this step's "never push" still
holds for you.

## Next

End every run, including one that stops early, by calling the Skill tool with `next-step`, handing
off the sprint's next ready ticket, or `/fk-sprint qa` when this was its last.

## Completion criteria

Every acceptance criterion has code, a test naming it, and a verification rung reported. Every
touched component's Check is clean, its suite matches or beats the baseline, and the review findings
are resolved rather than acknowledged.

Report what is **not** done in the same breath as what is: criteria dropped, rungs not reached,
findings deliberately left. A completion report listing only successes is not a report, and the next
person pays for the difference.
