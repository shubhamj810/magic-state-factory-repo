# Parent-check-first methodology

## What changes relative to direct search

A direct circuit search chooses check and output labels at the same time. The
parent-check-first method separates them:

1. choose or classify an unlabelled set of check syndromes (the **parent**);
2. compute every individually legal output direction once;
3. test which directions can coexist;
4. either solve for one target or list all compatible logical gates.

For distance three, a reduced parent is a set `S` of distinct nonzero points of
`F_2^r`. Distinctness rules out accepted faults of weight one and two. The check
rows span `C`. Let `C^<2>` be the span of all pairwise Schur products of check
rows. The legal one-output space and its check quotient are

```text
W_3(C) = (C^<2>)^perp,
V_3(C) = W_3(C) / C.
```

For distance `d > 3`, the implementation additionally builds the span
`Z_<d` of accepted check faults below `d` and uses
`W_d = (C^<2>)^perp intersect Z_<d^perp`.

Two quotient directions `a,b` can coexist exactly when every check row `c`
satisfies `<a*b,c> = 0`. These are alternating bilinear compatibility forms on
`V_d`. A legal output space is therefore a common totally isotropic subspace.

## The three certification quantities

The CLI reports the chain

```text
tau_D(C) <= mu_d(C) <= kappa_d(C).
```

- `kappa_d = dim V_d(C)` is exact linear algebra. At distance three the code
  also checks the capacity identity
  `kappa_3 = n - 2r - binom(r,2) + delta`, where `delta` is the dimension of
  the constant-free quadrics vanishing on `S`.
- `mu_d` is the maximum dimension of a common compatible subspace. Ranks of
  individual compatibility forms, and of all their check-linear
  combinations, give cheap upper bounds. Exact `mu_d` requires subspace
  enumeration.
- `tau_D` is the maximum width carrying target family `D`. The implemented
  summary target is `T^tensor k`; a fixed arbitrary degree-at-most-three target
  can be passed to the targeted command.

The JSON distinguishes exact values from lower/upper bounds. If a node or gate
orbit budget is reached, `complete` is false. Such output is useful search data,
not a nonexistence certificate.

## Targeted search and gate classification

The targeted solver adds output rows one at a time. At each step, all new
single, pair, triple and compatibility conditions are linear in the next row.
It solves that affine system over the quotient coordinates, then branches only
over the remaining free directions. Stored catalog parents also retain their
native output frame as an immediate positive control.

The target-agnostic solver enumerates each compatible subspace once in canonical
RREF form. A logical gate is its parity tensor:

```text
linear     |a_i| mod 2              -> T_i
quadratic  |a_i * a_j| mod 2        -> CS_ij
cubic      |a_i * a_j * a_l| mod 2  -> CCZ_ijl
```

Two dedup scopes are available:

- `symmetric`: output permutations `S_k` only;
- `gl`: output CNOT frames `GL(k,2)`.

The GL action must transform the linear, bilinear and trilinear phase tensors
with their coincident entries. Naively substituting variables in the mod-two
Boolean shadow is wrong: it would send `T0.T1` to a single `T`, even though its
physical orbit contains `T0.T1`, `T0.CS01`, and `T1.CS01`. The implementation
has a regression test for this distinction and checks tensor transformations
against transformed explicit output rows.

## Why one `RM(3,7)` sweep covers every `r <= 7` parent

For a distance-three parent of effective rank `r'`, the origin-augmented
indicator belongs to `RM(r'-4,r')`. Embed its span into `F_2^7`. The extension
is the product of that indicator with one linear factor for every unused
coordinate, so its degree is

```text
(r' - 4) + (7 - r') = 3.
```

Thus every rank `4,5,6,7` parent occurs among the marked words of `RM(3,7)`.
For `n <= 44`, only word weights `16,24,28,32,36,40,44` occur. The bundled
Gillot–Langevin table supplies 71 relevant affine orbits. Auditing all 128
origins gives 9,088 marked geometries; using the listed stabilizer generators
gives a smaller, completeness-safe representative run for invariant results.

The data parser provides a global certificate: after correcting the one known
weight-64 stabilizer typo, the 3,486 orbit sizes sum to `2^64`, the number of
words in `RM(3,7)`. See
[`../../classification/legacy/rank7_census/data/README.md`](../../classification/legacy/rank7_census/data/README.md).

## Reproduction levels

The per-parent commands are this directory's [`../cli.py`](../cli.py); the
`r <= 7` outer enumeration and the bundled orbit table live in
[`../../classification/legacy/rank7_census/`](../../classification/legacy/rank7_census/) and
are driven by its own `cli.py`. Every command below is run from the repository
root, so none of them depends on the one before it.

```bash
# Data and parser only.
.venv/bin/python classification/legacy/rank7_census/cli.py data-check

# One known parent: cheap screens, exact target, then a small gate list.
.venv/bin/python parent_first/cli.py analyze --factory 51,5,3 --cheap-only
.venv/bin/python parent_first/cli.py target --factory 47,3,3 --gate CCZ012
.venv/bin/python parent_first/cli.py gates --factory 15,1,3 --kmax 1 \
  --dedup gl --node-budget 0 --orbit-budget 0

# Constrained outer run suitable for a laptop/CI smoke test.
.venv/bin/python classification/legacy/rank7_census/cli.py census \
  --class-index 306 --max-parents 2 --kmax 2 --allow-incomplete \
  --output classification/legacy/rank7_census/results/r7_smoke.json

# Full selected enumeration (cluster scale; no search budgets).
.venv/bin/python classification/legacy/rank7_census/cli.py census \
  --mode all --kmax 7 --dedup gl \
  --node-budget 0 --orbit-budget 0 --checkpoint-every 1 \
  --output classification/legacy/rank7_census/results/r7_full_gl.json
```

The last command is intentionally available but not claimed to be cheap.
Closing full GL orbits at `k >= 6` can dominate the run. Constrained runs use
the exact same code path and retain explicit completion metadata.
