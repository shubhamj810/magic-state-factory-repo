# Searches

Three complementary numerical searches for borrowed-identity distillation factories, plus a
closed-form family with no search needed. See the [paper](https://arxiv.org/abs/2606.28518) for
the theory (borrowed-identity condition, Theorems 2/3/5); this file covers how to run each script
and what its parameters mean.

## The Clifford hierarchy, briefly

Each script is parametrized by a level `l`: it searches for factories that consume noisy copies of
the level-`l` magic state `|θ⟩ := |0⟩ + e^(2iθ)|1⟩`, `θ = π/2^l`, and Clifford operations, to
produce `k` higher-fidelity copies at distance `d`.

| `l` | weight-1 gate | weight-2 gate | weight-3 gate | weight-4 gate |
|---|---|---|---|---|
| 2 | `S`  | `CZ`  | —     | —      |
| 3 | `T`  | `CS`  | `CCZ` | —      |
| 4 | `√T` | `CT`  | `CCS` | `CCCZ` |

`l = 3` is where `T` lives; `l = 2` is Clifford; `l ≥ 4` are higher levels. All three scripts below
are written generically in `l`; the Clifford hierarchy level isn't hardcoded anywhere.

## The three searches

| Search | Files | Purpose |
|---|---|---|
| **Two-group** (Sec. IV) | `Two_group.py`, `two_group.ipynb` | The main systematic search. Partitions the `n` circuit qubits into `k` output qubits and `n-k` check qubits, with gate weights compatible with the output/check symmetry (three skip parameters `s_total`, `s_O`, `s_S=1`). Recovers all 21,920 valid `[[N,k,2]]` factories for `l∈{2,3,4}`, `k≤7`, `n≤11`, in well under a second. |
| **Symmetry-free / targeted-output** (App. H) | `symfree_search.py` | Drops the two-group symmetry ansatz and solves the borrowed-identity condition directly for a chosen output block-size partition. Reaches multi-block and mixed-output states, one `CS` block and one `CCZ` block from the same factory, that the symmetric ansatz cannot produce. |
| **Sequential / malleable** (Sec. III) | `sequential.ipynb` | Builds a circuit one step at a time, checking the disentangling condition (Theorem 2) at every intermediate step. This is the construction behind the paper's malleable circuits: a single parent can be stopped early, or extended with a catalytic step, to yield different `(N,k)` factories from the same circuit. |
| Closed-form family (Theorem 3) | `distance_check.py` | Not a search: verifies the true GF(2) distance of the analytic `s=1`/`s=2` symmetric family (`[[2^(l+1)-2,1,2]]`, `[[2^(l+1)-1,1,3]]`) by brute force against the claimed values. |

## Running them

```
python3 searches/Two_group.py        # library module; run via two_group.ipynb, or import directly
jupyter notebook searches/two_group.ipynb
jupyter notebook searches/sequential.ipynb
python3 searches/symfree_search.py   # writes ../figures/block_search_levels.png, reads ../outputs/factory_catalogue_l{2,3,4}.csv
python3 searches/distance_check.py
```

To widen any search past its current swept range (`k≤7, n≤11` for two-group; `n≤8` for sequential;
`k≤6` for symfree), edit the relevant loop bounds (`L_RANGE`, `n_max`, `k_max`) directly. The
condition being checked doesn't change, only how far it's swept. Both scale polynomially in `n`
and `k`, so a factory at larger `k` is reachable by widening the sweep, not by new theory.

## Sequential search: no new factories, but the malleability engine

Running the sequential search exhaustively over `l∈{2,3,4}`, `n≤8`, skip parameters
`s_j∈{1,2,3,4}` per step, and both sign choices, and classifying every result with
`classification/classify.py`: every genuinely non-Clifford result it finds is already found by the
two-group search, at the same `N`. Its only real hits are the `k=2`, degree-1 family `[[6,2,2]]`
(`l=2`, H-code), `[[14,2,2]]` (`l=3`, Bravyi–Haah `k=2`), and `[[30,2,2]]` (`l=4`, same family), all
three independently recovered by two-group already. Zero new `(N,k)` pairs.

That is expected: the sequential ansatz (one anchor plus a higher-weight block per step) is a
strict special case of what the other two searches already cover, so it cannot beat them on
record-setting `(N,k,d)`. Its value is different: it is the construction the paper uses to
demonstrate malleability (Sec. III.c). One parent circuit, stopped at different steps or extended
with a catalytic conversion, yields genuinely distinct factories from the same circuit. The
paper's hand-built example (App. G, a 4-qubit `l=3` parent) yields `[[8,3,2]]→CCZ`,
`[[12,2,2]]→CS`, `[[14,1,2]]→T` this way, plus, via an added catalytic/Hadamard step this notebook
doesn't implement, `[[11,1,2]]→T` and `[[10,2,2]]→T,T`, the only genuinely new factories the
malleable idea produces in the paper. Running `sequential.ipynb` as coded verifies the diagonal
chain is valid at every step, but doesn't reach the catalytic endpoints.

**Caveat if you extend this search:** a term with coefficient nonzero mod `2^l` can still be
Clifford if that coefficient is even mod `2^size`. Check genuineness with
`classification/classify.py`, not a bare "coefficient ≠ 0" test (see that folder's README for why).
