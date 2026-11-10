# Counts and distances from the round-6 housekeeping search

The round-6 search s6-house (9 November 2026) counted `A_d` on the 40
catalogue rows with `127 <= n < 500` whose `A_d` was null, and ran tropidist on
three rows whose distance rested on one program. This folder holds the
evidence the catalogue takes from it. It was assembled on 9 November 2026.

| file | what it is |
|---|---|
| `evidence/s6-house/` | copied unchanged from the research branch (`research/search2/s6-house/` at commit `b4f0910`): the report, the SU ledger, the run records in `data/` (`counts.jsonl`, `zaratan/counts*.jsonl`, `macw.jsonl`, `zaratan/macw.jsonl`, `trellis.jsonl` with the column orders in `orders/`, `regen.jsonl`, `contraction.jsonl`, `degrees.jsonl`, `doubling_counts.json` and `dblspec/`, `zaratan/tropidist.jsonl`, the slice certificates in `certs/`), its summary `results.json`, and the code that made them (`code/`) |
| `evidence/stage3/listed_counts_round4.jsonl` | the three `count_weight.py` records of 8 November 2026 for 348.22.7.a, 452.66.6.a and 470.28.7.a, copied from `research/search2/catalogue/stage3/data/lists/listed_counts.jsonl` (research commit `1f5ceee`) |
| `assemble.py` | writes the two files below from `evidence/`; `--check` compares |
| `coefficients.json` | exact counts of the harmful faults of weight `d`, one record per circuit and program |
| `certificates.json` | tropidist's lower bound `d >= 8` on 406.3.8.a, 448.7.8.a and 490.11.8.a, with the fault of weight 8 it found |

`assemble.py` writes a count only for a row that `results.json` calls
"accepted (two programs)", and takes every value from the raw run records,
not from `results.json`. Each program's count must equal the row's, and the
programs that count accepted faults must agree on those too. Each run must
name the stored columns by their SHA-256 (`constructions.digest`), and the
row's `n`, `k` and `N` must match. mitml, the plan kernel and the counting
trellis are the copies already in `round2_certificates/evidence/` (the
script checks their SHA-256 against the runs). The lists themselves are not
kept, as in round 2.

## The programs

* **mitml** (`round2_certificates/evidence/distances/mitml/mitml.c`), in list
  mode with every listed set re-checked by its own XOR, or in count mode on
  the UMD cluster Zaratan.
* **The plan's kernel** (`round2_certificates/evidence/plan/mitm/mitm.c`),
  which partitions by a hash of the full syndrome where mitml uses linear
  keys.
* **MacWilliams** (`evidence/s6-house/code/wdist/wdist.c`), which lists every
  word of the check span and of the full span; a third program on 218.5.7.a,
  221.2.8.a, 222.2.8.a, 250.3.7.a and 280.6.7.a.
* **The counting trellis**
  (`round2_certificates/evidence/distances/trellis/trellis_count.c`), run on
  column orders annealed to cut rank 15 to 21 on 270.1.10.a, 318.2.9.a,
  451.3.9.a and 459.2.9.a, where mitml counted on Zaratan. It also finds
  `A_w = 0` for every `w < d` on those four rows.
* **For 348.22.7.a, 452.66.6.a and 470.28.7.a**, the two programs are mitml in
  list mode and mydist, run by `round1_certificates/count_weight.py` on
  8 November 2026. Their lists (11 to 42 MB gzipped) are not committed. Each
  record gives the SHA-256 of the raw list, and
  `evidence/s6-house/code/regen.py` (the problem file and build of
  `round1_certificates/sweep.py`, then `mitml FILE W --list OUT --parts 8`)
  reproduced it byte for byte (`data/regen.jsonl`). The slice certificates
  in `data/certs/` let a reader recount any slice with mydist, and the
  contraction identity of the s6-house report, section 3(c), gives the same
  three counts from the parents' counts (`data/contraction.jsonl`).

## Left null

* **410.2.11.a** (`A_11 = 9,387,592`) and **441.1.13.a**
  (`A_13 = 8,838,881,899`) rest on s6-house's counting theorem for doubled
  factories alone (report, section 2). Its ingredients were counted by two
  programs and it reproduces nine counts made independently, but no program
  has counted these two rows, and the theorem has not been reviewed line by
  line. Their `A_d` stays null.
* **462.4.9.a** (`A_9 = 3,140`) was counted by mitml only; no second program
  reaches it. Its `A_d` stays null.

[`master_catalog/migrations/round6_evidence_2026_11_09.py`](../master_catalog/migrations/round6_evidence_2026_11_09.py)
writes the 37 counts and the three tropidist records into the rows.

```bash
.venv/bin/python round6_certificates/assemble.py --check
```
