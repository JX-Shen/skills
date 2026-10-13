"""Parse a briefing's brief.md into front matter and a flat list of blocks.

The Markdown subset, and nothing beyond it:

    --- key: value ---   front matter (absent keys are dropped by every renderer)
    # Heading            section heading
    ## Heading           subheading
    - item               bullet (continuation lines indented two spaces)
    > note               small muted line, for reference URLs and asides
    | a | b |            table (first row is the header)
    ```                  fenced block, rendered monospace
    **bold** *italic*    inline emphasis
    @pagebreak           forced page break (paged media only; others ignore it)
    @figure <name>       a figure registered in the briefing's figures.py
    @diagram <name>      a PDF-only Flowable registered in the briefing's figures.py

Every renderer consumes the same block list, so a wording change in brief.md
reaches every medium and no medium carries prose of its own.

Blocks are (kind, payload) tuples:

    ("part", text)        # heading
    ("section", text)     ## heading
    ("para", text)
    ("bullets", [text, ...])
    ("note", text)
    ("table", [[cell, ...], ...])   first row is the header
    ("code", text)
    ("pagebreak", None)
    ("figure", name)
    ("diagram", name)
"""

import re

FRONT_MATTER_KEYS = ("title", "subtitle", "org", "to", "author", "date",
                     "scope", "distribution", "footer", "kind", "evidence",
                     "figures", "lang")

_BLOCK_START = re.compile(r"(#|-\s|\||>\s|@)")


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


def parse_located(lines):
    """Yield (line_index, kind, payload); line_index is 0-based into `lines`."""
    i, n = 0, len(lines)
    while i < n:
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue
        start = i
        if line.startswith("## "):
            yield start, "section", line[3:].strip()
            i += 1
        elif line.startswith("# "):
            yield start, "part", line[2:].strip()
            i += 1
        elif line.strip() == "@pagebreak":
            yield start, "pagebreak", None
            i += 1
        elif line.strip().startswith("@figure"):
            yield start, "figure", line.strip()[len("@figure"):].strip()
            i += 1
        elif line.strip().startswith("@diagram"):
            yield start, "diagram", line.strip()[len("@diagram"):].strip()
            i += 1
        elif line.startswith("```"):
            i += 1
            code = []
            while i < n and not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            yield start, "code", "\n".join(code)
        elif line.startswith("> "):
            yield start, "note", line[2:].strip()
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
            yield start, "bullets", items
        elif line.startswith("|"):
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            yield start, "table", rows
        else:
            para = [line.strip()]
            i += 1
            while i < n and lines[i].strip() and not _BLOCK_START.match(lines[i]):
                para.append(lines[i].strip())
                i += 1
            yield start, "para", " ".join(para)


def parse_blocks(lines):
    """Yield (kind, payload) for the documented Markdown subset."""
    for _, kind, payload in parse_located(lines):
        yield kind, payload


def load(md_path):
    """Return (front_matter, blocks, fm_line_count) for a brief.md path."""
    with open(md_path, encoding="utf-8") as f:
        raw = f.read().splitlines()
    fm, body = parse_front_matter(raw)
    return fm, list(parse_blocks(body)), len(raw) - len(body)


def load_located(md_path):
    """Return (front_matter, [(line_no, kind, payload), ...]) with 1-based line numbers."""
    with open(md_path, encoding="utf-8") as f:
        raw = f.read().splitlines()
    fm, body = parse_front_matter(raw)
    offset = len(raw) - len(body)
    return fm, [(idx + offset + 1, kind, payload)
                for idx, kind, payload in parse_located(body)]


def is_heading_para(payload):
    """A paragraph that is nothing but bold text acts as a run-in heading."""
    return bool(re.fullmatch(r"\*\*[^*]+\*\*", payload))
