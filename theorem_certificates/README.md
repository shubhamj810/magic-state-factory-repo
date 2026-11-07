# Distances from theorems checked on the columns

Two families in the catalogue have a distance theorem whose hypotheses can be
read off the circuit itself. This folder applies each theorem to the
circuits the catalogue holds or imports, checks its hypotheses on the
columns as the catalogue stores them, and records the bound.

| file | what it is |
|---|---|
| `inputs.json` | the circuits: a name, the research file it came from, the construction object of [`master_catalog/constructions.py`](../master_catalog/constructions.py), and a fault at the bound where the research found one |
| `assemble.py` | runs the checks and writes `certificates.json`; `--check` compares |
| `certificates.json` | one record per circuit, bound to its columns by their SHA-256, with the bound the check proves and the fault where there is one |

**San José's theorem.** R. San-José, "Asymptotically good binary
triorthogonal codes and higher-level transversal gates", arXiv:2609.08203
(2026), builds a factory from an outer code over GF(2^m) that is punctured at
P coordinates and mapped to binary through an inner map. If the outer
code's dual has minimum distance delta, the factory has distance at least
delta − P. [`construction_sanjose.py`](../master_catalog/construction_sanjose.py)
states the proof in its docstring. Its `hypothesis_check` decodes the binary
columns back to field values, checks that the rows are the multiples of the
systematic and subcode vectors the proof uses, that every recovered vector
lies in the outer code and that they span it, and that the outer code's dual
distance is delta (distinct evaluation points and nonzero multipliers for a
generalised Reed–Solomon code, the Goppa bound for a curve). The bound it
proves is the one recorded. The catalogue's rows 742.36.8.a and 756.32.6.a
are such circuits, as are the San José rows imported on 2026-11-07.

**The CCZ frame theorem.** For m = 3q, the factory on all 2^m points of
F_2^m with the monomials of degree below q as checks and a family of q-sets
as outputs, split into triples that partition [m] and with no other three
members partitioning [m], has gate CCZ on those triples and distance exactly
2^q (research/search/parents/REPORT.md §1.2, proved in the docstring of
[`construction_rm.py`](../master_catalog/construction_rm.py)). `packing_check`
verifies the hypothesis on the family exhaustively, over every triple of
sets, and `frame_check` verifies from the columns that the circuit is the
frame of that family. The 16 points of a coordinate 4-flat are the fault of
weight 2^q.

```bash
.venv/bin/python theorem_certificates/assemble.py --check
```
