# Exhaustive classifications

This directory contains two complementary complete windows.

| directory | complete window | published catalogue |
|---|---|---|
| [`exhaustive_n38/`](exhaustive_n38/) | every check rank, `n <= 38`, distance 3 | 74 `S_k` classes |
| [`rank7_census/`](rank7_census/) | effective check rank `r <= 7`, `n <= 44`, distance 3 | 21 T-count-5 frontier classes |

The first begins from classified triorthogonal supports and marks every
admissible origin. The second begins from the complete Gillot–Langevin affine
orbit table for `RM(3,7)` and marks all 128 origins of every relevant class.
Both then exhaust legal output frames, use output permutations `S_k` for the
catalogue key, and retain explicit independently verified circuits.

The two windows interlock: the rank-7 census closes low-rank parents throughout
`n <= 38`, while the quotient-dimension bound in `exhaustive_n38` rules out
wide outputs at higher rank. Together they establish the unique `k=5`
`[[31,5,3]]` class and nonexistence of `k=6` in the all-rank window.

These are classifications, not heuristic searches. Only complete runs and
certificates may be used for absence claims. Budget-limited results always
carry `complete=false` and are excluded by catalogue builders.

See each subdirectory README and [`../REPRODUCING.md`](../REPRODUCING.md).
