---
name: client-questionnaire
description: Turn decisions you cannot make in-house into a questionnaire for the client to fill in. Use when /fk-plan reaches a question only the client can answer, or when the user asks for a client questionnaire.
---

# Client questionnaire

Some decisions are not ours. Guessing them and building is how a feedback round becomes a rebuild.
This skill turns what we cannot answer into a **questionnaire**: one Markdown document the client
fills in async, or that we walk through together on a call.

The cheapest artifact in this kit. Reach for it before the first line of code on a new app, and
again any time a round stalls on something only the client knows.

## Grill the send, not the subject

Interview the user about the **send**, which they can always answer, not about the subject, which
they cannot. Two exchanges:

1. **Who is it going to?** Their role, how technical they are, and how close they are to the
   product. This fixes the tone and how much context the document has to carry. A founder answering
   about their own product needs no background; a marketing contact relaying answers from an
   operations team needs every question to stand alone.

2. **What do you need back?** The specific decisions or facts we cannot resolve in-house. Done when
   you have a concrete list of what we must walk away able to build.

Then write the document. Do not interview the client through the user: the questionnaire *is* the
interview.

## What to ask about on a new client app

Pull from this list only what the project actually needs. A questionnaire nobody finishes is worth
nothing, so cut every question we could answer ourselves or defer safely.

- **The one job.** What a user opens the app to do. If two answers compete, which one wins on the
  first screen.
- **Who the users are.** Every distinct role, and whether any of them can use the app without an
  account.
- **Content and copy ownership.** Who writes the user-facing strings, and in which languages. If
  the answer is "you write it", say so in the document, because it becomes our scope.
- **Rules with money or time in them.** Currency, tax, rounding, cancellation windows, minimum
  durations, timezone of record. Ask for the rule, not an example.
- **The states nobody describes.** What the user should see when a list is empty, a request fails,
  or they have no connection. Offer a recommendation for each so the client only has to disagree.
- **Notifications.** What the app is allowed to send, when, and what happens if the user denies
  permission.
- **Accounts and data.** Sign-in methods, whether accounts can be deleted in-app (both stores now
  require this where accounts can be created), and what data we are permitted to collect.
- **Store presence.** Who owns the developer accounts, the app name and subtitle, the support URL,
  and the privacy policy. These block submission, and they surface late if not asked early.
- **Out of scope.** What they are explicitly not expecting in this phase. Ask directly. A written
  "not in v1" is worth more than any other answer on the page.

## The document

Write to `docs/client/<slug>-questionnaire.md`, most-important-first, since async often means one
pass only. The session that reads the client's answers matches them against this file, which is why
it is written down; show the whole questionnaire in the reply too, ready to paste. Group under `##` headings once there are more than a handful of questions.

```markdown
# <Questionnaire title>

**Purpose:** the decision riding on these answers, in one line.

**From:** <us> · **To:** <recipient> · **Needed by:** <date> · **Rough effort:** <n minutes>

## Context

One paragraph for a reader who was not in our planning. Enough to answer well, not a briefing.

## How to answer

Type under each question. Partial answers and "I don't know" are useful — flag anything you are
unsure of rather than skipping it, and we will follow up on just those.

## <Theme>

### <One question, one idea, never compound>

_Why this matters: <one line, only where the question could be misread or invite a throwaway answer>_

**Our recommendation:** <what we would do absent an answer>

>

## Anything else?

Anything we did not ask that we should know?
```

Two rules make it work. Every question carries **our recommendation**, so the client can accept the
whole document by not disagreeing. And every question is **one idea**: a compound question comes
back half-answered.

## After it comes back

Answers are input, not criteria. Call the Skill tool with `grill` over what returned, to close the
branches the client's answers opened. Then call the Skill tool with `to-spec`; when the answers
arrive in a later session, tell the user to run `/fk-plan` with the filled questionnaire instead.

Where a question came back blank, that is a live risk: name it in the spec's assumptions rather than
quietly picking for them.
