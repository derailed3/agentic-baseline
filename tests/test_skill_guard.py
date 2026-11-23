"""The skill guard in a scratch repository: install writes marked hooks (and keeps a foreign one),
a commit refreshes the mirror, a commit that breaks a skill is refused, uninstall removes only its own hooks."""
import importlib.util
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("skill_guard", HERE / "scripts" / "skill_guard.py")
sg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sg)

VALIDATOR = '''import sys
from pathlib import Path
root = Path(__file__).resolve().parents[4]
bad = [p for p in (root / ".agents" / "skills").glob("*/SKILL.md") if "BROKEN" in p.read_text()]
print("broken: " + ", ".join(p.parent.name for p in bad) if bad else "ok")
sys.exit(1 if bad else 0)
'''


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)


@unittest.skipUnless(shutil.which("git"), "git not installed")
class GuardTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        r = self.root = Path(self.tmp.name)
        git(r, "init", "-q", "-b", "main")
        git(r, "config", "user.email", "guard-test")
        git(r, "config", "user.name", "test")
        (r / "scripts").mkdir()
        for f in ("skill_guard.py", "deploy_skills.py"):
            shutil.copyfile(HERE / "scripts" / f, r / "scripts" / f)
        (r / "registry").mkdir()
        (r / "registry" / "skill-host.yaml").write_text("mirrors:\n  - path: .tool/skills\n    reads: a tool\n", encoding="utf-8")
        gov = r / ".agents" / "skills" / "meta-skills-govern" / "scripts"
        gov.mkdir(parents=True)
        (gov / "validate_skills.py").write_text(VALIDATOR, encoding="utf-8")
        (gov.parent / "SKILL.md").write_text("fine\n", encoding="utf-8")
        (r / ".gitignore").write_text("/.tool/\n", encoding="utf-8")
        self.guard = sg

    def tearDown(self):
        self.tmp.cleanup()

    def run_guard(self, action):
        return subprocess.run([sys.executable, str(self.root / "scripts" / "skill_guard.py"), action], cwd=self.root,
                              capture_output=True, text=True)

    def hooks(self):
        return Path(git(self.root, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip()) / "hooks"

    def test_install_commit_refresh_block_uninstall(self):
        foreign = self.hooks() / "post-merge"
        foreign.parent.mkdir(parents=True, exist_ok=True)
        foreign.write_text("#!/bin/sh\necho mine\n", encoding="utf-8")
        out = self.run_guard("install").stdout
        self.assertIn("installed post-commit", out)
        self.assertIn("kept      post-merge", out)
        self.assertIn(sg.MARKER, (self.hooks() / "pre-commit").read_text(encoding="utf-8"))
        # A commit refreshes the mirror through the post-commit hook.
        git(self.root, "add", "-A")
        c = git(self.root, "commit", "-q", "-m", "first")
        self.assertEqual(c.returncode, 0, c.stderr)
        mirrored = self.root / ".tool" / "skills" / "meta-skills-govern" / "SKILL.md"
        self.assertTrue(mirrored.is_file(), "post-commit hook did not write the mirror")
        # A commit that breaks a skill is refused by the pre-commit hook.
        skill = self.root / ".agents" / "skills" / "meta-skills-govern" / "SKILL.md"
        skill.write_text("BROKEN\n", encoding="utf-8")
        git(self.root, "add", "-A")
        c = git(self.root, "commit", "-q", "-m", "break it")
        self.assertNotEqual(c.returncode, 0)
        self.assertIn("broken: meta-skills-govern", c.stderr + c.stdout)
        # Uninstall removes the guard's hooks and keeps the foreign one.
        self.run_guard("uninstall")
        self.assertFalse((self.hooks() / "pre-commit").exists())
        self.assertTrue(foreign.exists())

    def test_check_ignores_commits_without_skill_changes(self):
        (self.root / "notes.txt").write_text("x\n", encoding="utf-8")
        git(self.root, "add", "notes.txt")
        self.assertEqual(self.run_guard("check").returncode, 0)


if __name__ == "__main__":
    unittest.main()
