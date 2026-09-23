# Third-party notices

## Gillot–Langevin Reed–Muller classification data

The repository includes `classification/rank7_census/data/B-0-3-7.dat`,
downloaded from
the [Gillot–Langevin numerical-data
page](https://langevin.univ-tln.fr/project/agl7/data/index.php). Cite:

> Valérie Gillot and Philippe Langevin, “Classification of Some Cosets of the
> Reed–Muller Code,” *Cryptography and Communications* 15 (2023), 1129–1137.
> <https://doi.org/10.1007/s12095-023-00652-4>

No separate data license is stated on the upstream download page. The data is
included unchanged for reproducibility and is not covered by any license later
chosen for this repository’s original code. See
[`classification/rank7_census/data/README.md`](classification/rank7_census/data/README.md)
for the checksum, integrity audit, and the one metadata correction applied in
memory. `classification/rank7_census/tests/test_data.py` pins the file's
SHA-256, so an accidental replacement is caught by the test suite.
