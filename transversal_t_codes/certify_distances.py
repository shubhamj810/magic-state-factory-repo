#!/usr/bin/env python3
"""The doubling theorem's distance bounds, for the codes whose hypotheses this
folder checks: writes `distance_certificates.json`.

    python transversal_t_codes/certify_distances.py           # write the file
    python transversal_t_codes/certify_distances.py --check   # compare with it

The doubling theorem of Jain and Albert (arXiv:2408.12752, Sec. III) gives
``d >= min(d_sd, d_tri + 2)`` for a self-dual input of distance ``d_sd`` doubled
onto a triorthogonal code of distance ``d_tri``.  The chain starts at one qubit
(``d = 1``), and every code gets a record.

The self-dual distances this folder proves are `PROVED`: by enumerating every
word, or by the Brouwer-Zimmermann bound of `min_distance.py`, each in a named
test of `tests/test_transversal_t_codes.py`.  A record whose chain uses only
these has the tool `TOOL`.

The quantum QR code of length 167 is proved here too: the C walk of
`bz_bound.c` (driven by `min_distance.py --qr 167`) listed every word of the
extended QR code [168,84] with at most 10 ones on one information set and 9
on the other, 3.6e12 sums of rows in 3,559 s on two threads, and the lightest
weighs 24, so its minimum distance is 24 (`xqr168_distance.json`).

The quantum QR codes of length 191 and 199 are in `FROM_PAPER`: their
distances rest on the minimum distances 28 and 32 of the extended QR codes of
length 192 and 200, as the paper's Table II states them.  This folder does
not re-prove those (the same bound would need about 8e14 and 6e16 sums of
rows).  The owner's decision of 2026-11-07 counts the
Table II distances as sure, so a code whose chain uses one gets a record too,
with the tool `TOOL_WITH_PAPER` and the Table II distances it rests on listed
in ``rests_on_paper`` and what this folder proves for it in ``proved_here``.
Every other input along its chain is proved here.

The proof of the bound itself, for the factory distance used here (accepted
by every check row, odd overlap with the all-ones logical row): split a fault
into ``(a, b, c)`` over the two self-dual blocks and the triorthogonal block.
The checks force ``a + b`` into ``ker C_sd`` and ``c`` into ``ker C_tri``, and
the row ``[0 1 1]`` makes ``|b| + |c|`` even, so ``|a|`` is odd.  If ``|b|`` is
even, ``a + b`` is an odd word of ``ker C_sd`` and weighs at least ``d_sd``.  If
``|b|`` is odd, ``|c|`` is odd, so ``c`` is a logical fault of the inner code
and weighs at least ``d_tri``, while ``|a|`` and ``|b|`` are each at least 1.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "master_catalog"))

import build_codes as B                                           # noqa: E402
import constructions as K                                         # noqa: E402

CERTIFICATES_JSON = HERE / "distance_certificates.json"
TEST_FILE = "transversal_t_codes/tests/test_transversal_t_codes.py"
TOOL = "the doubling theorem of Jain and Albert (arXiv:2408.12752, Sec. III)"

#: The distance of each self-dual input -- the least odd weight in the kernel
#: of its stabilisers -- that this folder PROVES, and the test that proves it.
PROVED = {
    7: (3, "test_the_small_self_dual_inputs_have_the_distances_used"),
    17: (5, "test_the_small_self_dual_inputs_have_the_distances_used"),
    23: (7, "test_the_small_self_dual_inputs_have_the_distances_used"),
    45: (9, "test_the_small_self_dual_inputs_have_the_distances_used"),
    47: (11, "test_the_small_self_dual_inputs_have_the_distances_used"),
    41: (9, "test_gong_s_self_dual_codes_have_the_distances_used"),
    65: (13, "test_gong_s_self_dual_codes_have_the_distances_used"),
    69: (13, "test_the_70_bit_code_gives_a_69_1_13"),
    79: (15, "test_the_larger_self_dual_inputs_have_the_distances_used"),
    101: (17, "test_the_larger_self_dual_inputs_have_the_distances_used"),
    103: (19, "test_the_larger_self_dual_inputs_have_the_distances_used"),
    167: (23, "test_the_168_bit_qr_code_has_distance_24"),
}
#: The self-dual inputs whose distance is taken from the paper's Table II, not
#: proved here: the distance used, and the classical distance it rests on.
FROM_PAPER = {
    191: (27, "the minimum distance 28 of the extended QR code [192,96], from "
              "the paper's Table II and not re-proved in this repository"),
    199: (31, "the minimum distance 32 of the extended QR code [200,100], from "
              "the paper's Table II and not re-proved in this repository"),
}
#: What a record resting on Table II has proved here besides its inputs'
#: distances.
_DOUBLING_PROVED = ("the doubling theorem's bound d >= min(d_sd, d_tri + 2), "
                    "proved in the docstring of "
                    "transversal_t_codes/certify_distances.py")
_STRUCTURE_PROVED = ("the code's triorthogonality and its harmful fault of the "
                     "paper's weight, checked by build_codes.py and by "
                     "tests/test_transversal_t_codes.py with faultcore")
TOOL_WITH_PAPER = (TOOL + ", with the extended QR distances of their Table II "
                   "(not re-proved here)")


def label_of(code) -> str:
    """The code's id in `codes.json` and `factories.json`."""
    prefix = ("G" if code.tables == ("G",) else "GJ" if code.tables == ("GJ",)
              else "JA")
    return f"{prefix}-{code.n}"


def self_dual_distance(n_sd):
    """``(distance, proved by, from the paper)`` of a self-dual input: the
    test that proves it, or the Table II statement it rests on."""
    if n_sd in PROVED:
        return PROVED[n_sd][0], f"{TEST_FILE}::{PROVED[n_sd][1]}", None
    if n_sd in FROM_PAPER:
        return FROM_PAPER[n_sd][0], None, FROM_PAPER[n_sd][1]
    raise AssertionError(f"the self-dual input of length {n_sd} has no distance")


def certificates(codes):
    """One record for every code but the one-qubit seed."""
    bound, paper, proved = {"1": 1}, {"1": []}, {"1": []}
    order = sorted(codes.values(), key=lambda c: c.n)
    for code in order:                   # an inner code is always shorter
        inner = B.SINGLE if code.tri == "1" else codes[code.tri]
        n_sd = (code.n - inner.n) // 2
        if 2 * n_sd + inner.n != code.n:
            raise AssertionError(f"{code.name}: not a doubling of {inner.name}")
        d_sd, _proof, statement = self_dual_distance(n_sd)
        paper[code.key] = sorted(set(paper[inner.key]
                                     + ([statement] if statement else [])))
        proved[code.key] = proved[inner.key] + (
            [] if statement else [f"d_sd = {d_sd} for the self-dual input of "
                                  f"length {n_sd} ({_proof})"])
        bound[code.key] = min(d_sd, bound[inner.key] + 2)
        if bound[code.key] != code.d:
            raise AssertionError(f"{code.name}: the inputs give d >= "
                                 f"{bound[code.key]}, not the paper's {code.d}")
    records = []
    for code in order:
        inner = B.SINGLE if code.tri == "1" else codes[code.tri]
        n_sd = (code.n - inner.n) // 2
        d_sd, proof, statement = self_dual_distance(n_sd)
        records.append({
            "label": label_of(code), "n": code.n, "k": 1, "N": len(code.rows),
            "columns_sha256": K.digest(B.columns_of(code)),
            "lower_bound": bound[code.key],
            "witness": code.witness,
            "construction": code.recipe,
            "self_dual_input": code.sd,
            "self_dual_distance": d_sd,
            **({"self_dual_distance_proved_by": proof} if proof else
               {"self_dual_distance_from_paper": statement}),
            "inner_code": "[[1,1,1]], one qubit" if inner is B.SINGLE else label_of(inner),
            "inner_lower_bound": bound[inner.key],
            **({"tool": TOOL_WITH_PAPER, "rests_on_paper": paper[code.key],
                "proved_here": [_DOUBLING_PROVED, _STRUCTURE_PROVED]
                               + sorted(set(proved[code.key]),
                                        key=proved[code.key].index)}
               if paper[code.key] else {}),
        })
    return records


def payload(codes):
    records = certificates(codes)
    return {
        "about": ("Lower bounds on the distance of the codes of transversal_t_codes/ "
                  "from the doubling theorem of Jain and Albert (arXiv:2408.12752, "
                  "Sec. III): d >= min(d_sd, d_tri + 2) at every doubling, from one "
                  "qubit up. Where every self-dual input along a code's chain has a "
                  "distance proved in this folder, self_dual_distance_proved_by "
                  "names the test that proves the last one, and the record has the "
                  "file's tool (the input of length 167 by the C bound recorded in "
                  "xqr168_distance.json). Where the chain uses a quantum QR code of "
                  "length 191 or 199, the record has its own tool and rests_on_paper lists "
                  "the minimum distances of the extended QR codes it takes from the "
                  "paper's Table II without re-proving them, and proved_here "
                  "lists what is proved here: the theorem, the code's structure "
                  "and every other input along the chain. columns_sha256 is "
                  "the SHA-256 of the code's columns as compact JSON "
                  "(master_catalog/constructions.digest), the circuit the catalogue "
                  "stores. witness is a harmful fault of weight lower_bound. Written "
                  "by transversal_t_codes/certify_distances.py."),
        "method": "theorem",
        "tool": TOOL,
        "records": records,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="rebuild and compare with the committed file")
    args = parser.parse_args(argv)
    text = B.render(payload(B.build()))
    if args.check:
        if not CERTIFICATES_JSON.exists() or \
                CERTIFICATES_JSON.read_text(encoding="utf-8") != text:
            raise SystemExit(f"out of date: {CERTIFICATES_JSON.name}")
        print(f"{CERTIFICATES_JSON.name} is up to date")
        return 0
    CERTIFICATES_JSON.write_text(text, encoding="utf-8")
    blob = json.loads(text)
    paper = [r for r in blob["records"] if r.get("rests_on_paper")]
    print(f"wrote {CERTIFICATES_JSON.name}: {len(blob['records'])} records, "
          f"{len(paper)} resting on the paper's Table II")
    for record in paper:
        print(f"  {record['label']}: {'; '.join(record['rests_on_paper'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
