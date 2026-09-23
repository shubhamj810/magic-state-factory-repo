#!/usr/bin/env python3
"""Reading the gate STRING a source record wrote, so it can be compared with the
gate its columns actually deposit.

This is a separate module because search corpora write the same object at
least seven ways -- ``'T0.T1.T2'``, ``'0+01+012'``, ``'CCZ012-CCZ013'``,
``'CS'``, ``'0-1'``, ``'T^5'``, ``'CS01 . CS02'`` -- and because one of those
forms is actively misleading.  The audit of the two AI corpora merged into this
catalogue found 62 records whose stored ``gate`` disagreed with their columns,
and the bulk of them were ``'T^m'``: a reader takes it for a single ``T`` on
qubit ``m``, the writer meant ``T`` on each of ``m`` outputs.  That is why
`merge_results.py` treats a claimed gate as a claim to be CHECKED, never as
information.

So the parser has three outcomes rather than two:

``('monomials', set)``  the label names a definite monomial set
``('ambiguous', set)``  the label is readable only under a stated convention,
                        and the convention is recorded with it
``('unreadable', None)``

An ambiguous label is never treated as agreement or as disagreement -- it is
reported as what it is.  The verdict on such a record rests on its columns,
which are unambiguous.
"""
from __future__ import annotations

import re

NAMED_ARITY = {"T": 1, "CS": 2, "CCZ": 3}
SEPARATORS = re.compile(r"[.+·*\s]+")
_NAMED = re.compile(r"^([A-Za-z]+)\^?([0-9]+(?:\s*,\s*[0-9]+)*|)$")
_DIGITS = re.compile(r"^[0-9]+$")
_COMMAS = re.compile(r"^[0-9]+(?:,[0-9]+)+$")


def _split(text: str) -> list[str]:
    """Tokenise on every separator any source here uses.

    ``-`` is the awkward one: `factory_records` writes
    ``'CCZ012-CCZ013'`` (a separator) and `ai_campaign` writes ``'0-1'``
    (a single ``CS`` monomial, indices joined).  Splitting on ``-`` only when
    every piece carries a gate NAME keeps both readable.
    """
    text = text.strip()
    if "-" in text and not SEPARATORS.search(text):
        pieces = [p for p in text.split("-") if p]
        if all(_NAMED.match(p) and _NAMED.match(p).group(1) in NAMED_ARITY
               for p in pieces):
            return pieces
        return [text.replace("-", ",")]          # '0-1' is one monomial
    if "-" in text:
        text = text.replace("-", " ")
    return [token for token in SEPARATORS.split(text) if token]


def parse(label, k: int):
    """``(kind, monomials, note)`` for one stored gate string."""
    if not isinstance(label, str) or not label.strip():
        return "unreadable", None, "no gate string"
    body = label.strip()
    if body in ("check-only", "identity", "(identity)"):
        return "monomials", frozenset(), None
    tokens = _split(body)
    if not tokens:
        return "unreadable", None, f"nothing to read in {label!r}"

    monomials, ambiguous, note = set(), False, None

    def repeated(mono):
        """Refuse a factor the label already named, instead of merging it.

        A pi/4 factor squared is Clifford phase -- ``T0.T0`` is ``S0``, not
        ``T0`` -- and a monomial SET cannot say that.  Deduplicating silently
        read ``T0.T0`` as ``T0``, so a label naming a Clifford-equivalent
        product compared EQUAL to a genuine ``T0`` circuit's derived gate and
        passed `merge_results`' claim check.  This parser never guesses, so a
        repeated factor is unreadable, with the reason stated.
        """
        if mono in monomials:
            return True
        monomials.add(mono)
        return False

    for token in tokens:
        named = _NAMED.match(token)
        if named and named.group(1) in NAMED_ARITY:
            name, digits = named.group(1), named.group(2)
            arity = NAMED_ARITY[name]
            if not digits:
                # 'CS' with no indices: the canonical gate on outputs 0..arity-1
                if arity > k:
                    return "unreadable", None, f"{token!r} needs {arity} outputs"
                if repeated(frozenset(range(arity))):
                    return "unreadable", None, (f"{label!r} names the factor "
                                                f"{token!r} more than once; the "
                                                f"repeat is Clifford phase this "
                                                f"grammar cannot carry")
                continue
            if "^" in token:
                # 'T^5': the two readings are a T on qubit 5 and T on five
                # qubits, and the corpus means the second one.
                count = int(digits)
                if name != "T" or count > k:
                    return "unreadable", None, f"cannot read {token!r}"
                for q in range(count):
                    if repeated(frozenset((q,))):
                        return "unreadable", None, (
                            f"{label!r} names T{q} both inside {token!r} and "
                            f"on its own; the repeat is Clifford phase this "
                            f"grammar cannot carry")
                ambiguous = True
                note = (f"{label!r} is the 'T^m' shorthand: read as T on each of "
                        f"{count} outputs, not as a single T on qubit {count}")
                continue
            indices = _indices(digits, arity, k)
            if indices is None:
                return "unreadable", None, f"cannot read indices in {token!r}"
            if len(indices) != arity or len(set(indices)) != arity:
                # ``len`` alone let ``CS00`` through: two digits, so it passed
                # the arity test, and the frozenset then silently collapsed it
                # to a DEGREE-ONE monomial -- a nominal CS that compared equal
                # to a genuine T0.  Distinctness is part of naming a monomial.
                return "unreadable", None, (f"{token!r} does not name {name} "
                                            f"on {arity} distinct qubits")
            if repeated(frozenset(indices)):
                return "unreadable", None, (f"{label!r} names the factor "
                                            f"{token!r} more than once; the "
                                            f"repeat is Clifford phase this "
                                            f"grammar cannot carry")
            continue
        if _COMMAS.match(token):
            raw_parts = token.split(",")
            if any(len(part) > 1 and part[0] == "0" for part in raw_parts):
                return "unreadable", None, (f"{token!r} writes an index with a "
                                            f"leading zero, which this "
                                            f"catalogue never does; the label "
                                            f"is refused rather than guessed "
                                            f"at")
            parts = [int(part) for part in raw_parts]
            if len(set(parts)) != len(parts):
                return "unreadable", None, (f"{token!r} repeats an output "
                                            f"index inside one monomial")
            if len(parts) > 3:
                return "unreadable", None, (f"{token!r} names a degree-"
                                            f"{len(parts)} monomial; this "
                                            f"catalogue's gates are level 3, "
                                            f"degree <= 3")
            if repeated(frozenset(parts)):
                return "unreadable", None, (f"{label!r} names the factor "
                                            f"{token!r} more than once; the "
                                            f"repeat is Clifford phase this "
                                            f"grammar cannot carry")
            continue
        if _DIGITS.match(token):
            if k > 10 and len(token) > 1:
                return "unreadable", None, (f"{token!r} is concatenated digits "
                                            f"at k={k}, which is ambiguous")
            digits = [int(ch) for ch in token]
            if len(set(digits)) != len(digits):
                return "unreadable", None, (f"{token!r} repeats an output "
                                            f"index inside one monomial")
            if len(digits) > 3:
                return "unreadable", None, (f"{token!r} names a degree-"
                                            f"{len(digits)} monomial; this "
                                            f"catalogue's gates are level 3, "
                                            f"degree <= 3")
            if repeated(frozenset(digits)):
                return "unreadable", None, (f"{label!r} names the factor "
                                            f"{token!r} more than once; the "
                                            f"repeat is Clifford phase this "
                                            f"grammar cannot carry")
            continue
        return "unreadable", None, f"cannot read token {token!r}"

    if any(max(mono) >= k for mono in monomials if mono):
        return "unreadable", None, f"{label!r} names an output above k-1"
    return ("ambiguous" if ambiguous else "monomials"), frozenset(monomials), note


def _indices(digits: str, arity: int, k: int):
    """The qubit indices in ``'012'`` or ``'0,1,2'`` for a gate of this arity.

    Source labels mix both inside ONE string --
    ``'CCZ012.CCZ345.CCZ9,10,11'`` -- because the corpora they come from only
    reach for commas once an index passes 9; four such labels are still stored
    in this catalogue's ``sources``.  Both forms are read; a concatenated one is
    only accepted when its digit count is exactly the gate's arity, so
    ``'CCZ123'`` at ``k > 10``, where it could equally be ``CCZ`` on 1, 2, 3 or
    on 1 and 23, is refused rather than guessed at.
    """
    digits = digits.replace(" ", "")
    if "," in digits:
        parts = digits.split(",")
        if any(len(part) > 1 and part[0] == "0" for part in parts):
            # '01' is not a way this catalogue writes 1, so reading it as 1 is
            # a guess -- most such labels are a mangled '0,1' or a concatenated
            # form pasted into the wrong grammar, and this parser never guesses
            return None
        return [int(part) for part in parts]
    if len(digits) == arity:
        return [int(ch) for ch in digits]
    if arity == 1:
        if len(digits) > 1 and digits[0] == "0":
            # 'T01' read as T1 -- or 'T012' at k > 12 read as T12 -- silently
            # dropped the zero; more likely the writer meant T0.T1 or CCZ012
            return None
        return [int(digits)]
    if k <= 10:
        return [int(ch) for ch in digits]
    return None
