# A new distance-three rate family, built and verified

Analysis date: 2026-09-18. Adapted from the companion AI repository’s Astra analysis; historical baseline comparisons refer to that analysis. Witnesses and self-contained reconstruction tools accompany this report.

The most useful result of this investigation is a concrete improvement, rather
than another proposal to extend a stalled simplex search: **pure-T distance-three
factories at `n/k = 5`, including `[[495,99,3]]` and `[[880,176,3]]`.** The best
distance-three rate in the shipped catalogue was `862/162 = 5.32098765`.
The improvement is **6.03% in raw T states per output**. This is a distance-three
rate result, not an improvement to the overall exponent record
`[[850,128,6]]`, `gamma = 1.056618`.

**The old small-size targets are now met as well.** During independent review,
the root agent constructed and verified **`[[255,47,3]]`**, with `A3 = 1995` and
`N = 62`, by gluing four 63-to-11 components and three 15-to-1 components on
`K7`. Its witness is `witnesses/graph_heterogeneous_n255_k47_d3.json`, reproduced
by the companion analysis tool `Astra suggestions/tools/heterogeneous_graphs.py`. This uses 15
checks and leaves the restricted eight-check full-simplex question open.
At the 511-input budget, `[[495,99,3]]` exceeds the
old target of 93 outputs with 16 fewer inputs than the budget.

The mechanism combines existing small factories through a graph of paired-column
contractions. The small components were already available; the previous rate
campaigns compared against their uncontracted direct sums. That comparison missed
a useful family.

## Verified witnesses

Each row below was built from raw catalogue columns. Verification recovered all
degree-one, degree-two and degree-three parity moments, confirmed exactly `T^k`,
checked full output rank modulo independent checks, and exhaustively counted
harmful faults of weights one, two and three. Every distance in this table is
**exactly three**, with zero harmful faults at weights one and two.

`A3` counts harmful fault patterns for the entire block. `Abar3` is the mean
single-output leading coefficient, independently counted by the root agent as
`sum_faults popcount(logical_error)/k`. **`A3/k` is not `Abar3`.**

| Factory | Graph and seed | `n/k` | `gamma` | `A3` | `Abar3` |
|---|---|---:|---:|---:|---:|
| **`[[495,99,3]]`** | `K9`, nine `[[63,11,3]]`, eight compatible ports each | **5.000000** | **1.464974** | **3971** | **180.535354** |
| **`[[880,176,3]]`** | `K8,8`, sixteen `[[63,11,3]]`, eight compatible ports each | **5.000000** | **1.464974** | **6896** | **169.909091** |
| `[[399,77,3]]` | `K7`, seven `[[63,11,3]]`, six independent ports each | 5.181818 | 1.497486 | 3395 | 200.090909 |
| `[[684,132,3]]` | `K6,6`, twelve `[[63,11,3]]`, six independent ports each | 5.181818 | 1.497486 | 5760 | 194.181818 |
| `[[960,184,3]]` | `K8`, eight `[[127,23,3]]`, seven independent ports each | 5.217391 | 1.503713 | 18032 | 540.782609 |
| **`[[909,171,3]]`** | `K9`, nine HH18 `[[109,19,3]]`, eight independent ports each | **5.315789** | **1.520720** | **2005** | **63.771930** |

The 909-input row is an alternate tradeoff, with a much smaller logical-error
coefficient. It improves slightly on the old 862-input rate while beating its
block coefficient, but it is slower in raw rate than the 495-input construction.
The larger independent-port examples are useful transparent controls for the
construction, not preferable choices after the rate-five examples exist.

The witnesses are in [`witnesses/`](witnesses/), with names giving their parameters.
The root report and operating-point audit make the finite-error comparisons;
the table here does not turn a raw-rate improvement into an unconditional
operational claim.

## The construction in columns

Write column `j` of a component as `(s_j, o_j)`, with check syndrome `s_j` and
logical-output vector `o_j`. Choose a set of columns called ports. The important
condition is

```
rank{(s_j,o_j): j in ports} = rank{s_j: j in ports}.
```

Equivalently, the output vector on the ports is a linear function of the check
syndrome. Adding check rows to output rows therefore makes every selected port's
output part zero, without changing the logical gate.

Take a direct sum of components, assign a different port to each incident graph
edge, identify the check syndromes of the two ports on that edge, and cancel the
two now-equal columns. Each edge saves two T inputs. The construction preserves
the degree-three signature because restricting to the annihilator of a column
difference makes the two columns equal, and two equal columns cancel in every
binary parity moment.

For `b` identical components of size `n0` and output width `k0`, a graph with `E`
edges gives

```
n = b*n0 - 2*E,          k = b*k0.
```

Distance must still be established. In the **independent-port case**, it has a
short proof. Put the ports in distinct coordinate directions of each component's
check space. After identifying an edge's two directions, a surviving column is
a subset of the incident edge coordinates, possibly together with check
coordinates private to that vertex. Two different vertices share at most one
edge in a simple graph. A surviving column consisting solely of that shared
edge would have been the deleted port. Thus all surviving syndromes are distinct
and nonzero, giving `d >= 3`. Explicit harmful triples pin the distance at three.

This also explains why the earlier simplex width plateaus are irrelevant:
the check rank grows across the graph, rather than remaining seven, eight or
nine. For example, `[[495,99,3]]` has 19 independent checks.

For dependent ports, this simple proof no longer applies. The two rate-five
witnesses have their distance established by the full weight-one/two/three
verification, not by asserting that every gluing automatically preserves it.

## Why the 63-input component wins

Saturating a component's `r` independent check directions gives a regular graph
with raw rate `(n0-r)/k0`. A cheap scan of the shipped pure-T distance-three seeds
gives:

| Component | `r` | `(n0-r)/k0` |
|---|---:|---:|
| `[[63,11,3]]` | 6 | **5.181818** |
| HH18 `[[109,19,3]]` | 10 | 5.210526 |
| `[[127,23,3]]` | 7 | 5.217391 |
| `[[862,162,3]]` | 14 | 5.234568 |

So maximizing the rate of the isolated component is not the correct way to
choose a component for gluing. The 63-input seed's check directions are unusually
valuable.

Its catalogue ID is `06803716bc802828`. A further gain comes from this explicit
compatible eight-port set, given as check syndromes in the saved seed's basis:

```
16, 54, 18, 27, 63, 32, 40, 24
```

Its syndrome rank and full-column rank are both six. Thus eight ports can be
used while preserving the logical action, yielding `(63-8)/11 = 5` on an
eight-regular graph. The saved `K9` and `K8,8` port assignments use Python's
`random.Random(18)` to permute this list separately at each vertex. Every port
assignment is also explicitly stored, so reproduction does not depend on
repeating a search.

The complete-graph witness has `N = 118`, hence 19 checks; the bipartite one has
`N = 209`, hence 33 checks. In each case the edge differences have one dependency,
and the saved verifier confirms that it is harmless.

For the 909-input low-prefactor variant, the seed is
`032b274e708e9d80`, and the port list is

```
962, 811, 31, 785, 841, 521, 564, 406
```

These eight syndromes are independent. A greedy choice maximizing the number of
covered harmful seed triples deletes 102 of the seed's 324 weight-three harmful
patterns at each vertex. Identical port assignments at the nine vertices give
`A3 = 2005`; the additional seven above `9*(324-102) = 1998` are new cross-block
triples. An earlier random assignment had `A3 = 2333` and is not retained.

## Smaller consequences and corrected baselines

Even a single bridge improves a direct sum of two nondegenerate distance-three
components: it saves two columns at fixed output count. The following are saved
and verified:

| Construction | Result | Old direct-sum comparator |
|---|---|---|
| two 127-input seeds, one edge | `[[252,46,3]]`, `A3=5208` | `[[254,46,3]]` |
| four 127-input seeds, path of three edges | `[[502,92,3]]`, `A3=10292` | `[[508,92,3]]` |

This matters for the previous 255/511 rate campaign: its own final `[[255,45,3]]`
and `[[511,89,3]]` already lost to direct sums, and lose more decisively to these
simple coupled alternatives. Re-running its stalled Gabidulin beams should not
precede exploiting graph gluing.

## Useful next research directions

1. **Optimize compatible port sets, not just output width.** The search objective
   for a component becomes `(n0-p)/k0`, where `p` ports can be matched while their
   check relations are all harmless. A nine-port compatible set in the
   63-input seed would suggest `54/11 = 4.909091`, before checking the global
   distance. The 20,000 sampled independent bases found only six-, seven- and
   eight-port patches (17,797 / 2,144 / 59); that is evidence about sampling,
   not a proof that nine is impossible. Exact matroid/linear-subspace methods
   are a better next instrument than more random frame beams.

2. **Optimize the graph and port assignment using the actual error channel.**
   Independent-port complete graphs create triangle faults; bipartite graphs
   avoid this source. Dependent ports allow additional global relations, so
   graph girth alone is insufficient. Score exact marginal error and acceptance,
   not `A3/k`. The root's enumeration already demonstrates that these quantities
   can be computed exactly at 19 checks.

3. **Optimize the component for gluing.** Scan seed codes for compatible port
   size, harmful triple incidence, and the restrictions of output functions on
   those ports. A seed that is inferior in isolation can be superior after gluing.
   The HH18-based 909-input construction is a concrete demonstration of the
   prefactor side of this tradeoff.

4. **Use graph gluing as a stronger derived-baseline operation.** A knapsack over
   uncontracted factories does not capture these codes. Add graph-constructible
   rows, with explicit verification and prefactors, before calling a new width
   point competitive. An optimized native search should beat these new bars.

The simple-graph independent-port construction cannot by itself beat the
smallest `(n0-r)/k0` among its components: every vertex consumes at most `r`
ports. This is an exact bound on that construction, not a bound on the
dependent-port extension, nor a bound on all distance-three factories.

## A negative worth preserving

An attempted nine-port extension gave full-column rank six but syndrome rank
five. It was initially mistaken for a compatible linear patch. That mistake
was caught by direct construction: both proposed dense-graph circuits had
harmful weight-one faults. The offending syndrome set was

```
44, 43, 25, 38, 47, 26, 33, 50, 59
```

It is **not** a compatible port set and is **not** evidence for a rate below
five. The constructor now asserts equality of the two ranks before it performs
any contraction. No failed circuit is filed as a witness.

## Prior art and scope of novelty

The general idea of gluing transversal-gate codes is established. In particular,
[Cao and Lackey, *Quantum Lego Power-up: Designing Transversal Gates with Tensor
Networks* (2026)](https://arxiv.org/abs/2603.03542) develops such constructions;
its discussion includes linear families from gluing small transversal-T seeds.
Do not claim graph gluing itself as a new invention.

The verified contribution here is the explicit application to this repository's
small, high-width seeds, the new saved rate-five witnesses, the transparent
independent-port subfamily, and their measured error behavior. These are new
relative to the catalogue and campaign comparisons inspected in this task.
An exhaustive publication novelty review has not been performed.

## Reproduce

From this bundle directory, reconstruct any witness directly from saved seeds
and its complete graph/port provenance:

```sh
python3 graph_gluing.py --replay witnesses/graph_dependent_ports_complete_n495_k99_d3.json
python3 graph_gluing.py --replay witnesses/graph_dependent_ports_bipartite_n880_k176_d3.json
python3 graph_gluing.py --replay witnesses/graph_heterogeneous_n255_k47_d3.json
python3 graph_gluing.py --replay witnesses/graph_low_prefactor_n909_k171_d3.json
```

The same command works for every JSON in `witnesses/`. Replay asserts equality
of every column, checks the gate and ranks, and exhaustively recounts harmful
faults of weights one through three. It refreshes verification metadata in the
selected witness. Python 3.10+ is sufficient; no external dependency is needed.
See README.md for the destination catalogue's independent verification commands.
