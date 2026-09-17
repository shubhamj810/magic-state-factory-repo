# The open sector: parents of the affine-rank-6 word

One weight-48 word of RM(3,7) has affine rank 6: class 3470, `a + abc`, the
length-48 table's single `m = 6` representative (stabiliser order
31,708,938,240 — the largest of any weight-48 class).  Inside its own span F₂⁶
it is a 48-point set with 16 points missing; its origins fall into 2
stabiliser orbits (on / off the support), plus the lift:

| n | origin | check rank | κ = dim V₃(C) | form ranks | μ upper bound | sampled compatible-pair density | est. width-2 subspaces |
|---|---|---|---|---|---|---|---|
| 47 | on S | 6 | 21 | 12,12,12,12,12,6 | 15 | 0.0154 | ≈ 1.1 × 10¹⁰ |
| 48 | off S | 6 | 21 | 12 ×6 | 15 | 0.0162 | ≈ 1.2 × 10¹⁰ |
| 48 | lift | 7 | 20 | 12,12,12,12,12,6,6 | 14 | 0.0097 | ≈ 1.8 × 10⁹ |

(`docs/open_rank6_bounds.json`, from `open_rank6_bounds.py`; the density is
a 20,000-pair sample.)

## Why brute force stops here

`factorylib.parent.compatible_subspaces` walks every compatible subspace of
the quotient V₃(C): 2^κ representatives, and each node costs a span over a
"safe" subspace of dimension ≈ κ − 6.  With κ = 21 the width-1 layer alone is
2 million nodes, the width-2 layer ~10¹⁰, and widths up to 15 are possible.
The n ≤ 46 and rank ≥ 7 parents of this directory have κ ≤ 13 and μ ≤ 7 and
cost milliseconds to minutes; these three would cost years.  Memory is the
other wall: the 2^κ representatives of one κ = 21 parent are ~1 GB.

```
   κ  = 21  ─┐                                         this directory's
   μ  ≤ 15   │  brute-force cost ~ (#compatible          heaviest swept
             │  subspaces) × 2^(κ-6)                     parents: κ = 13,
   n  = 47   │  ≈ 10^10 × 3·10^4  ≈ 10^14 node-ops       μ ≤ 7, ~3·10^5
             ┘                                            subspaces, seconds to an hour
```

## What could close it

* **Symmetry.**  The stabiliser has order 3 × 10¹⁰; the compatible-subspace
  walk should be done on orbits under it (a Schreier–Sims / canonical-augmentation
  walk), which would cut the count by up to that factor.  Nothing in
  `factorylib` does this today.
* **Theory.**  `a + abc` is the simplest cubic word (one cubic monomial,
  one linear term).  A direct description of V₃(C) for it may make the frame
  enumeration algebraic rather than combinatorial.
* **Width bound.**  Any argument that a distance-3 frame on these parents
  has width ≤ w reduces the walk to the layers ≤ w.

## Effect on the catalogue

Every (n, k, S_k) class carried by these three parents — and only these — is
absent from `classification_n41_48.json`.  Every other check rank at n = 47,
48 and every check rank at n ≤ 46 is covered (see `CLASSIFICATION_N41_48.md`,
"What is covered").  In particular a class with k > 7 at n = 47 or 48, if any
exists, can only live here.
