# Symmetry-slot and ansatz-free SAT search

This directory contains the two search engines and the catalogue of every
curated example they produced. It makes existence claims—every stored circuit
is verified—but does not claim that an absent factory is impossible unless a
specific SAT run completed with an optimal/UNSAT certificate.

## Files

| file | role |
|---|---|
| [`slot_search.py`](slot_search.py) | CP-SAT search over column orbits of fully symmetric or cyclic check blocks |
| [`exact_d4.py`](exact_d4.py) | exact distance-four CEGAR inside the slot ansatz |
| [`sat_search.py`](sat_search.py) | ansatz-free SAT/CP-SAT over every nonzero column of `F_2^N` |
| [`evaluator.py`](evaluator.py) | solver-independent gate readout, distance, and candidate scoring |
| [`build_catalog.py`](build_catalog.py) | rebuild and verify both catalogue formats from one curated source file |
| [`verify_catalog.py`](verify_catalog.py) | re-derives every published number of the generated JSON from its columns |
| [`symmetry_groups.py`](symmetry_groups.py) | compute each factory's full qubit-permutation automorphism group |
| [`rebuild_from_groups.py`](rebuild_from_groups.py) | discard columns, regenerate them from group orbits, and verify again |
| [`examples/found_factories.json`](examples/found_factories.json) | sole curated source of 57 explicit search/analytic witnesses |
| [`catalog/`](catalog/) | generated human-readable, machine-readable, and symmetry-group catalogues |
| [`selfcheck.py`](selfcheck.py) | run this directory's tests and print one verdict |
| [`tests/`](tests/) | small solver optima plus catalogue and group reconstruction checks |

There are no historical campaign wrappers or raw stdout archives. Stable
engine CLIs replace one-off drivers, and every publishable witness is preserved
as an explicit circuit in `examples/found_factories.json` with its provenance.

## Slot search

The slot ansatz partitions check qubits into blocks and requires selected
columns to be unions of symmetry orbits. `S4` means a four-qubit fully
symmetric block; `C7` means a seven-qubit cyclic block. Blocks can be combined,
for example `S3+C4`.

```bash
../.venv/bin/python slot_search.py \
  --k 2 --target T --geometry S3+S4 \
  --distance 3 --time 120
```

Repeat `--geometry` to compare several ansatzes. The solver minimizes the
number of columns and reports whether the result is proven `OPTIMAL`, merely
`FEASIBLE`, `UNSAT`, or `UNKNOWN`. The expanded circuit is independently
distance- and parity-checked before it is printed.

The exit code distinguishes answers from non-answers. `UNSAT` is an answer --
there is no factory on that geometry -- but `UNKNOWN` means the solve hit
`--time`, and a geometry that ends there, or whose winner fails the independent
check, makes the run exit nonzero. `--time 0` therefore reports `UNKNOWN` and
exits 1 rather than exiting 0 with nothing solved.

Programmatic callers can also supply explicit permutation-group (`P`) blocks;
the compact CLI intentionally exposes only the stable `S` and `C` families.

## Exact distance four in the slot ansatz

```bash
../.venv/bin/python exact_d4.py \
  --k 1 --target T --geometry C9 --time 180
```

The algorithm alternates exact CP-SAT minimization with a fault finder. Every
bad weight-three configuration adds a sound no-good clause. The first optimal
incumbent that passes the independent distance check is therefore the exact
minimum within that geometry.

`--time` bounds ONE CEGAR iteration and up to 4,000 may run, so pass
`--deadline` to bound the whole search; on expiry the geometry reports
`DEADLINE`. Only `OPTIMAL` and `UNSAT` are answers here: exactness is the claim,
so `UNKNOWN`, `ITERCAP`, `DEADLINE`, and a `FEASIBLE` incumbent whose minimality
the solver never proved all exit nonzero, even though a `FEASIBLE` row's columns
are a genuine verified distance-four factory.

## Ansatz-free SAT search

```bash
../.venv/bin/python sat_search.py \
  --k 1 --N 5 --target T --distance 3 --level 3 \
  --backend cpsat --time 120 --output /tmp/factory.json
```

This model has one Boolean variable for every nonzero column in `F_2^N`. It
enforces all target parities through the chosen Clifford level and forbids
undetectable faults below the requested distance. `OPTIMAL` and `UNSAT` are
global certificates at the given `(k,N,target,d,level)`, not ansatz-relative
statements.

The default backend is OR-Tools CP-SAT. Optional `pysat` and `cryptominisat`
backends remain available programmatically when their packages are installed.

Many catalogue rows deposit an entangled gate that no single named target
describes. Ask for one directly with `--target-monomials`, in the same notation
the catalogues print gates in: `'+'`-joined monomials of output-qubit digits.
This reproduces the `[[12,3,2]]` `CS01·CS02` row in well under a second:

```bash
../.venv/bin/python sat_search.py \
  --k 3 --N 6 --target-monomials 01+02 --distance 2 --level 3
```

Only output qubits may appear: a monomial naming a check qubit, or one whose
degree exceeds the Clifford level, is refused rather than solved. Refusing
matters here, because such a target is satisfiable and its solution is not the
factory that was asked for.

## Curating a result

Solver output is scratch data. To publish an example:

1. Inspect the explicit `columns` and solver status.
2. Add one record to `examples/found_factories.json`, retaining a precise
   provenance string and the expected output gate.
3. Run `../.venv/bin/python build_catalog.py`; it treats the new row as
   untrusted and aborts on any shape, parity, gate, distance, or idle-output
   mismatch.
4. Recompute the group and run both independent verifiers.

Required source fields are `label`, `target`, `kind`, `level`, `n`, `k`, `d`,
`N`, `columns`, `group`, `output_gate`, and `provenance`. Existing rows are
concrete schema examples.

## Rebuild and verify

```bash
../.venv/bin/python build_catalog.py
../.venv/bin/python verify_catalog.py
../.venv/bin/python symmetry_groups.py
../.venv/bin/python rebuild_from_groups.py
```

The builder imports no solver. For all 57 rows it checks:

- `n`, `N`, distinct nonempty columns, and no idle declared outputs;
- no *inflated* width either: the output rows must be independent modulo the
  check span. A dependent row is one output CNOT away from an idle `|+>`
  spectator, so such a circuit is a narrower factory on extra wires — same `n`,
  same distance, same T-count — and the builder rejects it rather than
  publishing the larger `k`;
- every check-touching parity through the row's Clifford level;
- the output gate re-derived from output-block parities;
- exact circuit distance through four (`d=5` means the lower bound `d>=5`);
- exact minimal T-count for level-3 gates and reduced polynomial degree.

`verify_catalog.py` checks the generated JSON again — the file a reader actually
consumes — re-deriving every number from the stored columns. It shares
`evaluator` and `factorylib.metrics` with the builder, so it catches a stale,
corrupted or hand-edited catalogue rather than proving two implementations
agree; `rebuild_from_groups.py` is the check that reconstructs the circuits by a
different route before verifying them. `symmetry_groups.py`
computes the complete automorphism group preserving the output block, and
`rebuild_from_groups.py` reconstructs every column set from group generators
and one representative per column orbit.

`symmetry_groups.py` exits nonzero if any enumeration hit `GROUP_CAP`, not only
if a group fails to regenerate its circuit. The two are different claims: a
proper subgroup can regenerate the columns perfectly well, so regeneration
cannot witness that the published `order` really is `|Aut(F)|` — and the file's
`group_definition` says it is. The largest group here is 14,400 against a cap of
2,000,000, so this is a guard on future rows rather than a live constraint.

## Catalogue conventions

The catalogue contains 57 examples: 41 at level 3, nine at level 2, and seven
at level 4. One row is one distinct circuit: labels are unique and a circuit
found by two routes is a single row recording both. Level 2 and level 4 reuse the same parity-column formalism but have
different rotation angles. Exact Clifford+T count is meaningful only at level
3; level-2 rows have T-count zero and level-4 rows report `null`.

See [`catalog/README.md`](catalog/README.md) for the complete generated schema
and [`../REPRODUCING.md`](../REPRODUCING.md) for repository-wide commands.
