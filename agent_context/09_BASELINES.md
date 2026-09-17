# 09 — Prior art and derived baselines: what you must beat

A result that is not scored against the cheapest alternative route to the same
output is not a result. This file is that alternative.

## 1. The published frontier (Haah & Hastings)

Haah & Hastings, *Quantum* **2**, 71 (2018), **arXiv:1709.02832 §4.5** —
punctured Reed–Muller triorthogonal factories, pure `T` output. These rows were
**verified directly from the arXiv source** and reproduced in-house: 11
factories rebuilt from the paper's puncture lists with `A_d` matching exactly.

| `d` | published | `A_d` | `n/k` |
|---|---|---|---|
| 3 | `[[109,19,3]]` | 324 | 5.73 |
| 3 | `[[863,161,3]]` | 3 231 | **5.36** |
| 4 | `[[116,12,4]]` | 495 | 9.67 |
| 4 | `[[872,152,4]]` | 1 514 | **5.74** |
| 5 | `[[887,137,5]]` | 709 | 6.47 |
| 6 | `[[912,112,6]]` | 1 191 † | 8.14 |
| 7 | `[[937,87,7]]` | — | 10.77 |

**† `A_6 = 1191` is the PUBLISHED value and is not re-counted in this corpus** —
weight 6 is out of sweep reach at `n = 912`, so the catalogue row carries
`A_d: null`. The `d = 3, 4, 5` prefactors above *were* independently reproduced
here (324 / 495 / 3231 / 1514 / 709, all matching). Treat the `d = 6` and
`d = 7` prefactors as the paper's claims, not as verified numbers.

**State the size any rate claim holds at.** The 5.36 needs `n = 863`; a result
at `n ≈ 255` is not competing with the same object.

Hastings–Haah **arXiv:1709.03543** (asymptotic, `gamma → 0`) is a *different
regime* and gives nothing at `n ≈ 255`. Do not cite it as a bound here.

## 2. The lower-exponent family you must know about

**Gong, Pattison, Rall, Wills, arXiv:2608.09727** — an `F_4` Reed–Solomon
`(2k+2) CS → k CS` family at `d = 2` whose exponent **tends to 1 from above**,
lower than anything in this corpus.

This project measured its prefactor for the first time: **`A_2 ≈ n²/18`**. The
consequence, and the reason `gamma` alone is never a comparison:

> **Pure `T` still wins on actual cost at 7 of 8 operating points.**

A lower asymptotic exponent does not imply a better factory at any size you will
ever build.

## 3. The conversion toolkit — nothing outside this list may be assumed

| identity | catalytic? | source |
|---|---|---|
| `CCZ → 2T` | **yes**, `T` catalyst returned | Gidney & Fowler, *Quantum* **3**, 135 (2019), arXiv:1812.01238 |
| `CS → T` | **yes**, `T` catalyst returned | Beverland, Campbell, Howard, Kliuchnikov, arXiv:1904.01124 Fig. 2 |
| `4T → CCZ` | no | Jones, *PRA* **87**, 022328 (2013), arXiv:1212.5069 |
| `3T → CS` | no | Howard & Campbell, arXiv:1609.07488 |
| `2CS → CCZ` | no | Beverland et al.; arXiv:2608.09727 |

Three currencies, never mixed:

| | meaning | `T` | `CS` | `CCZ` |
|---|---|---|---|---|
| `V_ex` | `T` states **extractable from** the output | 1 | 1 | **2** |
| `C_syn` | `T` states **needed to synthesise** it | 1 | 3 | 4 |
| `tau` | ancilla-free minimal T-count of the *unitary* | 1 | 3 | 7 |

`rho = n / V_ex` is the ranking metric. **`tau` is not a class label** — see
[`06_TECHNIQUES.md`](06_TECHNIQUES.md) §7.

## 4. The derived-baseline gate — apply it to every result

**A factory can be built out of a cheaper factory.** Comparing only against
other *native* factories flatters your result.

**Concatenation.** With `rho = n/V_ex`, stacking `L` levels gives `rho^L` at
distance `d^L`. Note this reaches only **powers of the base distance**: a `d = 2`
factory gives `d = 2, 4, 8` and **never** `d = 3`.

The row that matters most, and the one an early campaign missed entirely:

| level | from `[[8,3,2]]` `CCZ` (`rho = 4`) | distance | one `CCZ` costs |
|---|---|---|---|
| L=1 | `rho = 4` | 2 | **8** `T` |
| L=2 | `rho = 16` | 4 | **32** `T` — i.e. `[[32,2,4]]` with `T²` output |
| L=3 | `rho = 64` | 8 | **128** `T` |

**Catalysis.** Since `4T → CCZ`, a `CCZ` factory at distance `d` earns its keep
only if `n < 4 · rho_T(d)` — about **23** at `d = 3`. That is brutal, and it is
why a large set of `CCZ`-class circuits fill cells without beating anything.
Their value is *smallest `n` for a class*, which is a real axis — but it is not
a rate record, and must not be called one.

## 5. What surviving this filter looks like

One object at `d ≥ 3` in this corpus survives the derived-baseline gate:

**`[[512,39,≥7]]` = `CCZ^13`** — 13 disjoint `CCZ`s on 39 outputs from 512
columns, **39.385 `T` per `CCZ`**, beating *both* alternatives:

| route | `T` per `CCZ` |
|---|---|
| **this factory** | **39.385** |
| published native `512 T → 10 CCZ` | 51.200 |
| Jones `4T → CCZ` over pure-`T` `[[959,65,8]]` | 59.015 |

Note what is *not* claimed: its exponent is **not** a record and is not recorded
as one. The win is on cost per `CCZ` against the derived alternatives, **at one
operating point**.

And watch the exponent carefully, because it is a worked example of the floor
rule: its `d = 8` is **ARGUED, not enumerated** (faults lie in `RM(6,9)`, minimum
weight 8, plus an explicit weight-8 witness), while `d ≥ 7` *is* enumerated. So
`gamma_rho` is **1.531534 at the proven floor `d ≥ 7`**, and only `1.433187` if
you grant the argued `d = 8`. The catalogue quotes the floor. If you see the
smaller number quoted anywhere, it is resting on the argued distance.

That is the shape of an honest claim: name the axis, name the operating point,
name the evidence class, and say what you did not prove.

## 6. A caution about beating a published number

Two failure modes, both real here:

**Comparing to a mis-transcribed bar.** A tool's internal frontier had no
Haah–Hastings `d = 3` row at all and was **1.75× too generous**. Everything
scored against it looked better than it was. **Re-derive the bar from the
source**, do not read it from a file in your own project.

**Beating the rate and losing the prefactor.** This project's `[[119,17,3]]`
`T^17` matched `[[112,16,3]]` `T^16` at *exactly* the same rate 7.000 and lost
badly on the prefactor: `A_3/k` of **63.0 against 6.0**, a 10.5× gap. Quote the
pair, always.

**But then read the correction, which is the better lesson.** The campaign
later established that **`A_d/k` is the wrong cross-`k` comparator**: it divides
a *block* fault count by `k`, and blocks differ in how many outputs a single
harmful fault flips. On per-output flips (`Abar_d`) the same gap is **5.8×, not
10.5×**. Every audited comparison's *direction* survived that correction; **the
multipliers did not.** Use `Abar_d` for cross-`k` prefactor language.

And note what that one cell holds. At rate exactly 7.000 and `d = 3` there are
**five** distinct catalogued circuits:

| circuit | gate | `A_3/k` |
|---|---|---|
| `[[112,16,3]]` | `T^16` | **4.0** |
| `[[112,16,3]]` | `T^16` | 4.6 |
| `[[112,16,3]]` | `T^16` | 6.0 |
| `[[119,17,3]]` | `T^17` | 63.0 |
| `[[112,16,3]]` | `T^4·CCZ^4` | 112.0 |

A **16× spread among the pure-`T` four alone**, at one identical rate. (The
fifth is a different gate type, so comparing it here on `A_3/k` would be the very
cross-gate error §3 warns about — it is listed to show the cell is not
homogeneous, not to rank it.)

`[[n,k,d]]` does not identify a factory. Neither does the rate.
