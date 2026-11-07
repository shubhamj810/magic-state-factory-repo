#!/usr/bin/env python3
"""Own check of the curve outer code (no sanjose2 code): the curve p_K(y) = x^17 over GF(256), K an F_2-subspace of
GF(16) with |K| = t, p_K(y) = prod_{k in K}(y + k).  Checks:
  * the affine point count N = 256 t;
  * the evaluation ranks of the monomials x^i y^j (j < t, pole order t i + 17 j <= a) and <= b = N + 2g - 2 - a,
    g = (t - 1)(17 - 1)/2, against the counts a - g + 1 and b - g + 1;
  * C = L(a P_inf) is orthogonal to L(b P_inf) (the matrix product over GF(256) is zero) and the dimensions add to
    N, so C^perp = L(b P_inf) under the plain inner product (v = 1);
  * the first nonzero power sum sum_P f(P) over monomials appears above pole order N + 2g - 2 (residues of
    dx/(x^256 + x) equal 1);
  * a word of L(b P_inf) of weight N - b exists when t | b: prod_{x0 not in Y}(x + x0), |Y| = 256 - b/t, so the
    Goppa bound delta >= N - b = a - 2g + 2 is attained.

    python curvecheck.py t a [modulus] [Kbasis(json)]
"""
import json
import sys
import time

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from sjcheck import GF  # noqa: E402  (own GF class, written in this folder)


def rank_rows(F, rows):
    rows = [r[:] for r in rows]
    piv = []
    r = 0
    ncol = len(rows[0])
    for c in range(ncol):
        p = next((i for i in range(r, len(rows)) if rows[i][c]), None)
        if p is None:
            continue
        rows[r], rows[p] = rows[p], rows[r]
        iv = F.inv(rows[r][c])
        rows[r] = [F.mul(iv, x) for x in rows[r]]
        for i in range(r + 1, len(rows)):
            if rows[i][c]:
                f = rows[i][c]
                rows[i] = [x ^ F.mul(f, y) for x, y in zip(rows[i], rows[r])]
        r += 1
        if r == len(rows):
            break
    return r


def main():
    t0 = time.time()
    t, a = int(sys.argv[1]), int(sys.argv[2])
    mod = int(sys.argv[3]) if len(sys.argv) > 3 else 285
    F = GF(8, mod)
    sub16 = [x for x in range(256) if F.pow(x, 16) == x]
    if len(sys.argv) > 4:
        Kb = json.loads(sys.argv[4])
    else:
        Kb = []
        for x in sorted(sub16):
            v = x
            for b in Kb:
                v = min(v, v ^ b)
            if v:
                Kb.append(x)
        Kb = Kb[: t.bit_length() - 1]
    K = [0]
    for b in Kb:
        K = K + [k ^ b for k in K]
    assert len(K) == t and all(k in sub16 for k in K)
    pts = []
    for x in range(256):
        rhs = F.pow(x, 17)
        for y in range(256):
            val = 1
            for k in K:
                val = F.mul(val, y ^ k)
            if val == rhs:
                pts.append((x, y))
    N = len(pts)
    g = (t - 1) * 16 // 2
    b = N + 2 * g - 2 - a
    res = {"t": t, "a": a, "modulus": mod, "K": K, "N": N, "N_eq_256t": N == 256 * t, "g": g, "b": b,
           "4a_le_N+2g-2": 4 * a <= N + 2 * g - 2}

    def monos(c):
        return [(i, j) for j in range(t) for i in range(c // t + 1) if t * i + 17 * j <= c]

    def ev(i, j):
        return [F.mul(F.pow(x, i), F.pow(y, j)) for x, y in pts]
    Ma, Mb = monos(a), monos(b)
    Ga = [ev(i, j) for i, j in Ma]
    Gb = [ev(i, j) for i, j in Mb]
    res["dim_a_count"], res["dim_b_count"] = len(Ma), len(Mb)
    res["dim_a_expected"], res["dim_b_expected"] = a - g + 1, b - g + 1
    res["rank_a"] = rank_rows(F, Ga)
    res["rank_b"] = rank_rows(F, Gb)
    # orthogonality: all products of a C monomial and an L(b) monomial sum to 0 over the points
    bad = 0
    for ra in Ga:
        for rb in Gb:
            s = 0
            for x, y in zip(ra, rb):
                s ^= F.mul(x, y)
            if s:
                bad += 1
    res["nonorthogonal_pairs"] = bad
    res["C_perp_is_L(b)"] = bad == 0 and res["rank_a"] + res["rank_b"] == N
    # power sums of monomials by pole order
    first_nonzero = None
    for c in range(0, N + 2 * g + 2 * t + 40):
        for i, j in [(i, j) for j in range(t) for i in range(c // t + 1) if t * i + 17 * j == c]:
            s = 0
            for x, y in pts:
                s ^= F.mul(F.pow(x, i), F.pow(y, j))
            if s and first_nonzero is None:
                first_nonzero = c
        if first_nonzero is not None:
            break
    res["first_nonzero_moment_pole_order"] = first_nonzero
    res["expected_first_nonzero"] = N + 2 * g - 1
    # attaining word
    if b % t == 0:
        Ysz = 256 - b // t
        Y = set(range(Ysz))
        wt = 0
        for x, y in pts:
            val = 1
            for x0 in range(256):
                if x0 not in Y:
                    val = F.mul(val, x ^ x0)
            wt += 1 if val else 0
        res["fibre_word_weight"] = wt
        res["N_minus_b"] = N - b
    res["delta_bound"] = a - 2 * g + 2
    res["seconds"] = round(time.time() - t0, 1)
    print(json.dumps(res), flush=True)


if __name__ == "__main__":
    main()
