# The classification algorithm, microscopically — and a line-by-line audit

This document walks through **exactly** what the distance-3 factory classifier
does, one step at a time, and after every step records a **code check**: the
precise function and line range that implements it, and a confirmation (or a
flag) that the code does what the prose claims. The goal is to leave no step
unverified.

The companion document
[`THEORY_EXHAUSTIVENESS.md`](THEORY_EXHAUSTIVENESS.md) explains *why* the
algorithm is correct and complete for `n ≤ 38`; this document is only about
*what the code does*.

Current overview of this directory: [`../README.md`](../README.md). The
overview-level treatment of the same material is
[`../../../theory/02_classification.md`](../../../theory/02_classification.md).

## File map

| role | file |
|---|---|
| main engine (produces `results/quotient_catalog_*.json`) | [`classify.py`](../classify.py) |
| check-part representatives (KTA / Nezami–Haah), all weights ≤ 38 | [`nezami_haah_reps.py`](../nezami_haah_reps.py) |
| marking + linear algebra primitives | [`marking.py`](../marking.py) |
| exact fault-distance / parity verifier | [`factorylib/verification.py`](../../../factorylib/verification.py) |
| `S_k` dedup key + GL(k,2) gate canonicalisation | [`dedup.py`](../dedup.py) |
| hard parent `n=31` via GL(5,2) collapse | [`hard_parent_n31.py`](../hard_parent_n31.py) |
| consolidation into the deduped catalog + plot | [`build_catalog.py`](../build_catalog.py), [`plot_landscape.py`](../plot_landscape.py) |

The weight-40 representatives that carried the `n = 39, 40` extension are out of
scope for this repository; the exhaustive window shipped here is `n ≤ 38`.

Notation used throughout: a factory is a `[[N, k, d]]` circuit given as a list
of **columns**, one per parity-rotation gate. Each column is a subset of the
`N = k + r` qubits: output qubits `0..k-1` and `r` check qubits `k..k+r-1`.
Writing each row of the matrix as a vector in `F₂ⁿ` (`n` = number of columns),
`a_1..a_k` are the **output rows**, `h_1..h_r` are the **check rows**.

---

## Step 0 — What is being enumerated

For a fixed physical length `n` (the injection count = number of columns), the
algorithm enumerates every distance-≥3, non-redundant, output-marked
generalized-triorthogonal matrix, deduplicated by
`(n, k, gate up to output-qubit relabelling)`, and records the highest distance
seen for each. Only `d = 3` classes survive at `n ≤ 38`.

"Every" here means every frame whose `k` output rows are linearly independent
*modulo the check span* `C`. Frames using both `a` and `a + c` as separate
outputs are real circuits this engine cannot represent, but they carry no extra
magic — one output CNOT makes the extra output an idle spectator — so the result
is complete for gate content. Proved in
[`THEORY_EXHAUSTIVENESS.md`, "Lift-degenerate frames"](THEORY_EXHAUSTIVENESS.md#lift-degenerate-frames-what-independence-modulo-c-leaves-out-and-why-it-carries-no-magic),
and stated in the `SCOPE` section of [`classify.py`](../classify.py).

The enumeration is done **per check-part parent**: fix the check rows first,
then attach output rows. This is Steps 1–8. The rest of this document follows
one parent through the pipeline, then the driver that loops over all parents,
then the special handling of the one hard parent.

---

## Step 1 — Enumerate the marked check-part parents

**What it does.** For a target injection count `n`, set the *unital weight*
`c = n + (n mod 2)`. Look up the classified triorthogonal representatives of
weight `c` (the KTA / Nezami–Haah affine classes, stored as Boolean
polynomials in `m` variables). For each representative, produce every **marked
check support**: a set of `n` distinct nonzero points in `F₂ʳ` obtained by
translating (and, for even `n`, optionally lifting into one extra coordinate)
the polynomial's support so the origin is excluded.

- Even `n`: for every origin *outside* the support `S`, translate `S` by that
  origin (origin never lands in the support, so `0 ∉ cs`); plus one extra
  "hyperplane-miss" marking that lifts `S` into a new `(m+1)`-th coordinate.
- Odd `n`: for every point `s ∈ S`, translate by `s` and drop the resulting
  `0`, giving `|S|−1 = n` columns.

**Why these are the only markings.** Let `L = aff(S)` and let `o` be the image
of the original zero under the affine equivalence taking the augmented check
support to `S`. Exactly one of `o ∈ S`, `o ∈ L \ S`, or `o ∉ L` holds. The
first is forced for odd `n`; the latter two are the even-`n` cases. If `o ∉ L`,
moving `o` to zero makes `L` an affine hyperplane in its `(m+1)`-dimensional
linear span. A check-basis change takes it to `x_{m+1}=1`, and a shear removes
the remaining translation, so every such marking is the one canonical
hyperplane-miss lift. Extra ambient coordinates are redundant check rows.
The complete statement and proof are in
[`THEORY_EXHAUSTIVENESS.md`, “The three marking cases”](THEORY_EXHAUSTIVENESS.md#the-three-marking-cases).

**Code check.**
`marked_all` — [`classify.py`](../classify.py) —
computes `weight = n + (n % 2)`, picks `BY_WEIGHT[weight]`, chooses
`marked_even`/`marked_odd` by parity, and yields `(class_index, r, check_tuple)`.
`marked_even`/`marked_odd` are
[`marking.py`](../marking.py) and
[`marking.py`](../marking.py); their support-level implementations
raise on `0 ∈ cs` at
[`marking.py`](../marking.py), and both build the
support with `support_of`
([`marking.py`](../marking.py)),
which correctly handles negated literals `('not', i)`. `BY_WEIGHT`
([`nezami_haah_reps.py`](../nezami_haah_reps.py)) covers weights
`{16,24,28,30,32,34,36,38}`; all eight tables (including weight-36, 14
classes, and weight-38, 8 classes) live in that one module.
`marked_all` also asserts each representative actually has weight `c`
([`classify.py`](../classify.py)).
**Confirmed**: parents are
generated from the classified weight-`c` spaces, each with `n` distinct nonzero
columns, origin excluded. The raw parent counts this produces (320 at `n=31`,
504 at `n=35`, 3032 at `n=38`) match the `stats` block written into the
catalogs.

---

## Step 2 — Build the quotient space `V = R(C)/C`

**What it does.** From the check support, build:

- the `r` check rows `h_1..h_r` (degree-1 rows) as vectors in `F₂ⁿ`;
- `R(C)` = the space of candidate output rows `a` satisfying the *linear*
  triorthogonality conditions `|a ∧ h_i| ≡ 0` (output–check) and
  `|a ∧ h_i ∧ h_j| ≡ 0` (output–check–check) for all `i,j`;
- `C` = span of the check rows (`C ⊆ R(C)` because the check space is itself
  triorthogonal);
- `V = R(C)/C`, with an explicit basis `Qbasis` and a table `Vreps[x]` giving,
  for each coordinate `x ∈ {0,…,2^{dimV}−1}`, the canonical `C`-reduced
  representative vector.

**Code check.**
`row_space_rows(checks, r, degree)` —
[`marking.py`](../marking.py) — for each subset
`T` of check-bits with `|T| ≤ degree`, emits the `F₂ⁿ` indicator of the columns
whose point has *all* bits of `T` set. So `T=∅` → the all-ones row; `|T|=1` →
the check rows `h_i`; `|T|=2` → the pointwise-AND rows `h_i∧h_j`. In
`quotient_reps` ([`classify.py`](../classify.py)):
`hlist = rows1[1:]` drops the all-ones row and keeps `h_1..h_r`;
`Rbasis = nullspace_basis(rows2[1:], n)` is the nullspace of the
degree-1 **and** degree-2 rows — i.e. exactly `R(C) = {a : a·h_i = 0, a·(h_i∧h_j)=0}`;
`Crref = rref_basis(hlist)` is a basis of `C`. The loop that follows reduces
each `R`-generator mod `C` and keep the independent residuals, giving a
complement basis `Qbasis` of `C` in `R` — a basis of `V`. The final loop
tabulates `Vreps[x]` = XOR of the `Qbasis` vectors indexed by the set bits of
`x`. `nullspace_basis`
([`marking.py`](../marking.py)) is the standard
free-column construction. **Confirmed**: `R(C)`, `C`, and the quotient basis
are built as described. (The docstring writes the degree-2 generator as
"`h_i ^ h_j`"; the code uses the *pointwise product* `h_i ∧ h_j` via
`row_space_rows(...,2)` — the product is the correct triorthogonality
generator, so this is a notation slip in the comment, not in the code.)
Audited separately: `dimV ≤ 11` over every parent in the ladder, with the
maximum attained at `n=31` (see Step 9).

---

## Step 3 — Build the compatibility graph on `V`

**What it does.** Two candidate output rows `a, b` may coexist in one factory
iff the *output–output–check* condition holds:

    B_j(a, b) = |a ∧ b ∧ h_j| ≡ 0   for every check row h_j.

The code precomputes, for each `h_j`, the bilinear form on the `dimV` basis
coordinates and evaluates it on all `2^{dimV} × 2^{dimV}` coordinate pairs at
once, producing a boolean adjacency matrix `comp[x][y]`.

**Code check.**
`compat_adjacency` —
[`classify.py`](../classify.py).
For each `h`, it forms `M[b][c] = parity(Qbasis[b] & h & Qbasis[c])` (lines
220–224), i.e. `M[b][c] = |Q_b ∧ h ∧ Q_c| mod 2`, then
`Bj = ((X @ M) @ X.T) & 1` where `X` is the coordinate bit-matrix. Because a
mod-2 sum may be reduced summand-by-summand, `(X M Xᵀ)[x,y] mod 2 =
Σ_i h_i (Σ_b x_b Q_{b,i})(Σ_c y_c Q_{c,i}) mod 2 = Σ_i h_i A_i B_i mod 2 =
|A ∧ B ∧ h|` with `A = Vreps[x]`, `B = Vreps[y]`. So `comp[x][y]` is true iff
`|Vreps[x] ∧ Vreps[y] ∧ h_j| = 0` for all `j`. **Confirmed**:
the adjacency is precisely the pairwise compatibility `B_j = 0`. It is also
gauge-invariant: replacing `a` by `a+c` (`c ∈ C`) changes `B_j` by
`|c ∧ b ∧ h_j| = |b ∧ (h_i∧h_j)| = 0` since `b ∈ R(C)` — so evaluating it on
the `C`-reduced `Vreps` is well defined.

---

## Step 4 — Enumerate compatible, independent output frames

**What it does.** A `k`-output factory is a size-`k` set of quotient points
that is (i) a **clique** in the compatibility graph and (ii) **linearly
independent** in `V` (each new output is a genuinely new logical). The code
does a depth-first recursion adding points in strictly increasing coordinate
order, intersecting candidate masks with each chosen vertex's neighbourhood
(maintaining the clique) and rejecting any point that is linearly dependent on
those already chosen.

**Code check.**
In `classify_parent`
([`classify.py`](../classify.py)):
after building `comp`, vertex `0` (the identity coset) is excluded — `verts =
list(range(1, size))` — and per-vertex neighbour bitmasks `adj[x]` are
packed with bit 0 and the self-bit cleared. The recursion
`extend(frame, cand_mask, basis_rref)` walks candidates `y` in
`cand_mask`, skips `y ≤ frame[-1]` to enforce increasing order and count each
set once, computes the residual of `y` against the running RREF
basis via `indep` and skips dependent points (`res == 0`),
then recurses with `cand_mask & adj[y]` so the clique property is
preserved. **Confirmed**: the walk enumerates every compatible independent
frame of size `1..kmax` exactly once. (The independence test is on quotient
*coordinates*; since `x ↦ Vreps[x]` is a linear isomorphism `V(coords) → R/C`,
coordinate-independence equals independence of the output rows modulo `C`,
which is the intended "distinct logicals" condition — and, being independence
*modulo* `C`, is also exactly the scope recorded in Step 0, which costs no gate
content.)

---

## Step 5 — Read off the logical gate and reject degenerate frames

**What it does.** For a frame `a_1..a_k`, the logical gate is the phase
polynomial whose monomials are the odd output-only parities:
`i` (single) if `|a_i|` is odd; `ij` (pair) if `|a_i ∧ a_j|` is odd; `ijk`
(triple) if `|a_i ∧ a_j ∧ a_l|` is odd. A frame is rejected if it implements
nothing (`wants` empty) or if some output qubit appears in no monomial (that
qubit is padding a smaller gate — it will be found at its true `k`).

**Code check.**
`frame_wants` —
[`classify.py`](../classify.py) —
computes exactly these single/pair/triple parities using `.bit_count() & 1`.
`record` collects `covered = ∪ wants`; if `wants` is empty it
returns, and if `len(covered) != k` it returns,
enforcing non-degeneracy. **Confirmed**: gate readout and both degeneracy
rejections match. These parities are gauge-invariant because the checks have
even weight (`|c| ≡ 0`) and `b ∈ R(C)` kills the mixed terms — so the gate is a
function of the coset, computed correctly on `Vreps`.

---

## Step 6 — Assemble columns and verify parity + exact distance

**What it does.** Turn the abstract frame into an explicit `[[k+r, k, d]]`
column list, then independently verify (a) the assembled circuit realises the
claimed gate (all degree-≤3 output parities match, all check-touching parities
vanish) and (b) its exact fault distance by enumerating weight-1…4 column
subsets that XOR to a purely-logical error.

**Code check.**
`build_columns` —
[`classify.py`](../classify.py) —
column `idx` gets output qubit `q` iff `(a_q >> idx) & 1`, and check qubit
`k+bit` iff the point `s` has that bit. The output rows handed to it are already
permuted into the canonical frame (Step 7), so `record` verifies against
`canonical_wants` — the gate the row will be filed under — by calling
`verify(k, k+r, cols, canonical_wants, dmax=4)`, and **raises** if the parity
check fails. Any enumerated frame that did not actually realise its own gate
would crash the run rather than be silently recorded.
`verify` — [`factorylib/verification.py`](../../../factorylib/verification.py) —
first asserts columns are distinct, checks all singles/pairs/triples
against `want`, then finds the minimum-weight column subset whose
XOR is `is_bad` = nonzero and supported only on output qubits,
returning that weight as the distance (`>dmax` if none ≤ `dmax`). **Confirmed**:
this is the exact circuit fault-distance, verified from the raw columns, not
inferred from the construction.

*Verified edge case (repeated columns).* `record` asserts that the columns it
built are distinct. In the quotient engine that assertion cannot fire: each
column's check-qubit part is the bit pattern of its point `s`, and the points of
a marked support are distinct nonzero integers, so no two columns can be equal.
It is an assertion rather than a fallback on purpose — a repeated column is a
weight-2 undetectable fault, i.e. a `d = 2` circuit, which is outside this
distance-`≥3` classification altogether, so recording one with `dist = 2` (as an
earlier revision did) would have quietly admitted an out-of-scope row. Confirmed
empirically: every stored circuit has distinct columns.

---

## Step 7 — Canonicalise the gate and deduplicate

**What it does.** Gates are identified up to relabelling the output qubits
(the symmetric group `S_k`). The signature `(n, k, S_k-canonical gate)` keys a
`seen` dictionary; the first frame realising a signature is stored, and later
frames only replace it if they achieve a strictly higher distance. The
`GL(k,2)` class is computed and stored as an annotation but is **not** the
dedup key.

**Code check.**
`sk_canonical` —
[`dedup.py`](../dedup.py) —
minimises the encoded monomial set over all `k!` output permutations. `record`
sets `pc, perm = sk_canonical_with_perm(k, wants)` and `sig = (n, k, pc)` — so
the dedup key is the **`S_k` class**. It then uses `perm` for more than the key:
the output rows are placed at `a_vectors[perm[i]]`, so the columns it builds
deposit exactly `pc` rather than the labelling the enumeration happened to
reach. That is what lets `build_catalog.py` compare a row's stored gate against
its stored circuit as plain strings, with no permutation allowed. The `GL(k,2)` truth-table canonical
form `canonical_gate`
([`dedup.py`](../dedup.py),
enumerating all of `GL(k,2)` via `_gl_perms`) is stored only in
`gate_gl_canonical`. The best-distance replacement is the `dval > rec['_dval']` test, with a
`CAP = 60` on re-verification calls per signature that bounds runtime without affecting which
signatures are discovered.

> **⚠ Discrepancy found (documentation, not algorithm) — corrected in this
> layout.** The JSON metadata string written by the engine used to read
> `"dedup_signature": "(n, k, canonical gate under GL(k,2)); max distance
> kept"`, while the code actually deduplicated by the **`S_k`** canonical form
> (`sk_canonical`), not `GL(k,2)`. The `S_k` key is *finer* (keeps more
> classes), so this never threatened completeness — it was a mislabelled
> metadata string, evidently copied from the `classify_rowspace.py`
> engine, which *does* dedup by `GL(k,2)` (see
> [`classify_rowspace.py`](../classify_rowspace.py)). The string
> shipped here, [`classify.py`](../classify.py), now names `S_k`, so
> metadata and code agree.
> **Evidence the effective key is `S_k`:** the catalog contains distinct gates
> that share a `GL(k,2)` class — e.g. at `[[35,3,3]]`, `0+1+01+02+012` and
> `0+12+012` both have `gate_gl_canonical = 62`, and `0+01+12` and `0+2+01`
> both have `30`. Under a true `GL(k,2)` key these would have merged. The
> prose report
> [`quotient_classification_report.md`](quotient_classification_report.md)
> states the equivalence correctly ("up to permutation of output qubits
> (S_k); the GL(k,2) mod-2 class is annotated separately"), and the JSON string
> now says the same. **The 74/73 counts I consolidated use the `S_k` key and
> match the report exactly.**

---

## Step 8 — Driver over all parents; budget and partiality

**What it does.** For each `n` in the ladder, loop over every marked parent,
run Step 2–7, and accumulate into the global `seen`. A per-parent node budget
(default `50,000,000`) bounds the recursion; a parent that exceeds it is flagged
`PARTIAL` for that `n`, meaning its enumeration was not exhaustive and must be
completed another way.

**Code check.**
`run` — [`classify.py`](../classify.py) —
iterates `marked_all(n)`, calls `classify_parent`, and records
`partial[n].add(ci)` when the budget was hit. Inside
`classify_parent`, `nodes[0]` is incremented per candidate and, when it exceeds
`budget`, sets `hit = True` and unwinds. The written
`partial_ns` field is `{str(n): sorted(v)}`. In the `k≤4` run the
**only** partial parent was `{"31": [0]}` — the `F₂⁵` parent — which is then
completed exhaustively by Step 9. Every other parent finished under budget, so
their enumeration is complete. **Confirmed**: partiality is tracked honestly
and localised to exactly one parent.

---

## Step 9 — The hard parent `n=31`, via the GL(5,2) automorphism collapse

**What it does.** The `n=31` class-0 parent is the 31 nonzero points of `F₂⁵`;
its automorphism group is the full `GL(5,2)` (order 9,999,360), which permutes
the 31 physical columns while preserving the check code — a genuine
physical-qubit relabelling equivalence. Every output frame is `Aut`-equivalent
to one whose *first* output is one of the few orbit representatives of quotient
points, and the logical gate is `Aut`-invariant. So fixing the first output to
an orbit rep and enumerating the rest **exhaustively** classifies this parent in
seconds, with no node budget.

**Code check.**
`hard_parent_n31.py`. `gl_transvections`
([`hard_parent_n31.py`](../hard_parent_n31.py)) builds the
elementary transvections that generate `GL(5,2)`; `induced_V_action`
([`hard_parent_n31.py`](../hard_parent_n31.py)) computes,
for each generator, the induced column permutation `p ↦ Mp` and
its action on the `V`-basis coordinates. `orbits`
([`hard_parent_n31.py`](../hard_parent_n31.py)) computes
point orbits; `main` asserts single-parity is orbit-invariant
and spot-checks gate invariance on compatible pairs.
`complete_hard_parent`
([`hard_parent_n31.py`](../hard_parent_n31.py))
performs the exhaustive classification: it seeds the recursion with each orbit
rep as the first output (`for r0 in reps: grow((r0,), adj[r0], …)`, lines
291–292) and enumerates compatible independent extensions with the same
clique+independence logic as Step 4. It reproduces exactly one gate class per
`k` for `k = 1..4` (and, run to `k=5`, the single `[[31,5,3]]` all-monomials
gate). **Confirmed**: the collapse is sound (orbit-invariance of both the
compatibility relation and the gate is asserted at runtime) and the resulting
classification of the sole partial parent is exhaustive.

---

## Step 10 — Consolidation into the deduped catalog + plot

**What it does.** Union the `k≤3` and `k≤4` quotient catalogs and the
hard-parent run, dedup by `(n, k, gate)` keeping the largest verified distance
and then the smallest `N`, and emit the JSON, markdown, and the landscape
figure.

**Code check.**
`build_catalog.py`. `build`
([`build_catalog.py`](../build_catalog.py)) globs every
`results/quotient_catalog_*.json` and appends `results/hard_parent_n31.json`
(`input_files`), re-canonicalises each gate label on
load, and keys by `(n, k, S_k gate)` keeping the larger distance and then the
smaller `rows` (= `N`); the certified `[[31,5,3]]` class enters this way, with
the explicit circuit written by the collapse of Step 9. Independent checks I
ran and that this pipeline is designed to satisfy:

- the `k3` and `k4` catalogs **agree on their overlapping `(n,k)`** (no gate
  string or `N` mismatch);
- per-`(n,k)` class counts of the consolidated set **match the report** exactly
  (74 total, 73 with circuits);
- every stored circuit has **distinct columns**, `N = max column index + 1`,
  and exactly `n` columns.

**Confirmed**: the consolidation is a faithful, loss-free union of the two
exhaustive runs plus the one certified point; no re-derivation of circuits is
performed (columns are copied verbatim from the verified quotient reps).

---

## Summary of the audit

| step | implements | verdict |
|---|---|---|
| 1 | marked check-part parents from weight-`c` classes | ✅ matches |
| 2 | `R(C)`, `C`, quotient `V = R(C)/C` | ✅ matches (comment uses `^` for the `∧` generator) |
| 3 | pairwise compatibility `B_j = |a∧b∧h_j| = 0` | ✅ matches (mod-2 bilinearity verified) |
| 4 | clique + independence frame enumeration | ✅ matches |
| 5 | phase-polynomial gate readout + degeneracy rejects | ✅ matches |
| 6 | column assembly, parity + exact fault distance | ✅ matches; repeated-column branch is unreachable/defensive |
| 7 | dedup key + GL annotation + best distance | matches; the `dedup_signature` string that used to mislabel this as GL(k,2) now names `S_k` |
| 8 | driver, node budget, partial flagging | ✅ matches; only `n=31` was partial |
| 9 | GL(5,2) collapse completes `n=31` | ✅ matches; invariances asserted at runtime |
| 10 | consolidation + plot | ✅ faithful union; three independent cross-checks pass |

**Net finding:** one documentation discrepancy (Step 7 metadata string, since
corrected in the shipped engine), no algorithmic bug. The effective dedup is the more conservative `S_k` key, so the
classification distinguishes at least as many gate classes as the JSON string
claims, never fewer.
