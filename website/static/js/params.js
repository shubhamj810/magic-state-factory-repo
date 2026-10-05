/* params.html?n=..&k=..&d=..  -- every output gate at one [[n,k,d]]. */
(function () {
  "use strict";
  var C = window.Catalog;

  var n = Number(C.query("n")), k = Number(C.query("k")), d = Number(C.query("d"));
  var label = C.params(n, k, d);

  function statbar(members) {
    var gamma = (n && k && d > 1) ? Math.log(n / k) / Math.log(d) : null;
    var counts = members.map(function (m) { return m.t_count; })
                        .filter(function (t) { return !C.blank(t); });
    var rhos = members.map(function (m) { return m.gamma_rho; })
                      .filter(function (g) { return !C.blank(g); });
    return [
      [members.length, members.length === 1 ? "distinct gate" : "distinct gates"],
      [rhos.length ? C.num(Math.min.apply(null, rhos)) : "—", "best γρ"],
      [C.num(gamma), "γ = log(n/k)/log d"],
      [counts.length ? Math.min.apply(null, counts) : "—", "best T-count"],
      [Math.min.apply(null, members.map(function (m) { return m.N; })), "min wires N"]
    ].map(function (pair) {
      return '<div class="stat"><span class="value">' + C.escapeHtml(pair[0]) +
             '</span><span class="label">' + C.escapeHtml(pair[1]) + "</span></div>";
    }).join("");
  }

  C.loadIndex().then(function (index) {
    window.Query.prepare(index);
    var members = index.factories.filter(function (f) {
      return f.n === n && f.k === k && f.d === d;
    });

    document.title = label + " — Magic State Factory Catalog";
    document.getElementById("crumb").innerHTML =
      '<span class="mono">' + C.escapeHtml(label) + "</span>";
    document.getElementById("heading").textContent = label;

    if (!members.length) {
      document.getElementById("blurb").innerHTML =
        "No factory in the catalogue has these parameters. " +
        '<a href="index.html#parameters">Back to the parameter table</a> or ' +
        '<a href="search.html">search the catalogue</a>.';
      document.getElementById("stats").remove();
      document.querySelector(".table-wrap").innerHTML =
        '<p class="empty">Nothing catalogued at ' + C.escapeHtml(label) + ".</p>";
      document.querySelector(".toolbar").remove();
      return;
    }

    document.getElementById("blurb").innerHTML =
      members.length + (members.length === 1 ? " factory" : " inequivalent factories") +
      " consuming <strong>" + n + "</strong> noisy T states to protect <strong>" +
      k + "</strong> output " + (k === 1 ? "wire" : "wires") +
      " at distance <strong>" + d + "</strong>.";
    document.getElementById("stats").innerHTML = statbar(members);

    var body = document.getElementById("body");
    var count = document.getElementById("count");
    var filter = document.getElementById("filter");

    function render(sorted) {
      var needle = filter.value.trim().toLowerCase();
      var shown = needle ? sorted.filter(function (m) {
        return m._text.indexOf(needle) >= 0;
      }) : sorted;
      count.textContent = shown.length + " of " + members.length + " gates";
      if (!shown.length) {
        body.innerHTML = '<tr><td colspan="9" class="empty">No gate matches that filter.</td></tr>';
        return;
      }
      body.innerHTML = shown.map(function (m) {
        var href = C.factoryHref(m.id);
        return '<tr class="clickable" data-href="' + href + '">' +
          '<td class="gate"><a href="' + href + '">' + C.gateHtml(m.gate_human) +
            "</a>" + (m.gate_truncated ? ' <span class="tag">' + m.terms + " terms</span>" : "") +
            (m.pure_t ? ' <span class="tag pure">pure T</span>' : "") + "</td>" +
          '<td class="num">' + m.terms + "</td>" +
          '<td class="num">' + C.integer(m.t_count) + "</td>" +
          '<td class="num">' + C.integer(m.poly_degree) + "</td>" +
          '<td class="num">' + C.num(m.gamma_rho) + "</td>" +
          '<td class="num">' + C.num(m.gamma_t) + "</td>" +
          '<td class="num">' + m.N + "</td>" +
          "<td>" + C.distanceTag(m) + "</td>" +
          '<td class="small cites">' + C.escapeHtml(m.cite_text || "—") + "</td></tr>";
      }).join("");
    }

    var table = C.sortable(document.getElementById("table"), members, render,
                           { key: "t_count", direction: 1 });
    filter.addEventListener("input", table.refresh);
    C.clickableRows(body);

    /* Neighbouring parameter sets: the same (n,k) at other distances, and the
     * same k and d at other lengths -- the two questions a reader asks next. */
    var sameNk = index.parameters.filter(function (p) {
      return p.n === n && p.k === k && p.d !== d;
    });
    var sameKd = index.parameters.filter(function (p) {
      return p.k === k && p.d === d && p.n !== n;
    });
    function links(list) {
      return list.map(function (p) {
        return '<a href="' + C.paramsHref(p.n, p.k, p.d) + '">' +
               C.escapeHtml(C.params(p.n, p.k, p.d)) + "</a>";
      }).join(" · ");
    }
    var parts = [];
    if (sameNk.length) parts.push("Same n and k at other distances: " + links(sameNk));
    if (sameKd.length) {
      parts.push("Same k and d at other lengths: " +
        links(sameKd.slice(0, 12)) +
        (sameKd.length > 12 ? ' · <a href="search.html?kmin=' + k + "&kmax=" + k + "&d=" + d +
                              '">all ' + sameKd.length + "</a>" : ""));
    }
    if (parts.length) {
      document.getElementById("neighbours").innerHTML = parts.join("<br>");
      document.getElementById("neighbours-panel").hidden = false;
    }
  }).catch(function (error) {
    C.fail(document.querySelector("main"), error);
  });
}());
