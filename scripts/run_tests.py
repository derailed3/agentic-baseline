"""Run every test in the repository: each skill's tests/ folder and the repository's tests/ folder.

Usage: python scripts/run_tests.py [-v]
Test folders are not Python packages, so plain `unittest discover` from the root would find
nothing; this runner discovers test_*.py in each tests/ folder on its own. Exit 1 if any test
fails or errors, or if no tests were found at all (a runner that silently runs nothing is a lie).
Standard library only.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_dirs() -> list[Path]:
    dirs = sorted(p for p in (ROOT / "skills").glob("*/tests") if p.is_dir())
    if (ROOT / "tests").is_dir():
        dirs.append(ROOT / "tests")
    return dirs


def main(argv: list[str]) -> int:
    suite = unittest.TestSuite()
    for d in test_dirs():
        suite.addTests(unittest.defaultTestLoader.discover(start_dir=str(d), pattern="test_*.py", top_level_dir=str(d)))
    count = suite.countTestCases()
    if count == 0:
        print("no tests found")
        return 1
    result = unittest.TextTestRunner(verbosity=2 if "-v" in argv else 1).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
