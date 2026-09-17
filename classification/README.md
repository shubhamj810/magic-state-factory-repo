# Exhaustive classifications

This directory contains a copy of the frontier of the exhaustive length-54
classification and, under [`legacy/`](legacy/), the repository's own
classification stages, which the length-54 classification supersedes.

| directory | complete window | published catalogue |
|---|---|---|
| [`length54/`](length54/) | the exhaustive classification of generalised triorthogonal protocols through `n <= 54`, exact `d_Z >= 3` (Wills, Jain and Singh) — a copy of its data, not its code | its 74 Pareto points for 62 CNOT+S output classes |
| [`legacy/exhaustive_n38/`](legacy/exhaustive_n38/) | legacy: every check rank, `n <= 38`, distance 3 | 74 `S_k` classes |
| [`legacy/rank7_census/`](legacy/rank7_census/) | legacy: effective check rank `r <= 7`, `n <= 44`, distance 3 | 21 T-count-5 frontier classes |
| [`legacy/n40/`](legacy/n40/) | legacy: every check rank, `n = 39, 40`, distance 3 | `S_k` classes with their best-error-coefficient witnesses |
| [`legacy/n48/`](legacy/n48/) | legacy: `n = 41..48`, distance 3 — complete only where its README says so (`n = 47, 48` are partial) | the same, for the completed part |

The length-54 classification subsumes the four legacy windows; its enumeration code
and proofs live in its own repository, and only its published Pareto frontier
is copied here. The master catalogue
([`../master_catalog/`](../master_catalog/)) files the rows it inherited from
`legacy/exhaustive_n38/` and `legacy/rank7_census/` under that classification,
as the regime `exhaustive classification n<=54`, and the 74 Pareto points as
`exhaustive classification n<=54 (Pareto point)`. The `legacy/n40/` and
`legacy/n48/` catalogues are not merged into it.

The four legacy stages are kept for reproducibility, and the master catalogue
cites the catalogue files of the first two; [`legacy/README.md`](legacy/README.md)
says what else depends on them. `exhaustive_n38` begins from classified
triorthogonal supports and marks every admissible origin. `rank7_census` begins
from the complete Gillot–Langevin affine orbit table for `RM(3,7)` and marks
all 128 origins of every relevant class. `n40` and `n48` begin from complete
affine classifications of no-repeated-column unital triorthogonal spaces of
lengths 40 and 42 to 48 (with `RM(3,7)` for the rank-7 words at `n48`), mark
every check parent they carry, and record per class and check rank the witness
of minimum leading error coefficient. All four then exhaust legal output
frames, use output permutations `S_k` for the catalogue key, and retain
explicit independently verified circuits.

The `exhaustive_n38` and `rank7_census` windows interlock: the rank-7 census closes low-rank parents throughout
`n <= 38`, while the quotient-dimension bound in `exhaustive_n38` rules out
wide outputs at higher rank. Together they establish the unique `k=5`
`[[31,5,3]]` class and nonexistence of `k=6` in the all-rank window.

These are classifications, not heuristic searches. Only complete runs and
certificates may be used for absence claims. Budget-limited results always
carry `complete=false` and are excluded by catalogue builders; the one
catalogue built from a partial sweep, `legacy/n48/`'s, is marked `partial`
and states what it does not cover.

See each subdirectory README and [`../REPRODUCING.md`](../REPRODUCING.md).
