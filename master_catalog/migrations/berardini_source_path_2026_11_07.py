#!/usr/bin/env python3
"""One-off migration: the two Berardini rows name their source file by its path.

    python master_catalog/migrations/berardini_source_path_2026_11_07.py [--dry-run]

The import of 737.1.17.a and 753.1.17.a on 2026-11-07 wrote their source's
``file`` as ``transversal_t_codes/berardini_factories.json (built by
transversal_t_codes/berardini.py)``.  A source in a folder of this repository
must name a file that exists, and `tests/test_master_catalog.py` opens it to
find the source's label.  This script sets ``file`` to the path alone and adds
"built by transversal_t_codes/berardini.py" to the source's ``provenance``.
It checks that the file holds a circuit under the source's label with the
row's columns, and that the changed rows pass `verify_catalog.verify_row` and
the file-level checks, before anything is written.  Idempotent.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import catalogfile as CF                                          # noqa: E402
import distance_policy_2026_11_07 as DP                           # noqa: E402
import verify_catalog as VC                                       # noqa: E402

PATH = "transversal_t_codes/berardini_factories.json"
OLD = f"{PATH} (built by transversal_t_codes/berardini.py)"
NOTE = "built by transversal_t_codes/berardini.py"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    built = {f["label"]: f for f in json.loads((REPO / PATH).read_text())}
    payload = CF.load_all()
    changed = []
    for row in payload["factories"]:
        for source in row["sources"]:
            if source["file"] != OLD:
                continue
            circuit = built.get(source["label"])
            if circuit is None or circuit["columns"] != row["columns"]:
                raise SystemExit(f"{row['catalog_label']}: {PATH} does not hold "
                                 f"{source['label']} with the row's columns")
            source["file"] = PATH
            source["provenance"] = f"{source['provenance']}; {NOTE}"
            changed.append(row)
    for row in changed:
        _facts, problems = VC.verify_row(row)
        print(f"  {row['catalog_label']}: source file {PATH}"
              + (f": {problems}" if problems else ""))
        if problems:
            raise SystemExit("a changed row fails verification; nothing written")
    residue = (VC.duplicate_class_problems(payload["factories"])
               + VC.duplicate_label_problems(payload["factories"])
               + VC.provenance_problems(payload) + VC.citation_problems(payload)
               + VC.header_problems(payload))
    if residue:
        raise SystemExit(f"the catalogue fails a file-level check: {residue}")
    print(f"{len(changed)} row(s) changed")
    if args.dry_run or not DP._changes(payload):
        print("nothing written" + (": dry run" if args.dry_run else ""))
        return 0
    CF.write_all(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
