#!/usr/bin/env python3
"""THE SYMMETRY GROUPS THAT GENERATE THE CATALOGUE.

Every factory in ``catalog/factories.json`` is a set of columns on N qubits.
This module computes, for each of them, the group

    Aut(F) = { permutations pi of the N qubits :
               pi maps the column SET to itself, and maps the output block
               {0..k-1} to itself }

and writes it, with a set of generators, its order, and the induced orbits on
columns, to ``catalog/symmetry_groups.json``.

WHY THIS FILE EXISTS
--------------------
The slot-ansatz search *starts* from a symmetry group: you pick check blocks
with a symmetric (S_lambda) or cyclic (C_lambda) group acting on them, and the
solver only chooses one label per group orbit.  So the group is what makes the
search tractable, and the group plus one representative column per orbit is
what actually generates the factory.  But that group lived only in the search
driver and in the log file's geometry tag -- the shipped circuits were flat
column lists, and a reader could not recover the structure that produced them.

Recomputing Aut(F) directly from the columns fixes that, and does better than
recording the design group would have:

  * it applies uniformly to every catalogued factory, including the ones found
    by raw column-level SAT with no ansatz at all;
  * it is a property of the *circuit*, not of the search that happened to find
    it, so it is reproducible by anyone holding the columns;
  * it can be LARGER than the design group -- a solution found inside an
    S_4 x S_4 ansatz may turn out to have extra symmetry -- which is itself
    information about the construction.

REGENERATION (the property that makes this data useful)
-------------------------------------------------------
For each factory we also store one representative column per Aut(F)-orbit.
Closing those representatives under the stored generators must return exactly
the original column set; ``rebuild_from_groups.py`` does that and then
re-verifies the resulting factory's [[n,k,d]] and gate from scratch.  When the
orbit count is much smaller than n, the pair (group, representatives) is a
genuinely compressed description of the factory -- the same compression the
slot ansatz exploits during the search.

ALGORITHM
---------
Backtracking over images of the qubits, in a fixed order, with two prunings:

  1. *Colour refinement.*  Each qubit gets an invariant -- whether it is an
     output, and the sorted multiset of the weights of the columns containing
     it -- iterated once against neighbours.  A qubit may only map to a qubit
     of the same colour.
  2. *Partial-consistency.*  After assigning images to a prefix A of the qubits,
     the multiset  { c intersect A : c in columns }  must map, under the partial
     permutation, onto the multiset  { c intersect pi(A) : c in columns }.
     This is a necessary condition for any completion, checked in O(n).

N <= 14 across the catalogue and the groups are small, so the full group is
enumerated exactly rather than estimated by a stabiliser chain.  ``GROUP_CAP``
bounds the enumeration; hitting it is reported in the output as
``complete: false`` and never silently truncated.
"""
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)          # run from anywhere: siblings by bare name

#: Refuse to enumerate a group larger than this; report complete=False instead.
GROUP_CAP = 2_000_000


# ------------------------------------------------------------ colour refinement
def _colours(cols, k, N):
    """Initial qubit colours: (is_output, sorted multiset of incident column
    weights), refined once by the multiset of neighbour colours."""
    incident = [[] for _ in range(N)]
    for c in cols:
        for q in c:
            incident[q].append(len(c))
    base = [(0 if q < k else 1, tuple(sorted(incident[q]))) for q in range(N)]
    # one refinement round: append the multiset of co-occurring qubits' colours
    nbr = [Counter() for _ in range(N)]
    for c in cols:
        for q in c:
            for p in c:
                if p != q:
                    nbr[q][base[p]] += 1
    return [(base[q], tuple(sorted(nbr[q].items()))) for q in range(N)]


# ---------------------------------------------------------------- automorphisms
def automorphisms(cols, k, N, cap=GROUP_CAP):
    """All qubit permutations preserving the column set and the output block.

    `cols` is a list of frozensets/tuples of qubit indices.  Returns
    (perms, complete) where `perms` is a list of tuples pi with pi[q] the image
    of qubit q, and `complete` is False if the enumeration hit `cap`.
    """
    cols = [frozenset(c) for c in cols]
    colset = set(cols)
    colour = _colours(cols, k, N)
    by_colour = defaultdict(list)
    for q in range(N):
        by_colour[colour[q]].append(q)

    # order qubits by scarcest colour first -- fewest candidate images earliest
    order = sorted(range(N), key=lambda q: (len(by_colour[colour[q]]), q))

    perms = []
    image = [None] * N
    used = [False] * N

    def consistent(depth):
        """Partial-consistency prune, on the prefix order[:depth]."""
        A = order[:depth]
        piA = [image[q] for q in A]
        left = Counter()
        for c in cols:
            left[frozenset(image[q] for q in A if q in c)] += 1
        right = Counter()
        piAset = set(piA)
        for c in cols:
            right[frozenset(c & piAset)] += 1
        return left == right

    def walk(depth):
        if len(perms) >= cap:
            return
        if depth == N:
            if {frozenset(image[q] for q in c) for c in cols} == colset:
                perms.append(tuple(image))
            return
        q = order[depth]
        for p in by_colour[colour[q]]:
            if used[p]:
                continue
            image[q] = p
            used[p] = True
            if consistent(depth + 1):
                walk(depth + 1)
            used[p] = False
            image[q] = None

    walk(0)
    return perms, len(perms) < cap


def generating_set(perms, N):
    """A small generating set for the group `perms` (given in full).

    Sift once through the listed elements, keeping any element not already in
    the subgroup generated so far.  Each kept generator at least doubles the
    subgroup order (its coset is new), so this stops after at most log2(|G|)
    generators -- 14 for the largest group in the catalogue -- and recomputes
    the closure only that many times.  Not guaranteed minimal; the goal is a
    short, human-readable generator list in the shipped JSON, and the
    round-trip check in rebuild_from_groups.py is what certifies correctness.
    """
    identity = tuple(range(N))
    full = set(perms)
    gens = []
    closure = {identity}
    for g in perms:
        if g in closure:
            continue
        gens.append(g)
        closure = _closure(gens, N)
        if closure == full:
            break
    return gens


def _closure(gens, N):
    """Subgroup generated by `gens`, by breadth-first multiplication."""
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


def column_orbits(cols, perms):
    """Partition the columns into Aut(F)-orbits; return a list of
    (representative, orbit size), representative = the sorted column."""
    cols = [frozenset(c) for c in cols]
    remaining = set(cols)
    out = []
    for c in cols:
        if c not in remaining:
            continue
        orbit = {frozenset(pi[q] for q in c) for pi in perms}
        orbit &= set(cols)
        remaining -= orbit
        out.append((sorted(c), len(orbit)))
    return out


def cycle_type(perm, k):
    """(output cycle type, check cycle type) of a permutation, as sorted tuples
    of cycle lengths -- a compact readable fingerprint for the JSON."""
    N = len(perm)
    seen = [False] * N
    out, chk = [], []
    for s in range(N):
        if seen[s]:
            continue
        length, x = 0, s
        while not seen[x]:
            seen[x] = True
            x = perm[x]
            length += 1
        (out if s < k else chk).append(length)
    return tuple(sorted(out, reverse=True)), tuple(sorted(chk, reverse=True))


# ------------------------------------------------------------------ the driver
def analyse(entry, cap=GROUP_CAP):
    """Compute the symmetry record for one catalogue row.

    ``cap`` is threaded through rather than read from the module constant so a
    test can force the truncated case; the enumeration is far too fast at these
    sizes to reach GROUP_CAP otherwise (the largest group here is 14,400).
    """
    cols = [tuple(sorted(c)) for c in entry["columns"]]
    k, N = entry["k"], entry["N"]
    perms, complete = automorphisms(cols, k, N, cap)
    gens = generating_set(perms, N) if complete else []
    orbits = column_orbits(cols, perms)
    # a group generates the factory iff closing the orbit reps returns every column
    regen = set()
    for rep, _size in orbits:
        for pi in perms:
            regen.add(tuple(sorted(pi[q] for q in rep)))
    return {
        "label": entry["label"],
        "params": [entry["n"], entry["k"], entry["d"]],
        "N": N,
        "level": entry["level"],
        "output_gate": entry["output_gate"],
        "source": entry["source"],
        "group": {
            "description": "qubit permutations preserving the column set and "
                           "the output block {0..k-1}",
            "order": len(perms),
            "complete": complete,
            "generators": [list(g) for g in gens],
            "generator_cycle_types": [
                {"outputs": list(cycle_type(g, k)[0]),
                 "checks": list(cycle_type(g, k)[1])} for g in gens],
        },
        "column_orbits": [{"representative": rep, "orbit_size": size}
                          for rep, size in orbits],
        "n_orbits": len(orbits),
        "compression": round(entry["n"] / max(len(orbits), 1), 2),
        "regenerates_factory": regen == {tuple(c) for c in cols},
    }


def build(catalog_path=None, out_path=None, cap=GROUP_CAP):
    """Analyse every catalogue row and write catalog/symmetry_groups.json."""
    catalog_path = str(catalog_path or
                       os.path.join(HERE, "catalog", "factories.json"))
    out_path = out_path or os.path.join(HERE, "catalog", "symmetry_groups.json")
    with open(catalog_path, encoding="utf-8") as fh:
        entries = json.load(fh)["factories"]
    records = []
    for e in entries:
        rec = analyse(e, cap)
        records.append(rec)
        flag = "" if rec["regenerates_factory"] else "   <-- DOES NOT REGENERATE"
        print(f"[[{e['n']},{e['k']},{e['d']}]] {e['label'][:32]:<32} "
              f"|Aut| = {rec['group']['order']:>7}  "
              f"orbits = {rec['n_orbits']:>3}  "
              f"compression = {rec['compression']:>5}x{flag}", flush=True)
    bad = [r for r in records if not r["regenerates_factory"]]
    # A capped enumeration is not a smaller answer, it is a different claim.
    # `order` is published as |Aut(F)| and `group_definition` says so; if the
    # search stopped at GROUP_CAP then `order` is the size of a SUBGROUP, and a
    # proper subgroup can perfectly well regenerate the columns -- so
    # `regenerates_factory` does not catch this and used to be the only thing
    # that could fail the build.
    truncated = [r for r in records if not r["group"]["complete"]]
    payload = {
        "description": (
            "For each catalogued factory: the group of qubit permutations "
            "preserving its column set and its output block, a generating set, "
            "and one representative column per orbit. Closing the "
            "representatives under the generators reproduces the factory "
            "exactly -- see rebuild_from_groups.py."),
        "group_definition": "Aut(F) = { pi in S_N : pi(columns) = columns, "
                            "pi({0..k-1}) = {0..k-1} }",
        "n_factories": len(records),
        "all_regenerate": not bad,
        "all_groups_complete": not truncated,
        "group_cap": cap,
        "factories": records,
    }
    # A truncated run must not REPLACE the published file.  Returning nonzero
    # was not enough: the write happened first, so a capped run left an
    # incomplete symmetry_groups.json on disk that every downstream reader would
    # pick up, and the nonzero exit only helped a caller who checked it.  The
    # partial result is still written, under a name that cannot be mistaken for
    # the catalogue, because on a capped run the interesting question is WHICH
    # rows blew the cap.
    failed = bool(bad or truncated)
    # str(), because callers pass either: the CLI hands over a string and a
    # programmatic caller naturally passes a Path, which used to fail on the
    # concatenation below with a TypeError instead of writing anything.
    out_path = str(out_path)
    destination = (out_path + ".incomplete.json") if failed else out_path
    tmp = destination + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
        fh.write("\n")
    os.replace(tmp, destination)           # atomic: no half-written catalogue
    print(f"\n{len(records)} factories; all regenerate: {not bad}; "
          f"all groups complete: {not truncated}")
    print(f"  -> {os.path.relpath(destination, HERE)}")
    if truncated:
        print(f"\n{len(truncated)} row(s) hit the group cap {cap:,}, so the "
              f"published `order` is a subgroup's, not |Aut(F)|:")
        for rec in truncated:
            print(f"  [[{rec['params'][0]},{rec['params'][1]},"
                  f"{rec['params'][2]}]] {rec['label']}: order >= "
                  f"{rec['group']['order']:,}, generators withheld")
        print("Raise the cap and rerun, or the file's group_definition is "
              "false for those rows.")
    if failed:
        print(f"\n{os.path.basename(out_path)} was NOT replaced.")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(build())
