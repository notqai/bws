# Digital Business Card (Mazinah) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a mobile-first digital business card for Mazinah Binti Mohd Masri at `/card/mazinah`, with a Save Contact (.vcf) button, quick-action buttons, both offices, credentials, and a QR code.

**Architecture:** One static HTML page inside the existing BWS site (`site/card/`), styled by the site's `styles.css` tokens plus a small `card.css`. A stdlib-plus-`segno` Python script (`tools/make_card.py`) generates the `.vcf` and QR SVG from one data dict, with unit tests. No build step, no backend.

**Tech Stack:** Plain HTML/CSS/JS, Python 3 `unittest`, `segno` (pure-Python QR generator) in a venv outside the repo.

**Spec:** `docs/superpowers/specs/2026-10-19-digital-card-design.md`

**Notes before starting**
- Work on branch `digital-card`, not `main`. Do not push anything without Qai's go-ahead.
- Temporary base URL for the QR code: `https://bwsengsdnbhd.vercel.app`. The QR must be regenerated after the `.com` cutover.
- The HTML page is written by hand for Mazinah. For a future staff member, add an entry to `PEOPLE` in `make_card.py` (generates their `.vcf` and QR) and copy `mazinah.html`, changing the text and links.

---

### Task 1: Branch and tooling

**Files:**
- No repo files changed

- [ ] **Step 1: Create the branch**

```bash
cd ~/bws && git switch -c digital-card
```
Expected: `Switched to a new branch 'digital-card'`

- [ ] **Step 2: Create a venv and install segno**

```bash
python3 -m venv ~/.venvs/bws-card && ~/.venvs/bws-card/bin/python -m pip install --quiet segno
```

- [ ] **Step 3: Verify**

Run: `~/.venvs/bws-card/bin/python -c "import segno; print(segno.__version__)"`
Expected: a version number such as `1.6.x`

---

### Task 2: vCard and QR generator (TDD)

**Files:**
- Create: `tools/make_card.py`
- Test: `tools/test_make_card.py`

- [ ] **Step 1: Write the failing tests**

Create `tools/test_make_card.py`:

```python
import tempfile
import unittest
from pathlib import Path

import make_card


def unfold(text):
    return text.replace("\r\n ", "")


class VCardTests(unittest.TestCase):
    def setUp(self):
        self.vcf = make_card.build_vcf(make_card.PEOPLE["mazinah"])

    def test_uses_crlf_only(self):
        self.assertTrue(self.vcf.startswith("BEGIN:VCARD\r\n"))
        self.assertTrue(self.vcf.endswith("END:VCARD\r\n"))
        self.assertNotIn("\n", self.vcf.replace("\r\n", ""))

    def test_core_fields(self):
        text = unfold(self.vcf)
        for line in [
            "VERSION:3.0",
            "N:Mohd Masri;Mazinah Binti;;;",
            "FN:Mazinah Binti Mohd Masri",
            "ORG:BWS Engineering Sdn Bhd",
            "TITLE:Executive Director / Personnel & Administration Manager",
            "TEL;TYPE=CELL,VOICE:+60198894946",
            "TEL;TYPE=WORK,VOICE:+6085652743",
            "EMAIL;TYPE=INTERNET,WORK:mazinahmasribws@gmail.com",
            "URL:https://www.bwsengineeringsb.com",
        ]:
            self.assertIn(line + "\r\n", text)

    def test_address_commas_are_escaped(self):
        text = unfold(self.vcf)
        self.assertIn(
            "ADR;TYPE=WORK:;;Lot 1743\\, Block 3 MCLD\\, Piasau Industrial Estate Phase III\\, Jalan Prunus 1;Miri;Sarawak;98000;Malaysia\r\n",
            text,
        )

    def test_lines_are_at_most_75_octets(self):
        for line in self.vcf.split("\r\n"):
            self.assertLessEqual(len(line.encode("utf-8")), 75, line)


class QrTests(unittest.TestCase):
    def test_svg_output(self):
        svg = make_card.build_qr_svg("https://example.com/card/mazinah")
        self.assertTrue(svg.lstrip().startswith("<svg"))
        self.assertIn("</svg>", svg)


class WriteAllTests(unittest.TestCase):
    def test_writes_vcf_and_qr_per_person(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_card.write_all(Path(tmp), "https://example.com")
            self.assertTrue((Path(tmp) / "mazinah.vcf").is_file())
            self.assertTrue((Path(tmp) / "mazinah-qr.svg").is_file())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd ~/bws && ~/.venvs/bws-card/bin/python -m unittest discover -s tools -p "test_make_card.py" -v`
Expected: FAIL / ERROR with `ModuleNotFoundError: No module named 'make_card'`

- [ ] **Step 3: Write the implementation**

Create `tools/make_card.py`:

```python
"""Build the vCard and QR code for each staff digital card.

Usage (from the repo root):
    ~/.venvs/bws-card/bin/python tools/make_card.py [base_url]

Writes site/card/<slug>.vcf and site/card/<slug>-qr.svg. The QR encodes
<base_url>/card/<slug>. The default base URL is the temporary Vercel address;
pass the real domain after the cutover, then reprint nothing until it is done.
"""
import io
import sys
from pathlib import Path

import segno

SITE_CARD_DIR = Path(__file__).resolve().parent.parent / "site" / "card"
DEFAULT_BASE_URL = "https://bwsengsdnbhd.vercel.app"

PEOPLE = {
    "mazinah": {
        "family": "Mohd Masri",
        "given": "Mazinah Binti",
        "full": "Mazinah Binti Mohd Masri",
        "title": "Executive Director / Personnel & Administration Manager",
        "org": "BWS Engineering Sdn Bhd",
        "mobile": "+60198894946",
        "office": "+6085652743",
        "email": "mazinahmasribws@gmail.com",
        "url": "https://www.bwsengineeringsb.com",
        "street": "Lot 1743, Block 3 MCLD, Piasau Industrial Estate Phase III, Jalan Prunus 1",
        "city": "Miri",
        "region": "Sarawak",
        "postcode": "98000",
        "country": "Malaysia",
    },
}


def esc(value):
    """Escape a vCard text value."""
    return (
        value.replace("\\", "\\\\")
        .replace(",", "\\,")
        .replace(";", "\\;")
        .replace("\n", "\\n")
    )


def fold(line):
    """Fold a content line to at most 75 octets; continuations start with a space."""
    out, cur = [], ""
    for ch in line:
        if len((cur + ch).encode("utf-8")) > 75:
            out.append(cur)
            cur = " " + ch
        else:
            cur += ch
    out.append(cur)
    return "\r\n".join(out)


def build_vcf(p):
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{esc(p['family'])};{esc(p['given'])};;;",
        f"FN:{esc(p['full'])}",
        f"ORG:{esc(p['org'])}",
        f"TITLE:{esc(p['title'])}",
        f"TEL;TYPE=CELL,VOICE:{p['mobile']}",
        f"TEL;TYPE=WORK,VOICE:{p['office']}",
        f"EMAIL;TYPE=INTERNET,WORK:{p['email']}",
        f"URL:{p['url']}",
        "ADR;TYPE=WORK:;;{};{};{};{};{}".format(
            esc(p["street"]), esc(p["city"]), esc(p["region"]), esc(p["postcode"]), esc(p["country"])
        ),
        "END:VCARD",
    ]
    return "".join(fold(line) + "\r\n" for line in lines)


def build_qr_svg(url):
    buf = io.BytesIO()
    segno.make(url, error="m").save(
        buf,
        kind="svg",
        scale=8,
        border=2,
        dark="#0A1240",
        light="#FFFFFF",
        xmldecl=False,
        svgns=True,
        title="QR code for the BWS digital business card",
    )
    return buf.getvalue().decode("utf-8")


def write_all(out_dir, base_url):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for slug, person in PEOPLE.items():
        (out_dir / f"{slug}.vcf").write_bytes(build_vcf(person).encode("utf-8"))
        (out_dir / f"{slug}-qr.svg").write_text(
            build_qr_svg(f"{base_url.rstrip('/')}/card/{slug}"), encoding="utf-8"
        )


if __name__ == "__main__":
    write_all(SITE_CARD_DIR, sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE_URL)
    print(f"Wrote cards to {SITE_CARD_DIR}")
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd ~/bws && ~/.venvs/bws-card/bin/python -m unittest discover -s tools -p "test_make_card.py" -v`
Expected: 6 tests, `OK`

- [ ] **Step 5: Commit**

```bash
cd ~/bws && git add tools/make_card.py tools/test_make_card.py
git commit -m "Add vCard and QR generator for digital cards

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Generate the vCard and QR files

**Files:**
- Create: `site/card/mazinah.vcf`
- Create: `site/card/mazinah-qr.svg`

- [ ] **Step 1: Generate**

Run: `cd ~/bws && ~/.venvs/bws-card/bin/python tools/make_card.py`
Expected: `Wrote cards to /Users/qai/bws/site/card`

- [ ] **Step 2: Inspect the vCard**

Run: `cat -A ~/bws/site/card/mazinah.vcf | head -20`
Expected: every line ends in `^M$` (CRLF), starts with `BEGIN:VCARD`, ends with `END:VCARD^M$`, and the `ADR` line contains `Lot 1743\, Block 3 MCLD\,`.

- [ ] **Step 3: Commit**

```bash
cd ~/bws && git add site/card/mazinah.vcf site/card/mazinah-qr.svg
git commit -m "Generate Mazinah vCard and temporary QR code

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Card stylesheet

**Files:**
- Create: `site/assets/css/card.css`

It relies on the tokens in `styles.css` (`--ink`, `--brand-blue`, `--space-*`, `--shadow-*`, `--font-*`, `--fs-*`, `--steel-*`, `--on-ink-muted`), so `styles.css` must be linked first.

- [ ] **Step 1: Write the stylesheet**

Create `site/assets/css/card.css`:

```css
/* ==========================================================================
   Digital business card: page-specific styles.
   Loaded after styles.css, which provides all colour, type and spacing tokens.
   ========================================================================== */

.card-page { background: var(--steel-100); min-height: 100vh; }
.card { max-width: 440px; margin-inline: auto; background: var(--steel-50); box-shadow: var(--shadow-2); }

/* Header */
.card-head { background: var(--ink); color: var(--on-ink); padding: var(--space-6) var(--space-5) var(--space-5); text-align: center; }
.card-head img { display: block; margin: 0 auto var(--space-3); width: 120px; height: auto; }
.card-head .jawi { color: var(--on-ink-muted); text-align: center; font-size: 1rem; margin: 0; }

/* Identity */
.card-id { padding: var(--space-5); text-align: center; background: var(--white); border-bottom: 1px solid var(--steel-200); }
.card-id h1 { font: 700 var(--fs-h3)/1.2 var(--font-head); color: var(--ink); margin: 0 0 var(--space-2); }
.card-id .role { margin: 0 0 var(--space-1); color: var(--steel-800); font-size: var(--fs-sm); }
.card-id .company { margin: 0; color: var(--steel-600); font-size: var(--fs-sm); }
.card-save { display: flex; width: 100%; margin-top: var(--space-5); }

/* Quick actions */
.card-actions { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-3); padding: var(--space-5) var(--space-5) 0; }
.card-actions .btn { width: 100%; }

/* Sections */
.card-section { padding: var(--space-5); }
.card-section h2 { font: 700 var(--fs-xs)/1.2 var(--font-body); letter-spacing: 0.12em; text-transform: uppercase; color: var(--steel-600); margin: 0 0 var(--space-3); }

/* Offices */
.office { background: var(--white); border: 1px solid var(--steel-200); border-radius: var(--radius); padding: var(--space-4); box-shadow: var(--shadow-1); }
.office + .office { margin-top: var(--space-3); }
.office h3 { font: 700 var(--fs-base)/1.2 var(--font-head); color: var(--ink); margin: 0 0 var(--space-2); }
.office address { font-style: normal; font-size: var(--fs-sm); color: var(--steel-800); margin: 0 0 var(--space-3); }
.office ul { list-style: none; margin: 0 0 var(--space-3); padding: 0; font-size: var(--fs-sm); }
.office li { padding: var(--space-1) 0; color: var(--steel-800); }
.office a { color: var(--brand-blue); font-weight: 600; text-decoration: none; }
.office a:hover { text-decoration: underline; }
.office .btn { width: 100%; }

/* Credentials */
.chips { display: flex; flex-wrap: wrap; gap: var(--space-2); list-style: none; margin: 0; padding: 0; }
.chip { background: var(--brand-cyan); color: var(--ink); border-radius: 999px; padding: var(--space-2) var(--space-3); font-size: var(--fs-xs); font-weight: 600; }
.reg { margin: var(--space-3) 0 0; font-size: var(--fs-xs); color: var(--steel-600); }

/* Share + QR */
.card-share { text-align: center; }
.card-share .btn { width: 100%; }
.card-qr { margin: var(--space-5) auto 0; width: 160px; }
.card-qr img { display: block; width: 160px; height: 160px; }
.card-qr p { margin: var(--space-2) 0 0; font-size: var(--fs-xs); color: var(--steel-600); }
.card-foot { padding: var(--space-4) var(--space-5) var(--space-6); text-align: center; font-size: var(--fs-xs); color: var(--steel-600); }
.card-foot a { color: var(--brand-blue); }

@media (min-width: 480px) {
  .card-page { padding: var(--space-6) var(--space-4); }
  .card { border-radius: 8px; overflow: hidden; }
}
```

- [ ] **Step 2: Commit**

```bash
cd ~/bws && git add site/assets/css/card.css
git commit -m "Add card stylesheet

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
```

---

### Task 5: Card page (TDD with a static check)

**Files:**
- Create: `site/card/mazinah.html`
- Test: `tools/test_card_page.py`

- [ ] **Step 1: Write the failing page checks**

Create `tools/test_card_page.py`:

```python
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
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd ~/bws && ~/.venvs/bws-card/bin/python -m unittest discover -s tools -p "test_card_page.py" -v`
Expected: ERROR in `setUpClass` with `FileNotFoundError: ... site/card/mazinah.html`

- [ ] **Step 3: Write the page**

Create `site/card/mazinah.html`:

```html
<!doctype html>
<html lang="en-MY">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mazinah Binti Mohd Masri | BWS Engineering Sdn Bhd</title>
<meta name="description" content="Digital business card for Mazinah Binti Mohd Masri, Executive Director / Personnel &amp; Administration Manager, BWS Engineering Sdn Bhd.">
<meta name="robots" content="noindex">
<meta name="theme-color" content="#0A1240">
<meta property="og:type" content="profile">
<meta property="og:title" content="Mazinah Binti Mohd Masri | BWS Engineering Sdn Bhd">
<meta property="og:description" content="Executive Director / Personnel &amp; Administration Manager. Tap to save her contact.">
<!-- TEMPORARY absolute URL: change to https://www.bwsengineeringsb.com/... after the domain cutover -->
<meta property="og:image" content="https://bwsengsdnbhd.vercel.app/assets/img/og-image.jpg">
<link rel="icon" href="../favicon.ico" sizes="32x32">
<link rel="icon" href="../assets/logo/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="../assets/logo/apple-touch-icon.png">
<link rel="preload" href="../assets/fonts/source-serif-4-700-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="../assets/fonts/source-sans-3-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@500&display=swap&text=%D9%83%D8%AC%D8%B1%D9%88%D8%AA%D8%B1%D8%A7%D9%86%D8%A8%D9%8A%D8%AF%D8%A8%D9%84%D9%8A%D9%88%D8%A5%D9%8A%D8%B3%D8%B3%D9%86%D8%AF%DB%8C%D8%B1%DB%8C%D8%A7%D9%86%D8%A8%D8%B1%D8%AD%D8%AF">
<link rel="stylesheet" href="../assets/css/styles.css">
<link rel="stylesheet" href="../assets/css/card.css">
</head>
<body class="card-page">
<main class="card">

  <header class="card-head">
    <img src="../assets/logo/logo-white.svg" alt="BWS Engineering Sdn Bhd" width="120" height="91">
    <p class="jawi" lang="ar" dir="rtl">كجروتران بي دبليو إيس سندیریان برحد</p>
  </header>

  <section class="card-id" aria-labelledby="name">
    <h1 id="name">Mazinah Binti Mohd Masri</h1>
    <p class="role">Executive Director / Personnel &amp; Administration Manager</p>
    <p class="company">BWS Engineering Sdn Bhd</p>
    <a class="btn btn--primary card-save" href="mazinah.vcf" download>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M12 4v11"/><path d="m7 11 5 5 5-5"/><path d="M5 20h14"/></svg>
      Save Contact
    </a>
  </section>

  <div class="card-actions">
    <a class="btn btn--ghost" href="tel:+60198894946">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/></svg>
      Call
    </a>
    <a class="btn btn--ghost" href="https://wa.me/60198894946" rel="noopener">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M4 20l1.3-4.2A8 8 0 1 1 8.3 18.8z"/></svg>
      WhatsApp
    </a>
    <a class="btn btn--ghost" href="mailto:mazinahmasribws@gmail.com">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><rect x="3" y="5" width="18" height="14" rx="1"/><path d="m3 7 9 6 9-6"/></svg>
      Email
    </a>
    <a class="btn btn--ghost" href="https://www.bwsengineeringsb.com">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3a14 14 0 0 1 0 18 14 14 0 0 1 0-18z"/></svg>
      Website
    </a>
  </div>

  <section class="card-section" aria-labelledby="offices">
    <h2 id="offices">Offices</h2>

    <article class="office">
      <h3>Miri: Main Office &amp; Workshop</h3>
      <address>Lot 1743, Block 3 MCLD, Piasau Industrial Estate Phase III, Jalan Prunus 1, 98000 Miri, Sarawak, Malaysia</address>
      <ul>
        <li>Tel <a href="tel:+6085652743">085-652743</a> / <a href="tel:+6085652744">44</a> / <a href="tel:+6085652745">45</a></li>
        <li>Fax 085-652709</li>
        <li><a href="mailto:bwsesb@gmail.com">bwsesb@gmail.com</a></li>
        <li><a href="mailto:bws@bwsengineeringsb.com">bws@bwsengineeringsb.com</a></li>
      </ul>
      <a class="btn btn--ghost" href="https://www.google.com/maps?cid=4214669276461699859" target="_blank" rel="noopener">Open in Maps</a>
    </article>

    <article class="office">
      <h3>Bintulu: Office &amp; Fabrication Yard</h3>
      <address>Lot 782, Block 20, Kemena Land District, Jalan Tanjung Kidurong, 97007 Bintulu, Sarawak, Malaysia</address>
      <ul>
        <li>Tel <a href="tel:+6086252476">086-252476</a></li>
      </ul>
      <a class="btn btn--ghost" href="https://www.google.com/maps?cid=6044021619715074034" target="_blank" rel="noopener">Open in Maps</a>
    </article>
  </section>

  <section class="card-section" aria-labelledby="creds">
    <h2 id="creds">Credentials</h2>
    <ul class="chips">
      <li class="chip">PETRONAS &amp; PETROS Licensed</li>
      <li class="chip">CIDB G7</li>
      <li class="chip">ISO 9001 · Cert No. 44 100 072059</li>
      <li class="chip">ISO 45001 (BSI) · OHS 796482</li>
    </ul>
    <p class="reg">Registration No. 200201029529 (597192-V)</p>
  </section>

  <section class="card-section card-share" aria-labelledby="share-h">
    <h2 id="share-h">Share this card</h2>
    <button class="btn btn--primary" id="share" type="button" hidden>Share</button>
    <!-- TEMPORARY QR (points at the vercel.app address): regenerate with tools/make_card.py after the domain cutover -->
    <div class="card-qr">
      <img src="mazinah-qr.svg" alt="QR code for this card" width="160" height="160">
      <p>Scan to open this card</p>
    </div>
  </section>

  <footer class="card-foot">
    <a href="https://www.bwsengineeringsb.com">www.bwsengineeringsb.com</a>
  </footer>

</main>
<script>
(function () {
  var b = document.getElementById('share');
  if (!b) return;
  b.hidden = false;
  b.addEventListener('click', function () {
    var data = { title: document.title, url: location.href };
    if (navigator.share) {
      navigator.share(data).catch(function () {});
    } else if (navigator.clipboard) {
      navigator.clipboard.writeText(data.url).then(function () { b.textContent = 'Link copied'; });
    }
  });
})();
</script>
</body>
</html>
```

- [ ] **Step 4: Run all tests to verify they pass**

Run: `cd ~/bws && ~/.venvs/bws-card/bin/python -m unittest discover -s tools -p "test_*.py" -v`
Expected: 12 tests, `OK`

- [ ] **Step 5: Commit**

```bash
cd ~/bws && git add site/card/mazinah.html tools/test_card_page.py
git commit -m "Add Mazinah digital business card page

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
```

---

### Task 6: Visual and device verification

**Files:**
- No files changed (fix anything found, then re-run Task 5 Step 4)

- [ ] **Step 1: Serve the site locally**

Run: `cd ~/bws && python3 -m http.server 8000 -d site`
Open `http://localhost:8000/card/mazinah.html` in the browser (leave the server running).

- [ ] **Step 2: Check layout at phone and desktop width**

At 375px wide: single column, no horizontal scroll, Jawi name renders right-to-left in Naskh, the logo is crisp, and buttons are at least 44px tall. At 1280px wide: the card is centred at about 440px with rounded corners on a grey background.

- [ ] **Step 3: Check the Share button**

The Share button is visible when JavaScript is on. In a desktop browser without the Web Share API, clicking it changes the label to "Link copied" and puts the URL on the clipboard.

- [ ] **Step 4: Check links**

Click every link: `tel:`, WhatsApp (opens `wa.me/60198894946`), `mailto:`, both Maps links, and the website link. Expected: each opens its target, and the Miri/Bintulu Maps pins match the addresses.

- [ ] **Step 5: Check the vCard on real phones (after Task 7 gives a preview URL)**

Open the preview URL on an iPhone and on an Android phone, tap **Save Contact**, and confirm the contact has the right name, title, company, both phone numbers, email, website and address.

- [ ] **Step 6: Check the QR code**

Scan `site/card/mazinah-qr.svg` (open it on screen) with a phone camera. Expected: it opens `https://bwsengsdnbhd.vercel.app/card/mazinah`.

- [ ] **Step 7: Stop the server**

Press Ctrl+C in the server terminal.

---

### Task 7: README note, preview deploy and merge

**Files:**
- Modify: `README.md` (add a "Digital business cards" section before the "Tools" section)

- [ ] **Step 1: Add the README section**

Insert this section in `README.md` before the heading that begins the Tools section:

```markdown
## Digital business cards

Staff cards live in `site/card/<name>.html` (the first is `mazinah.html`), with a vCard (`<name>.vcf`) and a QR code (`<name>-qr.svg`) beside it. Cards are `noindex` and are not in `sitemap.xml`.

Regenerate the vCard and QR codes after editing the `PEOPLE` data in `tools/make_card.py`:

```
python3 -m venv ~/.venvs/bws-card && ~/.venvs/bws-card/bin/python -m pip install segno
~/.venvs/bws-card/bin/python tools/make_card.py [base_url]
~/.venvs/bws-card/bin/python -m unittest discover -s tools -p "test_*.py"
```

To add a person: add an entry to `PEOPLE`, copy `mazinah.html` to `<name>.html` and change the text and links, then regenerate.

**After the domain cutover:** run `tools/make_card.py https://www.bwsengineeringsb.com`, and change the temporary `og:image` URL in each card from `bwsengsdnbhd.vercel.app` to the `.com` domain. Do not print or hand out the QR code before this is done.
```

- [ ] **Step 2: Commit**

```bash
cd ~/bws && git add README.md
git commit -m "Document digital business cards in README

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
```

- [ ] **Step 3: Ask Qai before pushing**

Show `git log --oneline main..digital-card` and ask for permission to push the branch. Do not push without a yes.

- [ ] **Step 4: Push the branch and use the Vercel preview**

```bash
cd ~/bws && git push -u origin digital-card
```
Vercel builds a preview deployment for the branch. Open it from the Vercel dashboard (or `gh pr create` and use the preview link on the PR) and run Task 6 Step 5 on it.

- [ ] **Step 5: Merge after Qai confirms the preview**

Only after Qai approves the preview and the open items are answered (client confirms the licence wording, Mazinah agrees to publish her mobile and Gmail):

```bash
cd ~/bws && git switch main && git merge --ff-only digital-card && git push origin main
```
Expected: Vercel deploys, and `https://bwsengsdnbhd.vercel.app/card/mazinah` shows the card.
