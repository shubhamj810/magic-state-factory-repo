# Exhaustive classifications

This directory contains the complete windows this repository ran, and a copy of
the frontier of the classification that subsumes them.

| directory | complete window | published catalogue |
|---|---|---|
| [`exhaustive_n38/`](exhaustive_n38/) | every check rank, `n <= 38`, distance 3 | 74 `S_k` classes |
| [`rank7_census/`](rank7_census/) | effective check rank `r <= 7`, `n <= 44`, distance 3 | 21 T-count-5 frontier classes |
| [`n40/`](n40/) | every check rank, `n = 39, 40`, distance 3 | `S_k` classes with their best-error-coefficient witnesses |
| [`n48/`](n48/) | `n = 41..48`, distance 3 — complete only where its README says so (`n = 47, 48` are partial) | the same, for the completed part |
| [`length54/`](length54/) | the exhaustive classification of generalised triorthogonal protocols through `n <= 54`, exact `d_Z >= 3` (Wills, Jain and Singh) — a copy of its data, not its code | its 74 Pareto points for 62 CNOT+S output classes |

The length-54 classification subsumes the windows above; its enumeration code
and proofs live in its own repository, and only its published Pareto frontier
is copied here. The master catalogue
([`../master_catalog/`](../master_catalog/)) files the rows it inherited from
`exhaustive_n38/` and `rank7_census/` under that classification, as the regime
`exhaustive classification n<=54`, and the 74 Pareto points as
`exhaustive classification n<=54 (Pareto point)`. The `n40/` and `n48/`
catalogues are not merged into it.

The first begins from classified triorthogonal supports and marks every
admissible origin. The second begins from the complete Gillot–Langevin affine
orbit table for `RM(3,7)` and marks all 128 origins of every relevant class.
Both then exhaust legal output frames, use output permutations `S_k` for the
catalogue key, and retain explicit independently verified circuits.

The first two windows interlock: the rank-7 census closes low-rank parents throughout
`n <= 38`, while the quotient-dimension bound in `exhaustive_n38` rules out
wide outputs at higher rank. Together they establish the unique `k=5`
`[[31,5,3]]` class and nonexistence of `k=6` in the all-rank window.

These are classifications, not heuristic searches. Only complete runs and
certificates may be used for absence claims. Budget-limited results always
carry `complete=false` and are excluded by catalogue builders.

See each subdirectory README and [`../REPRODUCING.md`](../REPRODUCING.md).
