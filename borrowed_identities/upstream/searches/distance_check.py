"""
True distance of a borrowed-identity factory.

Gates (after output-only extraction) are multi-qubit Z-rotations, each supported
on a subset of the n circuit qubits: outputs = {0..k-1}, checks = {k..n-1}.
An error set E of gates is UNDETECTED iff every CHECK qubit is covered an even
number of times (XOR=0 on checks); it is a LOGICAL error iff some OUTPUT qubit
is covered an odd number of times. Distance = min |E| over such undetectable
logical errors.  (This is the paper's 'min # of gates with odd overlap on <=k qubits'.)
"""
from math import comb
from itertools import combinations
from Two_group import build_gate_set, extract_factory, find_valid_signs

def gate_supports(n, k, s_total, s_O):
    pairs, W_total, W_O = build_gate_set(k, n-k, s_total, s_O)
    removed = {(w, 0) for w in (set(W_O) & set(W_total)) if w >= 1}   # output-only, extracted
    out = list(range(k)); chk = list(range(k, n))
    gates = []
    for (wO, wS) in pairs:
        if (wO, wS) in removed:
            continue
        for Osub in combinations(out, wO):
            for Ssub in combinations(chk, wS):
                mask = 0
                for q in Osub + Ssub:
                    mask |= (1 << q)
                gates.append(mask)
    return gates, out, chk

def true_distance(n, k, s_total, s_O, max_w=8):
    gates, out, chk = gate_supports(n, k, s_total, s_O)
    chk_mask = sum(1 << q for q in chk)
    out_mask = sum(1 << q for q in out)
    N = len(gates)
    for w in range(1, max_w + 1):
        for E in combinations(range(N), w):
            x = 0
            for i in E:
                x ^= gates[i]
            if (x & chk_mask) == 0 and (x & out_mask) != 0:
                return w, N
    return None, N

cases = [
    ("[[7,1,?]]  claimed d=3", 2, 4, 1, 2, 1),
    ("[[15,1,?]] claimed d=3", 3, 5, 1, 2, 1),
    ("[[31,1,?]] claimed d=3", 4, 6, 1, 2, 1),
    ("[[27,1,?]] claimed d=5", 2, 7, 1, 4, 1),
    ("[[15,1,?]] claimed d=7", 2, 8, 1, 6, 1),
    ("[[6,1,?]]  claimed d=2", 2, 3, 1, 1, 1),
]
print(f"{'factory':24} {'s_total':>7} {'N':>4} {'claimed':>8} {'TRUE d':>7}")
for name, l, n, k, st, so in cases:
    claimed = st + 1
    d, N = true_distance(n, k, st, so, max_w=8)
    print(f"{name:24} {st:>7} {N:>4} {claimed:>8} {str(d):>7}")
