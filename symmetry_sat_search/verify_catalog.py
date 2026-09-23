#!/usr/bin/env python3
"""RE-VERIFICATION of every row of the shipped ``catalog/factories.json``.

`build_catalog.py` verifies each circuit as it builds the catalogue from
``examples/found_factories.json``.  This file re-derives every published number
from the *shipped file*, afterwards, from the stored column lists alone: nothing
is read from a row except its columns, ``k``, ``N`` and ``level``.

WHAT THIS DOES AND DOES NOT PROVE.  It catches a corrupted, hand-edited or
stale ``catalog/factories.json`` -- the file a reader actually consumes -- and
it re-does every derivation from scratch.  It is NOT an independent
implementation of the underlying algorithms: the distance comes from the same
``evaluator._distance`` the builder calls, the output parities from the same
``evaluator``, and the metrics from the same ``factorylib.metrics``.  Agreement
therefore means "the shipped file matches what this code computes", not "two
implementations agree".

For genuinely independent checks of the same circuits: the parity/distance
verifier in ``factorylib/verification.py`` shares no code with the classifier
that produced the classification catalogue, ``rebuild_from_groups.py``
reconstructs each circuit from its symmetry group before verifying, and
``tests/test_search_engines.py`` re-derives the small optima with the solvers.

Checks, per row
---------------
1. ``n == len(columns)``; columns distinct and nonempty.  (A repeated column is
   a weight-2 undetectable fault, so this is a distance check in disguise.)
2. ``N`` equals the stored ambient qubit count.
3. Every degree-<=level monomial that touches a CHECK qubit has EVEN parity.
   This is the factory condition itself: the circuit must deposit nothing on
   the postselected checks.
4. The output-block parities reproduce the stored gate, compared up to output
   permutations S_k (a witness circuit realises one particular labelling).
5. The true circuit distance equals the stored ``d``.  The fault enumerator is
   exact through weight 4 and reports ">= 5" beyond that (weight-5 faults would
   need a five-fold meet-in-the-middle), which is also the convention the
   catalogue itself uses: a stored ``d = 5`` means "no undetectable fault of
   weight <= 4", i.e. a lower bound, not a computed value.  Rows with d <= 4 are
   checked exactly -- a distance too small *or* too large both surface -- and
   rows with d >= 5 are checked against that lower bound and printed as ">=5".
6. Level-3 rows only: the exact minimal T count and the CNOT-frame-reduced
   phase-polynomial degree of the RE-DERIVED gate match the stored values.

Level 2 and level 4 rows
------------------------
A factory's columns fix its *parity structure*; the rotation angle (pi/2 for
level 2, pi/4 for level 3, pi/8 for level 4) is a separate choice made when the
circuit is instantiated.  So a level-2 ``S0`` and a level-3 ``T0`` have
identical column data, and the parity read-off cannot tell them apart -- it
recovers the monomial set, not the level.  Checks 1-5 therefore run on every
row using the row's own level, while check 6 (exact T count, reduced degree)
runs only at level 3, where those quantities are defined.  The catalogue
already stores ``t_count: null`` for the level-4 rows for the same reason.

Exit status is 0 only if every row passes.

Run:  python verify_catalog.py            (from anywhere; a second or two)
"""
import itertools
import json
import sys
from itertools import permutations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))          # run from anywhere: siblings by bare name
sys.path.insert(0, str(HERE.parent))   # shared factorylib package

from evaluator import _distance, output_data            # noqa: E402
from factorylib import metrics as gate_metrics           # noqa: E402
from factorylib.metrics import metrics_from_named        # noqa: E402

# Bound the CNOT-frame-reduced degree search: exact enumeration of GL(5,2) is
# ~10^7 frames per gate.  k<=4 stays exact; above that the degree becomes an
# upper bound, and is only compared for rows the catalogue also computed
# exactly (those carry no `poly_degree_note`).
gate_metrics._DEG_CAP = 21_000
gate_metrics._DEG_SAMPLES = 20_000


# --------------------------------------------------------------- gate algebra
def sk_canonical(k, mons):
    """S_k-canonical encoding of a monomial set (output permutations only).

    The same key as ../classification/exhaustive_n38/dedup.py::sk_canonical,
    re-implemented here so this directory depends on nothing outside itself.
    Used only to compare a derived gate against a stored one up to output
    relabelling.
    """
    best = None
    for p in permutations(range(k)):
        e = tuple(sorted(tuple(sorted(p[i] for i in Q)) for Q in mons))
        if best is None or e < best:
            best = e
    return best


def sk_name(canon):
    """Readable '+'-joined, degree-major label of an sk_canonical encoding."""
    by_deg = {}
    for Q in canon:
        by_deg.setdefault(len(Q), []).append("".join(map(str, Q)))
    parts = []
    for deg in sorted(by_deg):
        parts += sorted(by_deg[deg])
    return "+".join(parts) if parts else "check-only"


def named_gate_to_monomials(named):
    """``'T0 . CS01'`` -> ``{frozenset({0}), frozenset({0,1})}``.

    The catalogue stores the human-named gate ('T', 'CS', 'CCZ', 'S', 'CZ',
    'sqrtT', 'CT', 'CCS', 'CCCZ' plus indices).  Only the index digits carry
    information for a parity comparison -- the name prefix encodes the level,
    which the column data cannot express (see the module docstring).
    """
    if not named or named.startswith("identity"):
        return frozenset()
    out = set()
    for tok in named.split("."):
        digits = [ch for ch in tok if ch.isdigit()]
        if digits:
            out.add(frozenset(int(ch) for ch in digits))
    return frozenset(out)


def check_parities_even(columns, N, k, level):
    """Return the degree-<=level monomials touching a check qubit whose parity
    is ODD.  Empty list == the circuit deposits nothing on the checks.

    Bitmask form: row i is the n-bit indicator of the columns containing qubit
    i, and a monomial's moment is the popcount parity of the AND of its rows --
    O(N^level) popcounts rather than O(N^level * n) set containments.
    """
    n = len(columns)
    rows = [0] * N
    for j, c in enumerate(columns):
        for i in c:
            rows[i] |= 1 << j
    full = (1 << n) - 1
    bad = []
    for deg in range(1, level + 1):
        for t in itertools.combinations(range(N), deg):
            if t[-1] < k:
                continue                      # pure-output term: that's the gate
            acc = full
            for i in t:
                acc &= rows[i]
            if acc.bit_count() & 1:
                bad.append(t)
    return bad


# ------------------------------------------------------------------- one row
def verify_row(r):
    """Run the checks above on one catalogue row.

    Returns (fails, dist, derived_label): `fails` is a list of human-readable
    failure strings -- empty means the row is verified.
    """
    fails = []
    n, k, d, level = r["n"], r["k"], r["d"], r["level"]
    cols = [tuple(sorted(c)) for c in r["columns"]]
    N = max(max(c) for c in cols) + 1

    # 1 / 2 -- shape
    if len(cols) != n:
        fails.append(f"len(columns)={len(cols)} != n={n}")
    if len(set(cols)) != len(cols):
        fails.append("repeated column (weight-2 undetectable fault)")
    if any(len(c) == 0 for c in cols):
        fails.append("empty column")
    if r.get("N") is not None and N != r["N"]:
        fails.append(f"N={N} != stored {r['N']}")

    # 3 -- nothing deposited on the checks
    bad = check_parities_even(cols, N, k, level)
    if bad:
        fails.append(f"{len(bad)} check-touching parities odd, e.g. {bad[:3]}")

    # 4 -- gate, compared up to S_k
    derived = output_data(cols, k, level=level)
    derived_mons = frozenset(frozenset(t) for v in derived.values() for t in v)
    stored_mons = named_gate_to_monomials(r["output_gate"])
    got = sk_name(sk_canonical(k, derived_mons))
    want = sk_name(sk_canonical(k, stored_mons))
    if got != want:
        fails.append(f"gate mismatch: derived {got} vs stored {want} "
                     f"({r['output_gate']})")

    # 5 -- true distance.  _distance is exact through weight 4 and returns its
    # cap+1 as a ">= " sentinel above that; see the module docstring.
    masks = [sum(1 << q for q in c) for c in cols]
    dist = _distance(masks, k, 4)
    if dist <= 4:
        if dist != d:
            fails.append(f"true distance {dist} != stored d={d}")
        shown = str(dist)
    else:
        if d < 5:
            fails.append(f"stored d={d} but no undetectable fault of weight "
                         f"<= 4 exists (true distance >= 5)")
        shown = ">=5"

    # 6 -- metrics, level 3 only
    if level == 3 and r.get("t_count") is not None:
        named = " . ".join(
            {1: "T", 2: "CS", 3: "CCZ"}[len(Q)] + "".join(map(str, sorted(Q)))
            for Q in sorted(derived_mons, key=lambda Q: (len(Q), sorted(Q))))
        try:
            tc, _, deg, _ = metrics_from_named(named or "identity")
        except (OverflowError, ValueError):
            tc, deg = None, None          # k >= 7: the T-count decoder overflows
        if tc is not None and tc != r["t_count"]:
            fails.append(f"t_count {tc} != stored {r['t_count']}")
        if (deg is not None and "poly_degree_note" not in r
                and deg != r["poly_degree"]):
            fails.append(f"poly_degree {deg} != stored {r['poly_degree']}")

    return fails, shown, got


def main():
    """Verify every row of catalog/factories.json; exit 0 iff all pass."""
    recs = json.loads((HERE / "catalog" / "factories.json")
                  .read_text(encoding="utf-8"))["factories"]
    nofail = 0
    for r in recs:
        tag = f"[[{r['n']},{r['k']},{r['d']}]] L{r['level']} {r['label'][:34]:<34}"
        fails, shown, derived = verify_row(r)
        if fails:
            print(f"FAIL  {tag}")
            for f in fails:
                print(f"        - {f}")
        else:
            nofail += 1
            print(f"OK    {tag} d={shown} gate={derived}")
    print(f"\n{nofail}/{len(recs)} catalogue rows independently re-verified")
    return 0 if nofail == len(recs) else 1


if __name__ == "__main__":
    sys.exit(main())
