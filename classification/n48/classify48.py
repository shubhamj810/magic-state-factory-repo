#!/usr/bin/env python3
"""THE SWEEP -- every S_k class of distance-3 factory carried by a family of
check parents, with, per class and per check rank, the witness of minimum
leading error coefficient.  The n = 41 .. 48 counterpart of
``../n40/classify40.py``; the engine is the same (imported, unchanged), the
bookkeeping is rebuilt for 15.6 million geometries.

Sources (``sources48.py``): ``length42``, ``length44``, ``length46``,
``length48`` (m >= 8), ``rm37_w44`` and ``rm37_w48`` (the rank-7 sectors at
n = 43, 44 and n = 47, 48 plus their rank-8 lifts, from RM(3,7)).  ``open_rank6`` is listed there but refused here.

For each marked geometry: build the check parent and its quotient V_3(C) with
``factorylib.parent.Parent`` and run ``../n40/landscape.classify_landscape``:
every compatible subspace at every width (no cap by default), one witness per
S_k class, chosen to minimise the p^3 coefficient a3 among all subspaces of
the geometry that realise the class.  Nothing has a budget: a geometry either
finishes completely or is recorded as failed (with the exception), and the
run's summary and the catalogue builder both refuse an incomplete source.

WHAT IS KEPT (the n40 per-geometry records would be ~5 GB here):
  per representative
    * a histogram of its geometries over (n, ambient rank, check rank,
      kappa, mu, number of S_k classes) -- the whole coefficient-free
      landscape, geometry counts exactly recoverable;
    * ``factories``: its distinct (n, k, S_k class, check rank) entries, each
      with the minimum-a3 witness over all its geometries of that rank, the
      maximum a3 met, how many geometries and subspaces carry the class;
    * totals (subspaces visited, seconds, max kappa / mu) and ``complete``.
  Representatives are grouped into shards of ~50,000 geometries
  (``results/<source>/shard_NNNN.json.gz``), each written atomically once every
  geometry in it is done; a restarted run skips finished shards.

The workers mark the representatives themselves (``sources48.marking_of``),
one chunk of origins per job, so the parent process never holds a geometry.

Usage:
    classify48.py --source length42 --workers 2         # ~10 min
    classify48.py --source length48 --workers 2         # ~5 h
    classify48.py --source rm37_w44 --workers 2         # ~1 h
    classify48.py --source rm37_w48 --workers 2         # days
    classify48.py --source length44 --rep <id> --force  # one representative, re-run

Run it through ``run48.sh`` (nice, load check, log file) rather than directly.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import signal
import sys
import time
import traceback
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
for p in (HERE, HERE.parent / "n40", REPO):
    sys.path.insert(0, str(p))

import landscape                                                        # noqa: E402  (n40's, unchanged)
from landscape import Parent, classify_landscape                       # noqa: E402
from sources48 import SOURCES, input_digest, marking_of, reps_of        # noqa: E402


# ------------------------------------------- cross-parent orbit memo (speed only)
# ``classify_landscape`` memoises GL(k,2) gate orbits per parent, so a sweep of
# 15 million parents recomputes the same few hundred orbits 15 million times
# (half the profile at m = 8).  The orbit of a gate and its S_k class keys
# depend only on (k, gate), never on the parent, and the callers only read the
# returned dict -- so the two functions are wrapped in a process-level memo.
# Results are bit-for-bit those of the unwrapped classifier (tests/test_n48.py
# checks a sample both ways); ENGINE is unchanged for that reason.
_ORBIT_MEMO: dict = {}          # (k, gate) -> (orbit dict, complete)
_CLASSES_MEMO: dict = {}        # (k, id(orbit)) -> (orbit, classes)   (orbit held to pin its id)
# Memory, not entry count, is what bounds the memo: a member of a k = 6 orbit
# (a frozenset of monomial frozensets plus its basis-change matrix) costs
# several KB, so the 39,060-member orbits met at kappa = 7 weigh ~0.3 GB each.
# An entry-count cap (4096 orbits, the first version) let two workers grow to
# 18 GB and 16 GB on an 8 GB laptop -- see docs/INCIDENT_MEMORY_20260906.md.
_MEMO_MAX_ORBIT = 8_000         # orbits larger than this are never memoised
_MEMO_MEMBER_BUDGET = 60_000    # total memoised members before the memo is cleared
_memo_members = 0
# A single orbit walk is capped too: GL(7,2) orbits of a generic cubic gate run
# to 10^7+ members (hours and many GB), which no laptop sweep can hold.  A parent
# whose classification needs such a walk is recorded as a *failure* in its shard
# (error "OrbitTooLarge"), never silently skipped, so the builder sees it.
ORBIT_CAP = int(os.environ.get("N48_ORBIT_CAP", "150000"))
PARENT_SECONDS = int(os.environ.get("N48_PARENT_SECONDS", "1800"))   # wall-clock alarm per parent
_gl_orbit_raw = landscape.gl_orbit
_classes_raw = landscape._classes_of_orbit


class OrbitTooLarge(RuntimeError):
    """A GL(k,2) orbit walk exceeded ORBIT_CAP members."""


class ParentTimeout(RuntimeError):
    """A single parent's classification exceeded PARENT_SECONDS."""


def _walk(k, gate, limit=None):
    if limit is not None:
        return _gl_orbit_raw(k, gate, limit)
    orbit, complete = _gl_orbit_raw(k, gate, ORBIT_CAP)
    if not complete:
        raise OrbitTooLarge(f"k={k} orbit of a {len(gate)}-monomial gate exceeds {ORBIT_CAP} members")
    return orbit, True


def _gl_orbit_memo(k, gate, limit=None):
    global _memo_members
    if limit is not None:
        return _gl_orbit_raw(k, gate, limit)
    hit = _ORBIT_MEMO.get((k, gate))
    if hit is None:
        hit = _walk(k, gate)
        size = len(hit[0])
        if size <= _MEMO_MAX_ORBIT:
            if _memo_members + size > _MEMO_MEMBER_BUDGET:
                _ORBIT_MEMO.clear()
                _CLASSES_MEMO.clear()
                _memo_members = 0
            _ORBIT_MEMO[(k, gate)] = hit
            _memo_members += size
    return hit


def _classes_memo(k, orbit):
    hit = _CLASSES_MEMO.get((k, id(orbit)))
    if hit is None or hit[0] is not orbit:
        hit = (orbit, _classes_raw(k, orbit))
        if len(orbit) <= _MEMO_MAX_ORBIT:
            _CLASSES_MEMO[(k, id(orbit))] = hit
    return hit[1]


def enable_orbit_memo(on=True):
    """Switch the memo on (default in the workers) or off (for the identity test)."""
    landscape.gl_orbit = _gl_orbit_memo if on else _walk
    landscape._classes_of_orbit = _classes_memo if on else _classes_raw


enable_orbit_memo(True)

RESULTS = HERE / "results"
ENGINE = ("factorylib.parent (Parent.from_points at the parent's own ambient rank; "
          "compatible_subspaces uncapped) + orbit-memoised S_k classification with the "
          "minimum-a3 witness per class (n40/landscape.classify_landscape)")
SHARD_GEOMETRIES = 50_000      # target geometries per result shard
CHUNK_ORIGINS = 512            # origins per worker job (table sources)
HIST_KEY = ("n", "ambient_rank", "check_rank", "kappa", "mu", "n_gates")


# ------------------------------------------------------------------ worker
def _job(args):
    """Sweep one chunk of origins of one representative.  Returns the
    chunk's histogram, its (n, k, class, rank) entries with best witnesses,
    and the failures (never raises for a single bad geometry)."""
    rep_id, m, support, origins, kmax = args
    support = frozenset(support)

    def _alarm(*_):
        raise ParentTimeout(f"classification exceeded {PARENT_SECONDS}s")
    signal.signal(signal.SIGALRM, _alarm)
    hist = Counter()
    entries = {}
    failed = []
    subspaces = 0
    t_chunk = time.time()
    slowest = 0.0
    for origin in origins:
        n, ambient, points = marking_of(m, support, origin)
        t0 = time.time()
        signal.alarm(PARENT_SECONDS)
        try:
            parent = Parent.from_points(points, ambient_rank=ambient, distance=3)
            if parent.n != n:
                raise AssertionError(f"parent has {parent.n} columns, marking says {n}")
            out = classify_landscape(parent, kmax=kmax)
            if not out["complete"]:
                raise AssertionError("classify_landscape reported itself incomplete")
        except Exception as exc:                       # noqa: BLE001  recorded, reported, never hidden
            failed.append({"origin": origin, "n": n, "ambient_rank": ambient,
                           "error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()})
            continue
        finally:
            signal.alarm(0)
        dt = time.time() - t0
        slowest = max(slowest, dt)
        rank = parent.check_rank
        hist[(n, ambient, rank, parent.kappa, out["mu"], out["n_gates"])] += 1
        subspaces += out["subspaces_visited"]
        for g in out["gates"]:
            key = (n, g["k"], tuple(tuple(q) for q in g["canonical_key"]), rank)
            e = entries.get(key)
            if e is None:
                entries[key] = {
                    "n": n, "k": g["k"], "r": rank, "N": g["k"] + ambient, "distance": g["distance"],
                    "gate": g["gate"], "canonical_key": g["canonical_key"], "wants": g["wants"],
                    "a3": g["a3"], "a3_max": g["a3_max"], "n_subspaces": g["n_subspaces"],
                    "columns": g["columns"], "origin": origin, "ambient_rank": ambient,
                    "n_geometries_carrying": 1,
                }
            else:
                e["n_geometries_carrying"] += 1
                e["n_subspaces"] += g["n_subspaces"]
                e["a3_max"] = max(e["a3_max"], g["a3_max"])
                if g["a3"] < e["a3"]:
                    e.update(a3=g["a3"], columns=g["columns"], origin=origin, ambient_rank=ambient,
                             N=g["k"] + ambient, distance=g["distance"])
    return {
        "rep_id": rep_id, "n_origins": len(origins), "hist": list(hist.items()),
        "entries": list(entries.values()), "failed": failed, "subspaces": subspaces,
        "seconds": time.time() - t_chunk, "slowest": slowest,
    }


# ------------------------------------------------------------------ parent
def _merge(rec, part):
    rec["n_geometries"] += part["n_origins"] - len(part["failed"])
    rec["failed"] += part["failed"]
    rec["subspaces_visited"] += part["subspaces"]
    rec["seconds"] += part["seconds"]
    rec["slowest_geometry_seconds"] = max(rec["slowest_geometry_seconds"], part["slowest"])
    for key, count in part["hist"]:
        rec["_hist"][tuple(key)] += count
    for e in part["entries"]:
        key = (e["n"], e["k"], tuple(tuple(q) for q in e["canonical_key"]), e["r"])
        c = rec["_entries"].get(key)
        if c is None:
            rec["_entries"][key] = e
        else:
            c["n_geometries_carrying"] += e["n_geometries_carrying"]
            c["n_subspaces"] += e["n_subspaces"]
            c["a3_max"] = max(c["a3_max"], e["a3_max"])
            if e["a3"] < c["a3"]:
                c.update(a3=e["a3"], columns=e["columns"], origin=e["origin"], ambient_rank=e["ambient_rank"],
                         N=e["N"], distance=e["distance"])


def _new_record(rep):
    return {
        "rep_id": rep.id, "m": rep.m, "note": rep.note, "support": sorted(rep.support),
        "n_geometries_expected": rep.n_geometries, "n_geometries": 0, "failed": [],
        "subspaces_visited": 0, "seconds": 0.0, "slowest_geometry_seconds": 0.0,
        "_hist": Counter(), "_entries": {},
    }


def _finish(rec):
    hist = sorted(rec.pop("_hist").items())
    entries = sorted(rec.pop("_entries").values(), key=lambda e: (e["n"], e["k"], e["r"], e["canonical_key"]))
    for i, e in enumerate(entries):
        e["index"] = i
    rec["complete"] = rec["n_geometries"] == rec["n_geometries_expected"] and not rec["failed"]
    rec["max_kappa"] = max((k[3] for k, _ in hist), default=None)
    rec["max_mu"] = max((k[4] for k, _ in hist), default=None)
    rec["histogram_key"] = list(HIST_KEY)
    rec["histogram"] = [list(k) + [v] for k, v in hist]
    rec["n_entries"] = len(entries)
    rec["n_classes"] = len({(e["n"], e["k"], tuple(map(tuple, e["canonical_key"]))) for e in entries})
    rec["entries_by_n_k"] = {f"{n},{k}": v for (n, k), v in
                             sorted(Counter((e["n"], e["k"]) for e in entries).items())}
    rec["factories"] = entries
    rec["seconds"] = round(rec["seconds"], 2)
    rec["slowest_geometry_seconds"] = round(rec["slowest_geometry_seconds"], 2)
    return rec


def plan_shards(reps, target=SHARD_GEOMETRIES):
    """Consecutive groups of representatives of ~target geometries each (a
    representative bigger than the target is a shard of its own)."""
    shards, cur, cur_n = [], [], 0
    for rep in reps:
        if cur and cur_n + rep.n_geometries > target:
            shards.append(cur)
            cur, cur_n = [], 0
        cur.append(rep)
        cur_n += rep.n_geometries
    if cur:
        shards.append(cur)
    return shards


def jobs_of(rep, kmax, chunk):
    support = tuple(sorted(rep.support))
    return [(rep.id, rep.m, support, rep.origins[i:i + chunk], kmax)
            for i in range(0, len(rep.origins), chunk)]


def shard_path(out_dir, index):
    return out_dir / f"shard_{index:04d}.json.gz"


def read_shard(path):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def write_shard(path, blob):
    tmp = path.with_suffix(".tmp")
    with gzip.open(tmp, "wt", encoding="utf-8", compresslevel=6) as f:
        json.dump(blob, f, separators=(",", ":"))
        f.write("\n")
    os.replace(tmp, path)


def shard_is_done(path, digest, kmax, rep_ids):
    if not path.exists():
        return False
    try:
        blob = read_shard(path)
    except (OSError, ValueError):
        return False
    return (blob.get("complete") and blob.get("input_sha256") == digest and blob.get("kmax") == kmax
            and blob.get("engine") == ENGINE and blob.get("rep_ids") == rep_ids)


def sweep_shard(shard, pool, kmax, chunk, digest, source, index, n_shards):
    t0 = time.time()
    records = {rep.id: _new_record(rep) for rep in shard}
    jobs = [j for rep in shard for j in jobs_of(rep, kmax, chunk)]
    total = sum(rep.n_geometries for rep in shard)
    done, last = 0, t0
    for part in pool.imap_unordered(_job, jobs, chunksize=1):
        _merge(records[part["rep_id"]], part)
        done += part["n_origins"]
        if time.time() - last > 60:
            last = time.time()
            print(f"    shard {index}/{n_shards}: {done}/{total} geometries, {last - t0:.0f}s", flush=True)
    reps_out = [_finish(records[rep.id]) for rep in shard]
    return {
        "source": source, "input_sha256": digest, "engine": ENGINE, "dedup": "symmetric",
        "kmax": kmax, "distance": 3, "node_budget_per_parent": 0, "orbit_budget_per_gate": 0,
        "shard_index": index, "n_shards": n_shards, "shard_geometries_target": SHARD_GEOMETRIES,
        "rep_ids": [rep.id for rep in shard],
        "n_geometries_expected": total,
        "n_geometries": sum(r["n_geometries"] for r in reps_out),
        "n_failed": sum(len(r["failed"]) for r in reps_out),
        "complete": all(r["complete"] for r in reps_out),
        "seconds_wall": round(time.time() - t0, 1),
        "reps": reps_out,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--source", choices=[s for s in SOURCES if s != "open_rank6"], required=True)
    ap.add_argument("--rep", action="append", help="representative id (repeatable)")
    ap.add_argument("--m", action="append", type=int, help="intrinsic dimension (repeatable)")
    ap.add_argument("--kmax", type=int, default=None,
                    help="cap the frame width (default: none; the catalogue builder refuses a capped run)")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--force", action="store_true", help="re-run shards that have a complete result file")
    ap.add_argument("--output-dir", default=None, help="default results/<source>")
    ap.add_argument("--max-shards", type=int, default=None, help="stop after this many shards (for probing)")
    a = ap.parse_args(argv)

    import reps48
    if a.source in ("length42", "length44", "length46", "length48"):
        L = int(a.source[6:])
        problems = reps48.validate(L)
        if problems:
            for p in problems:
                print("PROBLEM:", p)
            raise SystemExit("the input table did not validate; nothing was run")
        if reps48.sha256_of(L) != reps48.EXPECTED_SHA256[L]:
            print(f"note: {reps48.FILES[L].name} does not have the digest this directory was built from")
    digest = input_digest(a.source)
    reps = reps_of(a.source)
    if a.rep:
        reps = [r for r in reps if r.id in set(a.rep)]
    if a.m:
        reps = [r for r in reps if r.m in set(a.m)]
    out_dir = Path(a.output_dir) if a.output_dir else RESULTS / a.source
    out_dir.mkdir(parents=True, exist_ok=True)
    chunk = 1 if a.source.startswith("rm37") else CHUNK_ORIGINS
    if a.rep or a.m:
        # a partial selection is written to its own shard files, never over the full plan's
        out_dir = out_dir / "partial"
        out_dir.mkdir(exist_ok=True)
    shards = plan_shards(reps)
    todo = [(i, s) for i, s in enumerate(shards, 1)
            if a.force or not shard_is_done(shard_path(out_dir, i), digest, a.kmax, [r.id for r in s])]
    if a.max_shards is not None:
        todo = todo[:a.max_shards]
    n_geo = sum(r.n_geometries for _, s in todo for r in s)
    print(f"source {a.source}: {len(reps)} representative(s), {len(shards)} shards, {len(todo)} to run "
          f"({n_geo} geometries), {a.workers} workers, kmax={'none' if a.kmax is None else a.kmax}, "
          f"input sha256 {digest}", flush=True)
    t0 = time.time()
    done_geo, failed = 0, 0
    with Pool(a.workers, maxtasksperchild=32) as pool:
        for j, (i, shard) in enumerate(todo, 1):
            blob = sweep_shard(shard, pool, a.kmax, chunk, digest, a.source, i, len(shards))
            write_shard(shard_path(out_dir, i), blob)
            done_geo += blob["n_geometries_expected"]
            failed += blob["n_failed"]
            elapsed = time.time() - t0
            eta = elapsed / done_geo * (n_geo - done_geo) if done_geo else 0
            print(f"[{j}/{len(todo)}] shard {i}: {len(shard)} reps (m={shard[0].m}..{shard[-1].m}), "
                  f"{blob['n_geometries_expected']} geometries, "
                  f"{sum(r['n_entries'] for r in blob['reps'])} entries, "
                  f"max kappa {max(r['max_kappa'] or 0 for r in blob['reps'])}, "
                  f"max mu {max(r['max_mu'] or 0 for r in blob['reps'])}, "
                  f"{blob['seconds_wall']}s"
                  + (f", FAILED {blob['n_failed']}" if blob["n_failed"] else "")
                  + f"  | {elapsed / 60:.1f} min elapsed, ~{eta / 60:.0f} min left", flush=True)
    print(f"done: {len(todo)} shard(s), {done_geo} geometries in {time.time() - t0:.0f}s"
          + (f"; {failed} FAILED geometries -- the source is incomplete" if failed else ""), flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
