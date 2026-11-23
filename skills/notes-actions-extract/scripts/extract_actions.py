"""Print the action items in a notes file as a Markdown checklist.

An action item is a line that starts with "Action:" or "TODO:" (any case),
optionally after a list marker. Usage: python extract_actions.py <notes-file>
"""
import re
import sys
from pathlib import Path

PATTERN = re.compile(r"^\s*(?:[-*]\s+)?(?:action|todo)\s*:\s*(.+?)\s*$", re.IGNORECASE)


def extract(text: str) -> list[str]:
    """Return the action items found in text, in order."""
    return [m.group(1) for line in text.splitlines() if (m := PATTERN.match(line))]


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: extract_actions.py <notes-file>", file=sys.stderr)
        return 2
    path = Path(argv[1])
    if not path.is_file():
        print(f"not a file: {path}", file=sys.stderr)
        return 2
    items = extract(path.read_text(encoding="utf-8"))
    if not items:
        print("No action items found.")
        return 0
    for item in items:
        print(f"- [ ] {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
