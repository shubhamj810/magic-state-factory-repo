# Zaratan runs of the second round (7 November 2026, 05:25 to 06:30)

The ControlMaster came up at about 05:25 and stayed up until the end. Every connection used `ssh -o BatchMode=yes`, and no login was attempted. I ran the jobs the distances and packings agents had prepared. I also ran two lead items: the weight-7 sweep of the two d = 8 weighted rows, and a weight-6 second opinion on the two RM(4,13) rows of weighted2 (the coordinator's item 4). Thirteen jobs used **159.05 SU** of the 450 cap. All of them have ended, and nothing of mine is queued.

Every job type ran first on `debug` or as a short job, and I read its log before the full run. Charges come from `sacct` through `ledger.py` and are itemised in `SU_LEDGER.md`. Nothing was committed. Outside `zaratan2/` I wrote only into `../distances/data/zaratan/` and `../packings/data/zaratan/`. The catalogue repository, the import worktree, `factory-search-repo` and `tropidist-src` were not touched. Catalogue faultcore was imported read-only. The laptop ran only ssh, rsync, editing and checks of a few seconds.

## 1. Distances

After `zaratan/push.sh`, the smoke job t0 (23875674, debug, 2.64 SU) reproduced every reference value:
- brute force agreed on 1,345 (problem, weight) pairs;
- 255.3.7.a at w = 8 gave 3,011,805 accepted and 2,642,688 harmful;
- 901.123.6.a at w = 6 gave 2,781;
- A_7 of 935.89.6.a over 32 slices was 1,883, as the pilot kernel found;
- sjfast hit bound 12 in 5 of 16 seeds within 60 s;
- tropidist found 901.123.6.a's weight-6 fault.

Every witness was re-checked by `faultcore.Circuit.harmful` and by the literal XOR.

`zaratan/submit.sh full` then ran j1, j2, j3, j7 and j8, for 59.78 SU against the 50 to 75 expected. All other work was in by then and the worst case stayed under the cap, so I also ran the optional j5. It took 45 s and 1.60 SU against the 85 SU expected. Distances total 64.02 SU.

- **j2** (23875687, 2.38 SU). tropidist threshold 6 was exhausted over all anchors on [[931,93,7]] 83a91c80c5 (70.4 s, 64 threads) and on [[932,92,7]] 0f5a3a3102 (58.5 s). Both lift results now rest on two tools.
- **j1** (23875686, 25.92 SU). The weight-7 sweep of 998.26.6.a is clean, with 0 accepted sets. With tropidist's threshold 7 and the weight-8 fault [5, 60, 241, 245, 249, 303, 307, 311], d = 8 is exact by two tools.
- **j1, 756.32.6.a.** The weight-8 sweep is clean (757,782 accepted, 0 harmful). The kernel now covers weights 1 to 8, and with the stored fault of weight 9, d = 9 is exact by the kernel as well as by the theorem.
- **j1, counts.** Exact A_7 for 931, 932, 933, 936, 937 and 988. Exact A_8 for 742, 954, 955, 959, 998 and 512.84. The recounts of the three [[930,94,7]] circuits and of 512.39.6.a (50,397,952) equal the earlier counts. `assemble.py` asserts a single value per (row, weight), and the assertion held.
- **j7** (23875689, 9.00 SU). Exact A_8 for the eight San José bound-8 records. The weight-8 sweeps of the seven bound-9 records are clean (0 harmful, 280,137 to 675,291 harmless accepted sets). That checks the theorem bound at weight 8 only, because weights 1 to 7 were not swept here.
- **j8** (23875690, 1.04 SU). The counting trellis gives A_w = 0 for w < 13 and A_13 = 7,598,286,923 for 417.1.6.a, all accepted sets harmful (cut rank 27, 162 s, one column order). Its brute-force test passed on 200 problems first.
- **j3** (23875688, 21.44 SU). sjfast found faults at bound 13 (P = 52) after 14 s and at bound 14 (P = 51) after 589 s.
- **j5** (23876255, 1.60 SU). sjfast found a fault at bound 15 (P = 50) after 44 s. The model had predicted about 40 minutes.

I rebuilt the three San José faults on the laptop with `sjwit/sjinputs.py recheck`. All three are harmful by faultcore and by literal XOR, and their weights equal the bound. With San José's algebraic bound, three GF(256), L = 254 rows are now exact:
- [[4242,260,13]], digest 71363138e0c8efac…;
- [[4263,255,14]], digest e1742a3b6e0948ca…;
- [[4284,250,15]], digest cbc2ed65abfe8540….

The records are in `../distances/data/zaratan/sjfast_recheck.jsonl`.

`zaratan/pull.sh` brought everything into `../distances/data/zaratan/`. I could not write into the distances folder, so I ran a copy of its assembly. `zaratan2/assemble_distances.py` is `../distances/assemble.py` with three changes: it reads `../distances`, writes `zaratan2/distances_results.jsonl`, and also reads the pulled `trellis_counts.jsonl`. Before the pull its output was byte-identical to `../distances/results.jsonl`. It now gives 86 results instead of 60. All 27 Zaratan count records with a witness carry `faultcore_harmful: true` and `literal_harmful: true`. `mitml.py` asserts both before it writes a record, so the re-check did run. The lead may want to copy `distances_results.jsonl` over `../distances/results.jsonl`.

## 2. Weight-7 sweep of [[1893,155,8]] and [[1894,154,8]]

The 1893 row is `../distances/data/rows/w188c0f.json`. The 1894 row was missing from `distances/data/rows/`. I wrote `zaratan2/rows/wa6e304.json` in the same format from `../weighted/data/claimed_factories.json`, and its SHA-256 matches (a6e3040381…). Both rows have SW = 3, with r = 169 and 170.

The debug job t1 (23875679, 0.78 SU) built `mitml` on a compute node. `mitml.py test 100 5` agreed with brute force on 893 pairs. It reproduced the laptop result: w5d387e at w = 6 is clean, with 0 accepted sets over 32 slices, and the 3-sets tabulated total C(1842,3) = 1,039,944,080.

The coordinator's note was correct: `--slice 0 256 --mem-mb 2500` gives Q = 5, so the lead's slice was 1/32 of the sweep. My `sweep.sh` sets `--parts 12` and runs 4,096 slices, one partition each. `combine.py` declares a sweep complete only when:
- every slice is present with `complete == 1`, under one seed;
- the summed raw tallies are divisible by C(7,4);
- the 3-sets tabulated, summed over all slices, equal C(n,3), which shows that every partition was visited.

On debug, one slice took 7.4 s, so a row needs about 8.4 core-hours.

The full run j1 (23875729, 30.47 SU) did 1893 first:

| row | slices complete | 3-sets tabulated | accepted 7-sets | harmful | core-hours |
|---|---|---|---|---|---|
| [[1893,155,8]] 188c0f5df2… | 4,096 / 4,096 | 1,128,787,066 = C(1893,3) | 0 | 0 | 9.9 |
| [[1894,154,8]] a6e3040381… | 4,096 / 4,096 | 1,130,577,844 = C(1894,3) | 0 | 0 | 9.9 |

Neither row has any set of 7 columns with zero syndrome, harmful or not. No witness appeared, so nothing contradicts the theorem. The weight-7 floor of both rows now also rests on an exhaustive kernel sweep. The slices are in `zaratan2/out/`, and a second combine on the laptop gave the same result (`combined_laptop.jsonl`).

## 3. Packings, m = 12

`zaratan2/packings_push.sh` copied the code and group lists. The debug job (23875680, 0.38 SU) ran 16 groups for 60 s each and wrote valid records. Model building adds up to about 50 s per group. `small12.sh` (23875731, 30.29 SU) then ran all 303 groups of orders 2 to 10 for 800 s each, on 124 workers. The 55 hint was invariant under none of them.

No packing above 55 was found, so none reaches the bar of 59. The largest is 51 (SG6_2_4, FEASIBLE, bound 180). `check_packing.py` accepts it and all eight saved packings of size 50.
- 231 groups are OPTIMAL, with maximum 50. These include the three left open on the laptop: SG10_1_2 and SG10_2_2 (50 each) and SG9_1_2 (47).
- 7 groups hit the limit with bounds below 59, so they cannot reach the bar: SG2_1_1 (45), SG4_2_17 (45), SG4_2_18 (46), SG4_2_21 (42), SG4_2_26 (43), SG4_2_31 (29) and SG6_2_9 (45). The figure in parentheses is the solver bound.
- 65 groups remain unresolved, with incumbents of 36 to 51 and bounds of 94 to 302: SG2_1_2 to SG2_1_6; SG3_1_2, SG3_1_3, SG3_1_4; SG4_1_2, 4_1_3, 4_1_4, 4_1_5, 4_1_7, 4_1_8, 4_1_9; SG4_2_2, 4_2_3, 4_2_4, 4_2_5, 4_2_6, 4_2_8, 4_2_9, 4_2_10 to 4_2_16, 4_2_19, 4_2_20, 4_2_22 to 4_2_25, 4_2_27 to 4_2_30; SG5_1_2; SG6_1_2, 6_1_3, 6_1_4, 6_1_5, 6_1_7, 6_1_8, 6_1_10 to 6_1_13, 6_1_15, 6_1_16; SG6_2_2 to 6_2_8, 6_2_11, 6_2_12; SG8_2_2, SG8_2_3, SG8_3_2, SG8_3_3.

Results and logs are in `../packings/data/zaratan/`. I did not run `m15.sh`.

## 4. Weight 6 of [[7171,1021,7]] and [[7167,1025,7]] (coordinator's item 4)

`zaratan2/rm413_inputs.py` checks weighted2's `tmp/r7_1021_s1.bin` and `tmp/r7_1025_s11.bin`. Each column list hashes to its claimed digest (b57acec86f… and a7f8760693…). The syndrome words in each `.bin` equal those of the published columns, with 0 mismatches. The rows have r = 72 and 68.

The output word in these files is a random 64-bit projection (`rm413.write_mitml`). Weighted2's argument is that d ≥ 7 holds exactly when no 6 or fewer survivor syndromes sum to zero. So I ran count mode and required accepted == 0, which is the exact statement. Status mode, as you asked for it, would see only sets whose projected output is nonzero, and in a clean sweep both modes cost the same.

The timing job t2 (23875796, 0.21 SU) measured 3.35 s per slice at Q = 13, or 7.6 core-hours per row. The full run j2 (23875797):

| row | slices complete | 3-sets tabulated | accepted 6-sets | harmful |
|---|---|---|---|---|
| [[7171,1021,7]] b57acec86f… | 8,192 / 8,192 | 61,433,634,305 = C(7171,3) | 0 | 0 |
| [[7167,1025,7]] a7f8760693… | 8,192 / 8,192 | 61,330,873,855 = C(7167,3) | 0 | 0 |

Weight 6 is now clean by two tools on both rows: weighted2's `zs.c` and `mitml`.

This item cost 33.10 SU, over the roughly 20 SU you set. The sweeps took 4.6 min per row, as estimated. The extra cost came from `combine.py` reading 8,192 small files on Lustre, which took 3.5 min while the job held the whole node. The second combine then ran into the 15-minute limit, so sacct reports TIMEOUT. All 8,192 slices of that row were already written, and the log shows the sweep ended at 06:08:30. I pulled them and combined them on the laptop in 1 s. `combine.py` now reads each file once.

## Files

Everything is under `/Users/shubhamjain/Documents/IBM internship/Shraddha (Magic states)/magic-state-factory-research/research/search2/zaratan2/`:
- `push.sh`, `packings_push.sh` and `packings_pull.sh` move work to and from Zaratan.
- `jobs/` holds t1, j1, t2 and j2. `sweep.sh` runs the sliced count, and `combine.py` sums and checks it.
- `rm413_inputs.py` checks the item 4 inputs, and `rows/` holds the row files I made.
- `out/` holds all slice records, `combined.jsonl` (cluster) and `combined_laptop.jsonl`. `logs/` holds the Slurm logs.
- `assemble_distances.py` and `distances_results.jsonl` cover item 1.
- `ledger.py`, `my_jobs.txt` and `SU_LEDGER.md` hold the charges.
- `.gitignore` excludes the 39 MB of copied RM(4,13) rows, the copied kernel and `tmp/`.
- `out/` is 96 MB in 24,000 small files. You may want to archive it rather than commit it.

## Results table

| item | circuit | before | now | evidence | jobs | SU |
|---|---|---|---|---|---|---|
| 1 | 998.26.6.a | d = 8, floor at 7 by tropidist only | d = 8, two tools | mitml w7 clean (0 accepted), tropidist 7, fault at 8; A_8 = 70 | j1 | 25.92 |
| 1 | 756.32.6.a | theorem 9, fault 9, both tools clean to 7 | d = 9, kernel through weight 8 | mitml w8 clean (0 harmful) | j1 | in j1 |
| 1 | [[931,93,7]], [[932,92,7]] | two kernel implementations | d = 7, two tools | tropidist threshold 6 exhausted | j2 | 2.38 |
| 1 | A_7 of 931, 932, 933, 936, 937, 988 | null | 2,857; 2,450; 2,441; 1,784; 1,598; 400 | mitml count | j1 | in j1 |
| 1 | A_8 of 742, 954, 955, 959, 998, 512.84 | null or 4-flat count only | 331,891; 3,649; 3,328; 1,770; 70; 50,434,240 | mitml count | j1 | in j1 |
| 1 | A_8 of 8 San José bound-8 records | null | 1,575 to 202,355 | mitml count | j7 | 9.00 |
| 1 | 7 San José bound-9 records | theorem 9 + fault | w8 clean (kernel check of the bound at weight 8) | mitml w8 | j7 | in j7 |
| 1 | 417.1.6.a | d = 13 | A_13 = 7,598,286,923; A_w = 0 below 13 | counting trellis, one order | j8 | 1.04 |
| 1 | San José GF(256) [[4242,260,13]], [[4263,255,14]], [[4284,250,15]] | theorem only | exact 13, 14, 15 | theorem + fault at the bound, re-checked | j3, j5 | 23.04 |
| 1 | smoke test | | all reference values reproduced | | t0 | 2.64 |
| 2 | [[1893,155,8]], [[1894,154,8]] | w7 floor by theorem and two implementations | w7 exhaustive: 0 accepted 7-sets | mitml, 4,096 of 4,096 slices each | t1, j1 | 31.25 |
| 3 | m = 12 packings, 303 groups of order 2 to 10 | 221 run at 40 s, max 51 | max 51, none above 55; 238 settled below the bar, 65 open | CP-SAT 800 s each; packings re-checked | debug, small12 | 30.67 |
| 4 | [[7171,1021,7]], [[7167,1025,7]] | w6 by zs only | w6 by two tools: 0 accepted 6-sets | mitml, 8,192 of 8,192 slices each | t2, j2 | 33.10 |

**SU used: 159.05 of 450** (distances 64.02, weight-7 sweep 31.25, packings 30.67, RM(4,13) weight 6 33.10). No job of mine is queued or running.
