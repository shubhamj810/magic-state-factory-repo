/* Landmarks for the landing page: the gamma_rho frontier, per-distance record
 * holders, and a gamma-against-n plot.
 *
 * Everything here is computed in the browser from `data/index.json` -- the same
 * file the tables read.  Nothing is precomputed into the index and nothing is
 * hand-maintained, so a landmark cannot drift out of step with the catalogue it
 * describes: reseed the data, rebuild the index, and these move with it.
 *
 * These rank on gamma_rho = log(n/V_ex)/log(d), NOT on gamma = log(n/k)/log(d),
 * and the distinction is the whole reason this file is careful.  gamma counts
 * output WIRES, so it is not comparable between gates: a CCZ occupies three
 * wires and is worth two T states, which flatters it by half again, and a gate
 * whose monomials OVERLAP has no extractable T count at all.  Ranked on gamma
 * the catalogue's apparent champion is a CCZ web at gamma 0.80 -- a number that
 * cannot be compared with anything and must never be quoted as a record.
 * Ranked honestly on gamma_rho the leader is a pure-T circuit at 1.0566.
 *
 * So: parameter sets whose gates overlap are excluded from every landmark here,
 * and the plot says how many it dropped and why.  LOWER IS BETTER throughout.
 */
(function (global) {
  "use strict";
  var C = global.Catalog;

  /* --------------------------------------------------------------- helpers */

  /* Least gamma_rho wins; a missing one never wins. */
  function bestBy(rows, key) {
    var best = null;
    rows.forEach(function (row) {
      var v = row[key];
      if (v === null || v === undefined || Number.isNaN(v)) return;
      if (best === null || v < best[key]) best = row;
    });
    return best;
  }

  function maxBy(rows, key) {
    var best = null;
    rows.forEach(function (row) {
      var v = row[key];
      if (v === null || v === undefined || Number.isNaN(v)) return;
      if (best === null || v > best[key]) best = row;
    });
    return best;
  }

  function href(row) {
    return C.paramsHref(row.n, row.k, row.d);
  }

  function label(row) {             /* plain text, for SVG titles and aria labels */
    return "\u27e6" + row.n + ", " + row.k + ", " + row.d + "\u27e7";
  }

  function byDistance(parameters) {
    var groups = {};
    parameters.forEach(function (row) {
      if (row.d === null || row.d === undefined) return;
      (groups[row.d] = groups[row.d] || []).push(row);
    });
    return Object.keys(groups)
      .map(Number)
      .sort(function (a, b) { return a - b; })
      .map(function (d) { return { d: d, rows: groups[d] }; });
    }

  /* ------------------------------------------------------- the record cards */

  /* One card per distance: the least-gamma circuit at that d, which is the
   * question the catalogue exists to answer. */
  function recordCards(parameters) {
    return byDistance(parameters).map(function (group) {
      var usable = group.rows.filter(function (r) { return r.comparable; });
      var best = bestBy(usable, "gamma_rho");
      if (!best) return "";
      var widest = maxBy(usable, "v_ex_best");
      return '<a class="record" href="' + href(best) + '">' +
        '<span class="d">' + C.tex("d=" + group.d) + "</span>" +
        '<span class="g">' + C.tex(C.TEX.gr + "=" + C.num(best.gamma_rho, 4)) + "</span>" +
        '<span class="p">' + C.paramsTex(best.n, best.k, best.d) + "</span>" +
        '<span class="meta">' + C.tex(C.TEX.vex + "=" + best.v_ex_best) +
        "</span></a>";
    }).join("");
  }

  /* --------------------------------------------------------- the headline */

  function headline(parameters) {
    var comparable = parameters.filter(function (r) { return r.comparable; });
    var best = bestBy(comparable, "gamma_rho");
    var widest = maxBy(comparable, "v_ex_best");
    var deepest = maxBy(parameters, "d");
    if (!best) return "";
    function cell(title, value, row, note) {
      return '<div class="head-stat">' +
        '<span class="t">' + title + "</span>" +
        '<span class="v">' + value + "</span>" +
        (row ? '<a class="l" href="' + href(row) + '">' + C.paramsTex(row.n, row.k, row.d) + "</a>" : "") +
        (note ? '<span class="n">' + note + "</span>" : "") +
        "</div>";
    }
    return cell("least " + C.tex(C.TEX.gr), C.tex(C.TEX.gr + "=" + C.num(best.gamma_rho, 4)), best,
                C.tex(C.TEX.vex + "=" + best.v_ex_best) + " T states per run") +
           cell("most T states per run", C.tex(C.TEX.vex + "=" + widest.v_ex_best), widest, "") +
           cell("highest distance", C.tex("d=" + deepest.d), deepest, "");
  }

  /* ------------------------------------------------------------- the plot */

  /* SMALL MULTIPLES: one panel per distance, on shared axes.  Within a panel
   * every comparable parameter set is a grey point and the running best
   * gamma_rho as n grows -- the frontier -- is one accent-coloured staircase.
   * Position (which panel) carries the distance, so no colour legend is
   * needed, the frontiers do not tangle, and shared axes keep the panels
   * directly comparable.  Inline SVG: no dependency, nothing to load. */
  var panels = [];                       /* [{d, pts, svg}] for the hover layer */
  var W = 380, H = 236, L = 44, R = 12, T = 30, B = 34;

  function plot(parameters) {
    var pts = parameters.filter(function (r) {
      return r.comparable && r.gamma_rho !== null && r.gamma_rho !== undefined &&
             !Number.isNaN(r.gamma_rho) && r.n > 0;
    });
    var skipped = parameters.length - pts.length;
    if (pts.length < 2) return "";

    var xs = pts.map(function (p) { return Math.log10(p.n); });
    var ys = pts.map(function (p) { return p.gamma_rho; });
    var x0 = Math.min.apply(null, xs) - 0.04, x1 = Math.max.apply(null, xs) + 0.04;
    var y0 = Math.min(0.95, Math.min.apply(null, ys) - 0.05), y1 = Math.max.apply(null, ys) + 0.08;
    var iw = W - L - R, ih = H - T - B;
    function X(n) { return L + (Math.log10(n) - x0) / (x1 - x0) * iw; }
    function Y(g) { return T + ih - (g - y0) / (y1 - y0) * ih; }

    panels = [];
    var html = byDistance(pts).map(function (group) {
      var rows = group.rows.slice().sort(function (a, b) { return a.n - b.n || a.gamma_rho - b.gamma_rho; });
      var run = Infinity, stair = [];
      rows.forEach(function (p) { if (p.gamma_rho < run) { run = p.gamma_rho; stair.push(p); } });
      var best = stair[stair.length - 1];
      var parts = [];

      for (var gy = Math.ceil(y0 * 2) / 2; gy <= y1; gy += 0.5) {
        parts.push('<line class="grid" x1="' + L + '" y1="' + Y(gy).toFixed(1) + '" x2="' + (W - R) +
                   '" y2="' + Y(gy).toFixed(1) + '"/>');
        parts.push('<text class="ax" x="' + (L - 6) + '" y="' + (Y(gy) + 3.5).toFixed(1) +
                   '" text-anchor="end">' + gy.toFixed(1) + "</text>");
      }
      [20, 50, 100, 200, 500, 1000].forEach(function (n) {
        if (Math.log10(n) < x0 || Math.log10(n) > x1) return;
        parts.push('<line class="tick" x1="' + X(n).toFixed(1) + '" y1="' + (T + ih) + '" x2="' +
                   X(n).toFixed(1) + '" y2="' + (T + ih + 4) + '"/>');
        parts.push('<text class="ax" x="' + X(n).toFixed(1) + '" y="' + (T + ih + 15) +
                   '" text-anchor="middle">' + n + "</text>");
      });
      parts.push('<line class="axis" x1="' + L + '" y1="' + (T + ih) + '" x2="' + (W - R) + '" y2="' + (T + ih) + '"/>');
      if (y0 <= 1 && 1 <= y1) {
        parts.push('<line class="unity" x1="' + L + '" y1="' + Y(1).toFixed(1) + '" x2="' + (W - R) +
                   '" y2="' + Y(1).toFixed(1) + '"/>');
      }
      rows.forEach(function (p) {
        p._x = X(p.n); p._y = Y(p.gamma_rho); p._front = stair.indexOf(p) >= 0;
      });
      if (stair.length) {
        var path = "";
        stair.forEach(function (p, i) {
          path += (i === 0 ? "M" : "H" + p._x.toFixed(1) + "V") + (i === 0 ? p._x.toFixed(1) + "," : "") + p._y.toFixed(1);
        });
        path += "H" + (W - R);
        parts.push('<path class="stair" d="' + path + '"/>');
      }
      rows.forEach(function (p, i) {
        parts.push('<circle class="pt' + (p._front ? " front" : "") + '" data-i="' + i + '" cx="' +
                   p._x.toFixed(1) + '" cy="' + p._y.toFixed(1) + '" r="' + (p._front ? 3.6 : 2.6) + '"/>');
      });
      parts.push('<text class="ptitle" x="' + L + '" y="16"><tspan class="mi">d</tspan> = ' + group.d + "</text>");
      parts.push('<text class="psub" x="' + (W - R) + '" y="16" text-anchor="end">best ' +
                 C.num(best.gamma_rho, 3) + " at " + C.escapeHtml(label(best)) + " · " + rows.length +
                 (rows.length === 1 ? " set" : " sets") + "</text>");
      panels.push({ d: group.d, pts: rows });
      return '<svg class="panel-svg" data-panel="' + (panels.length - 1) + '" viewBox="0 0 ' + W + " " + H +
        '" role="img" aria-label="gamma_rho against n at distance ' + group.d + ": " + rows.length +
        " parameter sets, best " + C.num(best.gamma_rho, 3) + " at " + label(best) + '">' + parts.join("") + "</svg>";
    }).join("");

    return '<figure class="plot">' +
      '<div class="plot-tip" id="plot-tip" role="status"></div>' +
      '<div class="panels">' + html + "</div>" +
      "<figcaption>Inputs " + C.tex("n") + " on a log scale against " + C.tex(C.TEX.gr) +
      ", on axes shared by all panels. " +
      '<span class="key"><span class="key-dot"></span><span>parameter set</span></span>' +
      '<span class="key"><span class="stair-key"></span><span>lowest ' + C.tex(C.TEX.gr) + " up to this " + C.tex("n") + '</span></span>' +
      '<span class="key"><span class="unity-key"></span><span>' + C.tex(C.TEX.gr + "=1") + '</span></span>' +
      "<br>Hover over a point for details, or click it to open." +
      (skipped ? " " + skipped + " parameter set" + (skipped === 1 ? " is" : "s are") +
                 " left out because their gates have no " + C.tex(C.TEX.vex) + "." : "") +
      "</figcaption></figure>";
  }

  /* ------------------------------------------------------- plot hover layer */
  /* One tooltip for the figure, following the nearest point (within 16 px) of
   * whichever panel the pointer is over -- a hit area far bigger than a mark. */
  function wirePlot(figure) {
    var tip = figure.querySelector(".plot-tip");
    var hot = null;
    function clear() {
      if (hot) { hot.classList.remove("hot"); hot = null; }
      tip.classList.remove("on");
    }
    figure.querySelectorAll("svg.panel-svg").forEach(function (svg) {
      var panel = panels[Number(svg.getAttribute("data-panel"))];
      var circles = svg.querySelectorAll("circle.pt");
      function nearest(event) {
        var box = svg.getBoundingClientRect(), sx = W / box.width, sy = H / box.height;
        var x = (event.clientX - box.left) * sx, y = (event.clientY - box.top) * sy;
        var best = null, bestD = Infinity;
        panel.pts.forEach(function (p, i) {
          var dd = (p._x - x) * (p._x - x) + (p._y - y) * (p._y - y);
          if (dd < bestD) { bestD = dd; best = i; }
        });
        return Math.sqrt(bestD) / sx <= 16 ? best : null;
      }
      svg.addEventListener("mousemove", function (event) {
        var i = nearest(event);
        if (i === null) { clear(); svg.style.cursor = ""; return; }
        var p = panel.pts[i], c = circles[i];
        if (hot !== c) { if (hot) hot.classList.remove("hot"); hot = c; c.classList.add("hot"); }
        var box = svg.getBoundingClientRect(), fig = figure.getBoundingClientRect();
        tip.style.left = (box.left - fig.left + p._x * box.width / W) + "px";
        tip.style.top = (box.top - fig.top + p._y * box.height / H) + "px";
        tip.innerHTML = "<b>" + C.paramsTex(p.n, p.k, p.d) + "</b>" +
          '<div class="row"><span>' + C.tex(C.TEX.gr) + "</span><span>" + C.num(p.gamma_rho, 4) + "</span></div>" +
          '<div class="row"><span>' + C.tex(C.TEX.vex) + "</span><span>" + p.v_ex_best + "</span></div>" +
          '<div class="row"><span>gates</span><span>' + p.count + "</span></div>" +
          (p._front ? '<div class="hint">on the frontier</div>' : "");
        tip.classList.add("on");
        svg.style.cursor = "pointer";
      });
      svg.addEventListener("mouseleave", clear);
      svg.addEventListener("click", function (event) {
        var i = nearest(event);
        if (i !== null) global.location.href = href(panel.pts[i]);
      });
    });
  }

  /* ------------------------------------------------------------------ mount */

  function mount(index) {
    var p = index.parameters || [];
    var slots = {
      "headline-stats": headline(p),
      "record-cards": recordCards(p),
      "frontier-plot": plot(p)
    };
    Object.keys(slots).forEach(function (id) {
      var node = document.getElementById(id);
      if (node) node.innerHTML = slots[id];
    });
    var figure = document.querySelector("#frontier-plot figure.plot");
    if (figure) wirePlot(figure);
  }

  global.Highlights = { mount: mount };
}(window));
