# The complete `r <= 7`, `n <= 44` classification, up to `S_k`

**1201 distinct `(n, k, S_k gate)` classes** of distance-3 factory with at most seven check qubits and `n <= 44`, each with a verified witness circuit, in [`../catalog/sk_classes_r7.json`](../catalog/sk_classes_r7.json) and [`../catalog/SK_CLASSES_R7.md`](../catalog/SK_CLASSES_R7.md).

## Why this table exists

The shipped census catalogue, [`../catalog/census_r7.json`](../catalog/census_r7.json), is the census **maximum-T frontier**: the 21 classes at `T = 5`, and nothing else.  The census sweep behind it enumerated every compatible *subspace* of every marked geometry, but read one gate off each subspace -- its RREF basis.  A subspace is a code, not a gate: its other output bases are related by output CNOTs and are *distinct* `S_k` classes, which is exactly the granularity the master catalogue files rows by.  So the old sweep was complete for geometries and for the `T = 5` maximum (which a second, unrestricted subspace search corroborated), but not for `S_k` classes: it missed, for instance, the `T ⊗ CS` factory at `n = 43` that a later search campaign turned up, and even six of the 21 frontier classes were reachable only through the second search.

This table closes that gap.  It is the same window and the same 9,088 marked geometries, swept by the repository's newer engine (`factorylib.parent`, via `cli.py census --kmax 7 --dedup symmetric`), which walks the full `GL(k,2)` orbit of every compatible subspace and records one witness per `S_k` class.

## What was run

`cli.py census --mode all --nmax 44 --kmax 7 --dedup symmetric --node-budget 0 --orbit-budget 0` over the 71 `RM(3,7)` classes of weight `<= 44`.  Light classes were swept at all 128 origins; the heavy ones (`kappa >= 10`) at one origin per stabiliser orbit of origins, which suffices because two origins in one orbit give the same marked geometry up to a change of basis of the check rows (the map is affine on `F_2^7` and fixes the word), and a check-basis change moves no compatible frame and no output gate.  `build_sk_catalog.py` recomputes the orbits with the engine's own routine and proves this coverage before it writes anything.

Coverage: 44 classes at all 128 origins, 27 at orbit representatives.  Run files: `census_shard_04.json`, `census_shard_05.json`, `census_shard_06.json`, `census_shard_07.json`, `census_shard_08.json`, `census_shard_09.json` and 131 more.

## How it was verified

* **Every witness, twice, from raw columns.**  `build_sk_catalog.py` re-checks each with `factorylib.verification.verify` (gate parities, all check-touching parities even, distance exact by enumeration to weight 4).  `verify_sk_classification.py` re-derives each again with code sharing nothing with the engine -- its own parity reader, its own `k!` canonical form, its own fault enumerator -- and with the master catalogue's bar (`master_catalog/verify_catalog.derive`, `measure_distance`).
* **The `T = 5` slice is the shipped frontier.**  The classes at the maximum T are exactly the 21 of `census_r7.json`.
* **Two classifications agree on their overlap.**  On `n <= 38`, every class of the all-rank classification with `r <= 7` is here, and every class here is there.
* **Every master-catalogue row in the window is a class here**, including the campaign rows that first exposed the gap.

## The numbers

| n | classes | by k | max T |
|---|---|---|---|
| 15 | 1 | 1: 1 | 1 |
| 23 | 1 | 1: 1 | 1 |
| 27 | 1 | 1: 1 | 1 |
| 28 | 3 | 1: 1, 2: 2 | 2 |
| 31 | 5 | 1: 1, 2: 1, 3: 1, 4: 1, 5: 1 | 1 |
| 32 | 3 | 1: 1, 2: 2 | 2 |
| 35 | 13 | 1: 1, 2: 4, 3: 8 | 3 |
| 36 | 20 | 1: 1, 2: 4, 3: 8, 4: 7 | 4 |
| 39 | 288 | 1: 1, 2: 4, 3: 14, 4: 37, 5: 83, 6: 149 | 3 |
| 40 | 31 | 1: 1, 2: 4, 3: 8, 4: 8, 5: 10 | 4 |
| 43 | 666 | 1: 1, 2: 4, 3: 30, 4: 92, 5: 83, 6: 169, 7: 287 | 5 |
| 44 | 169 | 1: 1, 2: 4, 3: 24, 4: 72, 5: 35, 6: 15, 7: 18 | 4 |

By width: k=1: 12, k=2: 29, k=3: 93, k=4: 217, k=5: 212, k=6: 333, k=7: 305.
By exact T-count: T=1: 38, T=2: 139, T=3: 547, T=4: 111, T=5: 61, T=None: 305.

Compared with the master catalogue before this table was merged: it held 77 rows in the window, of which 21 came from the census frontier and the rest from the `n <= 38` classification and from search campaigns.

## Reproducing it

```bash
# one job per (class, origin) is how it was actually run; see docs/CLUSTER_RUN.md
.venv/bin/python classification/rank7_census/cli.py census --mode all --nmax 44 --kmax 7 \
    --dedup symmetric --node-budget 0 --orbit-budget 0 --allow-incomplete \
    --class-index <C> [--origin <O>] --output classification/rank7_census/results/rep_<C>_<O>.json
.venv/bin/python classification/rank7_census/build_sk_catalog.py --runs classification/rank7_census/results/census_shard_*.json classification/rank7_census/results/rep_*_*.json
.venv/bin/python classification/rank7_census/verify_sk_classification.py
```

## Engine cross-check of the fast runner

`results/rep_2978_60.json` was produced by `fast_census.py`.  The unmodified engine (`cli.py census --mode all --kmax 7 --dedup symmetric`, no budgets) was run on the same geometry in parallel and finished after 39 h 33 m; its output is kept as `results/rep_2978_60_engine_crosscheck.json`.  The two class sets are identical: 595 classes, k = 1:1, 2:4, 3:14, 4:37, 5:83, 6:169, 7:287.  With the earlier identical results on classes 3386/1 (14 h vs 3.4 min), 3268/63, 2633/3 and 2936/3, every geometry the fast runner was used for has been reproduced by the engine it shortcuts.
