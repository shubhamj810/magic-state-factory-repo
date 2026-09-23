# Sharding the independent row-space audit

**Nothing in this repository requires a cluster.** Every shipped artifact is
produced by the four commands in [`../../../REPRODUCING.md`](../../../REPRODUCING.md)
and runs in minutes on a laptop:

| pass | command | time here |
|---|---|---|
| width <= 3, whole ladder | `classify.py --kmax 3 --tag k3` | ~2 min |
| width 4, away from n=31 | `classify.py --ns ... --kmax 4 --tag k4_easy` | ~15 s |
| width 4, the n=31 parents | `classify.py --ns 31 --kmax 4 --skip-classes 0 --tag k4_n31_rest` | ~5 s |
| the maximally symmetric n=31 parent | `hard_parent_n31.py --kmax 5` | ~2 min |

This note is about the *optional* second enumerator,
[`../classify_rowspace.py`](../classify_rowspace.py), which re-derives the same
classes in the full row space instead of the quotient. It is the independent
cross-check (`tests/test_classification.py` runs both on the small ladder), and
it is much slower, because it does not get the factor-`2^r` the quotient gives.
Sharding it is therefore worth doing if you want the full-ladder cross-check
rather than the small-ladder one.

## The sharding interface

`classify_rowspace.py` splits the work itself; there is no scheduler-specific
driver in the repository, because a correct one depends on your cluster:

```bash
cd classification/exhaustive_n38

# one line per shard task: "n chunk nchunks"  (121 lines at --nchunks 8,
# plus a trailing "# <count> shard tasks" comment line)
../../.venv/bin/python classify_rowspace.py manifest --nchunks 8

# run one shard (this is what an array task should call)
../../.venv/bin/python classify_rowspace.py task --n 38 --chunk 3 \
  --nchunks 8 --kmax 2 --budget 20000000
#   -> results/shards/shard_n38_c3of8_k2.json

# after all shards finish: merge with a global dedup
../../.venv/bin/python classify_rowspace.py merge
#   -> results/factory_catalog_n38.json
```

Shard files under `results/shards/` are gitignored: large, and reproducible from
the two commands above. Only the merged catalogue is worth keeping — and note
that it keys on `GL(k,2)`, coarser than the shipped `S_k` catalogue, so its row
counts are a lower bound on the 74 (see `classify_rowspace.py`'s docstring).

Write the array wrapper for your own scheduler: read one manifest line per array
index, call `task`, and run `merge` once at the end as a dependent job. Size the
array to the manifest's *task* count, not its line count — the trailing comment
line is not a task.

`merge` audits the shard *set* against exactly this manifest and exits nonzero
unless every task is present once, at one `--kmax` and one `--nchunks`. Chunks
that come out empty (`n = 16` has a single support, so seven of its eight chunks
are empty) are not tasks and are not expected. An empty `results/shards/`
directory is refused before anything is written, rather than merged into an empty
"complete" catalogue over the top of a real one.

## What it cost when we ran it

Measured single-core, ~0.9M nodes/s, at `--kmax 2` (the setting at which the
full ladder is exhaustive rather than budget-capped):

| n | supports | max row-code dim | single-core time | exhaustive at 20M nodes? |
|---|---:|---:|---:|---|
| 38 | 3032 | 11 | ~80 min | yes |
| 36 | 2390 | 15 | ~110 min | class-0 capped |
| 32 | 1514 | 16 | ~35 min | class-0 capped |
| 35 | 504 | 14 | ~25 min | class-0 capped |
| 31 | 320 | 15 | ~15 min | class-0 capped |
| 37 | 304 | 10 | ~8 min | yes |
| all others | <1000 | <=9 | ~3 min total | yes |

- **Total ~5 core-hours** for the whole `n <= 38` sweep at `kmax = 2`; with 121
  shards the longest single shard is ~15 min.
- **Per task:** 1 CPU, well under 1 GB, and an hour of walltime is generous.
- **"class-0 capped"** means the low-`m` near-affine-subspace support at that
  `n` hit the default 20M-node budget and is reported `partial`, never dropped.
  Raise `--budget` on just those shards to close them: row-code dimension 16 is
  ~2^32 nodes, roughly 80 min per support.
- **Higher `k`** costs about `2^(k*dim)`: `kmax = 3` is ~50-150 core-hours with
  most medium/high-dimension supports capped; `kmax = 4` is a sampling pass, not
  a classification. The shipped classification gets width 4 and 5 from the
  quotient engine instead, which is the entire point of the quotient.
