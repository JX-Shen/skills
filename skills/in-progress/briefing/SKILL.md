---
name: briefing
description: Produce a decision briefing that asks a named non-technical audience to ratify a design, with its cost stated. Use when the user wants a memo, brief, board paper, or decision document for management, an executive, or a client, or wants an existing briefing re-released.
---

<what-to-do>

A briefing **ratifies**. It asks a named human to confirm a design that is already reasoned, and it states what that design costs. It never sells. Every step below serves that.

## 1. Settle the essence before drafting a word

Write the design as **one sentence carrying its own cost**:

> A multi-account AWS design: higher maintenance, in exchange for a higher standard.

Show that sentence to the user and get it confirmed. A cost-free sentence is a pitch, not an essence — if no cost appears in it, keep looking.

**Done when** the user has confirmed the sentence. Draft nothing before that.

## 2. Settle the three things the essence leaves open

- **Audience.** Who reads it, and which vocabulary lands. An accounting reader takes *preventive control*, *line item*, *one invoice*, and stops reading at IAM, bucket, CDK. Ask when it is not obvious from the repo.
- **Channel.** Is this document the whole ask, or the supplement to a spoken one? A supplement still stands alone — the reader six months from now was never in the room — and it also earns a `speaking-notes.md`.
- **What the reader already owns.** Prior briefs, diagrams, decisions. That material is the cheapest opening available: they have already paid for it.

## 3. Build the artefact

Read [`MECHANICS.md`](MECHANICS.md): the directory, the renderer, the page-check loop, and the release rule.

## 4. Write the brief, summary last

The summary is the section that comes back for rework; the body usually survives untouched. Read [`SUMMARY-SECTION.md`](SUMMARY-SECTION.md) before writing it.

Across the whole document, carry three things **together**: a strong recommendation, the honest disadvantages *of the option you recommend*, and an explicit hand-over of the decision. Drop the disadvantages and it is a sale; drop the recommendation and it is an abdication.

## 5. Render, then look at every page as an image

Orphaned headings, split tables, colliding diagram labels and overflowing URLs live in the pixels, not in the Markdown. Read every page, every render.

## 6. Release only what the user approved

The user approves the content *and* the rendered pages. Then cut a date-stamped file and treat it as immutable — corrections are a new date, never an overwrite.

## 7. Ratchet every confirmation into the README

Each time the user corrects the essence, the order, the voice, or the register, write the confirmed principle into the briefing directory's `README.md` as a rule with its reason. The README is a **ratchet**: it turns one way, so a later edit cannot quietly undo a decision the user already made.

Expect the essence itself to be corrected more than once. When it moves, **re-derive the summary from the new essence** rather than patching the old one — a summary whose weight sits on the wrong object cannot be fixed by tightening sentences.

</what-to-do>

<supporting-info>

## Why the essence gates everything

A reviewer who keeps rejecting the summary is not editing wording; they are testing whether the document knows what it is. Each answer to "what is this really about?" re-weights the entire front section — which thing is the object, which is downstream of it, what opens, what closes. Getting that sentence confirmed first is what makes the rest of the work survive review.

## Where this fits

- `/grilling` — stress-test the underlying decision *before* briefing anyone on it. A briefing communicates a decision; it does not make one.
- `/research` — gather the primary sources a briefing cites, so every claim traces to something.

</supporting-info>
