# `agent_context/` — everything an outside agent needs to continue this work

> **In this repository.** This pack was written in the AI-search repository
> `shubhamj810/magic-states-AI` and is a copy of its commit `5cf5966`,
> unchanged apart from this note.
>
> - **What its numbers describe.** The figures in `03_STATE.md` and below are
>   about that repository's own corpus, `master_catalogue.jsonl`. It is
>   deduplicated on `S_k`; `03_STATE.md` and `check_claims.py` count 837
>   factories in it (the one-paragraph summary below says 822; the checked
>   figure is 837). That corpus is merged into this repository's database, but
>   it is not the database.
> - **This repository's database** is
>   [`../master_catalog/master_catalog.json`](../master_catalog/master_catalog.json).
>   It keys classes on `(n, k, d, GL(k,2))` and also holds the length-54
>   classification and later campaigns, so its counts differ.
> - **What runs here as is.** `reference/verify_factory.py` needs only the
>   standard library.
> - **What does not.** `reference/check_claims.py` reads `master_catalogue.jsonl`,
>   which lives only in magic-states-AI.
>
> Read the pack for how the searches work, what is known to be closed, and how
> not to be fooled. Read the master catalogue for which factories exist.

This is a **portable context pack**. It supplements the public master catalogue:
the catalogue tells you *which factories exist*, this tells you *what is known,
what is false, what has already been tried, and what will fool you*.

It is written to be handed to an AI agent as-is. It is self-contained — nothing
here requires the rest of the repository, and the reference verifier depends on
nothing but the Python standard library.

```
agent_context/
  README.md              you are here
  01_PRIMER.md           the object, the data model, and every metric — read first
  02_RULES.md            nine rules, each with the failure that produced it
  03_STATE.md            records, what is closed by theorem, what is open
  04_VERIFY.md           the verification contract: what to check and why
  05_CAMPAIGN.md         how to run a campaign and contribute results back
  06_TECHNIQUES.md       reformulations, search methods, measured costs, tooling bugs
  07_THEOREMS.md         structural results, each with its exact scope
  08_HISTORY.md          eight campaigns: what was tried, what held, what was retracted
  09_BASELINES.md        prior art, conversion identities, the derived-baseline gate
  reference/
    verify_factory.py    a complete verifier in one stdlib file
    check_claims.py      re-derives every figure in 03_STATE.md from the catalogue
    fixtures/            real circuits: one healthy, two with real defects
```

## Read in this order

| you are… | read |
|---|---|
| orienting, any purpose | `01_PRIMER.md` — 10 minutes, and nothing else makes sense without it |
| about to search | `02_RULES.md`, `03_STATE.md` (do not re-derive a closed result), then `06_TECHNIQUES.md` |
| about to claim a result | `04_VERIFY.md` and `09_BASELINES.md`, then run `reference/verify_factory.py` |
| reading the catalogue | `01_PRIMER.md` §4 (metrics) and `04_VERIFY.md` §5 (evidence classes) |
| wondering if it has been tried | `08_HISTORY.md`, then `03_STATE.md` §6 |
| proving something | `07_THEOREMS.md` — scope matters as much as the statement |
| contributing back | `05_CAMPAIGN.md` |

**Minimum viable read** if you are only going to read two: `01_PRIMER.md` and
`04_VERIFY.md`. **Minimum before claiming anything**: add `09_BASELINES.md`.

## Start here, literally

```bash
python3 reference/verify_factory.py --selftest
python3 reference/verify_factory.py reference/fixtures/good_n8_k3_d2.json
python3 reference/check_claims.py path/to/master_catalogue.jsonl
```

The selftest runs three real circuits and two planted ones. Two of the three
real ones were **catalogued as correct for months** before the defect they
carry was found. If your verifier passes those two, your verifier is broken —
which is the whole reason this directory exists.

## The one-paragraph version

A magic-state factory consumes `n` noisy `T` states and emits `k` better ones,
suppressing error `p → A_d·p^d` where `d` is the circuit distance. The figure of
merit for the asymptotic limit is `gamma = log(n/k)/log(d)` (lower is better);
the figure of merit at any real operating point also needs `A_d`. The current
record in this corpus is `[[901,123,6]]` at `gamma = 1.111377`. **822 distinct
verified factories** are catalogued. The single most important thing to
internalise: *every number about a circuit is recomputed from its `columns`, and
nothing stored is believed* — including, especially, numbers written by this
project.

## What this corpus is good for, and what it is not

**Good for.** Starting from a verified frontier instead of zero; knowing which
search routes are already closed *by proof* rather than by someone giving up;
inheriting a verification discipline that took a dozen real defects to build;
and not re-walking eight campaigns' worth of dead ends.

**The three things most likely to save you a week**, if you read nothing else:

1. `06_TECHNIQUES.md` §2 — which search methods are *measured dead* here, and
   which one found the current record.
2. `07_THEOREMS.md` §5 — what is closed by proof on the main parent, so you do
   not search a region that cannot contain an answer.
3. `09_BASELINES.md` §4 — the derived-baseline gate, which retracted an entire
   campaign's framing when it was finally applied.

**Not good for.** Hardware cost estimates — `gamma` is an asymptotic exponent
and nothing operates in that limit. Cross-gate rate comparisons without `V_ex`.
Anything that treats `[[n,k,d]]` as identifying a circuit: **148 parameter
tuples in this catalogue are realised by more than one genuinely distinct
factory**, and two rows agreeing on every rate can differ by 10% in `A_d`.

## Provenance and honesty

Every figure in these files was **counted from the shipped data on
2026-09-11**, not transcribed from an older document — and you do not have to
take that on faith either. `reference/check_claims.py` re-derives all 50 of them
from the catalogue and exits non-zero on any disagreement:

```
$ python3 reference/check_claims.py master_catalogue.jsonl
  OK   distinct verified factories: 822
  OK   record gamma: 1.111377
  ...
ALL CLAIMS HOLD
```

A failure there means the corpus has moved on and this prose is stale — fix the
prose, not the check. Where this corpus disagrees with itself, the disagreement
is written down rather than smoothed over: see `03_STATE.md` §5. Where a claim
is argued rather than enumerated, it says so.

If you find an error here, you are doing it right; that is how every rule in
`02_RULES.md` came to exist.
