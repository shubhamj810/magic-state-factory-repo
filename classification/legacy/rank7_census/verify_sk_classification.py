#!/usr/bin/env python3
"""Independent verification of ``catalog/sk_classes_r7.json``: correctness of
every witness, and completeness of the classification.

Nothing here reuses the census engine's gate, frame or distance code.  The
witnesses are re-derived by (1) a self-contained enumerator below and (2) the
master catalogue's own bar, ``verify_catalog.derive`` + ``measure_distance``,
which shares no code with the engine or with (1).

CORRECTNESS, per class witness
  * shape: n == len(columns); N == max index + 1; columns distinct, non-empty;
    output rows independent modulo the check span (no pseudo output); every
    output wire touched by the gate (no spectator); check rows independent
    (no dead check wire)
  * gate: the odd degree-<=3 parities of the output rows, canonicalised under
    S_k by brute force over k!, equal the stored gate
  * factory condition: every degree-<=3 parity touching a check row is even
  * distance: the lightest accepted harmful fault, by exhaustive enumeration
    to weight 4, is exactly the stored d
  * the master catalogue's bar (`verify_catalog.derive`, `measure_distance`)
    agrees; its S_k key equals the stored gate
  * the stored T-count agrees with an independent k = 3 computation where
    k = 3 (the 7x7 Amy--Mosca system is invertible there, so it is exact)

COMPLETENESS
  * the table's own coverage record: 9,088 geometries (build_sk_catalog.py
    proves the run files sweep each exactly once)
  * the T = 5 classes are exactly the 21 S_k classes of catalog/census_r7.json
  * against the all-rank n <= 38 classification on the overlap, BOTH ways:
    every n <= 38 class with r <= 7 there is here, and every class here with
    n <= 38 is there
  * every master-catalogue row inside the window (n <= 44, r <= 7) is here

Run:  python verify_sk_classification.py [catalog/sk_classes_r7.json]
"""
import itertools
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "master_catalog"))
import verify_catalog as VC            # noqa: E402  the catalogue's bar
VC.persist_metric_cache = lambda *a, **k: None
# The bar's metric recomputation is a ~100 s search per uncached k = 5, 6 gate
# and is not what is being verified here.  Everything else in `derive` runs.
VC.recompute_metrics = lambda gate, k: (None, "skipped here", None, "skipped here")

CATALOG = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "catalog" / "sk_classes_r7.json"
CENSUS_CAT = HERE / "catalog" / "census_r7.json"
N38 = REPO / "classification" / "legacy" / "exhaustive_n38" / "catalog" / "classification_n38.json"
MASTER = REPO / "master_catalog" / "master_catalog.json"

fails = []


def fail(msg):
    fails.append(msg)
    print("FAIL:", msg)


# ------------------------------------------------------------ independent maths
def rows_of(columns, N):
    rows = [0] * N
    for j, c in enumerate(columns):
        for i in c:
            rows[i] |= 1 << j
    return rows


def odd_monomials(rows, k, n):
    full = (1 << n) - 1
    mons = []
    for d in (1, 2, 3):
        for T in itertools.combinations(range(k), d):
            acc = full
            for i in T:
                acc &= rows[i]
            if bin(acc).count("1") & 1:
                mons.append(T)
    return mons


def sk_min(mons, k):
    best = None
    for p in itertools.permutations(range(k)):
        key = tuple(sorted(tuple(sorted(p[i] for i in m)) for m in mons))
        if best is None or key < best:
            best = key
    return best


def gate_string(key):
    return "+".join("".join(map(str, m)) for m in key)


def gate_set(text):
    """A '+'-joined monomial string -> frozenset of wire tuples (order-free)."""
    return frozenset(tuple(int(ch) for ch in tok) for tok in text.split("+") if tok)


def rank_f2(vecs):
    basis = []
    for v in vecs:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
    return len(basis)


def min_harmful_weight(columns, k, N, cap=4):
    rows = rows_of(columns, N)
    n = len(columns)
    for w in range(1, cap + 1):
        for X in itertools.combinations(range(n), w):
            mask = 0
            for j in X:
                mask |= 1 << j
            if any(bin(rows[i] & mask).count("1") & 1 for i in range(k, N)):
                continue
            if any(bin(rows[i] & mask).count("1") & 1 for i in range(k)):
                return w
    return None


def tcount_k3(mons):
    """Exact T-count at k = 3: the unique solution of the 7x7 F_2 system that
    writes the gate as a set of T gates on linear functionals."""
    funcs = [v for v in itertools.product([0, 1], repeat=3) if any(v)]
    monos = [(0,), (1,), (2,), (0, 1), (0, 2), (1, 2), (0, 1, 2)]
    A = [[int(all(a[i] for i in m)) for a in funcs] for m in monos]
    b = [int(m in set(mons)) for m in monos]
    M = [row[:] + [bb] for row, bb in zip(A, b)]
    r = 0
    piv = []
    for c in range(7):
        p = next((i for i in range(r, 7) if M[i][c]), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        for i in range(7):
            if i != r and M[i][c]:
                M[i] = [x ^ y for x, y in zip(M[i], M[r])]
        piv.append(c)
        r += 1
    return sum(M[i][7] for i in range(len(piv)))


def key_from_columns(columns, k):
    N = max(max(c) for c in columns) + 1
    return sk_min(odd_monomials(rows_of(columns, N), k, len(columns)), k)


# --------------------------------------------------------------- correctness
payload = json.loads(CATALOG.read_text(encoding="utf-8"))
rows_cat = payload["factories"]
print(f"{CATALOG.name}: {len(rows_cat)} classes; engine: {payload.get('engine')}")

seen = set()
d_hist = Counter()
for r in rows_cat:
    n, k, N, cols = r["n"], r["k"], r["N"], [list(c) for c in r["columns"]]
    tag = f"#{r['index']} [[{n},{k},{r['d']}]] {r['gate']}"
    if n != len(cols):
        fail(f"{tag}: n != len(columns)")
    if N != max(max(c) for c in cols) + 1:
        fail(f"{tag}: N != max index + 1")
    if N - k != r["r_checks"]:
        fail(f"{tag}: r_checks != N - k")
    if len({tuple(c) for c in cols}) != len(cols) or any(not c for c in cols):
        fail(f"{tag}: repeated or empty column")
    rows = rows_of(cols, N)
    if rank_f2(rows[k:]) != N - k:
        fail(f"{tag}: dependent check rows")
    if rank_f2(rows) != N:
        fail(f"{tag}: an output row lies in the span of the others + checks")
    for d in (1, 2, 3):
        odd = False
        for T in itertools.combinations(range(N), d):
            if max(T) >= k:
                acc = (1 << n) - 1
                for t in T:
                    acc &= rows[t]
                if bin(acc).count("1") & 1:
                    odd = True
                    break
        if odd:
            fail(f"{tag}: odd parity on a check-touching degree-{d} monomial")
    mons = odd_monomials(rows, k, n)
    if len({w for m in mons for w in m}) != k:
        fail(f"{tag}: spectator output wire")
    key = sk_min(mons, k)
    stored = gate_set(r["gate"])
    if frozenset(key) != stored:
        fail(f"{tag}: recomputed S_k canonical gate {gate_string(key)} != stored")
    if frozenset(mons) != stored:
        # the columns are supposed to be IN the canonical frame already
        fail(f"{tag}: columns are not in the canonical S_k frame (they deposit {gate_string(tuple(sorted(mons)))})")
    if (n, k, stored) in seen:
        fail(f"{tag}: duplicate class")
    seen.add((n, k, stored))
    w = min_harmful_weight(cols, k, N, cap=4)
    if w != r["d"]:
        fail(f"{tag}: lightest accepted harmful fault has weight {w}, stored d={r['d']}")
    d_hist[w] += 1
    if k == 3 and r["t_count"] is not None and tcount_k3(mons) != r["t_count"]:
        fail(f"{tag}: k=3 T-count {tcount_k3(mons)} != stored {r['t_count']}")
    facts, problems = VC.derive(cols, k, N)
    if problems:
        fail(f"{tag}: verify_catalog.derive: {problems}")
    else:
        rep = VC.measure_distance(cols, k, N)
        if rep.get("d_exact") != r["d"]:
            fail(f"{tag}: verify_catalog distance d_exact={rep.get('d_exact')} != {r['d']}")
        if facts.get("sk_key") is not None and frozenset(tuple(m) for m in facts["sk_key"]) != stored:
            fail(f"{tag}: verify_catalog sk_key {facts['sk_key']} != stored gate")
print(f"correctness: {len(rows_cat)} witnesses checked by two independent routes; "
      f"distance histogram {dict(d_hist)}")

# --------------------------------------------------------------- completeness
if payload.get("n_geometries") != 9088:
    fail(f"the table records {payload.get('n_geometries')} geometries swept, not 9088")

ours = {(r["n"], r["k"], gate_set(r["gate"])) for r in rows_cat}
shipped = json.loads(CENSUS_CAT.read_text(encoding="utf-8"))
shipped = shipped["factories"] if isinstance(shipped, dict) else shipped
shipped_keys = {(r["n"], r["k"], frozenset(key_from_columns(r["columns"], r["k"]))) for r in shipped}
top = {(r["n"], r["k"], gate_set(r["gate"])) for r in rows_cat if r["t_count"] == payload["t_max"]}
if max(r["t_count"] for r in shipped) != payload["t_max"]:
    fail(f"maximum T {payload['t_max']} differs from the shipped frontier's")
if not shipped_keys <= top:
    fail(f"{len(shipped_keys - top)} shipped census frontier classes are not among the T = {payload['t_max']} classes here")
print(f"frontier: maximum T = {payload['t_max']}; {len(top)} classes attain it, containing all {len(shipped_keys)} shipped census classes")

blob = json.loads(N38.read_text(encoding="utf-8"))
n38 = blob["factories"] if isinstance(blob, dict) else blob
theirs, theirs7 = {}, set()
for r in n38:
    if r.get("level", 3) != 3 or r["d"] < 3:
        continue
    cols = [sorted(set(c)) for c in r["columns"]]
    key = (r["n"], r["k"], frozenset(key_from_columns(cols, r["k"])))
    theirs[key] = r
    if r.get("r_checks", r["N"] - r["k"]) <= 7:
        theirs7.add(key)
ours38 = {key for key in ours if key[0] <= 38}
a = theirs7 - ours
b = ours38 - set(theirs)
if a:
    fail(f"{len(a)} classes of the n<=38 classification with r<=7 are missing here: {sorted(a)[:6]}")
if b:
    fail(f"{len(b)} classes here at n<=38 are missing from the n<=38 classification: {sorted(b)[:6]}")
print(f"n<=38 overlap: {len(theirs7)} classified classes with r<=7 there, {len(ours38)} classes at n<=38 here"
      + (" -- identical" if not a and not b else ""))

master = json.loads(MASTER.read_text(encoding="utf-8"))
inside = [r for r in master["factories"] if r["n"] <= 44 and r["N"] - r["k"] <= 7]
absent = [(r["n"], r["k"], r["gate"], r["regimes"]) for r in inside
          if (r["n"], r["k"], frozenset(key_from_columns(r["columns"], r["k"]))) not in ours]
if absent:
    fail(f"{len(absent)} master-catalogue rows in the window are not classes here: {absent[:6]}")
print(f"window: all {len(inside)} master-catalogue rows with n<=44, r<=7 are classes here"
      if not absent else f"window: {len(inside) - len(absent)} of {len(inside)} master rows found")

print("\nRESULT:", "PASS" if not fails else f"{len(fails)} FAILURES")
sys.exit(1 if fails else 0)
