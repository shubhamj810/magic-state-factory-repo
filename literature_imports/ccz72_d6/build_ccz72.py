#!/usr/bin/env python3
"""Rebuild the 72 T -> 1 CCZ, distance-6 protocol of Gong, Pattison, Rall and
Wills as one level-3 factory circuit.

    .venv/bin/python literature_imports/ccz72_d6/build_ccz72.py          # write ccz72.json, factories.json
    .venv/bin/python literature_imports/ccz72_d6/build_ccz72.py --check  # rebuild, compare, write nothing

A. Gong, C. A. Pattison, P. Rall and A. Wills, "Magic State Distillation via
Codes over Binary Extension Fields", arXiv:2608.09727 (v1, 2026-08-10), list
the chain ``(8T -> CCZ) * (9CCZ -> CCZ)`` in their Table 7 (T in, CCZ out),
with leading-order output error ``10^{4.58} p^6``.  It is two protocols:

* the outer one is their Construction 4.5, ``9CCZ -> 1CCZ`` at distance 3, a
  code over ``F_8 = F_2(alpha)``, ``alpha^3 = alpha + 1``, given by the
  generator matrix of their Eq. (49)::

        [ 0  0  a^2 a^4 a^6 a^8 a^3 a^5 1 ]   logical (x^2, padded with 0)
        [ 1  0  a   a^2 a^3 a^4 a^5 a^6 1 ]   stabiliser (x, padded with 1)
        [ 0  1  1   1   1   1   1   1   1 ]   stabiliser (1, padded with 0)

  It satisfies their twisted three-orthogonality, Eq. (41), so the
  single-qudit gate ``U_7: |g> -> (-1)^tr(g^7) |g>`` applied to all nine
  qudits is the logical ``U_7``.  Over ``F_8`` that gate is
  ``(-1)^[g != 0]``, a CCZ on the qudit's three qubits up to CZ and Z
  (their Sec. 3.2.5).  The paper binarises the matrix in the self-dual normal
  basis of its Eq. (46) by the rule of its Eq. (47): entry ``g`` becomes the
  3x3 block ``tr(g alpha_l alpha_j)``.
* the inner one is ``8T -> CCZ`` at distance 2, the ``k = 1`` member of the
  ``(6k+2)T -> kCCZ`` synthillation family of Campbell and Howard that the
  paper uses.  Its error ``28 p^2`` fixes it: 8 rotations on the parities
  ``x . (a, b, c) + s`` for every ``x`` in ``F_2^3``, with ``s`` its check.

Each of the nine CCZ states the outer code consumes comes from its own copy of
the inner protocol.  Written as one circuit, consuming a state on the parities
``(q_0, q_1, q_2)`` of the outer code means running the inner rotations with
``a, b, c`` replaced by ``q_0, q_1, q_2``.  The 8 rotations of copy ``i`` then
apply ``exp`` of ``pi/4`` times ``sum_x [x . q]``, which is ``4 [q != 0]``:
exactly ``U_7`` on qudit ``i``, with no Clifford left over.

THE CIRCUIT (k = 3, N = 18, n = 72)
-----------------------------------
wires 0..2    the binarised logical row (outputs)
wires 3..8    the binarised stabiliser rows (outer checks)
wires 9..17   the check wire of the inner copy feeding qudit 0..8
column 8 i + x, for qudit i = 0..8 and x = 0..7 read as bits (x_0 x_1 x_2),
    x_0 the most significant: the XOR of the binary columns of qubits (i, j)
    with x_j = 1, plus wire 9 + i.

The script builds the circuit, checks the algebra the construction rests on
(the basis is self-dual and normal, Eq. (49) is twisted three-orthogonal, the
binarisation reproduces the paper's printed Eq. (48) for its Eq. (45)), then
measures the distance and the leading coefficient with the master catalogue's
own `faultcore` and `errorcoeff`, and writes

    ccz72.json      the construction, the measured values and the paper's
    factories.json  the merge record, in `merge_results.py`'s input format
"""
from __future__ import annotations

import argparse
import itertools
import json
import re
import sys
from fractions import Fraction
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "master_catalog"))

import errorcoeff as EC                                            # noqa: E402
import faultcore as FC                                             # noqa: E402

CCZ72_JSON = HERE / "ccz72.json"
FACTORIES_JSON = HERE / "factories.json"
RELATIVE = "literature_imports/ccz72_d6/factories.json"

PAPER = ("A. Gong, C. A. Pattison, P. Rall, and A. Wills, \"Magic State "
         "Distillation via Codes over Binary Extension Fields,\" "
         "arXiv:2608.09727 (2026)")
CITE = "gong2026magic"
REGIME = "Gong et al.: F8 codes concatenated with 8T->CCZ"
STRENGTH = ("a concatenated protocol of Gong, Pattison, Rall and Wills "
            "(arXiv:2608.09727; literature_imports/ccz72_d6/): an F8 code fed "
            "by copies of the 8T->CCZ protocol, rebuilt here from the paper's "
            "construction and written as one circuit; a verified witness, not "
            "a maximum")

# ------------------------------------------------------------------ F_8
#: F_8 = F_2[alpha]/(alpha^3 + alpha + 1); an element is a 3-bit int, bit e
#: the coefficient of alpha^e.
MODULUS = 0b1011


def mul(a: int, b: int) -> int:
    """The product in F_8."""
    r = 0
    for e in range(3):
        if b >> e & 1:
            r ^= a << e
    for e in (4, 3):
        if r >> e & 1:
            r ^= MODULUS << (e - 3)
    return r


def power(a: int, e: int) -> int:
    r = 1
    for _ in range(e):
        r = mul(r, a)
    return r


def trace(g: int) -> int:
    """``tr(g) = g + g^2 + g^4``, which lies in F_2."""
    t = g ^ mul(g, g) ^ power(g, 4)
    assert t in (0, 1), g
    return t


ALPHA = 0b010


def alpha(e: int | None) -> int:
    """``alpha^e``, and 0 for ``None``."""
    return 0 if e is None else power(ALPHA, e)


#: The paper's Eq. (46): alpha_0 = alpha^2 + alpha + 1, alpha_1 = alpha + 1,
#: alpha_2 = alpha^2 + 1, a self-dual normal basis.
BASIS = (0b111, 0b011, 0b101)

#: Eq. (49), Construction 4.5, as exponents of alpha (None is 0).  The first
#: row is the logical, the other two the stabilisers.  The paper writes alpha^8
#: in the logical row, which is alpha.
EQ49 = (
    (None, None, 2, 4, 6, 8, 3, 5, 0),
    (0, None, 1, 2, 3, 4, 5, 6, 0),
    (None, 0, 0, 0, 0, 0, 0, 0, 0),
)
#: Eq. (45), Construction 4.3 (8CCZ -> 2CCZ), and its binarisation as the paper
#: prints it in Eq. (48).  Used only to pin the binarisation convention.
EQ45 = (
    (None, 2, 4, 6, 8, 3, 5, 0),
    (None, 1, 2, 3, 4, 5, 6, 0),
    (0, 0, 0, 0, 0, 0, 0, 0),
)
EQ48 = (
    "000 111 110 011 001 101 010 100",
    "000 100 111 110 011 001 101 010",
    "000 101 010 100 111 110 011 001",
    "000 001 111 101 110 010 011 100",
    "000 011 100 001 111 101 110 010",
    "000 111 101 110 010 011 100 001",
    "100 100 100 100 100 100 100 100",
    "010 010 010 010 010 010 010 010",
    "001 001 001 001 001 001 001 001",
)

#: Table 5 of the paper (App. D.2): K(a, b, c), the probability that three
#: input CCZ states with Z errors of weights a <= b <= c, placed and chosen
#: uniformly, give an accepted logical error of the binarised 9CCZ -> 1CCZ.
TABLE5 = {
    (1, 1, 1): Fraction(1, 63), (1, 1, 2): Fraction(17, 567),
    (1, 1, 3): Fraction(1, 189), (1, 2, 2): Fraction(1, 189),
    (1, 2, 3): Fraction(1, 27), (1, 3, 3): Fraction(1, 63),
    (2, 2, 2): Fraction(23, 567), (2, 2, 3): Fraction(1, 189),
    (2, 3, 3): Fraction(1, 63), (3, 3, 3): Fraction(1, 21),
}
TABLE7_LEADING = "10^{4.58} p^6"

#: The 8T -> CCZ protocol's rotations: x . (a, b, c) + s for x in F_2^3,
#: x_0 most significant.  Its accepted harmful faults of weight 2 are all 28
#: pairs, and Z error v in F_2^3 \ {0} comes from exactly 4 of them.
INNER_X = tuple(itertools.product((0, 1), repeat=3))


def field_matrix(exponents):
    return [[alpha(e) for e in row] for row in exponents]


def binarise(G):
    """Binary row ``(a, l)`` over qubit ``(i, j)`` is ``tr(g_ai alpha_l
    alpha_j)``: the paper's Eq. (47), row-major in ``(a, l)`` and ``(i, j)``."""
    return [[trace(mul(G[a][i], mul(BASIS[l], BASIS[j])))
             for i in range(len(G[0])) for j in range(3)]
            for a in range(len(G)) for l in range(3)]


def twisted_three_orthogonal(G, k):
    """Eq. (41): ``sum_i g_ai^4 g_bi^2 g_ci`` is 1 if ``a = b = c < k``, else 0."""
    for a, b, c in itertools.product(range(len(G)), repeat=3):
        s = 0
        for i in range(len(G[0])):
            s ^= mul(mul(power(G[a][i], 4), power(G[b][i], 2)), G[c][i])
        if s != (1 if a == b == c < k else 0):
            return False
    return True


def build():
    """``(binary outer matrix, columns)`` of the 72-rotation circuit."""
    H = binarise(field_matrix(EQ49))
    qudits = len(EQ49[0])
    wires = len(H)                                   # 9: 3 outputs, 6 checks

    def qubit(i, j):
        return {r for r in range(wires) if H[r][3 * i + j]}

    columns = []
    for i in range(qudits):
        for x in INNER_X:
            support = set()
            for j in range(3):
                if x[j]:
                    support ^= qubit(i, j)
            columns.append(sorted(support | {wires + i}))
    return H, columns


def check():
    """The algebra the construction rests on.  Raises on any failure."""
    assert all(BASIS[i + 1] == mul(BASIS[i], BASIS[i]) for i in range(2)), \
        "basis is not normal"
    assert all(trace(mul(BASIS[i], BASIS[j])) == (i == j)
               for i in range(3) for j in range(3)), "basis is not self-dual"
    printed = [[int(c) for c in row.replace(" ", "")] for row in EQ48]
    assert binarise(field_matrix(EQ45)) == printed, \
        "binarisation does not reproduce the paper's Eq. (48)"
    assert twisted_three_orthogonal(field_matrix(EQ45), 2)
    assert twisted_three_orthogonal(field_matrix(EQ49), 1), \
        "Eq. (49) is not twisted three-orthogonal"


def table5_coefficient():
    """The paper's leading coefficient from its own Table 5, exactly.

    ``C(9,3) sum P_abc w_a w_b w_c K(a,b,c)`` (its Eq. (189)), with the
    weights of the 8T -> CCZ protocol in place of the 2CS -> CCZ ones: an
    error of weight ``w`` arises from ``4 C(3, w)`` pairs, so ``w_1 = w_2 =
    12 p^2`` and ``w_3 = 4 p^2``."""
    w = {a: 4 * comb(3, a) for a in (1, 2, 3)}
    total = Fraction(0)
    for (a, b, c), K in TABLE5.items():
        perms = len(set(itertools.permutations((a, b, c))))
        total += perms * w[a] * w[b] * w[c] * K
    total *= comb(9, 3)
    assert total.denominator == 1, total
    return int(total)


def measure(columns, k=3, N=18):
    report = FC.distance_report(columns, k, N)
    d = report["d_exact"]
    coefficient = EC.error_coefficient(columns, k, N, d)
    return report, coefficient


def records(H, columns, report, coefficient):
    k, N, n = 3, 18, len(columns)
    d = report["d_exact"]
    meta = {
        "paper": PAPER,
        "arXiv": "2608.09727v1",
        "where": ("Table 7 (App. D.3), row '(8T -> CCZ) * (9CCZ -> CCZ)': "
                  "leading-order output error 10^{4.58} p^6, spatial footprint "
                  "13; outer code: Construction 4.5, Eq. (49), binarised by "
                  "Eqs. (46)-(47); transversality: Eq. (41), Lemma 4.2, "
                  "Sec. 3.2.5 (U_7 over F_8 is a CCZ up to Clifford); error "
                  "model: App. D.2, Example D.2 and Table 5"),
        "outer_F8_matrix_eq49": [" ".join("0" if e is None else "1" if e == 0
                                          else f"a^{e}" for e in row)
                                 for row in EQ49],
        "self_dual_normal_basis_eq46": "a^2+a+1, a+1, a^2+1",
        "outer_binary_matrix": [" ".join("".join(map(str, row[3 * i:3 * i + 3]))
                                         for i in range(9)) for row in H],
        "inner_protocol": "8T -> CCZ: rotations x.(a,b,c) + s, x in F_2^3",
        "wires": {"outputs": [0, 1, 2], "outer_checks": list(range(3, 9)),
                  "inner_checks": list(range(9, 18))},
        "k": k, "N": N, "n": n,
        "measured": {
            "d_exact": d,
            "scanned": report["scanned"],
            "witness": report["witness"],
            "A_d": coefficient["count"],
            "A_d_methods": coefficient["methods"],
        },
        "paper_error": {
            "table7_leading_order": TABLE7_LEADING,
            "table5_K": {f"{a}{b}{c}": str(K) for (a, b, c), K in TABLE5.items()},
            "table5_coefficient_exact": table5_coefficient(),
        },
    }
    record = {
        "k": k, "N": N, "n": n, "columns": columns,
        "gate": "CCZ012", "d": d,
        "regime": REGIME, "strength": STRENGTH,
        "discovery": "pre-existing",
        "citations": [CITE],
        "label": "GPRW-72T-CCZ",
        "file": RELATIVE,
        "origin": PAPER,
        "provenance": ("(8T -> CCZ) * (9CCZ -> CCZ) of Table 7: the F8 code of "
                       "Construction 4.5, Eq. (49), binarised in the self-dual "
                       "normal basis of Eq. (46), each of its nine input CCZ "
                       "states made by its own 8T -> CCZ, written as one "
                       "circuit with the nine inner checks as wires 9..17"),
        "notes": (f"A_{d} = {coefficient['count']}. The paper states "
                  f"{TABLE7_LEADING} (Table 7). Its Eq. (189) with its Table 5 "
                  f"and the 8T -> CCZ error weights (12, 12, 4) p^2 gives "
                  f"exactly {table5_coefficient()}, which is 10^4.576. "
                  f"Clifford correction: Z on each output and CZ on each "
                  f"pair, since transversal U_7 over F_8 deposits "
                  f"(-1)^[u != 0] on the logical qudit u"),
    }
    return meta, [record]


def render(payload) -> str:
    """``indent=1``, with integer lists kept on one line."""
    text = json.dumps(payload, indent=1)
    return re.sub(r"\[\s*\n\s*((?:-?\d+,\s+)*-?\d+)\s+\]",
                  lambda m: "[" + re.sub(r"\s+", " ", m.group(1)) + "]",
                  text) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="rebuild and compare with the committed files")
    args = parser.parse_args(argv)
    check()
    H, columns = build()
    report, coefficient = measure(columns)
    meta, out = records(H, columns, report, coefficient)
    texts = {CCZ72_JSON: render(meta), FACTORIES_JSON: render(out)}
    print(f"  [[{len(columns)},3,{report['d_exact']}]] N = 18, "
          f"A_{report['d_exact']} = {coefficient['count']} "
          f"(paper, from its Table 5: {table5_coefficient()})")
    if args.check:
        stale = [path.name for path, text in texts.items()
                 if not path.exists() or path.read_text(encoding="utf-8") != text]
        if stale:
            raise SystemExit(f"out of date: {', '.join(stale)}")
        print("ccz72.json and factories.json are up to date")
        return 0
    for path, text in texts.items():
        path.write_text(text, encoding="utf-8")
    print(f"wrote {CCZ72_JSON.name} and {FACTORIES_JSON.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
