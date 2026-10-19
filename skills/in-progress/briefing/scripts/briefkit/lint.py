"""Shape lint for brief.md: the checks a reviewer would otherwise make by hand.

    lint.py brief.md            exit 1 and a problem list when the shape is off

Rules come from SHAPE.md. Each problem prints as `file:line: CODE message` so
the agent can jump to the block and fix it before anyone reads the draft.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if os.path.dirname(HERE) not in sys.path:
    sys.path.insert(0, os.path.dirname(HERE))

from briefkit.inline import inline_plain  # noqa: E402
from briefkit.parse import load_located  # noqa: E402

REQUIRED_KEYS = ("title", "kind", "to", "date")
KINDS = ("decision", "progress", "review")
SUMMARY_MAX_LINES = 25

# Section order per kind: each group is a set of heading keywords; a `#` heading
# containing any keyword satisfies the group. Groups must appear in this order.
ORDER = {
    "decision": [
        ("summary", ("summary",)),
        ("the proposal", ("proposal", "design", "rule", "the change", "what is proposed")),
        ("the alternative", ("alternative",)),
        ("the cost", ("cost",)),
        ("the recommendation", ("recommend", "decision")),
    ],
    "progress": [
        ("summary", ("summary",)),
        ("where the work stands", ("where", "stand", "progress", "what changed", "built", "done so far")),
        ("the gaps", ("gap", "open", "remaining", "risk", "not yet")),
        ("what comes next", ("next", "plan", "proposal", "ask")),
    ],
    "review": [
        ("summary", ("summary",)),
        ("what was delivered", ("delivered", "delivery", "handed over", "received")),
        ("findings", ("finding", "gap", "defect", "deviation")),
        ("acceptance", ("accept", "recommend", "decision")),
    ],
}

# Phrases that dress up a position instead of stating it. (pattern, reason)
FORBIDDEN = [
    (r"\b(done )?with caveats?\b", "a failed check keeps its objective open; name the gap and who acts, or drop the word"),
    (r"\binherent(ly)?\b", "'inherent' needs a measurement that shows it; cite the run or remove"),
    (r"\bnot fixable\b|\bcannot be fixed\b|\bcan't be fixed\b", "needs a measurement that shows it, not an explanation"),
    (r"\byou'?re absolutely right\b|\bgreat point\b", "performative agreement; state the verified fact instead"),
    (r"\bno such [^.]{0,40}\b(found|exists)\b", "an absence found by search is unverified; state what was searched and when"),
    (r"\bwe recommend\b", "one author means first person singular: 'I recommend'"),
    (r"\bit'?s worth noting\b|\bimportantly,", "filler; delete and keep the fact"),
]

DEVIATION_COLS = ["Deviation", "Rule it departs from", "Measured effect", "Status", "Consequence"]
RECOMMENDATION_COLS = ["Recommendation", "Expected effect", "Basis", "Cost and time", "Decider"]
STATUS_WORDS = ("ratified", "provisional", "declared")
NON_OWNERS = ("phase 2", "information", "tbd", "later", "future")

_TAG = re.compile(r"\[(evidence|run):\s*[^\]]+\]")
_NUMBER = re.compile(r"(?<![\w.])\d[\d,]*(\.\d+)?\s?%?(?![\w.])")
_YEAR = re.compile(r"^(19|20)\d\d$")
_DATE = re.compile(r"\b(19|20)\d\d-\d\d-\d\d\b")
_MONTH = (r"(?:January|February|March|April|May|June|July|August|September|October|November|December"
          r"|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec)\.?")
# "16 Oct", "27 to 29 October", "27-29 Oct", "October 27": a calendar day, not a measured number.
_DAY_MONTH = re.compile(r"\b\d{1,2}(?:\s*(?:to|-|\u2013)\s*\d{1,2})?\s+" + _MONTH + r"(?![A-Za-z])"
                        r"|\b" + _MONTH + r"\s+\d{1,2}(?:\s*(?:to|-|\u2013)\s*\d{1,2})?\b")


class Problem:
    def __init__(self, path, line, code, message):
        self.path, self.line, self.code, self.message = path, line, code, message

    def __str__(self):
        return f"{self.path}:{self.line}: {self.code} {self.message}"


def _numbers_needing_trace(text):
    """Numbers in prose that are not years, dates, or inside citation tags."""
    text = _DAY_MONTH.sub(" ", _DATE.sub(" ", _TAG.sub(" ", text)))
    found = []
    for m in _NUMBER.finditer(text):
        tok = m.group(0).strip()
        if _YEAR.match(tok):
            continue
        found.append(tok)
    return found


def lint_file(md_path):
    fm, located = load_located(md_path)
    name = os.path.basename(md_path)
    problems = []
    P = lambda line, code, msg: problems.append(Problem(name, line, code, msg))

    # ---- front matter
    for key in REQUIRED_KEYS:
        if not fm.get(key):
            P(1, "FM01", f"front matter needs `{key}:`")
    kind = fm.get("kind", "")
    if kind and kind not in KINDS:
        P(1, "FM02", f"`kind:` must be one of {', '.join(KINDS)}; got {kind!r}")

    parts = [(ln, payload) for ln, k, payload in located if k == "part"]
    if not parts:
        P(1, "SUM01", "no `#` section; the first section must be the summary")
        return problems

    # ---- summary: first, short, carries cost and recommendation
    first_ln, first_title = parts[0]
    if "summary" not in first_title.lower():
        P(first_ln, "SUM01", f"the first `#` section must be the summary; got {first_title!r}")
    summary_end = parts[1][0] if len(parts) > 1 else None
    summary_blocks = [(ln, k, p) for ln, k, p in located
                      if ln > first_ln and (summary_end is None or ln < summary_end)]
    if summary_end is not None:
        with open(md_path, encoding="utf-8") as f:
            src = f.read().splitlines()
        body_lines = [l for l in src[first_ln:summary_end - 1] if l.strip()]
        if len(body_lines) > SUMMARY_MAX_LINES:
            P(first_ln, "SUM02", f"summary runs {len(body_lines)} non-blank lines; keep it within "
                                 f"{SUMMARY_MAX_LINES} so it stays one page")
    summary_text = " ".join(
        inline_plain(p if isinstance(p, str) else " ".join(
            " ".join(r) if isinstance(r, list) else r for r in p))
        for ln, k, p in summary_blocks if k in ("para", "bullets", "table"))
    if not re.search(r"\bcosts?\b|\bnothing new\b", summary_text, re.I):
        P(first_ln, "SUM03", "the summary names no cost; state what the recommended path or the next stage "
                             "costs the reader, or say in so many words that it costs nothing new")
    if kind == "review":
        if not re.search(r"\baccept|\breject", summary_text, re.I):
            P(first_ln, "SUM04", "a review's summary says whether to accept or reject the delivery")
    elif not re.search(r"\brecommend", summary_text, re.I):
        P(first_ln, "SUM04", "the summary carries the recommendation; a reader who stops here must have it")

    # ---- section order for the kind
    if kind in ORDER:
        hits = []
        for label, keys in ORDER[kind]:
            match = next(((ln, t) for ln, t in parts if any(k in t.lower() for k in keys)), None)
            if match is None:
                P(first_ln, "ORD01", f"no `#` section for {label} (a heading containing one of: {', '.join(keys)})")
            hits.append(match)
        last = None
        for (label, _), match in zip(ORDER[kind], hits):
            if match is None:
                continue
            if last is not None and match[0] < last[0]:
                P(match[0], "ORD02", f"{label} ({match[1]!r}) comes before {last[1]!r}; SHAPE.md orders a {kind} the other way")
            last = match

    # ---- numbers trace to a figure or a citation tag
    prose = [(i, ln, k, p) for i, (ln, k, p) in enumerate(located) if k in ("para", "bullets")]
    kinds_by_index = [k for _, k, _ in located]
    for i, ln, k, p in prose:
        text = p if isinstance(p, str) else " ".join(p)
        nums = _numbers_needing_trace(text)
        if not nums:
            continue
        if _TAG.search(text):
            continue
        window = kinds_by_index[max(0, i - 2): i + 3]
        if "figure" in window:
            continue
        P(ln, "NUM01", f"numbers {nums[:4]} have no [evidence: ...] or [run: ...] tag and no @figure within two blocks")

    # ---- forbidden phrases
    for ln, k, p in located:
        if k not in ("para", "bullets", "table", "note"):
            continue
        if k == "table":
            text = " ".join(" ".join(r) for r in p)
        elif k == "bullets":
            text = " ".join(p)
        else:
            text = p
        for pat, why in FORBIDDEN:
            m = re.search(pat, text, re.I)
            if m:
                P(ln, "WORD01", f"{m.group(0)!r}: {why}")

    # ---- the two management tables
    for ln, k, rows in located:
        if k != "table" or not rows:
            continue
        head = [c.strip() for c in rows[0]]
        if head and head[0].lower() == DEVIATION_COLS[0].lower():
            if [h.lower() for h in head] != [c.lower() for c in DEVIATION_COLS]:
                P(ln, "TAB01", f"deviation table columns must be: {' | '.join(DEVIATION_COLS)}")
            else:
                for r in rows[1:]:
                    if len(r) == 5 and r[3].split()[0].lower().rstrip(",.") not in STATUS_WORDS:
                        P(ln, "TAB02", f"deviation status {r[3]!r} must start with ratified, provisional or declared")
                    if len(r) == 5 and not r[2].strip():
                        P(ln, "TAB02", "measured effect is empty; write 'unmeasured' rather than leave the cell blank")
        if head and head[0].lower() == RECOMMENDATION_COLS[0].lower():
            if [h.lower() for h in head] != [c.lower() for c in RECOMMENDATION_COLS]:
                P(ln, "TAB01", f"recommendation table columns must be: {' | '.join(RECOMMENDATION_COLS)}")
            else:
                for r in rows[1:]:
                    if len(r) == 5 and r[4].strip().lower() in NON_OWNERS:
                        P(ln, "TAB03", f"decider {r[4]!r} is not a person who can say yes")
        # Owner columns anywhere: a stage or a title is not an owner.
        for ci, h in enumerate(head):
            if h.lower() in ("owner", "decider", "who acts next"):
                for r in rows[1:]:
                    if ci < len(r) and r[ci].strip().lower() in NON_OWNERS:
                        P(ln, "TAB03", f"{h} {r[ci]!r}: owner means who acts next, not a phase or a placeholder")
    return problems


def report(problems, stream=None):
    stream = stream or sys.stderr
    for p in problems:
        stream.write(f"{p}\n")
    stream.write(f"{len(problems)} problem(s)\n")


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    path = argv[0] if argv else "brief.md"
    problems = lint_file(path)
    if problems:
        report(problems)
        return 1
    print(f"{os.path.basename(path)}: shape ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
