# 02 — The rules, and the failure that produced each one

None of these are style preferences. Each is here because this project got it
wrong first, published or nearly published the consequence, and had to retract.
They are ordered by how much damage the violation does.

---

## 1. Trust `columns`. Nothing else.

Recompute the gate, `n`, `N`, `k_essential`, the distance, `V_ex`, `rho`,
`gamma` and `A_d` from the column set every time.

> **The failure.** Stored `gate` fields are wrong in **62+ records** here.
> `findings_tm.jsonl` writes `"T^5"`, which the reference verifier parses as a
> single `T` on wire 5. Twenty-five rows of an exhaustive catalogue store an
> `S_k` relabelling of what their columns realise. Any pipeline handing `gate`
> and `columns` to a verifier together breaks on these.

`k` is the one unavoidable exception: the output/check split is a **choice**,
not derivable from the columns. Take `k` from the source, then derive
`k_essential` and compute every rate on that.

## 2. Nothing is a result until a verifier re-derives it from the columns

The search that produced a circuit is not evidence that the circuit is a
factory. A separate tool, sharing no code with the search, must re-derive it.

> **The failure.** Nine defects across one week of campaigns died against the
> verifier — **one of them inside the verifier itself.** A search reporting
> success is a hypothesis.

## 3. Never weaken or delete a check to make something pass

If a candidate fails, the candidate is wrong until proven otherwise. Fix the
circuit, not the verifier.

> **The failure.** Not a hypothetical: a verifier check was once phrased so
> loosely it reported "N drops to 2" on a circuit whose `N` actually drops to 10.
> The fix made the check *stricter* (report the rank **deficiency**, not the
> count of dependent wires) — and it kept finding real defects afterwards.

## 4. `k/n` is not a cross-gate comparison — score on `V_ex`

Quote `V_ex` beside every rate, or write `null` and make no cross-gate claim.

> **The failure.** An entire campaign's `d = 4` framing was retracted when the
> derived-baseline filter was applied to it. A `CCZ` spends three output wires
> per gate; wire-counting flattered every `CCZ` row in the corpus.

## 5. A randomised miss proves nothing

Log `"not found in N nodes"` or `"CUT"`. **Never** `"does not exist"`.
`"EXHAUSTED"` / `"impossible"` is earned only by a completed deterministic walk
or an algebraic argument — and then you must say exactly *what* was exhausted,
for which parent and which gate.

> **The failure.** `complete=True` and `"budget exhausted"` are different facts.
> Blurring them manufactures a theorem that gets cited later. One certificate in
> this corpus was written `complete=true, evidence=CERTIFIED` by pre-fix code
> asserting an empty enumeration where the truth was **41 witnesses**; it stood
> as a false certificate until a reviewer re-read the raw log.

## 6. Score against DERIVED baselines, not just other native factories

A factory can be built from a cheaper factory by **catalysis and
concatenation**. Every result carries two numbers: its cost, and the cost of the
cheapest alternative route to the same output.

> **The failure.** A tool's internal frontier had no Haah–Hastings `d = 3` row
> and was **1.75× too generous**, making beaten baselines look beaten when they
> were not.

## 7. `A_d` is an axis, not a footnote

A rate win with a worse prefactor is a **Pareto trade**, and must be reported as
one.

> **The failure.** This project's own `[[119,17,3]]` matched a published rate
> exactly and lost **10.5×** on `A_3/k`. And the current `gamma` record is a
> trade, not a win: `[[902,122,6]] → [[901,123,6]]` improves the exponent
> `1.116552 → 1.111377` while `A_6` goes `2475 → 2781`, ~12% worse. State both.

## 8. An unknown is not a zero

A weight absent from a fault table was **never counted**, which is never the
same as counted-and-empty. Keep `"swept and clean"`, `"never looked"` and
`"found"` as three distinct states.

> **The failure.** A certification pass once read "`A_d` unknown" as "`A_d = 0`"
> and concluded the distance *exceeded* its claim on records where nothing had
> been measured — inventing floors out of silence. Separately, an `A_d` was
> silently computed at the wrong weight and reported as the prefactor.

## 9. Write every verified circuit to disk the moment it passes, and log as you go

Agents die mid-run. One session's work survived three usage-limit kills only
because of this; another campaign lost **rounds 2–6 entirely** to a session
limit and had to rewind.

---

## The habit underneath all nine

> **Nearly every real error in this project was caught by re-deriving a claim
> independently, not by reviewing it.**

A false published bound (`n(CCZ) ≥ 39`, disproved by a witness at `n = 36`), a
dedup that kept a mislabelled duplicate, an `A_d` computed at the wrong
distance, a structural "law" that failed by 40× when extrapolated — none were
caught by reading. All were caught by recomputation.

Budget for it. When a number matters, compute it twice with two implementations
that share no code. This corpus does exactly that: its master catalogue
re-verifies every row with a **second, independent fault counter** that shares
nothing with the first.
