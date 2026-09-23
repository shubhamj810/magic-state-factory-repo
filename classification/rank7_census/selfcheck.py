#!/usr/bin/env python3
"""SELF-CHECK -- run this first, and after any change.

    python selfcheck.py

Checks:

  tests/test_data.py     the bundled Gillot--Langevin table is byte-identical
                         to the shipped file, parses to 3,486 classes of
                         degree <= 3, and -- the real test -- its orbit sizes
                         sum to 2^64 = |RM(3,7)|, which is what makes the
                         outer enumeration complete
  tests/test_census.py   the engine runs, a budget-limited run is correctly
                         marked incomplete, and every circuit in the shipped
                         census catalogue re-verifies


Everything here is fast by design (target: under 30 seconds).  It is a correctness
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
    print("rank7_census -- self-check")
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
        print("PASS -- the bundled orbit table is intact and complete, and the census catalogue re-verifies")
        return 0
    print(f"FAIL -- {len(result.failures)} failure(s), "
          f"{len(result.errors)} error(s). See the trace above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
