# Outputs

## The catalogues

`factory_catalogue_l2.csv`, `factory_catalogue_l3.csv`, `factory_catalogue_l4.csv`: one file per
Clifford-hierarchy level `l` (root [README](../README.md) for what `l` means: the level of magic
state the factory consumes, `θ=π/2^l`, with `l=3` the level `T` lives at). Each row is a single
distinct `(N, k, decomposition)` factory recovered by the two-group search
(`searches/Two_group.py`), the symmetry-free search (`searches/symfree_search.py`), or both, then
classified by `classification/classify.py`. Every row is distance `d=2`.

### How the files were generated

Both searches were swept over their full parameter range and every valid result classified;
nothing here is hand-picked. The exact ranges:

**Two-group** (`Two_group.py`'s `find_valid_signs`/`build_gate_set`):
- level `l ∈ {2, 3, 4}`
- output qubits `k ∈ {1, ..., 7}`
- circuit qubits `n ∈ {k+1, ..., 11}` (so `n - k`, the check-qubit count, ranges `1..10`)
- skip parameters `s_total ∈ {1, ..., 7}`, `s_O ∈ {1, ..., 7}` (`s_S` fixed at 1)

This sweep enumerates 21,920 valid `(parameter-tuple, sign)` factories in well under a second on a
laptop: the same sweep, and the same count, reported in the paper. Only the distinct `(l, N, k, d)`
shapes are kept for classification (668 of them across all three levels); the rest are duplicates
of a shape already seen at smaller or equal cost.

**Symmetry-free** (`symfree_search.py`'s `search`/`solve_binding`):
- level `l ∈ {2, 3, 4}`
- output qubits `k ∈ {2, ..., 6}`
- output block-size partition of `k` with each block size `≤ l` (`_partitions(k, l)`)
- check qubits `n - k ∈ {1, ..., 4}`, taking the smallest check count that admits a solution for
  each `(l, k, partition)`

This sweep attempts 132 `(l, k, partition, checks)` combinations and keeps 60 distinct
`(l, k, partition)` shapes that are distance-2 with genuine non-Clifford content, in under 3
minutes, dominated by the linear-algebra solve at larger `k` rather than by breadth: this search is
much narrower than two-group's by design, targeting a chosen output shape rather than sweeping
everything symmetric.

`21,920 + 132 = 22,052` valid borrowed-identity circuits found, in about three minutes of combined
search time, produced these three CSVs. Classification (`classify.classify`, run once per distinct
shape) is a separate, slower step, and is where the `degree`/`essential_dim`/`t_count`/
`decomposition` columns below come from.

## Columns

| column | meaning |
|---|---|
| `N` | input magic states the factory consumes |
| `k` | output qubits |
| `d` | distance (always `2` in these files) |
| `degree` | the Clifford-reduced genuine degree of the deposited output state: the largest group of qubits with a real, non-Clifford, joint dependency, after minimizing over every possible relabeling of the output qubits by a CNOT circuit (`GL(k,2)`). A plain single-qubit `T`/`S`/`√T` factory has degree 1; `CS`-type has degree 2; `CCZ`-type has degree 3; `CCCZ`-type has degree 4. `classification/README.md` explains why this minimization is needed: a naive read of the un-minimized output can report a higher, wrong degree. |
| `essential_dim` | how many of the `k` output qubits carry that genuine content, in the best relabeling found. `essential_dim = k` means every output qubit matters; `essential_dim < k` means the factory is padded: one or more output qubits could be dropped, going to a smaller `k`, without losing anything, since they don't participate in any genuine joint dependency. |
| `t_count` *(only in `factory_catalogue_l3.csv`)* | the exact minimum number of `T`-gates needed to prepare the deposited output state (Reed–Muller minimum-weight-coset decoder, `classification/README.md`). Only meaningful at `l=3`, so this column and the next don't exist at all in the `l=2`/`l=4` files. |
| `t_count_note` *(only in `factory_catalogue_l3.csv`)* | blank except for `k=7` rows, where the exact T-count decoder can't run (it packs `2^k-1` bits into a 64-bit integer, so it's limited to `k≤6`; this note says so instead of silently guessing). |
| `decomposition` | the deposited state's genuine content, written out gate-by-gate with the specific output qubits each gate touches, e.g. `CS01+CS02` (two `CS`-type terms sharing qubit `0`, one connected 3-qubit block) versus `CS01+CS23` (two separate 2-qubit blocks on disjoint qubits). These look similar as an aggregate count but are physically different factories, which is why the qubit indices are spelled out rather than writing `2×CS` for both. A densely entangled block with many simultaneous genuine terms (this happens for some fully-symmetric two-group states at `k≥6`) would be unreadable listed term by term, so it's summarized as `<gate><qubits>(<counts> terms)`, e.g. `CS012345(5 terms)` for a 6-qubit block whose reduction leaves 5 simultaneous genuine pairwise terms. Qubit numbers are positions in the reduced frame found by the classifier (renumbered 0-indexed among just the qubits that survive), not necessarily the original circuit's physical output wires. |
| `n` | total circuit qubits: `k` outputs plus `n-k` check qubits |
| `s_total`, `s_O` | two-group rows only (blank for symmetry-free rows): the two skip parameters passed to `Two_group.py`'s `build_gate_set(k, n-k, s_total, s_O)` that produce this exact row (the third skip parameter, `s_S`, is always fixed at 1 in this search) |
| `parts` | symmetry-free rows only (blank for two-group rows): the output block-size partition passed to `symfree_search.py`'s `solve_binding(parts, n-k, l)` that produces this exact row, written as e.g. `3+2` for the partition `(3, 2)` (one weight-≤3 block, one weight-≤2 block). Two-group has no equivalent column, since its ansatz is always fully symmetric across all `k` outputs at once; there's no block structure to choose. |
| `search` | which search(es) produced this exact `(N, k, decomposition)`: `two-group`, `symmetry-free`, or `two-group + symmetry-free` when both independently found the identical shape |

Every row is self-describing and reproducible from its own columns. For a two-group row,
`(l, n, k, s_total, s_O)` regenerates it; for a symmetry-free row, `(l, parts, n-k)` does:

```
# a two-group row: l=3, n=4, k=2, s_total=1, s_O=1  ([[12,2,2]] CS)
python3 classification/export_circuit.py two-group --l 3 --n 4 --k 2 --s_total 1 --s_O 1

# a symmetry-free row: l=3, parts=3+2, n-k=2  ([[18,5,2]] CS+CCZ)
python3 classification/export_circuit.py symfree --l 3 --parts 3,2 --checks 2
```

`export_circuit.py` also prints `degree`/`essential_dim`/`t_count`/`decomposition` for the
reconstructed circuit, as a check that it matches the CSV row it came from.

## Newly-found factories

The symmetry-free search found factories not previously described in the literature, not one
isolated example but a whole family at multiple sizes:

- **A `T`-to-`CS` synthillation family, `[[6m+6, 2m, 2]]`.** Two members are in
  `factory_catalogue_l3.csv`: `[[18,4,2]]` (`m=2`) and `[[24,6,2]]` (`m=3`), both a single
  entangled block spanning all `k` outputs (`essential_dim = k`). This is the genuinely new
  construction, distinct from a `two-group`-labeled row at the same `(N,k)` that happens to be a
  simpler, less efficient direct sum of independent `CS` pairs. (`m=1`, `[[12,2,2]]`, coincides
  with an already-known factory, so the family is new only starting at `m=2`.)
- **Mixed-output factories from a single circuit.** `[[18,5,2]]` (`CCZ012+CS34`, one `CCZ` block
  and one `CS` block from the same factory) and `[[26,6,2]]` (`CCZ012+CS34+T5`, three output types
  from one factory). The two-group ansatz's full output symmetry structurally cannot produce this;
  it's specific to the symmetry-free search's targeted-block approach.

## Raw sweep logs (not classified)

`output_sequential.txt`, `output_two_group.txt`: captured stdout from running the sequential and
two-group searches directly. These are the unfiltered sweep, before the classification/dedup step
above, useful for seeing every parameter combination tried, including the two-group log's own
"recovery check" cross-referencing named literature factories (H-code, Bravyi–Haah,
Campbell–Howard, etc.) by name.

## The closed-form family (not in these CSVs)

There is a separate, distance-3 closed-form family (Theorem 3) at every level, obtained
analytically for fully symmetric circuits with no search needed, so it isn't in these
sweep-generated catalogues: the quantum Reed–Muller code `[[2^(l+1)-1,1,3]]`, which specializes to
the Steane code `[[7,1,3]]` at `l=2` and the classic `15→1` T-distillation factory `[[15,1,3]]` at
`l=3`. Verified by brute-force GF(2) distance in `searches/distance_check.py`.

## Distance-2 factories a SAT/exhaustive search finds that these two don't

A prior audit of this repository, cross-checked against a SAT/exhaustive classification, flagged
five specific `l=3` distance-2 factories as reachable only by SAT search. Re-checked here with
`classify.py` (the same `essential_dim`/`degree`/`decomposition` signature that audit used), out of
the 22,052 factories the two searches above found combined:

`[[12,3,2]]a` (essential_dim 3, degree 2, `CS01+CS02`) is a false negative, not a gap: two-group
finds it exactly (`l=3 n=5 k=3 s_total=2 s_O=1`, `t_count=4`). It isn't a very good factory either
way: `[[12,2,2]]`, also found here, gets the same degree-2 content at the same `N=12` with one
fewer output qubit and one fewer T-state (`t_count=3`); `[[12,3,2]]a`'s third qubit is entangled
but doesn't add anything `[[12,2,2]]` doesn't already provide.

`[[16,6,2]]` (essential_dim 6, degree 3, a single connected 6-qubit `CCZ`-type block) isn't worth
chasing: the symmetry-free search already gets the same degree-3 content on 6 outputs more cheaply
(`N=14`) by depositing it as two independent `CCZ` blocks instead of one entangled one. `16 > 14`,
so even reaching the entangled version wouldn't be an improvement.

Three are genuine gaps, real structure that neither search here reaches, out of the tens of
thousands of parameter combinations tried:
- `[[16,4,2]]` (essential_dim 4, degree 2, `CS`) beats this repo's best single-block `CS` factory
  at `k=4` (`N=18`) by 2.
- `[[16,5,2]]` (essential_dim 5, degree 2, `CS`) beats this repo's best single-block `CS` factory
  at `k=5` (`N=105`) by nearly 7×.
- `[[12,6,2]]` (essential_dim 5, degree 3, `CCZ`, padded to `k=6`) beats this repo's best
  single-block `CCZ` factory at `k=6` (`N=124`) by over 10×, and beats the `2×CCZ` direct-sum
  factory above (`N=14`) by 2.

Closing that gap needs a genuinely different search, not more sweeping of the ranges already
covered here. A small, specific miss against an exhaustive/SAT method, not a broad one: a few
minutes of two-group and symmetry-free search already cover most of the reachable space.
