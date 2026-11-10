#!/usr/bin/env python3
"""Write `certificates.json`: distance bounds from theorems whose hypotheses
this repository checks from a circuit's columns.

    python theorem_certificates/assemble.py            # write the file
    python theorem_certificates/assemble.py --check    # compare with it

`inputs.json` lists the circuits, each as a construction object of
`master_catalog/constructions.py` with a name.  For each one this script
finds the columns the catalogue stores (a row whose columns are the
construction's in its build order or in the sorted order of the contract);
for a circuit not yet in the catalogue it takes the sorted order, which is
how the large file stores a construction.  On exactly those columns it runs
the theorem's own check and writes one record, bound to them by the SHA-256
of the columns (`constructions.digest`), with the bound the check proves:

* **San-José's theorem** (`construction_sanjose.hypothesis_check`):
  ``d >= delta - P``, where ``delta`` is the outer code's dual distance and P
  the number of punctured coordinates; the check decodes the binary columns
  back to the outer code and verifies every hypothesis it uses;
* **the CCZ frame theorem** (`construction_rm.packing_check` on the family of
  sets, then `construction_rm.frame_check` on the columns): ``d = 2^q``
  exactly, with the fault of the theorem's proof as the witness.

A record carries the fault the research found at the bound where there is
one, re-checked here with `faultcore.Circuit.harmful` and by the XOR of the
wire masks.  Nothing is written if any check fails.
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

import catalogfile as CF                                          # noqa: E402
import constructions as K                                         # noqa: E402
import construction_rm as RM                                      # noqa: E402
import construction_sanjose as SJ                                 # noqa: E402
import faultcore as FC                                            # noqa: E402

INPUTS = HERE / "inputs.json"
OUT = HERE / "certificates.json"
SANJOSE = ("San-José's distance theorem d >= delta - P, its hypotheses checked "
           "from the columns by master_catalog/construction_sanjose.py "
           "(hypothesis_check)")
FRAME = ("the CCZ frame theorem d = 2^q, its hypotheses checked by "
         "master_catalog/construction_rm.py (packing_check on the sets, "
         "frame_check on the columns)")


def harmful(columns, k, N, witness):
    acc = 0
    for j in witness:
        for q in columns[j]:
            acc ^= 1 << q
    literal = acc != 0 and (acc >> k) == 0
    return literal and len(set(witness)) == len(witness) \
        and FC.Circuit(columns, k, N).harmful(list(witness))


def stored_columns(construction, by_digest):
    """``(columns, label, ordered)``: the columns as the catalogue stores
    the circuit, or sorted; its label or ``None``; the sorted columns."""
    family = construction["family"]
    if family in SJ.FAMILIES:
        native = SJ.build(construction)["columns"]
    elif family == "ccz-frame":
        native = RM.native_columns(construction)
    else:
        native = None
    ordered = K.columns(construction)
    for cols in ([native] if native is not None else []) + [ordered]:
        row = by_digest.get(K.digest(cols))
        if row is not None:
            return cols, row["catalog_label"], ordered
    return ordered, None, ordered


def assemble():
    rows = CF.load_all()["factories"]
    by_digest = {K.digest(row["columns"]): row for row in rows}
    records = []
    for item in json.loads(INPUTS.read_text(encoding="utf-8"))["circuits"]:
        c = item["construction"]
        wrong = K.problems(c)
        if wrong:
            raise AssertionError(f"{item['name']}: {wrong}")
        columns, label, ordered = stored_columns(c, by_digest)
        k, N = c["k"], c["N"]
        if c["family"] in SJ.FAMILIES:
            bound, tool = SJ.hypothesis_check(columns, k, N, c)["bound"], SANJOSE
            if bound != SJ.bound(c):
                raise AssertionError(f"{item['name']}: the check proves {bound}, "
                                     f"the construction says {SJ.bound(c)}")
        elif c["family"] == "ccz-frame":
            wrong = RM.packing_check(c) + RM.frame_check(columns, k, N, c)
            if wrong:
                raise AssertionError(f"{item['name']}: {wrong}")
            bound, tool = 2 ** c["q"], FRAME
        else:
            raise AssertionError(f"{item['name']}: no theorem for {c['family']}")
        witness = item.get("witness")            # indices in the sorted order
        if witness is not None:
            if columns != ordered:
                # the catalogue stores the build order: move the fault there
                where = {tuple(col): i for i, col in enumerate(columns)}
                witness = sorted(where[tuple(ordered[j])] for j in witness)
            if len(witness) != bound or not harmful(columns, k, N, witness):
                raise AssertionError(f"{item['name']}: the fault does not hold")
        records.append({"name": item["name"], "label": label, "n": len(columns),
                        "k": k, "N": N, "columns_sha256": K.digest(columns),
                        "tool": tool, "lower_bound": bound,
                        "exact": witness is not None,
                        **({"witness": witness} if witness is not None else {}),
                        "source": item["source"]})
    return records


def render(blob):
    text = json.dumps(blob, indent=1)
    return re.sub(r"\[\s*\n\s*((?:-?\d+,\s+)*-?\d+)\s+\]",
                  lambda m: "[" + re.sub(r"\s+", " ", m.group(1)) + "]", text) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    records = assemble()
    text = render({
        "about": ("Distance bounds from theorems whose hypotheses this repository "
                  "checks from the columns: San-José's theorem for the GRS and "
                  "curve outer codes, and the CCZ frame theorem. Each record is "
                  "bound to the circuit by columns_sha256 (constructions.digest of "
                  "the columns as the catalogue stores them, or in the sorted order "
                  "of the large file for a circuit not yet in it); label is the "
                  "catalogue row at assembly. lower_bound is what the check "
                  "proves; witness, where present, is a fault of that weight. "
                  "Written by theorem_certificates/assemble.py from inputs.json."),
        "method": "theorem",
        "records": records,
    })
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            raise SystemExit("out of date: certificates.json")
        print("certificates.json is up to date")
        return 0
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {len(records)} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
