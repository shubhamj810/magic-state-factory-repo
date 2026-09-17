#!/usr/bin/env python3
"""One-off migration: the n <= 38 classification and the rank-7 census moved to
``classification/legacy/``.

    python master_catalog/migrations/legacy_paths_2026_09_17.py [--dry-run]

Run after the two directories have been moved (``git mv``).  Running it again
finds nothing to rewrite and writes nothing.

The exhaustive classification of generalised triorthogonal protocols through
length 54 (Wills, Jain and Singh) subsumes the repository's own exhaustive
``n <= 38`` classification and ``r <= 7`` census, so those two directories were
demoted from ``classification/exhaustive_n38/`` and
``classification/rank7_census/`` to ``classification/legacy/exhaustive_n38/``
and ``classification/legacy/rank7_census/``.  They were kept, not deleted,
partly because this catalogue cites them: the ``sources`` of its rows name
their catalogue files (``classification_n38.json``, ``census_r7.json``,
``sk_classes_r7.json``), and
`tests/test_master_catalog.test_source_attribution_is_real` follows every such
citation into the file it names.  After the move those citations point at
nothing.

This script rewrites the two path PREFIXES, and nothing else, wherever they
occur in a string anywhere in a row -- ``sources[].file`` is where they are
today, but ``provenance``, ``notes`` and every other string field are searched
too, so a prose mention would be carried along rather than left stale.  No
circuit field, gate, distance, regime, label or citation changes: the classes
the citations name are the same rows of the same files, now at a new path.

Before anything is written it checks that

* the payload differs from the file on disk ONLY by those prefix rewrites
  (every other value compared exactly, string for string);
* no string anywhere in the payload -- header included -- still carries an old
  prefix;
* every rewritten ``file`` exists and writes the label its source cites, which
  is the check `test_source_attribution_is_real` makes;
* `verify_catalog`'s provenance, citation and header checks still pass.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOGUE = HERE.parent
REPO = CATALOGUE.parent
sys.path.insert(0, str(CATALOGUE))

import catalogfile as CF                                          # noqa: E402
import verify_catalog as VC                                       # noqa: E402

MOVED = (("classification/exhaustive_n38/", "classification/legacy/exhaustive_n38/"),
         ("classification/rank7_census/", "classification/legacy/rank7_census/"))
#: The keys a classification catalogue names a gate under; the same list
#: `test_source_attribution_is_real` accepts a label from.
LABEL_KEYS = ("label", "gate_human", "gate", "gate_named", "output_gate")


def moved(text):
    """``text`` with every old prefix replaced by its new one."""
    for old, new in MOVED:
        text = text.replace(old, new)
    return text


def rewrite(value, where, changes):
    """``value`` with every string rewritten; each change is appended to ``changes``."""
    if isinstance(value, str):
        new = moved(value)
        if new != value:
            changes.append((where, value, new))
        return new
    if isinstance(value, list):
        return [rewrite(v, f"{where}[{i}]", changes) for i, v in enumerate(value)]
    if isinstance(value, dict):
        return {k: rewrite(v, f"{where}.{k}", changes) for k, v in value.items()}
    return value


def unexplained_differences(before, after, where="payload"):
    """Every place ``after`` differs from ``before`` other than by a prefix rewrite."""
    if isinstance(before, str) and isinstance(after, str):
        return [] if after in (before, moved(before)) else [where]
    if type(before) is not type(after):
        return [where]
    if isinstance(before, list):
        if len(before) != len(after):
            return [where]
        return [d for i, (b, a) in enumerate(zip(before, after))
                for d in unexplained_differences(b, a, f"{where}[{i}]")]
    if isinstance(before, dict):
        if list(before) != list(after):
            return [where]
        return [d for k in before
                for d in unexplained_differences(before[k], after[k], f"{where}.{k}")]
    return [] if before == after else [where]


def stale_strings(value, where="payload"):
    """Every string that still carries an old prefix."""
    if isinstance(value, str):
        return [where] if any(old in value for old, _ in MOVED) else []
    if isinstance(value, list):
        return [s for i, v in enumerate(value) for s in stale_strings(v, f"{where}[{i}]")]
    if isinstance(value, dict):
        return [s for k, v in value.items() for s in stale_strings(v, f"{where}.{k}")]
    return []


def citation_residue(payload):
    """Rewritten ``file`` citations that do not resolve to their label."""
    labels, problems = {}, []
    for index, row in enumerate(payload["factories"], 1):
        for source in row["sources"]:
            path = source.get("file") or ""
            if not path.startswith(tuple(new for _, new in MOVED)):
                continue
            if path not in labels:
                target = REPO / path
                if not target.is_file():
                    labels[path] = None
                else:
                    blob = json.loads(target.read_text(encoding="utf-8"))
                    rows = blob["factories"] if isinstance(blob, dict) else blob
                    labels[path] = {r[key] for r in rows for key in LABEL_KEYS if r.get(key)}
            if labels[path] is None:
                problems.append(("citation-file", f"row {index} cites {path}, "
                                                  f"which does not exist"))
            elif source.get("label") not in labels[path]:
                problems.append(("citation-label", f"row {index} cites "
                                                   f"{source.get('label')!r}, which "
                                                   f"{path} does not write"))
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    for old, new in MOVED:
        if (REPO / old).exists() or not (REPO / new).is_dir():
            raise SystemExit(f"{old} has not been moved to {new}; move it first")
    before = CF.load()
    changes = []
    rows = [rewrite(row, f"factories[{i}]", changes)
            for i, row in enumerate(before["factories"])]
    payload = {**before, "factories": rows}
    by_field = {}
    for where, _old, _new in changes:
        field = ".".join(part.split("[")[0] for part in where.split(".")[1:])
        by_field[field] = by_field.get(field, 0) + 1
    touched = len({where.split(".")[0] for where, _, _ in changes})
    print(f"{len(changes)} strings rewritten in {touched} of {len(rows)} rows "
          f"({', '.join(f'{n} in {f}' for f, n in sorted(by_field.items())) or 'none'})")
    if not changes:
        print("nothing to rewrite: already applied; nothing written")
        return 0
    residue = ([("unexplained-difference", w)
                for w in unexplained_differences(before, payload)]
               + [("stale-path", w) for w in stale_strings(payload)]
               + citation_residue(payload)
               + VC.provenance_problems(payload) + VC.citation_problems(payload)
               + VC.header_problems(payload))
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("the rewrite would leave the catalogue inconsistent; "
                         "nothing written")
    if args.dry_run:
        print("dry run: nothing written")
        return 0
    CF.write(payload)
    print("wrote master_catalog.json and MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
