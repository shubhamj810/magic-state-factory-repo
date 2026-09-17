# What to run on the cluster, if it comes to that

Two computations may be left unfinished on the laptop.  Both are single-threaded,
budget-free enumerations by the repository's own engine, so they need no new
code: only wall time.  Everything below is copy-paste from the repository root
with the repository's `.venv` (Python 3.12; the engine has no dependencies
beyond the standard library).

## 0. Status at the time of writing

**Update: a cluster is no longer needed.**  [`fast_census.py`](../fast_census.py)
runs the engine's own classification of one geometry with two bookkeeping
memoisations that leave the recorded class set unchanged (an orbit shared by
several subspaces is processed once; the `k!` canonical form is computed once
per `S_k` class instead of once per orbit member).  It reproduces the engine's
output exactly on every geometry it was checked against, including the 14-hour
class 3386 / origin 1, in minutes.  Section 1's command becomes

```bash
.venv/bin/python classification/legacy/rank7_census/fast_census.py 2978 60 \
    --output classification/legacy/rank7_census/results/rep_2978_60.json
```

The rest of this note is kept for the record of what the unmodified engine
costs.

Class 3386 origin 1 **finished locally** after 13 h 59 m (288 classes, recorded as
`results/rep_3386_1.json`).  The one geometry still pending is **class 2978,
origin 60** ($n = 43$, $\kappa = 11$, an orbit of 2 origins); substitute it into
the command of section 1.  The engine costs about 1 ms per (compatible
subspace, GL(k,2)-orbit member) -- calibrated on the two finished heavy
geometries (0.79 and 1.07 ms) -- and [`orbit_probe.py`](../orbit_probe.py)
measures that member count in minutes without running the engine.

## 1. The one pending geometry: class 3386, origin 1 (now done; the recipe applies to 2978 / 60)

This is the only representative geometry whose sweep may not finish locally.
It stands for the 40 origins of its stabiliser orbit
(`gillot_langevin.origin_orbits` on class 3386, orbit containing origin 1).

```bash
.venv/bin/python classification/legacy/rank7_census/cli.py census \
    --mode all --nmax 44 --kmax 7 --dedup symmetric \
    --node-budget 0 --orbit-budget 0 --allow-incomplete \
    --class-index 3386 --origin 1 \
    --output classification/legacy/rank7_census/results/rep_3386_1.json
```

* **Resources.** One core, ~200 MB resident, no I/O until the final write.
  The engine is pure Python; there is nothing to parallelise *inside* one
  geometry.  Ask for the longest wall-time queue available (days) and a single
  slot.  The three other representatives of comparable size took 0.3, 6 and 47
  minutes; this one had run more than 4 CPU-hours at the time of writing.
* **What makes it slow.** $\kappa = 13$: 1,201,395 compatible subspaces, of
  which 12,755 have dimension 5 and 63 dimension 6, and the engine walks the
  full $GL(k,2)$ orbit of every one (`factorylib.parent.gl_orbit`, breadth
  first, `|GL(5,2)| \approx 10^7`).  Progress is not printed; the file appears
  only at the end.
* **The output** is one JSON with `geometries` (one entry, `gate_search_complete`
  must be `true`) and `factories` (one record per $S_k$ class, each with
  explicit `columns`).  `complete` will be `false` -- correctly, since the run is
  restricted to one geometry -- which is why `--allow-incomplete` is passed and
  why `build_catalog.py` (the T = 5 frontier builder) will skip it.
  `build_sk_catalog.py` is the consumer.

## 2. Folding it in

Copy the file into `classification/legacy/rank7_census/results/` beside the other
representative files and rebuild the $S_k$ catalogue from all of them:

```bash
.venv/bin/python classification/legacy/rank7_census/build_sk_catalog.py \
    --runs classification/legacy/rank7_census/results/census_shard_*.json \
           classification/legacy/rank7_census/results/rep_*_*.json
.venv/bin/python classification/legacy/rank7_census/verify_sk_classification.py
```

`build_sk_catalog.py` proves, class by class, that the run files cover every
one of the 71 relevant classes -- either all 128 origins or one origin in each
stabiliser orbit -- with every per-geometry gate search complete and no budget,
and refuses to write the catalogue otherwise.  Until `rep_3386_1.json` exists it
refuses with `class 3386: 1 origin orbit(s) with no swept member`.  Then it
re-verifies every witness from raw columns, checks the T = 5 slice against
`catalog/census_r7.json`, and writes `catalog/sk_classes_r7.{json,md}`.

Afterwards, merging into the master catalogue is
```bash
.venv/bin/python classification/legacy/rank7_census/sk_merge_input.py > /tmp/sk_merge_input.json
.venv/bin/python master_catalog/merge_results.py /tmp/sk_merge_input.json
.venv/bin/python master_catalog/attribute_classification.py \
    classification/legacy/rank7_census/catalog/sk_classes_r7.json \
    --regime "exhaustive classification n<=54"
.venv/bin/python master_catalog/verify_catalog.py
.venv/bin/python -m unittest discover -s master_catalog/tests
```
(all of which will already have been run once on the laptop with the
pre-cluster table; re-running them with the completed table is a no-op except
for whatever new classes the pending geometry adds).

## 3. The full-window certificate (optional, genuinely cluster-scale)

The repository's own certificate for the frontier builder is ONE unrestricted
run over all 9,088 origins with no orbit shortcut.  A copy was started on the
laptop (`results/census_r7_all.json`, checkpointed every 50 geometries); at its
pace it takes days.  On a cluster it cannot be sharded *into one certificate*
-- `build_catalog._certificate_problems` refuses any restricted run -- so it is
one long serial job:

```bash
.venv/bin/python classification/legacy/rank7_census/cli.py census \
    --mode all --nmax 44 --kmax 7 --dedup symmetric \
    --node-budget 0 --orbit-budget 0 --checkpoint-every 50 \
    --output classification/legacy/rank7_census/results/census_r7_all.json
```

Its value is a second, independent derivation of the *same* class set from the
same engine with no orbit reduction.  Once it exists,
`build_sk_catalog.py --runs ... --certificate results/census_r7_all.json`
requires the two class sets to be identical.  If only throughput matters, the
sharded-by-class recipe used on the laptop is the right one instead:

```bash
# one job per class; the builder proves the covering
for c in $(.venv/bin/python -c "
import sys; sys.path.insert(0,'classification/legacy/rank7_census')
from gillot_langevin import parse_file
print(' '.join(str(w.index) for w in parse_file('classification/legacy/rank7_census/data/B-0-3-7.dat', 7) if 0 < w.weight <= 44))"); do
  sbatch --wrap=".venv/bin/python classification/legacy/rank7_census/cli.py census \
     --mode all --nmax 44 --kmax 7 --dedup symmetric --node-budget 0 --orbit-budget 0 \
     --allow-incomplete --class-index $c \
     --output classification/legacy/rank7_census/results/census_shard_class_$c.json"
done
```
Per-class wall times on the laptop ranged from seconds to many hours; the eight
classes with $\kappa \ge 10$ (3386, 3268, 2978, 3257, 2990, 3236, 2936, 2633)
should be split further by `--origin` (one job per stabiliser-orbit
representative, the list `origin_orbits(word)` gives) exactly as was done here.
