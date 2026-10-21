# Group A: Speed & Infrastructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove all Google Maps and Google Fonts loading from first paint, shrink the photos, and make the site deploy-ready on Cloudflare Pages with analytics allowed, without changing any content.

**Architecture:** Plain static site in `site/` (no build step). Everything is produced by small Python scripts in `tools/` that edit or generate files in place. Tests are `unittest` files in `tools/`, run with the `bws-card` venv. The BM site (`site/ms/`) is produced from the EN pages by `tools/build_ms.py`.

**Tech Stack:** HTML/CSS/vanilla JS, Python 3 (stdlib + fontTools + uharfbuzz), cwebp 1.6, Lighthouse via npx.

**Spec:** `docs/superpowers/specs/2026-10-22-speed-infra-design.md`

**Deviations from the spec, decided while planning:**
1. **Location drawings live in a new `tools/make_locations.py`**, which imports the drawing helpers from `make_illustrations.py`. That file runs its writer loop at import time, so Task 2 first puts the loop behind `if __name__ == "__main__":`.
2. **The pin pulse is an HTML `<span>` animated by `styles.css`,** not CSS inside the SVG. Reduced-motion handling for SVG-as-`<img>` is inconsistent across browsers, while page CSS already follows the site's reduced-motion pattern.
3. **The Jawi name is one cached file, `site/assets/logo/jawi.svg`, shown through a CSS mask,** instead of inline SVG. Inline outlines would add about 2 × 8 KB to every page. A mask gives one cached request and still takes `currentColor`, so the header and footer colours keep working.
4. **New Task 1 fixes `build_ms.py`.** It currently adds two blank lines to every page on each run, so its output is never a clean diff.

**Commit messages:** no `Co-Authored-By` trailer (owner's preference).

**Run tests with:** `~/.venvs/bws-card/bin/python -m unittest discover -s tools -p "test_*.py"` from the repo root `~/bws`.

---

## File map

| File | Status | Responsibility |
|---|---|---|
| `tools/build_ms.py` | modify | idempotent language-switch insertion; translate `data-map-title` |
| `tools/test_build_ms.py` | create | re-running the BM build changes nothing |
| `tools/make_illustrations.py` | modify | `__main__` guard only |
| `tools/make_locations.py` | create | draws `loc-miri.svg`, `loc-bintulu.svg`; exposes `PINS` |
| `tools/test_make_locations.py` | create | SVGs are valid and carry the required labels |
| `site/contact.html` | modify | drawing cards replace the iframes |
| `site/assets/css/styles.css` | modify | map card, pulse, button; `.jawi` rule (owned by `make_jawi.py`) |
| `site/assets/js/main.js` | modify | click loads the iframe |
| `tools/ms_strings.py` | modify | 3 new BM strings |
| `tools/optimize_images.py` | create | re-encodes WebP, keeps a file only if smaller |
| `tools/test_optimize_images.py` | create | never grows a file, keeps dimensions |
| `tools/make_jawi.py` | create | outlines the name → `jawi.svg`; rewrites pages and the `.jawi` CSS |
| `tools/test_make_jawi.py` | create | page rewrite, no Google Fonts left |
| `tools/generate_site.py` | modify | template matches (not run) |
| `site/_headers` | create | Cloudflare Pages headers |
| `vercel.json`, `site/.htaccess` | modify | same CSP |
| `README.md` | modify | Pages analytics step, new tools |
| `.gitignore` | modify | ignore `tools/fonts/` |

---

### Task 0: Setup and baseline

**Files:** none committed, except `.gitignore`.

- [ ] **Step 1: Install Python dependencies into the existing venv**

```bash
~/.venvs/bws-card/bin/python -m pip install "fonttools==4.55.3" "uharfbuzz==0.45.0"
```
Expected: `Successfully installed fonttools-4.55.3 uharfbuzz-0.45.0`.

- [ ] **Step 2: Download the Jawi source font (build input only, never shipped)**

```bash
cd ~/bws && mkdir -p tools/fonts && curl -fsSL -o "tools/fonts/NotoNaskhArabic[wght].ttf" "https://github.com/google/fonts/raw/main/ofl/notonaskharabic/NotoNaskhArabic%5Bwght%5D.ttf" && ls -l tools/fonts
```
Expected: one `.ttf` file, roughly 200–400 KB.

- [ ] **Step 3: Ignore the font folder**

Append to `.gitignore`:
```
tools/fonts/
```

- [ ] **Step 4: Record the baseline Lighthouse runs and network requests**

```bash
cd ~/bws && (python3 -m http.server 8080 -d site >/dev/null 2>&1 &) && sleep 1
mkdir -p /private/tmp/claude-501/bws-lh
for p in "" contact.html; do
  npx -y lighthouse@12.6.1 "http://localhost:8080/$p" --only-categories=performance --output=json --quiet \
    --chrome-flags="--headless=new" --output-path="/private/tmp/claude-501/bws-lh/before-${p:-index}.json"
done
python3 - <<'EOF'
import json, glob
for f in sorted(glob.glob("/private/tmp/claude-501/bws-lh/before-*.json")):
    r = json.load(open(f)); items = r["audits"]["network-requests"]["details"]["items"]
    print(f.split("/")[-1], "score", round(r["categories"]["performance"]["score"]*100),
          "requests", len(items), "KB", round(sum(i.get("transferSize", 0) for i in items)/1024),
          "google", sum("google" in i["url"] or "gstatic" in i["url"] for i in items))
EOF
```
Expected: one line per page. Note the numbers for the final report. `contact` should show several `google` requests.

- [ ] **Step 5: Commit**

```bash
git add .gitignore && git commit -m "Ignore build-only font folder"
```

---

### Task 1: Make `build_ms.py` idempotent and translate `data-map-title`

**Files:**
- Modify: `tools/build_ms.py:63` and `tools/build_ms.py:108`
- Test: `tools/test_build_ms.py`

- [ ] **Step 1: Write the failing test**

`tools/test_build_ms.py`:
```python
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
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `~/.venvs/bws-card/bin/python -m unittest tools/test_build_ms.py -v` (from `~/bws`, after `cd tools` if import fails; or `-s tools` discovery as above)
Expected: FAIL on `test_second_run_changes_nothing`, `test_no_whitespace_only_lines_added_by_switch` and `test_map_title_attribute_is_translated`.

- [ ] **Step 3: Fix the removal regex**

The inserter (line 98–99) writes `switch + "\n    "` before the CTA and the toggle. The remover must take that trailing newline and indent too. In `tools/build_ms.py`, replace line 108:
```python
            en = re.sub(r'\n?<a class="lang-switch[^>]*>.*?</a>', "", en)
```
with:
```python
            en = re.sub(r'<a class="lang-switch[^>]*>.*?</a>\n[ \t]*', "", en)
```

- [ ] **Step 4: Translate `data-map-title`**

Replace line 63:
```python
        seg = re.sub(r'\b(alt|aria-label|placeholder|title|data-title|content)="([^"]*)"', tr_attr, seg)
```
with:
```python
        seg = re.sub(r'\b(alt|aria-label|placeholder|title|data-title|data-map-title|content)="([^"]*)"', tr_attr, seg)
```

- [ ] **Step 5: Run the tests and confirm they pass**

Run: `~/.venvs/bws-card/bin/python -m unittest discover -s tools -p "test_*.py" -v`
Expected: all PASS, including the existing card tests.

- [ ] **Step 6: Confirm the real site rebuilds with no diff**

```bash
cd ~/bws && python3 tools/build_ms.py && git status --short site
```
Expected: no output from `git status`. If pages show as modified, run `git diff site | head -40`. The fix must reproduce the committed pages exactly, so stop and investigate before continuing.

- [ ] **Step 7: Commit**

```bash
git add tools/build_ms.py tools/test_build_ms.py
git commit -m "Make the BM build idempotent and translate map titles"
```

---

### Task 2: Guard `make_illustrations.py` so it can be imported

**Files:** Modify `tools/make_illustrations.py` (the final `for name, fn in [...]` loop).

- [ ] **Step 1: Wrap the writer loop**

Replace the final block:
```python
for name, fn in [("plant", plant), ("crane-lift", crane), ("workshop", building), ("offshore", platform),
                 ("hard-hat", hardhat), ("tools", tools), ("coast-map", coast_map),
                 ("blasting-painting", blasting), ("cable-laying", cable), ("instrument-calibration", calibration)]:
    svg = fn()
    with open(os.path.join(OUT, name + ".svg"), "w") as f:
        f.write(svg)
    print(name, len(svg))
```
with:
```python
if __name__ == "__main__":
    for name, fn in [("plant", plant), ("crane-lift", crane), ("workshop", building), ("offshore", platform),
                     ("hard-hat", hardhat), ("tools", tools), ("coast-map", coast_map),
                     ("blasting-painting", blasting), ("cable-laying", cable), ("instrument-calibration", calibration)]:
        svg = fn()
        with open(os.path.join(OUT, name + ".svg"), "w") as f:
            f.write(svg)
        print(name, len(svg))
```

- [ ] **Step 2: Verify the output is unchanged and the import is silent**

```bash
cd ~/bws && python3 tools/make_illustrations.py >/dev/null && git status --short site/assets/illustrations
cd tools && python3 -c "import make_illustrations" && echo "import ok, nothing printed above"
```
Expected: `git status` prints nothing, then `import ok, nothing printed above`.

- [ ] **Step 3: Commit**

```bash
git add tools/make_illustrations.py && git commit -m "Allow importing the illustration helpers without regenerating"
```

---

### Task 3: Location drawings

**Files:**
- Create: `tools/make_locations.py`
- Create: `site/assets/illustrations/loc-miri.svg`, `site/assets/illustrations/loc-bintulu.svg` (generated)
- Test: `tools/test_make_locations.py`

- [ ] **Step 1: Write the failing test**

`tools/test_make_locations.py`:
```python
import unittest
import xml.etree.ElementTree as ET

import make_locations

NS = "{http://www.w3.org/2000/svg}"


class LocationDrawingTests(unittest.TestCase):
    def check(self, svg, must_contain):
        root = ET.fromstring(svg)  # well-formed XML
        self.assertEqual(root.get("viewBox"), "0 0 800 500")
        self.assertIsNotNone(root.find(NS + "title"))
        for s in must_contain:
            self.assertIn(s, svg)

    def test_miri(self):
        self.check(make_locations.miri(), ["DWG BWS-LOC-01", "MIRI HQ", "PIASAU INDUSTRIAL ESTATE PH III",
                                           "JLN PRUNUS 1", "LOT 1743", "NOT TO SCALE", "4.4469° N  114.0116° E"])

    def test_bintulu(self):
        self.check(make_locations.bintulu(), ["DWG BWS-LOC-02", "BINTULU", "KIDURONG INDUSTRIAL ESTATE",
                                              "LOT 782", "LOT 124–128", "NOT TO SCALE", "3.2725° N  113.0802° E"])

    def test_pins_are_inside_the_drawing_area(self):
        for name, (x, y) in make_locations.PINS.items():
            self.assertTrue(0 < x < 800 and 0 < y < 430, name)  # above the title block

    def test_pin_percentages(self):
        self.assertEqual(make_locations.pin_style("miri"), "--pin-x:70%;--pin-y:70%")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `~/.venvs/bws-card/bin/python -m unittest discover -s tools -p "test_make_locations.py" -v`
Expected: ERROR `No module named 'make_locations'`.

- [ ] **Step 3: Write `tools/make_locations.py`**

```python
# Generates the "site drawing" cards shown on the contact page in place of the Google maps, until the
# visitor clicks "Load interactive map". Same blueprint style as make_illustrations.py, 800 x 500 (16:10).
# Layouts are schematic (marked NOT TO SCALE): real coordinates and lot numbers, simplified roads and coast.
# Output: ../site/assets/illustrations/loc-miri.svg, loc-bintulu.svg
# Run: python3 tools/make_locations.py
import os

from make_illustrations import INK, BLUE, SKY, CYAN, FONT, OUT, line, rect, circle, text

W, H = 800, 500
MONO = 'font-family="ui-monospace, Menlo, Consolas, monospace"'
# Pin tip positions in drawing units; contact.html places the pulse ring here (see pin_style).
PINS = {"miri": (560, 350), "bintulu": (430, 330)}


def pin_style(key):
    x, y = PINS[key]
    return f"--pin-x:{round(x / W * 100)}%;--pin-y:{round(y / H * 100)}%"


def sheet(body, title):
    grid = []
    for x in range(0, W + 1, 20):
        grid.append(f'<path d="M{x} 0V{H}" stroke="{SKY}" stroke-opacity="{.16 if x % 100 == 0 else .06}"/>')
    for y in range(0, H + 1, 20):
        grid.append(f'<path d="M0 {y}H{W}" stroke="{SKY}" stroke-opacity="{.16 if y % 100 == 0 else .06}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{title}">'
            f'<title>{title}</title><rect width="{W}" height="{H}" fill="{INK}"/>'
            f'<g stroke-width="1">{"".join(grid)}</g>'
            f'<g fill="none" stroke-linecap="round" stroke-linejoin="round">{body}</g></svg>')


def rtext(x, y, s, angle, size=11, color=SKY):
    return (f'<text x="{x}" y="{y}" {FONT} font-size="{size}" font-weight="600" letter-spacing="2" fill="{color}" '
            f'stroke="none" text-anchor="middle" transform="rotate({angle} {x} {y})">{s}</text>')


def sea(coast_d, label_x, label_y):
    """Coastline path along the top of the sheet, wave strokes above it and the sea label."""
    out = f'<path d="{coast_d}" stroke="{CYAN}" stroke-width="2.5"/>'
    for y in (34, 62, 90):
        for x in range(30 + (y % 40), W - 40, 90):
            out += f'<path d="M{x} {y}q10 -7 20 0t20 0" stroke="{SKY}" stroke-width="1.2" stroke-opacity=".45"/>'
    return out + text(label_x, label_y, "SOUTH CHINA SEA", 12, SKY, "start", 700, 4)


def road(pts, w=16):
    """Double-line road: a wide cyan stroke with the ink sheet colour drawn down the middle."""
    return line(pts, CYAN, w, .9) + line(pts, INK, w - 4) + line(pts, SKY, 1, .5, dash="10 8")


def lots(x0, y0, cols, rows, w, h, gap=10):
    """Neighbouring plots in the estate, drawn faint and dashed."""
    out = ""
    for c in range(cols):
        for r in range(rows):
            out += rect(x0 + c * (w + gap), y0 + r * (h + gap), w, h, SKY, 1, "none", .35)
    return out


def plot(x, y, w, h, label, lx=None, ly=None):
    """The BWS plot: brand-blue fill, cyan outline, label underneath."""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{BLUE}" fill-opacity=".55" stroke="{CYAN}" stroke-width="2"/>'
            + text(lx if lx is not None else x + w / 2, ly if ly is not None else y + h + 18, label, 11, CYAN, "middle", 700, 2))


def pin(x, y):
    """Map pin whose tip touches (x, y)."""
    return (f'<path d="M{x} {y}c-4-10-18-22-18-36a18 18 0 0 1 36 0c0 14-14 26-18 36z" fill="{CYAN}" stroke="{INK}" stroke-width="2"/>'
            + circle(x, y - 36, 7, INK, 0, INK))


def north_arrow(x, y):
    return (circle(x, y, 22, SKY, 1.2, "none", .7)
            + f'<path d="M{x} {y - 18}l9 26-9-6-9 6z" fill="{CYAN}" stroke="none"/>'
            + text(x, y - 28, "N", 12, CYAN, "middle", 700, 0))


def scale_bar(x, y):
    out = ""
    for i in range(4):
        out += f'<rect x="{x + i * 30}" y="{y}" width="30" height="6" fill="{CYAN if i % 2 == 0 else INK}" stroke="{CYAN}" stroke-width="1"/>'
    return out + text(x, y - 8, "SCHEMATIC · NOT TO SCALE", 10, SKY, "start", 600, 2)


def coords(x, y, s):
    return (f'<text x="{x}" y="{y}" {MONO} font-size="12" font-weight="600" letter-spacing="1" fill="{CYAN}" '
            f'stroke="none" text-anchor="end">{s}</text>')


def title_block(dwg, site):
    """Engineering title block along the bottom. The right-hand cell is left blank: the HTML button sits there."""
    y, h = 440, 44
    out = rect(20, y, 760, h, CYAN, 1.5, INK)
    for x in (230, 430, 530):
        out += line([(x, y), (x, y + h)], CYAN, 1.5)
    out += text(36, y + 28, f"DWG {dwg}", 13, CYAN, "start", 700, 2)
    out += text(246, y + 28, site, 13, CYAN, "start", 700, 2)
    out += text(446, y + 28, "REV A", 13, SKY, "start", 700, 2)
    return out


def miri():
    b = sea("M0 128C160 96 300 140 460 118S700 84 800 104", 40, 70)
    b += road([(0, 250), (800, 250)])                       # estate trunk road
    b += road([(470, 250), (470, 430)])                     # Jalan Prunus 1
    b += rtext(452, 345, "JLN PRUNUS 1", -90)
    b += lots(40, 160, 6, 1, 60, 70) + lots(40, 280, 6, 2, 60, 55)
    b += lots(500, 160, 4, 1, 60, 70) + lots(650, 290, 2, 2, 50, 55)
    b += plot(500, 300, 120, 80, "LOT 1743")
    b += text(40, 410, "PIASAU INDUSTRIAL ESTATE PH III", 12, SKY, "start", 700, 3)
    b += pin(*PINS["miri"])
    b += north_arrow(740, 190) + scale_bar(40, 372) + coords(780, 420, "4.4469° N  114.0116° E")
    b += title_block("BWS-LOC-01", "MIRI HQ")
    return sheet(b, "Site drawing of the BWS Engineering main office location, Piasau Industrial Estate, Miri")


def bintulu():
    b = sea("M0 120C140 150 280 104 430 126S690 150 800 112", 40, 70)
    b += road([(0, 230), (800, 230)])                       # Jalan Tanjung Kidurong
    b += text(40, 214, "JLN TANJUNG KIDURONG", 11, SKY, "start", 600, 2)
    b += road([(330, 230), (330, 430)])                     # Jalan Kidurong
    b += rtext(312, 345, "JLN KIDURONG", -90)
    b += lots(40, 260, 4, 2, 60, 55) + lots(560, 160, 3, 1, 60, 55)
    b += plot(370, 260, 110, 70, "LOT 782 · OFFICE")
    b += plot(540, 280, 200, 110, "LOT 124–128 · FABRICATION YARD", ly=408)
    b += text(40, 160, "KIDURONG INDUSTRIAL ESTATE", 12, SKY, "start", 700, 3)
    b += pin(*PINS["bintulu"])
    b += north_arrow(740, 190) + scale_bar(40, 410) + coords(780, 428, "3.2725° N  113.0802° E")
    b += title_block("BWS-LOC-02", "BINTULU")
    return sheet(b, "Site drawing of the BWS Engineering office and fabrication yard location, Kidurong, Bintulu")


if __name__ == "__main__":
    for name, fn in [("loc-miri", miri), ("loc-bintulu", bintulu)]:
        svg = fn()
        with open(os.path.join(OUT, name + ".svg"), "w") as f:
            f.write(svg)
        print(name, len(svg), pin_style(name[4:]))
```

- [ ] **Step 4: Run the tests and confirm they pass**

Run: `~/.venvs/bws-card/bin/python -m unittest discover -s tools -p "test_make_locations.py" -v`
Expected: 4 PASS. If `test_pin_percentages` fails, the expected string must equal `pin_style("miri")` for `PINS["miri"] = (560, 350)`: `--pin-x:70%;--pin-y:70%`.

- [ ] **Step 5: Generate the SVGs and look at them**

```bash
cd ~/bws && python3 tools/make_locations.py
```
Expected:
```
loc-miri <bytes> --pin-x:70%;--pin-y:70%
loc-bintulu <bytes> --pin-x:54%;--pin-y:66%
```
Open both files in a browser (`open site/assets/illustrations/loc-miri.svg`). Check:
- no text overlaps a road or another label
- the plots read clearly against the faint lots
- the right-hand title-block cell (x 530–780) is empty

If a label collides, nudge only its `x`/`y` in `miri()`/`bintulu()`, re-run, and re-run the tests.

- [ ] **Step 6: Commit**

```bash
git add tools/make_locations.py tools/test_make_locations.py site/assets/illustrations/loc-miri.svg site/assets/illustrations/loc-bintulu.svg
git commit -m "Add blueprint site drawings for the two office locations"
```

---

### Task 4: Contact page drawing cards (markup, CSS, JS, BM)

**Files:**
- Modify: `site/contact.html:109` and `site/contact.html:123`
- Modify: `site/assets/css/styles.css:484-485`
- Modify: `site/assets/js/main.js` (before the final `})();`)
- Modify: `tools/ms_strings.py` (next to line 570)
- Regenerate: `site/ms/*` via `tools/build_ms.py`

- [ ] **Step 1: Replace the Miri iframe**

In `site/contact.html`, replace line 109:
```html
        <div class="map-wrap"><iframe class="map" src="https://maps.google.com/maps?q=4.446917,114.011563&z=17&hl=en&output=embed" title="Map: BWS Engineering main office, Piasau Industrial Estate, Miri" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div>
```
with:
```html
        <div class="map-wrap" style="--pin-x:70%;--pin-y:70%" data-map-src="https://maps.google.com/maps?q=4.446917,114.011563&amp;z=17&amp;hl=en&amp;output=embed" data-map-title="Map: BWS Engineering main office, Piasau Industrial Estate, Miri">
          <img class="map-drawing" src="assets/illustrations/loc-miri.svg" alt="Site drawing of the BWS Engineering main office location, Piasau Industrial Estate, Miri" width="800" height="500" loading="lazy" decoding="async">
          <span class="map-pulse" aria-hidden="true"></span>
          <button type="button" class="btn btn--light map-load">Load interactive map</button>
        </div>
```

- [ ] **Step 2: Replace the Bintulu iframe**

Replace line 123 (now shifted by 4 lines; match on content):
```html
        <div class="map-wrap"><iframe class="map" src="https://maps.google.com/maps?q=3.2724729,113.0802423&z=17&hl=en&output=embed" title="Map: BWS Engineering fabrication yard, Kidurong, Bintulu" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div>
```
with:
```html
        <div class="map-wrap" style="--pin-x:54%;--pin-y:66%" data-map-src="https://maps.google.com/maps?q=3.2724729,113.0802423&amp;z=17&amp;hl=en&amp;output=embed" data-map-title="Map: BWS Engineering fabrication yard, Kidurong, Bintulu">
          <img class="map-drawing" src="assets/illustrations/loc-bintulu.svg" alt="Site drawing of the BWS Engineering office and fabrication yard location, Kidurong, Bintulu" width="800" height="500" loading="lazy" decoding="async">
          <span class="map-pulse" aria-hidden="true"></span>
          <button type="button" class="btn btn--light map-load">Load interactive map</button>
        </div>
```
The `--pin-*` values must match what `make_locations.py` printed in Task 3 Step 5.

- [ ] **Step 3: CSS**

In `site/assets/css/styles.css`, replace lines 484–485:
```css
.map { width: 100%; aspect-ratio: 16 / 10; border: 0; background: var(--steel-100); }
.map-wrap { margin-top: auto; border-top: 1px solid var(--steel-200); }
```
with:
```css
.map { display: block; width: 100%; aspect-ratio: 16 / 10; border: 0; background: var(--steel-100); }
.map-wrap { position: relative; margin-top: auto; border-top: 1px solid var(--steel-200); background: var(--ink); }
/* Site drawing shown until the visitor loads the Google map (make_locations.py) */
.map-drawing { display: block; width: 100%; height: auto; aspect-ratio: 16 / 10; }
.map-pulse { position: absolute; left: var(--pin-x); top: var(--pin-y); width: 7%; aspect-ratio: 1; border: 2px solid var(--brand-sky); border-radius: 50%; transform: translate(-50%, -50%) scale(.4); opacity: 0; pointer-events: none; }
@media (prefers-reduced-motion: no-preference) { .map-pulse { animation: map-pulse 2.4s var(--ease) infinite; } }
@keyframes map-pulse { 0% { transform: translate(-50%, -50%) scale(.4); opacity: .9; } 100% { transform: translate(-50%, -50%) scale(2.4); opacity: 0; } }
.map-load { display: none; position: absolute; right: 3.5%; bottom: 2%; min-height: 40px; padding: .5rem 1rem; }
.js .map-load { display: inline-flex; }
@media (max-width: 30rem) { .map-load { right: 50%; transform: translateX(50%); bottom: 12%; } }
```
On narrow phones the title-block cell is too small for the button, so the button centres above the block.

- [ ] **Step 4: JS**

In `site/assets/js/main.js`, insert before the final `})();`:
```js

  /* ---- Contact: the site drawings swap in the Google map only when asked ---- */
  document.querySelectorAll(".map-wrap[data-map-src]").forEach(function (wrap) {
    var load = wrap.querySelector(".map-load");
    if (!load) return;
    load.addEventListener("click", function () {
      var frame = document.createElement("iframe");
      frame.className = "map";
      frame.src = wrap.getAttribute("data-map-src");
      frame.title = wrap.getAttribute("data-map-title");
      frame.setAttribute("referrerpolicy", "no-referrer-when-downgrade");
      wrap.replaceChildren(frame);
      frame.focus();
    });
  });
```
Also update the header comment on line 3 from `· gallery filter + lightbox · contact form · careers apply links */` to `· gallery filter + lightbox · contact form · map loader · careers apply links */`.

- [ ] **Step 5: BM strings**

In `tools/ms_strings.py`, directly after the line `"Map: BWS Engineering fabrication yard, Kidurong, Bintulu": "Peta: Limbungan fabrikasi BWS Engineering, Kidurong, Bintulu",` add:
```python
"Load interactive map": "Muatkan peta interaktif",
"Site drawing of the BWS Engineering main office location, Piasau Industrial Estate, Miri": "Lukisan tapak lokasi pejabat utama BWS Engineering, Kawasan Perindustrian Piasau, Miri",
"Site drawing of the BWS Engineering office and fabrication yard location, Kidurong, Bintulu": "Lukisan tapak lokasi pejabat dan limbungan fabrikasi BWS Engineering, Kidurong, Bintulu",
```

- [ ] **Step 6: Rebuild BM and check the diff is limited to the contact page**

```bash
cd ~/bws && python3 tools/build_ms.py && git status --short site
grep -c 'Muatkan peta interaktif\|Lukisan tapak' site/ms/contact.html
grep -o 'src="[^"]*loc-[a-z]*.svg"' site/ms/contact.html
```
Expected:
- `git status` lists only `site/contact.html` and `site/ms/contact.html`
- the count is `4`
- both image paths start with `../assets/illustrations/`

- [ ] **Step 7: Check it in a browser**

```bash
cd ~/bws && (python3 -m http.server 8080 -d site >/dev/null 2>&1 &) ; open "http://localhost:8080/contact.html"
```
Check:
- both drawings show, the pulse ring sits on the pin tip, and the button sits in the empty title-block cell
- clicking the button replaces the card with the Google map, and focus moves into it
- at 375 px wide (DevTools device mode) the button is centred and readable
- with DevTools → Rendering → "prefers-reduced-motion: reduce" the ring does not animate
- DevTools Network panel, filtered on `google`: nothing loads before the click
- `http://localhost:8080/ms/contact.html` shows "Muatkan peta interaktif"

If the ring is off the pin, adjust `PINS` in `make_locations.py`, regenerate, and update both `style="--pin-*"` values.

- [ ] **Step 8: Run all tests and commit**

```bash
~/.venvs/bws-card/bin/python -m unittest discover -s tools -p "test_*.py"
git add site/contact.html site/ms/contact.html site/assets/css/styles.css site/assets/js/main.js tools/ms_strings.py
git commit -m "Show site drawings on the contact page and load Google Maps on request"
```
Expected: `OK`.

---

### Task 5: Re-encode photos

**Files:**
- Create: `tools/optimize_images.py`
- Test: `tools/test_optimize_images.py`
- Modify (generated): `site/assets/img/*.webp`

- [ ] **Step 1: Write the failing test**

`tools/test_optimize_images.py`:
```python
import os
import random
import shutil
import subprocess
import tempfile
import unittest

import optimize_images


def make_ppm(path, w, h, seed=1):
    """Gradient plus noise, so quality settings make a real size difference."""
    rnd = random.Random(seed)
    rows = bytearray()
    for y in range(h):
        for x in range(w):
            n = rnd.randint(-25, 25)
            rows += bytes(max(0, min(255, v + n)) for v in (x * 255 // w, y * 255 // h, 128))
    with open(path, "wb") as f:
        f.write(f"P6 {w} {h} 255\n".encode() + rows)


def make_webp(path, w, h, q):
    with tempfile.TemporaryDirectory() as tmp:
        ppm = os.path.join(tmp, "src.ppm")
        make_ppm(ppm, w, h)
        subprocess.run(["cwebp", "-quiet", "-q", str(q), ppm, "-o", path], check=True)


class OptimiseTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_dims_reads_webp_header(self):
        p = os.path.join(self.dir, "a-800.webp")
        make_webp(p, 320, 200, 90)
        self.assertEqual(optimize_images.dims(p), (320, 200))

    def test_shrinks_heavy_files_and_keeps_dimensions(self):
        big = os.path.join(self.dir, "photo-1600.webp")
        mid = os.path.join(self.dir, "photo-800.webp")
        make_webp(big, 640, 400, 100)
        make_webp(mid, 320, 200, 100)
        before = {p: os.path.getsize(p) for p in (big, mid)}
        optimize_images.optimise(self.dir)
        for p in (big, mid):
            self.assertLess(os.path.getsize(p), before[p])
        self.assertEqual(optimize_images.dims(big), (640, 400))
        self.assertEqual(optimize_images.dims(mid), (320, 200))

    def test_never_grows_a_file(self):
        p = os.path.join(self.dir, "tiny-800.webp")
        make_webp(p, 320, 200, 5)
        before = os.path.getsize(p)
        optimize_images.optimise(self.dir)
        self.assertLessEqual(os.path.getsize(p), before)

    def test_ignores_other_files(self):
        other = os.path.join(self.dir, "og-image.jpg")
        open(other, "wb").write(b"not an image")
        rows = optimize_images.optimise(self.dir)
        self.assertEqual(rows, [])
        self.assertEqual(open(other, "rb").read(), b"not an image")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `~/.venvs/bws-card/bin/python -m unittest discover -s tools -p "test_optimize_images.py" -v`
Expected: ERROR `No module named 'optimize_images'`.

- [ ] **Step 3: Write `tools/optimize_images.py`**

```python
# Re-encodes the site's WebP photos (name-480/800/1600.webp) with tuned cwebp settings and keeps a
# file only if the new one is smaller. Smaller sizes are rebuilt from the largest sibling at their own
# pixel size, so the width/height in the HTML stay valid. og-image.jpg and client logos are not touched.
# Needs cwebp (brew install webp). Run: python3 tools/optimize_images.py
import os, re, shutil, subprocess, sys, tempfile

IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site", "assets", "img")
QUALITY = {480: 75, 800: 75, 1600: 72}
NAME_RE = re.compile(r"^(?P<stem>.+)-(?P<w>480|800|1600)\.webp$")


def dims(path):
    """(width, height) from the WebP header (VP8, VP8L or VP8X)."""
    with open(path, "rb") as f:
        b = f.read(30)
    kind = b[12:16]
    if kind == b"VP8X":
        return 1 + int.from_bytes(b[24:27], "little"), 1 + int.from_bytes(b[27:30], "little")
    if kind == b"VP8 ":
        return int.from_bytes(b[26:28], "little") & 0x3FFF, int.from_bytes(b[28:30], "little") & 0x3FFF
    if kind == b"VP8L":
        bits = int.from_bytes(b[21:25], "little")
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    raise ValueError(f"not a WebP file: {path}")


def encode(src, w, h, q, dst):
    subprocess.run(["cwebp", "-quiet", "-q", str(q), "-m", "6", "-af", "-mt", "-resize", str(w), str(h), src, "-o", dst],
                   check=True)


def optimise(img_dir=IMG_DIR):
    """Returns [(file name, old bytes, new bytes)]."""
    groups = {}
    for name in sorted(os.listdir(img_dir)):
        m = NAME_RE.match(name)
        if m:
            groups.setdefault(m["stem"], {})[int(m["w"])] = os.path.join(img_dir, name)
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        for stem, sizes in groups.items():
            master = sizes[max(sizes)]
            mw, mh = dims(master)
            # smallest first, so every size is cut from the untouched master before the master itself is re-encoded
            for w, path in sorted(sizes.items()):
                tw, th = dims(path)
                src = master if abs(tw / th - mw / mh) < 0.01 else path  # different crop: re-encode from itself
                out = os.path.join(tmp, os.path.basename(path))
                encode(src, tw, th, QUALITY[w], out)
                old, new = os.path.getsize(path), os.path.getsize(out)
                if new < old:
                    shutil.copyfile(out, path)
                rows.append((os.path.basename(path), old, min(old, new)))
    return rows


if __name__ == "__main__":
    rows = optimise(sys.argv[1] if len(sys.argv) > 1 else IMG_DIR)
    for name, old, new in sorted(rows, key=lambda r: r[1] - r[2], reverse=True):
        print(f"{name:45} {old / 1024:7.1f} KB -> {new / 1024:7.1f} KB")
    before, after = sum(r[1] for r in rows), sum(r[2] for r in rows)
    print(f"{'TOTAL':45} {before / 1024:7.1f} KB -> {after / 1024:7.1f} KB  (-{(1 - after / before) * 100:.0f}%)")
```

- [ ] **Step 4: Run the tests and confirm they pass**

Run: `~/.venvs/bws-card/bin/python -m unittest discover -s tools -p "test_optimize_images.py" -v`
Expected: 4 PASS (takes a few seconds).

- [ ] **Step 5: Run it on the site**

```bash
cd ~/bws && du -sk site/assets/img && python3 tools/optimize_images.py | tail -12 && du -sk site/assets/img
```
Expected: a table ending in `TOTAL … (-NN%)`. Acceptance is at least a 25% saving.
- If the saving is under 15%, the originals were already near these settings. Report the number and keep the result. Don't lower quality to hit the target.
- If it's between 15% and 25%, keep it and note it in the final report.

- [ ] **Step 6: Visual spot-check**

```bash
cd ~/bws && mkdir -p /private/tmp/claude-501/bws-img && for f in hse-fire-drill-1600 facility-bintulu-yard-1600 hero-column-erection-1600; do git show HEAD:site/assets/img/$f.webp > /private/tmp/claude-501/bws-img/$f-before.webp; cp site/assets/img/$f.webp /private/tmp/claude-501/bws-img/$f-after.webp; done; open /private/tmp/claude-501/bws-img
```
Compare each before/after pair at 100% zoom, looking for banding in skies and smearing on faces or text. If one image shows artefacts, restore it with `git checkout -- site/assets/img/<name>` and note it.

- [ ] **Step 7: Commit**

```bash
git add tools/optimize_images.py tools/test_optimize_images.py site/assets/img
git commit -m "Re-encode site photos with tuned WebP settings"
```

---

### Task 6: Jawi name without Google Fonts

**Files:**
- Create: `tools/make_jawi.py`, `site/assets/logo/jawi.svg` (generated)
- Test: `tools/test_make_jawi.py`
- Modify: every `site/*.html` and `site/ms/*.html` (by the script), `site/assets/css/styles.css:161` (by the script), `tools/generate_site.py`

- [ ] **Step 1: Write the failing test**

`tools/test_make_jawi.py`:
```python
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


@unittest.skipUnless(os.path.exists(make_jawi.FONT), "source font not downloaded (Task 0 Step 2)")
class OutlineTests(unittest.TestCase):
    def test_outline_produces_paths(self):
        d, width, asc, desc, upm = make_jawi.outline()
        self.assertGreater(len(d), 500)
        self.assertGreater(width, 0)
        self.assertGreater(asc, 0)
        self.assertLess(desc, 0)

    def test_svg_is_single_path_in_currentcolor_free_mask(self):
        svg = make_jawi.build_svg()
        self.assertTrue(svg.startswith('<svg xmlns="http://www.w3.org/2000/svg"'))
        self.assertEqual(svg.count("<path"), 1)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `~/.venvs/bws-card/bin/python -m unittest discover -s tools -p "test_make_jawi.py" -v`
Expected: ERROR `No module named 'make_jawi'`.

- [ ] **Step 3: Write `tools/make_jawi.py`**

```python
# Replaces the Jawi company name (previously set in Noto Naskh Arabic from Google Fonts) with outlined
# letters in one cached file, site/assets/logo/jawi.svg, shown through a CSS mask so it still takes the
# text colour (header grey, footer light). The site then makes no request to Google Fonts.
# Edits every page in place (header + footer span, font <link>, preconnect) and owns the .jawi rule in styles.css.
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

TAG = f'<span class="jawi" role="img" lang="ms-Arab" aria-label="{JAWI}"></span>'
SPAN_RE = re.compile(r'<span class="jawi" dir="rtl" lang="ms-Arab">' + re.escape(JAWI) + r"</span>")
FONT_LINK_RE = re.compile(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2\?family=Noto\+Naskh\+Arabic[^"]*">\n')
PRECONNECT_RE = re.compile(r'<link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin>\n')
CSS_RULE_RE = re.compile(r"^\.jawi \{[^}]*\}$", re.M)


def outline(text=JAWI, font_path=FONT, weight=WEIGHT):
    """Shape the text with HarfBuzz and return (path d, advance width, ascent, descent, units per em)."""
    import uharfbuzz as hb
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.ttLib import TTFont
    from fontTools.varLib.instancer import instantiateVariableFont

    font = TTFont(font_path)
    if "fvar" in font:
        font = instantiateVariableFont(font, {"wght": weight})
    data = io.BytesIO()
    font.save(data)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()  # Arabic script, right to left
    hb.shape(hb.Font(hb.Face(data.getvalue())), buf, {})
    glyphs, order = font.getGlyphSet(), font.getGlyphOrder()
    x, parts = 0, []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):  # HarfBuzz returns visual (left-to-right) order
        pen = SVGPathPen(glyphs, ntos=lambda v: str(round(v)))
        glyphs[order[info.codepoint]].draw(TransformPen(pen, (1, 0, 0, -1, x + pos.x_offset, -pos.y_offset)))
        if pen.getCommands():
            parts.append(pen.getCommands())
        x += pos.x_advance
    return "".join(parts), x, font["hhea"].ascent, font["hhea"].descent, font["head"].unitsPerEm


def build_svg():
    d, width, asc, desc, upm = outline()
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 {-asc} {width} {asc - desc}">'
            f'<path d="{d}"/></svg>\n')


def rewrite_page(doc):
    doc = PRECONNECT_RE.sub("", doc)
    doc = FONT_LINK_RE.sub("", doc)
    return SPAN_RE.sub(TAG, doc)


def rewrite_css(css, width, height, upm):
    """Replace the single-line .jawi rule. The box height equals the font's line box at 1em, so the letters
    render at the same size the text did; aspect-ratio gives the width."""
    rule = (f".jawi {{ display: block; height: {height / upm:.3f}em; aspect-ratio: {width:.0f} / {height:.0f}; "
            f"font-size: 0.82rem; color: var(--steel-600); background-color: currentColor; "
            f'-webkit-mask: url("../logo/jawi.svg") no-repeat 0 50% / contain; '
            f'mask: url("../logo/jawi.svg") no-repeat 0 50% / contain; }}')
    out, n = CSS_RULE_RE.subn(rule, css, count=1)
    if n != 1:
        raise SystemExit("make_jawi: .jawi rule not found in styles.css")
    return out


def pages():
    return sorted(glob.glob(os.path.join(SITE_DIR, "*.html")) + glob.glob(os.path.join(SITE_DIR, "ms", "*.html")))


if __name__ == "__main__":
    d, width, asc, desc, upm = outline()
    with open(SVG_OUT, "w", encoding="utf-8") as f:
        f.write(build_svg())
    with open(CSS, encoding="utf-8") as f:
        css = f.read()
    with open(CSS, "w", encoding="utf-8") as f:
        f.write(rewrite_css(css, width, asc - desc, upm))
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
```

- [ ] **Step 4: Run the tests and confirm they pass**

Run: `~/.venvs/bws-card/bin/python -m unittest discover -s tools -p "test_make_jawi.py" -v`
Expected: 6 PASS.

- [ ] **Step 5: Run it on the site**

```bash
cd ~/bws && ~/.venvs/bws-card/bin/python tools/make_jawi.py
grep -rl 'fonts.g' site --include=*.html | wc -l
grep -c 'class="jawi" role="img"' site/index.html site/ms/index.html
```
Expected:
- `jawi.svg <N> bytes, 18 pages updated`, with N around 5–15 KB
- the `grep -rl` count is `0`
- `2` for each file

- [ ] **Step 6: Compare visually with the old rendering**

```bash
open "http://localhost:8080/" ; open "http://localhost:8080/ms/"
```
Check:
- the name appears in the header under the logo and in the footer, and the letters are joined (cursive), not separate
- the header is grey and the footer light
- the size is close to before. The live preview `https://bwsengsdnbhd.vercel.app/` still has the old rendering, so compare against it side by side.

If the size is off, change only the multiplier in `rewrite_css` (`height / upm`). For example, `* 0.9` makes it smaller. Then re-run Step 5. The script owns the rule, so re-running is safe.

- [ ] **Step 7: Update the generator template (it is not run)**

In `tools/generate_site.py`:
- Delete the line `<link rel="stylesheet" href="{FONT_JAWI}">` (about line 150) and the preceding `fonts.gstatic.com` preconnect line, if the template has one.
- Delete the `FONT_JAWI = ...` assignment (line 67).
- Replace both `<span class="jawi" dir="rtl" lang="ms-Arab">{JAWI}</span>` (about lines 177 and 224) with:
```python
<span class="jawi" role="img" lang="ms-Arab" aria-label="{JAWI}"></span>
```
Then confirm:
```bash
cd ~/bws && grep -n 'Noto+Naskh\|FONT_JAWI\|dir="rtl" lang="ms-Arab"' tools/generate_site.py
```
Expected: no output.

- [ ] **Step 8: Rebuild BM to prove it agrees, run all tests, commit**

```bash
cd ~/bws && python3 tools/build_ms.py && git status --short site/ms | grep -v '^ M' ; ~/.venvs/bws-card/bin/python -m unittest discover -s tools -p "test_*.py"
git add tools/make_jawi.py tools/test_make_jawi.py tools/generate_site.py site/assets/logo/jawi.svg site/assets/css/styles.css site/*.html site/ms/*.html
git commit -m "Draw the Jawi name from a cached SVG instead of Google Fonts"
```
Expected: no stray (untracked or added) files in `site/ms`, and tests `OK`.

---

### Task 7: Hosting headers, CSP and analytics

**Files:**
- Create: `site/_headers`
- Modify: `vercel.json` (CSP value), `site/.htaccess:27`, `README.md`

The new CSP, used verbatim in all three files:
```
default-src 'self'; script-src 'self' https://static.cloudflareinsights.com; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' data:; frame-src https://maps.google.com https://www.google.com; connect-src 'self' https://formspree.io https://cloudflareinsights.com; form-action 'self' https://formspree.io; base-uri 'self'; object-src 'none'; upgrade-insecure-requests; frame-ancestors 'none'
```
Compared with today: the Google Fonts hosts are gone from `style-src` and `font-src`, and the Cloudflare beacon is added to `script-src` and `connect-src`.

- [ ] **Step 1: Create `site/_headers`**

```
/*
  Content-Security-Policy: default-src 'self'; script-src 'self' https://static.cloudflareinsights.com; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' data:; frame-src https://maps.google.com https://www.google.com; connect-src 'self' https://formspree.io https://cloudflareinsights.com; form-action 'self' https://formspree.io; base-uri 'self'; object-src 'none'; upgrade-insecure-requests; frame-ancestors 'none'
  Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=(), interest-cohort=()
  Cross-Origin-Opener-Policy: same-origin

/assets/fonts/*
  Cache-Control: public, max-age=31536000, immutable

/assets/img/*
  Cache-Control: public, max-age=2592000, stale-while-revalidate=86400

/assets/illustrations/*
  Cache-Control: public, max-age=2592000, stale-while-revalidate=86400

/assets/logo/*
  Cache-Control: public, max-age=2592000, stale-while-revalidate=86400

/assets/css/*
  Cache-Control: public, max-age=86400, stale-while-revalidate=604800

/assets/js/*
  Cache-Control: public, max-age=86400, stale-while-revalidate=604800
```

- [ ] **Step 2: `vercel.json`**

Replace the `"value"` of the `Content-Security-Policy` header with the new CSP string above. Then validate it:
```bash
cd ~/bws && python3 -c "import json; v=json.load(open('vercel.json')); print([h['value'] for h in v['headers'][0]['headers'] if h['key']=='Content-Security-Policy'][0])"
```
Expected: the new CSP printed, with no JSON error.

- [ ] **Step 3: `site/.htaccess` line 27**

Replace the quoted value in `Header always set Content-Security-Policy "…"` with the new CSP string.

- [ ] **Step 4: Check all three agree**

```bash
cd ~/bws && grep -h -o "default-src[^\"]*" site/_headers site/.htaccess vercel.json | sort -u | wc -l
grep -c 'fonts.g' site/_headers site/.htaccess vercel.json
```
Expected: `1` (identical policies), then `0` for each file.

- [ ] **Step 5: README**

In `README.md`, under the `## Deploy` table, add:
```markdown
**Cloudflare Pages (recommended):** create a Pages project from this repo with *Build output directory* `site` and no build command. `site/_headers` sets the security headers and caching (it mirrors `vercel.json` and `.htaccess`, so keep all three in step when changing the CSP).

**Visitor statistics:** in the Pages project open *Metrics → Web Analytics → Enable*. Cloudflare adds its own small script; it uses no cookies, so no consent banner is needed. The CSP already allows it.
```
In the `## Tools` section (or the file structure `tools/` line), add one line per new script:
```markdown
- `make_locations.py`: the blueprint site drawings on the contact page (`assets/illustrations/loc-*.svg`)
- `optimize_images.py`: re-encodes the WebP photos; only keeps a file if it gets smaller
- `make_jawi.py`: draws the Jawi name into `assets/logo/jawi.svg` (needs the venv and the font in `tools/fonts/`)
```

- [ ] **Step 6: Commit**

```bash
git add site/_headers vercel.json site/.htaccess README.md
git commit -m "Add Cloudflare Pages headers and allow Web Analytics in the CSP"
```

---

### Task 8: Verification and report

- [ ] **Step 1: Lighthouse after**

```bash
cd ~/bws && (python3 -m http.server 8080 -d site >/dev/null 2>&1 &) ; sleep 1
for p in "" contact.html; do
  npx -y lighthouse@12.6.1 "http://localhost:8080/$p" --only-categories=performance --output=json --quiet \
    --chrome-flags="--headless=new" --output-path="/private/tmp/claude-501/bws-lh/after-${p:-index}.json"
done
python3 - <<'EOF'
import json, glob
for f in sorted(glob.glob("/private/tmp/claude-501/bws-lh/*.json")):
    r = json.load(open(f)); items = r["audits"]["network-requests"]["details"]["items"]
    print(f.split("/")[-1], "score", round(r["categories"]["performance"]["score"]*100),
          "requests", len(items), "KB", round(sum(i.get("transferSize", 0) for i in items)/1024),
          "google", sum("google" in i["url"] or "gstatic" in i["url"] for i in items))
EOF
```
Expected: the `after-*` lines show `google 0` on both pages, fewer KB than `before-*` and an equal or higher score.

- [ ] **Step 2: Every page, EN and BM, has no Google Fonts references**

```bash
cd ~/bws && grep -rl 'fonts.googleapis\|fonts.gstatic' site | wc -l
```
Expected: `0`.

- [ ] **Step 3: Full test suite**

Run: `~/.venvs/bws-card/bin/python -m unittest discover -s tools -p "test_*.py" -v`
Expected: all PASS.

- [ ] **Step 4: Stop the local server**

```bash
pkill -f "http.server 8080"
```

- [ ] **Step 5: Report**

Give the owner a before/after table covering score, KB and Google requests for index and contact, the image saving %, and any image that was restored or any label that was nudged. Don't push or deploy. Pushing to the Vercel preview is a separate decision for the owner.
