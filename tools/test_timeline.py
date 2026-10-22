"""Tests for the "Since 2002" timeline on the About page (English and Bahasa Melayu).

tools/generate_site.py rebuilds the whole site when imported (it has no __main__ guard), so importing it from a
test would rewrite site/. Instead TIMELINE is read by parsing the file with ast: no side effects, and the test
still checks the one list the generator itself uses.
"""
import ast
import html
import re
import unittest
from pathlib import Path

import ms_strings

TOOLS = Path(__file__).resolve().parent
SITE = TOOLS.parent / "site"


def load_timeline():
    tree = ast.parse((TOOLS / "generate_site.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "TIMELINE" for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError("TIMELINE not found in generate_site.py")


def page(path):
    return (SITE / path).read_text(encoding="utf-8")


def rows_of(text):
    ol = re.search(r'<ol class="timeline">(.*?)</ol>', text, re.S)
    assert ol, "no <ol class=\"timeline\"> on the page"
    return [(dt, html.unescape(label), html.unescape(body)) for dt, label, body in
            re.findall(r'<time datetime="([^"]+)">(.*?)</time><p>(.*?)</p>', ol.group(1), re.S)]


class TimelineTests(unittest.TestCase):
    def test_timeline_has_nine_rows(self):
        self.assertEqual(len(load_timeline()), 9)

    def test_english_rows_render_in_order(self):
        self.assertEqual(rows_of(page("about.html")), [(d, l, t) for d, l, t in load_timeline()])

    def test_malay_rows_translated_in_order(self):
        got = rows_of(page("ms/about.html"))
        self.assertEqual(len(got), len(load_timeline()))
        for (dt, label, text), (mdt, mlabel, mtext) in zip(load_timeline(), got):
            self.assertEqual(mdt, dt)
            self.assertEqual(mtext, ms_strings.MS[text])
            self.assertNotEqual(mtext, text, f"untranslated: {text}")
            self.assertIn(mlabel, (label, ms_strings.MS.get(label)))
        self.assertEqual(got[0][1], "Okt 2002")
        self.assertIn("Sejak 2002", page("ms/about.html"))

    def test_section_follows_who_we_are(self):
        for path in ("about.html", "ms/about.html"):
            text = page(path)
            who, hist, obj = (text.index(f'id="{i}"') for i in ("profile-title", "history-title", "obj-title"))
            self.assertLess(who, hist)
            self.assertLess(hist, obj)
            self.assertEqual(text.count('class="timeline"'), 1)


if __name__ == "__main__":
    unittest.main()
