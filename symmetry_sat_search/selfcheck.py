#!/usr/bin/env python3
"""SELF-CHECK -- run this first, and after any change.

    python selfcheck.py

Checks:

  tests/test_search_engines.py   both engines are re-run from scratch on the
                                 smallest cases and must return the known
                                 optima -- including reporting UNSAT where
                                 nothing exists
  tests/test_slot_search_rm.py   the Reed--Muller slot-pruning regression
  tests/test_catalog.py          every catalogued factory re-verifies along
                                 an independent code path, and every one of
                                 them regenerates from its stored symmetry
                                 group alone


Everything here is fast by design (target: under 60 seconds).  It is a correctness
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
    print("symmetry_sat_search -- self-check")
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
        print("PASS -- both engines reproduce their optima and all 57 catalogued factories re-verify")
        return 0
    print(f"FAIL -- {len(result.failures)} failure(s), "
          f"{len(result.errors)} error(s). See the trace above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
