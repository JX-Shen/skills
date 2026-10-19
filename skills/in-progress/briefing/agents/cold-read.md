# Cold read

Run this as a fresh subagent (a smaller model is fine) after the lint passes and before the user sees the draft. Give it the rendered medium the reader will receive (the HTML or the page images, not brief.md), the reader's description from their reader model (step 1 of `SKILL.md`), and nothing else: no conversation history, no evidence files, no explanation of what the document is trying to say.

Prompt:

```
You are the reader of the attached document: <reader description from the reader model,
e.g. "a portfolio manager who decides on this work and does not read code">.
You have five minutes and no one to ask. Read only what is in front of you.

Answer three questions and nothing else. Quote the document where you can.

1. From the first screen alone, what is being asked of you, what does it cost,
   and what do you now believe is true? One sentence each. If you cannot answer
   one of them from the first screen, say which.

2. Where did you stop and want to ask a question? List each place by its
   heading or first words, and the question you would ask.

3. Which line would you not take on trust? Name it and say what would make
   you believe it (a figure, a number with a source, a named run).

Do not suggest rewording. Do not summarise the document. Do not praise it.
```

What to do with the answers:

- A miss on question 1 means the summary is wrong, not the wording. Go back to the essence sentence (step 1) and re-derive the summary.
- Each question 2 stop is a place where the body must answer before the reader asks, or where a figure belongs.
- Each question 3 line gets a citation tag, a figure, or deletion.

Record the reader's questions and what changed in the briefing `README.md` ratchet. The next version is checked against them.
