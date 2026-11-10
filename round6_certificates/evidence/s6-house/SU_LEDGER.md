# Zaratan SU ledger, s6-house (9 November 2026)

Charge = max(cores, mem / 4 GB) × hours, read back with `sacct`. Account vva-prj-aac, constraint epyc_7763. Cap 60 SU.

| job id | name | partition | allocation | elapsed | charge (SU) | purpose and result |
|---|---|---|---|---|---|---|
| 23960615 | s6-house-t0 | debug | 32 cores, 120G (charged as 32) | 00:00:53 | 0.47 | build and test: mitml count of 318.2.9.a at w = 9 gives 4,288,272 (s4-d8's laptop census); tropidist probe of 406.3.8.a at K = 7 (16 anchors, depth-3 table) exhausted in 0.1 s; the 218.5.7.a test stopped on a path bug in my driver (fixed) |
| 23960722 | s6-house-t1 | debug | 64 cores, 200G (charged as 64) | 00:08:29 | 9.05 | mitml counts: A_9 of 459.2.9.a = 2,356,352 (13,286 core-s), A_9 of 451.3.9.a = 2,352,334 (11,344 core-s), A_10 of 270.1.10.a = 3,206,763 (3,611 core-s); tropidist (task depth 2, depth-3 table, 64 threads): K = 7 exhausted and K = 8 found on 406.3.8.a, 490.11.8.a and 448.7.8.a, each in under 3 s of search |
| 23961061 | s6-house-t2 | debug | 32 cores, 120G (charged as 32) | 00:08:18 | 4.43 | 222.2.8.a split by flipped outputs: weight 8, 223 sets, all flip both outputs (mitml list; plan kernel with one output kept gives 0 and 0); weight 9, 11,320 sets, 5,660 flip output 0 only and 5,660 output 1 only (mitml list; MacWilliams with one output kept agrees); MacWilliams as a third program: A_7 of 218.5.7.a = 360, A_8 of 221.2.8.a = 642, A_8 of 222.2.8.a = 223, A_7 of 280.6.7.a = 13,334, A_7 of 250.3.7.a = 4,933 (test, as on the laptop); cancelled during the rank-42 MacWilliams of 378.12.6.a, which is not needed |
| 23962041 | s6-house-t3 | debug | 64 cores, 120G (charged as 64) | 00:04:32 | 4.84 | mitml count of 462.4.9.a at w = 9: 3,140 harmful of 1,943,167 accepted (16,552 core-s); one program only |
| 23962157 | s6-house-t4 | debug | 1 core, 4G | 00:00:14 | 0.00 | test of the counting trellis on Zaratan: 451.3.9.a at W = 9 in the annealed order (cut rank 21) gives 2,352,334, 6.0 + 7.0 s (laptop 2.0 + 2.3 s) |
| 23962169 | s6-house-t5 | debug | 64 cores, 120G (charged as 64) | 00:04:38 | 4.95 | mitml --list of 462.4.9.a at w = 9 in 256 slices: the 3,140 harmful sets, each re-checked by its own XOR (a proof that A_9 >= 3,140); same program as t3, so still one program for the count |
| 23962866 | s6-house-t6 | debug | 32 cores, 128G (charged as 32) | 00:12:29 | 6.66 | the 20 rows the laptop queue had not reached, one process each (mitml --list, then the plan kernel): 18 agree (see the results table); for 382.21.8.a and 256.20.8.a mitml listed 3,554,730 and 27,393,120 sets, and the plan kernel's 8-slice runs stopped on its per-slice divisibility check (a driver bug, fixed in t7) |
| 23963210 | s6-house-t7 | debug | 16 cores, 60G (charged as 16) | 00:00:07 | 0.03 | stopped at once on a second driver bug (the plan kernel's error line has no timing field); cancelled |
| 23963239 | s6-house-t7b | debug | 16 cores, 64G (charged as 16) | 00:09:49 | 2.62 | sliced plan kernel checked on 218.5.7.a (360) and 221.2.8.a (642), then A_8 of 382.21.8.a = 3,554,730 and of 256.20.8.a = 27,393,120, equal to mitml's lists; slice certificates of 342.45.6.a, 382.21.8.a and 256.20.8.a |

Total: 33.05 SU of the 60 SU cap. No job of mine is left in the queue.
