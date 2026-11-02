# Changelog

What changed in each Spec-to-Ship version, and what a project or an install has to do about it. A
**Migration** line means something you already have stops working until you act on it.

## 1.0.0

First release: the stack-free half of what used to be one large kit.

- Eight commands: `/fk-setup`, `/fk-plan`, `/fk-sprint`, `/fk-build`, `/fk-feedback`, `/fk-change`, `/fk-release` and `/retro`, plus `/ask-kit` to say which comes next.
- Project delivery: proposal, feature list, drawn screens, backlog in GitHub Issues, flow-sized sprints, QA gate, feedback sorting, memory vault and `prune-context`.
- The agent loop (`kit loop run`): builder and reviewer agents drive a sprint's tickets to ready-for-human pull requests on models the user chooses.
- Stack-free by check: no skill or agent names a stack. `project-stack` reaches one through a stack kit's slot skills when installed, and falls back to each component's commands.
- One hook, a prompt-time secrets guard, with an opencode plugin equivalent.
- Installs once per user for Claude Code, Codex, opencode, Antigravity and Cursor.

**Migration:** none. This is the first release.
