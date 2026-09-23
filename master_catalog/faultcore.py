#!/usr/bin/env python3
"""Column-level primitives for auditing a factory, written for the scale the
widest catalogued rows reach (``n`` to 1023, ``k`` to 162, ``N`` to 176).

The literal enumerations at the bottom of `verify_catalog.py` re-derive
everything from columns too, but they are written for the classification
catalogues -- ``n <= 63``, ``k <= 6`` -- and are quadratic-or-worse in exactly
the places that matter here: ``itertools.combinations(range(k), 3)`` is 690k
monomials at ``k = 162``, and a weight-4 distance pass is
``C(n, 4) = 4.5e10`` subsets at ``n = 1023``.  This
module answers the same questions with bit-level and meet-in-the-middle
algorithms, and it is deliberately a SEPARATE implementation: the small-circuit
routines stay where they are, and `tests/test_faultcore.py` pins the two against
each other on every circuit both can run.

WHAT A FACTORY IS (theory/01_factories_and_distance.md)
------------------------------------------------------
``N = k + r`` wires; outputs ``0..k-1``, postselected checks ``k..N-1``.  A
circuit is a list of *columns*, each the qubit support of one ``pi/4`` parity
rotation.  Stack them into a binary matrix with one ROW per wire.  Then:

  * the deposited gate is the set of degree-1/2/3 output monomials whose row
    overlap has ODD weight (``|a_i|``, ``|a_i & a_j|``, ``|a_i & a_j & a_l|``);
  * it is a factory iff every degree-<=3 parity TOUCHING a check row is even;
  * a fault set is undetectable when its syndromes XOR to zero, and damaging
    when its output parts do not; the distance is the least weight of a fault
    that is both.

Everything here is computed on those rows and columns and nothing else.

ABSENCE IS PROVED, PRESENCE IS WITNESSED
----------------------------------------
Every scan returns one of three things -- ``clean`` (ran to completion, nothing
there), ``found`` (an explicit fault, re-checkable in three lines), or
``skipped`` (the budget stopped it, so NOTHING is proved).  A distance is called
exact only when a clean sweep below it meets a witness at it.  Everything else
is a floor and says so.
"""
from __future__ import annotations

import itertools
import random
from typing import Iterable, Sequence

try:                                            # numpy is used only to go fast
    import numpy as np
except Exception:                               # pragma: no cover - no numpy
    np = None

# The sampling witness search is seeded, so a rerun reproduces the same witness.
_RNG_SEED = 20260826


# --------------------------------------------------------------- row/column form
def rows_over_columns(columns: Sequence[Sequence[int]], N: int) -> list[int]:
    """Row ``q`` as a bitmask over COLUMN indices: bit ``j`` set iff ``q in c_j``.

    This transpose is what makes every parity below a popcount: the overlap
    ``|a_i & a_j & a_l|`` is ``popcount(rows[i] & rows[j] & rows[l])``, one
    machine word per 64 columns instead of a scan over the columns.
    """
    rows = [0] * N
    for j, column in enumerate(columns):
        bit = 1 << j
        for q in column:
            # Validated here and not left to the caller, because Python would
            # otherwise read a malformed label as a DIFFERENT circuit rather
            # than an error: ``rows[-1]`` is the last wire, not a crash, and a
            # boolean indexes as 0 or 1.  A conversion primitive that silently
            # relocates a rotation is worse than one that refuses.
            if type(q) is not int or not 0 <= q < N:
                raise ValueError(f"wire label {q!r} in column {j} is outside "
                                 f"0..{N - 1}")
            rows[q] |= bit
    return rows


def column_masks(columns: Sequence[Sequence[int]], N: int) -> list[int]:
    """Column ``j`` as a bitmask over WIRE indices -- the fault label.

    OR, not addition: they agree only while a column never repeats a wire, and
    a mask builder is exactly the place a raw, unnormalised column arrives.
    ``sum(1 << q ...)`` turns a repeated wire into a CARRY -- ``[0, 0]`` becomes
    bit 1, a rotation on a wire the column never touches -- which is a silently
    different circuit, not an error.  Out-of-range labels are refused for the
    same reason as in `rows_over_columns`.
    """
    masks = []
    for j, column in enumerate(columns):
        mask = 0
        for q in column:
            if type(q) is not int or not 0 <= q < N:
                raise ValueError(f"wire label {q!r} in column {j} is outside "
                                 f"0..{N - 1}")
            mask |= 1 << q
        masks.append(mask)
    return masks


def _odd(value: int) -> bool:
    """Odd popcount, via ``int.bit_count`` rather than ``bin(x).count('1')``.

    The rows here are bitmasks over COLUMNS, so at ``n = 1023`` every parity is
    a popcount of a thousand-bit integer, and ``bin(...)`` materialises a
    thousand-character string for each one.  `check_contamination` alone asks
    for ``C(176, 3)`` of them on the widest circuit, which is where most of a
    build went before this was a native call.
    """
    return value.bit_count() & 1 == 1


# ------------------------------------------------------------------- the gate
def recover_gate(rows: Sequence[int], k: int) -> frozenset:
    """The monomial set the columns deposit on the outputs.

    Degrees 1, 2 and 3 exhaust it: a column with support ``S`` contributes
    ``+/- 2^(t-1)`` to the ``Z_8`` coefficient of a degree-``t`` monomial, which
    vanishes mod 8 for ``t >= 4``.  So a level-3 circuit's whole non-Clifford
    content is these three parities, and there is nothing above them to miss.
    """
    gate = set()
    for i in range(k):
        if _odd(rows[i]):
            gate.add(frozenset((i,)))
    for i in range(k):
        ri = rows[i]
        if not ri:
            continue
        for j in range(i + 1, k):
            pair = ri & rows[j]
            if not pair:
                continue
            if _odd(pair):
                gate.add(frozenset((i, j)))
            for l in range(j + 1, k):
                triple = pair & rows[l]
                if triple and _odd(triple):
                    gate.add(frozenset((i, j, l)))
    return frozenset(gate)


def check_contamination(rows: Sequence[int], k: int, N: int,
                        limit: int = 8) -> list[tuple[int, ...]]:
    """Degree-<=3 monomials that TOUCH a check wire and have odd parity.

    The factory condition is that this list is empty: triorthogonality of the
    check block, plus the mixed output-check conditions.  A non-empty list means
    the circuit deposits phase on a postselected wire, so the accepted action is
    not the gate the outputs claim.  Returns at most ``limit`` witnesses -- this
    is a rejection reason, not a census.
    """
    if limit < 1:
        # ``limit=0`` cannot mean anything: the return value would be [] both
        # for a clean circuit and for a contaminated one, which is the one
        # conflation this module exists to prevent.  The old behaviour --
        # append first, test the cap second -- quietly returned one witness
        # anyway, so the documented contract held for no value of ``limit``
        # below 1.
        raise ValueError(f"limit must be at least 1, not {limit!r}: a caller "
                         f"that wants no witnesses cannot tell clean from "
                         f"contaminated")
    bad: list[tuple[int, ...]] = []
    for i in range(N):
        ri = rows[i]
        if i >= k and ri and _odd(ri):
            bad.append((i,))
            if len(bad) >= limit:
                return bad
    for i in range(N):
        ri = rows[i]
        if not ri:
            continue
        for j in range(i + 1, N):
            pair = ri & rows[j]
            if not pair:
                continue
            if j >= k and _odd(pair):
                bad.append((i, j))
                if len(bad) >= limit:
                    return bad
            for l in range(j + 1, N):
                triple = pair & rows[l]
                if triple and l >= k and _odd(triple):
                    bad.append((i, j, l))
                    if len(bad) >= limit:
                        return bad
    return bad


# ------------------------------------------------- outputs modulo the check span
def output_report(rows: Sequence[int], k: int, N: int) -> dict:
    """Are the ``k`` output rows genuinely ``k`` independent logical qubits?

    The classification quotient is ``V = R(C)/C``: everything the gate reads off
    an output row is invariant under ``a -> a + c`` for ``c`` in the check span
    ``C``, so an output row is only defined modulo ``C``, and a ``k``-output
    factory is a ``k``-subset of ``V`` that is LINEARLY INDEPENDENT.  A circuit
    whose outputs are dependent mod ``C`` is not a width-``k`` factory: it is a
    narrower one wearing a wider label, and ``k`` is the denominator of every
    rate anyone will quote from it.

    Four named ways that fails, kept apart because they read very differently:

    ``duplicate_rows``    two output rows equal as vectors -- a literal copy.
    ``equal_mod_checks``  ``a_i + a_j`` in ``C``: the same logical qubit twice,
                          one of them dressed with a stabiliser.
    ``in_check_span``     ``a_i`` in ``C``: a logical qubit that is not one.
    ``other_dependence``  any remaining dependence, e.g. ``a_i + a_j + a_l``
                          in ``C``.

    ``effective_width`` is the rank of the outputs modulo ``C``; the circuit is
    a genuine width-``k`` factory iff it equals ``k``.
    """
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
    check_span_basis = dict(basis)

    def in_check_span(value: int) -> bool:
        for pivot in sorted(check_span_basis, reverse=True):
            if (value >> pivot) & 1:
                value ^= check_span_basis[pivot]
        return value == 0

    outputs = list(rows[:k])
    in_span = [i for i in range(k) if in_check_span(outputs[i])]
    duplicate_rows, equal_mod_checks = [], []
    for i in range(k):
        for j in range(i + 1, k):
            if outputs[i] == outputs[j]:
                duplicate_rows.append([i, j])
            elif in_check_span(outputs[i] ^ outputs[j]):
                equal_mod_checks.append([i, j])

    width, dependent = 0, []
    for i, output in enumerate(outputs):
        if insert(output):
            width += 1
        else:
            dependent.append(i)
    named = set(in_span) | {q for pair in duplicate_rows + equal_mod_checks
                            for q in pair}
    return {
        "effective_width": width,
        "independent": width == k,
        "duplicate_rows": duplicate_rows,
        "equal_mod_checks": equal_mod_checks,
        "in_check_span": in_span,
        "other_dependence": [q for q in dependent if q not in named],
    }


def spectators(gate: Iterable[frozenset], k: int) -> list[int]:
    """Output qubits the recovered gate never touches -- padding, not magic."""
    touched: set[int] = set()
    for mono in gate:
        touched |= set(mono)
    return [q for q in range(k) if q not in touched]


def redundant_checks(rows: Sequence[int], k: int, N: int) -> list[int]:
    """Check wires that carry no syndrome bit of their own -- dead postselection.

    The check-side twin of a pseudo-output, and it fails for the same reason:
    a row that is not independent is a label, not a degree of freedom.  A fault
    set ``F`` gives check wire ``w`` the bit ``<F, rows[w]>``, so when
    ``rows[w]`` lies in the span of the OTHER check rows that bit is the XOR of
    theirs for EVERY fault -- the wire can never reject anything they accept,
    and postselecting on it is free in the useless sense.

    Such a wire is always deletable.  Removing it from every column it appears
    in leaves ``n``, ``k``, the gate and the distance exactly as they were: the
    output rows are untouched, monomials not involving ``w`` keep their
    parities, and the undetectable sets are unchanged because the bit that
    disappears was already determined by the ones that remain.  The two ways
    the deletion could go wrong are both ruled out by the dependence itself --
    two columns differing only in ``w`` would be a fault whose ONLY nonzero
    syndrome bit is ``w``, and a column equal to ``{w}`` would be another, and
    a determined bit cannot be a lone nonzero one.

    So a row carrying such a wire publishes an ``N`` one larger than its
    circuit needs, and ``N`` is both the headline ambient-qubit cost and the
    tie-break `merge_results.py` minimises on when it keeps one circuit per
    class.  Returned in wire order: the wires a left-to-right independence pass
    finds already spanned by those before them.
    """
    basis: dict[int, int] = {}
    dependent = []
    for wire in range(k, N):
        value = rows[wire]
        for pivot in sorted(basis, reverse=True):
            if (value >> pivot) & 1:
                value ^= basis[pivot]
        if value:
            basis[value.bit_length() - 1] = value
        else:
            dependent.append(wire)
    return dependent


# ----------------------------------------------------------------- fault search
class Budget:
    """What the fault search is allowed to spend.

    The defaults are set from the two corpora being audited: ``max_pairs`` clears
    ``n = 1023`` (523k pairs), ``max_triples`` clears the ``n ~ 910`` weight-5
    sweep under numpy, and ``max_triple_table`` clears ``n = 256`` at weight 6
    while refusing ``n ~ 900``, where the table alone would be a gigabyte.
    """

    def __init__(self, max_pairs: int = 600_000, max_triples: int = 200_000_000,
                 max_triple_table: int = 6_000_000, max_candidates: int = 3_000_000,
                 witness_samples: int = 200_000, count_upto_n: int = 260):
        self.max_pairs = max_pairs
        self.max_triples = max_triples
        self.max_triple_table = max_triple_table
        self.max_candidates = max_candidates
        self.witness_samples = witness_samples
        self.count_upto_n = count_upto_n


def _syndrome_output(columns, k):
    """Split every column into (syndrome, output part) as plain ints."""
    syn, out = [], []
    for column in columns:
        s = o = 0
        for q in column:
            if q < k:
                o |= 1 << q
            else:
                s |= 1 << (q - k)
        syn.append(s)
        out.append(o)
    return syn, out


def _fold(values: list[int], r: int, seed: int = 0x5bd1e995):
    """An F_2-LINEAR fold of ``r``-bit syndromes into 64 bits, for bulk work.

    Above ``r = 64`` a syndrome no longer fits a machine word, and the four
    circuits here that reach it (``r = 87, 88, 89, 111``) are also the largest,
    so plain Python ints would be hopeless.  Folding by a random linear map preserves
    XOR, so a fault set whose true syndromes cancel has folded syndromes that
    cancel too: **the fold has no false negatives**, which is the direction a
    proof of absence depends on.  It can create false positives, so every hit is
    re-checked against the exact syndrome before it is believed.  Values that
    already fit are returned unchanged.
    """
    if r <= 64:
        return values, False
    rng = random.Random(seed)
    images = [rng.getrandbits(64) for _ in range(r)]
    folded = []
    for value in values:
        acc, v = 0, value
        while v:
            low = v & -v
            acc ^= images[low.bit_length() - 1]
            v ^= low
        folded.append(acc)
    return folded, True


class Circuit:
    """A circuit plus the derived tables every scan below shares."""

    def __init__(self, columns, k, N, budget: Budget | None = None):
        # Every raw label is validated BEFORE ``set``/``sorted`` touch it,
        # because both of those read malformed input as something else rather
        # than failing: ``sorted`` puts ``True`` between 0 and 2 (it compares
        # as 1), so an end-of-column check saw a valid first element and an
        # in-range last one and let ``[0, True]`` through as wires 0 and 1 --
        # and a mixed-type column crashed inside ``sorted`` with a TypeError
        # instead of being refused.  The scans below split every wire into an
        # output bit (``q < k``) or a syndrome bit (``q - k``), so a label that
        # slips past here does not crash later; it folds into the WRONG bit and
        # verifies a circuit nobody wrote.
        checked = []
        for j, raw in enumerate(columns):
            for q in raw:
                if type(q) is not int or not 0 <= q < N:
                    raise ValueError(f"wire label {q!r} in column {j} is "
                                     f"outside 0..{N - 1}")
            checked.append(tuple(sorted(set(raw))))
        self.columns = checked
        self.k, self.N = k, N
        self.n = len(self.columns)
        self.budget = budget or Budget()
        self.syn, self.out = _syndrome_output(self.columns, k)
        self.syn64, self.folded = _fold(self.syn, N - k)
        self._pairs = "unset"
        self._np_pairs = "unset"

    # -- exact predicate, always on the TRUE syndromes ------------------------
    def harmful(self, indices) -> bool:
        s = o = 0
        for index in indices:
            s ^= self.syn[index]
            o ^= self.out[index]
        return s == 0 and o != 0

    # -- pair table ----------------------------------------------------------
    @property
    def pairs(self):
        """``{folded syndrome XOR: [(i, j), ...]}`` over all column pairs."""
        if self._pairs == "unset":
            if self.n * (self.n - 1) // 2 > self.budget.max_pairs:
                self._pairs = None
            else:
                table: dict[int, list[tuple[int, int]]] = {}
                syn64 = self.syn64
                for i in range(self.n):
                    si = syn64[i]
                    for j in range(i + 1, self.n):
                        table.setdefault(si ^ syn64[j], []).append((i, j))
                self._pairs = table
        return self._pairs

    @property
    def np_pairs(self):
        """The same pairs as numpy arrays, ordered by ``i`` so ``i > t`` is a
        contiguous suffix -- which is what lets the weight-5 sweep run one
        vectorised pass per column instead of one per pair."""
        if self._np_pairs == "unset":
            if np is None or self.pairs is None:
                self._np_pairs = None
            else:
                n = self.n
                total = n * (n - 1) // 2
                pi = np.empty(total, dtype=np.int32)
                pj = np.empty(total, dtype=np.int32)
                psyn = np.empty(total, dtype=np.uint64)
                offset = np.zeros(n + 1, dtype=np.int64)
                syn64 = self.syn64
                at = 0
                for i in range(n):
                    offset[i] = at
                    span = n - i - 1
                    if span:
                        pi[at:at + span] = i
                        pj[at:at + span] = np.arange(i + 1, n, dtype=np.int32)
                        psyn[at:at + span] = (
                            np.uint64(syn64[i])
                            ^ np.array(syn64[i + 1:], dtype=np.uint64))
                        at += span
                offset[n - 1] = at
                offset[n] = at
                self._np_pairs = (pi, pj, psyn, offset)
        return self._np_pairs


class _Collector:
    """Accumulates harmful faults for one weight: the first witness and, when
    asked, the exact count.

    A tiny object rather than a closure because the weight-5 sweep has to ask
    "have we got one yet?" from inside a vectorised loop, and reading that back
    out of a closure cell is the kind of cleverness that quietly stops working.
    """

    def __init__(self, circuit, want_count):
        self.circuit = circuit
        self.want_count = want_count
        self.witness = None
        self.count = 0
        self.overflow = False

    def offer(self, indices) -> bool:
        """Record ``indices`` if it is genuinely harmful; True when it was."""
        if not self.circuit.harmful(indices):
            return False
        self.count += 1
        if self.witness is None:
            self.witness = tuple(sorted(indices))
        return True

    @property
    def stop(self) -> bool:
        """A witness is all the caller wanted, so the sweep can end here."""
        return self.witness is not None and not self.want_count

    def done(self, divisor):
        return ("found" if self.witness is not None else "clean", self.witness,
                (self.count // divisor) if self.want_count else None)


def scan_weight(circuit: Circuit, weight: int, want_count: bool = False):
    """Harmful faults of exactly ``weight``: ``(status, witness, count)``.

    ``status`` is ``'clean'`` / ``'found'`` / ``'skipped'`` as described in the
    module docstring.  ``count`` is exact when ``want_count`` and the scan ran to
    completion, else ``None`` -- a count of ``0`` and "did not look" are never
    the same value.

    Each weight is a meet-in-the-middle against the pair table, so every harmful
    fault is visited several times and the raw tally is divided by how many:
    ``3`` at weight 3 (once per element), ``3`` at weight 4 (splits into two
    pairs), ``10`` at weight 5 (``C(5,3)`` triple/pair splits) and ``10`` at
    weight 6 (``C(6,3)/2`` unordered triple splits).
    """
    n, budget = circuit.n, circuit.budget
    syn64 = circuit.syn64
    if weight > n:
        return "clean", None, (0 if want_count else None)
    box = _Collector(circuit, want_count)

    if weight == 1:
        for i in range(n):
            if box.offer((i,)) and box.stop:
                break
        return box.done(1)

    if weight == 2:
        buckets: dict[int, list[int]] = {}
        for i in range(n):
            buckets.setdefault(syn64[i], []).append(i)
        # On a valid factory every bucket has one member -- two columns with
        # equal syndrome are a weight-2 fault or a repeated column -- so this
        # loop is O(n).  On degenerate input the buckets collapse and the pair
        # enumeration is C(n, 2), which is exactly the work `max_candidates`
        # exists to bound everywhere else, so it is honoured here too.  The
        # budget is charged per pair EXAMINED, not per bucket up front: in the
        # common degenerate case the very first pair of a big bucket is a
        # harmful witness, and a scan that pre-skipped the bucket threw that
        # witness away to save work it never had to do.  A witness found
        # within budget is "found"; running out while counting or while every
        # examined pair is benign (duplicate columns, or fold collisions above
        # ``r = 64``) is "skipped", never an unbounded run.
        seen = 0
        for members in buckets.values():
            for i, j in itertools.combinations(members, 2):
                seen += 1
                if seen > budget.max_candidates:
                    return "skipped", None, None
                if box.offer((i, j)) and box.stop:
                    return box.done(1)
        return box.done(1)

    pairs = circuit.pairs
    if pairs is None:
        return "skipped", None, None

    if weight == 3:
        for l in range(n):
            for (i, j) in pairs.get(syn64[l], ()):
                if l == i or l == j:
                    continue
                if box.offer((i, j, l)) and box.stop:
                    return box.done(3)
        return box.done(3)

    if weight == 4:
        seen = 0
        for members in pairs.values():
            if len(members) < 2:
                continue
            seen += len(members) * (len(members) - 1) // 2
            if seen > budget.max_candidates:
                return "skipped", None, None
            for (a, b), (c, d) in itertools.combinations(members, 2):
                if a == c or a == d or b == c or b == d:
                    continue
                if box.offer((a, b, c, d)) and box.stop:
                    return box.done(3)
        return box.done(3)

    if weight == 5:
        return _scan_five(circuit, box)

    if weight == 6:
        # Build the triple table only if the join it feeds can finish.  Two
        # triples pair up when their syndromes collide, so the number of
        # candidates is about T^2 / 2^r for T = C(n,3) syndromes over an r-bit
        # space -- 5.7e7 at [[255,k]] with r = 16, which the candidate budget
        # refuses.  Discovering that AFTER building the table costs half a
        # minute and a gigabyte per circuit for an answer of "skipped", and
        # eight circuits here are exactly that shape.
        triples = n * (n - 1) * (n - 2) // 6
        width = min(circuit.N - circuit.k, 64)
        if triples * triples / float(1 << width) / 2 > budget.max_candidates:
            return "skipped", None, None
        table = _triple_table(circuit)
        if table is None:
            return "skipped", None, None
        # a 6-set with zero syndrome splits into two triples with EQUAL
        # syndrome, so the two halves live in the same bucket
        seen = 0
        for members in table.values():
            if len(members) < 2:
                continue
            seen += len(members) * (len(members) - 1) // 2
            if seen > budget.max_candidates:
                return "skipped", None, None
            for left, right in itertools.combinations(members, 2):
                if set(left) & set(right):
                    continue
                if box.offer(left + right) and box.stop:
                    return box.done(10)
        return box.done(10)

    return "skipped", None, None


def _scan_five(circuit: Circuit, box: _Collector):
    """Weight 5 as 3 + 2: every triple, completed through the pair table.

    Vectorised over the pair table when numpy is present, because the plain
    Python form is ``C(n, 3)`` dict lookups -- 1.2e8 of them at ``n = 910``,
    and the exhaustive weight-5 sweep is what sixteen rows' ``d >= 6`` floors
    rest on, the widest of them at ``n = 959``.
    """
    n, budget = circuit.n, circuit.budget
    if n * (n - 1) * (n - 2) // 6 > budget.max_triples:
        return "skipped", None, None
    pairs, syn64 = circuit.pairs, circuit.syn64
    tables = circuit.np_pairs
    seen = 0

    if tables is None:                                   # pure Python fallback
        for i in range(n):
            si = syn64[i]
            for j in range(i + 1, n):
                sij = si ^ syn64[j]
                for l in range(j + 1, n):
                    for (a, b) in pairs.get(sij ^ syn64[l], ()):
                        if a in (i, j, l) or b in (i, j, l):
                            continue
                        seen += 1
                        if seen > budget.max_candidates:
                            return "skipped", None, None
                        if box.offer((i, j, l, a, b)) and box.stop:
                            return box.done(10)
        return box.done(10)

    pi, pj, psyn, offset = tables
    keys = np.array(sorted(pairs), dtype=np.uint64)
    for t in range(n - 2):
        start = int(offset[t + 1])
        if start >= psyn.size:
            break
        targets = psyn[start:] ^ np.uint64(syn64[t])
        where = np.searchsorted(keys, targets)
        np.clip(where, 0, keys.size - 1, out=where)
        for local in np.nonzero(keys[where] == targets)[0]:
            position = start + int(local)
            i, j = int(pi[position]), int(pj[position])
            for (a, b) in pairs[int(targets[local])]:
                if a in (t, i, j) or b in (t, i, j):
                    continue
                seen += 1
                if seen > budget.max_candidates:
                    return "skipped", None, None
                if box.offer((t, i, j, a, b)) and box.stop:
                    return box.done(10)
    return box.done(10)


def _triple_table(circuit: Circuit):
    """``{folded syndrome XOR: [(i, j, l), ...]}`` over all triples, or ``None``."""
    n = circuit.n
    total = n * (n - 1) * (n - 2) // 6
    if total > circuit.budget.max_triple_table:
        return None
    syn64 = circuit.syn64
    table: dict[int, list[tuple[int, int, int]]] = {}
    for i in range(n):
        si = syn64[i]
        for j in range(i + 1, n):
            sij = si ^ syn64[j]
            for l in range(j + 1, n):
                table.setdefault(sij ^ syn64[l], []).append((i, j, l))
    return table


def sample_witness(circuit: Circuit, weight: int):
    """Look for a harmful fault of exactly ``weight`` by sampling, not by proof.

    This exists to turn a floor into a pinned distance: a clean sweep below ``w``
    plus an explicit harmful fault AT ``w`` is an exact distance, and the witness
    is re-checkable by anyone in three lines.  Sampling ``(w-2)``-subsets and
    completing them through the pair table beats blind subset sampling by the
    size of the syndrome space, which is the whole reason it terminates at
    ``n ~ 1000``.  Returns the witness, or ``None`` -- which proves nothing.
    """
    n = circuit.n
    if weight > n:
        return None
    pairs = circuit.pairs
    if pairs is None or weight < 3:
        return None
    syn64 = circuit.syn64
    rng = random.Random(_RNG_SEED + weight * 7919 + n)
    head_size = weight - 2
    population = list(range(n))
    for _ in range(circuit.budget.witness_samples):
        head = rng.sample(population, head_size)
        target = 0
        for index in head:
            target ^= syn64[index]
        hits = pairs.get(target)
        if not hits:
            continue
        for (a, b) in hits:
            if a in head or b in head:
                continue
            candidate = tuple(sorted(head + [a, b]))
            if circuit.harmful(candidate):
                return candidate
    return None


def distance_report(columns, k, N, budget: Budget | None = None,
                    ceiling: int = 8) -> dict:
    """Pin the distance if the budget allows, and always say which it is.

    Two moves, in this order at every weight ``w`` that everything below has
    already been proved clean at:

    1.  **Witness first, from weight 5 up.**  Sampling ``(w-2)``-subsets and
        completing them through the pair table finds an explicit harmful fault
        in seconds where the exhaustive sweep is ``C(n, w-2)`` lookups.  A clean
        sweep below ``w`` plus a witness AT ``w`` is an EXACT distance, so this
        alone settles most of the corpus -- including every ``n = 1023`` circuit,
        where the weight-5 sweep is 1.8e8 lookups and the witness takes a
        millisecond.
    2.  **Otherwise sweep**, if the budget reaches.  A clean sweep raises the
        floor and the loop moves up a weight.

    No stored claim steers the sweep.  It runs weight by weight to ``ceiling``
    regardless of what any source said, which is why an understated claim gets
    corrected upward -- three ``n = 255`` rows of this catalogue arrived saying
    ``d = 5`` and the sweep pinned the exact distance at 7 -- and an inflated
    one is caught by the witness landing below it.  (An earlier version took a
    ``claimed`` parameter that read as if it decided how far to go; it never
    did, and a parameter that reads as steering and steers nothing is worse
    than none, so it is gone.  Stored claims are compared against measured
    distances by `verify_catalog.confirm_distance`, not consulted here.)

    Keys: ``d_exact`` (int or None), ``d_at_least`` (proven floor), ``d_upper``
    (weight of an explicit witness, or None), ``witness``, ``scanned``
    (per-weight status), ``A_d`` / ``A_d_at_weight`` where counted.
    """
    budget = budget or Budget()
    circuit = Circuit(columns, k, N, budget)
    n = circuit.n
    top = min(n, ceiling)
    want_count = n <= budget.count_upto_n

    scanned: dict[int, str] = {}
    floor, hit = 1, None
    weight = 1
    while weight <= top:
        # everything below `weight` is proven clean here, so `floor == weight`
        if weight >= 5:
            probe = sample_witness(circuit, weight)
            if probe is not None:
                scanned[weight] = "witnessed"
                return _pinned(scanned, weight, probe, circuit, want_count)
        status, witness, count = scan_weight(circuit, weight, want_count=want_count)
        scanned[weight] = status
        if status == "found":
            hit = (weight, witness, count)
            break
        if status == "skipped":
            break
        floor = weight + 1
        weight += 1

    report = {
        "d_at_least": floor,
        "d_exact": None,
        "d_upper": None,
        "witness": None,
        "A_d": None,
        "A_d_at_weight": None,
        "scanned": {str(w): s for w, s in scanned.items()},
    }
    if hit:
        weight, witness, count = hit
        report.update(d_exact=weight, d_at_least=weight, d_upper=weight,
                      witness=list(witness))
        if count is not None:
            report.update(A_d=count, A_d_at_weight=weight)
        return report
    # The sweep ran out of budget below the ceiling.  All that is left is an
    # upper bound: an explicit fault above the floor bounds the distance without
    # pinning it, and finding none proves nothing whatsoever.
    for weight in range(floor, min(n, floor + 3) + 1):
        witness = sample_witness(circuit, weight)
        if witness is not None:
            report.update(d_upper=weight, witness=list(witness))
            if weight == floor:
                report["d_exact"] = weight
            break
    return report


def _pinned(scanned, weight, witness, circuit, want_count):
    """A clean sweep below ``weight`` met a witness at it: an exact distance."""
    report = {
        "d_at_least": weight,
        "d_exact": weight,
        "d_upper": weight,
        "witness": list(witness),
        "A_d": None,
        "A_d_at_weight": None,
        "scanned": {str(w): s for w, s in scanned.items()},
    }
    if want_count:
        status, _witness, count = scan_weight(circuit, weight, want_count=True)
        if status == "clean":
            # A witness at this weight was just produced and re-checked against
            # the true syndromes, so a sweep that reports nothing here has a bug
            # in it.  Failing loudly is the only safe response: the alternative
            # is a catalogue row whose distance and whose A_d disagree about
            # whether anything is there at all.
            raise AssertionError(
                f"scan_weight found nothing at weight {weight} but "
                f"{witness} is a harmful fault of exactly that weight")
        if status == "found" and count is not None:
            report.update(A_d=count, A_d_at_weight=weight)
            report["scanned"][str(weight)] = "found"
    return report
