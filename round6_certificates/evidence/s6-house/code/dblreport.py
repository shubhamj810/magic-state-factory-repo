#!/usr/bin/env python3
"""Write data/doubling_counts.json: for every doubled row counted by code/dblformula.py, the structure
check, the ingredients with their sources, the count at every weight up to d, and the direct counts
it is compared with."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
TOP = HERE.parent
sys.path.insert(0, str(HERE))
import dblformula as DF
SRC = {
 "177.1.9.a": ("gong41", "95.1.7.a", "catalogue A_7 of 95.1.7.a = 48,645 (recounted here: mitml + plan kernel)", 2172877, "catalogue (mitml + trellis)"),
 "189.1.9.a": ("qr47", "95.1.7.a", "as above", 2286315, "catalogue (mitml + trellis)"),
 "271.1.11.a": ("qr47", "177.1.9.a", "catalogue A_9 of 177.1.9.a (mitml + trellis)", 106552995, "catalogue (trellis, two orders)"),
 "283.1.11.a": ("qr47", "189.1.9.a", "catalogue A_9 of 189.1.9.a (mitml + trellis)", 111884581, "catalogue (trellis, two orders)"),
 "401.1.13.a": ("gong65", "271.1.11.a", "catalogue A_11 of 271.1.11.a (trellis; this formula reproduces it)", 6958671715, "catalogue (trellis, two orders)"),
 "441.1.13.a": ("qr79", "283.1.11.a", "catalogue A_11 of 283.1.11.a (trellis; this formula reproduces it)", None, "none (mitml has w <= 12; trellis cut rank 31)"),
 "270.1.10.a": ("qr47", "176.1.8.a", "A_8 of 176.1.8.a = 68,229 (mitml list + plan kernel, data/counts.jsonl)", 3206763, "mitml count (Zaratan) and trellis"),
 "318.2.9.a": ("gong41", "154.2.7.a", "A_7 of 154.2.7.a split by flipped outputs (data/flipsplit.jsonl: mitml list + plan kernel)", 4288272, "mitml count (Zaratan, and s4-d8) and trellis"),
 "451.3.9.a": ("gong41", "205.3.7.a", "as above for 205.3.7.a", 2352334, "mitml count (Zaratan, and s4-d8) and trellis"),
 "459.2.9.a": ("gong41", "213.2.7.a", "as above for 213.2.7.a", 2356352, "mitml count (Zaratan) and trellis"),
 "410.2.11.a": ("qr47", "222.2.8.a", "222.2.8.a split by flipped outputs at w = 8 (mitml list + plan kernel) and w = 9 (mitml list + MacWilliams), data/zaratan/t2/flipsplit.jsonl", None, "none (mitml estimate 81 core-hours; trellis cut rank >= 38)"),
}
out = {}
for lab, (blk, inner, isrc, direct, dsrc) in SRC.items():
    s = json.loads((TOP / "data" / "dblspec" / f"{lab}.json").read_text())
    blocks = [(b["n_b"], {int(j): c for j, c in b["W"].items()}, b["label"]) for b in s["blocks"]]
    inner_d = {(int(a), int(b)): c for a, b, c in s["inner"]}
    A = {w: DF.a_w(blocks, s["k"], w, inner_d, s["d_t"])[0] for w in s["weights"]}
    d = max(s["weights"])
    bw = json.loads((TOP / "data" / f"blockw_{blk}.json").read_text()) if blk != "qr79" else \
        {"min_odd": 15, "min_even_nonzero": 16, "note": "no word of weight 1..14: the extended QR [80,40] code has d = 16 (transversal_t_codes/min_distance.py, the catalogue's proof)"}
    out[lab] = {"block": blk, "labels": [b["label"] for b in s["blocks"]], "inner": inner, "d_t": s["d_t"],
                "inner_counts": s["inner"], "inner_source": isrc,
                "block_S_perp": {k: bw.get(k) for k in ("min_odd", "min_even_nonzero", "note") if k in bw},
                "block_odd_words_at_min": bw.get("W", {}).get(str(bw.get("min_odd"))) if "W" in bw else 0,
                "A_by_weight": A, "A_d": A[d], "direct_count": direct, "direct_source": dsrc,
                "agrees_with_direct": (direct == A[d]) if direct is not None else None}
    print(lab, A[d], direct, out[lab]["agrees_with_direct"])
(TOP / "data" / "doubling_counts.json").write_text(json.dumps(out, indent=1))
