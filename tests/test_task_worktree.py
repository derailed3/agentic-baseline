import importlib.util
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "task_worktree", Path(__file__).resolve().parent.parent / "scripts" / "task_worktree.py")
tw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tw)


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


class WorktreeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        origin, self.clone = base / "origin.git", base / "clone"
        git(base, "init", "-q", "--bare", "-b", "main", str(origin))
        git(base, "clone", "-q", str(origin), str(self.clone))
        for k, v in (("user.email", "test@example.com"), ("user.name", "Test")):
            git(self.clone, "config", k, v)
        (self.clone / "registry").mkdir()
        (self.clone / "registry" / "code-host.yaml").write_text(
            "host: github\nowner: someone\nrepo: something\nshared_branch: main\ngh_account:\n", encoding="utf-8")
        (self.clone / "README.md").write_text("hello\n", encoding="utf-8")
        git(self.clone, "add", ".")
        git(self.clone, "commit", "-q", "-m", "init")
        git(self.clone, "push", "-q", "origin", "main")
        self.cwd = os.getcwd()
        os.chdir(self.clone)
        self.repo = tw.Repo(self.clone)

    def tearDown(self):
        os.chdir(self.cwd)
        subprocess.run(["git", "worktree", "prune"], cwd=self.clone, capture_output=True)
        self.tmp.cleanup()

    def test_start_creates_branch_and_folder_and_refuses_twice(self):
        out = tw.cmd_start(self.repo, "skill/notes-tidy")
        folder = self.clone / ".worktrees" / "skill-notes-tidy"
        self.assertIn("started skill/notes-tidy", out)
        self.assertTrue(folder.is_dir())
        self.assertEqual(git(folder, "rev-parse", "--abbrev-ref", "HEAD"), "skill/notes-tidy")
        with self.assertRaises(tw.Refused):
            tw.cmd_start(self.repo, "skill/notes-tidy")

    def test_new_task_is_not_reported_as_pushed(self):
        tw.cmd_start(self.repo, "docs/fresh")
        folder = self.clone / ".worktrees" / "docs-fresh"
        self.repo.prs = lambda branch, state: []
        os.chdir(folder)
        self.assertIn("state: no commits yet", tw.cmd_status(self.repo, None))
        (folder / "a.txt").write_text("a\n", encoding="utf-8")
        git(folder, "add", "a.txt")
        git(folder, "commit", "-qm", "a")
        self.assertIn("1 commit(s), not pushed", tw.cmd_status(self.repo, None))
        os.chdir(self.clone)

    def test_start_rejects_bad_names(self):
        for bad in ("notes", "misc/notes", "skill/Notes", "skill/notes_tidy"):
            with self.assertRaises(tw.Refused):
                tw.cmd_start(self.repo, bad)

    def test_check_flags_local_work_on_shared_branch(self):
        self.assertIn("clean", tw.cmd_check(self.repo))
        (self.clone / "README.md").write_text("changed\n", encoding="utf-8")
        with self.assertRaises(tw.Refused):
            tw.cmd_check(self.repo)

    def test_finish_fails_closed_without_matching_merged_pr(self):
        tw.cmd_start(self.repo, "fix/typo")
        folder = self.clone / ".worktrees" / "fix-typo"
        (folder / "README.md").write_text("fixed\n", encoding="utf-8")
        git(folder, "commit", "-qam", "fix")
        head = git(folder, "rev-parse", "HEAD")
        self.repo.prs = lambda branch, state: [{"headRefOid": "0" * 40, "url": "u", "state": "MERGED"}] if state == "merged" else []
        with self.assertRaises(tw.Refused):
            tw.cmd_finish(self.repo, "fix/typo")  # merged PR is at another commit
        self.assertTrue(folder.is_dir())
        self.repo.prs = lambda branch, state: [{"headRefOid": head, "url": "u", "state": "MERGED"}] if state == "merged" else []
        self.assertIn("finished fix/typo", tw.cmd_finish(self.repo, "fix/typo"))
        self.assertFalse(folder.exists())
        self.assertEqual(git(self.clone, "branch", "--list", "fix/typo"), "")

    def test_finish_refuses_with_uncommitted_changes(self):
        tw.cmd_start(self.repo, "docs/readme")
        folder = self.clone / ".worktrees" / "docs-readme"
        (folder / "new.txt").write_text("x\n", encoding="utf-8")
        self.repo.prs = lambda branch, state: []
        with self.assertRaises(tw.Refused):
            tw.cmd_finish(self.repo, "docs/readme")

    def test_pr_previews_without_apply(self):
        tw.cmd_start(self.repo, "feature/thing")
        body = Path(self.tmp.name) / "body.md"
        body.write_text("What and why.\n", encoding="utf-8")
        out = tw.cmd_pr(self.repo, "Add thing", body, "feature/thing", apply=False)
        self.assertIn("preview only", out)
        self.assertEqual(git(self.clone, "ls-remote", "--heads", "origin", "feature/thing"), "")


if __name__ == "__main__":
    unittest.main()
