---
name: explain
description: Explain how a feature, subsystem or codebase actually works, and why it was built that way. Use when asked how something works, where something lives, why a decision was made, or when onboarding onto unfamiliar code.
---

# Explain

Answer "how does this work" from the code, at whichever zoom level the question is asked. Most of
the reading should happen in a subagent: dispatch `codebase-explorer` for the sweeps and keep the
synthesis here, so the answer is written in a clean window rather than one full of file dumps.

Explain what the code **does**, not what it should do. Where you find a bug while reading, say so
separately at the end rather than describing the intended behaviour as if it were real.

## Pick the zoom level

| The question | Scope |
|---|---|
| "How does sign-in work?" | One feature: its state layer, repo, view, and the route in |
| "How do we talk to the API?" | One subsystem across features |
| "What is this codebase?" | Whole repo: the features, the shared core, the conventions |
| "Why is it done this way?" | Archaeology, below |

Ask which one only when the request is genuinely ambiguous. Most questions name their own scope.

## The shape of an answer

Five headings, in this order, because it is the order a reader needs them:

**Overview.** Two or three sentences. What this does and who triggers it.

**Key concepts.** The nouns a reader needs before the rest makes sense, including any term this
codebase uses differently from its usual meaning. Where `GLOSSARY.md` exists, use its vocabulary
rather than inventing a parallel one.

**How it works.** The path through the code for the main case, as a numbered sequence with
`file:line` references. One path, the common one. Branches go under gotchas.

**Where things live.** A short table of file to responsibility, so the reader can navigate after the
explanation ends.

**Gotchas.** What would surprise someone changing this: the implicit ordering, the retry that hides
failures, the state that survives navigation, the special case for one platform. This section is
the reason the explanation is worth more than reading the code, so do not pad it and do not skip it.

## Whole-repo scope

For "what is this codebase", add a survey of what is decaying, since that is what the reader will
hit next:

- Features far larger than their neighbours, and what they have absorbed
- A state layer with more actions than the screen has affordances
- Cross-feature imports, which mark a boundary in the wrong place
- Near-duplicate data-access methods
- Screen code long enough that nobody reads to the bottom

Report these as observations with locations, not as a plan. Where the user wants one addressed, call
the Skill tool with `plan-change`, which owns designing the fix. A survey that turns itself
into a refactor is how a question becomes an unreviewed rewrite.

## Archaeology, for "why"

The code says what. Git says why:

```bash
git log --follow -p -- <path>       # how this file got here
git log -S '<symbol>' --oneline     # when a symbol appeared or vanished
git blame -w -- <path>              # who last touched each line, ignoring reformatting
```

Read the commit messages and the PR bodies they reference, and check `docs/adr/` before concluding
anything: a decision recorded there beats a reconstruction from commit order.

Where the history does not say, say that. An invented rationale is worse than an unexplained
decision, because it gets quoted back later as fact.

## Completion criteria

Every claim about behaviour cites `file:line`, the gotchas section names at least what surprised you
while reading, and anything you could not determine is listed as unknown rather than smoothed over.

Where the reader's next step is a change, name the skill for it rather than starting it.
