# Master catalogue

**This directory is the repository's database.** It holds the permanent
collection of factory protocols: one table of **every Clifford level-3, distance
≥ 2 factory** this repository holds. Every row carries its own explicit circuit,
and every published number can be re-derived from that circuit alone. Rows come
from the exhaustive length-54 classification, the
[borrowed-identity searches](../borrowed_identities/) of Singh, Gidney and Jones,
the [transversal-T codes](../transversal_t_codes/) of Jain and Albert, the
AI-assisted and SAT searches, the literature and
[community contributions](../community_contributions/).

| file | contents |
|---|---|
| [`master_catalog.json`](master_catalog.json) | **the catalogue.** One self-contained row per class |
| [`MASTER_CATALOG.md`](MASTER_CATALOG.md) | a human-readable **view** of it — generated, never hand-edited |
| [`verify_catalog.py`](verify_catalog.py) | re-derives every row of the JSON from its columns |
| [`merge_results.py`](merge_results.py) | verifies new results to the same bar and merges them in |
| [`catalogfile.py`](catalogfile.py) | reading, writing and rendering the two files; no verification logic |
| [`attribute_classification.py`](attribute_classification.py) | credit a classification catalogue on the rows it certifies -- provenance only, no circuit field is touched; needed because a class first merged from a search and later covered by a classification is a `duplicate` to `merge_results.py`, which changes nothing |
| [`faultcore.py`](faultcore.py), [`glcanon.py`](glcanon.py), [`skcanon.py`](skcanon.py), [`gatelabels.py`](gatelabels.py) | the primitives: fault search, the `GL(k,2)` class decision, the `S_k` frame, reading a claimed gate string |
| [`clifford.py`](clifford.py) | the Clifford correction a circuit needs, the rotation powers that avoid it (or the proof that none do), and a direct evaluation of the logical action |
| [`migrations/`](migrations/) | the one-off scripts that made structural changes to the file (keying on `GL(k,2)` classes, citations, distance certificates, the length-54 classification, source paths, header wording, the distance-2 floor and the Borrowed Identities import, the Clifford corrections, the transversal-T codes), kept so each can be re-run and read |
| [`reduced_degree_cache.json`](reduced_degree_cache.json) | memoised reduced-degree bounds, so re-verifying a `k = 5, 6` row is a lookup rather than a ~100 s re-search |
| [`tests/`](tests/) | an independent re-derivation of the shipped file, plus the verifier's and merger's own suites |

```bash
.venv/bin/python master_catalog/verify_catalog.py            # all rows, plus the file-level checks (~20 min)
.venv/bin/python master_catalog/verify_catalog.py --changed  # only the rows that differ from HEAD, plus the file-level checks (seconds)
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

**1027 distinct `(n, k, d, GL(k,2) gate)` classes**. 181 of them are at
distance 2, and 217 are at `d ≥ 3` with `n ≤ 54`. Widths run `k = 1..373`,
injection counts `n = 8..3239`, and distances proved here `d = 2..7`. Sources
certify up to `d ≥ 31` on the transversal-T codes.

**Transversal-T codes.**
[`migrations/transversal_t_codes_2026_10_10.py`](migrations/transversal_t_codes_2026_10_10.py)
and
[`migrations/transversal_t_codes_table1_2026_10_10.py`](migrations/transversal_t_codes_table1_2026_10_10.py)
merged the codes of S. P. Jain and V. V. Albert (IEEE JSAIT 6, 127 (2025),
arXiv:2408.12752). They are rebuilt from the paper's doubling construction in
[`../transversal_t_codes/`](../transversal_t_codes/README.md): `[[15,1,3]]` to
`[[3239,1,31]]`, all 27 codes of its two tables, 25 of them new classes. Ten of
them rest on a `[[69,1,13]]` code from a self-dual `[70,35,12]` code found by
the search in that folder, in place of the paper's formally self-dual
`[70,35,14]`. Above `n = 95`
the sweep here proves only a floor, from 7 down to 3. Each of those rows
carries the paper's distance as a certified lower bound (`d_certified`) and an
explicit fault of exactly that weight (`d_upper`, `d_witness`). Together they
pin the distance, though the label, as always, uses the proved one.

**Clifford corrections.** Every row says what its circuit needs besides the
rotations to be exactly its gate (`clifford_correction`), and whether running
some rotations as `T³`, `T⁵` or `T†` makes that unnecessary
(`rotation_powers`). 10 classes need nothing, 561 need only powers, and 456
need `S` or `CZ` gates whatever the powers.
[`migrations/clifford_corrections_2026_10_10.py`](migrations/clifford_corrections_2026_10_10.py)
added the fields, and [`clifford.py`](clifford.py) explains the method.

**Distance 2.** The floor was `d ≥ 3` until 2026-10-07.
[`migrations/distance_two_2026_10_07.py`](migrations/distance_two_2026_10_07.py)
lowered it to 2 and merged two sets of circuits, both through `merge_results`:

- the level-3 circuits of the
  [Borrowed Identities import](../borrowed_identities/README.md) (Singh, Gidney
  and Jones, arXiv:2606.28518). Their 185 circuits give 179 new classes, 171 at
  distance 2 and 8 single-output classes at distance 3;
- the 19 distance-2 rows of the symmetry-SAT catalogue, which the old floor
  kept out. They give 10 new classes.

The length-54 classification is a `d ≥ 3` statement, so the two
`exhaustive classification` regimes, and the frontier tests, apply to `d ≥ 3`
rows only.

The [graph-gluing import](imports/2026-09-18_graph_gluing_d3/README.md) holds
nine exact-distance-three pure-T witnesses built by gluing catalogued small
factories along a graph of paired-column contractions, including `[[495,99,3]]`
and `[[880,176,3]]` at five inputs per output. The bundle includes every
witness, its seed circuits, construction provenance, and a self-contained
reconstruction script.

A class is a distance together with a gate up to an invertible change of the
output basis (a CNOT frame) and diagonal Clifford corrections — the CNOT+S
output equivalence of the length-54 classification. Two circuits at the same
distance whose gates differ only by such a frame, `T0·T1` and `T0·CS01` for
example, prepare the same magic state and are one row. Circuits at different
distances are always different rows. This is coarser than the `S_k` key (output
permutations only) that the legacy classification catalogues use: one class can
hold several `S_k` classes. [`glcanon.py`](glcanon.py) decides the
relation from the gate's third finite difference, a symmetric trilinear form
that transforms covariantly and vanishes exactly on Cliffords; see
[`theory/02_classification.md`](../theory/02_classification.md) for why it is not
the `F_2` truth-table `gl_class` annotation of the classification catalogues.

The retained circuit for a class is the one with the fewest ambient qubits,
relabelled into its `S_k`-canonical output frame so the columns shown deposit
exactly the `gate` shown. Every contributing source, in any frame, is listed in
`sources`. Exact `T`-count and
reduced degree are CNOT-frame invariants, so they are properties of the class.

Every row also credits the works that state it, in `citations`, resolved against
the header's `references` map. `MASTER_CATALOG.md` prints only the papers, and
links each published one to its DOI or arXiv page.

* **The 74 Pareto points of the length-54 classification** are credited by who
  found them.
  * **In the literature.** Nine are attributed to a published protocol by the
    classification's Pareto table (Table `tab:complete-pareto`): Bravyi & Kitaev,
    Nezami & Haah, Jacinto et al. and Gong et al. A tenth, `[[49,1,5]]`, is
    the 49-qubit code of Bravyi & Haah (2012, Appendix B), which that table
    does not attribute
    ([`migrations/bravyi_haah_49_2026_10_10.py`](migrations/bravyi_haah_49_2026_10_10.py)).
    These are credited to that work **alone**.
  * **Also found by our searches.** A Pareto point that this project's own
    symmetry-SAT or AI searches also found is credited to the
    classification (Wills, Jain and Singh,
    [arXiv:2609.30860](https://arxiv.org/abs/2609.30860)) **and** the
    symmetry-and-AI report (Jain, Wills and Singh,
    [arXiv:2610.06535](https://arxiv.org/abs/2610.06535)).
  * **Everything else** is credited to the classification alone.
* **Every other class with `n ≤ 54`** is credited to the classification and the
  symmetry-and-AI report. A published work that states it is credited too;
  none currently does.
* **`n > 54`.** The published works that state the class with the same `n`,
  `k`, distance and output gate, where there are any, and otherwise the
  symmetry-and-AI report.
* **The transversal-T codes** of Jain and Albert are credited to their paper,
  except `[[95,1,7]]`, which Sullivan (PRA 109, 042416 (2024)) published
  first. The `[[15,1,3]]` and `[[49,1,5]]` codes were already held and keep
  their credit.
* **Distance 2.** The length-54 classification does not cover distance 2, so a
  distance-2 class never cites it. A class the borrowed-identity searches found
  is credited to their paper (Singh, Gidney and Jones), unless an earlier work
  published it. Then that earlier work alone is credited: Bravyi & Haah,
  Eastin and Jones, Webster et al., Campbell & Howard, and, for the 15-to-1,
  Bravyi & Kitaev ([`migrations/earliest_reference_2026_10_07.py`](migrations/earliest_reference_2026_10_07.py)).
  The table is in
  [`../borrowed_identities/README.md`](../borrowed_identities/README.md). A
  distance-2 class only the symmetry-SAT
  search found is credited to the symmetry-and-AI report, unless a published
  work states it (`12.5.2.a`, Campbell & Howard's Example IV.4).
* **A community contribution** that brings a new class is credited to the
  contributor's own reference. A published work is linked; an unpublished one
  credits the contributor without a link. A contribution that repeats or
  improves a class already held does not change that class's credit. See
  [`../community_contributions/README.md`](../community_contributions/README.md).

The literature matching is in
[`migrations/literature_citations_2026_09_15.py`](migrations/literature_citations_2026_09_15.py),
entry by entry and with the place each parameter set is printed. The Pareto-point
rules are in
[`migrations/length54_classification_2026_09_16.py`](migrations/length54_classification_2026_09_16.py).

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
| `clifford_correction` | `{"S": [[wire, p], ...], "CZ": [[wire, wire], ...]}`: the diagonal Clifford to apply after the rotations and before the checks are measured, so that the accepted action is **exactly** `gate`, with `T = diag(1, e^{iπ/4})`, `CS = diag(1,1,1,i)` and `CCZ`. `S^p` for `p` = 1, 2, 3 is `S`, `Z`, `S†`. Unique; derived by the weight expansion of Bravyi and Haah (2012) |
| `rotation_powers` | `[[column, power], ...]`: run those rotations as `T^power` (3, 5 or 7, and `T⁷ = T†`) and the rest as `T`, and no correction is needed. `[]` when none is needed anyway; `null` when no choice of powers avoids `S` or `CZ` gates. Not unique: a list is checked by evaluating the logical action at those powers, and `null` is re-proved by solving the `Z_4` system |
| `regimes`, `discovery`, `strongest_claim`, `sources` | provenance |
| `relabelled_into_canonical_frame` | provenance too: whether the ingest permuted the columns on the way in. A self-contained row cannot prove or refute it — the source frame is not stored — so the verifier checks its type and nothing else |
| `citations` | provenance too: keys of the header's `references` map crediting the class. The verifier checks that every key resolves, that a row cites at least one work and none twice; which works are credited is a curation decision |
| `catalog_label` | the row's permanent public name, `n.k.d.x` (e.g. `15.1.3.a`): `d` is the distance proved here, and the letters (`a`…`z`, then `ba`, `bb`, … as LMFDB numbers its classes) count the classes at that `(n, k, d)` in the order they entered the catalogue. `merge_results.py` gives a new class the next unused letter, and an improvement keeps the label, so a label is never changed or reused. The verifier checks the format and that no two rows share one. It is also the address of the class's page on the website |

**Provenance is inert.** `sources` and
`relabelled_into_canonical_frame` record where a class came from and how it
arrived, in strings and a flag, several of which name directories outside this
repository. Nothing in this folder ever opens a path one of them mentions or
computes with the flag: a row is true or false on its columns alone.

`k` is the one thing that is read rather than derived, because the output/check
split is a **declaration**: the same columns with a different `k` are a
different factory, or none.

## Verifying

```bash
.venv/bin/python master_catalog/verify_catalog.py              # every row
.venv/bin/python master_catalog/verify_catalog.py --changed    # the rows a merge changed
```

The full run re-derives all rows and takes about twenty minutes on one core;
the time is in the few large-`n`, high-distance rows. After a merge, `--changed`
re-derives only the rows whose circuit differs from the catalogue committed at
`HEAD` (or at `--changed REF`, or in a file with `--baseline PATH`) and runs the
whole-file checks below over everything, which takes seconds. A row is
unchanged when a committed row equals it on every field other than provenance
(`regimes`, `discovery`, `strongest_claim`, `sources`, `citations`), since
nothing the row-level checks compute reads those.

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
9. **The Clifford correction**, re-derived and compared literally. Then the
   **logical action** is checked by a computation that does not use the
   derivation. The phase of the corrected circuit, every rotation a `T`, is
   evaluated on every input (`N ≤ 16`), or on every input of weight at most 3
   (or 2 for the widest rows), plus 64 random inputs. It must equal the gate's
   phase on every input, checks included. Weight 3 is complete, because the
   residual phase is a polynomial of degree at most 3. Weight 2 is complete
   given checks 2 and 3. A stored `rotation_powers` list is checked the same
   way, with no correction applied; a `null` is re-proved. On every circuit
   with `N ≤ 12` and `2^(N+k) ≤ 65536`, both are also simulated gate by gate:
   CNOT ladders and single-qubit `T`s, then the correction. Every output basis
   state, with the checks in `|+⟩`, must come back with exactly the gate's
   phase.

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
| `regime` | optional; how the result was found, in a few words (see [the regimes](#the-regimes-and-why-they-stay-apart)). Default `merged results` |
| `strength` | optional; what a row from a **new** regime means, one sentence |
| `discovery` | optional; `AI search` (default) or `pre-existing` |
| `citations` | optional; keys of the header's `references` map. Omitted, an **accepted** row is credited to the length-54 classification and the symmetry-and-AI report when `n ≤ 54` and `d ≥ 3`, and to the report alone otherwise. An improvement or a duplicate adds only the citations the record **names** — a held class keeps the credit it was given, so a class credited to a published work alone is not re-credited because a search found it again |
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
   | `duplicate` | a class it had, with a circuit no better. **Nothing about the circuit or its provenance changes** — not the columns, not `sources`, not `regimes` — which is what makes re-merging a file a no-op the second time. Only a citation the record explicitly names is added |
   | `rejected` | did not verify. The reason is printed, and the exit status is 1 |

Both files are then regenerated from the merged payload, deterministically, so
an unchanged catalogue is rewritten **byte-identically** and a real change shows
up as a minimal diff rather than a reformat of twelve megabytes. Regenerating
takes about two seconds; no existing row is re-verified by a merge. Afterwards,
`verify_catalog.py --changed` re-derives exactly the rows the merge added or
improved and re-runs the whole-file checks, in seconds.

**A claim is checked, never believed, and only a *disproved* claim rejects.** A
`d` claimed above what an explicit witness allows rejects the record — a wrong
distance usually means the record is about a different circuit. A `d` claimed
*below* the measured value is accepted and the larger proved value is stored:
understating is not an error. An **unreadable** `gate` string does reject: the
circuit may be fine, but a claim nothing can check should not ride along into a
catalogue whose whole premise is that every field was re-derived.

## The regimes, and why they stay apart

A row's regime says, in a few words, **how its class was found**, and each
regime carries a claim of its own strength (`strongest_claim`, defined once in
the header). A row keeps every regime one of its sources came from, strongest
first, because mixing them is how a search witness gets misread as an optimum.
The header, in order:

| regime | a row from it means |
|---|---|
| `exhaustive classification n<=54 (Pareto point)` | one of the 74 Pareto points of the exhaustive classification through length 54 ([`../classification/length54/`](../classification/length54/)): nothing with `n ≤ 54`, the same CNOT+S output and the same exact distance uses no more inputs and no more wires, with one strictly fewer |
| `exhaustive classification n<=54` | inside that classification but not on its frontier; a Pareto point strictly dominates it (tested). The repository's exhaustive `n ≤ 38` classification and rank-7 census are stages of this classification and are credited as it; their directories are in `classification/legacy/` |
| `symmetry-SAT search` | found by the symmetry-slot or ansatz-free SAT search ([`../symmetry_sat_search/`](../symmetry_sat_search/)); a verified witness, **not** a maximum |
| `AI search` | found by an AI search campaign; a verified witness, **not** a maximum |
| `AI search: punctured r=7 simplex parents`, `AI search: multi-agent campaign 39<=n<=127` | the named AI campaigns; verified witnesses, **not** maxima |
| `AI search (gamma frontier): …` | the pure-T distillation-exponent release, split by the construction each record names: from Wills parent codes, contraction of an existing code, logical restriction of a length-54 Pareto point, or (one row) a punctured Reed–Muller code. Verified witnesses; only the release's own frontier points are its lowest `γ` |
| `AI search: Wills downset framework` | exact optima of one framework (arXiv:2608.24000), not maxima over all factories |
| `AI search: pure-T width campaign n=255, 511`, `AI search: pure-T puncture caps`, `AI search: full-simplex pure-T frames` | width and cap witnesses, explicitly **not** rate records |
| `AI search: generalised triorthogonal search 55<=n<=64` | found by the AI-assisted public search for generalised triorthogonal protocols at lengths 55–64; a verified witness, not a maximum |
| `community contribution` | a protocol an outside author submitted through [`../community_contributions/`](../community_contributions/), verified here from its columns; a verified witness, not a maximum. Registered the first time one is merged |
| `borrowed-identity search: two-group`, `borrowed-identity search: symmetry-free` | found by the two searches of Singh, Gidney and Jones (arXiv:2606.28518), imported in [`../borrowed_identities/`](../borrowed_identities/); verified witnesses, not maxima |

The full sentence for each is in the header and on the first page of
`MASTER_CATALOG.md`. A regime a merge introduces is registered at the **end** of
that order, i.e. as the weakest claim — a merged witness can never outrank a
classification.

`discovery` is a different axis, read off a row's `sources`:

* `AI search` when an AI search campaign is among them and no
  classification stage run in this repository (the `n ≤ 38` classification, the
  rank-7 census), symmetry-SAT search, borrowed-identity search or community
  contribution is. The
  length-54 classification does not count against it: a Pareto point an AI
  search also found is `AI search`;
* `pre-existing` otherwise — including a class only the length-54
  classification has.

Sources carry no dates, so the tag says which finders are on record, not who
was first. A community circuit that improves a class adds a source; a duplicate
adds none. The tag says nothing about the literature — a published class can be
`AI search`; `citations` credits the literature.

## The distance, and what a number in that column means

`d_is_exact` is the field to read. When it is true, there is proved to be no
harmful fault below `d` **and** one is exhibited at it; the witness ships in
`d_witness` and is three lines to re-check. When it is false, `d` is a proved
floor and the tables print it as `≥d`. An unpinned distance is never quoted as a
measured one.

## Three implementations, on purpose

| module | what it does | pinned against |
|---|---|---|
| [`faultcore.py`](faultcore.py) | bit-level gate read-off, output structure, fault search at the scale the catalogue reaches (`n` to 2046, `k` to 373) | the literal `C(k,3)` / `C(n,4)` enumerations kept beside the verifier in [`verify_catalog.py`](verify_catalog.py), on every circuit small enough for both |
| [`glcanon.py`](glcanon.py) | the `GL(k,2)` class decision: tensor, invariants and a budgeted search | a literal enumeration of `GL(k,2)` on `Z_8` truth tables in [`tests/test_glcanon.py`](tests/test_glcanon.py) — every pair at `k = 2, 3`, random pairs at `k = 4`, and all 9,999,360 frames of `GL(5,2)` for a pair whose invariants agree |
| [`skcanon.py`](skcanon.py) | the `S_k` frame at widths where `k!` is not a loop | `classification/legacy/exhaustive_n38/dedup.py`, on 1,200 random gates |
| `factorylib/verification.py` | the repository's standalone verifier, sharing no code with any search or catalogue here | run as a third opinion on every circuit within its reach |

[`tests/`](tests/) re-does the core checks on the shipped file with its **own**
implementations rather than importing the verifier's, so a mistake has to be
made twice to go unnoticed. It adds what only a consumer can check: that the
catalogue holds every qualifying row of the legacy `n ≤ 38` classification and
rank-7 census catalogues and of the symmetry-SAT catalogue, and every Pareto point of the length-54 classification, that no other class with
`n ≤ 54` and `d ≥ 3` beats that frontier, that its filter is exactly "level 3, distance ≥ 2",
that the `discovery` tag and the Pareto points' citations follow their rules,
and that no class is in the table twice. The verifier's and merger's own suites are mostly **negative** — a
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
* **Hidden spectators.** The spectator and pseudo-output checks are made in the
  stored frame. A gate that, in some other CNOT frame, leaves an output untouched
  up to Cliffords (`T0·T1·CS01` is `T` on `x0 + x1` times a `CZ`) passes them;
  102 of the 1002 classes are of this kind. 80 are at `d ≥ 3`, 70 of them with
  `n ≤ 54`. The other 22 are at distance 2: three from the symmetry-SAT search,
  and 19 from the Borrowed Identities import. Those 19 are exactly the rows
  whose upstream catalogue marks them `essential_dim < k` (padded), apart from
  its `[[8,4,2]]`, which is refused as a pseudo-output. None is a Pareto point,
  since those outputs are spectator-free by construction. Each of the 70 is
  dominated by the Pareto point of its spectator-free output (tested).
* **Repairs.** A circuit rejected for a spectator, a pseudo-output or a
  redundant check wire is not fixed on the way in. Demoting a redundant output
  to a check, or deleting a check wire the others already decide, gives a valid
  circuit, but it is not the one that was submitted — so it is a search result,
  not a merge. Where this catalogue has itself made such a repair, the row says
  so in `columns_note` and the verifier requires that note wherever the shipped
  `N` is one no source published.
