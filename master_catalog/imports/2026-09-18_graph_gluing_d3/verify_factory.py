#!/usr/bin/env python3
"""A complete magic-state-factory verifier in one file, standard library only.

This is the reference implementation of everything `04_VERIFY.md` requires. It
depends on nothing -- no numpy, no repository, no network -- so an agent that
has only this directory and a catalogue row can still re-derive every claim
made about that row instead of believing it.

    python3 verify_factory.py circuit.json [circuit.json ...]
    python3 verify_factory.py --selftest

A circuit file is `{"columns": [[...], ...], "k": <int>}`; extra fields such as
`d`, `gate` and `n` are read as CLAIMS and checked, never trusted. A file may
also hold a list of such objects.

THE MODEL
---------
A factory is a set of pi/4 (T) rotations on N wires. Column j is the wire
support of rotation j. Wires 0..k-1 are OUTPUTS, wires k..N-1 are POSTSELECTED
CHECKS. Writing

    mask_j = sum(1 << q for q in column_j)
    syn_j  = mask_j >> k                    the check part
    out_j  = mask_j & ((1 << k) - 1)        the output part

a FAULT is a subset F of the columns (the input T states that arrived faulty).

    UNDETECTED  iff  XOR_{j in F} syn_j == 0      no check fires
    HARMFUL     iff  undetected and XOR_{j in F} out_j != 0

The distance d is the least weight at which a harmful fault exists, and
A_d is how many there are at that weight: error p -> A_d p^d.

WHAT IS EXACT HERE, AND WHAT IS NOT
-----------------------------------
Weights 1-4 are counted exactly by meet-in-the-middle. Weight 5 and above are
NOT implemented: the honest cost is O(n^3) and up, and a verifier that silently
stops looking is worse than one that says it stopped. So this file reports a
FLOOR past weight 4 and never upgrades a floor to a certificate.

That limit has bitten this project: the repository's own reference verifier
searches only to weight 4, which makes a `d >= 6` PASS from it VACUOUS. If you
need weight 5+, say so explicitly and use a tool that implements it.
"""
from __future__ import annotations

import itertools
import json
import sys
from collections import defaultdict

MAX_EXACT_WEIGHT = 4


# --------------------------------------------------------------- primitives --
def wire_rows(columns, N):
    """rows[q] = bitmask over columns, bit j set iff wire q is in column j."""
    rows = [0] * N
    for j, col in enumerate(columns):
        for q in col:
            rows[q] |= 1 << j
    return rows


def f2_rank(vectors):
    """Rank over F_2 of a list of integers-as-bit-vectors."""
    basis = {}
    for v in vectors:
        for pivot in sorted(basis, reverse=True):
            if (v >> pivot) & 1:
                v ^= basis[pivot]
        if v:
            basis[v.bit_length() - 1] = v
    return len(basis)


def recover_gate(rows, k, N):
    """Monomials of degree 1..3 whose column-parity is odd.

    The gate is a property of the columns and is recovered from them. A stored
    `gate` field is a claim: they are known to be wrong in 62+ records of the
    corpus this comes from ("T^5" parses as a single T on wire 5).

    Returns (gate_monomials, contaminating_monomials). A monomial touching a
    CHECK wire must have even parity -- that is what makes a check a check --
    so anything in the second list means the object is not a factory.
    """
    gate, contamination = [], []
    for a in range(N):
        if bin(rows[a]).count("1") & 1:
            (contamination if a >= k else gate).append((a,))
    for a in range(N):
        if not rows[a]:
            continue
        for b in range(a + 1, N):
            ab = rows[a] & rows[b]
            if not ab:
                continue
            if bin(ab).count("1") & 1:
                (contamination if b >= k else gate).append((a, b))
            for c in range(b + 1, N):
                abc = ab & rows[c]
                if abc and (bin(abc).count("1") & 1):
                    (contamination if c >= k else gate).append((a, b, c))
    return gate, contamination


def gate_string(monomials):
    if not monomials:
        return "I"
    name = {1: "T", 2: "CS", 3: "CCZ"}
    parts = [name[len(m)] + ",".join(map(str, m))
             for m in sorted(monomials, key=lambda t: (len(t), t))]
    return ".".join(parts)


def v_ex(monomials):
    """Extractable T states: over DISJOINT factors, CCZ -> 2, CS -> 1, T -> 1.

    `None` when monomials share an output: overlapping factors earn no
    catalytic credit, and a rate quoted on them is not a cross-gate comparison.
    """
    seen = set()
    total = 0
    for m in monomials:
        if seen & set(m):
            return None
        seen |= set(m)
        total += 2 if len(m) == 3 else 1
    return total


# ------------------------------------------------------------ fault counting --
def harmful_counts(columns, k, max_w=MAX_EXACT_WEIGHT):
    """Exact harmful-fault count at each weight 1..max_w (max_w <= 4)."""
    if max_w > MAX_EXACT_WEIGHT:
        raise ValueError(f"weights above {MAX_EXACT_WEIGHT} are not implemented; "
                         "do not pretend otherwise")
    n = len(columns)
    masks = [sum(1 << q for q in c) for c in columns]
    out = [m & ((1 << k) - 1) for m in masks]
    syn = [m >> k for m in masks]
    counts = {}

    counts[1] = sum(1 for j in range(n) if syn[j] == 0 and out[j])
    if max_w < 2:
        return counts

    by_syn = defaultdict(list)
    for j in range(n):
        by_syn[syn[j]].append(j)
    counts[2] = sum(1 for group in by_syn.values()
                    for a, b in itertools.combinations(group, 2)
                    if out[a] ^ out[b])
    if max_w < 3:
        return counts

    by_pair = defaultdict(list)
    for a, b in itertools.combinations(range(n), 2):
        by_pair[syn[a] ^ syn[b]].append((a, b))
    # a weight-3 fault {a,b,c} is seen once per choice of the singleton: /3
    triple = 0
    for c in range(n):
        for a, b in by_pair.get(syn[c], ()):
            if c not in (a, b) and (out[a] ^ out[b] ^ out[c]):
                triple += 1
    assert triple % 3 == 0, "weight-3 count not divisible by 3"
    counts[3] = triple // 3
    if max_w < 4:
        return counts

    # a weight-4 fault splits into two pairs of equal syndrome in 3 ways: /3
    quad = 0
    for pairs in by_pair.values():
        if len(pairs) < 2:
            continue
        for (a, b), (c, e) in itertools.combinations(pairs, 2):
            if len({a, b, c, e}) == 4 and (out[a] ^ out[b] ^ out[c] ^ out[e]):
                quad += 1
    assert quad % 3 == 0, "weight-4 count not divisible by 3"
    counts[4] = quad // 3
    return counts


# ------------------------------------------------------------- the verdict --
def verify(columns, k, claims=None):
    """Re-derive everything about one circuit. Returns (problems, facts)."""
    claims = claims or {}
    columns = [tuple(sorted(set(int(q) for q in c))) for c in columns]
    n = len(columns)
    N = max(max(c) for c in columns) + 1
    problems, facts = [], {"n": n, "k": k, "N": N}

    if not 0 < k <= N:
        return [f"k = {k} is not in 1..N = {N}"], facts

    rows = wire_rows(columns, N)
    gate, contamination = recover_gate(rows, k, N)
    touched = {q for m in gate for q in m}
    facts["gate"] = gate_string(gate)
    facts["degree_counts"] = {d: sum(1 for m in gate if len(m) == d) for d in (1, 2, 3)}

    # 1. is it a factory at all?
    if contamination:
        problems.append(
            f"NOT A FACTORY: {len(contamination)} odd degree-<=3 monomial(s) touch a "
            f"check wire, e.g. {contamination[0]}. A check wire must see even parity.")

    # 2. spectator outputs -- an output the gate never touches carries no magic
    #    and inflates k, which is the denominator of every rate.
    spectators = sorted(set(range(k)) - touched)
    facts["spectators"] = spectators
    if spectators:
        problems.append(
            f"SPECTATOR OUTPUTS {spectators}: the gate never touches them, so k is "
            f"padded. Honest width is {len(touched)}; delete the wires or demote them "
            f"to checks.")

    # 3. outputs independent modulo the check span -- two output wires equal mod
    #    the checks are ONE logical output wearing two labels.
    chk_rows = [rows[q] for q in range(k, N)]
    chk_rank = f2_rank(chk_rows)
    eff = f2_rank(chk_rows + [rows[q] for q in range(k)]) - chk_rank
    facts["effective_width"] = eff
    if eff != k:
        problems.append(
            f"OUTPUTS NOT INDEPENDENT mod the check span: effective width {eff} != k = "
            f"{k}. k counts a logical output more than once; every rate is flattered.")

    # 4. redundant check wires -- a check row inside the span of the others is
    #    dead postselection: its syndrome bit is an XOR of theirs for every
    #    fault, so it rejects nothing and only overstates N.
    deficiency = (N - k) - chk_rank
    facts["redundant_checks"] = deficiency
    if deficiency:
        problems.append(
            f"{deficiency} REDUNDANT CHECK WIRE(S): the check rows have rank {chk_rank} "
            f"< r = {N - k}. Delete dependent wires one at a time until independent; "
            f"N drops to {N - deficiency} with n, k, the gate and d unchanged.")

    # 5. rates -- computed on the honest width, and only where they mean something
    width = len(touched) if touched else 0
    facts["k_essential"] = width
    V = v_ex(gate)
    facts["V_ex"] = V
    facts["rho"] = round(n / V, 6) if V else None

    # 6. distance, honestly labelled
    counts = harmful_counts(columns, k, MAX_EXACT_WEIGHT)
    facts["harmful_by_weight"] = counts
    first = next((w for w in sorted(counts) if counts[w] > 0), None)
    if first is None:
        facts["d_exact"], facts["d_floor"] = None, MAX_EXACT_WEIGHT + 1
        facts["d_display"] = f">= {MAX_EXACT_WEIGHT + 1}"
        facts["A_d"], facts["A_d_at_weight"] = None, None
    else:
        facts["d_exact"], facts["d_floor"] = first, first
        facts["d_display"] = str(first)
        facts["A_d"], facts["A_d_at_weight"] = counts[first], first
    d_for_rates = facts["d_exact"] or facts["d_floor"]
    if width and d_for_rates >= 2:
        import math
        facts["gamma"] = round(math.log(n / width) / math.log(d_for_rates), 6)
        facts["gamma_rho"] = (round(math.log(n / V) / math.log(d_for_rates), 6)
                              if V else None)
        facts["gamma_evidence"] = ("exact" if facts["d_exact"]
                                   else "upper bound at the proven floor")
    else:
        facts["gamma"] = facts["gamma_rho"] = None
        facts["gamma_evidence"] = None

    # 7. every CLAIM the file made, checked against what the columns say
    if "d" in claims and isinstance(claims["d"], int):
        if facts["d_exact"] is not None and claims["d"] != facts["d_exact"]:
            problems.append(f"CLAIMED d = {claims['d']} but the true distance is "
                            f"{facts['d_exact']}")
        elif facts["d_exact"] is None and claims["d"] > facts["d_floor"]:
            problems.append(
                f"CLAIMED d = {claims['d']} is NOT CHECKED here: this verifier counts "
                f"only to weight {MAX_EXACT_WEIGHT}, so it proves d >= {facts['d_floor']} "
                f"and no more. A pass is VACUOUS for that claim -- use a weight-"
                f"{claims['d']} counter.")
    if "n" in claims and claims["n"] != n:
        problems.append(f"CLAIMED n = {claims['n']} but there are {n} columns")
    if "gate" in claims and isinstance(claims["gate"], str):
        facts["gate_as_stored"] = claims["gate"]
        facts["gate_matches_stored"] = claims["gate"] == facts["gate"]
    return problems, facts


# ----------------------------------------------------------------- selftest --
SELFTEST = [
    # [[8,3,2]] -- the unpunctured RM(1,3), the smallest non-Clifford factory
    # that exists. Its orbit is necessarily CCZ. Distance 2, A_2 = 28.
    {"name": "[[8,3,2]] CCZ012, the smallest factory there is",
     "k": 3, "expect": {"gate": "CCZ0,1,2", "d_exact": 2, "A_d": 28, "V_ex": 2},
     "columns": [[0, 1, 2, 3], [0, 1, 3], [0, 2, 3], [0, 3], [1, 2, 3], [1, 3],
                 [2, 3], [3]]},
    # A spectator planted on purpose: wire 3 is an output the gate never
    # touches. The verifier must say so rather than quietly rate it at k = 4.
    {"name": "planted spectator: same circuit relabelled to k = 4",
     "k": 4, "expect_problem": "SPECTATOR",
     "columns": [[0, 1, 2, 4], [0, 1, 4], [0, 2, 4], [0, 4], [1, 2, 4], [1, 4],
                 [4], [2, 4]]},
]


def selftest():
    """The two planted cases, then every fixture in fixtures/.

    The fixtures are REAL circuits, not constructed ones: two of them were
    catalogued for months before the defect they carry was found. A verifier
    that passes them is broken.
    """
    ok = True
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    fixtures = os.path.join(here, "fixtures")
    if os.path.isdir(fixtures):
        for name in sorted(os.listdir(fixtures)):
            if not name.endswith(".json"):
                continue
            rec = json.load(open(os.path.join(fixtures, name)))
            problems, facts = verify(rec["columns"], rec["k"], rec)
            want_bad = name.startswith("bad_")
            hit = bool(problems) == want_bad
            print(f"  {'PASS' if hit else 'FAIL'}  {name} "
                  f"({'defect expected' if want_bad else 'must be clean'})")
            if problems:
                for prob in problems:
                    print(f"        - {prob[:96]}")
            ok &= hit
    for case in SELFTEST:
        problems, facts = verify(case["columns"], case["k"])
        if "expect_problem" in case:
            hit = any(case["expect_problem"] in p for p in problems)
            print(f"  {'PASS' if hit else 'FAIL'}  {case['name']}")
            print(f"        -> {problems[0] if problems else 'no problem reported'}")
            ok &= hit
            continue
        bad = [f"{key}: got {facts.get(key)!r}, want {want!r}"
               for key, want in case["expect"].items() if facts.get(key) != want]
        if problems:
            bad.append(f"unexpected problems: {problems}")
        print(f"  {'PASS' if not bad else 'FAIL'}  {case['name']}")
        for b in bad:
            print(f"        {b}")
        ok &= not bad
    return ok


def main(argv):
    if "--selftest" in argv:
        print("selftest:")
        return 0 if selftest() else 1
    if len(argv) < 2:
        print(__doc__)
        return 2
    worst = 0
    for path in argv[1:]:
        payload = json.load(open(path))
        records = payload if isinstance(payload, list) else [payload]
        for i, rec in enumerate(records):
            problems, facts = verify(rec["columns"], rec["k"], rec)
            tag = f"{path}" + (f"[{i}]" if len(records) > 1 else "")
            head = (f"[[{facts['n']},{facts.get('k_essential')},"
                    f"{facts.get('d_display')}]] {facts.get('gate', '?')[:44]}")
            print(f"{tag}\n  {head}")
            for key in ("V_ex", "rho", "gamma", "gamma_rho", "gamma_evidence",
                        "A_d", "A_d_at_weight", "effective_width",
                        "redundant_checks", "harmful_by_weight"):
                if facts.get(key) is not None:
                    print(f"    {key} = {facts[key]}")
            if problems:
                worst = 1
                print("  PROBLEMS:")
                for p in problems:
                    print(f"    - {p}")
            else:
                print("  OK -- every check re-derived from the columns")
    return worst


if __name__ == "__main__":
    sys.exit(main(sys.argv))
