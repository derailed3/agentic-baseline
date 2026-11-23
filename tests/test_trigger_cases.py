"""Every recorded request in trigger_cases.yaml ranks its expected skill first."""
import importlib.util
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("find_skill", ROOT / "skills" / "meta-skills-govern" / "scripts" / "find_skill.py")
fs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fs)
CASES = yaml.safe_load((ROOT / "tests" / "trigger_cases.yaml").read_text(encoding="utf-8"))["cases"]


class TriggerCases(unittest.TestCase):
    def test_every_case_ranks_its_skill_first(self):
        for case in CASES:
            with self.subTest(request=case["request"]):
                ranked = fs.rank(ROOT, case["request"])
                self.assertTrue(ranked, "no skill matched")
                self.assertEqual(ranked[0][1], case["expect"], f"ranking: {[(round(s, 1), n) for s, n, _ in ranked[:3]]}")

    def test_every_skill_has_at_least_two_cases(self):
        skills = {p.name for p in (ROOT / "skills").iterdir() if p.is_dir()}
        counts = {s: sum(1 for c in CASES if c["expect"] == s) for s in skills}
        self.assertEqual({s: n for s, n in counts.items() if n < 2}, {})


if __name__ == "__main__":
    unittest.main()
