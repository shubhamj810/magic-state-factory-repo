"""Render a factory's gate list as a clickable Quirk circuit (https://algassert.com/quirk).

Thin wrapper around searches/unified_search.quirk_url, so every link in this repo has one form: every qubit
starts in |0> and gets H; each gate is ONE multi-qubit Z(pi/2^l) parity rotation (Quirk "zpar" controls on its
support with a global-phase gate on an extra wire); when k is given, the Clifford corrections on the checks,
Bloch spheres, the inverse of the output and a final H return every qubit to |0>.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "searches"))
from unified_search import quirk_url as _quirk_url  # noqa: E402


def quirk_url(Gf, cf, n, l, k=None):
    """Quirk URL for gates with supports Gf and coefficients cf (units of pi/2^l) on n wires, outputs first."""
    return _quirk_url([(tuple(sorted(S)), c % (1 << l)) for S, c in zip(Gf, cf)], n, l, k=k)
