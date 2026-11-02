---
name: release-readiness
description: Before shipping to a live app, find what a change could break elsewhere and prove the one fact its safety depends on by running code. Use when /fk-release starts, or before a production release, a backend cutover, or any change to a live app the user is nervous about.
---

# Release readiness

The check before a build goes to real users of a live app. Listing what a change touches is not the
job — an agent can grep that in a second. The job is the breakage grep will not show you, and the
proof that the one thing you are relying on is actually true.

Read `docs/agents/project.md` for the Components table, the environments, the integrations, and
where each component ships.

## Do not trust your own writeup

A readiness writeup that sounds right is worthless. It reads as convincing whether or not it is true,
and that is the trap. So do not hand back the writeup. Find the one or two facts the release's safety
depends on, and prove them by running code.

### How sure are you

For each safety fact, get it as far down this list as is cheap, and **say where it stopped**.

1. You said so. Worthless alone.
2. You pointed at the line. A real `file:line`.
3. You showed the bad case cannot happen. You walked the failure path and it does not reach.
4. You ran it. A test or script that calls the real code and fails loudly if you are wrong.
5. You reproduced it in the running app on a device.

Any fact you cannot get to step 4, **say so out loud**. Do not write it up as settled, and do not
round up.

## Steps

1. **Read the change.** The diff against the last released tag, what it now does differently, and
   the part the diff does not spell out.

2. **Find the one fact it is safe because of.** Most scary-looking releases are safe because of a
   single fact. Find it. If it holds, most of the scary cases die at once. Spend your time here, not
   on a long list of maybes.

3. **Look where grep stops.** On a client that ships to users' devices it is almost always one of
   these:
   - **The API contract.** A field the backend now returns differently, or stopped returning. Our
     lenient parsing defaults will silently paper over it and show a blank or a zero.
   - **Persisted state from the previous version.** Anything cached, stored, or written by the build
     already on users' phones. A changed model shape meets old stored JSON on first launch after
     update. This is the single most common way a mobile release breaks for existing users only.
   - **The environment and its secrets.** Which environment this build actually points at. Confirm
     it from the built artifact, not from the config file.
   - **Minimum supported version and force-update gates.** Whether this build can be locked out by
     its own remote config, and whether the version compare handles the new version string.
   - **Deep links and push payloads.** A route id or payload key that changed, where the sender is
     a backend or a dashboard we do not deploy.
   - **Store-facing requirements.** New permissions, a new SDK collecting data, a privacy manifest
     that no longer matches what ships.
   - **Platform differences.** A change verified on one platform only, when the component ships
     to two.

   On a server or database component, look from the other side: a migration that rows already
   stored do not satisfy, and clients still in users' hands calling the previous contract.

4. **Be honest about each risk.** Give it a real likelihood and a real cost. Keep what you confirmed;
   list separately what you checked and cleared. Cite a real `file:line`. A search that finds nothing
   is still an answer. Never invent a caller.

5. **Prove the one fact.** Write the test or script, run it, paste the output. For the
   old-stored-state case, the proof is concrete: feed the previous version's stored payload into the
   current model and assert it still parses.

6. **Check the upgrade path, not just the install path.** Install the previous release, use it enough
   to write state, then install this build over it. A fresh install proves nothing about the users
   who already have the app. Where `verify`'s device rung is unavailable, say that this is
   unproven.

## What to hand back

- **What changes for users.** Including anything the diff does not make obvious.
- **The one fact it is safe because of.** State it, name the step you got it to, show the proof.
  Write **unproven** if you could not.
- **Risks.** Only the real ones. Each with how it breaks, a `file:line`, likelihood, cost, and how to
  check.
- **Cleared.** What you checked and why it is fine.
- **Before you ship.** The cheapest check that would catch the real bug, including the script you
  wrote.

Inside `/fk-release` the build and the store pack come next; on its own, tell the user
`/fk-release` covers them. The mechanical steps stay with the project's release checklist.
