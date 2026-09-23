# Exhaustive distance-3 classification for `n <= 38`

This directory classifies every genuine magic-state factory with circuit
distance at least three and at most 38 noisy injections, across every check
rank. The generated catalogue contains 74 inequivalent `(n,k,gate)` rows under
output permutations `S_k`, each with an explicit independently verified
circuit.

## Pipeline

```text
nezami_haah_reps.py     classified triorthogonal supports
          |
          v
marking.py              mark every admissible origin -> check parents
          |
          v
classify.py             exhaustive compatible frames in R(C)/C
hard_parent_n31.py      symmetry collapse for the one exceptional parent
          |
          v
build_catalog.py        global S_k dedup + circuit/metric verification
          |
          +--> catalog/classification_n38.{json,md}
          +--> plot_landscape.py -> landscape_n38.{png,pdf}
```

`classify_rowspace.py` is an independent slower classifier used as a regression
oracle: the tests run it and `classify.py` on the small ladder and require them
to agree. It produces no shipped artifact. For the whole-ladder comparison it
splits into chunks — see [`docs/SHARDING.md`](docs/SHARDING.md).

## Files to read

| file | role |
|---|---|
| [`nezami_haah_reps.py`](nezami_haah_reps.py) | classification input tables and valid `n` values |
| [`marking.py`](marking.py) | support-to-parent marking and elementary `F_2` linear algebra |
| [`classify.py`](classify.py) | main exhaustive quotient-space enumerator |
| [`dedup.py`](dedup.py) | `S_k` catalogue key and coarser `GL(k,2)` annotation |
| [`hard_parent_n31.py`](hard_parent_n31.py) | exhaustive automorphism reduction of the all-nonzero-points parent |
| [`classify_rowspace.py`](classify_rowspace.py) | independent full-row-space cross-check; chunked via `manifest`/`task`/`merge` |
| [`build_catalog.py`](build_catalog.py) | consolidate passes, deduplicate, verify, and render catalogues |
| [`plot_landscape.py`](plot_landscape.py) | classification-only plot |
| [`selfcheck.py`](selfcheck.py) | run this directory's tests and print one verdict |
| [`tests/`](tests/) | input, deduplication, independent enumeration, and catalogue checks |

Shared gate metrics and the independent fault verifier live once in
[`../../factorylib/`](../../factorylib/) and contain no solver dependency.

## Why the enumeration is complete

For a fixed check code `C`, legal output rows lie in

```text
R(C) = {a : <a,h_i>=0 and <a,h_i h_j>=0 for every check pair}
V(C) = R(C) / C.
```

All degree-at-most-three output parities and mixed output/check constraints are
invariant under adding a check row, so output enumeration descends to the much
smaller quotient `V`. A valid width-`k` output is a linearly independent frame
whose every pair satisfies the check-indexed compatibility forms. `classify.py`
visits every such frame, reads its phase tensor, applies the `S_k` key, and
constructs explicit columns for independent verification.

The one expensive case is the `n=31` parent consisting of all nonzero points of
`F_2^5`. `hard_parent_n31.py` computes the induced `GL(5,2)` action on `V` and
enumerates orbit representatives rather than millions of equivalent frames.

The quotient classifier omits representations in which two output rows become
dependent modulo `C`. Such a pair is CNOT-equivalent to a lower-width factory
plus an idle `|+>` spectator, so it adds no magic content. The independent
row-space tests enumerate these representations and verify this statement
directly. Full proof details are in [`docs/THEORY_EXHAUSTIVENESS.md`](docs/THEORY_EXHAUSTIVENESS.md).

## Deduplication

Two rows merge only if they have equal `n`, equal `k`, and phase polynomials
related by a permutation of output qubits (`S_k`). Arbitrary CNOT frame changes
are not the catalogue key: they can produce different output polynomials and
different circuit interfaces. The coarser `GL(k,2)` class is stored as an
annotation. See [`dedup.py`](dedup.py) and its tests for the `[[28,2,3]]`
example separating these notions.

## Reproduce

From the repository root:

```bash
.venv/bin/python classification/exhaustive_n38/classify.py --kmax 3 --tag k3
.venv/bin/python classification/exhaustive_n38/classify.py \
  --ns 15 16 23 24 27 28 29 30 32 33 34 35 36 37 38 \
  --kmax 4 --tag k4_easy
.venv/bin/python classification/exhaustive_n38/classify.py \
  --ns 31 --kmax 4 --skip-classes 0 --tag k4_n31_rest
.venv/bin/python classification/exhaustive_n38/hard_parent_n31.py --kmax 5
.venv/bin/python classification/exhaustive_n38/build_catalog.py
.venv/bin/python classification/exhaustive_n38/plot_landscape.py
```

The builder reads `results/quotient_catalog_*.json` plus
`results/hard_parent_n31.json`, re-canonicalizes every gate, and expects 74
distinct rows. Generated catalogue files are not hand-edited.

Run this directory's tests alone with:

```bash
.venv/bin/python -m unittest discover \
  -s classification/exhaustive_n38/tests -v
```

See [`../../REPRODUCING.md`](../../REPRODUCING.md) for runtimes and the optional
HPC row-space audit.

## Results

- 74 `S_k` classes, all at distance three and all with explicit circuits.
- No pure `CCZ` for `n <= 38`, establishing `n >= 39` at distance three.
- Maximum genuine output width `k=5`, uniquely at `[[31,5,3]]`.
- No `k=6` factory; the rank-partition certificate is documented in
  [`docs/N38_K56_CERTIFICATE.md`](docs/N38_K56_CERTIFICATE.md).
- Maximum exact minimal T-count is 4.
- No factories at `n=16` or `n=24`.
