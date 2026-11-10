#!/usr/bin/env python3
"""Time slices of a mitml count to estimate the cost of the whole count.
    python timeslice.py LABEL W Q M I [I ...]   (partitions 2^Q, M slices, run slices I)"""
import json, subprocess, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
TOP = HERE.parent
sys.path.insert(0, str(HERE))
import acount
lab, w, q, m = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
row = json.loads((TOP / "data" / "rows" / f"{lab}.json").read_text())
p = TOP / "tmp" / f"{lab}.ts.bin"
sw = acount.write_problem(p, row["columns"], row["k"], row["N"])
binary = HERE / "mitml" / f"mitml{min(v for v in (1, 2, 3) if sw <= v)}"
tot = 0.0
for i in sys.argv[5:]:
    t0 = time.time()
    r = json.loads(subprocess.run([str(binary), str(p), str(w), "--count", "--parts", str(q), "--slice", i, str(m)],
                                  check=True, capture_output=True, text=True).stdout)
    tot += r["seconds"]
    print(json.dumps({"label": lab, "w": w, "parts_log2": q, "slices": m, "slice": int(i), "seconds": r["seconds"],
                      "accepted_raw": r["accepted_raw"], "harmful_raw": r["harmful_raw"]}), flush=True)
k = len(sys.argv) - 5
rec = {"label": lab, "w": w, "parts_log2": q, "slices": m, "timed": k, "mean_seconds": tot / k,
       "estimate_core_seconds": tot / k * m, "estimate_core_hours": round(tot / k * m / 3600, 1)}
print(json.dumps(rec))
with open(TOP / "data" / "timeslice.jsonl", "a") as f:
    f.write(json.dumps(rec) + "\n")
