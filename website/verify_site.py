#!/usr/bin/env python3
"""Does the website actually work?  Drive a real browser over the built site.

    python website/build_site.py
    python website/verify_site.py            # sampled: every page shape, ~1 min
    python website/verify_site.py --full     # every parameter set and factory

Needs `pip install playwright && playwright install chromium`; the rest of the
repository does not, which is why this is not part of `verify_repo.py`.

The pages build themselves from JSON in the browser, so a link that resolves is
not evidence that the page it lands on RENDERED.  This script asserts on the
DOM that comes out, against numbers it computes itself from `data/index.json`
and the per-factory files:

    index.html    stat bar, the paged [[n,k,d]] table, its links
    search.html   result counts for a set of URL searches, each recomputed here
                  in Python, the typed-query syntax, and the CSV export
    params.html   one row per factory at those parameters, each linking on
    factory.html  N matrix rows, the first k marked output and the rest check,
                  row weights equal to the columns', every panel non-empty,
                  and the references the catalogue cites

Plus, on every page visited: no console error, no failed request, no
`undefined` / `NaN` / `[object Object]` in the text.

    exit 0  the website works        exit 1  it does not; the report says where
"""
from __future__ import annotations

import argparse
import contextlib
import functools
import http.server
import json
import random
import socket
import sys
import threading
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_SITE = HERE / "_site"
#: the catalogue's own GL(k,2) decision, used to check the browser's answers
sys.path.insert(0, str(HERE.parent / "master_catalog"))


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


@contextlib.contextmanager
def serve(directory: Path):
    """The built site on a free port, for as long as the block runs."""
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    handler = functools.partial(_Quiet, directory=str(directory))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()
        server.server_close()


class Failures(list):
    def check(self, condition, message):
        if not condition:
            self.append(message)
        return bool(condition)


class _Watcher:
    """Console errors and failed requests are failures, not warnings.

    Handlers are registered ONCE and read a mutable label: Playwright never
    unsubscribes them, so per-navigation handlers would report the next page's
    error under a stale name.
    """

    def __init__(self, page, failures):
        self.failures = failures
        self.where = "(before any page)"
        self.expect_errors = False
        page.on("console", lambda m: m.type == "error" and self._note(f"console error: {m.text}"))
        page.on("pageerror", lambda e: self._note(f"page error: {e}"))
        page.on("requestfailed", lambda r: self._note(f"request failed: {r.url}"))
        page.on("response", lambda r: r.status >= 400 and self._note(f"HTTP {r.status} for {r.url}"))

    def _note(self, message):
        if not self.expect_errors:
            self.failures.append(f"{self.where}: {message}")

    def at(self, where, expect_errors=False):
        self.where = where
        self.expect_errors = expect_errors


def _ghosts(page, failures, where):
    body = page.inner_text("body")
    for ghost in ("undefined", "NaN", "[object Object]"):
        if ghost in body:
            failures.append(f"{where}: the rendered page contains {ghost!r}")


# ------------------------------------------------- searches, recomputed here
def _monomials(gate: str, k: int) -> set[tuple[int, ...]]:
    out = set()
    for token in gate.split("+") if gate else []:
        wires = token.split(",") if "," in token else ([token] if k > 10 else list(token))
        out.add(tuple(sorted(int(w) for w in wires)))
    return out


#: the project's own two reports; "from the literature" means citing another paper
OWN = ("wills2026classification", "jain2026symmetry")


def searches(factories: list[dict], references: dict) -> list[tuple[str, int]]:
    """``(query string, expected count)`` -- each count computed independently."""
    def haystack(f):
        shorts = "; ".join(references[c]["short"] if c in references else c
                           for c in f["citations"])
        return " ".join([f["id"], f["gate_human"], " ".join(f["regimes"]),
                         f["discovery"] or "", shorts, " ".join(f["citations"])]).lower()
    count = lambda pred: sum(1 for f in factories if pred(f))  # noqa: E731
    return [
        ("", len(factories)),
        # a distance filter matches the re-verified OR the source-certified distance
        ("d=5", count(lambda f: 5 in (f["d"], f["d_claim"]))),
        ("d=6,7&exact=1", count(lambda f: (f["d"] in (6, 7) or f["d_claim"] in (6, 7)) and f["d_is_exact"])),
        ("d=8", count(lambda f: 8 in (f["d"], f["d_claim"]))),
        ("has=ccz", count(lambda f: f["ccz_terms"] > 0)),
        ("has=cs,ccz", count(lambda f: f["cs_terms"] > 0 and f["ccz_terms"] > 0)),
        ("pure=1", count(lambda f: f["pure_t"])),
        ("kmin=2&kmax=4&nmax=60", count(lambda f: 2 <= f["k"] <= 4 and f["n"] <= 60)),
        ("tmax=4", count(lambda f: f["t_count"] is not None and f["t_count"] <= 4)),
        ("grmax=1.2", count(lambda f: f["gamma_rho_claim"] is not None and f["gamma_rho_claim"] <= 1.2)),
        ("disc=pre-existing", count(lambda f: f["discovery"] == "pre-existing")),
        ("cite=haah2018codes", count(lambda f: "haah2018codes" in f["citations"])),
        ("regime=symmetry-SAT%20search", count(lambda f: "symmetry-SAT search" in f["regimes"])),
        # the typed syntax
        ("q=CCZ012", count(lambda f: (0, 1, 2) in _monomials(f["gate"], f["k"]))),
        ("q=%5B%5B15%2C%201%2C%203%5D%5D", count(lambda f: (f["n"], f["k"], f["d"]) == (15, 1, 3))),
        ("q=k%3D2%20t%3C%3D4", count(lambda f: f["k"] == 2 and f["t_count"] is not None
                                       and f["t_count"] <= 4)),
        ("q=N%3C10", count(lambda f: f["N"] < 10)),
        ("q=n%3C10", count(lambda f: f["n"] < 10)),
        ("q=CS%20d%3E%3D4", count(lambda f: f["cs_terms"] > 0 and f["d_claim"] >= 4)),
        ("q=pure%20exact", count(lambda f: f["pure_t"] and f["d_is_exact"])),
        ("q=haah", count(lambda f: "haah" in haystack(f))),
        ("lit=1", count(lambda f: any(c not in OWN for c in f["citations"]))),
        ("q=graph%20gluing", count(lambda f: "graph" in haystack(f) and "gluing" in haystack(f))),
    ]


def verify(site: Path, base: str, *, full: bool, sample: int, seed: int):
    from playwright.sync_api import sync_playwright

    index = json.loads((site / "data" / "index.json").read_text())
    factories, parameters = index["factories"], index["parameters"]
    failures = Failures()
    stats = {"pages": 0, "factories": 0, "searches": 0}
    rng = random.Random(seed)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        watcher = _Watcher(page, failures)

        def visit(url, where, selector, timeout=20000):
            watcher.at(where)
            page.goto(base + "/" + url, wait_until="networkidle")
            page.wait_for_selector(selector, timeout=timeout)
            stats["pages"] += 1

        # ---------------------------------------------------------- landing
        visit("", "index.html", "#body tr")
        rows = page.query_selector_all("#body tr")
        failures.check(len(rows) == min(50, len(parameters)),
                       f"index.html shows {len(rows)} rows on page 1, expected "
                       f"{min(50, len(parameters))}")
        count = page.inner_text("#count")
        failures.check(f"{len(parameters)} of {len(parameters)}" in count,
                       f"index.html count reads {count!r}")
        hero = page.inner_text("#hero-count")
        failures.check(hero.startswith(str(len(factories))),
                       f"index.html hero says {hero!r}, the catalogue has {len(factories)} factories")
        failures.check(page.evaluate("!!window.katex") and
                       not page.query_selector_all(".tex-fallback"),
                       "index.html: KaTeX did not load, so the maths is shown as TeX source")
        failures.check(page.query_selector("#frontier-plot svg") is not None,
                       "index.html: the frontier plot did not render")
        claimed = {p["d_claim"] for p in parameters if p["comparable"]}
        failures.check(len(page.query_selector_all("#record-cards a.record")) == len(claimed),
                       f"index.html: expected one record card per claimed distance {sorted(claimed)}")
        best_claim = min((p for p in parameters if p["gamma_rho_claim"] is not None),
                         key=lambda p: p["gamma_rho_claim"])
        failures.check(f"{best_claim['gamma_rho_claim']:.4f}" in page.inner_text("#headline-stats"),
                       f"index.html: headline does not show the best claim {best_claim['gamma_rho_claim']:.4f}")
        failures.check(len(page.query_selector_all("#cite-list li")) >= 1,
                       "index.html: the how-to-cite list is empty")
        _ghosts(page, failures, "index.html")
        # the hero draws the 15-to-1 factory from its own record: N x n cells
        bk = next((f for f in factories if (f["n"], f["k"], f["d"]) == (15, 1, 3)), None)
        if bk:
            page.wait_for_selector("#hm-svg rect")
            cells = len(page.query_selector_all("#hm-svg rect"))
            failures.check(cells == bk["N"] * bk["n"],
                           f"index.html: hero matrix has {cells} cells, expected {bk['N'] * bk['n']}")
        # hovering a plot point shows its parameters
        point = page.query_selector_all("#frontier-plot circle.pt")[0]
        point.scroll_into_view_if_needed()
        box = point.bounding_box()
        page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        failures.check("gates" in page.inner_text("#plot-tip") and
                       page.query_selector("#plot-tip.on") is not None,
                       "index.html: hovering a plot point shows no tooltip")
        page.click('#pager button[data-page="2"]')
        failures.check("page 2 of" in page.inner_text("#count"),
                       "index.html: the pager did not move to page 2")
        page.fill("#filter", "k=1 d=3")
        expected = sum(1 for p in parameters if p["k"] == 1 and p["d"] == 3)
        failures.check(page.inner_text("#count").startswith(f"{expected} of"),
                       f"index.html filter 'k=1 d=3' reads {page.inner_text('#count')!r}, "
                       f"expected {expected}")
        hrefs = [a.get_attribute("href") for a in page.query_selector_all("#body a[href]")]
        failures.check(hrefs and all(h.startswith("params.html?") for h in hrefs),
                       "index.html has a row link that does not go to params.html")
        # the landing search box submits into search.html
        page.fill("#hero-q", "CCZ")
        page.click(".searchbar.big button[type=submit]")
        page.wait_for_selector("#body tr")
        failures.check("search.html" in page.url and "q=CCZ" in page.url,
                       f"the landing search box went to {page.url}")

        # ----------------------------------------------------------- search
        for query, expected in searches(factories, index.get("references") or {}):
            visit(f"search.html?{query}", f"search.html?{query}", "#count strong, #body td.empty")
            stats["searches"] += 1
            shown = page.inner_text("#count")
            failures.check(shown.startswith(f"{expected} of {len(factories)}"),
                           f"search.html?{query}: reads {shown!r}, expected {expected}")
            _ghosts(page, failures, f"search.html?{query}")
        # a search survives the URL: set controls, reload, same count
        visit("search.html", "search.html (controls)", "#count strong")
        # the toggles are pills: a checkbox inside a label, so click the label
        page.click('label.pill:has(input[name="d"][value="4"])')
        page.click("label.pill:has(#exact)")
        page.wait_for_timeout(300)
        after = page.inner_text("#count")
        page.reload(wait_until="networkidle")
        page.wait_for_selector("#count strong")
        failures.check(page.inner_text("#count") == after and "d=4" in page.url,
                       f"search.html: state did not survive a reload ({page.url})")
        with page.expect_download() as info:
            page.click("#export-csv")
        lines = Path(info.value.path()).read_text().strip().splitlines()
        wanted = sum(1 for f in factories if 4 in (f["d"], f["d_claim"]) and f["d_is_exact"])
        failures.check(len(lines) == wanted + 1,
                       f"search.html: CSV export has {len(lines) - 1} rows, expected {wanted}")
        # sorting by a header puts the least gamma_rho first
        visit("search.html?sort=gamma_rho_claim", "search.html sorted", "#body tr")
        best = min(f["gamma_rho_claim"] for f in factories if f["gamma_rho_claim"] is not None)
        first = page.inner_text("#body tr:first-child td:nth-child(5)")
        failures.check(first.startswith(f"{best:.3f}"),
                       f"search.html?sort=gamma_rho_claim: first row shows {first}, least is {best:.3f}")

        # ----------------------------------------------------------- params
        wanted_params = parameters if full else rng.sample(parameters, min(sample, len(parameters)))
        for edge in (parameters[0], parameters[-1],
                     max(parameters, key=lambda p: p["k"]),
                     max(parameters, key=lambda p: p["count"])):
            if edge not in wanted_params:
                wanted_params.append(edge)
        linked: set[str] = set()
        for p in wanted_params:
            where = f"params.html [[{p['n']},{p['k']},{p['d']}]]"
            visit(f"params.html?n={p['n']}&k={p['k']}&d={p['d']}", where, "#body tr")
            links = [a.get_attribute("href") for a in page.query_selector_all("#body td.gate a[href]")]
            failures.check(len(links) == p["count"],
                           f"{where}: {len(links)} gate links for {p['count']} factories")
            title = page.title()
            failures.check(f"[[{p['n']}, {p['k']}, {p['d']}]]" in title and
                           page.query_selector("#heading .katex") is not None,
                           f"{where}: title is {title!r}, or the heading was not typeset")
            _ghosts(page, failures, where)
            for href in links:
                if not href or not href.startswith("factory.html?id="):
                    failures.append(f"{where}: bad gate link {href!r}")
                else:
                    linked.add(href.split("id=", 1)[1])

        # ---------------------------------------------------------- factory
        by_id = {f["id"]: f for f in factories}
        targets = sorted(linked)
        if not full:
            # always include the widest circuit and one with every reference kind
            targets += [max(factories, key=lambda f: f["n"] * f["N"])["id"]]
            targets += [f["id"] for f in factories if "haah2018codes" in f["citations"]][:1]
            targets = sorted(set(targets))
        for fid in targets:
            if fid not in by_id:
                failures.append(f"a params page linked to unknown factory {fid}")
                continue
            record = json.loads((site / "data" / "factories" / f"{fid}.json").read_text())
            where = f"factory.html {fid}"
            visit(f"factory.html?id={fid}", where, "table.matrix tbody tr", timeout=40000)
            stats["factories"] += 1
            k, N, n = (record["parameters"][key] for key in ("k", "N", "n"))
            matrix_rows = page.query_selector_all("table.matrix tbody tr")
            failures.check(len(matrix_rows) == N, f"{where}: {len(matrix_rows)} matrix rows, N = {N}")
            failures.check(len(page.query_selector_all("table.matrix tbody tr.out")) == k,
                           f"{where}: output rows marked != k = {k}")
            failures.check(len(page.query_selector_all("table.matrix tbody tr.chk")) == N - k,
                           f"{where}: check rows marked != r = {N - k}")
            weights = [0] * N
            for column in record["circuit"]["columns"]:
                for wire in column:
                    weights[wire] += 1
            for q in {0, N - 1}:
                bits = matrix_rows[q].query_selector("td.bits").inner_text()
                failures.check(len(bits) == n, f"{where}: row {q} is {len(bits)} wide, n = {n}")
                failures.check(bits.count("1") == weights[q],
                               f"{where}: row {q} has {bits.count('1')} ones, columns give {weights[q]}")
            for section in ("#metric-grid", "#gate-panel", "#distance-panel",
                            "#references-panel", "#provenance-panel"):
                element = page.query_selector(section)
                failures.check(element is not None and element.inner_text().strip(),
                               f"{where}: {section} is empty")
            refs = page.query_selector_all("#references-panel ol.refs li")
            failures.check(len(refs) == len(record["references"]),
                           f"{where}: {len(refs)} references shown, record cites "
                           f"{len(record['references'])}")
            failures.check(page.query_selector('#crumbs a[href^="params.html"]') is not None,
                           f"{where}: no breadcrumb back to params.html")
            _ghosts(page, failures, where)

        # ------------------------------------------- the CNOT + S tool, cross-checked
        import glcanon

        def monos(gate, k):
            return [tuple(int(w) for w in (t.split(",") if "," in t else ([t] if k > 10 else list(t))))
                    for t in gate.split("+")] if gate else []

        same_k = [f for f in factories if f["k"] == 3]
        source = same_k[0]
        other = next(f for f in same_k[1:]
                     if glcanon.gl_isomorphic(3, monos(source["gate"], 3), monos(f["gate"], 3)) is False)
        where = f"factory.html {source['id']} (CNOT + S tool)"
        visit(f"factory.html?id={source['id']}", where, "table.matrix tbody tr")
        page.fill("#tf-target", other["gate_human"])
        page.click("#tf-check")
        page.wait_for_selector(".tf-verdict")
        failures.check("Not reachable" in page.inner_text(".tf-verdict"),
                       f"{where}: {other['gate_human']} is not GL-equivalent, page says "
                       f"{page.inner_text('.tf-verdict')[:80]!r}")
        page.wait_for_function("!/Looking/.test(document.getElementById('tf-elsewhere').textContent)",
                               timeout=60000)
        listed = [a.get_attribute("href").split("id=", 1)[1]
                  for a in page.query_selector_all("#tf-elsewhere a[href^='factory.html']")]
        by = {f["id"]: f for f in factories}
        failures.check(listed, f"{where}: no catalogued factory listed for {other['gate_human']}")
        for fid in listed:
            failures.check(glcanon.gl_isomorphic(3, monos(by[fid]["gate"], 3), monos(other["gate"], 3)) is True,
                           f"{where}: lists {fid}, which does not produce {other['gate_human']}")
        for attempt in range(3):
            page.click("#tf-random")
            page.wait_for_selector(".tf-verdict.ok")
            target = page.input_value("#tf-target")
            parsed = [tuple(int(ch) for ch in (tok[3:] if tok.startswith("CCZ") else tok[2:] if tok.startswith("CS")
                                               else tok[1:])) for tok in target.split("·")]
            failures.check(glcanon.gl_isomorphic(3, monos(source["gate"], 3), parsed) is True,
                           f"{where}: random gate {target} is not GL-equivalent in Python")
            text = page.inner_text("#tf-result")
            failures.check("Same gate" in text or "Checked on all 8 basis states" in text,
                           f"{where}: no verified construction for {target}")

        # one export from a factory page, checked cell by cell
        small = factories[0]["id"]
        visit(f"factory.html?id={small}", "factory.html export", "table.matrix tbody tr")
        with page.expect_download() as info:
            page.click("#download-csv")
        record = json.loads((site / "data" / "factories" / f"{small}.json").read_text())
        lines = Path(info.value.path()).read_text().strip().splitlines()
        ones = sum(line.split(",")[2:].count("1") for line in lines[1:])
        failures.check(len(lines) == record["parameters"]["N"] + 1 and
                       ones == sum(len(c) for c in record["circuit"]["columns"]),
                       f"factory.html {small}: matrix CSV does not match the columns")

        # ------------------------------------------- graceful failures
        for url, expect in (("params.html?n=999999&k=1&d=3", "Nothing catalogued"),
                            ("factory.html?id=nope", "Could not load"),
                            ("factory.html", "Could not load")):
            watcher.at(url, expect_errors=True)
            page.goto(f"{base}/{url}", wait_until="networkidle")
            stats["pages"] += 1
            failures.check(expect.lower() in page.inner_text("body").lower(),
                           f"{url}: expected a graceful {expect!r} message")

        browser.close()
    return failures, stats


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--site", type=Path, default=DEFAULT_SITE, help="the built site")
    parser.add_argument("--full", action="store_true",
                        help="visit every parameter set and every factory (slow)")
    parser.add_argument("--sample", type=int, default=12,
                        help="parameter sets to sample when not --full (default 12)")
    parser.add_argument("--seed", type=int, default=0, help="sampling seed")
    arguments = parser.parse_args(argv)
    if not (arguments.site / "data" / "index.json").exists():
        print(f"no built site at {arguments.site}; run website/build_site.py first")
        return 1

    with serve(arguments.site) as base:
        failures, stats = verify(arguments.site, base, full=arguments.full,
                                 sample=arguments.sample, seed=arguments.seed)
    print(f"visited {stats['pages']} pages, ran {stats['searches']} searches, "
          f"checked {stats['factories']} factory pages")
    if failures:
        print(f"\nFAILED -- {len(failures)} problem(s):")
        for failure in failures:
            print(f"  · {failure}")
        return 1
    print("\nOK -- every page rendered and every link resolved.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
