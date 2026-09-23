# Theory notes

Background for the code in this repository: what the shared object of study is,
what each search directory actually computes, and exactly how strong each of its
claims is. These notes are the written account of the results -- they are
self-contained, and each one names the code that produces what it describes.

## What a magic-state factory is here

Throughout this repository a *factory* is a diagonal, level-3, generalized
triorthogonal circuit on `N = k + r` qubits: `k` output wires, indexed
`0..k-1`, and `r` postselected check wires. Every physical injection is one
parity rotation

```text
P_alpha = exp[ i (pi/8) ( I - prod_{a : alpha_a = 1} Z_a ) ],
```

so a circuit is nothing but a set of columns, each column the qubit support of
one such rotation. That is literally how circuits are stored: a column is a
list of qubit indices, outputs first. The same vector `alpha` labels the
`Z` fault that a faulty injection deposits, which is why one object carries
both the logical action and the fault model.

Reading the circuit as a binary matrix (rows = qubits, columns = injections)
gives the *check part* `C` — the span of the `r` check rows — and the `k`
output rows. Postselection keeps only runs in which every check measurement
passes, and the accepted logical action is read off the output-only overlap
parities of the rows: `|a_i|` odd is a `T` on output `i`, `|a_i AND a_j|` odd a
`CS`, `|a_i AND a_j AND a_l|` odd a `CCZ`. For the circuit to deposit that gate
and nothing else, every degree-at-most-3 parity touching a check wire must be
even.

`[[n, k, d]]` records `n` injections consumed, `k` protected outputs, and
circuit distance `d`: the minimum size of a fault set that passes every check
and still acts nontrivially on the outputs. The quantity to minimise is `n`.
See [`01_factories_and_distance.md`](01_factories_and_distance.md) for the
precise definitions and for why distance three turns the whole problem into
finite geometry.

## Three attacks on one problem

There are four code directories, implementing three different strategies
against the same feasible set.

**Classify everything in a window.**
[`../classification/exhaustive_n38/`](../classification/exhaustive_n38/) and
[`../classification/rank7_census/`](../classification/rank7_census/) each close
a complete window and are complementary cuts through the same space. The first
fixes the injection count and closes *every* check rank: for each classified
Kasami-Tokura / Nezami-Haah check-support class up to `n = 38` it enumerates
every way of attaching output rows, in the quotient `V = R(C)/C`, and reads off
the gate. The second fixes the check rank and closes *every* length up to
`n = 44`: rank-at-most-7 check supports are exactly the codewords of `RM(3,7)`,
which Gillot and Langevin have classified, so sweeping their orbit table and
auditing the inner problem on each marked geometry settles `r <= 7` outright.

**Filter a parent, then solve.** [`../parent_first/`](../parent_first/) does not
enumerate anything by itself. It takes one check parent and computes the
cost-ordered filter chain `tau_D <= mu_d <= kappa_d`: how many output
directions are individually legal, how many can coexist, and how wide a
requested target family can actually be realised. Each filter is a cheap
necessary condition that can kill a parent before the expensive stage runs.
The rank-7 census drives the same [`factorylib/parent.py`](../factorylib/parent.py) implementation over its whole outer enumeration,
so this directory is both a standalone triage tool and the inner engine of one
of the classifications.

**Search with an ansatz, or exhaustively.**
[`../symmetry_sat_search/`](../symmetry_sat_search/) contains two solvers that
do not use parents at all. Column-level SAT allocates one boolean per nonzero
column of `F_2^N`, adds parity and distance clauses, and returns a certified
global minimum `T`-count — complete, but with `2^N - 1` variables. The slot
ansatz instead fixes check blocks carrying a symmetric or cyclic group,
enumerates group orbits rather than individual columns, and solves with CP-SAT;
that is optimal only *within* the ansatz, but it scales far past the raw search
and produces the distance-3, 4 and 5 records in the catalogue.

## Which note explains which directory

| note | explains | code |
| --- | --- | --- |
| [`01_factories_and_distance.md`](01_factories_and_distance.md) | the shared object: columns, phase polynomial, level, the factory condition, the punctured simplex, circuit distance, the finite-geometry picture, the two reported gate metrics | all four directories |
| [`02_classification.md`](02_classification.md) | the two complete windows, the quotient trick, marking, the `S_k` key versus CNOT frames versus `GL(k,2)`, and the precise scope of the quotient method | [`../classification/exhaustive_n38/`](../classification/exhaustive_n38/), [`../classification/rank7_census/`](../classification/rank7_census/) |
| [`03_parent_first.md`](03_parent_first.md) | the colored quotient, the `kappa`/`mu`/`tau` chain, why the ordering pays, and what a budget hit does and does not certify | [`../parent_first/`](../parent_first/), reused by [`../classification/rank7_census/`](../classification/rank7_census/) |
| [`04_symmetry_and_sat.md`](04_symmetry_and_sat.md) | ansatz-free column SAT, the slot ansatz and its distance rules, and the recovered automorphism groups | [`../symmetry_sat_search/`](../symmetry_sat_search/) |
| [`notation.md`](notation.md) | symbols, gate strings, geometry tags, distance conventions | all four directories |
| [`PROVENANCE.md`](PROVENANCE.md) | where every published number comes from: the run or derivation behind each quoted factory, and how strong that makes it | all four directories |
| [`figures/README.md`](figures/README.md) | the cross-cutting landscape figure and how to read its bands | [`figures/landscape_all.py`](figures/landscape_all.py) |

## How to read this repository

Read [`01_factories_and_distance.md`](01_factories_and_distance.md) first: every
other note assumes the column picture and the geometry/phase split. After that
the notes are independent, and each one points at the module whose docstring
carries the implementation detail — the docstrings are the primary source and
are written to be read. The catalogues
([`../classification/exhaustive_n38/catalog/CLASSIFICATION_N38.md`](../classification/exhaustive_n38/catalog/CLASSIFICATION_N38.md),
[`../classification/rank7_census/catalog/CENSUS_R7.md`](../classification/rank7_census/catalog/CENSUS_R7.md),
[`../symmetry_sat_search/catalog/FACTORY_CATALOG.md`](../symmetry_sat_search/catalog/FACTORY_CATALOG.md))
are generated, never hand-edited, and every row ships explicit columns that a
standard-library verifier re-checks from scratch. The one habit worth forming
before reading any table: check which regime a row lives in. A row from a
classification window is a statement that nothing else exists there; a row from
a search is the best that was found. [`figures/landscape_all.py`](figures/landscape_all.py)
draws that distinction as coloured bands, and
[`PROVENANCE.md`](PROVENANCE.md) traces every quoted factory back
to the run that produced it.
