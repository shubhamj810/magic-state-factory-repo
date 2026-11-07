#!/usr/bin/env python3
"""Brute-force test of trellis_count on random small problems (random column orders included)."""
import itertools, random, struct, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import trellis_count as TC
HERE = Path(__file__).resolve().parent
rng = random.Random(int(sys.argv[2]) if len(sys.argv) > 2 else 1)
ok = 0
for trial in range(int(sys.argv[1]) if len(sys.argv) > 1 else 200):
    n = rng.randint(2, 14); nb = rng.choice([2, 3, 5, 8, 20, 70]); W = rng.randint(1, n)
    base = [rng.getrandbits(nb) for _ in range(rng.randint(1, 6))]
    vecs = []
    for _ in range(n):
        v = 0
        for b in base:
            if rng.random() < 0.5: v ^= b
        if rng.random() < 0.2: v ^= rng.getrandbits(nb)
        vecs.append(v)
    brute = [0] * (W + 1)
    for w in range(W + 1):
        for sup in itertools.combinations(range(n), w):
            x = 0
            for j in sup: x ^= vecs[j]
            brute[w] += x == 0
    steps, maxcut = TC.steps_for(vecs, nb, W)
    with tempfile.NamedTemporaryFile(dir=HERE.parent / "tmp", suffix=".bin", delete=False) as f:
        f.write(struct.pack("<iii", len(steps), W, maxcut))
        for a, b, packed, pg in steps:
            f.write(struct.pack("<ii", a, b)); f.write(struct.pack("<%dQ" % (a + 1), *(packed + [pg])))
        fn = f.name
    r = subprocess.run([str(HERE / "trellis_count"), fn], capture_output=True, text=True); Path(fn).unlink()
    got = [int(x) for x in r.stdout.split()]
    assert got == brute, (trial, n, nb, W, got, brute)
    ok += 1
print("ok:", ok, "random problems agree with brute force")
