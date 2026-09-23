# Parent input examples

[`parent_15_1_3.json`](parent_15_1_3.json) stores the 15 nonzero points of
`F_2^4`, the check parent behind the punctured Reed–Muller `[[15,1,3]]`
factory.

```bash
../../.venv/bin/python ../cli.py analyze \
  --input parent_15_1_3.json --node-budget 0
```

Catalogue selectors are resolved directly from
[`../../symmetry_sat_search/catalog/factories.json`](../../symmetry_sat_search/catalog/factories.json);
there is no duplicated frozen catalogue in this directory.
