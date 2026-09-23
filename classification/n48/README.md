# Exhaustive distance-3 classification at `n = 41 … 48`, every check rank

This directory extends the `n <= 40` classification
([`../n40`](../n40)) by eight more T-counts.  Its inputs are the four complete
affine classifications of no-repeated-column unital triorthogonal spaces of
lengths 42, 44, 46 and 48 (`length{42,44,46,48}_catalogue.json`, 86 + 543 +
1015 + 28,873 representatives) together with the RM(3,7) orbit table already
used by [`../rank7_census`](../rank7_census).  Every check parent with 41 to
48 injections is marked from these, and each parent is classified completely
at every check rank with the orbit-memoised `S_k` classifier of `n40`,
recording per class and per rank the circuit of minimum leading error
coefficient `a3`.

> **Status (2026-09-11, checkpoint 2).**  `n = 41 .. 46` complete at every
> covered rank (checkpoint 1, 1,754 classes).  `n = 47, 48` at check rank
> >= 8: the length-48 sweep is done through its κ <= 10 shards (313 of 315,
> 15,503,442 of 15,566,440 parents; 2,453 classes) and the catalogue is built
> from it as a declared-partial source -- the 62,998 unclassified parents (two
> κ >= 11 tail shards, and 67 parents whose k = 6 orbit walk exceeded the
> 150,000-member cap) are listed one by one in the JSON.  The rank-7 sector
> `rm37_w48` is not started (held), the rank-6 word is open.  The
> CNOT-frame-reduced degree of 1,794 new k = 5, 6 classes is being filled in
> by `metrics48.py` in the background.  See *Results*.

## What is classified, and relative to what

The lengths are five times the size of `n40`'s problem and the input is not
quite the same shape, so the coverage statement is made sector by sector.
A *sector* is a (T-count range, check-rank range) block of the classification;
each is produced by one sweep source and carries its own completeness
statement.

```text
   check rank r
    ^
 13 |                              ·  ·  ·  ·  ·  ·  ·  ·          length48  (r = 8..13)
 12 |                              ·  ·  ·  ·  ·  ·  ·  ·          from the length-48 table,
 11 |                              ·  ·  ·  ·  ·  ·  ·  ·          m >= 8 only
 10 |                  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·          length46 (r=8..12) / length44 (r=8..11)
  9 |       ·  ·  ·  · ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·          length42 (r=8..10)
  8 |       ·  ·  ·  · ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·
  7 |             R  R           R  R   rm37_w44 / rm37_w48: rank-7 words of RM(3,7),
  6 |                                O  O   weight 44 / 48, one origin per stabiliser orbit
    +----------------------------------------------------->  n
          41 42   43 44   45 46   47 48

    ·  swept from a length table       R  swept from RM(3,7) (rank 7, and its rank-8 lift)
    O  open: the single rank-6 weight-48 word `a + abc` (see docs/OPEN_RANK6.md)
```

| sector | n | ranks | source | parents | completeness |
|---|---|---|---|---|---|
| `length42` | 41, 42 | 8 – 10 | length-42 table, all 86 reps, every origin | 41,558 | complete relative to the table (which has no m ≤ 7 words: weight 42 does not occur in RM(3,7)) |
| `length44` | 43, 44 | 8 – 11 | length-44 table, the 508 reps with m ≥ 8, every origin | 239,100 | complete relative to the table |
| `rm37_w44` | 43, 44 | 7 – 8 | RM(3,7) weight-44 classes (35, all rank 7), one origin per stabiliser orbit + lift | 474 | unconditional: RM(3,7)'s weight-44 orbits are the m = 7 words |
| `length46` | 45, 46 | 8 – 12 | length-46 table, all 1015 reps, every origin | 326,647 | complete relative to the table (no m ≤ 7 words) |
| `length48` | 47, 48 | 8 – 13 | length-48 table, the 28,776 reps with m ≥ 8, every origin | 15,566,440 | complete relative to the table |
| `rm37_w48` | 47, 48 | 7 – 8 | RM(3,7) weight-48 classes of rank 7 (98), one origin per stabiliser orbit + lift | 1,870 | unconditional |
| *(open)* | 47, 48 | 6 – 7 | the rank-6 weight-48 word `a + abc`, 3 parents | 3 | **not swept**: κ = 21, ~10¹⁰ compatible width-2 subspaces |

Why the m = 7 words come from RM(3,7) and not from the tables: the length-48
table lists 96 classes of intrinsic dimension 7 but RM(3,7) has 98 weight-48
rank-7 orbits (two are missing from the table, both verified genuine).  So the
tables are used only for m ≥ 8 at lengths 44 and 48, and the rank-7 sectors
are taken from the RM(3,7) table, which is complete by construction.  Details
and the two missing words: [`docs/INPUT_DEFECT_M7.md`](docs/INPUT_DEFECT_M7.md).

Reading the completeness column: "complete relative to the table" is exactly
`n40`'s statement -- the argument in
[`../exhaustive_n38/docs/THEORY_EXHAUSTIVENESS.md`](../exhaustive_n38/docs/THEORY_EXHAUSTIVENESS.md)
applies verbatim with weight `c = n + (n mod 2)`, and the only hypothesis is
that the table is the complete affine classification at that weight and
dimension.  Since the length-48 table is known to be short by two classes at
m = 7, its m ≥ 8 part is trusted as labelled (`status: complete`, no dimension
left) but not independently checked; the rank-7 sector, where it *could* be
checked, was replaced.

## Marking, in one picture

A classified support `S ⊂ F_2^m` of weight `w` becomes `2^m + 1` check
parents, exactly as in `n40`:

```text
        S = {s_1, ..., s_w}  ⊂ F_2^m           choose the origin o

   o ∈ S            o ∉ S, o ∈ F_2^m           o off the flat ("lift")
   ───────          ──────────────────         ────────────────────────
   columns          columns s_i + o            columns (s_i, 1)
   s_i + o, s_i≠o   for all i                  in F_2^{m+1}
   n = w - 1        n = w                      n = w
   rank m           rank m                     rank m + 1
```

`sources48.marking_of(m, S, origin)` does one origin; `all_origins(m)` is the
list `[0, …, 2^m - 1, "lift"]`.  For the RM(3,7) sources the origins are one
representative per orbit of the word's stabiliser (`rank7_census.gillot_langevin.origin_orbits`)
restricted to the span of `S`, plus the lift -- the census's own reduction,
which loses no class because the classifier is affine-invariant.

## Pipeline

```text
length4{2,4,6,8}_catalogue.json      the four input tables (48 shipped gzipped)
../rank7_census/  RM(3,7) table      the m = 7 words
          |
reps48.py           load + validate each table: sha256, counts by m, weight, affine rank,
          |         unital triorthogonality; cross-check the m = 7 part against RM(3,7)
sources48.py        the seven parent families (one per sector) -> Rep(id, m, support, origins)
          |
classify48.py       factorylib.parent quotient V_3(C) per parent, landscape.classify_landscape
   --source X       (n40's classifier, imported unchanged): every compatible frame at every
          |         width, one witness per S_k class on the subspace of minimum a3
          |         -> results/X/shard_NNNN.json.gz   (~50k parents per shard, resumable)
build_catalog48.py  coverage proof per source, global S_k dedup, per-rank best witnesses,
          |         canonical frames, metrics, independent re-verification
          +--> catalog/classification_n41_48.{json,md}     the new classes
          +--> catalog/witnesses/WITNESSES_N<n>.md          every per-rank witness, by n
          +--> catalog/classification_upto_n48.{json,md}   n40's 393 classes verbatim + ours
verify48.py         everything again with code sharing nothing with the engine, plus the
                    completeness proof and the cross-checks with the census and the master catalogue
```

The classifier and the verification bar are `n40`'s
([`../n40/landscape.py`](../n40/landscape.py),
[`../n40/build_landscape.py`](../n40/build_landscape.py) helpers,
`factorylib.verification`, `master_catalog/verify_catalog`), imported
unmodified.  Nothing outside `classification/n48` was changed.

## Running it

```sh
./run48.sh length42                # one source; refuses if the 1-min load is >= 4
./run48.sh length44 --rep length44_m8_class_0001    # a selection -> results/<source>/partial/
./stop48.sh [source]               # kill driver *and* workers (process group)
python build_catalog48.py [--partial]
python verify48.py
python -m unittest discover -s tests -v
```

`run48.sh` runs the driver under `nice -n 15` with two workers and logs to
`logs/<source>_<timestamp>.log`; the shard files are written atomically
(`.tmp` then rename) and a rerun skips every shard whose header matches the
current input digest, `kmax` and rep list, so an interrupted sweep resumes at
the shard boundary.  A source's shards are checked one by one by the builder
(`aggregate`), which recomputes the shard plan and separates *integrity
problems* (wrong digest or engine, a budget or cap, a histogram that does not
add up: the source is refused) from *coverage gaps* (a shard not yet run, a
parent the engine gave up on: with `--partial` the source is included and
every unclassified parent is listed under `sources.<source>.coverage_gaps`;
without it the build stops).  `verify48.py --allow-partial` re-checks that
the declared gaps account for every parent the inputs expect.

The reduced-degree metric is the one slow decoration (the master catalogue's
exact GL(5,2) walk, ~20 min per k = 5 gate of degree >= 2), so the builder
reads it from `reduced_degree_cache.json` and `metrics48.py` fills that file
in the background; rebuild afterwards to pick the values up.

The two-worker, nice-15 policy is a constraint of this laptop, not of the
method; on a cluster set `--workers` to the core count and shard the sources
by `--max-shards` / `--rep`.

## Cost

Measured with two workers under `nice -n 15` on this laptop (per-source
`done:` lines in `logs/`; CPU seconds in the catalogue's `sources`):

| source | parents | wall | CPU | parents / s (wall) |
|---|---|---|---|---|
| `length42` | 41,558 | 36 s | 72 s | 1,150 |
| `length44` | 239,100 | 45 min | 1.3 h | 89 |
| `rm37_w44` | 474 | 36 min | 1.1 h | 0.2 |
| `length46` | 326,647 | 77 min | 1.8 h | 70 |
| `length48` (313 of 315 shards) | 15,503,442 | 5.1 days | 10.0 CPU-days | 35 overall |
| `rm37_w48` | 1,870 | not run | | |

The cost is set by κ = dim V_3, the number of degree-<= 3 parities the
parent leaves free: each extra dimension roughly doubles the compatible
subspaces and, more importantly, admits wider frames whose GL(k,2) orbit
walks (39,060 members at k = 6 for a single gate) dominate.  Shards are
planned in order of κ at the origin, so the length-48 wall time is a clean
κ profile:

```text
   max κ in shard    shards   parents      wall    parents/s
        1               46   2,269,401     0.2 h     3,700
        2               68   3,360,305     0.4 h     2,600
        3               66   3,266,678     0.5 h     1,900
        4               56   2,780,910     1.2 h       670
        5               43   2,134,220     1.8 h       320
        6               16     796,154     4.0 h        56
        7               12     597,145    20.2 h         8
        8                4     199,264    15.0 h         4
        9                2      99,365    78.5 h       0.4   <- shards 312, 313 (49 h each)
      10-11 (314)              49,828    not run    est. 3-5 days here
      11-14 (315)              13,103    not run    est. weeks here: a κ = 13 parent alone is days
```

The rank-7 parents from RM(3,7) sit at κ up to 12 (the weight-44 census saw
2,881 s for one parent); at weight 48 they are 1,870 parents of that kind.

Memory: the orbit memo is bounded by member count (60,000), orbit walks are
capped at 150,000 members (`N48_ORBIT_CAP`) and a parent at 1,800 s
(`N48_PARENT_SECONDS`); the 2026-09-06 incident that motivated this is in
[`docs/INCIDENT_MEMORY_20260906.md`](docs/INCIDENT_MEMORY_20260906.md).

## Results

From [`catalog/CLASSIFICATION_N41_48.md`](catalog/CLASSIFICATION_N41_48.md)
(checkpoint 2; `verify48.py --allow-partial`: PASS, 4 warnings = the declared
gaps).  **4,207 classes at n = 41 .. 48**, 6,029 (class, rank) witnesses,
every one re-verified; with the 393 rows of `n40` the combined table
`classification_upto_n48.json` has 4,600 classes.

| n | classes | by k | best-witness rank | max T | sector status |
|---|---|---|---|---|---|
| 41 | 124 | 1 / 4 / 14 / 37 / 68 | r=8: 89, r=9: 34, r=10: 1 | 3 | complete |
| 42 | 31 | 1 / 4 / 8 / 8 / 10 | r=8: 26, r=9: 5 | 4 | complete |
| 43 | 666 | 1 / 4 / 30 / 92 / 83 / 169 / 287 | r=7: 531, r=8: 135 | 5 | complete |
| 44 | 169 | 1 / 4 / 24 / 72 / 35 / 15 / 18 | r=7: 111, r=8: 58 | 4 | complete |
| 45 | 595 | 1 / 4 / 14 / 37 / 83 / 169 / 287 | r=8: 592, r=9: 1, r=10: 2 | 3 | complete |
| 46 | 169 | 1 / 4 / 24 / 72 / 35 / 15 / 18 | r=8: 160, r=9: 1, r=10: 8 | 4 | complete |
| 47 | 377 | 1 / 4 / 34 / 105 / 83 / 149 / 1 | r=8: 249, r=9: 128 | 7 | rank >= 8, κ <= 10 part; rank 7 held; rank 6 open |
| 48 | 2,076 | 1 / 4 / 25 / 127 / 500 / 1419 | r=8: 2008, r=9: 58, r=10: 10 | 7 | rank >= 8, κ <= 10 part; rank 7 held; rank 6 open |

("by k" lists the class counts at k = 1, 2, 3, ...)

What the `n = 47, 48` rows say, and what they do not:

* Every class carried by a check parent of rank >= 8 whose length-48 space
  has κ <= 10 at the origin (99.6 % of the parents) is in the table with its
  minimum-a3 witness at every rank.  The 62,998 parents not classified are the
  κ >= 11 tail (shards 314, 315) and the 67 orbit-cap parents (all at n = 48,
  rank 8; each has a k = 6 gate whose GL(6,2) orbit exceeds 150,000 members).
  A class carried only by those parents is absent.  The master catalogue's
  three distance-4 rows at n = 48, rank 8 (`[[48,2,4]]`, `[[48,3,4]]`,
  `[[48,4,4]]`) all sit on `length48_m8_class_00057` (κ = 13, shard 315) --
  so they are not in this catalogue yet, and their gate classes appear here
  only with distance-3 witnesses from other parents.
* Of the 18 master-catalogue rows at n = 47, 48, the 7 with check rank 6
  (`[[47,4,3]]` `CS²`, `T²·CS`, `T⁴`; `[[47,5,3]]` `T⁵` and the t = 10
  class; `[[47,6,3]]`; `[[48,4,3]]` `CS²`) live on the open rank-6
  word and are outside every sector swept here.  The other 11 are classes
  here; for `T @ 47` (a3 115 -> 7), `T³ @ 47` (115 -> 31), `T² @ 48`
  (73 -> 20), `T⁴ @ 48` (140 -> 60) the best circuit here has a smaller
  leading coefficient than the master's, at one or two more checks.
* New at n = 48: 500 k = 5 and 1,419 k = 6 classes, none in the master
  catalogue; the largest gate at n = 47 is the single k = 7 class, the
  gate with all 63 degree-<= 3 monomials on 7 outputs (`N = 15`, a3 = 67).
* Eight classes at n = 48 have a distance-4 primary witness (a3 = 0): `T`
  at `N = 11` (the master's `[[48,1,4]]` needs 13), `CS`, `T²·CS`, `CCZ`,
  `T³·CS³·CCZ`, and three CCZ-products at k = 4, all at ranks 9 -- 12.  The
  `[[n,k,d]]` label carries the primary witness's distance; the rank whose
  best witness has d = 3 is marked in the landscape column.

## Files

| file | role |
|---|---|
| `length42_catalogue.json`, `length44_catalogue.json`, `length46_catalogue.json`, `length48_catalogue.json.gz` | **the inputs** (sha256 in `reps48.EXPECTED_SHA256`); the gunzipped length-48 file is git-ignored |
| [`reps48.py`](reps48.py) | reads and checks them; `affine_signature` and the RM(3,7) cross-check |
| [`sources48.py`](sources48.py) | the seven parent families and the marking |
| [`classify48.py`](classify48.py) | the sweep driver (sharded, resumable, failure-tolerant) |
| [`run48.sh`](run48.sh), [`stop48.sh`](stop48.sh) | launch under `nice` with a load guard; stop driver and workers together |
| [`build_catalog48.py`](build_catalog48.py) | coverage proof, aggregation, verification, the tables |
| [`verify48.py`](verify48.py) | independent verification and cross-checks (`--allow-partial` for a checkpoint build) |
| [`metrics48.py`](metrics48.py) | fills `reduced_degree_cache.json` for the classes whose reduced degree is pending (slow, resumable, off the build path) |
| [`watchdog48.sh`](watchdog48.sh) | kills a sweep whose worker exceeds a memory bound (2.5 GB default) |
| [`probes/`](probes/) | one-off diagnostics: orbit-memory probe, single-parent probe, master-catalogue comparison |
| [`open_rank6_bounds.py`](open_rank6_bounds.py) | the numbers behind `docs/OPEN_RANK6.md` |
| [`docs/INPUT_DEFECT_M7.md`](docs/INPUT_DEFECT_M7.md) | the two rank-7 weight-48 words missing from the length-48 table, and the policy adopted |
| [`docs/OPEN_RANK6.md`](docs/OPEN_RANK6.md) | the unswept rank-6 sector at `n = 47, 48`: what it is, why brute force does not reach it, what would |
| [`docs/INCIDENT_MEMORY_20260906.md`](docs/INCIDENT_MEMORY_20260906.md) | the memory blow-up of 2026-09-06, its cause and the four fixes |
| [`docs/PROGRESS.md`](docs/PROGRESS.md) | running log of the effort: checkpoints, decisions, open items |
| [`results/<source>/shard_NNNN.json.gz`](results/) | per-rep records: histogram over (n, rank, check rank, κ, μ, #gates), per-rank best witnesses |
| [`catalog/`](catalog/) | the tables |
| [`logs/`](logs/) | every sweep's log, including the aborted ones |
| [`reduced_degree_cache.json`](reduced_degree_cache.json) | this directory's copy of the reduced-degree memo (seeded from `n40`) |
| [`tests/test_n48.py`](tests/test_n48.py) | inputs, sources, marking, sweep worker, shard round-trip, catalogue consistency |
