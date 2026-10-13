# Shape

What a briefing looks like before anyone reads a word of it. `scripts/briefkit/lint.py` checks the parts of this file that a script can check; the rest is yours.

## The reader

The reader decides and does not code. They will not open the repository; at most they will point their own agent at it. The first screen is what they read; everything after it is what they consult when a line on the first screen makes them stop. Write for that reader even when the document is also the record: the record survives because the first screen was understood.

## Three kinds, one order

Name the kind in the front matter (`kind: decision | progress | review`). Each kind has a fixed order of `#` sections, and the first is always the summary.

| Kind | Sections, in order | Essence sentence |
| --- | --- | --- |
| decision | Summary, the proposal, the alternative, the cost, the recommendation | the design, carrying its own cost |
| progress | Summary, where the work stands, the gaps, what comes next | where the work is, and what the next stage costs |
| review | Summary, what was delivered, findings, acceptance | what was delivered against what was asked, and what accepting it costs |

Headings may use other words; the lint matches by keyword (see `ORDER` in `lint.py`). Appendices follow the last section and are free in form.

## Good news, then gaps, then the plan

A progress report opens with what now works, then names what does not, then says what happens next. The gap section is where the reader learns the honest state; it is never folded into the good news as a qualifier, and never held back to the end as a confession.

A progress report tells the **evolution**, not the current state. "Two weeks ago the rules matched a third of the list; the rebalance check now matches all but three" is a report. "The rules match all but three" is a status line.

## Show, then tell

Where a number matters, the reader sees the thing counted before they read the count. A grid of every holding with the misses in red lets the reader count; "97 of 100" asks them to trust. Prose carries the story; figures carry the numbers; adjectives carry nothing.

Every figure is code in the briefing's `figures.py`, drawn from the evidence root named in the front matter. No number is typed into a figure, and no figure is kept that cannot be drawn from the evidence it cites.

## Every number traces

A number in prose carries a citation tag in the same block, or sits within two blocks of the `@figure` that shows it:

```
[evidence: figures-data.json stats]     a file under the evidence root, and the key
[run: 2026-10-07-l1-15-recut2]          a named run whose outputs hold the figure
```

Years and dates are exempt. Every medium renders the tag small and muted; the lint reads it. A number with neither is a number the reader cannot check, and the lint stops the build on it.

## The first screen

The summary fits one page in PDF and one screen in HTML: at most 25 non-blank source lines. It carries the cost of the recommended path in plain words, and it says when the money is unchanged, because a reader with an accounting background collapses labour into spend unless told otherwise. It carries the recommendation (or, for a review, accept or reject) so a reader who stops here leaves with the decision. `SUMMARY-SECTION.md` gives the internal order.

## Words that dress up a position

A problem list states the position. These phrases hide it, and the lint flags them:

- "done with caveat": a failed check keeps its objective open; name the gap and who acts.
- "inherent", "not fixable": needs a measurement that shows it, not an explanation.
- "no such notice found": an absence found by search is unverified; say what was searched and when.
- "we recommend": one author, first person singular.
- "you're absolutely right", "it's worth noting": filler and performative agreement.

Severity follows the effect on the result, not who must fix it. A gap caused by our own construction choice stays ours until the choice has actually been put to the reader. Owner means who acts next; "Phase 2", "information" or a title is not an owner.

## The two tables for management

When the document asks the reader to accept a departure from a rule, or to take a decision, use these tables as the appendix format. They present a choice; the rules and their authority stay in the specifications and decision records, and every figure in them comes from a named run.

Deviation table, one row per departure from the reference rule in force:

| Deviation | Rule it departs from | Measured effect | Status | Consequence |
| --- | --- | --- | --- | --- |
| what was done differently | the clause or record | the effect, naming its run; "unmeasured" when it was not measured | ratified (cite the record), provisional, or declared by the run | what follows if it stands |

Recommendation table, one row per decision requested:

| Recommendation | Expected effect | Basis | Cost and time | Decider |
| --- | --- | --- | --- | --- |
| the action | what changes if taken | measured or estimated; an estimate names what it rests on | effort and calendar | the person who must say yes, never who does the work |

Flag the rows a reader would not expect.
