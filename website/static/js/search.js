/* search.html -- every factory, filtered, sorted, paged and exportable.
 *
 *   URL query string  <->  the controls  ->  Query.filter  ->  sort  ->  page
 *
 * The URL is the single source of the filter state: every change rewrites it
 * (replaceState, so the back button still leaves the page), and loading a URL
 * restores every control.  A search is therefore a link someone can send.
 */
(function () {
  "use strict";
  var C = window.Catalog, Q = window.Query;

  var EXPORT_FIELDS = ["id", "n", "k", "d", "N", "r", "gate_human", "gate", "terms",
                       "t_terms", "cs_terms", "ccz_terms", "pure_t", "t_count",
                       "poly_degree", "effective_width", "gamma", "gamma_t",
                       "gamma_rho", "v_ex", "rate", "d_is_exact", "d_cert", "d_cert_exact",
                       "d_claim", "gamma_claim", "gamma_rho_claim", "discovery",
                       "regimes", "citations", "row"];

  function $(id) { return document.getElementById(id); }

  function option(value, text) {
    var o = document.createElement("option");
    o.value = value;
    o.textContent = text;
    return o;
  }

  function counted(rows, pick) {
    var counts = {};
    rows.forEach(function (r) {
      [].concat(pick(r)).forEach(function (v) { if (v) counts[v] = (counts[v] || 0) + 1; });
    });
    return counts;
  }

  C.loadIndex().then(function (index) {
    Q.prepare(index);
    var all = index.factories;
    var state = Q.readState(window.location.search);
    var current = [];

    /* ------------------------------------------------ populate the controls */
    index.ranges.d.forEach(function (d) {
      var label = document.createElement("label");
      label.className = "pill";
      label.innerHTML = '<input type="checkbox" name="d" value="' + d + '">' + C.tex("d=" + d);
      $("d-checks").appendChild(label);
    });
    var discCounts = counted(all, function (r) { return r.discovery; });
    Object.keys(discCounts).sort().forEach(function (key) {
      var o = option(key, key + " (" + discCounts[key] + ")");
      o.title = (index.discovery || {})[key] || "";
      $("disc").appendChild(o);
    });
    var regimeCounts = counted(all, function (r) { return r.regimes; });
    Object.keys(regimeCounts).sort().forEach(function (key) {
      var o = option(key, key + " (" + regimeCounts[key] + ")");
      o.title = (index.regimes || {})[key] || "";
      $("regime").appendChild(o);
    });
    var citeCounts = counted(all, function (r) { return r.citations; });
    Object.keys(citeCounts).sort(function (a, b) { return citeCounts[b] - citeCounts[a]; })
      .forEach(function (key) {
        $("cite").appendChild(option(key, C.referenceShort(index, key) + " (" + citeCounts[key] + ")"));
      });

    /* state -> controls */
    function show() {
      $("q").value = state.q || "";
      ["nmin", "nmax", "kmin", "kmax", "tmax", "grmax"].forEach(function (key) {
        $(key).value = state[key] === undefined ? "" : state[key];
      });
      ["exact", "pure", "known", "lit"].forEach(function (key) { $(key).checked = !!state[key]; });
      document.querySelectorAll('input[name="d"]').forEach(function (box) {
        box.checked = (state.d || []).indexOf(box.value) >= 0;
      });
      document.querySelectorAll('input[name="has"]').forEach(function (box) {
        box.checked = (state.has || []).indexOf(box.value) >= 0;
      });
      ["disc", "regime", "cite"].forEach(function (key) { $(key).value = state[key] || ""; });
      $("size").value = String(state.size === undefined ? 50 : state.size);
    }

    /* controls -> state */
    function read() {
      var next = { sort: state.sort, dir: state.dir, size: state.size };
      var q = $("q").value.trim();
      if (q) next.q = q;
      ["nmin", "nmax", "kmin", "kmax", "tmax"].forEach(function (key) {
        var v = parseInt($(key).value, 10);
        if (!Number.isNaN(v)) next[key] = v;
      });
      var g = parseFloat($("grmax").value);
      if (!Number.isNaN(g)) next.grmax = g;
      ["exact", "pure", "known", "lit"].forEach(function (key) { if ($(key).checked) next[key] = true; });
      next.d = [].map.call(document.querySelectorAll('input[name="d"]:checked'), function (b) { return b.value; });
      next.has = [].map.call(document.querySelectorAll('input[name="has"]:checked'), function (b) { return b.value; });
      ["disc", "regime", "cite"].forEach(function (key) { if ($(key).value) next[key] = $(key).value; });
      return next;
    }

    function sync() {
      var s = Object.assign({}, state);
      if (s.size === 50) delete s.size;
      if (s.page === 1) delete s.page;
      if (s.sort === "order" && s.dir === 1) { delete s.sort; delete s.dir; }
      history.replaceState(null, "", window.location.pathname + Q.writeState(s));
    }

    /* ------------------------------------------------------------ rendering */
    function row(f) {
      var href = C.factoryHref(f.id);
      return '<tr class="clickable" data-href="' + href + '">' +
        '<td class="params"><a href="' + C.paramsHref(f.n, f.k, f.d) + '" title="all gates at these parameters" aria-label="' +
          C.params(f.n, f.k, f.d) + '">' + C.paramsTex(f.n, f.k, f.d) + "</a></td>" +
        '<td class="gate"><a href="' + href + '" aria-label="' + C.escapeHtml(f.gate_human) + '">' + C.gateTex(f.gate_human) + "</a>" +
          (f.gate_truncated ? ' <span class="tag" title="the full gate is on the factory page">' +
                              f.terms + " terms</span>" : "") +
          (f.pure_t ? ' <span class="tag pure">pure T</span>' : "") + "</td>" +
        '<td class="num">' + f.N + "</td>" +
        '<td class="num">' + C.integer(f.t_count) + "</td>" +
        '<td class="num">' + C.num(f.gamma_rho_claim) + C.claimMark(f) + "</td>" +
        '<td class="num">' + C.num(f.gamma_claim) + C.claimMark(f) + "</td>" +
        "<td>" + C.distanceTag(f) + "</td>" +
        '<td><span class="tag ' + (f.discovery === "AI search" ? "ai" : "pre") + '" title="' +
          C.escapeHtml(f.regimes.join("\n")) + '">' + C.escapeHtml(f.discovery || "—") + "</span></td>" +
        '<td class="small cites">' + C.escapeHtml(f.cite_text || "—") + "</td></tr>";
    }

    function render(sorted) {
      current = sorted;
      var size = state.size === undefined ? 50 : state.size;
      var pages = size ? Math.max(1, Math.ceil(sorted.length / size)) : 1;
      var page = Math.min(Math.max(state.page || 1, 1), pages);
      state.page = page;
      var shown = size ? sorted.slice((page - 1) * size, page * size) : sorted;

      $("count").innerHTML = "<strong>" + sorted.length + "</strong> of " + all.length +
        " factories" + (sorted.length && size && pages > 1
          ? ' <span class="muted">· showing ' + ((page - 1) * size + 1) + "–" +
            ((page - 1) * size + shown.length) + "</span>" : "");
      $("body").innerHTML = shown.length ? shown.map(row).join("")
        : '<tr><td colspan="9" class="empty">No factory matches. ' +
          '<button type="button" class="linkish" id="reset-inline">Reset the search</button></td></tr>';
      $("pager").innerHTML = C.pagerHtml(page, pages);
      ["export-csv", "export-json"].forEach(function (id) { $(id).disabled = !sorted.length; });
      var inline = $("reset-inline");
      if (inline) inline.addEventListener("click", reset);
      sync();
    }

    var notesNode = document.createElement("p");
    notesNode.className = "small muted notes";
    $("search-form").after(notesNode);

    var table;
    function getRows() {
      var result = Q.filter(all, state);
      notesNode.textContent = result.notes.join(" · ");
      return result.rows;
    }

    show();
    table = C.sortable($("table"), getRows, render,
                       { key: state.sort || "order", direction: state.dir === -1 ? -1 : 1 },
                       function (s) { state.sort = s.key; state.dir = s.direction; state.page = 1; });

    function update() {
      state = read();
      state.page = 1;
      table.refresh();
    }

    function reset() {
      state = {};
      show();
      table.set({ key: "order", direction: 1 });
    }

    /* ------------------------------------------------------------- wiring */
    var timer = null;
    $("q").addEventListener("input", function () {
      clearTimeout(timer);
      timer = setTimeout(update, 120);
    });
    $("filters").addEventListener("change", update);
    $("filters").addEventListener("input", function (event) {
      if (event.target.type === "number") { clearTimeout(timer); timer = setTimeout(update, 250); }
    });
    $("size").addEventListener("change", function () {
      state.size = Number($("size").value);
      state.page = 1;
      table.refresh();
    });
    $("reset").addEventListener("click", reset);
    $("pager").addEventListener("click", function (event) {
      var b = event.target.closest("button[data-page]");
      if (!b || b.disabled) return;
      state.page = Number(b.getAttribute("data-page"));
      table.refresh();
      $("results").scrollIntoView({ block: "start" });
    });
    C.clickableRows($("body"));

    $("copy-link").addEventListener("click", function (event) {
      C.copy(window.location.href, event.currentTarget);
    });
    function exportName(ext) {
      return "magic-state-factories-" + current.length + "." + ext;
    }
    function plain(rows) {
      return rows.map(function (f) {
        var o = {};
        EXPORT_FIELDS.forEach(function (key) { o[key] = f[key]; });
        return o;
      });
    }
    $("export-csv").addEventListener("click", function () {
      C.download(exportName("csv"), C.toCsv(plain(current), EXPORT_FIELDS), "text/csv");
    });
    $("export-json").addEventListener("click", function () {
      C.download(exportName("json"), JSON.stringify(plain(current), null, 1), "application/json");
    });

    /* Filters open beside the results on a wide screen, folded on a phone. */
    if (window.matchMedia && window.matchMedia("(max-width: 900px)").matches) {
      $("filters").open = false;
    }
  }).catch(function (error) {
    C.fail(document.querySelector("main"), error);
  });
}());
