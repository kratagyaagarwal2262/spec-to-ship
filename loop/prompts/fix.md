This run is the builder in the kit's agent loop, fixing pull request #{{pr}} for ticket
#{{ticket}} on branch `{{branch}}`, unattended. Nobody will answer a question during it.

Read `docs/agents/project.md` for the commands, then fix exactly what is below.

{{reason}}

- Fix the cause, not the symptom: a test edited until it passes is a second bug.
- After the fix, run the analyzer and the tests for the files you touched, and commit with a
  message naming what was fixed. The loop pushes after you exit.
- Where a review finding is wrong, change no code for it. Write the finding and why it is wrong to
  `{{notes}}`; the loop posts it on the pull request for the reviewer and the human to see.
