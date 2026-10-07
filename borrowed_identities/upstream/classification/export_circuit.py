"""Reconstruct one catalogue row's explicit circuit as a binary matrix.

A borrowed-identity factory on n = k + r wires (k outputs 0..k-1, r checks
k..n-1) is a list of N parity rotations; column j of the matrix is wire i's
bit in gate j (row i, column j). This matches the column convention used
throughout this project's classification code and in the columns field of
the `sj-magic-state-factory-searches` repository's `master_catalog` catalogue.

Usage (from the repo root):
    python3 classification/export_circuit.py two-group --l 3 --n 4 --k 2 --s_total 1 --s_O 1
    python3 classification/export_circuit.py symfree   --l 3 --parts 3,2 --checks 3

Prints the circuit as one gate (qubit-support) per line, then the same
circuit as an explicit 0/1 matrix (rows = wires, columns = gates).
"""
import argparse
import os
import sys
from itertools import combinations

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "searches"))
import Two_group as tg
import symfree_search as sym
import classify


def two_group_columns(l, n, k, s_total, s_O):
    n_minus_k = n - k
    pairs, W_total, W_O = tg.build_gate_set(k, n_minus_k, s_total, s_O)
    valid = tg.find_valid_signs(l, n, k, pairs)
    if not valid:
        raise SystemExit(f"no valid sign assignment at l={l} n={n} k={k} "
                          f"s_total={s_total} s_O={s_O}")
    sigma_dict = valid[0]
    removed = {(w, 0) for w in (set(W_O) & set(W_total)) if w >= 1}
    out, chk = list(range(k)), list(range(k, n))
    columns, signs = [], []
    for (wO, wS), sig in sigma_dict.items():
        if sig == 0 or (wO, wS) in removed:
            continue
        for Osub in combinations(out, wO):
            for Ssub in combinations(chk, wS):
                columns.append(sorted(Osub + Ssub))
                signs.append(sig)
    return columns, signs, out, chk, n


def symfree_columns(l, parts, checks):
    r = sym.solve_binding(list(parts), checks, l)
    if r is None:
        raise SystemExit(f"no borrowed identity at l={l} parts={parts} checks={checks}")
    columns = [sorted(supp) for supp, _ in r["gates"]]
    signs = [c for _, c in r["gates"]]
    return columns, signs, list(r["O"]), [q for q in range(r["n"]) if q not in r["O"]], r["n"]


def print_circuit(columns, signs, out, chk, n):
    print(f"n={n} qubits: outputs={out} checks={chk}")
    print(f"N={len(columns)} gates:")
    for col, s in zip(columns, signs):
        sign_str = "+" if s > 0 else "-"
        print(f"  {sign_str} on qubits {col}")
    print()
    print("matrix (rows = wires 0..n-1, columns = gates 0..N-1):")
    for wire in range(n):
        print("  " + "".join("1" if wire in col else "0" for col in columns))
    print()
    Gf = [frozenset(col) for col in columns]
    info = classify.classify(Gf, signs, out, l_level)
    print(f"deposited output: degree={info['degree']} essential_dim={info['essential_dim']} "
          f"decomposition={info['decomposition']} t_count={info['t_count']}"
          + (f"  [{info['degree_note']}]" if info['degree_note'] else "")
          + (f"  [{info['t_count_note']}]" if info['t_count_note'] else ""))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="search", required=True)

    p1 = sub.add_parser("two-group", help="reconstruct a two-group (Two_group.py) factory")
    p1.add_argument("--l", type=int, required=True)
    p1.add_argument("--n", type=int, required=True)
    p1.add_argument("--k", type=int, required=True)
    p1.add_argument("--s_total", type=int, required=True)
    p1.add_argument("--s_O", type=int, required=True)

    p2 = sub.add_parser("symfree", help="reconstruct a symmetry-free (symfree_search.py) factory")
    p2.add_argument("--l", type=int, required=True)
    p2.add_argument("--parts", type=str, required=True, help="comma-separated output block sizes, e.g. 3,2")
    p2.add_argument("--checks", type=int, required=True, help="number of check qubits")

    args = ap.parse_args()
    l_level = args.l
    if args.search == "two-group":
        columns, signs, out, chk, n = two_group_columns(args.l, args.n, args.k, args.s_total, args.s_O)
    else:
        parts = tuple(int(x) for x in args.parts.split(","))
        columns, signs, out, chk, n = symfree_columns(args.l, parts, args.checks)
    print_circuit(columns, signs, out, chk, n)
