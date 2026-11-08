#!/usr/bin/env python3
"""Build the catalogue website from `master_catalog/master_catalog.json`
and `master_catalog/master_catalog_large.json`.

    python website/build_site.py                 # -> website/_site/
    python website/build_site.py --out /tmp/site
    python -m http.server -d website/_site 8000  # then open http://localhost:8000/

The master catalogue is the ONLY data source.  It is read through
`catalogfile.load_all`, which rebuilds the columns of the large file's rows
from their constructions, so every row arrives here with its columns.
Nothing the site shows is stored anywhere else in the repository, so the
site cannot drift from the database: merge a result into the catalogue, push,
and the deploy rebuilds every page's data from it.

    master_catalog/master_catalog.json      1278 rows, 43 MB, with columns
    master_catalog/master_catalog_large.json  rows built by a construction
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
LARGE_NAME = "master_catalog_large.json"
sys.path.insert(0, str(ROOT / "master_catalog"))
import catalogfile as CF  # noqa: E402  (standard library only, like this file)
import records as RC  # noqa: E402  (the record rule with direct sums; standard library only)
CONTRIBUTORS = ROOT / "community_contributions" / "contributors.json"
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
def legacy_id(row: dict) -> str:
    """``n0015-k001-d3-1e610403``: sortable, readable, stable across rebuilds.

    A row is identified by ``(n, k, d, gate)``.  The gate of a row is its
    stored representative, so the id moves only if a merge replaces the
    representative itself -- which is exactly when the page should change.
    """
    key = f"{row['n']}|{row['k']}|{row['d']}|{row['gate']}"
    digest = hashlib.sha256(key.encode()).hexdigest()[:8]
    return f"n{row['n']:04d}-k{row['k']:03d}-d{row['d']}-{digest}"


def clifford_kind(row: dict) -> str:
    """``none``: the rotations, every one a T, deposit exactly the gate;
    ``powers``: they do once some rotations run as T^3, T^5 or T-dagger, so no
    Clifford gate is needed; ``required``: S or CZ gates are needed whatever
    the powers (the catalogue proves it: ``rotation_powers`` is null)."""
    corr = row["clifford_correction"]
    if not corr["S"] and not corr["CZ"]:
        return "none"
    return "powers" if row["rotation_powers"] is not None else "required"


ARXIV = re.compile(r"arXiv:(\d{4}\.\d{4,5})")


def named_references(row: dict, catalog: dict) -> list[str]:
    """The references a row's regime sentences name by arXiv number that no
    row of the catalogue cites: papers in the references only for a
    construction the AI searches used (San-Jose's GRS construction and Wills's
    parent codes, the owner's decision of 2026-11-07: credit the search, name
    the paper).  They are shown beside the provenance and never as the row's
    source, which is ``citations`` alone.  A paper some row cites is credit
    there, and is not repeated on other rows' pages."""
    references = catalog.get("references") or {}
    regimes = catalog.get("regimes") or {}
    cited = {c for r in catalog["factories"] for c in r.get("citations") or []}
    by_arxiv = {}
    for key in sorted(k for k in references if k not in cited):
        entry = references[key]
        for found in ARXIV.findall(entry.get("full", "")) + ARXIV.findall(
                (entry.get("url") or "").replace("arxiv.org/abs/", "arXiv:")):
            by_arxiv.setdefault(found, key)
    named = []
    for regime in row.get("regimes") or []:
        for found in ARXIV.findall(regimes.get(regime, "")):
            key = by_arxiv.get(found)
            if key and key not in named:
                named.append(key)
    return named


def build_rows(catalog: dict):
    """Yield ``(summary, record)`` per row; raise on anything inconsistent."""
    references = catalog.get("references") or {}
    in_file = {False: 0, True: 0}
    for position, row in enumerate(catalog["factories"]):
        # where the row is stored: its file, and its index there
        large = CF.is_large(row)
        stored_at = {"file": LARGE_NAME if large else CATALOG.name,
                     "row": in_file[large],
                     "construction": row.get("construction"),
                     "columns_sha256": row.get("columns_sha256")}
        in_file[large] += 1
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

        # the public name is the catalogue's own label; the old hash id is kept
        # only so links made before labels existed can be redirected
        fid = row["catalog_label"]
        old_id = legacy_id(row)
        by_degree = [sum(1 for t in terms if len(t) == w) for w in (1, 2, 3)]
        v_ex = extractable_t(terms)
        gamma = exponent(n, k, d)
        gamma_t = exponent(n, row.get("t_count"), d)
        gamma_rho = exponent(n, v_ex, d)
        # A source may certify a larger distance than the catalogue could
        # re-measure.  Tables show both; claims (rankings, the frontier) may use
        # the certified one, so the exponents are also given at that distance.
        d_cert = row.get("d_certified")
        d_claim = max(d, d_cert) if d_cert else d
        # a certified lower bound met by a fault exhibited here pins the distance
        d_cert_met = bool(d_cert) and row.get("d_upper") == d_cert
        gate_human = row["gate_human"]

        summary = {
            "id": fid, "legacy_id": old_id, "n": n, "k": k, "d": d, "N": N, "r": N - k,
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
            "A_d": row.get("A_d"),
            "d_cert": d_cert,
            "d_cert_exact": row.get("d_certified_is_exact") if d_cert else None,
            "d_cert_met": d_cert_met,
            "d_claim": d_claim,
            # how the lower bound in d is proved: "sweep", or the certificate's
            # method when d rests on one; and the labels the row had before
            "d_by": CF.distance_basis(row),
            "former_ids": list(row.get("former_labels") or []),
            "clifford": clifford_kind(row),
            "gamma_claim": exponent(n, k, d_claim),
            "gamma_t_claim": exponent(n, row.get("t_count"), d_claim),
            "gamma_rho_claim": exponent(n, v_ex, d_claim),
            "regimes": list(row.get("regimes") or []),
            "discovery": row.get("discovery"),
            "citations": list(row.get("citations") or []),
            "construction_refs": named_references(row, catalog),
            "row": stored_at["row"],
            "file": stored_at["file"],
        }
        record = {
            "id": fid,
            "row": stored_at["row"],
            "stored": stored_at,
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
                         "upper": row.get("d_upper"), "witness": row.get("d_witness"),
                         "A_d": row.get("A_d"),
                         "A_d_evidence": row.get("A_d_evidence") or [],
                         "basis": CF.distance_basis(row),
                         "sweep_floor": row.get("d_sweep_floor"),
                         "evidence": row.get("d_certified_evidence") or [],
                         "certified": ({"d": d_cert,
                                        "is_exact": row.get("d_certified_is_exact"),
                                        "met": d_cert_met,
                                        "source": row.get("d_certified_source")} if d_cert else None)},
            "clifford": {"kind": clifford_kind(row),
                         "correction": row["clifford_correction"],
                         "rotation_powers": row["rotation_powers"]},
            "metrics": {"gamma": gamma, "gamma_t": gamma_t, "gamma_rho": gamma_rho,
                        "gamma_claim": exponent(n, k, d_claim),
                        "gamma_t_claim": exponent(n, row.get("t_count"), d_claim),
                        "gamma_rho_claim": exponent(n, v_ex, d_claim),
                        "v_ex": v_ex, "rate": k / n,
                        "t_count": row.get("t_count"),
                        "poly_degree": row.get("poly_degree"),
                        "effective_width": row.get("effective_width")},
            "provenance": {"regimes": list(row.get("regimes") or []),
                           "discovery": row.get("discovery"),
                           "strongest_claim": row.get("strongest_claim"),
                           "sources": row.get("sources") or []},
            "references": [dict(key=c, **references[c]) for c in row.get("citations") or []],
            "construction_references": [dict(key=c, **references[c])
                                        for c in named_references(row, catalog)],
            "former_ids": list(row.get("former_labels") or []),
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
        claims = [m["gamma_rho_claim"] for m in members if m["gamma_rho_claim"] is not None]
        d_claim = max(m["d_claim"] for m in members)
        out.append({
            "n": n, "k": k, "d": d,
            "count": len(members),
            "gamma": members[0]["gamma"],          # a function of (n, k, d) alone
            "rate": k / n,
            "best_t_count": min(t_counts) if t_counts else None,
            "v_ex_best": max(v_exs) if v_exs else None,
            "gamma_rho": min(rhos) if rhos else None,
            "comparable": bool(rhos),
            # claims may use a distance certified by the source (see build_rows)
            "d_claim": d_claim,
            "d_claim_certified": d_claim > d,
            "d_claim_exact": next((bool(m["d_cert_exact"]) for m in members
                                   if m["d_cert"] == d_claim), True) if d_claim > d else None,
            "gamma_claim": exponent(n, k, d_claim),
            "gamma_rho_claim": min(claims) if claims else None,
            # the landing page can also rank by plain gamma, among pure T^k gates only
            "has_pure": any(m["pure_t"] for m in members),
            # a record under the owner's rule (see build): a pure T^k row of this
            # (n, k, d) that is a record in the T class; any row that is a record
            # in its own gate class (what the gamma_rho ranking uses: k counts
            # wires, so a record over all gates would compare a CCZ's three
            # wires with three T states); and a record over all gates
            "record_pure": any(m["pure_t"] and m["record_class"] for m in members),
            "record_class": any(m["record_class"] for m in members),
            "record_all": any(m["record_all"] for m in members),
            # what the landing page may present as best: a record (above) that
            # also has no hidden spectator, since its gamma counts all k outputs
            "best_pure": any(m["pure_t"] and m["record_class"] and m["_full_width"]
                             for m in members),
            "best_class": any(m["record_class"] and m["_full_width"] for m in members),
            "N_min": min(m["N"] for m in members),
            "ids": [m["id"] for m in members],
        })
    return out


CSV_FIELDS = ("id", "n", "k", "d", "d_is_exact", "A_d", "d_cert", "d_cert_exact", "N", "r", "gate_human", "terms", "t_terms",
              "cs_terms", "ccz_terms", "pure_t", "t_count", "poly_degree", "clifford",
              "gamma", "gamma_t", "gamma_rho", "v_ex", "rate",
              "discovery", "regimes", "citations", "file", "row")


def source_stamp(catalog_path: Path, large_path: Path | None = None) -> dict:
    """The commit and date of the catalogue the site was built from, if git knows:
    the last commit to touch either file, since a merge may change only one."""
    paths = [str(catalog_path)] + ([str(large_path)] if large_path else [])
    try:
        line = subprocess.run(
            ["git", "log", "-1", "--format=%h %cs", "--", *paths],
            cwd=catalog_path.parent, capture_output=True, text=True, check=True,
            timeout=20).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        line = ""
    commit, _, date = line.partition(" ")
    return {"commit": commit or None, "date": date or None}


def render_pages(out: Path, index: dict) -> None:
    import pages as P
    home = out / "index.html"
    home.write_text(home.read_text(encoding="utf-8").replace(
        "<!--#dataset-->", P.structured_data(index)), encoding="utf-8")
    stitch(out, list(out.glob("*.html")), depth=0)


def stitch(out: Path, files, depth: int) -> None:
    """Stitch the shared head, header and footer into every page.

    A page marks where they go with ``<!--#head-->``, ``<!--#header PAGE-->``
    and ``<!--#footer-->``.  ``PAGE`` names the nav link to mark current; a
    page that has its own search box adds ``nosearch`` to drop the header's.
    """
    logo = (TEMPLATES / "logo.svg").read_text(encoding="utf-8").strip()
    head = (TEMPLATES / "head.html").read_text(encoding="utf-8").strip()
    header = (TEMPLATES / "header.html").read_text(encoding="utf-8").replace("{{logo}}", logo)
    footer = (TEMPLATES / "footer.html").read_text(encoding="utf-8").replace("{{logo}}", logo)
    version = asset_version(out)
    marker = re.compile(r"<!--#header ?([^>]*)-->")
    root = "../" * depth or "./"
    head_here = head.replace("<!--#root-->", f'<meta name="site-root" content="{root}">')
    for page in files:
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
        text = text.replace("<!--#head-->", head_here).replace("<!--#footer-->", footer.strip())
        if "<!--#" in text:
            raise ValueError(f"{page.name}: an unknown template marker is left")
        text = _ASSET.sub(lambda m: f"{m.group(1)}?v={version}{m.group(2)}", text)
        page.write_text(relocate(text, depth), encoding="utf-8")


_ASSET = re.compile(r'(\b(?:href|src)="(?:css|js)/[\w.-]+\.(?:css|js))(")')


def asset_version(out: Path) -> str:
    """A hash of the stylesheet and scripts, appended to their URLs.

    GitHub Pages lets browsers keep a file for ten minutes; a new hash makes
    every page ask for the new file at once, so a page and its scripts never
    come from different builds."""
    digest = hashlib.sha256()
    for path in sorted((out / "css").glob("*.css")) + sorted((out / "js").glob("*.js")):
        digest.update(path.name.encode() + b"\0" + path.read_bytes())
    return digest.hexdigest()[:8]


_RELATIVE = re.compile(r'(\b(?:href|src|action|data-href)=")(?!https?:|/|#|mailto:|data:|javascript:)')


def relocate(text: str, depth: int) -> str:
    """Prefix every relative link with ``../`` per directory level."""
    return _RELATIVE.sub(lambda m: m.group(1) + "../" * depth, text) if depth else text


def shell(title: str, description: str, main: str, current: str, scripts, depth: int,
          canonical: str) -> str:
    """A whole page around ``main``: the shared head, header and footer."""
    import pages as P
    text = f"""<!doctype html>
<html lang="en">
<head>
<!--#head-->
<title>{P.esc(title)}</title>
<meta name="description" content="{P.esc(description)}">
<link rel="canonical" href="{P.SITE}{canonical}">
<meta property="og:url" content="{P.SITE}{canonical}">
<meta property="og:title" content="{P.esc(title)}">
<meta property="og:description" content="{P.esc(description)}">
</head>
<body data-prerendered="1">
<!--#header {current}-->
{main}
<!--#footer-->
{"".join(f'<script src="js/{name}"></script>' + chr(10) for name in scripts)}</body>
</html>
"""
    return text


def render_entries(out: Path, index: dict, records: list) -> None:
    """f/<label>/ for every factory and p/<n>.<k>.<d>/ for every parameter set."""
    import pages as P
    by_id = {f["id"]: f for f in index["factories"]}
    groups = {(g["n"], g["k"], g["d"]): g for g in index["parameters"]}
    pages = []
    for record in records:
        title, desc, main = P.factory_page(record, by_id[record["id"]], groups, by_id, index["source"])
        path = P.factory_path(record["id"])
        pages.append((path, shell(title, desc, main, "browse",
                                  ["catalog.js", "glequiv.js", "transform.js", "factory.js"], 2, path)))
    for key, group in groups.items():
        members = sorted((by_id[i] for i in group["ids"]), key=lambda f: f["id"])
        title, desc, main = P.params_page(group, members, groups)
        path = P.params_path(*key)
        pages.append((path, shell(title, desc, main, "browse",
                                  ["catalog.js", "query.js", "params.js"], 2, path)))
    contributors = (json.loads(CONTRIBUTORS.read_text(encoding="utf-8")).get("contributors") or []
                    if CONTRIBUTORS.exists() else [])
    # A row whose distance became a certificate's was relabelled; its old
    # address, and the old parameter page when no row is left there, send the
    # reader on to the new one.  They are not listed in the sitemap.
    redirects = []
    for record in records:
        for old in record.get("former_ids") or []:
            redirects.append((P.factory_path(old), P.factory_path(record["id"]), old))
    for record in records:
        for old in record.get("former_ids") or []:
            on, ok, od, _letters = CF.LABEL_RE.match(old).groups()
            key = (int(on), int(ok), int(od))
            path = P.params_path(*key)
            if key not in groups and path not in {r[0] for r in redirects}:
                p = record["parameters"]
                redirects.append((path, P.params_path(p["n"], p["k"], p["d"]),
                                  f"{key[0]}.{key[1]}.{key[2]}"))
    taken = {path for path, _ in pages}
    for path, target, old in redirects:
        if path in taken:
            raise ValueError(f"the old address {path} is also a live page")
        out_file = out / path / "index.html"
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(P.redirect_page(old, target), encoding="utf-8")
    title, desc, main = P.references_page(index, contributors)
    (out / "references.html").write_text(
        shell(title, desc, main, "references", ["catalog.js"], 0, "references.html"), encoding="utf-8")
    stitch(out, [out / "references.html"], depth=0)
    for path, text in pages:
        target = out / path / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    stitch(out, [out / path / "index.html" for path, _ in pages], depth=2)
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    # the date of the catalogue the pages were built from, so a crawler revisits after a merge
    date = index["source"].get("date")
    lastmod = f"<lastmod>{date}</lastmod>" if date else ""
    for path in ["", "search.html", "about.html", "references.html", "contribute.html"] + [path for path, _ in pages]:
        sitemap.append(f"  <url><loc>{P.SITE}{path}</loc>{lastmod}</url>")
    sitemap.append("</urlset>")
    (out / "sitemap.xml").write_text("\n".join(sitemap) + "\n", encoding="utf-8")


def build(out: Path, catalog_path: Path = CATALOG, large_path: Path | None = None) -> dict:
    large_path = large_path or catalog_path.with_name(LARGE_NAME)
    catalog = CF.load_all(catalog_path, large_path)
    summaries, records = [], []
    by_label = {row["catalog_label"]: row for row in catalog["factories"]}
    for summary, record in build_rows(catalog):
        summaries.append(summary)
        records.append(record)

    ids = [s["id"] for s in summaries]
    if len(set(ids)) != len(ids):
        raise ValueError("two rows share a catalog_label")
    references_map = catalog.get("references") or {}
    for s_ in summaries:
        s_["cite_text"] = "; ".join(references_map.get(c, {}).get("short", c) for c in s_["citations"])
    main_count = len(CF.main_rows(catalog["factories"]))
    if catalog.get("n_classes") not in (None, main_count):
        raise ValueError(f"n_classes says {catalog['n_classes']}, "
                         f"the main file has {main_count} rows")

    # Which factories the site may present as best: a record under the owner's
    # rule (master_catalog/records.py), in the row's own gate class and over
    # all gates. A direct sum can be in the catalogue but is never a record.
    verdicts = RC.status(catalog["factories"])
    for s_ in summaries:
        own = RC.gate_class(by_label[s_["id"]]["gate_human"])
        s_["record_class"] = verdicts[s_["id"]][own]["record"]
        s_["record_all"] = verdicts[s_["id"]]["all"]["record"]
        # whether every output is used in every CNOT frame (no hidden spectator,
        # intrinsic_width == k); kept out of the published index, since showing
        # the width is the owner's decision, and used only to choose what the
        # landing page presents as best
        s_["_full_width"] = by_label[s_["id"]]["intrinsic_width"] == s_["k"]
    summaries.sort(key=lambda s: (s["n"], s["k"], s["d"], s["gate"]))
    named = {c for row in catalog["factories"] for c in named_references(row, catalog)}
    used = sorted({c for s in summaries for c in s["citations"]} | named)
    index = {
        "index_version": INDEX_VERSION,
        "counts": {"factories": len(summaries),
                   "parameter_sets": len({(s["n"], s["k"], s["d"]) for s in summaries}),
                   "with_t_count": sum(1 for s in summaries if s["t_count"] is not None)},
        "ranges": {key: [min(s[key] for s in summaries), max(s[key] for s in summaries)]
                   for key in ("n", "k", "N")} |
                  {"d": sorted({s["d"] for s in summaries} | {s["d_claim"] for s in summaries})},
        "source": source_stamp(catalog_path, large_path),
        "dedup_key": catalog.get("dedup_key"),
        "regimes": catalog.get("regimes") or {},
        "discovery": catalog.get("discovery") or {},
        "references": {key: catalog["references"][key] for key in used},
        "parameters": parameter_groups(summaries),
        "factories": summaries,
    }
    for s_ in summaries:
        del s_["_full_width"]

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
    render_pages(out, index)
    render_entries(out, index, records)
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
    parser.add_argument("--large", type=Path, default=None,
                        help=f"its large file (default: {LARGE_NAME} beside it)")
    arguments = parser.parse_args(argv)
    index = build(arguments.out, arguments.catalog, arguments.large)
    counts = index["counts"]
    print(f"built {counts['factories']} factories in {counts['parameter_sets']} "
          f"parameter sets -> {arguments.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
