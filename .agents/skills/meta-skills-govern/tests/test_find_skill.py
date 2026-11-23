import importlib.util
import tempfile
import unittest
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("find_skill", HERE.parent / "scripts" / "find_skill.py")
fs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fs)


def write_skill(root: Path, name: str, description: str, keywords: list[str]) -> None:
    folder = root / ".agents" / "skills" / name
    folder.mkdir(parents=True)
    meta = yaml.safe_dump({"name": name, "description": description, "version": "1.0.0", "keywords": keywords})
    (folder / "SKILL.md").write_text("---\n" + meta + "---\n", encoding="utf-8")


class FindSkillTest(unittest.TestCase):
    def test_ranks_by_phrase_then_pattern(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            write_skill(root, "notes-actions-extract", "Pull action items from notes.", ["action items", "meeting notes"])
            write_skill(root, "tickets-report-draft", "Draft a weekly status report.", ["status report", "rx:\\bblocked\\b"])
            self.assertEqual(fs.rank(root, "what are the action items in my meeting notes")[0][1], "notes-actions-extract")
            self.assertEqual(fs.rank(root, "which tickets are blocked")[0][1], "tickets-report-draft")

    def test_words_of_the_skill_name_count(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            write_skill(root, "media-shot-detect", "Find edit points.", [])
            write_skill(root, "media-speech-transcribe", "Words with times.", [])
            ranked = fs.rank(root, "detect every shot in this video")
            self.assertEqual(ranked[0][1], "media-shot-detect")
            self.assertTrue(any(w.startswith("name:") for w in ranked[0][2]))

    def test_no_match_is_empty(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            write_skill(root, "notes-actions-extract", "Pull action items from notes.", ["action items"])
            self.assertEqual(fs.rank(root, "bake sourdough"), [])


if __name__ == "__main__":
    unittest.main()
