# Outputs

## The catalogues

Two tables hold every factory. Every Quirk link is drawn the same way, using only multi-qubit `Z(pi/2^l)`
parity rotations (no CNOTs or controlled gates): all qubits start in `|0>` and get `H`; each factory gate is one
parity rotation; the Clifford corrections, also written as parity rotations, return the checks to `|+>` (first
row of Bloch spheres); then the output decomposition is undone and a final `H` returns every qubit to `|0>`
(second row of Bloch spheres).

| file | rows | what it lists |
|---|---|---|
| `smallest_per_class.csv` | 186 | the **smallest factory for each output class** (Clifford-reduced decomposition, per `k`), at `l=2,3,4`, with Quirk links. These are the factories quoted in the paper; the paper's Tables SII(a-c) give representatives. |
| `all_factories.csv` | 1,564 | **every distinct factory** the unified search finds (all `n`), at `l=2,3,4`, **without** the Quirk column so it opens directly on GitHub. |
| `all_factories_with_quirk.csv.zip` | 1,564 | the same table **with** a Quirk link per row (about 70 MB unzipped, 1.8 MB zipped). |
| `search_timing.json` | | wall-clock seconds of every stage, and the parameters of the run |
| `literature_refs.json` | | literature references for the paper's table rows, keyed `l,k,n,N`; fills the `reference` column |

`n` is always the number of input magic states and `N` the number of circuit qubits, as in the paper's `[[n,k,d]]`.

### Clifford-equivalent factories are listed separately

In `all_factories.csv`, factories whose outputs are equivalent up to a Clifford circuit share the same
`clifford_class` label (e.g. `L3-007`), and the file is sorted so that each class is contiguous. They are
still **listed as separate rows**, because they are different factories: different `n`, `k` or circuit
size `N`, and different output gates. Two columns tell them apart:

- `raw` is the gate the factory actually deposits on its outputs; `reduced` is its Clifford-reduced class.
- `clifford_padded = yes` means the output is Clifford-equivalent to a state on fewer than `k` qubits
  (it delivers the same magic as a smaller factory, on more wires).

A padded factory adds no distillation power: the smaller factory followed by a CNOT circuit does the same.
It is worth having where that CNOT circuit is expensive, for instance in architectures where logical
Clifford gates are synthesized from multi-step Pauli measurements (such as bivariate-bicycle codes). There
the padded factory delivers the target state directly, spending only magic-state inputs it needs anyway. For
that reason no Clifford-equivalent factory is dropped from `all_factories.csv`.

Every row is distance `d=2` (the distance-3 Reed-Muller factories are not swept here), built only from
`Z(pi/2^l)` parity rotations, and re-verified by brute-force simulation of its phase table.

### How the files were generated (and how to regenerate them for any range)

One command runs the search and writes **both** files, each row with its search stage and Quirk link, plus
`search_timing.json` with the wall-clock time of every stage:

```
python3 searches/unified_search.py --levels 2 3 4 --kmax 6 --nmax 11 --rmax 4 --relabel 4 --sat --sat-time 60
```

Change any parameter and the same two CSVs are produced for that range (use `--out-dir` to keep them apart
from the published ones). `--levels` picks `l`; `--kmax` the number of outputs; `--nmax` the circuit size in
the two-group stage; `--rmax` the check qubits in the gluing stage; `--relabel` the extra output wires
added by Clifford padding; `--sat` adds the optional SAT stage.

The stages: (i) two-group circuits (`Two_group.py`, `s_total, s_O <= 7`; all signs `+1` at `l<=3`, every
check-only sign pattern at `l=4`); (ii) shared-check gluing, output blocks sharing one check register
(`symfree_search.py`'s 2-adic linear solve); (iii) Clifford padding, CNOT relabeling of the output block at
the same `N`; (iv) optional SAT. Classifying each output (Clifford class, distance, z-count) is bookkeeping,
timed separately in `search_timing.json`, and is not needed to find a factory.

## Columns

| column | meaning |
|---|---|
| `clifford_class` | output class label, e.g. `L3-007`; rows sharing it have Clifford-equivalent outputs |
| `l`, `k`, `n`, `N`, `d` | level, output qubits, input magic states, circuit qubits, distance |
| `search_stage` | the stage that found the factory: `two-group`, `gluing` (shared-check gluing), `padding` (Clifford padding) or `SAT` |
| `padded_from` | for `padding` rows, the stage of the circuit that was relabeled (`two-group` or `gluing`) |
| | for `padding` rows, `reduced`, `zcount` and `essential_dim` are those of the circuit that was relabeled: a CNOT relabeling preserves the Clifford class, and the parent's smaller frame is searched exactly. `raw` is the gate the padded factory itself deposits. |
| `params` | stage parameters (`s_total,s_O` for two-group; block partition for gluing; target for SAT) |
| `reduced` | the output up to Clifford equivalence, as a product of generators |
| `raw` | the gate the circuit actually deposits on its outputs |
| `zcount` | exact minimal number of `Z(pi/2^l)` rotations to prepare the output unitarily (blank where not computed) |
| `essential_dim` | output qubits carrying genuine content after Clifford reduction |
| `clifford_padded` | `yes` when `essential_dim < k` |
| `masks` | for `padding` rows, the CNOT relabeling (one bit-mask per new output wire) |
| `reference` | prior construction of the same factory, for the rows in the paper's tables (blank = none known to us) |
| `quirk` | Quirk link of the circuit, drawn as described above (in `all_factories.csv` only inside the zip) |

## Other files

| file | from | what it is |
|---|---|---|
| `l3_k78_targets.csv` | `searches/large_k_sweep.py` | shared-check gluing for every `l=3` target on `k=7,8` outputs |
| `landscape_l3.json`, `landscape_l4.json` | `searches/synthillation_compare.py` | per-target comparison with distilling parts separately and with synthillation (Fig. 1) |
| `large_sweep.csv` | `searches/large_sweep.py` | two-group stage up to `N=16` circuit qubits, `k<=8`: 1,453 verified factories, one per `(l, k, n)`, `n` up to 65,534 (about 2.5 h) |
| `large_sweep_with_quirk.csv.zip` | `searches/large_sweep.py` | the same table with Quirk links for circuits of up to 14 qubits |
| `stage_scaling.json` | `searches/stage_scaling.py` | wall-clock seconds of each stage at `l=3` for `k_max` in {4,6,8} and `N_max` from 6 to 16, with the number of factories per stage (Fig. S2) |
| `error_coefficients.json` | `searches/error_coefficients.py` | for each Fig. 1 target: our `n` and output-error coefficient `c`, and those of the cheapest prior construction, with how it is built (Fig. 1) |
