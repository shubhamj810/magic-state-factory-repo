# Factories, gates, and distance

The object every directory in this repository searches for. Read this first.

## A circuit is a set of columns

Fix `N = k + r` wires: outputs `0..k-1` and postselected checks `k..N-1`. A
nonzero vector `alpha` in `F_2^N` labels one parity rotation

```text
P_alpha = exp[ i (pi/8) ( I - prod_{a : alpha_a = 1} Z_a ) ],
```

which applies a `pi/4` phase to the computational basis states on which the
parity `alpha . x` is odd. A circuit is a selection of such rotations, stored
as a list of *columns*, each column the qubit support of one rotation. Two
equal columns cancel to a diagonal Clifford, so reduced circuits have distinct
columns.

Stack the columns into a binary matrix with one row per wire. The `r` check
rows span the check code `C`; the `k` output rows are `a_1, ..., a_k`. This is
the same matrix a triorthogonal-code search would produce, and it is the same
data a borrowed-identity search produces after translation: the three
formulations are three coordinate systems on one affine fibre. Nothing below
depends on which reading you prefer, but the
code is written in matrix coordinates because that is what makes the outer
geometry finite.

The same `alpha` is also a fault label. An injected state that fails deposits
the `Z` fault `prod Z_a` over its support. Splitting a column as
`alpha = (P | S)` into an output part `P` and a check part (the *syndrome*)
`S`, a fault set is *accepted* when its syndromes cancel and *damaging* when
its output parts do not.

## Phase polynomial, level, and "the gate"

The accepted logical action is diagonal. Write it as

```text
U = diag_x exp( i (pi / 2^{L-1}) f(x) ),   f : F_2^k -> Z_{2^L},
```

where `L` is the *Clifford level*. Level 2 (`pi/2`) is `S` and `CZ`; level 3
(`pi/4`) is `T`, `CS` and `CCZ`; level 4 (`pi/8`) is `sqrt(T)`, `CT`, `CCS` and
`CCCZ`. Everything classified in this repository is level 3; the search
catalogue also contains level-2 and level-4 rows, which is why the landscape
figure filters on level before drawing the classification bands. (The
convention is implemented in [`factorylib/degree.py`](../factorylib/degree.py);
[`sat_search.py`](../symmetry_sat_search/sat_search.py) names the same levels by
the half-angle of the rotation, `pi/4`, `pi/8`, `pi/16`.)

At level 3 the non-Clifford content of `f` is a set of `F_2` monomials in the
output variables, and each monomial is read off a single overlap parity of the
output rows:

| monomial | condition | gate |
| --- | --- | --- |
| degree 1, `x_i` | `\|a_i\|` odd | `T` on output `i` |
| degree 2, `x_i x_j` | `\|a_i AND a_j\|` odd | `CS` on `i, j` |
| degree 3, `x_i x_j x_l` | `\|a_i AND a_j AND a_l\|` odd | `CCZ` on `i, j, l` |

Here `AND` is the coordinatewise product of row vectors and `|.|` is Hamming
weight. *The gate* means exactly this monomial set, written as a string:
`0+1+01` is `T_0 . T_1 . CS_01`, and `012` is `CCZ_012`. It is a phase
polynomial, not a name from a fixed menu — the classifications are
target-agnostic and report whatever gate a frame happens to carry, including
entangled ones with no standard name.

## The factory condition

A set of columns is a factory when the gate lands on the outputs and nothing at
all is deposited on the postselected checks. Concretely, with `a` any output
row and `h` any check row, every degree-at-most-3 parity that touches a check
wire must be even:

```text
|h_i| , |h_i AND h_j| , |h_i AND h_j AND h_l|  =  0   (mod 2)
|a AND h_j| , |a AND h_i AND h_j|              =  0   (mod 2)
|a AND b AND h_j|                              =  0   (mod 2)
```

The first line says the check part is *triorthogonal*. The second and third are
the mixed output-check conditions. The first two lines are linear in a single
output row; only the last couples two different outputs, and that is the whole
reason the inner problem splits into "which directions are legal" and "which
legal directions can coexist" (see [`03_parent_first.md`](03_parent_first.md)).
Verification never trusts this algebra: given explicit columns,
[`factorylib/verification.py`](../factorylib/verification.py) recomputes every
degree-1, 2 and 3 column parity directly and compares against the claimed
target, with `0` required on every subset touching a check.

## The Clifford correction

The factory condition makes every parity touching a check *even*, not zero
mod 8, and an odd output parity fixes only which gate is there, not its exact
phase. So the rotations deposit the gate times a diagonal Clifford, and the
factory must undo it after the rotations and before it measures the checks.
With every rotation a `T = diag(1, e^{i pi/4})`, the rotations multiply in
`e^{i pi f(v)/4}` on the basis state `v` of all `N` wires, and expanding the
parity of each column (Bravyi and Haah, PRA 86, 052329 (2012), Sec. III) gives

```text
f(v) = sum_q |g_q| v_q - 2 sum_{q<r} |g_q AND g_r| v_q v_r
       + 4 sum_{q<r<s} |g_q AND g_r AND g_s| v_q v_r v_s      (mod 8),
```

with `g_q` the row of wire `q`. Take away the gate as printed (`x_i` for each
`T`, `2 x_i x_j` for each `CS`, `4 x_i x_j x_l` for each `CCZ`). The cubic
terms cancel, every pair coefficient is `0` or `4` (a `CZ`), and every single
coefficient is even (an `S^p`). That residual is the row's
`clifford_correction`, unique for the stored circuit. Undoing it on a check
makes an error-free run pass with certainty. Undoing it on an output makes the
output the gate shown rather than the gate times a Clifford, for instance `T`
rather than `T^dagger` for the 15-to-1.

Running a rotation as `T^3`, `T^5` or `T^7 = T^dagger` costs the same magic
state and adds `2 s |c . v|` to `f`. The correction disappears for some choice
of powers exactly when a linear system over `Z_4` has a solution: for each
wire `q`, `sum_{c contains q} s_c = p_q (mod 4)`, and for each pair `q < r`,
`sum_{c contains q, r} s_c = [CZ_qr] (mod 2)`. For a code, with columns as
qubits, a solution is a transversal `T` gate (`T^j` on each qubit), in the
sense of Jain and Albert, arXiv:2408.12752. The row stores a solution as
`rotation_powers`, or `null` when the system has none and `S` or `CZ` gates
are unavoidable.
[`master_catalog/clifford.py`](../master_catalog/clifford.py) computes both.
`verify_catalog.py` checks them without the expansion: it evaluates the
circuit's phase directly on every input of weight at most 3, which is complete
because the residual has degree at most 3, and it simulates small circuits
gate by gate.

## The punctured simplex

One family is worth writing down explicitly, because nine rows of the
symmetry search's example catalogue are members of it and every search in
this repository starts from inside it. They are distance 2. Since the master
catalogue's floor was lowered to `d >= 2` (2026-10-07) they are held there,
among them `14.1.2.a`, `12.2.2.a` and `8.3.2.a`: the `T`, `CS` and `CCZ` members
of the malleable chain of Singh, Gidney and Jones (arXiv:2606.28518), whose
catalogue is imported in [`../borrowed_identities/`](../borrowed_identities/).

Fix `N` wires with the output block `0..k-1`, and take **every nonzero column
except those supported inside the output block** — that is, every column
touching at least one check wire. Its size is

```text
n = 2^N - 2^k .
```

Three facts, each a line of counting.

*It is a factory, at level `N-1`.* For a monomial `Q` that touches a check wire,
the columns containing `Q` are all `2^(N-|Q|)` supersets of it, none of which is
output-only, so that parity is even whenever `|Q| <= N-1`. For `Q` inside the
output block with `|Q| = q`, the count is `2^(N-q) - 2^(k-q)`, and both terms are
even unless `q = k`, where it is `2^(N-k) - 1`. So exactly one parity is odd: the
full output monomial `x_0 x_1 ... x_(k-1)`. The circuit deposits the width-`k`
gate of Clifford level `N-1` and nothing else.

*Its distance is exactly 2.* No column lies inside the outputs, so no single
column is an undetectable fault and `d >= 2`. For any check wire `c`, both `{c}`
and `{c, 0}` are present and their XOR is `{0}` — an undetectable weight-2
damaging fault. Hence `d = 2`.

*It is the largest such circuit on those wires.* A column supported inside the
output block is itself a weight-1 undetectable fault, so no distance-2 circuit
can contain one; every factory on `N` wires with a `k`-output block and `d >= 2`
is therefore a **subset** of the punctured simplex. This is the sense in which
the symmetry search's catalogue labels the level-3 members *malleable*: they
are not one circuit among many but the ceiling, and improving distance means
deleting columns from them, which is what the searches in
[`../symmetry_sat_search/`](../symmetry_sat_search/) do.

The nine members that ship are `N = 3, 4, 5` with every `k < N`, giving the
level-2, level-3 and level-4 chains `S/CZ`, `T/CS/CCZ` and
`sqrtT/CT/CCS/CCCZ`; they carry `analytic: punctured simplex` provenance in
[`../symmetry_sat_search/examples/found_factories.json`](../symmetry_sat_search/examples/found_factories.json)
and can be regenerated in one line, which is what makes them a check on the
verifiers rather than data to be trusted:

```python
[c for size in range(1, N + 1) for c in itertools.combinations(range(N), size)
 if max(c) >= k]
```

## Circuit distance

The circuit distance is the minimum weight of an undetectable damaging fault:

```text
d = min { |F| : XOR_{m in F} S_m = 0  and  XOR_{m in F} P_m != 0 }.
```

This is not a circuit-specific notion: it is exactly the `Z`-distance of the
generalized-triorthogonal CSS code built from the same rows.

The successive distance conditions are instances of one rule: if fewer than `d`
faults have zero total syndrome, they must have zero total output action.

```text
d >= 2 :  S_i = 0                 =>  P_i = 0
d >= 3 :  S_i + S_j = 0           =>  P_i + P_j = 0
d >= 4 :  S_i + S_j + S_l = 0     =>  P_i + P_j + P_l = 0
```

For a reduced circuit (no zero column, no repeated column) the first line says
every syndrome is nonzero and the second says the syndromes are pairwise
distinct. So **distance three is a property of the check part alone**, and
imposes nothing on the output labels. Distance four is the first condition that
constrains outputs: whenever three syndromes sum to zero, the three output
labels must too. If the syndrome set contains no such triple — if it is a cap —
the distance-four condition is vacuous.

**Reporting convention.** The verifiers enumerate faults by ascending weight
and are exact through weight 4, using a meet-in-the-middle over the table of
pairwise column XORs for weights 3 and 4. Beyond the cap they return the string
`>4` ([`factorylib/verification.py`](../factorylib/verification.py)) or the integer
`dmax + 1`, meaning "at least that"
([`evaluator.py`](../symmetry_sat_search/evaluator.py)). A catalogued `d = 5`
therefore means "no damaging fault of weight 4 or less", not "exactly 5". Every
catalogued circuit carries an independently recomputed distance; the search
modules and the verifiers deliberately share no code.

## Distance three as finite geometry

Put the two previous sections together. At distance three a factory is

```text
a set S of distinct nonzero points of F_2^r  (the syndromes),
each carrying a colour f(S) = P in F_2^k     (the output label),
```

with `n = |S|` and `r` checks. The unlabelled point set is the *outer geometry*
(equivalently, the check parent); choosing colours is the *inner phase
problem*. The split is exact, and it immediately gives the width bound
`n <= 2^r - 1`, saturated by the 15-to-1 factory, plus the reason complete
enumeration at fixed `r` is possible at all.

The point set is not arbitrary. Let `chi` be its indicator, extended to the
origin by `chi(0) = n mod 2`. Triorthogonality says `chi` is orthogonal to every
check monomial of degree 1, 2 and 3, i.e. to `RM(3,r)`, so

```text
chi in RM(r-4, r),     |chi| = n + (n mod 2).
```

The check support is a Reed-Muller codeword. This is the fact both
classifications are built on: at `r <= 6` the code is `RM(2,6)`, so every
geometry with at most six checks is cut out by one quadratic equation; at
`r = 7` it is `RM(3,7)`, whose affine orbits are tabulated. It also gives the
free arithmetic screens, since `RM(r-4,r)` has minimum weight 16 and (by
Kasami-Tokura) no weights strictly between 16 and 32 other than 24, 28 and 30:
every nontrivial level-3 factory has `r >= 4` and `n >= 15`, and `n` can never
lie in 17-22 or equal 25 or 26.

## Two metrics per gate, and why both

Every catalogued row reports two numbers about its gate, computed by
[`factorylib/metrics.py`](../factorylib/metrics.py) from the
two shared modules below.

**Exact minimal `T`-count**
([`factorylib/tcount.py`](../factorylib/tcount.py)). A
level-3 diagonal gate is a product of `pi/4` rotations on parities,
`f(x) = sum_y a_y (y . x)` mod 8, and the `T`-count of one such representation
is the number of odd `a_y`. The representation is not unique: two of them
differ by an element of the Amy-Mosca kernel, a punctured `RM(k-4,k)` code. So
the exact minimum is the minimum-weight coset leader of `(a_0 mod 2) + V`,
computed by solving `M a = f` over `Z_8` by Smith normal form and then
minimising the weight over the coset. This is exact, not an estimate, and is
practical through `k = 6`.

**CNOT-frame-reduced phase-polynomial degree**
([`factorylib/degree.py`](../factorylib/degree.py)). The
deposited gate is only defined up to the CNOT frame of the output qubits:
conjugating by `M` in `GL(k,2)` sends `f(x)` to `f(Mx)`. A size-`s` monomial is
*genuine* (not absorbable into Cliffords) exactly when its coefficient is
nonzero mod `2^s`; the reduced degree is the minimum, over all output frames, of
the largest genuine monomial size.

The two answer different questions and neither implies the other. Degree says
what kind of resource this is: a gate of reduced degree 1 is a product of `T`s
in a rotated output frame, however elaborate its written phase polynomial, while
reduced degree 3 genuinely needs `CCZ` content. `T`-count says what it costs.
The `[[31,5,3]]` gate — the sum of every nonempty monomial on five outputs,
25 written terms including ten `CCZ`s — has reduced degree 1 and exact
`T`-count 1. Elsewhere in the catalogues reduced degree 1 occurs with `T`-counts
up to 6, while the largest `T`-counts recorded, 10 and 11, sit at reduced
degree 3. Reporting both is what makes the catalogues comparable across
directories, and both are invariant under the deduplication choices discussed in
[`02_classification.md`](02_classification.md).
