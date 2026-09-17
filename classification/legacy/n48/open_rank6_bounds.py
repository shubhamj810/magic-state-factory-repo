#!/usr/bin/env python3
"""What the open sector looks like: the three parents of the affine-rank-6
weight-48 word (RM(3,7) class 3470, a+abc) that ``classify48.py`` does not
sweep -- their quotient dimension kappa, the frame-width upper bound the
compatibility forms give, and a sampled density of compatible pairs -- so
``docs/OPEN_RANK6.md`` can say exactly why brute force stops here.

Writes ``docs/open_rank6_bounds.json``.  Builds three parents with
kappa = 20 .. 21 (2^kappa quotient representatives each, ~1 GB); enumerates
nothing.

Run:  python open_rank6_bounds.py        (a few minutes, ~1 GB)
"""
from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
for p in (HERE, HERE.parent / "n40", REPO):
    sys.path.insert(0, str(p))

from factorylib.parent import Parent, apply_form, form_rank_bounds, nullspace   # noqa: E402
from sources48 import marking_of, reps_of                                       # noqa: E402

OUT = HERE / "docs" / "open_rank6_bounds.json"


def main():
    random.seed(0)
    rep = reps_of("open_rank6")[0]
    out = {"rep_id": rep.id, "note": rep.note, "m": rep.m, "support": sorted(rep.support), "geometries": []}
    for origin in rep.origins:
        n, ambient, points = marking_of(rep.m, rep.support, origin)
        t0 = time.time()
        parent = Parent.from_points(points, ambient_rank=ambient, distance=3, max_kappa=24)
        build = time.time() - t0
        b = form_rank_bounds(parent)
        K, forms = parent.kappa, parent.compatibility_forms

        def compat(u, v):
            return all(((apply_form(f, u) & v).bit_count() & 1) == 0 for f in forms)
        trials = 20000
        ok = sum(compat(random.randrange(1, 1 << K), random.randrange(1, 1 << K)) for _ in range(trials))
        dims = sorted({len(nullspace([apply_form(f, u) for f in forms], K))
                       for u in random.sample(range(1, 1 << K), 50)})
        g = {"n": n, "origin": origin, "check_rank": parent.check_rank, "kappa": K, "t3": len(parent.triples)
             if hasattr(parent, "triples") else None,
             "form_ranks": b.get("basis_form_ranks"), "max_combined_form_rank": b.get("max_combined_form_rank"),
             "mu_upper_bound": b.get("mu_upper_bound"),
             "compatible_pair_fraction_sampled": ok / trials, "safe_dims_sampled": dims,
             "width2_subspaces_estimate": round((1 << K) * ((1 << K) * ok / trials) / 6),
             "build_seconds": round(build, 1)}
        print(g, flush=True)
        out["geometries"].append(g)
        del parent
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("wrote", OUT.relative_to(HERE))


if __name__ == "__main__":
    main()
