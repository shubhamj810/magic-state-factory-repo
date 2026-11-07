# Transversal-T codes of Jain and Albert, and of A. Gong

This folder rebuilds the one-qubit codes with a transversal logical `T` gate
from

> S. P. Jain and V. V. Albert, “Transversal Clifford and T-gate codes of short
> length and high distance,” *IEEE Journal on Selected Areas in Information
> Theory* **6**, 127–137 (2025).
> [doi:10.1109/JSAIT.2025.3570832](https://doi.org/10.1109/JSAIT.2025.3570832),
> [arXiv:2408.12752](https://arxiv.org/abs/2408.12752)

It writes each code as a factory and merges the factories into the
[master catalogue](../master_catalog/README.md). The paper prints the codes'
parameters and how to build them, not their matrices, and it has no software
release. So nothing here is copied: [`build_codes.py`](build_codes.py) builds
every code from the paper's recipe and the classical codes it names. Please cite
the paper for these codes.

```bibtex
@article{jain2025transversal,
  author  = {Jain, Shubham P. and Albert, Victor V.},
  title   = {Transversal {Clifford} and {T}-Gate Codes of Short Length and High Distance},
  journal = {IEEE Journal on Selected Areas in Information Theory},
  volume  = {6},
  pages   = {127--137},
  year    = {2025},
  doi     = {10.1109/JSAIT.2025.3570832},
  eprint  = {2408.12752},
  archivePrefix = {arXiv}
}
```

| file | contents |
|---|---|
| [`build_codes.py`](build_codes.py) | builds every code, checks it, and writes the two files below. `--check` rebuilds them and fails if a committed file differs |
| [`min_distance.py`](min_distance.py) | a proved lower bound on a code's minimum distance (Brouwer–Zimmermann, two disjoint information sets), used for the self-dual inputs of length 79 to 103 |
| [`bz_bound.c`](bz_bound.c) | the same bound in C, for the extended QR code `[168,84]`: every sum of 1 to `t` rows of one information set, formed once by a depth-first walk on threads, resumable from a log; `min_distance.py --qr 167 --t 10 9` drives it and writes the run record |
| [`xqr168_distance.json`](xqr168_distance.json) | that run: `[168,84]` has minimum distance 24 (3.6·10^12 sums, 3,559 s on two threads, 7 November 2026) |
| [`certify_distances.py`](certify_distances.py) | writes `distance_certificates.json`: the doubling theorem's bound for each code whose inputs' distances are all proved here, `--check` compares |
| [`search_sd70.py`](search_sd70.py) | the exhaustive search that found the self-dual `[70,35,12]` code behind Table I's `[[69,1,13]]` (see below), ~2 minutes |
| [`gong_self_dual_codes.json`](gong_self_dual_codes.json) | the stabilisers of A. Gong's doubly even self-dual `[[41,1,9]]` and `[[65,1,13]]` codes, copied from her repository (see [Gong's codes](#gongs-codes)) |
| [`codes.json`](codes.json) | one entry per code: parameters, the paper's tables, how it was built, its two inputs, a harmful fault of the paper's weight, the weak-triply-even partition where there is one, and the distance certificate |
| [`factories.json`](factories.json) | the same codes in the input format of [`merge_results.py`](../master_catalog/merge_results.py): wire 0 is the logical row (the output), wires `1..` are the X stabilisers (the checks), and column `j` is the set of rows containing qubit `j` |
| [`tests/`](tests/) | the codes re-checked with the catalogue's own primitives, the small inputs' distances computed by enumeration, and the catalogue rows they became |

## The construction

The paper's doubling map (its Sec. III, after Betsumiya–Munemasa and
Bravyi–Cross) takes a self-dual CSS code `[[n_sd,1,d_sd]]` and a triorthogonal
code `[[n_tri,1,d_tri]]`, both with logical X on every qubit. It returns the
triorthogonal code `[[2n_sd + n_tri, 1, min(d_sd, d_tri + 2)]]`, whose
generator matrix is

```
[ 1     1     1     ]   the logical row
[ C_sd  C_sd  0     ]   the self-dual code's X stabilisers, twice
[ 0     0     C_tri ]   the triorthogonal code's X stabilisers
[ 0     1     1     ]
```

The self-dual inputs come from classical self-dual codes by the paper's
puncture-and-dualise map (Lemma 2.4). Puncture the last coordinate to get `C`.
Then `C⊥` is both the X and the Z stabiliser space, and every qubit carries the
logical X and Z. The script builds:

* **Table II, weak triply even**, all fifteen codes. Start from one qubit and
  double with the `[[7,1,3]]` Steane code, the `[[17,1,5]]` color code and the
  `[[23,1,7]]` Golay code, which gives `[[15,1,3]]`, `[[49,1,5]]` and
  `[[95,1,7]]`. Then double twice each with the doubly even quantum
  quadratic-residue codes of length 47, 79, 103, 167, 191 and 199, which gives
  `[[189,1,9]]` up to `[[3239,1,31]]`. A QR code of prime length `p ≡ −1 mod 8`
  is spanned by the cyclic shifts of `Σ_{r residue} x^r`, and its extension
  `[p+1, (p+1)/2]` is doubly even and self-dual. The paper's Theorem 3.1
  carries a partition `M+ | M−` of the qubits through each doubling, such that
  `T` on `M+` and `T†` on `M−` is the logical `T^7`. The script builds the
  partition, and the tests check it.
* **Table I, triorthogonal**, all fifteen codes. They share `[[15,1,3]]`,
  `[[49,1,5]]` and `[[95,1,7]]` with Table II. Then come, in order:
  * `[[185,1,9]]`, from the `[[45,1,9]]` code of a self-dual `[46,23,10]`
    code;
  * `[[279,1,11]]`, from `[[47,1,11]]`;
  * `[[417,1,13]]`, from a `[[69,1,13]]` code (see below);
  * `[[575,1,15]]`, from `[[79,1,15]]`;
  * `[[777,1,17]]`, from the `[[101,1,17]]` code of a self-dual `[102,51,18]`
    code;
  * `[[983,1,19]]`, from `[[103,1,19]]`;
  * two codes each from the QR codes of length 167, 191 and 199, up to
    `[[3211,1,31]]`.

  The `[46,23,10]` and `[102,51,18]` codes are subtractions of the extended QR
  codes `[48,24,12]` and `[104,52,20]`: keep the words that agree on two
  coordinates, then delete both. Gaborit's tables of self-dual codes list them
  as `sub(XQ47)` and `sub(XQ103)`. Each is unique up to equivalence, because
  `PSL(2,p)` is 2-transitive on the `p + 1` coordinates.

**The `[[17,1,5]]` code.** The paper uses the 4.8.8 color code of Bombin and
Martin-Delgado. `COLOR17` in the script is a basis of its stabiliser group: one
weight-8 and seven weight-4 generators, overlapping pairwise in 0 or 2 qubits.
A doubly even `[[17,1,5]]` code is unique up to qubit permutation. With its
parity bit appended it is a self-dual `[18,9,4]` code with 17 words of weight
4, all missing the parity bit. That makes it `d10 + e7 + f1`, punctured at
`f1`: the one self-dual code of length 18 with a coordinate that no weight-4
word covers. The tests check each of these properties.

**The `[[69,1,13]]` code.** The paper takes it from a `[70,35,14]` code, and
`[[417,1,13]]` and the nine codes doubled from it depend on it. The code the
paper cites (Gulliver and Harada, 1998) is *formally* self-dual: it has the
weight enumerator of a self-dual code, but it is not equal to its dual, so the
puncture-and-dualise map does not apply to it. No self-dual `[70,35,14]` code
is known; the best known self-dual codes of length 70 have distance 12.

A `[[69,1,13]]` needs less than distance 14. Puncturing a self-dual `[70,35]`
code at a coordinate `p` gives distance one less than the lightest word through
`p`. So it is enough that every word through one coordinate weighs at least 14.
Lighter words that miss that coordinate do no harm.
[`search_sd70.py`](search_sd70.py) searches every self-dual `[70,35]` code
with an automorphism of order 23 that has three 23-cycles and one fixed point.
By Huffman–Yorgov theory these are 386 codes up to equivalence. It enumerates
every word of weight 12 or less in each one exactly. Exactly one code
qualifies, and only at the fixed point: a `[70,35,12]` code whose 368
lightest words all miss it. `build_codes.py` builds it from three polynomials
(`SD70_U`). The tests prove the property a second, independent way: they
enumerate all `2^34` words through the fixed point using the code's algebraic
structure, and the lightest weighs exactly 14. So the code gives `[[69,1,13]]`
exactly, and the ten codes come out with the paper's parameters. Each of their
rows and records notes where this input comes from.

(Two other families cannot work. A pure double-circulant code would need
distance 14 outright, because every nonzero word touches both circulant
halves and its shifts move each half transitively. A bordered double-circulant
self-dual code of length 70 does not exist. The subtraction of the `[72,36,12]`
QR code has distance 10, and its light words touch every coordinate.)

The paper's transversal-Clifford codes (its doubly even `[[n,1,d]]` codes) are
not built: they are not `T` factories, and the catalogue holds level-3
factories only.

## Checks

`build_codes.py` checks every code before writing anything:

* the logical row covers every qubit;
* the rows are independent and the columns distinct;
* the logical row has odd weight and every stabiliser even weight;
* the matrix is triorthogonal (every pair and triple of rows overlaps
  evenly);
* the fault built below has zero syndrome and flips the logical, with the
  paper's weight;
* in Table II, `T` on `M+` and `T†` on `M−` leaves every stabiliser alone and
  acts as `T^m` on the logical.

The tests re-check all of this with the master catalogue's own primitives,
[`faultcore`](../master_catalog/faultcore.py) and
[`clifford`](../master_catalog/clifford.py), which share no code with the
script. They also compute the distances of the small self-dual inputs
(`[[7,1,3]]`, `[[17,1,5]]`, `[[23,1,7]]`, `[[45,1,9]]` and `[[47,1,11]]`) and
the minimum distance of the `[46,23]` code, by enumerating every codeword. And
they prove the `[70,35,12]` code's property, as above.

## Distances

In both chains every doubling's distance is `d_tri + 2`. So two qubits of the
self-dual blocks, one in each copy, plus the smaller code's own fault, make a
harmful fault of exactly the paper's distance. The script builds each code's
fault that way, starting from `{0}` on the one-qubit code. The lower bound is
the paper's theorem: `d ≥ min(d_sd, d_tri + 2)`, where `d_sd` is at least the
classical distance less one. For the codes doubled from `[[69,1,13]]`, that
input's distance is the one proved here.

The theorem needs the distance of every self-dual input along a code's chain.
This folder proves them for every input up to length 103: by enumerating
every word for the small inputs, `[[45,1,9]]`, `[[47,1,11]]` and Gong's two
codes, through the code's structure for `[[69,1,13]]`, and by the
Brouwer–Zimmermann bound of [`min_distance.py`](min_distance.py) for
`[[79,1,15]]`, `[[101,1,17]]` and `[[103,1,19]]` (the extended QR codes
`[80,40]` and `[104,52]` and `sub(XQ103)` have distance at least 14, 18 and 18,
so 16, 20 and 18 since their weights are multiples of 4, 4 and 2).
[`certify_distances.py`](certify_distances.py) applies the theorem along each
chain and writes [`distance_certificates.json`](distance_certificates.json),
one record per code, bound to its circuit by the SHA-256 of the columns.

The quantum QR codes of length 167, 191 and 199 rest on the minimum distances
24, 28 and 32 of the extended QR codes of length 168, 192 and 200, as the
paper's Table II states them. The first is proved here: [`bz_bound.c`](bz_bound.c),
the Brouwer–Zimmermann bound in C, listed every word of `[168,84]` with at
most 10 ones on one information set and 9 on the other, `3.6·10^12` sums of
rows, and the lightest weighs 24. A word it did not list weighs at least
11 + 10 = 21, and the code is doubly even, so its minimum distance is 24
([`xqr168_distance.json`](xqr168_distance.json), checked by
`test_the_168_bit_qr_code_has_distance_24`, which also confirms the record is
of this code, by this program, on the information sets the seeded choice
gives). The other two are not re-proved: the same bound would need about
`8·10^14` and `6·10^16` sums of rows. The owner decided on 2026-11-07 to count
the Table II distances as sure. So the 18 codes from `[[1301,1,21]]` on have
records: the six that double only the length-167 code (`[[1301,1,21]]` to
`[[1679,1,23]]`) under the file's tool, every input proved here, and the
twelve from `[[2017,1,25]]` on, whose chains double a QR code of length 191
or 199, under their own tool ("...,
with the extended QR distances of their Table II (not re-proved here)"). Each
such record lists the Table II distances it takes in `rests_on_paper` and
what this folder proves for it in `proved_here`: the theorem, the code's
structure and fault, and every other input distance along its chain. The
same sentence ends the row's `d_certified_source`.

The catalogue's own fault sweep proves only a floor above `n = 95`. Since
2026-11-07 the theorem's bound is the row's distance wherever the file
certifies it: the row is exact at the paper's distance, keeps the sweep's
floor in `d_sweep_floor`, cites the file in `d_certified_evidence`, and was
relabelled, keeping its old label in `former_labels`. On most of the rows up
to `n = 599` tropidist computes the same value, a second proof. The 18 codes
from `[[1301,1,21]]` on were relabelled by
[`doubled_qr_distances_2026_11_07.py`](../master_catalog/migrations/doubled_qr_distances_2026_11_07.py),
`2017.1.3.a` to `2017.1.25.a` among them. Every row stores a fault of the
paper's weight as `d_upper` and `d_witness`, and the verifier re-checks it
against the true syndromes.

| code | paper | catalogue row | `d` | sweep proves | how `d` is proved | credit |
|---|---|---|---|---|---|---|
| `[[15,1,3]]` | I, II | `15.1.3.a` (held) | `d = 3` | `d = 3` | sweep | Bravyi & Kitaev (2005) |
| `[[49,1,5]]` | I, II | `49.1.5.a` (held) | `d = 5` | `d = 5` | sweep | Bravyi & Haah (2012) |
| `[[95,1,7]]` | I, II | `95.1.7.a` | `d = 7` | `d = 7` | sweep | Sullivan (2024) |
| `[[185,1,9]]` | I | `185.1.9.a` (was `185.1.7.a`) | `d = 9` | `d ≥ 7` | theorem and exhaustive search | Jain & Albert |
| `[[189,1,9]]` | II | `189.1.9.a` (was `189.1.7.a`) | `d = 9` | `d ≥ 7` | theorem and exhaustive search | Jain & Albert |
| `[[279,1,11]]` | I | `279.1.11.a` (was `279.1.7.a`) | `d = 11` | `d ≥ 7` | theorem and exhaustive search | Jain & Albert |
| `[[283,1,11]]` | II | `283.1.11.a` (was `283.1.7.a`) | `d = 11` | `d ≥ 7` | theorem and exhaustive search | Jain & Albert |
| `[[417,1,13]]` | I | `417.1.13.a` (was `417.1.6.a`) | `d = 13` | `d ≥ 6` | theorem and exhaustive search | Jain & Albert |
| `[[441,1,13]]` | II | `441.1.13.a` (was `441.1.6.a`) | `d = 13` | `d ≥ 6` | theorem and exhaustive search | Jain & Albert |
| `[[575,1,15]]` | I | `575.1.15.a` (was `575.1.6.a`) | `d = 15` | `d ≥ 6` | theorem and exhaustive search | Jain & Albert |
| `[[599,1,15]]` | II | `599.1.15.a` (was `599.1.6.a`) | `d = 15` | `d ≥ 6` | theorem | Jain & Albert |
| `[[777,1,17]]` | I | `777.1.17.a` (was `777.1.6.a`) | `d = 17` | `d ≥ 6` | theorem | Jain & Albert |
| `[[805,1,17]]` | II | `805.1.17.a` (was `805.1.6.a`) | `d = 17` | `d ≥ 6` | theorem | Jain & Albert |
| `[[983,1,19]]` | I | `983.1.19.a` (was `983.1.6.a`) | `d = 19` | `d ≥ 6` | theorem | Jain & Albert |
| `[[1011,1,19]]` | II | `1011.1.19.a` (was `1011.1.6.a`) | `d = 19` | `d ≥ 6` | theorem | Jain & Albert |
| `[[1317,1,21]]` | I | `1317.1.21.a` (was `1317.1.3.a`) | `d = 21` | `d ≥ 3` | theorem | Jain & Albert |
| `[[1345,1,21]]` | II | `1345.1.21.a` (was `1345.1.3.a`) | `d = 21` | `d ≥ 3` | theorem | Jain & Albert |
| `[[1651,1,23]]` | I | `1651.1.23.a` (was `1651.1.3.a`) | `d = 23` | `d ≥ 3` | theorem | Jain & Albert |
| `[[1679,1,23]]` | II | `1679.1.23.a` (was `1679.1.3.a`) | `d = 23` | `d ≥ 3` | theorem | Jain & Albert |
| `[[2033,1,25]]` | I | `2033.1.25.a` (was `2033.1.3.a`) | `d = 25` | `d ≥ 3` | theorem, with Table II's QR distances | Jain & Albert |
| `[[2061,1,25]]` | II | `2061.1.25.a` (was `2061.1.3.a`) | `d = 25` | `d ≥ 3` | theorem, with Table II's QR distances | Jain & Albert |
| `[[2415,1,27]]` | I | `2415.1.27.a` (was `2415.1.3.a`) | `d = 27` | `d ≥ 3` | theorem, with Table II's QR distances | Jain & Albert |
| `[[2443,1,27]]` | II | `2443.1.27.a` (was `2443.1.3.a`) | `d = 27` | `d ≥ 3` | theorem, with Table II's QR distances | Jain & Albert |
| `[[2813,1,29]]` | I | `2813.1.29.a` (was `2813.1.3.a`) | `d = 29` | `d ≥ 3` | theorem, with Table II's QR distances | Jain & Albert |
| `[[2841,1,29]]` | II | `2841.1.29.a` (was `2841.1.3.a`) | `d = 29` | `d ≥ 3` | theorem, with Table II's QR distances | Jain & Albert |
| `[[3211,1,31]]` | I | `3211.1.31.a` (was `3211.1.3.a`) | `d = 31` | `d ≥ 3` | theorem, with Table II's QR distances | Jain & Albert |
| `[[3239,1,31]]` | II | `3239.1.31.a` (was `3239.1.3.a`) | `d = 31` | `d ≥ 3` | theorem, with Table II's QR distances | Jain & Albert |

A catalogue label carries the row's distance. That is why `[[1011,1,19]]` is
`1011.1.19.a` and `[[3239,1,31]]` is `3239.1.31.a`. A former label still
resolves on the website.

## Credit

A class is credited to its earliest publication alone.

* The `[[15,1,3]]` and `[[49,1,5]]` codes are classes the catalogue already
  held with smaller circuits. Their records name no citation, so the merge
  left those rows, and their credit, as they were.
* `[[95,1,7]]` is credited to M. Sullivan, “Code conversion with the quantum
  Golay code for a universal transversal gate set,” Phys. Rev. A 109, 042416
  (2024), which built it first by the same doubling. The paper credits it the
  same way.
* Every other code is credited to Jain and Albert.

The rows' regimes are `Jain-Albert doubling: weak triply even family` (Table
II) and `Jain-Albert doubling: triorthogonal family` (Table I). Their discovery
tag is `pre-existing`.

## Clifford corrections

With every qubit a `T`, each of these codes needs a Clifford correction, like
most of the catalogue. The catalogue stores it with each row: `S` powers and
`CZ`s on the wires, applied after the rotations. None of the 27 codes needs a
Clifford gate if its qubits may run at other powers of `T`:

* **Table II.** `T` on `M+` and `T†` on `M−`, the paper's own partition,
  gives the logical `T⁷ = T†`. Scaled to the logical `T`, it is `T†` on `M+`
  and `T` on `M−`, and that is what each row stores as `rotation_powers`.
* **Table I.** `[[185,1,9]]` is the logical `T` with `T` on 157 qubits and
  `T³ = T·S` on 28. `[[279,1,11]]` is the logical `T` with `T`, `T³` and `T†`.
  The ten codes from `[[417,1,13]]` on use `T`, `T³`, `T⁵` and `T†`. The
  catalogue's solver found all of these powers.

The paper says the Table I codes need extra `S` and `CZ` gates. That is true
when every qubit runs a `T`. It is not needed once a qubit may run any `T^j`,
which is how the paper's own Sec. II defines a transversal `T` gate. The
catalogue's verifier checks both statements. It evaluates the phase of the
code at the stored powers on every input of weight at most 3, which is
complete for a phase polynomial of degree 3, and finds the logical `T` with
every stabiliser left alone.

## Gong's codes

A. Gong, in a note in her repository
[`gongaa/RM127`](https://github.com/gongaa/RM127/tree/main/triply-even)
(“On some K=1 codes admitting strongly transversal T”, 2025), found two doubly
even self-dual CSS codes, `[[41,1,9]]` and `[[65,1,13]]`, and used them in the
same doubling:

| code | doubled from |
|---|---|
| `[[177,1,9]]` | her `[[41,1,9]]` onto `[[95,1,7]]` |
| `[[271,1,11]]` | the `[[47,1,11]]` quantum QR code onto `[[177,1,9]]` |
| `[[401,1,13]]` | her `[[65,1,13]]` onto `[[271,1,11]]` |
| `[[559,1,15]]` | the `[[79,1,15]]` quantum QR code onto `[[401,1,13]]` |

Each is shorter than the paper's code of the same distance: 185, 279, 417 and
575 qubits in Table I, 189, 283, 441 and 599 in Table II. Every input is doubly
even, so every X stabiliser weighs 0 mod 8 and `T` on every qubit is the
logical `T^m` with `m = n mod 8`: `T` for 177 and 401 qubits, `T†` for 271
and 559, and never an `S` or `CZ`. The rows store no powers for the first two and
`T†` on every qubit for the other two.

Her two self-dual codes are copied, as lists of qubit indices, into
[`gong_self_dual_codes.json`](gong_self_dual_codes.json) from her
`triply-even/41_XZ.mtx` and `65_XZ.mtx` (commit `b425fd5`, MIT licence; see
[`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md)). `build_codes.py` doubles
them onto its own `[[95,1,7]]`, with the quantum QR codes it already builds.
The doubling theorem gives `d >= min(d_sd, d_tri + 2)`, so it needs her codes'
distances. The tests prove them by enumerating every word of each stabiliser
space `S`, 2^20 and 2^32 words. A doubly even self-dual `[[n,1]]` code has
distance `n` minus the largest weight in `S`, and the largest weights are 32
and 52, so the distances are exactly 9 and 13.

Built from her own `[[95,1,7]]` matrix, this doubling gives exactly her
`[[177,1,9]]` stabilisers. Her larger matrices are built with her own QR-code
matrices, so they are not identical to these, though the construction and
parameters are the same. The four codes are credited to her note (`gong2025triply`), with
regime `Gong doubling: triply even family`, and came in through
[`gong_triply_even_2026_10_30.py`](../master_catalog/migrations/gong_triply_even_2026_10_30.py).

Her chain stops at distance 15. `build_codes.py` continues it with the
self-dual inputs Table I uses from distance 17 on, the paper's method applied
to her codes:

| code | doubled from | Table I code |
|---|---|---|
| `[[761,1,17]]` | the `[[101,1,17]]` code of sub(XQ103) onto `[[559,1,15]]` | `[[777,1,17]]` |
| `[[967,1,19]]` | the `[[103,1,19]]` quantum QR code onto `[[761,1,17]]` | `[[983,1,19]]` |
| `[[1301,1,21]]` | the `[[167,1,23]]` quantum QR code onto `[[967,1,19]]` | `[[1317,1,21]]` |
| `[[1635,1,23]]` | the same onto `[[1301,1,21]]` | `[[1651,1,23]]` |
| `[[2017,1,25]]` | the `[[191,1,27]]` quantum QR code onto `[[1635,1,23]]` | `[[2033,1,25]]` |
| `[[2399,1,27]]` | the same onto `[[2017,1,25]]` | `[[2415,1,27]]` |
| `[[2797,1,29]]` | the `[[199,1,31]]` quantum QR code onto `[[2399,1,27]]` | `[[2813,1,29]]` |
| `[[3195,1,31]]` | the same onto `[[2797,1,29]]` | `[[3211,1,31]]` |

Each is 16 qubits shorter than the Table I code. The `[[101,1,17]]` input is
not doubly even, so these codes are not triply even. Like Table I, each needs
no `S` or `CZ` once some qubits run `T³`, `T⁵` or `T†`, which the catalogue's
solver found. Their labels are `GJ-761` to `GJ-3195` and their regime is
`Jain-Albert doubling of Gong's codes`. Each row cites both the paper and her
note, and its regime description and source say how it was built. They came in
through
[`gong_doubled_2026_10_30.py`](../master_catalog/migrations/gong_doubled_2026_10_30.py).

Her four codes are the rows `177.1.9.a`, `271.1.11.a`, `401.1.13.a` and
`559.1.15.a`, at the certified distance. The eight doubled on are too:
`761.1.17.a` and `967.1.19.a` with every input proved here, and the six from
`[[1301,1,21]]` on (`1301.1.21.a` to `3195.1.31.a`): `1301.1.21.a` and
`1635.1.23.a` with every input proved here, the four from `2017.1.25.a` on
with the Table II distances of the QR codes of length 192 and 200.

## Reproduce

```bash
.venv/bin/python transversal_t_codes/search_sd70.py      # finds the [70,35,12] code, ~2 min on 16 cores
.venv/bin/python transversal_t_codes/build_codes.py --check
.venv/bin/python -m unittest discover -s transversal_t_codes/tests
.venv/bin/python master_catalog/migrations/transversal_t_codes_table1_2026_10_10.py --dry-run
```

The search prints the one usable code and the polynomials `SD70_U` it is built
from. The migration is a no-op on the shipped catalogue, because every code is
held. The first import,
[`transversal_t_codes_2026_10_10.py`](../master_catalog/migrations/transversal_t_codes_2026_10_10.py),
merged seventeen codes. The second,
[`transversal_t_codes_table1_2026_10_10.py`](../master_catalog/migrations/transversal_t_codes_table1_2026_10_10.py),
merged the ten Table I codes that depend on `[[69,1,13]]`. The third,
[`gong_triply_even_2026_10_30.py`](../master_catalog/migrations/gong_triply_even_2026_10_30.py),
merged Gong's four codes, and the fourth,
[`gong_doubled_2026_10_30.py`](../master_catalog/migrations/gong_doubled_2026_10_30.py),
the eight doubled on from them.
