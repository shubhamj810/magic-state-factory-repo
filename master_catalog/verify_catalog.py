#!/usr/bin/env python3
"""RE-VERIFICATION of every row of the shipped ``master_catalog.json``.

The single entry point for the question the catalogue exists to answer: *is
every row of this file true?*  Nothing is read from a row except ``columns``,
``k`` and ``N``; every other published field is RE-DERIVED from those and then
compared with what the row stores.  A disagreement is a failure, printed with
the reason, and the exit status is non-zero.

    python verify_catalog.py                 # the whole shipped catalogue
    python verify_catalog.py --rows 1-20     # a slice, by 1-based row number
    python verify_catalog.py --quiet         # only failures and the summary

WHY ``k`` IS AN INPUT AND EVERYTHING ELSE IS NOT
------------------------------------------------
The output/check split is a DECLARATION, not a derivable fact: the same columns
with a different ``k`` are a different factory (or none).  So ``k`` is read from
the row, and then everything the row says about itself has to follow from it.
``N`` is read too, but immediately re-derived and required to match the largest
qubit index the columns use, in both directions -- a row that cannot state its
own register size is not a row to publish.

WHAT IS RE-DERIVED, PER ROW
---------------------------
1.  **Validity.**  ``n == len(columns)``; the columns are non-empty and
    DISTINCT (two equal columns cancel to a diagonal Clifford: they contribute
    nothing to any parity, so the pair is dead weight in ``n`` -- the injection
    count this whole table is read for -- and the circuit is not the reduced one
    it claims to be); ``N`` as above; ``k <= N``; ``level == 3``.
2.  **The factory condition.**  Every degree-<=3 parity that touches a check
    wire is even.  If one is odd the circuit deposits phase on a postselected
    wire and the accepted action is not the gate the outputs claim -- it is not
    a factory at all.
3.  **The gate.**  The monomial set the columns deposit on the outputs, read off
    the rows, compared LITERALLY against the row's ``gate`` and ``gate_human``
    strings and against its ``sk_key`` / ``sk_fingerprint``.  An empty gate is
    Clifford, level <= 2, and out of scope.
4.  **The distance.**  Absence below ``d`` is PROVED: every weight ``1..d-1`` is
    swept to completion, and a sweep the budget cut short is a failure, not a
    pass -- a floor nobody proved is not a floor.  Presence at ``d`` is
    WITNESSED: when ``d_is_exact`` the stored ``d_witness`` must be a harmful
    fault of exactly that weight, re-checked against the true syndromes.  A
    floor stores ``d_is_exact: false`` and is printed as ``>=d``; if it carries
    a witness at all, that witness must lie strictly ABOVE the floor and equal
    ``d_upper``, because a fault at the floor would have made it exact.
5.  **No spectator output.**  The gate touches all ``k`` outputs; an output it
    never touches is padding, and ``k`` is the denominator of every rate anyone
    quotes off this table.
6.  **No pseudo-output.**  The ``k`` output rows are linearly independent MODULO
    THE CHECK SPAN.  ``theory/02_classification.md`` places a ``k``-output
    factory in the quotient ``V = R(C)/C`` as an independent ``k``-subset:
    everything the gate reads off an output row is invariant under ``a -> a + c``
    for ``c`` in the check span, so an output equal to another one up to check
    rows is one logical qubit wearing two labels.  This is NOT implied by 5.
7.  **No redundant check.**  The ``r`` check rows are linearly independent of
    each other -- the check-side twin of 6.  A check row inside the span of
    the others contributes a syndrome bit that is an XOR of theirs for every
    fault, so it rejects nothing they accept and can be deleted with ``n``,
    ``k``, the gate and the distance all intact.  A row carrying one overstates
    ``N``, which is the ambient-qubit cost this table is read for and the
    tie-break the merge minimises on.  Structurally idle wires are already
    refused by 1 (every wire ``0..N-1`` must be touched by some column, checks
    included); this is the linear-algebra case that survives that test.
8.  **The metrics**, where they are computable: the exact minimal T-count and
    the CNOT-frame-reduced phase-polynomial degree of the re-derived gate.
    Above ``k = 6`` both are minimisations over groups that stop being finite in
    practice, and the row carries ``null`` with a note saying so; the note is
    then required to be there.

AND, ONCE, OVER THE WHOLE FILE
------------------------------
9.  **No duplicate classes.**  A class is ``(n, k, d, GL(k,2) gate)``: the
    distance, and the gate up to an invertible change of the output basis and
    diagonal Cliffords.  Two rows with equal ``d`` and equal PROVED ``S_k`` keys
    are one class outright (a permutation is a frame change), and then every
    same-``(n, k, d)`` PAIR is decided by
    `glcanon.gl_isomorphic`, which is what certifies the claim in both
    directions.  Where that search runs out of budget the pair must carry a
    ``dedup_note``: the file may hold a class whose distinctness is unproved,
    at the widths where proving it is out of reach, but it may not do so
    silently -- and a note on a row whose every pair WAS decided is refused.
10. **The provenance labels resolve.**  Every name in a row's ``regimes`` is
    one the file's own header defines, the names are listed strongest-first in
    the header's order, and ``strongest_claim`` is the header's sentence for
    the first of them.  This is the one published field a row cannot check
    alone -- it is a statement about the row AND the header -- which is why it
    lives here rather than in `verify_row`.
11. **The header is there and counts its rows.**  Every key
    `catalogfile.HEADER_KEYS` names is present and typed, the two definition
    maps really map names to sentences, and ``n_classes`` equals the number of
    rows -- the one header value that is DERIVABLE, and so the one that can go
    stale without anything else noticing.
12. **The citations resolve.**  Every row cites at least one work, no key twice,
    and every key is an entry of the header's ``references`` map.  Which works
    a class is credited to is a curation decision and nothing here re-derives
    it; what is checked is that a reader following a citation finds one.

THREE IMPLEMENTATIONS, ON PURPOSE
---------------------------------
`faultcore.py` answers 2-7 with bit-level and meet-in-the-middle algorithms that
reach ``n = 1023`` and ``k = 162``.  On every circuit small enough for them, the
literal ``C(k,3)`` / ``C(n,4)`` enumerations at the bottom of this file are run
as well and must agree; so is `factorylib/verification.py`, which shares no code
with anything in this folder.  Agreement of three implementations is the point.

Exit status is 0 only if every row passes and the file-level checks pass.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
import tempfile
import time
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))          # run from anywhere: siblings by bare name
sys.path.insert(0, str(REPO))          # shared factorylib package

import catalogfile as CF                                          # noqa: E402
import faultcore as FC                                            # noqa: E402
import glcanon as GC                                              # noqa: E402
import skcanon as SK                                              # noqa: E402
from factorylib.verification import verify as reference_verify    # noqa: E402

# `factorylib.metrics` memoises the reduced-degree search to a file next to
# itself.  This folder must not write outside `master_catalog/`, so the cache is
# redirected here first, with the upstream entries preloaded so the gates
# already solved stay free.  The caps below are what a RECOMPUTATION here runs:
# exact enumeration of GL(k,2) through k = 4, and a seeded 100,000-frame bounded
# search above it, which `factorylib` labels as the upper bound it is.  They are
# not what every shipped row was computed under -- five k = 6 rows carry a note
# saying their bound came from 2,000,000 frames -- and those rows verify because
# the cache above is preloaded with the value, not because this cap reproduces
# it.  A row whose bound is NOT cached is recomputed under these caps, so
# changing them would change the numbers being compared.
import factorylib.metrics as _metrics                             # noqa: E402
METRIC_CACHE = HERE / "reduced_degree_cache.json"
if METRIC_CACHE.exists():
    _metrics._DEG_CACHE.update(
        json.loads(METRIC_CACHE.read_text(encoding="utf-8")))
# `factorylib.metrics` persists every value it computes to ``_CACHE_PATH``.
# Verifying must not write anything: a re-verification that dirties the git
# tree is not a re-verification, and the entry it would write is computed under
# THIS file's smaller frame budget, so caching it makes the affected row fail
# every subsequent run.  The path is therefore sent to a scratch file that
# nothing reads; `persist_metric_cache` is the one deliberate way to grow the
# real one, and only `merge_results` calls it, only when it actually writes.
_metrics._CACHE_PATH = Path(tempfile.gettempdir()) / "mc_reduced_degree.json"
_metrics._DEG_CAP = 21_000
_metrics._DEG_SAMPLES = 100_000
from factorylib.metrics import metrics_from_monomials             # noqa: E402


def persist_metric_cache(path=METRIC_CACHE):
    """Write back the reduced-degree values computed this session.

    Called by `merge_results` after a real write, so a merge that had to
    compute a new bound leaves it for next time.  Verification never calls it.
    """
    Path(path).write_text(json.dumps(_metrics._DEG_CACHE, indent=1),
                          encoding="utf-8")

#: Both metrics are minimisations -- over ``GL(k,2)`` for the degree and over a
#: punctured Reed-Muller coset for the T-count -- and neither is feasible past
#: ``k = 6`` (theory/01_factories_and_distance.md).  Above it the fields are null
#: with a note, never guessed.  Below it the T-count is exact throughout, but
#: the DEGREE is exact only through ``k = 4``: ``|GL(5,2)| = 1e7`` and
#: ``|GL(6,2)| = 2e10`` are past exact enumeration, so those rows publish a
#: sampled upper bound and say so in ``poly_degree_note``.  "Computable" here
#: means the field has a value the row stands behind, not that the value is a
#: proved minimum.
METRICS_K_CAP = 6
#: `factorylib.verification` sweeps all ``2^k - 1`` output targets, so it is a
#: usable second opinion only while that is a number.
REFERENCE_K_CAP = 12
REFERENCE_N_CAP = 300
#: The literal enumerations below are ``C(k,3)`` monomials and ``C(n,4)``
#: subsets; past these they stop being a cross-check and become the run.
LITERAL_N_CAP = 70
LITERAL_K_CAP = 8


# ------------------------------------------------- literal reference routines
# Deliberately naive: these are the definitions, transcribed, and they exist to
# disagree with `faultcore` if `faultcore` is ever wrong.  They are unusable
# above a few dozen columns, which is exactly why `faultcore` exists.
def derived_gate(columns, k):
    """The deposited monomial set, by literal enumeration over output subsets.

    Degrees 1, 2 and 3 exhaust it: a column with support ``S`` contributes
    ``+/- 2^(t-1)`` to the ``Z_8`` coefficient of a degree-``t`` monomial, which
    vanishes mod 8 for ``t >= 4``, so a level-3 circuit's whole non-Clifford
    content is these three parities.
    """
    supports = [set(column) for column in columns]
    gate = set()
    for size in (1, 2, 3):
        for subset in itertools.combinations(range(k), size):
            want = set(subset)
            if sum(1 for support in supports if want <= support) % 2:
                gate.add(frozenset(subset))
    return frozenset(gate)


def exact_distance(columns, k, cap=4):
    """Smallest undetectable damaging fault by ascending weight; ``cap+1`` = ">cap".

    The masks are built with OR, not ``sum``: the two agree only while no
    column repeats a wire, and this is the LITERAL reference implementation --
    the one place a wrong answer would be trusted over a clever one.
    """
    masks = []
    for column in columns:
        mask = 0
        for q in column:
            mask |= 1 << q
        masks.append(mask)
    outm = (1 << k) - 1
    for weight in range(1, cap + 1):
        for support in itertools.combinations(range(len(masks)), weight):
            value = 0
            for index in support:
                value ^= masks[index]
            if value and not value & ~outm:
                return weight
    return cap + 1


def effective_width(columns, k, N):
    """Rank of the output rows modulo the check span -- the genuine width."""
    rows = [sum(1 << j for j, c in enumerate(columns) if q in set(c))
            for q in range(N)]
    basis: dict[int, int] = {}

    def insert(value):
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


# ------------------------------------------------------------- the shape check
def _integer(value):
    """A genuine non-negative int -- `True` is not 1 here, and 3.5 is not 3."""
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def structural_problems(k, N, columns):
    """Whether ``(k, N, columns)`` can even be INDEXED as a circuit ([] if so).

    This runs before anything else because ``N`` and ``k`` index every loop
    below and they come out of a file.  A validator that hangs on ``N: 2**63``
    or raises on a string where an int belongs has not rejected its input -- it
    has crashed on it, which is a different thing and a worse one.
    """
    problems = []
    for name, value in (("k", k), ("N", N)):
        if not _integer(value) or value < 1:
            problems.append(("schema", f"{name}={value!r} is not a positive "
                                       f"integer"))
    if not isinstance(columns, (list, tuple)) or not columns:
        problems.append(("schema", f"columns is a "
                                   f"{type(columns).__name__}, not a non-empty "
                                   f"list"))
        return problems
    for index, column in enumerate(columns):
        if not isinstance(column, (list, tuple)) or not column \
                or not all(_integer(q) for q in column):
            problems.append(("schema", f"column {index} is not a non-empty list "
                                       f"of qubit indices: {column!r}"))
            return problems
    if problems:
        return problems
    normalised = [tuple(sorted(set(c))) for c in columns]
    repeats = len(normalised) - len(set(normalised))
    if repeats:
        problems.append(("repeated-column",
                         f"{repeats} repeated column(s): equal columns cancel "
                         f"to a diagonal Clifford, contributing to no parity "
                         f"and to no monomial, so they are dead weight in the "
                         f"injection count n and this is not the reduced "
                         f"circuit it claims to be"))
    touched = set().union(*(set(c) for c in normalised))
    used = max(touched) + 1
    if used != N:
        # Strict in both directions.  ``used > N`` is a circuit that runs off
        # the end of its own register; ``used < N`` is a record declaring a
        # check wire no rotation touches, which is physically harmless but makes
        # ``N`` -- a published parameter -- something the row cannot state.
        problems.append(("shape", f"N={N} but the columns use {used} wires"))
    elif len(touched) != N:
        # The same misstatement, hidden in the middle rather than at the end:
        # the highest index is right but some wire below it is never rotated.
        # ``N`` is the headline ambient-qubit cost and the tie-break the merge
        # tool minimises on, so an inflated one is not a harmless untidiness.
        # ``sorted(set(range(N)) - touched)`` is the obvious way to name the
        # idle wires and is the one thing this function must not do.  ``N``
        # comes out of a file, and the branch above only sends control here when
        # the TOP wire is present, so ``N = 2**63`` with a column touching
        # ``2**63 - 1`` lands on this line and the range is not a slow rejection
        # but an out-of-memory kill -- precisely the failure this docstring
        # promises not to have, arrived at by the one path the absurd-register
        # test does not take.  Walking the supports finds the same gaps in
        # ``len(touched)`` steps, whatever ``N`` claims.
        # ``missing`` is exact and costs nothing; ``idle`` is only the first
        # few to name.  Deciding the elision marker on ``len(idle) == 6`` said
        # "..." when there were exactly six and nothing had been elided.
        missing = N - len(touched)
        idle, previous = [], -1
        for wire in sorted(touched):
            while previous + 1 < wire and len(idle) < 6:
                previous += 1
                idle.append(previous)
            previous = max(previous, wire)
        problems.append(("shape", f"N={N} but no column touches wire(s) "
                                  f"{idle}{' ...' if missing > len(idle) else ''}"
                                  f", so the register is larger than the "
                                  f"circuit needs"))
    if k > N:
        problems.append(("shape", f"k={k} outputs do not fit in N={N} qubits"))
    return problems


# ------------------------------------------------------------ the derivation
def derive(columns, k, N):
    """Everything a row publishes, re-derived from ``(columns, k, N)`` alone.

    Returns ``(facts, problems)``.  ``problems`` is a list of
    ``(kind, detail)`` pairs and means the circuit is not a publishable
    level-3 distance->=3 factory; ``facts`` carries the derived values, and is
    incomplete when the shape checks failed (nothing after them is meaningful).

    The distance is NOT derived here -- see `confirm_distance` (which re-proves
    a stored one) and `measure_distance` (which finds one for a new circuit).
    They are different jobs and conflating them is how a floor becomes an exact
    value.
    """
    problems = structural_problems(k, N, columns)
    if any(kind == "schema" or kind == "shape" for kind, _d in problems):
        return {}, problems
    normalised = [tuple(sorted(set(c))) for c in columns]
    rows = FC.rows_over_columns(normalised, N)

    contamination = FC.check_contamination(rows, k, N)
    if contamination:
        problems.append(("check-contamination",
                         f"odd degree-<=3 parity touching a check wire at "
                         f"{[list(m) for m in contamination[:3]]}: the circuit "
                         f"deposits phase on a postselected wire, so it is not "
                         f"a factory"))

    gate = FC.recover_gate(rows, k)
    if len(normalised) <= LITERAL_N_CAP and k <= LITERAL_K_CAP \
            and gate != derived_gate(normalised, k):
        problems.append(("implementation-disagreement",
                         "the bit-level and literal gate read-offs disagree"))
    if not gate:
        problems.append(("not-level-3",
                         "the columns deposit no non-Clifford gate on the "
                         "outputs (level <= 2, not a level-3 factory)"))

    idle = FC.spectators(gate, k)
    if idle:
        problems.append(("spectator-output",
                         f"spectator output(s) {idle[:6]}: the recovered gate "
                         f"never touches them, so k={k} is padded"))
    widths = FC.output_report(rows, k, N)
    if not widths["independent"]:
        problems.append(("pseudo-output", _pseudo_output_reason(widths, k)))
    dead_checks = FC.redundant_checks(rows, k, N)
    if dead_checks:
        problems.append(("redundant-check",
                         f"check wire(s) {dead_checks[:6]}"
                         f"{' ...' if len(dead_checks) > 6 else ''}: each one's "
                         f"syndrome bit is an XOR of the other checks' for "
                         f"every fault, so it can never reject anything they "
                         f"accept and N={N} is one larger per such wire than "
                         f"this circuit needs"))
    if len(normalised) <= LITERAL_N_CAP \
            and widths["effective_width"] != effective_width(normalised, k, N):
        problems.append(("implementation-disagreement",
                         "the bit-level and literal width computations "
                         "disagree"))

    encoding, perm = SK.sk_canonical_with_perm(k, gate)
    t_count, t_note, degree, degree_note = recompute_metrics(gate, k)
    facts = {
        "n": len(normalised), "k": k, "N": N, "level": 3,
        "monomials": gate,
        "gate": SK.gate_string(gate, k),
        "gate_human": SK.gate_human(gate, k),
        "sk_key": [list(Q) for Q in encoding] if encoding is not None else None,
        # The relabelling that CARRIES the columns into that canonical frame,
        # output ``i -> sk_perm[i]``.  Nothing about a shipped row depends on
        # it -- the row is already in its frame -- but `merge_results.py` needs
        # it to put an incoming circuit there, and re-deriving it separately
        # would be a second S_k minimisation of the same gate.
        "sk_perm": perm,
        "sk_fingerprint": SK.sk_fingerprint(k, gate),
        "effective_width": widths["effective_width"],
        "t_count": t_count, "t_count_note": t_note,
        "poly_degree": degree, "poly_degree_note": degree_note,
        "columns": [list(c) for c in normalised],
    }
    return facts, problems


def _pseudo_output_reason(widths, k):
    """Which of the four ways independence-modulo-checks failed, by name."""
    detail = []
    if widths["duplicate_rows"]:
        detail.append(f"identical output rows {widths['duplicate_rows'][:3]}")
    if widths["equal_mod_checks"]:
        detail.append(f"output rows equal modulo the check span "
                      f"{widths['equal_mod_checks'][:3]}")
    if widths["in_check_span"]:
        detail.append(f"output row(s) inside the check span "
                      f"{widths['in_check_span'][:3]}")
    if widths["other_dependence"]:
        detail.append(f"output(s) {widths['other_dependence'][:3]} dependent on "
                      f"the others modulo the check span")
    # No "pseudo-output:" prefix here: the caller prints the KIND alongside the
    # detail, and a message that repeats its own label reads like a bug.
    return (f"only {widths['effective_width']} of {k} outputs are independent "
            f"modulo the check span (" + "; ".join(detail) + ")")


_METRICS_CACHE: dict = {}


def recompute_metrics(gate, k):
    """``(t_count, t_note, poly_degree, degree_note)`` for a monomial set.

    Both numbers minimise over a group that is astronomical past ``k = 6``, so
    above that they are not attempted: a missing number here is MISSING, never
    estimated.  `theory/01_factories_and_distance.md` is explicit that the whole
    point of these two fields is that they are exact.
    """
    if k > METRICS_K_CAP:
        note = (f"not computed: exact minimisation is over GL({k},2) and a "
                f"punctured RM({k}-4,{k}) coset, neither feasible at k={k}")
        return None, note, None, note
    if not gate:
        # The identity deposits nothing, so both metrics are 0.  This is a real
        # case and not a defensive branch: a circuit whose columns cancel on the
        # outputs IS rejected -- as `not-level-3` -- but the rejection has to be
        # reported, and it cannot be if the metric call raises on the way there.
        # `skcanon.gate_string` renders the empty gate as `check-only`, which is
        # a label for a reader and not a monomial list for a parser.
        return 0, None, 0, None
    key = (k, SK.gate_string(gate, k))
    if key not in _METRICS_CACHE:
        _METRICS_CACHE[key] = metrics_from_monomials(key[1])
    return _METRICS_CACHE[key]


# ------------------------------------------------------------------- distance
def confirm_distance(columns, k, N, d, d_is_exact, d_witness, d_upper,
                     budget=None):
    """Re-prove a STORED distance from the columns; return a list of problems.

    Absence is proved and presence is witnessed, and the two halves are kept
    apart on purpose:

    * every weight ``1..d-1`` is swept to completion.  ``found`` means the
      stored ``d`` is inflated and the sweep names the fault that disproves it.
      ``skipped`` means the budget stopped the sweep, which proves NOTHING --
      and an unproved floor published as a floor is exactly the failure this
      catalogue is supposed to make impossible, so it is a failure here too.
    * ``d_is_exact`` additionally requires ``d_witness`` to be a harmful fault
      of weight exactly ``d``, re-checked against the true syndromes rather than
      the folded ones the sweeps use.  Clean below plus a witness at ``d`` is
      what "exact" means; nothing weaker is allowed to print an unadorned ``d``.
    * a floor may still carry a witness ABOVE itself -- ``d = 6, d_upper = 7``
      says the distance is one of two values and names the fault ruling out an
      eighth -- but a witness AT the floor would have made it exact, so one
      there is a contradiction rather than a bonus.

    The asymmetry is deliberate and is not a gap.  A row that publishes a floor
    where an exact value was in fact available UNDERSTATES itself, and that
    passes here, because what the row claims is true.  The failure this
    catalogue exists to make impossible is the other one -- a floor printed as a
    measurement -- and that is what the checks above are pointed at.
    """
    problems = []
    if not _integer(d) or d < 3:
        return [("distance-below-3",
                 f"d={d!r} is not an integer >= 3; this catalogue is d >= 3")]
    circuit = FC.Circuit(columns, k, N, budget or FC.Budget())
    if d > circuit.n:
        problems.append(("distance", f"d={d} exceeds the {circuit.n} columns"))

    def harmful_of_weight(indices, want, label):
        if not isinstance(indices, (list, tuple)) \
                or not all(_integer(q) and q < circuit.n for q in indices):
            return [("distance-witness",
                     f"{label} {indices!r} is not a list of column indices")]
        if len(set(indices)) != want:
            return [("distance-witness",
                     f"{label} has weight {len(set(indices))}, not {want}")]
        if not circuit.harmful(indices):
            return [("distance-witness",
                     f"{label} {sorted(set(indices))} is not an undetectable "
                     f"damaging fault: it does not have zero syndrome and a "
                     f"non-zero output part")]
        return []

    for weight in range(1, min(d, circuit.n + 1)):
        status, witness, _count = FC.scan_weight(circuit, weight)
        if status == "found":
            problems.append(("distance-inflated",
                             f"a harmful fault of weight {weight} exists "
                             f"(columns {list(witness)}), so the distance is at "
                             f"most {weight}, not {d}"))
            break
        if status == "skipped":
            problems.append(("distance-unproved",
                             f"the weight-{weight} sweep did not run to "
                             f"completion under the fault budget, so d >= {d} "
                             f"is not proved here"))
            break

    if d_is_exact:
        problems += harmful_of_weight(d_witness, d, "d_witness")
        if d_upper != d:
            problems.append(("distance",
                             f"d_is_exact but d_upper={d_upper!r} != d={d}"))
    else:
        if d_upper is None:
            if d_witness is not None:
                problems.append(("distance",
                                 f"a floor with no d_upper stores a witness "
                                 f"{d_witness!r} anyway"))
        elif not _integer(d_upper) or d_upper <= d:
            problems.append(("distance",
                             f"a floor d >= {d} must carry d_upper strictly "
                             f"above it, not {d_upper!r}: a fault at the floor "
                             f"would have made the distance exact"))
        else:
            problems += harmful_of_weight(d_witness, d_upper, "d_witness")
    return problems


def measure_distance(columns, k, N, budget=None):
    """Find the distance of a NEW circuit: `faultcore.distance_report` verbatim.

    Used by `merge_results.py`, where nothing is stored yet and there is nothing
    to re-prove.  A row it produces is then handed straight to `verify_row`, so
    what merge accepts is what this file would accept afterwards -- by
    construction, not by promise.  The record's own distance claim is not passed
    down: the sweep is claim-independent, and the claim is compared against the
    MEASURED result by the caller.
    """
    return FC.distance_report(columns, k, N, budget=budget or FC.Budget())


# ------------------------------------------------------------------- one row
def verify_row(row, budget=None, reference=True):
    """Re-derive a shipped row from its columns; return ``(facts, problems)``.

    ``problems`` is a list of ``(kind, detail)`` and is empty exactly when the
    row is true.  Every published field is compared, not just the interesting
    ones: a stale ``gate_human`` is a lie to a reader even though no computation
    depends on it.
    """
    problems: list[tuple[str, str]] = []
    if not isinstance(row, dict):
        return {}, [("schema", f"the row is a {type(row).__name__}, "
                               f"not an object")]
    missing = [name for name in CF.REQUIRED_FIELDS if name not in row]
    if missing:
        problems.append(("schema", f"row is missing {', '.join(missing)}"))
    unknown = [name for name in row
               if name not in CF.REQUIRED_FIELDS + CF.OPTIONAL_FIELDS]
    if unknown:
        problems.append(("schema", f"row carries undocumented field(s) "
                                   f"{', '.join(sorted(unknown))}"))
    if missing:
        return {}, problems

    # Types BEFORE values.  Every comparison below is `==` or a truth test, and
    # both of those cross type boundaries that JSON does not: `True == 1` makes
    # a boolean pass for a T-count of 1, and `if row["d_is_exact"]` is true for
    # any non-empty string.  A row that is the wrong SHAPE has not been checked
    # by being compared, so it is refused before anything reads it.
    typed = CF.type_problems(row)
    problems += typed
    if typed:
        return {}, problems
    problems += certificate_problems(row)

    facts, derived_problems = derive(row["columns"], row["k"], row["N"])
    problems += derived_problems
    if not facts:
        return facts, problems

    if row["n"] != facts["n"]:
        problems.append(("shape", f"n={row['n']} but there are "
                                  f"{facts['n']} columns"))
    if row["level"] != 3:
        problems.append(("schema", f"level={row['level']!r}; this catalogue is "
                                   f"level 3 throughout"))
    if [list(c) for c in row["columns"]] != facts["columns"]:
        problems.append(("columns",
                         "the stored columns are not sorted and duplicate-free "
                         "within each column; the derived fields belong to the "
                         "normalised circuit, so the two could differ"))
    for name in ("gate", "gate_human", "sk_fingerprint", "effective_width"):
        if row[name] != facts[name]:
            problems.append((f"{name}-mismatch",
                             f"row says {name}={row[name]!r}, the columns give "
                             f"{facts[name]!r}"))

    # The S_k frame.  `sk_canonical_frame` is a CLAIM that the columns are shown
    # in the lex-minimal output labelling, and it is checked as one: the derived
    # key must exist, equal what the row stores, and equal the gate's own
    # encoding -- that last equality is the frame claim itself.
    if row["sk_canonical_frame"]:
        if facts["sk_key"] is None:
            problems.append(("sk_key-mismatch",
                             "the row claims a canonical frame but the S_k "
                             "minimisation did not finish here"))
        elif row["sk_key"] != facts["sk_key"]:
            problems.append(("sk_key-mismatch",
                             f"row says sk_key={row['sk_key']!r}, the columns "
                             f"give {facts['sk_key']!r}"))
        elif [list(Q) for Q in SK.encode(facts["monomials"])] != facts["sk_key"]:
            problems.append(("sk_key-mismatch",
                             "the stored columns are not in the canonical "
                             "output frame they claim: their gate is not its "
                             "own S_k representative"))
        if "sk_key_note" in row:
            problems.append(("schema", "a canonical-frame row carries an "
                                       "sk_key_note explaining a frame it has"))
    else:
        if row["sk_key"] is not None:
            problems.append(("sk_key-mismatch",
                             "sk_canonical_frame is false but sk_key is not "
                             "null"))
        if "sk_key_note" not in row:
            problems.append(("schema",
                             "a row shown outside the canonical frame must "
                             "carry sk_key_note saying so"))

    problems.extend(_circuit_provenance_problems(row))

    for name in ("t_count", "poly_degree"):
        stored, got, note = row[name], facts[name], facts[f"{name}_note"]
        if stored is None and got is not None:
            problems.append((f"{name}-mismatch",
                             f"row stores no {name} but it recomputes to "
                             f"{got}"))
        elif stored is not None and got is not None and stored != got:
            problems.append((f"{name}-mismatch",
                             f"row says {name}={stored}, recomputed {got}"))
        elif stored is not None and got is None:
            # The fourth case, and the one that was missing.  Above
            # ``METRICS_K_CAP`` the recomputation returns nothing, so a stored
            # number met none of the branches above and sailed through: a
            # ``k = 7`` row could publish ``t_count: 999999`` and verify with no
            # problems at all.  That is the only place in this file where a
            # published field was not re-derived, and it is exactly the place
            # where nothing else could catch it -- the minimisations are
            # infeasible there, which is WHY the field is meant to be null.
            problems.append((f"{name}-mismatch",
                             f"row publishes {name}={stored} but this "
                             f"catalogue cannot recompute {name} at k="
                             f"{row['k']}, so the number rests on nothing"))
        elif stored is None and got is None and f"{name}_note" not in row:
            problems.append(("schema", f"{name} is null with no {name}_note "
                                       f"saying why"))
        if note is not None and row.get(f"{name}_note") != note:
            problems.append((f"{name}-mismatch",
                             f"the {name} note has drifted from the one the "
                             f"recomputation produces"))
        if note is None and f"{name}_note" in row:
            problems.append(("schema", f"row carries a {name}_note but the "
                                       f"recomputation has nothing to note"))

    problems += confirm_distance(facts["columns"], row["k"], row["N"], row["d"],
                                 row["d_is_exact"], row["d_witness"],
                                 row["d_upper"], budget)

    if reference and row["k"] <= REFERENCE_K_CAP \
            and facts["n"] <= REFERENCE_N_CAP \
            and not any(kind == "repeated-column" for kind, _d in problems):
        # The third opinion: `factorylib/verification.py` shares no code with
        # this folder.  It enumerates faults only through weight 4 and reports
        # ">= 5" beyond, so it can confirm a distance below 5 exactly and
        # otherwise only that the floor is not contradicted.
        #
        # It REFUSES a repeated-column circuit by raising, which is the right
        # behaviour for a verifier and the wrong shape for a caller collecting
        # reasons, so that case is caught above (it is already reported) and
        # anything else it raises becomes a reported problem rather than a
        # traceback: a row that makes the checker crash has not been cleared.
        try:
            parity_ok, reference_d = reference_verify(
                row["k"], row["N"], [frozenset(c) for c in facts["columns"]],
                set(facts["monomials"]), dmax=4)
        except (ValueError, KeyError, IndexError) as failure:
            problems.append(("reference-verifier",
                             f"factorylib.verification refuses this circuit: "
                             f"{failure}"))
        else:
            # It returns either an exact weight <= 4 or the string ">= 5", and
            # what contradicts the row depends on which of the two the ROW is
            # claiming.  An exact row must agree; a FLOOR only claims that
            # nothing lighter than `d` is harmful, so a reference distance
            # ABOVE the floor confirms it rather than contradicting it.  Getting
            # this wrong would flag every honestly understated row, which is
            # the one direction `confirm_distance` deliberately permits.
            exact_reference = None if isinstance(reference_d, str) \
                else reference_d
            if not parity_ok:
                problems.append(("reference-verifier",
                                 "factorylib.verification rejects the parity "
                                 "tensor of this circuit"))
            elif exact_reference is not None:
                contradicted = (exact_reference != row["d"] if row["d_is_exact"]
                                else exact_reference < row["d"])
            else:
                contradicted = row["d_is_exact"] and row["d"] < 5
            if parity_ok and contradicted:
                problems.append(("reference-verifier",
                                 f"factorylib.verification gives distance "
                                 f"{reference_d}, the row says "
                                 f"{'' if row['d_is_exact'] else '>='}"
                                 f"{row['d']}"))
    return facts, problems


# ------------------------------------------------------------ the whole file
def _typed_row(row):
    """Whether the file-level passes may read ``row`` at all.

    Object-shaped and correctly TYPED -- `CF.type_problems` -- which is the
    same bar `verify_row` applies before it compares anything, and for the
    same reason: the passes below index ``sk_key`` as nested lists and hash
    ``regimes`` entries, so a row that failed row-level typing (``sk_key:
    true``, ``regimes: [["x"]]``) re-read here under stronger assumptions
    turned its recorded rejection into a TypeError.  Skipping it loses
    nothing: it is already in the failure list on exactly those grounds.
    """
    return isinstance(row, dict) and not CF.type_problems(row)


def duplicate_class_problems(rows):
    """Pairs of rows that are the same ``(n, k, d, GL(k,2) gate)`` class.

    The distance is part of the class: two circuits for one gate at different
    distances are two rows, and neither is a duplicate of the other.

    Two passes.  First the ``S_k`` key, which REFINES the class: two rows whose
    PROVED keys agree deposit the same gate up to an output permutation, and a
    permutation is a frame change, so they are one class and saying so is
    sound.  That pass can only convict -- rows with different ``S_k`` keys may
    still be one ``GL(k,2)`` class, ``T0.T1`` and ``T0.CS01`` being the
    smallest example -- and the fingerprint is a hash, so fingerprint rows take
    no part in it.  Then every same-``(n, k, d)`` pair is decided by
    `glcanon.gl_isomorphic`, a decision procedure and not a hash, which is what
    actually certifies the claim.
    """
    problems = []
    # Only rows whose circuit can be READ take part.  A row that is not an
    # object, or whose (k, N, columns) fail the structural checks, has already
    # failed `verify_row` for exactly that reason; deriving a gate from it here
    # would crash the file-level pass after the row-level pass finished
    # diagnosing it, and a crash reports one problem where the run had found
    # many.  Skipping it loses nothing: a row with no readable circuit has no
    # class to collide with.
    readable = [(index, row) for index, row in enumerate(rows, 1)
                if _typed_row(row)
                and not structural_problems(row.get("k"), row.get("N"),
                                            row.get("columns"))]
    seen: dict[tuple, int] = {}
    for index, row in readable:
        if row.get("sk_key") is None:
            continue
        key = (row.get("n"), row.get("k"), row.get("d"),
               tuple(map(tuple, row["sk_key"])))
        if key in seen:
            problems.append(("duplicate-class",
                             f"rows {seen[key]} and {index} share the S_k key "
                             f"(n={row.get('n')}, k={row.get('k')}, "
                             f"d={row.get('d')}, {row.get('gate')})"))
        seen[key] = index
    by_shape = defaultdict(list)
    for index, row in readable:
        by_shape[(row.get("n"), row["k"], row.get("d"))].append((index, row))
    undecided_rows = set()
    for (n, k, d), group in sorted(by_shape.items()):
        if len(group) < 2:
            continue
        # re-derived once per row, not once per pair: at k = 162 the gate has
        # hundreds of monomials and the read-off is not free
        gates = {index: row_monomials(row) for index, row in group}
        for (i, left), (j, right) in itertools.combinations(group, 2):
            if gates[i] is None or gates[j] is None:
                continue
            verdict = GC.gl_isomorphic(k, gates[i], gates[j])
            if verdict is None:
                # The search gave up.  It has NOT shown the two to be
                # different, so the file cannot claim they are distinct on the
                # strength of it.  What it CAN do is say so: refusing the row
                # would throw away a verified factory over bookkeeping, at the
                # widths where results are least easily found again.  So a
                # pair one of whose rows carries a ``dedup_note`` is admitted
                # as documented uncertainty, exactly as an unproved canonical
                # frame is admitted with ``sk_key_note``.  An UNdocumented one
                # is still a failure: the prohibition is on silence, not on
                # not knowing.
                undecided_rows.update((i, j))
                if not (left.get("dedup_note") or right.get("dedup_note")):
                    problems.append(("undecided-class",
                                     f"rows {i} and {j} are both [[{n},{k},{d}]], "
                                     f"the GL(k,2) isomorphism search ran out "
                                     f"of budget, and neither row carries a "
                                     f"dedup_note saying their distinctness is "
                                     f"unproved"))
            elif verdict:
                problems.append(("duplicate-class",
                                 f"rows {i} and {j} are both [[{n},{k},{d}]] and "
                                 f"their gates ({left['gate']} and "
                                 f"{right['gate']}) are the same up to an "
                                 f"invertible change of the output basis and "
                                 f"diagonal Clifford corrections"))
    # A note is spurious exactly when every pair its row takes part in was
    # decided: then there is nothing for its distinctness to be undecided
    # against.  Judged AFTER the searches, on their verdicts, so the rule can
    # never demand a note (above) that it then refuses (here).
    for index, row in readable:
        if row.get("dedup_note") and index not in undecided_rows:
            problems.append(("schema",
                             f"row {index} carries a dedup_note, but its "
                             f"distinctness from every other "
                             f"[[{row.get('n')},{row['k']},{row.get('d')}]] row in this file "
                             f"was decided -- there is nothing for the note "
                             f"to be about"))
    return problems


def _circuit_provenance_problems(row):
    """A shipped circuit no source recorded must SAY it is not one of theirs.

    Every ``sources`` entry stores the ``N`` its own file published, and until
    now nothing compared those with the row's.  They agreed by construction --
    `merge_results` appends a source entry for the circuit it keeps, so the
    kept ``N`` is always some source's ``N`` -- which made the agreement an
    invariant nobody had written down, and therefore one a hand-edit could
    break in silence.  A row whose ``N`` matches no source is a circuit that
    exists verbatim in none of the files it credits, and a reader who follows
    the citation finds a different circuit with no explanation of the gap.

    That is allowed, because a catalogue may legitimately improve on what it
    was given -- deleting a redundant check wire is exactly such an improvement
    -- but it may not be silent.  So the rule is the ``sk_key_note`` rule
    again: the row carries ``columns_note`` when, and only when, there is
    something for it to explain.
    """
    sources = row.get("sources")
    if not isinstance(sources, list):
        return []                       # its TYPE is reported by the schema pass
    if not sources:
        # The shape grammar accepts ``[]`` -- a list of objects with none in it
        # -- so nothing else rejects this, and an empty ``sources`` silently
        # disables the very comparison below.  A row that cites nothing has no
        # provenance at all, which is not a state this catalogue publishes.
        return [("provenance",
                 "the row cites no source, so nothing records where this "
                 "circuit came from and there is nothing for its N to agree "
                 "with")]
    published = [s.get("N") for s in sources if isinstance(s, dict)]
    if not all(type(N) is int for N in published):
        return []                       # a broken source entry, reported elsewhere
    if row["N"] in published:
        if "columns_note" in row:
            return [("schema",
                     "the row carries a columns_note explaining a circuit that "
                     "is exactly what its sources published")]
        return []
    if "columns_note" not in row:
        return [("provenance",
                 f"N={row['N']} but every source published "
                 f"{sorted(set(published))}, so this circuit is in none of the "
                 f"files the row credits and nothing says why")]
    return []


def provenance_problems(payload):
    """Rows whose ``regimes`` / ``strongest_claim`` disagree with the header.

    ``strongest_claim`` is the sentence `MASTER_CATALOG.md` prints beside every
    row to say how strong that row's claim is -- "classified: nothing else
    exists in this window" versus "a verified witness, not a maximum".  It is
    not free prose: it is the header's definition of the row's STRONGEST
    regime, which is the first entry of ``regimes`` because ``regimes`` is kept
    in the header's own order, strongest first.  So all three of those are
    re-derivable from the row's regime NAMES plus the header, and all three are
    checked here:

    * every name is one the header defines -- an undefined regime renders a
      claim the file cannot explain, and `merge_results` registers a new name
      in the header precisely so this stays true;
    * the names are in the header's order, so ``regimes[0]`` really is the
      strongest and not merely the first one that happened to be appended;
    * ``strongest_claim`` is the header's sentence for ``regimes[0]``, compared
      literally, exactly as `verify_row` compares ``gate_human``.

    None of this is derivable from ``columns``, so it proves nothing about the
    circuit.  It is the same kind of check as the metric notes: a field a
    reader reads, kept honest against the only thing that defines it.
    """
    problems = []
    header = payload.get("regimes")
    if not isinstance(header, dict) or not header:
        return [("regime-header",
                 "the catalogue header carries no regimes map, so no row's "
                 "strongest_claim can be resolved")]
    glossary = payload.get("discovery")
    if not isinstance(glossary, dict) or not glossary:
        return [("regime-header",
                 "the catalogue header carries no discovery map, so no row's "
                 "discovery tag can be resolved")]
    order = list(header)
    for index, row in enumerate(payload["factories"], 1):
        if not _typed_row(row):
            continue        # already rejected by verify_row on the same shape
        names = row.get("regimes")
        if not isinstance(names, list) or not names \
                or not all(isinstance(name, str) for name in names):
            problems.append(("regime-mismatch",
                             f"row {index} lists no regime (or lists one that "
                             f"is not a name), so nothing says how strong its "
                             f"claim is"))
            continue
        unknown = [name for name in names if name not in header]
        if unknown:
            problems.append(("regime-mismatch",
                             f"row {index} cites regime(s) "
                             f"{', '.join(map(repr, unknown))} that this "
                             f"catalogue's header does not define"))
            continue
        ranks = [order.index(name) for name in names]
        if ranks != sorted(ranks):
            problems.append(("regime-mismatch",
                             f"row {index} lists {names} out of the header's "
                             f"strongest-first order, so regimes[0] is not "
                             f"its strongest claim"))
        expected = header[names[min(range(len(ranks)), key=ranks.__getitem__)]]
        if row.get("strongest_claim") != expected:
            problems.append(("strongest_claim-mismatch",
                             f"row {index} says strongest_claim="
                             f"{row.get('strongest_claim')!r}, but its "
                             f"strongest regime is defined as {expected!r}"))
        # ``discovery`` is the table's other published axis and the one
        # `catalogfile.render_markdown` COUNTS rows by.  `merge_results`
        # already refuses a value the header does not define; nothing here did,
        # so a hand-edited ``discovery`` passed every check this file makes
        # while dropping out of the rendered "N + M rows" split -- the file
        # reported clean and the page it generates no longer added up.
        if row.get("discovery") not in glossary:
            problems.append(("discovery-mismatch",
                             f"row {index} says discovery="
                             f"{row.get('discovery')!r}, which this "
                             f"catalogue's header does not define "
                             f"({', '.join(map(repr, glossary))})"))
    return problems


def citation_problems(payload):
    """Rows whose ``citations`` do not resolve against the header.

    A citation is a curation decision -- which published work states a class,
    and which report this catalogue lists it in -- and nothing in this folder
    re-derives it.  What CAN be checked is the thing a reader relies on: every
    row credits at least one work, credits none twice, and every key it names
    is an entry of the header's ``references`` map, so the rendered
    "References" section really has the line the table points at.
    """
    references = payload.get("references")
    if not isinstance(references, dict) or not references:
        return [("citation-header",
                 "the catalogue header carries no references map, so no row's "
                 "citations can be resolved")]
    problems = []
    for index, row in enumerate(payload["factories"], 1):
        if not _typed_row(row):
            continue        # already rejected by verify_row on the same shape
        keys = row.get("citations")
        if not isinstance(keys, list) or not keys:
            problems.append(("citation-mismatch",
                             f"row {index} cites no work, so nothing says "
                             f"whose result this class is"))
            continue
        if len(set(keys)) != len(keys):
            problems.append(("citation-mismatch",
                             f"row {index} cites {keys}, naming a work more "
                             f"than once"))
        unknown = [key for key in keys if key not in references]
        if unknown:
            problems.append(("citation-mismatch",
                             f"row {index} cites "
                             f"{', '.join(map(repr, unknown))}, which this "
                             f"catalogue's references map does not define"))
    return problems


CERTIFICATE_FIELDS = ("d_certified", "d_certified_is_exact", "d_certified_source")


def certificate_problems(row):
    """A source's distance certificate that is incomplete or says nothing true.

    The certificate is not re-derived -- it exists because the sweep that would
    re-derive it is out of reach -- so what is checked is its consistency with
    what WAS proved here: the three fields come together; the certificate is
    stronger than the proved floor ``d`` (otherwise it is noise); the row's own
    distance is not already exact (an exact ``d`` leaves nothing to certify);
    and it does not exceed a proved upper bound ``d_upper``.
    """
    present = [name for name in CERTIFICATE_FIELDS if name in row]
    if not present:
        return []
    if len(present) != len(CERTIFICATE_FIELDS):
        missing = [name for name in CERTIFICATE_FIELDS if name not in row]
        return [("certificate", f"a distance certificate without "
                                f"{', '.join(missing)}")]
    problems = []
    if row["d_is_exact"]:
        problems.append(("certificate",
                         f"d={row['d']} is proved exact here, so a certificate "
                         f"d_certified={row['d_certified']} is either redundant "
                         f"or contradicts it"))
    elif row["d_certified"] <= row["d"]:
        problems.append(("certificate",
                         f"d_certified={row['d_certified']} is not stronger "
                         f"than the proved floor d>={row['d']}"))
    upper = row.get("d_upper")
    if isinstance(upper, int) and row["d_certified"] > upper:
        problems.append(("certificate",
                         f"d_certified={row['d_certified']} exceeds the proved "
                         f"upper bound d_upper={upper}"))
    if not row["d_certified_source"].strip():
        problems.append(("certificate", "the certificate names no source"))
    return problems


def row_monomials(row):
    """The row's gate as a monomial set, from its columns -- or ``None``.

    ``None`` when the row's ``(k, N, columns)`` cannot even be indexed as a
    circuit.  Such a row has already failed `verify_row` on the same grounds;
    re-deriving a gate from it here would turn that recorded failure into an
    ``IndexError`` -- a verifier that crashes on input it has already rejected
    has not finished rejecting it.
    """
    if structural_problems(row.get("k"), row.get("N"), row.get("columns")):
        return None
    columns = [tuple(sorted(set(c))) for c in row["columns"]]
    return FC.recover_gate(FC.rows_over_columns(columns, row["N"]), row["k"])


def header_problems(payload):
    """The header the file promises to carry, present, typed, and consistent.

    `catalogfile.HEADER_KEYS` names what `merge_results` writes onto a rebuilt
    payload and what `provenance_problems` and `MASTER_CATALOG.md` read back
    out of it; until now nothing checked that a shipped file actually carries
    them, so the constant was a promise with no test.  ``n_classes`` is checked
    too because it is the one header value that is DERIVABLE -- a count that
    disagrees with the rows it counts is exactly the kind of stale published
    number every other check in this file exists to catch.
    """
    problems = []
    for key in CF.HEADER_KEYS:
        if key not in payload:
            problems.append(("header", f"the catalogue header is missing "
                                       f"{key!r}"))
        elif key == "references":
            entries = payload[key]
            if not isinstance(entries, dict):
                problems.append(("header", "header 'references' is not an "
                                           "object"))
            elif not all(isinstance(name, str) and isinstance(entry, dict)
                         and set(entry) == set(CF.REFERENCE_FIELDS)
                         and all(isinstance(entry[f], str) and entry[f]
                                 for f in CF.REFERENCE_FIELDS)
                         for name, entry in entries.items()):
                # the map IS the meaning of every row's citation keys, so an
                # entry without a label and a full line is a citation no reader
                # can follow
                problems.append(("header", "header 'references' maps something "
                                           "other than names to "
                                           "{short, full} strings"))
        elif key in ("regimes", "discovery"):
            if not isinstance(payload[key], dict):
                problems.append(("header", f"header {key!r} is not an object"))
            elif not all(isinstance(name, str) and isinstance(text, str)
                         for name, text in payload[key].items()):
                # the maps ARE the meaning of every row's regime names, so a
                # non-string entry is a definition no row can be checked against
                problems.append(("header", f"header {key!r} maps something "
                                           f"other than names to sentences"))
        elif not isinstance(payload[key], str):
            problems.append(("header", f"header {key!r} is not a string"))
    stated = payload.get("n_classes")
    if "n_classes" not in payload:
        # The docstring above promises this count is checked BECAUSE it is the
        # one header value that is derivable and so the one that goes stale.  A
        # missing count was passing: the guards below all read "is not None",
        # which is true of a wrong count and equally true of no count at all.
        problems.append(("header", "the catalogue header is missing "
                                   "'n_classes', the one header value the "
                                   "rows themselves determine"))
    elif stated is None:
        # ``is not None`` guarded all three branches below, so a missing count
        # was caught (above) and an explicit ``null`` was not.
        problems.append(("header", "the header's n_classes is null; the row "
                                   "count is derivable and must be stated"))
    elif not isinstance(stated, int) or isinstance(stated, bool):
        # `True == 1` in Python and not in JSON: a boolean count compared
        # EQUAL to a one-row file and passed, which is the exact conflation
        # `catalogfile`'s field typing exists to prevent -- so the header
        # value is held to the same bar as every row value.
        problems.append(("header", f"the header says n_classes={stated!r}, "
                                   f"which is not a whole number"))
    elif stated is not None and stated != len(payload["factories"]):
        problems.append(("header", f"the header says n_classes={stated!r} but "
                                   f"the file carries "
                                   f"{len(payload['factories'])} rows"))
    return problems


def verify_catalog(payload, budget=None, verbose=True, indices=None):
    """Verify every row (or a slice of them) plus the file-level checks.

    Returns ``(failures, checked)``: ``failures`` is a list of
    ``(index, row, problems)``, ``checked`` the number of rows examined.
    """
    rows = payload["factories"]
    wanted = range(1, len(rows) + 1) if indices is None else indices
    failures, checked = [], 0
    for index in wanted:
        row = rows[index - 1]
        started = time.time()
        _facts, problems = verify_row(row, budget)
        checked += 1
        # `verify_row` rejects a non-object row instead of crashing on it; the
        # progress line has to clear the same bar.
        field = row.get if isinstance(row, dict) else (lambda _name: None)
        tag = (f"[[{field('n')},{field('k')},"
               f"{'' if field('d_is_exact') else '>='}{field('d')}]]")
        if problems:
            failures.append((index, row, problems))
            print(f"FAIL  {index:>4}. {tag:<18} {str(field('gate'))[:40]}")
            for kind, detail in problems:
                print(f"          - {kind}: {detail}")
        elif verbose:
            print(f"ok    {index:>4}. {tag:<18} "
                  f"{str(field('gate'))[:40]:<40} "
                  f"{time.time() - started:6.2f}s", flush=True)
    if indices is None:
        for kind, detail in (duplicate_class_problems(rows)
                             + provenance_problems(payload)
                             + citation_problems(payload)
                             + header_problems(payload)):
            failures.append((None, None, [(kind, detail)]))
            print(f"FAIL  file-level - {kind}: {detail}")
    return failures, checked


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--catalog", type=Path, default=CF.CATALOG_JSON,
                        help="the catalogue JSON to verify")
    parser.add_argument("--rows", default=None,
                        help="a 1-based slice, e.g. 1-20 or 7; the file-level "
                             "duplicate check is skipped when this is given")
    parser.add_argument("--quiet", action="store_true",
                        help="print only failures and the summary")
    args = parser.parse_args(argv)

    payload = CF.load(args.catalog)
    total = len(payload["factories"])
    indices = None
    if args.rows:
        first, _, last = args.rows.partition("-")
        try:
            low, high = int(first), int(last or first)
        except ValueError:
            raise SystemExit(f"--rows {args.rows!r} is not a row or a range "
                             f"like 12 or 12-40")
        if low < 1 or high > total:
            raise SystemExit(f"--rows {args.rows} is outside 1-{total}")
        if high < low:
            # ``range(2, 2)`` is empty, so a reversed range checked nothing,
            # printed PASS and exited 0 -- a verifier reporting success for
            # work it did not do, which is the one thing it may never say.
            raise SystemExit(f"--rows {args.rows} runs backwards; "
                             f"nothing would be verified")
        indices = range(low, high + 1)

    started = time.time()
    print(f"verifying {len(indices) if indices else total} of {total} rows of "
          f"{args.catalog.name}", flush=True)
    failures, checked = verify_catalog(payload, verbose=not args.quiet,
                                       indices=indices)
    elapsed = time.time() - started
    if failures:
        print(f"\nFAILED: {len(failures)} problem(s) over {checked} rows "
              f"({elapsed:.1f}s). A row that fails honest verification is NOT "
              f"to be deleted: record it and leave it marked.")
        return 1
    print(f"\nPASS: {checked} rows re-derived from their columns in "
          f"{elapsed:.1f}s -- gate, check parities, distance (absence proved "
          f"below d, presence witnessed at it), output width modulo the check "
          f"span, spectator and pseudo-output freedom, no check wire whose "
          f"syndrome bit the others already decide, T-count and reduced "
          f"degree where computable, and a circuit its own sources published "
          f"or a note saying why not"
          + ("" if indices else ", and no two rows are the same GL(k,2) class, "
             "every row's regimes, strongest_claim and citations resolve "
             "against the file's own header, and the header itself is "
             "present, typed and counts the rows it has"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
