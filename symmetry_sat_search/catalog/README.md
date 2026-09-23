# Generated factory catalogue

Do not edit files in this directory by hand.

| file | contents | generator |
|---|---|---|
| [`factories.json`](factories.json) | 57 explicit verified circuits and derived metrics | [`../build_catalog.py`](../build_catalog.py) |
| [`FACTORY_CATALOG.md`](FACTORY_CATALOG.md) | the same rows as a human-readable table with matrices | [`../build_catalog.py`](../build_catalog.py) |
| [`symmetry_groups.json`](symmetry_groups.json) | automorphism generators and column-orbit representatives | [`../symmetry_groups.py`](../symmetry_groups.py) |

The sole editable source is
[`../examples/found_factories.json`](../examples/found_factories.json).

```bash
../../.venv/bin/python ../build_catalog.py
../../.venv/bin/python ../verify_catalog.py
../../.venv/bin/python ../symmetry_groups.py
../../.venv/bin/python ../rebuild_from_groups.py
```

Every JSON row records `label`, `target`, `kind`, `level`, `n`, `k`, `d`, `N`,
explicit `columns`, provenance (`source` and `group`), re-derived `output_gate`,
`t_count`, `poly_degree`, and verification flags. Qubits `0..k-1` are outputs.
A stored `d=5` certifies `d>=5`, because fault enumeration is exhaustive
through weight four.

These are search witnesses, not a complete classification. See
[`../../classification/`](../../classification/) for exhaustive windows.
