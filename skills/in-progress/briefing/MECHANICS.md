# Mechanics

## The directory

One directory per briefing, holding every version of it:

```
<scratch>/briefings/YYYY-MM-DD-<brief-name>/
  brief.md                       the single content source — all wording lives here
  md_to_pdf.py                   the renderer — owns all layout
  README.md                      cold-start guide, and the ratchet
  speaking-notes.md              only when the PDF supplements a spoken ask; never distributed
  YYYY-MM-DD-<Name>.pdf          a release; immutable
  work.pdf                       the current unapproved render
```

Both levels are date-stamped, and the two dates mean different things. The **directory** date is when the briefing was started, and it never changes — the directory is a stable path that later releases are cut inside. Each **PDF** date is when that version was approved and sent. So a briefing begun in August and re-released in October keeps its August directory and gains an October PDF beside the first one. Sorting `briefings/` therefore lists briefings in the order they were taken up.

Put `briefings/` where the repo already keeps generated, uncommitted material — a gitignored scratch directory if one exists. Match the existing convention; if there is none, choose somewhere sensible and say where. Releases are archived in the directory, not in repository history.

Two rules make the directory work, and both are load-bearing:

- **`brief.md` is the only place wording lives.** Never edit the PDF, never keep a second copy of the prose.
- **The renderer owns all layout.** No layout instructions in the Markdown beyond the small directive set below. When something looks wrong on the page, the renderer is what changes.

## The renderer

Copy [`scripts/md_to_pdf.template.py`](scripts/md_to_pdf.template.py) into the directory as `md_to_pdf.py`. It parses a deliberately small Markdown subset and owns every layout decision. Its header documents the subset; the parts worth knowing before you write `brief.md`:

- Front matter `--- key: value ---` builds the title page. Keys are dropped when absent, so the cover carries only what you set.
- `#` is a numbered section heading, `##` a subheading, `- ` a bullet, `> ` a small muted note (used for reference URLs), `|` a table, ``` a monospace block.
- `@pagebreak` forces a break. Use it when a block reads badly split, not to tune whitespace.
- `@diagram <name>` draws a registered figure. Diagrams are **code, not Markdown**: register a `Flowable` in the `DIAGRAMS` dict at the top of the script and draw at fixed coordinates.
- `layout()` binds a run of headings — and any paragraph that is nothing but bold text, such as `**Advantages.**` — to the block that follows, so nothing is left stranded at the foot of a page.

Environment, once per directory:

```bash
python3 -m venv .venv
.venv/bin/pip install reportlab pypdfium2 pillow
```

Then, to render:

```bash
.venv/bin/python md_to_pdf.py brief.md work.pdf
```

## Look at every page

A briefing is a fixed-layout artefact, so its defects are visual. Render each page and read it as an image:

```bash
.venv/bin/python -c "
import pypdfium2 as pdfium
pdf = pdfium.PdfDocument('work.pdf')
for i in range(len(pdf)):
    pdf[i].render(scale=1.6).to_pil().save(f'pg{i+1}.png')
print(len(pdf), 'pages')"
```

Look at all of them, every time. What only the pixels show: a heading stranded at a page foot, a table splitting without repeating its header, a diagram label running outside its box, a long URL past the right margin, a summary that has spilled onto a second page. Delete the PNGs afterwards.

Record the expected page count and where the set pieces land in the `README.md`, so the next render is checked against something.

## Releasing

A release happens only after the user approves both the content of `brief.md` and the rendered pages.

```bash
mv work.pdf $(date +%Y-%m-%d)-<Name>.pdf
```

A released file is **immutable** — it has been sent, and it is the record. A correction is a new date-stamped release beside it, never an overwrite.

Put no signature block in the PDF. The durable record of approval belongs in the tracker or decision record that owns the decision; the briefing is what those cite.

## The README is the ratchet

Every briefing directory carries a `README.md` written so that an agent with no memory of the conversation can produce a correct new version from it alone. It holds:

- **The essence sentence, first**, with the principles that follow from it.
- Audience and voice rules, as rules with their reasons.
- The section structure, and which parts of it are load-bearing rather than incidental.
- Environment, render, page-check, and release commands.
- The renderer's directive set and its gotchas.
- Facts that were checked, with where they were checked, and the wording that was **rejected** — a wrong claim tends to grow back in the same spot.

Add to it every time the user confirms something. That is what stops the next editing pass from undoing a decision already made.
