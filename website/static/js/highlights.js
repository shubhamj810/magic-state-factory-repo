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

  function label(row) {
    return "[[" + row.n + ", " + row.k + ", " + row.d + "]]";
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
      return '<a class="record d' + group.d + '" href="' + href(best) + '">' +
        '<span class="d">d = ' + group.d + "</span>" +
        '<span class="g">&gamma;<sub>&rho;</sub> ' + C.num(best.gamma_rho, 4) + "</span>" +
        '<span class="p">' + C.escapeHtml(label(best)) + "</span>" +
        '<span class="meta">V<sub>ex</sub> ' + best.v_ex_best +
        " &middot; " + usable.length + " of " + group.rows.length + " comparable" +
        (widest ? " &middot; best V<sub>ex</sub> " + widest.v_ex_best : "") +
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
        (row ? '<a class="l" href="' + href(row) + '">' +
               C.escapeHtml(label(row)) + "</a>" : "") +
        (note ? '<span class="n">' + note + "</span>" : "") +
        "</div>";
    }
    return cell("least &gamma;<sub>&rho;</sub>", C.num(best.gamma_rho, 4), best,
                "log(n/V<sub>ex</sub>)/log(d) &mdash; V<sub>ex</sub> = " + best.v_ex_best) +
           cell("most magic states", "V<sub>ex</sub> = " + widest.v_ex_best, widest,
                "extractable T states from one circuit") +
           cell("greatest distance", "d = " + deepest.d, deepest,
                "least weight of an undetectable fault");
  }

  /* ------------------------------------------------------------- the plot */

  /* gamma against n, log-x, one mark per parameter set, coloured by d, with the
   * running best-gamma staircase drawn over it.  Inline SVG: no dependency, no
   * network, and it renders from a file:// copy as readily as from a server. */
  function plot(parameters) {
    var skipped = parameters.length;
    var pts = parameters.filter(function (r) {
      return r.comparable && r.gamma_rho !== null && r.gamma_rho !== undefined &&
             !Number.isNaN(r.gamma_rho) && r.n > 0;
    });
    skipped -= pts.length;
    if (pts.length < 2) return "";

    var W = 760, H = 320, L = 52, R = 14, T = 16, B = 40;
    var iw = W - L - R, ih = H - T - B;

    var xs = pts.map(function (p) { return Math.log10(p.n); });
    var ys = pts.map(function (p) { return p.gamma_rho; });
    var x0 = Math.min.apply(null, xs), x1 = Math.max.apply(null, xs);
    var y0 = Math.min.apply(null, ys), y1 = Math.max.apply(null, ys);
    /* pad so marks are not clipped by the axes */
    var padY = (y1 - y0) * 0.06 || 0.1;
    y0 -= padY; y1 += padY;

    function X(n) { return L + (Math.log10(n) - x0) / ((x1 - x0) || 1) * iw; }
    function Y(g) { return T + ih - (g - y0) / ((y1 - y0) || 1) * ih; }

    var parts = [];

    /* gamma = 1 is the line the whole subject is trying to cross; draw it if
     * it is in range, so its absence is as visible as its presence. */
    var unity = "";
    if (y0 <= 1 && 1 <= y1) {
      unity = '<line class="unity" x1="' + L + '" y1="' + Y(1).toFixed(1) +
              '" x2="' + (W - R) + '" y2="' + Y(1).toFixed(1) + '"/>' +
              '<text class="unity-t" x="' + (L + 6) + '" y="' + (Y(1) - 6).toFixed(1) +
              '">&gamma;<tspan baseline-shift="sub">&rho;</tspan> = 1</text>';
    }

    /* y gridlines at sensible gamma values */
    var gridStep = (y1 - y0) > 1.5 ? 0.5 : (y1 - y0) > 0.6 ? 0.25 : 0.1;
    var gy = Math.ceil(y0 / gridStep) * gridStep;
    for (; gy <= y1; gy += gridStep) {
      parts.push('<line class="grid" x1="' + L + '" y1="' + Y(gy).toFixed(1) +
                 '" x2="' + (W - R) + '" y2="' + Y(gy).toFixed(1) + '"/>');
      parts.push('<text class="ax" x="' + (L - 8) + '" y="' + (Y(gy) + 3.5).toFixed(1) +
                 '" text-anchor="end">' + gy.toFixed(2) + "</text>");
    }

    /* x ticks at decades and half-decades present in the data */
    [10, 20, 50, 100, 200, 500, 1000, 2000].forEach(function (n) {
      if (Math.log10(n) < x0 - 0.02 || Math.log10(n) > x1 + 0.02) return;
      parts.push('<line class="grid" x1="' + X(n).toFixed(1) + '" y1="' + T +
                 '" x2="' + X(n).toFixed(1) + '" y2="' + (T + ih) + '"/>');
      parts.push('<text class="ax" x="' + X(n).toFixed(1) + '" y="' + (T + ih + 16) +
                 '" text-anchor="middle">' + n + "</text>");
    });

    /* the best-gamma staircase: sweep n upward, drop whenever a better gamma
     * appears.  This is the catalogue's actual frontier. */
    var sorted = pts.slice().sort(function (a, b) { return a.n - b.n; });
    var run = Infinity, stair = [];
    sorted.forEach(function (p) {
      if (p.gamma_rho < run) { run = p.gamma_rho; stair.push(p); }
    });
    if (stair.length > 1) {
      var path = "";
      stair.forEach(function (p, i) {
        var x = X(p.n).toFixed(1), y = Y(p.gamma_rho).toFixed(1);
        path += i === 0 ? "M" + x + "," + y
                        : "H" + x + "V" + y;   /* step down, not a diagonal */
      });
      path += "H" + (W - R);
      parts.push('<path class="stair" d="' + path + '"/>');
    }

    /* the marks, drawn after the grid so they sit on top */
    pts.forEach(function (p, i) {
      p._x = X(p.n); p._y = Y(p.gamma_rho);
      parts.push('<circle class="pt d' + p.d + '" data-i="' + i + '" cx="' + p._x.toFixed(1) +
                 '" cy="' + p._y.toFixed(1) + '" r="4"/>');
    });

    /* the frontier points again, larger, so the staircase corners read */
    stair.forEach(function (p) {
      p._corner = true;
      parts.push('<circle class="corner" cx="' + X(p.n).toFixed(1) +
                 '" cy="' + Y(p.gamma_rho).toFixed(1) + '" r="5.5"/>');
    });

    var swatches = byDistance(pts).map(function (g) {
      return '<span class="key"><span class="dot d' + g.d + '"></span>d = ' + g.d + "</span>";
    }).join("");

    lastPoints = pts;
    return '<figure class="plot">' +
      '<div class="plot-tip" id="plot-tip" role="status"></div>' +
      '<svg viewBox="0 0 ' + W + " " + H + '" role="img" ' +
      'aria-label="Yield exponent gamma against circuit length n, one mark per parameter set.">' +
      parts.join("") + unity +
      '<text class="ax-t" x="' + (L + iw / 2) + '" y="' + (H - 6) +
      '" text-anchor="middle">n &mdash; rotations consumed (log scale)</text>' +
      '<text class="ax-t" transform="translate(14,' + (T + ih / 2) +
      ') rotate(-90)" text-anchor="middle">&gamma;<tspan baseline-shift="sub">&rho;</tspan></text>' +
      "</svg>" +
      '<figcaption class="small muted">' + swatches +
      '<span class="key"><span class="stair-key"></span><span>best &gamma;<sub>&rho;</sub> so far</span></span>' +
      "<br>Hover a point for its parameters, click to open it. The staircase is the catalogue&rsquo;s " +
      "&gamma;<sub>&rho;</sub> frontier: it can only fall, and each corner is a circuit no " +
      "shorter circuit beats." +
      (skipped ? " " + skipped + " parameter set" + (skipped === 1 ? " is" : "s are") +
                 " not plotted: their gates have overlapping monomials, so no " +
                 "extractable T count exists and no rate claim can be made from them."
               : "") +
      "</figcaption></figure>";
  }

  /* ------------------------------------------------------- plot hover layer */
  var lastPoints = [];

  /* One tooltip, following the nearest point within 18 px -- a hit area much
   * bigger than the 4 px mark, so the plot is usable with a trackpad. */
  function wirePlot(figure) {
    var svg = figure.querySelector("svg"), tip = figure.querySelector(".plot-tip");
    if (!svg || !tip) return;
    var circles = svg.querySelectorAll("circle.pt"), hot = null;
    function nearest(event) {
      var box = svg.getBoundingClientRect(), vb = svg.viewBox.baseVal;
      var sx = vb.width / box.width, sy = vb.height / box.height;
      var x = (event.clientX - box.left) * sx, y = (event.clientY - box.top) * sy;
      var best = null, bestD = Infinity;
      lastPoints.forEach(function (p, i) {
        var dx = p._x - x, dy = p._y - y, dd = dx * dx + dy * dy;
        if (dd < bestD) { bestD = dd; best = i; }
      });
      return Math.sqrt(bestD) / sx <= 18 ? best : null;
    }
    function show(i) {
      if (hot !== null && circles[hot]) { circles[hot].classList.remove("hot"); circles[hot].setAttribute("r", "4"); }
      hot = i;
      if (i === null) { tip.classList.remove("on"); svg.style.cursor = ""; return; }
      var p = lastPoints[i], c = circles[i];
      c.classList.add("hot"); c.setAttribute("r", "6.5");
      var box = svg.getBoundingClientRect(), fig = figure.getBoundingClientRect(), vb = svg.viewBox.baseVal;
      tip.style.left = (box.left - fig.left + p._x * box.width / vb.width) + "px";
      tip.style.top = (box.top - fig.top + p._y * box.height / vb.height) + "px";
      tip.innerHTML = "<b>" + C.escapeHtml(label(p)) + "</b>" +
        '<div class="row"><span>&gamma;<sub>&rho;</sub></span><span>' + C.num(p.gamma_rho, 4) + "</span></div>" +
        '<div class="row"><span>V<sub>ex</sub></span><span>' + p.v_ex_best + "</span></div>" +
        '<div class="row"><span>gates</span><span>' + p.count + "</span></div>" +
        (p._corner ? '<div class="hint">on the frontier</div>' : "") +
        '<div class="hint">click to open</div>';
      tip.classList.add("on");
      svg.style.cursor = "pointer";
    }
    svg.addEventListener("mousemove", function (event) { show(nearest(event)); });
    svg.addEventListener("mouseleave", function () { show(null); });
    svg.addEventListener("click", function (event) {
      var i = nearest(event);
      if (i !== null) global.location.href = href(lastPoints[i]);
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
