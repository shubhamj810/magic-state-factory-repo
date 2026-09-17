# Quotient-space classification of distance-≥3 factories, n≤38

Generated from the [`../classify.py`](../classify.py) runs stored in
[`../results/`](../results/). Current overview of this directory:
[`../README.md`](../README.md); the overview-level treatment is
[`../../../../theory/02_classification.md`](../../../../theory/02_classification.md).
The output-width ceiling is separately packaged in the checked-in
[`n38_k56_certificate.json`](../results/n38_k56_certificate.json);
see [`N38_K56_CERTIFICATE.md`](N38_K56_CERTIFICATE.md).

**Equivalence:** gates identified up to permutation of output qubits (S_k) acting on the (single, pair, triple) parity tensor; the GL(k,2) mod-2 class is annotated separately. **Scope:** reduced distance-≥3, k independent output rows taken in the quotient R(C)/C over the marked Nezami–Haah/KTA check parents.

## Validation

- All 74 representatives have an explicit witness: 73 from the quotient passes
  and the `[[31,5,3]]` witness from the automorphism-reduced `n=31` run
  (`hard_parent_n31.json`, also embedded in `n38_k56_certificate.json`).
  Independent parity, distinct-column and exact-distance verification: **PASS**.
- Every witness is stored **in its canonical output frame**, so the columns
  deposit exactly the gate string the row is filed under; `build_catalog.py`
  compares the two as strings, with no permutation allowed. (Earlier revisions
  stored whichever labelling the enumeration reached, so 25 of the 73 quotient
  witnesses agreed with their label only up to `S_k`. Both engines now apply the
  canonicalising permutation to the output qubits before writing the columns —
  a renaming of output wires, so `n`, `N`, every check parity and the distance
  are untouched.)
- Reference [[15,1,3]] gate `0`: reproduced (d=3)
- Reference [[28,2,3]] gate `0+1`: reproduced (d=3)
- Reference [[35,3,3]] gate `0+1+2`: reproduced (d=3)
- **CCZ** (`012`, k=3): absent for all n≤38 — the ≥39 lower bound rests on
  exactly this absence; the shipped certificate is
  [`../catalog/CLASSIFICATION_N38.md`](../catalog/CLASSIFICATION_N38.md)
- **n=31** (the 31-point F₂⁵ parent, dimV=11): classified **exhaustively** by GL(5,2) automorphism reduction (2047 quotient points → 5 orbits); no budget cap. It realises exactly one gate class per k (k=1..5) — the fully-symmetric all-degree-≤3 gate (punctured quantum Reed–Muller family). Independently audited (group order, orbit structure, compatibility/gate/distance invariance, and a second from-scratch clique enumerator through k=6): **PASS**, no completeness gap found.
- **k=5:** the only distance-≥3 k=5 factory at n≤38 is [[31,5,3]]
  (all-monomials gate), and its explicit circuit is now stored in the
  certificate. The proof partitions every parent by effective check rank:
  the complete `RM(3,7)` all-origin census closes rank `<= 7`, while all
  rank-`>= 8` parents have `dim V <= 4`. Thus n=32,35,36,38 host no k=5
  factory, and no k=6 factory exists anywhere in the window.

## Gate frontier (minimum n realising each gate class)

| k | gate (parity tensor, mod S_k) | min n | distance | GL(k,2) class |
|---|---|---|---|---|
| 1 | `0` | 15 | 3 | 2 |
| 2 | `0+01` | 28 | 3 | 2 |
| 2 | `0+1` | 28 | 3 | 6 |
| 2 | `0+1+01` | 31 | 3 | 14 |
| 2 | `01` | 35 | 3 | 2 |
| 3 | `0+1+2+01+02+12+012` | 31 | 3 | 254 |
| 3 | `0+01+02+12+012` | 35 | 3 | 14 |
| 3 | `0+01+12` | 35 | 3 | 30 |
| 3 | `0+1+01+02+012` | 35 | 3 | 62 |
| 3 | `0+1+2` | 35 | 3 | 60 |
| 3 | `0+1+2+01+02` | 35 | 3 | 126 |
| 3 | `0+12+012` | 35 | 3 | 62 |
| 3 | `0+2+01` | 35 | 3 | 30 |
| 3 | `0+01+02+012` | 36 | 3 | 2 |
| 3 | `0+1+01+02+12+012` | 36 | 3 | 14 |
| 3 | `0+1+2+01` | 36 | 3 | 30 |
| 3 | `0+2+01+12` | 36 | 3 | 6 |
| 3 | `01+012` | 36 | 3 | 2 |
| 3 | `01+02` | 36 | 3 | 6 |
| 3 | `01+02+12+012` | 36 | 3 | 14 |
| 4 | `0+1+2+3+01+02+03+12+13+23+012+013+023+123` | 31 | 3 | 32766 |
| 4 | `0+01+02+03+012+013+023` | 36 | 3 | 6 |
| 4 | `0+1+01+02+03+12+13+012+013+023+123` | 36 | 3 | 30 |
| 4 | `0+1+2+01+02+03+12+13+23+012+013+023+123` | 36 | 3 | 510 |
| 4 | `0+1+2+3+01+02+12+012` | 36 | 3 | 510 |
| 4 | `0+1+2+3+01+23` | 36 | 3 | 854 |
| 4 | `0+1+3+01+02+12+23+012` | 36 | 3 | 30 |
| 4 | `0+3+01+02+13+23+012+123` | 36 | 3 | 6 |
| 5 | `0+1+2+3+4+01+02+03+04+12+13+14+23+24+34+012+013+014+023+024+034+123+124+134+234` | 31 | 3 | 402653054 |

## Full per-(n, k) catalogue

| n | k | # gate classes | gates (distance) | complete? |
|---|---|---|---|---|
| 15 | 1 | 1 | 0(d3) | complete |
| 23 | 1 | 1 | 0(d3) | complete |
| 27 | 1 | 1 | 0(d3) | complete |
| 28 | 1 | 1 | 0(d3) | complete |
| 28 | 2 | 2 | 0+01(d3), 0+1(d3) | complete |
| 29 | 1 | 1 | 0(d3) | complete |
| 30 | 1 | 1 | 0(d3) | complete |
| 30 | 2 | 2 | 0+01(d3), 0+1(d3) | complete |
| 31 | 1 | 1 | 0(d3) | complete (Aut-certified) |
| 31 | 2 | 1 | 0+1+01(d3) | complete (Aut-certified) |
| 31 | 3 | 1 | 0+1+2+01+02+12+012(d3) | complete (Aut-certified) |
| 31 | 4 | 1 | 0+1+2+3+01+02+03+12+13+23+012+013+023+123(d3) | complete (Aut-certified) |
| 31 | 5 | 1 | 0+1+2+3+4+01+02+03+04+12+13+14+23+24+34+012+013+014+023+024+034+123+124+134+234(d3) | complete (Aut-certified) |
| 32 | 1 | 1 | 0(d3) | complete |
| 32 | 2 | 2 | 0+01(d3), 0+1(d3) | complete |
| 33 | 1 | 1 | 0(d3) | complete |
| 34 | 1 | 1 | 0(d3) | complete |
| 34 | 2 | 2 | 0+01(d3), 0+1(d3) | complete |
| 35 | 1 | 1 | 0(d3) | complete |
| 35 | 2 | 4 | 0+01(d3), 0+1(d3), 0+1+01(d3), 01(d3) | complete |
| 35 | 3 | 8 | 0+01+02+12+012(d3), 0+01+12(d3), 0+1+01+02+012(d3), 0+1+2(d3), 0+1+2+01+02(d3), 0+1+2+01+02+12+012(d3), 0+12+012(d3), 0+2+01(d3) | complete |
| 36 | 1 | 1 | 0(d3) | complete |
| 36 | 2 | 4 | 0+01(d3), 0+1(d3), 0+1+01(d3), 01(d3) | complete |
| 36 | 3 | 8 | 0+01+02+012(d3), 0+1+01+02+12+012(d3), 0+1+2+01(d3), 0+1+2+01+02+12+012(d3), 0+2+01+12(d3), 01+012(d3), 01+02(d3), 01+02+12+012(d3) | complete |
| 36 | 4 | 7 | 0+01+02+03+012+013+023(d3), 0+1+01+02+03+12+13+012+013+023+123(d3), 0+1+2+01+02+03+12+13+23+012+013+023+123(d3), 0+1+2+3+01+02+12+012(d3), 0+1+2+3+01+23(d3), 0+1+3+01+02+12+23+012(d3), 0+3+01+02+13+23+012+123(d3) | complete |
| 37 | 1 | 1 | 0(d3) | complete |
| 37 | 2 | 1 | 0+1+01(d3) | complete |
| 37 | 3 | 1 | 0+1+2+01+02+12+012(d3) | complete |
| 38 | 1 | 1 | 0(d3) | complete |
| 38 | 2 | 3 | 0+01(d3), 0+1(d3), 0+1+01(d3) | complete |
| 38 | 3 | 5 | 0+01+02+012(d3), 0+1+01+02+12+012(d3), 0+1+2+01(d3), 0+1+2+01+02+12+012(d3), 0+2+01+12(d3) | complete |
| 38 | 4 | 7 | 0+01+02+03+012+013+023(d3), 0+1+01+02+03+12+13+012+013+023+123(d3), 0+1+2+01+02+03+12+13+23+012+013+023+123(d3), 0+1+2+3+01+02+12+012(d3), 0+1+2+3+01+23(d3), 0+1+3+01+02+12+23+012(d3), 0+3+01+02+13+23+012+123(d3) | complete |

Total distinct (n, k, gate) classes: **74**.

All parents classified completely: n≤30, 32–38 exhausted directly in the quotient; n=31 exhausted via GL(5,2) automorphism reduction ([`hard_parent_n31.py`](../hard_parent_n31.py)). No budget caps remain.
