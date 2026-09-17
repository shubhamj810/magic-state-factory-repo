# Can row-by-row augmentation push the triorthogonal classification from \(n+k\leq 38\) to \(n\leq 38\)?

> **A dated design note, kept for the reasoning, not for the numbers.** Written
> 17 July 2026, while the approach was being decided; it argues *why* the
> classification had to be narrowed to output-marked frames in the quotient. The
> mid-run figures quoted in the next two paragraphs are superseded by the final
> catalogue — see [`quotient_classification_report.md`](quotient_classification_report.md)
> for the shipped numbers, and
> [`../catalog/CLASSIFICATION_N38.md`](../catalog/CLASSIFICATION_N38.md) for the
> catalogue itself. Where the two disagree, the catalogue is right.

Date: 17 July 2026

Current overview of this directory: [`../README.md`](../README.md); the
overview-level treatment is
[`../../../../theory/02_classification.md`](../../../../theory/02_classification.md).

**Implemented result (2026-07-17):** the quotient-space classification below
has been built and run to completion for $k\leq4$ over the distinct-column
(distance-$\geq3$) marked parents. Gates are classified up to output-qubit
permutation of the parity tensor (GL$(k,2)$ class annotated). Engine:
[`../classify.py`](../classify.py);
report + independent 3-way validation:
[`quotient_classification_report.md`](quotient_classification_report.md).
Headline at the time: 73 distinct $(n,k,\text{gate})$ classes from the $k\leq4$
quotient passes; the known [[15,1,3]], [[28,2,3]] $T^2$, [[35,3,3]] $T^3$,
[[35,2,3]] CS cases reproduce; CCZ is absent for all $n\leq38$ (independent
reconfirmation of the $\geq39$ lower bound). *Superseded:* the shipped
catalogue has **74** classes — the 73 here plus the $k=5$ [[31,5,3]] class that
the automorphism-reduced $n=31$ run adds — and $k=4$ gates first appear at
$n=31$, not $n=36$, again from that run.

**Hard parent settled by automorphism reduction:** the only budget-limited
parent, $n=31$ class 0, is the 31 nonzero points of $\mathbb F_2^5$; its
automorphism group is GL$(5,2)$ (order $9{,}999{,}360$). Reducing the quotient
$V$ (2047 points $\to$ 5 orbits) makes the search exhaustive and certifies
exactly one gate class per $k$, through $k=5$ (about two minutes at `--kmax 5`). See
[`../hard_parent_n31.py`](../hard_parent_n31.py).
This is the same automorphism collapse that turns the ~$10^7$ raw output
configurations on that parent into ~$10^3$ inequivalent classes.

**Scope note (multisets):** the classification below fixes $k$ *independent*
logical outputs (genuine $k$-qubit codes). A general parity-phase factory may
instead use a compatible *multiset* of output cosets (need not be independent
or distinct); that broader object is a superset and is not yet enumerated.

## Executive verdict

There is a good idea here, but the claim needs to be narrowed and the objects
being classified need to be changed.

- **Yes:** for *reduced distance-\(\geq3\)* matrices, classify the pure-check
  part at fixed \(n\leq38\), then attach output rows. This really does avoid
  paying the Nezami--Haah \(+k\) completion cost. The one-output rung is small,
  and the two-output rung is computationally realistic.
- **No, as presently stated:** an unmarked classification of even spaces plus
  a classification of spaces with one odd row does not classify all
  two-output gates, and it does not classify all triorthogonal codes in the
  scope of Nezami--Haah. The recursion forgets logical-row markings, uses an
  incomplete equivalence relation, and ceases to be hereditary when deleting
  a row creates zero or repeated parent columns.
- **Not presently realistic:** a complete classification of every
  output-marked space, for every \(k\), at \(n\leq38\). The output itself can
  be exponentially large. At \(k\geq4\), the hard near-affine parent classes
  already defeat the current unquotiented decision search.

The right near-term project is therefore:

> Classify reduced distance-\(\geq3\), output-marked extensions of each
> classified check support, using output rows modulo the check space and
> canonical augmentation under the parent automorphism group.

That is a meaningful new \(n\leq38\) frontier. It is not quite the same
classification problem as the one in Nezami--Haah.

## 1. The precise object

Write a factory/code matrix as

\[
G=\begin{bmatrix}A\\ C\end{bmatrix},
\]

where \(C\) contains the even check rows and the rows of \(A\) are distinguished
logical/output rows. Let \(h_1,\ldots,h_r\in\mathbb F_2^n\) be a basis for
the check-row space.

There is an important terminology correction here. In the Nezami--Haah
definition, a *triorthogonal space* requires the triple condition even when
the three vectors coincide. Taking \(u=v=w\) forces every vector in that space
to have even weight. A matrix with one odd output row is therefore not a new
kind of Nezami--Haah triorthogonal space. It is a triorthogonal matrix/code
with a distinguished even check subspace, equivalently data such as
\((C,a+C)\). Calling both rungs “spaces” hides exactly the marking information
that the recursion needs.

For one \(T\) output, a new row \(a\in\mathbb F_2^n\) must satisfy

\[
|a|=1\pmod2,\qquad
 a\cdot h_i=0,\qquad
 a\cdot(h_i\wedge h_j)=0
\]

for all \(i,j\). Thus the hard-looking row search begins with a linear
space

\[
R(C)=\left\{a:
a\perp \operatorname{span}\{h_i,h_i\wedge h_j\}\right\},
\]

followed by the affine condition \(|a|=1\). Moreover, \(a\) and \(a+c\),
for \(c\in C\), give the same logical row up to multiplication by an
\(X\)-stabilizer. The natural one-output search space is consequently the odd
part of the quotient

\[
R(C)/C,
\]

not all \(2^n\) rows and not even all of \(R(C)\).

After rows \(a_1,\ldots,a_s\) have been chosen, the constraints on the next
row remain linear in that last row. In addition to membership in \(R(C)\), one
imposes

\[
(a_i\wedge a)\cdot h_j=0
\]

for all previous outputs and checks, and fixes the desired pure-output single,
pair, and triple parities. This is exactly why a recursive extension algorithm
is mathematically sound once the parent is correctly marked.

For pure \(T^{\otimes k}\), the pure-output conditions are

\[
|a_i|=1,\qquad a_i\cdot a_j=0,
\qquad |a_i\wedge a_j\wedge a_\ell|=0.
\]

For a general degree-at-most-three diagonal gate, those last parities are
instead read as the target's linear, quadratic, and cubic tensor.

## 2. Why the base check classification reaches \(n\leq38\)

[Nezami--Haah](https://arxiv.org/abs/2107.09684) classify unital
triorthogonal spaces through indicator words of weight below \(40\), and use
them to classify reduced codes in the region \(n+k\leq38\). For a reduced
distance-three matrix, however, the check columns alone form a set of
distinct nonzero points. An even check space of length \(n\) can be made
unital at length

\[
c=n+(n\bmod2).
\]

For even \(n\), adjoin the all-ones row. For odd \(n\), first append the
unique zero check column and then adjoin the all-ones row. Therefore
\(n\leq38\) maps into the already classified weights \(c\leq38\).

This is the valid mechanism for removing \(k\) from the boundary. It is also
the mechanism already used in the local KTA ladder work, whose methodology
notes are out of scope for this repository; the unital-completion step as
shipped here is [`marking.py`](../marking.py).
The Nezami--Haah representatives are not by themselves the final list of
check parents. One must also mark the origin/puncture choice. For example,
the current raw marking produces 320 parents at \(n=31\), 504 at \(n=35\),
and 3032 at \(n=38\). These are deliberately overcomplete under affine
automorphisms.

So the proposed base case is feasible, but it should be described as a
classification of **marked reduced check supports derived from** the
Nezami--Haah unital classification, not simply “the even triorthogonal spaces
at \(n\leq38\).”

## 3. The most serious completeness failure: row deletion creates collisions

The no-repeated-column convention is not hereditary under deletion of an
output row.

Two distinct columns of a one-output child may have the form

\[
\binom{0}{s},\qquad \binom{1}{s}.
\]

The child columns are distinct, but after deleting the output row the parent
contains the check column \(s\) twice. Similarly, a column supported only on
the deleted output becomes a zero column in the parent. Nezami--Haah exclude
repeated columns in their distinguished classification because such columns
do not improve parameters. That does **not** mean a row-deletion recursion may
silently discard them: a new row can split a repeated parent fibre into
distinct child columns.

This is fatal if the goal is “all triorthogonal codes” including distance two.
The collision above is precisely capable of supporting a weight-two logical
operator. Hence a classification based only on distinct nonzero check
supports will miss valid reduced distance-two children even when the full
child matrix has no repeated columns.

There are two repairs:

1. Restrict the theorem to reduced distance-\(\geq3\) objects. Then check
   columns may be assumed distinct and nonzero, and the check-support base is
   hereditary for the purpose of finding optimal factories.
2. If distance-two codes must be included, classify parent **multisets** and
   retain every fibre over a check column. After \(k\) output rows, one check
   vector can split into as many as \(2^k\) output labels. Reducing duplicate
   pairs at an intermediate rung loses necessary extension data.

The second repair is much larger and largely destroys the simplicity of the
proposal. The first repair is the recommended scope.

## 4. “Number of odd rows” is not “number of outputs”

The suggested two-list recursion is complete for pure product-\(T\) outputs,
where every output row is odd. It is not complete for arbitrary output gates.

The simplest counterexample is \(CS\). Its two logical rows can both have even
weight while their pair overlap is odd:

\[
|a|=|b|=0,\qquad |a\wedge b|=1\pmod2.
\]

Deleting either row leaves an even matrix, not a one-output \(T\) matrix. To
recover the child from an even-space representative, one must remember that a
particular even row was already designated as the first output. An unmarked
even row space forgets this completely.

The same issue is stronger for \(CCZ\): all three singles and all pairs may be
even, while the output triple is odd. Before the third row is attached, the
first two logical rows can be invisible inside an ordinary even
triorthogonal space.

Thus the actual state of the recursion is a flag such as

\[
C\subseteq C+\langle a_1,\ldots,a_s\rangle,
\]

together with a distinguished basis, or at least a distinguished output
quotient, and its accumulated target tensor. It is not merely an unmarked row
space in one of two parity classes.

For “any two-output gate,” the repaired split is:

- if the surviving first output has odd single parity, extend a marked
  one-output parent;
- if it has even single parity, extend an even space **with a marked
  codimension-one check subspace and a marked output coset**.

That marking step is the part missing from the original proposal.

## 5. The proposed equivalence relation is too small

“Up to row permutations” is not the relevant code equivalence.

At minimum, the following identifications are unavoidable:

- arbitrary change of basis among check rows;
- addition of check rows to an output row;
- permutation of physical columns;
- permutation of output qubits, if outputs are unlabeled;
- possibly a larger target-preserving subgroup of \(GL(k,2)\), depending on
  whether logical CNOT basis changes are considered equivalent.

The last choice must be made explicitly. A logical basis change can mix the
linear, quadratic, and cubic Boolean terms because \(x_i^2=x_i\). Consequently
“how many single parities are nonzero” is not generally an invariant of an
unlabeled generalized gate once pair or triple terms are present.

There is a related algorithmic trap: a representative of a parent class is
not enough for efficient extension. One needs its automorphism group. Valid
new rows should be enumerated as orbits under

\[
\operatorname{Aut}(C,\text{existing output markings}),
\]

and a child must be canonicalized because it can arise from several
nonisomorphic deletion parents. Without canonical augmentation, the same
child is regenerated many times; with overly aggressive representative-only
deduplication, valid children can instead be lost.

A sound implementation should use a canonical-deletion rule in the style of
canonical augmentation: retain a child only when its canonically selected
output deletion returns the current parent class. A colored bipartite graph
encoding of columns, check fibres, and output markings would make nauty/Traces
or an equivalent canonical-labeling backend natural.

## 6. What the local counts say about tractability

A direct audit of the local weight-\(\leq38\) representatives gives the
following scale. These are raw counts over the overcomplete marked-parent
family, before parent automorphism quotienting, so they are workload upper
indicators rather than numbers of equivalence classes.

| object | raw audit count |
|---|---:|
| candidate odd output vectors before quotienting by check rows | 2,726,912 |
| candidate odd output cosets in \(R(C)/C\) | 49,470 |
| compatible pure-\(T^2\) output pairs | 14,192 |
| compatible pure-\(T^3\) output triples | 4,320 |
| compatible nonzero two-output pairs when all output-only parities are allowed | 3,579,081 |

The homogeneous row-code dimension reaches 16 in the hardest parents, but the
largest quotient dimension seen in this audit is 11. This is why quotienting
by check-row additions is not cosmetic: on the worst parent it removes a
factor of roughly \(2^r\) per output row.

These counts support the following judgments.

### One output

Fully feasible. Linear algebra produces the candidates; automorphism orbits
and canonical labeling should dominate, not candidate generation. This is a
reasonable desktop/medium-cluster classification.

### Two outputs

Feasible for reduced distance-three objects. Pure \(T^2\) is small. Even the
raw all-gates compatibility graph has only a few million edges across the
overcomplete parents, which is a realistic compiled/parallel workload.
Canonical classification will be substantially more expensive than merely
finding a witness, but it is still plausible.

### Three outputs

Fixed-target decisions are feasible in many cases, and the specialized CCZ
algebraic solver has already closed the \(n=31,\ldots,38\) ladder. That solver
is out of scope for this repository; the same window is closed here by the
\(n\leq38\) classification itself, which contains no pure CCZ class
([`../catalog/CLASSIFICATION_N38.md`](../catalog/CLASSIFICATION_N38.md)). A full
classification of all marked triples is less clear: it asks for orbit
classification of compatible graph triangles plus the cubic color on each
triangle. It may be feasible after automorphism quotienting, but it should be
benchmarked rather than assumed.

### Four or more outputs

This is the present wall. The current recursive fixed-target solver scales
roughly as \(2^{(k-1)d}\) in a row-code dimension \(d\). The CCZ-ladder target
findings, which are out of scope for this repository,
record unresolved \(k=4\) instances at dimensions 14--16 after the easy
parents are exhausted. A full classification is harder than those existence
decisions because every inequivalent solution must be retained.

There is, however, a strong optimization opportunity: the local diagnostic
counts above work in \(R(C)/C\), whereas the current general target recursion
enumerates representatives before fully removing that gauge. A
quotient-space clique/isotropic-subspace solver should be built before
declaring the \(k=4\) rung impossible. It may close some current decision
timeouts, but it does not remove the worst-case exponential output size.

## 7. Do not confuse a gate catalog with a space classification

The local
[`classify_rowspace.py`](../classify_rowspace.py) is a
useful prototype of the output-label enumeration, but its current dedup key is

\[
(n,k,\text{logical gate up to }GL(k,2)).
\]

It keeps one representative for a gate signature. Two inequivalent codes or
spaces implementing the same gate are intentionally merged. Some large
parents are also node-budget capped. Therefore its output is a factory/gate
catalog, not the classification proposed here, and it cannot be used as an
exhaustiveness certificate for equivalence classes without substantial
changes.

Likewise, the single-target labelling solver of the CCZ-ladder work
(`general_target.py`, superseded by, hence not shipped alongside, the quotient
engine; its findings note is out of scope for this repository) answers a
decision question: it stops at the first witness. A hierarchy of decision
problems can be easy while the hierarchy of all isomorphism classes is huge.

## 8. A repaired classification algorithm

### Stage 0: fix the scope

Use the following explicit claim:

> Reduced distance-\(\geq3\) output-marked generalized triorthogonal matrices
> with \(n\leq38\), no redundant check rows, and a stated equivalence on
> logical outputs.

Do not initially claim all distance-two codes, nonunital variants, or all
matrices obtained by inserting cancelling duplicate columns.

### Stage 1: canonical check parents

1. Generate the raw marked check supports from the weight
   \(c=n+(n\bmod2)\) Nezami--Haah/KTA representatives.
2. Canonicalize them as binary linear spaces with physical-coordinate
   permutations.
3. Store an exact automorphism group for each parent.

The public source data are in the
[Tri_from_RM repository](https://github.com/sgnez/Tri_from_RM); the local
transcription is in
[`nezami_haah_reps.py`](../nezami_haah_reps.py).

### Stage 2: one-output classes

1. Compute \(R(C)/C\).
2. Select odd nonzero cosets.
3. Take orbits under \(\operatorname{Aut}(C)\).
4. Canonicalize every child and store its automorphism group and its marked
   check hyperplane.

This should be the pilot. It has a clean theorem and a small workload.

### Stage 3: two-output classes

Do **not** use only one-output-\(T\) parents.

- For \(T^2\)-type children, extend the one-odd-output classes.
- For \(CS\)-type and other even-first-output children, enumerate marked
  output cosets/hyperplanes inside even parents.
- Equivalently, and probably more cleanly, enumerate compatible two-frames
  directly in \(R(C)/C\), color each frame by its single and pair parities,
  and quotient by the parent automorphism group and the chosen output group.

The direct two-frame formulation avoids a large amount of duplicate parentage
and naturally classifies every two-output target at once.

### Stage 4: higher outputs

Represent compatible output cosets as vertices of a parent-dependent graph;
an edge means every mixed output--output--check moment vanishes. Pure pair
parity is an edge color. Cubic parity colors compatible triangles. The
classification becomes an orbit problem for colored frames/cliques under the
parent automorphism group.

For a fixed target, use the target colors to prune. For “all gates,” expect
the class count, not merely runtime per node, to become the limiting resource.

### Stage 5: independent verification

For every retained representative:

- verify all degree-at-most-three moments directly;
- verify row/check ranks and the selected equivalence data;
- compute the actual code distance rather than inferring it from
  triorthogonality;
- compare the \(n+k\leq38\) overlap against the published Nezami--Haah list;
- reproduce the known \(15\)-to-\(1\), \([[28,2,3]]\) \(T^2\),
  \([[35,3,3]]\) \(T^3\), and \([[35,2,3]]\) \(CS\) cases.

## 9. Recommended go/no-go sequence

1. **Go:** one-output \(T\), reduced distance three, all \(n\leq38\), with
   full canonical representatives and automorphism groups.
2. **Go:** direct two-frame classification over the same parents, with target
   colors distinguishing all linear/quadratic two-output signatures, including
   \(T^{\otimes2}\), \(CS\), and \(CS\) with attached \(T\) terms. Benchmark
   the few-million-edge raw workload.
3. **Conditional go:** three-output fixed targets. First implement the
   quotient-space compatibility graph and compare it against the existing CCZ
   and \(T^3\) decisions.
4. **No-go for now:** claim a complete all-\(k\), all-gates, all-distances
   \(n\leq38\) classification. That requires multiset parents, marked flags,
   canonical augmentation, and a new high-dimensional orbit algorithm.

## Bottom line

The core insight is correct: classify the check geometry once at physical
length \(n\), then attach output labels, and the \(+k\) in the
Nezami--Haah completion disappears. For reduced distance-three factories this
is more than a heuristic; it is a complete reduction.

The dangerous leap is from that reduction to “classify all spaces by adding
one row repeatedly.” The deletion category is not closed when repeated
columns are excluded, general gates hide even output rows inside unmarked even
spaces, and representatives without automorphism/flag data are insufficient
for the next rung. After repairing those points, the one- and two-output
classifications look tractable. The unrestricted hierarchy does not.
