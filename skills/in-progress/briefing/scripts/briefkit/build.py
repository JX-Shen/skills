#!/usr/bin/env python3
"""Build a briefing from brief.md into one or more media.

    build.py brief.md --to html,md,docx,pdf [--out out/] [--no-lint]
                      [--figures figures.py] [--evidence DIR]

brief.md is the single content source. The briefing directory may carry a
figures.py registering `@figure` and `@diagram` names; `evidence:` in the front
matter (or --evidence) names the directory those figures read from. Both paths
are taken relative to brief.md.

Outputs land in <out>/ as work.<ext>; figures beside them in <out>/figures/.
The lint runs first and a failing brief is not rendered; --no-lint is for
drafting only, never for a file that reaches the reader.
"""

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if os.path.dirname(HERE) not in sys.path:
    sys.path.insert(0, os.path.dirname(HERE))

from briefkit import figures as figlib  # noqa: E402
from briefkit import lint as lintlib  # noqa: E402
from briefkit.parse import load  # noqa: E402

MEDIA = ("html", "md", "docx", "pdf")


class Context:
    def __init__(self, out_dir, evidence_root):
        self.out_dir = out_dir
        self.evidence = figlib.Evidence(evidence_root) if evidence_root else None


def resolve(base_dir, value, default=None):
    v = value if value is not None else default
    if v is None:
        return None
    return v if os.path.isabs(v) else os.path.join(base_dir, v)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("brief", nargs="?", default="brief.md")
    ap.add_argument("--to", default="html",
                    help="comma-separated media: " + ",".join(MEDIA))
    ap.add_argument("--out", default=None, help="output directory (default: out/ beside brief.md)")
    ap.add_argument("--figures", default=None, help="figures.py (default: beside brief.md)")
    ap.add_argument("--evidence", default=None, help="evidence root (default: front matter `evidence:`)")
    ap.add_argument("--no-lint", action="store_true", help="skip the shape lint (drafting only)")
    args = ap.parse_args(argv)

    brief = os.path.abspath(args.brief)
    base = os.path.dirname(brief)
    media = [m.strip() for m in args.to.split(",") if m.strip()]
    unknown = [m for m in media if m not in MEDIA]
    if unknown:
        raise SystemExit(f"unknown media {unknown}; choose from {MEDIA}")

    fm, blocks, fm_lines = load(brief)

    if not args.no_lint:
        problems = lintlib.lint_file(brief)
        if problems:
            lintlib.report(problems)
            raise SystemExit(2)

    out_dir = resolve(base, args.out, "out")
    os.makedirs(out_dir, exist_ok=True)
    figures_path = resolve(base, args.figures, fm.get("figures", "figures.py"))
    evidence_root = resolve(base, args.evidence, fm.get("evidence"))
    figlib.load_registry(figures_path)

    uses_figures = any(k in ("figure", "diagram") for k, _ in blocks)
    if uses_figures and not evidence_root and any(k == "figure" for k, _ in blocks):
        raise SystemExit("brief.md uses @figure but names no evidence root: "
                         "set `evidence:` in the front matter or pass --evidence")
    if any(k == "diagram" for k, _ in blocks) and any(m != "pdf" for m in media):
        raise SystemExit("@diagram is PDF-only; use @figure for a brief that "
                         "ships to html, md or docx")

    ctx = Context(out_dir, evidence_root)
    written = []
    for m in media:
        out_path = os.path.join(out_dir, f"work.{m}")
        if m == "pdf":
            from briefkit import render_pdf
            render_pdf.render(fm, blocks, out_path, ctx)
        elif m == "html":
            from briefkit import render_html
            render_html.render(fm, blocks, out_path, ctx)
        elif m == "md":
            from briefkit import render_md
            render_md.render(fm, blocks, out_path, ctx)
        elif m == "docx":
            from briefkit import render_docx
            render_docx.render(fm, blocks, out_path, ctx)
        written.append(out_path)
    for p in written:
        print("written:", p)


if __name__ == "__main__":
    main()
