# Magic State Factory Search

Code and data for:

> S. Singh, C. Gidney, C. Jones, **"Borrowed Identities: Malleable Distillation Factories and a
> Unified Numerical Search,"** [arXiv:2606.28518](https://arxiv.org/abs/2606.28518) (2026).

We introduce a *borrowed-identity* condition for magic-state distillation factories: a circuit
need only act as the identity on one input state, not the full codespace. The condition holds at
every level of the Clifford hierarchy and turns factory-finding into a search problem. This
repository implements the search, classifies what it finds, and catalogues the results. See the
paper for the theory.

## Repository structure

| folder | contents |
|---|---|
| [`searches/`](searches/) | The three search methods (two-group, symmetry-free, sequential/malleable) and the closed-form family's distance verifier. **[README](searches/README.md)** |
| [`classification/`](classification/) | Turns a factory's gate list into `(degree, essential_dim, t_count, decomposition)`, and reconstructs a factory's explicit circuit or a Quirk link from a catalogue row. **[README](classification/README.md)** |
| [`outputs/`](outputs/) | The factory catalogues (one CSV per level) and raw sweep logs. **[README](outputs/README.md)** |
| [`figures/`](figures/) | Generated plots and Quirk circuit diagrams. **[README](figures/README.md)** |

[`pipeline.ipynb`](pipeline.ipynb), at the root, runs the whole chain: search, classify,
reconstruct a circuit (matrix or Quirk link), re-verify it, or look up a factory already in the
catalogue.

## Main findings

The Clifford-hierarchy level `l` fixes which magic state a factory consumes: `θ=π/2^l`, with
`l=3` the level `T` lives at (full hierarchy table in `searches/README.md`). Numbers below are
combined across `l=2,3,4`.

- **Two-group and symmetry-free together found 22,052 valid borrowed-identity circuits**: 21,920
  from two-group's full sweep (`l∈{2,3,4}`, `k≤7`, `n≤11`, skip parameters `s_total,s_O≤7`, the
  same sweep and count reported in the paper) plus 132 from the symmetry-free search's own sweep
  (`l∈{2,3,4}`, `k≤6`, every output block partition, checks `≤4`). Combined search time under
  three minutes on a laptop: two-group runs in well under a second, symmetry-free (which solves a
  targeted linear system per shape rather than sweeping) takes the remaining ~3 minutes.
  Classifying every distinct shape found (`degree`, `essential_dim`, `t_count`, `decomposition`)
  is a separate, slower step, and is what turns those circuits into the 539 catalogued rows in
  `outputs/factory_catalogue_l{2,3,4}.csv`, including entangled- and mixed-output families no
  single earlier framework reached at once.
- **The results include factories new to the literature**, not one isolated example but a whole
  family at multiple sizes: the `T`-to-`CS` synthillation family `[[6m+6,2m,2]]`, found at both
  `[[18,4,2]]` (`m=2`) and `[[24,6,2]]` (`m=3`); and mixed-output factories with no two-group
  analogue, `[[18,5,2]]` (one `CS` block and one `CCZ` block from a single factory) and
  `[[26,6,2]]` (three output types from one factory). Details in `outputs/README.md`.
- **Checked against a SAT/exhaustive classification's five "SAT-only" `l=3` targets**: of 22,052
  factories found, only **3** are confirmed gaps. A 4th (`[[16,6,2]]`) is dominated by a cheaper
  factory already found here, and a 5th (`[[12,3,2]]a`) is already in the two-group catalogue, a
  false negative from an earlier, looser classification. See `outputs/README.md` for which three
  and by how much.
- **The sequential search finds no new factories.** Every genuinely non-Clifford result it
  produces is already in the two-group catalogue. Its role is the construction behind the paper's
  malleable circuits, one parent circuit with many distillation targets, not a source of new
  records. Details in `searches/README.md`.

## An active, extensible tool

This repository is meant to keep being used, not just to reproduce the paper's figures. The
borrowed-identity condition is written generically in `l`; finding a `Z(π/2^l)`-to-any-`D_l`
magic-state factory at a level or parameter range not yet swept only requires widening the sweep
(see `searches/README.md`).
