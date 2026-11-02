{{invoke}}

This run is the builder in the kit's agent loop, working unattended in a git worktree on branch
`{{branch}}`. Nobody will answer a question during it.

- Where the ticket leaves a decision open, take the most conservative reading that satisfies its
  criteria, and list each one under **Assumptions** in the pull request body.
- Commit once `/fk-build`'s gates pass. The loop pushes the branch and opens the pull request after
  you exit, so leave both to it.
- Write the pull request body, in the shape the `pr` skill gives, to `{{pr_body}}`. It ends with
  `Closes #{{ticket}}`.
- Where the ticket cannot be built as written (criteria missing, or a decision only a person can
  make), commit nothing and write `BLOCKED:` and the reason as the first line of `{{pr_body}}`.
