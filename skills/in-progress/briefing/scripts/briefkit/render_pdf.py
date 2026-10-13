"""Render parsed blocks to PDF. Owns every PDF layout decision.

This is the layout from `md_to_pdf.template.py`, reading blocks from
`briefkit.parse` instead of parsing itself, with `@figure` drawn as a scaled
image and `@diagram` drawn from the briefing's registered Flowable factories.
For a brief without figures the pages are pixel-identical to the template's.
"""

import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    Image,
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

from briefkit import figures as figlib
from briefkit.inline import inline_xml as inline
from briefkit.parse import is_heading_para

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


def make_figure(name, ctx):
    path = figlib.render_figure(name, "png", ctx.out_dir, ctx.evidence)
    img = Image(path)
    scale = BODY_W / img.imageWidth
    img.drawWidth = BODY_W
    img.drawHeight = img.imageHeight * scale
    return img


def block_flowables(kind, payload, ctx):
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
    if kind == "figure":
        return [Spacer(1, 6), make_figure(payload, ctx), Spacer(1, 8)]
    if kind == "diagram":
        name = payload or ""
        if name not in figlib.DIAGRAMS:
            raise SystemExit(
                f"@diagram {name!r} is not registered. Add it to figures.py "
                f"beside brief.md. Registered: {sorted(figlib.DIAGRAMS) or 'none'}")
        return [Spacer(1, 6), figlib.DIAGRAMS[name](), Spacer(1, 8)]
    return [Paragraph(inline(payload), body)]


def layout(blocks, ctx):
    """Flow the blocks, never stranding a heading at the foot of a page.

    A run of headings, and any paragraph that is nothing but bold text such as
    `**Advantages.**`, binds to the block that follows it: the whole table when a
    table follows, otherwise its first line.
    """
    def is_head(block):
        kind, payload = block
        return (kind in ("part", "section")
                or (kind == "para" and is_heading_para(payload)))

    flows, i, n = [], 0, len(blocks)
    while i < n:
        if not is_head(blocks[i]):
            flows += block_flowables(*blocks[i], ctx)
            i += 1
            continue
        group, j = [], i
        while j < n and is_head(blocks[j]):
            group += block_flowables(*blocks[j], ctx)
            j += 1
        rest = []
        if j < n:
            nxt = block_flowables(*blocks[j], ctx)
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
def render(fm, blocks, out_path, ctx):
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

    story += layout(blocks, ctx)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    doc.build(story)
    return out_path
