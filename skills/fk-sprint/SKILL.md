---
name: fk-sprint
description: Run the sprint, from planning it out of the ready tickets and reporting where it stands, through gating its build with QA before anyone outside sees it, to closing it with velocity and a review, or running the final acceptance window.
disable-model-invocation: true
---

# Sprint

A sprint is a promise sized to what has actually been delivered before: a goal, the tickets that
serve it, and a date. This command keeps the promise honest at each of its five moments. Each mode
calls the skills that own its parts; this one owns the order and the gates between them.

| Mode | When |
|---|---|
| `plan` | No sprint is open, and the backlog has ready tickets |
| `status` | A sprint is open and you want to know where it stands |
| `qa` | The sprint's tickets are merged, and a build is about to go to a client or tester |
| `close` | The sprint's last day has passed |
| `uat` | Every planned sprint is closed, and the final acceptance window starts |

Take the mode the user named. With none, infer it: no open sprint → `plan`; an open sprint before
its due date → `status`; one past it → `close`. Say which you chose.

## Before any mode

Read `docs/agents/project.md` and `docs/agents/issue-tracker.md`, and call the Skill tool with
`project-memory` to load the vault. Where `issue-tracker.md` is missing, or `project.md` names no
tracker, tell the user to run `/fk-setup` first. Where there is no backlog yet, tell them to run
`/fk-plan`.

## plan

A sprint delivers **one user flow**: a journey a user can walk from its start to its end in the
build, such as the whole of onboarding. That is what a client can be shown, and what makes the next
flow buildable. The flows and their order come from the **Flow** column of
`docs/vault/features.md`, which `project-proposal` keeps in delivery order.

1. **The flow.** Read `docs/vault/features.md` for the current phase. The sprint's flow is the first
   flow, in the list's order, that still has open tickets; tickets the last sprint carried over
   belong to it, or finish first. Where the list has no Flow column, call the Skill tool with
   `project-proposal` to add one before going on: a sprint cut from features alone drifts to
   whatever small item happens to fit.
2. **Its tickets.** Call the Skill tool with `project-tracker` for every open ticket of every feature
   in the flow, including tickets blocked by other tickets in the flow: a blocker inside the sprint
   only fixes the order. A ticket blocked by work outside the flow is a finding: that blocker joins
   the sprint, or the flow cannot finish, and you say which. A Must feature of the flow with no
   tickets yet is a gap: call the Skill tool with `project-backlog` for it before going on. Order
   the tickets foundation first, then by how many others each unblocks.
3. **Capacity.** From `issue-tracker.md`: the average velocity of the last three closed sprints.
   Before any sprint has closed there is nothing to average, so the first sprint is sized by its
   flow: its points become the guess, marked as one, unless the user says one sprint cannot hold
   that much.
4. **Fit.** Compare the flow's points with capacity:
   - **It fits:** the sprint is the whole flow. Where it leaves more than a third of capacity
     unused, offer the next flow's first tickets as **stretch**, listed apart from the commitment,
     so spare capacity is used without blurring what the sprint promised.
   - **It does not fit:** split the flow by screen, in the order a user meets them. The sprint takes
     the first stage, a stretch of screens a user can walk start to finish on real data, and the
     rest is the next sprint's goal. A sprint never commits to less than one whole stage.
5. **Goal.** The flow, or its stage, and its features by ID, in one sentence a client would
   understand, such as "Onboarding (M1.1 to M1.4): a new user can sign up, verify their email and
   reach the home screen".
6. **Ready check.** Every chosen ticket has numbered criteria and points. One that does not goes back
   for criteria: call the Skill tool with `grill` for it, or leave it out. List `ready-for-human`
   tickets separately: they are the user's own work this sprint.
7. **Confirm.** Show the goal, the dates, the tickets with points, the total against capacity, the
   stretch tickets, and the human tasks. Then the **sprint map**: every remaining flow of the
   current phase assigned to a sprint in order at today's capacity, with its points and its
   expected end date, so the user approves the sequence and not one sprint in isolation. The map is
   recomputed at every plan, so it stays in the reply. On a yes, call the Skill tool with
   `project-tracker` to create the milestone and assign the committed and stretch tickets, write
   `docs/vault/sprints/sprint-NN.md`, and point the vault index's **Now** line at it.

```markdown
# Sprint NN: <goal>

**Dates:** YYYY-MM-DD to YYYY-MM-DD · **Milestone:** <link> · **Capacity:** <N points, measured | guess>
**Flow:** <Onboarding, or Onboarding stage 1 of 2> · **Features:** M1.1, M1.2, M1.3

## Committed

- #12 <title> (5)

## Stretch

- #18 <title> (3)

## Human tasks

- #15 <title>

## QA

## Review
```

The Committed list records the promise and never changes; the tracker records what happened to each
ticket.

Then tell the user how the tickets get built. By hand: `/fk-build #N` for each, in the order given;
tickets with no edge between them can run at the same time, each in its own session, branch and
worktree. Unattended: `kit loop run` (add `--watch 300` to keep it running) builds the
`ready-for-agent` tickets, gets each pull request reviewed, and labels it `ready-for-human` when it
is theirs to test and merge.

## status

Call the Skill tool with `project-tracker` for the sprint report, and relay it in plain language for
someone who has not looked at the code: what is done, in review, in progress, not started and
blocked, and by what. Compare points closed with points committed and days gone with days left.
Where the sprint is behind, name the ticket you would drop to save the goal.

## qa

The gate between merged work and a build someone outside sees.

1. Name the build: the commit on the main branch that the build will be cut from.
2. Dispatch the `qa-engineer` agent with that commit, the sprint's milestone and the closed tickets.
   It runs the analyzer and the suite against the baseline, proves each ticket's criteria at the
   highest rung the project can reach, and files every failure as a bug ticket in this sprint.
3. Write the QA section of the sprint note: the commit, each ticket with the rung reached and its
   result, and the bugs filed.

The build passes when no open bug is filed against a ticket in this sprint. A pass goes out: tell
the user to run `/fk-release` with a tester group as the target. A fail goes back: tell them to run
`/fk-build` on each new bug, then `/fk-sprint qa` again.

## close

1. Call the Skill tool with `project-tracker` for the final report: closed against committed, in
   points.
2. For each unfinished ticket, ask whether it carries into the next sprint or goes back to the
   backlog. Recommend carrying it when it serves the next goal.
3. Write the Review section of the sprint note: the features finished, by ID, as outcomes a user
   would notice; what did not finish, and why; the feedback rounds and changes that came in,
   linked; the velocity.
4. Call the Skill tool with `project-tracker` to move the unfinished tickets, close the milestone and
   record the velocity.
5. Call the Skill tool with `prune-context` to cut the vault and the agent docs back to what the
   next sprint will read.
6. Where velocity has now been measured twice and the proposal's timeline still rests on a guess,
   call the Skill tool with `project-proposal` to revise the timeline.
7. Where `kit loop` built tickets this sprint, call the Skill tool with `configure-models` to read
   the cost report against the review rounds, and propose a model change only where the numbers
   support one.

Then tell the user to run `/retro` while the round is fresh. Where every Must feature of the current
phase is now done, say so too: the phase is ready for `/fk-sprint uat` and `/fk-release`, and
`/fk-plan` cuts the next phase's tickets after it.

## uat

The final acceptance window before the store, one week unless the proposal says otherwise.

1. **Freeze.** From now on only bugs are fixed. Every change request is recorded and deferred to a
   revision after launch. Draft the message telling the client this, for the user to send.
2. **Milestone.** Call the Skill tool with `project-tracker` to create a `UAT` milestone due at the
   window's end.
3. **Checklist.** Draft it in the conversation, ready to paste to the client: for every module, each
   agreed criterion as a checkbox in the client's words, which build to test it on, and how to report
   a problem. Use the glossary's terms; it is read by someone who never saw a ticket. The criteria
   already live in the tickets and specs, so the vault records only the build and the window's dates,
   in `docs/vault/sprints/uat.md`.
4. **During the window**, feedback goes through `/fk-feedback`, which applies the freeze.
5. **Sign-off.** When the client accepts, record who and when in `docs/vault/sprints/uat.md`, and
   call the Skill tool with `project-proposal` to add the sign-off as a revision row. Then tell the
   user to run `/fk-release` with the store as the target.

## Next

End every run, including one that stops early, by calling the Skill tool with `next-step`, handing
off the step the mode above names: `/fk-build` for the sprint's tickets after `plan`, `/fk-sprint qa`
or `/fk-release` after `qa`, `/retro` after `close`.

## Completion criteria

- **plan**: a milestone exists whose goal is one whole flow or one whole stage of it, every
  committed ticket has criteria and points, the total is at or under capacity, the sprint note links
  each ticket, and the user has seen the sprint map.
- **status**: points closed against committed, and every blocked ticket named with its blocker.
- **qa**: every closed ticket has a rung and a result in the sprint note, and every failure is a
  filed bug.
- **close**: velocity recorded, every unfinished ticket moved, the milestone closed, the review
  written and the vault pruned.
- **uat**: the checklist covers every module, and the sign-off, when it comes, is a revision row.
