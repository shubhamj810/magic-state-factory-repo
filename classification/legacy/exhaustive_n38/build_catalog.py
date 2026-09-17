#!/usr/bin/env python3
"""BUILD THE n <= 38 CATALOGUE from the classification runs.

Reads every classification result in ``results/`` and consolidates them into

  * ``catalog/classification_n38.json`` -- machine-readable, one record per class
  * ``catalog/CLASSIFICATION_N38.md``   -- the same thing for humans, with the
    explicit circuit of every class

WHAT GOES IN
------------
Every ``results/quotient_catalog_*.json`` written by ``classify.py``, plus
``results/hard_parent_n31.json`` written by ``hard_parent_n31.py``.  The file
list is a glob on purpose: the classification is run in several passes (a cheap
kmax=3 pass over the whole ladder, a kmax=4 pass, the hard parent separately),
and adding a pass should not mean editing this file.

THE DEDUPLICATION KEY IS S_k
----------------------------
Two records collapse iff they have the same ``n``, the same ``k``, and gates
that agree up to a PERMUTATION of the output qubits.  See ``dedup.py`` for why
that key and not the coarser GL(k,2) one, and for the consequences when reading
row counts.

Every gate label is re-canonicalised with ``dedup.sk_canonical`` as it is read,
rather than trusted.  That matters: an early version of this pipeline emitted
labels in whatever frame the search happened to find them, so unioning raw gate
strings across files silently over-counted.  Re-canonicalising on load makes the
consolidation idempotent and immune to a stale or hand-edited input.

Among records that collapse, the one kept is the one with the largest verified
distance, and among those the one with the smallest ambient qubit count N.

WHAT IS NOT HERE
----------------
Only the exhaustive n <= 38 window.  Factories found by targeted search beyond
it live in ``../../../symmetry_sat_search/catalog/``, and the r <= 7 census lives
in ``../rank7_census/catalog/``.  Keeping the three apart is deliberate: mixing
"this is everything that exists" with "this is the best we found" in one table
is the fastest way to have a classified maximum misread as a record, or worse,
the other way round.

Run:  python build_catalog.py            (from anywhere; a few seconds)
"""
import glob
import itertools
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))          # run from anywhere: siblings by bare name
sys.path.insert(0, str(HERE.parents[2]))  # shared factorylib package

from dedup import sk_canonical, sk_canonical_with_perm, sk_name   # noqa: E402
from nezami_haah_reps import BY_WEIGHT, VALID_NS            # noqa: E402
from factorylib.metrics import metrics_from_monomials       # noqa: E402
from factorylib.verification import verify as exact_verify  # noqa: E402

RESULTS = HERE / "results"
CATALOG = HERE / "catalog"

#: Monomial degree -> the canonical diagonal gate of that arity.
LEVEL_GATE = {1: "T", 2: "CS", 3: "CCZ", 4: "CCCZ", 5: "C4Z"}

#: Width every length on the ladder must be swept to before the catalogue may
#: claim the window.  4 is what the documented passes use; width 5 occurs only
#: at n=31, whose maximally symmetric parent hard_parent_n31.py handles at
#: kmax=5.  See validate_inputs for why this is a documented requirement rather
#: than something the builder can prove from its inputs.
LADDER_KMAX = 4

#: The class the n=31 hand-off covers: the maximally symmetric parent is
#: weight-32 class 0 marked odd (all 31 nonzero points of F_2^5).  It is ONE of
#: the ten classes at n=31, which is why a coverage check counted per length
#: rather than per class read the hand-off as covering all of them.
HARD_PARENT_CLASSES = {0}

#: Width the n=31 hand-off must be swept to.  The unique [[31,5,3]] class lives
#: at width 5, and hard_parent_n31.py's --kmax defaults there; a kmax=4 run of
#: it is a perfectly good classification of the widths it enumerated and is NOT
#: an input this catalogue may be built from -- max_k would silently drop to 4
#: with no other symptom.  Checked in validate_inputs.
HARD_PARENT_KMAX = 5


# ---------------------------------------------------------------- gate naming
def parse_gate(gate):
    """``'0+01+012'`` -> ``[(0,), (0,1), (0,1,2)]`` (list of monomials)."""
    if not gate or gate in ("check-only", "0empty"):
        return []
    return [tuple(int(ch) for ch in tok) for tok in gate.split("+") if tok.strip()]


def gate_monomials(gate):
    """``'0+01'`` -> ``{frozenset({0}), frozenset({0,1})}``."""
    return {frozenset(m) for m in parse_gate(gate)}


def canonical_gate_string(k, gate):
    """The S_k-canonical label of a gate string -- the catalogue key's name."""
    return sk_name(sk_canonical(k, gate_monomials(gate)))


def gate_string(wants):
    """Render a monomial set in the catalogue's gate-string format.

    Same convention as ``sk_name``: degree 1 first, then 2, then 3, each group
    sorted, joined by ``+``.  This renders a gate WITHOUT canonicalising it, so
    it can be compared literally against a stored label.
    """
    return sk_name(tuple(sorted(tuple(sorted(Q)) for Q in wants)))


def gate_human(gate):
    """Compact human name: ``'0+1+01'`` -> ``'T0·T1·CS01'``."""
    mons = parse_gate(gate)
    if not mons:
        return "(identity)"
    by_deg = defaultdict(list)
    for m in mons:
        by_deg[len(m)].append(m)
    parts = []
    for deg in sorted(by_deg):
        g = LEVEL_GATE.get(deg, f"deg{deg}")
        for m in sorted(by_deg[deg]):
            parts.append(f"{g}{''.join(str(i) for i in m)}")
    return "·".join(parts)


def gate_family(gate):
    """Coarse label for grouping: which gate level the richest monomial reaches."""
    mons = parse_gate(gate)
    if not mons:
        return "identity"
    maxdeg = max(len(m) for m in mons)
    return {1: "T-type", 2: "CS-type", 3: "CCZ-type"}.get(maxdeg, f"deg{maxdeg}-type")


def max_level(gate):
    """Highest monomial degree present (0 for the identity)."""
    return max((len(m) for m in parse_gate(gate)), default=0)


# ------------------------------------------------------------------- loading
def input_files():
    """Every classification result this build consumes, in a stable order."""
    files = sorted(glob.glob(str(RESULTS / "quotient_catalog_*.json")))
    hard = RESULTS / "hard_parent_n31.json"
    if hard.exists():
        files.append(str(hard))
    return files


def canonicalise_columns(k, columns):
    """Relabel output qubits so the circuit deposits its S_k-canonical gate.

    The catalogue key is the S_k-canonical gate string, but a witness circuit
    realises whichever output labelling its enumeration reached.  Reading the
    gate off the columns and applying the permutation that canonicalises it
    makes the two agree LITERALLY, so ``gate`` describes the shipped circuit
    rather than merely its S_k class.  ``reverify`` then compares raw strings.

    Returns ``(columns, gate_string)``; a row without columns is passed
    through.  Check qubits (index >= k) are untouched, so ``n``, ``N``, every
    check parity and the fault distance are all unchanged -- this is a
    renaming of output wires.
    """
    if columns is None:
        return None, None
    wants = derived_gate(columns, k)
    _key, perm = sk_canonical_with_perm(k, wants)
    relabelled = [
        sorted(perm[q] if q < k else q for q in column) for column in columns
    ]
    gate = sk_name(sk_canonical(k, derived_gate(relabelled, k)))
    return relabelled, gate


def _classes_at(n):
    """The KTA/Nezami-Haah class indices a length n has parents from.

    Coverage has to be counted per class, not per length: at n=31 the ten
    classes are split between two producers, so "some pass swept n=31 at width 4"
    was satisfied by the hand-off that covers exactly one of them -- and deleting
    the pass carrying the other nine left a catalogue that still validated.
    """
    return set(range(len(BY_WEIGHT[n + n % 2])))


def _width(name, blob, problems):
    """A pass's swept width, or -1 with a problem recorded.

    Returning a number rather than whatever was in the file keeps the coverage
    comparison below total: `kmax: null` used to reach `p["kmax"] >= LADDER_KMAX`
    and raise a TypeError, which is a crash where a verdict belongs.
    """
    kmax = blob.get("kmax")
    if isinstance(kmax, int) and not isinstance(kmax, bool) and kmax >= 0:
        return kmax
    problems.append(f"{name}: kmax={kmax!r} is not a width")
    return -1


def validate_inputs(files):
    """Refuse to build unless the input passes really cover the whole window.

    The builder globs its inputs, so before this check it would happily emit a
    smaller, fully verified, self-consistent catalogue from a SUBSET of the
    passes -- deleting two of the four inputs produced a 59-class catalogue with
    ``max_k`` silently down to 4 (the [[31,5,3]] class simply gone), exit code 0,
    and a ``scope`` string still claiming every gate in the window.  Verified
    does not mean complete.

    Three things must hold, and each is read from the inputs themselves rather
    than assumed:

    1. no pass hit a node budget (``complete``, written by ``classify.py``);
    2. every CLASS of every length in ``VALID_NS`` is swept by some pass at width
       ``LADDER_KMAX`` or more.  Per class, not per length: n=31 is split between
       two producers -- the hand-off classifies the maximally symmetric parent
       (weight-32 class 0) and a ladder pass run with ``--skip-classes 0`` does
       the other nine -- so a per-length count was satisfied by the hand-off
       alone, and deleting the pass carrying nine tenths of that length still
       validated.  A deferral that is not a class index (``[null]``, or
       ``[false]`` deferring class 0 by way of ``False == 0``) is refused too,
       since it would quietly widen what the pass claims;
    3. the ``n=31`` hand-off lands: ``hard_parent_n31.py``'s result is present,
       complete, and swept to ``HARD_PARENT_KMAX`` -- a ``--kmax 4`` run of it
       is self-consistent and still drops the unique [[31,5,3]] class.

    What it cannot check is a pass that OVERSTATES its own sweep: coverage is read
    from what the passes say they did, so a file edited to drop its own deferral
    record claims the class it skipped, and only re-running the pass refutes that.
    The deferral is written by ``classify.py`` rather than inferred for exactly
    this reason.  ``tests/test_certificate_boundaries.py`` names this as the
    boundary's limit rather than leaving it to be discovered.

    What it deliberately does NOT try to certify is that ``LADDER_KMAX`` is wide
    enough.  Widths above 4 are impossible away from n=31 because ``dim V <= 4``
    there, which is a property of the parents rather than of these files -- it is
    established by the rank-partition certificate in
    ``results/n38_k56_certificate.json`` and re-derivable from
    ``nezami_haah_reps.py`` plus ``marking.py``.  Asserting it here would mean
    re-deriving every quotient dimension on every build; the per-n widths that
    were swept are recorded in the catalogue instead, so the assumption is
    visible rather than hidden.
    """
    problems = []
    passes = []
    for path in files:
        blob = json.loads(Path(path).read_text(encoding="utf-8"))
        name = os.path.basename(path)
        # hard_parent_n31.json is a different producer with its own certificate
        if name == "hard_parent_n31.json":
            if blob.get("complete") is not True:
                reasons = blob.get("incomplete_reasons")
                reasons = ("; ".join(str(r) for r in reasons)
                           if isinstance(reasons, list) and reasons
                           else "unrecorded")
                problems.append(f"{name}: complete={blob.get('complete')!r}, "
                                f"not true ({reasons})")
            hard_kmax = _width(name, blob, problems)
            if hard_kmax < HARD_PARENT_KMAX:
                problems.append(
                    f"{name}: kmax={hard_kmax}, below the {HARD_PARENT_KMAX} "
                    f"the [[31,5,3]] class needs (rerun hard_parent_n31.py "
                    f"without narrowing --kmax)")
            passes.append({"name": name, "ns": [31], "kmax": hard_kmax,
                           "deferred": {31: _classes_at(31) - HARD_PARENT_CLASSES},
                           "covers": {31: set(HARD_PARENT_CLASSES)}})
            continue
        if "complete" not in blob:
            problems.append(f"{name}: no `complete` field -- written by a "
                            f"classify.py predating the completeness fix, so "
                            f"whether it was truncated is unknown")
        elif blob["complete"] is not True:
            # `is not True`, not falsiness: `1` and `"yes"` are not this
            # producer's output, so reading them generously would only ever
            # help a hand-edited file through.
            reasons = blob.get("incomplete_reasons")
            reasons = ("; ".join(str(r) for r in reasons)
                       if isinstance(reasons, list) and reasons else "unrecorded")
            problems.append(f"{name}: complete={blob['complete']!r}, not true "
                            f"({reasons})")
        try:
            ns = blob.get("ns_swept")
            if ns is None:
                ns = sorted({int(n) for n in blob.get("stats", {})})
            ns = sorted(int(n) for n in ns)
            deferred = {}
            for key, value in (blob.get("deferred_ns") or {}).items():
                length = int(key)
                classes = set()
                for entry in value:
                    # A deferral that is not a class index silently defers
                    # NOTHING -- `[None]` subtracted no class, and `[false]`
                    # deferred class 0 by way of False == 0 -- so a pass could
                    # claim coverage it does not have through a typo.
                    if (not isinstance(entry, int) or isinstance(entry, bool)
                            or entry not in _classes_at(length)):
                        problems.append(
                            f"{name}: deferred_ns[{length}] contains {entry!r}, "
                            f"which is not a class index at n={length}")
                    else:
                        classes.add(entry)
                deferred[length] = classes
        except (AttributeError, TypeError, ValueError) as error:
            # Every field here came out of a file.  Saying which one is wrong is
            # the job; dying while reading it is not.
            problems.append(f"{name}: cannot read the swept lengths "
                            f"({type(error).__name__}: {error})")
            continue
        passes.append({"name": name, "ns": ns, "kmax": _width(name, blob, problems),
                       "deferred": deferred,
                       "covers": {n: _classes_at(n) - deferred.get(n, set())
                                  for n in ns if n in VALID_NS}})
    if not passes:
        problems.append("no input passes at all")
        return problems

    if not any(p["name"] == "hard_parent_n31.json" for p in passes):
        problems.append(
            "results/hard_parent_n31.json is missing: without it the k=5 "
            "[[31,5,3]] class is absent and max_k silently drops to 4")
    # Every class of every length must be swept by SOME pass wide enough for it.
    # Counting per class is what makes the n=31 split checkable: the hand-off
    # covers class 0 and the remainder pass covers the other nine, and dropping
    # either one now leaves classes unaccounted for by name.
    for n in sorted(VALID_NS):
        wide = [p for p in passes if p["kmax"] >= LADDER_KMAX]
        covered = set()
        for p in wide:
            covered |= p["covers"].get(n, set())
        missing = _classes_at(n) - covered
        if missing:
            reached = [p["name"] for p in wide if n in p["ns"]]
            problems.append(
                f"n={n}: classes {sorted(missing)} are not swept at width "
                f"kmax>={LADDER_KMAX} by any pass"
                + (f" (the passes reaching n={n} are {reached}, which defer them)"
                   if reached else " (no pass covers this length)"))
    return problems


def load_records():
    """Read every input file, re-canonicalise gates, and return flat records.

    Both the label and the circuit are canonicalised, so every returned record
    satisfies "the columns deposit exactly `gate`".  Nothing is trusted from
    the input file: the gate is re-read from the columns.
    """
    out = []
    for path in input_files():
        blob = json.load(open(path))
        tag = os.path.basename(path).replace(".json", "")
        for f in blob["factories"]:
            k = f["k"]
            columns, circuit_gate = canonicalise_columns(k, f.get("columns"))
            # `gate` is the S_k-canonical LABEL -- the catalogue key -- and,
            # for every row that ships a circuit, also the gate those columns
            # actually deposit.  A row without columns keeps the label alone.
            gate = circuit_gate or canonical_gate_string(k, f["gate"])
            out.append({
                "n": f["n"], "k": k, "d": f["distance"],
                "N": f.get("rows"),
                "r_checks": f.get("r"),
                "gate": gate,
                "gl_class": f.get("gate_gl_canonical"),
                "columns": columns,
                "source": tag,
            })
    return out


def dedup(records):
    """Collapse on (n, k, S_k-canonical gate); keep max distance, then min N."""
    best = {}
    for r in records:
        key = (r["n"], r["k"], r["gate"])
        prev = best.get(key)
        if prev is None:
            best[key] = r
            continue
        # distance may be an int or the string '>4'; treat '>4' as 5
        def dval(x):
            return x if isinstance(x, int) else 5
        if (dval(r["d"]), -(r["N"] or 10**9)) > (dval(prev["d"]), -(prev["N"] or 10**9)):
            best[key] = r
    return best


def enrich(rec):
    """Add the derived fields every catalogue row carries."""
    t_count, t_note, poly_deg, deg_note = metrics_from_monomials(rec["gate"])
    rec = dict(rec)
    rec.update({
        "gate_human": gate_human(rec["gate"]),
        "family": gate_family(rec["gate"]),
        "max_level": max_level(rec["gate"]),
        "t_count": t_count,
        "poly_degree": poly_deg,
        "has_circuit": rec["columns"] is not None,
    })
    if t_note:
        rec["t_count_note"] = t_note
    if deg_note:
        rec["poly_degree_note"] = deg_note
    return rec


def derived_gate(columns, k):
    """Read the logical gate straight off the stored columns.

    A monomial Q over the output qubits is present iff an ODD number of columns
    contain all of Q.  This is the definition of what the circuit deposits, and
    it is computed here from the column list alone -- nothing is taken from the
    record.
    """
    cols = [set(c) for c in columns]

    def parity(qs):
        qs = set(qs)
        return sum(1 for c in cols if qs <= c) & 1

    out = set()
    for deg in (1, 2, 3):
        for T in itertools.combinations(range(k), deg):
            if parity(T):
                out.add(frozenset(T))
    return out


def reverify(rec):
    """Independently re-check one row's circuit.  Returns None if the row has
    no circuit, '' if it verifies, else a failure string.

    Three things are checked, all from the raw columns:

      1. the gate the columns actually deposit equals the catalogued gate
         label, as a STRING -- no permutation allowed;
      2. every degree-<=3 parity that touches a check qubit is even -- the
         factory condition;
      3. the exact fault distance equals the stored d.

    Check (1) is a literal string comparison because ``load_records`` has
    already relabelled every witness into its canonical output frame
    (``canonicalise_columns``).  Comparing up to S_k instead -- as this
    function used to -- would also pass rows whose stored label and stored
    circuit disagree about which output carries which monomial.  Checks (2)
    and (3) use ``factorylib.verification``, which shares no code with the
    classification engine.
    """
    if not rec["has_circuit"]:
        return None
    cols = [frozenset(c) for c in rec["columns"]]
    k, N = rec["k"], rec["N"]

    wants = derived_gate(cols, k)
    got = gate_string(wants)
    if got != rec["gate"]:
        return f"circuit deposits {got}, catalogued as {rec['gate']}"

    # verify() against the DERIVED gate: parity_ok is then exactly the statement
    # that nothing is deposited on any check qubit.
    ok, dist = exact_verify(k, N, cols, wants, dmax=4)
    if not ok:
        return "a check-touching parity is odd (circuit deposits on a check)"
    dval = dist if isinstance(dist, int) else 5
    stored = rec["d"] if isinstance(rec["d"], int) else 5
    if dval != stored:
        return f"distance {dist} != stored {rec['d']}"
    return ""


def build(verify_rows=True):
    """Load, dedup, enrich, optionally re-verify.  Returns the sorted rows."""
    files = input_files()
    if not files:
        raise SystemExit(
            f"no classification results in {RESULTS}. Run classify.py first "
            f"(see README.md, 'Reproduce the catalogue').")
    print("inputs:")
    for f in files:
        print(f"  {os.path.relpath(f, HERE)}")
    problems = validate_inputs(files)
    if problems:
        print("\nthe input passes do not cover the n <= 38 window:")
        for problem in problems:
            print(f"  - {problem}")
        raise SystemExit(
            "catalogue build aborted: this would publish a verified but "
            "INCOMPLETE catalogue whose scope string claims the whole window. "
            "Re-run the missing passes (see README.md, 'Reproduce') or, for a "
            "deliberate partial build, say so in the scope yourself.")
    raw = load_records()
    best = dedup(raw)
    rows = [enrich(r) for r in best.values()]
    rows.sort(key=lambda r: (r["k"], r["n"], r["max_level"], r["gate"]))
    print(f"\n{len(raw)} records read -> {len(rows)} distinct (n, k, S_k gate) classes")

    if verify_rows:
        failures = []
        checked = 0
        for r in rows:
            msg = reverify(r)
            if msg is None:
                continue
            checked += 1
            if msg:
                failures.append((r["n"], r["k"], r["gate"], msg))
        print(f"{checked - len(failures)}/{checked} circuits independently "
              f"re-verified (parity + exact fault distance)")
        if failures:
            for n, k, g, msg in failures:
                print(f"  FAIL [[{n},{k},?]] {g}: {msg}")
            raise SystemExit("catalogue build aborted: a stored circuit does "
                             "not reproduce its stated parameters")
    return rows


# ------------------------------------------------------------------ rendering
def cols_str(columns):
    """Columns as ``[{0,1,2}, {0,3}, ...]`` for the markdown circuit blocks."""
    return "[" + ", ".join("{" + ",".join(str(i) for i in c) + "}"
                           for c in columns) + "]"


def render_markdown(rows):
    """Full text of catalog/CLASSIFICATION_N38.md."""
    lines = []
    A = lines.append
    A("# Exhaustive distance-≥3 classification, `n ≤ 38`")
    A("")
    A("Every distinct logical gate realisable by a reduced distance-≥3 factory")
    A("with at most 38 physical injections, together with an explicit verified")
    A("circuit for each. Generated by [`build_catalog.py`](../build_catalog.py)")
    A("from the runs in [`../results/`](../results/) — **do not edit by hand**.")
    A("")
    A("Machine-readable companion: [`classification_n38.json`](classification_n38.json).")
    A("")
    A("## What \"exhaustive\" means here")
    A("")
    A("For each classified triorthogonal check-part support at physical length")
    A("`n ≤ 38` (the Kasami–Tokura / Nezami–Haah affine class representatives in")
    A("[`../nezami_haah_reps.py`](../nezami_haah_reps.py)), **every** way of")
    A("attaching output rows was enumerated in the quotient `V = R(C)/C`. No")
    A("target was requested and no node budget was consumed: the table answers")
    A("\"which gates exist *at all* at this T-count and distance\", not \"can we")
    A("find gate X\".")
    A("")
    A("### The precise scope of the word \"exhaustive\"")
    A("")
    A("The enumeration covers factories whose `k` output rows are linearly")
    A("independent **modulo the check span `C`**. Frames whose rows collapse")
    A("mod `C` — one output `a`, another `a + c` for a check-span element `c` —")
    A("are not enumerated.")
    A("")
    A("**This costs no magic.** Such a frame is a real circuit, and its gate is")
    A("genuinely different (`0+1+01`, i.e. `T₀·T₁·CS₀₁`). But one output CNOT")
    A("turns the second row into `c` itself, which carries no monomial of any")
    A("degree — `|c|` is even, `|c ∧ a'|` is even for every `a'` in `R(C)`, and")
    A("`|c ∧ a' ∧ a''|` is even for every compatible pair. So after one Clifford")
    A("the extra output is an idle `|+⟩` spectator and what remains is exactly")
    A("the lower-width factory that *is* in this table. The arithmetic agrees:")
    A("`T₀·T₁·CS₀₁` has exact minimal T-count **1**, not 2, because")
    A("`x₀ + x₁ + 2x₀x₁ = (x₀ ⊕ x₁) + 4x₀x₁` — one T on the parity of the two")
    A("outputs, times a CZ.")
    A("")
    A("So this catalogue is complete for magic **content** — which gates are")
    A("achievable at each `n`, the largest genuine output width, the largest")
    A("exact T-count. It is incomplete only for circuit **representations** in")
    A("which an output is Clifford-equivalent to an idle spectator. The engine")
    A("already discards frames with a manifestly idle output, so this is the")
    A("same policy one Clifford deeper rather than a different one.")
    A("")
    A("If you are counting distinct circuits rather than distinct resources,")
    A("[`../classify_rowspace.py`](../classify_rowspace.py) enumerates in the")
    A("full row space and does reach them. A concrete example is the")
    A("`[[15,2,3]]` with gate `0+1+01` over the `[[15,1,3]]` check part: 6 rows")
    A("of rank 5, exact T-count 1. It is deliberately absent from the search")
    A("catalogue, which rejects a width whose output rows are dependent modulo")
    A("the check span — one CNOT leaves the second output idle, so the circuit is")
    A("the `[[15,1,3]]` on a spare wire. See")
    A("[`../../../../symmetry_sat_search/examples/README.md`](../../../../symmetry_sat_search/examples/README.md).")
    A("")
    A("The one maximally symmetric parent — the 31 nonzero points of `F₂⁵`, whose")
    A("automorphism group is all of `GL(5,2)` — is settled separately by")
    A("[`../hard_parent_n31.py`](../hard_parent_n31.py), which collapses the")
    A("search along that group instead of enumerating through it.")
    A("")
    A("## Deduplication: the key is S_k")
    A("")
    A("Rows are deduplicated by `(n, k, gate up to a PERMUTATION of the output")
    A("qubits)`. Not up to `GL(k,2)`, which is strictly coarser and would merge")
    A("rows. Each row also carries its `GL(k,2)` class as an annotation, so a")
    A("`GL(k,2)` census can be recovered by grouping on that field without")
    A("re-running anything. [`../dedup.py`](../dedup.py) explains the choice and")
    A("its consequences in full; the short version is that a CNOT frame change on")
    A("the outputs produces a *different circuit* with a *different phase")
    A("polynomial*, and this is a construction catalogue.")
    A("")
    A("**Row counts are upper bounds on class counts.** A raw gate string is a")
    A("representation, not an invariant. Maxima — largest `k`, largest `T`, which")
    A("gates occur at a given `n` — are unaffected.")
    A("")
    A("## Notation")
    A("")
    A("An output gate is a phase polynomial over F₂ monomials in the output qubits")
    A("`0..k-1`: degree 1 is a `T`, degree 2 a `CS`, degree 3 a `CCZ`. So")
    A("`0+1+01` = `T₀·T₁·CS₀₁`. `T` is the exact minimal T-count of the deposited")
    A("gate (Amy–Mosca / Reed–Muller minimum-weight coset over ℤ₈); `deg` is the")
    A("CNOT-frame-reduced phase-polynomial degree, minimised over output frames in")
    A("`GL(k,2)`. `N` = ambient circuit qubits = `k` outputs + checks.")
    A("")
    fam = defaultdict(int)
    for r in rows:
        fam[r["family"]] += 1
    kmax = max(r["k"] for r in rows)
    tmax = max((r["t_count"] for r in rows if r["t_count"] is not None), default=0)
    A(f"**{len(rows)} classes**, all with explicit circuits"
      if all(r["has_circuit"] for r in rows) else
      f"**{len(rows)} classes** "
      f"({sum(1 for r in rows if r['has_circuit'])} with explicit circuits)")
    A("")
    A("### Headline findings")
    A("")
    A(f"- Gate content: **{fam['T-type']}** T-only, **{fam['CS-type']}** CS-level,")
    A(f"  **{fam['CCZ-type']}** CCZ-level classes.")
    A("- **Pure `CCZ` (the monomial `012` alone) never occurs for `n ≤ 38`.**")
    A("  Inside this window CCZ content appears only inside fully-symmetric")
    A("  degree-≤3 combinations. This table *is* the witness for the `CCZ ≥ 39`")
    A("  distance-3 lower bound.")
    A(f"- Maximum output width in the window: **k = {kmax}**.")
    A(f"- Highest exact minimal T-count: **T = {tmax}**.")
    A("")

    # ---- Section 1: one row per [[n,k,d]]
    A("## 1. Gates per `[[n,k,d]]`")
    A("")
    A("| `[[n,k,d]]` | N | # classes | output gates |")
    A("|---|---|---|---|")
    bynkd = defaultdict(list)
    for r in rows:
        bynkd[(r["n"], r["k"], r["d"])].append(r)
    for (n, k, d) in sorted(bynkd):
        grp = sorted(bynkd[(n, k, d)], key=lambda r: (r["max_level"], r["gate"]))
        Ns = sorted({r["N"] for r in grp if r["N"] is not None})
        Nstr = (str(Ns[0]) if len(Ns) == 1 else
                (f"{min(Ns)}–{max(Ns)}" if Ns else "—"))
        names = ", ".join(f"`{r['gate_human']}`" for r in grp)
        A(f"| [[{n},{k},{d}]] | {Nstr} | {len(grp)} | {names} |")
    A("")

    # ---- Section 2: smallest n per gate
    A("## 2. Gate frontier — smallest `n` realising each gate")
    A("")
    A("| gate | human | k | min n | N | d | T | deg | GL(k,2) class |")
    A("|---|---|---|---|---|---|---|---|---|")
    best = {}
    for r in rows:
        key = (r["k"], r["gate"])
        cur = (r["n"], r["N"] or 10**9)
        if key not in best or cur < (best[key]["n"], best[key]["N"] or 10**9):
            best[key] = r
    for key in sorted(best, key=lambda kk: (kk[0], best[kk]["n"], best[kk]["max_level"])):
        r = best[key]
        A(f"| `{r['gate']}` | `{r['gate_human']}` | {r['k']} | {r['n']} | "
          f"{r['N'] if r['N'] is not None else '—'} | {r['d']} | "
          f"{'n/a' if r['t_count'] is None else r['t_count']} | "
          f"{r['poly_degree']} | "
          f"{r['gl_class'] if r['gl_class'] is not None else '—'} |")
    A("")

    # ---- Section 3: the full catalogue with circuits
    A("## 3. Full catalogue with explicit circuits")
    A("")
    A("Columns are the qubit supports of each parity-`T` rotation; qubits")
    A("`0..k-1` are the outputs, the rest are postselected checks.")
    A("")
    for i, r in enumerate(rows, 1):
        A(f"### {i}. `[[{r['n']},{r['k']},{r['d']}]]` — {r['gate_human']}")
        A("")
        A(f"- output gate (phase polynomial): `{r['gate']}`")
        A(f"- exact minimal T-count = "
          f"{'n/a' if r['t_count'] is None else r['t_count']}, "
          f"reduced phase-polynomial degree = {r['poly_degree']}")
        A(f"- N = {r['N'] if r['N'] is not None else '—'}, "
          f"checks = {r['r_checks'] if r['r_checks'] is not None else '—'}, "
          f"family = {r['family']}, GL(k,2) class = "
          f"{r['gl_class'] if r['gl_class'] is not None else '—'}")
        A(f"- source run: `{r['source']}`")
        if r["has_circuit"]:
            A("")
            A("```")
            A(cols_str(r["columns"]))
            A("```")
        else:
            A("- circuit: not stored")
        A("")
    return "\n".join(lines)


def main():
    rows = build()
    CATALOG.mkdir(parents=True, exist_ok=True)
    payload = {
        "scope": "every distinct logical gate realisable by a reduced "
                 "distance >= 3 factory with n <= 38, from the exhaustive "
                 "quotient R(C)/C classification over the Kasami-Tokura / "
                 "Nezami-Haah check-support classes",
        "dedup_key": "(n, k, S_k-canonical gate) -- output-qubit PERMUTATIONS "
                     "only, not GL(k,2). The coarser GL(k,2) class is stored "
                     "per row as gl_class. See dedup.py.",
        "caveat": "a raw gate string is a representation, not an invariant, so "
                  "row counts are upper bounds on the number of inequivalent "
                  "gates; maxima are unaffected",
        "scope_limitation": "Enumerates factories whose k output rows are "
                            "linearly independent MODULO the check span C. "
                            "Frames that collapse mod C are real circuits "
                            "(gate 0+1+01) which the quotient method cannot "
                            "represent, but they carry no extra magic: one "
                            "output CNOT makes the extra output an idle "
                            "spectator, and 0+1+01 has exact minimal T-count 1. "
                            "So this catalogue is complete for magic content "
                            "and incomplete only for circuit representations. "
                            "See classify.py, section SCOPE.",
        "inputs": [os.path.basename(f) for f in input_files()],
        "n_classes": len(rows),
        "n_with_circuit": sum(1 for r in rows if r["has_circuit"]),
        "max_k": max(r["k"] for r in rows),
        "factories": rows,
    }
    out_json = CATALOG / "classification_n38.json"
    with open(out_json, "w") as fh:
        json.dump(payload, fh, indent=1)
        fh.write("\n")
    out_md = CATALOG / "CLASSIFICATION_N38.md"
    out_md.write_text(render_markdown(rows))
    print(f"\n  -> {out_json.relative_to(HERE)}")
    print(f"  -> {out_md.relative_to(HERE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
