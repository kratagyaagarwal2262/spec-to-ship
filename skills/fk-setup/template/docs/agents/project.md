# Project configuration

Written by `/fk-setup`. Every kit skill reads this file for anything that differs
between projects. If a skill needs a fact that is not here, the fact belongs here.

Edit this file directly when something changes. Re-run the setup skill only to start over.

## Identity

| Field | Value |
|---|---|
| Product name | `<Product Name>` |
| Client | `<client or internal>` |
| Repo | `<git remote url>` |

## Components

Contract: 1

| Component | Kind | Stack | Kit | Path | Install | Check | Test | Run | Build |
|---|---|---|---|---|---|---|---|---|---|
| `<app>` | `<client>` | `<as the project names it>` | `<stack kit, or none>` | `<path>` | `<command>` | `<command>` | `<command>` | `<command>` | `<command>` |

`project-stack` owns what each column holds and routes every stack question through this table. A
stack kit's setup fills its components' commands and adds its own section below.

## Environments

| Environment | What it is | Safe for verification |
|---|---|---|
| `<staging>` | `<a copy of the backend with test data>` | yes |
| `<production>` | real users and real data | no |

**Never verify against an environment that writes real data** (orders, payments, messages). Name
the safe one above and use it.

## Design source

| Field | Value |
|---|---|
| Source | `<Figma MCP server>` / `<pasted CSS + screenshot>` / `<drawn screens in docs/vault/screens/>` / `<written spec only>` |
| Design file or project | `<url>` |
| Token strategy | `<get_variable_defs first, then get_design_context>` |
| Design language | `<docs/agents/design.md>` — personality, type steps, colour roles, motion tokens and state patterns. Written through `project-stack`'s `design` slot once there is something to settle; `<not yet settled>` until then |

## Documents

| Field | Value |
|---|---|
| Project memory | `docs/vault/` |
| Acceptance criteria and specs | `docs/specs/` |
| Domain glossary | `GLOSSARY.md` |
| Decisions worth recording | `docs/adr/` |
| Client questionnaires | `docs/client/` |
| Store and compliance pack | `docs/store/` |
| Issue tracker | `<GitHub — see docs/agents/issue-tracker.md>` or `<none>` |

With GitHub, `project-tracker` files and moves tickets, and `docs/agents/issue-tracker.md` records
the repo, the board and the sprint rhythm. With `none`, the backlog is a table in
`docs/vault/backlog.md` and ticket bodies are files under `docs/specs/`.

## Integrations

Only what is wired. An empty row means the product does not do this.

| Concern | Provider | Component |
|---|---|---|
| Crash and error reporting | `<Sentry>` | |
| Push notifications | `<OneSignal / FCM>` | |
| Remote config or force-update | `<>` | |
| Maps and places | `<>` | |
| Payments | `<>` | |
| Auth | `<email + social>` | |
| Analytics | `<>` | |

## Verification

| Field | Value |
|---|---|
| Test account | `<none — most flows need sign-in>` / `<where the credential is kept, never the credential>` |

| Component | Known failing tests on a clean checkout |
|---|---|
| `<app>` | `<none>` |

`verify` reads this section. Known failing tests stop an agent reporting a pre-existing failure as
its own breakage, so record each by name, per component, with the command that showed it.

<!-- Each stack kit's setup appends its own section below this line, one per component it serves. -->
