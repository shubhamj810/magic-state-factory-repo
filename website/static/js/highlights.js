/* Landmarks for the landing page: the gamma_rho frontier, per-distance record
 * holders, and a gamma-against-n plot.
 *
 * Everything here is computed in the browser from `data/index.json` -- the same
 * file the tables read.  Nothing is precomputed into the index and nothing is
 * hand-maintained, so a landmark cannot drift out of step with the catalogue it
 * describes: reseed the data, rebuild the index, and these move with it.
 *
 * A switch picks the ranking, and the distinction is the whole reason this
 * file is careful.  gamma = log(n/k)/log(d) counts output WIRES, so it is not
 * comparable between gates: a CCZ occupies three wires and is worth two T
 * states, which flatters it by half again.  Ranked on gamma over every gate the
 * apparent champion is a CCZ web at 0.80 -- a number that must never be quoted
 * as a record.  So the two rankings are:
 *
 *   gamma     (default)  only parameter sets holding a pure T^k gate, where k
 *                        wires are k T states and gamma is unambiguous;
 *   gamma_rho            log(n/V_ex)/log(d) over every gate, excluding those
 *                        whose monomials OVERLAP (they have no V_ex).
 *
 * Whatever is excluded, the plot says how many and why.  LOWER IS BETTER.
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

  /* Landmarks are claims, so they use the distance a source certified where
   * there is one (see claims() below); links still go to the catalogue's row,
   * which is keyed on the distance re-verified here. */
  function href(row) {
    return C.paramsHref(row.n, row.k, row.d_verified || row.d);
  }

  /* The two rankings the landing page offers.  Each fills the same fields the
   * code below reads -- `gamma_rho` (the value ranked), `v_ex_best` (the count
   * beside it) and `comparable` -- so only the wording depends on the choice.
   *   gamma : log(n/k)/log d, among parameter sets holding a pure T^k gate,
   *           where it is unambiguous and equals gamma_rho;
   *   rho   : log(n/V_ex)/log d, across every gate with a defined V_ex. */
  var METRICS = {
    gamma: { sym: "\\gamma", count: "k", countText: "outputs" },
    rho: { sym: "\\gamma_\\rho", count: "V_{\\mathrm{ex}}", countText: "T states per run" }
  };
  var M = METRICS.gamma;

  function claims(parameters, metric) {
    return parameters.map(function (p) {
      var value = metric === "gamma" ? (p.has_pure ? p.gamma_claim : null) : p.gamma_rho_claim;
      return Object.assign({}, p, {
        d_verified: p.d, d: p.d_claim, gamma_rho: value, comparable: value !== null && value !== undefined,
        v_ex_best: metric === "gamma" ? p.k : p.v_ex_best,
        certified: p.d_claim_certified, lower_bound: p.d_claim_certified && p.d_claim_exact === false
      });
    });
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
  function recordCards(parameters, factories) {
    return byDistance(parameters).map(function (group) {
      var usable = group.rows.filter(function (r) { return r.comparable; });
      var best = bestBy(usable, "gamma_rho");
      if (!best) return "";
      /* the factory in that parameter set that holds the record */
      var holder = factories.filter(function (f) {
        return f.n === best.n && f.k === best.k && f.d === best.d_verified &&
               (M === METRICS.gamma ? f.pure_t && Math.abs(f.gamma_claim - best.gamma_rho) < 1e-12
                                    : f.gamma_rho_claim !== null && Math.abs(f.gamma_rho_claim - best.gamma_rho) < 1e-12);
      })[0];
      var link = holder ? C.factoryHref(holder.id) : href(best);
      return '<tr class="clickable" data-href="' + link + '">' +
        '<td><a href="' + link + '">' + C.paramsTex(best.n, best.k, best.d) + "</a></td>" +
        '<td class="num">' + C.num(best.gamma_rho, 4) + "</td>" + countCell(best) + "</tr>";
    }).join("");
  }

  /* k is already in the parameters; V_ex is not, so only the gamma_rho view
   * gives it a column. */
  function countCell(row) {
    return M === METRICS.gamma ? "" : '<td class="num">' + row.v_ex_best + "</td>";
  }

  function tableHead() {
    return '<tr><th scope="col">parameters</th><th class="num" scope="col">' + C.tex(M.sym) + "</th>" +
      (M === METRICS.gamma ? "" : '<th class="num" scope="col">' + C.tex(M.count) + "</th>") + "</tr>";
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
    return cell("lowest " + C.tex(M.sym), C.tex(M.sym + "=" + C.num(best.gamma_rho, 4)), best,
                M === METRICS.gamma ? "" : C.tex(M.count + "=" + best.v_ex_best) + " " + M.countText) +
           cell("most " + M.countText, C.tex(M.count + "=" + widest.v_ex_best), widest, "") +
           cell("highest distance", C.tex("d" + (deepest.lower_bound ? "\\ge " : "=") + deepest.d), deepest, "");
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
      panels.push({ d: group.d, pts: rows, stair: stair });
      return '<svg class="panel-svg" data-panel="' + (panels.length - 1) + '" viewBox="0 0 ' + W + " " + H +
        '" role="img" aria-label="' + (M === METRICS.gamma ? "gamma" : "gamma_rho") + ' against n at distance ' + group.d + ": " + rows.length +
        " parameter sets, best " + C.num(best.gamma_rho, 3) + " at " + label(best) + '">' + parts.join("") + "</svg>";
    }).join("");

    var tableRows = panels.map(function (panel) {
      return panel.stair.map(function (p) {
        return '<tr class="clickable" data-href="' + href(p) + '"><td><a href="' + href(p) + '">' +
          C.paramsTex(p.n, p.k, p.d) + "</a></td>" +
          '<td class="num">' + C.num(p.gamma_rho, 4) + "</td>" + countCell(p) + "</tr>";
      }).join("");
    }).join("");
    return '<figure class="plot">' +
      '<div class="plot-bar">' +
        '<div class="seg" role="group" aria-label="view"><button type="button" id="plot-view-plot" aria-pressed="true">Plot</button>' +
        '<button type="button" id="plot-view-table" aria-pressed="false">Table</button></div>' +
        '<span class="spacer"></span>' +
        '<button type="button" class="btn" id="plot-svg">SVG</button>' +
        '<button type="button" class="btn" id="plot-png">PNG</button></div>' +
      '<div class="plot-tip" id="plot-tip" role="status"></div>' +
      '<div class="panels">' + html + "</div>" +
      '<div class="table-wrap plot-table" hidden><table><caption class="sr-only">The frontier points, by distance: ' +
        "each lowers the best " + (M === METRICS.gamma ? "gamma" : "gamma_rho") + " at its distance.</caption><thead>" + tableHead() +
        "</thead><tbody>" + tableRows + "</tbody></table></div>" +
      "<figcaption>Inputs " + C.tex("n") + " on a log scale against " + C.tex(M.sym) +
      ", on axes shared by all panels. " +
      '<span class="key"><span class="key-dot"></span><span>parameter set</span></span>' +
      '<span class="key"><span class="stair-key"></span><span>lowest ' + C.tex(M.sym) + " up to this " + C.tex("n") + '</span></span>' +
      '<span class="key"><span class="unity-key"></span><span>' + C.tex(M.sym + "=1") + '</span></span>' +
      "<br>Hover over a point for details, or click it to open." +
      (skipped ? " " + skipped + " parameter set" + (skipped === 1 ? " is" : "s are") + " left out because " +
                 (M === METRICS.gamma ? "they hold no pure " + C.tex("T^{\\otimes k}") + " gate."
                                      : "their gates have no " + C.tex(C.TEX.vex) + ".") : "") +
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
          '<div class="row"><span>' + C.tex(M.sym) + "</span><span>" + C.num(p.gamma_rho, 4) + "</span></div>" +
          '<div class="row"><span>' + C.tex(M.count) + "</span><span>" + p.v_ex_best + "</span></div>" +
          '<div class="row"><span>gates</span><span>' + p.count + "</span></div>" +
          (p._front ? '<div class="hint">on the frontier</div>' : "") +
          (p.certified ? '<div class="hint">distance certified by its source</div>' : "");
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

  /* ---------------------------------------------------------- export */
  /* One standalone SVG of every panel: styles inlined, so it looks the same
   * outside the site, laid out three panels to a row. */
  var STYLE_PROPS = ["fill", "stroke", "stroke-width", "stroke-dasharray", "opacity",
                     "font-family", "font-size", "font-weight", "font-style", "text-anchor"];

  function composedSvg(figure) {
    var svgs = Array.prototype.slice.call(figure.querySelectorAll("svg.panel-svg"));
    var per = Math.min(3, svgs.length), rows = Math.ceil(svgs.length / per), foot = 26;
    var bg = getComputedStyle(document.body).backgroundColor;
    var ink = getComputedStyle(document.body).color;
    var out = '<svg xmlns="http://www.w3.org/2000/svg" width="' + per * W + '" height="' + (rows * H + foot) +
      '" viewBox="0 0 ' + per * W + " " + (rows * H + foot) + '"><rect width="100%" height="100%" fill="' + bg + '"/>';
    svgs.forEach(function (svg, i) {
      var clone = svg.cloneNode(true), src = svg.querySelectorAll("*"), dst = clone.querySelectorAll("*");
      for (var e = 0; e < src.length; e++) {
        var cs = getComputedStyle(src[e]);
        dst[e].setAttribute("style", STYLE_PROPS.map(function (prop) {
          return prop + ":" + cs.getPropertyValue(prop);
        }).join(";"));
        dst[e].removeAttribute("class");
      }
      out += '<g transform="translate(' + (i % per) * W + "," + Math.floor(i / per) * H + ')">' + clone.innerHTML + "</g>";
    });
    out += '<text x="8" y="' + (rows * H + 17) + '" style="font:11px sans-serif;fill:' + ink + '">' +
      (M === METRICS.gamma ? "gamma (pure T^k)" : "gamma_rho") + " frontier by distance. Magic State Factory Catalog, " + new Date().toISOString().slice(0, 10) + "</text></svg>";
    return out;
  }

  function wireTools(figure) {
    var panelsNode = figure.querySelector(".panels"), tableNode = figure.querySelector(".plot-table");
    [["plot-view-plot", false], ["plot-view-table", true]].forEach(function (pair) {
      document.getElementById(pair[0]).addEventListener("click", function () {
        panelsNode.hidden = pair[1];
        tableNode.hidden = !pair[1];
        /* set display too: the panel grid's own display would otherwise
         * override [hidden] wherever the stylesheet lacks the rule for it */
        panelsNode.style.display = pair[1] ? "none" : "";
        tableNode.style.display = pair[1] ? "" : "none";
        document.getElementById("plot-view-plot").setAttribute("aria-pressed", String(!pair[1]));
        document.getElementById("plot-view-table").setAttribute("aria-pressed", String(pair[1]));
      });
    });
    C.clickableRows(tableNode.querySelector("tbody"));
    document.getElementById("plot-svg").addEventListener("click", function () {
      C.download("gamma-rho-frontier.svg", composedSvg(figure), "image/svg+xml");
    });
    document.getElementById("plot-png").addEventListener("click", function () {
      var svg = composedSvg(figure), img = new Image();
      img.onload = function () {
        var canvas = document.createElement("canvas");
        canvas.width = img.width * 2;
        canvas.height = img.height * 2;
        var ctx = canvas.getContext("2d");
        ctx.scale(2, 2);
        ctx.drawImage(img, 0, 0);
        canvas.toBlob(function (blob) {
          var url = URL.createObjectURL(blob), a = document.createElement("a");
          a.href = url;
          a.download = "gamma-rho-frontier.png";
          document.body.appendChild(a);
          a.click();
          setTimeout(function () { URL.revokeObjectURL(url); a.remove(); }, 0);
        });
      };
      img.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
    });
  }

  /* ------------------------------------------------------------------ mount */

  function draw(index, metric) {
    M = METRICS[metric];
    var p = claims(index.parameters || [], metric);
    var node = document.getElementById("headline-stats");
    if (node) node.innerHTML = headline(p);
    var records = document.querySelector("#record-cards tbody");
    if (records) records.innerHTML = recordCards(p, index.factories || []);
    var recordsHead = document.querySelector("#record-cards thead");
    if (recordsHead) recordsHead.innerHTML = tableHead();
    var intro = document.getElementById("best-intro");
    if (intro) {
      intro.innerHTML = metric === "gamma"
        ? "Lowest " + C.tex("\\gamma=\\log(n/k)/\\log d") + " among pure " + C.tex("T^{\\otimes k}") + " factories. " + '<a href="about.html#numbers">What this measures</a>'
        : "Lowest " + C.tex("\\gamma_\\rho=\\log(n/V_{\\mathrm{ex}})/\\log d") + " across every gate, " +
          "counting the T states a run yields. " + '<a href="about.html#numbers">What this measures</a>';
    }
    var plotNode = document.getElementById("frontier-plot");
    if (plotNode) plotNode.innerHTML = plot(p);
    var frontierSym = document.getElementById("frontier-sym");
    if (frontierSym) frontierSym.innerHTML = C.tex(M.sym);
    var figure = document.querySelector("#frontier-plot figure.plot");
    if (figure) { wirePlot(figure); wireTools(figure); C.renderTex(figure); }
  }

  function mount(index) {
    var records = document.querySelector("#record-cards tbody");
    if (records) C.clickableRows(records);
    var current = "gamma";
    draw(index, current);
    document.querySelectorAll("#metric-switch button[data-metric]").forEach(function (b) {
      b.addEventListener("click", function () {
        current = b.getAttribute("data-metric");
        document.querySelectorAll("#metric-switch button").forEach(function (x) {
          x.setAttribute("aria-pressed", String(x === b));
        });
        draw(index, current);
      });
    });
  }

  global.Highlights = { mount: mount };
}(window));
