#!/usr/bin/env python3
"""Re-count chosen slices of a certificate (data/certs/LABEL_wW.json) with mydist, which shares no code
with mitml: slice i = harmful W-sets whose smallest column is i = {i} + E, E a (W-1)-set of columns > i.
    python slicecheck.py LABEL W I [I ...]   -> data/slicecheck.jsonl"""
import json, sys, time
from math import comb
from pathlib import Path
HERE = Path(__file__).resolve().parent
TOP = HERE.parent
ROOT = Path("/Users/shubhamjain/Documents/IBM internship/Shraddha (Magic states)")
sys.path.insert(0, str(ROOT / "magic-state-factory-repo" / "round1_certificates" / "evidence" / "small_review"))
import mydist
lab, w = sys.argv[1], int(sys.argv[2])
cert = json.loads((TOP / "data" / "certs" / f"{lab}_w{w}.json").read_text())
want = {s[0]: s[1] for s in cert["slices"]}
row = json.loads((TOP / "data" / "rows" / f"{lab}.json").read_text())
P = mydist.Packed(row["columns"], row["k"], row["N"])
for i in map(int, sys.argv[3:]):
    t0 = time.time()
    a, b = mydist.split(w - 1)
    r = mydist.join(P, a, b, U=list(range(i + 1, P.n)), F=(i,), stop_first=False, count=True)
    assert r["complete_pass"] and r["raw"] % comb(w - 1, a) == 0
    got = r["raw"] // comb(w - 1, a)
    rec = {"label": lab, "weight": w, "slice": i, "certificate": want.get(i, 0), "mydist": got, "agree": got == want.get(i, 0),
           "seconds": round(time.time() - t0, 1)}
    print(json.dumps(rec), flush=True)
    with open(TOP / "data" / "slicecheck.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")
