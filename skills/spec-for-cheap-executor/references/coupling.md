# Multi-doc coupling: corrections, not additions

When doc 02 ships before doc 03, doc 02's changes can make statements in doc 03 **false** —
and vice versa when a later doc redesigns something an earlier doc described.

The wrong move is appending. `> Note: see doc 03 for the updated shape` leaves the stale text
in place, and the executor reads it first, applies it, and only then reaches the note. A cheap
executor does not reconcile two contradictory instructions; it follows whichever it read last
in the section it happened to be working from.

**The rule: delete the stale text and replace it. A corrected doc reads as if it were always
correct, plus a changelog row explaining the change.**

## Procedure

### 1. Detect

Before writing or revising any doc, list the other docs in `docs/tasks/` and identify overlap.
Overlap is not just "same feature" — these are the real coupling surfaces:

| Coupling surface | Example break |
|------------------|---------------|
| Shared state fields | Doc 02 added `OrderState.filter`; doc 03's state-copy snippet omits it |
| Enum values / ordering | Doc 02 appended `OrderStatus.pending`; doc 03's exhaustive table has 3 rows, needs 4 |
| Shared UI pieces | Doc 02 extracted `OrderStatusChip`; doc 03 still says "add an inline badge" |
| File line numbers | Doc 02 inserted 40 lines; every `file:472` in doc 03 is now `file:512` |
| Deletion targets | Doc 02 already deleted `formatBadgeLabel`; doc 03's D2 will no-op and confuse |
| UI states | Doc 02 added a state; doc 03's §5 has a mockup per state and is now missing one |
| Test names | Doc 02 renamed a group; doc 03's "must fail before" test now fails for the wrong reason |
| Build-order prerequisites | Doc 03 step 1 assumes doc 02 step 4 shipped — say so in the header |
| Constants | Doc 02 added `colors.warningBg`; doc 03 says "(add: #FFF4E0)" and will duplicate it |

### 2. Correct

For every break:

1. **Delete** the stale section or table row outright. Do not strike it through, do not wrap it
   in "previously". The executor should never read the old version.
2. **Replace** with the now-correct text — same section number, same form, fully rewritten.
3. **Re-measure.** Line numbers in the corrected section must come from reading the file *as it
   is now*, after the earlier doc shipped. Every `file:line` in the corrected section is
   re-verified, not adjusted by arithmetic.
4. **Chase downstream references.** A change to §4 usually forces edits in §5 (a new state → a
   new mockup), §9 (a step becomes a no-op → renumber), and §10 (assertions move). Walk the
   whole doc; do not stop at the first section you fixed.
5. **Re-run the §6 `rg` checks** mentally against the new tree — a deletion the earlier doc
   already performed must be removed from §6, not left to no-op.

### 3. Record

Add one changelog row per correction in the doc header. State what changed **and why**, naming
the doc that forced it:

```markdown
## Changelog
| Date | Change | Reason |
|------|--------|--------|
| 2026-08-01 | §4 table regenerated: 3 rows → 4 | Doc 02 shipped `OrderStatus.pending` |
| 2026-08-01 | §5.3 mockup added (pending state) | Downstream of the §4 change |
| 2026-08-01 | §6 D2 removed | Doc 02 already deleted `formatBadgeLabel`; the row would no-op |
| 2026-08-01 | All `order_card.ext` line refs re-measured | Doc 02 inserted 40 lines above them |
```

The changelog is for the human reviewing the doc. The executor does not act on it — which is
exactly why the body must already be correct without it.

### 4. Declare the dependency

If the corrected doc now *requires* the other to have shipped, say so in the header:

```markdown
| **Prerequisites** | Doc 02 shipped and merged. Verify: `rg -q 'OrderStatus.pending' src/orders/model/order.ext` returns 0. |
```

Give a runnable check, not a trust statement. If it fails, the executor stops — the alternative
is applying a doc whose premise is false.

## Ordering choice

When two docs collide and neither has shipped, you have two options. Pick one and state it:

- **Sequence them** — add a `Prerequisites` row and correct the later doc to assume the earlier
  landed. Preferred: each doc stays simple.
- **Merge them** — if the cutover in §9 cannot be split (both docs must change the same line in
  the same commit to compile), they are one doc. Merge and renumber.

Never ship two docs that both claim ownership of the same file region. §1's "Do NOT touch" list
in each is where that ownership gets recorded.
