"""The exit-code contract, checked through the CLIs a script would actually run.

A status printed on stdout protects a reader; only the exit code protects a
`&&`-chain, a cluster job, or a CI step.  Three audits found commands that
printed `UNKNOWN`, `complete=false` or `FEASIBLE` and exited 0, so the rule is
stated here once and tested end to end: **nonzero unless the run answered the
question it was asked.**

`UNSAT` is an answer -- "no factory on this geometry" -- and exits 0.  A timeout,
a budget cap, a capped enumeration, or an unproven optimum is not, and exits
nonzero unless the caller explicitly asked for a partial run.

Only fast commands are here.  The slower contracts are unit-tested where they
live: `hard_parent_n31.py --kmax 4` in `classification/exhaustive_n38/tests`,
the shard merge in the same place, and the capped automorphism run in
`symmetry_sat_search/tests`.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: The interpreter running this suite, and nothing cleverer.  Preferring
#: `.venv/bin/python` when that path happens to exist meant a stale venv could
#: hijack a run deliberately launched under conda, tox or CI -- so the tests
#: would report on an environment nobody asked for.  If the running interpreter
#: lacks OR-Tools, that is an environment problem and must surface as one.
PYTHON = sys.executable


class TestExitCodes(unittest.TestCase):

    def run_cli(self, *args, expect):
        command = [PYTHON, *(str(a) for a in args)]
        completed = subprocess.run(command, cwd=ROOT, capture_output=True,
                                   text=True, timeout=300)
        self.assertEqual(
            completed.returncode, expect,
            f"{' '.join(command[1:])}\nexpected exit {expect}, got "
            f"{completed.returncode}\n--- stdout ---\n{completed.stdout[-2000:]}"
            f"\n--- stderr ---\n{completed.stderr[-2000:]}")
        return completed

    # ------------------------------------------------ census completeness
    def test_a_capped_census_exits_nonzero(self):
        """The documented smoke run is deliberately incomplete."""
        with tempfile.TemporaryDirectory() as tmp:
            self.run_cli(
                ROOT / "classification" / "rank7_census" / "cli.py", "census",
                "--class-index", 306, "--max-parents", 1, "--kmax", 1,
                "--output", Path(tmp) / "census.json", expect=1)

    def test_a_capped_census_exits_zero_when_that_was_asked_for(self):
        with tempfile.TemporaryDirectory() as tmp:
            completed = self.run_cli(
                ROOT / "classification" / "rank7_census" / "cli.py", "census",
                "--class-index", 306, "--max-parents", 1, "--kmax", 1,
                "--allow-incomplete",
                "--output", Path(tmp) / "census.json", expect=0)
        self.assertIn("complete=false", completed.stdout,
                      "the flag must not change what is REPORTED, only the exit")

    def test_the_orbit_table_check_exits_zero(self):
        """A control: the boundary is 'unanswered', not 'ran at all'."""
        self.run_cli(ROOT / "classification" / "rank7_census" / "cli.py",
                     "data-check", expect=0)

    # ------------------------------------------------------- slot search
    def test_a_timed_out_slot_search_exits_nonzero(self):
        self.run_cli(ROOT / "symmetry_sat_search" / "slot_search.py",
                     "--k", 1, "--target", "T", "--geometry", "S4+C7",
                     "--time", 0, expect=1)

    def test_an_unsat_slot_search_exits_zero(self):
        """UNSAT is an answer: there is no such factory on that geometry."""
        self.run_cli(ROOT / "symmetry_sat_search" / "slot_search.py",
                     "--k", 1, "--target", "T", "--geometry", "S3",
                     "--time", 30, expect=0)

    def test_a_solved_slot_search_exits_zero(self):
        """The documented example, which must stay a working command."""
        self.run_cli(ROOT / "symmetry_sat_search" / "slot_search.py",
                     "--k", 1, "--target", "T", "--geometry", "S4+C7",
                     "--time", 60, expect=0)

    # -------------------------------------------------- input validation
    def test_an_impossible_target_width_is_a_usage_error(self):
        """`--k 1 --target CS` asked for CS on a check qubit and got OPTIMAL."""
        for script in ("sat_search.py", "slot_search.py", "exact_d4.py"):
            with self.subTest(script=script):
                args = [ROOT / "symmetry_sat_search" / script,
                        "--k", 1, "--target", "CS"]
                args += (["--N", 5] if script == "sat_search.py"
                         else ["--geometry", "C9", "--time", 1])
                self.run_cli(*args, expect=2)      # argparse usage error

    def test_a_custom_target_on_a_check_qubit_is_a_usage_error(self):
        self.run_cli(ROOT / "symmetry_sat_search" / "sat_search.py",
                     "--k", 1, "--N", 5, "--target-monomials", "0+01",
                     expect=2)

    def test_a_custom_target_on_outputs_is_accepted(self):
        """The catalogue-notation path must still work: [[12,3,2]] CS01·CS02."""
        completed = self.run_cli(
            ROOT / "symmetry_sat_search" / "sat_search.py",
            "--k", 3, "--N", 6, "--target-monomials", "01+02",
            "--distance", 2, "--time", 120, expect=0)
        self.assertIn("[[12,3,2]]", completed.stdout)


if __name__ == "__main__":
    unittest.main()
