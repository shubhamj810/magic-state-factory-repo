"""The unified search (two-group + shared-check gluing; no padding, no SAT) over a large range, one level and one k
per process, run in parallel. Each factory is verified algebraically (the monomial condition, no 2^N table) and its
output classified. Results stream to outputs/large_unified/l{L}_k{k}.csv, so finished slices survive an interruption.
Run: python3 searches/large_unified.py --levels 2 3 4 --kmax 12 --nmax 18 --smax 12 --jobs 15
"""
import argparse, csv, os, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
OUT = os.path.join(ROOT, "outputs", "large_unified")
APPROX_KMIN = 11                               # from this k on, the output class is an approximate upper bound
APPROX_FRAMES = 1                              # k >= APPROX_KMIN: no frame search, the class is the identity frame (approximate)
F = ["l", "k", "n", "N", "d", "search_stage", "params", "reduced", "raw", "zcount", "essential_dim", "frame_exact", "seconds"]


def slice_job(L, k, nmax, smax, rmax, glue_kmax=99):
    """One (level, k) slice. Resumable: candidates are processed in a fixed order and the index of the last one
    handled is saved in <slice>.progress, so after an interruption the slice continues where it stopped."""
    import unified_search as us
    us.S_MAX = smax
    if k >= APPROX_KMIN:                        # exact frame search costs ~1 h per factory at k >= 11
        import classify
        classify._GL_SAMPLE_CAP = APPROX_FRAMES
    path = os.path.join(OUT, f"l{L}_k{k}.csv"); prog = path + ".progress"
    if os.path.exists(path) and os.path.exists(path + ".done"):
        return L, k, sum(1 for _ in open(path)) - 1, 0.0, "cached"
    start = int(open(prog).read() or 0) if os.path.exists(prog) and os.path.exists(path) else 0
    if start:                                   # keep only rows of complete lines under a valid header
        lines = open(path).read().splitlines(keepends=True)
        if not lines or lines[0].rstrip("\r\n") != ",".join(F):
            lines = [",".join(F) + "\n"] + [x for x in lines if x.strip() and not x.startswith(F[0] + ",")]
        if lines and not lines[-1].endswith("\n"):
            lines = lines[:-1]                      # a row cut off mid-write
        open(path, "w").writelines(lines)
    t0 = time.time(); seen = set(); n = 0
    t_tg = time.time(); seeds = list(us.stage_two_group(L, k, nmax, k, one_sign=True)); t_tg = time.time() - t_tg
    t_gl = time.time()
    if k <= glue_kmax:
        seeds += list(us.stage_gluing(L, k, rmax, k))
    t_gl = time.time() - t_gl
    t_ver = t_cls = 0.0
    with open(path, "a" if start else "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=F)
        if not start:
            w.writeheader(); fh.flush()
        for i, f in enumerate(seeds):
            key = (f["k"], f["r"], frozenset(f["gates"]))
            if key in seen:
                continue
            seen.add(key)
            if i < start:                       # handled before the interruption
                continue
            tv = time.time(); ok = us.is_factory(f, L); t_ver += time.time() - tv
            if ok:
                t = time.time()
                info = us.classify_factory(f, L)
                t_cls += time.time() - t
                if info is not None and info["d"] != 1:
                    w.writerow(dict(l=L, k=k, n=info["N"], N=info["n"], d=info["d"], search_stage=f["stage"],
                                    params=f["params"], reduced=info["reduced"], raw=info["raw"], zcount=info["zcount"],
                                    essential_dim=info["essential_dim"], frame_exact=info["frame_exact"],
                                    seconds=round(time.time() - t, 2)))
                    fh.flush(); n += 1
            fh.flush()
            open(prog, "w").write(str(i + 1))          # written only after that candidate's row is on disk
    import json
    json.dump(dict(two_group=t_tg, gluing=t_gl, verification=t_ver, classification=t_cls, total=time.time() - t0,
                   resumed_at=start), open(path + ".done", "w"))
    return L, k, n, time.time() - t0, "done" if not start else f"resumed at {start}"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", type=int, nargs="+", default=[2, 3, 4])
    ap.add_argument("--kmax", type=int, default=12)
    ap.add_argument("--nmax", type=int, default=18)
    ap.add_argument("--smax", type=int, default=12)
    ap.add_argument("--rmax", type=int, default=4)
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument("--kmin", type=int, default=1)
    ap.add_argument("--nmax-l4", type=int, default=None, help="smaller circuit-size cap for l=4, whose sign enumeration makes it slowest")
    ap.add_argument("--glue-kmax", type=int, default=99, help="run shared-check gluing only for k <= this (its cost grows exponentially in k)")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    jobs = [(L, k) for L in a.levels for k in range(a.kmax, a.kmin - 1, -1)      # large k first: they take longest
            if not os.path.exists(os.path.join(OUT, f"l{L}_k{k}.csv.done"))]
    t0 = time.time()
    with ProcessPoolExecutor(a.jobs) as ex:
        futs = [ex.submit(slice_job, L, k, a.nmax_l4 if (L == 4 and a.nmax_l4) else a.nmax, a.smax, a.rmax, a.glue_kmax)
                for L, k in jobs]
        for fu in as_completed(futs):
            L, k, n, dt, st = fu.result()
            print(f"l={L} k={k}: {n} factories ({st}, {dt:.0f}s; elapsed {time.time() - t0:.0f}s)", flush=True)
    print("all slices finished", flush=True)
