# Borrowed Identities: distance-2 factories at every Clifford level

This folder imports the factory catalogue of

> S. Singh, C. Gidney and C. Jones, **"Borrowed Identities: Malleable
> Distillation Factories and a Unified Numerical Search,"**
> [arXiv:2606.28518](https://arxiv.org/abs/2606.28518) (2026),

from its code and data repository,
[`shraggy/Magic_state_factory_search`](https://github.com/shraggy/Magic_state_factory_search)
(S. Singh), at commit `cae49828ed9ab9c1079c7cdf66c5bd337b027515`. The searches,
the theory and every factory listed here are theirs. **If you use these circuits,
cite the paper.** If you use the code, cite the repository too:

```bibtex
@misc{singh2026borrowed,
  title         = {Borrowed Identities: Malleable Distillation Factories and a Unified Numerical Search},
  author        = {Singh, Shraddha and Gidney, Craig and Jones, Cody},
  year          = {2026},
  eprint        = {2606.28518},
  archiveprefix = {arXiv},
  primaryclass  = {quant-ph},
  doi           = {10.48550/arXiv.2606.28518}
}
@misc{singh2026search,
  title        = {Magic State Factory Search},
  author       = {Singh, Shraddha},
  year         = {2026},
  howpublished = {\url{https://github.com/shraggy/Magic_state_factory_search}},
  note         = {Code and data for arXiv:2606.28518; commit cae4982}
}
```

What this repository adds is bookkeeping. It rebuilds an explicit circuit for every
row, re-checks each one, and merges the level-3 circuits into the
[master catalogue](../master_catalog/), credited to the paper.

## What the upstream catalogue is

The paper's borrowed-identity condition asks only that a circuit of parity
rotations act as the identity on `|+>^n`. Removing the gates that touch only the
output qubits then leaves those qubits in a magic state, and every remaining gate
touches a check, so every single fault is detected: distance 2. The condition is
written for any level `l` of the Clifford hierarchy, with rotation angle
`pi/2^l`. Level 2 distils `S`-type states, level 3 `T`, `CS` and `CCZ`, and
level 4 `sqrt(T)` up to `CCCZ`.

Two searches produced the catalogue:

- **two-group**: circuits symmetric within the output block and within the check
  block, swept over `l = 2, 3, 4`, `k <= 7`, `n <= 11` circuit qubits and skip
  parameters `s_total, s_O <= 7`;
- **symmetry-free**: a chosen output block structure, with the check couplings
  solved for directly. It reaches mixed outputs such as one `CCZ` and one `CS`
  from one factory.

Their catalogue keeps one row per `(N, k, decomposition)`:

| level | rows | circuits rebuilt here |
|---|---:|---:|
| `l = 2` | 208 | 211 |
| `l = 3` | 182 | 185 |
| `l = 4` | 149 | 153 |

A row both searches found gets both circuits, which is why there are more
circuits than rows. The upstream
[`outputs/README.md`](upstream/outputs/README.md) describes the columns.
**Notation:** the paper writes `[[N, k, d]]` with `N` the number of input magic
states and `n` the number of circuit qubits. The master catalogue uses the
opposite letters: `n` inputs (columns) and `N` wires.

## Files

| path | what it is |
|---|---|
| [`upstream/`](upstream/) | a **byte-identical** copy of the upstream code, catalogues and READMEs (16 files, SHA-256 pinned in [`tests/`](tests/)) |
| [`export_circuits.py`](export_circuits.py) | rebuilds every row's circuit by running the upstream code on the row's parameters, checks it, measures its distance, and writes `circuits/` |
| [`circuits/circuits_l{2,3,4}.json`](circuits/) | one entry per circuit: the gates with their coefficients, the parameters that build it, the upstream row, and the measured distance with a witness |
| [`circuits/factories_l3.json`](circuits/factories_l3.json) | the level-3 circuits in the master catalogue's merge format, with regime, provenance and citations |
| [`tests/`](tests/) | the checks listed under [Verification](#verification) |

The copy in `upstream/` is the two searches
(`searches/Two_group.py`, `searches/symfree_search.py`), the
closed-form distance check (`searches/distance_check.py`), the classifier and
circuit exporter (`classification/`), the three catalogues
(`outputs/factory_catalogue_l{2,3,4}.csv`) and the four READMEs. The notebooks,
figures and raw sweep logs are not copied; they are in the upstream repository.

## How the circuits are rebuilt

`export_circuits.py` imports the upstream modules unmodified and, for each row:

- **two-group** (`n`, `s_total`, `s_O` given): `Two_group.build_gate_set`, the first
  valid sign assignment from `Two_group.find_valid_signs`, then removal of the
  output-only gate types. This is what `upstream/classification/export_circuit.py`
  does.
- **symmetry-free** (`parts` given): `symfree_search.solve_binding(parts, n - k, l)`.
- **both searches** (only the two-group parameters are printed): the symmetry-free
  circuit is rebuilt as `symfree_search.search` finds it. The output blocks are
  read off the row's `decomposition`, and the check register is the smallest one
  whose solution has distance 2 and a non-Clifford output.

A gate is stored as `[support, c]`. It is the paper's parity phase gate at angle
`c·pi/2^l`, which applies the phase `exp(2πi c/2^l)` to basis states of odd
parity on `support`, with `c` taken modulo `2^l`. Gates with odd `c` consume a
level-`l` magic state. `N` counts them. Gates with even `c` are lower-level
rotations, which the paper counts as free. Only the symmetry-free circuits have
them.

## Verification

Each circuit is checked before it is written, by code independent of the search
that built it:

- **its row**: the number of odd-`c` gates is the row's `N`, and the wire count
  is the row's `n`;
- **the borrowed-identity condition**: no monomial that touches a check wire
  carries genuine level-`l` phase;
- **the distance**: measured over the odd-`c` gates with the master catalogue's
  fault search ([`../master_catalog/faultcore.py`](../master_catalog/faultcore.py)).
  Every lighter fault is shown to be harmless, and an undetectable damaging fault
  of weight `d` is stored as the witness.

[`tests/`](tests/) re-checks the condition with a separate phase computation,
re-checks every witness, re-proves the absence below `d` by brute force on every
circuit with at most 40 magic gates, and pins the upstream files' hashes.
`export_circuits.py --check` rebuilds everything from the upstream code (about
half a minute) and fails if a committed file differs.

### Ten upstream distances are too high

The 508 rows printed at distance 2, and the 21 printed at distance 3, agree with
the measurement. Ten single-output rows print `d = 5` or `d = 7`, but each of
their circuits has distance exactly 3.

| level | upstream row | `[[N, k]]` (paper's notation) | printed `d` | measured `d` |
|---|---:|---|---:|---:|
| 2 | 5 | `[[15, 1]]` | 7 | 3 |
| 2 | 6 | `[[27, 1]]` | 5 | 3 |
| 2 | 11 | `[[63, 1]]` | 5 | 3 |
| 2 | 14 | `[[135, 1]]` | 5 | 3 |
| 2 | 17 | `[[271, 1]]` | 5 | 3 |
| 2 | 20 | `[[527, 1]]` | 5 | 3 |
| 3 | 9 | `[[135, 1]]` | 5 | 3 |
| 3 | 12 | `[[271, 1]]` | 5 | 3 |
| 3 | 15 | `[[527, 1]]` | 5 | 3 |
| 4 | 11 | `[[527, 1]]` | 5 | 3 |

In each, three gates cancel on every check and leave `Z` on the output: for
the level-3 `[[135, 1]]`, gates on qubits `{1}`, `{1,2,3,4,5}` and
`{0,2,3,4,5}`. This agrees with the paper itself, which says the distance of
these symmetric circuits saturates at 3 (its Sec. a and App. B). The circuits
store both values, `d` and `d_upstream`. The level-3 records carry no distance
claim for these three rows, and the master catalogue holds them at `d = 3`.

## What the master catalogue holds

The master catalogue is level 3 only, since its columns are `T` injections, so
the 185 level-3 circuits are merged. Levels 2 and 4 stay in this folder, with
explicit, verified circuits, for anyone who needs them.

A level-3 circuit becomes a catalogue record by keeping its odd-`c` gates as the
columns, outputs `0..k-1`. At level 3 the signs (`c = 1, 3, 5, 7`) and the
even-`c` rotations change the deposited state only by Clifford gates, which the
catalogue counts as free corrections, so the gate and the distance are
unchanged. Then [`../master_catalog/migrations/distance_two_2026_10_07.py`](../master_catalog/migrations/distance_two_2026_10_07.py)
opened the catalogue to distance 2 and merged them with the same verifier as
every other row:

| verdict | circuits | |
|---|---:|---|
| new class | 179 | 171 at `d = 2` and 8 at `d = 3` (`63`, `127`, `135`, `255`, `271`, `511`, `527` and `1023` inputs, one `T` output) |
| already held | 5 | `15.1.3.a` and `31.1.3.a`, and the symmetry-free twins of `8.3.2.a`, `12.2.2.a` and `14.2.2.a` |
| refused | 1 | the paper's `[[8, 4, 2]]`: its fourth output equals a combination of the other three modulo the checks, a pseudo-output in the catalogue's terms. The paper keeps it on purpose, for the correlated errors the extra qubit detects (its note [45]); the catalogue's one-fault-per-column model does not count those |

The same migration also merged the 19 distance-2 rows of this repository's own
[symmetry-SAT catalogue](../symmetry_sat_search/catalog/). Before, the `d ≥ 3`
floor kept them out. Ten are new classes and seven repeat a Borrowed Identities
class. The other two are not admitted as circuits (a redundant check wire, an
idle wire), but their classes are held through the Borrowed Identities
`[[12, 3, 2]]` circuits.

Every imported row has the regime `borrowed-identity search: two-group` or
`borrowed-identity search: symmetry-free`, `discovery: pre-existing`, and a
`sources` entry naming its circuit id in `circuits/circuits_l3.json`, the
upstream repository, the commit and the CSV row. The factory pages on the
[website](https://shubhamj810.github.io/magic-state-factory-repo/search.html?d=2)
show the same.

### Credit

Every class these searches found is credited to the paper. Where an earlier
work published the same class (same inputs, outputs, distance and output gate up
to a CNOT frame), that work is credited first:

| class | credited to | where |
|---|---|---|
| `14.2.2.a`, `20.4.2.a`, `26.6.2.a` (`T^⊗k`) | Bravyi & Haah (2012), then the paper | the `k = 2, 4, 6` members of the `[[3k+8, k, 2]]` family (paper, App. F.3a) |
| `8.3.2.a` (`CCZ`) | Eastin (2013), Jones (2013), then the paper | the 8 `T` → `CCZ` factory |
| `12.2.2.a` (`CS`) | Webster, Quintavalle & Bartlett (2023), then the paper | the paper's ref. [33] |
| `14.6.2.a` (`CCZ⊗CCZ`) | Campbell & Howard (2017), then the paper | their Example IV.2, the `N = 2` member of their `6N + 2` Toffoli family |
| `18.4.2.b` (`CS⊗CS`) | Campbell & Howard (2017), then the paper | their Example IV.3: 18 `T` states for two `CS` gates, output error `45ε²` |
| `15.1.3.a` (`T`) | Bravyi & Kitaev (2005) alone | unchanged. A Pareto point of the length-54 classification already credited to its publication, which the paper recovers |
| `31.1.3.a` (`T`) | the length-54 classification and the symmetry-and-AI report, then the paper | an existing class within the classification window, where a published work stating a class is credited too |

Two of these attributions go beyond the paper's own reference list:

- **The Jones paper for the 8-`T` Toffoli factory** is *Novel constructions for
  the fault-tolerant Toffoli gate*, Phys. Rev. A 87, 022328 (2013),
  arXiv:1212.5069. That is the paper Eastin's and Campbell–Howard's papers cite
  for it. The Borrowed Identities paper's ref. [48] points instead to Jones's
  later composite-Toffoli paper (Phys. Rev. A 87, 052334), which uses 64 `T`
  gates.
- **`[[18, 4, 2]]`.** The paper presents it as the first new member of its
  `T`-to-`CS` family `[[6m+6, 2m, 2]]`. Campbell and Howard's Example IV.3
  already prints an 18-`T`-state, distance-2 protocol for two `CS` gates, the
  same class, so they are credited too. For three `CS` gates their general count
  (their Eq. 121, `7N + 5` for odd `N`) is 26 inputs, so `[[24, 6, 2]]`
  (`m = 3`) is credited to the paper alone.

Separately, Campbell and Howard's Example IV.4 (12 `T` states for two `CCZ`s
sharing a qubit, distance 2) is the class of the symmetry-SAT row `12.5.2.a`,
which is credited to them.

Nezami and Haah (2022) list distance-2 triorthogonal codes with `n + k ≤ 38`
only implicitly, as distances of descendants in their Table II. The ones they
name are the first three Bravyi–Haah codes, so, under the catalogue's rule of
crediting explicitly printed protocols, they add no credit here.

## Licence

The upstream repository states no licence. The files in `upstream/` are included
unchanged, with attribution, so that the catalogue's provenance resolves inside
this repository and the circuits can be rebuilt. They remain the work of their
authors and are not covered by any licence later chosen for this repository's own
code. See [`../THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md).

## Reproduce

From the repository root, with the environment in [`../requirements.txt`](../requirements.txt):

```bash
.venv/bin/python borrowed_identities/export_circuits.py --check      # rebuild from upstream, compare (~35 s)
.venv/bin/python -m unittest discover -s borrowed_identities/tests   # the checks above (~2 s)
.venv/bin/python master_catalog/migrations/distance_two_2026_10_07.py --dry-run   # the merge, written nowhere (seconds)
```
