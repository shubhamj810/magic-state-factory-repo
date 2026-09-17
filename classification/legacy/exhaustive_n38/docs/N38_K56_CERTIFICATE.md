# Certificate for the `n <= 38` output-width ceiling

Current overview of this directory: [`../README.md`](../README.md); the
overview-level treatment is
[`../../../../theory/02_classification.md`](../../../../theory/02_classification.md).

The machine-readable certificate is
[`../results/n38_k56_certificate.json`](../results/n38_k56_certificate.json).
It closes the provenance gap behind two catalog claims:

- the only `k = 5`, distance-3 class at `n <= 38` is the fully symmetric
  `[[31,5,3]]` class; and
- no `k = 6` distance-3 factory exists in the classified `n <= 38` window.

The equivalence relation is output permutation (`S_k`), matching the frontier
catalog. `GL(k,2)` values in the data are annotations, not the deduplication key.

## Proof split

Every parent is assigned by its effective check rank.

| parent layer | exhaustive argument | decisive bound |
|---|---|---|
| effective rank `<= 7` | Complete `RM(3,7)` census: 3,486 affine orbits, orbit sizes summing to `2^64`; all 71 relevant orbits and all `71 x 128 = 9,088` marked origins; all compatible subspaces | At `n <= 38`, compatible dimension 5 occurs only at `n = 31`; there are no compatible 6-spaces |
| effective rank `>= 8` | Every KTA/Nezami-Haah marked parent is scanned using the quotient `V = R(C)/C` | `dim V <= 4` throughout this layer, so five or six independent outputs are impossible |

For the only critical low-rank lengths, the completed all-origin census gives:

| `n` | marked geometries | maximum compatible dimension | 5-spaces | 6-spaces |
|---:|---:|---:|---:|---:|
| 31 | 192 | **5** | 992 | 0 |
| 32 | 576 | 4 | 0 | 0 |
| 35 | 252 | 3 | 0 | 0 |
| 36 | 644 | 4 | 0 | 0 |

There is no effective-rank-`<= 7` parent at `n = 38`; every `n = 38` parent is
in the second layer, where the maximum quotient dimension is 4. The JSON
certificate records the corresponding bound for every effective-rank-`>= 8`
length, not only these four critical cases.

The 992 compatible 5-spaces at `n = 31` collapse to one gate class under `S_5`:
the sum of every nonempty degree-at-most-3 monomial on five outputs. The
certificate includes a 31-column, `N = 10` witness. The standard-library-only
[`factorylib/verification.py`](../../../../factorylib/verification.py) independently
recomputes its parity tensor and exact distance 3.

## What is checked locally

The raw Gillot-Langevin orbit file is shipped at
[`../../rank7_census/data/B-0-3-7.dat`](../../rank7_census/data/B-0-3-7.dat).
Its SHA-256 digest, orbit count and corrected orbit-size identity are embedded
in the certificate and can be checked quickly with, from the repository root:

```bash
cd classification/legacy/rank7_census && ../../../.venv/bin/python cli.py data-check
```

The explicit witness can be checked without a solver or NumPy, from the
repository root:

```bash
cd classification/legacy/exhaustive_n38 && ../../../.venv/bin/python - <<'PY'
import json
import sys
from itertools import combinations

sys.path.insert(0, "../../..")              # the shared factorylib package
from factorylib.verification import verify

c = json.load(open("results/n38_k56_certificate.json"))
w = c["n31_k5_witness"]
target = {
    frozenset(qs)
    for degree in (1, 2, 3)
    for qs in combinations(range(w["k"]), degree)
}
print(verify(w["k"], w["N"], [frozenset(x) for x in w["columns"]], target))
PY
```

The expected result is `(True, 3)`. Reproducing the complete compatible-frame
census is intentionally not a laptop check; the cluster-scale command and
`complete`-flag semantics are documented in
[`../../rank7_census/README.md`](../../rank7_census/README.md).

## Imported-run provenance

The compact certificate was distilled from completed artifacts found beside
the pre-restructure workspace. Those artifacts are not shipped here; their
original relative paths, as recorded before this repository was restructured,
and their SHA-256 digests are retained in the JSON:

- `../rank7_census/census7_all_origins.json` — complete all-origin census;
- `../results/gl_r7_n38.json` — 47-class rank-`<= 7`, `S_k` gate catalog and the
  explicit `[[31,5,3]]` witness; and
- `../code/numba_ccz/n31_k6.log` — independent automorphism-reduced `n = 31`
  run through `k = 6`.

Those parent-directory files are provenance, not runtime dependencies, and the
paths above are historical: none of them resolves in the current layout. The
claim, decisive aggregate bounds, hashes and positive witness now live inside
this repository.
