# Model the domain in types

Where a rule lives in a type, code that breaks it does not compile. Where it lives in a runtime
check, a comment, or the reader's memory, it is broken eventually and found in production.

Most typed languages have the pieces for this: closed sets of types (sealed classes, tagged
unions), exhaustive matching, non-null by default, and cheap wrapper types. This is about using them
for the domain rather than only for the plumbing. The examples below are pseudo-code; the project's
language spells them its own way.

## Make invalid states unrepresentable

The most common version of this in an app is a state class where the status and the data disagree:

```
// Every combination is expressible, including the wrong ones
OrderState {
  status: initial | loading | success | failure
  order: Order or nothing           // nothing when successful?
  errorMessage: String or nothing   // set when successful?
}
```

Three fields, twenty-plus combinations, a handful of them meaningful. Every reader that
force-unwraps `order` is trusting a rule nothing enforces, and one of them will be wrong.

Tie the data to the state that carries it:

```
OrderState is exactly one of:
  Initial
  Loading
  Loaded(order: Order)        // never missing here
  Failed(failure: Failure)    // never missing here
```

Now `order` exists exactly where it is meaningful, no unwrap is needed, and an exhaustive match
makes a fifth state a compile error in every consumer rather than a silent fallthrough.

**The tradeoff is real.** A status enum plus a copy-with-changes helper is less code and easier to
extend one field at a time, which is why it is a common template default. Reach for the closed set
when the states genuinely carry different data, or when you find yourself force-unwrapping to get
at a field.

## Parse at the boundary, then trust

Validate once where data enters, convert to a type that cannot be wrong, and stop checking:

```
// Checked in eleven places, guaranteed nowhere
sendReceipt(email: String):
  if email does not contain "@": return
  ...

// Checked once, guaranteed everywhere
type Email wraps String
Email.tryParse(raw: String) -> Email or nothing:
  return raw contains "@" ? Email(raw) : nothing

sendReceipt(email: Email):
  ...                         // no check needed
```

An `Email` parameter cannot receive an unvalidated string, so the eleven checks collapse to one and
the compiler enforces the rest.

## Give a primitive its meaning

`userId: String, orderId: String` accepts them in the wrong order and compiles. Two wrapper types
over a string do not. This is worth doing for ids that get passed together, money, and anything
where a unit is implied but unstated, such as a duration versus an integer of unknown units.

## Do not over-apply it

A wrapper type per field makes reading worse for no safety gain. Reach for this where **a wrong
value is actually possible and would be costly**: identifiers that get transposed, money, states
carrying conditional data, values arriving from a network or a user. A local variable in a
twelve-line function needs none of it.

Beyond this, the project's `CLAUDE.md` already sets its floor on loose types, and `code-review`
already flags an unchecked cast off a network payload. Those are the floor, not this principle.
