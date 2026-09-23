# Complete classification at `n = 39` and `n = 40`: every `S_k` class, every check rank

**319 distinct `(n, k, S_k gate)` classes** of distance-3 factory with 39 or 40 injections, at every check rank, each with the witness circuit of smallest leading error coefficient and the best witness at every check rank the class occurs at.

`a3` is the number of 3-sets of injections that pass every check and act on the outputs: `P_fail ~ a3 p^3` for independent injection errors of rate `p`.  145 classes occur at more than one check rank; for 145 of the 319 the best circuit is not the fewest-check one.

## How it was produced

From the complete affine classification of length-40 no-repeated-column unital triorthogonal spaces (`length40_catalogue.json`, sha256 `8f942ad1645b15e5…`, 110 representatives): every representative marked at every origin -- 40 on the support (n = 39), 2^m - 40 off it (n = 40) and the hyperplane-miss lift (n = 40, rank m + 1) -- giving 44974 check parents, each classified completely by `classify40.py` (`factorylib.parent` quotient V_3(C), every compatible subspace at every width, one witness per S_k class of every GL(k,2) output basis, the witness chosen on the subspace of minimum a3).  No budget, no width cap: the widest compatible subspace met was k = 6, the largest quotient dimension 13.

## How it was verified

* `build_catalog40.py` (via `build_landscape.aggregate`) proves the result files sweep every marking of every representative exactly once, completely; every witness -- the primary one and the best one at every rank -- is relabelled into its canonical `S_k` frame, re-checked from its raw columns by `factorylib.verification.verify` (gate parities, all check-touching parities even, distance exact by enumeration to weight 4) and has its a3 recounted; T-count and reduced degree recomputed by `factorylib.metrics` for `k <= 6`;
* `verify40.py` re-derives every witness with code sharing nothing with the engine and with the master catalogue's own bar, and checks completeness: the `r <= 7` slice equals the rank-7 census table at `n = 39, 40` (both directions), every class of the earlier quotient-search catalogue (`reference/`) is here, every master-catalogue row at `n = 39, 40` is here, and -- when the census landscape has been built -- the per-rank minimum a3 at `r <= 7` agrees with the census parents' exactly.

## Counts

| n | classes | by k | check rank of the best witness | max T |
|---|---|---|---|---|
| 39 | 288 | k=1: 1, k=2: 4, k=3: 14, k=4: 37, k=5: 83, k=6: 149 | r=6: 163, r=7: 113, r=8: 12 | 3 |
| 40 | 31 | k=1: 1, k=2: 4, k=3: 8, k=4: 8, k=5: 10 | r=7: 15, r=8: 12, r=9: 4 | 4 |

T-count histogram: T=1: 10, T=2: 46, T=3: 260, T=4: 3.  Maximum exact T-count 4.

## Coverage, per representative

| representative | m | geometries | max kappa | widest frame | classes | seconds |
|---|---|---|---|---|---|---|
| `length40_m6_001` | 6 | 65 | 13 | 6 | 292 | 1344.7 |
| `length40_m7_001` | 7 | 129 | 11 | 5 | 32 | 15.9 |
| `length40_m7_002` | 7 | 129 | 7 | 5 | 21 | 0.6 |
| `length40_m7_003` | 7 | 129 | 7 | 4 | 53 | 0.5 |
| `length40_m7_004` | 7 | 129 | 8 | 4 | 20 | 0.5 |
| `length40_m7_005` | 7 | 129 | 10 | 5 | 125 | 22.1 |
| `length40_m7_006` | 7 | 129 | 8 | 5 | 31 | 3.0 |
| `length40_m7_007` | 7 | 129 | 6 | 3 | 11 | 0.1 |
| `length40_m7_008` | 7 | 129 | 8 | 5 | 31 | 1.3 |
| `length40_m7_009` | 7 | 129 | 7 | 4 | 20 | 0.2 |
| `length40_m7_010` | 7 | 129 | 6 | 5 | 151 | 6.2 |
| `length40_m7_011` | 7 | 129 | 9 | 5 | 152 | 8.7 |
| `length40_m7_012` | 7 | 129 | 9 | 5 | 32 | 3.6 |
| `length40_m7_013` | 7 | 129 | 7 | 4 | 29 | 0.3 |
| `length40_m7_014` | 7 | 129 | 5 | 3 | 20 | 0.1 |
| `length40_m7_015` | 7 | 129 | 8 | 4 | 33 | 0.3 |
| `length40_m7_016` | 7 | 129 | 5 | 4 | 19 | 0.1 |
| `length40_m7_017` | 7 | 129 | 6 | 5 | 31 | 0.9 |
| `length40_m7_018` | 7 | 129 | 6 | 4 | 29 | 0.2 |
| `length40_m8_discovery_001` | 8 | 257 | 7 | 4 | 46 | 0.5 |
| `length40_m8_discovery_002` | 8 | 257 | 5 | 4 | 20 | 0.2 |
| `length40_m8_discovery_003` | 8 | 257 | 7 | 4 | 4 | 0.4 |
| `length40_m8_discovery_004` | 8 | 257 | 6 | 4 | 4 | 0.2 |
| `length40_m8_discovery_005` | 8 | 257 | 7 | 4 | 20 | 0.2 |
| `length40_m8_discovery_006` | 8 | 257 | 5 | 4 | 12 | 0.1 |
| `length40_m8_discovery_007` | 8 | 257 | 4 | 3 | 10 | 0.0 |
| `length40_m8_discovery_008` | 8 | 257 | 5 | 3 | 3 | 0.1 |
| `length40_m8_discovery_009` | 8 | 257 | 5 | 3 | 11 | 0.0 |
| `length40_m8_discovery_010` | 8 | 257 | 7 | 4 | 62 | 0.3 |
| `length40_m8_discovery_011` | 8 | 257 | 6 | 4 | 19 | 0.1 |
| `length40_m8_discovery_012` | 8 | 257 | 5 | 4 | 61 | 0.2 |
| `length40_m8_discovery_013` | 8 | 257 | 5 | 4 | 19 | 0.1 |
| `length40_m8_discovery_014` | 8 | 257 | 6 | 4 | 19 | 0.1 |
| `length40_m8_discovery_015` | 8 | 257 | 4 | 4 | 19 | 0.1 |
| `length40_m8_discovery_016` | 8 | 257 | 4 | 4 | 19 | 0.1 |
| `length40_m8_discovery_017` | 8 | 257 | 6 | 3 | 3 | 0.1 |
| `length40_m8_discovery_018` | 8 | 257 | 5 | 3 | 3 | 0.1 |
| `length40_m8_discovery_019` | 8 | 257 | 5 | 3 | 11 | 0.0 |
| `length40_m8_discovery_020` | 8 | 257 | 4 | 3 | 10 | 0.0 |
| `length40_m8_discovery_021` | 8 | 257 | 5 | 3 | 3 | 0.1 |
| `length40_m8_discovery_022` | 8 | 257 | 4 | 3 | 11 | 0.0 |
| `length40_m8_discovery_023` | 8 | 257 | 5 | 3 | 10 | 0.0 |
| `length40_m8_discovery_024` | 8 | 257 | 4 | 3 | 10 | 0.0 |
| `length40_m8_discovery_025` | 8 | 257 | 3 | 3 | 10 | 0.0 |
| `length40_m8_discovery_026` | 8 | 257 | 3 | 3 | 10 | 0.0 |
| `length40_m8_discovery_027` | 8 | 257 | 4 | 3 | 10 | 0.0 |
| `length40_m8_discovery_028` | 8 | 257 | 5 | 3 | 12 | 0.0 |
| `length40_m8_discovery_029` | 8 | 257 | 3 | 3 | 10 | 0.0 |
| `length40_m8_discovery_030` | 8 | 257 | 2 | 2 | 4 | 0.0 |
| `length40_m8_discovery_031` | 8 | 257 | 3 | 3 | 10 | 0.0 |
| `length40_m8_discovery_032` | 8 | 257 | 3 | 3 | 10 | 0.0 |
| `length40_m8_discovery_033` | 8 | 257 | 4 | 2 | 5 | 0.0 |
| `length40_m8_discovery_034` | 8 | 257 | 3 | 3 | 3 | 0.0 |
| `length40_m8_discovery_035` | 8 | 257 | 2 | 2 | 2 | 0.0 |
| `length40_m8_discovery_036` | 8 | 257 | 5 | 3 | 3 | 0.1 |
| `length40_m8_discovery_037` | 8 | 257 | 5 | 3 | 3 | 0.1 |
| `length40_m8_discovery_038` | 8 | 257 | 3 | 3 | 10 | 0.0 |
| `length40_m8_discovery_039` | 8 | 257 | 1 | 1 | 1 | 0.0 |
| `length40_m8_discovery_040` | 8 | 257 | 1 | 1 | 1 | 0.0 |
| `length40_m8_discovery_041` | 8 | 257 | 3 | 2 | 5 | 0.0 |
| `length40_m8_discovery_042` | 8 | 257 | 5 | 3 | 3 | 0.1 |
| `length40_m8_discovery_043` | 8 | 257 | 3 | 3 | 10 | 0.0 |
| `length40_m8_discovery_044` | 8 | 257 | 2 | 2 | 4 | 0.0 |
| `length40_m8_discovery_045` | 8 | 257 | 2 | 2 | 4 | 0.0 |
| `length40_m8_discovery_046` | 8 | 257 | 1 | 1 | 1 | 0.0 |
| `length40_m9_discovery_001` | 9 | 513 | 4 | 3 | 3 | 0.0 |
| `length40_m9_discovery_002` | 9 | 513 | 3 | 3 | 3 | 0.0 |
| `length40_m9_discovery_003` | 9 | 513 | 4 | 3 | 11 | 0.0 |
| `length40_m9_discovery_004` | 9 | 513 | 4 | 3 | 3 | 0.0 |
| `length40_m9_discovery_005` | 9 | 513 | 4 | 3 | 10 | 0.0 |
| `length40_m9_discovery_006` | 9 | 513 | 4 | 3 | 6 | 0.0 |
| `length40_m9_discovery_007` | 9 | 513 | 2 | 2 | 4 | 0.0 |
| `length40_m9_discovery_008` | 9 | 513 | 2 | 2 | 4 | 0.0 |
| `length40_m9_discovery_009` | 9 | 513 | 3 | 2 | 2 | 0.0 |
| `length40_m9_discovery_010` | 9 | 513 | 3 | 2 | 2 | 0.0 |
| `length40_m9_discovery_011` | 9 | 513 | 3 | 2 | 2 | 0.0 |
| `length40_m9_discovery_012` | 9 | 513 | 3 | 2 | 5 | 0.0 |
| `length40_m9_discovery_013` | 9 | 513 | 5 | 3 | 21 | 0.0 |
| `length40_m9_discovery_014` | 9 | 513 | 3 | 2 | 2 | 0.0 |
| `length40_m9_discovery_015` | 9 | 513 | 4 | 3 | 20 | 0.0 |
| `length40_m9_discovery_016` | 9 | 513 | 3 | 2 | 2 | 0.0 |
| `length40_m9_discovery_017` | 9 | 513 | 4 | 3 | 10 | 0.0 |
| `length40_m9_discovery_018` | 9 | 513 | 3 | 3 | 10 | 0.0 |
| `length40_m9_discovery_019` | 9 | 513 | 3 | 3 | 10 | 0.0 |
| `length40_m9_discovery_020` | 9 | 513 | 3 | 3 | 10 | 0.0 |
| `length40_m9_discovery_021` | 9 | 513 | 2 | 2 | 2 | 0.0 |
| `length40_m9_discovery_022` | 9 | 513 | 2 | 2 | 4 | 0.0 |
| `length40_m9_discovery_023` | 9 | 513 | 2 | 2 | 4 | 0.0 |
| `length40_m9_discovery_024` | 9 | 513 | 2 | 2 | 4 | 0.0 |
| `length40_m9_discovery_025` | 9 | 513 | 2 | 2 | 4 | 0.0 |
| `length40_m9_discovery_026` | 9 | 513 | 2 | 2 | 4 | 0.0 |
| `length40_m9_discovery_027` | 9 | 513 | 1 | 1 | 1 | 0.0 |
| `length40_m9_discovery_028` | 9 | 513 | 1 | 1 | 1 | 0.0 |
| `length40_m9_discovery_029` | 9 | 513 | 1 | 1 | 1 | 0.0 |
| `length40_m9_discovery_030` | 9 | 513 | 3 | 2 | 2 | 0.0 |
| `length40_m9_discovery_031` | 9 | 513 | 2 | 2 | 4 | 0.0 |
| `length40_m9_discovery_032` | 9 | 513 | 3 | 2 | 2 | 0.0 |
| `length40_m10_class_0001` | 10 | 1025 | 3 | 2 | 5 | 0.0 |
| `length40_m10_class_0002` | 10 | 1025 | 2 | 2 | 4 | 0.0 |
| `length40_m10_class_0003` | 10 | 1025 | 1 | 1 | 1 | 0.0 |
| `length40_m10_class_0004` | 10 | 1025 | 1 | 1 | 1 | 0.0 |
| `length40_m10_class_0005` | 10 | 1025 | 2 | 2 | 4 | 0.0 |
| `length40_m10_class_0006` | 10 | 1025 | 2 | 2 | 2 | 0.0 |
| `length40_m10_class_0007` | 10 | 1025 | 1 | 1 | 1 | 0.0 |
| `length40_m10_class_0008` | 10 | 1025 | 2 | 2 | 4 | 0.0 |
| `length40_m10_class_0009` | 10 | 1025 | 2 | 2 | 2 | 0.0 |
| `length40_m10_class_0010` | 10 | 1025 | 1 | 1 | 1 | 0.0 |
| `length40_m10_class_0011` | 10 | 1025 | 1 | 1 | 1 | 0.0 |
| `length40_m10_class_0012` | 10 | 1025 | 1 | 1 | 1 | 0.0 |
| `length40_m11_class_0001` | 11 | 2049 | 1 | 1 | 1 | 0.0 |

## The classes

Output labels come first, check labels follow; the columns are in the canonical `S_k` output frame, so they deposit exactly the gate shown.  `a3 (rank)` is the best coefficient and the rank of the circuit attaining it; `a3 by rank` the best at each rank.

### n = 39

| # | [[n,k,d]] | N | gate | T | deg | a3 (rank) | a3 by rank |
|---|---|---|---|---|---|---|---|
| 1 | `[[39,1,3]]` | 9 | `T0` | 1 | 1 | 19 (r=8) | r=6: 59, r=7: 23, r=8: 19, r=9: 19, r=10: 19, r=11: 31 |
| 2 | `[[39,2,3]]` | 10 | `T0·CS01` | 2 | 1 | 35 (r=8) | r=6: 101, r=7: 47, r=8: 35, r=9: 45 |
| 3 | `[[39,2,3]]` | 10 | `T0·T1` | 2 | 1 | 35 (r=8) | r=6: 101, r=7: 47, r=8: 35, r=9: 45 |
| 4 | `[[39,2,3]]` | 9 | `T0·T1·CS01` | 1 | 1 | 23 (r=7) | r=6: 75, r=7: 23, r=8: 23, r=9: 23, r=10: 31 |
| 5 | `[[39,2,3]]` | 10 | `CS01` | 3 | 2 | 48 (r=8) | r=6: 90, r=7: 60, r=8: 48, r=9: 66 |
| 6 | `[[39,3,3]]` | 10 | `T0·CS01·CS02·CCZ012` | 2 | 1 | 51 (r=7) | r=6: 109, r=7: 51, r=8: 53 |
| 7 | `[[39,3,3]]` | 11 | `T0·CS01·CS02·CS12·CCZ012` | 3 | 1 | 51 (r=8) | r=6: 133, r=7: 63, r=8: 51, r=9: 67 |
| 8 | `[[39,3,3]]` | 11 | `T0·CS01·CS12` | 3 | 1 | 51 (r=8) | r=6: 133, r=7: 63, r=8: 51, r=9: 67 |
| 9 | `[[39,3,3]]` | 11 | `T0·T1·CS01·CS02·CCZ012` | 3 | 1 | 51 (r=8) | r=6: 133, r=7: 63, r=8: 51, r=9: 67 |
| 10 | `[[39,3,3]]` | 10 | `T0·T1·CS01·CS02·CS12·CCZ012` | 2 | 1 | 51 (r=7) | r=6: 109, r=7: 51, r=8: 53 |
| 11 | `[[39,3,3]]` | 11 | `T0·T1·T2` | 3 | 1 | 51 (r=8) | r=6: 133, r=7: 63, r=8: 51, r=9: 67 |
| 12 | `[[39,3,3]]` | 10 | `T0·T1·T2·CS01` | 2 | 1 | 51 (r=7) | r=6: 109, r=7: 51, r=8: 53 |
| 13 | `[[39,3,3]]` | 11 | `T0·T1·T2·CS01·CS02` | 3 | 1 | 51 (r=8) | r=6: 133, r=7: 63, r=8: 51, r=9: 67 |
| 14 | `[[39,3,3]]` | 10 | `T0·T1·T2·CS01·CS02·CS12·CCZ012` | 1 | 1 | 23 (r=7) | r=6: 83, r=7: 23, r=8: 23, r=9: 31 |
| 15 | `[[39,3,3]]` | 11 | `T0·CS12·CCZ012` | 3 | 1 | 51 (r=8) | r=6: 133, r=7: 63, r=8: 51, r=9: 67 |
| 16 | `[[39,3,3]]` | 11 | `T0·T2·CS01` | 3 | 1 | 51 (r=8) | r=6: 133, r=7: 63, r=8: 51, r=9: 67 |
| 17 | `[[39,3,3]]` | 10 | `T0·T2·CS01·CS12` | 2 | 1 | 51 (r=7) | r=6: 109, r=7: 51, r=8: 53 |
| 18 | `[[39,3,3]]` | 10 | `CS01·CS02·CCZ012` | 3 | 2 | 64 (r=7) | r=6: 98, r=7: 64, r=8: 74 |
| 19 | `[[39,3,3]]` | 10 | `CS01·CS02·CS12` | 3 | 2 | 64 (r=7) | r=6: 98, r=7: 64, r=8: 74 |
| 20 | `[[39,4,3]]` | 11 | `T0·CS01·CS02·CS03·CCZ012·CCZ013·CCZ023` | 2 | 1 | 69 (r=7) | r=6: 113, r=7: 69 |
| 21 | `[[39,4,3]]` | 11 | `T0·CS01·CS02·CS03·CS12·CS13·CCZ012·CCZ013·CCZ023·CCZ123` | 3 | 1 | 67 (r=7) | r=6: 137, r=7: 67, r=8: 75 |
| 22 | `[[39,4,3]]` | 11 | `T0·CS01·CS02·CS12·CS13·CS23·CCZ012` | 3 | 1 | 67 (r=7) | r=6: 137, r=7: 67, r=8: 75 |
| 23 | `[[39,4,3]]` | 11 | `T0·CS01·CS02·CS13·CS23·CCZ012·CCZ123` | 3 | 1 | 67 (r=7) | r=6: 137, r=7: 67, r=8: 75 |
| 24 | `[[39,4,3]]` | 11 | `T0·CS01·CS12·CS13·CCZ123` | 3 | 1 | 67 (r=7) | r=6: 137, r=7: 67, r=8: 75 |
| 25 | `[[39,4,3]]` | 11 | `T0·T1·CS01·CS02·CS03·CCZ012·CCZ013·CCZ023` | 3 | 1 | 67 (r=7) | r=6: 137, r=7: 67, r=8: 75 |
| 26 | `[[39,4,3]]` | 11 | `T0·T1·CS01·CS02·CS03·CS12·CS13·CCZ012·CCZ013·CCZ023·CCZ123` | 2 | 1 | 69 (r=7) | r=6: 113, r=7: 69 |
| 27 | `[[39,4,3]]` | 11 | `T0·T1·CS01·CS02·CS03·CS12·CS13·CS23·CCZ012·CCZ013·CCZ023·CCZ123` | 3 | 1 | 67 (r=7) | r=6: 137, r=7: 67, r=8: 75 |
| 28 | `[[39,4,3]]` | 11 | `T0·T1·CS01·CS02·CS03·CS23·CCZ012·CCZ013·CCZ023·CCZ123` | 3 | 1 | 67 (r=7) | r=6: 137, r=7: 67, r=8: 75 |
| 29 | `[[39,4,3]]` | 11 | `T0·T1·CS01·CS02·CS12·CS23·CCZ012` | 3 | 1 | 67 (r=7) | r=6: 137, r=7: 67, r=8: 75 |
| 30 | `[[39,4,3]]` | 11 | `T0·T1·CS01·CS02·CS23·CCZ012·CCZ123` | 3 | 1 | 67 (r=7) | r=6: 137, r=7: 67, r=8: 75 |
| 31 | `[[39,4,3]]` | 11 | `T0·T1·CS01·CS23·CCZ023·CCZ123` | 3 | 1 | 67 (r=7) | r=6: 137, r=7: 67, r=8: 75 |
| 32 | `[[39,4,3]]` | 11 | `T0·T1·T2·CS01·CS02·CS03·CS12·CCZ012·CCZ013·CCZ023` | 3 | 1 | 67 (r=7) | r=6: 137, r=7: 67, r=8: 75 |
| 33 | `[[39,4,3]]` | 11 | `T0·T1·T2·CS01·CS02·CS03·CS12·CS13·CCZ012·CCZ013·CCZ023·CCZ123` | 3 | 1 | 67 (r=7) | r=6: 137, r=7: 67, r=8: 75 |
| 34 | `[[39,4,3]]` | 11 | `T0·T1·T2·CS01·CS02·CS03·CS12·CS13·CS23·CCZ012·CCZ013·CCZ023·CCZ123` | 2 | 1 | 69 (r=7) | r=6: 113, r=7: 69 |
| 35 | `[[39,4,3]]` | 11 | `T0·T1·T2·CS01·CS23` | 3 | 1 | 67 (r=7) | r=6: 137, r=7: 67, r=8: 75 |
| 36 | `[[39,4,3]]` | 11 | `T0·T1·T2·T3·CS01` | 3 | 1 | 67 (r=7) | r=6: 137, r=7: 67, r=8: 75 |
| 37 | `[[39,4,3]]` | 11 | `T0·T1·T2·T3·CS01·CS02·CS03` | 3 | 1 | 67 (r=7) | r=6: 137, r=7: 67, r=8: 75 |
| 38 | `[[39,4,3]]` | 11 | `T0·T1·T2·T3·CS01·CS02·CS03·CS12·CCZ012` | 3 | 1 | 67 (r=7) | r=6: 137, r=7: 67, r=8: 75 |
| 39 | `[[39,4,3]]` | 11 | `T0·T1·T2·T3·CS01·CS02·CS03·CS12·CS13·CCZ012·CCZ013` | 3 | 1 | 67 (r=7) | r=6: 137, r=7: 67, r=8: 75 |
| 40 | `[[39,4,3]]` | 12 | `T0·T1·T2·T3·CS01·CS02·CS03·CS12·CS13·CS23·CCZ012·CCZ013·CCZ023·CCZ123` | 1 | 1 | 39 (r=8) | r=6: 95, r=7: 47, r=8: 39 |
| 41 | `[[39,4,3]]` | 11 | `T0·T1·T2·T3·CS01·CS02·CS12·CCZ012` | 2 | 1 | 69 (r=7) | r=6: 113, r=7: 69 |
| 42 | `[[39,4,3]]` | 11 | `T0·T1·T2·T3·CS01·CS23` | 2 | 1 | 69 (r=7) | r=6: 113, r=7: 69 |
| 43 | `[[39,4,3]]` | 11 | `T0·T1·T3·CS01·CS02·CS12·CCZ012` | 3 | 1 | 67 (r=7) | r=6: 137, r=7: 67, r=8: 75 |
| 44 | `[[39,4,3]]` | 11 | `T0·T1·T3·CS01·CS02·CS12·CS23·CCZ012` | 2 | 1 | 69 (r=7) | r=6: 113, r=7: 69 |
| 45 | `[[39,4,3]]` | 11 | `T0·T1·T3·CS01·CS02·CS13·CCZ012` | 3 | 1 | 67 (r=7) | r=6: 137, r=7: 67, r=8: 75 |
| 46 | `[[39,4,3]]` | 11 | `T0·T1·T3·CS01·CS02·CS13·CS23·CCZ012·CCZ123` | 3 | 1 | 67 (r=7) | r=6: 137, r=7: 67, r=8: 75 |
| 47 | `[[39,4,3]]` | 11 | `T0·CS12·CS13·CCZ012·CCZ013·CCZ123` | 3 | 1 | 67 (r=7) | r=6: 137, r=7: 67, r=8: 75 |
| 48 | `[[39,4,3]]` | 11 | `T0·CS12·CS13·CS23·CCZ012·CCZ013·CCZ023` | 3 | 1 | 67 (r=7) | r=6: 137, r=7: 67, r=8: 75 |
| 49 | `[[39,4,3]]` | 11 | `T0·T2·T3·CS01·CS12` | 3 | 1 | 67 (r=7) | r=6: 137, r=7: 67, r=8: 75 |
| 50 | `[[39,4,3]]` | 11 | `T0·T3·CS01·CS02·CCZ012` | 3 | 1 | 67 (r=7) | r=6: 137, r=7: 67, r=8: 75 |
| 51 | `[[39,4,3]]` | 11 | `T0·T3·CS01·CS02·CS12·CS13·CCZ012` | 3 | 1 | 67 (r=7) | r=6: 137, r=7: 67, r=8: 75 |
| 52 | `[[39,4,3]]` | 11 | `T0·T3·CS01·CS02·CS13·CS23·CCZ012·CCZ123` | 2 | 1 | 69 (r=7) | r=6: 113, r=7: 69 |
| 53 | `[[39,4,3]]` | 11 | `T0·T3·CS01·CS12·CS23` | 3 | 1 | 67 (r=7) | r=6: 137, r=7: 67, r=8: 75 |
| 54 | `[[39,4,3]]` | 11 | `CS01·CS02·CS03·CCZ012·CCZ013·CCZ023` | 3 | 2 | 90 (r=7) | r=6: 102, r=7: 90 |
| 55 | `[[39,4,3]]` | 11 | `CS01·CS02·CS03·CS13·CS23·CCZ012·CCZ123` | 3 | 2 | 90 (r=7) | r=6: 102, r=7: 90 |
| 56 | `[[39,4,3]]` | 11 | `CS01·CS02·CS13·CS23·CCZ012·CCZ013·CCZ023·CCZ123` | 3 | 2 | 90 (r=7) | r=6: 102, r=7: 90 |
| 57 | `[[39,5,3]]` | 11 | `T0·CS01·CS02·CS03·CS04·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034` | 2 | 1 | 123 (r=6) | r=6: 123 |
| 58 | `[[39,5,3]]` | 12 | `T0·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 59 | `[[39,5,3]]` | 12 | `T0·CS01·CS02·CS03·CS04·CS12·CS13·CS24·CS34·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 60 | `[[39,5,3]]` | 12 | `T0·CS01·CS02·CS03·CS12·CS13·CS14·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 61 | `[[39,5,3]]` | 12 | `T0·CS01·CS02·CS03·CS14·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ124·CCZ134·CCZ234` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 62 | `[[39,5,3]]` | 12 | `T0·CS01·CS02·CS12·CS13·CS14·CS23·CS24·CCZ012·CCZ134·CCZ234` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 63 | `[[39,5,3]]` | 12 | `T0·CS01·CS02·CS13·CS14·CS23·CS24·CCZ012·CCZ123·CCZ124·CCZ134·CCZ234` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 64 | `[[39,5,3]]` | 12 | `T0·CS01·CS12·CS13·CS14·CCZ123·CCZ124·CCZ134` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 65 | `[[39,5,3]]` | 12 | `T0·T1·CS01·CS02·CS03·CS04·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 66 | `[[39,5,3]]` | 11 | `T0·T1·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134` | 2 | 1 | 123 (r=6) | r=6: 123 |
| 67 | `[[39,5,3]]` | 12 | `T0·T1·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 68 | `[[39,5,3]]` | 12 | `T0·T1·CS01·CS02·CS03·CS04·CS23·CS24·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ234` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 69 | `[[39,5,3]]` | 12 | `T0·T1·CS01·CS02·CS03·CS12·CS13·CS23·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ123` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 70 | `[[39,5,3]]` | 12 | `T0·T1·CS01·CS02·CS03·CS12·CS13·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 71 | `[[39,5,3]]` | 12 | `T0·T1·CS01·CS02·CS03·CS23·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ123·CCZ124·CCZ134` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 72 | `[[39,5,3]]` | 12 | `T0·T1·CS01·CS02·CS03·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ124·CCZ134·CCZ234` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 73 | `[[39,5,3]]` | 12 | `T0·T1·CS01·CS02·CS12·CS23·CS24·CCZ012·CCZ234` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 74 | `[[39,5,3]]` | 12 | `T0·T1·CS01·CS02·CS23·CS24·CCZ012·CCZ123·CCZ124·CCZ234` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 75 | `[[39,5,3]]` | 12 | `T0·T1·CS01·CS23·CS24·CCZ023·CCZ024·CCZ123·CCZ124·CCZ234` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 76 | `[[39,5,3]]` | 12 | `T0·T1·CS01·CS23·CS24·CS34·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 77 | `[[39,5,3]]` | 12 | `T0·T1·T2·CS01·CS02·CS03·CS04·CS12·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 78 | `[[39,5,3]]` | 12 | `T0·T1·T2·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 79 | `[[39,5,3]]` | 11 | `T0·T1·T2·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234` | 2 | 1 | 123 (r=6) | r=6: 123 |
| 80 | `[[39,5,3]]` | 12 | `T0·T1·T2·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CS34·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 81 | `[[39,5,3]]` | 12 | `T0·T1·T2·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS34·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 82 | `[[39,5,3]]` | 12 | `T0·T1·T2·CS01·CS02·CS03·CS04·CS12·CS34·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ134·CCZ234` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 83 | `[[39,5,3]]` | 12 | `T0·T1·T2·CS01·CS02·CS03·CS12·CS13·CS23·CS34·CCZ012·CCZ013·CCZ023·CCZ123` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 84 | `[[39,5,3]]` | 12 | `T0·T1·T2·CS01·CS02·CS03·CS12·CS13·CS34·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 85 | `[[39,5,3]]` | 12 | `T0·T1·T2·CS01·CS02·CS03·CS12·CS34·CCZ012·CCZ013·CCZ023·CCZ134·CCZ234` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 86 | `[[39,5,3]]` | 12 | `T0·T1·T2·CS01·CS02·CS12·CS34·CCZ012·CCZ034·CCZ134·CCZ234` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 87 | `[[39,5,3]]` | 12 | `T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 88 | `[[39,5,3]]` | 12 | `T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 89 | `[[39,5,3]]` | 11 | `T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CS34·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234` | 2 | 1 | 123 (r=6) | r=6: 123 |
| 90 | `[[39,5,3]]` | 12 | `T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS12·CS13·CS23·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 91 | `[[39,5,3]]` | 12 | `T0·T1·T2·T3·CS01·CS02·CS03·CS12·CS34·CCZ012·CCZ034` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 92 | `[[39,5,3]]` | 12 | `T0·T1·T2·T3·CS01·CS02·CS12·CS34·CCZ012` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 93 | `[[39,5,3]]` | 12 | `T0·T1·T2·T3·T4·CS01·CS02·CS03·CS04·CS12·CCZ012` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 94 | `[[39,5,3]]` | 12 | `T0·T1·T2·T3·T4·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CCZ012·CCZ013·CCZ014` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 95 | `[[39,5,3]]` | 12 | `T0·T1·T2·T3·T4·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CCZ012·CCZ013·CCZ014·CCZ023·CCZ123` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 96 | `[[39,5,3]]` | 12 | `T0·T1·T2·T3·T4·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ123·CCZ124` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 97 | `[[39,5,3]]` | 12 | `T0·T1·T2·T3·T4·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CS34·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234` | 1 | 1 | 55 (r=7) | r=6: 119, r=7: 55 |
| 98 | `[[39,5,3]]` | 12 | `T0·T1·T2·T3·T4·CS01·CS02·CS03·CS04·CS12·CS13·CS23·CCZ012·CCZ013·CCZ023·CCZ123` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 99 | `[[39,5,3]]` | 12 | `T0·T1·T2·T3·T4·CS01·CS02·CS03·CS04·CS12·CS34·CCZ012·CCZ034` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 100 | `[[39,5,3]]` | 11 | `T0·T1·T2·T3·T4·CS01·CS02·CS03·CS12·CS13·CS23·CCZ012·CCZ013·CCZ023·CCZ123` | 2 | 1 | 123 (r=6) | r=6: 123 |
| 101 | `[[39,5,3]]` | 12 | `T0·T1·T2·T3·T4·CS01·CS02·CS12·CCZ012` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 102 | `[[39,5,3]]` | 11 | `T0·T1·T2·T3·T4·CS01·CS02·CS12·CS34·CCZ012` | 2 | 1 | 123 (r=6) | r=6: 123 |
| 103 | `[[39,5,3]]` | 12 | `T0·T1·T2·T3·T4·CS01·CS23` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 104 | `[[39,5,3]]` | 12 | `T0·T1·T2·T4·CS01·CS02·CS03·CS12·CS13·CS23·CCZ012·CCZ013·CCZ023·CCZ123` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 105 | `[[39,5,3]]` | 11 | `T0·T1·T2·T4·CS01·CS02·CS03·CS12·CS13·CS23·CS34·CCZ012·CCZ013·CCZ023·CCZ123` | 2 | 1 | 123 (r=6) | r=6: 123 |
| 106 | `[[39,5,3]]` | 12 | `T0·T1·T2·T4·CS01·CS02·CS03·CS12·CS13·CS24·CCZ012·CCZ013·CCZ023·CCZ123` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 107 | `[[39,5,3]]` | 12 | `T0·T1·T2·T4·CS01·CS02·CS03·CS12·CS13·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 108 | `[[39,5,3]]` | 12 | `T0·T1·T2·T4·CS01·CS02·CS03·CS12·CS14·CS24·CCZ012·CCZ013·CCZ023·CCZ124` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 109 | `[[39,5,3]]` | 12 | `T0·T1·T2·T4·CS01·CS02·CS03·CS12·CS14·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ124·CCZ134·CCZ234` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 110 | `[[39,5,3]]` | 12 | `T0·T1·T2·T4·CS01·CS23·CS34` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 111 | `[[39,5,3]]` | 12 | `T0·T1·T3·CS01·CS02·CS12·CS23·CS24·CS34·CCZ012·CCZ234` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 112 | `[[39,5,3]]` | 12 | `T0·T1·T3·T4·CS01·CS02·CS12·CS23·CCZ012` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 113 | `[[39,5,3]]` | 11 | `T0·T1·T3·T4·CS01·CS02·CS12·CS23·CS24·CS34·CCZ012·CCZ234` | 2 | 1 | 123 (r=6) | r=6: 123 |
| 114 | `[[39,5,3]]` | 12 | `T0·T1·T3·T4·CS01·CS02·CS12·CS34·CCZ012` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 115 | `[[39,5,3]]` | 12 | `T0·T1·T3·T4·CS01·CS02·CS13·CS14·CS23·CCZ012·CCZ123` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 116 | `[[39,5,3]]` | 12 | `T0·T1·T4·CS01·CS02·CS03·CS12·CS13·CCZ012·CCZ013·CCZ023·CCZ123` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 117 | `[[39,5,3]]` | 12 | `T0·T1·T4·CS01·CS02·CS03·CS12·CS13·CS23·CS24·CCZ012·CCZ013·CCZ023·CCZ123` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 118 | `[[39,5,3]]` | 11 | `T0·T1·T4·CS01·CS02·CS03·CS12·CS13·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234` | 2 | 1 | 123 (r=6) | r=6: 123 |
| 119 | `[[39,5,3]]` | 12 | `T0·T1·T4·CS01·CS02·CS03·CS14·CCZ012·CCZ013·CCZ023` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 120 | `[[39,5,3]]` | 12 | `T0·T1·T4·CS01·CS02·CS03·CS14·CS23·CS24·CCZ012·CCZ013·CCZ023·CCZ123·CCZ124` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 121 | `[[39,5,3]]` | 12 | `T0·T1·T4·CS01·CS02·CS03·CS14·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ124·CCZ134·CCZ234` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 122 | `[[39,5,3]]` | 12 | `T0·T1·T4·CS01·CS02·CS12·CS23·CS34·CCZ012` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 123 | `[[39,5,3]]` | 12 | `T0·T1·T4·CS01·CS02·CS14·CS23·CS34·CCZ012·CCZ123·CCZ134` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 124 | `[[39,5,3]]` | 12 | `T0·CS12·CS13·CS14·CCZ012·CCZ013·CCZ014·CCZ123·CCZ124·CCZ134` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 125 | `[[39,5,3]]` | 12 | `T0·CS12·CS13·CS14·CS23·CS24·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ134·CCZ234` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 126 | `[[39,5,3]]` | 12 | `T0·CS12·CS13·CS24·CS34·CCZ012·CCZ013·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 127 | `[[39,5,3]]` | 12 | `T0·T3·T4·CS01·CS02·CS12·CS13·CS24·CCZ012` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 128 | `[[39,5,3]]` | 12 | `T0·T3·T4·CS01·CS02·CS13·CS23·CCZ012·CCZ123` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 129 | `[[39,5,3]]` | 12 | `T0·T3·T4·CS01·CS02·CS34·CCZ012` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 130 | `[[39,5,3]]` | 12 | `T0·T4·CS01·CS02·CS03·CCZ012·CCZ013·CCZ023` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 131 | `[[39,5,3]]` | 12 | `T0·T4·CS01·CS02·CS03·CS12·CS13·CS14·CCZ012·CCZ013·CCZ023·CCZ123` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 132 | `[[39,5,3]]` | 12 | `T0·T4·CS01·CS02·CS03·CS12·CS13·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 133 | `[[39,5,3]]` | 11 | `T0·T4·CS01·CS02·CS03·CS14·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ124·CCZ134·CCZ234` | 2 | 1 | 123 (r=6) | r=6: 123 |
| 134 | `[[39,5,3]]` | 12 | `T0·T4·CS01·CS02·CS12·CS13·CS14·CS23·CS34·CCZ012·CCZ134` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 135 | `[[39,5,3]]` | 12 | `T0·T4·CS01·CS02·CS13·CS23·CS34·CCZ012·CCZ123` | 3 | 1 | 91 (r=7) | r=6: 139, r=7: 91 |
| 136 | `[[39,5,3]]` | 11 | `CS01·CS02·CS03·CS04·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034` | 3 | 2 | 144 (r=6) | r=6: 144 |
| 137 | `[[39,5,3]]` | 11 | `CS01·CS02·CS03·CS04·CS14·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ124·CCZ134·CCZ234` | 3 | 2 | 144 (r=6) | r=6: 144 |
| 138 | `[[39,5,3]]` | 11 | `CS01·CS02·CS03·CS14·CS24·CS34·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ124·CCZ134·CCZ234` | 3 | 2 | 144 (r=6) | r=6: 144 |
| 139 | `[[39,5,3]]` | 11 | `CS01·CS02·CS04·CS13·CS14·CS23·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ034·CCZ123·CCZ124` | 3 | 2 | 144 (r=6) | r=6: 144 |
| 140 | `[[39,6,3]]` | 12 | `T0·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 141 | `[[39,6,3]]` | 12 | `T0·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS25·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ235·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 142 | `[[39,6,3]]` | 12 | `T0·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS15·CS25·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ235·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 143 | `[[39,6,3]]` | 12 | `T0·CS01·CS02·CS03·CS04·CS12·CS13·CS15·CS24·CS25·CS34·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ145·CCZ234·CCZ235` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 144 | `[[39,6,3]]` | 12 | `T0·CS01·CS02·CS03·CS04·CS15·CS25·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ125·CCZ135·CCZ145·CCZ235·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 145 | `[[39,6,3]]` | 12 | `T0·CS01·CS02·CS03·CS12·CS13·CS14·CS15·CS24·CS25·CS34·CS35·CCZ012·CCZ013·CCZ023·CCZ123·CCZ145·CCZ234·CCZ235·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 146 | `[[39,6,3]]` | 12 | `T0·CS01·CS02·CS03·CS14·CS15·CS24·CS25·CS34·CS35·CCZ012·CCZ013·CCZ023·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 147 | `[[39,6,3]]` | 12 | `T0·CS01·CS02·CS12·CS13·CS14·CS15·CS23·CS24·CS25·CCZ012·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 148 | `[[39,6,3]]` | 12 | `T0·CS01·CS02·CS13·CS14·CS15·CS23·CS24·CS25·CCZ012·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 149 | `[[39,6,3]]` | 12 | `T0·CS01·CS12·CS13·CS14·CS15·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 150 | `[[39,6,3]]` | 12 | `T0·T1·CS01·CS02·CS03·CS04·CS05·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 151 | `[[39,6,3]]` | 12 | `T0·T1·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS24·CS25·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 152 | `[[39,6,3]]` | 12 | `T0·T1·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS24·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 153 | `[[39,6,3]]` | 12 | `T0·T1·CS01·CS02·CS03·CS04·CS05·CS23·CS24·CS25·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ234·CCZ235·CCZ245` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 154 | `[[39,6,3]]` | 12 | `T0·T1·CS01·CS02·CS03·CS04·CS05·CS23·CS24·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 155 | `[[39,6,3]]` | 12 | `T0·T1·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CS25·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 156 | `[[39,6,3]]` | 12 | `T0·T1·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS25·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ235·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 157 | `[[39,6,3]]` | 12 | `T0·T1·CS01·CS02·CS03·CS04·CS23·CS24·CS25·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ125·CCZ135·CCZ145·CCZ234·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 158 | `[[39,6,3]]` | 12 | `T0·T1·CS01·CS02·CS03·CS04·CS25·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ125·CCZ135·CCZ145·CCZ235·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 159 | `[[39,6,3]]` | 12 | `T0·T1·CS01·CS02·CS03·CS12·CS13·CS23·CS24·CS25·CS34·CS35·CCZ012·CCZ013·CCZ023·CCZ123·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 160 | `[[39,6,3]]` | 12 | `T0·T1·CS01·CS02·CS03·CS12·CS13·CS24·CS25·CS34·CS35·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234·CCZ235·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 161 | `[[39,6,3]]` | 12 | `T0·T1·CS01·CS02·CS03·CS23·CS24·CS25·CS34·CS35·CCZ012·CCZ013·CCZ023·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 162 | `[[39,6,3]]` | 12 | `T0·T1·CS01·CS02·CS03·CS24·CS25·CS34·CS35·CCZ012·CCZ013·CCZ023·CCZ124·CCZ125·CCZ134·CCZ135·CCZ234·CCZ235·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 163 | `[[39,6,3]]` | 12 | `T0·T1·CS01·CS02·CS12·CS23·CS24·CS25·CCZ012·CCZ234·CCZ235·CCZ245` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 164 | `[[39,6,3]]` | 12 | `T0·T1·CS01·CS02·CS23·CS24·CS25·CCZ012·CCZ123·CCZ124·CCZ125·CCZ234·CCZ235·CCZ245` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 165 | `[[39,6,3]]` | 12 | `T0·T1·CS01·CS23·CS24·CS25·CCZ023·CCZ024·CCZ025·CCZ123·CCZ124·CCZ125·CCZ234·CCZ235·CCZ245` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 166 | `[[39,6,3]]` | 12 | `T0·T1·CS01·CS23·CS24·CS25·CS34·CS35·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 167 | `[[39,6,3]]` | 12 | `T0·T1·CS01·CS23·CS24·CS35·CS45·CCZ023·CCZ024·CCZ035·CCZ045·CCZ123·CCZ124·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 168 | `[[39,6,3]]` | 12 | `T0·T1·T2·CS01·CS02·CS03·CS04·CS05·CS12·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 169 | `[[39,6,3]]` | 12 | `T0·T1·T2·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 170 | `[[39,6,3]]` | 12 | `T0·T1·T2·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS24·CS25·CS34·CS35·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 171 | `[[39,6,3]]` | 12 | `T0·T1·T2·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS34·CS35·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 172 | `[[39,6,3]]` | 12 | `T0·T1·T2·CS01·CS02·CS03·CS04·CS05·CS12·CS34·CS35·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ134·CCZ135·CCZ234·CCZ235·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 173 | `[[39,6,3]]` | 12 | `T0·T1·T2·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CS34·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 174 | `[[39,6,3]]` | 12 | `T0·T1·T2·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 175 | `[[39,6,3]]` | 12 | `T0·T1·T2·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS34·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234·CCZ235·CCZ245` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 176 | `[[39,6,3]]` | 12 | `T0·T1·T2·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ235·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 177 | `[[39,6,3]]` | 12 | `T0·T1·T2·CS01·CS02·CS03·CS04·CS12·CS34·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 178 | `[[39,6,3]]` | 12 | `T0·T1·T2·CS01·CS02·CS03·CS04·CS12·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ135·CCZ145·CCZ235·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 179 | `[[39,6,3]]` | 12 | `T0·T1·T2·CS01·CS02·CS03·CS12·CS13·CS23·CS34·CS35·CCZ012·CCZ013·CCZ023·CCZ123·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 180 | `[[39,6,3]]` | 12 | `T0·T1·T2·CS01·CS02·CS03·CS12·CS13·CS34·CS35·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234·CCZ235·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 181 | `[[39,6,3]]` | 12 | `T0·T1·T2·CS01·CS02·CS03·CS12·CS34·CS35·CCZ012·CCZ013·CCZ023·CCZ134·CCZ135·CCZ234·CCZ235·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 182 | `[[39,6,3]]` | 12 | `T0·T1·T2·CS01·CS02·CS12·CS34·CS35·CCZ012·CCZ034·CCZ035·CCZ134·CCZ135·CCZ234·CCZ235·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 183 | `[[39,6,3]]` | 12 | `T0·T1·T2·CS01·CS02·CS12·CS34·CS35·CS45·CCZ012·CCZ034·CCZ035·CCZ045·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 184 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 185 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS24·CS25·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 186 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS24·CS25·CS34·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 187 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS24·CS25·CS45·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 188 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS45·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 189 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS23·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 190 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS23·CS45·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ145·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 191 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CS34·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 192 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 193 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 194 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS12·CS13·CS23·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ145·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 195 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·CS01·CS02·CS03·CS12·CS13·CS23·CS45·CCZ012·CCZ013·CCZ023·CCZ045·CCZ123·CCZ145·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 196 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·CS01·CS02·CS12·CS34·CS35·CCZ012·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 197 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T4·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS24·CS25·CS34·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 198 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T4·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS24·CS25·CS34·CS35·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 199 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T4·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS24·CS34·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ234` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 200 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T4·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS23·CS24·CS34·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ134·CCZ234` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 201 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T4·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ045·CCZ123·CCZ145` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 202 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T4·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS25·CS35·CCZ012·CCZ013·CCZ014·CCZ025·CCZ035·CCZ125·CCZ135` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 203 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T4·CS01·CS02·CS03·CS04·CS12·CS13·CS23·CS45·CCZ012·CCZ013·CCZ023·CCZ045·CCZ123` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 204 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T4·CS01·CS02·CS03·CS12·CS13·CS23·CS45·CCZ012·CCZ013·CCZ023·CCZ123` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 205 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T4·CS01·CS02·CS12·CS34·CS35·CS45·CCZ012·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 206 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T4·T5·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ123` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 207 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T4·T5·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS24·CS25·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ123·CCZ124·CCZ125` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 208 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T4·T5·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS24·CS25·CS34·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ123·CCZ124·CCZ125·CCZ134·CCZ234` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 209 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T4·T5·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS24·CS25·CS34·CS35·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ234·CCZ235` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 210 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T4·T5·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS24·CS25·CS34·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245·CCZ345` | 1 | 1 | 151 (r=6) | r=6: 151 |
| 211 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T4·T5·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS24·CS34·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 212 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T4·T5·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS45·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ045·CCZ123·CCZ145` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 213 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T4·T5·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS23·CS24·CS34·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 214 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T4·T5·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS23·CCZ012·CCZ013·CCZ023·CCZ123` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 215 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T4·T5·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS23·CS45·CCZ012·CCZ013·CCZ023·CCZ045·CCZ123` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 216 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T4·T5·CS01·CS02·CS03·CS04·CS05·CS12·CS34·CCZ012·CCZ034` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 217 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T4·T5·CS01·CS02·CS03·CS12·CS13·CS23·CCZ012·CCZ013·CCZ023·CCZ123` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 218 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T4·T5·CS01·CS02·CS12·CS34·CCZ012` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 219 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T4·T5·CS01·CS23·CS45` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 220 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CS34·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 221 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CS35·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 222 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 223 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS25·CS35·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ235` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 224 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS25·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ235·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 225 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS15·CS23·CS25·CS35·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ125·CCZ135·CCZ235` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 226 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS15·CS23·CS25·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ125·CCZ135·CCZ145·CCZ235·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 227 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T5·CS01·CS02·CS03·CS05·CS12·CS34·CS45·CCZ012·CCZ034·CCZ045` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 228 | `[[39,6,3]]` | 12 | `T0·T1·T2·T3·T5·CS01·CS02·CS12·CS34·CS45·CCZ012` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 229 | `[[39,6,3]]` | 12 | `T0·T1·T2·T4·CS01·CS02·CS03·CS12·CS13·CS23·CS34·CS35·CS45·CCZ012·CCZ013·CCZ023·CCZ123·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 230 | `[[39,6,3]]` | 12 | `T0·T1·T2·T4·CS01·CS02·CS03·CS12·CS13·CS24·CS34·CS35·CS45·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234·CCZ235·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 231 | `[[39,6,3]]` | 12 | `T0·T1·T2·T4·CS01·CS02·CS03·CS12·CS14·CS24·CS35·CS45·CCZ012·CCZ013·CCZ023·CCZ124·CCZ135·CCZ145·CCZ235·CCZ245` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 232 | `[[39,6,3]]` | 12 | `T0·T1·T2·T4·T5·CS01·CS02·CS03·CS12·CS13·CS23·CS34·CCZ012·CCZ013·CCZ023·CCZ123` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 233 | `[[39,6,3]]` | 12 | `T0·T1·T2·T4·T5·CS01·CS02·CS03·CS12·CS13·CS23·CS45·CCZ012·CCZ013·CCZ023·CCZ123` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 234 | `[[39,6,3]]` | 12 | `T0·T1·T2·T4·T5·CS01·CS02·CS03·CS12·CS13·CS24·CS25·CS34·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 235 | `[[39,6,3]]` | 12 | `T0·T1·T2·T4·T5·CS01·CS02·CS03·CS12·CS13·CS24·CS25·CS34·CS35·CS45·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234·CCZ235·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 236 | `[[39,6,3]]` | 12 | `T0·T1·T2·T4·T5·CS01·CS02·CS03·CS12·CS13·CS24·CS25·CS45·CCZ012·CCZ013·CCZ023·CCZ123·CCZ245` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 237 | `[[39,6,3]]` | 12 | `T0·T1·T2·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 238 | `[[39,6,3]]` | 12 | `T0·T1·T2·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CS34·CS35·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 239 | `[[39,6,3]]` | 12 | `T0·T1·T2·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS25·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 240 | `[[39,6,3]]` | 12 | `T0·T1·T2·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS25·CS34·CS35·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234·CCZ235` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 241 | `[[39,6,3]]` | 12 | `T0·T1·T2·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS25·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ235·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 242 | `[[39,6,3]]` | 12 | `T0·T1·T2·T5·CS01·CS02·CS03·CS04·CS12·CS15·CS25·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ125` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 243 | `[[39,6,3]]` | 12 | `T0·T1·T2·T5·CS01·CS02·CS03·CS04·CS12·CS15·CS25·CS34·CS35·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ125·CCZ134·CCZ135·CCZ234·CCZ235` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 244 | `[[39,6,3]]` | 12 | `T0·T1·T2·T5·CS01·CS02·CS03·CS04·CS12·CS15·CS25·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ125·CCZ135·CCZ145·CCZ235·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 245 | `[[39,6,3]]` | 12 | `T0·T1·T2·T5·CS01·CS02·CS03·CS12·CS13·CS23·CS34·CS45·CCZ012·CCZ013·CCZ023·CCZ123` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 246 | `[[39,6,3]]` | 12 | `T0·T1·T2·T5·CS01·CS02·CS03·CS12·CS13·CS25·CS34·CS45·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234·CCZ245` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 247 | `[[39,6,3]]` | 12 | `T0·T1·T3·T4·T5·CS01·CS02·CS12·CS23·CS24·CS34·CCZ012·CCZ234` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 248 | `[[39,6,3]]` | 12 | `T0·T1·T3·T4·T5·CS01·CS02·CS12·CS23·CS45·CCZ012` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 249 | `[[39,6,3]]` | 12 | `T0·T1·T3·T5·CS01·CS02·CS12·CS23·CS24·CS34·CS45·CCZ012·CCZ234` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 250 | `[[39,6,3]]` | 12 | `T0·T1·T4·CS01·CS02·CS03·CS12·CS13·CS24·CS25·CS34·CS35·CS45·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234·CCZ235·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 251 | `[[39,6,3]]` | 12 | `T0·T1·T4·T5·CS01·CS02·CS03·CS12·CS13·CS23·CS24·CS25·CS45·CCZ012·CCZ013·CCZ023·CCZ123·CCZ245` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 252 | `[[39,6,3]]` | 12 | `T0·T1·T4·T5·CS01·CS02·CS03·CS12·CS13·CS23·CS24·CS35·CCZ012·CCZ013·CCZ023·CCZ123` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 253 | `[[39,6,3]]` | 12 | `T0·T1·T4·T5·CS01·CS02·CS03·CS12·CS13·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 254 | `[[39,6,3]]` | 12 | `T0·T1·T4·T5·CS01·CS02·CS03·CS12·CS13·CS45·CCZ012·CCZ013·CCZ023·CCZ123` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 255 | `[[39,6,3]]` | 12 | `T0·T1·T4·T5·CS01·CS02·CS03·CS14·CS15·CS23·CS24·CS35·CCZ012·CCZ013·CCZ023·CCZ123·CCZ124·CCZ135` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 256 | `[[39,6,3]]` | 12 | `T0·T1·T4·T5·CS01·CS02·CS03·CS14·CS15·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ124·CCZ134·CCZ234` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 257 | `[[39,6,3]]` | 12 | `T0·T1·T4·T5·CS01·CS02·CS03·CS14·CS15·CS45·CCZ012·CCZ013·CCZ023·CCZ145` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 258 | `[[39,6,3]]` | 12 | `T0·T1·T4·T5·CS01·CS02·CS12·CS23·CS34·CS35·CS45·CCZ012·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 259 | `[[39,6,3]]` | 12 | `T0·T1·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 260 | `[[39,6,3]]` | 12 | `T0·T1·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CS25·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 261 | `[[39,6,3]]` | 12 | `T0·T1·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 262 | `[[39,6,3]]` | 12 | `T0·T1·T5·CS01·CS02·CS03·CS04·CS15·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 263 | `[[39,6,3]]` | 12 | `T0·T1·T5·CS01·CS02·CS03·CS04·CS15·CS23·CS24·CS25·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ125·CCZ234` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 264 | `[[39,6,3]]` | 12 | `T0·T1·T5·CS01·CS02·CS03·CS04·CS15·CS23·CS24·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ135·CCZ145·CCZ234·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 265 | `[[39,6,3]]` | 12 | `T0·T1·T5·CS01·CS02·CS03·CS04·CS15·CS25·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ125·CCZ135·CCZ145·CCZ235·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 266 | `[[39,6,3]]` | 12 | `T0·T1·T5·CS01·CS02·CS03·CS12·CS13·CS23·CS24·CS25·CS34·CS45·CCZ012·CCZ013·CCZ023·CCZ123·CCZ245` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 267 | `[[39,6,3]]` | 12 | `T0·T1·T5·CS01·CS02·CS03·CS12·CS13·CS24·CS34·CS45·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 268 | `[[39,6,3]]` | 12 | `T0·T1·T5·CS01·CS02·CS03·CS15·CS23·CS24·CS25·CS34·CS45·CCZ012·CCZ013·CCZ023·CCZ123·CCZ124·CCZ125·CCZ134·CCZ145·CCZ245` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 269 | `[[39,6,3]]` | 12 | `T0·T1·T5·CS01·CS02·CS03·CS15·CS24·CS34·CS45·CCZ012·CCZ013·CCZ023·CCZ124·CCZ134·CCZ145·CCZ234` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 270 | `[[39,6,3]]` | 12 | `T0·T1·T5·CS01·CS02·CS12·CS23·CS24·CS35·CS45·CCZ012·CCZ234·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 271 | `[[39,6,3]]` | 12 | `T0·CS12·CS13·CS14·CS15·CCZ012·CCZ013·CCZ014·CCZ015·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 272 | `[[39,6,3]]` | 12 | `T0·CS12·CS13·CS14·CS15·CS23·CS24·CS25·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 273 | `[[39,6,3]]` | 12 | `T0·CS12·CS13·CS14·CS15·CS23·CS24·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ035·CCZ045·CCZ125·CCZ134·CCZ234·CCZ235·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 274 | `[[39,6,3]]` | 12 | `T0·CS12·CS13·CS14·CS25·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ025·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ235·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 275 | `[[39,6,3]]` | 12 | `T0·T3·T4·T5·CS01·CS02·CS13·CS23·CS45·CCZ012·CCZ123` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 276 | `[[39,6,3]]` | 12 | `T0·T4·T5·CS01·CS02·CS03·CS12·CS13·CS14·CS15·CS45·CCZ012·CCZ013·CCZ023·CCZ123·CCZ145` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 277 | `[[39,6,3]]` | 12 | `T0·T4·T5·CS01·CS02·CS03·CS12·CS13·CS14·CS25·CS35·CCZ012·CCZ013·CCZ023·CCZ123·CCZ235` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 278 | `[[39,6,3]]` | 12 | `T0·T4·T5·CS01·CS02·CS03·CS14·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ124·CCZ134·CCZ234` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 279 | `[[39,6,3]]` | 12 | `T0·T4·T5·CS01·CS02·CS03·CS45·CCZ012·CCZ013·CCZ023` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 280 | `[[39,6,3]]` | 12 | `T0·T4·T5·CS01·CS02·CS12·CS13·CS14·CS23·CS25·CS34·CS35·CCZ012·CCZ134·CCZ235` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 281 | `[[39,6,3]]` | 12 | `T0·T5·CS01·CS02·CS03·CS04·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 282 | `[[39,6,3]]` | 12 | `T0·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS15·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 283 | `[[39,6,3]]` | 12 | `T0·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS25·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ235·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 284 | `[[39,6,3]]` | 12 | `T0·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS15·CS24·CS34·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ145·CCZ234` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 285 | `[[39,6,3]]` | 12 | `T0·T5·CS01·CS02·CS03·CS12·CS13·CS14·CS15·CS24·CS34·CS45·CCZ012·CCZ013·CCZ023·CCZ123·CCZ145·CCZ234` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 286 | `[[39,6,3]]` | 12 | `T0·T5·CS01·CS02·CS03·CS12·CS13·CS14·CS24·CS25·CS34·CS35·CS45·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234·CCZ235·CCZ245·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 287 | `[[39,6,3]]` | 12 | `T0·T5·CS01·CS02·CS03·CS14·CS24·CS34·CS45·CCZ012·CCZ013·CCZ023·CCZ124·CCZ134·CCZ234` | 3 | 1 | 151 (r=6) | r=6: 151 |
| 288 | `[[39,6,3]]` | 12 | `T0·T5·CS01·CS02·CS13·CS14·CS23·CS24·CS35·CS45·CCZ012·CCZ123·CCZ124·CCZ134·CCZ234·CCZ345` | 3 | 1 | 151 (r=6) | r=6: 151 |

### n = 40

| # | [[n,k,d]] | N | gate | T | deg | a3 (rank) | a3 by rank |
|---|---|---|---|---|---|---|---|
| 289 | `[[40,1,3]]` | 10 | `T0` | 1 | 1 | 16 (r=9) | r=7: 30, r=8: 20, r=9: 16, r=10: 16 |
| 290 | `[[40,2,3]]` | 11 | `T0·CS01` | 2 | 1 | 32 (r=9) | r=7: 52, r=8: 36, r=9: 32, r=10: 44 |
| 291 | `[[40,2,3]]` | 11 | `T0·T1` | 2 | 1 | 32 (r=9) | r=7: 52, r=8: 36, r=9: 32, r=10: 44 |
| 292 | `[[40,2,3]]` | 11 | `T0·T1·CS01` | 1 | 1 | 20 (r=9) | r=7: 38, r=8: 24, r=9: 20 |
| 293 | `[[40,2,3]]` | 9 | `CS01` | 3 | 2 | 72 (r=7) | r=6: 120, r=7: 72 |
| 294 | `[[40,3,3]]` | 11 | `T0·CS01·CS02·CCZ012` | 2 | 1 | 40 (r=8) | r=7: 56, r=8: 40, r=9: 48 |
| 295 | `[[40,3,3]]` | 11 | `T0·T1·CS01·CS02·CS12·CCZ012` | 2 | 1 | 40 (r=8) | r=7: 56, r=8: 40, r=9: 48 |
| 296 | `[[40,3,3]]` | 11 | `T0·T1·T2·CS01` | 2 | 1 | 40 (r=8) | r=7: 56, r=8: 40, r=9: 48 |
| 297 | `[[40,3,3]]` | 11 | `T0·T1·T2·CS01·CS02·CS12·CCZ012` | 1 | 1 | 28 (r=8) | r=7: 42, r=8: 28 |
| 298 | `[[40,3,3]]` | 11 | `T0·T2·CS01·CS12` | 2 | 1 | 40 (r=8) | r=7: 56, r=8: 40, r=9: 48 |
| 299 | `[[40,3,3]]` | 10 | `CS01·CCZ012` | 4 | 2 | 104 (r=7) | r=6: 160, r=7: 104 |
| 300 | `[[40,3,3]]` | 10 | `CS01·CS02` | 4 | 2 | 104 (r=7) | r=6: 160, r=7: 104 |
| 301 | `[[40,3,3]]` | 10 | `CS01·CS02·CS12·CCZ012` | 4 | 2 | 104 (r=7) | r=6: 160, r=7: 104 |
| 302 | `[[40,4,3]]` | 12 | `T0·CS01·CS02·CS03·CCZ012·CCZ013·CCZ023` | 2 | 1 | 56 (r=8) | r=7: 60, r=8: 56 |
| 303 | `[[40,4,3]]` | 12 | `T0·T1·CS01·CS02·CS03·CS12·CS13·CCZ012·CCZ013·CCZ023·CCZ123` | 2 | 1 | 56 (r=8) | r=7: 60, r=8: 56 |
| 304 | `[[40,4,3]]` | 12 | `T0·T1·T2·CS01·CS02·CS03·CS12·CS13·CS23·CCZ012·CCZ013·CCZ023·CCZ123` | 2 | 1 | 56 (r=8) | r=7: 60, r=8: 56 |
| 305 | `[[40,4,3]]` | 11 | `T0·T1·T2·T3·CS01·CS02·CS03·CS12·CS13·CS23·CCZ012·CCZ013·CCZ023·CCZ123` | 1 | 1 | 52 (r=7) | r=7: 52 |
| 306 | `[[40,4,3]]` | 12 | `T0·T1·T2·T3·CS01·CS02·CS12·CCZ012` | 2 | 1 | 56 (r=8) | r=7: 60, r=8: 56 |
| 307 | `[[40,4,3]]` | 12 | `T0·T1·T2·T3·CS01·CS23` | 2 | 1 | 56 (r=8) | r=7: 60, r=8: 56 |
| 308 | `[[40,4,3]]` | 12 | `T0·T1·T3·CS01·CS02·CS12·CS23·CCZ012` | 2 | 1 | 56 (r=8) | r=7: 60, r=8: 56 |
| 309 | `[[40,4,3]]` | 12 | `T0·T3·CS01·CS02·CS13·CS23·CCZ012·CCZ123` | 2 | 1 | 56 (r=8) | r=7: 60, r=8: 56 |
| 310 | `[[40,5,3]]` | 12 | `T0·CS01·CS02·CS03·CS04·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034` | 2 | 1 | 80 (r=7) | r=7: 80 |
| 311 | `[[40,5,3]]` | 12 | `T0·T1·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134` | 2 | 1 | 80 (r=7) | r=7: 80 |
| 312 | `[[40,5,3]]` | 12 | `T0·T1·T2·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234` | 2 | 1 | 80 (r=7) | r=7: 80 |
| 313 | `[[40,5,3]]` | 12 | `T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CS34·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234` | 2 | 1 | 80 (r=7) | r=7: 80 |
| 314 | `[[40,5,3]]` | 12 | `T0·T1·T2·T3·T4·CS01·CS02·CS03·CS12·CS13·CS23·CCZ012·CCZ013·CCZ023·CCZ123` | 2 | 1 | 80 (r=7) | r=7: 80 |
| 315 | `[[40,5,3]]` | 12 | `T0·T1·T2·T3·T4·CS01·CS02·CS12·CS34·CCZ012` | 2 | 1 | 80 (r=7) | r=7: 80 |
| 316 | `[[40,5,3]]` | 12 | `T0·T1·T2·T4·CS01·CS02·CS03·CS12·CS13·CS23·CS34·CCZ012·CCZ013·CCZ023·CCZ123` | 2 | 1 | 80 (r=7) | r=7: 80 |
| 317 | `[[40,5,3]]` | 12 | `T0·T1·T3·T4·CS01·CS02·CS12·CS23·CS24·CS34·CCZ012·CCZ234` | 2 | 1 | 80 (r=7) | r=7: 80 |
| 318 | `[[40,5,3]]` | 12 | `T0·T1·T4·CS01·CS02·CS03·CS12·CS13·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234` | 2 | 1 | 80 (r=7) | r=7: 80 |
| 319 | `[[40,5,3]]` | 12 | `T0·T4·CS01·CS02·CS03·CS14·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ124·CCZ134·CCZ234` | 2 | 1 | 80 (r=7) | r=7: 80 |

## Witness circuits

### 1. `[[39,1,3]]` — T0

- gate `0`, `N = 9` (1 outputs + 8 checks), T-count 1, reduced degree 1, a3 = 19
- source: length40_m8_discovery_007, origin 0; rep_length40_m8_discovery_007.json

```text
[{0,5}, {0,6}, {0,5,6}, {0,7}, {0,5,7}, {0,6,7}, {0,5,6,7}, {1,2,8}, {1,3,8}, {2,3,8}, {0,1,4,8}, {0,2,4,8}, {0,1,3,4,8}, {0,2,3,4,8}, {0,5,8}, {0,1,5,8}, {0,1,2,5,8}, {3,5,8}, {0,2,3,5,8}, {0,4,5,8}, {2,4,5,8}, {0,3,4,5,8}, {2,3,4,5,8}, {0,6,8}, {0,2,6,8}, {0,1,2,6,8}, {3,6,8}, {0,1,3,6,8}, {0,4,6,8}, {1,4,6,8}, {0,3,4,6,8}, {1,3,4,6,8}, {1,5,6,8}, {2,5,6,8}, {1,2,5,6,8}, {7,8}, {5,7,8}, {6,7,8}, {5,6,7,8}]
```

Best witness at each other check rank:

- rank 6 (`N = 7`), a3 = 59; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1}, {0,2}, {1,2,3}, {4}, {0,1,4}, {2,4}, {0,3,4}, {1,3,4}, {0,2,3,4}, {5}, {1,5}, {0,2,5}, {1,2,3,5}, {0,4,5}, {1,4,5}, {2,4,5}, {0,3,4,5}, {1,3,4,5}, {0,2,3,4,5}, {6}, {0,1,6}, {2,6}, {1,2,3,6}, {4,6}, {0,1,4,6}, {2,4,6}, {3,4,6}, {1,3,4,6}, {2,3,4,6}, {0,5,6}, {1,5,6}, {2,5,6}, {1,2,3,5,6}, {0,4,5,6}, {1,4,5,6}, {2,4,5,6}, {3,4,5,6}, {1,3,4,5,6}, {2,3,4,5,6}]
  ```

- rank 7 (`N = 8`), a3 = 23; length40_m7_004, origin 82; rep_length40_m7_004.json

  ```text
  [{0,3}, {0,2,3}, {4}, {0,3,4}, {2,3,4}, {0,1,5}, {0,3,5}, {0,1,2,3,5}, {0,1,4,5}, {0,3,4,5}, {0,1,2,3,4,5}, {0,2,6}, {0,2,4,6}, {5,6}, {1,5,6}, {0,2,5,6}, {2,3,5,6}, {1,2,3,5,6}, {0,4,5,6}, {1,4,5,6}, {0,2,4,5,6}, {0,2,3,4,5,6}, {1,2,3,4,5,6}, {7}, {1,2,7}, {2,3,7}, {1,3,4,7}, {0,5,7}, {1,2,5,7}, {0,2,3,5,7}, {1,3,4,5,7}, {0,6,7}, {1,2,6,7}, {0,2,3,6,7}, {1,3,4,6,7}, {5,6,7}, {1,2,5,6,7}, {2,3,5,6,7}, {1,3,4,5,6,7}]
  ```

- rank 9 (`N = 10`), a3 = 19; length40_m9_discovery_005, origin 296; rep_length40_m9_discovery_005.json

  ```text
  [{0,3}, {0,3,4}, {6}, {5,6}, {0,4,5,6}, {7}, {0,5,7}, {4,5,7}, {0,1,6,7}, {0,2,6,7}, {0,1,2,6,7}, {1,3,6,7}, {2,3,6,7}, {1,2,3,6,7}, {3,4,6,7}, {0,8}, {0,3,8}, {0,3,4,8}, {6,8}, {5,6,8}, {0,4,5,6,8}, {7,8}, {0,5,7,8}, {4,5,7,8}, {0,1,6,7,8}, {0,2,6,7,8}, {0,1,2,6,7,8}, {1,3,6,7,8}, {2,3,6,7,8}, {1,2,3,6,7,8}, {3,4,6,7,8}, {4,9}, {4,6,9}, {4,7,9}, {4,6,7,9}, {4,8,9}, {4,6,8,9}, {4,7,8,9}, {4,6,7,8,9}]
  ```

- rank 10 (`N = 11`), a3 = 19; length40_m10_class_0007, origin 736; rep_length40_m10_class_0007.json

  ```text
  [{0,3}, {0,2,5}, {0,3,5}, {0,4,5}, {0,2,4,5}, {1,3,6}, {2,5,6}, {1,3,5,6}, {4,5,6}, {2,4,5,6}, {6,7}, {1,6,8}, {5,6,8}, {1,5,6,8}, {6,7,8}, {6,9}, {0,7,9}, {0,3,7,9}, {0,2,5,7,9}, {0,3,5,7,9}, {0,4,5,7,9}, {0,2,4,5,7,9}, {1,3,6,7,9}, {2,5,6,7,9}, {1,3,5,6,7,9}, {4,5,6,7,9}, {2,4,5,6,7,9}, {6,8,9}, {1,6,7,8,9}, {5,6,7,8,9}, {1,5,6,7,8,9}, {6,10}, {6,7,10}, {6,8,10}, {6,7,8,10}, {6,9,10}, {6,7,9,10}, {6,8,9,10}, {6,7,8,9,10}]
  ```

- rank 11 (`N = 12`), a3 = 31; length40_m11_class_0001, origin 1920; rep_length40_m11_class_0001.json

  ```text
  [{0,2,8}, {3,8}, {2,3,8}, {1,2,3,8}, {1,2,3,4,8}, {1,2,3,5,8}, {1,2,3,4,5,8}, {1,2,3,6,8}, {1,2,3,4,6,8}, {1,2,3,5,6,8}, {1,2,3,4,5,6,8}, {1,2,3,7,8}, {1,2,3,4,7,8}, {1,2,3,5,7,8}, {1,2,3,4,5,7,8}, {1,2,3,6,7,8}, {1,2,3,4,6,7,8}, {1,2,3,5,6,7,8}, {1,2,3,4,5,6,7,8}, {0,9}, {0,2,8,9}, {3,8,9}, {2,3,8,9}, {0,10}, {0,2,8,10}, {3,8,10}, {2,3,8,10}, {0,9,10}, {0,2,8,9,10}, {3,8,9,10}, {2,3,8,9,10}, {11}, {8,11}, {9,11}, {8,9,11}, {10,11}, {8,10,11}, {9,10,11}, {8,9,10,11}]
  ```

### 2. `[[39,2,3]]` — T0·CS01

- gate `0+01`, `N = 10` (2 outputs + 8 checks), T-count 2, reduced degree 1, a3 = 35
- source: length40_m8_discovery_028, origin 208; rep_length40_m8_discovery_028.json

```text
[{0,1,2}, {3}, {0,1,4}, {0,1,2,4}, {1,5}, {1,3,5}, {1,6}, {4,6}, {3,4,6}, {1,4,5,6}, {1,3,4,5,6}, {1,2,7}, {1,3,7}, {1,2,4,7}, {3,5,7}, {4,5,7}, {1,3,4,6,7}, {5,6,7}, {3,4,5,6,7}, {1,8}, {0,5,8}, {0,2,5,8}, {0,4,5,8}, {0,2,4,5,8}, {1,6,8}, {1,4,7,8}, {2,5,7,8}, {2,4,5,7,8}, {1,4,6,7,8}, {5,6,7,8}, {4,5,6,7,8}, {9}, {6,9}, {7,9}, {6,7,9}, {8,9}, {6,8,9}, {7,8,9}, {6,7,8,9}]
```

Best witness at each other check rank:

- rank 6 (`N = 8`), a3 = 101; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{2}, {1,3}, {1,2,3,4}, {5}, {0,2,5}, {1,3,5}, {0,4,5}, {0,2,4,5}, {1,3,4,5}, {0,1,6}, {2,6}, {3,6}, {1,2,3,4,6}, {1,5,6}, {0,2,5,6}, {3,5,6}, {0,4,5,6}, {0,2,4,5,6}, {1,3,4,5,6}, {1,7}, {0,2,7}, {1,3,7}, {2,3,4,7}, {5,7}, {0,1,2,5,7}, {1,3,5,7}, {4,5,7}, {2,4,5,7}, {3,4,5,7}, {6,7}, {0,2,6,7}, {3,6,7}, {2,3,4,6,7}, {1,5,6,7}, {0,1,2,5,6,7}, {3,5,6,7}, {4,5,6,7}, {2,4,5,6,7}, {3,4,5,6,7}]
  ```

- rank 7 (`N = 9`), a3 = 47; length40_m7_003, origin 70; rep_length40_m7_003.json

  ```text
  [{1,4}, {2,4}, {0,2,3,4}, {0,1,5}, {2,4,5}, {3,4,5}, {0,2,3,4,5}, {6}, {1,3,6}, {1,5,6}, {1,3,5,6}, {1,4,5,6}, {3,4,5,6}, {0,1,3,7}, {0,2,4,7}, {1,3,4,7}, {2,3,4,7}, {0,1,3,5,7}, {1,4,5,7}, {0,2,4,5,7}, {2,3,4,5,7}, {1,4,6,7}, {1,3,4,6,7}, {1,4,8}, {2,4,8}, {2,5,8}, {1,3,5,8}, {2,6,8}, {1,4,6,8}, {1,3,5,6,8}, {2,4,5,6,8}, {4,7,8}, {2,4,7,8}, {2,5,7,8}, {3,5,7,8}, {2,6,7,8}, {4,6,7,8}, {3,5,6,7,8}, {2,4,5,6,7,8}]
  ```

- rank 9 (`N = 11`), a3 = 45; length40_m9_discovery_015, origin 496; rep_length40_m9_discovery_015.json

  ```text
  [{1,2}, {0,1,3}, {0,1,4}, {0,1,3,4}, {0,1,2,5}, {0,1,3,5}, {0,1,4,5}, {0,1,3,4,5}, {0,1,4,6}, {0,1,2,4,6}, {1,4,5,6}, {1,2,4,5,6}, {2,7}, {0,5,7}, {0,2,5,7}, {0,4,6,7}, {0,2,4,6,7}, {4,5,6,7}, {2,4,5,6,7}, {3,8}, {4,8}, {3,4,8}, {5,8}, {3,5,8}, {4,5,8}, {3,4,5,8}, {7,8}, {9}, {7,9}, {8,9}, {7,8,9}, {6,10}, {6,7,10}, {6,8,10}, {6,7,8,10}, {6,9,10}, {6,7,9,10}, {6,8,9,10}, {6,7,8,9,10}]
  ```

### 3. `[[39,2,3]]` — T0·T1

- gate `0+1`, `N = 10` (2 outputs + 8 checks), T-count 2, reduced degree 1, a3 = 35
- source: length40_m8_discovery_028, origin 208; rep_length40_m8_discovery_028.json

```text
[{0,2}, {3}, {0,4}, {0,2,4}, {1,5}, {1,3,5}, {1,6}, {4,6}, {3,4,6}, {1,4,5,6}, {1,3,4,5,6}, {1,2,7}, {1,3,7}, {1,2,4,7}, {3,5,7}, {4,5,7}, {1,3,4,6,7}, {5,6,7}, {3,4,5,6,7}, {1,8}, {0,1,5,8}, {0,1,2,5,8}, {0,1,4,5,8}, {0,1,2,4,5,8}, {1,6,8}, {1,4,7,8}, {2,5,7,8}, {2,4,5,7,8}, {1,4,6,7,8}, {5,6,7,8}, {4,5,6,7,8}, {9}, {6,9}, {7,9}, {6,7,9}, {8,9}, {6,8,9}, {7,8,9}, {6,7,8,9}]
```

Best witness at each other check rank:

- rank 6 (`N = 8`), a3 = 101; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{2}, {1,3}, {1,2,3,4}, {5}, {0,1,2,5}, {1,3,5}, {0,1,4,5}, {0,1,2,4,5}, {1,3,4,5}, {0,6}, {2,6}, {3,6}, {1,2,3,4,6}, {1,5,6}, {0,1,2,5,6}, {3,5,6}, {0,1,4,5,6}, {0,1,2,4,5,6}, {1,3,4,5,6}, {1,7}, {0,1,2,7}, {1,3,7}, {2,3,4,7}, {5,7}, {0,2,5,7}, {1,3,5,7}, {4,5,7}, {2,4,5,7}, {3,4,5,7}, {6,7}, {0,1,2,6,7}, {3,6,7}, {2,3,4,6,7}, {1,5,6,7}, {0,2,5,6,7}, {3,5,6,7}, {4,5,6,7}, {2,4,5,6,7}, {3,4,5,6,7}]
  ```

- rank 7 (`N = 9`), a3 = 47; length40_m7_003, origin 70; rep_length40_m7_003.json

  ```text
  [{1,4}, {2,4}, {0,1,2,3,4}, {0,5}, {2,4,5}, {3,4,5}, {0,1,2,3,4,5}, {6}, {1,3,6}, {1,5,6}, {1,3,5,6}, {1,4,5,6}, {3,4,5,6}, {0,3,7}, {0,1,2,4,7}, {1,3,4,7}, {2,3,4,7}, {0,3,5,7}, {1,4,5,7}, {0,1,2,4,5,7}, {2,3,4,5,7}, {1,4,6,7}, {1,3,4,6,7}, {1,4,8}, {2,4,8}, {2,5,8}, {1,3,5,8}, {2,6,8}, {1,4,6,8}, {1,3,5,6,8}, {2,4,5,6,8}, {4,7,8}, {2,4,7,8}, {2,5,7,8}, {3,5,7,8}, {2,6,7,8}, {4,6,7,8}, {3,5,6,7,8}, {2,4,5,6,7,8}]
  ```

- rank 9 (`N = 11`), a3 = 45; length40_m9_discovery_015, origin 496; rep_length40_m9_discovery_015.json

  ```text
  [{1,2}, {0,3}, {0,4}, {0,3,4}, {0,2,5}, {0,3,5}, {0,4,5}, {0,3,4,5}, {0,4,6}, {0,2,4,6}, {1,4,5,6}, {1,2,4,5,6}, {2,7}, {0,1,5,7}, {0,1,2,5,7}, {0,1,4,6,7}, {0,1,2,4,6,7}, {4,5,6,7}, {2,4,5,6,7}, {3,8}, {4,8}, {3,4,8}, {5,8}, {3,5,8}, {4,5,8}, {3,4,5,8}, {7,8}, {9}, {7,9}, {8,9}, {7,8,9}, {6,10}, {6,7,10}, {6,8,10}, {6,7,8,10}, {6,9,10}, {6,7,9,10}, {6,8,9,10}, {6,7,8,9,10}]
  ```

### 4. `[[39,2,3]]` — T0·T1·CS01

- gate `0+1+01`, `N = 9` (2 outputs + 7 checks), T-count 1, reduced degree 1, a3 = 23
- source: length40_m7_004, origin 82; rep_length40_m7_004.json

```text
[{1,4}, {0,1,3,4}, {5}, {1,4,5}, {3,4,5}, {0,1,2,6}, {1,4,6}, {0,1,2,3,4,6}, {0,1,2,5,6}, {1,4,5,6}, {0,1,2,3,4,5,6}, {1,3,7}, {1,3,5,7}, {6,7}, {2,6,7}, {1,3,6,7}, {3,4,6,7}, {2,3,4,6,7}, {0,1,5,6,7}, {2,5,6,7}, {1,3,5,6,7}, {0,1,3,4,5,6,7}, {2,3,4,5,6,7}, {8}, {2,3,8}, {3,4,8}, {2,4,5,8}, {0,1,6,8}, {2,3,6,8}, {0,1,3,4,6,8}, {2,4,5,6,8}, {0,1,7,8}, {2,3,7,8}, {0,1,3,4,7,8}, {2,4,5,7,8}, {6,7,8}, {2,3,6,7,8}, {3,4,6,7,8}, {2,4,5,6,7,8}]
```

Best witness at each other check rank:

- rank 6 (`N = 8`), a3 = 75; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2}, {0,1,3}, {2,3,4}, {1,5}, {0,2,5}, {3,5}, {0,1,4,5}, {2,4,5}, {0,1,3,4,5}, {6}, {2,6}, {0,1,3,6}, {2,3,4,6}, {0,5,6}, {1,2,5,6}, {3,5,6}, {0,1,4,5,6}, {2,4,5,6}, {0,1,3,4,5,6}, {7}, {0,1,2,7}, {3,7}, {2,3,4,7}, {1,5,7}, {0,2,5,7}, {3,5,7}, {4,5,7}, {2,4,5,7}, {3,4,5,7}, {0,1,6,7}, {2,6,7}, {3,6,7}, {2,3,4,6,7}, {0,5,6,7}, {1,2,5,6,7}, {3,5,6,7}, {4,5,6,7}, {2,4,5,6,7}, {3,4,5,6,7}]
  ```

- rank 8 (`N = 10`), a3 = 23; length40_m8_discovery_004, origin 202; rep_length40_m8_discovery_004.json

  ```text
  [{0,2,3}, {4}, {0,2,3,4}, {0,1,3,5}, {0,1,6}, {0,3,6}, {4,6}, {0,3,4,6}, {0,1,3,5,6}, {0,1,3,7}, {0,1,2,3,7}, {0,1,3,4,7}, {0,1,2,3,4,7}, {3,5,7}, {3,5,6,7}, {8}, {1,2,3,8}, {0,1,4,8}, {1,2,3,4,8}, {0,1,3,5,8}, {6,8}, {1,3,6,8}, {0,1,4,6,8}, {1,3,4,6,8}, {0,1,3,5,6,8}, {3,7,8}, {2,3,7,8}, {3,4,7,8}, {2,3,4,7,8}, {3,5,7,8}, {3,5,6,7,8}, {3,5,9}, {3,5,6,9}, {3,5,7,9}, {3,5,6,7,9}, {3,5,8,9}, {3,5,6,8,9}, {3,5,7,8,9}, {3,5,6,7,8,9}]
  ```

- rank 9 (`N = 11`), a3 = 23; length40_m9_discovery_012, origin 271; rep_length40_m9_discovery_012.json

  ```text
  [{0,1,3}, {0,1,4}, {0,1,3,4}, {2,3,5}, {1,6}, {1,3,6}, {1,4,6}, {1,3,4,6}, {5,6}, {3,5,6}, {4,5,6}, {3,4,5,6}, {5,7}, {2,4,5,7}, {3,4,5,7}, {3,5,8}, {4,5,8}, {2,4,5,8}, {2,3,5,7,8}, {0,5,9}, {0,3,5,9}, {2,3,5,9}, {0,4,5,9}, {0,3,4,5,9}, {5,7,9}, {2,4,5,7,9}, {3,4,5,7,9}, {3,5,8,9}, {4,5,8,9}, {2,4,5,8,9}, {2,3,5,7,8,9}, {2,3,4,5,10}, {2,3,4,5,7,10}, {2,3,4,5,8,10}, {2,3,4,5,7,8,10}, {2,3,4,5,9,10}, {2,3,4,5,7,9,10}, {2,3,4,5,8,9,10}, {2,3,4,5,7,8,9,10}]
  ```

- rank 10 (`N = 12`), a3 = 31; length40_m10_class_0009, origin 896; rep_length40_m10_class_0009.json

  ```text
  [{0,1,3,8}, {4,8}, {3,4,8}, {0,1,9}, {0,1,3,8,9}, {4,8,9}, {3,4,8,9}, {0,2,3,4,8,9}, {0,2,3,4,5,8,9}, {0,2,3,4,6,8,9}, {0,2,3,4,5,6,8,9}, {0,2,3,4,7,8,9}, {0,2,3,4,5,7,8,9}, {0,2,3,4,6,7,8,9}, {0,2,3,4,5,6,7,8,9}, {0,1,3,10}, {4,10}, {3,4,10}, {0,1,8,10}, {2,3,4,8,10}, {2,3,4,5,8,10}, {2,3,4,6,8,10}, {2,3,4,5,6,8,10}, {2,3,4,7,8,10}, {2,3,4,5,7,8,10}, {2,3,4,6,7,8,10}, {2,3,4,5,6,7,8,10}, {0,1,3,9,10}, {4,9,10}, {3,4,9,10}, {0,1,8,9,10}, {11}, {8,11}, {9,11}, {8,9,11}, {10,11}, {8,10,11}, {9,10,11}, {8,9,10,11}]
  ```

### 5. `[[39,2,3]]` — CS01

- gate `01`, `N = 10` (2 outputs + 8 checks), T-count 3, reduced degree 2, a3 = 48
- source: length40_m8_discovery_028, origin 208; rep_length40_m8_discovery_028.json

```text
[{1,2}, {0,3}, {1,4}, {1,2,4}, {1,5}, {1,3,5}, {0,1,6}, {0,4,6}, {0,3,4,6}, {1,4,5,6}, {1,3,4,5,6}, {0,1,2,7}, {0,1,3,7}, {0,1,2,4,7}, {3,5,7}, {4,5,7}, {0,1,3,4,6,7}, {5,6,7}, {3,4,5,6,7}, {0,1,8}, {0,5,8}, {0,2,5,8}, {0,4,5,8}, {0,2,4,5,8}, {0,1,6,8}, {0,1,4,7,8}, {2,5,7,8}, {2,4,5,7,8}, {0,1,4,6,7,8}, {5,6,7,8}, {4,5,6,7,8}, {9}, {6,9}, {7,9}, {6,7,9}, {8,9}, {6,8,9}, {7,8,9}, {6,7,8,9}]
```

Best witness at each other check rank:

- rank 6 (`N = 8`), a3 = 90; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,2}, {3}, {2,3,4}, {1,5}, {0,1,2,5}, {3,5}, {0,1,4,5}, {2,4,5}, {0,1,3,4,5}, {0,6}, {1,2,6}, {3,6}, {1,2,3,4,6}, {0,5,6}, {2,5,6}, {1,3,5,6}, {0,1,4,5,6}, {1,2,4,5,6}, {0,1,3,4,5,6}, {7}, {2,7}, {0,1,3,7}, {1,2,3,4,7}, {0,1,5,7}, {1,2,5,7}, {1,3,5,7}, {4,5,7}, {1,2,4,5,7}, {3,4,5,7}, {0,6,7}, {0,1,2,6,7}, {0,1,3,6,7}, {2,3,4,6,7}, {5,6,7}, {0,2,5,6,7}, {3,5,6,7}, {4,5,6,7}, {2,4,5,6,7}, {3,4,5,6,7}]
  ```

- rank 7 (`N = 9`), a3 = 60; length40_m7_003, origin 70; rep_length40_m7_003.json

  ```text
  [{0,1,4}, {2,4}, {0,2,3,4}, {1,5}, {2,4,5}, {0,3,4,5}, {0,2,3,4,5}, {0,6}, {0,1,3,6}, {0,1,5,6}, {0,1,3,5,6}, {0,1,4,5,6}, {0,3,4,5,6}, {1,3,7}, {0,2,4,7}, {0,1,3,4,7}, {2,3,4,7}, {1,3,5,7}, {0,1,4,5,7}, {0,2,4,5,7}, {2,3,4,5,7}, {0,1,4,6,7}, {0,1,3,4,6,7}, {1,4,8}, {2,4,8}, {2,5,8}, {1,3,5,8}, {2,6,8}, {1,4,6,8}, {1,3,5,6,8}, {2,4,5,6,8}, {4,7,8}, {2,4,7,8}, {2,5,7,8}, {3,5,7,8}, {2,6,7,8}, {4,6,7,8}, {3,5,6,7,8}, {2,4,5,6,7,8}]
  ```

- rank 9 (`N = 11`), a3 = 66; length40_m9_discovery_015, origin 496; rep_length40_m9_discovery_015.json

  ```text
  [{0,1,2}, {1,3}, {1,4}, {1,3,4}, {0,1,2,5}, {0,1,3,5}, {0,1,4,5}, {0,1,3,4,5}, {1,4,6}, {1,2,4,6}, {1,4,5,6}, {1,2,4,5,6}, {0,2,7}, {0,5,7}, {0,2,5,7}, {4,6,7}, {2,4,6,7}, {4,5,6,7}, {2,4,5,6,7}, {0,3,8}, {0,4,8}, {0,3,4,8}, {5,8}, {3,5,8}, {4,5,8}, {3,4,5,8}, {0,7,8}, {0,9}, {0,7,9}, {0,8,9}, {0,7,8,9}, {6,10}, {6,7,10}, {6,8,10}, {6,7,8,10}, {6,9,10}, {6,7,9,10}, {6,8,9,10}, {6,7,8,9,10}]
  ```

### 6. `[[39,3,3]]` — T0·CS01·CS02·CCZ012

- gate `0+01+02+012`, `N = 10` (3 outputs + 7 checks), T-count 2, reduced degree 1, a3 = 51
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{1,2,5}, {1,3,5}, {0,1,3,4,5}, {0,1,2,6}, {1,3,5,6}, {4,5,6}, {0,1,3,4,5,6}, {7}, {1,2,4,7}, {1,2,6,7}, {1,2,4,6,7}, {1,2,5,6,7}, {4,5,6,7}, {0,1,2,4,8}, {0,1,3,5,8}, {1,2,4,5,8}, {1,3,4,5,8}, {0,1,2,4,6,8}, {1,2,5,6,8}, {0,1,3,5,6,8}, {1,3,4,5,6,8}, {1,2,5,7,8}, {1,2,4,5,7,8}, {1,2,5,9}, {3,5,9}, {3,6,9}, {1,2,4,6,9}, {3,7,9}, {1,2,5,7,9}, {1,2,4,6,7,9}, {3,5,6,7,9}, {5,8,9}, {3,5,8,9}, {3,6,8,9}, {4,6,8,9}, {3,7,8,9}, {5,7,8,9}, {4,6,7,8,9}, {3,5,6,7,8,9}]
```

Best witness at each other check rank:

- rank 6 (`N = 9`), a3 = 109; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{3}, {2,4}, {2,3,4,5}, {6}, {0,3,6}, {2,4,6}, {1,5,6}, {1,3,5,6}, {2,4,5,6}, {1,2,7}, {3,7}, {0,1,4,7}, {2,3,4,5,7}, {0,1,2,6,7}, {0,3,6,7}, {0,1,4,6,7}, {1,5,6,7}, {1,3,5,6,7}, {2,4,5,6,7}, {2,8}, {1,3,8}, {0,1,2,4,8}, {3,4,5,8}, {0,1,6,8}, {0,2,3,6,8}, {0,1,2,4,6,8}, {5,6,8}, {3,5,6,8}, {4,5,6,8}, {0,1,7,8}, {1,3,7,8}, {4,7,8}, {3,4,5,7,8}, {2,6,7,8}, {0,2,3,6,7,8}, {4,6,7,8}, {5,6,7,8}, {3,5,6,7,8}, {4,5,6,7,8}]
  ```

- rank 8 (`N = 11`), a3 = 53; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{2,3}, {0,1,2,4}, {0,1,2,5}, {0,1,2,4,5}, {0,2,3,6}, {0,1,2,4,6}, {0,1,2,5,6}, {0,1,2,4,5,6}, {7}, {0,2,5,7}, {0,1,2,3,5,7}, {2,5,6,7}, {1,2,3,5,6,7}, {1,3,8}, {0,6,8}, {0,1,3,6,8}, {7,8}, {0,1,5,7,8}, {0,3,5,7,8}, {1,5,6,7,8}, {3,5,6,7,8}, {4,9}, {5,9}, {4,5,9}, {6,9}, {4,6,9}, {5,6,9}, {4,5,6,9}, {7,9}, {8,9}, {7,8,9}, {10}, {7,10}, {8,10}, {7,8,10}, {9,10}, {7,9,10}, {8,9,10}, {7,8,9,10}]
  ```

### 7. `[[39,3,3]]` — T0·CS01·CS02·CS12·CCZ012

- gate `0+01+02+12+012`, `N = 11` (3 outputs + 8 checks), T-count 3, reduced degree 1, a3 = 51
- source: length40_m8_discovery_028, origin 208; rep_length40_m8_discovery_028.json

```text
[{2,3}, {1,4}, {2,5}, {2,3,5}, {0,2,6}, {0,2,4,6}, {0,1,2,7}, {1,5,7}, {1,4,5,7}, {0,2,5,6,7}, {0,2,4,5,6,7}, {0,1,2,3,8}, {0,1,2,4,8}, {0,1,2,3,5,8}, {4,6,8}, {5,6,8}, {0,1,2,4,5,7,8}, {6,7,8}, {4,5,6,7,8}, {0,1,2,9}, {0,1,6,9}, {0,1,3,6,9}, {0,1,5,6,9}, {0,1,3,5,6,9}, {0,1,2,7,9}, {0,1,2,5,8,9}, {3,6,8,9}, {3,5,6,8,9}, {0,1,2,5,7,8,9}, {6,7,8,9}, {5,6,7,8,9}, {10}, {7,10}, {8,10}, {7,8,10}, {9,10}, {7,9,10}, {8,9,10}, {7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 9`), a3 = 133; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,3}, {1,4}, {2,3,4,5}, {2,6}, {1,3,6}, {1,4,6}, {5,6}, {3,5,6}, {2,4,5,6}, {1,7}, {1,2,3,7}, {4,7}, {2,3,4,5,7}, {1,2,6,7}, {1,3,6,7}, {4,6,7}, {0,5,6,7}, {0,3,5,6,7}, {2,4,5,6,7}, {2,8}, {1,2,3,8}, {1,4,8}, {3,4,5,8}, {2,6,8}, {1,2,3,6,8}, {1,4,6,8}, {0,5,6,8}, {0,3,5,6,8}, {4,5,6,8}, {0,1,2,7,8}, {0,1,2,3,7,8}, {4,7,8}, {3,4,5,7,8}, {1,2,6,7,8}, {1,2,3,6,7,8}, {4,6,7,8}, {5,6,7,8}, {3,5,6,7,8}, {4,5,6,7,8}]
  ```

- rank 7 (`N = 10`), a3 = 63; length40_m7_003, origin 70; rep_length40_m7_003.json

  ```text
  [{0,1,2,5}, {3,5}, {0,1,3,4,5}, {2,6}, {3,5,6}, {1,4,5,6}, {0,1,3,4,5,6}, {1,7}, {0,1,2,4,7}, {0,1,2,6,7}, {0,1,2,4,6,7}, {0,1,2,5,6,7}, {1,4,5,6,7}, {2,4,8}, {0,1,3,5,8}, {0,1,2,4,5,8}, {3,4,5,8}, {2,4,6,8}, {0,1,2,5,6,8}, {0,1,3,5,6,8}, {3,4,5,6,8}, {0,1,2,5,7,8}, {0,1,2,4,5,7,8}, {0,2,5,9}, {3,5,9}, {3,6,9}, {0,2,4,6,9}, {3,7,9}, {0,2,5,7,9}, {0,2,4,6,7,9}, {3,5,6,7,9}, {5,8,9}, {3,5,8,9}, {3,6,8,9}, {4,6,8,9}, {3,7,8,9}, {5,7,8,9}, {4,6,7,8,9}, {3,5,6,7,8,9}]
  ```

- rank 9 (`N = 12`), a3 = 67; length40_m9_discovery_015, origin 496; rep_length40_m9_discovery_015.json

  ```text
  [{0,1,2,3}, {2,4}, {2,5}, {2,4,5}, {1,2,3,6}, {1,2,4,6}, {1,2,5,6}, {1,2,4,5,6}, {2,5,7}, {2,3,5,7}, {0,2,5,6,7}, {0,2,3,5,6,7}, {1,3,8}, {0,1,6,8}, {0,1,3,6,8}, {0,5,7,8}, {0,3,5,7,8}, {5,6,7,8}, {3,5,6,7,8}, {1,4,9}, {1,5,9}, {1,4,5,9}, {6,9}, {4,6,9}, {5,6,9}, {4,5,6,9}, {1,8,9}, {1,10}, {1,8,10}, {1,9,10}, {1,8,9,10}, {7,11}, {7,8,11}, {7,9,11}, {7,8,9,11}, {7,10,11}, {7,8,10,11}, {7,9,10,11}, {7,8,9,10,11}]
  ```

### 8. `[[39,3,3]]` — T0·CS01·CS12

- gate `0+01+12`, `N = 11` (3 outputs + 8 checks), T-count 3, reduced degree 1, a3 = 51
- source: length40_m8_discovery_028, origin 208; rep_length40_m8_discovery_028.json

```text
[{1,2,3}, {0,1,4}, {1,2,5}, {1,2,3,5}, {0,1,2,6}, {0,1,2,4,6}, {2,7}, {0,1,5,7}, {0,1,4,5,7}, {0,1,2,5,6,7}, {0,1,2,4,5,6,7}, {2,3,8}, {2,4,8}, {2,3,5,8}, {4,6,8}, {5,6,8}, {2,4,5,7,8}, {6,7,8}, {4,5,6,7,8}, {2,9}, {1,6,9}, {1,3,6,9}, {1,5,6,9}, {1,3,5,6,9}, {2,7,9}, {2,5,8,9}, {3,6,8,9}, {3,5,6,8,9}, {2,5,7,8,9}, {6,7,8,9}, {5,6,7,8,9}, {10}, {7,10}, {8,10}, {7,8,10}, {9,10}, {7,9,10}, {8,9,10}, {7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 9`), a3 = 133; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{2,3}, {1,2,4}, {0,1,3,4,5}, {0,1,6}, {1,2,3,6}, {1,2,4,6}, {5,6}, {3,5,6}, {0,1,4,5,6}, {1,2,7}, {0,2,3,7}, {4,7}, {0,1,3,4,5,7}, {0,2,6,7}, {1,2,3,6,7}, {4,6,7}, {0,5,6,7}, {0,3,5,6,7}, {0,1,4,5,6,7}, {0,1,8}, {0,2,3,8}, {1,2,4,8}, {3,4,5,8}, {0,1,6,8}, {0,2,3,6,8}, {1,2,4,6,8}, {0,5,6,8}, {0,3,5,6,8}, {4,5,6,8}, {2,7,8}, {2,3,7,8}, {4,7,8}, {3,4,5,7,8}, {0,2,6,7,8}, {0,2,3,6,7,8}, {4,6,7,8}, {5,6,7,8}, {3,5,6,7,8}, {4,5,6,7,8}]
  ```

- rank 7 (`N = 10`), a3 = 63; length40_m7_003, origin 70; rep_length40_m7_003.json

  ```text
  [{2,5}, {3,5}, {1,3,4,5}, {1,2,6}, {3,5,6}, {0,1,4,5,6}, {1,3,4,5,6}, {0,1,7}, {2,4,7}, {2,6,7}, {2,4,6,7}, {2,5,6,7}, {0,1,4,5,6,7}, {1,2,4,8}, {1,3,5,8}, {2,4,5,8}, {3,4,5,8}, {1,2,4,6,8}, {2,5,6,8}, {1,3,5,6,8}, {3,4,5,6,8}, {2,5,7,8}, {2,4,5,7,8}, {0,1,2,5,9}, {3,5,9}, {3,6,9}, {0,1,2,4,6,9}, {3,7,9}, {0,1,2,5,7,9}, {0,1,2,4,6,7,9}, {3,5,6,7,9}, {5,8,9}, {3,5,8,9}, {3,6,8,9}, {4,6,8,9}, {3,7,8,9}, {5,7,8,9}, {4,6,7,8,9}, {3,5,6,7,8,9}]
  ```

- rank 9 (`N = 12`), a3 = 67; length40_m9_discovery_015, origin 496; rep_length40_m9_discovery_015.json

  ```text
  [{2,3}, {0,1,4}, {0,1,5}, {0,1,4,5}, {0,2,3,6}, {0,2,4,6}, {0,2,5,6}, {0,2,4,5,6}, {0,1,5,7}, {0,1,3,5,7}, {1,5,6,7}, {1,3,5,6,7}, {1,2,3,8}, {0,1,2,6,8}, {0,1,2,3,6,8}, {0,5,7,8}, {0,3,5,7,8}, {5,6,7,8}, {3,5,6,7,8}, {1,2,4,9}, {1,2,5,9}, {1,2,4,5,9}, {6,9}, {4,6,9}, {5,6,9}, {4,5,6,9}, {1,2,8,9}, {1,2,10}, {1,2,8,10}, {1,2,9,10}, {1,2,8,9,10}, {7,11}, {7,8,11}, {7,9,11}, {7,8,9,11}, {7,10,11}, {7,8,10,11}, {7,9,10,11}, {7,8,9,10,11}]
  ```

### 9. `[[39,3,3]]` — T0·T1·CS01·CS02·CCZ012

- gate `0+1+01+02+012`, `N = 11` (3 outputs + 8 checks), T-count 3, reduced degree 1, a3 = 51
- source: length40_m8_discovery_028, origin 208; rep_length40_m8_discovery_028.json

```text
[{0,1,2,3}, {1,4}, {0,1,2,5}, {0,1,2,3,5}, {2,6}, {2,4,6}, {1,2,7}, {1,5,7}, {1,4,5,7}, {2,5,6,7}, {2,4,5,6,7}, {1,2,3,8}, {1,2,4,8}, {1,2,3,5,8}, {4,6,8}, {5,6,8}, {1,2,4,5,7,8}, {6,7,8}, {4,5,6,7,8}, {1,2,9}, {0,6,9}, {0,3,6,9}, {0,5,6,9}, {0,3,5,6,9}, {1,2,7,9}, {1,2,5,8,9}, {3,6,8,9}, {3,5,6,8,9}, {1,2,5,7,8,9}, {6,7,8,9}, {5,6,7,8,9}, {10}, {7,10}, {8,10}, {7,8,10}, {9,10}, {7,9,10}, {8,9,10}, {7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 9`), a3 = 133; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,3}, {1,2,4}, {1,3,4,5}, {1,6}, {1,2,3,6}, {1,2,4,6}, {5,6}, {3,5,6}, {1,4,5,6}, {1,2,7}, {2,3,7}, {4,7}, {1,3,4,5,7}, {2,6,7}, {1,2,3,6,7}, {4,6,7}, {0,1,5,6,7}, {0,1,3,5,6,7}, {1,4,5,6,7}, {1,8}, {2,3,8}, {1,2,4,8}, {3,4,5,8}, {1,6,8}, {2,3,6,8}, {1,2,4,6,8}, {0,1,5,6,8}, {0,1,3,5,6,8}, {4,5,6,8}, {0,1,2,7,8}, {0,1,2,3,7,8}, {4,7,8}, {3,4,5,7,8}, {2,6,7,8}, {2,3,6,7,8}, {4,6,7,8}, {5,6,7,8}, {3,5,6,7,8}, {4,5,6,7,8}]
  ```

- rank 7 (`N = 10`), a3 = 63; length40_m7_003, origin 70; rep_length40_m7_003.json

  ```text
  [{1,2,5}, {3,5}, {0,3,4,5}, {0,1,2,6}, {3,5,6}, {1,4,5,6}, {0,3,4,5,6}, {1,7}, {1,2,4,7}, {1,2,6,7}, {1,2,4,6,7}, {1,2,5,6,7}, {1,4,5,6,7}, {0,1,2,4,8}, {0,3,5,8}, {1,2,4,5,8}, {3,4,5,8}, {0,1,2,4,6,8}, {1,2,5,6,8}, {0,3,5,6,8}, {3,4,5,6,8}, {1,2,5,7,8}, {1,2,4,5,7,8}, {2,5,9}, {3,5,9}, {3,6,9}, {2,4,6,9}, {3,7,9}, {2,5,7,9}, {2,4,6,7,9}, {3,5,6,7,9}, {5,8,9}, {3,5,8,9}, {3,6,8,9}, {4,6,8,9}, {3,7,8,9}, {5,7,8,9}, {4,6,7,8,9}, {3,5,6,7,8,9}]
  ```

- rank 9 (`N = 12`), a3 = 67; length40_m9_discovery_015, origin 496; rep_length40_m9_discovery_015.json

  ```text
  [{1,2,3}, {1,4}, {1,5}, {1,4,5}, {0,2,3,6}, {0,2,4,6}, {0,2,5,6}, {0,2,4,5,6}, {1,5,7}, {1,3,5,7}, {0,5,6,7}, {0,3,5,6,7}, {0,1,2,3,8}, {2,6,8}, {2,3,6,8}, {0,1,5,7,8}, {0,1,3,5,7,8}, {5,6,7,8}, {3,5,6,7,8}, {0,1,2,4,9}, {0,1,2,5,9}, {0,1,2,4,5,9}, {6,9}, {4,6,9}, {5,6,9}, {4,5,6,9}, {0,1,2,8,9}, {0,1,2,10}, {0,1,2,8,10}, {0,1,2,9,10}, {0,1,2,8,9,10}, {7,11}, {7,8,11}, {7,9,11}, {7,8,9,11}, {7,10,11}, {7,8,10,11}, {7,9,10,11}, {7,8,9,10,11}]
  ```

### 10. `[[39,3,3]]` — T0·T1·CS01·CS02·CS12·CCZ012

- gate `0+1+01+02+12+012`, `N = 10` (3 outputs + 7 checks), T-count 2, reduced degree 1, a3 = 51
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{2,5}, {1,2,3,5}, {0,2,3,4,5}, {0,1,2,6}, {1,2,3,5,6}, {4,5,6}, {0,2,3,4,5,6}, {7}, {2,4,7}, {2,6,7}, {2,4,6,7}, {2,5,6,7}, {4,5,6,7}, {0,1,2,4,8}, {0,2,3,5,8}, {2,4,5,8}, {1,2,3,4,5,8}, {0,1,2,4,6,8}, {2,5,6,8}, {0,2,3,5,6,8}, {1,2,3,4,5,6,8}, {2,5,7,8}, {2,4,5,7,8}, {2,5,9}, {3,5,9}, {3,6,9}, {2,4,6,9}, {3,7,9}, {2,5,7,9}, {2,4,6,7,9}, {3,5,6,7,9}, {5,8,9}, {3,5,8,9}, {3,6,8,9}, {4,6,8,9}, {3,7,8,9}, {5,7,8,9}, {4,6,7,8,9}, {3,5,6,7,8,9}]
```

Best witness at each other check rank:

- rank 6 (`N = 9`), a3 = 109; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{3}, {1,4}, {1,3,4,5}, {6}, {0,1,3,6}, {1,4,6}, {1,2,5,6}, {1,2,3,5,6}, {1,4,5,6}, {2,7}, {3,7}, {0,2,4,7}, {1,3,4,5,7}, {0,1,2,6,7}, {0,1,3,6,7}, {0,2,4,6,7}, {1,2,5,6,7}, {1,2,3,5,6,7}, {1,4,5,6,7}, {1,8}, {1,2,3,8}, {0,1,2,4,8}, {3,4,5,8}, {0,2,6,8}, {0,3,6,8}, {0,1,2,4,6,8}, {5,6,8}, {3,5,6,8}, {4,5,6,8}, {0,2,7,8}, {1,2,3,7,8}, {4,7,8}, {3,4,5,7,8}, {1,6,7,8}, {0,3,6,7,8}, {4,6,7,8}, {5,6,7,8}, {3,5,6,7,8}, {4,5,6,7,8}]
  ```

- rank 8 (`N = 11`), a3 = 53; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{1,3}, {2,4}, {2,5}, {2,4,5}, {0,3,6}, {2,4,6}, {2,5,6}, {2,4,5,6}, {7}, {0,5,7}, {2,3,5,7}, {1,5,6,7}, {0,1,2,3,5,6,7}, {0,2,3,8}, {0,1,6,8}, {1,2,3,6,8}, {7,8}, {1,2,5,7,8}, {0,1,3,5,7,8}, {0,2,5,6,7,8}, {3,5,6,7,8}, {4,9}, {5,9}, {4,5,9}, {6,9}, {4,6,9}, {5,6,9}, {4,5,6,9}, {7,9}, {8,9}, {7,8,9}, {10}, {7,10}, {8,10}, {7,8,10}, {9,10}, {7,9,10}, {8,9,10}, {7,8,9,10}]
  ```

### 11. `[[39,3,3]]` — T0·T1·T2

- gate `0+1+2`, `N = 11` (3 outputs + 8 checks), T-count 3, reduced degree 1, a3 = 51
- source: length40_m8_discovery_028, origin 208; rep_length40_m8_discovery_028.json

```text
[{1,3}, {0,4}, {1,5}, {1,3,5}, {0,2,6}, {0,2,4,6}, {2,7}, {0,5,7}, {0,4,5,7}, {0,2,5,6,7}, {0,2,4,5,6,7}, {2,3,8}, {2,4,8}, {2,3,5,8}, {4,6,8}, {5,6,8}, {2,4,5,7,8}, {6,7,8}, {4,5,6,7,8}, {2,9}, {1,2,6,9}, {1,2,3,6,9}, {1,2,5,6,9}, {1,2,3,5,6,9}, {2,7,9}, {2,5,8,9}, {3,6,8,9}, {3,5,6,8,9}, {2,5,7,8,9}, {6,7,8,9}, {5,6,7,8,9}, {10}, {7,10}, {8,10}, {7,8,10}, {9,10}, {7,9,10}, {8,9,10}, {7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 9`), a3 = 133; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{2,3}, {0,4}, {1,3,4,5}, {1,6}, {0,3,6}, {0,4,6}, {5,6}, {3,5,6}, {1,4,5,6}, {0,7}, {0,1,3,7}, {4,7}, {1,3,4,5,7}, {0,1,6,7}, {0,3,6,7}, {4,6,7}, {0,1,2,5,6,7}, {0,1,2,3,5,6,7}, {1,4,5,6,7}, {1,8}, {0,1,3,8}, {0,4,8}, {3,4,5,8}, {1,6,8}, {0,1,3,6,8}, {0,4,6,8}, {0,1,2,5,6,8}, {0,1,2,3,5,6,8}, {4,5,6,8}, {2,7,8}, {2,3,7,8}, {4,7,8}, {3,4,5,7,8}, {0,1,6,7,8}, {0,1,3,6,7,8}, {4,6,7,8}, {5,6,7,8}, {3,5,6,7,8}, {4,5,6,7,8}]
  ```

- rank 7 (`N = 10`), a3 = 63; length40_m7_003, origin 70; rep_length40_m7_003.json

  ```text
  [{2,5}, {3,5}, {1,2,3,4,5}, {1,6}, {3,5,6}, {0,4,5,6}, {1,2,3,4,5,6}, {0,7}, {2,4,7}, {2,6,7}, {2,4,6,7}, {2,5,6,7}, {0,4,5,6,7}, {1,4,8}, {1,2,3,5,8}, {2,4,5,8}, {3,4,5,8}, {1,4,6,8}, {2,5,6,8}, {1,2,3,5,6,8}, {3,4,5,6,8}, {2,5,7,8}, {2,4,5,7,8}, {0,2,5,9}, {3,5,9}, {3,6,9}, {0,2,4,6,9}, {3,7,9}, {0,2,5,7,9}, {0,2,4,6,7,9}, {3,5,6,7,9}, {5,8,9}, {3,5,8,9}, {3,6,8,9}, {4,6,8,9}, {3,7,8,9}, {5,7,8,9}, {4,6,7,8,9}, {3,5,6,7,8,9}]
  ```

- rank 9 (`N = 12`), a3 = 67; length40_m9_discovery_015, origin 496; rep_length40_m9_discovery_015.json

  ```text
  [{2,3}, {1,4}, {1,5}, {1,4,5}, {0,1,3,6}, {0,1,4,6}, {0,1,5,6}, {0,1,4,5,6}, {1,5,7}, {1,3,5,7}, {0,2,5,6,7}, {0,2,3,5,6,7}, {0,3,8}, {1,2,6,8}, {1,2,3,6,8}, {0,1,2,5,7,8}, {0,1,2,3,5,7,8}, {5,6,7,8}, {3,5,6,7,8}, {0,4,9}, {0,5,9}, {0,4,5,9}, {6,9}, {4,6,9}, {5,6,9}, {4,5,6,9}, {0,8,9}, {0,10}, {0,8,10}, {0,9,10}, {0,8,9,10}, {7,11}, {7,8,11}, {7,9,11}, {7,8,9,11}, {7,10,11}, {7,8,10,11}, {7,9,10,11}, {7,8,9,10,11}]
  ```

### 12. `[[39,3,3]]` — T0·T1·T2·CS01

- gate `0+1+2+01`, `N = 10` (3 outputs + 7 checks), T-count 2, reduced degree 1, a3 = 51
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{2,5}, {1,2,3,5}, {0,3,4,5}, {0,1,6}, {1,2,3,5,6}, {4,5,6}, {0,3,4,5,6}, {7}, {2,4,7}, {2,6,7}, {2,4,6,7}, {2,5,6,7}, {4,5,6,7}, {0,1,4,8}, {0,3,5,8}, {2,4,5,8}, {1,2,3,4,5,8}, {0,1,4,6,8}, {2,5,6,8}, {0,3,5,6,8}, {1,2,3,4,5,6,8}, {2,5,7,8}, {2,4,5,7,8}, {2,5,9}, {3,5,9}, {3,6,9}, {2,4,6,9}, {3,7,9}, {2,5,7,9}, {2,4,6,7,9}, {3,5,6,7,9}, {5,8,9}, {3,5,8,9}, {3,6,8,9}, {4,6,8,9}, {3,7,8,9}, {5,7,8,9}, {4,6,7,8,9}, {3,5,6,7,8,9}]
```

Best witness at each other check rank:

- rank 6 (`N = 9`), a3 = 109; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{3}, {1,4}, {1,3,4,5}, {6}, {0,1,2,3,6}, {1,4,6}, {1,2,5,6}, {1,2,3,5,6}, {1,4,5,6}, {2,7}, {3,7}, {0,4,7}, {1,3,4,5,7}, {0,1,6,7}, {0,1,2,3,6,7}, {0,4,6,7}, {1,2,5,6,7}, {1,2,3,5,6,7}, {1,4,5,6,7}, {1,8}, {1,2,3,8}, {0,1,4,8}, {3,4,5,8}, {0,6,8}, {0,2,3,6,8}, {0,1,4,6,8}, {5,6,8}, {3,5,6,8}, {4,5,6,8}, {0,7,8}, {1,2,3,7,8}, {4,7,8}, {3,4,5,7,8}, {1,6,7,8}, {0,2,3,6,7,8}, {4,6,7,8}, {5,6,7,8}, {3,5,6,7,8}, {4,5,6,7,8}]
  ```

- rank 8 (`N = 11`), a3 = 53; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{1,2,3}, {2,4}, {2,5}, {2,4,5}, {0,3,6}, {2,4,6}, {2,5,6}, {2,4,5,6}, {7}, {0,5,7}, {2,3,5,7}, {1,2,5,6,7}, {0,1,3,5,6,7}, {0,2,3,8}, {0,1,2,6,8}, {1,3,6,8}, {7,8}, {1,5,7,8}, {0,1,2,3,5,7,8}, {0,2,5,6,7,8}, {3,5,6,7,8}, {4,9}, {5,9}, {4,5,9}, {6,9}, {4,6,9}, {5,6,9}, {4,5,6,9}, {7,9}, {8,9}, {7,8,9}, {10}, {7,10}, {8,10}, {7,8,10}, {9,10}, {7,9,10}, {8,9,10}, {7,8,9,10}]
  ```

### 13. `[[39,3,3]]` — T0·T1·T2·CS01·CS02

- gate `0+1+2+01+02`, `N = 11` (3 outputs + 8 checks), T-count 3, reduced degree 1, a3 = 51
- source: length40_m8_discovery_028, origin 208; rep_length40_m8_discovery_028.json

```text
[{0,1,3}, {0,4}, {0,1,5}, {0,1,3,5}, {2,6}, {2,4,6}, {0,2,7}, {0,5,7}, {0,4,5,7}, {2,5,6,7}, {2,4,5,6,7}, {0,2,3,8}, {0,2,4,8}, {0,2,3,5,8}, {4,6,8}, {5,6,8}, {0,2,4,5,7,8}, {6,7,8}, {4,5,6,7,8}, {0,2,9}, {1,2,6,9}, {1,2,3,6,9}, {1,2,5,6,9}, {1,2,3,5,6,9}, {0,2,7,9}, {0,2,5,8,9}, {3,6,8,9}, {3,5,6,8,9}, {0,2,5,7,8,9}, {6,7,8,9}, {5,6,7,8,9}, {10}, {7,10}, {8,10}, {7,8,10}, {9,10}, {7,9,10}, {8,9,10}, {7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 9`), a3 = 133; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,3}, {0,1,4}, {0,2,3,4,5}, {0,2,6}, {0,1,3,6}, {0,1,4,6}, {5,6}, {3,5,6}, {0,2,4,5,6}, {0,1,7}, {1,2,3,7}, {4,7}, {0,2,3,4,5,7}, {1,2,6,7}, {0,1,3,6,7}, {4,6,7}, {0,1,2,5,6,7}, {0,1,2,3,5,6,7}, {0,2,4,5,6,7}, {0,2,8}, {1,2,3,8}, {0,1,4,8}, {3,4,5,8}, {0,2,6,8}, {1,2,3,6,8}, {0,1,4,6,8}, {0,1,2,5,6,8}, {0,1,2,3,5,6,8}, {4,5,6,8}, {0,7,8}, {0,3,7,8}, {4,7,8}, {3,4,5,7,8}, {1,2,6,7,8}, {1,2,3,6,7,8}, {4,6,7,8}, {5,6,7,8}, {3,5,6,7,8}, {4,5,6,7,8}]
  ```

- rank 7 (`N = 10`), a3 = 63; length40_m7_003, origin 70; rep_length40_m7_003.json

  ```text
  [{0,2,5}, {3,5}, {1,2,3,4,5}, {0,1,6}, {3,5,6}, {0,4,5,6}, {1,2,3,4,5,6}, {0,7}, {0,2,4,7}, {0,2,6,7}, {0,2,4,6,7}, {0,2,5,6,7}, {0,4,5,6,7}, {0,1,4,8}, {1,2,3,5,8}, {0,2,4,5,8}, {3,4,5,8}, {0,1,4,6,8}, {0,2,5,6,8}, {1,2,3,5,6,8}, {3,4,5,6,8}, {0,2,5,7,8}, {0,2,4,5,7,8}, {2,5,9}, {3,5,9}, {3,6,9}, {2,4,6,9}, {3,7,9}, {2,5,7,9}, {2,4,6,7,9}, {3,5,6,7,9}, {5,8,9}, {3,5,8,9}, {3,6,8,9}, {4,6,8,9}, {3,7,8,9}, {5,7,8,9}, {4,6,7,8,9}, {3,5,6,7,8,9}]
  ```

- rank 9 (`N = 12`), a3 = 67; length40_m9_discovery_015, origin 496; rep_length40_m9_discovery_015.json

  ```text
  [{0,3}, {0,2,4}, {0,2,5}, {0,2,4,5}, {1,2,3,6}, {1,2,4,6}, {1,2,5,6}, {1,2,4,5,6}, {0,2,5,7}, {0,2,3,5,7}, {1,5,6,7}, {1,3,5,6,7}, {0,1,3,8}, {2,6,8}, {2,3,6,8}, {0,1,2,5,7,8}, {0,1,2,3,5,7,8}, {5,6,7,8}, {3,5,6,7,8}, {0,1,4,9}, {0,1,5,9}, {0,1,4,5,9}, {6,9}, {4,6,9}, {5,6,9}, {4,5,6,9}, {0,1,8,9}, {0,1,10}, {0,1,8,10}, {0,1,9,10}, {0,1,8,9,10}, {7,11}, {7,8,11}, {7,9,11}, {7,8,9,11}, {7,10,11}, {7,8,10,11}, {7,9,10,11}, {7,8,9,10,11}]
  ```

### 14. `[[39,3,3]]` — T0·T1·T2·CS01·CS02·CS12·CCZ012

- gate `0+1+2+01+02+12+012`, `N = 10` (3 outputs + 7 checks), T-count 1, reduced degree 1, a3 = 23
- source: length40_m7_012, origin 5; rep_length40_m7_012.json

```text
[{0,1,2,4}, {0,1,3,4}, {5}, {4,5}, {2,3,4,5}, {0,2,3,6}, {1,3,5,6}, {1,2,3,7}, {0,3,5,7}, {3,6,7}, {0,1,2,3,5,6,7}, {0,1,2,9}, {0,1,2,4,9}, {2,3,4,9}, {5,9}, {4,5,9}, {0,1,3,4,5,9}, {1,3,6,9}, {0,2,3,5,6,9}, {0,3,7,9}, {1,2,3,5,7,9}, {0,1,2,3,6,7,9}, {3,5,6,7,9}, {0,1,2,3,8,9}, {0,1,2,3,4,8,9}, {0,1,2,3,5,8,9}, {0,1,2,3,4,5,8,9}, {3,6,8,9}, {3,4,6,8,9}, {3,5,6,8,9}, {3,4,5,6,8,9}, {3,7,8,9}, {3,4,7,8,9}, {3,5,7,8,9}, {3,4,5,7,8,9}, {3,6,7,8,9}, {3,4,6,7,8,9}, {3,5,6,7,8,9}, {3,4,5,6,7,8,9}]
```

Best witness at each other check rank:

- rank 6 (`N = 9`), a3 = 83; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,2,3}, {0,1,2,4}, {3,4,5}, {2,6}, {0,3,6}, {4,6}, {0,1,2,5,6}, {3,5,6}, {0,1,2,4,5,6}, {7}, {1,3,7}, {0,1,2,4,7}, {3,4,5,7}, {0,1,6,7}, {1,2,3,6,7}, {4,6,7}, {0,1,2,5,6,7}, {3,5,6,7}, {0,1,2,4,5,6,7}, {8}, {0,2,3,8}, {4,8}, {3,4,5,8}, {2,6,8}, {0,3,6,8}, {4,6,8}, {5,6,8}, {3,5,6,8}, {4,5,6,8}, {0,1,2,7,8}, {1,3,7,8}, {4,7,8}, {3,4,5,7,8}, {0,1,6,7,8}, {1,2,3,6,7,8}, {4,6,7,8}, {5,6,7,8}, {3,5,6,7,8}, {4,5,6,7,8}]
  ```

- rank 8 (`N = 11`), a3 = 23; length40_m8_discovery_034, origin 64; rep_length40_m8_discovery_034.json

  ```text
  [{0,1,2,7}, {0,1,2,8}, {0,1,2,7,8}, {1,2,9}, {1,2,7,9}, {1,2,8,9}, {1,2,7,8,9}, {0,10}, {0,4,7,10}, {0,2,3,5,7,10}, {0,2,3,4,5,7,10}, {2,3,6,7,10}, {2,3,4,6,7,10}, {3,5,6,7,10}, {3,4,5,6,7,10}, {0,5,8,10}, {0,6,8,10}, {0,5,6,8,10}, {0,2,3,5,7,8,10}, {0,4,5,7,8,10}, {0,2,3,4,5,7,8,10}, {2,3,6,7,8,10}, {0,4,6,7,8,10}, {2,3,4,6,7,8,10}, {3,5,6,7,8,10}, {0,4,5,6,7,8,10}, {3,4,5,6,7,8,10}, {9,10}, {3,7,9,10}, {4,7,9,10}, {3,4,7,9,10}, {5,8,9,10}, {6,8,9,10}, {5,6,8,9,10}, {3,7,8,9,10}, {3,4,7,8,9,10}, {4,5,7,8,9,10}, {4,6,7,8,9,10}, {4,5,6,7,8,9,10}]
  ```

- rank 9 (`N = 12`), a3 = 31; length40_m9_discovery_006, origin 0; rep_length40_m9_discovery_006.json

  ```text
  [{0,1,2,8}, {0,1,2,9}, {0,1,2,8,9}, {0,1,2,10}, {0,1,2,8,10}, {0,1,2,9,10}, {0,1,2,8,9,10}, {0,1,3,11}, {1,3,4,11}, {0,3,5,11}, {3,4,5,11}, {0,1,3,6,11}, {4,6,11}, {1,3,4,6,11}, {5,6,11}, {0,3,5,6,11}, {4,5,6,11}, {3,4,5,6,11}, {0,1,3,7,11}, {1,3,4,7,11}, {0,3,5,7,11}, {3,4,5,7,11}, {0,1,3,6,7,11}, {1,3,4,6,7,11}, {0,3,5,6,7,11}, {3,4,5,6,7,11}, {6,8,11}, {4,6,9,11}, {5,6,9,11}, {4,5,6,9,11}, {6,8,9,11}, {4,6,10,11}, {5,6,10,11}, {4,5,6,10,11}, {6,8,10,11}, {4,6,9,10,11}, {5,6,9,10,11}, {4,5,6,9,10,11}, {6,8,9,10,11}]
  ```

### 15. `[[39,3,3]]` — T0·CS12·CCZ012

- gate `0+12+012`, `N = 11` (3 outputs + 8 checks), T-count 3, reduced degree 1, a3 = 51
- source: length40_m8_discovery_028, origin 208; rep_length40_m8_discovery_028.json

```text
[{0,1,2,3}, {0,1,4}, {0,1,2,5}, {0,1,2,3,5}, {1,2,6}, {1,2,4,6}, {0,2,7}, {0,1,5,7}, {0,1,4,5,7}, {1,2,5,6,7}, {1,2,4,5,6,7}, {0,2,3,8}, {0,2,4,8}, {0,2,3,5,8}, {4,6,8}, {5,6,8}, {0,2,4,5,7,8}, {6,7,8}, {4,5,6,7,8}, {0,2,9}, {1,6,9}, {1,3,6,9}, {1,5,6,9}, {1,3,5,6,9}, {0,2,7,9}, {0,2,5,8,9}, {3,6,8,9}, {3,5,6,8,9}, {0,2,5,7,8,9}, {6,7,8,9}, {5,6,7,8,9}, {10}, {7,10}, {8,10}, {7,8,10}, {9,10}, {7,9,10}, {8,9,10}, {7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 9`), a3 = 133; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,3}, {0,1,2,4}, {0,2,3,4,5}, {0,2,6}, {0,1,2,3,6}, {0,1,2,4,6}, {5,6}, {3,5,6}, {0,2,4,5,6}, {0,1,2,7}, {1,3,7}, {4,7}, {0,2,3,4,5,7}, {1,6,7}, {0,1,2,3,6,7}, {4,6,7}, {0,5,6,7}, {0,3,5,6,7}, {0,2,4,5,6,7}, {0,2,8}, {1,3,8}, {0,1,2,4,8}, {3,4,5,8}, {0,2,6,8}, {1,3,6,8}, {0,1,2,4,6,8}, {0,5,6,8}, {0,3,5,6,8}, {4,5,6,8}, {0,1,7,8}, {0,1,3,7,8}, {4,7,8}, {3,4,5,7,8}, {1,6,7,8}, {1,3,6,7,8}, {4,6,7,8}, {5,6,7,8}, {3,5,6,7,8}, {4,5,6,7,8}]
  ```

- rank 7 (`N = 10`), a3 = 63; length40_m7_003, origin 70; rep_length40_m7_003.json

  ```text
  [{0,2,5}, {3,5}, {1,3,4,5}, {0,1,2,6}, {3,5,6}, {0,1,4,5,6}, {1,3,4,5,6}, {0,1,7}, {0,2,4,7}, {0,2,6,7}, {0,2,4,6,7}, {0,2,5,6,7}, {0,1,4,5,6,7}, {0,1,2,4,8}, {1,3,5,8}, {0,2,4,5,8}, {3,4,5,8}, {0,1,2,4,6,8}, {0,2,5,6,8}, {1,3,5,6,8}, {3,4,5,6,8}, {0,2,5,7,8}, {0,2,4,5,7,8}, {1,2,5,9}, {3,5,9}, {3,6,9}, {1,2,4,6,9}, {3,7,9}, {1,2,5,7,9}, {1,2,4,6,7,9}, {3,5,6,7,9}, {5,8,9}, {3,5,8,9}, {3,6,8,9}, {4,6,8,9}, {3,7,8,9}, {5,7,8,9}, {4,6,7,8,9}, {3,5,6,7,8,9}]
  ```

- rank 9 (`N = 12`), a3 = 67; length40_m9_discovery_015, origin 496; rep_length40_m9_discovery_015.json

  ```text
  [{0,1,3}, {0,2,4}, {0,2,5}, {0,2,4,5}, {1,3,6}, {1,4,6}, {1,5,6}, {1,4,5,6}, {0,2,5,7}, {0,2,3,5,7}, {2,5,6,7}, {2,3,5,6,7}, {0,1,2,3,8}, {1,2,6,8}, {1,2,3,6,8}, {0,5,7,8}, {0,3,5,7,8}, {5,6,7,8}, {3,5,6,7,8}, {0,1,2,4,9}, {0,1,2,5,9}, {0,1,2,4,5,9}, {6,9}, {4,6,9}, {5,6,9}, {4,5,6,9}, {0,1,2,8,9}, {0,1,2,10}, {0,1,2,8,10}, {0,1,2,9,10}, {0,1,2,8,9,10}, {7,11}, {7,8,11}, {7,9,11}, {7,8,9,11}, {7,10,11}, {7,8,10,11}, {7,9,10,11}, {7,8,9,10,11}]
  ```

### 16. `[[39,3,3]]` — T0·T2·CS01

- gate `0+2+01`, `N = 11` (3 outputs + 8 checks), T-count 3, reduced degree 1, a3 = 51
- source: length40_m8_discovery_028, origin 208; rep_length40_m8_discovery_028.json

```text
[{0,1,3}, {2,4}, {0,1,5}, {0,1,3,5}, {1,2,6}, {1,2,4,6}, {1,7}, {2,5,7}, {2,4,5,7}, {1,2,5,6,7}, {1,2,4,5,6,7}, {1,3,8}, {1,4,8}, {1,3,5,8}, {4,6,8}, {5,6,8}, {1,4,5,7,8}, {6,7,8}, {4,5,6,7,8}, {1,9}, {0,6,9}, {0,3,6,9}, {0,5,6,9}, {0,3,5,6,9}, {1,7,9}, {1,5,8,9}, {3,6,8,9}, {3,5,6,8,9}, {1,5,7,8,9}, {6,7,8,9}, {5,6,7,8,9}, {10}, {7,10}, {8,10}, {7,8,10}, {9,10}, {7,9,10}, {8,9,10}, {7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 9`), a3 = 133; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{1,3}, {2,4}, {0,1,3,4,5}, {0,1,6}, {2,3,6}, {2,4,6}, {5,6}, {3,5,6}, {0,1,4,5,6}, {2,7}, {0,1,2,3,7}, {4,7}, {0,1,3,4,5,7}, {0,1,2,6,7}, {2,3,6,7}, {4,6,7}, {0,2,5,6,7}, {0,2,3,5,6,7}, {0,1,4,5,6,7}, {0,1,8}, {0,1,2,3,8}, {2,4,8}, {3,4,5,8}, {0,1,6,8}, {0,1,2,3,6,8}, {2,4,6,8}, {0,2,5,6,8}, {0,2,3,5,6,8}, {4,5,6,8}, {1,7,8}, {1,3,7,8}, {4,7,8}, {3,4,5,7,8}, {0,1,2,6,7,8}, {0,1,2,3,6,7,8}, {4,6,7,8}, {5,6,7,8}, {3,5,6,7,8}, {4,5,6,7,8}]
  ```

- rank 7 (`N = 10`), a3 = 63; length40_m7_003, origin 70; rep_length40_m7_003.json

  ```text
  [{1,5}, {3,5}, {0,3,4,5}, {0,1,6}, {3,5,6}, {2,4,5,6}, {0,3,4,5,6}, {2,7}, {1,4,7}, {1,6,7}, {1,4,6,7}, {1,5,6,7}, {2,4,5,6,7}, {0,1,4,8}, {0,3,5,8}, {1,4,5,8}, {3,4,5,8}, {0,1,4,6,8}, {1,5,6,8}, {0,3,5,6,8}, {3,4,5,6,8}, {1,5,7,8}, {1,4,5,7,8}, {1,2,5,9}, {3,5,9}, {3,6,9}, {1,2,4,6,9}, {3,7,9}, {1,2,5,7,9}, {1,2,4,6,7,9}, {3,5,6,7,9}, {5,8,9}, {3,5,8,9}, {3,6,8,9}, {4,6,8,9}, {3,7,8,9}, {5,7,8,9}, {4,6,7,8,9}, {3,5,6,7,8,9}]
  ```

- rank 9 (`N = 12`), a3 = 67; length40_m9_discovery_015, origin 496; rep_length40_m9_discovery_015.json

  ```text
  [{1,3}, {0,1,4}, {0,1,5}, {0,1,4,5}, {0,1,2,3,6}, {0,1,2,4,6}, {0,1,2,5,6}, {0,1,2,4,5,6}, {0,1,5,7}, {0,1,3,5,7}, {1,2,5,6,7}, {1,2,3,5,6,7}, {2,3,8}, {0,6,8}, {0,3,6,8}, {0,2,5,7,8}, {0,2,3,5,7,8}, {5,6,7,8}, {3,5,6,7,8}, {2,4,9}, {2,5,9}, {2,4,5,9}, {6,9}, {4,6,9}, {5,6,9}, {4,5,6,9}, {2,8,9}, {2,10}, {2,8,10}, {2,9,10}, {2,8,9,10}, {7,11}, {7,8,11}, {7,9,11}, {7,8,9,11}, {7,10,11}, {7,8,10,11}, {7,9,10,11}, {7,8,9,10,11}]
  ```

### 17. `[[39,3,3]]` — T0·T2·CS01·CS12

- gate `0+2+01+12`, `N = 10` (3 outputs + 7 checks), T-count 2, reduced degree 1, a3 = 51
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{0,1,5}, {0,1,2,3,5}, {1,3,4,5}, {1,2,6}, {0,1,2,3,5,6}, {4,5,6}, {1,3,4,5,6}, {7}, {0,1,4,7}, {0,1,6,7}, {0,1,4,6,7}, {0,1,5,6,7}, {4,5,6,7}, {1,2,4,8}, {1,3,5,8}, {0,1,4,5,8}, {0,1,2,3,4,5,8}, {1,2,4,6,8}, {0,1,5,6,8}, {1,3,5,6,8}, {0,1,2,3,4,5,6,8}, {0,1,5,7,8}, {0,1,4,5,7,8}, {0,1,5,9}, {3,5,9}, {3,6,9}, {0,1,4,6,9}, {3,7,9}, {0,1,5,7,9}, {0,1,4,6,7,9}, {3,5,6,7,9}, {5,8,9}, {3,5,8,9}, {3,6,8,9}, {4,6,8,9}, {3,7,8,9}, {5,7,8,9}, {4,6,7,8,9}, {3,5,6,7,8,9}]
```

Best witness at each other check rank:

- rank 6 (`N = 9`), a3 = 109; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{3}, {2,4}, {2,3,4,5}, {6}, {0,2,3,6}, {2,4,6}, {0,1,2,5,6}, {0,1,2,3,5,6}, {2,4,5,6}, {0,1,7}, {3,7}, {1,4,7}, {2,3,4,5,7}, {1,2,6,7}, {0,2,3,6,7}, {1,4,6,7}, {0,1,2,5,6,7}, {0,1,2,3,5,6,7}, {2,4,5,6,7}, {2,8}, {0,1,2,3,8}, {1,2,4,8}, {3,4,5,8}, {1,6,8}, {0,3,6,8}, {1,2,4,6,8}, {5,6,8}, {3,5,6,8}, {4,5,6,8}, {1,7,8}, {0,1,2,3,7,8}, {4,7,8}, {3,4,5,7,8}, {2,6,7,8}, {0,3,6,7,8}, {4,6,7,8}, {5,6,7,8}, {3,5,6,7,8}, {4,5,6,7,8}]
  ```

- rank 8 (`N = 11`), a3 = 53; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{0,1,2,3}, {0,1,4}, {0,1,5}, {0,1,4,5}, {1,3,6}, {0,1,4,6}, {0,1,5,6}, {0,1,4,5,6}, {7}, {1,5,7}, {0,1,3,5,7}, {0,1,2,5,6,7}, {1,2,3,5,6,7}, {0,3,8}, {0,2,6,8}, {2,3,6,8}, {7,8}, {2,5,7,8}, {0,2,3,5,7,8}, {0,5,6,7,8}, {3,5,6,7,8}, {4,9}, {5,9}, {4,5,9}, {6,9}, {4,6,9}, {5,6,9}, {4,5,6,9}, {7,9}, {8,9}, {7,8,9}, {10}, {7,10}, {8,10}, {7,8,10}, {9,10}, {7,9,10}, {8,9,10}, {7,8,9,10}]
  ```

### 18. `[[39,3,3]]` — CS01·CS02·CCZ012

- gate `01+02+012`, `N = 10` (3 outputs + 7 checks), T-count 3, reduced degree 2, a3 = 64
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{0,5}, {2,3,5}, {1,3,4,5}, {0,1,2,6}, {2,3,5,6}, {1,2,4,5,6}, {1,3,4,5,6}, {1,2,7}, {0,4,7}, {0,6,7}, {0,4,6,7}, {0,5,6,7}, {1,2,4,5,6,7}, {0,1,2,4,8}, {1,3,5,8}, {0,4,5,8}, {2,3,4,5,8}, {0,1,2,4,6,8}, {0,5,6,8}, {1,3,5,6,8}, {2,3,4,5,6,8}, {0,5,7,8}, {0,4,5,7,8}, {0,1,2,5,9}, {3,5,9}, {3,6,9}, {0,1,2,4,6,9}, {3,7,9}, {0,1,2,5,7,9}, {0,1,2,4,6,7,9}, {3,5,6,7,9}, {5,8,9}, {3,5,8,9}, {3,6,8,9}, {4,6,8,9}, {3,7,8,9}, {5,7,8,9}, {4,6,7,8,9}, {3,5,6,7,8,9}]
```

Best witness at each other check rank:

- rank 6 (`N = 9`), a3 = 98; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{1,2,3}, {4}, {3,4,5}, {2,6}, {1,3,6}, {4,6}, {0,5,6}, {3,5,6}, {0,4,5,6}, {1,2,7}, {0,1,2,3,7}, {4,7}, {0,1,2,3,4,5,7}, {0,2,6,7}, {0,1,3,6,7}, {0,1,2,4,6,7}, {0,5,6,7}, {0,1,2,3,5,6,7}, {0,4,5,6,7}, {8}, {3,8}, {0,4,8}, {0,1,2,3,4,5,8}, {1,6,8}, {2,3,6,8}, {0,1,2,4,6,8}, {5,6,8}, {0,1,2,3,5,6,8}, {4,5,6,8}, {1,2,7,8}, {0,3,7,8}, {0,4,7,8}, {3,4,5,7,8}, {0,1,6,7,8}, {0,2,3,6,7,8}, {4,6,7,8}, {5,6,7,8}, {3,5,6,7,8}, {4,5,6,7,8}]
  ```

- rank 8 (`N = 11`), a3 = 74; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{0,1,3}, {0,1,2,4}, {0,1,2,5}, {0,1,2,4,5}, {0,1,3,6}, {0,4,6}, {0,5,6}, {0,4,5,6}, {1,2,7}, {0,2,5,7}, {0,1,2,3,5,7}, {0,2,5,6,7}, {0,1,2,3,5,6,7}, {2,3,8}, {1,2,6,8}, {2,3,6,8}, {1,2,7,8}, {1,5,7,8}, {3,5,7,8}, {1,5,6,7,8}, {3,5,6,7,8}, {1,2,4,9}, {1,2,5,9}, {1,2,4,5,9}, {6,9}, {4,6,9}, {5,6,9}, {4,5,6,9}, {1,2,7,9}, {1,2,8,9}, {1,2,7,8,9}, {10}, {7,10}, {8,10}, {7,8,10}, {9,10}, {7,9,10}, {8,9,10}, {7,8,9,10}]
  ```

### 19. `[[39,3,3]]` — CS01·CS02·CS12

- gate `01+02+12`, `N = 10` (3 outputs + 7 checks), T-count 3, reduced degree 2, a3 = 64
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{0,2,5}, {1,3,5}, {0,3,4,5}, {1,2,6}, {1,3,5,6}, {0,1,4,5,6}, {0,3,4,5,6}, {0,1,7}, {0,2,4,7}, {0,2,6,7}, {0,2,4,6,7}, {0,2,5,6,7}, {0,1,4,5,6,7}, {1,2,4,8}, {0,3,5,8}, {0,2,4,5,8}, {1,3,4,5,8}, {1,2,4,6,8}, {0,2,5,6,8}, {0,3,5,6,8}, {1,3,4,5,6,8}, {0,2,5,7,8}, {0,2,4,5,7,8}, {1,2,5,9}, {3,5,9}, {3,6,9}, {1,2,4,6,9}, {3,7,9}, {1,2,5,7,9}, {1,2,4,6,7,9}, {3,5,6,7,9}, {5,8,9}, {3,5,8,9}, {3,6,8,9}, {4,6,8,9}, {3,7,8,9}, {5,7,8,9}, {4,6,7,8,9}, {3,5,6,7,8,9}]
```

Best witness at each other check rank:

- rank 6 (`N = 9`), a3 = 98; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,3}, {4}, {3,4,5}, {1,6}, {0,3,6}, {4,6}, {0,2,5,6}, {3,5,6}, {0,2,4,5,6}, {0,1,7}, {1,2,3,7}, {4,7}, {1,2,3,4,5,7}, {0,1,2,6,7}, {2,3,6,7}, {1,2,4,6,7}, {0,2,5,6,7}, {1,2,3,5,6,7}, {0,2,4,5,6,7}, {8}, {3,8}, {0,2,4,8}, {1,2,3,4,5,8}, {0,6,8}, {1,3,6,8}, {1,2,4,6,8}, {5,6,8}, {1,2,3,5,6,8}, {4,5,6,8}, {0,1,7,8}, {0,2,3,7,8}, {0,2,4,7,8}, {3,4,5,7,8}, {2,6,7,8}, {0,1,2,3,6,7,8}, {4,6,7,8}, {5,6,7,8}, {3,5,6,7,8}, {4,5,6,7,8}]
  ```

- rank 8 (`N = 11`), a3 = 74; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{2,3}, {1,2,4}, {1,2,5}, {1,2,4,5}, {2,3,6}, {0,2,4,6}, {0,2,5,6}, {0,2,4,5,6}, {0,1,7}, {0,1,2,5,7}, {1,2,3,5,7}, {0,1,2,5,6,7}, {1,2,3,5,6,7}, {1,3,8}, {0,1,6,8}, {1,3,6,8}, {0,1,7,8}, {0,5,7,8}, {3,5,7,8}, {0,5,6,7,8}, {3,5,6,7,8}, {0,1,4,9}, {0,1,5,9}, {0,1,4,5,9}, {6,9}, {4,6,9}, {5,6,9}, {4,5,6,9}, {0,1,7,9}, {0,1,8,9}, {0,1,7,8,9}, {10}, {7,10}, {8,10}, {7,8,10}, {9,10}, {7,9,10}, {8,9,10}, {7,8,9,10}]
  ```

### 20. `[[39,4,3]]` — T0·CS01·CS02·CS03·CCZ012·CCZ013·CCZ023

- gate `0+01+02+03+012+013+023`, `N = 11` (4 outputs + 7 checks), T-count 2, reduced degree 1, a3 = 69
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,3,4}, {0,1,2,3,5}, {0,1,2,3,4,5}, {0,1,2,3,6}, {0,1,2,3,4,6}, {0,1,2,3,4,5,6}, {7}, {0,1,2,4,7}, {1,2,4,5,6,7}, {8}, {2,3,5,8}, {0,2,3,6,8}, {7,8}, {0,2,4,5,7,8}, {2,4,6,7,8}, {0,5,6,9}, {7,9}, {0,3,4,7,9}, {3,4,5,6,7,9}, {8,9}, {1,5,8,9}, {0,1,6,8,9}, {7,8,9}, {0,1,3,4,5,7,8,9}, {1,3,4,6,7,8,9}, {4,10}, {4,7,10}, {4,8,10}, {4,7,8,10}, {9,10}, {5,9,10}, {4,5,9,10}, {6,9,10}, {4,6,9,10}, {5,6,9,10}, {4,5,6,9,10}, {4,7,9,10}, {4,8,9,10}, {4,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 113; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{4}, {0,2,3,5}, {0,1,3,4,5,6}, {1,2,7}, {0,4,7}, {0,1,3,5,7}, {2,6,7}, {2,4,6,7}, {0,1,3,5,6,7}, {0,1,2,3,8}, {4,8}, {0,1,5,8}, {0,1,3,4,5,6,8}, {3,7,8}, {0,4,7,8}, {0,2,5,7,8}, {2,6,7,8}, {2,4,6,7,8}, {0,1,3,5,6,7,8}, {0,1,3,9}, {2,4,9}, {3,5,9}, {4,5,6,9}, {0,1,7,9}, {1,3,4,7,9}, {1,2,3,5,7,9}, {6,7,9}, {4,6,7,9}, {5,6,7,9}, {0,2,8,9}, {2,4,8,9}, {1,2,5,8,9}, {4,5,6,8,9}, {0,2,3,7,8,9}, {1,3,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

### 21. `[[39,4,3]]` — T0·CS01·CS02·CS03·CS12·CS13·CCZ012·CCZ013·CCZ023·CCZ123

- gate `0+01+02+03+12+13+012+013+023+123`, `N = 11` (4 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 67
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{1,6}, {0,1,3,4,6}, {0,2,4,5,6}, {2,3,7}, {0,1,3,4,6,7}, {0,1,2,3,5,6,7}, {0,2,4,5,6,7}, {0,1,2,3,8}, {1,5,8}, {1,7,8}, {1,5,7,8}, {1,6,7,8}, {0,1,2,3,5,6,7,8}, {2,3,5,9}, {0,2,4,6,9}, {1,5,6,9}, {0,1,3,4,5,6,9}, {2,3,5,7,9}, {1,6,7,9}, {0,2,4,6,7,9}, {0,1,3,4,5,6,7,9}, {1,6,8,9}, {1,5,6,8,9}, {0,2,3,6,10}, {4,6,10}, {4,7,10}, {0,2,3,5,7,10}, {4,8,10}, {0,2,3,6,8,10}, {0,2,3,5,7,8,10}, {4,6,7,8,10}, {6,9,10}, {4,6,9,10}, {4,7,9,10}, {5,7,9,10}, {4,8,9,10}, {6,8,9,10}, {5,7,8,9,10}, {4,6,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 137; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{1,4}, {2,5}, {0,1,2,4,5,6}, {2,3,7}, {0,1,2,3,4,7}, {2,5,7}, {0,1,3,6,7}, {0,1,3,4,6,7}, {0,1,2,5,6,7}, {0,1,2,3,8}, {0,1,4,8}, {0,1,3,5,8}, {0,1,2,4,5,6,8}, {0,1,7,8}, {0,1,2,3,4,7,8}, {0,1,3,5,7,8}, {1,3,6,7,8}, {1,3,4,6,7,8}, {0,1,2,5,6,7,8}, {0,1,2,9}, {3,4,9}, {0,1,2,3,5,9}, {4,5,6,9}, {0,1,2,7,9}, {3,4,7,9}, {0,1,2,3,5,7,9}, {0,6,7,9}, {0,4,6,7,9}, {5,6,7,9}, {0,3,8,9}, {0,3,4,8,9}, {5,8,9}, {4,5,6,8,9}, {3,7,8,9}, {3,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

- rank 8 (`N = 12`), a3 = 75; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{0,3,4}, {2,3,5}, {2,3,6}, {2,3,5,6}, {3,4,7}, {0,1,5,7}, {0,1,6,7}, {0,1,5,6,7}, {0,1,2,3,8}, {0,1,2,6,8}, {2,3,4,6,8}, {1,2,6,7,8}, {0,2,3,4,6,7,8}, {2,4,9}, {1,2,3,7,9}, {0,2,4,7,9}, {0,1,2,3,8,9}, {1,3,6,8,9}, {0,4,6,8,9}, {0,1,3,6,7,8,9}, {4,6,7,8,9}, {0,1,2,3,5,10}, {0,1,2,3,6,10}, {0,1,2,3,5,6,10}, {7,10}, {5,7,10}, {6,7,10}, {5,6,7,10}, {0,1,2,3,8,10}, {0,1,2,3,9,10}, {0,1,2,3,8,9,10}, {11}, {8,11}, {9,11}, {8,9,11}, {10,11}, {8,10,11}, {9,10,11}, {8,9,10,11}]
  ```

### 22. `[[39,4,3]]` — T0·CS01·CS02·CS12·CS13·CS23·CCZ012

- gate `0+01+02+12+13+23+012`, `N = 11` (4 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 67
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{0,1,2,6}, {0,3,4,6}, {1,4,5,6}, {2,3,7}, {0,3,4,6,7}, {1,3,5,6,7}, {1,4,5,6,7}, {1,3,8}, {0,1,2,5,8}, {0,1,2,7,8}, {0,1,2,5,7,8}, {0,1,2,6,7,8}, {1,3,5,6,7,8}, {2,3,5,9}, {1,4,6,9}, {0,1,2,5,6,9}, {0,3,4,5,6,9}, {2,3,5,7,9}, {0,1,2,6,7,9}, {1,4,6,7,9}, {0,3,4,5,6,7,9}, {0,1,2,6,8,9}, {0,1,2,5,6,8,9}, {0,2,3,6,10}, {4,6,10}, {4,7,10}, {0,2,3,5,7,10}, {4,8,10}, {0,2,3,6,8,10}, {0,2,3,5,7,8,10}, {4,6,7,8,10}, {6,9,10}, {4,6,9,10}, {4,7,9,10}, {5,7,9,10}, {4,8,9,10}, {6,8,9,10}, {5,7,8,9,10}, {4,6,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 137; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{2,3,4}, {3,5}, {0,2,4,5,6}, {1,3,7}, {0,1,2,4,7}, {3,5,7}, {0,1,2,3,6,7}, {0,1,2,3,4,6,7}, {0,2,5,6,7}, {0,1,2,8}, {0,2,3,4,8}, {0,1,2,3,5,8}, {0,2,4,5,6,8}, {0,2,3,7,8}, {0,1,2,4,7,8}, {0,1,2,3,5,7,8}, {1,2,3,6,7,8}, {1,2,3,4,6,7,8}, {0,2,5,6,7,8}, {0,2,9}, {1,4,9}, {0,1,2,5,9}, {4,5,6,9}, {0,2,7,9}, {1,4,7,9}, {0,1,2,5,7,9}, {0,6,7,9}, {0,4,6,7,9}, {5,6,7,9}, {0,1,8,9}, {0,1,4,8,9}, {5,8,9}, {4,5,6,8,9}, {1,7,8,9}, {1,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

- rank 8 (`N = 12`), a3 = 75; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{0,1,4}, {0,1,2,5}, {0,1,2,6}, {0,1,2,5,6}, {1,4,7}, {0,1,3,5,7}, {0,1,3,6,7}, {0,1,3,5,6,7}, {2,3,8}, {1,2,3,6,8}, {0,1,2,4,6,8}, {0,1,2,3,6,7,8}, {1,2,4,6,7,8}, {0,2,4,9}, {0,2,3,7,9}, {2,4,7,9}, {2,3,8,9}, {3,6,8,9}, {0,4,6,8,9}, {0,3,6,7,8,9}, {4,6,7,8,9}, {2,3,5,10}, {2,3,6,10}, {2,3,5,6,10}, {7,10}, {5,7,10}, {6,7,10}, {5,6,7,10}, {2,3,8,10}, {2,3,9,10}, {2,3,8,9,10}, {11}, {8,11}, {9,11}, {8,9,11}, {10,11}, {8,10,11}, {9,10,11}, {8,9,10,11}]
  ```

### 23. `[[39,4,3]]` — T0·CS01·CS02·CS13·CS23·CCZ012·CCZ123

- gate `0+01+02+13+23+012+123`, `N = 11` (4 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 67
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{3,6}, {1,4,6}, {2,4,5,6}, {1,2,3,7}, {1,4,6,7}, {0,1,2,5,6,7}, {2,4,5,6,7}, {0,1,2,8}, {3,5,8}, {3,7,8}, {3,5,7,8}, {3,6,7,8}, {0,1,2,5,6,7,8}, {1,2,3,5,9}, {2,4,6,9}, {3,5,6,9}, {1,4,5,6,9}, {1,2,3,5,7,9}, {3,6,7,9}, {2,4,6,7,9}, {1,4,5,6,7,9}, {3,6,8,9}, {3,5,6,8,9}, {0,1,2,3,6,10}, {4,6,10}, {4,7,10}, {0,1,2,3,5,7,10}, {4,8,10}, {0,1,2,3,6,8,10}, {0,1,2,3,5,7,8,10}, {4,6,7,8,10}, {6,9,10}, {4,6,9,10}, {4,7,9,10}, {5,7,9,10}, {4,8,9,10}, {6,8,9,10}, {5,7,8,9,10}, {4,6,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 137; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{3,4}, {1,5}, {0,1,3,4,5,6}, {1,2,3,7}, {0,1,2,4,7}, {1,5,7}, {0,2,6,7}, {0,2,4,6,7}, {0,1,3,5,6,7}, {0,1,2,8}, {0,3,4,8}, {0,2,5,8}, {0,1,3,4,5,6,8}, {0,3,7,8}, {0,1,2,4,7,8}, {0,2,5,7,8}, {2,6,7,8}, {2,4,6,7,8}, {0,1,3,5,6,7,8}, {0,1,3,9}, {2,3,4,9}, {0,1,2,5,9}, {4,5,6,9}, {0,1,3,7,9}, {2,3,4,7,9}, {0,1,2,5,7,9}, {0,6,7,9}, {0,4,6,7,9}, {5,6,7,9}, {0,2,3,8,9}, {0,2,3,4,8,9}, {5,8,9}, {4,5,6,8,9}, {2,3,7,8,9}, {2,3,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

- rank 8 (`N = 12`), a3 = 75; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{0,1,3,4}, {3,5}, {3,6}, {3,5,6}, {1,3,4,7}, {1,2,5,7}, {1,2,6,7}, {1,2,5,6,7}, {1,2,3,8}, {2,6,8}, {3,4,6,8}, {0,2,6,7,8}, {0,3,4,6,7,8}, {1,4,9}, {0,1,2,3,7,9}, {0,1,4,7,9}, {1,2,3,8,9}, {0,2,3,6,8,9}, {0,4,6,8,9}, {2,3,6,7,8,9}, {4,6,7,8,9}, {1,2,3,5,10}, {1,2,3,6,10}, {1,2,3,5,6,10}, {7,10}, {5,7,10}, {6,7,10}, {5,6,7,10}, {1,2,3,8,10}, {1,2,3,9,10}, {1,2,3,8,9,10}, {11}, {8,11}, {9,11}, {8,9,11}, {10,11}, {8,10,11}, {9,10,11}, {8,9,10,11}]
  ```

### 24. `[[39,4,3]]` — T0·CS01·CS12·CS13·CCZ123

- gate `0+01+12+13+123`, `N = 11` (4 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 67
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{1,2,3,6}, {0,2,4,6}, {0,1,2,4,5,6}, {2,3,7}, {0,2,4,6,7}, {0,1,5,6,7}, {0,1,2,4,5,6,7}, {0,1,8}, {1,2,3,5,8}, {1,2,3,7,8}, {1,2,3,5,7,8}, {1,2,3,6,7,8}, {0,1,5,6,7,8}, {2,3,5,9}, {0,1,2,4,6,9}, {1,2,3,5,6,9}, {0,2,4,5,6,9}, {2,3,5,7,9}, {1,2,3,6,7,9}, {0,1,2,4,6,7,9}, {0,2,4,5,6,7,9}, {1,2,3,6,8,9}, {1,2,3,5,6,8,9}, {0,2,3,6,10}, {4,6,10}, {4,7,10}, {0,2,3,5,7,10}, {4,8,10}, {0,2,3,6,8,10}, {0,2,3,5,7,8,10}, {4,6,7,8,10}, {6,9,10}, {4,6,9,10}, {4,7,9,10}, {5,7,9,10}, {4,8,9,10}, {6,8,9,10}, {5,7,8,9,10}, {4,6,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 137; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,4}, {0,1,3,5}, {0,3,4,5,6}, {2,3,7}, {1,2,3,4,7}, {0,1,3,5,7}, {0,2,6,7}, {0,2,4,6,7}, {0,3,5,6,7}, {1,2,3,8}, {1,4,8}, {0,2,5,8}, {0,3,4,5,6,8}, {1,7,8}, {1,2,3,4,7,8}, {0,2,5,7,8}, {2,6,7,8}, {2,4,6,7,8}, {0,3,5,6,7,8}, {0,3,9}, {0,1,2,4,9}, {1,2,3,5,9}, {4,5,6,9}, {0,3,7,9}, {0,1,2,4,7,9}, {1,2,3,5,7,9}, {0,6,7,9}, {0,4,6,7,9}, {5,6,7,9}, {1,2,8,9}, {1,2,4,8,9}, {5,8,9}, {4,5,6,8,9}, {0,1,2,7,8,9}, {0,1,2,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

- rank 8 (`N = 12`), a3 = 75; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{1,3,4}, {2,3,5}, {2,3,6}, {2,3,5,6}, {0,1,3,4,7}, {1,5,7}, {1,6,7}, {1,5,6,7}, {1,2,3,8}, {0,2,6,8}, {2,3,4,6,8}, {2,6,7,8}, {0,2,3,4,6,7,8}, {0,1,2,4,9}, {0,1,2,3,7,9}, {1,2,4,7,9}, {1,2,3,8,9}, {3,6,8,9}, {0,4,6,8,9}, {0,3,6,7,8,9}, {4,6,7,8,9}, {1,2,3,5,10}, {1,2,3,6,10}, {1,2,3,5,6,10}, {7,10}, {5,7,10}, {6,7,10}, {5,6,7,10}, {1,2,3,8,10}, {1,2,3,9,10}, {1,2,3,8,9,10}, {11}, {8,11}, {9,11}, {8,9,11}, {10,11}, {8,10,11}, {9,10,11}, {8,9,10,11}]
  ```

### 25. `[[39,4,3]]` — T0·T1·CS01·CS02·CS03·CCZ012·CCZ013·CCZ023

- gate `0+1+01+02+03+012+013+023`, `N = 11` (4 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 67
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{1,2,3,6}, {3,4,6}, {2,4,5,6}, {1,7}, {3,4,6,7}, {0,1,2,3,5,6,7}, {2,4,5,6,7}, {0,1,2,3,8}, {1,2,3,5,8}, {1,2,3,7,8}, {1,2,3,5,7,8}, {1,2,3,6,7,8}, {0,1,2,3,5,6,7,8}, {1,5,9}, {2,4,6,9}, {1,2,3,5,6,9}, {3,4,5,6,9}, {1,5,7,9}, {1,2,3,6,7,9}, {2,4,6,7,9}, {3,4,5,6,7,9}, {1,2,3,6,8,9}, {1,2,3,5,6,8,9}, {0,6,10}, {4,6,10}, {4,7,10}, {0,5,7,10}, {4,8,10}, {0,6,8,10}, {0,5,7,8,10}, {4,6,7,8,10}, {6,9,10}, {4,6,9,10}, {4,7,9,10}, {5,7,9,10}, {4,8,9,10}, {6,8,9,10}, {5,7,8,9,10}, {4,6,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 137; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,3,4}, {3,5}, {2,4,5,6}, {1,7}, {1,2,3,4,7}, {3,5,7}, {1,2,6,7}, {1,2,4,6,7}, {2,5,6,7}, {1,2,3,8}, {2,3,4,8}, {1,2,5,8}, {2,4,5,6,8}, {2,3,7,8}, {1,2,3,4,7,8}, {1,2,5,7,8}, {0,2,6,7,8}, {0,2,4,6,7,8}, {2,5,6,7,8}, {2,9}, {1,3,4,9}, {1,2,3,5,9}, {4,5,6,9}, {2,7,9}, {1,3,4,7,9}, {1,2,3,5,7,9}, {0,1,6,7,9}, {0,1,4,6,7,9}, {5,6,7,9}, {0,3,8,9}, {0,3,4,8,9}, {5,8,9}, {4,5,6,8,9}, {1,3,7,8,9}, {1,3,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

- rank 8 (`N = 12`), a3 = 75; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{0,3,4}, {1,5}, {1,6}, {1,5,6}, {1,3,4,7}, {2,3,5,7}, {2,3,6,7}, {2,3,5,6,7}, {1,2,3,8}, {2,6,8}, {1,4,6,8}, {0,1,2,6,7,8}, {0,4,6,7,8}, {3,4,9}, {0,2,3,7,9}, {0,1,3,4,7,9}, {1,2,3,8,9}, {0,2,6,8,9}, {0,1,4,6,8,9}, {1,2,6,7,8,9}, {4,6,7,8,9}, {1,2,3,5,10}, {1,2,3,6,10}, {1,2,3,5,6,10}, {7,10}, {5,7,10}, {6,7,10}, {5,6,7,10}, {1,2,3,8,10}, {1,2,3,9,10}, {1,2,3,8,9,10}, {11}, {8,11}, {9,11}, {8,9,11}, {10,11}, {8,10,11}, {9,10,11}, {8,9,10,11}]
  ```

### 26. `[[39,4,3]]` — T0·T1·CS01·CS02·CS03·CS12·CS13·CCZ012·CCZ013·CCZ023·CCZ123

- gate `0+1+01+02+03+12+13+012+013+023+123`, `N = 11` (4 outputs + 7 checks), T-count 2, reduced degree 1, a3 = 69
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,3,4}, {0,1,2,3,5}, {0,1,2,3,4,5}, {0,1,2,3,6}, {0,1,2,3,4,6}, {0,1,2,3,4,5,6}, {7}, {0,1,2,4,7}, {2,4,5,6,7}, {8}, {0,2,3,5,8}, {1,2,3,6,8}, {7,8}, {1,2,4,5,7,8}, {0,2,4,6,7,8}, {0,1,5,6,9}, {7,9}, {0,1,3,4,7,9}, {3,4,5,6,7,9}, {8,9}, {0,5,8,9}, {1,6,8,9}, {7,8,9}, {1,3,4,5,7,8,9}, {0,3,4,6,7,8,9}, {4,10}, {4,7,10}, {4,8,10}, {4,7,8,10}, {9,10}, {5,9,10}, {4,5,9,10}, {6,9,10}, {4,6,9,10}, {5,6,9,10}, {4,5,6,9,10}, {4,7,9,10}, {4,8,9,10}, {4,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 113; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{4}, {0,2,3,5}, {1,3,4,5,6}, {0,1,2,7}, {0,1,4,7}, {1,3,5,7}, {1,2,6,7}, {1,2,4,6,7}, {1,3,5,6,7}, {2,3,8}, {4,8}, {1,5,8}, {1,3,4,5,6,8}, {3,7,8}, {0,1,4,7,8}, {0,2,5,7,8}, {1,2,6,7,8}, {1,2,4,6,7,8}, {1,3,5,6,7,8}, {1,3,9}, {1,2,4,9}, {3,5,9}, {4,5,6,9}, {1,7,9}, {0,3,4,7,9}, {0,1,2,3,5,7,9}, {6,7,9}, {4,6,7,9}, {5,6,7,9}, {0,2,8,9}, {1,2,4,8,9}, {0,1,2,5,8,9}, {4,5,6,8,9}, {0,2,3,7,8,9}, {0,3,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

### 27. `[[39,4,3]]` — T0·T1·CS01·CS02·CS03·CS12·CS13·CS23·CCZ012·CCZ013·CCZ023·CCZ123

- gate `0+1+01+02+03+12+13+23+012+013+023+123`, `N = 11` (4 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 67
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{0,1,2,3,6}, {0,2,4,6}, {1,2,3,4,5,6}, {2,7}, {0,2,4,6,7}, {3,5,6,7}, {1,2,3,4,5,6,7}, {3,8}, {0,1,2,3,5,8}, {0,1,2,3,7,8}, {0,1,2,3,5,7,8}, {0,1,2,3,6,7,8}, {3,5,6,7,8}, {2,5,9}, {1,2,3,4,6,9}, {0,1,2,3,5,6,9}, {0,2,4,5,6,9}, {2,5,7,9}, {0,1,2,3,6,7,9}, {1,2,3,4,6,7,9}, {0,2,4,5,6,7,9}, {0,1,2,3,6,8,9}, {0,1,2,3,5,6,8,9}, {0,1,2,6,10}, {4,6,10}, {4,7,10}, {0,1,2,5,7,10}, {4,8,10}, {0,1,2,6,8,10}, {0,1,2,5,7,8,10}, {4,6,7,8,10}, {6,9,10}, {4,6,9,10}, {4,7,9,10}, {5,7,9,10}, {4,8,9,10}, {6,8,9,10}, {5,7,8,9,10}, {4,6,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 137; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{2,4}, {1,2,5}, {0,4,5,6}, {3,7}, {0,1,2,3,4,7}, {1,2,5,7}, {0,3,6,7}, {0,3,4,6,7}, {0,5,6,7}, {0,1,2,3,8}, {0,1,2,4,8}, {0,3,5,8}, {0,4,5,6,8}, {0,1,2,7,8}, {0,1,2,3,4,7,8}, {0,3,5,7,8}, {1,3,6,7,8}, {1,3,4,6,7,8}, {0,5,6,7,8}, {0,9}, {1,2,3,4,9}, {0,1,2,3,5,9}, {4,5,6,9}, {0,7,9}, {1,2,3,4,7,9}, {0,1,2,3,5,7,9}, {0,1,6,7,9}, {0,1,4,6,7,9}, {5,6,7,9}, {0,2,3,8,9}, {0,2,3,4,8,9}, {5,8,9}, {4,5,6,8,9}, {1,2,3,7,8,9}, {1,2,3,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

- rank 8 (`N = 12`), a3 = 75; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{1,2,4}, {3,5}, {3,6}, {3,5,6}, {0,2,4,7}, {2,3,5,7}, {2,3,6,7}, {2,3,5,6,7}, {2,8}, {0,6,8}, {3,4,6,8}, {1,6,7,8}, {0,1,3,4,6,7,8}, {0,2,3,4,9}, {0,1,2,7,9}, {1,2,3,4,7,9}, {2,8,9}, {1,3,6,8,9}, {0,1,4,6,8,9}, {0,3,6,7,8,9}, {4,6,7,8,9}, {2,5,10}, {2,6,10}, {2,5,6,10}, {7,10}, {5,7,10}, {6,7,10}, {5,6,7,10}, {2,8,10}, {2,9,10}, {2,8,9,10}, {11}, {8,11}, {9,11}, {8,9,11}, {10,11}, {8,10,11}, {9,10,11}, {8,9,10,11}]
  ```

### 28. `[[39,4,3]]` — T0·T1·CS01·CS02·CS03·CS23·CCZ012·CCZ013·CCZ023·CCZ123

- gate `0+1+01+02+03+23+012+013+023+123`, `N = 11` (4 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 67
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{1,2,6}, {0,1,3,4,6}, {0,1,2,4,5,6}, {1,3,7}, {0,1,3,4,6,7}, {0,1,2,3,5,6,7}, {0,1,2,4,5,6,7}, {0,1,2,3,8}, {1,2,5,8}, {1,2,7,8}, {1,2,5,7,8}, {1,2,6,7,8}, {0,1,2,3,5,6,7,8}, {1,3,5,9}, {0,1,2,4,6,9}, {1,2,5,6,9}, {0,1,3,4,5,6,9}, {1,3,5,7,9}, {1,2,6,7,9}, {0,1,2,4,6,7,9}, {0,1,3,4,5,6,7,9}, {1,2,6,8,9}, {1,2,5,6,8,9}, {0,3,6,10}, {4,6,10}, {4,7,10}, {0,3,5,7,10}, {4,8,10}, {0,3,6,8,10}, {0,3,5,7,8,10}, {4,6,7,8,10}, {6,9,10}, {4,6,9,10}, {4,7,9,10}, {5,7,9,10}, {4,8,9,10}, {6,8,9,10}, {5,7,8,9,10}, {4,6,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 137; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{1,2,4}, {2,5}, {0,4,5,6}, {1,3,7}, {0,1,2,3,4,7}, {2,5,7}, {0,1,3,6,7}, {0,1,3,4,6,7}, {0,5,6,7}, {0,1,2,3,8}, {0,2,4,8}, {0,1,3,5,8}, {0,4,5,6,8}, {0,2,7,8}, {0,1,2,3,4,7,8}, {0,1,3,5,7,8}, {3,6,7,8}, {3,4,6,7,8}, {0,5,6,7,8}, {0,9}, {1,2,3,4,9}, {0,1,2,3,5,9}, {4,5,6,9}, {0,7,9}, {1,2,3,4,7,9}, {0,1,2,3,5,7,9}, {0,1,6,7,9}, {0,1,4,6,7,9}, {5,6,7,9}, {0,2,3,8,9}, {0,2,3,4,8,9}, {5,8,9}, {4,5,6,8,9}, {1,2,3,7,8,9}, {1,2,3,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

- rank 8 (`N = 12`), a3 = 75; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{0,2,3,4}, {0,1,2,3,5}, {0,1,2,3,6}, {0,1,2,3,5,6}, {1,2,3,4,7}, {0,3,5,7}, {0,3,6,7}, {0,3,5,6,7}, {1,2,8}, {3,6,8}, {0,1,2,3,4,6,8}, {0,1,3,6,7,8}, {2,3,4,6,7,8}, {0,4,9}, {0,2,7,9}, {1,4,7,9}, {1,2,8,9}, {2,6,8,9}, {0,1,4,6,8,9}, {0,1,2,6,7,8,9}, {4,6,7,8,9}, {1,2,5,10}, {1,2,6,10}, {1,2,5,6,10}, {7,10}, {5,7,10}, {6,7,10}, {5,6,7,10}, {1,2,8,10}, {1,2,9,10}, {1,2,8,9,10}, {11}, {8,11}, {9,11}, {8,9,11}, {10,11}, {8,10,11}, {9,10,11}, {8,9,10,11}]
  ```

### 29. `[[39,4,3]]` — T0·T1·CS01·CS02·CS12·CS23·CCZ012

- gate `0+1+01+02+12+23+012`, `N = 11` (4 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 67
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{0,1,2,6}, {0,3,4,6}, {1,4,5,6}, {2,3,7}, {0,3,4,6,7}, {3,5,6,7}, {1,4,5,6,7}, {3,8}, {0,1,2,5,8}, {0,1,2,7,8}, {0,1,2,5,7,8}, {0,1,2,6,7,8}, {3,5,6,7,8}, {2,3,5,9}, {1,4,6,9}, {0,1,2,5,6,9}, {0,3,4,5,6,9}, {2,3,5,7,9}, {0,1,2,6,7,9}, {1,4,6,7,9}, {0,3,4,5,6,7,9}, {0,1,2,6,8,9}, {0,1,2,5,6,8,9}, {0,1,2,3,6,10}, {4,6,10}, {4,7,10}, {0,1,2,3,5,7,10}, {4,8,10}, {0,1,2,3,6,8,10}, {0,1,2,3,5,7,8,10}, {4,6,7,8,10}, {6,9,10}, {4,6,9,10}, {4,7,9,10}, {5,7,9,10}, {4,8,9,10}, {6,8,9,10}, {5,7,8,9,10}, {4,6,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 137; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{2,3,4}, {1,3,5}, {0,2,4,5,6}, {0,1,2,7}, {3,4,7}, {1,3,5,7}, {1,6,7}, {1,4,6,7}, {0,2,5,6,7}, {3,8}, {0,1,2,3,4,8}, {1,5,8}, {0,2,4,5,6,8}, {0,1,2,3,7,8}, {3,4,7,8}, {1,5,7,8}, {0,6,7,8}, {0,4,6,7,8}, {0,2,5,6,7,8}, {0,2,9}, {0,2,3,4,9}, {3,5,9}, {4,5,6,9}, {0,2,7,9}, {0,2,3,4,7,9}, {3,5,7,9}, {0,1,6,7,9}, {0,1,4,6,7,9}, {5,6,7,9}, {1,2,3,8,9}, {1,2,3,4,8,9}, {5,8,9}, {4,5,6,8,9}, {0,2,3,7,8,9}, {0,2,3,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

- rank 8 (`N = 12`), a3 = 75; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{0,3,4}, {0,1,2,5}, {0,1,2,6}, {0,1,2,5,6}, {1,3,4,7}, {0,1,2,3,5,7}, {0,1,2,3,6,7}, {0,1,2,3,5,6,7}, {3,8}, {1,6,8}, {0,1,2,4,6,8}, {0,6,7,8}, {2,4,6,7,8}, {0,2,3,4,9}, {0,1,3,7,9}, {1,2,3,4,7,9}, {3,8,9}, {1,2,6,8,9}, {0,1,4,6,8,9}, {0,2,6,7,8,9}, {4,6,7,8,9}, {3,5,10}, {3,6,10}, {3,5,6,10}, {7,10}, {5,7,10}, {6,7,10}, {5,6,7,10}, {3,8,10}, {3,9,10}, {3,8,9,10}, {11}, {8,11}, {9,11}, {8,9,11}, {10,11}, {8,10,11}, {9,10,11}, {8,9,10,11}]
  ```

### 30. `[[39,4,3]]` — T0·T1·CS01·CS02·CS23·CCZ012·CCZ123

- gate `0+1+01+02+23+012+123`, `N = 11` (4 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 67
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{1,2,3,6}, {0,4,6}, {0,2,4,5,6}, {1,3,7}, {0,4,6,7}, {0,1,2,5,6,7}, {0,2,4,5,6,7}, {0,1,2,8}, {1,2,3,5,8}, {1,2,3,7,8}, {1,2,3,5,7,8}, {1,2,3,6,7,8}, {0,1,2,5,6,7,8}, {1,3,5,9}, {0,2,4,6,9}, {1,2,3,5,6,9}, {0,4,5,6,9}, {1,3,5,7,9}, {1,2,3,6,7,9}, {0,2,4,6,7,9}, {0,4,5,6,7,9}, {1,2,3,6,8,9}, {1,2,3,5,6,8,9}, {0,3,6,10}, {4,6,10}, {4,7,10}, {0,3,5,7,10}, {4,8,10}, {0,3,6,8,10}, {0,3,5,7,8,10}, {4,6,7,8,10}, {6,9,10}, {4,6,9,10}, {4,7,9,10}, {5,7,9,10}, {4,8,9,10}, {6,8,9,10}, {5,7,8,9,10}, {4,6,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 137; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,4}, {0,1,2,3,5}, {0,1,3,4,5,6}, {1,2,3,7}, {1,3,4,7}, {0,1,2,3,5,7}, {0,2,6,7}, {0,2,4,6,7}, {0,1,3,5,6,7}, {1,3,8}, {2,4,8}, {0,2,5,8}, {0,1,3,4,5,6,8}, {2,7,8}, {1,3,4,7,8}, {0,2,5,7,8}, {1,2,6,7,8}, {1,2,4,6,7,8}, {0,1,3,5,6,7,8}, {0,1,3,9}, {0,4,9}, {1,3,5,9}, {4,5,6,9}, {0,1,3,7,9}, {0,4,7,9}, {1,3,5,7,9}, {0,1,6,7,9}, {0,1,4,6,7,9}, {5,6,7,9}, {1,8,9}, {1,4,8,9}, {5,8,9}, {4,5,6,8,9}, {0,7,8,9}, {0,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

- rank 8 (`N = 12`), a3 = 75; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{3,4}, {1,3,5}, {1,3,6}, {1,3,5,6}, {0,1,3,4,7}, {2,5,7}, {2,6,7}, {2,5,6,7}, {1,2,3,8}, {0,2,6,8}, {1,3,4,6,8}, {1,2,6,7,8}, {0,3,4,6,7,8}, {0,4,9}, {0,2,3,7,9}, {1,4,7,9}, {1,2,3,8,9}, {2,3,6,8,9}, {0,1,4,6,8,9}, {0,1,2,3,6,7,8,9}, {4,6,7,8,9}, {1,2,3,5,10}, {1,2,3,6,10}, {1,2,3,5,6,10}, {7,10}, {5,7,10}, {6,7,10}, {5,6,7,10}, {1,2,3,8,10}, {1,2,3,9,10}, {1,2,3,8,9,10}, {11}, {8,11}, {9,11}, {8,9,11}, {10,11}, {8,10,11}, {9,10,11}, {8,9,10,11}]
  ```

### 31. `[[39,4,3]]` — T0·T1·CS01·CS23·CCZ023·CCZ123

- gate `0+1+01+23+023+123`, `N = 11` (4 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 67
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{0,1,3,6}, {1,2,3,4,6}, {1,3,4,5,6}, {0,1,2,3,7}, {1,2,3,4,6,7}, {0,1,2,5,6,7}, {1,3,4,5,6,7}, {0,1,2,8}, {0,1,3,5,8}, {0,1,3,7,8}, {0,1,3,5,7,8}, {0,1,3,6,7,8}, {0,1,2,5,6,7,8}, {0,1,2,3,5,9}, {1,3,4,6,9}, {0,1,3,5,6,9}, {1,2,3,4,5,6,9}, {0,1,2,3,5,7,9}, {0,1,3,6,7,9}, {1,3,4,6,7,9}, {1,2,3,4,5,6,7,9}, {0,1,3,6,8,9}, {0,1,3,5,6,8,9}, {2,3,6,10}, {4,6,10}, {4,7,10}, {2,3,5,7,10}, {4,8,10}, {2,3,6,8,10}, {2,3,5,7,8,10}, {4,6,7,8,10}, {6,9,10}, {4,6,9,10}, {4,7,9,10}, {5,7,9,10}, {4,8,9,10}, {6,8,9,10}, {5,7,8,9,10}, {4,6,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 137; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,4}, {0,2,5}, {0,4,5,6}, {0,1,3,7}, {0,1,2,3,4,7}, {0,2,5,7}, {1,3,6,7}, {1,3,4,6,7}, {0,5,6,7}, {0,1,2,3,8}, {2,4,8}, {1,3,5,8}, {0,4,5,6,8}, {2,7,8}, {0,1,2,3,4,7,8}, {1,3,5,7,8}, {0,3,6,7,8}, {0,3,4,6,7,8}, {0,5,6,7,8}, {0,9}, {1,2,3,4,9}, {0,1,2,3,5,9}, {4,5,6,9}, {0,7,9}, {1,2,3,4,7,9}, {0,1,2,3,5,7,9}, {0,1,6,7,9}, {0,1,4,6,7,9}, {5,6,7,9}, {0,2,3,8,9}, {0,2,3,4,8,9}, {5,8,9}, {4,5,6,8,9}, {1,2,3,7,8,9}, {1,2,3,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

- rank 8 (`N = 12`), a3 = 75; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{0,2,3,4}, {0,1,2,5}, {0,1,2,6}, {0,1,2,5,6}, {1,2,3,4,7}, {3,5,7}, {3,6,7}, {3,5,6,7}, {0,1,2,3,8}, {0,6,8}, {0,1,2,4,6,8}, {1,6,7,8}, {2,4,6,7,8}, {0,3,4,9}, {2,3,7,9}, {1,3,4,7,9}, {0,1,2,3,8,9}, {0,2,6,8,9}, {0,1,4,6,8,9}, {1,2,6,7,8,9}, {4,6,7,8,9}, {0,1,2,3,5,10}, {0,1,2,3,6,10}, {0,1,2,3,5,6,10}, {7,10}, {5,7,10}, {6,7,10}, {5,6,7,10}, {0,1,2,3,8,10}, {0,1,2,3,9,10}, {0,1,2,3,8,9,10}, {11}, {8,11}, {9,11}, {8,9,11}, {10,11}, {8,10,11}, {9,10,11}, {8,9,10,11}]
  ```

### 32. `[[39,4,3]]` — T0·T1·T2·CS01·CS02·CS03·CS12·CCZ012·CCZ013·CCZ023

- gate `0+1+2+01+02+03+12+012+013+023`, `N = 11` (4 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 67
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{1,2,3,6}, {0,2,4,6}, {0,2,3,4,5,6}, {1,2,7}, {0,2,4,6,7}, {0,1,2,3,5,6,7}, {0,2,3,4,5,6,7}, {0,1,2,3,8}, {1,2,3,5,8}, {1,2,3,7,8}, {1,2,3,5,7,8}, {1,2,3,6,7,8}, {0,1,2,3,5,6,7,8}, {1,2,5,9}, {0,2,3,4,6,9}, {1,2,3,5,6,9}, {0,2,4,5,6,9}, {1,2,5,7,9}, {1,2,3,6,7,9}, {0,2,3,4,6,7,9}, {0,2,4,5,6,7,9}, {1,2,3,6,8,9}, {1,2,3,5,6,8,9}, {0,6,10}, {4,6,10}, {4,7,10}, {0,5,7,10}, {4,8,10}, {0,6,8,10}, {0,5,7,8,10}, {4,6,7,8,10}, {6,9,10}, {4,6,9,10}, {4,7,9,10}, {5,7,9,10}, {4,8,9,10}, {6,8,9,10}, {5,7,8,9,10}, {4,6,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 137; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,3,4}, {0,1,3,5}, {0,1,4,5,6}, {1,2,3,7}, {1,2,4,7}, {0,1,3,5,7}, {0,2,3,6,7}, {0,2,3,4,6,7}, {0,1,5,6,7}, {1,2,8}, {3,4,8}, {0,2,3,5,8}, {0,1,4,5,6,8}, {3,7,8}, {1,2,4,7,8}, {0,2,3,5,7,8}, {1,3,6,7,8}, {1,3,4,6,7,8}, {0,1,5,6,7,8}, {0,1,9}, {0,2,4,9}, {1,2,5,9}, {4,5,6,9}, {0,1,7,9}, {0,2,4,7,9}, {1,2,5,7,9}, {0,1,2,6,7,9}, {0,1,2,4,6,7,9}, {5,6,7,9}, {1,8,9}, {1,4,8,9}, {5,8,9}, {4,5,6,8,9}, {0,2,7,8,9}, {0,2,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

- rank 8 (`N = 12`), a3 = 75; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{2,4}, {1,2,3,5}, {1,2,3,6}, {1,2,3,5,6}, {0,1,4,7}, {0,5,7}, {0,6,7}, {0,5,6,7}, {0,1,2,3,8}, {2,3,6,8}, {1,2,3,4,6,8}, {0,1,3,6,7,8}, {0,3,4,6,7,8}, {0,2,3,4,9}, {3,7,9}, {1,3,4,7,9}, {0,1,2,3,8,9}, {0,2,6,8,9}, {0,1,2,4,6,8,9}, {1,6,7,8,9}, {4,6,7,8,9}, {0,1,2,3,5,10}, {0,1,2,3,6,10}, {0,1,2,3,5,6,10}, {7,10}, {5,7,10}, {6,7,10}, {5,6,7,10}, {0,1,2,3,8,10}, {0,1,2,3,9,10}, {0,1,2,3,8,9,10}, {11}, {8,11}, {9,11}, {8,9,11}, {10,11}, {8,10,11}, {9,10,11}, {8,9,10,11}]
  ```

### 33. `[[39,4,3]]` — T0·T1·T2·CS01·CS02·CS03·CS12·CS13·CCZ012·CCZ013·CCZ023·CCZ123

- gate `0+1+2+01+02+03+12+13+012+013+023+123`, `N = 11` (4 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 67
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{2,3,6}, {1,3,4,6}, {0,3,4,5,6}, {0,1,2,3,7}, {1,3,4,6,7}, {2,5,6,7}, {0,3,4,5,6,7}, {2,8}, {2,3,5,8}, {2,3,7,8}, {2,3,5,7,8}, {2,3,6,7,8}, {2,5,6,7,8}, {0,1,2,3,5,9}, {0,3,4,6,9}, {2,3,5,6,9}, {1,3,4,5,6,9}, {0,1,2,3,5,7,9}, {2,3,6,7,9}, {0,3,4,6,7,9}, {1,3,4,5,6,7,9}, {2,3,6,8,9}, {2,3,5,6,8,9}, {3,6,10}, {4,6,10}, {4,7,10}, {3,5,7,10}, {4,8,10}, {3,6,8,10}, {3,5,7,8,10}, {4,6,7,8,10}, {6,9,10}, {4,6,9,10}, {4,7,9,10}, {5,7,9,10}, {4,8,9,10}, {6,8,9,10}, {5,7,8,9,10}, {4,6,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 137; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,3,4}, {0,2,3,5}, {0,2,4,5,6}, {2,7}, {2,3,4,7}, {0,2,3,5,7}, {0,6,7}, {0,4,6,7}, {0,2,5,6,7}, {2,3,8}, {3,4,8}, {0,5,8}, {0,2,4,5,6,8}, {3,7,8}, {2,3,4,7,8}, {0,5,7,8}, {1,2,6,7,8}, {1,2,4,6,7,8}, {0,2,5,6,7,8}, {0,2,9}, {0,3,4,9}, {2,3,5,9}, {4,5,6,9}, {0,2,7,9}, {0,3,4,7,9}, {2,3,5,7,9}, {0,1,2,6,7,9}, {0,1,2,4,6,7,9}, {5,6,7,9}, {1,2,3,8,9}, {1,2,3,4,8,9}, {5,8,9}, {4,5,6,8,9}, {0,3,7,8,9}, {0,3,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

- rank 8 (`N = 12`), a3 = 75; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{1,4}, {2,3,5}, {2,3,6}, {2,3,5,6}, {0,2,4,7}, {3,5,7}, {3,6,7}, {3,5,6,7}, {2,8}, {0,6,8}, {2,3,4,6,8}, {1,2,6,7,8}, {0,1,3,4,6,7,8}, {0,3,4,9}, {0,1,7,9}, {1,2,3,4,7,9}, {2,8,9}, {1,3,6,8,9}, {0,1,2,4,6,8,9}, {0,2,3,6,7,8,9}, {4,6,7,8,9}, {2,5,10}, {2,6,10}, {2,5,6,10}, {7,10}, {5,7,10}, {6,7,10}, {5,6,7,10}, {2,8,10}, {2,9,10}, {2,8,9,10}, {11}, {8,11}, {9,11}, {8,9,11}, {10,11}, {8,10,11}, {9,10,11}, {8,9,10,11}]
  ```

### 34. `[[39,4,3]]` — T0·T1·T2·CS01·CS02·CS03·CS12·CS13·CS23·CCZ012·CCZ013·CCZ023·CCZ123

- gate `0+1+2+01+02+03+12+13+23+012+013+023+123`, `N = 11` (4 outputs + 7 checks), T-count 2, reduced degree 1, a3 = 69
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,3,4}, {0,1,2,3,5}, {0,1,2,3,4,5}, {0,1,2,3,6}, {0,1,2,3,4,6}, {0,1,2,3,4,5,6}, {7}, {0,1,3,4,7}, {2,3,4,5,6,7}, {8}, {0,2,3,5,8}, {1,3,6,8}, {7,8}, {1,2,3,4,5,7,8}, {0,3,4,6,7,8}, {0,1,2,5,6,9}, {7,9}, {0,1,4,7,9}, {2,4,5,6,7,9}, {8,9}, {0,2,5,8,9}, {1,6,8,9}, {7,8,9}, {1,2,4,5,7,8,9}, {0,4,6,7,8,9}, {4,10}, {4,7,10}, {4,8,10}, {4,7,8,10}, {9,10}, {5,9,10}, {4,5,9,10}, {6,9,10}, {4,6,9,10}, {5,6,9,10}, {4,5,6,9,10}, {4,7,9,10}, {4,8,9,10}, {4,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 113; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{4}, {1,3,5}, {1,2,4,5,6}, {2,3,7}, {0,1,2,4,7}, {1,2,5,7}, {0,3,6,7}, {0,3,4,6,7}, {1,2,5,6,7}, {0,1,2,3,8}, {4,8}, {1,5,8}, {1,2,4,5,6,8}, {2,7,8}, {0,1,2,4,7,8}, {1,2,3,5,7,8}, {0,3,6,7,8}, {0,3,4,6,7,8}, {1,2,5,6,7,8}, {1,2,9}, {0,3,4,9}, {2,5,9}, {4,5,6,9}, {1,7,9}, {0,4,7,9}, {3,5,7,9}, {6,7,9}, {4,6,7,9}, {5,6,7,9}, {1,2,3,8,9}, {0,3,4,8,9}, {2,3,5,8,9}, {4,5,6,8,9}, {1,3,7,8,9}, {0,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

### 35. `[[39,4,3]]` — T0·T1·T2·CS01·CS23

- gate `0+1+2+01+23`, `N = 11` (4 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 67
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{3,6}, {1,2,4,6}, {0,2,3,4,5,6}, {0,1,7}, {1,2,4,6,7}, {2,3,5,6,7}, {0,2,3,4,5,6,7}, {2,3,8}, {3,5,8}, {3,7,8}, {3,5,7,8}, {3,6,7,8}, {2,3,5,6,7,8}, {0,1,5,9}, {0,2,3,4,6,9}, {3,5,6,9}, {1,2,4,5,6,9}, {0,1,5,7,9}, {3,6,7,9}, {0,2,3,4,6,7,9}, {1,2,4,5,6,7,9}, {3,6,8,9}, {3,5,6,8,9}, {2,6,10}, {4,6,10}, {4,7,10}, {2,5,7,10}, {4,8,10}, {2,6,8,10}, {2,5,7,8,10}, {4,6,7,8,10}, {6,9,10}, {4,6,9,10}, {4,7,9,10}, {5,7,9,10}, {4,8,9,10}, {6,8,9,10}, {5,7,8,9,10}, {4,6,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 137; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,4}, {0,5}, {0,2,4,5,6}, {3,7}, {2,3,4,7}, {0,5,7}, {0,2,3,6,7}, {0,2,3,4,6,7}, {0,2,5,6,7}, {2,3,8}, {2,4,8}, {0,2,3,5,8}, {0,2,4,5,6,8}, {2,7,8}, {2,3,4,7,8}, {0,2,3,5,7,8}, {1,3,6,7,8}, {1,3,4,6,7,8}, {0,2,5,6,7,8}, {0,2,9}, {0,3,4,9}, {2,3,5,9}, {4,5,6,9}, {0,2,7,9}, {0,3,4,7,9}, {2,3,5,7,9}, {0,1,2,6,7,9}, {0,1,2,4,6,7,9}, {5,6,7,9}, {1,2,3,8,9}, {1,2,3,4,8,9}, {5,8,9}, {4,5,6,8,9}, {0,3,7,8,9}, {0,3,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

- rank 8 (`N = 12`), a3 = 75; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{1,2,4}, {2,3,5}, {2,3,6}, {2,3,5,6}, {0,4,7}, {2,5,7}, {2,6,7}, {2,5,6,7}, {3,8}, {0,3,6,8}, {2,3,4,6,8}, {1,2,3,6,7,8}, {0,1,3,4,6,7,8}, {0,2,3,4,9}, {0,1,2,3,7,9}, {1,3,4,7,9}, {3,8,9}, {1,6,8,9}, {0,1,2,4,6,8,9}, {0,2,6,7,8,9}, {4,6,7,8,9}, {3,5,10}, {3,6,10}, {3,5,6,10}, {7,10}, {5,7,10}, {6,7,10}, {5,6,7,10}, {3,8,10}, {3,9,10}, {3,8,9,10}, {11}, {8,11}, {9,11}, {8,9,11}, {10,11}, {8,10,11}, {9,10,11}, {8,9,10,11}]
  ```

### 36. `[[39,4,3]]` — T0·T1·T2·T3·CS01

- gate `0+1+2+3+01`, `N = 11` (4 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 67
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{0,1,6}, {0,2,4,6}, {1,2,3,4,5,6}, {3,7}, {0,2,4,6,7}, {2,5,6,7}, {1,2,3,4,5,6,7}, {2,8}, {0,1,5,8}, {0,1,7,8}, {0,1,5,7,8}, {0,1,6,7,8}, {2,5,6,7,8}, {3,5,9}, {1,2,3,4,6,9}, {0,1,5,6,9}, {0,2,4,5,6,9}, {3,5,7,9}, {0,1,6,7,9}, {1,2,3,4,6,7,9}, {0,2,4,5,6,7,9}, {0,1,6,8,9}, {0,1,5,6,8,9}, {0,1,2,6,10}, {4,6,10}, {4,7,10}, {0,1,2,5,7,10}, {4,8,10}, {0,1,2,6,8,10}, {0,1,2,5,7,8,10}, {4,6,7,8,10}, {6,9,10}, {4,6,9,10}, {4,7,9,10}, {5,7,9,10}, {4,8,9,10}, {6,8,9,10}, {5,7,8,9,10}, {4,6,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 137; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,4}, {0,5}, {0,2,3,4,5,6}, {3,7}, {2,4,7}, {0,5,7}, {0,2,6,7}, {0,2,4,6,7}, {0,2,3,5,6,7}, {2,8}, {2,3,4,8}, {0,2,5,8}, {0,2,3,4,5,6,8}, {2,3,7,8}, {2,4,7,8}, {0,2,5,7,8}, {1,3,6,7,8}, {1,3,4,6,7,8}, {0,2,3,5,6,7,8}, {0,2,3,9}, {0,3,4,9}, {2,5,9}, {4,5,6,9}, {0,2,3,7,9}, {0,3,4,7,9}, {2,5,7,9}, {0,1,2,3,6,7,9}, {0,1,2,3,4,6,7,9}, {5,6,7,9}, {1,2,8,9}, {1,2,4,8,9}, {5,8,9}, {4,5,6,8,9}, {0,3,7,8,9}, {0,3,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

- rank 8 (`N = 12`), a3 = 75; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{1,2,4}, {3,5}, {3,6}, {3,5,6}, {0,3,4,7}, {2,3,5,7}, {2,3,6,7}, {2,3,5,6,7}, {2,8}, {0,2,3,6,8}, {3,4,6,8}, {1,6,7,8}, {0,1,2,4,6,7,8}, {0,4,9}, {0,1,3,7,9}, {1,2,3,4,7,9}, {2,8,9}, {1,3,6,8,9}, {0,1,2,3,4,6,8,9}, {0,2,6,7,8,9}, {4,6,7,8,9}, {2,5,10}, {2,6,10}, {2,5,6,10}, {7,10}, {5,7,10}, {6,7,10}, {5,6,7,10}, {2,8,10}, {2,9,10}, {2,8,9,10}, {11}, {8,11}, {9,11}, {8,9,11}, {10,11}, {8,10,11}, {9,10,11}, {8,9,10,11}]
  ```

### 37. `[[39,4,3]]` — T0·T1·T2·T3·CS01·CS02·CS03

- gate `0+1+2+3+01+02+03`, `N = 11` (4 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 67
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{0,3,6}, {1,4,6}, {1,2,3,4,5,6}, {0,2,7}, {1,4,6,7}, {0,1,5,6,7}, {1,2,3,4,5,6,7}, {0,1,8}, {0,3,5,8}, {0,3,7,8}, {0,3,5,7,8}, {0,3,6,7,8}, {0,1,5,6,7,8}, {0,2,5,9}, {1,2,3,4,6,9}, {0,3,5,6,9}, {1,4,5,6,9}, {0,2,5,7,9}, {0,3,6,7,9}, {1,2,3,4,6,7,9}, {1,4,5,6,7,9}, {0,3,6,8,9}, {0,3,5,6,8,9}, {1,3,6,10}, {4,6,10}, {4,7,10}, {1,3,5,7,10}, {4,8,10}, {1,3,6,8,10}, {1,3,5,7,8,10}, {4,6,7,8,10}, {6,9,10}, {4,6,9,10}, {4,7,9,10}, {5,7,9,10}, {4,8,9,10}, {6,8,9,10}, {5,7,8,9,10}, {4,6,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 137; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,3,4}, {0,5}, {0,1,2,4,5,6}, {0,2,7}, {0,1,4,7}, {0,5,7}, {1,6,7}, {1,4,6,7}, {0,1,2,5,6,7}, {0,1,8}, {1,2,4,8}, {1,5,8}, {0,1,2,4,5,6,8}, {1,2,7,8}, {0,1,4,7,8}, {1,5,7,8}, {0,2,3,6,7,8}, {0,2,3,4,6,7,8}, {0,1,2,5,6,7,8}, {0,1,2,9}, {2,4,9}, {0,1,5,9}, {4,5,6,9}, {0,1,2,7,9}, {2,4,7,9}, {0,1,5,7,9}, {0,1,2,3,6,7,9}, {0,1,2,3,4,6,7,9}, {5,6,7,9}, {0,1,3,8,9}, {0,1,3,4,8,9}, {5,8,9}, {4,5,6,8,9}, {2,7,8,9}, {2,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

- rank 8 (`N = 12`), a3 = 75; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{3,4}, {0,2,5}, {0,2,6}, {0,2,5,6}, {0,1,2,4,7}, {1,2,5,7}, {1,2,6,7}, {1,2,5,6,7}, {0,1,8}, {2,6,8}, {0,2,4,6,8}, {0,1,3,6,7,8}, {1,3,4,6,7,8}, {1,4,9}, {2,3,7,9}, {0,2,3,4,7,9}, {0,1,8,9}, {1,2,3,6,8,9}, {0,1,2,3,4,6,8,9}, {0,6,7,8,9}, {4,6,7,8,9}, {0,1,5,10}, {0,1,6,10}, {0,1,5,6,10}, {7,10}, {5,7,10}, {6,7,10}, {5,6,7,10}, {0,1,8,10}, {0,1,9,10}, {0,1,8,9,10}, {11}, {8,11}, {9,11}, {8,9,11}, {10,11}, {8,10,11}, {9,10,11}, {8,9,10,11}]
  ```

### 38. `[[39,4,3]]` — T0·T1·T2·T3·CS01·CS02·CS03·CS12·CCZ012

- gate `0+1+2+3+01+02+03+12+012`, `N = 11` (4 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 67
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{0,3,6}, {1,3,4,6}, {1,4,5,6}, {0,7}, {1,3,4,6,7}, {0,1,2,5,6,7}, {1,4,5,6,7}, {0,1,2,8}, {0,3,5,8}, {0,3,7,8}, {0,3,5,7,8}, {0,3,6,7,8}, {0,1,2,5,6,7,8}, {0,5,9}, {1,4,6,9}, {0,3,5,6,9}, {1,3,4,5,6,9}, {0,5,7,9}, {0,3,6,7,9}, {1,4,6,7,9}, {1,3,4,5,6,7,9}, {0,3,6,8,9}, {0,3,5,6,8,9}, {1,2,3,6,10}, {4,6,10}, {4,7,10}, {1,2,3,5,7,10}, {4,8,10}, {1,2,3,6,8,10}, {1,2,3,5,7,8,10}, {4,6,7,8,10}, {6,9,10}, {4,6,9,10}, {4,7,9,10}, {5,7,9,10}, {4,8,9,10}, {6,8,9,10}, {5,7,8,9,10}, {4,6,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 137; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,3,4}, {0,2,3,5}, {0,1,3,4,5,6}, {0,7}, {0,1,2,4,7}, {0,2,3,5,7}, {1,3,6,7}, {1,3,4,6,7}, {0,1,3,5,6,7}, {0,1,2,8}, {1,2,4,8}, {1,3,5,8}, {0,1,3,4,5,6,8}, {1,2,7,8}, {0,1,2,4,7,8}, {1,3,5,7,8}, {0,2,6,7,8}, {0,2,4,6,7,8}, {0,1,3,5,6,7,8}, {0,1,3,9}, {2,3,4,9}, {0,1,2,5,9}, {4,5,6,9}, {0,1,3,7,9}, {2,3,4,7,9}, {0,1,2,5,7,9}, {0,1,2,3,6,7,9}, {0,1,2,3,4,6,7,9}, {5,6,7,9}, {0,1,8,9}, {0,1,4,8,9}, {5,8,9}, {4,5,6,8,9}, {2,3,7,8,9}, {2,3,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

- rank 8 (`N = 12`), a3 = 75; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{0,2,3,4}, {0,5}, {0,6}, {0,5,6}, {1,4,7}, {3,5,7}, {3,6,7}, {3,5,6,7}, {0,3,8}, {0,1,3,6,8}, {0,4,6,8}, {2,6,7,8}, {1,2,3,4,6,7,8}, {0,1,4,9}, {1,2,7,9}, {2,3,4,7,9}, {0,3,8,9}, {0,2,6,8,9}, {0,1,2,3,4,6,8,9}, {1,3,6,7,8,9}, {4,6,7,8,9}, {0,3,5,10}, {0,3,6,10}, {0,3,5,6,10}, {7,10}, {5,7,10}, {6,7,10}, {5,6,7,10}, {0,3,8,10}, {0,3,9,10}, {0,3,8,9,10}, {11}, {8,11}, {9,11}, {8,9,11}, {10,11}, {8,10,11}, {9,10,11}, {8,9,10,11}]
  ```

### 39. `[[39,4,3]]` — T0·T1·T2·T3·CS01·CS02·CS03·CS12·CS13·CCZ012·CCZ013

- gate `0+1+2+3+01+02+03+12+13+012+013`, `N = 11` (4 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 67
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{0,1,6}, {0,4,6}, {0,2,4,5,6}, {0,1,2,7}, {0,4,6,7}, {0,1,3,5,6,7}, {0,2,4,5,6,7}, {0,1,3,8}, {0,1,5,8}, {0,1,7,8}, {0,1,5,7,8}, {0,1,6,7,8}, {0,1,3,5,6,7,8}, {0,1,2,5,9}, {0,2,4,6,9}, {0,1,5,6,9}, {0,4,5,6,9}, {0,1,2,5,7,9}, {0,1,6,7,9}, {0,2,4,6,7,9}, {0,4,5,6,7,9}, {0,1,6,8,9}, {0,1,5,6,8,9}, {3,6,10}, {4,6,10}, {4,7,10}, {3,5,7,10}, {4,8,10}, {3,6,8,10}, {3,5,7,8,10}, {4,6,7,8,10}, {6,9,10}, {4,6,9,10}, {4,7,9,10}, {5,7,9,10}, {4,8,9,10}, {6,8,9,10}, {5,7,8,9,10}, {4,6,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 137; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,3,4}, {0,5}, {0,2,4,5,6}, {0,1,7}, {0,1,2,4,7}, {0,5,7}, {1,2,6,7}, {1,2,4,6,7}, {0,2,5,6,7}, {0,1,2,8}, {2,4,8}, {1,2,5,8}, {0,2,4,5,6,8}, {2,7,8}, {0,1,2,4,7,8}, {1,2,5,7,8}, {0,3,6,7,8}, {0,3,4,6,7,8}, {0,2,5,6,7,8}, {0,2,9}, {1,4,9}, {0,1,2,5,9}, {4,5,6,9}, {0,2,7,9}, {1,4,7,9}, {0,1,2,5,7,9}, {0,1,2,3,6,7,9}, {0,1,2,3,4,6,7,9}, {5,6,7,9}, {0,2,3,8,9}, {0,2,3,4,8,9}, {5,8,9}, {4,5,6,8,9}, {1,7,8,9}, {1,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

- rank 8 (`N = 12`), a3 = 75; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{0,2,3,4}, {0,1,2,5}, {0,1,2,6}, {0,1,2,5,6}, {1,4,7}, {2,5,7}, {2,6,7}, {2,5,6,7}, {0,1,8}, {0,6,8}, {0,1,2,4,6,8}, {1,2,3,6,7,8}, {3,4,6,7,8}, {0,2,4,9}, {2,3,7,9}, {1,3,4,7,9}, {0,1,8,9}, {0,3,6,8,9}, {0,1,2,3,4,6,8,9}, {1,2,6,7,8,9}, {4,6,7,8,9}, {0,1,5,10}, {0,1,6,10}, {0,1,5,6,10}, {7,10}, {5,7,10}, {6,7,10}, {5,6,7,10}, {0,1,8,10}, {0,1,9,10}, {0,1,8,9,10}, {11}, {8,11}, {9,11}, {8,9,11}, {10,11}, {8,10,11}, {9,10,11}, {8,9,10,11}]
  ```

### 40. `[[39,4,3]]` — T0·T1·T2·T3·CS01·CS02·CS03·CS12·CS13·CS23·CCZ012·CCZ013·CCZ023·CCZ123

- gate `0+1+2+3+01+02+03+12+13+23+012+013+023+123`, `N = 12` (4 outputs + 8 checks), T-count 1, reduced degree 1, a3 = 39
- source: length40_m8_discovery_005, origin 141; rep_length40_m8_discovery_005.json

```text
[{2,5}, {0,2,3,4,5}, {0,1,2,3,6}, {2,5,6}, {0,2,3,4,5,6}, {4,6,7}, {3,4,8}, {3,4,6,8}, {4,6,7,8}, {0,1,4,9}, {0,1,4,6,9}, {4,6,7,9}, {0,2,3,4,8,9}, {0,2,3,4,6,8,9}, {4,6,7,8,9}, {1,10}, {0,3,5,10}, {4,5,10}, {1,6,10}, {0,3,5,6,10}, {4,5,6,10}, {4,6,7,10}, {0,2,4,8,10}, {0,2,4,6,8,10}, {4,6,7,8,10}, {1,2,3,4,9,10}, {1,2,3,4,6,9,10}, {4,6,7,9,10}, {4,8,9,10}, {4,6,8,9,10}, {4,6,7,8,9,10}, {4,6,7,11}, {4,6,7,8,11}, {4,6,7,9,11}, {4,6,7,8,9,11}, {4,6,7,10,11}, {4,6,7,8,10,11}, {4,6,7,9,10,11}, {4,6,7,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 95; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{4}, {0,2,3,5}, {2,3,4,5,6}, {0,7}, {0,1,2,3,4,7}, {2,3,5,7}, {0,1,6,7}, {0,1,4,6,7}, {2,3,5,6,7}, {1,2,8}, {1,2,4,8}, {1,5,8}, {2,3,4,5,6,8}, {1,2,3,7,8}, {0,1,2,3,4,7,8}, {0,1,5,7,8}, {0,2,6,7,8}, {0,2,4,6,7,8}, {2,3,5,6,7,8}, {0,2,9}, {0,2,4,9}, {1,2,3,5,9}, {4,5,6,9}, {1,7,9}, {0,1,4,7,9}, {0,1,2,3,5,7,9}, {1,2,6,7,9}, {1,2,4,6,7,9}, {5,6,7,9}, {2,3,8,9}, {0,1,4,8,9}, {0,5,8,9}, {4,5,6,8,9}, {0,2,3,7,8,9}, {0,1,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

- rank 7 (`N = 11`), a3 = 47; length40_m7_001, origin 65; rep_length40_m7_001.json

  ```text
  [{0,1,2,3,5}, {1,4,5}, {2,4,6}, {0,1,4,7}, {1,4,6,7}, {1,8}, {1,5,8}, {0,1,2,3,4,5,8}, {2,4,6,8}, {0,1,4,7,8}, {0,1,2,3,4,6,7,8}, {9}, {5,9}, {0,2,3,4,5,9}, {2,4,6,9}, {0,1,4,7,9}, {0,2,3,4,6,7,9}, {0,2,3,8,9}, {0,2,3,5,8,9}, {4,5,8,9}, {2,4,6,8,9}, {0,1,4,7,8,9}, {4,6,7,8,9}, {0,1,2,4,10}, {1,4,6,10}, {1,4,7,10}, {4,6,7,10}, {0,1,2,4,8,10}, {0,1,2,3,4,6,8,10}, {0,1,2,3,4,7,8,10}, {4,6,7,8,10}, {0,1,2,4,9,10}, {0,2,3,4,6,9,10}, {0,2,3,4,7,9,10}, {4,6,7,9,10}, {0,1,2,4,8,9,10}, {4,6,8,9,10}, {4,7,8,9,10}, {4,6,7,8,9,10}]
  ```

### 41. `[[39,4,3]]` — T0·T1·T2·T3·CS01·CS02·CS12·CCZ012

- gate `0+1+2+3+01+02+12+012`, `N = 11` (4 outputs + 7 checks), T-count 2, reduced degree 1, a3 = 69
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{3,4}, {3,5}, {3,4,5}, {3,6}, {3,4,6}, {3,4,5,6}, {7}, {2,3,4,7}, {0,1,4,5,6,7}, {8}, {1,2,5,8}, {0,3,6,8}, {7,8}, {0,2,3,4,5,7,8}, {1,4,6,7,8}, {0,1,2,3,5,6,9}, {7,9}, {0,1,3,4,7,9}, {2,4,5,6,7,9}, {8,9}, {0,5,8,9}, {1,2,3,6,8,9}, {7,8,9}, {1,3,4,5,7,8,9}, {0,2,4,6,7,8,9}, {4,10}, {4,7,10}, {4,8,10}, {4,7,8,10}, {9,10}, {5,9,10}, {4,5,9,10}, {6,9,10}, {4,6,9,10}, {5,6,9,10}, {4,5,6,9,10}, {4,7,9,10}, {4,8,9,10}, {4,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 113; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{4}, {0,5}, {0,2,3,4,5,6}, {2,3,7}, {0,1,2,3,4,7}, {0,2,3,5,7}, {1,3,6,7}, {1,3,4,6,7}, {0,2,3,5,6,7}, {0,1,2,8}, {4,8}, {0,3,5,8}, {0,2,3,4,5,6,8}, {2,7,8}, {0,1,2,3,4,7,8}, {0,2,5,7,8}, {1,3,6,7,8}, {1,3,4,6,7,8}, {0,2,3,5,6,7,8}, {0,2,3,9}, {1,3,4,9}, {2,5,9}, {4,5,6,9}, {0,3,7,9}, {1,4,7,9}, {3,5,7,9}, {6,7,9}, {4,6,7,9}, {5,6,7,9}, {0,2,8,9}, {1,3,4,8,9}, {2,3,5,8,9}, {4,5,6,8,9}, {0,7,8,9}, {1,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

### 42. `[[39,4,3]]` — T0·T1·T2·T3·CS01·CS23

- gate `0+1+2+3+01+23`, `N = 11` (4 outputs + 7 checks), T-count 2, reduced degree 1, a3 = 69
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,4}, {0,1,5}, {0,1,4,5}, {0,1,6}, {0,1,4,6}, {0,1,4,5,6}, {7}, {0,1,3,4,7}, {2,4,5,6,7}, {8}, {0,5,8}, {1,2,3,6,8}, {7,8}, {1,2,4,5,7,8}, {0,3,4,6,7,8}, {0,1,2,3,5,6,9}, {7,9}, {0,1,2,4,7,9}, {3,4,5,6,7,9}, {8,9}, {0,2,3,5,8,9}, {1,6,8,9}, {7,8,9}, {1,3,4,5,7,8,9}, {0,2,4,6,7,8,9}, {4,10}, {4,7,10}, {4,8,10}, {4,7,8,10}, {9,10}, {5,9,10}, {4,5,9,10}, {6,9,10}, {4,6,9,10}, {5,6,9,10}, {4,5,6,9,10}, {4,7,9,10}, {4,8,9,10}, {4,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 113; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{4}, {0,5}, {1,3,4,5,6}, {0,1,3,7}, {0,1,2,3,4,7}, {1,3,5,7}, {1,2,6,7}, {1,2,4,6,7}, {1,3,5,6,7}, {2,3,8}, {4,8}, {1,5,8}, {1,3,4,5,6,8}, {3,7,8}, {0,1,2,3,4,7,8}, {0,3,5,7,8}, {1,2,6,7,8}, {1,2,4,6,7,8}, {1,3,5,6,7,8}, {1,3,9}, {1,2,4,9}, {3,5,9}, {4,5,6,9}, {1,7,9}, {0,2,4,7,9}, {0,1,5,7,9}, {6,7,9}, {4,6,7,9}, {5,6,7,9}, {0,3,8,9}, {1,2,4,8,9}, {0,1,3,5,8,9}, {4,5,6,8,9}, {0,7,8,9}, {0,2,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

### 43. `[[39,4,3]]` — T0·T1·T3·CS01·CS02·CS12·CCZ012

- gate `0+1+3+01+02+12+012`, `N = 11` (4 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 67
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{0,1,2,6}, {0,4,6}, {1,2,3,4,5,6}, {3,7}, {0,4,6,7}, {2,5,6,7}, {1,2,3,4,5,6,7}, {2,8}, {0,1,2,5,8}, {0,1,2,7,8}, {0,1,2,5,7,8}, {0,1,2,6,7,8}, {2,5,6,7,8}, {3,5,9}, {1,2,3,4,6,9}, {0,1,2,5,6,9}, {0,4,5,6,9}, {3,5,7,9}, {0,1,2,6,7,9}, {1,2,3,4,6,7,9}, {0,4,5,6,7,9}, {0,1,2,6,8,9}, {0,1,2,5,6,8,9}, {0,1,6,10}, {4,6,10}, {4,7,10}, {0,1,5,7,10}, {4,8,10}, {0,1,6,8,10}, {0,1,5,7,8,10}, {4,6,7,8,10}, {6,9,10}, {4,6,9,10}, {4,7,9,10}, {5,7,9,10}, {4,8,9,10}, {6,8,9,10}, {5,7,8,9,10}, {4,6,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 137; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,4}, {0,2,5}, {0,3,4,5,6}, {3,7}, {2,4,7}, {0,2,5,7}, {0,6,7}, {0,4,6,7}, {0,3,5,6,7}, {2,8}, {2,3,4,8}, {0,5,8}, {0,3,4,5,6,8}, {2,3,7,8}, {2,4,7,8}, {0,5,7,8}, {1,3,6,7,8}, {1,3,4,6,7,8}, {0,3,5,6,7,8}, {0,3,9}, {0,2,3,4,9}, {2,5,9}, {4,5,6,9}, {0,3,7,9}, {0,2,3,4,7,9}, {2,5,7,9}, {0,1,3,6,7,9}, {0,1,3,4,6,7,9}, {5,6,7,9}, {1,2,8,9}, {1,2,4,8,9}, {5,8,9}, {4,5,6,8,9}, {0,2,3,7,8,9}, {0,2,3,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

- rank 8 (`N = 12`), a3 = 75; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{1,4}, {3,5}, {3,6}, {3,5,6}, {0,3,4,7}, {2,3,5,7}, {2,3,6,7}, {2,3,5,6,7}, {2,8}, {0,2,3,6,8}, {3,4,6,8}, {1,2,6,7,8}, {0,1,4,6,7,8}, {0,4,9}, {0,1,2,3,7,9}, {1,3,4,7,9}, {2,8,9}, {1,2,3,6,8,9}, {0,1,3,4,6,8,9}, {0,2,6,7,8,9}, {4,6,7,8,9}, {2,5,10}, {2,6,10}, {2,5,6,10}, {7,10}, {5,7,10}, {6,7,10}, {5,6,7,10}, {2,8,10}, {2,9,10}, {2,8,9,10}, {11}, {8,11}, {9,11}, {8,9,11}, {10,11}, {8,10,11}, {9,10,11}, {8,9,10,11}]
  ```

### 44. `[[39,4,3]]` — T0·T1·T3·CS01·CS02·CS12·CS23·CCZ012

- gate `0+1+3+01+02+12+23+012`, `N = 11` (4 outputs + 7 checks), T-count 2, reduced degree 1, a3 = 69
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,4}, {0,1,2,5}, {0,1,2,4,5}, {0,1,2,6}, {0,1,2,4,6}, {0,1,2,4,5,6}, {7}, {0,2,4,7}, {1,2,3,4,5,6,7}, {8}, {0,1,5,8}, {3,6,8}, {7,8}, {1,3,4,5,7,8}, {0,4,6,7,8}, {0,1,3,5,6,9}, {7,9}, {0,3,4,7,9}, {1,4,5,6,7,9}, {8,9}, {0,1,2,3,5,8,9}, {2,6,8,9}, {7,8,9}, {1,2,4,5,7,8,9}, {0,2,3,4,6,7,8,9}, {4,10}, {4,7,10}, {4,8,10}, {4,7,8,10}, {9,10}, {5,9,10}, {4,5,9,10}, {6,9,10}, {4,6,9,10}, {5,6,9,10}, {4,5,6,9,10}, {4,7,9,10}, {4,8,9,10}, {4,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 113; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{4}, {3,5}, {1,2,4,5,6}, {1,2,3,7}, {0,1,3,4,7}, {1,2,5,7}, {0,6,7}, {0,4,6,7}, {1,2,5,6,7}, {0,1,2,8}, {4,8}, {2,5,8}, {1,2,4,5,6,8}, {1,7,8}, {0,1,3,4,7,8}, {1,3,5,7,8}, {0,6,7,8}, {0,4,6,7,8}, {1,2,5,6,7,8}, {1,2,9}, {0,4,9}, {1,5,9}, {4,5,6,9}, {2,7,9}, {0,2,3,4,7,9}, {2,3,5,7,9}, {6,7,9}, {4,6,7,9}, {5,6,7,9}, {1,3,8,9}, {0,4,8,9}, {1,2,3,5,8,9}, {4,5,6,8,9}, {3,7,8,9}, {0,2,3,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

### 45. `[[39,4,3]]` — T0·T1·T3·CS01·CS02·CS13·CCZ012

- gate `0+1+3+01+02+13+012`, `N = 11` (4 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 67
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{0,1,2,6}, {1,4,6}, {0,1,2,3,4,5,6}, {1,3,7}, {1,4,6,7}, {1,2,5,6,7}, {0,1,2,3,4,5,6,7}, {1,2,8}, {0,1,2,5,8}, {0,1,2,7,8}, {0,1,2,5,7,8}, {0,1,2,6,7,8}, {1,2,5,6,7,8}, {1,3,5,9}, {0,1,2,3,4,6,9}, {0,1,2,5,6,9}, {1,4,5,6,9}, {1,3,5,7,9}, {0,1,2,6,7,9}, {0,1,2,3,4,6,7,9}, {1,4,5,6,7,9}, {0,1,2,6,8,9}, {0,1,2,5,6,8,9}, {0,6,10}, {4,6,10}, {4,7,10}, {0,5,7,10}, {4,8,10}, {0,6,8,10}, {0,5,7,8,10}, {4,6,7,8,10}, {6,9,10}, {4,6,9,10}, {4,7,9,10}, {5,7,9,10}, {4,8,9,10}, {6,8,9,10}, {5,7,8,9,10}, {4,6,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 137; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,4}, {1,5}, {1,2,3,4,5,6}, {1,3,7}, {1,2,4,7}, {1,5,7}, {2,6,7}, {2,4,6,7}, {1,2,3,5,6,7}, {1,2,8}, {2,3,4,8}, {2,5,8}, {1,2,3,4,5,6,8}, {2,3,7,8}, {1,2,4,7,8}, {2,5,7,8}, {0,1,2,3,6,7,8}, {0,1,2,3,4,6,7,8}, {1,2,3,5,6,7,8}, {1,2,3,9}, {3,4,9}, {1,2,5,9}, {4,5,6,9}, {1,2,3,7,9}, {3,4,7,9}, {1,2,5,7,9}, {0,1,3,6,7,9}, {0,1,3,4,6,7,9}, {5,6,7,9}, {0,1,8,9}, {0,1,4,8,9}, {5,8,9}, {4,5,6,8,9}, {3,7,8,9}, {3,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

- rank 8 (`N = 12`), a3 = 75; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{0,1,4}, {1,3,5}, {1,3,6}, {1,3,5,6}, {3,4,7}, {2,3,5,7}, {2,3,6,7}, {2,3,5,6,7}, {1,2,8}, {1,2,3,6,8}, {1,3,4,6,8}, {0,2,6,7,8}, {0,4,6,7,8}, {1,4,9}, {0,2,3,7,9}, {0,3,4,7,9}, {1,2,8,9}, {0,1,2,3,6,8,9}, {0,1,3,4,6,8,9}, {2,6,7,8,9}, {4,6,7,8,9}, {1,2,5,10}, {1,2,6,10}, {1,2,5,6,10}, {7,10}, {5,7,10}, {6,7,10}, {5,6,7,10}, {1,2,8,10}, {1,2,9,10}, {1,2,8,9,10}, {11}, {8,11}, {9,11}, {8,9,11}, {10,11}, {8,10,11}, {9,10,11}, {8,9,10,11}]
  ```

### 46. `[[39,4,3]]` — T0·T1·T3·CS01·CS02·CS13·CS23·CCZ012·CCZ123

- gate `0+1+3+01+02+13+23+012+123`, `N = 11` (4 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 67
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{0,1,2,6}, {0,4,6}, {3,4,5,6}, {1,2,3,7}, {0,4,6,7}, {1,5,6,7}, {3,4,5,6,7}, {1,8}, {0,1,2,5,8}, {0,1,2,7,8}, {0,1,2,5,7,8}, {0,1,2,6,7,8}, {1,5,6,7,8}, {1,2,3,5,9}, {3,4,6,9}, {0,1,2,5,6,9}, {0,4,5,6,9}, {1,2,3,5,7,9}, {0,1,2,6,7,9}, {3,4,6,7,9}, {0,4,5,6,7,9}, {0,1,2,6,8,9}, {0,1,2,5,6,8,9}, {0,2,6,10}, {4,6,10}, {4,7,10}, {0,2,5,7,10}, {4,8,10}, {0,2,6,8,10}, {0,2,5,7,8,10}, {4,6,7,8,10}, {6,9,10}, {4,6,9,10}, {4,7,9,10}, {5,7,9,10}, {4,8,9,10}, {6,8,9,10}, {5,7,8,9,10}, {4,6,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 137; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{1,4}, {1,2,5}, {0,1,2,3,4,5,6}, {1,2,3,7}, {0,1,2,4,7}, {1,2,5,7}, {0,6,7}, {0,4,6,7}, {0,1,2,3,5,6,7}, {0,1,2,8}, {0,3,4,8}, {0,5,8}, {0,1,2,3,4,5,6,8}, {0,3,7,8}, {0,1,2,4,7,8}, {0,5,7,8}, {1,3,6,7,8}, {1,3,4,6,7,8}, {0,1,2,3,5,6,7,8}, {0,1,2,3,9}, {3,4,9}, {0,1,2,5,9}, {4,5,6,9}, {0,1,2,3,7,9}, {3,4,7,9}, {0,1,2,5,7,9}, {0,1,3,6,7,9}, {0,1,3,4,6,7,9}, {5,6,7,9}, {0,1,8,9}, {0,1,4,8,9}, {5,8,9}, {4,5,6,8,9}, {3,7,8,9}, {3,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

- rank 8 (`N = 12`), a3 = 75; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{1,2,4}, {1,2,3,5}, {1,2,3,6}, {1,2,3,5,6}, {0,2,3,4,7}, {2,3,5,7}, {2,3,6,7}, {2,3,5,6,7}, {1,8}, {0,1,2,3,6,8}, {1,2,3,4,6,8}, {2,6,7,8}, {0,2,4,6,7,8}, {0,1,4,9}, {0,3,7,9}, {3,4,7,9}, {1,8,9}, {1,3,6,8,9}, {0,1,3,4,6,8,9}, {0,6,7,8,9}, {4,6,7,8,9}, {1,5,10}, {1,6,10}, {1,5,6,10}, {7,10}, {5,7,10}, {6,7,10}, {5,6,7,10}, {1,8,10}, {1,9,10}, {1,8,9,10}, {11}, {8,11}, {9,11}, {8,9,11}, {10,11}, {8,10,11}, {9,10,11}, {8,9,10,11}]
  ```

### 47. `[[39,4,3]]` — T0·CS12·CS13·CCZ012·CCZ013·CCZ123

- gate `0+12+13+012+013+123`, `N = 11` (4 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 67
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{0,2,3,6}, {1,2,4,6}, {2,4,5,6}, {0,1,2,3,7}, {1,2,4,6,7}, {0,1,5,6,7}, {2,4,5,6,7}, {0,1,8}, {0,2,3,5,8}, {0,2,3,7,8}, {0,2,3,5,7,8}, {0,2,3,6,7,8}, {0,1,5,6,7,8}, {0,1,2,3,5,9}, {2,4,6,9}, {0,2,3,5,6,9}, {1,2,4,5,6,9}, {0,1,2,3,5,7,9}, {0,2,3,6,7,9}, {2,4,6,7,9}, {1,2,4,5,6,7,9}, {0,2,3,6,8,9}, {0,2,3,5,6,8,9}, {1,2,3,6,10}, {4,6,10}, {4,7,10}, {1,2,3,5,7,10}, {4,8,10}, {1,2,3,6,8,10}, {1,2,3,5,7,8,10}, {4,6,7,8,10}, {6,9,10}, {4,6,9,10}, {4,7,9,10}, {5,7,9,10}, {4,8,9,10}, {6,8,9,10}, {5,7,8,9,10}, {4,6,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 137; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,2,3,4}, {0,2,5}, {0,3,4,5,6}, {0,1,7}, {0,1,2,3,4,7}, {0,2,5,7}, {1,3,6,7}, {1,3,4,6,7}, {0,3,5,6,7}, {0,1,2,3,8}, {2,3,4,8}, {1,3,5,8}, {0,3,4,5,6,8}, {2,3,7,8}, {0,1,2,3,4,7,8}, {1,3,5,7,8}, {0,1,3,6,7,8}, {0,1,3,4,6,7,8}, {0,3,5,6,7,8}, {0,3,9}, {1,2,4,9}, {0,1,2,3,5,9}, {4,5,6,9}, {0,3,7,9}, {1,2,4,7,9}, {0,1,2,3,5,7,9}, {0,6,7,9}, {0,4,6,7,9}, {5,6,7,9}, {0,1,2,8,9}, {0,1,2,4,8,9}, {5,8,9}, {4,5,6,8,9}, {1,2,7,8,9}, {1,2,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

- rank 8 (`N = 12`), a3 = 75; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{0,1,2,4}, {0,2,3,5}, {0,2,3,6}, {0,2,3,5,6}, {1,2,4,7}, {1,5,7}, {1,6,7}, {1,5,6,7}, {0,1,2,3,8}, {0,3,6,8}, {0,2,3,4,6,8}, {3,6,7,8}, {2,3,4,6,7,8}, {0,1,3,4,9}, {1,2,3,7,9}, {1,3,4,7,9}, {0,1,2,3,8,9}, {0,2,6,8,9}, {0,4,6,8,9}, {2,6,7,8,9}, {4,6,7,8,9}, {0,1,2,3,5,10}, {0,1,2,3,6,10}, {0,1,2,3,5,6,10}, {7,10}, {5,7,10}, {6,7,10}, {5,6,7,10}, {0,1,2,3,8,10}, {0,1,2,3,9,10}, {0,1,2,3,8,9,10}, {11}, {8,11}, {9,11}, {8,9,11}, {10,11}, {8,10,11}, {9,10,11}, {8,9,10,11}]
  ```

### 48. `[[39,4,3]]` — T0·CS12·CS13·CS23·CCZ012·CCZ013·CCZ023

- gate `0+12+13+23+012+013+023`, `N = 11` (4 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 67
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{0,2,3,6}, {0,1,2,3,4,6}, {0,2,4,5,6}, {0,1,2,7}, {0,1,2,3,4,6,7}, {0,1,3,5,6,7}, {0,2,4,5,6,7}, {0,1,3,8}, {0,2,3,5,8}, {0,2,3,7,8}, {0,2,3,5,7,8}, {0,2,3,6,7,8}, {0,1,3,5,6,7,8}, {0,1,2,5,9}, {0,2,4,6,9}, {0,2,3,5,6,9}, {0,1,2,3,4,5,6,9}, {0,1,2,5,7,9}, {0,2,3,6,7,9}, {0,2,4,6,7,9}, {0,1,2,3,4,5,6,7,9}, {0,2,3,6,8,9}, {0,2,3,5,6,8,9}, {1,2,6,10}, {4,6,10}, {4,7,10}, {1,2,5,7,10}, {4,8,10}, {1,2,6,8,10}, {1,2,5,7,8,10}, {4,6,7,8,10}, {6,9,10}, {4,6,9,10}, {4,7,9,10}, {5,7,9,10}, {4,8,9,10}, {6,8,9,10}, {5,7,8,9,10}, {4,6,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 137; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,4}, {2,5}, {1,4,5,6}, {0,1,3,7}, {0,2,3,4,7}, {2,5,7}, {0,3,6,7}, {0,3,4,6,7}, {1,5,6,7}, {0,2,3,8}, {1,2,4,8}, {0,3,5,8}, {1,4,5,6,8}, {1,2,7,8}, {0,2,3,4,7,8}, {0,3,5,7,8}, {3,6,7,8}, {3,4,6,7,8}, {1,5,6,7,8}, {1,9}, {0,1,2,3,4,9}, {0,2,3,5,9}, {4,5,6,9}, {1,7,9}, {0,1,2,3,4,7,9}, {0,2,3,5,7,9}, {0,6,7,9}, {0,4,6,7,9}, {5,6,7,9}, {1,2,3,8,9}, {1,2,3,4,8,9}, {5,8,9}, {4,5,6,8,9}, {0,1,2,3,7,8,9}, {0,1,2,3,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

- rank 8 (`N = 12`), a3 = 75; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{0,3,4}, {0,2,3,5}, {0,2,3,6}, {0,2,3,5,6}, {3,4,7}, {1,3,5,7}, {1,3,6,7}, {1,3,5,6,7}, {0,1,2,8}, {0,1,2,3,6,8}, {0,2,3,4,6,8}, {1,2,3,6,7,8}, {2,3,4,6,7,8}, {0,2,4,9}, {1,2,7,9}, {2,4,7,9}, {0,1,2,8,9}, {0,1,6,8,9}, {0,4,6,8,9}, {1,6,7,8,9}, {4,6,7,8,9}, {0,1,2,5,10}, {0,1,2,6,10}, {0,1,2,5,6,10}, {7,10}, {5,7,10}, {6,7,10}, {5,6,7,10}, {0,1,2,8,10}, {0,1,2,9,10}, {0,1,2,8,9,10}, {11}, {8,11}, {9,11}, {8,9,11}, {10,11}, {8,10,11}, {9,10,11}, {8,9,10,11}]
  ```

### 49. `[[39,4,3]]` — T0·T2·T3·CS01·CS12

- gate `0+2+3+01+12`, `N = 11` (4 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 67
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{1,2,6}, {1,4,6}, {0,1,2,4,5,6}, {0,1,7}, {1,4,6,7}, {3,5,6,7}, {0,1,2,4,5,6,7}, {3,8}, {1,2,5,8}, {1,2,7,8}, {1,2,5,7,8}, {1,2,6,7,8}, {3,5,6,7,8}, {0,1,5,9}, {0,1,2,4,6,9}, {1,2,5,6,9}, {1,4,5,6,9}, {0,1,5,7,9}, {1,2,6,7,9}, {0,1,2,4,6,7,9}, {1,4,5,6,7,9}, {1,2,6,8,9}, {1,2,5,6,8,9}, {1,2,3,6,10}, {4,6,10}, {4,7,10}, {1,2,3,5,7,10}, {4,8,10}, {1,2,3,6,8,10}, {1,2,3,5,7,8,10}, {4,6,7,8,10}, {6,9,10}, {4,6,9,10}, {4,7,9,10}, {5,7,9,10}, {4,8,9,10}, {6,8,9,10}, {5,7,8,9,10}, {4,6,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 137; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{1,2,4}, {1,5}, {0,3,4,5,6}, {0,1,7}, {3,4,7}, {1,5,7}, {1,3,6,7}, {1,3,4,6,7}, {0,3,5,6,7}, {3,8}, {0,1,3,4,8}, {1,3,5,8}, {0,3,4,5,6,8}, {0,1,3,7,8}, {3,4,7,8}, {1,3,5,7,8}, {0,1,2,6,7,8}, {0,1,2,4,6,7,8}, {0,3,5,6,7,8}, {0,3,9}, {0,4,9}, {3,5,9}, {4,5,6,9}, {0,3,7,9}, {0,4,7,9}, {3,5,7,9}, {0,2,3,6,7,9}, {0,2,3,4,6,7,9}, {5,6,7,9}, {2,3,8,9}, {2,3,4,8,9}, {5,8,9}, {4,5,6,8,9}, {0,7,8,9}, {0,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

- rank 8 (`N = 12`), a3 = 75; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{2,3,4}, {0,1,5}, {0,1,6}, {0,1,5,6}, {0,4,7}, {0,1,3,5,7}, {0,1,3,6,7}, {0,1,3,5,6,7}, {3,8}, {0,3,6,8}, {0,1,4,6,8}, {2,6,7,8}, {1,2,3,4,6,7,8}, {1,4,9}, {0,2,7,9}, {0,1,2,3,4,7,9}, {3,8,9}, {0,1,2,6,8,9}, {0,2,3,4,6,8,9}, {1,3,6,7,8,9}, {4,6,7,8,9}, {3,5,10}, {3,6,10}, {3,5,6,10}, {7,10}, {5,7,10}, {6,7,10}, {5,6,7,10}, {3,8,10}, {3,9,10}, {3,8,9,10}, {11}, {8,11}, {9,11}, {8,9,11}, {10,11}, {8,10,11}, {9,10,11}, {8,9,10,11}]
  ```

### 50. `[[39,4,3]]` — T0·T3·CS01·CS02·CCZ012

- gate `0+3+01+02+012`, `N = 11` (4 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 67
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{1,2,6}, {2,4,6}, {0,2,4,5,6}, {0,1,2,7}, {2,4,6,7}, {3,5,6,7}, {0,2,4,5,6,7}, {3,8}, {1,2,5,8}, {1,2,7,8}, {1,2,5,7,8}, {1,2,6,7,8}, {3,5,6,7,8}, {0,1,2,5,9}, {0,2,4,6,9}, {1,2,5,6,9}, {2,4,5,6,9}, {0,1,2,5,7,9}, {1,2,6,7,9}, {0,2,4,6,7,9}, {2,4,5,6,7,9}, {1,2,6,8,9}, {1,2,5,6,8,9}, {1,2,3,6,10}, {4,6,10}, {4,7,10}, {1,2,3,5,7,10}, {4,8,10}, {1,2,3,6,8,10}, {1,2,3,5,7,8,10}, {4,6,7,8,10}, {6,9,10}, {4,6,9,10}, {4,7,9,10}, {5,7,9,10}, {4,8,9,10}, {6,8,9,10}, {5,7,8,9,10}, {4,6,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 137; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{3,4}, {2,5}, {0,2,4,5,6}, {0,1,2,7}, {1,2,4,7}, {2,5,7}, {1,6,7}, {1,4,6,7}, {0,2,5,6,7}, {1,2,8}, {0,4,8}, {1,5,8}, {0,2,4,5,6,8}, {0,7,8}, {1,2,4,7,8}, {1,5,7,8}, {0,1,3,6,7,8}, {0,1,3,4,6,7,8}, {0,2,5,6,7,8}, {0,2,9}, {0,1,4,9}, {1,2,5,9}, {4,5,6,9}, {0,2,7,9}, {0,1,4,7,9}, {1,2,5,7,9}, {0,3,6,7,9}, {0,3,4,6,7,9}, {5,6,7,9}, {1,3,8,9}, {1,3,4,8,9}, {5,8,9}, {4,5,6,8,9}, {0,1,7,8,9}, {0,1,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

- rank 8 (`N = 12`), a3 = 75; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{1,3,4}, {0,1,2,5}, {0,1,2,6}, {0,1,2,5,6}, {0,1,4,7}, {0,5,7}, {0,6,7}, {0,5,6,7}, {1,2,8}, {0,2,6,8}, {0,1,2,4,6,8}, {2,3,6,7,8}, {1,2,3,4,6,7,8}, {2,4,9}, {0,1,2,3,7,9}, {0,2,3,4,7,9}, {1,2,8,9}, {0,1,3,6,8,9}, {0,3,4,6,8,9}, {1,6,7,8,9}, {4,6,7,8,9}, {1,2,5,10}, {1,2,6,10}, {1,2,5,6,10}, {7,10}, {5,7,10}, {6,7,10}, {5,6,7,10}, {1,2,8,10}, {1,2,9,10}, {1,2,8,9,10}, {11}, {8,11}, {9,11}, {8,9,11}, {10,11}, {8,10,11}, {9,10,11}, {8,9,10,11}]
  ```

### 51. `[[39,4,3]]` — T0·T3·CS01·CS02·CS12·CS13·CCZ012

- gate `0+3+01+02+12+13+012`, `N = 11` (4 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 67
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{1,3,6}, {1,4,6}, {0,1,2,3,4,5,6}, {0,1,2,7}, {1,4,6,7}, {2,5,6,7}, {0,1,2,3,4,5,6,7}, {2,8}, {1,3,5,8}, {1,3,7,8}, {1,3,5,7,8}, {1,3,6,7,8}, {2,5,6,7,8}, {0,1,2,5,9}, {0,1,2,3,4,6,9}, {1,3,5,6,9}, {1,4,5,6,9}, {0,1,2,5,7,9}, {1,3,6,7,9}, {0,1,2,3,4,6,7,9}, {1,4,5,6,7,9}, {1,3,6,8,9}, {1,3,5,6,8,9}, {1,2,3,6,10}, {4,6,10}, {4,7,10}, {1,2,3,5,7,10}, {4,8,10}, {1,2,3,6,8,10}, {1,2,3,5,7,8,10}, {4,6,7,8,10}, {6,9,10}, {4,6,9,10}, {4,7,9,10}, {5,7,9,10}, {4,8,9,10}, {6,8,9,10}, {5,7,8,9,10}, {4,6,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 137; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{1,3,4}, {1,5}, {0,4,5,6}, {2,7}, {0,1,2,4,7}, {1,5,7}, {0,2,6,7}, {0,2,4,6,7}, {0,5,6,7}, {0,1,2,8}, {0,1,4,8}, {0,2,5,8}, {0,4,5,6,8}, {0,1,7,8}, {0,1,2,4,7,8}, {0,2,5,7,8}, {2,3,6,7,8}, {2,3,4,6,7,8}, {0,5,6,7,8}, {0,9}, {1,2,4,9}, {0,1,2,5,9}, {4,5,6,9}, {0,7,9}, {1,2,4,7,9}, {0,1,2,5,7,9}, {0,3,6,7,9}, {0,3,4,6,7,9}, {5,6,7,9}, {0,1,2,3,8,9}, {0,1,2,3,4,8,9}, {5,8,9}, {4,5,6,8,9}, {1,2,7,8,9}, {1,2,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

- rank 8 (`N = 12`), a3 = 75; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{0,1,2,3,4}, {2,5}, {2,6}, {2,5,6}, {1,2,4,7}, {0,1,5,7}, {0,1,6,7}, {0,1,5,6,7}, {0,1,2,8}, {0,6,8}, {2,4,6,8}, {3,6,7,8}, {0,2,3,4,6,7,8}, {1,4,9}, {1,2,3,7,9}, {0,1,3,4,7,9}, {0,1,2,8,9}, {2,3,6,8,9}, {0,3,4,6,8,9}, {0,2,6,7,8,9}, {4,6,7,8,9}, {0,1,2,5,10}, {0,1,2,6,10}, {0,1,2,5,6,10}, {7,10}, {5,7,10}, {6,7,10}, {5,6,7,10}, {0,1,2,8,10}, {0,1,2,9,10}, {0,1,2,8,9,10}, {11}, {8,11}, {9,11}, {8,9,11}, {10,11}, {8,10,11}, {9,10,11}, {8,9,10,11}]
  ```

### 52. `[[39,4,3]]` — T0·T3·CS01·CS02·CS13·CS23·CCZ012·CCZ123

- gate `0+3+01+02+13+23+012+123`, `N = 11` (4 outputs + 7 checks), T-count 2, reduced degree 1, a3 = 69
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{1,2,3,4}, {1,2,3,5}, {1,2,3,4,5}, {1,2,3,6}, {1,2,3,4,6}, {1,2,3,4,5,6}, {7}, {1,2,4,7}, {0,1,2,3,4,5,6,7}, {8}, {0,2,5,8}, {2,3,6,8}, {7,8}, {2,4,5,7,8}, {0,2,3,4,6,7,8}, {0,3,5,6,9}, {7,9}, {0,4,7,9}, {3,4,5,6,7,9}, {8,9}, {1,5,8,9}, {0,1,3,6,8,9}, {7,8,9}, {0,1,4,5,7,8,9}, {1,3,4,6,7,8,9}, {4,10}, {4,7,10}, {4,8,10}, {4,7,8,10}, {9,10}, {5,9,10}, {4,5,9,10}, {6,9,10}, {4,6,9,10}, {5,6,9,10}, {4,5,6,9,10}, {4,7,9,10}, {4,8,9,10}, {4,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 113; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{4}, {0,1,5}, {2,3,4,5,6}, {0,1,2,3,7}, {0,3,4,7}, {2,3,5,7}, {1,6,7}, {1,4,6,7}, {2,3,5,6,7}, {1,2,3,8}, {4,8}, {2,5,8}, {2,3,4,5,6,8}, {3,7,8}, {0,3,4,7,8}, {0,1,3,5,7,8}, {1,6,7,8}, {1,4,6,7,8}, {2,3,5,6,7,8}, {2,3,9}, {1,4,9}, {3,5,9}, {4,5,6,9}, {2,7,9}, {0,2,4,7,9}, {0,1,2,5,7,9}, {6,7,9}, {4,6,7,9}, {5,6,7,9}, {0,1,3,8,9}, {1,4,8,9}, {0,1,2,3,5,8,9}, {4,5,6,8,9}, {0,1,7,8,9}, {0,2,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

### 53. `[[39,4,3]]` — T0·T3·CS01·CS12·CS23

- gate `0+3+01+12+23`, `N = 11` (4 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 67
- source: length40_m7_003, origin 70; rep_length40_m7_003.json

```text
[{1,2,6}, {0,4,6}, {0,1,3,4,5,6}, {2,3,7}, {0,4,6,7}, {0,1,5,6,7}, {0,1,3,4,5,6,7}, {0,1,8}, {1,2,5,8}, {1,2,7,8}, {1,2,5,7,8}, {1,2,6,7,8}, {0,1,5,6,7,8}, {2,3,5,9}, {0,1,3,4,6,9}, {1,2,5,6,9}, {0,4,5,6,9}, {2,3,5,7,9}, {1,2,6,7,9}, {0,1,3,4,6,7,9}, {0,4,5,6,7,9}, {1,2,6,8,9}, {1,2,5,6,8,9}, {0,2,6,10}, {4,6,10}, {4,7,10}, {0,2,5,7,10}, {4,8,10}, {0,2,6,8,10}, {0,2,5,7,8,10}, {4,6,7,8,10}, {6,9,10}, {4,6,9,10}, {4,7,9,10}, {5,7,9,10}, {4,8,9,10}, {6,8,9,10}, {5,7,8,9,10}, {4,6,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 137; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{1,2,4}, {1,5}, {0,2,3,4,5,6}, {2,3,7}, {0,1,4,7}, {1,5,7}, {0,6,7}, {0,4,6,7}, {0,2,3,5,6,7}, {0,1,8}, {0,1,2,3,4,8}, {0,5,8}, {0,2,3,4,5,6,8}, {0,1,2,3,7,8}, {0,1,4,7,8}, {0,5,7,8}, {3,6,7,8}, {3,4,6,7,8}, {0,2,3,5,6,7,8}, {0,2,3,9}, {1,2,3,4,9}, {0,1,5,9}, {4,5,6,9}, {0,2,3,7,9}, {1,2,3,4,7,9}, {0,1,5,7,9}, {0,3,6,7,9}, {0,3,4,6,7,9}, {5,6,7,9}, {0,1,2,8,9}, {0,1,2,4,8,9}, {5,8,9}, {4,5,6,8,9}, {1,2,3,7,8,9}, {1,2,3,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

- rank 8 (`N = 12`), a3 = 75; length40_m8_discovery_012, origin 240; rep_length40_m8_discovery_012.json

  ```text
  [{0,1,2,4}, {2,3,5}, {2,3,6}, {2,3,5,6}, {1,2,3,4,7}, {1,3,5,7}, {1,3,6,7}, {1,3,5,6,7}, {1,2,8}, {3,6,8}, {2,3,4,6,8}, {0,6,7,8}, {0,2,4,6,7,8}, {1,4,9}, {0,1,2,3,7,9}, {0,1,3,4,7,9}, {1,2,8,9}, {0,2,3,6,8,9}, {0,3,4,6,8,9}, {2,6,7,8,9}, {4,6,7,8,9}, {1,2,5,10}, {1,2,6,10}, {1,2,5,6,10}, {7,10}, {5,7,10}, {6,7,10}, {5,6,7,10}, {1,2,8,10}, {1,2,9,10}, {1,2,8,9,10}, {11}, {8,11}, {9,11}, {8,9,11}, {10,11}, {8,10,11}, {9,10,11}, {8,9,10,11}]
  ```

### 54. `[[39,4,3]]` — CS01·CS02·CS03·CCZ012·CCZ013·CCZ023

- gate `01+02+03+012+013+023`, `N = 11` (4 outputs + 7 checks), T-count 3, reduced degree 2, a3 = 90
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{1,2,3,4}, {1,2,3,5}, {1,2,3,4,5}, {1,2,3,6}, {1,2,3,4,6}, {1,2,3,4,5,6}, {0,7}, {1,2,4,7}, {0,1,2,4,5,6,7}, {0,8}, {0,2,3,5,8}, {2,3,6,8}, {0,7,8}, {2,4,5,7,8}, {0,2,4,6,7,8}, {5,6,9}, {0,7,9}, {3,4,7,9}, {0,3,4,5,6,7,9}, {0,8,9}, {0,1,5,8,9}, {1,6,8,9}, {0,7,8,9}, {1,3,4,5,7,8,9}, {0,1,3,4,6,7,8,9}, {4,10}, {4,7,10}, {4,8,10}, {4,7,8,10}, {9,10}, {5,9,10}, {4,5,9,10}, {6,9,10}, {4,6,9,10}, {5,6,9,10}, {4,5,6,9,10}, {4,7,9,10}, {4,8,9,10}, {4,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 102; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,2,4}, {5}, {4,5,6}, {0,1,2,7}, {1,4,7}, {5,7}, {1,2,3,6,7}, {4,6,7}, {1,2,3,5,6,7}, {0,8}, {0,1,3,4,8}, {5,8}, {0,1,2,3,4,5,6,8}, {0,3,7,8}, {2,3,4,7,8}, {0,1,2,3,5,7,8}, {1,2,3,6,7,8}, {0,1,2,3,4,6,7,8}, {1,2,3,5,6,7,8}, {9}, {2,4,9}, {1,2,3,5,9}, {0,1,2,3,4,5,6,9}, {1,2,7,9}, {0,1,4,7,9}, {0,1,2,3,5,7,9}, {6,7,9}, {0,1,2,3,4,6,7,9}, {5,6,7,9}, {0,8,9}, {1,3,4,8,9}, {1,2,3,5,8,9}, {4,5,6,8,9}, {3,7,8,9}, {0,2,3,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

### 55. `[[39,4,3]]` — CS01·CS02·CS03·CS13·CS23·CCZ012·CCZ123

- gate `01+02+03+13+23+012+123`, `N = 11` (4 outputs + 7 checks), T-count 3, reduced degree 2, a3 = 90
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{1,2,3,4}, {1,2,3,5}, {1,2,3,4,5}, {1,2,3,6}, {1,2,3,4,6}, {1,2,3,4,5,6}, {0,1,2,7}, {1,2,4,7}, {0,4,5,6,7}, {0,1,2,8}, {0,1,3,5,8}, {2,3,6,8}, {0,1,2,7,8}, {2,4,5,7,8}, {0,1,4,6,7,8}, {5,6,9}, {0,1,2,7,9}, {3,4,7,9}, {0,1,2,3,4,5,6,7,9}, {0,1,2,8,9}, {0,2,5,8,9}, {1,6,8,9}, {0,1,2,7,8,9}, {1,3,4,5,7,8,9}, {0,2,3,4,6,7,8,9}, {4,10}, {4,7,10}, {4,8,10}, {4,7,8,10}, {9,10}, {5,9,10}, {4,5,9,10}, {6,9,10}, {4,6,9,10}, {5,6,9,10}, {4,5,6,9,10}, {4,7,9,10}, {4,8,9,10}, {4,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 102; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,4}, {5}, {4,5,6}, {0,7}, {1,4,7}, {5,7}, {1,2,3,6,7}, {4,6,7}, {1,2,3,5,6,7}, {0,1,2,8}, {0,2,3,4,8}, {5,8}, {0,3,4,5,6,8}, {0,1,2,3,7,8}, {2,3,4,7,8}, {0,3,5,7,8}, {1,2,3,6,7,8}, {0,3,4,6,7,8}, {1,2,3,5,6,7,8}, {9}, {2,4,9}, {1,2,3,5,9}, {0,3,4,5,6,9}, {1,2,7,9}, {0,2,4,7,9}, {0,3,5,7,9}, {6,7,9}, {0,3,4,6,7,9}, {5,6,7,9}, {0,1,2,8,9}, {1,3,4,8,9}, {1,2,3,5,8,9}, {4,5,6,8,9}, {3,7,8,9}, {0,1,3,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

### 56. `[[39,4,3]]` — CS01·CS02·CS13·CS23·CCZ012·CCZ013·CCZ023·CCZ123

- gate `01+02+13+23+012+013+023+123`, `N = 11` (4 outputs + 7 checks), T-count 3, reduced degree 2, a3 = 90
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{1,2,4}, {1,2,5}, {1,2,4,5}, {1,2,6}, {1,2,4,6}, {1,2,4,5,6}, {0,3,7}, {1,4,7}, {0,1,3,4,5,6,7}, {0,3,8}, {0,2,5,8}, {2,3,6,8}, {0,3,7,8}, {3,4,5,7,8}, {0,4,6,7,8}, {5,6,9}, {0,3,7,9}, {2,4,7,9}, {0,2,3,4,5,6,7,9}, {0,3,8,9}, {0,1,5,8,9}, {1,3,6,8,9}, {0,3,7,8,9}, {1,2,3,4,5,7,8,9}, {0,1,2,4,6,7,8,9}, {4,10}, {4,7,10}, {4,8,10}, {4,7,8,10}, {9,10}, {5,9,10}, {4,5,9,10}, {6,9,10}, {4,6,9,10}, {5,6,9,10}, {4,5,6,9,10}, {4,7,9,10}, {4,8,9,10}, {4,7,8,9,10}]
```

Best witness at each other check rank:

- rank 6 (`N = 10`), a3 = 102; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,4}, {5}, {4,5,6}, {0,1,3,7}, {1,3,4,7}, {5,7}, {1,2,6,7}, {4,6,7}, {1,2,5,6,7}, {0,3,8}, {0,1,2,4,8}, {5,8}, {0,1,2,3,4,5,6,8}, {0,2,3,7,8}, {2,3,4,7,8}, {0,1,2,3,5,7,8}, {1,2,6,7,8}, {0,1,2,3,4,6,7,8}, {1,2,5,6,7,8}, {9}, {3,4,9}, {1,2,5,9}, {0,1,2,3,4,5,6,9}, {1,7,9}, {0,1,4,7,9}, {0,1,2,3,5,7,9}, {6,7,9}, {0,1,2,3,4,6,7,9}, {5,6,7,9}, {0,3,8,9}, {1,2,3,4,8,9}, {1,2,5,8,9}, {4,5,6,8,9}, {2,7,8,9}, {0,2,4,7,8,9}, {5,7,8,9}, {6,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}]
  ```

### 57. `[[39,5,3]]` — T0·CS01·CS02·CS03·CS04·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034

- gate `0+01+02+03+04+012+013+014+023+024+034`, `N = 11` (5 outputs + 6 checks), T-count 2, reduced degree 1, a3 = 123
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{1,2,3,4,5}, {1,2,6}, {2,5,6,7}, {1,8}, {5,8}, {0,1,3,4,6,8}, {0,1,3,4,7,8}, {0,1,3,4,5,7,8}, {2,6,7,8}, {9}, {2,3,5,9}, {0,2,4,6,9}, {2,5,6,7,9}, {0,4,8,9}, {5,8,9}, {3,6,8,9}, {0,3,7,8,9}, {0,3,5,7,8,9}, {2,6,7,8,9}, {2,10}, {0,1,2,4,5,10}, {1,2,3,6,10}, {5,6,7,10}, {1,3,8,10}, {2,5,8,10}, {0,1,4,6,8,10}, {1,4,7,8,10}, {1,4,5,7,8,10}, {6,7,8,10}, {0,2,9,10}, {0,2,5,9,10}, {0,2,3,4,6,9,10}, {5,6,7,9,10}, {0,3,4,8,9,10}, {2,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
```

### 58. `[[39,5,3]]` — T0·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134

- gate `0+01+02+03+04+12+13+14+012+013+014+023+024+034+123+124+134`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{2,3,4,5}, {2,3,4,6}, {2,3,4,5,6}, {2,3,4,7}, {2,3,4,5,7}, {2,3,4,5,6,7}, {1,8}, {2,3,5,8}, {0,1,2,3,5,6,7,8}, {1,9}, {1,2,4,6,9}, {0,2,4,7,9}, {1,8,9}, {0,2,5,6,8,9}, {1,2,5,7,8,9}, {0,6,7,10}, {1,8,10}, {0,4,5,8,10}, {1,4,5,6,7,8,10}, {1,9,10}, {0,1,3,6,9,10}, {3,7,9,10}, {1,8,9,10}, {3,4,5,6,8,9,10}, {0,1,3,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{1,5}, {0,1,2,4,6}, {0,3,4,5,6,7}, {0,4,8}, {0,1,2,3,4,5,8}, {1,3,4,6,8}, {0,2,7,8}, {0,2,5,7,8}, {0,3,4,6,7,8}, {0,1,2,3,4,9}, {0,1,5,9}, {3,6,9}, {0,3,4,5,6,7,9}, {1,2,3,8,9}, {0,1,2,3,4,5,8,9}, {0,2,6,8,9}, {2,7,8,9}, {2,5,7,8,9}, {0,3,4,6,7,8,9}, {0,3,4,10}, {1,2,5,10}, {1,4,6,10}, {5,6,7,10}, {2,4,8,10}, {1,2,5,8,10}, {0,1,2,3,4,6,8,10}, {0,7,8,10}, {0,5,7,8,10}, {6,7,8,10}, {0,1,2,9,10}, {0,1,2,5,9,10}, {0,2,3,6,9,10}, {5,6,7,9,10}, {0,1,3,8,9,10}, {1,2,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 59. `[[39,5,3]]` — T0·CS01·CS02·CS03·CS04·CS12·CS13·CS24·CS34·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234

- gate `0+01+02+03+04+12+13+24+34+012+013+014+023+024+034+123+124+134+234`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{2,3,5}, {2,3,6}, {2,3,5,6}, {2,3,7}, {2,3,5,7}, {2,3,5,6,7}, {1,4,8}, {2,4,5,8}, {0,1,2,5,6,7,8}, {1,4,9}, {1,3,4,6,9}, {0,3,7,9}, {1,4,8,9}, {0,4,5,6,8,9}, {1,5,7,8,9}, {0,6,7,10}, {1,4,8,10}, {0,3,4,5,8,10}, {1,3,5,6,7,8,10}, {1,4,9,10}, {0,1,2,4,6,9,10}, {2,7,9,10}, {1,4,8,9,10}, {2,3,4,5,6,8,9,10}, {0,1,2,3,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{1,4,5}, {0,1,3,6}, {0,2,3,4,5,6,7}, {0,3,8}, {0,1,2,3,4,5,8}, {1,2,3,6,8}, {0,4,7,8}, {0,4,5,7,8}, {0,2,3,4,6,7,8}, {0,1,2,3,4,9}, {0,1,4,5,9}, {2,4,6,9}, {0,2,3,4,5,6,7,9}, {1,2,4,8,9}, {0,1,2,3,4,5,8,9}, {0,4,6,8,9}, {4,7,8,9}, {4,5,7,8,9}, {0,2,3,4,6,7,8,9}, {0,2,3,4,10}, {1,5,10}, {1,3,4,6,10}, {5,6,7,10}, {3,4,8,10}, {1,5,8,10}, {0,1,2,3,4,6,8,10}, {0,7,8,10}, {0,5,7,8,10}, {6,7,8,10}, {0,1,9,10}, {0,1,5,9,10}, {0,2,6,9,10}, {5,6,7,9,10}, {0,1,2,8,9,10}, {1,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 60. `[[39,5,3]]` — T0·CS01·CS02·CS03·CS12·CS13·CS14·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234

- gate `0+01+02+03+12+13+14+24+34+012+013+023+123+234`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,3,5}, {0,1,2,3,6}, {0,1,2,3,5,6}, {0,1,2,3,7}, {0,1,2,3,5,7}, {0,1,2,3,5,6,7}, {1,4,8}, {1,3,5,8}, {0,3,4,5,6,7,8}, {1,4,9}, {0,1,2,3,4,6,9}, {2,3,7,9}, {1,4,8,9}, {0,3,5,6,8,9}, {1,3,4,5,7,8,9}, {0,6,7,10}, {1,4,8,10}, {2,5,8,10}, {0,1,2,4,5,6,7,8,10}, {1,4,9,10}, {0,4,6,9,10}, {1,7,9,10}, {1,4,8,9,10}, {0,1,2,5,6,8,9,10}, {2,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{2,3,4,5}, {0,2,4,6}, {1,2,4,5,6,7}, {2,3,8}, {0,1,2,3,5,8}, {0,1,3,6,8}, {2,7,8}, {2,5,7,8}, {1,2,4,6,7,8}, {0,1,2,3,9}, {0,2,3,4,5,9}, {1,3,4,6,9}, {1,2,4,5,6,7,9}, {0,1,8,9}, {0,1,2,3,5,8,9}, {2,6,8,9}, {0,2,7,8,9}, {0,2,5,7,8,9}, {1,2,4,6,7,8,9}, {1,2,4,10}, {0,3,4,5,10}, {0,4,6,10}, {5,6,7,10}, {3,8,10}, {0,3,4,5,8,10}, {0,1,2,3,6,8,10}, {0,7,8,10}, {0,5,7,8,10}, {6,7,8,10}, {3,4,9,10}, {3,4,5,9,10}, {1,2,3,4,6,9,10}, {5,6,7,9,10}, {0,1,2,8,9,10}, {0,3,4,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 61. `[[39,5,3]]` — T0·CS01·CS02·CS03·CS14·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ124·CCZ134·CCZ234

- gate `0+01+02+03+14+24+34+012+013+023+124+134+234`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{4,5}, {4,6}, {4,5,6}, {4,7}, {4,5,7}, {4,5,6,7}, {1,2,3,4,8}, {0,1,4,5,8}, {2,3,5,6,7,8}, {1,2,3,4,9}, {0,2,4,6,9}, {1,3,7,9}, {1,2,3,4,8,9}, {0,3,5,6,8,9}, {1,2,4,5,7,8,9}, {0,6,7,10}, {1,2,3,4,8,10}, {1,5,8,10}, {0,2,3,4,5,6,7,8,10}, {1,2,3,4,9,10}, {2,6,9,10}, {0,1,3,4,7,9,10}, {1,2,3,4,8,9,10}, {3,4,5,6,8,9,10}, {0,1,2,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,3,5}, {1,2,6}, {1,3,4,5,6,7}, {1,8}, {1,2,3,4,5,8}, {2,4,6,8}, {1,3,7,8}, {1,3,5,7,8}, {1,3,4,6,7,8}, {1,2,3,4,9}, {1,2,3,5,9}, {3,4,6,9}, {1,3,4,5,6,7,9}, {2,3,4,8,9}, {1,2,3,4,5,8,9}, {1,3,6,8,9}, {0,1,3,7,8,9}, {0,1,3,5,7,8,9}, {1,3,4,6,7,8,9}, {1,3,4,10}, {2,5,10}, {2,3,6,10}, {5,6,7,10}, {3,8,10}, {2,5,8,10}, {1,2,3,4,6,8,10}, {0,7,8,10}, {0,5,7,8,10}, {6,7,8,10}, {0,2,9,10}, {0,2,5,9,10}, {1,4,6,9,10}, {5,6,7,9,10}, {1,2,4,8,9,10}, {2,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 62. `[[39,5,3]]` — T0·CS01·CS02·CS12·CS13·CS14·CS23·CS24·CCZ012·CCZ134·CCZ234

- gate `0+01+02+12+13+14+23+24+012+134+234`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{2,3,4,5}, {2,3,4,6}, {2,3,4,5,6}, {2,3,4,7}, {2,3,4,5,7}, {2,3,4,5,6,7}, {1,3,4,8}, {2,3,5,8}, {0,1,2,4,5,6,7,8}, {1,3,4,9}, {1,2,3,6,9}, {0,2,4,7,9}, {1,3,4,8,9}, {0,2,5,6,8,9}, {1,2,3,4,5,7,8,9}, {0,6,7,10}, {1,3,4,8,10}, {0,4,5,8,10}, {1,3,5,6,7,8,10}, {1,3,4,9,10}, {0,1,4,6,9,10}, {3,7,9,10}, {1,3,4,8,9,10}, {3,4,5,6,8,9,10}, {0,1,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,5}, {1,6}, {0,2,3,5,6,7}, {0,1,4,8}, {2,3,4,5,8}, {0,1,3,6,8}, {0,1,2,4,7,8}, {0,1,2,4,5,7,8}, {0,2,3,6,7,8}, {2,3,4,9}, {1,2,5,9}, {1,2,3,4,6,9}, {0,2,3,5,6,7,9}, {0,1,2,3,8,9}, {2,3,4,5,8,9}, {0,1,2,4,6,8,9}, {1,2,4,7,8,9}, {1,2,4,5,7,8,9}, {0,2,3,6,7,8,9}, {0,2,3,10}, {0,4,5,10}, {0,2,4,6,10}, {5,6,7,10}, {2,8,10}, {0,4,5,8,10}, {2,3,4,6,8,10}, {0,7,8,10}, {0,5,7,8,10}, {6,7,8,10}, {4,9,10}, {4,5,9,10}, {0,3,6,9,10}, {5,6,7,9,10}, {3,4,8,9,10}, {0,4,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 63. `[[39,5,3]]` — T0·CS01·CS02·CS13·CS14·CS23·CS24·CCZ012·CCZ123·CCZ124·CCZ134·CCZ234

- gate `0+01+02+13+14+23+24+012+123+124+134+234`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{3,4,5}, {3,4,6}, {3,4,5,6}, {3,4,7}, {3,4,5,7}, {3,4,5,6,7}, {0,1,2,8}, {3,5,8}, {1,2,3,5,6,7,8}, {0,1,2,9}, {0,1,3,4,6,9}, {0,2,3,4,7,9}, {0,1,2,8,9}, {0,2,3,5,6,8,9}, {0,1,3,5,7,8,9}, {0,6,7,10}, {0,1,2,8,10}, {0,4,5,8,10}, {0,1,2,4,5,6,7,8,10}, {0,1,2,9,10}, {1,6,9,10}, {2,7,9,10}, {0,1,2,8,9,10}, {2,4,5,6,8,9,10}, {1,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,5}, {1,6}, {0,2,3,5,6,7}, {0,4,8}, {1,2,3,4,5,8}, {0,1,3,6,8}, {0,2,4,7,8}, {0,2,4,5,7,8}, {0,2,3,6,7,8}, {1,2,3,4,9}, {1,2,5,9}, {2,3,4,6,9}, {0,2,3,5,6,7,9}, {0,1,2,3,8,9}, {1,2,3,4,5,8,9}, {0,2,4,6,8,9}, {2,4,7,8,9}, {2,4,5,7,8,9}, {0,2,3,6,7,8,9}, {0,2,3,10}, {0,1,4,5,10}, {0,1,2,4,6,10}, {5,6,7,10}, {2,8,10}, {0,1,4,5,8,10}, {1,2,3,4,6,8,10}, {0,7,8,10}, {0,5,7,8,10}, {6,7,8,10}, {1,4,9,10}, {1,4,5,9,10}, {0,3,6,9,10}, {5,6,7,9,10}, {1,3,4,8,9,10}, {0,1,4,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 64. `[[39,5,3]]` — T0·CS01·CS12·CS13·CS14·CCZ123·CCZ124·CCZ134

- gate `0+01+12+13+14+123+124+134`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{2,3,4,5}, {2,3,4,6}, {2,3,4,5,6}, {2,3,4,7}, {2,3,4,5,7}, {2,3,4,5,6,7}, {0,1,8}, {0,2,3,5,8}, {0,1,2,3,5,6,7,8}, {0,1,9}, {1,3,4,6,9}, {3,4,7,9}, {0,1,8,9}, {0,3,5,6,8,9}, {0,1,3,5,7,8,9}, {0,6,7,10}, {0,1,8,10}, {4,5,8,10}, {1,4,5,6,7,8,10}, {0,1,9,10}, {0,1,2,6,9,10}, {0,2,7,9,10}, {0,1,8,9,10}, {2,4,5,6,8,9,10}, {1,2,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,5}, {1,3,6}, {4,5,6,7}, {2,8}, {1,2,3,4,5,8}, {1,4,6,8}, {2,3,7,8}, {2,3,5,7,8}, {4,6,7,8}, {1,2,3,4,9}, {1,5,9}, {2,4,6,9}, {4,5,6,7,9}, {1,3,4,8,9}, {1,2,3,4,5,8,9}, {2,3,6,8,9}, {0,2,3,7,8,9}, {0,2,3,5,7,8,9}, {4,6,7,8,9}, {4,10}, {1,2,3,5,10}, {1,2,6,10}, {5,6,7,10}, {3,8,10}, {1,2,3,5,8,10}, {1,2,3,4,6,8,10}, {0,7,8,10}, {0,5,7,8,10}, {6,7,8,10}, {0,1,2,3,9,10}, {0,1,2,3,5,9,10}, {3,4,6,9,10}, {5,6,7,9,10}, {1,2,4,8,9,10}, {1,2,3,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 65. `[[39,5,3]]` — T0·T1·CS01·CS02·CS03·CS04·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034

- gate `0+1+01+02+03+04+012+013+014+023+024+034`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,3,4,5}, {0,1,2,3,4,6}, {0,1,2,3,4,5,6}, {0,1,2,3,4,7}, {0,1,2,3,4,5,7}, {0,1,2,3,4,5,6,7}, {1,8}, {0,1,2,3,5,8}, {1,2,3,5,6,7,8}, {1,9}, {1,3,4,6,9}, {0,1,3,4,7,9}, {1,8,9}, {0,1,3,5,6,8,9}, {1,3,5,7,8,9}, {0,1,6,7,10}, {1,8,10}, {0,1,4,5,8,10}, {1,4,5,6,7,8,10}, {1,9,10}, {1,2,6,9,10}, {0,1,2,7,9,10}, {1,8,9,10}, {0,1,2,4,5,6,8,9,10}, {1,2,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{1,2,3,4,5}, {0,2,4,6}, {0,1,3,4,5,6,7}, {0,4,8}, {0,1,2,3,4,5,8}, {1,2,6,8}, {0,3,4,7,8}, {0,3,4,5,7,8}, {0,1,3,4,6,7,8}, {0,1,2,3,4,9}, {0,2,3,4,5,9}, {1,3,6,9}, {0,1,3,4,5,6,7,9}, {1,2,3,8,9}, {0,1,2,3,4,5,8,9}, {0,3,4,6,8,9}, {1,3,4,7,8,9}, {1,3,4,5,7,8,9}, {0,1,3,4,6,7,8,9}, {0,1,3,4,10}, {2,5,10}, {2,3,6,10}, {5,6,7,10}, {3,8,10}, {2,5,8,10}, {0,1,2,3,4,6,8,10}, {0,1,7,8,10}, {0,1,5,7,8,10}, {6,7,8,10}, {0,1,2,9,10}, {0,1,2,5,9,10}, {0,1,4,6,9,10}, {5,6,7,9,10}, {0,1,2,4,8,9,10}, {2,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 66. `[[39,5,3]]` — T0·T1·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134

- gate `0+1+01+02+03+04+12+13+14+012+013+014+023+024+034+123+124+134`, `N = 11` (5 outputs + 6 checks), T-count 2, reduced degree 1, a3 = 123
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,5}, {0,1,2,6}, {1,2,3,4,5,6,7}, {0,3,4,8}, {5,8}, {1,6,8}, {1,7,8}, {1,5,7,8}, {1,2,3,4,6,7,8}, {9}, {1,2,4,5,9}, {0,2,3,6,9}, {1,2,3,4,5,6,7,9}, {0,1,4,8,9}, {5,8,9}, {3,6,8,9}, {0,1,3,7,8,9}, {0,1,3,5,7,8,9}, {1,2,3,4,6,7,8,9}, {1,2,3,4,10}, {2,4,5,10}, {0,1,2,3,6,10}, {5,6,7,10}, {0,4,8,10}, {1,2,3,4,5,8,10}, {1,3,6,8,10}, {0,3,7,8,10}, {0,3,5,7,8,10}, {6,7,8,10}, {0,2,3,4,9,10}, {0,2,3,4,5,9,10}, {0,2,6,9,10}, {5,6,7,9,10}, {0,1,3,4,8,9,10}, {1,2,3,4,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
```

### 67. `[[39,5,3]]` — T0·T1·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234

- gate `0+1+01+02+03+04+12+13+14+23+24+012+013+014+023+024+034+123+124+134+234`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,3,4,5}, {0,1,2,3,4,6}, {0,1,2,3,4,5,6}, {0,1,2,3,4,7}, {0,1,2,3,4,5,7}, {0,1,2,3,4,5,6,7}, {2,8}, {0,2,3,4,5,8}, {1,3,4,5,6,7,8}, {2,9}, {1,2,4,6,9}, {0,4,7,9}, {2,8,9}, {0,1,4,5,6,8,9}, {2,4,5,7,8,9}, {0,1,6,7,10}, {2,8,10}, {0,5,8,10}, {1,2,5,6,7,8,10}, {2,9,10}, {1,3,6,9,10}, {0,2,3,7,9,10}, {2,8,9,10}, {0,1,2,3,5,6,8,9,10}, {3,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{3,4,5}, {0,1,3,6}, {0,2,4,5,6,7}, {0,8}, {0,1,2,3,4,5,8}, {1,2,3,6,8}, {0,4,7,8}, {0,4,5,7,8}, {0,2,4,6,7,8}, {0,1,2,3,4,9}, {0,1,3,4,5,9}, {2,4,6,9}, {0,2,4,5,6,7,9}, {1,2,3,4,8,9}, {0,1,2,3,4,5,8,9}, {0,4,6,8,9}, {1,4,7,8,9}, {1,4,5,7,8,9}, {0,2,4,6,7,8,9}, {0,2,4,10}, {1,3,5,10}, {1,3,4,6,10}, {5,6,7,10}, {4,8,10}, {1,3,5,8,10}, {0,1,2,3,4,6,8,10}, {0,1,7,8,10}, {0,1,5,7,8,10}, {6,7,8,10}, {0,3,9,10}, {0,3,5,9,10}, {0,2,6,9,10}, {5,6,7,9,10}, {0,1,2,3,8,9,10}, {1,3,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 68. `[[39,5,3]]` — T0·T1·CS01·CS02·CS03·CS04·CS23·CS24·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ234

- gate `0+1+01+02+03+04+23+24+012+013+014+023+024+034+123+124+234`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,3,4,5}, {0,1,2,3,4,6}, {0,1,2,3,4,5,6}, {0,1,2,3,4,7}, {0,1,2,3,4,5,7}, {0,1,2,3,4,5,6,7}, {1,2,8}, {0,1,2,3,5,8}, {1,3,5,6,7,8}, {1,2,9}, {0,4,6,9}, {2,4,7,9}, {1,2,8,9}, {2,5,6,8,9}, {0,5,7,8,9}, {0,1,6,7,10}, {1,2,8,10}, {0,1,4,5,8,10}, {1,2,4,5,6,7,8,10}, {1,2,9,10}, {0,2,3,6,9,10}, {3,7,9,10}, {1,2,8,9,10}, {3,4,5,6,8,9,10}, {0,2,3,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{1,2,5}, {2,6}, {3,5,6,7}, {0,1,4,8}, {0,1,2,3,4,5,8}, {0,2,3,6,8}, {1,4,7,8}, {1,4,5,7,8}, {3,6,7,8}, {0,1,2,3,4,9}, {0,2,5,9}, {0,1,3,4,6,9}, {3,5,6,7,9}, {2,3,8,9}, {0,1,2,3,4,5,8,9}, {1,4,6,8,9}, {0,4,7,8,9}, {0,4,5,7,8,9}, {3,6,7,8,9}, {3,10}, {0,1,2,4,5,10}, {1,2,4,6,10}, {5,6,7,10}, {0,8,10}, {0,1,2,4,5,8,10}, {0,1,2,3,4,6,8,10}, {0,1,7,8,10}, {0,1,5,7,8,10}, {6,7,8,10}, {2,4,9,10}, {2,4,5,9,10}, {0,3,6,9,10}, {5,6,7,9,10}, {1,2,3,4,8,9,10}, {0,1,2,4,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 69. `[[39,5,3]]` — T0·T1·CS01·CS02·CS03·CS12·CS13·CS23·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ123

- gate `0+1+01+02+03+12+13+23+24+34+012+013+023+123`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{3,4,5}, {3,4,6}, {3,4,5,6}, {3,4,7}, {3,4,5,7}, {3,4,5,6,7}, {0,1,2,3,8}, {3,5,8}, {2,5,6,7,8}, {0,1,2,3,9}, {0,3,4,6,9}, {0,2,4,7,9}, {0,1,2,3,8,9}, {0,2,5,6,8,9}, {0,3,5,7,8,9}, {0,1,6,7,10}, {0,1,2,3,8,10}, {0,1,4,5,8,10}, {0,1,2,3,4,5,6,7,8,10}, {0,1,2,3,9,10}, {1,6,9,10}, {1,2,3,7,9,10}, {0,1,2,3,8,9,10}, {1,2,3,4,5,6,8,9,10}, {1,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{2,4,5}, {0,4,6}, {0,2,3,5,6,7}, {0,1,4,8}, {0,1,2,3,5,8}, {1,3,4,6,8}, {0,2,4,7,8}, {0,2,4,5,7,8}, {0,2,3,6,7,8}, {0,1,2,3,9}, {0,1,2,4,5,9}, {1,2,3,4,6,9}, {0,2,3,5,6,7,9}, {2,3,4,8,9}, {0,1,2,3,5,8,9}, {0,2,4,6,8,9}, {1,2,4,7,8,9}, {1,2,4,5,7,8,9}, {0,2,3,6,7,8,9}, {0,2,3,10}, {1,5,10}, {2,6,10}, {5,6,7,10}, {1,2,8,10}, {1,5,8,10}, {0,1,2,3,6,8,10}, {0,1,7,8,10}, {0,1,5,7,8,10}, {6,7,8,10}, {0,9,10}, {0,5,9,10}, {0,1,3,6,9,10}, {5,6,7,9,10}, {0,3,8,9,10}, {1,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 70. `[[39,5,3]]` — T0·T1·CS01·CS02·CS03·CS12·CS13·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234

- gate `0+1+01+02+03+12+13+24+34+012+013+023+123+234`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,3,5}, {0,1,2,3,6}, {0,1,2,3,5,6}, {0,1,2,3,7}, {0,1,2,3,5,7}, {0,1,2,3,5,6,7}, {4,8}, {0,2,3,5,8}, {1,2,3,4,5,6,7,8}, {4,9}, {1,3,4,6,9}, {0,3,7,9}, {4,8,9}, {0,1,3,5,6,8,9}, {3,4,5,7,8,9}, {0,1,6,7,10}, {4,8,10}, {0,5,8,10}, {1,4,5,6,7,8,10}, {4,9,10}, {1,2,4,6,9,10}, {0,2,7,9,10}, {4,8,9,10}, {0,1,2,5,6,8,9,10}, {2,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,3,5}, {2,6}, {0,2,3,4,5,6,7}, {0,2,8}, {2,3,4,5,8}, {0,4,6,8}, {0,2,3,7,8}, {0,2,3,5,7,8}, {0,2,3,4,6,7,8}, {2,3,4,9}, {2,3,5,9}, {3,4,6,9}, {0,2,3,4,5,6,7,9}, {0,3,4,8,9}, {2,3,4,5,8,9}, {0,2,3,6,8,9}, {1,2,3,7,8,9}, {1,2,3,5,7,8,9}, {0,2,3,4,6,7,8,9}, {0,2,3,4,10}, {0,5,10}, {0,3,6,10}, {5,6,7,10}, {3,8,10}, {0,5,8,10}, {2,3,4,6,8,10}, {0,1,7,8,10}, {0,1,5,7,8,10}, {6,7,8,10}, {1,9,10}, {1,5,9,10}, {0,2,4,6,9,10}, {5,6,7,9,10}, {2,4,8,9,10}, {0,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 71. `[[39,5,3]]` — T0·T1·CS01·CS02·CS03·CS23·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ123·CCZ124·CCZ134

- gate `0+1+01+02+03+23+24+34+012+013+023+123+124+134`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,3,5}, {0,1,2,3,6}, {0,1,2,3,5,6}, {0,1,2,3,7}, {0,1,2,3,5,7}, {0,1,2,3,5,6,7}, {1,2,4,8}, {0,1,2,5,8}, {1,4,5,6,7,8}, {1,2,4,9}, {1,2,3,6,9}, {0,1,3,4,7,9}, {1,2,4,8,9}, {0,1,4,5,6,8,9}, {1,2,5,7,8,9}, {0,1,6,7,10}, {1,2,4,8,10}, {0,1,3,5,8,10}, {1,2,3,4,5,6,7,8,10}, {1,2,4,9,10}, {1,6,9,10}, {0,1,2,4,7,9,10}, {1,2,4,8,9,10}, {0,1,2,3,4,5,6,8,9,10}, {1,3,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{1,2,4,5}, {0,2,6}, {2,4,5,6,7}, {0,1,3,8}, {1,3,4,5,8}, {0,6,8}, {0,1,3,4,7,8}, {0,1,3,4,5,7,8}, {2,4,6,7,8}, {1,3,4,9}, {0,2,4,5,9}, {0,1,2,3,4,6,9}, {2,4,5,6,7,9}, {0,4,8,9}, {1,3,4,5,8,9}, {0,1,3,4,6,8,9}, {3,4,7,8,9}, {3,4,5,7,8,9}, {2,4,6,7,8,9}, {2,4,10}, {1,2,3,5,10}, {1,2,3,4,6,10}, {5,6,7,10}, {4,8,10}, {1,2,3,5,8,10}, {1,3,4,6,8,10}, {0,1,7,8,10}, {0,1,5,7,8,10}, {6,7,8,10}, {0,2,3,9,10}, {0,2,3,5,9,10}, {2,6,9,10}, {5,6,7,9,10}, {1,3,8,9,10}, {1,2,3,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 72. `[[39,5,3]]` — T0·T1·CS01·CS02·CS03·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ124·CCZ134·CCZ234

- gate `0+1+01+02+03+24+34+012+013+023+124+134+234`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{1,2,3,4,5}, {1,2,3,4,6}, {1,2,3,4,5,6}, {1,2,3,4,7}, {1,2,3,4,5,7}, {1,2,3,4,5,6,7}, {0,1,2,3,8}, {0,2,4,5,8}, {0,3,4,5,6,7,8}, {0,1,2,3,9}, {0,2,3,6,9}, {0,7,9}, {0,1,2,3,8,9}, {1,3,5,6,8,9}, {1,2,5,7,8,9}, {0,1,6,7,10}, {0,1,2,3,8,10}, {3,5,8,10}, {2,5,6,7,8,10}, {0,1,2,3,9,10}, {4,6,9,10}, {2,3,4,7,9,10}, {0,1,2,3,8,9,10}, {0,1,2,4,5,6,8,9,10}, {0,1,3,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,3,5}, {0,2,3,6}, {1,3,5,6,7}, {0,2,4,8}, {1,4,5,8}, {1,2,6,8}, {2,4,7,8}, {2,4,5,7,8}, {1,3,6,7,8}, {1,4,9}, {2,3,5,9}, {0,1,2,3,4,6,9}, {1,3,5,6,7,9}, {0,1,2,8,9}, {1,4,5,8,9}, {2,4,6,8,9}, {0,1,2,4,7,8,9}, {0,1,2,4,5,7,8,9}, {1,3,6,7,8,9}, {1,3,10}, {3,4,5,10}, {0,3,4,6,10}, {5,6,7,10}, {0,8,10}, {3,4,5,8,10}, {1,4,6,8,10}, {0,1,7,8,10}, {0,1,5,7,8,10}, {6,7,8,10}, {0,1,3,4,9,10}, {0,1,3,4,5,9,10}, {0,1,3,6,9,10}, {5,6,7,9,10}, {0,1,4,8,9,10}, {3,4,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 73. `[[39,5,3]]` — T0·T1·CS01·CS02·CS12·CS23·CS24·CCZ012·CCZ234

- gate `0+1+01+02+12+23+24+012+234`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{3,4,5}, {3,4,6}, {3,4,5,6}, {3,4,7}, {3,4,5,7}, {3,4,5,6,7}, {0,1,2,8}, {1,3,4,5,8}, {1,2,3,4,5,6,7,8}, {0,1,2,9}, {0,2,3,6,9}, {0,3,7,9}, {0,1,2,8,9}, {0,1,3,5,6,8,9}, {0,1,2,3,5,7,8,9}, {0,1,6,7,10}, {0,1,2,8,10}, {0,5,8,10}, {0,2,5,6,7,8,10}, {0,1,2,9,10}, {1,2,4,6,9,10}, {1,4,7,9,10}, {0,1,2,8,9,10}, {4,5,6,8,9,10}, {2,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,5}, {2,3,6}, {0,4,5,6,7}, {0,8}, {2,3,4,5,8}, {0,2,4,6,8}, {0,3,7,8}, {0,3,5,7,8}, {0,4,6,7,8}, {2,3,4,9}, {2,5,9}, {4,6,9}, {0,4,5,6,7,9}, {0,2,3,4,8,9}, {2,3,4,5,8,9}, {0,3,6,8,9}, {1,3,7,8,9}, {1,3,5,7,8,9}, {0,4,6,7,8,9}, {0,4,10}, {0,2,3,5,10}, {0,2,6,10}, {5,6,7,10}, {3,8,10}, {0,2,3,5,8,10}, {2,3,4,6,8,10}, {0,1,7,8,10}, {0,1,5,7,8,10}, {6,7,8,10}, {1,2,3,9,10}, {1,2,3,5,9,10}, {0,3,4,6,9,10}, {5,6,7,9,10}, {2,4,8,9,10}, {0,2,3,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 74. `[[39,5,3]]` — T0·T1·CS01·CS02·CS23·CS24·CCZ012·CCZ123·CCZ124·CCZ234

- gate `0+1+01+02+23+24+012+123+124+234`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{1,3,4,5}, {1,3,4,6}, {1,3,4,5,6}, {1,3,4,7}, {1,3,4,5,7}, {1,3,4,5,6,7}, {0,1,2,8}, {3,4,5,8}, {2,3,4,5,6,7,8}, {0,1,2,9}, {0,2,3,6,9}, {0,3,7,9}, {0,1,2,8,9}, {0,1,3,5,6,8,9}, {0,1,2,3,5,7,8,9}, {0,1,6,7,10}, {0,1,2,8,10}, {0,5,8,10}, {0,2,5,6,7,8,10}, {0,1,2,9,10}, {2,4,6,9,10}, {4,7,9,10}, {0,1,2,8,9,10}, {1,4,5,6,8,9,10}, {1,2,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,5}, {2,3,6}, {0,1,3,4,5,6,7}, {0,3,8}, {1,2,3,4,5,8}, {0,1,2,3,4,6,8}, {0,7,8}, {0,5,7,8}, {0,1,3,4,6,7,8}, {1,2,3,4,9}, {2,5,9}, {1,4,6,9}, {0,1,3,4,5,6,7,9}, {0,1,2,4,8,9}, {1,2,3,4,5,8,9}, {0,6,8,9}, {1,7,8,9}, {1,5,7,8,9}, {0,1,3,4,6,7,8,9}, {0,1,3,4,10}, {0,2,5,10}, {0,2,3,6,10}, {5,6,7,10}, {3,8,10}, {0,2,5,8,10}, {1,2,3,4,6,8,10}, {0,1,7,8,10}, {0,1,5,7,8,10}, {6,7,8,10}, {1,2,9,10}, {1,2,5,9,10}, {0,1,4,6,9,10}, {5,6,7,9,10}, {1,2,4,8,9,10}, {0,2,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 75. `[[39,5,3]]` — T0·T1·CS01·CS23·CS24·CCZ023·CCZ024·CCZ123·CCZ124·CCZ234

- gate `0+1+01+23+24+023+024+123+124+234`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,5}, {0,1,2,6}, {0,1,2,5,6}, {0,1,2,7}, {0,1,2,5,7}, {0,1,2,5,6,7}, {0,1,3,4,8}, {0,2,5,8}, {0,2,3,4,5,6,7,8}, {0,1,3,4,9}, {2,3,6,9}, {2,4,7,9}, {0,1,3,4,8,9}, {1,2,4,5,6,8,9}, {1,2,3,5,7,8,9}, {0,1,6,7,10}, {0,1,3,4,8,10}, {0,5,8,10}, {0,3,4,5,6,7,8,10}, {0,1,3,4,9,10}, {3,6,9,10}, {4,7,9,10}, {0,1,3,4,8,9,10}, {1,4,5,6,8,9,10}, {1,3,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,5}, {0,1,2,3,6}, {0,4,5,6,7}, {0,8}, {0,1,2,3,4,5,8}, {0,2,4,6,8}, {1,3,7,8}, {1,3,5,7,8}, {0,4,6,7,8}, {0,1,2,3,4,9}, {2,5,9}, {4,6,9}, {0,4,5,6,7,9}, {1,2,3,4,8,9}, {0,1,2,3,4,5,8,9}, {1,3,6,8,9}, {0,3,7,8,9}, {0,3,5,7,8,9}, {0,4,6,7,8,9}, {0,4,10}, {1,2,3,5,10}, {0,2,6,10}, {5,6,7,10}, {0,1,3,8,10}, {1,2,3,5,8,10}, {0,1,2,3,4,6,8,10}, {0,1,7,8,10}, {0,1,5,7,8,10}, {6,7,8,10}, {0,2,3,9,10}, {0,2,3,5,9,10}, {1,3,4,6,9,10}, {5,6,7,9,10}, {2,4,8,9,10}, {1,2,3,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 76. `[[39,5,3]]` — T0·T1·CS01·CS23·CS24·CS34·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134

- gate `0+1+01+23+24+34+023+024+034+123+124+134`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,4,5}, {0,1,2,4,6}, {0,1,2,4,5,6}, {0,1,2,4,7}, {0,1,2,4,5,7}, {0,1,2,4,5,6,7}, {0,1,2,3,8}, {0,1,2,5,8}, {0,1,3,5,6,7,8}, {0,1,2,3,9}, {1,2,4,6,9}, {1,3,4,7,9}, {0,1,2,3,8,9}, {1,3,5,6,8,9}, {1,2,5,7,8,9}, {0,1,6,7,10}, {0,1,2,3,8,10}, {0,1,4,5,8,10}, {0,1,2,3,4,5,6,7,8,10}, {0,1,2,3,9,10}, {1,6,9,10}, {1,2,3,7,9,10}, {0,1,2,3,8,9,10}, {1,2,3,4,5,6,8,9,10}, {1,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,4,5}, {0,4,6}, {0,2,3,5,6,7}, {0,1,4,8}, {0,1,2,3,5,8}, {0,3,4,6,8}, {1,2,4,7,8}, {1,2,4,5,7,8}, {0,2,3,6,7,8}, {0,1,2,3,9}, {2,4,5,9}, {1,2,3,4,6,9}, {0,2,3,5,6,7,9}, {2,3,4,8,9}, {0,1,2,3,5,8,9}, {1,2,4,6,8,9}, {0,2,4,7,8,9}, {0,2,4,5,7,8,9}, {0,2,3,6,7,8,9}, {0,2,3,10}, {1,5,10}, {0,1,2,6,10}, {5,6,7,10}, {0,2,8,10}, {1,5,8,10}, {0,1,2,3,6,8,10}, {0,1,7,8,10}, {0,1,5,7,8,10}, {6,7,8,10}, {0,9,10}, {0,5,9,10}, {3,6,9,10}, {5,6,7,9,10}, {1,3,8,9,10}, {1,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 77. `[[39,5,3]]` — T0·T1·T2·CS01·CS02·CS03·CS04·CS12·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034

- gate `0+1+2+01+02+03+04+12+012+013+014+023+024+034`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,3,4,5}, {0,1,2,3,4,6}, {0,1,2,3,4,5,6}, {0,1,2,3,4,7}, {0,1,2,3,4,5,7}, {0,1,2,3,4,5,6,7}, {1,2,8}, {0,1,2,3,5,8}, {1,2,3,5,6,7,8}, {1,2,9}, {1,4,6,9}, {0,1,4,7,9}, {1,2,8,9}, {0,1,5,6,8,9}, {1,5,7,8,9}, {0,1,2,6,7,10}, {1,2,8,10}, {0,1,2,4,5,8,10}, {1,2,4,5,6,7,8,10}, {1,2,9,10}, {1,3,6,9,10}, {0,1,3,7,9,10}, {1,2,8,9,10}, {0,1,3,4,5,6,8,9,10}, {1,3,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{1,2,3,4,5}, {0,2,3,4,6}, {2,3,5,6,7}, {0,1,2,4,8}, {1,2,5,8}, {0,2,4,6,8}, {0,1,4,7,8}, {0,1,4,5,7,8}, {2,3,6,7,8}, {1,2,9}, {0,3,4,5,9}, {0,1,3,4,6,9}, {2,3,5,6,7,9}, {0,4,8,9}, {1,2,5,8,9}, {0,1,4,6,8,9}, {2,4,7,8,9}, {2,4,5,7,8,9}, {2,3,6,7,8,9}, {2,3,10}, {1,3,5,10}, {1,2,3,6,10}, {5,6,7,10}, {2,8,10}, {1,3,5,8,10}, {1,2,6,8,10}, {0,1,2,7,8,10}, {0,1,2,5,7,8,10}, {6,7,8,10}, {0,2,3,9,10}, {0,2,3,5,9,10}, {3,6,9,10}, {5,6,7,9,10}, {1,8,9,10}, {1,3,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 78. `[[39,5,3]]` — T0·T1·T2·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134

- gate `0+1+2+01+02+03+04+12+13+14+012+013+014+023+024+034+123+124+134`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,3,4,5}, {0,1,2,3,4,6}, {0,1,2,3,4,5,6}, {0,1,2,3,4,7}, {0,1,2,3,4,5,7}, {0,1,2,3,4,5,6,7}, {2,8}, {0,1,4,5,8}, {4,5,6,7,8}, {2,9}, {0,3,4,6,9}, {1,3,4,7,9}, {2,8,9}, {1,2,4,5,6,8,9}, {0,2,4,5,7,8,9}, {0,1,2,6,7,10}, {2,8,10}, {0,1,3,5,8,10}, {3,5,6,7,8,10}, {2,9,10}, {0,6,9,10}, {1,7,9,10}, {2,8,9,10}, {1,2,3,5,6,8,9,10}, {0,2,3,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,3,4,5}, {3,6}, {0,2,4,5,6,7}, {0,8}, {2,3,4,5,8}, {0,2,3,6,8}, {0,4,7,8}, {0,4,5,7,8}, {0,2,4,6,7,8}, {2,3,4,9}, {3,4,5,9}, {2,4,6,9}, {0,2,4,5,6,7,9}, {0,2,3,4,8,9}, {2,3,4,5,8,9}, {0,4,6,8,9}, {1,2,4,7,8,9}, {1,2,4,5,7,8,9}, {0,2,4,6,7,8,9}, {0,2,4,10}, {0,3,5,10}, {0,3,4,6,10}, {5,6,7,10}, {4,8,10}, {0,3,5,8,10}, {2,3,4,6,8,10}, {0,1,2,7,8,10}, {0,1,2,5,7,8,10}, {6,7,8,10}, {1,2,3,9,10}, {1,2,3,5,9,10}, {0,2,6,9,10}, {5,6,7,9,10}, {2,3,8,9,10}, {0,3,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 79. `[[39,5,3]]` — T0·T1·T2·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234

- gate `0+1+2+01+02+03+04+12+13+14+23+24+012+013+014+023+024+034+123+124+134+234`, `N = 11` (5 outputs + 6 checks), T-count 2, reduced degree 1, a3 = 123
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{3,4,5}, {2,3,6}, {1,2,3,5,6,7}, {1,8}, {5,8}, {0,4,6,8}, {0,4,7,8}, {0,4,5,7,8}, {1,2,3,6,7,8}, {9}, {1,2,3,4,5,9}, {0,2,3,6,9}, {1,2,3,5,6,7,9}, {0,1,8,9}, {5,8,9}, {4,6,8,9}, {0,1,2,4,7,8,9}, {0,1,2,4,5,7,8,9}, {1,2,3,6,7,8,9}, {1,2,3,10}, {0,1,2,3,5,10}, {2,3,4,6,10}, {5,6,7,10}, {1,4,8,10}, {1,2,3,5,8,10}, {0,6,8,10}, {1,2,7,8,10}, {1,2,5,7,8,10}, {6,7,8,10}, {0,3,9,10}, {0,3,5,9,10}, {0,2,3,4,6,9,10}, {5,6,7,9,10}, {0,1,4,8,9,10}, {1,2,3,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
```

### 80. `[[39,5,3]]` — T0·T1·T2·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CS34·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234

- gate `0+1+2+01+02+03+04+12+13+14+23+24+34+012+013+014+023+024+034+123+124+134+234`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{4,5}, {4,6}, {4,5,6}, {4,7}, {4,5,7}, {4,5,6,7}, {3,8}, {2,5,8}, {0,1,3,5,6,7,8}, {3,9}, {1,2,3,4,6,9}, {0,4,7,9}, {3,8,9}, {0,2,5,6,8,9}, {1,3,5,7,8,9}, {0,1,2,6,7,10}, {3,8,10}, {0,1,4,5,8,10}, {2,3,4,5,6,7,8,10}, {3,9,10}, {0,3,6,9,10}, {1,2,7,9,10}, {3,8,9,10}, {1,4,5,6,8,9,10}, {0,2,3,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,3,4,5}, {1,3,4,6}, {0,5,6,7}, {0,1,4,8}, {3,5,8}, {0,3,4,6,8}, {0,4,7,8}, {0,4,5,7,8}, {0,6,7,8}, {3,9}, {3,4,5,9}, {1,4,6,9}, {0,5,6,7,9}, {0,1,3,4,8,9}, {3,5,8,9}, {0,4,6,8,9}, {1,2,4,7,8,9}, {1,2,4,5,7,8,9}, {0,6,7,8,9}, {0,10}, {0,3,5,10}, {0,1,3,6,10}, {5,6,7,10}, {1,8,10}, {0,3,5,8,10}, {3,6,8,10}, {0,1,2,7,8,10}, {0,1,2,5,7,8,10}, {6,7,8,10}, {1,2,3,9,10}, {1,2,3,5,9,10}, {0,1,6,9,10}, {5,6,7,9,10}, {1,3,8,9,10}, {0,3,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 81. `[[39,5,3]]` — T0·T1·T2·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS34·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234

- gate `0+1+2+01+02+03+04+12+13+14+34+012+013+014+023+024+034+123+124+134+234`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{2,4,5}, {2,4,6}, {2,4,5,6}, {2,4,7}, {2,4,5,7}, {2,4,5,6,7}, {0,1,2,3,4,8}, {1,4,5,8}, {1,3,5,6,7,8}, {0,1,2,3,4,9}, {0,1,3,4,6,9}, {0,1,7,9}, {0,1,2,3,4,8,9}, {0,2,5,6,8,9}, {0,2,3,4,5,7,8,9}, {0,1,2,6,7,10}, {0,1,2,3,4,8,10}, {0,5,8,10}, {0,3,4,5,6,7,8,10}, {0,1,2,3,4,9,10}, {3,6,9,10}, {4,7,9,10}, {0,1,2,3,4,8,9,10}, {1,2,4,5,6,8,9,10}, {1,2,3,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{2,3,5}, {0,3,6}, {0,2,4,5,6,7}, {0,1,8}, {0,1,2,3,4,5,8}, {1,2,3,4,6,8}, {0,7,8}, {0,5,7,8}, {0,2,4,6,7,8}, {0,1,2,3,4,9}, {0,1,3,5,9}, {1,2,4,6,9}, {0,2,4,5,6,7,9}, {2,3,4,8,9}, {0,1,2,3,4,5,8,9}, {0,6,8,9}, {1,2,7,8,9}, {1,2,5,7,8,9}, {0,2,4,6,7,8,9}, {0,2,4,10}, {1,3,5,10}, {3,6,10}, {5,6,7,10}, {1,8,10}, {1,3,5,8,10}, {0,1,2,3,4,6,8,10}, {0,1,2,7,8,10}, {0,1,2,5,7,8,10}, {6,7,8,10}, {0,2,3,9,10}, {0,2,3,5,9,10}, {0,1,2,4,6,9,10}, {5,6,7,9,10}, {0,2,3,4,8,9,10}, {1,3,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 82. `[[39,5,3]]` — T0·T1·T2·CS01·CS02·CS03·CS04·CS12·CS34·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ134·CCZ234

- gate `0+1+2+01+02+03+04+12+34+012+013+014+023+024+034+134+234`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,3,4,5}, {0,1,2,3,4,6}, {0,1,2,3,4,5,6}, {0,1,2,3,4,7}, {0,1,2,3,4,5,7}, {0,1,2,3,4,5,6,7}, {1,2,3,8}, {0,1,2,3,5,8}, {1,2,5,6,7,8}, {1,2,3,9}, {1,3,4,6,9}, {0,1,4,7,9}, {1,2,3,8,9}, {0,1,5,6,8,9}, {1,3,5,7,8,9}, {0,1,2,6,7,10}, {1,2,3,8,10}, {0,1,2,4,5,8,10}, {1,2,3,4,5,6,7,8,10}, {1,2,3,9,10}, {1,6,9,10}, {0,1,3,7,9,10}, {1,2,3,8,9,10}, {0,1,3,4,5,6,8,9,10}, {1,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{1,2,4,5}, {0,2,4,6}, {0,2,3,4,5,6,7}, {0,1,2,4,8}, {0,1,2,3,4,5,8}, {2,3,6,8}, {0,1,4,7,8}, {0,1,4,5,7,8}, {0,2,3,4,6,7,8}, {0,1,2,3,4,9}, {0,4,5,9}, {1,3,6,9}, {0,2,3,4,5,6,7,9}, {3,8,9}, {0,1,2,3,4,5,8,9}, {0,1,4,6,8,9}, {2,4,7,8,9}, {2,4,5,7,8,9}, {0,2,3,4,6,7,8,9}, {0,2,3,4,10}, {1,5,10}, {1,2,6,10}, {5,6,7,10}, {2,8,10}, {1,5,8,10}, {0,1,2,3,4,6,8,10}, {0,1,2,7,8,10}, {0,1,2,5,7,8,10}, {6,7,8,10}, {0,2,9,10}, {0,2,5,9,10}, {0,3,4,6,9,10}, {5,6,7,9,10}, {0,1,3,4,8,9,10}, {1,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 83. `[[39,5,3]]` — T0·T1·T2·CS01·CS02·CS03·CS12·CS13·CS23·CS34·CCZ012·CCZ013·CCZ023·CCZ123

- gate `0+1+2+01+02+03+12+13+23+34+012+013+023+123`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{3,4,5}, {3,4,6}, {3,4,5,6}, {3,4,7}, {3,4,5,7}, {3,4,5,6,7}, {4,8}, {2,3,4,5,8}, {0,1,3,5,6,7,8}, {4,9}, {0,2,3,4,6,9}, {1,3,7,9}, {4,8,9}, {1,2,3,5,6,8,9}, {0,3,4,5,7,8,9}, {0,1,2,6,7,10}, {4,8,10}, {0,1,5,8,10}, {2,4,5,6,7,8,10}, {4,9,10}, {1,6,9,10}, {0,2,4,7,9,10}, {4,8,9,10}, {0,4,5,6,8,9,10}, {1,2,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,3,5}, {0,6}, {1,3,4,5,6,7}, {0,1,8}, {3,4,5,8}, {1,4,6,8}, {1,3,7,8}, {1,3,5,7,8}, {1,3,4,6,7,8}, {3,4,9}, {3,5,9}, {0,3,4,6,9}, {1,3,4,5,6,7,9}, {0,1,3,4,8,9}, {3,4,5,8,9}, {1,3,6,8,9}, {0,2,3,7,8,9}, {0,2,3,5,7,8,9}, {1,3,4,6,7,8,9}, {1,3,4,10}, {1,5,10}, {0,1,3,6,10}, {5,6,7,10}, {0,3,8,10}, {1,5,8,10}, {3,4,6,8,10}, {0,1,2,7,8,10}, {0,1,2,5,7,8,10}, {6,7,8,10}, {0,2,9,10}, {0,2,5,9,10}, {0,1,4,6,9,10}, {5,6,7,9,10}, {0,4,8,9,10}, {1,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 84. `[[39,5,3]]` — T0·T1·T2·CS01·CS02·CS03·CS12·CS13·CS34·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234

- gate `0+1+2+01+02+03+12+13+34+012+013+023+123+234`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{2,4,5}, {2,4,6}, {2,4,5,6}, {2,4,7}, {2,4,5,7}, {2,4,5,6,7}, {2,3,4,8}, {1,2,4,5,8}, {0,2,3,5,6,7,8}, {2,3,4,9}, {1,3,4,6,9}, {0,7,9}, {2,3,4,8,9}, {0,1,5,6,8,9}, {3,4,5,7,8,9}, {0,1,2,6,7,10}, {2,3,4,8,10}, {0,2,5,8,10}, {1,2,3,4,5,6,7,8,10}, {2,3,4,9,10}, {0,3,6,9,10}, {1,4,7,9,10}, {2,3,4,8,9,10}, {4,5,6,8,9,10}, {0,1,3,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,3,5}, {2,3,6}, {0,2,4,5,6,7}, {0,2,8}, {2,3,4,5,8}, {0,2,3,4,6,8}, {0,7,8}, {0,5,7,8}, {0,2,4,6,7,8}, {2,3,4,9}, {3,5,9}, {4,6,9}, {0,2,4,5,6,7,9}, {0,3,4,8,9}, {2,3,4,5,8,9}, {0,6,8,9}, {1,2,7,8,9}, {1,2,5,7,8,9}, {0,2,4,6,7,8,9}, {0,2,4,10}, {0,3,5,10}, {0,2,3,6,10}, {5,6,7,10}, {2,8,10}, {0,3,5,8,10}, {2,3,4,6,8,10}, {0,1,2,7,8,10}, {0,1,2,5,7,8,10}, {6,7,8,10}, {1,2,3,9,10}, {1,2,3,5,9,10}, {0,4,6,9,10}, {5,6,7,9,10}, {3,4,8,9,10}, {0,3,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 85. `[[39,5,3]]` — T0·T1·T2·CS01·CS02·CS03·CS12·CS34·CCZ012·CCZ013·CCZ023·CCZ134·CCZ234

- gate `0+1+2+01+02+03+12+34+012+013+023+134+234`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{1,2,3,4,5}, {1,2,3,4,6}, {1,2,3,4,5,6}, {1,2,3,4,7}, {1,2,3,4,5,7}, {1,2,3,4,5,6,7}, {1,2,4,8}, {0,1,2,4,5,8}, {1,2,5,6,7,8}, {1,2,4,9}, {0,1,3,4,6,9}, {1,3,7,9}, {1,2,4,8,9}, {0,1,5,6,8,9}, {1,4,5,7,8,9}, {0,1,2,6,7,10}, {1,2,4,8,10}, {1,2,3,5,8,10}, {0,1,2,3,4,5,6,7,8,10}, {1,2,4,9,10}, {1,6,9,10}, {0,1,4,7,9,10}, {1,2,4,8,9,10}, {1,3,4,5,6,8,9,10}, {0,1,3,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,3,5}, {2,3,6}, {2,3,4,5,6,7}, {1,2,3,8}, {1,2,3,4,5,8}, {2,4,6,8}, {1,3,7,8}, {1,3,5,7,8}, {2,3,4,6,7,8}, {1,2,3,4,9}, {3,5,9}, {1,4,6,9}, {2,3,4,5,6,7,9}, {4,8,9}, {1,2,3,4,5,8,9}, {1,3,6,8,9}, {0,2,3,7,8,9}, {0,2,3,5,7,8,9}, {2,3,4,6,7,8,9}, {2,3,4,10}, {1,5,10}, {1,2,6,10}, {5,6,7,10}, {2,8,10}, {1,5,8,10}, {1,2,3,4,6,8,10}, {0,1,2,7,8,10}, {0,1,2,5,7,8,10}, {6,7,8,10}, {0,2,9,10}, {0,2,5,9,10}, {3,4,6,9,10}, {5,6,7,9,10}, {1,3,4,8,9,10}, {1,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 86. `[[39,5,3]]` — T0·T1·T2·CS01·CS02·CS12·CS34·CCZ012·CCZ034·CCZ134·CCZ234

- gate `0+1+2+01+02+12+34+012+034+134+234`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,4,5}, {0,1,2,4,6}, {0,1,2,4,5,6}, {0,1,2,4,7}, {0,1,2,4,5,7}, {0,1,2,4,5,6,7}, {0,1,2,3,8}, {0,1,3,5,8}, {0,1,5,6,7,8}, {0,1,2,3,9}, {0,2,3,4,6,9}, {0,2,4,7,9}, {0,1,2,3,8,9}, {0,3,5,6,8,9}, {0,5,7,8,9}, {0,1,2,6,7,10}, {0,1,2,3,8,10}, {0,1,3,4,5,8,10}, {0,1,4,5,6,7,8,10}, {0,1,2,3,9,10}, {0,2,3,6,9,10}, {0,2,7,9,10}, {0,1,2,3,8,9,10}, {0,3,4,5,6,8,9,10}, {0,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,3,5}, {0,4,6}, {0,2,3,4,5,6,7}, {0,1,4,8}, {0,1,2,3,4,5,8}, {0,2,4,6,8}, {1,3,7,8}, {1,3,5,7,8}, {0,2,3,4,6,7,8}, {0,1,2,3,4,9}, {3,5,9}, {1,2,3,6,9}, {0,2,3,4,5,6,7,9}, {2,3,8,9}, {0,1,2,3,4,5,8,9}, {1,3,6,8,9}, {0,2,3,7,8,9}, {0,2,3,5,7,8,9}, {0,2,3,4,6,7,8,9}, {0,2,3,4,10}, {1,5,10}, {0,1,3,4,6,10}, {5,6,7,10}, {0,3,4,8,10}, {1,5,8,10}, {0,1,2,3,4,6,8,10}, {0,1,2,7,8,10}, {0,1,2,5,7,8,10}, {6,7,8,10}, {0,2,9,10}, {0,2,5,9,10}, {2,6,9,10}, {5,6,7,9,10}, {1,2,8,9,10}, {1,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 87. `[[39,5,3]]` — T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134

- gate `0+1+2+3+01+02+03+04+12+13+14+23+012+013+014+023+024+034+123+124+134`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{2,3,4,5}, {2,3,4,6}, {2,3,4,5,6}, {2,3,4,7}, {2,3,4,5,7}, {2,3,4,5,6,7}, {0,1,2,3,4,8}, {2,4,5,8}, {2,5,6,7,8}, {0,1,2,3,4,9}, {0,6,9}, {0,4,7,9}, {0,1,2,3,4,8,9}, {0,3,4,5,6,8,9}, {0,3,5,7,8,9}, {0,1,2,3,6,7,10}, {0,1,2,3,4,8,10}, {0,1,2,5,8,10}, {0,1,2,4,5,6,7,8,10}, {0,1,2,3,4,9,10}, {1,4,6,9,10}, {1,7,9,10}, {0,1,2,3,4,8,9,10}, {1,3,5,6,8,9,10}, {1,3,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,3,4,5}, {1,2,4,6}, {0,2,3,5,6,7}, {0,1,2,8}, {2,3,4,5,8}, {0,2,3,4,6,8}, {0,7,8}, {0,5,7,8}, {0,2,3,6,7,8}, {2,3,4,9}, {4,5,9}, {1,3,6,9}, {0,2,3,5,6,7,9}, {0,1,3,4,8,9}, {2,3,4,5,8,9}, {0,6,8,9}, {1,2,3,7,8,9}, {1,2,3,5,7,8,9}, {0,2,3,6,7,8,9}, {0,2,3,10}, {0,4,5,10}, {0,1,2,4,6,10}, {5,6,7,10}, {1,2,8,10}, {0,4,5,8,10}, {2,3,4,6,8,10}, {0,1,2,3,7,8,10}, {0,1,2,3,5,7,8,10}, {6,7,8,10}, {1,2,3,4,9,10}, {1,2,3,4,5,9,10}, {0,1,3,6,9,10}, {5,6,7,9,10}, {1,3,4,8,9,10}, {0,4,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 88. `[[39,5,3]]` — T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234

- gate `0+1+2+3+01+02+03+04+12+13+14+23+24+012+013+014+023+024+034+123+124+134+234`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,3,4,5}, {0,1,2,3,4,6}, {0,1,2,3,4,5,6}, {0,1,2,3,4,7}, {0,1,2,3,4,5,7}, {0,1,2,3,4,5,6,7}, {3,4,8}, {0,1,3,4,5,8}, {2,3,5,6,7,8}, {3,4,9}, {0,2,6,9}, {1,4,7,9}, {3,4,8,9}, {1,2,4,5,6,8,9}, {0,5,7,8,9}, {0,1,2,3,6,7,10}, {3,4,8,10}, {0,1,3,5,8,10}, {2,3,4,5,6,7,8,10}, {3,4,9,10}, {0,2,4,6,9,10}, {1,7,9,10}, {3,4,8,9,10}, {1,2,5,6,8,9,10}, {0,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,3,4,5}, {0,6}, {1,4,5,6,7}, {0,1,3,8}, {3,4,5,8}, {1,6,8}, {1,3,4,7,8}, {1,3,4,5,7,8}, {1,4,6,7,8}, {3,4,9}, {4,5,9}, {0,3,4,6,9}, {1,4,5,6,7,9}, {0,1,4,8,9}, {3,4,5,8,9}, {1,3,4,6,8,9}, {0,2,4,7,8,9}, {0,2,4,5,7,8,9}, {1,4,6,7,8,9}, {1,4,10}, {1,3,5,10}, {0,1,3,4,6,10}, {5,6,7,10}, {0,4,8,10}, {1,3,5,8,10}, {3,4,6,8,10}, {0,1,2,3,7,8,10}, {0,1,2,3,5,7,8,10}, {6,7,8,10}, {0,2,9,10}, {0,2,5,9,10}, {0,1,6,9,10}, {5,6,7,9,10}, {0,3,8,9,10}, {1,3,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 89. `[[39,5,3]]` — T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CS34·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234

- gate `0+1+2+3+01+02+03+04+12+13+14+23+24+34+012+013+014+023+024+034+123+124+134+234`, `N = 11` (5 outputs + 6 checks), T-count 2, reduced degree 1, a3 = 123
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,5}, {0,1,4,6}, {1,4,5,6,7}, {0,8}, {5,8}, {1,6,8}, {1,7,8}, {1,5,7,8}, {1,4,6,7,8}, {9}, {1,2,4,5,9}, {0,2,4,6,9}, {1,4,5,6,7,9}, {0,1,2,8,9}, {5,8,9}, {2,6,8,9}, {0,1,3,7,8,9}, {0,1,3,5,7,8,9}, {1,4,6,7,8,9}, {1,4,10}, {2,4,5,10}, {0,1,2,4,6,10}, {5,6,7,10}, {0,2,8,10}, {1,4,5,8,10}, {1,2,6,8,10}, {0,3,7,8,10}, {0,3,5,7,8,10}, {6,7,8,10}, {0,2,3,4,9,10}, {0,2,3,4,5,9,10}, {0,4,6,9,10}, {5,6,7,9,10}, {0,1,8,9,10}, {1,4,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
```

### 90. `[[39,5,3]]` — T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS12·CS13·CS23·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123

- gate `0+1+2+3+01+02+03+04+12+13+23+012+013+014+023+024+034+123`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{1,2,3,4,5}, {1,2,3,4,6}, {1,2,3,4,5,6}, {1,2,3,4,7}, {1,2,3,4,5,7}, {1,2,3,4,5,6,7}, {0,1,2,3,4,8}, {0,1,5,8}, {0,1,4,5,6,7,8}, {0,1,2,3,4,9}, {0,2,4,6,9}, {0,2,7,9}, {0,1,2,3,4,8,9}, {3,4,5,6,8,9}, {3,5,7,8,9}, {0,1,2,3,6,7,10}, {0,1,2,3,4,8,10}, {1,4,5,8,10}, {1,5,6,7,8,10}, {0,1,2,3,4,9,10}, {2,6,9,10}, {2,4,7,9,10}, {0,1,2,3,4,8,9,10}, {0,3,5,6,8,9,10}, {0,3,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,3,4,5}, {3,4,6}, {1,3,5,6,7}, {2,3,4,8}, {1,2,3,5,8}, {1,3,4,6,8}, {2,4,7,8}, {2,4,5,7,8}, {1,3,6,7,8}, {1,2,3,9}, {4,5,9}, {1,2,4,6,9}, {1,3,5,6,7,9}, {1,4,8,9}, {1,2,3,5,8,9}, {2,4,6,8,9}, {0,1,3,4,7,8,9}, {0,1,3,4,5,7,8,9}, {1,3,6,7,8,9}, {1,3,10}, {2,5,10}, {2,3,6,10}, {5,6,7,10}, {3,8,10}, {2,5,8,10}, {1,2,3,6,8,10}, {0,1,2,3,7,8,10}, {0,1,2,3,5,7,8,10}, {6,7,8,10}, {0,1,3,9,10}, {0,1,3,5,9,10}, {1,6,9,10}, {5,6,7,9,10}, {1,2,8,9,10}, {2,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 91. `[[39,5,3]]` — T0·T1·T2·T3·CS01·CS02·CS03·CS12·CS34·CCZ012·CCZ034

- gate `0+1+2+3+01+02+03+12+34+012+034`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,5}, {0,1,2,6}, {0,1,2,5,6}, {0,1,2,7}, {0,1,2,5,7}, {0,1,2,5,6,7}, {0,3,4,8}, {1,2,5,8}, {4,5,6,7,8}, {0,3,4,9}, {1,3,4,6,9}, {2,3,7,9}, {0,3,4,8,9}, {0,2,3,5,6,8,9}, {0,1,3,4,5,7,8,9}, {0,1,2,3,6,7,10}, {0,3,4,8,10}, {1,2,3,5,8,10}, {3,4,5,6,7,8,10}, {0,3,4,9,10}, {1,4,6,9,10}, {2,7,9,10}, {0,3,4,8,9,10}, {0,2,5,6,8,9,10}, {0,1,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,4,5}, {1,4,6}, {0,2,5,6,7}, {1,2,3,8}, {0,3,4,5,8}, {0,1,3,4,6,8}, {1,7,8}, {1,5,7,8}, {0,2,6,7,8}, {0,3,4,9}, {1,2,3,4,5,9}, {0,1,3,6,9}, {0,2,5,6,7,9}, {0,1,2,4,8,9}, {0,3,4,5,8,9}, {1,6,8,9}, {0,2,3,7,8,9}, {0,2,3,5,7,8,9}, {0,2,6,7,8,9}, {0,2,10}, {2,3,4,5,10}, {4,6,10}, {5,6,7,10}, {2,3,8,10}, {2,3,4,5,8,10}, {0,3,4,6,8,10}, {0,1,2,3,7,8,10}, {0,1,2,3,5,7,8,10}, {6,7,8,10}, {0,1,4,9,10}, {0,1,4,5,9,10}, {0,3,6,9,10}, {5,6,7,9,10}, {0,2,4,8,9,10}, {2,3,4,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 92. `[[39,5,3]]` — T0·T1·T2·T3·CS01·CS02·CS12·CS34·CCZ012

- gate `0+1+2+3+01+02+12+34+012`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,5}, {0,1,2,6}, {0,1,2,5,6}, {0,1,2,7}, {0,1,2,5,7}, {0,1,2,5,6,7}, {4,8}, {0,2,3,5,8}, {1,4,5,6,7,8}, {4,9}, {0,1,4,6,9}, {2,3,7,9}, {4,8,9}, {1,2,5,6,8,9}, {0,3,4,5,7,8,9}, {0,1,2,3,6,7,10}, {4,8,10}, {0,2,5,8,10}, {1,3,4,5,6,7,8,10}, {4,9,10}, {0,1,3,4,6,9,10}, {2,7,9,10}, {4,8,9,10}, {1,2,3,5,6,8,9,10}, {0,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,5}, {1,3,6}, {0,3,4,5,6,7}, {0,1,8}, {4,5,8}, {0,4,6,8}, {0,7,8}, {0,5,7,8}, {0,3,4,6,7,8}, {4,9}, {3,5,9}, {1,3,4,6,9}, {0,3,4,5,6,7,9}, {0,1,4,8,9}, {4,5,8,9}, {0,6,8,9}, {1,2,3,7,8,9}, {1,2,3,5,7,8,9}, {0,3,4,6,7,8,9}, {0,3,4,10}, {0,3,5,10}, {0,1,3,6,10}, {5,6,7,10}, {1,8,10}, {0,3,5,8,10}, {4,6,8,10}, {0,1,2,3,7,8,10}, {0,1,2,3,5,7,8,10}, {6,7,8,10}, {1,2,9,10}, {1,2,5,9,10}, {0,1,3,4,6,9,10}, {5,6,7,9,10}, {1,4,8,9,10}, {0,3,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 93. `[[39,5,3]]` — T0·T1·T2·T3·T4·CS01·CS02·CS03·CS04·CS12·CCZ012

- gate `0+1+2+3+4+01+02+03+04+12+012`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,5}, {0,1,2,6}, {0,1,2,5,6}, {0,1,2,7}, {0,1,2,5,7}, {0,1,2,5,6,7}, {0,3,8}, {0,1,2,4,5,8}, {0,5,6,7,8}, {0,3,9}, {1,3,6,9}, {2,3,4,7,9}, {0,3,8,9}, {2,3,5,6,8,9}, {1,3,4,5,7,8,9}, {0,1,2,3,4,6,7,10}, {0,3,8,10}, {0,1,2,3,5,8,10}, {0,3,4,5,6,7,8,10}, {0,3,9,10}, {1,4,6,9,10}, {2,7,9,10}, {0,3,8,9,10}, {2,4,5,6,8,9,10}, {1,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,4,5}, {0,2,3,6}, {0,1,3,5,6,7}, {0,1,2,3,8}, {0,3,5,8}, {0,2,6,8}, {2,3,7,8}, {2,3,5,7,8}, {0,1,3,6,7,8}, {0,3,9}, {1,2,3,5,9}, {2,6,9}, {0,1,3,5,6,7,9}, {1,2,8,9}, {0,3,5,8,9}, {2,3,6,8,9}, {0,1,4,7,8,9}, {0,1,4,5,7,8,9}, {0,1,3,6,7,8,9}, {0,1,3,10}, {1,5,10}, {0,6,10}, {5,6,7,10}, {0,1,8,10}, {1,5,8,10}, {0,3,6,8,10}, {0,1,2,3,4,7,8,10}, {0,1,2,3,4,5,7,8,10}, {6,7,8,10}, {0,2,3,4,9,10}, {0,2,3,4,5,9,10}, {3,6,9,10}, {5,6,7,9,10}, {1,3,8,9,10}, {1,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 94. `[[39,5,3]]` — T0·T1·T2·T3·T4·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CCZ012·CCZ013·CCZ014

- gate `0+1+2+3+4+01+02+03+04+12+13+14+012+013+014`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,3,5}, {0,1,3,6}, {0,1,3,5,6}, {0,1,3,7}, {0,1,3,5,7}, {0,1,3,5,6,7}, {0,1,2,8}, {0,1,3,4,5,8}, {0,1,5,6,7,8}, {0,1,2,9}, {0,2,4,6,9}, {0,2,3,7,9}, {0,1,2,8,9}, {0,2,3,4,5,6,8,9}, {0,2,5,7,8,9}, {0,1,2,3,4,6,7,10}, {0,1,2,8,10}, {0,1,2,3,5,8,10}, {0,1,2,4,5,6,7,8,10}, {0,1,2,9,10}, {0,6,9,10}, {0,3,4,7,9,10}, {0,1,2,8,9,10}, {0,3,5,6,8,9,10}, {0,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,4,5}, {1,2,3,6}, {1,2,5,6,7}, {0,1,2,3,8}, {0,1,2,5,8}, {1,3,6,8}, {0,2,3,7,8}, {0,2,3,5,7,8}, {1,2,6,7,8}, {0,1,2,9}, {2,3,5,9}, {0,3,6,9}, {1,2,5,6,7,9}, {3,8,9}, {0,1,2,5,8,9}, {0,2,3,6,8,9}, {1,4,7,8,9}, {1,4,5,7,8,9}, {1,2,6,7,8,9}, {1,2,10}, {0,5,10}, {0,1,6,10}, {5,6,7,10}, {1,8,10}, {0,5,8,10}, {0,1,2,6,8,10}, {0,1,2,3,4,7,8,10}, {0,1,2,3,4,5,7,8,10}, {6,7,8,10}, {1,2,3,4,9,10}, {1,2,3,4,5,9,10}, {2,6,9,10}, {5,6,7,9,10}, {0,2,8,9,10}, {0,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 95. `[[39,5,3]]` — T0·T1·T2·T3·T4·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CCZ012·CCZ013·CCZ014·CCZ023·CCZ123

- gate `0+1+2+3+4+01+02+03+04+12+13+14+23+012+013+014+023+123`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,4,5}, {0,1,4,6}, {0,1,4,5,6}, {0,1,4,7}, {0,1,4,5,7}, {0,1,4,5,6,7}, {0,1,8}, {1,5,8}, {1,2,3,4,5,6,7,8}, {0,1,9}, {1,3,4,6,9}, {1,2,7,9}, {0,1,8,9}, {0,1,2,4,5,6,8,9}, {0,1,3,5,7,8,9}, {0,1,2,3,4,6,7,10}, {0,1,8,10}, {1,2,3,5,8,10}, {1,4,5,6,7,8,10}, {0,1,9,10}, {1,2,4,6,9,10}, {1,3,7,9,10}, {0,1,8,9,10}, {0,1,3,4,5,6,8,9,10}, {0,1,2,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,3,5}, {3,4,6}, {0,2,5,6,7}, {1,2,3,8}, {0,1,4,5,8}, {0,2,4,6,8}, {1,2,7,8}, {1,2,5,7,8}, {0,2,6,7,8}, {0,1,4,9}, {4,5,9}, {0,1,3,6,9}, {0,2,5,6,7,9}, {0,2,3,4,8,9}, {0,1,4,5,8,9}, {1,2,6,8,9}, {0,3,4,7,8,9}, {0,3,4,5,7,8,9}, {0,2,6,7,8,9}, {0,2,10}, {1,2,4,5,10}, {1,2,3,4,6,10}, {5,6,7,10}, {3,8,10}, {1,2,4,5,8,10}, {0,1,4,6,8,10}, {0,1,2,3,4,7,8,10}, {0,1,2,3,4,5,7,8,10}, {6,7,8,10}, {0,3,9,10}, {0,3,5,9,10}, {0,2,3,6,9,10}, {5,6,7,9,10}, {0,1,3,4,8,9,10}, {1,2,4,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 96. `[[39,5,3]]` — T0·T1·T2·T3·T4·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ123·CCZ124

- gate `0+1+2+3+4+01+02+03+04+12+13+14+23+24+012+013+014+023+024+123+124`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,4,5}, {0,1,2,4,6}, {0,1,2,4,5,6}, {0,1,2,4,7}, {0,1,2,4,5,7}, {0,1,2,4,5,6,7}, {0,1,2,3,8}, {1,2,5,8}, {1,2,4,5,6,7,8}, {0,1,2,3,9}, {2,3,4,6,9}, {2,3,7,9}, {0,1,2,3,8,9}, {0,2,3,4,5,6,8,9}, {0,2,3,5,7,8,9}, {0,1,2,3,4,6,7,10}, {0,1,2,3,8,10}, {1,2,3,5,8,10}, {1,2,3,4,5,6,7,8,10}, {0,1,2,3,9,10}, {2,4,6,9,10}, {2,7,9,10}, {0,1,2,3,8,9,10}, {0,2,4,5,6,8,9,10}, {0,2,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,4,5}, {1,3,6}, {1,2,3,5,6,7}, {0,1,3,8}, {0,1,2,3,5,8}, {1,2,6,8}, {0,3,7,8}, {0,3,5,7,8}, {1,2,3,6,7,8}, {0,1,2,3,9}, {3,5,9}, {0,2,6,9}, {1,2,3,5,6,7,9}, {2,8,9}, {0,1,2,3,5,8,9}, {0,3,6,8,9}, {1,2,4,7,8,9}, {1,2,4,5,7,8,9}, {1,2,3,6,7,8,9}, {1,2,3,10}, {0,5,10}, {0,1,6,10}, {5,6,7,10}, {1,8,10}, {0,5,8,10}, {0,1,2,3,6,8,10}, {0,1,2,3,4,7,8,10}, {0,1,2,3,4,5,7,8,10}, {6,7,8,10}, {1,2,3,4,9,10}, {1,2,3,4,5,9,10}, {2,3,6,9,10}, {5,6,7,9,10}, {0,2,3,8,9,10}, {0,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 97. `[[39,5,3]]` — T0·T1·T2·T3·T4·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CS34·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234

- gate `0+1+2+3+4+01+02+03+04+12+13+14+23+24+34+012+013+014+023+024+034+123+124+134+234`, `N = 12` (5 outputs + 7 checks), T-count 1, reduced degree 1, a3 = 55
- source: length40_m7_001, origin 65; rep_length40_m7_001.json

```text
[{0,1,2,3,4,6}, {0,2,3,5,6}, {3,5,7}, {0,1,5,8}, {0,2,3,5,7,8}, {0,1,2,3,9}, {0,1,2,3,6,9}, {0,2,3,4,5,6,9}, {3,5,7,9}, {0,1,5,8,9}, {0,2,3,4,5,7,8,9}, {1,10}, {1,6,10}, {4,5,6,10}, {3,5,7,10}, {0,1,5,8,10}, {4,5,7,8,10}, {1,4,9,10}, {1,4,6,9,10}, {5,6,9,10}, {3,5,7,9,10}, {0,1,5,8,9,10}, {5,7,8,9,10}, {0,1,3,5,11}, {0,2,3,5,7,11}, {0,2,3,5,8,11}, {5,7,8,11}, {0,1,3,5,9,11}, {0,2,3,4,5,7,9,11}, {0,2,3,4,5,8,9,11}, {5,7,8,9,11}, {0,1,3,5,10,11}, {4,5,7,10,11}, {4,5,8,10,11}, {5,7,8,10,11}, {0,1,3,5,9,10,11}, {5,7,9,10,11}, {5,8,9,10,11}, {5,7,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 119; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,3,4,5}, {0,6}, {1,2,3,5,6,7}, {0,1,2,3,8}, {5,8}, {1,2,3,6,8}, {2,3,7,8}, {2,3,5,7,8}, {1,2,3,6,7,8}, {0,2,9}, {0,2,5,9}, {0,6,9}, {1,2,3,5,6,7,9}, {0,1,2,3,8,9}, {5,8,9}, {1,2,3,6,8,9}, {1,2,4,7,8,9}, {1,2,4,5,7,8,9}, {1,2,3,6,7,8,9}, {0,3,10}, {0,3,5,10}, {0,1,2,3,6,10}, {5,6,7,10}, {0,8,10}, {1,2,3,5,8,10}, {6,8,10}, {1,3,4,7,8,10}, {1,3,4,5,7,8,10}, {6,7,8,10}, {0,1,4,9,10}, {0,1,4,5,9,10}, {0,1,2,3,6,9,10}, {5,6,7,9,10}, {0,8,9,10}, {1,2,3,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 98. `[[39,5,3]]` — T0·T1·T2·T3·T4·CS01·CS02·CS03·CS04·CS12·CS13·CS23·CCZ012·CCZ013·CCZ023·CCZ123

- gate `0+1+2+3+4+01+02+03+04+12+13+23+012+013+023+123`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,3,5}, {0,1,2,3,6}, {0,1,2,3,5,6}, {0,1,2,3,7}, {0,1,2,3,5,7}, {0,1,2,3,5,6,7}, {0,4,8}, {0,1,2,5,8}, {0,3,5,6,7,8}, {0,4,9}, {1,3,4,6,9}, {2,4,7,9}, {0,4,8,9}, {2,3,4,5,6,8,9}, {1,4,5,7,8,9}, {0,1,2,3,4,6,7,10}, {0,4,8,10}, {0,1,2,4,5,8,10}, {0,3,4,5,6,7,8,10}, {0,4,9,10}, {1,3,6,9,10}, {2,7,9,10}, {0,4,8,9,10}, {2,3,5,6,8,9,10}, {1,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,3,5}, {1,4,6}, {2,4,5,6,7}, {0,1,2,4,8}, {0,4,5,8}, {2,6,8}, {0,2,4,7,8}, {0,2,4,5,7,8}, {2,4,6,7,8}, {0,4,9}, {4,5,9}, {0,1,6,9}, {2,4,5,6,7,9}, {1,2,8,9}, {0,4,5,8,9}, {0,2,4,6,8,9}, {1,3,7,8,9}, {1,3,5,7,8,9}, {2,4,6,7,8,9}, {2,4,10}, {0,2,5,10}, {0,1,2,6,10}, {5,6,7,10}, {1,8,10}, {0,2,5,8,10}, {0,4,6,8,10}, {0,1,2,3,4,7,8,10}, {0,1,2,3,4,5,7,8,10}, {6,7,8,10}, {1,3,4,9,10}, {1,3,4,5,9,10}, {1,2,4,6,9,10}, {5,6,7,9,10}, {0,1,4,8,9,10}, {0,2,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 99. `[[39,5,3]]` — T0·T1·T2·T3·T4·CS01·CS02·CS03·CS04·CS12·CS34·CCZ012·CCZ034

- gate `0+1+2+3+4+01+02+03+04+12+34+012+034`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,3,4,5}, {0,3,4,6}, {0,3,4,5,6}, {0,3,4,7}, {0,3,4,5,7}, {0,3,4,5,6,7}, {0,1,2,8}, {0,2,3,4,5,8}, {0,2,5,6,7,8}, {0,1,2,9}, {1,2,3,6,9}, {1,2,4,7,9}, {0,1,2,8,9}, {1,4,5,6,8,9}, {1,3,5,7,8,9}, {0,1,2,3,4,6,7,10}, {0,1,2,8,10}, {0,1,3,4,5,8,10}, {0,1,5,6,7,8,10}, {0,1,2,9,10}, {3,6,9,10}, {4,7,9,10}, {0,1,2,8,9,10}, {2,4,5,6,8,9,10}, {2,3,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,3,4,5}, {1,3,6}, {1,2,4,5,6,7}, {0,1,3,4,8}, {0,1,2,5,8}, {4,6,8}, {0,1,2,4,7,8}, {0,1,2,4,5,7,8}, {1,2,4,6,7,8}, {0,1,2,9}, {1,2,5,9}, {0,2,3,6,9}, {1,2,4,5,6,7,9}, {2,3,4,8,9}, {0,1,2,5,8,9}, {0,1,2,4,6,8,9}, {3,7,8,9}, {3,5,7,8,9}, {1,2,4,6,7,8,9}, {1,2,4,10}, {0,4,5,10}, {0,2,3,4,6,10}, {5,6,7,10}, {2,3,8,10}, {0,4,5,8,10}, {0,1,2,6,8,10}, {0,1,2,3,4,7,8,10}, {0,1,2,3,4,5,7,8,10}, {6,7,8,10}, {1,2,3,9,10}, {1,2,3,5,9,10}, {1,3,4,6,9,10}, {5,6,7,9,10}, {0,1,3,8,9,10}, {0,4,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 100. `[[39,5,3]]` — T0·T1·T2·T3·T4·CS01·CS02·CS03·CS12·CS13·CS23·CCZ012·CCZ013·CCZ023·CCZ123

- gate `0+1+2+3+4+01+02+03+12+13+23+012+013+023+123`, `N = 11` (5 outputs + 6 checks), T-count 2, reduced degree 1, a3 = 123
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{4,5}, {2,3,6}, {1,2,3,5,6,7}, {1,8}, {5,8}, {0,6,8}, {0,7,8}, {0,5,7,8}, {1,2,3,6,7,8}, {9}, {1,2,5,9}, {0,2,6,9}, {1,2,3,5,6,7,9}, {0,1,3,8,9}, {5,8,9}, {3,6,8,9}, {0,1,2,4,7,8,9}, {0,1,2,4,5,7,8,9}, {1,2,3,6,7,8,9}, {1,2,3,10}, {0,1,2,5,10}, {2,6,10}, {5,6,7,10}, {1,3,8,10}, {1,2,3,5,8,10}, {0,3,6,8,10}, {1,2,4,7,8,10}, {1,2,4,5,7,8,10}, {6,7,8,10}, {0,4,9,10}, {0,4,5,9,10}, {0,2,3,6,9,10}, {5,6,7,9,10}, {0,1,8,9,10}, {1,2,3,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
```

### 101. `[[39,5,3]]` — T0·T1·T2·T3·T4·CS01·CS02·CS12·CCZ012

- gate `0+1+2+3+4+01+02+12+012`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,5}, {0,1,2,6}, {0,1,2,5,6}, {0,1,2,7}, {0,1,2,5,7}, {0,1,2,5,6,7}, {3,8}, {0,1,5,8}, {2,4,5,6,7,8}, {3,9}, {0,2,3,6,9}, {1,3,4,7,9}, {3,8,9}, {1,2,3,4,5,6,8,9}, {0,3,5,7,8,9}, {0,1,2,3,4,6,7,10}, {3,8,10}, {0,1,3,4,5,8,10}, {2,3,5,6,7,8,10}, {3,9,10}, {0,2,4,6,9,10}, {1,7,9,10}, {3,8,9,10}, {1,2,5,6,8,9,10}, {0,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,5}, {0,3,6}, {1,3,4,5,6,7}, {0,1,3,4,8}, {3,5,8}, {1,6,8}, {1,3,7,8}, {1,3,5,7,8}, {1,3,4,6,7,8}, {3,9}, {3,4,5,9}, {0,6,9}, {1,3,4,5,6,7,9}, {0,1,4,8,9}, {3,5,8,9}, {1,3,6,8,9}, {0,2,4,7,8,9}, {0,2,4,5,7,8,9}, {1,3,4,6,7,8,9}, {1,3,4,10}, {1,4,5,10}, {0,1,6,10}, {5,6,7,10}, {0,4,8,10}, {1,4,5,8,10}, {3,6,8,10}, {0,1,2,3,4,7,8,10}, {0,1,2,3,4,5,7,8,10}, {6,7,8,10}, {0,2,3,9,10}, {0,2,3,5,9,10}, {0,1,3,6,9,10}, {5,6,7,9,10}, {0,3,4,8,9,10}, {1,4,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 102. `[[39,5,3]]` — T0·T1·T2·T3·T4·CS01·CS02·CS12·CS34·CCZ012

- gate `0+1+2+3+4+01+02+12+34+012`, `N = 11` (5 outputs + 6 checks), T-count 2, reduced degree 1, a3 = 123
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{3,4,5}, {2,3,6}, {1,2,3,5,6,7}, {1,8}, {5,8}, {0,3,6,8}, {0,3,7,8}, {0,3,5,7,8}, {1,2,3,6,7,8}, {9}, {1,2,3,4,5,9}, {0,2,4,6,9}, {1,2,3,5,6,7,9}, {0,1,3,4,8,9}, {5,8,9}, {4,6,8,9}, {0,1,2,3,7,8,9}, {0,1,2,3,5,7,8,9}, {1,2,3,6,7,8,9}, {1,2,3,10}, {0,1,2,4,5,10}, {2,3,4,6,10}, {5,6,7,10}, {1,4,8,10}, {1,2,3,5,8,10}, {0,3,4,6,8,10}, {1,2,7,8,10}, {1,2,5,7,8,10}, {6,7,8,10}, {0,4,9,10}, {0,4,5,9,10}, {0,2,6,9,10}, {5,6,7,9,10}, {0,1,3,8,9,10}, {1,2,3,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
```

### 103. `[[39,5,3]]` — T0·T1·T2·T3·T4·CS01·CS23

- gate `0+1+2+3+4+01+23`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{4,5}, {4,6}, {4,5,6}, {4,7}, {4,5,7}, {4,5,6,7}, {0,1,8}, {1,4,5,8}, {1,2,3,5,6,7,8}, {0,1,9}, {0,1,3,6,9}, {0,1,2,4,7,9}, {0,1,8,9}, {0,2,4,5,6,8,9}, {0,3,5,7,8,9}, {0,1,2,3,4,6,7,10}, {0,1,8,10}, {0,2,3,4,5,8,10}, {0,5,6,7,8,10}, {0,1,9,10}, {2,6,9,10}, {3,4,7,9,10}, {0,1,8,9,10}, {1,3,4,5,6,8,9,10}, {1,2,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{2,3,5}, {0,1,3,4,6}, {0,2,5,6,7}, {0,2,3,4,8}, {0,1,5,8}, {1,2,4,6,8}, {0,2,4,7,8}, {0,2,4,5,7,8}, {0,2,6,7,8}, {0,1,9}, {0,1,4,5,9}, {3,4,6,9}, {0,2,5,6,7,9}, {1,2,3,4,8,9}, {0,1,5,8,9}, {0,2,4,6,8,9}, {1,3,7,8,9}, {1,3,5,7,8,9}, {0,2,6,7,8,9}, {0,2,10}, {1,2,5,10}, {1,2,3,6,10}, {5,6,7,10}, {3,8,10}, {1,2,5,8,10}, {0,1,6,8,10}, {0,1,2,3,4,7,8,10}, {0,1,2,3,4,5,7,8,10}, {6,7,8,10}, {0,3,4,9,10}, {0,3,4,5,9,10}, {0,2,3,6,9,10}, {5,6,7,9,10}, {0,1,3,8,9,10}, {1,2,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 104. `[[39,5,3]]` — T0·T1·T2·T4·CS01·CS02·CS03·CS12·CS13·CS23·CCZ012·CCZ013·CCZ023·CCZ123

- gate `0+1+2+4+01+02+03+12+13+23+012+013+023+123`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,3,5}, {0,1,2,3,6}, {0,1,2,3,5,6}, {0,1,2,3,7}, {0,1,2,3,5,7}, {0,1,2,3,5,6,7}, {3,8}, {0,1,3,4,5,8}, {2,5,6,7,8}, {3,9}, {1,3,4,6,9}, {0,2,7,9}, {3,8,9}, {0,4,5,6,8,9}, {1,2,3,5,7,8,9}, {0,1,2,4,6,7,10}, {3,8,10}, {0,1,5,8,10}, {2,3,4,5,6,7,8,10}, {3,9,10}, {1,6,9,10}, {0,2,3,4,7,9,10}, {3,8,9,10}, {0,3,5,6,8,9,10}, {1,2,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{4,5}, {0,1,6}, {0,3,5,6,7}, {0,2,8}, {0,1,2,3,5,8}, {1,2,3,6,8}, {0,7,8}, {0,5,7,8}, {0,3,6,7,8}, {0,1,2,3,9}, {0,1,2,5,9}, {2,3,6,9}, {0,3,5,6,7,9}, {1,3,8,9}, {0,1,2,3,5,8,9}, {0,6,8,9}, {1,2,4,7,8,9}, {1,2,4,5,7,8,9}, {0,3,6,7,8,9}, {0,3,10}, {1,2,5,10}, {1,6,10}, {5,6,7,10}, {2,8,10}, {1,2,5,8,10}, {0,1,2,3,6,8,10}, {0,1,2,4,7,8,10}, {0,1,2,4,5,7,8,10}, {6,7,8,10}, {0,4,9,10}, {0,4,5,9,10}, {0,2,3,6,9,10}, {5,6,7,9,10}, {0,1,3,8,9,10}, {1,2,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 105. `[[39,5,3]]` — T0·T1·T2·T4·CS01·CS02·CS03·CS12·CS13·CS23·CS34·CCZ012·CCZ013·CCZ023·CCZ123

- gate `0+1+2+4+01+02+03+12+13+23+34+012+013+023+123`, `N = 11` (5 outputs + 6 checks), T-count 2, reduced degree 1, a3 = 123
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,5}, {0,3,6}, {0,5,6,7}, {3,8}, {5,8}, {0,3,4,6,8}, {0,3,4,7,8}, {0,3,4,5,7,8}, {0,6,7,8}, {9}, {0,1,5,9}, {1,4,6,9}, {0,5,6,7,9}, {0,1,4,8,9}, {5,8,9}, {1,6,8,9}, {0,2,4,7,8,9}, {0,2,4,5,7,8,9}, {0,6,7,8,9}, {0,10}, {1,3,4,5,10}, {0,1,3,6,10}, {5,6,7,10}, {1,3,8,10}, {0,5,8,10}, {0,1,3,4,6,8,10}, {2,3,7,8,10}, {2,3,5,7,8,10}, {6,7,8,10}, {1,2,4,9,10}, {1,2,4,5,9,10}, {4,6,9,10}, {5,6,7,9,10}, {0,4,8,9,10}, {0,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
```

### 106. `[[39,5,3]]` — T0·T1·T2·T4·CS01·CS02·CS03·CS12·CS13·CS24·CCZ012·CCZ013·CCZ023·CCZ123

- gate `0+1+2+4+01+02+03+12+13+24+012+013+023+123`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,3,5}, {0,1,2,3,6}, {0,1,2,3,5,6}, {0,1,2,3,7}, {0,1,2,3,5,7}, {0,1,2,3,5,6,7}, {2,4,8}, {0,1,2,5,8}, {2,5,6,7,8}, {2,4,9}, {0,2,3,6,9}, {1,2,3,7,9}, {2,4,8,9}, {1,2,5,6,8,9}, {0,2,5,7,8,9}, {0,1,2,4,6,7,10}, {2,4,8,10}, {0,1,2,3,4,5,8,10}, {2,3,4,5,6,7,8,10}, {2,4,9,10}, {0,2,4,6,9,10}, {1,2,4,7,9,10}, {2,4,8,9,10}, {1,2,3,4,5,6,8,9,10}, {0,2,3,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{2,4,5}, {0,1,4,6}, {0,5,6,7}, {1,2,3,4,8}, {2,3,5,8}, {1,6,8}, {1,2,3,7,8}, {1,2,3,5,7,8}, {0,6,7,8}, {2,3,9}, {0,1,5,9}, {0,1,2,3,4,6,9}, {0,5,6,7,9}, {1,4,8,9}, {2,3,5,8,9}, {1,2,3,6,8,9}, {0,3,4,7,8,9}, {0,3,4,5,7,8,9}, {0,6,7,8,9}, {0,10}, {0,2,3,5,10}, {0,2,3,4,6,10}, {5,6,7,10}, {4,8,10}, {0,2,3,5,8,10}, {2,3,6,8,10}, {0,1,2,4,7,8,10}, {0,1,2,4,5,7,8,10}, {6,7,8,10}, {1,3,4,9,10}, {1,3,4,5,9,10}, {0,4,6,9,10}, {5,6,7,9,10}, {2,3,4,8,9,10}, {0,2,3,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 107. `[[39,5,3]]` — T0·T1·T2·T4·CS01·CS02·CS03·CS12·CS13·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234

- gate `0+1+2+4+01+02+03+12+13+24+34+012+013+023+123+234`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{2,3,4,5}, {2,3,4,6}, {2,3,4,5,6}, {2,3,4,7}, {2,3,4,5,7}, {2,3,4,5,6,7}, {2,8}, {1,2,3,4,5,8}, {0,2,3,5,6,7,8}, {2,9}, {1,2,3,6,9}, {0,2,3,4,7,9}, {2,8,9}, {0,1,2,3,4,5,6,8,9}, {2,3,5,7,8,9}, {0,1,2,4,6,7,10}, {2,8,10}, {0,2,4,5,8,10}, {1,2,5,6,7,8,10}, {2,9,10}, {0,2,6,9,10}, {1,2,4,7,9,10}, {2,8,9,10}, {2,4,5,6,8,9,10}, {0,1,2,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,3,5}, {4,6}, {0,3,4,5,6,7}, {0,2,4,8}, {2,3,4,5,8}, {0,6,8}, {0,2,3,4,7,8}, {0,2,3,4,5,7,8}, {0,3,4,6,7,8}, {2,3,4,9}, {3,4,5,9}, {2,3,6,9}, {0,3,4,5,6,7,9}, {0,3,8,9}, {2,3,4,5,8,9}, {0,2,3,4,6,8,9}, {1,3,7,8,9}, {1,3,5,7,8,9}, {0,3,4,6,7,8,9}, {0,3,4,10}, {0,2,5,10}, {0,2,3,6,10}, {5,6,7,10}, {3,8,10}, {0,2,5,8,10}, {2,3,4,6,8,10}, {0,1,2,4,7,8,10}, {0,1,2,4,5,7,8,10}, {6,7,8,10}, {1,4,9,10}, {1,4,5,9,10}, {0,4,6,9,10}, {5,6,7,9,10}, {2,4,8,9,10}, {0,2,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 108. `[[39,5,3]]` — T0·T1·T2·T4·CS01·CS02·CS03·CS12·CS14·CS24·CCZ012·CCZ013·CCZ023·CCZ124

- gate `0+1+2+4+01+02+03+12+14+24+012+013+023+124`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{1,2,3,5}, {1,2,3,6}, {1,2,3,5,6}, {1,2,3,7}, {1,2,3,5,7}, {1,2,3,5,6,7}, {1,2,4,8}, {1,2,5,8}, {0,1,2,5,6,7,8}, {1,2,4,9}, {0,2,3,6,9}, {2,3,7,9}, {1,2,4,8,9}, {2,5,6,8,9}, {0,2,5,7,8,9}, {0,1,2,4,6,7,10}, {1,2,4,8,10}, {0,1,2,3,4,5,8,10}, {1,2,3,4,5,6,7,8,10}, {1,2,4,9,10}, {2,4,6,9,10}, {0,2,4,7,9,10}, {1,2,4,8,9,10}, {0,2,3,4,5,6,8,9,10}, {2,3,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,3,5}, {0,1,3,4,6}, {1,3,5,6,7}, {0,1,2,3,4,8}, {1,2,3,5,8}, {1,4,6,8}, {2,3,4,7,8}, {2,3,4,5,7,8}, {1,3,6,7,8}, {1,2,3,9}, {3,4,5,9}, {0,2,4,6,9}, {1,3,5,6,7,9}, {0,4,8,9}, {1,2,3,5,8,9}, {2,3,4,6,8,9}, {0,1,3,7,8,9}, {0,1,3,5,7,8,9}, {1,3,6,7,8,9}, {1,3,10}, {2,5,10}, {0,1,2,6,10}, {5,6,7,10}, {0,1,8,10}, {2,5,8,10}, {1,2,3,6,8,10}, {0,1,2,4,7,8,10}, {0,1,2,4,5,7,8,10}, {6,7,8,10}, {0,1,4,9,10}, {0,1,4,5,9,10}, {0,3,6,9,10}, {5,6,7,9,10}, {0,2,3,8,9,10}, {2,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 109. `[[39,5,3]]` — T0·T1·T2·T4·CS01·CS02·CS03·CS12·CS14·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ124·CCZ134·CCZ234

- gate `0+1+2+4+01+02+03+12+14+24+34+012+013+023+124+134+234`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{1,2,3,4,5}, {1,2,3,4,6}, {1,2,3,4,5,6}, {1,2,3,4,7}, {1,2,3,4,5,7}, {1,2,3,4,5,6,7}, {0,1,2,3,8}, {1,3,4,5,8}, {1,5,6,7,8}, {0,1,2,3,9}, {0,1,3,4,6,9}, {0,1,7,9}, {0,1,2,3,8,9}, {0,1,2,5,6,8,9}, {0,1,2,3,4,5,7,8,9}, {0,1,2,4,6,7,10}, {0,1,2,3,8,10}, {0,1,4,5,8,10}, {0,1,3,5,6,7,8,10}, {0,1,2,3,9,10}, {1,4,6,9,10}, {1,3,7,9,10}, {0,1,2,3,8,9,10}, {1,2,3,5,6,8,9,10}, {1,2,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{1,2,5}, {0,6}, {0,2,3,4,5,6,7}, {0,1,4,8}, {0,1,2,3,5,8}, {2,3,6,8}, {0,1,7,8}, {0,1,5,7,8}, {0,2,3,4,6,7,8}, {0,1,2,3,9}, {0,4,5,9}, {1,2,3,6,9}, {0,2,3,4,5,6,7,9}, {2,3,4,8,9}, {0,1,2,3,5,8,9}, {0,1,6,8,9}, {2,4,7,8,9}, {2,4,5,7,8,9}, {0,2,3,4,6,7,8,9}, {0,2,3,4,10}, {1,4,5,10}, {1,6,10}, {5,6,7,10}, {4,8,10}, {1,4,5,8,10}, {0,1,2,3,6,8,10}, {0,1,2,4,7,8,10}, {0,1,2,4,5,7,8,10}, {6,7,8,10}, {0,2,9,10}, {0,2,5,9,10}, {0,2,3,6,9,10}, {5,6,7,9,10}, {0,1,2,3,4,8,9,10}, {1,4,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 110. `[[39,5,3]]` — T0·T1·T2·T4·CS01·CS23·CS34

- gate `0+1+2+4+01+23+34`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,5}, {0,1,6}, {0,1,5,6}, {0,1,7}, {0,1,5,7}, {0,1,5,6,7}, {2,3,8}, {1,4,5,8}, {0,3,5,6,7,8}, {2,3,9}, {2,3,4,6,9}, {0,1,2,7,9}, {2,3,8,9}, {1,2,4,5,6,8,9}, {0,2,3,5,7,8,9}, {0,1,2,4,6,7,10}, {2,3,8,10}, {1,2,5,8,10}, {0,2,3,4,5,6,7,8,10}, {2,3,9,10}, {3,6,9,10}, {0,1,4,7,9,10}, {2,3,8,9,10}, {1,5,6,8,9,10}, {0,3,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{3,4,5}, {1,2,3,6}, {0,2,5,6,7}, {0,1,2,8}, {2,3,5,8}, {1,3,6,8}, {1,2,7,8}, {1,2,5,7,8}, {0,2,6,7,8}, {2,3,9}, {0,1,2,3,5,9}, {1,6,9}, {0,2,5,6,7,9}, {0,1,3,8,9}, {2,3,5,8,9}, {1,2,6,8,9}, {0,4,7,8,9}, {0,4,5,7,8,9}, {0,2,6,7,8,9}, {0,2,10}, {0,3,5,10}, {3,6,10}, {5,6,7,10}, {0,8,10}, {0,3,5,8,10}, {2,3,6,8,10}, {0,1,2,4,7,8,10}, {0,1,2,4,5,7,8,10}, {6,7,8,10}, {1,2,3,4,9,10}, {1,2,3,4,5,9,10}, {2,6,9,10}, {5,6,7,9,10}, {0,2,3,8,9,10}, {0,3,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 111. `[[39,5,3]]` — T0·T1·T3·CS01·CS02·CS12·CS23·CS24·CS34·CCZ012·CCZ234

- gate `0+1+3+01+02+12+23+24+34+012+234`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,5}, {0,1,2,6}, {0,1,2,5,6}, {0,1,2,7}, {0,1,2,5,7}, {0,1,2,5,6,7}, {4,8}, {0,1,5,8}, {3,4,5,6,7,8}, {4,9}, {0,2,4,6,9}, {1,2,3,7,9}, {4,8,9}, {1,3,5,6,8,9}, {0,4,5,7,8,9}, {0,1,3,6,7,10}, {4,8,10}, {0,1,2,3,5,8,10}, {2,4,5,6,7,8,10}, {4,9,10}, {0,3,4,6,9,10}, {1,7,9,10}, {4,8,9,10}, {1,2,5,6,8,9,10}, {0,2,3,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{2,3,4,5}, {0,2,3,4,6}, {1,5,6,7}, {0,1,2,3,8}, {4,5,8}, {0,2,4,6,8}, {0,2,7,8}, {0,2,5,7,8}, {1,6,7,8}, {4,9}, {0,1,2,4,5,9}, {0,2,3,6,9}, {1,5,6,7,9}, {0,1,2,3,4,8,9}, {4,5,8,9}, {0,2,6,8,9}, {1,2,3,7,8,9}, {1,2,3,5,7,8,9}, {1,6,7,8,9}, {1,10}, {1,4,5,10}, {3,4,6,10}, {5,6,7,10}, {1,3,8,10}, {1,4,5,8,10}, {4,6,8,10}, {0,1,3,7,8,10}, {0,1,3,5,7,8,10}, {6,7,8,10}, {0,3,4,9,10}, {0,3,4,5,9,10}, {3,6,9,10}, {5,6,7,9,10}, {1,3,4,8,9,10}, {1,4,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 112. `[[39,5,3]]` — T0·T1·T3·T4·CS01·CS02·CS12·CS23·CCZ012

- gate `0+1+3+4+01+02+12+23+012`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{4,5}, {4,6}, {4,5,6}, {4,7}, {4,5,7}, {4,5,6,7}, {0,1,2,8}, {1,2,4,5,8}, {1,3,5,6,7,8}, {0,1,2,9}, {0,3,6,9}, {0,2,4,7,9}, {0,1,2,8,9}, {0,1,4,5,6,8,9}, {0,1,2,3,5,7,8,9}, {0,1,3,4,6,7,10}, {0,1,2,8,10}, {0,2,3,4,5,8,10}, {0,5,6,7,8,10}, {0,1,2,9,10}, {1,6,9,10}, {1,2,3,4,7,9,10}, {0,1,2,8,9,10}, {3,4,5,6,8,9,10}, {2,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{2,3,5}, {0,1,2,3,4,6}, {0,2,5,6,7}, {0,2,3,4,8}, {0,1,2,5,8}, {1,4,6,8}, {0,2,4,7,8}, {0,2,4,5,7,8}, {0,2,6,7,8}, {0,1,2,9}, {0,1,2,4,5,9}, {3,4,6,9}, {0,2,5,6,7,9}, {1,3,4,8,9}, {0,1,2,5,8,9}, {0,2,4,6,8,9}, {1,2,3,7,8,9}, {1,2,3,5,7,8,9}, {0,2,6,7,8,9}, {0,2,10}, {1,5,10}, {1,3,6,10}, {5,6,7,10}, {3,8,10}, {1,5,8,10}, {0,1,2,6,8,10}, {0,1,3,4,7,8,10}, {0,1,3,4,5,7,8,10}, {6,7,8,10}, {0,3,4,9,10}, {0,3,4,5,9,10}, {0,2,3,6,9,10}, {5,6,7,9,10}, {0,1,2,3,8,9,10}, {1,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 113. `[[39,5,3]]` — T0·T1·T3·T4·CS01·CS02·CS12·CS23·CS24·CS34·CCZ012·CCZ234

- gate `0+1+3+4+01+02+12+23+24+34+012+234`, `N = 11` (5 outputs + 6 checks), T-count 2, reduced degree 1, a3 = 123
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{2,3,4,5}, {1,2,3,6}, {0,1,2,3,5,6,7}, {0,8}, {5,8}, {3,6,8}, {3,7,8}, {3,5,7,8}, {0,1,2,3,6,7,8}, {9}, {0,1,2,3,4,5,9}, {1,2,4,6,9}, {0,1,2,3,5,6,7,9}, {0,3,4,8,9}, {5,8,9}, {4,6,8,9}, {0,1,3,7,8,9}, {0,1,3,5,7,8,9}, {0,1,2,3,6,7,8,9}, {0,1,2,3,10}, {0,1,2,4,5,10}, {1,2,3,4,6,10}, {5,6,7,10}, {0,4,8,10}, {0,1,2,3,5,8,10}, {3,4,6,8,10}, {0,1,7,8,10}, {0,1,5,7,8,10}, {6,7,8,10}, {2,4,9,10}, {2,4,5,9,10}, {1,2,6,9,10}, {5,6,7,9,10}, {0,3,8,9,10}, {0,1,2,3,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
```

### 114. `[[39,5,3]]` — T0·T1·T3·T4·CS01·CS02·CS12·CS34·CCZ012

- gate `0+1+3+4+01+02+12+34+012`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,5}, {0,1,2,6}, {0,1,2,5,6}, {0,1,2,7}, {0,1,2,5,7}, {0,1,2,5,6,7}, {2,8}, {0,1,2,4,5,8}, {3,5,6,7,8}, {2,9}, {0,2,6,9}, {1,3,4,7,9}, {2,8,9}, {1,3,5,6,8,9}, {0,2,4,5,7,8,9}, {0,1,3,4,6,7,10}, {2,8,10}, {0,1,3,5,8,10}, {2,4,5,6,7,8,10}, {2,9,10}, {0,3,4,6,9,10}, {1,2,7,9,10}, {2,8,9,10}, {1,2,4,5,6,8,9,10}, {0,3,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{3,4,5}, {1,6}, {0,2,3,5,6,7}, {0,1,3,8}, {2,5,8}, {1,2,3,6,8}, {1,3,7,8}, {1,3,5,7,8}, {0,2,3,6,7,8}, {2,9}, {0,1,5,9}, {1,2,6,9}, {0,2,3,5,6,7,9}, {0,1,2,3,8,9}, {2,5,8,9}, {1,3,6,8,9}, {0,4,7,8,9}, {0,4,5,7,8,9}, {0,2,3,6,7,8,9}, {0,2,3,10}, {0,3,5,10}, {3,6,10}, {5,6,7,10}, {0,8,10}, {0,3,5,8,10}, {2,6,8,10}, {0,1,3,4,7,8,10}, {0,1,3,4,5,7,8,10}, {6,7,8,10}, {1,4,9,10}, {1,4,5,9,10}, {2,3,6,9,10}, {5,6,7,9,10}, {0,2,8,9,10}, {0,3,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 115. `[[39,5,3]]` — T0·T1·T3·T4·CS01·CS02·CS13·CS14·CS23·CCZ012·CCZ123

- gate `0+1+3+4+01+02+13+14+23+012+123`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{1,2,3,5}, {1,2,3,6}, {1,2,3,5,6}, {1,2,3,7}, {1,2,3,5,7}, {1,2,3,5,6,7}, {1,4,8}, {1,3,5,8}, {0,1,5,6,7,8}, {1,4,9}, {0,1,2,4,6,9}, {1,2,3,4,7,9}, {1,4,8,9}, {1,3,4,5,6,8,9}, {0,1,4,5,7,8,9}, {0,1,3,4,6,7,10}, {1,4,8,10}, {0,1,2,3,4,5,8,10}, {1,2,4,5,6,7,8,10}, {1,4,9,10}, {1,6,9,10}, {0,1,3,7,9,10}, {1,4,8,9,10}, {0,1,2,3,5,6,8,9,10}, {1,2,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,5}, {0,2,3,4,6}, {4,5,6,7}, {0,1,2,3,4,8}, {1,4,5,8}, {2,3,6,8}, {1,2,3,4,7,8}, {1,2,3,4,5,7,8}, {4,6,7,8}, {1,4,9}, {2,3,4,5,9}, {0,1,2,3,6,9}, {4,5,6,7,9}, {0,2,3,8,9}, {1,4,5,8,9}, {1,2,3,4,6,8,9}, {0,2,7,8,9}, {0,2,5,7,8,9}, {4,6,7,8,9}, {4,10}, {1,5,10}, {0,1,6,10}, {5,6,7,10}, {0,8,10}, {1,5,8,10}, {1,4,6,8,10}, {0,1,3,4,7,8,10}, {0,1,3,4,5,7,8,10}, {6,7,8,10}, {0,3,4,9,10}, {0,3,4,5,9,10}, {0,4,6,9,10}, {5,6,7,9,10}, {0,1,4,8,9,10}, {1,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 116. `[[39,5,3]]` — T0·T1·T4·CS01·CS02·CS03·CS12·CS13·CCZ012·CCZ013·CCZ023·CCZ123

- gate `0+1+4+01+02+03+12+13+012+013+023+123`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{2,3,5}, {2,3,6}, {2,3,5,6}, {2,3,7}, {2,3,5,7}, {2,3,5,6,7}, {4,8}, {1,2,3,5,8}, {0,2,3,5,6,7,8}, {4,9}, {1,2,4,6,9}, {0,2,4,7,9}, {4,8,9}, {0,1,2,4,5,6,8,9}, {2,4,5,7,8,9}, {0,1,4,6,7,10}, {4,8,10}, {0,4,5,8,10}, {1,4,5,6,7,8,10}, {4,9,10}, {0,3,6,9,10}, {1,3,7,9,10}, {4,8,9,10}, {3,5,6,8,9,10}, {0,1,3,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,3,5}, {3,4,6}, {0,3,4,5,6,7}, {0,4,8}, {4,5,8}, {0,2,6,8}, {0,2,4,7,8}, {0,2,4,5,7,8}, {0,3,4,6,7,8}, {4,9}, {2,3,4,5,9}, {3,6,9}, {0,3,4,5,6,7,9}, {0,8,9}, {4,5,8,9}, {0,2,4,6,8,9}, {1,2,7,8,9}, {1,2,5,7,8,9}, {0,3,4,6,7,8,9}, {0,3,4,10}, {0,3,5,10}, {0,2,3,6,10}, {5,6,7,10}, {2,8,10}, {0,3,5,8,10}, {4,6,8,10}, {0,1,4,7,8,10}, {0,1,4,5,7,8,10}, {6,7,8,10}, {1,3,4,9,10}, {1,3,4,5,9,10}, {0,2,3,4,6,9,10}, {5,6,7,9,10}, {2,4,8,9,10}, {0,3,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 117. `[[39,5,3]]` — T0·T1·T4·CS01·CS02·CS03·CS12·CS13·CS23·CS24·CCZ012·CCZ013·CCZ023·CCZ123

- gate `0+1+4+01+02+03+12+13+23+24+012+013+023+123`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{2,4,5}, {2,4,6}, {2,4,5,6}, {2,4,7}, {2,4,5,7}, {2,4,5,6,7}, {3,8}, {1,2,4,5,8}, {0,2,3,5,6,7,8}, {3,9}, {1,2,3,6,9}, {0,2,4,7,9}, {3,8,9}, {0,1,2,4,5,6,8,9}, {2,3,5,7,8,9}, {0,1,4,6,7,10}, {3,8,10}, {0,4,5,8,10}, {1,3,5,6,7,8,10}, {3,9,10}, {0,3,6,9,10}, {1,4,7,9,10}, {3,8,9,10}, {4,5,6,8,9,10}, {0,1,3,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,3,5}, {3,4,6}, {0,5,6,7}, {0,4,8}, {3,5,8}, {0,2,3,4,6,8}, {0,2,4,7,8}, {0,2,4,5,7,8}, {0,6,7,8}, {3,9}, {2,3,4,5,9}, {4,6,9}, {0,5,6,7,9}, {0,3,4,8,9}, {3,5,8,9}, {0,2,4,6,8,9}, {1,2,7,8,9}, {1,2,5,7,8,9}, {0,6,7,8,9}, {0,10}, {0,3,5,10}, {0,2,3,6,10}, {5,6,7,10}, {2,8,10}, {0,3,5,8,10}, {3,6,8,10}, {0,1,4,7,8,10}, {0,1,4,5,7,8,10}, {6,7,8,10}, {1,3,4,9,10}, {1,3,4,5,9,10}, {0,2,6,9,10}, {5,6,7,9,10}, {2,3,8,9,10}, {0,3,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 118. `[[39,5,3]]` — T0·T1·T4·CS01·CS02·CS03·CS12·CS13·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234

- gate `0+1+4+01+02+03+12+13+24+34+012+013+023+123+234`, `N = 11` (5 outputs + 6 checks), T-count 2, reduced degree 1, a3 = 123
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{2,3,4,5}, {4,6}, {0,3,4,5,6,7}, {0,3,8}, {5,8}, {1,2,4,6,8}, {1,2,4,7,8}, {1,2,4,5,7,8}, {0,3,4,6,7,8}, {9}, {0,1,2,4,5,9}, {3,6,9}, {0,3,4,5,6,7,9}, {0,4,8,9}, {5,8,9}, {1,2,3,6,8,9}, {0,2,3,4,7,8,9}, {0,2,3,4,5,7,8,9}, {0,3,4,6,7,8,9}, {0,3,4,10}, {0,5,10}, {1,2,3,4,6,10}, {5,6,7,10}, {0,1,2,8,10}, {0,3,4,5,8,10}, {3,4,6,8,10}, {0,1,3,7,8,10}, {0,1,3,5,7,8,10}, {6,7,8,10}, {1,3,9,10}, {1,3,5,9,10}, {1,2,6,9,10}, {5,6,7,9,10}, {0,1,2,3,4,8,9,10}, {0,3,4,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
```

### 119. `[[39,5,3]]` — T0·T1·T4·CS01·CS02·CS03·CS14·CCZ012·CCZ013·CCZ023

- gate `0+1+4+01+02+03+14+012+013+023`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,3,5}, {0,1,2,3,6}, {0,1,2,3,5,6}, {0,1,2,3,7}, {0,1,2,3,5,7}, {0,1,2,3,5,6,7}, {1,4,8}, {0,1,2,5,8}, {1,2,5,6,7,8}, {1,4,9}, {1,2,3,4,6,9}, {0,1,2,3,4,7,9}, {1,4,8,9}, {0,1,2,4,5,6,8,9}, {1,2,4,5,7,8,9}, {0,1,4,6,7,10}, {1,4,8,10}, {0,1,3,4,5,8,10}, {1,3,4,5,6,7,8,10}, {1,4,9,10}, {1,6,9,10}, {0,1,7,9,10}, {1,4,8,9,10}, {0,1,3,5,6,8,9,10}, {1,3,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{1,4,5}, {0,2,6}, {4,5,6,7}, {0,1,3,4,8}, {1,2,3,5,8}, {0,4,6,8}, {0,1,2,3,4,7,8}, {0,1,2,3,4,5,7,8}, {4,6,7,8}, {1,2,3,9}, {0,5,9}, {0,1,3,6,9}, {4,5,6,7,9}, {0,2,4,8,9}, {1,2,3,5,8,9}, {0,1,2,3,4,6,8,9}, {2,3,7,8,9}, {2,3,5,7,8,9}, {4,6,7,8,9}, {4,10}, {1,2,3,4,5,10}, {1,3,4,6,10}, {5,6,7,10}, {2,8,10}, {1,2,3,4,5,8,10}, {1,2,3,6,8,10}, {0,1,4,7,8,10}, {0,1,4,5,7,8,10}, {6,7,8,10}, {0,2,3,9,10}, {0,2,3,5,9,10}, {2,4,6,9,10}, {5,6,7,9,10}, {1,3,8,9,10}, {1,2,3,4,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 120. `[[39,5,3]]` — T0·T1·T4·CS01·CS02·CS03·CS14·CS23·CS24·CCZ012·CCZ013·CCZ023·CCZ123·CCZ124

- gate `0+1+4+01+02+03+14+23+24+012+013+023+123+124`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{1,3,5}, {1,3,6}, {1,3,5,6}, {1,3,7}, {1,3,5,7}, {1,3,5,6,7}, {0,1,2,3,8}, {1,3,4,5,8}, {1,2,5,6,7,8}, {0,1,2,3,9}, {0,2,3,4,6,9}, {0,7,9}, {0,1,2,3,8,9}, {0,4,5,6,8,9}, {0,2,3,5,7,8,9}, {0,1,4,6,7,10}, {0,1,2,3,8,10}, {0,1,5,8,10}, {0,1,2,3,4,5,6,7,8,10}, {0,1,2,3,9,10}, {2,6,9,10}, {3,4,7,9,10}, {0,1,2,3,8,9,10}, {3,5,6,8,9,10}, {2,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{1,2,4,5}, {0,1,2,6}, {0,1,3,5,6,7}, {0,1,8}, {0,1,2,3,5,8}, {1,2,3,6,8}, {0,7,8}, {0,5,7,8}, {0,1,3,6,7,8}, {0,1,2,3,9}, {0,2,5,9}, {3,6,9}, {0,1,3,5,6,7,9}, {2,3,8,9}, {0,1,2,3,5,8,9}, {0,6,8,9}, {1,4,7,8,9}, {1,4,5,7,8,9}, {0,1,3,6,7,8,9}, {0,1,3,10}, {2,5,10}, {1,2,6,10}, {5,6,7,10}, {1,8,10}, {2,5,8,10}, {0,1,2,3,6,8,10}, {0,1,4,7,8,10}, {0,1,4,5,7,8,10}, {6,7,8,10}, {0,1,2,4,9,10}, {0,1,2,4,5,9,10}, {0,3,6,9,10}, {5,6,7,9,10}, {0,2,3,8,9,10}, {2,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 121. `[[39,5,3]]` — T0·T1·T4·CS01·CS02·CS03·CS14·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ124·CCZ134·CCZ234

- gate `0+1+4+01+02+03+14+24+34+012+013+023+124+134+234`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,3,5}, {0,1,2,3,6}, {0,1,2,3,5,6}, {0,1,2,3,7}, {0,1,2,3,5,7}, {0,1,2,3,5,6,7}, {1,8}, {0,1,2,5,8}, {1,2,4,5,6,7,8}, {1,9}, {0,3,6,9}, {3,4,7,9}, {1,8,9}, {4,5,6,8,9}, {0,5,7,8,9}, {0,1,4,6,7,10}, {1,8,10}, {0,1,3,4,5,8,10}, {1,3,5,6,7,8,10}, {1,9,10}, {0,2,4,6,9,10}, {2,7,9,10}, {1,8,9,10}, {2,3,5,6,8,9,10}, {0,2,3,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{1,5}, {0,1,3,6}, {0,1,2,3,4,5,6,7}, {0,1,3,4,8}, {0,1,2,3,5,8}, {1,2,3,6,8}, {0,7,8}, {0,5,7,8}, {0,1,2,3,4,6,7,8}, {0,1,2,3,9}, {0,4,5,9}, {2,6,9}, {0,1,2,3,4,5,6,7,9}, {2,4,8,9}, {0,1,2,3,5,8,9}, {0,6,8,9}, {1,4,7,8,9}, {1,4,5,7,8,9}, {0,1,2,3,4,6,7,8,9}, {0,1,2,3,4,10}, {4,5,10}, {1,3,6,10}, {5,6,7,10}, {1,3,4,8,10}, {4,5,8,10}, {0,1,2,3,6,8,10}, {0,1,4,7,8,10}, {0,1,4,5,7,8,10}, {6,7,8,10}, {0,1,9,10}, {0,1,5,9,10}, {0,2,6,9,10}, {5,6,7,9,10}, {0,2,4,8,9,10}, {4,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 122. `[[39,5,3]]` — T0·T1·T4·CS01·CS02·CS12·CS23·CS34·CCZ012

- gate `0+1+4+01+02+12+23+34+012`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,5}, {0,1,2,6}, {0,1,2,5,6}, {0,1,2,7}, {0,1,2,5,7}, {0,1,2,5,6,7}, {2,3,8}, {0,2,5,8}, {1,3,4,5,6,7,8}, {2,3,9}, {1,3,6,9}, {0,2,4,7,9}, {2,3,8,9}, {0,1,2,4,5,6,8,9}, {3,5,7,8,9}, {0,1,4,6,7,10}, {2,3,8,10}, {0,4,5,8,10}, {1,2,3,5,6,7,8,10}, {2,3,9,10}, {1,2,3,4,6,9,10}, {0,7,9,10}, {2,3,8,9,10}, {0,1,5,6,8,9,10}, {2,3,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{2,3,5}, {0,3,4,6}, {4,5,6,7}, {0,4,8}, {3,4,5,8}, {0,1,2,3,6,8}, {0,1,2,4,7,8}, {0,1,2,4,5,7,8}, {4,6,7,8}, {3,4,9}, {0,1,2,3,4,5,9}, {0,6,9}, {4,5,6,7,9}, {0,3,8,9}, {3,4,5,8,9}, {0,1,2,4,6,8,9}, {2,7,8,9}, {2,5,7,8,9}, {4,6,7,8,9}, {4,10}, {3,5,10}, {1,2,3,6,10}, {5,6,7,10}, {1,2,8,10}, {3,5,8,10}, {3,4,6,8,10}, {0,1,4,7,8,10}, {0,1,4,5,7,8,10}, {6,7,8,10}, {0,1,3,4,9,10}, {0,1,3,4,5,9,10}, {1,2,4,6,9,10}, {5,6,7,9,10}, {1,2,3,4,8,9,10}, {3,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 123. `[[39,5,3]]` — T0·T1·T4·CS01·CS02·CS14·CS23·CS34·CCZ012·CCZ123·CCZ134

- gate `0+1+4+01+02+14+23+34+012+123+134`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{1,2,3,5}, {1,2,3,6}, {1,2,3,5,6}, {1,2,3,7}, {1,2,3,5,7}, {1,2,3,5,6,7}, {0,1,2,8}, {0,1,2,3,5,8}, {0,1,3,4,5,6,7,8}, {0,1,2,9}, {0,2,6,9}, {0,4,7,9}, {0,1,2,8,9}, {4,5,6,8,9}, {2,5,7,8,9}, {0,1,4,6,7,10}, {0,1,2,8,10}, {1,4,5,8,10}, {1,2,5,6,7,8,10}, {0,1,2,9,10}, {3,4,6,9,10}, {2,3,7,9,10}, {0,1,2,8,9,10}, {0,2,3,5,6,8,9,10}, {0,3,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,5}, {1,2,4,6}, {1,2,3,4,5,6,7}, {1,4,8}, {1,3,4,5,8}, {1,3,6,8}, {4,7,8}, {4,5,7,8}, {1,2,3,4,6,7,8}, {1,3,4,9}, {2,4,5,9}, {2,3,6,9}, {1,2,3,4,5,6,7,9}, {3,8,9}, {1,3,4,5,8,9}, {4,6,8,9}, {0,1,7,8,9}, {0,1,5,7,8,9}, {1,2,3,4,6,7,8,9}, {1,2,3,4,10}, {2,5,10}, {1,2,6,10}, {5,6,7,10}, {1,8,10}, {2,5,8,10}, {1,3,4,6,8,10}, {0,1,4,7,8,10}, {0,1,4,5,7,8,10}, {6,7,8,10}, {0,1,2,4,9,10}, {0,1,2,4,5,9,10}, {2,3,4,6,9,10}, {5,6,7,9,10}, {3,4,8,9,10}, {2,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 124. `[[39,5,3]]` — T0·CS12·CS13·CS14·CCZ012·CCZ013·CCZ014·CCZ123·CCZ124·CCZ134

- gate `0+12+13+14+012+013+014+123+124+134`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,3,4,5}, {0,1,2,3,4,6}, {0,1,2,3,4,5,6}, {0,1,2,3,4,7}, {0,1,2,3,4,5,7}, {0,1,2,3,4,5,6,7}, {0,1,8}, {1,3,4,5,8}, {3,4,5,6,7,8}, {0,1,9}, {1,2,4,6,9}, {2,4,7,9}, {0,1,8,9}, {0,4,5,6,8,9}, {0,1,4,5,7,8,9}, {0,6,7,10}, {0,1,8,10}, {2,5,8,10}, {1,2,5,6,7,8,10}, {0,1,9,10}, {3,6,9,10}, {1,3,7,9,10}, {0,1,8,9,10}, {0,1,2,3,5,6,8,9,10}, {0,2,3,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,2,3,4,5}, {2,3,6}, {0,1,2,4,5,6,7}, {2,8}, {0,1,2,3,4,5,8}, {0,1,3,6,8}, {2,4,7,8}, {2,4,5,7,8}, {0,1,2,4,6,7,8}, {0,1,2,3,4,9}, {2,3,4,5,9}, {0,1,4,6,9}, {0,1,2,4,5,6,7,9}, {0,1,3,4,8,9}, {0,1,2,3,4,5,8,9}, {2,4,6,8,9}, {0,2,4,7,8,9}, {0,2,4,5,7,8,9}, {0,1,2,4,6,7,8,9}, {0,1,2,4,10}, {3,5,10}, {3,4,6,10}, {5,6,7,10}, {4,8,10}, {3,5,8,10}, {0,1,2,3,4,6,8,10}, {0,7,8,10}, {0,5,7,8,10}, {6,7,8,10}, {0,3,9,10}, {0,3,5,9,10}, {0,1,2,6,9,10}, {5,6,7,9,10}, {0,1,2,3,8,9,10}, {3,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 125. `[[39,5,3]]` — T0·CS12·CS13·CS14·CS23·CS24·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ134·CCZ234

- gate `0+12+13+14+23+24+012+013+014+023+024+134+234`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,2,3,4,5}, {0,2,3,4,6}, {0,2,3,4,5,6}, {0,2,3,4,7}, {0,2,3,4,5,7}, {0,2,3,4,5,6,7}, {0,1,2,8}, {0,2,3,5,8}, {0,1,3,5,6,7,8}, {0,1,2,9}, {1,4,6,9}, {2,4,7,9}, {0,1,2,8,9}, {2,5,6,8,9}, {1,5,7,8,9}, {0,6,7,10}, {0,1,2,8,10}, {0,4,5,8,10}, {0,1,2,4,5,6,7,8,10}, {0,1,2,9,10}, {1,2,3,6,9,10}, {3,7,9,10}, {0,1,2,8,9,10}, {3,4,5,6,8,9,10}, {1,2,3,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,5}, {1,6}, {1,2,3,5,6,7}, {0,4,8}, {0,2,3,4,5,8}, {3,6,8}, {0,2,4,7,8}, {0,2,4,5,7,8}, {1,2,3,6,7,8}, {0,2,3,4,9}, {1,2,5,9}, {0,1,2,3,4,6,9}, {1,2,3,5,6,7,9}, {2,3,8,9}, {0,2,3,4,5,8,9}, {0,2,4,6,8,9}, {2,4,7,8,9}, {2,4,5,7,8,9}, {1,2,3,6,7,8,9}, {1,2,3,10}, {0,1,4,5,10}, {0,1,2,4,6,10}, {5,6,7,10}, {2,8,10}, {0,1,4,5,8,10}, {0,2,3,4,6,8,10}, {0,7,8,10}, {0,5,7,8,10}, {6,7,8,10}, {1,4,9,10}, {1,4,5,9,10}, {1,3,6,9,10}, {5,6,7,9,10}, {0,3,4,8,9,10}, {0,1,4,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 126. `[[39,5,3]]` — T0·CS12·CS13·CS24·CS34·CCZ012·CCZ013·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234

- gate `0+12+13+24+34+012+013+024+034+123+124+134+234`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,2,3,5}, {0,2,3,6}, {0,2,3,5,6}, {0,2,3,7}, {0,2,3,5,7}, {0,2,3,5,6,7}, {0,1,4,8}, {0,2,5,8}, {0,1,2,4,5,6,7,8}, {0,1,4,9}, {1,2,3,6,9}, {2,3,4,7,9}, {0,1,4,8,9}, {2,4,5,6,8,9}, {1,2,5,7,8,9}, {0,6,7,10}, {0,1,4,8,10}, {0,3,5,8,10}, {0,1,3,4,5,6,7,8,10}, {0,1,4,9,10}, {1,6,9,10}, {4,7,9,10}, {0,1,4,8,9,10}, {3,4,5,6,8,9,10}, {1,3,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,2,3,5}, {0,1,3,6}, {0,2,3,4,5,6,7}, {0,3,8}, {0,1,2,3,4,5,8}, {0,4,6,8}, {1,2,3,7,8}, {1,2,3,5,7,8}, {0,2,3,4,6,7,8}, {0,1,2,3,4,9}, {2,3,5,9}, {2,4,6,9}, {0,2,3,4,5,6,7,9}, {1,2,4,8,9}, {0,1,2,3,4,5,8,9}, {1,2,3,6,8,9}, {0,1,2,3,7,8,9}, {0,1,2,3,5,7,8,9}, {0,2,3,4,6,7,8,9}, {0,2,3,4,10}, {1,5,10}, {0,2,6,10}, {5,6,7,10}, {0,1,2,8,10}, {1,5,8,10}, {0,1,2,3,4,6,8,10}, {0,7,8,10}, {0,5,7,8,10}, {6,7,8,10}, {0,1,9,10}, {0,1,5,9,10}, {1,3,4,6,9,10}, {5,6,7,9,10}, {3,4,8,9,10}, {1,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 127. `[[39,5,3]]` — T0·T3·T4·CS01·CS02·CS12·CS13·CS24·CCZ012

- gate `0+3+4+01+02+12+13+24+012`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{2,4,5}, {2,4,6}, {2,4,5,6}, {2,4,7}, {2,4,5,7}, {2,4,5,6,7}, {1,3,8}, {0,5,8}, {1,4,5,6,7,8}, {1,3,9}, {0,1,2,3,6,9}, {2,3,4,7,9}, {1,3,8,9}, {0,3,5,6,8,9}, {1,3,4,5,7,8,9}, {0,3,4,6,7,10}, {1,3,8,10}, {2,3,5,8,10}, {0,1,2,3,4,5,6,7,8,10}, {1,3,9,10}, {1,6,9,10}, {0,4,7,9,10}, {1,3,8,9,10}, {2,5,6,8,9,10}, {0,1,2,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,5}, {1,2,3,6}, {2,3,4,5,6,7}, {3,4,8}, {1,3,5,8}, {1,6,8}, {3,7,8}, {3,5,7,8}, {2,3,4,6,7,8}, {1,3,9}, {1,2,3,4,5,9}, {2,6,9}, {2,3,4,5,6,7,9}, {1,4,8,9}, {1,3,5,8,9}, {3,6,8,9}, {0,4,7,8,9}, {0,4,5,7,8,9}, {2,3,4,6,7,8,9}, {2,3,4,10}, {1,2,4,5,10}, {1,2,6,10}, {5,6,7,10}, {4,8,10}, {1,2,4,5,8,10}, {1,3,6,8,10}, {0,3,4,7,8,10}, {0,3,4,5,7,8,10}, {6,7,8,10}, {0,1,2,3,9,10}, {0,1,2,3,5,9,10}, {2,3,6,9,10}, {5,6,7,9,10}, {1,3,4,8,9,10}, {1,2,4,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 128. `[[39,5,3]]` — T0·T3·T4·CS01·CS02·CS13·CS23·CCZ012·CCZ123

- gate `0+3+4+01+02+13+23+012+123`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{4,5}, {4,6}, {4,5,6}, {4,7}, {4,5,7}, {4,5,6,7}, {1,2,3,8}, {2,4,5,8}, {0,1,5,6,7,8}, {1,2,3,9}, {1,2,6,9}, {0,4,7,9}, {1,2,3,8,9}, {0,2,4,5,6,8,9}, {1,5,7,8,9}, {0,3,4,6,7,10}, {1,2,3,8,10}, {0,2,3,4,5,8,10}, {1,3,5,6,7,8,10}, {1,2,3,9,10}, {0,1,2,3,6,9,10}, {3,4,7,9,10}, {1,2,3,8,9,10}, {2,3,4,5,6,8,9,10}, {0,1,3,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{1,2,3,5}, {0,1,2,3,4,6}, {0,2,5,6,7}, {0,2,3,4,8}, {0,1,2,5,8}, {1,4,6,8}, {0,2,4,7,8}, {0,2,4,5,7,8}, {0,2,6,7,8}, {0,1,2,9}, {0,1,2,4,5,9}, {3,4,6,9}, {0,2,5,6,7,9}, {1,3,4,8,9}, {0,1,2,5,8,9}, {0,2,4,6,8,9}, {2,3,7,8,9}, {2,3,5,7,8,9}, {0,2,6,7,8,9}, {0,2,10}, {1,5,10}, {1,3,6,10}, {5,6,7,10}, {3,8,10}, {1,5,8,10}, {0,1,2,6,8,10}, {0,3,4,7,8,10}, {0,3,4,5,7,8,10}, {6,7,8,10}, {0,1,3,4,9,10}, {0,1,3,4,5,9,10}, {0,2,3,6,9,10}, {5,6,7,9,10}, {0,1,2,3,8,9,10}, {1,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 129. `[[39,5,3]]` — T0·T3·T4·CS01·CS02·CS34·CCZ012

- gate `0+3+4+01+02+34+012`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{3,4,5}, {3,4,6}, {3,4,5,6}, {3,4,7}, {3,4,5,7}, {3,4,5,6,7}, {1,2,8}, {0,2,3,4,5,8}, {1,5,6,7,8}, {1,2,9}, {1,2,3,6,9}, {0,4,7,9}, {1,2,8,9}, {2,4,5,6,8,9}, {0,1,3,5,7,8,9}, {0,3,4,6,7,10}, {1,2,8,10}, {2,3,4,5,8,10}, {0,1,5,6,7,8,10}, {1,2,9,10}, {0,1,2,3,6,9,10}, {4,7,9,10}, {1,2,8,9,10}, {0,2,4,5,6,8,9,10}, {1,3,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,5}, {1,4,6}, {1,2,3,5,6,7}, {1,3,4,8}, {1,2,5,8}, {4,6,8}, {1,2,4,7,8}, {1,2,4,5,7,8}, {1,2,3,6,7,8}, {1,2,9}, {1,2,3,4,5,9}, {2,4,6,9}, {1,2,3,5,6,7,9}, {2,3,4,8,9}, {1,2,5,8,9}, {1,2,4,6,8,9}, {0,1,2,3,7,8,9}, {0,1,2,3,5,7,8,9}, {1,2,3,6,7,8,9}, {1,2,3,10}, {3,5,10}, {2,6,10}, {5,6,7,10}, {2,3,8,10}, {3,5,8,10}, {1,2,6,8,10}, {0,3,4,7,8,10}, {0,3,4,5,7,8,10}, {6,7,8,10}, {0,4,9,10}, {0,4,5,9,10}, {1,6,9,10}, {5,6,7,9,10}, {1,3,8,9,10}, {3,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 130. `[[39,5,3]]` — T0·T4·CS01·CS02·CS03·CCZ012·CCZ013·CCZ023

- gate `0+4+01+02+03+012+013+023`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{1,2,3,5}, {1,2,3,6}, {1,2,3,5,6}, {1,2,3,7}, {1,2,3,5,7}, {1,2,3,5,6,7}, {0,1,2,3,8}, {1,2,5,8}, {3,4,5,6,7,8}, {0,1,2,3,9}, {1,3,6,9}, {2,4,7,9}, {0,1,2,3,8,9}, {2,3,4,5,6,8,9}, {1,5,7,8,9}, {0,4,6,7,10}, {0,1,2,3,8,10}, {0,3,4,5,8,10}, {0,1,2,5,6,7,8,10}, {0,1,2,3,9,10}, {0,2,4,6,9,10}, {0,1,3,7,9,10}, {0,1,2,3,8,9,10}, {0,1,5,6,8,9,10}, {0,2,3,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{4,5}, {1,6}, {1,2,4,5,6,7}, {1,3,4,8}, {1,2,3,5,8}, {0,1,2,4,6,8}, {0,3,4,7,8}, {0,3,4,5,7,8}, {1,2,4,6,7,8}, {1,2,3,9}, {0,5,9}, {2,3,6,9}, {1,2,4,5,6,7,9}, {2,4,8,9}, {1,2,3,5,8,9}, {0,3,4,6,8,9}, {3,7,8,9}, {3,5,7,8,9}, {1,2,4,6,7,8,9}, {1,2,4,10}, {3,4,5,10}, {0,1,3,4,6,10}, {5,6,7,10}, {0,1,8,10}, {3,4,5,8,10}, {1,2,3,6,8,10}, {0,4,7,8,10}, {0,4,5,7,8,10}, {6,7,8,10}, {0,3,9,10}, {0,3,5,9,10}, {0,2,4,6,9,10}, {5,6,7,9,10}, {0,2,3,8,9,10}, {3,4,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 131. `[[39,5,3]]` — T0·T4·CS01·CS02·CS03·CS12·CS13·CS14·CCZ012·CCZ013·CCZ023·CCZ123

- gate `0+4+01+02+03+12+13+14+012+013+023+123`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,3,5}, {0,1,2,3,6}, {0,1,2,3,5,6}, {0,1,2,3,7}, {0,1,2,3,5,7}, {0,1,2,3,5,6,7}, {1,4,8}, {1,3,5,8}, {0,3,5,6,7,8}, {1,4,9}, {0,1,2,3,4,6,9}, {2,3,4,7,9}, {1,4,8,9}, {0,3,4,5,6,8,9}, {1,3,4,5,7,8,9}, {0,4,6,7,10}, {1,4,8,10}, {2,4,5,8,10}, {0,1,2,4,5,6,7,8,10}, {1,4,9,10}, {0,6,9,10}, {1,7,9,10}, {1,4,8,9,10}, {0,1,2,5,6,8,9,10}, {2,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,3,5}, {1,2,4,6}, {1,3,5,6,7}, {4,8}, {2,3,5,8}, {2,4,6,8}, {3,4,7,8}, {3,4,5,7,8}, {1,3,6,7,8}, {2,3,9}, {1,2,3,4,5,9}, {1,3,4,6,9}, {1,3,5,6,7,9}, {2,3,4,8,9}, {2,3,5,8,9}, {3,4,6,8,9}, {0,3,7,8,9}, {0,3,5,7,8,9}, {1,3,6,7,8,9}, {1,3,10}, {1,2,5,10}, {1,2,3,6,10}, {5,6,7,10}, {3,8,10}, {1,2,5,8,10}, {2,3,6,8,10}, {0,4,7,8,10}, {0,4,5,7,8,10}, {6,7,8,10}, {0,1,2,4,9,10}, {0,1,2,4,5,9,10}, {1,6,9,10}, {5,6,7,9,10}, {2,8,9,10}, {1,2,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 132. `[[39,5,3]]` — T0·T4·CS01·CS02·CS03·CS12·CS13·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234

- gate `0+4+01+02+03+12+13+24+34+012+013+023+123+234`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{0,1,2,3,5}, {0,1,2,3,6}, {0,1,2,3,5,6}, {0,1,2,3,7}, {0,1,2,3,5,7}, {0,1,2,3,5,6,7}, {1,8}, {0,1,2,5,8}, {2,4,5,6,7,8}, {1,9}, {0,1,3,6,9}, {3,4,7,9}, {1,8,9}, {4,5,6,8,9}, {0,1,5,7,8,9}, {0,4,6,7,10}, {1,8,10}, {0,3,4,5,8,10}, {1,3,5,6,7,8,10}, {1,9,10}, {0,2,4,6,9,10}, {1,2,7,9,10}, {1,8,9,10}, {1,2,3,5,6,8,9,10}, {0,2,3,4,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{2,3,4,5}, {2,6}, {1,4,5,6,7}, {0,3,4,8}, {0,1,2,3,5,8}, {0,1,2,3,4,6,8}, {4,7,8}, {4,5,7,8}, {1,4,6,7,8}, {0,1,2,3,9}, {0,2,3,5,9}, {0,1,3,6,9}, {1,4,5,6,7,9}, {1,2,4,8,9}, {0,1,2,3,5,8,9}, {4,6,8,9}, {0,7,8,9}, {0,5,7,8,9}, {1,4,6,7,8,9}, {1,4,10}, {0,2,3,4,5,10}, {2,4,6,10}, {5,6,7,10}, {0,3,8,10}, {0,2,3,4,5,8,10}, {0,1,2,3,6,8,10}, {0,4,7,8,10}, {0,4,5,7,8,10}, {6,7,8,10}, {2,3,9,10}, {2,3,5,9,10}, {0,1,3,4,6,9,10}, {5,6,7,9,10}, {1,2,8,9,10}, {0,2,3,4,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 133. `[[39,5,3]]` — T0·T4·CS01·CS02·CS03·CS14·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ124·CCZ134·CCZ234

- gate `0+4+01+02+03+14+24+34+012+013+023+124+134+234`, `N = 11` (5 outputs + 6 checks), T-count 2, reduced degree 1, a3 = 123
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{1,2,3,4,5}, {1,4,6}, {4,5,6,7}, {1,8}, {5,8}, {0,1,2,3,4,6,8}, {0,1,2,3,4,7,8}, {0,1,2,3,4,5,7,8}, {4,6,7,8}, {9}, {2,4,5,9}, {0,3,6,9}, {4,5,6,7,9}, {0,3,4,8,9}, {5,8,9}, {2,6,8,9}, {0,2,4,7,8,9}, {0,2,4,5,7,8,9}, {4,6,7,8,9}, {4,10}, {0,1,3,5,10}, {1,2,4,6,10}, {5,6,7,10}, {1,2,8,10}, {4,5,8,10}, {0,1,3,4,6,8,10}, {1,3,7,8,10}, {1,3,5,7,8,10}, {6,7,8,10}, {0,9,10}, {0,5,9,10}, {0,2,3,6,9,10}, {5,6,7,9,10}, {0,2,3,4,8,9,10}, {4,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
```

### 134. `[[39,5,3]]` — T0·T4·CS01·CS02·CS12·CS13·CS14·CS23·CS34·CCZ012·CCZ134

- gate `0+4+01+02+12+13+14+23+34+012+134`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{1,3,4,5}, {1,3,4,6}, {1,3,4,5,6}, {1,3,4,7}, {1,3,4,5,7}, {1,3,4,5,6,7}, {2,3,8}, {1,3,5,8}, {0,1,2,4,5,6,7,8}, {2,3,9}, {1,2,3,4,6,9}, {0,1,7,9}, {2,3,8,9}, {0,1,4,5,6,8,9}, {1,2,3,5,7,8,9}, {0,4,6,7,10}, {2,3,8,10}, {0,5,8,10}, {2,3,4,5,6,7,8,10}, {2,3,9,10}, {0,2,4,6,9,10}, {3,7,9,10}, {2,3,8,9,10}, {3,4,5,6,8,9,10}, {0,2,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{0,1,2,5}, {2,4,6}, {0,2,3,5,6,7}, {0,1,8}, {1,3,4,5,8}, {0,1,3,4,6,8}, {0,7,8}, {0,5,7,8}, {0,2,3,6,7,8}, {1,3,4,9}, {1,2,4,5,9}, {1,2,3,6,9}, {0,2,3,5,6,7,9}, {0,3,4,8,9}, {1,3,4,5,8,9}, {0,6,8,9}, {4,7,8,9}, {4,5,7,8,9}, {0,2,3,6,7,8,9}, {0,2,3,10}, {0,1,2,4,5,10}, {0,2,4,6,10}, {5,6,7,10}, {1,8,10}, {0,1,2,4,5,8,10}, {1,3,4,6,8,10}, {0,4,7,8,10}, {0,4,5,7,8,10}, {6,7,8,10}, {1,2,9,10}, {1,2,5,9,10}, {0,1,2,3,6,9,10}, {5,6,7,9,10}, {3,4,8,9,10}, {0,1,2,4,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 135. `[[39,5,3]]` — T0·T4·CS01·CS02·CS13·CS23·CS34·CCZ012·CCZ123

- gate `0+4+01+02+13+23+34+012+123`, `N = 12` (5 outputs + 7 checks), T-count 3, reduced degree 1, a3 = 91
- source: length40_m7_010, origin 97; rep_length40_m7_010.json

```text
[{3,4,5}, {3,4,6}, {3,4,5,6}, {3,4,7}, {3,4,5,7}, {3,4,5,6,7}, {1,2,3,8}, {2,3,4,5,8}, {0,1,5,6,7,8}, {1,2,3,9}, {1,2,6,9}, {0,3,4,7,9}, {1,2,3,8,9}, {0,2,3,4,5,6,8,9}, {1,5,7,8,9}, {0,4,6,7,10}, {1,2,3,8,10}, {0,2,4,5,8,10}, {1,3,5,6,7,8,10}, {1,2,3,9,10}, {0,1,2,3,6,9,10}, {4,7,9,10}, {1,2,3,8,9,10}, {2,4,5,6,8,9,10}, {0,1,3,5,7,8,9,10}, {5,11}, {5,8,11}, {5,9,11}, {5,8,9,11}, {10,11}, {6,10,11}, {5,6,10,11}, {7,10,11}, {5,7,10,11}, {6,7,10,11}, {5,6,7,10,11}, {5,8,10,11}, {5,9,10,11}, {5,8,9,10,11}]
```

Best witness at each other check rank:

- rank 6 (`N = 11`), a3 = 139; length40_m6_001, origin 8; rep_length40_m6_001.json

  ```text
  [{1,2,3,5}, {0,1,2,4,6}, {0,2,5,6,7}, {0,2,4,8}, {0,1,2,5,8}, {1,3,4,6,8}, {0,2,3,4,7,8}, {0,2,3,4,5,7,8}, {0,2,6,7,8}, {0,1,2,9}, {0,1,2,3,4,5,9}, {4,6,9}, {0,2,5,6,7,9}, {1,4,8,9}, {0,1,2,5,8,9}, {0,2,3,4,6,8,9}, {2,3,7,8,9}, {2,3,5,7,8,9}, {0,2,6,7,8,9}, {0,2,10}, {1,5,10}, {1,3,6,10}, {5,6,7,10}, {3,8,10}, {1,5,8,10}, {0,1,2,6,8,10}, {0,4,7,8,10}, {0,4,5,7,8,10}, {6,7,8,10}, {0,1,4,9,10}, {0,1,4,5,9,10}, {0,2,3,6,9,10}, {5,6,7,9,10}, {0,1,2,3,8,9,10}, {1,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
  ```

### 136. `[[39,5,3]]` — CS01·CS02·CS03·CS04·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034

- gate `01+02+03+04+012+013+014+023+024+034`, `N = 11` (5 outputs + 6 checks), T-count 3, reduced degree 2, a3 = 144
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{2,5}, {1,2,3,4,6}, {0,1,2,3,4,5,6,7}, {0,2,4,8}, {4,5,8}, {0,1,2,3,4,6,8}, {1,2,3,4,7,8}, {0,1,2,3,4,5,7,8}, {1,2,3,4,6,7,8}, {0,1,2,3,4,9}, {0,1,3,4,5,9}, {1,2,3,4,6,9}, {0,1,2,3,4,5,6,7,9}, {1,3,8,9}, {0,1,2,3,5,8,9}, {0,1,2,3,4,6,8,9}, {1,2,3,4,7,8,9}, {0,1,2,3,4,5,7,8,9}, {1,2,3,4,6,7,8,9}, {0,1,10}, {1,2,5,10}, {6,10}, {5,6,7,10}, {0,1,2,4,8,10}, {1,4,5,8,10}, {6,8,10}, {7,8,10}, {5,7,8,10}, {6,7,8,10}, {2,3,4,9,10}, {0,3,4,5,9,10}, {6,9,10}, {5,6,7,9,10}, {3,8,9,10}, {0,2,3,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
```

### 137. `[[39,5,3]]` — CS01·CS02·CS03·CS04·CS14·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ124·CCZ134·CCZ234

- gate `01+02+03+04+14+24+34+012+013+023+124+134+234`, `N = 11` (5 outputs + 6 checks), T-count 3, reduced degree 2, a3 = 144
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{2,5}, {0,1,2,3,6}, {1,2,3,4,5,6,7}, {0,2,3,4,8}, {3,5,8}, {1,2,3,4,6,8}, {0,1,2,3,7,8}, {1,2,3,4,5,7,8}, {0,1,2,3,6,7,8}, {1,2,3,4,9}, {1,3,4,5,9}, {0,1,2,3,6,9}, {1,2,3,4,5,6,7,9}, {0,1,8,9}, {1,2,4,5,8,9}, {1,2,3,4,6,8,9}, {0,1,2,3,7,8,9}, {1,2,3,4,5,7,8,9}, {0,1,2,3,6,7,8,9}, {1,10}, {0,1,2,4,5,10}, {6,10}, {5,6,7,10}, {1,2,3,8,10}, {0,1,3,4,5,8,10}, {6,8,10}, {7,8,10}, {5,7,8,10}, {6,7,8,10}, {2,3,4,9,10}, {0,3,5,9,10}, {6,9,10}, {5,6,7,9,10}, {4,8,9,10}, {0,2,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
```

### 138. `[[39,5,3]]` — CS01·CS02·CS03·CS14·CS24·CS34·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ124·CCZ134·CCZ234

- gate `01+02+03+14+24+34+012+013+014+023+024+034+124+134+234`, `N = 11` (5 outputs + 6 checks), T-count 3, reduced degree 2, a3 = 144
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,5}, {0,1,2,3,4,6}, {0,4,5,6,7}, {0,2,3,4,8}, {4,5,8}, {0,4,6,8}, {0,1,2,3,4,7,8}, {0,4,5,7,8}, {0,1,2,3,4,6,7,8}, {0,4,9}, {1,4,5,9}, {0,1,2,3,4,6,9}, {0,4,5,6,7,9}, {2,3,8,9}, {0,5,8,9}, {0,4,6,8,9}, {0,1,2,3,4,7,8,9}, {0,4,5,7,8,9}, {0,1,2,3,4,6,7,8,9}, {1,3,10}, {0,1,2,5,10}, {6,10}, {5,6,7,10}, {0,3,4,8,10}, {2,4,5,8,10}, {6,8,10}, {7,8,10}, {5,7,8,10}, {6,7,8,10}, {0,1,3,4,9,10}, {1,2,4,5,9,10}, {6,9,10}, {5,6,7,9,10}, {3,8,9,10}, {0,2,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
```

### 139. `[[39,5,3]]` — CS01·CS02·CS04·CS13·CS14·CS23·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ034·CCZ123·CCZ124

- gate `01+02+04+13+14+23+24+34+012+013+023+034+123+124`, `N = 11` (5 outputs + 6 checks), T-count 3, reduced degree 2, a3 = 144
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{2,4,5}, {0,1,2,3,6}, {0,3,4,5,6,7}, {1,2,8}, {2,5,8}, {0,3,4,6,8}, {0,1,2,3,7,8}, {0,3,4,5,7,8}, {0,1,2,3,6,7,8}, {0,3,4,9}, {0,2,3,5,9}, {0,1,2,3,6,9}, {0,3,4,5,6,7,9}, {0,1,2,3,4,8,9}, {0,2,3,4,5,8,9}, {0,3,4,6,8,9}, {0,1,2,3,7,8,9}, {0,3,4,5,7,8,9}, {0,1,2,3,6,7,8,9}, {0,10}, {0,1,5,10}, {6,10}, {5,6,7,10}, {0,4,8,10}, {0,1,4,5,8,10}, {6,8,10}, {7,8,10}, {5,7,8,10}, {6,7,8,10}, {3,4,9,10}, {1,3,4,5,9,10}, {6,9,10}, {5,6,7,9,10}, {3,8,9,10}, {1,3,5,8,9,10}, {6,8,9,10}, {7,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}]
```

### 140. `[[39,6,3]]` — T0·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145

- gate `0+01+02+03+04+05+12+13+14+15+012+013+014+015+023+024+025+034+035+045+123+124+125+134+135+145`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{1,6}, {0,1,2,4,7}, {3,4,5,6,7,8}, {4,9}, {0,1,2,3,4,5,6,9}, {0,1,3,4,5,7,9}, {0,1,3,4,5,8,9}, {0,1,3,4,5,6,8,9}, {3,4,5,7,8,9}, {0,1,2,3,4,5,10}, {1,4,5,6,10}, {0,3,4,7,10}, {3,4,5,6,7,8,10}, {1,2,3,4,9,10}, {0,1,2,3,4,5,6,9,10}, {0,2,4,5,7,9,10}, {0,1,3,8,9,10}, {0,1,3,6,8,9,10}, {3,4,5,7,8,9,10}, {0,1,2,11}, {0,3,6,11}, {1,5,7,11}, {6,7,8,11}, {0,2,5,9,11}, {0,1,2,6,9,11}, {1,2,3,7,9,11}, {4,5,8,9,11}, {4,5,6,8,9,11}, {7,8,9,11}, {0,3,4,5,10,11}, {0,3,4,5,6,10,11}, {2,3,5,7,10,11}, {6,7,8,10,11}, {0,1,3,5,9,10,11}, {0,1,2,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 141. `[[39,6,3]]` — T0·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS25·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ235·CCZ245·CCZ345

- gate `0+01+02+03+04+05+12+13+14+25+35+45+012+013+014+015+023+024+025+034+035+045+123+124+125+134+135+145+235+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{2,3,4,6}, {0,3,4,5,7}, {0,2,3,4,5,6,7,8}, {0,1,3,4,5,9}, {0,1,2,3,4,5,6,9}, {5,7,9}, {5,8,9}, {5,6,8,9}, {0,2,3,4,5,7,8,9}, {0,1,2,3,4,5,10}, {0,1,2,4,5,6,10}, {2,3,5,7,10}, {0,2,3,4,5,6,7,8,10}, {1,2,3,5,9,10}, {0,1,2,3,4,5,6,9,10}, {0,2,4,5,7,9,10}, {0,1,3,8,9,10}, {0,1,3,6,8,9,10}, {0,2,3,4,5,7,8,9,10}, {1,11}, {0,1,2,4,6,11}, {2,3,7,11}, {6,7,8,11}, {1,2,3,9,11}, {1,6,9,11}, {0,2,4,7,9,11}, {0,1,3,5,8,9,11}, {0,1,3,5,6,8,9,11}, {7,8,9,11}, {2,3,4,5,10,11}, {2,3,4,5,6,10,11}, {0,3,4,7,10,11}, {6,7,8,10,11}, {0,1,3,4,9,10,11}, {1,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 142. `[[39,6,3]]` — T0·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS15·CS25·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ235·CCZ245·CCZ345

- gate `0+01+02+03+04+12+13+14+15+25+35+45+012+013+014+023+024+034+123+124+134+235+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {0,2,4,5,7}, {0,1,2,3,5,6,7,8}, {1,2,5,9}, {2,3,4,5,6,9}, {0,4,5,7,9}, {0,4,5,8,9}, {0,4,5,6,8,9}, {0,1,2,3,5,7,8,9}, {2,3,4,5,10}, {0,1,3,4,5,6,10}, {2,3,5,7,10}, {0,1,2,3,5,6,7,8,10}, {0,1,2,3,4,5,9,10}, {2,3,4,5,6,9,10}, {3,5,7,9,10}, {0,2,4,8,9,10}, {0,2,4,6,8,9,10}, {0,1,2,3,5,7,8,9,10}, {0,1,4,11}, {1,3,6,11}, {0,2,3,4,7,11}, {6,7,8,11}, {1,2,3,9,11}, {0,1,4,6,9,11}, {0,3,4,7,9,11}, {2,5,8,9,11}, {2,5,6,8,9,11}, {7,8,9,11}, {1,2,3,5,10,11}, {1,2,3,5,6,10,11}, {2,7,10,11}, {6,7,8,10,11}, {0,1,2,4,9,10,11}, {0,1,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 143. `[[39,6,3]]` — T0·CS01·CS02·CS03·CS04·CS12·CS13·CS15·CS24·CS25·CS34·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ145·CCZ234·CCZ235

- gate `0+01+02+03+04+12+13+15+24+25+34+35+45+012+013+014+023+024+034+123+124+134+145+234+235`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {0,3,5,7}, {0,2,4,5,6,7,8}, {4,5,9}, {2,3,5,6,9}, {0,1,3,5,7,9}, {0,1,3,5,8,9}, {0,1,3,5,6,8,9}, {0,2,4,5,7,8,9}, {2,3,5,10}, {0,2,3,4,5,6,10}, {1,2,5,7,10}, {0,2,4,5,6,7,8,10}, {0,1,2,3,4,5,9,10}, {2,3,5,6,9,10}, {2,5,7,9,10}, {0,3,8,9,10}, {0,3,6,8,9,10}, {0,2,4,5,7,8,9,10}, {0,3,4,11}, {1,2,4,6,11}, {0,2,3,7,11}, {6,7,8,11}, {2,4,9,11}, {0,3,4,6,9,11}, {0,1,2,3,7,9,11}, {1,5,8,9,11}, {1,5,6,8,9,11}, {7,8,9,11}, {2,4,5,10,11}, {2,4,5,6,10,11}, {1,7,10,11}, {6,7,8,10,11}, {0,1,3,4,9,10,11}, {0,3,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 144. `[[39,6,3]]` — T0·CS01·CS02·CS03·CS04·CS15·CS25·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ125·CCZ135·CCZ145·CCZ235·CCZ245·CCZ345

- gate `0+01+02+03+04+15+25+35+45+012+013+014+023+024+034+125+135+145+235+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {2,4,5,7}, {3,5,6,7,8}, {1,5,9}, {1,2,3,4,5,6,9}, {1,2,4,5,7,9}, {1,2,4,5,8,9}, {1,2,4,5,6,8,9}, {3,5,7,8,9}, {1,2,3,4,5,10}, {3,4,5,6,10}, {2,3,5,7,10}, {3,5,6,7,8,10}, {1,3,4,5,9,10}, {1,2,3,4,5,6,9,10}, {1,2,3,5,7,9,10}, {0,4,8,9,10}, {0,4,6,8,9,10}, {3,5,7,8,9,10}, {1,2,4,11}, {1,2,3,6,11}, {1,3,4,7,11}, {6,7,8,11}, {2,3,9,11}, {1,2,4,6,9,11}, {3,4,7,9,11}, {0,1,2,5,8,9,11}, {0,1,2,5,6,8,9,11}, {7,8,9,11}, {0,3,5,10,11}, {0,3,5,6,10,11}, {1,7,10,11}, {6,7,8,10,11}, {2,4,9,10,11}, {1,2,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 145. `[[39,6,3]]` — T0·CS01·CS02·CS03·CS12·CS13·CS14·CS15·CS24·CS25·CS34·CS35·CCZ012·CCZ013·CCZ023·CCZ123·CCZ145·CCZ234·CCZ235·CCZ245·CCZ345

- gate `0+01+02+03+12+13+14+15+24+25+34+35+012+013+023+123+145+234+235+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{1,4,5,6}, {0,2,3,7}, {1,3,4,5,6,7,8}, {0,1,3,9}, {2,3,4,5,6,9}, {0,3,7,9}, {0,3,8,9}, {0,3,6,8,9}, {1,3,4,5,7,8,9}, {2,3,4,5,10}, {0,3,4,6,10}, {0,1,3,4,7,10}, {1,3,4,5,6,7,8,10}, {0,2,3,4,9,10}, {2,3,4,5,6,9,10}, {0,1,2,3,4,7,9,10}, {1,5,8,9,10}, {1,5,6,8,9,10}, {1,3,4,5,7,8,9,10}, {1,2,11}, {4,6,11}, {1,4,7,11}, {6,7,8,11}, {2,4,9,11}, {1,2,6,9,11}, {1,2,4,7,9,11}, {0,1,3,5,8,9,11}, {0,1,3,5,6,8,9,11}, {7,8,9,11}, {0,1,3,4,5,10,11}, {0,1,3,4,5,6,10,11}, {2,7,10,11}, {6,7,8,10,11}, {1,9,10,11}, {1,2,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 146. `[[39,6,3]]` — T0·CS01·CS02·CS03·CS14·CS15·CS24·CS25·CS34·CS35·CCZ012·CCZ013·CCZ023·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245·CCZ345

- gate `0+01+02+03+14+15+24+25+34+35+012+013+023+124+125+134+135+145+234+235+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{4,5,6}, {0,2,4,5,7}, {0,1,2,4,6,7,8}, {2,3,4,9}, {1,2,3,4,5,6,9}, {1,2,5,7,9}, {1,2,5,8,9}, {1,2,5,6,8,9}, {0,1,2,4,7,8,9}, {1,2,3,4,5,10}, {2,5,6,10}, {1,2,3,4,7,10}, {0,1,2,4,6,7,8,10}, {0,1,2,4,5,9,10}, {1,2,3,4,5,6,9,10}, {0,2,3,7,9,10}, {1,4,5,8,9,10}, {1,4,5,6,8,9,10}, {0,1,2,4,7,8,9,10}, {0,3,5,11}, {1,6,11}, {3,4,5,7,11}, {6,7,8,11}, {0,4,9,11}, {0,3,5,6,9,11}, {0,1,3,5,7,9,11}, {2,4,8,9,11}, {2,4,6,8,9,11}, {7,8,9,11}, {1,2,4,10,11}, {1,2,4,6,10,11}, {0,1,4,7,10,11}, {6,7,8,10,11}, {1,3,4,5,9,10,11}, {0,3,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 147. `[[39,6,3]]` — T0·CS01·CS02·CS12·CS13·CS14·CS15·CS23·CS24·CS25·CCZ012·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245

- gate `0+01+02+12+13+14+15+23+24+25+012+134+135+145+234+235+245`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,6}, {0,2,3,5,7}, {0,4,5,6,7,8}, {5,9}, {2,3,4,5,6,9}, {0,1,2,4,5,7,9}, {0,1,2,4,5,8,9}, {0,1,2,4,5,6,8,9}, {0,4,5,7,8,9}, {2,3,4,5,10}, {0,1,5,6,10}, {2,4,5,7,10}, {0,4,5,6,7,8,10}, {0,3,4,5,9,10}, {2,3,4,5,6,9,10}, {1,2,3,5,7,9,10}, {0,1,4,8,9,10}, {0,1,4,6,8,9,10}, {0,4,5,7,8,9,10}, {0,2,3,11}, {2,4,6,11}, {0,1,7,11}, {6,7,8,11}, {1,2,3,9,11}, {0,2,3,6,9,11}, {0,3,4,7,9,11}, {2,5,8,9,11}, {2,5,6,8,9,11}, {7,8,9,11}, {4,5,10,11}, {4,5,6,10,11}, {1,3,4,7,10,11}, {6,7,8,10,11}, {0,1,2,4,9,10,11}, {0,2,3,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 148. `[[39,6,3]]` — T0·CS01·CS02·CS13·CS14·CS15·CS23·CS24·CS25·CCZ012·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245

- gate `0+01+02+13+14+15+23+24+25+012+123+124+125+134+135+145+234+235+245`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{1,2,3,4,5,6}, {1,2,4,5,7}, {0,1,3,6,7,8}, {0,2,9}, {3,4,5,6,9}, {2,4,5,7,9}, {2,4,5,8,9}, {2,4,5,6,8,9}, {0,1,3,7,8,9}, {3,4,5,10}, {0,1,3,4,6,10}, {1,3,5,7,10}, {0,1,3,6,7,8,10}, {0,3,4,9,10}, {3,4,5,6,9,10}, {3,5,7,9,10}, {0,4,8,9,10}, {0,4,6,8,9,10}, {0,1,3,7,8,9,10}, {0,1,4,5,11}, {0,1,2,3,5,6,11}, {1,2,3,4,7,11}, {6,7,8,11}, {0,2,3,5,9,11}, {0,1,4,5,6,9,11}, {2,3,4,7,9,11}, {0,2,5,8,9,11}, {0,2,5,6,8,9,11}, {7,8,9,11}, {1,3,10,11}, {1,3,6,10,11}, {1,7,10,11}, {6,7,8,10,11}, {0,4,5,9,10,11}, {0,1,4,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 149. `[[39,6,3]]` — T0·CS01·CS12·CS13·CS14·CS15·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145

- gate `0+01+12+13+14+15+123+124+125+134+135+145`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{1,2,3,4,5,6}, {3,5,7}, {0,1,4,6,7,8}, {0,1,2,9}, {2,3,4,5,6,9}, {2,3,5,7,9}, {2,3,5,8,9}, {2,3,5,6,8,9}, {0,1,4,7,8,9}, {2,3,4,5,10}, {0,1,4,5,6,10}, {3,4,7,10}, {0,1,4,6,7,8,10}, {0,1,2,4,5,9,10}, {2,3,4,5,6,9,10}, {2,3,4,7,9,10}, {0,5,8,9,10}, {0,5,6,8,9,10}, {0,1,4,7,8,9,10}, {0,1,2,3,5,11}, {0,1,2,3,4,6,11}, {2,4,5,7,11}, {6,7,8,11}, {0,1,3,4,9,11}, {0,1,2,3,5,6,9,11}, {4,5,7,9,11}, {0,2,3,8,9,11}, {0,2,3,6,8,9,11}, {7,8,9,11}, {1,4,10,11}, {1,4,6,10,11}, {2,7,10,11}, {6,7,8,10,11}, {0,1,3,5,9,10,11}, {0,1,2,3,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 150. `[[39,6,3]]` — T0·T1·CS01·CS02·CS03·CS04·CS05·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045

- gate `0+1+01+02+03+04+05+012+013+014+015+023+024+025+034+035+045`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{1,6}, {1,2,3,5,7}, {0,3,4,6,7,8}, {0,3,9}, {1,2,3,4,5,6,9}, {3,4,7,9}, {3,4,8,9}, {3,4,6,8,9}, {0,3,4,7,8,9}, {1,2,3,4,5,10}, {0,1,3,5,6,10}, {1,3,4,5,7,10}, {0,3,4,6,7,8,10}, {0,2,3,4,9,10}, {1,2,3,4,5,6,9,10}, {2,3,7,9,10}, {0,4,5,8,9,10}, {0,4,5,6,8,9,10}, {0,3,4,7,8,9,10}, {0,1,2,5,11}, {0,1,4,5,6,11}, {1,5,7,11}, {6,7,8,11}, {0,2,9,11}, {0,1,2,5,6,9,11}, {2,4,7,9,11}, {0,3,5,8,9,11}, {0,3,5,6,8,9,11}, {7,8,9,11}, {1,3,4,10,11}, {1,3,4,6,10,11}, {1,2,4,5,7,10,11}, {6,7,8,10,11}, {0,4,9,10,11}, {0,1,2,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 151. `[[39,6,3]]` — T0·T1·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS24·CS25·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245

- gate `0+1+01+02+03+04+05+12+13+14+15+23+24+25+012+013+014+015+023+024+025+034+035+045+123+124+125+134+135+145+234+235+245`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,5,6}, {2,4,7}, {5,6,7,8}, {2,3,9}, {3,4,5,6,9}, {2,3,4,7,9}, {2,3,4,8,9}, {2,3,4,6,8,9}, {5,7,8,9}, {3,4,5,10}, {0,4,5,6,10}, {0,5,7,10}, {5,6,7,8,10}, {0,3,4,5,9,10}, {3,4,5,6,9,10}, {0,3,5,7,9,10}, {1,4,8,9,10}, {1,4,6,8,9,10}, {5,7,8,9,10}, {3,4,11}, {0,2,3,5,6,11}, {0,2,3,4,5,7,11}, {6,7,8,11}, {0,2,5,9,11}, {3,4,6,9,11}, {0,2,4,5,7,9,11}, {1,2,3,8,9,11}, {1,2,3,6,8,9,11}, {7,8,9,11}, {0,1,5,10,11}, {0,1,5,6,10,11}, {3,7,10,11}, {6,7,8,10,11}, {4,9,10,11}, {3,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 152. `[[39,6,3]]` — T0·T1·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS24·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245·CCZ345

- gate `0+1+01+02+03+04+05+12+13+14+15+23+24+35+45+012+013+014+015+023+024+025+034+035+045+123+124+125+134+135+145+234+235+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,5,6}, {0,3,7}, {0,3,5,6,7,8}, {2,9}, {2,5,6,9}, {0,2,4,7,9}, {0,2,4,8,9}, {0,2,4,6,8,9}, {0,3,5,7,8,9}, {2,5,10}, {0,1,3,5,6,10}, {1,3,4,5,7,10}, {0,3,5,6,7,8,10}, {0,1,2,4,5,9,10}, {2,5,6,9,10}, {1,2,5,7,9,10}, {0,8,9,10}, {0,6,8,9,10}, {0,3,5,7,8,9,10}, {0,2,3,11}, {1,2,3,4,5,6,11}, {0,1,2,3,5,7,11}, {6,7,8,11}, {1,5,9,11}, {0,2,3,6,9,11}, {0,1,4,5,7,9,11}, {2,4,8,9,11}, {2,4,6,8,9,11}, {7,8,9,11}, {1,3,5,10,11}, {1,3,5,6,10,11}, {2,3,4,7,10,11}, {6,7,8,10,11}, {0,4,9,10,11}, {0,2,3,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 153. `[[39,6,3]]` — T0·T1·CS01·CS02·CS03·CS04·CS05·CS23·CS24·CS25·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ234·CCZ235·CCZ245

- gate `0+1+01+02+03+04+05+23+24+25+012+013+014+015+023+024+025+034+035+045+123+124+125+234+235+245`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{1,3,4,5,6}, {0,1,2,5,7}, {1,2,4,6,7,8}, {1,2,3,9}, {0,1,2,3,4,5,6,9}, {0,1,2,3,5,7,9}, {0,1,2,3,5,8,9}, {0,1,2,3,5,6,8,9}, {1,2,4,7,8,9}, {0,1,2,3,4,5,10}, {2,4,6,10}, {0,2,4,5,7,10}, {1,2,4,6,7,8,10}, {2,3,4,9,10}, {0,1,2,3,4,5,6,9,10}, {0,2,3,4,5,7,9,10}, {0,8,9,10}, {0,6,8,9,10}, {1,2,4,7,8,9,10}, {0,3,5,11}, {0,1,3,4,5,6,11}, {1,3,4,7,11}, {6,7,8,11}, {0,1,4,5,9,11}, {0,3,5,6,9,11}, {1,4,7,9,11}, {1,2,3,5,8,9,11}, {1,2,3,5,6,8,9,11}, {7,8,9,11}, {0,2,4,10,11}, {0,2,4,6,10,11}, {3,7,10,11}, {6,7,8,10,11}, {0,5,9,10,11}, {0,3,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 154. `[[39,6,3]]` — T0·T1·CS01·CS02·CS03·CS04·CS05·CS23·CS24·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245·CCZ345

- gate `0+1+01+02+03+04+05+23+24+35+45+012+013+014+015+023+024+025+034+035+045+123+124+135+145+234+235+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{1,3,4,6}, {2,5,7}, {0,3,4,5,6,7,8}, {1,5,9}, {0,1,2,3,4,5,6,9}, {5,7,9}, {5,8,9}, {5,6,8,9}, {0,3,4,5,7,8,9}, {0,1,2,3,4,5,10}, {0,3,5,6,10}, {0,1,3,5,7,10}, {0,3,4,5,6,7,8,10}, {0,2,3,5,9,10}, {0,1,2,3,4,5,6,9,10}, {0,1,2,3,5,7,9,10}, {0,1,4,8,9,10}, {0,1,4,6,8,9,10}, {0,3,4,5,7,8,9,10}, {1,2,11}, {0,3,6,11}, {0,1,3,7,11}, {6,7,8,11}, {0,2,3,9,11}, {1,2,6,9,11}, {0,1,2,3,7,9,11}, {0,1,4,5,8,9,11}, {0,1,4,5,6,8,9,11}, {7,8,9,11}, {1,3,4,5,10,11}, {1,3,4,5,6,10,11}, {2,7,10,11}, {6,7,8,10,11}, {1,9,10,11}, {1,2,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 155. `[[39,6,3]]` — T0·T1·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CS25·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234·CCZ345

- gate `0+1+01+02+03+04+12+13+14+23+24+25+35+45+012+013+014+023+024+034+123+124+134+234+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {5,7}, {0,2,4,5,6,7,8}, {0,4,5,9}, {2,5,6,9}, {0,3,5,7,9}, {0,3,5,8,9}, {0,3,5,6,8,9}, {0,2,4,5,7,8,9}, {2,5,10}, {2,3,5,6,10}, {2,4,5,7,10}, {0,2,4,5,6,7,8,10}, {0,2,5,9,10}, {2,5,6,9,10}, {0,2,3,4,5,7,9,10}, {1,3,4,8,9,10}, {1,3,4,6,8,9,10}, {0,2,4,5,7,8,9,10}, {0,4,11}, {0,2,6,11}, {0,2,3,4,7,11}, {6,7,8,11}, {2,3,9,11}, {0,4,6,9,11}, {2,4,7,9,11}, {0,1,4,5,8,9,11}, {0,1,4,5,6,8,9,11}, {7,8,9,11}, {1,2,4,5,10,11}, {1,2,4,5,6,10,11}, {0,3,7,10,11}, {6,7,8,10,11}, {3,4,9,10,11}, {0,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 156. `[[39,6,3]]` — T0·T1·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS25·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ235·CCZ245·CCZ345

- gate `0+1+01+02+03+04+12+13+14+25+35+45+012+013+014+023+024+034+123+124+134+235+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{5,6}, {0,1,3,5,7}, {0,3,6,7,8}, {0,2,3,4,5,9}, {0,1,2,3,4,6,9}, {1,3,5,7,9}, {1,3,5,8,9}, {1,3,5,6,8,9}, {0,3,7,8,9}, {0,1,2,3,4,10}, {0,2,3,6,10}, {1,3,4,7,10}, {0,3,6,7,8,10}, {2,3,9,10}, {0,1,2,3,4,6,9,10}, {0,1,3,4,7,9,10}, {0,1,2,8,9,10}, {0,1,2,6,8,9,10}, {0,3,7,8,9,10}, {1,2,4,11}, {0,1,2,5,6,11}, {4,5,7,11}, {6,7,8,11}, {1,2,5,9,11}, {1,2,4,6,9,11}, {0,4,5,7,9,11}, {0,2,3,5,8,9,11}, {0,2,3,5,6,8,9,11}, {7,8,9,11}, {1,3,10,11}, {1,3,6,10,11}, {0,7,10,11}, {6,7,8,10,11}, {0,1,2,4,9,10,11}, {1,2,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 157. `[[39,6,3]]` — T0·T1·CS01·CS02·CS03·CS04·CS23·CS24·CS25·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ125·CCZ135·CCZ145·CCZ234·CCZ345

- gate `0+1+01+02+03+04+23+24+25+35+45+012+013+014+023+024+034+123+124+125+135+145+234+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {1,5,7}, {1,2,4,5,6,7,8}, {1,2,3,5,9}, {1,3,4,5,6,9}, {1,3,5,7,9}, {1,3,5,8,9}, {1,3,5,6,8,9}, {1,2,4,5,7,8,9}, {1,3,4,5,10}, {4,5,6,10}, {2,4,5,7,10}, {1,2,4,5,6,7,8,10}, {3,4,5,9,10}, {1,3,4,5,6,9,10}, {2,3,4,5,7,9,10}, {0,2,8,9,10}, {0,2,6,8,9,10}, {1,2,4,5,7,8,9,10}, {2,3,11}, {1,3,4,6,11}, {1,2,3,4,7,11}, {6,7,8,11}, {1,4,9,11}, {2,3,6,9,11}, {1,2,4,7,9,11}, {0,1,2,3,5,8,9,11}, {0,1,2,3,5,6,8,9,11}, {7,8,9,11}, {0,2,4,5,10,11}, {0,2,4,5,6,10,11}, {3,7,10,11}, {6,7,8,10,11}, {2,9,10,11}, {2,3,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 158. `[[39,6,3]]` — T0·T1·CS01·CS02·CS03·CS04·CS25·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ125·CCZ135·CCZ145·CCZ235·CCZ245·CCZ345

- gate `0+1+01+02+03+04+25+35+45+012+013+014+023+024+034+125+135+145+235+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{1,5,6}, {0,4,5,7}, {1,3,4,6,7,8}, {0,2,4,9}, {1,2,3,4,5,6,9}, {0,1,3,4,5,7,9}, {0,1,3,4,5,8,9}, {0,1,3,4,5,6,8,9}, {1,3,4,7,8,9}, {1,2,3,4,5,10}, {1,4,6,10}, {2,3,4,5,7,10}, {1,3,4,6,7,8,10}, {3,4,9,10}, {1,2,3,4,5,6,9,10}, {1,2,4,5,7,9,10}, {0,1,3,8,9,10}, {0,1,3,6,8,9,10}, {1,3,4,7,8,9,10}, {2,5,11}, {0,3,5,6,11}, {0,1,2,7,11}, {6,7,8,11}, {0,1,5,9,11}, {2,5,6,9,11}, {0,2,3,7,9,11}, {4,5,8,9,11}, {4,5,6,8,9,11}, {7,8,9,11}, {0,3,4,10,11}, {0,3,4,6,10,11}, {1,3,7,10,11}, {6,7,8,10,11}, {1,2,3,5,9,10,11}, {2,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 159. `[[39,6,3]]` — T0·T1·CS01·CS02·CS03·CS12·CS13·CS23·CS24·CS25·CS34·CS35·CCZ012·CCZ013·CCZ023·CCZ123·CCZ245·CCZ345

- gate `0+1+01+02+03+12+13+23+24+25+34+35+012+013+023+123+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,6}, {1,2,3,4,7}, {2,5,6,7,8}, {1,9}, {3,4,5,6,9}, {3,5,7,9}, {3,5,8,9}, {3,5,6,8,9}, {2,5,7,8,9}, {3,4,5,10}, {0,2,6,10}, {0,1,2,3,5,7,10}, {2,5,6,7,8,10}, {0,1,4,5,9,10}, {3,4,5,6,9,10}, {0,3,4,7,9,10}, {1,5,8,9,10}, {1,5,6,8,9,10}, {2,5,7,8,9,10}, {2,3,4,11}, {0,2,3,5,6,11}, {0,1,2,7,11}, {6,7,8,11}, {0,1,3,4,9,11}, {2,3,4,6,9,11}, {0,4,5,7,9,11}, {1,3,8,9,11}, {1,3,6,8,9,11}, {7,8,9,11}, {0,1,2,5,10,11}, {0,1,2,5,6,10,11}, {1,2,4,5,7,10,11}, {6,7,8,10,11}, {1,3,5,9,10,11}, {2,3,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 160. `[[39,6,3]]` — T0·T1·CS01·CS02·CS03·CS12·CS13·CS24·CS25·CS34·CS35·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234·CCZ235·CCZ245·CCZ345

- gate `0+1+01+02+03+12+13+24+25+34+35+012+013+023+123+234+235+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{2,3,4,5,6}, {0,3,7}, {1,2,3,5,6,7,8}, {3,5,9}, {0,1,2,3,6,9}, {0,4,7,9}, {0,4,8,9}, {0,4,6,8,9}, {1,2,3,5,7,8,9}, {0,1,2,3,10}, {1,2,4,6,10}, {0,1,2,3,5,7,10}, {1,2,3,5,6,7,8,10}, {1,2,3,9,10}, {0,1,2,3,6,9,10}, {0,1,2,4,5,7,9,10}, {0,1,3,4,5,8,9,10}, {0,1,3,4,5,6,8,9,10}, {1,2,3,5,7,8,9,10}, {0,5,11}, {0,1,2,6,11}, {1,2,3,4,5,7,11}, {6,7,8,11}, {0,1,2,3,4,9,11}, {0,5,6,9,11}, {1,2,5,7,9,11}, {1,3,5,8,9,11}, {1,3,5,6,8,9,11}, {7,8,9,11}, {0,2,3,5,10,11}, {0,2,3,5,6,10,11}, {3,4,7,10,11}, {6,7,8,10,11}, {0,3,4,5,9,10,11}, {0,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 161. `[[39,6,3]]` — T0·T1·CS01·CS02·CS03·CS23·CS24·CS25·CS34·CS35·CCZ012·CCZ013·CCZ023·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ245·CCZ345

- gate `0+1+01+02+03+23+24+25+34+35+012+013+023+123+124+125+134+135+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{1,2,4,5,6}, {1,3,4,7}, {1,3,5,6,7,8}, {1,3,9}, {1,3,4,5,6,9}, {0,1,2,3,4,7,9}, {0,1,2,3,4,8,9}, {0,1,2,3,4,6,8,9}, {1,3,5,7,8,9}, {1,3,4,5,10}, {1,2,3,4,5,6,10}, {0,1,3,5,7,10}, {1,3,5,6,7,8,10}, {0,1,3,4,5,9,10}, {1,3,4,5,6,9,10}, {1,2,3,5,7,9,10}, {0,1,2,4,8,9,10}, {0,1,2,4,6,8,9,10}, {1,3,5,7,8,9,10}, {4,11}, {0,5,6,11}, {2,4,5,7,11}, {6,7,8,11}, {2,5,9,11}, {4,6,9,11}, {0,4,5,7,9,11}, {3,8,9,11}, {3,6,8,9,11}, {7,8,9,11}, {0,3,5,10,11}, {0,3,5,6,10,11}, {0,2,7,10,11}, {6,7,8,10,11}, {0,2,4,9,10,11}, {4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 162. `[[39,6,3]]` — T0·T1·CS01·CS02·CS03·CS24·CS25·CS34·CS35·CCZ012·CCZ013·CCZ023·CCZ124·CCZ125·CCZ134·CCZ135·CCZ234·CCZ235·CCZ245·CCZ345

- gate `0+1+01+02+03+24+25+34+35+012+013+023+124+125+134+135+234+235+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,6}, {0,3,5,7}, {0,1,2,4,5,6,7,8}, {5,9}, {1,2,3,4,5,6,9}, {0,1,3,4,5,7,9}, {0,1,3,4,5,8,9}, {0,1,3,4,5,6,8,9}, {0,1,2,4,5,7,8,9}, {1,2,3,4,5,10}, {0,1,2,5,6,10}, {2,3,4,5,7,10}, {0,1,2,4,5,6,7,8,10}, {0,2,4,5,9,10}, {1,2,3,4,5,6,9,10}, {1,2,3,5,7,9,10}, {0,1,4,8,9,10}, {0,1,4,6,8,9,10}, {0,1,2,4,5,7,8,9,10}, {0,3,11}, {2,3,4,6,11}, {0,1,2,7,11}, {6,7,8,11}, {1,2,3,9,11}, {0,3,6,9,11}, {0,2,4,7,9,11}, {3,5,8,9,11}, {3,5,6,8,9,11}, {7,8,9,11}, {2,4,5,10,11}, {2,4,5,6,10,11}, {1,4,7,10,11}, {6,7,8,10,11}, {0,1,3,4,9,10,11}, {0,3,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 163. `[[39,6,3]]` — T0·T1·CS01·CS02·CS12·CS23·CS24·CS25·CCZ012·CCZ234·CCZ235·CCZ245

- gate `0+1+01+02+12+23+24+25+012+234+235+245`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{2,3,4,5,6}, {1,2,3,5,7}, {0,3,4,6,7,8}, {0,1,2,3,9}, {3,4,5,6,9}, {1,2,5,7,9}, {1,2,5,8,9}, {1,2,5,6,8,9}, {0,3,4,7,8,9}, {3,4,5,10}, {0,4,5,6,10}, {3,4,7,10}, {0,3,4,6,7,8,10}, {0,3,4,5,9,10}, {3,4,5,6,9,10}, {4,7,9,10}, {0,1,3,5,8,9,10}, {0,1,3,5,6,8,9,10}, {0,3,4,7,8,9,10}, {0,5,11}, {0,1,2,4,6,11}, {1,2,3,4,5,7,11}, {6,7,8,11}, {0,1,2,3,4,9,11}, {0,5,6,9,11}, {1,2,4,5,7,9,11}, {0,2,3,8,9,11}, {0,2,3,6,8,9,11}, {7,8,9,11}, {1,3,4,10,11}, {1,3,4,6,10,11}, {3,7,10,11}, {6,7,8,10,11}, {0,3,5,9,10,11}, {0,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 164. `[[39,6,3]]` — T0·T1·CS01·CS02·CS23·CS24·CS25·CCZ012·CCZ123·CCZ124·CCZ125·CCZ234·CCZ235·CCZ245

- gate `0+1+01+02+23+24+25+012+123+124+125+234+235+245`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,6}, {0,1,4,5,7}, {1,4,5,6,7,8}, {0,1,2,3,4,5,9}, {1,2,3,4,5,6,9}, {1,2,4,5,7,9}, {1,2,4,5,8,9}, {1,2,4,5,6,8,9}, {1,4,5,7,8,9}, {1,2,3,4,5,10}, {3,4,6,10}, {0,4,7,10}, {1,4,5,6,7,8,10}, {0,2,3,4,9,10}, {1,2,3,4,5,6,9,10}, {2,4,7,9,10}, {0,3,5,8,9,10}, {0,3,5,6,8,9,10}, {1,4,5,7,8,9,10}, {2,3,11}, {1,2,3,5,6,11}, {0,1,2,5,7,11}, {6,7,8,11}, {0,1,3,5,9,11}, {2,3,6,9,11}, {1,5,7,9,11}, {0,1,2,3,4,8,9,11}, {0,1,2,3,4,6,8,9,11}, {7,8,9,11}, {0,4,5,10,11}, {0,4,5,6,10,11}, {0,2,7,10,11}, {6,7,8,10,11}, {0,3,9,10,11}, {2,3,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 165. `[[39,6,3]]` — T0·T1·CS01·CS23·CS24·CS25·CCZ023·CCZ024·CCZ025·CCZ123·CCZ124·CCZ125·CCZ234·CCZ235·CCZ245

- gate `0+1+01+23+24+25+023+024+025+123+124+125+234+235+245`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,6}, {0,5,7}, {0,1,3,5,6,7,8}, {0,2,4,5,9}, {0,1,2,3,4,5,6,9}, {0,1,2,3,5,7,9}, {0,1,2,3,5,8,9}, {0,1,2,3,5,6,8,9}, {0,1,3,5,7,8,9}, {0,1,2,3,4,5,10}, {4,5,6,10}, {1,3,5,7,10}, {0,1,3,5,6,7,8,10}, {1,2,3,4,5,9,10}, {0,1,2,3,4,5,6,9,10}, {2,5,7,9,10}, {3,4,8,9,10}, {3,4,6,8,9,10}, {0,1,3,5,7,8,9,10}, {2,4,11}, {0,1,2,3,4,6,11}, {0,2,7,11}, {6,7,8,11}, {0,4,9,11}, {2,4,6,9,11}, {0,1,3,7,9,11}, {0,1,2,4,5,8,9,11}, {0,1,2,4,5,6,8,9,11}, {7,8,9,11}, {3,5,10,11}, {3,5,6,10,11}, {1,2,3,7,10,11}, {6,7,8,10,11}, {1,3,4,9,10,11}, {2,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 166. `[[39,6,3]]` — T0·T1·CS01·CS23·CS24·CS25·CS34·CS35·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ245·CCZ345

- gate `0+1+01+23+24+25+34+35+023+024+025+034+035+123+124+125+134+135+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,4,5,6}, {0,1,3,5,7}, {1,4,6,7,8}, {1,9}, {0,1,3,4,5,6,9}, {1,2,5,7,9}, {1,2,5,8,9}, {1,2,5,6,8,9}, {1,4,7,8,9}, {0,1,3,4,5,10}, {0,2,4,6,10}, {0,4,5,7,10}, {1,4,6,7,8,10}, {3,4,9,10}, {0,1,3,4,5,6,9,10}, {2,3,4,5,7,9,10}, {2,8,9,10}, {2,6,8,9,10}, {1,4,7,8,9,10}, {0,3,5,11}, {0,1,4,5,6,11}, {0,1,2,4,7,11}, {6,7,8,11}, {1,2,3,4,5,9,11}, {0,3,5,6,9,11}, {1,3,4,7,9,11}, {1,5,8,9,11}, {1,5,6,8,9,11}, {7,8,9,11}, {0,4,10,11}, {0,4,6,10,11}, {0,2,3,7,10,11}, {6,7,8,10,11}, {2,5,9,10,11}, {0,3,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 167. `[[39,6,3]]` — T0·T1·CS01·CS23·CS24·CS35·CS45·CCZ023·CCZ024·CCZ035·CCZ045·CCZ123·CCZ124·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245·CCZ345

- gate `0+1+01+23+24+35+45+023+024+035+045+123+124+135+145+234+235+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,3,4,6}, {1,2,4,5,7}, {0,3,5,6,7,8}, {5,9}, {0,1,2,3,4,5,6,9}, {0,4,5,7,9}, {0,4,5,8,9}, {0,4,5,6,8,9}, {0,3,5,7,8,9}, {0,1,2,3,4,5,10}, {0,3,4,5,6,10}, {3,5,7,10}, {0,3,5,6,7,8,10}, {1,2,3,4,5,9,10}, {0,1,2,3,4,5,6,9,10}, {0,1,2,3,5,7,9,10}, {0,1,4,8,9,10}, {0,1,4,6,8,9,10}, {0,3,5,7,8,9,10}, {1,2,4,11}, {3,6,11}, {0,3,4,7,11}, {6,7,8,11}, {0,1,2,3,9,11}, {1,2,4,6,9,11}, {1,2,3,4,7,9,11}, {1,5,8,9,11}, {1,5,6,8,9,11}, {7,8,9,11}, {1,3,5,10,11}, {1,3,5,6,10,11}, {0,1,2,7,10,11}, {6,7,8,10,11}, {0,4,9,10,11}, {1,2,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 168. `[[39,6,3]]` — T0·T1·T2·CS01·CS02·CS03·CS04·CS05·CS12·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045

- gate `0+1+2+01+02+03+04+05+12+012+013+014+015+023+024+025+034+035+045`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,5,6}, {1,2,3,5,7}, {0,2,3,4,6,7,8}, {0,2,3,9}, {1,2,3,4,5,6,9}, {0,2,5,7,9}, {0,2,5,8,9}, {0,2,5,6,8,9}, {0,2,3,4,7,8,9}, {1,2,3,4,5,10}, {1,4,6,10}, {1,3,4,5,7,10}, {0,2,3,4,6,7,8,10}, {0,3,4,9,10}, {1,2,3,4,5,6,9,10}, {0,4,5,7,9,10}, {3,8,9,10}, {3,6,8,9,10}, {0,2,3,4,7,8,9,10}, {0,1,5,11}, {0,1,2,4,5,6,11}, {0,1,2,3,4,7,11}, {6,7,8,11}, {2,3,4,5,9,11}, {0,1,5,6,9,11}, {2,4,7,9,11}, {0,2,3,5,8,9,11}, {0,2,3,5,6,8,9,11}, {7,8,9,11}, {1,3,4,10,11}, {1,3,4,6,10,11}, {0,1,3,7,10,11}, {6,7,8,10,11}, {3,5,9,10,11}, {0,1,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 169. `[[39,6,3]]` — T0·T1·T2·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145

- gate `0+1+2+01+02+03+04+05+12+13+14+15+012+013+014+015+023+024+025+034+035+045+123+124+125+134+135+145`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,5,6}, {1,3,4,5,7}, {1,3,6,7,8}, {2,3,9}, {2,3,4,5,6,9}, {1,4,5,7,9}, {1,4,5,8,9}, {1,4,5,6,8,9}, {1,3,7,8,9}, {2,3,4,5,10}, {0,1,3,4,6,10}, {0,2,5,7,10}, {1,3,6,7,8,10}, {0,1,4,9,10}, {2,3,4,5,6,9,10}, {0,2,3,5,7,9,10}, {1,2,4,8,9,10}, {1,2,4,6,8,9,10}, {1,3,7,8,9,10}, {1,2,4,5,11}, {0,3,5,6,11}, {0,1,2,4,7,11}, {6,7,8,11}, {0,5,9,11}, {1,2,4,5,6,9,11}, {0,1,2,3,4,7,9,11}, {2,5,8,9,11}, {2,5,6,8,9,11}, {7,8,9,11}, {0,2,3,10,11}, {0,2,3,6,10,11}, {3,7,10,11}, {6,7,8,10,11}, {1,2,3,4,5,9,10,11}, {1,2,4,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 170. `[[39,6,3]]` — T0·T1·T2·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS24·CS25·CS34·CS35·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245·CCZ345

- gate `0+1+2+01+02+03+04+05+12+13+14+15+23+24+25+34+35+012+013+014+015+023+024+025+034+035+045+123+124+125+134+135+145+234+235+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,5,6}, {0,1,3,4,7}, {1,4,5,6,7,8}, {0,5,9}, {3,6,9}, {1,3,7,9}, {1,3,8,9}, {1,3,6,8,9}, {1,4,5,7,8,9}, {3,10}, {1,2,4,5,6,10}, {0,2,3,4,7,10}, {1,4,5,6,7,8,10}, {0,1,2,5,9,10}, {3,6,9,10}, {2,3,7,9,10}, {0,1,8,9,10}, {0,1,6,8,9,10}, {1,4,5,7,8,9,10}, {1,3,4,5,11}, {2,3,4,5,6,11}, {0,1,2,4,7,11}, {6,7,8,11}, {0,2,3,5,9,11}, {1,3,4,5,6,9,11}, {1,2,7,9,11}, {0,3,8,9,11}, {0,3,6,8,9,11}, {7,8,9,11}, {0,2,4,5,10,11}, {0,2,4,5,6,10,11}, {0,4,7,10,11}, {6,7,8,10,11}, {0,1,3,5,9,10,11}, {1,3,4,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 171. `[[39,6,3]]` — T0·T1·T2·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS34·CS35·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ345

- gate `0+1+2+01+02+03+04+05+12+13+14+15+34+35+012+013+014+015+023+024+025+034+035+045+123+124+125+134+135+145+234+235+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{2,3,6}, {0,1,3,4,7}, {1,2,5,6,7,8}, {1,9}, {0,1,2,3,4,5,6,9}, {0,2,3,5,7,9}, {0,2,3,5,8,9}, {0,2,3,5,6,8,9}, {1,2,5,7,8,9}, {0,1,2,3,4,5,10}, {1,2,3,5,6,10}, {0,7,10}, {1,2,5,6,7,8,10}, {3,4,9,10}, {0,1,2,3,4,5,6,9,10}, {0,1,2,4,5,7,9,10}, {0,1,2,3,8,9,10}, {0,1,2,3,6,8,9,10}, {1,2,5,7,8,9,10}, {0,3,4,11}, {0,1,6,11}, {2,3,5,7,11}, {6,7,8,11}, {0,2,4,5,9,11}, {0,3,4,6,9,11}, {1,3,4,7,9,11}, {1,5,8,9,11}, {1,5,6,8,9,11}, {7,8,9,11}, {0,5,10,11}, {0,5,6,10,11}, {1,2,4,5,7,10,11}, {6,7,8,10,11}, {0,1,2,3,5,9,10,11}, {0,3,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 172. `[[39,6,3]]` — T0·T1·T2·CS01·CS02·CS03·CS04·CS05·CS12·CS34·CS35·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ134·CCZ135·CCZ234·CCZ235·CCZ345

- gate `0+1+2+01+02+03+04+05+12+34+35+012+013+014+015+023+024+025+034+035+045+134+135+234+235+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,5,6}, {2,3,7}, {1,2,3,5,6,7,8}, {2,4,9}, {1,2,4,5,6,9}, {1,2,4,7,9}, {1,2,4,8,9}, {1,2,4,6,8,9}, {1,2,3,5,7,8,9}, {1,2,4,5,10}, {0,1,2,3,5,6,10}, {0,2,3,5,7,10}, {1,2,3,5,6,7,8,10}, {0,2,4,5,9,10}, {1,2,4,5,6,9,10}, {0,1,2,4,5,7,9,10}, {1,2,8,9,10}, {1,2,6,8,9,10}, {1,2,3,5,7,8,9,10}, {3,4,11}, {0,3,4,5,6,11}, {0,1,3,4,5,7,11}, {6,7,8,11}, {0,1,5,9,11}, {3,4,6,9,11}, {0,5,7,9,11}, {4,8,9,11}, {4,6,8,9,11}, {7,8,9,11}, {0,3,5,10,11}, {0,3,5,6,10,11}, {1,3,4,7,10,11}, {6,7,8,10,11}, {1,9,10,11}, {3,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 173. `[[39,6,3]]` — T0·T1·T2·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CS34·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234

- gate `0+1+2+01+02+03+04+12+13+14+23+24+34+35+45+012+013+014+023+024+034+123+124+134+234`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {0,1,3,4,5,7}, {1,3,5,6,7,8}, {0,5,9}, {4,5,6,9}, {1,4,5,7,9}, {1,4,5,8,9}, {1,4,5,6,8,9}, {1,3,5,7,8,9}, {4,5,10}, {1,3,4,5,6,10}, {0,3,5,7,10}, {1,3,5,6,7,8,10}, {0,1,4,5,9,10}, {4,5,6,9,10}, {5,7,9,10}, {0,1,2,4,8,9,10}, {0,1,2,4,6,8,9,10}, {1,3,5,7,8,9,10}, {1,3,4,11}, {3,6,11}, {0,1,3,4,7,11}, {6,7,8,11}, {0,9,11}, {1,3,4,6,9,11}, {1,4,7,9,11}, {0,2,5,8,9,11}, {0,2,5,6,8,9,11}, {7,8,9,11}, {0,2,3,5,10,11}, {0,2,3,5,6,10,11}, {0,3,7,10,11}, {6,7,8,10,11}, {0,1,4,9,10,11}, {1,3,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 174. `[[39,6,3]]` — T0·T1·T2·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234·CCZ345

- gate `0+1+2+01+02+03+04+12+13+14+23+24+35+45+012+013+014+023+024+034+123+124+134+234+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {1,3,4,7}, {0,1,3,5,6,7,8}, {0,3,9}, {3,4,5,6,9}, {0,1,4,5,7,9}, {0,1,4,5,8,9}, {0,1,4,5,6,8,9}, {0,1,3,5,7,8,9}, {3,4,5,10}, {1,4,6,10}, {3,5,7,10}, {0,1,3,5,6,7,8,10}, {0,1,3,4,5,9,10}, {3,4,5,6,9,10}, {0,7,9,10}, {1,2,3,4,5,8,9,10}, {1,2,3,4,5,6,8,9,10}, {0,1,3,5,7,8,9,10}, {0,1,4,11}, {0,5,6,11}, {0,1,3,4,7,11}, {6,7,8,11}, {3,9,11}, {0,1,4,6,9,11}, {1,4,5,7,9,11}, {0,2,3,8,9,11}, {0,2,3,6,8,9,11}, {7,8,9,11}, {2,3,5,10,11}, {2,3,5,6,10,11}, {0,3,5,7,10,11}, {6,7,8,10,11}, {1,3,4,5,9,10,11}, {0,1,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 175. `[[39,6,3]]` — T0·T1·T2·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS34·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234·CCZ235·CCZ245

- gate `0+1+2+01+02+03+04+12+13+14+34+35+45+012+013+014+023+024+034+123+124+134+234+235+245`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{2,3,5,6}, {0,1,3,4,5,7}, {2,4,6,7,8}, {4,5,9}, {0,1,2,3,4,6,9}, {0,1,2,3,4,5,7,9}, {0,1,2,3,4,5,8,9}, {0,1,2,3,4,5,6,8,9}, {2,4,7,8,9}, {0,1,2,3,4,10}, {1,2,3,4,6,10}, {0,4,7,10}, {2,4,6,7,8,10}, {1,3,4,9,10}, {0,1,2,3,4,6,9,10}, {0,2,4,7,9,10}, {0,2,3,8,9,10}, {0,2,3,6,8,9,10}, {2,4,7,8,9,10}, {0,1,3,11}, {0,5,6,11}, {1,2,3,5,7,11}, {6,7,8,11}, {0,2,5,9,11}, {0,1,3,6,9,11}, {1,3,5,7,9,11}, {1,4,5,8,9,11}, {1,4,5,6,8,9,11}, {7,8,9,11}, {0,1,4,10,11}, {0,1,4,6,10,11}, {2,7,10,11}, {6,7,8,10,11}, {0,1,2,3,9,10,11}, {0,1,3,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 176. `[[39,6,3]]` — T0·T1·T2·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ235·CCZ245·CCZ345

- gate `0+1+2+01+02+03+04+12+13+14+35+45+012+013+014+023+024+034+123+124+134+235+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {0,2,3,4,5,7}, {0,1,6,7,8}, {1,9}, {2,3,4,5,6,9}, {0,1,3,4,7,9}, {0,1,3,4,8,9}, {0,1,3,4,6,8,9}, {0,1,7,8,9}, {2,3,4,5,10}, {0,2,3,6,10}, {2,4,7,10}, {0,1,6,7,8,10}, {0,1,3,5,9,10}, {2,3,4,5,6,9,10}, {1,4,5,7,9,10}, {0,3,8,9,10}, {0,3,6,8,9,10}, {0,1,7,8,9,10}, {0,1,2,3,4,5,11}, {1,2,4,6,11}, {0,1,2,3,7,11}, {6,7,8,11}, {4,5,9,11}, {0,1,2,3,4,5,6,9,11}, {0,3,5,7,9,11}, {1,4,8,9,11}, {1,4,6,8,9,11}, {7,8,9,11}, {2,10,11}, {2,6,10,11}, {1,2,5,7,10,11}, {6,7,8,10,11}, {0,3,4,9,10,11}, {0,1,2,3,4,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 177. `[[39,6,3]]` — T0·T1·T2·CS01·CS02·CS03·CS04·CS12·CS34·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245

- gate `0+1+2+01+02+03+04+12+34+35+45+012+013+014+023+024+034+134+135+145+234+235+245`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{1,2,4,5,6}, {0,1,2,3,4,5,7}, {2,5,6,7,8}, {2,9}, {0,1,2,3,4,6,9}, {0,2,4,7,9}, {0,2,4,8,9}, {0,2,4,6,8,9}, {2,5,7,8,9}, {0,1,2,3,4,10}, {1,2,5,6,10}, {0,1,2,4,5,7,10}, {2,5,6,7,8,10}, {2,3,9,10}, {0,1,2,3,4,6,9,10}, {0,2,3,4,7,9,10}, {0,2,8,9,10}, {0,2,6,8,9,10}, {2,5,7,8,9,10}, {0,1,3,4,5,11}, {0,1,4,5,6,11}, {1,5,7,11}, {6,7,8,11}, {0,3,4,9,11}, {0,1,3,4,5,6,9,11}, {3,7,9,11}, {4,8,9,11}, {4,6,8,9,11}, {7,8,9,11}, {0,1,5,10,11}, {0,1,5,6,10,11}, {1,3,5,7,10,11}, {6,7,8,10,11}, {0,4,9,10,11}, {0,1,3,4,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 178. `[[39,6,3]]` — T0·T1·T2·CS01·CS02·CS03·CS04·CS12·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ135·CCZ145·CCZ235·CCZ245·CCZ345

- gate `0+1+2+01+02+03+04+12+35+45+012+013+014+023+024+034+135+145+235+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{1,2,3,4,5,6}, {1,2,7}, {0,2,4,5,6,7,8}, {0,2,4,9}, {1,2,5,6,9}, {2,3,7,9}, {2,3,8,9}, {2,3,6,8,9}, {0,2,4,5,7,8,9}, {1,2,5,10}, {0,1,3,4,5,6,10}, {1,5,7,10}, {0,2,4,5,6,7,8,10}, {0,4,5,9,10}, {1,2,5,6,9,10}, {3,5,7,9,10}, {0,3,8,9,10}, {0,3,6,8,9,10}, {0,2,4,5,7,8,9,10}, {0,1,4,11}, {0,1,2,4,5,6,11}, {1,2,3,5,7,11}, {6,7,8,11}, {0,2,3,4,5,9,11}, {0,1,4,6,9,11}, {2,5,7,9,11}, {0,2,8,9,11}, {0,2,6,8,9,11}, {7,8,9,11}, {1,4,5,10,11}, {1,4,5,6,10,11}, {1,3,7,10,11}, {6,7,8,10,11}, {0,3,4,9,10,11}, {0,1,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 179. `[[39,6,3]]` — T0·T1·T2·CS01·CS02·CS03·CS12·CS13·CS23·CS34·CS35·CCZ012·CCZ013·CCZ023·CCZ123·CCZ345

- gate `0+1+2+01+02+03+12+13+23+34+35+012+013+023+123+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,6}, {0,3,4,5,7}, {0,5,6,7,8}, {3,5,9}, {4,5,6,9}, {0,3,5,7,9}, {0,3,5,8,9}, {0,3,5,6,8,9}, {0,5,7,8,9}, {4,5,10}, {0,1,5,6,10}, {1,5,7,10}, {0,5,6,7,8,10}, {0,1,4,5,9,10}, {4,5,6,9,10}, {1,4,5,7,9,10}, {0,2,8,9,10}, {0,2,6,8,9,10}, {0,5,7,8,9,10}, {0,4,11}, {1,3,6,11}, {0,1,3,7,11}, {6,7,8,11}, {1,3,4,9,11}, {0,4,6,9,11}, {0,1,3,4,7,9,11}, {2,3,5,8,9,11}, {2,3,5,6,8,9,11}, {7,8,9,11}, {1,2,5,10,11}, {1,2,5,6,10,11}, {4,7,10,11}, {6,7,8,10,11}, {0,9,10,11}, {0,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 180. `[[39,6,3]]` — T0·T1·T2·CS01·CS02·CS03·CS12·CS13·CS34·CS35·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234·CCZ235·CCZ345

- gate `0+1+2+01+02+03+12+13+34+35+012+013+023+123+234+235+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{2,4,5,6}, {0,2,3,4,5,7}, {1,2,3,4,6,7,8}, {2,3,5,9}, {0,1,2,3,6,9}, {0,2,3,5,7,9}, {0,2,3,5,8,9}, {0,2,3,5,6,8,9}, {1,2,3,4,7,8,9}, {0,1,2,3,10}, {2,3,4,6,10}, {0,2,3,4,7,10}, {1,2,3,4,6,7,8,10}, {2,3,9,10}, {0,1,2,3,6,9,10}, {0,2,3,7,9,10}, {0,2,8,9,10}, {0,2,6,8,9,10}, {1,2,3,4,7,8,9,10}, {0,4,11}, {0,4,5,6,11}, {4,5,7,11}, {6,7,8,11}, {0,5,9,11}, {0,4,6,9,11}, {5,7,9,11}, {3,5,8,9,11}, {3,5,6,8,9,11}, {7,8,9,11}, {0,3,4,10,11}, {0,3,4,6,10,11}, {4,7,10,11}, {6,7,8,10,11}, {0,9,10,11}, {0,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 181. `[[39,6,3]]` — T0·T1·T2·CS01·CS02·CS03·CS12·CS34·CS35·CCZ012·CCZ013·CCZ023·CCZ134·CCZ135·CCZ234·CCZ235·CCZ345

- gate `0+1+2+01+02+03+12+34+35+012+013+023+134+135+234+235+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{1,2,3,4,5,6}, {1,2,7}, {0,1,2,3,5,6,7,8}, {0,1,2,3,4,9}, {1,2,4,5,6,9}, {1,2,4,7,9}, {1,2,4,8,9}, {1,2,4,6,8,9}, {0,1,2,3,5,7,8,9}, {1,2,4,5,10}, {0,2,5,6,10}, {2,3,5,7,10}, {0,1,2,3,5,6,7,8,10}, {0,2,4,5,9,10}, {1,2,4,5,6,9,10}, {2,3,4,5,7,9,10}, {0,2,3,8,9,10}, {0,2,3,6,8,9,10}, {0,1,2,3,5,7,8,9,10}, {0,3,4,11}, {0,1,4,5,6,11}, {1,3,4,5,7,11}, {6,7,8,11}, {0,1,5,9,11}, {0,3,4,6,9,11}, {1,3,5,7,9,11}, {0,1,3,4,8,9,11}, {0,1,3,4,6,8,9,11}, {7,8,9,11}, {3,5,10,11}, {3,5,6,10,11}, {4,7,10,11}, {6,7,8,10,11}, {0,3,9,10,11}, {0,3,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 182. `[[39,6,3]]` — T0·T1·T2·CS01·CS02·CS12·CS34·CS35·CCZ012·CCZ034·CCZ035·CCZ134·CCZ135·CCZ234·CCZ235·CCZ345

- gate `0+1+2+01+02+12+34+35+012+034+035+134+135+234+235+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,6}, {0,2,4,5,7}, {1,2,6,7,8}, {2,9}, {0,1,2,4,5,6,9}, {1,2,3,7,9}, {1,2,3,8,9}, {1,2,3,6,8,9}, {1,2,7,8,9}, {0,1,2,4,5,10}, {0,1,2,3,5,6,10}, {0,2,5,7,10}, {1,2,6,7,8,10}, {2,4,9,10}, {0,1,2,4,5,6,9,10}, {1,2,3,4,7,9,10}, {1,2,3,5,8,9,10}, {1,2,3,5,6,8,9,10}, {1,2,7,8,9,10}, {0,4,5,11}, {0,5,6,11}, {0,1,3,5,7,11}, {6,7,8,11}, {1,3,4,9,11}, {0,4,5,6,9,11}, {4,7,9,11}, {5,8,9,11}, {5,6,8,9,11}, {7,8,9,11}, {0,10,11}, {0,6,10,11}, {0,1,3,4,5,7,10,11}, {6,7,8,10,11}, {1,3,9,10,11}, {0,4,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 183. `[[39,6,3]]` — T0·T1·T2·CS01·CS02·CS12·CS34·CS35·CS45·CCZ012·CCZ034·CCZ035·CCZ045·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245

- gate `0+1+2+01+02+12+34+35+45+012+034+035+045+134+135+145+234+235+245`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {0,1,2,5,7}, {1,4,6,7,8}, {1,9}, {0,1,2,4,5,6,9}, {1,3,7,9}, {1,3,8,9}, {1,3,6,8,9}, {1,4,7,8,9}, {0,1,2,4,5,10}, {0,3,4,6,10}, {0,4,7,10}, {1,4,6,7,8,10}, {2,4,5,9,10}, {0,1,2,4,5,6,9,10}, {2,3,4,5,7,9,10}, {2,3,8,9,10}, {2,3,6,8,9,10}, {1,4,7,8,9,10}, {0,2,5,11}, {0,1,4,6,11}, {0,1,3,4,7,11}, {6,7,8,11}, {1,2,3,4,5,9,11}, {0,2,5,6,9,11}, {1,2,4,5,7,9,11}, {1,2,8,9,11}, {1,2,6,8,9,11}, {7,8,9,11}, {0,2,4,10,11}, {0,2,4,6,10,11}, {0,2,3,5,7,10,11}, {6,7,8,10,11}, {3,9,10,11}, {0,2,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 184. `[[39,6,3]]` — T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145

- gate `0+1+2+3+01+02+03+04+05+12+13+14+15+23+012+013+014+015+023+024+025+034+035+045+123+124+125+134+135+145`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,5,6}, {0,1,2,4,5,7}, {1,2,3,6,7,8}, {0,2,9}, {2,3,4,5,6,9}, {1,2,3,4,5,7,9}, {1,2,3,4,5,8,9}, {1,2,3,4,5,6,8,9}, {1,2,3,7,8,9}, {2,3,4,5,10}, {1,3,4,6,10}, {0,5,7,10}, {1,2,3,6,7,8,10}, {0,1,4,9,10}, {2,3,4,5,6,9,10}, {3,5,7,9,10}, {0,1,3,4,8,9,10}, {0,1,3,4,6,8,9,10}, {1,2,3,7,8,9,10}, {1,4,5,11}, {2,5,6,11}, {0,1,2,3,4,7,11}, {6,7,8,11}, {0,2,3,5,9,11}, {1,4,5,6,9,11}, {1,2,4,7,9,11}, {0,2,5,8,9,11}, {0,2,5,6,8,9,11}, {7,8,9,11}, {0,10,11}, {0,6,10,11}, {0,3,7,10,11}, {6,7,8,10,11}, {0,1,3,4,5,9,10,11}, {1,4,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 185. `[[39,6,3]]` — T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS24·CS25·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245

- gate `0+1+2+3+01+02+03+04+05+12+13+14+15+23+24+25+012+013+014+015+023+024+025+034+035+045+123+124+125+134+135+145+234+235+245`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,5,6}, {0,1,5,7}, {1,4,6,7,8}, {0,3,9}, {3,4,5,6,9}, {1,5,7,9}, {1,5,8,9}, {1,5,6,8,9}, {1,4,7,8,9}, {3,4,5,10}, {1,4,5,6,10}, {0,3,4,7,10}, {1,4,6,7,8,10}, {0,1,4,5,9,10}, {3,4,5,6,9,10}, {3,4,7,9,10}, {0,1,2,3,5,8,9,10}, {0,1,2,3,5,6,8,9,10}, {1,4,7,8,9,10}, {1,3,5,11}, {4,6,11}, {0,1,3,4,5,7,11}, {6,7,8,11}, {0,4,9,11}, {1,3,5,6,9,11}, {1,3,4,5,7,9,11}, {0,2,3,8,9,11}, {0,2,3,6,8,9,11}, {7,8,9,11}, {0,2,3,4,10,11}, {0,2,3,4,6,10,11}, {0,7,10,11}, {6,7,8,10,11}, {0,1,3,5,9,10,11}, {1,3,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 186. `[[39,6,3]]` — T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS24·CS25·CS34·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245·CCZ345

- gate `0+1+2+3+01+02+03+04+05+12+13+14+15+23+24+25+34+35+45+012+013+014+015+023+024+025+034+035+045+123+124+125+134+135+145+234+235+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,5,6}, {0,2,5,7}, {2,6,7,8}, {0,4,5,9}, {4,6,9}, {2,4,5,7,9}, {2,4,5,8,9}, {2,4,5,6,8,9}, {2,7,8,9}, {4,10}, {1,2,6,10}, {0,1,7,10}, {2,6,7,8,10}, {0,1,2,4,9,10}, {4,6,9,10}, {1,4,7,9,10}, {0,2,3,8,9,10}, {0,2,3,6,8,9,10}, {2,7,8,9,10}, {2,4,11}, {1,4,5,6,11}, {0,1,2,4,5,7,11}, {6,7,8,11}, {0,1,5,9,11}, {2,4,6,9,11}, {1,2,5,7,9,11}, {0,3,4,5,8,9,11}, {0,3,4,5,6,8,9,11}, {7,8,9,11}, {0,1,3,10,11}, {0,1,3,6,10,11}, {0,4,7,10,11}, {6,7,8,10,11}, {0,2,9,10,11}, {2,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 187. `[[39,6,3]]` — T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS24·CS25·CS45·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245·CCZ345

- gate `0+1+2+3+01+02+03+04+05+12+13+14+15+23+24+25+45+012+013+014+015+023+024+025+034+035+045+123+124+125+134+135+145+234+235+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,5,6}, {0,1,4,5,7}, {0,3,4,6,7,8}, {1,9}, {3,5,6,9}, {0,3,5,7,9}, {0,3,5,8,9}, {0,3,5,6,8,9}, {0,3,4,7,8,9}, {3,5,10}, {0,3,4,5,6,10}, {1,4,7,10}, {0,3,4,6,7,8,10}, {0,1,5,9,10}, {3,5,6,9,10}, {3,7,9,10}, {0,1,2,3,5,8,9,10}, {0,1,2,3,5,6,8,9,10}, {0,3,4,7,8,9,10}, {0,4,5,11}, {4,6,11}, {0,1,3,4,5,7,11}, {6,7,8,11}, {1,3,9,11}, {0,4,5,6,9,11}, {0,5,7,9,11}, {1,2,8,9,11}, {1,2,6,8,9,11}, {7,8,9,11}, {1,2,4,10,11}, {1,2,4,6,10,11}, {1,3,4,7,10,11}, {6,7,8,10,11}, {0,1,3,5,9,10,11}, {0,4,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 188. `[[39,6,3]]` — T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS45·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ245·CCZ345

- gate `0+1+2+3+01+02+03+04+05+12+13+14+15+23+45+012+013+014+015+023+024+025+034+035+045+123+124+125+134+135+145+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,5,6}, {0,2,3,7}, {2,3,4,5,6,7,8}, {0,2,3,4,9}, {2,3,5,6,9}, {2,3,7,9}, {2,3,8,9}, {2,3,6,8,9}, {2,3,4,5,7,8,9}, {2,3,5,10}, {1,3,5,6,10}, {0,1,3,4,5,7,10}, {2,3,4,5,6,7,8,10}, {0,1,3,5,9,10}, {2,3,5,6,9,10}, {1,3,4,5,7,9,10}, {0,3,4,8,9,10}, {0,3,4,6,8,9,10}, {2,3,4,5,7,8,9,10}, {4,11}, {1,2,5,6,11}, {0,1,2,4,5,7,11}, {6,7,8,11}, {0,1,2,5,9,11}, {4,6,9,11}, {1,2,4,5,7,9,11}, {0,2,4,8,9,11}, {0,2,4,6,8,9,11}, {7,8,9,11}, {0,1,4,5,10,11}, {0,1,4,5,6,10,11}, {0,7,10,11}, {6,7,8,10,11}, {0,4,9,10,11}, {4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 189. `[[39,6,3]]` — T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS23·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123

- gate `0+1+2+3+01+02+03+04+05+12+13+23+012+013+014+015+023+024+025+034+035+045+123`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,5,6}, {2,7}, {1,2,4,5,6,7,8}, {2,3,4,5,9}, {1,2,3,6,9}, {1,2,7,9}, {1,2,8,9}, {1,2,6,8,9}, {1,2,4,5,7,8,9}, {1,2,3,10}, {1,5,6,10}, {3,4,7,10}, {1,2,4,5,6,7,8,10}, {5,9,10}, {1,2,3,6,9,10}, {1,3,4,7,9,10}, {0,1,3,4,8,9,10}, {0,1,3,4,6,8,9,10}, {1,2,4,5,7,8,9,10}, {3,4,5,11}, {2,5,6,11}, {1,2,3,4,7,11}, {6,7,8,11}, {1,2,5,9,11}, {3,4,5,6,9,11}, {2,3,4,7,9,11}, {0,2,3,4,8,9,11}, {0,2,3,4,6,8,9,11}, {7,8,9,11}, {0,3,4,5,10,11}, {0,3,4,5,6,10,11}, {1,7,10,11}, {6,7,8,10,11}, {1,3,4,5,9,10,11}, {3,4,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 190. `[[39,6,3]]` — T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS23·CS45·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ145·CCZ245·CCZ345

- gate `0+1+2+3+01+02+03+04+05+12+13+23+45+012+013+014+015+023+024+025+034+035+045+123+145+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{1,2,3,4,6}, {2,3,4,7}, {1,2,3,4,5,6,7,8}, {2,3,9}, {1,2,3,5,6,9}, {0,1,2,3,5,7,9}, {0,1,2,3,5,8,9}, {0,1,2,3,5,6,8,9}, {1,2,3,4,5,7,8,9}, {1,2,3,5,10}, {1,3,4,5,6,10}, {0,3,4,7,10}, {1,2,3,4,5,6,7,8,10}, {0,3,9,10}, {1,2,3,5,6,9,10}, {1,3,5,7,9,10}, {0,1,3,8,9,10}, {0,1,3,6,8,9,10}, {1,2,3,4,5,7,8,9,10}, {4,11}, {0,2,4,6,11}, {1,2,4,5,7,11}, {6,7,8,11}, {1,2,5,9,11}, {4,6,9,11}, {0,2,7,9,11}, {2,5,8,9,11}, {2,5,6,8,9,11}, {7,8,9,11}, {0,4,5,10,11}, {0,4,5,6,10,11}, {0,1,4,5,7,10,11}, {6,7,8,10,11}, {0,1,5,9,10,11}, {4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 191. `[[39,6,3]]` — T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CS34·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234

- gate `0+1+2+3+01+02+03+04+12+13+14+23+24+34+45+012+013+014+023+024+034+123+124+134+234`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {0,2,4,5,7}, {2,5,6,7,8}, {0,4,5,9}, {5,6,9}, {2,4,5,7,9}, {2,4,5,8,9}, {2,4,5,6,8,9}, {2,5,7,8,9}, {5,10}, {1,2,5,6,10}, {0,1,5,7,10}, {2,5,6,7,8,10}, {0,1,2,5,9,10}, {5,6,9,10}, {1,5,7,9,10}, {0,2,3,8,9,10}, {0,2,3,6,8,9,10}, {2,5,7,8,9,10}, {2,11}, {1,4,6,11}, {0,1,2,4,7,11}, {6,7,8,11}, {0,1,4,9,11}, {2,6,9,11}, {1,2,4,7,9,11}, {0,3,4,5,8,9,11}, {0,3,4,5,6,8,9,11}, {7,8,9,11}, {0,1,3,5,10,11}, {0,1,3,5,6,10,11}, {0,7,10,11}, {6,7,8,10,11}, {0,2,9,10,11}, {2,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 192. `[[39,6,3]]` — T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234·CCZ345

- gate `0+1+2+3+01+02+03+04+12+13+14+23+24+45+012+013+014+023+024+034+123+124+134+234+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{3,5,6}, {0,1,2,4,7}, {0,2,4,6,7,8}, {0,2,3,4,9}, {0,1,2,3,4,6,9}, {1,4,5,7,9}, {1,4,5,8,9}, {1,4,5,6,8,9}, {0,2,4,7,8,9}, {0,1,2,3,4,10}, {0,4,5,6,10}, {1,2,3,4,7,10}, {0,2,4,6,7,8,10}, {2,4,9,10}, {0,1,2,3,4,6,9,10}, {0,1,3,4,5,7,9,10}, {0,1,3,5,8,9,10}, {0,1,3,5,6,8,9,10}, {0,2,4,7,8,9,10}, {1,3,11}, {0,1,6,11}, {2,3,5,7,11}, {6,7,8,11}, {1,2,5,9,11}, {1,3,6,9,11}, {0,3,7,9,11}, {0,3,4,8,9,11}, {0,3,4,6,8,9,11}, {7,8,9,11}, {1,3,4,10,11}, {1,3,4,6,10,11}, {0,2,5,7,10,11}, {6,7,8,10,11}, {0,1,2,3,5,9,10,11}, {1,3,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 193. `[[39,6,3]]` — T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ245·CCZ345

- gate `0+1+2+3+01+02+03+04+12+13+14+23+45+012+013+014+023+024+034+123+124+134+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {0,2,3,5,7}, {0,1,3,4,6,7,8}, {1,3,9}, {2,3,4,5,6,9}, {0,1,3,7,9}, {0,1,3,8,9}, {0,1,3,6,8,9}, {0,1,3,4,7,8,9}, {2,3,4,5,10}, {0,2,4,5,6,10}, {2,4,5,7,10}, {0,1,3,4,6,7,8,10}, {0,1,4,9,10}, {2,3,4,5,6,9,10}, {1,4,7,9,10}, {0,5,8,9,10}, {0,5,6,8,9,10}, {0,1,3,4,7,8,9,10}, {0,1,2,5,11}, {1,2,3,4,5,6,11}, {0,1,2,3,4,5,7,11}, {6,7,8,11}, {3,4,9,11}, {0,1,2,5,6,9,11}, {0,3,4,7,9,11}, {1,3,5,8,9,11}, {1,3,5,6,8,9,11}, {7,8,9,11}, {2,4,10,11}, {2,4,6,10,11}, {1,2,5,7,10,11}, {6,7,8,10,11}, {0,9,10,11}, {0,1,2,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 194. `[[39,6,3]]` — T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS12·CS13·CS23·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ145·CCZ245·CCZ345

- gate `0+1+2+3+01+02+03+04+12+13+23+45+012+013+014+023+024+034+123+145+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {3,4,5,7}, {1,4,6,7,8}, {2,9}, {1,2,3,5,6,9}, {1,7,9}, {1,8,9}, {1,6,8,9}, {1,4,7,8,9}, {1,2,3,5,10}, {0,1,4,6,10}, {0,2,4,7,10}, {1,4,6,7,8,10}, {0,3,5,9,10}, {1,2,3,5,6,9,10}, {0,1,2,3,5,7,9,10}, {1,2,3,8,9,10}, {1,2,3,6,8,9,10}, {1,4,7,8,9,10}, {2,3,4,5,11}, {0,4,6,11}, {0,1,2,4,7,11}, {6,7,8,11}, {0,1,3,5,9,11}, {2,3,4,5,6,9,11}, {0,2,3,5,7,9,11}, {2,3,8,9,11}, {2,3,6,8,9,11}, {7,8,9,11}, {0,2,3,4,10,11}, {0,2,3,4,6,10,11}, {1,3,4,5,7,10,11}, {6,7,8,10,11}, {1,2,9,10,11}, {2,3,4,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 195. `[[39,6,3]]` — T0·T1·T2·T3·CS01·CS02·CS03·CS12·CS13·CS23·CS45·CCZ012·CCZ013·CCZ023·CCZ045·CCZ123·CCZ145·CCZ245·CCZ345

- gate `0+1+2+3+01+02+03+12+13+23+45+012+013+023+045+123+145+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {2,3,7}, {0,2,3,4,5,6,7,8}, {1,2,3,9}, {0,1,2,3,4,5,6,9}, {0,2,3,5,7,9}, {0,2,3,5,8,9}, {0,2,3,5,6,8,9}, {0,2,3,4,5,7,8,9}, {0,1,2,3,4,5,10}, {0,3,4,5,6,10}, {1,3,4,7,10}, {0,2,3,4,5,6,7,8,10}, {3,4,9,10}, {0,1,2,3,4,5,6,9,10}, {0,1,3,4,5,7,9,10}, {0,1,3,8,9,10}, {0,1,3,6,8,9,10}, {0,2,3,4,5,7,8,9,10}, {1,11}, {2,4,6,11}, {0,1,2,4,5,7,11}, {6,7,8,11}, {0,2,4,5,9,11}, {1,6,9,11}, {1,2,4,7,9,11}, {1,2,5,8,9,11}, {1,2,5,6,8,9,11}, {7,8,9,11}, {1,4,5,10,11}, {1,4,5,6,10,11}, {0,5,7,10,11}, {6,7,8,10,11}, {0,1,5,9,10,11}, {1,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 196. `[[39,6,3]]` — T0·T1·T2·T3·CS01·CS02·CS12·CS34·CS35·CCZ012·CCZ345

- gate `0+1+2+3+01+02+12+34+35+012+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,6}, {1,3,4,7}, {5,6,7,8}, {1,9}, {3,4,5,6,9}, {3,5,7,9}, {3,5,8,9}, {3,5,6,8,9}, {5,7,8,9}, {3,4,5,10}, {0,6,10}, {0,1,3,5,7,10}, {5,6,7,8,10}, {0,1,4,5,9,10}, {3,4,5,6,9,10}, {0,3,4,7,9,10}, {1,2,3,5,8,9,10}, {1,2,3,5,6,8,9,10}, {5,7,8,9,10}, {3,4,11}, {0,3,5,6,11}, {0,1,7,11}, {6,7,8,11}, {0,1,3,4,9,11}, {3,4,6,9,11}, {0,4,5,7,9,11}, {1,2,8,9,11}, {1,2,6,8,9,11}, {7,8,9,11}, {0,1,2,3,5,10,11}, {0,1,2,3,5,6,10,11}, {1,4,5,7,10,11}, {6,7,8,10,11}, {1,3,5,9,10,11}, {3,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 197. `[[39,6,3]]` — T0·T1·T2·T3·T4·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS24·CS25·CS34·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245

- gate `0+1+2+3+4+01+02+03+04+05+12+13+14+15+23+24+25+34+012+013+014+015+023+024+025+034+035+045+123+124+125+134+135+145+234+235+245`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,5,6}, {0,7}, {4,6,7,8}, {0,3,5,9}, {3,4,5,6,9}, {4,5,7,9}, {4,5,8,9}, {4,5,6,8,9}, {4,7,8,9}, {3,4,5,10}, {1,4,6,10}, {0,1,3,7,10}, {4,6,7,8,10}, {0,1,5,9,10}, {3,4,5,6,9,10}, {1,3,4,5,7,9,10}, {0,2,3,4,8,9,10}, {0,2,3,4,6,8,9,10}, {4,7,8,9,10}, {3,5,11}, {1,5,6,11}, {0,1,3,4,5,7,11}, {6,7,8,11}, {0,1,4,9,11}, {3,5,6,9,11}, {1,3,7,9,11}, {0,2,3,5,8,9,11}, {0,2,3,5,6,8,9,11}, {7,8,9,11}, {0,1,2,3,10,11}, {0,1,2,3,6,10,11}, {0,4,5,7,10,11}, {6,7,8,10,11}, {0,3,4,9,10,11}, {3,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 198. `[[39,6,3]]` — T0·T1·T2·T3·T4·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS24·CS25·CS34·CS35·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245·CCZ345

- gate `0+1+2+3+4+01+02+03+04+05+12+13+14+15+23+24+25+34+35+012+013+014+015+023+024+025+034+035+045+123+124+125+134+135+145+234+235+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,5,6}, {0,1,4,7}, {1,4,5,6,7,8}, {0,4,9}, {4,5,6,9}, {1,4,7,9}, {1,4,8,9}, {1,4,6,8,9}, {1,4,5,7,8,9}, {4,5,10}, {1,2,4,5,6,10}, {0,2,4,5,7,10}, {1,4,5,6,7,8,10}, {0,1,2,4,5,9,10}, {4,5,6,9,10}, {2,4,5,7,9,10}, {0,1,3,4,8,9,10}, {0,1,3,4,6,8,9,10}, {1,4,5,7,8,9,10}, {1,11}, {2,5,6,11}, {0,1,2,5,7,11}, {6,7,8,11}, {0,2,5,9,11}, {1,6,9,11}, {1,2,5,7,9,11}, {0,3,8,9,11}, {0,3,6,8,9,11}, {7,8,9,11}, {0,2,3,5,10,11}, {0,2,3,5,6,10,11}, {0,7,10,11}, {6,7,8,10,11}, {0,1,9,10,11}, {1,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 199. `[[39,6,3]]` — T0·T1·T2·T3·T4·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS24·CS34·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ234

- gate `0+1+2+3+4+01+02+03+04+05+12+13+14+15+23+24+34+012+013+014+015+023+024+025+034+035+045+123+124+125+134+135+145+234`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,5,6}, {0,4,5,7}, {2,4,5,6,7,8}, {0,3,4,9}, {2,3,4,6,9}, {2,4,7,9}, {2,4,8,9}, {2,4,6,8,9}, {2,4,5,7,8,9}, {2,3,4,10}, {2,5,6,10}, {0,3,5,7,10}, {2,4,5,6,7,8,10}, {0,9,10}, {2,3,4,6,9,10}, {2,3,7,9,10}, {0,1,2,3,8,9,10}, {0,1,2,3,6,8,9,10}, {2,4,5,7,8,9,10}, {3,5,11}, {4,5,6,11}, {0,2,3,4,5,7,11}, {6,7,8,11}, {0,2,4,9,11}, {3,5,6,9,11}, {3,4,7,9,11}, {0,1,3,4,8,9,11}, {0,1,3,4,6,8,9,11}, {7,8,9,11}, {0,1,3,5,10,11}, {0,1,3,5,6,10,11}, {0,2,5,7,10,11}, {6,7,8,10,11}, {0,2,3,9,10,11}, {3,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 200. `[[39,6,3]]` — T0·T1·T2·T3·T4·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS23·CS24·CS34·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ134·CCZ234

- gate `0+1+2+3+4+01+02+03+04+05+12+13+14+23+24+34+012+013+014+015+023+024+025+034+035+045+123+124+134+234`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,5,6}, {0,1,2,3,5,7}, {0,2,3,6,7,8}, {2,3,4,9}, {1,2,3,4,5,6,9}, {0,2,3,5,7,9}, {0,2,3,5,8,9}, {0,2,3,5,6,8,9}, {0,2,3,7,8,9}, {1,2,3,4,5,10}, {0,1,2,6,10}, {1,2,4,5,7,10}, {0,2,3,6,7,8,10}, {0,2,9,10}, {1,2,3,4,5,6,9,10}, {2,4,5,7,9,10}, {0,2,4,8,9,10}, {0,2,4,6,8,9,10}, {0,2,3,7,8,9,10}, {0,1,4,5,11}, {1,3,5,6,11}, {0,1,3,4,7,11}, {6,7,8,11}, {3,5,9,11}, {0,1,4,5,6,9,11}, {0,3,4,7,9,11}, {3,4,5,8,9,11}, {3,4,5,6,8,9,11}, {7,8,9,11}, {1,4,10,11}, {1,4,6,10,11}, {1,7,10,11}, {6,7,8,10,11}, {0,4,5,9,10,11}, {0,1,4,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 201. `[[39,6,3]]` — T0·T1·T2·T3·T4·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ045·CCZ123·CCZ145

- gate `0+1+2+3+4+01+02+03+04+12+13+14+23+45+012+013+014+023+045+123+145`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,4,5,6}, {1,4,5,7}, {0,3,4,6,7,8}, {3,9}, {0,1,5,6,9}, {0,2,4,5,7,9}, {0,2,4,5,8,9}, {0,2,4,5,6,8,9}, {0,3,4,7,8,9}, {0,1,5,10}, {0,3,4,5,6,10}, {2,7,10}, {0,3,4,6,7,8,10}, {1,2,3,4,5,9,10}, {0,1,5,6,9,10}, {0,1,7,9,10}, {0,1,2,3,4,5,8,9,10}, {0,1,2,3,4,5,6,8,9,10}, {0,3,4,7,8,9,10}, {1,3,4,5,11}, {2,3,6,11}, {0,4,5,7,11}, {6,7,8,11}, {0,1,3,9,11}, {1,3,4,5,6,9,11}, {1,2,4,5,7,9,11}, {1,3,8,9,11}, {1,3,6,8,9,11}, {7,8,9,11}, {1,2,10,11}, {1,2,6,10,11}, {0,1,2,7,10,11}, {6,7,8,10,11}, {0,2,3,4,5,9,10,11}, {1,3,4,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 202. `[[39,6,3]]` — T0·T1·T2·T3·T4·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS25·CS35·CCZ012·CCZ013·CCZ014·CCZ025·CCZ035·CCZ125·CCZ135

- gate `0+1+2+3+4+01+02+03+04+12+13+14+25+35+012+013+014+025+035+125+135`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,3,5,6}, {0,1,2,4,7}, {0,1,4,5,6,7,8}, {0,1,2,4,5,9}, {0,1,4,6,9}, {0,1,2,7,9}, {0,1,2,8,9}, {0,1,2,6,8,9}, {0,1,4,5,7,8,9}, {0,1,4,10}, {1,2,4,6,10}, {1,2,5,7,10}, {0,1,4,5,6,7,8,10}, {1,2,9,10}, {0,1,4,6,9,10}, {1,2,4,5,7,9,10}, {1,3,4,5,8,9,10}, {1,3,4,5,6,8,9,10}, {0,1,4,5,7,8,9,10}, {5,11}, {0,4,6,11}, {0,5,7,11}, {6,7,8,11}, {0,9,11}, {5,6,9,11}, {0,4,5,7,9,11}, {0,2,3,4,5,8,9,11}, {0,2,3,4,5,6,8,9,11}, {7,8,9,11}, {2,3,5,10,11}, {2,3,5,6,10,11}, {4,7,10,11}, {6,7,8,10,11}, {4,5,9,10,11}, {5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 203. `[[39,6,3]]` — T0·T1·T2·T3·T4·CS01·CS02·CS03·CS04·CS12·CS13·CS23·CS45·CCZ012·CCZ013·CCZ023·CCZ045·CCZ123

- gate `0+1+2+3+4+01+02+03+04+12+13+23+45+012+013+023+045+123`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,6}, {1,2,4,7}, {0,1,4,5,6,7,8}, {2,9}, {0,5,6,9}, {0,1,5,7,9}, {0,1,5,8,9}, {0,1,5,6,8,9}, {0,1,4,5,7,8,9}, {0,5,10}, {0,1,6,10}, {2,5,7,10}, {0,1,4,5,6,7,8,10}, {1,2,4,5,9,10}, {0,5,6,9,10}, {0,4,7,9,10}, {0,1,2,3,5,8,9,10}, {0,1,2,3,5,6,8,9,10}, {0,1,4,5,7,8,9,10}, {1,4,11}, {5,6,11}, {0,1,2,7,11}, {6,7,8,11}, {0,2,4,9,11}, {1,4,6,9,11}, {1,4,5,7,9,11}, {2,3,8,9,11}, {2,3,6,8,9,11}, {7,8,9,11}, {2,3,5,10,11}, {2,3,5,6,10,11}, {0,2,4,5,7,10,11}, {6,7,8,10,11}, {0,1,2,5,9,10,11}, {1,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 204. `[[39,6,3]]` — T0·T1·T2·T3·T4·CS01·CS02·CS03·CS12·CS13·CS23·CS45·CCZ012·CCZ013·CCZ023·CCZ123

- gate `0+1+2+3+4+01+02+03+12+13+23+45+012+013+023+123`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,6}, {0,1,4,5,7}, {1,4,5,6,7,8}, {0,5,9}, {5,6,9}, {1,5,7,9}, {1,5,8,9}, {1,5,6,8,9}, {1,4,5,7,8,9}, {5,10}, {1,2,5,6,10}, {0,2,5,7,10}, {1,4,5,6,7,8,10}, {0,1,2,4,5,9,10}, {5,6,9,10}, {2,4,5,7,9,10}, {0,1,3,8,9,10}, {0,1,3,6,8,9,10}, {1,4,5,7,8,9,10}, {1,4,11}, {2,6,11}, {0,1,2,7,11}, {6,7,8,11}, {0,2,4,9,11}, {1,4,6,9,11}, {1,2,4,7,9,11}, {0,3,5,8,9,11}, {0,3,5,6,8,9,11}, {7,8,9,11}, {0,2,3,5,10,11}, {0,2,3,5,6,10,11}, {0,4,7,10,11}, {6,7,8,10,11}, {0,1,9,10,11}, {1,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 205. `[[39,6,3]]` — T0·T1·T2·T3·T4·CS01·CS02·CS12·CS34·CS35·CS45·CCZ012·CCZ345

- gate `0+1+2+3+4+01+02+12+34+35+45+012+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{3,4,5,6}, {0,1,2,3,7}, {0,2,3,6,7,8}, {0,2,9}, {0,1,2,6,9}, {1,3,5,7,9}, {1,3,5,8,9}, {1,3,5,6,8,9}, {0,2,3,7,8,9}, {0,1,2,10}, {0,3,4,5,6,10}, {1,2,4,7,10}, {0,2,3,6,7,8,10}, {2,3,4,9,10}, {0,1,2,6,9,10}, {0,1,4,5,7,9,10}, {0,1,3,5,8,9,10}, {0,1,3,5,6,8,9,10}, {0,2,3,7,8,9,10}, {1,3,11}, {0,1,4,6,11}, {2,3,4,5,7,11}, {6,7,8,11}, {1,2,4,5,9,11}, {1,3,6,9,11}, {0,3,4,7,9,11}, {0,8,9,11}, {0,6,8,9,11}, {7,8,9,11}, {1,4,10,11}, {1,4,6,10,11}, {0,2,5,7,10,11}, {6,7,8,10,11}, {0,1,2,3,5,9,10,11}, {1,3,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 206. `[[39,6,3]]` — T0·T1·T2·T3·T4·T5·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ123

- gate `0+1+2+3+4+5+01+02+03+04+05+12+13+14+15+23+012+013+014+015+023+123`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,6}, {1,5,7}, {1,6,7,8}, {0,1,9}, {0,1,5,6,9}, {1,4,5,7,9}, {1,4,5,8,9}, {1,4,5,6,8,9}, {1,7,8,9}, {0,1,5,10}, {2,6,10}, {0,2,4,5,7,10}, {1,6,7,8,10}, {2,4,9,10}, {0,1,5,6,9,10}, {0,2,5,7,9,10}, {0,3,4,5,8,9,10}, {0,3,4,5,6,8,9,10}, {1,7,8,9,10}, {0,5,11}, {1,2,4,5,6,11}, {0,1,2,7,11}, {6,7,8,11}, {1,2,5,9,11}, {0,5,6,9,11}, {0,1,2,4,7,9,11}, {0,1,3,8,9,11}, {0,1,3,6,8,9,11}, {7,8,9,11}, {0,2,3,4,5,10,11}, {0,2,3,4,5,6,10,11}, {4,7,10,11}, {6,7,8,10,11}, {0,4,5,9,10,11}, {0,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 207. `[[39,6,3]]` — T0·T1·T2·T3·T4·T5·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS24·CS25·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ123·CCZ124·CCZ125

- gate `0+1+2+3+4+5+01+02+03+04+05+12+13+14+15+23+24+25+012+013+014+015+023+024+025+123+124+125`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,5,6}, {0,1,2,3,4,7}, {1,2,4,6,7,8}, {1,2,9}, {0,1,2,3,6,9}, {1,2,3,7,9}, {1,2,3,8,9}, {1,2,3,6,8,9}, {1,2,4,7,8,9}, {0,1,2,3,10}, {2,4,5,6,10}, {2,3,4,5,7,10}, {1,2,4,6,7,8,10}, {0,2,5,9,10}, {0,1,2,3,6,9,10}, {0,2,3,5,7,9,10}, {0,2,3,4,8,9,10}, {0,2,3,4,6,8,9,10}, {1,2,4,7,8,9,10}, {0,3,4,11}, {1,3,4,5,6,11}, {1,4,5,7,11}, {6,7,8,11}, {0,1,3,5,9,11}, {0,3,4,6,9,11}, {0,1,5,7,9,11}, {0,1,4,8,9,11}, {0,1,4,6,8,9,11}, {7,8,9,11}, {0,3,5,10,11}, {0,3,5,6,10,11}, {0,4,7,10,11}, {6,7,8,10,11}, {3,9,10,11}, {0,3,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 208. `[[39,6,3]]` — T0·T1·T2·T3·T4·T5·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS24·CS25·CS34·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ123·CCZ124·CCZ125·CCZ134·CCZ234

- gate `0+1+2+3+4+5+01+02+03+04+05+12+13+14+15+23+24+25+34+012+013+014+015+023+024+025+034+123+124+125+134+234`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,6}, {1,2,3,4,7}, {1,2,3,6,7,8}, {0,1,2,3,9}, {0,1,2,3,4,6,9}, {1,2,4,5,7,9}, {1,2,4,5,8,9}, {1,2,4,5,6,8,9}, {1,2,3,7,8,9}, {0,1,2,3,4,10}, {2,3,6,10}, {0,2,4,5,7,10}, {1,2,3,6,7,8,10}, {2,5,9,10}, {0,1,2,3,4,6,9,10}, {0,2,3,4,7,9,10}, {0,2,3,4,5,8,9,10}, {0,2,3,4,5,6,8,9,10}, {1,2,3,7,8,9,10}, {0,4,11}, {1,3,4,5,6,11}, {0,1,7,11}, {6,7,8,11}, {1,4,9,11}, {0,4,6,9,11}, {0,1,3,5,7,9,11}, {0,1,3,8,9,11}, {0,1,3,6,8,9,11}, {7,8,9,11}, {0,4,5,10,11}, {0,4,5,6,10,11}, {3,5,7,10,11}, {6,7,8,10,11}, {0,3,4,5,9,10,11}, {0,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 209. `[[39,6,3]]` — T0·T1·T2·T3·T4·T5·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS24·CS25·CS34·CS35·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ234·CCZ235

- gate `0+1+2+3+4+5+01+02+03+04+05+12+13+14+15+23+24+25+34+35+012+013+014+015+023+024+025+034+035+123+124+125+134+135+234+235`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {1,3,4,5,7}, {1,2,3,6,7,8}, {0,1,3,4,9}, {0,1,2,3,5,6,9}, {1,2,3,5,7,9}, {1,2,3,5,8,9}, {1,2,3,5,6,8,9}, {1,2,3,7,8,9}, {0,1,2,3,5,10}, {2,3,6,10}, {0,3,4,5,7,10}, {1,2,3,6,7,8,10}, {3,4,9,10}, {0,1,2,3,5,6,9,10}, {0,2,3,5,7,9,10}, {0,2,3,4,5,8,9,10}, {0,2,3,4,5,6,8,9,10}, {1,2,3,7,8,9,10}, {0,5,11}, {1,5,6,11}, {0,1,2,4,7,11}, {6,7,8,11}, {1,2,4,5,9,11}, {0,5,6,9,11}, {0,1,7,9,11}, {0,1,4,8,9,11}, {0,1,4,6,8,9,11}, {7,8,9,11}, {0,4,5,10,11}, {0,4,5,6,10,11}, {2,4,7,10,11}, {6,7,8,10,11}, {0,2,4,5,9,10,11}, {0,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 210. `[[39,6,3]]` — T0·T1·T2·T3·T4·T5·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS24·CS25·CS34·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ034·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245·CCZ345

- gate `0+1+2+3+4+5+01+02+03+04+05+12+13+14+15+23+24+25+34+35+45+012+013+014+015+023+024+025+034+035+045+123+124+125+134+135+145+234+235+245+345`, `N = 12` (6 outputs + 6 checks), T-count 1, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,5,6}, {0,3,7}, {1,2,4,6,7,8}, {0,1,2,4,9}, {3,6,9}, {1,2,4,7,9}, {2,4,8,9}, {2,4,6,8,9}, {1,2,4,7,8,9}, {0,2,3,10}, {0,2,3,6,10}, {0,3,7,10}, {1,2,4,6,7,8,10}, {0,1,2,4,9,10}, {3,6,9,10}, {1,2,4,7,9,10}, {1,2,5,8,9,10}, {1,2,5,6,8,9,10}, {1,2,4,7,8,9,10}, {0,3,4,11}, {0,3,4,6,11}, {0,1,2,3,4,7,11}, {6,7,8,11}, {0,9,11}, {1,2,3,4,6,9,11}, {7,9,11}, {1,4,5,8,9,11}, {1,4,5,6,8,9,11}, {7,8,9,11}, {0,1,3,5,10,11}, {0,1,3,5,6,10,11}, {0,1,2,3,4,7,10,11}, {6,7,8,10,11}, {0,9,10,11}, {1,2,3,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 211. `[[39,6,3]]` — T0·T1·T2·T3·T4·T5·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS24·CS34·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234

- gate `0+1+2+3+4+5+01+02+03+04+05+12+13+14+15+23+24+34+012+013+014+015+023+024+034+123+124+134+234`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {2,5,7}, {0,2,6,7,8}, {1,9}, {0,1,5,6,9}, {0,2,5,7,9}, {0,2,5,8,9}, {0,2,5,6,8,9}, {0,2,7,8,9}, {0,1,5,10}, {0,2,3,6,10}, {1,3,5,7,10}, {0,2,6,7,8,10}, {2,3,9,10}, {0,1,5,6,9,10}, {0,1,3,5,7,9,10}, {0,1,2,4,5,8,9,10}, {0,1,2,4,5,6,8,9,10}, {0,2,7,8,9,10}, {1,2,5,11}, {3,5,6,11}, {0,1,2,3,7,11}, {6,7,8,11}, {0,3,5,9,11}, {1,2,5,6,9,11}, {1,2,3,7,9,11}, {1,4,8,9,11}, {1,4,6,8,9,11}, {7,8,9,11}, {1,3,4,5,10,11}, {1,3,4,5,6,10,11}, {0,7,10,11}, {6,7,8,10,11}, {0,1,2,5,9,10,11}, {1,2,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 212. `[[39,6,3]]` — T0·T1·T2·T3·T4·T5·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS15·CS23·CS45·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ045·CCZ123·CCZ145

- gate `0+1+2+3+4+5+01+02+03+04+05+12+13+14+15+23+45+012+013+014+015+023+045+123+145`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,4,5,6}, {1,4,7}, {0,1,3,4,6,7,8}, {1,3,9}, {0,1,6,9}, {0,1,2,4,7,9}, {0,1,2,4,8,9}, {0,1,2,4,6,8,9}, {0,1,3,4,7,8,9}, {0,1,10}, {0,3,4,6,10}, {2,7,10}, {0,1,3,4,6,7,8,10}, {2,3,4,9,10}, {0,1,6,9,10}, {0,7,9,10}, {0,2,3,4,5,8,9,10}, {0,2,3,4,5,6,8,9,10}, {0,1,3,4,7,8,9,10}, {3,4,11}, {1,2,3,6,11}, {0,1,4,7,11}, {6,7,8,11}, {0,1,3,9,11}, {3,4,6,9,11}, {1,2,4,7,9,11}, {1,3,5,8,9,11}, {1,3,5,6,8,9,11}, {7,8,9,11}, {2,5,10,11}, {2,5,6,10,11}, {0,2,7,10,11}, {6,7,8,10,11}, {0,2,3,4,9,10,11}, {3,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 213. `[[39,6,3]]` — T0·T1·T2·T3·T4·T5·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS14·CS23·CS24·CS34·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234

- gate `0+1+2+3+4+5+01+02+03+04+05+12+13+14+23+24+34+012+013+014+023+024+034+123+124+134+234`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,6}, {0,1,2,5,7}, {0,1,5,6,7,8}, {0,1,3,4,9}, {0,1,2,3,4,6,9}, {0,2,3,4,7,9}, {0,2,3,4,8,9}, {0,2,3,4,6,8,9}, {0,1,5,7,8,9}, {0,1,2,3,4,10}, {1,3,6,10}, {2,3,7,10}, {0,1,5,6,7,8,10}, {4,5,9,10}, {0,1,2,3,4,6,9,10}, {1,2,4,5,7,9,10}, {1,2,4,8,9,10}, {1,2,4,6,8,9,10}, {0,1,5,7,8,9,10}, {2,3,4,5,11}, {0,1,2,4,6,11}, {0,4,7,11}, {6,7,8,11}, {0,2,3,5,9,11}, {2,3,4,5,6,9,11}, {0,1,3,5,7,9,11}, {0,1,3,8,9,11}, {0,1,3,6,8,9,11}, {7,8,9,11}, {2,3,4,10,11}, {2,3,4,6,10,11}, {1,3,4,5,7,10,11}, {6,7,8,10,11}, {1,2,9,10,11}, {2,3,4,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 214. `[[39,6,3]]` — T0·T1·T2·T3·T4·T5·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS23·CCZ012·CCZ013·CCZ023·CCZ123

- gate `0+1+2+3+4+5+01+02+03+04+05+12+13+23+012+013+023+123`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,6}, {0,1,2,4,7}, {0,2,4,6,7,8}, {0,1,4,9}, {0,4,6,9}, {0,2,5,7,9}, {0,2,5,8,9}, {0,2,5,6,8,9}, {0,2,4,7,8,9}, {0,4,10}, {2,4,6,10}, {1,5,7,10}, {0,2,4,6,7,8,10}, {1,2,5,9,10}, {0,4,6,9,10}, {4,7,9,10}, {1,2,3,4,5,8,9,10}, {1,2,3,4,5,6,8,9,10}, {0,2,4,7,8,9,10}, {2,11}, {0,4,5,6,11}, {0,1,2,7,11}, {6,7,8,11}, {0,1,9,11}, {2,6,9,11}, {0,2,4,5,7,9,11}, {0,1,3,4,8,9,11}, {0,1,3,4,6,8,9,11}, {7,8,9,11}, {1,3,5,10,11}, {1,3,5,6,10,11}, {1,4,5,7,10,11}, {6,7,8,10,11}, {1,2,4,5,9,10,11}, {2,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 215. `[[39,6,3]]` — T0·T1·T2·T3·T4·T5·CS01·CS02·CS03·CS04·CS05·CS12·CS13·CS23·CS45·CCZ012·CCZ013·CCZ023·CCZ045·CCZ123

- gate `0+1+2+3+4+5+01+02+03+04+05+12+13+23+45+012+013+023+045+123`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,4,5,6}, {0,1,2,4,7}, {0,1,4,6,7,8}, {0,1,3,9}, {0,1,2,3,6,9}, {0,2,3,4,7,9}, {0,2,3,4,8,9}, {0,2,3,4,6,8,9}, {0,1,4,7,8,9}, {0,1,2,3,10}, {0,1,3,4,6,10}, {0,2,3,7,10}, {0,1,4,6,7,8,10}, {0,4,9,10}, {0,1,2,3,6,9,10}, {0,1,2,7,9,10}, {0,1,2,4,5,8,9,10}, {0,1,2,4,5,6,8,9,10}, {0,1,4,7,8,9,10}, {2,3,4,11}, {1,2,6,11}, {4,7,11}, {6,7,8,11}, {2,3,9,11}, {2,3,4,6,9,11}, {1,3,4,7,9,11}, {1,3,5,8,9,11}, {1,3,5,6,8,9,11}, {7,8,9,11}, {2,3,5,10,11}, {2,3,5,6,10,11}, {1,3,7,10,11}, {6,7,8,10,11}, {1,2,4,9,10,11}, {2,3,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 216. `[[39,6,3]]` — T0·T1·T2·T3·T4·T5·CS01·CS02·CS03·CS04·CS05·CS12·CS34·CCZ012·CCZ034

- gate `0+1+2+3+4+5+01+02+03+04+05+12+34+012+034`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,3,4,6}, {5,7}, {0,2,6,7,8}, {2,9}, {0,5,6,9}, {0,1,5,7,9}, {0,1,5,8,9}, {0,1,5,6,8,9}, {0,2,7,8,9}, {0,5,10}, {0,2,3,6,10}, {1,3,5,7,10}, {0,2,6,7,8,10}, {1,2,3,9,10}, {0,5,6,9,10}, {0,3,5,7,9,10}, {0,1,2,4,5,8,9,10}, {0,1,2,4,5,6,8,9,10}, {0,2,7,8,9,10}, {2,5,11}, {1,2,3,5,6,11}, {0,3,7,11}, {6,7,8,11}, {0,2,3,5,9,11}, {2,5,6,9,11}, {1,3,7,9,11}, {2,4,8,9,11}, {2,4,6,8,9,11}, {7,8,9,11}, {1,3,4,5,10,11}, {1,3,4,5,6,10,11}, {0,1,7,10,11}, {6,7,8,10,11}, {0,1,2,5,9,10,11}, {2,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 217. `[[39,6,3]]` — T0·T1·T2·T3·T4·T5·CS01·CS02·CS03·CS12·CS13·CS23·CCZ012·CCZ013·CCZ023·CCZ123

- gate `0+1+2+3+4+5+01+02+03+12+13+23+012+013+023+123`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{4,6}, {0,1,3,4,7}, {0,3,4,6,7,8}, {0,2,3,9}, {0,1,2,3,6,9}, {1,2,4,5,7,9}, {1,2,4,5,8,9}, {1,2,4,5,6,8,9}, {0,3,4,7,8,9}, {0,1,2,3,10}, {0,2,4,6,10}, {1,2,3,5,7,10}, {0,3,4,6,7,8,10}, {3,4,5,9,10}, {0,1,2,3,6,9,10}, {0,1,7,9,10}, {0,1,4,5,8,9,10}, {0,1,4,5,6,8,9,10}, {0,3,4,7,8,9,10}, {1,2,4,11}, {0,1,5,6,11}, {3,4,7,11}, {6,7,8,11}, {1,2,3,9,11}, {1,2,4,6,9,11}, {0,2,4,5,7,9,11}, {0,2,8,9,11}, {0,2,6,8,9,11}, {7,8,9,11}, {1,2,5,10,11}, {1,2,5,6,10,11}, {0,2,3,5,7,10,11}, {6,7,8,10,11}, {0,1,3,4,5,9,10,11}, {1,2,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 218. `[[39,6,3]]` — T0·T1·T2·T3·T4·T5·CS01·CS02·CS12·CS34·CCZ012

- gate `0+1+2+3+4+5+01+02+12+34+012`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,6}, {1,3,7}, {4,6,7,8}, {1,9}, {3,4,6,9}, {3,5,7,9}, {3,5,8,9}, {3,5,6,8,9}, {4,7,8,9}, {3,4,10}, {0,6,10}, {0,1,3,5,7,10}, {4,6,7,8,10}, {0,1,5,9,10}, {3,4,6,9,10}, {0,3,7,9,10}, {1,2,3,5,8,9,10}, {1,2,3,5,6,8,9,10}, {4,7,8,9,10}, {3,11}, {0,3,5,6,11}, {0,1,7,11}, {6,7,8,11}, {0,1,3,9,11}, {3,6,9,11}, {0,5,7,9,11}, {1,2,8,9,11}, {1,2,6,8,9,11}, {7,8,9,11}, {0,1,2,3,5,10,11}, {0,1,2,3,5,6,10,11}, {1,5,7,10,11}, {6,7,8,10,11}, {1,3,5,9,10,11}, {3,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 219. `[[39,6,3]]` — T0·T1·T2·T3·T4·T5·CS01·CS23·CS45

- gate `0+1+2+3+4+5+01+23+45`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{4,5,6}, {2,4,7}, {1,3,4,6,7,8}, {1,9}, {2,3,6,9}, {0,2,4,7,9}, {0,2,4,8,9}, {0,2,4,6,8,9}, {1,3,4,7,8,9}, {2,3,10}, {1,3,4,5,6,10}, {0,2,3,5,7,10}, {1,3,4,6,7,8,10}, {0,1,3,4,5,9,10}, {2,3,6,9,10}, {2,3,5,7,9,10}, {0,1,2,3,4,8,9,10}, {0,1,2,3,4,6,8,9,10}, {1,3,4,7,8,9,10}, {1,2,4,11}, {0,1,2,3,5,6,11}, {3,4,5,7,11}, {6,7,8,11}, {1,2,3,5,9,11}, {1,2,4,6,9,11}, {0,3,4,5,7,9,11}, {1,3,8,9,11}, {1,3,6,8,9,11}, {7,8,9,11}, {0,2,5,10,11}, {0,2,5,6,10,11}, {0,7,10,11}, {6,7,8,10,11}, {0,1,2,4,9,10,11}, {1,2,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 220. `[[39,6,3]]` — T0·T1·T2·T3·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CS34·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234

- gate `0+1+2+3+5+01+02+03+04+12+13+14+23+24+34+012+013+014+023+024+034+123+124+134+234`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{4,6}, {0,1,5,7}, {0,5,6,7,8}, {0,2,3,4,9}, {0,1,2,3,4,6,9}, {1,2,3,4,7,9}, {1,2,3,4,8,9}, {1,2,3,4,6,8,9}, {0,5,7,8,9}, {0,1,2,3,4,10}, {0,2,5,6,10}, {1,2,5,7,10}, {0,5,6,7,8,10}, {3,4,9,10}, {0,1,2,3,4,6,9,10}, {0,1,3,4,7,9,10}, {0,1,3,5,8,9,10}, {0,1,3,5,6,8,9,10}, {0,5,7,8,9,10}, {1,2,3,4,5,11}, {0,1,3,4,5,6,11}, {3,4,5,7,11}, {6,7,8,11}, {1,2,9,11}, {1,2,3,4,5,6,9,11}, {0,2,7,9,11}, {0,2,4,5,8,9,11}, {0,2,4,5,6,8,9,11}, {7,8,9,11}, {1,2,3,10,11}, {1,2,3,6,10,11}, {0,2,3,4,5,7,10,11}, {6,7,8,10,11}, {0,1,9,10,11}, {1,2,3,4,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 221. `[[39,6,3]]` — T0·T1·T2·T3·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CS35·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234

- gate `0+1+2+3+5+01+02+03+04+12+13+14+23+24+35+012+013+014+023+024+034+123+124+134+234`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {0,1,4,7}, {1,3,4,6,7,8}, {0,5,9}, {3,5,6,9}, {1,3,5,7,9}, {1,3,5,8,9}, {1,3,5,6,8,9}, {1,3,4,7,8,9}, {3,5,10}, {1,3,4,5,6,10}, {0,4,5,7,10}, {1,3,4,6,7,8,10}, {0,1,9,10}, {3,5,6,9,10}, {3,7,9,10}, {0,1,2,3,8,9,10}, {0,1,2,3,6,8,9,10}, {1,3,4,7,8,9,10}, {1,4,5,11}, {4,6,11}, {0,1,3,4,7,11}, {6,7,8,11}, {0,3,5,9,11}, {1,4,5,6,9,11}, {1,5,7,9,11}, {0,2,5,8,9,11}, {0,2,5,6,8,9,11}, {7,8,9,11}, {0,2,4,5,10,11}, {0,2,4,5,6,10,11}, {0,3,4,5,7,10,11}, {6,7,8,10,11}, {0,1,3,9,10,11}, {1,4,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 222. `[[39,6,3]]` — T0·T1·T2·T3·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234·CCZ345

- gate `0+1+2+3+5+01+02+03+04+12+13+14+23+24+35+45+012+013+014+023+024+034+123+124+134+234+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {0,1,7}, {1,3,6,7,8}, {0,4,5,9}, {3,4,5,6,9}, {1,3,4,5,7,9}, {1,3,4,5,8,9}, {1,3,4,5,6,8,9}, {1,3,7,8,9}, {3,4,5,10}, {1,3,5,6,10}, {0,5,7,10}, {1,3,6,7,8,10}, {0,1,4,9,10}, {3,4,5,6,9,10}, {3,4,7,9,10}, {0,1,2,3,8,9,10}, {0,1,2,3,6,8,9,10}, {1,3,7,8,9,10}, {1,4,5,11}, {4,6,11}, {0,1,3,4,7,11}, {6,7,8,11}, {0,3,5,9,11}, {1,4,5,6,9,11}, {1,5,7,9,11}, {0,2,4,5,8,9,11}, {0,2,4,5,6,8,9,11}, {7,8,9,11}, {0,2,5,10,11}, {0,2,5,6,10,11}, {0,3,4,5,7,10,11}, {6,7,8,10,11}, {0,1,3,9,10,11}, {1,4,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 223. `[[39,6,3]]` — T0·T1·T2·T3·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS25·CS35·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ235

- gate `0+1+2+3+5+01+02+03+04+12+13+14+23+25+35+012+013+014+023+024+034+123+124+134+235`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {0,3,7}, {2,3,4,5,6,7,8}, {0,3,5,9}, {2,3,4,6,9}, {2,3,7,9}, {2,3,8,9}, {2,3,6,8,9}, {2,3,4,5,7,8,9}, {2,3,4,10}, {1,2,3,4,5,6,10}, {0,1,3,4,7,10}, {2,3,4,5,6,7,8,10}, {0,1,3,4,5,9,10}, {2,3,4,6,9,10}, {1,2,3,4,7,9,10}, {0,2,3,5,8,9,10}, {0,2,3,5,6,8,9,10}, {2,3,4,5,7,8,9,10}, {5,11}, {1,4,5,6,11}, {0,1,2,4,7,11}, {6,7,8,11}, {0,1,2,4,5,9,11}, {5,6,9,11}, {1,4,7,9,11}, {0,5,8,9,11}, {0,5,6,8,9,11}, {7,8,9,11}, {0,1,4,10,11}, {0,1,4,6,10,11}, {0,2,7,10,11}, {6,7,8,10,11}, {0,2,5,9,10,11}, {5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 224. `[[39,6,3]]` — T0·T1·T2·T3·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS25·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ235·CCZ245·CCZ345

- gate `0+1+2+3+5+01+02+03+04+12+13+14+23+25+35+45+012+013+014+023+024+034+123+124+134+235+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {0,7}, {0,2,4,5,6,7,8}, {3,9}, {2,3,4,5,6,9}, {0,2,7,9}, {0,2,8,9}, {0,2,6,8,9}, {0,2,4,5,7,8,9}, {2,3,4,5,10}, {0,2,4,6,10}, {3,4,7,10}, {0,2,4,5,6,7,8,10}, {0,4,9,10}, {2,3,4,5,6,9,10}, {2,3,4,7,9,10}, {0,1,2,3,8,9,10}, {0,1,2,3,6,8,9,10}, {0,2,4,5,7,8,9,10}, {0,3,11}, {4,6,11}, {0,2,3,4,7,11}, {6,7,8,11}, {2,4,9,11}, {0,3,6,9,11}, {0,3,4,7,9,11}, {1,3,8,9,11}, {1,3,6,8,9,11}, {7,8,9,11}, {1,3,4,10,11}, {1,3,4,6,10,11}, {2,7,10,11}, {6,7,8,10,11}, {0,2,3,9,10,11}, {0,3,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 225. `[[39,6,3]]` — T0·T1·T2·T3·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS15·CS23·CS25·CS35·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ125·CCZ135·CCZ235

- gate `0+1+2+3+5+01+02+03+04+12+13+15+23+25+35+012+013+014+023+024+034+123+125+135+235`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {3,4,7}, {1,3,5,6,7,8}, {2,3,4,9}, {1,2,3,5,6,9}, {1,3,4,7,9}, {1,3,4,8,9}, {1,3,4,6,8,9}, {1,3,5,7,8,9}, {1,2,3,5,10}, {0,1,5,6,10}, {0,2,5,7,10}, {1,3,5,6,7,8,10}, {0,5,9,10}, {1,2,3,5,6,9,10}, {0,1,2,5,7,9,10}, {1,2,5,8,9,10}, {1,2,5,6,8,9,10}, {1,3,5,7,8,9,10}, {2,11}, {0,3,4,5,6,11}, {0,1,2,3,4,5,7,11}, {6,7,8,11}, {0,1,3,4,5,9,11}, {2,6,9,11}, {0,2,3,4,5,7,9,11}, {2,3,4,5,8,9,11}, {2,3,4,5,6,8,9,11}, {7,8,9,11}, {0,2,10,11}, {0,2,6,10,11}, {1,7,10,11}, {6,7,8,10,11}, {1,2,9,10,11}, {2,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 226. `[[39,6,3]]` — T0·T1·T2·T3·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS15·CS23·CS25·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ125·CCZ135·CCZ145·CCZ235·CCZ245·CCZ345

- gate `0+1+2+3+5+01+02+03+04+12+13+15+23+25+35+45+012+013+014+023+024+034+123+125+135+145+235+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{1,2,3,4,5,6}, {0,3,7}, {0,1,3,4,6,7,8}, {0,2,3,9}, {0,1,2,3,4,6,9}, {1,3,7,9}, {1,3,8,9}, {1,3,6,8,9}, {0,1,3,4,7,8,9}, {0,1,2,3,4,10}, {0,1,4,6,10}, {2,4,7,10}, {0,1,3,4,6,7,8,10}, {4,9,10}, {0,1,2,3,4,6,9,10}, {0,1,2,4,7,9,10}, {0,1,2,5,8,9,10}, {0,1,2,5,6,8,9,10}, {0,1,3,4,7,8,9,10}, {2,11}, {0,3,4,6,11}, {1,2,3,4,7,11}, {6,7,8,11}, {1,3,4,9,11}, {2,6,9,11}, {0,2,3,4,7,9,11}, {0,2,3,5,8,9,11}, {0,2,3,5,6,8,9,11}, {7,8,9,11}, {2,4,5,10,11}, {2,4,5,6,10,11}, {0,1,7,10,11}, {6,7,8,10,11}, {0,1,2,9,10,11}, {2,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 227. `[[39,6,3]]` — T0·T1·T2·T3·T5·CS01·CS02·CS03·CS05·CS12·CS34·CS45·CCZ012·CCZ034·CCZ045

- gate `0+1+2+3+5+01+02+03+05+12+34+45+012+034+045`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,4,5,6}, {0,1,3,7}, {0,1,2,4,6,7,8}, {0,1,3,4,9}, {0,1,2,6,9}, {0,3,7,9}, {0,3,8,9}, {0,3,6,8,9}, {0,1,2,4,7,8,9}, {0,1,2,10}, {0,1,2,4,5,6,10}, {0,2,5,7,10}, {0,1,2,4,6,7,8,10}, {0,2,4,5,9,10}, {0,1,2,6,9,10}, {0,1,2,5,7,9,10}, {0,1,2,3,8,9,10}, {0,1,2,3,6,8,9,10}, {0,1,2,4,7,8,9,10}, {4,11}, {1,2,3,4,5,6,11}, {2,3,5,7,11}, {6,7,8,11}, {2,3,4,5,9,11}, {4,6,9,11}, {1,2,3,5,7,9,11}, {1,2,8,9,11}, {1,2,6,8,9,11}, {7,8,9,11}, {3,4,5,10,11}, {3,4,5,6,10,11}, {1,7,10,11}, {6,7,8,10,11}, {1,4,9,10,11}, {4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 228. `[[39,6,3]]` — T0·T1·T2·T3·T5·CS01·CS02·CS12·CS34·CS45·CCZ012

- gate `0+1+2+3+5+01+02+12+34+45+012`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{4,5,6}, {0,1,3,4,7}, {0,3,4,6,7,8}, {0,2,9}, {0,1,2,6,9}, {1,2,7,9}, {1,2,8,9}, {1,2,6,8,9}, {0,3,4,7,8,9}, {0,1,2,10}, {0,2,4,6,10}, {1,2,4,7,10}, {0,3,4,6,7,8,10}, {3,9,10}, {0,1,2,6,9,10}, {0,1,3,7,9,10}, {0,1,5,8,9,10}, {0,1,5,6,8,9,10}, {0,3,4,7,8,9,10}, {1,2,3,4,11}, {0,1,4,6,11}, {4,7,11}, {6,7,8,11}, {1,2,3,9,11}, {1,2,3,4,6,9,11}, {0,2,3,7,9,11}, {0,2,5,8,9,11}, {0,2,5,6,8,9,11}, {7,8,9,11}, {1,2,4,5,10,11}, {1,2,4,5,6,10,11}, {0,2,3,4,7,10,11}, {6,7,8,10,11}, {0,1,9,10,11}, {1,2,3,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 229. `[[39,6,3]]` — T0·T1·T2·T4·CS01·CS02·CS03·CS12·CS13·CS23·CS34·CS35·CS45·CCZ012·CCZ013·CCZ023·CCZ123·CCZ345

- gate `0+1+2+4+01+02+03+12+13+23+34+35+45+012+013+023+123+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{3,4,5,6}, {0,1,5,7}, {0,5,6,7,8}, {0,2,3,9}, {0,1,2,3,6,9}, {1,2,3,7,9}, {1,2,3,8,9}, {1,2,3,6,8,9}, {0,5,7,8,9}, {0,1,2,3,10}, {0,2,5,6,10}, {1,2,5,7,10}, {0,5,6,7,8,10}, {3,9,10}, {0,1,2,3,6,9,10}, {0,1,3,7,9,10}, {0,1,4,8,9,10}, {0,1,4,6,8,9,10}, {0,5,7,8,9,10}, {1,2,3,5,11}, {0,1,3,5,6,11}, {3,5,7,11}, {6,7,8,11}, {1,2,9,11}, {1,2,3,5,6,9,11}, {0,2,7,9,11}, {0,2,3,4,8,9,11}, {0,2,3,4,6,8,9,11}, {7,8,9,11}, {1,2,4,5,10,11}, {1,2,4,5,6,10,11}, {0,2,3,5,7,10,11}, {6,7,8,10,11}, {0,1,9,10,11}, {1,2,3,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 230. `[[39,6,3]]` — T0·T1·T2·T4·CS01·CS02·CS03·CS12·CS13·CS24·CS34·CS35·CS45·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234·CCZ235·CCZ245·CCZ345

- gate `0+1+2+4+01+02+03+12+13+24+34+35+45+012+013+023+123+234+235+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{2,3,4,5,6}, {0,2,3,7}, {2,3,6,7,8}, {1,2,3,9}, {0,1,2,3,6,9}, {0,1,2,5,7,9}, {0,1,2,5,8,9}, {0,1,2,5,6,8,9}, {2,3,7,8,9}, {0,1,2,3,10}, {1,2,6,10}, {0,1,2,3,5,7,10}, {2,3,6,7,8,10}, {2,3,5,9,10}, {0,1,2,3,6,9,10}, {0,2,7,9,10}, {0,2,3,4,8,9,10}, {0,2,3,4,6,8,9,10}, {2,3,7,8,9,10}, {0,1,11}, {0,5,6,11}, {3,7,11}, {6,7,8,11}, {0,1,3,9,11}, {0,1,6,9,11}, {1,5,7,9,11}, {1,3,4,5,8,9,11}, {1,3,4,5,6,8,9,11}, {7,8,9,11}, {0,1,3,4,10,11}, {0,1,3,4,6,10,11}, {1,3,5,7,10,11}, {6,7,8,10,11}, {0,3,5,9,10,11}, {0,1,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 231. `[[39,6,3]]` — T0·T1·T2·T4·CS01·CS02·CS03·CS12·CS14·CS24·CS35·CS45·CCZ012·CCZ013·CCZ023·CCZ124·CCZ135·CCZ145·CCZ235·CCZ245

- gate `0+1+2+4+01+02+03+12+14+24+35+45+012+013+023+124+135+145+235+245`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{1,2,4,5,6}, {1,2,3,4,5,7}, {0,2,3,4,6,7,8}, {0,2,3,9}, {1,2,3,5,6,9}, {2,3,4,5,7,9}, {2,3,4,5,8,9}, {2,3,4,5,6,8,9}, {0,2,3,4,7,8,9}, {1,2,3,5,10}, {0,2,3,4,5,6,10}, {2,3,7,10}, {0,2,3,4,6,7,8,10}, {0,1,2,3,4,5,9,10}, {1,2,3,5,6,9,10}, {1,2,3,7,9,10}, {0,1,2,4,5,8,9,10}, {0,1,2,4,5,6,8,9,10}, {0,2,3,4,7,8,9,10}, {0,1,4,5,11}, {0,6,11}, {4,5,7,11}, {6,7,8,11}, {0,1,9,11}, {0,1,4,5,6,9,11}, {1,4,5,7,9,11}, {0,1,3,8,9,11}, {0,1,3,6,8,9,11}, {7,8,9,11}, {1,3,10,11}, {1,3,6,10,11}, {1,7,10,11}, {6,7,8,10,11}, {0,4,5,9,10,11}, {0,1,4,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 232. `[[39,6,3]]` — T0·T1·T2·T4·T5·CS01·CS02·CS03·CS12·CS13·CS23·CS34·CCZ012·CCZ013·CCZ023·CCZ123

- gate `0+1+2+4+5+01+02+03+12+13+23+34+012+013+023+123`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{3,4,6}, {1,5,7}, {1,2,6,7,8}, {2,9}, {5,6,9}, {0,3,5,7,9}, {0,3,5,8,9}, {0,3,5,6,8,9}, {1,2,7,8,9}, {5,10}, {1,2,4,6,10}, {0,1,3,4,5,7,10}, {1,2,6,7,8,10}, {0,2,3,4,9,10}, {5,6,9,10}, {4,5,7,9,10}, {0,1,2,5,8,9,10}, {0,1,2,5,6,8,9,10}, {1,2,7,8,9,10}, {1,2,5,11}, {0,1,2,3,4,5,6,11}, {1,4,7,11}, {6,7,8,11}, {2,4,5,9,11}, {1,2,5,6,9,11}, {0,3,4,7,9,11}, {1,2,3,8,9,11}, {1,2,3,6,8,9,11}, {7,8,9,11}, {0,4,5,10,11}, {0,4,5,6,10,11}, {0,1,3,7,10,11}, {6,7,8,10,11}, {0,2,3,5,9,10,11}, {1,2,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 233. `[[39,6,3]]` — T0·T1·T2·T4·T5·CS01·CS02·CS03·CS12·CS13·CS23·CS45·CCZ012·CCZ013·CCZ023·CCZ123

- gate `0+1+2+4+5+01+02+03+12+13+23+45+012+013+023+123`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,6}, {0,7}, {0,3,5,6,7,8}, {5,9}, {3,6,9}, {0,4,7,9}, {0,4,8,9}, {0,4,6,8,9}, {0,3,5,7,8,9}, {3,10}, {0,1,3,5,6,10}, {1,3,4,7,10}, {0,3,5,6,7,8,10}, {0,1,3,4,5,9,10}, {3,6,9,10}, {1,3,7,9,10}, {0,2,4,5,8,9,10}, {0,2,4,5,6,8,9,10}, {0,3,5,7,8,9,10}, {0,5,11}, {1,3,4,5,6,11}, {0,1,3,7,11}, {6,7,8,11}, {1,3,5,9,11}, {0,5,6,9,11}, {0,1,3,4,7,9,11}, {2,5,8,9,11}, {2,5,6,8,9,11}, {7,8,9,11}, {1,2,3,4,10,11}, {1,2,3,4,6,10,11}, {4,7,10,11}, {6,7,8,10,11}, {0,4,5,9,10,11}, {0,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 234. `[[39,6,3]]` — T0·T1·T2·T4·T5·CS01·CS02·CS03·CS12·CS13·CS24·CS25·CS34·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234

- gate `0+1+2+4+5+01+02+03+12+13+24+25+34+012+013+023+123+234`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{2,3,4,6}, {0,2,5,7}, {1,3,6,7,8}, {5,9}, {0,1,2,3,6,9}, {0,5,7,9}, {0,5,8,9}, {0,5,6,8,9}, {1,3,7,8,9}, {0,1,2,3,10}, {1,3,4,6,10}, {0,1,3,4,7,10}, {1,3,6,7,8,10}, {1,2,3,4,9,10}, {0,1,2,3,6,9,10}, {0,1,2,3,4,7,9,10}, {0,1,2,5,8,9,10}, {0,1,2,5,6,8,9,10}, {1,3,7,8,9,10}, {0,2,11}, {0,1,3,4,5,6,11}, {1,3,4,5,7,11}, {6,7,8,11}, {0,1,2,3,4,5,9,11}, {0,2,6,9,11}, {1,2,3,4,5,7,9,11}, {1,2,8,9,11}, {1,2,6,8,9,11}, {7,8,9,11}, {0,2,3,4,5,10,11}, {0,2,3,4,5,6,10,11}, {2,7,10,11}, {6,7,8,10,11}, {0,9,10,11}, {0,2,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 235. `[[39,6,3]]` — T0·T1·T2·T4·T5·CS01·CS02·CS03·CS12·CS13·CS24·CS25·CS34·CS35·CS45·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234·CCZ235·CCZ245·CCZ345

- gate `0+1+2+4+5+01+02+03+12+13+24+25+34+35+45+012+013+023+123+234+235+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,6}, {0,3,4,7}, {5,6,7,8}, {0,2,3,4,5,9}, {2,6,9}, {3,4,7,9}, {3,4,8,9}, {3,4,6,8,9}, {5,7,8,9}, {2,10}, {4,5,6,10}, {0,2,4,7,10}, {5,6,7,8,10}, {0,4,5,9,10}, {2,6,9,10}, {2,4,7,9,10}, {0,1,2,5,8,9,10}, {0,1,2,5,6,8,9,10}, {5,7,8,9,10}, {2,5,11}, {3,5,6,11}, {0,2,3,7,11}, {6,7,8,11}, {0,3,5,9,11}, {2,5,6,9,11}, {2,3,7,9,11}, {0,1,2,3,4,5,8,9,11}, {0,1,2,3,4,5,6,8,9,11}, {7,8,9,11}, {0,1,2,4,10,11}, {0,1,2,4,6,10,11}, {0,7,10,11}, {6,7,8,10,11}, {0,2,5,9,10,11}, {2,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 236. `[[39,6,3]]` — T0·T1·T2·T4·T5·CS01·CS02·CS03·CS12·CS13·CS24·CS25·CS45·CCZ012·CCZ013·CCZ023·CCZ123·CCZ245

- gate `0+1+2+4+5+01+02+03+12+13+24+25+45+012+013+023+123+245`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{2,4,5,6}, {0,1,5,7}, {0,5,6,7,8}, {0,2,3,9}, {0,1,2,3,6,9}, {1,5,7,9}, {1,5,8,9}, {1,5,6,8,9}, {0,5,7,8,9}, {0,1,2,3,10}, {0,4,5,6,10}, {1,2,3,4,7,10}, {0,5,6,7,8,10}, {4,5,9,10}, {0,1,2,3,6,9,10}, {0,1,2,3,4,7,9,10}, {0,1,2,5,8,9,10}, {0,1,2,5,6,8,9,10}, {0,5,7,8,9,10}, {1,2,3,5,11}, {0,1,4,6,11}, {2,3,4,5,7,11}, {6,7,8,11}, {1,4,9,11}, {1,2,3,5,6,9,11}, {0,2,3,4,5,7,9,11}, {0,2,8,9,11}, {0,2,6,8,9,11}, {7,8,9,11}, {1,2,4,10,11}, {1,2,4,6,10,11}, {0,7,10,11}, {6,7,8,10,11}, {0,1,2,3,5,9,10,11}, {1,2,3,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 237. `[[39,6,3]]` — T0·T1·T2·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234

- gate `0+1+2+5+01+02+03+04+12+13+14+23+24+012+013+014+023+024+034+123+124+134+234`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {0,5,7}, {0,4,5,6,7,8}, {3,9}, {3,4,6,9}, {0,3,7,9}, {0,3,8,9}, {0,3,6,8,9}, {0,4,5,7,8,9}, {3,4,10}, {0,1,4,5,6,10}, {1,4,5,7,10}, {0,4,5,6,7,8,10}, {0,1,3,4,9,10}, {3,4,6,9,10}, {1,3,4,7,9,10}, {0,2,5,8,9,10}, {0,2,5,6,8,9,10}, {0,4,5,7,8,9,10}, {0,3,5,11}, {1,3,4,5,6,11}, {0,1,3,4,5,7,11}, {6,7,8,11}, {1,4,9,11}, {0,3,5,6,9,11}, {0,1,4,7,9,11}, {2,3,5,8,9,11}, {2,3,5,6,8,9,11}, {7,8,9,11}, {1,2,4,10,11}, {1,2,4,6,10,11}, {3,5,7,10,11}, {6,7,8,10,11}, {0,9,10,11}, {0,3,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 238. `[[39,6,3]]` — T0·T1·T2·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CS34·CS35·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234

- gate `0+1+2+5+01+02+03+04+12+13+14+23+24+34+35+012+013+014+023+024+034+123+124+134+234`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{3,5,6}, {0,1,4,7}, {1,4,6,7,8}, {1,2,3,4,9}, {0,1,2,3,4,6,9}, {0,2,3,4,7,9}, {0,2,3,4,8,9}, {0,2,3,4,6,8,9}, {1,4,7,8,9}, {0,1,2,3,4,10}, {1,2,4,6,10}, {0,2,4,7,10}, {1,4,6,7,8,10}, {3,4,9,10}, {0,1,2,3,4,6,9,10}, {0,1,3,4,7,9,10}, {0,1,5,8,9,10}, {0,1,5,6,8,9,10}, {1,4,7,8,9,10}, {0,2,3,11}, {0,1,3,6,11}, {3,7,11}, {6,7,8,11}, {0,2,9,11}, {0,2,3,6,9,11}, {1,2,7,9,11}, {1,2,3,4,5,8,9,11}, {1,2,3,4,5,6,8,9,11}, {7,8,9,11}, {0,2,4,5,10,11}, {0,2,4,5,6,10,11}, {1,2,3,7,10,11}, {6,7,8,10,11}, {0,1,9,10,11}, {0,2,3,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 239. `[[39,6,3]]` — T0·T1·T2·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS25·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134

- gate `0+1+2+5+01+02+03+04+12+13+14+25+012+013+014+023+024+034+123+124+134`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {3,4,7}, {0,3,5,6,7,8}, {0,2,3,5,9}, {2,3,4,6,9}, {0,4,7,9}, {0,4,8,9}, {0,4,6,8,9}, {0,3,5,7,8,9}, {2,3,4,10}, {0,1,3,5,6,10}, {0,1,2,4,7,10}, {0,3,5,6,7,8,10}, {1,5,9,10}, {2,3,4,6,9,10}, {1,2,3,4,7,9,10}, {0,2,5,8,9,10}, {0,2,5,6,8,9,10}, {0,3,5,7,8,9,10}, {0,2,4,5,11}, {1,3,4,5,6,11}, {1,2,7,11}, {6,7,8,11}, {0,1,4,5,9,11}, {0,2,4,5,6,9,11}, {0,1,2,3,7,9,11}, {2,4,5,8,9,11}, {2,4,5,6,8,9,11}, {7,8,9,11}, {1,2,3,10,11}, {1,2,3,6,10,11}, {0,3,7,10,11}, {6,7,8,10,11}, {2,3,4,5,9,10,11}, {0,2,4,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 240. `[[39,6,3]]` — T0·T1·T2·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS25·CS34·CS35·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234·CCZ235

- gate `0+1+2+5+01+02+03+04+12+13+14+25+34+35+012+013+014+023+024+034+123+124+134+234+235`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {4,5,7}, {2,3,6,7,8}, {4,9}, {2,3,5,6,9}, {2,4,5,7,9}, {2,4,5,8,9}, {2,4,5,6,8,9}, {2,3,7,8,9}, {2,3,5,10}, {0,2,3,6,10}, {0,3,5,7,10}, {2,3,6,7,8,10}, {0,3,9,10}, {2,3,5,6,9,10}, {0,2,3,5,7,9,10}, {1,2,5,8,9,10}, {1,2,5,6,8,9,10}, {2,3,7,8,9,10}, {5,11}, {0,3,4,5,6,11}, {0,2,3,4,7,11}, {6,7,8,11}, {0,2,3,4,5,9,11}, {5,6,9,11}, {0,3,4,7,9,11}, {1,4,8,9,11}, {1,4,6,8,9,11}, {7,8,9,11}, {0,1,3,5,10,11}, {0,1,3,5,6,10,11}, {2,7,10,11}, {6,7,8,10,11}, {2,5,9,10,11}, {5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 241. `[[39,6,3]]` — T0·T1·T2·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS25·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ235·CCZ245·CCZ345

- gate `0+1+2+5+01+02+03+04+12+13+14+25+35+45+012+013+014+023+024+034+123+124+134+235+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {0,4,5,7}, {2,3,6,7,8}, {0,9}, {2,3,4,5,6,9}, {2,4,5,7,9}, {2,4,5,8,9}, {2,4,5,6,8,9}, {2,3,7,8,9}, {2,3,4,5,10}, {2,3,4,6,10}, {0,3,5,7,10}, {2,3,6,7,8,10}, {0,3,4,9,10}, {2,3,4,5,6,9,10}, {2,3,5,7,9,10}, {0,1,2,4,5,8,9,10}, {0,1,2,4,5,6,8,9,10}, {2,3,7,8,9,10}, {4,5,11}, {3,5,6,11}, {0,2,3,4,7,11}, {6,7,8,11}, {0,2,3,5,9,11}, {4,5,6,9,11}, {3,4,7,9,11}, {0,1,8,9,11}, {0,1,6,8,9,11}, {7,8,9,11}, {0,1,3,5,10,11}, {0,1,3,5,6,10,11}, {0,2,7,10,11}, {6,7,8,10,11}, {0,2,4,5,9,10,11}, {4,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 242. `[[39,6,3]]` — T0·T1·T2·T5·CS01·CS02·CS03·CS04·CS12·CS15·CS25·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ125

- gate `0+1+2+5+01+02+03+04+12+15+25+012+013+014+023+024+034+125`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {2,3,5,7}, {1,2,3,5,6,7,8}, {2,5,9}, {1,2,5,6,9}, {1,2,4,7,9}, {1,2,4,8,9}, {1,2,4,6,8,9}, {1,2,3,5,7,8,9}, {1,2,5,10}, {1,3,5,6,10}, {3,4,7,10}, {1,2,3,5,6,7,8,10}, {4,9,10}, {1,2,5,6,9,10}, {1,5,7,9,10}, {0,1,5,8,9,10}, {0,1,5,6,8,9,10}, {1,2,3,5,7,8,9,10}, {3,11}, {2,3,4,5,6,11}, {1,2,3,7,11}, {6,7,8,11}, {1,2,9,11}, {3,6,9,11}, {2,4,5,7,9,11}, {0,2,4,5,8,9,11}, {0,2,4,5,6,8,9,11}, {7,8,9,11}, {0,3,10,11}, {0,3,6,10,11}, {1,3,4,5,7,10,11}, {6,7,8,10,11}, {1,4,5,9,10,11}, {3,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 243. `[[39,6,3]]` — T0·T1·T2·T5·CS01·CS02·CS03·CS04·CS12·CS15·CS25·CS34·CS35·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ125·CCZ134·CCZ135·CCZ234·CCZ235

- gate `0+1+2+5+01+02+03+04+12+15+25+34+35+012+013+014+023+024+034+125+134+135+234+235`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {2,4,7}, {2,6,7,8}, {1,2,3,4,5,9}, {1,2,3,5,6,9}, {2,3,4,5,7,9}, {2,3,4,5,8,9}, {2,3,4,5,6,8,9}, {2,7,8,9}, {1,2,3,5,10}, {2,5,6,10}, {1,2,5,7,10}, {2,6,7,8,10}, {2,3,9,10}, {1,2,3,5,6,9,10}, {1,2,3,7,9,10}, {0,1,2,8,9,10}, {0,1,2,6,8,9,10}, {2,7,8,9,10}, {1,3,5,11}, {3,4,6,11}, {1,3,4,7,11}, {6,7,8,11}, {4,5,9,11}, {1,3,5,6,9,11}, {1,4,5,7,9,11}, {0,1,3,4,5,8,9,11}, {0,1,3,4,5,6,8,9,11}, {7,8,9,11}, {0,1,5,10,11}, {0,1,5,6,10,11}, {3,5,7,10,11}, {6,7,8,10,11}, {1,9,10,11}, {1,3,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 244. `[[39,6,3]]` — T0·T1·T2·T5·CS01·CS02·CS03·CS04·CS12·CS15·CS25·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ125·CCZ135·CCZ145·CCZ235·CCZ245·CCZ345

- gate `0+1+2+5+01+02+03+04+12+15+25+35+45+012+013+014+023+024+034+125+135+145+235+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{1,2,3,4,5,6}, {1,5,7}, {5,6,7,8}, {2,9}, {1,2,6,9}, {0,3,4,5,7,9}, {0,3,4,5,8,9}, {0,3,4,5,6,8,9}, {5,7,8,9}, {1,2,10}, {1,3,5,6,10}, {0,1,2,4,7,10}, {5,6,7,8,10}, {0,4,5,9,10}, {1,2,6,9,10}, {2,3,7,9,10}, {0,2,3,5,8,9,10}, {0,2,3,5,6,8,9,10}, {5,7,8,9,10}, {1,2,5,11}, {0,1,4,6,11}, {1,2,3,5,7,11}, {6,7,8,11}, {3,9,11}, {1,2,5,6,9,11}, {0,2,4,5,7,9,11}, {2,4,8,9,11}, {2,4,6,8,9,11}, {7,8,9,11}, {0,1,2,10,11}, {0,1,2,6,10,11}, {0,1,3,4,7,10,11}, {6,7,8,10,11}, {0,2,3,4,5,9,10,11}, {1,2,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 245. `[[39,6,3]]` — T0·T1·T2·T5·CS01·CS02·CS03·CS12·CS13·CS23·CS34·CS45·CCZ012·CCZ013·CCZ023·CCZ123

- gate `0+1+2+5+01+02+03+12+13+23+34+45+012+013+023+123`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,6}, {0,4,7}, {0,3,5,6,7,8}, {5,9}, {3,4,6,9}, {0,7,9}, {0,8,9}, {0,6,8,9}, {0,3,5,7,8,9}, {3,4,10}, {0,1,3,5,6,10}, {1,3,7,10}, {0,3,5,6,7,8,10}, {0,1,3,4,5,9,10}, {3,4,6,9,10}, {1,3,4,7,9,10}, {0,2,5,8,9,10}, {0,2,5,6,8,9,10}, {0,3,5,7,8,9,10}, {0,4,5,11}, {1,3,5,6,11}, {0,1,3,7,11}, {6,7,8,11}, {1,3,4,5,9,11}, {0,4,5,6,9,11}, {0,1,3,4,7,9,11}, {2,5,8,9,11}, {2,5,6,8,9,11}, {7,8,9,11}, {1,2,3,10,11}, {1,2,3,6,10,11}, {4,7,10,11}, {6,7,8,10,11}, {0,5,9,10,11}, {0,4,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 246. `[[39,6,3]]` — T0·T1·T2·T5·CS01·CS02·CS03·CS12·CS13·CS25·CS34·CS45·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234·CCZ245

- gate `0+1+2+5+01+02+03+12+13+25+34+45+012+013+023+123+234+245`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,6}, {0,7}, {0,2,3,4,5,6,7,8}, {5,9}, {2,3,4,6,9}, {0,2,4,7,9}, {0,2,4,8,9}, {0,2,4,6,8,9}, {0,2,3,4,5,7,8,9}, {2,3,4,10}, {0,1,2,3,4,5,6,10}, {1,3,7,10}, {0,2,3,4,5,6,7,8,10}, {0,1,3,5,9,10}, {2,3,4,6,9,10}, {1,2,3,4,7,9,10}, {0,2,5,8,9,10}, {0,2,5,6,8,9,10}, {0,2,3,4,5,7,8,9,10}, {0,5,11}, {1,3,5,6,11}, {0,1,2,3,4,7,11}, {6,7,8,11}, {1,2,3,4,5,9,11}, {0,5,6,9,11}, {0,1,3,7,9,11}, {4,5,8,9,11}, {4,5,6,8,9,11}, {7,8,9,11}, {1,3,4,10,11}, {1,3,4,6,10,11}, {2,4,7,10,11}, {6,7,8,10,11}, {0,2,4,5,9,10,11}, {0,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 247. `[[39,6,3]]` — T0·T1·T3·T4·T5·CS01·CS02·CS12·CS23·CS24·CS34·CCZ012·CCZ234

- gate `0+1+3+4+5+01+02+12+23+24+34+012+234`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{2,3,4,6}, {0,3,7}, {0,1,2,3,5,6,7,8}, {0,5,9}, {0,1,2,6,9}, {3,7,9}, {3,8,9}, {3,6,8,9}, {0,1,2,3,5,7,8,9}, {0,1,2,10}, {0,2,3,5,6,10}, {2,7,10}, {0,1,2,3,5,6,7,8,10}, {2,3,5,9,10}, {0,1,2,6,9,10}, {0,2,7,9,10}, {0,3,4,5,8,9,10}, {0,3,4,5,6,8,9,10}, {0,1,2,3,5,7,8,9,10}, {3,5,11}, {0,2,5,6,11}, {2,3,7,11}, {6,7,8,11}, {2,5,9,11}, {3,5,6,9,11}, {0,2,3,7,9,11}, {0,4,5,8,9,11}, {0,4,5,6,8,9,11}, {7,8,9,11}, {2,4,10,11}, {2,4,6,10,11}, {0,7,10,11}, {6,7,8,10,11}, {0,3,5,9,10,11}, {3,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 248. `[[39,6,3]]` — T0·T1·T3·T4·T5·CS01·CS02·CS12·CS23·CS45·CCZ012

- gate `0+1+3+4+5+01+02+12+23+45+012`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{4,5,6}, {1,2,3,4,7}, {1,2,4,6,7,8}, {2,9}, {2,3,6,9}, {0,2,3,4,7,9}, {0,2,3,4,8,9}, {0,2,3,4,6,8,9}, {1,2,4,7,8,9}, {2,3,10}, {2,4,6,10}, {0,2,3,7,10}, {1,2,4,6,7,8,10}, {0,1,2,4,9,10}, {2,3,6,9,10}, {1,2,3,7,9,10}, {0,3,4,5,8,9,10}, {0,3,4,5,6,8,9,10}, {1,2,4,7,8,9,10}, {1,3,4,11}, {0,3,6,11}, {4,7,11}, {6,7,8,11}, {1,3,9,11}, {1,3,4,6,9,11}, {0,1,4,7,9,11}, {2,5,8,9,11}, {2,5,6,8,9,11}, {7,8,9,11}, {0,2,3,5,10,11}, {0,2,3,5,6,10,11}, {0,1,7,10,11}, {6,7,8,10,11}, {0,3,4,9,10,11}, {1,3,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 249. `[[39,6,3]]` — T0·T1·T3·T5·CS01·CS02·CS12·CS23·CS24·CS34·CS45·CCZ012·CCZ234

- gate `0+1+3+5+01+02+12+23+24+34+45+012+234`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{4,5,6}, {0,2,4,7}, {0,1,2,3,6,7,8}, {0,2,3,4,9}, {0,1,2,6,9}, {2,4,7,9}, {2,4,8,9}, {2,4,6,8,9}, {0,1,2,3,7,8,9}, {0,1,2,10}, {0,1,2,3,5,6,10}, {1,2,5,7,10}, {0,1,2,3,6,7,8,10}, {1,2,3,5,9,10}, {0,1,2,6,9,10}, {0,1,2,5,7,9,10}, {0,1,3,8,9,10}, {0,1,3,6,8,9,10}, {0,1,2,3,7,8,9,10}, {3,11}, {0,1,3,4,5,6,11}, {1,4,5,7,11}, {6,7,8,11}, {1,3,4,5,9,11}, {3,6,9,11}, {0,1,4,5,7,9,11}, {0,1,2,3,4,8,9,11}, {0,1,2,3,4,6,8,9,11}, {7,8,9,11}, {2,5,10,11}, {2,5,6,10,11}, {0,7,10,11}, {6,7,8,10,11}, {0,3,9,10,11}, {3,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 250. `[[39,6,3]]` — T0·T1·T4·CS01·CS02·CS03·CS12·CS13·CS24·CS25·CS34·CS35·CS45·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234·CCZ235·CCZ245·CCZ345

- gate `0+1+4+01+02+03+12+13+24+25+34+35+45+012+013+023+123+234+235+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{5,6}, {0,3,7}, {3,6,7,8}, {1,2,3,9}, {0,1,2,3,6,9}, {0,1,3,4,5,7,9}, {0,1,3,4,5,8,9}, {0,1,3,4,5,6,8,9}, {3,7,8,9}, {0,1,2,3,10}, {2,3,6,10}, {0,3,4,5,7,10}, {3,6,7,8,10}, {1,2,3,4,5,9,10}, {0,1,2,3,6,9,10}, {0,1,3,7,9,10}, {0,1,2,4,8,9,10}, {0,1,2,4,6,8,9,10}, {3,7,8,9,10}, {0,1,2,11}, {0,1,2,4,5,6,11}, {1,7,11}, {6,7,8,11}, {0,2,9,11}, {0,1,2,6,9,11}, {4,5,7,9,11}, {2,3,5,8,9,11}, {2,3,5,6,8,9,11}, {7,8,9,11}, {0,1,3,4,10,11}, {0,1,3,4,6,10,11}, {1,4,5,7,10,11}, {6,7,8,10,11}, {0,2,4,5,9,10,11}, {0,1,2,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 251. `[[39,6,3]]` — T0·T1·T4·T5·CS01·CS02·CS03·CS12·CS13·CS23·CS24·CS25·CS45·CCZ012·CCZ013·CCZ023·CCZ123·CCZ245

- gate `0+1+4+5+01+02+03+12+13+23+24+25+45+012+013+023+123+245`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{2,4,5,6}, {0,2,3,4,7}, {0,1,2,3,4,6,7,8}, {1,3,9}, {3,6,9}, {3,4,7,9}, {3,4,8,9}, {3,4,6,8,9}, {0,1,2,3,4,7,8,9}, {3,10}, {1,2,3,4,6,10}, {2,3,7,10}, {0,1,2,3,4,6,7,8,10}, {0,1,3,4,9,10}, {3,6,9,10}, {0,3,7,9,10}, {1,4,5,8,9,10}, {1,4,5,6,8,9,10}, {0,1,2,3,4,7,8,9,10}, {0,1,2,4,11}, {1,2,6,11}, {2,4,7,11}, {6,7,8,11}, {0,1,9,11}, {0,1,2,4,6,9,11}, {0,4,7,9,11}, {1,3,5,8,9,11}, {1,3,5,6,8,9,11}, {7,8,9,11}, {2,3,5,10,11}, {2,3,5,6,10,11}, {0,2,7,10,11}, {6,7,8,10,11}, {1,4,9,10,11}, {0,1,2,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 252. `[[39,6,3]]` — T0·T1·T4·T5·CS01·CS02·CS03·CS12·CS13·CS23·CS24·CS35·CCZ012·CCZ013·CCZ023·CCZ123

- gate `0+1+4+5+01+02+03+12+13+23+24+35+012+013+023+123`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,6}, {0,4,7}, {0,2,4,6,7,8}, {4,9}, {2,4,6,9}, {0,3,5,7,9}, {0,3,5,8,9}, {0,3,5,6,8,9}, {0,2,4,7,8,9}, {2,4,10}, {0,2,3,4,6,10}, {2,5,7,10}, {0,2,4,6,7,8,10}, {0,2,5,9,10}, {2,4,6,9,10}, {2,3,4,7,9,10}, {0,1,3,4,5,8,9,10}, {0,1,3,4,5,6,8,9,10}, {0,2,4,7,8,9,10}, {0,11}, {2,4,5,6,11}, {0,2,3,7,11}, {6,7,8,11}, {2,3,9,11}, {0,6,9,11}, {0,2,4,5,7,9,11}, {1,4,8,9,11}, {1,4,6,8,9,11}, {7,8,9,11}, {1,2,5,10,11}, {1,2,5,6,10,11}, {3,4,5,7,10,11}, {6,7,8,10,11}, {0,3,4,5,9,10,11}, {0,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 253. `[[39,6,3]]` — T0·T1·T4·T5·CS01·CS02·CS03·CS12·CS13·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234

- gate `0+1+4+5+01+02+03+12+13+24+34+012+013+023+123+234`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{2,3,4,6}, {0,3,7}, {1,2,3,6,7,8}, {3,9}, {0,1,2,3,6,9}, {0,5,7,9}, {0,5,8,9}, {0,5,6,8,9}, {1,2,3,7,8,9}, {0,1,2,3,10}, {2,3,6,10}, {0,2,5,7,10}, {1,2,3,6,7,8,10}, {2,5,9,10}, {0,1,2,3,6,9,10}, {0,2,3,7,9,10}, {0,4,5,8,9,10}, {0,4,5,6,8,9,10}, {1,2,3,7,8,9,10}, {0,11}, {0,2,3,5,6,11}, {2,7,11}, {6,7,8,11}, {0,2,9,11}, {0,6,9,11}, {2,3,5,7,9,11}, {4,8,9,11}, {4,6,8,9,11}, {7,8,9,11}, {0,2,3,4,5,10,11}, {0,2,3,4,5,6,10,11}, {3,5,7,10,11}, {6,7,8,10,11}, {0,3,5,9,10,11}, {0,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 254. `[[39,6,3]]` — T0·T1·T4·T5·CS01·CS02·CS03·CS12·CS13·CS45·CCZ012·CCZ013·CCZ023·CCZ123

- gate `0+1+4+5+01+02+03+12+13+45+012+013+023+123`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,6}, {4,7}, {3,5,6,7,8}, {3,9}, {4,5,6,9}, {2,4,7,9}, {2,4,8,9}, {2,4,6,8,9}, {3,5,7,8,9}, {4,5,10}, {0,2,6,10}, {0,3,4,7,10}, {3,5,6,7,8,10}, {0,9,10}, {4,5,6,9,10}, {0,2,3,4,7,9,10}, {1,2,3,4,8,9,10}, {1,2,3,4,6,8,9,10}, {3,5,7,8,9,10}, {3,4,11}, {0,4,6,11}, {0,2,3,7,11}, {6,7,8,11}, {0,2,4,9,11}, {3,4,6,9,11}, {0,3,7,9,11}, {1,3,8,9,11}, {1,3,6,8,9,11}, {7,8,9,11}, {0,1,3,4,10,11}, {0,1,3,4,6,10,11}, {2,7,10,11}, {6,7,8,10,11}, {2,3,4,9,10,11}, {3,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 255. `[[39,6,3]]` — T0·T1·T4·T5·CS01·CS02·CS03·CS14·CS15·CS23·CS24·CS35·CCZ012·CCZ013·CCZ023·CCZ123·CCZ124·CCZ135

- gate `0+1+4+5+01+02+03+14+15+23+24+35+012+013+023+123+124+135`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,6}, {2,7}, {1,2,3,4,5,6,7,8}, {4,9}, {1,3,5,6,9}, {1,7,9}, {1,8,9}, {1,6,8,9}, {1,2,3,4,5,7,8,9}, {1,3,5,10}, {0,1,2,3,4,5,6,10}, {0,2,3,5,7,10}, {1,2,3,4,5,6,7,8,10}, {0,3,4,5,9,10}, {1,3,5,6,9,10}, {0,1,3,5,7,9,10}, {1,4,5,8,9,10}, {1,4,5,6,8,9,10}, {1,2,3,4,5,7,8,9,10}, {2,4,11}, {0,2,3,4,5,6,11}, {0,1,2,3,5,7,11}, {6,7,8,11}, {0,1,3,4,5,9,11}, {2,4,6,9,11}, {0,3,5,7,9,11}, {4,5,8,9,11}, {4,5,6,8,9,11}, {7,8,9,11}, {0,2,3,10,11}, {0,2,3,6,10,11}, {1,2,7,10,11}, {6,7,8,10,11}, {1,4,9,10,11}, {2,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 256. `[[39,6,3]]` — T0·T1·T4·T5·CS01·CS02·CS03·CS14·CS15·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ124·CCZ134·CCZ234

- gate `0+1+4+5+01+02+03+14+15+24+34+012+013+023+124+134+234`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,6}, {0,1,3,4,7}, {1,2,5,6,7,8}, {0,1,5,9}, {1,2,3,4,6,9}, {1,3,4,7,9}, {1,3,4,8,9}, {1,3,4,6,8,9}, {1,2,5,7,8,9}, {1,2,3,4,10}, {1,2,3,5,6,10}, {0,1,2,4,7,10}, {1,2,5,6,7,8,10}, {0,1,2,3,5,9,10}, {1,2,3,4,6,9,10}, {1,2,4,7,9,10}, {0,1,3,4,5,8,9,10}, {0,1,3,4,5,6,8,9,10}, {1,2,5,7,8,9,10}, {3,4,5,11}, {2,4,5,6,11}, {0,2,3,7,11}, {6,7,8,11}, {0,2,4,5,9,11}, {3,4,5,6,9,11}, {2,3,7,9,11}, {0,5,8,9,11}, {0,5,6,8,9,11}, {7,8,9,11}, {0,2,4,10,11}, {0,2,4,6,10,11}, {0,7,10,11}, {6,7,8,10,11}, {0,3,4,5,9,10,11}, {3,4,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 257. `[[39,6,3]]` — T0·T1·T4·T5·CS01·CS02·CS03·CS14·CS15·CS45·CCZ012·CCZ013·CCZ023·CCZ145

- gate `0+1+4+5+01+02+03+14+15+45+012+013+023+145`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{1,4,5,6}, {0,3,4,7}, {3,6,7,8}, {1,2,3,4,9}, {0,1,2,3,6,9}, {0,3,7,9}, {0,3,8,9}, {0,3,6,8,9}, {3,7,8,9}, {0,1,2,3,10}, {2,3,6,10}, {0,1,3,4,7,10}, {3,6,7,8,10}, {2,3,4,9,10}, {0,1,2,3,6,9,10}, {0,1,3,7,9,10}, {0,1,2,4,5,8,9,10}, {0,1,2,4,5,6,8,9,10}, {3,7,8,9,10}, {0,1,2,11}, {0,2,6,11}, {1,4,7,11}, {6,7,8,11}, {0,2,4,9,11}, {0,1,2,6,9,11}, {1,7,9,11}, {1,2,3,4,5,8,9,11}, {1,2,3,4,5,6,8,9,11}, {7,8,9,11}, {0,1,3,4,5,10,11}, {0,1,3,4,5,6,10,11}, {4,7,10,11}, {6,7,8,10,11}, {0,1,2,4,9,10,11}, {0,1,2,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 258. `[[39,6,3]]` — T0·T1·T4·T5·CS01·CS02·CS12·CS23·CS34·CS35·CS45·CCZ012·CCZ345

- gate `0+1+4+5+01+02+12+23+34+35+45+012+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{2,3,6}, {1,2,3,4,5,7}, {1,2,5,6,7,8}, {5,9}, {3,4,5,6,9}, {0,3,4,7,9}, {0,3,4,8,9}, {0,3,4,6,8,9}, {1,2,5,7,8,9}, {3,4,5,10}, {1,2,3,5,6,10}, {0,1,2,4,7,10}, {1,2,5,6,7,8,10}, {0,3,9,10}, {3,4,5,6,9,10}, {4,5,7,9,10}, {0,1,3,4,5,8,9,10}, {0,1,3,4,5,6,8,9,10}, {1,2,5,7,8,9,10}, {1,2,3,4,11}, {0,1,2,4,5,6,11}, {1,2,3,7,11}, {6,7,8,11}, {4,9,11}, {1,2,3,4,6,9,11}, {0,3,5,7,9,11}, {1,5,8,9,11}, {1,5,6,8,9,11}, {7,8,9,11}, {0,2,4,10,11}, {0,2,4,6,10,11}, {0,1,2,5,7,10,11}, {6,7,8,10,11}, {0,3,4,5,9,10,11}, {1,2,3,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 259. `[[39,6,3]]` — T0·T1·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134

- gate `0+1+5+01+02+03+04+12+13+14+012+013+014+023+024+034+123+124+134`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {0,4,7}, {3,5,6,7,8}, {0,2,5,9}, {2,3,4,6,9}, {2,4,7,9}, {2,4,8,9}, {2,4,6,8,9}, {3,5,7,8,9}, {2,3,4,10}, {3,4,5,6,10}, {0,3,7,10}, {3,5,6,7,8,10}, {0,2,3,4,5,9,10}, {2,3,4,6,9,10}, {2,3,7,9,10}, {0,1,4,5,8,9,10}, {0,1,4,5,6,8,9,10}, {3,5,7,8,9,10}, {2,4,5,11}, {2,3,5,6,11}, {0,2,3,4,7,11}, {6,7,8,11}, {0,3,5,9,11}, {2,4,5,6,9,11}, {3,4,7,9,11}, {0,1,2,5,8,9,11}, {0,1,2,5,6,8,9,11}, {7,8,9,11}, {0,1,3,10,11}, {0,1,3,6,10,11}, {0,2,7,10,11}, {6,7,8,10,11}, {0,4,5,9,10,11}, {2,4,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 260. `[[39,6,3]]` — T0·T1·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CS25·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234

- gate `0+1+5+01+02+03+04+12+13+14+23+24+25+012+013+014+023+024+034+123+124+134+234`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {1,2,3,4,5,7}, {1,2,4,5,6,7,8}, {2,3,5,9}, {2,5,6,9}, {1,3,7,9}, {1,3,8,9}, {1,3,6,8,9}, {1,2,4,5,7,8,9}, {2,5,10}, {0,1,2,4,5,6,10}, {0,4,7,10}, {1,2,4,5,6,7,8,10}, {0,1,9,10}, {2,5,6,9,10}, {0,2,5,7,9,10}, {1,5,8,9,10}, {1,5,6,8,9,10}, {1,2,4,5,7,8,9,10}, {1,4,11}, {0,2,3,4,5,6,11}, {0,1,3,4,7,11}, {6,7,8,11}, {0,3,9,11}, {1,4,6,9,11}, {0,1,2,3,5,7,9,11}, {3,5,8,9,11}, {3,5,6,8,9,11}, {7,8,9,11}, {0,2,4,10,11}, {0,2,4,6,10,11}, {2,4,5,7,10,11}, {6,7,8,10,11}, {1,2,5,9,10,11}, {1,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 261. `[[39,6,3]]` — T0·T1·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234·CCZ345

- gate `0+1+5+01+02+03+04+12+13+14+23+24+35+45+012+013+014+023+024+034+123+124+134+234+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {0,4,5,7}, {2,3,6,7,8}, {0,2,9}, {3,4,5,6,9}, {4,5,7,9}, {4,5,8,9}, {4,5,6,8,9}, {2,3,7,8,9}, {3,4,5,10}, {1,3,6,10}, {0,1,2,3,4,5,7,10}, {2,3,6,7,8,10}, {0,1,3,9,10}, {3,4,5,6,9,10}, {1,2,3,4,5,7,9,10}, {0,2,5,8,9,10}, {0,2,5,6,8,9,10}, {2,3,7,8,9,10}, {2,4,5,11}, {1,3,4,5,6,11}, {0,1,2,3,7,11}, {6,7,8,11}, {0,1,3,4,5,9,11}, {2,4,5,6,9,11}, {1,2,3,7,9,11}, {0,2,4,8,9,11}, {0,2,4,6,8,9,11}, {7,8,9,11}, {0,1,2,3,5,10,11}, {0,1,2,3,5,6,10,11}, {0,7,10,11}, {6,7,8,10,11}, {0,2,4,5,9,10,11}, {2,4,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 262. `[[39,6,3]]` — T0·T1·T5·CS01·CS02·CS03·CS04·CS15·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034

- gate `0+1+5+01+02+03+04+15+012+013+014+023+024+034`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{1,5,6}, {0,3,4,7}, {0,1,2,4,6,7,8}, {4,9}, {1,2,3,4,6,9}, {1,2,4,7,9}, {1,2,4,8,9}, {1,2,4,6,8,9}, {0,1,2,4,7,8,9}, {1,2,3,4,10}, {1,4,6,10}, {2,4,7,10}, {0,1,2,4,6,7,8,10}, {0,2,3,4,9,10}, {1,2,3,4,6,9,10}, {0,1,3,4,7,9,10}, {1,2,5,8,9,10}, {1,2,5,6,8,9,10}, {0,1,2,4,7,8,9,10}, {0,3,11}, {2,6,11}, {1,7,11}, {6,7,8,11}, {0,1,3,9,11}, {0,3,6,9,11}, {0,2,3,7,9,11}, {4,5,8,9,11}, {4,5,6,8,9,11}, {7,8,9,11}, {2,4,5,10,11}, {2,4,5,6,10,11}, {0,1,2,3,7,10,11}, {6,7,8,10,11}, {1,2,9,10,11}, {0,3,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 263. `[[39,6,3]]` — T0·T1·T5·CS01·CS02·CS03·CS04·CS15·CS23·CS24·CS25·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ125·CCZ234

- gate `0+1+5+01+02+03+04+15+23+24+25+012+013+014+023+024+034+123+124+125+234`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {0,1,2,5,7}, {0,1,2,4,5,6,7,8}, {1,3,9}, {1,3,4,6,9}, {0,1,3,7,9}, {0,1,3,8,9}, {0,1,3,6,8,9}, {0,1,2,4,5,7,8,9}, {1,3,4,10}, {0,2,4,5,6,10}, {2,4,5,7,10}, {0,1,2,4,5,6,7,8,10}, {0,3,4,9,10}, {1,3,4,6,9,10}, {3,4,7,9,10}, {0,5,8,9,10}, {0,5,6,8,9,10}, {0,1,2,4,5,7,8,9,10}, {0,2,3,5,11}, {1,2,3,4,5,6,11}, {0,1,2,3,4,5,7,11}, {6,7,8,11}, {1,4,9,11}, {0,2,3,5,6,9,11}, {0,1,4,7,9,11}, {1,3,5,8,9,11}, {1,3,5,6,8,9,11}, {7,8,9,11}, {2,4,10,11}, {2,4,6,10,11}, {2,3,5,7,10,11}, {6,7,8,10,11}, {0,9,10,11}, {0,2,3,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 264. `[[39,6,3]]` — T0·T1·T5·CS01·CS02·CS03·CS04·CS15·CS23·CS24·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ135·CCZ145·CCZ234·CCZ345

- gate `0+1+5+01+02+03+04+15+23+24+35+45+012+013+014+023+024+034+123+124+135+145+234+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{1,3,4,5,6}, {2,7}, {0,2,4,6,7,8}, {0,1,2,4,9}, {1,2,6,9}, {2,3,7,9}, {2,3,8,9}, {2,3,6,8,9}, {0,2,4,7,8,9}, {1,2,10}, {0,2,4,5,6,10}, {1,2,3,5,7,10}, {0,2,4,6,7,8,10}, {0,2,3,4,5,9,10}, {1,2,6,9,10}, {1,2,5,7,9,10}, {0,1,8,9,10}, {0,1,6,8,9,10}, {0,2,4,7,8,9,10}, {0,1,4,11}, {0,3,4,5,6,11}, {1,5,7,11}, {6,7,8,11}, {0,4,5,9,11}, {0,1,4,6,9,11}, {1,3,5,7,9,11}, {0,1,2,3,8,9,11}, {0,1,2,3,6,8,9,11}, {7,8,9,11}, {1,2,4,5,10,11}, {1,2,4,5,6,10,11}, {3,7,10,11}, {6,7,8,10,11}, {0,1,3,4,9,10,11}, {0,1,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 265. `[[39,6,3]]` — T0·T1·T5·CS01·CS02·CS03·CS04·CS15·CS25·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ125·CCZ135·CCZ145·CCZ235·CCZ245·CCZ345

- gate `0+1+5+01+02+03+04+15+25+35+45+012+013+014+023+024+034+125+135+145+235+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{1,2,3,4,5,6}, {2,3,7}, {0,2,4,6,7,8}, {0,1,3,4,9}, {1,6,9}, {3,7,9}, {3,8,9}, {3,6,8,9}, {0,2,4,7,8,9}, {1,10}, {0,2,6,10}, {1,2,4,7,10}, {0,2,4,6,7,8,10}, {0,9,10}, {1,6,9,10}, {1,4,7,9,10}, {0,1,4,5,8,9,10}, {0,1,4,5,6,8,9,10}, {0,2,4,7,8,9,10}, {0,1,2,4,11}, {0,2,3,6,11}, {1,2,3,4,7,11}, {6,7,8,11}, {0,3,9,11}, {0,1,2,4,6,9,11}, {1,3,4,7,9,11}, {0,1,3,4,5,8,9,11}, {0,1,3,4,5,6,8,9,11}, {7,8,9,11}, {1,2,4,5,10,11}, {1,2,4,5,6,10,11}, {2,7,10,11}, {6,7,8,10,11}, {0,1,4,9,10,11}, {0,1,2,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 266. `[[39,6,3]]` — T0·T1·T5·CS01·CS02·CS03·CS12·CS13·CS23·CS24·CS25·CS34·CS45·CCZ012·CCZ013·CCZ023·CCZ123·CCZ245

- gate `0+1+5+01+02+03+12+13+23+24+25+34+45+012+013+023+123+245`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,6}, {0,2,4,5,7}, {0,2,5,6,7,8}, {2,5,9}, {2,4,5,6,9}, {0,3,7,9}, {0,3,8,9}, {0,3,6,8,9}, {0,2,5,7,8,9}, {2,4,5,10}, {0,5,6,10}, {2,3,7,10}, {0,2,5,6,7,8,10}, {0,2,3,4,9,10}, {2,4,5,6,9,10}, {4,5,7,9,10}, {0,1,2,5,8,9,10}, {0,1,2,5,6,8,9,10}, {0,2,5,7,8,9,10}, {0,4,11}, {3,5,6,11}, {0,2,7,11}, {6,7,8,11}, {2,4,9,11}, {0,4,6,9,11}, {0,3,4,5,7,9,11}, {1,2,3,5,8,9,11}, {1,2,3,5,6,8,9,11}, {7,8,9,11}, {1,2,10,11}, {1,2,6,10,11}, {2,3,4,5,7,10,11}, {6,7,8,10,11}, {0,2,3,5,9,10,11}, {0,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 267. `[[39,6,3]]` — T0·T1·T5·CS01·CS02·CS03·CS12·CS13·CS24·CS34·CS45·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234

- gate `0+1+5+01+02+03+12+13+24+34+45+012+013+023+123+234`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{2,3,4,6}, {0,7}, {0,1,2,6,7,8}, {0,3,9}, {0,1,2,3,6,9}, {3,4,5,7,9}, {3,4,5,8,9}, {3,4,5,6,8,9}, {0,1,2,7,8,9}, {0,1,2,3,10}, {0,1,2,4,6,10}, {1,2,5,7,10}, {0,1,2,6,7,8,10}, {1,2,3,5,9,10}, {0,1,2,3,6,9,10}, {0,1,2,3,4,7,9,10}, {0,1,4,5,8,9,10}, {0,1,4,5,6,8,9,10}, {0,1,2,7,8,9,10}, {3,11}, {0,1,2,3,5,6,11}, {1,2,3,4,7,11}, {6,7,8,11}, {1,2,4,9,11}, {3,6,9,11}, {0,1,2,5,7,9,11}, {0,1,3,8,9,11}, {0,1,3,6,8,9,11}, {7,8,9,11}, {2,5,10,11}, {2,5,6,10,11}, {0,3,4,5,7,10,11}, {6,7,8,10,11}, {0,4,5,9,10,11}, {3,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 268. `[[39,6,3]]` — T0·T1·T5·CS01·CS02·CS03·CS15·CS23·CS24·CS25·CS34·CS45·CCZ012·CCZ013·CCZ023·CCZ123·CCZ124·CCZ125·CCZ134·CCZ145·CCZ245

- gate `0+1+5+01+02+03+15+23+24+25+34+45+012+013+023+123+124+125+134+145+245`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,6}, {3,4,7}, {4,6,7,8}, {1,2,3,4,5,9}, {1,2,4,5,6,9}, {2,3,4,5,7,9}, {2,3,4,5,8,9}, {2,3,4,5,6,8,9}, {4,7,8,9}, {1,2,4,5,10}, {4,5,6,10}, {1,4,5,7,10}, {4,6,7,8,10}, {2,4,9,10}, {1,2,4,5,6,9,10}, {1,2,4,7,9,10}, {0,1,8,9,10}, {0,1,6,8,9,10}, {4,7,8,9,10}, {1,2,5,11}, {2,3,6,11}, {1,2,3,7,11}, {6,7,8,11}, {3,5,9,11}, {1,2,5,6,9,11}, {1,3,5,7,9,11}, {0,1,2,3,4,5,8,9,11}, {0,1,2,3,4,5,6,8,9,11}, {7,8,9,11}, {0,1,4,5,10,11}, {0,1,4,5,6,10,11}, {2,5,7,10,11}, {6,7,8,10,11}, {1,9,10,11}, {1,2,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 269. `[[39,6,3]]` — T0·T1·T5·CS01·CS02·CS03·CS15·CS24·CS34·CS45·CCZ012·CCZ013·CCZ023·CCZ124·CCZ134·CCZ145·CCZ234

- gate `0+1+5+01+02+03+15+24+34+45+012+013+023+124+134+145+234`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,6}, {1,3,4,7}, {1,2,6,7,8}, {1,9}, {1,2,3,4,6,9}, {1,3,5,7,9}, {1,3,5,8,9}, {1,3,5,6,8,9}, {1,2,7,8,9}, {1,2,3,4,10}, {1,2,3,6,10}, {1,2,5,7,10}, {1,2,6,7,8,10}, {1,2,3,4,5,9,10}, {1,2,3,4,6,9,10}, {1,2,4,7,9,10}, {0,1,3,5,8,9,10}, {0,1,3,5,6,8,9,10}, {1,2,7,8,9,10}, {3,4,11}, {2,5,6,11}, {2,3,7,11}, {6,7,8,11}, {2,4,9,11}, {3,4,6,9,11}, {2,3,4,5,7,9,11}, {0,8,9,11}, {0,6,8,9,11}, {7,8,9,11}, {0,2,5,10,11}, {0,2,5,6,10,11}, {4,5,7,10,11}, {6,7,8,10,11}, {3,5,9,10,11}, {3,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 270. `[[39,6,3]]` — T0·T1·T5·CS01·CS02·CS12·CS23·CS24·CS35·CS45·CCZ012·CCZ234·CCZ345

- gate `0+1+5+01+02+12+23+24+35+45+012+234+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{2,3,4,6}, {0,2,4,5,7}, {4,5,6,7,8}, {1,9}, {0,1,2,6,9}, {0,1,2,3,7,9}, {0,1,2,3,8,9}, {0,1,2,3,6,8,9}, {4,5,7,8,9}, {0,1,2,10}, {5,6,10}, {0,2,3,5,7,10}, {4,5,6,7,8,10}, {1,3,4,9,10}, {0,1,2,6,9,10}, {0,1,2,4,7,9,10}, {0,1,4,5,8,9,10}, {0,1,4,5,6,8,9,10}, {4,5,7,8,9,10}, {0,1,2,4,5,11}, {0,1,2,3,5,6,11}, {1,5,7,11}, {6,7,8,11}, {0,2,4,9,11}, {0,1,2,4,5,6,9,11}, {3,4,7,9,11}, {2,3,4,5,8,9,11}, {2,3,4,5,6,8,9,11}, {7,8,9,11}, {0,1,4,10,11}, {0,1,4,6,10,11}, {1,3,4,5,7,10,11}, {6,7,8,10,11}, {0,2,3,9,10,11}, {0,1,2,4,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 271. `[[39,6,3]]` — T0·CS12·CS13·CS14·CS15·CCZ012·CCZ013·CCZ014·CCZ015·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145

- gate `0+12+13+14+15+012+013+014+015+123+124+125+134+135+145`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,6}, {0,1,2,3,5,7}, {4,5,6,7,8}, {5,9}, {0,1,2,3,4,5,6,9}, {1,4,5,7,9}, {1,4,5,8,9}, {1,4,5,6,8,9}, {4,5,7,8,9}, {0,1,2,3,4,5,10}, {1,3,4,5,6,10}, {3,5,7,10}, {4,5,6,7,8,10}, {0,1,2,5,9,10}, {0,1,2,3,4,5,6,9,10}, {0,2,4,5,7,9,10}, {0,1,3,8,9,10}, {0,1,3,6,8,9,10}, {4,5,7,8,9,10}, {0,1,2,3,11}, {3,6,11}, {1,3,4,7,11}, {6,7,8,11}, {0,2,4,9,11}, {0,1,2,3,6,9,11}, {0,1,2,7,9,11}, {0,3,4,5,8,9,11}, {0,3,4,5,6,8,9,11}, {7,8,9,11}, {0,4,5,10,11}, {0,4,5,6,10,11}, {0,2,3,4,7,10,11}, {6,7,8,10,11}, {1,4,9,10,11}, {0,1,2,3,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 272. `[[39,6,3]]` — T0·CS12·CS13·CS14·CS15·CS23·CS24·CS25·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ025·CCZ134·CCZ135·CCZ145·CCZ234·CCZ235·CCZ245

- gate `0+12+13+14+15+23+24+25+012+013+014+015+023+024+025+134+135+145+234+235+245`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,3,4,5,6}, {0,2,5,7}, {0,2,3,5,6,7,8}, {0,2,4,5,9}, {0,2,3,4,5,6,9}, {0,1,2,4,7,9}, {0,1,2,4,8,9}, {0,1,2,4,6,8,9}, {0,2,3,5,7,8,9}, {0,2,3,4,5,10}, {0,2,3,6,10}, {0,1,2,3,5,7,10}, {0,2,3,5,6,7,8,10}, {0,1,2,3,4,5,9,10}, {0,2,3,4,5,6,9,10}, {0,2,3,4,7,9,10}, {0,5,8,9,10}, {0,5,6,8,9,10}, {0,2,3,5,7,8,9,10}, {4,11}, {1,3,4,6,11}, {3,4,5,7,11}, {6,7,8,11}, {3,5,9,11}, {4,6,9,11}, {1,3,7,9,11}, {1,2,4,5,8,9,11}, {1,2,4,5,6,8,9,11}, {7,8,9,11}, {2,3,5,10,11}, {2,3,5,6,10,11}, {1,4,5,7,10,11}, {6,7,8,10,11}, {1,5,9,10,11}, {4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 273. `[[39,6,3]]` — T0·CS12·CS13·CS14·CS15·CS23·CS24·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ015·CCZ023·CCZ024·CCZ035·CCZ045·CCZ125·CCZ134·CCZ234·CCZ235·CCZ245·CCZ345

- gate `0+12+13+14+15+23+24+35+45+012+013+014+015+023+024+035+045+125+134+234+235+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,2,3,4,5,6}, {0,1,4,5,7}, {3,6,7,8}, {5,9}, {0,1,3,4,6,9}, {2,4,5,7,9}, {2,4,5,8,9}, {2,4,5,6,8,9}, {3,7,8,9}, {0,1,3,4,10}, {0,2,3,6,10}, {0,3,4,7,10}, {3,6,7,8,10}, {1,3,9,10}, {0,1,3,4,6,9,10}, {1,2,3,4,7,9,10}, {2,8,9,10}, {2,6,8,9,10}, {3,7,8,9,10}, {0,1,4,11}, {0,3,4,5,6,11}, {0,2,3,5,7,11}, {6,7,8,11}, {1,2,3,4,5,9,11}, {0,1,4,6,9,11}, {1,3,5,7,9,11}, {4,5,8,9,11}, {4,5,6,8,9,11}, {7,8,9,11}, {0,3,10,11}, {0,3,6,10,11}, {0,1,2,7,10,11}, {6,7,8,10,11}, {2,4,9,10,11}, {0,1,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 274. `[[39,6,3]]` — T0·CS12·CS13·CS14·CS25·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ025·CCZ035·CCZ045·CCZ123·CCZ124·CCZ125·CCZ134·CCZ135·CCZ145·CCZ235·CCZ245·CCZ345

- gate `0+12+13+14+25+35+45+012+013+014+025+035+045+123+124+125+134+135+145+235+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,5,6}, {0,1,2,4,5,7}, {3,4,6,7,8}, {4,9}, {0,1,2,3,4,5,6,9}, {1,3,4,5,7,9}, {1,3,4,5,8,9}, {1,3,4,5,6,8,9}, {3,4,7,8,9}, {0,1,2,3,4,5,10}, {0,1,4,6,10}, {0,3,4,5,7,10}, {3,4,6,7,8,10}, {1,2,3,4,9,10}, {0,1,2,3,4,5,6,9,10}, {2,4,5,7,9,10}, {1,3,8,9,10}, {1,3,6,8,9,10}, {3,4,7,8,9,10}, {0,1,2,5,11}, {0,3,5,6,11}, {0,1,7,11}, {6,7,8,11}, {2,5,9,11}, {0,1,2,5,6,9,11}, {1,2,3,7,9,11}, {4,5,8,9,11}, {4,5,6,8,9,11}, {7,8,9,11}, {0,3,4,10,11}, {0,3,4,6,10,11}, {0,2,3,7,10,11}, {6,7,8,10,11}, {1,3,5,9,10,11}, {0,1,2,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 275. `[[39,6,3]]` — T0·T3·T4·T5·CS01·CS02·CS13·CS23·CS45·CCZ012·CCZ123

- gate `0+3+4+5+01+02+13+23+45+012+123`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{1,2,3,6}, {3,4,5,7}, {3,5,6,7,8}, {5,9}, {4,5,6,9}, {0,1,2,3,4,7,9}, {0,1,2,3,4,8,9}, {0,1,2,3,4,6,8,9}, {3,5,7,8,9}, {4,5,10}, {1,3,5,6,10}, {0,2,4,7,10}, {3,5,6,7,8,10}, {0,2,3,9,10}, {4,5,6,9,10}, {1,4,5,7,9,10}, {0,1,3,4,5,8,9,10}, {0,1,3,4,5,6,8,9,10}, {3,5,7,8,9,10}, {3,4,11}, {0,2,4,5,6,11}, {1,3,7,11}, {6,7,8,11}, {1,4,9,11}, {3,4,6,9,11}, {0,2,3,5,7,9,11}, {2,5,8,9,11}, {2,5,6,8,9,11}, {7,8,9,11}, {0,4,10,11}, {0,4,6,10,11}, {0,1,2,5,7,10,11}, {6,7,8,10,11}, {0,1,2,3,4,5,9,10,11}, {3,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 276. `[[39,6,3]]` — T0·T4·T5·CS01·CS02·CS03·CS12·CS13·CS14·CS15·CS45·CCZ012·CCZ013·CCZ023·CCZ123·CCZ145

- gate `0+4+5+01+02+03+12+13+14+15+45+012+013+023+123+145`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{1,4,5,6}, {1,2,3,7}, {3,6,7,8}, {1,3,9}, {2,3,6,9}, {0,1,3,7,9}, {0,1,3,8,9}, {0,1,3,6,8,9}, {3,7,8,9}, {2,3,10}, {3,4,6,10}, {0,3,4,7,10}, {3,6,7,8,10}, {0,2,3,4,9,10}, {2,3,6,9,10}, {2,3,4,7,9,10}, {0,5,8,9,10}, {0,5,6,8,9,10}, {3,7,8,9,10}, {2,11}, {0,1,4,6,11}, {1,4,7,11}, {6,7,8,11}, {1,2,4,9,11}, {2,6,9,11}, {0,1,2,4,7,9,11}, {1,3,5,8,9,11}, {1,3,5,6,8,9,11}, {7,8,9,11}, {0,3,4,5,10,11}, {0,3,4,5,6,10,11}, {0,2,7,10,11}, {6,7,8,10,11}, {0,9,10,11}, {2,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 277. `[[39,6,3]]` — T0·T4·T5·CS01·CS02·CS03·CS12·CS13·CS14·CS25·CS35·CCZ012·CCZ013·CCZ023·CCZ123·CCZ235

- gate `0+4+5+01+02+03+12+13+14+25+35+012+013+023+123+235`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{2,3,5,6}, {1,3,7}, {0,1,2,6,7,8}, {1,9}, {0,1,2,3,6,9}, {1,3,4,7,9}, {1,3,4,8,9}, {1,3,4,6,8,9}, {0,1,2,7,8,9}, {0,1,2,3,10}, {1,2,3,6,10}, {1,2,4,7,10}, {0,1,2,6,7,8,10}, {1,2,3,4,9,10}, {0,1,2,3,6,9,10}, {1,2,7,9,10}, {3,4,5,8,9,10}, {3,4,5,6,8,9,10}, {0,1,2,7,8,9,10}, {3,11}, {2,4,6,11}, {2,3,7,11}, {6,7,8,11}, {2,9,11}, {3,6,9,11}, {2,3,4,7,9,11}, {1,5,8,9,11}, {1,5,6,8,9,11}, {7,8,9,11}, {1,2,4,5,10,11}, {1,2,4,5,6,10,11}, {4,7,10,11}, {6,7,8,10,11}, {3,4,9,10,11}, {3,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 278. `[[39,6,3]]` — T0·T4·T5·CS01·CS02·CS03·CS14·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ124·CCZ134·CCZ234

- gate `0+4+5+01+02+03+14+24+34+012+013+023+124+134+234`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{1,2,3,4,6}, {0,1,3,5,7}, {2,3,5,6,7,8}, {0,1,2,5,9}, {5,6,9}, {0,1,7,9}, {0,1,8,9}, {0,1,6,8,9}, {2,3,5,7,8,9}, {5,10}, {0,3,5,6,10}, {0,2,3,7,10}, {2,3,5,6,7,8,10}, {0,9,10}, {5,6,9,10}, {0,2,5,7,9,10}, {2,4,5,8,9,10}, {2,4,5,6,8,9,10}, {2,3,5,7,8,9,10}, {2,3,11}, {1,3,5,6,11}, {1,2,3,7,11}, {6,7,8,11}, {1,9,11}, {2,3,6,9,11}, {1,2,5,7,9,11}, {0,1,2,4,5,8,9,11}, {0,1,2,4,5,6,8,9,11}, {7,8,9,11}, {0,2,3,4,10,11}, {0,2,3,4,6,10,11}, {3,5,7,10,11}, {6,7,8,10,11}, {2,5,9,10,11}, {2,3,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 279. `[[39,6,3]]` — T0·T4·T5·CS01·CS02·CS03·CS45·CCZ012·CCZ013·CCZ023

- gate `0+4+5+01+02+03+45+012+013+023`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{4,5,6}, {0,1,3,4,7}, {0,3,6,7,8}, {0,2,3,4,9}, {0,1,2,3,6,9}, {3,7,9}, {3,8,9}, {3,6,8,9}, {0,3,7,8,9}, {0,1,2,3,10}, {0,2,3,6,10}, {3,4,7,10}, {0,3,6,7,8,10}, {1,2,3,4,9,10}, {0,1,2,3,6,9,10}, {0,1,3,7,9,10}, {0,2,4,5,8,9,10}, {0,2,4,5,6,8,9,10}, {0,3,7,8,9,10}, {1,2,11}, {0,2,6,11}, {4,7,11}, {6,7,8,11}, {1,2,4,9,11}, {1,2,6,9,11}, {0,1,7,9,11}, {0,2,3,4,5,8,9,11}, {0,2,3,4,5,6,8,9,11}, {7,8,9,11}, {3,4,5,10,11}, {3,4,5,6,10,11}, {0,1,4,7,10,11}, {6,7,8,10,11}, {0,2,4,9,10,11}, {1,2,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 280. `[[39,6,3]]` — T0·T4·T5·CS01·CS02·CS12·CS13·CS14·CS23·CS25·CS34·CS35·CCZ012·CCZ134·CCZ235

- gate `0+4+5+01+02+12+13+14+23+25+34+35+012+134+235`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{2,3,5,6}, {1,4,7}, {1,3,6,7,8}, {1,9}, {1,3,4,6,9}, {0,1,2,4,7,9}, {0,1,2,4,8,9}, {0,1,2,4,6,8,9}, {1,3,7,8,9}, {1,3,4,10}, {1,2,3,6,10}, {0,1,3,4,7,10}, {1,3,6,7,8,10}, {0,1,3,9,10}, {1,3,4,6,9,10}, {1,2,3,4,7,9,10}, {0,2,4,5,8,9,10}, {0,2,4,5,6,8,9,10}, {1,3,7,8,9,10}, {4,11}, {0,3,4,6,11}, {2,3,7,11}, {6,7,8,11}, {2,3,4,9,11}, {4,6,9,11}, {0,3,7,9,11}, {1,5,8,9,11}, {1,5,6,8,9,11}, {7,8,9,11}, {0,1,3,4,5,10,11}, {0,1,3,4,5,6,10,11}, {0,2,7,10,11}, {6,7,8,10,11}, {0,2,4,9,10,11}, {4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 281. `[[39,6,3]]` — T0·T5·CS01·CS02·CS03·CS04·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034

- gate `0+5+01+02+03+04+012+013+014+023+024+034`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {1,2,5,7}, {1,3,4,6,7,8}, {2,3,4,9}, {5,6,9}, {2,5,7,9}, {2,5,8,9}, {2,5,6,8,9}, {1,3,4,7,8,9}, {5,10}, {1,4,6,10}, {1,3,5,7,10}, {1,3,4,6,7,8,10}, {4,9,10}, {5,6,9,10}, {3,5,7,9,10}, {0,3,5,8,9,10}, {0,3,5,6,8,9,10}, {1,3,4,7,8,9,10}, {1,3,4,5,11}, {1,2,4,5,6,11}, {1,2,3,7,11}, {6,7,8,11}, {2,4,5,9,11}, {1,3,4,5,6,9,11}, {2,3,7,9,11}, {0,2,3,8,9,11}, {0,2,3,6,8,9,11}, {7,8,9,11}, {0,1,3,4,5,10,11}, {0,1,3,4,5,6,10,11}, {1,7,10,11}, {6,7,8,10,11}, {3,4,5,9,10,11}, {1,3,4,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 282. `[[39,6,3]]` — T0·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS15·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134

- gate `0+5+01+02+03+04+12+13+14+15+012+013+014+023+024+034+123+124+134`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {0,2,4,7}, {0,1,2,3,5,6,7,8}, {1,2,5,9}, {2,3,4,6,9}, {0,4,7,9}, {0,4,8,9}, {0,4,6,8,9}, {0,1,2,3,5,7,8,9}, {2,3,4,10}, {0,1,3,4,5,6,10}, {2,3,7,10}, {0,1,2,3,5,6,7,8,10}, {0,1,2,3,4,5,9,10}, {2,3,4,6,9,10}, {3,7,9,10}, {0,2,4,5,8,9,10}, {0,2,4,5,6,8,9,10}, {0,1,2,3,5,7,8,9,10}, {0,1,4,5,11}, {1,3,5,6,11}, {0,2,3,4,7,11}, {6,7,8,11}, {1,2,3,5,9,11}, {0,1,4,5,6,9,11}, {0,3,4,7,9,11}, {2,5,8,9,11}, {2,5,6,8,9,11}, {7,8,9,11}, {1,2,3,10,11}, {1,2,3,6,10,11}, {2,7,10,11}, {6,7,8,10,11}, {0,1,2,4,5,9,10,11}, {0,1,4,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 283. `[[39,6,3]]` — T0·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS25·CS35·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ235·CCZ245·CCZ345

- gate `0+5+01+02+03+04+12+13+14+25+35+45+012+013+014+023+024+034+123+124+134+235+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {1,3,7}, {1,2,5,6,7,8}, {4,9}, {2,3,4,5,6,9}, {3,4,7,9}, {3,4,8,9}, {3,4,6,8,9}, {1,2,5,7,8,9}, {2,3,4,5,10}, {1,2,3,6,10}, {1,2,7,10}, {1,2,5,6,7,8,10}, {2,3,4,9,10}, {2,3,4,5,6,9,10}, {2,4,7,9,10}, {0,3,8,9,10}, {0,3,6,8,9,10}, {1,2,5,7,8,9,10}, {1,3,4,11}, {1,2,4,6,11}, {1,2,3,4,7,11}, {6,7,8,11}, {2,9,11}, {1,3,4,6,9,11}, {2,3,7,9,11}, {0,4,8,9,11}, {0,4,6,8,9,11}, {7,8,9,11}, {0,1,2,10,11}, {0,1,2,6,10,11}, {1,4,7,10,11}, {6,7,8,10,11}, {3,9,10,11}, {1,3,4,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 284. `[[39,6,3]]` — T0·T5·CS01·CS02·CS03·CS04·CS12·CS13·CS15·CS24·CS34·CS45·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ145·CCZ234

- gate `0+5+01+02+03+04+12+13+15+24+34+45+012+013+014+023+024+034+123+124+134+145+234`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,4,6}, {1,7}, {1,3,4,5,6,7,8}, {2,4,5,9}, {2,3,6,9}, {2,7,9}, {2,8,9}, {2,6,8,9}, {1,3,4,5,7,8,9}, {2,3,10}, {0,1,3,4,5,6,10}, {0,1,3,7,10}, {1,3,4,5,6,7,8,10}, {0,2,3,4,5,9,10}, {2,3,6,9,10}, {0,2,3,7,9,10}, {5,8,9,10}, {5,6,8,9,10}, {1,3,4,5,7,8,9,10}, {1,2,4,5,11}, {0,1,2,3,4,5,6,11}, {0,1,2,3,7,11}, {6,7,8,11}, {0,3,4,5,9,11}, {1,2,4,5,6,9,11}, {0,3,7,9,11}, {2,5,8,9,11}, {2,5,6,8,9,11}, {7,8,9,11}, {0,1,3,4,10,11}, {0,1,3,4,6,10,11}, {1,2,7,10,11}, {6,7,8,10,11}, {4,5,9,10,11}, {1,2,4,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 285. `[[39,6,3]]` — T0·T5·CS01·CS02·CS03·CS12·CS13·CS14·CS15·CS24·CS34·CS45·CCZ012·CCZ013·CCZ023·CCZ123·CCZ145·CCZ234

- gate `0+5+01+02+03+12+13+14+15+24+34+45+012+013+023+123+145+234`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,6}, {0,2,3,5,7}, {0,1,4,5,6,7,8}, {2,3,5,9}, {1,4,5,6,9}, {0,2,3,4,7,9}, {0,2,3,4,8,9}, {0,2,3,4,6,8,9}, {0,1,4,5,7,8,9}, {1,4,5,10}, {0,1,3,5,6,10}, {1,3,4,7,10}, {0,1,4,5,6,7,8,10}, {0,1,3,4,9,10}, {1,4,5,6,9,10}, {1,3,5,7,9,10}, {0,3,4,5,8,9,10}, {0,3,4,5,6,8,9,10}, {0,1,4,5,7,8,9,10}, {0,11}, {1,2,4,5,6,11}, {0,1,2,7,11}, {6,7,8,11}, {1,2,9,11}, {0,6,9,11}, {0,1,2,4,5,7,9,11}, {2,5,8,9,11}, {2,5,6,8,9,11}, {7,8,9,11}, {1,4,10,11}, {1,4,6,10,11}, {4,5,7,10,11}, {6,7,8,10,11}, {0,4,5,9,10,11}, {0,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 286. `[[39,6,3]]` — T0·T5·CS01·CS02·CS03·CS12·CS13·CS14·CS24·CS25·CS34·CS35·CS45·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234·CCZ235·CCZ245·CCZ345

- gate `0+5+01+02+03+12+13+14+24+25+34+35+45+012+013+023+123+234+235+245+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{1,4,6}, {0,1,2,7}, {3,4,5,6,7,8}, {4,5,9}, {0,1,2,3,6,9}, {0,1,3,7,9}, {0,1,3,8,9}, {0,1,3,6,8,9}, {3,4,5,7,8,9}, {0,1,2,3,10}, {5,6,10}, {0,1,3,4,7,10}, {3,4,5,6,7,8,10}, {2,3,5,9,10}, {0,1,2,3,6,9,10}, {0,1,2,4,7,9,10}, {0,3,4,5,8,9,10}, {0,3,4,5,6,8,9,10}, {3,4,5,7,8,9,10}, {0,1,2,4,5,11}, {0,1,3,5,6,11}, {4,7,11}, {6,7,8,11}, {0,1,2,5,9,11}, {0,1,2,4,5,6,9,11}, {2,3,4,7,9,11}, {1,4,5,8,9,11}, {1,4,5,6,8,9,11}, {7,8,9,11}, {0,3,4,10,11}, {0,3,4,6,10,11}, {2,3,7,10,11}, {6,7,8,10,11}, {0,1,3,4,5,9,10,11}, {0,1,2,4,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 287. `[[39,6,3]]` — T0·T5·CS01·CS02·CS03·CS14·CS24·CS34·CS45·CCZ012·CCZ013·CCZ023·CCZ124·CCZ134·CCZ234

- gate `0+5+01+02+03+14+24+34+45+012+013+023+124+134+234`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,3,6}, {3,4,7}, {2,4,5,6,7,8}, {1,4,5,9}, {1,2,3,4,6,9}, {1,3,4,7,9}, {1,3,4,8,9}, {1,3,4,6,8,9}, {2,4,5,7,8,9}, {1,2,3,4,10}, {0,2,4,5,6,10}, {0,2,3,4,7,10}, {2,4,5,6,7,8,10}, {0,1,2,4,5,9,10}, {1,2,3,4,6,9,10}, {0,1,2,3,4,7,9,10}, {5,8,9,10}, {5,6,8,9,10}, {2,4,5,7,8,9,10}, {1,3,5,11}, {0,1,2,3,5,6,11}, {0,1,2,7,11}, {6,7,8,11}, {0,2,3,5,9,11}, {1,3,5,6,9,11}, {0,2,7,9,11}, {1,3,4,5,8,9,11}, {1,3,4,5,6,8,9,11}, {7,8,9,11}, {0,2,4,10,11}, {0,2,4,6,10,11}, {1,7,10,11}, {6,7,8,10,11}, {3,5,9,10,11}, {1,3,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 288. `[[39,6,3]]` — T0·T5·CS01·CS02·CS13·CS14·CS23·CS24·CS35·CS45·CCZ012·CCZ123·CCZ124·CCZ134·CCZ234·CCZ345

- gate `0+5+01+02+13+14+23+24+35+45+012+123+124+134+234+345`, `N = 12` (6 outputs + 6 checks), T-count 3, reduced degree 1, a3 = 151
- source: length40_m6_001, origin 8; rep_length40_m6_001.json

```text
[{0,1,2,6}, {1,2,3,7}, {1,3,5,6,7,8}, {1,3,4,5,9}, {1,2,3,4,6,9}, {2,3,7,9}, {2,3,8,9}, {2,3,6,8,9}, {1,3,5,7,8,9}, {1,2,3,4,10}, {0,1,3,4,5,6,10}, {0,2,3,7,10}, {1,3,5,6,7,8,10}, {0,3,4,5,9,10}, {1,2,3,4,6,9,10}, {0,1,2,3,7,9,10}, {4,5,8,9,10}, {4,5,6,8,9,10}, {1,3,5,7,8,9,10}, {2,4,5,11}, {0,1,2,4,5,6,11}, {0,7,11}, {6,7,8,11}, {0,2,4,5,9,11}, {2,4,5,6,9,11}, {0,1,7,9,11}, {2,3,4,5,8,9,11}, {2,3,4,5,6,8,9,11}, {7,8,9,11}, {0,1,3,10,11}, {0,1,3,6,10,11}, {1,7,10,11}, {6,7,8,10,11}, {1,2,4,5,9,10,11}, {2,4,5,6,9,10,11}, {7,9,10,11}, {8,9,10,11}, {6,8,9,10,11}, {7,8,9,10,11}]
```

### 289. `[[40,1,3]]` — T0

- gate `0`, `N = 10` (1 outputs + 9 checks), T-count 1, reduced degree 1, a3 = 16
- source: length40_m9_discovery_026, origin 483; rep_length40_m9_discovery_026.json

```text
[{0,1,3,4}, {0,4,6}, {1,4,6}, {0,3,4,6}, {0,7}, {0,1,7}, {3,4,7}, {0,3,6,7}, {1,3,6,7}, {0,3,4,6,7}, {0,8}, {0,1,3,8}, {4,8}, {1,6,8}, {0,3,6,8}, {0,4,6,8}, {0,7,8}, {3,7,8}, {0,1,4,7,8}, {0,2,6,7,8}, {0,2,3,6,7,8}, {0,2,4,6,7,8}, {1,3,4,6,7,8}, {0,2,3,4,6,7,8}, {5,6,7,8}, {2,5,6,7,8}, {3,5,6,7,8}, {2,3,5,6,7,8}, {4,5,6,7,8}, {2,4,5,6,7,8}, {3,4,5,6,7,8}, {2,3,4,5,6,7,8}, {1,2,9}, {1,2,6,9}, {1,2,7,9}, {1,2,6,7,9}, {1,2,8,9}, {1,2,6,8,9}, {1,2,7,8,9}, {1,2,6,7,8,9}]
```

Best witness at each other check rank:

- rank 7 (`N = 8`), a3 = 30; length40_m7_002, origin 4; rep_length40_m7_002.json

  ```text
  [{0,1}, {2}, {1,2}, {1,3}, {0,2,3}, {0,1,2,3}, {0,4}, {0,3,4}, {0,5}, {0,3,5}, {4,5}, {3,4,5}, {1,7}, {0,2,7}, {0,1,2,7}, {1,3,7}, {0,2,3,7}, {0,1,2,3,7}, {0,4,7}, {0,3,4,7}, {0,5,7}, {0,3,5,7}, {4,5,7}, {3,4,5,7}, {0,3,6,7}, {0,1,3,6,7}, {0,2,3,6,7}, {0,1,2,3,6,7}, {3,4,6,7}, {1,3,4,6,7}, {2,3,4,6,7}, {1,2,3,4,6,7}, {3,5,6,7}, {1,3,5,6,7}, {2,3,5,6,7}, {1,2,3,5,6,7}, {3,4,5,6,7}, {1,3,4,5,6,7}, {2,3,4,5,6,7}, {1,2,3,4,5,6,7}]
  ```

- rank 8 (`N = 9`), a3 = 20; length40_m8_discovery_032, origin 158; rep_length40_m8_discovery_032.json

  ```text
  [{0,2,3}, {0,1,2,3}, {0,1,2,3,4}, {2,3,4,5}, {0,3,6}, {1,3,6}, {4,6}, {0,2,4,6}, {1,3,4,6}, {0,1,5,6}, {0,1,2,5,6}, {0,1,3,5,6}, {0,1,2,3,5,6}, {2,3,4,5,6}, {0,1,7}, {0,2,7}, {0,3,7}, {2,3,7}, {0,1,4,7}, {2,4,7}, {3,4,7}, {2,3,4,5,7}, {0,2,6,7}, {1,2,6,7}, {4,6,7}, {1,2,4,6,7}, {0,3,4,6,7}, {1,4,5,6,7}, {1,2,4,5,6,7}, {1,3,4,5,6,7}, {2,3,4,5,6,7}, {1,2,3,4,5,6,7}, {2,3,4,8}, {2,3,4,5,8}, {2,3,4,6,8}, {2,3,4,5,6,8}, {2,3,4,7,8}, {2,3,4,5,7,8}, {2,3,4,6,7,8}, {2,3,4,5,6,7,8}]
  ```

- rank 10 (`N = 11`), a3 = 16; length40_m10_class_0001, origin 640; rep_length40_m10_class_0001.json

  ```text
  [{0,1}, {0,2}, {0,1,2}, {7}, {8}, {0,1,8}, {0,2,8}, {0,1,2,8}, {0,3,8}, {0,4,8}, {0,3,4,8}, {0,5,8}, {0,3,5,8}, {0,4,5,8}, {0,3,4,5,8}, {6,8}, {3,6,8}, {4,6,8}, {3,4,6,8}, {5,6,8}, {3,5,6,8}, {4,5,6,8}, {3,4,5,6,8}, {7,8}, {1,9}, {2,9}, {1,2,9}, {7,9}, {1,8,9}, {2,8,9}, {1,2,8,9}, {7,8,9}, {10}, {7,10}, {8,10}, {7,8,10}, {9,10}, {7,9,10}, {8,9,10}, {7,8,9,10}]
  ```

### 290. `[[40,2,3]]` — T0·CS01

- gate `0+01`, `N = 11` (2 outputs + 9 checks), T-count 2, reduced degree 1, a3 = 32
- source: length40_m9_discovery_026, origin 483; rep_length40_m9_discovery_026.json

```text
[{0,2,4,5}, {0,1,5,7}, {2,5,7}, {0,1,4,5,7}, {0,1,8}, {0,2,8}, {1,4,5,8}, {0,1,4,7,8}, {2,4,7,8}, {0,1,4,5,7,8}, {0,1,9}, {0,2,4,9}, {1,5,9}, {2,7,9}, {0,1,4,7,9}, {0,1,5,7,9}, {0,1,8,9}, {1,4,8,9}, {0,2,5,8,9}, {0,1,3,7,8,9}, {0,1,3,4,7,8,9}, {0,1,3,5,7,8,9}, {2,4,5,7,8,9}, {0,1,3,4,5,7,8,9}, {6,7,8,9}, {3,6,7,8,9}, {4,6,7,8,9}, {3,4,6,7,8,9}, {5,6,7,8,9}, {3,5,6,7,8,9}, {4,5,6,7,8,9}, {3,4,5,6,7,8,9}, {2,3,10}, {2,3,7,10}, {2,3,8,10}, {2,3,7,8,10}, {2,3,9,10}, {2,3,7,9,10}, {2,3,8,9,10}, {2,3,7,8,9,10}]
```

Best witness at each other check rank:

- rank 7 (`N = 9`), a3 = 52; length40_m7_010, origin 38; rep_length40_m7_010.json

  ```text
  [{1,3,4}, {0,1,3,4,5}, {0,1,3,4,6}, {0,1,3,4,5,6}, {0,1,7}, {0,1,2,7}, {0,3,7}, {2,3,7}, {0,4,7}, {2,4,7}, {0,1,2,3,4,7}, {0,1,3,4,5,7}, {0,1,3,4,6,7}, {0,1,3,4,5,6,7}, {8}, {0,1,3,8}, {1,2,3,8}, {0,1,4,8}, {1,2,4,8}, {3,4,8}, {2,3,4,8}, {5,8}, {3,4,5,8}, {2,3,4,5,8}, {0,2,3,6,8}, {0,2,4,6,8}, {2,3,4,6,8}, {0,3,5,6,8}, {0,4,5,6,8}, {2,3,4,5,6,8}, {2,7,8}, {0,5,7,8}, {0,3,4,5,7,8}, {2,3,4,5,7,8}, {2,3,6,7,8}, {2,4,6,7,8}, {2,3,4,6,7,8}, {3,5,6,7,8}, {4,5,6,7,8}, {2,3,4,5,6,7,8}]
  ```

- rank 8 (`N = 10`), a3 = 36; length40_m8_discovery_032, origin 158; rep_length40_m8_discovery_032.json

  ```text
  [{1,3,4}, {0,2,3,4}, {1,2,3,4,5}, {3,4,5,6}, {1,4,7}, {2,4,7}, {5,7}, {0,3,5,7}, {0,1,2,4,5,7}, {1,2,6,7}, {1,2,3,6,7}, {1,2,4,6,7}, {1,2,3,4,6,7}, {3,4,5,6,7}, {0,2,8}, {1,3,8}, {1,4,8}, {0,1,3,4,8}, {1,2,5,8}, {3,5,8}, {4,5,8}, {3,4,5,6,8}, {1,3,7,8}, {2,3,7,8}, {5,7,8}, {0,1,2,3,5,7,8}, {0,4,5,7,8}, {2,5,6,7,8}, {2,3,5,6,7,8}, {2,4,5,6,7,8}, {3,4,5,6,7,8}, {2,3,4,5,6,7,8}, {3,4,5,9}, {3,4,5,6,9}, {3,4,5,7,9}, {3,4,5,6,7,9}, {3,4,5,8,9}, {3,4,5,6,8,9}, {3,4,5,7,8,9}, {3,4,5,6,7,8,9}]
  ```

- rank 10 (`N = 12`), a3 = 44; length40_m10_class_0001, origin 640; rep_length40_m10_class_0001.json

  ```text
  [{1,2}, {0,3}, {0,2,3}, {0,1,8}, {0,1,9}, {1,2,9}, {0,3,9}, {0,2,3,9}, {1,4,9}, {1,5,9}, {1,4,5,9}, {1,6,9}, {1,4,6,9}, {1,5,6,9}, {1,4,5,6,9}, {7,9}, {4,7,9}, {5,7,9}, {4,5,7,9}, {6,7,9}, {4,6,7,9}, {5,6,7,9}, {4,5,6,7,9}, {0,1,8,9}, {0,1,2,10}, {3,10}, {2,3,10}, {0,1,8,10}, {0,1,2,9,10}, {3,9,10}, {2,3,9,10}, {0,1,8,9,10}, {11}, {8,11}, {9,11}, {8,9,11}, {10,11}, {8,10,11}, {9,10,11}, {8,9,10,11}]
  ```

### 291. `[[40,2,3]]` — T0·T1

- gate `0+1`, `N = 11` (2 outputs + 9 checks), T-count 2, reduced degree 1, a3 = 32
- source: length40_m9_discovery_026, origin 483; rep_length40_m9_discovery_026.json

```text
[{0,1,2,4,5}, {0,5,7}, {2,5,7}, {0,4,5,7}, {0,8}, {0,1,2,8}, {1,4,5,8}, {0,4,7,8}, {2,4,7,8}, {0,4,5,7,8}, {0,9}, {0,1,2,4,9}, {1,5,9}, {2,7,9}, {0,4,7,9}, {0,5,7,9}, {0,8,9}, {1,4,8,9}, {0,1,2,5,8,9}, {0,3,7,8,9}, {0,3,4,7,8,9}, {0,3,5,7,8,9}, {2,4,5,7,8,9}, {0,3,4,5,7,8,9}, {6,7,8,9}, {3,6,7,8,9}, {4,6,7,8,9}, {3,4,6,7,8,9}, {5,6,7,8,9}, {3,5,6,7,8,9}, {4,5,6,7,8,9}, {3,4,5,6,7,8,9}, {2,3,10}, {2,3,7,10}, {2,3,8,10}, {2,3,7,8,10}, {2,3,9,10}, {2,3,7,9,10}, {2,3,8,9,10}, {2,3,7,8,9,10}]
```

Best witness at each other check rank:

- rank 7 (`N = 9`), a3 = 52; length40_m7_010, origin 38; rep_length40_m7_010.json

  ```text
  [{1,3,4}, {0,3,4,5}, {0,3,4,6}, {0,3,4,5,6}, {0,7}, {0,2,7}, {0,1,3,7}, {2,3,7}, {0,1,4,7}, {2,4,7}, {0,2,3,4,7}, {0,3,4,5,7}, {0,3,4,6,7}, {0,3,4,5,6,7}, {8}, {0,3,8}, {1,2,3,8}, {0,4,8}, {1,2,4,8}, {3,4,8}, {2,3,4,8}, {5,8}, {3,4,5,8}, {2,3,4,5,8}, {0,1,2,3,6,8}, {0,1,2,4,6,8}, {2,3,4,6,8}, {0,1,3,5,6,8}, {0,1,4,5,6,8}, {2,3,4,5,6,8}, {2,7,8}, {0,1,5,7,8}, {0,1,3,4,5,7,8}, {2,3,4,5,7,8}, {2,3,6,7,8}, {2,4,6,7,8}, {2,3,4,6,7,8}, {3,5,6,7,8}, {4,5,6,7,8}, {2,3,4,5,6,7,8}]
  ```

- rank 8 (`N = 10`), a3 = 36; length40_m8_discovery_032, origin 158; rep_length40_m8_discovery_032.json

  ```text
  [{1,3,4}, {0,1,2,3,4}, {1,2,3,4,5}, {3,4,5,6}, {1,4,7}, {2,4,7}, {5,7}, {0,1,3,5,7}, {0,2,4,5,7}, {1,2,6,7}, {1,2,3,6,7}, {1,2,4,6,7}, {1,2,3,4,6,7}, {3,4,5,6,7}, {0,1,2,8}, {1,3,8}, {1,4,8}, {0,3,4,8}, {1,2,5,8}, {3,5,8}, {4,5,8}, {3,4,5,6,8}, {1,3,7,8}, {2,3,7,8}, {5,7,8}, {0,2,3,5,7,8}, {0,1,4,5,7,8}, {2,5,6,7,8}, {2,3,5,6,7,8}, {2,4,5,6,7,8}, {3,4,5,6,7,8}, {2,3,4,5,6,7,8}, {3,4,5,9}, {3,4,5,6,9}, {3,4,5,7,9}, {3,4,5,6,7,9}, {3,4,5,8,9}, {3,4,5,6,8,9}, {3,4,5,7,8,9}, {3,4,5,6,7,8,9}]
  ```

- rank 10 (`N = 12`), a3 = 44; length40_m10_class_0001, origin 640; rep_length40_m10_class_0001.json

  ```text
  [{1,2}, {0,1,3}, {0,1,2,3}, {0,8}, {0,9}, {1,2,9}, {0,1,3,9}, {0,1,2,3,9}, {1,4,9}, {1,5,9}, {1,4,5,9}, {1,6,9}, {1,4,6,9}, {1,5,6,9}, {1,4,5,6,9}, {7,9}, {4,7,9}, {5,7,9}, {4,5,7,9}, {6,7,9}, {4,6,7,9}, {5,6,7,9}, {4,5,6,7,9}, {0,8,9}, {0,2,10}, {3,10}, {2,3,10}, {0,8,10}, {0,2,9,10}, {3,9,10}, {2,3,9,10}, {0,8,9,10}, {11}, {8,11}, {9,11}, {8,9,11}, {10,11}, {8,10,11}, {9,10,11}, {8,9,10,11}]
  ```

### 292. `[[40,2,3]]` — T0·T1·CS01

- gate `0+1+01`, `N = 11` (2 outputs + 9 checks), T-count 1, reduced degree 1, a3 = 20
- source: length40_m9_discovery_003, origin 387; rep_length40_m9_discovery_003.json

```text
[{0,1,2,3,4}, {0,1,7}, {2,7}, {0,1,3,4,7}, {0,1,8}, {0,1,2,8}, {3,4,8}, {2,3,4,7,8}, {9}, {0,1,3,9}, {0,4,9}, {0,3,4,9}, {0,1,2,3,4,9}, {0,1,5,9}, {0,1,3,5,9}, {0,4,5,9}, {0,3,4,5,9}, {1,6,9}, {1,3,6,9}, {4,6,9}, {3,4,6,9}, {1,5,6,9}, {1,3,5,6,9}, {4,5,6,9}, {3,4,5,6,9}, {0,1,7,9}, {2,7,9}, {0,1,3,4,7,9}, {0,1,8,9}, {0,1,2,8,9}, {3,4,8,9}, {2,3,4,7,8,9}, {2,3,10}, {2,3,7,10}, {2,3,8,10}, {2,3,7,8,10}, {2,3,9,10}, {2,3,7,9,10}, {2,3,8,9,10}, {2,3,7,8,9,10}]
```

Best witness at each other check rank:

- rank 7 (`N = 9`), a3 = 38; length40_m7_002, origin 4; rep_length40_m7_002.json

  ```text
  [{0,1,2}, {3}, {2,3}, {2,4}, {0,1,3,4}, {0,1,2,3,4}, {1,5}, {1,4,5}, {0,1,6}, {0,1,4,6}, {0,5,6}, {0,4,5,6}, {0,2,8}, {1,3,8}, {1,2,3,8}, {0,2,4,8}, {1,3,4,8}, {1,2,3,4,8}, {0,1,5,8}, {0,1,4,5,8}, {1,6,8}, {1,4,6,8}, {5,6,8}, {4,5,6,8}, {0,1,4,7,8}, {0,1,2,4,7,8}, {0,1,3,4,7,8}, {0,1,2,3,4,7,8}, {4,5,7,8}, {2,4,5,7,8}, {3,4,5,7,8}, {2,3,4,5,7,8}, {4,6,7,8}, {2,4,6,7,8}, {3,4,6,7,8}, {2,3,4,6,7,8}, {4,5,6,7,8}, {2,4,5,6,7,8}, {3,4,5,6,7,8}, {2,3,4,5,6,7,8}]
  ```

- rank 8 (`N = 10`), a3 = 24; length40_m8_discovery_032, origin 158; rep_length40_m8_discovery_032.json

  ```text
  [{0,1,3,4}, {1,2,3,4}, {1,2,3,4,5}, {3,4,5,6}, {0,1,4,7}, {0,2,4,7}, {5,7}, {0,1,3,5,7}, {0,2,4,5,7}, {0,1,2,6,7}, {0,1,2,3,6,7}, {0,1,2,4,6,7}, {0,1,2,3,4,6,7}, {3,4,5,6,7}, {1,2,8}, {0,1,3,8}, {0,1,4,8}, {3,4,8}, {1,2,5,8}, {3,5,8}, {4,5,8}, {3,4,5,6,8}, {0,1,3,7,8}, {0,2,3,7,8}, {5,7,8}, {0,2,3,5,7,8}, {0,1,4,5,7,8}, {2,5,6,7,8}, {2,3,5,6,7,8}, {2,4,5,6,7,8}, {3,4,5,6,7,8}, {2,3,4,5,6,7,8}, {3,4,5,9}, {3,4,5,6,9}, {3,4,5,7,9}, {3,4,5,6,7,9}, {3,4,5,8,9}, {3,4,5,6,8,9}, {3,4,5,7,8,9}, {3,4,5,6,7,8,9}]
  ```

### 293. `[[40,2,3]]` — CS01

- gate `01`, `N = 9` (2 outputs + 7 checks), T-count 3, reduced degree 2, a3 = 72
- source: length40_m7_015, origin 75; rep_length40_m7_015.json

```text
[{1,2}, {1,3}, {0,1,2,3}, {2,4}, {0,3,4}, {1,2,3,4}, {2,5}, {1,3,5}, {0,2,3,5}, {0,1,4,5}, {0,2,6}, {0,1,3,6}, {0,2,3,6}, {0,1,2,4,6}, {3,4,6}, {2,3,4,6}, {0,1,5,6}, {2,4,5,6}, {1,3,4,5,6}, {0,2,3,4,5,6}, {0,1,5,7}, {1,2,5,7}, {0,3,5,7}, {2,3,5,7}, {0,1,5,6,7}, {1,2,5,6,7}, {0,3,5,6,7}, {2,3,5,6,7}, {2,3,8}, {2,3,4,8}, {5,8}, {2,5,8}, {3,5,8}, {4,5,8}, {2,4,5,8}, {3,4,5,8}, {2,3,6,8}, {2,3,4,6,8}, {2,3,5,6,8}, {2,3,4,5,6,8}]
```

Best witness at each other check rank:

- rank 6 (`N = 8`), a3 = 120; length40_m6_001, origin 3; rep_length40_m6_001.json

  ```text
  [{1,2}, {0,3}, {2,3}, {2,4}, {0,1,3,4}, {2,3,4}, {1,2,5}, {3,5}, {0,1,2,3,5}, {0,4,5}, {0,2,6}, {3,6}, {1,2,3,6}, {2,4,6}, {0,1,3,4,6}, {2,3,4,6}, {0,2,5,6}, {0,3,5,6}, {0,2,3,5,6}, {0,4,5,6}, {0,2,7}, {0,1,3,7}, {2,3,7}, {0,1,2,4,7}, {0,3,4,7}, {2,3,4,7}, {0,1,2,5,7}, {0,3,5,7}, {1,2,3,5,7}, {4,5,7}, {1,2,6,7}, {1,3,6,7}, {1,2,3,6,7}, {0,1,2,4,6,7}, {0,3,4,6,7}, {2,3,4,6,7}, {2,5,6,7}, {3,5,6,7}, {2,3,5,6,7}, {4,5,6,7}]
  ```

### 294. `[[40,3,3]]` — T0·CS01·CS02·CCZ012

- gate `0+01+02+012`, `N = 11` (3 outputs + 8 checks), T-count 2, reduced degree 1, a3 = 40
- source: length40_m8_discovery_032, origin 158; rep_length40_m8_discovery_032.json

```text
[{1,2,4,5}, {0,1,3,4,5}, {2,3,4,5,6}, {4,5,6,7}, {1,2,5,8}, {1,3,5,8}, {6,8}, {0,4,6,8}, {0,2,3,5,6,8}, {1,2,3,7,8}, {1,2,3,4,7,8}, {1,2,3,5,7,8}, {1,2,3,4,5,7,8}, {4,5,6,7,8}, {0,1,3,9}, {1,2,4,9}, {1,2,5,9}, {0,1,2,4,5,9}, {2,3,6,9}, {4,6,9}, {5,6,9}, {4,5,6,7,9}, {1,2,4,8,9}, {1,3,4,8,9}, {6,8,9}, {0,2,3,4,6,8,9}, {0,5,6,8,9}, {3,6,7,8,9}, {3,4,6,7,8,9}, {3,5,6,7,8,9}, {4,5,6,7,8,9}, {3,4,5,6,7,8,9}, {4,5,6,10}, {4,5,6,7,10}, {4,5,6,8,10}, {4,5,6,7,8,10}, {4,5,6,9,10}, {4,5,6,7,9,10}, {4,5,6,8,9,10}, {4,5,6,7,8,9,10}]
```

Best witness at each other check rank:

- rank 7 (`N = 10`), a3 = 56; length40_m7_010, origin 38; rep_length40_m7_010.json

  ```text
  [{1,2,4,5}, {0,1,2,4,5,6}, {0,1,2,4,5,7}, {0,1,2,4,5,6,7}, {0,1,2,8}, {0,2,3,8}, {0,1,4,8}, {3,4,8}, {0,1,5,8}, {3,5,8}, {0,2,3,4,5,8}, {0,1,2,4,5,6,8}, {0,1,2,4,5,7,8}, {0,1,2,4,5,6,7,8}, {1,9}, {0,1,2,4,9}, {2,3,4,9}, {0,1,2,5,9}, {2,3,5,9}, {1,4,5,9}, {3,4,5,9}, {6,9}, {4,5,6,9}, {3,4,5,6,9}, {0,3,4,7,9}, {0,3,5,7,9}, {3,4,5,7,9}, {0,4,6,7,9}, {0,5,6,7,9}, {3,4,5,6,7,9}, {3,8,9}, {0,6,8,9}, {0,4,5,6,8,9}, {3,4,5,6,8,9}, {3,4,7,8,9}, {3,5,7,8,9}, {3,4,5,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}, {3,4,5,6,7,8,9}]
  ```

- rank 9 (`N = 12`), a3 = 48; length40_m9_discovery_003, origin 387; rep_length40_m9_discovery_003.json

  ```text
  [{0,3,4,5}, {0,1,2,8}, {1,2,3,8}, {0,4,5,8}, {0,1,2,9}, {0,1,2,3,9}, {4,5,9}, {3,4,5,8,9}, {1,2,10}, {0,1,2,4,10}, {1,5,10}, {1,4,5,10}, {0,3,4,5,10}, {0,1,2,6,10}, {0,1,2,4,6,10}, {1,5,6,10}, {1,4,5,6,10}, {0,2,7,10}, {0,2,4,7,10}, {5,7,10}, {4,5,7,10}, {0,2,6,7,10}, {0,2,4,6,7,10}, {5,6,7,10}, {4,5,6,7,10}, {0,1,2,8,10}, {1,2,3,8,10}, {0,4,5,8,10}, {0,1,2,9,10}, {0,1,2,3,9,10}, {4,5,9,10}, {3,4,5,8,9,10}, {3,4,11}, {3,4,8,11}, {3,4,9,11}, {3,4,8,9,11}, {3,4,10,11}, {3,4,8,10,11}, {3,4,9,10,11}, {3,4,8,9,10,11}]
  ```

### 295. `[[40,3,3]]` — T0·T1·CS01·CS02·CS12·CCZ012

- gate `0+1+01+02+12+012`, `N = 11` (3 outputs + 8 checks), T-count 2, reduced degree 1, a3 = 40
- source: length40_m8_discovery_032, origin 158; rep_length40_m8_discovery_032.json

```text
[{0,1,2,4,5}, {1,2,3,4,5}, {1,3,4,5,6}, {4,5,6,7}, {0,1,2,5,8}, {0,2,3,5,8}, {6,8}, {0,1,4,6,8}, {0,3,5,6,8}, {0,1,2,3,7,8}, {0,1,2,3,4,7,8}, {0,1,2,3,5,7,8}, {0,1,2,3,4,5,7,8}, {4,5,6,7,8}, {1,2,3,9}, {0,1,2,4,9}, {0,1,2,5,9}, {2,4,5,9}, {1,3,6,9}, {4,6,9}, {5,6,9}, {4,5,6,7,9}, {0,1,2,4,8,9}, {0,2,3,4,8,9}, {6,8,9}, {0,3,4,6,8,9}, {0,1,5,6,8,9}, {3,6,7,8,9}, {3,4,6,7,8,9}, {3,5,6,7,8,9}, {4,5,6,7,8,9}, {3,4,5,6,7,8,9}, {4,5,6,10}, {4,5,6,7,10}, {4,5,6,8,10}, {4,5,6,7,8,10}, {4,5,6,9,10}, {4,5,6,7,9,10}, {4,5,6,8,9,10}, {4,5,6,7,8,9,10}]
```

Best witness at each other check rank:

- rank 7 (`N = 10`), a3 = 56; length40_m7_010, origin 38; rep_length40_m7_010.json

  ```text
  [{0,1,2,4,5}, {2,4,5,6}, {2,4,5,7}, {2,4,5,6,7}, {2,8}, {0,3,8}, {1,2,4,8}, {3,4,8}, {1,2,5,8}, {3,5,8}, {0,3,4,5,8}, {2,4,5,6,8}, {2,4,5,7,8}, {2,4,5,6,7,8}, {0,2,9}, {2,4,9}, {1,3,4,9}, {2,5,9}, {1,3,5,9}, {0,2,4,5,9}, {3,4,5,9}, {6,9}, {4,5,6,9}, {3,4,5,6,9}, {0,1,3,4,7,9}, {0,1,3,5,7,9}, {3,4,5,7,9}, {0,1,4,6,7,9}, {0,1,5,6,7,9}, {3,4,5,6,7,9}, {3,8,9}, {0,1,6,8,9}, {0,1,4,5,6,8,9}, {3,4,5,6,8,9}, {3,4,7,8,9}, {3,5,7,8,9}, {3,4,5,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}, {3,4,5,6,7,8,9}]
  ```

- rank 9 (`N = 12`), a3 = 48; length40_m9_discovery_003, origin 387; rep_length40_m9_discovery_003.json

  ```text
  [{0,1,3,4,5}, {0,1,2,8}, {2,3,8}, {0,1,4,5,8}, {0,1,2,9}, {0,1,2,3,9}, {4,5,9}, {3,4,5,8,9}, {2,10}, {0,1,2,4,10}, {1,2,5,10}, {1,2,4,5,10}, {0,1,3,4,5,10}, {0,1,2,6,10}, {0,1,2,4,6,10}, {1,2,5,6,10}, {1,2,4,5,6,10}, {0,7,10}, {0,4,7,10}, {5,7,10}, {4,5,7,10}, {0,6,7,10}, {0,4,6,7,10}, {5,6,7,10}, {4,5,6,7,10}, {0,1,2,8,10}, {2,3,8,10}, {0,1,4,5,8,10}, {0,1,2,9,10}, {0,1,2,3,9,10}, {4,5,9,10}, {3,4,5,8,9,10}, {3,4,11}, {3,4,8,11}, {3,4,9,11}, {3,4,8,9,11}, {3,4,10,11}, {3,4,8,10,11}, {3,4,9,10,11}, {3,4,8,9,10,11}]
  ```

### 296. `[[40,3,3]]` — T0·T1·T2·CS01

- gate `0+1+2+01`, `N = 11` (3 outputs + 8 checks), T-count 2, reduced degree 1, a3 = 40
- source: length40_m8_discovery_032, origin 158; rep_length40_m8_discovery_032.json

```text
[{0,1,4,5}, {1,2,3,4,5}, {1,3,4,5,6}, {4,5,6,7}, {0,1,5,8}, {0,3,5,8}, {6,8}, {0,1,2,4,6,8}, {0,2,3,5,6,8}, {0,1,3,7,8}, {0,1,3,4,7,8}, {0,1,3,5,7,8}, {0,1,3,4,5,7,8}, {4,5,6,7,8}, {1,2,3,9}, {0,1,4,9}, {0,1,5,9}, {2,4,5,9}, {1,3,6,9}, {4,6,9}, {5,6,9}, {4,5,6,7,9}, {0,1,4,8,9}, {0,3,4,8,9}, {6,8,9}, {0,2,3,4,6,8,9}, {0,1,2,5,6,8,9}, {3,6,7,8,9}, {3,4,6,7,8,9}, {3,5,6,7,8,9}, {4,5,6,7,8,9}, {3,4,5,6,7,8,9}, {4,5,6,10}, {4,5,6,7,10}, {4,5,6,8,10}, {4,5,6,7,8,10}, {4,5,6,9,10}, {4,5,6,7,9,10}, {4,5,6,8,9,10}, {4,5,6,7,8,9,10}]
```

Best witness at each other check rank:

- rank 7 (`N = 10`), a3 = 56; length40_m7_010, origin 38; rep_length40_m7_010.json

  ```text
  [{0,1,4,5}, {2,4,5,6}, {2,4,5,7}, {2,4,5,6,7}, {2,8}, {0,3,8}, {1,4,8}, {3,4,8}, {1,5,8}, {3,5,8}, {0,3,4,5,8}, {2,4,5,6,8}, {2,4,5,7,8}, {2,4,5,6,7,8}, {0,2,9}, {2,4,9}, {1,2,3,4,9}, {2,5,9}, {1,2,3,5,9}, {0,2,4,5,9}, {3,4,5,9}, {6,9}, {4,5,6,9}, {3,4,5,6,9}, {0,1,2,3,4,7,9}, {0,1,2,3,5,7,9}, {3,4,5,7,9}, {0,1,2,4,6,7,9}, {0,1,2,5,6,7,9}, {3,4,5,6,7,9}, {3,8,9}, {0,1,2,6,8,9}, {0,1,2,4,5,6,8,9}, {3,4,5,6,8,9}, {3,4,7,8,9}, {3,5,7,8,9}, {3,4,5,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}, {3,4,5,6,7,8,9}]
  ```

- rank 9 (`N = 12`), a3 = 48; length40_m9_discovery_003, origin 387; rep_length40_m9_discovery_003.json

  ```text
  [{0,1,2,3,4,5}, {0,1,8}, {2,3,8}, {0,1,2,4,5,8}, {0,1,9}, {0,1,3,9}, {4,5,9}, {3,4,5,8,9}, {2,10}, {0,1,4,10}, {1,2,5,10}, {1,2,4,5,10}, {0,1,2,3,4,5,10}, {0,1,6,10}, {0,1,4,6,10}, {1,2,5,6,10}, {1,2,4,5,6,10}, {0,2,7,10}, {0,2,4,7,10}, {5,7,10}, {4,5,7,10}, {0,2,6,7,10}, {0,2,4,6,7,10}, {5,6,7,10}, {4,5,6,7,10}, {0,1,8,10}, {2,3,8,10}, {0,1,2,4,5,8,10}, {0,1,9,10}, {0,1,3,9,10}, {4,5,9,10}, {3,4,5,8,9,10}, {3,4,11}, {3,4,8,11}, {3,4,9,11}, {3,4,8,9,11}, {3,4,10,11}, {3,4,8,10,11}, {3,4,9,10,11}, {3,4,8,9,10,11}]
  ```

### 297. `[[40,3,3]]` — T0·T1·T2·CS01·CS02·CS12·CCZ012

- gate `0+1+2+01+02+12+012`, `N = 11` (3 outputs + 8 checks), T-count 1, reduced degree 1, a3 = 28
- source: length40_m8_discovery_002, origin 143; rep_length40_m8_discovery_002.json

```text
[{0,1,2,4}, {1,3,4}, {0,2,5}, {0,1,2,3,5}, {4,6}, {1,3,4,6}, {0,2,5,6}, {3,5,6}, {0,1,2,3,4,5,6}, {1,2,3,7}, {2,4,7}, {0,1,3,5,7}, {0,4,5,7}, {1,2,3,6,7}, {2,4,6,7}, {0,1,3,5,6,7}, {0,4,5,6,7}, {3,4,5,6,7}, {0,1,2,3,8}, {0,1,2,3,4,8}, {0,1,2,5,8}, {0,1,2,4,5,8}, {3,6,8}, {3,4,6,8}, {5,6,8}, {4,5,6,8}, {3,4,5,6,8}, {3,4,5,6,7,8}, {3,4,5,6,9}, {3,4,5,6,7,9}, {3,4,5,6,8,9}, {3,4,5,6,7,8,9}, {3,4,5,6,10}, {3,4,5,6,7,10}, {3,4,5,6,8,10}, {3,4,5,6,7,8,10}, {3,4,5,6,9,10}, {3,4,5,6,7,9,10}, {3,4,5,6,8,9,10}, {3,4,5,6,7,8,9,10}]
```

Best witness at each other check rank:

- rank 7 (`N = 10`), a3 = 42; length40_m7_002, origin 4; rep_length40_m7_002.json

  ```text
  [{0,1,2,3}, {4}, {3,4}, {3,5}, {0,1,2,4,5}, {0,1,2,3,4,5}, {0,2,6}, {0,2,5,6}, {2,7}, {2,5,7}, {0,6,7}, {0,5,6,7}, {0,3,9}, {1,2,4,9}, {1,2,3,4,9}, {0,3,5,9}, {1,2,4,5,9}, {1,2,3,4,5,9}, {2,6,9}, {2,5,6,9}, {0,2,7,9}, {0,2,5,7,9}, {6,7,9}, {5,6,7,9}, {0,1,2,5,8,9}, {0,1,2,3,5,8,9}, {0,1,2,4,5,8,9}, {0,1,2,3,4,5,8,9}, {5,6,8,9}, {3,5,6,8,9}, {4,5,6,8,9}, {3,4,5,6,8,9}, {5,7,8,9}, {3,5,7,8,9}, {4,5,7,8,9}, {3,4,5,7,8,9}, {5,6,7,8,9}, {3,5,6,7,8,9}, {4,5,6,7,8,9}, {3,4,5,6,7,8,9}]
  ```

### 298. `[[40,3,3]]` — T0·T2·CS01·CS12

- gate `0+2+01+12`, `N = 11` (3 outputs + 8 checks), T-count 2, reduced degree 1, a3 = 40
- source: length40_m8_discovery_032, origin 158; rep_length40_m8_discovery_032.json

```text
[{1,2,4,5}, {0,1,2,3,4,5}, {2,3,4,5,6}, {4,5,6,7}, {1,2,5,8}, {1,3,5,8}, {6,8}, {0,2,4,6,8}, {0,3,5,6,8}, {1,2,3,7,8}, {1,2,3,4,7,8}, {1,2,3,5,7,8}, {1,2,3,4,5,7,8}, {4,5,6,7,8}, {0,1,2,3,9}, {1,2,4,9}, {1,2,5,9}, {0,1,4,5,9}, {2,3,6,9}, {4,6,9}, {5,6,9}, {4,5,6,7,9}, {1,2,4,8,9}, {1,3,4,8,9}, {6,8,9}, {0,3,4,6,8,9}, {0,2,5,6,8,9}, {3,6,7,8,9}, {3,4,6,7,8,9}, {3,5,6,7,8,9}, {4,5,6,7,8,9}, {3,4,5,6,7,8,9}, {4,5,6,10}, {4,5,6,7,10}, {4,5,6,8,10}, {4,5,6,7,8,10}, {4,5,6,9,10}, {4,5,6,7,9,10}, {4,5,6,8,9,10}, {4,5,6,7,8,9,10}]
```

Best witness at each other check rank:

- rank 7 (`N = 10`), a3 = 56; length40_m7_010, origin 38; rep_length40_m7_010.json

  ```text
  [{1,2,4,5}, {0,1,4,5,6}, {0,1,4,5,7}, {0,1,4,5,6,7}, {0,1,8}, {1,3,8}, {2,4,8}, {3,4,8}, {2,5,8}, {3,5,8}, {1,3,4,5,8}, {0,1,4,5,6,8}, {0,1,4,5,7,8}, {0,1,4,5,6,7,8}, {0,9}, {0,1,4,9}, {0,1,2,3,4,9}, {0,1,5,9}, {0,1,2,3,5,9}, {0,4,5,9}, {3,4,5,9}, {6,9}, {4,5,6,9}, {3,4,5,6,9}, {0,2,3,4,7,9}, {0,2,3,5,7,9}, {3,4,5,7,9}, {0,2,4,6,7,9}, {0,2,5,6,7,9}, {3,4,5,6,7,9}, {3,8,9}, {0,2,6,8,9}, {0,2,4,5,6,8,9}, {3,4,5,6,8,9}, {3,4,7,8,9}, {3,5,7,8,9}, {3,4,5,7,8,9}, {4,6,7,8,9}, {5,6,7,8,9}, {3,4,5,6,7,8,9}]
  ```

- rank 9 (`N = 12`), a3 = 48; length40_m9_discovery_003, origin 387; rep_length40_m9_discovery_003.json

  ```text
  [{0,2,3,4,5}, {0,1,8}, {1,2,3,8}, {0,2,4,5,8}, {0,1,9}, {0,1,3,9}, {4,5,9}, {3,4,5,8,9}, {1,2,10}, {0,1,4,10}, {0,1,2,5,10}, {0,1,2,4,5,10}, {0,2,3,4,5,10}, {0,1,6,10}, {0,1,4,6,10}, {0,1,2,5,6,10}, {0,1,2,4,5,6,10}, {2,7,10}, {2,4,7,10}, {5,7,10}, {4,5,7,10}, {2,6,7,10}, {2,4,6,7,10}, {5,6,7,10}, {4,5,6,7,10}, {0,1,8,10}, {1,2,3,8,10}, {0,2,4,5,8,10}, {0,1,9,10}, {0,1,3,9,10}, {4,5,9,10}, {3,4,5,8,9,10}, {3,4,11}, {3,4,8,11}, {3,4,9,11}, {3,4,8,9,11}, {3,4,10,11}, {3,4,8,10,11}, {3,4,9,10,11}, {3,4,8,9,10,11}]
  ```

### 299. `[[40,3,3]]` — CS01·CCZ012

- gate `01+012`, `N = 10` (3 outputs + 7 checks), T-count 4, reduced degree 2, a3 = 104
- source: length40_m7_015, origin 75; rep_length40_m7_015.json

```text
[{2,3}, {2,4}, {0,2,3,4}, {1,2,3,5}, {0,1,2,4,5}, {2,3,4,5}, {1,2,3,6}, {2,4,6}, {0,1,2,3,4,6}, {0,2,5,6}, {0,1,2,3,7}, {0,2,4,7}, {0,1,2,3,4,7}, {0,2,3,5,7}, {1,2,4,5,7}, {1,2,3,4,5,7}, {0,2,6,7}, {1,2,3,5,6,7}, {2,4,5,6,7}, {0,1,2,3,4,5,6,7}, {0,1,6,8}, {1,3,6,8}, {0,4,6,8}, {3,4,6,8}, {0,1,6,7,8}, {1,3,6,7,8}, {0,4,6,7,8}, {3,4,6,7,8}, {3,4,9}, {3,4,5,9}, {6,9}, {3,6,9}, {4,6,9}, {5,6,9}, {3,5,6,9}, {4,5,6,9}, {3,4,7,9}, {3,4,5,7,9}, {3,4,6,7,9}, {3,4,5,6,7,9}]
```

Best witness at each other check rank:

- rank 6 (`N = 9`), a3 = 160; length40_m6_001, origin 3; rep_length40_m6_001.json

  ```text
  [{1,2,3}, {0,2,4}, {2,3,4}, {2,3,5}, {0,1,2,4,5}, {2,3,4,5}, {1,2,3,6}, {2,4,6}, {0,1,2,3,4,6}, {0,2,5,6}, {0,2,3,7}, {2,4,7}, {1,2,3,4,7}, {2,3,5,7}, {0,1,2,4,5,7}, {2,3,4,5,7}, {0,2,3,6,7}, {0,2,4,6,7}, {0,2,3,4,6,7}, {0,2,5,6,7}, {0,3,8}, {0,1,4,8}, {3,4,8}, {0,1,3,5,8}, {0,4,5,8}, {3,4,5,8}, {0,1,3,6,8}, {0,4,6,8}, {1,3,4,6,8}, {5,6,8}, {1,3,7,8}, {1,4,7,8}, {1,3,4,7,8}, {0,1,3,5,7,8}, {0,4,5,7,8}, {3,4,5,7,8}, {3,6,7,8}, {4,6,7,8}, {3,4,6,7,8}, {5,6,7,8}]
  ```

### 300. `[[40,3,3]]` — CS01·CS02

- gate `01+02`, `N = 10` (3 outputs + 7 checks), T-count 4, reduced degree 2, a3 = 104
- source: length40_m7_015, origin 75; rep_length40_m7_015.json

```text
[{2,3}, {2,4}, {0,2,3,4}, {1,3,5}, {0,1,4,5}, {2,3,4,5}, {1,3,6}, {2,4,6}, {0,1,3,4,6}, {0,2,5,6}, {0,1,3,7}, {0,2,4,7}, {0,1,3,4,7}, {0,2,3,5,7}, {1,4,5,7}, {1,3,4,5,7}, {0,2,6,7}, {1,3,5,6,7}, {2,4,5,6,7}, {0,1,3,4,5,6,7}, {0,1,2,6,8}, {1,2,3,6,8}, {0,4,6,8}, {3,4,6,8}, {0,1,2,6,7,8}, {1,2,3,6,7,8}, {0,4,6,7,8}, {3,4,6,7,8}, {3,4,9}, {3,4,5,9}, {6,9}, {3,6,9}, {4,6,9}, {5,6,9}, {3,5,6,9}, {4,5,6,9}, {3,4,7,9}, {3,4,5,7,9}, {3,4,6,7,9}, {3,4,5,6,7,9}]
```

Best witness at each other check rank:

- rank 6 (`N = 9`), a3 = 160; length40_m6_001, origin 3; rep_length40_m6_001.json

  ```text
  [{0,2,3}, {1,4}, {2,3,4}, {2,3,5}, {0,1,4,5}, {2,3,4,5}, {0,2,3,6}, {2,4,6}, {0,1,3,4,6}, {1,5,6}, {1,3,7}, {2,4,7}, {0,2,3,4,7}, {2,3,5,7}, {0,1,4,5,7}, {2,3,4,5,7}, {1,3,6,7}, {1,4,6,7}, {1,3,4,6,7}, {1,5,6,7}, {1,2,3,8}, {0,1,2,4,8}, {3,4,8}, {0,1,2,3,5,8}, {1,2,4,5,8}, {3,4,5,8}, {0,1,2,3,6,8}, {1,2,4,6,8}, {0,3,4,6,8}, {5,6,8}, {0,3,7,8}, {0,4,7,8}, {0,3,4,7,8}, {0,1,2,3,5,7,8}, {1,2,4,5,7,8}, {3,4,5,7,8}, {3,6,7,8}, {4,6,7,8}, {3,4,6,7,8}, {5,6,7,8}]
  ```

### 301. `[[40,3,3]]` — CS01·CS02·CS12·CCZ012

- gate `01+02+12+012`, `N = 10` (3 outputs + 7 checks), T-count 4, reduced degree 2, a3 = 104
- source: length40_m7_015, origin 75; rep_length40_m7_015.json

```text
[{2,3}, {2,4}, {0,1,2,3,4}, {1,3,5}, {0,4,5}, {2,3,4,5}, {1,3,6}, {2,4,6}, {0,3,4,6}, {0,1,2,5,6}, {0,3,7}, {0,1,2,4,7}, {0,3,4,7}, {0,1,2,3,5,7}, {1,4,5,7}, {1,3,4,5,7}, {0,1,2,6,7}, {1,3,5,6,7}, {2,4,5,6,7}, {0,3,4,5,6,7}, {0,2,6,8}, {1,2,3,6,8}, {0,1,4,6,8}, {3,4,6,8}, {0,2,6,7,8}, {1,2,3,6,7,8}, {0,1,4,6,7,8}, {3,4,6,7,8}, {3,4,9}, {3,4,5,9}, {6,9}, {3,6,9}, {4,6,9}, {5,6,9}, {3,5,6,9}, {4,5,6,9}, {3,4,7,9}, {3,4,5,7,9}, {3,4,6,7,9}, {3,4,5,6,7,9}]
```

Best witness at each other check rank:

- rank 6 (`N = 9`), a3 = 160; length40_m6_001, origin 3; rep_length40_m6_001.json

  ```text
  [{0,1,2,3}, {0,4}, {2,3,4}, {2,3,5}, {1,4,5}, {2,3,4,5}, {0,1,2,3,6}, {2,4,6}, {1,3,4,6}, {0,5,6}, {0,3,7}, {2,4,7}, {0,1,2,3,4,7}, {2,3,5,7}, {1,4,5,7}, {2,3,4,5,7}, {0,3,6,7}, {0,4,6,7}, {0,3,4,6,7}, {0,5,6,7}, {0,2,3,8}, {1,2,4,8}, {3,4,8}, {1,2,3,5,8}, {0,2,4,5,8}, {3,4,5,8}, {1,2,3,6,8}, {0,2,4,6,8}, {0,1,3,4,6,8}, {5,6,8}, {0,1,3,7,8}, {0,1,4,7,8}, {0,1,3,4,7,8}, {1,2,3,5,7,8}, {0,2,4,5,7,8}, {3,4,5,7,8}, {3,6,7,8}, {4,6,7,8}, {3,4,6,7,8}, {5,6,7,8}]
  ```

### 302. `[[40,4,3]]` — T0·CS01·CS02·CS03·CCZ012·CCZ013·CCZ023

- gate `0+01+02+03+012+013+023`, `N = 12` (4 outputs + 8 checks), T-count 2, reduced degree 1, a3 = 56
- source: length40_m8_discovery_002, origin 143; rep_length40_m8_discovery_002.json

```text
[{0,1,2,3,5}, {0,2,3,4,5}, {2,3,6}, {0,1,2,3,4,6}, {5,7}, {0,1,4,5,7}, {1,6,7}, {4,6,7}, {0,4,5,6,7}, {0,2,4,8}, {1,2,5,8}, {0,1,2,4,6,8}, {2,5,6,8}, {0,1,3,4,7,8}, {3,5,7,8}, {0,3,4,6,7,8}, {1,3,5,6,7,8}, {4,5,6,7,8}, {0,1,2,3,4,9}, {0,1,2,3,4,5,9}, {0,1,2,3,6,9}, {0,1,2,3,5,6,9}, {4,7,9}, {4,5,7,9}, {6,7,9}, {5,6,7,9}, {4,5,6,7,9}, {4,5,6,7,8,9}, {4,5,6,7,10}, {4,5,6,7,8,10}, {4,5,6,7,9,10}, {4,5,6,7,8,9,10}, {4,5,6,7,11}, {4,5,6,7,8,11}, {4,5,6,7,9,11}, {4,5,6,7,8,9,11}, {4,5,6,7,10,11}, {4,5,6,7,8,10,11}, {4,5,6,7,9,10,11}, {4,5,6,7,8,9,10,11}]
```

Best witness at each other check rank:

- rank 7 (`N = 11`), a3 = 60; length40_m7_010, origin 38; rep_length40_m7_010.json

  ```text
  [{1,2,3,5,6}, {0,1,2,3,5,6,7}, {0,1,2,3,5,6,8}, {0,1,2,3,5,6,7,8}, {0,1,2,3,9}, {0,3,4,9}, {0,2,5,9}, {1,4,5,9}, {0,2,6,9}, {1,4,6,9}, {0,3,4,5,6,9}, {0,1,2,3,5,6,7,9}, {0,1,2,3,5,6,8,9}, {0,1,2,3,5,6,7,8,9}, {1,2,10}, {0,2,3,5,10}, {1,3,4,5,10}, {0,2,3,6,10}, {1,3,4,6,10}, {1,2,5,6,10}, {4,5,6,10}, {7,10}, {5,6,7,10}, {4,5,6,7,10}, {0,4,5,8,10}, {0,4,6,8,10}, {4,5,6,8,10}, {0,5,7,8,10}, {0,6,7,8,10}, {4,5,6,7,8,10}, {4,9,10}, {0,7,9,10}, {0,5,6,7,9,10}, {4,5,6,7,9,10}, {4,5,8,9,10}, {4,6,8,9,10}, {4,5,6,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}, {4,5,6,7,8,9,10}]
  ```

### 303. `[[40,4,3]]` — T0·T1·CS01·CS02·CS03·CS12·CS13·CCZ012·CCZ013·CCZ023·CCZ123

- gate `0+1+01+02+03+12+13+012+013+023+123`, `N = 12` (4 outputs + 8 checks), T-count 2, reduced degree 1, a3 = 56
- source: length40_m8_discovery_002, origin 143; rep_length40_m8_discovery_002.json

```text
[{0,1,2,3,5}, {1,2,3,4,5}, {0,2,3,6}, {0,1,2,3,4,6}, {5,7}, {1,4,5,7}, {0,6,7}, {4,6,7}, {0,1,4,5,6,7}, {1,2,4,8}, {2,5,8}, {0,1,2,4,6,8}, {0,2,5,6,8}, {1,3,4,7,8}, {3,5,7,8}, {0,1,3,4,6,7,8}, {0,3,5,6,7,8}, {4,5,6,7,8}, {0,1,2,3,4,9}, {0,1,2,3,4,5,9}, {0,1,2,3,6,9}, {0,1,2,3,5,6,9}, {4,7,9}, {4,5,7,9}, {6,7,9}, {5,6,7,9}, {4,5,6,7,9}, {4,5,6,7,8,9}, {4,5,6,7,10}, {4,5,6,7,8,10}, {4,5,6,7,9,10}, {4,5,6,7,8,9,10}, {4,5,6,7,11}, {4,5,6,7,8,11}, {4,5,6,7,9,11}, {4,5,6,7,8,9,11}, {4,5,6,7,10,11}, {4,5,6,7,8,10,11}, {4,5,6,7,9,10,11}, {4,5,6,7,8,9,10,11}]
```

Best witness at each other check rank:

- rank 7 (`N = 11`), a3 = 60; length40_m7_010, origin 38; rep_length40_m7_010.json

  ```text
  [{2,3,5,6}, {0,1,2,3,5,6,7}, {0,1,2,3,5,6,8}, {0,1,2,3,5,6,7,8}, {0,1,2,3,9}, {1,4,9}, {0,1,2,5,9}, {0,3,4,5,9}, {0,1,2,6,9}, {0,3,4,6,9}, {1,4,5,6,9}, {0,1,2,3,5,6,7,9}, {0,1,2,3,5,6,8,9}, {0,1,2,3,5,6,7,8,9}, {0,2,3,10}, {1,2,5,10}, {3,4,5,10}, {1,2,6,10}, {3,4,6,10}, {0,2,3,5,6,10}, {4,5,6,10}, {7,10}, {5,6,7,10}, {4,5,6,7,10}, {0,1,4,5,8,10}, {0,1,4,6,8,10}, {4,5,6,8,10}, {0,1,5,7,8,10}, {0,1,6,7,8,10}, {4,5,6,7,8,10}, {4,9,10}, {0,1,7,9,10}, {0,1,5,6,7,9,10}, {4,5,6,7,9,10}, {4,5,8,9,10}, {4,6,8,9,10}, {4,5,6,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}, {4,5,6,7,8,9,10}]
  ```

### 304. `[[40,4,3]]` — T0·T1·T2·CS01·CS02·CS03·CS12·CS13·CS23·CCZ012·CCZ013·CCZ023·CCZ123

- gate `0+1+2+01+02+03+12+13+23+012+013+023+123`, `N = 12` (4 outputs + 8 checks), T-count 2, reduced degree 1, a3 = 56
- source: length40_m8_discovery_002, origin 143; rep_length40_m8_discovery_002.json

```text
[{0,1,2,3,5}, {1,3,4,5}, {0,2,3,6}, {0,1,2,3,4,6}, {5,7}, {1,4,5,7}, {0,2,6,7}, {4,6,7}, {0,1,2,4,5,6,7}, {1,2,3,4,8}, {2,3,5,8}, {0,1,3,4,6,8}, {0,3,5,6,8}, {1,2,4,7,8}, {2,5,7,8}, {0,1,4,6,7,8}, {0,5,6,7,8}, {4,5,6,7,8}, {0,1,2,3,4,9}, {0,1,2,3,4,5,9}, {0,1,2,3,6,9}, {0,1,2,3,5,6,9}, {4,7,9}, {4,5,7,9}, {6,7,9}, {5,6,7,9}, {4,5,6,7,9}, {4,5,6,7,8,9}, {4,5,6,7,10}, {4,5,6,7,8,10}, {4,5,6,7,9,10}, {4,5,6,7,8,9,10}, {4,5,6,7,11}, {4,5,6,7,8,11}, {4,5,6,7,9,11}, {4,5,6,7,8,9,11}, {4,5,6,7,10,11}, {4,5,6,7,8,10,11}, {4,5,6,7,9,10,11}, {4,5,6,7,8,9,10,11}]
```

Best witness at each other check rank:

- rank 7 (`N = 11`), a3 = 60; length40_m7_010, origin 38; rep_length40_m7_010.json

  ```text
  [{3,5,6}, {0,1,2,3,5,6,7}, {0,1,2,3,5,6,8}, {0,1,2,3,5,6,7,8}, {0,1,2,3,9}, {1,4,9}, {1,2,5,9}, {2,3,4,5,9}, {1,2,6,9}, {2,3,4,6,9}, {1,4,5,6,9}, {0,1,2,3,5,6,7,9}, {0,1,2,3,5,6,8,9}, {0,1,2,3,5,6,7,8,9}, {0,2,3,10}, {0,1,5,10}, {0,3,4,5,10}, {0,1,6,10}, {0,3,4,6,10}, {0,2,3,5,6,10}, {4,5,6,10}, {7,10}, {5,6,7,10}, {4,5,6,7,10}, {0,1,2,4,5,8,10}, {0,1,2,4,6,8,10}, {4,5,6,8,10}, {0,1,2,5,7,8,10}, {0,1,2,6,7,8,10}, {4,5,6,7,8,10}, {4,9,10}, {0,1,2,7,9,10}, {0,1,2,5,6,7,9,10}, {4,5,6,7,9,10}, {4,5,8,9,10}, {4,6,8,9,10}, {4,5,6,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}, {4,5,6,7,8,9,10}]
  ```

### 305. `[[40,4,3]]` — T0·T1·T2·T3·CS01·CS02·CS03·CS12·CS13·CS23·CCZ012·CCZ013·CCZ023·CCZ123

- gate `0+1+2+3+01+02+03+12+13+23+012+013+023+123`, `N = 11` (4 outputs + 7 checks), T-count 1, reduced degree 1, a3 = 52
- source: length40_m7_006, origin 10; rep_length40_m7_006.json

```text
[{0,1,2,3,5}, {0,1,2,3,5,6}, {2,3,7}, {0,1,2,3,4,7}, {0,1,2,3,4,5,7}, {0,1,6,7}, {0,1,2,3,4,6,7}, {0,1,2,3,4,5,6,7}, {0,5,8}, {1,2,3,5,6,8}, {0,2,3,5,7,8}, {1,5,6,7,8}, {1,3,10}, {0,2,6,10}, {1,2,7,10}, {4,7,10}, {5,7,10}, {0,3,6,7,10}, {4,6,7,10}, {5,6,7,10}, {0,1,3,5,8,10}, {2,5,6,8,10}, {7,8,10}, {0,1,2,5,7,8,10}, {4,5,7,8,10}, {6,7,8,10}, {3,5,6,7,8,10}, {4,5,6,7,8,10}, {9,10}, {5,9,10}, {6,9,10}, {5,6,9,10}, {5,7,9,10}, {4,5,7,9,10}, {5,6,7,9,10}, {4,5,6,7,9,10}, {7,8,9,10}, {4,5,7,8,9,10}, {6,7,8,9,10}, {4,5,6,7,8,9,10}]
```

### 306. `[[40,4,3]]` — T0·T1·T2·T3·CS01·CS02·CS12·CCZ012

- gate `0+1+2+3+01+02+12+012`, `N = 12` (4 outputs + 8 checks), T-count 2, reduced degree 1, a3 = 56
- source: length40_m8_discovery_002, origin 143; rep_length40_m8_discovery_002.json

```text
[{0,1,2,5}, {1,4,5}, {0,2,3,6}, {0,1,2,4,6}, {5,7}, {1,3,4,5,7}, {0,2,6,7}, {4,6,7}, {0,1,2,3,4,5,6,7}, {1,2,4,8}, {2,3,5,8}, {0,1,4,6,8}, {0,3,5,6,8}, {1,2,3,4,7,8}, {2,5,7,8}, {0,1,3,4,6,7,8}, {0,5,6,7,8}, {4,5,6,7,8}, {0,1,2,4,9}, {0,1,2,4,5,9}, {0,1,2,6,9}, {0,1,2,5,6,9}, {4,7,9}, {4,5,7,9}, {6,7,9}, {5,6,7,9}, {4,5,6,7,9}, {4,5,6,7,8,9}, {4,5,6,7,10}, {4,5,6,7,8,10}, {4,5,6,7,9,10}, {4,5,6,7,8,9,10}, {4,5,6,7,11}, {4,5,6,7,8,11}, {4,5,6,7,9,11}, {4,5,6,7,8,9,11}, {4,5,6,7,10,11}, {4,5,6,7,8,10,11}, {4,5,6,7,9,10,11}, {4,5,6,7,8,9,10,11}]
```

Best witness at each other check rank:

- rank 7 (`N = 11`), a3 = 60; length40_m7_010, origin 38; rep_length40_m7_010.json

  ```text
  [{0,1,2,5,6}, {3,5,6,7}, {3,5,6,8}, {3,5,6,7,8}, {3,9}, {0,3,4,9}, {0,2,3,5,9}, {0,1,4,5,9}, {0,2,3,6,9}, {0,1,4,6,9}, {0,3,4,5,6,9}, {3,5,6,7,9}, {3,5,6,8,9}, {3,5,6,7,8,9}, {0,10}, {0,1,3,5,10}, {0,2,4,5,10}, {0,1,3,6,10}, {0,2,4,6,10}, {0,5,6,10}, {4,5,6,10}, {7,10}, {5,6,7,10}, {4,5,6,7,10}, {0,1,2,3,4,5,8,10}, {0,1,2,3,4,6,8,10}, {4,5,6,8,10}, {0,1,2,3,5,7,8,10}, {0,1,2,3,6,7,8,10}, {4,5,6,7,8,10}, {4,9,10}, {0,1,2,3,7,9,10}, {0,1,2,3,5,6,7,9,10}, {4,5,6,7,9,10}, {4,5,8,9,10}, {4,6,8,9,10}, {4,5,6,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}, {4,5,6,7,8,9,10}]
  ```

### 307. `[[40,4,3]]` — T0·T1·T2·T3·CS01·CS23

- gate `0+1+2+3+01+23`, `N = 12` (4 outputs + 8 checks), T-count 2, reduced degree 1, a3 = 56
- source: length40_m8_discovery_002, origin 143; rep_length40_m8_discovery_002.json

```text
[{0,1,5}, {1,2,3,4,5}, {0,6}, {0,1,4,6}, {5,7}, {1,4,5,7}, {0,2,3,6,7}, {4,6,7}, {0,1,2,3,4,5,6,7}, {1,2,4,8}, {2,5,8}, {0,1,3,4,6,8}, {0,3,5,6,8}, {1,3,4,7,8}, {3,5,7,8}, {0,1,2,4,6,7,8}, {0,2,5,6,7,8}, {4,5,6,7,8}, {0,1,4,9}, {0,1,4,5,9}, {0,1,6,9}, {0,1,5,6,9}, {4,7,9}, {4,5,7,9}, {6,7,9}, {5,6,7,9}, {4,5,6,7,9}, {4,5,6,7,8,9}, {4,5,6,7,10}, {4,5,6,7,8,10}, {4,5,6,7,9,10}, {4,5,6,7,8,9,10}, {4,5,6,7,11}, {4,5,6,7,8,11}, {4,5,6,7,9,11}, {4,5,6,7,8,9,11}, {4,5,6,7,10,11}, {4,5,6,7,8,10,11}, {4,5,6,7,9,10,11}, {4,5,6,7,8,9,10,11}]
```

Best witness at each other check rank:

- rank 7 (`N = 11`), a3 = 60; length40_m7_010, origin 38; rep_length40_m7_010.json

  ```text
  [{2,3,5,6}, {0,1,5,6,7}, {0,1,5,6,8}, {0,1,5,6,7,8}, {0,1,9}, {1,4,9}, {0,1,3,5,9}, {0,2,4,5,9}, {0,1,3,6,9}, {0,2,4,6,9}, {1,4,5,6,9}, {0,1,5,6,7,9}, {0,1,5,6,8,9}, {0,1,5,6,7,8,9}, {0,10}, {1,2,5,10}, {3,4,5,10}, {1,2,6,10}, {3,4,6,10}, {0,5,6,10}, {4,5,6,10}, {7,10}, {5,6,7,10}, {4,5,6,7,10}, {0,1,2,3,4,5,8,10}, {0,1,2,3,4,6,8,10}, {4,5,6,8,10}, {0,1,2,3,5,7,8,10}, {0,1,2,3,6,7,8,10}, {4,5,6,7,8,10}, {4,9,10}, {0,1,2,3,7,9,10}, {0,1,2,3,5,6,7,9,10}, {4,5,6,7,9,10}, {4,5,8,9,10}, {4,6,8,9,10}, {4,5,6,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}, {4,5,6,7,8,9,10}]
  ```

### 308. `[[40,4,3]]` — T0·T1·T3·CS01·CS02·CS12·CS23·CCZ012

- gate `0+1+3+01+02+12+23+012`, `N = 12` (4 outputs + 8 checks), T-count 2, reduced degree 1, a3 = 56
- source: length40_m8_discovery_002, origin 143; rep_length40_m8_discovery_002.json

```text
[{0,1,2,5}, {3,4,5}, {0,1,6}, {0,1,2,4,6}, {5,7}, {2,4,5,7}, {0,1,2,3,6,7}, {4,6,7}, {0,1,3,4,5,6,7}, {1,3,4,8}, {1,2,3,5,8}, {0,2,4,6,8}, {0,5,6,8}, {1,2,4,7,8}, {1,5,7,8}, {0,3,4,6,7,8}, {0,2,3,5,6,7,8}, {4,5,6,7,8}, {0,1,2,4,9}, {0,1,2,4,5,9}, {0,1,2,6,9}, {0,1,2,5,6,9}, {4,7,9}, {4,5,7,9}, {6,7,9}, {5,6,7,9}, {4,5,6,7,9}, {4,5,6,7,8,9}, {4,5,6,7,10}, {4,5,6,7,8,10}, {4,5,6,7,9,10}, {4,5,6,7,8,9,10}, {4,5,6,7,11}, {4,5,6,7,8,11}, {4,5,6,7,9,11}, {4,5,6,7,8,9,11}, {4,5,6,7,10,11}, {4,5,6,7,8,10,11}, {4,5,6,7,9,10,11}, {4,5,6,7,8,9,10,11}]
```

Best witness at each other check rank:

- rank 7 (`N = 11`), a3 = 60; length40_m7_010, origin 38; rep_length40_m7_010.json

  ```text
  [{0,1,2,5,6}, {2,3,5,6,7}, {2,3,5,6,8}, {2,3,5,6,7,8}, {2,3,9}, {0,2,4,9}, {1,3,5,9}, {3,4,5,9}, {1,3,6,9}, {3,4,6,9}, {0,2,4,5,6,9}, {2,3,5,6,7,9}, {2,3,5,6,8,9}, {2,3,5,6,7,8,9}, {0,3,10}, {2,5,10}, {1,2,4,5,10}, {2,6,10}, {1,2,4,6,10}, {0,3,5,6,10}, {4,5,6,10}, {7,10}, {5,6,7,10}, {4,5,6,7,10}, {0,1,3,4,5,8,10}, {0,1,3,4,6,8,10}, {4,5,6,8,10}, {0,1,3,5,7,8,10}, {0,1,3,6,7,8,10}, {4,5,6,7,8,10}, {4,9,10}, {0,1,3,7,9,10}, {0,1,3,5,6,7,9,10}, {4,5,6,7,9,10}, {4,5,8,9,10}, {4,6,8,9,10}, {4,5,6,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}, {4,5,6,7,8,9,10}]
  ```

### 309. `[[40,4,3]]` — T0·T3·CS01·CS02·CS13·CS23·CCZ012·CCZ123

- gate `0+3+01+02+13+23+012+123`, `N = 12` (4 outputs + 8 checks), T-count 2, reduced degree 1, a3 = 56
- source: length40_m8_discovery_002, origin 143; rep_length40_m8_discovery_002.json

```text
[{1,2,3,5}, {0,1,4,5}, {1,3,6}, {1,2,3,4,6}, {5,7}, {2,4,5,7}, {0,2,3,6,7}, {4,6,7}, {0,3,4,5,6,7}, {0,1,3,4,8}, {0,1,2,3,5,8}, {1,2,4,6,8}, {1,5,6,8}, {2,3,4,7,8}, {3,5,7,8}, {0,4,6,7,8}, {0,2,5,6,7,8}, {4,5,6,7,8}, {1,2,3,4,9}, {1,2,3,4,5,9}, {1,2,3,6,9}, {1,2,3,5,6,9}, {4,7,9}, {4,5,7,9}, {6,7,9}, {5,6,7,9}, {4,5,6,7,9}, {4,5,6,7,8,9}, {4,5,6,7,10}, {4,5,6,7,8,10}, {4,5,6,7,9,10}, {4,5,6,7,8,9,10}, {4,5,6,7,11}, {4,5,6,7,8,11}, {4,5,6,7,9,11}, {4,5,6,7,8,9,11}, {4,5,6,7,10,11}, {4,5,6,7,8,10,11}, {4,5,6,7,9,10,11}, {4,5,6,7,8,9,10,11}]
```

Best witness at each other check rank:

- rank 7 (`N = 11`), a3 = 60; length40_m7_010, origin 38; rep_length40_m7_010.json

  ```text
  [{1,2,3,5,6}, {0,1,2,5,6,7}, {0,1,2,5,6,8}, {0,1,2,5,6,7,8}, {0,1,2,9}, {2,4,9}, {3,5,9}, {1,4,5,9}, {3,6,9}, {1,4,6,9}, {2,4,5,6,9}, {0,1,2,5,6,7,9}, {0,1,2,5,6,8,9}, {0,1,2,5,6,7,8,9}, {0,1,10}, {0,2,5,10}, {0,1,2,3,4,5,10}, {0,2,6,10}, {0,1,2,3,4,6,10}, {0,1,5,6,10}, {4,5,6,10}, {7,10}, {5,6,7,10}, {4,5,6,7,10}, {0,3,4,5,8,10}, {0,3,4,6,8,10}, {4,5,6,8,10}, {0,3,5,7,8,10}, {0,3,6,7,8,10}, {4,5,6,7,8,10}, {4,9,10}, {0,3,7,9,10}, {0,3,5,6,7,9,10}, {4,5,6,7,9,10}, {4,5,8,9,10}, {4,6,8,9,10}, {4,5,6,8,9,10}, {5,7,8,9,10}, {6,7,8,9,10}, {4,5,6,7,8,9,10}]
  ```

### 310. `[[40,5,3]]` — T0·CS01·CS02·CS03·CS04·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034

- gate `0+01+02+03+04+012+013+014+023+024+034`, `N = 12` (5 outputs + 7 checks), T-count 2, reduced degree 1, a3 = 80
- source: length40_m7_006, origin 10; rep_length40_m7_006.json

```text
[{1,2,3,4,6}, {1,2,3,4,6,7}, {0,1,2,8}, {1,2,3,4,5,8}, {1,2,3,4,5,6,8}, {1,2,7,8}, {1,2,3,4,5,7,8}, {1,2,3,4,5,6,7,8}, {1,6,9}, {0,1,6,7,9}, {1,3,4,6,8,9}, {0,1,3,4,6,7,8,9}, {0,1,3,11}, {1,3,7,11}, {0,1,4,8,11}, {5,8,11}, {6,8,11}, {1,4,7,8,11}, {5,7,8,11}, {6,7,8,11}, {1,2,4,6,9,11}, {0,1,2,4,6,7,9,11}, {8,9,11}, {1,2,3,6,8,9,11}, {5,6,8,9,11}, {7,8,9,11}, {0,1,2,3,6,7,8,9,11}, {5,6,7,8,9,11}, {10,11}, {6,10,11}, {7,10,11}, {6,7,10,11}, {6,8,10,11}, {5,6,8,10,11}, {6,7,8,10,11}, {5,6,7,8,10,11}, {8,9,10,11}, {5,6,8,9,10,11}, {7,8,9,10,11}, {5,6,7,8,9,10,11}]
```

### 311. `[[40,5,3]]` — T0·T1·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134

- gate `0+1+01+02+03+04+12+13+14+012+013+014+023+024+034+123+124+134`, `N = 12` (5 outputs + 7 checks), T-count 2, reduced degree 1, a3 = 80
- source: length40_m7_006, origin 10; rep_length40_m7_006.json

```text
[{2,3,4,6}, {2,3,4,6,7}, {0,1,2,8}, {2,3,4,5,8}, {2,3,4,5,6,8}, {2,7,8}, {2,3,4,5,7,8}, {2,3,4,5,6,7,8}, {1,2,6,9}, {0,2,6,7,9}, {1,2,3,4,6,8,9}, {0,2,3,4,6,7,8,9}, {0,2,3,11}, {1,2,3,7,11}, {0,2,4,8,11}, {5,8,11}, {6,8,11}, {1,2,4,7,8,11}, {5,7,8,11}, {6,7,8,11}, {2,4,6,9,11}, {0,1,2,4,6,7,9,11}, {8,9,11}, {2,3,6,8,9,11}, {5,6,8,9,11}, {7,8,9,11}, {0,1,2,3,6,7,8,9,11}, {5,6,7,8,9,11}, {10,11}, {6,10,11}, {7,10,11}, {6,7,10,11}, {6,8,10,11}, {5,6,8,10,11}, {6,7,8,10,11}, {5,6,7,8,10,11}, {8,9,10,11}, {5,6,8,9,10,11}, {7,8,9,10,11}, {5,6,7,8,9,10,11}]
```

### 312. `[[40,5,3]]` — T0·T1·T2·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234

- gate `0+1+2+01+02+03+04+12+13+14+23+24+012+013+014+023+024+034+123+124+134+234`, `N = 12` (5 outputs + 7 checks), T-count 2, reduced degree 1, a3 = 80
- source: length40_m7_006, origin 10; rep_length40_m7_006.json

```text
[{3,4,6}, {3,4,6,7}, {0,1,3,8}, {3,4,5,8}, {3,4,5,6,8}, {2,3,7,8}, {3,4,5,7,8}, {3,4,5,6,7,8}, {1,6,9}, {0,2,6,7,9}, {1,2,4,6,8,9}, {0,4,6,7,8,9}, {0,2,4,11}, {1,4,7,11}, {0,8,11}, {5,8,11}, {6,8,11}, {1,2,7,8,11}, {5,7,8,11}, {6,7,8,11}, {3,6,9,11}, {0,1,2,3,6,7,9,11}, {8,9,11}, {2,3,4,6,8,9,11}, {5,6,8,9,11}, {7,8,9,11}, {0,1,3,4,6,7,8,9,11}, {5,6,7,8,9,11}, {10,11}, {6,10,11}, {7,10,11}, {6,7,10,11}, {6,8,10,11}, {5,6,8,10,11}, {6,7,8,10,11}, {5,6,7,8,10,11}, {8,9,10,11}, {5,6,8,9,10,11}, {7,8,9,10,11}, {5,6,7,8,9,10,11}]
```

### 313. `[[40,5,3]]` — T0·T1·T2·T3·CS01·CS02·CS03·CS04·CS12·CS13·CS14·CS23·CS24·CS34·CCZ012·CCZ013·CCZ014·CCZ023·CCZ024·CCZ034·CCZ123·CCZ124·CCZ134·CCZ234

- gate `0+1+2+3+01+02+03+04+12+13+14+23+24+34+012+013+014+023+024+034+123+124+134+234`, `N = 12` (5 outputs + 7 checks), T-count 2, reduced degree 1, a3 = 80
- source: length40_m7_006, origin 10; rep_length40_m7_006.json

```text
[{0,1,2,3,4,6}, {0,1,2,3,4,6,7}, {2,3,4,8}, {0,1,2,3,4,5,8}, {0,1,2,3,4,5,6,8}, {0,1,4,7,8}, {0,1,2,3,4,5,7,8}, {0,1,2,3,4,5,6,7,8}, {0,4,6,9}, {1,2,3,4,6,7,9}, {0,2,3,4,6,8,9}, {1,4,6,7,8,9}, {1,3,4,11}, {0,2,4,7,11}, {1,2,4,8,11}, {5,8,11}, {6,8,11}, {0,3,4,7,8,11}, {5,7,8,11}, {6,7,8,11}, {0,1,3,4,6,9,11}, {2,4,6,7,9,11}, {8,9,11}, {0,1,2,4,6,8,9,11}, {5,6,8,9,11}, {7,8,9,11}, {3,4,6,7,8,9,11}, {5,6,7,8,9,11}, {10,11}, {6,10,11}, {7,10,11}, {6,7,10,11}, {6,8,10,11}, {5,6,8,10,11}, {6,7,8,10,11}, {5,6,7,8,10,11}, {8,9,10,11}, {5,6,8,9,10,11}, {7,8,9,10,11}, {5,6,7,8,9,10,11}]
```

### 314. `[[40,5,3]]` — T0·T1·T2·T3·T4·CS01·CS02·CS03·CS12·CS13·CS23·CCZ012·CCZ013·CCZ023·CCZ123

- gate `0+1+2+3+4+01+02+03+12+13+23+012+013+023+123`, `N = 12` (5 outputs + 7 checks), T-count 2, reduced degree 1, a3 = 80
- source: length40_m7_006, origin 10; rep_length40_m7_006.json

```text
[{4,6}, {4,6,7}, {0,1,4,8}, {4,5,8}, {4,5,6,8}, {2,3,7,8}, {4,5,7,8}, {4,5,6,7,8}, {1,6,9}, {0,2,3,4,6,7,9}, {1,2,3,4,6,8,9}, {0,6,7,8,9}, {0,2,4,11}, {1,3,7,11}, {0,3,8,11}, {5,8,11}, {6,8,11}, {1,2,4,7,8,11}, {5,7,8,11}, {6,7,8,11}, {3,4,6,9,11}, {0,1,2,6,7,9,11}, {8,9,11}, {2,6,8,9,11}, {5,6,8,9,11}, {7,8,9,11}, {0,1,3,4,6,7,8,9,11}, {5,6,7,8,9,11}, {10,11}, {6,10,11}, {7,10,11}, {6,7,10,11}, {6,8,10,11}, {5,6,8,10,11}, {6,7,8,10,11}, {5,6,7,8,10,11}, {8,9,10,11}, {5,6,8,9,10,11}, {7,8,9,10,11}, {5,6,7,8,9,10,11}]
```

### 315. `[[40,5,3]]` — T0·T1·T2·T3·T4·CS01·CS02·CS12·CS34·CCZ012

- gate `0+1+2+3+4+01+02+12+34+012`, `N = 12` (5 outputs + 7 checks), T-count 2, reduced degree 1, a3 = 80
- source: length40_m7_006, origin 10; rep_length40_m7_006.json

```text
[{3,4,6}, {3,4,6,7}, {0,1,4,8}, {3,4,5,8}, {3,4,5,6,8}, {2,3,7,8}, {3,4,5,7,8}, {3,4,5,6,7,8}, {1,6,9}, {0,2,3,4,6,7,9}, {1,2,4,6,8,9}, {0,3,6,7,8,9}, {0,2,3,11}, {1,4,7,11}, {0,3,4,8,11}, {5,8,11}, {6,8,11}, {1,2,7,8,11}, {5,7,8,11}, {6,7,8,11}, {3,6,9,11}, {0,1,2,4,6,7,9,11}, {8,9,11}, {2,3,4,6,8,9,11}, {5,6,8,9,11}, {7,8,9,11}, {0,1,6,7,8,9,11}, {5,6,7,8,9,11}, {10,11}, {6,10,11}, {7,10,11}, {6,7,10,11}, {6,8,10,11}, {5,6,8,10,11}, {6,7,8,10,11}, {5,6,7,8,10,11}, {8,9,10,11}, {5,6,8,9,10,11}, {7,8,9,10,11}, {5,6,7,8,9,10,11}]
```

### 316. `[[40,5,3]]` — T0·T1·T2·T4·CS01·CS02·CS03·CS12·CS13·CS23·CS34·CCZ012·CCZ013·CCZ023·CCZ123

- gate `0+1+2+4+01+02+03+12+13+23+34+012+013+023+123`, `N = 12` (5 outputs + 7 checks), T-count 2, reduced degree 1, a3 = 80
- source: length40_m7_006, origin 10; rep_length40_m7_006.json

```text
[{0,1,2,3,6}, {0,1,2,3,6,7}, {1,2,3,4,8}, {0,1,2,3,5,8}, {0,1,2,3,5,6,8}, {0,3,7,8}, {0,1,2,3,5,7,8}, {0,1,2,3,5,6,7,8}, {3,6,9}, {0,1,2,3,4,6,7,9}, {1,2,3,6,8,9}, {0,3,4,6,7,8,9}, {0,2,3,4,11}, {1,3,7,11}, {0,1,3,4,8,11}, {5,8,11}, {6,8,11}, {2,3,7,8,11}, {5,7,8,11}, {6,7,8,11}, {0,2,3,6,9,11}, {1,3,4,6,7,9,11}, {8,9,11}, {0,1,3,6,8,9,11}, {5,6,8,9,11}, {7,8,9,11}, {2,3,4,6,7,8,9,11}, {5,6,7,8,9,11}, {10,11}, {6,10,11}, {7,10,11}, {6,7,10,11}, {6,8,10,11}, {5,6,8,10,11}, {6,7,8,10,11}, {5,6,7,8,10,11}, {8,9,10,11}, {5,6,8,9,10,11}, {7,8,9,10,11}, {5,6,7,8,9,10,11}]
```

### 317. `[[40,5,3]]` — T0·T1·T3·T4·CS01·CS02·CS12·CS23·CS24·CS34·CCZ012·CCZ234

- gate `0+1+3+4+01+02+12+23+24+34+012+234`, `N = 12` (5 outputs + 7 checks), T-count 2, reduced degree 1, a3 = 80
- source: length40_m7_006, origin 10; rep_length40_m7_006.json

```text
[{2,3,4,6}, {2,3,4,6,7}, {0,2,4,8}, {2,3,4,5,8}, {2,3,4,5,6,8}, {1,2,3,7,8}, {2,3,4,5,7,8}, {2,3,4,5,6,7,8}, {0,6,9}, {1,3,4,6,7,9}, {0,1,4,6,8,9}, {3,6,7,8,9}, {1,3,11}, {0,4,7,11}, {3,4,8,11}, {5,8,11}, {6,8,11}, {0,1,7,8,11}, {5,7,8,11}, {6,7,8,11}, {2,3,6,9,11}, {0,1,2,4,6,7,9,11}, {8,9,11}, {1,2,3,4,6,8,9,11}, {5,6,8,9,11}, {7,8,9,11}, {0,2,6,7,8,9,11}, {5,6,7,8,9,11}, {10,11}, {6,10,11}, {7,10,11}, {6,7,10,11}, {6,8,10,11}, {5,6,8,10,11}, {6,7,8,10,11}, {5,6,7,8,10,11}, {8,9,10,11}, {5,6,8,9,10,11}, {7,8,9,10,11}, {5,6,7,8,9,10,11}]
```

### 318. `[[40,5,3]]` — T0·T1·T4·CS01·CS02·CS03·CS12·CS13·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ123·CCZ234

- gate `0+1+4+01+02+03+12+13+24+34+012+013+023+123+234`, `N = 12` (5 outputs + 7 checks), T-count 2, reduced degree 1, a3 = 80
- source: length40_m7_006, origin 10; rep_length40_m7_006.json

```text
[{2,3,4,6}, {2,3,4,6,7}, {0,2,8}, {2,3,4,5,8}, {2,3,4,5,6,8}, {1,2,4,7,8}, {2,3,4,5,7,8}, {2,3,4,5,6,7,8}, {0,3,6,9}, {1,3,4,6,7,9}, {0,1,6,8,9}, {4,6,7,8,9}, {1,4,11}, {0,7,11}, {3,4,8,11}, {5,8,11}, {6,8,11}, {0,1,3,7,8,11}, {5,7,8,11}, {6,7,8,11}, {2,4,6,9,11}, {0,1,2,6,7,9,11}, {8,9,11}, {1,2,3,4,6,8,9,11}, {5,6,8,9,11}, {7,8,9,11}, {0,2,3,6,7,8,9,11}, {5,6,7,8,9,11}, {10,11}, {6,10,11}, {7,10,11}, {6,7,10,11}, {6,8,10,11}, {5,6,8,10,11}, {6,7,8,10,11}, {5,6,7,8,10,11}, {8,9,10,11}, {5,6,8,9,10,11}, {7,8,9,10,11}, {5,6,7,8,9,10,11}]
```

### 319. `[[40,5,3]]` — T0·T4·CS01·CS02·CS03·CS14·CS24·CS34·CCZ012·CCZ013·CCZ023·CCZ124·CCZ134·CCZ234

- gate `0+4+01+02+03+14+24+34+012+013+023+124+134+234`, `N = 12` (5 outputs + 7 checks), T-count 2, reduced degree 1, a3 = 80
- source: length40_m7_006, origin 10; rep_length40_m7_006.json

```text
[{1,2,3,4,6}, {1,2,3,4,6,7}, {0,1,8}, {1,2,3,4,5,8}, {1,2,3,4,5,6,8}, {1,4,7,8}, {1,2,3,4,5,7,8}, {1,2,3,4,5,6,7,8}, {1,6,9}, {0,1,4,6,7,9}, {1,2,3,6,8,9}, {0,1,2,3,4,6,7,8,9}, {0,1,2,4,11}, {1,2,7,11}, {0,1,3,4,8,11}, {5,8,11}, {6,8,11}, {1,3,7,8,11}, {5,7,8,11}, {6,7,8,11}, {1,3,4,6,9,11}, {0,1,3,6,7,9,11}, {8,9,11}, {1,2,4,6,8,9,11}, {5,6,8,9,11}, {7,8,9,11}, {0,1,2,6,7,8,9,11}, {5,6,7,8,9,11}, {10,11}, {6,10,11}, {7,10,11}, {6,7,10,11}, {6,8,10,11}, {5,6,8,10,11}, {6,7,8,10,11}, {5,6,7,8,10,11}, {8,9,10,11}, {5,6,8,9,10,11}, {7,8,9,10,11}, {5,6,7,8,9,10,11}]
```

