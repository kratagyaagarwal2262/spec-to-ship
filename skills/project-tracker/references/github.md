# GitHub commands

Every operation in `project-tracker`, as `gh` commands. Run them from the repo root: `gh` resolves
the repo from the git remote, and `gh api` fills `{owner}` and `{repo}` from it. `<board>` and
`<board-owner>` come from `docs/agents/issue-tracker.md`.

## Set up

Labels. `--force` updates a label that already exists, so this is safe to run again.

```bash
gh label create "type:feature"        --color 1D76DB --description "New behaviour a user can see" --force
gh label create "type:bug"            --color D73A4A --description "Contradicts an agreed criterion or the proposal" --force
gh label create "type:change-request" --color FBCA04 --description "Outside the agreed scope; needs approval" --force
gh label create "type:chore"          --color C5DEF5 --description "No user-visible change" --force
for n in 1 2 3 5 8; do
  gh label create "points:$n" --color EDEDED --description "Story points" --force
done
gh label create needs-triage    --color E4E669 --description "Not yet classified" --force
gh label create needs-info      --color F9D0C4 --description "Waiting on an answer; the ticket says from whom" --force
gh label create ready-for-agent --color 0E8A16 --description "An agent can build this from the ticket alone" --force
gh label create ready-for-human --color 006B75 --description "Needs a person: access, a device, or a decision" --force
gh label create wontfix         --color FFFFFF --description "Decided against" --force
gh label create agent-loop      --color 5319E7 --description "Driven by kit loop" --force
gh label create agent-stuck     --color B60205 --description "The loop stopped; needs a person" --force
```

A module label, created when `project-backlog` defines the module:

```bash
gh label create "module:<slug>" --color 5319E7 --description "<module name>" --force
```

The board, only on a yes. `<board-owner>` is `@me` for a personal repo, or the organisation's login.

```bash
gh project create --owner <board-owner> --title "<app name> delivery" --format json --jq .number
gh project link <board> --owner <board-owner> --repo <owner>/<repo>
```

## File a ticket

The body goes through stdin, so no quoting can break it:

```bash
gh issue create --title "<title>" \
  --label "type:feature,points:3,module:<slug>,ready-for-agent" \
  --body-file - <<'EOF'
## Outcome
...
EOF
```

It prints the issue URL. Add it to the board where there is one:

```bash
gh project item-add <board> --owner <board-owner> --url <issue-url>
```

## Start a ticket

```bash
gh issue edit <N> --add-assignee "@me"
gh project item-edit <board> --owner <board-owner> --url <issue-url> --field Status --value "In Progress"
git switch -c <N>-<slug>
```

## Find the frontier

```bash
# candidates: ready, unassigned, not in a sprint
gh issue list --state open --label ready-for-agent --search "no:assignee no:milestone" \
  --json number,title,labels,body --limit 200
gh issue list --state open --label ready-for-human --search "no:assignee no:milestone" \
  --json number,title,labels,body --limit 200

# every open issue number, to test each "Blocked by #N" against
gh issue list --state open --json number --jq '.[].number' --limit 1000
```

A candidate is on the frontier when none of its `Blocked by` numbers is still open.

## Plan a sprint

```bash
gh api repos/{owner}/{repo}/milestones \
  -f title="Sprint 03" -f due_on="2026-10-20T23:59:59Z" -f description="<sprint goal>"
gh issue edit <N> --milestone "Sprint 03"
```

## Report

```bash
gh issue list --milestone "Sprint 03" --state all --limit 200 \
  --json number,title,state,labels,assignees

# closed points
gh issue list --milestone "Sprint 03" --state closed --limit 200 --json labels \
  --jq '[.[].labels[].name | select(startswith("points:")) | ltrimstr("points:") | tonumber] | add // 0'

# in review: open pull requests, matched to tickets by "Closes #N" in the body
gh pr list --state open --json number,title,body,isDraft --limit 100

# one feature's tickets, matched by the "Feature:" line in the body
gh issue list --state all --limit 500 --json number,title,state,labels,body \
  --jq '[.[] | select(.body | test("(?m)^Feature: M2\\.3\\s*$")) | {number,title,state}]'
```

## Close a sprint

```bash
gh issue edit <N> --milestone "Sprint 04"    # carried over
gh issue edit <N> --remove-milestone         # back to the backlog

num=$(gh api repos/{owner}/{repo}/milestones --jq '.[] | select(.title=="Sprint 03") | .number')
gh api -X PATCH "repos/{owner}/{repo}/milestones/$num" -f state=closed
```

## Close a ticket by hand

```bash
gh issue close <N> --reason "not planned" --comment "<why>"
gh issue close <N> --duplicate-of <K>
```
