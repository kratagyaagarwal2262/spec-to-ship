---
name: retro
description: After a round of work, propose improvements to the kit and the project's agent environment so the next round is shorter.
disable-model-invocation: true
---

# Retro

An agency ships the same shapes of work over and over. That is the whole opportunity: every round
should make the next one shorter. This skill turns a finished round into concrete edits, not
reflections.

You are improving the **environment the agent works in**, not the code it wrote.

## Process

1. Call the Skill tool with `writing-for-agents` for the writing standard before proposing any prose
   edit.

2. Read the primary sources for the round: the diff, the spec, the acceptance criteria, the review
   findings, and what the client came back with. If the round produced a feedback round, that is the
   most valuable input on the page. Where the project has `docs/vault/`, the sprint note, the
   feedback rounds and the log entries since the last retro are the round's record: read them first.

3. Look for candidates in these categories, in roughly this order of value.

   - **Alignment gaps.** Did a rebuild happen because a criterion was never pinned down? Which
     question, and where should it have been asked: `client-questionnaire`, `grill`, or the spec's
     assumptions section? This is the highest-value category on client work, and the one most often
     skipped in favour of code cleanup.
   - **Automated checks.** Could a lint, a test, a hook, or an analyzer rule have caught the mistake?
     Read what the repo already runs first: the linter config, the CI workflow, any pre-commit hook,
     and the Components table in `docs/agents/project.md`. A check that exists but is unwired,
     disabled or silently failing is the finding, not a reason to add a second one. A repo where
     nothing runs each component's Check and Test commands on every change, neither a pre-commit
     hook nor a CI job, is itself a finding: propose a pipeline built with `setup-ci`.
   - **Review rules.** Did the reviewer miss something it should have caught, or keep flagging noise?
     Conventions belong to the reviewer, not the implementer: the implementing agent is under the
     most context pressure and the reviewing agent is under the least. A judgement call true of every
     app goes into `code-review`'s baseline; one true of every app in one stack goes into that stack
     kit's conventions; one true of this project goes into its `docs/agents/coding-standards.md`,
     which only the reviewer reads. None goes into `CLAUDE.md`.
   - **Information access.** Was something the agent needed simply unavailable: the running app's
     logs, a device screenshot, the backend's response, a third-party dashboard? Giving the agent
     read access, such as a teed log file or an MCP server, often beats any amount of instruction.
   - **Tool economy.** Did the agent pay for an expensive call it could have avoided: a full test
     suite run per slice, a whole-file read where a search would do, a verbose MCP tool? Name the
     cheaper route and where it should be written down. Where `kit loop` ran, `kit models report`
     shows what each role and model cost; a role on a stronger model than its work needs is a
     `configure-models` change, not a prose rule.
   - **Navigation.** Did the agent spend a long time finding something? A pointer in `CLAUDE.md` or a
     row in `docs/agents/project.md` is cheaper than repeated searching.
   - **Glossary.** Did we and the client mean different things by a word? That is a `GLOSSARY.md`
     entry, and possibly an ADR.
   - **No-ops.** Instructions in the steering files that do not change behaviour. Deleting these is
     as valuable as adding a good one, and safer than it feels.
   - **Kit versus project.** Decide where each edit belongs. A lesson true for every client app goes
     to this kit's skill; one true of every app in one stack goes to the stack kit the Components
     table names; a lesson true only here goes to this project's `CLAUDE.md` or `project.md`.
     Putting a project fact in a kit is how a portable kit stops being portable.

4. Present the candidates in severity order, each as a concrete edit: the file, what changes, and the
   evidence from this round that motivates it. No general advice.

5. Apply only what the user approves. Skill changes affect every future project, so nothing lands
   automatically. Where the round was a sprint, add a Retro section to its sprint note listing each
   applied edit and what enforces it (the check, the type, the test, or "review rule"), so the next
   retro can see whether it worked.

6. Call the Skill tool with `next-step`, handing off the project's next stage.

## The structural test

Before writing any candidate as prose, classify the mistake behind it.

- **Mechanical**: a fixed pattern a tool can see. A banned API, an import shape, a file in the wrong
  folder, a literal where a token belongs. This gets a deterministic check, full stop. The prose
  version is never the candidate.
- **Judgement**: needs reading, not matching. Consistency across files, whether a name fits the
  domain, whether a state is handled sensibly. This becomes a review rule, as above.

A rule that has to be remembered will be forgotten; a rule that fails a build will not.

For a mechanical mistake, propose the highest of these levels that works, and say why each level
above it does not:

1. **Remove the cause.** Give the state one owner, delete the second way of doing the task, derive
   the hand-kept list. Call the Skill tool with `engineering-principles` for the shapes that keep
   misleading an agent.
2. **Make it unwritable.** A sealed class, an exhaustive `switch`, a non-nullable field, a
   library-private name.
3. **Fail the build with a message that names the fix.** A linter rule, a custom lint, a hook or a
   CI step, whichever the repo's existing guardrail makes cheapest. Its error names the file, type
   or function to use instead. Where the pattern is already common, fail only on new occurrences.
4. **A test**, where the mistake is a behaviour rather than a shape.

Prove each new check on this round's own mistake: put the mistake back, run the check, and show it
fail. A check that never failed has not been shown to catch anything.

When a mistake repeats a rule a previous retro already wrote down and nothing enforced, that is the
finding: the rule moves up this list in the same change, not into firmer prose.
