# CLAUDE.md — Spec-to-Ship

This repo is a Claude Code plugin, not an app. Its product is the skills under `skills/`, the agents
under `agents/`, and the project templates the setup skills write.

## Where it sits

Spec-to-Ship runs a product and its engineering for **any stack**: proposal, features, sprints, change,
feedback, and the method skills (plan-change, tdd, verify, code-review, security-audit,
diagnose-bug). **It names no stack.** It reaches a stack only by calling `project-stack`, which reads
the project's Components table and calls a stack kit's slot skills (`<kit>-setup`, `-conventions`,
`-design`, `-build`, `-verify`, `-release`) when they are installed, and falls back to each
component's commands when they are not. Flutterbase is the Flutter + Supabase stack kit; it never calls
a Spec-to-Ship skill. `validate-kit.py` check 23 fails on a stack named anywhere in a skill or agent.

## Before editing any skill

Call the Skill tool with `writing-for-agents`. It is the standard this repo holds itself to:
invocation choice, composition by tool call, single source of truth, completion criteria, pruning.

## The portability rule

**No client or project name appears anywhere in this repo.** The kit is written *from* real
projects, but a skill that names one stops being portable. `scripts/validate-kit.py` check 8
enforces this. The terms it scans for are client data, so they live in the gitignored
`.kit-private/{client-names,project-symbols}.txt`, never in a tracked file; add a line there when a
new client starts. A checkout without that directory configures zero terms and the check passes.

The same applies to a client's **domain vocabulary**, which leaks more quietly than the name. Use
neutral examples. **A project fact never goes in a skill:** if it is true of one project but not of
every project, it belongs in that project's `docs/agents/project.md`, and the skill reads it there.

## Repo invariants

- Every `skills/<name>/SKILL.md` has `name:` exactly equal to its directory name.
- Every skill is registered in `.claude-plugin/plugin.json`'s `skills` array.
- An **invocation** is always an instruction to call the Skill tool with the name, never a link to
  `../other/SKILL.md` and never a bare `/name`.
- **Reading** a reference file owned by another skill may cross folders, but only when that skill is
  user-invoked and therefore cannot be called at all (`triage-executor-bugs` links into
  `spec-for-cheap-executor/references/`). Anywhere the owner is model-invoked, call it instead.
- The command surface is fixed: `ask-kit`, the seven `fk-` commands, `retro`, and the tools
  `handoff`, `unslop` and `spec-for-cheap-executor`. Check 19 holds the list.
- Nothing calls a user-invoked skill. `ask-kit` routes every user-invoked skill.
- `README.md`'s Reference lists every skill, with the bullet text equal to the frontmatter
  description minus its trailing trigger sentence. Check 9 compares them.
- `fk-setup/template/AGENTS.md` twins its `CLAUDE.md`. Both carry the same sections.
- A skill carries every file it reads, inside its own folder. Nothing links out to `../../`.
- Every user-invoked skill stays human-started in every harness that can enforce it. `scripts/kit.py`
  derives the Codex policy and the opencode gate from the frontmatter; never hand-write them.
- The delivery skills (`project-memory`, `project-tracker`, `project-proposal`, `project-backlog`)
  name no framework and call no engineering skill. Check 20 holds this.
- No skill or loop prompt names a model. `install/roles.json` says what each kind of work needs;
  `configure-models` chooses models with the user, and `kit install` pins them. Checks 21 and 22.
- Every command ends by calling `next-step`. Check 24 holds this and runs `tests/screens_test.py`.
- A skill writes a file only when a later session, agent, script or the client reads it, and reads
  a file only at the step that uses it. `writing-for-agents` owns the rule.
- Run `claude plugin validate . --strict` after touching either manifest.

Run `python3 scripts/validate-kit.py` before committing.

## Installing

The kit installs once per user, never into a project. `scripts/kit.py` is the installer: Claude Code
gets the managed plugin; Codex, opencode, Antigravity and Cursor get the skills linked from a
generated build under `~/.spec-to-ship/build`, plus agents, commands and hooks converted to the shape
each one reads. `install/harnesses.json` is the one list of harnesses and their paths.

Generated files are never edited by hand: change the source here and re-run `kit install`.
`hooks/spec-to-ship-hook.py` is the one hook for every command-hook harness; `opencode/plugins/spec-to-ship.ts`
is its opencode equivalent. The root `install.sh` downloads a pinned tarball and delegates to
`scripts/kit.py`. It carries no kit content itself, so keep it that way.

## Models and the loop

`~/.spec-to-ship/models.json` is the user's, written by `kit models set` after the `configure-models`
skill proposes it and the user approves. `scripts/kitloop.py` is `kit loop`: a script, not an agent,
that runs each role as a short headless process through the `headless` template in
`install/harnesses.json`. Keep its next-step rule in `decide()`, which is pure, so check 22 can test
every branch. A headless template stays `verified: false` until it has been run against that CLI.

## Versioning

Bump `version` in `.claude-plugin/plugin.json` when skill behaviour changes, and set
`FALLBACK_VERSION` in `install.sh` to match in the same commit (check 15 holds this). Add the
CHANGELOG entry, with a **Migration** line for anything a project set up earlier must do.

A release is a `vX.Y.Z` tag. `install.sh` and `kit update` install the highest tag. Claude Code users
get the plugin from `main` directly, so `main` takes only release-ready merges.
