import unittest
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent / "site"
PAGE = (SITE / "card" / "mazinah.html")


class CardPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8")

    def test_noindex(self):
        self.assertIn('<meta name="robots" content="noindex">', self.html)

    def test_not_in_sitemap_or_robots(self):
        self.assertNotIn("card/", (SITE / "sitemap.xml").read_text(encoding="utf-8"))

    def test_primary_action_and_quick_links(self):
        for needle in [
            'href="mazinah.vcf"',
            'href="tel:+60198894946"',
            'href="https://wa.me/60198894946"',
            'href="mailto:mazinahmasribws@gmail.com"',
            'href="https://www.bwsengineeringsb.com"',
        ]:
            self.assertIn(needle, self.html)

    def test_both_offices_with_maps(self):
        self.assertIn("https://www.google.com/maps?cid=4214669276461699859", self.html)
        self.assertIn("https://www.google.com/maps?cid=6044021619715074034", self.html)
        self.assertIn("tel:+6085652743", self.html)
        self.assertIn("tel:+6086252476", self.html)

    def test_credentials(self):
        for needle in [
            "PETRONAS &amp; PETROS Licensed",
            "CIDB G7",
            "44 100 072059",
            "OHS 796482",
            "200201029529 (597192-V)",
        ]:
            self.assertIn(needle, self.html)

    def test_assets_exist(self):
        for rel in [
            "../assets/css/styles.css",
            "../assets/css/card.css",
            "../assets/logo/logo-white.svg",
            "mazinah.vcf",
            "mazinah-qr.svg",
        ]:
            self.assertIn(rel, self.html)
            self.assertTrue((PAGE.parent / rel).resolve().is_file(), rel)


if __name__ == "__main__":
    unittest.main()
