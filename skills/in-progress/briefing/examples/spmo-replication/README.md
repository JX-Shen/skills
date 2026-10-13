# Example: SPMO replication progress report

A worked `briefing` directory: a progress report for a non-technical portfolio manager, built from evidence through `briefkit`.

- `brief.md` is the only place wording lives. Its front matter names the kind (`progress`) and the evidence root.
- `figures.py` registers the three `@figure` names the brief uses. Every number on every figure is read from the evidence; none is typed in.
- `evidence/figures-data.json` is a verbatim copy of one evidence file from a private research work log (`momentum-anchor`, work-log `20260912-009-issue-7`, `spmo-comparison/figures-data.json`, 2023-08-31 reference date). It is here only so the example builds; its strings are data, not prose.

Build every medium:

```bash
../../.venv/bin/python ../../scripts/briefkit/build.py brief.md --to html,md,docx,pdf
```

Outputs land in `out/` (ignored by git).

## Ratchet

- The reader counts the grid; the prose does not quote a percentage for them. Reason: the owner's rule, "show 94/100 rather than say 94/100".
- Good news, then gaps, then the plan. Reason: the owner's order for progress reports.
- One cost sentence in the summary, with "the money is unchanged" stated outright. Reason: a reader with an accounting background collapses labour into spend unless told otherwise.
