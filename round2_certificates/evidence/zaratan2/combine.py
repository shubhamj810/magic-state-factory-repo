#!/usr/bin/env python3
"""combine.py ROWID W Q: sum the 2^Q slice records of out/ROWID_wW_qQ/ and report.

Clean means: every one of the 2^Q slices is present, each has complete == 1, the same n, w, Q and seed,
slice [I, 2^Q] for every I exactly once, the summed raw tallies are divisible by C(W, ceil(W/2)), and the
harmful count is 0, and the b-subsets tabulated over all slices number C(n, floor(W/2)).  Any witness is re-checked by faultcore.Circuit.harmful and the literal XOR."""
import json, sys
from math import comb
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "mitml"))
import mitml as M  # noqa: E402

row_id, w, q = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
d = HERE / "out" / f"{row_id}_w{w}_q{q}"
m = 1 << q
recs, missing = {}, []
for i in range(m):
    try:
        txt = (d / f"s{i}.json").read_text()
    except FileNotFoundError:
        txt = ""
    if not txt.strip():
        missing.append(i); continue
    r = json.loads(txt)
    assert r["slice"] == [i, m] and r["w"] == w and r["parts_log2"] == q and r["count_mode"] == 1, (i, r)
    recs[i] = r
row = M.load_row(row_id)
seeds = {r["seed"] for r in recs.values()}
ns = {r["n"] for r in recs.values()}
incomplete = [i for i, r in recs.items() if r["complete"] != 1]
wits = [r["witness"] for r in recs.values() if r["witness"]]
hr = sum(r["harmful_raw"] for r in recs.values())
ar = sum(r["accepted_raw"] for r in recs.values())
div = comb(w, (w + 1) // 2)
secs = [r["seconds"] for r in recs.values()]
out = {"id": row_id, "sha256": row["sha256"], "n": row["n"], "k": row["k"], "r": row["N"] - row["k"], "w": w,
       "parts_log2": q, "slices": m, "present": len(recs), "missing": len(missing), "incomplete": len(incomplete),
       "seeds": sorted(seeds), "n_ok": ns == {row["n"]}, "harmful_raw": hr, "accepted_raw": ar, "divisor": div,
       "divisible": hr % div == 0 and ar % div == 0,
       "core_seconds": round(sum(secs), 1), "slice_seconds_max": max(secs) if secs else None,
       "table_sum": sum(r["table_sum"] for r in recs.values()), "table_expected": comb(row["n"], w // 2)}
out["table_ok"] = out["table_sum"] == out["table_expected"]
if out["divisible"]:
    out["harmful"], out["accepted"] = hr // div, ar // div
if wits:
    out["witness"] = sorted(wits[0])
    out["witness_checks"] = M.check_witness(row, wits[0])
out["complete"] = int(not missing and not incomplete and len(seeds) == 1 and out["n_ok"] and out["table_ok"])
out["status"] = "found" if wits else ("clean" if out["complete"] and out["divisible"] and hr == 0 else "incomplete")
print(json.dumps(out))
