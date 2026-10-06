/* p/<n.k.d>/ -- every gate at one [[n,k,d]].  The table is rendered at build
 * time (pages.py); this script makes its columns sortable and its rows
 * clickable, re-rendering them from data/index.json in the same markup. */
(function () {
  "use strict";
  var C = window.Catalog;
  var main = document.querySelector("main[data-n]");
  if (!main) return;
  var n = Number(main.getAttribute("data-n")), k = Number(main.getAttribute("data-k")),
      d = Number(main.getAttribute("data-d"));
  var body = document.getElementById("body");
  C.clickableRows(body);

  C.loadIndex().then(function (index) {
    window.Query.prepare(index);
    var members = index.factories.filter(function (f) { return f.n === n && f.k === k && f.d === d; });
    function render(sorted) {
      body.innerHTML = sorted.map(function (m) {
        var href = C.factoryHref(m.id);
        return '<tr class="clickable" data-href="' + href + '">' +
          '<td class="lab"><a href="' + href + '">' + C.escapeHtml(m.id) + "</a></td>" +
          '<td class="gate">' + C.gateTex(m.gate_human) +
            (m.gate_truncated ? ' <span class="tag">' + m.terms + " terms</span>" : "") +
            (m.pure_t ? ' <span class="tag pure">pure T</span>' : "") + "</td>" +
          '<td class="num">' + C.num(m.gamma_rho_claim) + C.claimMark(m) + "</td>" +
          '<td class="num">' + m.N + "</td>" +
          "<td>" + C.distanceTag(m) + "</td>" +
          '<td class="small cites">' + C.escapeHtml(m.cite_text || "—") + "</td></tr>";
      }).join("");
    }
    C.sortable(document.getElementById("table"), members, render, { key: "label_order", direction: 1 });
  }).catch(function (error) {
    if (window.console) console.error(error);
  });
}());
