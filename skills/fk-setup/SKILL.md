---
name: fk-setup
description: Configure a repo for the engineering kit: its components and the stack kit serving each, the project config, the memory vault and the tracker. Run once per project before using the other skills.
disable-model-invocation: true
---

# Setup project

Every other skill in this kit assumes these exist: `docs/agents/project.md` (what differs between
projects, with the Components table every stack question routes through), a `CLAUDE.md` carrying
the always-on conventions with an `AGENTS.md` twin for Codex, opencode, Antigravity and Cursor, the
memory vault at `docs/vault/`, and the tracker conventions in `docs/agents/issue-tracker.md`. This
skill writes them, and hands each component to the stack kit that serves it.

The kit itself is installed once per user, not into the project. What this skill writes is the
project's own configuration, and it is the only kit-shaped thing a project carries.

Works on a freshly generated repo and on an existing project. Explore first, propose, get
confirmation, then write. Never overwrite a file the project already has without showing the diff.

## 1. Explore

Answer these from the repo. Only ask the user what you genuinely cannot observe.

- **The components.** Each folder with its own dependency manifest is one: an app, a backend, a
  database, a worker. For each, note its Kind, its Stack as the project's own docs name it, and its
  Path. Its Kit is the stack kit serving that stack, where a `<kit>-setup` skill for it is among the
  skills available to you, and `none` otherwise. A repo with no component yet is a product still to
  be built: ask the user what it is made of and in which stack, and record each row with the Path it
  will live at.
- **Is this greenfield or existing?** A component with real features and their tests means
  existing; a generator's starter code, or nothing, means greenfield.
- **Whose code is it?** `git log --reverse --format='%an %ad' | head` and the contributor list. A
  history written by people the user does not name, or one squashed import commit, suggests an
  inherited codebase. Confirm in step 2; an inherited one gets an audit before any estimate.
- **Identity.** The product name from the manifests and the README, and `git remote -v`.
- **Environments.** Gitignored env files, per-environment config, deploy scripts, and which
  backend each one points at.
- **Integrations.** Read each component's dependency manifest: crash reporting, push, remote config,
  maps, payments, sign-in providers, analytics.
- **Existing docs.** `CLAUDE.md`, `AGENTS.md`, `GLOSSARY.md`, `docs/`, a release checklist, CI
  workflows.

Done when every component has a row with Component, Kind, Stack, Kit and Path filled, and every
other section of the template is filled or marked as a question for step 2.

## 2. Propose

Show the user a filled-in draft of `docs/agents/project.md` using
[project.md](template/docs/agents/project.md) as the shape, with everything exploration settled
already filled and only the genuine unknowns marked. Show the Components table and ask the user to
correct it, rather than asking row by row. Then ask, one question at a time, in this order. Lead
each with your recommended answer so it can be accepted in a word.

1. **Whose code is this**, on an existing repo: the user's own, or inherited from someone else.
   Lead with what the history suggested.
2. **Safe environment for verification.** Which environment is safe to drive without creating real
   data. If the product talks to one live backend, say so plainly: verification stops short of
   real flows until a staging environment exists.
3. **Design source**, where a component has a user interface: Figma MCP server, pasted CSS plus
   screenshot, screens drawn by the kit in `docs/vault/screens/` (the default where no designer
   supplies frames), or written spec only.
4. **Issue tracker.** Recommend GitHub Issues when the remote is on GitHub and `gh auth status`
   succeeds: tickets, sprints and parallel agents all depend on it. Otherwise `none`, which keeps the
   backlog in the vault. Where the team already runs Linear or Jira, record it in `project.md` and
   use `none` for the kit's own tracking, since `project-tracker` speaks only GitHub. With GitHub,
   also ask the sprint length (recommend one week) and whether to create a project board.
5. **Test account.** Whether a credential exists for driving flows behind sign-in, and where it
   lives. Never write the credential itself into any file; record where it is kept.

Skip any question exploration already answered. Done when the user has confirmed the Components
table and every question has an answer or a recorded "not yet".

## 3. Write

Write, showing each for approval first:

- **`docs/agents/project.md`** from the confirmed draft, its Components table under the
  `Contract: 1` line exactly as the template has it. Commands a stack kit will fill stay marked
  until step 4.
- **`CLAUDE.md`** from [CLAUDE.md](template/CLAUDE.md), with the identity filled in. If a
  `CLAUDE.md` already exists, merge rather than replace: keep everything the project added, add the
  kit's sections that are missing, and show the diff.
- **`AGENTS.md`** from [AGENTS.md](template/AGENTS.md), filled in the same way and kept in
  sync with `CLAUDE.md`. Codex, opencode, Antigravity and Cursor read this file where Claude Code
  reads `CLAUDE.md`. If an `AGENTS.md` already exists, merge rather than replace, as with
  `CLAUDE.md`.
- **`docs/specs/.gitkeep`**, `docs/client/.gitkeep`, `docs/adr/.gitkeep` for whichever the answers
  above put in play.
- **`docs/vault/index.md`** and **`docs/vault/memory.md`** from [template/docs/vault/](template/docs/vault/),
  with the product name and today's date filled in. Create no other vault note: each is written by
  the skill that owns it, when it has something to say. Where a vault already exists, leave it.
- **`.gitattributes`** gains two lines, so agents on parallel branches merge their memory rather
  than conflict on it:

  ```
  docs/vault/memory.md merge=union
  docs/vault/index.md merge=union
  ```

- **With GitHub as the tracker**, `docs/agents/issue-tracker.md` from
  [issue-tracker.md](template/docs/agents/issue-tracker.md) with the repo, board and sprint answers
  filled in. Then call the Skill tool with `project-tracker` to set up the labels and, if the user
  wanted one, the board.

Hooks are not this skill's job: the user-level install wires them for every harness. Where the
user reports that formatting or the secret scan is not running, tell them to run `kit doctor`.

Do not write a `GLOSSARY.md`. That is `domain-glossary`'s job, and it should be created lazily when
the first term is actually resolved. The same holds for `docs/agents/design.md`: `project-stack`'s
`design` slot writes it once there is a settled product to design against, so leave the Design
language row pointing at it and unfilled here.

Done when every file above is written or its skip is named.

## 4. Configure each component

For each component, call the Skill tool with `project-stack` for its `setup` slot, passing the
component. A stack kit's setup proposes and writes its own share: the component's commands in the
Components table, its own section of `docs/agents/project.md`, its own section of `CLAUDE.md` and
`AGENTS.md`, its rules files, and the scaffold on a greenfield repo. Where no kit serves the
component, fill its Install, Check, Test, Run and Build from the repo yourself: its manifest's
scripts, a Makefile, the README, an existing CI workflow. Ask the user only for a command none of
them shows.

Done when every row has all ten columns filled, or a command is marked unknown with the question
that settles it.

## 5. Record the test baseline

Run each component's Check and Test commands, and record in the Verification section every test
that fails on this clean checkout, per component, before the project accumulates agent-authored
code on top of it.

Done when every component has a recorded baseline, `none` included.

## 6. Hand off

Tell the user what was written, then call the Skill tool with `next-step`, handing off the next
step for what the project is:

- **Greenfield** → tell them to run `/fk-plan`. It writes the proposal, the design language and the
  backlog, starting with a questionnaire for the client where there is no brief yet.
- **The user's own existing app** → the skills now read `docs/agents/project.md`. Mention that
  `verify` will report the test baseline recorded in step 5, so a pre-existing failure is
  never mistaken for new breakage. Where a client component already has screens, its design
  language exists in practice but nowhere in writing; call the Skill tool with `project-stack` for
  that component's `design` slot to recover it into `docs/agents/design.md` before the next screen
  adds to the drift. Then tell them to run `/fk-plan` for the next phase of work, or `/fk-build`
  for a single change.
- **An inherited app** → call the Skill tool with `takeover-audit` before anything else. An
  estimate given before the audit is a guess about code nobody here has run. Then tell them to run
  `/fk-plan`, which builds the proposal on the audit's findings.

Where exploration found integrations whose keys a human has to fetch by hand, call the Skill tool
with `setup-wizard`.

Where the repo still carries a copy of the kit from an older version (kit skills under
`.opencode/skills/`, `.cursor/skills/` or `.claude/skills/`), tell the user to run
`kit clean-project <path>`, which removes the kit's files and keeps the project's own. Two copies
offer every skill twice.
