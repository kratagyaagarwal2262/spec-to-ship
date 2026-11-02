---
name: engineering-principles
description: Five principles that change how a change is shaped rather than what it does: root causes, subtraction, reader load, modelling the domain in types, and designing for the agent that changes it next. Use when choosing between implementation shapes, when a fix could be made at more than one level, or when reviewing whether a change was built the right way.
---

# Engineering principles

*Adapted from the `principle-*`, `architect` and `correct` skills in
[pstack](https://github.com/cursor/plugins/tree/main/pstack) by Lauren Tan (MIT), rewritten for
product teams.*

Five principles that survived the test the kit applies to everything else: does stating this change
what gets built, versus not stating it? Each is one file. Read the one that bears on the decision in
front of you, rather than all five.

| The situation | Read |
|---|---|
| A fix could be applied at the symptom or deeper | [references/fix-root-causes.md](references/fix-root-causes.md) |
| The change is only adding things | [references/subtract-before-you-add.md](references/subtract-before-you-add.md) |
| The code works but is hard to follow | [references/minimize-reader-load.md](references/minimize-reader-load.md) |
| Invalid states are possible and guarded against at runtime | [references/model-the-domain.md](references/model-the-domain.md) |
| State gains a second writer, a task a second way, or a list a second copy | [references/design-for-agent-contributors.md](references/design-for-agent-contributors.md) |

These govern **shape**, not behaviour. Where the question is what the software should do, that is a
requirement, and calling the Skill tool with `grill` settles it faster than any principle will.

## Using one honestly

Cite a principle only where it changed a concrete decision, and say which decision. A principle
named in a summary but not visible in the diff is decoration, and it makes the next reader trust
the other citations less.

Where two principles point in opposite directions, say so and pick one with a reason. That tension
is real: subtraction and reader load frequently disagree, because the smallest change and the
clearest one are not always the same change.
