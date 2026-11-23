import importlib.util
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "scan_personal_data", Path(__file__).resolve().parent.parent / "scripts" / "scan_personal_data.py")
sp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sp)

# Test values are assembled from parts so this file itself never matches the scanner.
SSN = "123" + "-45-" + "6789"
CARD = "4111 1111" + " 1111 1111"   # the standard Visa test number (Luhn-valid)
PHONE = "(713) " + "555-2368"
EMAIL = "jane.doe" + "@" + "gmail.com"


def kinds(text: str) -> set[str]:
    return {k.split(" at ")[0] for _, k in sp.findings_in(text)}


class ScanTest(unittest.TestCase):
    def test_finds_each_kind(self):
        self.assertEqual(kinds(f"ssn {SSN}\ncard {CARD}\ncall {PHONE}\nmail {EMAIL}\n"),
                         {"Social Security number", "payment card number", "phone number", "email address"})

    def test_ignores_safe_values(self):
        text = "user@example.com\nversion 1.2.3\nid 2026-11-22\nsha 0123456789abcdef\nport 8080\n"
        self.assertEqual(sp.findings_in(text), [])

    def test_non_luhn_digits_are_not_cards(self):
        self.assertNotIn("payment card number", kinds("order 1234 5678 9012 3456"))

    def test_allow_marker_skips_line(self):
        self.assertEqual(sp.findings_in(f"{EMAIL}  # pii-allow (documented sample)\n"), [])


if __name__ == "__main__":
    unittest.main()
