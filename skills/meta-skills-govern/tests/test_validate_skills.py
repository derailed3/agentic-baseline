import importlib.util
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("validate_skills", HERE.parent / "scripts" / "validate_skills.py")
vs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vs)

GOOD_GUIDE = """---
name: notes-items-list
description: List the items in a notes file. Use for "list the items".
version: 1.0.0
---

# Notes Items List

## When to Use

- Listing items.

## Routing

| Request | Read |
|---|---|
| List items | workflows/list.md |
"""


def make_repo(tmp: Path, guide: str = GOOD_GUIDE, changelog: str = "## [1.0.0] - 2026-01-01\n", index: bool = True,
              name: str = "notes-items-list") -> Path:
    skill = tmp / "skills" / name
    (skill / "workflows").mkdir(parents=True)
    (skill / "SKILL.md").write_text(guide, encoding="utf-8", newline="\n")
    (skill / "README.md").write_text("Lists items.\n", encoding="utf-8", newline="\n")
    (skill / "CHANGELOG.md").write_text(changelog, encoding="utf-8", newline="\n")
    (skill / "workflows" / "list.md").write_text("# List\n", encoding="utf-8", newline="\n")
    (tmp / "skills" / "README.md").write_text(f"| `{name}` | lists |\n" if index else "# Skills\n", encoding="utf-8")
    return skill


def rules(report) -> set[str]:
    return {line.split(": ", 1)[1].split(" ", 1)[0] for line in report.fails}


class ValidatorTest(unittest.TestCase):
    def test_good_skill_passes(self):
        with tempfile.TemporaryDirectory() as d:
            make_repo(Path(d))
            self.assertEqual(vs.validate(Path(d)).fails, [])

    def test_version_and_changelog_must_agree(self):
        with tempfile.TemporaryDirectory() as d:
            make_repo(Path(d), changelog="## [0.9.0] - 2026-01-01\n")
            self.assertIn("R8", rules(vs.validate(Path(d))))

    def test_name_must_equal_folder_and_follow_grammar(self):
        with tempfile.TemporaryDirectory() as d:
            make_repo(Path(d), name="Notes")
            self.assertTrue({"R4", "R5"} <= rules(vs.validate(Path(d))))

    def test_missing_files_and_frontmatter(self):
        with tempfile.TemporaryDirectory() as d:
            skill = make_repo(Path(d), guide="# No frontmatter\n")
            (skill / "README.md").unlink()
            self.assertTrue({"R1", "R2"} <= rules(vs.validate(Path(d))))

    def test_paths_line_endings_and_index(self):
        with tempfile.TemporaryDirectory() as d:
            skill = make_repo(Path(d), index=False)
            climb, drive = b".." + b"/other/x.py", b"C" + b":\\Users\\x\\y.py"  # built in parts so this file passes R11/R12
            (skill / "workflows" / "list.md").write_bytes(b"Run " + climb + b"\r\nthen " + drive + b"\r\n")
            self.assertTrue({"R11", "R12", "R13", "R15"} <= rules(vs.validate(Path(d))))

    def test_orphan_workflow_and_missing_sections(self):
        with tempfile.TemporaryDirectory() as d:
            skill = make_repo(Path(d))
            (skill / "workflows" / "extra.md").write_text("# Extra\n", encoding="utf-8")
            (skill / "scripts").mkdir()
            got = rules(vs.validate(Path(d)))
            self.assertIn("R10", got)
            self.assertIn("R9", got)  # has scripts/ but no Parameters or Error Handling

    def test_run_evidence_folder(self):
        with tempfile.TemporaryDirectory() as d:
            skill = make_repo(Path(d))
            (skill / "runs").mkdir()
            (skill / "runs" / "out.txt").write_text("x\n", encoding="utf-8")
            self.assertIn("R14", rules(vs.validate(Path(d))))

    def test_this_repository_passes(self):
        self.assertEqual(vs.validate(HERE.parents[2]).fails, [])


if __name__ == "__main__":
    unittest.main()
