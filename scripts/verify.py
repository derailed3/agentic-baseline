"""Run every check the server runs, locally, and print a receipt-ready summary.

Usage: python scripts/verify.py
Checks: the skill validator, all tests (including trigger cases), the declared top-level layout,
LF line endings, the personal-data scan, the generated skill copies (when present), and, when the
tools are installed, gitleaks (secrets) and actionlint (workflow files). A check whose tool is
missing is reported SKIPPED, never PASS. Exit 1 if any check fails. Standard library only (the
validator and tests need PyYAML).
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable


def run(args: list[str]) -> tuple[bool, str]:
    proc = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    tail = (proc.stdout + proc.stderr).strip().splitlines()
    return proc.returncode == 0, (tail[-1] if tail else "")


def tracked() -> list[str]:
    out = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [p for p in out.split("\0") if p]


def check_layout() -> tuple[bool, str]:
    declared = {line.strip() for line in (ROOT / "registry" / "layout.txt").read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.startswith("#")}
    actual = {p.split("/", 1)[0] for p in tracked()}
    extra = sorted(actual - declared)
    return (not extra, "all top-level entries declared" if not extra else f"undeclared: {', '.join(extra)} (registry/layout.txt)")


def check_line_endings() -> tuple[bool, str]:
    bad = [p for p in tracked() if not p.endswith((".ps1", ".png", ".jpg", ".gif", ".ico"))
           and (ROOT / p).is_file() and b"\r\n" in (ROOT / p).read_bytes()]
    return (not bad, "LF everywhere" if not bad else f"CRLF in {', '.join(bad[:5])}")


def main() -> int:
    checks = [
        ("skill validator", lambda: run([PY, ".agents/skills/meta-skills-govern/scripts/validate_skills.py"])),
        ("tests and trigger cases", lambda: run([PY, "scripts/run_tests.py"])),
        ("top-level layout", check_layout),
        ("line endings", check_line_endings),
        ("personal-data scan", lambda: run([PY, "scripts/scan_personal_data.py"])),
        ("generated skill copies", lambda: run([PY, "scripts/deploy_skills.py", "--check"])),
    ]
    optional = [
        ("secret scan (gitleaks)", "gitleaks", ["gitleaks", "dir", "{entry}", "--no-banner", "--redact"]),
        ("workflow lint (actionlint)", "actionlint", ["actionlint"]),
    ]
    failed = 0
    for name, fn in checks:
        ok, detail = fn()
        failed += not ok
        print(f"{'PASS' if ok else 'FAIL':7} {name}: {detail}")
    for name, tool, args in optional:
        # Helper binaries may live in the main checkout's git-ignored .data/tools (shared by every worktree).
        common = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        local_tools = (Path(common).parent if common else ROOT) / ".data" / "tools"
        found = shutil.which(tool) or shutil.which(tool, path=str(local_tools))
        if found:
            args = [found] + args[1:]
        if not found:
            print(f"SKIPPED {name}: {tool} not installed (CI runs it)")
            continue
        if "{entry}" in args:
            # Scan only what git would track: every top-level entry of the tracked and not-ignored files,
            # so git-ignored local folders (.venv, .data) never produce findings.
            entries = sorted({f.split("/", 1)[0] for f in tracked() if (ROOT / f.split("/", 1)[0]).exists()})
            ok, detail = True, f"{len(entries)} top-level entries scanned, no leaks"
            for entry in entries:
                one_ok, one = run([a.replace("{entry}", entry) for a in args])
                if not one_ok:
                    ok, detail = False, f"{entry}: {one}"
                    break
        else:
            ok, detail = run(args)
        failed += not ok
        print(f"{'PASS' if ok else 'FAIL':7} {name}: {detail}")
    print("\nverify: " + ("all checks passed" if not failed else f"{failed} check(s) failed"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
