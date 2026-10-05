/* Landing page: the stat bar, the landmarks, and the paged [[n,k,d]] table. */
(function (global) {
  "use strict";
  var C = global.Catalog;
  var PAGE = 50;

  function statbar(index) {
    var counts = index.counts, ranges = index.ranges;
    return [
      [counts.factories, "factories"],
      [counts.parameter_sets, "[[n, k, d]] sets"],
      [ranges.n[0] + "–" + ranges.n[1], "n, inputs consumed"],
      [ranges.k[0] + "–" + ranges.k[1], "k, outputs"],
      [ranges.d.join(", "), "d, distance"]
    ].map(function (pair) {
      return '<div class="stat"><span class="value">' + C.escapeHtml(pair[0]) +
             '</span><span class="label">' + C.escapeHtml(pair[1]) + "</span></div>";
    }).join("");
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
    document.getElementById("stats").innerHTML = statbar(index);
    document.getElementById("hero-count").textContent =
      index.counts.factories + " verified";

    var refs = index.references || {};
    document.getElementById("cite-list").innerHTML =
      ["jain2026symmetry", "wills2026classification"].filter(function (key) { return refs[key]; })
        .map(function (key) { return "<li>" + C.referenceHtml(refs[key]) + "</li>"; }).join("");

    /* The landmarks read the same index; a failure to draw them must not take
     * the table down with it, so they are mounted defensively. */
    try {
      if (global.Highlights) global.Highlights.mount(index);
    } catch (e) {
      if (global.console) console.error("highlights:", e);
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
          '<td class="num">' + row.d + "</td>" +
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
