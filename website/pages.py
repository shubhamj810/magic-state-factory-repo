"""Static HTML for every factory page and every parameter page.

    f/<label>/index.html     one factory: matrix, figures of merit, gate,
                             distance, original source, provenance, related
    p/<n>.<k>.<d>/index.html every inequivalent gate at one [[n,k,d]]

Rendered here, at build time, so each page is real HTML: it has its own title
and description, reads without JavaScript, and can be indexed and archived.
The scripts only add interaction on top (sorting, the matrix view toggle,
exports, the CNOT + S tool) and KaTeX typesetting of the ``tex`` spans.
"""
from __future__ import annotations

import html
import json
import re
from urllib.parse import quote

REPO = "https://github.com/shubhamj810/magic-state-factory-repo"
SITE = "https://shubhamj810.github.io/magic-state-factory-repo/"
NAMES = {1: "T", 2: "CS", 3: "CCZ"}


def esc(text) -> str:
    return html.escape("" if text is None else str(text), quote=True)


def tex(source: str) -> str:
    """A span KaTeX typesets in the browser; the TeX itself is the fallback."""
    return f'<span class="tex">{esc(source)}</span>'


def params_tex(n, k, d) -> str:
    return tex(f"[\\![{n},\\,{k},\\,{d}]\\!]")


def params_text(n, k, d) -> str:
    return f"[[{n}, {k}, {d}]]"


def gate_tex(human: str) -> str:
    more = human.endswith("...")
    body = human[:-3] if more else human
    terms = []
    for tok in filter(None, body.split("·")):
        for name in ("CCZ", "CS", "T"):
            if tok.startswith(name):
                terms.append(f"\\mathrm{{{name}}}_{{{tok[len(name):]}}}")
                break
        else:
            terms.append(f"\\mathrm{{{tok}}}")
    return tex("\\cdot ".join(terms) + ("\\cdots" if more else ""))


def num(value, places=3) -> str:
    return "—" if value is None else f"{value:.{places}f}"


def factory_path(label: str) -> str:
    return f"f/{label}/"


def params_path(n, k, d) -> str:
    return f"p/{n}.{k}.{d}/"


def distance_tags(d, exact, cert, cert_exact) -> str:
    out = (f'<span class="tag exact" title="verified here: exact">d = {d}</span>' if exact
           else f'<span class="tag floor" title="verified here: a proved lower bound">d &ge; {d}</span>')
    if cert and cert > d:
        out += (f' <span class="tag cert" title="certified by its source, not re-checked here">certified '
                f'{"" if cert_exact else "&ge; "}{cert}</span>')
    return out


def distance_bounds(d, exact, upper) -> str:
    """What is proved about d, as TeX: d = 3, 6 <= d <= 7, or d >= 6.

    The lower bound is the exhaustive search below d; the upper bound is an
    explicit damaging fault, when one was found.
    """
    if exact:
        return f"d={d}"
    if upper is not None and upper > d:
        return f"{d}\\le d\\le {upper}"
    return f"d\\ge {d}"


def claim_mark(row) -> str:
    dc, dv = row.get("d_claim"), row.get("d")
    return (f'<sup class="cert-mark" title="at the distance certified by its source, d = {dc}">&dagger;</sup>'
            if dc and dc > dv else "")


# ------------------------------------------------------------------ the matrix
def matrix_html(record) -> str:
    p = record["parameters"]
    n, N, k = p["n"], p["N"], p["k"]
    by_wire = [[] for _ in range(N)]
    for j, column in enumerate(record["circuit"]["columns"]):
        for wire in column:
            if 0 <= wire < N:
                by_wire[wire].append(j)
    ticks = "".join("|" if j % 10 == 0 else ("'" if j % 5 == 0 else " ") for j in range(n))
    labels = ""
    for t in range(0, n, 10):
        labels += str(t)
        if t + 10 < n:
            labels += " " * max(10 - len(str(t)), 1)
    rows = []
    for q in range(N):
        out = q < k
        cls = ("out" if out else "chk") + (" divider" if q == k and k > 0 else "")
        bits = [0] * n
        for j in by_wire[q]:
            bits[j] = 1
        runs, start = [], 0
        for j in range(1, n + 1):
            if j == n or bits[j] != bits[start]:
                tag = "b" if bits[start] else "i"
                runs.append(f"<{tag}>{('1' if bits[start] else '·') * (j - start)}</{tag}>")
                start = j
        rows.append(f'<tr class="{cls}"><th class="rowlab" scope="row">{"out" if out else "check"} {q} '
                    f'<span class="muted">({len(by_wire[q])})</span></th><td class="bits">{"".join(runs)}</td></tr>')
    return ('<table class="matrix"><thead><tr><th class="rowlab" scope="col">wire</th><th scope="col">'
            f'<div class="ruler">{esc(labels)}</div><div class="ruler" aria-hidden="true">{esc(ticks)}</div>'
            f'</th></tr></thead><tbody>{"".join(rows)}</tbody></table>')


def metric(key, value, note="", empty="not computed") -> str:
    shown = (f'<span class="v none">{empty}</span>' if value is None or value == ""
             else f'<span class="v">{esc(value)}</span>')
    return (f'<div class="cell"><span class="k">{key}</span>{shown}'
            + (f'<span class="note">{note}</span>' if note else "") + "</div>")


def reference_html(ref) -> str:
    out = esc(ref.get("full") or ref.get("short") or ref.get("key"))
    if ref.get("url"):
        shown = ref["url"].split("://", 1)[-1].removeprefix("dx.")
        out += f' <a href="{esc(ref["url"])}" rel="noopener">{esc(shown)}</a>'
    return out


def code_snippet(label: str) -> str:
    return (f"""# git clone {REPO}
# cd magic-state-factory-repo/master_catalog
import json, urllib.request
import verify_catalog as VC

url = "{SITE}data/factories/{label}.json"
record = json.load(urllib.request.urlopen(url))
columns = record["circuit"]["columns"]
k, N = record["parameters"]["k"], record["parameters"]["N"]

facts, problems = VC.derive(columns, k, N)    # gate, T-count, degree, ...
distance = VC.measure_distance(columns, k, N)  # exhaustive fault search
print(facts["gate_human"], distance["d_exact"] or distance["d_at_least"],
      problems or "verified")
""")


def equivalents_snippet(label: str) -> str:
    return (f"""import json, urllib.request

NAMES = {{1: "T", 2: "CS", 3: "CCZ"}}


def equivalent_gates(k, terms, limit=1_000_000):
    \"\"\"Every gate a CNOT circuit and S, Z, CZ gates reach from this one.

    A gate is its set of terms mod Clifford: {{a}} is T, {{a,b}} is CS and
    {{a,b,c}} is CCZ on those outputs. CNOT c->t sends x_t to
    x_c + x_t - 2 x_c x_t, so a term on t but not c adds the term with t
    replaced by c, and, below CCZ, the term with c added.
    \"\"\"
    start = frozenset(frozenset(m) for m in terms)
    seen, queue = {{start}}, [start]
    for gate in queue:
        for c in range(k):
            for t in range(k):
                if c == t:
                    continue
                new = set(gate)
                for m in gate:
                    if t in m and c not in m:
                        new ^= {{(m - {{t}}) | {{c}}}}
                        if len(m) < 3:
                            new ^= {{m | {{c}}}}
                new = frozenset(new)
                if new not in seen:
                    seen.add(new)
                    queue.append(new)
                    if len(seen) > limit:
                        raise RuntimeError(f"more than {{limit}} equivalent gates")
    return seen


def name(gate, k):
    sep = "," if k > 10 else ""
    terms = sorted((sorted(m) for m in gate), key=lambda m: (len(m), m))
    return "·".join(NAMES[len(m)] + sep.join(map(str, m)) for m in terms) or "I"


url = "{SITE}data/factories/{label}.json"
record = json.load(urllib.request.urlopen(url))
k = record["parameters"]["k"]
gates = equivalent_gates(k, record["gate"]["monomials"])
lines = sorted(name(g, k) for g in gates)
print(len(lines), "equivalent gates")
with open("equivalent-gates-{label}.txt", "w") as out:
    out.write("\\n".join(lines) + "\\n")
""")


# ---------------------------------------------------------- references page
def _published(key: str, ref: dict) -> tuple[str, str]:
    """Sort key for a reference: its publication ``date`` (``YYYY-MM[-DD]``),
    else the year its label prints, else last; then the key."""
    year = re.search(r"\((\d{4})\)", ref.get("short", ""))
    return (ref.get("date") or (year.group(1) if year else "9999"), key)


def references_page(index: dict, contributors: list[dict]):
    """Every paper the catalogue draws on, and everyone who has contributed."""
    counts: dict[str, int] = {}
    for f in index["factories"]:
        for key in f["citations"]:
            counts[key] = counts.get(key, 0) + 1
    refs = sorted(index["references"].items(), key=lambda item: _published(*item))
    papers = "".join(
        f'<li id="ref-{esc(key)}">{reference_html(dict(key=key, **ref))} '
        f'<span class="muted">·</span> <a class="small" href="search.html?cite={quote(key)}">{counts.get(key, 0)} '
        f'{"factory" if counts.get(key, 0) == 1 else "factories"}</a></li>'
        for key, ref in refs)
    people = "".join(
        "<li><strong>" + esc(c["name"]) + "</strong>"
        + (f", {esc(c['affiliation'])}" if c.get("affiliation") else "")
        + (f'. <span class="muted">{esc(c["contribution"])}</span>' if c.get("contribution") else "")
        + (f' <span class="small muted">({esc(c["date"])})</span>' if c.get("date") else "")
        + "</li>" for c in contributors)
    main = f"""
<section class="page-head narrow">
  <div class="inner">
    <h1>References</h1>
    <p class="lede">The papers the catalogue's factories come from, and the people who have
    contributed to it.</p>
  </div>
</section>

<main id="main" class="guide">
  <nav class="toc" aria-label="on this page">
    <a href="#papers">Papers</a><a href="#contributors">Contributors</a>
  </nav>
  <div class="prose">
    <h2 id="papers">Papers</h2>
    <p>Every factory is credited to the work that found it. The papers are in order of
    publication, and the link after each one lists its factories.</p>
    <ol class="refs ref-list" id="paper-list">{papers}</ol>

    <h2 id="contributors">Contributors</h2>
    {f'<ul class="plain contributor-list" id="contributor-list">{people}</ul>' if people else
     '<p class="muted" id="contributor-list">No community contributions yet.</p>'}
    <p>Anyone who adds a factory is listed here. <a href="contribute.html">Contribute a factory</a>.</p>
  </div>
</main>"""
    return ("References · Magic State Factory Catalog",
            "The papers the Magic State Factory Catalog draws on, and everyone who has contributed to it.",
            main)


# ------------------------------------------------------------- factory page
def factory_main(record, summary, groups, by_id, stamp) -> str:
    p, gate, m, dist = record["parameters"], record["gate"], record["metrics"], record["distance"]
    n, k, d, N, r = p["n"], p["k"], p["d"], p["N"], p["r"]
    label = record["id"]
    cert = dist.get("certified") if dist.get("certified") and dist["certified"]["d"] > d else None
    monos = gate.get("monomials") or []
    kinds = {1: 0, 2: 0, 3: 0}
    for t in monos:
        kinds[len(t)] += 1
    pure = len(monos) == k and all(len(t) == 1 for t in monos)
    prov = record.get("provenance") or {}

    def at_cert(value):
        if not cert or value is None:
            return ""
        return f" At the certified {tex('d=' + str(cert['d']))}: {num(value, 4)}."

    short = gate["human"] if len(gate["human"]) <= 90 else gate["human"][:87] + "..."
    head = f"""
<section class="page-head">
  <div class="inner">
    <nav class="crumbs" id="crumbs" aria-label="breadcrumb"><span><a href="index.html">Home</a></span><span><a href="{params_path(n, k, d)}">{params_tex(n, k, d)}</a></span></nav>
    <h1 id="heading">{params_tex(n, k, d)} factory</h1>
    <p class="lede gate-lede">{gate_tex(short)}</p>
    <dl class="summary">
      <div><dt>distance, proved here</dt><dd>{tex(distance_bounds(d, dist["is_exact"], dist.get("upper")))}{(" <span class='tag cert' title='certified by its source, not re-checked here'>certified " + ("" if cert["is_exact"] else "&ge; ") + str(cert["d"]) + "</span>") if cert else ""}</dd></div>
      <div><dt>{tex(r"\gamma_\rho")}</dt><dd>{num(m.get("gamma_rho_claim"), 4)}{claim_mark(summary)}</dd></div>
      <div><dt>{tex(r"V_{\mathrm{ex}}")}</dt><dd>{m["v_ex"] if m["v_ex"] is not None else "—"}</dd></div>
      <div><dt>wires</dt><dd>{tex(f"N={N}")}</dd></div>
      <div><dt>found by</dt><dd><span class="tag {'ai' if prov.get('discovery') == 'AI search' else 'pre'}">{esc(prov.get("discovery") or "—")}</span>{' <span class="tag pure">pure T</span>' if pure else ""}</dd></div>
    </dl>
  </div>
</section>"""

    caption = (f"The {tex(f'{N}\\times{n}')} matrix. Rows are wires and columns are rotations. "
               "A 1 means the wire takes part in the rotation, and the number beside each wire is its row weight."
               + (" Scroll sideways to see every column." if n > 120 else ""))
    metrics = "".join([
        metric(f"inputs {tex('n')}", n, "Noisy T states per run."),
        metric(f"outputs {tex('k')}", k),
        metric(f"distance {tex('d')}", ("" if dist["is_exact"] else "≥ ") + str(d),
               ("Exact, proved and witnessed here." if dist["is_exact"] else "A lower bound proved here.")
               + (f" Its source certifies {tex(('d=' if cert['is_exact'] else 'd\\ge ') + str(cert['d']))}." if cert else "")),
        metric(f"wires {tex('N')}", N),
        metric(f"checks {tex('r')}", r),
        metric(tex(r"V_{\mathrm{ex}}"), m["v_ex"],
               "Undefined, because the gate's terms overlap." if m["v_ex"] is None
               else "T states per run. CCZ counts as two.", "not defined"),
        metric(tex(r"\gamma_\rho = \log(n/V_{\mathrm{ex}})/\log d"), None if m["gamma_rho"] is None else num(m["gamma_rho"], 4),
               "Overhead per extractable T state. Lower is better." + at_cert(m.get("gamma_rho_claim")), "not defined"),
        metric(tex(r"\gamma = \log(n/k)/\log d"), num(m["gamma"], 4), "Overhead per output qubit." + at_cert(m.get("gamma_claim"))),
        metric(tex(r"\gamma_T = \log(n/T)/\log d"), None if m["gamma_t"] is None else num(m["gamma_t"], 4),
               "Overhead per unit of T-count." + at_cert(m.get("gamma_t_claim"))),
        metric("T-count", m["t_count"], "Minimal T-count of the output gate."
               + (" Not computable at this width." if m["t_count"] is None else "")),
        metric("phase-polynomial degree", m["poly_degree"], "Minimised over changes of output basis."),
        metric("effective width", m["effective_width"], "Rank of the output rows modulo the check rows."),
    ])
    gate_panel = (
        '<div class="gate-terms">'
        f'<span class="term"><b>{kinds[1]}</b> T</span><span class="term"><b>{kinds[2]}</b> CS</span>'
        f'<span class="term"><b>{kinds[3]}</b> CCZ</span>'
        f'<span class="term">on <b>{k}</b> output {"wire" if k == 1 else "wires"}</span></div>'
        "<p><strong>As gates:</strong> "
        + (gate_tex(gate["human"]) if len(gate["human"]) <= 1500 else f'<code class="wrap">{esc(gate["human"])}</code>')
        + "</p>"
        f'<p><strong>As monomials:</strong> <code class="wrap">{esc(gate["string"])}</code> '
        '<span class="small muted">(output wires per term, separated by +)</span></p>'
        '<p class="small muted">This row stands for every gate that a CNOT circuit and S, Z and CZ '
        "gates on the outputs can reach from this one. They all prepare the same magic state. "
        + (f"The wires are shown in the {tex('S_k')}-canonical frame." if gate.get("sk_canonical_frame")
           else "The wires are shown in the labelling of the stored circuit.") + "</p>")
    distance_panel = (
        "<p>" + (f"<strong>{tex(f'd={d}')}, exact.</strong> No fault of weight below {d} is both undetectable "
                 f"and damaging. One of weight {d} is." if dist["is_exact"] else
                 f"<strong>{tex(distance_bounds(d, False, dist.get('upper')))}.</strong> No fault of weight below {d} is both "
                 f"undetectable and damaging. None of weight {d} has been found"
                 + (f", and one of weight {dist['upper']} is, so the distance lies between the two."
                    if dist.get("upper") is not None and dist["upper"] > d else ", so the true distance may be larger."))
        + "</p>"
        + (f'<p class="small">A damaging fault of weight {dist["upper"]}'
           + (f' sits on columns <code>{esc(json.dumps(dist["witness"], separators=(",", ":")))}</code>' if dist.get("witness") else " exists")
           + ".</p>" if dist.get("upper") is not None else "")
        + (f"<p>Its source certifies {tex(('d=' if cert['is_exact'] else 'd\\ge ') + str(cert['d']))}"
           f"{', exactly' if cert['is_exact'] else ', as a lower bound'}. That certificate is not re-checked here, "
           f"but rankings on this site may use it."
           + (f' <span class="small muted">Source: {esc(cert.get("source"))}.</span>' if cert.get("source") else "")
           + "</p>" if cert else "")
        + '<p class="small muted">A fault is a set of faulty columns. It is undetectable when their check parts '
          "cancel, and damaging when their output parts do not.</p>")
    refs = record.get("references") or []
    source_panel = (
        f'<p style="margin:0">{reference_html(refs[0])}</p>' if len(refs) == 1 else
        '<ul class="plain source-list">' + "".join(f"<li>{reference_html(x)}</li>" for x in refs) + "</ul>"
        if refs else '<p class="muted">No source is recorded for this factory.</p>')
    sources = prov.get("sources") or []
    provenance_panel = (
        (f"<p>{esc(prov['strongest_claim'])}</p>" if prov.get("strongest_claim") else "")
        + ('<p class="small">Found by: ' + " ".join(
            f'<a class="tag" href="search.html?regime={quote(x)}">{esc(x)}</a>' for x in prov.get("regimes") or [])
           + "</p>" if prov.get("regimes") else "")
        + (f'<p class="small">Discovery: <strong>{esc(prov["discovery"])}</strong></p>' if prov.get("discovery") else "")
        + (f"<details><summary>{len(sources)} recorded source{'' if len(sources) == 1 else 's'}</summary>"
           f'<pre class="raw">{esc(json.dumps(sources, indent=1))}</pre></details>' if sources else ""))

    # related: the other gates here, the same (n, k) at other distances, and the
    # nearest lengths with the same k and d
    same = [by_id[i] for i in groups[(n, k, d)]["ids"] if i != label]
    other_d = [g for key, g in groups.items() if key[:2] == (n, k) and key[2] != d]
    near = sorted((g for key, g in groups.items() if key[1:] == (k, d) and key[0] != n),
                  key=lambda g: abs(g["n"] - n))[:6]
    related = []
    if same:
        related.append("<h4>Same parameters</h4><ul>" + "".join(
            f'<li><a href="{factory_path(f["id"])}">{gate_tex(f["gate_human"][:40] + ("..." if len(f["gate_human"]) > 40 else ""))}</a></li>'
            for f in same[:8]) + ("<li>…</li>" if len(same) > 8 else "") + "</ul>")
    if other_d:
        related.append("<h4>Other distances</h4><ul>" + "".join(
            f'<li><a href="{params_path(g["n"], g["k"], g["d"])}">{params_tex(g["n"], g["k"], g["d"])}</a></li>' for g in other_d) + "</ul>")
    if near:
        related.append("<h4>Nearest lengths, same " + tex("k") + " and " + tex("d") + "</h4><ul>" + "".join(
            f'<li><a href="{params_path(g["n"], g["k"], g["d"])}">{params_tex(g["n"], g["k"], g["d"])}</a></li>' for g in near) + "</ul>")
    issue = (f"{REPO}/issues/new?title={quote(f'Factory {label}: ')}"
             f"&body={quote(f'Factory {label} at {SITE}{factory_path(label)}' + chr(10) + chr(10) + 'What looks wrong:' + chr(10))}")

    side = f"""
  <aside class="side">
    <section>
      <h3>Download</h3>
      <ul class="plain small">
        <li><a id="download-json" href="data/factories/{esc(label)}.json" download="factory-{esc(label)}.json">Record (JSON)</a></li>
        <li><button type="button" class="linkish" id="download-csv">Matrix (CSV)</button></li>
        <li><button type="button" class="linkish" id="copy-columns">Copy columns</button></li>
        <li><button type="button" class="linkish" id="copy-numpy">Copy as numpy</button></li>
      </ul>
    </section>
    {"<section class='related'><h3>Related</h3>" + "".join(related) + "</section>" if related else ""}
    <section>
      <h3>Something wrong?</h3>
      <p class="small"><a href="{esc(issue)}">Report a problem with this factory</a></p>
    </section>
  </aside>"""

    body = f"""
<main id="main" class="wide entry" data-label="{esc(label)}" data-k="{k}">
  <div class="entry-grid">
  <div class="entry-main">
  <h2 id="matrix" style="margin-top:8px">The circuit</h2>
  <p class="section-intro" id="matrix-caption">{caption}</p>
  <div class="matrix-bar">
    <ul class="legend">
      <li><span class="swatch out" aria-hidden="true"></span>output wires</li>
      <li><span class="swatch chk" aria-hidden="true"></span>check wires, measured and postselected</li>
    </ul>
    <div class="seg" role="group" aria-label="matrix view">
      <button type="button" id="view-cells" aria-pressed="true">Cells</button>
      <button type="button" id="view-digits" aria-pressed="false">0 / 1</button>
    </div>
  </div>
  <div class="matrix-wrap cells" id="matrix-wrap" tabindex="0" role="region" aria-label="binary matrix, scrollable">{matrix_html(record)}</div>
  <p class="small muted" id="matrix-note">The gate is read off the output rows. An output row of odd weight gives a T, a pair of output rows with odd overlap gives a CS, and an odd triple overlap gives a CCZ. The circuit is a valid factory because every such parity that touches a check row is even.</p>

  <h2 id="metrics">Figures of merit</h2>
  <div class="metrics" id="metric-grid">{metrics}</div>

  <h2 id="gate">Output gate</h2>
  <div class="panel" id="gate-panel">{gate_panel}</div>

  <h2 id="transform">Convert the output with CNOT and S</h2>
  <div class="panel" id="transform-panel">
    <p class="small muted" id="tf-intro">A CNOT circuit on the outputs, followed by S, Z and CZ gates, turns this factory's gate into other gates that prepare the same magic state. Type a target gate to check whether it is reachable. If it is, you get the circuit, checked on every basis state.</p>
    <form class="tf-row" id="tf-form" autocomplete="off">
      <label class="sr-only" for="tf-target">Target gate</label>
      <input id="tf-target" type="text" spellcheck="false" placeholder="e.g. T0·CS01   or   0+01">
      <button type="submit" class="btn primary" id="tf-check">Check and construct</button>
      <button type="button" class="btn" id="tf-random" title="fill in this gate after a random change of output basis">Random equivalent gate</button>
    </form>
    <div id="tf-result" aria-live="polite"></div>
    <div class="tf-all">
      <p class="small muted" id="eq-intro">Or list every gate it reaches. The list is built in your browser and saved as a text file, one gate per line.</p>
      <p><button type="button" class="btn" id="eq-list">List all equivalent gates</button> <span class="small muted" id="eq-status" aria-live="polite"></span></p>
      <details id="eq-code"><summary>Python code that writes the same list</summary>
        <pre class="raw code" id="eq-snippet">{esc(equivalents_snippet(label))}</pre>
        <button type="button" class="btn" id="copy-eq-code">Copy code</button>
      </details>
    </div>
  </div>

  <h2 id="distance">Distance</h2>
  <div class="panel" id="distance-panel">{distance_panel}</div>

  <h2 id="source">Original source</h2>
  <div class="panel" id="source-panel">{source_panel}</div>

  <h2 id="provenance">Provenance</h2>
  <div class="panel" id="provenance-panel">{provenance_panel}</div>

  <h2 id="code">Use it in code</h2>
  <div class="panel">
    <p class="small muted">Load this factory and re-derive every number from its circuit with the
    catalogue's own verifier.</p>
    <pre class="raw code" id="code-snippet">{esc(code_snippet(label))}</pre>
    <button type="button" class="btn" id="copy-code">Copy code</button>
  </div>

  <h2>Raw record</h2>
  <div class="panel">
    <details id="raw-details"><summary>Show the JSON this page is built from</summary><pre class="raw" id="raw"></pre></details>
    <p class="small muted" style="margin:10px 0 0">Source: <a href="{REPO}/blob/main/master_catalog/master_catalog.json">master_catalog.json</a>, <code>factories[{record["row"]}]</code>.</p>
  </div>
  </div>
  {side}
  </div>
</main>"""
    return head + body


def factory_page(record, summary, groups, by_id, stamp):
    p = record["parameters"]
    label = record["id"]
    gate = record["gate"]["human"]
    gate = gate if len(gate) <= 40 else gate[:37] + "..."
    title = f"{params_text(p['n'], p['k'], p['d'])} factory, {gate} · Magic State Factory Catalog"
    desc = (f"Magic-state factory {params_text(p['n'], p['k'], p['d'])} with output gate "
            f"{record['gate']['human'][:120]}. Binary matrix, distance, overhead exponents and original source.")
    return title, desc, factory_main(record, summary, groups, by_id, stamp)


# ------------------------------------------------------------ parameter page
def params_main(group, members, groups) -> str:
    n, k, d = group["n"], group["k"], group["d"]
    rows = "".join(
        f'<tr class="clickable" data-href="{factory_path(f["id"])}">'
        f'<td class="gate"><a href="{factory_path(f["id"])}">{gate_tex(f["gate_human"])}</a>'
        + (f' <span class="tag">{f["terms"]} terms</span>' if f["gate_truncated"] else "")
        + (' <span class="tag pure">pure T</span>' if f["pure_t"] else "") + "</td>"
        f'<td class="num">{num(f["gamma_rho_claim"])}{claim_mark(f)}</td>'
        f'<td class="num">{f["N"]}</td>'
        f'<td>{distance_tags(f["d"], f["d_is_exact"], f["d_cert"], f["d_cert_exact"])}</td>'
        f'<td class="small cites">{esc(f.get("cite_text") or "—")}</td></tr>'
        for f in members)
    others = [g for key, g in groups.items() if key[:2] == (n, k) and key[2] != d]
    near = sorted((g for key, g in groups.items() if key[1:] == (k, d) and key[0] != n),
                  key=lambda g: abs(g["n"] - n))[:12]
    links = lambda gs: " · ".join(f'<a href="{params_path(g["n"], g["k"], g["d"])}">{params_tex(g["n"], g["k"], g["d"])}</a>' for g in gs)
    neighbours = "<br>".join(
        ([f"Same {tex('n')} and {tex('k')} at other distances: {links(others)}"] if others else [])
        + ([f"Nearest lengths with the same {tex('k')} and {tex('d')}: {links(near)}"] if near else []))
    count = len(members)
    return f"""
<section class="page-head narrow">
  <div class="inner">
    <nav class="crumbs" aria-label="breadcrumb"><span><a href="index.html">Home</a></span><span><a href="index.html#parameters">Parameters</a></span><span id="crumb">{params_tex(n, k, d)}</span></nav>
    <h1 id="heading">{params_tex(n, k, d)}</h1>
    <p class="lede" id="blurb">{"One factory" if count == 1 else f"{count} inequivalent factories"} with {tex(f"n={n}")} inputs, {tex(f"k={k}")} {"output" if k == 1 else "outputs"} and distance {tex(f"d={d}")}.</p>
  </div>
</section>

<main id="main" data-n="{n}" data-k="{k}" data-d="{d}">
  <div class="table-wrap">
    <table id="table">
      <caption class="sr-only">Inequivalent gates at {esc(params_text(n, k, d))}. Click a column header to sort.</caption>
      <thead><tr>
        <th data-key="gate_human" data-type="text" scope="col">output gate</th>
        <th class="num" data-key="gamma_rho_claim" data-type="number" scope="col">{tex(r"\gamma_\rho")}</th>
        <th class="num" data-key="N" data-type="number" scope="col">{tex("N")}</th>
        <th data-key="d_is_exact" data-type="text" scope="col">distance</th>
        <th data-key="cite_text" data-type="text" scope="col">cited</th>
      </tr></thead>
      <tbody id="body">{rows}</tbody>
    </table>
  </div>
  {f'<p class="small muted" style="margin-top:14px">These factories share {tex("n")}, {tex("k")} and {tex("d")} but prepare different magic states. No CNOT circuit with S, Z and CZ corrections turns one of these gates into another.</p>' if count > 1 else ""}
  {f'<p class="small" id="neighbours" style="margin-top:18px">{neighbours}</p>' if neighbours else ""}
</main>"""


def params_page(group, members, groups):
    n, k, d = group["n"], group["k"], group["d"]
    title = f"{params_text(n, k, d)} · Magic State Factory Catalog"
    desc = (f"{len(members)} inequivalent magic-state factor{'y' if len(members) == 1 else 'ies'} with "
            f"{n} inputs, {k} output{'s' if k != 1 else ''} and distance {d}.")
    return title, desc, params_main(group, members, groups)
