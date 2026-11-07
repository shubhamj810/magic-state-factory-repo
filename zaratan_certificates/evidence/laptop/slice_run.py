#!/usr/bin/env python3
"""Run ONE slice of one weight of the MITM kernel on a cached row; the caller runs the other slices
(possibly at the same time) and combines them: a weight is clean only if every slice is complete and
clean.  Appends one line to ../data/mitm_slices.jsonl.

usage: python3 slice_run.py LABEL W I M
"""
import json, sys, tempfile, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import mitm as MM
label, w, i, m = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
row = json.loads((MM.PLAN / "data" / "rows" / f"{label}.json").read_text())
syn, out = MM.masks(row["columns"], row["k"])
with tempfile.TemporaryDirectory(dir=MM.PLAN / "tmp") as tmp:
    p = Path(tmp) / "p.bin"
    MM.write_problem(p, syn, out, row["k"])
    t = time.time()
    res = MM.run_bin(p, w, False, ["--slice", str(i), str(m)])
rec = {"label": label, "w": w, "slice": [i, m], "result": res, "wall": round(time.time() - t, 1)}
with open(MM.PLAN / "data" / "mitm_slices.jsonl", "a") as f:
    f.write(json.dumps(rec) + "\n")
print(json.dumps(rec))
