#!/usr/bin/env python3
"""Brute-force count, on the factory's own columns (no fibre theory), of the zero-syndrome sets of weight W = 2A+1
supported on the columns of two fibres z1, z2 (point p = y + 256 z, columns <-> sorted complement of P).
For every pair: sweep.c odd mode (A), table of <= A subsets, (A+1)-subsets looked up.  With no zero set below W,
HITS = C(W, A) * (number of weight-W zero sets).  Sum over pairs = (two-fibre sets) + 7 * (one-fibre sets).

    python pairfib.py PROBLEM.json A [z1 z2 ...pairs as "z1,z2"]
"""
import itertools
import json
import struct
import subprocess
import sys
import time
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dist as DI  # noqa: E402  (masks, project only)


def main(path, A, pairs):
    t0 = time.time()
    d = json.load(open(path))
    k, N, cols = d["k"], d["N"], d["columns"]
    P = sorted(d["points"])
    comp = [x for x in range(2048) if x not in set(P)]
    syn, out = DI.masks(cols, k)
    proj = DI.project(syn, N - k, 4242)
    total = 0
    for (z1, z2) in pairs:
        idx = [j for j, p in enumerate(comp) if (p >> 8) in (z1, z2)]
        sub = [proj[j] for j in idx]
        bp = HERE.parent / "tmp" / f"pf_{Path(path).stem}_{z1}{z2}.bin"
        with open(bp, "wb") as f:
            f.write(struct.pack("<I", len(sub)))
            f.write(struct.pack(f"<{len(sub)}Q", *sub))
        r = subprocess.run([str(DI.BIN), "odd", str(bp), str(A)], capture_output=True, text=True)
        bp.unlink()
        summ = [l for l in r.stdout.split("\n") if l.startswith("TABLE")][0].split()
        dups, hits = int(summ[3]), int(summ[7])
        total += hits
        print(json.dumps({"pair": [z1, z2], "columns": len(idx), "dups": dups, "hits": hits,
                          "sets": hits / comb(2 * A + 1, A), "t": round(time.time() - t0, 1)}), flush=True)
    print(json.dumps({"total_hits": total, "total_sets_counted": total / comb(2 * A + 1, A),
                      "seconds": round(time.time() - t0, 1)}), flush=True)


if __name__ == "__main__":
    path, A = sys.argv[1], int(sys.argv[2])
    if len(sys.argv) > 3:
        pairs = [tuple(int(t) for t in s.split(",")) for s in sys.argv[3:]]
    else:
        pairs = list(itertools.combinations(range(8), 2))
    main(path, A, pairs)
