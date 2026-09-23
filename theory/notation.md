# Notation

Symbols and string formats used across these notes, the code docstrings and the
catalogues. Definitions in
[`01_factories_and_distance.md`](01_factories_and_distance.md).

## Parameters

| symbol | meaning |
| --- | --- |
| `n` | injections: number of columns, i.e. parity-`T` rotations consumed |
| `k` | protected output wires, indexed `0..k-1` |
| `r` | postselected check wires; `check_rank` is the `F_2` rank of the check rows, `ambient_rank` the number of check coordinates carried |
| `N` | total circuit qubits, `N = k + r` |
| `d` | circuit distance (below) |
| `[[n,k,d]]` | a factory consuming `n`, producing `k`, at distance `d`; `N` is quoted separately |
| `alpha = (P \| S)` | one column, split into output part `P` in `F_2^k` and syndrome `S` in `F_2^r` |
| `L`, level | Clifford level: the gate is `diag_x exp(i (pi/2^{L-1}) f(x))`. `L = 2` is `S`/`CZ`, `L = 3` is `T`/`CS`/`CCZ`, `L = 4` is `sqrt(T)`/`CT`/`CCS`/`CCCZ` |

## Spaces attached to a check parent

| symbol | meaning |
| --- | --- |
| `C` | check code: the span of the `r` check rows, a subspace of `F_2^n` |
| `C^<2>` | Schur square of `C`: span of all coordinatewise products `c AND c'` |
| `R(C)` | `= (C^<2>)^perp`, the individually legal output rows |
| `Z_<d` | span of accepted check faults of weight below `d`; empty at `d = 3` |
| `W_d(C)` | `= R(C) intersect Z_<d^perp`; `W_3(C) = (C^<2>)^perp` |
| `V`, `V_d(C)` | the colored quotient `W_d(C) / C`; gates are functions of it |
| `B_c(a,b)` | `= < a AND b, c >`, the alternating compatibility form for check `c` |
| `delta` | quadric degeneracy: independent constant-free quadrics vanishing on the point set |
| `chi` | origin-augmented indicator of the check point set; a codeword of `RM(r-4, r)` |

## The filter chain

| symbol | meaning | cost |
| --- | --- | --- |
| `kappa_d(C)` | `dim V_d(C)`: how many output directions are individually legal. At `d = 3`, `kappa_3 = n - 2r - binom(r,2) + delta` | one row reduction, `O(n r^4)` |
| `mu_d(C)` | largest dimension of a subspace of `V_d(C)` totally isotropic for every `B_c`: how many can coexist | form-rank bounds are polynomial; exact value is exponential in `kappa_d` |
| `tau_D(C)` | largest width realising target family `D` (`tau_T` for product `T`) | affine recursion, branching over solution cosets |
| `crank(D)` | essential dimension of a target: `crank(T^k) = k`, `crank(CS) = 2`, `crank(CCZ) = 3` | free |

Always `tau_D <= mu_d <= kappa_d`, and each inequality can be strict.

## Equivalence relations

| symbol | relation | role |
| --- | --- | --- |
| `S_k` | permute the `k` output wires | **the classification catalogues' key**: same circuit, relabelled |
| CNOT+S (`GL(k,2)` on the `Z_8` phase) | change the output basis, modulo diagonal Cliffords | a different written phase polynomial but the **same magic state**; **the master catalogue's key** since 2026-09-15, decided by `master_catalog/glcanon.py` |
| `F_2` truth-table `GL(k,2)` | substitution `f -> f o M` on the gate read as a Boolean function over `F_2` | stored in the classification catalogues as an annotation (`gl_class` / `gate_gl_canonical`); coarser than `S_k` but NOT the magic-state relation (it separates `0+1` from `0+01`); `\|GL(k,2)\| = 6, 168, 20160, 9999360` for `k = 2..5` |

Row counts under `S_k` are representation-dependent upper bounds on the number
of inequivalent magic states; the master catalogue's CNOT+S rows count them. Maxima (largest `k`, largest `T`-count, which gates occur at
a given `n`) are unaffected.

## Gate strings

A gate is the set of `F_2` monomials in the output variables with odd overlap
parity, written as monomials joined by `+`, degree 1 first:

```text
0        =  T_0
01       =  CS_01
012      =  CCZ_012
0+1+01   =  T_0 . T_1 . CS_01
```

Degree 1 comes from `|a_i|` odd, degree 2 from `|a_i AND a_j|` odd, degree 3
from `|a_i AND a_j AND a_l|` odd. `check-only` denotes the empty monomial set.
Reported alongside every gate:

- `t_count` — exact minimal `T`-count (Amy-Mosca / Reed-Muller minimum-weight
  coset over `Z_8`); `null` for gates with no finite level-3 `T`-count;
- `poly_degree` — CNOT-frame-reduced phase-polynomial degree, minimised over
  output frames in `GL(k,2)`.

## Geometry tags

A slot-ansatz geometry is a list of check blocks, tagged by kind and size and
joined by `+`:

```text
S3+C4      one symmetric block on 3 check qubits, one cyclic block on 4
S1+S1+S2+S2   four symmetric blocks (the compact CCZ [[47,3,3]] geometry)
P5#2       an explicit permutation-group block of size 5, block index 2
```

`S` is the full symmetric group on the block, `C` the cyclic group, `P` an
explicit generator list. The block sizes sum to `r`, so `N = k + sum lam`.

## Two distance conventions

**What `d` means.** The circuit distance is the minimum weight of an
undetectable damaging fault: a set of columns whose syndromes XOR to zero while
their output parts do not. This equals the `Z`-distance of the
generalized-triorthogonal CSS code on the same rows
([`01_factories_and_distance.md`](01_factories_and_distance.md)), so `[[n,k,d]]`
is unambiguous and no separate circuit-specific notion is in play.

**How it is reported.** The verifiers enumerate by ascending weight and are
exact through weight 4 (meet-in-the-middle over pairwise column XORs at weights
3 and 4). Beyond that they saturate: `factorylib/verification.py` returns the
string `>4` and `evaluator._distance` returns `dmax + 1` meaning "at least". A catalogued
`d = 5` therefore asserts no damaging fault of weight 4 or less, not exactly 5.

Separately, the slot ansatz's `d >= 4` label rules are a *structural*
over-approximation used inside the model — sound, but excluding some genuine
distance-four circuits, which `exact_d4.py` recovers by CEGAR. Catalogued
distances are always the independently verified value, never the structural one.

## Counting vocabulary

Four different numbers get called "how many factories", and mixing them is the
easiest way to produce a contradiction between two files. Each catalogue states
which one it reports.

| term | what it counts | example |
| --- | --- | --- |
| **witness** (circuit) | one explicit column list. Two witnesses can realise the same gate in different output labellings, or even be byte-identical under different labels | the rank-7 census stores **28** T-count-5 witnesses |
| **`S_k` class** — *the classification catalogues' key* | one `(n, k, gate up to output permutation)` triple. This is the row count of the classification catalogues | those 28 witnesses are **21** `S_k` classes |
| **`F_2` `GL(k,2)` annotation class** | one orbit of the gate's `F_2` truth table under `f -> f o M`, stored per row as an annotation, coarser than `S_k` | the same 21 collapse to **13** |
| **CNOT+S class** — *the master catalogue's key* | one `(n, k, d, gate up to a CNOT frame and diagonal Cliffords)` tuple, decided by `master_catalog/glcanon.py`; circuits at different distances are different classes | the master catalogue's 1,750 `S_k` rows are **632** CNOT+S classes |
| **stored representative** | a raw census/search output before any deduplication, kept for provenance | the master catalogue's 302 rows cite **667** of them in their `sources` |

A row count is therefore an upper bound on the number of inequivalent *gates*
and not a count of *circuits*. Maxima — largest `k`, largest `T`-count, which
gates occur at a given `n` — are properties of the realisable set and are the
same under every one of these keys.

## Completeness vocabulary

| flag / word | meaning |
| --- | --- |
| `complete: true` | the stage exhausted its space; an absence is a certificate |
| `complete: false` | a node, orbit or time budget was hit. **Search data, never a nonexistence certificate.** In the CLIs, budget `0` means unlimited |
| marked | a classified support with a chosen origin, yielding an explicit check parent; markings are enumerated exhaustively, so the marked family is a superset |
| covering representatives | a completeness-safe list that may contain duplicates of one true orbit; sound for absence claims, not a count of classes |
| record | best circuit found by a search; not a classified maximum |
