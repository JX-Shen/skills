"""Figures for the SPMO replication progress report.

Every number drawn here is read from evidence/figures-data.json through `ev`.
Nothing is typed in: a figure that cannot be drawn from the evidence it cites
is not drawn.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from briefkit.figures import figure

INK, ACCENT, MUTE, RULE, SHADE = "#1a1a1a", "#1f3a5f", "#5a6472", "#c9cfd6", "#eef1f5"
MISS = "#c0392b"


def _style(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(RULE)
    ax.spines["bottom"].set_color(RULE)
    ax.tick_params(colors=MUTE, labelsize=8)


@figure("holdings-grid")
def holdings_grid(ev):
    """All of the tracker's holdings at the rebalance, one cell each, so the
    reader counts the misses instead of being told how many there are."""
    data = ev.json("figures-data.json")
    grid = data["grids"]["test"]
    cells = grid["cells"]
    cols = 10
    rows = (len(cells) + cols - 1) // cols
    fig, ax = plt.subplots(figsize=(7.2, 0.42 * rows + 0.9))
    for i, c in enumerate(cells):
        r, k = divmod(i, cols)
        colour = ACCENT if c["m"] else MISS
        ax.add_patch(Rectangle((k, rows - 1 - r), 0.94, 0.9, facecolor=colour,
                               edgecolor="white", linewidth=1))
        ax.text(k + 0.47, rows - 1 - r + 0.45, c["t"], ha="center", va="center",
                fontsize=7, color="white", fontweight="bold")
    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.set_axis_off()
    matched = sum(1 for c in cells if c["m"])
    ax.set_title(
        f"Tracker holdings as of {grid['as_of']}: {matched} of {len(cells)} names "
        f"also in our run ({grid['weight_covered']:.1f}% of tracker weight), "
        f"{len(cells) - matched} missed (red)",
        fontsize=9, color=INK, loc="left")
    return fig


@figure("weight-scatter")
def weight_scatter(ev):
    """Our weight against the tracker's for every shared name, on log axes so
    the small names stay visible."""
    data = ev.json("figures-data.json")
    pts = data["scatter"]
    stats = data["stats"]
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    them = [p["them"] for p in pts]
    us = [p["us"] for p in pts]
    bound = [p["bound"] for p in pts]
    ax.scatter([t for t, b in zip(them, bound) if not b],
               [u for u, b in zip(us, bound) if not b],
               s=18, color=ACCENT, alpha=0.85, label="shared name")
    ax.scatter([t for t, b in zip(them, bound) if b],
               [u for u, b in zip(us, bound) if b],
               s=26, facecolor="white", edgecolor=ACCENT, linewidth=1.2,
               label="at the weight cap in our run")
    lo, hi = min(them + us) * 0.8, max(them + us) * 1.25
    ax.plot([lo, hi], [lo, hi], color=RULE, linewidth=1, zorder=0)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Tracker weight, %", color=MUTE, fontsize=9)
    ax.set_ylabel("Our weight, %", color=MUTE, fontsize=9)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    ax.set_title(
        f"{stats['n']} shared names: median ratio {stats['median_ratio']:.3f}, "
        f"{stats['within_25pct']} within 25% of the tracker, "
        f"rank correlation {stats['spearman']:.3f}",
        fontsize=9, color=INK, loc="left")
    _style(ax)
    return fig


@figure("turnover")
def turnover(ev):
    """What the rebalance changed, and how much of each change our run made."""
    data = ev.json("figures-data.json")
    t = data["turnover"]
    labels = ["Names the tracker added", "Names the tracker kept", "Names the tracker removed"]
    totals = [t["replaced"], t["kept"], t["dropped"]]
    ours = [t["added_caught"], t["kept_held"], t["dropped_excluded"]]
    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    y = range(len(labels))
    ax.barh(y, totals, color=SHADE, edgecolor=RULE, height=0.6, label="tracker")
    ax.barh(y, ours, color=ACCENT, height=0.6, label="our run did the same")
    for i, (a, b) in enumerate(zip(ours, totals)):
        ax.text(b + 0.8, i, f"{a} of {b}", va="center", fontsize=8, color=INK)
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=9, color=INK)
    ax.invert_yaxis()
    ax.set_xlim(0, max(totals) * 1.25)
    ax.set_xlabel("names", color=MUTE, fontsize=9)
    ax.legend(frameon=False, fontsize=8, loc="upper center",
              bbox_to_anchor=(0.5, -0.32), ncol=2)
    ax.set_title("The rebalance replaced most of the list; the run followed it",
                 fontsize=9, color=INK, loc="left")
    _style(ax)
    return fig
