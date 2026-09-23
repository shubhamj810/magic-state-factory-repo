# Acceptance boundaries

Every other test directory here asks *are the published results right?* — by
re-deriving each number from raw columns. This one asks the other question:
**what would this repository accept as a result?**

```bash
.venv/bin/python -m unittest discover -s tests -v      # from the repository root
.venv/bin/python verify_repo.py                        # runs this with the rest
```

About twenty-five seconds.

## What is being defended against

Not a malicious file — a **partial or malformed run being taken for a finished
one**. A budget-capped sweep, a hand-off run at too small a width, a capped
group enumeration, a certificate copied from a cluster with a field edited: each
of those is internally consistent, verifies row by row, and is not the claim its
scope string makes.

[`mutation.py`](mutation.py) is the harness. Give it an artifact a boundary
**accepts**; it mutates every field one at a time (deletion, `None`, `1` where a
flag was `true`, `{}` where a digest belongs, `2**63`, a doubled list) and
requires each mutation to be:

| outcome | meaning |
|---|---|
| **rejected** | the default: the field holds up the claim |
| **benign** | declared with a reason: mutating it cannot weaken the claim |
| **tolerated** | the mutation leaves the claim true (a wider sweep still covers the window) |
| **overstating** | the artifact now claims *more*; only re-running the search can refute it |

No mutation may make a validator raise — a check that dies with a `TypeError` has
not rejected anything. The design property is that coverage grows with the
schema: add a field to a certificate and the sweep starts mutating it, and the
suite fails until someone validates it or writes the one-line reason it does not
matter.

## Trust boundaries, stated

[`test_certificate_boundaries.py`](test_certificate_boundaries.py) defines six:
census certificates, `n <= 38` input passes, master-catalogue rows, curated
search rows, symmetry-group files, row-space shard sets. Read its `benign` maps
as the documentation of what is *not* load-bearing — each entry had to be argued
for.

Two limits are recorded there rather than left implicit:

- **A pass that overstates its own sweep is not detectable here.** Coverage is
  read from what the passes say they did, so a file edited to drop its own
  deferral record claims the class it skipped. Only a rerun refutes that, which
  is why the deferral is written by `classify.py` rather than inferred.
- **Regeneration does not certify a group.** With every automorphism group
  truncated to the identity, all 57 rows still "rebuild" — each orbit is a
  singleton. So `rebuild_from_groups.py` checks the completeness flags first.

Baselines are real artifacts wherever one exists: the shipped result passes,
shipped catalogue rows, a genuine census run with its scope fields raised to the
full window. That way the sweep tests the schema the producers actually write.

## The other two files

[`test_exit_codes.py`](test_exit_codes.py) covers the same question through the
CLIs, where automation meets it: **nonzero unless the run answered the question
it was asked.** `UNSAT` is an answer and exits 0; a timeout, a budget cap, or an
unproven optimum is not.

[`test_sk_agreement.py`](test_sk_agreement.py) pins the four independent `S_k`
canonicalisers against each other. The three that name published rows must agree
representative for representative; all four must induce the same partition into
classes. `factorylib/parent.py` orders monomials degree-major and so picks a
different representative of the same orbit — a documented difference, asserted
here so that unifying them has to be a decision rather than an accident.
