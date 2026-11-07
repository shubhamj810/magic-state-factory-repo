"""Harmful-fault sweep to weight 2A (harm.c), exact re-check of every candidate.
    python harm.py PROBLEM.json A [--bb B]"""
import json, random, struct, subprocess, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dist as DI
t0 = time.time()
path, A = sys.argv[1], int(sys.argv[2])
bb = int(sys.argv[sys.argv.index("--bb") + 1]) if "--bb" in sys.argv else 4
d = json.load(open(path)); k, N, cols = d["k"], d["N"], d["columns"]
syn, out = DI.masks(cols, k)
ps = DI.project(syn, N - k, 31)
po = DI.project(out, k, 32)
bp = HERE.parent / "tmp" / f"harm_{int(t0)}.bin"
with open(bp, "wb") as f:
    f.write(struct.pack("<I", len(cols)))
    for a, b in zip(ps, po):
        f.write(struct.pack("<QQ", a, b))
r = subprocess.run([str(HERE.parent / "tmp" / "harm"), str(bp), str(A), str(bb)], capture_output=True, text=True)
bp.unlink()
genuine = []
for line in r.stdout.split("\n"):
    if line.startswith("H"):
        l, rr = line[1:].split("|")
        F = sorted(set(int(x) for x in l.split()) ^ set(int(x) for x in rr.split()))
        s = o = 0
        for j in F:
            s ^= syn[j]; o ^= out[j]
        if F and s == 0 and o:
            genuine.append(F)
summ = [l for l in r.stdout.split("\n") if l.startswith("SUMMARY")]
print(json.dumps({"file": path, "A": A, "summary": summ, "harmful_found": len(genuine),
                  "min_harmful_weight": min((len(F) for F in genuine), default=None),
                  "example": genuine[:1], "seconds": round(time.time() - t0, 1)}), flush=True)
