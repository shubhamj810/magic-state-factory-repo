#!/usr/bin/env python3
"""Exhaustive distance floor by meet in the middle, own code (sweep.c), no catalogue code.

    python dist.py PROBLEM.json A [--odd] [--bb B] [--seed S]

Without --odd: proves that no nonempty set of <= 2A columns has zero check syndrome (all subset XORs of size
<= A distinct).  With --odd: also sets of size 2A+1 (table of size <= A subsets in memory, (A+1)-subsets
looked up).  Every projected collision is re-checked with the full syndromes; each genuine zero-syndrome set
is printed with its output flips (harmful iff nonzero).
"""
import itertools
import json
import random
import struct
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BIN = HERE.parent / "tmp" / "sweep"


def masks(cols, k):
    syn, out = [], []
    for c in cols:
        s = o = 0
        for q in c:
            if q < k:
                o |= 1 << q
            else:
                s |= 1 << (q - k)
        syn.append(s)
        out.append(o)
    return syn, out


def project(syn, nchecks, seed):
    rng = random.Random(seed)
    R = [rng.getrandbits(64) for _ in range(nchecks)]
    proj = []
    for s in syn:
        v = 0
        q = 0
        while s:
            if s & 1:
                v ^= R[q]
            s >>= 1
            q += 1
        proj.append(v)
    return proj


def run(cols, k, N, A, odd=False, bb=4, seed=12345, tag="p"):
    t0 = time.time()
    syn, out = masks(cols, k)
    proj = project(syn, N - k, seed)
    path = HERE.parent / "tmp" / f"{tag}_{seed}.bin"
    with open(path, "wb") as f:
        f.write(struct.pack("<I", len(proj)))
        f.write(struct.pack(f"<{len(proj)}Q", *proj))
    mode = ["odd", str(path), str(A)] if odd else ["dist", str(path), str(A), str(bb)]
    r = subprocess.run([str(BIN)] + mode, capture_output=True, text=True)
    lines = r.stdout.split("\n")
    summary = [l for l in lines if l.startswith("TOTAL") or l.startswith("TABLE")]
    vals = sorted({int(l.split()[1], 16) for l in lines if l.startswith("DUP") or l.startswith("HIT")})
    res = {"n": len(cols), "k": k, "N": N, "A": A, "odd": odd, "summary": summary, "collisions": len(vals),
           "seed": seed}
    genuine = []
    if vals:
        sets = {}
        for c0 in range(0, len(vals), 2000):
            m = ["find", str(path), str(A + 1 if odd else A)] + [f"{v:x}" for v in vals[c0:c0 + 2000]]
            rr = subprocess.run([str(BIN)] + m, capture_output=True, text=True)
            for l in rr.stdout.split("\n"):
                if l.startswith("SET"):
                    v, idx = l[4:].split(":")
                    sets.setdefault(int(v, 16), []).append(tuple(int(t) for t in idx.split()))
        for v in vals:
            group = sets.get(v, [])
            if v == 0:
                group = group + [()]
            for a_, b_ in itertools.combinations(group, 2):
                F = sorted(set(a_) ^ set(b_))
                s = o = 0
                for j in F:
                    s ^= syn[j]
                    o ^= out[j]
                if F and s == 0:
                    genuine.append({"fault": F, "weight": len(F), "flips": bin(o).count("1")})
    res["zero_syndrome_sets"] = genuine[:20]
    res["n_zero_syndrome_sets"] = len({tuple(g["fault"]) for g in genuine})
    res["min_weight_found"] = min((g["weight"] for g in genuine), default=None)
    res["min_harmful_weight_found"] = min((g["weight"] for g in genuine if g["flips"]), default=None)
    res["seconds"] = round(time.time() - t0, 1)
    path.unlink()
    return res


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("problem")
    ap.add_argument("A", type=int)
    ap.add_argument("--odd", action="store_true")
    ap.add_argument("--bb", type=int, default=4)
    ap.add_argument("--seed", type=int, default=12345)
    a = ap.parse_args()
    d = json.load(open(a.problem))
    res = run(d["columns"], d["k"], d["N"], a.A, a.odd, a.bb, a.seed, tag=Path(a.problem).stem)
    res["file"] = a.problem
    print(json.dumps(res), flush=True)
