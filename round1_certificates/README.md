# Evidence for the first research round's imports

The catalogue's own sweep (`verify_catalog.py`) proves only a floor of 6 at
`n ≈ 930` and of 3 above `n ≈ 1,100`. The circuits of the first research
round (6 to 7 November 2026) that the catalogue took in, as constructions of
the large file, carry their distance as a certificate, and this folder holds
the evidence that is not a theorem (for those, see
[`theorem_certificates/`](../theorem_certificates/README.md)).

| file | what it is |
|---|---|
| `sweep.py` | runs mitml, the meet-in-the-middle sweep of the second-round distance search (`round2_certificates/evidence/distances/mitml/mitml.c`, unchanged), on the columns `constructions.columns` builds, and appends the run to `evidence/mitml_sweeps.jsonl` |
| `evidence/mitml_sweeps.jsonl` | the runs made here on 7 November 2026: weights 1 to 6 of the lift search's `[[930,94,7]]` (three circuits), `[[931,93,7]]`, `[[932,92,7]]` and `[[933,91,7]]`, weights 1 to 7 of `[[954,70,8]]` and `[[955,69,8]]`, weights 1 to 6 of the four weighted Reed–Muller rows of the second round (`[[1842,206,7]]`, `[[1845,203,7]]`, `[[1893,155,8]]`, `[[1894,154,8]]`), and mitml's counts of weight 7 of the three `[[930,94,7]]` circuits, which agree with the plan kernel's; on 8 November, for the round-4 imports, weights 1 to 6 of s4-csum's three `d = 7` rows (`[[348,22,7]]`, `[[432,14,7]]`, `[[470,28,7]]`), weights 1 to 8 of s4-d8's `[[318,2,9]]`, `[[451,3,9]]` and `[[459,2,9]]`, and weights 1 to 9 of its `[[270,1,10]]` and `[[410,2,11]]`; for `[[410,2,11]]` also weights 1 to 10, run on the UMD cluster Zaratan by the research's `research/search2/lead/zaratan_s5/sweep_par.py`, which runs `sweep.py` unchanged with each weight's slices in parallel (record `s4-d8.410.2.11.zaratan`) |
| `evidence/research/` | counts the research made on Zaratan, copied from the research branch at `1300c55`: the plan kernel's weight-7 counts of the three `[[930,94,7]]` circuits and its tropidist runs (`lift_counts.jsonl`, `lift_tropidist.jsonl`), and the Plücker count of the CCZ frame's weight-16 faults (`plucker_count.c`, `sets_q4.txt`, `plucker_q4_slices.jsonl`), with the construction objects and research digests that bind them (`native_digests.json`) |
| `count_weight.py` | counts the harmful faults of one weight of a stored circuit with two programs that share no code: mitml in list mode (every listed set re-checked by the script's own XOR, the list kept in `evidence/lists/`) and the research's small-review agent's `mydist.py`, copied unchanged into `evidence/small_review/` (research commit 82a5c7e); both counts must agree, and the run is appended to `evidence/listed_counts.jsonl` |
| `evidence/listed_counts.jsonl`, `evidence/lists/` | the runs made here on 7 November 2026: weight 7 of both `[[217,7,7]]` circuits (small-d7's 9c3da8b2, A_7 = 1,034, and small-cyc's 69bae4f9, A_7 = 973), weight 6 of `[[510,84,6]]` (A_6 = 10,795), and, on 8 November, weight 7 of the twelve `d = 7` rows of the round-3 search s3-d7, from `154.2.7.a` to `319.9.7.a`, and the round-4 counts of `424.22.6.a` (A_6 = 1,224), `432.14.7.a` (A_7 = 1,877) and `455.23.6.a` (A_6 = 1,162). Three more round-4 counts agree between the two programs but are not kept here, because their lists are over 5 MB gzipped: `348.22.7.a` (A_7 = 877,306), `452.66.6.a` (A_6 = 2,452,268) and `470.28.7.a` (A_7 = 833,477). Their lists and records are in the research worktree, `research/search2/catalogue/stage3/data/lists/`, and those rows store `A_d = null` |
| `evidence/small_cyc_217_7_7.json` | small-cyc's 69bae4f9 claim, copied from the research branch (commit 27ac40e) so that `master_catalog/migrations/store_217_7_7_2026_11_07.py` can be re-run here |
| `assemble.py` | writes the two files below; `--check` compares |
| `certificates.json` | lower bounds on the distance, one per sweep |
| `coefficients.json` | exact counts of the harmful faults of one weight |

A sweep gives the lower bound `u + 1` when every weight 1 to `u` completed
over all partitions with no harmful fault. The research's counts were made
on its own column order. A count does not depend on the order, and
`assemble.py` checks that the research's columns are the construction's in
its native order before it binds the count to the stored, sorted columns.
For the CCZ frame it checks instead that `sets_q4.txt` is the construction's
family of 165 sets and that the 64 slices cover all 13,910,980,083
four-dimensional subspaces of F_2^12; each subspace with a nonzero output
minor gives 2^8 harmful cosets.

The tropidist runs of the lift search name a circuit only by a job tag, so
they are kept as corroboration and are not cited by any row.

```bash
.venv/bin/python round1_certificates/assemble.py --check
```
