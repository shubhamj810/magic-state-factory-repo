"""Exact minimal T-count and phase-polynomial degree for catalogue entries.

Two independent invariants of the diagonal gate a factory deposits:

  * poly_degree -- the CNOT-frame-reduced algebraic degree of the phase
    polynomial, via `factorylib.degree.reduced_degree` with one canonical
    generator per gate (T->1, CS->2, CCZ->3, CCCZ->4; sqrt(T)->1).  This is
    the degree AFTER minimising over output frames, so it is <= the largest
    gate arity written in the gate string and usually strictly less: on the
    n <= 38 catalogue it differs from that row's `max_level` on 49 of the 74
    rows, and no row there has reduced degree 3 (see the CNOT-frame section
    below).

  * t_count -- the EXACT minimal T-count of the level-3 (Z_8) diagonal gate,
    via `factorylib.tcount.tcount_rm` (Amy--Mosca / Reed--Muller minimum-weight
    coset leader).  Defined for gates whose phases are all multiples of pi/4:
        T/CS/CCZ           -> the number the decoder returns
        S/CZ  (Clifford)   -> 0
    Not defined (t_count = None, with a note) for
        sqrt(T)            -> pi/8 rotation; not exactly synthesizable in Clifford+T
        CT / CCS / CCCZ    -> not in the k-qubit level-3 diagonal group generated
                              by pi/4 parity rotations (the Z_8 system is
                              inconsistent on these k qubits; they need ancillas)

Two gate encodings are supported:
  * named  : '.'-separated named gates, 0-indexed  (catalog/factories.json
             `output_gate`, e.g. 'CS01 . CS02 . CCZ012')
  * monomials: '+'-separated F2 monomials, digit strings (classification_frontier
             `gate`, e.g. '012+013'); degree d monomial == the canonical
             arity-d gate on that support.

(The degree routine referenced above lives in ``factorylib.degree`` as
`reduced_degree`; see the CNOT-frame section comment below for the current
reduced-degree semantics.)
"""
import json
from pathlib import Path
from itertools import product
from math import prod

import re                                                       # noqa: E402
from tcount import NotInGroup, tcount_rm, _remap
from degree import reduced_degree, _deg_after

# ------------------------------------------------ named-gate -> Z_8 phase polynomial
# (self-contained; formerly audit_flag2.poly_from_decomp).  Covers the full catalog
# gate vocabulary, not just the T/CS/CCZ the T-count self-test needs.
MOD = 8

# Z_8 coefficient deposited on the all-ones subset of a gate's support.
_GATE_COEFF = {
    "T": 1,     # pi/4 on 1 qubit
    "S": 2,     # pi/2 on 1 qubit  (Clifford)
    "CS": 2,    # pi/2 on 2 qubits
    "CZ": 4,    # pi   on 2 qubits (Clifford)
    "CCZ": 4,   # pi   on 3 qubits
    "CT": 1,    # pi/4 on 2 qubits (controlled-T)
    "CCS": 2,   # pi/2 on 3 qubits (controlled-controlled-S)
    "CCCZ": 4,  # pi   on 4 qubits
}
_TOKEN_RE = re.compile(r"^([A-Za-z]+)([0-9]+)$")


class NotLevel3Error(ValueError):
    """Raised for gates whose phases are not multiples of pi/4 (e.g. sqrt(T))."""


def poly_from_decomp(decomp_str):
    """'T0 . CS01' or 'T1 CS12' -> (P, qs); Z_8 coefficients summed mod 8."""
    P, qs = {}, set()
    if decomp_str is None:
        return P, qs
    for tok in decomp_str.replace(".", " ").split():
        m = _TOKEN_RE.match(tok)
        if not m:
            raise ValueError(f"unparseable gate token: {tok!r}")
        name, digits = m.group(1), m.group(2)
        if name not in _GATE_COEFF:
            if name.lower().startswith("sqrt"):
                raise NotLevel3Error(f"{tok!r}: pi/8 rotation, not a level-3 (Z_8) gate")
            raise ValueError(f"unknown gate {name!r} in token {tok!r}")
        support = frozenset(int(ch) for ch in digits)
        qs |= support
        P[support] = (P.get(support, 0) + _GATE_COEFF[name]) % MOD
    return {S: c for S, c in P.items() if c % MOD}, qs

# Z_8 coefficient of the canonical arity-d generator (T, CS, CCZ, C3Z, ...)
_CANON_COEFF = {1: 1, 2: 2, 3: 4}   # 2^{d-1} mod 8; degree>=4 handled below

# --------------------------------------------- CNOT-frame-reduced degree machinery
#
# The catalogue's `poly_degree` is now the *reduced* (Clifford-reduced, CNOT-frame-
# minimised) phase-polynomial degree: the minimum over output CNOT frames M in
# GL(k,2) of the in-frame genuine degree of the deposited gate
# (poly_degree.reduced_degree).  ZZ(pi/4) -> 1, CS -> 2, CCZ -> 3; Clifford
# gates (S, CZ) -> 0.  This is strictly <= the old "max gate arity" degree.
#
# reduced_degree enumerates GL(k,2) (~2^{k^2}), so we cap exact enumeration and fall
# back to a bounded random-frame search (an UPPER bound) beyond it.  Results are
# memoised, keyed by (L, sorted supports), in a persistent JSON cache so the
# expensive k=5 scans run once.
_DEG_CAP = 2.0e7                     # exact up to |GL(5,2)| = 9,999,360
_DEG_SAMPLES = 2_000_000             # bounded-search frame budget for k>=6
_DEG_SEED = 20260721
_CACHE_PATH = Path(__file__).with_name("reduced_degree_cache.json")
try:
    _DEG_CACHE = json.loads(_CACHE_PATH.read_text(encoding="utf-8"))
except (OSError, ValueError):
    _DEG_CACHE = {}


def _build_P(supports, L):
    """P[S] = sum of 2^{|S|-1} per gate on support S, mod 2^L (canonical arity-d gate)."""
    mod = 1 << L
    P = {}
    for m in supports:
        S = frozenset(m)
        if not S:
            continue
        P[S] = (P.get(S, 0) + (1 << (len(S) - 1))) % mod
    return {S: c for S, c in P.items() if c % mod}


def _remap0(P):
    """Relabel the qubits actually used by P to 0..k-1 (the reduced degree is
    relabel-invariant: a permutation is itself a GL(k,2) frame)."""
    qs = sorted({q for S in P for q in S})
    idx = {q: i for i, q in enumerate(qs)}
    return {frozenset(idx[q] for q in S): c for S, c in P.items()}, len(qs)


def _gl_size(k):
    """|GL(k,2)| = prod_{i<k} (2^k - 2^i)."""
    return prod((1 << k) - (1 << i) for i in range(k))


def _lcg(seed):
    """64-bit LCG (Knuth MMIX constants): deterministic frame sampling, so the
    bounded-search results are reproducible (no wall-clock randomness)."""
    x = seed & 0xFFFFFFFFFFFFFFFF
    while True:
        x = (6364136223846793005 * x + 1442695040888963407) & 0xFFFFFFFFFFFFFFFF
        yield x >> 11


def _random_invertible(k, rng):
    """Uniform random element of GL(k,2) by rejection (tuple of column ints)."""
    while True:
        cols = [next(rng) & ((1 << k) - 1) for _ in range(k)]
        b, ok = [], True
        for v in cols:
            w = v
            for e in b:
                w = min(w, w ^ e)
            if w == 0:
                ok = False
                break
            b.append(w)
        if ok:
            return tuple(cols)


def _bounded_degree(P, k, L, samples):
    """UPPER bound on the reduced degree: min in-frame genuine degree over the
    identity frame plus `samples` LCG-random invertible frames."""
    mod = 1 << L
    tab = {b: sum(c for S, c in P.items()
                  if S <= frozenset(i for i in range(k) if b[i])) % mod
           for b in product((0, 1), repeat=k)}
    best = _deg_after(tab, k, tuple(1 << j for j in range(k)), L)
    rng = _lcg(_DEG_SEED)
    for _ in range(samples):
        d = _deg_after(tab, k, _random_invertible(k, rng), L)
        if d < best:
            best = d
            if best <= 1:
                break
    return best


def reduced_poly_degree(supports, L):
    """CNOT-frame-reduced phase-polynomial degree of the gate with the given supports
    at level L.  Returns (degree, note): note is set only when the exact GL(k,2)
    enumeration was infeasible and a bounded random-frame upper bound was used."""
    P = _build_P(supports, L)
    if not P:
        return 0, None
    Pr, k = _remap0(P)
    key = f"{L}|" + repr(sorted(tuple(sorted(S)) for S in Pr))
    if key in _DEG_CACHE:
        e = _DEG_CACHE[key]
        return e["deg"], e.get("note")
    g = _gl_size(k)
    if g <= _DEG_CAP:
        deg, note = reduced_degree(Pr, k, L), None
    else:
        deg = _bounded_degree(Pr, k, L, _DEG_SAMPLES)
        # deg <= 1 is the provable floor (0 = Clifford, 1 = minimal non-Clifford), so
        # the bounded search is exact there; only deg >= 2 is a genuine upper bound.
        note = None if deg <= 1 else (
            f"reduced degree is an UPPER BOUND: |GL({k},2)|={g:.3g} too large for "
            f"exact enumeration; min over identity + {_DEG_SAMPLES:,} random frames")
    _DEG_CACHE[key] = {"deg": deg, "note": note}
    try:
        _CACHE_PATH.write_text(json.dumps(_DEG_CACHE, indent=1), encoding="utf-8")
    except OSError:
        pass
    return deg, note

# note strings for the two "no finite level-3 T-count" cases
_NOTE_PI8 = ("pi/8 rotation (sqrt(T)-type); not a level-3 (Z_8) diagonal gate "
             "and not exactly synthesizable in Clifford+T")
_NOTE_NOTIN = ("gate is not in the k-qubit level-3 diagonal group generated by "
               "pi/4 parity rotations (Z_8 system inconsistent; needs ancillas)")


def _degree_from_supports(supports, level):
    """CNOT-frame-reduced phase-polynomial degree from a list of gate supports,
    evaluated at the factory's level L (so an arity-d gate carries coeff 2^{d-1}
    mod 2^L).  Returns (degree, note)."""
    supports = [tuple(sorted(s)) for s in supports if s]
    if not supports:
        return 0, None
    L = max(level, max(len(s) for s in supports), 1)
    return reduced_poly_degree(supports, L)


def _tcount_from_P(P):
    """Exact minimal T-count from a Z_8 poly {frozenset(support): coeff}; None if
    the gate is not in the k-qubit level-3 diagonal group."""
    if not P:
        return 0, None
    Pr, k = _remap(P)
    try:
        return tcount_rm(Pr, k), None
    except NotInGroup:
        # factorylib.tcount._solve_z8 signals "M a == fvec unsolvable over Z_8",
        # i.e. the gate is outside the pi/4 parity-rotation group.
        return None, _NOTE_NOTIN


# ----------------------------------------------------------------- named gates
def metrics_from_named(output_gate, level=3):
    """(t_count, t_count_note, poly_degree, poly_degree_note) for a '.'-separated
    named-gate string on a factory of the given level."""
    if not output_gate:
        return 0, None, 0, None
    # phase-polynomial degree: CNOT-frame-reduced, one canonical generator per gate
    supports = []
    for tok in output_gate.replace(".", " ").split():
        digits = "".join(ch for ch in tok if ch.isdigit())
        supports.append(tuple(int(ch) for ch in digits))
    deg, deg_note = _degree_from_supports(supports, level)

    # exact minimal T-count (level-3 Z_8)
    try:
        P, _ = poly_from_decomp(output_gate)
    except NotLevel3Error:
        return None, _NOTE_PI8, deg, deg_note
    tc, note = _tcount_from_P(P)
    return tc, note, deg, deg_note


# ------------------------------------------------------------- F2 monomials
def _parse_monomials(gate):
    if gate in ("", "0empty", None):
        return []
    return [tuple(int(ch) for ch in tok.strip())
            for tok in gate.split("+") if tok.strip()]


def metrics_from_monomials(gate, level=3):
    """(t_count, t_count_note, poly_degree, poly_degree_note) for a '+'-separated
    monomial string (frontier classes are all level-3 T/CS/CCZ)."""
    mons = _parse_monomials(gate)
    if not mons:
        return 0, None, 0, None
    deg, deg_note = _degree_from_supports(mons, level)
    # each degree-d monomial is the canonical arity-d gate (coeff 2^{d-1} mod 8)
    P = {}
    for m in mons:
        d = len(m)
        coeff = _CANON_COEFF.get(d, (1 << (d - 1)) % MOD)
        S = frozenset(m)
        P[S] = (P.get(S, 0) + coeff) % MOD
    P = {S: c for S, c in P.items() if c % MOD}
    tc, note = _tcount_from_P(P)
    return tc, note, deg, deg_note
