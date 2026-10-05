#!/usr/bin/env python3
"""Build the catalogue website from `master_catalog/master_catalog.json`.

    python website/build_site.py                 # -> website/_site/
    python website/build_site.py --out /tmp/site
    python -m http.server -d website/_site 8000  # then open http://localhost:8000/

The master catalogue is the ONLY data source.  Nothing the site shows is stored
anywhere else in the repository, so the site cannot drift from the database:
merge a result into `master_catalog.json`, push, and the deploy rebuilds every
page's data from it.

    master_catalog/master_catalog.json      813 rows, 29 MB, with columns
                 |
                 |  build_site.py  (standard library only)
                 v
    _site/
      index.html search.html params.html factory.html css/ js/   <- website/static/
      data/index.json              every row WITHOUT its columns: what the
                                   search, landing and parameter pages read
      data/factories/<id>.json     one row WITH its columns: what one
                                   factory page reads
      data/factories.csv           the index as a spreadsheet

No number is recomputed here except the three closed-form exponents and the
extractable-T count, each a one-line function of fields the catalogue already
verified (`n`, `k`, `d`, `t_count`, and the monomials of `gate`).
`verify_catalog.py` is what certifies the rows; this script only lays them out.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CATALOG = ROOT / "master_catalog" / "master_catalog.json"
STATIC = HERE / "static"
TEMPLATES = HERE / "templates"
DEFAULT_OUT = HERE / "_site"

INDEX_VERSION = "2.0"
#: A table cell is not where anybody reads a 40,000-character gate; the full
#: string stays in the per-factory file.
HUMAN_LIMIT = 120
NAMES = {1: "T", 2: "CS", 3: "CCZ"}


# ------------------------------------------------------------------ the gate
def monomials(gate: str, k: int) -> list[tuple[int, ...]]:
    """``'0+1+01'`` -> ``[(0,), (1,), (0, 1)]``.

    The catalogue writes a gate as ``+``-separated monomials.  Inside one
    monomial the indices are concatenated digits when ``k <= 10`` (``'012'``),
    and comma-separated when ``k > 10`` (``'8,9'``, ``'10,11,12'``), where a
    token without a comma is then one wire (``'10'`` is ``T10``, not ``CS10``).
    Anything else is an error, not a guess.
    """
    if gate in ("", "I"):
        return []
    out = []
    for token in gate.split("+"):
        if "," in token:
            wires = tuple(int(part) for part in token.split(","))
        elif token.isdigit():
            wires = (int(token),) if k > 10 else tuple(int(ch) for ch in token)
        else:
            raise ValueError(f"unreadable monomial {token!r} in gate {gate[:60]!r}")
        if not 1 <= len(wires) <= 3 or any(not 0 <= w < k for w in wires) \
                or len(set(wires)) != len(wires):
            raise ValueError(f"monomial {token!r} is not a level-3 term on {k} outputs")
        out.append(wires)
    return out


def human(terms: list[tuple[int, ...]], k: int) -> str:
    """The catalogue's own ``gate_human`` spelling, rebuilt from the monomials."""
    joiner = "," if k > 10 else ""
    return "·".join(NAMES[len(t)] + joiner.join(str(w) for w in t) for t in terms)


def extractable_t(terms: list[tuple[int, ...]]) -> int | None:
    """``V_ex``: T states one run yields, or ``None`` when no count exists.

    ``T`` and ``CS`` are worth one ``T`` state, ``CCZ`` two -- but only when the
    monomials act on DISJOINT outputs.  Overlapping monomials have no
    well-defined extractable count, and no cross-gate rate claim can be made
    from such a circuit.
    """
    seen: set[int] = set()
    total = 0
    for wires in terms:
        if seen & set(wires):
            return None
        seen |= set(wires)
        total += 1 if len(wires) <= 2 else 2
    return total


def exponent(n: int, denominator, d: int) -> float | None:
    """``log(n / denominator) / log(d)`` -- every gamma on the site is this."""
    if not denominator or not n or d is None or d < 2:
        return None
    return math.log(n / denominator) / math.log(d)


# ------------------------------------------------------------------ one row
def factory_id(row: dict) -> str:
    """``n0015-k001-d3-1e610403``: sortable, readable, stable across rebuilds.

    A row is identified by ``(n, k, d, gate)``.  The gate of a row is its
    stored representative, so the id moves only if a merge replaces the
    representative itself -- which is exactly when the page should change.
    """
    key = f"{row['n']}|{row['k']}|{row['d']}|{row['gate']}"
    digest = hashlib.sha256(key.encode()).hexdigest()[:8]
    return f"n{row['n']:04d}-k{row['k']:03d}-d{row['d']}-{digest}"


def build_rows(catalog: dict):
    """Yield ``(summary, record)`` per row; raise on anything inconsistent."""
    references = catalog.get("references") or {}
    for position, row in enumerate(catalog["factories"]):
        n, k, d, N = row["n"], row["k"], row["d"], row["N"]
        terms = monomials(row["gate"], k)
        if human(terms, k) != row["gate_human"]:
            raise ValueError(f"factories[{position}]: gate {row['gate'][:40]!r} does not "
                             f"spell gate_human {row['gate_human'][:40]!r}")
        if len(row["columns"]) != n:
            raise ValueError(f"factories[{position}]: {len(row['columns'])} columns, n = {n}")
        missing = [c for c in row.get("citations") or [] if c not in references]
        if missing:
            raise ValueError(f"factories[{position}]: unknown citation(s) {missing}")

        fid = factory_id(row)
        by_degree = [sum(1 for t in terms if len(t) == w) for w in (1, 2, 3)]
        v_ex = extractable_t(terms)
        gamma = exponent(n, k, d)
        gamma_t = exponent(n, row.get("t_count"), d)
        gamma_rho = exponent(n, v_ex, d)
        gate_human = row["gate_human"]

        summary = {
            "id": fid, "n": n, "k": k, "d": d, "N": N, "r": N - k,
            "gate": row["gate"],
            "gate_human": gate_human if len(gate_human) <= HUMAN_LIMIT
                          else gate_human[:HUMAN_LIMIT - 3] + "...",
            "gate_truncated": len(gate_human) > HUMAN_LIMIT,
            "terms": len(terms),
            "t_terms": by_degree[0], "cs_terms": by_degree[1], "ccz_terms": by_degree[2],
            "pure_t": by_degree[0] == k and len(terms) == k,
            "t_count": row.get("t_count"),
            "poly_degree": row.get("poly_degree"),
            "effective_width": row.get("effective_width"),
            "gamma": gamma, "gamma_t": gamma_t, "gamma_rho": gamma_rho,
            "v_ex": v_ex, "rate": k / n,
            "d_is_exact": bool(row.get("d_is_exact")),
            "regimes": list(row.get("regimes") or []),
            "discovery": row.get("discovery"),
            "citations": list(row.get("citations") or []),
            "row": position,
        }
        record = {
            "id": fid,
            "row": position,
            "parameters": {"n": n, "k": k, "d": d, "N": N, "r": N - k,
                           "level": row.get("level")},
            "gate": {
                "string": row["gate"],
                "human": gate_human,
                "monomials": [list(t) for t in terms],
                "sk_key": row.get("sk_key"),
                "sk_fingerprint": row.get("sk_fingerprint"),
                "sk_canonical_frame": row.get("sk_canonical_frame"),
                "relabelled_into_canonical_frame": row.get("relabelled_into_canonical_frame"),
            },
            "circuit": {"columns": row["columns"]},
            "distance": {"d": d, "is_exact": bool(row.get("d_is_exact")),
                         "upper": row.get("d_upper"), "witness": row.get("d_witness")},
            "metrics": {"gamma": gamma, "gamma_t": gamma_t, "gamma_rho": gamma_rho,
                        "v_ex": v_ex, "rate": k / n,
                        "t_count": row.get("t_count"),
                        "poly_degree": row.get("poly_degree"),
                        "effective_width": row.get("effective_width")},
            "provenance": {"regimes": list(row.get("regimes") or []),
                           "discovery": row.get("discovery"),
                           "strongest_claim": row.get("strongest_claim"),
                           "sources": row.get("sources") or []},
            "references": [dict(key=c, **references[c]) for c in row.get("citations") or []],
        }
        yield summary, record


def parameter_groups(factories: list[dict]) -> list[dict]:
    """One entry per ``[[n,k,d]]``: what the landing table and landmarks read."""
    groups: dict[tuple, list] = defaultdict(list)
    for f in factories:
        groups[(f["n"], f["k"], f["d"])].append(f)
    out = []
    for (n, k, d), members in sorted(groups.items()):
        t_counts = [m["t_count"] for m in members if m["t_count"] is not None]
        v_exs = [m["v_ex"] for m in members if m["v_ex"] is not None]
        rhos = [m["gamma_rho"] for m in members if m["gamma_rho"] is not None]
        out.append({
            "n": n, "k": k, "d": d,
            "count": len(members),
            "gamma": members[0]["gamma"],          # a function of (n, k, d) alone
            "rate": k / n,
            "best_t_count": min(t_counts) if t_counts else None,
            "v_ex_best": max(v_exs) if v_exs else None,
            "gamma_rho": min(rhos) if rhos else None,
            "comparable": bool(rhos),
            "N_min": min(m["N"] for m in members),
            "ids": [m["id"] for m in members],
        })
    return out


CSV_FIELDS = ("id", "n", "k", "d", "N", "r", "gate_human", "terms", "t_terms",
              "cs_terms", "ccz_terms", "pure_t", "t_count", "poly_degree",
              "gamma", "gamma_t", "gamma_rho", "v_ex", "rate", "d_is_exact",
              "discovery", "regimes", "citations", "row")


def source_stamp(catalog_path: Path) -> dict:
    """The commit and date of the catalogue the site was built from, if git knows."""
    try:
        line = subprocess.run(
            ["git", "log", "-1", "--format=%h %cs", "--", str(catalog_path)],
            cwd=catalog_path.parent, capture_output=True, text=True, check=True,
            timeout=20).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        line = ""
    commit, _, date = line.partition(" ")
    return {"commit": commit or None, "date": date or None}


def render_pages(out: Path, stamp: dict) -> None:
    """Stitch the shared head, header and footer into every page.

    A page marks where they go with ``<!--#head-->``, ``<!--#header PAGE-->``
    and ``<!--#footer-->``.  ``PAGE`` names the nav link to mark current; a
    page that has its own search box adds ``nosearch`` to drop the header's.
    The footer's data stamp is written here, so no page fetches the index just
    to print a commit hash.
    """
    logo = (TEMPLATES / "logo.svg").read_text(encoding="utf-8").strip()
    head = (TEMPLATES / "head.html").read_text(encoding="utf-8").strip()
    header = (TEMPLATES / "header.html").read_text(encoding="utf-8").replace("{{logo}}", logo)
    commit, date = stamp.get("commit"), stamp.get("date")
    stamp_html = ('Data: <a href="https://github.com/shubhamj810/magic-state-factory-repo/'
                  'blob/main/master_catalog/master_catalog.json">master_catalog.json</a>'
                  + (f' at <a href="https://github.com/shubhamj810/magic-state-factory-repo/'
                     f'commit/{commit}"><code>{commit}</code></a>' if commit else "")
                  + (f" ({date})" if date else "") + ".")
    footer = (TEMPLATES / "footer.html").read_text(encoding="utf-8") \
        .replace("{{logo}}", logo.replace('id="lg"', 'id="lg-foot"').replace("url(#lg)", "url(#lg-foot)")) \
        .replace("{{stamp}}", stamp_html)
    marker = re.compile(r"<!--#header ?([^>]*)-->")
    for page in out.glob("*.html"):
        text = page.read_text(encoding="utf-8")
        if "<!--#" not in text:
            continue
        def stitched(match):
            words = match.group(1).split()
            html = header
            if "nosearch" in words:
                html = re.sub(r"\s*<!--search-->.*?<!--/search-->", "", html, flags=re.S)
            html = html.replace("<!--search-->", "").replace("<!--/search-->", "")
            for word in words:
                html = html.replace(f'data-page="{word}"', 'aria-current="page"')
            return re.sub(r' data-page="[a-z]+"', "", html).strip()
        text = marker.sub(stitched, text)
        text = text.replace("<!--#head-->", head).replace("<!--#footer-->", footer.strip())
        if "<!--#" in text:
            raise ValueError(f"{page.name}: an unknown template marker is left")
        page.write_text(text, encoding="utf-8")


def build(out: Path, catalog_path: Path = CATALOG) -> dict:
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    summaries, records = [], []
    for summary, record in build_rows(catalog):
        summaries.append(summary)
        records.append(record)

    ids = [s["id"] for s in summaries]
    if len(set(ids)) != len(ids):
        raise ValueError("two rows share an id: (n, k, d, gate) is not unique")
    if catalog.get("n_classes") not in (None, len(summaries)):
        raise ValueError(f"n_classes says {catalog['n_classes']}, "
                         f"the file has {len(summaries)} rows")

    summaries.sort(key=lambda s: (s["n"], s["k"], s["d"], s["gate"]))
    used = sorted({c for s in summaries for c in s["citations"]})
    index = {
        "index_version": INDEX_VERSION,
        "counts": {"factories": len(summaries),
                   "parameter_sets": len({(s["n"], s["k"], s["d"]) for s in summaries}),
                   "with_t_count": sum(1 for s in summaries if s["t_count"] is not None)},
        "ranges": {key: [min(s[key] for s in summaries), max(s[key] for s in summaries)]
                   for key in ("n", "k", "N")} |
                  {"d": sorted({s["d"] for s in summaries})},
        "source": source_stamp(catalog_path),
        "dedup_key": catalog.get("dedup_key"),
        "regimes": catalog.get("regimes") or {},
        "discovery": catalog.get("discovery") or {},
        "references": {key: catalog["references"][key] for key in used},
        "parameters": parameter_groups(summaries),
        "factories": summaries,
    }

    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(STATIC, out)
    data = out / "data"
    (data / "factories").mkdir(parents=True)
    (data / "index.json").write_text(json.dumps(index, separators=(",", ":")),
                                     encoding="utf-8")
    for record in records:
        (data / "factories" / f"{record['id']}.json").write_text(
            json.dumps(record, separators=(",", ":")), encoding="utf-8")
    with (data / "factories.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(CSV_FIELDS)
        for s in summaries:
            writer.writerow(["; ".join(s[f]) if isinstance(s[f], list) else s[f]
                             for f in CSV_FIELDS])
    render_pages(out, index["source"])
    # GitHub Pages runs Jekyll unless told not to, and Jekyll drops _-prefixed paths.
    (out / ".nojekyll").write_text("", encoding="utf-8")
    return index


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT,
                        help=f"output directory (default {DEFAULT_OUT.relative_to(ROOT)})")
    parser.add_argument("--catalog", type=Path, default=CATALOG,
                        help="the master catalogue to build from")
    arguments = parser.parse_args(argv)
    index = build(arguments.out, arguments.catalog)
    counts = index["counts"]
    print(f"built {counts['factories']} factories in {counts['parameter_sets']} "
          f"parameter sets -> {arguments.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
