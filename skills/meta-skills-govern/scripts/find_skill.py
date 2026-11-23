"""Rank existing skills against a request, to find the right one or spot an overlap.

Usage: python skills/meta-skills-govern/scripts/find_skill.py "<request>" [--top N] [--root <repo>]
Reads every skill's frontmatter fresh (no stored index to go stale) and scores it: a matched
"rx:" keyword pattern counts most, then a keyword phrase found in the request, then a single
keyword word, then a tag, then a description word. Prints the top skills with what matched.
When the top two scores are close, the request sits between two skills: read both before
creating a third. Needs PyYAML.
"""
import argparse
import re
import sys
from pathlib import Path

import yaml

DEFAULT_ROOT = Path(__file__).resolve().parents[3]
WEIGHTS = {"pattern": 8.0, "phrase": 5.0, "word": 2.0, "tag": 1.5, "description": 0.5}
STOP = {"a", "an", "the", "and", "or", "of", "to", "for", "in", "on", "my", "me", "i", "it", "is", "this",
        "that", "with", "from", "use", "when", "what", "how", "do", "make", "please", "can", "you", "be"}


def words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP and len(w) > 1}


def load(root: Path) -> list[dict]:
    out = []
    for guide in sorted((root / "skills").glob("*/SKILL.md")):
        m = re.match(r"^---\r?\n(.*?)\r?\n---", guide.read_text(encoding="utf-8"), re.S)
        if not m:
            continue
        try:
            meta = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            continue
        meta.setdefault("name", guide.parent.name)
        out.append(meta)
    return out


def score(meta: dict, request: str) -> tuple[float, list[str]]:
    req, req_words = request.lower(), words(request)
    total, why = 0.0, []
    for kw in meta.get("keywords") or []:
        kw = str(kw)
        if kw.startswith("rx:"):
            try:
                if re.search(kw[3:], req, re.I):
                    total += WEIGHTS["pattern"]
                    why.append(f"pattern {kw[3:]}")
            except re.error:
                pass
        elif " " in kw.strip() and kw.lower() in req:
            total += WEIGHTS["phrase"]
            why.append(f"phrase {kw!r}")
        else:
            hit = words(kw) & req_words
            if hit:
                total += WEIGHTS["word"] * len(hit)
                why.append(f"keyword {kw!r}")
    for tag in meta.get("tags") or []:
        value = str(tag).split(":", 1)[-1]
        if words(value) & req_words:
            total += WEIGHTS["tag"]
            why.append(f"tag {tag}")
    shared = words(str(meta.get("description", ""))) & req_words
    if shared:
        total += WEIGHTS["description"] * len(shared)
        why.append("description: " + ", ".join(sorted(shared)))
    return total, why


def rank(root: Path, request: str) -> list[tuple[float, str, list[str]]]:
    rows = [(*score(m, request), m["name"]) for m in load(root)]
    return sorted(((s, n, w) for s, w, n in rows if s > 0), key=lambda r: (-r[0], r[1]))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Rank skills against a request.")
    ap.add_argument("request")
    ap.add_argument("--top", type=int, default=3)
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = ap.parse_args(argv)
    ranked = rank(args.root, args.request)
    if not ranked:
        print("No skill matches. If this is a recurring task, create one (skills/meta-skills-govern/workflows/create.md).")
        return 0
    for s, name, why in ranked[: args.top]:
        print(f"{s:5.1f}  {name}  ({'; '.join(why)})")
    if len(ranked) > 1 and ranked[1][0] >= 0.8 * ranked[0][0]:
        print("\nThe top two are close: the request sits between them. Read both before creating another skill.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
