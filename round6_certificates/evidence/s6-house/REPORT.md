# s6-house: exact A_d for the 40 rows with 127 ≤ n < 500, and tropidist on 406, 448 and 490

*Lead note (9 November 2026).* The agent could not write this file, so the lead saved it from the agent's handback. The text below is the agent's. The lead's checks are in `lead/CHECKS.md`, section "s6-house". `data/lists_regen/` (61 MB) duplicates `catalogue/stage3/data/lists/` and is not to be committed; nor is `data/lists/` (51 MB).

## Summary

- **37 of the 40 rows now have an A_d that two programs agree on, each run on the row itself.** These counts can go into the catalogue under the usual rule.
- **410.2.11.a and 441.1.13.a** each rest on a counting theorem for doubled factories. Every ingredient of the theorem is counted by two programs, and the theorem reproduces 9 counts that were made independently.
- **462.4.9.a** has one program only. mitml counts A_9 = 3,140 and lists every set, and each listed set is re-checked by its own XOR, which proves A_9 ≥ 3,140. No second program reaches it: the trellis cut rank is 52, the MacWilliams ranks are 48 and 52, the plan kernel stops at w ≤ 8, and mydist at w ≤ 7 plus fixed columns.
- **tropidist (task 2) is done.** On 406.3.8.a, 448.7.8.a and 490.11.8.a it gives "K = 7 exhausted, K = 8 found". Each needed under 3 s of search with task depth 2, the depth-3 table and 64 threads, and every witness was re-checked by faultcore and by its own XOR.

Nothing in the catalogue, factory-search-repo or tropidist-src was changed, and nothing was committed. 33.05 SU of the 60 SU cap were used, and no s6-house job is left on Zaratan. Laptop jobs ran through `guard.py` (MAX_SLOTS = 1, nice 19, one thread, 3 GB) after a `pmset -g therm` check, with no warning.

## 1. Counting method

For d ≤ 8 the pair is mitml in list mode and the plan kernel in count mode.
- mitml is `round2_certificates/evidence/distances/mitml/mitml.c`, unchanged (sha256 79c7eeb9…). Each listed set is re-checked by `count_weight.check_list` (own XOR, distinct sets).
- The plan kernel is `research/plan/mitm/mitm.c`, unchanged (e0d4de7e…), the second program of the round-2 counts. It partitions by a hash of the full syndrome, where mitml uses linear keys, and it passed 1,397 brute-force cases here, including w = 8.
- Both the harmful and the accepted counts must agree.
- On 218, 221, 222, 250 and 280, MacWilliams also agrees as a third program (`code/wdist/wdist.c` lists every word of the span; the Krawtchouk sums are exact).

The d = 9 and 10 doubled rows (270, 318, 451, 459) each have three methods: mitml count on Zaratan; the counting trellis (`trellis_count.c`, unchanged) on column orders annealed with cutsa, which brought the cut ranks down to 17, 15, 21 and 15 from 26 to 56; and the doubling count of section 2. The trellis also gives A_w = 0 for every w < d on these four rows, an independent proof of their distances.

## 2. The doubling count (410 and 441 rest on it)

**The rows are the doubling map applied to the rows their provenance names.** `code/dbl/rebuild.py` rebuilds s4-d8's five rows with s4-d8's own builder from the catalogue's inner rows; the sorted columns are identical to the catalogue's. `code/dbl/rebuild_ja2.py` checks the Jain–Albert and Gong rows 177, 189, 271, 283, 401 and 441: their check spans and full spans equal those of `dbl.double` applied to the inner row. `code/dbl/wirematch.py` finds the wire permutation that carries JA-441 onto catalogue row 441.1.13.a.

**Theorem.** Take the doubled factory on X1 | X2 | Y with outputs (M_i, M_i, L_i) and checks (s, s, 0), (0, 0, c) and (0, M_i, L_i). For a fault (e1, e2, e3) put u = e1 ⊕ e2, g = e2 ∩ u and e′ = e2 ∖ u. The map (e1, e2) ↦ (u, g, e′) is a bijection, and the weight is |u| + 2|e′| + |e3|. The syndrome conditions read straight off the check rows: u ∈ S^⊥ (rows (s, s, 0)); C_t e3 = 0 (rows (0, 0, c)); M g + M e′ = L e3 (rows (0, M_i, L_i)). The flip on output i is M_i·(e1 ⊕ e2) + L_i·e3, so the fault is harmful exactly when Mu + Le3 ≠ 0. Since M x depends only on the parity of x on each block, A_w is a finite sum: a block-by-block DP over u, g and e′, multiplied by the inner counts Inner(w3, v) of sets e3 of size w3 that pass the inner checks and flip the pattern v. The program stops if it needs an inner value nobody supplied (`code/dblformula.py`).

**Ingredients.**
- Block codes: for the S^⊥ codes of Gong41, QR47 and Gong65 every word was listed, agreeing with MacWilliams from S. The least odd weights are 9, 11 and 13, with 697, 4,324 and 7,990 words.
- QR79: no word of weight 1 to 14, because the catalogue's `min_distance.py` proves d = 16 for the extended code.
- Inner rows: each inner row's sets are split by flip pattern with two programs (mitml's list, and a second count on derived rows that keep one output, by plan kernel or MacWilliams).
- 222.2.8.a: at w = 8 all 223 sets flip both outputs; at w = 9, 5,660 sets flip output 0 only and 5,660 flip output 1 only.

**Validation.** The theorem reproduces exactly 177 (2,172,877), 189 (2,286,315), 271 (106,552,995), 283 (111,884,581) and 401 (6,958,671,715), which the catalogue got by mitml and the trellis, and 318, 451, 459 and 270 against mitml and the trellis. For 271, 283 and 401, whose catalogue counts come from the trellis alone, this is the first second method.

**Results.** A_11(410.2.11.a) = 2·2^10·4,324 + 47·(5,660 + 5,660) = **9,387,592**, with A_w = 0 for w ≤ 10, which agrees with the Zaratan sweep. A_13(441.1.13.a) = 79·A_11(283.1.11.a) = **8,838,881,899**.

## 3. Compact certificates for 348, 452, 470 (and the other big lists)

**(a) Re-run recipe.** `code/regen.py` uses `count_weight`'s own problem file and build, then runs `mitml FILE W --list --parts 8`. It reproduced the stored raw-list SHA-256 byte for byte in 15 to 34 s (348: c1ee30a6…, 470: 4a534a0b…, 452: c4a19f48…). So the hash and the command can be stored instead of the 11 to 42 MB list. A reader who re-runs the command and re-checks every set by its own XOR has a proof of A_d ≥ count, independent of mitml's correctness.

**(b) Slice certificate.** `code/slicecert.py` writes `data/certs/LABEL_wW.json` (9 to 15 KB, 4.6 to 6.6 KB gzipped) with, per smallest column index, the count and a 16-hex hash of the slice's canonical text; the SHA-256 of the canonical list; and the degree of every column. Any slice can be recounted independently with mydist, taking the fixed column F = {i} and the pool of columns above i (`code/slicecheck.py`). On 348, slices 0, 100, 200, 250, 300 and 340 agreed (20 s for slice 0, well under a second for the high slices). This bounds the completeness of each slice a reader checks, and of the whole count only if all slices are checked, which costs about one full mydist run (25 min for 348, 2 h for 470). Certificates were also made for the other lists over 5 MB: 255.21.7.a (11 MB), 382.63.6.a (40 MB), 342.45.6.a (40 MB), 382.21.8.a (51 MB) and 256.20.8.a (347 MB, kept on Zaratan only).

**(c) Contraction identity (theorem plus checks).** A paired-column contraction keeps the row space on {v_a = v_b} and deletes columns a and b. Its harmful w-sets are the sum's harmful w-sets that avoid a and b, plus its harmful (w+2)-sets that contain both, because E is accepted after contraction exactly when E or E ∪ {a, b} is accepted before. In a sum of blocks with no zero column and no two equal check parts, every cross set has weight at least d + 3, so A_d = A_d(P1) − deg_P1(a) + A_d(P2) − deg_P2(b). The degrees agree between the list tally and mydist with a fixed column, and the rows are rebuilt exactly from the catalogue parents with s4-csum's `fac.py`. All three identities hold:
- 348.22.7.a: 48,645 − 3,875 + 856,035 − 23,499 = 877,306
- 452.66.6.a: 37,632 − 3,136 + 2,456,307 − 38,535 = 2,452,268
- 470.28.7.a: 973 − 32 + 856,035 − 23,499 = 833,477

(c) moves completeness onto the parents' counts. The parents are two-program counts, but 255.21.7.a's and 382.63.6.a's own lists are large too. The proposal is (a) plus (b) in the repository, with (c) as a cross-check.

## 4. Out of reach, with measured cost

- **410.2.11.a, mitml at w = 11.** Three timed slices of 4,096 average 71 s, so about 81 core-hours on the laptop; Zaratan cores ran these kernels 1.2 to 3 times slower, well over the cap. The trellis cut rank is at least 38, because the inner row 222.2.8.a stays at full rank 38.
- **441.1.13.a.** mitml supports w ≤ 12 only. The trellis on the matched order has cut rank 29: two arrays of 2^29 × 14 counters, 120 GB, about 1.2 h on Zaratan, about 38 SU. Not run.
- **462.4.9.a.** The mitml count cost 16,552 core-s (4.84 SU) and the list another 4.95 SU. A second program is out of reach.

## Files

In `research/search2/s6-house/`: `data/results.json` (per row: SHA-256, A_d, status, and every program with its record file); records in `data/counts.jsonl`, `data/zaratan/counts*.jsonl`, `data/macw.jsonl`, `data/trellis.jsonl`, `data/orders/`, `data/doubling_counts.json`, `data/dblspec/`, `data/blockw_*.json`, `data/flipsplit.jsonl`, `data/zaratan/t2/`, `data/contraction.jsonl`, `data/degrees.jsonl`, `data/certs/`, `data/regen.jsonl` and `data/zaratan/tropidist.jsonl`; code in `code/`, job scripts in `jobs/`, the ledger in `SU_LEDGER.md`. Two driver bugs cost 0.03 SU and part of t6; both are fixed and noted in the ledger.

## Results

| row | A_d | programs that agree | tropidist |
|---|---|---|---|
| 176.1.8.a | 68,229 | mitml + plan kernel | |
| 218.5.7.a | 360 | mitml + plan kernel + MacWilliams | |
| 221.2.8.a | 642 | mitml + plan kernel + MacWilliams | |
| 222.2.8.a | 223 | mitml + plan kernel + MacWilliams | |
| 250.3.7.a | 4,933 | mitml + plan kernel + MacWilliams | |
| 255.21.7.a | 856,035 | mitml + plan kernel | |
| 256.20.8.a | 27,393,120 | mitml + plan kernel | |
| 270.1.10.a | 3,206,763 | mitml + trellis + doubling count | |
| 280.6.7.a | 13,334 | mitml + plan kernel + MacWilliams | |
| 318.2.9.a | 4,288,272 | mitml + trellis + doubling count | |
| 333.9.7.a | 578 | mitml + plan kernel | |
| 341.11.7.a | 1,705 | mitml + plan kernel | |
| 342.45.6.a | 2,638,317 | mitml + plan kernel | |
| 348.22.7.a | 877,306 | mitml + mydist (8 Nov) + contraction identity | |
| 359.13.6.a | 5,077 | mitml + plan kernel | |
| 364.18.6.a | 768 | mitml + plan kernel | |
| 371.11.7.a | 416 | mitml + plan kernel | |
| 378.12.6.a | 2,251 | mitml + plan kernel | |
| 381.24.7.a | 195,834 | mitml + plan kernel | |
| 382.21.8.a | 3,554,730 | mitml + plan kernel | |
| 382.63.6.a | 2,456,307 | mitml + plan kernel | |
| 392.8.7.a | 2,044 | mitml + plan kernel | |
| 406.3.8.a | 1,464 | mitml + plan kernel | K = 7 exhausted, K = 8 found |
| 410.2.11.a | 9,387,592 | doubling count only (theorem, ingredients two-program) | |
| 416.16.6.a | 1,853 | mitml + plan kernel | |
| 420.16.6.a | 4,798 | mitml + plan kernel | |
| 434.12.7.a | 4,523 | mitml + plan kernel | |
| 441.1.13.a | 8,838,881,899 | doubling count only (theorem, ingredients two-program) | |
| 448.7.8.a | 4,151 | mitml + plan kernel | K = 7 exhausted, K = 8 found |
| 451.3.9.a | 2,352,334 | mitml + trellis + doubling count | |
| 452.66.6.a | 2,452,268 | mitml + mydist (8 Nov) + contraction identity | |
| 459.2.9.a | 2,356,352 | mitml + trellis + doubling count | |
| 462.20.6.a | 8,401 | mitml + plan kernel | |
| 462.4.9.a | 3,140 | mitml only (count + re-checked list) | |
| 466.70.6.a | 103,540 | mitml + plan kernel | |
| 470.28.7.a | 833,477 | mitml + mydist (8 Nov) + contraction identity | |
| 476.15.7.a | 8,976 | mitml + plan kernel | |
| 476.16.7.a | 8,976 | mitml + plan kernel | |
| 480.32.6.a | 17,360 | mitml + plan kernel | |
| 490.11.8.a | 8,965 | mitml + plan kernel | K = 7 exhausted, K = 8 found |

**SU used: 33.05 of 60.**
