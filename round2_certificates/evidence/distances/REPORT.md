# Distances and error coefficients, second round (night of 7 November 2026)

The folder holds evidence only: exact distances and exact leading error coefficients A_d, for catalogue rows and first-round results whose distance was a floor or rested on one tool. Nothing in the catalogue repository, `factory-search-repo`, `tropidist-src` or the import worktree was changed. Nothing was committed. The catalogue was read at dadb221.

Every result is one line of `results.jsonl` (60 lines), built by `assemble.py` from the raw records in `data/`. Each line is keyed by the row label or, for circuits outside the catalogue, by the SHA-256 of the column list (compact JSON, the `constructions.digest` convention). Each line gives the tools, their versions, the thread counts and the run times. The columns of every circuit are in `data/rows/<id>.json` with that SHA-256. Every witness listed was re-checked with `faultcore.Circuit.harmful` and by the literal XOR of the wire masks, and `assemble.py` checks it again.

## Zaratan

The ControlMaster was down at 00:15 and at every check from 01:05 to 01:45. `ssh -O check` finds no control socket at all, so the master process is gone, not idle. I did not try to log in, no job ran, and **0 SU were used**.

All the Zaratan work is ready to submit:
- `zaratan/push.sh` copies the folder to `$MSF/search2/distances/`.
- `zaratan/submit.sh smoke` submits `t0_smoke.sh`.
- After its log is checked, `zaratan/submit.sh full` submits j1, j2, j3, j7 and j8.
- `zaratan/pull.sh` copies results into `data/zaratan/`, where `assemble.py` reads them.

Expected cost is 50 to 75 SU, plus about 85 SU for the optional `j5`. The costs are itemised in `SU_LEDGER.md`.

Instead of waiting, I made several of the runs cheap enough for the laptop. Each laptop command ran under a minute, one at a time, at niceness 19.

## Tools written here

**`mitml/mitml.c`** is a meet-in-the-middle sweep derived from the pilot kernel `research/plan/mitm/mitm.c`. It keeps the pilot's method: split w = a + b, tabulate the b-subsets by full syndrome, look up the a-subsets, and divide by C(w, a).
- What changes is the partition key. It is Q random linear functionals of the syndrome, so a set's key is the XOR of its columns' keys.
- The last two columns of each subset come from column pairs grouped by key XOR. A sweep then costs about one enumeration instead of 2^Q. Equal syndromes still meet.
- Limits: up to 320 checks, 512 outputs and weight 12.
- Tests against brute force pass on 1,759, 820 and 1,315 (problem, weight) pairs (three seeds). They cover counts, slice sums, lists and witnesses.
- It reproduces every first-round count:
  - 255.3.7.a: weight 7 (85,248 / 97,155) and weight 8 (2,642,688 / 3,011,805);
  - all 31 counts of `research/plan/data/A_d_counts.json`.
- Speed on the laptop: a weight-6 count at n ≈ 900 takes 10 to 12 s (the pilot took 22 to 29 s). One of 2,048 partitions takes 1.9 s for weight 8 at n = 959 and 0.3 s for weight 7 at n = 935.
- Sliced counts are summed over all slices before the division.

**`trellis/trellis_count.py` and `.c`** compute A_w = B_w(ker H) − B_w(ker [H;L]), the definition in `errorcoeff.py`. They count exactly up to a weight bound with a syndrome trellis, whose states are the partial syndromes in the span intersection at each cut. Counts are kept mod 2^64, which is exact because there are only additions and the final values are far below 2^64. The program shares no code with tropidist, the kernels or faultcore. It agrees with brute force on 400 random problems and with `mitml` on A_9 of 177, 185 and 189.

**`doubled_order.py`, `order_polish.py` and `cutsa.c`** find low cut-rank column orders for the doubled rows. They anneal each self-dual block's order, interleave the two copies of a block, and rearrange whole blocks. `dp_perm.py` feeds a permuted row to tropidist's pipeline and maps any fault back to the catalogue's indices.

**`sjwit/sjfast.c`** searches for faults at San José's bound on the GF(256) rows, using the characterisation in the sparse search's `sj_witness.py`.
- A random core of w − 1 retained coordinates is tested against every completion and all 255 scalars at once, as ANDs of 256-bit sets.
- It tests about 3.4 × 10^8 sets per second on one laptop core.
- Re-checked faults at bounds 9, 10 and 11 came after 2 × 10^7, 1.7 × 10^8 and 1.6 × 10^9 sets (0.3, 0.6 and 4.5 s). Those rows were already exact, so this only validates the program.
- The counts fit a model in which a set of size w works with probability 255 · (21/255)^w.

**`flat512.py`** counts the harmful 3-flats of 512.39.6.a literally.

## Results

### Open catalogue rows

**599.1.6.a: d = 15 exactly.**
- tropidist's best order needs a 1 TiB DP table (cut rank 39). On `data/orders/599.1.6.a.json` the cut rank is 30, and tropidist's own estimate drops to 2 GiB and 67 s.
- The pipeline (`dp=2,table_gb=3,dp_fast=300`, b03ec2d4, one thread, laptop) returned DP value 15 after 33.7 s of DP, with a 2.2 GB peak.
- The doubling theorem (Jain and Albert) gives the same floor independently, and the stored weight-15 witness gives the upper bound.

**988.36.6.a: d = 7 exactly, two tools.** `mitml` swept weights 1 to 6 in count mode and found no accepted fault (23 s). With tropidist's threshold 6 and its fault [0..6], that settles it.

**998.26.6.a: d = 8 exactly.**
- `mitml` found the weight-8 fault [15, 64, 72, 245, 260, 307, 315, 323] in the third of 2,048 partitions (6.6 s).
- The floor 8 is tropidist's threshold 7. `mitml` is clean to weight 6, so the floor at weight 7 is still one tool.
- j1 runs the weight-7 sweep (about 1 SU).

**935.89.6.a and 936.88.6.a: d = 7 exactly, two tools.** This was in the pilot's records but not in any report.
- The pilot kernel is clean to weight 6, with weight-7 faults [0, 28, 165, 175, 254, 282, 927] and [0, 3, 117, 120, 448, 502, 934]. I re-checked both.
- tropidist exhausted threshold 6: in the pilot run (1,056 s) for 935, and in pass o3 for 936.

**756.32.6.a is unchanged.** It still stands on the theorem bound 9, a fault at 9, and both tools clean through weight 7. j1's weight-8 sweep (about 1 SU) would make it exact by the kernel.

**Doubled rows from 761.1.6.a up stay theorem plus witness.**
- The best order for 761 has cut rank 42 (stored order 51). Its [[101,1,17]] block stayed at 41 after 4 million annealing moves.
- 967, 983, 1011 and 1301 to 3239 are wider still.

### Independent confirmations

- **177, 185, 189:** `mitml` sweeps weights 1 to 8 clean, and the trellis gives A_w = 0 for w < 9. That is a third method for d = 9.
- **271, 279, 283 (d = 11) and 401 (d = 13):** confirmed by the trellis, each in two column orders.
- **511.9.6.a:** MacWilliams on its 27 check rows (the catalogue's `errorcoeff`, 8 s) shows no accepted fault of weight 1 to 6 exists. That is a search-free proof of d ≥ 7.
- **Lift [[931,93,7]] 83a91c80c5 and [[932,92,7]] 0f5a3a3102:** `mitml`, a second implementation of the sweep, is clean to weight 6, and the weight-7 faults were re-checked. The tropidist opinion the rules require is job j2 (about 5 SU).

### Exact A_d

The catalogue had A_d = null for every row here.

| circuit | d | A_d | accepted | methods |
|---|---|---|---|---|
| 512.39.6.a | 8 | 50,397,952 | 50,434,240 | literal count over all 788,035 subspaces × 64 cosets (17 s); matches the parents search's kernel and Plücker counts |
| 511.9.6.a | 7 | 13,271,112 | 13,297,315 | `mitml` (4 slices summed); accepted count = MacWilliams |
| 1715.287.3.a | 6 | 49,405 | 49,416 | `mitml` (4 slices) |
| 1675.373.3.a | 4 | 792,819 | 792,819 | `mitml`; = MacWilliams |
| 1676.372.3.a | 4 | 776,378 | 776,378 | `mitml`; = MacWilliams |
| 1683.365.3.a | 4 | 712,803 | 712,803 | `mitml` |
| 177.1.7.a | 9 | 2,172,877 | same | `mitml` (two seeds) + trellis |
| 185.1.7.a | 9 | 2,245,345 | same | `mitml` + trellis |
| 189.1.7.a | 9 | 2,286,315 | same | `mitml` + trellis |
| 271.1.7.a | 11 | 106,552,995 | same | trellis, two orders |
| 279.1.7.a | 11 | 109,958,991 | same | trellis, two orders |
| 283.1.7.a | 11 | 111,884,581 | same | trellis, two orders |
| 401.1.6.a | 13 | 6,958,671,715 | same | trellis, two orders |
| San José [[290,3,8]] sj_m5_L30_deg7_P1 | 8 | 14,412 | 50,472 | `mitml` |
| 27 d = 6 rows, 255.3 to 255.6 (d = 7), 901.123.6.a | | as in `A_d_counts.json` | | pilot kernel + `mitml` |

On every doubled row the harmless count at w = d is 0, so every accepted fault of weight d is harmful there.

## What the prepared jobs add

- **t0** (debug, ≤ 8 SU): builds everything on a compute node and reruns the brute-force tests. It re-counts 935's A_7 = 1,883 on 32 slices, times `sjfast` at bound 12, and runs a tropidist smoke test.
- **j1** (128 cores, expected 25 to 35 SU, cap 96) runs `mitml` counts on:
  - A_7 of 931, 932, 933, 936, 937 and 988, with a recount of the three [[930,94,7]] circuits as a check;
  - the 998 weight-7 sweep;
  - A_8 of 742, 954, 955, 959, 998 and 512.84 (954 and 955 have only their 4-flat counts today);
  - the 756 weight-8 sweep;
  - a recount of 512.39.
- **j2** (3 to 6 SU): tropidist threshold 6 on 931 and 932.
- **j7** (5 to 8 SU): A_8 of the seven other undominated San José records at bound 8, and weight-8 sweeps of the seven at bound 9, which would make those exact by the kernel.
- **j8** (3 to 5 SU): A_13 of 417.1.6.a by the trellis (cut rank 27, 30 GB).
- **j3** (expected 10 to 15 SU, cap 64): GF(256) San José faults at bound 13 (P = 52) and bound 14 (P = 51).
  - The model predicts 5 × 10^11 sets for bound 13 (seconds on 128 cores), 6 × 10^12 for bound 14 (minutes), 7 × 10^13 for bound 15 (about 40 minutes, the optional **j5**, about 85 SU) and 9 × 10^14 for bound 16 (about 8 h, not prepared).
  - The model expects about 2 × 10^8 faults at bound 13. The sparse search's 3.8 × 10^11 trials expected about 0.8 hits, so its miss is consistent with that.
- The kernel route to A_11 (14 SU per row) was dropped, because the trellis gave those counts on the laptop.

## Negatives and limits

- A tabu local search for San José faults (`sjwit/sjls.c`) found nothing at bounds 10 and 11 in 20 s each. `sjfast` needs under 5 s there.
- Annealing did not get below these cut ranks, which are search results, not lower bounds:
  - the 79-column blocks of 599: 29 (four 50-s seeds);
  - 599 as a whole: 30 (about a million moves of `cutsa`);
  - 761's 101-column block: 41.
- 441.1.6.a's best order has cut rank 31. That is too wide for the counting trellis at weight 13, so its A_d stays open. I did not compute orders for 559 or 575.

## Files

- Export scripts `rows.py` and `sjrows.py` write `data/rows/` (columns with SHA-256).
- Programs:
  - `mitml/`, `trellis/` and `sjwit/`;
  - `flat512.py`, `cutrank.py`, `doubled_order.py`, `order_polish.py`, `cutsa.c`, `cutsa_run.py` and `dp_perm.py`;
  - `tdirect.py`, a path-agnostic copy of the plan's, and `guard.py` with MAX_SLOTS = 0.
- Jobs are in `jobs/`, with the push, submit and pull scripts in `zaratan/`.
- Raw records in `data/`:
  - `counts.jsonl`, `mitml_runs.jsonl` and `validation.jsonl`;
  - `trellis_counts.jsonl`;
  - `flat512.json`, `macwilliams_511.json` and `macwilliams_d4.json`;
  - `witness_998.json`;
  - `dp_perm.jsonl` and `dp_records/`;
  - `sjfast_laptop.jsonl`, `slices/` and `orders/`.
- `SU_LEDGER.md` lists the jobs and their costs.
- Everything is under `/Users/shubhamjain/Documents/IBM internship/Shraddha (Magic states)/magic-state-factory-research/research/search2/distances/`.

## Results table

| row or circuit | before | now | evidence | status |
|---|---|---|---|---|
| 599.1.6.a | d ≥ 15 by theorem, witness 15, DP out of reach | **d = 15 exact** | DP on a cut-rank-30 order + theorem + witness | two tools |
| 988.36.6.a | 7, floor tropidist only | **d = 7 exact** | `mitml` 1 to 6 + tropidist 6 + witness | two tools |
| 998.26.6.a | ≥ 8, tropidist only, no witness | **d = 8 exact** | tropidist 7 + `mitml` witness at 8; `mitml` 1 to 6 | floor at weight 7 one tool (j1) |
| 935.89.6.a, 936.88.6.a | ≥ 7 by certificate | **d = 7 exact** | pilot kernel 1 to 6 + tropidist 6 + witness | two tools |
| 931, 932 (lift) | kernel only | d = 7, two implementations of the kernel | `mitml` 1 to 6 + witness | tropidist pending (j2) |
| 177, 185, 189 | exact | third method | `mitml` 1 to 8; trellis | |
| 271, 279, 283, 401 | exact | additional method | counting trellis | |
| 511.9.6.a | exact | search-free floor | MacWilliams | |
| A_d: 13 rows + one San José record | null | exact (table above) | `mitml`, trellis, MacWilliams, flat count | |
| 31 first-round kernel counts | one implementation | two | `mitml` | |
| 756.32.6.a | theorem 9 + fault | unchanged | weight-8 sweep prepared (j1) | |
| GF(256) San José, d = 13 to 16 | theorem only | unchanged | `sjfast` prepared (j3, j5) | |

**SU used: 0.** Zaratan was unreachable all session. Prepared work: 50 to 75 SU, plus about 85 SU optional.
