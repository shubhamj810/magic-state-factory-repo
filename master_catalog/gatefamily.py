#!/usr/bin/env python3
"""The gate family of a catalogue class: T only, CS only, CCZ only or mixed.

    python master_catalog/gatefamily.py              # counts per family
    python master_catalog/gatefamily.py LABEL ...    # the family and frame of some rows

A catalogue entry is a gate up to a CNOT frame on the outputs and diagonal
Cliffords (`glcanon`), but each row stores the gate in ONE frame. Whether the
gate is "T only", "CS only" or "CCZ only" is a property of the class, so it is
decided here over all frames: a gate is in the CS family when SOME frame shows
only CS gates, whatever the stored frame shows. 48.5.3.d, for example, is
stored as CS01·CS34·CCZ012·CCZ234 and is CS01·CS13·CS24·CS34 in another frame.

With ``tau`` the trilinear form of `glcanon` and ``beta(u, v) = tau(u, u, v)``
(the parity of the overlap of two output rows), the families are:

* **CCZ**: ``beta = 0``. Since ``beta`` is bilinear, this holds in one frame
  iff it holds in all, so the stored frame decides it.
* **T**: some frame has ``tau(b_i, b_j, b_l) = 0`` unless ``i = j = l``, so the
  gate is a product of T gates (outputs in the radical of ``tau`` carry
  nothing). Decided exactly, by algebra (`_t_frame`).
* **CS**: ``beta(u, u) = 0`` for every ``u``, ``beta != 0``, and some frame has
  ``tau(b_i, b_j, b_l) = 0`` for distinct ``i, j, l``. Decided by an exhaustive
  search over frames (`_cs_frame`) with a work budget.
* **mixed**: none of these.

The three named families are disjoint: T needs ``beta(u, u) = 1`` for some
``u``, CS needs ``beta(u, u) = 0`` for all ``u`` and ``beta != 0``, and CCZ
needs ``beta = 0``.

A frame is a list of ``k`` bitmasks ``b_0, ..., b_{k-1}`` over the stored
outputs, a basis of ``F_2^k``. The gate in that frame is ``f(sum_i y_i b_i)``:
new output ``i`` is the combination ``b_i`` of stored outputs, and the new
gate has tensor ``tau(b_i, b_j, b_l)``. `check_frame` re-derives that gate and
is all a reader needs to trust a stored frame. Only "mixed" and "undecided"
rest on the search.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import glcanon as G  # noqa: E402

FAMILIES = ("T", "CS", "CCZ", "mixed")
#: Nodes of the CS frame search before it gives up. At this budget every
#: catalogue row is decided in at most about a minute except 30.9.2.a.
CS_WORK_BUDGET = 5_000_000
_DECIDED: dict = {}


# ------------------------------------------------------------------ algebra
def _reduce(v: int, pivots: dict[int, int]) -> int:
    """``v`` reduced by an echelon basis ``{pivot bit: vector}``."""
    while v:
        top = v.bit_length() - 1
        if top not in pivots:
            return v
        v ^= pivots[top]
    return 0


def _kernel(images: list[int], k: int) -> list[int]:
    """A basis of ``{u in F_2^k : XOR of images[a] over a in u = 0}``."""
    pivots: dict[int, tuple[int, int]] = {}      # pivot bit -> (image, combination)
    out = []
    for a in range(k):
        v, comb = images[a], 1 << a
        while v:
            top = v.bit_length() - 1
            if top not in pivots:
                break
            pv, pc = pivots[top]
            v, comb = v ^ pv, comb ^ pc
        if v:
            pivots[v.bit_length() - 1] = (v, comb)
        else:
            out.append(comb)
    return out


def _rank(vectors) -> int:
    pivots: dict[int, int] = {}
    for v in vectors:
        v = _reduce(v, pivots)
        if v:
            pivots[v.bit_length() - 1] = v
    return len(pivots)


def _complement(sub: list[int], k: int) -> list[int]:
    """Unit vectors that extend the basis ``sub`` to a basis of ``F_2^k``."""
    pivots: dict[int, int] = {}
    for v in sub:
        v = _reduce(v, pivots)
        pivots[v.bit_length() - 1] = v
    out = []
    for a in range(k):
        v = _reduce(1 << a, pivots)
        if v:
            pivots[v.bit_length() - 1] = v
            out.append(1 << a)
    return out


def _slice(T, u: int, v: int) -> int:
    """The bitmask ``m`` with ``tau(u, v, w) = parity(w & m)``."""
    acc = 0
    for a in G._bits(u):
        row = T[a]
        for b in G._bits(v):
            acc ^= row[b]
    return acc


def _tau(T, u: int, v: int, w: int) -> int:
    return (_slice(T, u, v) & w).bit_count() & 1


def radical(k: int, T) -> list[int]:
    """A basis of the radical of ``tau``: ``u`` with ``tau(u, ., .) = 0``."""
    flat = [sum(T[a][b] << (b * k) for b in range(k)) for a in range(k)]
    return _kernel(flat, k)


def gate_in_frame(k: int, T, frame: list[int]) -> list[tuple[int, ...]]:
    """The monomials of the gate ``f(sum_i y_i b_i)``, read off ``tau`` on the frame."""
    out = []
    for i in range(k):
        if _tau(T, frame[i], frame[i], frame[i]):
            out.append((i,))
    for i in range(k):
        for j in range(i + 1, k):
            if _tau(T, frame[i], frame[i], frame[j]):
                out.append((i, j))
    for i in range(k):
        for j in range(i + 1, k):
            m = _slice(T, frame[i], frame[j])
            for l in range(j + 1, k):
                if (m & frame[l]).bit_count() & 1:
                    out.append((i, j, l))
    return out


def kind_of(monos) -> str:
    """``T``, ``CS``, ``CCZ`` or ``mixed`` for a monomial set in its own frame."""
    sizes = {len(m) for m in monos}
    return {frozenset({1}): "T", frozenset({2}): "CS", frozenset({3}): "CCZ"}.get(
        frozenset(sizes), "mixed")


# ------------------------------------------------------------------ T family
def _t_frame(k: int, T, rad: list[int]) -> list[int] | None:
    """A frame in which the gate is T on ``w`` outputs and nothing on the rest,
    or None when there is none.

    Let ``W`` be a complement of the radical ``R``. If such a frame exists,
    ``beta`` is nondegenerate on ``W`` (in the frame it is the dot product on
    the T outputs). Then ``x o y``, defined on ``W`` by
    ``beta(x o y, z) = tau(x, y, z)`` for all ``z``, is a commutative product
    with ``x o x = x`` (because ``beta(x, z) = tau(x, x, z)``). In a T frame it
    is the coordinatewise product, so it is associative. Conversely, an
    associative commutative product with ``x o x = x`` on a finite space is a
    Boolean ring, isomorphic to ``F_2^w`` with the coordinatewise product, and
    its ``w`` primitive idempotents ``p_i`` satisfy ``p_i o p_j = 0`` for
    ``i != j``. Then ``tau(p_i, p_j, z) = beta(p_i o p_j, z) = 0`` for
    ``i != j``, which is a T frame. So the test is: ``beta`` nondegenerate on
    ``W`` and ``o`` associative; the frame is the primitive idempotents. The
    caller still checks the frame with `gate_in_frame`.
    """
    W = _complement(rad, k)
    w = len(W)
    if w == 0:
        return None
    beta = [T[a][a] for a in range(k)]          # beta(e_a, .) as a mask

    def beta_vec(x):
        acc = 0
        for a in G._bits(x):
            acc ^= beta[a]
        return acc

    # Gram matrix of beta on W, inverted by elimination
    gram = [sum(((beta_vec(W[i]) & W[j]).bit_count() & 1) << j for j in range(w)) for i in range(w)]
    aug = [(gram[i], 1 << i) for i in range(w)]
    for col in range(w):
        piv = next((r for r in range(col, w) if aug[r][0] >> col & 1), None)
        if piv is None:
            return None                         # beta degenerate on W
        aug[col], aug[piv] = aug[piv], aug[col]
        for r in range(w):
            if r != col and aug[r][0] >> col & 1:
                aug[r] = (aug[r][0] ^ aug[col][0], aug[r][1] ^ aug[col][1])
    inv = [aug[i][1] for i in range(w)]          # rows of gram^-1 (gram is symmetric)

    # structure constants: W_i o W_j as a coordinate vector over W
    def prod_coords(ci: int, cj: int) -> int:
        x = 0
        for i in G._bits(ci):
            x ^= W[i]
        y = 0
        for j in G._bits(cj):
            y ^= W[j]
        m = _slice(T, x, y)
        rhs = sum(((m & W[j]).bit_count() & 1) << j for j in range(w))
        # z = sum_j z_j W_j with gram z = rhs
        return sum(((inv[i] & rhs).bit_count() & 1) << i for i in range(w))

    table = [[prod_coords(1 << i, 1 << j) for j in range(w)] for i in range(w)]

    def mul(a: int, b: int) -> int:
        acc = 0
        for i in G._bits(a):
            for j in G._bits(b):
                acc ^= table[i][j]
        return acc

    for i in range(w):
        for j in range(i, w):
            for l in range(w):
                if mul(table[i][j], 1 << l) != mul(1 << i, table[j][l]):
                    return None                 # not associative: no T frame
    # the unit: solve e o W_l = W_l for every l (linear in e)
    rows = []
    for l in range(w):
        for bit in range(w):
            lhs = sum(((table[i][l] >> bit) & 1) << i for i in range(w))
            rows.append((lhs, (1 << l) >> bit & 1))
    unit = _solve(rows, w)
    if unit is None:
        return None
    idem = [unit]
    for i in range(w):
        nxt = []
        for e in idem:
            a = mul(e, 1 << i)
            for part in (a, e ^ a):
                if part:
                    nxt.append(part)
        idem = nxt
    if len(idem) != w:
        return None
    frame = []
    for c in sorted(idem):
        x = 0
        for i in G._bits(c):
            x ^= W[i]
        frame.append(x)
    return frame + sorted(rad)


def _solve(rows: list[tuple[int, int]], w: int) -> int | None:
    """One solution x of ``parity(lhs & x) = rhs`` for every row, or None."""
    pivots: dict[int, tuple[int, int]] = {}
    for lhs, rhs in rows:
        while lhs:
            top = lhs.bit_length() - 1
            if top not in pivots:
                break
            pl, pr = pivots[top]
            lhs, rhs = lhs ^ pl, rhs ^ pr
        if lhs:
            pivots[lhs.bit_length() - 1] = (lhs, rhs)
        elif rhs:
            return None
    x = 0
    for top in sorted(pivots):
        lhs, rhs = pivots[top]
        if ((lhs ^ (1 << top)) & x).bit_count() & 1 != rhs:
            x |= 1 << top
    return x


# ------------------------------------------------------------------ CS family
class _OutOfWork(Exception):
    pass


def _cs_frame(k: int, T, rad: list[int], budget: int) -> list[int] | None | bool:
    """A frame in which the gate has no T and no CCZ, False if there is none,
    None if the search ran out of budget.

    Work modulo the radical: choose ``w`` vectors of a complement ``W``,
    independent, with ``tau(b_i, b_j, b_l) = 0`` for distinct ``i, j, l``
    (``tau(b, b, b) = beta(b, b) = 0`` holds already). Each condition on the
    next vector ``v`` is linear in ``v`` (``parity(v & slice(b_i, b_j)) = 0``),
    so the allowed vectors form a subspace; a node is cut when that subspace
    cannot complete a basis. Vectors are chosen in increasing order of their
    coordinates over ``W``, so each set is visited once. Exhaustive within the
    budget.
    """
    W = _complement(rad, k)
    w = len(W)

    def vec(c: int) -> int:
        x = 0
        for i in G._bits(c):
            x ^= W[i]
        return x

    vecs = [vec(c) for c in range(1 << w)]
    # slice(x, y) restricted to W, in W coordinates
    def wmask(m: int) -> int:
        return sum(((m & W[j]).bit_count() & 1) << j for j in range(w))

    work = [0]

    def rec(chosen: list[int], masks: list[int]):
        if len(chosen) == w:
            return list(chosen)
        # allowed coordinates c: parity(c & m) = 0 for every m in masks
        allowed_basis = _kernel_of_masks(masks, w)
        if _rank(chosen + allowed_basis) < w:
            return False
        last = chosen[-1] if chosen else 0
        for c in _span_above(allowed_basis, last):
            work[0] += 1
            if work[0] > budget:
                raise _OutOfWork
            if _rank(chosen + [c]) == len(chosen):
                continue
            new = [wmask(_slice(T, vecs[s], vecs[c])) for s in chosen]
            got = rec(chosen + [c], masks + new)
            if got:
                return got
        return False

    try:
        found = rec([], [])
    except _OutOfWork:
        return None
    if not found:
        return False
    return [vecs[c] for c in found] + sorted(rad)


def _kernel_of_masks(masks: list[int], w: int) -> list[int]:
    """A basis of ``{c in F_2^w : parity(c & m) = 0 for every m}``."""
    pivots: dict[int, int] = {}
    for m in masks:
        # keep every row fully reduced, so the free/pivot split below is valid
        for p, row in pivots.items():
            if m >> p & 1:
                m ^= row
        if m:
            top = m.bit_length() - 1
            for key in list(pivots):
                if pivots[key] >> top & 1:
                    pivots[key] ^= m
            pivots[top] = m
    out = []
    for f in range(w):
        if f in pivots:
            continue
        c = 1 << f
        for p, row in pivots.items():
            if row >> f & 1:
                c |= 1 << p
        out.append(c)
    return out


def _span_above(basis: list[int], last: int):
    """The elements of span(basis) greater than ``last``, in increasing order."""
    elems = [0]
    for g in basis:
        elems += [e ^ g for e in elems]
    return sorted(e for e in elems if e > last)


# ------------------------------------------------------------------ the decision
def decide(k: int, monomials, budget: int = CS_WORK_BUDGET) -> dict:
    """``{"family": T|CS|CCZ|mixed|None, "frame": [k bitmasks] or None,
    "gate": monomials in that frame or None}``.

    ``frame`` is None when the stored frame already shows the family (or the
    family is mixed or undecided). ``family`` None means the CS search ran out
    of budget; the row then counts as mixed, its stored kind.
    """
    monos = [tuple(sorted(m)) for m in monomials]
    key = (k, tuple(sorted(monos)), budget)
    if key not in _DECIDED:
        _DECIDED[key] = _decide(k, monos, budget)
    found = _DECIDED[key]
    return {"family": found["family"], "frame": list(found["frame"]) if found["frame"] else None,
            "gate": list(found["gate"]) if found["gate"] else None}


def _decide(k: int, monos, budget: int) -> dict:
    stored = kind_of(monos)
    if stored != "mixed":
        return {"family": stored, "frame": None, "gate": None}
    T = G.tensor(k, monos)
    beta = [T[a][a] for a in range(k)]
    if not any(beta):
        return {"family": "CCZ", "frame": None, "gate": None}   # cannot happen for a mixed gate
    rad = radical(k, T)
    has_t = any(T[a][a] >> a & 1 for a in range(k))
    if has_t:
        frame = _t_frame(k, T, rad)
        family = "T"
    else:
        frame = _cs_frame(k, T, rad, budget)
        family = "CS"
        if frame is None:
            return {"family": None, "frame": None, "gate": None}
    if not frame:
        return {"family": "mixed", "frame": None, "gate": None}
    gate = gate_in_frame(k, T, frame)
    if kind_of(gate) != family or _rank(frame) != k:
        raise AssertionError(f"a {family} frame failed its own check")
    return {"family": family, "frame": frame, "gate": gate}


def check_frame(k: int, monomials, frame: list[int], family: str) -> list[str]:
    """Problems with a stored frame (empty when it is good): it must be a basis
    of ``F_2^k``, and the gate in it must be of ``family``."""
    problems = []
    if len(frame) != k or any(not 0 < b < (1 << k) for b in frame):
        return [f"the frame is not {k} nonzero vectors on {k} outputs"]
    if _rank(frame) != k:
        problems.append("the frame is not a basis")
    gate = gate_in_frame(k, G.tensor(k, [tuple(sorted(m)) for m in monomials]), frame)
    if kind_of(gate) != family:
        problems.append(f"in the frame the gate is {kind_of(gate)}, not {family}")
    return problems


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    import catalogfile as CF
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "website"))
    rows = CF.load_all()["factories"]
    if argv:
        rows = [r for r in rows if r["catalog_label"] in argv]
    counts: dict = {}
    for r in rows:
        fam = r.get("gate_family")
        counts[fam] = counts.get(fam, 0) + 1
        if argv:
            print(r["catalog_label"], fam, r.get("gate_family_frame"), r.get("gate_family_human"))
    if not argv:
        print(counts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
