#!/usr/bin/env python3
"""Anneal a column order of one of my rows with cutsa (copied from research/search2/distances) and keep it
in data/orders/LABEL.json if its (max, count at max, sum) beats the current one.
    python cutsa_run.py LABEL SEED SECONDS"""
import json, subprocess, sys, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
TOP = HERE.parent
sys.path.insert(0, str(HERE))
from cutsurvey import profile, vecs_of
lab, seed, secs = sys.argv[1:4]
row = json.loads((TOP / "data" / "rows" / f"{lab}.json").read_text())
n = len(row["columns"])
of = TOP / "data" / "orders" / f"{lab}.json"
order = json.loads(of.read_text()) if of.exists() else list(range(n))
with tempfile.NamedTemporaryFile("w", dir=TOP / "tmp", suffix=".txt", delete=False) as f:
    f.write(f"{n} {row['N']}\n")
    for c in row["columns"]:
        f.write(f"{len(c)} {' '.join(map(str, c))}\n")
    f.write(" ".join(map(str, order)) + "\n")
    name = f.name
r = subprocess.run([str(HERE / "cutsa"), name, seed, secs], capture_output=True, text=True)
Path(name).unlink()
new = [int(x) for x in r.stdout.split("\n")[0].split()]
assert sorted(new) == list(range(n))
def sc(o, which):
    v = vecs_of(row, which); p = profile([v[i] for i in o]); m = max(p); return (m, p.count(m), sum(p))
a, b = sc(order, "G"), sc(new, "G")
print(lab, "G:", a, "->", b, "| H:", sc(order, "H"), "->", sc(new, "H"))
if b < a:
    of.write_text(json.dumps(new)); print("saved")
