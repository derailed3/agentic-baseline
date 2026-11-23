"""Check every skill against the rules a machine can decide.

Usage: python skills/meta-skills-govern/scripts/validate_skills.py [--root <repo>]
Prints one line per broken rule ("FAIL <skill>: R<n> <why>") and per warning, then a summary.
Exit 0 when nothing fails (warnings allowed), 1 otherwise. The rules and their ids are listed in
this skill's reference/conventions.md; add a rule each time the same mistake is caught twice.
Needs PyYAML.
"""
import argparse
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[3]
REQUIRED_FILES = ("README.md", "SKILL.md", "CHANGELOG.md")
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+){1,2}$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
CHANGELOG_RE = re.compile(r"^## \[(\d+\.\d+\.\d+)\]", re.M)
SECTION_RE = re.compile(r"^#{2,3}\s+(.+?)\s*$", re.M)
WORKFLOW_REF_RE = re.compile(r"workflows/([A-Za-z0-9_.-]+\.md)")
ABSOLUTE_RE = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]|(?<![\w.~])/(?:Users|home|usr|etc|var|opt|tmp|mnt|srv|root)/")
PARENT_RE = re.compile(r"\.\.[\\/]")
TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".json", ".txt", ".toml", ".sh", ".csv"}
EVIDENCE_DIRS = {"evidence", "rounds", "runs", "scratch"}
DESCRIPTION_WARN, DESCRIPTION_MAX = 400, 1024
GUIDE_WARN, GUIDE_MAX = 150, 500


class Report:
    def __init__(self) -> None:
        self.fails: list[str] = []
        self.warns: list[str] = []

    def fail(self, skill: str, rule: str, why: str) -> None:
        self.fails.append(f"FAIL {skill}: {rule} {why}")

    def warn(self, skill: str, rule: str, why: str) -> None:
        self.warns.append(f"WARN {skill}: {rule} {why}")


def split_frontmatter(text: str) -> tuple[str | None, str]:
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?", text, re.S)
    return (m.group(1), text[m.end():]) if m else (None, text)


def skill_files(folder: Path) -> list[Path]:
    return [p for p in folder.rglob("*") if p.is_file() and "__pycache__" not in p.parts]


def check_skill(folder: Path, all_names: set[str], r: Report) -> None:
    name = folder.name
    for f in REQUIRED_FILES:  # R1
        if not (folder / f).is_file():
            r.fail(name, "R1", f"missing {f}")
    guide = folder / "SKILL.md"
    if not guide.is_file():
        return
    text = guide.read_text(encoding="utf-8")
    raw, body = split_frontmatter(text)
    if raw is None:  # R2
        r.fail(name, "R2", "SKILL.md does not start with frontmatter between --- lines")
        return
    try:
        meta = yaml.safe_load(raw) or {}
        if not isinstance(meta, dict):
            raise yaml.YAMLError("not a mapping")
    except yaml.YAMLError as e:
        r.fail(name, "R2", f"frontmatter is not valid YAML ({e.__class__.__name__})")
        return
    for field in ("name", "description", "version"):  # R3
        if not meta.get(field):
            r.fail(name, "R3", f"frontmatter has no {field}")
    if meta.get("name") and meta["name"] != name:  # R4
        r.fail(name, "R4", f"name {meta['name']!r} does not equal the folder name")
    if not NAME_RE.match(name):  # R5
        r.fail(name, "R5", "name must be lowercase letters, digits and hyphens in two or three parts ({domain}-{resource}-{action})")
    desc = " ".join(str(meta.get("description", "")).split())  # R6
    if len(desc) > DESCRIPTION_MAX:
        r.fail(name, "R6", f"description is {len(desc)} characters; the limit is {DESCRIPTION_MAX}")
    elif len(desc) > DESCRIPTION_WARN:
        r.warn(name, "R6", f"description is {len(desc)} characters; aim for under {DESCRIPTION_WARN}")
    version = str(meta.get("version", ""))
    if version and not SEMVER_RE.match(version):  # R7
        r.fail(name, "R7", f"version {version!r} is not MAJOR.MINOR.PATCH")
    changelog = folder / "CHANGELOG.md"  # R8
    if changelog.is_file() and SEMVER_RE.match(version):
        found = CHANGELOG_RE.findall(changelog.read_text(encoding="utf-8"))
        if not found:
            r.fail(name, "R8", "CHANGELOG.md has no '## [X.Y.Z] - YYYY-MM-DD' heading")
        elif found[0] != version:
            r.fail(name, "R8", f"newest CHANGELOG.md version {found[0]} does not equal frontmatter version {version}")
    sections = {s.strip().lower() for s in SECTION_RE.findall(body)}  # R9
    if "when to use" not in sections:
        r.fail(name, "R9", "SKILL.md has no 'When to Use' section")
    runs_commands = (folder / "scripts").is_dir() or "```" in body
    if runs_commands:
        for needed in ("parameters", "error handling"):
            if needed not in sections:
                r.fail(name, "R9", f"a skill that runs commands needs a '{needed.title()}' section")
    named = set(WORKFLOW_REF_RE.findall(body))  # R10
    present = {p.name for p in (folder / "workflows").glob("*.md")} if (folder / "workflows").is_dir() else set()
    for missing in sorted(named - present):
        r.fail(name, "R10", f"SKILL.md names workflows/{missing}, which does not exist")
    for orphan in sorted(present - named):
        r.fail(name, "R10", f"workflows/{orphan} is not named in SKILL.md's routing")
    for p in skill_files(folder):  # R11, R12, R14, R15
        rel = p.relative_to(folder).as_posix()
        parts = set(p.relative_to(folder).parts[:-1])
        if parts & EVIDENCE_DIRS and "fixtures" not in parts:
            r.fail(name, "R14", f"{rel}: run evidence does not belong in a skill (keep it in your scratch folder)")
        if p.suffix not in TEXT_SUFFIXES:
            continue
        data = p.read_bytes()
        if b"\r\n" in data:
            r.fail(name, "R15", f"{rel}: Windows line endings; the repository uses LF")
        content = data.decode("utf-8", errors="replace")
        if PARENT_RE.search(content):
            r.fail(name, "R11", f"{rel}: a path climbs out of the skill's folder (a parent-folder step)")
        for other in all_names - {name}:
            if re.search(rf"skills[\\/]{re.escape(other)}[\\/]", content):
                r.fail(name, "R11", f"{rel}: reaches into another skill's folder ({other})")
        hit = ABSOLUTE_RE.search(content)
        if hit:
            r.fail(name, "R12", f"{rel}: absolute path {hit.group(0)!r}")
    lines = text.count("\n")  # R16
    if lines > GUIDE_MAX:
        r.fail(name, "R16", f"SKILL.md is {lines} lines; the ceiling is {GUIDE_MAX}, move detail into workflows/")
    elif lines > GUIDE_WARN:
        r.warn(name, "R16", f"SKILL.md is {lines} lines; aim for under {GUIDE_WARN}")


def validate(root: Path) -> Report:
    r = Report()
    skills_dir = root / "skills"
    folders = sorted(p for p in skills_dir.iterdir() if p.is_dir() and not p.name.startswith((".", "_")))
    names = {p.name for p in folders}
    if not folders:
        r.fail("skills", "R0", "no skills found")
    for folder in folders:
        check_skill(folder, names, r)
    index = skills_dir / "README.md"  # R13
    if not index.is_file():
        r.fail("skills", "R13", "skills/README.md (the index) is missing")
    else:
        listed = index.read_text(encoding="utf-8")
        for n in sorted(names):
            if f"`{n}`" not in listed:
                r.fail(n, "R13", "not listed in skills/README.md (add a row to the index)")
    return r


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate every skill.")
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="repository root (default: this repository)")
    args = ap.parse_args(argv)
    r = validate(args.root.resolve())
    for line in r.fails + r.warns:
        print(line)
    count = len([p for p in (args.root / "skills").iterdir() if p.is_dir()]) if (args.root / "skills").is_dir() else 0
    print(f"\n{count} skill(s): " + ("PASS" if not r.fails else f"{len(r.fails)} failure(s)") + (f", {len(r.warns)} warning(s)" if r.warns else ""))
    return 1 if r.fails else 0


if __name__ == "__main__":
    sys.exit(main())
