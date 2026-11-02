# Task-doc template

Eleven sections plus a header, in this order. None is optional; a section with nothing to say
writes `**None.**` and one line of why.

For each section below: **Form** is the skeleton to emit, **Example** is a filled instance,
**Fails when** is the executor behaviour you are preventing.

The examples serve every stack, so their code is pseudo-code and their paths a neutral layout
(`src/`, `tests/`, a `.ext` extension). In the doc you ship, every block is real code in the
component's language, which the executor pastes verbatim, and every path is a real one.

---

## Header

```markdown
# {NN} — {Imperative title}

| | |
|---|---|
| **Status** | Ready to execute |
| **Executor** | Assume no prior context on this repo |
| **Prerequisites** | Doc 02 must be shipped and merged first / None |
| **Supersedes** | Doc 01 §4 and §7 (see Changelog) / Nothing |
| **Est. touched files** | 6 modified, 2 created, 1 deleted |

## Changelog
| Date | Change | Reason |
|------|--------|--------|
| 2026-08-01 | §4 rewritten, §6 deleted | Doc 02 shipped `OrderStatus.pending`, invalidating both |
```

Omit the Changelog table entirely on a first-issue doc.

---

## §1 Scope box

**Form** — three explicit lists and one yes/no. Put it above everything else; it is the
executor's contract.

```markdown
## 1. Scope

**Code in scope:** YES — source under `src/orders/` and `tests/orders/`.

**Create**
- `src/orders/ui/order_status_chip.ext`
- `tests/orders/ui/order_status_chip_test.ext`

**Modify**
- `src/orders/ui/order_card.ext` — add the chip, delete the inline badge
- `src/core/exports.ext` — export the new chip
- `src/core/constants/colors.ext` — add three status colours

**Do NOT touch**
- `src/<other_feature>/**` — visually similar cards; out of scope, leave them inconsistent
- `src/core/network/api_client.ext` — no network change in this task
- Any file under `src/notifications/` — doc 04 owns it
```

**Fails when** omitted: the executor "helpfully" refactors the adjacent card, or
touches a file another in-flight doc owns, producing a conflict nobody asked for.

**Rule:** "Do NOT touch" must name the things a reasonable executor would be *tempted* to
touch — near-duplicates, obvious inconsistencies, adjacent dead code. Listing unrelated
directories is noise.

---

## §2 Findings — measured, not assumed

**Form** — a table of defects, each with a `file:line` link and a concrete number. Follow with
the boundary values you computed; they become the §10 fixtures.

```markdown
## 2. Findings

| # | Finding | Location | Measured |
|---|---------|----------|----------|
| F1 | Difficulty multiplier is unbounded | [progression.ext:88](src/core/progression.ext#L88) | At score 3.0 it prescribes **17 pull-ups × 5 sets**; at 4.0, **31 × 5** |
| F2 | Order list rebuilds every card per keystroke | [order_list_page.ext:140](src/orders/ui/order_list_page.ext#L140) | 40 cards rebuilt per character; 9 chars typed = 360 rebuilds |
| F3 | `status` is parsed but never rendered | [order.ext:31](src/orders/model/order.ext#L31) | Field read by the JSON parser, zero references under `src/orders/ui/` |

**Boundary values measured today (become test fixtures in §10):**

| Input score | Current reps | Current sets |
|---|---|---|
| 0.0 | 3 | 3 |
| 1.0 | 5 | 3 |
| 2.0 | 9 | 4 |
| 3.0 | 17 | 5 |
| 4.0 | 31 | 5 |
```

**Fails when** omitted or hedged: the executor cannot verify the premise, so it either
re-derives the problem (differently) or implements a fix for a defect that does not exist.

**Rule:** no *appears to* / *probably* / *seems*. If you could not measure it, do not claim it.

---

## §3 Algorithms as literal code

**Form** — the complete function body, in the project's language, with the signature the
executor will paste. Not pseudocode, not a description. (The example is pseudo-code only because
this template serves every language; the shipped block is the real thing.)

````markdown
## 3. Algorithm — replacement progression curve

Replace the body of `nextPrescription` at [progression.ext:88-104](src/core/progression.ext#L88-L104)
with exactly this:

```text
function nextPrescription(score: float) -> (reps: int, sets: int)
  // Logistic ceiling: reps asymptote at 20, never the exponential blow-up in F1.
  clamped = clamp(score, 0.0, 5.0)
  reps    = round_half_away_from_zero(3 + 17 / (1 + exp(-1.4 * (clamped - 2.5))))
  sets    = 3 if clamped < 1.0
            4 if clamped < 3.0
            5 otherwise
  return (reps, sets)
```

`exp` is already imported in this file; add no import.
````

**Fails when** written as prose ("cap the reps with a smooth curve"): every executor produces
a different curve, and none matches the §10 assertions.

**Rule:** if the executor would have to *derive* anything — a constant, a rounding mode, a tie
break, an ordering — derive it here. A 40-line function body is cheap; a judgment call is not.

---

## §4 Enumerate, never describe

**Form** — the full table. Generate it with a script in your scratchpad and paste the output.

```markdown
## 4. Rep ranges — complete table (79 rows)

Apply exactly. Do not infer from the movement name; if a movement is absent from this table
it is out of scope for this task.

| # | Movement | Category | Min reps | Max reps | Sets |
|---|----------|----------|----------|----------|------|
| 1 | Barbell back squat | compound-lower | 4 | 8 | 5 |
| 2 | Front squat | compound-lower | 4 | 8 | 5 |
| 3 | Lateral raise | isolation-shoulder | 12 | 20 | 3 |
| … | (all 79 rows present in the shipped doc) | | | | |
```

**Fails when** replaced by the rule that generated it ("isolation moves get 8–20 reps"): the
executor's classification of *isolation* differs from yours on ~15% of rows, silently.

**Rule:** long is fine, ambiguous is not. State the closed-world clause explicitly — "if it is
not in this table, it is out of scope" — or the executor will extend the table by analogy.

---

## §5 UI as ASCII mockups with exact tokens

**Form** — one mockup **per screen state**, not per screen. Annotate every text run and box
with size, weight, colour token, radius, padding.

```markdown
## 5. UI — `OrderCard`, all four states

### 5.1 State: confirmed

┌──────────────────────────────────────────────┐  ← Card: radius `radius.md` (12), `colors.surface`,
│  ┌────┐                                      │     padding `space.lg` (16) on all sides
│  │ AV │  Priya Raman            ┌──────────┐ │  ← Avatar 40 × 40, radius `radius.full`
│  └────┘  Confirmed              │ Confirmed│ │  ← Chip: height 24, padding `space.sm`/`space.xs`,
│          +61 4XX XXX XXX        └──────────┘ │     radius `radius.md`, `colors.successBg`
└──────────────────────────────────────────────┘

| Element | Style |
|---------|-------|
| Name | size 16 / weight 600 / `colors.textPrimary` |
| Phone | size 13 / weight 400 / `colors.textMuted` |
| Chip label | size 11 / weight 500 / `colors.successFg` |
| Chip fill | `colors.successBg` (add: `#E7F6EC`) |
| Gap avatar→text | `space.md` (12), horizontal |
| Gap name→phone | `space.xs` (4), vertical |

### 5.2 State: pending
Identical to 5.1 except: chip label "Pending", fill `colors.warningBg`
(add: `#FFF4E0`), text `colors.warningFg` (add: `#8A5A00`).

### 5.3 State: declined
… (one block per state — never "and similarly for the others")

### 5.4 State: loading (skeleton)
…
```

**Fails when** written as "make it look consistent with the other card": the executor copies
that card wholesale, including its hardcoded colours, violating the constants rule.

**Rule:** every colour is a named token. If the token does not exist yet, the mockup says
`(add: #…)` and §1 lists the constants file under **Modify**.

---

## §6 Deletions — explicit

**Form** — a table. Each row is an instruction, and each row states what replaces it (often
"nothing").

```markdown
## 6. Deletions

| # | Delete | Location | Replaced by |
|---|--------|----------|-------------|
| D1 | `_StatusBadge` class (lines 118–166) | [order_card.ext:118](src/orders/ui/order_card.ext#L118) | `OrderStatusChip` from §5 |
| D2 | `formatBadgeLabel()` | [order_card.ext:472](src/orders/ui/order_card.ext#L472) | **Nothing.** Its only caller is D1. |
| D3 | `colors.badgeGrey` | [colors.ext:64](src/core/constants/colors.ext#L64) | **Nothing.** Unused after D1; verified with `rg badgeGrey`. |
| D4 | Test group `'_StatusBadge'` (lines 88–140) | [order_list_test.ext:88](tests/orders/ui/order_list_test.ext#L88) | New group in §10.2 |

After applying D1–D4, this command must print nothing:

```bash
rg -n '_StatusBadge|formatBadgeLabel|badgeGrey' src/ tests/
```
```

**Fails when** omitted: the executor adds the new chip and leaves the old badge in place —
compiling, untested, and now silently dead. This is the single most common cheap-executor
failure. Always pair deletions with a `rg` command that proves they happened.

---

## §7 Migration & back-compat hazards

**Form** — what must never change, plus the exact guard code to copy.

````markdown
## 7. Migration & back-compat

**Must never change**
- `OrderStatus` enum **ordering** — index is persisted in on-device key-value storage under
  `order_filter_index`. Append new values at the end only.
- The `status` JSON string values (`"confirmed"`, `"pending"`, `"declined"`) — server-owned.
- Route id `routes.orderList` — deep links in production notifications point at it.

**Guard for rows written before this change** — paste verbatim into
`Order`'s JSON parser at [order.ext:31](src/orders/model/order.ext#L31):

```text
// Rows written before 2026-08 have no `status`; they are all confirmed orders.
raw    = json["status"] if it is a string, else "confirmed"
status = the OrderStatus whose name equals raw, else OrderStatus.confirmed
```

The `else OrderStatus.confirmed` fallback is required: an unknown server value must degrade to
`confirmed`, never throw.
````

**Fails when** omitted: the executor reorders an enum alphabetically "for tidiness" and every
stored index now points at the wrong value.

---

## §8 Failure modes, labelled

**Form** — a table separating *normal* outcomes from *something is wrong*, tied to observable
behaviour.

```markdown
## 8. Failure modes

| Outcome | Verdict | What to do |
|---------|---------|------------|
| Order list renders 0 cards, empty-state shown | **Normal** — user has no orders | Nothing |
| `OrderStatusChip` renders with no label | **Wrong** — status failed to parse; §7 guard missing or misapplied | Re-check §7 |
| Migration loop exits before reading any row | **Wrong** — a data gap, not a valid result. Do not report success | Stop and report the row count read |
| The test suite passes but `rg` in §6 prints matches | **Wrong** — new code added, old code not deleted | Apply §6 fully |
| Static check reports `order_status_chip.ext` as unused | **Wrong** — the chip was never wired into `OrderCard` | Complete step 4 of §9 |
```

**Fails when** omitted: the executor treats "zero rows migrated, no exception" as success and
reports the task complete.

---

## §9 Build order

**Form** — numbered steps, each of which **compiles on its own**, with the single behavioural
cutover named.

```markdown
## 9. Build order

Each step leaves the tree compiling and `make check` clean. Commit per step if you like.

1. Add the three colour constants (§5) to `colors.ext`. *No behaviour change.*
2. Add the `status` field + §7 guard to `Order`. *No behaviour change — nothing reads it yet.*
3. Create `order_status_chip.ext` (§5) and export it from `exports.ext`. *Not yet used.*
4. **CUTOVER** — in `order_card.ext`, replace the `_StatusBadge` usage with `OrderStatusChip`.
   This is the only step that changes what the user sees.
5. Apply deletions D1–D4 (§6) and run the §6 `rg` check.
6. Add the tests in §10.2 and run the full suite.
```

**Fails when** omitted: the executor writes everything at once, hits a compile error in the
middle, and starts "fixing" unrelated code to get green.

**Rule:** exactly one step is labelled **CUTOVER**. If you need two, the doc should be two docs.

---

## §10 Verification

**Form** — three parts: exact-assertion unit tests (including one fail-before/pass-after),
manual steps, and the static-analysis commands.

````markdown
## 10. Verification

### 10.1 Regression test — must FAIL before step 1, PASS after step 4

```text
test "OrderCard renders a status chip for a pending order":
  render OrderCard(order: anOrder(status: OrderStatus.pending))
  expect exactly one OrderStatusChip is rendered
  expect exactly one text equal to strings.orderStatusPending is rendered
```

Run it **before** starting: it must fail with `expected 1 OrderStatusChip, found 0`. If it fails
for any other reason, stop — the doc's premise does not match the tree.

### 10.2 Assertions — exact, from §2 boundary values

| Test | Input | Expect |
|------|-------|--------|
| `nextPrescription` floor | `0.0` | `reps == 3`, `sets == 3` |
| `nextPrescription` midpoint | `2.5` | `reps == 12`, `sets == 4` |
| `nextPrescription` ceiling | `5.0` | `reps == 20`, `sets == 5` |
| `nextPrescription` clamps above range | `9.9` | identical to `5.0` |
| `Order.fromJson` legacy row | `{"id":"1"}` (no `status`) | `status == OrderStatus.confirmed` |
| `Order.fromJson` unknown value | `{"status":"archived"}` | `status == OrderStatus.confirmed`, no throw |

### 10.3 Manual

1. `make run`, navigate Home → Orders.
2. Confirm each of the four states in §5 renders as mocked (seed with the fixture in §10.2).
3. Rotate the device — the chip must not wrap or clip.

### 10.4 Static

```bash
make check     # must report "No issues found."
make test
rg -n '_StatusBadge|formatBadgeLabel|badgeGrey' src/ tests/   # must print nothing
```
````

Every command is the component's own, copied from its row in the Components table of
`docs/agents/project.md`: `make check` stands for its Check column, `make run` for Run, `make test`
for Test.

**Fails when** assertions are approximate ("reps should be reasonable"): the executor writes a
test that passes against its own wrong implementation.

---

## §11 Style contract

**Form** — the project's **non-obvious** idioms only, each as a rule plus one example, each
pointing at the authoritative rule file rather than restating it.

```markdown
## 11. Style contract

The rules below are non-obvious and violated by default. Full spec:
[CLAUDE.md](CLAUDE.md), `.claude/rules/ui.md`, `.cursor/rules/conventions.mdc`.

| # | Rule | Example |
|---|------|---------|
| S1 | Exactly one project import per file — the barrel | `import src/core/exports` and nothing else |
| S2 | Every new `src/` file gets an export line in `exports.ext`, alphabetical within its section | `export src/orders/ui/order_status_chip` |
| S3 | Sizes come from the spacing tokens; font sizes unscaled | `space.md`, not `16` |
| S4 | Alpha lives in the colour constant, never applied at the callsite | `colors.scrim` (`#80000000`), not black faded to 50% inline |
| S5 | A named private view class per piece of UI, never a helper function returning UI | `class _StatusRow`, not `buildStatusRow()` |
| S6 | No untyped values — explicit types, immutable by default | `label: string = json["label"] if it is a string, else ""`, declared constant |
| S7 | No inline colours / strings / asset paths | `strings.orderStatusPending`, not `"Pending"` |
| S8 | `FIXTURE_START` / `FIXTURE:` comment markers are sanctioned conventions — leave them alone | Do not "clean up" a fixture marker |
```

**Fails when** omitted: the executor writes code idiomatic to the language at large, which is
*wrong* here — direct imports, raw numbers at the callsite, opacity applied inline, and helper
functions returning UI.

**Rule:** point at the rule file; restate only the handful of rules this task will actually
brush against. A style contract that restates the whole convention set gets skimmed. To find
them, call the Skill tool with `project-stack`, asking for the component's `conventions` on the
aspects the task touches, and cite the file each answer names.
