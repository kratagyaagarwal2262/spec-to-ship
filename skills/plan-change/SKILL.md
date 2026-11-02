---
name: plan-change
description: Design a change before writing it: the types, signatures and module boundaries it needs, and the order the work lands in. Use before implementing anything touching more than one file, when a change needs a technical design, or when deciding between implementation approaches.
---

# Plan change

Decide the shape before writing the code. A design settled in a sketch costs minutes to change; the
same decision found halfway through an implementation costs the implementation.

This is the **technical** counterpart to a spec. `to-spec` writes what the software should do for a
user and deliberately excludes file paths and code. This skill picks the types, the seams and the
order, and it starts from a settled requirement. Where the requirement is not settled, call the
Skill tool with `grill` first: designing against a guess produces a good design for the wrong
problem.

## 1. Ground

Read before proposing. Dispatch the `codebase-explorer` agent for the reading, so the sketch is
written in a clean window, and answer:

- Which features and which files does this touch?
- What already exists that this should use instead of duplicating, and what does the stack decide
  for me? Call the Skill tool with `project-stack`, asking for the `conventions` of each component
  this touches, then read the shared code it points to for what is actually there.
- What did previous decisions already fix? Read `docs/adr/`.

Ground first because a design proposed without it re-invents something the repo has, and that is the
most common failure of this step.

## 2. Sketch

Write the shape, with no bodies. Signatures, types, and the boundaries between them:

- **Types.** The data this introduces or changes, and where illegal states are made unrepresentable.
- **The seam.** Which actions the state layer gains, and which states it can be in.
- **Data-access signatures.** What each method takes and returns, including its failure shape.
- **UI boundaries.** Which parts of a screen are their own components, and what each takes.
- **What is deleted.** A change that only adds is usually a change that missed something.
- **Owners.** For each piece of state the change writes, the one place that writes it; for each task
  it introduces, whether the code already has a way to do it. A second writer, a second way or a
  second hand-kept list is what the next agent will copy from.

Keep it to signatures. The moment you write a body you are implementing, and the point of the sketch
is that it is cheap to throw away.

Where a decision has more than one defensible answer, name the alternatives and pick one with a
reason. Call the Skill tool with `engineering-principles` when the choice is between shapes rather
than between behaviours.

## 3. Sequence

Order the work so each step lands at a state that can be proven, not merely compiled. Call the Skill
tool with `verify` for the rungs, and say which rung each step reaches.

A step that can only be verified once three later steps land is too big, and should be split until
each one can be demonstrated on its own.

## 4. Agree

Present the sketch and wait. This is the cheapest point at which the user can say "that is not what
I meant", and the whole skill exists to create that moment.

Write the outcome down:

- The sketch goes into the **Sketch** section of the spec it implements, so `/fk-build`, often in a
  later session or under `kit loop`, reads one file and finds both the contract and the shape.
  Where there is no spec, the sketch stays in the reply: the build happens in this session.
- A decision that is **hard to reverse** goes to `docs/adr/` as an ADR: the context, the options, the
  choice, and what it costs. A choice of database, an auth model, an offline strategy, a
  state-management change. Nothing else does this today, which is why decisions get re-argued.

Then call the Skill tool with `next-step`, handing off `/fk-build` with the spec path.

## 5. Scrap

Revisit the sketch while implementing. Deviation is a signal, not something to hide: when the
implementation keeps needing a workaround, an escape-hatch type, or a surprise about shared state,
the sketch was wrong.

Say so and re-sketch. Carrying a design the code is already fighting is how the ball of mud starts,
and every workaround added after that point is harder to unpick than the redesign would have been.

## Completion criteria

The sketch names every type, signature and boundary the change introduces or alters, every
hard-to-reverse decision has an ADR, and the sequence gives each step a verifiable end state.

Name anything you could not decide and what would settle it. An unnamed open question becomes an
implementation-time guess by whoever hits it first.
