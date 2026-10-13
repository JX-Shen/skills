---
name: briefing
description: "Produce a briefing for a named non-technical decider: a decision document that asks them to ratify a design with its cost stated, a progress or stage report that says where the work stands and what continuing costs, or a review of a delivery they must accept or reject. Use when the user wants a memo, brief, board paper, progress report, status update, stage report, delivery review, or any document, HTML page, or PDF for management, an executive, a PM, a boss, or a client; when they say 汇报, 阶段汇报, 进展汇报, 汇报稿, 给老板看, 给老板写, 报告给管理层, 验收报告; or when they want an existing briefing re-released or re-cut."
---

<what-to-do>

A briefing **ratifies**. It asks a named human to confirm a design that is already reasoned, and it states what that design costs. It never sells. Every step below serves that.

The same discipline covers the other two documents a decider receives. A **progress report** asks them to ratify continuing: the essence is where the work stands and what the next stage costs. A **delivery review** asks them to ratify acceptance or rejection of something handed over: the essence is what was delivered against what was asked, and what accepting it costs. Both carry a cost sentence, both open with the summary, both are built, rendered and released the same way.

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

Read [`MECHANICS.md`](MECHANICS.md): the directory, the renderer and its media, the page-check loop, and the release rule. Read [`SHAPE.md`](SHAPE.md) for the section order of the kind you are writing and the rule that every number traces to a figure or a citation.

Settle the medium with the channel from step 2: HTML for a page the reader opens and scrolls, Markdown for an issue comment or a chat post, Word for a reader who edits, PDF for a reader who prints or files. One `brief.md` renders to all of them; pick what will actually be sent and look at that.

## 4. Write the brief, summary last

The summary is the section that comes back for rework; the body usually survives untouched. Read [`SUMMARY-SECTION.md`](SUMMARY-SECTION.md) before writing it.

Across the whole document, carry three things **together**: a strong recommendation, the honest disadvantages *of the option you recommend*, and an explicit hand-over of the decision. Drop the disadvantages and it is a sale; drop the recommendation and it is an abdication.

## 5. Render, then look at every page as an image

Orphaned headings, split tables, a legend sitting on a label and overflowing URLs live in the pixels, not in the Markdown. Read every page of every medium that will be sent, every render. When the page is wrong, the renderer in `scripts/briefkit/` changes, not `brief.md`.

## 6. Lint, then cold-read, before the user sees a draft

The build runs `scripts/briefkit/lint.py` first and refuses a brief whose shape is off: summary not first or too long, a number with no figure or citation, a section out of the order [`SHAPE.md`](SHAPE.md) sets for the kind, a phrase that dresses up a position. Fix every line it names.

Then run the cold read in [`agents/cold-read.md`](agents/cold-read.md): a fresh subagent plays the reader from step 2 and answers three questions from the rendered medium alone. A miss on the first question sends you back to step 1, not to the wording. Only a draft that has passed both goes to the user.

**Done when** the lint prints `shape ok` and the cold read's three answers are in the README with what changed.

## 7. Release only what the user approved

The user approves the content *and* the rendered pages of each medium that will be sent. Then cut a date-stamped file per medium and treat it as immutable: corrections are a new date, never an overwrite.

## 8. Ratchet every confirmation into the README

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
