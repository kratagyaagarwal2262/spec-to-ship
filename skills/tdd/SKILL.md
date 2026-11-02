---
name: tdd
description: Build a change test-first in thin vertical slices: a failing test at a named seam, seen to fail for the intended reason, then the smallest code that passes it. The test tool and layout come from the component's conventions. Use when the user asks for test-driven development, red-green-refactor, a failing test first, or a regression test before a fix.
---

# TDD

Write the test before the code, so the test is shaped by what the feature must do rather than by
what the code happens to do. A test written afterwards passes because it was written against the
implementation in front of you, which is why it so rarely catches the bug you feared.

This skill owns the loop, the seam choice and what makes a test worth keeping. The stack owns the
test tool and the file layout. Call the Skill tool with `verify` to report what was proven. Where
the target is an existing bug rather than new behaviour, call the Skill tool with `diagnose-bug`
instead. Its Phase 1 is this same red loop, built for a symptom nobody can yet explain.

## 1. Pick the seam

Call the Skill tool with `project-stack` for the `conventions` slot of the component the change
lands in, asking for its test tooling and layout: the test tool, where a test file goes, and how a
unit at each seam is driven. Where no stack kit answered, read one existing test beside the code you
are changing and take its tool, location and setup from there.

Then choose the cheapest seam that can actually express the requirement:

| The requirement is about | Test at |
|---|---|
| A status transition, a computed value, an error mapping | The logic seam |
| Parsing, defaults, a shape change | The model's parse from the wire format |
| Which call is made, and what a failure becomes | The data-access layer, with its client faked |
| Copy, an empty state, a tap dispatching an action | A test that renders the screen |
| Pixels against an approved design | A screenshot compared to an approved baseline |

One requirement, one seam. A requirement that seems to need two is usually two requirements, and
splitting it is the cheaper move.

This step is done when you can name the seam, the test file's path and the tool that drives it.

## 2. Red

Write the test and **run it**. It must fail for the intended reason, which is not the same as
failing. A test that fails on a missing import, a null in the fixture, or a typo in a selector
proves nothing about the behaviour, and it will pass later for reasons equally unrelated.

Read the failure message and confirm it names the assertion you meant to make.

Derive the expected value from the requirement, the design, or the API sample. A value copied from
what the code currently returns tests that the code does what it does.

Give the test a way to fail for a defect. Ask whether it would still pass if every function it calls
returned nothing. If it would, it observes no behaviour: call the subject with one concrete input
and compare the output, or the state after, against a literal. The shapes that pass that way:

- only an existence, non-null or type check
- only a call count, with nothing about the arguments or the state that followed
- an expected value computed by the code under test
- an assertion that restates a constant, such as a token, a default or a string table row
- an assertion on the fixture the test built, with the subject never run

Name the test for what it asserts, so a failure line is a bug report. Assert on the fields the
criterion is about, not every property: a test asserting everything fails on changes it was never
written to catch, and gets deleted rather than fixed.

## 3. Green

Write the smallest change that makes the test pass. Not the general version, not the version
handling the next three cases, and not the refactor you can already see. Those come after, and they
come with the test already protecting them.

## 4. Refactor

With the test green, improve the shape. Run the test after each step. The green bar is what makes
this safe, and it is the only part of the cycle that gets skipped without immediately hurting.

## 5. Next slice

Take the next thin vertical slice, not the next layer. One behaviour end to end beats every model
followed by every data-access class followed by every state class: a vertical slice can be
demonstrated and gets feedback, while a horizontal one is only testable once the last layer lands.

Repeat until every acceptance criterion has a test naming it.

## Completion criteria

Every acceptance criterion maps to a test that **was seen to fail before the code existed**, and the
suite is green against the baseline in `docs/agents/project.md`.

Name any criterion you could not drive from a test, the seam it would need, and what was missing.
That sentence is how the gap gets closed rather than quietly reclassified as covered.
