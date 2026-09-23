"""What the builder must REFUSE, not what it accepts.

A catalogue can be internally perfect and still be wrong, by being built from a
subset of the sweep.  Every check here is a case that once passed silently:

  * a `hard_parent_n31.py --kmax 4` hand-off, which finishes cleanly, writes a
    self-consistent file, and leaves the unique [[31,5,3]] class -- the widest
    factory in the window -- out of the catalogue with `max_k` quietly at 4;
  * a missing ladder pass, so a length is never swept at width 4;
  * a class one pass deferred that no other pass picked up.

The row-space audit's shard bookkeeping is here too: `manifest` and `merge` have
to agree about what the task list IS, or following the documented workflow
exactly produces `complete: false`.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parents[2]))

import build_catalog as B                                      # noqa: E402
from classify_rowspace import ROWSPACE_NS, manifest_tasks       # noqa: E402
from nezami_haah_reps import VALID_NS                           # noqa: E402


def _write(directory, name, blob):
    path = Path(directory) / name
    path.write_text(json.dumps(blob), encoding="utf-8")
    return str(path)


def _ladder_pass(ns, kmax=B.LADDER_KMAX, complete=True, deferred=None):
    return {"complete": complete, "kmax": kmax, "ns_swept": sorted(ns),
            "deferred_ns": {str(n): sorted(v) for n, v in (deferred or {}).items()},
            "factories": []}


def _hard_parent(kmax=B.HARD_PARENT_KMAX, complete=True):
    return {"kmax": kmax, "complete": complete, "factories": []}


class TestValidateInputs(unittest.TestCase):
    """`validate_inputs` decides whether a build may claim the window."""

    def _problems(self, files):
        return B.validate_inputs(files)

    def test_the_shipped_input_set_is_accepted(self):
        """The real files must pass, or every other case here proves nothing."""
        files = [str(p) for p in sorted(B.RESULTS.glob("*.json"))
                 if "certificate" not in p.name]
        self.assertTrue(files, "no result passes in results/")
        self.assertEqual(self._problems(files), [])

    def test_a_narrow_hard_parent_run_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            files = [
                _write(tmp, "hard_parent_n31.json", _hard_parent(kmax=4)),
                _write(tmp, "quotient_catalog_k4.json", _ladder_pass(VALID_NS)),
            ]
            problems = self._problems(files)
        self.assertTrue(any("kmax=4" in p for p in problems), problems)

    def test_a_narrow_hard_parent_run_is_refused_even_if_complete_is_forged(self):
        """The kmax check is independent of the flag, so editing one is not enough."""
        with tempfile.TemporaryDirectory() as tmp:
            files = [
                _write(tmp, "hard_parent_n31.json",
                       _hard_parent(kmax=4, complete=True)),
                _write(tmp, "quotient_catalog_k4.json", _ladder_pass(VALID_NS)),
            ]
            problems = self._problems(files)
        self.assertTrue(any("kmax=4" in p for p in problems), problems)

    def test_a_missing_hard_parent_hand_off_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            files = [_write(tmp, "quotient_catalog_k4.json",
                            _ladder_pass(VALID_NS))]
            problems = self._problems(files)
        self.assertTrue(any("hard_parent_n31.json is missing" in p
                            for p in problems), problems)

    def test_a_missing_length_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            files = [
                _write(tmp, "hard_parent_n31.json", _hard_parent()),
                _write(tmp, "quotient_catalog_k4.json",
                       _ladder_pass(n for n in VALID_NS if n != 38)),
            ]
            problems = self._problems(files)
        self.assertTrue(any("n=38" in p for p in problems), problems)

    def test_a_narrow_ladder_pass_is_refused(self):
        """kmax=3 everywhere: every length loses its width-4 sweep.

        n=31 is flagged too, and for the sharper reason: the hand-off sweeps it
        at width 5, but only for class 0, so the other nine classes there are as
        uncovered as any other length.
        """
        with tempfile.TemporaryDirectory() as tmp:
            files = [
                _write(tmp, "hard_parent_n31.json", _hard_parent()),
                _write(tmp, "quotient_catalog_k3.json",
                       _ladder_pass(VALID_NS, kmax=3)),
            ]
            problems = self._problems(files)
        flagged = {int(p.split("=")[1].split(":")[0]) for p in problems}
        self.assertEqual(flagged, set(VALID_NS), problems)
        n31 = next(p for p in problems if p.startswith("n=31"))
        self.assertIn("classes [1, 2, 3, 4, 5, 6, 7, 8, 9]", n31,
                      "class 0 at n=31 is covered by the hand-off")

    def test_a_truncated_pass_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            files = [
                _write(tmp, "hard_parent_n31.json", _hard_parent()),
                _write(tmp, "quotient_catalog_k4.json",
                       _ladder_pass(VALID_NS, complete=False)),
            ]
            problems = self._problems(files)
        self.assertTrue(any("not true" in p for p in problems), problems)

    def test_a_deferred_class_the_hand_off_covers_is_accepted(self):
        """This is the real shape of the sweep: `--skip-classes 0` at n=31."""
        with tempfile.TemporaryDirectory() as tmp:
            files = [
                _write(tmp, "hard_parent_n31.json", _hard_parent()),
                _write(tmp, "quotient_catalog_k4.json",
                       _ladder_pass(VALID_NS, deferred={31: [0]})),
            ]
            self.assertEqual(self._problems(files), [])

    def test_an_uncovered_deferred_class_is_refused(self):
        """Deferring at a length no other pass sweeps drops those classes."""
        with tempfile.TemporaryDirectory() as tmp:
            files = [
                _write(tmp, "hard_parent_n31.json", _hard_parent()),
                _write(tmp, "quotient_catalog_k4.json",
                       _ladder_pass(VALID_NS, deferred={38: [0, 1]})),
            ]
            problems = self._problems(files)
        self.assertTrue(any("n=38: classes [0, 1] are not swept" in p
                            for p in problems), problems)

    def test_the_n31_hand_off_does_not_cover_the_other_classes(self):
        """Coverage is counted per CLASS, not per length.

        n=31 is split between two producers: `hard_parent_n31.py` classifies the
        maximally symmetric parent (weight-32 class 0) and a ladder pass run with
        `--skip-classes 0` does the other nine.  Counted per length, the hand-off
        alone satisfied "n=31 is swept at width 4", so deleting the pass carrying
        nine tenths of that length left a catalogue that still validated.
        """
        with tempfile.TemporaryDirectory() as tmp:
            files = [
                _write(tmp, "hard_parent_n31.json", _hard_parent()),
                # sweeps every length except n=31, as the documented pass does
                _write(tmp, "quotient_catalog_k4_easy.json",
                       _ladder_pass(n for n in VALID_NS if n != 31)),
            ]
            problems = self._problems(files)
        n31 = [p for p in problems if p.startswith("n=31")]
        self.assertTrue(n31, problems)
        self.assertIn("classes [1, 2, 3, 4, 5, 6, 7, 8, 9]", n31[0],
                      "class 0 is covered by the hand-off; the other nine are "
                      "exactly what the missing pass carried")


class TestShardBookkeeping(unittest.TestCase):
    """`manifest` and `merge` must mean the same thing by "the task list"."""

    def test_empty_chunks_are_not_tasks(self):
        tasks = manifest_tasks(sorted(ROWSPACE_NS), 8)
        self.assertEqual(len(tasks), len(set(tasks)), "duplicate task")
        # n=16 has a single marked support, so 7 of its 8 chunks are empty and
        # can never be produced; demanding them made every merge incomplete.
        self.assertEqual(sum(1 for n, _c, _nc in tasks if n == 16), 1)
        self.assertLess(len(tasks), 8 * len(ROWSPACE_NS))

    def test_every_task_names_a_nonempty_chunk(self):
        from classify_rowspace import support_chunks
        for n, chunk, nchunks in manifest_tasks(sorted(ROWSPACE_NS), 4):
            with self.subTest(n=n, chunk=chunk):
                self.assertTrue(support_chunks(n, nchunks)[chunk])


if __name__ == "__main__":
    unittest.main()
