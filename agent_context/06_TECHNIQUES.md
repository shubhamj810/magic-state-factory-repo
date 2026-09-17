# 06 — How to actually search: reformulations, methods, measured costs

The single biggest lever in this problem is **not** a better solver. It is
changing what you are searching over. Every large result here came from a
reformulation that made the search space smaller or the test cheaper.

## 1. The reformulations, in order of value

### 1a. Distance-3 as a set of syndromes

A distance-3 factory *is* "the check parts `s_j` are distinct and nonzero", so
the check data is a **set** `S ⊆ F_2^r \ {0}` with `n = |S|`. Triorthogonality
becomes moment conditions on `S`:

```
chi = 1_S + (|S| mod 2)·delta_0          admissible iff  chi ∈ RM(r-4, r)
                                          and then n = |chi| - chi(0)

a row with support A ⊆ S is legal iff
psi = 1_A + (|A| mod 2)·delta_0  ∈  RM(r-3, r)      -- the NEXT RM code

T-parity of a row      = psi(0)
CS-parity of two rows  = 1 + <psi, psi'>
CCZ-parity of three    = the corresponding trilinear form
```

**Admissible check sets are exactly the supports of Reed–Muller codewords,
punctured at the origin.** Consequences that fall straight out: codewords of
degree `≤ r-1` have even weight, so admissible `n` come in **pairs `(n, n+1)`**
— which is why the `n` a parent can have is a theorem, not a search result.

### 1b. Puncturing as the search variable

For large factories, take `RM(r,m)` and delete a puncture set `P`, `|P| = t`:

```
n = 2^m - t        the game is: RAISE t AT FIXED d

d   = min over nonzero c in RM(2r,m) of ( |c| - |supp(c) ∩ P| )
A_w = #{ c in RM(2r,m) : |c| - |supp(c) ∩ P| = w }
```

**The growth rule**: a point `v` may be added to a `d ≥ D` set **iff `v` lies in
no weight-`D` harmful fault**. So `A_D` is not merely a scoring axis — it is
*the obstruction to the rate*. This single fact drives every ladder search here.

Computationally, with `φ(v)` the degree-`≤r` Veronese embedding and
`W = span φ(P)`, residues `φ(x) mod W` give:

| condition | test |
|---|---|
| `k = t` | `φ(P)` independent |
| `d ≥ 3` | residues distinct **and nonzero** off `P` |
| `d ≥ 4` | …and no three of them sum to zero |
| `A_w` | # `w`-subsets of survivor residues summing to zero |

Adding one point is a single `O(2^m)` pivot sweep — no re-echelonisation. This
reproduced five published rows (`n`, `k`, `d` **and** `A_d`) in **0.08 s total**
against the `O(n³)` column route.

### 1c. Appending an output row is a linear system

Whether another output can be added to an existing frame is an `F_2` **linear
system**, not a search. One solve says whether *any* row can be added
(saturation). This turned a combinatorial hunt into arithmetic and is what
closed several width questions.

## 2. Search methods, and what each is worth

| method | verdict here |
|---|---|
| **Ruin-and-recreate at depth** | **the current record's method.** Delete `R` punctures, add back more. The record came from a *depth-4* ruin after depths 1–3 were certified rigid |
| **Singer-orbit / symmetry ladders** | produced every record *before* the current one, then **plateaued** — 16 randomised restarts never exceeded `t = 111` |
| **Exhaustive orbit-swap scan** | found the `d = 6` record once randomised restarts stalled. The end of symmetry's reach |
| **Weight-/lookahead-ranked and stratified beams** | **all three stop at width 9** on the `n = 63` simplex where width 11 provably exists. Something structural; not a tuning problem |
| **CP-SAT on symmetric ansatz** | measured **plateau** at `d = 6` (`PROVEN_UB` 633 vs 131 needed) — UNDECIDED, not a timeout. Do not relaunch without a new idea |
| **Covering MIP** | **measured dead three times** (0 of 41 known-feasible points at 240 s, 150 s, 120 s). Killed |
| **Dual-codeword LP / cutting planes** | **provably vacuous**: the LP value is exactly 640, so it can never certify `t_max(6) < 640` |

**The pattern.** Symmetry gets you a long way and then stops dead; the escape
was an unsymmetric local move that a theorem made affordable.

## 3. Two tricks that made an infeasible search affordable

**A pruning theorem.** `|freed(R)| ≥ |R| + 1` or the ruin cannot gain. That cut
3.9M ruins to 13,860 candidates before any test ran.

**A validated symmetry dedup.** An 11-fold dedup cut 13,860 to 1,260 tests
(~47 min). *Validated* matters: it was first run on a class with known answers
and had to reproduce the same verdict, the same 44-element hit set, the same
`A_6` multiset, and a factor of exactly 11.0. An unvalidated dedup is a silent
correctness bug.

**The combination is the lesson**: a theorem to prune, a symmetry to quotient,
then exhaust what is left — and *price it before running it*.

## 4. Fault counting: the cost wall, exactly

This governs what is verifiable, and therefore what is claimable.

| weight | method | cost |
|---|---|---|
| 1–4 | meet-in-the-middle | milliseconds at `n ≈ 1000` |
| 5 | 2+3 split | `O(n³)`: seconds at `n ≤ 300`, **hours at `n ≈ 900`** |
| 6 | 3+3 split, `/C(6,3)/2 = 10` | ~3 s at `n = 256`; out of reach at `n ≈ 900` |
| 7 | 3+3+1 XOR-join | ~60 s at `n = 255` |

**Divisor discipline.** Each split counts every fault a fixed number of times:
weight 3 → 3, weight 4 → 3, weight 5 → 10, weight 6 → 10, weight 7 → 70.
*Assert divisibility before dividing.* A raw count that is not divisible means
the enumeration is wrong, and the assertion is free.

**Vectorising is worth ~1000×.** At `n = 880` with `k = 144` the check block is
only 32 bits, so a syndrome fits an `int64` and the 144-bit output block rides
in three `int64` lanes — exact, no hashing, ~5 s where the pure-Python route
takes hours. Where a syndrome does *not* fit one word, bucket on a collapsed key
and **confirm every bucket hit lane by lane**; then it is still exact.

## 5. Price the job before you run it

The discipline that produced the best results, worked end to end:

> A depth-4 census gave the freed-point histogram `{6: 825, 7: 66, 8: 11}`. A
> double gain needs `|freed| ≥ 6`, contributing `C(|freed|,6)` sets each:
> `825·1 + 66·7 + 11·28 = 1595`. None Singer-invariant, so `1595/11 = 145`
> orbit representatives × 2.5 s measured = **6–7 minutes** — not the 9.6
> core-hours a naive count suggests.

A measured price is a deliverable in its own right. One route was killed by
pricing alone: **509 priced core-hours decided in 18 minutes** by an algorithmic
reduction, a ~1560× saving, and the answer was "unreachable at depth ≤ 3".

## 6. Tooling failure modes seen here

Real bugs, all caught by re-deriving from columns — **none by reading code**:

* An `F_2` solver built echelon form **without back-substituting among pivots**,
  returning "solutions" that do not satisfy the system. Fix: a solver that
  asserts its own answer before returning it.
* A row-appender did not require the new row to be **independent modulo the
  check span**, returning a `[[100,15,4]]` whose effective width was 11.
* The same file **skipped an equation whose mask was empty** — valid only when
  the target is 0. With target 1 the system is inconsistent, and dropping it
  reported a `CCZ^5` that deposits `CCZ^3`.
* A search enforced fewer constraints than it reported (broken back-substitution
  in an incremental solve) and emitted frames with **extra** monomials.
* Randomised greedy computed a maximal common isotropic subspace as 6 where the
  truth was 8, and 6 where it was 15 — **a whole `d = 4` rate table was built on
  those numbers.** Compute such invariants exactly.
* An exact T-count decoder is valid only to 6 distinct qubits (it packs `2^k`
  into uint64 words) and **does not fail fast** above that — at `k = 40` it
  tries to build a `2^40` structure and never returns. Guard it.
* Gate-name parsing: legacy names concatenate indices with no separator, so
  `CCZ0914` is ambiguous and `T10` was read as two wires. **Emit comma form
  above index 9.**

## 7. Do not use τ as a class label

The ancilla-free minimal T-count `τ` of the unitary is invariant under CNOT
frames and diagonal Cliffords but **not** under the full Clifford group with
Hadamards. Using it to label output classes produces false *splits* (never false
merges). Real case: `CS01·CS02` is a single `CCZ` — `τ` says 4 vs 7; and a
catalogued `[[43,4,3]]` output is `T ⊗ CCZ`, proved by an explicit 11-gate
Clifford circuit containing exactly one Hadamard, across which `τ` falls 7 → 5.
