# Complete `r <= 7`, `n <= 44` census

This directory classifies distance-3 factories whose effective check rank is at
most seven and whose injection count is at most 44. It complements the
all-rank `n <= 38` classification in [`../exhaustive_n38/`](../exhaustive_n38/).

The headline result is that the maximum exact minimal T-count anywhere in this
window is 5, attained only at `n=43`. The shipped frontier catalogue contains
all 21 distinct `S_k` classes that reach it, each with an explicit verified
circuit: the census sweep's own representatives together with the witnesses
written out in [`docs/HIGH_TCOUNT_FACTORY_WITNESSES.md`](docs/HIGH_TCOUNT_FACTORY_WITNESSES.md),
deduplicated under one `S_k` key. Nothing the census found is left out of the
table. Under the coarser `GL(k,2)` action the same 21 collapse to 13.

## Pipeline

```text
data/B-0-3-7.dat       complete AGL(7,2) orbit table for RM(3,7)
        |
gillot_langevin.py     parse, integrity-check, and mark origins
        |
rank7.py               classify every marked parent using factorylib.parent
        |
build_catalog.py       accept only complete runs, S_k-dedup, verify witnesses
        |
catalog/census_r7.{json,md}
```

## Completeness certificate

A rank-at-most-seven triorthogonal check support is a codeword of `RM(3,7)`.
The Gillot–Langevin table contains 3,486 affine-equivalence classes. The parser
recomputes every orbit size and requires

```text
sum |AGL(7,2)| / |Stab(f)| = 18446744073709551616 = 2^64.
```

Exactly 71 nonzero classes have weight at most 44. In full mode the census
marks all 128 possible origins of each class, covering 9,088 marked geometries
with effective ranks four through seven.

One upstream stabilizer entry (class 3485, weight 64) is corrected in memory
for the integrity sum; the third-party data file is preserved byte-for-byte.
The class lies outside the census window. See [`data/README.md`](data/README.md)
and [`../../THIRD_PARTY_NOTICES.md`](../../THIRD_PARTY_NOTICES.md).

## Files

| file | role |
|---|---|
| [`cli.py`](cli.py) | `data-check` and checkpointed `census` commands (checkpointed, not resumable: a rerun starts from the first geometry) |
| [`gillot_langevin.py`](gillot_langevin.py) | orbit parser, affine actions, marking, and `2^64` check |
| [`rank7.py`](rank7.py) | census loop, checkpointing, and completeness propagation |
| [`build_catalog.py`](build_catalog.py) | accept complete results, deduplicate under `S_k`, verify, and render |
| [`data/B-0-3-7.dat`](data/B-0-3-7.dat) | unchanged external orbit table |
| [`results/high_tcount_subframes_REPS.json`](results/high_tcount_subframes_REPS.json) | the 28 stored T-count-5 frontier witnesses (13 from the census sweep, 15 transcribed from `docs/`) |
| [`catalog/`](catalog/) | generated frontier catalogue |
| [`docs/HIGH_TCOUNT_FACTORY_WITNESSES.md`](docs/HIGH_TCOUNT_FACTORY_WITNESSES.md) | the T-count-5 frontier witnesses written out one by one |
| [`selfcheck.py`](selfcheck.py) | one-command check of this directory (data integrity + catalogue re-verification) |
| [`tests/`](tests/) | data integrity, engine smoke, completeness flag, and catalogue checks |
| [`build_sk_catalog.py`](build_sk_catalog.py) | build the **complete `S_k` table** of the window, every class not just the T = 5 frontier, from `cli.py census --kmax 7 --dedup symmetric` run files; proves their coverage of all 71 classes first |
| [`verify_sk_classification.py`](verify_sk_classification.py) | re-derive every witness of that table with code sharing nothing with the engine, and cross-check it against `census_r7.json`, the `n <= 38` classification and the master catalogue |
| [`sk_merge_input.py`](sk_merge_input.py) | turn the table into a `master_catalog/merge_results.py` input |
| [`write_sk_report.py`](write_sk_report.py) | write `docs/SK_CLASSIFICATION.md` from the table |
| [`fast_census.py`](fast_census.py) | the engine's classification of one geometry with orbit memoisation: identical classes, minutes instead of hours; the way to re-run the window |
| [`orbit_probe.py`](orbit_probe.py) | count the (subspace, GL-orbit member) pairs of a geometry, which is what the unmodified engine's time is proportional to (about 1 ms each) |
| [`catalog/sk_classes_r7.json`](catalog/sk_classes_r7.json), [`catalog/SK_CLASSES_R7.md`](catalog/SK_CLASSES_R7.md) | the complete `S_k` table: 1201 classes with witnesses |
| [`docs/SK_CLASSIFICATION.md`](docs/SK_CLASSIFICATION.md) | what the table is, how it was produced and verified |
| [`docs/CLUSTER_RUN.md`](docs/CLUSTER_RUN.md) | the exact commands for whatever is left to run on a cluster |
| [`results/census_shard_*.json`](results/), [`results/rep_*_*.json`](results/) | the engine's run files behind the `S_k` table, one per class or per (class, origin) |

The check-parent implementation, exact circuit verifier, and gate metrics are
shared from [`../../factorylib/`](../../factorylib/).

## Verify the input first

```bash
.venv/bin/python classification/rank7_census/cli.py data-check
```

The report must be valid, list 3,486 classes and 71 relevant classes, and sum
to `2^64`.

## Smoke run

```bash
.venv/bin/python classification/rank7_census/cli.py census \
  --class-index 306 --max-parents 2 --kmax 2 --allow-incomplete \
  --output /tmp/census_smoke.json
```

This deliberately capped run must report `complete=false`. Every node budget,
orbit budget, or `--max-parents` cap propagates that flag. Incomplete output is
search data and cannot establish nonexistence, so it also exits 1 —
`--allow-incomplete` is how a run declares that a partial sweep was the
intention. Automation that omits the flag cannot mistake a capped run for a
finished census.

## Full census

```bash
.venv/bin/python classification/rank7_census/cli.py census \
  --mode all --nmax 44 --kmax 4 --dedup symmetric \
  --node-budget 0 --orbit-budget 0 --checkpoint-every 1 \
  --output classification/rank7_census/results/census_r7_all.json
```

This is cluster-scale. Checkpoints use write-then-rename and remain
`complete=false` until the final successful write. `--mode reps` visits one
safe origin per computed stabilizer orbit and is useful for auditing, but the
published all-origin certificate uses `--mode all`.

Because that run happens on a cluster and is read in a checkout somewhere else,
the certificate names its orbit table by SHA-256 rather than by path: copy the
JSON into `results/` on any machine and `build_catalog.py` will validate it
against the bundled table. It re-counts the 9,088 marked geometries itself and
requires `--dedup symmetric`, since GL(k,2) is coarser than this catalogue's
`S_k` key and a gl-deduped run cannot have recorded every class it saw.

## Build and test

```bash
.venv/bin/python classification/rank7_census/build_catalog.py
.venv/bin/python -m unittest discover \
  -s classification/rank7_census/tests -v
```

`build_catalog.py` always loads the stored frontier witnesses. It also scans
`results/census_*.json`, loudly skips any incomplete file, and folds in
complete runs only. Every explicit circuit is rechecked from its columns.

## The complete `S_k` table (every class, not only the frontier)

`catalog/census_r7.json` is the T = 5 **frontier** of the window and nothing
else, by design.  The census sweep that certified the frontier read one gate
per compatible subspace -- its RREF basis -- and a subspace's other output
bases are distinct `S_k` classes, so that sweep was complete for geometries and
for the maximum T but not for `S_k` classes (it reaches six of the 21 frontier
classes only through the second, unrestricted subspace search, and misses
e.g. the `T ⊗ CS` factory at `n = 43`).

[`catalog/sk_classes_r7.json`](catalog/sk_classes_r7.json) closes that:
**1201 `(n, k, S_k gate)` classes**, every one with a witness circuit
re-verified two independent ways, produced by this directory's own engine
(`cli.py census --mode all --nmax 44 --kmax 7 --dedup symmetric`) over all 71
classes -- light ones at all 128 origins, heavy ones at one origin per
stabiliser orbit, which the builder proves suffices.  How it was run, verified
and cross-checked is in [`docs/SK_CLASSIFICATION.md`](docs/SK_CLASSIFICATION.md);
what to run on a cluster if a geometry is still pending is in
[`docs/CLUSTER_RUN.md`](docs/CLUSTER_RUN.md).

## Witnesses versus classes

The curated input holds **28** verified T-count-5 witnesses; the catalogue has
**21** rows. The difference is the `S_k` deduplication this repository uses
everywhere: seven of the 28 realise a gate that another witness already realises
up to a permutation of the output qubits, so one circuit per class is published
and the rest stay in
[`results/high_tcount_subframes_REPS.json`](results/high_tcount_subframes_REPS.json)
and [`docs/HIGH_TCOUNT_FACTORY_WITNESSES.md`](docs/HIGH_TCOUNT_FACTORY_WITNESSES.md).
Nothing is discarded and no class is missing: every stored witness's `S_k` class
appears in the table, which is exactly the granularity of the sibling `n <= 38`
catalogue and of every exhaustivity claim here.

## What ships, and what the headline rests on

The two halves of "the maximum exact minimal T-count is 5, attained only at
`n=43`" have different provenance, and it is worth being explicit:

- **The attaining half is shipped and re-verified locally.** The 28 stored
  witnesses in [`results/high_tcount_subframes_REPS.json`](results/high_tcount_subframes_REPS.json)
  carry explicit columns; `build_catalog.py` re-derives each gate, its exact
  T-count and its distance from those columns alone, and the tests re-check the
  21 catalogue rows. Anyone can confirm that T = 5 *is reached* at `n = 43`.
- **The maximality half comes from a completed all-origin census run that is too
  large to ship.** What is local and cheap is the *outer* enumeration: the
  orbit table's `2^64` completeness identity (`cli.py data-check`) and the 9,088
  marked geometries, both covered by `tests/test_data.py`. The *inner* result —
  that no marked geometry in the window carries a factory above T = 5 — was
  produced by `cli.py census --mode all` and is recorded by SHA-256, with its
  geometry count and mode, under `proof_partition.rank_le_7.completed_run_provenance`
  in [`../exhaustive_n38/results/n38_k56_certificate.json`](../exhaustive_n38/results/n38_k56_certificate.json).
  No file in this repository re-proves it; re-running the full census does.

The related output-width claims are in a better position: their decisive
numbers *are* locally reproducible in minutes — see the next section.

## Relationship to the `n <= 38` result

Together the two classifications prove the output-width ceiling in the
all-rank `n <= 38` window:

- effective rank at most seven is closed by this complete orbit census;
- effective rank at least eight has quotient dimension at most four and cannot
  support `k=5` or `k=6`;
- compatible dimension five occurs only at `n=31`, and no compatible
  six-space occurs.

The combined certificate is
[`../exhaustive_n38/results/n38_k56_certificate.json`](../exhaustive_n38/results/n38_k56_certificate.json).

Both of its layers are reproducible on a laptop in about five minutes, which is
worth knowing before trusting them: iterate `rank7.iter_parents(mode="all",
nmax=44)`, build each parent with `factorylib.parent.Parent.from_points`, and
enumerate `compatible_subspaces` — at `n=31` that returns exactly 992 compatible
5-spaces and no 6-space, matching the certificate row for row.

See [`../../REPRODUCING.md`](../../REPRODUCING.md) for the full operator guide.
