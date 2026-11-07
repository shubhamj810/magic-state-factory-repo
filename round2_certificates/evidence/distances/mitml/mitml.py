#!/usr/bin/env python3
"""Driver and tests for mitml.c (linear-key meet-in-the-middle sweep, w <= 8, r <= 64*SW checks).

    python mitml.py build                         compile mitml2, mitml3, mitml5 (SW = 2, 3, 5 words)
    python mitml.py test [trials] [seed]          brute force on random small problems, plus agreement
                                                  of slices, seeds and partition counts
    python mitml.py prob ROWID OUT.bin            write the binary problem of data/rows/ROWID.json
    python mitml.py run ROWID W [--count] [--slices M] [--parts Q] [--jobs J] [--seed S] [--mem-mb MB]
                                                  sweep one weight of a row; slices run J at a time;
                                                  one JSON record appended to ../data/mitml_runs.jsonl

Every witness is re-checked with the catalogue's faultcore.Circuit.harmful and by the literal XOR
of the wire masks.  Sliced counts are summed over ALL slices before the division by C(w, a)
(divisibility is asserted on the sum only).
"""
from __future__ import annotations

import itertools
import json
import os
import random
import struct
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOP = HERE.parent
CATREPO = Path(os.environ.get("MSF_CATREPO", next(
    (p for p in ("/Users/shubhamjain/Documents/IBM internship/Shraddha (Magic states)/magic-state-factory-repo",
                 "/scratch/zt1/project/vva-prj/user/sjn/msf/magic-state-factory-repo") if Path(p).exists()), "")))
sys.path.insert(0, str(CATREPO / "master_catalog"))
(TOP / "tmp").mkdir(exist_ok=True)


def binary(sw: int) -> Path:
    for v in (2, 3, 5):
        if sw <= v:
            return HERE / f"mitml{v}"
    raise ValueError("more than 320 checks")


def build():
    for v in (2, 3, 5):
        cmd = ["cc", "-O3", "-march=native", f"-DSW={v}", "-o", str(HERE / f"mitml{v}"), str(HERE / "mitml.c")]
        if sys.platform == "darwin":
            cmd = [c for c in cmd if c != "-march=native"] + ["-mcpu=native"]
        subprocess.run(cmd, check=True)
    print("built", [f"mitml{v}" for v in (2, 3, 5)])


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


def write_problem(path: Path, syn, out, k, r):
    sw = max(1, (r + 63) // 64)
    ow = max(1, (k + 63) // 64)
    assert ow <= 8 and sw <= 5
    with open(path, "wb") as f:
        f.write(struct.pack("<iii", len(syn), sw, ow))
        for s, o in zip(syn, out):
            words = [(s >> (64 * w)) & (2**64 - 1) for w in range(sw)] + [(o >> (64 * w)) & (2**64 - 1) for w in range(ow)]
            f.write(struct.pack("<" + "Q" * len(words), *words))
    return sw


def run_bin(path: Path, sw: int, w: int, count: bool, extra=()):
    cmd = [str(binary(sw)), str(path), str(w)] + (["--count"] if count else []) + [str(x) for x in extra]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"mitml exit {res.returncode}: {res.stdout} {res.stderr}")
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


def combine(parts, w):
    div = comb(w, (w + 1) // 2) if w > 1 else 1
    hr = sum(p["harmful_raw"] for p in parts)
    ar = sum(p["accepted_raw"] for p in parts)
    assert hr % div == 0 and ar % div == 0, (hr, ar, div)
    return ar // div, hr // div


def test(trials=200, seed=11):
    rng = random.Random(seed)
    checked = 0
    with tempfile.TemporaryDirectory(dir=TOP / "tmp") as tmp:
        path = Path(tmp) / "p.bin"
        for t in range(trials):
            n = rng.randint(3, 17)
            r = rng.choice([3, 5, 8, 64, 65, 100, 128, 129, 150, 192, 193, 250, 320])
            k = rng.choice([1, 2, 5, 64, 65, 130])
            dens = rng.choice([0.1, 0.3, 0.5])
            base = [sum(1 << b for b in range(r) if rng.random() < dens) for _ in range(rng.randint(2, 6))]
            syn = []
            for _ in range(n):
                v = 0
                for b in base:
                    if rng.random() < 0.5:
                        v ^= b
                syn.append(v)
            out = [sum(1 << b for b in range(k) if rng.random() < 0.3) for _ in range(n)]
            sw = write_problem(path, syn, out, k, r)
            for w in range(1, min(n, 12) + 1):
                acc, harm = brute_counts(syn, out, w)
                for q in (0, 1, 3):
                    res = run_bin(path, sw, w, True, ["--parts", q, "--seed", rng.randrange(10**9)])
                    assert res["complete"] == 1, res
                    assert res["accepted"] == acc and res["harmful"] == harm, (t, w, q, acc, harm, res)
                # slices summed
                m = rng.choice([2, 3, 4])
                parts = [run_bin(path, sw, w, True, ["--parts", 2, "--slice", i, m]) for i in range(m)]
                assert combine(parts, w) == (acc, harm), (t, w, parts)
                if w >= 2:
                    lst = Path(tmp) / "list.txt"
                    res = run_bin(path, sw, w, True, ["--list", lst, "--parts", 2])
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
                res = run_bin(path, sw, w, False, ["--parts", rng.choice([0, 2])])
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
    print(f"ok: {checked} (problem, weight) pairs agree with brute force (counts, slices, lists, witnesses)")


def load_row(rowid):
    return json.loads((TOP / "data" / "rows" / f"{rowid}.json").read_text())


def prob(rowid, out_path):
    row = load_row(rowid)
    syn, out = masks(row["columns"], row["k"])
    sw = write_problem(Path(out_path), syn, out, row["k"], row["N"] - row["k"])
    print(json.dumps({"id": rowid, "n": row["n"], "k": row["k"], "r": row["N"] - row["k"], "sw": sw}))


def check_witness(row, wit):
    acc = 0
    for j in wit:
        for q in row["columns"][j]:
            acc ^= 1 << q
    out = {"literal_harmful": acc != 0 and (acc >> row["k"]) == 0, "distinct": len(set(wit)) == len(wit)}
    try:
        import faultcore as FC
    except ImportError as e:          # re-checked on the laptop then; the literal check still runs here
        out["faultcore_harmful"] = None
        out["faultcore_error"] = str(e)
        return out
    circ = FC.Circuit(row["columns"], row["k"], row["N"])
    out["faultcore_harmful"] = bool(circ.harmful(list(wit)))
    return out


def run(rowid, w, count=False, slices=1, parts=None, jobs=1, seed=None, mem_mb=None, out=None, tag=None):
    row = load_row(rowid)
    syn, outm = masks(row["columns"], row["k"])
    t0 = time.time()
    with tempfile.TemporaryDirectory(dir=TOP / "tmp") as tmp:
        path = Path(tmp) / "p.bin"
        sw = write_problem(path, syn, outm, row["k"], row["N"] - row["k"])
        extra = []
        if parts is not None:
            extra += ["--parts", parts]
        if seed is not None:
            extra += ["--seed", seed]
        if mem_mb is not None:
            extra += ["--mem-mb", mem_mb]

        def one(i):
            e = list(extra) + (["--slice", i, slices] if slices > 1 else [])
            return run_bin(path, sw, w, count, e)
        with ThreadPoolExecutor(max_workers=jobs) as ex:
            res = list(ex.map(one, range(slices)))
    rec = {"id": rowid, "label": row.get("label"), "sha256": row["sha256"], "n": row["n"], "k": row["k"],
           "r": row["N"] - row["k"], "w": w, "count": count, "slices": slices, "jobs": jobs,
           "kernel": res[0]["kernel"], "parts_log2": res[0]["parts_log2"], "seed": res[0]["seed"],
           "slice_seconds": [p["seconds"] for p in res], "wall_seconds": round(time.time() - t0, 2),
           "host": os.uname().nodename, "tag": tag}
    wit = next((p["witness"] for p in res if p["witness"]), None)
    complete = all(p["complete"] == 1 for p in res)
    if wit:
        rec["witness"] = sorted(wit)
        rec["witness_checks"] = check_witness(row, wit)
        assert rec["witness_checks"]["literal_harmful"] and rec["witness_checks"]["distinct"] \
            and rec["witness_checks"]["faultcore_harmful"] is not False, rec
    if count and complete:
        rec["accepted"], rec["harmful"] = combine(res, w)
    rec["status"] = "found" if wit else ("clean" if complete else "incomplete")
    outp = Path(out) if out else TOP / "data" / "mitml_runs.jsonl"
    with open(outp, "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps(rec), flush=True)
    return rec


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "build":
        build()
    elif cmd == "test":
        test(*(int(x) for x in sys.argv[2:4]))
    elif cmd == "prob":
        prob(sys.argv[2], sys.argv[3])
    elif cmd == "run":
        a = sys.argv[2:]

        def opt(name, conv=int, default=None):
            return conv(a[a.index(name) + 1]) if name in a else default
        run(a[0], int(a[1]), count="--count" in a, slices=opt("--slices", default=1), parts=opt("--parts"),
            jobs=opt("--jobs", default=1), seed=opt("--seed"), mem_mb=opt("--mem-mb"), out=opt("--out", str),
            tag=opt("--tag", str))
