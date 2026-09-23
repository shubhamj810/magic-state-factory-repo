"""THE CENSUS ENGINE -- complete ``r <= 7, n <= 44`` check-parent classification.

The window here is set by the *number of check qubits*, not by the T count: it
closes every factory whose check code has effective rank at most 7, for any
n <= 44.  That is a different and complementary cut to the sibling directory
``../exhaustive_n38``, which closes every rank at n <= 38.

OUTER ENUMERATION (which check geometries exist).  A rank-r check part is a set
of points of F_2^r, and the triorthogonality condition makes its indicator a
codeword of RM(3,7) when r <= 7.  So the outer problem is exactly "enumerate
RM(3,7) up to affine equivalence", which Gillot and Langevin have solved: their
table (``data/B-0-3-7.dat``) lists all 3,486 AGL(7,2) orbit representatives.
Of those, 71 have nonzero weight <= 44 and are therefore relevant here.
"Marking" an orbit means choosing which support point becomes the origin;
sweeping all 128 origins of each of the 71 relevant orbits (9,088 marked
geometries) covers effective ranks 4, 5, 6 and 7 in one pass.

INNER ENUMERATION (which gates each geometry carries).  Delegated to
``factorylib.parent`` -- the same machinery exposed by ``../../parent_first`` -- which
classifies gates either under the correct GL(k,2) phase-tensor action
(``dedup='gl'``) or under output permutations only (``dedup='symmetric'``,
i.e. S_k, the key used by the n <= 38 catalogue).

COMPLETENESS.  Every expensive stage carries a budget.  A run that exhausts one
reports ``complete: false``, and **only a run whose top-level ``complete`` is
true is a classification certificate**; anything else is search data.  Reading
those two cases as the same thing is the single most likely way to misuse this
module, so the flag is threaded through every payload it writes.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Iterable

import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))          # run from anywhere: siblings by bare name
sys.path.insert(0, str(HERE.parents[1]))  # shared factorylib package

from factorylib.parent import Parent, certification_metrics, classify_gates  # noqa: E402
from gillot_langevin import (integrity_report, marked_points,         # noqa: E402
                             origin_orbits, parse_file)

#: The bundled Gillot--Langevin orbit table.  See data/README.md for provenance,
#: checksum, third-party rights, and the one audited integrity correction.
DEFAULT_DATA = HERE / "data" / "B-0-3-7.dat"

def window_scope_problems(restrictions) -> list[str]:
    """Why these restrictions do not cover the whole window ([] if they do).

    THE definition of "covers the window", used by both the producer (to set
    ``covers_full_window``) and ``build_catalog.py`` (to recompute it rather than
    believe it).  Sharing one function is the point: the validator used to read
    the boolean and the two top-level convenience fields, so a file whose
    ``restrictions`` said ``class_indices=[306]`` while its boolean said true was
    accepted as a full-window certificate.
    """
    if not isinstance(restrictions, dict):
        return [f"restrictions is {type(restrictions).__name__}, not an object"]
    problems = []
    mode = restrictions.get("mode")
    if mode != "all":
        problems.append(f"restrictions.mode={mode!r}, not 'all' (a covering-"
                        f"representative sweep is not the all-origin census)")
    nmax = restrictions.get("nmax")
    if not isinstance(nmax, int) or isinstance(nmax, bool):
        problems.append(f"restrictions.nmax={nmax!r} is not an integer")
    elif nmax < WINDOW_NMAX:
        problems.append(f"restrictions.nmax={nmax}, below the window's "
                        f"{WINDOW_NMAX}")
    for field in ("class_indices", "origins", "max_parents"):
        # Presence is required, not just a None value: every producer writes
        # these three keys, so a file that simply omits one is hand-made, and
        # reading a missing restriction as "unrestricted" is the same mistake as
        # reading a missing `complete` as complete.  These are also precisely the
        # three fields an audit forged to widen a one-parent run.
        if field not in restrictions:
            problems.append(f"restrictions.{field} is absent, so what the sweep "
                            f"covered is unstated (absence is not consent)")
        elif restrictions[field] is not None:
            problems.append(f"restrictions.{field}={restrictions[field]!r}: the "
                            f"sweep was restricted, so it covers a subset of "
                            f"the window")
    return problems


def data_digest(path: str | Path) -> str:
    """SHA-256 of an orbit table, as recorded in and checked against a census.

    A census identifies its input table by CONTENT, not by where it sat.  The
    census is cluster-scale, so the certificate is generated on one machine and
    consumed in a checkout on another; an absolute path recorded on the cluster
    means nothing there, while this digest means exactly as much in both places.
    """
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


#: The injection-count bound this directory's window is defined by.  A run only
#: certifies that window if it sweeps every marked geometry up to this n.
WINDOW_NMAX = 44


def _atomic_json(path: Path, payload: dict) -> None:
    """Write-then-rename so an interrupted run never leaves malformed JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def iter_parents(
    data: str | Path = DEFAULT_DATA,
    mode: str = "reps",
    nmax: int = 44,
    class_indices: Iterable[int] | None = None,
    origins: Iterable[int] | None = None,
):
    """Yield ``(orbit, origin, points)`` for every selected marked geometry.

    RM(3,7) words have even weight, so the ``nmax + (nmax & 1)`` cap admits a
    weight-(nmax+1) word whose marking at a support point yields n = nmax
    (relevant only for odd ``nmax``); the ``len(points)`` check below then
    enforces the census bound exactly.  In 'reps' mode the ``origins`` filter
    matches the chosen representatives (orbit minima), not all 128 points.
    """
    if mode not in {"reps", "all"}:
        raise ValueError("mode must be 'reps' or 'all'")
    selected_classes = None if class_indices is None else set(class_indices)
    selected_origins = None if origins is None else set(origins)
    for orbit in parse_file(data, 7):
        if selected_classes is not None and orbit.index not in selected_classes:
            continue
        if not 0 < orbit.weight <= nmax + (nmax & 1):
            continue
        choices = range(128) if mode == "all" else (group[0] for group in origin_orbits(orbit))
        for origin in choices:
            if selected_origins is not None and origin not in selected_origins:
                continue
            points = marked_points(orbit, origin)
            if len(points) > nmax:
                continue
            yield orbit, origin, points


@lru_cache(maxsize=8)
def count_parents(data: str | Path = DEFAULT_DATA, nmax: int = WINDOW_NMAX) -> int:
    """How many marked geometries a full ``mode="all"`` sweep must visit.

    One extra pass over the orbit table (seconds) buys the census a check it
    could not otherwise make: that it really did reach every geometry, rather
    than stopping early for a reason nothing recorded.
    """
    return sum(1 for _ in iter_parents(data, mode="all", nmax=nmax))


def run(
    *,
    data: str | Path = DEFAULT_DATA,
    output: str | Path,
    mode: str = "reps",
    nmax: int = 44,
    kmax: int = 4,
    dedup: str = "gl",
    class_indices: Iterable[int] | None = None,
    origins: Iterable[int] | None = None,
    max_parents: int | None = None,
    node_budget: int | None = None,
    orbit_budget: int | None = None,
    checkpoint_every: int = 10,
) -> dict:
    """Run a checkpointed classification and write an honest JSON certificate.

    "Checkpointed" is not "resumable": every ``checkpoint_every`` parents the
    partial result is written atomically, so an interrupted run leaves a valid
    (and honestly ``complete: false``) file rather than a truncated one -- but
    starting the command again begins from the first geometry.  There is no
    resume-from-checkpoint facility.

    ``None`` budgets mean unconstrained enumeration.  ``max_parents`` is only a
    smoke/constrained-run control.  Any hit budget or parent cap makes the
    top-level ``complete`` flag false.
    """
    data_path = Path(data)
    output_path = Path(output)
    integrity = integrity_report(data_path)
    if not integrity["valid"]:
        raise ValueError(f"Gillot--Langevin data failed integrity checks: {integrity}")

    factories: dict[tuple, dict] = {}
    geometries = []
    rank_counts: Counter[int] = Counter()
    processed = 0
    all_complete = True
    capped = False

    # What this invocation actually sweeps.  `complete` used to ignore all of
    # this, so `--class-index 306 --origin 0` -- one parent out of 9,088 -- wrote
    # a certificate claiming the whole r<=7, n<=44 window.  The restrictions are
    # now recorded, the scope string describes what ran, and `complete` requires
    # the sweep to cover the window as well as to finish untruncated.
    restrictions = {
        "mode": mode,
        "nmax": nmax,
        "kmax": kmax,
        "class_indices": (None if class_indices is None
                          else sorted(int(c) for c in class_indices)),
        "origins": (None if origins is None else sorted(int(o) for o in origins)),
        "max_parents": max_parents,
    }
    covers_window = not window_scope_problems(restrictions)
    expected = count_parents(data_path, nmax) if covers_window else None
    if covers_window:
        scope = (f"distance-3 check-parent-first classification, r<=7, "
                 f"n<={WINDOW_NMAX}: all {expected} marked geometries, "
                 f"widths k<={kmax}")
    else:
        limits = ", ".join(
            f"{name}={value}" for name, value in restrictions.items()
            if value is not None and not (name == "nmax" and value >= WINDOW_NMAX))
        scope = (f"RESTRICTED distance-3 check-parent-first run ({limits}); "
                 f"a subset of the r<=7, n<={WINDOW_NMAX} window, not a "
                 f"certificate for it")

    payload = {
        "scope": scope,
        # By content and by name, never by absolute path: `data_name` is for a
        # human reading the file, `data_sha256` is what build_catalog.py checks.
        "data_name": data_path.name,
        "data_sha256": data_digest(data_path),
        "mode": mode,
        "dedup": dedup,
        "kmax": kmax,
        "restrictions": restrictions,
        "covers_full_window": covers_window,
        "geometries_expected": expected,
        "node_budget_per_parent": node_budget,
        "orbit_budget_per_gate": orbit_budget,
        "data_integrity": integrity,
        "complete": False,
        "geometries": geometries,
        "factories": [],
    }

    for orbit, origin, points in iter_parents(
        data_path, mode, nmax, class_indices=class_indices, origins=origins
    ):
        if max_parents is not None and processed >= max_parents:
            capped = True
            break
        # Ambient rank stays 7 even when the marked points span less; the
        # effective check rank (4..7) is reported separately as "rank".
        parent = Parent.from_points(points, ambient_rank=7, distance=3)
        gates = classify_gates(
            parent,
            kmax=kmax,
            dedup=dedup,
            node_budget=node_budget,
            orbit_budget=orbit_budget,
        )
        all_complete &= gates["complete"]
        cheap = {
            "kappa": parent.kappa,
            "quadric_degeneracy": parent.quadric_degeneracy,
        }
        geometry = {
            "class_index": orbit.index,
            "origin": origin,
            "weight": orbit.weight,
            "n": parent.n,
            "rank": parent.check_rank,
            **cheap,
            "gate_search_complete": gates["complete"],
            "n_gates": gates["n_gates"],
            "subspaces_visited": gates["subspaces_visited"],
        }
        geometries.append(geometry)
        rank_counts[parent.check_rank] += 1
        # Census dedup across parents is by (n, k, canonical gate key); the
        # stored r/N/columns are the first witness's, not a canonical parent.
        for gate in gates["gates"]:
            key = (parent.n, gate["k"], json.dumps(gate["canonical_key"], separators=(",", ":")))
            factories.setdefault(
                key,
                {
                    "n": parent.n,
                    "r": parent.check_rank,
                    "N": parent.check_rank + gate["k"],
                    "distance": 3,
                    "class_index": orbit.index,
                    "origin": origin,
                    **gate,
                },
            )
        processed += 1
        # Checkpoints keep the initial "complete": False; only the final
        # write below may certify completeness.
        if checkpoint_every and processed % checkpoint_every == 0:
            payload["processed_parents"] = processed
            payload["rank_counts"] = dict(sorted(rank_counts.items()))
            payload["factories"] = sorted(
                factories.values(), key=lambda item: (item["n"], item["k"], item["canonical_key"])
            )
            _atomic_json(output_path, payload)

    # `complete` = nothing was truncated AND the sweep covered the window.
    # Both halves matter: an untruncated run over one class is still not a
    # statement about r<=7, n<=44, and a full sweep that hit a node budget is
    # not a statement about anything.  Every reason it fails is listed, so a
    # consumer never has to guess which half was missing.
    untruncated = all_complete and not capped
    if covers_window and expected is not None and processed != expected:
        untruncated = False
    reasons = []
    if not all_complete:
        reasons.append("a node or orbit budget was hit inside classify_gates")
    if capped:
        reasons.append(f"stopped early by max_parents={max_parents}")
    if covers_window and expected is not None and processed != expected:
        reasons.append(f"visited {processed} of {expected} marked geometries")
    if not covers_window:
        reasons.append(
            "the sweep was restricted (see `restrictions`), so it covers a "
            f"subset of the r<=7, n<={WINDOW_NMAX} window")
    payload.update(
        processed_parents=processed,
        rank_counts=dict(sorted(rank_counts.items())),
        stopped_by_max_parents=capped,
        untruncated=untruncated,
        complete=untruncated and covers_window,
        incomplete_reasons=reasons,
        factories=sorted(
            factories.values(), key=lambda item: (item["n"], item["k"], item["canonical_key"])
        ),
    )
    _atomic_json(output_path, payload)
    return payload
