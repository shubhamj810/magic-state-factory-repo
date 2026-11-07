#!/usr/bin/env python3
"""Export the circuits this folder works on to data/rows/<id>.json: {id, label, sha256, n, k, N, columns, ...}.

Catalogue rows come from magic-state-factory-repo/master_catalog via catalogfile.load_all() (read-only);
first-round results from research/search/lift/data/certified/.  The SHA-256 is over compact JSON of the
column list (constructions.digest), the catalogue's columns_sha256 convention.

usage: python rows.py            (writes every circuit in TARGETS and LIFT)
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path("/Users/shubhamjain/Documents/IBM internship/Shraddha (Magic states)")
CAT = ROOT / "magic-state-factory-repo" / "master_catalog"
LIFT = HERE.parents[1] / "search" / "lift" / "data" / "certified"
sys.path.insert(0, str(CAT))

TARGETS = ["935.89.6.a", "936.88.6.a", "937.87.6.a", "742.36.6.a", "756.32.6.a", "959.65.6.a", "988.36.6.a",
           "998.26.6.a", "511.9.6.a", "512.39.6.a", "512.84.6.a", "599.1.6.a", "255.3.7.a", "901.123.6.a",
           "1715.287.3.a", "441.1.6.a", "575.1.6.a", "559.1.6.a", "761.1.6.a", "777.1.6.a", "805.1.6.a"]
# exact rows whose A_d is null at dadb221 and which the pilot kernel counted (research/plan/data/A_d_counts.json)
COUNTED = ["255.4.7.a", "255.5.7.a", "255.6.7.a", "496.16.6.a", "846.122.6.a", "848.122.6.a", "850.126.6.a",
           "850.128.6.a", "852.126.6.a", "852.128.6.a", "854.124.6.a", "854.126.6.a", "854.128.6.a", "856.128.6.a",
           "858.128.6.a", "860.124.6.a", "860.126.6.a", "860.128.6.a", "896.128.6.a", "902.122.6.a", "904.120.6.a",
           "905.119.6.a", "906.118.6.a", "907.117.6.a", "908.116.6.a", "909.115.6.a", "910.114.6.a", "911.113.6.a",
           "912.112.6.a"]
SMALLK1 = ["177.1.7.a", "185.1.7.a", "189.1.7.a", "271.1.7.a", "279.1.7.a", "283.1.7.a", "401.1.6.a", "417.1.6.a", "1675.373.3.a", "1676.372.3.a", "1683.365.3.a"]
TARGETS = TARGETS + COUNTED + SMALLK1
LIFTFILES = ["930.94.7.8edc44a935.t94_b712810aa9.json", "930.94.7.41eb2a9cef.json", "930.94.7.f34845ed1a.json",
             "931.93.7.83a91c80c5.lns_a_t93.json", "932.92.7.0f5a3a3102.json", "933.91.7.6a25de9b43.json",
             "954.70.8.ff92d26dfe.json", "955.69.8.6627c613e4.json"]


def digest(cols) -> str:
    return hashlib.sha256(json.dumps(cols, separators=(",", ":")).encode("ascii")).hexdigest()


def main():
    import catalogfile
    out = HERE / "data" / "rows"
    out.mkdir(parents=True, exist_ok=True)
    rows = {r["catalog_label"]: r for r in catalogfile.load_all()["factories"]}
    for lab in TARGETS:
        r = rows[lab]
        cols = [list(c) for c in r["columns"]]
        rec = {"id": lab, "label": lab, "sha256": digest(cols), "n": r["n"], "k": r["k"], "N": r["N"],
               "d": r["d"], "d_is_exact": r["d_is_exact"], "d_upper": r.get("d_upper"),
               "d_certified": r.get("d_certified"), "d_certified_is_exact": r.get("d_certified_is_exact"),
               "A_d": r.get("A_d"), "d_witness": r.get("d_witness"), "columns": cols}
        assert rec["n"] == len(cols)
        (out / f"{lab}.json").write_text(json.dumps(rec))
        print(lab, rec["n"], rec["k"], rec["N"], rec["sha256"][:10])
    for fn in LIFTFILES:
        r = json.loads((LIFT / fn).read_text())
        cols = [list(c) for c in r["columns"]]
        sha = digest(cols)
        assert sha == r["columns_sha256"], fn
        ident = f"{r['n']}.{r['k']}.{r['D_claimed']}.{sha[:10]}"
        rec = {"id": ident, "label": None, "sha256": sha, "n": r["n"], "k": r["k"], "N": r["N"],
               "d_claimed": r["D_claimed"], "source": f"research/search/lift/data/certified/{fn}", "columns": cols}
        (out / f"{ident}.json").write_text(json.dumps(rec))
        print(ident, r["n"], r["k"], r["N"])


if __name__ == "__main__":
    main()
