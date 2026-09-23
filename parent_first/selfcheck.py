#!/usr/bin/env python3
"""SELF-CHECK -- run this first, and after any change.

    python selfcheck.py

Checks:

  tests/test_core.py       the F_2 machinery, the GL(k,2) phase-tensor
                           action, and the gate census internals
  tests/test_examples.py   every worked example in README.md, run for real:
                           the kappa/mu/tau numbers quoted there, the cheap
                           filter never claiming a bound tighter than the
                           exact answer it bounds, and the targeted solves


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
    print("parent_first -- self-check")
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
        print("PASS -- the filter chain, the targeted solve and the gate census all behave as documented")
        return 0
    print(f"FAIL -- {len(result.failures)} failure(s), "
          f"{len(result.errors)} error(s). See the trace above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
