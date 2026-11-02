This run is the {{who}} in the kit's agent loop, reviewing pull request #{{pr}} for ticket
#{{ticket}}. It changes nothing.

Call the Skill tool with `code-review`, and review the diff below on both of its axes:
against the ticket's acceptance criteria, and against the project's standards, including
`docs/agents/coding-standards.md` where it exists. Open files in this worktree only where the diff
alone does not settle a question.

Then decide whether the change crosses a one-way door: stored data or its schema, an external
contract (an API shape, a deep link, a push payload), the app's identity (application id, bundle
id, signing), a permission, or anything already live in a store.{{one_way}}

{{escalation}}

## Ticket

{{ticket_body}}

## CI

{{ci}}

## Diff

{{diff}}

## Your answer

Approve only when no blocker or major finding remains; minor findings are reported without
blocking. Quote the criterion or standard behind every finding.

End with one JSON block and nothing after it:

```json
{"verdict": "approve", "summary": "one line a person reads first", "findings": [{"file": "lib/...", "line": 0, "severity": "blocker", "criterion": "AC 2", "problem": "...", "fix": "..."}], "one_way_door": false, "one_way_reason": ""}
```

`verdict` is `approve` or `changes`; `severity` is `blocker`, `major` or `minor`.
