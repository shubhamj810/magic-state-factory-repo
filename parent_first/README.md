# Parent-check-first analysis

This directory answers a local question: given a fixed geometry of check
qubits, which output gates can it support at a requested distance?

The expensive check structure is built once, then filtered in three stages:

```text
kappa_d(C)   dimension of the legal quotient V_d(C)
    |
mu_d(C)      largest mutually compatible output subspace
    |
tau_D(C)     largest width carrying the requested target family D
```

If a stage is too small, later searches are impossible and are skipped. Every
budgeted result carries `complete`; a budget hit is never reported as a proof.

## Files

| file | role |
|---|---|
| [`cli.py`](cli.py) | `analyze`, `target`, and `gates` commands |
| [`examples/parent_15_1_3.json`](examples/parent_15_1_3.json) | minimal points-format input example |
| [`selfcheck.py`](selfcheck.py) | run this directory's tests and print one verdict |
| [`tests/`](tests/) | parent algebra, target search, `S_k`/`GL(k,2)` and catalogue examples |
| [`docs/PARENT_CHECK_FIRST.md`](docs/PARENT_CHECK_FIRST.md) | mathematical derivation |

The implementation is [`../factorylib/parent.py`](../factorylib/parent.py),
shared with the rank-7 census. Exact gate metrics are in
[`../factorylib/metrics.py`](../factorylib/metrics.py). This directory stays a
small user-facing CLI rather than carrying private copies of those algorithms.

## Parent inputs

Choose exactly one source:

- `--factory n,k,d` selects a verified witness from
  [`../symmetry_sat_search/catalog/factories.json`](../symmetry_sat_search/catalog/factories.json)
  and discards its output rows to recover the check parent.
- `--input path.json` reads either points or explicit columns.

Points format:

```json
{
  "ambient_rank": 4,
  "points": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
}
```

Columns format:

```json
{
  "k": 1,
  "N": 5,
  "columns": [[0, 1], [0, 2], [0, 1, 2]]
}
```

Qubits `0..k-1` are outputs; only the remaining check components define the
parent.

## Analyse the filter chain

```bash
.venv/bin/python parent_first/cli.py analyze \
  --factory 15,1,3 --node-budget 0
```

Use `--cheap-only` to stop after linear algebra and compatibility-form rank
bounds. This is useful for triaging large parents before exact clique/subspace
enumeration.

Building the parent at all costs `2^kappa` in time and memory, since every coset
representative is tabulated, so a parent whose quotient dimension exceeds
`--max-kappa` (default 21) is refused up front with its `kappa` in the message
rather than allocating until the process dies. Three catalogued factories are
over the line — `--factory 141,2,4` has `kappa = 79` — and `--cheap-only` does
not help, because construction precedes every stage. Raise the flag only if you
mean to spend the memory.

## Search for one target

```bash
.venv/bin/python parent_first/cli.py target \
  --factory 47,3,3 --gate CCZ012 --node-budget 0
```

Gate syntax is a dot-separated product such as `T0.T1.CS01` or `CCZ012`.
`find_target` first applies the dimension and compatibility bounds, then solves
only if the parent survives them. A found witness is reconstructed as explicit
columns and verified.

## Enumerate every gate on a parent

```bash
.venv/bin/python parent_first/cli.py gates \
  --factory 28,2,3 --kmax 2 --dedup symmetric \
  --node-budget 0 --orbit-budget 0
```

`--dedup symmetric` uses output permutations `S_k`, matching both exhaustive
catalogues. `--dedup gl` uses the coarser linear output action. The command
annotates each row with exact minimal T-count and CNOT-frame-reduced degree;
`--no-metrics` skips those annotations.

Idle spectator outputs are excluded by default. Use `--include-spectators`
only when studying circuit representations rather than magic content.

## Output and budgets

Without `--output`, commands print JSON. With `--output`, the path is created
and written atomically at command granularity. `--node-budget 0` and
`--orbit-budget 0` mean unlimited. A finite budget is appropriate for search,
but only `complete=true` supports an exhaustive statement.

## Tests

```bash
.venv/bin/python -m unittest discover -s parent_first/tests -v
```

The examples pin the punctured Reed–Muller parent, the two `[[28,2,3]]`
`S_k` output frames, the difference between `S_k` and `GL(k,2)`, and a targeted
`CCZ` solve.

See [`../REPRODUCING.md`](../REPRODUCING.md) for repository-wide commands.
