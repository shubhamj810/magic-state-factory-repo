#!/usr/bin/env python3
"""A compact certificate for a long list of harmful weight-W sets: per-slice counts and hashes.

    python slicecert.py LABEL W LIST.txt.gz [--rows DIR] [--mitml-raw-sha SHA]

The list is mitml's --list output (one set per line: indices, ':', the output XOR in hex words).
Every set is re-checked by its own XOR of the column supports (round1_certificates/count_weight.check_list,
imported read-only).  Slice i holds the sets whose smallest column index is i.  For each slice the
certificate stores its count and the SHA-256 of its canonical text (each set as its sorted indices
joined by single spaces, the sets of the slice in lexicographic order, one per line, no output part).
It also stores the degree of every column (the number of sets containing it; they sum to W times the
total), the SHA-256 of the whole canonical list (the slices' texts concatenated in order of i), and the
SHA-256 of the raw file mitml wrote, which re-running mitml with the same arguments reproduces.

Writes data/certs/LABEL_wW.json.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOP = HERE.parent
ROOT = Path("/Users/shubhamjain/Documents/IBM internship/Shraddha (Magic states)")
import os
REPO = Path(os.environ.get("MSF_REPO", ROOT / "magic-state-factory-repo"))
sys.path.insert(0, str(REPO / "round1_certificates"))
sys.path.insert(0, str(REPO / "round1_certificates" / "evidence" / "small_review"))
sys.path.insert(0, str(REPO / "master_catalog"))
import count_weight as CW                                             # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("label")
    ap.add_argument("w", type=int)
    ap.add_argument("listing")
    ap.add_argument("--rows", default=str(TOP / "data" / "rows"))
    a = ap.parse_args()
    row = json.loads((Path(a.rows) / f"{a.label}.json").read_text())
    cols, k, w = row["columns"], row["k"], a.w
    n = len(cols)
    raw = gzip.decompress(Path(a.listing).read_bytes())
    t0 = time.time()
    with tempfile.NamedTemporaryFile("wb", suffix=".txt", dir=TOP / "tmp", delete=True) as f:
        f.write(raw)
        f.flush()
        distinct = CW.check_list(Path(f.name), cols, k, w)
    slices = [[] for _ in range(n)]
    deg = [0] * n
    for line in raw.decode().splitlines():
        if not line.strip():
            continue
        idx = sorted(int(x) for x in line.split(":")[0].split())
        slices[idx[0]].append(idx)
        for j in idx:
            deg[j] += 1
    whole = hashlib.sha256()
    per = []
    for i, s in enumerate(slices):
        s.sort()
        text = "".join(" ".join(map(str, x)) + "\n" for x in s).encode()
        whole.update(text)
        per.append([i, len(s), hashlib.sha256(text).hexdigest()[:16]])
    total = sum(p[1] for p in per)
    assert total == distinct and sum(deg) == w * total
    cert = {"label": a.label, "columns_sha256": row["columns_sha256"], "weight": w, "count": total,
            "raw_list_sha256": hashlib.sha256(raw).hexdigest(), "canonical_list_sha256": whole.hexdigest(),
            "slice_rule": "slice i = the sets whose smallest column index is i; hash = first 16 hex digits of the "
                          "SHA-256 of the slice's canonical text",
            "slices": [p for p in per if p[1]], "empty_slices": n - sum(1 for p in per if p[1]),
            "degrees": deg, "rechecked_by_own_xor": distinct, "seconds": round(time.time() - t0, 1)}
    out = TOP / "data" / "certs"
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{a.label}_w{w}.json"
    path.write_text(json.dumps(cert, separators=(",", ":")))
    print(json.dumps({k_: cert[k_] for k_ in ("label", "weight", "count", "raw_list_sha256", "canonical_list_sha256",
                                               "empty_slices")}), "bytes", path.stat().st_size)


if __name__ == "__main__":
    main()
