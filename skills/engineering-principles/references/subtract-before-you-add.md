# Subtract before you add

Before adding a thing, look for the thing it replaces. Adding is safe and removing feels risky, so
codebases accumulate: two ways to show a dialog, three button components, a helper nobody calls.
Each one was a reasonable addition, and together they are the reason a small change now takes a day.

## Ask this first

**What does this replace?** A change that adds and removes nothing is worth a second look. Sometimes
genuinely new behaviour is genuinely additive. Often the new thing is the fourth version of
something, and the honest change is to extend one of the three.

## What to look for before adding

| Adding | Look for |
|---|---|
| A UI component | Whatever the shared component library already has doing nearly this |
| A constant | A design token or shared constant with the same value under another name |
| A helper | The util that does 80% of it, which could take one parameter |
| A failure case | An existing case the UI already distinguishes |
| A state field | A field derivable from the ones present, which should be a getter |
| A package | The dependency already in the manifest that covers it |

The last one matters most, because a package is the hardest thing to remove later.

## Then actually remove it

Migrating callers and leaving the old thing in place is not subtraction. It is the same problem plus
a second way to do it, and now the codebase teaches both. Migrate the callers and delete the old
API **in the same change**, so there is never a window where both are correct.

Where the old thing cannot go yet, say why and what has to happen first. A deprecation with no named
condition for removal does not get removed.

## Deleting is part of the job

Dead code is not free. It shows up in searches, it gets read during reviews, it gets updated by
refactors that did not need to touch it, and it makes the next reader wonder what they are missing.

- An unused private component, helper or constant goes.
- A commented-out block goes. Version control already has it.
- A feature flag whose rollout finished goes, along with the branch it guarded.
- A test asserting behaviour that was deliberately removed goes.

Markers the project's conventions sanction, such as those fencing fixture data, are not dead code.
They stay until the API they stand in for arrives.

## Where this fights another principle

Reader load sometimes wants a wrapper that subtraction would call redundant. Deduplication sometimes
wants an abstraction over two things that only look alike. Both tensions are real; resolve them by
asking which version the next reader can change safely, not which has fewer lines.
