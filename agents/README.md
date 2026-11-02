# Agents

Specialists the skills delegate to. Each owns one document or one kind of judgement, so a skill can
fan out without any single agent holding the whole project in context.

These files are the source. `scripts/kit.py` converts them for each harness at install time
(TOML for Codex, opencode and Cursor frontmatter), so edit here and re-run `kit install`. Never
edit an installed copy.

## Models

The `model:` line in each file is Claude Code's default and nothing more. Which model an agent
really runs on is the user's choice: `install/roles.json` puts every agent in a role (explore,
build, judge, qa) and says what that role needs, the `configure-models` skill picks a model per
role in each harness the user has, and `kit install` pins it. Without that step, agents outside
Claude Code inherit the session's model.

Spec-to-Ship's agents name no stack. Layer engineers come from the stack kit installed beside it.

| Agent | Owns | Model |
|-------|------|-------|
| `codebase-explorer` | Read-only search: where things are, what already exists | `haiku` |
| `solution-architect` | Design decisions, planning tables, hard root-cause work | `opus` |
| `qa-engineer` | Tests a sprint's merged build against every ticket's criteria, files each failure as a bug | `sonnet` |

`solution-architect` holds no procedure of its own: it calls `plan-change`, `diagnose-bug` or
`engineering-principles`, so the method has one home and the agent is the context it runs in.

`/fk-sprint qa` sends `qa-engineer` the commit a client is about to receive. Each builder proved its
own ticket on its own branch; this agent tests them together, which is where tickets that passed
alone break each other. It runs the build and files bugs, and never edits source.

Reach for `codebase-explorer` for discovery, and `solution-architect` for judgement before any code
generation. Both pay for themselves by keeping the parent's context clear.
