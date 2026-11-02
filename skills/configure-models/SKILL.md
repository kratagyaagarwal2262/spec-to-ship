---
name: configure-models
description: Choose which model each kind of kit agent work runs on, in every harness the user has, from what they can actually reach, today's prices and benchmarks, and their budget, then save it with kit models set. Use when installing the kit, before the first kit loop run, when the user asks which models the agents use or how to cut agent cost, or when the loop's cost report suggests a change.
---

# Configure models

The kit names no models, because model lineups, prices and benchmarks change within weeks and a
name frozen into a skill is wrong by the next release. `install/roles.json` says what each kind of
work needs instead. This skill matches those needs to models the user can reach today, proves each
one answers, and saves the result once the user approves it. Until then, every kit sub-agent outside
Claude Code inherits the session's model, so a file search can run on the most expensive model the
user has.

## 1. What can be reached

Run `kit models discover`. It prints, without spending anything: the installed harnesses and
whether each one's headless run has been verified, which provider keys are set (names only, never
values), the model list from any harness that prints one, what each role needs, and the current
configuration.

Then ask only what it cannot show: which plans the user pays for (a Claude, ChatGPT or Cursor plan).
Usage a plan already includes changes the cost picture more than any price list.

The step is done when you have, for each installed harness, the models it can run.

## 2. What they cost today

Search the web for current prices and agentic-coding results for the candidates: benchmarks that
run tools in a terminal or fix real issues, with cost per task where a source gives one. Put a date
on every number and a source on every claim. Prefer an independent leaderboard to a vendor's own
page.

## 3. One question

Ask how to trade cost against quality (cheapest that works, balanced, or quality first) and what
budget per pull request the loop should stop at. Recommend balanced, and a budget about three times
what one build and two review rounds cost at the prices from step 2.

## 4. Propose

One table: each role, its model in each installed harness, and the reason, citing the step-2 line
behind it. Choose by the role's needs in `roles.json`:

- **explore**: the cheapest model whose tool calls are reliable. It runs more than anything else.
- **build**: the best coding and tool-use result per dollar. Give the loop a ladder of two, cheap
  first, so a hard ticket climbs instead of failing.
- **review**: strong at reading a diff against a spec, and **from a different model family than
  build**, so the reviewer does not share the builder's blind spots.
- **judge**: the best judgement the user can reach. It runs rarely, so this is where quality wins.
- **qa**: cheap and reliable at following steps exactly.

For the loop, pick a harness for each of builder, reviewer and escalation. Each runs as its own
process, so each can use whichever harness reaches its model best. Prefer a harness whose headless
run is verified; an unverified one needs step 5 to pass before the user opts in.

Where a harness cannot reach a suitable model for a role, leave that role unpinned there and say
the session's model will run it. Antigravity agents take only `inherit`, `flash` or `pro`.

Get the user's approval of the table before the next step.

## 5. Prove each one

For every model the loop will run, and every pinned model you are not certain of, run
`kit models probe <harness> <model> [--effort level]`. It costs a fraction of a cent, and passes
when the run succeeds and the model that answered is the one asked for. Fix a failing id and probe
again. Never save a model that has not answered.

The probe's `cost_usd` is that harness's fixed cost of starting a fresh run, before any work: each
run loads the harness's whole system prompt. Count it in every estimate. Runs started close together
reuse the prompt cache and cost several times less than a cold one, which is why the loop runs its
reviews back to back.

For a harness that does not report cost, estimate the cost of one run (its price times a typical
run's tokens, plus that start-up cost) and record it as `est_cost_usd` on that loop role, so the
budget still stops the loop.

## 6. Save

Write the approved mapping to a temporary file in this shape, then run `kit models set <file>`:

```json
{
  "version": 1,
  "basis": "prices and benchmarks checked YYYY-MM-DD: <sources>",
  "roles": {
    "explore": { "<harness>": { "model": "<model-id>", "effort": "low" } },
    "build":   { "<harness>": { "model": "<model-id>" } },
    "judge":   { "<harness>": { "model": "<model-id>", "effort": "high" } },
    "qa":      { "<harness>": { "model": "<model-id>" } }
  },
  "loop": {
    "builder":    { "harness": "<harness>", "ladder": ["<cheap-id>", "<stronger-id>"], "est_cost_usd": 0.4 },
    "reviewer":   { "harness": "<harness>", "ladder": ["<other-family-id>"] },
    "escalation": { "harness": "<harness>", "ladder": ["<best-id>"], "effort": "high" }
  },
  "budget": { "per_pr_usd": 10, "per_run_usd": 3 },
  "allow_unverified": false
}
```

`kit models set` refuses a mapping with an unknown role or harness, a reviewer starting on the
builder's model, or an unverified harness without `allow_unverified`, and says why. On success it
re-pins every installed harness. Run `kit models show` and tell the user to restart their agent
sessions, which load agents at start.

## Revisit

Once the loop has run, `kit models report` shows each role and model's runs, failures, cost and
time. Read it alongside `kit loop status` for rounds per pull request. Propose a change only with
evidence from those numbers, such as "the builder needed three review rounds on average; one step up
the ladder costs 20% more per run and should halve that". The user approves, and step 6 saves it.

## Completion criteria

Every role has a model in every installed harness, or a stated reason it inherits. Every model the
loop runs has passed a probe. The builder and reviewer come from different families. The user
approved the table, and `kit models show` prints it.
