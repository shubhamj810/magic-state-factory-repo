#!/usr/bin/env python3
"""Collect every count made here into data/results.json, one entry per catalogue row with
127 <= n < 500 and A_d null (data/rows_summary.json), and print a table.

Sources: data/counts.jsonl and data/zaratan/counts.jsonl (code/acount.py: mitml and the plan kernel),
data/macw.jsonl and data/zaratan/macw.jsonl (MacWilliams), data/trellis.jsonl (counting trellis),
data/dblspec/*.json through code/dblformula.py (the doubling count), research/search2/catalogue/stage3
(the earlier mitml + mydist records of 348, 452 and 470), data/contraction.jsonl (the contraction
identity), data/zaratan/tropidist.jsonl.  A count is "accepted" when two programs that share no code
agree on the row itself; "theorem" when it rests on the doubling count with checked ingredients.
"""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
TOP = HERE.parent
sys.path.insert(0, str(HERE))
import dblformula as DF                                              # noqa: E402


def jl(path):
    p = TOP / path
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


rows = json.loads((TOP / "data" / "rows_summary.json").read_text())
progs = {}


def add(label, w, name, value, src, extra=None):
    progs.setdefault((label, w), []).append({"program": name, "A_w": value, "record": src, **(extra or {})})


for src in ("data/counts.jsonl", "data/zaratan/counts.jsonl", "data/zaratan/counts_t6_recovered.jsonl"):
    for r in jl(src):
        if "mitml" in r:
            add(r["label"], r["weight"], "mitml (" + r["mitml"]["mode"] + ")", r["mitml"]["harmful"], src,
                {"accepted": r["mitml"]["accepted"]})
        if "plan" in r:
            add(r["label"], r["weight"], "plan kernel", r["plan"]["harmful"], src, {"accepted": r["plan"]["accepted"]})
for src in ("data/macw.jsonl", "data/zaratan/macw.jsonl"):
    for r in jl(src):
        if r["keep_out"] == list(range(len(r["keep_out"]))) and ".keep" not in r["label"]:
            add(r["label"], r["weight"], "MacWilliams (wdist.c)", r["A_w"], src)
for r in jl("data/trellis.jsonl"):
    add(r["label"], r["W"], "counting trellis", r["A"][r["W"]], "data/trellis.jsonl", {"order": r["order"]})
for spec in sorted((TOP / "data" / "dblspec").glob("*.json")):
    s = json.loads(spec.read_text())
    blocks = [(b["n_b"], {int(j): c for j, c in b["W"].items()}, b["label"]) for b in s["blocks"]]
    inner = {(int(a), int(b)): c for a, b, c in s["inner"]}
    w = max(s["weights"])
    tot, _ = DF.a_w(blocks, s["k"], w, inner, s["d_t"])
    add(s["name"], w, "doubling count (theorem)", tot, str(spec.relative_to(TOP)))
STAGE3 = TOP.parent / "catalogue" / "stage3" / "data" / "lists" / "listed_counts.jsonl"
for l in STAGE3.read_text().splitlines():
    r = json.loads(l)
    lab = r["name"].split(".", 1)[1]
    add(lab, r["weight"], "mitml (list), 8 Nov", r["mitml"]["harmful"], "research/search2/catalogue/stage3/data/lists/listed_counts.jsonl")
    add(lab, r["weight"], "mydist, 8 Nov", r["mydist"]["harmful"], "research/search2/catalogue/stage3/data/lists/listed_counts.jsonl")
for r in jl("data/contraction.jsonl"):
    add(r["label"], r["weight"], "contraction identity (theorem)", r["A_w"], "data/contraction.jsonl")
tro = {}
for r in jl("data/zaratan/tropidist.jsonl"):
    if r.get("anchors") == "all":
        tro.setdefault(r["label"], {})[r["K"]] = r["status"]

out = []
for row in rows:
    lab, d = row["label"], row["d"]
    ps = progs.get((lab, d), [])
    vals = {p["A_w"] for p in ps}
    direct = {p["program"].split(" (")[0].split(",")[0] for p in ps if "theorem" not in p["program"]}
    if len(vals) > 1:
        status, A = "DISAGREE", None
    elif not ps:
        status, A = "not counted", None
    elif len(direct) >= 2:
        status, A = "accepted (two programs)", ps[0]["A_w"]
    elif any("theorem" in p["program"] for p in ps):
        status, A = ("theorem + one program" if direct else "theorem only"), ps[0]["A_w"]
    else:
        status, A = "one program", ps[0]["A_w"]
    out.append({**{k: row[k] for k in ("label", "n", "k", "N", "d")}, "columns_sha256": row["sha"], "A_d": A,
                "status": status, "programs": ps, "tropidist": tro.get(lab)})
(TOP / "data" / "results.json").write_text(json.dumps(out, indent=1))
for e in out:
    print(f"{e['label']:12} d={e['d']:2} A_d={str(e['A_d']):>14}  {e['status']:28} "
          + ", ".join(sorted({p['program'] for p in e['programs']})))
