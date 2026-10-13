"""Render parsed blocks to a single self-contained HTML file.

One file, inline CSS, figures inlined as SVG, no external requests: the page
opens from a mail attachment or a file share exactly as it was approved.
Tables sort on header click; that is the only script, and it is inline.
"""

import html
import os
import re

from briefkit import figures as figlib
from briefkit.inline import inline_html as inline

META_LINES = [("To", "to"), ("From", "author"), ("Date", "date"),
              ("Scope", "scope"), ("Distribution", "distribution")]

CSS = """
:root { --ink:#1a1a1a; --accent:#1f3a5f; --mute:#5a6472; --rule:#c9cfd6; --shade:#eef1f5; }
html { font-size: 16px; }
body { margin:0; color:var(--ink); background:#fff;
  font-family: -apple-system, "Helvetica Neue", Helvetica, Arial, sans-serif; line-height:1.55; }
main { max-width: 46rem; margin: 0 auto; padding: 2.5rem 1.5rem 4rem; }
header.cover { border-bottom: 1px solid var(--rule); padding-bottom: 1.5rem; margin-bottom: 2rem; }
header.cover .org { font-weight:700; color:var(--mute); font-size:.85rem; letter-spacing:.02em; }
header.cover h1 { color:var(--accent); font-size:2.2rem; line-height:1.15; margin:.4rem 0 .2rem; }
header.cover .subtitle { font-size:1.15rem; margin:0 0 1.2rem; }
header.cover .meta { color:var(--mute); font-size:.95rem; }
header.cover .meta span { display:block; }
h2 { color:var(--accent); font-size:1.35rem; margin:2.2rem 0 .4rem; padding-bottom:.25rem; border-bottom:1px solid var(--rule); }
h3 { font-size:1.05rem; margin:1.6rem 0 .4rem; }
p { margin:0 0 .8rem; }
ul { padding-left:1.3rem; margin:0 0 .8rem; }
li { margin:0 0 .3rem; }
p.note { color:var(--mute); font-size:.8rem; padding-left:1.3rem; word-break:break-all; }
.cite { color:var(--mute); font-size:.72rem; font-family: ui-monospace, Menlo, monospace; white-space:nowrap; }
table { border-collapse:collapse; width:100%; margin:0 0 1.2rem; font-size:.92rem; }
th, td { border:1px solid var(--rule); padding:.35rem .5rem; vertical-align:top; text-align:left; }
th { background:var(--shade); color:var(--accent); cursor:pointer; user-select:none; }
th[data-dir="asc"]::after { content:" \\25B4"; } th[data-dir="desc"]::after { content:" \\25BE"; }
pre { background:var(--shade); border:1px solid var(--rule); padding:.7rem .9rem; overflow:auto;
  font-size:.82rem; line-height:1.45; margin:0 0 1rem; }
figure { margin:1rem 0 1.4rem; }
figure svg { width:100%; height:auto; display:block; }
footer { margin-top:3rem; padding-top:.8rem; border-top:1px solid var(--rule); color:var(--mute); font-size:.8rem;
  display:flex; justify-content:space-between; }
@media print { main { max-width:none; padding:0; } h2 { page-break-after:avoid; } figure, table, pre { page-break-inside:avoid; } }
"""

JS = """
document.querySelectorAll('table').forEach(function (t) {
  var ths = t.querySelectorAll('th');
  ths.forEach(function (th, idx) {
    th.addEventListener('click', function () {
      var dir = th.dataset.dir === 'asc' ? 'desc' : 'asc';
      ths.forEach(function (o) { delete o.dataset.dir; });
      th.dataset.dir = dir;
      var rows = Array.prototype.slice.call(t.tBodies[0].rows);
      var num = function (s) { var v = parseFloat(String(s).replace(/[,%\\s]/g, '')); return isNaN(v) ? null : v; };
      rows.sort(function (a, b) {
        var x = a.cells[idx].textContent.trim(), y = b.cells[idx].textContent.trim();
        var nx = num(x), ny = num(y);
        var c = (nx !== null && ny !== null) ? nx - ny : x.localeCompare(y);
        return dir === 'asc' ? c : -c;
      });
      rows.forEach(function (r) { t.tBodies[0].appendChild(r); });
    });
  });
});
"""


def _svg_inline(path):
    with open(path, encoding="utf-8") as f:
        svg = f.read()
    # Drop the XML prolog and DOCTYPE so the SVG sits inline.
    svg = re.sub(r"<\?xml[^>]*\?>\s*", "", svg)
    svg = re.sub(r"<!DOCTYPE[^>]*>\s*", "", svg)
    return svg


def _table(rows):
    head = "".join(f"<th>{inline(c)}</th>" for c in rows[0])
    body = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
                   for r in rows[1:])
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def block_html(kind, payload, ctx):
    if kind == "part":
        return f"<h2>{inline(payload)}</h2>"
    if kind == "section":
        return f"<h3>{inline(payload)}</h3>"
    if kind == "bullets":
        return "<ul>" + "".join(f"<li>{inline(i)}</li>" for i in payload) + "</ul>"
    if kind == "note":
        return f'<p class="note">{inline(payload)}</p>'
    if kind == "table":
        return _table(payload)
    if kind == "code":
        return f"<pre>{html.escape(payload)}</pre>"
    if kind == "pagebreak":
        return '<div style="page-break-after:always"></div>'
    if kind == "figure":
        path = figlib.render_figure(payload, "svg", ctx.out_dir, ctx.evidence)
        return f'<figure id="fig-{html.escape(payload)}">{_svg_inline(path)}</figure>'
    if kind == "diagram":
        raise SystemExit("@diagram is PDF-only; use @figure for html")
    return f"<p>{inline(payload)}</p>"


def render(fm, blocks, out_path, ctx):
    title = html.escape(fm.get("title", ""))
    subtitle = html.escape(fm.get("subtitle", ""))
    meta = "".join(f"<span>{label}: {html.escape(fm[key])}</span>"
                   for label, key in META_LINES if fm.get(key))
    cover = (f'<header class="cover">'
             f'<div class="org">{html.escape(fm.get("org", ""))}</div>'
             f"<h1>{title}</h1>"
             + (f'<p class="subtitle">{subtitle}</p>' if subtitle else "")
             + f'<div class="meta">{meta}</div></header>')
    body = "\n".join(block_html(k, p, ctx) for k, p in blocks)
    footer = (f"<footer><span>{html.escape(fm.get('footer', 'Internal'))}</span>"
              f"<span>{html.escape(fm.get('date', ''))}</span></footer>")
    lang = html.escape(fm.get("lang", "en"))
    page = (f'<!DOCTYPE html>\n<html lang="{lang}"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">'
            f"<title>{title}</title><style>{CSS}</style></head>"
            f"<body><main>{cover}\n{body}\n{footer}</main>"
            f"<script>{JS}</script></body></html>\n")
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)
    return out_path
