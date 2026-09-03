# ADR Format

ADRs live in `docs/adr/` and use sequential numbering: `0001-slug.md`, `0002-slug.md`, etc.

Create the `docs/adr/` directory lazily: only when the first ADR is needed.

## Template

```md
# {Short title of the decision}

{1-3 sentences: what's the context, what did we decide, and why.}
```

That's it. An ADR can be a single paragraph. The value is in recording *that* a decision was made and *why*, not in filling out sections.

## Optional sections

Only include these when they add genuine value. Most ADRs won't need them.

- **Status** frontmatter (`proposed | accepted | deprecated`): useful when decisions are revisited
- **Considered Options**: only when the rejected alternatives are worth remembering
- **Consequences**: only when non-obvious downstream effects need to be called out

## What an ADR holds

An ADR records a design conclusion and the reasoning for it **on design grounds alone**, and it
treats the conclusion as settled. Everything it cites is reproducible from the repository: a
quantity the argument needs is inlined, a reference points at a tracked file, and a question the
repository cannot close is named by the issue that owns it.

The **tracker** holds the rest, anything whose state lives outside git:

- approval or ratification by anyone ("confirmed by management", "awaiting sign-off")
- provisioning state ("three of the four accounts exist", "waits on a mailbox")
- identifiers that belong to an external system: email addresses, account numbers, URLs into
  ignored scratch directories
- compliance, legal or residency verdicts that only a person outside the repository can give

When such a question bears on the design, the ADR states the design choice, names the issue that
escalates the question, and says what would change if the answer went the other way. When the
outside decision later changes the design, amend the ADR then, and that amendment *is* the history.
The `Status` frontmatter above tracks the decision's own lifecycle inside the repository, not any
external approval.

## Match the repo before you match this template

Where `docs/adr/` already holds records, they are the format: a length, a set of
sections, a title style, a voice. Follow them. This file is the default for a repo
that has not decided; it never overrides one that has, and a repo whose ADRs are
all dense argued records is not served by a one-paragraph addition to them.

## Amend, don't supersede

An ADR found to be wrong is corrected in place, and records inside itself what
changed and why. Do not open a new ADR saying "supersedes ADR-000N": the argument
then lives in two files and a reader has to find both to know what holds. A new
number is for a subject that has genuinely split, never for a second opinion
about an old one.

An amendment is worth as much as the decision it corrects, and is written the
same way: say what the earlier reasoning got wrong, not only what the conclusion
now is.

## What a record keeps

"Considered Options" is not the whole of the reasoning worth keeping. Three
things get dropped routinely and are the hardest to recover afterwards:

- **An argument that was overturned, even where its conclusion survived.** If the
  first reason for a boundary turned out not to imply it and a different reason
  did, write both down. Otherwise a later reader concludes the line was drawn for
  whichever reason now looks obvious, and moves it.
- **A mistake that explains the design.** A shape that exists because a simpler
  one was tried and failed reads as arbitrary once the simpler one is forgotten.
- **What was deliberately not modelled.** A distinction you saw, weighed and left
  out is a decision. Unwritten, it looks like an oversight, and someone
  eventually "fixes" it.

None of the three is a rejected alternative in the ordinary sense: they are
reasoning that was tried rather than options that were on the table. Each is also
unrecoverable after the fact, including by whoever decided it, which is what
makes writing them down at the time the only chance.

This applies to a **Decision** comment on an issue as much as to an ADR.

## Numbering

Scan `docs/adr/` for the highest existing number and increment by one.

## When to offer an ADR

All three of these must be true:

1. **Hard to reverse**: the cost of changing your mind later is meaningful
2. **Surprising without context**: a future reader will look at the code and wonder "why on earth did they do it this way?"
3. **The result of a real trade-off**: there were genuine alternatives and you picked one for specific reasons

If a decision is easy to reverse, skip it: you'll just reverse it. If it's not surprising, nobody will wonder why. If there was no real alternative, there's nothing to record beyond "we did the obvious thing."

### What qualifies

- **Architectural shape.** "We're using a monorepo." "The write model is event-sourced, the read model is projected into Postgres."
- **Integration patterns between contexts.** "Ordering and Billing communicate via domain events, not synchronous HTTP."
- **Technology choices that carry lock-in.** Database, message bus, auth provider, deployment target. Not every library: just the ones that would take a quarter to swap out.
- **Boundary and scope decisions.** "Customer data is owned by the Customer context; other contexts reference it by ID only." The explicit no-s are as valuable as the yes-s.
- **Deliberate deviations from the obvious path.** "We're using manual SQL instead of an ORM because X." Anything where a reasonable reader would assume the opposite. These stop the next engineer from "fixing" something that was deliberate.
- **Constraints not visible in the code.** "We can't use AWS because of compliance requirements." "Response times must be under 200ms because of the partner API contract."
- **Rejected alternatives when the rejection is non-obvious.** If you considered GraphQL and picked REST for subtle reasons, record it; otherwise someone will suggest GraphQL again in six months.
