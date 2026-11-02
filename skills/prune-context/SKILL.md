---
name: prune-context
description: Cut the project's docs and agent context to what is still true and still read, by folding session logs into memory, deleting finished change notes and old sprint notes, shrinking the specs of shipped features, and removing lines from CLAUDE.md, AGENTS.md and docs/agents/ that are stale, repeated or already enforced. Use when the vault's budget check prints anything, at every sprint close, or when the user asks to clean up the docs, prune context or tidy the vault.
---

# Prune context

Every line an agent reads before it starts work is paid for in every session, and a stale line costs
more than its tokens: the agent believes it. Docs grow by default, because adding feels safe and
deleting feels risky. This skill is the deleting, done on a schedule so nobody has to remember it.

Git keeps everything, so cutting is reversible: delete rather than move to an archive folder, which
is only a second place to load.

## 1. Scope

Take the lines `project-memory`'s budget check printed, where you were given them: each names a
file or folder and its budget, and those are this run's scope. At a sprint close, or when the user
asked, the scope is everything in step 2.

The step is done when you have listed the files in scope, each with its size now and its budget
where it has one.

## 2. Cut, file by file

Apply each row that is in scope. Read a file before cutting it; never cut from its name alone.

| What | Do |
|---|---|
| Log entries in `docs/vault/log/` dated after `memory.md`'s `Consolidated:` line | Promote to `memory.md` what recurred or what the next sprint will need. Then delete every log entry older than the last seven days, and set `Consolidated:` to today |
| `memory.md` | Remove lines no longer true, lines a check, test or document now enforces, and duplicates. A line needing more than a sentence moves to the note it concerns, leaving a pointer |
| Change notes in `docs/vault/changes/` whose status is `done` | Promote any lesson to `memory.md`, then delete the note and its index line |
| Sprint notes in `docs/vault/sprints/` beyond the open one and the two before it | Velocity already lives in the tracker conventions file. Delete the note, and repoint any link to it at the milestone |
| Specs of features whose tickets are all closed | Cut each spec to its acceptance criteria and out-of-scope section: the code and its tests now hold the rest. Keep the file, because the feature list links it |
| `CLAUDE.md`, `AGENTS.md`, each file in `docs/agents/` | Remove what the code, the config or a script's help already says, what is no longer true, and what another doc owns. Keep `CLAUDE.md` and `AGENTS.md` carrying the same sections |
| `docs/vault/index.md` | Remove the link of every note deleted above, and any link to a file that no longer exists |

Leave the proposal, the feature list, feedback rounds, ADRs and the glossary alone: each is a record
someone may be held to, and each has an owner that revises it.

The step is done when every file in scope is under its budget, or you have named what keeps it over
and asked the user whether to cut further.

## 3. Report

In the reply, not a file: each file pruned, its size before and after, and every line or note
deleted that held a decision, one line each, so the user can bring one back with git. Then call the
Skill tool with `project-memory` to run its budget check again and leave the session's log entry.

## Completion criterion

`project-memory`'s budget check prints nothing, or each line it still prints has the user's
decision beside it; no index link points at a deleted note; and the reply
lists every deleted decision.
