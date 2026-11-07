#!/usr/bin/env python3
"""Sweep a circuit's light weights with mitml, on the columns the catalogue
stores, and append the run to `evidence/mitml_sweeps.jsonl`.

    python round1_certificates/sweep.py NAME CONSTRUCTION_JSON UPTO [--count W]

mitml is the meet-in-the-middle sweep of the second-round distance search,
copied unchanged into `round2_certificates/evidence/distances/mitml/mitml.c`;
this script compiles it into a scratch folder.  The circuit is rebuilt from
its construction object (`master_catalog/constructions.py`), so the columns
are the ones the large file stores, in its order, and the record carries
their SHA-256.  Every weight 1..UPTO is run in count mode over all 2^Q
partitions (in M slices, summed before the division by C(w, a), as mitml's
own driver does), and the record states, per weight, the accepted and
harmful counts and whether every slice completed.  ``--count W`` counts one
weight W instead (for ``A_W``).  A fault mitml reports is not needed here: a
weight is clean exactly when its harmful count is zero.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import subprocess
import sys
import tempfile
import time
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO / "master_catalog"))

import constructions as K                                         # noqa: E402

SOURCE = REPO / "round2_certificates" / "evidence" / "distances" / "mitml" / "mitml.c"
OUT = HERE / "evidence" / "mitml_sweeps.jsonl"


def compile_mitml(sw, folder):
    binary = Path(folder) / f"mitml{sw}"
    cmd = ["cc", "-O3", f"-DSW={sw}", "-o", str(binary), str(SOURCE)]
    cmd += ["-mcpu=native"] if sys.platform == "darwin" else ["-march=native"]
    subprocess.run(cmd, check=True)
    return binary


def problem(columns, k, N, path):
    r = N - k
    sw, ow = max(1, (r + 63) // 64), max(1, (k + 63) // 64)
    if sw not in (1, 2, 3, 4, 5) or ow > 8:
        raise ValueError("too many wires for mitml")
    with open(path, "wb") as f:
        f.write(struct.pack("<iii", len(columns), sw, ow))
        for col in columns:
            s = sum(1 << (q - k) for q in col if q >= k)
            o = sum(1 << q for q in col if q < k)
            words = [(s >> (64 * w)) & (2**64 - 1) for w in range(sw)] \
                + [(o >> (64 * w)) & (2**64 - 1) for w in range(ow)]
            f.write(struct.pack("<" + "Q" * len(words), *words))
    return min(v for v in (2, 3, 5) if sw <= v)


def run_weight(binary, path, w, parts, slices):
    """Accepted and harmful counts of weight ``w``, summed over the slices."""
    acc = harm = 0
    complete, seconds, div = True, 0.0, None
    for i in range(slices):
        cmd = [str(binary), str(path), str(w), "--count", "--parts", str(parts)]
        if slices > 1:
            cmd += ["--slice", str(i), str(slices)]
        res = json.loads(subprocess.run(cmd, check=True, capture_output=True,
                                        text=True).stdout)
        complete &= res["complete"] == 1
        acc += res["accepted_raw"]
        harm += res["harmful_raw"]
        seconds += res["seconds"]
        div = res["divisor"]
    if div != (1 if w == 1 else comb(w, (w + 1) // 2)) or acc % div or harm % div:
        raise AssertionError(f"weight {w}: the tallies do not divide")
    return {"w": w, "accepted": acc // div, "harmful": harm // div,
            "complete": complete, "parts_log2": parts, "slices": slices,
            "seconds": round(seconds, 1)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("name")
    ap.add_argument("construction", help="a JSON file holding the construction "
                    "object, or with --columns an object {k, N, columns}")
    ap.add_argument("--columns", action="store_true",
                    help="the file holds stored columns, not a construction")
    ap.add_argument("upto", type=int)
    ap.add_argument("--count", type=int, default=None)
    ap.add_argument("--parts", type=int, default=8)
    ap.add_argument("--slices", type=int, default=1)
    args = ap.parse_args(argv)
    construction = json.loads(Path(args.construction).read_text())
    if args.columns:
        columns, construction = construction["columns"], None
        blob = json.loads(Path(args.construction).read_text())
        k, N = blob["k"], blob["N"]
    else:
        columns = K.columns(construction)
        k, N = construction["k"], construction["N"]
    weights = [args.count] if args.count else list(range(1, args.upto + 1))
    with tempfile.TemporaryDirectory() as scratch:
        path = Path(scratch) / "p.bin"
        sw = problem(columns, k, N, path)
        binary = compile_mitml(sw, scratch)
        runs = []
        for w in weights:
            runs.append(run_weight(binary, path, w, args.parts if w > 1 else 0,
                                   args.slices if w > 1 else 1))
            print(json.dumps(runs[-1]), flush=True)
    record = {"name": args.name, "n": len(columns), "k": k, "N": N,
              "columns_sha256": K.digest(columns),
              **({"construction": construction} if construction else {}),
              "mode": "count" if args.count else "sweep", "weights": runs,
              "mitml_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "date": time.strftime("%Y-%m-%d")}
    with open(OUT, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
