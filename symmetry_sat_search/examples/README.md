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
`n`, same distance, same exact T-count, more wires. Five such rows were removed
from this file when the check was added:

| row | effective width | dominated by |
|---|---|---|
| `[[15,2,3]]` `T0.T1.CS01` | 1 | `[[15,1,3]]` `T`, also T-count 1 — its second output row was a verbatim copy of the first over the same check part |
| `[[14,3,2]]` `T1.T2.T3.CS12.CS23.CS13.CCZ123` | 1 | `[[14,1,2]]` `T`, also T-count 1 |
| `[[12,3,2]]` `CS12.CS13.CCZ123` | 2 | `[[12,2,2]]` `CS`, also T-count 3 |
| `[[8,4,2]]` `CCZ123.CCZ124.CCZ134` | 3 | `[[8,3,2]]` `CCZ`, also T-count 7 |
| `[[12,6,2]]` `CCZ123.CCZ124.CCZ125.CCZ135.CCZ136` | 5 | `[[12,5,2]]`, also T-count 11 |

The dominating circuit is in the catalogue in every case, so nothing was lost:
each removed row was the same resource on wider output registers.

Three further rows were **merged** rather than removed. The analytic `T`, `CS`
and `CCZ` simplex circuits at `[[14,1,2]]`, `[[12,2,2]]` and `[[8,3,2]]` turned
out to be byte-identical to their ansatz-free CP-SAT rediscoveries, which had
been catalogued separately as `T (N=4)`, `CS (N=4)` and `CCZ (N=4)`. Each pair
is now one row whose `provenance` records both routes — the closed form and the
independent search that found the same circuit. That is worth knowing about a
circuit, but it is one circuit, so it is one row.

The builder enforces both rules now: it rejects a second copy of a circuit
already present at the same level, `k` and distance, and it requires labels to
be unique, since labels are how rows are referenced from the catalogue, the
figures and the theory notes.
