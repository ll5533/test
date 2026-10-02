import json
import unittest
from pathlib import Path

from pricefinder.search import DEFAULT_DATA, search
from pricefinder.spec import parse_wanted

LISTINGS = json.loads(Path(DEFAULT_DATA).read_text(encoding="utf-8"))


class SearchTest(unittest.TestCase):
    def test_only_exact_milk_1l(self):
        matched, _ = search(LISTINGS, "우유", "매일", parse_wanted("1000ml", 1))
        self.assertEqual([m["price"] for m in matched], [2390, 2480, 2650])

    def test_no_other_sizes_leak(self):
        matched, excluded = search(LISTINGS, "우유", "매일", parse_wanted("1L", 1))
        titles = " ".join(m["title"] for m in matched)
        for bad in ["500ml", "300ml", "250ml", "x 2", "증정", "택1", "서울"]:
            self.assertNotIn(bad, titles)
        self.assertTrue(excluded)

    def test_haetban_12(self):
        matched, _ = search(LISTINGS, "햇반", "CJ", parse_wanted("210g", 12))
        self.assertEqual([m["price"] for m in matched], [13900, 14500, 15200])


if __name__ == "__main__":
    unittest.main()
