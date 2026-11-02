---
name: domain-glossary
description: Build and sharpen the project's shared vocabulary in GLOSSARY.md, and record hard-to-reverse decisions as ADRs. Use when discussing project terminology, when a term is doing two jobs, or when writing or editing GLOSSARY.md or an ADR.
---

# Domain glossary

A client's domain has words we did not invent, and getting them wrong is expensive twice: once in
the code, and again in every email where we and the client mean different things by the same term.

This skill is the **active** discipline of building that vocabulary: challenging terms, stress-testing
them against edge cases, and writing them down the moment they settle. Merely reading `GLOSSARY.md`
for vocabulary is not this skill; any skill can do that in one line.

## Why it pays on client work

The glossary is the one artifact that makes the code, the tests, the specs, the client emails, and
the store copy use the same word for the same thing. Skip it and each surface invents its own:
the API says one thing, the UI label says another, the state layer's status enum a third, and a
feedback round spent arguing about a word looks exactly like a feedback round about a feature.

Terms that carry a rule are the expensive ones. A domain word that implies a price, a duration, a
window, or a state transition is a business rule wearing a noun, and it has to be written down with
the rule attached.

## File layout

```
GLOSSARY.md         the glossary, at the repo root
docs/adr/           decisions, numbered: 0001-<slug>.md
```

A root `CONTEXT.md` is this glossary under its older name: `git mv` it to `GLOSSARY.md` before the
first edit, so the project keeps one glossary.

Create both lazily. No `GLOSSARY.md` until the first term is actually resolved; no `docs/adr/` until
the first decision earns a record. An empty glossary committed on day one just becomes a file nobody
reads.

## During a session

**Challenge against the glossary.** When the user or the client uses a term that conflicts with what
`GLOSSARY.md` already says, call it out immediately. "The glossary defines a cancellation as X, but
this reads as Y. Which is it?"

**Split overloaded words.** When one word is doing two jobs, propose two words. This is the most
common and most costly case: a single term covering both a person and their login, or both a
submitted request and an accepted one, will produce a model that is wrong in a way tests cannot
catch.

**Stress-test with scenarios.** When a relationship is being described, invent the edge case that
probes its boundary. Concrete scenarios force precision that definitions alone do not.

**Cross-check against the code.** When the user states how something works, check whether the code
agrees, and surface the contradiction when it does not. A glossary that disagrees with the
implementation is worse than none, because it is trusted.

**Write it down inline.** When a term resolves, update `GLOSSARY.md` right then. Do not batch: the
precision is in the moment, and a term recorded an hour later is recorded as a paraphrase.

`GLOSSARY.md` is a glossary and nothing else. No implementation notes, no plans, no scratch. One
entry per term: the word, what it means, and the rule it carries if it carries one. Where the client
uses a different word for the same thing, record theirs as an alias so their emails still parse.

## ADRs, sparingly

Offer to record a decision only when all three hold:

1. **Hard to reverse.** Changing our mind later has a real cost.
2. **Surprising without context.** A future reader will ask why it was done this way.
3. **A real trade-off.** There were genuine alternatives and one was chosen for stated reasons.

If any is missing, skip it. On client work a fourth case earns one regardless: **a decision the
client made that we would not have.** Record it with who decided and when, because it will be
questioned later, and the record is the difference between a change request and an accusation.
