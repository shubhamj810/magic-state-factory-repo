"""Clifford-frame-reduced phase-polynomial degree.

The deposited diagonal gate diag_x exp(i (pi/2^{L-1}) f(x)) is only defined up
to the CNOT frame of its k output qubits: conjugating by output CNOTs M in
GL(k,2) turns f(x) into f(Mx).  A size-s monomial is *genuine* (not absorbable
into Cliffords) iff its coefficient is nonzero mod 2^s; the reduced degree is
the minimum over all frames of the largest genuine monomial size.
"""
from itertools import product, permutations

def reduced_degree(P, k, L):
    """Full-Clifford-reduced genuine degree of diag_x exp(i (pi/2^{L-1}) f(x)),
       P = {frozenset(support): coeff mod 2^L} on k qubits.  = min over output CNOTs
       M in GL(k,2) of the in-frame genuine degree of P(Mx).  (ZZ -> 1, CS -> 2, CCZ -> 3.)"""
    MOD = 1 << L
    tab = {b: sum(c for S, c in P.items() if S <= frozenset(i for i in range(k) if b[i])) % MOD
           for b in product((0, 1), repeat=k)}          # truth table of f over F_2^k
    best = k
    for M in _gl_matrices(k):                            # M = tuple of k column bit-ints
        best = min(best, _deg_after(tab, k, M, L))
        if best <= 1:
            break
    return best

def _deg_after(tab, k, M, L):                            # in-frame genuine degree of f(Mx)
    MOD, deg = 1 << L, 0
    for mask in range(1, 1 << k):
        pc = bin(mask).count("1")
        if pc > L:                                       # size>L monomial is never genuine
            continue
        s, sub = 0, mask                                 # Mobius coeff of `mask` in f(Mx)
        while True:
            y = 0
            for j in range(k):
                if (sub >> j) & 1:
                    y ^= M[j]                            # y = M applied to submask point
            s += (-1) ** (pc - bin(sub).count("1")) * tab[tuple((y >> i) & 1 for i in range(k))]
            if sub == 0:
                break
            sub = (sub - 1) & mask
        if (s % MOD) % (1 << pc):                        # genuine at size pc: coeff != 0 mod 2^pc
            deg = max(deg, pc)
    return deg

def _gl_matrices(k):                                     # all invertible k x k over F2
    # Lazy: yield each frame so reduced_degree's `best<=1` early-exit can stop
    # before materialising all |GL(k,2)| frames (and so memory stays bounded).
    for cols in permutations(range(1, 1 << k), k):
        basis = []
        for v in cols:
            w = v
            for b in basis:
                w = min(w, w ^ b)
            if w:
                basis.append(w)
        if len(basis) == k:
            yield cols