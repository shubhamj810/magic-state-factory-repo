#!/usr/bin/env python3
"""Circuits given by a rule instead of a list of columns.

Most rows of the catalogue store their circuit as ``columns``.  Some are kept
as a rule instead, to hold ``master_catalog.json`` under GitHub's recommended
50 MB: the two-group circuits of the Borrowed Identities large sweep reach
65,534 rotations, and storing the 127 longest would take the file to about
99 MB, at GitHub's 100 MB hard limit; the 470 of the larger unified search, up
to 262,142 rotations, would take it past 50 MB.  Such a row is
kept in ``master_catalog_large.json`` with a ``construction`` -- a small object
naming a family and its parameters -- and this module turns it back into the
columns, which every other tool then reads exactly as it reads a stored circuit.

THE CONTRACT
------------
`columns` returns the circuit in ONE fixed order: every column sorted
ascending, and the list of columns sorted lexicographically.  That order is
part of the format.  ``d_witness`` and ``rotation_powers`` name columns by
position, so a row is only meaningful together with this order, and
``columns_sha256`` -- the SHA-256 of `canonical_text` of the columns, stored on
every such row -- pins it: if this module ever produced a different list, the
stored digest would stop matching and the verifier would say so, rather than
quietly verifying some other circuit.

Nothing here checks that the result is a factory.  That is the verifier's job,
done on the columns this returns, the same way as for a stored circuit.

THE FAMILIES
------------
``two-group``
    ``{"family": "two-group", "k": k, "N": N, "s_total": a, "s_O": b}``.  The
    circuits of Singh, Gidney and Jones (arXiv:2606.28518), symmetric within
    the ``k`` output wires ``0..k-1`` and within the ``N - k`` check wires.
    Every rotation has coefficient 1 at level 3 (one ``T``), and a column is
    every ``A | B``, ``A`` a set of outputs and ``B`` a non-empty set of
    checks, with

        |A| = 0  or  |A| = 1 (mod b),        and   |A| + |B| = 1 (mod a).

    This is ``Two_group.build_gate_set`` (``W_O``, ``W_total``, ``s_S = 1``)
    expanded the way ``unified_search.two_group_gates`` expands it, with the
    output-only gates (``B`` empty) left out, written again here from the
    definition rather than imported; `borrowed_identities/tests/test_unified.py`
    compares the two on every level-3 row of the upstream large sweep.
"""
from __future__ import annotations

import hashlib
import json
from itertools import combinations

FAMILIES = ("two-group",)

#: The fields of each family's construction object and their meaning, which
#: the large file's header repeats so a reader of the JSON alone can rebuild a
#: circuit.
FAMILY_FIELDS = {
    "two-group": ("k", "N", "s_total", "s_O"),
}
FAMILY_DESCRIPTIONS = {
    "two-group": (
        "Singh, Gidney and Jones (arXiv:2606.28518): outputs 0..k-1, checks "
        "k..N-1; one T rotation on A | B for every set A of outputs and every "
        "non-empty set B of checks with (|A| = 0 or |A| = 1 mod s_O) and "
        "|A| + |B| = 1 mod s_total; columns sorted ascending, then the list "
        "sorted lexicographically"),
}

#: Bounds that keep a malformed construction from being expanded at all: a
#: two-group circuit on N wires has up to 2^N - 1 columns, so N is what decides
#: the cost.  Every circuit this file holds has N <= 18, which is 262,143
#: columns at most and well under a second; N = 20 would already be a million.
MAX_WIRES = 18


def problems(construction) -> list[str]:
    """What is wrong with the SHAPE of a construction; empty if nothing.

    Checked before `columns` is called, so a hand-edited or corrupted object
    is a named rejection and never a crash or an enormous loop.
    """
    if not isinstance(construction, dict):
        return [f"the construction is a {type(construction).__name__}, not "
                f"an object"]
    family = construction.get("family")
    if family not in FAMILIES:
        return [f"unknown construction family {family!r}; this catalogue "
                f"knows {', '.join(FAMILIES)}"]
    fields = FAMILY_FIELDS[family]
    found = [name for name in construction if name != "family"]
    if sorted(found) != sorted(fields):
        return [f"a {family} construction has the fields "
                f"{', '.join(fields)}, not {', '.join(sorted(found))}"]
    out = []
    for name in fields:
        value = construction[name]
        if type(value) is not int or value < 1:
            out.append(f"{name} must be a positive whole number, not "
                       f"{value!r}")
    if out:
        return out
    k, N = construction["k"], construction["N"]
    if not k < N <= MAX_WIRES:
        out.append(f"need 1 <= k < N <= {MAX_WIRES}, not k={k}, N={N}")
    return out


def columns(construction) -> list[list[int]]:
    """The circuit, in the order the contract above fixes."""
    wrong = problems(construction)
    if wrong:
        raise ValueError("; ".join(wrong))
    family = construction["family"]
    if family == "two-group":
        return _two_group(construction["k"], construction["N"],
                          construction["s_total"], construction["s_O"])
    raise AssertionError(family)                  # `problems` lets no other


def _two_group(k, N, s_total, s_O):
    outputs, checks = range(k), range(k, N)
    out = []
    for a in range(k + 1):
        if a and (a - 1) % s_O:
            continue
        for b in range(1, N - k + 1):
            if (a + b - 1) % s_total:
                continue
            for A in combinations(outputs, a):
                for B in combinations(checks, b):
                    out.append(list(A + B))
    out.sort()
    return out


def canonical_text(cols) -> str:
    """The text ``columns_sha256`` is computed over: compact JSON."""
    return json.dumps(cols, separators=(",", ":"))


def digest(cols) -> str:
    return hashlib.sha256(canonical_text(cols).encode("ascii")).hexdigest()
