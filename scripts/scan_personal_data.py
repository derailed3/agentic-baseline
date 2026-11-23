"""Fail when a tracked file holds what looks like personal data.

Usage: python scripts/scan_personal_data.py [paths...]     (default: every tracked or new, non-ignored file)
Finds US Social Security numbers, payment card numbers (Luhn-valid, 13 to 19 digits), US phone
numbers, and email addresses outside reserved example domains. A line that is a deliberate,
harmless example can carry the marker `pii-allow` to be skipped. Secrets and tokens are the
job of gitleaks (CI), not this script. Exit 0 when clean, 1 with one line per finding.
Standard library only.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALLOW_MARK = "pii-allow"
SAFE_EMAIL_DOMAINS = ("example.com", "example.org", "example.net", "users.noreply.github.com", "localhost")
SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".zip", ".woff", ".woff2", ".ttf"}

SSN = re.compile(r"(?<!\d)(?!000|666|9\d\d)\d{3}-(?!00)\d{2}-(?!0000)\d{4}(?!\d)")
CARD = re.compile(r"(?<!\d)(?:\d[ -]?){12,18}\d(?!\d)")
PHONE = re.compile(r"(?<![\d.])(?:\+?1[ .-]?)?\(?[2-9]\d{2}\)?[ .-][2-9]\d{2}[ .-]\d{4}(?![\d])")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+)")


def luhn(digits: str) -> bool:
    total, alt = 0, False
    for ch in reversed(digits):
        d = int(ch)
        if alt:
            d = d * 2 - 9 if d > 4 else d * 2
        total, alt = total + d, not alt
    return total % 10 == 0


def findings_in(text: str) -> list[tuple[int, str]]:
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        if ALLOW_MARK in line:
            continue
        if SSN.search(line):
            out.append((n, "Social Security number"))
        for m in CARD.finditer(line):
            digits = re.sub(r"\D", "", m.group(0))
            if 13 <= len(digits) <= 19 and luhn(digits) and len(set(digits)) > 1:
                out.append((n, "payment card number"))
                break
        if PHONE.search(line):
            out.append((n, "phone number"))
        for m in EMAIL.finditer(line):
            domain = m.group(1).lower()
            if not any(domain == d or domain.endswith("." + d) for d in SAFE_EMAIL_DOMAINS):
                out.append((n, f"email address at {domain}"))
    return out


def tracked_files() -> list[Path]:
    out = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [ROOT / p for p in out.split("\0") if p]


def main(argv: list[str]) -> int:
    files = [Path(a) for a in argv] or tracked_files()
    found = 0
    for f in files:
        if f.suffix.lower() in SKIP_SUFFIXES or not f.is_file() or f.resolve() == Path(__file__).resolve():
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line, kind in findings_in(text):
            rel = f.resolve().relative_to(ROOT).as_posix() if f.resolve().is_relative_to(ROOT) else str(f)
            print(f"{rel}:{line}: possible {kind}")
            found += 1
    print(f"personal-data scan: {'clean' if not found else f'{found} finding(s)'} ({len(files)} file(s))")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
