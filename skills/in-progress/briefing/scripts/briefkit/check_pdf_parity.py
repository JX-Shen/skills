#!/usr/bin/env python3
"""Regression: briefkit's PDF renders pixel-identical to md_to_pdf.template.py.

Renders a synthetic brief that exercises every directive of the subset through
both renderers and compares each page as an image. Exit 1 on any differing pixel.

    .venv/bin/python scripts/briefkit/check_pdf_parity.py
"""

import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)

BRIEF = """---
title: Regression brief
subtitle: Every directive the subset allows
org: Example Org
to: The decider
author: The author
date: 2026-10-13
scope: Rendering only
distribution: Internal
footer: Regression
---

# Summary

The proposal is a **standing rule** with *one chore* attached. The money is the same;
the labour is higher. Symbols survive: a < b & c > d.

- First bullet with **bold** text
- Second bullet that runs
  onto a continuation line
- Third bullet

> Reference: https://example.org/a-very-long-url-that-runs-across-the-right-margin

## A subheading

**Advantages.**

A paragraph after a bold-only run-in heading, which binds to it.

| Option | Cost | Buys |
| --- | --- | --- |
| Keep | Nothing | Nothing |
| Change | One chore a month | A standard the reader can test |

| A | B |
| --- | --- |
| left | right |

| One | Two | Three | Four |
| --- | --- | --- | --- |
| 1 | 2 | 3 | 4 |

| P | Q | R | S | T |
| --- | --- | --- | --- | --- |
| p | q | r | s | t |

```
account-a --> account-b
   +-- log
```

@pagebreak

# The alternative

A paragraph long enough to wrap: the alternative is the absence of a rule rather
than a different rule, and the reader should see it stated as what it is.

## Filler to force a page turn

""" + "\n".join(
    f"- Bullet number {i} carries enough words to wrap at least once across the "
    "line width of the page so pagination is exercised" for i in range(1, 41)
) + """

# Recommendation

I recommend the change. The decision is not mine to make.
"""


def main():
    with tempfile.TemporaryDirectory() as tmp:
        brief = os.path.join(tmp, "brief.md")
        with open(brief, "w", encoding="utf-8") as f:
            f.write(BRIEF)
        old = os.path.join(tmp, "old.pdf")
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "md_to_pdf.template.py"),
                        brief, old], check=True, cwd=tmp, stdout=subprocess.DEVNULL)
        subprocess.run([sys.executable, os.path.join(HERE, "build.py"), brief,
                        "--to", "pdf", "--no-lint", "--out", os.path.join(tmp, "new")],
                       check=True, cwd=tmp, stdout=subprocess.DEVNULL)
        new = os.path.join(tmp, "new", "work.pdf")

        import numpy as np
        import pypdfium2 as pdfium
        a, b = pdfium.PdfDocument(old), pdfium.PdfDocument(new)
        if len(a) != len(b):
            print(f"page count differs: template {len(a)}, briefkit {len(b)}")
            return 1
        total = 0
        for i in range(len(a)):
            pa = np.asarray(a[i].render(scale=2).to_pil())
            pb = np.asarray(b[i].render(scale=2).to_pil())
            d = int((pa != pb).any(axis=-1).sum())
            total += d
            print(f"page {i + 1}: {d} differing pixels")
        print("pages:", len(a), "total differing pixels:", total)
        return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
