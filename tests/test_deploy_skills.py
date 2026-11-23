import importlib.util
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "deploy_skills", Path(__file__).resolve().parent.parent / "scripts" / "deploy_skills.py")
ds = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ds)

HOST = "# comment\nbase_branch: origin/main\nmirrors:\n  - path: .tool/skills\n    reads: a tool\n\nwork_folder: .data\n"


def quiet(fn, *args):
    with redirect_stdout(io.StringIO()) as out:
        code = fn(*args)
    return code, out.getvalue()


class DeployTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.src = self.root / ".agents" / "skills"
        (self.src / "a-b").mkdir(parents=True)
        (self.src / "a-b" / "SKILL.md").write_text("one\n", encoding="utf-8")
        (self.root / "registry").mkdir()
        (self.root / "registry" / "skill-host.yaml").write_text(HOST, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_missing_then_deployed_then_stale_then_in_sync(self):
        code, out = quiet(ds.main, ["--check"], self.root)
        self.assertEqual(code, 0)
        self.assertIn("missing", out)
        quiet(ds.main, [], self.root)
        self.assertTrue((self.root / ".tool" / "skills" / "a-b" / "SKILL.md").is_file())
        self.assertEqual(quiet(ds.main, ["--check"], self.root)[0], 0)
        (self.src / "a-b" / "SKILL.md").write_text("two\n", encoding="utf-8")
        code, out = quiet(ds.main, ["--check"], self.root)
        self.assertEqual(code, 1)
        self.assertIn("stale", out)
        quiet(ds.main, [], self.root)
        self.assertEqual(quiet(ds.main, ["--check"], self.root)[0], 0)

    def test_mirrors_read_from_host_file(self):
        self.assertEqual([(t.relative_to(self.root).as_posix(), r) for t, r in ds.mirrors(self.root)], [(".tool/skills", "a tool")])
        self.assertIn(".tool/skills", quiet(ds.main, ["--targets"], self.root)[1])

    def test_deleted_skill_leaves_the_mirror(self):
        (self.src / "c-d").mkdir()
        (self.src / "c-d" / "SKILL.md").write_text("x\n", encoding="utf-8")
        quiet(ds.main, [], self.root)
        self.assertTrue((self.root / ".tool" / "skills" / "c-d").is_dir())
        (self.src / "c-d" / "SKILL.md").unlink()
        (self.src / "c-d").rmdir()
        quiet(ds.main, [], self.root)
        self.assertFalse((self.root / ".tool" / "skills" / "c-d").exists())

    def test_refuses_to_replace_a_folder_it_did_not_make(self):
        (self.root / ".tool" / "skills").mkdir(parents=True)
        (self.root / ".tool" / "skills" / "precious.txt").write_text("keep\n", encoding="utf-8")
        with self.assertRaises(SystemExit):
            quiet(ds.main, [], self.root)
        self.assertTrue((self.root / ".tool" / "skills" / "precious.txt").is_file())


if __name__ == "__main__":
    unittest.main()
