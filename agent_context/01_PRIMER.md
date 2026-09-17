# 01 — The object, the data model, and the metrics

Read this before anything else. It is the minimum needed to read a catalogue
row, and every later file assumes it.

## 1. What a factory is

A **magic-state factory** consumes `n` noisy `T` states and emits `k` better
ones. Concretely it is a set of `π/4` (`T`) rotations on `N` wires:

```
wires  0 .. k-1     OUTPUTS      the magic states you keep
wires  k .. N-1     CHECKS       measured and POSTSELECTED on 0
```

A **column** is the wire support of one rotation. The circuit *is* its column
set — order does not matter, because the rotations commute.

```
[[8,3,2]], the smallest non-Clifford factory that exists:

  columns = [[0,1,2,3],[0,1,3],[0,2,3],[0,3],[1,2,3],[1,3],[2,3],[3]]
  k = 3            N = 4            n = 8 columns
  wires 0,1,2 are outputs; wire 3 is the single check
  gate = CCZ(0,1,2)          d = 2          A_2 = 28
```

`n` is the number of columns — the noisy `T` states consumed, one per rotation.
`N` is the number of wires, which is a different quantity and not a cost.

## 2. Faults, distance, and `A_d`

Write, for column `j`:

```
mask_j = sum(1 << q for q in column_j)
syn_j  = mask_j >> k                  the CHECK part
out_j  = mask_j & ((1 << k) - 1)      the OUTPUT part
```

A **fault** is a subset `F` of columns — the inputs that arrived faulty:

```
UNDETECTED   iff   XOR_{j in F} syn_j == 0      no check fires
HARMFUL      iff   undetected AND  XOR_{j in F} out_j != 0
```

* **`d`**, the distance, is the least weight `|F|` at which a harmful fault
  exists.
* **`A_d`** is how many harmful faults there are at that weight.

One block therefore sends input error `p → A_d · p^d`. **Both numbers matter.**

Everything above depends only on the output/check split and the columns. It does
*not* depend on the gate.

## 3. The gate is recovered, never read

The gate is the phase polynomial the circuit realises, and it is a **property of
the columns**:

> the coefficient of monomial `(a,b,c)` is the number of columns containing all
> of `a, b, c`, taken mod 2.

Degrees 1, 2, 3 give `T`, `CS`, `CCZ` respectively. Two consequences:

* **A monomial touching a check wire must have even parity.** That is what makes
  a check a check. An odd one means the object is not a factory at all
  (*check contamination*).
* **Stored `gate` fields are claims and they lie.** In this corpus they are
  wrong in 62+ records — `"T^5"` parses as a single `T` on wire 5, and some
  records store an `S_k` relabelling of what their columns actually realise.
  Recover the gate; do not read it.

## 4. The metrics — and which ones are comparisons

| symbol | definition | what it is for |
|---|---|---|
| `k_essential` | outputs the recovered gate actually touches | **the denominator of every rate.** Never use a stored `k` |
| `n/k` | `n / k_essential` | raw rate. **Not a cross-gate comparison** |
| `V_ex` | extractable `T` states over **disjoint** factors: `CCZ`→2, `CS`→1, `T`→1; `null` if monomials overlap | the honest output count |
| `rho` | `n / V_ex` | `T`-equivalent rate |
| `gamma` | `log(n / k_essential) / log(d)` | the **distillation exponent**, lower better |
| `gamma_rho` | `log(n / V_ex) / log(d)` | **the one to compare across gate types** |
| `A_d` | harmful faults at the leading weight | the error prefactor — a first-class axis |
| `Abar_d` | per-output flips: `(1/k)·Σ_j #{faults flipping output j}` | **the cross-`k` prefactor comparator** |

### Why `gamma`

Driving output error to `ε` by concatenating blocks costs
`O(log^gamma(1/ε))` inputs per output. Lower `gamma` wins asymptotically.

### Why `k/n` is not a cross-gate comparison

A `CCZ` spends **three output wires** for what is worth 2 `T` states, so
counting wires flatters every `CCZ` circuit. The catalogue's apparent `d = 2`
leader `[[74,36,2]]` has `gamma = 1.0395` on wires and `gamma_rho = 1.6245` on
`T` states. The first number is a counting artefact; the second is the factory.

A `gamma` below 1 is not a discovery — it is a signal that monomials overlap and
`V_ex` is undefined. Two rows in the catalogue do this (`0.803841`, `0.928875`).
Check `gamma_rho` before believing any exponent.

### Why `gamma` alone is never enough

`gamma` describes the `ε → 0` limit, which needs infinitely many levels of
concatenation. **Nothing operates past about five.** At real operating points
`A_d` and the level count dominate.

The sharpest illustration lives inside this corpus: Gong–Pattison–Rall–Wills
(`arXiv:2608.09727`) give an `F_4` Reed–Solomon `(2k+2) CS → k CS` family at
`d = 2` whose exponent tends to **1 from above** — lower than anything here.
This project measured its prefactor at `A_2 ≈ n²/18`, and the consequence is
that **pure `T` still wins on actual cost at 7 of 8 operating points.**

> Quote `gamma` and `A_d` together, or you have not made a comparison.

### And `A_d/k` is not the cross-`k` comparator

`A_d` counts faults on the **block** ("at least one of the `k` outputs is
wrong"), and blocks differ in how many outputs one fault flips — in this corpus
from ~6.5 to ~80. Dividing a block count by `k` therefore compares two different
things. Use per-output flips `Abar_d`.

This is not theoretical: a "13× worse prefactor" claim here recomputed to near
parity under `Abar_d`, and a "10.5×" gap became 5.8×. **Every audited
comparison's direction survived; none of the multipliers did.**

## 5. Where the big factories come from

Almost every large factory here is a **punctured Reed–Muller** code. Take
`RM(r, m)`, delete a set `P` of `t` coordinates, and you get

```
n = 2^m - t          k = t - (something)      the game: raise t at fixed d
```

For the records, `RM(3,10)`: `N = 176` wires, `n = 1024 - t`. This matters
because the search problem becomes **"choose the puncture set"**, and the useful
reformulation is:

```
d   = min over nonzero c in RM(2r, m) of ( |c| - |supp(c) ∩ P| )
A_w = #{ c in RM(2r, m) : |c| - |supp(c) ∩ P| = w }
```

so distance is a property of the puncture set against the dual code. A point `v`
may be added to a `d ≥ D` set **iff `v` lies in no weight-`D` harmful fault** —
that is the growth rule every ladder search in this project uses.

## 6. The minimum you must be able to compute

Implement these five, or use `reference/verify_factory.py` which does:

1. `rows[q]` = bitmask over columns containing wire `q`
2. gate = odd-parity monomials of degree ≤ 3; contamination = any touching a check
3. `k_essential` = wires the gate touches; **spectators** = outputs it does not
4. rank over `F_2` of the output rows modulo the check span (**effective width**)
5. harmful-fault counts by weight

Weights 1–4 are cheap by meet-in-the-middle. **Weight 5 and up are expensive**
(`O(n^3)` and worse) and this is the single biggest practical constraint in the
whole problem — see `04_VERIFY.md` §3.
