"""Render a factory's gate list as an actual clickable Quirk circuit.

Quirk (https://algassert.com/quirk) circuits are a JSON object `{"cols": [...]}`
of columns, each a list with one entry per wire (`1` = nothing on that wire),
URL-encoded after `#circuit=`.

Every gate here is a multi-qubit Z-type parity rotation on a qubit support
`S` -- exp(i*theta*(parity of S)), theta = +-pi/2^l -- with no native
multi-qubit Quirk gate for arbitrary `S`. The standard ancilla-free encoding:
pick one qubit in `S` as the "hub", CNOT every other qubit in `S` onto the
hub (computing the parity of `S` there), apply the single-qubit phase gate
on the hub, then undo the CNOTs. This is exactly the "CNOT-ladder into one
phase gate" construction referenced in the pipeline notebook and in
`export_circuit.py`.
"""
import json
import urllib.parse

# weight-1 gate at level l, matching GATE_BY_SIZE in classify.py (S/T/sqrtT/...)
_PHASE_GATE = {2: "Z^½", 3: "Z^¼", 4: "Z^⅛"}


def phase_gate_name(l, sign):
    """Quirk's single-qubit Z-rotation gate name for level l (theta=pi/2^l),
    dagger'd if sign < 0."""
    if l not in _PHASE_GATE:
        raise ValueError(f"no Quirk gate name registered for l={l}")
    name = _PHASE_GATE[l]
    return name if sign > 0 else name.replace("^", "^-")


def circuit_to_quirk_cols(Gf, cf, n, l):
    """[[gate-per-wire, ...], ...] Quirk columns for a gate list (Gf, cf) on
    n wires at level l. One multi-qubit gate becomes several columns (the
    CNOT-ladder in, the phase gate, the CNOT-ladder out); single-qubit gates
    are one column."""
    cols = []

    def add_column(assignment):
        col = ["1"] * n
        for wire, gate in assignment.items():
            col[wire] = gate
        cols.append(col)

    for supp, sign in zip(Gf, cf):
        support = sorted(supp)
        if len(support) == 1:
            add_column({support[0]: phase_gate_name(l, sign)})
            continue
        hub, others = support[0], support[1:]
        for other in others:
            add_column({hub: "X", other: "•"})
        add_column({hub: phase_gate_name(l, sign)})
        for other in reversed(others):
            add_column({hub: "X", other: "•"})
    return cols


def quirk_url(Gf, cf, n, l, base="https://algassert.com/quirk"):
    """A clickable Quirk URL for the factory's circuit (up to global phase).
    Output wires are drawn first (wires 0..k-1), then check wires, matching
    every other column/matrix representation in this repo."""
    cols = circuit_to_quirk_cols(Gf, cf, n, l)
    circuit = {"cols": cols}
    return f"{base}#circuit={urllib.parse.quote(json.dumps(circuit), safe='')}"
