# The catalogue website

A static, searchable view of [`master_catalog/master_catalog.json`](../master_catalog/master_catalog.json),
published at **<https://shubhamj810.github.io/magic-state-factory-repo/>**.

The master catalogue is the only data source. Nothing the site shows is stored
anywhere else in the repository. Every deploy rebuilds the site's data from the
catalogue, so a merged result appears on the site with no further step.

```
master_catalog/master_catalog.json          813 rows, columns included
            |
            |  website/build_site.py         standard library only, ~1 s
            v
website/_site/                               (git-ignored; built in CI)
  index.html    landing: best results, γ_ρ frontier, [[n,k,d]] table, cite, download
  search.html   every factory: filters, typed queries, sort, CSV/JSON export
  params.html   every inequivalent gate at one [[n,k,d]]
  factory.html  one circuit: its matrix, metrics, references, export
  data/index.json             every row WITHOUT columns (what the list pages read)
  data/factories/<id>.json    one row WITH columns (what one factory page reads)
  data/factories.csv          the index as a spreadsheet
```

## Running it locally

```bash
python website/build_site.py
python -m http.server -d website/_site 8000      # open http://localhost:8000/
```

## What the build adds, and what it does not

It copies `n`, `k`, `d`, `N`, the gate, the T-count, the degree, the distance
evidence, the provenance and the citations straight from each row. It computes
only these, each a one-line function of fields the catalogue already verified:

| field | definition |
|---|---|
| `gamma` | `log(n/k) / log d` |
| `gamma_t` | `log(n/T-count) / log d` |
| `V_ex` | T states one run yields: T and CS count 1, CCZ 2, and **undefined** when the gate's terms share an output |
| `gamma_rho` | `log(n/V_ex) / log d`; the landing page ranks on this |

It also checks every row on the way through. The build fails if any of these
does not hold:
- the `gate` string spells `gate_human`;
- there are `n` columns;
- every citation is in the reference table;
- no two rows share an id;
- the number of rows matches `n_classes`.

A factory's id is `n{n:04}-k{k:03}-d{d}-{sha256(n|k|d|gate)[:8]}`. It is stable
across rebuilds, so a link to a factory keeps working. It changes only if a merge
replaces that row's representative circuit.

## Searching

The search box takes words, combined with AND:

| type | means |
|---|---|
| `[[49, 1, 5]]` | exactly these parameters |
| `n<=100` `k=2` `d>=5` `N<12` `r=4` | parameters (`n` and `N` are different) |
| `t<=4` `deg=2` `g<1.3` | T-count, phase-polynomial degree, γ_ρ |
| `T0` `CS01` `CCZ012` `CCZ10,11,12` | the gate contains this exact term |
| `T` `CS` `CCZ` | the gate contains a term of this kind |
| `pure` `exact` | pure `T^⊗k`; exact distance |
| anything else | text in the gate, id, regime or cited papers |

Every filter lives in the URL, so a search can be shared as a link, for
example [`search.html?has=ccz&d=5`](https://shubhamj810.github.io/magic-state-factory-repo/search.html?has=ccz&d=5).

## Checks

```bash
cd website && python -m unittest discover -s tests   # the build (also run by verify_repo.py)
python website/verify_site.py                        # a real browser over the built site
python website/verify_site.py --full                 # every parameter set and factory, ~10 min
```

`verify_site.py` needs `pip install playwright && playwright install chromium`.
It is the only part of the repository that does, which is why `verify_repo.py`
does not run it. It loads every page shape in headless Chromium and checks the
rendered page against counts it computes itself:
- 21 searches;
- the CSV export;
- the matrix's output and check rows and its row weights;
- each factory's references.

It fails on any console error, failed request, or stray `undefined`/`NaN`.

## Deployment

[`.github/workflows/pages.yml`](../.github/workflows/pages.yml) runs on every
push to `main` that touches the catalogue or `website/`. It builds the site, runs
both checks, and publishes `website/_site` (and nothing else) to GitHub Pages.
On a pull request it builds and checks without deploying. A manual run can ask
for the full browser check.

One-time setup: **Settings → Pages → Build and deployment → Source: GitHub
Actions**.
