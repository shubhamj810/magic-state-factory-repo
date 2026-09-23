# Exhaustive distance-3 classification at `n = 39` and `n = 40`, every check rank, with the error-coefficient landscape

This directory closes the two T-counts that `../exhaustive_n38` stops short
of.  Its one external input is the complete affine classification of
length-40 no-repeated-column unital triorthogonal spaces
([`length40_catalogue.json`](length40_catalogue.json), 110 representatives),
the weight-40 analogue of the Kasami–Tokura / Nezami–Haah tables that drive
the `n <= 38` classification.  From it, every check parent with 39 or 40
injections is marked and classified completely, at every check rank, with the
orbit-memoised `S_k` classifier developed for the rank-7 census.

It does one more thing the sibling catalogues do not.  A class `(n, k, gate)`
is usually realised by circuits on parents of several check ranks and on many
output subspaces of each, and those circuits differ in their **leading error
coefficient** `a3`, the number of 3-sets of injections that pass every check
and act on the outputs (`P_fail ~ a3 p^3`; nothing lighter gets through a
distance-3 factory).  The sweep records, per class and per check rank, the
circuit of minimum `a3`, so the catalogue publishes the best circuit rather
than the first one found -- and the same sweep, run over the parents of the
two shipped classifications, shows what their one-witness tables collapsed.

Together with the shipped `n <= 38` table this gives **every distance-3
factory class with at most 40 injections**: 393 `(n, k, S_k gate)` classes,
each with an explicit, independently verified witness circuit
([`catalog/classification_upto_n40.json`](catalog/classification_upto_n40.json)).

## Result: the classes

| n | classes | by k | check rank of the best-`a3` witness | max exact T |
|---|---|---|---|---|
| 39 | 288 | k=1: 1, k=2: 4, k=3: 14, k=4: 37, k=5: 83, k=6: 149 | r=6: 163, r=7: 113, r=8: 12 | 3 |
| 40 | 31 | k=1: 1, k=2: 4, k=3: 8, k=4: 8, k=5: 10 | r=7: 15, r=8: 12, r=9: 4 | 4 |

* **The class set equals the rank-7 census slice.**  The 110 representatives
  span intrinsic dimensions 6 to 11, so their marked parents have check rank
  6 to 12, but every class carried by a rank 8 to 12 parent is also carried by
  a rank-6 or rank-7 one.  The all-rank classification at these lengths
  therefore coincides, class for class, with the `r <= 7` census table
  ([`../rank7_census/catalog/sk_classes_r7.json`](../rank7_census/catalog/sk_classes_r7.json)),
  which reached the same parents by a different route (RM(3,7) affine orbits
  at all 128 origins).  `verify40.py` checks this identity in both directions.
  The higher-rank parents are numerous and not empty; they add no *class*:

  | n | check rank | parents | parents carrying a class | distinct classes on them | classes not seen at rank <= 7 |
  |---|---|---|---|---|---|
  | 39 | 6 | 40 | 40 | 288 | — |
  | 39 | 7 | 720 | 720 | 125 | 0 |
  | 39 | 8 | 1,840 | 1,840 | 46 | 0 |
  | 39 | 9 | 1,280 | 1,280 | 13 | 0 |
  | 39 | 10 | 480 | 480 | 2 | 0 |
  | 39 | 11 | 40 | 40 | 1 | 0 |
  | 40 | 6 | 24 | 24 | 4 | — |
  | 40 | 7 | 1,585 | 636 | 31 | 0 |
  | 40 | 8 | 9,954 | 526 | 16 | 0 |
  | 40 | 9 | 15,150 | 122 | 8 | 0 |
  | 40 | 10 | 11,840 | 15 | 3 | 0 |
  | 40 | 11 | 2,020 | 0 | 0 | 0 |
  | 40 | 12 | 1 | 0 | 0 | 0 |

* Maximum genuine output width `k = 6`, at `n = 39` only (149 classes, all on
  the one rank-6 parent).  No `k = 7`: the widest compatible subspace met
  anywhere was 6, with no width cap in force.
* No pure `CCZ` at `n = 39, 40` (no class of reduced degree 3), so the
  `n <= 38` statement "no pure CCZ, hence `n >= 39`" sharpens to `n >= 41`.
* Maximum exact T-count 4, attained by 3 classes at `n = 40`.
* T-count histogram over the 319 classes: T=1: 10, T=2: 46, T=3: 260, T=4: 3.

## Result: the error-coefficient landscape

What the higher-rank parents *do* add is better circuits.  Check rank is
invariant under any change of check basis, so a rank-8 parent is a genuinely
different code from every rank-7 one, with one more independent check and
correspondingly fewer undetected fault sets.

| | `n = 39, 40` (this directory) | `n <= 38` (shipped table re-swept) | rank-7 census (`r <= 7`, `n <= 44`, re-swept) |
|---|---|---|---|
| classes | 319 | 74 | 1,201 |
| marked parents swept | 44,974 | 8,854 | 634 (one origin per stabiliser orbit) |
| (class, rank) witnesses | 537 | 116 | 1,341 |
| classes occurring at more than one rank | 145 | 26 | 137 |
| classes whose best circuit is at a higher rank than the fewest-check / shipped one | **145 (all of them)** | 18 | **137 (all of them)** |
| shipped witness beaten by a circuit on its own rank | — | 16 | 451 |
| shipped witness beaten anywhere | — | **24 of 74** | **460 of 1,201** |

Three independent parent enumerations agree on every coefficient where they
overlap: per (class, rank <= 7), the minimum `a3` found on the weight-40
parents at `n = 39, 40` equals the one found on the census's RM(3,7) parents
(448 entries, identical), and the `n <= 38` parents agree with the census at
`n <= 38` (58 entries, identical).  And none of the three sweeps finds any
`(n, k, gate)` at any distance that its shipped table lacks
(`crosscheck_new_results.py`, run on every entry of every raw run file, best
distance per class; all witnesses have distance exactly 3).

Some of what that means in circuits:

| class | fewest-check circuit | best circuit | `a3` by rank |
|---|---|---|---|
| `[[39,1]]` T | r=6, `a3` = 59 | r=8, `a3` = 19 | 6: 59, 7: 23, 8: 19, 9: 19, 10: 19, 11: 31 |
| `[[39,2]]` T·T | r=6, 101 | r=8, 35 | 6: 101, 7: 47, 8: 35, 9: 45 |
| `[[40,1]]` T | r=7, 30 | r=9, 16 | 7: 30, 8: 20, 9: 16, 10: 16 |
| `[[31,1]]` T (shipped `n <= 38`) | r=5, 75 (the shipped witness) | r=7, 27 | 5: 75, 6: 43, 7: 27, 8: 27, 9: 35 |
| `[[35,1]]` T (shipped) | r=6, 49 (shipped) | r=8, 17 | 6: 49, 7: 25, 8: 17, 9: 25 |
| `[[31,2]]` T·T·CS (shipped) | r=5, 107 (shipped) | r=7, 43 | 5: 107, 6: 59, 7: 43, 8: 43 |

Over the 145 multi-rank classes at `n = 39, 40` the best circuit cuts `a3`
by a median 35 % and up to 72 % relative to the fewest-check one.  The
coefficient is not monotone in rank: past the best rank the extra check
constrains the output subspace more than it removes fault sets (`[[39,1]]`
above rises again at r = 11).

The shipped `n <= 38` classifier keeps the first witness it meets per class
(replacing it only for a larger distance, among the first 60 seen), and its
builder keeps the max-distance, fewest-check one; the census catalogue keeps
the fewest-check witness.  Neither looked at `a3`, so both tables are correct
as *classifications* and arbitrary as *circuit* tables.  The per-rank best
circuits for both are now in
[`catalog/landscape_n38.json`](catalog/landscape_n38.json) and
[`catalog/landscape_census_r7.json`](catalog/landscape_census_r7.json).
The master catalogue inherits the census witnesses: 156 of its 319 rows at
`n = 39, 40` carry a circuit with a larger `a3` than the best one here.

## Pipeline

```text
length40_catalogue.json   110 classified weight-40 supports (the input)
          |
reps40.py                 load + validate (weight, affine rank, unital triorthogonality, counts)
          |
marking40.py              every origin: 40 odd (n=39), 2^m-40 even (n=40), 1 lift (n=40, rank m+1)
          |                                             -> 44,974 check parents
sources.py                the same marking for the n<=38 reps; the census's own orbit iterator
          |
classify40.py --source    factorylib.parent quotient V_3(C) per parent; landscape.classify_landscape:
          |               every compatible frame at every width, one witness per S_k class on
          |               the subspace of minimum a3 (no budget, no cap)
          |                                             -> results/<source>/rep_<id>.json
build_catalog40.py        weight40: coverage proof, global S_k dedup, per-rank best witnesses,
          |               canonical frames, metrics, independent re-verification
          +--> catalog/classification_n3940.{json,md}        319 classes, 537 per-rank witnesses
          +--> catalog/classification_upto_n40.{json,md}     74 (n<=38, verbatim) + 319
build_landscape.py        n38 / census: the same aggregation, compared with the shipped table
          +--> catalog/landscape_n38.{json,md}, catalog/landscape_census_r7.{json,md}
          |
verify40.py               everything again with code sharing nothing with the engine,
                          plus the completeness and landscape cross-checks
```

## Files

| file | role |
|---|---|
| [`length40_catalogue.json`](length40_catalogue.json) | **the input**: the complete length-40 classification, 110 representatives (sha256 `8f942ad1…`) |
| [`reps40.py`](reps40.py) | reads it, checks it (110 reps, 1/18/46/32/12/1 at m = 6..11, weight 40, affine rank m, rows `1, x_1..x_m` triorthogonal) |
| [`marking40.py`](marking40.py) | the three marking cases, copied from `../exhaustive_n38/marking.py`; standard library only |
| [`landscape.py`](landscape.py) | the classifier: the fast `S_k` classifier of `../rank7_census/fast_census.py` with the minimum-`a3` witness per class (why it is cheap, and the F_2 matrix algebra, in its docstring) |
| [`sources.py`](sources.py) | the three parent families: weight-40 reps, the `n <= 38` reps (`nezami_haah_reps.py`, imported unchanged), the census orbits (`rank7.iter_parents`, imported unchanged, one origin per stabiliser orbit) |
| [`classify40.py`](classify40.py) | the sweep driver, `--source weight40|n38|census`, 16 workers |
| [`build_landscape.py`](build_landscape.py) | coverage proof + per-class per-rank aggregation + witness verification (shared); builds the two landscape tables and their comparison with the shipped catalogues |
| [`build_catalog40.py`](build_catalog40.py) | the `n = 39, 40` catalogue and the combined `n <= 40` one |
| [`verify40.py`](verify40.py) | independent verification and the completeness / landscape cross-checks (see below) |
| [`crosscheck_new_results.py`](crosscheck_new_results.py) | from the raw run files of all three sweeps: no `(n, k, gate)` at its best distance that the shipped tables or the master catalogue lack, no witness off distance 3 |
| [`results/<source>/rep_<id>.json`](results/) | one file per representative: per-marking record (rank, kappa, undetected triples, widest frame, class indices with `a3`) and the representative's per-rank best witnesses |
| [`catalog/`](catalog/) | the tables, JSON and Markdown |
| [`reference/catalog_n3940_legacy.json`](reference/catalog_n3940_legacy.json) | the earlier quotient-search catalogue of these lengths (170 classes through k = 5), kept for the cross-check |
| [`reduced_degree_cache.json`](reduced_degree_cache.json) | this directory's own copy of the reduced-degree memo, so building here writes nothing outside it |
| [`tests/test_n40.py`](tests/test_n40.py) | input, marking, classifier (with `a3`) and catalogue checks |

Self-containment: nothing outside `classification/n40` was changed to make
this.  The shared engine `factorylib.parent`, the fault verifier
`factorylib.verification`, the metrics `factorylib.metrics`, the two input
tables and the census's orbit iterator, and the master catalogue's bar
`master_catalog/verify_catalog.py` are imported unmodified; everything that
needed adapting (marking, the classifier, the catalogue helpers) was copied
here and says where it came from.

## Why this is exhaustive

The argument is the one in
[`../exhaustive_n38/docs/THEORY_EXHAUSTIVENESS.md`](../exhaustive_n38/docs/THEORY_EXHAUSTIVENESS.md),
with weight 40 in place of weights `<= 38`:

1. **Every check parent comes from the table.**  A reduced distance-3 factory
   with `n` injections has check columns forming `n` distinct nonzero points
   of `F_2^r`.  Adjoin the origin when `n` is odd: the resulting set `W` has
   even size `c = n + (n mod 2) = 40` and, by triorthogonality of the check
   rows, its indicator lies in `RM(r-4, r)` -- the augmented check space is a
   unital triorthogonal space of length 40 with no repeated column.  The
   input table classifies exactly these up to affine equivalence
   (`classification_scope` in the file; `status: complete`, no dimension left,
   intrinsic dimensions 13 to 19 excluded by its square-component theorem,
   6 to 12 enumerated directly).
2. **Every marking is taken.**  The classification is affine but a check
   matrix has a distinguished zero, so each representative `S` in `F_2^m` is
   marked at every origin: on `S` (n = 39, 40 parents), off `S` inside the
   flat (n = 40, `2^m - 40` parents), and off the flat (n = 40, the single
   hyperplane-miss lift, rank `m + 1`; the lemma in the theory note shows one
   lift is all of them).  No automorphism quotient is taken; the family is
   over-complete, never under-complete.  44,974 parents in all.
3. **Every parent is classified completely.**  Outputs live in the quotient
   `V_3(C) = W_3(C)/C` (dimension at most 13 here); every compatible subspace
   is visited (`factorylib.parent.compatible_subspaces`, uncapped, no node
   budget), the full `GL(k,2)` orbit of its gate is walked, and one witness
   per `S_k` class is kept.  The orbit memoisation and the transposition
   components change what is recomputed, not what is recorded; the same
   classifier reproduced the unmodified engine's class set on every census
   geometry it was checked against (`../rank7_census/docs/SK_CLASSIFICATION.md`).
4. **The `a3` minimum is over everything.**  Whether an undetected 3-set is
   harmful depends only on the output subspace, not on the basis inside it
   (harmlessness -- even overlap with every output row -- is closed under
   XOR) nor on the coset representatives (an undetected set has even overlap
   with every check row).  So one number per compatible subspace covers every
   gate the subspace realises, every subspace is visited, and the per-class
   minimum is exact.  Each published `a3` is recounted from the published
   columns by a direct 3-set enumeration.
5. **The builder refuses anything less.**  A missing representative, a
   missing or repeated marking, an incomplete gate search, a budget, or a
   width cap that some geometry reached all abort the build.

The scope caveat of the `n <= 38` catalogue applies unchanged: frames whose
output rows are dependent modulo the check span are not enumerated; they are
a lower-width factory plus an idle spectator and carry no extra magic.

## Verification

`build_landscape.aggregate` re-checks every witness -- the primary one and the
best one at every rank -- from its raw columns with
`factorylib.verification.verify` (gate parities, all check-touching parities
even, fault distance exact by enumeration to weight 4) and recounts its `a3`;
`build_catalog40.py` recomputes T-count and reduced degree with
`factorylib.metrics`.  `verify40.py` then

* re-derives every witness with self-contained code (its own parity reader,
  brute-force `k!` canonical form, fault enumerator, direct 3-set count) and
  with the master catalogue's bar (`verify_catalog.derive`,
  `measure_distance`), and checks the columns are in the canonical `S_k`
  frame;
* checks the table records all 110 representatives and 44,974 markings,
  complete, from the table with the expected digest;
* checks the `r <= 7` slice equals the rank-7 census classes at `n = 39, 40`
  **both ways** (319 = 319, identical);
* checks all 170 classes of the earlier quotient-search catalogue are here;
* checks all 319 master-catalogue rows at `n = 39, 40` are here;
* checks the combined table is exactly the 74 shipped `n <= 38` rows plus
  these 319;
* when the census landscape is built: checks that, per (class, rank <= 7),
  the minimum `a3` found here at `n = 39, 40` equals the one found on the
  census's RM(3,7) parents exactly, and likewise the `n <= 38` landscape
  against the census at `n <= 38` -- two independent parent enumerations
  agreeing on every coefficient.

## Reproduce

From the repository root (the weight-40 sweep is about 25 minutes on 16
cores, the `n <= 38` one seconds, the census one a few hours):

```bash
.venv/bin/python classification/n40/reps40.py                          # validate the input
.venv/bin/python classification/n40/classify40.py --workers 16          # --source weight40
.venv/bin/python classification/n40/classify40.py --workers 16 --source n38
.venv/bin/python classification/n40/classify40.py --workers 16 --source census
.venv/bin/python classification/n40/build_catalog40.py
.venv/bin/python classification/n40/build_landscape.py --source n38
.venv/bin/python classification/n40/build_landscape.py --source census
.venv/bin/python classification/n40/verify40.py
.venv/bin/python classification/n40/crosscheck_new_results.py
.venv/bin/python -m unittest discover -s classification/n40/tests -v
```

`classify40.py` skips representatives whose result file is already complete
and built from the current input; pass `--force` to redo them, `--rep ID` or
`--m M` to restrict.
