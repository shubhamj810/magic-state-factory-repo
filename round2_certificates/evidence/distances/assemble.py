#!/usr/bin/env python3
"""Build results.jsonl from the raw records of this folder (and of data/zaratan/ once pulled back).

One JSON line per result: {key, label, sha256, n, k, kind, result, evidence, tools, run_seconds, job_ids,
witness, status, note}.  `kind` is "distance", "A_d" or "witness_at_bound".  Every witness listed here was
re-checked with faultcore.Circuit.harmful and the literal XOR (the raw record says so); this script re-checks
the distance witnesses once more.

    python assemble.py
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLAN = HERE.parents[1] / "plan" / "data"
sys.path.insert(0, str(HERE / "mitml"))
import mitml as M  # noqa: E402

TROPIDIST = "tropidist b03ec2d4 (Cheng, Guo and Pan, arXiv:2611.08247)"
CATALOGUE = "catalogue faultcore at dadb221"


def sha_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:12]


MITML = f"mitml.c sha256 {sha_file(HERE / 'mitml' / 'mitml.c')}"
SJFAST = f"sjfast.c sha256 {sha_file(HERE / 'sjwit' / 'sjfast.c')}"
PILOT = "research/plan/mitm/mitm.c (pilot kernel)"


def jsonl(p):
    p = Path(p)
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def counts():
    """Latest complete count per (id, w), laptop and Zaratan."""
    out = {}
    for f in [HERE / "data" / "counts.jsonl", HERE / "data" / "validation.jsonl",
              HERE / "data" / "zaratan" / "data" / "counts.jsonl", HERE / "data" / "zaratan" / "data" / "validation.jsonl"]:
        for r in jsonl(f):
            if r.get("harmful") is not None:
                out.setdefault((r["id"], r["w"]), []).append(r)
    return out


def main():
    res = []
    C = counts()

    def row(rid):
        return M.load_row(rid)

    def add(rid, kind, result, evidence, tools, status, witness=None, run_seconds=None, job_ids=None, note=None):
        r = row(rid)
        rec = {"key": r.get("label") or r["sha256"], "label": r.get("label"), "sha256": r["sha256"], "n": r["n"],
               "k": r["k"], "kind": kind, "result": result, "evidence": evidence, "tools": tools,
               "run_seconds": run_seconds, "job_ids": job_ids or [], "witness": witness, "status": status, "note": note}
        if witness is not None:
            rec["witness_recheck"] = M.check_witness(r, witness)
            assert rec["witness_recheck"]["faultcore_harmful"] and rec["witness_recheck"]["literal_harmful"]
        res.append(rec)

    # ---- distances
    pil = {(r["label"], r["w"]): r for r in jsonl(PLAN / "mitm_runs.jsonl")}
    tp = {r["label"]: r for r in jsonl(PLAN / "pilots.jsonl") if r.get("tag") == "direct"}
    for lab, wit in [("935.89.6.a", [0, 28, 165, 175, 254, 282, 927]), ("936.88.6.a", [0, 3, 117, 120, 448, 502, 934])]:
        secs = sum(pil[(lab, w)]["seconds"] for w in range(1, 8))
        trop = ("tropidist threshold 6 exhausted over all anchors (research/plan/data/pilots.jsonl, one thread, "
                f"{tp[lab]['search_seconds']} s)") if lab in tp else \
            "tropidist threshold 6 exhausted (research/tropidist/ pass o3, lower bound 7)"
        add(lab, "distance", {"d": 7, "exact": True},
            [f"{PILOT}: weights 1 to 6 swept clean (research/plan/data/mitm_runs.jsonl, laptop, one thread)",
             trop, "weight-7 fault from the pilot kernel"],
            [f"{PILOT}, 1 thread", f"{TROPIDIST}, 1 thread", CATALOGUE], "exact (two tools)", wit, round(secs, 1),
            note="both tools ran before this round; this round re-checked the fault and assembled the record")
    sweeps = [r for r in jsonl(HERE / "data" / "mitml_runs.jsonl") if r.get("tag") == "sweep-988"]
    assert sorted(r["w"] for r in sweeps) == [1, 2, 3, 4, 5, 6] and all(r["status"] == "clean" and r["accepted"] == 0 for r in sweeps)
    add("988.36.6.a", "distance", {"d": 7, "exact": True},
        [f"{MITML}: weights 1 to 6 swept clean in count mode, no accepted fault at all (laptop, one thread)",
         "tropidist threshold 6 exhausted (research/tropidist/, pass o3)", "weight-7 fault from tropidist (first round)"],
        [f"{MITML}, 1 thread", f"{TROPIDIST}, 1 thread", CATALOGUE], "exact (two tools)", [0, 1, 2, 3, 4, 5, 6],
        round(sum(r["wall_seconds"] for r in sweeps), 1))
    sweeps = [r for r in jsonl(HERE / "data" / "mitml_runs.jsonl") if r.get("tag") == "sweep-998"]
    assert sorted(r["w"] for r in sweeps) == [1, 2, 3, 4, 5, 6] and all(r["status"] == "clean" for r in sweeps)
    z998 = [r for r in C.get(("998.26.6.a", 7), []) if r["harmful"] == 0]
    w998 = json.loads((HERE / "data" / "witness_998.json").read_text())
    ev = [f"{MITML}: weights 1 to 6 swept clean in count mode (laptop)",
          "tropidist threshold 7 exhausted over all anchors (first round, Zaratan, 64 threads, 175 s)",
          f"weight-8 fault from {MITML} in status mode (third of 2,048 partitions, laptop, 6.6 s)"]
    if z998:
        ev.insert(1, f"{MITML}: weight 7 swept clean (Zaratan, {z998[-1]['slices']} slices)")
        add("998.26.6.a", "distance", {"d": 8, "exact": True}, ev, [MITML, TROPIDIST, CATALOGUE],
            "exact (two tools)", w998["witness"])
    else:
        add("998.26.6.a", "distance", {"d": 8, "exact": True}, ev, [MITML, TROPIDIST, CATALOGUE],
            "exact; the floor at weight 7 rests on tropidist alone (the kernel's weight-7 sweep is job j1)",
            w998["witness"])
    dp = [r for r in jsonl(HERE / "data" / "dp_perm.jsonl") if r["label"] == "599.1.6.a.ord" and r.get("lower_bound") == 15]
    if dp:
        r599 = row("599.1.6.a")
        rec = json.loads((HERE / "data" / "dp_records" / "599.1.6.a.ord.json").read_text())
        dpn = json.loads(rec["notes"])["dp"]["main"]
        add("599.1.6.a", "distance", {"d": 15, "exact": True},
            [f"{TROPIDIST}: dense rank DP, value {dpn['value']}, on the columns in the order data/orders/599.1.6.a.json "
             f"(cut rank {dpn['cut_rank']}, against 39 for the best order tropidist finds itself); DP {dpn['seconds']} s, "
             f"peak {dp[-1]['peak_group_rss_mb']} MB, laptop, one thread, config {dp[-1]['config']}",
             "the doubling theorem of Jain and Albert (arXiv:2408.12752) gives d >= 15 (the row's d_certified)",
             "stored weight-15 witness (d_witness), re-checked"],
            [f"{TROPIDIST}, 1 thread", "doubled_order.py", CATALOGUE], "exact (two tools)", r599["d_witness"],
            dp[-1]["wall_seconds"])
    trz = {r["label"]: r for f in [HERE / "data" / "tropidist_runs.jsonl", HERE / "data" / "zaratan" / "data" / "tropidist_runs.jsonl"]
           for r in jsonl(f) if r.get("K") == 6 and r.get("status") == "exhausted"}
    for rid, wit in [("931.93.7.83a91c80c5", [0, 27, 46, 119, 161, 512, 627]), ("932.92.7.0f5a3a3102", [0, 51, 131, 442, 681, 707, 848])]:
        sw = [r for r in jsonl(HERE / "data" / "mitml_runs.jsonl") if r["id"] == rid and r.get("tag") == "sweep-lift"]
        assert sorted(r["w"] for r in sw) == [1, 2, 3, 4, 5, 6] and all(r["accepted"] == 0 for r in sw)
        ev = ["research/search/lift/mitm/mitm.c (the lift search's copy of the pilot kernel): weights 1 to 6 clean (lift REPORT)",
              f"{MITML}: weights 1 to 6 clean in count mode, no accepted fault at all (laptop)",
              "weight-7 fault from the lift search, re-checked"]
        if rid in trz:
            ev.insert(2, f"tropidist threshold 6 exhausted over all anchors (Zaratan, {trz[rid].get('threads')} threads, "
                         f"{trz[rid]['search_seconds']} s)")
            st = "exact (two tools)"
        else:
            st = "exact; floor 7 by two implementations of the meet-in-the-middle sweep, tropidist pending (job j2)"
        add(rid, "distance", {"d": 7, "exact": True}, ev, [PILOT, MITML] + ([TROPIDIST] if rid in trz else []), st, wit)
    for rid in ["177.1.7.a", "185.1.7.a", "189.1.7.a"]:
        fl = [r for r in jsonl(HERE / "data" / "counts.jsonl") if r["id"] == rid and r.get("tag") == "laptop-floor"]
        assert sorted(r["w"] for r in fl) == list(range(1, 9)) and all(r["harmful"] == 0 for r in fl)
        add(rid, "distance", {"d": 9, "exact": True, "already_exact_in_catalogue": False},
            [f"{MITML}: weights 1 to 8 swept clean (count mode, laptop)", "weight-9 faults counted below",
             "agrees with tropidist's dense DP, the independent trellis and the doubling theorem (research/tropidist/)"],
            [f"{MITML}, 1 thread"], "exact (third tool)", None, round(sum(r["wall_seconds"] for r in fl), 1))
    mw = json.loads((HERE / "data" / "macwilliams_511.json").read_text())
    add("511.9.6.a", "distance", {"d": 7, "exact": True},
        ["MacWilliams identity on the 27 independent check rows (catalogue errorcoeff.span_weights and dual_count): "
         "no accepted fault of weight 1 to 6 at all, so d >= 7 without any search",
         "earlier: tropidist search to 6, its dense DP 7, the independent trellis 7, stored weight-7 witness"],
        ["catalogue errorcoeff at dadb221"], "exact (new independent floor)", None,
        note=f"B_w(ker C) = {mw['B_w_kerC_macwilliams']}")
    # ---- A_d
    pilotA = {r["label"]: r for r in json.loads((PLAN / "A_d_counts.json").read_text())["rows"]}
    lead = {}
    for (rid, w), recs in C.items():
        if recs[-1]["harmful"] > 0 and (rid not in lead or w < lead[rid]):
            lead[rid] = w
    TR = {}
    for t in jsonl(HERE / "data" / "trellis_counts.jsonl"):
        TR.setdefault(t["id"], []).append(t)
    for rid, ts in TR.items():
        vals = {tuple(t["A"]) for t in ts}
        assert len(vals) == 1, (rid, vals)
    TRELLIS = f"trellis/trellis_count.py + .c sha256 {sha_file(HERE / 'trellis' / 'trellis_count.c')} (counting syndrome trellis)"
    for rid, w in sorted(lead.items()):
        recs = C[(rid, w)]
        r = recs[-1]
        vals = {(x["harmful"], x["accepted"]) for x in recs}
        assert len(vals) == 1, (rid, w, vals)
        ev = [f"{MITML}: count of every accepted weight-{w} set; {r['slices']} slice(s) summed before the division"]
        tools = [f"{MITML}, {r.get('jobs', 1)} process(es)"]
        if rid in pilotA:
            assert (pilotA[rid]["A_d"], pilotA[rid]["accepted"]) == (r["harmful"], r["accepted"])
            ev.append(f"equals the pilot kernel's count ({PILOT}, research/plan/data/A_d_counts.json)")
            tools.append(PILOT)
        if rid == "511.9.6.a":
            assert mw["B_w_kerC_macwilliams"]["7"] == r["accepted"]
            ev.append("the accepted count equals the MacWilliams count of the check code")
        if rid in ("1675.373.3.a", "1676.372.3.a"):
            mw4 = json.loads((HERE / "data" / "macwilliams_d4.json").read_text())[rid]
            assert mw4["B_w_kerC_macwilliams"]["4"] == r["accepted"]
            ev.append("the accepted count equals the MacWilliams count of the check code")
        if rid in TR:
            A = TR[rid][0]["A"]
            assert A[w] == r["harmful"] and all(x == 0 for x in A[:w]), (rid, A, r["harmful"])
            ev.append(f"equals the counting trellis (B_w(ker H) - B_w(ker [H;L]), {len(TR[rid])} column order(s)), "
                      f"which also finds A_w = 0 below w = {w}")
            tools.append(TRELLIS)
        if rid == "512.39.6.a":
            fl = json.loads((HERE / "data" / "flat512.json").read_text())
            assert fl["harmful_flats"] == r["harmful"]
            ev.append("equals the literal count over all 50,434,240 affine 3-flats (flat512.py)")
        add(rid, "A_d", {"w": w, "A_w": r["harmful"], "accepted": r["accepted"]}, ev, tools, "exact count",
            run_seconds=r.get("wall_seconds") or sum(r.get("slice_seconds", [])), job_ids=[r.get("job")] if r.get("job") else [])
    for rid, ts in sorted(TR.items()):
        if rid in lead:
            continue
        A = ts[0]["A"]
        w = next(i for i, x in enumerate(A) if x)
        r0 = row(rid)
        add(rid, "A_d", {"w": w, "A_w": A[w], "accepted": ts[0]["B_kerH"][w], "harmless": ts[0]["B_kerG"][w]},
            [f"counting trellis, B_w(ker H) - B_w(ker [H;L]) for every w <= {ts[0]['W']}, in {len(ts)} column orders "
             f"(cut ranks {sorted({t['maxcut_H'] for t in ts})}), all agreeing; A_w = 0 for w < {w}"],
            [TRELLIS], "exact count (one method, two orders)" if len(ts) > 1 else "exact count (one method)",
            run_seconds=round(sum(sum(t['seconds_H']) + sum(t['seconds_G']) for t in ts), 1))
        add(rid, "distance", {"d": w, "exact": True},
            [f"counting trellis: no harmful fault of weight below {w}, and {A[w]} of weight {w}",
             "agrees with tropidist's DP, the independent trellis of research/tropidist/ and the doubling theorem"],
            [TRELLIS], "exact (additional method)", r0.get("d_witness"))
    if not any(x["key"] == "512.39.6.a" and x["kind"] == "A_d" for x in res):
        fl = json.loads((HERE / "data" / "flat512.json").read_text())
        add("512.39.6.a", "A_d", {"w": 8, "A_w": fl["harmful_flats"], "accepted": fl["accepted_flats"]},
            ["literal count over all 788,035 three-dimensional subspaces and their 64 cosets (flat512.py): every 3-flat "
             "is accepted, 50,397,952 flip an output; with the minimum-weight theorem for RM(6,9) this is A_8",
             "equals the parents search's kernel count (64 slices) and its Plücker count (research/search/parents/REPORT.md §2)"],
            ["flat512.py (numpy)", CATALOGUE], "exact count (third method)", run_seconds=fl["seconds"])
    with open(HERE / "results.jsonl", "w") as f:
        for r in res:
            f.write(json.dumps(r) + "\n")
    print(len(res), "results")
    for r in res:
        print(r["key"][:20], r["kind"], json.dumps(r["result"]), r["status"])


if __name__ == "__main__":
    main()
