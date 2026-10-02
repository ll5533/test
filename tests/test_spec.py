import unittest

from pricefinder.spec import Spec, parse_spec, parse_wanted


class ParseSpecTest(unittest.TestCase):
    def check(self, title, size, unit, count):
        spec, reason = parse_spec(title)
        self.assertEqual(spec, Spec(size, unit, count), f"{title} -> {reason}")

    def test_same_volume_written_differently(self):
        for t in ["우유 1L", "우유 1,000ml", "우유 1000ML", "우유 1리터", "우유 1.0L"]:
            self.check(t, 1000, "ml", 1)

    def test_pack_counts(self):
        self.check("햇반 210g x 12개", 210, "g", 12)
        self.check("햇반 210g×12입", 210, "g", 12)
        self.check("우유 2 x 1L", 1000, "ml", 2)
        self.check("우유 250ml x 4", 250, "ml", 4)

    def test_kg_and_rolls(self):
        self.check("쌀 10kg", 10000, "g", 1)
        self.check("화장지 27m 30롤 3팩", 30, "롤", 3)

    def test_ambiguous_is_rejected(self):
        for t in ["우유 1L + 300ml 증정", "우유 (500ml/1L 택1)", "우유 500ml 1+1",
                  "햇반 12개 / 1박스 24개", "우유"]:
            spec, reason = parse_spec(t)
            self.assertIsNone(spec, t)
            self.assertTrue(reason)

    def test_parse_wanted(self):
        self.assertEqual(parse_wanted("1L", 2), Spec(1000, "ml", 2))
        with self.assertRaises(ValueError):
            parse_wanted("많이", 1)
