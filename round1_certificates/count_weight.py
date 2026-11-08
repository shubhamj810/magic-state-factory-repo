#!/usr/bin/env python3
"""Count the harmful faults of one weight of a stored circuit with two programs
that share no code, and append the run to `evidence/listed_counts.jsonl`.

    python round1_certificates/count_weight.py NAME COLUMNS_JSON W

COLUMNS_JSON holds ``{"k", "N", "columns"}``, the columns as the catalogue
stores them (their SHA-256 is what the record is bound to).

1. mitml (`round2_certificates/evidence/distances/mitml/mitml.c`, unchanged)
   in ``--list`` mode: every harmful accepted set of weight W, written once.
   This script then re-checks every listed set by its own XOR of the column
   supports (distinct columns, check part zero, output part non-zero and equal
   to the output XOR mitml printed), and requires the number of distinct sets
   to equal mitml's own count.  The list is kept, gzipped, in `evidence/lists/`
   (the recorded SHA-256 is that of the uncompressed list).
2. `join` of the small-review agent's `mydist.py` (copied unchanged from the
   research branch, commit 82a5c7e, into `evidence/small_review/`): a numpy
   meet-in-the-middle written from the definitions, sharing no code with
   mitml or with the catalogue, over all columns, in count mode.

Both counts and both accepted counts must agree, or nothing is written.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO / "master_catalog"))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "evidence" / "small_review"))

import constructions as K                                         # noqa: E402
import sweep as SWEEP                                             # noqa: E402
import mydist                                                     # noqa: E402

OUT = HERE / "evidence" / "listed_counts.jsonl"
LISTS = HERE / "evidence" / "lists"
MYDIST = HERE / "evidence" / "small_review" / "mydist.py"


def check_list(path, columns, k, w):
    """Distinct sets in mitml's list, each re-checked here; returns their number."""
    seen = set()
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        left, right = line.split(":")
        idx = tuple(int(x) for x in left.split())
        words = [int(x, 16) for x in right.split()]
        if len(idx) != w or len(set(idx)) != w:
            raise AssertionError(f"listed set {idx} is not {w} distinct columns")
        acc = set()
        for j in idx:
            acc ^= set(columns[j])
        if any(q >= k for q in acc):
            raise AssertionError(f"listed set {idx} has a non-zero check part")
        out = sum(1 << q for q in acc)
        if not out:
            raise AssertionError(f"listed set {idx} is harmless")
        if out != sum(v << (64 * i) for i, v in enumerate(words)):
            raise AssertionError(f"listed set {idx}: output XOR differs from mitml's")
        key = tuple(sorted(idx))
        if key in seen:
            raise AssertionError(f"listed set {idx} appears twice")
        seen.add(key)
    return len(seen)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("name")
    ap.add_argument("columns_json")
    ap.add_argument("w", type=int)
    ap.add_argument("--parts", type=int, default=8)
    ap.add_argument("--scratch", default=None,
                    help="a test run: write the list and the record into this folder "
                         "instead of evidence/")
    args = ap.parse_args(argv)
    out_file, lists = OUT, LISTS
    if args.scratch:
        out_file = Path(args.scratch) / "listed_counts.jsonl"
        lists = Path(args.scratch)
    blob = json.loads(Path(args.columns_json).read_text())
    columns, k, N, w = blob["columns"], blob["k"], blob["N"], args.w
    digest = K.digest(columns)
    lists.mkdir(parents=True, exist_ok=True)
    listing = lists / f"{args.name}_w{w}.txt"
    with tempfile.TemporaryDirectory() as scratch:
        problem = Path(scratch) / "p.bin"
        sw = SWEEP.problem(columns, k, N, problem)
        binary = SWEEP.compile_mitml(sw, scratch)
        res = json.loads(subprocess.run(
            [str(binary), str(problem), str(w), "--list", str(listing),
             "--parts", str(args.parts)],
            check=True, capture_output=True, text=True).stdout)
    if res["complete"] != 1 or "harmful" not in res:
        raise AssertionError(f"mitml did not finish: {res}")
    distinct = check_list(listing, columns, k, w)
    if not distinct == res["harmful"] == res["listed"]:
        raise AssertionError(f"mitml: {res['harmful']} harmful, {res['listed']} listed, "
                             f"{distinct} distinct re-checked sets")
    started = time.time()
    a, b = mydist.split(w)
    mine = mydist.join(mydist.Packed(columns, k, N), a, b, stop_first=False, count=True)
    if mine["count"] is None or not mine["complete_pass"]:
        raise AssertionError(f"mydist did not finish: {mine}")
    accepted = mine["accepted_raw"] // math.comb(w, a)
    if mine["accepted_raw"] % math.comb(w, a):
        raise AssertionError("mydist: the accepted tally does not divide")
    if (mine["count"], accepted) != (res["harmful"], res["accepted"]):
        raise AssertionError(f"the counts disagree: mitml {res['harmful']} harmful, "
                             f"{res['accepted']} accepted; mydist {mine['count']}, {accepted}")
    text = listing.read_bytes()
    packed = listing.with_name(listing.name + ".gz")
    packed.write_bytes(gzip.compress(text, compresslevel=9, mtime=0))
    listing.unlink()
    listing = packed
    record = {"name": args.name, "n": len(columns), "k": k, "N": N,
              "columns_sha256": digest, "weight": w,
              "mitml": {"harmful": res["harmful"], "accepted": res["accepted"],
                        "listed": res["listed"], "rechecked": distinct,
                        "parts_log2": res["parts_log2"], "seconds": res["seconds"],
                        "list_file": (str(listing.relative_to(REPO)) if not args.scratch
                                      else str(listing)),
                        "list_sha256": hashlib.sha256(text).hexdigest(),
                        "mitml_sha256": hashlib.sha256(SWEEP.SOURCE.read_bytes()).hexdigest()},
              "mydist": {"harmful": mine["count"], "accepted": accepted, "a": a, "b": b,
                         "seconds": round(time.time() - started, 1),
                         "mydist_sha256": hashlib.sha256(MYDIST.read_bytes()).hexdigest()},
              "date": time.strftime("%Y-%m-%d")}
    with open(out_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    print(json.dumps(record))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
