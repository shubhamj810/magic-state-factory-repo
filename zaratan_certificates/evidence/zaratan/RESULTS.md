# Distance runs on Zaratan, 6 November 2026

These runs used the UMD cluster Zaratan (account vva-prj-aac, AMD EPYC 7763 nodes with 128 cores and 512 GB) on the
evening of 6 November 2026. They checked open catalogue rows with two programs. One is tropidist (B. Cheng, N. Guo
and F. Pan, arXiv:2611.08247; commit b03ec2d4, built with OpenMP), called through `research/plan/tdirect.py` or
through the pipeline driver `zaratan/dp_run.py`. The other is the meet-in-the-middle kernel of
`research/plan/mitm/mitm.c`. Every witness was re-checked with the catalogue's `faultcore.Circuit.harmful` and by
the XOR of the wire masks. The job scripts are in `jobs/`, the Slurm logs in `logs/`, the tropidist search records
in `zaratan_pilots.jsonl`, and the pipeline records in `dp_records/`. The workspace on the cluster is
`/scratch/zt1/project/vva-prj/user/sjn/msf`. Paths in the copied scripts point there.

## Tests before the runs

Job t1 ran on a debug node. The kernel agreed with brute force on 1,377 (problem, weight) pairs (`mitm.py test 200 7`).
tropidist's single-threshold and anchored modes agreed with brute force on 3,075 and 1,086 runs (`test_modes.py 150
21`, two threads). The kernel reproduced the laptop result on 937.87.6.a: weights 1 to 6 clean and a weight-7 fault.
tropidist reproduced 935.89.6.a at threshold 6 with 32 threads in 86 s, with the same lookup count as the laptop run
(2,895,638,949).

Job t2a checked slicing. On 255.3.7.a at weight 8, the raw tallies summed over 16 slices equal the unsliced ones
(accepted 210,826,350 and damaging 184,988,160, which give 3,011,805 and 2,642,688 after division by C(8,4)). Job
t2c checked the pipeline driver on 177.1.7.a (exact 9) and 417.1.6.a (exact 13, 4.2 GB).

## Results

| row | catalogue at dadb221 | result | evidence |
|---|---|---|---|
| 937.87.6.a | d ≥ 6, no witness | d = 7 | kernel: weights 1 to 6 clean (laptop and cluster); tropidist threshold 6 exhausted (64 threads, 105 s); weight-7 fault [0, 3, 117, 120, 449, 503, 935] |
| 742.36.6.a | d ≥ 6; certified d ≥ 8 (algebraic bound) | d = 8 | kernel: weights 1 to 7 clean (laptop); tropidist threshold 7 exhausted (64 threads, 1,736 s); weight-8 faults in all 30 partitions tried, e.g. [0, 14, 168, 434, 249, 534, 569, 660] |
| 959.65.6.a | d ≥ 6, no witness | d = 8 | kernel: weights 1 to 7 clean (laptop); tropidist threshold 6 exhausted (139 s) and threshold 7 exhausted (depth-3 table, 178 s); weight-8 faults in all 30 partitions tried, e.g. [0, 70, 697, 830, 7, 313, 520, 626] |
| 988.36.6.a | d ≥ 6; certified d ≥ 7 (tropidist) | d = 7 | tropidist threshold 6 exhausted (pass o3 on the laptop); tropidist weight-7 fault [0, 1, 2, 3, 4, 5, 6] |
| 998.26.6.a | d ≥ 6; certified d ≥ 7 (tropidist) | d ≥ 8 | tropidist threshold 7 exhausted (64 threads, 175 s); one tool |
| 441.1.6.a | d ≥ 6; certified d ≥ 13 (doubling theorem) and a witness of weight 13 | 13 | tropidist dense DP, 225 s, 32.8 GB; lower bound 13 meets the catalogue's witness |
| 575.1.6.a | d ≥ 6; certified d ≥ 15 (doubling theorem) and a witness of weight 15 | 15 | tropidist dense DP, 160 s, 65.6 GB; witness of weight 15 checked |
| 559.1.6.a | d ≥ 6; certified d ≥ 15 (doubling theorem) and a witness of weight 15 | 15 | tropidist dense DP, 298 s, 131 GB; witness of weight 15 checked |

The kernel's weight-8 runs were status runs on 30 of 1,024 partitions (959) and 30 of 256 (742). They stop at the
first damaging fault, so they give witnesses and no counts.

## Measured costs

tropidist's search at threshold 7 depends strongly on the depth of its completion table. On 959.65.6.a, 16 sampled
anchors took 513 s with depth 2 and 3.0 s with depth 3, and the full threshold-7 search took 178 s with depth 3 on
64 threads. The kernel runs about 1.8 times slower per core on these nodes than on the laptop (weight 6 on
937.87.6.a: 69 s against 37 s). The whole set of runs above cost about 60 SU.
