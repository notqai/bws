# Group A: speed and infrastructure — design

Date: 2026-10-22
Status: approved in chat, pending spec review

Part of a three-group improvement round for the BWS site:
**A. Speed & infra (this spec)** → B. Compliance & procurement (PDPA page, vendor block) → C. Visual features (project map, case studies, timeline, certificate cards, hero video).

## Goals

1. The contact page loads no Google Maps code until the visitor asks for it.
2. Large photos are noticeably smaller with no visible quality loss.
3. The site makes no request to Google Fonts.
4. The site is ready to deploy on Cloudflare Pages (the host named in quotation QT/2026/10/001) with correct security and cache headers, and stays deployable on Vercel.
5. Cloudflare Web Analytics can be switched on without code changes.

Non-goals: AVIF / `<picture>` markup, CSS/JS fingerprinting or minification, any content change.

## 1. Map facade: "site drawing" cards

Replace each `<iframe class="map">` in `site/contact.html` with a card drawn in the existing blueprint illustration style (navy `#0A1240` sheet, sky-blue grid, cyan line work, as in `tools/make_illustrations.py`).

**Drawing content (one per office):**

| | Miri HQ | Bintulu |
|---|---|---|
| Drawing no. | BWS-LOC-01 | BWS-LOC-02 |
| Water | none in view (coast ~1.5 km, Sungai Miri ~0.9 km away) | port basin (OSM coastline) and a river; unlabelled, as it isn't open sea |
| Road labels | JLN PRUNUS 1, JLN PUJUT-LUTONG | MLNG ROAD |
| Area label | PIASAU INDUSTRIAL ESTATE PH III | KIDURONG INDUSTRIAL ESTATE |
| Highlight | Lot 1743 building on Jalan Prunus 1 (OSM footprint) | Lot 782 office (marker at the point; OSM has no buildings here) |
| Scale | 1.15 units/m (~700 m across), 200 m scale bar | 1 unit per 3.5 m (~2.8 km across, to take in the port basin), 500 m scale bar |
| Coordinates | 4.4469° N 114.0116° E | 3.2725° N 113.0802° E |

The geometry is real, traced from OpenStreetMap: roads drawn by highway class (major roads wider), building outlines, rivers and water, industrial landuse as a faint hatch, and the coastline with the sea side filled (OSM coastlines keep the sea on the right, so each stretch is closed against the frame). The data is a trimmed Overpass extract cached in `tools/data/osm-miri.json` and `tools/data/osm-bintulu.json` (kind, name, coordinates to 6 dp, clipped to the drawing plus a margin), so the build is deterministic and needs no network; `python3 tools/make_locations.py --fetch` re-downloads and rewrites it. It is projected on a local equirectangular projection centred on each office, north up, at a fixed scale per site, and clipped to the map area above the title block.

Each sheet has the BWS site highlighted in brand blue, a pin whose tip is exactly on the office point (with a pulse ring), a few labels taken only from OSM names or the company address (road labels rotated along the road and kept upright), a true-length scale bar, a north arrow, the coordinates in a monospace face and the attribution "© OpenStreetMap contributors". A title block along the bottom shows drawing no., site name, "REV A" and the **Load interactive map** button.

The Bintulu fabrication yard (Lot 124–128) is not plotted: OSM doesn't map it and its exact position relative to the office is unknown, so drawing it would be a guess.

**Build:** `tools/make_locations.py` (reusing the style helpers in `tools/make_illustrations.py`) writes `site/assets/illustrations/loc-miri.svg` and `loc-bintulu.svg`. Static text (labels, coordinates) lives in the SVG. The button and links are HTML overlaid on the card, so they are translatable and accessible.

**Markup** (replaces `.map-wrap` contents):

```html
<div class="map-wrap" data-map-src="https://maps.google.com/maps?q=4.446917,114.011563&z=17&hl=en&output=embed"
     data-map-title="Map: BWS Engineering main office, Piasau Industrial Estate, Miri">
  <img class="map-drawing" src="assets/illustrations/loc-miri.svg" alt="Site drawing of the Miri head office location in Piasau Industrial Estate" width="800" height="600" loading="lazy">
  <button type="button" class="map-load">Load interactive map</button>
</div>
```

**Behaviour** (`site/assets/js/main.js`):
- Clicking `.map-load` replaces the card's contents with the iframe (built from `data-map-src` / `data-map-title`, same attributes as today) and moves focus to it.
- Without JavaScript the button does nothing harmful. The existing "Open in Google Maps" link in the office details still works.
- The pin pulse is a CSS animation on the SVG, disabled under `prefers-reduced-motion: reduce`.

**BM:** the HTML button label and alt text go through `tools/ms_strings.py` / `build_ms.py`. Any text the JS creates (the iframe title is reused from `data-map-title`, so in practice none) uses the existing `T(en, ms)` helper in `main.js`. The SVG labels stay in English, because map labels, like the site names, are proper nouns.

## 2. Image re-encode

New script `tools/optimize_images.py`:
- For every `*-480/800/1600.webp` in `site/assets/img/`, re-encodes from the highest-quality available source (the 1600 file, or an original if one exists in `assets/`) using `cwebp`: q72 for 1600 px, q75 for 800 and 480 px, `-m 6 -af`.
- Writes the new file only if it is smaller than the current one.
- Prints a before/after table and the total saving.
- Leaves `og-image.jpg` and client logos alone.

Dimensions don't change, so no HTML changes are needed and the gallery lightbox (`data-full`) is unaffected.

Acceptance: total `assets/img` size falls by at least 25%. Spot-check `hse-fire-drill`, `facility-bintulu-yard` and `hero-column-erection` side by side at 100% for visible artefacts.

## 3. Jawi name as SVG

- A tool script (`tools/make_jawi.py`) uses Noto Naskh Arabic 500 (downloaded once into `tools/`, not shipped) and fontTools to convert «كجروتران بي دبليو إيس سندیریان برحد» to outlined paths. HarfBuzz shaping (via `uharfbuzz`) is used so the letters join correctly.
- Output: an inline `<svg class="jawi" role="img" aria-label="…" viewBox="…">` snippet with `fill="currentColor"`, so it inherits the current text colour.
- The pages have been hand-edited since `tools/generate_site.py` last ran, and its header says re-running it overwrites them. So the script **does not regenerate pages**. Instead it replaces the existing `<span class="jawi" …>…</span>` (header and footer) and removes the Noto Naskh `<link>` in place, in every `site/*.html` and `site/ms/*.html`. `generate_site.py`'s template is updated to match, but it is not run.
- `lang="ms-Arab"` and `dir="rtl"` move to the SVG's `<title>` for assistive tech.
- Remove from all pages (EN + BM): the Noto Naskh `<link rel="stylesheet">` and the `fonts.googleapis.com` / `fonts.gstatic.com` preconnects.
- CSP: drop `https://fonts.googleapis.com` from `style-src` and `https://fonts.gstatic.com` from `font-src`.

Acceptance: no page requests any `fonts.google*` URL, and the rendered name matches the current one visually at header and footer sizes.

## 4. Hosting headers

**New `site/_headers`** (Cloudflare Pages):

```
/*
  Content-Security-Policy: <same policy as vercel.json, updated per §3 and §5>
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

CSS/JS keep a short cache because their file names don't change when edited.

`vercel.json` and `site/.htaccess` (the cPanel option, line 27) get the same CSP change, so all three hosting options serve identical policies.

## 5. Cloudflare Web Analytics

- No script tag in the HTML. Web Analytics is switched on in the Cloudflare Pages dashboard, which injects the beacon automatically.
- CSP additions: `script-src https://static.cloudflareinsights.com` and `connect-src https://cloudflareinsights.com`.
- README "Deploy" section gets a step: Pages project → Metrics → Web Analytics → Enable. It notes that the analytics are cookieless, so no consent banner is needed.

## 6. Verification

1. Lighthouse (mobile) on `index.html` and `contact.html`, before and after. Record scores and total transfer size in the PR or commit notes.
2. Headless browser on `contact.html`: no request to `google.com` or `maps.google.com` until `.map-load` is clicked. After the click, the iframe is present and focused.
3. Headless check across all pages (EN + BM): no `fonts.googleapis.com` or `fonts.gstatic.com` requests, and no CSP violations in the console.
4. `python3 -m pytest tools/` (existing `test_card_page.py`, `test_make_card.py`) passes. New tests: `optimize_images.py` never writes a larger file; `make_jawi.py` leaves no `fonts.google` reference and no `<span class="jawi">` in any page.
5. BM pages regenerated with `tools/build_ms.py` and the diff reviewed.

## Files touched

- `tools/make_illustrations.py` (location drawings), new `tools/optimize_images.py`, new `tools/make_jawi.py`, `tools/ms_strings.py`, `tools/generate_site.py` (template only, not run), new tests in `tools/`
- `site/contact.html`, header/footer of every `site/*.html` and `site/ms/*.html` (edited in place)
- `site/assets/js/main.js`, `site/assets/css/styles.css`
- `site/assets/illustrations/loc-*.svg`, re-encoded `site/assets/img/*.webp`
- new `site/_headers`, `vercel.json`, `site/.htaccess`, `README.md`
