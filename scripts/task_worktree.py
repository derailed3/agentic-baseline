"""Task lifecycle: one worktree and branch per task, so agents never share a checkout.

Usage:
  python scripts/task_worktree.py start <type>/<slug>        new branch + folder .worktrees/<type>-<slug>
  python scripts/task_worktree.py status [<slug>]            uncommitted, unpushed, PR open, PR merged
  python scripts/task_worktree.py pr --title "..." --body-file <file> [--slug <slug>] [--apply]
  python scripts/task_worktree.py finish <slug>              clean up after the PR merged at this exact commit
  python scripts/task_worktree.py check                      fail if this checkout is the shared branch with local work
  python scripts/task_worktree.py list                       every task worktree and its state

<type> is one of: feature, fix, docs, skill, chore, batch. <slug> is lowercase words joined by
hyphens. `pr` only previews unless --apply is given, and --apply is given only after the person
asked for a pull request. `finish` fails closed: it removes nothing unless the code host confirms a
merged pull request whose head commit equals the worktree's commit. Settings come from
registry/code-host.yaml; GitHub calls run as its gh_account without changing the active account.
Needs git; pr, status and finish also need the GitHub CLI (gh). Standard library only.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

TYPES = ("feature", "fix", "docs", "skill", "chore", "batch")
BRANCH_RE = re.compile(rf"^({'|'.join(TYPES)})/([a-z0-9]+(?:-[a-z0-9]+)*)$")


class Refused(Exception):
    """The helper declines to act; the message says why."""


def run(args: list[str], cwd: Path, check: bool = True, env: dict | None = None) -> subprocess.CompletedProcess:
    proc = subprocess.run(args, cwd=cwd, capture_output=True, text=True, env=env)
    if check and proc.returncode != 0:
        raise Refused(f"{' '.join(args[:3])} failed: {(proc.stderr or proc.stdout).strip()}")
    return proc


class Repo:
    def __init__(self, start: Path | None = None) -> None:
        here = start or Path.cwd()
        common = run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], here).stdout.strip()
        self.root = Path(common).parent
        self.config = self._config()
        self.shared = self.config.get("shared_branch", "main")

    def _config(self) -> dict:
        path = self.root / "registry" / "code-host.yaml"
        out = {}
        if path.is_file():
            for line in path.read_text(encoding="utf-8").splitlines():
                m = re.match(r"^([a-z_]+):\s*(.*?)\s*$", line)
                if m and not line.lstrip().startswith("#"):
                    out[m.group(1)] = m.group(2)
        return out

    def git(self, *args: str, cwd: Path | None = None, check: bool = True) -> str:
        return run(["git", *args], cwd or self.root, check).stdout.strip()

    # --- code host -------------------------------------------------------------------------
    def gh(self, *args: str) -> str:
        if not shutil.which("gh"):
            raise Refused("the GitHub CLI (gh) is not installed, so the code host cannot be reached")
        env = dict(os.environ)
        account = self.config.get("gh_account", "")
        if account and "GH_TOKEN" not in env:
            tok = run(["gh", "auth", "token", "-u", account], self.root, check=False)
            if tok.returncode != 0 or not tok.stdout.strip():
                raise Refused(f"no gh credentials for account {account!r}; run: gh auth login (as {account})")
            env["GH_TOKEN"] = tok.stdout.strip()
        repo = f"{self.config.get('owner')}/{self.config.get('repo')}"
        return run(["gh", *args, "--repo", repo], self.root, env=env).stdout

    def prs(self, branch: str, state: str) -> list[dict]:
        out = self.gh("pr", "list", "--head", branch, "--state", state, "--json", "number,state,headRefOid,url,mergedAt")
        return json.loads(out or "[]")

    # --- worktrees -------------------------------------------------------------------------
    def worktrees(self) -> list[tuple[Path, str]]:
        out, path, rows = self.git("worktree", "list", "--porcelain"), None, []
        for line in out.splitlines():
            if line.startswith("worktree "):
                path = Path(line[9:])
            elif line.startswith("branch ") and path is not None:
                rows.append((path, line[7:].removeprefix("refs/heads/")))
        return [(p, b) for p, b in rows if ".worktrees" in p.parts]

    def find(self, slug: str | None) -> tuple[Path, str]:
        here = Path.cwd().resolve()
        for path, branch in self.worktrees():
            if slug is None and (here == path.resolve() or path.resolve() in here.parents):
                return path, branch
            if slug and slug in (branch, branch.split("/", 1)[-1], path.name):
                return path, branch
        raise Refused(f"no task worktree {'for ' + slug if slug else 'here'}; see: task_worktree.py list")

    def dirty(self, path: Path) -> bool:
        return bool(self.git("status", "--porcelain", cwd=path))

    def ahead(self, path: Path, ref: str) -> int:
        out = self.git("rev-list", "--count", f"{ref}..HEAD", cwd=path, check=False)
        return int(out) if out.isdigit() else 0


def cmd_start(repo: Repo, branch: str) -> str:
    m = BRANCH_RE.match(branch)
    if not m:
        raise Refused(f"branch must be <type>/<slug> with type in {', '.join(TYPES)} and a lowercase hyphenated slug")
    folder = repo.root / ".worktrees" / f"{m.group(1)}-{m.group(2)}"
    if folder.exists():
        raise Refused(f"{folder.relative_to(repo.root).as_posix()} already exists")
    if repo.git("branch", "--list", branch):
        raise Refused(f"branch {branch} already exists locally")
    fetch = run(["git", "fetch", "origin", repo.shared], repo.root, check=False)
    if fetch.returncode != 0:
        raise Refused(f"could not fetch origin/{repo.shared}: {fetch.stderr.strip()}; nothing created")
    if repo.git("ls-remote", "--heads", "origin", branch):
        raise Refused(f"branch {branch} already exists on origin")
    if repo.git("rev-parse", "--abbrev-ref", "HEAD") == repo.shared and not repo.dirty(repo.root):
        repo.git("merge", "--ff-only", f"origin/{repo.shared}", check=False)
    repo.git("worktree", "add", "-b", branch, str(folder), f"origin/{repo.shared}")
    return f"started {branch}\nwork in: {folder}"


def cmd_status(repo: Repo, slug: str | None) -> str:
    path, branch = repo.find(slug)
    lines = [f"{branch}  ({path})"]
    if repo.dirty(path):
        lines.append("state: uncommitted changes")
    upstream = repo.git("rev-parse", "--abbrev-ref", "@{upstream}", cwd=path, check=False)
    if "fatal" in upstream or not upstream or upstream == "@{upstream}":
        n = repo.ahead(path, f"origin/{repo.shared}")
        lines.append(f"state: {n} commit(s), not pushed" if n else "state: no commits yet")
    else:
        n = repo.ahead(path, upstream)
        lines.append(f"state: pushed{f', {n} commit(s) not pushed' if n else ''}")
    try:
        head = repo.git("rev-parse", "HEAD", cwd=path)
        merged = [p for p in repo.prs(branch, "merged") if p["headRefOid"] == head]
        opened = repo.prs(branch, "open")
        if merged:
            lines.append(f"pull request: merged at this commit {merged[0]['url']} (run: finish {branch})")
        elif opened:
            lines.append(f"pull request: open {opened[0]['url']}")
        else:
            lines.append("pull request: none")
    except Refused as e:
        lines.append(f"pull request: unknown ({e})")
    return "\n".join(lines)


def cmd_pr(repo: Repo, title: str, body_file: Path, slug: str | None, apply: bool) -> str:
    path, branch = repo.find(slug)
    if not body_file.is_file():
        raise Refused(f"description file not found: {body_file}")
    preview = f"branch: {branch} -> {repo.shared}\ntitle: {title}\ndescription ({body_file}):\n{body_file.read_text(encoding='utf-8')}"
    if not apply:
        return preview + "\n(preview only; add --apply once the person has asked for a pull request)"
    if repo.dirty(path):
        raise Refused("commit or discard the uncommitted changes first")
    if repo.ahead(path, f"origin/{repo.shared}") == 0:
        raise Refused(f"no commits ahead of origin/{repo.shared}; nothing to propose")
    repo.git("push", "-u", "origin", branch, cwd=path)
    opened = repo.prs(branch, "open")
    if opened:
        return f"pushed; reusing open pull request {opened[0]['url']}"
    url = repo.gh("pr", "create", "--base", repo.shared, "--head", branch, "--title", title, "--body-file", str(body_file)).strip()
    return f"pushed; opened {url}"


def cmd_finish(repo: Repo, slug: str) -> str:
    path, branch = repo.find(slug)
    if repo.dirty(path):
        raise Refused("the worktree has uncommitted changes; nothing removed")
    head = repo.git("rev-parse", "HEAD", cwd=path)
    merged = [p for p in repo.prs(branch, "merged") if p["headRefOid"] == head]
    if not merged:
        raise Refused(f"no merged pull request for {branch} at commit {head[:10]}; nothing removed")
    repo.git("worktree", "remove", str(path))
    repo.git("branch", "-D", branch)
    repo.git("fetch", "origin", repo.shared, check=False)
    if repo.git("rev-parse", "--abbrev-ref", "HEAD") == repo.shared and not repo.dirty(repo.root):
        repo.git("merge", "--ff-only", f"origin/{repo.shared}", check=False)
    return f"finished {branch}: {merged[0]['url']} merged; worktree and local branch removed"


def cmd_check(repo: Repo) -> str:
    here = Path.cwd()
    branch = repo.git("rev-parse", "--abbrev-ref", "HEAD", cwd=here)
    if branch != repo.shared:
        return f"ok: on {branch}, not the shared branch"
    problems = []
    if repo.dirty(here):
        problems.append("uncommitted changes")
    n = repo.ahead(here, f"origin/{repo.shared}")
    if n:
        problems.append(f"{n} unpushed commit(s)")
    if problems:
        raise Refused(f"the shared branch {repo.shared} carries local work ({', '.join(problems)}); move it to a task worktree")
    return f"ok: {repo.shared} is clean"


def cmd_list(repo: Repo) -> str:
    rows = repo.worktrees()
    if not rows:
        return "no task worktrees"
    return "\n".join(f"{b:40} {'dirty' if repo.dirty(p) else 'clean':6} {p}" for p, b in rows)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="One worktree and branch per task.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("start").add_argument("branch")
    sub.add_parser("status").add_argument("slug", nargs="?")
    p = sub.add_parser("pr")
    p.add_argument("--title", required=True)
    p.add_argument("--body-file", required=True, type=Path)
    p.add_argument("--slug")
    p.add_argument("--apply", action="store_true")
    sub.add_parser("finish").add_argument("slug")
    sub.add_parser("check")
    sub.add_parser("list")
    a = ap.parse_args(argv)
    try:
        repo = Repo()
        out = {"start": lambda: cmd_start(repo, a.branch), "status": lambda: cmd_status(repo, a.slug),
               "pr": lambda: cmd_pr(repo, a.title, a.body_file, a.slug, a.apply), "finish": lambda: cmd_finish(repo, a.slug),
               "check": lambda: cmd_check(repo), "list": lambda: cmd_list(repo)}[a.cmd]()
    except Refused as e:
        print(f"refused: {e}", file=sys.stderr)
        return 1
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
