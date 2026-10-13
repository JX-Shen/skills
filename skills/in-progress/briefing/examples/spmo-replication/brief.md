---
title: Replicating the SPMO index
subtitle: Progress report, first rebalance check
org: Example
to: Portfolio manager
author: J. Shen
date: 2026-10-13
kind: progress
evidence: evidence
footer: Internal
---

# Summary

Our rule set now reproduces the tracker's holdings at the September 2023 rebalance closely enough to use it as the yardstick for everything that follows. The money at stake is unchanged; what we bought is a way to check our own work against a published list instead of against our own expectations.

Two gaps remain, both small and both named below: three names the tracker holds that our run does not, and the weights of the largest names, which our cap flattens. Neither changes the decision in front of you.

I recommend we continue to the full history on this basis. The decision is yours; continuing costs one more month of the same effort and no new data purchase.

# Where the work stands

The tracker publishes its holdings; we built the rules from its method document and ran them on the same date. The grid shows every name the tracker held, coloured by whether our run held it too. Count the red cells rather than take a percentage from me. [evidence: figures-data.json grids.test]

@figure holdings-grid

The rebalance in question replaced most of the list, so matching it is a different achievement from matching a list that barely moved. The bars show how much of each change the run made on its own. [evidence: figures-data.json turnover]

@figure turnover

# The gaps

- Three names the tracker holds are absent from our run, and three names we hold are absent from the tracker. All six sit at the edge of the selection, where a small difference in a score moves a name in or out. [evidence: figures-data.json offset]
- Weights agree in order but not in size at the top: our cap holds the largest names at a fixed ceiling while the tracker lets them run higher. The scatter shows the shared names on both scales. [evidence: figures-data.json stats]

@figure weight-scatter

# What comes next

- Run the same check at every rebalance since the tracker's inception, so the one match above becomes a record rather than a single reading.
- Keep the cap, and show its effect as a separate line in every later report, so you can see what it costs on each date.
- Leave the three edge names alone until the full history says whether they recur.

The decision is not mine to make. Continuing is reversible at any rebalance; stopping now leaves the single reading above as the only evidence.
