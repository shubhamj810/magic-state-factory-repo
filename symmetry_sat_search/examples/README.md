# Curated found factories

[`found_factories.json`](found_factories.json) is the only source file consumed
by `../build_catalog.py`. It contains all 57 retained explicit circuits from
analytic constructions, symmetry-slot searches, ansatz-free SAT searches, and
author-supplied witnesses.

Each row must include:

- identity/provenance: `label`, `target`, `kind`, `group`, `provenance`;
- parameters: `level`, `n`, `k`, `d`, `N`;
- witness: explicit `columns` and the expected `output_gate`.

The builder does not trust the derived fields: it recomputes the output gate,
all check-touching parities, distance, T-count, and reduced degree. A malformed
or incorrect addition aborts without producing a catalogue.

It also rejects a circuit whose declared width is inflated — whose output rows
are linearly dependent modulo the check span. One output CNOT turns a dependent
row into a check-span vector, which carries no monomial of any degree, so the
circuit is really a narrower factory with an idle `|+>` spectator attached: same
`n`, same distance, same exact T-count, more wires. The builder rejects such
rows. Five examples, each with the narrower circuit that dominates it:

| row | effective width | dominated by |
|---|---|---|
| `[[15,2,3]]` `T0.T1.CS01` | 1 | `[[15,1,3]]` `T`, also T-count 1 — its second output row was a verbatim copy of the first over the same check part |
| `[[14,3,2]]` `T1.T2.T3.CS12.CS23.CS13.CCZ123` | 1 | `[[14,1,2]]` `T`, also T-count 1 |
| `[[12,3,2]]` `CS12.CS13.CCZ123` | 2 | `[[12,2,2]]` `CS`, also T-count 3 |
| `[[8,4,2]]` `CCZ123.CCZ124.CCZ134` | 3 | `[[8,3,2]]` `CCZ`, also T-count 7 |
| `[[12,6,2]]` `CCZ123.CCZ124.CCZ125.CCZ135.CCZ136` | 5 | `[[12,5,2]]`, also T-count 11 |

The dominating circuit is in the catalogue in every case: each wide row is the
same resource on a wider output register.

The analytic `T`, `CS` and `CCZ` simplex circuits at `[[14,1,2]]`, `[[12,2,2]]`
and `[[8,3,2]]` are byte-identical to their ansatz-free CP-SAT rediscoveries, so
each is one row whose `provenance` records both routes — the closed form and
the independent search that found the same circuit.

The builder enforces both rules: it rejects a second copy of a circuit
already present at the same level, `k` and distance, and it requires labels to
be unique, since labels are how rows are referenced from the catalogue, the
figures and the theory notes.
