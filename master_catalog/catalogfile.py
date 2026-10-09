#!/usr/bin/env python3
"""The catalogue's two files: reading them, writing them, and rendering one
from the other.

`master_catalog.json` is the catalogue.  `MASTER_CATALOG.md` is a VIEW of it --
generated here, never hand-edited, and byte-reproducible from the JSON alone, so
that "the Markdown says what the JSON says" is something a test can assert
rather than something a reader has to trust.

Nothing in this module verifies anything.  It is deliberately the dumbest layer
in the folder: `verify_catalog.py` decides whether a row may be published and
`merge_results.py` decides which circuit represents a class, and both of them
come here only to read and write.  Keeping the split means a rendering bug can
never be mistaken for a mathematical one.

THE ROW SCHEMA
--------------
A row is self-contained: every number it publishes is re-derivable from
``columns`` and ``k`` and nothing else.  `verify_catalog.py` does exactly that
re-derivation, so this list is also the list of things that get checked.

  ``n``          number of columns (pi/4 parity rotations)
  ``k``          output wires; they are ``0..k-1``, wires ``k..N-1`` are checks
  ``N``          ambient wires -- equal to the largest qubit index used, plus 1
  ``d``          verified fault distance: exact if ``d_is_exact``, else a FLOOR
  ``level``      3 throughout this catalogue (pi/4 rotations)
  ``columns``    the circuit: one qubit-support list per rotation
  ``gate``       the deposited output gate, as a monomial string
  ``gate_human`` the same gate as ``T``/``CS``/``CCZ`` factors
  ``sk_key``     the S_k canonical monomial set, or ``null`` when the ``k!``
                 minimisation was not proved (then ``sk_key_note`` says so).
                 It names the stored FRAME; the class is wider (see below)
  ``sk_canonical_frame``  whether the columns are shown in that canonical frame
  ``sk_fingerprint``      a permutation-invariant fingerprint of the gate
  ``d_is_exact``  ``true`` iff a clean sweep below ``d`` met a witness AT ``d``
  ``d_upper``     the weight of an explicit harmful fault, or ``null``
  ``d_witness``   that fault, as column indices
  ``t_count``     exact minimal level-3 T-count, or ``null`` with a note
  ``poly_degree`` CNOT-frame-reduced phase-polynomial degree, or ``null``
  ``effective_width``  rank of the output rows modulo the check span; ``== k``
  ``regimes``, ``discovery``, ``strongest_claim``, ``sources``
                 provenance.  INERT STRINGS: they record where a class came
                 from, and no code here opens any path they name.  Several of
                 them point into source directories this folder no longer has.
  ``relabelled_into_canonical_frame``  whether the columns were permuted on the
                 way in, so a reader can tell the frame apart from the original
  ``catalog_label``  the row's permanent public name, ``n.k.d.x`` -- for
                 example ``15.1.3.a`` -- with ``d`` the distance proved here and
                 ``x`` a letter code numbering the classes at that ``(n, k, d)``
                 in the order they entered the catalogue (``a`` .. ``z``, then
                 ``ba``, ``bb``, ... as LMFDB does).  Assigned once by
                 `merge_results.py`, never changed by an improvement, never
                 reused; `verify_catalog.label_problems` checks the format and
                 the uniqueness.  It is identity, not data: nothing about the
                 circuit follows from it
  ``citations``  the works this class is credited to, as keys of the header's
                 ``references`` map.  Provenance like ``sources``: the keys must
                 resolve, and nothing about the circuit follows from them

THE CLASS
---------
One row per ``(n, k, d, GL(k,2) class of the gate)``: two circuits with the same
``n``, ``k`` and distance whose gates agree after an invertible change of the
output basis (a CNOT frame) and diagonal Clifford corrections are the same
entry, decided by `glcanon.gl_isomorphic`.  A circuit at another distance is
another row.  The stored circuit is one representative and ``gate``
is what IT deposits; the ``S_k`` fields describe that frame.
"""
from __future__ import annotations

import json
import os
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOG_JSON = HERE / "master_catalog.json"
CATALOG_MD = HERE / "MASTER_CATALOG.md"

#: MASTER_CATALOG.md inlines a circuit's columns only when a person could read
#: them; the JSON always carries all of them.
INLINE_COLUMNS = 200

#: Fields every row must carry.  A row missing one of these is not a row this
#: catalogue can publish: the whole design is that a row is self-contained, and
#: a consumer reading `row["d_is_exact"]` must never get a `KeyError` instead of
#: an answer.
REQUIRED_FIELDS = (
    "n", "k", "N", "d", "level", "columns", "gate", "gate_human",
    "sk_key", "sk_canonical_frame", "sk_fingerprint",
    "d_is_exact", "d_upper", "d_witness",
    "t_count", "poly_degree", "effective_width",
    "regimes", "discovery", "strongest_claim",
    # ``relabelled_into_canonical_frame`` is PROVENANCE: whether the ingest
    # permuted the output wires on the way in.  A self-contained row cannot
    # prove or refute it -- the source frame is not stored -- so the verifier
    # checks its TYPE and nothing else, exactly as it treats ``sources``.  It
    # stays required because a consumer reading it must get an answer rather
    # than a KeyError, but nothing in this folder ever computes with it.
    "relabelled_into_canonical_frame", "sources",
    # ``citations`` is provenance too: keys into the header's ``references``
    # map, checked to resolve by `verify_catalog.citation_problems` and never
    # computed with.
    "citations",
    # ``catalog_label`` is the row's permanent public name (see the schema
    # above).  Required, so every published row can be cited by it.
    "catalog_label",
)

#: Fields a row may carry.  Anything outside the two tuples is a field nobody
#: documented, which is how a stale value survives a refactor.
#: ``d_certified``, ``d_certified_is_exact`` and ``d_certified_source`` carry
#: a distance a SOURCE certifies that this folder could not re-measure, which
#: happens at the lengths where the sweep below ``d`` is out of reach.  The
#: certificate is either an exact value or itself only a lower bound, and
#: ``d_certified_is_exact`` says which, exactly as ``d_is_exact`` does for
#: ``d``.  They never replace ``d``: ``d`` stays what was proved here, and a
#: consumer that wants only what this folder proved can ignore all three.
#: `verify_catalog.certificate_problems` checks that they come together and
#: that a certificate says more than, and nothing against, what was proved.
OPTIONAL_FIELDS = ("sk_key_note", "t_count_note", "poly_degree_note",
                   "columns_note", "dedup_note",
                   "d_certified", "d_certified_is_exact", "d_certified_source")

#: The JSON TYPE every documented field must have, as a small grammar:
#: ``"int"``, ``"str"``, ``"bool"``, ``"dict"``, ``"int?"`` for "that or null",
#: and ``[inner]`` for a list of ``inner``.
#:
#: This exists because Python's ``==`` and its notion of truth both cross type
#: boundaries where JSON does not, and a verifier that compares before it types
#: is generous in exactly the places nobody looks:
#:
#:   * ``True == 1``, so a row publishing ``"t_count": true`` compares EQUAL to
#:     a recomputed T-count of 1 and sails through;
#:   * ``if row["d_is_exact"]`` is true for ``"garbage"``, ``[0]`` and
#:     ``2**63``, so a floor could be published as exact by any value that is
#:     not a boolean at all;
#:   * ``False == 0``, so a canonical key's leading ``0`` may be written as
#:     ``false`` and still match.
#:
#: None of those is a plausible typo, and all three are what a corrupted or
#: hand-edited file looks like.  Typing the row first turns each of them into a
#: named rejection instead of a silent agreement.  ``bool`` is deliberately NOT
#: a subtype of ``int`` here, which is the whole point.
FIELD_TYPES = {
    "n": "int", "k": "int", "N": "int", "d": "int", "level": "int",
    "effective_width": "int",
    "t_count": "int?", "poly_degree": "int?", "d_upper": "int?",
    "gate": "str", "gate_human": "str", "sk_fingerprint": "str",
    "discovery": "str", "strongest_claim": "str",
    "sk_key_note": "str", "t_count_note": "str", "poly_degree_note": "str",
    "columns_note": "str", "dedup_note": "str",
    "d_certified": "int", "d_certified_is_exact": "bool",
    "d_certified_source": "str",
    "d_is_exact": "bool", "sk_canonical_frame": "bool",
    "relabelled_into_canonical_frame": "bool",
    "columns": [["int"]], "sk_key": [["int"]],
    "d_witness": ["int"], "regimes": ["str"], "sources": ["dict"],
    "citations": ["str"], "catalog_label": "str",
}


# ------------------------------------------------------------------ labels
#: ``n.k.d.x``: the parameters, then a lowercase letter code.
LABEL_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)\.([a-z]+)$")


def label_letters(index: int) -> str:
    """``0 -> a``, ``25 -> z``, ``26 -> ba``: base 26 with ``a`` as zero, as LMFDB
    numbers isogeny classes, so the code for an index is unique and short."""
    if index < 0:
        raise ValueError("a label index is never negative")
    letters = ""
    while True:
        letters = chr(ord("a") + index % 26) + letters
        index //= 26
        if index == 0:
            return letters


def label_index(letters: str) -> int:
    """The inverse of `label_letters`."""
    value = 0
    for ch in letters:
        value = value * 26 + (ord(ch) - ord("a"))
    return value


def next_label(rows, n: int, k: int, d: int) -> str:
    """The first unused label at ``(n, k, d)``: one past the highest in use.

    Rows are never deleted, so "one past the highest" is also "never used
    before" -- a label, once given, is not handed out again.
    """
    used = [label_index(m.group(4)) for row in rows
            for m in [LABEL_RE.match(str(row.get("catalog_label", "")))]
            if m and (int(m.group(1)), int(m.group(2)), int(m.group(3))) == (n, k, d)]
    return f"{n}.{k}.{d}.{label_letters(max(used) + 1 if used else 0)}"
#: Fields whose value may be ``null`` INSTEAD of the shape above: a row with no
#: proved canonical frame stores no key, and a row whose distance search found
#: no fault at all stores no witness.
NULLABLE_FIELDS = ("sk_key", "d_witness")

#: The keys every entry of ``sources`` carries, and their types.  ``sources``
#: itself is typed only as a list of objects by `FIELD_TYPES`, which admits
#: ``[{}]`` -- and `render_markdown` then reads ``source["regime"]`` and three
#: siblings unconditionally, so an entry the outer grammar accepted could crash
#: the renderer after every mathematical check had passed.  The inner keys are
#: provenance and prove nothing about the circuit, but the same standard
#: applies to them as to every other published field: typed first, so a broken
#: one is a named rejection and not a KeyError three tools later.
SOURCE_FIELD_TYPES = {
    "regime": "str", "label": "str", "file": "str",
    "N": "int", "d": "int", "d_is_exact": "bool",
    # Null where the ingest had nothing to record: `merge_results` writes what
    # a submitted record carries, and a record owes no campaign name and no
    # file-and-line.  The renderer already reads them that way -- it prints
    # ``provenance or file``.
    "origin": "str?", "provenance": "str?",
}
#: ``notes`` is the one optional key, and the shipped file carries it in two
#: historical shapes -- one string, or a list of strings -- so it is checked by
#: hand in `_source_entry_problem` rather than through the grammar.
SOURCE_OPTIONAL_FIELDS = ("notes",)


def _source_entry_problem(entry):
    """``None`` if one ``sources`` entry is well-formed, else a phrase."""
    missing = [name for name in SOURCE_FIELD_TYPES if name not in entry]
    if missing:
        return f"missing {', '.join(missing)}"
    unknown = [name for name in entry
               if name not in SOURCE_FIELD_TYPES
               and name not in SOURCE_OPTIONAL_FIELDS]
    if unknown:
        return f"carrying undocumented key(s) {', '.join(sorted(unknown))}"
    for name, shape in SOURCE_FIELD_TYPES.items():
        wrong = _shape_problem(entry[name], shape)
        if wrong is not None:
            return f"storing {name} as {wrong}"
    notes = entry.get("notes")
    if notes is not None and not isinstance(notes, str) and not (
            isinstance(notes, list)
            and all(isinstance(line, str) for line in notes)):
        return f"storing notes as {_name_of(notes)}"
    return None


def type_problems(row):
    """Every documented field of ``row`` whose JSON type is wrong.

    Returns a list of ``(kind, detail)`` pairs, the shape the verifier collects
    problems in.  Fields the row does not carry are not reported here -- that
    is the missing/undocumented check's job -- so this can be run on a row that
    has already failed it without producing two complaints about one field.
    """
    problems = []
    for name, shape in FIELD_TYPES.items():
        if name not in row:
            continue
        value = row[name]
        if value is None and name in NULLABLE_FIELDS:
            continue
        wrong = _shape_problem(value, shape)
        if wrong is not None:
            problems.append(("field-type",
                             f"{name} is {wrong}, and this catalogue publishes "
                             f"it as {_describe_shape(shape)}"))
    sources = row.get("sources")
    if isinstance(sources, list):
        for position, entry in enumerate(sources):
            if not isinstance(entry, dict):
                continue                   # the grammar above already said so
            wrong = _source_entry_problem(entry)
            if wrong is not None:
                problems.append(("field-type",
                                 f"sources[{position}] is {wrong}"))
    return problems


def _shape_problem(value, shape):
    """``None`` if ``value`` has ``shape``, else a phrase describing what it is."""
    if isinstance(shape, list):
        if not isinstance(value, list):
            return _name_of(value)
        for element in value:
            wrong = _shape_problem(element, shape[0])
            if wrong is not None:
                return f"a list containing {wrong}"
        return None
    if shape.endswith("?"):
        return None if value is None else _shape_problem(value, shape[:-1])
    if shape == "bool":
        return None if isinstance(value, bool) else _name_of(value)
    if shape == "int":
        # `isinstance(True, int)` is True in Python and false in JSON.
        return None if isinstance(value, int) and not isinstance(value, bool) \
            else _name_of(value)
    if shape == "str":
        return None if isinstance(value, str) else _name_of(value)
    if shape == "dict":
        return None if isinstance(value, dict) else _name_of(value)
    raise ValueError(f"unknown field shape {shape!r}")


def _name_of(value):
    if isinstance(value, bool):
        return f"the boolean {str(value).lower()}"
    if value is None:
        return "null"
    return f"a {type(value).__name__} ({value!r})"[:80]


def _describe_shape(shape):
    if isinstance(shape, list):
        return f"a list of {_describe_shape(shape[0])}"
    return {"int": "a whole number", "int?": "a whole number or null",
            "str": "a string", "bool": "a boolean",
            "dict": "an object"}[shape]

#: The header this folder writes onto a rebuilt catalogue.  It travels with the
#: rows so that `MASTER_CATALOG.md` and any later consumer can read the meaning
#: of `regimes` and `discovery` out of the file itself rather than out of a
#: script that may no longer exist.
HEADER_KEYS = ("scope", "dedup_key", "regimes", "discovery", "caveat",
               "verification", "references")

#: The shape of one ``references`` entry: a short in-table label and the full
#: bibliographic line printed under "References" -- both required -- and, for a
#: published work, the ``url`` of its DOI or arXiv page, which the table links
#: the label to, and its ``date`` of publication, ``YYYY-MM`` or ``YYYY-MM-DD``:
#: the journal's (Crossref's) for an article, the arXiv v1 date for a preprint.
#: The date orders the reference lists; its year is the one ``short`` prints.
#: Unpublished works carry neither.
REFERENCE_FIELDS = ("short", "full")
REFERENCE_OPTIONAL = ("url", "date")
REFERENCE_DATE = re.compile(r"(\d{4})-(0[1-9]|1[0-2])(-(0[1-9]|[12]\d|3[01]))?")
REFERENCE_YEAR = re.compile(r"\((\d{4})\)")


def reference_order(references: dict) -> list[str]:
    """The reference keys, oldest publication first.

    By ``date`` where an entry has one, else by the year its ``short`` label
    prints; an entry with neither (an unpublished work) goes last.  Ties keep
    the key order, so the result is deterministic.
    """
    def when(key):
        entry = references[key]
        if entry.get("date"):
            return entry["date"]
        year = REFERENCE_YEAR.search(entry.get("short", ""))
        return year.group(1) if year else "9999"
    return sorted(references, key=lambda key: (when(key), key))


# --------------------------------------------------------------------- reading
def load(path: Path | str = CATALOG_JSON) -> dict:
    """The whole catalogue payload: header metadata plus ``factories``."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(
            payload.get("factories"), list):
        raise ValueError(f"{path}: not a catalogue payload "
                         f"(no 'factories' list)")
    return payload


def rows(path: Path | str = CATALOG_JSON) -> list[dict]:
    """Just the rows, for callers that do not care about the header."""
    return load(path)["factories"]


# --------------------------------------------------------------------- writing
def serialise(payload: dict) -> str:
    """``indent=1``, except that a list of bare integers stays on one line.

    A circuit's columns are lists of qubit indices, and at ``n = 1023`` writing
    each index on its own line takes the file from 9 MB to 19 MB of mostly
    whitespace.  Collapsing only the innermost integer lists keeps every other
    field as readable as it was, and `json.loads` on the result is equal to the
    payload -- which `tests/` asserts, since a formatter that quietly corrupted
    the columns would be the worst possible bug in this folder.
    """
    text = json.dumps(payload, indent=1)
    # The whitespace right after ``[`` must contain a NEWLINE.  That is what
    # anchors the pattern to a real JSON array: ``json.dumps`` never puts a raw
    # newline inside a string, so a bracketed number in a label or a note --
    # ``"iteration [ 12 ] of the search"`` -- can never match, where the
    # newline-less ``\[\s+...`` this replaces matched it and silently
    # rewrote the STRING to ``[12]``.  A formatter that edits payload content
    # is the worst possible bug in this folder, which is why the round-trip
    # equality below it is asserted in `tests/`.
    return re.sub(r"\[\s*\n\s*((?:\d+,\s+)*\d+)\s+\]",
                  lambda m: "[" + re.sub(r"\s+", " ", m.group(1)) + "]",
                  text) + "\n"


def write(payload: dict, json_path: Path | str = CATALOG_JSON,
          md_path: Path | str = CATALOG_MD) -> None:
    """Write both files from one payload, so they cannot drift apart.

    Both are RENDERED before either is written, and each is written to a
    temporary file beside its destination and then renamed.  The plain
    ``write_text`` pair this replaces truncated the JSON, wrote it, and only
    then rendered the Markdown -- so a renderer that raised left an updated
    catalogue beside a stale page, which is precisely the drift the docstring
    promises cannot happen, and an interrupted write left the catalogue itself
    truncated.  ``os.replace`` is atomic within a filesystem, so a reader sees
    either the old file or the new one.
    """
    json_path, md_path = Path(json_path), Path(md_path)
    if json_path.resolve() == md_path.resolve():
        # Otherwise the Markdown silently overwrites the catalogue it was
        # rendered from, exit status 0, recoverable only from version control.
        raise ValueError(f"the catalogue and its rendered page cannot be the "
                         f"same file ({json_path})")
    body, page = serialise(payload), render_markdown(payload)
    for path, text in ((json_path, body), (md_path, page)):
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, path)


# ------------------------------------------------------------------- rendering
def render_markdown(payload: dict) -> str:
    """`MASTER_CATALOG.md`, from the payload and nothing else.

    Deterministic by construction: every number below is counted off the rows
    in the order the JSON stores them, and the regime table is read out of the
    payload header rather than out of a table of sources this folder no longer
    keeps.  So regenerating from an unchanged JSON reproduces the shipped file
    byte for byte, which is one of the things `tests/` checks.
    """
    lines: list[str] = []
    A = lines.append
    rows_ = payload["factories"]
    regimes = payload.get("regimes", {})
    by_k = Counter(r["k"] for r in rows_)
    by_d = Counter(r["d"] for r in rows_)
    by_discovery = Counter(r["discovery"] for r in rows_)
    tmax = max((r["t_count"] for r in rows_ if r["t_count"] is not None),
               default=0)

    A("# Master catalogue — every level-3, distance ≥ 2 factory")
    A("")
    A("Generated from [`master_catalog.json`](master_catalog.json) by")
    A("[`catalogfile.py`](catalogfile.py) — **do not edit by hand**; edit")
    A("nothing here, run [`merge_results.py`](merge_results.py) instead.")
    A("Every row is re-checked against its own columns by")
    A("[`verify_catalog.py`](verify_catalog.py).")
    A("")
    A(f"**{len(rows_)} distinct `(n, k, d, GL(k,2) gate)` classes**, every one with an")
    A("explicit circuit whose gate, check parities, distance, output width,")
    A("freedom from spectator and pseudo-outputs, freedom from check wires")
    A("that carry no syndrome bit of their own, and — where those are")
    A("computable — exact T-count and reduced degree are re-derived from its")
    A("columns.")
    A("")
    A("## What this table is, and is not")
    A("")
    A("It is the union of what the repository knows, on one page. It is **not** a")
    A("uniform claim: a row's regime says how its class was found and keeps")
    A("that claim, because a Pareto point of a classification and a search")
    A("witness are different kinds of statement.")
    A("")
    A("| regime | what a row from it means |")
    A("|---|---|")
    for regime, strength in regimes.items():
        count = sum(1 for r in rows_ if regime in r["regimes"])
        A(f"| `{regime}` ({count} rows) | {strength} |")
    A("")
    A("A **class** is `(n, k, d, gate)` with the gate taken up to an invertible")
    A("change of the output basis (a CNOT frame, `GL(k,2)`) and diagonal Clifford")
    A("corrections — the CNOT+S output equivalence. Circuits at the same")
    A("distance whose gates differ only by such a frame, for example `T0·T1` and")
    A("`T0·CS01`, are one row; circuits at different distances are always")
    A("different rows. The stored circuit is one representative, and `gate` is")
    A("exactly what it deposits.")
    A("")
    A("A class found in more than one corpus, or in more than one frame, is **one")
    A("row** here, with every contributing source listed in its `sources` field;")
    A("the retained circuit is the one with the fewest ambient qubits. `regimes`")
    A("therefore tells you the strongest claim available for that class.")
    A("")
    A("`discovery` says whether a class is **found only by AI search**: "
      f"**{by_discovery['AI search']}** rows are")
    A("`AI search` — found only by AI search campaigns — and "
      f"**{by_discovery['pre-existing']}** are")
    A("`pre-existing` — a classification stage run in this repository, the")
    A("symmetry-SAT search, the borrowed-identity searches or a community")
    A("contribution has them, or the length-54 classification alone does. A")
    A("class both an AI search and the length-54")
    A("classification found is `AI search`. Whether a class was new to the")
    A("literature is what `citation` says, not `discovery`.")
    A("")
    A("Level-2 and level-4 circuits are outside this table by definition: they")
    A("use a different rotation angle. So are distance-1 circuits, which detect")
    A("no single fault, and padded circuits — a `k` that counts an output the")
    A("gate never touches, or two outputs that are the same logical qubit modulo")
    A("the check span. `merge_results.py` rejects all four with the reason")
    A("printed, and `verify_catalog.py` would reject any that ever got in.")
    A("Distance-2 rows are in: the length-54 classification covers `d ≥ 3`")
    A("only, so its claims, and the `exhaustive classification` regimes, say")
    A("nothing about them.")
    A("")
    A("## Summary")
    A("")
    A("- output widths: " + ", ".join(f"`k={k}`: {by_k[k]}" for k in sorted(by_k)))
    A("- distances: " + ", ".join(f"`d={d}`: {by_d[d]}" for d in sorted(by_d))
      + f" ({sum(1 for r in rows_ if r['d_is_exact'])} pinned exactly, the rest "
        f"proved floors)")
    A(f"- exact minimal T-count reaches **{tmax}** "
      f"({sum(1 for r in rows_ if r['t_count'] is None)} rows are too wide for "
      f"it to be computed)")
    # An empty catalogue is a legitimate payload -- it is what a merge starts
    # from when a fresh collection is being built, and `tests/` merges into one
    # -- so the summary has to describe zero rows rather than raise on them.
    A(f"- injection counts from `n={min((r['n'] for r in rows_), default=0)}` "
      f"to `n={max((r['n'] for r in rows_), default=0)}`")
    A("")
    A("`T` is the exact minimal level-3 T-count (Amy–Mosca / Reed–Muller")
    A("minimum-weight `Z_8` coset); `deg` is the CNOT-frame-reduced")
    A("phase-polynomial degree. Both are exact minimisations over groups that")
    A("stop being finite in practice past `k = 6`, so above that they are blank")
    A("rather than estimated. A `d` marked `≥` is a proved floor, not a")
    A("measured distance. `cert d` is a distance the row's source certifies")
    A("where this folder could only prove the floor; it is not re-measured")
    A("here, and a `≥` there means the source certifies only a lower bound.")
    A("")
    references = payload.get("references") or {}

    def cite(row):
        labels = []
        for key in row.get("citations", []):
            entry = references.get(key)
            if entry is None:
                labels.append(key)
            elif entry.get("url"):
                labels.append(f"[{entry['short']}]({entry['url']})")
            else:
                labels.append(entry["short"])
        return "; ".join(labels)

    A("`citation` names the papers that credit the class. A class in the")
    A("published literature is credited to the earliest work that published it,")
    A("linked; a class the Borrowed Identities searches (Singh, Gidney and Jones)")
    A("were the first to publish, to that paper; a class a community")
    A("contribution brought, to its contributor's work; every other class, to")
    A("the length-54 classification and/or the symmetry-and-AI report. Full")
    A("entries are under [References](#references).")
    A("")
    A("| # | label | `[[n,k,d]]` | cert d | N | gate | T | deg | discovery | "
      "regime(s) | citation |")
    A("|---:|---|---|---:|---:|---|---:|---:|---|---|---|")
    for index, row in enumerate(rows_, 1):
        t = "—" if row["t_count"] is None else row["t_count"]
        degree = "—" if row["poly_degree"] is None else row["poly_degree"]
        d = row["d"] if row["d_is_exact"] else f"≥{row['d']}"
        gate = row["gate"] if len(row["gate"]) <= 40 else row["gate"][:37] + "…"
        cert = ("—" if row.get("d_certified") is None
                else row["d_certified"] if row.get("d_certified_is_exact")
                else f"≥{row['d_certified']}")
        A(f"| {index} | `{row['catalog_label']}` | `[[{row['n']},{row['k']},{d}]]` | {cert} | "
          f"{row['N']} | "
          f"`{gate}` | {t} | {degree} | {row['discovery']} | "
          f"{'; '.join(row['regimes'])} | {cite(row)} |")
    A("")
    A("## Circuits")
    A("")
    A("Columns are the qubit supports of each parity-`T` rotation; qubits")
    A("`0..k-1` are the outputs, the rest are postselected checks. Every circuit")
    A("is stored in its `S_k`-canonical output frame, so these columns deposit")
    A("exactly the `gate` shown — the rows too wide to canonicalise say so.")
    A("")
    A(f"Circuits with more than {INLINE_COLUMNS} columns are **not** printed")
    A("here: a thousand-column list is not something a reader reads, and")
    A("inlining them would triple this file to no purpose. They are complete in")
    A("[`master_catalog.json`](master_catalog.json), which is the machine-")
    A("readable copy of exactly these rows.")
    A("")
    for index, row in enumerate(rows_, 1):
        d = row["d"] if row["d_is_exact"] else f"≥{row['d']}"
        A(f"### {index}. `[[{row['n']},{row['k']},{d}]]` — {row['gate_human']}")
        A("")
        A(f"- output gate: `{row['gate']}`")
        A(f"- `N = {row['N']}` ({row['k']} output"
          f"{'' if row['k'] == 1 else 's'} + {row['N'] - row['k']} check"
          f"{'' if row['N'] - row['k'] == 1 else 's'})"
          + (f", exact minimal T-count {row['t_count']}"
             if row["t_count"] is not None else "")
          + (f", reduced degree {row['poly_degree']}"
             if row["poly_degree"] is not None else ""))
        if row["d_is_exact"] and row["d_witness"]:
            A(f"- distance: exactly {row['d']}, witnessed by the fault on "
              f"columns {row['d_witness']}")
        elif row["d_witness"]:
            A(f"- distance: proved `{row['d']} <= d <= {row['d_upper']}`; the "
              f"upper bound is the fault on columns {row['d_witness']}")
        else:
            A(f"- distance: proved `d >= {row['d']}`")
        if row.get("d_certified") is not None:
            relation = "=" if row.get("d_certified_is_exact") else ">="
            A(f"- certified distance: `d {relation} {row['d_certified']}`, "
              f"from {row['d_certified_source']}; not re-measured here")
        A(f"- discovery: {row['discovery']}")
        A(f"- regime: {'; '.join(row['regimes'])} — {row['strongest_claim']}")
        A(f"- citation: {cite(row)}")
        for source in row["sources"]:
            A(f"- source: `{source['regime']}` · {source['label']} "
              f"(`{source['provenance'] or source['file']}`)")
        # Labelled by the field each one explains.  ``t_count_note`` and
        # ``poly_degree_note`` carry the same sentence on every row above
        # ``METRICS_K_CAP`` -- both numbers die on the same group -- and printed
        # as two bare "note:" lines they read as an accidental repetition
        # rather than as two fields that happen to agree.
        for name, label in (("sk_key_note", "S_k key"),
                            ("t_count_note", "T-count"),
                            ("poly_degree_note", "reduced degree"),
                            ("columns_note", "circuit"),
                            ("dedup_note", "dedup")):
            if name in row:
                A(f"- note ({label}): {row[name]}")
        A("")
        if row["n"] <= INLINE_COLUMNS:
            A("```text")
            A("[" + ", ".join("{" + ",".join(map(str, c)) + "}"
                              for c in row["columns"]) + "]")
            A("```")
        else:
            # ``index`` numbers the sections of this file from 1; the JSON is
            # an array indexed from 0.  Spelling the pointer as a subscript
            # says which of the two "237" means -- "factory 237" under a
            # heading that reads "### 238." sends the reader to the wrong row.
            A(f"- {row['n']} columns — see `master_catalog.json`, "
              f"`factories[{index - 1}]`")
        A("")
    A("## References")
    A("")
    A("In order of publication.")
    A("")
    for key in reference_order(references):
        entry = references[key]
        count = sum(1 for r in rows_ if key in r.get("citations", []))
        link = f" <{entry['url']}>" if entry.get("url") else ""
        A(f"- <a id=\"ref-{key}\"></a>**{entry['short']}** (`{key}`, "
          f"{count} rows) — {entry['full']}{link}")
    A("")
    return "\n".join(lines)
