"""For one class g: delta_z(g) per fibre by (i) exact search with canonical reduction (own), (ii) the
weighted agent's fibproof.py method (partial reduction, copied semantics), to expose any disagreement."""
import itertools, json, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import fibown as F

def partial_reduce(piv, v):          # semantics of fibproof.Span.reduce
    while v:
        h = v.bit_length() - 1
        b = piv.get(h)
        if b is None:
            return v
        v ^= b
    return 0

def their_span(vecs):
    piv = {}
    for v in vecs:
        v = partial_reduce(piv, v)
        if v:
            piv[v.bit_length() - 1] = v
    return piv

d = json.load(open(sys.argv[1])); g = int(sys.argv[2])
P = d["points"]
fib = {z: sorted(p & 255 for p in P if p >> 8 == z) for z in range(8)}
tot_own = tot_their = 0
for z in range(8):
    Pz = fib[z]; out = [y for y in range(256) if y not in set(Pz)]
    # own exact delta up to 4 by brute force on canonical reps
    B = F.Basis()
    for i, y in enumerate(Pz): B.add(F.psi2(y), 1 << i)
    target = B.reduce(g << 9)[0]
    rs = [B.reduce(F.psi2(y))[0] for y in out]
    own = None
    if target == 0: own = 0
    else:
        for w in (1, 2, 3):
            for S in itertools.combinations(range(len(out)), w):
                acc = 0
                for i in S: acc ^= rs[i]
                if acc == target: own = w; break
            if own is not None: break
    # their method
    piv = their_span(F.psi2(y) for y in Pz)
    r = partial_reduce(piv, g << 9)
    R = {partial_reduce(piv, F.psi2(b)) for b in out}
    if r == 0: th = 0
    elif r in R: th = 1
    else:
        R2 = {a ^ b for a, b in itertools.combinations(list(R), 2)} | R
        th = 2 if r in R2 else 3
    print(z, "own", own if own is not None else ">=4", "their", th)
    tot_own += own if own is not None else 4
    tot_their += th
print("sum own (>=4 counted as 4)", tot_own, "their (capped 3)", tot_their)
