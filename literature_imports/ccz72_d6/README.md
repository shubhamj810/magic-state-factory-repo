# 72 T to 1 CCZ at distance 6 (Gong, Pattison, Rall and Wills)

This folder rebuilds one protocol from

> A. Gong, C. A. Pattison, P. Rall, and A. Wills, “Magic State Distillation via
> Codes over Binary Extension Fields,” arXiv:2608.09727 (v1, 10 August 2026).
> [arXiv:2608.09727](https://arxiv.org/abs/2608.09727),
> [doi:10.48550/arXiv.2608.09727](https://doi.org/10.48550/arXiv.2608.09727)

as a single circuit in the catalogue's format, and prepares its merge record
for the [master catalogue](../../master_catalog/README.md). The paper prints
the outer code's matrix and its binarisation rule but no circuit for the whole
chain, so [`build_ccz72.py`](build_ccz72.py) assembles that circuit from the
paper's equations. Please cite the paper for this protocol. The catalogue's
references map already holds it as `gong2026magic`.

| file | contents |
|---|---|
| [`build_ccz72.py`](build_ccz72.py) | builds the circuit, checks the field algebra, measures `d` and `A_6`, and writes the two files below. `--check` rebuilds them and fails if a committed file differs |
| [`ccz72.json`](ccz72.json) | the construction: the `F_8` matrix, the basis, the binary outer matrix, the wire legend, the measured distance and witness, and the paper's error numbers |
| [`factories.json`](factories.json) | the merge record, in the input format of [`merge_results.py`](../../master_catalog/merge_results.py) |
| [`tests/`](tests/) | the circuit re-checked with the catalogue's primitives and three independent checks |

## Where the protocol is in the paper

The paper's Table 7 (App. D.3) lists the chain `(8T → CCZ) ∗ (9CCZ → CCZ)`
among its competitive protocols with T inputs and CCZ outputs, with
leading-order output error `10^{4.58} p^6` and spatial footprint 13. Nine CCZ
states from 8 T each make 72 T inputs, and the distance is `2 × 3 = 6`. Table 1
lists only the outer protocol.

The outer protocol is the paper's Construction 4.5, a code over
`F_8 = F_2(α)` with `α³ = α + 1`, given by its Eq. (49):

```
[ 0  0  α²  α⁴  α⁶  α⁸  α³  α⁵  1 ]   logical (x², padded with 0)
[ 1  0  α   α²  α³  α⁴  α⁵  α⁶  1 ]   stabiliser (x, padded with 1)
[ 0  1  1   1   1   1   1   1   1 ]   stabiliser (1, padded with 0)
```

The matrix satisfies the twisted three-orthogonality of Eq. (41), so by Lemma
4.2 the gate `U₇ : |γ⟩ ↦ (−1)^{tr(γ⁷)} |γ⟩` on all nine qudits is the logical
`U₇`. Over `F_8` this gate is `(−1)^{[γ ≠ 0]}`, a CCZ on the qudit's three
qubits up to CZ and Z (Sec. 3.2.5). The paper binarises the matrix in the
self-dual normal basis `α₀ = α² + α + 1`, `α₁ = α + 1`, `α₂ = α² + 1` of Eq.
(46), replacing each entry `γ` by the block `tr(γ α_l α_j)` of Eq. (47).

The inner protocol is `8T → CCZ` at distance 2, which the paper takes from the
`(6k+2)T → kCCZ` synthillation family of Campbell and Howard (Phys. Rev. A 95,
022316 (2017)) and lists in Table 7 at `28 p²`. That coefficient fixes the
circuit. Every rotation must touch the one check (otherwise a single fault is
undetected), and all 28 pairs must be harmful, so the eight output parts are
the eight vectors of `F_2³`. The rotations are therefore `x · (a, b, c) + s`
for every `x` in `F_2³`, with `s` the check.

## The circuit

Consuming a CCZ state on the parities `(q₀, q₁, q₂)` of the outer code is the
inner protocol with its outputs `a, b, c` replaced by those parities. The eight
rotations of one copy then add a phase `π/4 · Σ_x [x · q] = π [q ≠ 0]`, which
is exactly `U₇` on that qudit, with no Clifford left over. The whole chain is
therefore one circuit with `k = 3`, `N = 18` and `n = 72`:

- wires 0 to 2 are the binarised logical row (the outputs);
- wires 3 to 8 are the binarised stabiliser rows (the outer checks);
- wire `9 + i` is the check of the inner copy that feeds qudit `i`;
- column `8i + x`, for qudit `i = 0..8` and `x = 0..7` read as the bits
  `x₀x₁x₂` (with `x₀` the most significant), is the XOR of the binary columns
  of qubits `(i, j)` with `x_j = 1`, plus wire `9 + i`.

Column `8i` (that is, `x = 0`) touches only the check wire `9 + i`. It is the
rotation `s` of the inner protocol and belongs to the circuit.

## What was verified

All of the following run in [`tests/`](tests/) and pass.

The builder checks that the basis of Eq. (46) is normal and self-dual and that
Eq. (49) is twisted three-orthogonal. It pins the binarisation convention by
reproducing the paper's printed Eq. (48) from its Eq. (45) bit for bit.

The catalogue's `verify_catalog.derive` finds no problem: the factory
condition holds, the gate is `CCZ` on outputs 0, 1 and 2 (monomial `012`), the
effective width is 3, and there are no spectators, pseudo-outputs or redundant
checks. The Clifford correction is `Z` on each output and `CZ` on each pair,
which is what `(−1)^{[u ≠ 0]}` on the logical qudit `u` needs. A test evaluates
the phase of all 72 rotations on all `2^18` inputs and finds `4 [u ≠ 0] mod 8`
for every value of the check wires.

`faultcore.distance_report` sweeps weights 1 to 5 clean and finds a harmful
accepted fault of weight 6, on columns `[3, 6, 8, 11, 40, 43]`, so `d = 6`
exactly. `errorcoeff.error_coefficient` gives `A_6 = 37632`, by MacWilliams and
by direct enumeration. The outer code alone accepts no harmful qudit error of
weight 1 or 2 and accepts 588 of weight 3. Each inner copy makes a given
nonzero error from exactly 4 of its 28 weight-2 faults, so
`A_6 = 4³ × 588 = 37632`.

The paper states `10^{4.58} p^6`. Its Example D.2 computes such coefficients
as `C(9,3) Σ P_abc w_a w_b w_c K(a,b,c)` (Eq. (189)), with `K` from its Table
5. With the `8T → CCZ` weights `w₁ = w₂ = 12 p²` and `w₃ = 4 p²` this gives
exactly 37632, which is `10^{4.576}`. The tests also recompute all ten values
of Table 5 from the binarised outer code here and match the paper's fractions
exactly, which confirms that the circuit uses the paper's code in the paper's
basis.

## Merge

`merge_results.py factories.json --dry-run` against the shipped catalogue
(1027 classes) accepts the record as a new class, `72.3.6.a`, at `N = 18` with
`d = 6` exact and `A_d = 37632`. The catalogue held no `[[72,3,6]]` class.
Before this, its CCZ classes at distance 6 had `n = 128` and `n = 176`. The
record uses the existing reference key `gong2026magic`, a new regime
`Gong et al.: F8 codes concatenated with 8T->CCZ`, and discovery
`pre-existing`.

## Reproduce

```bash
.venv/bin/python literature_imports/ccz72_d6/build_ccz72.py --check
.venv/bin/python -m unittest discover -s literature_imports/ccz72_d6/tests
.venv/bin/python master_catalog/merge_results.py literature_imports/ccz72_d6/factories.json --dry-run
```
