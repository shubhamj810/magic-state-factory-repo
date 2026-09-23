#!/usr/bin/env python3
"""Rebuild every catalogued factory from its SYMMETRY GROUP alone, and verify.

This is the round trip that makes ``catalog/symmetry_groups.json`` meaningful
rather than decorative.  For each factory the file stores

    * a generating set for  Aut(F) = { pi in S_N : pi(columns) = columns,
                                       pi({0..k-1}) = {0..k-1} }, and
    * one representative column per Aut(F)-orbit.

This script throws the stored column list away, regenerates the factory by
closing the orbit representatives under the generated group, and then verifies
the reconstruction from first principles:

    1. the regenerated column set has exactly n columns and equals the
       catalogued one;
    2. every degree-<=3 monomial touching a check qubit has even parity;
    3. the output parities reproduce the catalogued gate;
    4. the true circuit distance (exact through weight 4) equals d.

Nothing in steps 2-4 consults the catalogue's stored columns -- they run on the
regenerated circuit.  So a pass means the group and the representatives really
do determine the factory.

Read this next to ``symmetry_groups.py``, which computes the groups, and
``verify_catalog.py``, which verifies the shipped columns directly.

Run:  python rebuild_from_groups.py           (from anywhere; a few seconds)
"""
import itertools
import json
import os
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)          # run from anywhere: siblings by bare name

from evaluator import _distance, output_data           # noqa: E402
from verify_catalog import (named_gate_to_monomials,   # noqa: E402
                            check_parities_even, sk_canonical, sk_name)


def group_from_generators(gens, N):
    """Closure of `gens` under composition (breadth-first).  Returns a set of
    permutation tuples, always containing the identity."""
    identity = tuple(range(N))
    seen = {identity}
    frontier = [identity]
    while frontier:
        nxt = []
        for x in frontier:
            for g in gens:
                y = tuple(g[x[i]] for i in range(N))
                if y not in seen:
                    seen.add(y)
                    nxt.append(y)
        frontier = nxt
    return seen


def regenerate(record):
    """Columns implied by the stored group and orbit representatives."""
    N = record["N"]
    gens = [tuple(g) for g in record["group"]["generators"]]
    group = group_from_generators(gens, N)
    cols = set()
    for orbit in record["column_orbits"]:
        rep = orbit["representative"]
        for pi in group:
            cols.add(tuple(sorted(pi[q] for q in rep)))
    return sorted(cols), len(group)


def _shape_problems(record, catalogued):
    """Whether this group record describes the catalogued row it is paired with.

    Everything `check` does below indexes `N`, `k` or `level` -- into
    `range(N)`, into permutations of `k` outputs -- so a mistyped or absurd value
    does not fail the rebuild, it hangs it: `N: 2**63` enumerates check-touching
    monomials over 2^63 qubits.  Rather than range-check each field on its own,
    every parameter is required to EQUAL the catalogue's, which is the stronger
    statement anyway: the catalogue row is independently verified from its
    columns by build_catalog and verify_catalog, so agreeing with it is what
    makes the rebuilt group a statement about a real factory.
    """
    problems = []
    params = record.get("params")
    want = [catalogued["n"], catalogued["k"], catalogued["d"]]
    if params != want:
        problems.append(f"params {params!r} != the catalogue's {want}")
    for field in ("N", "level"):
        if record.get(field) != catalogued[field]:
            problems.append(f"{field}={record.get(field)!r} != the catalogue's "
                            f"{catalogued[field]!r}")
    if record.get("output_gate") != catalogued["output_gate"]:
        problems.append(f"output_gate {record.get('output_gate')!r} != the "
                        f"catalogue's {catalogued['output_gate']!r}")
    group = record.get("group")
    if not isinstance(group, dict):
        problems.append(f"group is a {type(group).__name__}, not an object")
        return problems
    N = catalogued["N"]
    if "order" not in group:
        problems.append("group.order is absent, so there is nothing to compare "
                        "the regenerated order against")
    generators = group.get("generators")
    if not isinstance(generators, list):
        problems.append(f"group.generators is a {type(generators).__name__}, "
                        f"not a list")
    else:
        for index, gen in enumerate(generators):
            if not isinstance(gen, list) or sorted(gen) != list(range(N)):
                problems.append(f"generator {index} is not a permutation of "
                                f"0..{N - 1}: {gen!r}")
                break
    orbits = record.get("column_orbits")
    if not isinstance(orbits, list) or not orbits:
        problems.append("column_orbits is not a non-empty list")
    else:
        for index, orbit in enumerate(orbits):
            rep = orbit.get("representative") if isinstance(orbit, dict) else None
            if not isinstance(rep, list) or not rep or not all(
                    isinstance(q, int) and not isinstance(q, bool) and 0 <= q < N
                    for q in rep):
                problems.append(f"orbit {index} has no usable representative: "
                                f"{orbit!r}")
                break
    return problems


def check(record, catalogued):
    """Rebuild one factory and run the four checks.  Returns a failure list."""
    fails = _shape_problems(record, catalogued)
    if fails:
        # Nothing below is meaningful, or even terminating, once a parameter
        # disagrees with the catalogue.
        return fails, "?", record.get("group", {}).get("order"), 0
    n, k, d = record["params"]
    N, level = record["N"], record["level"]
    cols, order = regenerate(record)

    if order != record["group"]["order"]:
        fails.append(f"generated group order {order} != stored "
                     f"{record['group']['order']}")
    if len(cols) != n:
        fails.append(f"regenerated {len(cols)} columns, expected n={n}")
    if set(cols) != {tuple(sorted(c)) for c in catalogued["columns"]}:
        fails.append("regenerated column set differs from the catalogued one")

    bad = check_parities_even(cols, N, k, level)
    if bad:
        fails.append(f"{len(bad)} check-touching parities odd, e.g. {bad[:3]}")

    derived = output_data(cols, k, level=level)
    derived_mons = frozenset(frozenset(t) for v in derived.values() for t in v)
    got = sk_name(sk_canonical(k, derived_mons))
    want = sk_name(sk_canonical(k, named_gate_to_monomials(record["output_gate"])))
    if got != want:
        fails.append(f"gate mismatch: rebuilt {got} vs catalogued {want}")

    masks = [sum(1 << q for q in c) for c in cols]
    dist = _distance(masks, k, 4)
    if dist <= 4:
        if dist != d:
            fails.append(f"true distance {dist} != catalogued d={d}")
        shown = str(dist)
    else:
        if d < 5:
            fails.append(f"catalogued d={d} but no fault of weight <= 4 exists")
        shown = ">=5"
    return fails, shown, order, len(record["column_orbits"])


def main(groups=None, catalog=None):
    """Rebuild every catalogue row from its stored group.

    ``groups`` and ``catalog`` override the files, which is how the tests hand in
    a deliberately damaged group set without writing over the catalogue.
    """
    if groups is None:
        groups = json.loads(Path(HERE, "catalog", "symmetry_groups.json")
                            .read_text(encoding="utf-8"))
    if catalog is None:
        catalog = json.loads(Path(HERE, "catalog", "factories.json")
                             .read_text(encoding="utf-8"))["factories"]
    if len(groups["factories"]) != len(catalog):
        print("symmetry_groups.json and factories.json disagree on row count; "
              "re-run symmetry_groups.py")
        return 1
    if groups.get("n_factories") != len(groups["factories"]):
        print(f"symmetry_groups.json says n_factories="
              f"{groups.get('n_factories')!r} but carries "
              f"{len(groups['factories'])} rows; re-run symmetry_groups.py")
        return 1
    # Reconstruction does NOT certify that a stored group is Aut(F).  With every
    # group truncated to the identity, all 57 rows still "rebuilt" -- each orbit
    # is then a singleton, so closing the representatives trivially returns the
    # column set.  The claim being checked below is only meaningful if the groups
    # are the complete ones, so that is checked first, from the file.
    # `is not True`: a truncated enumeration is the one thing this check exists
    # to catch, so `1`, `"yes"` or a missing flag are not read generously.
    incomplete = [r for r in groups["factories"]
                  if not isinstance(r, dict)
                  or r.get("group", {}).get("complete") is not True]
    if groups.get("all_groups_complete") is not True or incomplete:
        print(f"symmetry_groups.json holds {len(incomplete)} truncated group(s) "
              f"(all_groups_complete="
              f"{groups.get('all_groups_complete')!r}): its `order` fields are "
              f"subgroup orders, not |Aut(F)|, and rebuilding from them proves "
              f"nothing. Re-run symmetry_groups.py with a higher cap.")
        for record in incomplete[:5]:
            named = record.get("label", "<unnamed>") if isinstance(record, dict) \
                else "<not an object>"
            print(f"        - {named}")
        return 1
    ok = 0
    for record, catalogued in zip(groups["factories"], catalog):
        fails, shown, order, orbits = check(record, catalogued)
        # Every field here came out of a file, so nothing is indexed before
        # check() has confirmed it: the tag is built defensively on purpose.
        params = record.get("params") if isinstance(record, dict) else None
        param_text = ",".join(str(v) for v in params) \
            if isinstance(params, list) else "?"
        named = str(record.get("label", "<unnamed>"))[:32] \
            if isinstance(record, dict) else "<not an object>"
        tag = f"[[{param_text}]] {named:<32}"
        if fails:
            print(f"FAIL  {tag}")
            for f in fails:
                print(f"        - {f}")
        else:
            ok += 1
            print(f"OK    {tag} |Aut|={order:>7} orbits={orbits:>3} d={shown}")
    print(f"\n{ok}/{len(catalog)} factories rebuilt from their symmetry group "
          f"and re-verified")
    return 0 if ok == len(catalog) else 1


if __name__ == "__main__":
    sys.exit(main())
