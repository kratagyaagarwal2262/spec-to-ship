---
name: code-review
description: Review changes on two independent axes: does the code follow the project's conventions and its stack's review baseline, and does it do what the spec asked. Use when the user wants a branch, PR, or work-in-progress reviewed, or asks to review since a commit or branch.
---

# Code review

Two axes over the same diff, run as **parallel sub-agents** so neither contaminates the other, then
reported side by side:

- **Conventions** — does the code follow this project's documented rules?
- **Spec** — does the code do what the acceptance criteria asked for?

A change can pass one and fail the other. Code that follows every convention and builds the wrong
thing is a **conventions pass, spec fail**, and it is the failure mode that costs a client project a
whole round. Reporting the axes separately is what stops one masking the other.

## 1. Pin the fixed point

Whatever the user names: a commit, a branch, a tag, `main`, `HEAD~5`. Ask if they did not say.

```bash
git rev-parse <fixed-point>            # confirm it resolves
git diff <fixed-point>...HEAD          # three-dot: against the merge base
git log <fixed-point>..HEAD --oneline
```

Confirm the ref resolves and the diff is non-empty **before** spawning anything. A bad ref should
fail here, not inside two sub-agents.

## 2. Find the spec

In order: a spec file under the directory `docs/agents/project.md` names, matching the branch or
feature; an issue referenced in the commit messages; a path the user passed. If nothing turns up,
ask. If the user says there is no spec, run the conventions axis alone and report the spec axis as
"no spec available" — never silently drop it, because a change with no written criteria is itself
worth surfacing on client work.

## 3. Gather the convention sources

Read what the project documents: `CLAUDE.md` or `AGENTS.md`, the path-scoped rules under
`.claude/rules/`, `docs/agents/coding-standards.md` (the judgement calls this project asks its
reviewer to enforce), and `GLOSSARY.md` for vocabulary. Those always win.

Then call the Skill tool with `project-stack` for the `conventions` slot of each component the diff
touches, asking for what a review checks. What comes back is the **stack baseline**: the stack's own
review items, each with a file that shows the convention. Where no stack kit answered, the stack
baseline is the shape `project-stack` reports from an existing module and its tests.

On top of whatever the project documents, the conventions axis always carries three baselines: the
**stack baseline**, the **general baseline** and the **general smells** below. Two rules bind all
three: a documented project rule **overrides** a baseline wherever they disagree, and every baseline
item is a **judgement call**, flagged as "possible", never as a violation. Skip anything the
component's Check command already enforces: a linter finding is not a review finding.

This step is done when you hold the documented rule files and a stack baseline for every component
the diff touches.

### The general baseline

Each reads *what it is* → *why it matters here*.

- **Business logic in the view layer.** Computation, formatting, or branching in rendering code that
  belongs in the state layer or a model. → Untestable without rendering the screen.
- **Presentation in the state layer.** Navigation, dialogs, or a handle on the UI tree held by state
  code. → Couples state to presentation and breaks its tests.
- **Inline literals.** A hex colour, a user-facing string, an asset path, or a magic number written
  at the point of use. → The reason a rebrand or a copy change becomes a hunt.
- **An untyped value, or an unchecked cast off a parsed payload.** → Moves a parse failure from the
  boundary to a random later moment.
- **A data-access method that swallows an error into a bare `null`** where the project's convention
  returns a typed failure. → The UI cannot tell "empty" from "broken".
- **Missing state coverage.** A status whose loading, failure, or empty case has no branch in the
  UI. → The single most common source of a feedback round.
- **A second source of truth for one screen's state**, held locally where the project's state layer
  already owns it. → The two disagree, and the screen shows whichever wrote last.
- **A teardown that does not release** a subscription, controller, or timer it created. → Leaks.
- **A new file outside the project's import convention**, or one not exported where the project's
  module index requires it. → Compiles locally, breaks the next importer.
- **A fixture or placeholder marker left in code the change presents as finished**, where the
  project treats those markers as a temporary state. → Ships a stub as a feature.
- **A second writer, a second way, or a second list.** The change writes state another place already
  writes, adds a way to do a task the code already does, or adds a list that must be kept in step
  with an existing one by hand. → The next agent copies whichever it finds first, and they drift.
- **A test that cannot fail.** It would still pass if every function it calls returned `null`: only
  an existence or call-count check, an expected value computed by the code under test, or a restated
  constant. → Costs CI time and catches nothing.

### General smells

Fowler's (*Refactoring*, ch. 3), for the shape of any code. Each reads *what it is* → *the fix*.

- **Mysterious name.** A name that does not say what the thing does or holds. → Rename it; if no
  honest name comes, the design is murky.
- **Duplicated code.** The same logic shape in more than one hunk or file of the change. → Extract
  it and call it from both.
- **Feature envy.** A method that reads another object's data more than its own. → Move it onto the
  data it envies.
- **Data clumps.** The same few fields or parameters always travelling together. → One small type.
- **Primitive obsession.** A `String` or `int` standing in for a domain concept. → Give the concept
  its own type.
- **Repeated switches.** The same `switch` or `if` cascade on the same type in several places. → One
  sealed hierarchy, or one map both sites share.
- **Shotgun surgery.** One logical change forcing scattered edits across many files. → Gather what
  changes together.
- **Divergent change.** One file edited for several unrelated reasons. → Split it.
- **Speculative generality.** Parameters, hooks or abstractions the spec does not need. → Inline them
  until a real need shows.
- **Message chains.** `a.b.c.d` navigation the caller should not depend on. → One method on the
  first object.
- **Middle man.** A class that mostly delegates onward. → Call the real target.

## 4. Spawn both axes in parallel

**Conventions sub-agent.** Give it the diff command, the commit list, the project's documented rule
files, and **all three baselines pasted in full** — it has no other access to them. Brief: report,
per file or hunk, every place the diff breaks a documented rule, citing the rule and where it is
written; then every baseline item you spot, named and quoted. Distinguish documented-rule breaches
from baseline judgement calls, and note that a documented rule overrides the baseline. Skip anything
the component's Check command catches. Under 400 words.

**Spec sub-agent.** Give it the diff command, the commit list, and the spec's contents. Brief:
report (a) criteria that are missing or only partly built; (b) behaviour in the diff nobody asked
for; (c) criteria that look implemented but look wrong. Quote the criterion for every finding. Pay
particular attention to criteria naming loading, empty, or failure states, since those are the ones
most often dropped. Under 400 words.

## 5. Aggregate

Present both under `## Conventions` and `## Spec`, verbatim or lightly cleaned. **Do not merge or
rerank across axes** — that is exactly the collapse the separation prevents.

Close with one line per axis: how many findings, and the worst one within that axis. No single
overall verdict, and no "looks good overall" that averages a spec failure away.

If the spec axis found anything under (b), scope creep, say so plainly and separately. On fixed-scope
work, unrequested behaviour is a cost even when the code is good.
