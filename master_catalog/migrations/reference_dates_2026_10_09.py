#!/usr/bin/env python3
"""One-off migration: date every reference, and correct the Jones (2013) entry.

    python master_catalog/migrations/reference_dates_2026_10_09.py [--dry-run]

The reference lists -- `MASTER_CATALOG.md` and the website's References page
-- are in order of publication, which the year in a label cannot settle within
a year.  Each entry gets a ``date``: the publication date Crossref records for a
journal article (looked up by DOI on 2026-10-09), and the arXiv v1 date for a
preprint.  For the two 2013 Toffoli papers the two orders differ: Jones's
article appeared first (20 February against 18 March), Eastin's preprint first
(arXiv:1212.4872, a day before 1212.5069).  The list follows publication.

The same lookup showed the Jones entry wrong: Phys. Rev. A 87, 022328 is
"Low-overhead constructions for the fault-tolerant Toffoli gate"; "Novel
constructions for the fault-tolerant Toffoli gate" is only the arXiv preprint's
title.  The entry takes the published title, and its key ``jones2013novel``
becomes ``jones2013low`` on the one row citing it (``8.3.2.a``).  No other row
field changes.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import catalogfile as CF                                          # noqa: E402
import verify_catalog as VC                                       # noqa: E402

#: key -> publication date, and where it comes from.
DATES = {
    "bravyi2005universal": "2005-02-22",       # Crossref, 10.1103/PhysRevA.71.022316
    "bravyi2012magic": "2012-11-27",           # Crossref, 10.1103/PhysRevA.86.052329
    "jones2013low": "2013-02-20",              # Crossref, 10.1103/PhysRevA.87.022328
    "eastin2013distilling": "2013-03-18",      # Crossref, 10.1103/PhysRevA.87.032321
    "campbell2017unified": "2017-02-09",       # Crossref, 10.1103/PhysRevA.95.022316
    "haah2018codes": "2018-06-07",             # Crossref, 10.22331/q-2018-06-07-71
    "rengaswamy2020optimality": "2020-08",     # Crossref, 10.1109/JSAIT.2020.3012914
    "nezami2022classification": "2022-07-28",  # Crossref, 10.1103/PhysRevA.106.012437
    "vuillot2022quantum": "2022-09",           # Crossref, 10.1109/TIT.2022.3170846
    "webster2023transversal": "2023-10-01",    # Crossref, 10.1088/1367-2630/acfc5f
    "shi2024triorthogonal": "2024-07-20",      # Crossref, 10.1007/s11128-024-04485-9
    "gong2024computation": "2024-10-30",       # arXiv:2410.23263 v1
    "jacinto2026exploring": "2026-06-05",      # arXiv:2606.07734 v1
    "singh2026borrowed": "2026-06-26",         # arXiv:2606.28518 v1
    "gong2026magic": "2026-08-10",             # arXiv:2608.09727 v1
    "wills2026classification": "2026-09-25",   # arXiv:2609.30860 v1
    "jain2026symmetry": "2026-10-05",          # arXiv:2610.06535 v1
}

OLD_JONES, JONES = "jones2013novel", "jones2013low"
JONES_ENTRY = {
    "short": "Jones (2013)",
    "full": "C. Jones, \"Low-overhead constructions for the fault-tolerant "
            "Toffoli gate,\" Phys. Rev. A 87, 022328 (2013).",
    "url": "https://doi.org/10.1103/PhysRevA.87.022328",
}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load()
    references = payload["references"]
    said = []

    if OLD_JONES in references:
        # rebuild the map with the new key in the old one's place, so the
        # header's own order -- and the diff -- stays as small as the change
        payload["references"] = references = {
            (JONES if key == OLD_JONES else key):
            (dict(JONES_ENTRY) if key == OLD_JONES else entry)
            for key, entry in references.items()}
        said.append(f"reference {OLD_JONES} -> {JONES}: {JONES_ENTRY['full']}")
    for row in payload["factories"]:
        if OLD_JONES in row["citations"]:
            row["citations"] = [JONES if key == OLD_JONES else key
                                for key in row["citations"]]
            said.append(f"  {row['catalog_label']} now cites {JONES}")

    for key, date in DATES.items():
        if key in references and references[key].get("date") != date:
            references[key]["date"] = date
            said.append(f"date {key}: {date}")
    undated = [key for key, entry in references.items()
               if entry.get("url") and not entry.get("date")]

    for line in said:
        print(line)
    if undated:
        raise SystemExit(f"published references with no date: {undated}")
    residue = (VC.citation_problems(payload) + VC.header_problems(payload)
               + VC.provenance_problems(payload))
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("the catalogue would fail its checks; nothing written")
    print("order: " + ", ".join(CF.reference_order(references)))
    if args.dry_run or not said:
        print("nothing written" + (": dry run" if args.dry_run else ""))
        return 0
    CF.write(payload)
    print("wrote master_catalog.json and MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
