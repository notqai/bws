import os
import unittest

import make_jawi

PAGE = (
    '<head>\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@500&display=swap&text=%D9%83">\n'
    '<link rel="stylesheet" href="assets/css/styles.css">\n'
    '</head><body>\n'
    f'<span class="jawi" dir="rtl" lang="ms-Arab">{make_jawi.JAWI}</span>\n'
    f'<span class="jawi" dir="rtl" lang="ms-Arab">{make_jawi.JAWI}</span>\n'
    '</body>'
)
CSS = ".a { x: 1; }\n.jawi { font-family: var(--font-jawi); font-weight: 500; font-size: 0.82rem; line-height: 1.5; color: var(--steel-600); text-align: left; }\n.b { y: 2; }\n"


class RewriteTests(unittest.TestCase):
    def test_page_has_no_google_fonts_or_text_span(self):
        out = make_jawi.rewrite_page(PAGE)
        self.assertNotIn("fonts.g", out)
        self.assertNotIn('<span class="jawi" dir="rtl"', out)
        self.assertEqual(out.count(make_jawi.TAG), 2)
        self.assertIn('<link rel="stylesheet" href="assets/css/styles.css">', out)

    def test_card_heading_rewritten(self):
        card = PAGE.replace("<body>", f'<body><p class="jawi" lang="ar" dir="rtl">{make_jawi.JAWI}</p>')
        out = make_jawi.rewrite_page(card)
        self.assertEqual(out.count(make_jawi.CARD_TAG), 1)
        self.assertNotIn('dir="rtl"', out)
        self.assertEqual(out, make_jawi.rewrite_page(out))

    def test_rewrite_is_idempotent(self):
        once = make_jawi.rewrite_page(PAGE)
        self.assertEqual(once, make_jawi.rewrite_page(once))

    def test_tag_keeps_the_name_for_assistive_tech(self):
        self.assertIn(f'aria-label="{make_jawi.JAWI}"', make_jawi.TAG)
        self.assertIn('role="img"', make_jawi.TAG)
        self.assertIn('lang="ms-Arab"', make_jawi.TAG)

    def test_css_rule_replaced(self):
        out = make_jawi.rewrite_css(CSS, 1234.0, 300.0, 1000)
        self.assertIn(".a { x: 1; }", out)
        self.assertIn(".b { y: 2; }", out)
        self.assertNotIn("--font-jawi", out)
        self.assertIn("aspect-ratio: 1234 / 300", out)
        self.assertIn("height: 0.300em", out)
        self.assertIn('mask: url("../logo/jawi.svg")', out)

    def test_css_rewrite_is_idempotent_and_drops_font_var(self):
        css = ":root {\n  --font-head: x;\n  --font-jawi: \"Noto Naskh Arabic\", serif;\n}\n" + CSS
        once = make_jawi.rewrite_css(css, 1234.0, 300.0, 1000)
        self.assertNotIn("--font-jawi", once)
        self.assertIn("--font-head: x;", once)
        self.assertEqual(once, make_jawi.rewrite_css(once, 1234.0, 300.0, 1000))


@unittest.skipUnless(os.path.exists(make_jawi.FONT), "source font not downloaded")
class OutlineTests(unittest.TestCase):
    def test_outline_produces_paths(self):
        d, width, asc, desc, upm = make_jawi.outline()
        self.assertGreater(len(d), 500)
        self.assertGreater(width, 0)
        self.assertGreater(asc, 0)
        self.assertLess(desc, 0)

    def test_svg_is_a_single_path(self):
        svg = make_jawi.build_svg()
        self.assertTrue(svg.startswith('<svg xmlns="http://www.w3.org/2000/svg"'))
        self.assertEqual(svg.count("<path"), 1)


if __name__ == "__main__":
    unittest.main()
