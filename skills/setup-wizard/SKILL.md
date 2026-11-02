---
name: setup-wizard
description: Generate an interactive script that walks a human through setup steps only they can perform, such as provisioning credentials, store accounts, or signing. Use when a step needs a person in a third-party dashboard, not when an agent could do it.
---

# Setup wizard

Some steps need a human: fetching a key from a dashboard, creating a store listing, uploading a
signing certificate, enabling a provider. They are tedious by hand and more tedious to re-explain to
an agent every time a new project starts.

A **wizard** is a script that walks a person through one such procedure: it opens each URL, says
exactly what to click and copy, captures the value, writes it where it belongs, and confirms at every
stage.

Do not reach for this when an agent could do the step itself. This is for where a human is genuinely
in the loop.

## Why it pays here

On a new client app the same human-only list recurs: a Firebase project and its two config files, a
push provider's app id and REST key, a maps or places API key with the right restrictions, a crash
reporting DSN, signing identities on both platforms, and two store listings. Written once as a
wizard, that stops being tribal knowledge and becomes a script the next project runs.

## Process

### 1. Scope the procedure

Read the repo before asking anything. A gitignored `.env` and any `.env.example`, the generated
secret files, the build-flavour script, each platform's native build config, the integrations table
in `docs/agents/project.md`, and any CI workflow — every secret reference in CI is a value the
wizard must produce.

Then show the user the ordered stages and the values each produces, and confirm. They may add, drop,
or reorder.

Done when, for every captured value, you know where the human gets it, where it is written (the env
file, a CI secret, a native config file, or nowhere because the stage is a pure action), and whether
it is secret and so needs hidden entry.

### 2. Map each stage's journey

For each stage write the precise path: which URL, what to do there, where the value appears, what it
fills. "Console → Project settings → Cloud Messaging → copy the Server key."

Where you do not know the current UI or the exact command, **say so and ask**, or check the vendor's
docs. Never invent steps in a dashboard you have not seen; a wrong click path is worse than none,
because the person following it assumes they made the mistake.

### 3. Author it

Write a bash script to `scripts/` in the project, or a scratch path if it is one-off. Structure every
stage the same way: clear the screen, say which stage of how many, open the URL, explain the clicks,
capture the value with hidden entry if secret, write it, confirm before anything irreversible.

Keep one focused task per stage so nothing the person needs scrolls out of view.

Never write a captured secret to a file that is not gitignored, and never echo one back to the
terminal. For a value that belongs in a native config file the kit does not manage, tell the person
where to put it rather than writing it for them.

### 4. Verify and hand off

- `bash -n <script>`, and `shellcheck` if available.
- `chmod +x`.
- Do not run it end to end yourself: it opens browsers and blocks on input. Trace it statically
  instead — every value from step 1 is captured and lands where step 1 said it would.
- Tell the user how to run it. If the procedure will recur on the next project, commit it and link it
  from the README, and consider whether it belongs in the kit rather than this repo.
