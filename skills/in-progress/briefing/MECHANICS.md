# Mechanics

## The directory

One directory per briefing, holding every version of it:

```
<scratch>/briefings/READER-<name>.md       the reader model: what one reader accepts, in every channel
<scratch>/briefings/YYYY-MM-DD-<brief-name>/
  brief.md                       the single content source: all wording lives here
  figures.py                     the figures, as code reading the evidence (only when the brief uses @figure)
  README.md                      cold-start guide, and the ratchet
  speaking-notes.md              only when the document supplements a spoken ask; never distributed
  out/                           the current unapproved renders: work.html, work.md, work.gh.html, work.docx, work.pdf, figures/
  YYYY-MM-DD-<Name>.<ext>        a release; immutable
```

Both levels are date-stamped, and the two dates mean different things. The **directory** date is when the briefing was started, and it never changes: the directory is a stable path that later releases are cut inside. Each **release** date is when that version was approved and sent. So a briefing begun in August and re-released in October keeps its August directory and gains an October file beside the first one. Sorting `briefings/` therefore lists briefings in the order they were taken up.

Put `briefings/` where the repo already keeps generated, uncommitted material: a gitignored scratch directory if one exists. Match the existing convention; if there is none, choose somewhere sensible and say where. Releases are archived in the directory, not in repository history.

Three rules make the directory work, and all three are load-bearing:

- **`brief.md` is the only place wording lives.** Never edit a rendered file, never keep a second copy of the prose.
- **The renderers own all layout.** No layout instructions in the Markdown beyond the small directive set below. When something looks wrong on the page, the renderer in `scripts/briefkit/` is what changes, and every briefing after it gets the fix.
- **Figures are code reading evidence.** `figures.py` registers each `@figure` name as a function of the evidence root; no number on a figure is typed in.

## The renderer

`scripts/briefkit/build.py` parses `brief.md` once and renders it to every medium asked for. It reads a deliberately small Markdown subset; the parts worth knowing before you write `brief.md`:

- Front matter `--- key: value ---` builds the cover. Keys are dropped when absent, so the cover carries only what you set. `cover: title` keeps only the title, for a host that already shows sender and date (an issue comment, a chat post). `repo: owner/name` gives the `gh` medium its context. `kind:` names the document kind (`decision`, `progress`, `review`) for the lint; `evidence:` names the directory figures read from, relative to `brief.md`.
- `#` is a section heading, `##` a subheading, `- ` a bullet, `> ` a small muted note (used for reference URLs), `|` a table, ``` a monospace block.
- `[evidence: <file> <key>]` and `[run: <name>]` are citation tags. Put one in every block that states a number; every medium renders them small and muted.
- `@figure <name>` draws a figure registered in `figures.py`. Figures are **code, not Markdown**: write a function that takes the evidence loader and returns a matplotlib `Figure`, and decorate it with `@figure("<name>")`. HTML and Markdown get SVG; PDF and Word get PNG.
- `@pagebreak` forces a break in paged media (PDF, Word) and is ignored elsewhere. Use it when a block reads badly split, not to tune whitespace.
- `@diagram <name>` is PDF-only, for a hand-drawn reportlab Flowable registered with `@diagram("<name>")`. A brief that uses it cannot ship to another medium; prefer `@figure`.
- The PDF layout binds a run of headings, and any paragraph that is nothing but bold text such as `**Advantages.**`, to the block that follows, so nothing is left stranded at the foot of a page.

Environment, once per skill checkout (not per briefing), from this skill's directory:

```bash
uv venv .venv
uv pip install --python .venv/bin/python reportlab pypdfium2 pillow matplotlib python-docx
```

Then, to render from the briefing directory (`$BRIEFING` is this skill's path):

```bash
$BRIEFING/.venv/bin/python $BRIEFING/scripts/briefkit/build.py brief.md --to html,md,docx,pdf
```

Outputs land in `out/`. `--to gh` writes `work.md` and `work.gh.html`: the Markdown sent through GitHub's own renderer (`gh api -X POST /markdown`, mode gfm, the repo as context) inside github-markdown-css. That page is how an issue or PR comment is reviewed, because briefkit's HTML is not what GitHub shows; the comment posted is still `work.md`. It needs `gh` signed in. The build runs the shape lint first and refuses a brief that fails it; `--no-lint` exists for drafting and never for a file that reaches the reader. `examples/spmo-replication/` is a complete directory to copy from.

`scripts/md_to_pdf.template.py` is the earlier single-file PDF renderer and still works for a briefing that copied it; `briefkit` renders the same pages (`scripts/briefkit/check_pdf_parity.py` proves it pixel for pixel).

## Look at every page

A briefing's defects are visual in every medium. Render each page and read it as an image:

```bash
# PDF: one PNG per page
$BRIEFING/.venv/bin/python -c "
import pypdfium2 as pdfium
pdf = pdfium.PdfDocument('out/work.pdf')
for i in range(len(pdf)):
    pdf[i].render(scale=1.6).to_pil().save(f'pg{i+1}.png')
print(len(pdf), 'pages')"

# HTML: one tall screenshot (Chrome, Brave or Chromium)
"/Applications/Brave Browser.app/Contents/MacOS/Brave Browser" --headless --disable-gpu --hide-scrollbars \
  --window-size=1000,2600 --screenshot=page.png "file://$PWD/out/work.html"
# an issue or PR comment: the same screenshot of out/work.gh.html
```

Look at all of them, every time. What only the pixels show: a heading stranded at a page foot, a table splitting without repeating its header, a figure legend sitting on a label, a long URL past the right margin, a summary that has spilled onto a second page or below the first screen. Delete the PNGs afterwards.

Record the expected page count and where the set pieces land in the `README.md`, so the next render is checked against something.

## Releasing

A release happens only after the user approves both the content of `brief.md` and the rendered pages, in each medium that will be sent.

```bash
cp out/work.html $(date +%Y-%m-%d)-<Name>.html     # and the same for .pdf, .docx, .md as sent
```

A released file is **immutable**: it has been sent, and it is the record. A correction is a new date-stamped release beside it, never an overwrite.

Put no signature block in any medium. The durable record of approval belongs in the tracker or decision record that owns the decision; the briefing is what those cite.

## The reader model

`READER-<name>.md` sits beside the briefing directories, in the repo the work belongs to, because a reader belongs to a project and not to this skill. It answers the questions of step 1 in `SKILL.md` (who they are, voice, lead, the ask, structure, register, silences), each with its date, its reason, and the document or correction it came from. The agent keeps it: step 1 builds or refreshes it by grilling itself against the evidence, and step 8 writes each confirmed reader rule into it.

A rule in the model changes only by the user's correction, never by a lint message or a template. When the two disagree, the model wins and the conflict goes to the user, so the skill can learn from it.

## The README is the ratchet

Every briefing directory carries a `README.md` written so that an agent with no memory of the conversation can produce a correct new version from it alone. It holds:

- **The essence sentence, first**, with the principles that follow from it.
- The reader model it follows, and only the rules particular to this document, with their reasons.
- The section structure, and which parts of it are load-bearing rather than incidental.
- Environment, render, page-check, and release commands.
- The directive set and its gotchas, and which media were sent.
- The cold read's three answers for each version, and what changed because of them.
- Facts that were checked, with where they were checked, and the wording that was **rejected**: a wrong claim tends to grow back in the same spot.

Add to it every time the user confirms something. That is what stops the next editing pass from undoing a decision already made.
