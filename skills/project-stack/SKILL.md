---
name: project-stack
description: Resolve the project's components (an app, a backend, a database) and, for one of them, its stack, its commands and the stack kit that serves it, then hand the request to that kit's skill when it is installed. Use before any step that sets up, builds, tests, verifies or releases a component, or when a skill needs a component's commands or conventions.
---

# Project stack

No other skill in this kit names a stack. A product is made of components, each built in some
stack, and this skill is the one place that turns "verify the change in the app" into what to run
and who knows how.

## The Components table

`docs/agents/project.md` carries it under **Components**, and `/fk-setup` writes it. Contract
version 1:

| Component | Kind | Stack | Kit | Path | Install | Check | Test | Run | Build |
|---|---|---|---|---|---|---|---|---|---|

| Column | Holds |
|---|---|
| Component | A short name the rest of the project uses: `app`, `backend`, `admin` |
| Kind | `client`, `server`, `database` or `worker`. A ticket's slice lands server-side first |
| Stack | The language and framework, as the project's own docs name it |
| Kit | The stack kit that serves this component, or `none` |
| Path | Where its code lives, relative to the repo root |
| Install | The command that installs its dependencies |
| Check | Static analysis and formatting, expected to finish clean |
| Test | The whole test suite for this component |
| Run | How to start it locally against a safe environment |
| Build | How to produce what ships |

Where the table is missing, find the components from the repo: each folder with its own dependency
manifest is one. Say that is where the answer came from, and tell the user to run `/fk-setup` so the
next skill reads something written down.

## The slots a stack kit fills

A stack kit serves its components through six skills, each named `<kit>-<slot>`:

| Slot | Asked for | Returns |
|---|---|---|
| `setup` | Configure a component: its conventions, rules files and scaffolding, and its own section of `project.md` | The files written |
| `conventions` | How code is written in this component, for the aspects asked: its layers, test tools, generated files, lockfiles, what a data call returns, what a review checks | One line per aspect, with a file that shows it |
| `design` | A client component's design language: hierarchy, type, colour roles, motion, and the states a screen must handle | `docs/agents/design.md`, written or confirmed |
| `build` | One ticket's slice in the components it serves, test-first | The files changed and the tests that prove each criterion |
| `verify` | The component's verification rungs, and a claim driven up them | The rung reached for each criterion |
| `release` | What ships from this component, and the platform's release steps | What was produced, and what only a person can do |

## Answer a request

1. **Find the component**: the one named, or the one whose Path holds the files in question. Where a
   request spans components, answer each.
2. **Where the row names a kit, and the skill `<kit>-<slot>` is among the skills available to you,**
   call the Skill tool with that skill, passing the component and the request. Where one kit
   serves every component a build touches, call its `build` once with all of them.
3. **Otherwise answer from the row**, and say no stack kit answered:

   | Slot | Without a kit |
   |---|---|
   | `setup` | Nothing beyond the row itself |
   | `conventions` | Read one existing module and its tests, and report the shape with the files that show it |
   | `design` | Settle the language with the user in prose, and write it to `docs/agents/design.md` |
   | `build` | Hand back to the caller, which builds test-first against the row's Test command |
   | `verify` | Run Check, then Test. The highest rung is a passing suite; anything above it is a manual step, named |
   | `release` | Run Build, and list the platform's release steps as manual work |

## Completion criterion

Every answer names the component, its stack, and whether a kit skill or the table answered. A
request answered from neither is not answered: name the missing row or command and the question that
settles it.
