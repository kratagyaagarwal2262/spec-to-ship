---
name: handoff
description: Compact the current conversation into a handoff document another session can pick up.
disable-model-invocation: true
---

# Handoff

Write a document that lets a fresh session continue this work without re-deriving it. Save it to the
OS temp directory, not the project, unless the user asks otherwise — a handoff is scaffolding, not a
deliverable.

Include:

- **Where this stands.** The feature or bug, the branch, and what is done versus outstanding.
- **Decisions already made**, with the reason. This is the part that is expensive to rediscover and
  the part a fresh session is most likely to relitigate.
- **What was tried and abandoned**, and why. Without it the next session repeats it.
- **Suggested skills.** Name which skills the next session should call, and for what.
- **The verification state.** Which rung the work has been proven to, per `verify`, and what
  remains unproven.

Do not restate what already lives somewhere durable — the spec, the acceptance criteria, an ADR, the
commits, the diff. Reference those by path. A handoff that duplicates the spec goes stale against it
within a day.

Redact anything sensitive: keys, tokens, credentials, customer data.

If the user said what the next session is for, tailor the document to that and cut the rest.
