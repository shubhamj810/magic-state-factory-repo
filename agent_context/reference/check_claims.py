#!/usr/bin/env python3
"""Re-derive every factual claim `03_STATE.md` makes, from the catalogue.

This directory tells you not to believe stored numbers. It would be absurd to
exempt itself, so every figure in `03_STATE.md` is listed here as an assertion
against the shipped `master_catalogue.jsonl` and re-counted on demand.

    python3 check_claims.py path/to/master_catalogue.jsonl

Exits non-zero on any disagreement. If the corpus has moved since this pack was
written, that is what a failure means -- update the prose, not the check.
"""
from __future__ import annotations

import collections
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from verify_factory import verify                                  # noqa: E402

WRITTEN = "2026-09-11"


def claims(rows):
    """(description, computed value, value asserted in 03_STATE.md)."""
    by_floor = collections.Counter(r["d_floor"] for r in rows)
    tuples = collections.Counter((r["n"], r["k_essential"], r["d_display"])
                                 for r in rows)
    pure_t = [r for r in rows if r.get("V_ex") is not None
              and r["gate_degree_counts"].get("1", 0) == r["k_essential"]]

    def one(n, k=None, d=None):
        hits = [r for r in rows if r["n"] == n
                and (k is None or r["k_essential"] == k)
                and (d is None or r["d_floor"] == d)]
        return hits[0] if hits else {}

    rec, prev = one(901, 123), one(902, 122)
    g5 = [r for r in rows if r["d_floor"] == 5 and r.get("gamma_rho") is not None]
    best5 = min(r["gamma_rho"] for r in g5) if g5 else None
    tied5 = [r for r in g5 if abs(r["gamma_rho"] - best5) < 1e-12]
    smallest = one(8)
    problems, facts = verify(smallest["columns"], smallest["k"])

    out = [
        ("distinct verified factories", len(rows), 837),
        ("distances pinned exactly", sum(1 for r in rows if r.get("d_exact")), 812),
        ("A_d known", sum(1 for r in rows if r.get("A_d") is not None), 812),
        ("rows failing verification", sum(1 for r in rows if not r.get("verified_ok")), 0),
        ("rows with spectator outputs", sum(1 for r in rows if r.get("spectators")), 0),
        ("rows with non-independent outputs",
         sum(1 for r in rows if r.get("outputs_independent") is False), 0),
        ("tuples realised by >1 circuit", sum(1 for v in tuples.values() if v > 1), 148),
        ("pure-T rows", len(pure_t), 518),
        ("pure-T rows with n < 1000", sum(1 for r in pure_t if r["n"] < 1000), 486),
        ("rows at d=2", by_floor[2], 33),
        ("rows at d=3", by_floor[3], 579),
        ("rows at d=4", by_floor[4], 108),
        ("rows at d=5", by_floor[5], 76),
        ("rows at d>=6", by_floor[6], 29),
        ("rows at d>=7", by_floor[7], 12),
        ("record gamma", rec.get("gamma"), 1.111377),
        ("record is [[901,123,*]]", (rec.get("n"), rec.get("k_essential")), (901, 123)),
        ("record distance is a FLOOR in the catalogue", rec.get("d_display"), ">= 6"),
        ("record A_d not carried by the catalogue", rec.get("A_d"), None),
        ("previous record gamma", prev.get("gamma"), 1.116552),
        ("previous record A_6", prev.get("A_d"), 2475),
        ("gamma = log(901/123)/log 6", round(math.log(901 / 123) / math.log(6), 6), 1.111377),
        ("best gamma_rho at d=5", best5, 1.119677),
        ("circuits tied there", len(tied5), 4),
        ("their A_5 values", sorted(r["A_d"] for r in tied5), [3152, 3177, 3239, 3401]),
        ("[[74,36,2]] gamma on wires", one(74, 36).get("gamma"), 1.039528),
        ("[[74,36,2]] gamma_rho on T states", one(74, 36).get("gamma_rho"), 1.624491),
        ("[[512,39]] T per CCZ", round(one(512, 39)["n"] / (one(512, 39)["V_ex"] / 2), 3), 39.385),
        ("[[127,23,3]] rate", round(one(127, 23)["n"] / 23, 4), 5.5217),
        ("smallest n at d>=3", min(r["n"] for r in rows if r["d_floor"] >= 3), 15),
        ("d=2 ladder: CCZ", one(8)["n"], 8),
        ("d=2 ladder: CS", one(12, 2)["n"], 12),
        ("d=2 ladder: T", one(14, 1)["n"], 14),
        ("[[8,3,2]] A_2, re-derived here", facts.get("A_d"), 28),
        ("[[8,3,2]] distance, re-derived here", facts.get("d_exact"), 2),
        ("[[8,3,2]] verifies clean", problems, []),
        # 09_BASELINES: the reproduced Haah-Hastings prefactors
        ("HH18 [[109,19,3]] A_3", one(109, 19).get("A_d"), 324),
        ("HH18 [[863,161,3]] A_3", one(863, 161).get("A_d"), 3231),
        ("HH18 [[116,12,4]] A_4", one(116, 12).get("A_d"), 495),
        ("HH18 [[872,152,4]] A_4", one(872, 152).get("A_d"), 1514),
        ("HH18 [[887,137,5]] A_5", one(887, 137).get("A_d"), 709),
        ("HH18 [[912,112,6]] A_6 NOT recounted here",
         one(912, 112).get("A_d"), None),
        # 09_BASELINES section 5: the derived-baseline arithmetic
        ("[[512,39]] T per CCZ",
         round(one(512, 39)["n"] / (one(512, 39)["V_ex"] // 2), 3), 39.385),
        ("published native 512T->10CCZ", round(512 / 10, 3), 51.200),
        ("Jones 4T/CCZ over [[959,65]]",
         round(4 * one(959, 65)["n"] / one(959, 65)["V_ex"], 3), 59.015),
        ("[[512,39]] gamma_rho at the PROVEN floor",
         one(512, 39).get("gamma_rho"), 1.531534),
        # 09_BASELINES section 6: the rate-7.000 cell
        ("rate-7.000 d=3 cell: all five A_3/k",
         sorted(round(r["A_d"] / r["k_essential"], 1) for r in rows
                if r["d_floor"] == 3 and r["k_essential"] in (16, 17)
                and r["n"] in (112, 119)),
         [4.0, 4.6, 6.0, 63.0, 112.0]),
        ("rate-7.000 d=3 cell: the pure-T four",
         sorted(round(r["A_d"] / r["k_essential"], 1) for r in rows
                if r["d_floor"] == 3 and r["k_essential"] in (16, 17)
                and r["n"] in (112, 119) and "CCZ" not in r["gate_short"]),
         [4.0, 4.6, 6.0, 63.0]),
        # 08_HISTORY / 03_STATE landmarks
        ("[[112,16,3]] CCZ^4.T^4 rho",
         round(one(112, 16)["n"] / one(112, 16)["V_ex"], 3), 9.333),
        ("[[127,23,3]] is pure T^23", one(127, 23).get("gate_short"), "T^23"),
    ]
    return out


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    rows = [json.loads(line) for line in open(argv[1]) if line.strip()]
    print(f"checking {len(rows)} catalogue rows against the figures written "
          f"into 03_STATE.md on {WRITTEN}\n")
    bad = 0
    for desc, got, want in claims(rows):
        ok = got == want
        bad += not ok
        print(f"  {'OK ' if ok else 'BAD'}  {desc}: {got}"
              + ("" if ok else f"   <- the pack says {want}"))
    print(f"\n{'ALL CLAIMS HOLD' if not bad else f'{bad} CLAIM(S) STALE'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
