# Replaces the Jawi company name (previously set in Noto Naskh Arabic from Google Fonts) with outlined
# letters in one cached file, site/assets/logo/jawi.svg, shown through a CSS mask so it still takes the
# text colour (header grey, footer light). The site then makes no request to Google Fonts.
# Edits every page in place (header + footer span, font <link>, preconnect), plus the business card pages in
# site/card/ (their <p class="jawi"> heading), and owns the .jawi rule in styles.css.
# Safe to run again: a second run changes nothing.
# Needs: pip install fonttools uharfbuzz, and tools/fonts/NotoNaskhArabic[wght].ttf (build input only, not shipped).
# Run: ~/.venvs/bws-card/bin/python tools/make_jawi.py
import glob, io, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.join(HERE, "..", "site")
FONT = os.path.join(HERE, "fonts", "NotoNaskhArabic[wght].ttf")
CSS = os.path.join(SITE_DIR, "assets", "css", "styles.css")
SVG_OUT = os.path.join(SITE_DIR, "assets", "logo", "jawi.svg")
JAWI = "كجروتران بي دبليو إيس سندیریان برحد"
WEIGHT = 500
# The old text used line-height 1.5, so the SVG's viewBox is that line box: 1.5em tall in font units. A 1.5em
# tall mask then draws the letters at exactly the font's size and the element keeps its old height.
# Baseline: measured in Chrome (2x screenshots, before vs after), the old text sat about 100 units (1.3 CSS px
# at 0.82rem) lower than Naskh's own half-leading would put it, because the Google subset had no space glyph,
# so the line's strut came from the serif fallback. Putting the baseline at the font ascent (1069 of 1500 units
# from the top) reproduces that position, and the ink (674 up, 431 down) still fits the box exactly.
LINE = 1.5

TAG = f'<span class="jawi" role="img" lang="ms-Arab" aria-label="{JAWI}"></span>'
SPAN_RE = re.compile(r'<span class="jawi" dir="rtl" lang="ms-Arab">' + re.escape(JAWI) + r"</span>")
CARD_TAG = f'<p class="jawi" role="img" lang="ms-Arab" aria-label="{JAWI}"></p>'
CARD_RE = re.compile(r'<p class="jawi" lang="ar" dir="rtl">' + re.escape(JAWI) + r"</p>")
FONT_LINK_RE = re.compile(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2\?family=Noto\+Naskh\+Arabic[^"]*">\n')
PRECONNECT_RE = re.compile(r'<link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin>\n')
CSS_RULE_RE = re.compile(r"^\.jawi \{[^}\n]*\}$", re.M)
FONT_VAR_RE = re.compile(r"^[ \t]*--font-jawi:[^;\n]*;[^\n]*\n", re.M)


def relative_pen(glyph_set):
    """A fontTools pen writing SVG path data with relative commands on whole font units. Relative deltas are
    short, which makes the file about 40% smaller than absolute coordinates. Points are rounded in absolute
    space first, so rounding never drifts along a contour."""
    from fontTools.pens.basePen import BasePen

    class Pen(BasePen):
        def __init__(self):
            super().__init__(glyph_set)  # resolves composite glyphs (e.g. alef + hamza below)
            self.out, self.cur, self.start = [], (0, 0), (0, 0)

        def _emit(self, cmd, pts):
            pts = [(round(x), round(y)) for x, y in pts]
            cx, cy = self.cur
            if cmd == "l" and pts[0][1] == cy:
                cmd, nums = "h", [pts[0][0] - cx]
            elif cmd == "l" and pts[0][0] == cx:
                cmd, nums = "v", [pts[0][1] - cy]
            else:
                nums = [v for x, y in pts for v in (x - cx, y - cy)]
            text = cmd
            for i, n in enumerate(nums):
                text += ("" if i == 0 or n < 0 else " ") + str(n)
            self.out.append(text)
            self.cur = pts[-1]

        def _moveTo(self, p):
            self._emit("m", [p])
            self.start = self.cur

        def _lineTo(self, p):
            self._emit("l", [p])

        def _qCurveToOne(self, p1, p2):
            self._emit("q", [p1, p2])

        def _curveToOne(self, p1, p2, p3):
            self._emit("c", [p1, p2, p3])

        def _closePath(self):
            self.out.append("z")
            self.cur = self.start

        def getCommands(self):
            return "".join(self.out)

    return Pen()


def outline(text=JAWI, font_path=FONT, weight=WEIGHT):
    """Shape the text with HarfBuzz and return (path d, advance width, ascent, descent, units per em)."""
    import uharfbuzz as hb
    from fontTools.pens.transformPen import TransformPen
    from fontTools.ttLib import TTFont
    from fontTools.varLib.instancer import instantiateVariableFont

    font = TTFont(font_path)
    if "fvar" in font:
        font = instantiateVariableFont(font, {"wght": weight})  # static 500 instance; shaped and drawn below
    data = io.BytesIO()
    font.save(data)
    font = TTFont(io.BytesIO(data.getvalue()))  # reload so glyph set and HarfBuzz see the same compiled instance
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()  # Arabic script, right to left
    hb.shape(hb.Font(hb.Face(data.getvalue())), buf, {})
    glyphs, order = font.getGlyphSet(), font.getGlyphOrder()
    x, pen = 0, relative_pen(glyphs)
    # For a right-to-left buffer HarfBuzz returns glyphs in visual order (leftmost first, last character
    # first) with positive advances, so drawing them left to right gives the name as it reads on screen.
    # The y flip turns font units (y up) into SVG units (y down) with the baseline at y = 0.
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        glyphs[order[info.codepoint]].draw(TransformPen(pen, (1, 0, 0, -1, x + pos.x_offset, -pos.y_offset)))
        x += pos.x_advance
    return pen.getCommands(), x, font["hhea"].ascent, font["hhea"].descent, font["head"].unitsPerEm


def num(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def build_svg():
    d, width, asc, desc, upm = outline()
    height = LINE * upm
    top = asc  # baseline offset from the top of the box (see LINE)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 {num(-top)} {width} {num(height)}">'
            f'<path d="{d}"/></svg>\n')


def rewrite_page(doc):
    doc = PRECONNECT_RE.sub("", doc)
    doc = FONT_LINK_RE.sub("", doc)
    doc = CARD_RE.sub(CARD_TAG, doc)
    return SPAN_RE.sub(TAG, doc)


def rewrite_css(css, width, height, upm):
    """Replace the single-line .jawi rule (old or already rewritten) and drop the unused --font-jawi.
    height is the SVG viewBox height in font units, so the box is height/upm em tall and the letters keep
    the font's size; aspect-ratio gives the width. The mask is sized by height, not 'contain', so a narrow
    container can never shrink the letters."""
    rule = (f".jawi {{ display: block; align-self: flex-start; height: {height / upm:.3f}em; "
            f"aspect-ratio: {width:.0f} / {height:.0f}; font-size: 0.82rem; color: var(--steel-600); "
            f"background-color: currentColor; "
            f'-webkit-mask: url("../logo/jawi.svg") no-repeat 0 0 / auto 100%; '
            f'mask: url("../logo/jawi.svg") no-repeat 0 0 / auto 100%; }}')
    out, n = CSS_RULE_RE.subn(lambda m: rule, css, count=1)
    if n != 1:
        raise SystemExit("make_jawi: .jawi rule not found in styles.css")
    return FONT_VAR_RE.sub("", out)


def pages():
    return sorted(glob.glob(os.path.join(SITE_DIR, "*.html")) + glob.glob(os.path.join(SITE_DIR, "ms", "*.html"))
                  + glob.glob(os.path.join(SITE_DIR, "card", "*.html")))


if __name__ == "__main__":
    d, width, asc, desc, upm = outline()
    with open(SVG_OUT, "w", encoding="utf-8") as f:
        f.write(build_svg())
    with open(CSS, encoding="utf-8") as f:
        css = f.read()
    with open(CSS, "w", encoding="utf-8") as f:
        f.write(rewrite_css(css, width, LINE * upm, upm))
    changed = 0
    for p in pages():
        with open(p, encoding="utf-8") as f:
            doc = f.read()
        new = rewrite_page(doc)
        if new != doc:
            with open(p, "w", encoding="utf-8") as f:
                f.write(new)
            changed += 1
    print(f"jawi.svg {os.path.getsize(SVG_OUT)} bytes, {changed} pages updated")
