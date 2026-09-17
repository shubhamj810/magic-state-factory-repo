#!/usr/bin/env python3
"""THE CROSS-CUTTING FIGURE -- everything this repository knows, on one plane.

This is the only script in the repository that reads the catalogues from more
than one workflow. It lives in `theory/` because this is where those independently
reproducible classifications are compared and interpreted together.

It merges

  ../../classification/legacy/exhaustive_n38/catalog/classification_n38.json
  ../../classification/legacy/rank7_census/catalog/census_r7.json
  ../../symmetry_sat_search/catalog/factories.json

and plots them keyed by phase-polynomial degree (marker SHAPE) and exact
minimal T-count (marker COLOUR).  Missing catalogues are skipped with a warning,
so the figure degrades gracefully if you have only built part of the repository.

**The bands are the point.**  A marker inside the green band is a classified
class: nothing else exists there.  A marker in the plain region is the best a
targeted search found: something better may well exist. Conflating the two is
the easiest mistake to make when reading a landscape plot, so the bands are
drawn before the data.

  * shape  = Clifford-reduced phase-polynomial degree  (deg 1 = o, 2 = s,
             3 = ^, 4 = D)  -- see `poly_degree` in the catalogues.
  * colour = exact minimal T-count  (Amy--Mosca / RM min-weight Z_8 coset),
             a sequential magnitude, drawn on the `turbo` ramp (see CMAP below
             if you want to change it).  Gates with no finite level-3
             T-count (sqrt(T) pi/8 rotations; C^mZ/C^mS needing ancillas) are
             drawn as hollow grey markers.
  * ring   = distance 4 or more; unringed points are d = 3.  Note that a
             ringed point at d >= 5 is a LOWER bound: the fault enumerator is
             exact only through weight 4.

Only LEVEL-3, DISTANCE >= 3 rows are plotted, because that is exactly what the
bands claim to have classified; `merged_records` explains why and lists every
excluded row on stdout.

Banding, by how strong the claim behind each region is:

  n <= 38  green   exhaustive quotient classification, EVERY check count r
                   (classification/legacy/exhaustive_n38); the dotted diagonal
                   n + k = 38 is the edge of that window
  n <= 44  blue    exhaustive census for r <= 7 check qubits
                   (classification/legacy/rank7_census)
  n >  44  plain   targeted search only -- best known, NOT a classified maximum
                   (symmetry_sat_search)

Writes, both next to this script in theory/figures/:
  landscape_all.{png,pdf}       -- the banded (n, k) landscape (level 3, d >= 3)
  factory_catalog.{png,pdf}     -- the search catalogue alone, faceted by
                                   distance, so every level and distance
                                   appears with its own panel

Needs matplotlib.  Run:  python landscape_all.py
"""
import json
import os
import tempfile
from pathlib import Path
from collections import Counter, defaultdict

# Keep Matplotlib and fontconfig caches out of the user's home directory. This
# also makes headless cluster/sandbox runs quiet and reproducible.
PLOT_CACHE = Path(tempfile.gettempdir()) / "magic-state-factories-plot-cache"
PLOT_CACHE.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(PLOT_CACHE / "matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(PLOT_CACHE))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.colors import BoundaryNorm
from matplotlib.cm import ScalarMappable

HERE = Path(__file__).resolve().parent

#: PDF metadata that would otherwise make an identical figure differ between
#: rebuilds: matplotlib stamps /CreationDate with the wall clock, so a rebuilt
#: figure appeared as a modified file in `git status` with nothing about the plot
#: changed.  None omits the key.
PDF_METADATA = {"CreationDate": None}
REPO = HERE.parent.parent

N38 = REPO / "classification" / "legacy" / "exhaustive_n38" / "catalog" / "classification_n38.json"
R7 = REPO / "classification" / "legacy" / "rank7_census" / "catalog" / "census_r7.json"
SEARCH = REPO / "symmetry_sat_search" / "catalog" / "factories.json"

REGIME_EXHAUSTIVE = "exhaustive n<=38"
REGIME_CENSUS = "census r<=7"
REGIME_RECORD = "record"


def _load(path, regime):
    """One catalogue, tagged with the regime it belongs to.  A missing file is
    a warning, not an error -- build what you have."""
    if not path.exists():
        print(f"WARNING: {path.relative_to(REPO)} not found; skipping the "
              f"{regime!r} layer. Build it with that directory's "
              f"build_catalog.py.")
        return []
    blob = json.load(open(path))
    rows = blob["factories"] if isinstance(blob, dict) else blob
    out = []
    for r in rows:
        rec = dict(r)
        rec["regime"] = regime
        # the search catalogue names its gate differently and has no
        # poly_degree for a couple of rows; normalise what the plot needs
        rec.setdefault("poly_degree", None)
        rec.setdefault("t_count", None)
        out.append(rec)
    return out


def merged_records():
    """Every LEVEL-3, DISTANCE >= 3 catalogued factory, regime-tagged.

    Both restrictions exist for honesty, not tidiness.  The bands this figure
    draws claim "exhaustive classification" over a region, and both windows are
    complete only for *level-3, distance >= 3* factories.  A row outside either
    restriction, plotted inside a band, would read as a classified class the
    classification had somehow missed -- when in fact it is outside what the
    band claims:

    * **level.** The windows are statements about level-3 (pi/4 rotation)
      factories; level-2 and level-4 rows reuse the same column formalism at a
      different rotation angle.
    * **distance.** The windows are statements about distance >= 3 factories.
      Distance-2 search records live at much smaller ``n`` for the same ``k``
      -- they are cheap because they are barely protected -- so plotting them
      unmarked inside the green band put ``k = 5`` and ``k = 6`` markers at
      ``n <= 26``, contradicting the very result the band certifies (largest
      width ``k = 5``, uniquely at ``[[31,5,3]]``, and no ``k = 6`` at all).

    Both excluded sets are listed on stdout, never dropped silently.  The
    per-distance ``factory_catalog`` figure below is where the distance-2 rows
    are shown: it facets the search catalogue BY distance, so nothing there can
    be mistaken for a classified class.
    """
    kept = (_load(N38, REGIME_EXHAUSTIVE) + _load(R7, REGIME_CENSUS)
            + _load(SEARCH, REGIME_RECORD))

    def _report(rows, reason, field):
        items = ", ".join(f"[[{r['n']},{r['k']},{r['d']}]] ({field}={r[field]})"
                          for r in sorted(rows, key=lambda r: (r[field], r["n"])))
        print(f"NOTE: {len(rows)} catalogued factories are {reason} and are not "
              f"plotted here (the classification windows are level-3, "
              f"distance >= 3 statements): {items}")

    wrong_level = [r for r in kept if r.get("level", 3) != 3]
    if wrong_level:
        _report(wrong_level, "not level 3", "level")
    kept = [r for r in kept if r.get("level", 3) == 3]

    low_distance = [r for r in kept if r["d"] < 3]
    if low_distance:
        _report(low_distance, "below distance 3", "d")
    return [r for r in kept if r["d"] >= 3]

# ------------------------------------------------------------------- encodings
# marker shape per phase-polynomial degree
DEG_MARK = {1: "o", 2: "s", 3: "^", 4: "D"}
DEG_LABEL = {1: "degree 1  ($T$)", 2: "degree 2  ($CS$)",
             3: "degree 3  ($CCZ$)", 4: "degree 4  ($C^3Z$)"}

# T-count colour ramp.  `turbo` orders cheap->costly as blue->green->red; it is
# chosen for how many distinct integer counts stay distinguishable (1..11 here),
# which a perceptually uniform ramp does less well at this many steps.  Swap the
# name here to change every panel and both colourbars at once.
CMAP = plt.get_cmap("turbo")
NA_FACE = "white"        # T-count not defined (level-4 gates)
NA_EDGE = "0.55"

# ---------------------------------------------------------------- search regions
# Boundaries of the two exhaustive windows (half-integer so they sit between
# integer n values).
N_EXHAUSTIVE = 38        # quotient classification: every r
N_CENSUS = 44            # product-T census: r <= 7
GREEN_FILL, GREEN_LINE = "#e7f2e8", "#3f7d4c"
BLUE_FILL, BLUE_LINE = "#eaf1fa", "#3b78b5"
RING_EDGE = "#111111"    # distance-4 ring

plt.rcParams.update({
    "font.size": 11, "axes.titlesize": 13, "figure.dpi": 140,
    "font.family": "DejaVu Sans",
})


def tcolor(t, norm):
    return CMAP(norm(t))


def jitter_offsets(m):
    """Horizontal offsets so co-located (n,k) points fan out but k stays on grid."""
    if m == 1:
        return [0.0]
    span = min(0.16 * (m - 1), 0.62)
    return [(-span / 2 + span * i / (m - 1)) for i in range(m)]


def scatter_group(ax, n, k, grp, norm, ring_d4=False):
    """Plot the DISTINCT marker kinds at grid point (n,k): one marker per unique
    (distance, phase-poly degree, T-count) triple.  Repeated identical kinds are
    collapsed to a single marker for clarity -- the per-n side panel carries the
    full multiplicity.  With ring_d4, distance-4 points get an outer ring."""
    seen, uniq = set(), []
    for r in sorted(grp, key=lambda r: (r["d"], r["poly_degree"],
                                        r["t_count"] if r["t_count"] is not None else 99)):
        key = (r["d"], r["poly_degree"], r["t_count"])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(r)
    for r, off in zip(uniq, jitter_offsets(len(uniq))):
        mk = DEG_MARK.get(r["poly_degree"], "P")
        if ring_d4 and r["d"] >= 4:
            # outer ring, drawn under the marker so the fill colour stays readable
            ax.scatter(n + off, k, s=100, marker="o", facecolor="none",
                       edgecolor=RING_EDGE, linewidth=1.1, zorder=3.5)
        if r["t_count"] is None:
            ax.scatter(n + off, k, s=52, marker=mk, facecolor=NA_FACE,
                       edgecolor=NA_EDGE, linewidth=1.1, zorder=4, hatch="////")
        else:
            ax.scatter(n + off, k, s=50, marker=mk, facecolor=tcolor(r["t_count"], norm),
                       edgecolor="white", linewidth=0.6, zorder=4, alpha=0.97)


def make_norm(tvals):
    """Discrete boundary norm over the integer T-counts present."""
    lo, hi = min(tvals), max(tvals)
    bounds = [b - 0.5 for b in range(lo, hi + 2)]
    return BoundaryNorm(bounds, CMAP.N), lo, hi


def degree_legend(degrees):
    return [Line2D([0], [0], marker=DEG_MARK[d], color="none",
                   markerfacecolor="0.35", markeredgecolor="white",
                   markersize=10, label=DEG_LABEL[d]) for d in sorted(degrees)]


# ============================================================= Fig 1: frontier
def plot_frontier():
    """landscape_all.{png,pdf}: every level-3, distance >= 3 catalogued row (all
    regimes, beyond-frontier records included) on the (n,k) plane with the
    search-strength bands, plus a per-n T-count composition side panel."""
    NMAX = 52                     # the panel's horizontal range
    allrecs = merged_records()
    recs = [r for r in allrecs if r["n"] <= NMAX]
    dropped = [r for r in allrecs if r["n"] > NMAX]
    if dropped:
        # No silent caps: say what is not on the figure, and where it lives.
        items = ", ".join(sorted({f"[[{r['n']},{r['k']},{r['d']}]]"
                                  for r in dropped}))
        print(f"NOTE: {len(dropped)} catalogued rows lie beyond n = {NMAX} and "
              f"are outside this panel: {items}. They are all search records "
              f"(symmetry_sat_search/catalog/), never classified classes.")
    # A search record inside an exhaustive band normally lands on an (n,k) cell
    # the classification already occupies.  If one does not, the band's "nothing
    # else exists here" reading needs a caveat, so name the row rather than let a
    # reader infer a gap.  As built this prints nothing: the row that used to
    # trigger it was a [[15,2,3]] with gate 0+1+01 whose two output rows were
    # equal modulo the check span -- the [[15,1,3]] on a spare wire, exact
    # T-count 1 -- and the search builder now rejects such inflated widths.
    # Kept because a future catalogue addition could reintroduce one.
    classified = {(r["n"], r["k"]) for r in recs if r["regime"] != REGIME_RECORD}
    unmatched = sorted({(r["n"], r["k"], r["d"]) for r in recs
                        if r["regime"] == REGIME_RECORD and r["n"] <= N_EXHAUSTIVE
                        and (r["n"], r["k"]) not in classified})
    if unmatched:
        items = ", ".join(f"[[{n},{k},{d}]]" for n, k, d in unmatched)
        print(f"NOTE: {len(unmatched)} search record(s) sit inside the exhaustive "
              f"n <= {N_EXHAUSTIVE} band at an (n,k) cell no classified class "
              f"occupies: {items}. These are circuit representations the quotient "
              f"method omits (outputs dependent modulo the check span), not gates "
              f"the classification missed -- they carry no extra magic content.")

    norm, tlo, thi = make_norm([r["t_count"] for r in recs
                                if r["t_count"] is not None])

    fig, (ax, axb) = plt.subplots(
        1, 2, figsize=(14.6, 5.6), gridspec_kw={"width_ratios": [2.75, 1]})

    XLO, XHI = 13.5, 53.0
    YLO, YHI = 0.3, 7.05
    xg, xb = N_EXHAUSTIVE , N_CENSUS 

    # ------------------------------------------------- search-strength bands
    # green: the exhaustive quotient classification (every check count r).
    ax.axvspan(XLO, xg, facecolor=GREEN_FILL, edgecolor="none", zorder=0)
    ax.axvline(xg, color=GREEN_LINE, lw=1.0, alpha=0.55, zorder=1)
    # blue: still exhaustive, but only for r <= 7 (the n <= 44 product-T census).
    ax.axvspan(xg, xb, facecolor=BLUE_FILL, edgecolor="none", zorder=0)
    ax.axvline(xb, color=BLUE_LINE, lw=1.0, alpha=0.55, zorder=1)
    # beyond xb: deliberately unshaded -- targeted searches only.

    # the Nezami--Haah search frontier n+k = 38, inside the green band
    ax.plot([N_EXHAUSTIVE - YLO, N_EXHAUSTIVE - YHI], [YLO, YHI],
            ls=":", color=GREEN_LINE, lw=1.5, zorder=1.5)
    ax.text(N_EXHAUSTIVE - 3.9, 3.62, "$n+k=38$\n(Nezami–Haah)", color=GREEN_LINE,
            fontsize=7.2, ha="right", va="center", zorder=2, linespacing=1.35)

    # band captions along the top
    ax.text((XLO + xg) / 2, YHI - 0.22,
            "exhaustive classification, every $r$   ($n\\leq38$)",
            color=GREEN_LINE, fontsize=8.2, ha="center", va="center", zorder=2)
    ax.text((xg + xb) / 2, YHI - 0.22, "exhaustive for $r\\leq7$\n($n\\leq44$)",
            color=BLUE_LINE, fontsize=7.6, ha="center", va="center", zorder=2,
            linespacing=1.25)
    bynk = defaultdict(list)
    for r in recs:
        bynk[(r["n"], r["k"])].append(r)
    for (n, k), grp in bynk.items():
        scatter_group(ax, n, k, grp, norm, ring_d4=True)

    notes = [
        (15, 1, 15, 1.62, "smallest $T$", "center", "bottom"),
        (31, 5, 29.5, 5.8, "$[[31,5,3]]$", "center", "bottom"),
        (43, 3, 42.2, 2.15, "census max\n$T{=}5$", "center", "top"),
        (44, 4, 40.9, 4.95, "$[[44,4,3]]$  $T^{\\otimes4}$,\noptimal for $r{\\leq}7$",
         "left", "bottom"),
        (47, 3, 45.9, 2.25, "first pure $CCZ$", "center", "top"),
        # deg 3 at k=6 is a bounded-search UPPER bound (|GL(6,2)| exceeds the
        # exact-enumeration cap) -- see poly_degree_note in the catalogue
        (47, 6, 45.9, 6.05, "$[[47,6,3]]$, $T{=}11$, $\\deg\\leq3$", "right", "center"),
        (51, 5, 51, 5.4, "$[[51,5,3]]$", "center", "bottom"),
        (48, 4, 49.1, 4.35, "$[[48,4,3]]$", "left", "center"),
        (48, 1, 49.1, 1.0, "$[[48,1,4]]$", "left", "center"),
    ]
    for n, k, tx, ty, txt, ha, va in notes:
        ax.annotate(txt, (n, k), (tx, ty), fontsize=7.2, color="0.25", ha=ha, va=va,
                    zorder=6, linespacing=1.3,
                    arrowprops=dict(arrowstyle="-", color="0.6", lw=0.6,
                                    shrinkA=0, shrinkB=6))

    ax.set_xlim(XLO, XHI)
    ax.set_ylim(YLO, YHI)
    ax.set_yticks(range(1, 7))
    ax.set_xticks(range(15, 53, 5))
    ax.set_xlabel("injected resources  $n$")
    ax.set_ylabel("output width  $k$")
    ax.set_title("Landscape by degree (shape), T-count (colour) & distance (ring)")
    ax.grid(True, color="0.87", lw=0.7)
    ax.set_axisbelow(True)

    leg = ax.legend(handles=degree_legend({r["poly_degree"] for r in recs}),
                    loc="upper left", frameon=False, fontsize=8.5,
                    handletextpad=0.4, borderpad=0.3, labelspacing=0.35,
                    title="phase-poly degree")
    leg.get_title().set_fontsize(8.5)
    ax.add_artist(leg)

    region_handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor="none",
               markeredgecolor=RING_EDGE, markeredgewidth=1.1, markersize=11,
               label="distance $\\geq4$  (else $d=3$)"),
        Patch(facecolor=GREEN_FILL, edgecolor=GREEN_LINE, lw=0.7,
              label="$n\\leq38$: exhaustive, all $r$"),
        Patch(facecolor=BLUE_FILL, edgecolor=BLUE_LINE, lw=0.7,
              label="$n\\leq44$: exhaustive, $r\\leq7$"),
    ]
    # below the shape legend, in the empty low-k / low-n corner
    leg2 = ax.legend(handles=region_handles, loc="upper left",
                     bbox_to_anchor=(0.005, 0.775), frameon=False, fontsize=8.5,
                     handletextpad=0.6, borderpad=0.3, labelspacing=0.55)
    leg2.get_frame().set_linewidth(0.6)

    # right panel: T-count composition per n (stacked, same colour scale)
    byn = defaultdict(lambda: defaultdict(int))
    for r in recs:
        byn[r["n"]][r["t_count"]] += 1
    ns = sorted(byn)
    bottom = [0] * len(ns)
    for t in range(tlo, thi + 1):
        vals = [byn[n].get(t, 0) for n in ns]
        if not any(vals):
            continue
        axb.barh(ns, vals, left=bottom, color=tcolor(t, norm), height=0.78,
                 edgecolor="white", linewidth=0.5)
        bottom = [b + v for b, v in zip(bottom, vals)]
    xmax = max(sum(byn[n].values()) for n in ns) + 3
    # same band shading, so the two panels read as one figure
    axb.axhspan(13.5, N_EXHAUSTIVE + 0.5, facecolor=GREEN_FILL, zorder=0, lw=0)
    axb.axhspan(N_EXHAUSTIVE + 0.5, N_CENSUS + 0.5, facecolor=BLUE_FILL, zorder=0, lw=0)
    for n in ns:
        tot = sum(byn[n].values())
        axb.text(tot + 0.3, n, str(tot), va="center", fontsize=7.5, color="0.3",
                 clip_on=True)
    axb.set_yticks(ns)
    axb.tick_params(axis="y", labelsize=8)
    axb.set_ylim(13.5, NMAX + 0.5)
    axb.set_xlim(0, xmax)
    axb.set_xlabel("# catalogued representatives")
    axb.set_ylabel("$n$")
    axb.set_title("T-count composition per $n$")
    axb.grid(True, axis="x", color="0.87", lw=0.7)
    axb.set_axisbelow(True)
    axb.invert_yaxis()

    sm = ScalarMappable(norm=norm, cmap=CMAP)
    cbar = fig.colorbar(sm, ax=axb, ticks=range(tlo, thi + 1), pad=0.02, fraction=0.09)
    cbar.set_label("exact minimal T-count")

    # Spell out the distance census rather than lumping it: every row here is
    # d >= 3 (see merged_records), and d = 5 means "no fault of weight <= 4".
    by_d = Counter(r["d"] for r in recs)
    census = ", ".join(
        f"{by_d[d]} at $d{{\\geq}}5$" if d >= 5 else f"{by_d[d]} at $d{{=}}{d}$"
        for d in sorted(by_d))
    fig.suptitle(
        "Classification frontier and beyond  —  shape = phase-poly degree,  "
        f"colour = exact minimal T-count,  ring = $d{{\\geq}}4$  "
        f"({census})",
        fontsize=12.5, y=1.005)
    fig.tight_layout(rect=[0, 0, 1, 0.98])
    for ext in ("png", "pdf"):
        p = HERE / f"landscape_all.{ext}"
        fig.savefig(p, bbox_inches="tight",
                    metadata=PDF_METADATA if ext == "pdf" else None)
        print("wrote", p)
    plt.close(fig)


# ======================================================= Fig 2: full catalog
def plot_factory():
    """factory_catalog.{png,pdf}: the whole search catalogue
    (symmetry_sat_search/catalog/factories.json), one (n,k) panel per distance,
    same shape/colour encoding.  Unlike the frontier figure this keeps every
    level and every distance -- faceting by distance is what makes that safe --
    so it is where the distance-2 and level-2/4 rows can be read off."""
    facs = json.load(open(SEARCH))["factories"]
    finite = [f["t_count"] for f in facs if f["t_count"] is not None]
    norm, tlo, thi = make_norm(finite)
    ds = sorted({f["d"] for f in facs})

    fig, axes = plt.subplots(2, 2, figsize=(13.4, 9.2))
    axes = axes.ravel()
    for ax, d in zip(axes, ds):
        sub = [f for f in facs if f["d"] == d]
        bynk = defaultdict(list)
        for f in sub:
            bynk[(f["n"], f["k"])].append(f)
        for (n, k), grp in bynk.items():
            scatter_group(ax, n, k, grp, norm)
        ns = [f["n"] for f in sub]
        xpad = max(1.5, 0.05 * (max(ns) - min(ns)))
        ax.set_xlim(min(ns) - xpad - 0.5, max(ns) + xpad + 0.5)
        ax.set_ylim(0.3, 6.7)
        ax.set_yticks(range(1, 7))
        ax.set_xlabel("injected resources  $n$")
        ax.set_ylabel("output width  $k$")
        ax.set_title(f"distance $d={d}$   ({len(sub)} factories)")
        ax.grid(True, color="0.92", lw=0.7)
        ax.set_axisbelow(True)
    for ax in axes[len(ds):]:
        ax.set_visible(False)

    # explicit layout: reserve a right strip for the colourbar and a bottom
    # strip for the shape legend (tight_layout mis-places colourbars over axes).
    fig.subplots_adjust(left=0.06, right=0.87, top=0.92, bottom=0.13,
                        hspace=0.30, wspace=0.16)

    handles = degree_legend({f["poly_degree"] for f in facs})
    handles.append(Line2D([0], [0], marker="o", color="none", markerfacecolor=NA_FACE,
                          markeredgecolor=NA_EDGE, markersize=10,
                          label="T-count n/a\n(π/8, or needs ancillas)"))
    fig.legend(handles=handles, loc="lower center", ncol=len(handles), frameon=False,
               fontsize=9, bbox_to_anchor=(0.47, 0.005),
               title="phase-poly degree (marker shape)")

    sm = ScalarMappable(norm=norm, cmap=CMAP)
    cax = fig.add_axes([0.905, 0.32, 0.016, 0.48])
    cbar = fig.colorbar(sm, cax=cax, ticks=range(tlo, thi + 1))
    cbar.set_label("exact minimal T-count  (colour)")

    fig.suptitle(
        "Factory catalog  —  shape = phase-poly degree,  colour = exact minimal T-count",
        fontsize=13, y=0.965)
    for ext in ("png", "pdf"):
        p = HERE / f"factory_catalog.{ext}"
        fig.savefig(p, bbox_inches="tight",
                    metadata=PDF_METADATA if ext == "pdf" else None)
        print("wrote", p)
    plt.close(fig)


if __name__ == "__main__":
    plot_frontier()
    plot_factory()
