# Magic-state factory classification and search

This repository contains reproducible code and explicit circuit data for
classifying and finding magic-state distillation factories. A factory is stored
as a list of parity-rotation columns: qubits `0..k-1` are logical outputs and
the remaining qubits are postselected checks. Its parameters `[[n,k,d]]` are
the number of noisy rotations, number of outputs, and circuit distance.

The central distinction is:

- A **classification** enumerates a complete window. A missing entry is a
  proved nonexistence result within that window.
- A **search catalogue** contains verified witnesses. A missing entry means
  only that no example is recorded here.

## Repository map

| path | purpose | main entry points |
|---|---|---|
| [`classification/exhaustive_n38/`](classification/exhaustive_n38/) | every distance-3 factory with `n <= 38`, all check ranks | `classify.py`, `hard_parent_n31.py`, `build_catalog.py`, `plot_landscape.py` |
| [`classification/rank7_census/`](classification/rank7_census/) | complete `r <= 7`, `n <= 44` census | `cli.py`, `rank7.py`, `build_catalog.py` |
| [`classification/length54/`](classification/length54/) | copy of the Pareto frontier of the exhaustive length-54 classification (Wills, Jain and Singh), which subsumes the windows above | `pareto_frontier.json` |
| [`parent_first/`](parent_first/) | analyse one check parent, target a gate, or enumerate all gates it carries | `cli.py` |
| [`symmetry_sat_search/`](symmetry_sat_search/) | symmetry-slot and ansatz-free SAT search; verified examples catalogue | `slot_search.py`, `sat_search.py`, `exact_d4.py`, `build_catalog.py` |
| [`master_catalog/`](master_catalog/) | the permanent collection: one table of every level-3, distance >= 3 factory held here, re-derived from columns | `verify_catalog.py`, `merge_results.py` |
| [`factorylib/`](factorylib/) | shared solver-independent parent model, verification, and gate metrics | imported by the four workflows |
| [`theory/`](theory/) | mathematical notes, result provenance, and cross-cutting figures | `01_factories_and_distance.md`, `PROVENANCE.md`, `figures/landscape_all.py` |
| [`tests/`](tests/) | what this repository would ACCEPT as a result: a mutation sweep over every acceptance boundary, and the exit-code contract | `mutation.py`, `test_certificate_boundaries.py` |

Generated catalogues are deliberately separate:

- [`classification_n38.json`](classification/exhaustive_n38/catalog/classification_n38.json): 74 `S_k`-deduplicated classes in the complete `n <= 38` window.
- [`census_r7.json`](classification/rank7_census/catalog/census_r7.json): the T-count-5 frontier from the complete `r <= 7`, `n <= 44` census.
- [`factories.json`](symmetry_sat_search/catalog/factories.json): 57 verified examples found analytically or by slot/SAT search.

Those three keep their regimes apart on purpose. When what you want is the
combined list rather than the distinction,
[`master_catalog/MASTER_CATALOG.md`](master_catalog/MASTER_CATALOG.md) is the
permanent collection: 804 distinct `(n, k, d, GL(k,2) gate)` classes -- the
three catalogues above, the 74 Pareto points of the length-54 classification
([`classification/length54/`](classification/length54/)) and every search
campaign merged in since -- each tagged with how it was found, credited to the
papers that state it, and re-derived from its own columns. It is checked in rather than rebuilt --
`master_catalog/verify_catalog.py` re-proves every row from the file itself,
and `merge_results.py` is the only way a row gets in.

## Setup

Use a fresh Python 3.12 environment: that is the only version the suite has been
run on here, so it is the only one claimed. The direct-dependency pins avoid the
NumPy/binary-extension ABI conflicts commonly caused by installing OR-Tools in
an existing Conda base environment.

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

## Verify the shipped repository

```bash
.venv/bin/python verify_repo.py
```

This runs every test suite in the repository, printing the number of tests it
discovered and ran: independent input-table checks, two classification paths on
the small ladder, exact circuit re-verification,
parent-filter tests, small solver optima, symmetry-group reconstruction, and --
in [`tests/`](tests/) -- a mutation sweep over the boundaries that decide which
search output may become a published result at all. A missing
or broken solver dependency, a skipped test, or a suite that collected nothing is
reported as a failure rather than hidden.

Each workflow directory also has a `selfcheck.py` that runs its own tests and
prints one plain-language verdict for that directory alone — useful after
changing something local:

```bash
.venv/bin/python classification/exhaustive_n38/selfcheck.py
.venv/bin/python classification/rank7_census/selfcheck.py
.venv/bin/python parent_first/selfcheck.py
.venv/bin/python symmetry_sat_search/selfcheck.py
```

To rebuild every inexpensive generated artifact:

```bash
.venv/bin/python classification/exhaustive_n38/build_catalog.py
.venv/bin/python classification/exhaustive_n38/plot_landscape.py
.venv/bin/python classification/rank7_census/build_catalog.py
.venv/bin/python symmetry_sat_search/build_catalog.py
.venv/bin/python symmetry_sat_search/verify_catalog.py
.venv/bin/python symmetry_sat_search/symmetry_groups.py
.venv/bin/python symmetry_sat_search/rebuild_from_groups.py
.venv/bin/python theory/figures/landscape_all.py
.venv/bin/python master_catalog/verify_catalog.py
```

See [`REPRODUCING.md`](REPRODUCING.md) for the exhaustive searches, expected
outputs, runtimes, and checkpoint rules.

The `n <= 38` classification and every verification, rebuild and figure above
run in minutes on a laptop; no cluster is required for any of them. The `r <= 7`
census is the exception and is cluster-scale: its 9,088 marked geometries take
many core-hours, which is why the maximality half of that result is a recorded
certificate rather than something this repository re-derives on demand. What
*is* local there is the outer enumeration — the orbit table's `2^64`
completeness identity and the geometry count — plus re-verification of every
shipped circuit.

## Headline certified results

- The `n <= 38` classification contains 74 distinct `(n,k,S_k gate)` classes,
  all with explicit circuits. No pure `CCZ` occurs, proving the distance-3
  lower bound `n >= 39` for `CCZ`. The largest genuine output width is `k=5`,
  occurring uniquely at `[[31,5,3]]`; no `k=6` factory exists in the window.
- In the complete `r <= 7`, `n <= 44` census, the maximum exact minimal
  T-count is 5, attained only at `n=43`, by 21 distinct `S_k` classes — every
  one with an explicit verified circuit.
- The search catalogue contains 57 explicit circuits, one per distinct circuit. Every row has its output
  gate and fault distance re-derived from columns, and every circuit can be
  regenerated from its stored automorphism group and column-orbit
  representatives.

## Deduplication convention

Classification rows use the `S_k` action: output-qubit permutations only. A
coarser `GL(k,2)` annotation is stored where relevant, but it is not the
catalogue key. This preserves distinct circuit output frames while removing
mere renamings. The formal discussion and regression examples are in
[`classification/exhaustive_n38/dedup.py`](classification/exhaustive_n38/dedup.py).

## Data and provenance

The Gillot–Langevin `RM(3,7)` orbit table is third-party data preserved
unchanged under [`classification/rank7_census/data/`](classification/rank7_census/data/).
Its checksum and the `2^64` orbit-sum completeness certificate are tested.
See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) and
[`theory/PROVENANCE.md`](theory/PROVENANCE.md).

Search provenance is retained per circuit in
[`symmetry_sat_search/examples/found_factories.json`](symmetry_sat_search/examples/found_factories.json).
Historical campaign scripts and raw stdout logs are intentionally not part of
the publishable repository; the stable search engines and every verified
explicit circuit are.
