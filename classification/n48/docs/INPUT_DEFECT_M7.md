# The length-48 table is missing two affine-rank-7 classes

`length48_catalogue.json` (status `complete_corrected_v2`, sha256
`f0615340…`) lists **96** representatives of intrinsic dimension `m = 7`.
An independent source lists **98**.

## The independent source

A no-repeated-column unital triorthogonal space of length 48 and affine rank 7
*is* a weight-48 word of the Reed–Muller code RM(3,7) whose support has full
affine rank, up to AGL(7,2).  The Gillot–Langevin orbit table behind
`../rank7_census` (`rank7_census/gillot_langevin.py`) enumerates **every**
AGL(7,2)-orbit of RM(3,7) — its class sizes sum to |AGL(7,2)| = 2⁶⁴, which the
census checks — so the weight-48, rank-7 classes can be read off:

```
weight 48 words of RM(3,7):   99 affine classes
   affine rank 7:             98      <- must equal the table's m = 7 sector
   affine rank 6:              1      (class 3470, a+abc; the table's m = 6 sector)
```

## The comparison

`reps48.rm37_crosscheck` computes a three-level AGL-invariant of each support
(`affine_signature`: the sorted derivative profile |S ∩ (S+a)|, the sorted
hyperplane profile, and the histogram of second derivatives) and matches the
two lists.  The invariant separates all 98 RM(3,7) classes and all 96 table
representatives, so the matching is one-to-one where it succeeds:

| length | table `m = 7` | RM(3,7) rank-7 classes | unmatched |
|---|---|---|---|
| 40 | 18 | 18 | none (`../n40`) |
| 42 | 0 | 0 | — |
| 44 | 35 | 35 | none |
| 46 | 0 | 0 | — |
| **48** | **96** | **98** | **classes 2164 and 2867 absent from the table** |

```
class 2164   c+ac+abc+d+ce+bde+df+abg+adg+afg          stabiliser order 32
class 2867   a+ab+bc+ad+abd+bce+cdf+aef+acg+deg+bfg    stabiliser order 64
```

Both are weight-48, affine-rank-7, unital triorthogonal (all pair and triple
overlaps of {1, x₁..x₇} on the support even) and indecomposable — exactly the
objects the table claims to list completely (`tests/test_n48.py::
test_missing_classes_are_genuine`).  No table representative fails to match an
RM(3,7) class, so the table has no spurious rows, only missing ones.

## What this directory does about it

```
                 length-48 table                    RM(3,7) orbit table
                 ┌───────────────┐                  ┌──────────────────┐
   m >= 8  ──────│ 28,776 reps   │── swept ──┐      │                  │
                 │ (every origin)│           │      │ 98 rank-7 classes│── swept (rm37_w48)
   m = 7   ──────│ 96 reps  ✗    │ NOT USED  ├──►   │ (one origin per  │   rank 7 at n = 47, 48
                 │               │           │      │  stabiliser orbit│   + the rank-8 lifts
   m = 6   ──────│ 1 rep         │── open ───┘      │  + lift)         │
                 └───────────────┘                  └──────────────────┘
```

* The **rank-7 sector at n = 47, 48** is taken from the RM(3,7) table
  (source `rm37_w48`), never from the length-48 table.  It is therefore
  *unconditional*: it does not depend on the table being right.
* The rank-8 lifts of the m = 7 words (n = 48, check rank 8) come from the
  same source, so the two missing classes contribute their lifts too.
* The **m ≥ 8 sector** cannot be checked against anything independent (no
  orbit table of RM(4,8) or beyond exists), so completeness at check rank ≥ 8
  is stated *relative to the table*.  A table that lost two rank-7 classes
  may have lost rank-≥8 classes as well; the catalogue says so.
* The same policy is applied at length 44 (source `rm37_w44`), where the
  table's m = 7 sector is actually correct, both for uniformity and because
  sweeping 35 classes at 128 origins each costs ten times what one origin per
  stabiliser orbit costs for the same classes and the same coefficients.

## Reproduce

```
python reps48.py            # validates the four tables and prints the cross-check
```

The two words in the table's own format (indicator polynomial, lexicographic support, 8 x 48 generator matrix): [`missing_m7_classes.txt`](missing_m7_classes.txt).

## Mechanism (from the table's own provenance fields)

Established from `length48_catalogue.json` and the RM(3,7) orbit table alone:

* The table's m = 7 branch is `reused_complete_rm37_coset_search_and_exact_affine_quotient`.
  Each m = 7 representative records the source entries it absorbed
  (`published_coset_source_lines`).  The 96 representatives absorb **98**
  source lines in total -- the correct number of rank-7 weight-48 orbits --
  and exactly two representatives absorb two lines each:

  | representative | source lines | RM(3,7) class it matches (by invariants) | stab |
  |---|---|---|---|
  | `length48_m7_class_0075` | 719, 723 | 2191 `abc+d+ce+bde+df+abg+adg+afg` | 32 |
  | `length48_m7_class_0065` | 749, 752 | 2933 `ab+abd+bce+cdf+aef+acg+deg+bfg` | 96 |

* The 96 representatives map injectively onto 96 of the 98 RM(3,7) classes by
  the three-level invariant of `reps48.affine_signature` (all 98 RM(3,7)
  classes have distinct signatures); the two unmatched are 2164 and 2867.
* Each missing class has **the same cubic part** as the representative that
  absorbed two lines, differing by a quadratic + linear term:
  2164 = 2191 + `c + ac`; 2867 = 2933 + `a + bc + ad`.
  2164 and 2191 share the derivative-weight profile and the hyperplane
  profile and are separated only by the second-derivative histogram;
  2867 and 2933 are separated already by the derivative profile.

Inference (not provable without the referenced but unshipped certificates
`outputs/m07_classification.json`, `corrected_v1/m06_m07_direct_search_reuse.json`):
the reading step saw all 98 orbits and the "exact affine quotient" step
identified 2164 with 2191 and 2867 with 2933 -- two false equivalences
between words in the same RM(2,7)-coset.  A quotient that really verified an
AGL(7,2) transporter for every merge could not have done this.

Ranks >= 8: the m >= 8 branches were generated by a different method
(`high_derivative_inverse_contraction` for m = 8..10, `zero_contraction_graph_lift`
for m = 11..14) whose input is not the m = 7 weight-48 list (a full-rank
weight-48 word at m = 8 has no weight-48 hyperplane section), so the two
missing classes do not propagate as data.  Whether the same quotient defect
recurs there cannot be decided from the file; the file does show that the
m >= 8 quotient split invariant buckets (m = 8: 9,845 buckets -> 9,868
classes; m = 9: 14,265 -> 14,293; m = 10: 3,887 -> 3,890), i.e. it did more
than bucket by invariants, and records independent pair audits at m = 9..14.
No such split count or audit is recorded for m = 7.
