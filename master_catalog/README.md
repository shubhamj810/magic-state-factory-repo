# Master catalogue

The owner's permanent collection of factory results: one table of **every
Clifford level-3, distance ≥ 3 factory** this repository holds, with every row
carrying its own explicit circuit and every published number re-derivable from
that circuit alone.

| file | contents |
|---|---|
| [`master_catalog.json`](master_catalog.json) | **the catalogue.** One self-contained row per class |
| [`MASTER_CATALOG.md`](MASTER_CATALOG.md) | a human-readable **view** of it — generated, never hand-edited |
| [`verify_catalog.py`](verify_catalog.py) | re-derives every row of the JSON from its columns |
| [`merge_results.py`](merge_results.py) | verifies new results to the same bar and merges them in |
| [`catalogfile.py`](catalogfile.py) | reading, writing and rendering the two files; no verification logic |
| [`attribute_classification.py`](attribute_classification.py) | credit a classification catalogue on the rows it certifies -- provenance only, no circuit field is touched; needed because a class first merged from a search and later covered by a classification is a `duplicate` to `merge_results.py`, which changes nothing |
| [`faultcore.py`](faultcore.py), [`glcanon.py`](glcanon.py), [`skcanon.py`](skcanon.py), [`gatelabels.py`](gatelabels.py) | the primitives: fault search, the `GL(k,2)` class decision, the `S_k` frame, reading a claimed gate string |
| [`migrations/`](migrations/) | the one-off scripts that re-keyed the catalogue on `GL(k,2)` classes and added its citations (2026-09-15), kept so the change can be re-run and read |
| [`reduced_degree_cache.json`](reduced_degree_cache.json) | memoised reduced-degree bounds, so re-verifying a `k = 5, 6` row is a lookup rather than a ~100 s re-search |
| [`tests/`](tests/) | an independent re-derivation of the shipped file, plus the verifier's and merger's own suites |

```bash
.venv/bin/python master_catalog/verify_catalog.py            # all rows, plus the file-level checks
.venv/bin/python master_catalog/verify_catalog.py --rows 1-20
.venv/bin/python master_catalog/merge_results.py new.json    # see "Merging" below
.venv/bin/python -m unittest discover -s master_catalog/tests
```

The dependency chain is one-directional on purpose:

```
faultcore / glcanon / skcanon /      primitives, pinned by tests/
gatelabels
        ^
catalogfile                          JSON I/O and the Markdown generator
        ^
verify_catalog                       the bar: row and catalogue checks
        ^
merge_results                        imports verify_catalog, so "verified to
                                     the same bar" is a fact about the call
                                     graph, not a promise in prose
```

## What is in it

Currently **632 distinct `(n, k, d, GL(k,2) gate)` classes**. Widths run
`k = 1..162`, injection counts `n = 15..1023`, and distances `d = 3..7`.

A class is a distance together with a gate up to an invertible change of the
output basis (a CNOT frame) and diagonal Clifford corrections — the CNOT+S
output equivalence of the length-54 classification. Two circuits at the same
distance whose gates differ only by such a frame, `T0·T1` and `T0·CS01` for
example, prepare the same magic state and are one row. Circuits at different
distances are always different rows. This is coarser than the `S_k` key (output permutations only) that the
classification catalogues use, and that the catalogue itself used until
2026-09-15, when [`migrations/gl_dedup_2026_09_15.py`](migrations/gl_dedup_2026_09_15.py)
folded 1,750 `S_k` rows into 632 classes. [`glcanon.py`](glcanon.py) decides the
relation from the gate's third finite difference, a symmetric trilinear form
that transforms covariantly and vanishes exactly on Cliffords; see
[`theory/02_classification.md`](../theory/02_classification.md) for why it is not
the `F_2` truth-table `gl_class` annotation of the classification catalogues.

The retained circuit for a class is the one with the fewest ambient qubits,
relabelled into its `S_k`-canonical output frame so the columns shown deposit
exactly the `gate` shown. Every contributing source — including those of every
frame that was folded in — stays listed in `sources`. Exact `T`-count and
reduced degree are CNOT-frame invariants, so they are properties of the class.

Every row also credits the works that state it, in `citations`, resolved against
the header's `references` map:

* `n ≤ 54`: the length-54 classification (Wills, Jain and Singh) and the
  symmetry-and-AI report (Jain, Wills and Singh), plus any published work the
  classification's Pareto table attributes the class to;
* `n > 54`: the published works that state the class with the same `n`, `k`,
  distance and output gate, where there are any, and otherwise the
  symmetry-and-AI report. The matching, entry by entry and with the place each
  parameter set is printed, is in
  [`migrations/literature_citations_2026_09_15.py`](migrations/literature_citations_2026_09_15.py).

## The row schema

A row is **self-contained**: every number it publishes follows from `columns`
and `k`, and `verify_catalog.py` recomputes each one and compares. So this list
is also the list of what gets checked.

| field | meaning |
|---|---|
| `n` | number of columns (π/4 parity rotations) |
| `k` | output wires; they are `0..k-1`, wires `k..N-1` are the postselected checks |
| `N` | ambient wires — equal to the largest qubit index used, plus one |
| `d` | verified fault distance: **exact** if `d_is_exact`, otherwise a proved **floor** |
| `level` | 3 throughout this catalogue |
| `columns` | the circuit: one qubit-support list per rotation, sorted and duplicate-free |
| `gate` | the deposited output gate, as a monomial string |
| `gate_human` | the same gate as `T`/`CS`/`CCZ` factors |
| `sk_key` | the `S_k` canonical monomial set, or `null` when the `k!` minimisation was not proved (then `sk_key_note` says so) |
| `sk_canonical_frame` | whether the columns are shown in that canonical frame |
| `sk_fingerprint` | a permutation-invariant fingerprint of the gate |
| `d_is_exact` | `true` iff a clean sweep below `d` met a witness **at** `d` |
| `d_upper` | the weight of an explicit harmful fault, or `null` |
| `d_witness` | that fault, as column indices into this row's `columns` |
| `t_count` | exact minimal level-3 T-count, or `null` with `t_count_note` |
| `poly_degree` | CNOT-frame-reduced phase-polynomial degree, or `null` with a note |
| `effective_width` | rank of the output rows modulo the check span; must equal `k` |
| `regimes`, `discovery`, `strongest_claim`, `sources` | provenance |
| `relabelled_into_canonical_frame` | provenance too: whether the ingest permuted the columns on the way in. A self-contained row cannot prove or refute it — the source frame is not stored — so the verifier checks its type and nothing else |
| `citations` | provenance too: keys of the header's `references` map crediting the class. The verifier checks that every key resolves, that a row cites at least one work and none twice; which works are credited is a curation decision |

**Provenance is inert.** `sources` and
`relabelled_into_canonical_frame` record where a class came from and how it
arrived, in strings and a flag, several of which name source directories this
folder no longer has. Nothing in this folder ever opens a path one of them
mentions or computes with the flag: a row is true or false on its columns
alone, and its history is history.

`k` is the one thing that is read rather than derived, because the output/check
split is a **declaration**: the same columns with a different `k` are a
different factory, or none.

## Verifying

```bash
.venv/bin/python master_catalog/verify_catalog.py
```

For every row, from `columns`, `k` and `N` alone:

1. **Validity.** `n == len(columns)`; the columns are non-empty and **distinct**
   — two equal columns cancel to a diagonal Clifford, contributing to no parity
   and no monomial, so they are dead weight in `n`, the injection count this
   table is read for, and the circuit is not the reduced one it claims to be;
   every wire `0..N-1` is touched; `level == 3`.
2. **The factory condition.** Every degree-≤3 parity that touches a check wire
   is even. If one is odd the circuit deposits phase on a postselected wire and
   the accepted action is not the gate the outputs claim — it is not a factory.
3. **The gate**, read off the columns and compared **literally** against `gate`,
   `gate_human`, `sk_key` and `sk_fingerprint`. An empty gate is Clifford,
   level ≤ 2 and out of scope.
4. **The distance.** Absence below `d` is *proved*: every weight `1..d-1` is
   swept to completion, and a sweep the budget cut short is a **failure**, not a
   pass — a floor nobody proved is not a floor. Presence at `d` is *witnessed*:
   when `d_is_exact`, `d_witness` is re-checked against the true syndromes.
5. **No spectator output**: the gate touches every one of the `k` outputs.
6. **No pseudo-output**: the `k` output rows are linearly independent *modulo
   the check span*, so an output equal to another one, or to another one plus a
   stabiliser, or lying in the check span itself, is rejected rather than
   counted twice.
7. **No redundant check**: the `r` check rows are linearly independent *of each
   other* — the check-side twin of 6. A check row inside the span of the others
   carries a syndrome bit that is an XOR of theirs for every fault, so it
   rejects nothing they accept and can be deleted with `n`, `k`, the gate and
   the distance all intact; a row carrying one overstates `N`.
8. **The metrics**: the minimal T-count and CNOT-frame-reduced degree wherever
   those are computable, and a note saying why wherever they are not. The
   T-count is exact throughout; the degree is exact through `k = 4` and a
   documented sampled upper bound at `k = 5, 6`.

Then, across the file, three checks a single row cannot make about itself:

* **No two rows are the same class** — equal `d` and `S_k` keys convict
  outright, and every same-`(n, k, d)` pair is then decided by
  `glcanon.gl_isomorphic`, a
  decision procedure rather than a hash. A pair whose search runs out of budget
  must carry a `dedup_note`.
* **Every row's citations resolve.** At least one work, none twice, every key an
  entry of the header's `references` map.
* **Every row's provenance labels resolve against the header.** Each name in
  `regimes` is one the file's own header defines, the names are in the header's
  strongest-first order, and `strongest_claim` is the header's sentence for the
  first of them. That sentence is what tells a reader whether a row is a
  classified maximum or a search witness, so it is derivable and therefore
  compared — the same standard `gate_human` is held to.

Every field is compared, not just the interesting ones, and the **type** of each
is checked before its value is: `True == 1` in Python and not in JSON, so a row
publishing `"t_count": true` would otherwise compare equal to a recomputed
T-count of 1 and pass. A failed row prints its reasons and the exit status is
non-zero.

Check 6 is the one an incoming search corpus most often fails.
`theory/02_classification.md` places a `k`-output factory in the quotient
`V = R(C)/C` as a linearly **independent** `k`-subset: everything the gate reads
off an output row is invariant under `a → a + c` for `c` in the check span, so
two outputs differing by a stabiliser are one logical qubit wearing two labels —
and `k` is the denominator of every rate anyone quotes. It is not the same check
as 5, and passing 5 does not imply it.

## Merging new results

```bash
.venv/bin/python master_catalog/merge_results.py new_results.json
.venv/bin/python master_catalog/merge_results.py new_results.json --dry-run
```

### The input file

One JSON object per result. The file may be a JSON array of them, an object
wrapping them under `results` / `factories` / `rows`, a single bare object, or
JSON Lines (`#` comments and blank lines ignored). An **empty file is valid**
and merging it changes nothing.

| field | |
|---|---|
| `k` | **required.** Output wires, as above — a declaration |
| `N` | **required.** Ambient wires; must equal the largest qubit index used, plus one |
| `columns` | **required.** One list of qubit indices per π/4 rotation |
| `n` | optional; checked against `columns` |
| `d` | optional **claim**. Never believed — see below |
| `gate` | optional **claim**, as monomials or a `T`/`CS`/`CCZ` string |
| `t_count`, `poly_degree` | optional **claims**, compared where the exact recomputation is feasible |
| `regime` | optional; which corpus this came from. Default `merged results` |
| `strength` | optional; what a row from a **new** regime means, one sentence |
| `discovery` | optional; `AI search` (default) or `pre-existing` |
| `citations` | optional; keys of the header's `references` map. Omitted, an accepted row is credited to the length-54 classification and the symmetry-and-AI report when `n ≤ 54`, and to the report alone otherwise; an improvement adds its citations to the class's |
| `label`, `provenance`, `origin`, `file`, `notes` | optional provenance strings — inert |

Anything else in a record is a typo and rejects it: `colums` silently ignored is
a circuit merged from a field nobody read.

### What happens to each result

1. **Verified** — structure, the factory condition, the gate, spectator and
   pseudo-output freedom, freedom from check wires that carry no syndrome bit
   of their own, the metrics.
2. **Canonicalised** — the output wires are relabelled into the `S_k` lex-minimal
   frame, *before* the distance is measured, so the witness's column indices
   index the columns that get stored.
3. **The distance is measured**, not assumed.
4. **The record's claims are checked**, and the assembled row is then put through
   `verify_catalog.verify_row` — the same code that will re-check it in the
   shipped file. If that finds anything, the row does not go in.
5. **Deduplicated** on `(n, k, d, GL(k,2) gate)`: an equal distance and proved
   `S_k` key settle a match, and `glcanon.gl_isomorphic` decides every other
   same-`(n, k, d)` row. A circuit at another distance is a new class.
6. One of four verdicts, all printed:

   | verdict | |
   |---|---|
   | `accepted` | a class the catalogue did not have. Appended |
   | `improved` | a class it had, with a better circuit. The retention rule is fewest ambient qubits, then fewest columns, then the strongest proved distance, then a proved canonical frame. The new provenance is **appended** to `sources` |
   | `duplicate` | a class it had, with a circuit no better. **Nothing changes** — not the row, not `sources`, not the header — which is what makes re-merging a file a no-op the second time |
   | `rejected` | did not verify. The reason is printed, and the exit status is 1 |

Both files are then regenerated from the merged payload, deterministically, so
an unchanged catalogue is rewritten **byte-identically** and a real change shows
up as a minimal diff rather than a reformat of twelve megabytes.

**A claim is checked, never believed, and only a *disproved* claim rejects.** A
`d` claimed above what an explicit witness allows rejects the record — a wrong
distance usually means the record is about a different circuit. A `d` claimed
*below* the measured value is accepted and the larger proved value is stored:
understating is not an error. An **unreadable** `gate` string does reject: the
circuit may be fine, but a claim nothing can check should not ride along into a
catalogue whose whole premise is that every field was re-derived.

## The regimes, and why they stay apart

Rows keep the regime they came from, because those make claims of different
strengths and mixing them is how a search record gets misread as a classified
maximum:

| regime | a row from it means |
|---|---|
| `exhaustive n<=38` | classified: nothing else exists in that window |
| `census r<=7` | classified subject to the check-rank bound `r ≤ 7` |
| `search record` | best found by targeted search; **not** a maximum |
| `AI results`, `catalogue_new` | found by an AI search campaign; a verified witness, **not** a maximum |
| `magic-states-AI master catalogue` | merged from the AI campaign's own catalogue; a verified witness, **not** a maximum |
| `campaign 48<n<128` | found by the targeted `48 < n < 128` campaign; a verified witness, **not** a maximum |

A regime a merge introduces is registered at the **end** of that order, i.e. as
the weakest claim — a merged witness can never outrank a classification.

`discovery` is a different axis: `pre-existing` if one of the three
classification catalogues has the class, `AI search` if it was found by a search
campaign instead. A class a campaign found that was **already** catalogued keeps
`pre-existing`; it is a reproduction, and its `sources` lists both.

## The distance, and what a number in that column means

`d_is_exact` is the field to read. When it is true, there is proved to be no
harmful fault below `d` **and** one is exhibited at it; the witness ships in
`d_witness` and is three lines to re-check. When it is false, `d` is a proved
floor and the tables print it as `≥d`. An unpinned distance is never quoted as a
measured one.

## Three implementations, on purpose

| module | what it does | pinned against |
|---|---|---|
| [`faultcore.py`](faultcore.py) | bit-level gate read-off, output structure, fault search at the scale the catalogue reaches (`n` to 1023, `k` to 162) | the literal `C(k,3)` / `C(n,4)` enumerations kept beside the verifier in [`verify_catalog.py`](verify_catalog.py), on every circuit small enough for both |
| [`glcanon.py`](glcanon.py) | the `GL(k,2)` class decision: tensor, invariants and a budgeted search | a literal enumeration of `GL(k,2)` on `Z_8` truth tables in [`tests/test_glcanon.py`](tests/test_glcanon.py) — every pair at `k = 2, 3`, random pairs at `k = 4`, and all 9,999,360 frames of `GL(5,2)` for a pair whose invariants agree |
| [`skcanon.py`](skcanon.py) | the `S_k` frame at widths where `k!` is not a loop | `classification/exhaustive_n38/dedup.py`, on 1,200 random gates |
| `factorylib/verification.py` | the repository's standalone verifier, sharing no code with any search or catalogue here | run as a third opinion on every circuit within its reach |

[`tests/`](tests/) re-does the core checks on the shipped file with its **own**
implementations rather than importing the verifier's, so a mistake has to be
made twice to go unnoticed. It adds what only a consumer can check: that the
catalogue still holds every qualifying row of the three classification
catalogues, that its filter is exactly "level 3, distance ≥ 3", that the
`discovery` tag agrees with the regimes, and that no class is in the table
twice. The verifier's and merger's own suites are mostly **negative** — a
verifier is worth what its rejections are worth — and cover broken check parity,
a wrong or unreadable gate label, an inflated distance, a pseudo-output, a
spectator output, a redundant check wire, a repeated column, a duplicate class,
wrong metrics, an unexplained circuit no source published, and misspelt, missing
or undocumented fields.

## What is deliberately missing

* **T-count and reduced degree above `k = 6`.** Both are minimisations — over
  `GL(k,2)` and over a punctured Reed–Muller coset — and neither is feasible
  past `k = 6`. Those fields are `null` with a note saying so, never
  estimated. Between `k = 5` and `k = 6` the degree is a documented upper bound
  over a seeded frame sample, which is what `factorylib` produces there; the
  sample size is written into the note, and `reduced_degree_cache.json` holds
  the results so re-verification is a lookup rather than a re-search.
* **A canonical output frame for six very wide gates.** The `S_k` lex-minimum
  over `k!` relabellings was not proved within the search budget for
  `[[127,26,3]]`, `[[127,37,3]]`, `[[256,16,4]]`, `[[256,84,4]]`,
  `[[496,36,4]]` and `[[512,84,6]]`, so those six are shown in their as-found
  frame and say so. Their uniqueness is decided by `glcanon.gl_isomorphic` like
  every other row's, so the dedup is sound; only the displayed labelling is
  arbitrary.
* **Higher-distance circuits discarded before 2026-09-15.** Until then the class
  key left out the distance, and a merge kept the circuit with fewest ambient
  qubits, so four higher-distance circuits were dropped for narrower ones at a
  lower distance and their columns are not in this file: `[[176,3]]` `CCZ` at
  `d = 6` (`N = 28`), `[[255,3]]` `T^3` at `d = 5` (`N = 19`), `[[511,9]]`
  `T^9` at `d = 6` (`N = 36`) — each still named in its row's `sources` — and
  `[[48,3]]` `CCZ` at `d = 4` (`N = 10`, Jacinto et al.). The key now includes
  `d`, so a re-merge of those circuits would be accepted as new rows.
* **Hidden spectators.** The spectator and pseudo-output checks are made in the
  stored frame. A gate that, in some other CNOT frame, leaves an output untouched
  up to Cliffords (`T0·T1·CS01` is `T` on `x0 + x1` times a `CZ`) passes them;
  80 of the 632 classes are of this kind, including rows inherited from the
  exhaustive classification.
* **Repairs.** A circuit rejected for a spectator, a pseudo-output or a
  redundant check wire is not fixed on the way in. Demoting a redundant output
  to a check, or deleting a check wire the others already decide, gives a valid
  circuit, but it is not the one that was submitted — so it is a search result,
  not a merge. Where this catalogue has itself made such a repair, the row says
  so in `columns_note` and the verifier requires that note wherever the shipped
  `N` is one no source published.
