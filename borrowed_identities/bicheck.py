"""The two checks both exporters make on a borrowed-identity circuit, written
out from the paper's definitions rather than imported from the upstream code.

A circuit is a list of ``(support, c)``: the parity phase gate at angle
``c*pi/2^l`` on the wires of ``support``, outputs ``0..k-1``.
"""
from itertools import combinations


def magic(gates):
    """Indices of the gates that consume a level-l magic state: odd coefficient."""
    return [index for index, (_support, coeff) in enumerate(gates) if coeff % 2]


def borrowed_identity_violation(gates, k, level):
    """The first check-touching monomial with genuine level-l phase, or None.

    The condition, written out from the paper's definition rather than imported:
    a parity gate on support ``g`` with coefficient ``c`` adds
    ``(-1)^(t+1) 2^(t-1) c`` to the monomial on every ``t``-subset of ``g``, and
    a monomial touching a check wire must be Clifford, i.e. its coefficient
    must vanish modulo ``2^t`` (it is reduced modulo ``2^l`` throughout).
    """
    mod = 1 << level
    for size in range(1, level + 1):
        totals = {}
        for support, coeff in gates:
            for T in combinations(support, size):
                totals[T] = totals.get(T, 0) + coeff
        for T, total in totals.items():
            if max(T) < k:
                continue
            value = ((-1) ** (size + 1)) * (1 << (size - 1)) * total % mod
            if value % (1 << size):
                return list(T)
    return None
