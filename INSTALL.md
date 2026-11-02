# Installing the Spec-to-Ship

You are an agent installing this kit for the user. It installs once per user, never into a
project folder, and works with Claude Code, Codex, opencode, Antigravity and Cursor in any
combination.

## 1. Find out which harnesses to install for

Run the detector first, so the question you ask is about this machine rather than a guess:

```bash
curl -fsSL https://raw.githubusercontent.com/kratagyaagarwal2262/spec-to-ship/main/install.sh | bash -s -- list
```

It prints each supported harness and marks the ones found. Ask the user which of them they want
the kit in, recommending the detected ones. The choice is theirs: a harness can be installed but
unused, and installing for it only adds files.

The step is done when you have a list of harness ids from `claude`, `codex`, `opencode`,
`antigravity`, `cursor`.

## 2. Install

```bash
curl -fsSL https://raw.githubusercontent.com/kratagyaagarwal2262/spec-to-ship/main/install.sh | bash -s -- --for <ids, comma-separated>
```

For **Claude Code**, the kit is a managed plugin. When the `claude` command is on PATH the
installer adds it; otherwise it prints two `/plugin` commands. Tell the user to type those inside
Claude Code, since only they can run a slash command there.

The step is done when the installer's summary lists every chosen harness with no `failed` line.

## 3. Check it

```bash
~/.spec-to-ship/bin/kit doctor
```

Report its result to the user as it stands. `all good` means every chosen harness sees all the
kit's skills once. A line starting with `!` is a problem to report, with the fix it names.

## 4. Choose the models

Until this step, every kit sub-agent outside Claude Code runs on whatever model the session uses,
so a file search can cost what the most expensive model costs. Read
`~/.spec-to-ship/current/skills/configure-models/SKILL.md` and follow it; a harness loads newly
installed skills only after a restart, so read the file rather than waiting for the skill. It finds
what the user can reach, checks today's prices, asks one question, proves each model answers, and
saves the choice with `kit models set`.

The step is done when `~/.spec-to-ship/bin/kit models show` prints a model for every role, or the
user chose to skip it.

## 5. Tell the user what changed and what is next

- Restart each harness so it loads the new skills.
- In each project, run `/fk-setup` once. It records the project's components and the stack kit that
  serves each, so every command works the way the project already does.
- For a Flutter or Supabase project, also install Flutterbase
  (`https://raw.githubusercontent.com/kratagyaagarwal2262/flutterbase/main/INSTALL.md`): it answers
  Spec-to-Ship's stack slots.
- To let agents build a sprint's tickets on their own, run `kit loop run <project>` in that
  project once `/fk-sprint plan` has filled a sprint. It opens each pull request, gets it reviewed,
  and labels it `ready-for-human` when it is the user's turn.
- To update later, run `~/.spec-to-ship/bin/kit update`. It installs the latest release for the
  same harnesses and lists what changed.

## Updating

```bash
~/.spec-to-ship/bin/kit update
```

It installs the newest release for every harness already installed, prints the changelog entries
since the installed version, and reminds the user to restart. A **Migration** line in that output
names a step for projects set up before that release.

## Removing it

```bash
~/.spec-to-ship/bin/kit uninstall              # every harness
~/.spec-to-ship/bin/kit uninstall --for codex  # one harness
```

Uninstall removes exactly the files and config entries the install recorded. Settings the user
changed themselves stay.
