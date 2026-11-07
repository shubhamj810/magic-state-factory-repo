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
| `evidence/mitml_sweeps.jsonl` | the runs made here on 7 November 2026: weights 1 to 6 of the lift search's `[[930,94,7]]` (three circuits), `[[931,93,7]]`, `[[932,92,7]]` and `[[933,91,7]]`, weights 1 to 7 of `[[954,70,8]]` and `[[955,69,8]]`, weights 1 to 6 of the four weighted Reed–Muller rows of the second round (`[[1842,206,7]]`, `[[1845,203,7]]`, `[[1893,155,8]]`, `[[1894,154,8]]`), and mitml's counts of weight 7 of the three `[[930,94,7]]` circuits, which agree with the plan kernel's |
| `evidence/research/` | counts the research made on Zaratan, copied from the research branch at `1300c55`: the plan kernel's weight-7 counts of the three `[[930,94,7]]` circuits and its tropidist runs (`lift_counts.jsonl`, `lift_tropidist.jsonl`), and the Plücker count of the CCZ frame's weight-16 faults (`plucker_count.c`, `sets_q4.txt`, `plucker_q4_slices.jsonl`), with the construction objects and research digests that bind them (`native_digests.json`) |
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
