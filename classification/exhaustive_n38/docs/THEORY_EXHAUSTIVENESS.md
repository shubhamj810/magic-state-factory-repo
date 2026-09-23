# Why the classification works, and why it is exhaustive for `n ≤ 38`

This document gives the mathematical justification behind the algorithm audited
step-by-step in [`ALGORITHM_STEP_BY_STEP.md`](ALGORITHM_STEP_BY_STEP.md). It
answers two questions:

1. **Why is the algorithm correct** — why does enumerating compatible,
   independent output frames over the quotient `V = R(C)/C` produce exactly the
   distance-≥3 factories, with their true logical gates?
2. **Why is it exhaustive for `n ≤ 38`** — why do the marked parents cover
   every possible check part, and why does the per-parent search miss nothing?

Current overview of this directory: [`../README.md`](../README.md). The
overview-level treatment of the same argument is
[`../../../theory/02_classification.md`](../../../theory/02_classification.md).

Throughout, a factory is a diagonal, degree-≤3 (level-3) generalized
triorthogonal circuit. Rows of its `F₂`-matrix are split into `k` **output
rows** `a_1..a_k` and `r` **check rows** `h_1..h_r`; columns index the physical
qubits / parity rotations. The physical length is `n` (number of columns), and
`N = k + r`.

---

## 1. The object and its logical gate

A diagonal level-3 factory applies, on postselection, a diagonal gate whose
phase is a Boolean polynomial of degree ≤ 3 in the logical variables. That
polynomial is read off from the **output-only overlap parities**:

- a linear term `x_i` (a `T` on logical `i`) iff `|a_i|` is odd;
- a quadratic term `x_i x_j` (a `CS` on `i,j`) iff `|a_i ∧ a_j|` is odd;
- a cubic term `x_i x_j x_l` (a `CCZ` on `i,j,l`) iff `|a_i ∧ a_j ∧ a_l|` is
  odd.

(`∧` is the pointwise AND of `F₂ⁿ` vectors; `|·|` is Hamming weight; parities
are mod 2.) So the *gate* is the multiset of odd output monomials — this is the
`gate` phase-polynomial string used everywhere in the catalog.

For the circuit to implement *that* gate and nothing else, every parity that
touches a **check** row must vanish, and the check space itself must be
triorthogonal. Concretely, with `a` any output and `h` any check:

| condition | meaning |
|---|---|
| `\|h_i\|, \|h_i∧h_j\|, \|h_i∧h_j∧h_l\| ≡ 0` | the check space `C` is triorthogonal |
| `\|a ∧ h_j\| ≡ 0` | each output commutes with each check (output–check) |
| `\|a ∧ h_i ∧ h_j\| ≡ 0` | output–check–check |
| `\|a ∧ b ∧ h_j\| ≡ 0` | output–output–check |

These are the standard generalized-triorthogonality conditions specialised to
degree 3. Everything the algorithm does is an efficient way to enumerate rows
satisfying them.

---

## 2. Linearising the search: `R(C)` and the compatibility form

Fix the check part `C` first (Section 4 explains how `C` is chosen
exhaustively). Then the conditions above split by how many *distinct output
rows* they involve:

- **Conditions on a single output `a`** are all *linear* in `a`:
  `a·h_j = 0` and `a·(h_i∧h_j) = 0`. Their common solution space is the
  linear space
  ```
  R(C) = { a ∈ F₂ⁿ : a ⊥ span{ h_i , h_i∧h_j } } .
  ```
  So every admissible output row lives in `R(C)` — a linear-algebra object, not
  a search.

- **The one condition coupling two outputs**, `|a ∧ b ∧ h_j| ≡ 0`, is
  *bilinear* in `(a,b)`. Define the `r` forms
  ```
  B_j(a,b) = ⟨ a , b ∧ h_j ⟩ = |a ∧ b ∧ h_j| (mod 2).
  ```
  Two admissible rows are **compatible** iff `B_j(a,b)=0` for all `j`.

- **There is no condition coupling three or more outputs.** The cubic parity
  `|a∧b∧c|` is *read as gate content*, not constrained to vanish. This is the
  key structural fact that makes the search a **clique problem**: a set of
  outputs is jointly admissible iff it lies in `R(C)` and is *pairwise*
  compatible. No higher-order joint constraint exists.

Hence a `k`-output factory on this check part is precisely a `k`-element
**clique** in the compatibility graph on `R(C)`, with the outputs linearly
independent (so they are `k` genuine logicals). Its gate is the phase
polynomial of Section 1. This is a complete, if-and-only-if, characterisation —
which is why the recursive frame enumeration of the algorithm is *sound and
complete on each parent*.

---

## 3. The gauge quotient `V = R(C)/C`: why we may divide by `C`

If `c ∈ C` (a combination of check rows), then `a` and `a + c` are the **same
logical row up to an `X`-type stabilizer** of the code — a borrowed-identity /
gauge move that changes neither the logical gate nor admissibility. Formally,
because the check space is triorthogonal and `a,b ∈ R(C)`:

- single/pair/triple gate parities are unchanged:
  `|a+c| ≡ |a| + |c| ≡ |a|` (checks have even weight `|c| ≡ 0`); and
  `|(a+c)∧b| ≡ |a∧b| + |c∧b| ≡ |a∧b|` because `|c∧b| = |b ∧ h_i…| = 0` for
  `b ∈ R(C)`; likewise for the triple;
- compatibility is unchanged: `B_j(a+c,b) = B_j(a,b) + |b ∧ (h_i∧h_j)| =
  B_j(a,b)` since `b ∈ R(C)`.

Therefore the entire problem — admissibility, compatibility, and gate — is
**invariant under translation by `C`**, and descends to the quotient
```
V = R(C) / C .
```
This is not cosmetic. The row-code dimension reaches 16 on the hardest parents,
but `dim V ≤ 11` across the whole ladder (audited; max attained at `n=31`).
Quotienting removes a factor `~2^r` of redundant rows per output, and — more
importantly — it shrinks the search enough that on almost every parent it runs
to completion with **no node budget**, i.e. exhaustively. Enumerating cliques in
`V` (excluding the identity coset `0`) instead of in `F₂ⁿ` is what turns an
intractable row search into a complete classification.

---

## 4. Why the check-part base is exhaustive for `n ≤ 38`

The one external input is the list of admissible check parts `C`. This is where
`n ≤ 38` comes from, and it rests on the **Nezami–Haah classification of unital
triorthogonal spaces** (arXiv:2107.09684), which is complete for indicator
words of weight `< 40`.

### From a check support to a classified polynomial

For a *reduced distance-≥3* matrix, the check columns form a set `P` of
**distinct nonzero points** in `F₂ʳ`. Define its origin-augmented support by

```
W = P             if n is even,
W = P ∪ {0}       if n is odd.
```

Thus `|W| = c = n + (n mod 2)` is even. Triorthogonality of the check rows says
that, for every coordinate monomial `x_I = ∏_{i∈I} x_i` of degree
`1 ≤ |I| ≤ 3`,

```
Σ_{p∈W} x_I(p) = 0  (mod 2).
```

The same equation for the degree-zero monomial is `|W| = 0 (mod 2)`. Hence the
indicator word `1_W` is orthogonal to every degree-≤3 polynomial:

```
1_W ∈ RM(3,r)⊥ = RM(r-4,r).
```

This is the precise polynomial object classified by Nezami–Haah / KTA. In
matrix language the same operation first appends the zero check column when
`n` is odd and then adjoins the all-ones row, producing a unital
triorthogonal space. Conversely, deleting the marked origin when it lies in
`W`, or merely choosing it outside `W`, recovers `P`; so this passage loses no
check parent once the origin is retained as a marking.

For `n ≤ 38`, the word has weight `c ≤ 38`. It is therefore affine-equivalent
to one of the finitely many supports `S` tabulated in
[`nezami_haah_reps.py`](../nezami_haah_reps.py)
(weights `16, 24, 28, 30, 32, 34, 36, 38`). Each table entry is represented in
its intrinsic affine span: `S ⊆ L ≅ F₂ᵐ` and `aff(S) = L`. Affine linear
factors in an ambient word cut out such a flat inside a larger ambient space;
after restriction to the flat, the remaining support is one of these
full-span representatives. They do not create another kind of marking.

### The three marking cases

The classification is affine, whereas a check matrix has a distinguished
zero: its columns must be nonzero. After an affine equivalence sends `W` to a
table support `S ⊆ L`, let `o` be the image of the original zero. The marked
object is therefore the pair `(S,o)`, not just `S`. Since affine maps preserve
membership,

```
o ∈ S  if and only if  0 ∈ W  if and only if  n is odd.
```

There are exactly three possibilities for the position of `o`:

| parity | position of `o` | check support after moving `o` to zero | implementation |
|---|---|---|---|
| odd | `o ∈ S` | `(S + o) \ {0}` | every `o ∈ S` in `marked_odd` |
| even | `o ∈ L \ S` | `S + o` | every `o ∈ F₂ᵐ \ S` in `marked_even` |
| even | `o ∉ L` | `{(s,1) : s ∈ S}` up to check-basis change | the single hyperplane-miss lift in `marked_even` |

Here `+` is translation in characteristic two. The table is exhaustive
because every point is in exactly one of `S`, `L \ S`, and the ambient space
outside `L`; parity rules out the other combinations. It remains to justify
why the last row is one case rather than many.

Non-redundancy fixes the ambient rank as well. In the first two rows, moving
`o` to zero makes the check support span an `m`-dimensional linear space, so
`r=m`. In the third row its span has dimension `m+1`, so `r=m+1`. Any further
ambient directions would be linearly dependent/zero check rows, not new
parents.

**Hyperplane-miss lemma.** Suppose `o ∉ L`, translate `o` to zero, and let
`D = L-L` be the `m`-dimensional direction space of `L`. Then `L+o` is an
affine `m`-flat not containing zero, and its linear span is
`U = D ⊕ ⟨v⟩` for any `v ∈ L+o`. An invertible linear map on `U` can send
`D` to `F₂ᵐ × {0}` and `v` to `(0,1)`. It therefore sends `L+o` to the
hyperplane `F₂ᵐ × {1}`. In those coordinates the image of the support has
the form `{(A(s)+a,1):s∈S}` for an invertible `A` and a translation `a`.
The linear map

```
(x,t) ↦ (A⁻¹(x + t a), t)
```

fixes the origin and sends this image to the canonical lift
`{(s,1):s∈S}`. Such linear maps are exactly changes of check-row basis. Any
ambient coordinates beyond `U` give zero/redundant check rows and disappear in
a non-redundant parent. Therefore there is no additional marking indexed by
how far outside `L` the origin lies.

The converse is immediate in all three rows: reinsert the marked zero when
needed and undo the translation/lift to recover a support affine-equivalent to
`S`. Thus the generated family is neither missing an affine-translation case
nor an extra-ambient-dimension case. It is deliberately *overcomplete* because
different listed origins can be related by an affine automorphism of `S`; this
only repeats parents and cannot invalidate an exhaustiveness claim. The raw
parent counts (320 at `n=31`, 504 at `n=35`, 3032 at `n=38`) are counts before
that optional automorphism quotient.

**The `n`-gaps are real, not omissions.** The weights present are exactly
`{16,24,28,30,32,34,36,38}`, so `c = n + (n mod 2)` is classifiable precisely
for
```
n ∈ {15,16, 23,24, 27,28,29,30, 31,32,33,34, 35,36,37,38}.
```
The missing `n` (17–22, 25, 26) map to weights `18,20,22,26`, which host **no
unital triorthogonal class** in the relevant range — there is no distance-≥3
reduced check part of those lengths to classify. The ladder is therefore
complete on its stated domain, and the gaps carry information (no factory of
those lengths exists in this family), rather than signalling unchecked cases.

---

## 5. Why distance ≥ 3 is exactly the right scope

The base classification is a classification of **distinct nonzero check
supports**. This is *hereditary* (well-behaved under deleting an output row)
**only** for distance-≥3 objects, and that is precisely the scope claimed.

The subtlety: deleting an output row can turn two distinct child columns
`(0,s)` and `(1,s)` into the same parent column `s` (a repeated column), or turn
an output-only column into a zero column. A classification built on
*distinct nonzero* supports would miss such children — but this can only happen
when a repeated/zero column exists, which forces a **weight-≤2 logical operator**,
i.e. distance ≤ 2. Restricting to **distance ≥ 3** removes exactly these cases:
then check columns may be assumed distinct and nonzero, the support base is
hereditary, and the classification is complete. (Including distance-2 codes
would require classifying parent *multisets* with every fibre retained — a
strictly larger problem, deliberately out of scope.)

This is also why the algorithm's "reduced, distinct-column" assumption is not a
loss: within `d ≥ 3` it is automatic. Every marked parent already has distinct
nonzero columns, every assembled factory column carries a distinct check-bit
signature, and the exact distance is recomputed from the raw columns by fault
enumeration (not assumed).

---

## 6. Completeness of the per-parent search

Given a correct, complete list of check parents, the per-parent search misses
nothing because:

1. every admissible output lies in the *finite linear space* `R(C)`, fully
   enumerated as the quotient `V` (Section 2–3);
2. joint admissibility is *exactly* pairwise compatibility + linear
   independence (Section 2), so a factory is exactly a clique of independent
   quotient points — and the recursion enumerates every such clique once
   (increasing-coordinate DFS with clique-mask intersection). "Independent"
   here means independent *in `V`*, i.e. modulo `C`; Section 8 says exactly what
   that covers, and why the frames it does not cover carry no extra magic;
3. the gate is a *function of the frame* (Section 1), computed directly, and
   verified together with the exact distance from the assembled columns.

The only place completeness could fail operationally is the node budget. In the
`k ≤ 4` run, exactly **one** parent hit it: the `n=31` class-0 parent (the 31
nonzero points of `F₂⁵`, the unique `dim V = 11` case). It is finished by an
exact method, not left partial.

---

## 7. The hard parent `n=31` and the `GL(5,2)` collapse

The `n=31` class-0 parent's automorphism group is the full `GL(5,2)` (order
9,999,360): every invertible `5×5` matrix permutes the 31 nonzero points of
`F₂⁵`, hence permutes the 31 physical columns while preserving the check code.
This is a genuine relabelling equivalence of the factory, and it acts on the
quotient `V`.

Two facts make it a *complete* shortcut rather than a heuristic:

- the **compatibility relation and the logical gate are `GL(5,2)`-invariant**
  (asserted at runtime in `hard_parent_n31.py`); and
- every output frame is `GL(5,2)`-equivalent to one whose *first* output is one
  of the **5 orbit representatives** of quotient points.

So fixing the first output to an orbit rep and freely enumerating the rest
visits every equivalence class of frames — an exhaustive classification of this
parent that runs in seconds with no budget. It certifies that `n=31` realises
**exactly one gate class per `k`** for `k = 1..5` (the fully-symmetric,
all-degree-≤3 punctured Reed–Muller family), and that these are the only ones.
This same collapse turns the ~`10⁷` raw configurations on the parent into ~`10³`
inequivalent classes.

---

## 8. What "exhaustive for `n ≤ 38`" precisely means — and its limits

Putting the pieces together, the exact claim certified is:

> For every `n ≤ 38` with a classified check weight `c = n + (n mod 2)`, the
> algorithm enumerates **all** reduced, distance-≥3, output-marked level-3
> generalized-triorthogonal factories with `k` logical outputs that are
> independent modulo the check span `C`,
> deduplicated up to relabelling the output qubits (`S_k`), with exact distance,
> for `k` up to the point where the quotient dimension allows it.

Concretely this yields **74 distinct `(n, k, d=3)` gate classes** (73 with
circuits embedded in the quotient catalogs, plus the explicit certified
`[[31,5,3]]` witness in
[`n38_k56_certificate.json`](../results/n38_k56_certificate.json)), matching
[`quotient_classification_report.md`](quotient_classification_report.md).

Boundaries of the claim, stated honestly:

- **Equivalence is `S_k`, not `GL(k,2)`.** Gates are identified up to output
  relabelling; the coarser `GL(k,2)` logical-Clifford class is only annotated.
  (Two gates sharing a `GL(k,2)` class but not an `S_k` class are kept
  separately — e.g. the two `GL`-class-62 gates at `[[35,3,3]]`.) An earlier
  engine's JSON `dedup_signature` string mislabelled this as `GL(k,2)`; the
  code, the string shipped here, and this document all use `S_k`. See
  [`ALGORITHM_STEP_BY_STEP.md`](ALGORITHM_STEP_BY_STEP.md) Step 7.
- **`k` ceiling.** `k ≤ 4` is complete across all classifiable `n`; `k = 5`
  occurs only at the `[[31,5,3]]` punctured-RM point; **no `k = 6` factory
  exists** at `d = 3`, `n ≤ 38` (for `n = 38` the quotient dimension caps at 4
  independent outputs beyond the `n = 31` family). The two-rank-layer proof,
  completed-run hashes and positive witness are packaged in
  [`N38_K56_CERTIFICATE.md`](N38_K56_CERTIFICATE.md).
- **Distance ≥ 3 only.** Distance-2 codes are deliberately excluded (Section 5);
  including them needs the larger multiset classification.
- **Level 3 (degree ≤ 3).** Only `T`/`CS`/`CCZ`-content gates; higher-level
  targets (`√T`, `CCCZ`, …) are a separate ladder.
- **Independence is modulo `C`.** Frames whose outputs coincide in `V` but not
  in the row space are outside the method. They carry no extra magic, so the
  claim is a boundary on circuit *representations* and not on gate content; the
  next subsection proves it.

### Lift-degenerate frames: what independence modulo C leaves out, and why it carries no magic

The enumeration covers factories whose `k` output rows are linearly independent
**modulo the check span `C`**. Frames using both `a` and `a + c`, for `c ∈ C`,
as two *separate* output qubits are not enumerated.

The premise of the obvious objection — "adding a check row to an output row
cannot change the gate, so why does this matter?" — is correct, and it is the
descent of Section 3: replacing a single output row `a` by `a + c` leaves every
degree-≤3 parity alone, which is exactly why the gate is a function of `V`. The
skipped case is a different object. It uses `a` **and** `a + c` as two separate
output qubits, so it is a larger circuit on more qubits, not a re-labelling of a
smaller one.

Such a frame is real: the columns come out distinct, every check-touching parity
vanishes, and the fault distance is 3. Its gate is forced, and always the same
one. Check rows have even weight, so `|a|` odd forces `|a + c|` odd; and
`a ∈ R(C)`, so `|a ∧ c|` is even and hence `|a ∧ (a + c)| = |a| − |a ∧ c|` is
odd. The gate is therefore always

```text
0+1+01   =   T_0 · T_1 · CS_01,
```

with no other possibility. A concrete example is the `[[15,2,3]]` with gate
`0+1+01`, found by ansatz-free column-level SAT over the `[[15,1,3]]` check
part; its 6 rows have rank 5 and its exact T-count is 1. It is deliberately not
in the search catalogue, which rejects a declared width whose output rows are
dependent modulo the check span — one output CNOT leaves the second output an
idle `|+>`, so the circuit is the `[[15,1,3]]` on a spare wire. The removal and
its four companions are recorded in
[`../../../symmetry_sat_search/examples/README.md`](../../../symmetry_sat_search/examples/README.md).

**The omission costs no magic.** One output CNOT replaces the second output row
`a + c` by `(a + c) + a = c`, and `c` carries no monomial of any degree at all.

*Parity lemma.* For `u, v ∈ F₂ⁿ`, `|u + v| = |u| + |v| − 2|u ∧ v|`, so
`|u + v| ≡ |u| + |v| (mod 2)`: weight mod 2 is `F₂`-linear in its argument.
Since `(u + v) ∧ w = (u ∧ w) + (v ∧ w)` pointwise, the map `x ↦ |x ∧ w| mod 2`
is likewise `F₂`-linear in `x` for any fixed `w`, and so is
`x ↦ |x ∧ w ∧ w'| mod 2`. Each of the three statements below is therefore a
linear functional on `C`, and it suffices to check it on the generators
`h_1, …, h_r`.

1. **No `T`: `|c|` is even for every `c ∈ C`.** Every check row has even weight
   (`|h_i| ≡ 0`), and weights add mod 2 under XOR, so the linear functional
   `x ↦ |x| mod 2` vanishes on every generator and hence on all of `C`.
2. **No `CS`: `|c ∧ a'|` is even for every `c ∈ C` and every `a' ∈ R(C)`.** On
   the generators, `|h_i ∧ a'| ≡ ⟨a', h_i⟩ = 0`, which is the `a·h_j = 0` half of
   the definition of `R(C)` — that is, `R(C) ⊆ C^⊥`. By linearity in `x` this
   extends from the `h_i` to all of `C`.
3. **No `CCZ`: `|c ∧ a' ∧ a''|` is even for every `c ∈ C` and every compatible
   pair `a', a'' ∈ R(C)`.** On the generators, `|h_j ∧ a' ∧ a''| ≡ B_j(a', a'')`
   is the compatibility form of Section 2, which vanishes for every check row
   `h_j` precisely because the pair is compatible. Linearity in `x` extends it
   to all of `C`.

The same argument disposes of the mixed output–output–check condition that a
factory has to satisfy: on the generators `|h_i ∧ a' ∧ h_j| ≡ ⟨a', h_i ∧ h_j⟩`,
which is the `a·(h_i∧h_j) = 0` half of the definition of `R(C)`, so
`|c ∧ a' ∧ h_j|` is even for every `c ∈ C` as well.

So after one Clifford the extra output is an idle `|+⟩` spectator, and what is
left is exactly the lower-width factory the enumeration did produce. The
arithmetic agrees. Over `ℤ₈` the phase polynomial of `T_0 · T_1 · CS_01` is
`x₀ + x₁ + 2x₀x₁`, and `x₀ ⊕ x₁ = x₀ + x₁ − 2x₀x₁`, so the polynomial equals
`(x₀ ⊕ x₁) + 4x₀x₁` — one `T` on the parity of the two outputs, times a `CZ`,
which is Clifford. Its exact minimal T-count is therefore **1**, not 2, and the
`[[15,2,3]]` described above has exact T-count 1 for that reason, which is why
the search catalogue does not carry it.

The conclusion is that the classification is complete for magic **content** —
which gates are achievable at each `n`, the largest genuine output width, the
largest exact T-count — and incomplete only for circuit **representations** in
which an output is Clifford-equivalent to an idle spectator.
[`classify.py`](../classify.py) already discards frames with a *manifestly* idle
output (the `covered` check in `record`, Step 5 of
[`ALGORITHM_STEP_BY_STEP.md`](ALGORITHM_STEP_BY_STEP.md)), so excluding
lift-degenerate frames is the same policy one Clifford deeper, not a different
one.

Two things remain true on top of that. The quotient method structurally cannot
represent these frames, and not for want
of trying: their gate depends on *which lift* of a quotient point is chosen, so
it is not a function of `V` at all — and the entire descent argument of
Section 3, the one that makes this search complete with no node budget, is
exactly the statement that the gate *is* a function of `V`. Enumerating them has
to be done in the row space ([`classify_rowspace.py`](../classify_rowspace.py),
which enumerates frames independent in `R(C)` rather than in `V`) or by raw
column-level search.

And if you are counting distinct *circuits* rather than distinct resources — for
instance because a spectator output is free in your architecture and you would
rather have the `CZ` than the `CNOT` — then the catalogue undercounts, and
`classify_rowspace.py` is again the tool.

[`tests/test_classification.py`](../tests/test_classification.py) proves both
halves on the small end of the ladder: the row-space enumerator finds exactly
the quotient classes plus lift-degenerate ones and every extra class has gate
`0+1+01`
(`test_every_extra_rowspace_class_is_lift_degenerate`); the CNOT'd row of every
extra class lands in `C` and carries no monomial of any degree
(`test_lift_degenerate_frames_carry_no_extra_magic`); and the exact minimal
T-count of `T_0 · T_1 · CS_01` is 1
(`test_the_omitted_gate_is_one_T_in_disguise`).

A notable *negative* result that falls straight out of exhaustiveness: **pure
`CCZ` (the monomial `012` alone) is absent for all `n ≤ 38`.** CCZ content
appears only inside the fully-symmetric degree-≤3 combinations. This is what
proves the `CCZ ≥ 39` lower bound in this repository — the classification
searched every candidate and found none; the shipped certificate is
[`../catalog/CLASSIFICATION_N38.md`](../catalog/CLASSIFICATION_N38.md), which
carries no pure-CCZ class. The separate lower-bound ladder that once derived the
same bound by a different route is not part of this repository.
