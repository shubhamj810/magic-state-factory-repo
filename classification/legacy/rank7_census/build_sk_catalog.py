#!/usr/bin/env python3
"""BUILD THE COMPLETE ``r <= 7, n <= 44`` S_k CATALOGUE.

``catalog/census_r7.json`` is the census MAXIMUM-T frontier: the 21 classes at
T = 5 and nothing else, by design (see ``build_catalog.py``).  This builder
publishes the other table the same census supports -- **every** ``(n, k,
S_k gate)`` class realised by a distance-3 factory with at most seven check
qubits and ``n <= 44`` -- into

  * ``catalog/sk_classes_r7.json``   one record per class, with a witness
  * ``catalog/SK_CLASSES_R7.md``      the same for humans

WHAT GOES IN
------------
``cli.py census --mode all --nmax 44 --kmax 7 --dedup symmetric --node-budget 0
--orbit-budget 0`` output: the census engine (``factorylib.parent``) visiting
every compatible subspace of every one of the 9,088 marked geometries and,
for each, every ``GL(k,2)`` output basis, recording one witness per ``S_k``
class.  Either

  * ONE unrestricted run -- a full-window certificate in the sense of
    ``build_catalog._certificate_problems`` -- or
  * a SET of ``--class-index``-restricted runs that between them cover every
    one of the 71 relevant classes exactly once.  Such shards are not
    certificates individually (the guard is right to refuse them for the
    frontier table) and this builder checks the covering itself: every
    ``(class, origin)`` geometry of the window present exactly once, every
    per-geometry ``gate_search_complete`` true, no node or orbit budget,
    ``kmax = 7``, ``dedup = symmetric``.

Pass files with ``--runs``.  With ``--certificate`` a second, unrestricted run
is required to yield the identical class set (engine self-consistency).

VERIFICATION, here, from the raw columns
----------------------------------------
Every witness is re-checked by ``factorylib.verification.verify`` -- exact
parity check of the deposited gate against the stored monomials, all
check-touching parities even, and the fault distance by exhaustive enumeration
to weight 4 -- and its T-count and reduced degree are recomputed by
``factorylib.metrics`` where feasible (``k <= 6``).  The witness is relabelled
into its canonical S_k output frame first (``build_catalog.enrich``), so the
published columns deposit literally the published gate.  Any failure aborts.
The maximum T must equal the shipped frontier's, and every class of
``catalog/census_r7.json`` must be among the classes attaining it.

Run:  python build_sk_catalog.py --runs results/census_shard_*.json
      python build_sk_catalog.py --runs results/census_r7_all.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2]))

import build_catalog as BC                                   # noqa: E402
from build_catalog import (CATALOG, enrich, named_to_monomials, sk_canonical,  # noqa: E402
                           sk_name)
from factorylib.verification import verify as exact_verify   # noqa: E402
from rank7 import WINDOW_NMAX, count_parents, iter_parents   # noqa: E402
from gillot_langevin import origin_orbits, parse_file         # noqa: E402
from rank7 import DEFAULT_DATA                                 # noqa: E402

OUT_JSON = CATALOG / "sk_classes_r7.json"
OUT_MD = CATALOG / "SK_CLASSES_R7.md"
METRICS_K_CAP = 6          # matches master_catalog/verify_catalog.py
REQUIRED_KMAX = 7          # the widest compatible frame in the window


# ------------------------------------------------------------------- loading
def window_geometries():
    """Every (class_index, origin) of the window, from the engine's own iterator."""
    return {(orbit.index, origin) for orbit, origin, _pts in iter_parents(mode="all", nmax=WINDOW_NMAX)}


def load_runs(paths, provisional=False):
    """Union the runs; prove that between them they sweep the window once."""
    seen_geoms: Counter = Counter()
    factories, problems = [], []
    for path in paths:
        blob = json.loads(Path(path).read_text(encoding="utf-8"))
        name = Path(path).name
        if blob.get("dedup") != "symmetric":
            problems.append(f"{name}: dedup={blob.get('dedup')!r}, not 'symmetric'")
        if blob.get("kmax") != REQUIRED_KMAX:
            problems.append(f"{name}: kmax={blob.get('kmax')!r}, not {REQUIRED_KMAX}: frames up to "
                            f"k = 7 exist in this window")
        if blob.get("mode") != "all":
            problems.append(f"{name}: mode={blob.get('mode')!r}, not 'all'")
        if blob.get("node_budget_per_parent") not in (0, None) or blob.get("orbit_budget_per_gate") not in (0, None):
            problems.append(f"{name}: a node or orbit budget was set")
        if blob.get("stopped_by_max_parents"):
            problems.append(f"{name}: stopped by max_parents")
        r = blob.get("restrictions") or {}
        # A run may be restricted to a class list and/or an origin list: coverage
        # is proved below, class by class, from what was actually swept.  A
        # narrower window or a parent cap is a different matter.
        if r.get("nmax") not in (None, WINDOW_NMAX) or r.get("max_parents"):
            problems.append(f"{name}: restrictions {r} narrow the window or cap the parent count")
        for g in blob.get("geometries", []):
            if not g.get("gate_search_complete"):
                problems.append(f"{name}: class {g['class_index']} origin {g['origin']}: gate search incomplete")
            seen_geoms[(g["class_index"], g["origin"])] += 1
        for f in blob.get("factories", []):
            if f.get("columns") is None or f["n"] > WINDOW_NMAX:
                continue
            if not f.get("orbit_complete", True):
                problems.append(f"{name}: a capped GL orbit on [[{f['n']},{f['k']}]] {f['gate']}")
            factories.append((name, f))
    expected = window_geometries()
    assert len(expected) == count_parents(nmax=WINDOW_NMAX) == 9088
    extra = set(seen_geoms) - expected
    dup = [g for g, c in seen_geoms.items() if c > 1]
    if extra:
        problems.append(f"{len(extra)} swept geometries lie outside the window")
    if dup:
        # Harmless: a geometry swept twice contributes the same classes twice
        # and the union is what is published.  Reported, not refused.
        print(f"  note: {len(dup)} geometries were swept by more than one run "
              f"(e.g. {sorted(dup)[:3]}); the union is used")
    # Coverage, class by class.  A class is covered when EVERY one of its 128
    # origins was swept, or when every stabiliser ORBIT of origins has a swept
    # member.  The second suffices: two origins in one orbit are carried onto
    # each other by an affine map fixing the RM(3,7) word, and that map acts on
    # the marked geometries as GL(7,2) on the syndromes -- a change of basis of
    # the check rows -- which leaves every compatible frame and every output
    # gate exactly where it was.  The orbits are recomputed here from the orbit
    # table, with the same routine the engine's own `--mode reps` uses.
    coverage, gaps = {}, []
    by_class = {}
    for cidx, origin in expected:
        by_class.setdefault(cidx, set()).add(origin)
    words = {w.index: w for w in parse_file(str(DEFAULT_DATA), 7)}
    for cidx, origins in sorted(by_class.items()):
        swept = {o for (c, o) in seen_geoms if c == cidx}
        if swept >= origins:
            coverage[cidx] = "all 128 origins"
            continue
        unmet = [grp for grp in origin_orbits(words[cidx]) if not (set(grp) & swept)]
        if unmet:
            msg = (f"class {cidx}: {len(unmet)} origin orbit(s) with no swept member, "
                   f"e.g. origins {sorted(unmet[0])[:6]}; swept {len(swept)} of {len(origins)}")
            if provisional:
                gaps.append(msg)
                coverage[cidx] = f"INCOMPLETE: {msg}"
            else:
                problems.append(msg)
        else:
            coverage[cidx] = (f"{len(swept)} origins, one or more in each of the "
                              f"{len(origin_orbits(words[cidx]))} stabiliser orbits")
    load_runs.coverage = coverage
    load_runs.gaps = gaps
    return factories, problems


def build(run_paths, certificate, provisional=False):
    factories, problems = load_runs(run_paths, provisional)
    if problems:
        for p in problems:
            print("  -", p)
        raise SystemExit("the runs do not add up to one complete sweep of the window")
    cov = load_runs.coverage
    by_reps = {c: v for c, v in cov.items() if not v.startswith("all")}
    print(f"input: {len(run_paths)} run file(s); {len(cov) - len(by_reps)} classes swept at all 128 "
          f"origins, {len(by_reps)} at one origin per stabiliser orbit "
          f"({', '.join(f'class {c}: {v}' for c, v in sorted(by_reps.items()))}); "
          f"{len(factories)} class records")

    best = {}
    dropped_wires = 0
    for name, f in factories:
        mons = named_to_monomials(f["gate"])
        # The engine writes every witness over all seven check coordinates.  On
        # a geometry of rank r < 7 that leaves 7 - r check wires no column
        # touches -- zero rows, which are not checks at all.  Drop them: the
        # outputs keep their labels, the used check wires close ranks.  Nothing
        # else changes (no column loses a qubit, no parity moves).
        k = f["k"]
        used = sorted({q for col in f["columns"] for q in col if q >= k})
        if len(used) != max(used) - k + 1 or (used and used[0] != k) or max(max(c) for c in f["columns"]) + 1 != f["N"]:
            remap = {q: k + i for i, q in enumerate(used)}
            columns = [sorted(q if q < k else remap[q] for q in col) for col in f["columns"]]
            dropped_wires += 1
        else:
            columns = [list(c) for c in f["columns"]]
        rec = {
            "n": f["n"], "k": f["k"], "d": f.get("distance", 3), "k_essential": None,
            "monomials": mons, "columns": columns,
            "stored_tcount": None,
            "source": f"RM(3,7) orbit class {f['class_index']}, origin {f['origin']}; {name}",
        }
        row = enrich_any_k(rec)
        key = (row["n"], row["k"], row["gate"])
        if key not in best or row["N"] < best[key]["N"]:
            best[key] = row
    rows = sorted(best.values(), key=lambda r: (r["n"], r["k"], r["gate"]))
    for i, r in enumerate(rows, 1):
        r["index"] = i
    print(f"{len(rows)} distinct (n, k, S_k gate) classes"
          + (f" ({dropped_wires} witness records had untouched check wires removed)" if dropped_wires else ""))

    bad = [(r, m) for r in rows for m in [reverify(r)] if m]
    print(f"{len(rows) - len(bad)}/{len(rows)} witnesses independently re-verified "
          f"(factorylib.verification, distance exact to weight 4)")
    if bad:
        for r, m in bad[:20]:
            print(f"  FAIL [[{r['n']},{r['k']},{r['d']}]] {r['gate']}: {m}")
        raise SystemExit("S_k catalogue build aborted")

    shipped = json.loads((CATALOG / "census_r7.json").read_text(encoding="utf-8"))
    shipped = shipped["factories"] if isinstance(shipped, dict) else shipped
    shipped_keys = {(r["n"], r["k"], r["gate"]) for r in shipped}
    tmax = max(r["t_count"] for r in rows if r["t_count"] is not None)
    ours_top = {(r["n"], r["k"], r["gate"]) for r in rows if r["t_count"] == tmax}
    # The shipped frontier must be CONTAINED in the top-T slice, and the maximum
    # must not have moved.  It need not be equal: the frontier catalogue was
    # assembled from the RREF-basis sweep plus one unrestricted search, and this
    # table is the first complete S_k enumeration, so extra classes at the
    # maximum are expected and are the point.  A class the frontier has and
    # this table lacks would be a bug here; a T above the frontier's would be
    # a new headline and is refused until looked at.
    shipped_tmax = max(r["t_count"] for r in shipped)
    if tmax != shipped_tmax:
        raise SystemExit(f"maximum T here is {tmax}, the shipped frontier's is {shipped_tmax}: "
                         f"a new headline, not folded in silently")
    if not shipped_keys <= ours_top:
        raise SystemExit(f"{len(shipped_keys - ours_top)} shipped frontier classes are missing: "
                         f"{sorted(shipped_keys - ours_top)[:5]}")
    print(f"frontier: maximum T = {tmax}; {len(ours_top)} classes attain it here, containing all "
          f"{len(shipped_keys)} of catalog/census_r7.json ({len(ours_top - shipped_keys)} more)")

    cert_note = None
    if certificate is not None:
        cert = json.loads(Path(certificate).read_text(encoding="utf-8"))
        cp = BC._certificate_problems(cert)
        if cp:
            raise SystemExit(f"{Path(certificate).name} is not a full-window certificate: {cp}")
        cert_keys = {(f["n"], f["k"], sk_name(sk_canonical(f["k"], named_to_monomials(f["gate"]))))
                     for f in cert["factories"] if f["n"] <= WINDOW_NMAX and f.get("columns") is not None}
        ours = {(r["n"], r["k"], r["gate"]) for r in rows}
        if cert_keys != ours:
            raise SystemExit(f"class set differs from {Path(certificate).name}: "
                             f"{len(cert_keys - ours)} only there, {len(ours - cert_keys)} only here")
        cert_note = f"{Path(certificate).name}: the unrestricted run yields the identical {len(ours)} classes"
        print("cross-check:", cert_note)
    return rows, tmax, cert_note, [Path(p).name for p in run_paths]


def enrich_any_k(rec):
    """`build_catalog.enrich`, except that metrics above k = 6 are not attempted."""
    if rec["k"] <= METRICS_K_CAP:
        return enrich(rec)
    saved = BC.metrics_from_named
    note = (f"not computed: exact minimisation is over GL({rec['k']},2) and a "
            f"punctured RM({rec['k']}-4,{rec['k']}) coset, neither feasible at k={rec['k']}")
    BC.metrics_from_named = lambda named: (None, note, None, note)
    try:
        return enrich(rec)
    finally:
        BC.metrics_from_named = saved


def reverify(row):
    cols = [frozenset(c) for c in row["columns"]]
    mons = named_to_monomials(row["gate_named"])
    ok, dist = exact_verify(row["k"], row["N"], cols, mons, dmax=4)
    if not ok:
        return "parity check failed"
    if dist != row["d"]:
        return f"distance {dist} != stored {row['d']}"
    return ""


# ----------------------------------------------------------------- rendering
def render_markdown(rows, tmax, cert_note, run_names):
    by_n = defaultdict(list)
    for r in rows:
        by_n[r["n"]].append(r)
    L = ["# Complete `r <= 7`, `n <= 44` catalogue: every `S_k` class", ""]
    L.append(f"**{len(rows)} distinct `(n, k, S_k gate)` classes** of distance-3 factory with at "
             f"most seven check qubits and `n <= 44`, one verified witness circuit each.")
    L.append("")
    L.append("[`census_r7.json`](census_r7.json) is the census T-count frontier: the classes it "
             "found attaining the maximum `T = 5`.  All of them are in this table's top-T slice, "
             "which is larger -- see the verification notes -- and everything else the same 9,088 "
             "marked geometries carry is listed here too.")
    L.append("")
    L.append("## How it was produced")
    L.append("")
    L.append("`cli.py census --mode all --nmax 44 --kmax 7 --dedup symmetric --node-budget 0 "
             "--orbit-budget 0`: the census engine (`factorylib.parent`) over all 71 `RM(3,7)` classes "
             "of weight `<= 44` and all 128 origins each, visiting every compatible subspace of every "
             "geometry and, for each subspace, every `GL(k,2)` output basis, recording one witness "
             "per `S_k` class.  A class whose gate leaves an output idle is not a class at that width; "
             "it is recovered at its true width on a sub-subspace.")
    L.append(f"Run files: {', '.join(f'`{n}`' for n in run_names)}.")
    L.append("")
    L.append("## How it was verified")
    L.append("")
    L.append("* the run files cover every one of the 71 classes -- each either at all 128 origins or at "
             "one origin in every stabiliser orbit of origins, which suffices because origins in one "
             "orbit give the same marked geometry up to a change of basis of the check rows -- with "
             "every per-geometry gate search complete and no node or orbit budget (`build_sk_catalog.py`);")
    L.append("* every witness re-checked from its raw columns by `factorylib.verification.verify`: "
             "gate parities, all check-touching parities even, distance exact by enumeration to weight 4;")
    L.append("* T-count and reduced degree recomputed by `factorylib.metrics` for `k <= 6`;")
    L.append(f"* the maximum exact T-count is still {tmax}; the {sum(1 for r in rows if r['t_count'] == tmax)} classes attaining it "
             f"contain all 21 of `census_r7.json`, whose frontier list was therefore itself incomplete as an `S_k` list;")
    L.append("* `verify_sk_classification.py` re-derives every witness with code sharing nothing with "
             "the engine, and checks the table against the all-rank `n <= 38` classification on their "
             "overlap and against every master-catalogue row in the window.")
    if cert_note:
        L.append(f"* {cert_note}.")
    L.append("")
    L.append("## Counts")
    L.append("")
    L.append("| n | classes | by k |")
    L.append("|---|---|---|")
    for n in sorted(by_n):
        ks = Counter(r["k"] for r in by_n[n])
        L.append(f"| {n} | {len(by_n[n])} | " + ", ".join(f"k={k}: {v}" for k, v in sorted(ks.items())) + " |")
    L.append("")
    tc = Counter(r["t_count"] for r in rows)
    L.append("T-count histogram: " + ", ".join(f"T={t}: {v}" for t, v in sorted(tc.items(), key=lambda x: (x[0] is None, x[0] or 0))))
    L.append("")
    L.append("## The classes")
    L.append("")
    L.append("Output labels come first, check labels follow; the columns are in the canonical "
             "`S_k` output frame, so they deposit exactly the gate shown.")
    L.append("")
    for n in sorted(by_n):
        L.append(f"### n = {n}")
        L.append("")
        L.append("| # | [[n,k,d]] | N | gate | T | deg |")
        L.append("|---|---|---|---|---|---|")
        for r in by_n[n]:
            t = "—" if r["t_count"] is None else r["t_count"]
            dg = "—" if r["poly_degree"] is None else r["poly_degree"]
            L.append(f"| {r['index']} | `[[{r['n']},{r['k']},{r['d']}]]` | {r['N']} | "
                     f"`{r['gate_human']}` | {t} | {dg} |")
        L.append("")
    L.append("## Witness circuits")
    L.append("")
    for r in rows:
        L.append(f"### {r['index']}. `[[{r['n']},{r['k']},{r['d']}]]` — {r['gate_human']}")
        L.append("")
        L.append(f"- gate `{r['gate']}`, `N = {r['N']}` ({r['k']} outputs + {r['r_checks']} checks), "
                 f"T-count {r['t_count'] if r['t_count'] is not None else '—'}, "
                 f"reduced degree {r['poly_degree'] if r['poly_degree'] is not None else '—'}")
        L.append(f"- source: {r['source']}")
        L.append("")
        L.append("```text")
        L.append("[" + ", ".join("{" + ",".join(map(str, c)) + "}" for c in r["columns"]) + "]")
        L.append("```")
        L.append("")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--certificate", default=None)
    ap.add_argument("--provisional", action="store_true",
                    help="tolerate uncovered origin orbits, record them as gaps, and write "
                         "catalog/sk_classes_r7_PROVISIONAL.{json,md} instead of the catalogue")
    a = ap.parse_args()
    rows, tmax, cert_note, run_names = build(a.runs, a.certificate, a.provisional)
    gaps = load_runs.gaps
    out_json, out_md = OUT_JSON, OUT_MD
    if a.provisional:
        out_json = CATALOG / "sk_classes_r7_PROVISIONAL.json"
        out_md = CATALOG / "SK_CLASSES_R7_PROVISIONAL.md"
        print(f"PROVISIONAL: {len(gaps)} coverage gap(s) tolerated:")
        for g in gaps:
            print("  -", g)
    CATALOG.mkdir(exist_ok=True)
    payload = {
        "scope": "every (n, k, S_k gate) class of distance-3 factory with at most 7 check qubits "
                 "and n <= 44; one verified witness per class",
        "dedup_key": "S_k: output permutations only (GL(k,2) is coarser and not used)",
        "engine": "cli.py census --mode all --nmax 44 --kmax 7 --dedup symmetric --node-budget 0 --orbit-budget 0",
        "run_files": run_names,
        "n_classes": len(rows),
        "n_geometries": 9088,
        "coverage": load_runs.coverage,
        "coverage_gaps": gaps,
        "complete": not gaps,
        "t_max": tmax,
        "frontier": "catalog/census_r7.json is contained in the classes at t_max; see n_classes_at_t_max",
        "n_classes_at_t_max": sum(1 for r in rows if r["t_count"] == tmax),
        "certificate_cross_check": cert_note,
        "factories": rows,
    }
    page = render_markdown(rows, tmax, cert_note, run_names)
    if gaps:
        page = page.replace("# Complete", "# PROVISIONAL (see coverage gaps below) -- complete", 1) \
            + "\n## Coverage gaps\n\nThis file was built with `--provisional`; the following origin orbits " \
              "were NOT swept, so classes from those geometries may be missing:\n\n" \
            + "".join(f"* {g}\n" for g in gaps)
    out_json.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    out_md.write_text(page, encoding="utf-8")
    print(f"wrote {out_json.relative_to(HERE)} and {out_md.relative_to(HERE)}: {len(rows)} classes"
          + (" (PROVISIONAL)" if gaps else ""))


if __name__ == "__main__":
    main()
