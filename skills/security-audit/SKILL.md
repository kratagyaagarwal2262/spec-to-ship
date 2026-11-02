---
name: security-audit
description: Audit a change or a codebase for security across secrets, authentication and authorisation, input handling, data at rest and in transit, dependencies, and logging of personal data, adding each component's platform checks from its stack kit. Use before a release, after work touching credentials, sign-in, stored data, the network or user input, or when asked for a security audit or review.
---

# Security review

An audit across seven pillars, run before a release or over a change that touches credentials,
sign-in, stored data, the network or input from outside. The pillars hold for any stack; what each
one looks like in code is the component's own, and its stack kit knows that part.

This skill reads and reports. Fixes land only once the user has approved them, because a security
edit made silently is one nobody reviewed.

Whether a branch does what the spec asked is a different question, which `code-review` answers. The
two do not substitute.

## 1. Scope and platform checks

Take the scope: a change (a branch, a diff, a file list) or `all`, and the files changed recently to
look at first.

Call the Skill tool with `project-stack` for the components the scope touches, asking each for its
`conventions` slot with the aspect `security`. A stack kit answers with the platform's own checks:
where secrets are allowed to live, which storage is encrypted, how the network layer can be told to
trust a bad certificate, what a backend's access rules look like. Add each check under the pillar it
belongs to, and run it there.

Where no stack kit answers, the pillars below are the whole audit for that component; say so in the
report.

The step is done when every component in scope is named, with its platform checks filed under the
pillars, or a line saying it has none.

## Severity

- **Critical**: fix immediately
- **High**: fix before release
- **Medium**: fix soon
- **Info**: consider improving

## Pillar 1: secrets

| Pattern | Severity |
|---|---|
| An API key, token, password or private key written into source or config that ships | Critical |
| A token-shaped string (a JWT, a provider-prefixed key such as `sk_live_`) in source | Critical |
| A base64 blob that decodes to a credential | Critical |
| A secret in git history, though gone from the working tree | Critical |
| A server-only key (an admin or service key) reachable from a client | Critical |
| A secret file (`.env`, a signing key, a credentials file) not ignored by git | High |

Search history as well as the tree: `git log -p -S '<prefix>'` for each key prefix the project's
providers use.

## Pillar 2: authentication and authorisation

| Pattern | Severity |
|---|---|
| An operation on another user's data that the server does not check ownership of | Critical |
| Authorisation enforced only in the client, with the server accepting any caller | Critical |
| A role or permission read from input the caller controls | Critical |
| A session or token with no expiry, or not revoked on sign-out | High |
| A password reset, invite or magic link that can be reused or never expires | High |
| An endpoint added by the change with no authentication decision recorded | Medium |

For each piece of user data the scope reads or writes, name the rule that stops a second user
reaching it, and where it is enforced. A rule enforced only where the attacker runs the code is not
enforced.

## Pillar 3: input handling

| Pattern | Severity |
|---|---|
| Input concatenated into a query, a shell command or a file path | Critical |
| Input rendered as markup or script without escaping | High |
| A URL from input or from a server response opened or loaded without an allowlist | High |
| A deep link or inbound message acting on its parameters without validating them | High |
| An upload accepted without a size limit or a type check | Medium |

## Pillar 4: data at rest

| Pattern | Severity |
|---|---|
| A password or payment data stored on the device or in a database unencrypted | Critical |
| A raw session token in plain storage where the platform offers an encrypted store | High |
| Personal or sensitive data persisted with no reason the spec gives | High |
| Sensitive data kept in memory or state after the flow that needed it ends | High |
| A backup or export that carries what the primary store encrypts | Medium |

## Pillar 5: data in transit

| Pattern | Severity |
|---|---|
| Certificate validation disabled, or every certificate trusted | Critical |
| Cleartext traffic allowed in a release build | Critical |
| A development or staging URL reachable from a release build | Critical |
| No certificate pinning on an API carrying payment or health data | High |
| A secret or personal data in a URL query string | High |

## Pillar 6: dependencies

| Pattern | Severity |
|---|---|
| A dependency with a published vulnerability affecting the version in the lockfile | Critical or High, as published |
| A dependency discontinued or unmaintained, on a path that handles data or auth | High |
| No lockfile committed, so the shipped versions are not the reviewed ones | Medium |
| A dependency added by the change that duplicates one already in use | Info |

Use the ecosystem's own audit command where the component has one, and name the command in the
report.

## Pillar 7: logging and personal data

| Pattern | Severity |
|---|---|
| A credential, token or password written to a log, crash report or analytics event | Critical |
| Personal data (name, email, location, health, payment) sent to a third party the privacy policy does not name | High |
| A full request or response body logged in a release build | High |
| An empty error handler that discards a failure the user or the logs needed | High |
| Debug logging left switched on in a release build | Medium |

## Findings table

Every finding cites a real `file:line` you have read. A pattern you expect to exist but did not find
is not a finding.

| # | Pillar | File | Line | Severity | Description | Fix |
|---|---|---|---|---|---|---|
| 1 | Secrets | src/api/client.ts | 42 | Critical | Payment provider key in source | Read it from the build environment |
| 2 | Data at rest | src/auth/session.ts | 78 | High | Session token in plain storage | Move it to the platform's encrypted store |

Redact as you go. This skill has you quote source that holds live keys: write `<REDACTED>` in place
of any real credential value, including in the description column.

## Workflow

1. Run step 1, then all seven pillars over the scope, in order, with each component's platform
   checks inside the pillar they belong to.
2. Present the findings table, worst severity first.
3. Apply the fixes the user approves, Critical first.
4. Run each touched component's Check and Test commands, which `project-stack` names, and compare
   against the baseline in `docs/agents/project.md`.

## Completion criteria

The audit is done when all seven pillars have been run over the whole scope, with every platform
check a stack kit returned, and each pillar has an explicit result, including the ones that found
nothing. Report:

- The findings table, or "no findings" per pillar.
- For each component, whether a stack kit supplied platform checks or the pillars stood alone.
- Which pillars you could not complete, and what blocked them.
- For every applied fix, the before and after, and the re-run output.

A pillar skipped in silence reads as a pillar that passed, which is the failure this criterion
prevents.
