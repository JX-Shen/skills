---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up.
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work.

Save it to `.scratch/handoff/` in the current project, creating the directory if it does not exist. Name the file for what the next session will *do*, in kebab-case: `ticket-3-bar-semantics.md`, not `handoff.md` and not a name describing the session that is ending. Keeping it in the project means the next window reaches it by a relative path and it survives a reboot; the OS temporary directory does neither.

`.scratch/` holds working state, not project record. Before writing, make sure the repo ignores it: add `.scratch/` to `.gitignore` if it is not already there, so that a handoff never lands in a commit.

Include a "suggested skills" section in the document, naming which skills the next agent should call the Skill tool for.

Do not duplicate content already captured in other artifacts (specs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
