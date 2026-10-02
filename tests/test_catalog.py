import json
import tempfile
import unittest
from pathlib import Path

from pricefinder.catalog import CATALOG, build, validate, TEMPLATE

GOOD = {"item": "우유", "brand": "매일", "variant": "오리지널", "size": "1L", "count": 1,
        "name": "매일우유 오리지널 1L", "links": [{"mall": "쿠팡", "url": "https://example.com/a"}]}


def variant(**kw):
    return {**GOOD, **kw}


class ValidateTest(unittest.TestCase):
    def test_shipped_catalog_is_valid(self):
        products = json.loads(Path(CATALOG).read_text(encoding="utf-8"))
        self.assertEqual(validate(products), [])

    def test_good_entry_passes(self):
        self.assertEqual(validate([GOOD], strict=True), [])

    def test_name_spec_mismatch_is_caught(self):
        errors = validate([variant(name="매일우유 오리지널 500ml")])
        self.assertTrue(any("다름" in e for e in errors))

    def test_count_mismatch_is_caught(self):
        errors = validate([variant(count=2)])
        self.assertTrue(any("다름" in e for e in errors))

    def test_duplicate_even_if_written_differently(self):
        dup = variant(size="1000ml", name="매일우유 오리지널 1000ml")
        self.assertTrue(any("중복" in e for e in validate([GOOD, dup])))

    def test_link_rules(self):
        self.assertTrue(validate([variant(links=[{"mall": "쿠팡", "url": "http://x.com"}])]))
        self.assertTrue(validate([variant(links=[])]))
        empty = variant(links=[{"mall": "쿠팡", "url": ""}])
        self.assertEqual(validate([empty]), [])
        self.assertTrue(validate([empty], strict=True))

    def test_missing_field(self):
        bad = {k: v for k, v in GOOD.items() if k != "brand"}
        self.assertTrue(validate([bad]))


class BuildTest(unittest.TestCase):
    def test_build_embeds_data_safely(self):
        tricky = variant(name="매일우유 오리지널 1L </script>")
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "index.html"
            build([tricky], TEMPLATE, out)
            html = out.read_text(encoding="utf-8")
        self.assertNotIn("__CATALOG__", html)
        self.assertIn("<\\/script>", html)
        self.assertEqual(html.count("</script>"), 1)


if __name__ == "__main__":
    unittest.main()
