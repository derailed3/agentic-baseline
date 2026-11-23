"""The skill guard: keeps the generated skill mirrors in step with .agents/skills/ without anyone
remembering, and stops a commit that breaks a skill.

    python scripts/skill_guard.py install     write the git hooks (repository-local, shared by every worktree)
    python scripts/skill_guard.py uninstall   remove them
    python scripts/skill_guard.py status      say which hooks are installed
    python scripts/skill_guard.py refresh     rewrite the mirrors (what the hooks run after checkout, merge, commit, rebase)
    python scripts/skill_guard.py check       validate the skills when the commit being made touches .agents/skills/ (pre-commit)

The hooks live in this repository's own .git/hooks (nothing system-wide, nothing in the user profile) and
hold no logic: each finds this script in the checkout it runs in and calls it, and does nothing when the
script is missing. They prefer the repository's .venv Python and fall back to the one on PATH. Only hooks
carrying the marker line below are ever replaced or removed. Standard library only.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKER = "# skill guard: written by scripts/skill_guard.py install; remove with scripts/skill_guard.py uninstall."
REFRESH_HOOKS = ("post-checkout", "post-merge", "post-commit", "post-rewrite")
CHECK_HOOKS = ("pre-commit",)
HOOK = """#!/bin/sh
{marker}
# No logic lives here. If the script below is missing, the hook does nothing.
root=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
guard="$root/scripts/skill_guard.py"
[ -f "$guard" ] || exit 0
main=$(dirname "$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)")
py=""
for c in "$root/.venv/Scripts/python.exe" "$root/.venv/bin/python" "$main/.venv/Scripts/python.exe" "$main/.venv/bin/python"; do
  [ -x "$c" ] && py="$c" && break
done
[ -n "$py" ] || py=$(command -v python3 || command -v python) || exit 0
"$py" "$guard" {action}
[ "$?" = 1 ] && exit 1
exit 0
"""


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True).stdout.strip()


def hooks_dir(root: Path = ROOT) -> Path:
    configured = git("config", "--get", "core.hooksPath", cwd=root)
    if configured:
        raise SystemExit(f"core.hooksPath is set to {configured}; the guard only writes .git/hooks. Unset it or add the hooks there by hand.")
    return Path(git("rev-parse", "--path-format=absolute", "--git-common-dir", cwd=root)) / "hooks"


def install(root: Path = ROOT) -> int:
    d = hooks_dir(root)
    d.mkdir(parents=True, exist_ok=True)
    for name in REFRESH_HOOKS + CHECK_HOOKS:
        path = d / name
        if path.exists() and MARKER not in path.read_text(encoding="utf-8", errors="replace"):
            print(f"kept      {name}: an existing hook not written by the guard (add `python scripts/skill_guard.py "
                  f"{'check' if name in CHECK_HOOKS else 'refresh'}` to it by hand)")
            continue
        path.write_text(HOOK.format(marker=MARKER, action="check" if name in CHECK_HOOKS else "refresh"), encoding="utf-8", newline="\n")
        path.chmod(0o755)
        print(f"installed {name}")
    return 0


def uninstall(root: Path = ROOT) -> int:
    d = hooks_dir(root)
    for name in REFRESH_HOOKS + CHECK_HOOKS:
        path = d / name
        if path.exists() and MARKER in path.read_text(encoding="utf-8", errors="replace"):
            path.unlink()
            print(f"removed   {name}")
    return 0


def status(root: Path = ROOT) -> int:
    d = hooks_dir(root)
    missing = 0
    for name in REFRESH_HOOKS + CHECK_HOOKS:
        path = d / name
        state = "guard" if path.exists() and MARKER in path.read_text(encoding="utf-8", errors="replace") else "other" if path.exists() else "missing"
        missing += state != "guard"
        print(f"{state:8} {name}")
    return 1 if missing else 0


def refresh(root: Path = ROOT) -> int:
    """Rewrite the mirrors; never fails a git operation (exit 2 on trouble, which the hooks ignore)."""
    if not (root / ".agents" / "skills").is_dir():
        return 0
    proc = subprocess.run([sys.executable, str(root / "scripts" / "deploy_skills.py")], cwd=root, capture_output=True, text=True)
    changed = [line for line in proc.stdout.splitlines() if line.startswith("deployed")]
    for line in changed:
        print(f"skill guard: {line}")
    if proc.returncode:
        print(f"skill guard: mirrors not refreshed: {(proc.stdout + proc.stderr).strip()}", file=sys.stderr)
        return 2
    return 0


def check(root: Path = ROOT) -> int:
    """Block a commit (exit 1) when it changes .agents/skills/ and the skill validator fails."""
    staged = git("diff", "--cached", "--name-only", "--", ".agents/skills", cwd=root)
    if not staged:
        return 0
    validator = root / ".agents" / "skills" / "meta-skills-govern" / "scripts" / "validate_skills.py"
    if not validator.is_file():
        return 0
    proc = subprocess.run([sys.executable, str(validator)], cwd=root, capture_output=True, text=True)
    if proc.returncode and "No module named" in proc.stderr:
        print("skill guard: validator not run (this Python lacks its packages; run scripts/setup first). The server still checks.", file=sys.stderr)
        return 0
    if proc.returncode:
        print("skill guard: the commit changes skills and the validator fails:", file=sys.stderr)
        print((proc.stdout + proc.stderr).strip(), file=sys.stderr)
        return 1
    return 0


def main(argv: list[str]) -> int:
    actions = {"install": install, "uninstall": uninstall, "status": status, "refresh": refresh, "check": check}
    if len(argv) != 1 or argv[0] not in actions:
        print(__doc__)
        return 2
    return actions[argv[0]]()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
