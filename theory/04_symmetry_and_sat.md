# Symmetry ansatz and SAT

Theory behind [`../symmetry_sat_search/`](../symmetry_sat_search/). Two search
paradigms live here. They trade completeness against reach in opposite
directions, and the catalogue keeps their claims apart.

## Ansatz-free column-level SAT

[`sat_search.py`](../symmetry_sat_search/sat_search.py) searches the entire
circuit space. One boolean variable per nonzero column `alpha` of `F_2^N`, with
`v_alpha = 1` meaning the parity rotation on that support is in the circuit.
Qubits `0..k-1` are outputs, the rest postselected checks. The constraints are
the definition of a factory, written out:

- **target parity**, one XOR constraint per monomial of degree 1 up to the
  Clifford level: `XOR_{alpha superset m} v_alpha = D[m]`, with `D[m] = 0` on
  every monomial touching a check qubit;
- **distance clauses** forbidding every undetected fault below `d`: at `d >= 2`
  no selected column is output-only; at `d >= 3` no two selected columns XOR to
  an output-only error; at `d >= 4` no three do;
- **objective**: minimise `sum_alpha v_alpha`, the `T`-count.

The level parameter sets the constraint degree — 2 for `S`/`CZ`, 3 for
`T`/`CS`/`CCZ`, 4 for `sqrt(T)`/`CT`/`CCS`/`CCCZ` — and distance is
level-independent. There is an optional symmetry break: the check qubits, and
for a fully symmetric target such as `T^k` the output qubits too, are
interchangeable, so for each adjacent transposition the model gets a
lexicographic-leader constraint `x <= sigma(x)`. That never removes the
lex-minimal member of an orbit, so the search stays complete; it only prunes
duplicates.

The default backend is CP-SAT, which has native boolean XOR and a linear
objective and therefore returns a genuine `OPTIMAL` or `UNSAT` certificate;
python-sat with CaDiCaL (Tseitin XOR, sequential-counter cardinality, minimum
found by at-most-`k` bisection) and CryptoMiniSat (native XOR clauses for the
parity equations) are available and mirror the same semantics. Every returned
factory is re-verified at the column level by
[`evaluator.py`](../symmetry_sat_search/evaluator.py).

What this buys is the strongest claim in the repository for a single
`(k, N, target, d)`: a **certified global minimum `T`-count**, or `UNSAT`
meaning no factory with those parameters exists at all. What it costs is
`2^N - 1` variables. The formulation is practical to roughly `N = 9`.
The stable CLI in [`sat_search.py`](../symmetry_sat_search/sat_search.py)
reproduces the small distance-2 and distance-3 factories directly; retained
explicit circuits from larger searches live in the single curated source
[`examples/found_factories.json`](../symmetry_sat_search/examples/found_factories.json).

## The slot ansatz

[`slot_search.py`](../symmetry_sat_search/slot_search.py) buys reach by giving
up "all columns". Declare `k` outputs plus a list of *check blocks*, each block
carrying a group: `('S', lam)` for the full symmetric group on `lam` check
qubits, `('C', lam)` for the cyclic group, or `('P', lam, gens)` for an explicit
permutation group. The group's orbits on subsets of the block become the
vocabulary: for `S` the orbits are the subsets of each fixed size, for `C` they
are necklace classes — far fewer gates per orbit and a much richer label
vocabulary, which is what `CCZ` targets need.

A **label** picks one orbit index per block. Together with an output pattern `P`
it defines a **slot**: the columns `P union (one member set per block of the
chosen orbits)`, `label_cost` of them, the product of the orbit sizes. A slot
enters the circuit wholly or not at all, so the selected circuit is a union of
full orbits and is invariant under the block groups by construction. The
all-empty-check label is excluded, since its columns would be output-only and
hence weight-one undetectable faults.

The gain is that the model has one variable per `(label, pattern)` rather than
per column, and because the circuit is a union of full orbits, monomial parities
are constant on symmetry classes: one XOR constraint per monomial *class*, using
one representative point-set per block, suffices. CP-SAT then gets an
at-most-one rule per label, those XOR constraints, and the objective
`sum label_cost * x`, and proves optimality of the `T`-count. Optional knobs —
a `T`-count cap turning optimisation into feasibility, restricted orbit sizes, a
whitelist of output patterns, `phase_support_only`, and redundant but sound
affine-slice Reed-Muller weight domains — narrow the model further;
`phase_support_only` in particular is a search ansatz, not a WLOG theorem, and
the docstring says so.

Note what is *not* symmetrised: the output patterns. A group may propose the
geometry, but the labels must be freed and solved. At distance three each
syndrome occurs at most once, so an output label invariant under a group
permuting two or more outputs would be constant on each block, leaving only the
all-zero and all-one labels and at most one essential output direction. Imposing
invariance on the labels — the natural way to make a symmetric search cheap —
destroys every multi-output factory at distance three.

### The structural distance rules

Distance three is free in this ansatz. Block supports are disjoint, so a
column's check part determines its label and its member combination, and
selected columns therefore have pairwise distinct nonzero check parts — which is
exactly the distance-three normal form.

Distance four is imposed structurally, and here the model over-approximates. For
each block, tabulate which orbit triples contain three member sets XORing to the
empty set; then forbid every label triple that can cancel on *every* check block
unless the three output patterns XOR to zero. This is sound — it never admits a
`d < 4` circuit — but it is conservative: the per-block cancelling columns always
exist inside the slots, yet they may fail to be three *distinct* columns, so
some genuinely distance-four factories are excluded.

[`exact_d4.py`](../symmetry_sat_search/exact_d4.py) drops the over-approximation
by CEGAR. Minimise the `T`-count subject to the slot rule and target parity
only; verify the true distance of the optimum; if an undetected weight-three
logical fault exists, forbid exactly that `(slot, output)` combination and
re-solve; stop when the CP-SAT optimum verifies as `d >= 4`. Every added clause
removes only genuinely `d < 4` configurations, so once the relaxed optimum lands
in the true-feasible set it *is* the true optimum — the exact slot-ansatz
optimum for that geometry.

### What the ansatz reaches

The slot searches produce the distance-3, distance-4 and distance-5 records in
the catalogue: `[[47,3,3]]` for `CCZ` on `S1+S1+S2+S2` at `N = 9`, `[[64,1,4]]`
on `C9`, `[[66,3,4]]` for `CCZ` on `C9`, `[[141,2,4]]` on `C7+S3`, `[[85,1,5]]`
on `S5+S5`, and — from an ansatz seeded with the automorphism group of the
Bravyi-Haah `[[49,1,5]]` — `[[48,1,4]]` and `[[49,1,5]]` at `N = 14`. None of
these is reachable by the raw column search, and none of them is a classified
maximum.

## Recovered symmetry groups

The slot ansatz *starts* from a group, so the group plus one representative
column per orbit is what actually generates the factory. But that group lived
only in the search driver and in a log file's geometry tag: the shipped circuits
are flat column lists, and a reader could not recover the structure that
produced them.

[`symmetry_groups.py`](../symmetry_sat_search/symmetry_groups.py) fixes this by
computing, for each catalogued factory, the group

```text
Aut(F) = { permutations pi of the N qubits :
           pi maps the column SET to itself,
           and maps the output block {0..k-1} to itself }
```

directly from the columns, and writing generators, order and induced column
orbits to
[`catalog/symmetry_groups.json`](../symmetry_sat_search/catalog/symmetry_groups.json).
Recomputing `Aut(F)` is strictly better than recording the design group:

- it applies **uniformly** to every catalogued factory, including the ones found
  by raw column-level SAT with no ansatz at all;
- it is a property of the **circuit**, not of the search that happened to find
  it, so anyone holding the columns can reproduce it;
- it **can be larger than the design group** — a solution found inside an
  `S_4 x S_4` ansatz may turn out to have extra symmetry — which is itself
  information about the construction.

The computation is backtracking over qubit images with two prunings: a colour
refinement (each qubit is coloured by whether it is an output and by the sorted
multiset of weights of the columns containing it, refined once against
neighbours; a qubit may only map to a qubit of the same colour), and a
partial-consistency check (after fixing images on a prefix `A`, the multiset of
column intersections with `A` must map onto the multiset of intersections with
`pi(A)`). Across the catalogue `N <= 14` and the groups are small, so the full
group is enumerated exactly rather than estimated by a stabiliser chain;
`GROUP_CAP = 2,000,000` bounds the enumeration and hitting it is reported as
`complete: false`, never silently truncated.

The round trip is what makes the data meaningful rather than decorative.
[`rebuild_from_groups.py`](../symmetry_sat_search/rebuild_from_groups.py) throws
the stored column list away, closes the orbit representatives under the stored
generators, and then verifies the reconstruction from first principles: that it
has exactly `n` columns and equals the catalogued set; that every
degree-at-most-3 monomial touching a check has even parity; that the output
parities reproduce the catalogued gate; and that the true circuit distance,
exact through weight 4, equals `d`. Nothing in the last three steps consults the
stored columns. A pass means the group and the representatives really do
determine the factory, and when the orbit count is much smaller than `n` the
pair is a genuinely compressed description — the same compression the slot
ansatz exploits during the search.

## A record is not a classified maximum

Say it plainly, because the catalogues sit side by side and invite the
confusion. A row from [`../classification/exhaustive_n38/`](../classification/exhaustive_n38/)
or [`../classification/rank7_census/`](../classification/rank7_census/) is a
statement that nothing else exists in that window. A row from this directory is
the best that a particular search found, and there are three distinct strengths
among them:

| claim | scope | what may still improve |
| --- | --- | --- |
| certified minimum (raw SAT) | every circuit on `N` qubits with that target and distance | nothing, at those parameters; larger `N` is open |
| ansatz optimum (`slot_search`, `exact_d4`) | every circuit inside the declared block symmetry | any non-symmetric circuit, or a different block structure |
| witness | one explicit verified circuit | any other circuit |

Only the first is a global statement, and only within its `(k, N, target, d)`.
The slot records are optimal *within* their ansatz; that qualifier is not
removable by running longer.
