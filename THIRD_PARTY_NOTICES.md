# Third-party notices

## Gillot–Langevin Reed–Muller classification data

The repository includes `classification/legacy/rank7_census/data/B-0-3-7.dat`,
downloaded from
the [Gillot–Langevin numerical-data
page](https://langevin.univ-tln.fr/project/agl7/data/index.php). Cite:

> Valérie Gillot and Philippe Langevin, “Classification of Some Cosets of the
> Reed–Muller Code,” *Cryptography and Communications* 15 (2023), 1129–1137.
> <https://doi.org/10.1007/s12095-023-00652-4>

No separate data license is stated on the upstream download page. The data is
included unchanged for reproducibility and is not covered by any license later
chosen for this repository’s original code. See
[`classification/legacy/rank7_census/data/README.md`](classification/legacy/rank7_census/data/README.md)
for the checksum, integrity audit, and the one metadata correction applied in
memory. `classification/legacy/rank7_census/tests/test_data.py` pins the file's
SHA-256, so an accidental replacement is caught by the test suite.

## Length-54 generalised triorthogonal classification frontier

The repository includes `classification/length54/pareto_frontier.json`,
unmodified from `AWillsQuantum/generalised_triorthogonal_classification`
(commit and SHA-256 in
[`classification/length54/README.md`](classification/length54/README.md)).
Copyright 2026 Adam Wills; creators Adam Wills, Shubham P. Jain and Shraddha
Singh. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Dataset: *Generalised triorthogonal protocols through length 54: classification
data and evidence*, DOI `10.6084/m9.figshare.33717319`.
