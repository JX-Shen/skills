"""Inline markup, one implementation per target medium.

`**bold**` and `*italic*` are the only emphasis. `[evidence: ...]` and
`[run: ...]` are citation tags: the lint requires one near every number, and
every medium renders them small and muted so the reader can see where a
figure came from without the tag competing with the sentence.
"""

import re

_BOLD = re.compile(r"\*\*(.+?)\*\*")
_ITALIC = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")
_TAG = re.compile(r"\[(evidence|run):\s*([^\]]+)\]")
MUTE_HEX = "#5a6472"


def _escape_xml(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline_xml(text):
    """reportlab Paragraph markup."""
    text = _escape_xml(text)
    text = _BOLD.sub(r"<b>\1</b>", text)
    text = _ITALIC.sub(r"<i>\1</i>", text)
    text = _TAG.sub(rf'<font size="7" color="{MUTE_HEX}">[\1: \2]</font>', text)
    return text


def inline_html(text):
    text = _escape_xml(text).replace('"', "&quot;")
    text = _BOLD.sub(r"<strong>\1</strong>", text)
    text = _ITALIC.sub(r"<em>\1</em>", text)
    text = _TAG.sub(r'<span class="cite">\1: \2</span>', text)
    return text


def inline_plain(text):
    """Strip emphasis and tags; for lint and plain-text fallbacks."""
    text = _BOLD.sub(r"\1", text)
    text = _ITALIC.sub(r"\1", text)
    text = _TAG.sub("", text)
    return text.strip()


def strip_tags(text):
    return _TAG.sub("", text).rstrip()


def is_heading_para_text(text):
    """A paragraph that is nothing but bold text acts as a run-in heading."""
    return bool(re.fullmatch(r"\*\*[^*]+\*\*", text))


def inline_runs(text):
    """Split into (text, bold, italic, muted) runs for docx."""
    runs = []
    pos = 0
    pattern = re.compile(
        r"\*\*(.+?)\*\*|(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)|\[(evidence|run):\s*([^\]]+)\]")
    for m in pattern.finditer(text):
        if m.start() > pos:
            runs.append((text[pos:m.start()], False, False, False))
        if m.group(1) is not None:
            runs.append((m.group(1), True, False, False))
        elif m.group(2) is not None:
            runs.append((m.group(2), False, True, False))
        else:
            runs.append((f"[{m.group(3)}: {m.group(4)}]", False, False, True))
        pos = m.end()
    if pos < len(text):
        runs.append((text[pos:], False, False, False))
    return runs
