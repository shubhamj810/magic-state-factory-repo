# Figures

[`landscape_all.py`](landscape_all.py) is the only script in the repository that
reads more than one code directory, which is why it lives in `theory/` rather
than in any of them. It merges

- [`../../classification/legacy/exhaustive_n38/catalog/classification_n38.json`](../../classification/legacy/exhaustive_n38/catalog/classification_n38.json)
- [`../../classification/legacy/rank7_census/catalog/census_r7.json`](../../classification/legacy/rank7_census/catalog/census_r7.json)
- [`../../symmetry_sat_search/catalog/factories.json`](../../symmetry_sat_search/catalog/factories.json)

and writes two figures:

- `landscape_all.{png,pdf}` — the banded `(n, k)` landscape, plus a side panel
  giving the `T`-count composition per `n`;
- `factory_catalog.{png,pdf}` — the search catalogue alone, one panel per
  distance.

Run it with `../../.venv/bin/python landscape_all.py` from this directory. It needs matplotlib
and nothing else. A missing catalogue is a warning, not an error, so the figure
degrades gracefully if you have built only part of the repository; rebuild a
missing layer with that directory's `build_catalog.py`.

## What the landscape figure plots, and what it leaves out

`landscape_all` plots **level-3, distance-≥3 rows only**, because that is
exactly what its bands claim to have classified. Both exclusions are printed on
stdout when the script runs, never applied silently:

1. **Level-2 and level-4 rows are dropped** (currently 16: nine at level 2,
   seven at level 4). Both classification windows are statements about level-3
   (`T`/`CS`/`CCZ`) factories, so a level-2 or level-4 record inside the `n ≤ 38`
   band would look like a class the classification had missed. It is not — it is
   outside what the band claims.
2. **Distance-2 rows are dropped** (currently 19). Same reason, and it matters
   more than it sounds: a distance-2 factory needs far fewer injections for the
   same width, so plotting these unmarked put `k = 6` at `n = 26` and `k = 5` at
   `n = 16, 18, 20` inside the green band — visibly contradicting the very
   result that band certifies, namely that the largest width in the window is
   `k = 5`, uniquely at `[[31,5,3]]`, with no `k = 6` at all.
3. **Rows beyond `n = 52` are outside the panel** — currently `[[63,4,3]]`,
   `[[64,1,4]]`, `[[66,3,4]]`, `[[85,1,5]]` and `[[141,2,4]]`, all search
   records from [`../../symmetry_sat_search/`](../../symmetry_sat_search/),
   never classified classes.

The distance-2 and level-2/4 rows are not hidden from the repository: they are
the whole content of the companion `factory_catalog` figure, which facets the
search catalogue **by distance**, so nothing in it can be mistaken for a
classified class.

The script also prints a note if a search record ever sits inside an exhaustive
band at an `(n, k)` cell no classified class occupies — which would need
explaining, since the band claims nothing else exists there. **With the
shipped catalogues it prints nothing.** A lift-degenerate circuit would trigger
it — for example a `[[15,2,3]]` with gate `0+1+01`, whose two output rows are
equal modulo the check span, so one CNOT leaves the second output idle (the
`[[15,1,3]]` on a spare wire, exact `T`-count 1 either way). The search builder
rejects inflated widths of that kind, and the check stays in the script as a
guard.

## Encoding

- **Shape** is the CNOT-frame-reduced phase-polynomial degree: `o` degree 1
  (`T`), `s` degree 2 (`CS`), `^` degree 3 (`CCZ`), `D` degree 4 (`C^3Z`). Note
  this is the degree *after* minimising over output CNOT frames, so it is
  usually lower than the largest gate arity in the written gate string — in the
  `n ≤ 38` window no class reaches reduced degree 3 at all, though 28 of the 74
  have a `CCZ` in their phase polynomial. The sibling figure
  [`../../classification/legacy/exhaustive_n38/catalog/landscape_n38.png`](../../classification/legacy/exhaustive_n38/catalog/landscape_n38.png)
  colours by that written arity instead, which is why its markers differ.
- **Colour** is the exact minimal `T`-count (Amy–Mosca / Reed–Muller
  minimum-weight `Z_8` coset), on the `turbo` ramp discretised by a
  `BoundaryNorm` over the integer counts present. Gates with no finite level-3
  `T`-count — `pi/8` rotations, and `C^mZ`/`C^mS` gates needing ancillas — are
  drawn as hollow grey hatched markers. The ramp is set by `CMAP` in the script;
  each figure normalises over the counts in its own panels, so a colour is only
  comparable within one figure.
- **Ring** marks distance 4 or more. With the catalogues as currently built the
  ringed points are `[[48,1,4]]`, `[[52,1,4]]` (twice) and `[[49,1,5]]`; a ring
  at `d ≥ 5` is a lower bound, since the fault enumerator is exact only through
  weight 4. The figure title spells out the distance census rather than lumping
  it — currently 108 rows at `d = 3`, 3 at `d = 4`, 1 at `d ≥ 5`.

At a repeated `(n, k)` the markers fan out horizontally, one per distinct
`(distance, degree, T-count)` triple; identical kinds collapse to a single
marker and the side panel carries the full multiplicity.

## The bands are the point

The horizontal shading records how strong the claim behind each region is, and
it is drawn before the data on purpose.

| band | region | claim |
| --- | --- | --- |
| green | `n <= 38` | exhaustive quotient classification, **every** check count `r` |
| blue | `38 < n <= 44` | exhaustive census, but only for `r <= 7` |
| plain | `n > 44` | targeted search only |

**A marker in the green band is a classified class: nothing else exists there**
— at level 3 and distance ≥ 3, which is exactly what the window classifies.
A marker in the blue band is classified subject to the check-rank bound. **A
marker in the plain region is only the best found** — something better may well
exist, and its absence from a neighbouring cell means nothing. Conflating the
two is the easiest mistake to make when reading a landscape plot. The dotted
diagonal `n + k = 38` inside the green band marks the Nezami–Haah search
frontier; the region beyond it is *reached* by this classification — that is the
point of fixing `n` rather than `n + k` — and 33 of the 74 classes live there.
