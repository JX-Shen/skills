"""Inline emphasis, one implementation per target markup.

`**bold**` and `*italic*` are the only inline syntax. Each renderer asks for the
markup it needs; the regexes are shared so every medium reads the same spans.
"""

import re

_BOLD = re.compile(r"\*\*(.+?)\*\*")
_ITALIC = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")


def inline_xml(text):
    """reportlab Paragraph markup."""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = _BOLD.sub(r"<b>\1</b>", text)
    text = _ITALIC.sub(r"<i>\1</i>", text)
    return text


def inline_html(text):
    text = (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))
    text = _BOLD.sub(r"<strong>\1</strong>", text)
    text = _ITALIC.sub(r"<em>\1</em>", text)
    return text


def inline_plain(text):
    """Strip emphasis; for docx runs and lint."""
    text = _BOLD.sub(r"\1", text)
    text = _ITALIC.sub(r"\1", text)
    return text


def inline_runs(text):
    """Split into (text, bold, italic) runs for docx."""
    runs = []
    pos = 0
    pattern = re.compile(r"\*\*(.+?)\*\*|(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")
    for m in pattern.finditer(text):
        if m.start() > pos:
            runs.append((text[pos:m.start()], False, False))
        if m.group(1) is not None:
            runs.append((m.group(1), True, False))
        else:
            runs.append((m.group(2), False, True))
        pos = m.end()
    if pos < len(text):
        runs.append((text[pos:], False, False))
    return runs
