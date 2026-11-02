---
name: verify
description: Prove a change actually works before calling it done, by climbing a ladder of verification rungs in each component it touches and naming the rung reached. Use after implementing a feature or fixing a bug, when asked to verify or confirm something works, or when a build reaches its verification phase.
---

# Verify

"It compiles" and "the unit test passes" are not proof that a screen works. This skill is the ladder
from cheapest signal to real proof, plus the rule for which rung a given claim needs.

Climb only as far as the claim requires, but **name the rung you stopped on** in your reply. A claim
reported at a rung below what it needs is the failure this skill exists to prevent.

Read `docs/agents/project.md` first, for the Components table, the known-failing-test baseline and
the environment that is safe to verify against.

## The ladder

Each rung proves more than the one below and costs more to reach.

| Rung | Proves | The right rung for a claim about |
|---|---|---|
| 1. Static | It compiles and matches house formatting, with the analyzer clean | Nothing about behaviour; never the final rung for a behaviour claim |
| 2. Unit | The logic produces what the criteria say | Status transitions, error mapping, a computed value |
| 3. Component in isolation | A component or screen, rendered alone, shows the expected content and responds to input | Copy, empty states, conditional visibility, that a tap triggers the right action |
| 4. Visual baseline | The rendered pixels still match an approved baseline | "It doesn't match the design" |
| 5. Integration | A running build behaves end to end: navigation, real network, a request through every layer | Flows across screens or services, data that round-trips |
| 6. Real device or environment | The build works where it ships: native permissions, push, payments, the deployed service | Anything an emulator or local stack fakes |
| 7. A person | What only a human can judge: feel, sign-off on the design, a real card | Acceptance by whoever owns the criterion |

Rung 3 catches most interface regressions in under a second, so reach for it before anything
heavier. Not every component has every rung: a service has no visual baseline, and a component with
no harness has no integration rung yet.

## Get each component's rungs

1. **Find the components the change touches**: those whose Path in the Components table holds the
   changed files. Done when each changed file maps to one component.
2. **For each component, call the Skill tool with `project-stack`** for the `verify` slot, passing
   the component and the claim to prove. It returns the rungs that component has, the exact
   commands, and what each rung needs before it can run. Where no stack kit serves the component,
   `project-stack` answers from the row: its Check, then its Test, and the highest rung is a passing
   suite. Done when every component has its rungs and the highest one available is named.
3. **Run the Check command for each component before climbing.** A dirty analyzer makes every higher
   rung ambiguous, so fix that first. Done when Check finishes clean.

**Check the baseline before reporting a failure as yours.** `docs/agents/project.md` records the
tests already failing on a clean checkout. A count matching the baseline is expected; anything worse
is new breakage. Reporting a pre-existing failure as your own wastes a round, and reporting the
suite as green when the baseline is not zero is worse.

## Verify against a safe environment

Rungs 5 and 6 drive real flows, and a flow that writes data against a live backend creates real
records. Use the environment `docs/agents/project.md` names as safe. Where the project has none, the
rungs that need one are unavailable: say so, and report it as a finding for whoever owns the
backend. A test account is read from the environment at run time and never written into a file.

## Evidence

State the rung, the exact command, and its real output. Paste the counts, not a paraphrase. Report
only commands you ran in this session.

Every other claim in the report, such as a cause, a prediction, or why something now passes,
carries its basis in the same sentence: **measured** (you ran it), **inferred** (from code you
read), or **guess**. Where a check you could run would turn an inference into a measurement, run
it rather than asking the user to.

For a bug fix, evidence is the **same command twice**: red before the fix, green after. One green run
proves the code passes a test, not that it fixed anything.

Redact before pasting. A gitignored `.env`, generated secret files, and env accessors carry live
keys; write `<REDACTED>` in place of any value that appears in output.

## Reporting

Two lines per component, always:

```
app: Rung 3 (component in isolation). <test command> <the feature's tests> → 42 passed, 0 failed.
Not proven: summary step to payment (needs rung 5, unavailable: no safe environment).
```

An honest "not proven" is worth more than a confident claim at the wrong rung. When a criterion
cannot be proven at any available rung, say which rung it needs and what is missing; that sentence
is how the gap gets closed instead of forgotten.
