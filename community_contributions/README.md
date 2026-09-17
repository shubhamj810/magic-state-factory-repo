# Community contributions

This directory is how people outside the project add magic-state distillation
factories to the [master catalogue](../master_catalog/). You send **one JSON
file** describing your protocols and who should be credited for them. The
maintainers re-derive every number from the explicit circuits with the
catalogue's own verifier, merge what verifies, and cite your work on every row
it adds.

## What is in scope

Anything the master catalogue's bar accepts:

* **level-3 outputs**: the accepted action on the outputs is a diagonal
  non-Clifford gate built from `T`, `CS` and `CCZ` factors;
* **fault distance `d ≥ 3`**;
* **an explicit circuit** for every protocol: the qubit support of each `T`
  (π/4 parity) rotation, with the outputs and the postselected checks declared.

Out of scope:

* level-2 (Clifford) or level-4 and higher outputs;
* distance-2 circuits;
* asymptotic families or constructions with no explicit circuit — send the
  members you want listed as explicit protocols instead;
* claims that cannot be checked from the file, such as a distance, gate or
  rate stated without the circuit it describes.

The verifier also refuses circuits that deposit phase on a check wire, repeat a
column, leave an output untouched (a spectator), count an output that is
another output plus a stabiliser (a pseudo-output), carry a check wire whose
syndrome bit the other checks already give, or declare wires no rotation uses.
It does not repair them. The full bar is under "Verifying" and "Merging new
results" in [`master_catalog/README.md`](../master_catalog/README.md).

## The submission file

A factory has `N` wires: wires `0..k-1` are the outputs and wires `k..N-1` are
postselected checks. Each column is one `T` rotation, and `n` is the number of
columns. Indices are 0-based throughout. [`TEMPLATE.json`](TEMPLATE.json) is a
file to copy and fill in. Every `<...>` value is a placeholder, and the checker
refuses the file while any placeholder is left.

| field | |
|---|---|
| `contributor.name` | **required.** The name you are credited under |
| `contributor.affiliation` | optional; printed after your name in each row's provenance |
| `contributor.contact` | optional; for the maintainers only, and never copied into the catalogue. A pull request makes it public, so leave it out if you would rather send it privately |
| `reference.key` | **required.** A citation key: 3–64 lowercase letters, digits, `_` or `-`, e.g. `surname2026firstword`. If the work is already listed under "References" in [`MASTER_CATALOG.md`](../master_catalog/MASTER_CATALOG.md), use that key and copy its entry exactly |
| `reference.short` | **required.** The label for the citation column, e.g. `Doe et al. (2026)` |
| `reference.full` | **required.** The full bibliographic line. For unpublished work, a line crediting you, e.g. `J. Doe, unpublished community contribution (2026).` |
| `reference.url` | optional. The `https` DOI or arXiv link of a **published** work, which the citation column links to. Leave it out for unpublished work |
| `method` | **required.** One or two sentences (at most 400 characters) on how the protocols were found |
| `terms` | **required.** The terms under which the protocols may be redistributed (see [Data terms](#data-terms)) |
| `protocols` | **required.** A non-empty list of protocols, each in one of the two forms below |

Each protocol gives its circuit in **exactly one** of two forms.

| columns form | |
|---|---|
| `k` | **required.** Number of outputs |
| `N` | **required.** Number of wires: the largest index used, plus one. Every wire must be used |
| `columns` | **required.** One list of wire indices per rotation |

| generator-matrix form (generalised triorthogonal) | |
|---|---|
| `generator_matrix_rows` | **required.** Strings of `0` and `1`, all of length `n`. The first `q` rows are logical and the rest are stabiliser rows |
| `q` | **required.** Number of logical rows |

A matrix becomes the factory with `k = q`, `N` = the number of rows, and
`columns[j]` = the rows with a `1` in column `j`. An all-zero column is refused;
delete it.

Both forms also take these optional fields:

| field | |
|---|---|
| `d` | claimed distance. It is measured, not trusted: a claim the measurement disproves rejects the protocol, and a claim below the measured distance is stored at the measured value |
| `gate` | claimed output gate, e.g. `T0.T1`, `CS01`, `CCZ012`, or monomials such as `0+01`. It is checked against the gate the columns produce, and an unreadable claim rejects the protocol |
| `n` | claimed number of columns; checked |
| `label` | a short name for the protocol |
| `notes` | free text, kept in the row's source entry |

Any other field is refused, so a typo cannot be silently ignored. This includes
the fields the tool sets itself: `regime`, `strength`, `discovery`,
`citations`, `provenance`, `origin` and `file`. The T-count and reduced degree
are computed by the verifier.

The shipped example,
[`examples/bravyi-kitaev_15-to-1.json`](examples/bravyi-kitaev_15-to-1.json),
is a complete submission: the [[15,1,3]] protocol of Bravyi and Kitaev in
generator-matrix form (shown here without its `notes` field).

```json
{
 "contributor": {"name": "magic-state-factories maintainers (worked example)"},
 "reference": {
  "key": "bravyi2005universal",
  "short": "Bravyi & Kitaev (2005)",
  "full": "S. Bravyi and A. Kitaev, \"Universal quantum computation with ideal Clifford gates and noisy ancillas,\" Phys. Rev. A 71, 022316 (2005).",
  "url": "https://doi.org/10.1103/PhysRevA.71.022316"
 },
 "method": "the 15-to-1 T distillation protocol (the [[15,1,3]] quantum Reed-Muller code), transcribed from the paper as a generator matrix: one logical row, four stabiliser rows",
 "terms": "The protocol is published in the reference above; this file restates its generator matrix as a worked example and adds no data of its own.",
 "protocols": [
  {"label": "15-to-1", "q": 1, "d": 3, "gate": "T0",
   "generator_matrix_rows": ["111111100000000", "101010101010101", "011001100110011",
                             "000111100001111", "000000011111111"]}
 ]
}
```

The same protocol in columns form:

```json
{"k": 1, "N": 5, "d": 3,
 "columns": [[0,1], [0,2], [0,1,2], [0,3], [0,1,3], [0,2,3], [0,1,2,3], [4],
             [1,4], [2,4], [1,2,4], [3,4], [1,3,4], [2,3,4], [1,2,3,4]]}
```

## Checking a submission before you send it

From the repository root, in the environment described under "Setup" in the
[top-level README](../README.md):

```bash
.venv/bin/python community_contributions/check_submission.py path/to/submission.json
```

The checker validates the file, then merges its protocols into an in-memory
copy of the catalogue using the catalogue's own merge tool. It prints a verdict
for each protocol and **writes nothing**. For the example it prints:

```text
checking community_contributions/examples/bravyi-kitaev_15-to-1.json: 1 protocol(s) from magic-state-factories maintainers (worked example), credited to bravyi2005universal
against master_catalog/master_catalog.json (804 classes)

  duplicate  protocol 0 (15-to-1): [[15,1,3]] N=5 T0 -- already held as N=5, d=3; nothing is stored, and the class keeps the credit it already had (bravyi2005universal)

1 protocol(s): 0 accepted, 0 improved, 1 duplicate, 0 rejected
catalogue: 804 -> 804 classes (nothing written: this was a check; maintainers merge with --write)
```

A rejected protocol is listed with its reasons, for example:

```text
  rejected   protocol 1 (broken):
               - check-contamination: odd degree-<=3 parity touching a check wire at [[4], [0, 1, 4], [0, 4]]: the circuit deposits phase on a postselected wire, so it is not a factory
```

| exit status | meaning |
|---|---|
| `0` | every protocol verified, whatever its verdict |
| `1` | a protocol was rejected, or the merged catalogue failed a check: a file-level check, or a circuit the length-54 classification says cannot exist (one that improves a Pareto point, or a new or improved class with `n ≤ 54` that no Pareto point dominates) |
| `2` | the submission is malformed (a missing, unknown or mistyped field, a placeholder, a bad link, or a reference key that clashes with the catalogue's), or the catalogue cannot be read. Nothing was merged |

`--catalog PATH` checks against another copy of the catalogue. The verdicts are
relative to the catalogue you check against. The maintainers re-run the check
against the current catalogue.

## How to submit

1. Name the file `YYYY-MM-DD_surname_short-title.json` and run the checker on
   it. Exit status `0` is what the maintainers can merge. If some protocols are
   rejected, fix or remove them, or explain in your submission why you think
   the verifier is wrong.
2. Open a pull request that adds that one file under
   [`submissions/`](submissions/), and nothing else. Do not edit
   `master_catalog/`, because the maintainers regenerate it. Include the
   checker's output in the description.
3. If you cannot open a pull request, open an issue on the repository with the
   file (attached or pasted) and the checker's output.

## For maintainers

1. **Re-run the check** on the submitted file against the current catalogue:
   `.venv/bin/python community_contributions/check_submission.py community_contributions/submissions/FILE.json`.
2. **Review what no verifier can check.** Is the contributor who they say they
   are, and does `method` describe how the protocols were found? Is the
   reference right? A published work needs its correct bibliographic line and
   its DOI or arXiv `url`. An unpublished one needs an entry crediting the
   contributor, with no `url`. Can the catalogue be redistributed under the
   stated `terms`? If the submission repeats or improves classes the catalogue
   already holds, is there a reason to change their credit (see below)?
3. **Merge:** re-run with `--write`. This rewrites
   `master_catalog/master_catalog.json` and `MASTER_CATALOG.md`, and saves any
   newly computed reduced-degree bounds to
   `master_catalog/reduced_degree_cache.json`. It writes only if no protocol
   was rejected and the merged catalogue passes the file-level checks
   (duplicate classes, provenance, citations, header). It also refuses a circuit
   the length-54 classification says cannot exist: one that improves a Pareto
   point, or a new or improved class with `n ≤ 54` that no Pareto point strictly
   dominates. It refuses to merge a
   file from outside `community_contributions/submissions/` into the master
   catalogue, because each merged row's source entry names the file.
4. **Verify:** run `.venv/bin/python master_catalog/verify_catalog.py`,
   `.venv/bin/python -m unittest discover -s master_catalog/tests` and
   `.venv/bin/python -m unittest discover -s community_contributions/tests`.
5. **Commit** the submission file and the regenerated catalogue together.

Classes are deduplicated on `(n, k, d, GL(k,2) class of the gate)`, and each
protocol gets one verdict:

| verdict | what it means for the catalogue |
|---|---|
| `accepted` | a class the catalogue did not have. Appended and credited to the submission's reference |
| `improved` | a class it had, with a better circuit (fewer wires `N`, then the tie-breaks in the master catalogue README). The circuit is replaced, and the submission is appended to `sources` and its regime to `regimes`. **The class keeps its citations**, and its `discovery` becomes `pre-existing` (a community contribution is not an AI discovery) |
| `duplicate` | a class it had, with a circuit no better. **Nothing changes**: not the circuit, its provenance or its citations |
| `rejected` | did not verify. The reasons are printed, and `--write` writes nothing |

**A class already held keeps its credit.** The catalogue credits a class
published earlier to that work alone, and a Pareto point of the length-54
classification by who found it. So the checker credits the submission's
reference only on classes the catalogue did not have. If a submission
establishes that a held class should also credit it, the maintainers make that
change separately, as a reviewed migration in `master_catalog/migrations/`. A
reference that ends up crediting no class is not added to the header.

## How contributions are credited

Every row a submission adds carries the four items below. A row it improves
gets the regime and the source entry, but keeps its citations.

* **a citation** of `reference.key`. A published work's entry has its DOI or
  arXiv `url`, and the citation column of `MASTER_CATALOG.md` links to it. An
  unpublished contribution's entry credits the contributor and has no `url`;
* **the regime `community contribution`**: contributed by an outside author
  and verified here from its explicit columns. It is a verified witness, not a
  maximum, and is placed at the weakest end of the header's regime order;
* **`discovery: pre-existing`** on a new class: not an AI discovery of this
  project;
* **a source entry**: `file` is the submission's path, `label` is the
  protocol's label, `origin` is the contributor's name, and `provenance` is
  `community contribution by NAME (AFFILIATION): METHOD`, followed by the
  protocol's label if it has one.

`contact` and `terms` are not copied into the catalogue. They stay in the
submission file, which remains in `submissions/`.

## Data terms

State in `terms` the terms under which the maintainers may redistribute your
protocols as part of this catalogue, for example the licence you release them
under or your permission to include them. A submission without redistribution
terms the maintainers can accept is not merged. If the protocols are someone
else's published work, say so and cite that work in `reference`.

## Files

| file | |
|---|---|
| [`check_submission.py`](check_submission.py) | validates a submission, checks it against the catalogue, and with `--write` merges it |
| [`TEMPLATE.json`](TEMPLATE.json) | a submission to copy and fill in |
| [`submissions/`](submissions/) | one file per submission, kept after merging |
| [`examples/`](examples/) | a complete, correct submission (a `duplicate` against the shipped catalogue) |
| [`tests/`](tests/) | the checker's tests: `.venv/bin/python -m unittest discover -s community_contributions/tests` |
