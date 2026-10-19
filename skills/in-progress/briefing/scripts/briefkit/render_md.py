"""Render parsed blocks to plain Markdown for an issue comment or a chat post.

The output is GitHub-flavoured and self-explanatory without a stylesheet:
the cover becomes a title and a meta list, figures become image links to the
SVGs written beside the file, page breaks vanish, citation tags stay as text
so the reader can follow them.
"""

import os
import re

from briefkit import figures as figlib

META_LINES = [("To", "to"), ("From", "author"), ("Date", "date"),
              ("Scope", "scope"), ("Distribution", "distribution")]


def _table(rows):
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    out = ["| " + " | ".join(rows[0]) + " |",
           "| " + " | ".join("---" for _ in rows[0]) + " |"]
    out += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(out)


_TAG_MD = re.compile(r"\[(evidence|run):\s*([^\]]+)\]")
_URL = re.compile(r"(?<![<(])(https?://[^\s;,)\]]+)")


def _link_tags(text):
    """URLs inside a citation tag become <autolinks>: GitHub does not autolink a bare URL after `[`."""
    return _TAG_MD.sub(lambda m: f"[{m.group(1)}: {_URL.sub(r'<\1>', m.group(2))}]", text)


def block_md(kind, payload, ctx, out_dir):
    out = _block_md(kind, payload, ctx, out_dir)
    return out if out is None or kind == "code" else _link_tags(out)


def _block_md(kind, payload, ctx, out_dir):
    if kind == "part":
        return f"## {payload}"
    if kind == "section":
        return f"### {payload}"
    if kind == "bullets":
        return "\n".join(f"- {i}" for i in payload)
    if kind == "note":
        return f"> {payload}"
    if kind == "table":
        return _table(payload)
    if kind == "code":
        return f"```\n{payload}\n```"
    if kind == "pagebreak":
        return None
    if kind == "figure":
        path = figlib.render_figure(payload, "svg", ctx.out_dir, ctx.evidence)
        rel = os.path.relpath(path, out_dir)
        return f"![{payload}]({rel})"
    if kind == "diagram":
        raise SystemExit("@diagram is PDF-only; use @figure for md")
    return payload


def render(fm, blocks, out_path, ctx):
    out_dir = os.path.dirname(os.path.abspath(out_path))
    os.makedirs(out_dir, exist_ok=True)
    head = []
    if fm.get("title"):
        head.append(f"# {fm['title']}")
    if fm.get("subtitle"):
        head.append(f"*{fm['subtitle']}*")
    # `cover: title` keeps only the title, for media whose host already shows sender and date
    # (an issue comment, a chat post).
    title_only = fm.get("cover", "").strip() == "title"
    meta = [] if title_only else [f"**{label}:** {fm[key]}" for label, key in META_LINES if fm.get(key)]
    if fm.get("org") and not title_only:
        meta.insert(0, f"**{fm['org']}**")
    if meta:
        head.append("  \n".join(meta))
    parts = head + [b for b in (block_md(k, p, ctx, out_dir) for k, p in blocks) if b is not None]
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(parts) + "\n")
    return out_path
