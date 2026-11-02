# Composing with this project's skills, rules and hooks

The generated doc must **name** the project's existing machinery so the cheap executor inherits
the project's conventions instead of re-deriving them. Naming a skill is a one-line instruction
that replaces two pages of restated convention — and it stays correct when the convention changes.

Skills reach only an executor running with the kit installed. Where it has no kit, cite only what
lives in the repo it works on, meaning `CLAUDE.md`, the rule files and the commands in
`docs/agents/project.md`, and let §11 carry the rest.

Three ways to cite, in order of preference:

1. **Invoke** — "Call the Skill tool with `security-audit` at step 7."
2. **Delegate** — "Step 3: call the Skill tool with `project-stack`, asking for the `app`
   component's `build` slot, and pass §1, §3 and §11 verbatim as the brief."
3. **Defer** — "`.claude/rules/{rule}.md` governs the state shape here; follow it."

Cite the path. Pasting a skill's or a rule's contents into the doc forks it: the copy stops tracking
the original the moment either changes.

## Stack knowledge goes through `project-stack`

The doc never names a stack kit's own skills or agents. It names `project-stack` and the slot it
needs, and `project-stack` calls whichever stack kit the executor has installed, or answers from the
component's row in the Components table where it has none. The same doc line is then right for any
executor with the kit, whatever stack kit sits beside it.

Name the component in every line: `app`, `backend`, whatever the Components table calls it. A slot
asked without a component makes the executor guess which one.

## Skills — instruct the executor to call the Skill tool

Write the instruction as a Skill tool call with the skill named, one call per line. A bare `/name`
dropped into prose reads as a label, and the executor will treat it as one.

| Cite | When the task involves | Typical doc line |
|-------|-------------------------------|------------------|
| `project-stack`, `conventions` slot | Writing code in a component: its layers, imports, shared constants, dialogs, generated files, test tools | "Before step 3, call the Skill tool with `project-stack`, asking for the `app` component's `conventions` on its state layer and its test tools." |
| `project-stack`, `build` slot | A step that is a whole slice a stack kit generates: a model, a repository, a state layer, a screen | "Step 4: call the Skill tool with `project-stack`, asking for the `app` component's `build` slot for the repository. §3 fixes the signatures; keep them." |
| `project-stack`, `verify` slot | Proof above the component's Test command: rendered output, a device run | "Step 9: call the Skill tool with `project-stack`, asking for the `app` component's `verify` slot on §10.1, then add the exact assertions in §10.2." |
| `security-audit` | Storage, network, secrets or an embedded web view touched | "Step 7: call the Skill tool with `security-audit` — this task adds a token to storage." |

Hand a step to the `build` slot only when its inputs are **fully specified in the doc**. A stack
kit handed a vague slice reintroduces exactly the judgment this skill removes, so say what to pass:
*"pass §1, §5 and §11 verbatim as its brief."*

A whole workflow, such as a new feature end to end or a store release, is not a step inside a task
doc. When the task's scope is one of those, say so in §1 and name the command a human runs instead:
`/fk-build` for a new feature, `/fk-release` for a release.

**Precedence must be stated.** A skill generates its own defaults; your doc's §3 / §5 / §10 are
authoritative. Say which wins, explicitly: *"Where the `build` slot's tests differ from §10.2, §10.2
wins."* Without that line the executor keeps the generated version.

## Rules — auto-load by path glob

Read the project's `.claude/rules/` directory for the rules it actually has, and the glob each one
loads for, before citing one. Which rule files exist is a project fact: a stack kit's setup writes
them, and a project may carry more. Where the rules mirror the stack kit's architecture, the
architecture source of truth is that kit, reached through `project-stack`'s `conventions` slot. A
mirror under `.cursor/` is generated from the same sources, so cite the original rather than the
mirrored path. Always-on layer: [CLAUDE.md](CLAUDE.md).

These load automatically for the executor — but a rule that loads is not a rule that gets
followed. §11 of the doc still spells out the handful the task will actually brush against,
with the rule file cited beside each.

## Hooks — tell the executor these fire

Installed with the kits for every harness that runs hooks (`hooks/spec-to-ship-hook.py`). Which ones fire
depends on the kits installed: `secrets` comes with this kit, `format` and `fixtures` with a stack
kit that ships them. The executor will see their output and may mistake it for its own error. Warn
it in the doc when relevant:

| Hook | Trigger | What the executor sees |
|------|---------|------------------------|
| format | after every file edit | Files reformat themselves after every edit — **do not hand-format, and do not "fix" the reformat** |
| secrets | on prompt submit (on file write under opencode) | **Blocks** submission on a secret match; a literal key in the doc will jam the executor |
| fixtures | before a shell command | A heads-up before `git commit` / `git push` when `FIXTURE` markers remain — expected in fixture mode, not an error |

Consequence for **you**, the doc author: never put a real key, token, or credential-shaped
string in the doc. Use `{{API_KEY}}` placeholders and a §7 note on where the real value lives.

## Always-include for this project

Regardless of task, whenever the task creates a source file, a task doc's §11 includes the
component's most-violated conventions for a new file, such as an import rule or a registration
line every new file needs. While writing the doc, call the Skill tool with `project-stack`, asking
for the component's `conventions` on new files: the executor will not guess them.

If the task touches a feature in **fixture mode** (the component's conventions say how it is
marked), §1 must state whether fixture markers stay or go, and §6 must list any marker being
removed. Fixture markers are sanctioned conventions, not `TODO`s — an executor left to judge will
delete them.

## Verification commands for this project

Take them from the component's row in the Components table of `docs/agents/project.md`, and paste
them into §10.4 literally:

| Column | In the doc |
|---|---|
| Install | Run first, once |
| Check | Must finish clean; quote the output that means clean |
| Test | The whole suite |

Add how to run one test file and one named test, which the component's `conventions` answer. Where
the row is missing a command, `project-stack` says so: settle it before the doc ships, because an
executor told to "run the tests" runs whatever it guesses.
