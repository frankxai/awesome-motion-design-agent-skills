import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent.parent / "benchmarks" / "motion-audit"
spec = importlib.util.spec_from_file_location("motion_audit_score", ROOT / "score.py")
scorer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scorer)


def perfect(key, level="required"):
    return [{"fixture": d["fixture"], "line": d["line"], "category": d["accept"][0], "summary": d["why"]}
            for d in key["defects"] if d["level"] == level]


class AnswerKeyTests(unittest.TestCase):
    def test_every_anchor_resolves_to_one_line(self):
        key = scorer.load_key(ROOT)  # raises if any anchor is missing or ambiguous
        self.assertTrue(all("line" in d for d in key["defects"]))

    def test_every_fixture_is_in_the_key(self):
        key = scorer.load_key(ROOT)
        on_disk = {p.name for p in (ROOT / "fixtures").glob("*.html")}
        self.assertEqual(on_disk, {d["fixture"] for d in key["defects"]})

    def test_fixture_names_and_bodies_do_not_leak_answers(self):
        for path in (ROOT / "fixtures").glob("*.html"):
            text = path.read_text(encoding="utf-8").lower()
            for word in ("defect", "bug", "control", "answer key", "todo", "fixme"):
                self.assertNotIn(word, path.name.lower())
            self.assertNotIn("defect", text)


class ScoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.key = scorer.load_key(ROOT)

    def test_perfect_run(self):
        r = scorer.score(perfect(self.key), self.key)
        self.assertEqual((r["recall"], r["precision"], r["falsePositives"]), (1.0, 1.0, 0))

    def test_empty_run(self):
        r = scorer.score([], self.key)
        self.assertEqual((r["recall"], r["precision"]), (0.0, None))

    def test_optional_findings_do_not_cost_precision(self):
        r = scorer.score(perfect(self.key) + perfect(self.key, "optional"), self.key)
        self.assertEqual((r["recall"], r["precision"]), (1.0, 1.0))

    def test_wrong_line_or_category_does_not_match(self):
        d = next(d for d in self.key["defects"] if d["id"] == "d02a")
        far = {"fixture": d["fixture"], "line": 1, "category": "performance", "summary": "x"}  # doctype line
        wrong = {"fixture": d["fixture"], "line": d["line"], "category": "cleanup", "summary": "x"}
        r = scorer.score([far, wrong], self.key)
        self.assertEqual((r["recall"], r["falsePositives"]), (0.0, 2))

    def test_duplicate_report_counts_once(self):
        f = perfect(self.key)[0]
        r = scorer.score([f, dict(f)], self.key)
        self.assertEqual((len(r["found"]), r["falsePositives"]), (1, 1))

    def test_control_false_positive_is_counted(self):
        r = scorer.score([{"fixture": "06-faq.html", "line": 1, "category": "keyboard", "summary": "x"}], self.key)
        self.assertEqual(r["controlFalsePositives"], 1)


if __name__ == "__main__":
    unittest.main()
