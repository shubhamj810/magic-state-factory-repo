"""The checks both unified-search exporters make on a level-3 circuit.

`export_unified.py` and `export_large_unified.py` rebuild each upstream row's
circuit by running the upstream code, then hand it here.  Nothing below comes
from the upstream search: the borrowed-identity condition is `bicheck`'s, and
the gate and the distance are read off the columns by the master catalogue's
fault search (`faultcore`), the error coefficient by `errorcoeff`.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "master_catalog"))

import errorcoeff as EC                                           # noqa: E402
import faultcore as FC                                            # noqa: E402
from bicheck import borrowed_identity_violation, magic            # noqa: E402

LEVEL = 3


_NAMES = {"T": 1, "CS": 2, "CCZ": 3}


def raw_gate(raw):
    """``\\mathrm{CS}_{12}\\mathrm{T}_{3}`` -> ``{(0, 1), (2,)}``, or the
    number of terms for a gate the table abbreviates (``16\\ \\text{terms}``
    -> ``16``)."""
    if "text{terms}" in raw:
        count = re.fullmatch(r"(\d+)\\ \\text\{terms\}", raw)
        if count is None:
            raise SystemExit(f"cannot read the gate {raw!r}")
        return int(count.group(1))
    terms = re.findall(r"\\mathrm\{(T|CS|CCZ)\}_\{(\d+)\}", raw)
    if "".join(rf"\mathrm{{{g}}}_{{{q}}}" for g, q in terms) != raw:
        raise SystemExit(f"cannot read the gate {raw!r}")
    out = set()
    for name, wires in terms:
        if len(wires) != _NAMES[name]:
            raise SystemExit(f"{name} on {wires} in {raw!r}")
        out.add(tuple(sorted(int(q) - 1 for q in wires)))
    return out


def checked(row, gates, where):
    """Stop unless ``gates`` is the row's factory; return its measurements."""
    k, wires, n, d = (int(row[name]) for name in ("k", "N", "n", "d"))
    problems = []
    if len({S for S, _c in gates}) != len(gates):
        problems.append("repeated support")
    if max(q for S, _c in gates for q in S) + 1 != wires:
        problems.append(f"the rotations do not use {wires} wires")
    odd = magic(gates)
    if len(odd) != n:
        problems.append(f"{len(odd)} odd-coefficient rotations, the row says "
                        f"n={n}")
    bad = borrowed_identity_violation(gates, k, LEVEL)
    if bad is not None:
        problems.append(f"monomial {bad} touches a check with genuine "
                        f"level-{LEVEL} phase")
    columns = [list(gates[i][0]) for i in odd]
    gate = {tuple(sorted(m)) for m in
            FC.recover_gate(FC.rows_over_columns(columns, wires), k)}
    want = raw_gate(row["raw"])
    if isinstance(want, int):
        if len(gate) != want:
            problems.append(f"the rotations deposit {len(gate)} monomials, "
                            f"the row says {row['raw']}")
    elif gate != want:
        problems.append(f"the rotations deposit {sorted(gate)}, the row says "
                        f"{row['raw']}")
    report = FC.distance_report(columns, k, wires, budget=FC.Budget())
    if report["d_exact"] != d:
        problems.append(f"measured distance {report['d_exact']} "
                        f"(at least {report['d_at_least']}), the row says {d}")
    if problems:
        raise SystemExit(f"{where}: " + "; ".join(problems))
    a_d = EC.error_coefficient(columns, k, wires, d)["count"]
    return columns, report["witness"], a_d
