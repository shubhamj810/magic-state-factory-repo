#!/usr/bin/env python3
"""Write `coefficients.json` and `certificates.json` from the run records in
`evidence/`.

    python round6_certificates/assemble.py            # write both files
    python round6_certificates/assemble.py --check    # compare with them

The run records are copied unchanged from the research branch (commit
b4f0910): the round-6 housekeeping search s6-house (`evidence/s6-house/`,
from research/search2/s6-house/) and the three count_weight.py runs of
8 November 2026 whose lists are too large to keep here
(`evidence/stage3/listed_counts_round4.jsonl`, from
research/search2/catalogue/stage3/data/lists/listed_counts.jsonl).

A count record is written for a catalogue row only where s6-house's
`results.json` calls the row's count "accepted (two programs)", and only
from the raw run records, never from `results.json` itself: every program's
harmful count must equal the stated A_d, programs that count accepted
faults must agree on those too, and the run must be complete.  Each record
is bound to the row by the SHA-256 of its columns as the catalogue stores
them (`constructions.digest`), and the row's n, k and N must match.  A
trellis run on another column order is used only when that order is a
permutation of the stored columns.

A distance record is written for a tropidist run on the whole circuit (all
anchors) whose threshold K - 1 was exhausted and K found, with the fault it
found re-checked here by `faultcore.Circuit.harmful` and by the XOR of the
wire masks.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO / "master_catalog"))

import catalogfile as CF                                          # noqa: E402
import constructions as K                                         # noqa: E402
import faultcore as FC                                            # noqa: E402

EV = HERE / "evidence" / "s6-house"
STAGE3 = HERE / "evidence" / "stage3" / "listed_counts_round4.jsonl"
COEFFICIENTS = HERE / "coefficients.json"
CERTIFICATES = HERE / "certificates.json"

MITML_SHA = "79c7eeb92ecb3cc9816ad2399bb485b49c2685ce1830dd356c433a6abcd5a0c7"
PLAN_SHA = "e0d4de7e29515356b943807b64d4ed3c35cd87ea8bcf4dbd3f87f6bc82f323c1"
TRELLIS_SHA = "27f824307b2a16a2e7f30f8c890299e7d752ea84afc637ffd1f8e6dab3ae890b"
WDIST_SHA = "26237eac4a8c60ca5bf77757656762a9a32389dc668b6dfa591b64fd59f6f79a"

#: The tools, as the catalogue rows name them.
MITML_LIST = ("mitml in list mode, every listed set re-checked by its own XOR "
              "(round2_certificates/evidence/distances/mitml/mitml.c, run by the round-6 "
              "search s6-house, round6_certificates/evidence/s6-house/code/acount.py)")
MITML_COUNT = ("mitml in count mode on the UMD cluster Zaratan "
               "(round2_certificates/evidence/distances/mitml/mitml.c, run by the round-6 "
               "search s6-house)")
KERNEL = ("the plan's meet-in-the-middle kernel (round2_certificates/evidence/plan/mitm/mitm.c), "
          "run by the round-6 search s6-house")
MACW = ("MacWilliams: every word of the check span and of the full span listed by wdist.c, "
        "Krawtchouk sums exact (round6_certificates/evidence/s6-house/code/wdist/)")
TRELLIS = ("the counting syndrome trellis (round2_certificates/evidence/distances/trellis/"
           "trellis_count.c) on an annealed column order "
           "(round6_certificates/evidence/s6-house/data/orders/)")
LIST_8NOV = ("mitml in list mode, run on 8 November 2026 by round1_certificates/count_weight.py, "
             "every set re-checked by its own XOR; the list is not kept here: its SHA-256 is in "
             "the record, and round6_certificates/evidence/s6-house/code/regen.py regenerates it "
             "byte for byte")
MYDIST_8NOV = ("mydist.py of the research's small-review agent (round1_certificates/evidence/"
               "small_review/), a numpy meet-in-the-middle sharing no code with mitml, run on "
               "8 November 2026 by round1_certificates/count_weight.py")
TROPIDIST = ("tropidist (B. Cheng, N. Guo and F. Pan, arXiv:2611.08247), run by the round-6 "
             "search s6-house on the UMD cluster Zaratan over every anchor")


def jsonl(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def recheck(columns, k, N, fault):
    acc = 0
    for j in fault:
        for q in columns[j]:
            acc ^= 1 << q
    literal = acc != 0 and (acc >> k) == 0
    core = FC.Circuit(columns, k, N).harmful(list(fault))
    if len(set(fault)) != len(fault) or not (literal and core):
        raise AssertionError(f"fault {fault}: faultcore {core}, XOR {literal}")


def assemble():
    rows = {r["catalog_label"]: r for r in CF.load_all()["factories"]}
    results = json.loads((EV / "data" / "results.json").read_text())
    raw = {}   # (label, weight) -> list of (tool, harmful, accepted, how)
    digests = {}   # (label, weight) -> the column digests the runs name

    def add(label, w, tool, harmful, accepted, how, digest):
        raw.setdefault((label, w), []).append((tool, harmful, accepted, how))
        digests.setdefault((label, w), set()).add(digest)

    for name in ("counts.jsonl", "zaratan/counts.jsonl", "zaratan/counts_t6_recovered.jsonl"):
        for r in jsonl(EV / "data" / name):
            m, p = r.get("mitml"), r.get("plan")
            if m:
                if m["mitml_sha256"] != MITML_SHA:
                    raise AssertionError(f"{r['label']}: mitml is not the round-2 copy")
                if m["mode"] == "list":
                    if not m["harmful"] == m["listed"] == m["rechecked"]:
                        raise AssertionError(f"{r['label']}: list and count differ")
                    add(r["label"], r["weight"], MITML_LIST, m["harmful"], m["accepted"],
                        f"list mode over 2^{m['parts_log2']} partitions "
                        f"(evidence/s6-house/data/{name})", r["columns_sha256"])
                elif m["mode"] == "count":
                    if m.get("complete") is not True:
                        raise AssertionError(f"{r['label']}: an incomplete mitml count")
                    add(r["label"], r["weight"], MITML_COUNT, m["harmful"], m["accepted"],
                        f"count mode over 2^{m['parts_log2']} partitions in {m['slices']} "
                        f"slices (evidence/s6-house/data/{name})", r["columns_sha256"])
            if p:
                if p.get("complete") is not True or p.get("mitm_sha256") != PLAN_SHA:
                    raise AssertionError(f"{r['label']}: plan kernel run incomplete or not "
                                         f"the round-2 copy")
                add(r["label"], r["weight"], KERNEL, p["harmful"], p["accepted"],
                    f"over 2^{p['parts_log2']} partitions in {p['slices']} slice(s) "
                    f"(evidence/s6-house/data/{name})", r["columns_sha256"])
    for name in ("macw.jsonl", "zaratan/macw.jsonl"):
        for r in jsonl(EV / "data" / name):
            if r["wdist_sha256"] != WDIST_SHA or r["B_kerH"] - r["B_kerG"] != r["A_w"]:
                raise AssertionError(f"{r['label']}: MacWilliams record inconsistent")
            add(r["label"], r["weight"], MACW, r["A_w"], r["B_kerH"],
                f"B_w(ker H) - B_w(ker G) = {r['B_kerH']} - {r['B_kerG']} "
                f"(evidence/s6-house/data/{name})", r["columns_sha256"])
    targets = {(r["label"], r["d"]) for r in results if r["status"] == "accepted (two programs)"}
    for r in jsonl(EV / "data" / "trellis.jsonl"):
        if (r["label"], r["W"]) not in targets:   # a parent counted for the contraction identity
            continue
        if r["trellis_c_sha256"] != TRELLIS_SHA:
            raise AssertionError(f"{r['label']}: trellis is not the round-2 copy")
        W = r["W"]
        if any(r["A"][w] for w in range(1, W)):
            raise AssertionError(f"{r['label']}: the trellis finds harmful faults below {W}")
        add(r["label"], W, TRELLIS, r["A"][W], r["B_kerH"][W],
            f"cut rank {r['maxcut_H']}, order {r['order']} (evidence/s6-house/data/trellis.jsonl)",
            r["columns_sha256"])
    for r in jsonl(STAGE3):
        label = r["name"].split(".", 1)[1]
        m, y = r["mitml"], r["mydist"]
        if not m["harmful"] == m["listed"] == m["rechecked"] == y["harmful"] \
                or m["accepted"] != y["accepted"] or m["mitml_sha256"] != MITML_SHA:
            raise AssertionError(f"{label}: the 8 November programs disagree")
        add(label, r["weight"], LIST_8NOV, m["harmful"], m["accepted"],
            f"list SHA-256 {m['list_sha256']} (uncompressed), regenerated byte for byte by "
            f"regen.py (evidence/s6-house/data/regen.jsonl)", r["columns_sha256"])
        add(label, r["weight"], MYDIST_8NOV, y["harmful"], y["accepted"],
            f"split {y['a']} + {y['b']} (evidence/stage3/listed_counts_round4.jsonl)",
            r["columns_sha256"])
    regen = {r["label"]: r for r in jsonl(EV / "data" / "regen.jsonl")}
    for label in ("348.22.7.a", "452.66.6.a", "470.28.7.a"):
        rec = [r for r in jsonl(STAGE3) if r["name"].endswith(label)][0]
        if regen[label]["raw_list_sha256"] != rec["mitml"]["list_sha256"]:
            raise AssertionError(f"{label}: regen.py did not reproduce the list")

    counts, certs = [], []
    for res in results:
        if res["status"] != "accepted (two programs)":
            continue
        label = res["label"]
        row = rows[label]
        w = row["d"]
        if K.digest(row["columns"]) != res["columns_sha256"] or not row["d_is_exact"] \
                or w != res.get("d", w):
            raise AssertionError(f"{label}: not the row s6-house counted")
        runs = raw.get((label, w), [])
        if digests.get((label, w)) != {K.digest(row["columns"])}:
            raise AssertionError(f"{label}: a run names other columns: {digests.get((label, w))}")
        tools = {t for t, *_ in runs}
        if len(tools) < 2:
            raise AssertionError(f"{label}: fewer than two programs")
        if any(h != res["A_d"] for _t, h, _a, _how in runs):
            raise AssertionError(f"{label}: a program disagrees with A_d = {res['A_d']}")
        accepted = {a for t, _h, a, _how in runs if t not in (MACW, TRELLIS)}
        if len(accepted) > 1:
            raise AssertionError(f"{label}: the accepted counts disagree: {accepted}")
        if TRELLIS in tools:
            order = json.loads((EV / "data" / "orders" / f"{label}.json").read_text())
            if sorted(order) != list(range(row["n"])):
                raise AssertionError(f"{label}: the trellis order is not a permutation")
        seen = set()
        for tool, harmful, acc, how in runs:
            if tool in seen:
                continue
            seen.add(tool)
            counts.append({"label": label, "n": row["n"], "k": row["k"], "N": row["N"],
                           "columns_sha256": K.digest(row["columns"]), "tool": tool,
                           "weight": w, "count": harmful, "accepted": acc, "how": how})
    for r in jsonl(EV / "data" / "zaratan" / "tropidist.jsonl"):
        if r["status"] != "found" or r["n_anchors"] != r["n"]:
            continue
        label = r["label"]
        below = [x for x in jsonl(EV / "data" / "zaratan" / "tropidist.jsonl")
                 if x["label"] == label and x["K"] == r["K"] - 1 and x["status"] == "exhausted"
                 and x["n_anchors"] == x["n"]]
        if not below:
            continue
        row = rows[label]
        recheck(row["columns"], row["k"], row["N"], r["witness"])
        certs.append({"label": label, "n": row["n"], "k": row["k"], "N": row["N"],
                      "columns_sha256": K.digest(row["columns"]), "method": "exhaustive search",
                      "tool": TROPIDIST, "lower_bound": r["K"], "witness": sorted(r["witness"]),
                      "how": (f"threshold {r['K'] - 1} exhausted, {r['K']} found, task depth "
                              f"{r['task_depth']}, {r['threads']} threads "
                              f"(evidence/s6-house/data/zaratan/tropidist.jsonl)")})
    counts.sort(key=lambda c: (c["n"], c["k"], c["label"], c["tool"]))
    certs.sort(key=lambda c: (c["n"], c["label"]))
    about = ("Records of the round-6 housekeeping search s6-house (research branch, "
             "research/search2/s6-house at b4f0910) and of three count_weight.py runs of "
             "8 November 2026, copied to evidence/.  Each record is bound to its circuit by "
             "columns_sha256 (constructions.digest of the stored columns).  Written by "
             "round6_certificates/assemble.py.")
    return ({"about": about + " count: the harmful accepted faults of the given weight.",
             "records": counts},
            {"about": about + " lower_bound: the distance is at least this.", "records": certs})


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    coefficients, certificates = assemble()
    pairs = ((COEFFICIENTS, coefficients), (CERTIFICATES, certificates))
    if args.check:
        stale = [p.name for p, blob in pairs
                 if not p.exists() or json.loads(p.read_text()) != blob]
        if stale:
            print("out of date: " + ", ".join(stale))
            return 1
        print("coefficients.json and certificates.json are up to date")
        return 0
    for path, blob in pairs:
        path.write_text(json.dumps(blob, indent=1) + "\n")
    print(f"wrote {len(coefficients['records'])} count and "
          f"{len(certificates['records'])} distance records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
