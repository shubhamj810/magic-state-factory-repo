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
      label.innerHTML = '<input type="checkbox" name="d" value="' + d + '">' + C.tex("d=" + d) +
                        ' <span class="cnt" data-count="d:' + d + '"></span>';
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
      if (s.sort === "label_order" && s.dir === 1) { delete s.sort; delete s.dir; }
      history.replaceState(null, "", window.location.pathname + Q.writeState(s));
    }

    /* ------------------------------------------------------------ rendering */
    function row(f) {
      var href = C.factoryHref(f.id);
      return '<tr class="clickable" data-href="' + href + '" data-id="' + f.id + '">' +
        '<td class="params" data-col="params"><button type="button" class="peek" aria-expanded="false" ' +
          'aria-label="preview the matrix" title="preview the matrix">&#9656;</button>' +
          '<a href="' + href + '" aria-label="' + C.params(f.n, f.k, f.d) + '">' + C.paramsTex(f.n, f.k, f.d) + "</a></td>" +
        '<td class="gate" data-col="gate"><a href="' + href + '" aria-label="' + C.escapeHtml(f.gate_human) + '">' + C.gateTex(f.gate_human) + "</a>" +
          (f.gate_truncated ? ' <span class="tag" title="the full gate is on the factory page">' +
                              f.terms + " terms</span>" : "") +
          (f.pure_t ? ' <span class="tag pure">pure T</span>' : "") + "</td>" +
        '<td class="num" data-col="N">' + f.N + "</td>" +
        '<td class="num" data-col="gamma_rho">' + C.num(f.gamma_rho_claim) + C.claimMark(f) + "</td>" +
        '<td class="num" data-col="gamma">' + C.num(f.gamma_claim) + C.claimMark(f) + "</td>" +
        '<td data-col="distance">' + C.distanceTag(f) + "</td>" +
        '<td data-col="found"><span class="tag ' + (f.discovery === "AI search" ? "ai" : "pre") + '" title="' +
          C.escapeHtml(f.regimes.join("\n")) + '">' + C.escapeHtml(f.discovery || "—") + "</span></td>" +
        '<td class="small cites" data-col="cited">' + C.escapeHtml(f.cite_text || "—") + "</td>" +
        '<td class="num" data-col="tcount">' + C.integer(f.t_count) + "</td></tr>";
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
      chips();
      counts();
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
                       { key: state.sort || "label_order", direction: state.dir === -1 ? -1 : 1 },
                       function (s) { state.sort = s.key; state.dir = s.direction; state.page = 1; });

    function update() {
      state = read();
      state.page = 1;
      table.refresh();
    }

    function reset() {
      state = {};
      show();
      table.set({ key: "label_order", direction: 1 });
    }

    /* ---------------------------------------------------- active filters */
    /* Every active filter as a chip with an x, plus "Clear all" (Baymard). */
    function chips() {
      var list = [];
      function add(text, drop) { list.push({ text: text, drop: drop }); }
      if (state.q) add("“" + C.escapeHtml(state.q) + "”", function (s) { delete s.q; });
      [["nmin", "n\\ge "], ["nmax", "n\\le "], ["kmin", "k\\ge "], ["kmax", "k\\le "],
       ["grmax", "\\gamma_\\rho\\le "]].forEach(function (pair) {
        if (state[pair[0]] !== undefined) add(C.tex(pair[1] + state[pair[0]]), function (s) { delete s[pair[0]]; });
      });
      (state.d || []).forEach(function (v) {
        add(C.tex("d=" + v), function (s) { s.d = s.d.filter(function (x) { return x !== v; }); });
      });
      (state.has || []).forEach(function (v) {
        add("has " + v.toUpperCase(), function (s) { s.has = s.has.filter(function (x) { return x !== v; }); });
      });
      if (state.exact) add("exact distance", function (s) { delete s.exact; });
      if (state.pure) add("pure " + C.tex(C.TEX.pure), function (s) { delete s.pure; });
      if (state.tmax !== undefined) add("T-count &le; " + state.tmax, function (s) { delete s.tmax; });
      if (state.known) add("T-count known", function (s) { delete s.known; });
      if (state.lit) add("from the literature", function (s) { delete s.lit; });
      if (state.disc) add(C.escapeHtml(state.disc), function (s) { delete s.disc; });
      if (state.regime) add(C.escapeHtml(state.regime), function (s) { delete s.regime; });
      if (state.cite) add("cites " + C.escapeHtml(C.referenceShort(index, state.cite)), function (s) { delete s.cite; });
      var node = $("chips");
      node.innerHTML = list.map(function (c, i) {
        return '<button type="button" class="chip" data-i="' + i + '" aria-label="remove this filter">' +
               c.text + ' <span aria-hidden="true">&times;</span></button>';
      }).join("") + (list.length > 1 ? '<button type="button" class="linkish" id="clear-all">Clear all</button>' : "");
      node.querySelectorAll("button.chip").forEach(function (b) {
        b.addEventListener("click", function () {
          list[Number(b.getAttribute("data-i"))].drop(state);
          state.page = 1;
          show();
          table.refresh();
        });
      });
      var clear = $("clear-all");
      if (clear) clear.addEventListener("click", reset);
    }

    /* How many results each pill would give, with every other filter as it is. */
    function counts() {
      function size(s) { return Q.filter(all, s).rows.length; }
      function copy() { return JSON.parse(JSON.stringify(state)); }
      document.querySelectorAll("[data-count]").forEach(function (span) {
        var key = span.getAttribute("data-count").split(":"), s = copy();
        if (key[0] === "d") s.d = [key[1]];
        else if (key[0] === "has") s.has = (s.has || []).filter(function (x) { return x !== key[1]; }).concat([key[1]]);
        else s[key[0]] = true;
        var c = size(s);
        span.textContent = c;
        span.parentNode.classList.toggle("zero", c === 0);
      });
    }

    /* --------------------------------------------------- column chooser */
    var COLUMNS = [["params", "[[n, k, d]]"], ["gate", "output gate"], ["N", "N"], ["gamma_rho", "γρ"],
                   ["gamma", "γ"], ["distance", "distance"], ["found", "found by"], ["cited", "cited"],
                   ["tcount", "T-count"]];
    var hidden = ["tcount"];
    try { var saved = JSON.parse(localStorage.getItem("msfc-hidden-cols")); if (Array.isArray(saved)) hidden = saved; }
    catch (e) { /* storage unavailable: keep the default */ }
    function applyColumns() {
      COLUMNS.forEach(function (c) { $("table").classList.toggle("hide-" + c[0], hidden.indexOf(c[0]) >= 0); });
      try { localStorage.setItem("msfc-hidden-cols", JSON.stringify(hidden)); } catch (e) { /* ignore */ }
    }
    $("colpick-menu").innerHTML = COLUMNS.map(function (c) {
      return '<label class="check"><input type="checkbox" value="' + c[0] + '"' +
             (hidden.indexOf(c[0]) < 0 ? " checked" : "") + "> " + c[1] + "</label>";
    }).join("");
    $("colpick-menu").addEventListener("change", function (event) {
      var v = event.target.value;
      hidden = event.target.checked ? hidden.filter(function (x) { return x !== v; }) : hidden.concat([v]);
      applyColumns();
    });
    applyColumns();

    /* ------------------------------------------------- inline preview */
    $("body").addEventListener("click", function (event) {
      var b = event.target.closest("button.peek");
      if (!b) return;
      var tr = b.closest("tr"), next = tr.nextElementSibling;
      if (next && next.classList.contains("preview")) {
        next.remove();
        b.setAttribute("aria-expanded", "false");
        return;
      }
      b.setAttribute("aria-expanded", "true");
      var id = tr.getAttribute("data-id");
      var row = document.createElement("tr");
      row.className = "preview";
      row.innerHTML = '<td colspan="9"><span class="muted small">loading…</span></td>';
      tr.after(row);
      C.loadFactory(id).then(function (record) {
        var p = record.parameters;
        row.firstChild.innerHTML = (p.n <= 400
          ? '<div class="preview-wrap">' + C.matrixSvg(record, p.n > 120 ? 4 : 7) + "</div>"
          : '<p class="small muted">' + p.n + " columns are too many to preview here.</p>") +
          '<p class="small"><span class="swatch out"></span> outputs <span class="swatch chk"></span> checks · ' +
          '<a href="' + C.factoryHref(id) + '">Open this factory &rarr;</a></p>';
      });
    });

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
