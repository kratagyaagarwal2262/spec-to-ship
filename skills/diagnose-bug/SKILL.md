---
name: diagnose-bug
description: Disciplined diagnosis loop for hard bugs, jank, and regressions. Use when the user says diagnose or debug this, or reports something broken, throwing, failing, or slow.
---

# Diagnose bug

A discipline for bugs that resist a first look. Skip a phase only with a stated reason.

**Redact first.** This skill has you paste commands and output. A gitignored `.env`, generated
secret files, tokens in a request log, and a real customer's details in a payload all show up in
app logs. Write `<REDACTED>` in place of any of it. If the redacted output is not enough to
diagnose, say so and ask.

## Phase 1: Build a loop that goes red

**This is the skill.** Everything after it is mechanical. With one command that reliably fails on
*this* bug, you will find the cause; without one, no amount of reading code will save you.

Spend disproportionate effort here. Be aggressive, be creative, refuse to give up.

### Ways to build one, cheapest first

1. **A state-layer test** driving the actions that produce the wrong state. Fastest and most
   deterministic; reach here first for anything about status, data, or a computed value.
2. **A UI test** rendering the screen and asserting the symptom the user described. Right for
   wrong copy, a missing empty state, a control that does nothing.
3. **A screenshot comparison test** when the complaint is visual and words cannot express it.
4. **A data-access test with a mocked client** replaying the exact response that breaks it. Save the
   real payload to a fixture file first.
5. **A model test** feeding the literal payload from the failing request into its parser. Catches
   most "field is blank in the UI" bugs in seconds.
6. **An integration test** on a simulator or emulator when the bug needs the app to actually boot.
7. **The running app plus the stack's profiler** for jank, leaks, and re-render storms. The timeline
   and a rebuild counter are the instruments, not logs.
8. **A physical device** when the bug involves permissions, push delivery, background state, or the
   camera. A simulator does not reproduce these, and pretending otherwise burns a phase.

For the command that runs each rung in this project, call the Skill tool with `project-stack`,
asking for the component's `conventions`, aspect "debugging tools". It returns the test tools, the
profiler, and the stack's common causes for Phase 3.

### Tighten it

Treat the loop as a product. Once you have one, make it faster, sharper, and more deterministic:
assert the specific symptom rather than "did not throw", pin time, seed randomness, stub the
network. A two-second deterministic loop is a superpower; a thirty-second flaky one barely helps.

### Non-deterministic bugs

The goal is not a clean repro but a **higher reproduction rate**. Loop the trigger, add load, narrow
the timing window. A bug that fires half the time is debuggable; one percent is not, so keep raising
the rate until it is.

### Completion criterion

Phase 1 is done when you can name **one command you have already run at least once**, showing the
invocation and its redacted output, that is:

- **Red-capable.** It drives the real code path and asserts the **user's exact symptom**, so it can
  fail now and pass once fixed. Not "runs without erroring".
- **Deterministic.** Same verdict every run, or a pinned high rate for a flaky bug.
- **Fast.** Seconds.
- **Agent-runnable.** No human tapping required.

If you catch yourself reading code to build a theory before that command exists, **stop**. Jumping
to a hypothesis is the exact failure this skill prevents. No red command, no Phase 2.

### When you genuinely cannot build one

Say so explicitly, list what you tried, and ask for one of: access to an environment that
reproduces it, a redacted artifact (a crash report, a captured response, a screen recording with
timestamps), or permission to add temporary instrumentation to a staging build. Do **not** proceed
to hypothesise without a loop.

## Phase 2: Reproduce and minimise

Run the loop. Watch it go red.

Confirm it produces the failure **the user described**, not a nearby one that happens to fail. Wrong
bug, wrong fix. Capture the exact symptom so later phases can prove it gone.

Then shrink the repro to the smallest scenario that still goes red. Cut inputs, config, data, and
steps **one at a time**, re-running after each cut. Done when every remaining element is
load-bearing: removing any one of them turns it green.

A minimal repro shrinks the hypothesis space and becomes the regression test in Phase 5.

## Phase 3: Hypothesise

Write **3 to 5 ranked hypotheses before testing any of them**. Generating one at a time anchors you
on the first plausible idea.

Each must be falsifiable, stated as a prediction: "if X is the cause, then changing Y makes it
disappear." If you cannot state the prediction, it is a vibe — sharpen it or drop it.

Show the ranked list to the user before testing. They often re-rank it instantly ("we changed that
last week"). Cheap checkpoint; do not block on it if they are away.

Common causes worth having on the list: a parser default masking a missing field; stale state
surviving a navigation back; a component re-rendering on an unrelated state change; an update
helper that cannot set a field back to empty; an async gap after which the screen is already gone;
a listener firing on a state that only partly changed. The stack's own list comes with its
debugging tools.

## Phase 4: Instrument

Every probe maps to a specific prediction. **Change one variable at a time.**

Prefer a breakpoint or one observer on the state layer over scattered prints — one observer
logging every transition beats ten print calls. For re-render and jank questions, the profiler's
timeline is the instrument, not logs.

**Tag every debug log** with a unique prefix, `[DBG-a4f2]`. Cleanup becomes one grep, and untagged
logs are the ones that ship.

## Phase 5: Fix and lock it down

Write the regression test **before** the fix, but only if a **correct seam** exists — one where the
test exercises the real bug pattern as it occurs at the call site. A test at too shallow a seam gives
false confidence.

**If no correct seam exists, that is itself the finding.** Record it: the architecture is preventing
the bug from being locked down.

With a seam: turn the minimised repro into a failing test, watch it fail, apply the fix, watch it
pass, then re-run the Phase 1 loop against the original un-minimised scenario.

**When two fixes have failed the same loop, stop fixing.** Write down the one sentence both fixes
assumed, such as "the list rebuilds because its state changed", and test that sentence before any
third fix. Each failure under a shared assumption is evidence against the assumption, not a reason
to write another fix on top of it. If the test shows the assumption holds, look for the cause
elsewhere, and go back to the Phase 3 list.

## Phase 6: Clean up

Before declaring done:

- The original repro no longer reproduces (re-run the Phase 1 command and paste both runs).
- The regression test passes, or the absence of a seam is written down.
- Every `[DBG-...]` line is gone. Grep the prefix.
- The component's Check command is clean, and its suite matches the baseline in
  `docs/agents/project.md`.
- The hypothesis that turned out correct is stated in the commit message, so the next person to
  meet this code learns something.
