# Distances from the Zaratan runs

On the evening of 6 November 2026 two programs were run on open catalogue rows,
on the UMD cluster Zaratan (AMD EPYC 7763 nodes) and on a laptop. One is
tropidist, the exact distance solver of B. Cheng, N. Guo and F. Pan
([arXiv:2611.08247](https://arxiv.org/abs/2611.08247),
[github.com/Fanerst/tropidist](https://github.com/Fanerst/tropidist), commit
`b03ec2d4`, built with OpenMP). The other is the meet-in-the-middle kernel
`research/plan/mitm/mitm.c` of the research branch, which sweeps every fault
of one weight. The research worker's own account is
[`evidence/zaratan/RESULTS.md`](evidence/zaratan/RESULTS.md).

[`certificates.json`](certificates.json) holds one record per tool and row,
bound to the row by the SHA-256 of its columns, and the faults the runs
returned. [`assemble.py`](assemble.py) writes it from the run records in
[`evidence/`](evidence/) and re-checks every fault with the catalogue's
`faultcore.Circuit.harmful` and by the XOR of the wire masks.
[`../master_catalog/migrations/zaratan_certificates_2026_11_07.py`](../master_catalog/migrations/zaratan_certificates_2026_11_07.py)
writes the results into the catalogue and refuses a record whose columns no
longer match.

## What the runs prove

| row at `dadb221` | result | tools |
|---|---|---|
| `937.87.6.a`, `d ≥ 6` | `d = 7` | kernel: weights 1 to 6 clean; tropidist: threshold 6 exhausted; a fault of weight 7 |
| `742.36.6.a`, `d ≥ 6` | `d = 8` | kernel: weights 1 to 7 clean; tropidist: threshold 7 exhausted; a fault of weight 8 |
| `959.65.6.a`, `d ≥ 6` | `d = 8` | kernel: weights 1 to 7 clean; tropidist: thresholds 6 and 7 exhausted; a fault of weight 8 |
| `988.36.6.a`, `d ≥ 6` | `d = 7` | tropidist: a fault of weight 7 (its threshold 6 was exhausted on the laptop, record `988.36.6.a` of [`../tropidist_certificates/`](../tropidist_certificates/README.md)) |
| `998.26.6.a`, `d ≥ 6` | `d ≥ 8` | tropidist: threshold 7 exhausted; no fault found |
| `441.1.6.a`, `d ≥ 6` | `d = 13` | tropidist pipeline, dense dynamic programme (32 GiB); the row's stored fault has weight 13 |
| `575.1.6.a`, `d ≥ 6` | `d = 15` | tropidist pipeline (64 GiB), with a fault of weight 15 |
| `559.1.6.a`, `d ≥ 6` | `d = 15` | tropidist pipeline (128 GiB), with a fault of weight 15 |
| `177.1.7.a`, `417.1.6.a` | `d = 9`, `d = 13` | tropidist pipeline, a test of the driver; both values were already known |

A threshold `K` exhausted means tropidist searched every anchor column with
its natural order and found no harmful fault of weight at most `K`, so
`d ≥ K + 1`. Runs on a sample of anchors were cost probes and prove nothing;
`assemble.py` does not use them. For the kernel, a weight counts as swept only
when every slice of it finished clean. Its weight-7 sweep of `959.65.6.a` ran
as two slices on the laptop, and its weight-8 runs on Zaratan stopped at the
first harmful fault of each slice, so they give faults and no counts.

The last three rows already carried the doubling theorem's bound and a fault
of that weight. For them the pipeline is a second, independent proof.

## Where the evidence comes from

Everything under [`evidence/zaratan/`](evidence/zaratan/) is a copy of
`research/zaratan/` on the research branch `research/tropidist-distances` at
commit `1300c55`: the job scripts, the Slurm logs, tropidist's search records
(`zaratan_pilots.jsonl`), the pipeline records (`dp_records/`) and the
kernel's weight-8 outputs. The paths inside the scripts point to the cluster
workspace. The kernel results from the laptop runs come from `research/plan`
on the same branch at commit `9932b15`. Their records for these three rows are
copied into [`evidence/laptop/`](evidence/laptop/), with the kernel source
(`mitm.c`, `mitm.py`, `slice_run.py`) and the tropidist driver `tdirect.py`
and its tests (`test_modes.py`). The cached rows that the kernel and
`tdirect.py` read are in [`evidence/rows/`](evidence/rows/); their columns are
the catalogue's. The pipeline read the catalogue itself, as it stood at commit
`d15e4eb`, which has the same columns for these rows.

Before the runs, the kernel agreed with brute force on 1,377 (problem, weight)
pairs and tropidist's single-threshold and anchored modes on 3,075 and 1,086
runs (job `t1`). The lower bounds are the tools' and are not re-derived by
`verify_catalog.py`. Every fault in `certificates.json` is re-checked by
`assemble.py`, and the ones the catalogue stores are re-checked by
`verify_catalog.py`.
