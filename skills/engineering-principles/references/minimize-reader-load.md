# Minimize reader load

Code is read far more often than it is written, and most of that reading is someone answering one
narrow question under time pressure. Optimise for how many hops that answer takes.

This is about **code**. Prose has its own standards: `writing-for-agents` for documents an agent
reads, `unslop` for anything a human reads.

## The measure

Pick a question a maintainer will actually ask, then count the files they must open to answer it.

*"What happens when this request fails?"* If the answer is: open the screen, follow to the
controller, follow to a wrapper, follow to the repository, follow to the client, then the depth is
five and one of those layers is probably doing nothing.

## Collapse a layer that only forwards

A function with one caller that only renames its arguments is a hop with no answer in it:

```
// Two hops to learn there is no logic here
getUser(id) -> User or nothing  =  repository.fetchUser(id)
```

Inline it. The exception is a layer that exists to be substituted in a test or to hold a boundary,
which is doing real work even when it looks like forwarding.

## Put the answer where the question is asked

Layout code reading top to bottom as the screen reads top to bottom is answerable in one pass. The
same tree with its middle third in a private component three files away is not, even though both
are the same code.

Extract a component when it is **reused**, when it needs its own state, or when it should re-render
independently. Extracting purely to shorten a function moves the load rather than reducing it.

## Name the thing, not the shape

| Costs a hop | Answers in place |
|---|---|
| `data`, `item`, `temp`, `result` | `pendingOrders`, `selectedAddress` |
| `flag`, `status2`, `isOk` | `hasUnsavedChanges`, `isAwaitingConfirmation` |
| `handleTap` | `onConfirmDelete` |
| A list of untyped key-value maps | A named model type |

The last is the expensive one: a bare map forces the reader to find a producer to learn the fields,
and the compiler cannot help them.

## Make the shape carry the rule

Where an invariant is written in a comment or checked at runtime, see whether a type could state it
instead. That is [model-the-domain.md](model-the-domain.md), and it is the strongest form of this
principle: a rule in a type needs no reading at all, because the code that breaks it does not
compile.

## Two hard cases

**A clever one-liner.** A chain of `fold`, `filter` and `flatMap` that took an hour to write takes an
hour to read. Where the loop is clearer, write the loop.

**A deep layout.** Ten levels of nesting is genuinely hard to read, and so is that tree scattered
over eight files. Break on the seams the design has, meaning header, list, footer, rather than on
line count.
