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
| [`master_catalog_large.json`](master_catalog_large.json) | the rows whose circuits are too long to store as columns, each with the rule that rebuilds them (see [The large file](#the-large-file)) |
| [`constructions.py`](constructions.py) | those rules: from a construction to its columns, in a fixed order, and the digest that pins them |
| [`MASTER_CATALOG.md`](MASTER_CATALOG.md) | a human-readable **view** of it — generated, never hand-edited |
| [`verify_catalog.py`](verify_catalog.py) | re-derives every row of the JSON from its columns |
| [`merge_results.py`](merge_results.py) | verifies new results to the same bar and merges them in |
| [`catalogfile.py`](catalogfile.py) | reading, writing and rendering the catalogue files; no verification logic |
| [`attribute_classification.py`](attribute_classification.py) | credit a classification catalogue on the rows it certifies -- provenance only, no circuit field is touched; needed because a class first merged from a search and later covered by a classification is a `duplicate` to `merge_results.py`, which changes nothing |
| [`faultcore.py`](faultcore.py), [`glcanon.py`](glcanon.py), [`skcanon.py`](skcanon.py), [`gatelabels.py`](gatelabels.py) | the primitives: fault search, the `GL(k,2)` class decision, the `S_k` frame, reading a claimed gate string |
| [`errorcoeff.py`](errorcoeff.py) | the leading error coefficient `A_d`, counted exactly by the MacWilliams identity and by enumeration |
| [`records.py`](records.py) | which rows are records under the owner's rule, direct sums included (see [Records](#records)); nothing stores the verdict, so it cannot go stale |
| [`clifford.py`](clifford.py) | the Clifford correction a circuit needs, the rotation powers that avoid it (or the proof that none do), and a direct evaluation of the logical action |
| [`migrations/`](migrations/) | the one-off scripts that made structural changes to the file (keying on `GL(k,2)` classes, citations, distance certificates, the length-54 classification, source paths, header wording, the distance-2 floor and the Borrowed Identities import, the Clifford corrections, the transversal-T codes), kept so each can be re-run and read |
| [`reduced_degree_cache.json`](reduced_degree_cache.json) | memoised reduced-degree bounds, so re-verifying a `k = 5, 6` row is a lookup rather than a ~100 s re-search |
| [`tests/`](tests/) | an independent re-derivation of the shipped file, plus the verifier's and merger's own suites |

```bash
.venv/bin/python master_catalog/verify_catalog.py            # all rows of both files, plus the file-level checks (~60 min)
.venv/bin/python master_catalog/verify_catalog.py --changed  # only the rows that differ from HEAD, plus the file-level checks (seconds)
.venv/bin/python master_catalog/verify_catalog.py --file main   # every row of the main file only (~35 min); --file large for the other (~25 min)
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

## The large file

Some circuits are stored as the rule that builds them, to keep
`master_catalog.json` under GitHub's recommended 50 MB. The Borrowed Identities
large sweep has two-group circuits of up to 65,534 rotations, and storing the
127 longest would take the file to about 99 MB, at GitHub's 100 MB hard limit.
The larger unified search added 478 more, from 1,026 to 262,142 rotations;
their columns are short enough one by one, but together they would take the
file past 50 MB. Such a row lives in [`master_catalog_large.json`](master_catalog_large.json). It has
every field of a row of the main file except `columns`, plus

- `construction`, the rule that builds the columns. The two-group rule is
  `{"family": "two-group", "k": k, "N": N, "s_total": a, "s_O": b}`, and
  [`constructions.py`](constructions.py) defines it from scratch: one `T` on
  `A ∪ B` for every set `A` of outputs and non-empty set `B` of checks with
  `|A| = 0` or `|A| ≡ 1 (mod b)`, and `|A| + |B| ≡ 1 (mod a)`. The columns
  come out in one fixed order, which `d_witness` and `rotation_powers` count
  in. Since 2026-11-07 there are six more families, each built by its own
  module and kept to the same order: `san-jose-grs` and `san-jose-curve`
  ([`construction_sanjose.py`](construction_sanjose.py), San-José's
  construction from an outer code over GF(2^m), arXiv:2609.08203), and
  `punctured-rm`, `punctured-weighted-rm`, `ccz-frame` and `four-block`
  ([`construction_rm.py`](construction_rm.py): Haah and Hastings's punctured
  RM(r, m), the same on Wills's weighted Reed–Muller codes, arXiv:2608.24000,
  the CCZ frame on F_2^(3q), and the four-block family). The large file's
  header describes every field of each. Each module also holds the check of
  its family's distance theorem from the columns, which
  [`theorem_certificates/`](../theorem_certificates/README.md) runs. A last family, `explicit`, is no rule at all:
  the columns themselves, compressed with zlib and written in base64, in the
  order they were stored. It holds the four gamma frontier rows from `n = 1675`
  to `1715` (4.3 MB of columns) and the 18 transversal-T rows from
  `[[1301,1,21]]` to `[[3239,1,31]]` (3.8 MB), moved there on 2026-11-07 by
  [`explicit_storage_2026_11_07.py`](migrations/explicit_storage_2026_11_07.py)
  and [`explicit_long_rows_2026_11_07.py`](migrations/explicit_long_rows_2026_11_07.py)
  when the imports of that day took the main file toward 50 MB, and then every
  main-file row over 200 kB of compact JSON
  ([`explicit_large_rows_2026_11_07.py`](migrations/explicit_large_rows_2026_11_07.py)).
- `columns_sha256`, the SHA-256 of those columns as compact JSON. It pins the
  circuit independently of the code that builds it.

`rotation_powers` is written as one digit per column there, the power of `T`
the column runs at (`1`, `3`, `5` or `7`). The main file's header (scope,
regimes, references, …) applies to these rows too; the large file carries only
a description of its encoding and its own `n_classes`.

[`catalogfile.load_all`](catalogfile.py) reads both files and rebuilds each
large row's columns, so the verifier, the merger and the website see the same
fields on every row and treat them alike. `write_all` writes them back apart,
and `write` refuses a large row rather than put its columns into the main
file. A result can be merged as a `construction` in place of `columns`.

The phase check of item 9 below evaluates every one of the `2^N` inputs on
the circuits of this file with `N ≤ 16`, and every input of weight at most 3
on the 17- and 18-wire ones.

## What is in it

**2716 distinct `(n, k, d, GL(k,2) gate)` classes**, 869 of them in the large
file. 1323 are at distance 2, and 229 are at `d ≥ 3` with `n ≤ 54`. Widths run
`k = 1..974`, injection counts `n = 8..262142`, and distances `d = 2..40`.
The sweep here proves `d = 2..7`. On 186 rows `d` is a certified bound, from
`d = 4` to `d = 40`, each backed by a theorem or exhaustive-search record in
this repository, and on 33 of them (`d ≥ 13`) it is a lower bound only. Every
certificate in the file is now the row's `d`.

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
explicit fault of exactly that weight (`d_upper`, `d_witness`). Through
`[[1011,1,19]]` the folder proves every input distance the doubling theorem
needs, so the paper's distance is the row's `d` (see
[The distance](#the-distance-and-what-a-number-in-that-column-means)); the 18
codes from `[[1301,1,21]]` on keep the sweep's floor as `d`.
[`migrations/gong_triply_even_2026_10_30.py`](migrations/gong_triply_even_2026_10_30.py)
merged four shorter codes of the same kind from a note by A. Gong
([`gongaa/RM127`](https://github.com/gongaa/RM127/tree/main/triply-even)):
`[[177,1,9]]`, `[[271,1,11]]`, `[[401,1,13]]` and `[[559,1,15]]`, her doubly
even self-dual `[[41,1,9]]` and `[[65,1,13]]` codes doubled onto `[[95,1,7]]`.
They carry their distances the same way.
[`migrations/gong_doubled_2026_10_30.py`](migrations/gong_doubled_2026_10_30.py)
merged eight more, built here: her `[[559,1,15]]` doubled on with the paper's
Table I inputs, `[[761,1,17]]` to `[[3195,1,31]]`, each 16 qubits shorter than
the Table I code of the same distance.

**Distances from tropidist.**
[`migrations/tropidist_certificates_2026_11_06.py`](migrations/tropidist_certificates_2026_11_06.py)
records what the exact solver tropidist (Cheng, Guo and Pan,
arXiv:2611.08247) certifies on the 62 rows this folder did not pin; the
results and how they were obtained are in
[`../tropidist_certificates/`](../tropidist_certificates/README.md). Eleven
rows near `n = 900` (`901.123.6.a` to `912.112.6.a`) became exact at `d = 6`
with this folder's own proof, since tropidist found a fault at their proved
floor. Eighteen more carry its result as a certificate: an exact distance on
eleven of them, from 4 to 13, a fault of weight 4 now stored on three of those,
and `d ≥ 7` on four.

**The Zaratan runs.**
[`migrations/zaratan_certificates_2026_11_07.py`](migrations/zaratan_certificates_2026_11_07.py)
records the runs of tropidist and of a meet-in-the-middle kernel made on the
UMD cluster Zaratan and on a laptop on 6 November 2026
([`../zaratan_certificates/`](../zaratan_certificates/README.md)):
`937.87.7.a` at `d = 7`, `742.36.8.a` and `959.65.8.a` at `d = 8`, `988.36.7.a`
at `d = 7`, `998.26.8.a` at `d ≥ 8`, and a second proof of the doubling
theorem's value on five transversal-T rows.

**Distances that rest on a certificate.**
[`migrations/distance_policy_2026_11_07.py`](migrations/distance_policy_2026_11_07.py)
made the certified bound the distance on 31 rows, where an evidence file the
repository is sure of states it, and relabelled them: `177.1.7.a` became
`177.1.9.a`, for example, and keeps the old label in `former_labels`.

**The second round of 7 November 2026.**
[`migrations/doubled_qr_distances_2026_11_07.py`](migrations/doubled_qr_distances_2026_11_07.py)
gave the 18 doubled codes from `[[1301,1,21]]` to `[[3239,1,31]]` the doubling
theorem's distance, with the Table II distances of Jain and Albert as inputs
(the length-168 one, 24, is now proved here by
[`../transversal_t_codes/min_distance.py`](../transversal_t_codes/min_distance.py)),
and relabelled them: `2017.1.3.a` became `2017.1.25.a`, for example.
[`migrations/round2_evidence_2026_11_07.py`](migrations/round2_evidence_2026_11_07.py)
wrote the records of [`../round2_certificates/`](../round2_certificates/README.md):
faults that make `935.89.7.a`, `936.88.7.a` and `998.26.8.a` exact, more
evidence on rows such as `599.1.15.a` and `988.36.7.a`, exact `A_d` counts,
and `d = 6` on the row now labelled `1715.287.6.a`.
[`migrations/sanjose_theorem_2026_11_07.py`](migrations/sanjose_theorem_2026_11_07.py)
checked San José's theorem (arXiv:2609.08203) on the columns of two gamma
frontier rows, so `756.32.6.a` became `756.32.9.a`.
[`migrations/research_faults_2026_11_07.py`](migrations/research_faults_2026_11_07.py)
made `218.5.7.a` and `708.58.6.a` exact with faults the research found, and
[`migrations/import_counts_2026_11_07.py`](migrations/import_counts_2026_11_07.py)
stored exact `A_d` counts from the research's tools on imported rows that
`errorcoeff.py` cannot count.
[`migrations/berardini_reference_2026_11_07.py`](migrations/berardini_reference_2026_11_07.py)
added Berardini et al. (arXiv:2412.08586), whose `[[753,1,17]]` came in that
day, and
[`migrations/reframe_93_3_5_2026_11_07.py`](migrations/reframe_93_3_5_2026_11_07.py)
stored `[[93,3,5]]` in the output frame where its gate is `T0·T1·T2`. The
searches imported that day took the catalogue from 2114 to 2711 classes.
Later that day, five one-step shortenings of held rows came in from the
descent search (`176.1.8.a`, `255.84.3.a`, `255.11.5.a`, `254.6.6.a` and
`510.84.6.a`), taking it to 2716;
[`migrations/store_217_7_7_2026_11_07.py`](migrations/store_217_7_7_2026_11_07.py)
stored the `[[217,7,7]]` circuit with the smaller `A_7` (973 against 1,034,
each counted by two programs in [`../round1_certificates/`](../round1_certificates/README.md));
[`migrations/credit_2026_11_07.py`](migrations/credit_2026_11_07.py) credited
`737.1.17.a` to Berardini et al. and Gong;
[`migrations/construction_references_2026_11_07.py`](migrations/construction_references_2026_11_07.py)
added San-José's and Wills's papers to the references, named in the regime
sentences of the rows built from their constructions, which stay credited to
the AI searches; and
[`migrations/record_wording_2026_11_07.py`](migrations/record_wording_2026_11_07.py)
took "undominated" out of the 84 release San-José rows' provenance (see
[Records](#records)).

**Clifford corrections.** Every row says what its circuit needs besides the
rotations to be exactly its gate (`clifford_correction`), and whether running
some rotations as `T³`, `T⁵` or `T†` makes that unnecessary
(`rotation_powers`). 42 classes need nothing, 1819 need only powers, and 855
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

**The unified borrowed-identity search.** In October 2026 the upstream
repository published the tables of one unified search.
[`migrations/borrowed_identities_unified_2026_10_26.py`](migrations/borrowed_identities_unified_2026_10_26.py)
merged the 792 level-3 circuits
[`../borrowed_identities/export_unified.py`](../borrowed_identities/export_unified.py)
rebuilt from them: 250 new classes, 187 already held, and 355 pseudo-outputs
refused, 351 of them the Clifford-padding circuits. New classes are credited to
the paper, and held classes keep their credit. The large sweep is taken up to
`n = 4095` there; above that it would take this file to about 99 MB, at
GitHub's 100 MB hard limit, so its 127 longer circuits, up to `n = 65534`, went to the large file
as two-group constructions:
[`migrations/borrowed_identities_large_2026_10_26.py`](migrations/borrowed_identities_large_2026_10_26.py)
merged them, all 127 new classes credited to the paper.
To stay under GitHub's 50 MB advisory size, the integer lists in this file
have been written without a space after the comma (`[0,1,3]`) since then.

**The larger unified search.** On 27 and 28 October 2026 the upstream
repository ran the two-group and gluing stages of the unified search up to
`k = 12` outputs and `N = 18` wires.
[`../borrowed_identities/export_large_unified.py`](../borrowed_identities/export_large_unified.py)
rebuilt and checked the 1,254 distance-2 rows of its level-3 table, and
[`migrations/borrowed_identities_large_unified_2026_10_28.py`](migrations/borrowed_identities_large_unified_2026_10_28.py)
merged them: 684 new classes credited to the paper, 559 already held (they keep
their credit), and 11 two-group circuits refused as pseudo-outputs, the
`[[8,4,2]]` among them. Of the new classes, the 214 gluing circuits and
two-group circuits of at most 1,023 rotations are stored as columns here. The
other 470 are two-group constructions in the large file. Columns up to 4,095
rotations, the bound the October 26 import used, would have taken this file
past 50 MB. The table's other 37 rows are single-output circuits at distance 3
or more. The exporter measured all 37 at exactly `d = 3`, 25 of them where the
table gives only `d ≥ 3`, and
[`migrations/borrowed_identities_large_unified_d3_2026_10_28.py`](migrations/borrowed_identities_large_unified_d3_2026_10_28.py)
merged them the same way: 13 new classes, from `n = 65` to `n = 131071`, 8 of
them in the large file, and 24 already held.

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
  their credit. The four codes doubled from A. Gong's self-dual codes are
  credited to her note (`gong2025triply`). The eight codes built here by
  doubling her `[[559,1,15]]` with the paper's inputs cite both the paper and
  her note. `737.1.17.a`, Berardini et al.'s Theorem 12 applied to her
  `[[559,1,15]]` by the catalogue's AI search, cites Berardini et al. and her
  note, and its source says the search made it.
* **A construction from a paper, the instance from an AI search.** The rows
  the AI searches built from San-José's GRS construction (arXiv:2609.08203)
  and from Wills's parent codes (arXiv:2608.24000) are credited to the search
  (`jain2026symmetry`, `discovery` `AI search`). The two papers are in the
  header's references (`sanjose2026asymptotically`, `wills2026improved`) and
  are named in those rows' regime sentences; the website shows them beside the
  provenance, not as the original source (the owner's decision of
  7 November 2026).
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
| `d` | verified fault distance: **exact** if `d_is_exact`, otherwise a proved **floor**. The lower bound is the sweep of `verify_catalog.py`, or a certificate where the row carries `d_sweep_floor` (see [The distance](#the-distance-and-what-a-number-in-that-column-means)) |
| `level` | 3 throughout this catalogue |
| `columns` | the circuit: one qubit-support list per rotation, sorted and duplicate-free |
| `gate` | the deposited output gate, as a monomial string |
| `gate_human` | the same gate as `T`/`CS`/`CCZ` factors |
| `sk_key` | the `S_k` canonical monomial set, or `null` when the `k!` minimisation was not proved (then `sk_key_note` says so) |
| `sk_canonical_frame` | whether the columns are shown in that canonical frame |
| `sk_fingerprint` | a permutation-invariant fingerprint of the gate |
| `d_is_exact` | `true` iff the proved lower bound `d` met a witness **at** `d` |
| `d_upper` | the weight of an explicit harmful fault, or `null` |
| `d_witness` | that fault, as column indices into this row's `columns` |
| `A_d` | the number of faults of weight `d` that the checks accept and that damage the output, so the output error is `A_d p^d` to leading order: `35` for the 15-to-1, `28` for the 8-`T` `CCZ` factory. Counted exactly by [`errorcoeff.py`](errorcoeff.py), or, where neither of its methods reaches, by another program whose record `A_d_evidence` names; `null` on a floor, where it is undefined, and where no count exists |
| `t_count` | exact minimal level-3 T-count, or `null` with `t_count_note` |
| `poly_degree` | CNOT-frame-reduced phase-polynomial degree, or `null` with a note |
| `effective_width` | rank of the output rows modulo the check span; must equal `k` |
| `clifford_correction` | `{"S": [[wire, p], ...], "CZ": [[wire, wire], ...]}`: the diagonal Clifford to apply after the rotations and before the checks are measured, so that the accepted action is **exactly** `gate`, with `T = diag(1, e^{iπ/4})`, `CS = diag(1,1,1,i)` and `CCZ`. `S^p` for `p` = 1, 2, 3 is `S`, `Z`, `S†`. Unique; derived by the weight expansion of Bravyi and Haah (2012) |
| `rotation_powers` | `[[column, power], ...]`: run those rotations as `T^power` (3, 5 or 7, and `T⁷ = T†`) and the rest as `T`, and no correction is needed. `[]` when none is needed anyway; `null` when no choice of powers avoids `S` or `CZ` gates. Not unique: a list is checked by evaluating the logical action at those powers, and `null` is re-proved by solving the `Z_4` system |
| `regimes`, `discovery`, `strongest_claim`, `sources` | provenance |
| `relabelled_into_canonical_frame` | provenance too: whether the ingest permuted the columns on the way in. A self-contained row cannot prove or refute it — the source frame is not stored — so the verifier checks its type and nothing else |
| `citations` | provenance too: keys of the header's `references` map crediting the class. The verifier checks that every key resolves, that a row cites at least one work and none twice; which works are credited is a curation decision |
| `d_certified`, `d_certified_is_exact`, `d_certified_source` | a distance certified by a theorem or by another program, exact or a lower bound, and who proved it. Optional |
| `d_sweep_floor` | only on a row whose `d` rests on its certificate: the floor the sweep itself proves, below `d` |
| `d_certified_evidence` | `[{"file", "method", "tool"}, ...]`: evidence files in this repository, each holding a record for this circuit, bound by the SHA-256 of its columns, with `method` `theorem` or `exhaustive search`. Required when `d` rests on the certificate |
| `former_labels` | the labels the row had before its `d` changed; old citations of them still find it, and they are never handed out again |
| `A_d_evidence` | `[{"file", "tool"}, ...]`: evidence files in this repository, each holding a record for this circuit, bound by the SHA-256 of its columns, that counts exactly `A_d` harmful faults of weight `d`. Present where another program counted `A_d` (since 2026-11-07, [`round2_certificates/`](../round2_certificates/README.md)) |
| `construction`, `columns_sha256` | only on a row of the large file: the rule that builds `columns`, and the SHA-256 of those columns as compact JSON |
| `catalog_label` | the row's public name, `n.k.d.x` (e.g. `15.1.3.a`): `d` is the row's distance, and the letters (`a`…`z`, then `ba`, `bb`, … as LMFDB numbers its classes) count the classes at that `(n, k, d)` in the order they entered the catalogue. `merge_results.py` gives a new class the next unused letter, and an improvement keeps the label. A label changes only when the row's `d` does, and the old one stays in `former_labels`; a label is never reused. The verifier checks the format and that no two rows share one. It is also the address of the class's page on the website |

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
   when `d_is_exact`, `d_witness` is re-checked against the true syndromes, by
   `faultcore` and by the XOR of the wire masks. On a row whose `d` rests on a
   certificate the sweep covers the weights below `d_sweep_floor`, and the
   certificate must equal `d`, name its source, and have evidence files that
   exist in the repository, hold a record of the stated method and tool for
   this circuit's SHA-256, and state exactly `d`.
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
10. **The error coefficient** `A_d`, counted again: the accepted faults of
    weight `d` less the harmless ones, each by the MacWilliams identity (from
    the `2^rank` words of the row space) or by enumeration, whichever is
    cheap. Where the direct enumeration of the harmful faults also finishes,
    it must give the same number. A floor carries `null`. An exact row
    carries `null` only where no count exists: where the recount here cannot
    reach, `A_d` may come from another program, and then `A_d_evidence` must
    name a record of exactly that count, at weight `d`, bound to this
    circuit by the SHA-256 of its columns. Wherever the recount reaches, it
    must agree whatever the evidence says.
11. **The construction**, on a row of the large file: the rule is well formed,
    agrees with the row's `k` and `N`, rebuilds exactly the columns every
    check above read, and their SHA-256 is the row's `columns_sha256`. The
    large file itself must be byte for byte what `catalogfile.write_all`
    writes for its rows.

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
| `columns` | **required**, unless `construction` is given. One list of qubit indices per π/4 rotation |
| `construction` | in place of `columns`, for a circuit too long to store: a rule [`constructions.py`](constructions.py) rebuilds the columns from. An accepted row keeps it and goes to the large file |
| `n` | optional; checked against `columns` |
| `d` | optional **claim**. Never believed — see below |
| `gate` | optional **claim**, as monomials or a `T`/`CS`/`CCZ` string |
| `t_count`, `poly_degree` | optional **claims**, compared where the exact recomputation is feasible |
| `regime` | optional; how the result was found, in a few words (see [the regimes](#the-regimes-and-why-they-stay-apart)). Default `merged results` |
| `strength` | optional; what a row from a **new** regime means, one sentence |
| `discovery` | optional; `AI search` (default) or `pre-existing` |
| `citations` | optional; keys of the header's `references` map. Omitted, an **accepted** row is credited to the length-54 classification and the symmetry-and-AI report when `n ≤ 54` and `d ≥ 3`, and to the report alone otherwise. An improvement or a duplicate adds only the citations the record **names** — a held class keeps the credit it was given, so a class credited to a published work alone is not re-credited because a search found it again |
| `label`, `provenance`, `origin`, `file`, `notes` | optional provenance strings — inert |
| `certificate` | optional: a distance bound proved where the sweep cannot reach, `{"d", "exact", "source", "witness", "evidence"}`. It becomes the row's `d` (see below) |

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
   | `improved` | a class it had, with a better circuit. Where both circuits have an `A_d`, the new one must be no worse in both `N` and `A_d` and better in one. Where either `A_d` is `null`, the rule is fewest ambient qubits, then fewest columns, then the strongest proved distance, then a proved canonical frame. The new provenance is **appended** to `sources` |
   | `duplicate` | a class it had, with a circuit no better, or one with fewer wires and a larger `A_d` (or the reverse); the report lists the second kind as not merged. **Nothing about the circuit or its provenance changes** — not the columns, not `sources`, not `regimes` — which is what makes re-merging a file a no-op the second time. Only a citation the record explicitly names is added |
   | `rejected` | did not verify. The reason is printed, and the exit status is 1 |

Both files are then regenerated from the merged payload, deterministically, so
an unchanged catalogue is rewritten **byte-identically** and a real change shows
up as a minimal diff rather than a reformat of twelve megabytes. Regenerating
takes about two seconds; no existing row is re-verified by a merge. Afterwards,
`verify_catalog.py --changed` re-derives exactly the rows the merge added or
improved and re-runs the whole-file checks, in seconds.

### Guards on certified rows

An improvement is refused, with the row's label in the reason, when it would
lower the row's distance, drop a certificate the new circuit does not match,
or replace a floor `d ≥ x` by a circuit whose distance is exactly `x`. The
toggles search of 2026-11-06 found a 12-wire `[[2017,1,3]]`, exact at 3, that
the fewest-wires rule alone would have put in place of the row then labelled
`2017.1.3.a`, whose 511-wire circuit carried the certificate `d ≥ 25` beside
its floor of 3; `tests/test_merge_results.py` keeps it as a regression case.
Since that row became `2017.1.25.a`, the 12-wire circuit is a class of its own
at `d = 3`, and the test checks that the merge leaves the row alone. Two more guards protect rows whose `d` rests on
a certificate. The very circuit a row stores, submitted at another distance, is
refused, since changing a stored row's distance is a migration. A circuit whose
distance is only a floor is refused when a row with the same `n`, `k` and gate
class holds a larger certified distance, since the two may be one class.

### Records with a certificate

A record may carry
`"certificate": {"d": 16, "exact": false, "source": "...", "witness": null,
"evidence": [{"file": "path/in/repo.json", "method": "exhaustive search",
"tool": "..."}]}`. The evidence file holds `records`, each with `n`, `k`, `N`,
`columns_sha256` (`constructions.digest` of the columns), `lower_bound` and,
unless the file states them once at the top, `method` and `tool`. The merge
measures the distance as usual and then requires that the sweep found no fault
lighter than the bound, that the bound exceeds the sweep's floor, that the
witness (required when `exact` is true, of weight `d`) is harmful, and that the
evidence states exactly the bound for the circuit as stored. The digest is that
of the columns after the outputs are relabelled into the canonical frame, and a
refusal prints it. The row then has `d` equal to the bound, the sweep's floor
in `d_sweep_floor`, and the certificate's fields, and `verify_catalog.py`
checks it like every other certified row.

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
| `AI search: Reed-Muller flat-toggle local search` | the catalogue's own local search of 6 November 2026 over Reed–Muller flat toggles, started from catalogue rows (research/search/toggles/); verified witnesses, not maxima |
| `AI search: punctured RM(3,10) lift and regrowth` | RM(3,10) punctured at searched sets (Haah and Hastings's construction), from the catalogue's lift search of 6 to 7 November 2026; `d` = 7 or 8 by mitml sweeps run here (`round1_certificates/`) |
| `AI search: CCZ frame on RM(3,12)` | the CCZ frame with 55 disjoint CCZ triples, `d = 16` by the frame theorem checked from the columns (`theorem_certificates/`) |
| `AI search: punctured weighted Reed-Muller parents`, `AI search: weighted Reed-Muller parent on 11 variables` | Wills's weighted Reed–Muller codes (arXiv:2608.24000) punctured at searched sets, from the sparse-cells search of 6 November 2026 (`[[480,32,6]]`, `[[479,33,5]]`) and the weighted search of 7 November 2026 (`[[1842,206,7]]`, `[[1845,203,7]]`, `[[1893,155,8]]`, `[[1894,154,8]]`, `d = 8` by mitml sweeps and the fibre theorem) |
| `AI search (gamma frontier): San José GRS construction`, `AI search: San José construction beyond the release` | San-José's construction (arXiv:2609.08203): the gamma frontier release's records, and circuits of the same construction the catalogue's own searches built; `d` from his theorem, its hypotheses checked from the columns (`theorem_certificates/`), exact where a fault of that weight is known |
| `AI search: four-block distance-3 factories` | punctured four-block parents at `d = 3` from the catalogue's second-round strategist and four-block searches; low `A_3` rather than new `(n, k)` |
| `AI search: small distance-5 and 6 factories` | three small factories at `d = 5` and 6 from the catalogue's second-round search, `[[93,3,5]]`, `[[127,9,5]]` and `[[128,7,6]]`; the sweep here proves each distance |
| `Vuillot-Breuckmann pin codes`, `Bravyi-Haah distance-2 family`, `Campbell-Howard distance-2 families`, `Berardini et al. doubling` | published factories the catalogue lacked, rebuilt by its second-round search from the constructions their papers give (arXiv:1906.11394, arXiv:1209.2426, arXiv:1606.01904, arXiv:2412.08586) and credited to those papers |
| `AI search: punctured pin codes` | the same construction with a choice the search made: puncture sets of pin codes it found |
| `Berardini et al. doubling of Gong's code` | Berardini et al.'s doubling onto A. Gong's `[[559,1,15]]`, which the catalogue's second-round AI search made (`737.1.17.a`); credited to both works and tagged `pre-existing`, as the Jain–Albert doublings of Gong's codes are, with the search named in its provenance |
| `AI search: symmetric CP-SAT search n<=127`, `AI search: punctured triply even cyclic codes`, `AI search: descent from catalogue rows` | the catalogue's second-round small-factory searches of 7 November 2026: a symmetric CP-SAT search, punctured extended triply even cyclic codes, and shortening and output restriction of held rows (credited also to the parent row's works); each row's distance is the sweep's or a mitml sweep run here (`round1_certificates/`) |
| `AI search: pin codes with searched relations` | quantum pin codes of Vuillot and Breuckmann (arXiv:1906.11394) whose box-sum relations, and punctures where there are any, the catalogue's small-pin search found (7 November 2026): CCZ rows at `d = 4` from `[[112,27,4]]` to `[[496,164,4]]`, `T` rows at `d = 4` and 6 |
| `AI search: even CCZ construction` | the catalogue's small-d4 search (7 November 2026): `d = 4` factories of its even CCZ construction, whose punctured parents follow Haah and Hastings (arXiv:1709.02832, Sec. 2.2), 20 CCZ rows from `[[94,16,4]]` to `[[240,74,4]]`, `T` and `CS` rows |
| `AI search: invariant radical growth` | the catalogue's small-radical search (7 November 2026, after small-d56): exact invariant radical growth on triorthogonal BCH-type check codes, 26 rows from `n = 93` to 512 at `d` from 5 to 8 in the `T`, `CS`, `CCZ` and mixed classes; it also gave the `T` frame in which `[[93,3,5]]` is stored |

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

The lower bound is proved one of two ways. On most rows it is the sweep of
`verify_catalog.py`. Since 2026-11-07 (the owner's decision, applied by
[`migrations/distance_policy_2026_11_07.py`](migrations/distance_policy_2026_11_07.py)),
a row may instead rest on a certificate the repository is sure of: the
doubling theorem of Jain and Albert along a chain whose every input distance
is proved in [`../transversal_t_codes/`](../transversal_t_codes/README.md), or
an exhaustive search by tropidist or by the meet-in-the-middle kernel of the
Zaratan runs. Such a row carries `d_sweep_floor`, what the sweep alone proves,
and `d_certified_evidence`, its evidence files. A certificate the repository
cannot check (the doubling theorem where it needs the distances of the
extended QR codes of length 168, 192 or 200, and two gamma frontier records)
stays in `d_certified` beside the sweep's `d`.

## Records

A row is a **record** when no other row of its gate class (`T` only, `CS`
only, `CCZ` only, mixed, or any gate) has `n' <= n`, `k' >= k` and `d' >= d`
with one of the three strict, and no direct sum of two or more rows of that
class reaches `n' <= n`, `k' >= k` and `d' >= d`. The direct sum of
`(n1, k1, d1)` and `(n2, k2, d2)` is `(n1 + n2, k1 + k2, min(d1, d2))`, and a sum
that only equals the row also takes the record away. This is the owner's rule
of 7 November 2026: a direct sum can be in the catalogue, but it is not a
record. [`records.py`](records.py) applies it to the rows as they stand, and
the website presents as best (its headline figures and the frontier staircase)
only records. No field of a row says that it is a record, so the verdict is
never stored where it could go stale; the regime sentences say what each
source proves, and most of them say "a verified witness, not a maximum". A
Pareto point of the length-54 classification is a statement about `n` and `N`
within one output class, not a record in this sense.

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
