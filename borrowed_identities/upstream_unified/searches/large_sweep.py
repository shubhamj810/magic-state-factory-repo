"""Larger two-group sweep: l=2,3,4, k<=8, circuits up to N_max qubits.

Step 1 lists every parameter tuple satisfying the two-group condition (Theorem 5), which needs only binomial sums.
Step 2 builds, verifies by brute force, and classifies one factory per (l, k, n) candidate, keeping the smallest n
per output class. Verification costs 2^N, so it is the only part that grows; results stream to
outputs/large_sweep.csv, and a rerun skips rows already written. When the run ends the Quirk column is moved
into outputs/large_sweep_with_quirk.csv.zip, so the CSV stays small.
Run: python3 searches/large_sweep.py [N_max]
"""
import os, sys, csv, time
from math import comb
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import unified_search as us
from Two_group import build_gate_set, is_borrowed_identity
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "outputs", "large_sweep.csv")
F = ["l", "k", "n", "N", "d", "s_total", "s_O", "reduced", "raw", "zcount", "seconds", "quirk"]
N_MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 14
done = set()
if os.path.exists(OUT):
    for r in csv.DictReader(open(OUT)): done.add((r["l"], r["k"], r["N"], r["s_total"], r["s_O"]))
new = not os.path.exists(OUT)
fh = open(OUT, "a", newline=""); w = csv.DictWriter(fh, fieldnames=F)
if new: w.writeheader()
t0 = time.time()
# step 1: candidate tuples, smallest-n first within each (l, k)
cand = []
for L in (2, 3, 4):
    for k in range(1, 9):
        for N in range(k + 1, N_MAX + 1):
            for st in range(1, 8):
                for so in range(1, 8):
                    pairs, _, _ = build_gate_set(k, N - k, st, so)
                    if not pairs: continue
                    sig = {p: 1 for p in pairs}
                    if L >= 4:
                        sigs = __import__("Two_group").find_valid_signs(L, N, k, pairs)
                        if not sigs: continue
                    elif not is_borrowed_identity(L, N, k, sig):
                        continue
                    n = sum(comb(k, a) * comb(N - k, b) for a, b in pairs if b >= 1)
                    cand.append((L, k, n, N, st, so))
cand.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
print(f"step 1: {len(cand)} valid tuples up to N={N_MAX} in {time.time() - t0:.1f}s", flush=True)
# step 2: verify one per (l, k, n); smallest N first
seen = set(); verified = 0
for L, k, n, N, st, so in cand:
    if (L, k, n) in seen: continue
    if (str(L), str(k), str(N), str(st), str(so)) in done: seen.add((L, k, n)); continue
    seen.add((L, k, n))
    t = time.time()
    pairs, _, _ = build_gate_set(k, N - k, st, so)
    sigma = {p: 1 for p in pairs} if L <= us.SIGN_FREE_MAX_L else __import__("Two_group").find_valid_signs(L, N, k, pairs)[0]
    f = dict(stage="two-group", k=k, r=N - k, gates=us.two_group_gates(k, N - k, sigma), params=f"s_total={st},s_O={so}")
    info = us.classify_factory(f, L)
    if info is None or info["d"] == 1 or not us.is_factory(f, L): continue
    w.writerow({"l": L, "k": k, "n": info["N"], "N": N, "d": info["d"], "s_total": st, "s_O": so, "reduced": info["reduced"],
                "raw": info["raw"], "zcount": info["zcount"], "seconds": round(time.time() - t, 2),
                "quirk": us.quirk_url(f["gates"], N, L, k=k) if N <= 14 else ""})
    fh.flush(); verified += 1
    if verified % 20 == 0: print(f"  verified {verified}; last l={L} k={k} n={n} N={N} ({time.time() - t0:.0f}s)", flush=True)
fh.close()
# publish: the CSV without Quirk links (small), and the full table with links zipped alongside
import zipfile
csv.field_size_limit(sys.maxsize)
rows = list(csv.DictReader(open(OUT)))
ZIP = OUT.replace(".csv", "_with_quirk.csv.zip")
tmp = OUT.replace(".csv", "_with_quirk.csv")
with open(tmp, "w", newline="") as f2:
    w2 = csv.DictWriter(f2, fieldnames=F); w2.writeheader(); w2.writerows(rows)
with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    z.write(tmp, os.path.basename(tmp))
os.remove(tmp)
with open(OUT, "w", newline="") as f2:
    w2 = csv.DictWriter(f2, fieldnames=[x for x in F if x != "quirk"], extrasaction="ignore"); w2.writeheader(); w2.writerows(rows)
print(f"done: {verified} new factories verified in {time.time() - t0:.0f}s -> {OUT} (+ {os.path.basename(ZIP)})", flush=True)
