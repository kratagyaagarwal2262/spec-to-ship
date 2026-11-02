---
name: spec-for-cheap-executor
description: Write one self-contained task doc for work that leaves this session with nobody reviewing it before it lands, such as another team or a model in a tool someone else runs.
disable-model-invocation: true
---

# Spec for a Cheap Executor

You are the expensive model. You do **all** of the thinking, once. The doc you produce is
executed by a **cheaper, less capable model** (or a person) that has no context on this project,
no access to the user, and no ability to make a design call.

> **The bar:** a competent-but-literal executor applies this doc end to end and gets the
> intended result. **Anywhere it would have to guess, the doc is not finished.**

The doc is the only artifact the executor sees. It never sees this conversation, the
requirements discussion, or your reasoning. Write nothing that depends on them.

## Gate — is this the right tool?

The doc front-loads every decision because nobody will be there to catch a wrong guess
afterwards. That costs hours of the strongest model, and it pays only when the executor really is
on its own. Where someone checks the work after it is done, checking is far cheaper than this.

Take the first row that fits:

| The executor | Route |
|---|---|
| A kit agent in this session | Tell the user to run `/fk-build`. It hands mechanical slices to the build-role agents and checks each one; `configure-models` sets how cheap that role's model is. |
| A sprint of tickets, built unattended | Tell the user to run `kit loop run`. Its reviewer and CI catch what a builder gets wrong, and the builder starts on the cheapest model in its ladder. |
| Anyone, for a change small enough that the doc would hold most of its final code | Tell the user that specifying it costs more than writing it, and offer to build it here. |
| A team, a teammate, or a model in a tool someone else runs, with no review before it lands | This skill. Continue to Phase 0. |

The gate is done when you have named the row and why, in one line. On any row but the last, stop
there.

## The executor you are writing for

Design against this profile, not against an idealised reader:

| Trait | Consequence for the doc |
|-------|-------------------------|
| Literal | Follows a table exactly; follows a prose rule loosely. Prefer tables. |
| No project context | "Match the existing style" resolves to nothing. Name files, tokens, idioms. |
| Cannot ask | Every ambiguity resolves into improvisation. There is no clarification round. |
| Adds code readily, deletes almost never | Silent obsolescence is the #1 failure. Deletions must be explicit instructions with line numbers. |
| Optimistic about success | Will ship a silent no-op as "done". Label which outcomes mean something is wrong. |
| Won't derive | Any formula in prose becomes a wrong number. Ship the computed result or the literal function body. |

## Output

One doc = one shippable change.

- Default path: `docs/tasks/{NN}-{kebab-slug}.md` (`NN` = next free two-digit number). Confirm
  with the user if they name a different location.
- Markdown only. Self-contained. No links to conversation history, tickets, or "as discussed".

## Phase 0 — Intake & scope lock

Establish, asking only for what you genuinely cannot determine from the repo:

- [ ] The feature request, in the user's words
- [ ] **Is code in scope at all?** (docs-only specs are legitimate — say so explicitly)
- [ ] Files/areas that must **not** be touched
- [ ] Existing docs in `docs/tasks/` that this one overlaps or contradicts → Phase 4 becomes mandatory
- [ ] Which model executes it (affects verbosity, not rigour — assume a small, fast model if unstated)
- [ ] Whether the executor has the kit installed, and a stack kit beside it, which decides what the
      doc can cite (see [references/project-composition.md](references/project-composition.md))

Produce the Scope Box (template §1) now. Everything later is checked against it.

## Phase 1 — Ground truth: measure, never assume

Read the **real code** before proposing anything. This phase produces the Findings section,
and it is what earns the executor's trust: a doc it can spot-check is a doc it follows.

Rules:

- **No claim without `file.ext:line`.** Use markdown links (`[order_form.ext:212](src/orders/ui/order_form.ext#L212)`).
- **Run the logic by hand and record real numbers.** Not "the multiplier grows too fast" but
  "at score 3.0 the formula prescribes 17 pull-ups × 5 sets". Not "the list rebuilds often"
  but "`OrderListPage` rebuilds all 40 cards on every keystroke".
- **Every number you record is also a regression-test fixture.** Compute at boundaries
  (min, max, zero, empty, null, first, last) — those become the assertions in §10.
- Banned in Findings: *appears to*, *probably*, *seems*, *should be*, *may*.

If a finding cannot be measured, either measure it (write and run a throwaway script in your
scratchpad) or drop it. An unmeasured finding is an assumption wearing a citation.

## Phase 2 — Decision ledger (the core mechanism)

Before writing the doc, enumerate in your scratchpad **every point where the executor could
choose differently than you intend**. Then convert each into a form that removes the choice:

| If the executor would have to… | Ship this instead | Never ship |
|--------------------------------|-------------------|------------|
| Derive a value from a formula | The computed value, or the literal function body | The formula described in prose |
| Select from a set | The exhaustive table, all N rows | "Isolation moves get 8–20 reps" |
| Judge spacing / colour / hierarchy | ASCII mockup with exact tokens per state | "Make it look consistent" |
| Know that old code is now dead | `delete X at file:472, nothing replaces it` | Silence |
| Pick an order | A numbered build order, each step compiling alone | "Implement the feature" |
| Decide whether an outcome is OK | An explicit normal / anomalous label | An unannotated early return |
| Recall a project idiom | The rule + one example + the rule-file path | Assumed familiarity |

The ledger is a working artifact — it does not ship. It is cleared only when **every row maps
to a concrete section of the doc**. A row you cannot place is a section you still owe.

## Phase 3 — Compose the doc

Follow [references/doc-template.md](references/doc-template.md) — all eleven sections, in
order, none omitted. A section with nothing to say says "None." and states why; it is never
silently dropped.

**Generate exhaustive tables programmatically.** When a table has more than ~10 rows, write a
generator script into your session scratchpad, run it, and paste the output into the doc.
Never hand-type a long table (you will skip rows) and never replace it with the rule that
produced it (the executor will misapply it). Long is fine; ambiguous is not.

**Cite this project's tooling by name** so the executor inherits conventions instead of
re-deriving them — see [references/project-composition.md](references/project-composition.md).

## Phase 4 — Coupling pass: corrections, not additions

Only when earlier docs exist. When one doc ships before another, the earlier one can make
statements in the later one **false**. Appending "note: see doc 03" is the wrong move — the
executor reads the stale text first and applies it.

Follow [references/coupling.md](references/coupling.md): delete the stale section, replace it,
fix every downstream reference (state fields, UI branches, test steps, build-order numbering),
and record what changed and why in the doc's changelog.

## Phase 5 — Adversarial self-audit

Re-read the finished doc **as the executor**: literal, contextless, unable to ask. Work
[references/audit-checklist.md](references/audit-checklist.md) line by line.

Every place you would have to guess goes back to Phase 2. Do not ship a doc with an open
ledger row — the executor's improvisation is exactly the cost this skill exists to avoid.

Finally, report to the user: the doc path, its section count, the exhaustive tables it
contains (with row counts), and any assumption you locked in on their behalf.

## After the executor runs

When the cheap model has executed the doc and the user comes back with bugs, call the Skill tool
with `triage-executor-bugs`. Bugs traced to an ambiguity in *this*
doc are `spec-defect`s: they oblige a correction here (via
[references/coupling.md](references/coupling.md)), not just a patch to the code. Recurring defect
classes get promoted into [references/audit-checklist.md](references/audit-checklist.md) so the
next spec prevents them.

## Hard rules

- **No `TODO`, no "decide during implementation", no "as appropriate".** If you are tempted,
  you have found a decision you have not made yet.
- **No prose algorithms.** If the executor would derive it, derive it in the doc.
- **No selection rules where a table fits.** Enumerate.
- **Deletions are instructions, not observations.** `file:line` + "nothing replaces it".
- **Every number carries its source** — a `file:line` for measured values, a named formula
  input for computed ones.
- **The doc is self-contained.** No "see the conversation", no ticket links as the only source
  of a requirement, no unexplained project jargon.
- **Name the project's skills and rules explicitly** (`project-stack` with a component and a slot,
  `security-audit`, a file under `.claude/rules/`) rather than restating them, citing skills only
  where the executor has the kit.
- **Verification is executable** — real commands, exact assertions, and at least one test that
  must **fail before** a named step and **pass after** it.
