#!/usr/bin/env python3
"""Turn ``catalog/sk_classes_r7.json`` into a ``merge_results.py`` input.

One record per S_k class, in the merge tool's documented schema.  The regime
is the census's existing one -- ``census r<=7``, "classified subject to the
check-rank bound r <= 7" -- because that is literally what every one of these
rows is; a new regime would be filed by `merge_results.py` at the END of the
regime order, i.e. as the weakest claim, which is the opposite of the truth.
``discovery`` is ``pre-existing`` for the same reason: a classification
catalogue has the class.  ``file`` and ``label`` point at the row of the S_k
catalogue that carries the witness, which is what
``tests/test_master_catalog.py::test_source_attribution_is_real`` opens.

Run:  python sk_merge_input.py [catalog/sk_classes_r7.json] > sk_merge_input.json
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "catalog" / "sk_classes_r7.json"
FILE = "classification/rank7_census/catalog/" + CAT.name

payload = json.loads(CAT.read_text(encoding="utf-8"))
records = []
for r in payload["factories"]:
    records.append({
        "k": r["k"], "N": r["N"], "n": r["n"], "d": r["d"],
        "columns": r["columns"],
        "gate": r["gate"],
        "t_count": r["t_count"], "poly_degree": r["poly_degree"],
        "regime": "census r<=7",
        "discovery": "pre-existing",
        "file": FILE,
        "label": r["gate"],
        "provenance": r["source"],
    })
json.dump({"results": records}, sys.stdout, indent=1)
print(file=sys.stdout)
print(f"{len(records)} records", file=sys.stderr)
