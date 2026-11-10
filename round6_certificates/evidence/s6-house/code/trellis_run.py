#!/usr/bin/env python3
"""Run the counting trellis of the second-round distance search (round2_certificates/evidence/distances/
trellis/, copied unchanged into code/trellis/) on one of my exported rows, in a given column order.
A_w = B_w(ker H) - B_w(ker G) for w <= W.

    python trellis_run.py LABEL W [ORDER.json]      -> data/trellis.jsonl
"""
import hashlib, json, struct, subprocess, sys, tempfile, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
TOP = HERE.parent
sys.path.insert(0, str(HERE / "trellis"))
import trellis_count as T                                            # noqa: E402
lab, W = sys.argv[1], int(sys.argv[2])
ofile = sys.argv[3] if len(sys.argv) > 3 else None
row = json.loads((TOP / "data" / "rows" / f"{lab}.json").read_text())
cols, k, N = row["columns"], row["k"], row["N"]
assert hashlib.sha256(json.dumps(cols, separators=(",", ":")).encode()).hexdigest() == row["columns_sha256"]
order = json.loads(Path(ofile).read_text()) if ofile else list(range(len(cols)))
assert sorted(order) == list(range(len(cols)))
res = {"label": lab, "columns_sha256": row["columns_sha256"], "W": W, "order": ofile or "stored",
       "trellis_c_sha256": hashlib.sha256((HERE / "trellis" / "trellis_count.c").read_bytes()).hexdigest()}
for name in ("H", "G"):
    vecs = [sum(1 << (q - k) for q in cols[j] if q >= k) if name == "H" else sum(1 << q for q in cols[j]) for j in order]
    nbits = (N - k) if name == "H" else N
    t0 = time.time()
    steps, maxcut = T.steps_for(vecs, nbits, W)
    tprep = time.time() - t0
    with tempfile.NamedTemporaryFile(dir=TOP / "tmp", suffix=".bin", delete=False) as f:
        f.write(struct.pack("<iii", len(steps), W, maxcut))
        for a, b, packed, pg in steps:
            f.write(struct.pack("<ii", a, b))
            f.write(struct.pack("<%dQ" % (a + 1), *(packed + [pg])))
        fn = f.name
    t1 = time.time()
    r = subprocess.run([str(HERE / "trellis" / "trellis_count"), fn], capture_output=True, text=True)
    Path(fn).unlink()
    if r.returncode:
        raise SystemExit(r.stderr)
    res[f"B_ker{name}"] = [int(x) for x in r.stdout.split()]
    res[f"maxcut_{name}"] = maxcut
    res[f"seconds_{name}"] = [round(tprep, 1), round(time.time() - t1, 1)]
res["A"] = [a - b for a, b in zip(res["B_kerH"], res["B_kerG"])]
with open(TOP / "data" / "trellis.jsonl", "a") as f:
    f.write(json.dumps(res) + "\n")
print(json.dumps(res))
