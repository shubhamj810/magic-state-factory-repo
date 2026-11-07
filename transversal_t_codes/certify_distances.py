#!/usr/bin/env python3
"""The doubling theorem's distance bounds, for the codes whose hypotheses this
folder checks: writes `distance_certificates.json`.

    python transversal_t_codes/certify_distances.py           # write the file
    python transversal_t_codes/certify_distances.py --check   # compare with it

The doubling theorem of Jain and Albert (arXiv:2408.12752, Sec. III) gives
``d >= min(d_sd, d_tri + 2)`` for a self-dual input of distance ``d_sd`` doubled
onto a triorthogonal code of distance ``d_tri``.  The catalogue stores that
bound as a row's distance only when every input along the row's chain has a
distance this folder proves: by enumerating every word, or by the
Brouwer-Zimmermann bound of `min_distance.py`, each in a named test of
`tests/test_transversal_t_codes.py`.  The chain starts at one qubit
(``d = 1``).

The proved self-dual distances are `PROVED`.  The quantum QR codes of length
167, 191 and 199 are not in it: their distances rest on the minimum distances
24, 28 and 32 of the extended QR codes of length 168, 192 and 200, which the
paper's Table II states and this folder does not check (the bound of
`min_distance.py` would need about 3e12, 2e14 and 4e16 sums of rows).  The
codes that depend on them are listed under ``unchecked`` with that reason, and
the catalogue keeps their distance as the certificate beside ``d``.

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
}
#: What the inputs this folder does not check rest on.
UNCHECKED = {
    167: "the minimum distance 24 of the extended QR code [168,84], stated in "
         "the paper's Table II and not checked here",
    191: "the minimum distance 28 of the extended QR code [192,96], stated in "
         "the paper's Table II and not checked here",
    199: "the minimum distance 32 of the extended QR code [200,100], stated in "
         "the paper's Table II and not checked here",
}


def label_of(code) -> str:
    """The code's id in `codes.json` and `factories.json`."""
    prefix = ("G" if code.tables == ("G",) else "GJ" if code.tables == ("GJ",)
              else "JA")
    return f"{prefix}-{code.n}"


def certificates(codes):
    """``(records, unchecked)`` for every code but the one-qubit seed."""
    bound, missing = {"1": 1}, {"1": []}
    order = sorted(codes.values(), key=lambda c: c.n)
    for code in order:                   # an inner code is always shorter
        inner = B.SINGLE if code.tri == "1" else codes[code.tri]
        n_sd = (code.n - inner.n) // 2
        if 2 * n_sd + inner.n != code.n:
            raise AssertionError(f"{code.name}: not a doubling of {inner.name}")
        sd = PROVED.get(n_sd)
        missing[code.key] = missing[inner.key] + (
            [] if sd else [UNCHECKED.get(n_sd, f"the self-dual input of length "
                                               f"{n_sd}, not proved here")])
        if sd is None or bound[inner.key] is None:
            bound[code.key] = None
            continue
        bound[code.key] = min(sd[0], bound[inner.key] + 2)
        if bound[code.key] != code.d:
            raise AssertionError(f"{code.name}: the proved inputs give "
                                 f"d >= {bound[code.key]}, not the paper's {code.d}")
    records, unchecked = [], []
    for code in order:
        inner = B.SINGLE if code.tri == "1" else codes[code.tri]
        n_sd = (code.n - inner.n) // 2
        if bound[code.key] is None:
            unchecked.append({"label": label_of(code), "n": code.n,
                              "paper_distance": code.d,
                              "rests_on": sorted(set(missing[code.key]))})
            continue
        records.append({
            "label": label_of(code), "n": code.n, "k": 1, "N": len(code.rows),
            "columns_sha256": K.digest(B.columns_of(code)),
            "lower_bound": bound[code.key],
            "witness": code.witness,
            "construction": code.recipe,
            "self_dual_input": code.sd,
            "self_dual_distance": PROVED[n_sd][0],
            "self_dual_distance_proved_by": f"{TEST_FILE}::{PROVED[n_sd][1]}",
            "inner_code": "[[1,1,1]], one qubit" if inner is B.SINGLE else label_of(inner),
            "inner_lower_bound": bound[inner.key],
        })
    return records, unchecked


def payload(codes):
    records, unchecked = certificates(codes)
    return {
        "about": ("Lower bounds on the distance of the codes of transversal_t_codes/ "
                  "from the doubling theorem of Jain and Albert (arXiv:2408.12752, "
                  "Sec. III): d >= min(d_sd, d_tri + 2) at every doubling, from one "
                  "qubit up. A record is written only when every self-dual input "
                  "along its chain has a distance proved in this folder; "
                  "self_dual_distance_proved_by names the test. columns_sha256 is "
                  "the SHA-256 of the code's columns as compact JSON "
                  "(master_catalog/constructions.digest), the circuit the catalogue "
                  "stores. witness is a harmful fault of weight lower_bound. Written "
                  "by transversal_t_codes/certify_distances.py."),
        "method": "theorem",
        "tool": TOOL,
        "records": records,
        "unchecked": unchecked,
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
    print(f"wrote {CERTIFICATES_JSON.name}: {len(blob['records'])} certified, "
          f"{len(blob['unchecked'])} unchecked")
    for entry in blob["unchecked"]:
        print(f"  unchecked {entry['label']}: {'; '.join(entry['rests_on'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
