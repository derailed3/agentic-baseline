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


def quiet(fn, *args):
    with redirect_stdout(io.StringIO()) as out:
        code = fn(*args)
    return code, out.getvalue()


class DeployTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "skills" / "a-b").mkdir(parents=True)
        (self.root / "skills" / "a-b" / "SKILL.md").write_text("one\n", encoding="utf-8")
        (self.root / "registry").mkdir()
        (self.root / "registry" / "skill-targets.txt").write_text("# comment\n.tool/skills\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_missing_then_deployed_then_stale_then_in_sync(self):
        code, out = quiet(ds.main, ["--check"], self.root)
        self.assertEqual(code, 0)
        self.assertIn("missing", out)
        quiet(ds.main, [], self.root)
        self.assertTrue((self.root / ".tool" / "skills" / "a-b" / "SKILL.md").is_file())
        self.assertEqual(quiet(ds.main, ["--check"], self.root)[0], 0)
        (self.root / "skills" / "a-b" / "SKILL.md").write_text("two\n", encoding="utf-8")
        code, out = quiet(ds.main, ["--check"], self.root)
        self.assertEqual(code, 1)
        self.assertIn("stale", out)
        quiet(ds.main, [], self.root)
        self.assertEqual(quiet(ds.main, ["--check"], self.root)[0], 0)

    def test_refuses_to_replace_a_folder_it_did_not_make(self):
        (self.root / ".tool" / "skills").mkdir(parents=True)
        (self.root / ".tool" / "skills" / "precious.txt").write_text("keep\n", encoding="utf-8")
        with self.assertRaises(SystemExit):
            quiet(ds.main, [], self.root)
        self.assertTrue((self.root / ".tool" / "skills" / "precious.txt").is_file())


if __name__ == "__main__":
    unittest.main()
