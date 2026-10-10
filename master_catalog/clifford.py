#!/usr/bin/env python3
"""The Clifford correction a factory needs, and whether it can be avoided.

A catalogued circuit is ``n`` parity rotations by ``pi/4`` -- each one a
``T = diag(1, w)``, ``w = e^{i pi/4}``, applied to the parity of a set of wires.
On a computational basis state ``|v>`` of the ``N`` wires they multiply in the
phase ``w^f(v)`` with

    f(v) = sum over columns c of |c . v|          (mod 8),

``|c . v|`` the parity of ``v`` on the wires of ``c``.  The row's ``gate`` names
the level-3 part of that phase and nothing else: ``T``, ``CS`` and ``CCZ``
factors on the outputs, each ``T_i = diag(1, w)``, ``CS_ij = diag(1,1,1,i)``,
``CCZ`` with its ``-1``.  What is left over,

    R(v) = f(v) - t(v),        t the phase of the gate as printed,

is a diagonal CLIFFORD on all ``N`` wires (proved below), and the factory has to
undo it -- after the rotations, before the checks are measured in the ``X``
basis.  Undoing it on a check wire is what makes an error-free run pass its
checks with certainty; undoing it on the outputs is what makes the output the
gate shown rather than the gate times a Clifford (``T-dagger`` instead of
``T``, for instance).  This module computes that correction, decides whether
it can be avoided altogether by running some rotations as ``T^3``, ``T^5`` or
``T^7 = T-dagger`` instead of ``T``, and checks both answers by evaluating the
logical action directly.

THE CORRECTION (Bravyi and Haah, PRA 86, 052329 (2012), Sec. III)
-----------------------------------------------------------------
Write ``g_q`` for the row of wire ``q`` -- the set of columns that contain it.
The parity of a sum expands by inclusion-exclusion,

    |a_1 + ... + a_m| = sum_i a_i - 2 sum_{i<j} a_i a_j
                        + 4 sum_{i<j<l} a_i a_j a_l - ... ,

with the ``t``-fold products carrying ``(-2)^(t-1)``, which vanishes mod 8 from
``t = 4`` on.  Summed over the columns this is

    f(v) = sum_q |g_q| v_q - 2 sum_{q<r} |g_q g_r| v_q v_r
           + 4 sum_{q<r<s} |g_q g_r g_s| v_q v_r v_s           (mod 8),

``g_q g_r`` the bitwise AND.  The gate is by definition the output monomials
whose overlap is ODD, and the factory condition (`faultcore.check_contamination`)
makes every overlap touching a check EVEN.  So in ``R``:

* the cubic terms cancel exactly (``4 * even`` and ``4 * odd - 4``);
* the coefficient of ``v_q v_r`` is ``-2|g_q g_r|``, less ``2`` for a ``CS``
  pair, which is ``0`` or ``4`` mod 8: a ``CZ`` when it is ``4``;
* the coefficient of ``v_q`` is ``|g_q|``, less ``1`` for a ``T`` output, which
  is even: ``2a`` is an ``S^a``.

The correction is ``e^{-i pi R / 4}``: ``S^p`` on wire ``q`` with
``p = -(|g_q| - [T_q]) / 2 mod 4`` (``S``, ``Z`` or ``S-dagger``), and ``CZ``
on every pair whose coefficient is ``4``.  It is unique: two corrections
giving the same accepted action differ by a diagonal Clifford that is the
identity, so this is THE correction of the stored circuit, which is why the
catalogue stores it literally and compares it literally.

AVOIDING IT: ROTATION POWERS
----------------------------
Running rotation ``c`` as ``T^(1 + 2 s_c)`` instead of ``T`` costs the same --
one magic state either way -- and adds ``2 s_c |c . v|`` to ``f``.  Expanding
that the same way, the correction disappears exactly when

    sum_{c contains q}    s_c = p_q        (mod 4)  for every wire q, and
    sum_{c contains q, r} s_c = [CZ_qr]    (mod 2)  for every pair q < r,

a linear system over ``Z_4`` in ``s``.  `rotation_powers` solves it (units
pivoted first, then the remaining even part over ``GF(2)``) and returns a
solution, or ``None`` when there is none -- and then the circuit needs ``S``
or ``CZ`` gates whatever powers its rotations run at.  For a one-output code
this is the distinction Jain and Albert draw between codes with a transversal
``T`` (``T^j`` on each qubit; their triply even and weak triply even codes) and
triorthogonal codes that need extra ``S`` and ``CZ`` gates (arXiv:2408.12752).
A solution is not unique, so it is checked, not compared: `logical_action`
must find that the powers alone give the gate.

THE INDEPENDENT CHECK
---------------------
`logical_action` does not use the expansion.  It evaluates ``f`` directly --
the actual parity of every column on every input it tries -- adds the
correction's phase and subtracts the gate's, and requires ``0 mod 8``.  The
inputs are every ``v`` when ``N <= 16``; otherwise every ``v`` of weight at most
3 where that is affordable, else at most 2, plus seeded random inputs of any
weight.  Weight 3 is complete: the residual is a polynomial of degree at most 3
in the ``v_q`` (the ``(-2)^(t-1)`` above), and such a polynomial vanishing at
every point of weight at most 3 is zero, by Moebius inversion.  Weight 2 is
complete given what `verify_catalog.derive` proves anyway -- the cubic
coefficients are ``4`` times the triple overlaps less the gate's ``CCZ`` terms,
zero exactly when the gate read-off and the factory condition hold.

`verify_catalog.statevector_problems` is the third implementation: for small
circuits it builds each rotation from CNOT ladders and a single-qubit ``T``,
applies the correction gate by gate, and checks that every output basis state
with the checks in ``|+>`` comes back as ``w^t(x)`` times itself.
"""
from __future__ import annotations

import itertools
import math
import random
from typing import Sequence

import numpy as np

#: Seed of the random inputs `logical_action` adds, so a rerun is identical.
_RNG_SEED = 20261010
#: Exhaustive evaluation up to this many wires (``2^16`` inputs).
EXHAUSTIVE_N = 16
#: Weight-3 inputs are tried while ``C(N,3) * n`` stays below this.
WEIGHT3_BUDGET = 400_000_000
#: Random inputs of any weight, on top of the structured ones.
RANDOM_INPUTS = 64
#: The phase of each gate factor, in units of ``pi/4``.
FACTOR_PHASE = {1: 1, 2: 2, 3: 4}
#: How a correction power is written: ``S^1``, ``S^2 = Z``, ``S^3 = S-dagger``.
S_NAMES = {1: "S", 2: "Z", 3: "S†"}


# ------------------------------------------------------------ the correction
def correction(rows: Sequence[int], k: int, N: int, gate) -> dict:
    """The diagonal Clifford that turns the rotations' phase into the gate.

    ``rows`` are the wires as bitmasks over columns
    (`faultcore.rows_over_columns`), ``gate`` the recovered monomial set
    (`faultcore.recover_gate`).  Returns ``{"S": [[q, p], ...], "CZ": [[q, r],
    ...]}`` -- apply ``S^p`` to wire ``q`` and ``CZ`` to each pair, after the
    rotations and before the checks are measured -- both lists sorted.

    Raises ``ValueError`` when a coefficient comes out non-Clifford, which
    happens only for a circuit that fails the factory condition or whose gate
    was not read off these rows: the caller has a bug, not a factory.
    """
    singles = {next(iter(m)) for m in gate if len(m) == 1}
    pairs = {tuple(sorted(m)) for m in gate if len(m) == 2}
    S = []
    for q in range(N):
        a = (rows[q].bit_count() - (q in singles)) % 8
        if a % 2:
            raise ValueError(f"wire {q}: |g_q| - [T_q] = {a} mod 8 is odd, so "
                             f"the residual phase is not Clifford")
        p = (-(a // 2)) % 4
        if p:
            S.append([q, p])
    CZ = []
    for q in range(N):
        rq = rows[q]
        if not rq:
            continue
        for r in range(q + 1, N):
            overlap = (rq & rows[r]).bit_count()
            b = (-2 * overlap - 2 * ((q, r) in pairs)) % 8
            if b % 4:
                raise ValueError(f"wires {q},{r}: the v_q v_r coefficient "
                                 f"{b} mod 8 is not a multiple of 4, so the "
                                 f"residual phase is not Clifford")
            if b == 4:
                CZ.append([q, r])
    return {"S": S, "CZ": CZ}


def is_trivial(corr: dict) -> bool:
    return not corr["S"] and not corr["CZ"]


def describe(corr: dict) -> str:
    """``S† on 0, Z on 3, CZ on (1,4)`` -- or ``none``."""
    parts = [f"{S_NAMES[p]} on {q}" for q, p in corr["S"]]
    parts += [f"CZ on ({q},{r})" for q, r in corr["CZ"]]
    return ", ".join(parts) if parts else "none"


# ------------------------------------------------------------ rotation powers
def _entry(row, j):
    return ((row[0] >> j) & 1) | (((row[1] >> j) & 1) << 1)


def _add(a, b):
    """``a + b`` for two ``Z_4`` vectors held as ``(low bits, high bits)``."""
    low = a[0] ^ b[0]
    return low, a[1] ^ b[1] ^ (a[0] & b[0])


def _minus_multiple(row, e, pivot):
    """``row - e * pivot`` over ``Z_4``, rows ``[low, high, rhs]``."""
    if e == 0:
        return row
    low, high = pivot[0], pivot[1]
    if e == 1:                                  # - pivot
        term, rhs = (low, high ^ low), -pivot[2]
    elif e == 2:                                # - 2 pivot = + 2 pivot
        term, rhs = (0, low), 2 * pivot[2]
    else:                                       # - 3 pivot = + pivot
        term, rhs = (low, high), pivot[2]
    new_low, new_high = _add((row[0], row[1]), term)
    return [new_low, new_high, (row[2] + rhs) % 4]


def rotation_powers(rows: Sequence[int], n: int, N: int, corr: dict):
    """Powers that make the correction unnecessary, or ``None`` if none do.

    Returns ``[[column, power], ...]`` for the rotations to run as ``T^power``
    (``power`` in 3, 5, 7), every other rotation staying a ``T``; ``[]`` when
    the correction is already trivial.  ``None`` is a proof: the ``Z_4`` system
    in the module docstring has no solution, so ``S`` or ``CZ`` gates are
    needed however the rotations are powered.

    A uniform power (every rotation ``T^3``, ``T^5`` or ``T^7``) is tried first,
    because it is the natural answer for a code with a strongly transversal
    ``T`` -- the 15-to-1 needs ``T-dagger`` on every rotation -- and then the
    general solver.
    """
    if is_trivial(corr):
        return []
    want = {q: p for q, p in corr["S"]}
    cz = {(q, r) for q, r in corr["CZ"]}
    for s in (1, 2, 3):
        if _uniform_works(rows, N, want, cz, s):
            return [[c, 1 + 2 * s] for c in range(n)]
    sigma = _solve(rows, n, N, want, cz)
    if sigma is None:
        return None
    return [[c, 1 + 2 * s] for c, s in enumerate(sigma) if s]


def _uniform_works(rows, N, want, cz, s):
    for q in range(N):
        if (s * rows[q].bit_count() - want.get(q, 0)) % 4:
            return False
    for q in range(N):
        for r in range(q + 1, N):
            if (s * (rows[q] & rows[r]).bit_count() - ((q, r) in cz)) % 2:
                return False
    return True


def _solve(rows, n, N, want, cz):
    """``s`` in ``Z_4^n`` solving the system, or ``None``."""
    # Phase 1: the wire equations, mod 4.  Pivot on UNIT entries only, keeping
    # every pivot column cleared from every other row, so what is left over
    # has even entries alone.
    pivots = []                                  # (column, [low, high, rhs])
    leftover = []
    for q in range(N):
        row = [rows[q], 0, want.get(q, 0)]
        for j, pivot in pivots:
            e = _entry(row, j)
            if e:
                row = _minus_multiple(row, e, pivot)
        if not row[0]:
            leftover.append(row)
            continue
        j = (row[0] & -row[0]).bit_length() - 1
        if _entry(row, j) == 3:                  # scale by 3 = -1
            row = [row[0], row[1] ^ row[0], (-row[2]) % 4]
        pivots = [(jj, _minus_multiple(p, _entry(p, j), row)) for jj, p in pivots]
        leftover = [_minus_multiple(L, _entry(L, j), row) for L in leftover]
        pivots.append((j, row))

    # Phase 2: what remains is 2 x (a GF(2) equation): the leftover wire rows,
    # and every pair equation, reduced mod 2 by the unit pivots.
    halves = []
    for low, high, rhs in leftover:
        if rhs % 2:
            return None                          # 2 x (...) = odd: no solution
        halves.append((high, rhs // 2))
    seen = {}
    for q in range(N):
        rq = rows[q]
        for r in range(q + 1, N):
            vector = rq & rows[r]
            z = 1 if (q, r) in cz else 0
            if not vector:
                if z:
                    return None
                continue
            if vector in seen:
                if seen[vector] != z:
                    return None
                continue
            seen[vector] = z
            halves.append((vector, z))
    pivot_mask = 0
    by_column = {}
    for j, (low, high, rhs) in pivots:
        pivot_mask |= 1 << j
        by_column[j] = (low, rhs % 2)
    basis = {}
    for vector, z in halves:
        hits = vector & pivot_mask
        while hits:
            lowest = hits & -hits
            plow, prhs = by_column[lowest.bit_length() - 1]
            vector ^= plow
            z ^= prhs
            hits ^= lowest
        while vector:
            top = vector.bit_length() - 1
            if top not in basis:
                basis[top] = (vector, z)
                break
            bv, bz = basis[top]
            vector ^= bv
            z ^= bz
        else:
            if z:
                return None
    # Back-substitute: the GF(2) part fixes s mod 2 on its pivot columns, free
    # columns are 0; then each unit pivot fixes its own column mod 4.
    bits = 0
    for top in sorted(basis):
        vector, z = basis[top]
        if ((vector & ~(1 << top) & bits).bit_count() + z) & 1:
            bits |= 1 << top
    sigma = [(bits >> c) & 1 for c in range(n)]
    for j, _row in pivots:
        sigma[j] = 0
    for j, (low, high, rhs) in pivots:
        total = rhs
        others = (low | high) & ~(1 << j)
        while others:
            lowest = others & -others
            c = lowest.bit_length() - 1
            total -= _entry((low, high), c) * sigma[c]
            others ^= lowest
        sigma[j] = total % 4
    return sigma


def powers_list(powers, n: int) -> list[int]:
    """The power of every rotation, from the sparse ``[[column, power]]`` form."""
    full = [1] * n
    for c, p in powers or []:
        full[c] = p
    return full


# ------------------------------------------------------- the logical action
def logical_action(columns, k: int, N: int, gate, corr=None, powers=None,
                   limit: int = 6) -> tuple[list[list[int]], str]:
    """Inputs on which the circuit, so corrected, is NOT exactly the gate.

    Runs rotation ``c`` as ``T^powers[c]`` (every one ``T`` when ``powers`` is
    ``None``), then the correction ``corr`` (none when ``None``), and compares
    the phase on each input against the gate's.  Returns ``(failures, scope)``:
    up to ``limit`` failing inputs, each as the list of wires set to 1, and a
    phrase saying which inputs were tried.  An empty list is the verdict that
    the logical action is the gate on all of them -- outputs AND checks: every
    phase on a check wire is accounted for too, so an error-free run passes its
    checks with certainty.

    The parity of every column is computed afresh on every input, from the
    columns; nothing here reads the overlaps `correction` expands into.
    """
    n = len(columns)
    G = np.zeros((N, n), dtype=np.bool_)
    for j, column in enumerate(columns):
        G[list(column), j] = True
    p = np.array(powers_list(powers, n), dtype=np.int64)
    # Everything but the rotations, as per-wire, per-pair and per-triple
    # phases in units of pi/4: the correction adds, the gate subtracts.
    single = np.zeros(N, dtype=np.int64)
    pair = np.zeros((N, N), dtype=np.int64)          # symmetric
    triple = {}
    for q, s in (corr or {}).get("S", []):
        single[q] += 2 * s
    for q, r in (corr or {}).get("CZ", []):
        pair[q, r] += 4
        pair[r, q] += 4
    for m in gate:
        wires = sorted(m)
        if len(wires) == 1:
            single[wires[0]] -= 1
        elif len(wires) == 2:
            pair[wires[0], wires[1]] -= 2
            pair[wires[1], wires[0]] -= 2
        else:
            triple[tuple(wires)] = -4
    failures: list[list[int]] = []

    def judge(rotations, extra, support):
        """``rotations`` = sum p_c |c.v| per input, ``extra`` the rest, and
        ``support(i)`` the wires input ``i`` sets -- asked only on failure."""
        bad = np.nonzero((rotations + extra) % 8)[0]
        for index in bad[:limit - len(failures)]:
            failures.append(sorted(int(q) for q in support(index)))
        return len(failures) >= limit

    # Integer arithmetic throughout.  A float product would go to BLAS, whose
    # thread pool costs more than it saves on thousands of small products.
    G64 = G.astype(np.int64)

    def parities_of(V):
        return (V @ G64) & 1

    def rotations_of(parity):
        return parity.astype(np.int64) @ p

    if N <= EXHAUSTIVE_N:
        # every input, as a matrix: the general form of every term
        V = np.array(list(itertools.product((0, 1), repeat=N)), dtype=np.int64)
        extra = V @ single + np.einsum("ij,ij->i", V @ pair, V) // 2
        for (a, b, c), phase in triple.items():
            extra += phase * (V[:, a] & V[:, b] & V[:, c])
        judge(rotations_of(parities_of(V)), extra, lambda i: np.nonzero(V[i])[0])
        return failures, "every input"

    weight3 = math.comb(N, 3) * n <= WEIGHT3_BUDGET
    scope = (f"every input of weight <= {3 if weight3 else 2} and "
             f"{RANDOM_INPUTS} random inputs")
    rng = random.Random(_RNG_SEED)
    V = np.array([[rng.randrange(2) for _ in range(N)]
                  for _ in range(RANDOM_INPUTS)], dtype=np.int64)
    extra = V @ single + np.einsum("ij,ij->i", V @ pair, V) // 2
    for (a, b, c), phase in triple.items():
        extra += phase * (V[:, a] & V[:, b] & V[:, c])
    if judge(rotations_of(parities_of(V)), extra, lambda i: np.nonzero(V[i])[0]):
        return failures, scope
    # weight 1 and 2: parities are rows of G and XORs of two rows
    if judge(rotations_of(G), single.copy(), lambda i: [i]):
        return failures, scope
    for q in range(N - 1):
        others = np.arange(q + 1, N)
        extra = single[q] + single[others] + pair[q, others]
        if judge(rotations_of(G[q + 1:] ^ G[q]), extra,
                 lambda i, q=q: [q, q + 1 + i]):
            return failures, scope
    if weight3:
        for q in range(N - 2):
            r, s = np.triu_indices(N - q - 1, 1)
            r, s = r + q + 1, s + q + 1
            extra = (single[q] + single[r] + single[s]
                     + pair[q, r] + pair[q, s] + pair[r, s])
            if triple:
                extra = extra + np.array([triple.get((q, int(a), int(b)), 0)
                                          for a, b in zip(r, s)], dtype=np.int64)
            if judge(rotations_of(G[r] ^ G[s] ^ G[q]), extra,
                     lambda i, q=q, r=r, s=s: [q, r[i], s[i]]):
                return failures, scope
    return failures, scope
