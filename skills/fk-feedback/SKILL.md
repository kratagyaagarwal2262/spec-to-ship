---
name: fk-feedback
description: Sort a round of client or tester feedback into bugs, change requests and questions against the agreed proposal, file each one, and draft the reply.
disable-model-invocation: true
---

# Feedback

Feedback is where scope drifts without anyone deciding it should. A change request filed as a bug
is unpaid work and a slipped sprint; a bug argued as a change request is a client who stops
trusting the team. This command classifies every item against what was agreed, so each answer has a
reason the client can read.

## 1. Orient

Read `docs/agents/project.md`, then call the Skill tool with `project-memory` to load the vault.
Read the proposal's current revision, especially out of scope and how the team works, and the
feature list in `docs/vault/features.md`. Note whether
a UAT window is open: during UAT every change request is deferred.

## 2. Keep their words

Write the round verbatim to `docs/vault/feedback/round-NN.md` with its source, date, sender and the
build it was about, and keep any screenshots beside it in `docs/vault/feedback/round-NN/`. Then split
it into items, numbered F1 onwards, one idea each: a sentence asking for two things is two items.

The step is done when every sentence of the original is covered by an item, or noted as needing
no action.

## 3. Classify

For each item, find what was agreed about it: the ticket's acceptance criteria (call the Skill tool
with `project-tracker` to read them), the proposal, the glossary.

| Class | When |
|---|---|
| Bug | The app contradicts an agreed criterion or the proposal, or is plainly broken: a crash, lost data, an unusable layout |
| Change request | It asks for behaviour no agreed criterion, feature or proposal section promises, or that out of scope excludes |
| Question | It asks for information, and nothing needs to change |
| Known | It is already fixed in a later build, or already a ticket |
| Unclear | It cannot be reproduced, or nothing agreed decides it |

Quote the line that decides every bug and change request. An item with no deciding line is
**Unclear**, never a quiet pick: whether work is billable is the user's call, not the agent's.

Show the table (item, class, deciding line, proposed action) and get the user's confirmation before
filing anything.

## 4. Act

- **Bug**: call the Skill tool with `project-tracker` to file it as `type:bug`, its body quoting the
  criterion it breaks, the steps, and the build. A bug in this sprint's work goes into this sprint.
- **Change request**: call the Skill tool with `grill` to turn it into acceptance criteria, then call
  the Skill tool with `project-backlog` to slice and point it. File it as `type:change-request` and
  `needs-info` until the client approves the estimate. On approval, call the Skill tool with
  `project-proposal` to add the revision and the feature's row, set the ticket's `Feature:` line to
  it, and relabel it `ready-for-agent`. During UAT, file it and
  leave it for after launch.
- **Question**: draft the answer. Where only the client can answer something this raised, call the
  Skill tool with `client-questionnaire`.
- **Known**: link the ticket or the build that has it.
- **Unclear**: put the question back to the user, or to the client in the reply.

## 5. Draft the reply

Draft the reply in the conversation, ready to paste, item by item in the client's numbering: what
will be fixed and in which sprint, which items are change requests with their estimate in days and
what they would push back, the answers, and anything we need from them. Plain language, no ticket
jargon. Tell the user they can run `/unslop` over it before sending. It goes to the client once and
nobody reads it from the repo, so it is not written to a file: the round's note keeps what was
decided.

Append the classification table, with ticket links, to the round's note, link the note from the
vault index, and leave a log entry.

## Next

End every run, including one that stops early, by calling the Skill tool with `next-step`, handing
off `/fk-build` for the first bug filed, or, where the round filed none, the client's approval of
the change requests.

## Completion criteria

Every item has a class, the line that decides it, and an action with a link. Nothing was filed
before the user confirmed the table. Every change request has an estimate and is waiting on approval
rather than scheduled. The reply covers every item.
