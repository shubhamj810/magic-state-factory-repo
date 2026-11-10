#!/usr/bin/env python3
"""The re-run recipe of a listed count: rebuild mitml's list exactly as round1_certificates/count_weight.py
does (its sweep.problem file, its compile_mitml build, `mitml FILE W --list OUT --parts 8`), and print the
SHA-256 of the raw list and the count, to compare with the stored record's list_sha256.

    python regen.py LABEL W [--parts 8]   -> data/lists_regen/LABEL_wW.txt.gz, data/regen.jsonl
"""
import argparse, gzip, hashlib, json, subprocess, sys, tempfile, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
TOP = HERE.parent
ROOT = Path("/Users/shubhamjain/Documents/IBM internship/Shraddha (Magic states)")
sys.path.insert(0, str(ROOT / "magic-state-factory-repo" / "round1_certificates"))
sys.path.insert(0, str(ROOT / "magic-state-factory-repo" / "master_catalog"))
import sweep as SWEEP                                                 # noqa: E402
ap = argparse.ArgumentParser()
ap.add_argument("label"); ap.add_argument("w", type=int); ap.add_argument("--parts", type=int, default=8)
a = ap.parse_args()
row = json.loads((TOP / "data" / "rows" / f"{a.label}.json").read_text())
out = TOP / "data" / "lists_regen"
out.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(dir=TOP / "tmp") as scratch:
    p = Path(scratch) / "p.bin"
    sw = SWEEP.problem(row["columns"], row["k"], row["N"], p)
    binary = SWEEP.compile_mitml(sw, scratch)
    lst = Path(scratch) / "list.txt"
    t0 = time.time()
    res = json.loads(subprocess.run([str(binary), str(p), str(a.w), "--list", str(lst), "--parts", str(a.parts)],
                                    check=True, capture_output=True, text=True).stdout)
    raw = lst.read_bytes()
gz = out / f"{a.label}_w{a.w}.txt.gz"
gz.write_bytes(gzip.compress(raw, compresslevel=9, mtime=0))
rec = {"label": a.label, "weight": a.w, "columns_sha256": row["columns_sha256"], "SW": sw, "parts": a.parts,
       "harmful": res.get("harmful"), "accepted": res.get("accepted"), "listed": res.get("listed"),
       "raw_list_sha256": hashlib.sha256(raw).hexdigest(), "seconds": round(time.time() - t0, 1),
       "mitml_sha256": hashlib.sha256(SWEEP.SOURCE.read_bytes()).hexdigest()}
with open(TOP / "data" / "regen.jsonl", "a") as f:
    f.write(json.dumps(rec) + "\n")
print(json.dumps(rec))
