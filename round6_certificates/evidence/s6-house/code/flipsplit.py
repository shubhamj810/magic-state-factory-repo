#!/usr/bin/env python3
"""Harmful sets of one weight split by the outputs they flip, two ways.

    python flipsplit.py LABEL W [--second plan|macw]

1. mitml --list (code/acount.py, every set re-checked by its own XOR): the output XOR of every listed set
   is tallied, giving Inner(W, v) for every pattern v.
2. for each output i, a derived row in which output i is the only output and the other outputs are
   checks: its harmful W-sets are exactly the sets whose flip pattern is e_i.  They are counted by the
   plan kernel (W <= 8) or by MacWilliams (code/wdist/macw.py --keep-out i), and must equal the tally.
Writes data/flipsplit.jsonl.
"""
import argparse, gzip, hashlib, json, subprocess, sys
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
TOP = HERE.parent
PY = sys.executable


def derived(row, i):
    k, N = row["k"], row["N"]
    order = [i] + [j for j in range(k) if j != i] + list(range(k, N))
    new = {q: p for p, q in enumerate(order)}
    cols = [sorted(new[q] for q in c) for c in row["columns"]]
    return {"label": f"{row['label']}.keep{i}", "k": 1, "N": N, "columns": cols,
            "columns_sha256": hashlib.sha256(json.dumps(cols, separators=(",", ":")).encode()).hexdigest()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("label"); ap.add_argument("w", type=int)
    ap.add_argument("--second", default="plan", choices=["plan", "macw"])
    a = ap.parse_args()
    row = json.loads((TOP / "data" / "rows" / f"{a.label}.json").read_text())
    row["label"] = a.label
    lst = TOP / "data" / "lists" / f"{a.label}_w{a.w}.txt.gz"
    if not lst.exists():
        subprocess.run([PY, str(HERE / "acount.py"), a.label, str(a.w), "--out", str(TOP / "data" / "counts_inner.jsonl")], check=True)
    tally = Counter()
    for line in gzip.decompress(lst.read_bytes()).decode().splitlines():
        if line.strip():
            words = [int(x, 16) for x in line.split(":")[1].split()]
            tally[sum(v << (64 * j) for j, v in enumerate(words))] += 1
    ddir = TOP / "data" / "rows_derived"
    ddir.mkdir(exist_ok=True)
    second = {}
    for i in range(row["k"]):
        d = derived(row, i)
        (ddir / f"{d['label']}.json").write_text(json.dumps(d))
        if a.second == "plan":
            out = subprocess.run([PY, str(HERE / "acount.py"), d["label"], str(a.w), "--rows", str(ddir), "--mitml", "none",
                                  "--plan", "--out", str(TOP / "data" / "counts_derived.jsonl")],
                                 check=True, capture_output=True, text=True).stdout
            second[i] = json.loads(out.strip().splitlines()[-1])["A_w"]
        else:
            out = subprocess.run([PY, str(HERE / "wdist" / "macw.py"), d["label"], str(a.w), "--rows", str(ddir)],
                                 check=True, capture_output=True, text=True).stdout
            second[i] = json.loads(out.strip().splitlines()[-1])["A_w"]
    agree = all(second[i] == tally.get(1 << i, 0) for i in second)
    rec = {"label": a.label, "weight": a.w, "columns_sha256": row["columns_sha256"], "by_flip": {format(v, f"0{row['k']}b")[::-1]: c for v, c in sorted(tally.items())},
           "total": sum(tally.values()), "single_output_second_program": {str(i): second[i] for i in second},
           "second": a.second, "agree": agree}
    with open(TOP / "data" / "flipsplit.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps(rec))


if __name__ == "__main__":
    main()
