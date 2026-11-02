# Adversarial self-audit

Read the finished doc **as the executor**: literal, no repo context, unable to ask a question,
inclined to add code and disinclined to delete it. You are hunting for the places it would
improvise.

Any box you cannot tick is an open decision. Go back to Phase 2, resolve it, and re-audit.

## A. Guess hunt — the primary pass

Read every sentence and ask: *could two competent executors read this and produce different
code?* If yes, it is not finished.

- [ ] Search the doc for these strings; each hit is a defect:
      `TODO`, `as appropriate`, `if needed`, `similar to`, `and so on`, `etc.`, `consistent with`,
      `reasonable`, `should probably`, `where applicable`, `use your judgment`, `see above`,
      `as discussed`, `the usual`, `standard`
- [ ] No section says "and similarly for the other states / rows / cases" — each is written out
- [ ] Every threshold, limit, timeout and default is a number, not an adjective
- [ ] Every "add a constant" instruction gives the literal value
- [ ] Every ordering (list sort, enum, build steps) is specified, including tie-breaks
- [ ] No requirement exists only in a link (ticket, Figma URL, another doc) — the doc states it

## B. Self-containment

- [ ] The doc never references this conversation, the user, or the requirements discussion
- [ ] Every project-specific term is either defined or cited to a rule file
- [ ] An executor with no project knowledge could apply §11 without reading anything else
      *except* the rule files §11 names
- [ ] No credential-shaped literals (the kit's secrets hook will block the executor's prompt)

## C. Verifiability

- [ ] Every finding in §2 has a `file:line` link that resolves in the current tree — **open each
      one and confirm the line number is right**, do not trust your earlier read
- [ ] Every number in §2 was computed, not estimated
- [ ] The §2 boundary values appear as assertions in §10.2
- [ ] The §10.1 fail-before/pass-after test names the exact step it flips on
- [ ] §10.1 states what the *pre-change* failure message looks like, so a wrong-reason failure
      is detectable
- [ ] Every §6 deletion has a `rg` command that proves it

## D. Deletion coverage — the highest-yield pass

Cheap executors add and do not remove. Walk it deliberately:

- [ ] For every thing §1 says to **create**, ask: what does it make obsolete? Is that in §6?
- [ ] For every §6 deletion, is the replacement named — including "**Nothing.**"?
- [ ] Are dead constants, strings, assets and barrel export lines included, not just classes?
- [ ] Are obsolete **tests** deleted too, not just source?
- [ ] Does the §6 `rg` command cover every identifier removed?

## E. Executability

- [ ] Every §9 step compiles on its own — mentally apply each and check for dangling references
- [ ] Exactly one step is labelled **CUTOVER**
- [ ] Step N never depends on a file that step N+2 creates
- [ ] The commands in §10.4 are real and runnable in this repo
- [ ] If a skill is invoked, precedence is stated: which wins, the skill's output or the doc's

## F. Failure labelling

- [ ] Every early return, empty result, and zero-count outcome in the doc's logic is labelled
      **Normal** or **Wrong** in §8
- [ ] §8 says what to do on each **Wrong** row — not just that it is wrong
- [ ] There is at least one row covering "it compiled and tests passed but the change did not
      actually take effect"

## G. Coupling

- [ ] Every other doc in `docs/tasks/` has been checked against this one
- [ ] No stale text was left behind with a "see doc NN" note appended
- [ ] Prerequisites in the header carry a runnable verification command
- [ ] Line numbers were **re-measured** after any prior doc shipped, not adjusted by arithmetic

## H. Scope discipline

- [ ] "Do NOT touch" names the things an executor would be *tempted* to fix
- [ ] Nothing outside §1's create/modify lists is edited by any instruction in §3–§11
- [ ] `Code in scope: YES/NO` is stated in plain words

---

## Final sweep

Pick the three most complex instructions in the doc. For each, write out — in your head, not in
the doc — the code a literal executor would produce. If it differs from what you intended, that
instruction is the next thing to fix.

Then report to the user:

- doc path and section count
- exhaustive tables shipped, with row counts
- every assumption you locked in on their behalf (this is the one thing they must review)
- any scope you deliberately excluded, and why
