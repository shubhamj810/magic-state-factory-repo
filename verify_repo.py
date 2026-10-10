#!/usr/bin/env python3
"""Run every fast correctness check in the repository.

This is intentionally a thin standard-library orchestrator: each workflow's
tests run in its own directory, so the command exercises the same imports and
relative paths a reader will use.

A missing solver dependency or an unbuilt catalogue must be a FAILURE, not a
silent skip: several suites guard on ``skipUnless(CATALOG.exists())`` or on
OR-Tools being importable, and ``unittest`` exits 0 when tests are skipped.  So
this script parses each run's summary and refuses to print PASS if anything was
skipped -- otherwise "PASS: ... without skips" would be a claim it never checked.

    python verify_repo.py
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SUITES = (
    ("legacy: exhaustive n<=38", ROOT / "classification" / "legacy" / "exhaustive_n38"),
    ("legacy: rank r<=7", ROOT / "classification" / "legacy" / "rank7_census"),
    ("parent check", ROOT / "parent_first"),
    ("symmetry and SAT", ROOT / "symmetry_sat_search"),
    ("master catalogue", ROOT / "master_catalog"),
    ("borrowed identities", ROOT / "borrowed_identities"),
    ("transversal-T codes", ROOT / "transversal_t_codes"),
    ("community contributions", ROOT / "community_contributions"),
    ("website build", ROOT / "website"),
    ("acceptance boundaries", ROOT),
)


def main() -> int:
    total = 0
    for label, directory in SUITES:
        print(f"\n{'=' * 72}\n{label}: {directory.relative_to(ROOT)}\n{'=' * 72}", flush=True)
        completed = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
            cwd=directory,
            check=False,
            capture_output=True,
            text=True,
        )
        # unittest writes its report to stderr; echo it so -v output is not lost
        sys.stdout.write(completed.stdout)
        sys.stderr.write(completed.stderr)
        sys.stderr.flush()
        if completed.returncode:
            print(f"\nFAILED: {label}", file=sys.stderr)
            return completed.returncode
        report = completed.stderr
        ran = re.search(r"^Ran (\d+) tests?", report, re.M)
        # "Ran 0 tests ... OK" is unittest's report for a suite it could not
        # collect (a renamed directory, an import error swallowed by a loader),
        # and it exits 0.  A suite that ran nothing has verified nothing.
        if ran is None:
            print(f"\nFAILED: {label}: the report has no 'Ran N tests' line, so "
                  f"no test is known to have run", file=sys.stderr)
            return 1
        if int(ran.group(1)) == 0:
            print(f"\nFAILED: {label}: ran 0 tests -- the suite was not "
                  f"collected (check the directory and its test file names)",
                  file=sys.stderr)
            return 1
        total += int(ran.group(1))
        # "OK (skipped=3)" / "... expected failures=1" -- anything but a bare OK
        outcome = re.search(r"^OK(?: \((.*)\))?\s*$", report, re.M)
        if outcome is None:
            print(f"\nFAILED: {label}: no OK summary found in the test report",
                  file=sys.stderr)
            return 1
        if outcome.group(1):
            print(f"\nFAILED: {label}: tests did not all run ({outcome.group(1)}). "
                  f"A skip usually means a generated catalogue is missing (run that "
                  f"directory's build_catalog.py) or a solver is not installed.",
                  file=sys.stderr)
            return 1
    print(f"\nPASS: all {total} tests in every repository suite ran, "
          f"with no skips and no failures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
