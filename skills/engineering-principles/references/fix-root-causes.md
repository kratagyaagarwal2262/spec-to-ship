# Fix root causes

When a symptom has a cheap local fix and an expensive deeper one, the deeper one is usually correct,
because the cheap fix leaves the cause free to produce a second symptom somewhere you are not
looking.

## How to tell which level you are at

Ask what has to be true for the symptom to happen, then ask that again about the answer. Stop when
the answer is a decision somebody made rather than a consequence of one.

A crash force-unwrapping `state.data` is a symptom. That `data` is null in the success state is a
consequence. That the state allows success and null data together is the decision, and that is the
level worth fixing.

## The shapes this takes

| The patch | What it hides |
|---|---|
| An empty-string default on a field that should never be empty | A parse that silently accepted the wrong shape |
| A "is the screen still there?" check added after an await until a crash stops | An async flow nothing owns or cancels |
| A `try/catch` swallowing an exception to stop an error screen | A failure the user should have been told about |
| A state write deferred to the next frame to dodge a render error | State being written during a render |
| A widened timeout until a flaky test passes | A race the test was correctly catching |
| A re-recorded snapshot to clear a failure | A visual regression, now approved |

Each of these is sometimes right. What makes it a patch is applying it **without being able to say
what the cause was**.

## When the shallow fix is the correct one

- The cause is in a dependency you do not control, and the patch is documented as a workaround with
  a link to the upstream issue.
- Production is broken now. Then the shallow fix ships, and the root cause becomes a task rather
  than a memory.
- The deep fix is a redesign whose cost the user should decide on. Name both and let them choose.

In all three the difference is the same: you can state the cause. Say what it is and what the patch
defers, so the next person is not re-deriving it.

## The test that proves you found it

A test that fails for the cause rather than the symptom. Fixing the state shape above means a test
asserting that a success state carries data, and it fails on the old code even where the screen
that crashed is not involved at all.
