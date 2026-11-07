# Distances and counts from the second research round

This folder holds the evidence behind distances and error coefficients that
the catalogue took from the second round of its own factory searches, run on
the night of 6 to 7 November 2026. It was assembled on 7 November 2026.

| file | what it is |
|---|---|
| `evidence/distances/` | the second-round distance search, copied unchanged from the research branch (`research/search2/distances/` at commit `2c3ce12`): its report, `results.jsonl`, the raw run records in `data/`, and the sources of the tools it wrote (`mitml/`, `trellis/`, `flat512.py`, `dp_perm.py`) |
| `evidence/plan/` | the plan's meet-in-the-middle kernel (`mitm/`), its runs on 935.89.6.a, 936.88.6.a and 1715.287.3.a, its counts (`A_d_counts.json`), the cached rows it read, and the research's run of this catalogue's own sweep on 1715.287.3.a (`own_sweep.py`, `own_sweeps.jsonl`), all from `research/plan/` at commit `9932b15` |
| `own_sweep.py`, `evidence/own_sweep_1715.json` | this catalogue's `faultcore.scan_weight`, unchanged, run here on 1715.287.3.a with the raised budget the research used |
| `assemble.py` | writes the two files below from `evidence/`, `--check` compares |
| `certificates.json` | lower bounds on the distance, one record per circuit and tool, and the faults the runs found |
| `coefficients.json` | exact counts of the harmful faults of one weight, one record per circuit and tool |

`assemble.py` binds every record to a catalogue row by the SHA-256 of the
row's columns (`constructions.digest`), the row being the one the research
named (its label then, which may now be a former label). It re-checks every
fault with `faultcore.Circuit.harmful` and by the XOR of the wire masks. A
lower bound is written only when every weight below it was swept completely
and no harmful fault was found. Where two tools counted the same circuit
they agree, or nothing is written.

## The tools

* **mitml**, a meet-in-the-middle sweep written in the second round from the
  plan's kernel. It keys the partial syndromes by random linear functionals,
  and it was tested against brute force on about 3,900 small problems.
* **The plan's kernel**, `research/plan/mitm/mitm.c`, the meet-in-the-middle
  kernel the zaratan certificates also use.
* **The counting trellis**, which counts `B_w(ker H) − B_w(ker [H;L])`, the
  definition `errorcoeff.py` uses, through a syndrome trellis. It shares no
  code with the other tools.
* **tropidist's dense DP** (B. Cheng, N. Guo and F. Pan, arXiv:2611.08247),
  run on 599.1.6.a with its columns permuted to an order of cut rank 30. The
  distance does not depend on the column order.
* **A literal count of 3-flats** on 512.39.6.a, whose harmful faults of
  weight 8 are the cosets of 3-dimensional subspaces.
* **This catalogue's own sweep** at a raised budget on 1715.287.3.a.

## What went into the catalogue

[`master_catalog/migrations/round2_evidence_2026_11_07.py`](../master_catalog/migrations/round2_evidence_2026_11_07.py)
writes the records into the rows.

* 935.89.7.a and 936.88.7.a were floors `d ≥ 7` proved by tropidist. The
  plan's kernel sweeps weights 1 to 6 clean on both, a second tool, and
  found the weight-7 faults `[0, 28, 165, 175, 254, 282, 927]` and
  `[0, 3, 117, 120, 448, 502, 934]`. Both rows are now exact at 7.
* 998.26.8.a was a floor `d ≥ 8` proved by tropidist at threshold 7. mitml
  found the weight-8 fault `[15, 64, 72, 245, 260, 307, 315, 323]`, so the
  row is exact at 8. Weight 7 still rests on tropidist alone; mitml swept
  only to weight 6.
* 599.1.15.a gets tropidist's dense DP as a second proof beside the doubling
  theorem, and 988.36.7.a mitml's sweep beside tropidist.
* 1715.287.3.a becomes 1715.287.6.a. Until now its `d = 6` rested on the
  gamma frontier release alone and sat beside the sweep's floor of 3. The
  plan's kernel and this catalogue's own sweep at a raised budget both find
  weights 1 to 5 clean, and mitml found the weight-6 fault
  `[0, 423, 572, 851, 998, 1433]`.
* The doubled transversal-T codes `177.1.9.a` to `401.1.13.a` get the
  trellis (and, for 177, 185 and 189, mitml) as further evidence.
* `A_d` is written, with `A_d_evidence`, on every exact row the file
  counts: 512.39.8.a (`A_8 = 50,397,952`), 511.9.7.a (`A_7 = 13,271,112`),
  1715.287.6.a (`A_6 = 49,405`), the three rows `1675.373.4.a`,
  `1676.372.4.a` and `1683.365.4.a` (`A_4`), the doubled codes 177, 185, 189
  (`A_9`), 271, 279, 283 (`A_11`) and 401 (`A_13`), and 31 rows at
  `d = 6` and 7 from 255.3.7.a to 912.112.6.a, each counted by mitml and by
  the plan's kernel. `verify_catalog.py`
  recounts `A_d` wherever `errorcoeff` reaches and otherwise checks the
  evidence record.

```bash
.venv/bin/python round2_certificates/assemble.py --check
.venv/bin/python master_catalog/migrations/round2_evidence_2026_11_07.py --dry-run
```
