# Channels

A **channel** is where the document lands: a GitHub issue thread, a report the reader opens in a browser, a PDF they file, a Word file they edit, a chat post. The host decides what the reader sees around the document and how it is drawn, so each channel has its own render target and its own way to look at the result. The rules here hold for every reader. What one reader wants (voice, register, silences) lives in their reader model (see [`MECHANICS.md`](MECHANICS.md)), whatever the channel.

## GitHub issue or pull request comment

- Medium: Markdown. Front matter `cover: title` (the comment header already shows author and date) and `repo: owner/name`.
- Review with `build.py brief.md --to gh`, then screenshot `out/work.gh.html`: that is GitHub's own rendering, so autolinks, issue references, commit SHAs and tables look as they will on the page. Post `out/work.md` verbatim.
- The thread is the record. Earlier comments in the same thread are the first precedent to read, and a link to one of them replaces restating it.
- The issue's own list of items (its parts, its acceptance tests, its asks) is the natural key for any status table.

## HTML report

- Medium: HTML, one self-contained file that opens from an attachment or a share.
- Screenshot at 1000 px wide. The summary fits the first screen; tables sort on header click and nothing overflows the right edge.

## PDF report

- Medium: PDF, for a reader who prints or files.
- Read every page as an image. The summary fits page one; no heading is stranded at a page foot; a split table repeats its header. Record the page count in the README.

## Word document

- Medium: docx, for a reader who edits or comments in Word.
- Open the file (or convert it to PDF) and look at every page; tracked changes from the reader come back as a new version of `brief.md`, never as edits to the docx.

## Chat post

- Medium: Markdown, cut to what the host renders. Discord and Telegram draw no tables: use one bullet per row. Slack's mrkdwn is not GitHub Markdown.
- Post a link to the full report rather than the report itself when the summary alone does not carry the decision.
