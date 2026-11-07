#!/usr/bin/env python3
"""San José's factories as a catalogue construction, and a column-level check
of the hypotheses of their distance bound.

San José (arXiv:2609.08203, as the gamma-frontier release cites it; the
release's recipe is ``gamma_frontier_release/sources/pass4/san_jose/
normalized.json``) builds a triorthogonal binary matrix from a code over
F = GF(2^m).  This module turns a small object naming the field data, the
outer code and the punctured coordinates into the circuit's columns, in the
order `constructions.py` fixes (every column sorted ascending, the list of
columns sorted lexicographically).  It is written from the recipe and from
the research notes (``research/search/sparse/REPORT.md`` section 2,
``research/search2/sanjose2/REPORT.md`` sections 2 and 3) and imports no
research code.  Standard library and numpy only.

THE CONSTRUCTION
----------------
F = GF(2^m), with elements written as polynomial-basis bitmasks reduced by
``field_modulus`` (leading bit included).  q = 2^m.  Both families share
everything except the outer code C, a code of length ``ell`` over F with
generator rows listed in a fixed order.

Outer code, family ``san-jose-grs``.  The evaluation points are a = 0, 1,
..., L - 1 (L = ``outer_length``, so ell = L).  The residue weights are
r_a = 1 / prod_{b != a} (a + b) and the multipliers v_a = r_a^(q/4), so
v_a^4 = r_a.  C = {(v_a f(a))_a : deg f <= D}, D = ``outer_degree``, with
generator rows (v_a a^e)_a for e = 0..D (0^0 = 1).  Dimension D + 1.

Outer code, family ``san-jose-curve``.  K = ``curve_subspace`` is an
F_2-subspace of F with t elements, p_K(y) = prod_{kappa in K} (y + kappa),
and e = ``curve_exponent``.  The coordinates are all points (x, y) in F x F
with p_K(y) = x^e, ordered by x and then by y; there must be ell = q t of
them.  With A = ``pole_order`` and genus g = (t - 1)(e - 1)/2, C is the
evaluation of the functions of pole order at most A at the point at
infinity: generator rows x^i y^j for j = 0..t-1 (outer loop) and i = 0, 1,
... (inner loop) with i t + j e <= A (0^0 = 1).  Dimension A - g + 1.  For
t = 16, e = 17, q = 256 this is the Hermitian curve y^16 + y = x^17.

The steps after the outer code:

1. Punctures.  R = ``punctures``, an ordered list of P coordinates.  Gaussian
   elimination puts the generator into systematic form on R: for each
   coordinate c of R in order, the first row at or below the current rank
   with a non-zero entry in column c is swapped up, scaled to 1 there, and
   cleared from every other row.  With ``echelon`` = "reduced" the
   elimination then continues on the remaining coordinates in increasing
   order, skipping a coordinate with no pivot, until every row has one (this
   is the reduced row echelon form the release's records use, with R =
   0..P-1).  With ``echelon`` = "punctures" it stops after R.  Rows 0..P-1
   are then g_i (g_i = e_i on R) and the remaining rows are a basis h_r of
   the subcode that vanishes on R.
2. Inner map.  phi(y)_j = parity(embedding_columns[j] AND y), j = 0..s-1.
3. Rows (wires).  Wires 0..k-1 are the outputs, k = P |U|: wire i|U| + t is
   phi(u_t g_i), u_t = ``compatible_elements``[t].  Wires k..N-1 are checks,
   N = k + m (dim C - P): wire k + r m + j is phi(x^j h_r), x^j = 1 << j.
   Each row is taken on the retained coordinates (those not in R) in
   increasing order; retained coordinate number p and inner bit j give
   binary column p s + j, so n = s (ell - P).
4. Columns.  Column c is the set of wires whose row has bit c set.  The
   catalogue order then sorts the list of columns.

The object also carries ``k`` and ``N`` (as every construction does, so that
`catalogfile` can compare them with the row); `problems` checks that they
equal the values the other fields give.

THE DISTANCE THEOREM AND ITS PROOF
----------------------------------
Theorem.  Suppose the binary matrix has wires as in step 3 for SOME vectors
g_0..g_{P-1} and h_0, h_1, ... over F on the retained coordinates, where
(a) every g_i extended by e_i on R, and every h_r extended by 0 on R, lies
in an outer code C, (b) these extended vectors span C, and (c) every
non-zero word of the dual code of C has weight at least delta.  Then every
harmful fault has weight at least delta - P.

Proof.  Take a fault: a set of columns, that is, a binary vector e on the
(retained coordinate, inner bit) pairs.  On the block of coordinate a it
acts on a field value y as y -> sum_j e_{a,j} phi(y)_j, an F_2-linear
functional, so it equals y -> Tr(lambda_a y) for exactly one lambda_a in F.
The parity of the fault on the check wire (r, j) is Tr(x^j sum_a lambda_a
h_r[a]); the x^j form a basis of F over F_2 and the trace form is
non-degenerate, so the fault is undetected exactly when sum_a lambda_a
h_r[a] = 0 for every r.  Define lambda at each punctured coordinate R[i] as
lambda_{R[i]} = sum_a lambda_a g_i[a].  The extended vector lambda is then
orthogonal to every extended g_i (the extension of g_i is 1 at R[i] and 0
elsewhere on R, so the pairing is lambda_{R[i]} - lambda_{R[i]} = 0) and to
every extended h_r, hence by (b) to all of C: lambda lies in the dual of C.
The parity of the fault on the output wire (i, t) is Tr(u_t lambda_{R[i]}).
A harmful fault flips some output, so some lambda_{R[i]} is non-zero, so
lambda is a non-zero dual word and by (c) has at least delta non-zero
coordinates.  At most P of them lie on R; every other one is a retained
coordinate a with lambda_a != 0, which needs at least one bit of e in block
a.  So the fault has weight at least delta - P.

The dual distance.  GRS: with distinct points and non-zero multipliers the
dual of C is {(w_a h(a))_a : deg h <= L - D - 2} with w_a = r_a / v_a, and a
non-zero h of degree at most L - D - 2 has at most L - D - 2 roots, so
delta = D + 2 and the bound is D + 2 - P.  Curve: with B = ell + 2g - 2 - A,
the dual of C is the evaluation of the functions of pole order at most B
(the monomials x^i y^j, j < t, i t + j e <= B), and a non-zero such function
has at most B zeros, since its only pole is the point at infinity, of order
at most B (the Goppa bound).  So delta = ell - B = A - 2g + 2 and the bound
is A - 2g + 2 - P.

WHAT `hypothesis_check` VERIFIES
--------------------------------
It is given the columns (in any order), k, N and the construction, and it
re-derives the hypotheses from the binary columns:

* the columns are well-formed and are, as a multiset, the n columns the
  construction defines; the check then reads the given columns in the
  coordinate-and-bit order of step 3 (the distance does not depend on the
  order of columns);
* the inner map is injective, and every s-bit block of every wire decodes
  to a field element;
* the output wires of puncture i are u_t times one vector g_i, for every u_t
  in the compatible list, and the check wires come in groups of m that are
  x^j times one vector h_r;
* the outer code: it builds a generator of C and of the claimed dual
  directly from the points (not from the builder's elimination) and checks
  that they are orthogonal and that their ranks are dim C and ell - dim C,
  so the claimed dual is the whole dual.  GRS: also the points are distinct,
  every multiplier is non-zero and the residue identity sum_a r_a a^e = 0
  holds for e <= L - 2.  Curve: there are q t points, all distinct and on
  the curve, and the monomials have distinct pole orders;
* every recovered vector, extended by e_i or 0 on R, is orthogonal to the
  dual generator, hence in C; there are dim C - P vectors h_r, and the
  dim C extended vectors have full rank, so they span C.

It returns the bound and raises AssertionError on any failure.  The one
step it cannot check by computation is the root count of the last
paragraph above: a polynomial of degree at most L - D - 2 has at most that
many roots (GRS), and a function with a single pole of order at most B has
at most B zeros (curve; this rests on the curve p_K(y) = x^e with
gcd(t, e) = 1 being irreducible with one point at infinity, where x and y
have pole orders t and e).

It also reports, without asserting, the conditions that make the matrix a
factory rather than the distance hypotheses: the inner-map identity
sum_j phi_j(a) phi_j(b) phi_j(c) = Tr(abc(a + b + c)) on basis triples, the
compatible-set conditions, and the outer code's fourth-power condition
(GRS: v_a^4 = r_a and 4 D <= L - 2; curve: the sum over the points of every
monomial of pole order at most 4A vanishes).  Whether the matrix is a
factory is the verifier's question (Stage 0), as for any circuit.
"""
from __future__ import annotations

import hashlib
import json
from math import gcd

import numpy as np

GRS = "san-jose-grs"
CURVE = "san-jose-curve"

_COMMON = ("k", "N", "field_degree", "field_modulus", "embedding_columns",
           "compatible_elements")

#: Family name -> the fields of its construction object (besides "family").
FAMILIES = {
    GRS: _COMMON + ("outer_length", "outer_degree", "punctures", "echelon"),
    CURVE: _COMMON + ("curve_subspace", "curve_exponent", "pole_order",
                      "punctures", "echelon"),
}

_TAIL = (
    "Eliminate on the coordinates of punctures in the given order (pivot = "
    "first row at or below the current rank that is non-zero there; swap it "
    "up, scale to 1, clear the column in every other row); if echelon is "
    "\"reduced\", continue on the other coordinates in increasing order, "
    "skipping any without a pivot, until every row has one. Rows 0..P-1 are "
    "g_i, the rest are h_r. Inner map phi(y)_j = parity(embedding_columns[j] "
    "& y). Wire i*|U| + t (outputs, k = P*|U|) is phi(u_t g_i), u_t = "
    "compatible_elements[t]; wire k + r*m + j (checks) is phi((1 << j) h_r); "
    "rows are restricted to the coordinates not in punctures, in increasing "
    "order, and retained coordinate p, inner bit j is column p*s + j "
    "(s = len(embedding_columns)). Column c = the wires whose row has bit c "
    "set; then every column sorted ascending and the list sorted "
    "lexicographically. k and N repeat the wire counts.")

DESCRIPTIONS = {
    GRS: (
        "San José's construction (arXiv:2609.08203) from a generalised "
        "Reed-Solomon code over F = GF(2^m), m = field_degree, elements as "
        "polynomial-basis bitmasks reduced by field_modulus. Points a = "
        "0..L-1 (L = outer_length); r_a = 1/prod_{b != a}(a + b); v_a = "
        "r_a^(2^m/4). Generator rows (v_a a^e)_a, e = 0..D (D = outer_degree, "
        "0^0 = 1). " + _TAIL + " Distance at least D + 2 - P."),
    CURVE: (
        "San José's construction (arXiv:2609.08203) with the outer code from "
        "a curve over F = GF(2^m), m = field_degree, elements as "
        "polynomial-basis bitmasks reduced by field_modulus. K = "
        "curve_subspace (t elements, an F_2-subspace), e = curve_exponent, "
        "A = pole_order, g = (t-1)(e-1)/2. Coordinates: every (x, y) in F x F "
        "with prod_{kappa in K}(y + kappa) = x^e, ordered by x then y "
        "(there must be 2^m * t of them). Generator rows: x^i y^j evaluated "
        "at the coordinates, for j = 0..t-1 (outer) and i = 0, 1, ... (inner) "
        "with i*t + j*e <= A, 0^0 = 1. " + _TAIL +
        " Distance at least A - 2g + 2 - P."),
}

ECHELONS = ("reduced", "punctures")

#: Bounds on the shape, so that a corrupted object is a named rejection and
#: never an enormous build.  The research's rows that are built here have
#: m <= 8, s <= 21, at most 18,000 columns and 1,410 wires.
MAX_FIELD_DEGREE = 10
MAX_INNER_BITS = 62           # one s-bit block must fit in an int64 key
MAX_LENGTH = 4096             # outer code length
MAX_CELLS = 50_000_000        # wires x columns of the binary matrix


# ------------------------------------------------------------------ the field
def _clmul_mod(a: int, b: int, m: int, modulus: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> m:
            a ^= modulus
    return r


def _irreducible(modulus: int, m: int) -> bool:
    """No polynomial of degree 1..m/2 divides the modulus."""
    def degree(p):
        return p.bit_length() - 1

    def remainder(a, b):
        db = degree(b)
        while a and degree(a) >= db:
            a ^= b << (degree(a) - db)
        return a

    for d in range(1, m // 2 + 1):
        for p in range(1 << d, 1 << (d + 1)):
            if remainder(modulus, p) == 0:
                return False
    return True


class Field:
    """GF(2^m) with exp/log tables; vectorised products on numpy arrays."""

    def __init__(self, m: int, modulus: int):
        if modulus >> m != 1:
            raise ValueError(f"modulus {modulus} does not have degree {m}")
        self.m, self.q, self.modulus = m, 1 << m, modulus
        q = self.q
        for g in range(2, q):
            exp = [0] * (q - 1)
            x, ok = 1, True
            for i in range(q - 1):
                exp[i] = x
                x = _clmul_mod(x, g, m, modulus)
                if x == 1 and i < q - 2:
                    ok = False
                    break
            if ok and x == 1 and len(set(exp)) == q - 1:
                break
        else:
            raise ValueError(f"modulus {modulus} is not irreducible")
        self.exp_list = exp
        self.log_list = [0] * q
        for i, x in enumerate(exp):
            self.log_list[x] = i
        self.exp = np.array(exp + exp, dtype=np.int64)
        self.log = np.array(self.log_list, dtype=np.int64)

    def mul(self, a: int, b: int) -> int:
        if a == 0 or b == 0:
            return 0
        return self.exp_list[(self.log_list[a] + self.log_list[b])
                             % (self.q - 1)]

    def inv(self, a: int) -> int:
        if a == 0:
            raise ZeroDivisionError("inverse of 0")
        return self.exp_list[(-self.log_list[a]) % (self.q - 1)]

    def pow(self, a: int, e: int) -> int:
        if e == 0:
            return 1
        if a == 0:
            return 0
        return self.exp_list[(self.log_list[a] * e) % (self.q - 1)]

    def trace(self, a: int) -> int:
        t, x = 0, a
        for _ in range(self.m):
            t ^= x
            x = self.mul(x, x)
        assert t in (0, 1)
        return t

    def scale(self, f: int, v: np.ndarray) -> np.ndarray:
        """f times every entry of v."""
        if f == 0:
            return np.zeros_like(v)
        out = self.exp[self.log[v] + self.log_list[f]]
        out[v == 0] = 0
        return out

    def times(self, u: np.ndarray, v: np.ndarray) -> np.ndarray:
        """Entrywise product (broadcasting)."""
        out = self.exp[self.log[u] + self.log[v]]
        out[(u == 0) | (v == 0)] = 0
        return out

    def rank(self, M: np.ndarray) -> int:
        M = np.array(M, dtype=np.int64, copy=True)
        rows, cols = M.shape
        r = 0
        for c in range(cols):
            if r == rows:
                break
            nz = np.flatnonzero(M[r:, c])
            if not len(nz):
                continue
            p = r + int(nz[0])
            if p != r:
                M[[r, p]] = M[[p, r]]
            M[r] = self.scale(self.inv(int(M[r, c])), M[r])
            below = np.flatnonzero(M[r + 1:, c]) + r + 1
            if len(below):
                M[below] ^= self.times(M[below, c][:, None], M[r][None, :])
            r += 1
        return r


# ------------------------------------------------------------------ the shape
def _is_int(x) -> bool:
    return type(x) is int


def _int_list(value) -> bool:
    return (isinstance(value, list) and bool(value)
            and all(_is_int(x) for x in value))


def _curve_numbers(c):
    """(t, e, genus, length, dimension, dual pole bound) of a curve object
    whose fields have already passed the type checks."""
    t, e, A = len(c["curve_subspace"]), c["curve_exponent"], c["pole_order"]
    g = (t - 1) * (e - 1) // 2
    ell = (1 << c["field_degree"]) * t
    return t, e, g, ell, A - g + 1, ell + 2 * g - 2 - A


def _length_and_dimension(c):
    if c["family"] == GRS:
        return c["outer_length"], c["outer_degree"] + 1
    _, _, _, ell, dim, _ = _curve_numbers(c)
    return ell, dim


def problems(construction) -> list[str]:
    """What is wrong with the SHAPE of a construction; empty if nothing.

    Checked before anything is built, so a hand-edited or corrupted object is
    a named rejection and never a crash or an enormous loop.
    """
    if not isinstance(construction, dict):
        return [f"the construction is a {type(construction).__name__}, not "
                f"an object"]
    family = construction.get("family")
    if family not in FAMILIES:
        return [f"unknown construction family {family!r}; this module knows "
                f"{', '.join(FAMILIES)}"]
    fields = FAMILIES[family]
    found = [name for name in construction if name != "family"]
    if sorted(found) != sorted(fields):
        return [f"a {family} construction has the fields "
                f"{', '.join(fields)}, not {', '.join(sorted(found))}"]
    c = construction
    ints = ["k", "N", "field_degree", "field_modulus"]
    lists = ["embedding_columns", "compatible_elements", "punctures"]
    if family == GRS:
        ints += ["outer_length", "outer_degree"]
    else:
        ints += ["curve_exponent", "pole_order"]
        lists += ["curve_subspace"]
    out = []
    for name in ints:
        if not _is_int(c[name]) or c[name] < 1:
            out.append(f"{name} must be a positive whole number, not "
                       f"{c[name]!r}")
    for name in lists:
        if not _int_list(c[name]):
            out.append(f"{name} must be a non-empty list of whole numbers")
    if c["echelon"] not in ECHELONS:
        out.append(f"echelon must be one of {', '.join(ECHELONS)}, not "
                   f"{c['echelon']!r}")
    if out:
        return out
    m = c["field_degree"]
    if not 3 <= m <= MAX_FIELD_DEGREE:
        return [f"need 3 <= field_degree <= {MAX_FIELD_DEGREE}, not {m}"]
    q = 1 << m
    mod = c["field_modulus"]
    if mod >> m != 1:
        out.append(f"field_modulus {mod} is not of degree {m} (its leading "
                   f"bit must be 2^{m})")
    elif not _irreducible(mod, m):
        out.append(f"field_modulus {mod} is reducible")
    emb, U = c["embedding_columns"], c["compatible_elements"]
    if not len(emb) <= MAX_INNER_BITS:
        out.append(f"at most {MAX_INNER_BITS} embedding columns, not "
                   f"{len(emb)}")
    if not all(0 < x < q for x in emb) or len(set(emb)) != len(emb):
        out.append(f"embedding_columns must be distinct and in 1..{q - 1}")
    if not len(U) <= m:
        out.append(f"at most m = {m} compatible elements, not {len(U)}")
    if not all(0 < x < q for x in U) or len(set(U)) != len(U):
        out.append(f"compatible_elements must be distinct and in 1..{q - 1}")
    R = c["punctures"]
    P = len(R)
    if family == GRS:
        L, D = c["outer_length"], c["outer_degree"]
        if not L <= q:
            out.append(f"outer_length {L} exceeds the field size {q}")
        if not 4 * D <= L - 2:
            out.append(f"need 4 outer_degree <= outer_length - 2, not "
                       f"4*{D} > {L} - 2")
        if not P <= D:
            out.append(f"need 1 <= P <= outer_degree, not P={P} with "
                       f"outer_degree {D}")
    else:
        K, e, A = c["curve_subspace"], c["curve_exponent"], c["pole_order"]
        t, Kset = len(K), set(K)
        if (t < 2 or t & (t - 1) or q * t > MAX_LENGTH
                or not all(0 <= x < q for x in K)
                or len(Kset) != t or 0 not in Kset
                or any(a ^ b not in Kset for a in K for b in K)):
            out.append(f"curve_subspace must be an F_2-subspace of F with at "
                       f"least 2 elements, listed once each, and q t at "
                       f"most {MAX_LENGTH}")
        elif not 2 <= e < q or gcd(e, t) != 1:
            out.append(f"need 2 <= curve_exponent < {q} and gcd(curve_"
                       f"exponent, t) = 1, not {e} with t = {t}")
        else:
            _, _, g, ell, dim, _ = _curve_numbers(c)
            if not 2 * g - 1 <= A or not 4 * A <= ell + 2 * g - 2:
                out.append(f"need 2g - 1 <= pole_order and 4 pole_order <= "
                           f"q t + 2g - 2, not pole_order {A} with g = {g}, "
                           f"q t = {ell}")
            elif not P <= dim - 1 or not A - 2 * g + 2 - P >= 1:
                out.append(f"need P <= dim - 1 = {dim - 1} and a positive "
                           f"bound A - 2g + 2 - P, not P = {P}")
    if out:
        return out
    ell, dim = _length_and_dimension(c)
    if not all(0 <= x < ell for x in R) or len(set(R)) != len(R):
        out.append(f"punctures must be distinct coordinates in 0..{ell - 1}")
    k = P * len(U)
    N = k + m * (dim - P)
    if c["k"] != k or c["N"] != N:
        out.append(f"k and N must be P*|U| = {k} and k + m(dim - P) = {N}, "
                   f"not k={c['k']}, N={c['N']}")
    n = len(emb) * (ell - P)
    if n * N > MAX_CELLS:
        out.append(f"the binary matrix would have {n} x {N} cells, more than "
                   f"{MAX_CELLS}")
    return out


def _require(construction):
    wrong = problems(construction)
    if wrong:
        raise ValueError("; ".join(wrong))


# -------------------------------------------------------------- outer codes
def residues(F: Field, L: int) -> list[int]:
    """r_a = 1 / prod_{b != a} (a + b) over the points 0..L-1."""
    out = []
    for a in range(L):
        den = 1
        for b in range(L):
            if b != a:
                den = F.mul(den, a ^ b)
        out.append(F.inv(den))
    return out


def grs_generator(F: Field, L: int, D: int):
    """The generator rows (v_a a^e), e = 0..D, and the residues and
    multipliers they use."""
    r = residues(F, L)
    v = [F.pow(x, F.q // 4) for x in r]
    G = np.array([[F.mul(v[a], F.pow(a, e)) for a in range(L)]
                  for e in range(D + 1)], dtype=np.int64)
    return G, r, v


def curve_points(F: Field, K, e) -> list[tuple[int, int]]:
    """Every (x, y) with prod_{kappa in K} (y + kappa) = x^e, by x then y."""
    by_value: dict[int, list[int]] = {}
    for y in range(F.q):
        val = 1
        for kappa in K:
            val = F.mul(val, y ^ kappa)
        by_value.setdefault(val, []).append(y)
    return [(x, y) for x in range(F.q) for y in by_value.get(F.pow(x, e), [])]


def monomials(t: int, e: int, bound: int) -> list[tuple[int, int]]:
    """(i, j) with j < t (outer) and i t + j e <= bound (inner, ascending)."""
    return [(i, j) for j in range(t) for i in range(bound // t + 1)
            if i * t + j * e <= bound]


def curve_matrix(F: Field, points, monos) -> np.ndarray:
    """Row (i, j) is x^i y^j at every point (0^0 = 1)."""
    xs = np.array([p[0] for p in points], dtype=np.int64)
    ys = np.array([p[1] for p in points], dtype=np.int64)
    top_i = max(i for i, _ in monos)
    top_j = max(j for _, j in monos)
    xp = [np.ones_like(xs)]
    for _ in range(top_i):
        xp.append(F.times(xp[-1], xs))
    yp = [np.ones_like(ys)]
    for _ in range(top_j):
        yp.append(F.times(yp[-1], ys))
    return np.array([F.times(xp[i], yp[j]) for i, j in monos],
                    dtype=np.int64)


def outer_generator(F: Field, c) -> np.ndarray:
    """The generator rows of the outer code C, in the order of the docs."""
    if c["family"] == GRS:
        G, _, v = grs_generator(F, c["outer_length"], c["outer_degree"])
        if not all(v):
            raise ValueError("a multiplier v_a is zero")
        return G
    t, e, g, ell, dim, _ = _curve_numbers(c)
    pts = curve_points(F, c["curve_subspace"], e)
    if len(pts) != ell:
        raise ValueError(f"the curve has {len(pts)} points, not q t = {ell}")
    monos = monomials(t, e, c["pole_order"])
    if len(monos) != dim:
        raise ValueError(f"{len(monos)} monomials, not A - g + 1 = {dim}")
    return curve_matrix(F, pts, monos)


# ---------------------------------------------------------------- the builder
def _eliminate(F: Field, G: np.ndarray, R, echelon: str) -> np.ndarray:
    """Systematic form on R (in R's order), then on the other coordinates in
    increasing order if echelon is "reduced"."""
    G = G.copy()
    rows = G.shape[0]
    rank = 0

    def pivot(c, required):
        nonlocal rank
        nz = np.flatnonzero(G[rank:, c])
        if not len(nz):
            if required:
                raise ValueError(f"the outer code has no pivot at punctured "
                                 f"coordinate {c}")
            return
        p = rank + int(nz[0])
        if p != rank:
            G[[rank, p]] = G[[p, rank]]
        G[rank] = F.scale(F.inv(int(G[rank, c])), G[rank])
        col = G[:, c].copy()
        col[rank] = 0
        others = np.flatnonzero(col)
        if len(others):
            G[others] ^= F.times(col[others][:, None], G[rank][None, :])
        rank += 1

    for c in R:
        pivot(c, True)
    if echelon == "reduced":
        Rset = set(R)
        for c in range(G.shape[1]):
            if rank == rows:
                break
            if c not in Rset:
                pivot(c, False)
    return G


def inner_image(F: Field, emb) -> np.ndarray:
    """img[y, j] = parity(emb[j] & y), as a q x s array of 0/1."""
    ys = np.arange(F.q, dtype=np.int64)
    out = np.zeros((F.q, len(emb)), dtype=np.uint8)
    for j, col in enumerate(emb):
        x = ys & col
        par = np.zeros(F.q, dtype=np.int64)
        while np.any(x):
            par ^= x & 1
            x = x >> 1
        out[:, j] = par
    return out


def build(construction) -> dict:
    """The circuit in BUILD order (step 3 of the module docstring), with the
    field rows and coordinates it came from.  `columns` sorts it."""
    _require(construction)
    c = construction
    m = c["field_degree"]
    F = Field(m, c["field_modulus"])
    emb, U, R = c["embedding_columns"], c["compatible_elements"], c["punctures"]
    P, s = len(R), len(emb)
    G = outer_generator(F, c)
    ell, dim = G.shape[1], G.shape[0]
    E = _eliminate(F, G, R, c["echelon"])
    Rset = set(R)
    keep = [a for a in range(ell) if a not in Rset]
    rows = [F.scale(u, E[i]) for i in range(P) for u in U]
    rows += [F.scale(1 << j, E[r]) for r in range(P, dim) for j in range(m)]
    FR = np.array(rows, dtype=np.int64)[:, keep]
    B = inner_image(F, emb)[FR].reshape(FR.shape[0], -1)   # wires x n
    k, N, n = P * len(U), B.shape[0], B.shape[1]
    assert (k, N, n) == (c["k"], c["N"], s * (ell - P))
    BT = np.ascontiguousarray(B.T)
    del B
    cols = [np.flatnonzero(BT[j]).tolist() for j in range(n)]
    return {"n": n, "k": k, "N": N, "bound": bound(c), "columns": cols,
            "field_rows": FR, "keep": keep, "punctures": list(R)}


def columns(construction) -> list[list[int]]:
    """The circuit, in the order `constructions.py` fixes."""
    out = build(construction)["columns"]
    out.sort()
    return out


def sorted_positions(build_columns) -> list[int]:
    """``pos[j]`` = the index of build-order column j in the sorted list.

    Equal columns keep their build order (a stable sort), so the map is a
    bijection even when columns repeat.
    """
    order = sorted(range(len(build_columns)), key=lambda j: build_columns[j])
    pos = [0] * len(order)
    for i, j in enumerate(order):
        pos[j] = i
    return pos


def bound(construction) -> int:
    """The theorem's lower bound on the distance: D + 2 - P (GRS) or
    A - 2g + 2 - P (curve)."""
    _require(construction)
    c = construction
    P = len(c["punctures"])
    if c["family"] == GRS:
        return c["outer_degree"] + 2 - P
    _, _, g, _, _, _ = _curve_numbers(c)
    return c["pole_order"] - 2 * g + 2 - P


def canonical_text(cols) -> str:
    """Compact JSON, the text ``columns_sha256`` is taken over (as in
    `constructions.canonical_text`)."""
    return json.dumps(cols, separators=(",", ":"))


def digest(cols) -> str:
    return hashlib.sha256(canonical_text(cols).encode("ascii")).hexdigest()


# ------------------------------------------------------ the hypothesis check
def _check(condition, message):
    if not condition:
        raise AssertionError(message)


def _pairings(F: Field, X: np.ndarray, Y: np.ndarray) -> np.ndarray:
    """``out[i, j] = sum_a X[i, a] Y[j, a]`` over F."""
    out = np.zeros((X.shape[0], Y.shape[0]), dtype=np.int64)
    for i in range(X.shape[0]):
        prod = F.times(X[i][None, :], Y)
        out[i] = np.bitwise_xor.reduce(prod, axis=1)
    return out


def _outer_and_dual(F: Field, c):
    """A generator of C and of its claimed dual, built from the points, with
    the checks that make the claim true (see the module docstring), and the
    factory side conditions of the outer code."""
    q = F.q
    if c["family"] == GRS:
        L, D = c["outer_length"], c["outer_degree"]
        _check(len(set(range(L))) == L and L <= q, "evaluation points")
        G, r, v = grs_generator(F, L, D)
        _check(all(v), "a multiplier v_a is zero")
        w = [F.mul(ra, F.inv(va)) for ra, va in zip(r, v)]
        _check(all(w), "a dual multiplier w_a is zero")
        W = np.array([[F.mul(w[a], F.pow(a, e)) for a in range(L)]
                      for e in range(L - D - 1)], dtype=np.int64)
        for e in range(L - 1):
            tot = 0
            for a in range(L):
                tot ^= F.mul(r[a], F.pow(a, e))
            _check(tot == 0, f"residue identity fails at e = {e}")
        side = {"multipliers_fourth_power_is_residue":
                all(F.pow(x, 4) == y for x, y in zip(v, r)),
                "four_D_at_most_L_minus_2": 4 * D <= L - 2}
        return G, W, D + 2, side
    t, e, g, ell, dim, Bpole = _curve_numbers(c)
    K, A = c["curve_subspace"], c["pole_order"]
    pts = curve_points(F, K, e)
    _check(len(pts) == ell, f"the curve has {len(pts)} points, not {ell}")
    _check(len(set(pts)) == ell, "the curve points are not distinct")
    for x, y in pts:
        val = 1
        for kappa in K:
            val = F.mul(val, y ^ kappa)
        _check(val == F.pow(x, e), f"({x}, {y}) is not on the curve")
    mon_a, mon_b = monomials(t, e, A), monomials(t, e, Bpole)
    for monos in (mon_a, mon_b):
        orders = [i * t + j * e for i, j in monos]
        _check(len(set(orders)) == len(orders),
               "two monomials share a pole order")
    G, W = curve_matrix(F, pts, mon_a), curve_matrix(F, pts, mon_b)
    _check(len(mon_a) == dim, f"{len(mon_a)} monomials, not A - g + 1")
    _check(len(mon_b) == ell - dim, f"{len(mon_b)} dual monomials, not "
                                    f"ell - dim C = {ell - dim}")
    top = 4 * A
    mon_4 = monomials(t, e, top)
    moments = curve_matrix(F, pts, mon_4)
    side = {"moments_vanish_to_pole_order_4A":
            not np.any(np.bitwise_xor.reduce(moments, axis=1)),
            "four_A_at_most_ell_plus_2g_minus_2": 4 * A <= ell + 2 * g - 2}
    return G, W, ell - Bpole, side


def hypothesis_check(columns, k, N, construction) -> dict:
    """Re-derive the hypotheses of the distance theorem from the columns.

    See the module docstring for the list.  Returns a dict whose ``bound``
    is the proved lower bound; raises AssertionError with a message naming
    the first hypothesis that fails.
    """
    wrong = problems(construction)
    _check(not wrong, f"construction: {'; '.join(wrong)}")
    c = construction
    m = c["field_degree"]
    emb, U, R = c["embedding_columns"], c["compatible_elements"], c["punctures"]
    P, s, nU = len(R), len(emb), len(U)
    ell, dim = _length_and_dimension(c)
    _check(k == c["k"] and N == c["N"],
           f"k={k}, N={N} differ from the construction's k={c['k']}, "
           f"N={c['N']}")
    n = s * (ell - P)
    _check(len(columns) == n, f"{len(columns)} columns, the construction "
                              f"has {n}")
    for j, col in enumerate(columns):
        _check(isinstance(col, (list, tuple))
               and all(type(w) is int and 0 <= w < N for w in col)
               and all(a < b for a, b in zip(col, col[1:])),
               f"column {j} is not a strictly increasing list of wires in "
               f"0..{N - 1}")

    # Align the given columns with the coordinate-and-bit order.
    expected = build(c)["columns"]
    slots: dict[tuple, list[int]] = {}
    for j, col in enumerate(expected):
        slots.setdefault(tuple(col), []).append(j)
    del expected
    B = np.zeros((N, n), dtype=np.uint8)
    for j, col in enumerate(columns):
        free = slots.get(tuple(col))
        _check(free, f"column {j} ({list(col)[:8]}...) is not a column of "
                     f"this construction, or occurs too often")
        B[list(col), free.pop()] = 1
    _check(not any(slots.values()), "some column of the construction is "
                                    "missing")

    # Decode every s-bit block through the inner map.
    F = Field(m, c["field_modulus"])
    q = F.q
    img = inner_image(F, emb)
    weights = (np.int64(1) << np.arange(s, dtype=np.int64))
    keys = img.astype(np.int64) @ weights                 # key of phi(y)
    _check(len(set(keys.tolist())) == q, "the inner map is not injective")
    order = np.argsort(keys)
    sorted_keys = keys[order]
    vals = np.zeros((N, ell - P), dtype=np.int64)
    for r0 in range(0, N, 128):                           # bounded memory
        blocks = (B[r0:r0 + 128].reshape(-1, ell - P, s).astype(np.int64)
                  @ weights)
        at = np.minimum(np.searchsorted(sorted_keys, blocks), q - 1)
        _check(np.array_equal(sorted_keys[at], blocks),
               "a block of s bits is not the image of a field element")
        vals[r0:r0 + 128] = order[at]
    del B

    # Output wires: u_t times one vector per puncture.
    inv_u0 = F.inv(U[0])
    g = []
    for i in range(P):
        base = F.scale(inv_u0, vals[i * nU])
        for t, u in enumerate(U):
            _check(np.array_equal(vals[i * nU + t], F.scale(u, base)),
                   f"output wire {i * nU + t} is not u_{t} times the vector "
                   f"of puncture {i}")
        g.append(base)
    # Check wires: x^j times one vector per group of m.
    _check((N - k) % m == 0, f"N - k = {N - k} is not a multiple of m = {m}")
    ne = (N - k) // m
    h = []
    for r in range(ne):
        base = vals[k + r * m]
        for j in range(m):
            _check(np.array_equal(vals[k + r * m + j],
                                  F.scale(1 << j, base)),
                   f"check wire {k + r * m + j} is not x^{j} times the "
                   f"vector of group {r}")
        h.append(base)
    _check(ne == dim - P, f"{ne} check groups, the subcode vanishing on the "
                          f"punctures has dimension {dim - P}")

    # The outer code and its dual.
    G, W, delta, side = _outer_and_dual(F, c)
    _check(G.shape == (dim, ell), "outer generator shape")
    _check(F.rank(G) == dim, "the outer generator does not have rank dim C")
    _check(F.rank(W) == ell - dim and W.shape[0] == ell - dim,
           "the dual generator does not have rank ell - dim C")
    _check(not np.any(_pairings(F, G, W)), "the dual generator is not "
                                           "orthogonal to the outer code")

    # Recovered vectors, extended, lie in C and span it.
    Rarr = np.array(R, dtype=np.int64)
    Rset = set(R)
    keep = np.array([a for a in range(ell) if a not in Rset], dtype=np.int64)
    ext = np.zeros((dim, ell), dtype=np.int64)
    for i, gi in enumerate(g):
        ext[i, keep] = gi
        ext[i, Rarr[i]] = 1
    for j, hr in enumerate(h):
        ext[P + j, keep] = hr
    _check(not np.any(_pairings(F, ext, W)),
           "a recovered vector, extended on the punctures, is not in the "
           "outer code")
    _check(F.rank(ext) == dim, "the recovered vectors do not span the "
                               "outer code")

    proved = delta - P
    _check(proved == bound(c), "internal: bound disagrees")
    side.update(_field_side_conditions(F, img, U))
    return {
        "bound": proved,
        "dual_distance": delta,
        "punctures": P,
        "n": n, "k": k, "N": N,
        "verified": [
            "columns are the construction's columns up to order",
            "inner map injective; every block decodes",
            "output wires are u * g_i, check wires x^j * h_r",
            "outer code and dual generator built from the points: "
            "orthogonal, ranks dim C and ell - dim C",
            "extended g_i and h_r lie in C and span it",
        ],
        "factory_side_conditions": side,
    }


def _field_side_conditions(F, img, U) -> dict:
    m = F.m

    def cubic(a, b, c):
        return F.trace(F.mul(F.mul(F.mul(a, b), c), a ^ b ^ c))

    identity = all(
        (int(np.sum(img[1 << x] & img[1 << y] & img[1 << z])) & 1)
        == cubic(1 << x, 1 << y, 1 << z)
        for x in range(m) for y in range(m) for z in range(m))
    compatible = (all(F.trace(u) == 1 for u in U)
                  and all(F.trace(F.mul(a, b)) == 0
                          for i, a in enumerate(U) for b in U[i + 1:])
                  and all(cubic(U[i], U[j], U[t]) == 0
                          for i in range(len(U))
                          for j in range(i + 1, len(U))
                          for t in range(j + 1, len(U))))
    return {"inner_map_identity_on_basis_triples": identity,
            "compatible_set_conditions": compatible}
