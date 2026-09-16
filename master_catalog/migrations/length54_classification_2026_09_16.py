#!/usr/bin/env python3
"""One-off migration: merge the length-54 classification and re-credit its classes.

    python master_catalog/migrations/length54_classification_2026_09_16.py [--dry-run]

Run after `distance_certificates_2026_09_16.py`.  Refuses to run twice.

The exhaustive classification of generalised triorthogonal protocols through
length 54 (Wills, Jain and Singh) publishes its Pareto frontier: 74 protocols,
one for every output class, exact distance and undominated ``(n, S)``.  A copy
is in `classification/length54/pareto_frontier.json`.  This script does four
things, and nothing else.

1.  **Regimes say how a class was found.**  The corpus names the catalogue
    grew up with are replaced by short descriptions of the method:

    * the repository's exhaustive ``n <= 38`` classification and rank-7 census
      are stages of the length-54 classification and become
      ``exhaustive classification n<=54`` -- or, on a Pareto point, the
      stronger ``exhaustive classification n<=54 (Pareto point)``;
    * ``search record`` is the symmetry-slot / SAT search, and the AI corpora
      (``AI results``, ``catalogue_new``, the magic-states-AI master
      catalogue) are one ``AI search``; the named AI campaigns keep a brief
      description of their method;
    * the gamma frontier release is split by the construction each of its
      records names (``origin``): parents from Wills's constructions, paired-
      column contractions of existing codes, logical restrictions of a length-54
      Pareto point, and one punctured Reed-Muller code.  Its two records that the release itself says
      it took from the classification (``classified_direct_protocol_*``) are
      credited to the classification.

    A row's ``regimes`` are re-derived from its sources and ``strongest_claim``
    from the header.  ``discovery`` keeps its meaning -- was the class an AI
    discovery? -- so it is read from the sources, not the relabelled regimes:
    ``AI search`` exactly when an AI search or search release found the class
    and neither a classification stage this repository ran before them nor
    the symmetry-SAT search did.  The script checks that this reproduces every
    held row's tag before it changes anything, so the only rows whose tag moves
    are the two gamma records that were the classification's own.  A Pareto
    point our searches had already found stays ``AI search``; one only the
    classification has is ``pre-existing``.

2.  **The frontier is merged**, each protocol put through
    `merge_results.candidate_row` -- the bar every row meets.  A class not held
    is appended; a held class whose circuit uses more wires is improved to the
    classification's; a held class with the same circuit cost gains the
    classification as a source, exactly as `attribute_classification.py`
    credits a classification on a row it certifies.  A held circuit with FEWER
    wires than a Pareto point would contradict the classification and stops
    the script.

3.  **The 74 are re-credited**, as the catalogue's owner set out:

    * a class the classification's Pareto table (Table ``tab:complete-pareto``)
      attributes to a published protocol is credited to that work ONLY;
    * otherwise, a class this project's own searches had found (a symmetry-SAT
      or AI-search source on the held row) is credited to the classification
      and to the symmetry-and-AI report;
    * every other Pareto point is credited to the classification alone.

    No other row's ``citations`` change.

4.  **References get links.**  Every published work carries a ``url``
    (a DOI where the work has one, else its arXiv page), which the rendered
    table uses for the citation.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOGUE = HERE.parent
REPO = CATALOGUE.parent
sys.path.insert(0, str(CATALOGUE))
sys.path.insert(0, str(HERE))

import catalogfile as CF                                          # noqa: E402
import merge_results as MR                                        # noqa: E402
import verify_catalog as VC                                       # noqa: E402
import literature_citations_2026_09_15 as LIT                     # noqa: E402

FRONTIER_FILE = "classification/length54/pareto_frontier.json"

PARETO = "exhaustive classification n<=54 (Pareto point)"
CLASSIFIED = "exhaustive classification n<=54"
SAT = "symmetry-SAT search"
AI = "AI search"
AI_SIMPLEX = "AI search: punctured r=7 simplex parents"
AI_MULTI = "AI search: multi-agent campaign 39<=n<=127"
G_WILLS = "AI search (gamma frontier): from Wills parent codes"
G_CONTRACT = "AI search (gamma frontier): contraction of an existing code"
G_RESTRICT = ("AI search (gamma frontier): logical restriction of a length-54 "
              "Pareto point")
G_RM = "AI search (gamma frontier): punctured Reed-Muller code"
DOWNSET = "AI search: Wills downset framework"
WIDTH = "AI search: pure-T width campaign n=255, 511"
RELEASE = "search release 55<=n<=64"
CAPS = "AI search: pure-T puncture caps"
FRAMES = "AI search: full-simplex pure-T frames"

GAMMA_TAIL = ("in the pure-T distillation-exponent release (gamma = "
              "log(n/k)/log d, n < 1000); a verified witness, not a maximum -- "
              "only the release's own frontier points are the lowest gamma it "
              "knows")


def build_header(old):
    """The new regime map, strongest claim first, reusing unchanged sentences."""
    return {
        PARETO: ("a Pareto point of the exhaustive classification of generalised "
                 "triorthogonal protocols through length 54 (classification/"
                 "length54/): no protocol with n <= 54, the same CNOT+S output "
                 "class and the same exact distance has n and S both no larger "
                 "and one of them smaller, where S counts every matrix row -- "
                 "the N of this table"),
        CLASSIFIED: ("found within the exhaustive classification through length "
                     "54 but not one of its Pareto points: a Pareto point with "
                     "the same output class (after removing spectator outputs) "
                     "and the same exact distance strictly dominates it, which "
                     "tests/test_master_catalog.py checks -- a verified "
                     "witness, not an optimum"),
        SAT: ("found by the symmetry-slot or ansatz-free SAT search "
              "(symmetry_sat_search/); a verified witness, not a maximum"),
        AI: "found by an AI search campaign; a verified witness, not a maximum",
        AI_SIMPLEX: ("found by the 48 < n < 128 AI campaigns, from punctured r=7 "
                     "simplex parents with free-row appending; a verified "
                     "witness, not a maximum"),
        AI_MULTI: ("found by the 39 <= n <= 127 multi-actor AI campaign (three "
                   "Opus 5 actors, two conferring Fable 5 reviewers, three "
                   "rounds, 2026-09-01); a verified witness, not a maximum"),
        G_WILLS: ("built from one of Wills's parent codes (weighted Reed-Muller, "
                  "restricted-light or one-heavy) by searched punctures, "
                  "paired-column contractions or logical-pair checks, "
                  + GAMMA_TAIL),
        G_CONTRACT: ("a paired-column contraction of an existing triorthogonal "
                     "code, " + GAMMA_TAIL),
        G_RESTRICT: ("a restriction to fewer logical rows of a Pareto point of "
                     "the length-54 classification, " + GAMMA_TAIL),
        G_RM: ("a punctured Reed-Muller code found by the gamma sub-1000 AI "
               "campaign (RM(3,10) punctured at 123 points), filed with the "
               "pure-T distillation-exponent frontier (gamma = log(n/k)/log d, "
               "n < 1000); a verified witness, not a maximum"),
        DOWNSET: old["campaign wills downset framework"],
        WIDTH: old["magic-states-AI 255_511_width campaign (2026-09-14)"],
        RELEASE: old["public release 55<=n<=64"],
        CAPS: old["pure_T"],
        FRAMES: old["n2exp_minus1_full_simplex_pureT"],
    }


RENAMES = {
    "exhaustive n<=38": CLASSIFIED,
    "census r<=7": CLASSIFIED,
    "search record": SAT,
    "AI results": AI,
    "catalogue_new": AI,
    "magic-states-AI master catalogue": AI,
    "campaign 48<n<128": AI_SIMPLEX,
    "campaign 39<=n<=127": AI_MULTI,
    "campaign wills downset framework": DOWNSET,
    "magic-states-AI 255_511_width campaign (2026-09-14)": WIDTH,
    "public release 55<=n<=64": RELEASE,
    "pure_T": CAPS,
    "n2exp_minus1_full_simplex_pureT": FRAMES,
}
GAMMA = "gamma frontier"

#: The regimes of this project's own searches, for the citation rule.
OUR_SEARCHES = (SAT, AI, AI_SIMPLEX, AI_MULTI, G_WILLS, G_CONTRACT, G_RESTRICT,
                G_RM, DOWNSET, WIDTH, CAPS, FRAMES)
#: The regimes that make a class an AI discovery, absent an earlier catalogue.
AI_FOUND = tuple(r for r in OUR_SEARCHES if r != SAT) + (RELEASE,)
#: The classification stages this repository ran itself -- every catalogue under
#: ``classification/`` except the copied length-54 frontier.
EARLY_STAGES = "classification/"
FRONTIER_DIR = "classification/length54/"

DISCOVERY = {
    "pre-existing": ("not an AI discovery: a classification stage this "
                     "repository ran, the symmetry-SAT search catalogue, or "
                     "only the exhaustive length-54 classification has this "
                     "class"),
    "AI search": ("found by an AI search campaign or a search release, and by "
                  "no classification stage this repository ran and no "
                  "symmetry-SAT search (the length-54 classification may have "
                  "it too); whether it was new to the literature is what "
                  "citations says"),
}
SCOPE = ("every Clifford level-3, distance >= 3 factory this collection holds, "
         "deduplicated on (n, k, d, GL(k,2) class of the gate); rows arrive from "
         "the exhaustive length-54 classification and from search campaigns "
         "merged in by merge_results.py")
CAVEAT = ("rows keep the regime they came from: a Pareto point of the length-54 "
          "classification is an optimality statement, a search witness is not. "
          "This table is their union, not a uniform claim.")

#: Links for every published work: the DOI where there is one, else arXiv.
#: Each was resolved and its title checked against ``full`` on 2026-09-16.
URLS = {
    "bravyi2005universal": "https://doi.org/10.1103/PhysRevA.71.022316",
    "nezami2022classification": "https://doi.org/10.1103/PhysRevA.106.012437",
    "jacinto2026exploring": "https://arxiv.org/abs/2606.07734",
    "gong2026magic": "https://arxiv.org/abs/2608.09727",
    "haah2018codes": "https://doi.org/10.22331/q-2018-06-07-71",
    "vuillot2022quantum": "https://doi.org/10.1109/TIT.2022.3170846",
    "rengaswamy2020optimality": "https://doi.org/10.1109/JSAIT.2020.3012914",
    "gong2024computation": "https://arxiv.org/abs/2410.23263",
    "shi2024triorthogonal": "https://doi.org/10.1007/s11128-024-04485-9",
}
UNPUBLISHED = ("wills2026classification", "jain2026symmetry")


def gamma_regime(source):
    """The regime a gamma frontier source is, from the construction it names."""
    label, origin = source.get("label") or "", source.get("origin") or ""
    if label.startswith("classified_direct_protocol_"):
        return PARETO
    if label.startswith("logical_restriction_"):
        return G_RESTRICT
    # the release's weighted_sources records name no construction ("Triorthogonal;
    # matrix verified"), but their recipes cite Wills, arXiv:2608.24000, Prop. 3.7
    if "Wills" in origin or label.startswith("weighted_sources_"):
        return G_WILLS
    if origin.startswith(("Existing triorthogonal code", "Haah")):
        return G_CONTRACT
    if "RM(3,10) punctured" in (source.get("provenance") or ""):
        return G_RM
    raise SystemExit(f"gamma frontier source {label!r} names no construction "
                     f"this script knows; refusing to guess its regime")


def frontier_records(path=REPO / FRONTIER_FILE):
    data = json.loads(path.read_text())
    outputs = {o["output_id"]: o for o in data["outputs"]}
    records = []
    for p in data["protocols"]:
        rows = p["generator_matrix_rows"]
        S, n = len(rows), len(rows[0])
        output = outputs[p["output_id"]]
        records.append((p, {
            "k": p["q"], "N": S, "n": n, "d": p["d_Z"],
            "columns": [[i for i in range(S) if rows[i][j] == "1"]
                        for j in range(n)],
            "regime": PARETO, "discovery": "pre-existing",
            "file": FRONTIER_FILE, "label": f"protocol {p['index']}",
            "origin": ("exhaustive classification of generalised triorthogonal "
                       "protocols through length 54 (Wills, Jain and Singh)"),
            "provenance": (f"Pareto point {p['index']} of the length-54 "
                           f"classification: output class {p['output_id']} "
                           f"({output['factorised_representative_gate']}), "
                           f"(n, S, d_Z) = ({n}, {S}, {p['d_Z']}), leading "
                           f"error coefficient {p['error_coefficient']}; the "
                           f"outputs are its {p['q']} logical rows"),
        }))
    return records


def relabel(payload):
    """Rename every row's and source's regime; return the gamma split counts."""
    old = payload["regimes"]
    unknown = set(old) - set(RENAMES) - {GAMMA}
    if unknown:
        raise SystemExit(f"regimes this script does not know: {sorted(unknown)}")
    payload["regimes"] = build_header(old)
    counts = collections.Counter()
    for row in payload["factories"]:
        for source in row["sources"]:
            was = source["regime"]
            source["regime"] = (gamma_regime(source) if was == GAMMA
                                else RENAMES[was])
            counts[(was, source["regime"])] += 1
    return counts


def discovery_of(row):
    """``AI search`` iff an AI search found it and no earlier catalogue had it."""
    early = any(s["regime"] == SAT
                or (s["file"].startswith(EARLY_STAGES)
                    and not s["file"].startswith(FRONTIER_DIR))
                for s in row["sources"])
    found = any(s["regime"] in AI_FOUND for s in row["sources"])
    return "AI search" if found and not early else "pre-existing"


def settle(payload, row):
    """``regimes``, ``strongest_claim`` and ``discovery`` from the sources."""
    header = payload["regimes"]
    order = list(header)
    row["regimes"] = sorted({s["regime"] for s in row["sources"]},
                            key=order.index)
    row["strongest_claim"] = header[row["regimes"][0]]
    row["discovery"] = discovery_of(row)


def migrate(payload):
    if PARETO in payload["regimes"]:
        raise SystemExit("the length-54 classification is already merged")
    rows = payload["factories"]
    before = {id(row): (row["discovery"], list(row["citations"])) for row in rows}

    # --- 1. every frontier record through the catalogue's own bar, against the
    # catalogue as it stands (classes are independent of regime names)
    candidates = []
    for p, record in frontier_records():
        candidate, problems = MR.candidate_row(record, payload, FRONTIER_FILE,
                                               p["index"])
        if candidate is None:
            raise SystemExit(f"Pareto point {p['index']} does not verify: "
                             f"{problems}")
        if (candidate["d"], candidate["d_is_exact"]) != (p["d_Z"], True):
            raise SystemExit(f"Pareto point {p['index']}: measured "
                             f"d={candidate['d']} (exact={candidate['d_is_exact']})"
                             f", the classification says exactly {p['d_Z']}")
        held = MR.find_class(rows, candidate)           # Undecided propagates
        candidates.append((p, candidate, None if held is None else rows[held]))

    # --- 2. regimes describe how a class was found.  The discovery rule is
    # checked against every held tag first: it must reproduce all of them
    # except on rows whose sources the release took from the classification.
    renamed = relabel(payload)
    for row in rows:
        if discovery_of(row) != row["discovery"] and not any(
                s["label"].startswith("classified_direct_protocol_")
                for s in row["sources"]):
            raise SystemExit(f"[[{row['n']},{row['k']},{row['d']}]] is tagged "
                             f"{row['discovery']!r} but its sources say "
                             f"{discovery_of(row)!r}")
        settle(payload, row)

    # --- 3. merge
    verdicts = collections.Counter()
    pareto_rows = {}
    for p, candidate, held in candidates:
        candidate["regimes"] = [PARETO]
        candidate["strongest_claim"] = payload["regimes"][PARETO]
        ours = held is not None and any(s["regime"] in OUR_SEARCHES
                                        for s in held["sources"])
        if held is None:
            rows.append(candidate)
            row, verdict = candidate, "accepted"
        elif MR.retention_key(candidate) < MR.retention_key(held):
            was = held["N"]
            MR.improve(held, candidate, payload["regimes"])
            row, verdict = held, f"improved (N {was} -> {held['N']})"
        else:
            if candidate["N"] != held["N"]:
                raise SystemExit(f"Pareto point {p['index']} has S={candidate['N']}"
                                 f" but the catalogue holds its class with "
                                 f"N={held['N']}: the classification says no "
                                 f"such circuit exists")
            held["sources"].append(candidate["sources"][0])
            if "columns_note" in held and held["N"] in [s["N"] for s in
                                                        held["sources"]]:
                # the note said no source published this N; the
                # classification now does, and a note explaining nothing is
                # what `verify_catalog._circuit_provenance_problems` refuses
                held.pop("columns_note")
            row, verdict = held, "held"
        if id(row) in pareto_rows:
            raise SystemExit(f"Pareto points {pareto_rows[id(row)][0]['index']} "
                             f"and {p['index']} land on one row")
        pareto_rows[id(row)] = (p, ours, verdict)
        verdicts[verdict.split(" ")[0]] += 1

    # --- 4. classification stages on a Pareto row are that Pareto point
    for row in rows:
        on_frontier = id(row) in pareto_rows
        for source in row["sources"]:
            if source["regime"] == CLASSIFIED and on_frontier:
                source["regime"] = PARETO
            if source["regime"] == PARETO and not on_frontier:
                raise SystemExit(f"[[{row['n']},{row['k']},{row['d']}]] has a "
                                 f"source crediting a Pareto point, but no "
                                 f"Pareto point is this class")
        settle(payload, row)

    # --- 5. citations of the 74
    literature = collections.defaultdict(list)
    for n, k, d, gate, keys, where in LIT.LITERATURE:
        if n > MR.CLASSIFICATION_LENGTH:
            continue
        hits = [row for row in rows if LIT.matches(row, n, k, d, gate)]
        if len(hits) != 1 or id(hits[0]) not in pareto_rows:
            raise SystemExit(f"[[{n},{k},{d}]] ({where}) matches {len(hits)} "
                             f"rows, not exactly one Pareto point")
        literature[id(hits[0])] += [key for key in keys
                                    if key not in literature[id(hits[0])]]
    credit = collections.Counter()
    for row in rows:
        if id(row) not in pareto_rows:
            continue
        _p, ours, _verdict = pareto_rows[id(row)]
        if literature[id(row)]:
            row["citations"], kind = list(literature[id(row)]), "literature"
        elif ours:
            row["citations"] = ["wills2026classification", "jain2026symmetry"]
            kind = "classification + our searches"
        else:
            row["citations"], kind = ["wills2026classification"], "classification"
        credit[kind] += 1
        pareto_rows[id(row)] += (kind,)

    # --- 6. references, with links
    references = payload["references"]
    for key, url in URLS.items():
        if key in references:
            references[key]["url"] = url
    used = {key for row in rows for key in row["citations"]}
    missing = [key for key in used
               if key not in references and key not in UNPUBLISHED]
    if missing:
        raise SystemExit(f"citations with no reference entry: {missing}")
    ordered = {key: dict(MR.DEFAULT_REFERENCES[key]) for key in UNPUBLISHED
               if key in used}
    ordered.update({key: entry for key, entry in references.items()
                    if key in used and key not in ordered})
    payload["references"] = ordered

    payload["discovery"] = dict(DISCOVERY)
    payload["scope"] = SCOPE
    payload["caveat"] = CAVEAT
    rows.sort(key=MR.sort_key)
    payload["n_classes"] = len(rows)

    changed_discovery = [row for row in rows if id(row) in before
                         and before[id(row)][0] != row["discovery"]]
    if any(not any(s["label"].startswith("classified_direct_protocol_")
                   for s in row["sources"]) for row in changed_discovery):
        raise SystemExit("a held row's discovery tag moved for a reason other "
                         "than a gamma record taken from the classification")
    changed_citations = [row for row in rows if id(row) in before
                         and id(row) not in pareto_rows
                         and before[id(row)][1] != row["citations"]]
    if changed_citations:
        raise SystemExit("a row off the frontier changed its citations")
    return dict(verdicts=verdicts, credit=credit, renamed=renamed,
                pareto_rows=pareto_rows, changed_discovery=changed_discovery,
                rows=rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load()
    before = len(payload["factories"])
    result = migrate(payload)
    print("regimes (old -> new, source entries):")
    for (was, now), count in sorted(result["renamed"].items()):
        print(f"  {count:>5}  {was!r} -> {now!r}")
    print(f"\nPareto points: " + ", ".join(
        f"{count} {verdict}" for verdict, count in result["verdicts"].items()))
    print("citations of the 74: " + ", ".join(
        f"{count} {kind}" for kind, count in result["credit"].items()))
    for row in result["rows"]:
        entry = result["pareto_rows"].get(id(row))
        if entry is None:
            continue
        p, ours, verdict, kind = entry
        print(f"  #{p['index']:>2} [[{row['n']},{row['k']},{row['d']}]] "
              f"N={row['N']:<3} {verdict:<22} {kind:<30} "
              f"{', '.join(row['citations'])}")
    print(f"\ndiscovery changed on {len(result['changed_discovery'])} held rows: "
          + "; ".join(f"[[{r['n']},{r['k']},{r['d']}]] -> {r['discovery']}"
                      for r in result["changed_discovery"]))
    print(f"catalogue: {before} -> {len(payload['factories'])} classes")
    touched = [p for row in payload["factories"] if row["n"] <= MR.CLASSIFICATION_LENGTH
               for p in VC.verify_row(row)[1]]
    residue = (touched + VC.duplicate_class_problems(payload["factories"])
               + VC.provenance_problems(payload)
               + VC.citation_problems(payload)
               + VC.header_problems(payload)
               + [p for row in payload["factories"]
                  for p in VC.certificate_problems(row)])
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("the migrated catalogue fails file-level checks; "
                         "nothing written")
    if args.dry_run:
        print("dry run: nothing written")
        return 0
    CF.write(payload)
    VC.persist_metric_cache()
    print("wrote master_catalog.json and MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
