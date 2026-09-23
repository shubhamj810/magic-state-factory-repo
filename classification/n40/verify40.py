#!/usr/bin/env python3
"""Independent verification of ``catalog/classification_n3940.json`` (and the
combined ``classification_upto_n40.json``): correctness of every witness, and
completeness of the classification.

An adapted copy of ``../rank7_census/verify_sk_classification.py``.  Nothing
here reuses the engine's gate, frame or distance code.  The witnesses are
re-derived by (1) a self-contained enumerator below and (2) the master
catalogue's own bar, ``verify_catalog.derive`` + ``measure_distance``, which
shares no code with the engine or with (1).

CORRECTNESS, per class witness
  * shape: n == len(columns); N == max index + 1; columns distinct, non-empty;
    output rows independent modulo the check span (no pseudo output); every
    output wire touched by the gate (no spectator); check rows independent
    (no dead check wire)
  * gate: the odd degree-<=3 parities of the output rows, canonicalised under
    S_k by brute force over k!, equal the stored gate, and the columns are in
    that canonical frame
  * factory condition: every degree-<=3 parity touching a check row is even
  * distance: the lightest accepted harmful fault, by exhaustive enumeration
    to weight 4, is exactly the stored d
  * the master catalogue's bar (`verify_catalog.derive`, `measure_distance`)
    agrees; its S_k key equals the stored gate
  * the stored T-count agrees with an independent k = 3 computation at k = 3

COMPLETENESS
  * the input table validates (``reps40.validate``) and the catalogue records
    a complete sweep of all 110 representatives and 44,974 markings
  * the r <= 7 slice equals the rank-7 census table's classes at n = 39, 40,
    BOTH ways (that table swept every rank <= 7 parent of these lengths by a
    different route: RM(3,7) orbits at all 128 origins)
  * every class of the earlier quotient-search catalogue of these lengths
    (``reference/catalog_n3940_legacy.json``, 170 classes through k = 5) is here
  * every master-catalogue row at n = 39, 40 is here
  * the combined n <= 40 table is exactly the 74 shipped n <= 38 rows plus
    this table's rows

Run:  python verify40.py
"""
import itertools
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "master_catalog"))
import verify_catalog as VC            # noqa: E402  the catalogue's bar (redirects its metric cache to a temp file)
VC.persist_metric_cache = lambda *a, **k: None
VC.recompute_metrics = lambda gate, k: (None, "skipped here", None, "skipped here")
from reps40 import EXPECTED_COUNT, validate, sha256_of      # noqa: E402

CATALOG = HERE / "catalog" / "classification_n3940.json"
ALL = HERE / "catalog" / "classification_upto_n40.json"
CENSUS = REPO / "classification" / "rank7_census" / "catalog" / "sk_classes_r7.json"
LEGACY = HERE / "reference" / "catalog_n3940_legacy.json"
N38 = REPO / "classification" / "exhaustive_n38" / "catalog" / "classification_n38.json"
MASTER = REPO / "master_catalog" / "master_catalog.json"
EXPECTED_GEOMETRIES = 44974        # sum over representatives of 2^m + 1

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


def functools_reduce(rows, T):
    acc = -1
    for t in T:
        acc &= rows[t]
    return acc


def key_from_columns(columns, k):
    N = max(max(c) for c in columns) + 1
    return frozenset(sk_min(odd_monomials(rows_of(columns, N), k, len(columns)), k))


# --------------------------------------------------------------- correctness
payload = json.loads(CATALOG.read_text(encoding="utf-8"))
rows_cat = payload["factories"]
print(f"{CATALOG.name}: {len(rows_cat)} classes; engine: {payload.get('engine')}")

seen = set()
d_hist = Counter()
for r in rows_cat:
    n, k, N, cols = r["n"], r["k"], r["N"], [list(c) for c in r["columns"]]
    tag = f"#{r['index']} [[{n},{k},{r['d']}]] {r['gate']}"
    if n not in (39, 40):
        fail(f"{tag}: n outside this table's scope")
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
probs = validate()
for p in probs:
    fail(f"input table: {p}")
if payload.get("input", {}).get("sha256") != sha256_of():
    fail("the catalogue was built from a different input table than the one in this directory")
if payload.get("n_representatives") != EXPECTED_COUNT:
    fail(f"the table records {payload.get('n_representatives')} representatives swept, not {EXPECTED_COUNT}")
if payload.get("n_geometries") != EXPECTED_GEOMETRIES:
    fail(f"the table records {payload.get('n_geometries')} geometries swept, not {EXPECTED_GEOMETRIES}")
if payload.get("complete") is not True:
    fail("the table does not record a complete sweep")
cov = payload.get("coverage", {})
short = [rid for rid, c in cov.items() if c.get("geometries") != c.get("expected")]
if short:
    fail(f"{len(short)} representatives were not swept at every marking: {short[:5]}")
print(f"coverage: {len(cov)} representatives, {payload.get('n_geometries')} markings, complete")

ours = {(r["n"], r["k"], gate_set(r["gate"])) for r in rows_cat}

# the rank-7 census: an independent sweep of every rank <= 7 parent at these lengths
census = json.loads(CENSUS.read_text(encoding="utf-8"))["factories"]
theirs7 = {(r["n"], r["k"], key_from_columns(r["columns"], r["k"])) for r in census if r["n"] in (39, 40)}
ours7 = {key for key, r in zip(((r["n"], r["k"], gate_set(r["gate"])) for r in rows_cat), rows_cat)
         if r["r_checks"] <= 7}
a = theirs7 - ours
b = ours7 - theirs7
if a:
    fail(f"{len(a)} census classes at n = 39, 40 are missing here: {sorted(a, key=str)[:6]}")
if b:
    fail(f"{len(b)} classes here with r <= 7 are missing from the census table: {sorted(b, key=str)[:6]}")
print(f"rank-7 census overlap: {len(theirs7)} census classes at n = 39, 40; {len(ours7)} classes here with r <= 7"
      + (" -- identical" if not a and not b else ""))
above7 = [r for r in rows_cat if r["r_checks"] > 7]
print(f"classes here with r >= 8: {len(above7)}"
      + (f" ({Counter((r['n'], r['k']) for r in above7)})" if above7 else ""))

# the earlier quotient-search catalogue of these lengths
legacy = json.loads(LEGACY.read_text(encoding="utf-8"))["factories"]
legacy_keys = {(r["n"], r["k"], key_from_columns(r["columns"], r["k"])) for r in legacy}
missing = legacy_keys - ours
if missing:
    fail(f"{len(missing)} classes of the earlier catalogue are missing here: {sorted(missing, key=str)[:6]}")
print(f"earlier quotient-search catalogue: all {len(legacy_keys)} classes are here"
      if not missing else f"earlier catalogue: {len(legacy_keys) - len(missing)} of {len(legacy_keys)} found")

# the master catalogue
master = json.loads(MASTER.read_text(encoding="utf-8"))
inside = [r for r in master["factories"] if r["n"] in (39, 40)]
absent = [(r["n"], r["k"], r["gate"], r["regimes"]) for r in inside
          if (r["n"], r["k"], key_from_columns(r["columns"], r["k"])) not in ours]
if absent:
    fail(f"{len(absent)} master-catalogue rows at n = 39, 40 are not classes here: {absent[:6]}")
print(f"master catalogue: all {len(inside)} rows at n = 39, 40 are classes here"
      if not absent else f"master catalogue: {len(inside) - len(absent)} of {len(inside)} rows found")

# --------------------------------------------------------- the landscape
def a3_direct(columns, k, N):
    """Independent recount: every 3-set of columns, syndrome by syndrome."""
    rows = rows_of(columns, N)
    n = len(columns)
    count = 0
    for X in itertools.combinations(range(n), 3):
        mask = (1 << X[0]) | (1 << X[1]) | (1 << X[2])
        if any(bin(rows[i] & mask).count("1") & 1 for i in range(k, N)):
            continue
        if any(bin(rows[i] & mask).count("1") & 1 for i in range(k)):
            count += 1
    return count


n_witnesses = 0
for r in rows_cat:
    n, k, stored = r["n"], r["k"], gate_set(r["gate"])
    tag = f"#{r['index']} [[{n},{k},{r['d']}]] {r['gate']}"
    if str(r["best_rank"]) not in r["landscape"] or r["landscape"][str(r["best_rank"])]["columns"] != r["columns"]:
        fail(f"{tag}: the primary columns are not the landscape's best-rank witness")
    if r["a3"] != min(w["a3"] for w in r["landscape"].values()):
        fail(f"{tag}: a3 is not the minimum over the landscape")
    if sorted(int(x) for x in r["landscape"]) != r["ranks"]:
        fail(f"{tag}: ranks do not match the landscape keys")
    if r["a3_at_fewest_checks"] != r["landscape"][str(min(r["ranks"]))]["a3"]:
        fail(f"{tag}: a3_at_fewest_checks is wrong")
    for rank, w in r["landscape"].items():
        cols = [list(c) for c in w["columns"]]
        N = max(max(c) for c in cols) + 1
        n_witnesses += 1
        if N != w["N"] or N - k != int(rank):
            fail(f"{tag} rank {rank}: N/rank mismatch")
        if len({tuple(c) for c in cols}) != len(cols):
            fail(f"{tag} rank {rank}: repeated column")
        rows = rows_of(cols, N)
        if rank_f2(rows[k:]) != N - k or rank_f2(rows) != N:
            fail(f"{tag} rank {rank}: dependent rows")
        if frozenset(odd_monomials(rows, k, n)) != stored:
            fail(f"{tag} rank {rank}: witness deposits a different gate")
        if any(bin(functools_reduce(rows, T)).count("1") & 1
               for d in (1, 2, 3) for T in itertools.combinations(range(N), d) if max(T) >= k):
            fail(f"{tag} rank {rank}: odd check-touching parity")
        if min_harmful_weight(cols, k, N, cap=4) != r["d"]:
            fail(f"{tag} rank {rank}: distance != {r['d']}")
        if a3_direct(cols, k, N) != w["a3"]:
            fail(f"{tag} rank {rank}: a3 recount {a3_direct(cols, k, N)} != stored {w['a3']}")
print(f"landscape: {n_witnesses} (class, rank) witnesses re-verified, a3 recounted by direct enumeration; "
      f"{sum(1 for r in rows_cat if len(r['ranks']) > 1)} classes at more than one rank, "
      f"{sum(1 for r in rows_cat if r['a3'] < r['a3_at_fewest_checks'])} whose best circuit is not the fewest-check one")

# the census parents, swept the same way: per (class, rank <= 7) the minimum a3 must agree exactly
LAND_CENSUS = HERE / "catalog" / "landscape_census_r7.json"
LAND_N38 = HERE / "catalog" / "landscape_n38.json"
if LAND_CENSUS.exists():
    lc = json.loads(LAND_CENSUS.read_text(encoding="utf-8"))
    census_land = {(r["n"], r["k"], gate_set(r["gate"]), int(rk)): w["a3"]
                   for r in lc["factories"] for rk, w in r["landscape"].items()}
    ours_land = {(r["n"], r["k"], gate_set(r["gate"]), int(rk)): w["a3"]
                 for r in rows_cat for rk, w in r["landscape"].items() if int(rk) <= 7}
    census_here = {key: v for key, v in census_land.items() if key[0] in (39, 40)}
    if census_here != ours_land:
        only_c = {k2: v for k2, v in census_here.items() if ours_land.get(k2) != v}
        only_o = {k2: v for k2, v in ours_land.items() if census_here.get(k2) != v}
        fail(f"per-(class, rank) minimum a3 at r <= 7 differs from the census parents': "
             f"{len(only_c)} census entries unmatched, {len(only_o)} entries here unmatched; "
             f"e.g. {list(only_c.items())[:3]} vs {list(only_o.items())[:3]}")
    print(f"census landscape at n = 39, 40: {len(census_here)} (class, rank) minimum-a3 entries; "
          f"{len(ours_land)} here at r <= 7" + (" -- identical" if census_here == ours_land else ""))
    if LAND_N38.exists():
        l38 = json.loads(LAND_N38.read_text(encoding="utf-8"))
        n38_land = {(r["n"], r["k"], gate_set(r["gate"]), int(rk)): w["a3"]
                    for r in l38["factories"] for rk, w in r["landscape"].items() if int(rk) <= 7}
        census_38 = {key: v for key, v in census_land.items() if key[0] <= 38}
        if n38_land != census_38:
            fail(f"n <= 38 landscape at r <= 7 differs from the census parents': "
                 f"{sum(1 for k2, v in census_38.items() if n38_land.get(k2) != v)} census entries unmatched, "
                 f"{sum(1 for k2, v in n38_land.items() if census_38.get(k2) != v)} n38 entries unmatched")
        print(f"census landscape at n <= 38: {len(census_38)} entries; n <= 38 landscape at r <= 7: "
              f"{len(n38_land)}" + (" -- identical" if n38_land == census_38 else ""))
else:
    print("census landscape not built; the per-rank a3 cross-check was skipped")

# how the master catalogue's circuits at these lengths compare
improvable = [(r["n"], r["k"], r["gate"], a3_direct([list(c) for c in r["columns"]], r["k"], r["N"]))
              for r in inside]
better = 0
by_key = {(r["n"], r["k"], gate_set(r["gate"])): r for r in rows_cat}
for r, (n, k, gate, a3m) in zip(inside, improvable):
    ours_r = by_key.get((n, k, frozenset(key_from_columns(r["columns"], k))))
    if ours_r is not None and ours_r["a3"] < a3m:
        better += 1
print(f"master catalogue: {better} of {len(inside)} rows at n = 39, 40 carry a circuit with larger a3 than the best here")

# the combined table
if ALL.exists():
    allp = json.loads(ALL.read_text(encoding="utf-8"))
    n38 = json.loads(N38.read_text(encoding="utf-8"))["factories"]
    keys38 = {(r["n"], r["k"], key_from_columns(r["columns"], r["k"])) for r in n38}
    keys_all = Counter((r["n"], r["k"], key_from_columns(r["columns"], r["k"])) for r in allp["factories"])
    if any(v > 1 for v in keys_all.values()):
        fail("the combined table repeats a class")
    if set(keys_all) != keys38 | ours:
        fail(f"the combined table is not the n <= 38 rows plus this table's: "
             f"{len(set(keys_all) - (keys38 | ours))} extra, {len((keys38 | ours) - set(keys_all))} missing")
    if allp.get("n_classes") != len(allp["factories"]) or len(allp["factories"]) != len(n38) + len(rows_cat):
        fail("the combined table's counts do not add up")
    print(f"combined n <= 40 table: {len(allp['factories'])} classes = {len(n38)} (n <= 38) + {len(rows_cat)} (n = 39, 40)")
else:
    fail(f"{ALL.name} is missing")

print("\nRESULT:", "PASS" if not fails else f"{len(fails)} FAILURES")
sys.exit(1 if fails else 0)
