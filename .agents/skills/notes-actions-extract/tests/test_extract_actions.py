import importlib.util
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "extract_actions", Path(__file__).resolve().parent.parent / "scripts" / "extract_actions.py")
ea = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ea)


class ExtractTest(unittest.TestCase):
    def test_finds_actions_and_todos_in_order(self):
        notes = "Agenda\n- Action: send the draft to the team\nTODO: book the room\nNot an action: ignore me\n"
        self.assertEqual(ea.extract(notes), ["send the draft to the team", "book the room"])

    def test_no_items(self):
        self.assertEqual(ea.extract("Just notes, nothing to do.\n"), [])


if __name__ == "__main__":
    unittest.main()
