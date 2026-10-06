/* Is a target gate reachable from this factory's gate by CNOT + S on the
 * outputs -- and if so, which circuit does it?
 *
 * A level-3 diagonal gate is a phase f : F_2^k -> Z_8 (in units of pi/4):
 * T on a contributes x_a, CS on {a,b} 2 x_a x_b, CCZ on {a,b,c} 4 x_a x_b x_c.
 * A CNOT circuit U with U|x> = |Mx> conjugates D_f to D_{f o M^-1}, and the
 * diagonal Cliffords (S, Z, CZ) are exactly the phases 2*linear + 4*quadratic.
 * So the target g is reachable iff  g = f o A + (Clifford phase)  for some
 * A in GL(k,2), which is the catalogue's own deduplication relation.
 *
 * DECIDING it is a port of master_catalog/glcanon.py: the third finite
 * difference tau of f is a symmetric trilinear form, invariant mod Clifford
 * and covariant under A; label every nonzero u by (rank tau(u,.,.),
 * tau(u,u,u), tau(u,u,.) != 0), compare the label multisets, then search for
 * basis images with matching labels and matching tau on basis triples.  The
 * search has a work budget: running out is reported as "undecided", never as
 * an answer.
 *
 * CONSTRUCTING it is new here: from the witness A we build
 *   1. the CNOT circuit for M = A^-1 by Gaussian elimination, and
 *   2. the Clifford correction c = g - f o A, decomposed by a Moebius
 *      transform over Z_4 into S / Z / S-dagger on single outputs and CZ on
 *      pairs (anything of higher degree would mean "not Clifford"),
 * and then CHECK both by brute force on all 2^k basis states: the CNOT circuit
 * is simulated on every basis vector, and the phase of
 * (corrections) o (CNOT circuit) o D_f o (CNOT circuit)^dagger is compared with
 * the target's phase, exactly, mod 8, up to one global phase.
 */
(function (global) {
  "use strict";

  var LABEL_K_CAP = 16;
  var WORK_BUDGET = 20000000;
  var NAMES = { 1: "T", 2: "CS", 3: "CCZ" };

  function popcount(x) {
    x = x - ((x >>> 1) & 0x55555555);
    x = (x & 0x33333333) + ((x >>> 2) & 0x33333333);
    return (((x + (x >>> 4)) & 0x0F0F0F0F) * 0x01010101) >>> 24;
  }
  function parity(x) { return popcount(x) & 1; }
  function bits(mask) {
    var out = [];
    for (var i = 0; mask; i++, mask >>>= 1) if (mask & 1) out.push(i);
    return out;
  }

  /* ------------------------------------------------------------- parsing */
  /* "T0·T1·CS01", "T0 T1 CS01", "0+1+01", "CCZ10,11,12" -> [[0],[1],[0,1]].
   * Repeated terms cancel in pairs: T.T = S, CS.CS = CZ and CCZ.CCZ = 1 are
   * all Clifford, and everything here is modulo Clifford. */
  function parseGate(text, k) {
    var tokens = String(text || "").trim().split(/[\s·.*+]+/).filter(Boolean);
    if (!tokens.length) throw new Error("type a gate, e.g. T0·CS01");
    var seen = {};
    tokens.forEach(function (tok) {
      if (/^(I|id|1)$/i.test(tok)) return;
      var m = /^(CCZ|CS|T)?(\d+(?:,\d+)*)$/i.exec(tok);
      if (!m) throw new Error("cannot read “" + tok + "”. Write terms like T0, CS01 or CCZ012, with commas once an index reaches 10");
      var name = m[1] ? m[1].toUpperCase() : null;
      var digits = m[2];
      var arity = name === "T" ? 1 : name === "CS" ? 2 : name === "CCZ" ? 3 : null;
      var wires;
      if (digits.indexOf(",") >= 0) wires = digits.split(",");
      else if (arity === 1) wires = [digits];
      else if (k > 10) {
        if (arity && arity > 1) throw new Error("“" + tok + "”: with more than 10 outputs, separate indices by commas, e.g. CS10,11");
        wires = [digits];
      } else wires = digits.split("");
      wires = wires.map(Number);
      if (arity && wires.length !== arity) throw new Error("“" + tok + "” is not a " + name + " term");
      if (wires.length < 1 || wires.length > 3) throw new Error("“" + tok + "” is not a level-3 term");
      wires.forEach(function (w) {
        if (!(w >= 0 && w < k)) throw new Error("“" + tok + "” uses output " + w + "; this factory has outputs 0…" + (k - 1));
      });
      wires.sort(function (a, b) { return a - b; });
      for (var i = 1; i < wires.length; i++) if (wires[i] === wires[i - 1]) throw new Error("“" + tok + "” repeats an output");
      var key = wires.join(",");
      if (seen[key]) delete seen[key]; else seen[key] = wires;
    });
    return Object.keys(seen).map(function (key) { return seen[key]; })
      .sort(function (a, b) { return a.length - b.length || (a.join(",") < b.join(",") ? -1 : 1); });
  }

  /* The catalogue's gate string: "+"-separated, digits run together when k <= 10. */
  function parseCatalogGate(gate, k) {
    if (!gate) return [];
    return gate.split("+").map(function (tok) {
      return (tok.indexOf(",") >= 0 ? tok.split(",") : (k > 10 ? [tok] : tok.split(""))).map(Number);
    });
  }

  function human(monos, k) {
    if (!monos.length) return "I (a Clifford gate)";
    var joiner = k > 10 ? "," : "";
    return monos.map(function (m) { return NAMES[m.length] + m.join(joiner); }).join("·");
  }

  /* ------------------------------------------------------------- the tensor */
  function tensor(k, monos) {
    var T = [];
    for (var a = 0; a < k; a++) T.push(new Array(k).fill(0));
    function put(x, y, z) { T[x][y] |= 1 << z; }
    monos.forEach(function (m) {
      if (m.length === 1) put(m[0], m[0], m[0]);
      else if (m.length === 2) {
        var p = m[0], q = m[1];
        [[p, p, q], [p, q, p], [q, p, p], [p, q, q], [q, p, q], [q, q, p]].forEach(function (t) { put(t[0], t[1], t[2]); });
      } else {
        var r = m[0], s = m[1], t3 = m[2];
        [[r, s, t3], [r, t3, s], [s, r, t3], [s, t3, r], [t3, r, s], [t3, s, r]].forEach(function (t) { put(t[0], t[1], t[2]); });
      }
    });
    return T;
  }

  function evaluate(T, u, v, w) {
    var acc = 0, bu = bits(u), bv = bits(v);
    for (var i = 0; i < bu.length; i++) {
      var row = T[bu[i]];
      for (var j = 0; j < bv.length; j++) acc ^= row[bv[j]];
    }
    return parity(acc & w);
  }

  /* rank over F_2 of rows, each an array of 32-bit words */
  function rankRows(rows) {
    var basis = [];
    rows.forEach(function (row) {
      var v = row.slice();
      basis.forEach(function (b) {
        var lead = b.lead;
        if ((v[lead >> 5] >>> (lead & 31)) & 1) for (var i = 0; i < v.length; i++) v[i] ^= b.v[i];
      });
      for (var w = 0; w < v.length; w++) {
        if (v[w]) {
          var bit = 31 - Math.clz32(v[w] & -v[w]);
          basis.push({ v: v, lead: w * 32 + bit });
          return;
        }
      }
    });
    return basis.length;
  }
  function rank(vectors) { return rankRows(vectors.map(function (v) { return [v]; })); }

  function coarse(k, T) {
    var flat = T.map(function (row) { return row.slice(); });
    var diag = T.map(function (row, a) { return row[a]; });
    return k + ":" + rankRows(flat) + ":" + rank(diag);
  }

  /* label of every nonzero u, packed as rank*4 + tau(u,u,u)*2 + (d_u != 0) */
  function labels(k, T) {
    var size = 1 << k, out = new Int32Array(size), B = new Array(k).fill(0), d = 0, u = 0;
    var diag = T.map(function (row, a) { return row[a]; });
    for (var step = 1; step < size; step++) {
      var a = 31 - Math.clz32(step & -step);
      u ^= 1 << a;
      for (var b = 0; b < k; b++) B[b] ^= T[a][b];
      d ^= diag[a];
      out[u] = rank(B) * 4 + parity(d & u) * 2 + (d !== 0 ? 1 : 0);
    }
    return out;
  }

  function sameTensor(A, B) {
    for (var a = 0; a < A.length; a++) for (var b = 0; b < A.length; b++) if (A[a][b] !== B[a][b]) return false;
    return true;
  }

  /* -------------------------------------------------------- the decision */
  /* {status: "equal" | "found", basis, images}  -- tau_L(images) = tau_R(basis)
   * {status: "no", reason}                       -- proved inequivalent
   * {status: "undecided", reason}                -- budget, or k above the cap */
  function transform(k, left, right, budget) {
    budget = budget || WORK_BUDGET;
    var TL = tensor(k, left), TR = tensor(k, right);
    var standard = [];
    for (var i = 0; i < k; i++) standard.push(1 << i);
    if (sameTensor(TL, TR)) return { status: "equal", basis: standard, images: standard.slice() };
    if (coarse(k, TL) !== coarse(k, TR)) {
      return { status: "no", reason: "the two gates' cubic forms have different ranks, and CNOT and S circuits preserve that rank" };
    }
    if (k > LABEL_K_CAP) {
      return { status: "undecided", reason: "with more than " + LABEL_K_CAP + " outputs only identical gates are decided in the browser" };
    }
    var LL = labels(k, TL), LR = labels(k, TR), size = 1 << k;
    var countL = {}, countR = {};
    for (var u = 1; u < size; u++) {
      countL[LL[u]] = (countL[LL[u]] || 0) + 1;
      countR[LR[u]] = (countR[LR[u]] || 0) + 1;
    }
    var keys = Object.keys(countL).concat(Object.keys(countR));
    for (var q = 0; q < keys.length; q++) {
      if (countL[keys[q]] !== countR[keys[q]]) {
        return { status: "no", reason: "the two gates differ in an invariant that CNOT and S circuits preserve" };
      }
    }
    var byLabel = {};
    for (u = 1; u < size; u++) (byLabel[LL[u]] = byLabel[LL[u]] || []).push(u);

    var order = [];
    for (u = 1; u < size; u++) order.push(u);
    order.sort(function (x, y) { return (byLabel[LR[x]].length - byLabel[LR[y]].length) || (x - y); });
    var basis = [], inSpan = new Uint8Array(size), spanList = [0];
    inSpan[0] = 1;
    for (var o = 0; o < order.length && basis.length < k; o++) {
      var p = order[o];
      if (inSpan[p]) continue;
      basis.push(p);
      var grow = spanList.map(function (s) { return s ^ p; });
      grow.forEach(function (s) { inSpan[s] = 1; });
      spanList = spanList.concat(grow);
    }
    var want = [];
    for (i = 0; i < k; i++) {
      want.push([]);
      for (var j = 0; j < k; j++) {
        want[i].push([]);
        for (var l = 0; l < k; l++) want[i][j].push(i <= j && j <= l ? evaluate(TR, basis[i], basis[j], basis[l]) : 0);
      }
    }
    var work = 0;
    function independent(images, cand) { return rank(images.concat([cand])) === images.length + 1; }

    function extend(i, images, spanS, spanI) {
      if (i === k) return images;
      var b = basis[i], cands = byLabel[LR[b]];
      for (var c = 0; c < cands.length; c++) {
        var cand = cands[c];
        if (++work > budget) throw new Error("budget");
        if (!independent(images, cand)) continue;
        var trial = images.concat([cand]), ok = true;
        for (var j = 0; j <= i && ok; j++) {
          for (var l = j; l <= i; l++) {
            work++;
            if (evaluate(TL, trial[j], trial[l], cand) !== want[j][l][i]) { ok = false; break; }
          }
        }
        if (!ok) continue;
        work += spanS.length;
        if (work > budget) throw new Error("budget");
        var nS = spanS.slice(), nI = spanI.slice();
        for (var s = 0; s < spanS.length; s++) {
          if (LL[spanI[s] ^ cand] !== LR[spanS[s] ^ b]) { ok = false; break; }
          nS.push(spanS[s] ^ b);
          nI.push(spanI[s] ^ cand);
        }
        if (!ok) continue;
        var found = extend(i + 1, trial, nS, nI);
        if (found) return found;
      }
      return null;
    }
    var images;
    try {
      images = extend(0, [], [0], [0]);
    } catch (e) {
      if (e.message === "budget") return { status: "undecided", reason: "the search ran out of its work budget" };
      throw e;
    }
    if (!images) return { status: "no", reason: "an exhaustive search found no change of output basis that relates them" };
    return { status: "found", basis: basis, images: images };
  }

  /* --------------------------------------------------------- construction */
  /* Coefficients (bitmask over vectors[]) writing target as their XOR, or -1. */
  function solveIn(vectors, target) {
    var rows = vectors.map(function (v, i) { return { v: v, c: 1 << i }; });
    var basis = [];
    rows.forEach(function (r) {
      var v = r.v, c = r.c;
      basis.forEach(function (b) { if ((v >>> b.lead) & 1) { v ^= b.v; c ^= b.c; } });
      if (v) basis.push({ v: v, c: c, lead: 31 - Math.clz32(v & -v) });
    });
    var t = target, cc = 0;
    basis.forEach(function (b) { if ((t >>> b.lead) & 1) { t ^= b.v; cc ^= b.c; } });
    return t ? -1 : cc;
  }

  function applyColumns(cols, x) {
    var y = 0;
    for (var q = 0; x; q++, x >>>= 1) if (x & 1) y ^= cols[q];
    return y;
  }

  function phaseTable(k, monos) {
    var size = 1 << k, f = new Uint8Array(size);
    var masks = monos.map(function (m) {
      return { mask: m.reduce(function (acc, w) { return acc | (1 << w); }, 0), weight: m.length === 1 ? 1 : m.length === 2 ? 2 : 4 };
    });
    for (var x = 0; x < size; x++) {
      var v = 0;
      for (var i = 0; i < masks.length; i++) if ((x & masks[i].mask) === masks[i].mask) v += masks[i].weight;
      f[x] = v & 7;
    }
    return f;
  }

  /* CNOTs, in time order, whose product sends |x> to |Mx>; cols[q] = M e_q. */
  function cnotCircuit(k, cols) {
    var rows = [];
    for (var t = 0; t < k; t++) {
      var r = 0;
      for (var q = 0; q < k; q++) if ((cols[q] >>> t) & 1) r |= 1 << q;
      rows.push(r);
    }
    var ops = [];
    for (var j = 0; j < k; j++) {
      if (!((rows[j] >>> j) & 1)) {
        for (var i = j + 1; i < k; i++) {
          if ((rows[i] >>> j) & 1) { rows[j] ^= rows[i]; ops.push([i, j]); break; }
        }
      }
      for (i = 0; i < k; i++) {
        if (i !== j && ((rows[i] >>> j) & 1)) { rows[i] ^= rows[j]; ops.push([j, i]); }
      }
    }
    return ops.reverse().map(function (op) { return { control: op[0], target: op[1] }; });
  }

  function simulateCnots(gates, x) {
    gates.forEach(function (g) { if ((x >>> g.control) & 1) x ^= 1 << g.target; });
    return x;
  }

  /* The witness -> an explicit circuit, checked on every basis state. */
  function construct(k, left, right, witness) {
    var size = 1 << k, A = [], q;
    for (q = 0; q < k; q++) {                       // A e_q, from A basis[i] = images[i]
      var c = solveIn(witness.basis, 1 << q);
      A.push(applyColumns(witness.images, c));
    }
    var M = [];                                     // M = A^-1, so U|x> = |A^-1 x>
    for (q = 0; q < k; q++) M.push(solveIn(A, 1 << q));
    var cnots = cnotCircuit(k, M);

    var fL = phaseTable(k, left), fR = phaseTable(k, right);
    var corr = new Int32Array(size), c0 = (fR[0] - fL[0] + 8) & 7;
    for (var x = 0; x < size; x++) {
      corr[x] = ((fR[x] - fL[applyColumns(A, x)] - c0) % 8 + 16) % 8;
      if (corr[x] & 1) return { ok: false, reason: "the remaining phase is not Clifford (odd value)" };
      corr[x] >>= 1;                                // now in Z_4
    }
    for (var bit = 0; bit < k; bit++) {             // Moebius transform over Z
      for (x = 0; x < size; x++) if ((x >>> bit) & 1) corr[x] -= corr[x ^ (1 << bit)];
    }
    var singles = [], czs = [];
    for (x = 1; x < size; x++) {
      var coef = ((corr[x] % 4) + 4) % 4, deg = popcount(x);
      if (!coef) continue;
      if (deg === 1) singles.push({ q: 31 - Math.clz32(x), power: coef });
      else if (deg === 2 && coef === 2) czs.push(bits(x));
      else return { ok: false, reason: "the remaining phase is not Clifford" };
    }

    /* the check, by brute force on every basis state */
    for (q = 0; q < k; q++) {
      if (simulateCnots(cnots, 1 << q) !== M[q]) return { ok: false, reason: "CNOT circuit check failed" };
    }
    var corrPhase = function (y) {
      var v = 0;
      singles.forEach(function (s) { if ((y >>> s.q) & 1) v += 2 * s.power; });
      czs.forEach(function (p) { if (((y >>> p[0]) & 1) && ((y >>> p[1]) & 1)) v += 4; });
      return v;
    };
    for (var y = 0; y < size; y++) {
      // U D_f U^dagger |y> = w^{f(A y)} |y>  (U^dagger |y> = |A y>), then the corrections
      var got = (fL[simulateInverse(cnots, y, k)] + corrPhase(y) + c0) & 7;
      if (got !== fR[y]) return { ok: false, reason: "phase check failed at input " + y };
    }
    return { ok: true, A: A, M: M, cnots: cnots, singles: singles, czs: czs, globalPhase: c0, checked: size };
  }

  /* U^dagger |y>: run the CNOTs backwards. */
  function simulateInverse(gates, y) {
    for (var i = gates.length - 1; i >= 0; i--) {
      var g = gates[i];
      if ((y >>> g.control) & 1) y ^= 1 << g.target;
    }
    return y;
  }

  /* A random equivalent gate: f o A for a random invertible A, read off mod Clifford. */
  function randomEquivalent(k, monos) {
    if (k > LABEL_K_CAP) return null;
    var T = tensor(k, monos), A;
    do {
      A = [];
      for (var q = 0; q < k; q++) A.push(Math.floor(Math.random() * (1 << k)) || (1 << q));
    } while (rank(A) < k);
    var out = [];
    for (var a = 0; a < k; a++) {
      if (evaluate(T, A[a], A[a], A[a])) out.push([a]);
    }
    for (a = 0; a < k; a++) for (var b = a + 1; b < k; b++) {
      if (evaluate(T, A[a], A[a], A[b])) out.push([a, b]);
    }
    for (a = 0; a < k; a++) for (b = a + 1; b < k; b++) for (var c = b + 1; c < k; c++) {
      if (evaluate(T, A[a], A[b], A[c])) out.push([a, b, c]);
    }
    return out;
  }

  global.GLEquiv = {
    LABEL_K_CAP: LABEL_K_CAP,
    parseGate: parseGate,
    parseCatalogGate: parseCatalogGate,
    human: human,
    transform: transform,
    construct: construct,
    randomEquivalent: randomEquivalent
  };
}(window));
