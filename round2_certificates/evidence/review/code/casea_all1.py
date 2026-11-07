#!/usr/bin/env python3
"""Case A words of weight exactly 8 with delta_z(g) = 1 in all eight fibres: the classes g (nonzero, 28-bit
quadratic part) with g in G1_z for every z, where G1_z = {g : (0, g) = psi2(b) + sum_A psi2(p), b outside P_z,
A subset of P_z}.  If the intersection is empty, no case-A word has weight 8 outside the classes lying in some
V_z (which fibown.py bounds separately).

    python casea_all1.py PROBLEM.json
"""
import json
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import fibown as F  # noqa: E402


def g1(Pz):
    B = F.Basis()
    for i, y in enumerate(Pz):
        B.add(F.psi2(y), 1 << i)
    # V_z: span of quadratic parts of kernel combinations
    basis = {}
    gens = []
    for y in Pz:
        lo, hi = F.psi2(y) & 0x1FF, F.psi2(y) >> 9
        for p in sorted(basis, reverse=True):
            if (lo >> p) & 1:
                blo, bhi = basis[p]
                lo ^= blo
                hi ^= bhi
        if lo:
            basis[lo.bit_length() - 1] = (lo, hi)
        else:
            gens.append(hi)
    V = {0}
    for g in gens:
        V |= {v ^ g for v in V}
    out = set()
    for b in range(256):
        if b in set(Pz):
            continue
        lo, hi = F.psi2(b) & 0x1FF, F.psi2(b) >> 9
        for p in sorted(basis, reverse=True):
            if (lo >> p) & 1:
                blo, bhi = basis[p]
                lo ^= blo
                hi ^= bhi
        if lo:
            continue
        out |= {hi ^ v for v in V}
    return out, len(V)


def main(path):
    d = json.load(open(path))
    P = d["points"]
    fib = {z: sorted(p & 255 for p in P if p >> 8 == z) for z in range(8)}
    inter = None
    sizes = {}
    for z in range(8):
        s, nv = g1(fib[z])
        sizes[z] = [len(s), nv]
        inter = s if inter is None else inter & s
    inter.discard(0)
    print(json.dumps({"file": path, "G1_sizes_and_Vz": sizes, "intersection_size": len(inter)}))


if __name__ == "__main__":
    main(sys.argv[1])
