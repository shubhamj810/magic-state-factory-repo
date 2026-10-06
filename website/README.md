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
  index.html          landing: search, what the catalogue offers, best factories, frontier, parameter table
  about.html          what the numbers mean, how each is obtained, citing, data
  contribute.html     a step-by-step guide to contributing, ending with an email address
  search.html         every factory: filters, typed queries, sort, CSV/JSON export
  f/<label>/          one static page per factory, e.g. f/15.1.3.a/
  p/<n>.<k>.<d>/      one static page per parameter set, e.g. p/15.1.3/
  factory.html, params.html   old addresses, redirected to the two above
  sitemap.xml         every page, for search engines
  data/index.json             every row WITHOUT columns (what the list pages read)
  data/factories/<label>.json one row WITH columns
  data/factories.csv          the index as a spreadsheet
```

## Running it locally

```bash
python website/build_site.py
python -m http.server -d website/_site 8000      # open http://localhost:8000/
```

## Static pages and labels

Every factory and parameter page is rendered to HTML at build time
([`pages.py`](pages.py)), so it has its own title and description, reads
without JavaScript, and can be indexed by search engines (including Google
Scholar) and archived. The scripts only add interaction on top: sorting, the
matrix view toggle, exports, the CNOT + S tool and KaTeX typesetting.

A factory's address is its catalogue label, `catalog_label` in
`master_catalog.json`, for example `f/15.1.3.a/`. Labels are assigned once by
the catalogue and never change, so these links are permanent. Links in the old
form, `factory.html?id=…` (including the hash ids used before labels) and
`params.html?n=…&k=…&d=…`, redirect to the new pages.

Each factory page has:
- a summary strip, with the distance as proved bounds (`6 ≤ d ≤ 7` when an explicit
  damaging fault gives an upper bound);
- a BibTeX entry, downloads and related parameter sets;
- a "Use it in code" snippet that loads the factory and re-derives it with
  `verify_catalog.py`;
- a "Report a problem" link that opens a prefilled GitHub issue.

The search page shows each active filter as a removable chip, and counts how many
results each filter value would give. A column chooser hides or shows columns
(T-count is off by default), and every row can preview its matrix inline. `/`
focuses the search box on any page. The landing page ranks by γ among pure
T⊗k factories by default, and by γ_ρ across every gate at the flip of a
switch; the best-factories figures, the records table and the frontier all
follow it. The frontier plot switches to a table of its frontier points and
exports to SVG and PNG.
[`CITATION.cff`](../CITATION.cff) at the repository root gives GitHub's
"Cite this repository" button and describes releases archived on Zenodo.

## Layout and design

`static/` holds the pages, stylesheet and scripts. `templates/` holds what
every page shares: the `<head>`, the header and the footer. A page marks their
places with `<!--#head-->`, `<!--#header PAGE-->` and `<!--#footer-->`, and
the build stitches them in. `PAGE` names the nav link to mark as current; add
`nosearch` to drop the header's search box. The build also appends a hash of
the stylesheet and scripts to their URLs, so a deploy is never mixed with a
browser's cached copy. The catalogue commit is recorded in `data/index.json`.

The look comes from [`static/css/style.css`](static/css/style.css). Headings
and prose are set in Source Serif 4. Tables and controls use IBM Plex Sans with
tabular figures, and monospace is kept for raw data only: gate strings, the
matrix and code. All mathematics, including γ_ρ, V_ex, ⟦n, k, d⟧ and gate names
such as T₀·CS₀₁, is typeset with KaTeX, so it reads like the papers. Surfaces are
flat, with hairline borders, 4 px corners and one accent blue. There are no gradients, glows, shadows on cards or accent bars. Every
colour is a token on `:root`, and dark mode is a separate palette rather than
an automatic inversion. Colour is used only where it carries meaning:
- **Output wires** are amber and **check wires** are teal, in the matrix, the
  hero and the logo.
- **Distance** `d = 3…7` is a single-hue blue ramp on the small distance dots,
  checked as an ordinal ramp against both surfaces.
- **The frontier plot** is small multiples, one panel per distance on shared
  axes. Points are grey and the frontier staircase is the accent, so position
  rather than colour tells the distances apart.

`n` and `N` are different parameters, so the stylesheet never uses
`text-transform`.

## The CNOT + S tool on each factory page

Two output gates prepare the same magic state when a CNOT circuit on the
outputs and diagonal Clifford corrections (S, Z, CZ) turn one into the other.
That is the catalogue's own deduplication relation, the `GL(k,2)` key. Each
factory page lets you type a target gate and get one of three answers:
- **reachable**, with the circuit that does it;
- **not reachable**, with the catalogued factories that do produce that gate;
- **undecided**, when the search runs out of budget or k > 16.

[`static/js/glequiv.js`](static/js/glequiv.js) decides the question with a port
of [`master_catalog/glcanon.py`](../master_catalog/glcanon.py): the cubic form's
labels, then a bounded basis search. It then constructs the answer:
- the CNOT circuit for `A⁻¹`, by Gaussian elimination;
- the leftover diagonal Clifford, by a Möbius transform over Z₄.

Both are checked by brute force on all 2^k basis states before anything is
shown. Running out of search budget is reported as undecided, never as an answer.

The port was checked against the Python on the catalogue:
- 4,000 same-k pairs of rows, k ≤ 6: 4,000 agree, none undecided;
- every row with k ≤ 8 after a random change of output basis: all recognised,
  and all constructions pass.

## What the build adds, and what it does not

It copies `n`, `k`, `d`, `N`, the gate, the T-count, the degree, the distance
evidence, the provenance and the citations straight from each row. It computes
only these, each a one-line function of fields the catalogue already verified:

| field | definition |
|---|---|
| `gamma` | `log(n/k) / log d` |
| `gamma_t` | `log(n/T-count) / log d` |
| `V_ex` | T states one run yields: T and CS count 1, CCZ 2, and **undefined** when the gate's terms share an output |
| `gamma_rho` | `log(n/V_ex) / log d`; the landing page can rank on this |

It also checks every row on the way through. The build fails if any of these
does not hold:
- the `gate` string spells `gate_human`;
- there are `n` columns;
- every citation is in the reference table;
- no two rows share an id;
- the number of rows matches `n_classes`.

A few rows carry a distance certified by their source that the catalogue could
not re-check (`d_certified`). Tables show both distances side by side. Claims,
meaning the rankings, the frontier plot and the exponents marked †, use the
certified distance. Filters on distance match either one.

A factory's id on the site is its `catalog_label`. The earlier hash id
`n{n:04}-k{k:03}-d{d}-{sha256(n|k|d|gate)[:8]}` is still computed, as
`legacy_id`, only so old links can be redirected.

## Searching

The search box takes words, combined with AND:

| type | means |
|---|---|
| `[[49, 1, 5]]` | exactly these parameters |
| `15.1.3.a` | a factory by its label |
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
- 22 searches;
- the CSV export;
- the hero matrix, the plot tooltip, and that KaTeX typeset the maths;
- the search chips, a filter count, the column chooser and an inline preview;
- the frontier table, under both rankings, against the frontier recomputed in
  Python, that Plot and Table each hide the other, and that the SVG
  export holds every plotted point;
- a proved upper bound on a factory page;
- the new addresses: old links redirect, and a factory page renders its title
  and matrix with JavaScript turned off;
- the CNOT + S tool, against `master_catalog/glcanon.py`: an inequivalent target is
  refused, every factory it lists instead really is equivalent, and random
  equivalent targets come back with a construction checked on every basis state;
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
