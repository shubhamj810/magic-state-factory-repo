#!/usr/bin/env python3
"""Independent verification of ``catalog/classification_n41_48.json`` (and the
combined ``classification_upto_n48.json``): correctness of every witness, and
completeness of the classification relative to its stated scope.

An adapted copy of ``../n40/verify40.py``.  Nothing here reuses the engine's
gate, frame or distance code.  The witnesses are re-derived by (1) a
self-contained enumerator below and (2) the master catalogue's own bar,
``verify_catalog.derive`` + ``measure_distance``, which shares no code with
the engine or with (1).

CORRECTNESS, per class witness (primary and at every rank)
  * shape: n == len(columns); N == max index + 1; columns distinct, non-empty;
    output rows independent modulo the check span; every output wire touched
    by the gate; check rows independent
  * gate: the odd degree-<=3 parities of the output rows, canonicalised under
    S_k by brute force over k!, equal the stored gate, in that canonical frame
  * factory condition: every degree-<=3 parity touching a check row is even
  * distance: the lightest accepted harmful fault, by exhaustive enumeration
    to weight 4, is exactly the stored d
  * a3 recounted by direct enumeration of every 3-set of columns
  * the master catalogue's bar (`verify_catalog.derive`, `measure_distance`)
    agrees on the primary witness; its S_k key equals the stored gate
  * the stored T-count agrees with an independent k = 3 computation at k = 3

COMPLETENESS (relative to the scope the catalogue states)
  * the four input tables validate (``reps48.validate``); the catalogue was
    built from the tables in this directory; every source it lists records
    exactly the geometry count recomputed from ``sources48`` and is complete;
    the build is not partial
  * the r <= 7 slice at n = 41 .. 44 equals the rank-7 census table's classes
    at those n, BOTH ways (that table swept every rank <= 7 parent of these
    lengths by a different route: RM(3,7) orbits at all 128 origins), and the
    per-(class, rank <= 7) minimum a3 at n = 43, 44 equals the n40 directory's
    census landscape entry for entry
  * every master-catalogue row at n = 41 .. 48 is a class here
  * the combined n <= 48 table is exactly the n <= 40 rows plus this table's

Run:  python verify48.py                  (~30 min: thousands of witnesses to weight 4)
      python verify48.py --allow-partial  (a partial build: correctness is checked in
                                           full; the declared coverage gaps are checked
                                           for consistency and reported as WARNINGS
                                           instead of failures, as are master rows that
                                           fall outside the swept part)
"""
import itertools
import json
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "master_catalog"))
import verify_catalog as VC            # noqa: E402  the catalogue's bar
VC.persist_metric_cache = lambda *a, **k: None
VC.recompute_metrics = lambda gate, k: (None, "skipped here", None, "skipped here")
import reps48                          # noqa: E402
from sources48 import SOURCES, expected_geometries, input_digest   # noqa: E402

CATALOG = HERE / "catalog" / "classification_n41_48.json"
ALL = HERE / "catalog" / "classification_upto_n48.json"
CENSUS = REPO / "classification" / "rank7_census" / "catalog" / "sk_classes_r7.json"
LAND_CENSUS = REPO / "classification" / "n40" / "catalog" / "landscape_census_r7.json"
UPTO40 = REPO / "classification" / "n40" / "catalog" / "classification_upto_n40.json"
MASTER = REPO / "master_catalog" / "master_catalog.json"
NS = tuple(range(41, 49))

fails = []
warnings = []


def fail(msg):
    fails.append(msg)
    print("FAIL:", msg)


def warn(msg):
    warnings.append(msg)
    print("WARNING:", msg)


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
    checks, outs = rows[k:N], rows[:k]
    for w in range(1, cap + 1):
        for X in itertools.combinations(range(n), w):
            mask = 0
            for j in X:
                mask |= 1 << j
            if any((c & mask).bit_count() & 1 for c in checks):
                continue
            if any((o & mask).bit_count() & 1 for o in outs):
                return w
    return None


def a3_direct(columns, k, N):
    """Independent recount: every 3-set of columns, syndrome by syndrome."""
    rows = rows_of(columns, N)
    n = len(columns)
    checks, outs = rows[k:N], rows[:k]
    count = 0
    for X in itertools.combinations(range(n), 3):
        mask = (1 << X[0]) | (1 << X[1]) | (1 << X[2])
        if any((c & mask).bit_count() & 1 for c in checks):
            continue
        if any((o & mask).bit_count() & 1 for o in outs):
            count += 1
    return count


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


def odd_check_parity(rows, k, N):
    for d in (1, 2, 3):
        for T in itertools.combinations(range(N), d):
            if max(T) >= k:
                acc = -1
                for t in T:
                    acc &= rows[t]
                if acc.bit_count() & 1:
                    return True
    return False


def key_from_columns(columns, k):
    N = max(max(c) for c in columns) + 1
    return frozenset(sk_min(odd_monomials(rows_of(columns, N), k, len(columns)), k))


def check_witness(tag, n, k, cols, stored, d, a3=None, primary=False):
    N = max(max(c) for c in cols) + 1
    if n != len(cols):
        fail(f"{tag}: n != len(columns)")
    if len({tuple(c) for c in cols}) != len(cols) or any(not c for c in cols):
        fail(f"{tag}: repeated or empty column")
    rows = rows_of(cols, N)
    if rank_f2(rows[k:]) != N - k:
        fail(f"{tag}: dependent check rows")
    if rank_f2(rows) != N:
        fail(f"{tag}: an output row lies in the span of the others + checks")
    if odd_check_parity(rows, k, N):
        fail(f"{tag}: odd parity on a check-touching degree-<=3 monomial")
    mons = odd_monomials(rows, k, n)
    if len({w for m in mons for w in m}) != k:
        fail(f"{tag}: spectator output wire")
    if frozenset(mons) != stored:
        fail(f"{tag}: columns deposit {gate_string(tuple(sorted(mons)))}, not the stored gate in its canonical frame")
    if primary and frozenset(sk_min(mons, k)) != stored:
        fail(f"{tag}: recomputed S_k canonical gate != stored")
    w = min_harmful_weight(cols, k, N, cap=4)
    if w != d:
        fail(f"{tag}: lightest accepted harmful fault has weight {w}, stored d={d}")
    if a3 is not None and a3_direct(cols, k, N) != a3:
        fail(f"{tag}: a3 recount {a3_direct(cols, k, N)} != stored {a3}")
    return mons, N


def main(argv=None):
    allow_partial = "--allow-partial" in (sys.argv[1:] if argv is None else argv)
    t0 = time.time()
    payload = json.loads(CATALOG.read_text(encoding="utf-8"))
    rows_cat = payload["factories"]
    print(f"{CATALOG.name}: {len(rows_cat)} classes; engine: {payload.get('engine')}")
    partial = bool(payload.get("partial"))
    if partial:
        (warn if allow_partial else fail)(
            "the catalogue is a PARTIAL build: not swept "
            f"{payload.get('sources_not_swept')}, with coverage gaps {payload.get('sources_with_coverage_gaps')}")
    soft = warn if (partial and allow_partial) else fail

    # --------------------------------------------------------------- correctness
    seen = set()
    d_hist = Counter()
    n_witnesses = 0
    for i, r in enumerate(rows_cat, 1):
        n, k, N, cols = r["n"], r["k"], r["N"], [list(c) for c in r["columns"]]
        tag = f"#{r['index']} [[{n},{k},{r['d']}]] {r['gate']}"
        if n not in NS:
            fail(f"{tag}: n outside this table's scope")
        if N != max(max(c) for c in cols) + 1:
            fail(f"{tag}: N != max index + 1")
        if N - k != r["r_checks"]:
            fail(f"{tag}: r_checks != N - k")
        stored = gate_set(r["gate"])
        if (n, k, stored) in seen:
            fail(f"{tag}: duplicate class")
        seen.add((n, k, stored))
        mons, _ = check_witness(tag, n, k, cols, stored, r["d"], r["a3"], primary=True)
        d_hist[r["d"]] += 1
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
        # the landscape
        if str(r["best_rank"]) not in r["landscape"] or r["landscape"][str(r["best_rank"])]["columns"] != r["columns"]:
            fail(f"{tag}: the primary columns are not the landscape's best-rank witness")
        if r["a3"] != min(w["a3"] for w in r["landscape"].values()):
            fail(f"{tag}: a3 is not the minimum over the landscape")
        if sorted(int(x) for x in r["landscape"]) != r["ranks"]:
            fail(f"{tag}: ranks do not match the landscape keys")
        if r["a3_at_fewest_checks"] != r["landscape"][str(min(r["ranks"]))]["a3"]:
            fail(f"{tag}: a3_at_fewest_checks is wrong")
        for rank, w in r["landscape"].items():
            n_witnesses += 1
            wc = [list(c) for c in w["columns"]]
            Nw = max(max(c) for c in wc) + 1
            if Nw != w["N"] or Nw - k != int(rank):
                fail(f"{tag} rank {rank}: N/rank mismatch")
            if int(rank) != r["best_rank"]:
                # the distance belongs to the witness: a3 = 0 iff d >= 4, and the
                # row's d is the primary (minimum-a3) witness's, the largest
                if (w.get("d", r["d"]) >= 4) != (w["a3"] == 0) or w.get("d", r["d"]) > r["d"]:
                    fail(f"{tag} rank {rank}: d = {w.get('d')} against a3 = {w['a3']} and the row's d = {r['d']}")
                check_witness(f"{tag} rank {rank}", n, k, wc, stored, w.get("d", r["d"]), w["a3"])
        if i % 200 == 0:
            print(f"  .. {i}/{len(rows_cat)} classes, {n_witnesses} witnesses, {time.time() - t0:.0f}s", flush=True)
    print(f"correctness: {len(rows_cat)} primary witnesses checked by two independent routes, "
          f"{n_witnesses} (class, rank) witnesses re-verified with a3 recounted; distance histogram {dict(d_hist)}; "
          f"{sum(1 for r in rows_cat if len(r['ranks']) > 1)} classes at more than one rank, "
          f"{sum(1 for r in rows_cat if r['a3'] < r['a3_at_fewest_checks'])} whose best circuit is not the fewest-check one")

    # --------------------------------------------------------------- completeness
    for L in reps48.LENGTHS:
        for p in reps48.validate(L):
            fail(f"input table {L}: {p}")
        if payload.get("inputs", {}).get(f"length{L}", {}).get("sha256") != reps48.sha256_of(L):
            fail(f"the catalogue was built from a different length-{L} table than the one in this directory")
    swept = payload.get("sources", {})
    n_gap_total = 0
    for s in SOURCES:
        if s == "open_rank6":
            continue
        sm = swept.get(s)
        if sm is None:
            soft(f"source {s} was not swept")
            continue
        exp = expected_geometries(s)
        if sm.get("input_sha256") != input_digest(s):
            fail(f"source {s}: built from a different input")
        cov = payload.get("coverage", {}).get(s, {})
        gaps = sm.get("coverage_gaps")
        if not gaps:
            if sm.get("n_geometries") != sum(exp.values()) or sm.get("n_representatives") != len(exp):
                fail(f"source {s}: catalogue records {sm.get('n_representatives')} representatives / "
                     f"{sm.get('n_geometries')} geometries, the inputs give {len(exp)} / {sum(exp.values())}")
            if sm.get("complete") is not True:
                fail(f"source {s}: not complete")
            short = [rid for rid, c in cov.items() if c.get("geometries") != exp.get(rid)]
            if set(cov) != set(exp) or short:
                fail(f"source {s}: coverage does not list every representative at every marking "
                     f"({len(set(exp) - set(cov))} missing, {len(short)} short)")
            continue
        # a source with declared coverage gaps: the declaration must account, geometry
        # by geometry, for everything the inputs expect that the coverage does not list
        soft(f"source {s}: {gaps.get('statement')}")
        if sm.get("complete") is not False:
            fail(f"source {s}: declares coverage gaps but complete={sm.get('complete')!r}")
        missing_reps = {rid for g in gaps.get("missing_shards", []) for rid in g["rep_ids"]}
        failed = Counter(f["rep_id"] for f in gaps.get("failed_geometries", []))
        if missing_reps & set(cov) or set(cov) | missing_reps != set(exp):
            fail(f"source {s}: the unswept shards and the coverage do not partition the representatives "
                 f"({len(set(exp) - set(cov) - missing_reps)} unaccounted, {len(missing_reps & set(cov))} both)")
        bad = [rid for rid, c in cov.items()
               if c.get("geometries") != exp.get(rid, -1) - failed.get(rid, 0) or c.get("failed", 0) != failed.get(rid, 0)]
        if bad:
            fail(f"source {s}: {len(bad)} representatives whose swept + failed geometries != the marking count "
                 f"({bad[:4]})")
        if any(f["rep_id"] in missing_reps for f in gaps.get("failed_geometries", [])):
            fail(f"source {s}: a failed geometry is listed inside an unswept shard")
        n_missing = sum(g["n_geometries"] for g in gaps.get("missing_shards", []))
        if n_missing != sum(exp[rid] for rid in missing_reps):
            fail(f"source {s}: the unswept shards' geometry count is misstated")
        n_gap = n_missing + sum(failed.values())
        if gaps.get("n_geometries_not_classified") != n_gap or sm.get("n_geometries") + n_gap != sum(exp.values()):
            fail(f"source {s}: classified {sm.get('n_geometries')} + not classified {n_gap} != {sum(exp.values())}")
        n_gap_total += n_gap
    print(f"coverage: {len(swept)} sources, {payload.get('n_geometries')} markings classified, "
          f"every representative at every marking the source lists"
          + (f"; {n_gap_total} markings declared NOT classified, the declaration accounts for every one"
             if n_gap_total else ""))

    ours = {(r["n"], r["k"], gate_set(r["gate"])) for r in rows_cat}

    # the rank-7 census: an independent sweep of every rank <= 7 parent at n <= 44
    census = json.loads(CENSUS.read_text(encoding="utf-8"))["factories"]
    theirs7 = {(r["n"], r["k"], key_from_columns(r["columns"], r["k"])) for r in census if 41 <= r["n"] <= 44}
    ours7 = {(r["n"], r["k"], gate_set(r["gate"])) for r in rows_cat if r["n"] <= 44 and min(r["ranks"]) <= 7}
    a = theirs7 - ours
    b = ours7 - theirs7
    if a:
        fail(f"{len(a)} census classes at n = 41 .. 44 are missing here: {sorted(a, key=str)[:6]}")
    if b:
        fail(f"{len(b)} classes here at n <= 44 with r <= 7 are missing from the census table: {sorted(b, key=str)[:6]}")
    print(f"rank-7 census overlap: {len(theirs7)} census classes at n = 41 .. 44; {len(ours7)} classes here with r <= 7"
          + (" -- identical" if not a and not b else ""))
    if LAND_CENSUS.exists():
        lc = json.loads(LAND_CENSUS.read_text(encoding="utf-8"))
        census_land = {(r["n"], r["k"], gate_set(r["gate"]), int(rk)): w["a3"]
                       for r in lc["factories"] for rk, w in r["landscape"].items() if 41 <= r["n"] <= 44}
        ours_land = {(r["n"], r["k"], gate_set(r["gate"]), int(rk)): w["a3"]
                     for r in rows_cat if r["n"] <= 44 for rk, w in r["landscape"].items() if int(rk) <= 7}
        if census_land != ours_land:
            only_c = {k2: v for k2, v in census_land.items() if ours_land.get(k2) != v}
            only_o = {k2: v for k2, v in ours_land.items() if census_land.get(k2) != v}
            fail(f"per-(class, rank <= 7) minimum a3 at n = 43, 44 differs from the n40 census landscape: "
                 f"{len(only_c)} census entries unmatched, {len(only_o)} entries here unmatched; "
                 f"e.g. {list(only_c.items())[:3]} vs {list(only_o.items())[:3]}")
        print(f"census landscape at n = 43, 44: {len(census_land)} (class, rank) minimum-a3 entries; "
              f"{len(ours_land)} here at r <= 7" + (" -- identical" if census_land == ours_land else ""))
    by_n_r = Counter((r["n"], r["r_checks"]) for r in rows_cat)
    print("classes by (n, best rank): " + ", ".join(f"n={n} r={rk}: {v}" for (n, rk), v in sorted(by_n_r.items())))

    # the master catalogue
    master = json.loads(MASTER.read_text(encoding="utf-8"))
    inside = [r for r in master["factories"] if r["n"] in NS]
    absent = [(r["n"], r["k"], r["N"] - r["k"], r["gate"]) for r in inside
              if (r["n"], r["k"], key_from_columns(r["columns"], r["k"])) not in ours]
    if absent:
        soft(f"{len(absent)} master-catalogue rows at n = 41 .. 48 are not classes here (n, k, r, gate): "
             f"{absent[:20]}")
    better = 0
    by_key = {(r["n"], r["k"], gate_set(r["gate"])): r for r in rows_cat}
    for r in inside:
        ours_r = by_key.get((r["n"], r["k"], frozenset(key_from_columns(r["columns"], r["k"]))))
        if ours_r is not None and ours_r["a3"] < a3_direct([list(c) for c in r["columns"]], r["k"], r["N"]):
            better += 1
    print(f"master catalogue: {len(inside) - len(absent)} of {len(inside)} rows at n = 41 .. 48 are classes here; "
          f"{better} of them carry a circuit with larger a3 than the best here")

    # the combined table
    if ALL.exists():
        allp = json.loads(ALL.read_text(encoding="utf-8"))
        old = json.loads(UPTO40.read_text(encoding="utf-8"))["factories"]
        keys_old = {(r["n"], r["k"], key_from_columns(r["columns"], r["k"])) for r in old}
        keys_all = Counter((r["n"], r["k"], key_from_columns(r["columns"], r["k"])) for r in allp["factories"])
        if any(v > 1 for v in keys_all.values()):
            fail("the combined table repeats a class")
        if set(keys_all) != keys_old | ours:
            fail(f"the combined table is not the n <= 40 rows plus this table's: "
                 f"{len(set(keys_all) - (keys_old | ours))} extra, {len((keys_old | ours) - set(keys_all))} missing")
        if allp.get("n_classes") != len(allp["factories"]) or len(allp["factories"]) != len(old) + len(rows_cat):
            fail("the combined table's counts do not add up")
        print(f"combined n <= 48 table: {len(allp['factories'])} classes = {len(old)} (n <= 40) + {len(rows_cat)} (n = 41 .. 48)")
    else:
        fail(f"{ALL.name} is missing")

    print(f"\nRESULT: {'PASS' if not fails else f'{len(fails)} FAILURES'}"
          + (f" with {len(warnings)} warning(s) (partial build)" if warnings else "")
          + f"  [{time.time() - t0:.0f}s]")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
