# The two complete windows

Theory behind [`../classification/legacy/exhaustive_n38/`](../classification/legacy/exhaustive_n38/)
and [`../classification/legacy/rank7_census/`](../classification/legacy/rank7_census/).
Both directories answer the target-agnostic question — *which gates exist at
all* at distance 3 — rather than "can we build gate `X`", and both are complete
inside a stated window. The windows are complementary cuts through the same
space:

| directory | window | outer input | what is closed |
| --- | --- | --- | --- |
| [`exhaustive_n38`](../classification/legacy/exhaustive_n38/) | `n <= 38`, **every** check rank | Kasami-Tokura / Nezami-Haah affine class tables | every injection count up to 38 |
| [`rank7_census`](../classification/legacy/rank7_census/) | `r <= 7`, **any** `n <= 44` | Gillot-Langevin `RM(3,7)` orbit table | every check rank up to 7 |

Neither contains the other, and the `[[31,5,3]]` output-width certificate below
uses both at once.

Both are legacy stages: the exhaustive classification of generalised
triorthogonal protocols through `n <= 54`
([`../classification/length54/`](../classification/length54/)) supersedes
them, and they are kept for reproducibility and provenance
([`../classification/legacy/README.md`](../classification/legacy/README.md)).

## The outer input is a Reed-Muller classification

By [`01_factories_and_distance.md`](01_factories_and_distance.md), the
origin-augmented indicator of a check geometry with `r` checks is a codeword of
`RM(r-4, r)` of weight `n + (n mod 2)`. Classifying outer geometries is
therefore classifying Reed-Muller codewords up to a change of check basis, and
that is a solved problem in two different regimes.

**By weight.**
[`nezami_haah_reps.py`](../classification/legacy/exhaustive_n38/nezami_haah_reps.py) is
the entire external input to the `n <= 38` classification; everything else in
that directory is derived from it by computation. The Kasami-Tokura /
Nezami-Haah tables list every affine class of weight below `2.5 * d_min = 40`,
and each classified weight decides two consecutive injection counts, since
`c = n + (n mod 2)`:

```text
weight  16 -> n = 15,16    24 -> 23,24    28 -> 27,28    30 -> 29,30
        32 -> 31,32        34 -> 33,34    36 -> 35,36    38 -> 37,38
```

with 1, 1, 2, 1, 10, 1, 14 and 8 classes respectively. Weight 40 — that is,
`n = 39, 40` — would need the separate length-40 classification
([`../classification/legacy/n40/`](../classification/legacy/n40/)) and is
deliberately absent: asking for `n >= 39` raises an error rather than silently
returning a partial answer. Transcription from the published notebook is the
one place a silent error could enter, so it is checked three ways
(advertised weight, triorthogonality of every marked support, and published
class counts per weight) by `tests/test_reps.py`.

**By rank.** For `r <= 7` the relevant code is `RM(3,7)`, whose 3,486
`AGL(7,2)` orbit representatives Gillot and Langevin computed; the table ships
as [`data/B-0-3-7.dat`](../classification/legacy/rank7_census/data/B-0-3-7.dat). Of
those, 71 have nonzero weight at most 44 and are therefore relevant. One sweep
of `RM(3,7)` covers ranks 4, 5, 6 and 7 together: a rank-`r'` parent has
indicator in `RM(r'-4, r')`, and embedding into `F_2^7` multiplies it by one
linear factor per unused coordinate, giving total degree
`(r' - 4) + (7 - r') = 3`. The parser also provides a global certificate — after
one audited correction to a stabiliser entry, the 3,486 orbit sizes sum to
`2^64`, the number of words in `RM(3,7)` — and
`cli.py data-check` runs it in seconds. Run it before trusting anything built
on the table.

## Marking: from a classified support to a check parent

A class representative is a *support*: the set of points of `F_2^m` where its
indicator polynomial equals 1. A check parent is a set of `n` distinct nonzero
points. Turning one into the other requires choosing which point of the support
becomes the origin, and that choice is not free — different origins give
genuinely different parents.
[`marking.py`](../classification/legacy/exhaustive_n38/marking.py) does it in two
cases:

- `marked_even` (`n = |S|` even): the origin lies outside the support, so the
  check set is a translate of `S`, plus the case where an affine hyperplane
  misses the origin, which raises the ambient rank by one;
- `marked_odd` (`n = |S| - 1` odd): the origin lies on the support, so translate
  a support point to zero and drop it.

Marking is finite for the obvious reason: there are at most `|S|` support points
to promote to the origin, and in the rank-7 census exactly 128 origins per
orbit, giving `71 * 128 = 9,088` marked geometries. Both markers enumerate
*every* inequivalent origin, so the marked family is a superset of the
deduplicated one. That direction matters: a superset is exhaustive by
construction, which is what makes an absence statement over it a valid
certificate. Counting the other way — using the listed stabiliser generators to
shrink the sweep rather than to grow it — gives 618 covering representatives at
`r = 7`: 179 with `n <= 40` and 439 at `n` in `{43, 44}`, plus 16 of effective
rank at most six, for 634 in all. That reduced list is what the inner audit
below runs over. Because the marking
subgroup can refine a true stabiliser orbit, these are *covering*
representatives, not a claim of 634 distinct `GL(7,2)` classes.

## The quotient trick

Fix a parent. The conditions on a single output row `a` are all linear:
`a . h_j = 0` and `a . (h_i AND h_j) = 0` for all checks. Their solution space is

```text
R(C) = { a : a . h_i = 0 and a . (h_i AND h_j) = 0 }  =  (C^<2>)^perp,
```

which contains `C` itself. The key observation is that everything the
classification reads off a frame is invariant under `a -> a + c` for `c` in `C`:
the degree-1, 2 and 3 output parities and the mixed output-output-check
condition `|a AND b AND h_j| = 0` all descend. So the entire search descends to

```text
V = R(C) / C.
```

This is not a cosmetic simplification. Across the whole `n <= 38` ladder
`dim V <= 11` (audited), against an unquotiented row-code dimension of up to 16:
a factor `2^r` that is the difference between an enumeration that finishes with
no node budget consumed and one that does not.

In these coordinates a `k`-output factory is a `k`-subset of `V` that is
linearly independent and *pairwise compatible*, where `a` and `b` are compatible
when the `r` bilinear forms

```text
B_j(a, b) = < a, b AND h_j >
```

all vanish. Compatible frames are exactly the cliques of the compatibility graph
on `V \ {0}`, which is how
[`classify.py`](../classification/legacy/exhaustive_n38/classify.py) enumerates them.
Because each `B_j` is bilinear, compatibility is closed under XOR, so a clique
spans a compatible *subspace*; the parent-first engine exploits this and
enumerates subspaces by canonical row-reduced augmentation instead, so that two
bases of one subspace cannot be counted twice
([`03_parent_first.md`](03_parent_first.md)).

Distance is never inferred from this algebra. Every recorded frame is expanded
back to explicit columns and re-verified by
[`factorylib/verification.py`](../factorylib/verification.py), which shares no enumeration code
with the classifier on purpose.

## Three relations that are not the same relation

The single most misreadable thing about these catalogues is what "the same
factory" means. Three distinct relations are in play, and
[`dedup.py`](../classification/legacy/exhaustive_n38/dedup.py) keeps them apart.

**1. Permuting the outputs — `S_k`. This is the key of the classification
catalogues.** Sending output `i` to `sigma(i)` permutes the variables of the
phase polynomial. It is a relabelling of the *same* circuit, so factories
related this way are genuinely one entry. The classification catalogues key on
`(n, k, S_k`-canonical gate`)`, the lexicographic minimum over all `k!`
permutations of the encoded monomial set.

**2. Changing the output basis — a CNOT frame. This is a different circuit, and
gets its own catalogue row.** Replace the output rows by another basis of the
same subspace of `V`. The phase polynomial is read off *pointwise products* of
the rows, a nonlinear function of the basis, so it changes.

The worked example is `[[28,2,3]]`, which appears twice in the catalogue. Take
a compatible independent pair `(a_0, a_1)` with `|a_0|` and `|a_1|` odd and
`|a_0 AND a_1|` even: the gate is `0+1`, that is `T_0 . T_1`. Re-read the same
subspace in the basis `(a_0, a_0 + a_1)`. Now `|a_0 + a_1|` is even, while
`|a_0 AND (a_0 + a_1)| = |a_0| - |a_0 AND a_1|` is odd, so the gate is `0+01`,
that is `T_0 . CS_01`. One subspace, two circuits, two `S_k` rows.

They are nevertheless one *magic state*. The phase lives in `Z_8`, and
substituting `x_1 -> x_0 + x_1` into the phase `x_0 + x_1` of `T_0 . T_1` gives
`x_0 + (x_0 + x_1 - 2 x_0 x_1) = 2 x_0 + x_1 - 2 x_0 x_1`: the `T` on `x_1` and a
`CS` on `{0,1}`, times the Clifford `S_0` and `CS_01^2 = CZ_01`, which is `0+01`
after swapping the outputs. This relation — the gate up to an invertible change
of the output basis and diagonal Clifford corrections, the CNOT+S output
equivalence of the length-54 classification — is decided by
[`master_catalog/glcanon.py`](../master_catalog/glcanon.py) through the gate's
third finite difference, a symmetric trilinear form that is covariant under the
frame change and vanishes exactly on Cliffords. **It is the key
of the master catalogue**, together with the distance — `(n, k, d, gate up to
CNOT+S)` — so the two `[[28,2,3]]` frames are one master row, while circuits for
one gate at different distances stay separate rows.
Because an `X` on an output only adds a level-2 phase, affine frames give
nothing more.

**3. The `F_2` truth-table annotation — stored in the classification
catalogues, never as a key.** This is the orbit of the gate's monomial set read
as a Boolean function — its `2^k`-bit XOR truth table over `F_2` — under
variable substitution `f -> f o M` for `M` in `GL(k,2)`, recorded per row as
`gate_gl_canonical` / `gl_class` (the lexicographically minimal truth table
over the orbit). Since permutation matrices lie in `GL(k,2)`, it is coarser
than the `S_k` key. It is *not* the magic-state relation of 2: reducing the
phase to `F_2` discards the `Z_8` carries that a substitution creates, so `0+1`
and `0+01` above get canonical truth tables 6 and 2 and land in different
annotation classes although they are the same gate up to a CNOT frame and
diagonal Cliffords. Canonicalisation is cheap through `k = 4` and still
feasible, cached, at `k = 5`; `|GL(k,2)| = 6, 168, 20160, 9999360` for
`k = 2, 3, 4, 5`.

Which key? A CNOT frame change is free at the Clifford level, so the coarser
key is right if you care which magic state comes out, and the finer one if you
care which written phase polynomial a circuit deposits. The two `[[28,2,3]]`
frames have different phase polynomials but the same exact `T`-count (2) and
the same reduced degree (1), since both are CNOT-frame invariants. The
classification catalogues keep the finer `S_k` key, so **their row counts are
representation-dependent upper bounds on the number of inequivalent gates**.
The master catalogue keys on the magic state: one row per CNOT+S class, stored
as one representative frame, with every absorbed frame's provenance kept in
`sources`. Maxima — largest `k`, largest `T`-count, which gates occur at all at a
given `n` — are properties of the set of realisable gates rather than of how the
set is partitioned, and are the same under both keys.

## The one hard parent

[`classify.py`](../classification/legacy/exhaustive_n38/classify.py) finishes every
marked parent in the `n <= 38` ladder without a budget hit except one:
weight-32 class 0 marked odd, which is the set of all 31 nonzero points of
`F_2^5`. That parent is maximally symmetric — every invertible `5 x 5` matrix
over `F_2` permutes the nonzero points, so its automorphism group is all of
`GL(5,2)`, of order 9,999,360 — and its quotient has `dim V = 11`. Plain frame
enumeration over the `2^11 - 1 = 2047` nonzero quotient points revisits the same
gate millions of times.

[`hard_parent_n31.py`](../classification/legacy/exhaustive_n38/hard_parent_n31.py) uses
the symmetry instead of fighting it. A qubit relabelling by `M` in `GL(5,2)` is
a physical relabelling: it permutes the 31 columns, preserves the check code,
and leaves the logical gate invariant — which the module checks rather than
assumes, by transporting `GL(5,2)` (generated by elementary transvections)
through the quotient construction to its induced action on `V`, verifying that
the degree-1 parity is constant on orbits and spot-checking that whole gates
are orbit-invariant. Every compatible frame is then `GL(5,2)`-equivalent to one
whose first output is an orbit representative, so fixing the first output loses
no gate class while cutting the search by orders of magnitude. This is where the
unique `[[31,5,3]]` class — the widest factory anywhere in the `n <= 38` window
— comes from.

## Scope: what "exhaustive" covers, precisely

Read this before quoting the word.

The `n <= 38` enumeration covers factories whose `k` output rows are linearly
independent **modulo the check span `C`**. Frames using both `a` and `a + c`,
for `c` in `C`, as two separate output qubits are not enumerated.

The first objection to that is the right one to raise, and it is worth answering
carefully because it is the crux of the descent argument. Adding a check row to
an output row cannot change the gate: replacing `a` by `a + c` leaves every
degree-1, 2 and 3 parity alone, and *that invariance is exactly the descent*
above — it is why the gate is a function of `V` at all. So a relabelling of this
kind is not a missing case; there is nothing there to miss. The frames the
engine skips are different objects: they use `a` **and** `a + c` as two separate
output qubits, which is a larger circuit on more qubits rather than a
relabelling of a smaller one.

Such a frame is real: the columns come out distinct, all check-touching parities
vanish, and the fault distance is 3. Its gate is forced, and always the same
one. Check rows have even weight, so `|a|` odd forces `|a + c|` odd; and since
`a` lies in `R(C)`, `|a AND c|` is even, so `|a AND (a + c)| = |a| - |a AND c|`
is odd. The gate is therefore

```text
0+1+01   =   T_0 . T_1 . CS_01,
```

with no other possibility. Ansatz-free column-level SAT finds one: a
`[[15,2,3]]` with gate `0+1+01` over the `[[15,1,3]]` check part, 6 rows of
rank 5, exact T-count 1. It is deliberately **not** in the search catalogue —
[`../symmetry_sat_search/`](../symmetry_sat_search/) rejects a declared width
whose output rows are dependent modulo the check span, since one output CNOT
leaves the extra wire idle and the circuit is just the `[[15,1,3]]` again. The
row-space enumerator and `tests/test_classification.py` are where these frames
are exhibited.

**These frames carry no extra magic.** One output CNOT replaces the second row
`a + c` by `c`, which carries no monomial of any degree: `|c|` is even, because
check rows have even weight and weights add mod 2 under XOR; `|c AND a'|` is
even for every `a'` in `R(C)`, because `R(C)` lies in the dual of `C`; and
`|c AND a' AND a''|` is even for every compatible pair, because pairwise
compatibility says `|a' AND a'' AND h_j|` is even for each check row `h_j`, and
that extends to all of `C` by the same parity argument. So after one Clifford
the extra output is an idle `|+>` spectator, and what remains is exactly the
lower-width factory the classification does enumerate. The arithmetic says the
same thing: `T_0 . T_1 . CS_01` has exact minimal T-count **1**, not 2, because
`x0 + x1 + 2*x0*x1 = (x0 XOR x1) + 4*x0*x1` — one T on the parity of the two
outputs, times a CZ. The `[[15,2,3]]` described above has exact T-count 1 for
that reason, which is why the search catalogue does not carry it.

So the catalogue is complete for magic **content** — which gates are achievable
at each `n`, the largest genuine output width, the largest exact T-count — and
incomplete only for circuit **representations** in which an output is
Clifford-equivalent to an idle spectator.
[`classify.py`](../classification/legacy/exhaustive_n38/classify.py) already discards
frames with a *manifestly* idle output, so this is the same policy one Clifford
deeper rather than a different one.

Two things remain true on top of that. The quotient method structurally cannot
represent these frames: the gate of such a frame depends on which lift of a
quotient point you pick, so it is not a function of `V`, and the descent
argument that makes the quotient search complete is precisely the statement that
gates *are* functions of `V`. Reaching them requires the row space
([`classify_rowspace.py`](../classification/legacy/exhaustive_n38/classify_rowspace.py),
which enumerates frames independent in `R(C)` rather than in `V`, and doubles as
an independent cross-check of the quotient engine) or raw column-level search.
And if you are counting distinct *circuits* rather than distinct resources — say
a spectator output is free in your architecture and you would rather have the CZ
than the CNOT — then the catalogue undercounts, and `classify_rowspace.py` is
the tool. `tests/test_classification.py` pins both halves down on the small end
of the ladder: the row-space enumerator finds exactly the quotient classes plus
lift-degenerate ones with gate `0+1+01`, and the CNOT'd row of every extra class
carries no monomial of any degree.

## What the classifications prove

**At `n <= 38`, every check rank**
([`CLASSIFICATION_N38.md`](../classification/legacy/exhaustive_n38/catalog/CLASSIFICATION_N38.md)):
74 distinct `(n, k, S_k`-gate`)` classes, all with explicit verified circuits —
22 `T`-only, 24 `CS`-level, 28 `CCZ`-level.

- **Pure `CCZ` — the monomial `012` alone — never occurs.** Inside this window
  `CCZ` content appears only inside larger degree-at-most-3 combinations. This
  table is the witness for the distance-3 lower bound `n(CCZ) >= 39`.
- **Maximum output width is `k = 5`**, attained only by the fully symmetric
  `[[31,5,3]]` class, and **no `k = 6` factory exists in the window.**
- The highest exact minimal `T`-count in the window is 4.

The width ceiling is certified by splitting the parents by effective check rank
and using both directories
([`docs/N38_K56_CERTIFICATE.md`](../classification/legacy/exhaustive_n38/docs/N38_K56_CERTIFICATE.md)).
At effective rank at most 7, the complete `RM(3,7)` census over all 9,088 marked
origins shows compatible dimension 5 occurs only at `n = 31` (992 compatible
5-spaces there, collapsing to one `S_5` gate class) and that there are no
compatible 6-spaces. At effective rank 8 or more, `dim V <= 4` throughout the
layer, so five or six independent outputs are impossible outright.

**At `r <= 6`**: up to a linear change of check basis there are exactly 19
nonempty distance-`>= 3` geometries, with injection counts

```text
n in {15, 16, 23, 24, 27, 28, 31, 32, 35, 36, 39, 40, 47, 48, 63},
```

so no factory of any target has `41 <= n <= 46` with at most six checks. The
proof is a complete orbit decomposition of all `2^22` words of `RM(2,6)` under
`GL(6,2)`, returning 20 orbits whose sizes sum to 4,194,304 — the completeness
certificate — one of them the zero word. Eighteen of the nineteen have
`kappa_4 = 0`: no legal output direction survives at distance four at all. The
exception is the 32-point affine cap, which contains no line and so has
`kappa_4 = kappa_3 = 10`, and the universal colour test shows it carries no
linear, quadratic or cubic content whatsoever. Hence **every distance-`>= 4`
factory with a nontrivial level-3 target has at least seven checks.**

**At `r <= 7`, `n <= 44`**
([`CENSUS_R7.md`](../classification/legacy/rank7_census/catalog/CENSUS_R7.md)): running
the full inner audit — every compatible output subspace, then its phase, rather
than a list of named targets — over the 634-representative covering list gives
1,337 compatible six-spaces, 8 seven-spaces (all with nonzero phase radical, so
they expose a spectator output under a logical CNOT and are already counted at
smaller `k`), and no eight-spaces. Therefore every spectator-free output phase,
product or entangled, has **at most six essential output qubits and exact
minimum `T`-count at most five**, with the bound five attained only at `n = 43`.
The shipped catalogue lists the 21 `(n, k, S_k`-gate`)` classes realising
`T = 5`, all at `n = 43`, with explicit circuits — deduplicated from 28 stored
witnesses under the `S_k` key, so 21 counts classes and 28 counts circuits.

Two optimality statements follow unconditionally for at most seven checks:
`[[44,4,3]]` is optimal for `T^4`, `[[47,3,3]]` is optimal for pure `CCZ`, and
`n_3(CS^2) >= 47` and `n_3(T^5) >= 47`.

Two cautions. The census bound does not extrapolate past `n = 44` — at `n = 47`
the six-check `CCZ` geometry already carries verified phases of exact `T`-count
10 and 11 — and completeness is a runtime property, not a promise: every
expensive stage in the census carries a budget, and **only a run whose top-level
`complete` flag is true is a classification certificate.** Anything else is
search data.
