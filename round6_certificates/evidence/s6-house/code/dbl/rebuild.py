#!/usr/bin/env python3
"""Rebuild s4-d8's five doubled rows from the main catalogue's inner rows with s4-d8's own builder
(code/dbl/dbl.py and forms.py, copied unchanged from research/search2/s4-d8/code) and check that the
columns are exactly the catalogue row's (same SHA-256).  Writes data/dbl_structure.json: per row the
inner label, the block code's X stabilisers S (rows over n_b positions), n_b, the labels, and the
layout X1 = [0, ns), X2 = [ns, 2 ns), Y = [2 ns, 2 ns + n_t).

    python code/dbl/rebuild.py
"""
import hashlib, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
TOP = HERE.parent.parent
ROOT = Path("/Users/shubhamjain/Documents/IBM internship/Shraddha (Magic states)")
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "magic-state-factory-repo" / "transversal_t_codes"))
sys.path.insert(0, str(ROOT / "magic-state-factory-repo" / "master_catalog"))
import dbl, forms                                   # noqa: E402
import build_codes as BC                            # noqa: E402
import catalogfile as CF                            # noqa: E402

ROWS = {"318.2.9.a": ("154.2.7.a", "gong41"), "451.3.9.a": ("205.3.7.a", "gong41"),
        "459.2.9.a": ("213.2.7.a", "gong41"), "410.2.11.a": ("222.2.8.a", "qr47"),
        "270.1.10.a": ("176.1.8.a", "qr47")}


def block(name):
    if name == "gong41":
        return BC.gong_self_dual(41), 41, 9
    if name == "qr47":
        return BC.quantum_qr(47), 47, 11
    raise SystemExit(name)


def main():
    cat = {r["catalog_label"]: r for r in CF.load_all()["factories"]}
    out = {}
    for lab, (inner, bname) in ROWS.items():
        x = cat[inner]
        rows = dbl.rows_from_cols(x["columns"], x["N"])
        L, C = rows[:x["k"]], rows[x["k"]:]
        E, nb, db = block(bname)
        labs = forms.rep_labels(L)
        S, M = [], [0] * len(L)
        for b, l in enumerate(labs):
            S += dbl.shift_rows(E, nb * b)
            for i in range(len(L)):
                if (l >> i) & 1:
                    M[i] |= ((1 << nb) - 1) << (nb * b)
        assert not dbl.weak_ok(S, M)
        f = dbl.double(S, M, nb * len(labs), C, L, x["n"])
        dig = hashlib.sha256(json.dumps(f["columns"], separators=(",", ":")).encode()).hexdigest()
        same = dig == cat[lab]["columns_sha256"] if "columns_sha256" in cat[lab] else \
            f["columns"] == cat[lab]["columns"]
        print(lab, "rebuilt", f["n"], f["k"], f["N"], "digest", dig[:12], "equal to catalogue:", same,
              "| sorted equal:", sorted(f["columns"]) == sorted(cat[lab]["columns"]))
        out[lab] = {"inner": inner, "inner_columns_sha256": hashlib.sha256(json.dumps(
                    x["columns"], separators=(",", ":")).encode()).hexdigest(),
                    "block": bname, "n_b": nb, "d_b": db, "S": [str(v) for v in E], "labels": labs,
                    "ns": nb * len(labs), "n_t": x["n"], "k": x["k"], "rebuilt_sha256": dig,
                    "catalogue_equal": same}
    (TOP / "data" / "dbl_structure.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
