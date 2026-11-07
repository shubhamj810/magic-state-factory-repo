#!/usr/bin/env python3
"""A distance proof for puncture sets of the parent W = weighted RM(weights 2^8 on y = bits 0..7, 1^3 on z = bits
8..10, cutoff 6), by the fibre decomposition of REPORT.md section 2.

Every word of W^perp is c(z, y) = sum_a z^a c_a(y) with c_0 in RM(6,8), c_a in RM(5,8) for 1 <= |a| <= 2 and
c_{z0z1z2} in RM(4,8).  In fibre form, h_z = c(z, .) is in RM(6,8) for every z, the h_z are congruent modulo
RM(5,8), and sum_z h_z is in RM(4,8).  The weight of the fault is w(c) = sum_z |h_z minus P_z|.  Three cases cover
every nonzero c:

  A  class g of the h_z modulo RM(5,8) nonzero: w >= sum_z delta_z(g), with delta_z(g) the least number of points
     outside P_z in a word of RM(6,8) of class g (linear algebra on psi(x) = (1, x, x_i x_j));
  B  g = 0 and some h_z outside RM(4,8): w >= sum over fibres of eps_z(kappa_z), kappa_z = h_z mod RM(4,8),
     sum_z kappa_z = 0, eps_z(kappa) the least |h minus P_z| over h in RM(5,8) of class kappa (from kernel lists of
     the RM(2,8) problem on P_z);
  C  every h_z in RM(4,8): w >= min_z d3(P_z), with d3 from kernel sweeps of the RM(3,8) problem on P_z.

The script proves w(c) >= D for every nonzero c, or reports the case that fails.  It also checks the fibre form
of W^perp on random words (orthogonality to all 324 parent rows).

    python3 fibproof.py PROBLEM.json D
"""
from __future__ import annotations

import itertools
import json
import random
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import monomial as MO  # noqa: E402
import sj_sweep as SW  # noqa: E402
import fam11 as F  # noqa: E402

PAIRS = [(i, j) for i in range(8) for j in range(i + 1, 8)]
TRIPLES = list(itertools.combinations(range(8), 3))


def bit(x, i):
    return (x >> i) & 1


def psi(x):
    """(1, x_0..x_7, x_i x_j) as a 37-bit integer: the RM(2,8) evaluation column at x."""
    v = 1
    for i in range(8):
        v |= bit(x, i) << (1 + i)
    for t, (i, j) in enumerate(PAIRS):
        v |= (bit(x, i) & bit(x, j)) << (9 + t)
    return v


def phi3(x):
    v = 0
    for t, (i, j, k) in enumerate(TRIPLES):
        v |= (bit(x, i) & bit(x, j) & bit(x, k)) << t
    return v


class Span:
    """echelon basis over F_2 with reduction"""
    def __init__(self, vecs=()):
        self.piv = {}
        for v in vecs:
            self.add(v)

    def reduce(self, v):
        while v:
            h = v.bit_length() - 1
            b = self.piv.get(h)
            if b is None:
                return v
            v ^= b
        return 0

    def add(self, v):
        v = self.reduce(v)
        if v:
            self.piv[v.bit_length() - 1] = v
            return True
        return False


def rm_delta(m, r):
    return [a for a in range(1 << m) if bin(a).count("1") <= r]


def eps_table(Pz, wmax, wmin_only=False):
    """class kappa (cubic moments of h, 56 bits) -> least |h minus Pz| over the nonzero words h of RM(5,8) with
    |h minus Pz| <= wmax and kappa != 0, from the kernel's harmful lists of the RM(2,8) problem punctured at Pz
    (every accepted set of weight < 8 is harmful there).  Also returns the least weight of any listed set."""
    f = MO.factory(8, rm_delta(8, 2), list(Pz))
    if f is None:
        return None, None
    k, N, cols, surv = f
    syn, out = SW.masks(cols, k)
    PH = [phi3(x) for x in range(256)]
    phP = [PH[x] for x in Pz]
    e, wfirst = {}, None
    def note(svs, o, w):
        nonlocal wfirst
        kap = 0
        for x in svs:
            kap ^= PH[x]
        i = 0
        while o:
            if o & 1:
                kap ^= phP[i]
            o >>= 1; i += 1
        if wfirst is None:
            wfirst = w
        if kap and (kap not in e or w < e[kap]):
            e[kap] = w
    for j, (sv, o) in enumerate(zip(syn, out)):
        if sv == 0 and o:
            note([surv[j]], o, 1)
    with tempfile.TemporaryDirectory(dir=SW.TMP) as tmp:
        p = Path(tmp) / "p.bin"
        SW.write_problem(p, syn, out, k)
        for w in range(2, wmax + 1):
            if wmin_only and wfirst is not None:
                break
            lst = Path(tmp) / f"l{w}.txt"
            rr = SW.run_bin(p, w, extra=["--list", str(lst)])
            assert rr["complete"] == 1
            with open(lst) as fh:
                for line in fh:
                    idx, hx = line.split(":")
                    words = hx.split()
                    o = 0
                    for i, wd in enumerate(words):
                        o |= int(wd, 16) << (64 * i)
                    note([surv[int(t)] for t in idx.split()], o, w)
            lst.unlink()
    return e, wfirst


def check_dual_form(trials=20, seed=1):
    rows = F.rows()
    rng = random.Random(seed)
    def rand_word(r):     # random element of RM(r,8) as a 256-bit set
        v = 0
        for a in rm_delta(8, r):
            if rng.random() < 0.5:
                v ^= sum(1 << y for y in range(256) if y & a == a)
        return v
    lev = {0: 6, 1: 5, 2: 5, 3: 4}
    for _ in range(trials):
        c = 0
        for a in range(8):
            ca = rand_word(lev[bin(a).count("1")])
            for z in range(8):
                if z & a == a:
                    c ^= ca << (256 * z)
        assert all(bin(r & c).count("1") % 2 == 0 for r in rows), "fibre form is not dual"
    return trials


def prove(P, D, log=lambda m: print(m, flush=True)):
    t0 = time.time()
    fib = {z: sorted(p & 255 for p in P if p >> 8 == z) for z in range(8)}
    sizes = {z: len(v) for z, v in fib.items()}
    out = {"D": D, "fibre_sizes": sizes, "dual_form_checked_on": check_dual_form()}
    # case C
    d3 = {}
    for z, Pz in fib.items():
        f = MO.factory(8, rm_delta(8, 3), Pz)
        assert f is not None, "fibre dependent for RM(3,8)"
        k, N, cols, surv = f
        floor, wit, per = MO.kernel_distance(cols, k, N, D - 1)
        d3[z] = floor
    out["C_d3"] = d3
    out["C_ok"] = all(v >= D for v in d3.values())
    log(json.dumps({"case": "C", "d3": d3, "ok": out["C_ok"], "seconds": round(time.time() - t0, 1)}))
    # case B: least listed weight per fibre first, then lists up to the weight a pair can still afford
    budget = D - 1
    wmins = {}
    for z, Pz in fib.items():
        e0, w0 = eps_table(Pz, budget, wmin_only=True)
        assert e0 is not None, "fibre dependent for RM(2,8)"
        wmins[z] = w0 if w0 is not None else 99
    emin0 = min(wmins.values())
    eps = {}
    for z, Pz in fib.items():
        e, _ = eps_table(Pz, max(1, budget - emin0))
        eps[z] = e
        log(json.dumps({"case": "B", "fibre": z, "entries": len(e), "seconds": round(time.time() - t0, 1)}))
    emin = min((min(e.values()) for e in eps.values() if e), default=99)
    out["B_entries"] = {z: len(e) for z, e in eps.items()}
    out["B_min_eps"] = emin
    emin = min(emin0, emin)
    bad = []
    zs = list(range(8))
    # pairs
    for z1, z2 in itertools.combinations(zs, 2):
        for kap, w1 in eps[z1].items():
            w2 = eps[z2].get(kap)
            if w2 is not None and w1 + w2 <= budget:
                bad.append(("pair", z1, z2, w1 + w2))
    # triples and more, while affordable
    if 3 * emin <= budget:
        small = {z: [(kap, w) for kap, w in eps[z].items() if w <= budget - 2 * emin] for z in zs}
        for z1, z2, z3 in itertools.combinations(zs, 3):
            for k1, w1 in small[z1]:
                for k2, w2 in small[z2]:
                    if w1 + w2 + emin > budget:
                        continue
                    w3 = eps[z3].get(k1 ^ k2)
                    if w3 is not None and w1 + w2 + w3 <= budget:
                        bad.append(("triple", z1, z2, z3, w1 + w2 + w3))
    if 4 * emin <= budget:
        bad.append(("four or more fibres not checked", emin))
    out["B_ok"] = not bad
    out["B_bad"] = bad[:10]
    log(json.dumps({"case": "B", "entries": out["B_entries"], "min_eps": emin, "ok": out["B_ok"], "bad": bad[:5],
                    "seconds": round(time.time() - t0, 1)}))
    # case A
    PSI = [psi(x) for x in range(256)]
    PH2 = [p >> 9 for p in PSI]
    L, Rsets, R2 = {}, {}, {}
    gens = set()
    for z, Pz in fib.items():
        S = Span(PSI[x] for x in Pz)
        L[z] = S
        Rsets[z] = {S.reduce(PSI[b]) for b in range(256) if b not in set(Pz)}
        # classes of RM(6,8) words inside P_z: g = sum_A phi2 over A with sum_A (1, x) = 0
        low = Span()
        comb = []          # (low part reduced, phi2 part) pairs to find the kernel of the low projection
        basis = []         # rows (lowvec, highvec)
        for x in Pz:
            lo, hi = PSI[x] & 0x1FF, PH2[x]
            # Gaussian elimination keeping track of the high part
            for (blo, bhi) in basis:
                if lo ^ blo < lo:
                    lo ^= blo
                    hi ^= bhi
            if lo:
                basis.append((lo, hi))
                basis.sort(key=lambda t: -t[0])
            else:
                comb.append(hi)
        gens_z = Span(comb)
        for v in gens_z.piv.values():
            gens.add((z, v))
        out.setdefault("A_dim_classes_inside", {})[z] = len(gens_z.piv)
    # every nonzero class g lying in some pi(V_z): enumerate those spans
    worst = None
    nchecked = 0
    for z0 in range(8):
        basis = [v for (z, v) in gens if z == z0]
        for mask in range(1, 1 << len(basis)):
            g = 0
            for i, v in enumerate(basis):
                if mask >> i & 1:
                    g ^= v
            nchecked += 1
            tot = 0
            pending = []
            for z in range(8):
                r = L[z].reduce(g << 9)
                if r == 0:
                    dz = 0
                elif r in Rsets[z]:
                    dz = 1
                else:
                    dz = 2          # lower bound; refined below if needed
                    pending.append((z, r))
                tot += dz
            if tot < D:
                # refine: delta >= 3 if r is not a sum of two outside images
                for z, r in pending:
                    if z not in R2:
                        R = list(Rsets[z])
                        R2[z] = {a ^ b for a, b in itertools.combinations(R, 2)} | set(R)
                    if r not in R2[z]:
                        tot += 1
            if worst is None or tot < worst[0]:
                worst = (tot, z0, g)
    out["A_classes_checked"] = nchecked
    out["A_min_bound"] = worst[0] if worst else None
    out["A_ok"] = worst is None or worst[0] >= D
    log(json.dumps({"case": "A", "classes": nchecked, "dims": out["A_dim_classes_inside"], "min_bound": out["A_min_bound"],
                    "ok": out["A_ok"], "seconds": round(time.time() - t0, 1)}))
    out["proved_floor_at_least_D"] = out["A_ok"] and out["B_ok"] and out["C_ok"]
    out["seconds"] = round(time.time() - t0, 1)
    return out


if __name__ == "__main__":
    prob = json.loads(Path(sys.argv[1]).read_text())
    D = int(sys.argv[2])
    P = prob["points"]
    b = F.build(P)
    import sanjose as SJ
    assert SJ.digest(b["columns"]) == prob["digest"] == SJ.digest(prob["columns"]), "columns are not W punctured at P"
    res = prove(P, D)
    res["digest"] = prob["digest"]
    print(json.dumps(res), flush=True)
    if len(sys.argv) > 3:
        with open(sys.argv[3], "a") as f:
            f.write(json.dumps(res) + "\n")
