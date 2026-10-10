# Transversal-T codes of Jain and Albert

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
| [`search_sd70.py`](search_sd70.py) | the exhaustive search that found the self-dual `[70,35,12]` code behind Table I's `[[69,1,13]]` (see below), ~2 minutes |
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

The catalogue's own fault sweep proves only a floor above `n = 95`. For each
of those rows the paper's distance is stored as a certificate,
`d_certified`, marked as a lower bound (`d_certified_is_exact: false`), with
the doubling theorem as its source. The fault of that weight is stored as
`d_upper` and `d_witness`, and the verifier re-checks it against the true
syndromes. Together they pin the distance.

| code | paper | catalogue row | proved here | certified | fault | credit |
|---|---|---|---|---|---|---|
| `[[15,1,3]]` | I, II | `15.1.3.a` (held) | `d = 3` | — | — | Bravyi & Kitaev (2005) |
| `[[49,1,5]]` | I, II | `49.1.5.a` (held) | `d = 5` | — | — | Bravyi & Haah (2012) |
| `[[95,1,7]]` | I, II | `95.1.7.a` | `d = 7` | — | 7 | Sullivan (2024) |
| `[[185,1,9]]` | I | `185.1.7.a` | `d ≥ 7` | `≥ 9` | 9 | Jain & Albert |
| `[[189,1,9]]` | II | `189.1.7.a` | `d ≥ 7` | `≥ 9` | 9 | Jain & Albert |
| `[[279,1,11]]` | I | `279.1.7.a` | `d ≥ 7` | `≥ 11` | 11 | Jain & Albert |
| `[[283,1,11]]` | II | `283.1.7.a` | `d ≥ 7` | `≥ 11` | 11 | Jain & Albert |
| `[[417,1,13]]` | I | `417.1.6.a` | `d ≥ 6` | `≥ 13` | 13 | Jain & Albert |
| `[[441,1,13]]` | II | `441.1.6.a` | `d ≥ 6` | `≥ 13` | 13 | Jain & Albert |
| `[[575,1,15]]` | I | `575.1.6.a` | `d ≥ 6` | `≥ 15` | 15 | Jain & Albert |
| `[[599,1,15]]` | II | `599.1.6.a` | `d ≥ 6` | `≥ 15` | 15 | Jain & Albert |
| `[[777,1,17]]` | I | `777.1.6.a` | `d ≥ 6` | `≥ 17` | 17 | Jain & Albert |
| `[[805,1,17]]` | II | `805.1.6.a` | `d ≥ 6` | `≥ 17` | 17 | Jain & Albert |
| `[[983,1,19]]` | I | `983.1.6.a` | `d ≥ 6` | `≥ 19` | 19 | Jain & Albert |
| `[[1011,1,19]]` | II | `1011.1.6.a` | `d ≥ 6` | `≥ 19` | 19 | Jain & Albert |
| `[[1317,1,21]]` | I | `1317.1.3.a` | `d ≥ 3` | `≥ 21` | 21 | Jain & Albert |
| `[[1345,1,21]]` | II | `1345.1.3.a` | `d ≥ 3` | `≥ 21` | 21 | Jain & Albert |
| `[[1651,1,23]]` | I | `1651.1.3.a` | `d ≥ 3` | `≥ 23` | 23 | Jain & Albert |
| `[[1679,1,23]]` | II | `1679.1.3.a` | `d ≥ 3` | `≥ 23` | 23 | Jain & Albert |
| `[[2033,1,25]]` | I | `2033.1.3.a` | `d ≥ 3` | `≥ 25` | 25 | Jain & Albert |
| `[[2061,1,25]]` | II | `2061.1.3.a` | `d ≥ 3` | `≥ 25` | 25 | Jain & Albert |
| `[[2415,1,27]]` | I | `2415.1.3.a` | `d ≥ 3` | `≥ 27` | 27 | Jain & Albert |
| `[[2443,1,27]]` | II | `2443.1.3.a` | `d ≥ 3` | `≥ 27` | 27 | Jain & Albert |
| `[[2813,1,29]]` | I | `2813.1.3.a` | `d ≥ 3` | `≥ 29` | 29 | Jain & Albert |
| `[[2841,1,29]]` | II | `2841.1.3.a` | `d ≥ 3` | `≥ 29` | 29 | Jain & Albert |
| `[[3211,1,31]]` | I | `3211.1.3.a` | `d ≥ 3` | `≥ 31` | 31 | Jain & Albert |
| `[[3239,1,31]]` | II | `3239.1.3.a` | `d ≥ 3` | `≥ 31` | 31 | Jain & Albert |

A catalogue label carries the distance proved here, as every label in the
catalogue does. That is why `[[3239,1,31]]` is `3239.1.3.a`.

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
merged the ten Table I codes that depend on `[[69,1,13]]`.
