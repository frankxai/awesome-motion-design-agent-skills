import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("update_stars", Path(__file__).parent.parent / "scripts" / "update-stars.py")
update_stars = importlib.util.module_from_spec(spec)
spec.loader.exec_module(update_stars)

TABLE = """intro
| Pack                                      | Pulse        | Job  |
| ----------------------------------------- | ------------ | ---- |
| [a/one](https://github.com/a/one)         | MIT · 15.8k★ | Jobs |
| [b/two](https://github.com/b/two)         | 0★           | More |
outro"""


class FormatTests(unittest.TestCase):
    def test_formats(self):
        self.assertEqual(update_stars.format_stars(7), "7★")
        self.assertEqual(update_stars.format_stars(999), "999★")
        self.assertEqual(update_stars.format_stars(1000), "1k★")
        self.assertEqual(update_stars.format_stars(15840), "15.8k★")
        self.assertEqual(update_stars.format_stars(134_400), "134k★")


class RewriteTests(unittest.TestCase):
    def test_updates_and_realigns(self):
        counts = {("a", "one"): 123_456, ("b", "two"): 12}
        text, changes = update_stars.rewrite(TABLE, lambda o, r: counts[(o, r)])
        self.assertEqual(len(changes), 2)
        lines = text.split("\n")
        self.assertEqual(lines[0], "intro")
        self.assertEqual(lines[-1], "outro")
        self.assertIn("MIT · 123k★", lines[3])
        self.assertIn("| 12★ ", lines[4])
        pipes = {tuple(i for i, ch in enumerate(line) if ch == "|") for line in lines[1:5]}
        self.assertEqual(len(pipes), 1, "pipes must stay aligned across the table")

    def test_unknown_repo_left_alone(self):
        text, changes = update_stars.rewrite(TABLE, lambda o, r: None)
        self.assertEqual(text, TABLE)
        self.assertEqual(changes, [])

    def test_unchanged_count_does_not_realign(self):
        counts = {("a", "one"): 15_800, ("b", "two"): 0}
        text, changes = update_stars.rewrite(TABLE, lambda o, r: counts[(o, r)])
        self.assertEqual((text, changes), (TABLE, []))


if __name__ == "__main__":
    unittest.main()
