#!/usr/bin/env python3
"""Case C of the fibre decomposition with own code: per fibre z, the sets F outside P_z with sum_F v = 0
(v = canonical psi3 residual, fibown.fibre_data) are exactly the faults of words h in RM(4,8) inside fibre z.
Sweeps every fibre exhaustively to weight W (sweep.c) and lists every zero set of weight W exactly, with
flips |h cap P_z|.

    python casec.py PROBLEM.json W
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
sys.path.insert(0, str(HERE))
import fibown as F  # noqa: E402

BIN = HERE.parent / "tmp" / "sweep"


def run_fibre(Pz, W, tag, seed=777):
    B, out, V = F.fibre_data(Pz)
    full = [(V[y][0] << 56) | V[y][1] for y in out]
    qm = [V[y][2] for y in out]
    rng = random.Random(seed)
    R = [rng.getrandbits(64) for _ in range(93)]
    proj = []
    for v in full:
        p = 0
        i = 0
        while v:
            if v & 1:
                p ^= R[i]
            v >>= 1
            i += 1
        proj.append(p)
    path = HERE.parent / "tmp" / f"cc_{tag}.bin"
    with open(path, "wb") as f:
        f.write(struct.pack("<I", len(proj)))
        f.write(struct.pack(f"<{len(proj)}Q", *proj))
    a = W // 2
    if W % 2:
        mode = ["odd", str(path), str(a)]
        fa = a + 1
    else:
        mode = ["dist", str(path), str(a), "1"]
        fa = a
    r = subprocess.run([str(BIN)] + mode, capture_output=True, text=True)
    lines = r.stdout.split("\n")
    summ = [l for l in lines if l.startswith("TOTAL") or l.startswith("TABLE")]
    vals = sorted({int(l.split()[1], 16) for l in lines if l.startswith("DUP") or l.startswith("HIT")})
    zero = {}
    if vals:
        sets = {}
        # find in chunks of target values
        for c0 in range(0, len(vals), 2000):
            chunk = vals[c0:c0 + 2000]
            rr = subprocess.run([str(BIN), "find", str(path), str(fa)] + [f"{v:x}" for v in chunk],
                                capture_output=True, text=True)
            for l in rr.stdout.split("\n"):
                if l.startswith("SET"):
                    v, idx = l[4:].split(":")
                    sets.setdefault(int(v, 16), []).append(tuple(int(t) for t in idx.split()))
        for v in vals:
            grp = sets.get(v, []) + ([()] if v == 0 else [])
            for s1, s2 in itertools.combinations(grp, 2):
                Fs = tuple(sorted(set(s1) ^ set(s2)))
                acc = 0
                q = 0
                for j in Fs:
                    acc ^= full[j]
                    q ^= qm[j]
                if Fs and acc == 0:
                    zero[Fs] = F.popc(q)
    path.unlink()
    byw = {}
    for Fs, fl in zero.items():
        e = byw.setdefault(len(Fs), [0, 0])
        e[0] += 1
        e[1] += fl
    return {"summary": summ, "collisions": len(vals), "zero_sets_by_weight": byw,
            "examples": [[[out[j] for j in Fs], fl] for Fs, fl in list(zero.items())[:3]]}


def main(path, W):
    t0 = time.time()
    d = json.load(open(path))
    P = d["points"]
    fib = {z: sorted(p & 255 for p in P if p >> 8 == z) for z in range(8)}
    res = {"file": path, "W": W, "fibres": {}}
    for z in range(8):
        res["fibres"][z] = run_fibre(fib[z], W, f"{Path(path).stem}_{z}")
        print(json.dumps({"z": z, **res["fibres"][z]}), flush=True)
    res["seconds"] = round(time.time() - t0, 1)
    print(json.dumps(res), flush=True)


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]))
