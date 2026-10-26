"""Leading-order output error and acceptance of the Fig. 1 factories and of the prior construction for each target.

Noise model (as in the paper): every input magic state carries an independent Z fault with probability p; a
fault on an input of the parity rotation on support S applies Z_S. The factory accepts when every check qubit
returns the trivial X outcome, i.e. when the check parts of the faults cancel. All factories here have
distance 2, so acceptance is 1 - n p + O(p^2) and the probability that the accepted output state is wrong is
c p^2 + O(p^3), where c counts the pairs of faults whose check parts cancel and whose output parts do not.
For "distil the parts separately" the targets' parts come from independent factories, so n and c add.
Writes outputs/error_coefficients.json. Run: python3 searches/error_coefficients.py
"""
import csv, json, math, os, sys, urllib.parse
from itertools import combinations
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
csv.field_size_limit(sys.maxsize)
import unified_search as us
ROOT = os.path.dirname(HERE)


def decode(url):
    """Factory rotations (support, coefficient units of pi/2^L) from a Quirk link of quirk_url()."""
    d = json.loads(urllib.parse.unquote(url.split("circuit=")[1])); custom = {g["id"]: g for g in d.get("gates", [])}
    cols = d["cols"]; b = next((i for i, c in enumerate(cols) if "Bloch" in c), len(cols))
    def ang(g):
        if g in ("i", "-i"): return (1 if g == "i" else -1) / 4
        if g in ("√i", "√-i"): return (1 if g == "√i" else -1) / 8
        z = complex(custom[g]["matrix"].split(",")[0].strip("{}").replace("i", "j")); return math.atan2(z.imag, z.real) / (2 * math.pi)
    return [(frozenset(q for q, g in enumerate(c) if g == "zpar"), ang([x for x in c if x not in (1, "zpar")][0]))
            for c in cols[:b] if "zpar" in c]


def gates_of(row):
    L = int(row["l"]); mod = 1 << L; g = {}
    for S, a in decode(row["quirk"]): g[S] = (g.get(S, 0) + round(a * mod)) % mod      # e^{2 pi i a} = a 2^L units of pi/2^L
    return [(S, c) for S, c in g.items() if c]


def coefficients(gates, k, L):
    """(n, c): input count and number of undetected weight-2 fault sets that corrupt the output."""
    out = set(range(k)); faults = []
    for S, c in gates:
        for _ in range(us.inputs(c, L)):                  # one fault location per input magic state
            faults.append((frozenset(S - out), frozenset(S & out)))
    assert all(ch for ch, _ in faults), "a single fault goes undetected: distance 1"
    bad = sum(1 for (c1, o1), (c2, o2) in combinations(faults, 2) if c1 == c2 and o1 != o2)
    return len(faults), bad


def syn_gates(names, mu):
    """The synthillation construction for a target, as parity rotations (one T each), outputs first."""
    import synthillation_compare as sc
    k, target = sc.tgt(names); A = sc.opt_A(k, target); tau = len(A)
    lin = any(len(T) == 1 for T in target); B = sc.opt_B(k, target, mu)
    if lin:
        tm = sc.C14[{(0, 0): 1, (0, 1): 2, (1, 0): 3, (1, 1): 4}[(tau % 2, mu % 2)]]
        c = sum(1 << i for i in range(k) if frozenset([i]) in target); blocks = [A, B, B] + [[c]] * 4
    else:
        tm = sc.T5[(tau % 2, mu % 2)]; blocks = [A, B, B]
    blocks += [[0]] * (len(tm[0]) - len(blocks)); R = len(tm)
    cols = [v | sum(1 << (k + r) for r in range(R) if tm[r][bi]) for bi, blk in enumerate(blocks) for v in blk]
    assert sc.coeffs_ok(cols, k + R, k, target, 3)
    return k, [(frozenset(q for q in range(k + R) if y >> q & 1), 1) for y in cols]


def set_partitions(items):
    if not items:
        yield []
        return
    first, rest = items[0], items[1:]
    for p in set_partitions(rest):
        yield [[first]] + p
        for i in range(len(p)):
            yield p[:i] + [[first] + p[i]] + p[i + 1:]


if __name__ == "__main__":
    from symfree_search import solve_binding
    rows = list(csv.DictReader(open(os.path.join(ROOT, "outputs", "smallest_per_class.csv"))))
    k78 = list(csv.DictReader(open(os.path.join(ROOT, "outputs", "l3_k78_targets.csv"))))
    SIZE = {"T": 1, "CS": 2, "CCZ": 3, "sT": 1, "CT": 2, "CCS": 3}
    NAME = {"T": r"\mathrm{T}", "CS": r"\mathrm{CS}", "CCZ": r"\mathrm{CCZ}", "sT": r"\mathrm{\sqrt{T}}", "CT": r"\mathrm{CT}", "CCS": r"\mathrm{CCS}"}
    def label(parts):
        """Canonical reduced label of a product of parts on consecutive qubits, larger gates first (as fmt_poly)."""
        out, q = [], 1
        for p in sorted(parts, key=lambda p: -SIZE[p]):
            out.append(NAME[p] + "_{" + "".join(str(q + i) for i in range(SIZE[p])) + "}"); q += SIZE[p]
        return "".join(out)
    def best_factory(L, parts):
        k = sum(SIZE[p] for p in parts); red = label(parts)
        if L == 3 and k >= 7:
            c = [r for r in k78 if r["k"] == str(k) and r["reduced"] == red]
            if not c: return None
            r = min(c, key=lambda r: int(r["n"])); blocks = [int(b) for b in r["params"].split("=")[1].split("+")]
            sol = solve_binding(blocks, int(r["N"]) - k, L)
            return k, [(frozenset(S), c % 8) for S, c in sol["gates"]]
        c = [r for r in rows if r["l"] == str(L) and r["k"] == str(k) and r["reduced"] == red]
        if not c: return None
        r = min(c, key=lambda r: int(r["n"]))
        return k, gates_of(r)
    def prior_parts(L, parts):
        """Cheapest way to distil the target as independent factories for groups of its parts: (n, c)."""
        best = None
        for P in set_partitions(list(range(len(parts)))):
            if len(P) == 1:
                continue                                  # the whole target in one factory is the new factory itself
            tot_n = tot_c = 0; ok = True
            for grp in P:
                fac = best_factory(L, [parts[i] for i in grp])
                if fac is None: ok = False; break
                a, b = coefficients(fac[1], fac[0], L); tot_n += a; tot_c += b
            if ok and (best is None or (tot_n, tot_c) < best): best = (tot_n, tot_c)
        return best
    # (label, level, parts, prior kind, synthillation spec, prior n in Fig. 1)
    FIG1 = [("CS12 T3", 3, ["CS", "T"], "parts", None, 26), ("CS12 CS34 CS56", 3, ["CS"] * 3, "syn", (["CS"] * 3, 7), 26),
            ("CS12 CS34 T5", 3, ["CS", "CS", "T"], "syn", (["CS", "CS", "T"], 5), 28), ("CCZ123 CS45 T6", 3, ["CCZ", "CS", "T"], "parts", None, 34),
            ("CS12 T3 T4 T5", 3, ["CS", "T", "T", "T"], "parts", None, 32), ("CS12 T3...T7", 3, ["CS"] + ["T"] * 5, "parts", None, 38),
            ("CS12 CS34 CS56 T7", 3, ["CS"] * 3 + ["T"], "parts", None, 50), ("CT12 sT3", 4, ["CT", "sT"], "parts", None, 58),
            ("CCS123 sT4", 4, ["CCS", "sT"], "parts", None, 54), ("CT12 sT3 sT4", 4, ["CT", "sT", "sT"], "parts", None, 58),
            ("CT12 CT34 sT5", 4, ["CT", "CT", "sT"], "parts", None, 78), ("CCS123 CT45 sT6", 4, ["CCS", "CT", "sT"], "parts", None, 82),
            ("CT12 CT34 sT5 sT6", 4, ["CT", "CT", "sT", "sT"], "parts", None, 78)]
    def by_type(L, parts):
        """Distil the parts of each gate type together, with the smallest factory for that same-type product."""
        tn = tc = 0
        for t in dict.fromkeys(parts):
            fac = best_factory(L, [p for p in parts if p == t])
            if fac is None:
                return None
            a, b = coefficients(fac[1], fac[0], L); tn += a; tc += b
        return tn, tc
    import synthillation_compare as sc
    MU = {tuple(sorted(n)): mu for n, mu in sc.TARGETS}
    SYN = {"T": "T", "CS": "CS", "CCZ": "CCZ"}
    def syn_cost(grp):
        key = tuple(sorted(SYN[p] for p in grp))
        if key not in MU:
            return None
        try:
            kk, gg = syn_gates(list(key), MU[key])
        except AssertionError:
            return None                                   # the template gives no valid factory for this group
        return coefficients(gg, kk, 3)
    def type_cost(L, grp):
        fac = best_factory(L, grp) if len(set(grp)) == 1 else None
        return None if fac is None else coefficients(fac[1], fac[0], L)
    def prior(L, parts):
        """Best prior construction: split the parts into groups; distil each group either with the smallest factory
        for that single gate type, or (l=3) with the synthillation construction. A target of one gate type is
        compared with synthillation only, since its smallest factory is the factory itself."""
        best = None
        for P in set_partitions(list(range(len(parts)))):
            if len(P) == 1 and len(set(parts)) > 1 and L == 4:
                continue
            tot = [0, 0]; ok = True; how = []
            for grp in P:
                g = [parts[i] for i in grp]
                opts = []
                if not (len(P) == 1 and len(set(parts)) == 1):
                    t = type_cost(L, g)
                    if t: opts.append((t, "factory(" + "".join(g) + ")"))
                if L == 3:
                    sy = syn_cost(g)
                    if sy: opts.append((sy, "synth(" + "".join(g) + ")"))
                if not opts: ok = False; break
                (a_, b_), h = min(opts)
                tot[0] += a_; tot[1] += b_; how.append(h)
            if ok and (best is None or tuple(tot) < best[0]): best = (tuple(tot), " + ".join(how))
        return best
    out = []
    for lab, L, parts, kind, syn, fig_prior in FIG1:
        k, g = best_factory(L, parts); n, c = coefficients(g, k, L)
        (pn, pc), how = prior(L, parts)
        out.append(dict(target=lab, l=L, k=k, n=n, c=c, prior_n=pn, prior_c=pc, prior=how, fig1_prior_n=fig_prior))
        print(f"l={L} {lab:18s} ours n={n:3d} c={c:4d} | best prior n={pn:3d} c={pc:4d} via {how}  (Fig.1: {fig_prior})", flush=True)
    json.dump(out, open(os.path.join(ROOT, "outputs", "error_coefficients.json"), "w"), indent=1)
