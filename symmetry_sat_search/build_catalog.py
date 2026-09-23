#!/usr/bin/env python3
"""Build and verify the catalogue of factories found by symmetry/SAT search.

The search engines write experimental output; only deliberately curated
examples belong in ``examples/found_factories.json``. This builder treats that
file as untrusted input. For every explicit circuit it independently checks
shape, all check-touching parities, the deposited output gate, and fault
distance through weight four. It then recomputes the exact level-3 T-count and
CNOT-frame-reduced degree before writing both catalogue formats.

No solver is imported, so rebuilding published data is cheap and only needs
the base NumPy dependency.

Run from anywhere: ``python symmetry_sat_search/build_catalog.py``.
"""

from __future__ import annotations

import itertools
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import evaluator  # noqa: E402
from factorylib.metrics import metrics_from_named  # noqa: E402

SOURCE = HERE / "examples" / "found_factories.json"
OUT_JSON = HERE / "catalog" / "factories.json"
OUT_MD = HERE / "catalog" / "FACTORY_CATALOG.md"


def matrix_string(columns: list[list[int]], N: int, k: int) -> str:
    """Render a circuit as a binary matrix with output/check row labels."""
    n = len(columns)
    width = max(2, len(str(n - 1)) + 1)
    lines = ["     " + "".join(f"{'g' + str(j):>{width}}" for j in range(n))]
    column_sets = [set(column) for column in columns]
    for qubit in range(N):
        label = f"o{qubit}" if qubit < k else f"c{qubit - k}"
        row = "".join(
            f"{int(qubit in column_sets[j]):>{width}}" for j in range(n)
        )
        lines.append(f"{label:<5}{row}")
    return "\n".join(lines)


def _effective_width(columns: list[list[int]], k: int, N: int) -> int:
    """Rank of the output rows modulo the check span -- the genuine output width.

    An output row may be changed by any element of the check span without
    changing a single parity the gate is read from, so a factory whose output
    rows are DEPENDENT mod that span is a narrower factory on extra wires: one
    output CNOT turns the dependent row into a check-span vector, which carries
    no monomial of any degree, leaving an idle ``|+>`` spectator.

    The extreme case is two identical output rows.  The catalogue used to carry
    one, a ``[[15,2,3]]`` with gate ``T0.T1.CS01`` whose second output row was a
    verbatim copy of the first over the ``[[15,1,3]]`` check part; its exact
    T-count is 1, the same single T the ``[[15,1,3]]`` delivers on one wire
    instead of two.  Such a row is strictly dominated -- same n, same distance,
    same T-count, more wires -- so the builder rejects it rather than publishing
    an inflated width.  The classification engines cannot produce these at all
    (they enumerate frames independent mod the check span), which is why the
    check lives here, on the search side.
    """
    rows = [
        sum(1 << j for j, column in enumerate(columns) if qubit in set(column))
        for qubit in range(N)
    ]
    basis: dict[int, int] = {}

    def insert(value: int) -> bool:
        for pivot in sorted(basis, reverse=True):
            if (value >> pivot) & 1:
                value ^= basis[pivot]
        if value:
            basis[value.bit_length() - 1] = value
            return True
        return False

    for check in rows[k:]:
        insert(check)
    return sum(1 for output in rows[:k] if insert(output))


def _odd_check_monomials(
    columns: list[list[int]], N: int, k: int, level: int
) -> list[tuple[int, ...]]:
    """Return check-touching monomials whose column parity is incorrectly odd."""
    column_sets = [set(column) for column in columns]
    bad = []
    for degree in range(1, level + 1):
        for monomial in itertools.combinations(range(N), degree):
            if monomial[-1] < k:  # output-only: this term describes the gate
                continue
            support = set(monomial)
            if sum(support <= column for column in column_sets) & 1:
                bad.append(monomial)
    return bad


def _verify_record(record: dict) -> dict:
    """Validate one source row and return its fully derived catalogue record."""
    required = {
        "label", "target", "kind", "level", "n", "k", "d", "N",
        "columns", "group", "output_gate", "provenance",
    }
    missing = sorted(required - record.keys())
    if missing:
        raise ValueError(f"{record.get('label', '<unnamed>')}: missing {missing}")

    # Types before meaning.  `examples/found_factories.json` is curated BY HAND,
    # which makes it the likeliest file in the repository to contain a string
    # where an int belongs -- and `N` and `level` bound loops below, so a mistyped
    # one does not fail the check, it hangs it: `level: 2**63` enumerates
    # monomials of every degree up to 2^63.  Every field is checked before it is
    # used for anything.
    label = record["label"]
    if not isinstance(label, str) or not label.strip():
        raise ValueError(f"label is not a non-empty string: {label!r}")
    for key in ("n", "k", "d", "N"):
        value = record[key]
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise ValueError(f"{label}: {key}={value!r} is not a positive integer")
    if record["k"] > record["N"]:
        # Also bounds k for everything below: the output block is qubits
        # 0..k-1 of N, so `k` indexes real wires or the row is nonsense.
        raise ValueError(f"{label}: k={record['k']} outputs do not fit in "
                         f"N={record['N']} qubits")
    if record["level"] not in (2, 3, 4):
        raise ValueError(
            f"{label}: level={record['level']!r} is not a Clifford level this "
            f"catalogue publishes (2: S/CZ, 3: T/CS/CCZ, 4: sqrtT/CT/CCS/CCCZ)")
    for key in ("target", "kind", "group", "output_gate", "provenance"):
        if not isinstance(record[key], str):
            raise ValueError(f"{label}: {key} is a "
                             f"{type(record[key]).__name__}, not a string")
    if not isinstance(record["columns"], list) or not record["columns"]:
        raise ValueError(f"{label}: columns is not a non-empty list")
    for index, column in enumerate(record["columns"]):
        if not isinstance(column, (list, tuple)) or not column or not all(
                isinstance(q, int) and not isinstance(q, bool) for q in column):
            raise ValueError(f"{label}: column {index} is not a non-empty list "
                             f"of qubit indices: {column!r}")

    n, k, stored_d, N = (record[key] for key in ("n", "k", "d", "N"))
    level = record["level"]
    columns = [sorted(set(column)) for column in record["columns"]]
    if len(columns) != n:
        raise ValueError(f"{label}: n={n}, but {len(columns)} columns are stored")
    if any(not column for column in columns):
        raise ValueError(f"{label}: empty columns are not allowed")
    if len({tuple(column) for column in columns}) != n:
        raise ValueError(f"{label}: repeated column (distance is at most 2)")
    if any(qubit < 0 or qubit >= N for column in columns for qubit in column):
        raise ValueError(f"{label}: a column contains a qubit outside 0..{N - 1}")
    used_N = max(max(column) for column in columns) + 1
    if used_N != N:
        raise ValueError(f"{label}: stored N={N}, but explicit columns use N={used_N}")

    bad = _odd_check_monomials(columns, N, k, level)
    if bad:
        raise ValueError(
            f"{label}: {len(bad)} check-touching parities are odd; first={bad[:3]}"
        )

    derived_gate, _, trivial_outputs = evaluator.describe_output(columns, k, level)
    if derived_gate != record["output_gate"]:
        raise ValueError(
            f"{label}: output gate is {derived_gate!r}, not {record['output_gate']!r}"
        )
    if trivial_outputs:
        raise ValueError(
            f"{label}: declared k={k} includes idle output(s) {trivial_outputs}"
        )

    effective = _effective_width(columns, k, N)
    if effective < k:
        raise ValueError(
            f"{label}: declared k={k} but only {effective} output rows are "
            f"independent modulo the check span, so {k - effective} output(s) are "
            f"a Clifford away from idle -- this is a [[{n},{effective},{stored_d}]] "
            f"factory on {k - effective} extra wire(s), carrying no extra magic. "
            f"Publish the width-{effective} circuit instead."
        )

    masks = [sum(1 << qubit for qubit in column) for column in columns]
    derived_d = evaluator._distance(masks, k, 4)
    if derived_d != stored_d:
        relation = ">=" if derived_d == 5 else "="
        raise ValueError(
            f"{label}: stored d={stored_d}, but fault enumeration gives d{relation}{derived_d}"
        )

    t_count, t_note, poly_degree, degree_note = metrics_from_named(
        derived_gate, level
    )
    output = {
        "label": label,
        "target": record["target"],
        "kind": record["kind"],
        "level": level,
        "n": n,
        "k": k,
        "d": stored_d,
        "N": N,
        "columns": columns,
        "source": record["provenance"],
        "group": record["group"],
        "parity_verified": True,
        "distance_verified": True,
        "output_gate": derived_gate,
        "trivial_outputs": [],
        "t_count": t_count,
        "poly_degree": poly_degree,
        "note": "all check parities, output gate, and distance independently verified",
    }
    if t_note:
        output["t_count_note"] = t_note
    if degree_note:
        output["poly_degree_note"] = degree_note
    return output


def load_and_verify() -> list[dict]:
    """Load the curated source, reject duplicates, and verify every circuit."""
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise ValueError(f"{SOURCE}: unsupported or missing schema_version")
    records = [_verify_record(record) for record in payload.get("factories", [])]
    if not records:
        raise ValueError(f"{SOURCE}: no factories")
    # Reject the same CIRCUIT twice.  The identity key deliberately excludes the
    # label: keying on it let a byte-identical circuit through under a second
    # name, which is how three analytic rows (T, CS, CCZ) and their CP-SAT
    # rediscoveries were both published, advertising 60 circuits when 57 were
    # distinct.  Level and k stay in the key, because the same column data at a
    # different Clifford level -- or read with a different output block -- is a
    # genuinely different factory: columns fix the parity structure, the rotation
    # angle is chosen when the circuit is instantiated.  A circuit found twice
    # belongs in ONE row whose provenance records both routes.
    identities = [
        (
            record["level"], record["k"], record["d"],
            tuple(tuple(column) for column in record["columns"]),
        )
        for record in records
    ]
    if len(set(identities)) != len(identities):
        seen: dict[tuple, str] = {}
        for identity, record in zip(identities, records):
            if identity in seen:
                raise ValueError(
                    f"{record['label']!r} is byte-identical to {seen[identity]!r} "
                    f"(same level, k, d and columns): merge them into one row and "
                    f"record both provenances there"
                )
            seen[identity] = record["label"]

    # Labels ARE identifiers: they are how the catalogue, the figures and the
    # theory notes refer to a row, so two rows sharing one make every such
    # reference ambiguous.  Two distinct [[52,1,4]] circuits used to share the
    # label 'T [[52,1,4]]'.
    labels = [record["label"] for record in records]
    duplicated = sorted({label for label in labels if labels.count(label) > 1})
    if duplicated:
        raise ValueError(
            f"labels must be unique -- they identify rows in the catalogue, the "
            f"figures and the theory notes; reused: {duplicated}"
        )
    return records


def _write_json(records: list[dict]) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(
        json.dumps({"factories": records}, indent=2) + "\n", encoding="utf-8"
    )


def _write_markdown(records: list[dict]) -> None:
    groups: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        groups[record["group"]].append(record)

    lines = [
        "# Factory catalogue",
        "",
        "Generated and verified by [`../build_catalog.py`](../build_catalog.py) from",
        "the curated explicit circuits in",
        "[`../examples/found_factories.json`](../examples/found_factories.json).",
        "Do not edit generated files by hand.",
        "",
        "**These are verified search records, not classified maxima.** Absence from",
        "this table is not a nonexistence result; exhaustive statements live in",
        "[`../../classification/`](../../classification/).",
        "",
        f"**{len(records)} factories; every circuit passed parity, gate, and distance checks.**",
        "",
        "## Summary",
        "",
        "`T` is the exact minimal level-3 T-count; `deg` is the CNOT-frame-reduced",
        "phase-polynomial degree. A stored `d=5` means no fault of weight at most",
        "four was found, i.e. the certified lower bound `d>=5`.",
        "",
        "| # | target | [[n,k,d]] | N | level | T | deg | provenance group |",
        "|---:|---|---|---:|---:|---:|---:|---|",
    ]
    for index, record in enumerate(records, 1):
        t_value = "n/a" if record["t_count"] is None else record["t_count"]
        lines.append(
            f"| {index} | {record['target']} | [[{record['n']},{record['k']},{record['d']}]] "
            f"| {record['N']} | {record['level']} | {t_value} | "
            f"{record['poly_degree']} | {record['group']} |"
        )

    index = 0
    for group, group_records in groups.items():
        lines.extend(["", f"## {group}", ""])
        for record in group_records:
            index += 1
            lines.extend([
                f"### {index}. {record['target']} [[{record['n']},{record['k']},{record['d']}]]",
                "",
                f"- output gate: `{record['output_gate']}`",
                f"- ambient qubits: `N={record['N']}`; Clifford level: `{record['level']}`",
                f"- provenance: {record['source']}",
                f"- exact T-count: `{record['t_count']}`; reduced degree: `{record['poly_degree']}`",
                "- verification: all check parities, output gate, and distance re-derived",
                "",
                "Columns (qubit supports):",
                "",
                "```text",
                "[" + ", ".join(
                    "{" + ",".join(map(str, column)) + "}" for column in record["columns"]
                ) + "]",
                "```",
                "",
                "Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):",
                "",
                "```text",
                matrix_string(record["columns"], record["N"], record["k"]),
                "```",
                "",
            ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def build() -> list[dict]:
    """Verify the curated examples and regenerate both catalogue formats."""
    records = load_and_verify()
    _write_json(records)
    _write_markdown(records)
    print(f"catalogue: {len(records)} factories, all verified")
    print(f"  -> {OUT_JSON.relative_to(HERE)}")
    print(f"  -> {OUT_MD.relative_to(HERE)}")
    return records


if __name__ == "__main__":
    build()
