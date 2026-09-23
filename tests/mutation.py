"""A mutation sweep for the repository's acceptance boundaries.

WHAT THIS IS FOR
----------------
Every published claim here rests on some function deciding that a file, or a run,
or a row is good enough to publish.  Four rounds of adversarial audit found the
same defect five times, never in a result and always in one of those decisions:
a field the documentation said was checked and the code did not read, or read
too generously.  Each was fixed with a test for that exact case, which is a
losing game -- the next unchecked field is found by the next audit, not by the
suite.

This module inverts that.  Instead of testing the cases someone thought of, it
takes an artifact the boundary ACCEPTS, mutates every field in it one at a time
through a battery of substitutions, and requires each mutation to be either

  * REJECTED, or
  * declared -- in the boundary's own definition, with a reason -- as a field
    that cannot weaken the claim, or as a change that leaves the claim true.

Nothing may simply be ignored.  The consequence is the property that makes this
maintainable: when a field is ADDED to a certificate, the sweep starts mutating
it automatically, and the suite fails until someone either validates the field or
says in one line why it does not matter.  Coverage grows with the schema instead
of with the audit history.

It also requires that no mutation makes a validator RAISE.  A validator that
crashes on malformed input has not rejected it -- the caller sees a traceback
from inside a library instead of a verdict, and that is how an `int` in a
`data_sha256` field crashed the census gate while it was building the very error
message that would have rejected it.

WHAT IT DOES NOT DO
-------------------
It does not check that accepted artifacts are CORRECT: that is what the per-
directory suites do, by re-deriving every published number from raw columns.
This is only about the boundary -- what gets in.

Baselines are real wherever a real one exists (the shipped result passes, the
shipped catalogue rows, a genuine census run patched to full-window scope), so
the sweep tests the shape the producers actually write rather than a shape
invented here.
"""
from __future__ import annotations

import copy
import re
from dataclasses import dataclass, field
from typing import Callable, Iterator

#: Marker for "remove this key entirely" -- the mutation that catches a
#: validator using `.get(name)` without deciding what a missing name means.
DELETE = object()

#: Substitutions applied to every leaf.  Deliberately includes the values that
#: pass a falsiness test but not a type check (`1` for a flag), the values that
#: crash string handling (`{}` where a digest is expected), and one absurd
#: integer, because "n is large" and "n is wrong" are different bugs.
SUBSTITUTES = (
    DELETE, None, True, False, 0, 1, -1, 3.5, "", "garbage", [], {},
    2 ** 63, [0], {"garbage": True},
)


def _describe(value) -> str:
    if value is DELETE:
        return "<deleted>"
    return repr(value)


def leaf_paths(obj, prefix: str = "", skip: tuple[str, ...] = ()) -> list[str]:
    """Dotted paths to every leaf in a JSON-shaped object.

    Dict keys join with ``.``; list elements are ``[i]``.  A path matching one of
    `skip` (by prefix) is returned as a leaf without being descended into, so a
    boundary can say "mutate `factories` as a whole, not its 74 rows" -- the
    contents of a result list are the per-row suites' subject, not the gate's.
    """
    if any(prefix == s or prefix.startswith(s + ".") or prefix.startswith(s + "[")
           for s in skip):
        return [prefix]
    if isinstance(obj, dict) and obj:
        out = []
        for key, value in obj.items():
            child = f"{prefix}.{key}" if prefix else str(key)
            out += leaf_paths(value, child, skip)
        return out
    if isinstance(obj, list) and obj:
        # One element is enough: a list of records is validated by the same code
        # for every element, and mutating all of them multiplies runtime without
        # covering anything new.
        return leaf_paths(obj[0], f"{prefix}[0]", skip)
    return [prefix]


def _split(path: str) -> list:
    parts: list = []
    for token in re.findall(r"[^.\[\]]+|\[\d+\]", path):
        parts.append(int(token[1:-1]) if token.startswith("[") else token)
    return parts


def get_path(obj, path: str):
    for part in _split(path):
        obj = obj[part]
    return obj


def with_mutation(obj, path: str, value):
    """A deep copy of `obj` with `path` set to `value` (or deleted)."""
    out = copy.deepcopy(obj)
    parts = _split(path)
    target = out
    for part in parts[:-1]:
        target = target[part]
    last = parts[-1]
    if value is DELETE:
        del target[last]
    else:
        target[last] = value
    return out


@dataclass
class Boundary:
    """One acceptance decision, and what may and may not get past it.

    ``validate`` takes an artifact and returns the list of reasons it is not
    acceptable -- empty means accepted.  A boundary whose real code signals
    rejection by raising wraps it (see ``rejects_by_raising``).

    ``benign`` maps a path prefix to the reason mutating it cannot weaken the
    claim.  ``tolerates`` is for changes that leave the claim TRUE rather than
    unexamined -- a wider sweep than the window, a larger width than required --
    and is asked about a specific (path, value).

    ``overstates`` is the honest third case.  Some mutations make an artifact
    claim MORE than it did: a pass that recorded deferring a class, edited to say
    it swept that class after all.  No consistency check can refute that -- only
    re-running the pass can -- so the sweep accepts these, and requires the
    boundary to name them, so the limit of what it verifies is written down
    rather than discovered by the next audit.
    """
    name: str
    claim: str
    baseline: object
    validate: Callable[[object], list]
    benign: dict[str, str] = field(default_factory=dict)
    tolerates: Callable[[str, object], bool] = lambda path, value: False
    overstates: Callable[[str, object], bool] = lambda path, value: False
    skip: tuple[str, ...] = ()

    def is_benign(self, path: str) -> str | None:
        for prefix, reason in self.benign.items():
            if path == prefix or path.startswith(prefix + ".") \
                    or path.startswith(prefix + "["):
                return reason
        return None

    def mutations(self) -> Iterator[tuple[str, object, object]]:
        """(path, substituted value, mutated artifact) for the whole battery."""
        for path in leaf_paths(self.baseline, skip=self.skip):
            current = get_path(self.baseline, path)
            values = list(SUBSTITUTES)
            if isinstance(current, bool):
                values.append(not current)
            elif isinstance(current, int):
                values += [current + 1, current - 1]
            elif isinstance(current, str):
                values.append(current + "x")
            elif isinstance(current, list):
                values.append(current + current)
            for value in values:
                if value is not DELETE and value == current \
                        and type(value) is type(current):
                    continue          # not a mutation
                yield path, value, with_mutation(self.baseline, path, value)


def rejects_by_raising(call: Callable, expected: type | tuple[type, ...]):
    """Adapt a validator that RAISES on rejection into one that returns reasons.

    Only `expected` counts as a rejection.  Any other exception is a crash and
    propagates, which is the point: a validator that dies with `KeyError` has not
    rejected anything, it has failed.
    """
    def validate(artifact) -> list:
        try:
            call(artifact)
        except expected as error:
            return [str(error) or error.__class__.__name__]
        return []
    return validate


def sweep(case, boundary: Boundary) -> dict:
    """Assert the boundary holds under every mutation.  Returns a small summary.

    `case` is a `unittest.TestCase`.  Three things are asserted, in this order,
    because they fail for different reasons and the message matters:

      1. the honest baseline is ACCEPTED -- otherwise every rejection below is
         vacuous and the sweep proves nothing;
      2. no mutation makes the validator raise;
      3. every mutation is rejected, unless the boundary declares the field
         benign, tolerates that particular value, or names it as one the
         artifact can only OVERSTATE (see `Boundary.overstates`).
    """
    problems = boundary.validate(boundary.baseline)
    case.assertEqual(
        list(problems), [],
        f"{boundary.name}: the honest baseline must be accepted, or the whole "
        f"sweep is vacuous. Rejected because: {problems}")

    counts = {"rejected": 0, "benign": 0, "tolerated": 0, "overstated": 0}
    for path, value, mutated in boundary.mutations():
        label = f"{boundary.name}: {path} = {_describe(value)}"
        with case.subTest(mutation=label):
            try:
                found = boundary.validate(mutated)
            except Exception as error:                      # noqa: BLE001
                raise AssertionError(
                    f"{label} made the validator RAISE "
                    f"{type(error).__name__}: {error}. Malformed input must be "
                    f"rejected with a reason, not crash the check.") from error
            reason = boundary.is_benign(path)
            if reason is not None:
                counts["benign"] += 1
                continue
            if boundary.tolerates(path, value):
                case.assertEqual(
                    list(found), [],
                    f"{label} still satisfies the claim, so it must be "
                    f"accepted, but was rejected: {found}")
                counts["tolerated"] += 1
                continue
            if boundary.overstates(path, value):
                case.assertEqual(
                    list(found), [],
                    f"{label} makes the artifact claim MORE than the baseline "
                    f"did, which only a rerun can refute -- it must be accepted "
                    f"here, but was rejected: {found}")
                counts["overstated"] += 1
                continue
            case.assertTrue(
                found,
                f"{label} was ACCEPTED. {boundary.claim} If this field cannot "
                f"weaken that claim, add it to the boundary's `benign` map with "
                f"the reason; otherwise the validator must check it.")
            counts["rejected"] += 1
    return counts
