# Legacy classification stages

The repository's own four exhaustive classification stages. All are
superseded by the exhaustive classification of generalised triorthogonal
protocols through `n <= 54` (Wills, Jain and Singh), whose Pareto frontier is
copied in [`../length54/`](../length54/). Nothing here is being extended.

| directory | complete window | shipped catalogues |
|---|---|---|
| [`exhaustive_n38/`](exhaustive_n38/) | every check rank, `n <= 38`, distance 3, from the Kasami–Tokura / Nezami–Haah support tables | 74 `S_k` classes ([`classification_n38.json`](exhaustive_n38/catalog/classification_n38.json)) |
| [`rank7_census/`](rank7_census/) | effective check rank `r <= 7`, `n <= 44`, distance 3, from the Gillot–Langevin `RM(3,7)` orbit table | the 21 T-count-5 frontier classes ([`census_r7.json`](rank7_census/catalog/census_r7.json)) and the complete table of 1201 `S_k` classes ([`sk_classes_r7.json`](rank7_census/catalog/sk_classes_r7.json)) |
| [`n40/`](n40/) | every check rank, `n = 39, 40`, distance 3, from the complete affine classification of length-40 no-repeated-column unital triorthogonal spaces | 319 `S_k` classes with their minimum-`a3` witnesses ([`classification_n3940.json`](n40/catalog/classification_n3940.json)) and the combined 393-class `n <= 40` table ([`classification_upto_n40.json`](n40/catalog/classification_upto_n40.json)) |
| [`n48/`](n48/) | `n = 41..48`, distance 3, from the length-42, 44, 46 and 48 tables and `RM(3,7)` — complete only where its README says so (`n = 47, 48` are partial) | 4,207 `S_k` classes ([`classification_n41_48.json`](n48/catalog/classification_n41_48.json)) and the combined 4,600-class `n <= 48` table ([`classification_upto_n48.json`](n48/catalog/classification_upto_n48.json)), both marked `partial` |

Each directory's README describes its pipeline, completeness argument and
results; `theory/02_classification.md` gives the theory.

## Why they are kept

- **Reproducibility.** They are the stages this repository ran itself, with
  their code, inputs, result passes and certificates. The test suites of
  `exhaustive_n38/` and `rank7_census/` run under `verify_repo.py`; `n40/` and
  `n48/` have their own suites and verifiers (`verify40.py`, `verify48.py`).
- **Provenance.** The master catalogue credits the classes of the first two to
  the length-54 classification (regimes `exhaustive classification n<=54` and
  `... (Pareto point)`), and its rows' `sources` cite
  `classification_n38.json`, `census_r7.json` and `sk_classes_r7.json` at
  these paths. `master_catalog/tests/test_master_catalog.py` opens those files
  to check each citation and that every qualifying row of the first two is held.
  The `n40/` and `n48/` catalogues are not merged into the master catalogue.
- **Pinned primitives.** `master_catalog/tests/test_master_catalog.py`,
  `master_catalog/tests/test_skcanon.py` and `tests/test_sk_agreement.py` check
  other code against the `S_k` key in
  [`exhaustive_n38/dedup.py`](exhaustive_n38/dedup.py). `n40/` imports the
  first two stages' input tables and the census's orbit iterator, and checks its
  classes against their catalogues; `n48/` imports the census's orbit-table
  parser and `n40/`'s marking, classifier and catalogue helpers, and extends
  `n40/`'s combined table.

## Class keys differ from the master catalogue

All four directories key a class on `(n, k, gate)` up to **`S_k`**: permutations of
the output qubits only. The master catalogue keys a row on `(n, k, d)` and the
gate's **`GL(k,2)`** class, which is invertible CNOT changes of the output basis
with diagonal Clifford corrections. The length-54 classification identifies
outputs under the same CNOT+S equivalence. `GL(k,2)` is coarser, so a count of
`S_k` classes here is not a count of master-catalogue rows. For example, the 21
T-count-5 frontier classes of the census are 2 master-catalogue rows (the
`[[43,k,3]]` rows with T-count 5). The census documents' count of 13 "under
`GL(k,2)`" uses the `F_2` truth-table relation, which
[`theory/02_classification.md`](../../theory/02_classification.md) explains is
not the magic-state relation.
