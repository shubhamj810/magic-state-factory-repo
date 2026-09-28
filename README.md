# Magic-state factory protocols: a verified catalogue

This repository is a **catalogue of magic-state distillation factory
protocols**. Each is stored as an explicit circuit, and every number published
about a circuit is re-derived from that circuit, never taken on trust. A distance
a source certifies but that could not be re-measured is printed separately and
marked as such. The protocols come from:

- an **exhaustive classification** of every protocol with up to 54 inputs;
- **AI-assisted and symmetry-constrained searches** for larger and better ones;
- the **published literature**;
- **community contributions** from outside authors, verified to the same bar.

## The database: `master_catalog/`

**[`master_catalog/master_catalog.json`](master_catalog/master_catalog.json) is
the database.** Every row is one factory class and carries its own circuit. It
also records how the class was found, where it came from, and which papers to
cite. [`master_catalog/MASTER_CATALOG.md`](master_catalog/MASTER_CATALOG.md) is
a generated, human-readable view of the same rows.
[`master_catalog/README.md`](master_catalog/README.md) documents the schema, the
verification bar and the merge process.

A factory consumes `n` noisy `T` states and outputs `k` magic qubits. Its
circuit is a list of parity-rotation `columns` over `N` wires: wires `0..k-1`
are the outputs and the rest are postselected checks. `d` is the circuit's
fault distance.

The catalogue holds **804 classes**:

- `n = 15..1715`, `k = 1..373`, `d = 3..7`;
- 217 classes with `n <= 54`, including all 74 Pareto points of the length-54
  classification.

```bash
.venv/bin/python master_catalog/verify_catalog.py            # re-derive every row from its columns
.venv/bin/python master_catalog/merge_results.py new.json    # verify and merge new results (seconds)
.venv/bin/python master_catalog/verify_catalog.py --changed  # re-verify just the rows a merge changed
```

### One row per magic state: the `GL(k,2)` key

The catalogue deduplicates on **`(n, k, d, gate up to GL(k,2))`**, the CNOT+S
output equivalence. Two circuits at the same distance are one row when their
output gates differ only by an invertible change of the output basis (a CNOT
frame) and diagonal Clifford corrections. Such circuits prepare the same magic
state: `T0·T1` and `T0·CS01` are one class. Circuits at different distances are
always different rows.
[`master_catalog/glcanon.py`](master_catalog/glcanon.py) decides the relation;
[`theory/02_classification.md`](theory/02_classification.md) explains it.

## Where the protocols come from

Each row's **regime** says briefly how the class was found. Its **citation**
names the papers that credit it, linked where they are published.

| source | what it contributes | regime(s) |
|---|---|---|
| **Exhaustive classification**, `n <= 54` (Wills, Jain and Singh; [code and theory](https://github.com/AWillsQuantum/generalised_triorthogonal_classification), [data](https://figshare.com/articles/dataset/Generalised_Triorthogonal_Code_Classification_Through_Length_54_Data/33717319)) | every generalised triorthogonal protocol with `n <= 54` and exact `d_Z >= 3`, up to CNOT+S. Its 74 Pareto points (undominated in inputs `n` and wires `N`) are copied in [`classification/length54/`](classification/length54/); a test checks that every other class the catalogue holds in that window is dominated by one | `exhaustive classification n<=54 (Pareto point)`, `exhaustive classification n<=54` |
| **AI-assisted search** (Jain, Wills and Singh) | AI search campaigns run in the companion repository `magic-states-AI`, from punctured simplex and Reed–Muller parents and Wills's parent codes, including the pure-T distillation-exponent (`γ`) frontier, and the public search for generalised triorthogonal protocols at lengths 55–64 | `AI search`, `AI search: …`, `AI search (gamma frontier): …` |
| **Symmetry-constrained SAT search** (same report) | CP-SAT searches over symmetric column orbits and ansatz-free SAT, in [`symmetry_sat_search/`](symmetry_sat_search/). Not counted as an AI discovery | `symmetry-SAT search` |
| **Literature** | published protocols: Bravyi & Kitaev, Nezami & Haah, Haah & Hastings, Jacinto et al., Gong et al., and others | cited in the row's `citations`, linked to the DOI or arXiv page |
| **Community contributions** | protocols from outside authors, verified here; a class new to the catalogue is cited to its contributor | `community contribution` |

A published class is credited to its paper. The rest
of the credit rules are in [`master_catalog/README.md`](master_catalog/README.md).

### Distance-2 factories

This catalogue holds `d ≥ 3` only. Distance-2 factories, and the
borrowed-identity search that finds them at every level of the Clifford
hierarchy, are in
[`shraggy/Magic_state_factory_search`](https://github.com/shraggy/Magic_state_factory_search)
(S. Singh, C. Gidney and C. Jones, *Borrowed Identities: Malleable Distillation
Factories and a Unified Numerical Search*,
[arXiv:2606.28518](https://arxiv.org/abs/2606.28518)).

## Context for AI agents: `agent_context/`

[`agent_context/`](agent_context/) is a self-contained briefing pack for an agent
(or a person) continuing the search. It covers:

- the data model and metrics;
- the rules learned from real mistakes;
- what is closed by theorem and what is still open;
- the verification contract;
- search techniques and their measured costs;
- the history of every campaign, and the baselines a new result must beat.

It was written alongside the AI campaigns in `magic-states-AI` and imported
here. The catalogue says *which* factories exist; the pack says what is known,
what has been tried, and what will fool you. Start with
[`agent_context/README.md`](agent_context/README.md). Its stdlib verifier runs
anywhere:

```bash
python3 agent_context/reference/verify_factory.py --selftest
```

## Contributing protocols: `community_contributions/`

Protocols can be submitted **in any format**: a paper or arXiv link, matrices,
circuits, code, a notebook, or a precise description. Send them as a folder in
[`community_contributions/submissions/`](community_contributions/submissions/)
by pull request, or attach or link them in an issue. Say who to credit and
whether the protocols may be redistributed with the catalogue.

The maintainers then:

1. convert the protocols into the catalogue's input format;
2. verify every protocol to the same bar as a catalogue row, with
   `community_contributions/check_submission.py`;
3. merge them into the master catalogue;
4. cite the contributor on every class new to the catalogue. A class already
   held keeps its credit.

[`community_contributions/README.md`](community_contributions/README.md)
describes what to send and how the maintainers process it.

## Repository map

| path | purpose |
|---|---|
| [`master_catalog/`](master_catalog/) | **the database**, its verifier, merge tool and one-off migrations |
| [`classification/length54/`](classification/length54/) | the length-54 classification's Pareto frontier (byte-identical copy, CC BY 4.0) |
| [`symmetry_sat_search/`](symmetry_sat_search/) | symmetry-slot and ansatz-free SAT search engines and their verified examples |
| [`parent_first/`](parent_first/) | analyse one check parent, target a gate, or enumerate the gates it carries |
| [`agent_context/`](agent_context/) | the context pack for agents continuing the search |
| [`community_contributions/`](community_contributions/) | how outside authors submit protocols, and the tool that checks them |
| [`factorylib/`](factorylib/) | shared parent model, verification and gate metrics |
| [`theory/`](theory/) | mathematical notes, result provenance and figures |
| [`tests/`](tests/) | what the repository would accept as a result: a mutation sweep over every acceptance boundary, and the exit-code contract |

## Setup

Use a fresh Python 3.12 environment; it is the only version the suite has been
run on. The pinned direct dependencies avoid the NumPy/binary-extension ABI
conflicts that installing OR-Tools into an existing Conda base environment
commonly causes.

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

## Verify the repository

```bash
.venv/bin/python verify_repo.py
```

This runs every test suite and prints how many tests each discovered and ran. A
missing solver dependency, a skipped test, or a suite that collected nothing is
reported as a failure rather than hidden. The full row-by-row re-verification of
the database is separate:

```bash
.venv/bin/python master_catalog/verify_catalog.py
```

It takes about fifteen minutes on one core; `--changed` re-verifies only the
rows that differ from the committed catalogue, in seconds.
[`REPRODUCING.md`](REPRODUCING.md) has every rebuild and search command, with
expected outputs and runtimes.

## Data and provenance

- **The length-54 frontier** is copied unmodified from the classification's own
  delivery. Its commit and SHA-256 are in
  [`classification/length54/README.md`](classification/length54/README.md).
- **Third-party data** the repository uses is listed, with its terms, in
  [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
- **Per-row provenance** is in each row's `sources`: the file, record and
  construction every circuit came from. Where each claim is certified is mapped
  in [`theory/PROVENANCE.md`](theory/PROVENANCE.md).
