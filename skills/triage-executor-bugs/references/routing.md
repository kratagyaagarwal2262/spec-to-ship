# Routing a cluster: inline, fix doc, or spec amendment

## The cost model

Four costs are in play. Only two of them move when you change route:

| Cost | Route A (inline) | Route B (fix doc) |
|------|------------------|-------------------|
| Diagnosis (expensive reasoning) | Paid | Paid — **identical** |
| Writing the change | A few edits, expensive tier | A doc, expensive tier — **larger** |
| Applying the change | Included above | Cheap tier, plus re-reading context |
| Verification | One pass | One pass, plus a round-trip if the executor deviates |

Diagnosis does not change. That is the whole point: **you have already spent the expensive part
by the time you are choosing a route.** Route B adds expensive-tier *writing* in exchange for
moving *application* to the cheap tier.

So the question is never "is this a bug?" It is:

> **Is the mechanical application large enough that moving it to the cheap tier saves more than
> writing the doc costs?**

For a three-line fix the answer is obviously no — you would spend a page of expensive output
describing an edit you could have made in one call, and then pay a verification round on top.

For one root cause across forty call sites the answer is obviously yes — the doc is barely longer
than it would be for four sites, but the application it offloads is ten times bigger.

## Break-even heuristic

A rule of thumb, not a measurement — calibrate it against your own results:

| Mechanical application size | Route |
|-----------------------------|-------|
| 1–3 sites | **A**, always |
| 4–10 sites, fully mechanical | **A** — writing the doc is roughly a wash, and A has no round-trip risk |
| 10–25 sites, fully mechanical | **B** starts to pay |
| 25+ sites, fully mechanical | **B**, clearly |
| Any size, any per-site judgment | **A** — size is irrelevant |

The last row dominates every other row. A single judgment call anywhere in the application makes
the site count meaningless: the cheap executor will resolve it, differently, at every site, and
you will pay a second full diagnosis to find out how.

## Decision table

Work top to bottom; the first matching row wins.

| # | Signal | Route | Why |
|---|--------|-------|-----|
| 1 | The fix requires a design call (naming, layout, API shape, error semantics) | **A** | Judgment is exactly what the cheap tier cannot supply |
| 2 | You are not yet certain of the root cause | **A** | Never delegate an unproven hypothesis; it multiplies a wrong fix across sites |
| 3 | The fix touches a subsystem the doc never described | **A** | The executor has no grounding there and will improvise |
| 4 | The fix is security-relevant (auth, storage, network, user input, embedded web content) | **A** | Also call the Skill tool with `security-audit` over the result |
| 5 | Under ~10 near-identical sites | **A** | Doc-writing cost exceeds the application it offloads |
| 6 | 10+ near-identical sites, verbatim before/after expressible for each | **B** | One diagnosis, many mechanical edits — the case B exists for |
| 7 | A regenerated exhaustive table must be re-applied across the codebase | **B** | Table generation is programmatic; application is pure mechanics |
| 8 | A rename or signature change rippling through many files | **B** | Zero judgment per site, high volume |
| 9 | Origin is `spec-defect` | **C**, plus A or B for the code | The doc still contains the text that caused the bug |

Rows 1–5 are the common case. Expect most rounds to be entirely Route A plus some Route C.

## Why Route B needs a *tighter* doc than a spec

The cheap model already failed on this code once. Two things changed since the original spec,
both bad for you:

1. **It has partial ownership.** It is editing code it wrote, in a codebase it half-recognises,
   and it will be tempted to tidy adjacent things it now "understands".
2. **The defect proves the previous specificity was insufficient.** Whatever level of detail
   produced the bug is, by definition, not enough. Re-issuing the same instruction more firmly
   ("make sure you add the chip to *all* states this time") changes nothing.

Hence the fix doc's extra constraints: verbatim before/after per site, an exhaustive site
inventory produced by a command rather than described, a hard "change nothing else" boundary, and
a match-count assertion that mechanically proves completion. See
[fix-doc-template.md](fix-doc-template.md).

## Route C is not optional and not a substitute

`spec-defect` origin means the task doc contains text that reliably produces a bug. Two failure
modes to avoid:

- **Fixing only the code.** The doc survives. The next feature built from it — or the next
  executor re-reading it during a related task — reproduces the defect.
- **Fixing only the doc.** The bug is still in the tree.

`spec-defect` always means C **and** (A or B).

## When not to run this skill at all

- **A single obvious bug with an obvious fix.** Just fix it. Triage overhead is real.
- **The user is still testing.** Wait and batch — a second round re-pays the entire diagnosis
  context. Say this out loud rather than starting early.
- **The executor never actually ran the doc.** If the work was abandoned partway, this is not a
  bug round; it is an unfinished task. Resume the build order in the original doc instead.
- **Bugs are dense and structural** (the executor misunderstood the feature wholesale). Rewriting
  the spec section and re-running it is cheaper than triaging a long tail of downstream symptoms.
  Say so and recommend the re-run rather than triaging thirty consequences of one misreading.
