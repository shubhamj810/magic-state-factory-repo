"""Parser and integrity checks for the Gillot--Langevin orbit data.

The bundled ``B-0-3-7.dat`` file lists the 3,486 AGL(7,2) orbits of
``RM(3,7)``.  One published metadata value is known to be wrong: the final
nonconstant affine class reports the whole AGL group as its stabilizer.  Its
orbit has 254 elements, so the corrected stabilizer is ``|AGL(7,2)|/254``.
The defect is at weight 64 and does not affect the ``n <= 44`` census, but the
correction is applied when checking the global orbit-size certificate.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


VARIABLES = "abcdefgh"
_ROW_RE = re.compile(r"\[([01 ]+)\](\S*)")


def agl_order(dimension: int) -> int:
    """|AGL(d,2)| = 2^d * prod_{i<d} (2^d - 2^i)."""
    order = 1 << dimension
    for index in range(dimension):
        order *= (1 << dimension) - (1 << index)
    return order


def _bits_left_to_right(text: str) -> int:
    """'0110...' -> int with the LEFTMOST character as bit 0 (file convention)."""
    value = 0
    for index, char in enumerate(text):
        if char == "1":
            value |= 1 << index
    return value


def anf_truth_table(anf: str, dimension: int) -> int:
    """Truth table (bit x = f(x)) of an ANF like ``abc+de+1``; vars a..h are bits 0..7."""
    table = 0
    all_ones = (1 << (1 << dimension)) - 1
    for raw_term in anf.strip().split("+"):
        term = raw_term.strip()
        if not term or term == "0":
            continue
        if term == "1":
            table ^= all_ones
            continue
        mask = 0
        for variable in term:
            index = VARIABLES.index(variable)
            if index >= dimension:
                raise ValueError(f"variable {variable!r} is outside dimension {dimension}")
            mask |= 1 << index
        for point in range(1 << dimension):
            if point & mask == mask:
                table ^= 1 << point
    return table


def truth_table_degree(table: int, dimension: int) -> int:
    """Algebraic degree via the in-place Moebius transform; -1 for the zero function."""
    values = [(table >> point) & 1 for point in range(1 << dimension)]
    for bit in range(dimension):
        for point in range(1 << dimension):
            if (point >> bit) & 1:
                values[point] ^= values[point ^ (1 << bit)]
    return max((point.bit_count() for point, value in enumerate(values) if value), default=-1)


@dataclass(frozen=True)
class AffineMap:
    """AGL element ``x -> translation ^ XOR of images[i] over set bits i of x``."""

    images: tuple[int, ...]
    translation: int
    dimension: int

    def apply(self, point: int) -> int:
        image = self.translation
        for index in range(self.dimension):
            if (point >> index) & 1:
                image ^= self.images[index]
        return image

    def pullback(self, table: int) -> int:
        """Truth table of ``f o A``: bit x set iff ``table`` has bit A(x)."""
        result = 0
        for point in range(1 << self.dimension):
            if (table >> self.apply(point)) & 1:
                result |= 1 << point
        return result


@dataclass
class OrbitClass:
    """One parsed AGL(7,2) class: ANF representative, stabilizer, generators."""

    index: int
    anf: str
    table: int
    dimension: int
    reported_stabilizer: int = 0
    generators: list[AffineMap] = field(default_factory=list)

    @property
    def weight(self) -> int:
        return self.table.bit_count()

    @property
    def degree(self) -> int:
        return truth_table_degree(self.table, self.dimension)

    @property
    def stabilizer(self) -> int:
        """Reported stabilizer size, with the known final-class correction."""
        # The final `anf=a` class represents all 254 nonconstant affine
        # functions, rather than a singleton orbit.
        if (
            self.dimension == 7
            and self.anf == "a"
            and self.weight == 64
            and self.reported_stabilizer == agl_order(7)
        ):
            return agl_order(7) // 254
        return self.reported_stabilizer

    @property
    def metadata_corrected(self) -> bool:
        return self.stabilizer != self.reported_stabilizer


def parse_file(path: str | Path, dimension: int = 7) -> list[OrbitClass]:
    """Parse ``B-0-3-7.dat``: ``anf=``, ``stabSize=``, generator rows, footer.

    Strict: every line must be recognized, the footer class count must match,
    and every class must report a positive stabilizer.  The file is read as
    published; the one known metadata defect is corrected in memory by
    ``OrbitClass.stabilizer``.
    """
    classes: list[OrbitClass] = []
    current: OrbitClass | None = None
    footer_count = None
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, 1):
            line = raw.strip()
            if not line:
                continue
            if line.startswith("anf="):
                anf = line[4:]
                current = OrbitClass(
                    index=len(classes),
                    anf=anf,
                    table=anf_truth_table(anf, dimension),
                    dimension=dimension,
                )
                classes.append(current)
                continue
            if line.startswith("stabSize="):
                if current is None:
                    raise ValueError(f"{path}:{line_number}: stabilizer before ANF")
                current.reported_stabilizer = int(line.split("=", 1)[1])
                continue
            if line.startswith("#number of class"):
                footer_count = int(line.rsplit(" ", 1)[1])
                continue
            if line.startswith("#"):
                continue
            match = _ROW_RE.fullmatch(line)
            if match:
                if current is None:
                    raise ValueError(f"{path}:{line_number}: generator before ANF")
                rows = match.group(1).split()
                if len(rows) != dimension:
                    raise ValueError(
                        f"{path}:{line_number}: expected {dimension} generator rows"
                    )
                current.generators.append(
                    AffineMap(
                        tuple(_bits_left_to_right(row) for row in rows),
                        _bits_left_to_right(match.group(2)) if match.group(2) else 0,
                        dimension,
                    )
                )
                continue
            raise ValueError(f"{path}:{line_number}: unrecognized line {line[:80]!r}")
    if footer_count is not None and footer_count != len(classes):
        raise ValueError(f"footer says {footer_count} classes; parsed {len(classes)}")
    if any(orbit.reported_stabilizer <= 0 for orbit in classes):
        raise ValueError("one or more classes have no positive stabilizer size")
    return classes


def integrity_report(path: str | Path) -> dict:
    """The 2^64 certificate: corrected orbit sizes must sum to |RM(3,7)|.

    ``valid`` requires exactly 3,486 classes and orbit-size sum 2^64; any
    in-memory stabilizer corrections are listed explicitly.
    """
    classes = parse_file(path, 7)
    group_order = agl_order(7)
    orbit_sum = sum(group_order // orbit.stabilizer for orbit in classes)
    return {
        "classes": len(classes),
        "expected_classes": 3486,
        "max_degree": max(orbit.degree for orbit in classes),
        "orbit_size_sum": orbit_sum,
        "expected_orbit_size_sum": 2**64,
        "corrected_class_indices": [orbit.index for orbit in classes if orbit.metadata_corrected],
        "valid": len(classes) == 3486 and orbit_sum == 2**64,
    }


def origin_orbits(orbit: OrbitClass) -> list[list[int]]:
    """Safe origin representatives under listed generators fixing the word.

    Only generators whose pullback fixes the truth table contribute, so the
    union-find joins orbits of a subgroup of the true stabilizer.  The
    resulting partition can only be finer than the true one: 'reps' mode may
    audit a duplicate marking but can never miss one.
    """
    size = 1 << orbit.dimension
    parent = list(range(size))

    def find(value: int) -> int:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    for generator in orbit.generators:
        if generator.pullback(orbit.table) != orbit.table:
            continue
        for point in range(size):
            left, right = find(point), find(generator.apply(point))
            if left != right:
                parent[left] = right
    groups: dict[int, list[int]] = {}
    for point in range(size):
        groups.setdefault(find(point), []).append(point)
    return [sorted(group) for group in groups.values()]


def marked_points(orbit: OrbitClass, origin: int) -> tuple[int, ...]:
    """Support translated so ``origin`` maps to 0, which is then dropped.

    n = weight - 1 when ``origin`` lies in the support, else n = weight (no
    translated point can be 0 in that case).
    """
    return tuple(
        sorted(
            point ^ origin
            for point in range(1 << orbit.dimension)
            if ((orbit.table >> point) & 1) and point != origin
        )
    )
