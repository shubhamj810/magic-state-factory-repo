#!/usr/bin/env python3
"""The two doublings of Berardini et al.'s [[89,1,17]] code: write
`berardini_certificates.json` and `berardini_factories.json`.

    python transversal_t_codes/berardini.py            # write both files
    python transversal_t_codes/berardini.py --check    # compare with them

Berardini, Dastbasteh, Etxezarreta Martinez, Jain and Sanz Larrarte
(arXiv:2412.08586) take C, the cyclic self-orthogonal [89,44] code of
`odd_distance.G_EXP`, and their Theorem 12 doubles it onto a triorthogonal
[[n2,1,d2]] code with the matrix

    [ 1  1  1      ]   the logical row
    [ C  C  0      ]
    [ 0  0  C2'    ]   the inner code's checks
    [ 0  1  1      ]

giving [[2*89 + n2, 1, min(d1, d2 + 2)]], d1 the least odd weight of C^perp.
This is the doubling of Jain and Albert, and the proof in the docstring of
`certify_distances.py` covers it.  Their Example 1 uses the [[575,1,15]] code
of Jain and Albert (`[[753,1,17]]`); the catalogue's second-round search did
the same with A. Gong's [[559,1,15]] (`[[737,1,17]]`).

The inputs are all proved here: d1 = 17 by `odd_distance.py`
(`berardini89_distance.json`, the Brouwer-Zimmermann bound on C^perp), and
d2 = 15 is the catalogue's distance of 575.1.15.a and 559.1.15.a, exact by
the doubling theorem along chains of proved inputs (`distance_certificates.json`).
This script builds the two circuits from C and those rows, checks they are the
circuits the research found (the SHA-256 it keyed them by), and writes a
theorem record with the bound and a fault of that weight: the lightest odd
word of C^perp on the first block, re-checked with faultcore and by the XOR of
the wire masks.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "master_catalog"))

import catalogfile as CF                                          # noqa: E402
import constructions as K                                         # noqa: E402
import faultcore as FC                                            # noqa: E402
import odd_distance as O                                          # noqa: E402

N1 = 89
D1_RECORD = HERE / "berardini89_distance.json"
CERTS = HERE / "berardini_certificates.json"
FACTORIES = HERE / "berardini_factories.json"
#: The circuits as the research keyed them (research/search2/small-lit/
#: berardini_codes.json at f1083d7): the SHA-256 of the columns.
RESEARCH = {"575.1.6.a": "4799bd9cc632", "559.1.6.a": "8a333b56dd5f"}
TOOL = ("Theorem 12 of Berardini et al. (arXiv:2412.08586), the doubling of Jain "
        "and Albert: d >= min(d1, d2 + 2), with d1 = 17 for the cyclic [89,44] code "
        "proved by transversal_t_codes/odd_distance.py and d2 = 15 the catalogue's "
        "distance of the inner row")


def build(inner):
    n2, N2 = inner["n"], inner["N"]
    rows2 = [0] * N2
    for j, c in enumerate(inner["columns"]):
        for q in c:
            rows2[q] |= 1 << j
    if rows2[0] != (1 << n2) - 1:
        raise AssertionError("the inner code's logical row is not all-ones")
    C = [sum(1 << e for e in O.G_EXP) << i for i in range(N1 - 45)]
    n = 2 * N1 + n2
    out = (1 << n) - 1
    checks = [c | (c << N1) for c in C] + [c << (2 * N1) for c in rows2[1:]] \
        + [(((1 << N1) - 1) << N1) | (((1 << n2) - 1) << (2 * N1))]
    rows = [out] + checks
    return [[r for r in range(len(rows)) if rows[r] >> j & 1] for j in range(n)], len(rows)


def harmful(cols, k, N, wit):
    acc = 0
    for j in wit:
        for q in cols[j]:
            acc ^= 1 << q
    return acc != 0 and (acc >> k) == 0 and FC.Circuit(cols, k, N).harmful(list(wit))


def assemble():
    d1rec = json.loads(D1_RECORD.read_text())
    C, D = O.berardini_code()
    again = O.odd_distance_bound(D, N1, *d1rec["t"])
    if again["bound"] != 17 or d1rec["bound"] != 17 \
            or again["lightest_odd_word"] != d1rec["lightest_odd_word"]:
        raise AssertionError("d1 = 17 does not reproduce")
    rows = {}
    for r in CF.load_all()["factories"]:
        for name in [r["catalog_label"]] + (r.get("former_labels") or []):
            rows[name] = r
    certs, factories = [], []
    for former, prefix in RESEARCH.items():
        inner = rows[former]
        if not (inner["d_is_exact"] and inner["d"] == 15 and inner["k"] == 1):
            raise AssertionError(f"{former}: not exact at 15")
        cols, N = build(inner)
        digest = K.digest(cols)
        if not digest.startswith(prefix):
            raise AssertionError(f"{former}: the doubling is not the research's circuit")
        wit = d1rec["lightest_odd_word"]               # block 1 is columns 0..88
        if len(wit) != 17 or not harmful(cols, 1, N, wit):
            raise AssertionError(f"{former}: the fault does not hold")
        name = f"berardini-{len(cols)}"
        certs.append({"name": name, "n": len(cols), "k": 1, "N": N,
                      "columns_sha256": digest, "tool": TOOL,
                      "lower_bound": min(17, inner["d"] + 2), "witness": wit,
                      "inner_row": inner["catalog_label"],
                      "how": "d1 from transversal_t_codes/berardini89_distance.json; "
                             f"d2 = {inner['d']} for {inner['catalog_label']}"})
        factories.append({"k": 1, "N": N, "n": len(cols), "columns": cols,
                          "label": name, "inner": inner["catalog_label"]})
    return certs, factories


def render(blob):
    text = json.dumps(blob, indent=1)
    return re.sub(r"\[\s*\n\s*((?:-?\d+,\s+)*-?\d+)\s+\]",
                  lambda m: "[" + re.sub(r"\s+", " ", m.group(1)) + "]", text) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    certs, factories = assemble()
    texts = {CERTS: render({"about": "Theorem 12 of Berardini et al. on two doublings of "
                                     "their [[89,1,17]] code; written by "
                                     "transversal_t_codes/berardini.py.",
                            "method": "theorem", "records": certs}),
             FACTORIES: json.dumps(factories) + "\n"}
    if args.check:
        stale = [p.name for p, t in texts.items()
                 if not p.exists() or p.read_text(encoding="utf-8") != t]
        if stale:
            raise SystemExit(f"out of date: {', '.join(stale)}")
        print("up to date")
        return 0
    for p, t in texts.items():
        p.write_text(t, encoding="utf-8")
    print(f"wrote {len(certs)} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
