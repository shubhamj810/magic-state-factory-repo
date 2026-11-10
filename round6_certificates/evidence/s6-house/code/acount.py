#!/usr/bin/env python3
"""Count the harmful faults of one weight of a catalogue row with two programs, and append a record.

    python acount.py LABEL W [--mitml list|count|none] [--mparts Q] [--mslices M]
                             [--plan] [--pparts Q] [--pslices M] [--workers P] [--out FILE]

The row is data/rows/LABEL.json (columns as the catalogue stores them, exported by the lead's
catalogfile.load_all(); the record carries their SHA-256, the constructions.digest convention).

* mitml (round2_certificates/evidence/distances/mitml/mitml.c, unchanged, sha256 79c7eeb9...):
  --list writes every harmful w-set once; each listed set is re-checked here by its own XOR of the
  column supports (round1_certificates/count_weight.check_list, imported read-only), and the number of
  distinct re-checked sets must equal mitml's count.  --count sums the raw tallies of all slices and
  divides by C(w, ceil(w/2)), as round1_certificates/sweep.py does.
* the plan kernel (research/plan/mitm/mitm.c, unchanged, sha256 e0d4de7e..., the second program of the
  round-2 counts in round2_certificates/evidence/plan/A_d_counts.json): hashed partitions of the FULL
  syndrome, a different partition key from mitml's linear functionals; w <= 8, r <= 128.

Slices of one program run on --workers processes at once (default 1: one after another).
Both harmful and accepted counts must agree between the programs that ran, or the record says so.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import struct
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOP = HERE.parent
ROOT = Path("/Users/shubhamjain/Documents/IBM internship/Shraddha (Magic states)")
REPO = Path(__import__("os").environ.get("MSF_REPO", ROOT / "magic-state-factory-repo"))
sys.path.insert(0, str(REPO / "round1_certificates"))
sys.path.insert(0, str(REPO / "round1_certificates" / "evidence" / "small_review"))
sys.path.insert(0, str(REPO / "master_catalog"))
import count_weight as CW                                             # noqa: E402

MITML_SRC = HERE / "mitml" / "mitml.c"
PLAN_SRC = HERE / "plan" / "mitm.c"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(columns):
    return hashlib.sha256(json.dumps(columns, separators=(",", ":")).encode()).hexdigest()


def masks(columns, k):
    syn, out = [], []
    for c in columns:
        syn.append(sum(1 << (q - k) for q in c if q >= k))
        out.append(sum(1 << q for q in c if q < k))
    return syn, out


def write_problem(path, columns, k, N, sw=None):
    r = N - k
    sw = sw or max(1, (r + 63) // 64)
    ow = max(1, (k + 63) // 64)
    syn, out = masks(columns, k)
    with open(path, "wb") as f:
        f.write(struct.pack("<iii", len(columns), sw, ow))
        for s, o in zip(syn, out):
            words = [(s >> (64 * w)) & (2**64 - 1) for w in range(sw)] + \
                    [(o >> (64 * w)) & (2**64 - 1) for w in range(ow)]
            f.write(struct.pack("<" + "Q" * len(words), *words))
    return sw


def run_slices(binary, problem, w, extra, parts, slices, workers):
    def one(i):
        cmd = [str(binary), str(problem), str(w)] + extra + ["--parts", str(parts)]
        if slices > 1:
            cmd += ["--slice", str(i), str(slices)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        # the plan kernel asserts divisibility on every run and exits 4 on a slice whose partial tally does
        # not divide (the splits of one set can fall in different partitions); its JSON line still holds
        # the raw tallies, which are summed over all slices and divided below
        if r.returncode != 0 and not (r.returncode == 4 and slices > 1 and '"tally not divisible"' in r.stdout):
            raise subprocess.CalledProcessError(r.returncode, cmd, r.stdout, r.stderr)
        return json.loads(r.stdout)
    with ThreadPoolExecutor(max(1, min(workers, slices))) as ex:
        res = list(ex.map(one, range(slices)))
    div = comb(w, (w + 1) // 2) if w > 1 else 1
    acc = sum(r["accepted_raw"] for r in res)
    harm = sum(r["harmful_raw"] for r in res)
    complete = all(r["complete"] == 1 for r in res)
    assert {r["divisor"] for r in res} == {div}, "divisor"
    assert acc % div == 0 and harm % div == 0, "tallies do not divide"
    return {"harmful": harm // div, "accepted": acc // div, "complete": complete,
            "parts_log2": parts, "slices": slices,
            "cpu_seconds": round(sum(r.get("seconds", 0.0) for r in res), 1)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("label")
    ap.add_argument("w", type=int)
    ap.add_argument("--rows", default=str(TOP / "data" / "rows"))
    ap.add_argument("--mitml", default="list", choices=["list", "count", "none"])
    ap.add_argument("--mparts", type=int, default=8)
    ap.add_argument("--mslices", type=int, default=1)
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--pparts", type=int, default=-1)
    ap.add_argument("--pslices", type=int, default=1)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--bindir", default=str(HERE))
    ap.add_argument("--out", default=str(TOP / "data" / "counts.jsonl"))
    ap.add_argument("--lists", default=str(TOP / "data" / "lists"))
    a = ap.parse_args(argv)
    row = json.loads((Path(a.rows) / f"{a.label}.json").read_text())
    columns, k, N, w = row["columns"], row["k"], row["N"], a.w
    dig = digest(columns)
    assert dig == row["columns_sha256"], "digest"
    tmp = TOP / "tmp"
    tmp.mkdir(exist_ok=True)
    rec = {"label": a.label, "n": len(columns), "k": k, "N": N, "weight": w, "columns_sha256": dig}
    bindir = Path(a.bindir)
    if a.mitml != "none":
        prob = tmp / f"{a.label}.m.bin"
        sw = write_problem(prob, columns, k, N)
        sw_bin = min(v for v in (1, 2, 3) if sw <= v)
        binary = bindir / "mitml" / f"mitml{sw_bin}"
        t0 = time.time()
        if a.mitml == "list":
            Path(a.lists).mkdir(parents=True, exist_ok=True)
            listing = Path(a.lists) / f"{a.label}_w{w}.txt"
            res = json.loads(subprocess.run([str(binary), str(prob), str(w), "--list", str(listing),
                                             "--parts", str(a.mparts)], check=True,
                                            capture_output=True, text=True).stdout)
            assert res["complete"] == 1, res
            distinct = CW.check_list(listing, columns, k, w)
            assert distinct == res["harmful"] == res["listed"], (distinct, res)
            text = listing.read_bytes()
            gz = listing.with_name(listing.name + ".gz")
            gz.write_bytes(gzip.compress(text, compresslevel=9, mtime=0))
            listing.unlink()
            rec["mitml"] = {"mode": "list", "harmful": res["harmful"], "accepted": res["accepted"],
                            "listed": res["listed"], "rechecked": distinct, "parts_log2": res["parts_log2"],
                            "seconds": res["seconds"], "list_file": str(gz.resolve().relative_to(TOP.resolve())) if str(gz.resolve()).startswith(str(TOP.resolve())) else str(gz),
                            "list_sha256": hashlib.sha256(text).hexdigest(),
                            "list_gz_bytes": gz.stat().st_size}
        else:
            r = run_slices(binary, prob, w, ["--count"], a.mparts, a.mslices, a.workers)
            assert r["complete"], r
            rec["mitml"] = {"mode": "count", **r}
        rec["mitml"]["wall_seconds"] = round(time.time() - t0, 1)
        rec["mitml"]["mitml_sha256"] = sha(MITML_SRC)
        print(json.dumps(rec["mitml"]), flush=True)
    if a.plan:
        prob = tmp / f"{a.label}.p.bin"
        write_problem(prob, columns, k, N, sw=2)
        t0 = time.time()
        if a.pparts < 0:
            nb = comb(len(columns), w // 2)
            q = 0
            while (nb >> q) > (1 << 25):
                q += 1
            a.pparts = q
        r = run_slices(bindir / "plan" / "mitm", prob, w, ["--count"], a.pparts, a.pslices, a.workers)
        assert r["complete"], r
        rec["plan"] = {**r, "wall_seconds": round(time.time() - t0, 1), "mitm_sha256": sha(PLAN_SRC)}
        print(json.dumps(rec["plan"]), flush=True)
    got = [(rec[p]["harmful"], rec[p]["accepted"]) for p in ("mitml", "plan") if p in rec]
    rec["agree"] = len(set(got)) == 1 if len(got) == 2 else None
    rec["A_w"] = got[0][0] if len(set(got)) == 1 else None
    rec["date"] = time.strftime("%Y-%m-%d %H:%M")
    with open(a.out, "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps({k_: rec[k_] for k_ in ("label", "weight", "A_w", "agree")}), flush=True)
    return 0 if rec["agree"] in (True, None) else 5


if __name__ == "__main__":
    raise SystemExit(main())
