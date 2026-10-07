/* The "Convert the output with CNOT and S" panel on factory.html.
 *
 *   target gate (typed)  --GLEquiv.transform-->  witness A, or a proof of "no"
 *                        --GLEquiv.construct-->  CNOT circuit + S/Z/CZ, checked
 *                                                on all 2^k basis states
 *
 * When the target is not reachable from this factory, the catalogue is
 * scanned for the factories (same k) that do produce it, cheapest first.
 * Factory.html calls Transform.mount(record) once the record has loaded.
 */
(function (global) {
  "use strict";
  var C = global.Catalog, G = global.GLEquiv;
  var MAX_DRAWN = 80;                    /* gates; past this the diagram is skipped */
  var MAX_LISTED = 50000;                /* equivalent gates listed in the browser */

  function $(id) { return document.getElementById(id); }

  /* A small circuit diagram: k wires, one column per gate. */
  function diagram(k, circuit) {
    var cols = circuit.cnots.map(function (g) { return { type: "cx", c: g.control, t: g.target }; })
      .concat(circuit.singles.map(function (s) { return { type: "1q", q: s.q, label: s.power === 1 ? "S" : s.power === 2 ? "Z" : "S†" }; }))
      .concat(circuit.czs.map(function (p) { return { type: "cz", a: p[0], b: p[1] }; }));
    if (!cols.length || cols.length > MAX_DRAWN || k > 16) return "";
    var dx = 30, dy = 26, left = 38, top = 14;
    var W = left + cols.length * dx + 18, H = top * 2 + (k - 1) * dy;
    var y = function (q) { return top + q * dy; };
    var parts = [];
    for (var q = 0; q < k; q++) {
      parts.push('<text class="cw-l" x="0" y="' + (y(q) + 4) + '">out ' + q + "</text>");
      parts.push('<line class="cw" x1="' + (left - 6) + '" y1="' + y(q) + '" x2="' + (W - 4) + '" y2="' + y(q) + '"/>');
    }
    cols.forEach(function (g, i) {
      var x = left + 10 + i * dx;
      if (g.type === "cx") {
        parts.push('<line class="cv" x1="' + x + '" y1="' + y(g.c) + '" x2="' + x + '" y2="' + y(g.t) + '"/>');
        parts.push('<circle class="cdot" cx="' + x + '" cy="' + y(g.c) + '" r="3.5"/>');
        parts.push('<circle class="ctarget" cx="' + x + '" cy="' + y(g.t) + '" r="7"/>');
        parts.push('<line class="cv" x1="' + (x - 7) + '" y1="' + y(g.t) + '" x2="' + (x + 7) + '" y2="' + y(g.t) + '"/>');
        parts.push('<line class="cv" x1="' + x + '" y1="' + (y(g.t) - 7) + '" x2="' + x + '" y2="' + (y(g.t) + 7) + '"/>');
      } else if (g.type === "cz") {
        parts.push('<line class="cv" x1="' + x + '" y1="' + y(g.a) + '" x2="' + x + '" y2="' + y(g.b) + '"/>');
        parts.push('<circle class="cdot" cx="' + x + '" cy="' + y(g.a) + '" r="3.5"/>');
        parts.push('<circle class="cdot" cx="' + x + '" cy="' + y(g.b) + '" r="3.5"/>');
      } else {
        parts.push('<rect class="cbox" x="' + (x - 10) + '" y="' + (y(g.q) - 9) + '" width="20" height="18" rx="2"/>');
        parts.push('<text class="cbox-l" x="' + x + '" y="' + (y(g.q) + 4) + '" text-anchor="middle">' + g.label + "</text>");
      }
    });
    return '<div class="circ-wrap"><svg class="circ" viewBox="0 0 ' + W + " " + H + '" width="' + W +
      '" role="img" aria-label="CNOT and Clifford correction circuit">' + parts.join("") + "</svg></div>";
  }

  function qiskit(k, circuit, target) {
    var lines = ["from qiskit import QuantumCircuit", "",
                 "# after the factory: turns its output into " + target,
                 "qc = QuantumCircuit(" + k + ")"];
    circuit.cnots.forEach(function (g) { lines.push("qc.cx(" + g.control + ", " + g.target + ")"); });
    circuit.singles.forEach(function (s) {
      lines.push("qc." + (s.power === 1 ? "s" : s.power === 2 ? "z" : "sdg") + "(" + s.q + ")");
    });
    circuit.czs.forEach(function (p) { lines.push("qc.cz(" + p[0] + ", " + p[1] + ")"); });
    return lines.join("\n") + "\n";
  }

  function gateList(circuit) {
    var items = circuit.cnots.map(function (g) { return "CNOT " + g.control + "→" + g.target; })
      .concat(circuit.singles.map(function (s) { return (s.power === 1 ? "S" : s.power === 2 ? "Z" : "S†") + " on " + s.q; }))
      .concat(circuit.czs.map(function (p) { return "CZ " + p[0] + "," + p[1]; }));
    return items.length ? items.map(function (t) { return '<code class="g">' + C.escapeHtml(t) + "</code>"; }).join(" ")
                        : '<span class="muted">nothing, the gates are already equal</span>';
  }

  function mount(record) {
    var k = record.parameters.k, own = record.gate.monomials || [];
    var input = $("tf-target"), out = $("tf-result");
    if (!input) return;
    if (k > G.LABEL_K_CAP) {
      $("tf-intro").innerHTML += " <strong>With " + k + " outputs, only identical gates can be " +
        "checked in the browser. The limit is " + G.LABEL_K_CAP + ".</strong>";
      $("tf-random").disabled = true;
    }

    $("tf-random").addEventListener("click", function () {
      var monos = G.randomEquivalent(k, own);
      if (monos) { input.value = G.human(monos, k); check(); }
    });
    $("tf-form").addEventListener("submit", function (event) { event.preventDefault(); check(); });

    /* Every equivalent gate, found in slices so the page stays responsive. */
    var listButton = $("eq-list"), status = $("eq-status");
    if (listButton && k > G.ORBIT_K_CAP) {
      listButton.disabled = true;
      status.textContent = "With " + k + " outputs, use the Python code below.";
    } else if (listButton) listButton.addEventListener("click", function () {
      listButton.disabled = true;
      var walker = G.orbitWalker(k, own, MAX_LISTED);
      (function slice() {
        walker.step(200);
        if (!walker.done && !walker.overflow) {
          status.textContent = walker.count().toLocaleString() + " gates so far…";
          setTimeout(slice, 0);
          return;
        }
        listButton.disabled = false;
        if (walker.overflow) {
          status.textContent = "More than " + MAX_LISTED.toLocaleString() + " gates are equivalent to this one, " +
            "too many to list here. The Python code below takes a limit you can raise.";
          $("eq-code").open = true;
          return;
        }
        var gates = walker.gates().map(function (g) { return G.human(g, k); });
        var p = record.parameters;
        C.download("equivalent-gates-" + record.id + ".txt",
          "# [[" + p.n + "," + p.k + "," + p.d + "]] factory, output gate " + record.gate.human + "\n" +
          "# " + gates.length + " gate" + (gates.length === 1 ? "" : "s") + " reachable with a CNOT circuit and S, Z, CZ on the outputs,\n" +
          "# up to Clifford corrections. Fewest terms first.\n" + gates.join("\n") + "\n", "text/plain");
        status.textContent = gates.length.toLocaleString() + " gate" + (gates.length === 1 ? "" : "s") + ", saved as a text file.";
      }());
    });

    function check() {
      var target;
      try { target = G.parseGate(input.value, k); } catch (e) {
        out.innerHTML = '<p class="tf-msg bad">' + C.escapeHtml(e.message) + "</p>";
        return;
      }
      var name = G.human(target, k);
      var started = performance.now();
      var verdict = G.transform(k, own, target);
      if (verdict.status === "found" || verdict.status === "equal") {
        var circuit = G.construct(k, own, target, verdict);
        if (!circuit.ok) {
          out.innerHTML = '<p class="tf-msg bad">Internal check failed: ' + C.escapeHtml(circuit.reason) +
            ". Please report this factory id.</p>";
          return;
        }
        var ms = Math.max(1, Math.round(performance.now() - started));
        var gates = circuit.cnots.length + circuit.singles.length + circuit.czs.length;
        if (!gates) {
          out.innerHTML = '<p class="tf-verdict ok"><strong>✓ Same gate.</strong> ' + C.gateTex(name) +
            " is already this factory's gate, up to Clifford corrections. Nothing to apply.</p>";
          return;
        }
        out.innerHTML =
          '<p class="tf-verdict ok"><strong>✓ Reachable.</strong> Apply ' +
          circuit.cnots.length + " CNOT" + (circuit.cnots.length === 1 ? "" : "s") + " and then " +
          (circuit.singles.length + circuit.czs.length) + " Clifford correction" +
          (circuit.singles.length + circuit.czs.length === 1 ? "" : "s") + " to the outputs to get " +
          C.gateTex(name) + ".</p>" +
          diagram(k, circuit) +
          '<p class="tf-gates">' + gateList(circuit) + "</p>" +
          '<p class="small muted tf-check">Checked on all ' + circuit.checked + " basis states. The " +
          "converted gate matches the target exactly, up to a global phase (" + ms + " ms).</p>" +
          '<p><button type="button" class="btn" id="tf-copy">Copy as Qiskit</button></p>';
        var copy = $("tf-copy");
        if (copy) copy.addEventListener("click", function (event) { C.copy(qiskit(k, circuit, name), event.currentTarget); });
        return;
      }
      out.innerHTML =
        '<p class="tf-verdict ' + (verdict.status === "no" ? "no" : "maybe") + '"><strong>' +
        (verdict.status === "no" ? "✗ Not reachable" : "? Undecided") + ".</strong> " +
        (verdict.status === "no" ? "No CNOT and S circuit turns this factory's gate into "
                                 : "Could not decide whether this factory reaches ") +
        C.gateTex(name) + ": " + C.escapeHtml(verdict.reason) + ".</p>" +
        '<div id="tf-elsewhere" class="small muted">Looking for factories that produce it…</div>';
      setTimeout(function () { elsewhere(k, target, name); }, 30);
    }

    /* Which catalogued factories DO produce the target?  Same k only. */
    function elsewhere(k, target, name) {
      C.loadIndex().then(function (index) {
        var hits = [], undecided = 0;
        index.factories.forEach(function (f) {
          if (f.k !== k || f.id === record.id) return;
          var v = G.transform(k, G.parseCatalogGate(f.gate, k), target, 2000000);
          if (v.status === "found" || v.status === "equal") hits.push(f);
          else if (v.status === "undecided") undecided++;
        });
        hits.sort(function (a, b) { return a.n - b.n || b.d - a.d; });
        var node = $("tf-elsewhere");
        if (!node) return;
        node.className = "small";
        node.innerHTML = hits.length
          ? "Factories that produce it, fewest inputs first: " +
            hits.slice(0, 12).map(function (f) {
              return '<a href="' + C.factoryHref(f.id) + '">' + C.paramsTex(f.n, f.k, f.d) + "</a>";
            }).join(" · ") + (hits.length > 12 ? " and " + (hits.length - 12) + " more" : "") + "."
          : "No factory in the catalogue with " + k + " outputs produces it" +
            (undecided ? " (" + undecided + " comparisons undecided)" : "") + ".";
      });
    }
  }

  global.Transform = { mount: mount };
}(window));
