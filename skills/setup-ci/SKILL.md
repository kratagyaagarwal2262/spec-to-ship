---
name: setup-ci
description: Generate a CI pipeline that runs every component's install, check and test commands on every push, then its build. Use when /fk-setup or /fk-release finds no CI, or when the user asks to set up CI.
---

# Setup CI

CI is **the automation of `verify` rungs 1 to 4**. That framing is the whole scope: the
pipeline runs what a person would run to prove a change works, on every push, so nobody has to
remember to.

What CI does not own is the human-only setup: creating store accounts, generating certificates,
fetching provider keys. `setup-wizard` owns those, and this skill consumes their output as secrets.

Run once per project, then edit the generated config directly.

## 1. Read what the project already does

Everything here comes from `docs/agents/project.md` rather than from a guess:

- **The Components table**: each component's Path, and its Install, Check, Test and Build commands
- **Environments**, and how a build selects one
- **Secret layers** each component's own section names: a gitignored env file, a generated secrets
  file, a codegen step
- **Known failing tests**, the baseline the pipeline compares against

A component that generates code does it in its Install command, so Check never analyzes symbols
nobody generated. Where Check fails on a clean checkout for missing generated files, fix the row
before the pipeline.

Done when every component has all four commands, or the missing one is named.

## 2. The stages, in ladder order

One job per component, run when a change touches its Path, or on every push where the CI cannot
filter by path:

| Stage | Command | Rung |
|---|---|---|
| Install | The row's Install command | — |
| Check | The row's Check command | 1 |
| Test | The row's Test command | 2, 3, 4 |
| Build | The row's Build command, once per environment that ships | — |

Fail fast on the cheap stages. A pipeline that runs a fifteen-minute build before a two-second
format check wastes the majority of its failures' feedback time.

## 3. The visual-baseline problem

This is the thing that will actually bite, and it lands the moment visual-baseline tests (goldens,
snapshots) and CI coexist.

They are pixel comparisons, and pixels differ between machines: font rendering and available font
faces differ between macOS and Linux most of all. A baseline generated on a developer's Mac fails
on a Linux runner while nothing is wrong.

Three workable answers, in order of preference:

1. **Generate baselines in the same environment that checks them.** Run them only on one
   runner OS, and generate the baseline there.
2. **Bundle the font.** Load a project font explicitly in the test harness rather than relying on the
   platform's, so text renders identically everywhere.
3. **Tag them out.** Mark visual-baseline tests with a tag and skip them in CI, keeping them a
   local gate. The honest but weakest option, and the pipeline should say the coverage is reduced
   rather than implying rungs 1 to 4 all ran.

Pick one and write down which, next to the Test stage, so the next person does not "fix" the
failures by regenerating the baseline.

## 4. Secrets

Every value from `setup-wizard` becomes a CI secret, referenced by name. Never a literal in the
config, and never echoed in a log: a printed secret is a leaked secret, because build logs are
retained and frequently readable more widely than the repo.

Where a component generates a secrets file at build time, that generation step runs in the
pipeline from the secrets, rather than the file being committed.

## 5. Signing and upload

Only after the ladder passes. Signing needs the certificate and provisioning profile as secrets, and
the upload needs a store credential.

Where those do not exist yet, stop before this stage and call the Skill tool with `setup-wizard`. A
pipeline that builds and verifies is worth having on its own; half-configured signing that fails
every run teaches the team to ignore red builds, which costs more than not having it.

## 6. Prove it

Push a branch and watch a real run. A pipeline that has never run is a configuration file.

Where it fails, fix it before handing over. Where it fails before the tests run (the install, the
toolchain, a native build), call the Skill tool with `project-stack` for that component's
`conventions` slot, asking how its toolchain and lockfiles are pinned and what a failure at that
stage usually means. Its stack kit knows that component's failures; the row alone does not.

## Completion criteria

The pipeline has run green at least once on a real push, with the run shown. Every component in the
Components table has a job, every stage maps to a named rung or is explicitly out of the ladder, and
the visual-baseline strategy is written down next to the Test stage.

Say which rungs CI now covers for each component and which still need a human, so `verify` claims
can be made against what the pipeline actually proves.
