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

- **Fonts:** *Source Serif 4* Bold (headings) and *Source Sans 3* (body) are **self-hosted** in `site/assets/fonts/` and preloaded, so text never jumps when they load. *Noto Naskh Arabic* for the Jawi name comes from Google Fonts and downloads only the letters in that name.
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

Logos show in full colour, with a slight zoom on hover. To swap one, replace the file, keeping the name, or edit the list in `clients.html` and the marquee in `index.html`.
Company logos are trademarks of their owners. Showing them as a client list is common practice, but BWS should be comfortable it has worked for each client before publishing.

### Update the stats (home page)
In `index.html` search for `KEY STATS`. Each number looks like:
```html
<span class="stat-num" data-count="20" data-suffix="+">20+</span>
```
Change **both** `data-count` (what the counter animates to) and the text inside (what shows without JavaScript).

### Careers ("Send your CV")
The Careers page has no job list, just a "Send your CV" card. Its **Gmail / Outlook / Email app** buttons open a new email to **bwsesbhr@gmail.com** with the subject "Job Application – [Position]" and a short template. To change the address or template, edit `careers()` in `tools/generate_site.py` (`compose_links(...)`).

### Connect the contact form
The form is on `contact.html` (search for `CONTACT FORM`).
- **Right now** (no setup): after the form is filled in, *Send enquiry* offers **Gmail**, **Outlook** or **Email app**, each opening a pre-filled email to **bws@bwsengineeringsb.com**.
- **To receive submissions directly** (recommended): create a free form at **formspree.io**, copy its ID (e.g. `xyzabcd`) and replace `YOUR_FORM_ID` in
  `action="https://formspree.io/f/YOUR_FORM_ID"`. The form then sends in the background and shows a thank-you message. Spam protection (a hidden "honeypot" field) is already included.
- Netlify users can instead add `data-netlify="true"` and `name="enquiry"` to the `<form>` and remove the `action`.

### Map pins
The two maps on `contact.html` are pinned to the exact coordinates of BWS's own Google Maps business listings (Miri `4.446917,114.011563`, Bintulu `3.2724729,113.0802423`), and "Open in Google Maps" opens those listings. If an office moves, change `MIRI_LL` / `BTU_LL` and the place links in `tools/generate_site.py`, or edit the `q=` coordinates in the iframe `src` and the link `href` in `contact.html`.

### Change colours or fonts
Edit the variables at the top of `site/assets/css/styles.css`. To change fonts, replace the `.woff2` files in `site/assets/fonts/`, update the `@font-face` rules at the top of the CSS, and update the preload `<link>`s in each page's `<head>`.

### Source of company facts
Most company facts now come from **BWS's own Company Profile (October 2026)**: particulars, policies, certificates and licences, equipment list, awards, main clients, the work-experience list (81 contracts) and project photos.

**Deliberately not published:** contract sums, client contact persons and phone numbers, directors' names and IC numbers, bank facilities, TIN and SST numbers, and scans of certificates (they're watermarked "For company profile reference only").

### Certificate & licence details (update when renewed)
| Item | Number / scope | Valid until |
|---|---|---|
| ISO 9001:2015 (TÜV NORD) | 44 100 0072059 · first certified 2007 | 7 Feb 2028 |
| ISO 45001:2018 (BSI) | OHS 796482 | 25 Sep 2027 |
| CIDB G7 (B, CE, ME) | 0120030415-SR082502 · PPK, SPKK, STB | 7 Nov 2028 |
| PETRONAS licence | Company no. 200201029529 · onshore pipeline, fabrication, piping, repair & maintenance | 30 Jul 2027 |
| PETROS vendor | P250528-S | 6 Dec 2028 |
| DOSH Competent Firm (Petroleum Contractor) | JKKP/2022/26/76 · KPD 01, KPD 02 | 30 Mar 2028 |
| MOF | 357-30003574 | 12 Mar 2027 |
| UPKJ Sarawak | UPKJ/W/021609 · Class A · Rescue Contractor | (see letters) |
| CIDB SCORE | 3 stars (2025) | 1 Sep 2027 |

CIDB and TÜV NORD details were also checked against their public online registers.

### Bintulu addresses (checked online, Oct 2026)
- **Office:** Lot 782, Block 20 KLD, Jalan Tanjung Kidurong, 97007 Bintulu. Matches the old website, BWS's Google Maps listing and the profile.
- **Fabrication yard:** Lot 124–128, Block 20 KLD, Jalan Kidurong, 97000 Bintulu. This is the workplace registered with DOSH (Grade A inspection, 2021); the profile says "Lot 128". The same address is also KPG Engineering's Bintulu site office.
- The **ISO 45001 certificate (BSI)** lists "Sublot 1, Lot 802, Block 20 KLD", which matches no other record. **BWS should ask BSI to check it.**

### Key projects, awards and equipment
- **Key projects** (`PROJECTS` in `tools/generate_site.py`): 29 selected from the profile's work-experience list. Projects marked "Ongoing" have end dates after Oct 2026, or are listed as ongoing in the profile. **Remove the Ongoing badge when a project completes.**
- **Full project list** (`ALL_PROJECTS`, shown under "View all projects" on the Projects page): every work-experience entry from 2003 on, with team size where recorded. Entries 1–3 (1997–2001) pre-date incorporation and are left out; the profile has no entry 69.
- **Org charts** (About page): company and project organisation from the profile (updated 10.26), with roles only.
- **Awards** (`hse.html#awards`) and the **plant & equipment** summary (`services.html#equipment`) are summarised from the profile.

### Page header illustrations
Inner pages use blueprint-style line drawings (`site/assets/illustrations/*.svg`), generated by `tools/make_illustrations.py`. Edit the script and re-run it to change them, or replace an SVG with any 4:3 image.

### Security headers
`vercel.json` sets a Content-Security-Policy, HSTS, X-Frame-Options, Referrer-Policy and Permissions-Policy, plus caching rules (`site/.htaccess` does the same on Apache/cPanel). If you add a new external service (analytics, a chat widget, another embed), add its domain to the CSP or the browser will block it.

## Bahasa Melayu (future)
The site is English-only for now, with all text in the HTML (none in the JS). To add BM, copy the pages into `site/ms/`, translate them, set `<html lang="ms">`, add a language link to the header, and add `<link rel="alternate" hreflang="ms" href="…">` / `hreflang="en"` tags to each pair of pages. The contact form, job-apply and lightbox scripts work unchanged.

## Accessibility & performance notes
- WCAG AA contrast throughout, a skip link, visible focus outlines, a keyboard-operable menu (Esc closes, focus is trapped while open) and lightbox (← → Esc). Labelled form fields with error messages.
- Animations (reveal-on-scroll, counters, client marquee) switch off when the visitor's device asks for reduced motion.
- Images are WebP with fixed `width`/`height` (no layout jumping), lazy-loaded below the fold, and use `srcset` so phones get smaller files.
- Lighthouse (mobile, local test server): **Performance 98–99, Accessibility 100, Best Practices 100, SEO 100**, layout shift 0, blocking time 0 ms.
- Scrolling is kept cheap: no backdrop blur or blend modes, only opacity/transform animations, and a throttled scroll handler. It measured a steady 60 fps.

## Tools (optional)
- `tools/generate_site.py` is the script that generated the HTML pages from shared header/footer templates. Use it **or** hand-edit the HTML, not both: running it overwrites every page. Run with `python3 tools/generate_site.py`.
- `tools/make_logo.py` rebuilds the logo SVGs. It needs `pip install fonttools` and the Noto Serif variable font (`NotoSerif[wdth,wght].ttf` from github.com/google/fonts, saved as `fonts/NotoSerif.ttf`).

## Assets still needed from BWS (placeholders)
See the list below. Each placeholder is marked in the HTML with a `PLACEHOLDER` comment.

| # | Where | What to supply |
|---|---|---|
| 4 | `projects.html` | Real photos of **cable laying / termination**, **instrument calibration** and **blasting & painting** (blueprint illustrations stand in for now: gallery items with `ill:` in `tools/generate_site.py`) |
| 5 | `contact.html` | **Formspree form ID** (or keep the email fallback) |
| 6 | Everywhere | **Higher-resolution / newer site photos**. Current photos come from the old website; many are small (448–1024 px) and some have date stamps burned in |
| 7 | `clients.html`, home | A sharper **ASEAN Bintulu Fertilizer** logo, and confirmation BWS is happy to display client logos |
| 8 | Home | Confirm the stats (20+ years, 80+ contracts, 2 bases, 15+ clients) |
| 9 | Logo | If an original vector logo exists (from the printer/sign maker), swap it in for the rebuilt SVG |
