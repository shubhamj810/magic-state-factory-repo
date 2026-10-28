#!/usr/bin/env python3
"""One-off migration: merge the larger unified borrowed-identity search.

    python master_catalog/migrations/borrowed_identities_large_unified_2026_10_28.py [--dry-run]

On 27 and 28 October 2026 the Borrowed Identities repository (S. Singh, C.
Gidney and C. Jones, arXiv:2606.28518) ran its unified search's two-group and
gluing stages up to ``k = 12`` outputs and ``N = 18`` circuit wires.
`borrowed_identities/export_large_unified.py` rebuilt and checked every
distance-2 row of its level-3 table and wrote them to
``borrowed_identities/circuits/large_unified_l3.json``: each two-group row as
the construction that builds it, each gluing row as its gates.

This turns each entry into a merge record and merges them through
`merge_results.merge`, the same bar as every merge.  A gluing circuit and a
two-group circuit of at most `STORE_MAX_N` inputs are given as columns, the
construction's expanded here, and land in ``master_catalog.json``.  A longer
two-group circuit is given as its construction and lands in
``master_catalog_large.json``, as the large sweep's did.

Credit: a class the merge adds is credited to the paper.  A held class keeps
exactly the credit it had, the rule of the October 26 import: the merge would
append the paper to it, and this migration puts the old list back.  The
classes held at distance 2 already cite the paper or an earlier work, except
the nine only the symmetry-SAT search found, which keep the symmetry-and-AI
report by the owner's decision; the run reports any of those it meets.
Re-running it changes nothing.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOGUE = HERE.parent
REPO = CATALOGUE.parent
sys.path.insert(0, str(CATALOGUE))

import catalogfile as CF                                          # noqa: E402
import constructions as K                                         # noqa: E402
import merge_results as MR                                        # noqa: E402
import verify_catalog as VC                                       # noqa: E402

CIRCUITS = "borrowed_identities/circuits/large_unified_l3.json"
BORROWED = "singh2026borrowed"
SYMMETRY = "jain2026symmetry"
#: The longest two-group circuit stored as columns; longer ones are stored as
#: their construction.  The October 26 import stored columns up to 4,095
#: inputs.  This table has 740 distance-2 two-group rows that short, 15 MB of
#: columns if every one were new, which would take ``master_catalog.json``
#: from 43 MB to about 58 MB, past GitHub's recommended 50 MB; up to 1,023
#: inputs it is 471 rows and 3 MB at most.
STORE_MAX_N = 1023
REGIMES = {"two-group": "borrowed-identity search: two-group",
           "gluing": "borrowed-identity search: symmetry-free"}
REPOSITORY = "https://github.com/shraggy/Magic_state_factory_search"


def records(path=REPO / CIRCUITS):
    """The merge record of every entry of the circuit file, in its order."""
    blob = json.loads(Path(path).read_text(encoding="utf-8"))
    commit = blob["source"]["commit"][:7]
    out = []
    for e in blob["circuits"]:
        record = {"k": e["k"], "N": e["wires"], "n": e["n"], "d": e["d"]}
        if e["stage"] == "gluing":
            record["columns"] = [S for S, c in e["gates"] if c % 2]
        elif e["n"] <= STORE_MAX_N:
            columns = K.columns(e["construction"])
            if K.digest(columns) != e["columns_sha256"]:
                raise SystemExit(f"{e['id']}: the construction does not build "
                                 f"the columns the circuit file pins")
            record["columns"] = columns
        else:
            record["construction"] = e["construction"]
        record.update({
            "regime": REGIMES[e["stage"]],
            "discovery": "pre-existing",
            "citations": [BORROWED],
            "file": CIRCUITS,
            "label": e["id"],
            "provenance": f"larger unified search l=3, {e['stage']} "
                          f"{e['params']}",
            "origin": f"{REPOSITORY} at {commit}, "
                      f"outputs/{e['table']} line {e['line']}",
        })
        out.append(record)
    return out


def _changes(payload):
    """Whether writing ``payload`` would change any of the three files."""
    real = (CF.CATALOG_JSON, CF.CATALOG_LARGE_JSON, CF.CATALOG_MD)
    with tempfile.TemporaryDirectory() as scratch:
        trial = [Path(scratch) / path.name for path in real]
        if real[1].exists():
            # `write_all` rewrites an existing large file even with no rows to
            # put in it, so the trial must start with one too
            trial[1].write_text("", encoding="utf-8")
        CF.write_all(payload, *trial)
        return any((path.read_text(encoding="utf-8") if path.exists() else None)
                   != (out.read_text(encoding="utf-8") if out.exists() else None)
                   for path, out in zip(real, trial))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load_all()
    before = len(payload["factories"])
    credit = {row["catalog_label"]: list(row["citations"])
              for row in payload["factories"]}
    batch = records()
    verdicts = MR.merge(payload, batch, CIRCUITS)
    restored = 0
    for row in payload["factories"]:
        old = credit.get(row["catalog_label"])
        if old is not None:
            restored += row["citations"] != old
            row["citations"] = old
    met = sorted({row["catalog_label"] for _i, verdict, row, _d in verdicts
                  if verdict in ("duplicate", "improved")
                  and row["citations"] == [SYMMETRY]})
    tally = collections.Counter(verdict for _i, verdict, _row, _d in verdicts)
    reasons = collections.Counter(kind for _i, verdict, _row, problems in verdicts
                                  if verdict == "rejected"
                                  for kind, _detail in problems)
    large = sum(1 for row in payload["factories"] if CF.is_large(row))
    print(f"{len(batch)} results: " + ", ".join(
        f"{n} {v}" for v, n in sorted(tally.items()))
        + (f"; refused as {dict(reasons)}" if reasons else "")
        + f"; credit restored on {restored} held row(s)"
        + f"; {before} -> {len(payload['factories'])} classes, {large} of "
          f"them in the large file")
    if met:
        print(f"held classes credited to the symmetry-and-AI report alone "
              f"that this search also finds: {', '.join(met)}")
    for index, verdict, row, detail in verdicts:
        if verdict in ("improved", "rejected"):
            print(f"  {batch[index]['label']}: {verdict} "
                  f"{row['catalog_label'] if row else ''} {detail}")
    residue = (VC.duplicate_class_problems(payload["factories"])
               + VC.duplicate_label_problems(payload["factories"])
               + VC.provenance_problems(payload)
               + VC.citation_problems(payload)
               + VC.header_problems(payload))
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("the merged catalogue fails a file-level check; "
                         "nothing written")
    if args.dry_run or not _changes(payload):
        print("nothing written" + (": dry run" if args.dry_run else ""))
        return 0
    CF.write_all(payload)
    VC.persist_metric_cache()
    problems = VC.large_file_problems(CF.CATALOG_LARGE_JSON)
    if problems:
        raise SystemExit(f"the large file written fails its own check: "
                         f"{problems}")
    print("wrote master_catalog.json, master_catalog_large.json and "
          "MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
