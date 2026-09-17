# 07 — Structural results, with their exact scope

Everything here is **proved**, not measured — but a theorem is only as useful as
its scope, so each carries what it does *not* cover. Contradicting one of these
requires a proof, not a search result.

Vocabulary: `r` is the number of check wires (the check rank); a **parent** is
the check structure before output rows are chosen.

---

## 1. Which `n` can exist at all

**Admissible check sets are exactly the supports of Reed–Muller codewords,
punctured at the origin.** Since codewords of degree `≤ r-1` have even weight,
admissible `n` come in **pairs `(n, n+1)`**.

* **`n mod 4`.** Column counts of `r ≤ 7` parents are constrained mod 4; on
  6/7-check parents `n ≡ 0, 3 (mod 4)`.
* **A `T` on an `r = 6` parent exists iff `n ≡ 3 (mod 4)`.**
* **`n ∈ {17..22, 25, 26}` admits NO `d = 3` factory at any rank.** From
  Kasami–Tokura: the available weights below 32 are `{16, 24, 28, 30}`.
* **`e(n) = n + (n mod 2)` must be a weight of `RM(r-4, r)`.** Therefore
  `e(n) ≡ 2 (mod 4)` **forces check rank ≥ 8** — sixteen for sixteen on the
  catalogue's empty cells in `[39,70]`.

> **Scope.** The last item explains the gaps in the `nu(m)` table as a *theorem*,
> not a search gap — but note that essentially every tool in this corpus is a
> rank-≤7 tool, so rank ≥ 8 is under-explored rather than impossible.

## 2. Smallest factories — the fully closed end

* **`n ≥ 15` for `d ≥ 3`, and `[[15,1,3]]` is the unique `n = 15` parent.**
  So `nu(1) = 15` is optimal.
* **`[[8,3,2]]` is the smallest non-Clifford factory that exists**, and its orbit
  is necessarily `CCZ`. PROVEN by exhaustive enumeration: 6720 circuits at
  `n = 8`, all `[[8,3,2]]`.
* **The `d = 2` ladder is closed and optimal**: `CCZ` at `n = 8`, `CS` at 12,
  `T` at 14.
* **Row-weight lemma.** An odd legal row has weight `≥ 7`, tight iff its seven
  points form a specific configuration.

## 3. Parents in the `48 ≤ n ≤ 128` window

* **At `d ≥ 3` every parent is a punctured simplex.**
* **`n = 48` collapses to ONE parent** — proved.
* **The `r = 6` parent reaches only `n ∈ {…, 47, 48, 63}`**; the `r = 7` parent
  reaches 31 values in the window.
* **Halving identity: `r = 7` is two copies of `r = 6`** — proved.
* **`CCZ³` and `CCZ⁴` at `n = 63` are IMPOSSIBLE in the quadratic family** —
  590/590 first-block classes exhausted.
* **The quadratic layer at `n = 48` classifies into 139 orbits**, 26 carrying a
  `CCZ`.
* **`d ≥ 4` for free**: on an odd-detecting (affine-hyperplane) parent, even `n`
  with pure `CCZ` at `d ≥ 3` gives `d ≥ 4` at no cost — the all-ones-check lift.

> **Scope.** "Impossible in the quadratic family" is exactly that. It says
> nothing about cubic or higher layers on the same parent.

## 4. Appending outputs

* **Appending an output row is an `F_2` linear system** — proved. Not a search.
* **Saturation**: one solve decides whether *any* row can be added.
* **A new row must be independent of the existing rows modulo the check span.**
  Nothing in the naive conditions excludes `f = f' + c` for an earlier row `f'`
  and a check `c` — every parity `f` owes is one `f'` already satisfies. Omitting
  this produced a `[[100,15,4]]` whose effective width was 11.

## 5. The `gamma` closures on `RM(3,10)`

* **`d = 3` and `d = 4` are CLOSED for `gamma`** by a Hamming bound on the
  puncture-set size (floors 1.495 and 1.185). Derived independently three times.
* **All punctured `RM(2,m)` at `d ≥ 5` are closed** — flat-cap lemma. So inside
  punctured RM, the `n < 1000` window is **`RM(3,10)` only**.
* **The dual-codeword LP can never certify `t_max(6) < 640`** — its value is
  exactly 640. A whole proof technique is ruled out, not merely unsuccessful.

> **Scope.** The Hamming closures are scoped to that parent and those distances.
> They say nothing about `d ≥ 5` on the same parent — which is exactly where the
> records live.

## 6. The `n = 127` width programme

A long autonomous campaign on "how wide can a pure-`T` factory at `n = 127` be".
Records the shape of a *hard* sub-problem:

* **`[[127,23,3]]` found** on a Gabidulin/MRD scaffold (nullity 41, deficiency 7).
* **Deficiency ceiling theorem: `D ≤ 7`** for all subspace-hole scaffolds at
  `n = 127` — machine-checked over 95 MRD codes including nonlinear ones.
  Decomposition `D = (7 − span O) + dim B`, with equality certified.
* **The Φ invariant**: width `≥ 24` at `n = 127` is PROVEN to need `≤ 14`
  lights — every `s ≥ 15` shape caps at 23. Parity lemma `Φ ≤ |O| − 2·span(O)`
  tight 27/27.
* **Spread-product lemma**: every legal row costs `≤ 8` at any scaffold.
* **The 23-wall**: the cost-floor route was **falsified** (a constructed
  30-state beat every arithmetic gate); the minimum surviving first-heavy cost
  is 5, certified exhaustively.

**And two results that were refuted by their own follow-up**, which is why they
are listed here rather than as established fact:

* a Φ-equality conjecture — **FALSIFIED by 720 counterexamples**;
* a "joint-spend law" — **REFUTED at depth**;
* a width law measured as `17 + 2D` that **does not transplant**: `n = 111`
  walls at 17 and `n = 95` at 15, both certified.

> **The lesson worth inheriting from this programme**: a measured "law" that fits
> every case you have seen is a conjecture. Two here fit dozens of cases and were
> then refuted. Another failed by **40×** when extrapolated.

## 7. Argued, not certified — handle with care

From the campaign halted at round 2:

* Two theory results (`T-E` at even `δ ≥ 4`, and `T-J` at `δ ≥ 18`) are
  **ARGUED** pending a proof repair at one named step. The supporting lemma was
  **refuted by an explicit counterexample** that satisfies every stated
  hypothesis — while the theorem's *conclusion* survived on that same
  counterexample. A proof repair, not a collapse, but do not build on it.
* `δ = 2` remains **CERTIFIED unconditional** (the gap case cannot arise).
* **`[[512,39]]`'s `d = 8` is ARGUED, not enumerated**: faults lie in `RM(6,9)`,
  minimum weight 8, plus an explicit weight-8 witness. `d ≥ 7` *is* enumerated.

## 8. A published bound this corpus disproved

**`n(CCZ) ≥ 39` is FALSE.** It was stated in this project's own manuscript and
in a classification write-up; the `CCZ` Clifford orbit is reached at **`n = 36`**
by explicit witness. Both files now carry a marked correction.

The mechanism of the error is worth knowing because it generalises: the 74 gate
classes it rested on are classes of *gate strings*, but a factory's output is
defined only **up to a final Clifford** — and `CS01·CS02`, which does occur at
`n = 36`, is `CCZ012` up to a Clifford containing one Hadamard. **An enumeration
can be perfectly correct and still support a false bound, if the equivalence it
quotients by is not the one the claim needs.**

---

## The floor for punctured monomial codes (2026-09-15)

Four campaigns compose into one statement, and it is the most useful structural
fact this repository holds about `gamma`:

> **Within punctured monomial codes at `d = 6`, `gamma = log7/log6 = 1.086033`
> is a floor.** It can be *attained* and not beaten, for every `m <= 9`.

The pieces, each with the scope that makes it usable:

**A13 (the identity that makes the floor meaningful).** Taking one puncture per
cell of a top dual direction gives `n/t = 7` EXACTLY, at every `m` — so the
canonical construction sits at `gamma = log7/log d`, and at `d = 6` that *is*
the Wills bar. The bar is not a lucky instance; it is this construction at
`m = 10`. Beating it therefore means holding `2^(m-3) + 1` punctures.

**The fibre lemma (`m = 10`, the Wills parent).** The weight-8 dual layer is
exactly the 3-flats meeting the heavy subspace in dimension `>= 2`; any two
punctures in one light fibre plus any third anywhere lie in a common weight-8
word; at `d = 6` such a word admits only 2. Hence one puncture per fibre, and
`t <= 2^(m-3) = 128`. *Scope: that parent. Not all `m = 10` parents.*

**R6 (`m <= 9`, every parent).** The same conclusion, reached by a different
route — a support cap via `D`-free sets, a complete classification (exactly 15
valid parents at `m = 8`), and a one-triple lemma giving a unified criterion.
The caps are **attained**: `[[248,8,6]]` and `[[496,16,6]]`, both `n/t = 31`
exactly, hence `gamma = 1.9165` independent of `m`. *Scope: `m <= 9`. At
`m = 10` the criterion has a survivor (`dim 138`), so that cell is open.*

**Why the floor is escapable at all.** The current bar `[[860,128,6]]`,
`gamma = 1.063146`, has `n/k = 6.719` — **below the canonical 7**, which is
only possible from outside the family. It is triorthogonal rather than
8-divisible (check rows `0` or `6` mod 8) and `n != 2^m - k`. The floor is
real; the way past it is to leave the family, not to search harder inside it.

## Two routes out of the family, both priced (2026-09-15)

**Downset punctures.** Closed: `gamma >= 1.502` at `n <= 1000`, exhaustively,
the window being finite because `n >= 2^(m-1)` forces `m <= 10`.

**Extension-field alphabet reduction** (`F_{2^m} -> F_2`, San-José
arXiv:2609.08203). Closed at `n <= 1000` by an arithmetic obstruction rather
than a search: `s_min(m) = floor(m^2/4) + m - 1` (the Waring rank of `Theta_m`
over `F_2`) against `k ~ m/2`, so **the blowup grows quadratically while the
payload grows linearly**. Best reachable `gamma = 1.439227`; largest `k`
anywhere on the route is 64 against the 147 the bar needs. The bound is not
about Reed–Solomon — the scan took the outer dual distance at its Singleton
maximum, so it covers every outer code of ordinary Schur growth. *Scope:
unconditional for `m <= 6`; above that it rests on the `s_min` conjecture.*

The one question that would settle the route: **is there a code with
`C^{*3} subset C^perp`, `dim C^{*3}` about 3x below the RS-like `3k-2`, at
`k ~ n/2`, with dual distance near Singleton?** These pull against each other —
degenerate Schur powers come from block structure, and block structure collapses
dual distance.
