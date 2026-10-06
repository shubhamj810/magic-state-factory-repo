/* factory.html?id=n0015-k001-d3-1e610403 -- one circuit, in full.
 *
 * THE MATRIX.  A factory is an N x n binary matrix: one ROW per wire, one
 * COLUMN per pi/4 parity rotation, and a 1 where that rotation touches that
 * wire.  Rows 0..k-1 are the outputs, rows k..N-1 the postselected checks, and
 * the two blocks are coloured apart because the whole theory turns on which
 * block a row is in.
 *
 * The widest catalogued circuit has hundreds of thousands of cells.  One <td>
 * per cell would be a page that stutters, so each row is rendered as ONE cell
 * holding a run of <b>/<i> spans, which the browser lays out as text.  Adjacent
 * equal bits share a span, so a typical row is a few dozen nodes.
 */
(function () {
  "use strict";
  var C = window.Catalog;

  /* Per wire, the columns it is in. */
  function wiresOf(record) {
    var N = record.parameters.N, byWire = [];
    for (var q = 0; q < N; q++) byWire.push([]);
    record.circuit.columns.forEach(function (column, j) {
      column.forEach(function (wire) {
        if (wire >= 0 && wire < N) byWire[wire].push(j);
      });
    });
    return byWire;
  }

  /* The N x n matrix as 0/1 rows. */
  function matrix(record) {
    var n = record.parameters.n;
    return wiresOf(record).map(function (members) {
      var row = new Array(n).fill(0);
      members.forEach(function (j) { row[j] = 1; });
      return row;
    });
  }

  /* One matrix row as a run-length-collapsed string of 1s and dots. */
  function bitsHtml(members, n) {
    var set = new Uint8Array(n);
    for (var i = 0; i < members.length; i++) {
      if (members[i] >= 0 && members[i] < n) set[members[i]] = 1;
    }
    var html = "", start = 0;
    for (var j = 1; j <= n; j++) {
      if (j === n || set[j] !== set[start]) {
        var text = new Array(j - start + 1).join(set[start] ? "1" : "·");
        html += (set[start] ? "<b>" : "<i>") + text + (set[start] ? "</b>" : "</i>");
        start = j;
      }
    }
    return html;
  }

  /* A column ruler every 10 columns: |....'....|  with the index above each |. */
  function rulerHtml(n) {
    var ticks = "", labels = "";
    for (var j = 0; j < n; j++) ticks += (j % 10 === 0) ? "|" : (j % 5 === 0 ? "'" : " ");
    for (var t = 0; t < n; t += 10) {
      var text = String(t);
      labels += text;
      if (t + 10 < n) labels += new Array(Math.max(10 - text.length, 1) + 1).join(" ");
    }
    return { ticks: ticks, labels: labels };
  }

  function renderMatrix(record) {
    var n = record.parameters.n, N = record.parameters.N, k = record.parameters.k;
    var byWire = wiresOf(record);
    var ruler = rulerHtml(n);
    var html = '<table class="matrix"><thead>' +
      '<tr><th class="rowlab" scope="col">wire</th><th scope="col"><div class="ruler">' +
      C.escapeHtml(ruler.labels) + '</div><div class="ruler" aria-hidden="true">' +
      C.escapeHtml(ruler.ticks) + "</div></th></tr></thead><tbody>";
    for (var q = 0; q < N; q++) {
      var isOutput = q < k;
      var classes = isOutput ? "out" : "chk";
      if (q === k && k > 0) classes += " divider";
      html += '<tr class="' + classes + '">' +
        '<th class="rowlab" scope="row">' + (isOutput ? "out " : "check ") + q +
        ' <span class="muted">(' + byWire[q].length + ")</span></th>" +
        '<td class="bits">' + bitsHtml(byWire[q], n) + "</td></tr>";
    }
    return html + "</tbody></table>";
  }

  function metric(key, value, note, empty, highlight) {
    var shown = C.blank(value) || value === "—" || value === ""
      ? '<span class="v none">' + (empty || "not computed") + "</span>"
      : '<span class="v">' + C.escapeHtml(value) + "</span>";
    return '<div class="cell' + (highlight ? " key-metric" : "") + '"><span class="k">' + key + "</span>" +
      shown + (note ? '<span class="note">' + note + "</span>" : "") + "</div>";
  }

  var id = C.query("id");
  if (!id) {
    C.fail(document.querySelector("main"), new Error("no ?id= in the URL"));
    return;
  }

  C.loadFactory(id).then(function (record) {
    var p = record.parameters, gate = record.gate, m = record.metrics;
    var cert = record.distance.certified && record.distance.certified.d > p.d ? record.distance.certified : null;
    function atCert(value) {
      return cert && !C.blank(value) ? " At the certified " + C.tex("d=" + cert.d) + ": " + C.num(value, 4) + "." : "";
    }
    var label = C.params(p.n, p.k, p.d);
    var short = gate.human.length > 90 ? gate.human.slice(0, 90) + "…" : gate.human;

    document.title = gate.human.slice(0, 40) + " at " + label + " · Magic State Factory Catalog";
    document.getElementById("heading").innerHTML = C.gateTex(short.replace(/…$/, "..."));
    document.getElementById("crumbs").innerHTML =
      '<span><a href="index.html">Home</a></span>' +
      '<span><a href="index.html#parameters">Parameters</a></span>' +
      '<span><a href="' + C.paramsHref(p.n, p.k, p.d) + '">' + C.paramsTex(p.n, p.k, p.d) + "</a></span>" +
      '<span class="mono">' + C.escapeHtml(record.id) + "</span>";
    document.getElementById("blurb").innerHTML =
      "A " + C.paramsTex(p.n, p.k, p.d) + " factory on " + C.tex("N=" + p.N) +
      " wires: " + C.tex("k=" + p.k) + " output " + (p.k === 1 ? "wire" : "wires") +
      " and " + C.tex("r=" + p.r) + " postselected " + (p.r === 1 ? "check" : "checks") +
      ", consuming " + C.tex("n=" + p.n) + " noisy T states as " + C.tex("\\pi/4") + " parity rotations." +
      '<span class="pills" style="margin-top:10px">' +
      C.distanceTag({ d: p.d, d_is_exact: record.distance.is_exact,
                      d_cert: cert && cert.d, d_cert_exact: cert && cert.is_exact }) + " " +
      (record.provenance && record.provenance.discovery
        ? '<span class="tag ' + (record.provenance.discovery === "AI search" ? "ai" : "pre") + '">' +
          C.escapeHtml(record.provenance.discovery) + "</span> " : "") +
      ((gate.monomials || []).length === p.k && (gate.monomials || []).every(function (t) { return t.length === 1; })
        ? '<span class="tag pure">pure T</span>' : "") + "</span>";

    /* Cells (filled squares) or digits: the same DOM, two stylesheets. */
    var wrap = document.getElementById("matrix-wrap");
    [["view-cells", true], ["view-digits", false]].forEach(function (pair) {
      document.getElementById(pair[0]).addEventListener("click", function () {
        wrap.classList.toggle("cells", pair[1]);
        document.getElementById("view-cells").setAttribute("aria-pressed", String(pair[1]));
        document.getElementById("view-digits").setAttribute("aria-pressed", String(!pair[1]));
      });
    });

    /* ------------------------------------------------------------ matrix */
    document.getElementById("matrix-caption").innerHTML =
      "The " + C.tex(p.N + "\\times" + p.n) + " matrix. Rows are wires and columns are rotations. " +
      "A 1 means the wire takes part in the rotation, and the number beside each wire is its row weight." +
      (p.n > 120 ? " Scroll sideways to see every column." : "");
    document.getElementById("matrix-wrap").innerHTML = renderMatrix(record);
    document.getElementById("matrix-note").innerHTML =
      "The gate is read off the output rows. An output row of odd weight gives a T, a pair of " +
      "output rows with odd overlap gives a CS, and an odd triple overlap gives a CCZ. The circuit " +
      "is a valid factory because every such parity that touches a check row is even.";

    /* ------------------------------------------------------------ export */
    var base = "factory-" + record.id;
    document.getElementById("copy-columns").addEventListener("click", function (event) {
      C.copy(JSON.stringify(record.circuit.columns), event.currentTarget);
    });
    document.getElementById("copy-numpy").addEventListener("click", function (event) {
      C.copy("import numpy as np\n# " + label + ", rows 0.." + (p.k - 1) +
             " are outputs, the rest checks\nM = np.array([\n" +
             matrix(record).map(function (r) { return "    [" + r.join(",") + "],"; }).join("\n") +
             "\n], dtype=np.uint8)\n", event.currentTarget);
    });
    document.getElementById("download-csv").addEventListener("click", function () {
      var rows = matrix(record);
      var header = ["wire", "role"];
      for (var j = 0; j < p.n; j++) header.push("c" + j);
      C.download(base + "-matrix.csv", header.join(",") + "\n" + rows.map(function (r, q) {
        return [q, q < p.k ? "output" : "check"].concat(r).join(",");
      }).join("\n") + "\n", "text/csv");
    });
    var jsonLink = document.getElementById("download-json");
    jsonLink.href = C.DATA + "factories/" + record.id + ".json";
    jsonLink.setAttribute("download", base + ".json");

    /* ----------------------------------------------------------- metrics */
    document.getElementById("metric-grid").innerHTML =
      metric("inputs " + C.tex("n"), p.n, "Noisy T states per run.") +
      metric("outputs " + C.tex("k"), p.k) +
      metric("distance " + C.tex("d"), (record.distance.is_exact ? "" : "≥ ") + p.d,
             (record.distance.is_exact ? "Exact, proved and witnessed here." : "A lower bound proved here.") +
             (cert ? " Its source certifies " + C.tex("d" + (cert.is_exact ? "=" : "\\ge ") + cert.d) + "." : ""),
             null, true) +
      metric("wires " + C.tex("N"), p.N) +
      metric("checks " + C.tex("r"), p.r) +
      metric("T-count", m.t_count, "Minimal T-count of the output gate." +
             (C.blank(m.t_count) ? " Not computable at this width." : ""), null, true) +
      metric("phase-polynomial degree", m.poly_degree, "Minimised over changes of output basis.") +
      metric(C.tex(C.TEX.vex), m.v_ex, C.blank(m.v_ex)
             ? "Undefined, because the gate's terms overlap."
             : "T states per run. CCZ counts as two.", "not defined") +
      metric(C.tex(C.TEX.grDef), C.num(m.gamma_rho, 4),
             "Overhead per extractable T state. Lower is better." + atCert(m.gamma_rho_claim), "not defined", true) +
      metric(C.tex(C.TEX.gDef), C.num(m.gamma, 4), "Overhead per output qubit." + atCert(m.gamma_claim)) +
      metric(C.tex(C.TEX.gtDef), C.num(m.gamma_t, 4), "Overhead per unit of T-count." + atCert(m.gamma_t_claim)) +
      metric("rate " + C.tex("k/n"), C.num(m.rate, 5), "Outputs per input.") +
      metric("effective width", m.effective_width, "Rank of the output rows modulo the check rows.");

    /* -------------------------------------------------------------- gate */
    var kinds = { 1: 0, 2: 0, 3: 0 };
    (gate.monomials || []).forEach(function (t) { kinds[t.length] += 1; });
    document.getElementById("gate-panel").innerHTML =
      '<div class="gate-terms">' +
        '<span class="term"><b>' + kinds[1] + "</b> T</span>" +
        '<span class="term"><b>' + kinds[2] + "</b> CS</span>" +
        '<span class="term"><b>' + kinds[3] + "</b> CCZ</span>" +
        '<span class="term">on <b>' + p.k + "</b> output " + (p.k === 1 ? "wire" : "wires") + "</span></div>" +
      "<p><strong>As gates:</strong> " + (gate.human.length <= 1500 ? C.gateTex(gate.human)
        : '<code class="wrap">' + C.escapeHtml(gate.human) + "</code>") + "</p>" +
      "<p><strong>As monomials:</strong> <code class=\"wrap\">" + C.escapeHtml(gate.string) + "</code>" +
 ' <span class="small muted">(output wires per term, separated by +)</span></p>' +
      '<p class="small muted">This row stands for every gate that a CNOT circuit and S, Z and CZ ' +
      "gates on the outputs can reach from this one. They all prepare the same magic state. " +
      (gate.sk_canonical_frame
        ? "The wires are shown in the " + C.tex("S_k") + "-canonical frame."
        : "The wires are shown in the labelling of the stored circuit.") + "</p>";

    /* ---------------------------------------------------------- distance */
    var distance = record.distance;
    document.getElementById("distance-panel").innerHTML =
      "<p>" + (distance.is_exact
        ? "<strong>" + C.tex("d=" + distance.d) + ", exact.</strong> No fault of weight below " +
          distance.d + " is both undetectable and damaging. One of weight " + distance.d + " is."
        : "<strong>" + C.tex("d\\ge " + distance.d) + ", a lower bound.</strong> No fault of weight below " +
          distance.d + " is both undetectable and damaging. None of weight " + distance.d +
          " has been found, so the true distance may be larger.") + "</p>" +
      (!C.blank(distance.upper)
        ? '<p class="small">A damaging fault of weight ' + distance.upper +
          (distance.witness ? " sits on columns <code>" +
          C.escapeHtml(JSON.stringify(distance.witness)) + "</code>" : " exists") + ".</p>"
        : "") +
      (cert ? "<p>Its source certifies " + C.tex("d" + (cert.is_exact ? "=" : "\\ge ") + cert.d) +
        (cert.is_exact ? ", exactly" : ", as a lower bound") + ". That certificate is not re-checked " +
        "here, but rankings on this site may use it." +
        (cert.source ? ' <span class="small muted">Source: ' + C.escapeHtml(cert.source) + ".</span>" : "") + "</p>" : "") +
      '<p class="small muted">A fault is a set of faulty columns. It is undetectable when their ' +
      "check parts cancel, and damaging when their output parts do not.</p>";

    /* -------------------------------------------------------- references */
    var references = record.references || [];
    document.getElementById("references-panel").innerHTML =
      (references.length
        ? '<p class="small muted" style="margin-top:0">If you use this factory, please cite</p>' +
          '<ol class="refs">' + references.map(function (r) {
            return "<li>" + C.referenceHtml(r) + "</li>";
          }).join("") + "</ol>" +
          '<p class="small" style="margin:12px 0 0">' + references.map(function (r) {
            return '<a href="search.html?cite=' + encodeURIComponent(r.key) + '">All factories citing ' +
                   C.escapeHtml(r.short || r.key) + "</a>";
          }).join(" · ") + "</p>"
        : '<p class="muted">No reference is recorded for this factory.</p>');

    /* -------------------------------------------------------- provenance */
    var provenance = record.provenance || {};
    var sources = provenance.sources || [];
    document.getElementById("provenance-panel").innerHTML =
      (provenance.strongest_claim
        ? "<p>" + C.escapeHtml(provenance.strongest_claim) + "</p>" : "") +
      (provenance.regimes && provenance.regimes.length
        ? '<p class="small">Found by: ' + provenance.regimes.map(function (r) {
            return '<a class="tag" href="search.html?regime=' + encodeURIComponent(r) + '">' +
                   C.escapeHtml(r) + "</a>";
          }).join(" ") + "</p>" : "") +
      (provenance.discovery
        ? '<p class="small">Discovery: <strong>' + C.escapeHtml(provenance.discovery) + "</strong></p>" : "") +
      (sources.length
        ? "<details><summary>" + sources.length + (sources.length === 1 ? " recorded source" : " recorded sources") +
          '</summary><pre class="raw">' + C.escapeHtml(JSON.stringify(sources, null, 1)) + "</pre></details>"
        : "");

    if (window.Transform) window.Transform.mount(record);

    var shallow = JSON.parse(JSON.stringify(record));
    shallow.circuit = { columns: "[" + p.n + " columns, shown as the matrix above]" };
    document.getElementById("raw").textContent = JSON.stringify(shallow, null, 2);
    document.getElementById("source-line").innerHTML =
      'Source: <a href="' + C.CATALOG_FILE + '">master_catalog.json</a>, ' +
      "<code>factories[" + record.row + "]</code>.";
  }).catch(function (error) {
    C.fail(document.querySelector("main"), error);
  });
}());
