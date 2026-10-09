# Community contributions

This directory is how people outside the project add magic-state distillation
factories to the [master catalogue](../master_catalog/). **Send your protocols
in whatever form you have them.** The maintainers:

1. convert them into the catalogue's format;
2. re-derive every number from explicit circuits with the catalogue's own
   verifier;
3. merge what verifies;
4. cite your work on every class that is new to the catalogue.

## Submitting

### Any format is fine

For example:

* a paper, preprint or arXiv link that describes the protocols;
* generator matrices, parity-check or stabiliser matrices, or triorthogonal
  matrices, as text, CSV, JSON, LaTeX tables or images;
* circuits, in any notation;
* code or a notebook that constructs the protocols;
* a construction described in words, precisely enough to write the circuits
  down;
* a mix of these, as a single file, a folder or a zip archive.

### Tell us, if you can

* **Who to credit.** Names, affiliations, and the paper if the protocols are
  published.
* **Redistribution terms.** Whether the protocols may be included in this
  catalogue and redistributed with it, for example under a licence. See
  [Data terms](#data-terms).
* **What the protocols are,** as far as you know: the number of `T` inputs `n`,
  outputs `k`, distance `d`, the output gate, and how they were found. The
  maintainers check all of this themselves, so an approximate or partial
  description is fine.
* **A way to reach you,** if the maintainers have questions. A pull request is
  public, so send contact details privately if you prefer.

If some of this is missing, send what you have. The maintainers will ask.

### What the catalogue can hold

It holds protocols whose output is a diagonal non-Clifford gate built from `T`,
`CS` and `CCZ` (level 3), with fault distance `d ≥ 2`. Each protocol must be
writable as an explicit circuit. A family or asymptotic construction is fine to
send: the maintainers list the explicit members they can write down. If you are
not sure a protocol fits, send it anyway.

### How to send it

* **Submission form (easiest).** Open a
  [factory submission](https://github.com/shubhamj810/magic-state-factory-repo/issues/new?template=submit-factory.yml),
  or use the text box on the website's
  [contribute page](https://shubhamj810.github.io/magic-state-factory-repo/contribute.html#send).
  Type a description and attach files. On submit, a workflow copies your text to
  `submissions/YYYY-MM-DD_<github-login>_issue-<N>/description.txt`, downloads
  your attachments beside it, and opens a pull request. You never fork or push.
  No GitHub account? Email shubhamj810@gmail.com.
* **Pull request.** Add one folder,
  `submissions/YYYY-MM-DD_surname_short-title/`, containing your files as they
  are. Do not edit `master_catalog/`; the maintainers regenerate it.
* **Issue.** Open an issue on the repository with your files attached or
  linked.

## What happens next

The maintainers convert your submission into a catalogue input file, stored in
your submission's folder beside your originals. They then run the checker.
Every protocol is verified from its circuit, not from its stated parameters, and
gets one of four verdicts:

| verdict | what it means |
|---|---|
| `accepted` | a class the catalogue did not have. It is added and credited to your work |
| `improved` | a class the catalogue had, and your circuit is better (fewer wires). Your circuit replaces the stored one and is recorded as a source; the class keeps the credit it already had |
| `duplicate` | a class the catalogue had, with a circuit no better. Nothing changes |
| `rejected` | it did not verify, for example because a single fault goes undetected (distance 1) or it is not a factory as stated. The maintainers tell you why |

Nothing is merged that the verifier would not re-derive from the circuit.
Classes are compared up to relabelling and a change of output basis (the
`GL(k,2)` class of the gate) at the same `n`, `k` and distance.

## For maintainers

### The catalogue input format

A submission is converted into one JSON file,
`submissions/<submission>/catalogue_input.json`. The contributor's original
files stay beside it. [`TEMPLATE.json`](TEMPLATE.json) is the file to start
from; every `<...>` value is a placeholder, and the checker refuses the file
while any placeholder is left.

A factory has `N` wires: wires `0..k-1` are the outputs and wires `k..N-1` are
postselected checks. Each column is one `T` rotation, and `n` is the number of
columns. Indices are 0-based throughout.

| field | |
|---|---|
| `contributor.name` | **required.** The name the contribution is credited under |
| `contributor.affiliation` | optional; printed after the name in each row's provenance |
| `contributor.contact` | optional; never copied into the catalogue |
| `reference.key` | **required.** A citation key: 3–64 lowercase letters, digits, `_` or `-`, e.g. `surname2026firstword`. If the work is already listed under "References" in [`MASTER_CATALOG.md`](../master_catalog/MASTER_CATALOG.md), use that key and copy its entry exactly |
| `reference.short` | **required.** The label for the citation column, e.g. `Doe et al. (2026)`; it must differ from every other work's label |
| `reference.full` | **required.** The full bibliographic line. For unpublished work, a line crediting the contributor, e.g. `J. Doe, unpublished community contribution (2026).` |
| `reference.url` | optional. The `https` DOI or arXiv link of a **published** work, which the citation column links to |
| `reference.date` | optional. The publication date of a **published** work, `YYYY-MM-DD` or `YYYY-MM` (the journal's, or the arXiv v1 date for a preprint), in the year `short` prints. It orders the reference lists |
| `method` | **required.** One or two sentences (at most 400 characters) on how the protocols were found |
| `terms` | **required.** The redistribution terms the contributor gave (see [Data terms](#data-terms)) |
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
the fields the checker sets itself: `regime`, `strength`, `discovery`,
`citations`, `provenance`, `origin` and `file`.

[`examples/bravyi-kitaev_15-to-1.json`](examples/bravyi-kitaev_15-to-1.json) is
a complete input file for the [[15,1,3]] protocol of Bravyi and Kitaev in
generator-matrix form (shown here without its `notes` field):

```json
{
 "contributor": {"name": "magic-state-factories maintainers (worked example)"},
 "reference": {
  "key": "bravyi2005universal",
  "short": "Bravyi & Kitaev (2005)",
  "full": "S. Bravyi and A. Kitaev, \"Universal quantum computation with ideal Clifford gates and noisy ancillas,\" Phys. Rev. A 71, 022316 (2005).",
  "url": "https://doi.org/10.1103/PhysRevA.71.022316",
  "date": "2005-02-22"
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

### Checking

From the repository root, in the environment described under "Setup" in the
[top-level README](../README.md):

```bash
.venv/bin/python community_contributions/check_submission.py path/to/catalogue_input.json
```

The checker validates the file, then merges its protocols into an in-memory
copy of the catalogue using the catalogue's own merge tool. It prints a verdict
for each protocol and **writes nothing**. For the example it prints:

```text
checking community_contributions/examples/bravyi-kitaev_15-to-1.json: 1 protocol(s) from magic-state-factories maintainers (worked example), credited to bravyi2005universal
against master_catalog/master_catalog.json (813 classes)

  duplicate  protocol 0 (15-to-1): [[15,1,3]] N=5 T0 -- already held as N=5, d=3; nothing is stored, and the class keeps the credit it already had (bravyi2005universal)

1 protocol(s): 0 accepted, 0 improved, 1 duplicate, 0 rejected
catalogue: 813 -> 813 classes (nothing written: this was a check; maintainers merge with --write)
```

A rejected protocol is listed with its reasons, for example:

```text
  rejected   protocol 1 (broken):
               - check-contamination: odd degree-<=3 parity touching a check wire at [[4], [0, 1, 4], [0, 4]]: the circuit deposits phase on a postselected wire, so it is not a factory
```

| exit status | meaning |
|---|---|
| `0` | every protocol verified, whatever its verdict |
| `1` | a protocol was rejected, or the merged catalogue failed a check: a file-level check, or a circuit the length-54 classification says cannot exist (one that improves a Pareto point, or a new or improved class with `n ≤ 54` and `d ≥ 3` that no Pareto point strictly dominates) |
| `2` | the input file is malformed (a missing, unknown or mistyped field, a placeholder, a bad link, or a reference key that clashes with the catalogue's), or the catalogue cannot be read. Nothing was merged |

`--catalog PATH` checks against another copy of the catalogue.

The verifier refuses circuits that:
* deposit phase on a check wire;
* repeat a column;
* leave an output untouched (a spectator);
* count an output that is another output plus a stabiliser (a pseudo-output);
* carry a check wire whose syndrome bit the other checks already give;
* declare wires no rotation uses.

It does not repair them. A repaired circuit (for example with a redundant wire
deleted) is a different factory from the one submitted, so raise the failure
with the contributor rather than converting a repair. The full bar is under
"Verifying" and "Merging new results" in
[`master_catalog/README.md`](../master_catalog/README.md).

### Merging

1. **Convert** the submission into
   `submissions/<submission>/catalogue_input.json`. Keep the contributor's
   originals in the same folder, unchanged.
2. **Check** it:
   `.venv/bin/python community_contributions/check_submission.py community_contributions/submissions/<submission>/catalogue_input.json`.
   Resolve rejections with the contributor.
3. **Review what no verifier can check.**
   * Is the credit right? A published work needs its correct bibliographic line
     and its DOI or arXiv `url`; an unpublished one needs an entry crediting the
     contributor, with no `url`.
   * Does `method` describe how the protocols were found?
   * May the protocols be redistributed under the stated `terms`?
4. **Merge:** re-run with `--write`.
   * **What it rewrites:** `master_catalog/master_catalog.json` and
     `MASTER_CATALOG.md`. Any newly computed reduced-degree bounds are saved to
     `master_catalog/reduced_degree_cache.json`.
   * **When it writes nothing:**
     * a protocol was rejected;
     * the merged catalogue fails a file-level check (duplicate classes,
       provenance, citations, header);
     * a circuit is one the length-54 classification says cannot exist;
     * the input file is outside `community_contributions/submissions/` — every
       merged row's source entry names this file.
5. **Verify:**
   * `.venv/bin/python master_catalog/verify_catalog.py --changed` (the rows
     the merge changed, plus the whole-file checks; the flag-less full run
     takes about fifteen minutes)
   * `.venv/bin/python -m unittest discover -s master_catalog/tests`
   * `.venv/bin/python -m unittest discover -s community_contributions/tests`
6. **Commit** the submission folder and the regenerated catalogue together.

### How contributions are credited

Every row a contribution adds carries:

* **a citation** of `reference.key`. A published work's entry has its DOI or
  arXiv `url`, and the citation column of `MASTER_CATALOG.md` links to it. An
  unpublished contribution's entry credits the contributor and has no `url`;
* **the regime `community contribution`**: contributed by an outside author
  and verified here from its explicit columns; a verified witness, not a
  maximum;
* **`discovery: pre-existing`**: not an AI discovery of this project;
* **a source entry**: `file` is the input file's path, `label` is the protocol's
  label, `origin` is the contributor's name, and `provenance` is
  `community contribution by NAME (AFFILIATION): METHOD`, followed by the
  protocol's label if it has one.

A row a contribution improves gets the regime and the source entry, and keeps
its citations. **A class already held keeps its credit.** The catalogue credits
a published class to that work alone, and a Pareto point of the length-54
classification by who found it. So the checker credits a contribution's
reference only on classes the catalogue did not have. If a contribution shows
that a held class should also credit it, the maintainers make that change
separately, as a reviewed migration in `master_catalog/migrations/`. A reference
that ends up crediting no class is not added to the header.

`contact` and `terms` are not copied into the catalogue. They stay in the input
file, in the submission's folder.

## Data terms

The maintainers can only include protocols they may redistribute with the
catalogue. Contributors should say so: for example, the licence they release the
protocols under, or their permission to include them. Protocols that are someone
else's published work are cited to that work. The terms the contributor gives
are recorded in the input file's `terms`.

## Files

| file | |
|---|---|
| [`submissions/`](submissions/) | one folder per submission: the contributor's files as sent, and the maintainers' `catalogue_input.json` |
| [`check_submission.py`](check_submission.py) | validates a catalogue input file, checks it against the catalogue, and with `--write` merges it |
| [`TEMPLATE.json`](TEMPLATE.json) | a catalogue input file to copy and fill in |
| [`examples/`](examples/) | a complete, correct input file (a `duplicate` against the catalogue) |
| [`tests/`](tests/) | the checker's tests: `.venv/bin/python -m unittest discover -s community_contributions/tests` |
