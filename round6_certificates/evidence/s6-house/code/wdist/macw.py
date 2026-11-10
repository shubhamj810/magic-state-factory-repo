#!/usr/bin/env python3
"""B_w of the kernel of a set of a row's wire rows, by MacWilliams from the weight distribution of their
span (wdist.c visits every word of the span), and A_w = B_w(ker H) - B_w(ker G) (the definition in
master_catalog/errorcoeff.py), with exact integer Krawtchouk sums written here.

    python macw.py LABEL W [--rows DIR] [--keep-out i,j]   (--keep-out: only these outputs stay outputs;
                                                           the others join the checks, so A_w counts the
                                                           sets whose flips lie in the kept outputs only)
"""
import argparse, hashlib, json, os, subprocess, sys, time
from math import comb
from pathlib import Path
HERE = Path(__file__).resolve().parent
TOP = HERE.parent.parent


def basis(vecs):
    piv = {}
    for v in vecs:
        x = v
        while x:
            p = x.bit_length() - 1
            if p in piv:
                x ^= piv[p]
            else:
                piv[p] = x
                break
    return list(piv.values())


def kraw(w, i, n):
    return sum((-1) ** j * comb(i, j) * comb(n - i, w - j) for j in range(min(i, w) + 1))


def dist(vecs, n, binary):
    b = basis(vecs)
    W = (n + 63) // 64
    lines = [f"{n} {len(b)}"] + [" ".join(f"{(v >> (64 * w)) & (2**64 - 1):x}" for w in range(W)) for v in b]
    t0 = time.time()
    out = subprocess.run([str(binary)], input="\n".join(lines) + "\n", capture_output=True, text=True, check=True).stdout
    D = [int(x) for x in out.split()]
    assert len(D) == n + 1 and sum(D) == 2 ** len(b)
    return D, len(b), time.time() - t0


def dual_B(D, n, w):
    tot = sum(d * kraw(w, i, n) for i, d in enumerate(D) if d)
    size = sum(D)
    assert tot % size == 0
    return tot // size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("label"); ap.add_argument("w", type=int)
    ap.add_argument("--rows", default=str(TOP / "data" / "rows"))
    ap.add_argument("--keep-out", default=None)
    ap.add_argument("--binary", default=str(HERE / "wdist"))
    ap.add_argument("--out", default=str(TOP / "data" / "macw.jsonl"))
    a = ap.parse_args()
    row = json.loads((Path(a.rows) / f"{a.label}.json").read_text())
    cols, k, N = row["columns"], row["k"], row["N"]
    dig = hashlib.sha256(json.dumps(cols, separators=(",", ":")).encode()).hexdigest()
    assert dig == row["columns_sha256"]
    n = len(cols)
    rows = [0] * N
    for j, c in enumerate(cols):
        for q in c:
            rows[q] |= 1 << j
    keep = list(range(k)) if a.keep_out is None else [int(x) for x in a.keep_out.split(",")]
    H = rows[k:] + [rows[i] for i in range(k) if i not in keep]
    G = rows
    DH, rH, tH = dist(H, n, a.binary)
    DG, rG, tG = dist(G, n, a.binary)
    BH, BG = dual_B(DH, n, a.w), dual_B(DG, n, a.w)
    rec = {"label": a.label, "columns_sha256": dig, "weight": a.w, "keep_out": keep, "rank_H": rH, "rank_G": rG,
           "B_kerH": BH, "B_kerG": BG, "A_w": BH - BG, "seconds": [round(tH, 1), round(tG, 1)],
           "wdist_sha256": hashlib.sha256((HERE / "wdist.c").read_bytes()).hexdigest(),
           "threads": os.environ.get("OMP_NUM_THREADS"), "date": time.strftime("%Y-%m-%d %H:%M")}
    with open(a.out, "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps(rec))


if __name__ == "__main__":
    main()
