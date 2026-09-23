#!/usr/bin/env python3
"""THE LANDSCAPE FIGURE for the exhaustive n <= 38 classification.

Reads ``catalog/classification_n38.json`` (built by ``build_catalog.py``) and
draws the (injections n, output width k) plane, with each distinct gate class as
a jittered marker coloured by its highest gate level -- T-only, CS-level, or
CCZ-level.  Read as a picture of "what magic can you get, and how much does it
cost", the panel shows two things at a glance: the frontier of achievable
(n, k) pairs, and the fact that CCZ-level content is confined to a small region
and never appears as a pure CCZ anywhere in the window.

Every point here is a *classified* class, not a search record: within this
panel, absence of a point is a proof of nonexistence.  That is not true of the
figures that mix in beyond-window records -- see ``../../../theory/figures/``.

The grey wedge is the only thing in the panel that is not an absence claim: it
marks n+k > 38, beyond the Nezami--Haah search frontier, and it is deliberately
FULL of classes -- reaching those is the point of fixing n rather than n+k.

Outputs ``catalog/landscape_n38.png`` and ``.pdf``.

Needs matplotlib.  Run:  python plot_landscape.py
"""
import json
import os
import tempfile
from pathlib import Path
from collections import defaultdict

# Matplotlib/fontconfig try to write user-level caches even with the headless
# backend. Use a predictable writable temporary cache on clusters and in
# sandboxed reproduction environments.
PLOT_CACHE = Path(tempfile.gettempdir()) / "magic-state-factories-plot-cache"
PLOT_CACHE.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(PLOT_CACHE / "matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(PLOT_CACHE))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

HERE = Path(__file__).resolve().parent

#: PDF metadata that would otherwise make an identical figure differ between
#: rebuilds: matplotlib stamps /CreationDate with the wall clock, so a rebuilt
#: figure appeared as a modified file in `git status` with nothing about the plot
#: changed.  None omits the key.
PDF_METADATA = {"CreationDate": None}
recs = json.loads((HERE / "catalog" / "classification_n38.json")
                  .read_text(encoding="utf-8"))["factories"]

# Okabe--Ito colourblind-safe palette, one colour per gate level.
LEVEL = {
    1: ("#0072B2", "T-only  (max degree 1)"),
    2: ("#E69F00", "CS-level  (max degree 2)"),
    3: ("#D55E00", "CCZ-level  (max degree 3)"),
}
MARK = {1: "o", 2: "s", 3: "^"}

plt.rcParams.update({
    "font.size": 11, "axes.titlesize": 13, "figure.dpi": 140,
    "font.family": "DejaVu Sans",
})

fig, (ax, axb) = plt.subplots(
    1, 2, figsize=(13.2, 5.4), gridspec_kw={"width_ratios": [2.35, 1]})

# ----------------------------------------------------------- main (n,k) panel
# Shade the region BEYOND THE NEZAMI--HAAH SEARCH FRONTIER, n+k > 38.  That
# frontier is a statement about the prior classification, which enumerated
# triorthogonal matrices of total size n+k <= 38, NOT about this window: the
# quotient classification fixes n <= 38 and lets k run free, so it reaches this
# region and populates it -- 33 of the 74 classes below have n+k > 38.  The
# shading marks where those classes are new relative to Nezami--Haah.
ax.fill([31.5, 40, 40, 37.6], [6.5, 6.5, 0.4, 0.4], color="0.92",
        zorder=0, lw=0)
ax.plot([31.5, 37.6], [6.5, 0.4], ls="--", color="0.55", lw=1.1, zorder=1)
ax.text(39.4, 5.1, "$n+k>38$\n(beyond Nezami–Haah)", rotation=-90, color="0.5",
        fontsize=8, ha="center", va="center")

# group classes by (n,k) and jitter horizontally so co-located points show
# while k stays exactly on its integer grid line.
bynk = defaultdict(list)
for r in recs:
    bynk[(r["n"], r["k"])].append(r)

for (n, k), grp in bynk.items():
    grp = sorted(grp, key=lambda r: (r["max_level"], r["gate"]))
    m = len(grp)
    span = min(0.16 * (m - 1), 0.62)          # total horizontal spread
    offs = [0.0] if m == 1 else [(-span/2 + span*i/(m-1)) for i in range(m)]
    for r, off in zip(grp, offs):
        lv = r["max_level"]
        ax.scatter(n + off, k, s=48, marker=MARK[lv],
                   facecolor=LEVEL[lv][0], edgecolor="white", linewidth=0.6,
                   zorder=4, alpha=0.95)

# annotate a few landmark frontier points (target xy, text xytext, alignment)
notes = [
    (15, 1, 15, 1.7, "smallest $T$", "center", "bottom"),
    (28, 2, 25.2, 2.75, "first beyond-$T$\n($T{\\cdot}CS$)", "center", "bottom"),
    # (31, 3, 25.6, 3.55, "sym. CCZ\n(punctured RM)", "center", "bottom"),
    (31, 5, 31, 5.75, "$[[31,5,3]]$;  no $k{=}6$", "center", "bottom"),
]
for n, k, tx, ty, txt, ha, va in notes:
    ax.annotate(txt, (n, k), (tx, ty), fontsize=7.5, color="0.25",
                ha=ha, va=va,
                arrowprops=dict(arrowstyle="-", color="0.6", lw=0.6))

ax.set_xlim(13.5, 40)
ax.set_ylim(0.3, 6.7)
ax.set_yticks(range(1, 7))
ax.set_xlabel("injected resources  $n$")
ax.set_ylabel("output width  $k$")
ax.set_title("Distance-3 gate landscape  ($n\\leq 38$, exhaustive)")
ax.grid(True, color="0.9", lw=0.7)
ax.set_axisbelow(True)

legend_elems = [
    Line2D([0], [0], marker=MARK[lv], color="none", markerfacecolor=LEVEL[lv][0],
           markeredgecolor="white", markersize=9, label=LEVEL[lv][1])
    for lv in (1, 2, 3)]
legend_elems.append(Patch(facecolor="0.92",
                          label="$n+k>38$: beyond Nezami–Haah"))
ax.legend(handles=legend_elems, loc="upper left", frameon=False, fontsize=9,
          handletextpad=0.4, borderpad=0.3)

# ----------------------------------------------------- right: diversity by n
byn = defaultdict(lambda: defaultdict(int))
for r in recs:
    byn[r["n"]][r["max_level"]] += 1
ns = sorted(byn)
bottom = [0] * len(ns)
for lv in (1, 2, 3):
    vals = [byn[n][lv] for n in ns]
    axb.barh(ns, vals, left=bottom, color=LEVEL[lv][0], height=0.72,
             edgecolor="white", linewidth=0.5, label=LEVEL[lv][1].split("  ")[0])
    bottom = [b + v for b, v in zip(bottom, vals)]
for n in ns:
    tot = sum(byn[n].values())
    axb.text(tot + 0.15, n, str(tot), va="center", fontsize=8, color="0.3")
axb.set_yticks(ns)
axb.set_ylim(13.5, 39)
axb.set_xlim(0, 22)
axb.set_xlabel("# distinct gate classes")
axb.set_ylabel("$n$")
axb.set_title("Gate diversity per $n$")
axb.grid(True, axis="x", color="0.9", lw=0.7)
axb.set_axisbelow(True)
axb.invert_yaxis()

fig.suptitle(
    "Classification-frontier magic-state factories beyond $T$  —  "
    f"{len(recs)} distinct $(n,k,d{{=}}3)$ output gates",
    fontsize=13, y=1.005)
fig.tight_layout(rect=[0, 0, 1, 0.98])

for ext in ("png", "pdf"):
    p = HERE / f"catalog/landscape_n38.{ext}"
    fig.savefig(p, bbox_inches="tight",
                metadata=PDF_METADATA if ext == "pdf" else None)
    print("wrote", p)
