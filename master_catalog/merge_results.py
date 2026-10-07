#!/usr/bin/env python3
"""Merge new factory results into the master catalogue.

    python merge_results.py new_results.json          # verify, merge, rewrite
    python merge_results.py new_results.json --dry-run # say what would happen

Every incoming circuit is put through the SAME bar as a shipped row, and that
is a fact about the call graph rather than a promise in prose: this module
imports `verify_catalog`, assembles a candidate row, and refuses to accept it
unless `verify_catalog.verify_row` passes on the assembled row.  So whatever
this tool admits is, by construction, what `verify_catalog.py` will afterwards
confirm -- there is no second, laxer definition of "verified" anywhere here.

THE INPUT FILE
--------------
One JSON object per result.  The file may be

  * a JSON array of them,                       ``[{...}, {...}]``
  * an object wrapping one under ``results`` / ``factories`` / ``rows``,
  * a single bare object,                       ``{...}``
  * or JSON Lines -- one object per line, ``#`` comments and blank lines
    ignored.

An empty file is a valid input with no results in it, and merging it changes
nothing.

Fields of a result object:

  ``k``          REQUIRED.  Output wires.  They are qubits ``0..k-1``; wires
                 ``k..N-1`` are the postselected checks.  This is a DECLARATION
                 and not a derivable fact -- the same columns with a different
                 ``k`` are a different factory, or none -- which is why it is an
                 input and almost nothing else is.
  ``N``          REQUIRED.  Ambient wires; must equal the largest qubit index
                 the columns use, plus one.
  ``columns``    REQUIRED.  The circuit: one list of qubit indices per pi/4
                 parity rotation.
  ``n``          optional.  Number of columns; checked against ``columns``.
  ``d``          optional CLAIM.  Never believed: the distance is measured from
                 the columns and the measurement is what gets stored.  A claim
                 the measurement DISPROVES (an explicit fault lighter than the
                 claim) rejects the record, because a wrong distance usually
                 means the record is about a different circuit.  A claim the
                 measurement merely exceeds is accepted, and the larger proved
                 value is stored: understating is not an error.
  ``gate``       optional CLAIM, as a monomial or ``T``/``CS``/``CCZ`` string.
                 Read by `gatelabels.parse`, which reports a string it cannot
                 read as unreadable rather than guessing; either way the gate
                 stored is the one the columns actually deposit.
  ``t_count``, ``poly_degree``   optional CLAIMS, compared with the exact
                 recomputation where the recomputation is feasible.
  ``regime``     optional.  Which corpus this result came from, defaulting to
                 ``merged results``.  A regime the catalogue has not seen is
                 registered in the file header, at the END of the regime order
                 -- i.e. as the weakest claim -- with ``strength`` as its
                 meaning.
  ``strength``   optional.  What a row from a NEW regime means, one sentence.
  ``discovery``  optional.  ``AI search`` (default) or ``pre-existing``; must
                 be a value the catalogue header's glossary defines.
  ``citations``  optional.  Keys of the header's ``references`` map crediting
                 the class -- a published work that states it, and the report
                 this catalogue lists it in.  Omitted, an ACCEPTED row is
                 credited to the default works for its length and distance
                 (`default_citations`).  An improvement or a duplicate adds
                 only the citations the record names: a class already held
                 keeps the credit it was given, so a class credited to a
                 published work alone is not re-credited to the defaults
                 because a search found it again.
  ``label``, ``provenance``, ``origin``, ``file``, ``notes``
                 optional provenance strings for the row's ``sources`` entry.
                 They are INERT: nothing in this folder ever opens a path they
                 name.

WHAT HAPPENS TO EACH RESULT
---------------------------
1.  **Verified.**  Structure, the factory condition, the gate, spectator and
    pseudo-output freedom, freedom from check wires that carry no syndrome bit
    of their own, the metrics -- `verify_catalog.derive`.  Then the
    distance is MEASURED (`verify_catalog.measure_distance`), not assumed.
2.  **Canonicalised.**  The output wires are relabelled into the S_k lex-
    minimal frame, so the stored columns deposit literally the stored ``gate``
    rather than merely an S_k-equivalent one.  A gate too wide for the ``k!``
    minimisation to be proved is stored in its as-found frame, exactly as the
    six wide rows already in the catalogue are; the frame is cosmetic, and the
    class is decided either way.
3.  **Deduplicated** on ``(n, k, d, GL(k,2) gate)`` -- the catalogue's key: the
    measured distance, and the gate up to an invertible change of the output
    basis and diagonal Clifford corrections.  A circuit at a different distance
    is a different class and is never folded into one at another distance.  An equal proved ``S_k`` key settles a match outright;
    everything else is decided by the explicit `glcanon.gl_isomorphic`
    procedure rather than a hash.  That search
    is bounded and can return no verdict; when it does, the result is KEPT as a
    class of its own and records the gap in ``dedup_note``.  Refusing it would
    discard a verified factory over a bookkeeping question, at the widths where
    results are hardest to find again -- and the circuit, its gate and its
    distance were re-derived here regardless of how it is filed.
4.  Then one of four verdicts:

    ``accepted``   a class the catalogue did not have.  Appended.
    ``improved``   a class it had, with a better circuit: fewer ambient qubits,
                   then fewer columns, then a stronger proved distance, then a
                   proved canonical frame.  The row's circuit fields are
                   replaced and the new provenance is APPENDED to ``sources``,
                   so the class's history survives the replacement.
    ``duplicate``  a class it had, with a circuit no better.  **Nothing
                   changes** -- not even ``sources``.  The catalogue records
                   where the circuits it STORES came from, and re-merging the
                   same file must be a no-op the second time; accreting
                   provenance for a circuit that was thrown away would break
                   both.  The one exception is credit: a citation the record
                   explicitly names is added to the class.
    ``rejected``   did not verify.  The reason is printed.

5.  Both catalogue files are regenerated from the merged payload by
    `catalogfile.write`, deterministically: rows are re-sorted on
    ``(n, k, str(class key))``, which is the order the catalogue is already in,
    so an unchanged catalogue is rewritten byte-identically.

Exit status is 0 when every result was verified (whatever its verdict) and 1
when any was rejected -- a rejection is input the owner should look at.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import catalogfile as CF                                          # noqa: E402
import gatelabels as GL                                           # noqa: E402
import glcanon as GC                                              # noqa: E402
import skcanon as SK                                              # noqa: E402
import verify_catalog as VC                                       # noqa: E402

#: Fields a result object must carry, and may carry.  Anything else is a typo
#: -- ``colums`` silently ignored is a circuit merged from a field nobody read.
RECORD_REQUIRED = ("k", "N", "columns")
RECORD_OPTIONAL = ("n", "d", "gate", "t_count", "poly_degree",
                   "regime", "strength", "discovery", "citations",
                   "label", "provenance", "origin", "file", "notes")

#: Where a result with no stated corpus is filed, and what such a row means.
#: A new regime joins the header's regime order at the END, which is the order
#: `strongest_claim` reads: a freshly merged witness never outranks a
#: classification, and nothing this tool does can promote it.
DEFAULT_REGIME = "merged results"
DEFAULT_STRENGTH = ("verified witness merged into this catalogue by "
                    "merge_results.py; not a maximum")
DEFAULT_DISCOVERY = "AI search"

#: The works a merged class is credited to when its record names none.  Every
#: class this catalogue holds is reported in the symmetry-and-AI paper; one no
#: longer than the length-54 classification, and at a distance that
#: classification covers (it is ``d >= 3``), is ALSO within that
#: classification's window and is credited to it.  A record that knows of a
#: published source for its class passes ``citations`` itself.  The entries are
#: registered in the header the first time a row uses them, exactly as a new
#: regime is.
CLASSIFICATION_LENGTH = 54
CLASSIFICATION_MIN_DISTANCE = 3
DEFAULT_REFERENCES = {
    "wills2026classification": {
        "short": "Wills et al. (2026)",
        "full": "A. Wills, S. P. Jain, and S. Singh, \"Classification of "
                "Generalised Triorthogonal Codes through Length 54,\" "
                "arXiv:2609.30860 (2026).",
        "url": "https://arxiv.org/abs/2609.30860",
    },
    "jain2026symmetry": {
        "short": "Jain et al. (2026)",
        "full": "S. P. Jain, A. Wills, and S. Singh, \"Symmetry and "
                "AI-assisted discovery of magic-state factories,\" "
                "arXiv:2610.06535 (2026).",
        "url": "https://arxiv.org/abs/2610.06535",
    },
}


def default_citations(n: int, d: int = CLASSIFICATION_MIN_DISTANCE) -> list[str]:
    """The works a class of ``n`` injections at distance ``d`` is credited to
    by default.  A distance-2 class is outside the length-54 classification,
    whatever its length."""
    if n <= CLASSIFICATION_LENGTH and d >= CLASSIFICATION_MIN_DISTANCE:
        return ["wills2026classification", "jain2026symmetry"]
    return ["jain2026symmetry"]


# ------------------------------------------------------------------- reading
def read_records(path: Path | str) -> list[dict]:
    """The result objects in ``path``, in any of the four accepted layouts.

    An empty file yields an empty list rather than an error: "nothing new to
    merge" is a normal thing to say, and a tool that treats it as a failure
    invites the caller to skip the merge step entirely.
    """
    text = Path(path).read_text(encoding="utf-8")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        records = []
        for lineno, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            try:
                records.append(json.loads(stripped))
            except json.JSONDecodeError as bad:
                raise ValueError(
                    f"{path}:{lineno}: the file is neither one JSON document "
                    f"nor one JSON object per line ({bad})") from None
        return records
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for name in ("results", "factories", "rows"):
            if isinstance(payload.get(name), list):
                return payload[name]
        return [payload]
    raise ValueError(f"{path}: a {type(payload).__name__} is not a result "
                     f"object, a list of them, or an object wrapping one")


def record_problems(record) -> list[tuple[str, str]]:
    """Whether the RECORD is well formed, before its circuit is looked at.

    Only the envelope: required fields present, no undocumented ones, claims of
    the right type.  Whether the circuit is a factory is `verify_catalog`'s
    question and is asked next.
    """
    if not isinstance(record, dict):
        return [("schema", f"the result is a {type(record).__name__}, not an "
                           f"object")]
    problems = []
    missing = [name for name in RECORD_REQUIRED if name not in record]
    if missing:
        problems.append(("schema", f"missing required field(s) "
                                   f"{', '.join(missing)}"))
    unknown = [name for name in record
               if name not in RECORD_REQUIRED + RECORD_OPTIONAL]
    if unknown:
        problems.append(("schema", f"undocumented field(s) "
                                   f"{', '.join(sorted(unknown))}; see the "
                                   f"schema in the README"))
    for name in ("d", "n", "t_count", "poly_degree"):
        if record.get(name) is not None and not VC._integer(record[name]):
            problems.append(("schema", f"{name}={record[name]!r} is not a "
                                       f"non-negative integer"))
    for name in ("gate", "regime", "strength", "discovery", "label",
                 "provenance", "origin", "file", "notes"):
        if record.get(name) is not None and not isinstance(record[name], str):
            problems.append(("schema", f"{name} must be a string, not a "
                                       f"{type(record[name]).__name__}"))
    citations = record.get("citations")
    if citations is not None and not (
            isinstance(citations, list) and citations
            and all(isinstance(key, str) for key in citations)
            and len(set(citations)) == len(citations)):
        problems.append(("schema", "citations must be a non-empty list of "
                                   "distinct reference keys"))
    return problems


# ---------------------------------------------------------- one candidate row
def candidate_row(record, payload, source_file: str, index: int):
    """Build the catalogue row an accepted result would become.

    Returns ``(row, problems)``.  ``problems`` empty means the row is publish-
    able and `verify_catalog.verify_row` has already said so about this exact
    dictionary -- the last thing this function does is ask it.
    """
    problems = record_problems(record)
    if any(kind == "schema" for kind, _d in problems):
        return None, problems
    k, N, columns = record["k"], record["N"], record["columns"]

    # `derive` opens with the indexing-safety checks -- `N` and `k` bound every
    # loop after them and they came out of a file, so `N: 2**63` is rejected in
    # milliseconds rather than hung on -- and returns no facts if they fail.
    facts, derived = VC.derive(columns, k, N)
    problems += derived
    if not facts:
        return None, problems
    if record.get("n") is not None and record["n"] != facts["n"]:
        problems.append(("shape", f"n={record['n']} but there are "
                                  f"{facts['n']} columns"))
    if problems:
        # Not a factory, so not worth canonicalising or sweeping: at n ~ 1000
        # the distance sweep is the entire cost of a merge.
        return None, problems

    # ---- the claimed gate, if there is one -- checked IN THE SOURCE FRAME,
    # before any output relabelling.  The label describes the circuit as
    # submitted; canonicalisation permutes the outputs, so comparing the claim
    # against the canonical gate rejected truthful labels -- a record whose
    # columns deposit ``1+01`` and honestly say ``T1.CS01`` was refused
    # because the STORED frame calls that class ``0+01``.  The frame is this
    # catalogue's presentation choice, not the submitter's error.
    # `gatelabels.parse` reads the string or says it cannot; it never guesses,
    # and neither do we.
    if record.get("gate") is not None:
        kind, claimed_gate, note = GL.parse(record["gate"], k)
        if kind == "unreadable":
            problems.append(("gate-claim",
                             f"the claimed gate {record['gate']!r} cannot be "
                             f"read ({note}); drop the field or write it as "
                             f"monomials, but do not publish an unreadable "
                             f"claim"))
        elif set(claimed_gate) != set(facts["monomials"]):
            problems.append(("gate-claim",
                             f"the record claims the gate {record['gate']!r}, "
                             f"the columns deposit {facts['gate']!r}"))
    if problems:
        # Checked before the canonicalisation and the sweep because the record
        # is going to be refused, and the sweep is the expensive part.
        return None, problems

    # ---- the canonical output frame.  Relabelling output wires permutes the
    # gate and leaves the fault structure alone, so it is done BEFORE the
    # distance is measured and the witness's column indices stay meaningful.
    canonical = facts["sk_key"] is not None
    relabelled = False
    if canonical:
        perm = facts["sk_perm"]
        moved = [sorted(perm[q] if q < k else q for q in column)
                 for column in facts["columns"]]
        relabelled = moved != facts["columns"]
        if relabelled:
            facts, again = VC.derive(moved, k, N)
            problems += again
            if not facts:
                return None, problems
        if facts["sk_key"] != [list(Q) for Q in SK.encode(facts["monomials"])]:
            problems.append(("sk_key-mismatch",
                             "relabelling into the canonical frame did not "
                             "reproduce the gate's own S_k representative"))
            return None, problems
    if problems:
        return None, problems

    # ---- the distance.  MEASURED, then read back out of the report the way a
    # row stores it: exact only when a clean sweep below it met a witness at it.
    report = VC.measure_distance(facts["columns"], k, N)
    if report["d_exact"] is not None:
        d, exact = report["d_exact"], True
        d_upper, witness = report["d_exact"], report["witness"]
    else:
        d, exact = report["d_at_least"], False
        d_upper = report["d_upper"]
        witness = report["witness"] if d_upper is not None else None
    if d < 2:
        problems.append(("distance-below-2",
                         f"the distance is {d}: this catalogue is d >= 2, and "
                         f"a circuit with an undetectable single fault "
                         f"distils nothing"))
    if record.get("d") is not None and d_upper is not None \
            and record["d"] > d_upper:
        problems.append(("distance-claim",
                         f"the record claims d={record['d']} but the fault on "
                         f"columns {witness} has weight {d_upper}, so the "
                         f"distance is at most that"))
    if problems:
        return None, problems

    # ---- the claimed metrics, where the recomputation is feasible.
    for name in ("t_count", "poly_degree"):
        claimed, got = record.get(name), facts[name]
        if claimed is None or got is None:
            continue
        if "UPPER BOUND" in (facts.get(f"{name}_note") or ""):
            # ``got`` is a sampled bound on the true minimum, not the minimum:
            # only a claim ABOVE it is disproved, while one below it may well
            # be right and cannot be refuted here.  Comparing for equality
            # rejected a record claiming this catalogue's OWN published value
            # whenever the local search happened to land on a weaker bound --
            # which it does on any cache miss, since a verify runs fewer frames
            # than some shipped rows were computed with.
            if claimed > got:
                problems.append((f"{name}-claim",
                                 f"the record claims {name}={claimed}, but a "
                                 f"frame reaching {got} already beats it, so "
                                 f"the claim is disproved"))
        elif claimed != got:
            problems.append((f"{name}-claim",
                             f"the record claims {name}={claimed}, the exact "
                             f"recomputation gives {got}"))

    # ---- provenance.  Inert strings, every one of them.
    regime = record.get("regime") or DEFAULT_REGIME
    discovery = record.get("discovery") or DEFAULT_DISCOVERY
    if discovery not in payload["discovery"]:
        problems.append(("schema",
                         f"discovery={discovery!r} is not one of the values "
                         f"the catalogue header defines "
                         f"({', '.join(payload['discovery'])})"))
    known = payload["regimes"]
    if regime in known and record.get("strength") is not None \
            and record["strength"] != known[regime]:
        problems.append(("schema",
                         f"regime {regime!r} already means "
                         f"{known[regime]!r}; a result may not redefine it"))
    if problems:
        return None, problems
    strength = known.get(regime) or record.get("strength") or DEFAULT_STRENGTH
    citations = list(record.get("citations") or default_citations(facts["n"], d))
    references = payload.get("references") or {}
    unknown = [key for key in citations
               if key not in references and key not in DEFAULT_REFERENCES]
    if unknown:
        problems.append(("schema",
                         f"citations {', '.join(map(repr, unknown))} are not "
                         f"keys of the catalogue's references map; add the "
                         f"work to the header first"))
        return None, problems

    row = {
        "n": facts["n"], "k": k, "d": d, "N": N, "level": 3,
        "gate": facts["gate"], "gate_human": facts["gate_human"],
        "sk_key": facts["sk_key"], "sk_canonical_frame": canonical,
        "sk_fingerprint": facts["sk_fingerprint"],
        "t_count": facts["t_count"], "poly_degree": facts["poly_degree"],
        "effective_width": facts["effective_width"],
        "d_is_exact": exact, "d_upper": d_upper, "d_witness": witness,
        "regimes": [regime], "discovery": discovery,
        "relabelled_into_canonical_frame": relabelled,
        "strongest_claim": strength,
        "columns": facts["columns"],
        "citations": citations,
        # provisional: kept only if `merge` accepts this row as a NEW class --
        # an improvement keeps the incumbent's label, a duplicate changes nothing
        "catalog_label": CF.next_label(payload["factories"], facts["n"], k, d),
        "sources": [{
            "regime": regime,
            "file": record.get("file") or source_file,
            "label": record.get("label") or str(index),
            "N": N, "d": d, "d_is_exact": exact,
            "origin": record.get("origin"),
            "provenance": record.get("provenance"),
            **({"notes": record["notes"]} if record.get("notes") else {}),
        }],
    }
    if not canonical:
        row["sk_key_note"] = (
            f"the S_k lex-minimum over {k}! relabellings of a "
            f"{len(facts['monomials'])}-monomial gate was not proved within "
            f"the search budget, so this circuit is shown in its as-found "
            f"output frame; only the displayed labelling is affected, and this "
            f"row's class was decided against every other row of its shape by "
            f"glcanon.gl_isomorphic")
    for name in ("t_count_note", "poly_degree_note"):
        if facts[name] is not None:
            row[name] = facts[name]

    # ---- the bar, applied to the finished row by the same code that will
    # re-check it in the shipped file.  If this ever disagrees with everything
    # above, the bug is here and the row does not go in.
    _facts, final = VC.verify_row(row)
    if final:
        problems += [("not-as-verified", f"{kind}: {detail}")
                     for kind, detail in final]
        return None, problems
    return row, problems


# ------------------------------------------------------------------- dedup
def class_key(row):
    """``(n, k, d, S_k gate)``, fingerprint if unproved.

    A REFINEMENT of the catalogue's class ``(n, k, d, GL(k,2) gate)``: equal
    proved keys are one class, unequal ones may still be.  The distance is part
    of both, so a circuit at a higher distance is never folded into a narrower
    one at a lower distance.
    """
    return (row["n"], row["k"], row["d"],
            tuple(map(tuple, row["sk_key"])) if row["sk_key"] is not None
            else f"fingerprint:{row['sk_fingerprint']}")


def sort_key(row):
    """The catalogue's row order, and the reason a no-op merge is byte-identical."""
    n, k, d, cls = class_key(row)
    return (n, k, d, str(cls))


def retention_key(row):
    """Lower is better: the tightest circuit for a class.

    Fewest ambient qubits first -- that is the cost that matters and the rule
    the catalogue was built under -- then fewest columns, then the strongest
    proved distance, then a circuit whose canonical frame was actually proved
    over one shown as found.  ``n`` is constant within a class, and since
    2026-09-15 so is ``d`` -- both are part of the key -- so neither of those
    tie-breaks can fire; they are written down because the rule is stated in
    terms of them and a reader should not have to rediscover why.
    """
    return (row["N"], row["n"], -row["d"], row["sk_key"] is None)


class Undecided(Exception):
    """No verdict on whether a candidate is a held class, within budget.

    Carries the rows it could not be told apart from.  The merge does NOT
    refuse the record over it: the circuit was re-derived and its distance
    proved like every other row's, and at the widths where the search gives up
    those results are the hardest to find again.  It is kept as a class of its
    own, carrying a ``dedup_note`` that says what was not proved -- which is
    the bargain `sk_key_note` already makes for an unproved canonical frame.
    """

    def __init__(self, rows):
        super().__init__(f"undecided against row(s) {rows}")
        self.rows = rows


def find_class(rows, candidate):
    """Index of the row holding ``candidate``'s class, or ``None``.

    The class is ``(n, k, d, GL(k,2) gate)`` -- a circuit at another distance is
    another class, whatever its gate.  An equal PROVED ``S_k`` key settles
    a match on its own: the lex-minimum is a complete invariant of the finer
    permutation class, and a permutation is a frame change.  It settles nothing
    in the other direction -- ``T0.T1`` and ``T0.CS01`` have different keys and
    are one class -- so every other same-``(n, k, d)`` row is decided by
    `glcanon.gl_isomorphic`, a decision procedure, which is what makes the
    catalogue's "no duplicate classes" a statement rather than a hope.
    """
    if candidate["sk_key"] is not None:
        key = class_key(candidate)
        for index, row in enumerate(rows):
            if row["sk_key"] is not None and class_key(row) == key:
                return index
    same_shape = [(index, row) for index, row in enumerate(rows)
                  if (row["n"], row["k"], row["d"])
                  == (candidate["n"], candidate["k"], candidate["d"])]
    if not same_shape:
        return None
    mine = VC.row_monomials(candidate)
    undecided = []
    for index, row in same_shape:
        verdict = GC.gl_isomorphic(row["k"], VC.row_monomials(row), mine)
        if verdict is None:
            undecided.append(index)
        elif verdict:
            return index
    if undecided:
        # Not a miss.  `gl_isomorphic` returns ``None`` when its search ran out
        # of budget, which is the one answer that must not be rounded: rounding
        # it to "no match" files the candidate as a NEW class, and if it was in
        # fact the held one the catalogue has just acquired the duplicate its
        # key exists to prevent.  Raising it as a distinguishable outcome lets
        # the caller decide.
        raise Undecided(undecided)
    return None


#: The circuit-describing half of a row: what an improvement replaces.  The
#: provenance half (``regimes``, ``discovery``, ``strongest_claim``,
#: ``sources``) is merged instead of overwritten, so a class keeps its history.
CIRCUIT_FIELDS = ("d", "N", "gate", "gate_human", "sk_key",
                  "sk_canonical_frame", "sk_fingerprint", "t_count",
                  "poly_degree", "effective_width", "d_is_exact", "d_upper",
                  "d_witness", "relabelled_into_canonical_frame", "columns")
#: Every optional note, so `improve` replaces or clears ALL of them.  A note
#: left behind by an improvement describes a circuit that is no longer there:
#: the ten reduced rows each carry a ``columns_note`` saying their N is not one
#: their sources published, and an improvement appends a source publishing the
#: new N -- so a stranded note turns into a `verify_catalog` schema failure the
#: moment any of them is improved.  Keep this in step with
#: `catalogfile.OPTIONAL_FIELDS`.
NOTE_FIELDS = ("sk_key_note", "t_count_note", "poly_degree_note",
               "columns_note", "dedup_note",
               # a certificate belongs to the circuit it certified, so an
               # improvement that replaces the circuit must drop it
               "d_certified", "d_certified_is_exact", "d_certified_source")


def improve(incumbent, candidate, regimes):
    """Replace the stored circuit, keep the class's provenance, in place.

    In place, and field by field, so the row's key order -- and therefore the
    diff against the shipped JSON -- stays as small as the change really is.

    ``regimes`` is the catalogue header's regime map, whose ORDER is strongest
    claim first; the improved row keeps its strongest one, which is not
    necessarily the incoming one.
    """
    for name in CIRCUIT_FIELDS:
        incumbent[name] = candidate[name]
    for name in NOTE_FIELDS:
        if name in candidate:
            incumbent[name] = candidate[name]
        else:
            incumbent.pop(name, None)
    order = list(regimes)
    incumbent["regimes"] = sorted(
        set(incumbent["regimes"]) | set(candidate["regimes"]),
        key=order.index)
    incumbent["strongest_claim"] = regimes[incumbent["regimes"][0]]
    # `discovery` is a property of the CLASS, not of the retained circuit: a
    # class one of the older catalogues already had stays `pre-existing` however
    # much better the new circuit for it is.
    if "pre-existing" in (incumbent["discovery"], candidate["discovery"]):
        incumbent["discovery"] = "pre-existing"
    incumbent["sources"] = incumbent["sources"] + candidate["sources"]
    # Like ``sources``, credit accumulates: a class improved by a circuit from
    # another work is still the class the first work stated.  `merge` passes
    # only the citations a record NAMES, never the length defaults.
    incumbent["citations"] = incumbent["citations"] + [
        key for key in candidate["citations"]
        if key not in incumbent["citations"]]
    return incumbent


# ------------------------------------------------------------------- merging
def merge(payload, records, source_file: str):
    """Merge ``records`` into ``payload`` (mutated); return the verdict list.

    Verdicts are ``(index, verdict, row, detail)`` with ``verdict`` one of
    ``accepted`` / ``improved`` / ``duplicate`` / ``rejected``, in input order.
    Results are merged one at a time against the growing catalogue, so two
    copies of a new class inside one file behave exactly as they would in two
    files: the first is accepted and the second is its duplicate.
    """
    rows = payload["factories"]
    verdicts = []
    for index, record in enumerate(records):
        candidate, problems = candidate_row(record, payload, source_file, index)
        if candidate is None:
            verdicts.append((index, "rejected", None, problems))
            continue
        brought = list(record.get("citations") or []) \
            if isinstance(record, dict) else []
        try:
            held = find_class(rows, candidate)
        except Undecided as undecided:
            # KEEP IT.  The alternative was to refuse, and refusing throws away
            # a verified factory over a question about bookkeeping: the circuit
            # itself was re-derived and its distance proved like every other
            # row's, and the only thing unsettled is whether some existing row
            # of the same (n, k, d) is the same class up to a frame.  At the
            # widths where the search gives up -- k in the tens, gates in the
            # thousands of monomials -- that is exactly where new results are
            # hardest to come by and least replaceable.  So the row is admitted
            # and says what is unproved about it, the way a row whose canonical
            # frame was never proved says so in ``sk_key_note``.  What is NOT
            # allowed is silence: `verify_catalog.duplicate_class_problems`
            # fails an undecided pair unless one of the two carries this note.
            held = None
            candidate["dedup_note"] = (
                "distinctness from " + ", ".join(
                    f"the [[{rows[i]['n']},{rows[i]['k']},{rows[i]['d']}]] row keyed "
                    f"{rows[i]['sk_fingerprint']}" for i in undecided.rows)
                + " up to an invertible change of the output basis was not "
                  "decided: the GL(k,2) isomorphism search that decides such "
                  "pairs ran out of budget, so this row is held as a distinct "
                  "class WITHOUT that having been proved")
        if held is not None and retention_key(candidate) >= retention_key(rows[held]):
            # The CIRCUIT changes nothing -- not the columns, not ``sources``,
            # not ``regimes``: re-merging a file must be a no-op the second
            # time, and provenance accreted for a circuit that was thrown away
            # would break that.  CREDIT is different: a work that states this
            # class states it whichever circuit the catalogue keeps, so a
            # citation the record NAMES is added and registered.  The defaults
            # are not: a record that names none (the re-merge case) changes
            # nothing at all, and a class credited to a published work alone
            # stays credited to it alone.
            for key in brought:
                if key not in rows[held]["citations"]:
                    rows[held]["citations"].append(key)
                    references = payload.setdefault("references", {})
                    if key not in references:
                        references[key] = dict(DEFAULT_REFERENCES[key])
            verdicts.append((index, "duplicate", rows[held],
                             f"already held as N={rows[held]['N']}, "
                             f"d={rows[held]['d']}"))
            continue
        regime = candidate["regimes"][0]
        if regime not in payload["regimes"]:
            payload["regimes"][regime] = candidate["strongest_claim"]
        references = payload.setdefault("references", {})
        for key in candidate["citations"]:
            if key not in references:
                references[key] = dict(DEFAULT_REFERENCES[key])
        if held is None:
            rows.append(candidate)
            verdicts.append((index, "accepted", candidate, None))
        else:
            was = f"N={rows[held]['N']}, d={rows[held]['d']}"
            improve(rows[held], {**candidate, "citations": brought},
                    payload["regimes"])
            verdicts.append((index, "improved", rows[held],
                             f"was {was}, now N={candidate['N']}, "
                             f"d={candidate['d']}"))
    rows.sort(key=sort_key)
    payload["n_classes"] = len(rows)
    return verdicts


def _describe(row):
    d = row["d"] if row["d_is_exact"] else f">={row['d']}"
    return f"[[{row['n']},{row['k']},{d}]] N={row['N']} {row['gate'][:36]}"


def report(verdicts, before, after, wrote):
    """The plain-language account of what the merge did."""
    counts = {name: 0 for name in
              ("accepted", "improved", "duplicate", "rejected")}
    for _index, verdict, _row, _detail in verdicts:
        counts[verdict] += 1
    for index, verdict, row, detail in verdicts:
        if verdict == "rejected":
            print(f"  rejected   result {index}:")
            for kind, message in detail:
                print(f"               - {kind}: {message}")
        elif verdict == "accepted":
            print(f"  accepted   result {index}: {_describe(row)} "
                  f"(a class the catalogue did not have)")
        elif verdict == "improved":
            print(f"  improved   result {index}: {_describe(row)} ({detail})")
        else:
            print(f"  duplicate  result {index}: {_describe(row)} ({detail})")
    print(f"\n{len(verdicts)} result(s): "
          + ", ".join(f"{counts[name]} {name}" for name in counts))
    print(f"catalogue: {before} -> {after} classes"
          + ("" if wrote else " (nothing written: --dry-run)"))
    if wrote and (counts["accepted"] or counts["improved"]):
        print("next: master_catalog/verify_catalog.py --changed  re-verifies "
              "exactly the rows this merge changed, plus the file-level checks")
    return 1 if counts["rejected"] else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("results", type=Path,
                        help="the file of new results (see the README)")
    parser.add_argument("--catalog", type=Path, default=CF.CATALOG_JSON,
                        help="the catalogue JSON to merge into")
    parser.add_argument("--markdown", type=Path, default=None,
                        help="where to write the rendered catalogue "
                             "(default: MASTER_CATALOG.md beside the JSON)")
    parser.add_argument("--dry-run", action="store_true",
                        help="verify and report, but write nothing")
    args = parser.parse_args(argv)

    payload = CF.load(args.catalog)
    before = len(payload["factories"])
    records = read_records(args.results)
    print(f"merging {len(records)} result(s) from {args.results} into "
          f"{args.catalog.name} ({before} classes)", flush=True)

    verdicts = merge(payload, records, str(args.results))
    after = len(payload["factories"])

    # Every admitted ROW was verified on the way in, but nothing checked the
    # FILE the merge produced, and three separate defects have now escaped
    # through that gap -- a note stranded on a row the merge did not touch, a
    # note stripped from a pair that still needed it, and a duplicate rule that
    # deadlocked.  Each left merge exiting 0 on a catalogue `verify_catalog`
    # rejects, which is the one promise this tool makes.  So the file-level
    # passes run here, on the result, and nothing is written if they fail.
    residue = (VC.duplicate_class_problems(payload["factories"])
               + VC.provenance_problems(payload)
               + VC.citation_problems(payload)
               + VC.header_problems(payload))
    if residue:
        print(f"\nNOT WRITTEN: the merged catalogue fails "
              f"{len(residue)} file-level check(s):")
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        print("the catalogue on disk is unchanged.")
        return 1

    if not args.dry_run:
        CF.write(payload, args.catalog,
                 args.markdown or args.catalog.parent / CF.CATALOG_MD.name)
        VC.persist_metric_cache()
    return report(verdicts, before, after, not args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
