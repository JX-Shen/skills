"""Preview a Markdown brief the way GitHub shows it in an issue or PR comment.

briefkit's own HTML is not what GitHub renders: autolinks, code spans inside
tables, issue references and the stylesheet all differ. This medium renders
work.md first, sends it to GitHub's own Markdown API (`gh api -X POST /markdown`,
mode gfm, with the repository as context so #123 and commit SHAs resolve), and
wraps the returned HTML in github-markdown-css. The result is a review copy,
never sent: the comment posted is work.md.

Needs `gh` signed in. The repository comes from front matter `repo:` (owner/name).
"""

import html
import json
import os
import subprocess

from briefkit import render_md

CSS_URL = "https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.8.1/github-markdown.min.css"

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="{css}">
<style>body{{background:#fff}}@media (prefers-color-scheme:dark){{body{{background:#0d1117}}}}
.markdown-body{{box-sizing:border-box;min-width:200px;max-width:980px;margin:0 auto;padding:45px}}
@media (max-width:767px){{.markdown-body{{padding:15px}}}}</style>
</head><body><article class="markdown-body">
{body}
</article></body></html>
"""


def github_html(text, repo):
    payload = {"text": text, "mode": "gfm"}
    if repo:
        payload["context"] = repo
    try:
        done = subprocess.run(["gh", "api", "-X", "POST", "/markdown", "--input", "-"],
                              input=json.dumps(payload), capture_output=True, text=True, check=True)
    except FileNotFoundError:
        raise SystemExit("--to gh needs the GitHub CLI (`gh`) on PATH")
    except subprocess.CalledProcessError as e:
        raise SystemExit(f"gh api /markdown failed: {e.stderr.strip()}")
    return done.stdout


def render(fm, blocks, out_path, ctx):
    md_path = os.path.join(os.path.dirname(out_path), "work.md")
    render_md.render(fm, blocks, md_path, ctx)
    with open(md_path, encoding="utf-8") as f:
        text = f.read()
    body = github_html(text, fm.get("repo", "").strip())
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(PAGE.format(title=html.escape(fm.get("title", "comment preview")), css=CSS_URL, body=body))
