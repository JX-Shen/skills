"""Render parsed blocks to Word (.docx) for the reader who edits in Word.

Built with python-docx on the default template, so the file opens cleanly in
Word, Pages and Google Docs. Styles mirror the PDF palette; figures go in as
PNG at the body width.
"""

import os

from docx import Document
from docx.enum.text import WD_BREAK
from docx.shared import Cm, Pt, RGBColor

from briefkit import figures as figlib
from briefkit.inline import inline_runs, is_heading_para_text

META_LINES = [("To", "to"), ("From", "author"), ("Date", "date"),
              ("Scope", "scope"), ("Distribution", "distribution")]

INK = RGBColor(0x1A, 0x1A, 0x1A)
ACCENT = RGBColor(0x1F, 0x3A, 0x5F)
MUTE = RGBColor(0x5A, 0x64, 0x72)
BODY_W_CM = 16.2


def _runs(paragraph, text, size=None, colour=None):
    for chunk, bold, italic, muted in inline_runs(text):
        run = paragraph.add_run(chunk)
        run.bold = bold or None
        run.italic = italic or None
        if muted:
            run.font.size = Pt(7.5)
            run.font.color.rgb = MUTE
        else:
            if size:
                run.font.size = Pt(size)
            if colour is not None:
                run.font.color.rgb = colour
    return paragraph


def render(fm, blocks, out_path, ctx):
    doc = Document()
    section = doc.sections[0]
    section.left_margin = section.right_margin = Cm(2.4)
    section.top_margin, section.bottom_margin = Cm(2.2), Cm(2.1)
    normal = doc.styles["Normal"]
    normal.font.name = "Helvetica"
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = INK

    # Cover
    if fm.get("org"):
        p = doc.add_paragraph()
        r = p.add_run(fm["org"])
        r.bold, r.font.size, r.font.color.rgb = True, Pt(10), MUTE
    p = doc.add_paragraph()
    r = p.add_run(fm.get("title", ""))
    r.bold, r.font.size, r.font.color.rgb = True, Pt(26), ACCENT
    if fm.get("subtitle"):
        p = doc.add_paragraph()
        r = p.add_run(fm["subtitle"])
        r.font.size = Pt(13)
    for label, key in META_LINES:
        if fm.get(key):
            p = doc.add_paragraph()
            r = p.add_run(f"{label}: {fm[key]}")
            r.font.size, r.font.color.rgb = Pt(10), MUTE
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    for kind, payload in blocks:
        if kind == "part":
            p = doc.add_heading(level=1)
            r = p.add_run(payload)
            r.font.color.rgb, r.font.size = ACCENT, Pt(15)
        elif kind == "section":
            p = doc.add_heading(level=2)
            r = p.add_run(payload)
            r.font.color.rgb, r.font.size = INK, Pt(12)
        elif kind == "bullets":
            for item in payload:
                _runs(doc.add_paragraph(style="List Bullet"), item)
        elif kind == "note":
            _runs(doc.add_paragraph(), payload, size=8, colour=MUTE)
        elif kind == "table":
            rows = payload
            width = max(len(r) for r in rows)
            t = doc.add_table(rows=len(rows), cols=width)
            t.style = "Table Grid"
            for i, row in enumerate(rows):
                for j in range(width):
                    cell = t.cell(i, j)
                    cell.text = ""
                    text = row[j] if j < len(row) else ""
                    para = cell.paragraphs[0]
                    _runs(para, text, size=9, colour=ACCENT if i == 0 else None)
                    if i == 0:
                        for run in para.runs:
                            run.bold = True
            doc.add_paragraph()
        elif kind == "code":
            p = doc.add_paragraph()
            r = p.add_run(payload)
            r.font.name, r.font.size = "Menlo", Pt(8)
        elif kind == "pagebreak":
            doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        elif kind == "figure":
            path = figlib.render_figure(payload, "png", ctx.out_dir, ctx.evidence)
            doc.add_picture(path, width=Cm(BODY_W_CM))
        elif kind == "diagram":
            raise SystemExit("@diagram is PDF-only; use @figure for docx")
        else:
            p = doc.add_paragraph()
            if is_heading_para_text(payload):
                p.paragraph_format.keep_with_next = True
            _runs(p, payload)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    doc.save(out_path)
    return out_path
