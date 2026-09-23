#!/usr/bin/env python3
"""Exact, standard-library check-parent analysis.

For a fixed check code ``C`` this module constructs

``R(C) = (C^<2>)^perp``, ``W_d = R(C) intersect Z_<d^perp``, and
``V_d(C) = W_d/C``.

It then computes the parent-filter chain (``../theory/03_parent_first.md``):

``kappa_d``
    Dimension of the legal quotient ``V_d(C)`` (linear algebra).
``mu_d``
    Largest mutually compatible subspace of ``V_d(C)`` (exact enumeration).
``tau_D``
    Largest width carrying a requested target family (exact frame search).

All vectors are Python integers and all arithmetic is over F_2.  There is no
NumPy or solver dependency.  Expensive searches accept a node budget; hitting
it is returned as ``complete=False`` and is never presented as a certificate.

Construction itself is bounded: ``Parent`` stores all ``2^kappa`` coset
representatives, so ``from_points``/``from_columns`` refuse a parent whose
``kappa`` exceeds ``MAX_QUOTIENT_DIM`` (raising ``QuotientTooLarge``) instead
of allocating until the process dies.  See that constant for the numbers.

Bit conventions: a vector over the ``n`` columns has bit ``j`` = column ``j``;
a check point has bit ``b`` = check row ``b``; a quotient element is a
coordinate int with bit ``b`` = coefficient of ``quotient_basis[b]``.  Frames
are sequences of coordinate ints, one per output.
"""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass, replace
from itertools import combinations, permutations
from typing import Iterable, Iterator, Sequence


Monomial = frozenset[int]
Gate = frozenset[Monomial]


class SearchLimit(RuntimeError):
    """Raised internally when an exact search reaches its declared budget."""


#: Largest quotient dimension ``Parent`` will construct.  ``from_points``
#: materialises all ``2^kappa`` coset representatives, so kappa is a hard
#: memory/time exponent: kappa = 21 is ~2M representatives (about a second,
#: tens of MB), kappa = 30 is ~1e9 (minutes, tens of GB), and the check parent
#: of the catalogued ``[[141,2,4]]`` has kappa = 79.  Without this cap those
#: parents do not fail -- the process is killed while filling the list, which
#: a caller reads as a hang or, worse, as success.  A parent over the cap is
#: refused up front, before any allocation, with its kappa in the message.
#:
#: 21 is deliberate rather than round: it is exactly the kappa of the
#: ``[[47,3,3]]`` CCZ parent, the largest one this repository's own examples
#: and tests analyse.  The catalogued parents that motivate the cap sit well
#: above it (25 for ``[[85,1,5]]``, 27 for ``[[63,4,3]]``, 79 for
#: ``[[141,2,4]]``); nothing in any catalogue lies between 21 and 25.
MAX_QUOTIENT_DIM = 21


class QuotientTooLarge(ValueError):
    """A parent whose ``kappa`` exceeds the requested cap.

    A ``ValueError`` so the CLIs report it as bad input rather than a crash.
    ``kappa`` is exact: it is computed from ranks alone, before the
    ``2^kappa`` representative table is built.
    """

    def __init__(self, kappa: int, cap: int) -> None:
        super().__init__(
            f"quotient dimension kappa={kappa} exceeds the cap {cap}: building "
            f"this parent needs 2^{kappa} coset representatives. The exact "
            f"enumerations in this repository run at kappa <= 11; raise "
            f"max_kappa deliberately (and expect ~2^kappa memory) if you mean "
            f"to build it anyway."
        )
        self.kappa = kappa
        self.cap = cap


# ------------------------------------------------------------------ F_2 tools
def rref_dict(vectors: Iterable[int]) -> dict[int, int]:
    """Canonical reduced basis, represented as ``pivot -> row``.

    Fully reduced: each pivot bit appears in exactly one stored row, so the
    basis is unique for the span and reduction against it is linear.
    """
    basis: dict[int, int] = {}
    for vector in vectors:
        value = int(vector)
        for pivot in sorted(basis, reverse=True):
            if (value >> pivot) & 1:
                value ^= basis[pivot]
        if not value:
            continue
        pivot = value.bit_length() - 1
        for old_pivot, old in list(basis.items()):
            if (old >> pivot) & 1:
                basis[old_pivot] = old ^ value
        basis[pivot] = value
    return basis


def canonical_basis(vectors: Iterable[int]) -> tuple[int, ...]:
    """RREF rows, highest pivot first: a canonical key for span(vectors)."""
    basis = rref_dict(vectors)
    return tuple(basis[p] for p in sorted(basis, reverse=True))


def reduce_mod(vector: int, basis: Iterable[int] | dict[int, int]) -> int:
    """Canonical coset representative of ``vector`` modulo span(basis).

    Linear in ``vector`` (the basis is fully reduced), so canonical
    representatives are closed under XOR.
    """
    rref = basis if isinstance(basis, dict) else rref_dict(basis)
    value = vector
    for pivot in sorted(rref, reverse=True):
        if (value >> pivot) & 1:
            value ^= rref[pivot]
    return value


def nullspace(rows: Iterable[int], width: int) -> tuple[int, ...]:
    """Basis of vectors orthogonal to every row (``<u,v> = parity(u & v)``).

    One basis vector per non-pivot column of the RREF of ``rows``.
    """
    basis = rref_dict(rows)
    pivots = set(basis)
    out = []
    for free in range(width):
        if free in pivots:
            continue
        vector = 1 << free
        for pivot, row in basis.items():
            if (row >> free) & 1:
                vector |= 1 << pivot
        out.append(vector)
    return tuple(out)


def span(basis: Sequence[int]) -> list[int]:
    """All XOR combinations: 2^len(basis) values when ``basis`` is independent."""
    values = [0]
    for row in basis:
        values += [value ^ row for value in values]
    return values


def rank(rows: Iterable[int]) -> int:
    """F_2 rank of the row set."""
    return len(rref_dict(rows))


def parity(value: int) -> int:
    """Bit count mod 2; the F_2 inner product is ``parity(u & v)``."""
    return value.bit_count() & 1


# --------------------------------------------------------------- gate helpers
def gate_key(wants: Iterable[Iterable[int]]) -> tuple[tuple[int, ...], ...]:
    """Canonical sorted monomial tuple: the comparison/dedup key of a gate."""
    return tuple(sorted((tuple(sorted(q)) for q in wants), key=lambda q: (len(q), q)))


def gate_name(wants: Iterable[Iterable[int]]) -> str:
    """``T0.CS12.CCZ345``-style label; ``"I"`` for the empty gate."""
    names = {1: "T", 2: "CS", 3: "CCZ"}
    key = gate_key(wants)
    return ".".join(names[len(q)] + "".join(map(str, q)) for q in key) or "I"


def parse_gate(spec: str) -> Gate:
    """Parse ``T0.T1.CS01.CCZ012`` or ``0+1+01+012``.

    Output indices are single digits (outputs 0..9); degrees 1..3 only.
    """
    wants: set[Monomial] = set()
    tokens = spec.replace("+", ".").replace(" ", "").split(".")
    for token in tokens:
        if not token or token.upper() in {"I", "CLIFFORD", "CHECK-ONLY"}:
            continue
        digits = "".join(ch for ch in token if ch.isdigit())
        if not digits:
            raise ValueError(f"gate token {token!r} has no output indices")
        support = frozenset(int(ch) for ch in digits)
        if len(support) != len(digits) or not 1 <= len(support) <= 3:
            raise ValueError(f"invalid degree-<=3 gate token {token!r}")
        prefix = token[: len(token) - len(digits)].upper()
        expected = {1: {"", "T"}, 2: {"", "CS"}, 3: {"", "CCZ"}}
        if prefix not in expected[len(support)]:
            raise ValueError(f"prefix/arity mismatch in gate token {token!r}")
        wants.add(support)
    return frozenset(wants)


def gate_of_rows(rows: Sequence[int]) -> Gate:
    """Gate of output rows: monomial S wanted iff ``|AND_{i in S} rows[i]|`` is odd."""
    wants: set[Monomial] = set()
    for degree in (1, 2, 3):
        for subset in combinations(range(len(rows)), degree):
            # -1 is the all-ones seed for the running AND.
            product = -1
            for index in subset:
                product &= rows[index]
            if parity(product):
                wants.add(frozenset(subset))
    return frozenset(wants)


def verify_columns(
    columns: Sequence[Sequence[int]],
    outputs: int,
    total_rows: int,
    wants: Gate,
    distance_cap: int = 4,
) -> tuple[bool, int | str]:
    """Independently re-read parity and low-weight fault distance.

    Returns ``(parity_ok, distance)`` where ``distance`` is the weight of the
    lightest harmful fault found, else ``">cap"``.  Harmful = zero syndrome
    on every check yet nonzero on the outputs (bits ``< outputs``).  Repeated
    columns are rejected outright as ``(False, 2)``.
    """
    normalized = [frozenset(column) for column in columns]
    if len(set(normalized)) != len(normalized):
        return False, 2

    def column_parity(subset: Iterable[int]) -> int:
        required = frozenset(subset)
        return sum(required <= column for column in normalized) & 1

    parity_ok = True
    for degree in (1, 2, 3):
        for subset in combinations(range(total_rows), degree):
            expected = int(all(index < outputs for index in subset) and frozenset(subset) in wants)
            parity_ok &= column_parity(subset) == expected

    masks = [sum(1 << q for q in column) for column in normalized]
    output_mask = (1 << outputs) - 1

    def harmful(value: int) -> bool:
        return value != 0 and value & ~output_mask == 0

    for weight in range(1, distance_cap + 1):
        for support in combinations(range(len(masks)), weight):
            value = 0
            for index in support:
                value ^= masks[index]
            if harmful(value):
                return parity_ok, weight
    return parity_ok, f">{distance_cap}"


def covered_width(wants: Gate) -> int:
    """Number of outputs touched by some monomial (spectators excluded)."""
    return len(set().union(*wants)) if wants else 0


def sk_canonical(k: int, wants: Gate) -> tuple[tuple[tuple[int, ...], ...], tuple[int, ...]]:
    """Return the S_k key and a permutation attaining it.

    NOTE the encoding: `gate_key` orders monomials DEGREE-MAJOR, while the
    catalogues' own S_k implementations order them plainly lexicographically.
    Both minimise over the same k! images, so both are orbit invariants and both
    induce exactly the same partition into S_k classes -- which is all a dedup
    key has to do.  They can and do pick a DIFFERENT REPRESENTATIVE of the same
    orbit, so this key's rendering need not equal the published gate string
    (`T0.T1.CS01` here where the catalogue writes `0+01+1`).  Published names
    always come from the catalogue implementations.
    `tests/test_sk_agreement.py` pins both halves of that: identical partitions,
    and the trio of catalogue implementations agreeing representative for
    representative.
    """
    best = None
    best_perm = tuple(range(k))
    for perm in permutations(range(k)):
        image = gate_key(frozenset(frozenset(perm[i] for i in q) for q in wants))
        if best is None or image < best:
            best, best_perm = image, perm
    return best or (), best_perm


def _forms_from_gate(k: int, wants: Gate):
    """Linear, bilinear and trilinear phase tensors, including coincidences."""
    # Coincidences: parity(a & a) = parity(a) and parity(a & a & b) =
    # parity(a & b), so beta's diagonal is ell and tau's repeated indices
    # fall back to beta/ell.  These entries are what Boolean substitution
    # drops.
    ell = [int(frozenset((i,)) in wants) for i in range(k)]
    beta = [[0] * k for _ in range(k)]
    for i in range(k):
        beta[i][i] = ell[i]
        for j in range(i + 1, k):
            beta[i][j] = beta[j][i] = int(frozenset((i, j)) in wants)
    tau = {}
    for i in range(k):
        for j in range(k):
            for ell_index in range(k):
                unique = sorted({i, j, ell_index})
                if len(unique) == 1:
                    value = ell[unique[0]]
                elif len(unique) == 2:
                    value = beta[unique[0]][unique[1]]
                else:
                    value = int(frozenset(unique) in wants)
                tau[(i, j, ell_index)] = value
    return ell, beta, tau


def transform_gate(k: int, wants: Gate, matrix_rows: Sequence[int]) -> Gate:
    """Correct output-CNOT action for ``new_i = sum_j M[i,j] old_j``.

    Ordinary Boolean-polynomial substitution is incorrect here because the
    T/CS/CCZ coefficients are 1/2/4 modulo 8.  The coincident entries of the
    bilinear and trilinear tensors carry the required phase information.

    Exact identity (bitwise multilinearity of the moment parities; covered by
    the unit tests): ``gate_of_rows(transform_frame(rows, M)) ==
    transform_gate(k, gate_of_rows(rows), M)`` for every row tuple.
    """
    ell, beta, tau = _forms_from_gate(k, wants)
    indices = [[j for j in range(k) if (row >> j) & 1] for row in matrix_rows]
    out: set[Monomial] = set()
    for i in range(k):
        if sum(ell[j] for j in indices[i]) & 1:
            out.add(frozenset((i,)))
    for i, j in combinations(range(k), 2):
        value = 0
        for p in indices[i]:
            for q in indices[j]:
                value ^= beta[p][q]
        if value:
            out.add(frozenset((i, j)))
    for i, j, ell_index in combinations(range(k), 3):
        value = 0
        for p in indices[i]:
            for q in indices[j]:
                for t in indices[ell_index]:
                    value ^= tau[(p, q, t)]
        if value:
            out.add(frozenset((i, j, ell_index)))
    return frozenset(out)


def _gl_generators(k: int) -> tuple[tuple[int, ...], ...]:
    """The elementary transvections ``row_i ^= row_j``; they generate GL(k,2)."""
    generators = []
    for i in range(k):
        for j in range(k):
            if i == j:
                continue
            rows = [1 << q for q in range(k)]
            rows[i] ^= 1 << j
            generators.append(tuple(rows))
    return tuple(generators)


def _matmul_rows(left: Sequence[int], right: Sequence[int]) -> tuple[int, ...]:
    """Row-convention product: ``out[i]`` = XOR of ``right[j]`` over set bits j of ``left[i]``."""
    out = []
    for row in left:
        value = 0
        for j in range(len(right)):
            if (row >> j) & 1:
                value ^= right[j]
        out.append(value)
    return tuple(out)


def gl_orbit(
    k: int, wants: Gate, limit: int | None = None
) -> tuple[dict[Gate, tuple[int, ...]], bool]:
    """Enumerate the correct GL(k,2) orbit and a basis change for each member.

    Invariant: ``seen[g] = M`` with ``g = transform_gate(k, wants, M)``.
    Hitting ``limit`` returns the partial dict with ``False``; the minimum of
    a partial orbit is not a canonical invariant, so callers must not treat
    it as a dedup certificate.
    """
    identity = tuple(1 << i for i in range(k))
    seen: dict[Gate, tuple[int, ...]] = {wants: identity}
    queue = deque([wants])
    generators = _gl_generators(k)
    while queue:
        current = queue.popleft()
        current_matrix = seen[current]
        for generator in generators:
            image = transform_gate(k, current, generator)
            if image in seen:
                continue
            if limit is not None and len(seen) >= limit:
                return seen, False
            seen[image] = _matmul_rows(generator, current_matrix)
            queue.append(image)
    return seen, True


def transform_frame(frame: Sequence[int], matrix_rows: Sequence[int]) -> tuple[int, ...]:
    """New frame ``out[i]`` = XOR of ``frame[j]`` over set bits j of row i (same convention as transform_gate)."""
    out = []
    for row in matrix_rows:
        value = 0
        for j in range(len(frame)):
            if (row >> j) & 1:
                value ^= frame[j]
        out.append(value)
    return tuple(out)


# --------------------------------------------------------------- parent model
@dataclass(frozen=True)
class Parent:
    """The check parent and its colored quotient at a fixed target distance.

    ``points[j]`` is column ``j``'s check syndrome (bit b = check row b); the
    other stored vectors live over the n columns (bit j = column j).
    ``quotient_basis`` rows are canonical coset representatives mod C, so
    their XORs stay canonical; ``quotient_reps[x]`` is the representative of
    coordinate int ``x``.  ``compatibility_forms[c]`` stores the alternating
    form B_c row-wise as coordinate covectors.  ``seed_frame`` is the native
    output frame recovered by ``from_columns`` (a positive control), if any.
    """

    points: tuple[int, ...]
    ambient_rank: int
    distance: int
    check_rows: tuple[int, ...]
    check_rank: int
    schur_square: tuple[int, ...]
    short_faults: tuple[int, ...]
    quotient_basis: tuple[int, ...]
    quotient_reps: tuple[int, ...]
    compatibility_forms: tuple[tuple[int, ...], ...]
    seed_frame: tuple[int, ...] | None = None

    @classmethod
    def from_points(
        cls,
        points: Iterable[int],
        ambient_rank: int | None = None,
        distance: int = 3,
        max_kappa: int = MAX_QUOTIENT_DIM,
    ) -> "Parent":
        """Validate a check parent and construct its quotient ``V_d(C)``.

        Raises ``ValueError`` before any search runs if the parent cannot
        support ``distance`` (zero/repeated syndromes, odd check-only
        moments, rank zero), and ``QuotientTooLarge`` -- also before any
        allocation -- if ``kappa`` exceeds ``max_kappa``.
        """
        # Preserve column order.  Sorting is harmless for a bare point set but
        # would detach stored output-row bits from their columns in
        # ``from_columns`` and silently corrupt seed witnesses.
        pts = tuple(int(point) for point in points)
        if not pts:
            raise ValueError("a check parent needs at least one column")
        if distance < 2:
            raise ValueError("distance must be at least 2")
        inferred = max(1, max(pts).bit_length())
        ambient = inferred if ambient_rank is None else int(ambient_rank)
        if ambient < inferred:
            raise ValueError("ambient_rank is too small for the supplied check points")
        if any(point < 0 for point in pts):
            raise ValueError("check points must be nonnegative integers")
        if distance >= 2 and any(point == 0 for point in pts):
            raise ValueError("distance >= 2 requires nonzero check syndromes")
        if distance >= 3 and len(set(pts)) != len(pts):
            raise ValueError("distance >= 3 requires distinct check syndromes")

        n = len(pts)
        raw_rows = []
        for bit in range(ambient):
            raw_rows.append(sum(1 << j for j, point in enumerate(pts) if (point >> bit) & 1))
        checks = canonical_basis(raw_rows)
        check_rank = len(checks)
        if check_rank == 0:
            raise ValueError("the check parent has rank zero")

        # Check-only moments through degree three must vanish.
        for degree in (1, 2, 3):
            for subset in combinations(range(check_rank), degree):
                product = -1
                for index in subset:
                    product &= checks[index]
                if parity(product):
                    raise ValueError(
                        f"check-only degree-{degree} moment is odd for rows {subset}"
                    )

        square = canonical_basis(
            checks[i] & checks[j]
            for i in range(check_rank)
            for j in range(i, check_rank)
        )
        # Z_<d is spanned by every zero-syndrome support of weight < d.  For
        # d <= 3 the nonzero/distinct syndromes above already exclude such
        # supports, so the enumeration only runs for d > 3.
        faults = []
        if distance > 3:
            for weight in range(1, distance):
                for support in combinations(range(n), weight):
                    syndrome = 0
                    mask = 0
                    for index in support:
                        syndrome ^= pts[index]
                        mask |= 1 << index
                    if syndrome == 0:
                        faults.append(mask)
        short_faults = canonical_basis(faults)
        # W_d = R(C) cap Z_<d^perp = (C^<2> + Z_<d)^perp.
        legal = nullspace(square + short_faults, n)

        # C <= W_d always holds (C is orthogonal to C^<2> and to every
        # zero-syndrome support), so a failure here is an internal error.
        legal_rref = rref_dict(legal)
        for check in checks:
            if reduce_mod(check, legal_rref):
                raise ValueError("C is not contained in W_d; the parent is inconsistent")

        # kappa = dim W_d - dim C, from ranks alone.  Checked here, before the
        # 2^kappa representative table below is allocated.
        kappa = len(legal) - check_rank
        if kappa > max_kappa:
            raise QuotientTooLarge(kappa, max_kappa)

        # V_d = W_d/C: store canonical coset reps; quotient_span tracks their
        # independence (nonzero residual <=> new quotient direction).
        check_rref = rref_dict(checks)
        quotient_span: dict[int, int] = {}
        quotient_basis = []
        for legal_row in legal:
            representative = reduce_mod(legal_row, check_rref)
            residual = reduce_mod(representative, quotient_span)
            if residual:
                quotient_span[residual.bit_length() - 1] = residual
                quotient_basis.append(representative)
        quotient_basis_t = tuple(quotient_basis)
        if len(quotient_basis_t) != kappa:
            raise RuntimeError(
                f"quotient basis has {len(quotient_basis_t)} vectors but the "
                f"rank bound says kappa={kappa}: the 2^kappa enumeration below "
                f"would not be the whole quotient")
        # All 2^kappa representatives, indexed by coordinate int.  Linearity
        # of reduce_mod keeps every XOR of basis reps canonical.  O(2^kappa)
        # time and memory -- bounded by the max_kappa check above.
        reps = []
        for coordinates in range(1 << len(quotient_basis_t)):
            value = 0
            for bit, row in enumerate(quotient_basis_t):
                if (coordinates >> bit) & 1:
                    value ^= row
            reps.append(value)

        # B_c(e_i, e_j) = parity(q_i & q_j & c).  The diagonal vanishes
        # (q & q = q, and q in R(C) is orthogonal to c in C <= C^<2>), so
        # each form is alternating: pairwise compatibility of a basis makes
        # its whole span compatible.
        forms = []
        for check in checks:
            matrix_rows = []
            for left in quotient_basis_t:
                covector = 0
                for j, right in enumerate(quotient_basis_t):
                    if parity(left & right & check):
                        covector |= 1 << j
                matrix_rows.append(covector)
            forms.append(tuple(matrix_rows))

        return cls(
            points=pts,
            ambient_rank=ambient,
            distance=distance,
            check_rows=checks,
            check_rank=check_rank,
            schur_square=square,
            short_faults=short_faults,
            quotient_basis=quotient_basis_t,
            quotient_reps=tuple(reps),
            compatibility_forms=tuple(forms),
        )

    @classmethod
    def from_columns(
        cls,
        columns: Sequence[Iterable[int]],
        outputs: int,
        total_rows: int | None = None,
        distance: int = 3,
        max_kappa: int = MAX_QUOTIENT_DIM,
    ) -> "Parent":
        """Parent of stored factory columns (outputs ``0..outputs-1`` first).

        If every output row reduces to a legal quotient element and the rows
        form an independent pairwise-compatible frame, they are retained as
        ``seed_frame`` -- a positive control for ``find_target``.  Otherwise
        the parent is returned without a seed; that is not an error.
        """
        normalized = [frozenset(int(q) for q in column) for column in columns]
        if outputs < 0:
            raise ValueError("outputs must be nonnegative")
        inferred_rows = 1 + max((max(column, default=-1) for column in normalized), default=-1)
        nrows = inferred_rows if total_rows is None else int(total_rows)
        if nrows < inferred_rows or nrows <= outputs:
            raise ValueError("total_rows is inconsistent with the columns/outputs")
        points = []
        output_rows = [0] * outputs
        for column_index, column in enumerate(normalized):
            point = 0
            for q in column:
                if q < outputs:
                    output_rows[q] |= 1 << column_index
                else:
                    point |= 1 << (q - outputs)
            points.append(point)
        parent = cls.from_points(points, nrows - outputs, distance, max_kappa)
        check_rref = rref_dict(parent.check_rows)
        # Invert quotient_reps: canonical rep -> coordinate int (O(2^kappa)).
        coordinates = {row: index for index, row in enumerate(parent.quotient_reps)}
        seed = []
        for output_row in output_rows:
            representative = reduce_mod(output_row, check_rref)
            if representative not in coordinates:
                return parent
            seed.append(coordinates[representative])
        if len(canonical_basis(seed)) != len(seed):
            return parent
        if any(not parent.compatible(seed[i], seed[j])
               for i in range(len(seed)) for j in range(i + 1, len(seed))):
            return parent
        return replace(parent, seed_frame=tuple(seed))

    @property
    def n(self) -> int:
        """Number of columns (parity-T injections)."""
        return len(self.points)

    @property
    def kappa(self) -> int:
        """kappa_d = dim V_d(C)."""
        return len(self.quotient_basis)

    @property
    def quadric_degeneracy(self) -> int | None:
        """Generic dim of C^<2> (``r + C(r,2)``) minus its actual dim; d = 3 only."""
        if self.distance != 3:
            return None
        return self.check_rank + self.check_rank * (self.check_rank - 1) // 2 - len(
            self.schur_square
        )

    def representative(self, coordinates: int) -> int:
        """Canonical coset representative of the coordinate int."""
        return self.quotient_reps[coordinates]

    def columns(self, frame: Sequence[int]) -> list[list[int]]:
        """Explicit factory columns: outputs 0..k-1, then the ambient check rows.

        Check qubits are the ambient coordinates, so all ``ambient_rank``
        rows are kept even when ``check_rank`` is smaller.
        """
        output_rows = [self.representative(vector) for vector in frame]
        columns = []
        for index, point in enumerate(self.points):
            column = [q for q, row in enumerate(output_rows) if (row >> index) & 1]
            column += [len(frame) + bit for bit in range(self.ambient_rank) if (point >> bit) & 1]
            columns.append(column)
        return columns

    def gate(self, frame: Sequence[int]) -> Gate:
        """Gate implemented by ``frame`` (parities of representative AND-products)."""
        return gate_of_rows([self.representative(vector) for vector in frame])

    def compatible(self, left: int, right: int) -> bool:
        """True iff B_c(left, right) = 0 for every check row c."""
        return all(parity(apply_form(form, left) & right) == 0 for form in self.compatibility_forms)


def apply_form(form_rows: Sequence[int], vector: int) -> int:
    """Covector ``w`` with ``parity(w & v) = B(vector, v)`` for every ``v``."""
    covector = 0
    for index, row in enumerate(form_rows):
        if (vector >> index) & 1:
            covector ^= row
    return covector


def form_rank_bounds(parent: Parent) -> dict:
    """Ranks of the compatibility forms and the strongest single-combination bound.

    An alternating form of rank 2m admits isotropic subspaces of dimension at
    most ``kappa - m``, so the best rank over all 2^check_rank nonzero check
    combinations upper-bounds mu.  Exponential in check_rank.
    """
    basis_ranks = [rank(form) for form in parent.compatibility_forms]
    maximum = 0
    maximizing = 0
    for combination in range(1, 1 << len(parent.compatibility_forms)):
        rows = [0] * parent.kappa
        for index, form in enumerate(parent.compatibility_forms):
            if (combination >> index) & 1:
                rows = [left ^ right for left, right in zip(rows, form)]
        current = rank(rows)
        if current > maximum:
            maximum, maximizing = current, combination
    return {
        "basis_form_ranks": basis_ranks,
        "max_combined_form_rank": maximum,
        "maximizing_check_combination": maximizing,
        "mu_upper_bound": parent.kappa - maximum // 2,
    }


# ---------------------------------------------------------- compatible spaces
def compatible_subspaces(
    parent: Parent,
    kmax: int | None = None,
    node_budget: int | None = None,
) -> Iterator[tuple[int, ...]]:
    """Yield every compatible subspace once, by its canonical RREF basis.

    The empty subspace is included.  A ``SearchLimit`` is raised if the budget
    is reached.  The set-based canonical augmentation is deliberately simple
    and independently testable; unlike the legacy DFS it cannot count two
    different bases of the same subspace as two subspaces.

    ``node_budget`` counts dequeued subspaces (the empty one included); the
    node that would exceed it raises *before* being yielded, so callers must
    downgrade their result to ``complete=False``.
    """
    maximum = parent.kappa if kmax is None else min(kmax, parent.kappa)
    queue = deque([tuple()])
    seen = {tuple()}
    nodes = 0
    while queue:
        basis = queue.popleft()
        nodes += 1
        if node_budget is not None and nodes > node_budget:
            raise SearchLimit(f"compatible-subspace budget {node_budget} reached")
        yield basis
        if len(basis) >= maximum:
            continue
        # safe_basis spans every vector compatible with the whole current
        # basis; bilinearity extends that to the whole subspace.
        constraints = []
        for vector in basis:
            constraints.extend(apply_form(form, vector) for form in parent.compatibility_forms)
        safe_basis = nullspace(constraints, parent.kappa)
        extensions = set()
        basis_rref = rref_dict(basis)
        for vector in span(safe_basis):
            if vector and reduce_mod(vector, basis_rref):
                extensions.add(canonical_basis(basis + (vector,)))
        for extension in sorted(extensions):
            if extension not in seen:
                seen.add(extension)
                queue.append(extension)


def exact_mu(parent: Parent, node_budget: int | None = None) -> dict:
    """Exact mu_d by full compatible-subspace enumeration.

    On a budget hit ``value`` is only a lower bound, ``complete`` is False,
    and ``upper_bound`` falls back to the form-rank bound.
    """
    maximum = 0
    counts: Counter[int] = Counter()
    complete = True
    try:
        for basis in compatible_subspaces(parent, node_budget=node_budget):
            counts[len(basis)] += 1
            maximum = max(maximum, len(basis))
    except SearchLimit:
        complete = False
    bounds = form_rank_bounds(parent)
    return {
        "value": maximum,
        "complete": complete,
        "counts_by_dimension": dict(sorted(counts.items())),
        "upper_bound": maximum if complete else bounds["mu_upper_bound"],
    }


# ------------------------------------------------------------- target search
def find_target(
    parent: Parent,
    wants: Gate,
    width: int | None = None,
    node_budget: int | None = None,
) -> dict:
    """Find one exact ordered output frame for ``wants`` or certify absence.

    Every condition on the next frame row (its T parity, pair/triple parities
    against the chosen rows, compatibility) is affine in its quotient
    coordinates, so each level solves one linear system and branches only
    over the solution coset.  ``nodes`` counts coset candidates; a budget hit
    returns ``complete=False`` and is never a negative certificate, whereas
    ``width > kappa`` is a genuine absence certificate.  A stored seed frame
    matching ``wants`` is returned directly after independent re-verification.
    """
    target_width = width
    if target_width is None:
        target_width = 1 + max((max(q) for q in wants), default=-1)
    if any(max(q, default=-1) >= target_width for q in wants):
        raise ValueError("target monomial index exceeds the requested width")
    if target_width > parent.kappa:
        return {"found": False, "complete": True, "nodes": 0, "reason": "kappa bound"}

    if (
        parent.seed_frame is not None
        and len(parent.seed_frame) == target_width
        and parent.gate(parent.seed_frame) == wants
    ):
        columns = parent.columns(parent.seed_frame)
        parity_ok, distance = verify_columns(
            columns, target_width, target_width + parent.ambient_rank, wants,
            max(4, parent.distance - 1),
        )
        if not parity_ok or (isinstance(distance, int) and distance < parent.distance):
            raise AssertionError("the stored seed frame failed independent verification")
        return {
            "found": True,
            "complete": True,
            "nodes": 0,
            "seeded_by_input_frame": True,
            "frame": list(parent.seed_frame),
            "gate": gate_name(wants),
            "wants": [list(q) for q in gate_key(wants)],
            "distance": distance,
            "columns": columns,
        }

    nodes = 0
    frame: list[int] = []
    found: tuple[int, ...] | None = None

    def wanted(subset: Iterable[int]) -> int:
        return int(frozenset(subset) in wants)

    def solve_affine(constraints: Sequence[tuple[int, int]]):
        pivots: dict[int, tuple[int, int]] = {}
        for mask, rhs in constraints:
            value, bit = mask, rhs & 1
            for pivot in sorted(pivots, reverse=True):
                if (value >> pivot) & 1:
                    value ^= pivots[pivot][0]
                    bit ^= pivots[pivot][1]
            if not value:
                if bit:
                    return None
                continue
            pivot = value.bit_length() - 1
            for old_pivot, (old, old_rhs) in list(pivots.items()):
                if (old >> pivot) & 1:
                    pivots[old_pivot] = (old ^ value, old_rhs ^ bit)
            pivots[pivot] = (value, bit)
        particular = 0
        for pivot, (_row, rhs) in pivots.items():
            if rhs:
                particular |= 1 << pivot
        homogeneous = nullspace((row for row, _rhs in pivots.values()), parent.kappa)
        return particular, homogeneous

    # <single_covector, x> = parity of x's representative = its T parity.
    single_covector = sum(
        1 << index for index, row in enumerate(parent.quotient_basis) if parity(row)
    )

    def recurse() -> bool:
        nonlocal nodes, found
        q = len(frame)
        if q == target_width:
            found = tuple(frame)
            return True
        constraints: list[tuple[int, int]] = [(single_covector, wanted((q,)))]
        old_rows = [parent.representative(old) for old in frame]
        for old_coordinates in frame:
            constraints.extend(
                (apply_form(form, old_coordinates), 0)
                for form in parent.compatibility_forms
            )
        for i, old_row in enumerate(old_rows):
            covector = sum(
                1 << bit
                for bit, basis_row in enumerate(parent.quotient_basis)
                if parity(basis_row & old_row)
            )
            constraints.append((covector, wanted((i, q))))
        for i, j in combinations(range(q), 2):
            covector = sum(
                1 << bit
                for bit, basis_row in enumerate(parent.quotient_basis)
                if parity(basis_row & old_rows[i] & old_rows[j])
            )
            constraints.append((covector, wanted((i, j, q))))
        solution = solve_affine(constraints)
        if solution is None:
            return False
        particular, homogeneous = solution
        frame_rref = rref_dict(frame)
        for offset in span(homogeneous):
            candidate = particular ^ offset
            nodes += 1
            if node_budget is not None and nodes > node_budget:
                raise SearchLimit(f"target-search budget {node_budget} reached")
            if candidate == 0 or reduce_mod(candidate, frame_rref) == 0:
                continue
            frame.append(candidate)
            if recurse():
                return True
            frame.pop()
        return False

    complete = True
    try:
        recurse()
    except SearchLimit:
        complete = False
    result = {"found": found is not None, "complete": complete, "nodes": nodes}
    if found is not None:
        # Independent re-read of the witness; a failure here is a code bug,
        # never a search outcome.
        columns = parent.columns(found)
        gate = parent.gate(found)
        parity_ok, distance = verify_columns(
            columns, target_width, target_width + parent.ambient_rank, gate,
            max(4, parent.distance - 1),
        )
        if not parity_ok or (isinstance(distance, int) and distance < parent.distance):
            raise AssertionError("target-search witness failed independent verification")
        result.update(
            frame=list(found),
            gate=gate_name(gate),
            wants=[list(q) for q in gate_key(gate)],
            distance=distance,
            columns=columns,
        )
    return result


def tau_product_t(
    parent: Parent,
    max_width: int | None = None,
    node_budget: int | None = None,
) -> dict:
    """Largest width carrying ``T^w``, tried from kappa (or the cap) downward.

    One shared node budget is spent across the attempts.  A budget hit stops
    the sweep with ``value=None, complete=False``; ``value=0, complete=True``
    certifies that even a single T is impossible.
    """
    maximum = min(parent.kappa, max_width or parent.kappa)
    remaining = node_budget
    attempts = []
    for width in range(maximum, 0, -1):
        target = frozenset(frozenset((i,)) for i in range(width))
        result = find_target(parent, target, width, remaining)
        attempts.append({"width": width, **result})
        if remaining is not None:
            # remaining == 0 is a real zero budget here (the next attempt
            # trips on its first node), unlike the CLI where 0 = unlimited.
            remaining = max(0, remaining - result["nodes"])
        if result["found"]:
            return {"value": width, "complete": result["complete"], "attempts": attempts}
        if not result["complete"]:
            return {"value": None, "complete": False, "attempts": attempts}
    return {"value": 0, "complete": True, "attempts": attempts}


def certification_metrics(
    parent: Parent,
    target_family: str = "product-t",
    max_width: int | None = None,
    node_budget: int | None = None,
) -> dict:
    """Compute ``kappa_d >= mu_d >= tau_D`` with honest completion flags.

    ``node_budget`` applies per stage: once to ``exact_mu`` and once (shared
    across widths) to ``tau_product_t``.
    """
    bounds = form_rank_bounds(parent)
    mu = exact_mu(parent, node_budget)
    if target_family.lower() not in {"product-t", "t", "t-product"}:
        raise ValueError("currently supported target family: product-t")
    tau = tau_product_t(parent, max_width, node_budget)
    return {
        "n": parent.n,
        "ambient_check_rows": parent.ambient_rank,
        "check_rank": parent.check_rank,
        "distance_filter": parent.distance,
        "quadric_degeneracy": parent.quadric_degeneracy,
        "kappa": parent.kappa,
        "form_rank_bounds": bounds,
        "mu": mu,
        "tau": {"family": "product-t", **tau},
    }


# -------------------------------------------------------------- gate census
def _permute_frame(frame: Sequence[int], permutation: Sequence[int]) -> tuple[int, ...]:
    """Reindex so the row at old position ``i`` lands at ``permutation[i]``."""
    out = [0] * len(frame)
    for old, new in enumerate(permutation):
        out[new] = frame[old]
    return tuple(out)


def classify_gates(
    parent: Parent,
    kmax: int,
    dedup: str = "gl",
    node_budget: int | None = None,
    orbit_budget: int | None = None,
    active_only: bool = True,
) -> dict:
    """Enumerate compatible gates under ``gl`` or ``symmetric`` (S_k) dedup.

    Each compatible subspace is visited once.  Its possible output bases form
    the correct GL(k,2) orbit of the phase tensor.  A capped orbit or subspace
    walk marks the whole result partial.

    ``gl`` keys a record by the orbit-minimal gate key; a capped orbit is
    keyed apart under ``(k, "partial", ...)`` because a partial minimum is
    not an invariant.  ``symmetric`` records one witness per S_k class of
    orbit members.  With ``active_only`` a class whose gate leaves an output
    idle is skipped and recovered at its true width on a sub-subspace, so no
    active class is lost.  Every witness is re-verified (parity + distance)
    from raw columns before being recorded.
    """
    if dedup not in {"gl", "symmetric"}:
        raise ValueError("dedup must be 'gl' or 'symmetric'")
    records: dict[tuple, dict] = {}
    subspaces = 0
    complete = True
    try:
        for basis in compatible_subspaces(parent, kmax=kmax, node_budget=node_budget):
            if not basis:
                continue
            subspaces += 1
            k = len(basis)
            raw_gate = parent.gate(basis)
            orbit, orbit_complete = gl_orbit(k, raw_gate, orbit_budget)
            complete &= orbit_complete
            if dedup == "gl":
                active = [(gate, matrix) for gate, matrix in orbit.items()
                          if not active_only or covered_width(gate) == k]
                if not active:
                    continue
                # Orbit-wide minimum is the class key; the witness is the
                # minimal *active* member, which may differ from it.
                canonical = min(gate_key(gate) for gate in orbit)
                witness_gate, matrix = min(active, key=lambda item: gate_key(item[0]))
                transformed = transform_frame(basis, matrix)
                columns = parent.columns(transformed)
                parity_ok, distance = verify_columns(
                    columns, k, k + parent.ambient_rank, witness_gate,
                    max(4, parent.distance - 1),
                )
                if not parity_ok or (isinstance(distance, int) and distance < parent.distance):
                    raise AssertionError("GL-dedup gate witness failed independent verification")
                key = (k, canonical) if orbit_complete else (k, "partial", canonical)
                records.setdefault(
                    key,
                    {
                        "k": k,
                        "gate": gate_name(witness_gate),
                        "canonical_key": [list(q) for q in canonical],
                        "dedup": "GL(k,2)" if orbit_complete else "partial GL(k,2) orbit",
                        "orbit_complete": orbit_complete,
                        "distance": distance,
                        "wants": [list(q) for q in gate_key(witness_gate)],
                        "columns": columns,
                    },
                )
            else:
                for gate, matrix in orbit.items():
                    if active_only and covered_width(gate) != k:
                        continue
                    canonical, permutation = sk_canonical(k, gate)
                    transformed = transform_frame(basis, matrix)
                    transformed = _permute_frame(transformed, permutation)
                    canonical_gate = frozenset(frozenset(q) for q in canonical)
                    columns = parent.columns(transformed)
                    parity_ok, distance = verify_columns(
                        columns, k, k + parent.ambient_rank, canonical_gate,
                        max(4, parent.distance - 1),
                    )
                    if not parity_ok or (isinstance(distance, int) and distance < parent.distance):
                        raise AssertionError("S_k-dedup gate witness failed independent verification")
                    key = (k, canonical)
                    records.setdefault(
                        key,
                        {
                            "k": k,
                            "gate": gate_name(frozenset(frozenset(q) for q in canonical)),
                            "canonical_key": [list(q) for q in canonical],
                            "dedup": "S_k",
                            "orbit_complete": orbit_complete,
                            "distance": distance,
                            "wants": [list(q) for q in canonical],
                            "columns": columns,
                        },
                    )
    except SearchLimit:
        complete = False
    ordered = sorted(records.values(), key=lambda record: (record["k"], record["canonical_key"]))
    return {
        "n": parent.n,
        "check_rank": parent.check_rank,
        "distance_filter": parent.distance,
        "kappa": parent.kappa,
        "dedup": dedup,
        "complete": complete,
        "subspaces_visited": subspaces,
        "n_gates": len(ordered),
        "gates": ordered,
    }
