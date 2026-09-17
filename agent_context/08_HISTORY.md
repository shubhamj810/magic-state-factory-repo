# 08 — The campaign record: what was tried, what held, what was retracted

Eight campaigns, roughly 2026-08 to 2026-09. This is the part a catalogue cannot
carry: **which routes were walked, and which claims died.**

Retractions are listed as prominently as results. That is deliberate — a claim
that was withdrawn is more useful to you than one that was never made, because
it tells you where the ice is thin.

---

## The arc in one paragraph

Campaigns 1–2 chased **rate** (`n/k`) and **smallest `n`**. Campaign 3 switched
to the **distillation exponent** `gamma`, which is what governs overhead as
target error → 0, and that reframing produced every subsequent record. Campaigns
4–6 industrialised the discipline (a written contract, a mandatory verifier, a
deduplicated master catalogue). Campaigns 7–8 pushed `gamma` at `n < 1000` and
moved it twice. Running through all of it: **the verification apparatus caught
more than the searches did.**

---

## 1. `ai_campaign` — first AI search, 17 iterations

Search over a slot ansatz. Produced 119 raw circuits, of which a subset survived
audit into the consolidated corpus.

**What it left behind:** the observation that stored `gate` fields cannot be
trusted — 24 of its records use a shorthand (`"T^5"`) that a verifier reads as a
single `T` on wire 5.

## 2. `frontier_campaign` — four cycles, any output state

Clifford equivalence handled in post-processing. 5,567 recorded negatives, ~174
audited circuits, 21 reports.

**Held.** Haah–Hastings §4.5 **reproduced in-house** — 11 factories rebuilt from
the paper's puncture lists with `A_d` matching exactly (324 / 495 / 3231 / 1514).
Four previously-open problems closed, including `nu(4) = 44` and `nu(5) = 47`
optimal at rank 7, and `maxT([[47,5,3]]) = 5`.

**Retracted.** The campaign's own `d = 3/4/5` "frontiers" were **never
frontiers** — every "frontier moved" claim before the closing audit was an
*internal best*. A published bound in the project's manuscript (`n(CCZ) ≥ 39`)
was **disproved**.

**Tooling bugs found:** lying `gate` fields; a concatenation tool with no
Haah–Hastings `d = 3` row and a frontier **1.75× too generous**; a T-count
routine overflowing above 6 qubits; a Clifford-class routine hanging above
`k ≈ 20`.

## 3. `gamma_campaign` — the reframing

Switched the objective to `gamma = log(n/k)/log(d)`.

**Held.** The exponent record moved twice: `1.124684` (`[[880,144,5]]`) →
`1.119677` (`[[879,145,5]]`) → `1.116552` (`[[902,122,6]]`), both distances
pinned, every `A_d` counted by two independently written tools. The `d = 6`
record was 11 orbits of the order-11 Singer subgroup of `GF(2^10)*` plus the
origin, found by an **exhaustive orbit-swap scan** after 16 randomised restarts
had never exceeded `t = 111`. Also the first `d = 8` puncture set of `RM(3,10)`
ever built. `d = 3` and `d = 4` on `RM(3,10)` **closed for `gamma`** by a
Hamming bound.

**The finding that reframed everything again.** A paper already sitting in the
repository (`arXiv:2608.09727`, Gong–Pattison–Rall–Wills) has a **lower exponent
than anything in this corpus** — an `F_4` Reed–Solomon `(2k+2) CS → k CS` family
at `d = 2` with `gamma → 1`. Its `A_2` was computed here for the first time at
`≈ n²/18`, and the consequence is that **pure `T` still wins on actual cost at 7
of 8 operating points.** Hence: *`gamma` alone is not a comparison.*

## 4. `ralph` — the autonomous loop, 10 rounds

Every round a fresh session with no carried context except what is on disk.
Attacked the `n = 127` width question. Results and refutations in
[`07_THEOREMS.md`](07_THEOREMS.md) §6.

**Worth noting as process:** the loop's memory is a single append-only journal,
and results flow through the normal ingest door rather than living in the loop's
own directory. That is what made ten rounds of a self-directed agent auditable.

## 5. `2026-08-31_48to128` — filling the empty window

**Held.** `[[112,16,3]]` `CCZ⁴·T⁴` at `rho` 9.333 — the **first `CCZ³`/`CCZ⁴`
factories at any `d ≥ 3`**. `CS³`, `CS²·T`, `CCZ²·T` cells filled. The
structural theorems in `07_THEOREMS.md` §3.

**Did not hold.** Pure `T` was **not** beaten: `[[127,23,3]]` at 5.522 is
saturated. And the campaign's entire `d = 4` framing was **retracted** when the
derived-baseline filter was applied to it.

**Seven bugs**, all caught by re-deriving from columns or by watching the
machine, none by reading code — enumerated in
[`06_TECHNIQUES.md`](06_TECHNIQUES.md) §6.

## 6. `2026-09-01_width_repairs` and `_check_trims` — not searches

Two campaigns that only cleaned up, and between them removed **44 rows** from the
consolidated corpus.

* **15 rows dropped** whose outputs were not independent modulo the check span —
  each a genuine factory wearing a wider label. 13 reduced to circuits already
  catalogued; the 2 that did not were re-derived and filed, so nothing that
  verifies was lost.
* **31 circuits trimmed** for carrying a redundant check wire (10 found
  upstream, then a sweep of all 821 rows found **21 more** — two of them filed
  *hours earlier* by a campaign that ran before the check existed).

**Why this matters more than it sounds.** These are the second and third of the
three width degeneracies, found months apart, each after the previous was
thought to be the whole story. See [`04_VERIFY.md`](04_VERIFY.md) §1.

## 7. `2026-09-01_39to127_broad` — populate the window

3 actors in parallel, 2 reviewers conferring, 3 rounds. **99 circuits kept**
after the reviewers retired 28 as dominated: 88 new `[[n,k,d]]`, 68 gate shapes
absent from the catalogue, 39 values of `n`.

**No rate record** — best `rho` 6.263 against pure `T`'s 5.522. Filling cells is
a real axis; it is not a frontier move, and the campaign said so.

## 8. `2026-09-04_gamma_sub1000` — the current record

Beat the bar: **`gamma 1.116552 → 1.111377`, `[[901,123,6]]`, pure `T^123`,
`A_6 = 2781` exact, `d = 6` pinned.**

The method matters: a **depth-4 ruin** of the old record, and the family's
**first non-symmetric record** — every previous one came from symmetry. The old
record was certified rigid at depths 1, 2 and 3 and gave way at depth 4, where
13,860 candidates held **exactly one** hit.

**An honest Pareto trade**, stated as such: `A_6` went 2475 → 2781, ~12% worse.

**Three certified negatives, which are worth as much:** punctured `RM(2,7)`
closed at `d ≥ 5` entirely; the dual-codeword LP is exactly 640 at `D = 6` so no
such bound can ever certify `t_max(6) < 640`; the 12-orbit Singer ILP is a
**plateau, not a timeout**.

## 9. `2026-09-04_gamma_deep` — halted at round 2

Five actors (three search, two zero-CPU theory), two reviewers. **Stopped
deliberately at the owner's request**, not by failure. Open fronts in
[`03_STATE.md`](03_STATE.md) §4.

Two things from it you should carry:

**Rounds 2–6 of the first attempt were void** — burned by a session limit,
rewound, and the limit detector fixed. Checkpoint every round.

**The final round's reviewer challenged nine points and won all nine**, against
an actor and an orchestrator who had both signed off. Among them: a standing
**false certificate** (`complete=true, evidence=CERTIFIED` on an enumeration
whose truth was 41 witnesses, written by pre-fix code); a **refuted lemma** that
had passed the previous round's review; and a claimed "completely empty band"
that a recount showed held 30 rows. All three were found by **re-reading the raw
artefacts**, not the summaries.

---

## What the whole record says

1. **Reformulation beat compute, every time.** Every record came from changing
   the search space, not from a bigger search.
2. **The verification apparatus out-produced the searches.** Nine defects in one
   week of campaigns; three separate width degeneracies; a disproved published
   bound; a whole rate table built on wrong invariants.
3. **Retract in place and keep the record.** Several results here are corrections
   of earlier results by the same project. That is the system working.
4. **A measured "law" is a conjecture.** Two structural laws that fit dozens of
   cases were later refuted; another failed by 40× on extrapolation.
5. **The reviewer is not a formality.** The strongest single round of quality
   control in this record was a fresh reviewer overturning nine accepted points.

---

## A note on raw logs

This pack deliberately ships **no raw logs**. They run to hundreds of thousands
of lines, most of which is job output, and an agent reading them inherits noise
rather than knowledge. Everything above is the distillate: what was tried, what
survived, what died and why.

If you have the full repository, the primary sources are each campaign's
`LOG.md` (per-round journal), `RESULTS.md` (theorems and verified circuits only)
and `logs/` (run transcripts) — and the master catalogue's `FINDINGS.md`, which
records what building it revealed about its own sources. If you have only this
pack and the catalogue, you have the conclusions and the means to re-derive
every one of them.

## 2026-09-14/15 — five campaigns against one bar, and the bar moved twice

The frontier moved by **import**, not by search: `[[896,128,6]]`
(`gamma 1.086033`, Wills) and then `[[860,128,6]]` (**1.063146**), both
supplied from outside and both verified here from their raw matrices before
anything was built on them. Every search campaign of these two days returned a
**negative** — and together the negatives explain the imports.

| campaign | asked | returned |
|---|---|---|
| `gamma_wills` | beat 1.086033 by extending Wills' puncture set | the fibre lemma: his 128 is **optimal**, not maximal. Lost its last rounds to a usage limit, so its headline theorem never reached its own `RESULTS.md` |
| `wills_downset_theory` | exploit the Wills paper properly | the paper's own explicit family crosses the bar only at `n ~ 3.8M`; the downset family caps at `1.502` |
| `wills_substrate130` | build `[[894,130,6]]` on a freer substrate | refuted: `t_max = 64` exactly, tight, witness attained — and the screening test that would have killed the lead in one second |
| `m8_m9_d6` | settle two open cells | a **floor** for the whole family at every `m <= 9` (see `07_THEOREMS.md`) |
| `alphabet_reduction` | reach the bar from outside the family | closed by arithmetic: blowup `~m^2/4` against payload `~m/2` |

**What the pattern is worth.** Three separate routes died the same way:
a cell survives every *optimistic* bound and then fails at realisability. AG
cells needed very special curves; 3,552 live cyclic cells had **zero**
certifiable by BCH or Hartmann–Tzeng; the substrate's 10 "favourable" dual
directions turned out to be concentrated in one 5-space, which tightened rather
than loosened the constraint. Optimistic-bound survivors are coordinates, not
codes.

**Three self-caught errors, all material, all recorded in place rather than
quietly fixed** — the habit is the transferable part:

* a campaign brief priced a route on **conflated constants** from the source
  paper (`s <= 41` where the truth was `14`; `s = 93` was a different map
  entirely). The campaign re-derived from the field and corrected its own brief.
* a cyclic closure was claimed while its scan **skipped** every outer length
  past the MDS arc bound — three skipped cells beat the bar. Retracted, repaired
  with four filters, re-closed.
* a theorem was stated using a **conjectured** `t_max` that a tool had silently
  fallen through to. Retracted with the mechanism named.

**One process failure worth not repeating.** Two campaigns merged into the
shared upstream catalogue concurrently with no write locking. Nothing was lost,
but one campaign's `PASS on 1748 rows` no longer covered the file by the time it
would have committed, and an authoritative claim string carried a rate computed
from the wrong circuit (`511/92` quoted as `508/92`). Both were caught before
the push. If campaigns are to merge autonomously, the slot ledger needs to cover
**writes**, not only CPU.
