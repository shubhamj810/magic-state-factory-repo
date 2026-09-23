# Factory catalogue

Generated and verified by [`../build_catalog.py`](../build_catalog.py) from
the curated explicit circuits in
[`../examples/found_factories.json`](../examples/found_factories.json).
Do not edit generated files by hand.

**These are verified search records, not classified maxima.** Absence from
this table is not a nonexistence result; exhaustive statements live in
[`../../classification/`](../../classification/).

**57 factories; every circuit passed parity, gate, and distance checks.**

## Summary

`T` is the exact minimal level-3 T-count; `deg` is the CNOT-frame-reduced
phase-polynomial degree. A stored `d=5` means no fault of weight at most
four was found, i.e. the certified lower bound `d>=5`.

| # | target | [[n,k,d]] | N | level | T | deg | provenance group |
|---:|---|---|---:|---:|---:|---:|---|
| 1 | T | [[14,1,2]] | 4 | 3 | 1 | 1 | analytic (level-3 simplex chain) |
| 2 | CS | [[12,2,2]] | 4 | 3 | 3 | 2 | analytic (level-3 simplex chain) |
| 3 | CCZ | [[8,3,2]] | 4 | 3 | 7 | 3 | analytic (level-3 simplex chain) |
| 4 | sqrt(T) | [[30,1,2]] | 5 | 4 | n/a | 1 | analytic (level-4 simplex chain) |
| 5 | CT | [[28,2,2]] | 5 | 4 | n/a | 2 | analytic (level-4 simplex chain) |
| 6 | CCS | [[24,3,2]] | 5 | 4 | n/a | 3 | analytic (level-4 simplex chain) |
| 7 | CCCZ | [[16,4,2]] | 5 | 4 | n/a | 4 | analytic (level-4 simplex chain) |
| 8 | S | [[6,1,2]] | 3 | 2 | 0 | 1 | analytic (level-2 simplex chain) |
| 9 | CZ | [[4,2,2]] | 3 | 2 | 0 | 2 | analytic (level-2 simplex chain) |
| 10 | CS | [[20,2,2]] | 6 | 3 | 3 | 2 | distance-2 level-3 (SAT search, explicit circuits) |
| 11 | T^2 | [[21,2,2]] | 6 | 3 | 2 | 1 | distance-2 level-3 (SAT search, explicit circuits) |
| 12 | T1_CS12 | [[25,2,2]] | 6 | 3 | 2 | 1 | distance-2 level-3 (SAT search, explicit circuits) |
| 13 | T3_CCZ123 | [[18,3,2]] | 6 | 3 | 6 | 2 | distance-2 level-3 (SAT search, explicit circuits) |
| 14 | CS12_CS13_CCZ123 | [[20,3,2]] | 6 | 3 | 3 | 2 | distance-2 level-3 (SAT search, explicit circuits) |
| 15 | T1_T2_T3_CS13_CS23 | [[24,3,2]] | 6 | 3 | 3 | 1 | distance-2 level-3 (SAT search, explicit circuits) |
| 16 | CS13_CS14_CS23_CCZ124_CCZ234 | [[18,4,2]] | 6 | 3 | 6 | 2 | distance-2 level-3 (SAT search, explicit circuits) |
| 17 | CS13_CS23_CS34_CCZ234 | [[20,4,2]] | 6 | 3 | 4 | 2 | distance-2 level-3 (SAT search, explicit circuits) |
| 18 | CCZ135_CCZ145_CCZ234_CCZ245 | [[12,5,2]] | 6 | 3 | 11 | 3 | distance-2 level-3 (SAT search, explicit circuits) |
| 19 | CCZ123_CCZ124_CCZ125 | [[16,5,2]] | 6 | 3 | 7 | 3 | distance-2 level-3 (SAT search, explicit circuits) |
| 20 | CCZ123_CCZ124_CCZ134_CCZ235 | [[20,5,2]] | 6 | 3 | 11 | 3 | distance-2 level-3 (SAT search, explicit circuits) |
| 21 | T | [[15,1,3]] | 5 | 3 | 1 | 1 | distance-3/4 slot-ansatz (CP-SAT, structural distance) |
| 22 | T | [[28,2,3]] | 9 | 3 | 2 | 1 | distance-3/4 slot-ansatz (CP-SAT, structural distance) |
| 23 | CS | [[35,2,3]] | 9 | 3 | 3 | 2 | distance-3/4 slot-ansatz (CP-SAT, structural distance) |
| 24 | T | [[35,3,3]] | 10 | 3 | 3 | 1 | distance-3/4 slot-ansatz (CP-SAT, structural distance) |
| 25 | T | [[64,1,4]] | 10 | 3 | 1 | 1 | distance-3/4 slot-ansatz (CP-SAT, structural distance) |
| 26 | T | [[141,2,4]] | 12 | 3 | 2 | 1 | distance-3/4 slot-ansatz (CP-SAT, structural distance) |
| 27 | CCZ | [[66,3,4]] | 12 | 3 | 7 | 3 | distance-3/4 slot-ansatz (CP-SAT, structural distance) |
| 28 | T | [[85,1,5]] | 11 | 3 | 1 | 1 | distance-3/4 slot-ansatz (CP-SAT, structural distance) |
| 29 | S | [[8,3,2]] | 5 | 2 | 0 | 1 | level-2 / level-4 exhaustive SAT (gap closures) |
| 30 | S | [[8,4,2]] | 6 | 2 | 0 | 1 | level-2 / level-4 exhaustive SAT (gap closures) |
| 31 | S | [[7,1,3]] | 4 | 2 | 0 | 1 | level-2 / level-4 exhaustive SAT (gap closures) |
| 32 | S | [[15,2,3]] | 6 | 2 | 0 | 1 | level-2 / level-4 exhaustive SAT (gap closures) |
| 33 | CZ | [[15,2,3]] | 6 | 2 | 0 | 2 | level-2 / level-4 exhaustive SAT (gap closures) |
| 34 | S | [[20,1,4]] | 7 | 2 | 0 | 1 | level-2 / level-4 exhaustive SAT (gap closures) |
| 35 | CZ | [[16,2,4]] | 7 | 2 | 0 | 2 | level-2 / level-4 exhaustive SAT (gap closures) |
| 36 | T^2 | [[14,2,2]] | 5 | 3 | 2 | 1 | level-3 general-target exhaustive SAT (gap closures) |
| 37 | CS12·CS13 | [[12,3,2]] | 6 | 3 | 4 | 2 | level-3 general-target exhaustive SAT (gap closures) |
| 38 | CS13·CCZ123 | [[12,3,2]] | 7 | 3 | 4 | 2 | level-3 general-target exhaustive SAT (gap closures) |
| 39 | 01·234 | [[18,5,2]] | 7 | 3 | 9 | 3 | my experiments: CS+CCZ entangled 5-output factory |
| 40 | T^6 | [[26,6,2]] | 9 | 3 | 6 | 1 | level-3 general-target exhaustive SAT (gap closures) |
| 41 | T0.CS01.CCZ012 | [[43,3,3]] | 10 | 3 | 5 | 2 | author-supplied: [[43,3,3]] T-count-5 witness (complete n<=44 checks<=7 census; k=3 representative, GL(3,2)-inequivalent to the k=4 T-count-5 entry) |
| 42 | CCZ | [[47,3,3]] | 9 | 3 | 7 | 3 | slot ansatz S1+S1+S2+S2 (N=9, most compact CCZ [[47,3,3]]) |
| 43 | T0.CS01.CS02.CS12.CS13.CS23.CCZ012.CCZ013.CCZ023.CCZ123 | [[43,4,3]] | 11 | 3 | 5 | 2 | author-supplied: [[43,4,3]] T-count-5 witness (complete n<=44 checks<=7 census; representative of the GL(4,2) class {t5-07,08,10}) |
| 44 | T | [[44,4,3]] | 11 | 3 | 4 | 1 | beyond cyclic/symmetric: odd-order non-cyclic permutation groups (interactive session) |
| 45 | T | [[47,4,3]] | 10 | 3 | 4 | 1 | slot ansatz, k=4 subgroup-relaxed geometry (interactive session) |
| 46 | 01·23 | [[48,4,3]] | 11 | 3 | 6 | 2 | author-supplied: [[48,4,3]] CS01.CS23 factory (improves on [[63,4,3]]) |
| 47 | 01·23 | [[63,4,3]] | 13 | 3 | 6 | 2 | slot ansatz, subgroup-relaxed geometries (interactive session) |
| 48 | T0.T1.T4.CS01.CS04.CS14.CCZ012.CCZ013.CCZ023.CCZ024.CCZ124.CCZ234 | [[47,5,3]] | 11 | 3 | 10 | 3 | author-supplied: [[47,5,3]] T-count-10 witness (unrestricted output-subspace random search) |
| 49 | T^5 | [[51,5,3]] | 12 | 3 | 5 | 1 | author-supplied: [[51,5,3]] T^5 factory |
| 50 | CCZ-parent relabel | [[47,6,3]] | 12 | 3 | 11 | 3 | colored-quotient free-relabel search (colored-quotient relabel search) over the CCZ [[47,3,3]] check parent (archived result ccz_47_s1s1s2s2.json) |
| 51 | T | [[48,1,4]] | 14 | 3 | 1 | 1 | automorphism-seeded ansatz: Bravyi-Haah [[49,1,5]] symmetry group (arXiv:1209.2426 App. B), extended search |
| 52 | T | [[52,1,4]] | 10 | 3 | 1 | 1 | beyond cyclic/symmetric: odd-order non-cyclic permutation groups (interactive session) |
| 53 | T | [[52,1,4]] | 10 | 3 | 1 | 1 | slot ansatz, subgroup-relaxed geometries (interactive session) |
| 54 | T | [[49,1,5]] | 14 | 3 | 1 | 1 | automorphism-seeded ansatz: Bravyi-Haah [[49,1,5]] symmetry group (arXiv:1209.2426 App. B), extended search |
| 55 | sqrtT | [[30,2,2]] | 6 | 4 | n/a | 1 | level-2 / level-4 exhaustive SAT (gap closures) |
| 56 | sqrtT | [[44,3,2]] | 7 | 4 | n/a | 1 | level-2 / level-4 exhaustive SAT (gap closures) |
| 57 | sqrtT | [[31,1,3]] | 6 | 4 | n/a | 1 | level-2 / level-4 exhaustive SAT (gap closures) |

## analytic (level-3 simplex chain)

### 1. T [[14,1,2]]

- output gate: `T0`
- ambient qubits: `N=4`; Clifford level: `3`
- provenance: analytic: punctured simplex on N=4 wires -- every nonzero column except those inside the k=1 output block, so n = 2^4 - 2^1 = 14; deposits the width-1 level-3 gate and has d = 2 exactly, derived in theory/01_factories_and_distance.md ('The punctured simplex'); the identical circuit was independently rediscovered by ansatz-free CP-SAT search (archived symmetry-reduced CP-SAT binary-matrix export, catalogued separately as 'T (N=4)' until the two rows were merged)
- exact T-count: `1`; reduced degree: `1`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{1}, {0,1}, {2}, {0,2}, {1,2}, {0,1,2}, {3}, {0,3}, {1,3}, {0,1,3}, {2,3}, {0,2,3}, {1,2,3}, {0,1,2,3}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13
o0     0  1  0  1  0  1  0  1  0  1  0  1  0  1
c0     1  1  0  0  1  1  0  0  1  1  0  0  1  1
c1     0  0  1  1  1  1  0  0  0  0  1  1  1  1
c2     0  0  0  0  0  0  1  1  1  1  1  1  1  1
```

### 2. CS [[12,2,2]]

- output gate: `CS01`
- ambient qubits: `N=4`; Clifford level: `3`
- provenance: analytic: punctured simplex on N=4 wires -- every nonzero column except those inside the k=2 output block, so n = 2^4 - 2^2 = 12; deposits the width-2 level-3 gate and has d = 2 exactly, derived in theory/01_factories_and_distance.md ('The punctured simplex'); the identical circuit was independently rediscovered by ansatz-free CP-SAT search (archived symmetry-reduced CP-SAT binary-matrix export, catalogued separately as 'CS (N=4)' until the two rows were merged)
- exact T-count: `3`; reduced degree: `2`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{2}, {0,2}, {1,2}, {0,1,2}, {3}, {0,3}, {1,3}, {0,1,3}, {2,3}, {0,2,3}, {1,2,3}, {0,1,2,3}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11
o0     0  1  0  1  0  1  0  1  0  1  0  1
o1     0  0  1  1  0  0  1  1  0  0  1  1
c0     1  1  1  1  0  0  0  0  1  1  1  1
c1     0  0  0  0  1  1  1  1  1  1  1  1
```

### 3. CCZ [[8,3,2]]

- output gate: `CCZ012`
- ambient qubits: `N=4`; Clifford level: `3`
- provenance: analytic: punctured simplex on N=4 wires -- every nonzero column except those inside the k=3 output block, so n = 2^4 - 2^3 = 8; deposits the width-3 level-3 gate and has d = 2 exactly, derived in theory/01_factories_and_distance.md ('The punctured simplex'); the identical circuit was independently rediscovered by ansatz-free CP-SAT search (archived symmetry-reduced CP-SAT binary-matrix export, catalogued separately as 'CCZ (N=4)' until the two rows were merged)
- exact T-count: `7`; reduced degree: `3`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{3}, {0,3}, {1,3}, {0,1,3}, {2,3}, {0,2,3}, {1,2,3}, {0,1,2,3}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
     g0g1g2g3g4g5g6g7
o0    0 1 0 1 0 1 0 1
o1    0 0 1 1 0 0 1 1
o2    0 0 0 0 1 1 1 1
c0    1 1 1 1 1 1 1 1
```


## analytic (level-4 simplex chain)

### 4. sqrt(T) [[30,1,2]]

- output gate: `sqrtT0`
- ambient qubits: `N=5`; Clifford level: `4`
- provenance: analytic: punctured simplex on N=5 wires -- every nonzero column except those inside the k=1 output block, so n = 2^5 - 2^1 = 30; deposits the width-1 level-4 gate and has d = 2 exactly, derived in theory/01_factories_and_distance.md ('The punctured simplex')
- exact T-count: `None`; reduced degree: `1`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{1}, {0,1}, {2}, {0,2}, {1,2}, {0,1,2}, {3}, {0,3}, {1,3}, {0,1,3}, {2,3}, {0,2,3}, {1,2,3}, {0,1,2,3}, {4}, {0,4}, {1,4}, {0,1,4}, {2,4}, {0,2,4}, {1,2,4}, {0,1,2,4}, {3,4}, {0,3,4}, {1,3,4}, {0,1,3,4}, {2,3,4}, {0,2,3,4}, {1,2,3,4}, {0,1,2,3,4}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19g20g21g22g23g24g25g26g27g28g29
o0     0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1
c0     1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1
c1     0  0  1  1  1  1  0  0  0  0  1  1  1  1  0  0  0  0  1  1  1  1  0  0  0  0  1  1  1  1
c2     0  0  0  0  0  0  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1
c3     0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1
```

### 5. CT [[28,2,2]]

- output gate: `CT01`
- ambient qubits: `N=5`; Clifford level: `4`
- provenance: analytic: punctured simplex on N=5 wires -- every nonzero column except those inside the k=2 output block, so n = 2^5 - 2^2 = 28; deposits the width-2 level-4 gate and has d = 2 exactly, derived in theory/01_factories_and_distance.md ('The punctured simplex')
- exact T-count: `None`; reduced degree: `2`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{2}, {0,2}, {1,2}, {0,1,2}, {3}, {0,3}, {1,3}, {0,1,3}, {2,3}, {0,2,3}, {1,2,3}, {0,1,2,3}, {4}, {0,4}, {1,4}, {0,1,4}, {2,4}, {0,2,4}, {1,2,4}, {0,1,2,4}, {3,4}, {0,3,4}, {1,3,4}, {0,1,3,4}, {2,3,4}, {0,2,3,4}, {1,2,3,4}, {0,1,2,3,4}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19g20g21g22g23g24g25g26g27
o0     0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1
o1     0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1
c0     1  1  1  1  0  0  0  0  1  1  1  1  0  0  0  0  1  1  1  1  0  0  0  0  1  1  1  1
c1     0  0  0  0  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1
c2     0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1
```

### 6. CCS [[24,3,2]]

- output gate: `CCS012`
- ambient qubits: `N=5`; Clifford level: `4`
- provenance: analytic: punctured simplex on N=5 wires -- every nonzero column except those inside the k=3 output block, so n = 2^5 - 2^3 = 24; deposits the width-3 level-4 gate and has d = 2 exactly, derived in theory/01_factories_and_distance.md ('The punctured simplex')
- exact T-count: `None`; reduced degree: `3`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{3}, {0,3}, {1,3}, {0,1,3}, {2,3}, {0,2,3}, {1,2,3}, {0,1,2,3}, {4}, {0,4}, {1,4}, {0,1,4}, {2,4}, {0,2,4}, {1,2,4}, {0,1,2,4}, {3,4}, {0,3,4}, {1,3,4}, {0,1,3,4}, {2,3,4}, {0,2,3,4}, {1,2,3,4}, {0,1,2,3,4}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19g20g21g22g23
o0     0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1
o1     0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1
o2     0  0  0  0  1  1  1  1  0  0  0  0  1  1  1  1  0  0  0  0  1  1  1  1
c0     1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1
c1     0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1
```

### 7. CCCZ [[16,4,2]]

- output gate: `CCCZ0123`
- ambient qubits: `N=5`; Clifford level: `4`
- provenance: analytic: punctured simplex on N=5 wires -- every nonzero column except those inside the k=4 output block, so n = 2^5 - 2^4 = 16; deposits the width-4 level-4 gate and has d = 2 exactly, derived in theory/01_factories_and_distance.md ('The punctured simplex')
- exact T-count: `None`; reduced degree: `4`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{4}, {0,4}, {1,4}, {0,1,4}, {2,4}, {0,2,4}, {1,2,4}, {0,1,2,4}, {3,4}, {0,3,4}, {1,3,4}, {0,1,3,4}, {2,3,4}, {0,2,3,4}, {1,2,3,4}, {0,1,2,3,4}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15
o0     0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1
o1     0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1
o2     0  0  0  0  1  1  1  1  0  0  0  0  1  1  1  1
o3     0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1
c0     1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1
```


## analytic (level-2 simplex chain)

### 8. S [[6,1,2]]

- output gate: `S0`
- ambient qubits: `N=3`; Clifford level: `2`
- provenance: analytic: punctured simplex on N=3 wires -- every nonzero column except those inside the k=1 output block, so n = 2^3 - 2^1 = 6; deposits the width-1 level-2 gate and has d = 2 exactly, derived in theory/01_factories_and_distance.md ('The punctured simplex')
- exact T-count: `0`; reduced degree: `1`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{1}, {0,1}, {2}, {0,2}, {1,2}, {0,1,2}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
     g0g1g2g3g4g5
o0    0 1 0 1 0 1
c0    1 1 0 0 1 1
c1    0 0 1 1 1 1
```

### 9. CZ [[4,2,2]]

- output gate: `CZ01`
- ambient qubits: `N=3`; Clifford level: `2`
- provenance: analytic: punctured simplex on N=3 wires -- every nonzero column except those inside the k=2 output block, so n = 2^3 - 2^2 = 4; deposits the width-2 level-2 gate and has d = 2 exactly, derived in theory/01_factories_and_distance.md ('The punctured simplex')
- exact T-count: `0`; reduced degree: `2`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{2}, {0,2}, {1,2}, {0,1,2}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
     g0g1g2g3
o0    0 1 0 1
o1    0 0 1 1
c0    1 1 1 1
```


## distance-2 level-3 (SAT search, explicit circuits)

### 10. CS [[20,2,2]]

- output gate: `CS01`
- ambient qubits: `N=6`; Clifford level: `3`
- provenance: archived symmetry-reduced CP-SAT binary-matrix export
- exact T-count: `3`; reduced degree: `2`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{2}, {0,2}, {1,2}, {0,1,2}, {3}, {0,3}, {1,3}, {0,1,3}, {4}, {0,4}, {1,4}, {0,1,4}, {5}, {0,5}, {1,5}, {0,1,5}, {2,3,4,5}, {0,2,3,4,5}, {1,2,3,4,5}, {0,1,2,3,4,5}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19
o0     0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1
o1     0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1
c0     1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1
c1     0  0  0  0  1  1  1  1  0  0  0  0  0  0  0  0  1  1  1  1
c2     0  0  0  0  0  0  0  0  1  1  1  1  0  0  0  0  1  1  1  1
c3     0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1
```

### 11. T^2 [[21,2,2]]

- output gate: `T0 . T1`
- ambient qubits: `N=6`; Clifford level: `3`
- provenance: archived symmetry-reduced CP-SAT binary-matrix export
- exact T-count: `2`; reduced degree: `1`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{0,1,2}, {0,1,3}, {0,1,2,3}, {0,1,4}, {0,1,2,4}, {0,1,3,4}, {2,3,4}, {0,2,3,4}, {1,2,3,4}, {0,5}, {1,5}, {0,1,5}, {2,5}, {3,5}, {2,3,5}, {4,5}, {2,4,5}, {3,4,5}, {0,2,3,4,5}, {1,2,3,4,5}, {0,1,2,3,4,5}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19g20
o0     1  1  1  1  1  1  0  1  0  1  0  1  0  0  0  0  0  0  1  0  1
o1     1  1  1  1  1  1  0  0  1  0  1  1  0  0  0  0  0  0  0  1  1
c0     1  0  1  0  1  0  1  1  1  0  0  0  1  0  1  0  1  0  1  1  1
c1     0  1  1  0  0  1  1  1  1  0  0  0  0  1  1  0  0  1  1  1  1
c2     0  0  0  1  1  1  1  1  1  0  0  0  0  0  0  1  1  1  1  1  1
c3     0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1
```

### 12. T1_CS12 [[25,2,2]]

- output gate: `T0 . CS01`
- ambient qubits: `N=6`; Clifford level: `3`
- provenance: archived symmetry-reduced CP-SAT binary-matrix export
- exact T-count: `2`; reduced degree: `1`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{0,1,2}, {0,1,3}, {0,2,3}, {0,4}, {1,4}, {0,1,4}, {1,2,4}, {1,3,4}, {2,3,4}, {0,5}, {1,5}, {0,1,5}, {2,5}, {0,2,5}, {0,1,2,5}, {3,5}, {0,3,5}, {0,1,3,5}, {2,3,5}, {0,4,5}, {0,1,2,4,5}, {0,1,3,4,5}, {2,3,4,5}, {1,2,3,4,5}, {0,1,2,3,4,5}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19g20g21g22g23g24
o0     1  1  1  1  0  1  0  0  0  1  0  1  0  1  1  0  1  1  0  1  1  1  0  0  1
o1     1  1  0  0  1  1  1  1  0  0  1  1  0  0  1  0  0  1  0  0  1  1  0  1  1
c0     1  0  1  0  0  0  1  0  1  0  0  0  1  1  1  0  0  0  1  0  1  0  1  1  1
c1     0  1  1  0  0  0  0  1  1  0  0  0  0  0  0  1  1  1  1  0  0  1  1  1  1
c2     0  0  0  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1
c3     0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1
```

### 13. T3_CCZ123 [[18,3,2]]

- output gate: `T2 . CCZ012`
- ambient qubits: `N=6`; Clifford level: `3`
- provenance: archived symmetry-reduced CP-SAT binary-matrix export
- exact T-count: `6`; reduced degree: `2`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{0,1,3}, {0,1,2,3}, {0,1,4}, {0,1,2,4}, {0,3,4}, {1,3,4}, {0,1,3,4}, {0,2,3,4}, {1,2,3,4}, {0,1,2,3,4}, {0,1,5}, {0,1,2,5}, {3,5}, {2,3,5}, {4,5}, {2,4,5}, {0,1,3,4,5}, {0,1,2,3,4,5}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17
o0     1  1  1  1  1  0  1  1  0  1  1  1  0  0  0  0  1  1
o1     1  1  1  1  0  1  1  0  1  1  1  1  0  0  0  0  1  1
o2     0  1  0  1  0  0  0  1  1  1  0  1  0  1  0  1  0  1
c0     1  1  0  0  1  1  1  1  1  1  0  0  1  1  0  0  1  1
c1     0  0  1  1  1  1  1  1  1  1  0  0  0  0  1  1  1  1
c2     0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1
```

### 14. CS12_CS13_CCZ123 [[20,3,2]]

- output gate: `CS01 . CS02 . CCZ012`
- ambient qubits: `N=6`; Clifford level: `3`
- provenance: archived symmetry-reduced CP-SAT binary-matrix export
- exact T-count: `3`; reduced degree: `2`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{0,4}, {1,4}, {2,4}, {0,1,2,4}, {0,3,4}, {0,1,3,4}, {0,2,3,4}, {0,1,2,3,4}, {0,5}, {1,5}, {2,5}, {0,1,2,5}, {0,3,5}, {0,1,3,5}, {0,2,3,5}, {0,1,2,3,5}, {4,5}, {0,4,5}, {1,2,4,5}, {0,1,2,4,5}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19
o0     1  0  0  1  1  1  1  1  1  0  0  1  1  1  1  1  0  1  0  1
o1     0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  0  1  1
o2     0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1
c0     0  0  0  0  1  1  1  1  0  0  0  0  1  1  1  1  0  0  0  0
c1     1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  1  1  1  1
c2     0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1
```

### 15. T1_T2_T3_CS13_CS23 [[24,3,2]]

- output gate: `T0 . T1 . T2 . CS02 . CS12`
- ambient qubits: `N=6`; Clifford level: `3`
- provenance: archived symmetry-reduced CP-SAT binary-matrix export
- exact T-count: `3`; reduced degree: `1`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{0,1,3}, {0,2,3}, {1,2,3}, {0,1,2,3}, {0,1,4}, {0,2,4}, {1,2,4}, {0,1,2,4}, {0,3,4}, {1,3,4}, {0,1,3,4}, {0,1,2,3,4}, {0,5}, {1,5}, {0,1,5}, {2,5}, {0,2,5}, {1,2,5}, {0,1,3,5}, {2,3,5}, {0,1,4,5}, {2,4,5}, {3,4,5}, {0,1,2,3,4,5}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19g20g21g22g23
o0     1  1  0  1  1  1  0  1  1  0  1  1  1  0  1  0  1  0  1  0  1  0  0  1
o1     1  0  1  1  1  0  1  1  0  1  1  1  0  1  1  0  0  1  1  0  1  0  0  1
o2     0  1  1  1  0  1  1  1  0  0  0  1  0  0  0  1  1  1  0  1  0  1  0  1
c0     1  1  1  1  0  0  0  0  1  1  1  1  0  0  0  0  0  0  1  1  0  0  1  1
c1     0  0  0  0  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  1  1  1  1
c2     0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1
```

### 16. CS13_CS14_CS23_CCZ124_CCZ234 [[18,4,2]]

- output gate: `CS02 . CS03 . CS12 . CCZ013 . CCZ123`
- ambient qubits: `N=6`; Clifford level: `3`
- provenance: archived symmetry-reduced CP-SAT binary-matrix export
- exact T-count: `6`; reduced degree: `2`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{1,2,4}, {0,1,2,4}, {0,3,4}, {1,3,4}, {0,2,3,4}, {0,1,2,3,4}, {1,2,5}, {0,1,2,5}, {0,3,5}, {1,3,5}, {0,2,3,5}, {0,1,2,3,5}, {1,2,4,5}, {0,1,2,4,5}, {0,3,4,5}, {1,3,4,5}, {0,2,3,4,5}, {0,1,2,3,4,5}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17
o0     0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1
o1     1  1  0  1  0  1  1  1  0  1  0  1  1  1  0  1  0  1
o2     1  1  0  0  1  1  1  1  0  0  1  1  1  1  0  0  1  1
o3     0  0  1  1  1  1  0  0  1  1  1  1  0  0  1  1  1  1
c0     1  1  1  1  1  1  0  0  0  0  0  0  1  1  1  1  1  1
c1     0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1
```

### 17. CS13_CS23_CS34_CCZ234 [[20,4,2]]

- output gate: `CS02 . CS12 . CS23 . CCZ123`
- ambient qubits: `N=6`; Clifford level: `3`
- provenance: archived symmetry-reduced CP-SAT binary-matrix export
- exact T-count: `4`; reduced degree: `2`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{0,1,4}, {0,1,2,4}, {3,4}, {2,3,4}, {0,1,5}, {2,5}, {0,2,5}, {1,2,5}, {3,5}, {0,2,3,5}, {1,2,3,5}, {0,1,2,3,5}, {4,5}, {1,4,5}, {0,1,4,5}, {0,2,4,5}, {3,4,5}, {0,3,4,5}, {0,1,3,4,5}, {1,2,3,4,5}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19
o0     1  1  0  0  1  0  1  0  0  1  0  1  0  0  1  1  0  1  1  0
o1     1  1  0  0  1  0  0  1  0  0  1  1  0  1  1  0  0  0  1  1
o2     0  1  0  1  0  1  1  1  0  1  1  1  0  0  0  1  0  0  0  1
o3     0  0  1  1  0  0  0  0  1  1  1  1  0  0  0  0  1  1  1  1
c0     1  1  1  1  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1
c1     0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1
```

### 18. CCZ135_CCZ145_CCZ234_CCZ245 [[12,5,2]]

- output gate: `CCZ024 . CCZ034 . CCZ123 . CCZ134`
- ambient qubits: `N=6`; Clifford level: `3`
- provenance: archived symmetry-reduced CP-SAT binary-matrix export
- exact T-count: `11`; reduced degree: `3`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{0,2,5}, {1,2,5}, {1,3,5}, {0,1,3,5}, {0,2,3,5}, {0,1,2,3,5}, {0,4,5}, {0,1,4,5}, {1,2,4,5}, {0,1,2,4,5}, {0,3,4,5}, {1,3,4,5}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11
o0     1  0  0  1  1  1  1  1  0  1  1  0
o1     0  1  1  1  0  1  0  1  1  1  0  1
o2     1  1  0  0  1  1  0  0  1  1  0  0
o3     0  0  1  1  1  1  0  0  0  0  1  1
o4     0  0  0  0  0  0  1  1  1  1  1  1
c0     1  1  1  1  1  1  1  1  1  1  1  1
```

### 19. CCZ123_CCZ124_CCZ125 [[16,5,2]]

- output gate: `CCZ012 . CCZ013 . CCZ014`
- ambient qubits: `N=6`; Clifford level: `3`
- provenance: archived symmetry-reduced CP-SAT binary-matrix export
- exact T-count: `7`; reduced degree: `3`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{2,3,5}, {0,2,3,5}, {1,2,3,5}, {0,1,2,3,5}, {2,4,5}, {0,2,4,5}, {1,2,4,5}, {0,1,2,4,5}, {3,4,5}, {0,3,4,5}, {1,3,4,5}, {0,1,3,4,5}, {2,3,4,5}, {0,2,3,4,5}, {1,2,3,4,5}, {0,1,2,3,4,5}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15
o0     0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1
o1     0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1
o2     1  1  1  1  1  1  1  1  0  0  0  0  1  1  1  1
o3     1  1  1  1  0  0  0  0  1  1  1  1  1  1  1  1
o4     0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1
c0     1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1
```

### 20. CCZ123_CCZ124_CCZ134_CCZ235 [[20,5,2]]

- output gate: `CCZ012 . CCZ013 . CCZ023 . CCZ124`
- ambient qubits: `N=6`; Clifford level: `3`
- provenance: archived symmetry-reduced CP-SAT binary-matrix export
- exact T-count: `11`; reduced degree: `3`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{1,5}, {0,1,5}, {2,5}, {0,2,5}, {0,3,5}, {1,3,5}, {2,3,5}, {0,1,2,3,5}, {4,5}, {0,4,5}, {1,4,5}, {0,1,4,5}, {2,4,5}, {0,2,4,5}, {1,2,4,5}, {0,1,2,4,5}, {0,3,4,5}, {0,1,3,4,5}, {0,2,3,4,5}, {0,1,2,3,4,5}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19
o0     0  1  0  1  1  0  0  1  0  1  0  1  0  1  0  1  1  1  1  1
o1     1  1  0  0  0  1  0  1  0  0  1  1  0  0  1  1  0  1  0  1
o2     0  0  1  1  0  0  1  1  0  0  0  0  1  1  1  1  0  0  1  1
o3     0  0  0  0  1  1  1  1  0  0  0  0  0  0  0  0  1  1  1  1
o4     0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1
c0     1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1
```


## distance-3/4 slot-ansatz (CP-SAT, structural distance)

### 21. T [[15,1,3]]

- output gate: `T0`
- ambient qubits: `N=5`; Clifford level: `3`
- provenance: archived slot-search output: geometry S4
- exact T-count: `1`; reduced degree: `1`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{1}, {2}, {3}, {4}, {0,1,2}, {0,1,3}, {0,1,4}, {0,2,3}, {0,2,4}, {0,3,4}, {1,2,3}, {1,2,4}, {1,3,4}, {2,3,4}, {0,1,2,3,4}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14
o0     0  0  0  0  1  1  1  1  1  1  0  0  0  0  1
c0     1  0  0  0  1  1  1  0  0  0  1  1  1  0  1
c1     0  1  0  0  1  0  0  1  1  0  1  1  0  1  1
c2     0  0  1  0  0  1  0  1  0  1  1  0  1  1  1
c3     0  0  0  1  0  0  1  0  1  1  0  1  1  1  1
```

### 22. T [[28,2,3]]

- output gate: `T0 . T1`
- ambient qubits: `N=9`; Clifford level: `3`
- provenance: archived slot-search output: geometry S3+S4
- exact T-count: `2`; reduced degree: `1`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{5}, {6}, {7}, {8}, {1,5,6}, {1,5,7}, {1,5,8}, {1,6,7}, {1,6,8}, {1,7,8}, {5,6,7}, {5,6,8}, {5,7,8}, {6,7,8}, {0,1,2}, {0,1,3}, {0,1,4}, {2,5,6,7,8}, {3,5,6,7,8}, {4,5,6,7,8}, {0,2,3}, {0,2,4}, {0,3,4}, {1,2,3,5,6,7,8}, {1,2,4,5,6,7,8}, {1,3,4,5,6,7,8}, {0,1,2,3,4}, {2,3,4,5,6,7,8}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19g20g21g22g23g24g25g26g27
o0     0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  0  0  0  1  1  1  0  0  0  1  0
o1     0  0  0  0  1  1  1  1  1  1  0  0  0  0  1  1  1  0  0  0  0  0  0  1  1  1  1  0
c0     0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  0  0  1  0  0  1  1  0  1  1  0  1  1
c1     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  0  0  1  0  1  0  1  1  0  1  1  1
c2     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  0  0  1  0  1  1  0  1  1  1  1
c3     1  0  0  0  1  1  1  0  0  0  1  1  1  0  0  0  0  1  1  1  0  0  0  1  1  1  0  1
c4     0  1  0  0  1  0  0  1  1  0  1  1  0  1  0  0  0  1  1  1  0  0  0  1  1  1  0  1
c5     0  0  1  0  0  1  0  1  0  1  1  0  1  1  0  0  0  1  1  1  0  0  0  1  1  1  0  1
c6     0  0  0  1  0  0  1  0  1  1  0  1  1  1  0  0  0  1  1  1  0  0  0  1  1  1  0  1
```

### 23. CS [[35,2,3]]

- output gate: `CS01`
- ambient qubits: `N=9`; Clifford level: `3`
- provenance: archived slot-search output: geometry C7
- exact T-count: `3`; reduced degree: `2`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{1,2,3}, {1,3,4}, {1,4,5}, {1,5,6}, {1,6,7}, {1,2,8}, {1,7,8}, {1,2,5}, {1,2,6}, {1,3,6}, {1,3,7}, {1,4,7}, {1,4,8}, {1,5,8}, {1,2,3,4,5}, {1,3,4,5,6}, {1,4,5,6,7}, {1,2,3,4,8}, {1,2,3,7,8}, {1,2,6,7,8}, {1,5,6,7,8}, {0,1,2,3,4,6}, {0,1,3,4,5,7}, {0,1,2,5,6,7}, {0,1,2,3,5,8}, {0,1,4,5,6,8}, {0,1,2,4,7,8}, {0,1,3,6,7,8}, {0,2,4,5,6}, {0,2,3,4,7}, {0,3,5,6,7}, {0,3,4,5,8}, {0,2,3,6,8}, {0,2,5,7,8}, {0,4,6,7,8}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19g20g21g22g23g24g25g26g27g28g29g30g31g32g33g34
o0     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  1  1
o1     1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0
c0     1  0  0  0  0  1  0  1  1  0  0  0  0  0  1  0  0  1  1  1  0  1  0  1  1  0  1  0  1  1  0  0  1  1  0
c1     1  1  0  0  0  0  0  0  0  1  1  0  0  0  1  1  0  1  1  0  0  1  1  0  1  0  0  1  0  1  1  1  1  0  0
c2     0  1  1  0  0  0  0  0  0  0  0  1  1  0  1  1  1  1  0  0  0  1  1  0  0  1  1  0  1  1  0  1  0  0  1
c3     0  0  1  1  0  0  0  1  0  0  0  0  0  1  1  1  1  0  0  0  1  0  1  1  1  1  0  0  1  0  1  1  0  1  0
c4     0  0  0  1  1  0  0  0  1  1  0  0  0  0  0  1  1  0  0  1  1  1  0  1  0  1  0  1  1  0  1  0  1  0  1
c5     0  0  0  0  1  0  1  0  0  0  1  1  0  0  0  0  1  0  1  1  1  0  1  1  0  0  1  1  0  1  1  0  0  1  1
c6     0  0  0  0  0  1  1  0  0  0  0  0  1  1  0  0  0  1  1  1  1  0  0  0  1  1  1  1  0  0  0  1  1  1  1
```

### 24. T [[35,3,3]]

- output gate: `T0 . T1 . T2`
- ambient qubits: `N=10`; Clifford level: `3`
- provenance: archived slot-search output: geometry C7
- exact T-count: `3`; reduced degree: `1`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{2,3,4,5,6}, {2,4,5,6,7}, {2,5,6,7,8}, {2,3,4,5,9}, {2,3,4,8,9}, {2,3,7,8,9}, {2,6,7,8,9}, {0,3,4,5,7}, {0,4,5,6,8}, {0,3,6,7,8}, {0,3,4,6,9}, {0,5,6,7,9}, {0,3,5,8,9}, {0,4,7,8,9}, {2,3,4,6,7}, {2,3,4,7,8}, {2,4,5,7,8}, {2,3,5,6,9}, {2,3,6,7,9}, {2,4,5,8,9}, {2,5,6,8,9}, {1,3,5,6,7}, {1,3,4,5,8}, {1,4,6,7,8}, {1,4,5,6,9}, {1,3,4,7,9}, {1,3,6,8,9}, {1,5,7,8,9}, {2,3,4,6,8}, {2,3,5,6,8}, {2,3,5,7,8}, {2,3,5,7,9}, {2,4,5,7,9}, {2,4,6,7,9}, {2,4,6,8,9}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19g20g21g22g23g24g25g26g27g28g29g30g31g32g33g34
o0     0  0  0  0  0  0  0  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
o1     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  0  0  0  0  0  0  0
o2     1  1  1  1  1  1  1  0  0  0  0  0  0  0  1  1  1  1  1  1  1  0  0  0  0  0  0  0  1  1  1  1  1  1  1
c0     1  0  0  1  1  1  0  1  0  1  1  0  1  0  1  1  0  1  1  0  0  1  1  0  0  1  1  0  1  1  1  1  0  0  0
c1     1  1  0  1  1  0  0  1  1  0  1  0  0  1  1  1  1  0  0  1  0  0  1  1  1  1  0  0  1  0  0  0  1  1  1
c2     1  1  1  1  0  0  0  1  1  0  0  1  1  0  0  0  1  1  0  1  1  1  1  0  1  0  0  1  0  1  1  1  1  0  0
c3     1  1  1  0  0  0  1  0  1  1  1  1  0  0  1  0  0  1  1  0  1  1  0  1  1  0  1  0  1  1  0  0  0  1  1
c4     0  1  1  0  0  1  1  1  0  1  0  1  0  1  1  1  1  0  1  0  0  1  0  1  0  1  0  1  0  0  1  1  1  1  0
c5     0  0  1  0  1  1  1  0  1  1  0  0  1  1  0  1  1  0  0  1  1  0  1  1  0  0  1  1  1  1  1  0  0  0  1
c6     0  0  0  1  1  1  1  0  0  0  1  1  1  1  0  0  0  1  1  1  1  0  0  0  1  1  1  1  0  0  0  1  1  1  1
```

### 25. T [[64,1,4]]

- output gate: `T0`
- ambient qubits: `N=10`; Clifford level: `3`
- provenance: archived slot-search output: geometry C9
- exact T-count: `1`; reduced degree: `1`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{1,3,5}, {2,4,6}, {3,5,7}, {1,3,8}, {1,6,8}, {4,6,8}, {2,4,9}, {2,7,9}, {5,7,9}, {1,2,6}, {1,5,6}, {2,3,7}, {2,6,7}, {3,4,8}, {3,7,8}, {1,5,9}, {4,5,9}, {4,8,9}, {1,2,3,5,6}, {2,3,4,6,7}, {3,4,5,7,8}, {1,2,6,7,8}, {1,2,4,5,9}, {1,5,6,7,9}, {1,3,4,8,9}, {4,5,6,8,9}, {2,3,7,8,9}, {0,1,4,5,6}, {0,1,2,3,7}, {0,2,5,6,7}, {0,2,3,4,8}, {0,3,6,7,8}, {0,3,4,5,9}, {0,1,2,6,9}, {0,1,5,8,9}, {0,4,7,8,9}, {1,3,5,7}, {1,3,5,8}, {1,3,6,8}, {1,4,6,8}, {2,4,6,8}, {2,4,6,9}, {2,4,7,9}, {2,5,7,9}, {3,5,7,9}, {1,3,4,5,7}, {1,2,3,5,8}, {2,4,5,6,8}, {1,4,6,7,8}, {2,3,4,6,9}, {1,2,4,7,9}, {3,5,6,7,9}, {1,3,6,8,9}, {2,5,7,8,9}, {0,1,2,4,6,8}, {0,1,3,4,6,8}, {0,1,3,5,6,8}, {0,1,3,5,7,8}, {0,1,3,5,7,9}, {0,2,3,5,7,9}, {0,2,4,5,7,9}, {0,2,4,6,7,9}, {0,2,4,6,8,9}, {0,1,2,3,4,5,6,7,8,9}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19g20g21g22g23g24g25g26g27g28g29g30g31g32g33g34g35g36g37g38g39g40g41g42g43g44g45g46g47g48g49g50g51g52g53g54g55g56g57g58g59g60g61g62g63
o0     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1
c0     1  0  0  1  1  0  0  0  0  1  1  0  0  0  0  1  0  0  1  0  0  1  1  1  1  0  0  1  1  0  0  0  0  1  1  0  1  1  1  1  0  0  0  0  0  1  1  0  1  0  1  0  1  0  1  1  1  1  1  0  0  0  0  1
c1     0  1  0  0  0  0  1  1  0  1  0  1  1  0  0  0  0  0  1  1  0  1  1  0  0  0  1  0  1  1  1  0  0  1  0  0  0  0  0  0  1  1  1  1  0  0  1  1  0  1  1  0  0  1  1  0  0  0  0  1  1  1  1  1
c2     1  0  1  1  0  0  0  0  0  0  0  1  0  1  1  0  0  0  1  1  1  0  0  0  1  0  1  0  1  0  1  1  1  0  0  0  1  1  1  0  0  0  0  0  1  1  1  0  0  1  0  1  1  0  0  1  1  1  1  1  0  0  0  1
c3     0  1  0  0  0  1  1  0  0  0  0  0  0  1  0  0  1  1  0  1  1  0  1  0  1  1  0  1  0  0  1  0  1  0  0  1  0  0  0  1  1  1  1  0  0  1  0  1  1  1  1  0  0  0  1  1  0  0  0  0  1  1  1  1
c4     1  0  1  0  0  0  0  0  1  0  1  0  0  0  0  1  1  0  1  0  1  0  1  1  0  1  0  1  0  1  0  0  1  0  1  0  1  1  0  0  0  0  0  1  1  1  1  1  0  0  0  1  0  1  0  0  1  1  1  1  1  0  0  1
c5     0  1  0  0  1  1  0  0  0  1  1  0  1  0  0  0  0  0  1  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  0  0  0  1  1  1  1  0  0  0  0  0  1  1  1  0  1  1  0  1  1  1  0  0  0  0  1  1  1
c6     0  0  1  0  0  0  0  1  1  0  0  1  1  0  1  0  0  0  0  1  1  1  0  1  0  0  1  0  1  1  0  1  0  0  0  1  1  0  0  0  0  0  1  1  1  1  0  0  1  0  1  1  0  1  0  0  0  1  1  1  1  1  0  1
c7     0  0  0  1  1  1  0  0  0  0  0  0  0  1  1  0  0  1  0  0  1  1  0  0  1  1  1  0  0  0  1  1  0  0  1  1  0  1  1  1  1  0  0  0  0  0  1  1  1  0  0  0  1  1  1  1  1  1  0  0  0  0  1  1
c8     0  0  0  0  0  0  1  1  1  0  0  0  0  0  0  1  1  1  0  0  0  0  1  1  1  1  1  0  0  0  0  0  1  1  1  1  0  0  0  0  0  1  1  1  1  0  0  0  0  1  1  1  1  1  0  0  0  0  1  1  1  1  1  1
```

### 26. T [[141,2,4]]

- output gate: `T0 . T1`
- ambient qubits: `N=12`; Clifford level: `3`
- provenance: archived slot-search output: geometry C7+S3
- exact T-count: `2`; reduced degree: `1`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{1,2,5}, {1,2,6}, {1,3,6}, {1,3,7}, {1,4,7}, {1,4,8}, {1,5,8}, {0,1,2,5,9}, {0,1,2,5,10}, {0,1,2,5,11}, {0,1,2,6,9}, {0,1,2,6,10}, {0,1,2,6,11}, {0,1,3,6,9}, {0,1,3,6,10}, {0,1,3,6,11}, {0,1,3,7,9}, {0,1,3,7,10}, {0,1,3,7,11}, {0,1,4,7,9}, {0,1,4,7,10}, {0,1,4,7,11}, {0,1,4,8,9}, {0,1,4,8,10}, {0,1,4,8,11}, {0,1,5,8,9}, {0,1,5,8,10}, {0,1,5,8,11}, {0,2,5,9,10}, {0,2,5,9,11}, {0,2,5,10,11}, {0,2,6,9,10}, {0,2,6,9,11}, {0,2,6,10,11}, {0,3,6,9,10}, {0,3,6,9,11}, {0,3,6,10,11}, {0,3,7,9,10}, {0,3,7,9,11}, {0,3,7,10,11}, {0,4,7,9,10}, {0,4,7,9,11}, {0,4,7,10,11}, {0,4,8,9,10}, {0,4,8,9,11}, {0,4,8,10,11}, {0,5,8,9,10}, {0,5,8,9,11}, {0,5,8,10,11}, {1,2,5,9,10,11}, {1,2,6,9,10,11}, {1,3,6,9,10,11}, {1,3,7,9,10,11}, {1,4,7,9,10,11}, {1,4,8,9,10,11}, {1,5,8,9,10,11}, {1,2,3,5}, {1,3,4,6}, {1,4,5,7}, {1,2,6,7}, {1,2,4,8}, {1,5,6,8}, {1,3,7,8}, {2,3,6}, {2,5,6}, {3,4,7}, {3,6,7}, {2,5,8}, {4,5,8}, {4,7,8}, {2,4,6}, {2,4,7}, {2,5,7}, {3,5,7}, {3,5,8}, {3,6,8}, {4,6,8}, {1,2,3,4,6,9}, {1,2,3,4,6,10}, {1,2,3,4,6,11}, {1,3,4,5,7,9}, {1,3,4,5,7,10}, {1,3,4,5,7,11}, {1,2,5,6,7,9}, {1,2,5,6,7,10}, {1,2,5,6,7,11}, {1,2,3,5,8,9}, {1,2,3,5,8,10}, {1,2,3,5,8,11}, {1,4,5,6,8,9}, {1,4,5,6,8,10}, {1,4,5,6,8,11}, {1,2,4,7,8,9}, {1,2,4,7,8,10}, {1,2,4,7,8,11}, {1,3,6,7,8,9}, {1,3,6,7,8,10}, {1,3,6,7,8,11}, {2,3,4,6,9,10}, {2,3,4,6,9,11}, {2,3,4,6,10,11}, {3,4,5,7,9,10}, {3,4,5,7,9,11}, {3,4,5,7,10,11}, {2,5,6,7,9,10}, {2,5,6,7,9,11}, {2,5,6,7,10,11}, {2,3,5,8,9,10}, {2,3,5,8,9,11}, {2,3,5,8,10,11}, {4,5,6,8,9,10}, {4,5,6,8,9,11}, {4,5,6,8,10,11}, {2,4,7,8,9,10}, {2,4,7,8,9,11}, {2,4,7,8,10,11}, {3,6,7,8,9,10}, {3,6,7,8,9,11}, {3,6,7,8,10,11}, {0,1,2,4,5,6,9,10,11}, {0,1,2,3,4,7,9,10,11}, {0,1,3,5,6,7,9,10,11}, {0,1,3,4,5,8,9,10,11}, {0,1,2,3,6,8,9,10,11}, {0,1,2,5,7,8,9,10,11}, {0,1,4,6,7,8,9,10,11}, {2,3,4,5,6}, {3,4,5,6,7}, {2,3,4,5,8}, {2,3,4,7,8}, {2,3,6,7,8}, {2,5,6,7,8}, {4,5,6,7,8}, {1,2,3,4,6,7}, {1,2,3,5,6,7}, {1,2,3,5,6,8}, {1,2,4,5,6,8}, {1,2,4,5,7,8}, {1,3,4,5,7,8}, {1,3,4,6,7,8}, {2,3,4,5,6,7,8}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
       g0  g1  g2  g3  g4  g5  g6  g7  g8  g9 g10 g11 g12 g13 g14 g15 g16 g17 g18 g19 g20 g21 g22 g23 g24 g25 g26 g27 g28 g29 g30 g31 g32 g33 g34 g35 g36 g37 g38 g39 g40 g41 g42 g43 g44 g45 g46 g47 g48 g49 g50 g51 g52 g53 g54 g55 g56 g57 g58 g59 g60 g61 g62 g63 g64 g65 g66 g67 g68 g69 g70 g71 g72 g73 g74 g75 g76 g77 g78 g79 g80 g81 g82 g83 g84 g85 g86 g87 g88 g89 g90 g91 g92 g93 g94 g95 g96 g97 g98 g99g100g101g102g103g104g105g106g107g108g109g110g111g112g113g114g115g116g117g118g119g120g121g122g123g124g125g126g127g128g129g130g131g132g133g134g135g136g137g138g139g140
o0      0   0   0   0   0   0   0   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   1   1   1   1   1   1   1   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0
o1      1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   1   1   1   1   1   1   1   1   1   1   1   1   1   1   0   0   0   0   0   0   0   0   0   0   0   0   0   0   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   1   1   1   1   1   1   1   0   0   0   0   0   0   0   1   1   1   1   1   1   1   0
c0      1   1   0   0   0   0   0   1   1   1   1   1   1   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   1   1   1   1   1   1   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   1   1   0   0   0   0   0   1   0   0   1   1   0   0   1   1   0   0   1   0   0   1   1   1   0   0   0   0   1   1   1   0   0   0   1   1   1   1   1   1   0   0   0   1   1   1   0   0   0   1   1   1   0   0   0   1   1   1   1   1   1   0   0   0   1   1   1   0   0   0   1   1   0   0   1   1   0   1   0   1   1   1   1   0   1   1   1   1   1   0   0   1
c1      0   0   1   1   0   0   0   0   0   0   0   0   0   1   1   1   1   1   1   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   1   1   1   1   1   1   0   0   0   0   0   0   0   0   0   0   0   1   1   0   0   0   1   1   0   0   0   0   1   1   0   1   1   0   0   0   0   0   0   1   1   1   0   1   1   1   1   1   1   0   0   0   1   1   1   0   0   0   0   0   0   1   1   1   1   1   1   1   1   1   0   0   0   1   1   1   0   0   0   0   0   0   1   1   1   0   1   1   1   1   0   0   1   1   1   1   1   0   0   1   1   1   0   0   1   1   1
c2      0   0   0   0   1   1   0   0   0   0   0   0   0   0   0   0   0   0   0   1   1   1   1   1   1   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   1   1   1   1   1   1   0   0   0   0   0   0   0   1   1   0   0   1   1   0   1   0   0   0   0   1   0   0   1   1   1   1   0   0   0   0   1   1   1   1   1   1   1   0   0   0   0   0   0   1   1   1   1   1   1   0   0   0   1   1   1   1   1   1   0   0   0   0   0   0   1   1   1   1   1   1   0   0   0   1   1   0   1   0   0   1   1   1   1   1   0   0   1   1   0   0   1   1   1   1   1
c3      1   0   0   0   0   0   1   1   1   1   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   1   1   1   1   1   1   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   1   1   1   1   0   0   0   0   0   1   1   0   1   0   0   1   0   0   1   0   0   1   1   0   0   0   1   1   1   0   0   0   0   0   1   1   1   1   1   1   1   1   1   1   1   1   0   0   0   0   0   0   0   0   0   1   1   1   1   1   1   1   1   1   1   1   1   0   0   0   0   0   0   1   0   1   1   0   1   0   1   1   1   0   0   1   1   0   1   1   1   1   1   0   1
c4      0   1   1   0   0   0   0   0   0   0   1   1   1   1   1   1   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   1   1   1   1   1   1   0   0   0   0   0   0   0   0   0   0   0   0   0   1   1   0   0   0   0   0   1   0   1   0   1   0   1   1   0   1   0   0   0   1   0   0   0   0   1   1   1   1   1   0   0   0   1   1   1   0   0   0   1   1   1   0   0   0   1   1   1   1   1   1   0   0   0   1   1   1   0   0   0   1   1   1   0   0   0   1   1   1   1   0   1   0   1   0   1   1   1   0   0   1   1   1   1   1   1   1   0   0   1   1
c5      0   0   0   1   1   0   0   0   0   0   0   0   0   0   0   0   1   1   1   1   1   1   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   1   1   1   1   1   1   0   0   0   0   0   0   0   0   0   1   1   0   0   0   0   1   1   0   0   1   0   0   1   1   0   0   1   0   1   1   1   0   0   0   0   0   0   1   1   1   1   1   1   0   0   0   0   0   0   1   1   1   1   1   1   0   0   0   1   1   1   1   1   1   0   0   0   0   0   0   1   1   1   1   1   1   0   1   1   0   0   1   1   0   1   0   1   1   1   1   1   1   0   0   1   1   1   1
c6      0   0   0   0   0   1   1   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   1   1   1   1   1   1   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   1   1   1   1   1   1   0   0   0   0   0   1   1   0   0   0   0   1   1   1   0   0   0   0   1   1   1   0   0   0   0   1   1   1   0   0   0   0   0   0   0   0   0   1   1   1   1   1   1   1   1   1   1   1   1   0   0   0   0   0   0   0   0   0   1   1   1   1   1   1   1   1   1   1   1   1   0   0   0   1   1   1   1   0   0   1   1   1   1   1   0   0   1   1   1   1   1   1
c7      0   0   0   0   0   0   0   1   0   0   1   0   0   1   0   0   1   0   0   1   0   0   1   0   0   1   0   0   1   1   0   1   1   0   1   1   0   1   1   0   1   1   0   1   1   0   1   1   0   1   1   1   1   1   1   1   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   1   0   0   1   0   0   1   0   0   1   0   0   1   0   0   1   0   0   1   0   0   1   1   0   1   1   0   1   1   0   1   1   0   1   1   0   1   1   0   1   1   0   1   1   1   1   1   1   1   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0
c8      0   0   0   0   0   0   0   0   1   0   0   1   0   0   1   0   0   1   0   0   1   0   0   1   0   0   1   0   1   0   1   1   0   1   1   0   1   1   0   1   1   0   1   1   0   1   1   0   1   1   1   1   1   1   1   1   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   1   0   0   1   0   0   1   0   0   1   0   0   1   0   0   1   0   0   1   0   1   0   1   1   0   1   1   0   1   1   0   1   1   0   1   1   0   1   1   0   1   1   1   1   1   1   1   1   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0
c9      0   0   0   0   0   0   0   0   0   1   0   0   1   0   0   1   0   0   1   0   0   1   0   0   1   0   0   1   0   1   1   0   1   1   0   1   1   0   1   1   0   1   1   0   1   1   0   1   1   1   1   1   1   1   1   1   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   1   0   0   1   0   0   1   0   0   1   0   0   1   0   0   1   0   0   1   0   1   1   0   1   1   0   1   1   0   1   1   0   1   1   0   1   1   0   1   1   1   1   1   1   1   1   1   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0
```

### 27. CCZ [[66,3,4]]

- output gate: `CCZ012`
- ambient qubits: `N=12`; Clifford level: `3`
- provenance: archived slot-search output: geometry C9
- exact T-count: `7`; reduced degree: `3`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{0,2,3,5,6}, {0,2,4,6,7}, {0,2,5,7,8}, {0,2,6,8,9}, {0,2,3,4,10}, {0,2,7,9,10}, {0,2,4,5,11}, {0,2,3,9,11}, {0,2,8,10,11}, {1,3,6,7}, {1,4,7,8}, {1,3,4,9}, {1,5,8,9}, {1,4,5,10}, {1,6,9,10}, {1,5,6,11}, {1,3,8,11}, {1,7,10,11}, {2,3,5,8}, {2,4,6,9}, {2,3,7,9}, {2,3,6,10}, {2,5,7,10}, {2,4,8,10}, {2,4,7,11}, {2,6,8,11}, {2,5,9,11}, {3,4,6,7,8}, {4,5,7,8,9}, {3,4,5,9,10}, {5,6,8,9,10}, {3,5,6,7,11}, {3,4,8,9,11}, {4,5,6,10,11}, {3,7,8,10,11}, {6,7,9,10,11}, {0,1,2,3,5,6,7,8}, {0,1,2,4,6,7,8,9}, {0,1,2,3,4,5,6,10}, {0,1,2,5,7,8,9,10}, {0,1,2,4,5,6,7,11}, {0,1,2,3,4,5,9,11}, {0,1,2,3,4,8,10,11}, {0,1,2,3,7,9,10,11}, {0,1,2,6,8,9,10,11}, {0,1,3,6,9}, {0,1,4,7,10}, {0,1,5,8,11}, {1,2,3,4,5,7,9}, {1,2,4,5,6,8,10}, {1,2,3,6,7,8,10}, {1,2,3,5,8,9,10}, {1,2,3,4,6,8,11}, {1,2,5,6,7,9,11}, {1,2,4,7,8,9,11}, {1,2,3,5,7,10,11}, {1,2,4,6,9,10,11}, {0,3,5,6,8,9}, {0,3,4,6,7,10}, {0,3,4,7,9,10}, {0,4,6,7,9,10}, {0,4,5,7,8,11}, {0,3,5,6,9,11}, {0,3,6,8,9,11}, {0,4,5,8,10,11}, {0,5,7,8,10,11}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19g20g21g22g23g24g25g26g27g28g29g30g31g32g33g34g35g36g37g38g39g40g41g42g43g44g45g46g47g48g49g50g51g52g53g54g55g56g57g58g59g60g61g62g63g64g65
o0     1  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1
o1     0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0
o2     1  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  0  0  0  1  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0
c0     1  0  0  0  1  0  0  1  0  1  0  1  0  0  0  0  1  0  1  0  1  1  0  0  0  0  0  1  0  1  0  1  1  0  1  0  1  0  1  0  0  1  1  1  0  1  0  0  1  0  1  1  1  0  0  1  0  1  1  1  0  0  1  1  0  0
c1     0  1  0  0  1  0  1  0  0  0  1  1  0  1  0  0  0  0  0  1  0  0  0  1  1  0  0  1  1  1  0  0  1  1  0  0  0  1  1  0  1  1  1  0  0  0  1  0  1  1  0  0  1  0  1  0  1  0  1  1  1  1  0  0  1  0
c2     1  0  1  0  0  0  1  0  0  0  0  0  1  1  0  1  0  0  1  0  0  0  1  0  0  0  1  0  1  1  1  1  0  1  0  0  1  0  1  1  1  1  0  0  0  0  0  1  1  1  0  1  0  1  0  1  0  1  0  0  0  1  1  0  1  1
c3     1  1  0  1  0  0  0  0  0  1  0  0  0  0  1  1  0  0  0  1  0  1  0  0  0  1  0  1  0  0  1  1  0  1  0  1  1  1  1  0  1  0  0  0  1  1  0  0  0  1  1  0  1  1  0  0  1  1  1  0  1  0  1  1  0  0
c4     0  1  1  0  0  1  0  0  0  1  1  0  0  0  0  0  0  1  0  0  1  0  1  0  1  0  0  1  1  0  0  1  0  0  1  1  1  1  0  1  1  0  0  1  0  0  1  0  1  0  1  0  0  1  1  1  0  0  1  1  1  1  0  0  0  1
c5     0  0  1  1  0  0  0  0  1  0  1  0  1  0  0  0  1  0  1  0  0  0  0  1  0  1  0  1  1  0  1  0  1  0  1  0  1  1  0  1  0  0  1  0  1  0  0  1  0  1  1  1  1  0  1  0  0  1  0  0  0  1  0  1  1  1
c6     0  0  0  1  0  1  0  1  0  0  0  1  1  0  1  0  0  0  0  1  1  0  0  0  0  0  1  0  1  1  1  0  1  0  0  1  0  1  0  1  0  1  0  1  1  1  0  0  1  0  0  1  0  1  1  0  1  1  0  1  1  0  1  1  0  0
c7     0  0  0  0  1  1  0  0  1  0  0  0  0  1  1  0  0  1  0  0  0  1  1  1  0  0  0  0  0  1  1  0  0  1  1  1  0  0  1  1  0  0  1  1  1  0  1  0  0  1  1  1  0  0  0  1  1  0  1  1  1  0  0  0  1  1
c8     0  0  0  0  0  0  1  1  1  0  0  0  0  0  0  1  1  1  0  0  0  0  0  0  1  1  1  0  0  0  0  1  1  1  1  1  0  0  0  0  1  1  1  1  1  0  0  1  0  0  0  0  1  1  1  1  1  0  0  0  0  1  1  1  1  1
```

### 28. T [[85,1,5]]

- output gate: `T0`
- ambient qubits: `N=11`; Clifford level: `3`
- provenance: archived slot-search output: geometry S5+S5
- exact T-count: `1`; reduced degree: `1`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{0,6}, {0,7}, {0,8}, {0,9}, {0,10}, {1}, {2}, {3}, {4}, {5}, {1,6,7,8,9,10}, {2,6,7,8,9,10}, {3,6,7,8,9,10}, {4,6,7,8,9,10}, {5,6,7,8,9,10}, {0,1,2,3,4}, {0,1,2,3,5}, {0,1,2,4,5}, {0,1,3,4,5}, {0,2,3,4,5}, {0,1,2,3,4,6,7}, {0,1,2,3,4,6,8}, {0,1,2,3,4,6,9}, {0,1,2,3,4,6,10}, {0,1,2,3,4,7,8}, {0,1,2,3,4,7,9}, {0,1,2,3,4,7,10}, {0,1,2,3,4,8,9}, {0,1,2,3,4,8,10}, {0,1,2,3,4,9,10}, {0,1,2,3,5,6,7}, {0,1,2,3,5,6,8}, {0,1,2,3,5,6,9}, {0,1,2,3,5,6,10}, {0,1,2,3,5,7,8}, {0,1,2,3,5,7,9}, {0,1,2,3,5,7,10}, {0,1,2,3,5,8,9}, {0,1,2,3,5,8,10}, {0,1,2,3,5,9,10}, {0,1,2,4,5,6,7}, {0,1,2,4,5,6,8}, {0,1,2,4,5,6,9}, {0,1,2,4,5,6,10}, {0,1,2,4,5,7,8}, {0,1,2,4,5,7,9}, {0,1,2,4,5,7,10}, {0,1,2,4,5,8,9}, {0,1,2,4,5,8,10}, {0,1,2,4,5,9,10}, {0,1,3,4,5,6,7}, {0,1,3,4,5,6,8}, {0,1,3,4,5,6,9}, {0,1,3,4,5,6,10}, {0,1,3,4,5,7,8}, {0,1,3,4,5,7,9}, {0,1,3,4,5,7,10}, {0,1,3,4,5,8,9}, {0,1,3,4,5,8,10}, {0,1,3,4,5,9,10}, {0,2,3,4,5,6,7}, {0,2,3,4,5,6,8}, {0,2,3,4,5,6,9}, {0,2,3,4,5,6,10}, {0,2,3,4,5,7,8}, {0,2,3,4,5,7,9}, {0,2,3,4,5,7,10}, {0,2,3,4,5,8,9}, {0,2,3,4,5,8,10}, {0,2,3,4,5,9,10}, {0,1,2,3,4,6,7,8,9,10}, {0,1,2,3,5,6,7,8,9,10}, {0,1,2,4,5,6,7,8,9,10}, {0,1,3,4,5,6,7,8,9,10}, {0,2,3,4,5,6,7,8,9,10}, {1,2,3,4,5,6}, {1,2,3,4,5,7}, {1,2,3,4,5,8}, {1,2,3,4,5,9}, {1,2,3,4,5,10}, {1,2,3,4,5,6,7,8,9}, {1,2,3,4,5,6,7,8,10}, {1,2,3,4,5,6,7,9,10}, {1,2,3,4,5,6,8,9,10}, {1,2,3,4,5,7,8,9,10}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19g20g21g22g23g24g25g26g27g28g29g30g31g32g33g34g35g36g37g38g39g40g41g42g43g44g45g46g47g48g49g50g51g52g53g54g55g56g57g58g59g60g61g62g63g64g65g66g67g68g69g70g71g72g73g74g75g76g77g78g79g80g81g82g83g84
o0     1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0
c0     0  0  0  0  0  1  0  0  0  0  1  0  0  0  0  1  1  1  1  0  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  1  1  1  1  0  1  1  1  1  1  1  1  1  1  1
c1     0  0  0  0  0  0  1  0  0  0  0  1  0  0  0  1  1  1  0  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  1  0  1  1  1  1  1  1  1  1  1  1  1
c2     0  0  0  0  0  0  0  1  0  0  0  0  1  0  0  1  1  0  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  0  1  1  1  1  1  1  1  1  1  1  1  1
c3     0  0  0  0  0  0  0  0  1  0  0  0  0  1  0  1  0  1  1  1  1  1  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  0  1  1  1  1  1  1  1  1  1  1  1  1  1
c4     0  0  0  0  0  0  0  0  0  1  0  0  0  0  1  0  1  1  1  1  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  0  1  1  1  1  1  1  1  1  1  1  1  1  1  1
c5     1  0  0  0  0  0  0  0  0  0  1  1  1  1  1  0  0  0  0  0  1  1  1  1  0  0  0  0  0  0  1  1  1  1  0  0  0  0  0  0  1  1  1  1  0  0  0  0  0  0  1  1  1  1  0  0  0  0  0  0  1  1  1  1  0  0  0  0  0  0  1  1  1  1  1  1  0  0  0  0  1  1  1  1  0
c6     0  1  0  0  0  0  0  0  0  0  1  1  1  1  1  0  0  0  0  0  1  0  0  0  1  1  1  0  0  0  1  0  0  0  1  1  1  0  0  0  1  0  0  0  1  1  1  0  0  0  1  0  0  0  1  1  1  0  0  0  1  0  0  0  1  1  1  0  0  0  1  1  1  1  1  0  1  0  0  0  1  1  1  0  1
c7     0  0  1  0  0  0  0  0  0  0  1  1  1  1  1  0  0  0  0  0  0  1  0  0  1  0  0  1  1  0  0  1  0  0  1  0  0  1  1  0  0  1  0  0  1  0  0  1  1  0  0  1  0  0  1  0  0  1  1  0  0  1  0  0  1  0  0  1  1  0  1  1  1  1  1  0  0  1  0  0  1  1  0  1  1
c8     0  0  0  1  0  0  0  0  0  0  1  1  1  1  1  0  0  0  0  0  0  0  1  0  0  1  0  1  0  1  0  0  1  0  0  1  0  1  0  1  0  0  1  0  0  1  0  1  0  1  0  0  1  0  0  1  0  1  0  1  0  0  1  0  0  1  0  1  0  1  1  1  1  1  1  0  0  0  1  0  1  0  1  1  1
c9     0  0  0  0  1  0  0  0  0  0  1  1  1  1  1  0  0  0  0  0  0  0  0  1  0  0  1  0  1  1  0  0  0  1  0  0  1  0  1  1  0  0  0  1  0  0  1  0  1  1  0  0  0  1  0  0  1  0  1  1  0  0  0  1  0  0  1  0  1  1  1  1  1  1  1  0  0  0  0  1  0  1  1  1  1
```


## level-2 / level-4 exhaustive SAT (gap closures)

### 29. S [[8,3,2]]

- output gate: `S0 . S1 . S2`
- ambient qubits: `N=5`; Clifford level: `2`
- provenance: explicit circuit from ansatz-free SAT; archived result: gap_factories.json
- exact T-count: `0`; reduced degree: `1`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{3}, {0,1,2,3}, {4}, {0,1,2,4}, {0,1,3,4}, {0,2,3,4}, {1,2,3,4}, {0,1,2,3,4}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
     g0g1g2g3g4g5g6g7
o0    0 1 0 1 1 1 0 1
o1    0 1 0 1 1 0 1 1
o2    0 1 0 1 0 1 1 1
c0    1 1 0 0 1 1 1 1
c1    0 0 1 1 1 1 1 1
```

### 30. S [[8,4,2]]

- output gate: `S0 . S1 . S2 . S3`
- ambient qubits: `N=6`; Clifford level: `2`
- provenance: explicit circuit from ansatz-free SAT; archived result: gap_factories.json
- exact T-count: `0`; reduced degree: `1`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{1,2,4}, {0,3,4}, {1,2,5}, {0,3,5}, {0,1,2,4,5}, {0,1,3,4,5}, {0,2,3,4,5}, {1,2,3,4,5}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
     g0g1g2g3g4g5g6g7
o0    0 1 0 1 1 1 1 0
o1    1 0 1 0 1 1 0 1
o2    1 0 1 0 1 0 1 1
o3    0 1 0 1 0 1 1 1
c0    1 1 0 0 1 1 1 1
c1    0 0 1 1 1 1 1 1
```

### 31. S [[7,1,3]]

- output gate: `S0`
- ambient qubits: `N=4`; Clifford level: `2`
- provenance: explicit circuit from ansatz-free SAT; archived result: gap_factories.json
- exact T-count: `0`; reduced degree: `1`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{0,1}, {0,2}, {0,1,2}, {3}, {1,3}, {2,3}, {1,2,3}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
     g0g1g2g3g4g5g6
o0    1 1 1 0 0 0 0
c0    1 0 1 0 1 0 1
c1    0 1 1 0 0 1 1
c2    0 0 0 1 1 1 1
```

### 32. S [[15,2,3]]

- output gate: `S0 . S1`
- ambient qubits: `N=6`; Clifford level: `2`
- provenance: explicit circuit from ansatz-free SAT; archived result: gap_factories.json
- exact T-count: `0`; reduced degree: `1`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{0,1,2}, {1,3}, {2,3}, {4}, {1,2,4}, {1,3,4}, {1,2,3,4}, {5}, {2,5}, {0,3,5}, {0,1,2,3,5}, {1,4,5}, {2,4,5}, {3,4,5}, {2,3,4,5}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14
o0     1  0  0  0  0  0  0  0  0  1  1  0  0  0  0
o1     1  1  0  0  1  1  1  0  0  0  1  1  0  0  0
c0     1  0  1  0  1  0  1  0  1  0  1  0  1  0  1
c1     0  1  1  0  0  1  1  0  0  1  1  0  0  1  1
c2     0  0  0  1  1  1  1  0  0  0  0  1  1  1  1
c3     0  0  0  0  0  0  0  1  1  1  1  1  1  1  1
```

### 33. CZ [[15,2,3]]

- output gate: `CZ01`
- ambient qubits: `N=6`; Clifford level: `2`
- provenance: explicit circuit from ansatz-free SAT; archived result: gap_factories.json
- exact T-count: `0`; reduced degree: `2`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{0,1,2}, {1,3}, {0,1,2,3}, {1,4}, {2,4}, {1,3,4}, {1,2,3,4}, {5}, {0,2,5}, {1,3,5}, {0,2,3,5}, {0,4,5}, {0,2,4,5}, {0,3,4,5}, {0,1,2,3,4,5}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14
o0     1  0  1  0  0  0  0  0  1  0  1  1  1  1  1
o1     1  1  1  1  0  1  1  0  0  1  0  0  0  0  1
c0     1  0  1  0  1  0  1  0  1  0  1  0  1  0  1
c1     0  1  1  0  0  1  1  0  0  1  1  0  0  1  1
c2     0  0  0  1  1  1  1  0  0  0  0  1  1  1  1
c3     0  0  0  0  0  0  0  1  1  1  1  1  1  1  1
```

### 34. S [[20,1,4]]

- output gate: `S0`
- ambient qubits: `N=7`; Clifford level: `2`
- provenance: explicit circuit from ansatz-free SAT; archived result: gap_factories.json
- exact T-count: `0`; reduced degree: `1`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{2,3}, {0,1,2,3}, {1,4}, {1,3,4}, {0,5}, {1,2,3,5}, {0,1,4,5}, {1,2,4,5}, {6}, {1,2,6}, {0,3,6}, {2,3,6}, {4,6}, {0,3,4,6}, {0,5,6}, {3,5,6}, {1,3,5,6}, {0,2,3,5,6}, {3,4,5,6}, {2,3,4,5,6}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19
o0     0  1  0  0  1  0  1  0  0  0  1  0  0  1  1  0  0  1  0  0
c0     0  1  1  1  0  1  1  1  0  1  0  0  0  0  0  0  1  0  0  0
c1     1  1  0  0  0  1  0  1  0  1  0  1  0  0  0  0  0  1  0  1
c2     1  1  0  1  0  1  0  0  0  0  1  1  0  1  0  1  1  1  1  1
c3     0  0  1  1  0  0  1  1  0  0  0  0  1  1  0  0  0  0  1  1
c4     0  0  0  0  1  1  1  1  0  0  0  0  0  0  1  1  1  1  1  1
c5     0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1
```

### 35. CZ [[16,2,4]]

- output gate: `CZ01`
- ambient qubits: `N=7`; Clifford level: `2`
- provenance: explicit circuit from ansatz-free SAT; archived result: gap_factories.json
- exact T-count: `0`; reduced degree: `2`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{0,1,5}, {0,1,2,5}, {0,3,5}, {2,3,5}, {4,5}, {0,1,2,4,5}, {3,4,5}, {1,2,3,4,5}, {0,6}, {1,2,6}, {1,3,6}, {2,3,6}, {4,6}, {2,4,6}, {0,3,4,6}, {2,3,4,6}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15
o0     1  1  1  0  0  1  0  0  1  0  0  0  0  0  1  0
o1     1  1  0  0  0  1  0  1  0  1  1  0  0  0  0  0
c0     0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1
c1     0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1
c2     0  0  0  0  1  1  1  1  0  0  0  0  1  1  1  1
c3     1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0
c4     0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1
```

### 36. sqrtT [[30,2,2]]

- output gate: `sqrtT0 . sqrtT1`
- ambient qubits: `N=6`; Clifford level: `4`
- provenance: explicit circuit from ansatz-free SAT; archived result: gap_factories.json
- exact T-count: `None`; reduced degree: `1`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{2}, {0,1,2}, {3}, {0,1,3}, {0,2,3}, {1,2,3}, {4}, {0,1,4}, {0,2,4}, {1,2,4}, {0,3,4}, {1,3,4}, {2,3,4}, {0,1,2,3,4}, {5}, {0,1,5}, {0,2,5}, {1,2,5}, {0,3,5}, {1,3,5}, {2,3,5}, {0,1,2,3,5}, {0,4,5}, {1,4,5}, {2,4,5}, {0,1,2,4,5}, {3,4,5}, {0,1,3,4,5}, {0,2,3,4,5}, {1,2,3,4,5}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19g20g21g22g23g24g25g26g27g28g29
o0     0  1  0  1  1  0  0  1  1  0  1  0  0  1  0  1  1  0  1  0  0  1  1  0  0  1  0  1  1  0
o1     0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1
c0     1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1
c1     0  0  1  1  1  1  0  0  0  0  1  1  1  1  0  0  0  0  1  1  1  1  0  0  0  0  1  1  1  1
c2     0  0  0  0  0  0  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1
c3     0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1
```

### 37. sqrtT [[44,3,2]]

- output gate: `sqrtT0 . sqrtT1 . sqrtT2`
- ambient qubits: `N=7`; Clifford level: `4`
- provenance: explicit circuit from ansatz-free SAT; archived result: gap_factories.json
- exact T-count: `None`; reduced degree: `1`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{0,1,3}, {0,2,3}, {1,2,3}, {0,1,2,3}, {0,1,4}, {2,4}, {0,1,3,4}, {2,3,4}, {1,5}, {0,2,5}, {1,3,5}, {0,2,3,5}, {1,4,5}, {2,4,5}, {1,2,4,5}, {0,1,2,4,5}, {3,4,5}, {0,3,4,5}, {0,1,3,4,5}, {0,2,3,4,5}, {0,6}, {1,2,6}, {0,3,6}, {1,2,3,6}, {0,4,6}, {2,4,6}, {0,2,4,6}, {0,1,2,4,6}, {3,4,6}, {1,3,4,6}, {0,1,3,4,6}, {1,2,3,4,6}, {0,5,6}, {1,5,6}, {0,1,5,6}, {0,1,2,5,6}, {3,5,6}, {2,3,5,6}, {0,2,3,5,6}, {1,2,3,5,6}, {4,5,6}, {0,1,2,4,5,6}, {3,4,5,6}, {0,1,2,3,4,5,6}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19g20g21g22g23g24g25g26g27g28g29g30g31g32g33g34g35g36g37g38g39g40g41g42g43
o0     1  1  0  1  1  0  1  0  0  1  0  1  0  0  0  1  0  1  1  1  1  0  1  0  1  0  1  1  0  0  1  0  1  0  1  1  0  0  1  0  0  1  0  1
o1     1  0  1  1  1  0  1  0  1  0  1  0  1  0  1  1  0  0  1  0  0  1  0  1  0  0  0  1  0  1  1  1  0  1  1  1  0  0  0  1  0  1  0  1
o2     0  1  1  1  0  1  0  1  0  1  0  1  0  1  1  1  0  0  0  1  0  1  0  1  0  1  1  1  0  0  0  1  0  0  0  1  0  1  1  1  0  1  0  1
c0     1  1  1  1  0  0  1  1  0  0  1  1  0  0  0  0  1  1  1  1  0  0  1  1  0  0  0  0  1  1  1  1  0  0  0  0  1  1  1  1  0  0  1  1
c1     0  0  0  0  1  1  1  1  0  0  0  0  1  1  1  1  1  1  1  1  0  0  0  0  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  1  1  1  1
c2     0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1
c3     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1
```

### 38. sqrtT [[31,1,3]]

- output gate: `sqrtT0`
- ambient qubits: `N=6`; Clifford level: `4`
- provenance: explicit circuit from ansatz-free SAT; archived result: gap_factories.json
- exact T-count: `None`; reduced degree: `1`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{1}, {2}, {0,1,2}, {3}, {0,1,3}, {0,2,3}, {1,2,3}, {4}, {0,1,4}, {0,2,4}, {1,2,4}, {0,3,4}, {1,3,4}, {2,3,4}, {0,1,2,3,4}, {5}, {0,1,5}, {0,2,5}, {1,2,5}, {0,3,5}, {1,3,5}, {2,3,5}, {0,1,2,3,5}, {0,4,5}, {1,4,5}, {2,4,5}, {0,1,2,4,5}, {3,4,5}, {0,1,3,4,5}, {0,2,3,4,5}, {1,2,3,4,5}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19g20g21g22g23g24g25g26g27g28g29g30
o0     0  0  1  0  1  1  0  0  1  1  0  1  0  0  1  0  1  1  0  1  0  0  1  1  0  0  1  0  1  1  0
c0     1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1
c1     0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1
c2     0  0  0  1  1  1  1  0  0  0  0  1  1  1  1  0  0  0  0  1  1  1  1  0  0  0  0  1  1  1  1
c3     0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1
c4     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1
```


## level-3 general-target exhaustive SAT (gap closures)

### 39. T^2 [[14,2,2]]

- output gate: `T0 . T1`
- ambient qubits: `N=5`; Clifford level: `3`
- provenance: explicit circuit from ansatz-free SAT; archived result: level3_general_factories.json
- exact T-count: `2`; reduced degree: `1`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{2}, {0,1,2}, {3}, {0,1,3}, {0,2,3}, {1,2,3}, {4}, {0,1,4}, {0,2,4}, {1,2,4}, {0,3,4}, {1,3,4}, {2,3,4}, {0,1,2,3,4}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13
o0     0  1  0  1  1  0  0  1  1  0  1  0  0  1
o1     0  1  0  1  0  1  0  1  0  1  0  1  0  1
c0     1  1  0  0  1  1  0  0  1  1  0  0  1  1
c1     0  0  1  1  1  1  0  0  0  0  1  1  1  1
c2     0  0  0  0  0  0  1  1  1  1  1  1  1  1
```

### 40. CS12·CS13 [[12,3,2]]

- output gate: `CS01 . CS02`
- ambient qubits: `N=6`; Clifford level: `3`
- provenance: explicit circuit from ansatz-free SAT; archived result: level3_general_factories.json
- exact T-count: `4`; reduced degree: `2`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{1,3,4}, {0,1,3,4}, {2,3,4}, {0,2,3,4}, {5}, {0,5}, {1,2,5}, {0,1,2,5}, {3,4,5}, {0,3,4,5}, {1,2,3,4,5}, {0,1,2,3,4,5}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11
o0     0  1  0  1  0  1  0  1  0  1  0  1
o1     1  1  0  0  0  0  1  1  0  0  1  1
o2     0  0  1  1  0  0  1  1  0  0  1  1
c0     1  1  1  1  0  0  0  0  1  1  1  1
c1     1  1  1  1  0  0  0  0  1  1  1  1
c2     0  0  0  0  1  1  1  1  1  1  1  1
```

### 41. CS13·CCZ123 [[12,3,2]]

- output gate: `CS02 . CCZ012`
- ambient qubits: `N=7`; Clifford level: `3`
- provenance: explicit circuit from ansatz-free SAT; archived result: level3_general_factories.json
- exact T-count: `4`; reduced degree: `2`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{1,4,5}, {0,1,4,5}, {1,2,4,5}, {0,1,2,4,5}, {6}, {0,6}, {2,6}, {0,2,6}, {4,5,6}, {0,4,5,6}, {2,4,5,6}, {0,2,4,5,6}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11
o0     0  1  0  1  0  1  0  1  0  1  0  1
o1     1  1  1  1  0  0  0  0  0  0  0  0
o2     0  0  1  1  0  0  1  1  0  0  1  1
c0     0  0  0  0  0  0  0  0  0  0  0  0
c1     1  1  1  1  0  0  0  0  1  1  1  1
c2     1  1  1  1  0  0  0  0  1  1  1  1
c3     0  0  0  0  1  1  1  1  1  1  1  1
```

### 42. T^6 [[26,6,2]]

- output gate: `T0 . T1 . T2 . T3 . T4 . T5`
- ambient qubits: `N=9`; Clifford level: `3`
- provenance: explicit circuit from ansatz-free SAT; archived result: level3_general_factories.json
- exact T-count: `6`; reduced degree: `1`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{6}, {0,1,2,3,4,5,6}, {7}, {0,1,2,3,4,5,7}, {0,6,7}, {1,6,7}, {2,6,7}, {3,6,7}, {4,6,7}, {5,6,7}, {8}, {0,1,2,3,4,5,8}, {0,6,8}, {1,6,8}, {2,6,8}, {3,6,8}, {4,6,8}, {5,6,8}, {0,7,8}, {1,7,8}, {2,7,8}, {3,7,8}, {4,7,8}, {5,7,8}, {6,7,8}, {0,1,2,3,4,5,6,7,8}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19g20g21g22g23g24g25
o0     0  1  0  1  1  0  0  0  0  0  0  1  1  0  0  0  0  0  1  0  0  0  0  0  0  1
o1     0  1  0  1  0  1  0  0  0  0  0  1  0  1  0  0  0  0  0  1  0  0  0  0  0  1
o2     0  1  0  1  0  0  1  0  0  0  0  1  0  0  1  0  0  0  0  0  1  0  0  0  0  1
o3     0  1  0  1  0  0  0  1  0  0  0  1  0  0  0  1  0  0  0  0  0  1  0  0  0  1
o4     0  1  0  1  0  0  0  0  1  0  0  1  0  0  0  0  1  0  0  0  0  0  1  0  0  1
o5     0  1  0  1  0  0  0  0  0  1  0  1  0  0  0  0  0  1  0  0  0  0  0  1  0  1
c0     1  1  0  0  1  1  1  1  1  1  0  0  1  1  1  1  1  1  0  0  0  0  0  0  1  1
c1     0  0  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1
c2     0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1
```


## my experiments: CS+CCZ entangled 5-output factory

### 43. 01·234 [[18,5,2]]

- output gate: `CS01 . CCZ234`
- ambient qubits: `N=7`; Clifford level: `3`
- provenance: explicit circuit from ansatz-free SAT; archived result: my_factories.json
- exact T-count: `9`; reduced degree: `3`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{4,5}, {0,4,5}, {1,4,5}, {0,1,4,5}, {0,6}, {1,6}, {0,1,6}, {2,6}, {3,6}, {2,3,6}, {4,6}, {2,4,6}, {3,4,6}, {2,3,4,6}, {4,5,6}, {0,4,5,6}, {1,4,5,6}, {0,1,4,5,6}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17
o0     0  1  0  1  1  0  1  0  0  0  0  0  0  0  0  1  0  1
o1     0  0  1  1  0  1  1  0  0  0  0  0  0  0  0  0  1  1
o2     0  0  0  0  0  0  0  1  0  1  0  1  0  1  0  0  0  0
o3     0  0  0  0  0  0  0  0  1  1  0  0  1  1  0  0  0  0
o4     1  1  1  1  0  0  0  0  0  0  1  1  1  1  1  1  1  1
c0     1  1  1  1  0  0  0  0  0  0  0  0  0  0  1  1  1  1
c1     0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  1  1
```


## author-supplied: [[43,3,3]] T-count-5 witness (complete n<=44 checks<=7 census; k=3 representative, GL(3,2)-inequivalent to the k=4 T-count-5 entry)

### 44. T0.CS01.CCZ012 [[43,3,3]]

- output gate: `T0 . CS01 . CCZ012`
- ambient qubits: `N=10`; Clifford level: `3`
- provenance: explicit circuit from ansatz-free SAT; archived result: t5_43_3_3.json
- exact T-count: `5`; reduced degree: `2`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{2,3}, {0,1,2,4}, {0,5}, {2,4,5}, {0,2,3,4,5}, {0,2,6}, {1,2,3,6}, {1,2,4,6}, {0,1,2,3,4,6}, {2,5,6}, {2,4,5,6}, {0,7}, {2,3,7}, {0,2,4,7}, {0,5,7}, {1,2,4,5,7}, {0,2,3,4,5,7}, {1,2,6,7}, {1,2,3,6,7}, {0,1,2,4,6,7}, {0,1,2,3,4,6,7}, {0,1,2,5,6,7}, {0,2,4,5,6,7}, {0,1,3,5,8}, {0,3,4,5,8}, {3,6,8}, {1,3,4,5,6,8}, {0,1,3,7,8}, {0,3,4,7,8}, {1,3,4,6,7,8}, {3,5,6,7,8}, {3,4,9}, {3,4,5,9}, {3,6,9}, {3,4,6,9}, {3,5,6,9}, {3,4,5,6,9}, {3,7,9}, {3,5,7,9}, {3,4,6,8,9}, {3,4,5,6,8,9}, {3,4,6,7,8,9}, {3,4,5,6,7,8,9}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19g20g21g22g23g24g25g26g27g28g29g30g31g32g33g34g35g36g37g38g39g40g41g42
o0     0  1  1  0  1  1  0  0  1  0  0  1  0  1  1  0  1  0  0  1  1  1  1  1  1  0  0  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0
o1     0  1  0  0  0  0  1  1  1  0  0  0  0  0  0  1  0  1  1  1  1  1  0  1  0  0  1  1  0  1  0  0  0  0  0  0  0  0  0  0  0  0  0
o2     1  1  0  1  1  1  1  1  1  1  1  0  1  1  0  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
c0     1  0  0  0  1  0  1  0  1  0  0  0  1  0  0  0  1  0  1  0  1  0  0  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1
c1     0  1  0  1  1  0  0  1  1  0  1  0  0  1  0  1  1  0  0  1  1  0  1  0  1  0  1  0  1  1  0  1  1  0  1  0  1  0  0  1  1  1  1
c2     0  0  1  1  1  0  0  0  0  1  1  0  0  0  1  1  1  0  0  0  0  1  1  1  1  0  1  0  0  0  1  0  1  0  0  1  1  0  1  0  1  0  1
c3     0  0  0  0  0  1  1  1  1  1  1  0  0  0  0  0  0  1  1  1  1  1  1  0  0  1  1  0  0  1  1  0  0  1  1  1  1  0  0  1  1  1  1
c4     0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  0  0  0  0  1  1  1  1  0  0  0  0  0  0  1  1  0  0  1  1
c5     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  1  1  1  1
c6     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1
```


## slot ansatz S1+S1+S2+S2 (N=9, most compact CCZ [[47,3,3]])

### 45. CCZ [[47,3,3]]

- output gate: `CCZ012`
- ambient qubits: `N=9`; Clifford level: `3`
- provenance: explicit circuit from ansatz-free SAT; archived result: ccz_47_s1s1s2s2.json
- exact T-count: `7`; reduced degree: `3`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{0,1,2,7}, {0,1,2,8}, {0,1,2,7,8}, {5}, {6}, {0,2,5,7,8}, {0,2,6,7,8}, {1,2,5,6}, {0,2,5,6,7}, {0,2,5,6,8}, {0,5,6,7,8}, {0,1,4}, {0,2,4,7}, {0,2,4,8}, {2,4,7,8}, {0,4,5}, {0,4,6}, {2,4,5,7,8}, {2,4,6,7,8}, {0,2,4,5,6}, {0,1,2,4,5,6,7}, {0,1,2,4,5,6,8}, {1,4,5,6,7,8}, {0,3}, {0,1,2,3,7}, {0,1,2,3,8}, {0,1,2,3,7,8}, {1,3,5}, {1,3,6}, {1,2,3,5,7,8}, {1,2,3,6,7,8}, {3,5,6}, {1,3,5,6,7}, {1,3,5,6,8}, {1,2,3,5,6,7,8}, {0,3,4}, {0,3,4,7}, {0,3,4,8}, {0,1,2,3,4,7,8}, {2,3,4,5}, {2,3,4,6}, {3,4,5,7,8}, {3,4,6,7,8}, {3,4,5,6}, {2,3,4,5,6,7}, {2,3,4,5,6,8}, {1,2,3,4,5,6,7,8}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19g20g21g22g23g24g25g26g27g28g29g30g31g32g33g34g35g36g37g38g39g40g41g42g43g44g45g46
o0     1  1  1  0  0  1  1  0  1  1  1  1  1  1  0  1  1  0  0  1  1  1  0  1  1  1  1  0  0  0  0  0  0  0  0  1  1  1  1  0  0  0  0  0  0  0  0
o1     1  1  1  0  0  0  0  1  0  0  0  1  0  0  0  0  0  0  0  0  1  1  1  0  1  1  1  1  1  1  1  0  1  1  1  0  0  0  1  0  0  0  0  0  0  0  1
o2     1  1  1  0  0  1  1  1  1  1  0  0  1  1  1  0  0  1  1  1  1  1  0  0  1  1  1  0  0  1  1  0  0  0  1  0  0  0  1  1  1  0  0  0  1  1  1
c0     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1
c1     0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1
c2     0  0  0  1  0  1  0  1  1  1  1  0  0  0  0  1  0  1  0  1  1  1  1  0  0  0  0  1  0  1  0  1  1  1  1  0  0  0  0  1  0  1  0  1  1  1  1
c3     0  0  0  0  1  0  1  1  1  1  1  0  0  0  0  0  1  0  1  1  1  1  1  0  0  0  0  0  1  0  1  1  1  1  1  0  0  0  0  0  1  0  1  1  1  1  1
c4     1  0  1  0  0  1  1  0  1  0  1  0  1  0  1  0  0  1  1  0  1  0  1  0  1  0  1  0  0  1  1  0  1  0  1  0  1  0  1  0  0  1  1  0  1  0  1
c5     0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1
```


## author-supplied: [[43,4,3]] T-count-5 witness (complete n<=44 checks<=7 census; representative of the GL(4,2) class {t5-07,08,10})

### 46. T0.CS01.CS02.CS12.CS13.CS23.CCZ012.CCZ013.CCZ023.CCZ123 [[43,4,3]]

- output gate: `T0 . CS01 . CS02 . CS12 . CS13 . CS23 . CCZ012 . CCZ013 . CCZ023 . CCZ123`
- ambient qubits: `N=11`; Clifford level: `3`
- provenance: explicit circuit from ansatz-free SAT; archived result: t5_43_4_3.json
- exact T-count: `5`; reduced degree: `2`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{3,4}, {1,5}, {0,6}, {2,5,6}, {0,2,4,5,6}, {0,1,2,3,7}, {1,2,3,4,7}, {0,3,5,7}, {0,1,4,5,7}, {2,6,7}, {2,5,6,7}, {0,8}, {3,4,8}, {0,3,5,8}, {0,6,8}, {0,1,2,3,5,6,8}, {0,2,4,5,6,8}, {1,7,8}, {1,2,3,4,7,8}, {0,1,2,3,5,7,8}, {0,1,4,5,7,8}, {0,3,6,7,8}, {1,5,6,7,8}, {0,2,3,4,6,9}, {1,2,4,5,6,9}, {4,7,9}, {0,1,3,4,5,6,7,9}, {0,2,3,4,8,9}, {1,2,4,5,8,9}, {0,1,3,4,5,7,8,9}, {4,6,7,8,9}, {4,5,10}, {4,5,6,10}, {4,7,10}, {4,5,7,10}, {4,6,7,10}, {4,5,6,7,10}, {4,8,10}, {4,6,8,10}, {4,5,7,9,10}, {4,5,6,7,9,10}, {4,5,7,8,9,10}, {4,5,6,7,8,9,10}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19g20g21g22g23g24g25g26g27g28g29g30g31g32g33g34g35g36g37g38g39g40g41g42
o0     0  0  1  0  1  1  0  1  1  0  0  1  0  1  1  1  1  0  0  1  1  1  0  1  0  0  1  1  0  1  0  0  0  0  0  0  0  0  0  0  0  0  0
o1     0  1  0  0  0  1  1  0  1  0  0  0  0  0  0  1  0  1  1  1  1  0  1  0  1  0  1  0  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0
o2     0  0  0  1  1  1  1  0  0  1  1  0  0  0  0  1  1  0  1  1  0  0  0  1  1  0  0  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0
o3     1  0  0  0  0  1  1  1  0  0  0  0  1  1  0  1  0  0  1  1  0  1  0  1  0  0  1  1  0  1  0  0  0  0  0  0  0  0  0  0  0  0  0
c0     1  0  0  0  1  0  1  0  1  0  0  0  1  0  0  0  1  0  1  0  1  0  0  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1
c1     0  1  0  1  1  0  0  1  1  0  1  0  0  1  0  1  1  0  0  1  1  0  1  0  1  0  1  0  1  1  0  1  1  0  1  0  1  0  0  1  1  1  1
c2     0  0  1  1  1  0  0  0  0  1  1  0  0  0  1  1  1  0  0  0  0  1  1  1  1  0  1  0  0  0  1  0  1  0  0  1  1  0  1  0  1  0  1
c3     0  0  0  0  0  1  1  1  1  1  1  0  0  0  0  0  0  1  1  1  1  1  1  0  0  1  1  0  0  1  1  0  0  1  1  1  1  0  0  1  1  1  1
c4     0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  0  0  0  0  1  1  1  1  0  0  0  0  0  0  1  1  0  0  1  1
c5     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  1  1  1  1
c6     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1
```


## beyond cyclic/symmetric: odd-order non-cyclic permutation groups (interactive session)

### 47. T [[44,4,3]]

- output gate: `T0 . T1 . T2 . T3`
- ambient qubits: `N=11`; Clifford level: `3`
- provenance: explicit circuit from ansatz-free SAT; archived result: beyond_cyclic_symmetric.json
- exact T-count: `4`; reduced degree: `1`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{0,1,4}, {3,5,6}, {3,5,8}, {3,6,8}, {2,5,6,8}, {4,5,6,8}, {1,7,9}, {1,7,10}, {1,9,10}, {1,5,7,9}, {1,6,7,10}, {1,8,9,10}, {4,5,7,9}, {4,6,7,10}, {4,8,9,10}, {2,6,7,9}, {2,7,8,10}, {2,5,9,10}, {0,1,4,6,7,9}, {0,1,4,7,8,10}, {0,1,4,5,9,10}, {0,1,4,5,6,7,9}, {0,1,4,6,7,8,10}, {0,1,4,5,8,9,10}, {2,5,7,8,9}, {2,5,6,7,10}, {2,6,8,9,10}, {0,6,7,8,9}, {0,5,7,8,10}, {0,5,6,9,10}, {1,5,6,7,8,9}, {1,5,6,7,8,10}, {1,5,6,8,9,10}, {0,1,4,5,6,7,8,9}, {0,1,4,5,6,7,8,10}, {0,1,4,5,6,8,9,10}, {3,7,9,10}, {0,1,4,7,9,10}, {3,5,6,7,9,10}, {3,5,7,8,9,10}, {3,6,7,8,9,10}, {0,1,4,5,6,7,9,10}, {0,1,4,5,7,8,9,10}, {0,1,4,6,7,8,9,10}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19g20g21g22g23g24g25g26g27g28g29g30g31g32g33g34g35g36g37g38g39g40g41g42g43
o0     1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  0  0  0  1  1  1  0  0  0  1  1  1  0  1  0  0  0  1  1  1
o1     1  0  0  0  0  0  1  1  1  1  1  1  0  0  0  0  0  0  1  1  1  1  1  1  0  0  0  0  0  0  1  1  1  1  1  1  0  1  0  0  0  1  1  1
o2     0  0  0  0  1  0  0  0  0  0  0  0  0  0  0  1  1  1  0  0  0  0  0  0  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
o3     0  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  0  1  1  1  0  0  0
c0     1  0  0  0  0  1  0  0  0  0  0  0  1  1  1  0  0  0  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  1  1  1  0  1  0  0  0  1  1  1
c1     0  1  1  0  1  1  0  0  0  1  0  0  1  0  0  0  0  1  0  0  1  1  0  1  1  1  0  0  1  1  1  1  1  1  1  1  0  0  1  1  0  1  1  0
c2     0  1  0  1  1  1  0  0  0  0  1  0  0  1  0  1  0  0  1  0  0  1  1  0  0  1  1  1  0  1  1  1  1  1  1  1  0  0  1  0  1  1  0  1
c3     0  0  0  0  0  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  1  1  1  1  1  1
c4     0  0  1  1  1  1  0  0  0  0  0  1  0  0  1  0  1  0  0  1  0  0  1  1  1  0  1  1  1  0  1  1  1  1  1  1  0  0  0  1  1  0  1  1
c5     0  0  0  0  0  0  1  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  1  1  1  1  1  1  1
c6     0  0  0  0  0  0  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  1  1  1  1  1  1  1  1
```

### 48. T [[52,1,4]]

- output gate: `T0`
- ambient qubits: `N=10`; Clifford level: `3`
- provenance: explicit circuit from ansatz-free SAT; archived result: beyond_cyclic_symmetric.json
- exact T-count: `1`; reduced degree: `1`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{0,1,2,3,4,7}, {0,1,4,5,6,7}, {0,1,2,3,5,8}, {0,2,4,5,6,8}, {0,1,2,3,6,9}, {0,3,4,5,6,9}, {0,1,4,7,8,9}, {0,2,5,7,8,9}, {0,3,6,7,8,9}, {0,3,5,7}, {0,1,6,8}, {0,2,4,9}, {2,3,5,7}, {3,4,5,7}, {1,3,6,8}, {1,5,6,8}, {1,6,7,8}, {1,2,4,9}, {2,4,6,9}, {3,5,7,9}, {2,4,8,9}, {0,2,6,7}, {0,3,4,8}, {0,1,5,9}, {0,1,2,6,7}, {0,2,5,6,7}, {0,2,3,4,8}, {0,3,4,6,8}, {0,3,4,7,8}, {0,1,3,5,9}, {0,1,4,5,9}, {0,2,6,7,9}, {0,1,5,8,9}, {0,2,3,4,6,7}, {0,1,3,4,5,8}, {0,2,3,6,7,8}, {0,2,4,6,7,8}, {0,1,2,5,6,9}, {0,1,2,5,7,9}, {0,1,5,6,7,9}, {0,1,3,4,8,9}, {0,3,4,5,8,9}, {1,3,5,6,7}, {1,2,4,6,8}, {1,3,5,7,8}, {3,5,6,7,8}, {2,3,4,5,9}, {2,3,4,7,9}, {2,4,5,7,9}, {1,2,6,8,9}, {1,4,6,8,9}, {1,2,3,4,5,6,7,8,9}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19g20g21g22g23g24g25g26g27g28g29g30g31g32g33g34g35g36g37g38g39g40g41g42g43g44g45g46g47g48g49g50g51
o0     1  1  1  1  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0
c0     1  1  1  0  1  0  1  0  0  0  1  0  0  0  1  1  1  1  0  0  0  0  0  1  1  0  0  0  0  1  1  0  1  0  1  0  0  1  1  1  1  0  1  1  1  0  0  0  0  1  1  1
c1     1  0  1  1  1  0  0  1  0  0  0  1  1  0  0  0  0  1  1  0  1  1  0  0  1  1  1  0  0  0  0  1  0  1  0  1  1  1  1  0  0  0  0  1  0  0  1  1  1  1  0  1
c2     1  0  1  0  1  1  0  0  1  1  0  0  1  1  1  0  0  0  0  1  0  0  1  0  0  0  1  1  1  1  0  0  0  1  1  1  0  0  0  0  1  1  1  0  1  1  1  1  0  0  0  1
c3     1  1  0  1  0  1  1  0  0  0  0  1  0  1  0  0  0  1  1  0  1  0  1  0  0  0  1  1  1  0  1  0  0  1  1  0  1  0  0  0  1  1  0  1  0  0  1  1  1  0  1  1
c4     0  1  1  1  0  1  0  1  0  1  0  0  1  1  0  1  0  0  0  1  0  0  0  1  0  1  0  0  0  1  1  0  1  0  1  0  0  1  1  1  0  1  1  0  1  1  1  0  1  0  0  1
c5     0  1  0  1  1  1  0  0  1  0  1  0  0  0  1  1  1  0  1  0  0  1  0  0  1  1  0  1  0  0  0  1  0  1  0  1  1  1  0  1  0  0  1  1  0  1  0  0  0  1  1  1
c6     1  1  0  0  0  0  1  1  1  1  0  0  1  1  0  0  1  0  0  1  0  1  0  0  1  1  0  0  1  0  0  1  0  1  0  1  1  0  1  1  0  0  1  0  1  1  0  1  1  0  0  1
c7     0  0  1  1  0  0  1  1  1  0  1  0  0  0  1  1  1  0  0  0  1  0  1  0  0  0  1  1  1  0  0  0  1  0  1  1  1  0  0  0  1  1  0  1  1  1  0  0  0  1  1  1
c8     0  0  0  0  1  1  1  1  1  0  0  1  0  0  0  0  0  1  1  1  1  0  0  1  0  0  0  0  0  1  1  1  1  0  0  0  0  1  1  1  1  1  0  0  0  0  1  1  1  1  1  1
```


## slot ansatz, k=4 subgroup-relaxed geometry (interactive session)

### 49. T [[47,4,3]]

- output gate: `T0 . T1 . T2 . T3`
- ambient qubits: `N=10`; Clifford level: `3`
- provenance: explicit circuit from ansatz-free SAT; archived result: slot_ansatz_k4_c9sub3.json
- exact T-count: `4`; reduced degree: `1`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{0,1,4,5,7}, {0,1,4,7,9}, {0,1,5,6,9}, {0,1,5,7,8}, {0,1,5,8,9}, {0,1,6,7,9}, {0,3,4,5,6,7,9}, {0,3,4,5,7,8,9}, {0,3,5}, {0,3,5,6,7,8,9}, {0,3,7}, {0,3,9}, {0,4,5,6,7,8}, {0,4,5,6,8,9}, {0,4,5,9}, {0,4,6,7,8,9}, {0,5,6,7}, {0,5,7}, {0,5,9}, {0,7,8,9}, {0,7,9}, {1,4,5,6,9}, {1,4,6,9}, {1,4,7,8}, {1,4,7,8,9}, {1,5,6,7,8}, {1,5,6,8}, {1,5,7,9}, {2,4}, {2,4,6}, {2,4,6,8}, {2,4,8}, {2,6}, {2,6,8}, {2,8}, {3,4,5,6}, {3,4,5,6,7}, {3,4,5,8}, {3,4,5,8,9}, {3,4,6,7}, {3,4,8,9}, {3,6,7,8}, {3,6,7,8,9}, {3,6,8,9}, {4,5,7,8}, {4,6,7,9}, {5,6,8,9}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19g20g21g22g23g24g25g26g27g28g29g30g31g32g33g34g35g36g37g38g39g40g41g42g43g44g45g46
o0     1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
o1     1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
o2     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0
o3     0  0  0  0  0  0  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  0  0  0
c0     1  1  0  0  0  0  1  1  0  0  0  0  1  1  1  1  0  0  0  0  0  1  1  1  1  0  0  0  1  1  1  1  0  0  0  1  1  1  1  1  1  0  0  0  1  1  0
c1     1  0  1  1  1  0  1  1  1  1  0  0  1  1  1  0  1  1  1  0  0  1  0  0  0  1  1  1  0  0  0  0  0  0  0  1  1  1  1  0  0  0  0  0  1  0  1
c2     0  0  1  0  0  1  1  0  0  1  0  0  1  1  0  1  1  0  0  0  0  1  1  0  0  1  1  0  0  1  1  0  1  1  0  1  1  0  0  1  0  1  1  1  0  1  1
c3     1  1  0  1  0  1  1  1  0  1  1  0  1  0  0  1  1  1  0  1  1  0  0  1  1  1  0  1  0  0  0  0  0  0  0  0  1  0  0  1  0  1  1  0  1  1  0
c4     0  0  0  1  1  0  0  1  0  1  0  0  1  1  0  1  0  0  0  1  0  0  0  1  1  1  1  0  0  0  1  1  0  1  1  0  0  1  1  0  1  1  1  1  1  0  1
c5     0  1  1  0  1  1  1  1  0  1  0  1  0  1  1  1  0  0  1  1  1  1  1  0  1  0  0  1  0  0  0  0  0  0  0  0  0  0  1  0  1  0  1  1  0  1  1
```


## author-supplied: [[48,4,3]] CS01.CS23 factory (improves on [[63,4,3]])

### 50. 01·23 [[48,4,3]]

- output gate: `CS01 . CS23`
- ambient qubits: `N=11`; Clifford level: `3`
- provenance: explicit circuit from ansatz-free SAT; archived result: cs01_cs23_48_4_3.json
- exact T-count: `6`; reduced degree: `2`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{2,3,4,5}, {2,3,4,6}, {2,3,4,8}, {3,7}, {3,9}, {3,10}, {0,1,4,5,7}, {0,1,4,8,9}, {0,1,4,6,10}, {2,3,4,6,7}, {2,3,4,5,9}, {2,3,4,8,10}, {2,3,5,6,7}, {2,3,5,8,9}, {2,3,6,8,10}, {1,4,5,6,8}, {0,4,7,8}, {0,4,6,9}, {0,4,5,10}, {2,5,7,8}, {2,6,8,9}, {2,5,6,10}, {1,6,7,8}, {1,5,6,9}, {1,5,8,10}, {1,4,5,6,7,8}, {1,4,5,6,8,9}, {1,4,5,6,8,10}, {2,4,5,7,9}, {2,4,6,7,10}, {2,4,8,9,10}, {3,4,6,7,9}, {3,4,7,8,10}, {3,4,5,9,10}, {0,4,7,8,9}, {0,4,5,7,10}, {0,4,6,9,10}, {0,1,4,5,6,7,8,9}, {0,1,4,5,6,7,8,10}, {0,1,4,5,6,8,9,10}, {0,1,7,9,10}, {2,4,5,7,9,10}, {2,4,6,7,9,10}, {2,4,7,8,9,10}, {0,5,6,7,9,10}, {0,5,7,8,9,10}, {0,6,7,8,9,10}, {3,4,5,6,7,8,9,10}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19g20g21g22g23g24g25g26g27g28g29g30g31g32g33g34g35g36g37g38g39g40g41g42g43g44g45g46g47
o0     0  0  0  0  0  0  1  1  1  0  0  0  0  0  0  0  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  0  0  0  1  1  1  0
o1     0  0  0  0  0  0  1  1  1  0  0  0  0  0  0  1  0  0  0  0  0  0  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  1  1  1  1  0  0  0  0  0  0  0
o2     1  1  1  0  0  0  0  0  0  1  1  1  1  1  1  0  0  0  0  1  1  1  0  0  0  0  0  0  1  1  1  0  0  0  0  0  0  0  0  0  0  1  1  1  0  0  0  0
o3     1  1  1  1  1  1  0  0  0  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  1
c0     1  1  1  0  0  0  1  1  1  1  1  1  0  0  0  1  1  1  1  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  0  1  1  1  0  0  0  1
c1     1  0  0  0  0  0  1  0  0  0  1  0  1  1  0  1  0  0  1  1  0  1  0  1  1  1  1  1  1  0  0  0  0  1  0  1  0  1  1  1  0  1  0  0  1  1  0  1
c2     0  1  0  0  0  0  0  0  1  1  0  0  1  0  1  1  0  1  0  0  1  1  1  1  0  1  1  1  0  1  0  1  0  0  0  0  1  1  1  1  0  0  1  0  1  0  1  1
c3     0  0  0  1  0  0  1  0  0  1  0  0  1  0  0  0  1  0  0  1  0  0  1  0  0  1  0  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  1  1  1  1  1  1
c4     0  0  1  0  0  0  0  1  0  0  0  1  0  1  1  1  1  0  0  1  1  0  1  0  1  1  1  1  0  0  1  0  1  0  1  0  0  1  1  1  0  0  0  1  0  1  1  1
c5     0  0  0  0  1  0  0  1  0  0  1  0  0  1  0  0  0  1  0  0  1  0  0  1  0  0  1  0  1  0  1  1  0  1  1  0  1  1  0  1  1  1  1  1  1  1  1  1
c6     0  0  0  0  0  1  0  0  1  0  0  1  0  0  1  0  0  0  1  0  0  1  0  0  1  0  0  1  0  1  1  0  1  1  0  1  1  0  1  1  1  1  1  1  1  1  1  1
```


## slot ansatz, subgroup-relaxed geometries (interactive session)

### 51. 01·23 [[63,4,3]]

- output gate: `CS01 . CS23`
- ambient qubits: `N=13`; Clifford level: `3`
- provenance: explicit circuit from ansatz-free SAT; archived result: slot_ansatz_subgroup_extras.json
- exact T-count: `6`; reduced degree: `2`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{0,1,4,7,10}, {0,1,4,9}, {0,1,6,9,12}, {0,1,6,10}, {0,1,7,12}, {0,4,6,7}, {0,4,6,9}, {0,4,10,12}, {0,4,12}, {0,6,7}, {0,6,10,12}, {0,7,9,10}, {0,7,9,12}, {0,9,10}, {1,4,6,7,9,10}, {1,4,6,7,10}, {1,4,6,7,10,12}, {1,4,6,7,12}, {1,4,6,9,10}, {1,4,6,10}, {1,4,7,9}, {1,4,7,9,10}, {1,4,7,9,10,12}, {1,4,7,9,12}, {1,4,7,10,12}, {1,4,9,10,12}, {1,6,7,9,10}, {1,6,7,10,12}, {1,7,10,12}, {2,3,4,7}, {2,3,4,10}, {2,3,7,10}, {2,4,6,7,9,12}, {2,4,6,9,10,12}, {2,6}, {2,6,7,9,10,12}, {2,6,9}, {2,6,12}, {2,9}, {2,9,12}, {2,12}, {3,4}, {3,4,5,7,8,10}, {3,4,5,7,10,11}, {3,4,7,8,10,11}, {3,5,8}, {3,5,11}, {3,7}, {3,8,11}, {3,10}, {4,5,6,7,8,9,10,12}, {4,5,6,7,9,10,11,12}, {4,6,7,8,9,10,11,12}, {4,6,7,9,10,12}, {4,6,9,12}, {4,6,12}, {5,6,8,9,12}, {5,6,9,11,12}, {6,7,9}, {6,7,9,12}, {6,8,9,11,12}, {6,9,10,12}, {9,10,12}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19g20g21g22g23g24g25g26g27g28g29g30g31g32g33g34g35g36g37g38g39g40g41g42g43g44g45g46g47g48g49g50g51g52g53g54g55g56g57g58g59g60g61g62
o0     1  1  1  1  1  1  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
o1     1  1  1  1  1  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
o2     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
o3     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0
c0     1  1  0  0  0  1  1  1  1  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  0  0  0  1  1  0  1  1  0  0  0  0  0  0  0  1  1  1  1  0  0  0  0  0  1  1  1  1  1  1  0  0  0  0  0  0  0
c1     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  0  1  1  0  0  0  1  1  0  0  0  0  1  1  0  0  0  0  0
c2     0  0  1  1  0  1  1  0  0  1  1  0  0  0  1  1  1  1  1  1  0  0  0  0  0  0  1  1  0  0  0  0  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  0
c3     1  0  0  0  1  1  0  0  0  1  0  1  1  0  1  1  1  1  0  0  1  1  1  1  1  0  1  1  1  1  0  1  1  0  0  1  0  0  0  0  0  0  1  1  1  0  0  1  0  0  1  1  1  1  0  0  0  0  1  1  0  0  0
c4     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  0  1  1  0  0  1  0  1  0  1  0  0  0  1  0  0  0  1  0  0
c5     0  1  1  0  0  0  1  0  0  0  0  1  1  1  1  0  0  0  1  0  1  1  1  1  0  1  1  0  0  0  0  0  1  1  0  1  1  0  1  1  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  0  1  1  1  1  1  1  1
c6     1  0  0  1  0  0  0  1  0  0  1  1  0  1  1  1  1  0  1  1  0  1  1  0  1  1  1  1  1  0  1  1  0  1  0  1  0  0  0  0  0  0  1  1  1  0  0  0  0  1  1  1  1  1  0  0  0  0  0  0  0  1  1
c7     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  0  1  0  1  0  0  1  1  0  0  0  0  1  0  0  1  0  0
c8     0  0  1  0  1  0  0  1  1  0  1  0  1  0  0  0  1  1  0  0  0  0  1  1  1  1  0  1  1  0  0  0  1  1  0  1  0  1  0  1  1  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  0  1  1  1  1
```

### 52. T [[52,1,4]]

- output gate: `T0`
- ambient qubits: `N=10`; Clifford level: `3`
- provenance: explicit circuit from ansatz-free SAT; archived result: slot_ansatz_subgroup_extras.json
- exact T-count: `1`; reduced degree: `1`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{0,1,2}, {0,1,2,3,4}, {0,1,2,3,4,5,6,7,8,9}, {0,1,2,3,7,8}, {0,1,2,4,5,6}, {0,1,2,5,8,9}, {0,1,3,6}, {0,1,4,8}, {0,1,5,6}, {0,1,5,7}, {0,1,5,8,9}, {0,1,7,8,9}, {0,2,3,4,5,8}, {0,2,3,4,8}, {0,2,3,7}, {0,2,4,7}, {0,2,5,6,7}, {0,2,5,6,7,8}, {0,3,7,9}, {0,4,5}, {0,4,5,6,7}, {0,4,5,7,8,9}, {0,4,6,9}, {0,4,8,9}, {0,7,8}, {1,2,3,4,5,6,8,9}, {1,2,3,4,9}, {1,2,3,5,6,7,8,9}, {1,2,3,5,6,8}, {1,2,3,5,6,8,9}, {1,2,4,5,7,8}, {1,3,4}, {1,3,4,6,7,9}, {1,3,5,6}, {1,4,7}, {1,6}, {1,6,7,8,9}, {1,7,9}, {1,9}, {2,3,4,5,6,7,8,9}, {2,3,4,5,6,8,9}, {2,3,5,6,7,8,9}, {2,3,5,7,8,9}, {2,3,7,9}, {2,4,5,6,8,9}, {3,4}, {3,4,5,6,7}, {3,7}, {4,6,7}, {4,6,8,9}, {4,9}, {6,7}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19g20g21g22g23g24g25g26g27g28g29g30g31g32g33g34g35g36g37g38g39g40g41g42g43g44g45g46g47g48g49g50g51
o0     1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
c0     1  1  1  1  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0
c1     1  1  1  1  1  1  0  0  0  0  0  0  1  1  1  1  1  1  0  0  0  0  0  0  0  1  1  1  1  1  1  0  0  0  0  0  0  0  0  1  1  1  1  1  1  0  0  0  0  0  0  0
c2     0  1  1  1  0  0  1  0  0  0  0  0  1  1  1  0  0  0  1  0  0  0  0  0  0  1  1  1  1  1  0  1  1  1  0  0  0  0  0  1  1  1  1  1  0  1  1  1  0  0  0  0
c3     0  1  1  0  1  0  0  1  0  0  0  0  1  1  0  1  0  0  0  1  1  1  1  1  0  1  1  0  0  0  1  1  1  0  1  0  0  0  0  1  1  0  0  0  1  1  1  0  1  1  1  0
c4     0  0  1  0  1  1  0  0  1  1  1  0  1  0  0  0  1  1  0  1  1  1  0  0  0  1  0  1  1  1  1  0  0  1  0  0  0  0  0  1  1  1  1  0  1  0  1  0  0  0  0  0
c5     0  0  1  0  1  0  1  0  1  0  0  0  0  0  0  0  1  1  0  0  1  0  1  0  0  1  0  1  1  1  0  0  1  1  0  1  1  0  0  1  1  1  0  0  1  0  1  0  1  1  0  1
c6     0  0  1  1  0  0  0  0  0  1  0  1  0  0  1  1  1  1  1  0  1  1  0  0  1  0  0  1  0  0  1  0  1  0  1  0  1  1  0  1  0  1  1  1  0  0  1  1  1  0  0  1
c7     0  0  1  1  0  1  0  1  0  0  1  1  1  1  0  0  0  1  0  0  0  1  0  1  1  1  0  1  1  1  1  0  0  0  0  0  1  0  0  1  1  1  1  0  1  0  0  0  0  1  0  0
c8     0  0  1  0  0  1  0  0  0  0  1  1  0  0  0  0  0  0  1  0  0  1  1  1  0  1  1  1  0  1  0  0  1  0  0  0  1  1  1  1  1  1  1  1  1  0  0  0  0  1  1  0
```


## author-supplied: [[47,5,3]] T-count-10 witness (unrestricted output-subspace random search)

### 53. T0.T1.T4.CS01.CS04.CS14.CCZ012.CCZ013.CCZ023.CCZ024.CCZ124.CCZ234 [[47,5,3]]

- output gate: `T0 . T1 . T4 . CS01 . CS04 . CS14 . CCZ012 . CCZ013 . CCZ023 . CCZ024 . CCZ124 . CCZ234`
- ambient qubits: `N=11`; Clifford level: `3`
- provenance: explicit circuit from ansatz-free SAT; archived result: t10_47_5_3.json
- exact T-count: `10`; reduced degree: `3`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{1,4,5}, {0,1,2,3,4,6}, {1,2,3,4,5,6}, {0,7}, {1,3,4,5,7}, {0,3,4,6,7}, {1,5,6,7}, {0,2,3,4,8}, {2,3,4,5,8}, {0,1,3,6,8}, {1,3,5,6,8}, {0,2,4,7,8}, {1,2,3,5,7,8}, {0,1,2,4,6,7,8}, {2,3,5,6,7,8}, {1,2,4,9}, {3,4,5,9}, {0,1,2,3,4,6,9}, {0,1,3,5,6,9}, {0,1,2,7,9}, {0,1,4,5,7,9}, {0,6,7,9}, {0,1,2,3,5,6,7,9}, {0,1,8,9}, {0,2,3,5,8,9}, {4,6,8,9}, {2,5,6,8,9}, {1,4,7,8,9}, {1,2,5,7,8,9}, {1,2,3,6,7,8,9}, {5,6,7,8,9}, {0,1,3,4,10}, {0,5,10}, {1,3,4,6,10}, {1,3,4,5,6,10}, {1,3,4,7,10}, {5,7,10}, {6,7,10}, {5,6,7,10}, {0,8,10}, {0,1,3,4,5,8,10}, {6,8,10}, {5,6,8,10}, {1,3,4,7,8,10}, {5,7,8,10}, {6,7,8,10}, {5,6,7,8,10}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19g20g21g22g23g24g25g26g27g28g29g30g31g32g33g34g35g36g37g38g39g40g41g42g43g44g45g46
o0     0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  0  0  1  1  1  1  1  1  1  1  0  0  0  0  0  0  1  1  0  0  0  0  0  0  1  1  0  0  0  0  0  0
o1     1  1  1  0  1  0  1  0  0  1  1  0  1  1  0  1  0  1  1  1  1  0  1  1  0  0  0  1  1  1  0  1  0  1  1  1  0  0  0  0  1  0  0  1  0  0  0
o2     0  1  1  0  0  0  0  1  1  0  0  1  1  1  1  1  0  1  0  1  0  0  1  0  1  0  1  0  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
o3     0  1  1  0  1  1  0  1  1  1  1  0  1  0  1  0  1  1  1  0  0  0  1  0  1  0  0  0  0  1  0  1  0  1  1  1  0  0  0  0  1  0  0  1  0  0  0
o4     1  1  1  0  1  1  0  1  1  0  0  1  0  1  0  1  1  1  0  0  1  0  0  0  0  1  0  1  0  0  0  1  0  1  1  1  0  0  0  0  1  0  0  1  0  0  0
c0     1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1
c1     0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1
c2     0  0  0  1  1  1  1  0  0  0  0  1  1  1  1  0  0  0  0  1  1  1  1  0  0  0  0  1  1  1  1  0  0  0  0  1  1  1  1  0  0  0  0  1  1  1  1
c3     0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1
c4     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
c5     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1
```


## author-supplied: [[51,5,3]] T^5 factory

### 54. T^5 [[51,5,3]]

- output gate: `T0 . T1 . T2 . T3 . T4`
- ambient qubits: `N=12`; Clifford level: `3`
- provenance: explicit circuit from ansatz-free SAT; archived result: t5_51_5_3.json
- exact T-count: `5`; reduced degree: `1`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{2,5}, {0,6}, {0,7}, {0,9}, {0,6,7}, {0,6,9}, {0,7,9}, {1,5,8}, {1,5,10}, {1,5,11}, {4,5,6,8}, {4,5,9,10}, {4,5,7,11}, {3,5,7,8}, {3,5,6,10}, {3,5,9,11}, {0,6,7,9}, {3,5,6,7,9}, {3,5,8,9}, {3,5,7,10}, {3,5,6,11}, {1,8,10}, {1,8,11}, {1,10,11}, {2,5,8,10}, {2,5,8,11}, {2,5,10,11}, {3,5,6,8,10}, {3,5,7,8,11}, {3,5,9,10,11}, {2,5,7,8,10}, {2,5,8,9,11}, {2,5,6,10,11}, {3,6,7,8,10}, {3,7,8,9,11}, {3,6,9,10,11}, {2,5,8,9,10}, {2,5,6,8,11}, {2,5,7,10,11}, {4,6,8,9,10}, {4,6,7,8,11}, {4,7,9,10,11}, {2,7,8,9,10}, {2,6,8,9,11}, {2,6,7,10,11}, {1,5,8,10,11}, {2,6,8,10,11}, {2,7,8,10,11}, {2,8,9,10,11}, {2,6,7,8,9,10,11}, {4,5,6,7,8,9,10,11}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19g20g21g22g23g24g25g26g27g28g29g30g31g32g33g34g35g36g37g38g39g40g41g42g43g44g45g46g47g48g49g50
o0     0  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
o1     0  0  0  0  0  0  0  1  1  1  0  0  0  0  0  0  0  0  0  0  0  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  0  0  0  0  0
o2     1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  0  0  0  1  1  1  0  0  0  1  1  1  0  0  0  1  1  1  0  1  1  1  1  0
o3     0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  0  1  1  1  1  0  0  0  0  0  0  1  1  1  0  0  0  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
o4     0  0  0  0  0  0  0  0  0  0  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  0  0  0  0  0  0  0  0  1
c0     1  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  0  1  1  1  1  0  0  0  1  1  1  1  1  1  1  1  1  0  0  0  1  1  1  0  0  0  0  0  0  1  0  0  0  0  1
c1     0  1  0  0  1  1  0  0  0  0  1  0  0  0  1  0  1  1  0  0  1  0  0  0  0  0  0  1  0  0  0  0  1  1  0  1  0  1  0  1  1  0  0  1  1  0  1  0  0  1  1
c2     0  0  1  0  1  0  1  0  0  0  0  0  1  1  0  0  1  1  0  1  0  0  0  0  0  0  0  0  1  0  1  0  0  1  1  0  0  0  1  0  1  1  1  0  1  0  0  1  0  1  1
c3     0  0  0  0  0  0  0  1  0  0  1  0  0  1  0  0  0  0  1  0  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  1  1  1  1
c4     0  0  0  1  0  1  1  0  0  0  0  1  0  0  0  1  1  1  1  0  0  0  0  0  0  0  0  0  0  1  0  1  0  0  1  1  1  0  0  1  0  1  1  1  0  0  0  0  1  1  1
c5     0  0  0  0  0  0  0  0  1  0  0  1  0  0  1  0  0  0  0  1  0  1  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  1  1  1  1  1
c6     0  0  0  0  0  0  0  0  0  1  0  0  1  0  0  1  0  0  0  0  1  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  1  1  1  1  1  1
```


## colored-quotient free-relabel search (colored-quotient relabel search) over the CCZ [[47,3,3]] check parent (archived result ccz_47_s1s1s2s2.json)

### 55. CCZ-parent relabel [[47,6,3]]

- output gate: `T0 . T2 . T3 . T4 . CS02 . CS03 . CS04 . CS23 . CS24 . CS34 . CCZ012 . CCZ014 . CCZ015 . CCZ023 . CCZ024 . CCZ025 . CCZ034 . CCZ045 . CCZ123 . CCZ124 . CCZ125 . CCZ234 . CCZ235 . CCZ245`
- ambient qubits: `N=12`; Clifford level: `3`
- provenance: explicit circuit from ansatz-free SAT; archived result: ccz47_relabel_k6_t11.json
- exact T-count: `11`; reduced degree: `3`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{2,3,5,10}, {0,4,11}, {1,2,4,5,10,11}, {1,2,8}, {0,1,3,9}, {0,2,4,8,10,11}, {3,4,9,10,11}, {0,1,2,4,5,8,9}, {1,8,9,10}, {0,2,3,4,8,9,11}, {1,2,3,4,5,8,9,10,11}, {0,1,2,3,4,5,7}, {4,7,10}, {1,4,5,7,11}, {1,2,7,10,11}, {0,2,3,5,7,8}, {0,1,2,3,7,9}, {0,1,4,5,7,8,10,11}, {0,4,7,9,10,11}, {0,1,2,7,8,9}, {0,1,7,8,9,10}, {0,1,7,8,9,11}, {2,3,4,7,8,9,10,11}, {0,1,5,6}, {0,2,3,6,10}, {4,5,6,11}, {1,3,5,6,10,11}, {0,1,2,4,6,8}, {3,4,5,6,9}, {1,2,5,6,8,10,11}, {0,3,6,9,10,11}, {0,1,3,5,6,8,9}, {0,1,5,6,8,9,10}, {2,3,4,5,6,8,9,11}, {6,8,9,10,11}, {0,1,5,6,7}, {0,1,4,6,7,10}, {0,4,5,6,7,11}, {3,4,5,6,7,10,11}, {2,3,4,5,6,7,8}, {2,3,4,5,6,7,9}, {6,7,8,10,11}, {6,7,9,10,11}, {0,3,4,5,6,7,8,9}, {6,7,8,9,10}, {6,7,8,9,11}, {6,7,8,9,10,11}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19g20g21g22g23g24g25g26g27g28g29g30g31g32g33g34g35g36g37g38g39g40g41g42g43g44g45g46
o0     0  1  0  0  1  1  0  1  0  1  0  1  0  0  0  1  1  1  1  1  1  1  0  1  1  0  0  1  0  0  1  1  1  0  0  1  1  1  0  0  0  0  0  1  0  0  0
o1     0  0  1  1  1  0  0  1  1  0  1  1  0  1  1  0  1  1  0  1  1  1  0  1  0  0  1  1  0  1  0  1  1  0  0  1  1  0  0  0  0  0  0  0  0  0  0
o2     1  0  1  1  0  1  0  1  0  1  1  1  0  0  1  1  1  0  0  1  0  0  1  0  1  0  0  1  0  1  0  0  0  1  0  0  0  0  0  1  1  0  0  0  0  0  0
o3     1  0  0  0  1  0  1  0  0  1  1  1  0  0  0  1  1  0  0  0  0  0  1  0  1  0  1  0  1  0  1  1  0  1  0  0  0  0  1  1  1  0  0  1  0  0  0
o4     0  1  1  0  0  1  1  1  0  1  1  1  1  1  0  0  0  1  1  0  0  0  1  0  0  1  0  1  1  0  0  0  0  1  0  0  1  1  1  1  1  0  0  1  0  0  0
o5     1  0  1  0  0  0  0  1  0  0  1  1  0  1  0  1  0  1  0  0  0  0  0  1  0  1  1  0  1  1  0  1  1  1  0  1  0  1  1  1  1  0  0  1  0  0  0
c0     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1
c1     0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1
c2     0  0  0  1  0  1  0  1  1  1  1  0  0  0  0  1  0  1  0  1  1  1  1  0  0  0  0  1  0  1  0  1  1  1  1  0  0  0  0  1  0  1  0  1  1  1  1
c3     0  0  0  0  1  0  1  1  1  1  1  0  0  0  0  0  1  0  1  1  1  1  1  0  0  0  0  0  1  0  1  1  1  1  1  0  0  0  0  0  1  0  1  1  1  1  1
c4     1  0  1  0  0  1  1  0  1  0  1  0  1  0  1  0  0  1  1  0  1  0  1  0  1  0  1  0  0  1  1  0  1  0  1  0  1  0  1  0  0  1  1  0  1  0  1
c5     0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1
```


## automorphism-seeded ansatz: Bravyi-Haah [[49,1,5]] symmetry group (arXiv:1209.2426 App. B), extended search

### 56. T [[48,1,4]]

- output gate: `T0`
- ambient qubits: `N=14`; Clifford level: `3`
- provenance: explicit circuit from ansatz-free SAT; archived result: bh49_automorphism_seeded.json
- exact T-count: `1`; reduced degree: `1`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{0,1,2,4,5}, {0,1,2,8,9}, {0,1,4,8}, {0,1,5}, {0,1,9}, {0,1,10,11}, {0,1,10,11,12,13}, {0,1,10,12}, {0,1,10,13}, {0,1,11,12}, {0,1,11,13}, {0,1,12,13}, {0,2,4,5}, {0,2,8,9}, {0,4,8}, {0,5}, {0,9}, {1}, {1,2,3}, {1,2,3,6,7}, {1,2,4,8}, {1,2,5}, {1,2,6,7}, {1,2,9}, {1,3}, {1,3,6,7}, {1,4,5}, {1,6,7}, {1,8,9}, {1,10}, {1,10,11,12}, {1,10,11,13}, {1,10,12,13}, {1,11}, {1,11,12,13}, {1,12}, {1,13}, {2,3}, {2,3,6,7}, {2,4,8}, {2,5}, {2,6,7}, {2,9}, {3}, {3,6,7}, {4,5}, {6,7}, {8,9}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19g20g21g22g23g24g25g26g27g28g29g30g31g32g33g34g35g36g37g38g39g40g41g42g43g44g45g46g47
o0     1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
c0     1  1  1  1  1  1  1  1  1  1  1  1  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0
c1     1  1  0  0  0  0  0  0  0  0  0  0  1  1  0  0  0  0  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  0  0  0  0  0
c2     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  0  0  0  0  1  1  0  0  0  0  0  0  0  0  0  0  0  1  1  0  0  0  0  1  1  0  0  0
c3     1  0  1  0  0  0  0  0  0  0  0  0  1  0  1  0  0  0  0  0  1  0  0  0  0  0  1  0  0  0  0  0  0  0  0  0  0  0  0  1  0  0  0  0  0  1  0  0
c4     1  0  0  1  0  0  0  0  0  0  0  0  1  0  0  1  0  0  0  0  0  1  0  0  0  0  1  0  0  0  0  0  0  0  0  0  0  0  0  0  1  0  0  0  0  1  0  0
c5     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  0  0  1  0  0  1  0  1  0  0  0  0  0  0  0  0  0  0  1  0  0  1  0  0  1  0  1  0
c6     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  0  0  1  0  0  1  0  1  0  0  0  0  0  0  0  0  0  0  1  0  0  1  0  0  1  0  1  0
c7     0  1  1  0  0  0  0  0  0  0  0  0  0  1  1  0  0  0  0  0  1  0  0  0  0  0  0  0  1  0  0  0  0  0  0  0  0  0  0  1  0  0  0  0  0  0  0  1
c8     0  1  0  0  1  0  0  0  0  0  0  0  0  1  0  0  1  0  0  0  0  0  0  1  0  0  0  0  1  0  0  0  0  0  0  0  0  0  0  0  0  0  1  0  0  0  0  1
c9     0  0  0  0  0  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
c10    0  0  0  0  0  1  1  0  0  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  0  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0
c11    0  0  0  0  0  0  1  1  0  1  0  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  0  1  0  1  1  0  0  0  0  0  0  0  0  0  0  0  0
c12    0  0  0  0  0  0  1  0  1  0  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  0  1  0  1  0  0  0  0  0  0  0  0  0  0  0
```

### 57. T [[49,1,5]]

- output gate: `T0`
- ambient qubits: `N=14`; Clifford level: `3`
- provenance: explicit circuit from ansatz-free SAT; archived result: bh49_automorphism_seeded.json
- exact T-count: `1`; reduced degree: `1`
- verification: all check parities, output gate, and distance re-derived

Columns (qubit supports):

```text
[{0,1,10}, {0,1,11}, {0,1,10,11}, {0,1,12}, {0,1,10,12}, {0,1,11,12}, {0,1,10,11,12}, {0,1,13}, {0,1,10,13}, {0,1,11,13}, {0,1,10,11,13}, {0,1,12,13}, {0,1,10,12,13}, {0,1,11,12,13}, {0,1,10,11,12,13}, {0,3}, {0,1,3}, {0,5}, {0,1,5}, {0,2,5}, {0,1,2,5}, {0,2,6}, {0,1,2,6}, {0,3,6}, {0,1,3,6}, {0,2,7}, {0,1,2,7}, {0,3,7}, {0,1,3,7}, {0,2,6,7}, {0,1,2,6,7}, {0,3,6,7}, {0,1,3,6,7}, {0,4,8}, {0,1,4,8}, {0,2,4,8}, {0,1,2,4,8}, {0,5,8}, {0,1,5,8}, {0,2,5,8}, {0,1,2,5,8}, {0,9}, {0,1,9}, {0,2,9}, {0,1,2,9}, {0,4,9}, {0,1,4,9}, {0,2,4,9}, {0,1,2,4,9}]
```

Binary matrix (outputs `o*`, checks `c*`, rotations `g*`):

```text
      g0 g1 g2 g3 g4 g5 g6 g7 g8 g9g10g11g12g13g14g15g16g17g18g19g20g21g22g23g24g25g26g27g28g29g30g31g32g33g34g35g36g37g38g39g40g41g42g43g44g45g46g47g48
o0     1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1
c0     1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  1
c1     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  0  0  1  1  0  0  1  1  0  0  0  0  1  1  0  0  1  1  0  0  1  1  0  0  1  1
c2     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  0  0  0  0  0  0  1  1  0  0  1  1  0  0  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
c3     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  0  0  0  0  0  0  0  0  1  1  1  1
c4     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  0  0  0  0  0  0  0  0
c5     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  0  0  0  0  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
c6     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
c7     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0
c8     0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  1  1  1  1  1
c9     1  0  1  0  1  0  1  0  1  0  1  0  1  0  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
c10    0  1  1  0  0  1  1  0  0  1  1  0  0  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
c11    0  0  0  1  1  1  1  0  0  0  0  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
c12    0  0  0  0  0  0  0  1  1  1  1  1  1  1  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
```
