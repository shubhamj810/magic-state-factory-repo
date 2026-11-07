"""Factories from the parent C = RM(3,11) + span{x^S : |S| = 4, |S cap W| >= 2}, W = {8, 9, 10} (the (3,2)
threshold family; weighted RM with weights 2,2,2 on W and 3 on the other eight variables, cutoff 9).
Point p = y + 256 z.

    python3 fam11.py SETS.jsonl [--line I] [--wmax W] [--stage0] [--out FILE]
"""
import argparse, json, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import monomial as MO
import sj_sweep as SW
import sanjose as SJ

M = 11
WMASK = 0b111 << 8

def delta(s=3, j=2, m=M):
    W = ((1 << s) - 1) << (m - s)
    out = []
    for a in range(1 << m):
        c = bin(a).count("1")
        if c <= 3 or (c == 4 and bin(a & W).count("1") >= j):
            out.append(a)
    return out

def check_tri(dl, m=M):
    full = (1 << m) - 1
    s = set(dl)
    for a in dl:
        if bin(a).count("1") < 4: continue
        for b in dl:
            ab = a | b
            for c in dl:
                if ab | c == full: return False
    return True

_ROWS = {}
def rows(s=3, j=2):
    if (s, j) not in _ROWS:
        _ROWS[(s, j)] = MO.rows_of(M, delta(s, j))
    return _ROWS[(s, j)]

def build(P, s=3, j=2):
    dl = delta(s, j)
    f = MO.factory(M, dl, sorted(P), rows(s, j))
    if f is None: return None
    k, N, cols, surv = f
    return {"k": k, "N": N, "columns": cols, "survivors": surv}

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("sets"); ap.add_argument("--line", type=int, default=-1)
    ap.add_argument("--wmax", type=int, default=5); ap.add_argument("--stage0", action="store_true"); ap.add_argument("--out")
    ap.add_argument("--s", type=int, default=3); ap.add_argument("--j", type=int, default=2)
    a = ap.parse_args()
    lines = [json.loads(l) for l in open(a.sets)]
    rec0 = lines[a.line]
    P = rec0["points"]
    t0 = time.time()
    b = build(P, a.s, a.j)
    if b is None:
        print(json.dumps({"t": len(P), "dependent": True})); sys.exit(0)
    cols, k, N = b["columns"], b["k"], b["N"]
    rec = {"t": len(P), "n": len(cols), "k": k, "N": N, "nk": round(len(cols) / k, 4), "digest": SJ.digest(cols), "points": sorted(P)}
    print(json.dumps({x: rec[x] for x in ("t", "n", "k", "N", "nk", "digest")}), flush=True)
    if a.stage0:
        import stage0 as S0
        rec["stage0"] = S0.stage0(cols, k, N); print(json.dumps(rec["stage0"]), flush=True)
    fl, wit, per = MO.kernel_distance(cols, k, N, a.wmax)
    rec.update({"kernel_floor": fl, "witness": wit, "per_weight": per, "seconds": round(time.time() - t0, 1)})
    print(json.dumps({x: rec[x] for x in ("kernel_floor", "witness", "per_weight", "seconds")}), flush=True)
    if a.out:
        with open(a.out, "a") as f: f.write(json.dumps(rec) + "\n")
