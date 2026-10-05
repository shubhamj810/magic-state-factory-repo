/* Landing page: the hero matrix, stat cards, explore tiles, landmarks, and the
 * paged [[n,k,d]] table.  Every count on the page is computed here from
 * data/index.json, so nothing can drift from the catalogue. */
(function (global) {
  "use strict";
  var C = global.Catalog, Q = global.Query;
  var PAGE = 50;

  function statbar(index) {
    var counts = index.counts, ranges = index.ranges;
    return [
      [counts.factories, "verified factories"],
      [counts.parameter_sets, "distinct [[n, k, d]]"],
      [ranges.n[0] + "–" + ranges.n[1], "n, noisy inputs"],
      [ranges.k[0] + "–" + ranges.k[1], "k, outputs"],
      [ranges.d[0] + "–" + ranges.d[ranges.d.length - 1], "d, distance"]
    ].map(function (pair) {
      return '<div class="stat"><span class="value">' + C.escapeHtml(pair[0]) +
             '</span><span class="label">' + C.escapeHtml(pair[1]) + "</span></div>";
    }).join("");
  }

  /* ------------------------------------------------------- explore tiles */
  function tiles(index) {
    var f = index.factories;
    function count(test) { return f.filter(test).length; }
    var PARETO = "exhaustive classification n<=54 (Pareto point)";
    var list = [
      ["Pure T<sup>⊗k</sup>", "search.html?pure=1",
       count(function (r) { return r.pure_t; }), "k independent T states from one circuit"],
      ["Gates with CCZ", "search.html?has=ccz",
       count(function (r) { return r.ccz_terms > 0; }), "Toffoli-type magic, three outputs at a time"],
      ["Gates with CS", "search.html?has=cs",
       count(function (r) { return r.cs_terms > 0; }), "controlled-S terms on pairs of outputs"],
      ["Distance 5 or more", "search.html?d=5,6,7",
       count(function (r) { return r.d >= 5; }), "the strongest error suppression catalogued"],
      ["Pareto-optimal, n ≤ 54", "search.html?regime=" + encodeURIComponent(PARETO),
       count(function (r) { return r.regimes.indexOf(PARETO) >= 0; }), "undominated in inputs and wires by the exhaustive classification"],
      ["Found by AI search", "search.html?disc=" + encodeURIComponent("AI search"),
       count(function (r) { return r.discovery === "AI search"; }), "classes no classification or SAT search had"],
      ["From the literature", "search.html?lit=1",
       count(Q.isLiterature), "credited to a published paper"],
      ["Best yield, γ<sub>ρ</sub> ≤ 1.2", "search.html?grmax=1.2&sort=gamma_rho",
       count(function (r) { return r.gamma_rho !== null && r.gamma_rho <= 1.2; }), "the frontier of the distillation exponent"]
    ];
    return list.map(function (t) {
      return '<a class="tile" href="' + t[1] + '">' +
        '<span class="t"><span>' + t[0] + '</span><span class="c">' + t[2] + "</span></span>" +
        '<span class="s">' + t[3] + "</span></a>";
    }).join("");
  }

  /* ------------------------------------------- the hero's binary matrix */
  function heroMatrix(record) {
    var p = record.parameters, n = p.n, N = p.N, k = p.k;
    var on = [];
    for (var q = 0; q < N; q++) on.push(new Uint8Array(n));
    record.circuit.columns.forEach(function (col, j) {
      col.forEach(function (w) { if (w < N) on[w][j] = 1; });
    });
    var cell = 20, gap = 3, lab = 58, step = cell + gap;
    var W = lab + n * step - gap, H = N * step - gap;
    var parts = [];
    for (q = 0; q < N; q++) {
      var out = q < k;
      parts.push('<text class="rowlab ' + (out ? "o" : "c") + '" x="0" y="' +
                 (q * step + cell * 0.72) + '">' + (out ? "out " : "check ") + q + "</text>");
      for (var j = 0; j < n; j++) {
        var x = lab + j * step, y = q * step;
        parts.push('<rect class="' + (on[q][j] ? (out ? "cell-out" : "cell-chk") : "cell-zero") +
                   '" x="' + x + '" y="' + y + '" width="' + cell + '" height="' + cell + '" rx="1.5"/>');
      }
    }
    return '<svg viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="' + N + " by " + n +
           ' binary matrix of the ' + C.params(n, k, p.d) + ' factory">' + parts.join("") + "</svg>";
  }

  /* "15", "k=3", "d>=5", "n<40" -- a filter people can type without a manual. */
  function matcher(text) {
    var terms = text.replace(/\s*(>=|<=|=|>|<)\s*/g, "$1").split(/\s+/).filter(Boolean);
    if (!terms.length) return function () { return true; };
    var tests = terms.map(function (term) {
      var m = /^([nkdN])(>=|<=|=|>|<)(\d+)$/.exec(term);
      if (m) {
        var field = m[1] === "N" ? "N_min" : m[1], op = m[2], value = Number(m[3]);
        return function (row) {
          var v = row[field];
          if (v === null || v === undefined) return false;
          return op === "=" ? v === value : op === ">" ? v > value :
                 op === "<" ? v < value : op === ">=" ? v >= value : v <= value;
        };
      }
      return function (row) { return row.label.indexOf(term) >= 0; };
    });
    return function (row) { return tests.every(function (t) { return t(row); }); };
  }

  C.loadIndex().then(function (index) {
    Q.prepare(index);
    document.getElementById("stats").innerHTML = statbar(index);
    document.getElementById("hero-count").textContent = index.counts.factories + " verified";
    document.getElementById("tiles").innerHTML = tiles(index);

    var refs = index.references || {};
    document.getElementById("cite-list").innerHTML =
      ["jain2026symmetry", "wills2026classification"].filter(function (key) { return refs[key]; })
        .map(function (key) { return "<li>" + C.referenceHtml(refs[key]) + "</li>"; }).join("");

    /* The landmarks and the hero read the same index; a failure to draw them
     * must not take the table down with it, so they are mounted defensively. */
    try {
      if (global.Highlights) global.Highlights.mount(index);
    } catch (e) {
      if (global.console) console.error("highlights:", e);
    }
    var bk = index.factories.filter(function (f) { return f.n === 15 && f.k === 1 && f.d === 3; })[0];
    if (bk) {
      C.loadFactory(bk.id).then(function (record) {
        document.getElementById("hm-svg").innerHTML = heroMatrix(record);
        document.getElementById("hm-link").href = C.factoryHref(bk.id);
      }).catch(function (e) { if (global.console) console.error("hero matrix:", e); });
    }

    var rows = index.parameters.map(function (p) {
      p.label = C.params(p.n, p.k, p.d).replace(/\s/g, "");
      p.order = p.n * 10000 + p.k * 10 + p.d;
      return p;
    });

    var select = document.getElementById("dfilter");
    index.ranges.d.forEach(function (d) {
      var o = document.createElement("option");
      o.value = String(d);
      o.textContent = "d = " + d;
      select.appendChild(o);
    });

    var body = document.getElementById("body");
    var count = document.getElementById("count");
    var filter = document.getElementById("filter");
    var pager = document.getElementById("pager");
    var page = 1;

    function render(sorted) {
      var test = matcher(filter.value);
      var wanted = select.value;
      var shown = sorted.filter(function (row) {
        return test(row) && (!wanted || String(row.d) === wanted);
      });
      var pages = Math.max(1, Math.ceil(shown.length / PAGE));
      page = Math.min(page, pages);
      var slice = shown.slice((page - 1) * PAGE, page * PAGE);
      count.textContent = shown.length + " of " + rows.length + " parameter sets" +
        (pages > 1 ? " · page " + page + " of " + pages : "");
      pager.innerHTML = C.pagerHtml(page, pages);
      if (!slice.length) {
        body.innerHTML = '<tr><td colspan="10" class="empty">Nothing matches that filter.</td></tr>';
        return;
      }
      body.innerHTML = slice.map(function (row) {
        var href = C.paramsHref(row.n, row.k, row.d);
        return '<tr class="clickable" data-href="' + href + '">' +
          '<td class="params"><a href="' + href + '">' + C.params(row.n, row.k, row.d) + "</a></td>" +
          '<td class="num">' + row.n + "</td>" +
          '<td class="num">' + row.k + "</td>" +
          '<td><span class="tag"><span class="dot d' + row.d + '"></span>' + row.d + "</span></td>" +
          '<td class="num">' + row.count + "</td>" +
          '<td class="num">' + C.num(row.gamma_rho) + "</td>" +
          '<td class="num">' + C.num(row.gamma) + "</td>" +
          '<td class="num">' + C.num(row.rate, 4) + "</td>" +
          '<td class="num">' + C.integer(row.best_t_count) + "</td>" +
          '<td class="num">' + row.N_min + "</td></tr>";
      }).join("");
    }

    var table = C.sortable(document.getElementById("table"), rows, render,
                           { key: "order", direction: 1 },
                           function () { page = 1; });
    function refilter() { page = 1; table.refresh(); }
    filter.addEventListener("input", refilter);
    select.addEventListener("change", refilter);
    pager.addEventListener("click", function (event) {
      var b = event.target.closest("button[data-page]");
      if (!b || b.disabled) return;
      page = Number(b.getAttribute("data-page"));
      table.refresh();
      document.getElementById("parameters").scrollIntoView({ block: "start" });
    });
    C.clickableRows(body);
  }).catch(function (error) {
    C.fail(document.querySelector("main"), error);
  });
}(window));
