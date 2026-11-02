---
name: triage-executor-bugs
description: Diagnose and route bugs found after a cheap model executed a spec-for-cheap-executor task doc. Batches bug reports, finds root causes (which usually cluster), then routes each one to inline repair, a mechanical fix doc for the cheap executor, or an amendment to the original spec. Use when reporting bugs in work a cheaper model just shipped, after switching back to a stronger model to fix an executed task doc, or when asking whether to fix something directly or hand it back.
---

# Triage Executor Bugs

The follow-up half of [spec-for-cheap-executor](../spec-for-cheap-executor/SKILL.md). A cheap
model executed a task doc; the user found bugs; you are the expensive model they switched back to.

**Your job is not "fix the bugs". It is: diagnose once, then route each defect to the cheapest
agent that can resolve it *without judgment* — and repair the spec that caused it.**

## The economics you are optimising against

Diagnosis is reasoning-heavy and unavoidable — you pay it no matter what happens next. Once you
hold the diagnosis, you have already spent most of the money. Writing a fix doc so a cheap model
can apply a three-line change costs *more* than applying it yourself.

The fix doc only wins when **one diagnosis unlocks many mechanical sites**. That happens more
often than it sounds here, because cheap-executor bugs cluster: one ambiguous spec section gets
misread once and misapplied everywhere it appears.

Full decision table and break-even reasoning: [references/routing.md](references/routing.md).

## Phase 0 — Batch intake

**Collect every known bug before diagnosing anything.** Each model switch re-pays the cost of
reading the codebase from scratch; five bugs in one pass is far cheaper than five passes.

Ask the user for anything missing, in one batch:

```
Per bug:
- [ ] Symptom — what you saw, in your words
- [ ] Repro — screen / input / steps, or the failing test name
- [ ] Expected vs observed
- [ ] Which task doc shipped this (docs/tasks/NN-*.md)

Once:
- [ ] Is this the complete list, or is more testing still happening?
```

If the user has more testing to do, say so plainly and offer to wait — starting now means a
second full diagnosis pass later.

Vague reports ("the order screen looks wrong") are normal. Do not bounce them back for detail
you can get yourself; run the app or read the code. Bounce back only when you cannot reproduce
and the symptom depends on data you do not have.

## Phase 1 — Diagnose (expensive, unavoidable, do it properly)

For each symptom, find the **root cause**, not the surface. Same standard as the spec skill's
Findings: `file:line` links, real values, no *appears to*.

Record, per symptom:

| Field | Content |
|-------|---------|
| Symptom | As reported |
| Root cause | One sentence, at `file:line` |
| Blast radius | Every site with the same cause — **count them** with `rg` |
| Origin | `spec-defect` / `executor-slip` / `unknowable` |

**Origin drives everything downstream**, so classify it honestly:

- **`spec-defect`** — the doc was ambiguous, incomplete, or wrong. The executor followed it
  faithfully. Quote the offending line from the task doc. This obliges a Phase 4c amendment.
- **`executor-slip`** — the doc was unambiguous and the executor deviated anyway. No spec change;
  consider whether the audit checklist should have caught it (Phase 5).
- **`unknowable`** — neither party could have known (API behaved differently, a dependency
  changed, the requirement was wrong). Not a process failure; just fix it.

Default to `spec-defect` when it is genuinely arguable. Blaming the executor is comfortable and
teaches nothing.

## Phase 2 — Cluster

Collapse symptoms into root causes. Five bug reports are frequently one cause.

```markdown
| Cluster | Root cause | Symptoms | Sites | Origin |
|---------|-----------|----------|-------|--------|
| C1 | `statusChip` never wired into 3 of 4 states | B1, B2, B5 | 3 | spec-defect (§5.2–5.4 said "and similarly") |
| C2 | List lookup with no not-found guard | B3 | 1 | executor-slip (§7 gave the guard verbatim) |
| C3 | Chip clips on a 320-wide screen | B4 | 1 | unknowable (not in §5 mockups) |
```

Cluster **before** routing. A per-bug routing decision will send three symptoms of one cause
down three different paths.

## Phase 3 — Route each cluster

Apply the table in [references/routing.md](references/routing.md). Summary:

| Route | When | Cost shape |
|-------|------|-----------|
| **A — Fix inline** | Few sites, or any per-site judgment, or unfamiliar subsystem | You edit. Cheapest for the common case. |
| **B — Fix doc → cheap executor** | Many near-identical sites, zero judgment per site | Expensive doc + cheap application. Wins on volume only. |
| **C — Amend the spec** | Origin is `spec-defect` | Mandatory *in addition to* A or B, never instead of |

Route A is the default and will be the majority. Choosing B for a small fix is the failure mode
this skill exists to prevent — state the site count when you pick B, so the choice is auditable.

Present the routing table to the user before executing. This is the one point where their
judgment beats yours: they know whether more bugs are coming.

## Phase 4 — Execute

### 4a — Inline fixes (Route A)

Fix directly. For each, add a regression test that **fails before** the fix and passes after,
following §10.1 of the spec template. Call the Skill tool with `project-stack` for the component's
Check and Test commands, and run both.

### 4b — Fix doc (Route B)

Write it per [references/fix-doc-template.md](references/fix-doc-template.md), to
`docs/tasks/NN-fix-{slug}.md`.

A fix doc is **tighter than a spec doc**, because the executor is now editing a codebase it
partly wrote and will be tempted to tidy: verbatim before/after per site, an exhaustive site
inventory produced by a command, a hard "change nothing else" boundary, and a match-count
assertion that proves completion.

### 4c — Spec amendment (Route C)

The original task doc is now **wrong** — it contains the text that produced the bug. Leaving it
means the next feature built from it repeats the defect.

Apply the correction protocol from
[spec-for-cheap-executor/references/coupling.md](../spec-for-cheap-executor/references/coupling.md):
delete the stale section, replace it with an unambiguous version, chase downstream references,
and add a changelog row naming the bug that forced the change.

Do not append "this was ambiguous, see fix doc 07". That leaves the ambiguity in place.

## Phase 5 — Close the loop

For each cluster, ask: **would the spec skill's audit checklist have caught this?**

- If yes → the audit was skipped. Note it; no file change.
- If no, and the defect class is likely to recur → add a line to
  [spec-for-cheap-executor/references/audit-checklist.md](../spec-for-cheap-executor/references/audit-checklist.md)
  or a *Fails when* note in its doc template.

This is the compounding part of the workflow. A defect class promoted into the checklist is
prevented in every future spec; a bug merely fixed is prevented in none.

Only promote patterns you have now seen bite. A checklist that grows on speculation gets skimmed,
and a skimmed checklist catches nothing.

## Report

Close with:

- Cluster table: root cause → symptoms → route → status
- Files changed inline; fix docs written; spec sections amended
- Test results (the Check and Test commands) — state failures plainly, with output
- Any bug you could **not** reproduce, and what you need to proceed
- Whether anything was promoted into the audit checklist

## Hard rules

- **Diagnose before routing** — a route chosen from a symptom is a guess.
- **Cluster before routing** — one cause, one route.
- **Route A is the default.** Justify B with a site count, never with a feeling.
- **Never route a judgment call to the cheap executor.** It failed here once already.
- **`spec-defect` obliges an amendment.** Fixing only the code leaves the cause in place.
- **Every confirmed bug gets a test that fails before its fix.** Otherwise you cannot prove the
  fix landed, and neither can the next executor.
- **Never re-issue an instruction at the specificity that caused the bug** — if "and similarly"
  broke it, the replacement is verbatim per site.
