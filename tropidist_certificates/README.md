# Distances certified by tropidist

tropidist is the exact distance solver of B. Cheng, N. Guo and F. Pan,
"Certifying quantum code and circuit distances at scale",
[arXiv:2611.08247](https://arxiv.org/abs/2611.08247)
([github.com/Fanerst/tropidist](https://github.com/Fanerst/tropidist), MIT
licence). It computes `Δ(H, L) = min{|e| : He = 0, Le ≠ 0}` over GF(2) and
returns a certified lower bound together with a fault set of weight equal to
its upper bound. A factory's distance is this problem with `H` the check rows
(wires `k..N-1`) and `L` the output rows (wires `0..k-1`), one column per
rotation in the row's stored order.

[`certificates.json`](certificates.json) holds its results on all 62 rows
whose distance the catalogue did not prove exactly as of commit `d15e4eb`. Each
record is tied to its row by the SHA-256 of the row's columns.
[`../master_catalog/migrations/tropidist_certificates_2026_11_06.py`](../master_catalog/migrations/tropidist_certificates_2026_11_06.py)
writes them into the catalogue. It refuses a record whose columns no longer
match.

## How it was run

Every run used tropidist commit `b03ec2d4` with its benchmark entry point
`bench/adapters/ours_pipeline.py --variant full --threads 1 --config dp=2`. That
is the configuration of the paper's benchmark. The pipeline was given no
distance, symmetry or hint. Runs took place on a laptop on 6 November 2026, at
600 s per row in a first pass and up to 3,600 s in later passes.

The same runs were first made on 1,752 rows whose distance the catalogue
already proves exactly: every main-file row, and every large-file row with
`n ≤ 11,000`. tropidist returned that exact distance on all 1,752, each with a
fault of that weight that the catalogue's code accepts. The `validation` block
of the JSON gives the counts by distance.

## What entered the catalogue

Twenty-nine rows changed, and no row's `d` or label did.

- 901.123.6.a, 902.122.6.a and 904.120.6.a to 912.112.6.a are now exact at
  `d = 6`, with this folder's own proof. The sweep here had already proved
  that no lighter fault exists, and tropidist found a fault of weight 6, which
  `verify_catalog.py` re-checks as `d_witness`. Their `A_d` is `null` because
  the count does not reach weight 6 at `n ≈ 900`.
- 177.1.7.a, 185.1.7.a and 189.1.7.a (9), 271.1.7.a, 279.1.7.a and 283.1.7.a
  (11), and 401.1.6.a and 417.1.6.a (13) already carried the doubling
  theorem's lower bound and a fault of that weight. Their certificate now also
  cites tropidist's independent computation of the same exact value.
- 1675.373.3.a, 1676.372.3.a and 1683.365.3.a already carried the gamma
  frontier release's exact distance 4. tropidist computes the same value, and
  its fault of weight 4 is now stored as `d_witness`.
- 511.9.6.a (7), 512.39.6.a (8) and 512.84.6.a (8) get a certificate
  `d = 7` or `d = 8`. tropidist's lower bound meets the weight of the row's
  stored fault.
- 935.89.6.a, 936.88.6.a, 988.36.6.a and 998.26.6.a get a certified lower
  bound `d ≥ 7`.

Where tropidist's lower bound is no stronger than the row already states, the
row is unchanged. This holds for the 28 doubled transversal-T codes from
441.1.6.a to 3239.1.3.a, whose theorem bounds are higher than what tropidist
reached in the time given. It also holds for 742.36.6.a, 756.32.6.a and
1715.287.3.a, where the gamma frontier release certifies more, and for
937.87.6.a and 959.65.6.a.

## What rests on what

The lower bounds in the certificates are tropidist's and are not re-derived by
`verify_catalog.py`. Some have independent support. An independent
syndrome-trellis program, written for this study, gives the same exact values
for 177, 185, 189, 271, 279, 283, 401 and 511.9.6.a. For the eight doubled
codes, the doubling theorem gives the same lower bound by a separate argument.
The values of 417.1.6.a (13), 512.39.6.a (8) and 512.84.6.a (8), and the
four bounds `d ≥ 7`, rest on tropidist alone. Every fault stored here is
re-checked by `verify_catalog.py`.
