# Generalised triorthogonal protocols through length 54

A copy of the Pareto frontier from the exhaustive classification of
generalised triorthogonal protocols with `n <= 54` and exact `d_Z >= 3`
(A. Wills, S. P. Jain and S. Singh, *Classification of Generalised
Triorthogonal Codes through Length 54*, [arXiv:2609.30860](https://arxiv.org/abs/2609.30860)).

| file | contents |
|---|---|
| [`pareto_frontier.json`](pareto_frontier.json) | the 74 Pareto points for the 62 CNOT+S output classes: generator matrices, exact distances, leading error coefficients, representative gates and output-basis certificates |

## Where it comes from

`pareto_frontier.json` is **byte-identical** to `data/protocols/pareto_frontier.json`
in the classification's code and theory delivery,
`AWillsQuantum/generalised_triorthogonal_classification`, at commit
`9de3c553ed6658e29e504866a04b08702cfeb248`. Its SHA-256,
`5f60bbd546769a71dbadbe97992b091fabc77b8c20b1697d869dc0c1484d7e95`, is the one
that delivery's `MANIFEST.json` records. The delivery's own witness verifier,
`code/verify_protocols.py`, passes on this copy.

The copy is here so the master catalogue's provenance resolves inside this
repository. The enumeration code, the proofs of exhaustiveness and the space
catalogues are not copied. They are in that repository and its companion
Figshare dataset (DOI `10.6084/m9.figshare.33717319`, stated by the delivery).

The data is licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Copyright 2026 Adam Wills;
creators Adam Wills, Shubham P. Jain and Shraddha Singh. The file is unmodified.

## What it contains

- **Matrices.** Each protocol's matrix is `G = [G_1; G_0]`: `q` logical rows,
  then the stabiliser rows. `S` is the total number of rows and `n` the number
  of columns.
- **Scope.** The classification covers `n <= 54` and exact distance `d_Z >= 3`.
  Matrices have full row rank and distinct columns, with one zero column allowed.
- **Frontier.** Outputs are identified under CNOT+S equivalence. For each output
  class and exact distance, the frontier keeps the protocols that are
  undominated in `(n, S)`.
- **Counts.** 67 points have distance 3, five have distance 4 and two have
  distance 5.

The file lists witnesses only. The exhaustiveness proof is in the delivery;
see its README and `AUDIT_GUIDE.md`.

## How the master catalogue uses it

Read as a factory, a protocol is `N = S` wires with outputs `0..q-1` (the
logical rows) and one column per `T` injection. All 74 are rows of
[`../../master_catalog/master_catalog.json`](../../master_catalog/master_catalog.json).
They carry the regime `exhaustive classification n<=54 (Pareto point)` and a
`sources` entry whose label is `protocol <index>` in this file.
[`../../master_catalog/migrations/length54_classification_2026_09_16.py`](../../master_catalog/migrations/length54_classification_2026_09_16.py)
merged them. `master_catalog/tests/test_master_catalog.py` checks two things
against this file:

- every protocol is held;
- no other catalogue row at `n <= 54` beats the frontier.
