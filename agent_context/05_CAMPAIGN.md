# 05 — Running a campaign, and contributing results back

The structure below is not bureaucracy; it is what made the results in
`03_STATE.md` reproducible and auditable after the agents that produced them
were gone.

## 1. Campaign layout

```
campaigns/<YYYY-MM-DD>_<slug>/
  TASK.md      the brief an agent loop re-reads every round: goal, bar, routes,
               rules, and a machine-checkable DEFINITION OF DONE
  README.md    the campaign for a human: headline table, the ideas, the map
  RESULTS.md   theorems and verified circuits ONLY — no narrative
  LOG.md       per round: what ran, what verified, what was ruled out and how,
               what was left running (with PIDs)
  tools/       verify.py is mandatory; the rest is the campaign's own
  found/       verified circuits. NOTHING enters without passing tools/verify.py
  reports/     generated tables
  logs/        every run transcript. Kept, not ignored
  archive/     tools whose front closed, with the proof that it closed
```

`found/` is the door into the catalogue. A file holds one object or a list;
each needs `columns` (one list of wire indices per rotation, wires `0..k-1`
outputs) and `k`. `d`, `gate` and `provenance` are carried as **claims** and
recomputed.

**Name a file for what it is.** A control, a parent, or a circuit outside the
window is not a result:

```
n48_ccz1_VALIDATION_not_a_record.json
n127_ccz4_parent.json
n128_ccz5_OUTSIDE_window.json
```

They are valid factories and the catalogue takes them — but nobody should be
able to quote one as a headline by mistake.

## 2. Write the brief so it can be failed

A `TASK.md` needs a **bar that is a number** and a definition of done a reviewer
can check mechanically. "Improve the frontier" is not a bar. `gamma < 1.111377`
at `n < 1000` for pure `T^k` is.

**Verify the bar by running the verifier, not by quoting a file.** Every
campaign here opens by re-deriving its own starting point — one of them found
stale claims in older files while doing so, and another found the previous
record's distance was labelled inconsistently between a table and its own prose
two paragraphs later.

## 3. Price the job before running it

The discipline that produced the best results: **decide the job arithmetically
before spending CPU on it.**

> A depth-4 census on disk gave the freed-point histogram `{6: 825, 7: 66, 8: 11}`.
> A double gain needs `|freed| ≥ 6`, contributing `C(|freed|, 6)` sets each:
> `825·1 + 66·7 + 11·28 = 1595` candidates. None Singer-invariant, so
> `1595 / 11 = 145` orbit representatives × 2.5 s measured = **6–7 minutes**,
> not the 9.6 core-hours the naive count suggested.

A measured price is itself a deliverable. One route in the halted campaign was
killed by pricing alone: 509 priced core-hours were decided in 18 minutes by an
algorithmic reduction, a ~1560× saving, and the answer was "unreachable".

## 4. Two-agent flow

An **actor** searches; a **fresh reviewer** reads the work and decides whether
it is done. This is what produced every result here. The reviewer re-runs the
verifier rather than reading its output, and re-derives disputed numbers.

It works: in the last campaign's final round, **all nine** of a reviewer's
challenges resolved in the reviewer's favour — including a standing false
certificate and a refuted lemma that had passed the previous round's review.

## 5. Machine discipline

If you are running on someone's working machine:

* at most **2 concurrent search jobs**, always niced
* check load before launching; nothing if the 1-minute load is above 4
* kill orphans (`PPID 1`) before starting — searches from dead agents survive
  and keep running
* record every PID in `LOG.md`
* **write every verified circuit to disk the moment it passes.** Agents die
  mid-run; one campaign lost rounds 2–6 to a session limit and had to rewind

## 6. Documentation discipline

* Every round appends to `LOG.md`.
* `RESULTS.md` holds theorems and verified circuits only. **Retract in place**
  when something turns out wrong, and say so — do not delete it.
* A reader must be able to reproduce the headline from the README alone, and
  **the reproduce block must actually run.** One did not, once, because it
  pointed at the wrong parent.
* Any figure describing the corpus must be **counted, not typed**. A caveat in
  this project once asserted a count that described only a sub-corpus; the
  merged number was nearly double.

## 7. Contributing back

1. Everything in `found/` must pass `tools/verify.py` first — all eight checks
   in `04_VERIFY.md`, including the three degeneracies.
2. Rebuild the catalogue and re-verify **everything**, not just the new rows.
3. Quote `(gamma, A_d)` as a pair, with `V_ex` beside every rate.
4. Say which evidence class each claim is in: `CERTIFIED`, `ARGUED`, `floor`,
   or `not found in N nodes`.

When merging against an external catalogue: join on the column-set hash where
you have columns; on `(n, k_essential, d, gate)` where you only have
parameters; **never** on `(n, k, d)`.

**Do not pass a `gate` claim to a merge tool.** Above `k = 10` the digit form is
ambiguous — bare `12` is wire 12 or wires `{1,2}` — and a claim in the as-found
frame will not match an `S_k`-canonical one. The gate is derived from columns
regardless. `d` **may** be passed: it is measured, and a claim the measurement
disproves rejects the row, which is what you want.

## 8. If you are starting fresh

The highest-value opening moves, in order:

1. Run `reference/verify_factory.py --selftest`. Confirm it fails the two real
   defective fixtures. If your own verifier passes them, fix it before anything
   else.
2. Re-derive the bar you intend to beat, from columns, with your own tool.
3. Read `03_STATE.md` §3 and §6 so you do not spend a week on something closed
   by theorem or measured dead three times.
4. Pick an open front from `03_STATE.md` §4 and **price it before running it**.
