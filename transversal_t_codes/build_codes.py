#!/usr/bin/env python3
"""Rebuild the transversal-T codes of Jain and Albert as factory circuits.

    .venv/bin/python transversal_t_codes/build_codes.py          # write codes.json, factories.json
    .venv/bin/python transversal_t_codes/build_codes.py --check  # rebuild, compare, write nothing

S. P. Jain and V. V. Albert, "Transversal Clifford and T-gate codes of short
length and high distance", IEEE J. Sel. Areas Inf. Theory 6, 127-137 (2025),
arXiv:2408.12752, construct one-qubit CSS codes admitting the logical ``T``
gate by DOUBLING (their Sec. III, after Betsumiya-Munemasa and Bravyi-Cross): a
self-dual CSS code ``[[n_sd,1,d_sd]]`` and a triorthogonal code
``[[n_tri,1,d_tri]]``, both with logical ``X`` on every qubit, give the
triorthogonal code ``[[2 n_sd + n_tri, 1, min(d_sd, d_tri + 2)]]`` whose
generator matrix is

    [ 1      1      1     ]     <- the logical row (every qubit)
    [ C_sd   C_sd   0     ]     <- the self-dual code's X stabilisers, twice
    [ 0      0      C_tri ]     <- the triorthogonal code's X stabilisers
    [ 0      1      1     ]

The paper prints parameters, not matrices.  This script builds every code it
can from the recipe and the classical codes the paper names, and writes each
one as a factory: wire 0 is the logical row (the output), wires ``1..`` the X
stabilisers (the checks), and column ``j`` -- physical qubit ``j`` -- is the
set of rows containing it, one ``pi/4`` rotation.  Transversal ``T`` on the code
is then exactly these rotations.

THE TWO FAMILIES
----------------
Table II ("weak triply even"): starting from ``[[1,1,1]]`` (one qubit), double
with the ``[[7,1,3]]`` Steane code, the doubly even ``[[17,1,5]]`` color code,
the ``[[23,1,7]]`` Golay code -- giving ``[[15,1,3]]``, ``[[49,1,5]]``,
``[[95,1,7]]`` -- then twice each with the doubly even quantum quadratic-residue
codes of length 47, 79, 103, 167, 191 and 199: ``[[189,1,9]]`` up to
``[[3239,1,31]]``.  A quantum QR code of prime length ``p = -1 mod 8`` comes from
the extended QR code ``[p+1, (p+1)/2]``, a doubly even self-dual code, by the
paper's puncture-and-dualise map (its Lemma 2.4): X and Z stabilisers are both
the even-weight QR subcode.  The paper's Theorem 3.1 makes every member weak
triply even, with a partition ``M+ | M-`` of the qubits such that ``T`` on
``M+`` and ``T-dagger`` on ``M-`` is the logical ``T^m``, ``m = 7``; this
script carries the partition through each doubling and the tests check it.

Table I ("triorthogonal"): the same chain to ``[[95,1,7]]``, then doubled with
the ``[[45,1,9]]`` code of a self-dual ``[46,23,10]`` code -- here the
"subtraction" of the ``[48,24,12]`` extended QR code (keep the words agreeing
on two coordinates, delete both; Gaborit's tables list the ``[46,23,10]`` as
``sub(XQ47)``) -- to ``[[185,1,9]]``, then with ``[[47,1,11]]`` to
``[[279,1,11]]``.  These need ``S``/``CZ`` corrections in general.

The paper's Table I continues from ``[[279,1,11]]`` with a ``[[69,1,13]]`` code
from a ``[70,35,14]`` code, which its reference is a FORMALLY self-dual code
(Gulliver and Harada 1998), not a self-dual one; no self-dual ``[70,35,14]``
code is known.  The puncture-and-dualise map needs self-duality, so
``[[417,1,13]]`` and the nine codes doubled from it are not built here.
README.md says more.

DISTANCES
---------
Every doubling's distance is ``min(d_sd, d_tri + 2)``, and in both chains it is
``d_tri + 2`` at every step; so the fault ``{j, n_sd + j} + (witness of the
triorthogonal input)``, two qubits of the self-dual blocks plus the input's
own witness, is a harmful fault of weight exactly the paper's ``d``.  Each
code's witness is built that way from ``{0}`` on ``[[1,1,1]]`` and checked
against the true syndromes before anything is written.  The lower bound is
the paper's theorem: ``d >= min(d_sd, d_tri + 2)`` with the self-dual input's
distance at least the classical distance less one.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CODES_JSON = HERE / "codes.json"
FACTORIES_JSON = HERE / "factories.json"

PAPER = ("S. P. Jain and V. V. Albert, \"Transversal Clifford and T-gate codes "
         "of short length and high distance\", IEEE J. Sel. Areas Inf. Theory 6, "
         "127 (2025), arXiv:2408.12752")
CITE = "jain2025transversal"
#: The earliest publication of a code the paper rebuilds; the catalogue
#: credits a class to its earliest publication alone.  The 15- and 49-qubit
#: classes are already held (``15.1.3.a``, ``49.1.5.a``), so their records name
#: no citation and leave the held rows' credit as it is; the [[95,1,7]] class
#: is new and is credited to Sullivan.
HELD = (15, 49)
EARLIER = {
    15: ("bravyi2005universal", "the 15-qubit Reed-Muller code of Bravyi and "
                                "Kitaev (2005)"),
    49: ("bravyi2012magic", "the [[49,1,5]] code of Bravyi and Haah (2012)"),
    95: ("sullivan2024code", "the [[95,1,7]] code of Sullivan (2024), the "
                             "Golay code doubled onto [[49,1,5]]"),
}
REGIME_II = "Jain-Albert doubling: weak triply even family"
REGIME_I = "Jain-Albert doubling: triorthogonal family"
STRENGTH = {
    REGIME_II: ("a code of the weak triply even family of Jain and Albert "
                "(arXiv:2408.12752, Table II; transversal_t_codes/): "
                "quadratic-residue CSS codes doubled onto [[95,1,7]], rebuilt "
                "here from the paper's construction, where T on some qubits and "
                "T-dagger on the rest is a logical T; a verified witness, not a "
                "maximum"),
    REGIME_I: ("a code of the triorthogonal family of Jain and Albert "
               "(arXiv:2408.12752, Table I; transversal_t_codes/), self-dual "
               "CSS codes doubled onto [[95,1,7]], rebuilt here from the "
               "paper's construction; a verified witness, not a maximum"),
}

#: X stabilisers of the doubly even [[17,1,5]] code: one weight-8 and seven
#: weight-4 generators overlapping pairwise in 0 or 2 qubits.  The code is
#: unique up to qubit permutation -- with its parity bit appended it is the
#: self-dual [18,9,4] code d10+e7+f1, punctured at the f1 coordinate, the one
#: length-18 self-dual code with a coordinate no weight-4 word covers -- so
#: this is the 4.8.8 color code the paper uses (Bombin and Martin-Delgado).
COLOR17 = [
    [1, 2, 7, 8], [0, 4, 13, 16], [4, 9, 10, 13], [6, 7, 8, 14],
    [4, 9, 15, 16], [3, 5, 11, 12], [1, 2, 5, 12],
    [0, 1, 3, 6, 7, 12, 15, 16],
]


# ----------------------------------------------------------------- GF(2)
def weight(v: int) -> int:
    return v.bit_count()


def mask(support) -> int:
    out = 0
    for q in support:
        out |= 1 << q
    return out


def support(v: int) -> list[int]:
    out, q = [], 0
    while v:
        if v & 1:
            out.append(q)
        v >>= 1
        q += 1
    return out


def basis(vectors) -> list[int]:
    """A reduced row-echelon basis of the span, sorted by leading bit."""
    pivots: dict[int, int] = {}
    for v in vectors:
        for top in sorted(pivots, reverse=True):
            if (v >> top) & 1:
                v ^= pivots[top]
        if v:
            top = v.bit_length() - 1
            for other in pivots:
                if (pivots[other] >> top) & 1:
                    pivots[other] ^= v
            pivots[top] = v
    return [pivots[top] for top in sorted(pivots)]


def self_orthogonal(rows) -> bool:
    return all(weight(a & b) % 2 == 0 for i, a in enumerate(rows)
               for b in rows[i:])


def doubly_even(rows) -> bool:
    """Every word of the span has weight 0 mod 4: generators of weight 0 mod 4
    overlapping pairwise evenly."""
    return all(weight(r) % 4 == 0 for r in rows) and self_orthogonal(rows)


# --------------------------------------------------------- classical codes
def quadratic_residue_code(p: int) -> list[int]:
    """The binary QR code of prime length ``p = -1 mod 8``: the cyclic code
    spanned by the shifts of ``sum over residues r of x^r``, dimension
    ``(p + 1) / 2``."""
    if p % 8 != 7:
        raise ValueError(f"{p} is not -1 mod 8")
    residues = {(i * i) % p for i in range(1, p)}
    word = mask(residues)
    full = (1 << p) - 1
    shifts = [((word << s) | (word >> (p - s))) & full for s in range(p)]
    rows = basis(shifts)
    if len(rows) != (p + 1) // 2:
        raise AssertionError(f"QR({p}) came out of dimension {len(rows)}")
    return rows


def extend(rows, n: int) -> list[int]:
    """Append an overall parity bit at position ``n``."""
    return [r | ((weight(r) & 1) << n) for r in rows]


def subtract(rows, n: int, i: int, j: int) -> list[int]:
    """The words agreeing on coordinates ``i`` and ``j``, both deleted: a
    self-dual ``[n, n/2, d]`` code gives a self-dual ``[n-2, n/2-1, >= d-2]``."""
    agree = [r for r in rows if ((r >> i) ^ (r >> j)) & 1 == 0]
    differ = [r for r in rows if ((r >> i) ^ (r >> j)) & 1]
    agree += [differ[0] ^ r for r in differ[1:]]
    keep = [q for q in range(n) if q not in (i, j)]
    return basis([mask(t for t, q in enumerate(keep) if (r >> q) & 1)
                  for r in agree])


def is_self_dual(rows, n: int) -> bool:
    return len(basis(rows)) == n // 2 and self_orthogonal(rows)


def css_from_self_dual(rows, n: int) -> list[int]:
    """X stabilisers of the ``[[n-1, 1]]`` code of a self-dual ``[n, n/2]``
    code (the paper's Lemma 2.4): puncture the last coordinate to get ``C``;
    ``C-perp`` -- the words with a 0 there, shortened -- is both the X and the
    Z stabiliser space, and every qubit carries the logical X and Z."""
    if not is_self_dual(rows, n):
        raise AssertionError("the input is not self-dual")
    last = n - 1
    zero = [r for r in rows if not (r >> last) & 1]
    one = [r for r in rows if (r >> last) & 1]
    zero += [one[0] ^ r for r in one[1:]]
    out = basis([r & ((1 << last) - 1) for r in zero])
    if len(out) != n // 2 - 1:
        raise AssertionError("the shortened code has the wrong dimension")
    return out


# ------------------------------------------------------------------ codes
class Code:
    """A one-qubit triorthogonal code: ``rows[0]`` the logical row (every
    qubit), ``rows[1:]`` the X stabilisers, each a bitmask over ``n`` qubits."""

    def __init__(self, key, n, rows, d, witness, minus=None, m=None,
                 tables=(), recipe="", sd=None, tri=None):
        self.key, self.n, self.rows, self.d = key, n, rows, d
        self.witness = witness              # a harmful fault of weight d
        self.minus = minus                  # the M- of a TE* partition, or None
        self.m = m                          # |M+| - |M-| mod 8, or None
        self.tables, self.recipe = tuple(tables), recipe
        self.sd, self.tri = sd, tri

    @property
    def name(self):
        return f"[[{self.n},1,{self.d}]]"


SINGLE = Code("1", 1, [1], 1, [0], minus=[], m=1, recipe="one qubit")


def double(sd_stabs, n_sd, d_sd, tri: Code, sd_name, tables, de=False):
    """The paper's doubling map (its Eq. 7).

    ``de`` says the self-dual input is doubly even with ``n_sd = m mod 8``;
    then Theorem 3.1 gives a weak triply even output, its partition built from
    the input's -- flipped first when needed so both sides have the same
    ``m``, since swapping ``M+`` and ``M-`` negates ``m``.
    """
    n = 2 * n_sd + tri.n
    ones_sd = (1 << n_sd) - 1
    rows = [(1 << n) - 1]
    rows += [s | (s << n_sd) for s in sd_stabs]
    rows += [t << (2 * n_sd) for t in tri.rows[1:]]
    rows.append((ones_sd << n_sd) | (((1 << tri.n) - 1) << (2 * n_sd)))
    d = min(d_sd, tri.d + 2)
    if d != tri.d + 2:
        raise AssertionError("the witness below assumes d = d_tri + 2")
    witness = [0, n_sd] + [2 * n_sd + j for j in tri.witness]
    minus = m = None
    if de and tri.minus is not None:
        m_sd = n_sd % 8
        t_minus = set(tri.minus)
        if tri.m % 8 != m_sd:
            if (-tri.m) % 8 != m_sd:
                raise AssertionError("no orientation of the partition matches")
            t_minus = set(range(tri.n)) - t_minus       # flip: m -> -m
        # Theorem 3.1: M+ = M_de+ u (n_de + M_de+) u (2 n_de + M_te-),
        #              M- = M_de- u (n_de + M_de-) u (2 n_de + M_te+); M_de- = {}
        minus = sorted(2 * n_sd + j for j in range(tri.n) if j not in t_minus)
        m = (n - 2 * len(minus)) % 8
        if m != m_sd:
            raise AssertionError("Theorem 3.1 should keep m")
    return Code(f"{n}", n, rows, d, witness, minus=minus, m=m, tables=tables,
                recipe=f"{sd_name} doubled onto {tri.name}", sd=sd_name,
                tri=tri.key)


def quantum_qr(p):
    """X stabilisers of the doubly even quantum QR code ``[[p, 1, .]]``."""
    xq = extend(quadratic_residue_code(p), p)
    if not doubly_even(xq):
        raise AssertionError(f"the extended QR code of length {p + 1} is not "
                             f"doubly even")
    return css_from_self_dual(xq, p + 1)


#: The minimum distance of each extended QR code used, as the paper's Table II
#: states it; the quantum QR code's distance is one less (its Lemma 2.4 and the
#: transitivity of the QR code's automorphism group).  The tests recompute the
#: values through p = 47 by enumerating every codeword.
QR_DISTANCE = {7: 4, 23: 8, 47: 12, 79: 16, 103: 20, 167: 24, 191: 28, 199: 32}


def build():
    """Every code this folder ships, as ``{key: Code}``, in build order."""
    codes = {}
    steane = quantum_qr(7)
    golay = quantum_qr(23)
    color = [mask(f) for f in COLOR17]
    if not doubly_even(color) or len(basis(color)) != 8:
        raise AssertionError("COLOR17 is not a doubly even [17,8] code")
    both = ("I", "II")
    c15 = double(steane, 7, 3, SINGLE, "[[7,1,3]] Steane code (QR 7)", both, de=True)
    c49 = double(color, 17, 5, c15, "[[17,1,5]] 4.8.8 color code", both, de=True)
    c95 = double(golay, 23, 7, c49, "[[23,1,7]] Golay code (QR 23)", both, de=True)
    for code in (c15, c49, c95):
        codes[code.key] = code
    # Table II: each quantum QR code twice
    tri = c95
    for p in (47, 79, 103, 167, 191, 199):
        stabs = quantum_qr(p)
        for _twice in range(2):
            tri = double(stabs, p, QR_DISTANCE[p] - 1, tri,
                         f"[[{p},1,{QR_DISTANCE[p] - 1}]] quantum QR code "
                         f"(extended QR [{p + 1},{(p + 1) // 2},{QR_DISTANCE[p]}])",
                         ("II",), de=True)
            codes[tri.key] = tri
    # Table I: the [46,23,10] subtraction code, then QR 47
    xq47 = extend(quadratic_residue_code(47), 47)
    sub46 = subtract(xq47, 48, 46, 47)
    c185 = double(css_from_self_dual(sub46, 46), 45, 9, c95,
                  "[[45,1,9]] code of the self-dual [46,23,10] code sub(XQ47)",
                  ("I",))
    c279 = double(quantum_qr(47), 47, 11, c185,
                  "[[47,1,11]] quantum QR code (extended QR [48,24,12])", ("I",))
    codes[c185.key] = c185
    codes[c279.key] = c279
    return codes


# ------------------------------------------------------------- the checks
def triorthogonal(rows) -> bool:
    """Every pair and triple of rows overlaps evenly (the logical row too)."""
    for a, ra in enumerate(rows):
        for b in range(a + 1, len(rows)):
            pair = ra & rows[b]
            if not pair:
                continue
            if weight(pair) % 2:
                return False
            for c in range(b + 1, len(rows)):
                if weight(pair & rows[c]) % 2:
                    return False
    return True


def columns_of(code: Code) -> list[list[int]]:
    return [[q for q, r in enumerate(code.rows) if (r >> j) & 1]
            for j in range(code.n)]


def harmful(code: Code, fault) -> bool:
    """Zero syndrome on every check row and odd overlap with the logical row."""
    f = mask(fault)
    return (all(weight(r & f) % 2 == 0 for r in code.rows[1:])
            and weight(code.rows[0] & f) % 2 == 1)


def signed_phase_ok(code: Code) -> bool:
    """``T`` on ``M+``, ``T-dagger`` on ``M-`` is the logical ``T^m`` and does
    nothing on the stabilisers: in the factory picture, every degree-1, 2, 3
    coefficient of the signed phase vanishes on the check wires and the
    output's linear coefficient is ``m`` (the weight expansion of
    master_catalog/clifford.py, with signs)."""
    sign = [1] * code.n
    for j in code.minus:
        sign[j] = -1
    rows, N = code.rows, len(code.rows)

    def signed(v):
        return sum(sign[j] for j in support(v))

    if signed(rows[0]) % 8 != code.m % 8:
        return False
    for q in range(1, N):
        if signed(rows[q]) % 8:
            return False
    for q in range(N):
        for r in range(q + 1, N):
            pair = rows[q] & rows[r]
            if pair and (-2 * signed(pair)) % 8:
                return False
    # cubic coefficients are 4 x (signed triple overlap), odd overlaps are
    # excluded by triorthogonality, so they vanish already
    return True


def check(codes) -> None:
    for code in codes.values():
        where = code.name
        N = len(code.rows)
        if code.rows[0] != (1 << code.n) - 1:
            raise AssertionError(f"{where}: the logical row is not every qubit")
        if len(basis(code.rows)) != N:
            raise AssertionError(f"{where}: dependent rows")
        cols = columns_of(code)
        if len({tuple(c) for c in cols}) != code.n:
            raise AssertionError(f"{where}: repeated columns")
        if weight(code.rows[0]) % 2 == 0 or any(weight(r) % 2 for r in code.rows[1:]):
            raise AssertionError(f"{where}: row weights are not odd | even")
        if not triorthogonal(code.rows):
            raise AssertionError(f"{where}: not triorthogonal")
        if len(code.witness) != code.d or not harmful(code, code.witness):
            raise AssertionError(f"{where}: the witness is not a harmful fault "
                                 f"of weight {code.d}")
        if code.minus is not None and not signed_phase_ok(code):
            raise AssertionError(f"{where}: the M+/M- partition is not a "
                                 f"transversal T^{code.m}")


# ------------------------------------------------------------- the output
def certificate(code: Code) -> str:
    table = " and ".join(f"Table {t}" for t in code.tables)
    return (f"Jain and Albert (arXiv:2408.12752), {table}: {code.recipe}; the "
            f"doubling theorem of their Sec. III gives d >= min(d_sd, d_tri + 2) "
            f"= {code.d}, with d_sd at least the classical distance less one "
            f"(their Lemma 2.4)")


def records(codes):
    """``(codes.json payload, factories.json records)``."""
    meta, out = [], []
    for code in sorted(codes.values(), key=lambda c: (c.n, c.tables)):
        cols = columns_of(code)
        tables = list(code.tables)
        regime = REGIME_II if "II" in tables else REGIME_I
        earlier = EARLIER.get(code.n)
        entry = {
            "id": f"JA-{code.n}",
            "parameters": [code.n, 1, code.d],
            "tables": tables,
            "construction": code.recipe,
            "self_dual_input": code.sd,
            "triorthogonal_input": f"JA-{code.tri}" if code.tri not in (None, "1")
                                   else ("[[1,1,1]], one qubit" if code.tri else None),
            "N": len(code.rows),
            "check_rows": len(code.rows) - 1,
            "witness": code.witness,
            "weak_triply_even": None if code.minus is None else
                                {"m": code.m, "minus": code.minus},
            "distance_certificate": certificate(code),
            "earlier_publication": earlier[1] if earlier else None,
        }
        meta.append(entry)
        out.append({
            "k": 1, "N": len(code.rows), "n": code.n, "columns": cols,
            "gate": "T0", "d": code.d,
            "regime": regime, "strength": STRENGTH[regime],
            "discovery": "pre-existing",
            **({} if code.n in HELD else
               {"citations": [earlier[0]] if earlier else [CITE]}),
            "label": entry["id"],
            "file": "transversal_t_codes/factories.json",
            "origin": PAPER,
            "provenance": f"{code.recipe} ({' and '.join('Table ' + t for t in tables)})",
            **({"notes": f"earlier publication: {earlier[1]}"} if earlier else {}),
        })
    return {"paper": PAPER, "codes": meta}, out


def render(payload) -> str:
    """``indent=1``, with integer lists kept on one line."""
    import re
    text = json.dumps(payload, indent=1)
    return re.sub(r"\[\s*\n\s*((?:-?\d+,\s+)*-?\d+)\s+\]",
                  lambda m: "[" + re.sub(r"\s+", " ", m.group(1)) + "]",
                  text) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="rebuild and compare with the committed files")
    args = parser.parse_args(argv)
    codes = build()
    check(codes)
    meta, out = records(codes)
    texts = {CODES_JSON: render(meta), FACTORIES_JSON: render(out)}
    for code in sorted(codes.values(), key=lambda c: c.n):
        print(f"  {code.name:<16} N = {len(code.rows):>3}  Table "
              f"{'/'.join(code.tables):<5} {code.recipe}")
    if args.check:
        stale = [path.name for path, text in texts.items()
                 if not path.exists() or path.read_text(encoding="utf-8") != text]
        if stale:
            raise SystemExit(f"out of date: {', '.join(stale)}")
        print("codes.json and factories.json are up to date")
        return 0
    for path, text in texts.items():
        path.write_text(text, encoding="utf-8")
    print(f"wrote {CODES_JSON.name} and {FACTORIES_JSON.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
