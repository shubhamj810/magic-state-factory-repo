#!/usr/bin/env python3
"""Write `certificates.json` and `coefficients.json` for the circuits of the
first research round that the catalogue imports as constructions.

    python round1_certificates/assemble.py            # write both files
    python round1_certificates/assemble.py --check    # compare with them

Two kinds of evidence:

* `evidence/mitml_sweeps.jsonl`: runs of mitml made in this repository by
  `sweep.py` on the columns the large file stores, rebuilt from each
  construction.  A sweep whose weights 1..u are all complete with no harmful
  fault gives the lower bound u + 1; a count run gives the number of harmful
  faults of one weight.
* counts the research made on Zaratan, copied to `evidence/research/`: the
  plan kernel's weight-7 counts of the three [[930,94,7]] circuits
  (`lift_counts.jsonl`, from research/search/lift/data/zaratan_sync at
  1300c55) and the Plücker count of the CCZ frame's weight-16 faults
  (`plucker_q4_slices.jsonl` and `plucker_count.c`, from
  research/search/parents at 1300c55).  The research ran them on its own
  column order; a count does not depend on the order, and this script checks
  that the research's columns are the construction's columns in its native
  order (the SHA-256 the research recorded) before binding the count to the
  stored, sorted columns.

Every record is bound to its circuit by the SHA-256 of the stored columns.
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

EV = HERE / "evidence"
CERTS = HERE / "certificates.json"
COUNTS = HERE / "coefficients.json"
MITML = ("mitml, the meet-in-the-middle sweep of the second-round distance "
         "search (round2_certificates/evidence/distances/mitml/mitml.c), run "
         "here by round1_certificates/sweep.py")
KERNEL = ("the plan's meet-in-the-middle kernel in count mode, run by the lift "
          "search on Zaratan (round1_certificates/evidence/research/lift_counts.jsonl)")
PLUCKER = ("plucker_count.c of the parents search: every 4-dimensional subspace "
           "of F_2^12 and its output minors (round1_certificates/evidence/research/)")


def jsonl(path):
    return [json.loads(x) for x in Path(path).read_text().splitlines() if x.strip()]


def assemble():
    certs, counts = [], []
    for run in jsonl(EV / "mitml_sweeps.jsonl"):
        if "construction" in run:
            cols = K.columns(run["construction"])
            digest = K.digest(cols)
            if digest != run["columns_sha256"] or len(cols) != run["n"]:
                raise AssertionError(f"{run['name']}: the run's columns are not the "
                                     f"construction's")
        else:                     # a circuit stored as columns, named by digest
            digest = run["columns_sha256"]
        base = {"name": run["name"], "n": run["n"], "k": run["k"], "N": run["N"],
                "columns_sha256": digest, "tool": MITML}
        if run["mode"] == "sweep":
            upto = 0
            for w in run["weights"]:
                if w["w"] != upto + 1 or not w["complete"] or w["harmful"]:
                    break
                upto = w["w"]
            if upto:
                certs.append({**base, "lower_bound": upto + 1,
                              "how": f"count mode, weights 1 to {upto} complete with "
                                     f"no harmful fault ({run['date']})"})
        else:
            (w,) = run["weights"]
            if not w["complete"]:
                raise AssertionError(f"{run['name']}: an incomplete count")
            counts.append({**base, "weight": w["w"], "count": w["harmful"],
                           "accepted": w["accepted"],
                           "how": f"count mode over 2^{w['parts_log2']} partitions "
                                  f"in {w['slices']} slice(s) ({run['date']})"})
    # the research's counts, bound through the native order
    native = json.loads((EV / "research" / "native_digests.json").read_text())["circuits"]
    for rec in jsonl(EV / "research" / "lift_counts.jsonl"):
        name = Path(rec["row"]).stem
        if name not in native:
            continue
        item = native[name]
        cons = item["construction"]
        if K.digest(RM.native_columns(cons)) != item["research_sha256"]:
            raise AssertionError(f"{name}: the native columns are not the research's")
        cols = K.columns(cons)
        counts.append({"name": name, "n": len(cols), "k": cons["k"], "N": cons["N"],
                       "columns_sha256": K.digest(cols), "tool": KERNEL,
                       "weight": rec["w"], "count": rec["harmful"],
                       "accepted": rec["accepted"],
                       "how": f"{rec['seconds']} s on Zaratan, on the research's "
                              f"column order {item['research_sha256'][:16]}..."})
    # the CCZ frame: A_16 = 2^(m-q) x the 4-dimensional subspaces with some
    # nonzero output minor (research/search/parents/REPORT.md 1.5), from the
    # 64 slices of plucker_count run on sets_q4.txt, which must be this
    # construction's family of 165 sets
    name = "ccz-frame-q4-c55"
    cons = native[name]["construction"]
    lines = (EV / "research" / "sets_q4.txt").read_text().split("\n")
    m, q, nsets = map(int, lines[0].split())
    sets = {frozenset(map(int, x.split())) for x in lines[1:1 + nsets]}
    mine = {frozenset(t) for triple in cons["triples"] for t in triple}
    if (m, q, nsets) != (3 * cons["q"], cons["q"], cons["k"]) or sets != mine:
        raise AssertionError("sets_q4.txt is not the construction's family of sets")
    slices = jsonl(EV / "research" / "plucker_q4_slices.jsonl")
    if sorted(r["slice"][0] for r in slices) != list(range(64)) \
            or any(r["slice"][1] != 64 or (r["m"], r["q"], r["k"]) != (m, q, nsets)
                   for r in slices):
        raise AssertionError("the Plücker slices are not 0..63 of 64 on this family")
    total = sum(r["subspaces"] for r in slices)
    harmless = sum(r["harmless"] for r in slices)
    if total != 13_910_980_083:          # the Gaussian binomial [12 choose 4]_2
        raise AssertionError("the slices do not cover every 4-dimensional subspace")
    cols = K.columns(cons)
    counts.append({"name": name, "n": len(cols), "k": cons["k"], "N": cons["N"],
                   "columns_sha256": K.digest(cols), "tool": PLUCKER,
                   "weight": 2 ** q, "count": (total - harmless) * 2 ** (m - q),
                   "accepted": None,
                   "how": f"{total} subspaces (the Gaussian binomial), {harmless} with "
                          f"every output minor zero; each of the others gives "
                          f"2^{m - q} harmful cosets (Zaratan, 64 slices)"})
    return certs, counts


def render(blob):
    text = json.dumps(blob, indent=1)
    return re.sub(r"\[\s*\n\s*((?:-?\d+,\s+)*-?\d+)\s+\]",
                  lambda m: "[" + re.sub(r"\s+", " ", m.group(1)) + "]", text) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    certs, counts = assemble()
    about = ("Evidence for circuits of the first research round of 6 to 7 November "
             "2026 that the catalogue stores as constructions; each record is bound "
             "by columns_sha256 to the columns constructions.columns builds. Written "
             "by round1_certificates/assemble.py.")
    texts = {CERTS: render({"about": about + " lower_bound: every weight below it "
                            "swept completely with no harmful fault.",
                            "method": "exhaustive search", "records": certs}),
             COUNTS: render({"about": about + " count: the harmful accepted faults "
                             "of the given weight.", "records": counts})}
    if args.check:
        stale = [p.name for p, t in texts.items()
                 if not p.exists() or p.read_text(encoding="utf-8") != t]
        if stale:
            raise SystemExit(f"out of date: {', '.join(stale)}")
        print("certificates.json and coefficients.json are up to date")
        return 0
    for p, t in texts.items():
        p.write_text(t, encoding="utf-8")
    print(f"wrote {len(certs)} distance and {len(counts)} count records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
