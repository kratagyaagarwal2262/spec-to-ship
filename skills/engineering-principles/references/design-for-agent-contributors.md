# Design for agent contributors

Assume the next change to this code is made by an agent that sees only the files it opened, copies
the nearest example, and takes the shortest path that compiles. Prefer the shape where a change that
looks right from one file is right for the whole app.

## Four shapes that mislead it

| The shape | What the agent does | The fix |
|---|---|---|
| Two places write the same state, or one keeps its own copy | Edits the writer it found, and the others drift | Give each piece of state one owner; everything else reads it or asks the owner to change it |
| Two ways to do one task: two dialog helpers, two date formatters, two paths to the API | Copies whichever it found first, so both keep gaining callers | Keep one, move the callers onto it, and delete the other in the same change |
| A helper written for one feature that any file can call | Calls it from somewhere else, and it becomes shared without anyone deciding that | Make it private to its file or module, or move it to the shared code on purpose |
| The same items listed in several places: an enum and a map of its labels, routes and a menu, an asset folder and the manifest that declares it | Updates the list it saw | Derive the others from one list. Where one cannot be derived, make the build or a test fail when they disagree |

An exhaustive match over an enum or a closed set of types is the cheapest derivation a typed
language offers: add a case, and the compiler names every place that has not handled it. Where the
language cannot check exhaustiveness, a test that walks every case does the same job.

The second row is [subtract-before-you-add](subtract-before-you-add.md) seen from the other side:
that file is about not adding the fourth version, this one about why the third one keeps spreading.

## When it applies

While sketching a change, ask of each piece of state and each task it introduces: who owns it, and
is there already a way to do it? While reviewing, look for a change that adds a second writer, a
second way or a second list. Either one is cheaper to fix now than after an agent has copied it.
