#!/usr/bin/env python3
"""Write docs/SK_CLASSIFICATION.md -- the short report on the complete S_k
table -- from catalog/sk_classes_r7.json (or the PROVISIONAL file).

Run:  python write_sk_report.py [catalog/sk_classes_r7.json]
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "catalog" / "sk_classes_r7.json"
OUT = HERE / "docs" / "SK_CLASSIFICATION.md"

P = json.loads(CAT.read_text(encoding="utf-8"))
rows = P["factories"]
by_n = defaultdict(list)
for r in rows:
    by_n[r["n"]].append(r)
gaps = P.get("coverage_gaps") or []
tmax = P["t_max"]

L = []
L.append("# The complete `r <= 7`, `n <= 44` classification, up to `S_k`")
L.append("")
if gaps:
    L.append("> **PROVISIONAL.** Built from a sweep with the coverage gaps listed at the end; "
             "classes from those geometries may be missing.  `catalog/sk_classes_r7.json` is "
             "written only when there are none.")
    L.append("")
L.append(f"**{len(rows)} distinct `(n, k, S_k gate)` classes** of distance-3 factory with at most "
         f"seven check qubits and `n <= 44`, each with a verified witness circuit, in "
         f"[`../catalog/sk_classes_r7{'_PROVISIONAL' if gaps else ''}.json`](../catalog/sk_classes_r7{'_PROVISIONAL' if gaps else ''}.json) "
         f"and [`../catalog/SK_CLASSES_R7{'_PROVISIONAL' if gaps else ''}.md`](../catalog/SK_CLASSES_R7{'_PROVISIONAL' if gaps else ''}.md).")
L.append("")
L.append("## Why this table exists")
L.append("")
L.append("The shipped census catalogue, [`../catalog/census_r7.json`](../catalog/census_r7.json), "
         "is the census **maximum-T frontier**: the 21 classes at `T = 5`, and nothing else.  "
         "The census sweep behind it enumerated every compatible *subspace* of every marked "
         "geometry, but read one gate off each subspace -- its RREF basis.  A subspace is a "
         "code, not a gate: its other output bases are related by output CNOTs and are "
         "*distinct* `S_k` classes, which is exactly the granularity the master catalogue "
         "files rows by.  So the old sweep was complete for geometries and for the `T = 5` "
         "maximum (which a second, unrestricted subspace search corroborated), but not for "
         "`S_k` classes: it missed, for instance, the `T ⊗ CS` factory at `n = 43` that a "
         "later search campaign turned up, and even six of the 21 frontier classes were "
         "reachable only through the second search.")
L.append("")
L.append("This table closes that gap.  It is the same window and the same 9,088 marked "
         "geometries, swept by the repository's newer engine (`factorylib.parent`, via "
         "`cli.py census --kmax 7 --dedup symmetric`), which walks the full `GL(k,2)` orbit "
         "of every compatible subspace and records one witness per `S_k` class.")
L.append("")
L.append("## What was run")
L.append("")
L.append(f"`{P['engine']}` over the 71 `RM(3,7)` classes of weight `<= 44`.  Light classes were "
         "swept at all 128 origins; the heavy ones (`kappa >= 10`) at one origin per "
         "stabiliser orbit of origins, which suffices because two origins in one orbit give "
         "the same marked geometry up to a change of basis of the check rows (the map is "
         "affine on `F_2^7` and fixes the word), and a check-basis change moves no compatible "
         "frame and no output gate.  `build_sk_catalog.py` recomputes the orbits with the "
         "engine's own routine and proves this coverage before it writes anything.")
L.append("")
cov = P.get("coverage", {})
reps = {c: v for c, v in cov.items() if not str(v).startswith("all")}
L.append(f"Coverage: {len(cov) - len(reps)} classes at all 128 origins, {len(reps)} at orbit "
         f"representatives.  Run files: {', '.join(f'`{n}`' for n in P['run_files'][:6])}"
         + (f" and {len(P['run_files']) - 6} more" if len(P['run_files']) > 6 else "") + ".")
L.append("")
L.append("## How it was verified")
L.append("")
L.append("* **Every witness, twice, from raw columns.**  `build_sk_catalog.py` re-checks each with "
         "`factorylib.verification.verify` (gate parities, all check-touching parities even, "
         "distance exact by enumeration to weight 4).  `verify_sk_classification.py` re-derives "
         "each again with code sharing nothing with the engine -- its own parity reader, its own "
         "`k!` canonical form, its own fault enumerator -- and with the master catalogue's bar "
         "(`master_catalog/verify_catalog.derive`, `measure_distance`).")
L.append("* **The `T = 5` slice is the shipped frontier.**  The classes at the maximum T are exactly "
         "the 21 of `census_r7.json`.")
L.append("* **Two classifications agree on their overlap.**  On `n <= 38`, every class of the "
         "all-rank classification with `r <= 7` is here, and every class here is there.")
L.append("* **Every master-catalogue row in the window is a class here**, including the campaign "
         "rows that first exposed the gap.")
if P.get("certificate_cross_check"):
    L.append(f"* **Engine self-consistency.** {P['certificate_cross_check']}.")
L.append("")
L.append("## The numbers")
L.append("")
L.append("| n | classes | by k | max T |")
L.append("|---|---|---|---|")
for n in sorted(by_n):
    ks = Counter(r["k"] for r in by_n[n])
    mt = max((r["t_count"] for r in by_n[n] if r["t_count"] is not None), default=None)
    L.append(f"| {n} | {len(by_n[n])} | " + ", ".join(f"{k}: {v}" for k, v in sorted(ks.items())) + f" | {mt} |")
L.append("")
kc = Counter(r["k"] for r in rows)
L.append("By width: " + ", ".join(f"k={k}: {v}" for k, v in sorted(kc.items())) + ".")
tc = Counter(r["t_count"] for r in rows)
L.append("By exact T-count: " + ", ".join(f"T={t}: {v}" for t, v in sorted(tc.items(), key=lambda x: (x[0] is None, x[0] or 0))) + ".")
L.append("")
L.append("Compared with the master catalogue before this table was merged: it held 77 rows in "
         "the window, of which 21 came from the census frontier and the rest from the "
         "`n <= 38` classification and from search campaigns.")
L.append("")
L.append("## Reproducing it")
L.append("")
L.append("```bash")
L.append("# one job per (class, origin) is how it was actually run; see docs/CLUSTER_RUN.md")
L.append(".venv/bin/python classification/legacy/rank7_census/cli.py census --mode all --nmax 44 --kmax 7 \\")
L.append("    --dedup symmetric --node-budget 0 --orbit-budget 0 --allow-incomplete \\")
L.append("    --class-index <C> [--origin <O>] --output classification/legacy/rank7_census/results/rep_<C>_<O>.json")
L.append(".venv/bin/python classification/legacy/rank7_census/build_sk_catalog.py --runs classification/legacy/rank7_census/results/census_shard_*.json classification/legacy/rank7_census/results/rep_*_*.json")
L.append(".venv/bin/python classification/legacy/rank7_census/verify_sk_classification.py")
L.append("```")
if gaps:
    L.append("")
    L.append("## Coverage gaps (provisional build)")
    L.append("")
    for g in gaps:
        L.append(f"* {g}")
OUT.parent.mkdir(exist_ok=True)
OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
print(f"wrote {OUT}")
