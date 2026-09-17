# 04 — The verification contract

A candidate is a hypothesis until a tool that shares no code with the search
re-derives it from the columns. This file is what that tool must check.

`reference/verify_factory.py` implements all of it in one stdlib file.

```bash
python3 reference/verify_factory.py --selftest      # 5 cases, 3 of them real
python3 reference/verify_factory.py candidate.json
```

## 1. The eight checks

| # | check | failing means |
|---|---|---|
| 1 | **no check contamination** — no odd degree-≤3 monomial touches a wire `≥ k` | it is **not a factory** |
| 2 | **gate** recovered from column parities matches the target | you built something else |
| 3 | **no spectator outputs** — every output `< k` is touched by the gate | `k` is padded; every rate is inflated |
| 4 | **outputs independent mod the check span** — rank of output rows modulo the check span `== k` | `k` counts one logical output twice |
| 5 | **no redundant check wires** — check rows have full rank `N - k` | dead postselection; `N` overstated |
| 6 | **distance** — every weight below `d` enumerated and empty | the distance claim is unsupported |
| 7 | **`A_d`** counted at the leading weight, and said to be *at* that weight | the prefactor is meaningless or wrong |
| 8 | **`V_ex`** computed, or explicitly `null` | no cross-gate claim is permitted |

Checks 3, 4 and 5 are three **different** degeneracies. They were found in that
order, months apart, each after the previous was thought to be the whole story:

```
3. spectator output       an output the gate never touches
4. dependent output       one output equals another MODULO THE CHECK SPAN
5. redundant check        a check inside the span of the OTHER CHECKS
```

All three are rank conditions on the frame. **A single rank check over the full
frame catches all three**; checking only one is how this corpus shipped
defective rows three separate times. `fixtures/bad_outputs_not_independent.json`
is a real row that carried #4 and #5 simultaneously and was catalogued as
correct for months.

## 2. What each degeneracy costs

| defect | effect | fix |
|---|---|---|
| spectator | `k` inflated, `gamma` flattered | delete the wire, or demote it to a check |
| dependent output | `k` counts a logical output twice | reduce to the honest width — often a circuit already catalogued |
| redundant check | `N` overstated, acceptance probability wasted, `n`/`k`/gate/`d` all unchanged | delete dependent wires one at a time until independent |

**Demote or delete?** Demoting a spectator to a check kills every harmful fault
whose output support *contains* that wire; deleting it kills only those whose
support is *exactly* that wire. Demotion therefore dominates on distance — but it
costs acceptance probability, so it has to earn its place. The rule that
follows: **demote when it strictly increases the distance, otherwise delete.**
(Across 50 real repairs in this corpus, deletion always matched demotion, so
nothing was demoted.)

Deletion is **gate-preserving**, and this is a theorem, not a hope: the parity of
a monomial `m` is the count of columns containing all of `m`; if `q ∉ m`,
dropping `q` from every column cannot change which columns contain `m`. Assert
it anyway — compare the relabelled monomial set, do not just check the width.

## 3. The cost wall, and the vacuous PASS

Exact fault counting by weight:

| weight | method | cost |
|---|---|---|
| 1–4 | meet-in-the-middle | milliseconds, even at `n ≈ 1000` |
| 5 | 2+3 split | `O(n³)` — seconds at `n ≤ 300`, **hours at `n ≈ 900`** |
| 6 | 3+3 split | `O(n³)` — ~3 s at `n = 256`, out of reach at `n ≈ 900` |
| 7 | 3+3+1 XOR-join | ~60 s at `n = 255` |

**This is the single biggest practical constraint in the problem.** It is why
the record's distance is a floor in the catalogue and pinned in the campaign.

> **The vacuous PASS.** This project's own reference verifier searches faults
> only to weight 4. A `d ≥ 6` PASS from it is therefore **VACUOUS** — it proves
> `d ≥ 5` and nothing more. A verifier that silently stops looking is worse than
> one that refuses. `reference/verify_factory.py` reports a floor past weight 4
> and says so in the output rather than upgrading it.

If you need weight 5+, use a tool that implements it and **name the tool beside
the number.**

## 4. Evidence classes — label every number

Three states, never two:

```
FOUND        a harmful fault exists at this weight (count it)
CLEAN        swept exhaustively, none exists
NEVER LOOKED absent from the table
```

Collapsing the last two into "zero" is how a distance claim gets invented out of
silence. Then:

| label | meaning |
|---|---|
| `d_exact` | clean sweep below, **nonzero count at** it. The true distance |
| `d_floor` | nothing found below; the weight itself never counted. **A floor** |
| `d_claimed` | what a source asserted. **A claim, never evidence** |
| `CERTIFIED` | completed deterministic walk, or an algebraic proof |
| `ARGUED` | reasoned but not enumerated — say which step is unproven |
| `not found in N nodes` | a randomised miss. **Not** "does not exist" |

A `gamma` quoted at a floor is an **upper bound valid whatever the true distance
is** — because `gamma = log(n/k)/log(d)` falls as `d` rises. That is a useful,
honest number; it is not an achievement. Label it.

## 5. Reading a catalogue row without being misled

* `k_essential`, never `k`, is the denominator of every rate.
* `≥d` in a distance means **floor**. Its `gamma` is an upper bound.
* `A_d = —` means **not counted**. It never means zero.
* `gamma_rho = —` means monomials overlap, `V_ex` is undefined, and **no
  cross-gate comparison is available for that row**.
* `gate_matches_stored: false` is **common and expected** — the stored gate was
  wrong, the derived one is right.
* Join on the column-set hash `id`. Where you only have parameters, use
  `(n, k_essential, d, gate)`. **Never join on `(n, k, d)`** — 148 tuples here
  are realised by more than one distinct circuit.

## 6. Two habits worth stealing

**Compute it twice, with two implementations that share no code.** The master
catalogue re-verifies every row with a second, independent fault counter. Every
real error in this project was caught this way and essentially none by review.

**Check that your pipeline is a fixed point.** Run it twice on its own output
and require that nothing moves. A real bug here survived a full single-pass
verification: one stage re-quoted `A_d` at the *rate* distance, and the next
stage read that field as the count at the *claimed* distance — so records
correctly moved from `d = 5` to `d = 7` silently reverted on the second run.
The first pass was correct; only the second was wrong. A single-pass check can
never see that.

The underlying fix is worth generalising: **make state self-describing.** The
fault table is keyed *by weight* and cannot be misread at a different one; a
bare `A_d` field can. Prefer the structure that carries its own meaning.
