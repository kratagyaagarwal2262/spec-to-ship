---
name: pr
description: Shape a pull request body for fast human review: the smallest visual that shows the change, before-and-after evidence that it works, and how dangerous it is to merge. Use when opening a pull request, writing or updating a PR description, or summarising a branch for someone to review and merge.
---

# Pull request

The reader is the person who decides whether to merge, often between other things. Write for the
thirty seconds they will give it before choosing to read the diff or not. Use the project's words
from `GLOSSARY.md`, and skip any preamble.

Keep the body to what fits those thirty seconds. Full logs, run tables and file-by-file notes go in
a linked artifact or a collapsed `<details>` block, never inline.

## The body

```markdown
## Summary

<the smallest visual that makes the change clear>

## Scope

<what this covers, and what it deliberately leaves out>

## Evidence

**Before:** <screenshot / golden / failing test / output>
**After:** <screenshot / golden / passing test / output>

<verification rung reached, and what is not proven>

## Merge danger

**Door:** <one-way or two-way>
**Blast radius:** <one or two words>

<only if needed: what could break, and for whom>
```

## Summary

Pick the one view that answers "what changed", and add a second only if the first leaves a real
question open.

- **A screen or UI component change** → the component tree, marking what is new and where state is
  read:

  ```diff
   SettingsPage
     <state layer> → SettingsState
     ProfileTile
  +  NotificationToggle      (new, reads SettingsState.notifications)
     SignOutButton
  ```

- **Behaviour in the state layer** → the status transitions, as pseudocode:

  ```text
  on NotificationsToggled
    if permission denied → failure(permissionDenied)
    else                 → success(enabled: !enabled)
  ```

- **A flow across screens or services** → a call tree, or a Mermaid sequence diagram when more than
  two parts talk to each other.
- **A refactor or a moved feature** → a shallow file tree as a `diff`, so the move reads at a glance.

Keep only the components, files, states and calls the reader needs. Leave out everything else,
however true.

## Scope

One to three short items: what the PR covers, and what it deliberately leaves out, such as a
follow-up, a known gap, or a criterion deferred to another ticket. Without it, the reviewer cannot
tell an omission from an oversight, and asks.

## Evidence

Show it working, as a before and an after. Ranked by how much they prove:

1. **Pixels**: a screenshot or golden image, before and after. The best evidence for any visual
   change; a golden diff a reviewer can see beats a sentence describing it.
2. **Execution**: the test that failed before and passes after, named, with its exact command and
   the counts. For a bug fix, the same command twice: red, then green.
3. **Static**: the Check command clean. True of every PR, so it is never the evidence on its own.

Then the rung. Call the Skill tool with `verify` if no rung was reported yet, and copy its
two lines: the rung reached for each acceptance criterion, and what is **not** proven. A PR that
hides a gap gets merged with it.

## Merge danger

**Door.** A two-way door can be walked back by reverting. A one-way door cannot. The one-way doors
are:

- A change to **stored data on the device**: a local database schema, a stored-preference key, a
  secure-storage key. Users who update carry the old shape forward.
- A change to a **contract someone else holds**: an API request shape, a deep-link path, a push
  payload, an analytics event name.
- Anything that **ships to a store**. A released binary stays on phones until users update, so a
  revert on `main` does not reach them.
- Identity: the bundle id, application id or signing key.

Everything else is two-way. Say which, and for a one-way door, say what the rollback plan is.

**Blast radius.** Name what it can touch: one screen, a shared component, one platform, a minimum OS
version, every user on startup. A change to the app's entry point, routing or a core component has a
wider radius than its diff suggests; say so.

## Completion criteria

The summary has one visual, the scope names what is left out (or says nothing is), the evidence
shows a before and an after with the rung named, and the door and blast radius are both stated.
Where one of them cannot be stated yet, the PR is not ready to be marked ready for review.
