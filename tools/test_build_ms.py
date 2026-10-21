import os
import shutil
import tempfile
import unittest
from pathlib import Path

import build_ms

SITE = Path(__file__).resolve().parent.parent / "site"


def snapshot(root):
    return {p.relative_to(root): p.read_bytes() for p in Path(root).rglob("*.html")}


class IdempotentBuildTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.site = os.path.join(self.tmp, "site")
        shutil.copytree(SITE, self.site)
        self._orig = build_ms.SITE_DIR
        build_ms.SITE_DIR = self.site

    def tearDown(self):
        build_ms.SITE_DIR = self._orig
        shutil.rmtree(self.tmp)

    def test_second_run_changes_nothing(self):
        build_ms.build()
        first = snapshot(self.site)
        build_ms.build()
        self.assertEqual(first, snapshot(self.site))

    def test_no_whitespace_only_lines_added_by_switch(self):
        build_ms.build()
        build_ms.build()
        about = Path(self.site, "about.html").read_text(encoding="utf-8")
        self.assertNotIn("</nav>\n    \n", about)

    def test_map_title_attribute_is_translated(self):
        out = build_ms.translate_html('<div data-map-title="Map: BWS Engineering fabrication yard, Kidurong, Bintulu"></div>')
        self.assertIn('data-map-title="Peta: Limbungan fabrikasi BWS Engineering, Kidurong, Bintulu"', out)


if __name__ == "__main__":
    unittest.main()
