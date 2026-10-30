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

## Borrowed Identities catalogue and search code

The repository includes `borrowed_identities/upstream/`, sixteen files copied
unmodified from
[`shraggy/Magic_state_factory_search`](https://github.com/shraggy/Magic_state_factory_search)
at commit `cae49828ed9ab9c1079c7cdf66c5bd337b027515` (author: Shraddha Singh):
the two-group and symmetry-free searches, the classifier and circuit
exporter, the factory catalogues `outputs/factory_catalogue_l{2,3,4}.csv`, and
their READMEs. Cite:

> S. Singh, C. Gidney, and C. Jones, “Borrowed Identities: Malleable
> Distillation Factories and a Unified Numerical Search,” arXiv:2606.28518
> (2026). <https://arxiv.org/abs/2606.28518>

The upstream repository states no licence. The files are included unchanged,
with attribution, so that the master catalogue's provenance resolves inside this
repository and the circuits in `borrowed_identities/circuits/` can be rebuilt.
They are not covered by any licence later chosen for this repository's own
code. `borrowed_identities/tests/` pins every file's SHA-256, so an accidental
edit is caught by the test suite. See
[`borrowed_identities/README.md`](borrowed_identities/README.md).

`borrowed_identities/upstream_unified/` holds 25 files copied unmodified from
the same repository at commit `46270145dc77643672ee4afbc9ff9f4b48bab083`: the
unified search, its large two-group sweep and `k = 7, 8` gluing scripts, the
classifier, the tables `all_factories.csv`, `large_sweep.csv`,
`l3_k78_targets.csv` and `smallest_per_class.csv`, the upstream error
coefficients, and the READMEs, `LICENSE` and `CITATION.cff`. By that commit
the upstream repository is licensed under the
[Apache License 2.0](borrowed_identities/upstream_unified/LICENSE), whose
terms these files keep; the licence text is included beside them, and they
are unmodified. The same citation applies.

`borrowed_identities/upstream_large_unified/` holds 15 files copied
unmodified from the same repository at commit
`ae9fbf895e2993568f731b22e785e1e1fcb93655`: the unified search scripts with
the larger run's `large_unified.py` and `merge_large_unified.py`, the
classifier, the level-3 table `large_unified_factories_l3.csv` and its gate
lists `large_unified_l3_circuits.txt.zip`, and the READMEs, `LICENSE` and
`CITATION.cff`. They are under the same
[Apache License 2.0](borrowed_identities/upstream_large_unified/LICENSE), and
the same citation applies.

## Transversal-T codes of Jain and Albert, and of A. Gong

Apart from `gong_self_dual_codes.json` (below), `transversal_t_codes/`
contains no third-party files. It builds the codes of
S. P. Jain and V. V. Albert, “Transversal Clifford and T-gate codes of short
length and high distance,” *IEEE J. Sel. Areas Inf. Theory* 6, 127–137 (2025)
(<https://doi.org/10.1109/JSAIT.2025.3570832>, arXiv:2408.12752), from the
paper's published construction, with this repository's own code. Please cite
the paper for the codes. The construction name `sub(XQ47)` of the `[46,23,10]`
self-dual code is from P. Gaborit's tables of self-dual codes
(<https://www.unilim.fr/pages_perso/philippe.gaborit/SD/>); no data was copied
from them.

`transversal_t_codes/gong_self_dual_codes.json` holds the stabilisers of two
doubly even self-dual codes, `[[41,1,9]]` and `[[65,1,13]]`, copied from
`triply-even/41_XZ.mtx` and `triply-even/65_XZ.mtx` of A. Gong's repository
<https://github.com/gongaa/RM127> at commit
`b425fd5f07e86152518115c939a03b21b87960ae`, rewritten as lists of qubit
indices. Please cite her note, "On some K=1 codes admitting strongly transversal
T" (in that repository, `triply-even/`), for these codes and the codes
doubled from them. They are used under the repository's MIT licence:

```text
MIT License

Copyright (c) 2024 Anqi Gong

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
