#!/usr/bin/env python3
"""tropidist's pipeline (dp=2, as in research/tropidist/ and research/zaratan/) on a row whose columns are given
in a chosen order, so that its dense DP starts from an order of small cut rank (doubled_order.py).

The distance does not depend on the column order.  The row is exported with its columns permuted
(column i of the instance is column order[i] of the catalogue row); tropidist's pipeline still tries
its own orders as well (the given one, its reverse, two greedy ones) and keeps the cheapest.  A returned
fault is mapped back to the catalogue's column indices and re-checked there with faultcore.Circuit.harmful
and by the literal XOR of the wire masks.

    python dp_perm.py estimate ROWID                 tropidist's cost estimate for the stored and the new order
                                                     (tropidist venv; nothing is allocated)
    python dp_perm.py run ROWID --limit S --table-gb G --threads T --mem-mb M     (catalogue venv)
"""
import argparse
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CANDS = [Path("/Users/shubhamjain/Documents/IBM internship/Shraddha (Magic states)/magic-state-factory-research/research"),
         Path(os.environ.get("MSF", "/scratch/zt1/project/vva-prj/user/sjn/msf")) / "magic-state-factory-research" / "research"]
RESEARCH = next(p for p in CANDS if p.exists())


def rows_for(rid):
    row = json.loads((HERE / "data" / "rows" / f"{rid}.json").read_text())
    order = json.loads((HERE / "data" / "orders" / f"{rid}.json").read_text())
    n = len(row["columns"])
    assert sorted(order) == list(range(n))
    inv = {c: i for i, c in enumerate(order)}
    base = {"catalog_label": rid, "n": row["n"], "k": row["k"], "N": row["N"], "regimes": [], "discovery": None,
            "d": row["d"], "d_is_exact": row["d_is_exact"], "d_upper": row["d_upper"], "d_witness": row["d_witness"],
            "d_certified": row["d_certified"], "d_certified_is_exact": row["d_certified_is_exact"],
            "columns": row["columns"]}
    perm = dict(base)
    perm["catalog_label"] = rid + ".ord"
    perm["columns"] = [row["columns"][c] for c in order]
    perm["d_witness"] = sorted(inv[j] for j in row["d_witness"]) if row["d_witness"] else None
    return row, base, perm, order


def estimate(rid):
    sys.path.insert(0, str(RESEARCH / "tropidist"))
    root = Path(os.environ.get("TROPIDIST_SRC", RESEARCH.parents[1] / "tropidist-src"))
    sys.path.insert(0, str(root))
    from cdist import auto
    from cdist.problem import Problem
    row, base, perm, order = rows_for(rid)
    for name, r in (("stored", base), ("new", perm)):
        k, N = r["k"], r["N"]
        h, l = [], []
        for c in r["columns"]:
            a = b = 0
            for q in c:
                if q < k:
                    b |= 1 << q
                else:
                    a |= 1 << (q - k)
            h.append(a)
            l.append(b)
        p = Problem(name=name, nrows=N - k, nobs=k, h=h, l=l, row_meta=[[x] for x in range(N - k)])
        est = auto.estimate(p, threads=1, seeds=2, time_limit=60, max_table_bytes=None)
        print(json.dumps({"id": rid, "order": name, "cut_rank": est["cut_rank"], "peak_bits": est.get("peak_bits"),
                          "table_gib": round((1 << est["peak_bits"]) / 2 ** 30, 3) if est.get("peak_bits") else None,
                          "work": est.get("work"), "predicted_seconds": est.get("predicted_seconds")}), flush=True)


def run(a):
    sys.path.insert(0, str(RESEARCH / "tropidist"))
    import tropirun as T
    import faultcore as FC
    T.THREADS = a.threads
    if a.kill_margin is not None:
        T.KILL_MARGIN = a.kill_margin
    T.CPU_ENV["OMP_NUM_THREADS"] = str(a.threads)
    row, base, perm, order = rows_for(a.rowid)
    commit = T.tropidist_commit()
    records = HERE / "data" / "dp_records"
    config = f"dp=2,table_gb={a.table_gb}" + (f",dp_fast={a.dp_fast}" if a.dp_fast else "")
    res = T.run_row(perm, a.limit, records, commit, mem_limit_mb=a.mem_mb, config=config)
    res["sha256_stored_order"] = row["sha256"]
    res["order_file"] = f"data/orders/{a.rowid}.json"
    wit = res.get("witness")
    if wit is not None:
        orig = sorted(order[i] for i in wit)
        circ = FC.Circuit(row["columns"], row["k"], row["N"])
        acc = 0
        for j in orig:
            for q in row["columns"][j]:
                acc ^= 1 << q
        res["witness_catalogue_order"] = orig
        res["witness_catalogue_check"] = {"faultcore_harmful": bool(circ.harmful(orig)),
                                          "literal_harmful": acc != 0 and (acc >> row["k"]) == 0}
    res["host"] = os.uname().nodename
    with open(HERE / "data" / "dp_perm.jsonl", "a") as f:
        f.write(json.dumps(res) + "\n")
    print(json.dumps({k: res.get(k) for k in ("label", "status", "lower_bound", "upper_bound", "witness_check",
                                              "witness_catalogue_check", "wall_seconds", "peak_group_rss_mb",
                                              "runner_note", "how")}), flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "estimate":
        estimate(sys.argv[2])
    else:
        ap = argparse.ArgumentParser()
        ap.add_argument("mode")
        ap.add_argument("rowid")
        ap.add_argument("--limit", type=float, required=True)
        ap.add_argument("--table-gb", type=int, required=True)
        ap.add_argument("--threads", type=int, default=1)
        ap.add_argument("--mem-mb", type=float, required=True)
        ap.add_argument("--kill-margin", type=float, default=None)
        ap.add_argument("--dp-fast", type=int, default=0, help="pipeline dp_fast: run the DP first if predicted below")
        run(ap.parse_args())
