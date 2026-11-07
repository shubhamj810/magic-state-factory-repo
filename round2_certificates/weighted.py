#!/usr/bin/env python3
"""Write `weighted_certificates.json` and `weighted_coefficients.json`: the
distances and counts of the second round's weighted Reed-Muller factories.

    python round2_certificates/weighted.py            # write both files
    python round2_certificates/weighted.py --check    # compare with them

The circuits are Wills's weighted Reed-Muller code W on F_2^11 (weight 1 on
three variables, 2 on eight, cutoff 6; arXiv:2608.24000, Definition 2.15)
punctured at a searched set, as `construction_rm.py` builds them
(`punctured-weighted-rm`).  The research (`evidence/weighted/`, research
commit c2df149) and an adversarial review of it (`evidence/review/`, research
commit 121e495) give:

* the fibre theorem of `evidence/weighted/REPORT.md` section 2.4, which
  splits a dual word by its restrictions to the eight fibres z = const and
  bounds each case.  The review found the proof correct and the research's
  `fibproof.py` unsound in Case A (it compares residues that are not in
  canonical form, so it can over-state the bound), and implemented Cases A,
  B and C again (`fibown.py`, `casec.py`, `casea_all1.py`), with a brute
  force over every pair of fibres (`pairfib.py`) on the columns.  For the two
  d = 8 circuits that is the evidence for weight 7, which no exhaustive sweep
  of the whole circuit has covered; weights 1 to 6 are swept exhaustively
  (`round1_certificates/evidence/mitml_sweeps.jsonl`);
* exact counts A_d: 4,745 at weight 7 for [[1842,206,7]], 5,600 and 5,398 at
  weight 8 for [[1893,155,8]] and [[1894,154,8]], by the research's
  `countad.py` (`evidence/weighted/data/A_d.jsonl`) and again by the review's
  own fibre code.

The research and the review name each circuit by the SHA-256 of its columns
in the research's order.  This script checks that the construction's native
order has that digest and binds every record to the sorted columns the large
file stores.  The faults are re-checked with faultcore and by the XOR of the
wire masks.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO / "master_catalog"))

import constructions as K                                         # noqa: E402
import construction_rm as RM                                      # noqa: E402
import faultcore as FC                                            # noqa: E402

EV = HERE / "evidence"
CIRCUITS = EV / "weighted" / "circuits.json"
CERTS = HERE / "weighted_certificates.json"
COUNTS = HERE / "weighted_coefficients.json"
THEOREM = ("the fibre theorem for Wills's weighted Reed-Muller parent on F_2^11 "
           "(round2_certificates/evidence/weighted/REPORT.md section 2.4), in two "
           "implementations: the research's countad.py (Cases B and C) and the "
           "review's fibown.py, casec.py and casea_all1.py (Cases A, B and C), with "
           "the review's brute force over every pair of fibres (pairfib.py); weight "
           "7 rests on this theorem")
SWEEP = ("mitml in count mode: weights 1 to 6 run in this repository "
         "(round1_certificates/evidence/mitml_sweeps.jsonl), weight 7 on Zaratan over "
         "all 4,096 partitions with every C(n,3) 3-set tabulated "
         "(round2_certificates/evidence/zaratan2/out/combined.jsonl)")
COUNT_RESEARCH = ("countad.py of the weighted search, by the fibre decomposition "
                  "(round2_certificates/evidence/weighted/data/A_d.jsonl)")
COUNT_REVIEW = ("the review's own fibre count, fibown.py and casec.py "
                "(round2_certificates/evidence/review/logs/)")


def harmful(cols, k, N, wit):
    acc = 0
    for j in wit:
        for q in cols[j]:
            acc ^= 1 << q
    return acc != 0 and (acc >> k) == 0 and len(set(wit)) == len(wit) \
        and FC.Circuit(cols, k, N).harmful(list(wit))


def assemble():
    circuits = json.loads(CIRCUITS.read_text())["circuits"]
    counts = {r["digest"]: r for r in
              (json.loads(x) for x in (EV / "weighted" / "data" / "A_d.jsonl")
               .read_text().splitlines() if x.strip())}
    certs, coeffs = [], []
    for name, item in circuits.items():
        cons = item["construction"]
        if K.digest(RM.native_columns(cons)) != item["research_sha256"]:
            raise AssertionError(f"{name}: the native columns are not the research's")
        cols = K.columns(cons)
        k, N = cons["k"], cons["N"]
        base = {"name": name, "research_sha256": item["research_sha256"],
                "n": len(cols), "k": k, "N": N, "columns_sha256": K.digest(cols)}
        wit = item["witness"]
        if not harmful(cols, k, N, wit) or len(wit) != item["d"]:
            raise AssertionError(f"{name}: the fault does not hold")
        if item["d"] == 8:
            log = (EV / "review" / "logs" / f"fibown_{item['research_sha256'][:6]}.log").read_text()
            last = json.loads(log.strip().splitlines()[-1])
            b = last["B_counts"]
            if any(b[str(w)] != [0, 0] for w in range(1, 8)) or last["A_min_bound"] < 8:
                raise AssertionError(f"{name}: the review's Cases A and B do not clear weight 7")
            # and the exhaustive sweep: 1..6 here, 7 on Zaratan
            sweeps = [json.loads(x) for x in (REPO / "round1_certificates" / "evidence"
                                              / "mitml_sweeps.jsonl").read_text().splitlines()
                      if x.strip()]
            here = [r for r in sweeps if r["columns_sha256"] == base["columns_sha256"]
                    and r["mode"] == "sweep"]
            ok_here = here and all(any(w["w"] == u and w["complete"] and not w["harmful"]
                                       for w in here[0]["weights"]) for u in range(1, 7))
            zar = [json.loads(x) for x in (EV / "zaratan2" / "out" / "combined.jsonl")
                   .read_text().splitlines() if x.strip()]
            z7 = [r for r in zar if r["sha256"] == item["research_sha256"] and r["w"] == 7]
            ok_z = z7 and all(r["complete"] == 1 and r["harmful"] == 0 and r["missing"] == 0
                              and r["table_ok"] and r["present"] == r["slices"] for r in z7)
            if ok_here and ok_z:
                certs.append({**base, "method": "exhaustive search", "tool": SWEEP,
                              "lower_bound": 8, "witness": wit,
                              "how": f"weights 1 to 6 here; weight 7: {z7[0]['slices']} "
                                     f"of {z7[0]['slices']} slices, {z7[0]['accepted']} "
                                     f"accepted sets, on the research's column order"})
            certs.append({**base, "tool": THEOREM, "lower_bound": 8, "witness": wit,
                          "how": f"review: Case A bound {last['A_min_bound']}, Case B "
                                 f"no word below weight 8 ({last['B_counts']['8'][0]} "
                                 f"at 8); Case C and the pair brute force in "
                                 f"evidence/review/logs/"})
        r = counts.get(item["research_sha256"])
        if r is None or r["D"] != item["d"]:
            raise AssertionError(f"{name}: no count at d")
        coeffs.append({**base, "tool": COUNT_RESEARCH, "weight": r["D"],
                       "count": r["A_D"], "accepted": None,
                       "how": f"Case B {r['case_B_faults']}, Case C {r['case_C_faults']}"})
        log = (EV / "review" / "logs" / f"fibown_{item['research_sha256'][:6]}.log").read_text()
        last = json.loads(log.strip().splitlines()[-1])
        b = last["B_counts"][str(item["d"])][0]
        cfile = EV / "review" / "logs" / f"casec_{item['research_sha256'][:6]}.log"
        casec = json.loads(cfile.read_text().strip().splitlines()[-1])
        if casec["W"] != item["d"]:
            raise AssertionError(f"{name}: Case C ran to weight {casec['W']}")
        light = [w for f in casec["fibres"].values() for w in f["zero_sets_by_weight"]
                 if int(w) < item["d"]]
        if light:
            raise AssertionError(f"{name}: Case C finds a word below d")
        c_words = sum(f["zero_sets_by_weight"].get(str(item["d"]), [0])[0]
                      for f in casec["fibres"].values())
        if b + c_words != r["A_D"]:
            raise AssertionError(f"{name}: the review counts {b} + {c_words}, not {r['A_D']}")
        coeffs.append({**base, "tool": COUNT_REVIEW, "weight": r["D"], "count": b + c_words,
                       "accepted": None,
                       "how": f"Case B {b} (fibown_{item['research_sha256'][:6]}.log), "
                              f"Case C {c_words} ({cfile.name})"})
    return certs, coeffs


def render(blob):
    text = json.dumps(blob, indent=1)
    return re.sub(r"\[\s*\n\s*((?:-?\d+,\s+)*-?\d+)\s+\]",
                  lambda m: "[" + re.sub(r"\s+", " ", m.group(1)) + "]", text) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    certs, coeffs = assemble()
    about = ("The weighted Reed-Muller factories of the second research round; each "
             "record is bound by columns_sha256 to the sorted columns "
             "constructions.columns builds, and names the research's digest of its "
             "own column order. Written by round2_certificates/weighted.py.")
    texts = {CERTS: render({"about": about, "method": "theorem", "records": certs}),
             COUNTS: render({"about": about, "records": coeffs})}
    if args.check:
        stale = [p.name for p, t in texts.items()
                 if not p.exists() or p.read_text(encoding="utf-8") != t]
        if stale:
            raise SystemExit(f"out of date: {', '.join(stale)}")
        print("weighted certificates are up to date")
        return 0
    for p, t in texts.items():
        p.write_text(t, encoding="utf-8")
    print(f"wrote {len(certs)} distance and {len(coeffs)} count records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
