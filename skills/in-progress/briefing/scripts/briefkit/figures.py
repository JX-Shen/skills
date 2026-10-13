"""Figures are code, not Markdown, and every number on them is read from evidence.

A briefing directory may carry a `figures.py`. It registers one function per
`@figure <name>` used in brief.md:

    from briefkit.figures import figure

    @figure("overlap")
    def overlap(ev):
        data = ev.json("figures-data.json")
        fig, ax = plt.subplots(figsize=(7, 3))
        ...
        return fig

`ev` is an Evidence loader rooted at the directory named by the `evidence:`
front-matter key (or `--evidence` on the command line). Read through it; never
type a number into the figure. If a figure cannot be drawn from the evidence it
cites, the briefing has no business showing it.

`@diagram <name>` stays for PDF-only drawings. Register a reportlab Flowable
factory with `diagram(name)`; other media refuse a brief that uses one.

Rendering writes `<out>/figures/<name>.svg` (html, md) or `.png` (pdf, docx)
and returns the path.
"""

import importlib.util
import json
import os
import sys

FIGURES = {}
DIAGRAMS = {}


def figure(name):
    def register(fn):
        FIGURES[name] = fn
        return fn
    return register


def diagram(name):
    def register(factory):
        DIAGRAMS[name] = factory
        return factory
    return register


class Evidence:
    """Read-only access to the evidence directory a briefing cites."""

    def __init__(self, root):
        self.root = os.path.abspath(root)

    def path(self, rel):
        p = os.path.join(self.root, rel)
        if not os.path.exists(p):
            raise SystemExit(f"evidence file not found: {p}")
        return p

    def json(self, rel):
        with open(self.path(rel), encoding="utf-8") as f:
            return json.load(f)

    def text(self, rel):
        with open(self.path(rel), encoding="utf-8") as f:
            return f.read()


def load_registry(figures_path):
    """Import a briefing's figures.py so its decorators populate the registries."""
    FIGURES.clear()
    DIAGRAMS.clear()
    if not figures_path or not os.path.exists(figures_path):
        return
    # Let `import briefkit` resolve from the figures file as it does from build.py.
    kit_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if kit_parent not in sys.path:
        sys.path.insert(0, kit_parent)
    spec = importlib.util.spec_from_file_location("briefing_figures", figures_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)


def render_figure(name, fmt, out_dir, evidence):
    """Draw a registered figure to <out_dir>/figures/<name>.<fmt>; return the path."""
    if name not in FIGURES:
        raise SystemExit(
            f"@figure {name!r} is not registered. Add it to figures.py beside "
            f"brief.md. Registered: {sorted(FIGURES) or 'none'}")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig = FIGURES[name](evidence)
    fig_dir = os.path.join(out_dir, "figures")
    os.makedirs(fig_dir, exist_ok=True)
    path = os.path.join(fig_dir, f"{name}.{fmt}")
    fig.savefig(path, format=fmt, bbox_inches="tight",
                dpi=200 if fmt == "png" else None, metadata=_metadata(fmt))
    plt.close(fig)
    return path


def _metadata(fmt):
    # Keep the output stable across runs so a re-render diffs clean.
    if fmt == "svg":
        return {"Date": None, "Creator": None}
    if fmt == "png":
        return {"Software": None}
    return None
