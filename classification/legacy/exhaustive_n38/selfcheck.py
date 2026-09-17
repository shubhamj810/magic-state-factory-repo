#!/usr/bin/env python3
"""SELF-CHECK -- run this first, and after any change.

    python selfcheck.py

Checks, in the order a sceptic would want them:

  tests/test_reps.py            the hand-transcribed Nezami--Haah class
                                tables really are triorthogonal supports of
                                the advertised weight, in the advertised
                                numbers
  tests/test_dedup.py           the S_k key behaves as documented, and the
                                S_k / GL(k,2) / same-subspace distinction is
                                exactly as dedup.py claims
  tests/test_classification.py  the classifier reproduces the known counts
                                at the small end, every witness re-verifies,
                                and the independent row-space enumerator
                                agrees -- including on where the two
                                deliberately differ
  tests/test_catalog.py         the shipped catalogue has its headline
                                numbers and every circuit in it re-verifies


Everything here is fast by design (target: under 5 minutes).  It is a correctness
check, not a benchmark: nothing in it re-runs a search that takes longer than a
coffee break.  For the full reproduction path see README.md.

Exit status is 0 only if every check passes.
"""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def main():
    print("=" * 72)
    print("exhaustive_n38 -- self-check")
    print("=" * 72)
    loader = unittest.TestLoader()
    suite = loader.discover(str(HERE / "tests"), pattern="test_*.py",
                            top_level_dir=str(HERE / "tests"))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    print()
    skipped = len(getattr(result, "skipped", []))
    if result.wasSuccessful():
        if skipped:
            # Never let a green banner imply that skipped checks ran.
            print(f"PASS (with {skipped} test(s) SKIPPED -- see the reasons "
                  f"above; usually a missing optional dependency, so the "
                  f"claims those tests back are NOT checked here)")
            for case, reason in result.skipped:
                print(f"    skipped: {case.id().split('.')[-1]}  --  {reason}")
            return 0
        print("PASS -- the input tables, the dedup key, the classifier and the shipped catalogue all check out")
        return 0
    print(f"FAIL -- {len(result.failures)} failure(s), "
          f"{len(result.errors)} error(s). See the trace above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
