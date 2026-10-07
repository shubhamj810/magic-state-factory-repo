# Classification

Turns a factory's raw gate list into the numbers and labels that appear in `outputs/*.csv`:
`degree`, `essential_dim`, `t_count`, and a qubit-indexed `decomposition` string. Adapted from the
classification code in the `sj-magic-state-factory-searches` companion repository (that project's
`l=3`-only distance-3 extension of this one): `tcount.py` and `degree.py` are copied verbatim;
`classify.py` generalizes that repo's `audit_flag2.py` from `l=3`-only to any level.

## Why a dedicated classifier

A factory's output is a diagonal state defined only up to the CNOT frame of its output qubits: a
monomial of size `r` is genuine (not absorbable into free Cliffords) only if its coefficient is
nonzero mod `2^r`, not merely nonzero, and not merely odd. Both weaker tests give wrong answers: a
naive "coefficient ≠ 0" test misreports Clifford states as having real content, and a naive
"coefficient is odd" test misclassifies the real `[[4,2,2]]` Iceberg code as Clifford (its genuine
`CZ` coefficient is 2, even but nonzero mod 4). Getting this right requires minimizing over every
output CNOT frame (`GL(k,2)`), not just reading off the identity frame.

## Files

| file | role |
|---|---|
| `tcount.py` | Exact minimal T-count via the Amy–Mosca / Reed–Muller minimum-weight-coset decoder. Given the deposited phase polynomial, finds the true minimum T-gate count, correctly identifying that different gate strings can be the same resource (`T1 T2 CS12` is Clifford-equivalent to a single `T`). Self-tested. Only defined at `l=3`; only valid to `k≤6` (packs `2^k-1` bits into a `uint64`, per its own docstring; `classify.py` guards the `k=7` overflow rather than crashing). |
| `degree.py` | The general-`l`, brute-force `GL(k,2)`-frame degree reduction `classify.py` builds on (kept for reference; `classify.py` reimplements the same idea with the qubit-tracking needed for `decomposition`, adapted from `audit_flag2.py`). |
| `metrics.py` | A caching/practical-budget wrapper around `degree.py` from the companion repo (kept for reference; not used directly by `classify.py`, which has its own budget, below). |
| `classify.py` | The classifier both catalogue builders call: `classify.classify(Gf, cf, O, l)` → `dict(degree, essential_dim, degree_note, t_count, t_count_note, decomposition)`. |
| `quirk.py` | Renders a gate list as a clickable [Quirk](https://algassert.com/quirk) circuit URL (CNOT-ladder-into-one-phase-gate encoding, no ancillas). Verified against the target diagonal unitary by direct simulation; see its module docstring. |
| `export_circuit.py` | CLI: reconstructs one catalogue row's explicit circuit as a binary matrix and prints its classification, an independent check that the two agree. |

## `classify.classify(Gf, cf, O, l)`

`Gf`, `cf`: the factory's gates as `(frozenset(qubit support), ±1 coefficient)` pairs. `O`: the
output qubit indices. Returns:

- `degree`, `essential_dim`: minimized `(essential_dim, degree)` over `GL(k,2)`. Exact for `k≤4`
  (`|GL(4,2)|=20,160`); a documented upper bound from a bounded random-frame search for `k≥5`
  (can only overstate, never understate, both numbers). `degree_note` carries that caveat as text
  when it applies; the catalogue CSVs don't include it as its own column, since the exact/upper-bound
  distinction only ever affects `k≥5` rows and is documented once, here, rather than per row.
- `t_count`: the exact answer from `tcount.py`, only at `l=3` and `k≤6` (`t_count_note` explains
  why otherwise; this column doesn't exist at all in the `l=2`/`l=4` catalogues, where it's never
  defined).
- `decomposition`: one term per genuine monomial found in the best frame, named by size and the
  specific qubits it acts on there, e.g. `CS01+CS02` (one 3-qubit essential block, sharing qubit
  `0`) versus `CS01+CS23` (two independent 2-qubit blocks). More specific than an aggregate count
  like `2×CS`, which can't distinguish those two cases. Qubit labels are positions in the reduced
  frame (0-indexed, renumbered among the qubits that survive), not necessarily the original
  circuit's physical output wires; recovering the physical circuit for a row is what
  `export_circuit.py` is for.

The `GL(k,2)` sampling budget for `k≥5` is set low in `classify.py` (4,000 frames, not
`audit_flag2.py`'s original 60,000) for practicality: sweeping the ~150 `k≥6` rows in the two-group
catalogue at 60,000 samples each was projected to take over an hour; at 4,000 it takes minutes, and
every anchor case checked against `audit_flag2.py`'s own reported numbers, including all five
SAT-only targets in `outputs/README.md`, still matches exactly at this budget.

## Usage

```
python3 classification/export_circuit.py two-group --l 3 --n 4 --k 2 --s_total 1 --s_O 1
python3 classification/export_circuit.py symfree   --l 3 --parts 3,2 --checks 2
```

Each prints the gate list, the circuit as a 0/1 matrix (rows = wires, columns = gates, the same
column convention as the `sj-magic-state-factory-searches` companion repo's `master_catalog`
catalogue), and its classification.
