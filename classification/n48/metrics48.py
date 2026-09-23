#!/usr/bin/env python3
"""Fill ``reduced_degree_cache.json`` for every class of the catalogue whose
CNOT-frame-reduced degree is still pending, then rebuild to pick it up.

The builder (``build_catalog48.py``) computes the exact T-count itself but
only *reads* the reduced degree from the cache, because the master
catalogue's bar for it -- ``factorylib.metrics.metrics_from_named``: the
exact minimum over GL(k,2) at k <= 5 (10^7 frames at k = 5, ~20 min for a
gate of degree >= 2) and a 2,000,000-frame bounded search at k = 6 (~7 min)
-- costs hours over the thousands of new k = 5, 6 classes at n = 47, 48.
This script does that work off the critical path, one gate at a time, each
result persisted as soon as it is known (``factorylib.metrics`` writes the
cache after every gate), so it can be stopped and restarted at will.

    nice -n 15 python metrics48.py [--workers 2] [--limit N] [--k 5]

Gates of degree 1 finish in milliseconds (the walk stops at the provable
floor); only degree >= 2 gates pay the full price.  Progress goes to stdout;
``run48.sh``-style logging: ``nohup nice -n 15 python -u metrics48.py > logs/metrics48_<ts>.log``.
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_catalog48 as B                       # noqa: E402  (redirects the cache path)
from factorylib import metrics as _metrics        # noqa: E402

CACHE = HERE / "reduced_degree_cache.json"


def pending_gates(k_only=None):
    """(gate_named, key, k) for every catalogue class without a cached degree."""
    payload = json.loads(B.OUT_JSON.read_text(encoding="utf-8"))
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    seen, out = set(), []
    for r in payload["factories"]:
        if r["k"] > B.METRICS_K_CAP or (k_only and r["k"] != k_only):
            continue
        key = B.degree_cache_key(r["gate_named"])
        if key is None or key in cache or key in seen:
            continue
        seen.add(key)
        out.append((r["gate_named"], key, r["k"]))
    return out


def _one(args):
    gate, key, k = args
    # each worker keeps its own memo; the parent merges and persists
    _metrics._DEG_CACHE = {}
    _metrics._CACHE_PATH = Path("/dev/null")
    t0 = time.time()
    deg, note = _metrics._degree_from_supports(
        [tuple(int(ch) for ch in tok if ch.isdigit()) for tok in gate.replace(".", " ").split()], 3)
    return gate, key, k, deg, note, time.time() - t0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--k", type=int, default=None, help="only classes with this k")
    a = ap.parse_args(argv)
    todo = pending_gates(a.k)
    if a.limit:
        todo = todo[:a.limit]
    print(f"{len(todo)} gates pending (k: {sorted({t[2] for t in todo})}); {a.workers} workers", flush=True)
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    t0, done = time.time(), 0
    with mp.Pool(a.workers, maxtasksperchild=8) as pool:
        for gate, key, k, deg, note, dt in pool.imap_unordered(_one, todo):
            cache[key] = {"deg": deg, "note": note}
            tmp = CACHE.with_suffix(".tmp")
            tmp.write_text(json.dumps(cache, indent=1), encoding="utf-8")
            tmp.replace(CACHE)
            done += 1
            print(f"[{done}/{len(todo)}] k={k} deg={deg} {dt:6.1f}s  {gate}  (elapsed {time.time() - t0:.0f}s)",
                  flush=True)
    print(f"done: {done} gates in {time.time() - t0:.0f}s; cache holds {len(cache)} entries; rebuild with "
          f"python build_catalog48.py [--partial]")


if __name__ == "__main__":
    main()
