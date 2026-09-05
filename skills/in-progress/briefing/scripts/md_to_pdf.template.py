"""Render a briefing's brief.md to PDF. Copy this beside brief.md as md_to_pdf.py.

`brief.md` is the single content source; this script owns every layout decision.
Keep it that way: when the page looks wrong, this file changes, not the Markdown.

The Markdown subset, and nothing beyond it:

    --- key: value ---   front matter, builds the title page (absent keys are dropped)
    # Heading            numbered section heading, with a rule under it
    ## Heading           subheading
    - item               bullet (continuation lines indented two spaces)
    > note               small muted line, for reference URLs and asides
    | a | b |            table (first row is the header, and it repeats on a split)
    ```                  fenced block, rendered monospace in a tinted box
    **bold** *italic*    inline emphasis
    @pagebreak           forced page break
    @diagram <name>      a figure registered in DIAGRAMS below

Diagrams are code, not Markdown. Register a Flowable factory in DIAGRAMS and draw
at fixed coordinates in cm; after any coordinate change, re-render and look at the
page, because labels collide silently.

Setup, once:
    python3 -m venv .venv && .venv/bin/pip install reportlab pypdfium2 pillow
Render:
    .venv/bin/python md_to_pdf.py brief.md work.pdf
"""

import re
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    HRFlowable,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)

# ---------------------------------------------------------------- page and palette
PAGESIZE = A4
MARGIN_X = 2.4 * cm
MARGIN_TOP = 2.2 * cm
MARGIN_BOTTOM = 2.1 * cm
BODY_W = PAGESIZE[0] - 2 * MARGIN_X          # usable width; tables are keyed to it

INK = colors.HexColor("#1a1a1a")
ACCENT = colors.HexColor("#1f3a5f")
MUTE = colors.HexColor("#5a6472")
RULE = colors.HexColor("#c9cfd6")
SHADE = colors.HexColor("#eef1f5")

# Title-page meta block: (label, front-matter key), in order. Absent keys are skipped.
META_LINES = [("To", "to"), ("From", "author"), ("Date", "date"),
              ("Scope", "scope"), ("Distribution", "distribution")]

# Table column widths in cm, keyed by column count. Unlisted counts split evenly.
WIDTHS = {
    2: [3.6, 12.6],
    3: [4.0, 6.1, 6.1],
    4: [2.9, 5.1, 4.9, 3.3],
}

# ---------------------------------------------------------------- styles
body = ParagraphStyle("body", fontName="Helvetica", fontSize=10, leading=15,
                      textColor=INK, alignment=TA_LEFT, spaceAfter=7)
bullet = ParagraphStyle("bullet", parent=body, leftIndent=0.55 * cm,
                        bulletIndent=0.1 * cm, spaceAfter=5)
note = ParagraphStyle("note", parent=body, fontSize=7, leading=10,
                      textColor=MUTE, leftIndent=0.55 * cm, spaceAfter=7)
cell = ParagraphStyle("cell", parent=body, fontSize=9, leading=13, spaceAfter=0)
cellb = ParagraphStyle("cellb", parent=cell, fontName="Helvetica-Bold",
                       textColor=ACCENT)
h_part = ParagraphStyle("h_part", fontName="Helvetica-Bold", fontSize=15,
                        leading=19, textColor=ACCENT, spaceBefore=16, spaceAfter=4)
h_sec = ParagraphStyle("h_sec", fontName="Helvetica-Bold", fontSize=11.5,
                       leading=15, textColor=INK, spaceBefore=13, spaceAfter=5)
meta = ParagraphStyle("meta", fontName="Helvetica", fontSize=10.5, leading=17,
                      textColor=MUTE)
t_title = ParagraphStyle("t_title", fontName="Helvetica-Bold", fontSize=30,
                         leading=36, textColor=ACCENT)
t_sub = ParagraphStyle("t_sub", fontName="Helvetica", fontSize=14, leading=19,
                       textColor=INK, spaceBefore=8)
t_org = ParagraphStyle("t_org", fontName="Helvetica-Bold", fontSize=11,
                       leading=14, textColor=MUTE)


def _mono_font():
    """A monospace face with box-drawing glyphs; built-in Courier lacks them."""
    for path in ("/System/Library/Fonts/Menlo.ttc",
                 "/System/Library/Fonts/Monaco.ttf"):
        try:
            pdfmetrics.registerFont(TTFont("Mono", path, subfontIndex=0))
            return "Mono"
        except Exception:
            continue
    return "Courier"


MONO = _mono_font()
mono = ParagraphStyle("mono", fontName=MONO, fontSize=8, leading=12, textColor=INK)


# ---------------------------------------------------------------- diagrams
# Register one entry per `@diagram <name>` used in brief.md. Delete the example.
#
#     class Topology(Flowable):
#         def __init__(self, width=BODY_W):
#             super().__init__()
#             self.width, self.height = width, 9 * cm
#
#         def draw(self):
#             c = self.canv
#             c.setStrokeColor(ACCENT)
#             c.roundRect(0, 2 * cm, 7 * cm, 5 * cm, 6, stroke=1, fill=0)
#             c.setFillColor(INK)
#             c.setFont("Helvetica-Bold", 8)
#             c.drawString(0.3 * cm, 6.4 * cm, "one account")
#
#     DIAGRAMS = {"topology": Topology}

DIAGRAMS = {}


# ---------------------------------------------------------------- parsing
def inline(text):
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)
    return text


def parse_front_matter(lines):
    fm, i = {}, 0
    if lines and lines[0].strip() == "---":
        i = 1
        while i < len(lines) and lines[i].strip() != "---":
            if ":" in lines[i]:
                k, v = lines[i].split(":", 1)
                fm[k.strip()] = v.strip()
            i += 1
        i += 1
    return fm, lines[i:]


def parse_blocks(lines):
    """Yield (kind, payload) for the documented Markdown subset."""
    i, n = 0, len(lines)
    while i < n:
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue
        if line.startswith("## "):
            yield "section", line[3:].strip()
            i += 1
        elif line.startswith("# "):
            yield "part", line[2:].strip()
            i += 1
        elif line.strip() == "@pagebreak":
            yield "pagebreak", None
            i += 1
        elif line.strip().startswith("@diagram"):
            yield "diagram", line.strip()[len("@diagram"):].strip()
            i += 1
        elif line.startswith("```"):
            i += 1
            code = []
            while i < n and not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            yield "code", "\n".join(code)
        elif line.startswith("> "):
            yield "note", line[2:].strip()
            i += 1
        elif line.startswith("- "):
            items = []
            while i < n and lines[i].rstrip().startswith("- "):
                item = lines[i].rstrip()[2:]
                i += 1
                while i < n and lines[i].startswith("  ") and lines[i].strip():
                    item += " " + lines[i].strip()
                    i += 1
                items.append(item)
            yield "bullets", items
        elif line.startswith("|"):
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            yield "table", rows
        else:
            para = [line.strip()]
            i += 1
            while i < n and lines[i].strip() and not re.match(r"(#|-\s|\||>\s|@)",
                                                             lines[i]):
                para.append(lines[i].strip())
                i += 1
            yield "para", " ".join(para)


# ---------------------------------------------------------------- flowables
def make_table(rows):
    ncols = len(rows[0])
    default = [BODY_W / cm / ncols] * ncols
    widths = [w * cm for w in WIDTHS.get(ncols, default)]
    data = [[Paragraph(inline(c), cellb) for c in rows[0]]]
    data += [[Paragraph(inline(c), cell) for c in row] for row in rows[1:]]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), SHADE),
        ("GRID", (0, 0), (-1, -1), 0.5, RULE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def make_code(payload):
    box = Table([[Preformatted(payload, mono)]], colWidths=[BODY_W])
    box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SHADE),
        ("BOX", (0, 0), (-1, -1), 0.5, RULE),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    return box


def block_flowables(kind, payload):
    if kind == "part":
        return [Paragraph(inline(payload), h_part), Spacer(1, 2),
                HRFlowable(width="100%", thickness=0.7, color=RULE, spaceAfter=8)]
    if kind == "section":
        return [Paragraph(inline(payload), h_sec)]
    if kind == "bullets":
        return [Paragraph(inline(i), bullet, bulletText="–") for i in payload]
    if kind == "note":
        return [Paragraph(inline(payload), note)]
    if kind == "table":
        return [make_table(payload), Spacer(1, 9)]
    if kind == "code":
        return [make_code(payload), Spacer(1, 8)]
    if kind == "pagebreak":
        return [PageBreak()]
    if kind == "diagram":
        name = payload or ""
        if name not in DIAGRAMS:
            raise SystemExit(
                f"@diagram {name!r} is not registered. Add it to DIAGRAMS "
                f"in this script. Registered: {sorted(DIAGRAMS) or 'none'}")
        return [Spacer(1, 6), DIAGRAMS[name](), Spacer(1, 8)]
    return [Paragraph(inline(payload), body)]


def layout(blocks):
    """Flow the blocks, never stranding a heading at the foot of a page.

    A run of headings — and any paragraph that is nothing but bold text, such as
    `**Advantages.**` — binds to the block that follows it: the whole table when a
    table follows, otherwise its first line.
    """
    def is_head(block):
        kind, payload = block
        return (kind in ("part", "section")
                or (kind == "para" and re.fullmatch(r"\*\*[^*]+\*\*", payload)))

    flows, i, n = [], 0, len(blocks)
    while i < n:
        if not is_head(blocks[i]):
            flows += block_flowables(*blocks[i])
            i += 1
            continue
        group, j = [], i
        while j < n and is_head(blocks[j]):
            group += block_flowables(*blocks[j])
            j += 1
        rest = []
        if j < n:
            nxt = block_flowables(*blocks[j])
            if blocks[j][0] == "table":
                group += nxt
            else:
                group += nxt[:1]
                rest = nxt[1:]
            j += 1
        flows.append(KeepTogether(group))
        flows += rest
        i = j
    return flows


# ---------------------------------------------------------------- build
def build(md_path, out_path):
    with open(md_path, encoding="utf-8") as f:
        fm, lines = parse_front_matter(f.read().splitlines())

    footer_text = fm.get("footer", "Internal")

    def footer(canv, doc):
        canv.saveState()
        canv.setStrokeColor(RULE)
        canv.setLineWidth(0.5)
        canv.line(MARGIN_X, 1.55 * cm, PAGESIZE[0] - MARGIN_X, 1.55 * cm)
        canv.setFont("Helvetica", 8)
        canv.setFillColor(MUTE)
        canv.drawString(MARGIN_X, 1.15 * cm, footer_text)
        canv.drawRightString(PAGESIZE[0] - MARGIN_X, 1.15 * cm, f"Page {doc.page}")
        canv.restoreState()

    doc = BaseDocTemplate(
        out_path, pagesize=PAGESIZE, leftMargin=MARGIN_X, rightMargin=MARGIN_X,
        topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM,
        title=" — ".join(x for x in (fm.get("title"), fm.get("subtitle")) if x),
        author=fm.get("author", ""),
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
    doc.addPageTemplates([
        PageTemplate(id="title", frames=[frame]),
        PageTemplate(id="page", frames=[frame], onPage=footer),
    ])

    story = [Spacer(1, 4.2 * cm), Paragraph(fm.get("org", ""), t_org),
             Spacer(1, 0.5 * cm), Paragraph(fm.get("title", ""), t_title),
             Paragraph(fm.get("subtitle", ""), t_sub), Spacer(1, 1.6 * cm),
             HRFlowable(width="38%", thickness=1, color=RULE, hAlign="LEFT",
                        spaceAfter=14),
             Paragraph("<br/>".join(f"{label}: {fm[key]}"
                                    for label, key in META_LINES if fm.get(key)),
                       meta),
             NextPageTemplate("page"), PageBreak()]

    story += layout(list(parse_blocks(lines)))
    doc.build(story)
    print("written:", out_path)


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "brief.md",
          sys.argv[2] if len(sys.argv) > 2 else "work.pdf")
