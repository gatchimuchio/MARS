"""史料正本のURL・取得ファイル・検証方法を独立にテストする。"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import archive_originals as archive  # noqa: E402


class SourceArchiveTests(unittest.TestCase):
    def setUp(self):
        self.catalog = archive.read_catalog(archive.REGISTER.read_text(encoding="utf-8"))

    def test_source_mother_set_is_35_distinct_ids(self):
        self.assertEqual(len(self.catalog), 35)
        self.assertEqual(set(self.catalog), {f"S{number:02d}" for number in range(1, 36)})

    def test_original_proper_names_not_synthetic_summaries(self):
        self.assertIn("穂坂衛", self.catalog["S31"].title)
        self.assertIn("大野豊", self.catalog["S32"].title)
        self.assertIn("尾関雅則", self.catalog["S33"].title)

    def test_rejects_non_official_url_and_unsafe_schemes(self):
        for url in (
            "file:///etc/passwd",
            "http://www.hitachihyoron.com/a.pdf",
            "https://127.0.0.1/private",
            "https://not-hitachihyoron.com/example.pdf",
            "https://www.hitachihyoron.com:8080/a.pdf",
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                archive.require_official_url(url)

    def test_lock_matches_current_original_urls(self):
        locked = archive.load_lock()["sources"]
        self.assertEqual(set(locked), set(self.catalog))
        for identifier, source in self.catalog.items():
            with self.subTest(identifier=identifier):
                self.assertEqual(locked[identifier]["url"], source.url)
                self.assertEqual(locked[identifier]["title"], source.title)
                self.assertGreater(len(locked[identifier]["captures"]), 0)
                for capture in locked[identifier]["captures"]:
                    self.assertRegex(capture["sha256"], r"^[0-9a-f]{64}$")
                    self.assertGreater(capture["bytes"], 0)


if __name__ == "__main__":
    unittest.main()
