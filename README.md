# BWS Engineering Sdn Bhd: website

Corporate website for **BWS Engineering Sdn Bhd**, a Bumiputera oil & gas construction and maintenance contractor based in Miri and Bintulu, Sarawak. It replaces the old Wix site at www.bwsengineeringsb.com.

It is a plain static site: HTML, one CSS file and one small JavaScript file. There is no framework and no build step. Upload the **`site/`** folder to any static host.

## Deploy

| Host | How |
|---|---|
| **Netlify** | Drag the `site/` folder onto app.netlify.com/drop, or connect this repo and set the *publish directory* to `site`. |
| **Vercel** | Import the repo and set the *Root Directory* to `site`. Framework preset: *Other*. |
| **cPanel / Apache** | Upload the **contents** of `site/` into `public_html/`. The included `.htaccess` turns on compression, caching and the 404 page. |

After going live on the real domain, submit `https://www.bwsengineeringsb.com/sitemap.xml` in Google Search Console.
If the domain changes, search and replace `https://www.bwsengineeringsb.com` across `site/` (it appears in canonical links, Open Graph tags, JSON-LD, `sitemap.xml` and `robots.txt`).

## File structure

```
site/
├── index.html          Home
├── about.html          Company profile, objective, facilities, organisation chart (from BWS's own chart), licences
├── services.html       One section per service line (#plant #mechanical #civil #electrical)
├── clients.html        Main clients (logo cards)
├── projects.html       Filterable photo gallery with lightbox
├── hse.html            HSE policy, Quality policy, ISO / licences
├── careers.html        Working at BWS + job openings (apply by email)
├── contact.html        Two offices + Google Maps + enquiry form
├── 404.html            "Page not found"
├── sitemap.xml  robots.txt  site.webmanifest  favicon.ico  .htaccess
└── assets/
    ├── css/styles.css  All styles. Colours, fonts and spacing are variables at the top (:root)
    ├── js/main.js      Menu, counters, reveal animations, gallery filter/lightbox, contact form
    ├── logo/           logo.svg, logo-white.svg, favicon.svg, PNG app icons
    └── img/            Photos (WebP, 480 / 800 / 1600 px wide) + og-image.jpg (social share card)
assets/logo.jpg         The original 210×141 logo the SVG was rebuilt from (reference only)
tools/                  Optional scripts used to build the site (see "Tools" below)
```

Every page repeats the same header and footer. If you change a phone number, a menu item or similar, change it in **all 9 HTML files** (a find-and-replace across `site/*.html` does it in one go).

## Brand

| Token | Value | Use |
|---|---|---|
| `--brand-blue` | `#0A18D9` | Logo royal blue: buttons, links, key highlights. White text on it is 9.8:1 |
| `--brand-sky` | `#4797E6` | Logo sky blue: icons, accents, hovers. **Not** for white text (3.1:1 fails AA) |
| `--brand-cyan` | `#E4FCFC` | Logo pale cyan: light section backgrounds |
| `--ink` | `#0A1240` | Deep navy: dark sections, hero overlay, footer |
| `--steel-*` | greys | Body text `#2C3440`, secondary text `#5B6675` |
| `--safety` | `#F2A900` | **HSE callouts only** |

- **Fonts** (Google Fonts): *Source Serif 4* Bold for headings, *Source Sans 3* for body text, *Noto Naskh Arabic* for the Jawi company name. Only the letters in the Jawi name are downloaded, so that font costs almost nothing.
- **Logo:** `logo.svg` is a clean rebuild of the original mark: same three panels and proportions, the sky-blue glow behind the "W", and white serif capitals converted to outlines (no font needed). `logo-white.svg` is a single-colour version for dark backgrounds. `favicon.svg` is just the three panels.

## Common edits

### Swap or add photos
1. Export the photo as WebP (or JPG) at **800 px wide** (and optionally 480 and 1600 px wide). Use free tools like squoosh.app, or `cwebp -q 75 in.jpg -o out.webp`.
2. Put it in `site/assets/img/`, e.g. `civil-jetty-800.webp`.
3. In the HTML, change the `src` (and `srcset` if present), the `width`/`height` (the real pixel size of the 800 px file) and the **`alt` text** (describe what's in the photo).

Gallery photos (`projects.html`) are `<li data-cat="...">` items. Copy an existing one, change the file names, `data-full` (big version shown in the lightbox), `data-title` and `alt`. Categories: `plant`, `mech`, `civil`, `ei`, `hse`. The counts on the filter buttons are typed into the HTML, so update them if you add or remove photos.

**Placeholders** are grey striped boxes with a `<!-- PLACEHOLDER PHOTO … -->` comment above them. Replace the whole `<div class="ph">…</div>` with an `<img>`. For gallery items, copy a real gallery `<li>` instead.

### Swap the logo
Replace `site/assets/logo/logo.svg` and `logo-white.svg` (keep the file names). If the new logo has a different shape, update the `width`/`height` on the `<img>` tags in the header and footer.

### Client logos
Logos live in `site/assets/img/clients/` and are each client's **current** brand mark (checked October 2026):
- **PETRONAS mark** (`petronas.svg`) for Malaysia LNG, PETRONAS Carigali and PETRONAS Dagangan, which use the group brand.
- **JX Nippon Oil & Gas Exploration** was renamed **ENEOS Xplora** in 2023, so its card shows the ENEOS Xplora logo with a "Now ENEOS Xplora" note.
- **PT Rekayasa Industri** trades as **Rekind**.
- **Sources:** Wikimedia Commons / Wikipedia for JGC, Chiyoda, Mitsui & Co, Shell, ENEOS Xplora, PETRONAS and Rekind; Taihei Dengyo from its own website.
- **ASEAN Bintulu Fertilizer:** no current logo could be found online, so the file from the old BWS website is used. It is low resolution.

Logos show in greyscale and turn colour on hover (always colour on touch screens). To swap one, replace the file, keeping the name, or edit the list in `clients.html` and the marquee in `index.html`.
Company logos are trademarks of their owners. Showing them as a client list is common practice, but BWS should be comfortable it has worked for each client before publishing.

### Update the stats (home page)
In `index.html` search for `KEY STATS`. Each number looks like:
```html
<span class="stat-num" data-count="20" data-suffix="+">20+</span>
```
Change **both** `data-count` (what the counter animates to) and the text inside (what shows without JavaScript).

### Update job openings
In `careers.html` search for `JOB OPENINGS`. Each role is one `<article class="job">`. Copy one, change the title, location, type and summary, and set `data-apply="Exact Position Title"` on its button. The button opens an email to bwsesbhr@gmail.com with the subject **"Job Application – Exact Position Title"**. Also update the button's `href` the same way so it works without JavaScript.
⚠️ The three roles currently listed are **examples**. Replace or delete them before launch.

### Connect the contact form
The form is on `contact.html` (search for `CONTACT FORM`).
- **Right now** (no setup): pressing *Send* opens the visitor's email app with a pre-filled message to **bwsesb@gmail.com**.
- **To receive submissions directly** (recommended): create a free form at **formspree.io**, copy its ID (e.g. `xyzabcd`) and replace `YOUR_FORM_ID` in
  `action="https://formspree.io/f/YOUR_FORM_ID"`. The form then sends in the background and shows a thank-you message. Spam protection (a hidden "honeypot" field) is already included.
- Netlify users can instead add `data-netlify="true"` and `name="enquiry"` to the `<form>` and remove the `action`.

### Map pins
The two maps on `contact.html` are pinned to the exact coordinates of BWS's own Google Maps business listings (Miri `4.446917,114.011563`, Bintulu `3.2724729,113.0802423`), and "Open in Google Maps" opens those listings. If an office moves, change `MIRI_LL` / `BTU_LL` and the place links in `tools/generate_site.py`, or edit the `q=` coordinates in the iframe `src` and the link `href` in `contact.html`.

### Change colours or fonts
Edit the variables at the top of `site/assets/css/styles.css`. If you change fonts, update the Google Fonts `<link>` in each page's `<head>`.

## Bahasa Melayu (future)
The site is English-only for now, with all text in the HTML (none in the JS). To add BM, copy the pages into `site/ms/`, translate them, set `<html lang="ms">`, add a language link to the header, and add `<link rel="alternate" hreflang="ms" href="…">` / `hreflang="en"` tags to each pair of pages. The contact form, job-apply and lightbox scripts work unchanged.

## Accessibility & performance notes
- WCAG AA contrast throughout, a skip link, visible focus outlines, a keyboard-operable menu (Esc closes, focus is trapped while open) and lightbox (← → Esc). Labelled form fields with error messages.
- Animations (reveal-on-scroll, counters, client marquee) switch off when the visitor's device asks for reduced motion.
- Images are WebP with fixed `width`/`height` (no layout jumping), lazy-loaded below the fold, and use `srcset` so phones get smaller files.
- Lighthouse (mobile, local test server): **Performance 91–99, Accessibility 100, Best Practices 100, SEO 100** on every page. Real hosting with compression should be equal or better.

## Tools (optional)
- `tools/generate_site.py` is the script that generated the HTML pages from shared header/footer templates. Use it **or** hand-edit the HTML, not both: running it overwrites every page. Run with `python3 tools/generate_site.py`.
- `tools/make_logo.py` rebuilds the logo SVGs. It needs `pip install fonttools` and the Noto Serif variable font (`NotoSerif[wdth,wght].ttf` from github.com/google/fonts, saved as `fonts/NotoSerif.ttf`).

## Assets still needed from BWS (placeholders)
See the list below. Each placeholder is marked in the HTML with a `PLACEHOLDER` comment.

| # | Where | What to supply |
|---|---|---|
| 1 | `careers.html` | **Real job openings** (3 example roles are shown now). Remove or replace before launch |
| 3 | `hse.html` | **ISO 9001:2015 certificate** scan (TÜV NORD) |
| 4 | `projects.html` | Photos of **cable laying / termination**, **instrument calibration** and **blasting & painting** at the Bintulu yard |
| 5 | `contact.html` | **Formspree form ID** (or keep the email fallback) |
| 6 | Everywhere | **Higher-resolution / newer site photos**. Current photos come from the old website; many are small (448–1024 px) and some have date stamps burned in |
| 7 | `clients.html`, home | A sharper **ASEAN Bintulu Fertilizer** logo, and confirmation BWS is happy to display client logos |
| 8 | Home / footer | Confirm the stats (20+ years, 2 bases, 4 disciplines, 10+ clients) and that the **CIDB grade/categories** and **PETRONAS licence** wording is as BWS wants it shown |
| 9 | Logo | If an original vector logo exists (from the printer/sign maker), swap it in for the rebuilt SVG |
