# 03 — State of the art: records, what is closed, what is open

Every figure counted from the shipped `master_catalogue.jsonl` on **2026-09-11**,
not transcribed. Re-count before quoting: the corpus moves.

## 1. The corpus

| | |
|---|---|
| distinct verified factories | **837** |
| distances pinned exactly | 812 (18 are proven floors) |
| `A_d` known | 812 |
| rows failing verification | **0** |
| spectator outputs anywhere | **0** |
| non-independent outputs | **0** |
| redundant check wires | **0** |
| parameter tuples realised by >1 distinct circuit | **148** |

Distance spread: `d=2` 33, `d=3` 579, `d=4` 108, `d=5` 76, `d≥6` 29, `d≥7` 12.
518 rows are pure `T`; 486 of those have `n < 1000`.

## 2. The frontier, by distance

Best `gamma_rho` — the cross-gate-honest exponent — with ties broken by `A_d`,
which is the only honest way to break them:

| `d` | rows | pinned | best `gamma_rho` | circuit | `A_d` | id |
|---|---|---|---|---|---|---|
| 2 | 33 | 33 | 1.624491 | `[[74,36,2]]` | 2 701 | `dd9eb2e3` |
| 3 | 579 | 579 | 1.521610 | `[[862,162,3]]` | 6 391 | `1f41510c` |
| 4 | 108 | 108 | 1.249043 | `[[870,154,4]]` | 5 955 | `b1ad3be6` |
| 5 | 76 | 76 | **1.119677** | `[[879,145,5]]` | 3 152 | `79d0f1fd` |
| 6 | 29 | 8 | **1.111377** | `[[901,123,≥6]]` | — | `c76406c6` |
| 7 | 12 | 7 | 1.208643 | `[[935,89,≥7]]` | — | `dbacb8f2` |

> **THE CORPUS RECORD IS NO LONGER THE KNOWN FRONTIER (2026-09-15).** Two
> circuits verified in this repository beat it and are **not in the corpus**,
> so the table above — which `reference/check_claims.py` re-derives from the
> catalogue — is correct as a statement about the corpus and stale as a
> statement about the world:
>
> | circuit | `gamma` | status |
> |---|---|---|
> | `[[896,128,6]]` | 1.086033 | Wills, arXiv:2608.24000; `external_data/sub_1000_new_protocol.json` |
> | **`[[860,128,6]]`** | **1.063146** | **owner-supplied; `external_data/n860_k128_d6.json`** |
>
> Both are pure disjoint `T^128`, `d = 6` EXACT, re-derived here from their raw
> matrices (gate from column parities, factory condition, output independence,
> full weight-1..5 sweep with a witness at 6). **Quote `1.063146` as the bar.**
> `[[860,128,6]]` is deletion-maximal at depth 1 — all 860 single-column
> deletions tested, none preserves gate + factory + width — and is
> **triorthogonal, not 8-divisible** (check rows `0` or `6` mod 8) with
> `n != 2^m - k`, so it lies **outside the punctured-monomial family** that
> §3's floor governs. That is exactly why it beats the floor.

**The record is `[[901,123,6]]`, `gamma = 1.111377`, pure `T^123`.** Found by a
**depth-4 ruin** of the previous record `[[902,122,6]]` — delete 4 punctures,
add back 5 — and notable for being the family's **first non-symmetric record**;
every earlier one came from Singer-orbit symmetry.

Three things about it you must carry:

* It is a **Pareto trade, not a clean win**: `gamma` improved `1.116552 →
  1.111377` while `A_6` went `2475 → 2781`, ~12% worse.
* The catalogue prints it as a **floor** `≥6` with `A_d` unknown — see §5.
* At `d = 5`, **four distinct circuits tie** at `gamma_rho = 1.119677` and are
  separated only by `A_5` (3152, 3177, 3239, 3401). The row above is the best of
  them. This is rule 7 in miniature.

### Other landmarks

* **`[[512,39,≥7]]` = `CCZ^13`** — the only certified `d = 8`-class factory,
  39.385 `T` per `CCZ`. It beats **both** derived baselines (a published native
  `512 T → 10 CCZ` at 51.200, and Jones catalysis over pure `T` at 59.015), and
  is the first object at `d ≥ 3` here to survive the derived-baseline filter.
  `d ≥ 7` is enumerated; **`d = 8` is ARGUED, not enumerated.**
* **`[[127,23,3]]`**, pure `T^23`, rate 5.5217 — built on a Gabidulin/MRD
  scaffold. Widths `k ≥ 12` had never been reached at any `n` before it.
* **`[[8,3,2]]`** is the smallest non-Clifford factory that exists, PROVEN by
  exhaustive enumeration (6720 circuits at `n = 8`, all `[[8,3,2]]`), and its
  orbit is necessarily `CCZ`. The whole `d = 2` ladder is closed and optimal:
  `CCZ` at 8, `CS` at 12, `T` at 14. Smallest at `d ≥ 3` is `n = 15`.

### `nu(m)` — smallest known `n` for pure `T^m` at `d = 3`

`15, 28, 35, 44, 47, 55, 55, 56, 63, 63, 63, 76, 79, 88, 91, 100, 103, 109, …`
reaching `nu(23) ≤ 127`.

**Evidence is mixed and the mix matters.** `nu(1)`, `nu(2)` proven optimal;
`nu(3)` proven given the complete `n ≤ 38` classification; `nu(4)`, `nu(5)`
optimal **at check rank ≤ 7 only**; everything above is **best known**, and
probably short by 2 or more — the beams that produced the wide rows all stop at
width 9 on the `n = 63` simplex where width 11 provably exists.

## 3. Closed by theorem — do not re-derive these

* **`d = 3` and `d = 4` on `RM(3,10)` are closed for `gamma`.** A Hamming bound
  caps the puncture-set size (floors 1.495 and 1.185). Proven, derived
  independently three times. *Scope: that parent, those distances only.*
* **All punctured `RM(2,m)` at `d ≥ 5`** — flat-cap lemma. So within punctured
  RM, the `n < 1000` window is **`RM(3,10)` only**; a pure-`T` win there needs
  `RM(3,10)` or a non-RM base.
* **Dual-codeword LP / cutting planes can never certify `t_max(6) < 640`** — the
  LP value is exactly 640. A whole proof technique is ruled out.
* **`n ∈ {17..22, 25, 26}` admits no `d = 3` factory at any rank** (Kasami–Tokura:
  the available weights below 32 are `{16, 24, 28, 30}`).
* **`CCZ³`/`CCZ⁴` impossible in the `r = 6` quadratic family** (590/590 exhausted).
* **The 12-orbit symmetric CP-SAT at `d = 6` is a measured plateau**
  (`PROVEN_UB` 633 vs 131 needed) — **UNDECIDED, not a timeout.** Do not
  relaunch it without a new idea.
* **A published bound in this project's own manuscript is FALSE**: `n(CCZ) ≥ 39`
  is disproved by an explicit witness at `n = 36`.


### Added 2026-09-15 — four campaigns, and a floor for a whole family

* **`gamma = log7/log6 = 1.086033` is a HARD FLOOR for 8-divisible monomial
  parents at `d = 6`, every `m <= 9`.** The cap `t <= 2^(m-3)` is *attained*
  exactly at that value, so the family can **tie** Wills' exponent and never
  beat it. Complete in `mu` (`mu<=2` gives `d<=3`; `mu>=4` impossible at
  `m<=9` by Ward), and the caps are witnessed: `[[248,8,6]]` and
  `[[496,16,6]]`, both with `n/t = 31` exactly.
  *Scope: does **NOT** close `m = 10` — a surviving parent exists at `dim 138`.*
  (`campaigns/2026-09-15_m8_m9_d6`, R1–R7.)
* **Wills' 128 punctures are OPTIMAL on his parent at `d = 6`, not merely
  maximal** — the fibre lemma: each of the `2^(m-3)` light fibres holds at most
  one puncture. *Scope: that parent only, not all `m = 10` parents.*
  **This theorem is NOT in its campaign's `RESULTS.md`** — that run lost its
  last rounds to a usage limit before the paste. It lives in
  `campaigns/2026-09-14_gamma_wills/work/actor-1/for_RESULTS.md`.
* **The downset-puncture family tops out at `gamma = 1.502` at `n <= 1000`**
  (`[[959,65,6]]`); exhaustive over the finite window, `m <= 10` forced by
  `n >= 2^(m-1)`. The bar's own punctures are a downset under **0 of 1024**
  relabellings. (`campaigns/2026-09-14_wills_downset_theory`.)
* **Extension-field alphabet reduction cannot reach the bar at `n <= 1000`.**
  The blowup costs `~m^2/4` (`s_min(m) = floor(m^2/4)+m-1`, the Waring rank of
  `Theta_m` over `F_2`) while `k` buys only `~m/2`: raising the extension
  degree is a losing trade. Best reachable `gamma = 1.439227`
  (`[[756,32,9]]`); largest `k` anywhere on the route is **64** where the bar
  needs **147**. Not specific to Reed–Solomon — the scan took the outer dual
  distance at its Singleton maximum, so it bounds every outer code with
  ordinary Schur growth. *Scope: unconditional for `m <= 6`; `m >= 7` rests on
  the `s_min` conjecture.* (`campaigns/2026-09-15_alphabet_reduction`, T6/T6b.)

## 4. Open, with the best current handle on each

From the campaign halted at round 2 on 2026-09-05. The bar to beat is
`gamma = 1.111377` at `n < 1000`, pure `T`.

| front | target | state |
|---|---|---|
| `d = 6` depth ladder | `t = 124` → `gamma` 1.1062 | **best open cell.** Depth-5 gain-1 at `t=124` can *never* close by refutation (proven feasible), so it must be searched. A ~119-candidate forced sub-family was priced at ~5 min and never run |
| `d = 5`, `t = 147` | `gamma` 1.1098 | `t = 146` and `t = 147` both **unreachable at depth ≤ 3** — 509 priced core-hours decided in 18 minutes by an algorithmic reduction. Needs a different mechanism |
| `d = 7` ladder/lift | `t' = 106` → 1.1094 | the pair sub-front is **RETIRED with certificates on both sides**; the 17-set `t=122` family lift sweep is the whole remaining front |
| `d = 8` closure | — | its flat system `\|A ∩ P\| ≤ 8` is the tightest; closing it would retire a front |
| rank-deficient / non-RM bases | new space | the only doors the `RM(2,7)` closure leaves open. Extra punctures buy down `n` at fixed `k` **if purity survives** — undetermined |

**Two theory results in that campaign are ARGUED, not certified**, pending a
proof repair at one named step (an "occupied-cell" step whose supporting lemma
was refuted by explicit counterexample, though the theorem's conclusion survived
on the counterexample itself). Treat anything depending on them accordingly.

## 5. Where this corpus disagrees with itself

Written down rather than smoothed over, because you will hit them.

**The record's distance.** The campaign claims `[[901,123,6]]` is `d = 6`
**PINNED** with `A_6 = 2781` **exact**, verified by its own tools. The master
catalogue row says `d_display: ">= 6"`, `d_exact: null`, `A_d: null`,
`gamma_evidence: "upper bound at the proven floor"` — because the catalogue swept
weights 1–5 clean itself and **skipped weight 6** as out of reach at `n = 901`,
and the campaign's count was never propagated into the row.

Neither is wrong; they are different evidence classes. **The bar `gamma =
1.111377` stands either way** — as an exact value if the campaign's count holds,
as an upper bound if you only trust the catalogue. If you beat it, say which one
you beat.

**Older documents carry stale counts.** A root-level orientation file quotes
"79 parameter tuples realised more than once"; that figure describes one
sub-corpus and the merged number is **148**. Count from the shipped data.

## 6. What has been tried and did not work

Worth as much as the successes, and much cheaper to inherit:

* **Symmetry-first search has plateaued.** 16 randomised restarts never exceeded
  `t = 111`; the exhaustive orbit-swap scan that found the `d = 6` record was the
  end of that method's reach. The current record is the first **non**-symmetric one.
* **Covering-MIP solver path: measured dead three times** (0 of 41 known-feasible
  points at 240 s, 150 s and 120 s). Killed, not to be relaunched.
* **Randomised beams stop at width 9** on the `n = 63` simplex where width 11
  provably exists — weight-ranked, lookahead-ranked and stratified all stop in
  the same place. Something structural, not a tuning problem.
* **The per-puncture `A_d` doubling rule does not extrapolate**: predicted a 123×
  prefactor penalty where the observed one was 3.05×.

### Added 2026-09-15 — routes priced and abandoned, with the numbers

* **Do not implement an asymptotically-good construction at `n <= 1000`
  without pricing its crossover first.** Twice now the honest answer was
  "real result, wrong scale": Wills' own explicit family crosses
  `gamma = 1.086033` only at **`m = 22`, `n ~ 3.8 million`**; San-José's AG
  family crosses `1.063146` only at **`N ~ 15,000–108,000`** (at `N = 1000`
  it yields `K ~ 17`, `d ~ 3`, `gamma ~ 3.7`). Both were priced in minutes
  and saved a campaign each.
* **"Few top dual directions" is the WRONG objective for choosing a parent.**
  A substrate with only 10 (vs the Wills parent's 22) was refuted: its 10 all
  lived inside one 5-dimensional subspace, and that *concentration* collapses
  "at most 2 per 3-flat" into "at most 2 per 32-point block", capping
  `t <= 64` where 130 was needed. **The right test is whether the
  minimum-weight dual layer SPANS** — `dim span(core supports)` must be `m`.
  One second per parent:
  `campaigns/2026-09-15_wills_substrate130/tools/cluster.py`. It reports no cap
  on the Wills parent (where `t = 128` *is* achievable) and the cap on the
  substrate, so it discriminates rather than killing everything.
* **Optimistic bounds produce cells, not codes — and the cells keep dying at
  realisability.** Across two independent slices: AG cells survived every
  degree/point bound and then required very special curves (one below the
  Clifford ceiling); and of **3,552** live cyclic cells, **zero** were
  certifiable by BCH *or* Hartmann–Tzeng. Treat a surviving cell as a
  coordinate, never as a `gamma`.
* **`gamma < 1` is exactly `n < k*d`, and the required rate falls like `1/d`.**
  At `n = 1000`: `d=6` needs `k/n >= 0.167`, `d=8` needs `0.126`, `d=16` needs
  only `0.063`. The current bar sits at `0.149` — 12% short of the `d = 6`
  threshold — while `k/n = 0.068` is *already achieved* at `d = 8` and would
  clear `d = 16` outright. **`d >= 10` at `n <= 1000` has never been searched
  here.** Caveat that must travel with this: the known `gamma < 1` objects
  (`[[512,84,8]]`, `gamma 0.869`) have `V_ex` **null** — overlapping monomials,
  no extractable `T`. A `gamma < 1` claim without a real `V_ex` is not a result.
