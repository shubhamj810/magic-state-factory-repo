# Parent-first: cheap filters before exact enumeration

Theory behind [`../parent_first/`](../parent_first/): the filter chain, and where
it sits in the decision pipeline.

## The idea

A direct circuit search chooses check and output labels at the same time. The
parent-first method separates them, in this order:

1. choose or classify an unlabelled set of check syndromes — the **parent**;
2. compute every individually legal output direction, once;
3. test which of those directions can coexist;
4. either solve for one named target, or list every logical gate the parent can
   carry.

The payoff is that steps 2-4 are computed *per parent*, not per target. One
parent audited once answers product targets, entangled targets, and targets
nobody named before the search started. Only a direct target solve has to
specialise the right-hand side.

## The colored quotient

Fix the check code `C` — the span of the `r` check rows. Write `u AND v` for the
coordinatewise product and `C^<2>` for the Schur square, the span of all
pairwise products of check rows. With `Z_<d` the span of accepted check faults
of weight below `d`,

```text
R(C) = (C^<2>)^perp,
W_d  = R(C)  intersect  Z_<d ^perp,
V_d(C) = W_d / C.
```

Three linear filters and a quotient: exclude labels that leak a non-Clifford
phase onto a check; exclude labels that would make a short accepted fault
logical; and identify labels differing by a check row, which changes the written
matrix but not what the circuit does.

At distance three the short-fault list is empty. A weight-one vector in
`C^perp` would be a zero syndrome and a weight-two vector two equal syndromes,
both already excluded by the reduced normal form, so

```text
W_3(C) = (C^<2>)^perp
```

and that is the simplification used throughout the distance-three computations.
For `d > 3` the implementation genuinely builds `Z_<d`, which costs a search
over at most `sum_{w<d} binom(n, w)` supports.

Two quotient directions `a, b` can coexist exactly when `< a AND b, c > = 0` for
every check row `c`. Each `B_c(a, b) = < a AND b, c >` is a well-defined
alternating bilinear form on `V_d(C)` — well-defined because replacing `a` by
`a + c'` changes it by `< b, c' AND c >`, which vanishes since `c' AND c` lies
in `C^<2>` and `b` lies in `W_d`; alternating because `B_c(a, a) = < a, c >` and
`c AND c = c`. So a legal output space is a subspace of `V_d(C)` totally
isotropic for every `B_c`, and one searches subspaces, not cliques:
compatibility is closed under XOR, so the search can be organised by canonical
row-reduced bases with no duplication.

## The three filters, in cost order

```text
tau_D(C)  <=  mu_d(C)  <=  kappa_d(C)
```

Each inequality can be strict. The chain is a sequence of *stopping tests*, not
a score to maximise, and the whole point is that the cheap ones can kill a
parent before the expensive one runs.

### kappa_d: how many directions are legal

`kappa_d(C) = dim V_d(C)`. This is a nullity — one row reduction — and is
sub-second even on large parents; `cli.py analyze --cheap-only` stops here, and
that is how you triage a parent before spending anything. At distance three it
has a closed form, checked by the code against the direct computation:

```text
kappa_3 = n - 2r - binom(r,2) + delta,
```

where `delta` is the *quadric degeneracy*, the number of independent constant-free
quadratic forms vanishing on every point of the parent. Read it as a budget: you
start with `n` injections, the checks consume `2r + binom(r,2)` of them, and
quadric degeneracy refunds `delta`. At fixed `n` and `r` the only lever is
`delta`, and `delta` is testable. Representative values:

| factory | n | r | delta | kappa_3 | the points |
| --- | ---: | ---: | ---: | ---: | --- |
| `[[15,1,3]]` | 15 | 4 | 0 | 1 | all nonzero points of `F_2^4` |
| `[[35,3,3]]` | 35 | 6 | 1 | 9 | a rank-six quadric |
| `[[47,3,3]]` | 47 | 6 | 1 | 21 | union of two hyperplanes |
| `[[44,4,3]]` | 44 | 7 | 3 | 12 | cubic |
| `[[51,5,3]]` | 51 | 7 | 0 | 16 | cubic, no quadric |
| `[[49,1,5]]` | 49 | 13 | 56 | 1 | contains no line (a cap) |

Cost is `O(n r^4)`: build and row-reduce the `(r + binom(r,2)) x n` matrix of
restricted linear and quadratic monomials.

### mu_d: how many can coexist

`mu_d(C)` is the largest dimension of a subspace of `V_d(C)` that is totally
isotropic for every `B_c`. Before paying for it there is a cheap alarm. An
alternating form of rank `2m` admits isotropic subspaces of dimension at most
`kappa_d - m`, so

```text
mu_d(C)  <=  kappa_d(C) - (1/2) max_c rank B_c.
```

Building the `r` basis forms costs `O(r kappa_d^2 n)` and ranking them
`O(r kappa_d^3)`, which already gives an immediate alarm from any single form.
The strongest version tests every linear combination of the `r` forms and costs
`O(2^r kappa_d^3)` — exponential in `r`, but `r` is small here, and
`form_rank_bounds` in [`factorylib/parent.py`](../factorylib/parent.py) does exactly that,
reporting the maximising check combination alongside the bound.

Exact `mu_d` requires enumerating compatible subspaces, which is exponential in
`kappa_d`. That is still useful because `kappa_d` is often near ten even when
`n` is much larger — the controlling dimension is `kappa_d`, not `n`.

### tau_D: how wide a target actually fits

`tau_D(C)` is the largest width realised by the exact target equations for a
named family `D` — `tau_T(C)` is the largest `k` for which `T^k` is realised.
The solve is an affine recursion. With `u_1, ..., u_{j-1}` fixed, every
condition on the next row `u_j` is linear in its quotient coordinates: its `T`
parity, its pair and triple parities against the chosen rows, and compatibility
with each previous row against each check. Writing
`u_j = sum_t z_t v_t` in a basis of `V_d(C)`, all of it becomes one binary
system `M_j z = b_j` with at most

```text
m_j = 1 + (j-1) + r(j-1) + binom(j-1, 2)
```

equations. Gaussian elimination does exactly two things: it certifies
inconsistency, in which case the branch stops, or it returns a solution `z_0`
and a basis of `ker M_j`, so every possible next row is `z_0 + ker M_j`, a coset
of `2^{kappa_d - rank M_j}` candidates. Those candidates are enumerated because
different choices impose different conditions on later rows. The linear solve is
polynomial; the branching over cosets is the exponential part, and in practice
each new output adds about `r` compatibility equations, so the cosets shrink
fast.

There is also a cheap necessary condition on the target side. Quotienting out
the output combinations invisible to every target coefficient leaves the
target's *essential dimension* `crank(D)` — `crank(T^k) = k`, `crank(CS) = 2`,
`crank(CCZ) = 3` — and `crank(D) <= mu_d(C)` is necessary. It is not sufficient:
the available directions may have the wrong odd overlaps, which only the affine
solve decides. Conversely, once the exact solve has produced `tau_D(C)` for a
nested family, width `k` is realisable exactly when `k <= tau_D(C)` — sufficient
only because `tau_D` already contains the hard result.

For a target-agnostic answer there is a sharper tool than any dimension count.
Every degree of non-Clifford phase is read off one linear functional on
`V_d(C)`, and compatibility with the already-chosen rows is a system of linear
functionals; so a gate of that degree is reachable exactly when the colour
functional is *not* in the span of the compatibility functionals. If it is in
the span, compatibility already forces the colour to vanish and the gate is
unreachable — not because a search failed, but because the constraints implied
it. Checking span membership is a rank computation, needs no target list, and is
what makes the target-agnostic census affordable. It is also strictly sharper
than the dimension screens: the 32-point affine cap at six checks passes every
capacity bound at distance four and is nevertheless colour-dead.

## Why the ordering pays

The escalation rule is: reject a parent as soon as `kappa_d < crank(D)`, or as
soon as a form-rank bound puts `mu_d < crank(D)`. Exact `mu_d` and `tau_D` are
paid for only after those polynomial screens pass.

The `[[51,5,3]]` parent is the example that justifies the whole chain. Its
seven-check geometry has `dim C^<2> = 28` and `dim W_3 = 23`, hence
`kappa_3 = 16`. Taken alone, a menu of dimension sixteen invites the guess that
this geometry hides a much richer factory. Exact continuation says otherwise:

```text
kappa_3 = 16   ->   mu_3 = 8   ->   tau_T = 5.
```

Eight directions can coexist but not nine; of those, five can carry product `T`
but not six. The stored `T^5` output is already maximal for this geometry, and
an exact probe confirms it from the other side: pure `CCZ` (`T`-count 7) and
`CS^2` (`T`-count 6) are both impossible here. A report of `kappa_3 = 16` alone
would have implied room for eleven more outputs.

Note what `tau_T = 5` does *not* say. It is a product-`T` statement; it does not
bound the exact `T`-count of an arbitrary entangled phase on up to eight
compatible directions. The two questions must not be conflated.

## Budgets and the `complete` flag

Every expensive stage in [`factorylib/parent.py`](../factorylib/parent.py) takes a node
budget: `compatible_subspaces` counts dequeued subspaces, `find_target` counts
coset candidates, `classify_gates` additionally caps `GL` orbit enumeration.
Hitting a budget raises internally, is caught, and is returned as
`complete: false`.

**A budget hit is search data. It is never a nonexistence certificate.** This
is the single most likely way to misuse these modules, so the flag is threaded
through every payload they write, and downgraded results say so explicitly: on a
budget hit `exact_mu` returns its value as a lower bound and falls back to the
form-rank upper bound; `tau_product_t` returns `value: null`; a capped `GL`
orbit is keyed apart under `(k, "partial", ...)` because a partial orbit minimum
is not an invariant. In the CLI, budget `0` means unlimited.

The complement is worth stating too, because some negative answers *are*
certificates: `find_target` returns `complete: true` with `found: false` when
the requested width exceeds `kappa`, and `tau_product_t` returns
`value: 0, complete: true` when even a single `T` is impossible. Those are
genuine parent-level no-goes. A parent-complete claim permits neither a node
budget nor an unresolved timeout.

Every positive result is re-verified before it is recorded. `verify_columns`
re-reads parity and low-weight fault distance from raw columns, and a stored
seed frame — the native output frame recovered by `Parent.from_columns`, kept as
a positive control — is re-verified before being returned rather than trusted.

## Where else this machinery runs

[`../classification/rank7_census/`](../classification/rank7_census/) ships the
same [`factorylib/parent.py`](../factorylib/parent.py) implementation and drives it across its entire outer enumeration: for every
marked `RM(3,7)` geometry it builds the parent, then calls `classify_gates` to
enumerate every compatible subspace and read off its phase, deduplicated either
under `GL(k,2)` or under `S_k`. So the census is exactly this parent-first
pipeline run over a complete outer list rather than over one parent of interest.
Use [`../parent_first/cli.py`](../parent_first/cli.py) — `analyze`, `target`,
`gates` — to interrogate a single parent, and
[`../classification/rank7_census/cli.py`](../classification/rank7_census/cli.py)
to run the sweep. The methodology write-up is
[`docs/PARENT_CHECK_FIRST.md`](../parent_first/docs/PARENT_CHECK_FIRST.md).
