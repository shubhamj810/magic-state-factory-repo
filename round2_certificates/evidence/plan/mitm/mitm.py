#!/usr/bin/env python3
"""Driver and tests for mitm.c, the exact meet-in-the-middle sweep for factories with r <= 128 checks.

    python3 mitm.py test [trials] [seed]          brute-force comparison on random small problems
    python3 mitm.py row LABEL W1-W2 [--count] [--slices M]
                                                  sweep weights W1..W2 of a cached catalogue row
                                                  (../data/rows/LABEL.json, written by tdirect.py)

Every witness the C program returns is re-checked here with the catalogue's faultcore.Circuit.harmful
and by the literal XOR of wire masks.  With --slices M the partitions of one weight are split across M
processes run one after another (the caller decides what runs concurrently); a weight is "clean" only
if every slice is complete and clean.  One JSON line per weight goes to ../data/mitm_runs.jsonl.
"""
from __future__ import annotations

import itertools
import json
import math
import random
import struct
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIST_MODE = False
PLAN = HERE.parent
BIN = HERE / "mitm"
CATREPO = Path("/Users/shubhamjain/Documents/IBM internship/Shraddha (Magic states)/magic-state-factory-repo")
(PLAN / "tmp").mkdir(exist_ok=True)       # scratch space for the binary problem files
sys.path.insert(0, str(CATREPO / "master_catalog"))


def masks(columns, k):
    syn, out = [], []
    for c in columns:
        s = o = 0
        for q in c:
            if q < k:
                o |= 1 << q
            else:
                s |= 1 << (q - k)
        syn.append(s)
        out.append(o)
    return syn, out


def write_problem(path: Path, syn, out, k):
    ow = max(1, (k + 63) // 64)
    assert ow <= 8, "more than 512 outputs"
    assert all(s < (1 << 128) for s in syn), "more than 128 checks"
    with open(path, "wb") as f:
        f.write(struct.pack("<iii", len(syn), 2, ow))
        for s, o in zip(syn, out):
            words = [s & (2**64 - 1), s >> 64] + [(o >> (64 * w)) & (2**64 - 1) for w in range(ow)]
            f.write(struct.pack("<" + "Q" * len(words), *words))


def run_bin(path: Path, w: int, count: bool, extra=()):
    cmd = [str(BIN), str(path), str(w)] + (["--count"] if count else []) + list(extra)
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"mitm exit {res.returncode}: {res.stdout} {res.stderr}")
    return json.loads(res.stdout)


def brute_counts(syn, out, w):
    acc = harm = 0
    for sup in itertools.combinations(range(len(syn)), w):
        s = o = 0
        for j in sup:
            s ^= syn[j]
            o ^= out[j]
        if s == 0:
            acc += 1
            harm += o != 0
    return acc, harm


def test(trials=300, seed=5):
    rng = random.Random(seed)
    checked = 0
    with tempfile.TemporaryDirectory(dir=PLAN / "tmp") as tmp:
        path = Path(tmp) / "p.bin"
        for t in range(trials):
            n = rng.randint(3, 15)
            r = rng.choice([3, 5, 8, 64, 65, 100, 128])
            k = rng.choice([1, 2, 5, 64, 65, 130])
            dens = rng.choice([0.1, 0.3, 0.5])
            # few distinct check patterns so that accepted sets exist; spread bits over both words
            base = [sum(1 << b for b in range(r) if rng.random() < dens) for _ in range(rng.randint(2, 6))]
            syn = []
            for _ in range(n):
                v = 0
                for b in base:
                    if rng.random() < 0.5:
                        v ^= b
                syn.append(v)
            out = [sum(1 << b for b in range(k) if rng.random() < 0.3) for _ in range(n)]
            write_problem(path, syn, out, k)
            for w in range(1, min(n, 8) + 1):
                acc, harm = brute_counts(syn, out, w)
                for q in (0, 2):
                    res = run_bin(path, w, True, ["--parts", str(q)])
                    assert res["complete"] == 1, res
                    assert res["accepted"] == acc and res["harmful"] == harm, (t, w, q, acc, harm, res)
                if w >= 2:
                    lst = Path(tmp) / "list.txt"
                    res = run_bin(path, w, True, ["--list", str(lst)])
                    got = set()
                    for line in lst.read_text().splitlines():
                        idx, hexes = line.split(":")
                        sup = tuple(sorted(int(x) for x in idx.split()))
                        o = sum(int(h, 16) << (64 * i) for i, h in enumerate(hexes.split()))
                        assert len(set(sup)) == w and sup not in got
                        s2 = o2 = 0
                        for j in sup:
                            s2 ^= syn[j]
                            o2 ^= out[j]
                        assert s2 == 0 and o2 == o and o != 0
                        got.add(sup)
                    assert len(got) == harm == res["listed"], (t, w, len(got), harm, res)
                res = run_bin(path, w, False)
                assert (res["status"] == "found") == (harm > 0), (t, w, harm, res)
                if harm:
                    wit = res["witness"]
                    assert len(set(wit)) == w
                    s = o = 0
                    for j in wit:
                        s ^= syn[j]
                        o ^= out[j]
                    assert s == 0 and o != 0
                checked += 1
    print(f"ok: {checked} (problem, weight) pairs agree with brute force, counts and witnesses")


def row_sweep(label, wspec, count=False, slices=1):
    import faultcore as FC
    row = json.loads((PLAN / "data" / "rows" / f"{label}.json").read_text())
    k, N, columns = row["k"], row["N"], row["columns"]
    syn, out = masks(columns, k)
    circuit = FC.Circuit(columns, k, N)
    lo, hi = (int(x) for x in wspec.split("-"))
    with tempfile.TemporaryDirectory(dir=PLAN / "tmp") as tmp:
        path = Path(tmp) / f"{label}.bin"
        write_problem(path, syn, out, k)
        for w in range(lo, hi + 1):
            t0 = time.time()
            parts = []
            for i in range(slices):
                extra = ["--slice", str(i), str(slices)] if slices > 1 else []
                if LIST_MODE:
                    (PLAN / "data" / "faults").mkdir(parents=True, exist_ok=True)
                    extra += ["--list", str(PLAN / "data" / "faults" / f"{label}.w{w}.s{i}.txt")]
                parts.append(run_bin(path, w, count or LIST_MODE, extra))
                if parts[-1]["status"] == "found" and not count:
                    break
            wit = next((p["witness"] for p in parts if p["witness"]), None)
            rec = {"label": label, "n": len(columns), "k": k, "r": N - k, "w": w, "count": count,
                   "slices": slices, "parts": parts, "seconds": round(time.time() - t0, 2)}
            if wit:
                acc = 0
                for j in wit:
                    for q in columns[j]:
                        acc ^= 1 << q
                rec["witness"] = sorted(wit)
                rec["witness_faultcore_harmful"] = circuit.harmful(wit)
                rec["witness_literal_harmful"] = acc != 0 and (acc >> k) == 0
                assert rec["witness_faultcore_harmful"] and rec["witness_literal_harmful"], rec
                rec["status"] = "found"
            elif all(p["complete"] == 1 and p["status"] == "clean" for p in parts) and len(parts) == slices:
                rec["status"] = "clean"
            else:
                rec["status"] = "incomplete"
            if (count or LIST_MODE) and all(p["complete"] for p in parts) and len(parts) == slices:
                div = parts[0]["divisor"]
                hr = sum(p["harmful_raw"] for p in parts)
                ar = sum(p["accepted_raw"] for p in parts)
                assert hr % div == 0 and ar % div == 0
                rec["harmful"], rec["accepted"] = hr // div, ar // div
            with open(PLAN / "data" / "mitm_runs.jsonl", "a") as f:
                f.write(json.dumps(rec) + "\n")
            print(json.dumps({x: rec[x] for x in rec if x != "parts"}), flush=True)
            if rec["status"] == "found" and not count:
                break


if __name__ == "__main__":
    global_list = None
    if sys.argv[1] == "test":
        test(*(int(x) for x in sys.argv[2:4]))
    elif sys.argv[1] == "row":
        args = sys.argv[2:]
        count = "--count" in args
        LIST_MODE = "--list" in args
        slices = int(args[args.index("--slices") + 1]) if "--slices" in args else 1
        row_sweep(args[0], args[1], count=count, slices=slices)
