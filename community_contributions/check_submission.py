#!/usr/bin/env python3
"""Check a community contribution's catalogue input file, and merge it.

    python community_contributions/check_submission.py INPUT.json
    python community_contributions/check_submission.py INPUT.json --catalog PATH
    python community_contributions/check_submission.py INPUT.json --write   # maintainers

Contributors send protocols in any format.  The maintainers convert each
submission into ONE JSON catalogue input file, kept in the submission's folder
under ``submissions/``: who contributed it, the work it is credited to, how the
protocols were found, the terms the data may be redistributed under, and the
protocols as explicit circuits (the format is in ``README.md`` beside this
file).  This tool

1.  validates that file -- every field known, typed and filled in -- and
    converts each protocol into a `master_catalog/merge_results.py` record,
    setting the provenance fields itself (a contributor cannot choose a regime,
    a discovery tag or a citation);
2.  loads the catalogue and works on a COPY of it: registers the submission's
    reference in the copy's ``references`` map, then calls
    `merge_results.merge`, which verifies every protocol to exactly the bar a
    shipped row is held to and files it as accepted / improved / duplicate /
    rejected.  Only an ACCEPTED protocol -- a class the catalogue did not have
    -- is credited to the submission's reference; a class already held keeps
    the credit it had;
3.  runs the catalogue's file-level checks on the merged copy, refuses a
    circuit the length-54 classification says cannot exist (one that improves a
    Pareto point, or a new or improved class with ``n <= 54`` that no Pareto
    point strictly dominates), and prints a report.

Nothing is written unless ``--write`` is given, and ``--write`` writes nothing
unless every protocol verified and the merged catalogue passes the file-level
checks.  ``--write`` into the master catalogue itself also requires the
submission to live under ``community_contributions/submissions/``, so the
source entry every merged row carries names a file the repository holds.

Exit status: 0 every protocol verified (whatever its verdict), 1 a protocol was
rejected or the merged catalogue failed a check, 2 the submission itself is
malformed or the catalogue cannot be read (nothing was merged).
"""
from __future__ import annotations

import argparse
import itertools
import json
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SUBMISSIONS = HERE / "submissions"
sys.path.insert(0, str(REPO / "master_catalog"))

import catalogfile as CF                                          # noqa: E402
import glcanon as GC                                              # noqa: E402
import merge_results as MR                                        # noqa: E402
import verify_catalog as VC                                       # noqa: E402

#: What the tool sets on every record.  The regime is registered at the END of
#: the header's order (the weakest claim) the first time one is merged, with
#: STRENGTH as its sentence; once the header has it, the header's own sentence
#: stands, so rewording it there does not start rejecting contributions.
REGIME = "community contribution"
STRENGTH = ("contributed by an outside author and verified here from its "
            "explicit columns; a verified witness, not a maximum")
#: Not an AI discovery of this project: the header's glossary lists a community
#: contribution among the finders that make a class ``pre-existing``.
DISCOVERY = "pre-existing"
#: The master catalogue's regime for the length-54 classification's Pareto
#: points.  A contributed circuit that IMPROVES one would contradict that
#: classification, so the check refuses to write it and says why.
PARETO = "exhaustive classification n<=54 (Pareto point)"

TOP_FIELDS = ("contributor", "reference", "method", "terms", "protocols")
CONTRIBUTOR_REQUIRED, CONTRIBUTOR_OPTIONAL = ("name",), ("affiliation", "contact")
REFERENCE_REQUIRED, REFERENCE_OPTIONAL = ("key", "short", "full"), ("url", "date")
COLUMNS_FORM = ("k", "N", "columns")
MATRIX_FORM = ("generator_matrix_rows", "q")
PROTOCOL_OPTIONAL = ("n", "d", "gate", "label", "notes")
#: Record fields `merge_results` accepts that only this tool may set.
TOOL_SET = ("regime", "strength", "discovery", "citations", "provenance",
            "origin", "file")

REFERENCE_KEY = re.compile(r"[a-z][a-z0-9_-]{2,63}")
#: `<...>` is how TEMPLATE.json marks a value to replace.
PLACEHOLDER = re.compile(r"\s*<.*>\s*", re.S)
METHOD_MAX = 400
#: Strings the rendered MASTER_CATALOG.md prints inside code spans, tables and
#: link text, where these characters break the page: backticks, pipes, angle
#: brackets (raw HTML), and every control, format (bidi overrides, zero-width),
#: line- or paragraph-separator character.
UNPRINTABLE = re.compile(r"[`|<>]")
UNPRINTABLE_CATEGORIES = ("Cc", "Cf", "Zl", "Zp")
#: Lengths of the strings the catalogue prints on every row that cites them.
SHORT_MAX, FULL_MAX, LABEL_MAX = 80, 400, 80


def _unprintable(value, angles=False):
    """``angles``: '<' and '>' are harmless in text printed only inside a code
    span (``method``, which reaches the page inside the provenance span)."""
    found = set(UNPRINTABLE.findall(value))
    if angles:
        found -= {"<", ">"}
    return bool(found) or any(
        unicodedata.category(ch) in UNPRINTABLE_CATEGORIES for ch in value)


class SubmissionError(ValueError):
    """The submission is malformed; ``problems`` says every way it is."""

    def __init__(self, problems):
        super().__init__("; ".join(problems))
        self.problems = list(problems)


# ------------------------------------------------------------------- reading
def load_submission(path):
    """The submission object in ``path``, or `SubmissionError`."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as error:
        raise SubmissionError([f"cannot read {path}: {error.strerror}"]) from None
    try:
        submission = json.loads(text)
    except json.JSONDecodeError as error:
        raise SubmissionError([f"{path} is not valid JSON ({error})"]) from None
    if not isinstance(submission, dict):
        raise SubmissionError([f"{path} holds a {type(submission).__name__}, "
                               f"not one submission object"])
    return submission


def _integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _fields(obj, where, required, optional, problems, forbidden=()):
    """Required fields present, nothing undocumented; False if not an object."""
    if not isinstance(obj, dict):
        problems.append(f"{where} must be an object, not a "
                        f"{type(obj).__name__}")
        return False
    missing = [name for name in required if name not in obj]
    if missing:
        problems.append(f"{where} is missing {', '.join(missing)}")
    for name in obj:
        if name in forbidden:
            problems.append(f"{where}.{name} is set by check_submission.py, "
                            f"not by the contributor; delete it")
        elif name not in required and name not in optional:
            problems.append(f"{where}.{name} is not a field of the submission "
                            f"format (see community_contributions/README.md)")
    return True


def _text(obj, name, where, problems, printable=True, limit=None,
          angles=False):
    """A present field is a filled-in string."""
    if name not in obj:
        return
    value = obj[name]
    if not isinstance(value, str) or not value.strip():
        problems.append(f"{where}.{name} must be a non-empty string")
    elif PLACEHOLDER.fullmatch(value):
        problems.append(f"{where}.{name} still holds the template placeholder "
                        f"{value!r}")
    elif printable and _unprintable(value, angles):
        problems.append(f"{where}.{name} contains a line break, tab, control "
                        f"or invisible formatting character, backtick, '|', "
                        f"'<' or '>', which the rendered catalogue cannot "
                        f"print safely")
    elif limit is not None and len(value) > limit:
        problems.append(f"{where}.{name} is {len(value)} characters; keep it "
                        f"to {limit} and put the detail in the reference")


def _protocol_problems(protocol, where):
    problems = []
    if not isinstance(protocol, dict):
        return [f"{where} must be an object, not a {type(protocol).__name__}"]
    has_columns = any(name in protocol for name in COLUMNS_FORM)
    has_matrix = any(name in protocol for name in MATRIX_FORM)
    if has_columns and has_matrix:
        return [f"{where} mixes the two circuit forms: give EITHER k, N and "
                f"columns OR generator_matrix_rows and q"]
    if not has_columns and not has_matrix:
        return [f"{where} has no circuit: give either k, N and columns or "
                f"generator_matrix_rows and q"]
    form = COLUMNS_FORM if has_columns else MATRIX_FORM
    _fields(protocol, where, form, PROTOCOL_OPTIONAL, problems,
            forbidden=TOOL_SET)
    for name in ("n", "d"):
        if name in protocol and not (_integer(protocol[name])
                                     and protocol[name] >= 1):
            problems.append(f"{where}.{name} must be a positive integer")
    _text(protocol, "gate", where, problems)
    _text(protocol, "label", where, problems, limit=LABEL_MAX)
    _text(protocol, "notes", where, problems, printable=False, limit=FULL_MAX)
    if problems:
        return problems
    if has_columns:
        # `verify_catalog.structural_problems` separates "cannot be read as a
        # circuit" (kind ``schema``: a string where an index belongs, an empty
        # column) from "is not a factory" (a repeated column, a mis-stated N).
        # The first is a malformed submission; the second is the verifier's to
        # reject, with its reasons, in the merge.
        problems += [f"{where}: {detail}" for kind, detail in
                     VC.structural_problems(protocol["k"], protocol["N"],
                                            protocol["columns"])
                     if kind == "schema"]
        return problems
    rows, q = protocol["generator_matrix_rows"], protocol["q"]
    if not isinstance(rows, list) or not rows or not all(
            isinstance(row, str) and row and set(row) <= {"0", "1"}
            for row in rows):
        return [f"{where}.generator_matrix_rows must be a non-empty list of "
                f"non-empty strings of '0' and '1'"]
    if len({len(row) for row in rows}) != 1:
        return [f"{where}.generator_matrix_rows have different lengths "
                f"{sorted({len(row) for row in rows})}"]
    if not _integer(q) or not 1 <= q <= len(rows):
        problems.append(f"{where}.q must be an integer from 1 to the number "
                        f"of rows ({len(rows)})")
    zero = [j for j in range(len(rows[0])) if all(row[j] == "0" for row in rows)]
    if zero:
        problems.append(f"{where}.generator_matrix_rows has all-zero "
                        f"column(s) {zero}: a rotation on no qubit is not part "
                        f"of a circuit here, so delete the column (and do not "
                        f"count it in n)")
    return problems


def submission_problems(submission):
    """Every way the submission file is malformed ([] if it is well formed).

    Only the file: whether a protocol is a factory is the merge's question, and
    whether the reference clashes with the catalogue's is `reference_problems`.
    """
    problems = []
    if not _fields(submission, "submission", TOP_FIELDS, (), problems):
        return problems
    contributor = submission.get("contributor")
    if "contributor" in submission and _fields(
            contributor, "contributor", CONTRIBUTOR_REQUIRED,
            CONTRIBUTOR_OPTIONAL, problems):
        for name in CONTRIBUTOR_REQUIRED + CONTRIBUTOR_OPTIONAL:
            _text(contributor, name, "contributor", problems, limit=200)
    reference = submission.get("reference")
    if "reference" in submission and _fields(
            reference, "reference", REFERENCE_REQUIRED, REFERENCE_OPTIONAL,
            problems):
        for name in REFERENCE_REQUIRED + REFERENCE_OPTIONAL:
            _text(reference, name, "reference", problems,
                  limit={"short": SHORT_MAX, "full": FULL_MAX}.get(name))
        key, url = reference.get("key"), reference.get("url")
        if isinstance(key, str) and not PLACEHOLDER.fullmatch(key) \
                and not REFERENCE_KEY.fullmatch(key):
            problems.append(f"reference.key {key!r} must be 3-64 lowercase "
                            f"letters, digits, '_' or '-', starting with a "
                            f"letter (for example surname2026firstword)")
        short = reference.get("short")
        if isinstance(short, str) and re.search(r"[\[\]]", short):
            problems.append("reference.short may not contain '[' or ']': the "
                            "catalogue prints it as link text")
        if isinstance(url, str) and url.strip() and not PLACEHOLDER.fullmatch(url) \
                and not VC.REFERENCE_URL.fullmatch(url):
            problems.append(f"reference.url {url!r} is not an https link "
                            f"(https://host/path, no spaces, brackets or "
                            f"parentheses); omit the field for unpublished work")
        date = reference.get("date")
        if isinstance(date, str) and not PLACEHOLDER.fullmatch(date) \
                and not VC._reference_date_ok(reference):
            problems.append(f"reference.date {date!r} is not a publication "
                            f"date YYYY-MM or YYYY-MM-DD in the year "
                            f"reference.short prints; omit the field for "
                            f"unpublished work")
    _text(submission, "method", "submission", problems, limit=METHOD_MAX,
          angles=True)
    _text(submission, "terms", "submission", problems, printable=False)
    protocols = submission.get("protocols")
    if "protocols" in submission:
        if not isinstance(protocols, list) or not protocols:
            problems.append("protocols must be a non-empty list")
        else:
            for index, protocol in enumerate(protocols):
                problems += _protocol_problems(protocol, f"protocols[{index}]")
    return problems


# ---------------------------------------------------------------- converting
def matrix_columns(rows):
    """``columns[j]`` = the rows with a 1 in column ``j``: outputs first."""
    return [[i for i, row in enumerate(rows) if row[j] == "1"]
            for j in range(len(rows[0]))]


def source_file(path):
    """The submission's path relative to the repository root, if it is inside."""
    resolved = Path(path).resolve()
    try:
        return resolved.relative_to(REPO.resolve()).as_posix()
    except ValueError:
        return str(path)


def records(submission, file):
    """The `merge_results` records of a WELL-FORMED submission."""
    contributor = submission["contributor"]
    who = contributor["name"].strip()
    if contributor.get("affiliation"):
        who += f" ({contributor['affiliation'].strip()})"
    method = submission["method"].strip()
    out = []
    for index, protocol in enumerate(submission["protocols"]):
        if "generator_matrix_rows" in protocol:
            rows = protocol["generator_matrix_rows"]
            circuit = {"k": protocol["q"], "N": len(rows),
                       "columns": matrix_columns(rows)}
        else:
            circuit = {name: protocol[name] for name in COLUMNS_FORM}
        label = protocol.get("label")
        record = {
            **circuit,
            **{name: protocol[name] for name in ("n", "d", "gate", "notes")
               if name in protocol},
            "regime": REGIME,
            "strength": STRENGTH,
            "discovery": DISCOVERY,
            "citations": [submission["reference"]["key"]],
            "file": file,
            "label": label or f"protocol {index}",
            "origin": contributor["name"].strip(),
            "provenance": (f"community contribution by {who}: {method}"
                           + (f"; protocol {label!r}" if label else "")),
        }
        out.append(record)
    return out


def reference_entry(reference):
    return {name: reference[name]
            for name in REFERENCE_REQUIRED[1:] + REFERENCE_OPTIONAL
            if name in reference}


def reference_problems(payload, reference):
    """Whether the submission's reference can join ``payload``'s header."""
    key, entry = reference["key"], reference_entry(reference)
    if key in MR.DEFAULT_REFERENCES:
        return [f"reference.key {key!r} is one of the maintainers' own "
                f"reports; credit the submission to its own work"]
    held = (payload.get("references") or {}).get(key)
    if held is not None and held != entry:
        return [f"reference.key {key!r} is already in the catalogue as "
                f"{json.dumps(held, ensure_ascii=False)}; use exactly that "
                f"entry, or another key for a different work"]
    for other, other_entry in (payload.get("references") or {}).items():
        if other != key and (other_entry.get("full") == entry["full"]
                             or (entry.get("url") is not None
                                 and other_entry.get("url") == entry["url"])):
            return [f"this work is already in the catalogue under the key "
                    f"{other!r}; use that key and its exact entry"]
        if other != key and other_entry.get("short") == entry["short"]:
            return [f"reference.short {entry['short']!r} is already the label "
                    f"of {other!r}; the citation column would print two "
                    f"different works identically -- distinguish it (for "
                    f"example with a letter after the year)"]
    return []


# ------------------------------------------------ the length-54 classification
def intrinsic_output(k, monomials):
    """``(q, monomials')``: the gate with its spectator outputs removed.

    A spectator direction ``u`` has ``tau(u, -, -) = 0``, so the gate is
    Clifford along it; the output that the length-54 classification keys on is
    the gate restricted to a complement of those directions, up to CNOT+S.
    Read off the ``Z_8`` phase on a complement by Mobius inversion.
    """
    T = GC.tensor(k, monomials)
    equations = [sum(1 << a for a in range(k)
                     if GC.evaluate(T, 1 << a, 1 << b, 1 << c))
                 for b in range(k) for c in range(k)]
    pivots = {}
    for vector in equations:                       # reduced row echelon form
        for column, row in pivots.items():
            if vector >> column & 1:
                vector ^= row
        if vector:
            column = vector.bit_length() - 1
            for other in list(pivots):
                if pivots[other] >> column & 1:
                    pivots[other] ^= vector
            pivots[column] = vector
    radical = []
    for free in (c for c in range(k) if c not in pivots):
        vector = 1 << free
        for column, row in pivots.items():
            if row >> free & 1:
                vector |= 1 << column
        radical.append(vector)
    span, complement = list(radical), []

    def independent(vectors, v):
        basis = []
        for w in vectors + [v]:
            for b in basis:
                w = min(w, w ^ b)
            if not w:
                return False
            basis.append(w)
        return True
    for a in range(k):
        if independent(span, 1 << a):
            span.append(1 << a)
            complement.append(1 << a)
    q = len(complement)

    def phase(x):
        return sum(1 << (len(m) - 1) for m in monomials
                   if all(x >> w & 1 for w in m)) % 8
    values = []
    for y in range(1 << q):
        x = 0
        for i in range(q):
            if y >> i & 1:
                x ^= complement[i]
        values.append(phase(x))
    reduced = set()
    for size in (1, 2, 3):
        for support in itertools.combinations(range(q), size):
            coefficient = sum(
                (-1) ** (size - bin(sub).count("1"))
                * values[sum(1 << support[j] for j in range(size)
                             if sub >> j & 1)]
                for sub in range(1 << size)) % 8
            if coefficient >> (size - 1) & 1:
                reduced.add(frozenset(support))
    return q, reduced


def frontier_problems(merged, verdicts):
    """Circuits the length-54 classification says cannot exist.

    Every class with ``n <= 54`` and ``d >= 3`` is on that classification's
    Pareto frontier or strictly dominated by a point of it -- same exact
    distance, same output
    once spectators are removed, no more inputs and no more wires --
    `master_catalog/tests` holds the catalogue to that.  A contributed circuit
    that improves a Pareto point, or is a new or improved class no Pareto point
    dominates, would contradict it (or lie outside its domain), and is refused
    here rather than found by the tests after a write.
    """
    pareto = [row for row in merged["factories"] if PARETO in row["regimes"]]
    if not pareto:
        return []           # a catalogue without the frontier has nothing to hold
    problems = []
    for index, verdict, row, _detail in verdicts:
        # the classification covers d >= 3: a distance-2 class is outside it
        if verdict not in ("accepted", "improved") \
                or row["n"] > MR.CLASSIFICATION_LENGTH \
                or row["d"] < MR.CLASSIFICATION_MIN_DISTANCE:
            continue
        shape = f"[[{row['n']},{row['k']},{row['d']}]] N={row['N']}"
        if PARETO in row["regimes"]:
            problems.append((
                "pareto-improvement",
                f"protocol {index} would improve a Pareto point of the "
                f"length-54 classification ({shape}), which that "
                f"classification says cannot exist: investigate before "
                f"merging"))
            continue
        q, output = intrinsic_output(row["k"], VC.row_monomials(row))
        if not row["d_is_exact"]:
            problems.append((
                "frontier-unchecked",
                f"protocol {index} ({shape}) has no exact distance, so it "
                f"cannot be compared with the length-54 classification's "
                f"Pareto points, which are all exact: investigate before "
                f"merging"))
            continue
        dominated = any(
            point["k"] == q and point["d"] == row["d"]
            and point["n"] <= row["n"] and point["N"] <= row["N"]
            and (point["n"], point["N"]) != (row["n"], row["N"])
            and GC.gl_isomorphic(q, VC.row_monomials(point), output)
            for point in pareto)
        if not dominated:
            problems.append((
                "frontier-contradiction",
                f"protocol {index} ({shape}) is not dominated by any Pareto "
                f"point of the length-54 classification with its exact "
                f"distance and spectator-free output: it lies outside that "
                f"classification's domain or contradicts it -- investigate "
                f"before merging"))
    return problems


# ------------------------------------------------------------------ checking
def check(submission, payload, file):
    """Merge a well-formed submission into a COPY of ``payload``.

    Returns ``(merged, verdicts, residue, cited)``: the merged copy, the
    `merge_results.merge` verdicts in protocol order, the problems that stop a
    write (a circuit the length-54 classification says cannot exist -- see
    `frontier_problems` -- and the file-level checks of the merged copy), and for each verdict whether the submission's
    reference was credited on its row -- which happens exactly for a class the
    catalogue did not have.  ``payload`` itself is never touched.  Raises
    `SubmissionError` when the reference cannot be registered.
    """
    reference = submission["reference"]
    problems = reference_problems(payload, reference)
    if problems:
        raise SubmissionError(problems)

    def prepared(batch):
        # A JSON round trip is a complete deep copy of a JSON payload, at half
        # the cost of `copy.deepcopy` on a 12 MB catalogue.
        copy = json.loads(json.dumps(payload))
        copy.setdefault("references", {}).setdefault(
            reference["key"], reference_entry(reference))
        if REGIME in copy["regimes"]:
            # the header's sentence stands; restating it differently would be
            # a redefinition, which `merge_results` rejects
            for record in batch:
                record.pop("strength", None)
        return copy

    # Credit goes to NEW classes only.  A class the catalogue already holds
    # keeps the credit it was given -- a class published before is credited to
    # that work alone, and a Pareto point of the length-54 classification by
    # who found it -- so a protocol that turns out to be a duplicate or an
    # improvement must not name the contributor's reference, or
    # `merge_results` would add it.  Which protocols those are is only known
    # after merging, and a submission can hold two copies of one class, so the
    # verdicts come from a first merge into a scratch copy, in order.
    scratch_batch = records(submission, file)
    merged = prepared(scratch_batch)
    verdicts = MR.merge(merged, scratch_batch, file)
    if any(v in ("duplicate", "improved") for _i, v, _r, _d in verdicts):
        # only then does the credit differ, so only then merge again -- the
        # verification a merge repeats is the expensive part at large n
        batch = records(submission, file)
        for record, (_i, verdict, _row, _detail) in zip(batch, verdicts):
            if verdict in ("duplicate", "improved"):
                del record["citations"]
        scratch = verdicts
        merged = prepared(batch)
        verdicts = MR.merge(merged, batch, file)
        if [v for _i, v, _r, _d in verdicts] != [v for _i, v, _r, _d in scratch]:
            raise RuntimeError("the second merge disagreed with the first")

    cited = [verdict == "accepted" for _i, verdict, _r, _d in verdicts]
    residue = frontier_problems(merged, verdicts)
    if not any(cited) and reference["key"] not in (payload.get("references")
                                                    or {}):
        # nothing cites it, so it does not join the header
        del merged["references"][reference["key"]]
    residue += (VC.duplicate_class_problems(merged["factories"])
                + VC.provenance_problems(merged)
                + VC.citation_problems(merged)
                + VC.header_problems(merged))
    return merged, verdicts, residue, cited


def _describe(row):
    d = row["d"] if row["d_is_exact"] else f">={row['d']}"
    gate = row["gate_human"]
    gate = gate if len(gate) <= 40 else gate[:37] + "..."
    return f"[[{row['n']},{row['k']},{d}]] N={row['N']} {gate}"


def report(submission, verdicts, cited, residue):
    """Print one line per protocol and the totals; return the counts."""
    key = submission["reference"]["key"]
    counts = dict.fromkeys(("accepted", "improved", "duplicate", "rejected"), 0)
    for (index, verdict, row, detail), new in zip(verdicts, cited):
        counts[verdict] += 1
        label = submission["protocols"][index].get("label")
        name = f"protocol {index}" + (f" ({label})" if label else "")
        if verdict == "rejected":
            print(f"  rejected   {name}:")
            for kind, message in detail:
                print(f"               - {kind}: {message}")
            continue
        if verdict == "accepted":
            why = f"a class the catalogue did not have; credited to {key}"
        elif verdict == "improved":
            why = (f"{detail}; the circuit is stored, but the class keeps the "
                   f"credit it already had ({', '.join(row['citations'])})")
        else:
            why = (f"already held as N={row['N']}, d={row['d']}; nothing is "
                   f"stored, and the class keeps the credit it already had "
                   f"({', '.join(row['citations'])})")
        print(f"  {verdict:<10} {name}: {_describe(row)} -- {why}")
    print(f"\n{len(verdicts)} protocol(s): "
          + ", ".join(f"{count} {name}" for name, count in counts.items()))
    if residue:
        print(f"\nthe merged catalogue fails {len(residue)} check(s):")
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
    return counts


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("submission", type=Path,
                        help="the catalogue input JSON file")
    parser.add_argument("--catalog", type=Path, default=CF.CATALOG_JSON,
                        help="the catalogue JSON to check against "
                             "(default: master_catalog/master_catalog.json)")
    parser.add_argument("--markdown", type=Path, default=None,
                        help="with --write, where to write the rendered "
                             "catalogue (default: MASTER_CATALOG.md beside "
                             "the JSON)")
    parser.add_argument("--write", action="store_true",
                        help="MAINTAINERS: write the merged catalogue if every "
                             "protocol verified")
    args = parser.parse_args(argv)

    try:
        submission = load_submission(args.submission)
        problems = submission_problems(submission)
        if problems:
            raise SubmissionError(problems)
        file = source_file(args.submission)
        into_master = args.catalog.resolve() == CF.CATALOG_JSON.resolve()
        if args.write and into_master and not Path(args.submission).resolve() \
                .is_relative_to(SUBMISSIONS.resolve()):
            raise SubmissionError([
                f"--write into the master catalogue needs the submission "
                f"under {SUBMISSIONS.relative_to(REPO)}/, so every merged "
                f"row's source names a file the repository holds; move it "
                f"there first"])
        try:
            payload = CF.load(args.catalog)
        except (OSError, ValueError) as error:
            print(f"CANNOT READ THE CATALOGUE {args.catalog}: {error}")
            return 2
        before = len(payload["factories"])
        contributor = submission["contributor"]["name"]
        print(f"checking {file}: {len(submission['protocols'])} protocol(s) "
              f"from {contributor}, credited to {submission['reference']['key']}")
        print(f"against {source_file(args.catalog)} ({before} classes)\n",
              flush=True)
        merged, verdicts, residue, cited = check(submission, payload, file)
    except SubmissionError as error:
        print(f"MALFORMED SUBMISSION {args.submission} -- nothing was checked "
              f"against the catalogue:")
        for problem in error.problems:
            print(f"  - {problem}")
        return 2

    counts = report(submission, verdicts, cited, residue)
    after = len(merged["factories"])
    failed = bool(counts["rejected"] or residue)
    if not args.write:
        print(f"catalogue: {before} -> {after} classes (nothing written: this "
              f"was a check; maintainers merge with --write)")
        return 1 if failed else 0
    if failed:
        print(f"catalogue: NOT WRITTEN -- "
              + ("a protocol was rejected" if counts["rejected"]
                 else "the merged catalogue fails a check")
              + f"; {args.catalog} is unchanged")
        return 1
    markdown = args.markdown or args.catalog.parent / CF.CATALOG_MD.name
    CF.write(merged, args.catalog, markdown)
    # reduced-degree bounds computed on the way in, kept beside the catalogue
    # they were computed for (for the master catalogue, the cache
    # verify_catalog.py preloads)
    VC.persist_metric_cache(args.catalog.parent / VC.METRIC_CACHE.name)
    print(f"catalogue: {before} -> {after} classes, written to {args.catalog} "
          f"and {markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
