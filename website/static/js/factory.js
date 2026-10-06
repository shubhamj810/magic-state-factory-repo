/* f/<label>/ -- one factory.  The page is rendered at build time (pages.py);
 * this script only adds what needs a browser:
 *
 *   the Cells | 0/1 view of the matrix     copying the BibTeX
 *   exports (CSV, columns, numpy)          the CNOT + S tool (transform.js)
 *   the raw record, filled in when opened
 *
 * The record JSON is fetched once, for the exports and the tool.
 */
(function () {
  "use strict";
  var C = window.Catalog;
  var main = document.querySelector("main[data-label]");
  if (!main) return;
  var label = main.getAttribute("data-label");

  function $(id) { return document.getElementById(id); }

  /* Cells (filled squares) or digits: the same DOM, two stylesheets. */
  var wrap = $("matrix-wrap");
  [["view-cells", true], ["view-digits", false]].forEach(function (pair) {
    $(pair[0]).addEventListener("click", function () {
      wrap.classList.toggle("cells", pair[1]);
      $("view-cells").setAttribute("aria-pressed", String(pair[1]));
      $("view-digits").setAttribute("aria-pressed", String(!pair[1]));
    });
  });

  $("copy-bibtex").addEventListener("click", function (event) {
    C.copy($("bibtex").textContent, event.currentTarget);
  });

  /* The N x n matrix as 0/1 rows. */
  function matrix(record) {
    var p = record.parameters, rows = [];
    for (var q = 0; q < p.N; q++) rows.push(new Array(p.n).fill(0));
    record.circuit.columns.forEach(function (column, j) {
      column.forEach(function (wire) { if (wire < p.N) rows[wire][j] = 1; });
    });
    return rows;
  }

  C.loadFactory(label).then(function (record) {
    var p = record.parameters;
    var name = C.params(p.n, p.k, p.d);
    $("copy-columns").addEventListener("click", function (event) {
      C.copy(JSON.stringify(record.circuit.columns), event.currentTarget);
    });
    $("copy-numpy").addEventListener("click", function (event) {
      C.copy("import numpy as np\n# " + label + ", " + name + ", rows 0.." + (p.k - 1) +
             " are outputs, the rest checks\nM = np.array([\n" +
             matrix(record).map(function (r) { return "    [" + r.join(",") + "],"; }).join("\n") +
             "\n], dtype=np.uint8)\n", event.currentTarget);
    });
    $("download-csv").addEventListener("click", function () {
      var header = ["wire", "role"];
      for (var j = 0; j < p.n; j++) header.push("c" + j);
      C.download("factory-" + label + "-matrix.csv", header.join(",") + "\n" +
        matrix(record).map(function (r, q) {
          return [q, q < p.k ? "output" : "check"].concat(r).join(",");
        }).join("\n") + "\n", "text/csv");
    });
    $("raw-details").addEventListener("toggle", function () {
      if (!$("raw").textContent) {
        var shallow = JSON.parse(JSON.stringify(record));
        shallow.circuit = { columns: "[" + p.n + " columns, shown as the matrix above]" };
        $("raw").textContent = JSON.stringify(shallow, null, 2);
      }
    });
    if (window.Transform) window.Transform.mount(record);
  }).catch(function (error) {
    if (window.console) console.error(error);
  });
}());
