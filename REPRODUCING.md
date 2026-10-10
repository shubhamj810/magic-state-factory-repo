# Reproducing the results

Every command below is launched from the repository root, and the paths in them
are root-relative -- `.venv/bin/python` included -- so they do not work unchanged
from elsewhere. What *is* independent of the working directory is the code: every
script resolves its data and its sibling modules relative to its own file, so
`/somewhere/else/.venv/bin/python /path/to/repo/classification/legacy/exhaustive_n38/build_catalog.py`
finds the right inputs. Only the shell paths need adjusting.

## 1. Create the environment

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

The dependency versions are exact pins. Use a fresh virtual environment rather
than an existing Conda base environment.

## 2. Verify the shipped state

```bash
.venv/bin/python verify_repo.py
```

The final line begins with `PASS:` and names the number of tests it discovered
and ran:

```text
PASS: all <N> tests in every repository suite ran, with no skips and no failures
```

Anything else — a failure, a skip, or a suite that collected no tests — is
reported as a failure and exits nonzero.

Seven of the ten suites check that the published results are right, the
Borrowed Identities import and the transversal-T codes among them. One tests
the community-contribution checker and one the website build. The tenth,
[`tests/`](tests/), checks what this repository would ACCEPT as a result: it
mutates every field of a real accepted artifact — a census certificate, a shipped
input pass, a catalogue row — and requires each mutation to be rejected, declared
harmless with a reason, or named as one that only a rerun could refute. See
[`tests/README.md`](tests/README.md).

## 3. Complete `n <= 38` classification (legacy)

This stage and the census in section 4 are legacy: the exhaustive length-54
classification ([`classification/length54/`](classification/length54/))
supersedes both, and they are kept for reproducibility and provenance (see
[`classification/legacy/README.md`](classification/legacy/README.md)).

Inputs are the classified supports in
[`nezami_haah_reps.py`](classification/legacy/exhaustive_n38/nezami_haah_reps.py).
`marking.py` turns every support and origin into a check parent. `classify.py`
exhausts compatible output frames in `R(C)/C`, verifies explicit circuits, and
writes one result file per pass when that pass finishes -- it does not
checkpoint, so an interrupted pass leaves nothing behind and is rerun from the
start. `build_catalog.py` performs global `S_k` deduplication, verifies the
retained witness for every class, and refuses to build unless the passes it
finds cover the whole window (see `validate_inputs`). A pass that hit a node
budget writes `complete: false` and exits nonzero, and the builder rejects it.

```bash
# Every length, output width through three (roughly two minutes on this machine)
.venv/bin/python classification/legacy/exhaustive_n38/classify.py \
  --kmax 3 --tag k3

# Width four away from the exceptional n=31 parent
.venv/bin/python classification/legacy/exhaustive_n38/classify.py \
  --ns 15 16 23 24 27 28 29 30 32 33 34 35 36 37 38 \
  --kmax 4 --tag k4_easy

# The remaining n=31 parents
.venv/bin/python classification/legacy/exhaustive_n38/classify.py \
  --ns 31 --kmax 4 --skip-classes 0 --tag k4_n31_rest

# The maximally symmetric n=31 parent, collapsed by GL(5,2)
.venv/bin/python classification/legacy/exhaustive_n38/hard_parent_n31.py --kmax 5

# Consolidate, re-verify, and plot
.venv/bin/python classification/legacy/exhaustive_n38/build_catalog.py
.venv/bin/python classification/legacy/exhaustive_n38/plot_landscape.py
```

Expected catalogue result:

```text
136 records read -> 74 distinct (n, k, S_k gate) classes
74/74 circuits independently re-verified
```

Re-running a pass reproduces its result file exactly except for the per-`n`
wall-clock `seconds` in `stats`, which naturally differ; the catalogue built from
those files ignores the timings, so `catalog/` is byte-stable across runs. Every
witness is written in its canonical output frame, so a row's stored columns
deposit exactly its stored `gate` string — the builder compares the two as
strings and aborts on any mismatch.

The generated files are
`classification/legacy/exhaustive_n38/catalog/classification_n38.json`,
`CLASSIFICATION_N38.md`, and `landscape_n38.{png,pdf}`.

### Independent row-space audit

`classify_rowspace.py` is a slower independent enumerator that uses the full
row space rather than `R(C)/C`. Nothing shipped depends on it; it exists so the
two enumerators can be compared:

```bash
.venv/bin/python classification/legacy/exhaustive_n38/classify_rowspace.py manifest
```

The fast test suite compares both algorithms on the small ladder. To run the
comparison over the whole ladder, split it with the `manifest`/`task`/`merge`
subcommands — sizing and measured costs are in
[`docs/SHARDING.md`](classification/legacy/exhaustive_n38/docs/SHARDING.md). No cluster
is needed for anything this repository ships.

## 4. Complete `r <= 7`, `n <= 44` census (legacy)

First verify the external orbit table. The orbit sizes must sum to exactly
`2^64`; this is the outer-enumeration completeness certificate.

```bash
.venv/bin/python classification/legacy/rank7_census/cli.py data-check
```

Interactive smoke run (deliberately incomplete):

```bash
.venv/bin/python classification/legacy/rank7_census/cli.py census \
  --class-index 306 --max-parents 2 --kmax 2 --allow-incomplete \
  --output /tmp/census_smoke.json
```

The output must say `complete=false`. Budget-limited or capped output is search
data and is never accepted as a classification certificate — so an incomplete
run exits 1, and `--allow-incomplete` is how this smoke run says that a partial
sweep is exactly what was wanted. Drop the flag and the same command exits 1,
which is what keeps a capped run from passing for a census in a cluster job.

Full cluster-scale census:

```bash
.venv/bin/python classification/legacy/rank7_census/cli.py census \
  --mode all --nmax 44 --kmax 4 --dedup symmetric \
  --node-budget 0 --orbit-budget 0 --checkpoint-every 1 \
  --output classification/legacy/rank7_census/results/census_r7_all.json
```

This visits all `71 x 128 = 9,088` marked geometries and may take many
core-hours. Writes are atomic and checkpointed. Only a final top-level
`"complete": true` supports nonexistence claims.

Rebuild the shipped frontier catalogue:

```bash
.venv/bin/python classification/legacy/rank7_census/build_catalog.py
```

## 5. Parent-check workflow

The parent tool reads either explicit points/columns or a factory from the
search catalogue:

```bash
.venv/bin/python parent_first/cli.py analyze \
  --factory 15,1,3 --node-budget 0

.venv/bin/python parent_first/cli.py target \
  --factory 47,3,3 --gate CCZ012

.venv/bin/python parent_first/cli.py gates \
  --factory 28,2,3 --kmax 2 --dedup symmetric
```

The three stages are `kappa` (legal quotient dimension), `mu` (largest
compatible subspace), and `tau` (largest width carrying the requested target
family). A budget hit always propagates `complete=false`.

Constructing a parent tabulates all `2^kappa` coset representatives, so parents
above `--max-kappa` (default 21) are refused immediately, naming their `kappa`.
`--factory 141,2,4`, `85,1,5` and `63,4,3` are the catalogued rows this rejects.

## 6. Symmetry-slot and ansatz-free SAT search

Run a slot search directly; there are no campaign wrappers:

```bash
.venv/bin/python symmetry_sat_search/slot_search.py \
  --k 1 --target T --geometry S4 --geometry C7 \
  --distance 3 --time 120
```

Geometry syntax is `S<number>` for a fully symmetric block and `C<number>` for
a cyclic block. Join blocks with `+`, for example `S3+C4`.

Run the ansatz-free entire-column-space search:

```bash
.venv/bin/python symmetry_sat_search/sat_search.py \
  --k 1 --N 5 --target T --distance 3 --level 3 \
  --backend cpsat --time 120 --output /tmp/sat_15_to_1.json
```

Run exact distance-four CEGAR within a slot geometry. `--time` is the CP-SAT
limit for ONE CEGAR iteration and up to 4,000 iterations may run, so bound the
whole search with `--deadline` unless you intend to leave it for days; on expiry
the geometry reports `DEADLINE` and the exit code is nonzero:

```bash
.venv/bin/python symmetry_sat_search/exact_d4.py \
  --k 1 --target T --geometry C9 --time 180 --deadline 3600
```

This geometry is genuinely hard: it was still unresolved after several minutes
on the machine these timings were measured on. `UNKNOWN`, `ITERCAP`, `DEADLINE`
and a `FEASIBLE` incumbent whose minimality was never proven all exit nonzero --
only `OPTIMAL` and `UNSAT` are answers.

Search for an entangled multi-monomial gate, in the notation the catalogues
print gates in (this is the shape of the catalogue rows whose `target` field is a
campaign descriptor rather than a named gate):

```bash
.venv/bin/python symmetry_sat_search/sat_search.py \
  --k 3 --N 6 --target-monomials 01+02 --distance 2 --level 3
```

Search output is experimental until an explicit circuit is deliberately added
to [`examples/found_factories.json`](symmetry_sat_search/examples/found_factories.json).
That single file is the complete record of the search examples.

Rebuild and independently verify the curated catalogue:

```bash
.venv/bin/python symmetry_sat_search/build_catalog.py
.venv/bin/python symmetry_sat_search/verify_catalog.py
.venv/bin/python symmetry_sat_search/symmetry_groups.py
.venv/bin/python symmetry_sat_search/rebuild_from_groups.py
```

Expected summaries are `57 factories, all verified`, `57/57 catalogue rows`,
`all regenerate: True`, and `57/57 factories rebuilt`.

## 7. The master catalogue

`master_catalog/master_catalog.json` is not regenerated from the other
catalogues: it is a permanent, checked-in collection, and rows only ever arrive
through `merge_results.py`. So what there is to reproduce is the VERIFICATION,
which reads nothing but the file itself:

```bash
.venv/bin/python master_catalog/verify_catalog.py            # every row, ~20 min on one core
.venv/bin/python master_catalog/verify_catalog.py --changed  # rows that differ from HEAD, seconds
```

Expected summary of the full run (`--rows 1-20` for a quick slice):

```text
PASS: <N> rows re-derived from their columns in <time>s -- gate, check
parities, distance (absence proved below d, presence witnessed at it), output
width modulo the check span, spectator and pseudo-output freedom, no check wire
whose syndrome bit the others already decide, T-count and reduced degree where
computable, the Clifford correction with the corrected logical action evaluated
(and simulated gate by gate on small circuits), the rotation powers that avoid
it or the proof that none do, and a circuit its own sources published or a note
saying why not,
and no two rows are the same GL(k,2) class, every row's regimes,
strongest_claim and citations resolve against the file's own header, and the
header itself is present, typed and counts the rows it has
```

Every number is re-derived from the explicit columns rather than copied, and
`master_catalog/tests/` re-derives the shipped file again with a second,
independent set of implementations. `MASTER_CATALOG.md` is a generated view of
the JSON and is byte-reproducible from it, which the same suite asserts.

To add results, write them to a file in the schema
[`master_catalog/README.md`](master_catalog/README.md) documents and run:

```bash
.venv/bin/python master_catalog/merge_results.py new_results.json --dry-run
.venv/bin/python master_catalog/merge_results.py new_results.json
```

Each incoming circuit is verified to the same bar as a shipped row --
`merge_results` imports `verify_catalog` and refuses anything the verifier would
not afterwards confirm -- then deduplicated against the catalogue, and the
report names every result as accepted, improved, duplicate or rejected. Merging
an empty file, or a file of circuits the catalogue already holds, rewrites both
files byte-identically. A merge re-verifies no existing row and takes seconds
plus the cost of verifying the new circuits; `verify_catalog.py --changed`
then re-derives exactly the rows it changed.

### Distance 2: the Borrowed Identities import

The distance-2 rows came in through one migration, from two inputs: the
circuits of S. Singh, C. Gidney and C. Jones's Borrowed Identities catalogue
(arXiv:2606.28518), rebuilt in [`borrowed_identities/`](borrowed_identities/),
and the distance-2 rows of the symmetry-SAT catalogue. To reproduce it:

```bash
.venv/bin/python borrowed_identities/export_circuits.py --check      # rebuild every circuit from the upstream code, ~35 s
.venv/bin/python -m unittest discover -s borrowed_identities/tests   # copy, circuits, distances, credit, ~2 s
.venv/bin/python master_catalog/migrations/distance_two_2026_10_07.py --dry-run   # seconds
```

The export prints `up to date`. Run against the catalogue before the
migration (`git show 990f259:master_catalog/master_catalog.json`), the
migration reports `179 accepted, 5 duplicate, 1 rejected` for the import and
`10 accepted, 7 duplicate, 2 rejected` for the symmetry-SAT rows. The one refused
import is the paper's `[[8,4,2]]`, a pseudo-output here. The two refused SAT
rows' classes are held anyway. Against the shipped catalogue every admissible
circuit is already held: `184 duplicate, 1 rejected`, `17 duplicate, 2
rejected`, and `1002 -> 1002 classes`.
[`borrowed_identities/README.md`](borrowed_identities/README.md) explains each
verdict and the credit.

### The transversal-T codes of Jain and Albert

The codes of S. P. Jain and V. V. Albert (IEEE JSAIT 6, 127 (2025),
arXiv:2408.12752) are built from the paper's doubling construction in
[`transversal_t_codes/`](transversal_t_codes/) and came in through one
migration:

```bash
.venv/bin/python transversal_t_codes/build_codes.py --check          # build and check all 17 codes, ~15 s
.venv/bin/python -m unittest discover -s transversal_t_codes/tests   # re-checks, small distances by enumeration, catalogue rows, ~1 min
.venv/bin/python master_catalog/migrations/transversal_t_codes_2026_10_10.py --dry-run   # ~4 min
```

The build prints `up to date`. Run against the catalogue before the migration,
the migration reports `15 accepted, 2 duplicate`: `[[15,1,3]]` and
`[[49,1,5]]` were held already. Against the shipped catalogue it reports `17
duplicate` and writes nothing. Most of its time is the distance sweep of the
`n = 805` and `n = 1011` codes.

### Clifford corrections

Every row's `clifford_correction` and `rotation_powers` were added by one
migration, which checks every row before it writes:

```bash
.venv/bin/python master_catalog/migrations/clifford_corrections_2026_10_10.py --dry-run   # ~1 min
```

Against the shipped catalogue it reports, for 1017 rows, `S, CZ: 456,
T-powers: 551, none: 10` and `nothing written`. `verify_catalog.py`
re-derives both fields on every row, evaluates each corrected circuit's
logical action, re-proves every `null` power list, and simulates the small
circuits gate by gate.

## 8. Community contributions and the agent context pack

Contributions arrive in any format and are converted by the maintainers into a
catalogue input file, which is checked against the master catalogue without
writing anything:

```bash
.venv/bin/python community_contributions/check_submission.py community_contributions/examples/bravyi-kitaev_15-to-1.json
```

The example is the Bravyi–Kitaev `[[15,1,3]]` protocol. The catalogue already
holds it, so its one verdict is `duplicate` and the exit status is 0.
[`community_contributions/README.md`](community_contributions/README.md) covers
the format, the exit codes and the maintainers' `--write` merge.

The context pack for agents ships a standard-library verifier with real
fixtures:

```bash
python3 agent_context/reference/verify_factory.py --selftest
```

Its `check_claims.py` re-derives the pack's prose figures from the
`magic-states-AI` corpus file `master_catalogue.jsonl`, which is not in this
repository. See [`agent_context/README.md`](agent_context/README.md).

## 9. Figures

```bash
.venv/bin/python theory/figures/landscape_all.py
```

Both figures read all three generated catalogues, so rebuild those first. They
are byte-stable: an unchanged catalogue regenerates an identical PNG and PDF, so
a modified figure file in `git status` means a result moved.

The written account of the results lives in [`theory/`](theory/) -- the notes
there are self-contained, and every number they quote is re-derived by the
commands above.

## Output hygiene

- `catalog/` contains publishable generated tables and figures.
- `results/` contains classification certificates or local scratch output.
- `symmetry_sat_search/examples/found_factories.json` is the sole curated
  source of search examples.
- Do not commit solver stdout, temporary campaigns, checkpoints, or partial
  runs. Store cluster-scale certificates externally with a checksum when they
  are too large for version control.
