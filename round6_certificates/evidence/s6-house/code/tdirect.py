#!/usr/bin/env python3
"""tropidist's weight-bounded search called directly, at one threshold, on a factory.

The factory problem is the one of research/tropidist/tropirun.py: H = check rows (wires k..N-1),
L = output rows (wires 0..k-1), one column per rotation in the stored order.  This script calls
cdist.search (tropidist commit b03ec2d4, read-only checkout) without the benchmark pipeline, so the
options the pipeline fixes can be varied:

  --K K               the single threshold: "exhausted" proves that no harmful fault of weight <= K
                      exists among the faults the anchors cover; "found" returns one of weight <= K
  --task-depth T      prefix depth of the kernel's task list (the pipeline uses up to 3 or 4)
  --labelfree 0|1     label-free search (forced above 64 outputs)
  --cover 0|1         covering-LP pruning (the pipeline's cover=1)
  --exclusions 0|1    column-pair exclusions (the pipeline builds them)
  --k-table k         depth of the completion table (the pipeline's k_table=2)
  --anchors SPEC      all (default) | sample:M[:seed] (M anchors spread evenly, natural rank, for
                      cost-per-anchor estimates) | cols:i,j,...
  --rank natural|equal  equal: nothing is forbidden, so a search from anchor v covers every
                      fault containing v (the "can column v be part of a light fault" test)
  --problem-file F    a JSON {"k","N","columns"} instead of a catalogue row

Every returned witness is re-checked with the catalogue's faultcore.Circuit.harmful (code shared
with neither tropidist nor this file's problem export) and by the literal XOR of wire masks.
One JSON line per run is appended to data/pilots.jsonl.

usage: PYTHONDONTWRITEBYTECODE=1 nice -n 19 <tropidist venv python> tdirect.py LABEL --K 6 [options]
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import resource
import sys
import time
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
HERE = Path(__file__).resolve().parent
# research/search2/distances copy: the laptop folder or the Zaratan workspace $MSF, whichever exists
ROOT = next(p for p in (Path("/Users/shubhamjain/Documents/IBM internship/Shraddha (Magic states)"),
                        Path(os.environ.get("MSF", "/scratch/zt1/project/vva-prj/user/sjn/msf"))) if p.exists())
TROPI = Path(os.environ.get("TROPIDIST_SRC", ROOT / "tropidist-src"))
CATREPO = Path(os.environ.get("MSF_CATREPO", ROOT / "magic-state-factory-repo"))
sys.path.insert(0, str(TROPI))
sys.path.insert(0, str(CATREPO / "master_catalog"))

import numpy as np                                   # noqa: E402
from cdist import search                             # noqa: E402
from cdist.problem import Problem                    # noqa: E402
import faultcore as FC                               # noqa: E402

ROWS = HERE / "data" / "rows"


def load_row(label: str) -> dict:
    """A main-file catalogue row, cached as data/rows/<label>.json (columns, k, N, d fields)."""
    cache = ROWS / f"{label}.json"
    if cache.exists():
        return json.loads(cache.read_text())
    blob = json.loads((CATREPO / "master_catalog" / "master_catalog.json").read_text())
    for row in blob["factories"]:
        if row["catalog_label"] == label:
            keep = {key: row.get(key) for key in ("catalog_label", "n", "k", "N", "d", "d_is_exact", "d_upper",
                                                  "d_witness", "d_certified", "d_certified_is_exact", "columns")}
            ROWS.mkdir(parents=True, exist_ok=True)
            cache.write_text(json.dumps(keep))
            return keep
    raise SystemExit(f"{label}: not in the main catalogue file")


def problem_of(row: dict) -> Problem:
    k, N = row["k"], row["N"]
    h, l = [], []
    for column in row["columns"]:
        assert list(column) == sorted(set(column))
        a = b = 0
        for q in column:
            assert 0 <= q < N
            if q < k:
                b |= 1 << q
            else:
                a |= 1 << (q - k)
        h.append(a)
        l.append(b)
    return Problem(name=row.get("catalog_label", "problem"), nrows=N - k, nobs=k, h=h, l=l,
                   row_meta=[[r] for r in range(N - k)])


def our_check(row: dict, cols) -> dict:
    circuit = FC.Circuit(row["columns"], row["k"], row["N"])
    acc = 0
    for j in cols:
        for q in row["columns"][j]:
            acc ^= 1 << q
    return {"faultcore_harmful": circuit.harmful(cols), "literal_harmful": acc != 0 and (acc >> row["k"]) == 0,
            "distinct": len(set(cols)) == len(cols)}


def peak_rss_mb() -> float:
    ru = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return ru / (1024 * 1024) if platform.system() == "Darwin" else ru / 1024


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("label")
    ap.add_argument("--K", type=int, required=True)
    ap.add_argument("--task-depth", type=int, default=1)
    ap.add_argument("--labelfree", type=int, default=-1)
    ap.add_argument("--cover", type=int, default=1)
    ap.add_argument("--exclusions", type=int, default=1)
    ap.add_argument("--k-table", type=int, default=2)
    ap.add_argument("--anchors", default="all")
    ap.add_argument("--rank", default="natural", choices=("natural", "equal"))
    ap.add_argument("--time-limit", type=float, default=1500.0)
    ap.add_argument("--problem-file", default=None)
    ap.add_argument("--tag", default="")
    ap.add_argument("--out", default=str(HERE / "data" / "tropidist_runs.jsonl"))
    a = ap.parse_args(argv)

    row = json.loads(Path(a.problem_file).read_text()) if a.problem_file else load_row(a.label)
    p = problem_of(row)
    n = p.ncols
    t0 = time.time()
    labelfree = None if a.labelfree < 0 else bool(a.labelfree)
    if a.anchors == "all":
        anchors = None
    elif a.anchors.startswith("sample:"):
        parts = a.anchors.split(":")
        m = int(parts[1])
        step = max(1, n // m)
        anchors = list(range(0, n, step))[:m]
    elif a.anchors.startswith("cols:"):
        anchors = [int(x) for x in a.anchors[5:].split(",")]
    else:
        raise SystemExit("bad --anchors")
    rank = [0] * n if a.rank == "equal" else None
    S = search.Searcher(p, rank=rank, anchors=anchors, labelfree=labelfree)
    n_ex = S.build_exclusions() if a.exclusions else 0
    t_ex = time.time() - t0
    tab = search.Table(p, a.k_table, labelfree=S.labelfree)
    S.add_table(tab, exact=True)
    t_setup = time.time() - t0
    try:
        r = S.search(a.K, task_depth=a.task_depth, time_limit=a.time_limit, exclusions=bool(a.exclusions),
                     cover=bool(a.cover))
    finally:
        tab.free()
    checks = [our_check(row, s) for s in r["solutions"][:5]]
    for s, c in zip(r["solutions"], checks):
        assert search.verify(p, s), "tropidist's own verify rejected its solution"
        assert c["faultcore_harmful"] and c["literal_harmful"] and c["distinct"], (s, c)
    rec = {"label": a.label, "sha256": row.get("sha256"), "tag": a.tag, "threads": os.environ.get("OMP_NUM_THREADS"), "host": platform.node(), "n": n, "k": row["k"], "r": row["N"] - row["k"], "K": a.K,
           "status": r["status"], "best": r["best"],
           "witness": list(r["solutions"][0]) if r["solutions"] else None, "witness_checks": checks[:1],
           "search_seconds": round(r["seconds"], 3), "setup_seconds": round(t_setup, 3),
           "exclusion_seconds": round(t_ex, 3), "exclusion_pairs": n_ex,
           "table_entries": tab.entries, "k_table": a.k_table, "labelfree": S.labelfree,
           "cover": a.cover, "task_depth": a.task_depth, "tasks": r["tasks"],
           "anchors": "all" if anchors is None else (a.anchors if len(anchors) > 20 else anchors),
           "n_anchors": n if anchors is None else len(anchors), "rank": a.rank,
           "nodes": r["nodes"], "lookups": r["lookups"], "hits": r["hits"], "false_hits": r["false_hits"],
           "cover_pruned": r["cover_pruned"], "time_limit": a.time_limit,
           "peak_rss_mb": round(peak_rss_mb(), 1), "wall_seconds": round(time.time() - t0, 3)}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps({key: rec[key] for key in rec if key not in ("nodes",)}))


if __name__ == "__main__":
    main()
