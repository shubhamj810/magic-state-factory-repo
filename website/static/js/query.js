/* The search engine behind search.html: pure functions over data/index.json.
 *
 *   prepare(index)          annotate each factory once: sort order, the set of
 *                           its gate's monomials, a lowercase haystack
 *   parse(text)             "CCZ012 k=2 t<=4" -> a list of row predicates
 *   filter(rows, state)     apply the free text AND every filter control
 *   readState / writeState  the filter state <-> the URL query string
 *
 * A gate is stored as "+"-separated monomials over the output wires: "0+1+01"
 * is T0·T1·CS01.  Indices are concatenated digits when k <= 10 and
 * comma-separated when k > 10, so "10" is T10 at k = 12 and CS on wires 1, 0
 * at k = 4.  Monomials are compared as sorted index lists, never as strings.
 */
(function (global) {
  "use strict";

  var ARITY = { t: 1, cs: 2, ccz: 3 };

  function monomialKeys(gate, k) {
    var keys = new Set();
    if (!gate) return keys;
    gate.split("+").forEach(function (token) {
      var wires = token.indexOf(",") >= 0 ? token.split(",")
                : (k > 10 ? [token] : token.split(""));
      keys.add(wires.map(Number).sort(function (a, b) { return a - b; }).join(","));
    });
    return keys;
  }

  function prepare(index) {
    var refs = index.references || {};
    index.factories.forEach(function (f) {
      f.order = f.n * 10000 + f.k * 10 + f.d;
      f._mono = monomialKeys(f.gate, f.k);
      f.cite_text = f.citations.map(function (c) { return refs[c] ? refs[c].short : c; }).join("; ");
      f._text = [f.id, f.gate_human, f.regimes.join(" "), f.discovery || "", f.cite_text,
                 f.citations.join(" ")].join(" ").toLowerCase();
    });
    return index;
  }

  /* --------------------------------------------------------- the free text */
  var FIELD = {           /* query word -> index field; n and N are DIFFERENT */
    n: "n", k: "k", d: "d", N: "N", r: "r",
    t: "t_count", T: "t_count", deg: "poly_degree",
    g: "gamma_rho", gamma: "gamma"
  };
  var COMPARE = /^(n|k|d|N|r|t|T|deg|g|gamma)\s*(>=|<=|=|==|>|<)\s*(\d+(?:\.\d+)?)$/;
  var TERM = /^(t|cs|ccz)(\d+(?:,\d+)*)$/i;
  var PARAMS = /\[\[\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\]\]/g;

  function comparator(op, value) {
    return function (v) {
      if (v === null || v === undefined) return false;
      return op === "=" || op === "==" ? v === value : op === ">" ? v > value :
             op === "<" ? v < value : op === ">=" ? v >= value : v <= value;
    };
  }

  /* Returns { tests: [row -> bool], notes: [string] }.  A note explains a word
   * that was read in a way the user might not expect, or not at all. */
  function parse(text) {
    var tests = [], notes = [];
    text = (text || "").replace(PARAMS, function (_, n, k, d) {
      return " n=" + n + " k=" + k + " d=" + d + " ";
    }).replace(/\s*(>=|<=|==|=|>|<)\s*/g, "$1");

    text.split(/\s+/).filter(Boolean).forEach(function (word) {
      var m = COMPARE.exec(word);
      if (m) {
        var field = FIELD[m[1]], test = comparator(m[2], Number(m[3]));
        tests.push(function (row) { return test(row[field]); });
        return;
      }
      var lower = word.toLowerCase();
      if (ARITY[lower]) {
        var key = lower + "_terms";
        tests.push(function (row) { return row[key] > 0; });
        return;
      }
      if (lower === "pure") { tests.push(function (row) { return row.pure_t; }); return; }
      if (lower === "exact") { tests.push(function (row) { return row.d_is_exact; }); return; }
      m = TERM.exec(word);
      if (m) {
        var arity = ARITY[m[1].toLowerCase()];
        var digits = m[2];
        var wires = digits.indexOf(",") >= 0 ? digits.split(",")
                  : (arity === 1 ? [digits] : digits.split(""));
        if (wires.length === arity) {
          var want = wires.map(Number).sort(function (a, b) { return a - b; }).join(",");
          tests.push(function (row) { return row._mono.has(want); });
          return;
        }
        notes.push("“" + word + "” is not a " + m[1].toUpperCase() + " term on " + arity +
                   (arity === 1 ? " wire" : " wires") + "; matched as text");
      }
      tests.push(function (row) { return row._text.indexOf(lower) >= 0; });
    });
    return { tests: tests, notes: notes };
  }

  /* ----------------------------------------------------- the filter state */
  /* Every control, its URL key, and how to read it.  Defaults are omitted from
   * the URL, so a bare search.html is the whole catalogue. */
  var KEYS = {
    q: "text", nmin: "int", nmax: "int", kmin: "int", kmax: "int",
    d: "list", exact: "bool", has: "list", pure: "bool",
    tmax: "int", known: "bool", grmax: "float",
    disc: "text", regime: "text", cite: "text",
    sort: "text", dir: "int", page: "int", size: "int"
  };

  function readState(search) {
    var url = new URLSearchParams(search), state = {};
    Object.keys(KEYS).forEach(function (key) {
      var raw = url.get(key);
      if (raw === null || raw === "") return;
      var type = KEYS[key];
      if (type === "int") { var i = parseInt(raw, 10); if (!Number.isNaN(i)) state[key] = i; }
      else if (type === "float") { var f = parseFloat(raw); if (!Number.isNaN(f)) state[key] = f; }
      else if (type === "bool") state[key] = raw === "1" || raw === "true";
      else if (type === "list") state[key] = raw.split(",").filter(Boolean);
      else state[key] = raw;
    });
    return state;
  }

  function writeState(state) {
    var url = new URLSearchParams();
    Object.keys(KEYS).forEach(function (key) {
      var v = state[key];
      if (v === undefined || v === null || v === "" || v === false) return;
      if (Array.isArray(v)) { if (v.length) url.set(key, v.join(",")); return; }
      url.set(key, v === true ? "1" : String(v));
    });
    var text = url.toString();
    return text ? "?" + text : "";
  }

  function filter(rows, state) {
    var parsed = parse(state.q);
    var tests = parsed.tests.slice();
    function add(t) { tests.push(t); }
    if (state.nmin !== undefined) add(function (r) { return r.n >= state.nmin; });
    if (state.nmax !== undefined) add(function (r) { return r.n <= state.nmax; });
    if (state.kmin !== undefined) add(function (r) { return r.k >= state.kmin; });
    if (state.kmax !== undefined) add(function (r) { return r.k <= state.kmax; });
    if (state.d && state.d.length) {
      var ds = state.d.map(Number);
      add(function (r) { return ds.indexOf(r.d) >= 0; });
    }
    if (state.exact) add(function (r) { return r.d_is_exact; });
    (state.has || []).forEach(function (kind) {
      if (ARITY[kind]) add(function (r) { return r[kind + "_terms"] > 0; });
    });
    if (state.pure) add(function (r) { return r.pure_t; });
    if (state.tmax !== undefined) add(function (r) { return r.t_count !== null && r.t_count <= state.tmax; });
    if (state.known) add(function (r) { return r.t_count !== null; });
    if (state.grmax !== undefined) add(function (r) { return r.gamma_rho !== null && r.gamma_rho <= state.grmax; });
    if (state.disc) add(function (r) { return r.discovery === state.disc; });
    if (state.regime) add(function (r) { return r.regimes.indexOf(state.regime) >= 0; });
    if (state.cite) add(function (r) { return r.citations.indexOf(state.cite) >= 0; });
    return {
      rows: rows.filter(function (r) {
        for (var i = 0; i < tests.length; i++) if (!tests[i](r)) return false;
        return true;
      }),
      notes: parsed.notes
    };
  }

  global.Query = {
    monomialKeys: monomialKeys,
    prepare: prepare,
    parse: parse,
    filter: filter,
    readState: readState,
    writeState: writeState
  };
}(window));
