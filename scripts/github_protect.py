"""Set branch protection on the shared branch so the server check cannot be skipped.

Usage: python scripts/github_protect.py            (preview the settings; changes nothing)
       python scripts/github_protect.py --apply    (apply them; needs repository admin rights)
       python scripts/github_protect.py --show     (print what GitHub has now)

What it sets on the shared branch (registry/code-host.yaml):
- changes arrive only by pull request (no direct pushes), for administrators too;
- every job in .github/workflows/checks.yml must pass, on the latest commit (branch up to date);
- no required approving vote: GitHub never lets an author approve their own pull request, so in a
  one-person repository merging is the person's act (decisions/0004-approval-is-the-person-merging.md);
- no force-pushes, no deletion, conversations resolved before merge.
After applying, prove it: open a pull request with a deliberately broken skill and confirm GitHub
refuses to merge it (docs/code-host-setup.md). Runs gh as registry gh_account. Standard library only.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED_CHECKS = ["verify (ubuntu-latest)", "verify (windows-latest)", "verify (macos-latest)", "scan", "lint-workflows"]


def config() -> dict:
    out = {}
    for line in (ROOT / "registry" / "code-host.yaml").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^([a-z_]+):\s*(.*?)\s*$", line)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def payload() -> dict:
    return {
        "required_status_checks": {"strict": True, "contexts": REQUIRED_CHECKS},
        "enforce_admins": True,
        "required_pull_request_reviews": {"required_approving_review_count": 0, "dismiss_stale_reviews": True},
        "restrictions": None,
        "allow_force_pushes": False,
        "allow_deletions": False,
        "required_conversation_resolution": True,
        "required_linear_history": False,
    }


def gh(cfg: dict, *args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    if cfg.get("gh_account") and "GH_TOKEN" not in env:
        env["GH_TOKEN"] = subprocess.run(["gh", "auth", "token", "-u", cfg["gh_account"]],
                                         capture_output=True, text=True).stdout.strip()
    return subprocess.run(["gh", *args], input=stdin, capture_output=True, text=True, env=env)


def main(argv: list[str]) -> int:
    cfg = config()
    path = f"repos/{cfg['owner']}/{cfg['repo']}/branches/{cfg.get('shared_branch', 'main')}/protection"
    if "--show" in argv:
        r = gh(cfg, "api", path)
        print(r.stdout or r.stderr)
        return r.returncode
    body = json.dumps(payload(), indent=2)
    if "--apply" not in argv:
        print(f"PUT {path}\n{body}\n(preview only; add --apply to set it)")
        return 0
    r = gh(cfg, "api", "-X", "PUT", path, "--input", "-", stdin=body)
    if r.returncode != 0:
        print(f"failed: {r.stderr.strip() or r.stdout.strip()}")
        return 1
    print(f"protection applied to {cfg['owner']}/{cfg['repo']}:{cfg.get('shared_branch', 'main')}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
