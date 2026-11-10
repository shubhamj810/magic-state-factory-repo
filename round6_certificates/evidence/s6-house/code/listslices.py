#!/usr/bin/env python3
"""mitml --list run in slices on several processes (each harmful set is written by the one partition that
holds its canonical split, so the slice lists are disjoint and their union is the list), concatenated in
slice order, every set re-checked by its own XOR (round1_certificates/count_weight.check_list).
    python listslices.py LABEL W Q M WORKERS   -> data/lists/LABEL_wW.txt.gz, data/counts.jsonl (mode list-sliced)"""
import gzip, hashlib, json, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from math import comb
from pathlib import Path
HERE = Path(__file__).resolve().parent
TOP = HERE.parent
sys.path.insert(0, str(HERE))
import acount
lab, w, q, m, workers = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
row = json.loads((TOP / "data" / "rows" / f"{lab}.json").read_text())
p = TOP / "tmp" / f"{lab}.ls.bin"
sw = acount.write_problem(p, row["columns"], row["k"], row["N"])
binary = HERE / "mitml" / f"mitml{min(v for v in (1, 2, 3) if sw <= v)}"
t0 = time.time()
def one(i):
    out = TOP / "tmp" / f"{lab}.w{w}.s{i}.txt"
    r = json.loads(subprocess.run([str(binary), str(p), str(w), "--list", str(out), "--parts", str(q), "--slice", str(i), str(m)],
                                  check=True, capture_output=True, text=True).stdout)
    return r, out
with ThreadPoolExecutor(workers) as ex:
    res = list(ex.map(one, range(m)))
assert all(r["complete"] == 1 for r, _ in res)
div = comb(w, (w + 1) // 2)
harm = sum(r["harmful_raw"] for r, _ in res); acc = sum(r["accepted_raw"] for r, _ in res)
assert harm % div == 0 and acc % div == 0
raw = b"".join(o.read_bytes() for _, o in res)
for _, o in res:
    o.unlink()
lst = TOP / "data" / "lists" / f"{lab}_w{w}.txt"
lst.parent.mkdir(exist_ok=True)
lst.write_bytes(raw)
distinct = acount.CW.check_list(lst, row["columns"], row["k"], w)
assert distinct == harm // div == sum(r["listed"] for r, _ in res)
gz = lst.with_name(lst.name + ".gz"); gz.write_bytes(gzip.compress(raw, compresslevel=9, mtime=0)); lst.unlink()
rec = {"label": lab, "n": len(row["columns"]), "k": row["k"], "N": row["N"], "weight": w, "columns_sha256": row["columns_sha256"],
       "mitml": {"mode": "list-sliced", "harmful": harm // div, "accepted": acc // div, "listed": distinct, "rechecked": distinct,
                 "parts_log2": q, "slices": m, "cpu_seconds": round(sum(r["seconds"] for r, _ in res), 1),
                 "wall_seconds": round(time.time() - t0, 1), "list_file": f"data/lists/{gz.name}",
                 "list_sha256": hashlib.sha256(raw).hexdigest(), "mitml_sha256": acount.sha(acount.MITML_SRC)},
       "agree": None, "A_w": harm // div, "date": time.strftime("%Y-%m-%d %H:%M")}
with open(TOP / "out" / "counts.jsonl" if (TOP / "out").exists() else TOP / "data" / "counts.jsonl", "a") as f:
    f.write(json.dumps(rec) + "\n")
print(json.dumps(rec))
