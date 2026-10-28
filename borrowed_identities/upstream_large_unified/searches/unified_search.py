"""SAT-free unified distance-2 search: two-group, shared-check gluing, and CNOT relabeling of the output block.

At distance 2 every gate touching a check qubit is detected, so a factory is fixed by what it deposits on the
output block. Three closed-form or linear stages choose that deposit:
  1. two-group     -- full output symmetry S_k (closed form, Two_group.py)
  2. shared-check gluing  -- output blocks sharing one check register (2-adic linear solve, symfree_search.py)
  3. relabeling    -- extra output wires carrying XORs of existing ones (no solve)
Every circuit is built only from Z(pi/2^l) parity rotations and is re-verified by brute-force phase simulation.
"""
import os, sys, csv, json, time, argparse, urllib.parse
from itertools import combinations
from math import comb

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "classification"))
from Two_group import build_gate_set, find_valid_signs  # noqa: E402
from symfree_search import solve_binding, _partitions  # noqa: E402
from classify import phase_polynomial, genuine_monomials, essential_and_reduced  # noqa: E402
from tcount import tcount_rm, _remap, NotInGroup, snf_z8, _matvec_mod  # noqa: E402

GEN = {2: {1: "S", 2: "CZ"}, 3: {1: "T", 2: "CS", 3: "CCZ"}, 4: {1: r"\sqrt{T}", 2: "CT", 3: "CCS", 4: "CCCZ"}}


# ----------------------------------------------------------------- level-l cost
def inputs(c, L):
    """Z(pi/2^L) inputs a parity rotation of coefficient c consumes; rotations that are Clifford at level L are free."""
    base = 1 << max(L - 2, 1)
    r = c % base
    return min(r, base - r)


# ----------------------------------------------------------------- stage 1: two-group circuits as explicit gates
def two_group_gates(k, r, sigma):
    """Expand a two-group gate-type/sign assignment into explicit (support, coeff); outputs 0..k-1, checks k..k+r-1."""
    gates, outq, chk = [], range(k), range(k, k + r)
    for (wO, wS), s in sigma.items():
        if wS == 0:
            continue
        for A in combinations(outq, wO):
            for B in combinations(chk, wS):
                gates.append((frozenset(A) | frozenset(B), s))
    return gates


SIGN_FREE_MAX_L = 3


S_MAX = 7                                      # largest skip parameter s_total, s_O tried (--smax)


def stage_two_group(L, k_max, n_max, k_min=1, one_sign=False):
    """At l<=3 every gate carries +theta: a sign flip changes a rotation by Z(-2 theta), a Clifford there, so it is
    absorbed into the Clifford correction on the checks. At l>=4 Z(-2 theta) is non-Clifford and signs are enumerated."""
    for k in range(k_min, k_max + 1):
        for n in range(k + 1, n_max + 1):
            r = n - k
            for st in range(1, S_MAX + 1):
                for so in range(1, S_MAX + 1):
                    pairs, _, _ = build_gate_set(k, r, st, so)
                    if not pairs:
                        continue
                    if L <= SIGN_FREE_MAX_L:
                        sigmas = [{p: 1 for p in pairs}]
                    else:
                        sigmas = find_valid_signs(L, n, k, pairs)
                        if one_sign:
                            # signs only flip check-only rotations, which do not touch the outputs: every valid
                            # pattern gives the same output, n and N, so one representative suffices
                            sigmas = sigmas[:1]
                    for sigma in sigmas:
                        yield dict(stage="two-group", k=k, r=r, gates=two_group_gates(k, r, sigma),
                                   params=f"s_total={st},s_O={so}")


# ----------------------------------------------------------------- stage 2: shared-check gluing
def stage_gluing(L, k_max, r_max, k_min=1):
    for k in range(k_min, k_max + 1):
        for parts in _partitions(k, L):
            for r in range(1, r_max + 1):
                sol = solve_binding(parts, r, L)
                if sol is None:
                    continue
                yield dict(stage="gluing", k=k, r=r, gates=[(S, c % (1 << L)) for S, c in sol["gates"]],
                           params="blocks=" + "+".join(map(str, parts)))
                break


# ----------------------------------------------------------------- stage 3: CNOT relabeling of the output block
def relabel(f, masks):
    """Add output wires whose value is the XOR of existing output wires in each mask; checks shift down."""
    k, r, p = f["k"], f["r"], len(masks)
    gates = []
    for S, c in f["gates"]:
        core = {q for q in S if q < k}
        extra = {k + j for j, m in enumerate(masks) if sum(1 for i in core if m >> i & 1) % 2}
        chk = {q + p for q in S if q >= k}
        gates.append((frozenset(core | extra | chk), c))
    return dict(stage=f["stage"] + "+relabel", k=k + p, r=r, gates=gates, params=f["params"],
                parent=f, masks=list(masks))


def relabel_masks(ess_qubits, p):
    """p new output wires, each the XOR of a distinct >=2-subset of the essential qubits (single wires add nothing)."""
    pool = [sum(1 << q for q in T) for w in range(2, len(ess_qubits) + 1) for T in combinations(ess_qubits, w)]
    return pool[:p] if p <= len(pool) else None


# ----------------------------------------------------------------- verification and classification
def phases(gates, n, L):
    xs = np.arange(1 << n, dtype=np.int64)
    ph = np.zeros(1 << n, dtype=np.int64)
    for S, c in gates:
        m = sum(1 << q for q in S)
        par = np.zeros_like(xs)
        v = xs & m
        while v.any():
            par ^= v & 1
            v >>= 1
        ph = (ph + c * par) % (1 << L)
    return ph


def poly_from_table(tab, k, mod):
    a = list(tab)
    for i in range(k):
        bit = 1 << i
        for x in range(1 << k):
            if x & bit:
                a[x] = (a[x] - a[x ^ bit]) % mod
    return {frozenset(i for i in range(k) if x >> i & 1): a[x] for x in range(1, 1 << k) if a[x]}


def is_factory(f, L, brute_force=False):
    """Borrowed-identity condition in the paper's monomial form (App. S5): every Newton coefficient on a support T
    that touches a check, a_T = (-1)^{|T|+1} 2^{|T|-1} sum_{S >= T} c_S, must vanish modulo 2^{cliff_exp(|T|)}, so the
    checks return to |+> after a diagonal Clifford correction. Only |T| <= L matters: higher coefficients are
    multiples of 2^L. Exact, and polynomial in N (no 2^N phase table). brute_force=True instead evaluates the
    phase table on all 2^N basis states, as an independent cross-check."""
    k, r = f["k"], f["r"]
    n = k + r
    out = set(range(k))
    if brute_force:
        P = poly_from_table(list(phases(f["gates"], n, L)), n, 1 << L)
        return all(c % (1 << cliff_exp(len(T), L)) == 0 for T, c in P.items() if not T <= out)
    gates = [(frozenset(S), c) for S, c in f["gates"]]
    for t in range(1, min(L, n) + 1):
        m = 1 << cliff_exp(t, L)
        for T in combinations(range(n), t):
            Ts = frozenset(T)
            if Ts <= out:
                continue
            s_ = sum(c for S, c in gates if Ts <= S)
            if ((-1) ** (t + 1) * 2 ** (t - 1) * s_) % m:
                return False
    return True


def distance(f, L):
    k = f["k"]
    out = set(range(k))
    mg = [S for S, c in f["gates"] if inputs(c, L)]
    chk = [S - out for S in mg]
    if any(not c for c in chk):
        return 1
    lab = [S & out for S in mg]
    seen = {}
    for c, o in zip(chk, lab):
        if c in seen and seen[c] != o:
            return 2
        seen.setdefault(c, o)
    for w in (3, 4):
        if len(mg) > 40 and w == 4:
            return ">=4"
        if len(mg) > 400:                      # distance >= 3 established; deeper search too costly
            return ">=3"
        for E in combinations(range(len(mg)), w):
            cc, oo = frozenset(), frozenset()
            for g in E:
                cc ^= chk[g]
                oo ^= lab[g]
            if not cc and oo:
                return w
    return ">=5"


def fmt_poly(g, L, cap=6):
    """LaTeX product of generators; output qubits are labeled from 1, as in the manuscript tables."""
    terms = sorted(g, key=lambda S: (-len(S), sorted(S)))
    names = [f"\\mathrm{{{GEN[L].get(len(S), 'deg' + str(len(S)))}}}_{{{''.join(str(q + 1) for q in sorted(S))}}}" for S in terms]
    if len(names) > cap:
        return f"{len(names)}\\ \\text{{terms}}"
    return "".join(names) if names else "\\mathbb{1}"


def cliff_exp(s, L):
    """An s-body coefficient may be shifted by any multiple of 2^cliff_exp by a free diagonal Clifford."""
    return min(L, max(L - 3 + s, s))


def zcount_exact(P, k, L, cap=1 << 22):
    """Exact min Z(pi/2^L) count of P up to diagonal Clifford: solve M a = f over Z_{2^L} (M = parity matrix),
    then minimize the per-rotation cost of a mod 2^{L-2} over the kernel (Amy-Mosca generalized to any level)."""
    mod, n = 1 << L, (1 << k) - 1
    base = 1 << max(L - 2, 1)
    M = [[bin(x & y).count("1") & 1 for y in range(1, n + 1)] for x in range(1, n + 1)]
    f = [sum(c for T, c in P.items() if all(x >> q & 1 for q in T)) % mod for x in range(1, n + 1)]
    U, W, D = snf_z8(M, mod)
    cvec = _matvec_mod(U, f, mod)
    ap = [0] * n
    gens = []
    for i in range(n):
        d, ci = D[i] % mod, cvec[i] % mod
        if d == 0:
            if ci:
                return None
            gens.append([W[r][i] % base for r in range(n)])
            continue
        sols = [v for v in range(mod) if (d * v) % mod == ci]
        if not sols:
            return None
        ap[i] = sols[0]
        step = mod // (d & -d)
        if step < mod:
            gens.append([(W[r][i] * step) % base for r in range(n)])
    a0 = [x % base for x in _matvec_mod(W, ap, mod)]
    gens = [g for g in gens if any(g)]
    cost = [min(v, base - v) for v in range(base)]
    span = {tuple(a0)}
    for g in gens:
        grown = set(span)
        for v in span:
            w = list(v)
            for _ in range(base - 1):
                w = [(w[r] + g[r]) % base for r in range(n)]
                grown.add(tuple(w))
        span = grown
        if len(span) > cap:
            return None
    return min(sum(cost[x] for x in v) for v in span)


def zcount(P, k, L):
    """Exact min Z(pi/2^L) count to prepare the output unitarily (S-count at l=2, T-count at l=3, sqrt(T)-count at l=4)."""
    if not P:
        return 0
    qs = sorted({q for S in P for q in S})
    idx = {q: i for i, q in enumerate(qs)}
    Pc = {frozenset(idx[q] for q in S): c for S, c in P.items()}
    kk = len(qs)
    if L == 3 and kk <= 6:
        Pr, k3 = _remap(P)
        try:
            return tcount_rm(Pr, k3)
        except NotInGroup:
            return None
    if kk > 5:
        return None
    return zcount_exact(Pc, kk, L)


_FRAME_CACHE = {}


def reduce_frame(P, k, L):
    """Clifford-reduced (essential_dim, degree, poly, exact), cached by output state since many circuits share one."""
    key = (L, k, frozenset(P.items()))
    if key not in _FRAME_CACHE:
        _FRAME_CACHE[key] = essential_and_reduced(P, list(range(k)), L)
    return _FRAME_CACHE[key]


def classify_factory(f, L):
    k = f["k"]
    Gf = [S for S, _ in f["gates"]]
    cf = [c for _, c in f["gates"]]
    P = phase_polynomial(Gf, cf, set(range(k)), L)
    raw = genuine_monomials(P)
    if not P or not raw:
        return None
    ess, deg, red, exact = reduce_frame(P, k, L)
    if deg == 0:
        return None
    return dict(N=sum(inputs(c, L) for c in cf), n=k + f["r"], d=distance(f, L), degree=deg,
                essential_dim=ess, frame_exact=exact, raw=fmt_poly(raw, L), reduced=fmt_poly(red, L),
                red_poly=red, zcount=zcount(P, k, L))


# ----------------------------------------------------------------- Quirk link (any coefficient)
PHASE = {2: "Z^½", 3: "Z^¼", 4: "Z^⅛"}
_ZPOW = {1: "Z", 2: "Z^½", 4: "Z^¼", 8: "Z^⅛"}          # Z^(1/d) by denominator d
_GPHASE = {4: ("i", "-i"), 8: ("√i", "√-i")}           # global phase e^{+-2 pi i/d}, d = 4 or 8
_CUSTOM = []


def _global_phase_gate(d, sign):
    """Quirk gate applying the global phase e^{sign 2 pi i / d}; under parity controls it is a parity rotation."""
    if d in _GPHASE:
        return _GPHASE[d][0 if sign > 0 else 1]
    gid = f"~ph{d}{'p' if sign > 0 else 'm'}"
    if gid not in [g["id"] for g in _CUSTOM]:
        import math
        c, s_ = math.cos(2 * math.pi / d), sign * math.sin(2 * math.pi / d)
        z = f"{c:.7f}{s_:+.7f}i"
        _CUSTOM.append({"id": gid, "name": f"e^({'+' if sign > 0 else '-'}2pi i/{d})", "matrix": "{{%s,0},{0,%s}}" % (z, z)})
    return gid


def _units(c, L):
    """Signed decomposition of c (mod 2^L) into powers of two, smallest number of terms."""
    mod = 1 << L
    c %= mod
    if c > mod // 2:
        c -= mod
    sign = 1 if c >= 0 else -1
    c = abs(c)
    return [(sign, 1 << b) for b in range(L) if c >> b & 1]


def quirk_url(gates, n, L, k=None):
    """Quirk circuit in the borrowed-identity form used throughout the paper.

    every qubit starts in |0> and gets H; each factory gate as ONE multi-qubit parity rotation (Quirk parity controls "zpar" on its
    support with a global-phase gate, so a Z(pi/2^L) rotation is a single column); when the outputs (first k qubits)
    are known, the Clifford corrections that return the checks to |+>, a row of Bloch spheres, then the inverse of
    the output decomposition (multi-controlled Z^t gates: T, CS, CCZ, ... at l=3) and a second row of Bloch spheres,
    then H on every qubit and Bloch spheres showing every qubit back in |0>."""
    global _CUSTOM
    _CUSTOM = []
    mod = 1 << L
    ph = n          # the global-phase gates sit on one extra wire
    cols = [["H"] * n]
    for S, c in gates:
        for sign, u in _units(c, L):
            col = [1] * (n + 1)
            for q in S:
                col[q] = "zpar"
            col[ph] = _global_phase_gate(mod // u, sign)
            cols.append(col)
    if k is not None:
        # phase polynomial on all n qubits from the Newton coefficients (no 2^n table): a_T for |T| <= L
        P = {}
        G = [(frozenset(S), c) for S, c in gates]
        for t in range(1, min(L, n) + 1):
            for T in combinations(range(n), t):
                Ts = frozenset(T)
                a = ((-1) ** (t + 1) * 2 ** (t - 1) * sum(c for S, c in G if Ts <= S)) % mod
                if a:
                    P[Ts] = a
        out = set(range(k))

        def mono(T, a):
            # e^{2 pi i a prod_{q in T} x_q / 2^L} as parity rotations only (one "zpar" column each), using
            # prod x = 2^{1-|T|} sum_{nonempty S in T} (-1)^{|S|+1} parity(S): angle (-1)^{|S|+1} a / (2^L 2^{|T|-1})
            T = sorted(T)
            LL = L + len(T) - 1
            for r in range(1, len(T) + 1):
                for S in combinations(T, r):
                    for sign, u in _units((-1) ** (r + 1) * a, LL):
                        col = [1] * (n + 1)
                        for q in S:
                            col[q] = "zpar"
                        col[ph] = _global_phase_gate((1 << LL) // u, sign)
                        cols.append(col)

        for T, a in sorted(P.items(), key=lambda t: (len(t[0]), sorted(t[0]))):
            if not T <= out:
                mono(T, -a)                       # Clifford correction on the checks
        cols.append(["Bloch"] * n)
        for T, a in sorted(P.items(), key=lambda t: (len(t[0]), sorted(t[0]))):
            if T <= out:
                mono(T, -a)                       # undo the output decomposition
        cols.append(["H"] * n)                    # every qubit returns to |0>
        cols.append(["Bloch"] * n)
    spec = {"cols": cols}
    if _CUSTOM:
        spec["gates"] = _CUSTOM
    return "https://algassert.com/quirk#circuit=" + urllib.parse.quote(json.dumps(spec, ensure_ascii=False), safe="")


# ----------------------------------------------------------------- the sweep
def run(L, k_max, n_max, r_max, relabel_max, log=print, timing=None, k_min=1):
    """All verified factories at level L. `timing`, if given, receives the wall-clock seconds of each stage:
    two-group, gluing, classification (output class, distance and z-count of every seed; optional bookkeeping, not
    needed to find a factory), padding (CNOT relabeling and its verification) and quirk (writing the links)."""
    T = dict(two_group=0.0, gluing=0.0, classification=0.0, padding=0.0, quirk=0.0)
    seeds, t0 = [], time.time()
    for f in stage_two_group(L, k_max, n_max, k_min):
        seeds.append(f)
    t1 = time.time()
    for f in stage_gluing(L, k_max, r_max, k_min):
        seeds.append(f)
    t2 = time.time()
    T["two_group"], T["gluing"] = t1 - t0, t2 - t1

    uniq, seen = [], set()
    for f in seeds:
        key = (f["k"], f["r"], frozenset(f["gates"]))
        if key not in seen:
            seen.add(key)
            uniq.append(f)
    seeds = uniq
    rows, best = [], {}
    stage_counts = {}
    for f in seeds:
        t = time.time()
        info = classify_factory(f, L)
        ok = info is not None and info["d"] != 1 and is_factory(f, L)
        T["classification"] += time.time() - t
        if not ok:
            continue
        stage_counts[f["stage"]] = stage_counts.get(f["stage"], 0) + 1
        row = dict(l=L, k=f["k"], stage=f["stage"], params=f["params"], parent_k=f["k"], checks=f["r"],
                   masks="", **info)
        t = time.time()
        row["quirk"] = quirk_url(f["gates"], info["n"], L, k=f["k"])
        T["quirk"] += time.time() - t
        rows.append(row)
        key = (f["k"], info["N"], info["reduced"])
        if key not in best or info["n"] < best[key]["n"]:
            best[key] = row
        if relabel_max and f["k"] <= k_max:
            t = time.time()
            ess_q = sorted({q for S in info["red_poly"] for q in S})
            if info["essential_dim"] < f["k"] or not info["frame_exact"]:
                T["padding"] += time.time() - t
                continue
            for p in range(1, relabel_max + 1):
                if f["k"] + p > k_max + relabel_max:
                    break
                masks = relabel_masks(ess_q, p)
                if masks is None:
                    break
                g = relabel(f, masks)
                cf = [c for _, c in g["gates"]]
                raw = genuine_monomials(phase_polynomial([S for S, _ in g["gates"]], cf, set(range(g["k"])), L))
                gi = dict(N=sum(inputs(c, L) for c in cf), n=g["k"] + g["r"], d=distance(g, L), raw=fmt_poly(raw, L))
                if gi["d"] == 1 or not is_factory(g, L):
                    log(f"relabel FAILED l={L} k={g['k']} from {f['params']}")
                    continue
                for key_ in ("degree", "essential_dim", "frame_exact", "reduced", "red_poly", "zcount"):
                    gi[key_] = info[key_]
                rr = dict(l=L, k=g["k"], stage=g["stage"], params=f["params"], parent_k=f["k"], checks=f["r"],
                          masks=";".join(bin(m)[2:] for m in masks), **gi)
                tq = time.time()
                rr["quirk"] = quirk_url(g["gates"], gi["n"], L, k=g["k"])
                T["quirk"] += time.time() - tq
                T["padding"] -= time.time() - tq
                rows.append(rr)
                stage_counts["relabel"] = stage_counts.get("relabel", 0) + 1
            T["padding"] += time.time() - t
    log(f"l={L}: " + ", ".join(f"{k} {v:.1f}s" for k, v in T.items()) + f"; {len(rows)} factories")
    log(f"l={L}: verified factories per stage: {stage_counts}")
    if timing is not None:
        timing.update(T)
    return rows


# ----------------------------------------------------------------- stage 4 (optional): SAT recovery
SAT_TARGETS = {
    3: [("CS01,CS02,CS03", 4, 6), ("CS01,CS02,CS03,CS04", 5, 7), ("CCZ012,CCZ013,CCZ045", 6, 7)],
}


def stage_sat(L, rows, targets, time_limit=30.0, log=print):
    """For each (target, k, n), ask SAT for a factory below the best N the SAT-free stages found for that
    output class. Finding is fast when one exists; a timeout only means none was found within the limit."""
    from sat_certify import certify as sat_find
    from coset_certify import parse_target
    added = []
    for spec, k, n in targets:
        tgt = parse_target(spec, L)
        P = {T: c for T, c in tgt.items() if c}
        _, _, red, _ = reduce_frame(P, k, L)
        red_key = fmt_poly(red, L)
        prior = [r["N"] for r in rows if r["l"] == L and r["k"] == k and r["reduced"] == red_key]
        cap = min(prior) if prior else 10 ** 6
        t = time.time()
        best = None
        while time.time() - t < time_limit:
            res, N, gates = sat_find(tgt, k, n, L, cap, max(1.0, time_limit - (time.time() - t)))
            if res != "sat":
                break
            best, cap = (N, gates), N
        log(f"l={L} SAT {spec} n={n}: {'none below cap' if best is None else f'N={best[0]}'} "
            f"(final cap {cap}, {time.time() - t:.1f}s)")
        if best is None:
            continue
        N, gates = best
        f = dict(stage="sat", k=k, r=n - k, gates=gates, params=f"target={spec}")
        info = classify_factory(f, L)
        if info is None or info["d"] == 1 or not is_factory(f, L):
            log(f"   SAT result failed verification for {spec}")
            continue
        row = dict(l=L, k=k, stage="sat", params=f["params"], parent_k=k, checks=n - k, masks="", **info)
        row["quirk"] = quirk_url(gates, info["n"], L, k=k)
        added.append(row)
    return added


def smallest_per_class(rows):
    """Smallest N, then smallest n, for each (l, k, reduced output)."""
    best = {}
    for r in rows:
        key = (r["l"], r["k"], r["reduced"])
        if key not in best or (r["N"], r["n"]) < (best[key]["N"], best[key]["n"]):
            best[key] = r
    return sorted(best.values(), key=lambda r: (r["l"], r["k"], r["N"]))


# ----------------------------------------------------------------- the two catalogues
# Paper convention in the CSVs: n = input magic states, N = circuit qubits (k outputs + checks); internally the
# rows carry the opposite names, so they are swapped on output.
STAGE_NAME = {"two-group": "two-group", "gluing": "gluing", "two-group+relabel": "padding",
              "gluing+relabel": "padding", "sat": "SAT"}
FIELDS = ["clifford_class", "l", "k", "n", "N", "d", "search_stage", "padded_from", "params", "reduced", "raw",
          "zcount", "essential_dim", "clifford_padded", "masks", "reference", "quirk"]
# literature references for the rows of the paper's Tables SII(a-c), keyed "l,k,n,N"; blank = none known to us
_REFS_PATH = os.path.join(ROOT, "outputs", "literature_refs.json")
REFS = json.load(open(_REFS_PATH)) if os.path.exists(_REFS_PATH) else {}


def catalogue_rows(rows):
    """Distinct factories, sorted so that each Clifford class (same l and Clifford-reduced output) is contiguous.
    search_stage is the stage that produced the circuit (two-group, gluing, padding, SAT); for padding,
    padded_from names the stage of the circuit it was relabeled from."""
    seen, out = set(), []
    for r in rows:
        key = (r["l"], r["k"], r["N"], r["n"], r["reduced"], r["stage"], r["params"], r.get("masks", ""))
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    first = {}
    for r in sorted(out, key=lambda r: (r["l"], r["k"], r["N"], r["n"])):
        first.setdefault((r["l"], r["reduced"]), len(first))
    label, count = {}, {}
    for (L, red), _ in sorted(first.items(), key=lambda t: t[1]):
        count[L] = count.get(L, 0) + 1
        label[(L, red)] = f"L{L}-{count[L]:03d}"
    out.sort(key=lambda r: (label[(r["l"], r["reduced"])], r["k"], r["N"], r["n"]))
    return [dict(clifford_class=label[(r["l"], r["reduced"])], l=r["l"], k=r["k"], n=r["N"], N=r["n"], d=r["d"],
                 search_stage=STAGE_NAME.get(r["stage"], r["stage"]),
                 padded_from=r["stage"].split("+")[0] if r["stage"].endswith("+relabel") else "",
                 params=r["params"], reduced=r["reduced"], raw=r["raw"], zcount=r["zcount"],
                 essential_dim=r["essential_dim"], clifford_padded="yes" if r["essential_dim"] < r["k"] else "no",
                 masks=r.get("masks", ""), reference=REFS.get(f'{r["l"]},{r["k"]},{r["N"]},{r["n"]}', ""),
                 quirk=r["quirk"]) for r in out]


def write_csv(path, rows, fields=FIELDS):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def write_all_factories(out_dir, rows):
    """all_factories.csv without the Quirk column (small enough to browse on GitHub), and the same table with Quirk
    links as all_factories_with_quirk.csv.zip (the links make the full table ~70 MB)."""
    import zipfile
    write_csv(os.path.join(out_dir, "all_factories.csv"), rows, [f for f in FIELDS if f != "quirk"])
    tmp = os.path.join(out_dir, "all_factories_with_quirk.csv")
    write_csv(tmp, rows)
    with zipfile.ZipFile(tmp + ".zip", "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.write(tmp, "all_factories_with_quirk.csv")
    os.remove(tmp)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Unified distance-2 factory search. Writes all_factories.csv (every "
                                             "distinct factory; its Quirk links are in all_factories_with_quirk.csv.zip) and "
                                             "smallest_per_class.csv (smallest per output class, with Quirk links), both with "
                                             "search stage, for whatever range is given.")
    ap.add_argument("--levels", type=int, nargs="+", default=[2, 3, 4])
    ap.add_argument("--kmin", type=int, default=1, help="smallest k (to split a large run across processes)")
    ap.add_argument("--kmax", type=int, default=6)
    ap.add_argument("--smax", type=int, default=7, help="largest skip parameter s_total, s_O in the two-group stage")
    ap.add_argument("--nmax", type=int, default=11, help="max circuit qubits in the two-group stage")
    ap.add_argument("--rmax", type=int, default=4, help="max check qubits in the gluing stage")
    ap.add_argument("--relabel", type=int, default=4, help="max extra output wires added by CNOT relabeling")
    ap.add_argument("--sat", action="store_true", help="add the SAT recovery stage for SAT_TARGETS (off by default)")
    ap.add_argument("--sat-time", type=float, default=30.0, help="per-target SAT time limit in seconds")
    ap.add_argument("--out-dir", default=os.path.join(ROOT, "outputs"), help="where the two CSVs are written")
    a = ap.parse_args()
    S_MAX = a.smax
    os.makedirs(a.out_dir, exist_ok=True)
    allrows, timings = [], {}
    for L in a.levels:
        timings[L] = {}
        rows = run(L, a.kmax, a.nmax, a.rmax, a.relabel, timing=timings[L], k_min=a.kmin)
        if a.sat and SAT_TARGETS.get(L):
            t = time.time()
            rows += stage_sat(L, rows, SAT_TARGETS[L], a.sat_time)
            timings[L]["sat"] = time.time() - t
        allrows += rows
    full = catalogue_rows(allrows)
    keep = {(r["l"], r["k"], r["reduced"]): None for r in []}
    for r in full:
        key = (r["l"], r["k"], r["reduced"])
        if key not in keep or keep[key] is None or (r["n"], r["N"]) < (keep[key]["n"], keep[key]["N"]):
            keep[key] = r
    small = sorted(keep.values(), key=lambda r: (r["l"], r["k"], r["n"]))
    write_all_factories(a.out_dir, full)
    write_csv(os.path.join(a.out_dir, "smallest_per_class.csv"), small)
    with open(os.path.join(a.out_dir, "search_timing.json"), "w") as fh:
        json.dump(dict(args=vars(a), seconds=timings), fh, indent=1)
    print(f"{len(full)} factories -> {a.out_dir}/all_factories.csv (+ _with_quirk.csv.zip); {len(small)} smallest per class -> "
          f"{a.out_dir}/smallest_per_class.csv; per-stage times -> {a.out_dir}/search_timing.json")
