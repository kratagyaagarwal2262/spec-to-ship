---
name: merge-conflicts
description: Resolve merge and rebase conflicts by intent, including the generated files and lockfiles that must be regenerated rather than merged. Use when a merge or rebase conflicts, or when resolving conflicts in a generated file, a lockfile, a barrel or registry file, or a snapshot image.
---

# Merge conflicts

Resolve by **intent**: what was each side trying to do. A conflict resolved by picking whichever
hunk looks tidier produces code that compiles and does neither thing.

Work hunk by hunk. Never `--abort` to escape a hard conflict: the work does not get easier later,
and aborting loses the resolution decisions already made.

## 1. Sort the conflicts by kind first

Learn which files in this repo are generated, which are lockfiles, and what rewrites each: call the
Skill tool with `project-stack`, asking for the `conventions` of each component with a conflict,
aspect "generated files and lockfiles". It returns the file patterns and the commands.

Repos conflict in five distinct ways, and four of them are not merges at all:

| Conflicted file | How to resolve |
|---|---|
| Generated output: codegen, mocks, compiled assets | **Regenerate**, never merge |
| A lockfile | **Regenerate** from the resolved manifest |
| A file a tool owns: an IDE project file, a platform build registry | Take one side, then re-add the other's changes through that tool |
| A snapshot or golden image | Take one side, then re-run the test that writes it and review the diff |
| Ordinary source | Merge by intent, below |

Doing the mechanical ones first shrinks the real work, and often removes conflicts that only looked
like conflicts.

### Generated files

```bash
git checkout --ours <conflicted generated file>   # either side; it is about to be overwritten
<the component's codegen command>
```

Resolve the **source** file first, then regenerate. A hand-merged generated file is wrong the moment
anyone runs codegen, and reviewing one is wasted effort.

### Lockfiles

Resolve the **manifest** by intent first, taking both sides' dependency additions unless they
genuinely conflict on a version. Then run the component's Install command and let the package
manager write the lock.

## 2. The file every branch appends to

A file that every new piece of code adds a line to (a single export barrel, a route table, a
dependency registry) conflicts on **every** parallel feature branch. It has a fixed recipe:

**Take both sides.** Those lines are additive; two branches adding different entries are not in
conflict, they only touched adjacent lines. Keep every line from both, then restore the file's own
ordering within each section.

Then run the component's Check command: an entry lost in the merge shows up as an unresolved symbol.

The failure to avoid is resolving with `--ours` and silently dropping the other branch's entries.
The Check command catches it, which is why it runs immediately after.

## 3. Ordinary source, resolved by intent

For each hunk, establish what each side wanted before writing anything:

```bash
git log --merge -p -- <path>    # the commits from both sides touching this file
git log --oneline HEAD..MERGE_HEAD -- <path>
```

Read the commit messages. Where a side's intent is still unclear, read the spec or the issue it
references rather than inferring from the diff.

Then, in order of how often it applies:

- **Both changes belong** and touch different things. Keep both.
- **Both changed the same behaviour** differently. This is a real decision, not a merge: pick one,
  say why, and tell whoever wrote the other side.
- **One side deleted what the other edited.** Deletion usually wins, since it was deliberate, but
  confirm the edit was not the reason to keep it.
- **A rename against an edit.** Take the rename, then reapply the edit to the new name. Git often
  cannot see this, and it surfaces as a whole file conflicting.

## 4. Verify, do not assume

A resolved merge compiles far more easily than it is correct, because both sides individually
compiled.

Run the Check and Test commands of every component the merge touched, from the Components table in
`docs/agents/project.md`.

Then, specifically: run the tests **from both sides** of the merge. A conflict resolved by dropping
one side's logic leaves that side's tests failing, and that is the fastest signal that intent was
lost. Where either side changed a screen, call the Skill tool with `verify` and reach a UI or
screenshot rung rather than trusting static analysis.

## Completion criteria

Every conflicted file is resolved, generated files and lockfiles are regenerated rather than merged,
every touched component's Check is clean, and the suites from **both** sides pass.

Name every hunk where you chose one side's behaviour over the other, and why. That list is what the
other author needs to see, and it is the part a silent resolution loses.
