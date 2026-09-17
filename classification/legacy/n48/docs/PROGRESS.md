# Progress log -- `classification/legacy/n48`

Running record of the effort, newest checkpoint first.  Headline numbers
live in [`../README.md`](../README.md) *Results*; this file keeps the
sequence of decisions and what each step cost, so a later pass can see why
things are the way they are.

```text
  2026-09-05  directory laid out on the n40 template; inputs validated;
              two rank-7 weight-48 classes found missing from the length-48
              table  -> docs/INPUT_DEFECT_M7.md, rank-7 sector rerouted to RM(3,7)
  2026-09-06  checkpoint 1: n = 41 .. 46 swept and verified (1,754 classes)
              length48 sweep started (315 shards in kappa order)
              21:50  memory incident at shard 298 (kappa 8)  -> docs/INCIDENT_MEMORY_20260906.md
              22:28  sweep resumed with bounded memo, orbit cap, parent timeout, watchdog
  2026-09-11  shard 313 done: kappa <= 10 leg complete (313 / 315 shards, 5.1 days wall)
              checkpoint 2: catalogue built from the declared-partial length48 source
```

## Checkpoint 2 -- 2026-09-11

**State.**  4,207 classes at n = 41 .. 48; 2,453 at n = 47, 48 from
15,503,442 of the 15,566,440 rank->= 8 parents.  `verify48.py
--allow-partial`: PASS with 4 warnings (the declared gaps).  16 tests pass.

**What was done.**

1. The builder learnt to tell *integrity problems* from *coverage gaps*
   (`aggregate` returns both), so a source whose sweep is sound but
   unfinished is included under `--partial` with every unclassified parent
   listed (`sources.length48.coverage_gaps`: 2 unrun shards = 211
   representatives = 62,931 parents; 67 orbit-cap parents by representative
   and origin).  Before this the source was dropped wholesale.
2. Distance became a per-witness property.  At n = 48 the T class has
   distance-4 witnesses (a3 = 0) at ranks 10 -- 12 and distance-3 ones at
   ranks 8, 9; the old builder refused the class.  Rule: `a3 = 0 <=> d >= 4`,
   the row's d is the primary (minimum-a3) witness's, each landscape entry
   keeps its own.
3. The reduced-degree metric was taken off the build path.  The master
   catalogue's exact bar (`factorylib.metrics`) walks all of GL(5,2) for a
   k = 5 gate of degree >= 2 (~20 min) and samples 2,000,000 frames at k = 6
   (~7 min); with 1,794 new k = 5, 6 classes the build would have run for
   days.  The builder now reads `reduced_degree_cache.json` and marks the
   rest pending; `metrics48.py` fills the cache at low priority (running,
   one worker) and a rebuild picks the values up.  T-counts are exact and
   present for every k <= 6 class.
4. Master-catalogue cross-check: all 7 master rows at n = 47, 48 absent here
   have check rank 6 (the open sector); the 3 distance-4 master rows at
   n = 48, rank 8 were traced (affine signature) to `length48_m8_class_00057`,
   kappa = 13, in unrun shard 315.

**Cost of the length48 leg.**  313 shards, 5.07 days wall, 10.0 CPU-days at
two workers; the kappa profile is in the README.  Shards 312 and 313
(kappa 9 -- 10) took 29.7 h and 48.9 h; the tail (314: kappa 10 -- 11 at the
origin, 49,828 parents; 315: kappa 11 -- 14, 13,103 parents) is not
attempted on this laptop.

**Open items** (decisions for the owner):

| item | size | options |
|---|---|---|
| tail shards 314, 315 | 62,931 parents, kappa 10 -- 14 | cluster run of `classify48.py --source length48` (resumes at the shard boundary); or a canonical-form classifier that avoids the orbit walk |
| 67 orbit-cap parents | all n = 48, rank 8, k = 6 gates with GL(6,2) orbits > 150,000 | raise `N48_ORBIT_CAP` on a machine with memory to spare, or the canonical-form route |
| `rm37_w48` (rank 7 at n = 47, 48) | 1,870 parents, kappa up to ~12 | held until the checkpoints have been seen; census-style cost (hours per parent at the top) |
| open rank-6 word | 3 parents, kappa 20 -- 21 | `docs/OPEN_RANK6.md`: not brute-forceable; this is where the master's `[[47,4,3]] CS^2` and `[[47,5,3]] T^5` live |

## Checkpoint 1 -- 2026-09-06

n = 41 .. 46 at every covered rank: 1,754 classes; identical to the rank-7
census on the r <= 7 slice at n = 43, 44 (835 classes, both ways) and to the
n40 census landscape entry for entry.  Sources: `length42` (36 s),
`length44` (45 min), `rm37_w44` (36 min), `length46` (77 min).

## Set-up -- 2026-09-05

Inputs: the four affine classifications of unital triorthogonal spaces at
lengths 42, 44, 46, 48.  The RM(3,7) cross-check of the m = 7 sector found
the length-48 table two classes short (verified genuine, both triorthogonal,
both of affine rank 7): `docs/INPUT_DEFECT_M7.md`.  Consequence: the rank-7
sectors at n = 43, 44 and 47, 48 are taken from RM(3,7) (unconditional), the
tables are used for m >= 8 only.  Feasibility estimate given to the owner:
n <= 46 in hours, n = 47, 48 rank >= 8 in days on this laptop, the rank-7
weight-48 sector and the tail in cluster territory.
