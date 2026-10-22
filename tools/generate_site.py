# Page generator for the BWS static site: writes plain HTML into ../site.
# Optional. If you edit the HTML files by hand, do NOT re-run this (it overwrites them).
import json, os, re
from urllib.parse import quote

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site") + "/"
SITE = "https://www.bwsengineeringsb.com"
# BWS Portal (Laravel app in portal/): job openings, online applications and the HR admin panel.
# Until it is live, the Careers page simply keeps its "Send your CV" email option.
PORTAL = "https://portal.bwsengineeringsb.com"
JAWI = "كجروتران بي دبليو إيس سندیریان برحد"

# ---------------------------------------------------------------- icons
def icon(name, cls=""):
    P = {
        "plant": '<path d="M3 21h18M5 21V10l4 3V9l4 3V5h3v16M19 21V8h-3"/><path d="M8 17h1M12 17h1"/>',
        "mech": '<path d="M3 9h5v6H3zM16 9h5v6h-5zM8 12h8"/><path d="M12 12V6M9 6h6M10 3h4"/>',
        "civil": '<path d="M3 21h18M5 21V9l7-5 7 5v12"/><path d="M9 21v-6h6v6M9 11h6"/>',
        "ei": '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
        "shield": '<path d="M12 3 4 6v6c0 5 3.4 8.3 8 9 4.6-.7 8-4 8-9V6z"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
        "badge": '<circle cx="12" cy="9" r="6"/><path d="m9 14-1.5 7L12 19l4.5 2L15 14"/>',
        "doc": '<path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5M10 13h6M10 17h6"/>',
        "calendar": '<rect x="3" y="5" width="18" height="16" rx="1"/><path d="M3 10h18M8 3v4M16 3v4"/>',
        "flag": '<path d="M5 21V4M5 4h11l-2 4 2 4H5"/>',
        "pin": '<path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
        "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/>',
        "fax": '<path d="M7 9V3h10v6M7 17H4V9h16v8h-3"/><path d="M7 14h10v7H7z"/>',
        "mail": '<rect x="3" y="5" width="18" height="14" rx="1"/><path d="m3 7 9 6 9-6"/>',
        "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
        "briefcase": '<rect x="3" y="7" width="18" height="13" rx="1"/><path d="M9 7V4h6v3M3 12h18"/>',
        "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
        "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
        "close": '<path d="M6 6l12 12M18 6 6 18"/>',
        "left": '<path d="m15 5-7 7 7 7"/>',
        "right": '<path d="m9 5 7 7-7 7"/>',
        "hat": '<path d="M3 17h18M5 17a7 7 0 0 1 14 0M12 6v4M9 8.5l1 2.5M15 8.5l-1 2.5"/>',
        "warn": '<path d="M12 3 2 20h20z"/><path d="M12 10v4M12 17v.01"/>',
        "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0M16 4.5a3.5 3.5 0 0 1 0 7M18 14a6.5 6.5 0 0 1 3.5 6"/>',
        "factory": '<path d="M3 21V11l5 3v-3l5 3v-3l5 3V4h3v17z"/>',
    }[name]
    c = f' class="{cls}"' if cls else ""
    # width/height are a fallback size: without them Safari can shrink an icon to nothing inside a flex button
    return f'<svg{c} width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{P}</svg>'

PANELS = '<span class="panels" aria-hidden="true"><i></i><i></i><i></i></span>'

def eyebrow(num, label):
    # num is ignored: sections are labelled, not numbered
    return f'<p class="eyebrow">{label}</p>'

def img(key, alt, w, h, sizes="(min-width: 60rem) 50vw, 100vw", big=False, cls="", eager=False):
    src = f"assets/img/{key}-800.webp"
    sets = [(480, f"assets/img/{key}-480.webp"), (800, f"assets/img/{key}-800.webp")]
    if big: sets.append((1600, f"assets/img/{key}-1600.webp"))
    sets = [(w, u) for w, u in sets if os.path.exists(OUT + u)]
    srcset = f' srcset="{", ".join(f"{u} {w}w" for w, u in sets)}" sizes="{sizes}"' if len(sets) > 1 else ""
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return f'<img{c} src="{src}"{srcset} width="{w}" height="{h}" alt="{alt}" {load}>'

def ph(what, note=""):
    return (f'<!-- PLACEHOLDER PHOTO: {what}. Replace this <div class="ph"> with an <img> (see README). -->\n'
            f'<div class="ph" role="img" aria-label="Photo coming soon: {what}"><div><strong>Photo placeholder</strong>{what}{("<br>" + note) if note else ""}</div></div>')

# ---------------------------------------------------------------- shared bits
NAV = [("index.html", "Home"), ("about.html", "About"), ("services.html", "Services"), ("clients.html", "Clients"),
       ("projects.html", "Projects"), ("hse.html", "HSE &amp; Quality"), ("careers.html", "Careers"), ("contact.html", "Contact")]

FONTS = ("https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700"
         "&family=Source+Serif+4:wght@700&display=swap")

ORG_LD = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "@id": SITE + "/#organization",
    "name": "BWS Engineering Sdn Bhd",
    "alternateName": ["BWS Engineering Sdn. Bhd.", JAWI],
    "url": SITE + "/",
    "logo": SITE + "/assets/logo/logo.svg",
    "image": SITE + "/assets/img/og-image.jpg",
    "description": "Bumiputera engineering construction and maintenance contractor for the oil and gas industries, based in Miri and Bintulu, Sarawak. PETRONAS licensed, CIDB registered, ISO 9001:2015 certified by TÜV NORD.",
    "foundingDate": "2002-10",
    "email": "bws@bwsengineeringsb.com",
    "sameAs": ["https://www.facebook.com/bwsengineeringsdnbhd/"],
    "contactPoint": [{"@type": "ContactPoint", "contactType": "customer service", "email": "bws@bwsengineeringsb.com", "telephone": "+60-85-652743", "areaServed": "MY"}, {"@type": "ContactPoint", "contactType": "recruitment", "email": "bwsesbhr@gmail.com"}],
    "telephone": "+60-85-652743",
    "faxNumber": "+60-85-652709",
    "areaServed": "Malaysia",
    "knowsAbout": ["Industrial plant construction and maintenance", "Mechanical and piping work",
                   "Civil, building and structural steel construction", "Electrical and instrumentation work"],
    "address": {"@type": "PostalAddress", "streetAddress": "Lot 1743, Block 3 MCLD, Piasau Industrial Estate Phase III, Jalan Prunus 1",
                "addressLocality": "Miri", "postalCode": "98000", "addressRegion": "Sarawak", "addressCountry": "MY"},
    "subOrganization": [
        {"@type": "LocalBusiness", "@id": SITE + "/#miri", "name": "BWS Engineering Sdn Bhd: Main Office cum Workshop (Miri)",
         "image": SITE + "/assets/img/facility-miri-hq-1600.webp", "telephone": "+60-85-652743", "faxNumber": "+60-85-652709", "email": "bws@bwsengineeringsb.com",
         "address": {"@type": "PostalAddress", "streetAddress": "Lot 1743, Block 3 MCLD, Piasau Industrial Estate Phase III, Jalan Prunus 1",
                     "addressLocality": "Miri", "postalCode": "98000", "addressRegion": "Sarawak", "addressCountry": "MY"},
         "geo": {"@type": "GeoCoordinates", "latitude": 4.446917, "longitude": 114.011563}, "hasMap": "https://www.google.com/maps?cid=4214669276461699859"},
        {"@type": "LocalBusiness", "@id": SITE + "/#bintulu", "name": "BWS Engineering Sdn Bhd: Bintulu Office cum Fabrication Yard",
         "image": SITE + "/assets/img/facility-bintulu-yard-1600.webp", "telephone": "+60-86-252476", "email": "bws@bwsengineeringsb.com",
         "address": {"@type": "PostalAddress", "streetAddress": "Lot 782, Block 20, Kemena Land District, Jalan Tanjung Kidurong",
                     "addressLocality": "Bintulu", "postalCode": "97007", "addressRegion": "Sarawak", "addressCountry": "MY"},
         "geo": {"@type": "GeoCoordinates", "latitude": 3.2724729, "longitude": 113.0802423}, "hasMap": "https://www.google.com/maps?cid=6044021619715074034"},
    ],
}

HEROES = {"index.html": "hero-column-erection"}

import sys as _sys
_sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_css
build_css.build()  # src/css/*.css -> site/assets/css/styles.css, before it is hashed below

import hashlib as _hl
# Cache-busting version for CSS/JS: changes whenever either file changes
ASSET_V = _hl.md5(open(OUT + "assets/css/styles.css", "rb").read() + open(OUT + "assets/js/main.js", "rb").read()).hexdigest()[:8]

def head(page, title, desc, extra_ld=None):
    url = SITE + "/" + ("" if page == "index.html" else page)
    lds = [ORG_LD] + (extra_ld or [])
    ld = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False, separators=(",", ":"))}</script>' for x in lds)
    hero = HEROES.get(page)
    preload = ""
    if hero:
        sets = [(w, f"assets/img/{hero}-{w}.webp") for w in (480, 800, 1600) if os.path.exists(OUT + f"assets/img/{hero}-{w}.webp")]
        preload = (f'<link rel="preload" as="image" href="assets/img/{hero}-800.webp" imagesrcset="{", ".join(f"{u} {w}w" for w, u in sets)}" '
                   f'imagesizes="{"(min-width: 60rem) 45vw, 100vw" if page == "index.html" else "(min-width: 60rem) 40vw, 100vw"}" fetchpriority="high">\n')
    return f'''<!doctype html>
<html lang="en-MY">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#0A1240">
<meta name="robots" content="index, follow">
<!-- Open Graph / Twitter -->
<meta property="og:type" content="website">
<meta property="og:site_name" content="BWS Engineering Sdn Bhd">
<meta property="og:locale" content="en_MY">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/assets/img/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="BWS Engineering Sdn Bhd: oil &amp; gas construction and maintenance, Miri &amp; Bintulu, Sarawak">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{SITE}/assets/img/og-image.jpg">
<!-- Icons -->
<link rel="icon" href="favicon.ico" sizes="32x32">
<link rel="icon" href="assets/logo/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="assets/logo/apple-touch-icon.png">
<link rel="manifest" href="site.webmanifest">
<!-- Fonts -->
<link rel="preload" href="assets/fonts/source-serif-4-700-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/source-sans-3-latin.woff2" as="font" type="font/woff2" crossorigin>
{preload}<link rel="stylesheet" href="assets/css/styles.css?v={ASSET_V}">
<script src="assets/js/main.js?v={ASSET_V}" defer></script>
{ld}
</head>'''

def header(page):
    desk = "".join(
        f'<li><a href="{h}"{" aria-current=\"page\"" if h == page else ""}>{t}</a></li>'
        for h, t in NAV if h != "index.html")
    mob = "".join(
        f'<li><a href="{h}"{" aria-current=\"page\"" if h == page else ""}>{t}</a></li>'
        for i, (h, t) in enumerate(NAV, 1))
    return f'''<body>
<a class="skip-link" href="#main">Skip to content</a>
<div class="topbar on-dark">
  <div class="container topbar-inner">
    <p class="topbar-contact">Miri <a href="tel:+6085652743">085-652743</a><span aria-hidden="true">·</span>Bintulu <a href="tel:+6086252476">086-252476</a><span aria-hidden="true">·</span><a href="mailto:bws@bwsengineeringsb.com">bws@bwsengineeringsb.com</a></p>
    <p class="topbar-creds">ISO 9001 · ISO 45001<span aria-hidden="true">·</span>CIDB G7<span aria-hidden="true">·</span>PETRONAS &amp; PETROS Licensed</p>
  </div>
</div>
<header class="site-header">
  <div class="container header-inner">
    <a class="brand" href="index.html"{' aria-current="page"' if page == "index.html" else ""}>
      <img src="assets/logo/logo.svg" width="56" height="43" alt="">
      <span class="brand-text">
        <span class="brand-name">BWS Engineering Sdn&nbsp;Bhd</span>
        <span class="jawi" dir="rtl" lang="ms-Arab">{JAWI}</span>
      </span>
      <span class="visually-hidden">: home</span>
    </a>
    <nav class="primary-nav" aria-label="Main">
      <ul>{desk}</ul>
    </nav>
    <a class="btn btn--primary header-cta" href="contact.html#enquiry">Request a Quote</a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="mobile-menu">
      {icon("menu")}<span class="visually-hidden">Open menu</span>
    </button>
  </div>
</header>
<div class="mobile-menu" id="mobile-menu" role="dialog" aria-modal="true" aria-label="Site menu" hidden>
    <div class="mobile-menu-top">
      <img src="assets/logo/logo-white.svg" width="56" height="43" alt="BWS Engineering">
      <button class="nav-close" type="button">{icon("close")}<span class="visually-hidden">Close menu</span></button>
    </div>
    <nav aria-label="Main (mobile)"><ul>{mob}</ul></nav>
    <a class="btn btn--light" href="contact.html#enquiry">Request a Quote</a>
    <p class="mobile-menu-contact">Miri <a href="tel:+6085652743">085-652743</a> · Bintulu <a href="tel:+6086252476">086-252476</a><br><a href="mailto:bws@bwsengineeringsb.com">bws@bwsengineeringsb.com</a></p>
</div>
<main id="main">'''

CTA = f'''
<section class="cta-band" aria-labelledby="cta-title">
  <div class="container cta-inner">
    <div>
      <h2 id="cta-title">Discuss your project requirements with BWS</h2>
      <p>We look forward to serving you better.</p>
    </div>
    <div class="btn-row">
      <a class="btn btn--light" href="contact.html#enquiry">Request a Quote {icon("arrow")}</a>
      <a class="btn btn--outline-light" href="tel:+6085652743">Call 085-652743</a>
    </div>
  </div>
</section>'''

def footer():
    links = "".join(f'<li><a href="{h}">{t}</a></li>' for h, t in NAV)
    return f'''
</main>
<footer class="site-footer on-dark">
  <div class="container footer-top">
    <div class="footer-brand">
      <img src="assets/logo/logo-white.svg" width="74" height="56" alt="">
      <span class="brand-name">BWS Engineering Sdn&nbsp;Bhd</span>
      <span class="jawi" dir="rtl" lang="ms-Arab">{JAWI}</span>
      <p>Wholly owned Bumiputera engineering construction and maintenance contractor for the oil and gas industries, since October 2002.</p>
      <div class="licences">
        <span>PETRONAS Licensed</span><span>CIDB Registered</span><span>ISO 9001:2015 · TÜV NORD</span>
      </div>
    </div>
    <div>
      <h2>Main Office</h2>
      <div class="footer-office">
        <strong>Office cum Workshop, Miri</strong>
        <address>Lot 1743, Block 3 MCLD, Piasau Industrial Estate Phase III, Jalan Prunus 1, 98000 Miri, Sarawak, Malaysia</address>
        <ul>
          <li>Tel: <a href="tel:+6085652743">085-652743</a> / <a href="tel:+6085652744">44</a> / <a href="tel:+6085652745">45</a></li>
          <li>Fax: 085-652709</li>
        </ul>
      </div>
    </div>
    <div>
      <h2>Bintulu</h2>
      <div class="footer-office">
        <strong>Office cum Fabrication Yard</strong>
        <address>Lot 782, Block 20, Kemena Land District, Jalan Tanjung Kidurong, 97007 Bintulu, Sarawak, Malaysia</address>
        <ul><li>Tel: <a href="tel:+6086252476">086-252476</a></li></ul>
      </div>
      <div class="footer-office">
        <strong>Email</strong>
        <ul>
          <li>Enquiries: <a href="mailto:bws@bwsengineeringsb.com">bws@bwsengineeringsb.com</a></li>
          <li>Also: <a href="mailto:bwsesb@gmail.com">bwsesb@gmail.com</a></li>
          <li>Careers: <a href="mailto:bwsesbhr@gmail.com">bwsesbhr@gmail.com</a></li>
        </ul>
      </div>
    </div>
    <nav aria-label="Footer">
      <h2>Quick links</h2>
      <ul>{links}</ul>
      <a class="social" href="https://www.facebook.com/bwsengineeringsdnbhd/" target="_blank" rel="noopener"><svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M13.5 21v-7.5h2.5l.4-3h-2.9V8.6c0-.9.3-1.5 1.5-1.5h1.5V4.4c-.3 0-1.2-.1-2.2-.1-2.2 0-3.7 1.3-3.7 3.8v2.4H8v3h2.6V21z"/></svg>Facebook<span class="visually-hidden"> (opens in a new tab)</span></a>
    </nav>
  </div>
  <div class="container footer-bottom">
    <p>© <span data-year>2026</span> BWS Engineering Sdn Bhd (597192-V). All rights reserved.</p>
    <p><a href="vendor.html">Vendor information</a> · <a href="privacy.html">Privacy Notice</a> · Miri · Bintulu · Sarawak, Malaysia</p>
  </div>
</footer>
</body>
</html>
'''

def panels(photo, w, h, sizes, alt="", cls=""):
    # Signature: a photo seen through the three BWS logo panels (4 : 5 : 3, sky glow on the middle one)
    return (f'<div class="bws-panels {cls}"{"" if alt else " aria-hidden=\"true\""}>'
            f'{img(photo, alt, w, h, sizes, big=True, eager=True)}<span class="bws-glow"></span></div>')

def illus_panels(name):
    # Blueprint-style illustration (tools/make_illustrations.py) seen through the three logo panels
    return (f'<div class="bws-panels bws-panels--page bws-panels--illus" aria-hidden="true">'
            f'<img src="assets/illustrations/{name}.svg" width="800" height="600" alt="" fetchpriority="high"><span class="bws-glow"></span></div>')

def page_hero(crumb, title, lead, illus=None, *_unused):
    return f'''
<section class="page-hero on-dark">
  <div class="container page-hero-grid{"" if illus else " page-hero-grid--text"}">
    <div class="page-hero-inner">
      <ol class="breadcrumb"><li><a href="index.html">Home</a></li><li aria-current="page">{crumb}</li></ol>
      <h1>{title}</h1>
      <p>{lead}</p>
    </div>
    {illus_panels(illus) if illus else ""}
  </div>
</section>'''

def compose_links(to, subject, body="", primary=True):
    """Three ways to send the same pre-filled email: Gmail web, Outlook web, or the device's mail app."""
    q = lambda v: quote(v, safe="")
    gmail = f"https://mail.google.com/mail/?view=cm&amp;fs=1&amp;to={q(to)}&amp;su={q(subject)}" + (f"&amp;body={q(body)}" if body else "")
    outlook = f"https://outlook.office.com/mail/deeplink/compose?to={q(to)}&amp;subject={q(subject)}" + (f"&amp;body={q(body)}" if body else "")
    mailto = f"mailto:{to}?subject={q(subject)}" + (f"&amp;body={q(body)}" if body else "")
    cls = "btn btn--primary" if primary else "btn btn--ghost"
    return (f'<div class="mail-choice" role="group" aria-label="Choose how to send your email">'
            f'<a class="{cls}" href="{gmail}" target="_blank" rel="noopener">{icon("mail")}Gmail<span class="visually-hidden"> (opens in a new tab)</span></a>'
            f'<a class="btn btn--ghost" href="{outlook}" target="_blank" rel="noopener">{icon("mail")}Outlook<span class="visually-hidden"> (opens in a new tab)</span></a>'
            f'<a class="btn btn--ghost" href="{mailto}">{icon("mail")}Email app</a></div>')

def write(name, html):
    with open(OUT + name, "w") as f:
        f.write(html)
    print("wrote", name, len(html))

# ---------------------------------------------------------------- content
SERVICES = [
    ("plant", "plant", "Industrial Plant Construction and Maintenance",
     "Construction and maintenance for oil and gas facilities, power generation plants and wood-based factories.",
     ["Oil and gas facilities", "Power generation plants", "Wood-based factories"],
     "BWS provides construction and maintenance services for industrial plants, drawing on more than two decades of work in operating oil and gas facilities. Our scope covers oil and gas facilities, power generation plants and wood-based factories, supported from our bases in Miri and Bintulu. Every job is carried out under our HSE policy and our ISO 9001:2015 Quality Management System.",
     ("power-import-aerial-1", "Aerial view of the MLNG Power Import Project facility under construction", 675, 520)),
    ("mechanical", "mech", "Mechanical and Piping Work",
     "Equipment installation and testing, piping fabrication, installation and testing, plus blasting and painting.",
     ["Mechanical equipment installation and testing", "Piping fabrication, installation and testing", "Blasting and painting work"],
     "Our mechanical teams install and test mechanical equipment, and fabricate, install and test piping systems. Fabrication is carried out at our Miri workshop and at our Bintulu yard, which has a covered fabrication shop, an open fabrication area, blasting and painting facilities and NDT facilities.",
     ("mech-heavy-lift", "Mobile crane lifting a large cylindrical vessel on site while a rigger in a hi-vis vest looks on", 800, 600)),
    ("civil", "civil", "Civil, Building and Structural Steel Construction",
     "From site clearing and earthwork to foundations, industrial buildings, warehouses and jetties.",
     ["Site clearing", "Earthwork", "Foundations", "Industrial buildings and warehouses", "Jetties"],
     "From site clearing and earthwork through to foundations, we deliver the civil works that industrial facilities depend on. Our scope extends to industrial buildings, warehouses, structural steel and jetties. BWS is registered with the Construction Industry Development Board (CIDB) for various categories of construction activities.",
     ("civil-rebar", "Construction crew in coveralls tying reinforcement steel for a foundation, with an excavator behind", 800, 460)),
    ("electrical", "ei", "Electrical and Instrumentation Work",
     "Cable laying, equipment installation, instrument calibration and testing, and commissioning assistance.",
     ["Cable laying and testing", "Electrical equipment installation and testing", "Instrument calibration, installation and testing", "Commissioning assistance"],
     "Our electrical and instrumentation team carries out cable laying and testing, and the installation and testing of electrical equipment. We calibrate, install and test instruments, and provide commissioning assistance to help bring systems safely into service.",
     ("ei-switchgear", "Row of electrical switchgear panels installed in a substation room", 800, 599)),
]

# Key projects, selected from the "Work Experience" list in the BWS Company Profile (Oct 2026, 81 contracts since 1997).
# Contract sums and client contact persons in the profile are deliberately NOT published.
# (years, client, project, location, scope tags, related service ids, ongoing?)
PROJECTS = [
    ("2026 – 2027", "Shell MDS", "Multi-mechanical package (MECH03) for Project Rejuv: steel structure, equipment, piping, insulation and painting", "Bintulu, Sarawak",
     ["Equipment installation", "Piping", "Insulation", "Painting"], ["mechanical", "plant"], True),
    ("2026 – 2027", "PETRONAS Carigali", "Compressed-air pressurisation for pipeline pre-decommissioning, BV106 to KP131.2", "Lawas, Sarawak",
     ["Pipeline pre-decommissioning"], ["mechanical"], True),
    ("2025 – 2028", "Ministry of Rural and Regional Development", "Road from Kampung Murud Suang to the Kampung Long Pos junction", "Lawas, Sarawak",
     ["Earthworks", "Drainage", "Roads", "Bridges", "Piling"], ["civil"], True),
    ("2025 – 2027", "Regional Corridor Development Authority (RECODA)", "Highland Development Agency Package 5: water supply and electricity infrastructure", "Bario, Mulu &amp; Telang Usan, Sarawak",
     ["Water supply", "Electricity infrastructure"], ["civil", "electrical"], True),
    ("2023 – 2026", "Housing Development Corporation (PPP)", "50 Rumah Spektra Permata houses, Skim Pembesaran Kampung Gedong Baru (IBS)", "Samarahan, Sarawak",
     ["Building construction", "Industrialised Building System"], ["civil"], True),
    ("2023 – 2026", "Samsung E&amp;A, for Sarawak Shell", "Rosmari-Marjoram Onshore Gas Plant (Shell OGP Project): underground piping, pipelines, brownfield and BIF area works", "Bintulu, Sarawak",
     ["UG process piping (PE100)", "Pipelines &amp; brownfield", "Civil &amp; steel structures", "E&amp;I"], ["mechanical", "civil", "electrical"], False),
    ("2024", "PETRONAS Carigali", "EPCIC of the Sipitang scraper station at KP91, Sabah Sarawak Gas Pipeline", "Sipitang, Sabah",
     ["Pipeline &amp; piping", "Civil", "Instrument &amp; control", "Electrical", "Cathodic protection", "Tie-ins"], ["plant", "mechanical", "electrical"], False),
    ("2024", "Malaysia LNG", "Upgrade of the Train 9 LNG rundown flow meter to allocation metering (turnaround scope)", "Bintulu, Sarawak",
     ["Procurement", "Construction", "Commissioning", "Metering"], ["plant", "electrical"], False),
    ("2019 – 2025", "Rural Water Supply Department (JBALB) Sarawak", "Miri Water Supply Source Development Phase 2, Sarawak Water Grid Programme: raw water transfer from Batang Baram", "Miri, Sarawak",
     ["1,600 mm pipeline", "Pumping station", "HT line", "Earthworks &amp; M&amp;E"], ["civil", "mechanical", "electrical"], False),
    ("2022 – 2025", "Malaysia LNG", "EPCC of the Power Import Project (Transgrid-BWS JV)", "Bintulu, Sarawak",
     ["Engineering", "Procurement", "Construction", "Commissioning"], ["plant", "electrical"], False),
    ("2022 – 2024", "JKR Malaysia", "Full replacement of 12 classrooms and facilities, SK Jalan Haji Baki", "Padawan, Sarawak",
     ["Building construction"], ["civil"], False),
    ("2022 – 2023", "PTTEP", "EPCIC of a shelter at the Bintulu Onshore Receiving Facility", "Bintulu, Sarawak",
     ["Structure fabrication &amp; installation"], ["plant", "civil"], False),
    ("2020 – 2024", "PETRONAS Carigali", "Term contract, Sabah Sarawak Mechanical (Package B): pipeline rehabilitation and repair, KP-210 to KP-503", "Miri – Bintulu, Sarawak",
     ["Pipeline rehabilitation &amp; repair"], ["mechanical"], False),
    ("2020 – 2021", "Malaysia LNG", "EPCC of Kenyalang Project 2.0: tie-ins to the LNG loading, vapour return and firewater lines", "Bintulu, Sarawak",
     ["Engineering", "Procurement", "Construction", "Commissioning"], ["plant"], False),
    ("2020 – 2023", "Ministry of International Trade and Industry", "Site clearing, earthworks and infrastructure, Sematan Industrial Area Phase I", "Kuching Division, Sarawak",
     ["Earthworks", "Roads", "Drainage", "M&amp;E services"], ["civil"], False),
    ("2019 – 2023", "Malaysia LNG Dua", "EPCC of the gasoline and NGL metering skid upgrades", "Bintulu, Sarawak",
     ["Metering skids", "Instrumentation"], ["plant", "electrical"], False),
    ("2019 – 2022", "PETRONAS, for ASEAN Bintulu Fertilizer", "Structure improvement at the offsite plant: ammonia tanks and shed", "Bintulu, Sarawak",
     ["Fabrication", "Scaffolding", "Painting"], ["civil"], False),
    ("2019 – 2021", "PRPC Utilities &amp; Facilities", "Two-year term contract for non-metallic piping rectification", "Pengerang, Johor",
     ["Non-metallic piping"], ["mechanical"], False),
    ("2018 – 2019", "JGC SP, for Hengyuan Refining", "Mechanical work package for the Clean Air Regulation Project: new wet gas scrubber facilities", "Port Dickson, Negeri Sembilan",
     ["Steel structure", "Piping", "Insulation", "Painting"], ["mechanical"], False),
    ("2017 – 2020", "PETRONAS RAPID (PRPC)", "UIO facilities: underground pressurised non-metallic firewater network, 16 km of GRE pipeline", "Pengerang, Johor",
     ["GRE pipe laying &amp; lamination", "Excavation &amp; box culverts", "Hydrotest"], ["mechanical", "civil"], False),
    ("2016 – 2018", "Malaysia LNG", "Piping, protective coating, insulation, minor civil and scaffolding works, PETRONAS LNG Complex", "Bintulu, Sarawak",
     ["Piping", "Coating", "Insulation", "Team of 296"], ["mechanical"], False),
    ("2014 – 2015", "PETRONAS Dagangan", "EPCC of the PDB Miri Fuel Terminal", "Miri, Sarawak",
     ["Engineering", "Procurement", "Construction", "Commissioning"], ["plant", "civil"], False),
    ("2014 – 2015", "Shell MDS", "SMDS Rejuvenation Project 2015: mechanical work packages", "Bintulu, Sarawak",
     ["Steel structure", "Equipment", "Piping", "Insulation", "Painting"], ["mechanical"], False),
    ("2012 – 2013", "Malaysia LNG (Train 9 Project)", "New MLNG CSA office and warehouse, Jalan Kidurong", "Bintulu, Sarawak",
     ["Building construction", "Team of 160"], ["civil"], False),
    ("2007 – 2011", "PETRONAS Carigali, via Rekind–Simfoni consortium", "Miri Crude Oil Terminal (MCOT) Rejuvenation Project Phase 2: piping, supports and painting", "Miri, Sarawak",
     ["Piping", "Painting", "E&amp;I", "Teams of up to 150", "3.9 million man-hours"], ["mechanical"], False),
    ("2008 – 2011", "Sabah Shell Petroleum", "Installation, tie-in and commissioning of new furnace F-104, Labuan Crude Oil Terminal", "Labuan",
     ["Mechanical installation", "Tie-in", "Commissioning"], ["mechanical", "plant"], False),
    ("2005 – 2006", "PETRONAS Dagangan", "EPCC of the aviation depot at Bintulu Airport", "Bintulu, Sarawak",
     ["Engineering", "Procurement", "Construction", "Commissioning"], ["plant", "civil"], False),
    ("2003 – 2005", "Sarawak Shell", "Turnkey minor civil works, Bintulu Integrated Facilities: control centre revamp and pipe bridges", "Bintulu, Sarawak",
     ["Design", "Procurement", "Construction", "Commissioning", "237,296 man-hours"], ["civil"], False),
]

# Full work-experience list from the BWS Company Profile (Oct 2026), entries 4–81 (no. 69 is not used in the
# profile; entries 1–3 pre-date incorporation and are left out). Sector: "og" = oil, gas &amp; petrochemical,
# "gov" = government &amp; infrastructure. No contract sums or contact persons.
ALL_PROJECTS = [
    (4, "2003 – 2005", "Minor civil construction works (turnkey) for Bintulu Integrated Facilities", "Sarawak Shell Berhad", "og"),
    (5, "2005 – 2006", "EPCC of the PETRONAS Dagangan aviation depot, Bintulu Airport", "PETRONAS Dagangan Berhad", "og"),
    (6, "2006 – 2007", "EPCC for upgrading the loading metering system, Sibu Depot", "PETRONAS Dagangan Berhad", "og"),
    (7, "2006 – 2007", "EPCC of the fire-fighting system and other works, Miri Aviation Depot", "PETRONAS Dagangan Berhad", "og"),
    (8, "2007 – 2011", "Price agreement for civil and mechanical maintenance of PETRONAS service stations, Sarawak", "PETRONAS Dagangan Berhad", "og"),
    (9, "2007", "On-call general civil and building maintenance, PCSB Sarawak Operations", "PETRONAS Carigali Sdn Bhd", "og"),
    (10, "2007", "MCOT Rejuvenation Phase 2: shop fabrication of carbon steel piping", "PETRONAS Carigali, via Rekind–Simfoni consortium", "og"),
    (11, "2007 – 2008", "MCOT Rejuvenation Phase 2: blasting and painting works", "PETRONAS Carigali, via Rekind–Simfoni consortium", "og"),
    (12, "2008", "MCOT Rejuvenation Phase 2: pipe installation works", "PETRONAS Carigali, via Rekind–Simfoni consortium", "og"),
    (13, "2008 – 2011", "Installation, tie-in and commissioning of new furnace F-104, Labuan Crude Oil Terminal", "Sabah Shell Petroleum Co. Ltd", "og"),
    (14, "2008", "UHP water jetting services using the abseiling method", "Petra Resources Sdn Bhd", "og"),
    (15, "2008 – 2010", "PC30046 Tiga Field Station extension, MLNG Tiga plant", "Malaysia LNG Sdn Bhd", "og"),
    (16, "2008 – 2009", "Temporary camp facilities (Camp 6), Lapok – Long Lama Road", "Punj Lloyd Oil &amp; Gas (Malaysia) Sdn Bhd", "og"),
    (17, "2008 – 2009", "MCOT Rejuvenation Phase 2: cable tray and pipe support works", "PETRONAS Carigali, via Rekind–Simfoni consortium", "og"),
    (18, "2008 – 2009", "Clearing, grading and earthworks for the Bintulu Compressor Station", "Punj Lloyd Oil &amp; Gas (Malaysia) Sdn Bhd", "og"),
    (19, "2009", "Improvement works at MLNG Tiga upstream and process areas", "Malaysia LNG Sdn Bhd", "og"),
    (20, "2009 – 2010", "PC12350 Terminal Field Station extension", "Malaysia LNG Sdn Bhd", "og"),
    (21, "2009", "PC12303 installation of new headers at B-Track", "Malaysia LNG Sdn Bhd", "og"),
    (22, "2009", "Replacement of the Trunkline 1 beach valve hydraulic unit, MOVs and sphere receiver door", "Malaysia LNG Sdn Bhd", "og"),
    (23, "2009 – 2011", "MCOT Rejuvenation Phase 2: piping installation, blasting and painting", "PETRONAS Carigali, via Rekind–Simfoni consortium", "og"),
    (24, "2009 – 2011", "MCOT Rejuvenation Phase 2: electrical and instrumentation installation", "PETRONAS Carigali, via Rekind–Simfoni consortium", "og"),
    (25, "2009", "Classroom and teachers’ quarters cabins, furniture and equipment, 2nd Economic Stimulus Package", "Ministry of Education, Development Division", "gov"),
    (26, "2011", "PC12399 new blast-resilient turnaround office building, PETRONAS LNG Complex", "Malaysia LNG Sdn Bhd", "og"),
    (27, "2011", "Kumang Cluster onshore tie-in at MLNG-2 and Bintulu Integrated Facilities", "PETRONAS Carigali, via Petra Resources", "og"),
    (28, "2011", "PC20555 MCHE tube leaks improvement", "Malaysia LNG Sdn Bhd", "og"),
    (29, "2011 – 2012", "Above-ground piping work, C1/U1 area", "Shinko Plantech Co. Ltd (Malaysia)", "og"),
    (30, "2012", "Replacement of 30\" and 24\" slugcatcher valves at SC1 and two new vessels", "Malaysia LNG Sdn Bhd", "og"),
    (31, "2012", "Temporary facilities for the MLNG &amp; MLNG Dua New Common Reclaimer Project", "JGC SP (M) Sdn Bhd", "og"),
    (32, "2012 – 2013", "New MLNG CSA office and warehouse, Jalan Kidurong (LNG Train 9 Project)", "PETRONAS LNG 9 Sdn Bhd", "og"),
    (33, "2012 – 2013", "Steel structure, equipment, piping, insulation and painting, New Common Reclaimer Project", "JGC SP (M) Sdn Bhd", "og"),
    (34, "2012 – 2015", "Fabrication and welding services for plant changes, PETRONAS LNG Complex", "Malaysia LNG Sdn Bhd", "og"),
    (35, "2013", "Piping and pipe support installation at MLNG 2 &amp; 3, DGDM Project", "Aqeel Engineering &amp; Construction Sdn Bhd", "og"),
    (36, "2013 – 2014", "EPCC of metering facilities for backloading, Tanjung Manis OGC Jetty, Mukah", "Assar Senary", "og"),
    (37, "2014", "Acid gas removal unit cleaning and pipe welding, MLNG Turnaround 2014", "Malaysia LNG Sdn Bhd", "og"),
    (38, "2014", "Scaffolding for steel structure and equipment erection, PETRONAS LNG Train 9", "Nippon Express Co. Ltd", "og"),
    (39, "2014 – 2015", "General civil and concrete structures, SMDS Rejuvenation Project 2015", "Shell MDS (Malaysia) Sdn Bhd", "og"),
    (40, "2014 – 2015", "Procurement and construction of PTA village infrastructure", "Shell MDS (Malaysia) Sdn Bhd", "og"),
    (41, "2014 – 2015", "New main switchboard at Substation 7 and associated works", "Sarawak Shell Berhad", "og"),
    (42, "2014 – 2015", "EPCC of the PDB Miri Fuel Terminal", "PETRONAS Dagangan Berhad", "og"),
    (43, "2014 – 2015", "Mechanical work package Phase 1, SMDS Rejuvenation Project", "Shell MDS (Malaysia) Sdn Bhd", "og"),
    (44, "2016", "MLNG Dua Rejuvenation Project (WP2–WP4): manpower, tools, scaffolding and NDT", "GE Oil and Gas", "og"),
    (45, "2016 – 2018", "Piping and associated work, PETRONAS LNG Complex", "Malaysia LNG Sdn Bhd", "og"),
    (46, "2016 – 2017", "Demolition of the existing MLNG reclaimer unit (U-1200)", "Malaysia LNG Sdn Bhd", "og"),
    (47, "2017 – 2018", "LV main switchboards and underground cabling for the electrical distribution system, Miri", "Sarawak Shell Berhad", "og"),
    (48, "2017 – 2018", "Scaffolding systems for UIO facilities, RAPID", "PRPC Utilities &amp; Facilities, via OUI JV", "og"),
    (49, "2017 – 2019", "Rural water supply from Kampung Manggut to Kampung Supa, Medang, Tuie and Serabang, Betong", "Ministry of Rural and Regional Development (KKLW)", "gov"),
    (50, "2017 – 2018", "Refurbishment of Café Kemboja and lab pantry", "Shell MDS (Malaysia) Sdn Bhd", "og"),
    (51, "2017 – 2020", "RAPID UIO facilities: underground pressurised non-metallic firewater network", "PRPC Utilities &amp; Facilities Sdn Bhd", "og"),
    (52, "2018", "Decommissioning and removal of gas engine compressor skid Q, Bintulu Onshore Receiving Facility", "Murphy Sarawak Oil Co. Ltd", "og"),
    (53, "2018 – 2019", "Mechanical work package, Clean Air Regulation Project (wet gas scrubber facilities)", "JGC SP (M) Sdn Bhd, for Hengyuan Refining", "og"),
    (54, "2019 – 2022", "Structure improvement at the offsite plant, ASEAN Bintulu Fertilizer", "PETRONAS Project Delivery &amp; Technology", "og"),
    (55, "2019 – 2024", "Minor construction and modification works for PETRONAS onshore facilities", "PETRONAS Strategic Procurement (Downstream)", "og"),
    (56, "2019 – 2025", "Miri Water Supply Source Development Phase 2, Sarawak Water Grid Programme", "Jabatan Bekalan Air Luar Bandar Sarawak", "gov"),
    (57, "2019 – 2021", "Kampung Sadong Jaya Extension (upgrading): earth filling, roads and drainage, Samarahan", "Land and Survey Department, Sarawak", "gov"),
    (58, "2019 – 2021", "Two-year term contract for non-metallic piping rectification at PRPC UF", "PRPC Utilities &amp; Facilities Sdn Bhd", "og"),
    (59, "2019 – 2023", "EPCC of the gasoline and NGL metering skid upgrades, MLNG Dua", "Malaysia LNG Sdn Bhd", "og"),
    (60, "2020 – 2024", "Term contract, Sabah Sarawak Mechanical (Package B): pipeline rehabilitation and repair", "PETRONAS Carigali Sdn Bhd", "og"),
    (61, "2020", "Piping works for DELIMA Unit 41 (greenfield)", "Melaka Refinery Diesel Euro 5 Project", "og"),
    (62, "2020 – 2021", "EPCC of Kenyalang Project 2.0: tie-ins and associated facilities, PETRONAS LNG Complex", "Malaysia LNG Sdn Bhd", "og"),
    (63, "2020 – 2023", "Site clearing, earthworks and infrastructure, Sematan Industrial Area Phase I", "Ministry of International Trade and Industry", "gov"),
    (64, "2020 – 2021", "OSBL piping construction, Hengyuan Refining Euro IV project", "HQC Engineering Malaysia Sdn Bhd", "og"),
    (65, "2022 – 2024", "Full replacement of 12 classrooms and facilities, SK Jalan Haji Baki, Padawan", "Jabatan Kerja Raya Malaysia", "gov"),
    (66, "2022 – 2023", "EPCIC of a shelter, Bintulu Onshore Receiving Facility", "PTTEP", "og"),
    (67, "2022", "Demolition of old solvent concrete tank T-1203, PETRONAS LNG Complex", "Malaysia LNG Sdn Bhd", "og"),
    (68, "2022 – 2025", "EPCC of the Power Import Project (Transgrid-BWS JV)", "Malaysia LNG Sdn Bhd", "og"),
    (70, "2023 – 2024", "Shell OGP Project: underground process piping", "Samsung E&amp;A, for Sarawak Shell", "og"),
    (71, "2023 – 2024", "Procurement, construction and commissioning of a piping system (PC40008)", "PETRONAS Carigali Sdn Bhd", "og"),
    (72, "2023 – 2026", "Shell OGP Project: pipeline and brownfield work", "Samsung E&amp;A, for Sarawak Shell", "og"),
    (73, "2023 – 2026", "50 Rumah Spektra Permata houses, Gedong Baru, Samarahan (IBS)", "Housing Development Corporation", "gov"),
    (74, "2024 – 2025", "Removal and disposal of three vessels at the PM5 metering station, Miri", "PETRONAS Gas Berhad", "og"),
    (75, "2024", "Upgrade of the Train 9 LNG rundown flow meter to allocation metering", "Malaysia LNG Sdn Bhd", "og"),
    (76, "2024", "EPCIC of the Sipitang scraper station at KP91, Sabah Sarawak Gas Pipeline", "PETRONAS Carigali Sdn Bhd", "og"),
    (77, "2024 – 2026", "Shell OGP Project: Bintulu Integrated Facilities area work", "Samsung E&amp;A, for Sarawak Shell", "og"),
    (78, "2025 – 2027", "Highland Development Agency Package 5: water supply and electricity infrastructure, Bario / Mulu / Telang Usan", "Regional Corridor Development Authority (RECODA)", "gov"),
    (79, "2025 – 2028", "Road from Kampung Murud Suang to the Kampung Long Pos junction, Lawas", "Ministry of Rural and Regional Development", "gov"),
    (80, "2026 – 2027", "Multi-mechanical package MECH03 for Project Rejuv", "Shell MDS (Malaysia) Sdn Bhd", "og"),
    (81, "2026 – 2027", "Compressed-air pressurisation for pipeline pre-decommissioning, Lawas", "PETRONAS Carigali Sdn Bhd", "og"),
]

# Team size per entry, where the profile records it ("Manpower")
MANPOWER = {4: 90, 5: 50, 6: 20, 7: 30, 8: 15, 9: 10, 10: 77, 11: 15, 12: 151, 13: 30, 14: 10, 15: 70, 16: 27, 17: 36, 18: 12,
            19: 20, 20: 80, 21: 50, 22: 84, 23: 150, 24: 80, 25: 40, 26: 50, 27: 12, 28: 10, 29: 12, 30: 20, 31: 12, 32: 160,
            33: 100, 34: 20, 35: 70, 36: 48, 37: 50, 39: 50, 40: 70, 41: 20, 42: 60, 45: 296, 46: 30}

def full_project_list():
    n = len(ALL_PROJECTS)
    rows = "".join(
        f'<tr data-sector="{sec}"><td class="fl-year">{yrs}</td><td>{title}{f"<span class=\"fl-team\">Team of {MANPOWER[no]}</span>" if no in MANPOWER else ""}</td><td>{client}</td></tr>'
        for no, yrs, title, client, sec in reversed(ALL_PROJECTS))
    og = sum(1 for x in ALL_PROJECTS if x[4] == "og"); gov = n - og
    return f'''
    <details class="full-list" id="all-projects">
      <summary>View all {n} projects since 2003</summary>
      <div class="fl-tools">
        <label class="visually-hidden" for="fl-search">Search projects</label>
        <input id="fl-search" type="search" placeholder="Search by project or client, e.g. MLNG, pipeline, water" data-fl-search>
        <div class="filters" role="group" aria-label="Filter by sector" data-fl-filters>
          <button class="filter-btn" type="button" data-fl="all" aria-pressed="true">All<span class="count">({n})</span></button>
          <button class="filter-btn" type="button" data-fl="og" aria-pressed="false">Oil, gas &amp; petrochemical<span class="count">({og})</span></button>
          <button class="filter-btn" type="button" data-fl="gov" aria-pressed="false">Government &amp; infrastructure<span class="count">({gov})</span></button>
        </div>
      </div>
      <p class="visually-hidden" role="status" data-fl-status></p>
      <div class="fl-scroll">
        <table class="fl-table">
          <thead><tr><th scope="col">Years</th><th scope="col">Project</th><th scope="col">Client</th></tr></thead>
          <tbody data-fl-body data-fl-unit="projects|projek">{rows}</tbody>
        </table>
      </div>
      <p class="small mt-5 mb-0">From BWS’s work-experience record. Contract values are available to procurement teams on request.</p>
    </details>'''

def project_rows(items, compact=False):
    out = ""
    for years, client, name, loc, tags, _svc, ongoing in items:
        tag_html = "" if compact else '<ul class="proj-tags" role="list">' + "".join(f"<li>{t}</li>" for t in tags) + "</ul>"
        out += f'''
      <li class="proj">
        <span class="proj-years">{years}{'<span class="proj-status">Ongoing</span>' if ongoing else ''}</span>
        <div class="proj-main"><p class="proj-client">{client}</p><h3 class="proj-name">{name}</h3>{tag_html}</div>
        <span class="proj-loc">{icon("pin")}{loc}</span>
      </li>'''
    return out

# (name, logo file in assets/img/clients/, intrinsic width, height, note)
# Logos are the clients' current brand marks (PETRONAS subsidiaries use the group mark).
CLIENTS = [
    ("Malaysia LNG Sdn Bhd", "petronas.svg", 544, 558, "PETRONAS Group"),
    ("PETRONAS Carigali Sdn Bhd", "petronas.svg", 544, 558, ""),
    ("PETRONAS Dagangan Berhad", "petronas.svg", 544, 558, ""),
    ("PRPC Utilities &amp; Facilities Sdn Bhd", "petronas.svg", 544, 558, "RAPID, Pengerang"),
    ("Sarawak Shell Berhad", "shell.svg", 150, 139, ""),
    ("Sabah Shell Petroleum Co. Ltd", "shell.svg", 150, 139, ""),
    ("Shell MDS (Malaysia) Sdn Bhd", "shell.svg", 150, 139, ""),
    ("Samsung E&amp;A Co. Ltd", "samsung-ena.svg", 168, 21, ""),
    ("JGC (Malaysia) Sdn Bhd &amp; JGC SP (M) Sdn Bhd", "jgc.svg", 373, 202, ""),
    ("Chiyoda Malaysia Sdn Bhd", "chiyoda.svg", 201, 64, ""),
    ("JX Nippon Oil &amp; Gas Exploration (M) Ltd", "eneos-xplora.webp", 640, 91, "Now ENEOS Xplora"),
    ("PTTEP", "pttep.svg", 240, 212, "Bintulu Onshore Receiving Facility"),
    ("ASEAN Bintulu Fertilizer Sdn Bhd", "abf.webp", 150, 97, ""),
    ("PT Rekayasa Industri", "rekind.webp", 360, 404, "Rekind"),
    ("Mitsui &amp; Co. Ltd", "mitsui.svg", 512, 636, ""),
    ("Taihei Dengyo Kaisha, Ltd", "taihei-dengyo.webp", 122, 90, ""),
    ("Jabatan Kerja Raya (JKR)", "jkr.webp", 300, 222, "Public Works Department"),
    ("Ibu Pejabat Tanah dan Survei", None, 0, 0, "Land and Survey Department, Sarawak"),
]

def client_logo(logo, w, h, alt=""):
    if not logo:  # no published logo: clean text mark
        return f'<span class="client-textmark"{" role=\"img\" aria-label=\"" + alt + "\"" if alt else " aria-hidden=\"true\""}>Land &amp; Survey<small>Sarawak</small></span>'
    return f'<img src="assets/img/clients/{logo}" width="{w}" height="{h}" alt="{alt}" loading="lazy" decoding="async">'

def client_grid():
    # To change a logo: replace the file in assets/img/clients/ (keep the name) or edit the <img> below.
    lis = "".join(
        f'<li class="client"><span class="client-logo">{client_logo(logo, w, h)}</span>'
        f'<span class="client-name">{n}{f"<small>{note}</small>" if note else ""}</span></li>'
        for n, logo, w, h, note in CLIENTS)
    return f'<ul class="client-grid reveal-stagger" role="list">{lis}</ul>'

TRUST = f'''
<section class="trust on-dark" aria-label="Licences and credentials">
  <div class="container">
    <ul role="list">
      <li><div>PETRONAS Licensed<span>Valid PETRONAS licence</span></div></li>
      <li><div>CIDB Grade G7<span>Building · Civil · M&amp;E</span></div></li>
      <li><div>ISO 9001 · ISO 45001<span>TÜV NORD · BSI certified</span></div></li>
      <li><div>Est. 2002<span>Formed October 2002</span></div></li>
      <li><div>Bumiputera Company<span>Wholly owned · CIDB STB certified</span></div></li>
    </ul>
  </div>
</section>'''

# ================================================================ HOME
def home():
    svc_cards = "".join(f'''
      <a class="card card--media" href="services.html#{sid}">
        <div class="card-photo">{img(ph[0], "", ph[2], ph[3], "(min-width: 75rem) 25vw, (min-width: 40rem) 50vw, 100vw")}</div>
        <div class="card-body">
          
          <h3>{t}</h3>
          <p>{blurb}</p>
          <span class="link-arrow">View scope</span>
        </div>
      </a>''' for (sid, ic, t, blurb, _sc, _in, ph) in SERVICES)
    work = [("power-import-aerial-2", 686, 520, "Plant · MLNG", "Power Import Project, Bintulu"),
            ("miri-water-pipeline", 694, 441, "Civil &amp; Mechanical · JBALB", "Miri Water Supply, 1,600 mm pipeline"),
            ("rsp-housing-aerial-1", 679, 495, "Building · PPP", "50 houses, Gedong Baru, Samarahan"),
            ("miri-water-baram-intake", 632, 499, "Civil · JBALB", "Batang Baram intake works")]
    work_items = "".join(
        f'''
      <li><a class="work-item" href="projects.html">{img(k, t, w, h, "(min-width: 60rem) 25vw, 50vw")}<span class="cap"><span>{c}</span>{t}</span></a></li>'''
        for k, w, h, c, t in work)
    # One logo per brand in the scrolling strip (PETRONAS and Shell cover several client companies)
    brands = {}
    for n, logo, w, h, _ in CLIENTS:
        if not logo: continue  # text-only badges stay on the Clients page, not the logo wall
        key = logo
        if key in brands: brands[key][3].append(n)
        else: brands[key] = (logo, w, h, [n])
    def strip_logo(logo, w, h, names):
        # Exact display size per logo (44px tall, max 150px wide) so every browser lays the row out the same
        dw = min(150, round(44 * w / h)); dh = round(dw * h / w)
        return (f'<li style="--lw:{dw}px;--lh:{dh}px"><img src="assets/img/clients/{logo}" width="{dw}" height="{dh}" '
                f'alt="{", ".join(names)}" loading="lazy" decoding="async"></li>')
    marq = lambda alt: "".join(strip_logo(logo, w, h, names) for logo, w, h, names in brands.values())
    return head("index.html",
        "BWS Engineering Sdn Bhd | Oil &amp; Gas Construction &amp; Maintenance Contractor, Miri, Sarawak",
        "Bumiputera engineering construction and maintenance contractor for oil &amp; gas, based in Miri and Bintulu, Sarawak since 2002. PETRONAS licensed, CIDB registered, ISO 9001:2015 (TÜV NORD).") + header("index.html") + f'''
<section class="hero on-dark" aria-labelledby="hero-title">
  <div class="container hero-grid">
  <div class="hero-inner">
    <p class="eyebrow">Miri &amp; Bintulu, Sarawak</p>
    <h1 id="hero-title">Engineering, Construction &amp; Maintenance for Oil&nbsp;&amp;&nbsp;Gas, <span class="accent">Since&nbsp;2002.</span></h1>
    <p class="sub">Bumiputera contractor based in Miri &amp; Bintulu, Sarawak.</p>
    <div class="btn-row">
      <a class="btn btn--primary" href="services.html">Our Services {icon("arrow")}</a>
      <a class="btn btn--outline-light" href="contact.html">Contact Us</a>
    </div>
  </div>
  {panels("hero-column-erection", 1600, 1200, "(min-width: 60rem) 45vw, 100vw", alt="Crane lifting a process column into position during plant construction", cls="bws-panels--hero")}
  </div>
</section>
{TRUST}

<section class="stats-band" aria-labelledby="stats-title">
  <div class="container">
    <h2 id="stats-title" class="visually-hidden">BWS in numbers</h2>
    <!-- KEY STATS: edit the numbers here. data-count = the number, data-suffix = text after it.
         The number inside the tag is what shows without JavaScript, so keep both the same. -->
    <dl class="stats">
      <div class="stat"><dt class="stat-label">Years of experience</dt><dd class="stat-num" data-count="20" data-suffix="+">20+</dd><dd class="stat-note">Operating since October 2002</dd></div>
      <div class="stat"><dt class="stat-label">Operating bases</dt><dd class="stat-num" data-count="2">2</dd><dd class="stat-note">Miri &amp; Bintulu, Sarawak</dd></div>
      <div class="stat"><dt class="stat-label">Contracts delivered</dt><dd class="stat-num" data-count="80" data-suffix="+">80+</dd><dd class="stat-note">Oil &amp; gas, industry and government</dd></div>
      <div class="stat"><dt class="stat-label">Major clients</dt><dd class="stat-num" data-count="15" data-suffix="+">15+</dd><dd class="stat-note">Operators, EPC contractors and industry</dd></div>
    </dl>
  </div>
</section>

<section class="section" aria-labelledby="svc-title">
  <div class="container">
    <div class="section-head section-head--split">
      <div>{eyebrow("01", "Services")}<h2 id="svc-title">Integrated engineering and construction services</h2></div>
      <p class="lead">Construction and maintenance services for the oil and gas industries, from civil works and steel structures to mechanical, piping and E&amp;I.</p>
    </div>
    <div class="grid grid--4 reveal-stagger">{svc_cards}
    </div>
  </div>
</section>

<section class="section section--tint" aria-labelledby="about-title">
  <div class="container split split--wide-text">
    <div class="reveal">
      {eyebrow("02", "About BWS")}
      <h2 id="about-title">A wholly owned Bumiputera engineering contractor</h2>
      <p class="lead">Founded in October 2002 by Bumiputera professionals from the oil and gas industry, BWS has grown from minor plant maintenance in Miri into a Grade G7 contractor delivering complete EPCC packages.</p>
      <p>Supported by its own facilities in Miri and Bintulu, the company delivers engineering, construction and maintenance services to the oil and gas, power and public sectors across Malaysia.</p>
      <a class="btn btn--ghost mt-5" href="about.html">Read more about us {icon("arrow")}</a>
    </div>
    <figure class="media media--framed ratio-4x3 reveal">
      {img("mech-firepump-install", "BWS crew installing a diesel fire pump set on site", 706, 569)}
    </figure>
  </div>
</section>

<section class="section section--steel section--track" aria-labelledby="track-title">
  <div class="container">
    <div class="section-head section-head--split">
      <div>{eyebrow("", "Track record")}<h2 id="track-title">Current projects</h2></div>
      <p class="lead">More than 80 contracts since 2002, for oil and gas operators, EPC contractors and government agencies. <a href="projects.html#track">See key projects</a></p>
    </div>
    <ol class="proj-list reveal-stagger" role="list">{project_rows(PROJECTS[:4], compact=True)}
    </ol>
  </div>
</section>

<section class="section section--work" aria-labelledby="work-title">
  <div class="container">
    <div class="section-head section-head--split">
      <div>{eyebrow("", "On site")}<h2 id="work-title">Recent work</h2></div>
      <p class="lead">Plant, mechanical, civil and E&amp;I work across Sarawak. <a href="projects.html">View the full gallery</a></p>
    </div>
    <ul class="work-strip reveal-stagger" role="list">{work_items}
    </ul>
  </div>
</section>

<section class="section" aria-labelledby="clients-title">
  <div class="container">
    <div class="section-head section-head--split">
      <div>{eyebrow("03", "Clients")}<h2 id="clients-title">Trusted by operators and EPC contractors</h2></div>
      <p class="lead">Our main clients include national and international oil and gas operators, EPC contractors and industrial companies. <a href="clients.html">See all clients</a></p>
    </div>
  </div>
  <div class="marquee marquee--static" tabindex="0" aria-label="Main clients (scroll sideways for more)">
    <ul role="list" aria-label="Main clients">{marq(True)}</ul>
  </div>
</section>

<section class="section section--steel" aria-labelledby="fac-title">
  <div class="container">
    <div class="section-head section-head--split">
      <div>{eyebrow("04", "Facilities")}<h2 id="fac-title">Our own workshop and fabrication yard</h2></div>
      <p class="lead mb-0">Our main office and fabrication workshop is in Piasau Industrial Estate, Miri, with a fabrication yard at Kidurong, Bintulu. <a class="link-arrow" href="about.html#fac-title">See our facilities</a></p>
    </div>
    </div>
  </div>
</section>

<section class="hse-banner on-dark" aria-labelledby="hse-title">
  <div class="hero-media">{img("hse-smds-partnership", "", 1600, 1200, "100vw", big=True)}</div>
  <div class="container hse-banner-inner">
    <div class="reveal">
      {eyebrow("05", "Health, Safety &amp; Environment")}
      <h2 id="hse-title">Health, safety and environment come first</h2>
      <p>Every project is planned and executed under our HSE policy and an occupational health and safety management system certified to ISO 45001:2018.</p>
      <ul class="hse-mini" role="list"><li><strong>3 million</strong> man-hours without LTI on a single project</li><li><strong>15+</strong> HSE awards since 2005</li></ul>
      {hse_live("hse-live--dark")}
      <a class="btn btn--outline-light mt-5" href="hse.html#record">Our safety record {icon("arrow")}</a>
    </div>
    <blockquote class="safety-quote reveal">
      <span class="safety-tag">{icon("warn")} HSE Policy</span>
      <p>“No work shall commence or continue without ensuring a safe and healthy workplace and protection of the environment.”</p>
      <footer>BWS Engineering Sdn Bhd HSE Policy</footer>
    </blockquote>
  </div>
</section>
{CTA}''' + footer()

# ================================================================ ABOUT
# "Since 2002" timeline on the About page. Built only from facts already stated elsewhere on the site; the comment on
# each row says where. Each row: (datetime attribute, date label, text). Edit here, then regenerate.
TIMELINE = [
    # about.html "Who we are" and index.html: formed in October 2002 by Bumiputera from the oil and gas industry; Miri base
    ("2002-10", "Oct 2002", "Incorporated in Miri by Bumiputera professionals from the oil and gas industry"),
    # index.html "Licences": CIDB since 2003, Grade G7; ALL_PROJECTS no. 4 (2003 – 2005, turnkey, Sarawak Shell, Bintulu Integrated Facilities)
    ("2003", "2003", "Registered with CIDB at Grade G7; first turnkey contract, for Sarawak Shell’s Bintulu Integrated Facilities"),
    # index.html "PETRONAS & PETROS" card and hse.html PETRONAS licence card: licensed since 2004
    ("2004", "2004", "Licensed by PETRONAS"),
    # index.html "Licences": quality management certified by TÜV NORD since 2007
    ("2007", "2007", "ISO 9001 quality management certified by TÜV NORD"),
    # PROJECTS featured card "Teams of up to 150" (MCOT Rejuvenation Phase 2, PETRONAS Carigali); HSE_RECORD / awards: 3,000,000 man-hours without LTI, 2010
    ("2007", "2007 – 2011", "MCOT Rejuvenation Phase 2 for PETRONAS Carigali, with teams of up to 150; 3,000,000 man-hours without LTI (2010)"),
    # ALL_PROJECTS no. 42 and HSE_RECORD: EPCC of the PDB Miri Fuel Terminal, 2014 – 2015
    ("2014", "2014 – 2015", "EPCC of the PDB Miri Fuel Terminal"),
    # ALL_PROJECTS no. 68 and PROJECTS: EPCC of the Power Import Project for Malaysia LNG (Transgrid-BWS JV), 2022 – 2025
    ("2022", "2022 – 2025", "EPCC of the MLNG Power Import Project (Transgrid-BWS JV)"),
    # hse.html awards: National OSH Award, 2023
    ("2023", "2023", "National OSH Award"),
    # hse.html awards: PSIEA Silver Award, 2025; REG_CARDS: PETROS registered vendor (registered since 7 December 2025)
    ("2025", "2025", "PSIEA Silver Award; registered PETROS vendor"),
]

def about():
    return head("about.html", "About Us | BWS Engineering Sdn Bhd, Miri, Sarawak",
        "Company profile of BWS Engineering Sdn Bhd: a wholly owned Bumiputera oil &amp; gas construction and maintenance contractor formed in October 2002, with facilities in Miri and Bintulu.") + header("about.html") + page_hero(
        "About", "A Bumiputera contractor built on oil &amp; gas experience",
        "Engineering construction and maintenance services for the oil and gas industries since October 2002.",
        "workshop") + f'''

<section class="section" aria-labelledby="profile-title">
  <div class="container split split--wide-text">
    <div>
      {eyebrow("01", "Company profile")}
      <h2 id="profile-title">Who we are</h2>
      <p class="lead">BWS Engineering Sdn. Bhd. is a wholly owned Bumiputera company whose core business is engineering construction and maintenance services for the oil and gas industries.</p>
      <p>The company was formed in October 2002 by a group of Bumiputera with many years of experience in the oil and gas industry, particularly in construction and maintenance services.</p>
      <p>The company is run by its shareholders, who are members of the Board of Directors and Management. It also employs qualified professionals with thorough experience in various engineering and construction disciplines.</p>
      <p>BWS began with minor mechanical and civil works in oil and gas plants in Miri. It has since expanded its fabrication and civil capacity and added project management, so it can take on complete scopes covering procurement, construction and commissioning.</p>
    </div>
    <div>
      <dl class="facts reveal-stagger">
        <div><dt>Incorporated</dt><dd>29 October 2002</dd></div>
        <div><dt>Company no.</dt><dd>200201029529 (597192-V)</dd></div>
        <div><dt>Ownership</dt><dd>100% Bumiputera</dd></div>
        <div><dt>Paid-up capital</dt><dd>RM5,000,000</dd></div>
        <div><dt>Bases</dt><dd>Miri &amp; Bintulu, Sarawak</dd></div>
        <div><dt>Certified</dt><dd>ISO 9001:2015 · ISO 45001:2018</dd></div>
        <div><dt>Licensing</dt><dd>PETRONAS · PETROS · CIDB G7</dd></div>
      </dl>
    </div>
  </div>
</section>

<section class="section section--steel" aria-labelledby="history-title">
  <div class="container">
    <div class="section-head">
      {eyebrow("02", "Our history")}
      <h2 id="history-title">Since 2002</h2>
    </div>
    <ol class="timeline">{"".join(f'<li class="timeline-item"><time datetime="{dt}">{label}</time><p>{text}</p></li>' for dt, label, text in TIMELINE)}</ol>
  </div>
</section>

<section class="section section--ink" aria-labelledby="obj-title">
  <div class="container measure center" style="margin-inline:auto">
    {eyebrow("02", "Our objective").replace('class="eyebrow"', 'class="eyebrow" style="justify-content:center"')}
    <h2 id="obj-title" class="visually-hidden">Our objective</h2>
    <p style="font-family:var(--font-head);font-size:clamp(1.5rem,1.2rem + 1.6vw,2.5rem);line-height:1.25;color:#fff;margin:0">“Become one of the major contractors in the construction industry.”</p>
  </div>
</section>

<section class="section section--steel" aria-labelledby="fac-title">
  <div class="container">
    <div class="section-head">
      {eyebrow("03", "Facilities")}
      <h2 id="fac-title">Miri headquarters and Bintulu fabrication yard</h2>
    </div>
    <div class="grid grid--2">
      <article class="facility">
        {img("facility-miri-hq", "BWS Engineering main office and workshop building at Piasau Industrial Estate, Miri", 800, 600, "(min-width: 60rem) 50vw, 100vw", big=True)}
        <div class="facility-body">
          <span class="tag">Miri · Main Office</span>
          <h3>Piasau Industrial Estate</h3>
          <p class="mb-0">The company owns an industrial building at Piasau Industrial Estate, Miri, which serves as its main office, warehouse and fabrication workshop for civil, building, structural, mechanical, piping, and electrical &amp; instrumentation construction and maintenance work.</p>
        </div>
      </article>
      <article class="facility">
        {img("facility-bintulu-yard", "Entrance to the BWS Engineering fabrication yard at Kidurong Industrial Estate, Bintulu", 800, 800, "(min-width: 60rem) 50vw, 100vw", big=True)}
        <div class="facility-body">
          <span class="tag">Bintulu · Fabrication Yard</span>
          <h3>Kidurong Industrial Estate</h3>
          <p>In Bintulu, the company has a fabrication yard at Kidurong Industrial Estate, equipped with:</p>
          <ul class="ticks mb-0">
            <li>Offices</li><li>A covered fabrication shop</li><li>An open fabrication area</li>
            <li>Covered and open storage</li><li>Blasting and painting facilities</li><li>NDT facilities</li>
          </ul>
        </div>
      </article>
    </div>
  </div>
</section>

<section class="section" aria-labelledby="org-title">
  <div class="container">
    <div class="section-head">
      <div>{eyebrow("04", "Organisation")}<h2 id="org-title">Organisation chart</h2></div>
    </div>
    <!-- BOARD OF DIRECTORS: as listed in the BWS Company Profile (page 5). -->
    <h3 class="org-subtitle org-subtitle--first" id="board-title">Board of Directors</h3>
    <table class="board-table" aria-labelledby="board-title">
      <thead><tr><th scope="col">Position</th><th scope="col">Name</th></tr></thead>
      <tbody>
        <tr><td>Managing Director</td><td>Bundan Anak Ngila</td></tr>
        <tr><td>Executive / Project Director</td><td>Fabian Anak Raymond Langin</td></tr>
        <tr><td>Executive / Project Director / HSE Manager</td><td>Martin Jau</td></tr>
        <tr><td>Executive Director / Personnel &amp; Administration Manager</td><td>Mazinah binti Mohd. Masri</td></tr>
        <tr><td>Executive Director / Accounts Manager</td><td>Salmah binti Ahmad</td></tr>
      </tbody>
    </table>

    <h3 class="org-subtitle" id="corg-title">Company organisation</h3>
    <!-- ORGANISATION CHARTS: structure and names from the BWS Company Profile (updated 10.26).
         Update names here (or in tools/generate_site.py) when staff change. -->
    <figure class="org" aria-labelledby="corg-title">
      <div class="org-top">
        <div class="org-node org-node--lead">Managing Director<span class="org-person">Bundan Anak Ngila</span></div>
        <div class="org-staff"><span class="org-staff-line" aria-hidden="true"></span><div class="org-node org-node--staff">HSE Secretary<span class="org-person">Dominic Saga</span><span class="org-person org-reg">HQ/16/SHO/04/00830</span></div></div>
      </div>
      <ul class="org-sections" role="list">
        <li><ol class="org-chain"><li class="org-node org-node--section">Personnel &amp; Administration Section</li><li class="org-node">Personnel &amp; Administration Manager<span class="org-person">Mazinah Bt Mohd Masri</span></li><li class="org-node">Administration Support</li><li class="org-split"><span class="org-node org-node--leaf">Miri Office<span class="org-person">Siti Yasmeen</span><span class="org-person">Mary Maja</span></span><span class="org-node org-node--leaf">Bintulu Office<span class="org-person">Umah @ Timah</span></span></li></ol></li>
        <li><ol class="org-chain"><li class="org-node org-node--section">Account Section</li><li class="org-node">Accounts Manager<span class="org-person">Salmah Ahmad</span></li><li class="org-node">Accounts Assistants<span class="org-person">Stacy Ganin</span><span class="org-person">Francisca</span></li></ol></li>
        <li><ol class="org-chain"><li class="org-node org-node--section">Engineering / Contract Section</li><li class="org-split org-split--sub"><ol class="org-chain"><li class="org-node">Engineering / Project Section</li><li class="org-node">Project Manager<span class="org-person">Fabian Raymond Langin</span></li><li class="org-node org-node--leaf">Project Team</li></ol><ol class="org-chain"><li class="org-node">Contract / Procurement Section</li><li class="org-node">Contract Manager<span class="org-person">Mohd Qhadaffie Siew</span></li><li class="org-node org-node--leaf">Procurement<span class="org-person">Kasfalela Manja</span><span class="org-person">Hafizah Bt Mohedin</span></li></ol></li></ol></li>
        <li><ol class="org-chain"><li class="org-node org-node--section">Quality Assurance Section</li><li class="org-node">Quality Management Representative (QMR)<span class="org-person">Martin Jau</span></li></ol></li>
        <li><ol class="org-chain"><li class="org-node org-node--section org-node--hse">Health, Safety &amp; Environment (HSE) Section</li><li class="org-node">HSE Officer<span class="org-person">Dominic Saga</span><span class="org-person org-reg">HQ/16/SHO/04/00830</span></li><li class="org-split"><span class="org-node org-node--leaf">Site Safety Supervisor<span class="org-person">Yvonne Ilam Anak James</span><span class="org-person org-reg">HQ/22/SSS/00/20471</span><span class="org-person">Esther Annie</span><span class="org-person org-reg">SW/24/SSS/00/00141</span></span><span class="org-node org-node--leaf">HSE Committee</span></li></ol></li>
      </ul>
    </figure>

    <h3 class="org-subtitle" id="porg-title">Project organisation</h3>
    <p class="small">How BWS staffs a typical project.</p>
    <figure class="org org--project" aria-labelledby="porg-title">
      <div class="org-top"><div class="org-node org-node--lead">Project Manager<span class="org-person">Fabian Raymond Langin</span></div></div>
      <ul class="org-sections" role="list" style="--cols: 6">
        <li><ol class="org-chain"><li class="org-node org-node--section">Engineering Design</li><li class="org-node org-node--leaf">Consultant</li></ol></li>
        <li><ol class="org-chain"><li class="org-node org-node--section">Quantity Surveyor<span class="org-person">Nur Zukrina</span></li><li class="org-node">Material Coordinator<span class="org-person">Kunjan Tipong</span></li></ol></li>
        <li><ol class="org-chain"><li class="org-node org-node--section">Planning &amp; Measurement Engineer<span class="org-person">Nurhaziqah</span><span class="org-person">Vallery Ramlee</span></li><li class="org-node">Document Controller<span class="org-person">Assa Adenna</span></li></ol></li>
        <li><ol class="org-chain"><li class="org-node org-node--section">Construction Superintendent<span class="org-person">Chia Shuck Ping</span></li><li class="org-node">Construction Engineer<span class="org-person">Paul Yeo Ing Ming</span><span class="org-person">Nur Aida Bt Ali</span></li></ol></li>
        <li><ol class="org-chain"><li class="org-node org-node--section">QA/QC Engineer<span class="org-person">Roland bin Andrew</span></li><li class="org-node">QA/QC Inspector<span class="org-person">Sylvester Linang</span><span class="org-person">Hamka bin Aslan</span></li></ol></li>
        <li><ol class="org-chain"><li class="org-node org-node--section org-node--hse">HSE Manager<span class="org-person">Dominic Saga</span><span class="org-person org-reg">HQ/16/SHO/04/00830</span></li><li class="org-node">Site Safety Supervisor<span class="org-person">Joshua Emang</span><span class="org-person org-reg">HQ/14/SSS/00/0648</span><span class="org-person">Azumanor Ahmad Majid</span><span class="org-person org-reg">HQ/14/SSS/00/0685</span><span class="org-person">Dennis Bengau</span><span class="org-person org-reg">SW/24/SSS/00/00135</span></li></ol></li>
      </ul>
    </figure>
    <p class="org-caption">Site construction, under the Construction Engineer</p>
    <figure class="org org--teams" aria-label="Construction teams under the Construction Supervisor">
      <div class="org-top"><div class="org-node">Construction Supervisor<span class="org-person">Roysten Alyster</span></div></div>
      <ul class="org-sections" role="list" style="--cols: 3">
        <li><ol class="org-chain"><li class="org-node org-node--section">Civil &amp; Structural Team</li><li class="org-node">C&amp;S Supervisor<span class="org-person">Chung Tech Poh</span></li></ol></li>
        <li><ol class="org-chain"><li class="org-node org-node--section">Mechanical &amp; Piping Team</li></ol></li>
        <li><ol class="org-chain"><li class="org-node org-node--section">Electrical &amp; Instrumentation Team</li></ol></li>
      </ul>
    </figure>
  </div>
</section>

<section class="section section--tint" aria-labelledby="lic-title">
  <div class="container">
    <div class="section-head">{eyebrow("05", "Licences &amp; certification")}<h2 id="lic-title">Licensed, registered and certified</h2></div>
    <div class="grid grid--3 reveal-stagger">
      <div class="card"><h3>PETRONAS &amp; PETROS</h3><p class="mb-0">PETRONAS licensed since 2004 for onshore pipeline, fabrication, inspection and repair work, and a registered vendor of Petroleum Sarawak (PETROS).</p></div>
      <div class="card"><h3>CIDB Grade G7</h3><p class="mb-0">Registered with CIDB since 2003 at Grade G7, the highest grade, in Building, Civil Engineering and Mechanical &amp; Electrical. Registration no. 0120030415-SR082502. <a href="hse.html#cert-title">Details</a></p></div>
      <div class="card"><h3>ISO 9001 &amp; ISO 45001</h3><p class="mb-0">Quality management certified by TÜV NORD since 2007, and occupational health &amp; safety management certified by BSI since 2024. <a href="hse.html#quality">Details</a></p></div>
    </div>
  </div>
</section>
{CTA}''' + footer()

# ================================================================ SERVICES
from equipment import EQUIPMENT, GROUPS as EQUIP_GROUPS

def equipment_register():
    n = sum(len(items) for _g, _c, items in EQUIPMENT)
    cnt = lambda g: sum(len(items) for gg, _c, items in EQUIPMENT if gg == g)
    rows = "".join(
        f'<tr data-sector="{g}"><td>{cat}</td><td>{desc}</td><td class="eq-cap">{cap or "–"}</td><td class="eq-units">{units:,}</td></tr>'
        for g, cat, items in EQUIPMENT for desc, cap, units in items)
    btns = "".join(f'<button class="filter-btn" type="button" data-fl="{k}" aria-pressed="false">{v}<span class="count">({cnt(k)})</span></button>' for k, v in EQUIP_GROUPS)
    return f'''
    <details class="full-list full-list--dark" id="equipment-register">
      <summary>View the full equipment register ({n} items)</summary>
      <div class="fl-tools">
        <label class="visually-hidden" for="eq-search">Search equipment</label>
        <input id="eq-search" type="search" placeholder="Search, e.g. crane, Wachs, generator, 36" data-fl-search>
        <div class="filters" role="group" aria-label="Filter by type" data-fl-filters>
          <button class="filter-btn" type="button" data-fl="all" aria-pressed="true">All<span class="count">({n})</span></button>{btns}
        </div>
      </div>
      <p class="visually-hidden" role="status" data-fl-status></p>
      <div class="fl-scroll">
        <table class="fl-table eq-table">
          <thead><tr><th scope="col">Type</th><th scope="col">Item</th><th scope="col">Capacity</th><th scope="col">Units</th></tr></thead>
          <tbody data-fl-body data-fl-unit="items|item">{rows}</tbody>
        </table>
      </div>
      <p class="small mt-5 mb-0">From the BWS equipment list, October 2026. Availability for a particular project is confirmed at tender stage.</p>
    </details>'''

def services():
    nav = "".join(f'<li><a href="#{sid}">{t}</a></li>' for sid, _i, t, *_ in SERVICES)
    secs = ""
    for i, (sid, ic, t, blurb, scope, intro, photo) in enumerate(SERVICES, 1):
        key, alt, w, h = photo
        scope_li = "".join(f"<li>{s}</li>" for s in scope)
        rel = [p for p in PROJECTS if p[5][0] == sid][:5]
        related_html = ("" if not rel else
            '<div class="related"><h3 class="related-title">Selected projects</h3><ul class="related-list" role="list">'
            + "".join(f'<li><span>{p[0]}</span>{p[2]} <em>· {p[1]}</em></li>' for p in rel) + '</ul><a class="link-arrow" href="projects.html#track">All key projects</a></div>')
        secs += f'''
<section class="service" id="{sid}" aria-labelledby="{sid}-title">
  <div class="container service-grid">
    <div>
      <div class="service-head"><h2 id="{sid}-title">{t}</h2></div>
      <p class="lead">{intro}</p>
      <h3 class="visually-hidden">Scope</h3>
      <ul class="scope reveal-stagger" role="list">{scope_li}</ul>
      {related_html}
      <a class="btn btn--primary" href="contact.html?service={sid}#enquiry">Discuss your project {icon("arrow")}<span class="visually-hidden">: {t}</span></a>
    </div>
    <figure class="media ratio-4x3 reveal">
      {img(key, alt, w, h)}
    </figure>
  </div>
</section>'''
    return head("services.html", "Services | Plant, Mechanical, Civil &amp; E&amp;I Works | BWS Engineering",
        "Industrial plant construction and maintenance, mechanical and piping, civil, building and structural steel, and electrical and instrumentation work for oil &amp; gas in Sarawak.") + header("services.html") + page_hero(
        "Services", "Construction &amp; maintenance services for oil and gas",
        "Four core disciplines delivered from our Miri workshop and Bintulu fabrication yard, with project management covering procurement, construction and commissioning.",
        "plant") + f'''
<nav class="service-nav" aria-label="Services on this page"><div class="container"><ul>{nav}<li><a href="#equipment">Plant &amp; equipment</a></li></ul></div></nav>
{secs}
<section class="section section--ink" id="equipment" aria-labelledby="equip-title">
  <div class="container">
    <div class="section-head section-head--split">
      <div>{eyebrow("", "Plant &amp; equipment")}<h2 id="equip-title">Company-owned plant and equipment</h2></div>
      <p class="lead">BWS maintains its own lifting, welding, cutting and testing equipment, reducing reliance on third-party hire. Principal items include:</p>
    </div>
    <!-- EQUIPMENT: summarised from the BWS Company Profile equipment list (Oct 2026). -->
    <ul class="equip-grid reveal-stagger" role="list">
      <li><span class="equip-num">13</span><h3>Cranes, 25 to 120 tonnes</h3><p>Rough-terrain, mobile and a 120-tonne all-terrain crane, plus forklifts up to 10 tonnes, lorry trailers and a prime mover.</p></li>
      <li><span class="equip-num">50+</span><h3>Welding sets</h3><p>Lincoln and Miller welding machines, diesel welding generators, inverters and electrode baking ovens.</p></li>
      <li><span class="equip-num">8–36″</span><h3>Pipe cutting &amp; bevelling</h3><p>Wachs pneumatic cold-cutting and bevelling machines, Koike automatic pipe cutters, pipe benders and threading machines.</p></li>
      <li><span class="equip-num">5,000 psi</span><h3>Testing &amp; torque</h3><p>Hydrostatic pumps and pressure recorders, hydraulic torque tooling, and multi-gas and single-gas detectors.</p></li>
      <li><span class="equip-num">150 kVA</span><h3>Power &amp; lighting</h3><p>Diesel generators up to 150 kVA and mobile lighting towers for night work.</p></li>
      <li><span class="equip-num">BS 1139</span><h3>Earthworks &amp; access</h3><p>Excavators, backhoe, surveying instruments and a large stock of BS 1139 scaffolding.</p></li>
    </ul>
    <!-- EQUIPMENT REGISTER: edit tools/equipment.py -->
    {equipment_register()}
  </div>
</section>
{CTA}''' + footer()

# ================================================================ CLIENTS
def clients():
    return head("clients.html", "Clients | BWS Engineering Sdn Bhd",
        "BWS Engineering’s main clients include Malaysia LNG, PETRONAS Carigali, PETRONAS Dagangan, Sarawak Shell, JGC, Chiyoda and other oil &amp; gas operators and EPC contractors.") + header("clients.html") + page_hero(
        "Clients", "Our main clients",
        "Oil and gas operators, EPC contractors and industrial companies have trusted BWS with construction and maintenance work since 2002.",
        "offshore") + f'''

<section class="section" aria-labelledby="cl-title">
  <div class="container">
    <div class="section-head">
      <div>{eyebrow("01", "Clients")}<h2 id="cl-title">Client list</h2></div>
    </div>
    {client_grid()}
  </div>
</section>

<section class="section section--steel" aria-labelledby="why-title">
  <div class="container">
    <div class="section-head">{eyebrow("02", "Our commitment")}<h2 id="why-title">What clients can expect</h2></div>
    <div class="grid grid--3 reveal-stagger">
      <div class="card"><h3>Safety first</h3><p class="mb-0">An occupational health and safety management system certified to ISO 45001:2018, applied on every site.</p></div>
      <div class="card"><h3>Certified quality</h3><p class="mb-0">An ISO 9001:2015 Quality Management System, certified by TÜV NORD and continually improved.</p></div>
      <div class="card"><h3>Company-owned facilities</h3><p class="mb-0">A workshop in Miri and a fabrication yard with blasting, painting and NDT facilities in Bintulu.</p></div>
    </div>
  </div>
</section>
{CTA}''' + footer()

# ================================================================ PROJECTS
GALLERY = [
    ("plant", "power-import-aerial-1", 675, 520, "Power Import Project, MLNG", "Aerial view of the new power import buildings under construction at the MLNG complex"),
    ("plant", "power-import-aerial-2", 686, 520, "Power Import Project, MLNG", "Aerial view of the power import facility buildings and pipe racks"),
    ("civil", "rsp-housing-aerial-1", 679, 495, "50 houses, Gedong Baru, Samarahan", "Aerial view of the Rumah Spektra Permata housing scheme under construction"),
    ("civil", "rsp-housing-aerial-2", 592, 463, "Rumah Spektra Permata houses", "Completed and in-progress two-storey houses at the Gedong Baru housing scheme"),
    ("civil", "miri-water-pipeline", 694, 441, "Miri Water Supply: DN1600 pipeline", "A 1,600 mm water pipeline running in a straight line through a plantation"),
    ("civil", "miri-water-baram-intake", 632, 499, "Batang Baram intake", "Aerial view of the Batang Baram intake structure under construction"),
    ("mech", "miri-water-submarine-pipes", 474, 447, "Launching twin 1.2 m submarine pipes", "Twin 1.2 m pipes being launched into the river from a steel frame"),
    ("mech", "pipeline-joint-hillside", 507, 380, "Pipeline installation", "Workers in PPE joining a large pipeline on a cleared hillside"),
    ("plant", "plant-bullet-vessels", 325, 337, "LPG bullet vessels", "Row of white horizontal pressure vessels on concrete saddles inside a process plant"),
    ("plant", "plant-pipe-rack", 361, 333, "Pipe rack and steel structures", "Steel pipe rack and structures at an onshore facility under a blue sky"),
    ("plant", "plant-tank-scaffold", 384, 295, "Tank construction", "Large storage tank wrapped in scaffolding during construction"),
    ("mech", "mech-firepump-install", 706, 569, "Fire pump set installation", "Crew in coveralls and hard hats installing a red diesel fire pump set on its plinth"),
    ("mech", "mech-vessel-lift-crew", 346, 334, "Vessel lift with the rigging crew", "Rigging crew guiding a pressure vessel lifted by crane inside a plant"),
    ("hse", "hse-smds-partnership", 800, 600, "SMDS HSSE Partnership 2026", "BWS team at the Shell MDS HSSE Partnership 2026 event"),
    ("hse", "award-psiea", 369, 328, "PSIEA 2025 award ceremony", "BWS receiving the Premier of Sarawak Industry Excellence Award on stage"),
    ("plant", "project-shelter", 445, 333, "Shelter structure at an onshore facility", "Steel-framed shelter with a roof canopy beside a process facility"),
    ("hse", "pdb-team", 465, 315, "Project team at a PETRONAS Dagangan site", "Project team in coveralls and hard hats gathered at a PETRONAS Dagangan site"),
    ("hse", "miri-water-team", 710, 447, "Project team, Miri Water Supply", "Project team in hi-vis vests and hard hats beside a large pipeline"),
    ("hse", "award-msosh-gold", 523, 367, "MSOSH Gold Class 1 Award", "Award ceremony on stage for the MSOSH Gold Class 1 Award, Power Import Project for MLNG"),
    ("hse", "award-46m-safe-manhours", 466, 311, "46 million safe man-hours", "BWS representatives receiving recognition for contributions to 46 million safe man-hours"),
    # (category, image key, w, h, title, alt) or (category, None, ..., placeholder text)
    ("plant", "hero-column-erection", 800, 600, "Process column erection", "Crane lifting a process column into position inside its scaffolding"),
    ("plant", "plant-tanks-piping", 800, 468, "Storage tanks and piping", "White storage tanks with yellow piping and access stairways"),
    ("plant", "plant-firewater-tank", 800, 473, "Firewater tank and pump shelter", "Firewater tank and green-roofed pump shelter at a facility"),
    ("mech", "mech-heavy-lift", 800, 600, "Heavy lift of a vessel", "Mobile crane lifting a large cylindrical vessel on site"),
    ("mech", "mech-pump-skid", 448, 292, "Pump installation", "Electric pump and pipework installed on a skid"),
    ("mech", "piping-spool", 448, 295, "Large-bore piping", "Large-bore white piping with flanged connections"),
    ("mech", "mech-container-unloading", 800, 487, "Material receiving", "Crew in PPE unloading materials from a shipping container"),
    ("civil", "civil-rebar", 800, 460, "Foundation reinforcement", "Construction crew tying reinforcement steel for a foundation"),
    ("civil", "civil-foundation-slab", 800, 488, "Concrete foundation slab", "Large concrete slab with formwork and an excavator at the edge of the site"),
    ("civil", "civil-excavation-formwork", 800, 563, "Excavation and formwork", "Excavator working beside timber formwork in an excavation"),
    ("civil", "civil-concrete-finishing", 800, 481, "Concrete finishing", "Workers in coveralls and boots finishing a concrete surface"),
    ("civil", "civil-drainage", 640, 480, "Drainage works", "Drainage channel under construction along a slope"),
    ("civil", "building-scaffold", 800, 600, "Building construction", "Two-storey building wrapped in scaffolding beside a container yard"),
    ("civil", "building-interior", 800, 534, "Building fit-out", "Interior of a building under fit-out with steel roof structure"),
    ("ei", "ei-switchgear", 800, 599, "Switchgear installation", "Row of electrical switchgear panels in a substation room"),
    ("hse", "hse-toolbox-talk", 800, 600, "Toolbox talk", "Workers seated under a site tent for a safety briefing"),
    ("hse", "hse-site-walk", 577, 564, "Site inspection", "Supervisors in hard hats walking a cleared site"),
    ("hse", "hse-fire-drill", 800, 600, "Fire extinguisher drill", "Crew in coveralls and hard hats during a fire extinguisher drill"),
]
CATS = [("all", "All"), ("plant", "Plant"), ("mech", "Mechanical &amp; Piping"), ("civil", "Civil &amp; Structural"),
        ("ei", "Electrical &amp; Instrumentation"), ("hse", "HSE")]
CATNAME = dict(CATS)

# ================================================================ CASE STUDIES (Projects page)
# From the BWS Company Profile (Oct 2026): work-experience entries for scope and dates, and the client
# certificates for results. Contract sums and client contact names are deliberately left out.
# photo: (image key, width, height, alt). Only projects with an official photo (from BWS's profile or old website) are featured.
CASE_STUDIES = [
    {"id": "case-power-import", "client": "Malaysia LNG", "years": "2022 – 2025", "where": "Bintulu, Sarawak",
     "title": "EPCC of the Power Import Project for MLNG",
     "summary": "A joint venture between Transgrid Ventures Sdn Bhd and BWS Engineering, delivering new power import facilities at the PETRONAS LNG Complex from design through to handover.",
     "scope": ["Management, administration and detailed design engineering",
               "Site preparation, earthworks, procurement, storage and preservation",
               "Construction, equipment installation, testing and pre-commissioning",
               "Tie-ins and modifications of piping and cables to the existing facilities",
               "Commissioning, start-up and handover"],
     "results": ["MSOSH Gold Class 1 Award for very good OSH performance in 2023"],
     "photo": ("power-import-aerial-2", 686, 520, "Aerial view of the power import facility buildings and pipe racks")},
    {"id": "case-miri-water", "client": "Rural Water Supply Department (JBALB) Sarawak", "years": "2019 – 2025", "where": "Miri, Sarawak",
     "title": "Miri Water Supply Source Development Phase 2",
     "summary": "Part of the Sarawak Water Grid Programme: transferring raw water from Batang Baram to Sungai Bakong and Sungai Liku, to meet the demand of Miri city and its surroundings up to 2030.",
     "scope": ["Earthworks and infrastructure, including the service road",
               "1,600 mm diameter raw water pipeline, including twin 1.2 m submarine pipes",
               "Pumping station, guard house and genset house",
               "High-tension line and mechanical and electrical works"],
     "results": [],
     "photo": ("miri-water-baram-intake", 632, 499, "Aerial view of the Batang Baram intake structure under construction")},
    {"id": "case-pdb", "client": "PETRONAS Dagangan", "years": "2014 – 2015", "where": "Miri, Sarawak",
     "title": "EPCC of the PDB Miri Fuel Terminal",
     "summary": "Engineering, procurement, construction and commissioning of new facilities at the PETRONAS Dagangan fuel terminal in Miri, with a team of about 60.",
     "scope": ["Administration building, MSB room and substation, and other civil and structural work",
               "Fabrication and erection of tanks and accessories",
               "Firefighting facilities and other mechanical and electrical work"],
     "results": ["150,000 man-hours without lost-time injury (PETRONAS Dagangan certificates at 30,000 and 150,000 man-hours, 2015)"],
     "photo": ("pdb-team", 465, 315, "Project team in coveralls and hard hats gathered at a PETRONAS Dagangan site")},
]

def case_studies():
    out = ""
    for i, c in enumerate(CASE_STUDIES):
        key, w, h, alt = c["photo"]
        media = img(key, alt, w, h, "(min-width: 60rem) 40vw, 100vw")
        scope = "".join(f"<li>{x}</li>" for x in c["scope"])
        results = ("<h4>Results</h4><ul class=\"case-results\">" + "".join(f"<li>{icon('badge')}<span>{x}</span></li>" for x in c["results"]) + "</ul>") if c["results"] else ""
        out += f'''
      <article class="case{" case--flip" if i % 2 else ""}" id="{c["id"]}" aria-labelledby="{c["id"]}-title">
        <div class="case-media">{media}</div>
        <div class="case-body">
          <p class="case-meta">{c["client"]} · {c["years"]} · {c["where"]}</p>
          <h3 id="{c["id"]}-title">{c["title"]}</h3>
          <p>{c["summary"]}</p>
          <h4>Scope</h4><ul>{scope}</ul>
          {results}
        </div>
      </article>'''
    return out

def projects():
    # Photos already shown in the case studies above are left out of the gallery on this page
    case_keys = {c["photo"][0] for c in CASE_STUDIES}
    shown = [g for g in GALLERY if g[1] not in case_keys]
    cnt = lambda k: len(shown) if k == "all" else sum(1 for g in shown if g[0] == k)
    btns = "".join(f'<button class="filter-btn" type="button" data-filter="{k}" aria-pressed="{str(k == "all").lower()}">{v}<span class="count">({cnt(k)})</span></button>' for k, v in CATS)
    lis = ""
    for cat, key, w, h, title, alt in shown:
        if key and key.startswith("ill:"):
            # Blueprint illustration standing in until a real site photo is supplied (see README)
            src = f"assets/illustrations/{key[4:]}.svg"
            lis += f'''
      <li data-cat="{cat}"><button type="button" data-full="{src}" data-title="{title} (illustration)" aria-label="Illustration {title} (enlarge)">
        <img src="{src}" width="800" height="600" alt="{alt}" loading="lazy" decoding="async">
        <span class="cap" aria-hidden="true"><span>Illustration</span>{title}</span></button></li>'''
        elif key:
            big = os.path.exists(OUT + f"assets/img/{key}-1600.webp")
            full = f"assets/img/{key}-{'1600' if big else '800'}.webp"
            lis += f'''
      <li data-cat="{cat}"><button type="button" data-full="{full}" data-title="{title}" aria-label="{CATNAME[cat]} {title} (enlarge photo)">
        {img(key, alt, w, h, "(min-width: 75rem) 25vw, (min-width: 40rem) 50vw, 100vw")}
        <span class="cap" aria-hidden="true"><span>{CATNAME[cat]}</span>{title}</span></button></li>'''
        else:
            lis += f'\n      <li data-cat="{cat}">{ph(alt)}</li>'
    return head("projects.html", "Projects &amp; Gallery | BWS Engineering Sdn Bhd",
        "Photos of BWS Engineering’s plant construction, mechanical and piping, civil and structural, electrical and instrumentation, and HSE activities in Sarawak.") + header("projects.html") + page_hero(
        "Projects", "Projects &amp; gallery",
        "A look at our work on site, filtered by discipline.",
        "crane-lift") + f'''

<section class="section" id="case-studies" aria-labelledby="cases-title">
  <div class="container">
    <div class="section-head section-head--split">
      <div>{eyebrow("", "Case studies")}<h2 id="cases-title">Featured projects</h2></div>
      <p class="lead">A closer look at three projects: what we were asked to do, and the results our clients recorded.</p>
    </div>
    <!-- CASE STUDIES: edit CASE_STUDIES in tools/generate_site.py. Results must be backed by a client certificate or letter. -->
    <div class="cases">{case_studies()}
    </div>
  </div>
</section>

<section class="section section--steel" id="track" aria-labelledby="track-title">
  <div class="container">
    <div class="section-head section-head--split">
      <div>{eyebrow("", "Track record")}<h2 id="track-title">Key projects</h2></div>
      <p class="lead">Selected from more than 80 contracts delivered since 2002 for oil and gas operators, EPC contractors and government agencies across Malaysia.</p>
    </div>
    <!-- KEY PROJECTS: edit the PROJECTS list in tools/generate_site.py, or edit the <li class="proj"> items below. -->
    <ol class="proj-list" role="list">{project_rows(PROJECTS)}
    </ol>
    {full_project_list()}
  </div>
</section>

<section class="section" aria-labelledby="gal-title">
  <div class="container">
    <h2 id="gal-title" class="visually-hidden">Photo gallery</h2>
    <!-- GALLERY: each <li data-cat="..."> is one photo. Categories: plant, mech, civil, ei, hse.
         Copy an existing <li>, change the image file names, data-title and alt text. -->
    <div class="filters" data-filters role="group" aria-label="Filter photos by discipline">{btns}</div>
    <p class="visually-hidden" role="status" data-gallery-status></p>
    <ul class="gallery" data-gallery role="list">{lis}
    </ul>
  </div>
</section>

<dialog class="lightbox" id="lightbox" aria-label="Photo viewer">
  <figure>
    <div class="lightbox-stage">
      <div class="loader" aria-hidden="true"><span class="panels"><i></i><i></i><i></i></span></div>
      <img src="data:," alt="">
      <button class="lb-btn lb-prev" type="button">{icon("left")}<span class="visually-hidden">Previous photo</span></button>
      <button class="lb-btn lb-next" type="button">{icon("right")}<span class="visually-hidden">Next photo</span></button>
      <button class="lb-btn lb-close" type="button">{icon("close")}<span class="visually-hidden">Close</span></button>
    </div>
    <figcaption><strong data-lb-title></strong><span data-lb-count></span></figcaption>
  </figure>
</dialog>
{CTA}''' + footer()

# ================================================================ HSE
# Documented HSE milestones: each one is backed by a certificate or letter in the BWS Company Profile (Oct 2026).
HSE_RECORD = [
    ("3,000,000", "man-hours without lost-time injury", "MCOT Rejuvenation Project Phase 2, 2010"),
    ("400,000", "exposure hours without lost-time injury", "Civil and mechanical teams, SMDS Rejuvenation Project, 2015"),
    ("150,000", "man-hours without lost-time injury", "EPCC of the PDB Miri Fuel Terminal, 2015"),
    ("Zero LTI", "and 25 days ahead of schedule", "SSGP KP265 recovery works for PETRONAS, 2020"),
    ("Grade A", "DOSH workplace inspection", "Bintulu fabrication yard, score 92, 2021"),
    ("15+", "HSE awards and recognitions", "From clients, industry bodies and government since 2005"),
]

def hse_live(cls=""):
    """Latest HSE figures, published by BWS in the portal (HSE figures) and filled in by main.js; hidden until then."""
    c = f" {cls}" if cls else ""
    return (f'<div class="hse-live{c}" data-hse-figures data-portal="{PORTAL}" hidden>'
            f'<p class="hse-live-title">Latest HSE figures <span data-hse-asof></span></p><dl data-hse-list></dl></div>')

# Further registrations shown as cards on the HSE page, from the certificates in the BWS Company Profile (Oct 2026).
# Each row: (id, issuer, title, [(label, value, wide?)], note). The first two rows of each card should be the
# number and the validity (they are set larger). Directors' names and IC numbers on the certificates are left out.
REG_CARDS = [
    ("petros", "Petroleum Sarawak Berhad (PETROS)", "Registered vendor, PETROS Group", [
        ("Registration no.", "P250528-S", False),
        ("Valid until", "6 December 2028", False),
        ("Work categories", "SB200001 building &amp; structure construction · SO100005 onshore maintenance, construction &amp; modification (minor onshore fabrication) · SK500007 onshore pipeline fabrication &amp; construction", True),
        ("Covers", "PETROS and its related corporations, including PETROS E&amp;P, PETROS Gas, PETROSNiaga, PETROS Power and Sarawak Gas Distribution", True),
    ], "Registered since 7 December 2025, for quotations and tenders across the PETROS Group."),
    ("dosh", "Department of Occupational Safety and Health (DOSH)", "Competent Firm (Petroleum Contractor)", [
        ("Registration no.", "JKKP/2022/26/76", False),
        ("Valid until", "30 March 2028", False),
        ("Scope", "KPD 01 onshore pipeline · KPD 02 onshore reticulation piping", True),
        ("Registered workplaces", "Miri head office (SW/20/22/161834) and Bintulu fabrication yard (SW/18/03/128374)", True),
    ], "Approved for 31 March 2025 to 30 March 2028 by DOSH's Petroleum Safety Division."),
    ("upkj", "Sarawak State Financial Secretary (UPKJ)", "Class A contractor, works and mechanical", [
        ("Certificates", "UPKJ/W/021609 · UPKJ/M/001828", False),
        ("Valid until", "4 July 2028", False),
        ("Classification", "Works: Class A, Heads I, II and III · Mechanical: Class A, Head V", True),
        ("Rescue Contractor", "Recognised in the works and mechanical fields, valid to 26 August 2028", True),
    ], "Bumiputera status recognised by UPKJ for the same period."),
    ("mof", "Ministry of Finance Malaysia", "Registered supplier and Bumiputera company", [
        ("Certificate no.", "KQ24038211643726829", False),
        ("Valid until", "12 March 2027", False),
        ("Registration ref.", "357-30003574 · Bumiputera certificate BPQ24038211643726829", True),
        ("Supply and service fields", "020101 furniture &amp; fittings · 080101 civil engineering, construction &amp; public amenities equipment · 220502 maintenance &amp; repair of containers and tanks · 220503 electrical systems and equipment · 220506 bulk fuel tanks · 220507 pumps, water pipes and components", True),
    ], "Registered with the Ministry of Finance since 2 January 2024."),
    ("score", "CIDB Malaysia and SME Corp", "SCORE 3-star rating", [
        ("Certificate no.", "SC150630", False),
        ("Valid until", "1 September 2027", False),
        ("Rating", "3 stars for 2025, as a Grade G7 contractor", True),
        ("Assessment", "Good management and technical capabilities, compliance with best practices and good project management", True),
    ], "Issued on 2 September 2025."),
    ("ssm", "Companies Commission of Malaysia (SSM)", "Private limited company", [
        ("Company no.", "200201029529 (597192-V)", False),
        ("Incorporated", "29 October 2002", False),
        ("Paid-up capital", "RM5,000,000", True),
        ("Registered address", "Lot 1743, Block 3 MCLD, Piasau Industrial Estate Phase III, Jalan Prunus 1, 98000 Miri, Sarawak", True),
    ], "Wholly owned Bumiputera company."),
]

def reg_cards():
    out = ""
    for rid, issuer, title, rows, note in REG_CARDS:
        # A long number gets the full width so it never breaks in the middle
        dl = "".join(f'<div{" class=\"wide\"" if wide or len(v) > 16 else ""}><dt>{k}</dt><dd>{v}</dd></div>' for k, v, wide in rows)
        out += f'''
      <article class="cert-card" aria-labelledby="{rid}-card-title">
        <header class="cert-head">
          <div><p class="cert-issuer">{issuer}</p><h3 id="{rid}-card-title">{title}</h3></div>
        </header>
        <dl class="cert-data">{dl}</dl>
        <p class="small mb-0">{note}</p>
      </article>'''
    return out

def hse():
    return head("hse.html", "HSE &amp; Quality | ISO 9001:2015 | BWS Engineering Sdn Bhd",
        "BWS Engineering’s HSE, Quality, Anti-Corruption and Sustainability policies. ISO 9001:2015 (TÜV NORD) and ISO 45001:2018 (BSI) certified, with national OSH awards.") + header("hse.html") + page_hero(
        "HSE &amp; Quality", "Health, safety, environment and quality",
        "Our policies, certifications and recognition in health, safety, environment and quality.",
        "hard-hat") + f'''

<section class="section" id="hse" aria-labelledby="hsep-title">
  <div class="container split">
    <div>
      {eyebrow("01", "HSE policy")}
      <h2 id="hsep-title">Our HSE policy</h2>
      <div class="policy policy--hse">
        <span class="safety-tag">{icon("warn")} Health · Safety · Environment</span>
        <blockquote>
          <p>BWS Engineering Sdn Bhd is committed to conducting its operations with full regard to Health, Safety and Environmental (HSE) requirements. No work shall commence or continue without ensuring a safe and healthy workplace and protection of the environment.</p>
        </blockquote>
        <p class="policy-sub">To achieve this, the company undertakes to:</p>
        <ul class="ticks mb-0">
          <li>Create a safe and healthy workplace</li>
          <li>Prevent all occupational diseases and accidents</li>
          <li>Create an environment that recognises safe and healthy practice</li>
          <li>Work in a manner that is friendly to the environment</li>
          <li>Provide experienced, trained and competent management and supervisors</li>
        </ul>
      </div>
      <p class="mt-5 mb-0">Our performance in Health, Safety and Environment is the ultimate yardstick of our success in running our business.</p>
    </div>
    <figure class="media media--framed ratio-4x3 reveal">
      {img("mech-container-unloading", "Crew in coveralls, hard hats and gloves unloading materials from a container", 800, 487)}
      <figcaption>Full PPE during material handling.</figcaption>
    </figure>
  </div>
</section>

<section class="section section--tint" id="quality" aria-labelledby="qp-title">
  <div class="container split split--reverse">
    <div>
      {eyebrow("02", "Quality policy")}
      <h2 id="qp-title">Our quality policy</h2>
      <div class="policy">
        <blockquote>
          <p>BWS Engineering Sdn Bhd is committed to providing products and services of the highest quality to achieve total customer satisfaction through continually improving the effectiveness of its Quality Management System.</p>
        </blockquote>
        <p class="policy-sub">Our quality objectives:</p>
        <ul class="ticks mb-0">
          <li>Continuously improve our products and services by upgrading our people’s skills, with at least 4 hours of training for every employee each year</li>
          <li>Provide and maintain high-quality services in compliance with ISO 9001, aiming for zero customer complaints</li>
          <li>Assess vendors and subcontractors at least once a year</li>
        </ul>
      </div>
    </div>
    <div>
      <!-- ISO CERTIFICATE: details from TÜV NORD's public certificate database (checked Oct 2026).
           Update "Valid until" when the certificate is renewed. -->
      <article class="cert-card" aria-labelledby="cert-card-title">
        <header class="cert-head">
          <div><p class="cert-issuer">TÜV NORD CERT GmbH</p><h3 id="cert-card-title">ISO 9001:2015 Quality Management System</h3></div>
        </header>
        <dl class="cert-data">
          <div><dt>Certificate no.</dt><dd>44100072059</dd></div>
          <div><dt>Valid until</dt><dd>7 February 2028</dd></div>
          <div class="wide"><dt>Certificate holder</dt><dd>BWS Engineering Sdn. Bhd., Lot 1743, Block 3 MCLD, Piasau Industrial Estate, 98000 Miri, Sarawak</dd></div>
          <div class="wide"><dt>Scope</dt><dd>Provision of service in engineering, construction and project management</dd></div>
        </dl>
        <a class="link-arrow" href="https://www.tuev-nord.de/en/certificate-database/" target="_blank" rel="noopener">Verify with TÜV NORD (certificate no. 44100072059)<span class="visually-hidden"> (opens in a new tab)</span></a>
      </article>
      <article class="cert-card mt-6" aria-labelledby="ohs-card-title">
        <header class="cert-head">
          <div><p class="cert-issuer">BSI</p><h3 id="ohs-card-title">ISO 45001:2018 Occupational Health &amp; Safety Management System</h3></div>
        </header>
        <dl class="cert-data">
          <div><dt>Certificate no.</dt><dd>OHS 796482</dd></div>
          <div><dt>Valid until</dt><dd>25 September 2027</dd></div>
          <div class="wide"><dt>Scope</dt><dd>Engineering, construction and project management, including civil, mechanical, piping, electrical and instrumentation works</dd></div>
          <div class="wide"><dt>Sites</dt><dd>Miri head office and Bintulu, Sarawak</dd></div>
        </dl>
        <a class="link-arrow" href="https://www.bsigroup.com/en-GB/validate-bsi-issued-certificates/" target="_blank" rel="noopener">Verify with BSI (certificate no. OHS 796482)<span class="visually-hidden"> (opens in a new tab)</span></a>
      </article>
    </div>
  </div>
</section>

<section class="section" aria-labelledby="cert-title">
  <div class="container">
    <div class="section-head">{eyebrow("03", "Licences &amp; certification")}<h2 id="cert-title">Licences and registrations</h2></div>
    <!-- CIDB details from CIDB's public contractor search (CIMS), checked Oct 2026.
         PETRONAS licences can't be looked up publicly (PLMS needs a vendor login): details from the MPRC supplier directory. -->
    <div class="grid grid--2 reveal-stagger">
      <article class="cert-card" aria-labelledby="cidb-card-title">
        <header class="cert-head">
          <div><p class="cert-issuer">CIDB Malaysia</p><h3 id="cidb-card-title">Grade G7 registered contractor</h3></div>
        </header>
        <dl class="cert-data">
          <div><dt>Registration no.</dt><dd>0120030415-SR082502</dd></div>
          <div><dt>Valid until</dt><dd>7 November 2028</dd></div>
          <div class="wide"><dt>Categories</dt><dd>B (Building) · CE (Civil Engineering) · ME (Mechanical &amp; Electrical)</dd></div>
          <div class="wide"><dt>Certificates</dt><dd>PPK (contractor registration) · SPKK (government works) · STB (Bumiputera status)</dd></div>
          <div class="wide"><dt>Registered since</dt><dd>April 2003</dd></div>
        </dl>
        <a class="link-arrow" href="https://cims.cidb.gov.my/smis/regcontractor/reglocalsearchcontractor.vbhtml" target="_blank" rel="noopener">Verify on CIDB’s contractor search<span class="visually-hidden"> (opens in a new tab)</span></a>
      </article>
      <article class="cert-card" aria-labelledby="pet-card-title">
        <header class="cert-head">
          <div><p class="cert-issuer">PETRONAS</p><h3 id="pet-card-title">Licensed to supply services to oil &amp; gas companies</h3></div>
        </header>
        <dl class="cert-data">
          <div><dt>Licensed since</dt><dd>2004</dd></div>
          <div><dt>Valid until</dt><dd>30 July 2027</dd></div>
          <div class="wide"><dt>Licensed categories</dt><dd>Onshore pipeline · Onshore pipeline inspection &amp; repair · Major and minor onshore fabrication · Metallic (carbon &amp; stainless steel) and non-metallic (PVC, HDPE, fibreglass) piping · Cleaning, repair &amp; maintenance · Slope protection</dd></div>
        </dl>
        <p class="small mb-0">Issued under the Petroleum Development Act 1974.</p>
      </article>
    </div>
    <h3 class="reg-more-title">Further registrations</h3>
    <!-- FURTHER REGISTRATIONS: edit REG_CARDS above hse() when a certificate is renewed. -->
    <div class="grid grid--2 reg-more">{reg_cards()}
    </div>
    <details class="reg-detail">
      <summary>CIDB and PETRONAS codes for procurement teams</summary>
      <dl class="reg-codes">
        <div><dt>CIDB G7 specialisations: Building</dt><dd>B01 · B02 · B04 · B05 · B12</dd></div>
        <div><dt>CIDB G7 specialisations: Civil Engineering</dt><dd>CE01 · CE02 · CE03 · CE09 · CE20 · CE21 · CE36 · CE41</dd></div>
        <div><dt>CIDB G7 specialisations: Mechanical &amp; Electrical</dt><dd>E03 · E05 · E06 · E10 · E11 · E16 · E32 · M01 · M02 · M12 · M14 · M15 · M20 · M21</dd></div>
        <div><dt>PETRONAS licence codes</dt><dd>15141911S non-metallic piping · 15141700S onshore pipeline · 27131100S onshore pipeline inspection &amp; repair · 24241010S cleaning, repair &amp; maintenance · 27111000S minor onshore fabrication · 11141700S slope protection · 15141610S major fabrication · 15141910S metallic piping (carbon &amp; stainless steel)</dd></div>
      </dl>
    </details>
  </div>
</section>

<section class="section" id="record" aria-labelledby="record-title">
  <div class="container">
    <div class="section-head section-head--split">
      <div>{eyebrow("", "HSE performance")}<h2 id="record-title">Our safety record</h2></div>
      <p class="lead">Milestones recorded and certified by our clients on major projects.</p>
    </div>
    <!-- HSE RECORD: edit HSE_RECORD in tools/generate_site.py. Each figure is backed by a certificate in the company profile.
         Current figures are published from the BWS Portal (HSE figures) and appear above the list. -->
    {hse_live()}
    <ul class="hse-record reveal-stagger" role="list">{"".join(f'<li><span class="hse-record-num">{n}</span><span class="hse-record-label">{l}</span><span class="hse-record-note">{d}</span></li>' for n, l, d in HSE_RECORD)}</ul>
  </div>
</section>

<section class="section section--ink" id="awards" aria-labelledby="awards-title">
  <div class="container">
    <div class="section-head section-head--split">
      <div>{eyebrow("", "Recognition")}<h2 id="awards-title">Awards &amp; recognition</h2></div>
      <p class="lead">Recognised by government, industry and our clients for safety performance and quality of work.</p>
    </div>
    <!-- AWARDS: from the BWS Company Profile (Oct 2026), "List of Awards". -->
    <ul class="award-photos reveal-stagger" role="list">
      <li><figure>{img("award-psiea", "BWS receiving the PSIEA 2025 Silver Award on stage", 369, 328, "(min-width: 60rem) 25vw, 50vw")}<figcaption>PSIEA 2025</figcaption></figure></li>
      <li><figure>{img("award-msosh-trophy", "MSOSH Gold Class 1 Award trophy for the MLNG Power Import Project", 800, 1067, "(min-width: 60rem) 25vw, 50vw")}<figcaption>MSOSH Gold Class 1</figcaption></figure></li>
      <li><figure>{img("award-samsung-trophy", "Samsung E&amp;A appreciation trophy for the National OSH Award 2023", 800, 1067, "(min-width: 60rem) 25vw, 50vw")}<figcaption>Samsung E&amp;A appreciation</figcaption></figure></li>
      <li><figure>{img("award-46m-safe-manhours", "BWS representatives recognised for 46 million safe man-hours", 466, 311, "(min-width: 60rem) 25vw, 50vw")}<figcaption>46 million safe man-hours</figcaption></figure></li>
    </ul>
    <ul class="award-grid reveal-stagger" role="list">
      <li class="award award--lead"><span class="award-year">2025</span><h3>PSIEA Silver Award</h3><p>Premier of Sarawak Industry Excellence Awards, Large Enterprise category.</p></li>
      <li class="award award--lead"><span class="award-year">2023</span><h3>National OSH Award</h3><p>Anugerah Keselamatan dan Kesihatan Pekerjaan Negara 2023, for the OSH management system at the workplace.</p></li>
      <li class="award award--lead"><span class="award-year">2023</span><h3>MSOSH Gold Class 1 Award</h3><p>Malaysian Society for Occupational Safety and Health, for very good OSH performance on the MLNG Power Import Project (Transgrid-BWS JV).</p></li>
      <li class="award"><span class="award-year">2023</span><h3>PTTEP CEO SSHE Excellence Award</h3><p>For safety, security, health and environment performance excellence.</p></li>
      <li class="award"><span class="award-year">2023</span><h3>Samsung E&amp;A appreciation</h3><p>For contribution to the National OSH Award by NCOSH on the Rosmari-Marjoram Onshore Gas Plant Project.</p></li>
      <li class="award"><span class="award-year">2022</span><h3>IRSO West Coast Mega HSE Council</h3><p>Top 5 Best Project HSE Performance, Sabah Sarawak Gas Pipeline KP220 &amp; KP265.</p></li>
      <li class="award"><span class="award-year">2022</span><h3>PETRONAS certificate of appreciation</h3><p>Successful completion of the mechanical scope, 36" SSGP pipeline replacement at KP220.</p></li>
      <li class="award"><span class="award-year">2021</span><h3>DOSH Grade A workplace</h3><p>Grade A (score 92) in the DOSH Sarawak workplace inspection of the Bintulu yard.</p></li>
      <li class="award"><span class="award-year">2020</span><h3>PETRONAS Focused Recognition</h3><p>Work completed 25 days ahead of schedule with zero LTI and within cost.</p></li>
      <li class="award"><span class="award-year">2018</span><h3>PRPC Focused Recognition</h3><p>PETRONAS Refinery &amp; Petrochemical Corporation, for the underground GRE firewater installation in Area East, RAPID.</p></li>
      <li class="award"><span class="award-year">2015</span><h3>400,000 exposure hours without LTI</h3><p>Shell MDS certificates of appreciation (200,000 and 400,000 hours), SMDS Rejuvenation Project 2015.</p></li>
      <li class="award"><span class="award-year">2013</span><h3>PETRONAS Best HSE Practice, Gold</h3><p>FED HSE Awareness Day, for dedication and commitment to safety at the workplace.</p></li>
      <li class="award"><span class="award-year">2013</span><h3>MLNG &amp; MLNG Dua Contractor HSE Award</h3><p>New Common Reclaimer Project, incident and injury free from Feb to Oct 2013.</p></li>
      <li class="award"><span class="award-year">2013</span><h3>MLNG Tiga ROSE Contractor HSE Award</h3><p>Injury and environmental incident free from Feb 2012 to May 2013.</p></li>
      <li class="award"><span class="award-year">2012</span><h3>250,000 man-hours LTI-free</h3><p>Milestone on the MLNG ROSE Project, recognised by JGC SP (M).</p></li>
      <li class="award"><span class="award-year">2011</span><h3>MLNG HSE Excellence Recognition</h3><p>Malaysia LNG, for significant contribution through excellent HSE performance.</p></li>
      <li class="award"><span class="award-year">2010</span><h3>3,000,000 man-hours without LTI</h3><p>HSE Award from the Rekind–Simfoni consortium, MCOT Rejuvenation Project Phase 2.</p></li>
      <li class="award"><span class="award-year">2005</span><h3>237,296 man-hours without LTI</h3><p>Sarawak Shell certificate of appreciation, Bintulu Integrated Facilities.</p></li>
      <li class="award"><span class="award-year">Recognition</span><h3>46 million safe man-hours</h3><p>Honoured for our contribution to a project milestone of 46 million safe man-hours.</p></li>
    </ul>
  </div>
</section>

<section class="section" aria-labelledby="ethics-title">
  <div class="container">
    <div class="section-head">{eyebrow("", "Integrity")}<h2 id="ethics-title">Anti-corruption and sustainability</h2></div>
    <div class="grid grid--2 reveal-stagger">
      <div class="policy"><h3>Anti-Corruption and Bribery Policy</h3><blockquote><p>At BWS Engineering Sdn Bhd, we are committed to conducting business honestly, ethically, and with integrity, with zero tolerance for bribery and corruption, and by maintaining effective measures to prevent and combat bribery.</p></blockquote></div>
      <div class="policy"><h3>Sustainability</h3><blockquote><p>We are committed to operating responsibly and sustainably. We aim to reduce our environmental impact through efficient use of resources, waste reduction, and environmentally friendly engineering practices. We support ESG principles and CSR initiatives by conducting business ethically, supporting our communities, and creating long-term value for our stakeholders.</p></blockquote></div>
    </div>
  </div>
</section>

<section class="section section--steel" aria-labelledby="site-title">
  <div class="container">
    <div class="section-head section-head--split">
      <div>{eyebrow("04", "On site")}<h2 id="site-title">Safety in practice</h2></div>
      <div class="callout-safety"><strong>Planning and supervision.</strong> Hazards are assessed before work begins, and site safety supervisors monitor every activity until completion.</div>
    </div>
    <div class="grid grid--3 reveal-stagger">
      <figure class="media ratio-4x3">{img("hse-site-walk", "Supervisors in hard hats walking a cleared construction site", 577, 564, "(min-width: 60rem) 33vw, 100vw")}<figcaption>Site inspection.</figcaption></figure>
      <figure class="media ratio-4x3">{img("hse-fire-drill", "Crew in coveralls and hard hats during a fire extinguisher drill", 800, 600, "(min-width: 60rem) 33vw, 100vw")}<figcaption>Fire extinguisher drill.</figcaption></figure>
      <figure class="media ratio-4x3">{img("hse-toolbox-talk", "Workers gathered under a tent for a toolbox talk", 800, 600, "(min-width: 60rem) 33vw, 100vw")}<figcaption>Toolbox talk.</figcaption></figure>
    </div>
    <figure class="media hse-milestone reveal">
      {img("hse-awareness-day", "Large group of BWS and client staff in green and blue workwear at an HSE Awareness Day in a hall", 1600, 875, "(min-width: 75rem) 1200px, 100vw", big=True)}
      <figcaption><strong>150,000 man-hours.</strong> HSE Awareness Day for the EPCC of the PETRONAS Dagangan Miri Fuel Terminal, September 2015.</figcaption>
    </figure>
  </div>
</section>
{CTA}''' + footer()

# ================================================================ CAREERS
def careers():
    cv_body = "Position / discipline:\nYears of experience:\nCurrent location:\nPhone number:\n\n(Please attach your CV and certificates.)"
    return head("careers.html", "Careers | Jobs in Oil &amp; Gas Construction, Miri &amp; Bintulu | BWS Engineering",
        "Join BWS Engineering Sdn Bhd in Miri and Bintulu, Sarawak, a safety-first oil &amp; gas construction and maintenance contractor. Send your CV to bwsesbhr@gmail.com.") + header("careers.html") + page_hero(
        "Careers", "Build your career with BWS",
        "Join a Sarawak contractor that has been building and maintaining oil and gas facilities since 2002.",
        "tools") + f'''

<section class="section" aria-labelledby="work-title">
  <div class="container split split--wide-text">
    <div>
      {eyebrow("01", "Working at BWS")}
      <h2 id="work-title">A career in engineering and construction</h2>
      <p class="lead">Our workforce comprises engineers, supervisors and skilled tradespeople in civil, mechanical, piping, and electrical and instrumentation disciplines, based at our Miri head office and Bintulu fabrication yard.</p>
      <p>Our work spans industrial plant construction and maintenance, mechanical and piping, civil and structural steel, and electrical and instrumentation, for some of the region’s major oil and gas operators and EPC contractors.</p>
    </div>
    <aside class="callout-safety" aria-labelledby="safe-title">
      <span class="safety-tag">{icon("hat")} Safety-first culture</span>
      <h3 id="safe-title" style="font-size:1.2rem">A safety-first workplace</h3>
      <p class="mb-0">Safety is the first responsibility of every employee. All personnel are inducted, trained and supervised in line with our HSE policy and ISO 45001:2018 management system.</p>
    </aside>
  </div>
</section>

<section class="section" id="openings" aria-labelledby="open-title" data-portal="{PORTAL}" hidden>
  <div class="container">
    <div class="section-head">{eyebrow("", "Vacancies")}<h2 id="open-title">Current openings</h2></div>
    <!-- VACANCIES: managed in the BWS Portal (Vacancies) and loaded here by main.js. This section stays
         hidden until the portal answers, so the email option below always works on its own. -->
    <p class="lead" data-no-openings hidden>There are no advertised openings at the moment. You are welcome to send a general application below.</p>
    <ul class="vacancies" data-vacancies role="list"></ul>

    <div class="enquiry-card apply-online" id="apply-online">
      <h2 id="apply-online-title">Apply online</h2>
      <p class="lead">Complete the form and attach your CV. Our recruitment team reviews every application.</p>
      <form class="form" method="POST" action="{PORTAL}/api/applications" enctype="multipart/form-data" data-apply-form>
        <div class="form-row">
          <div class="field"><label for="a-vacancy">Position</label>
            <select id="a-vacancy" name="vacancy_id"><option value="">General application</option></select>
          </div>
          <div class="field" data-position-other><label for="a-position">Position or discipline <span class="req" aria-hidden="true">*</span></label><input id="a-position" name="position" type="text" maxlength="120" required aria-describedby="a-position-error"><span class="field-error" id="a-position-error" hidden>Please tell us the position or discipline you are applying for.</span></div>
        </div>
        <div class="form-row">
          <div class="field"><label for="a-name">Full name <span class="req" aria-hidden="true">*</span></label><input id="a-name" name="name" type="text" autocomplete="name" maxlength="120" required aria-describedby="a-name-error"><span class="field-error" id="a-name-error" hidden>Please enter your name.</span></div>
          <div class="field"><label for="a-email">Email <span class="req" aria-hidden="true">*</span></label><input id="a-email" name="email" type="email" autocomplete="email" maxlength="200" required aria-describedby="a-email-error"><span class="field-error" id="a-email-error" hidden>Please enter a valid email address.</span></div>
        </div>
        <div class="form-row">
          <div class="field"><label for="a-phone">Phone <span class="req" aria-hidden="true">*</span></label><input id="a-phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" maxlength="40" required aria-describedby="a-phone-error"><span class="field-error" id="a-phone-error" hidden>Please enter a phone number.</span></div>
          <div class="field"><label for="a-location">Current location</label><input id="a-location" name="location" type="text" autocomplete="address-level2" maxlength="120"></div>
        </div>
        <div class="form-row">
          <div class="field"><label for="a-years">Years of experience</label><input id="a-years" name="years_experience" type="number" min="0" max="60" inputmode="numeric"></div>
          <div class="field"><label for="a-cv">CV <span class="req" aria-hidden="true">*</span></label><input id="a-cv" name="cv" type="file" accept=".pdf,.doc,.docx" required aria-describedby="a-cv-hint a-cv-error"><span class="form-note" id="a-cv-hint">PDF or Word, up to 5 MB. Please include your certificates in the same file.</span><span class="field-error" id="a-cv-error" hidden>Please attach your CV as a PDF or Word file of up to 5 MB.</span></div>
        </div>
        <div class="field"><label for="a-message">Anything else we should know</label><textarea id="a-message" name="message" maxlength="3000"></textarea></div>
        <div class="field field--check"><input id="a-consent" name="consent" type="checkbox" value="1" required aria-describedby="a-consent-error"><label for="a-consent">I agree to BWS Engineering Sdn Bhd using my personal data to consider my application, as described in the <a href="privacy.html">Privacy Notice</a>. <span class="req" aria-hidden="true">*</span></label><span class="field-error" id="a-consent-error" hidden>Please tick to agree before sending your application.</span></div>
        <div class="hp" aria-hidden="true"><label for="a-hp">Leave this empty</label><input id="a-hp" name="_gotcha" type="text" tabindex="-1" autocomplete="off"></div>
        <p class="form-note mb-0"><span aria-hidden="true">*</span> Required fields.</p>
        <div><button class="btn btn--primary" type="submit">Submit application {icon("arrow")}</button></div>
        <div class="form-status" role="status" aria-live="polite" hidden></div>
      </form>
    </div>
  </div>
</section>

<section class="section section--steel" id="apply" aria-labelledby="apply-title">
  <div class="container">
    <div class="apply-card">
      <div>
        {eyebrow("", "Join us")}
        <h2 id="apply-title">Send your CV</h2>
        <p class="lead">We welcome applications from experienced engineering and construction professionals. Please email your CV and certificates to our recruitment team, stating the position or discipline applied for.</p>
        <p class="apply-address">{icon("mail")}<a href="mailto:bwsesbhr@gmail.com?subject={quote("Job Application – [Position]")}">bwsesbhr@gmail.com</a></p>
      </div>
    </div>
  </div>
</section>
{CTA}''' + footer()

# ================================================================ CONTACT
# Listings of BWS's own Google Maps business entries (verified Oct 2026). The office coordinates and the
# site drawings next to each office come from tools/make_locations.py (SITES); pin_style() places the pulse ring.
import make_locations
MIRI_PLACE = "https://www.google.com/maps/place/Bws+Engineering+Sdn.+Bhd./@4.446917,114.011563,17z/data=!4m6!3m5!1s0x321f4eff4ad03523:0x3a7d83606d409313!8m2!3d4.446917!4d114.011563"
BTU_PLACE = "https://www.google.com/maps/place/BWS+Engineering+Sdn.+Bhd./@3.2724729,113.0802423,17z/data=!4m6!3m5!1s0x321dc31223ffffff:0x53e0ada3f9e5e7f2!8m2!3d3.2724729!4d113.0802423"

def contact():
    miri_q = "Lot 1743, Block 3 MCLD, Piasau Industrial Estate Phase III, Jalan Prunus 1, 98000 Miri, Sarawak"
    btu_q = "Lot 782, Block 20, Kemena Land District, Jalan Tanjung Kidurong, 97007 Bintulu, Sarawak"
    opts = "".join(f'<option value="{t.replace("&amp;", "&")}" data-key="{sid}">{t}</option>' for sid, _i, t, *_ in SERVICES)
    ld = [{"@context": "https://schema.org", "@type": "ContactPage", "url": SITE + "/contact.html", "about": {"@id": SITE + "/#organization"}}]
    return head("contact.html", "Contact Us | Miri &amp; Bintulu Offices | BWS Engineering Sdn Bhd",
        "Contact BWS Engineering Sdn Bhd. Main office and workshop in Piasau Industrial Estate, Miri (085-652743) and fabrication yard in Kidurong, Bintulu (086-252476). Email bwsesb@gmail.com.", ld) + header("contact.html") + page_hero(
        "Contact", "Contact us",
        "Contact our Miri or Bintulu office, or submit an enquiry and it will be directed to the relevant department.",
        "coast-map") + f'''

<section class="section" aria-labelledby="off-title">
  <div class="container">
    <div class="section-head">{eyebrow("01", "Offices")}<h2 id="off-title">Our offices</h2></div>
    <div class="grid grid--2">
      <article class="office" aria-labelledby="miri-title">
        <div class="office-body">
          <span class="tag">Main Office</span>
          <h3 id="miri-title">Miri: Office cum Workshop</h3>
          <ul class="contact-list" role="list">
            <li>{icon("pin")}<address>Lot 1743, Block 3 MCLD, Piasau Industrial Estate Phase III, Jalan Prunus 1, 98000 Miri, Sarawak, Malaysia</address></li>
            <li>{icon("phone")}<span><a href="tel:+6085652743">085-652743</a> / <a href="tel:+6085652744">44</a> / <a href="tel:+6085652745">45</a></span></li>
            <li>{icon("fax")}<span>Fax: 085-652709</span></li>
            <li>{icon("mail")}<span><a href="mailto:bws@bwsengineeringsb.com">bws@bwsengineeringsb.com</a><br><a href="mailto:bwsesb@gmail.com">bwsesb@gmail.com</a></span></li>
          </ul>
          <p class="mt-5 mb-0"><a class="link-arrow" href="{MIRI_PLACE}" target="_blank" rel="noopener">Open in Google Maps<span class="visually-hidden"> (opens in a new tab)</span></a></p>
        </div>
        <div class="map-wrap" style="{make_locations.pin_style("miri")}">
          <img class="map-drawing" fetchpriority="low" src="assets/illustrations/loc-miri.svg" alt="Site drawing of the BWS Engineering main office location, Piasau Industrial Estate, Miri" width="800" height="500" loading="lazy" decoding="async">
          <span class="map-pulse" aria-hidden="true"></span>
        </div>
      </article>
      <article class="office" aria-labelledby="btu-title">
        <div class="office-body">
          <span class="tag">Fabrication Yard</span>
          <h3 id="btu-title">Bintulu: Office cum Fabrication Yard</h3>
          <ul class="contact-list" role="list">
            <li>{icon("pin")}<address>Lot 782, Block 20, Kemena Land District, Jalan Tanjung Kidurong, 97007 Bintulu, Sarawak, Malaysia</address></li>
            <li>{icon("phone")}<a href="tel:+6086252476">086-252476</a></li>
            <li>{icon("mail")}<span><a href="mailto:bws@bwsengineeringsb.com">bws@bwsengineeringsb.com</a><br><a href="mailto:bwsesb@gmail.com">bwsesb@gmail.com</a></span></li>
          </ul>
          <p class="mt-4 small mb-0"><strong>Fabrication yard:</strong> Lot 124–128, Block 20, Kemena Land District, Jalan Kidurong, 97000 Bintulu, Sarawak</p>
          <p class="mt-5 mb-0"><a class="link-arrow" href="{BTU_PLACE}" target="_blank" rel="noopener">Open in Google Maps<span class="visually-hidden"> (opens in a new tab)</span></a></p>
        </div>
        <div class="map-wrap" style="{make_locations.pin_style("bintulu")}">
          <img class="map-drawing" fetchpriority="low" src="assets/illustrations/loc-bintulu.svg" alt="Site drawing of the BWS Engineering Bintulu office location, Kidurong Industrial Estate" width="800" height="500" loading="lazy" decoding="async">
          <span class="map-pulse" aria-hidden="true"></span>
        </div>
      </article>
    </div>
  </div>
</section>

<section class="section section--steel" id="enquiry" aria-labelledby="form-title">
  <div class="container">
    <div class="enquiry-card">
      <h2 id="form-title">Enquiry</h2>
      <p class="lead">For quotations and general enquiries, please complete the form below.</p>
      <!-- CONTACT FORM: posts to the BWS Portal (saved in its Enquiries list and emailed). If the portal
           doesn't answer it tries data-fallback (contact.php, emails only; PHP hosts), and if that fails too
           the visitor's email app opens, pre-filled and addressed to data-mailto. -->
      <form class="form" action="{PORTAL}/api/enquiries" method="POST" data-contact-form data-fallback="contact.php" data-mailto="bws@bwsengineeringsb.com">
        <input type="hidden" name="_subject" value="Website enquiry: BWS Engineering">
        <div class="form-row">
          <div class="field"><label for="f-name">Name <span class="req" aria-hidden="true">*</span></label><input id="f-name" name="name" type="text" autocomplete="name" required aria-describedby="f-name-error"><span class="field-error" id="f-name-error" hidden>Please enter your name.</span></div>
          <div class="field"><label for="f-company">Company</label><input id="f-company" name="company" type="text" autocomplete="organization"></div>
        </div>
        <div class="form-row">
          <div class="field"><label for="f-email">Email <span class="req" aria-hidden="true">*</span></label><input id="f-email" name="email" type="email" autocomplete="email" required aria-describedby="f-email-error"><span class="field-error" id="f-email-error" hidden>Please enter a valid email address.</span></div>
          <div class="field"><label for="f-phone">Phone</label><input id="f-phone" name="phone" type="tel" autocomplete="tel" inputmode="tel"></div>
        </div>
        <div class="field"><label for="f-service">Service of interest</label>
          <select id="f-service" name="service">
            <option value="">Select a service (optional)</option>{opts}
            <option value="Other / General enquiry">Other / General enquiry</option>
          </select>
        </div>
        <div class="field"><label for="f-message">Message <span class="req" aria-hidden="true">*</span></label><textarea id="f-message" name="message" required aria-describedby="f-message-error"></textarea><span class="field-error" id="f-message-error" hidden>Please tell us about your enquiry.</span></div>
        <div class="hp" aria-hidden="true"><label for="f-hp">Leave this empty</label><input id="f-hp" name="_gotcha" type="text" tabindex="-1" autocomplete="off"></div>
        <p class="form-note mb-0"><span aria-hidden="true">*</span> Required fields. We use your details only to reply to your enquiry, as described in our <a href="privacy.html">Privacy Notice</a>.</p>
        <div><button class="btn btn--primary" type="submit">Send enquiry {icon("arrow")}</button></div>
        <div class="form-status" role="status" aria-live="polite" hidden></div>
      </form>
    </div>
  </div>
</section>
''' + footer()

# ================================================================ PRIVACY (PDPA 2010)
# Shown on the page. When the notice changes, update this and PORTAL_PRIVACY_VERSION in portal/.env.
PRIVACY_VERSION = "October 2026"

PRIVACY_SECTIONS = [
    ("p-who", "Who we are", """<p>BWS Engineering Sdn Bhd (597192-V), Lot 1743, Block 3 MCLD, Piasau Industrial Estate Phase III, Jalan Prunus 1, 98000 Miri, Sarawak, Malaysia, is responsible for the personal data described in this notice.</p>"""),
    ("p-what", "What we collect", """<ul>
        <li><strong>Enquiries:</strong> your name, company, email address, phone number, the service you are interested in and your message.</li>
        <li><strong>Job applications:</strong> your name, email address, phone number, location, years of experience, the position you are applying for, your message, and your CV with anything it contains, such as qualifications, work history and certificates.</li>
        <li><strong>Technical data:</strong> like most websites, our web host keeps short-term server logs (IP address, browser type, pages requested) to run the site securely. We also count visits with Cloudflare Web Analytics, which does not use cookies or identify you. This website does not use advertising or tracking cookies.</li>
      </ul>
      <p>Fields marked with an asterisk (*) are required. If you do not provide them, we cannot reply to your enquiry or consider your application. Everything else is optional.</p>"""),
    ("p-why", "Why we use it", """<ul>
        <li>To reply to your enquiry and prepare quotations.</li>
        <li>To assess your job application, contact you about it and, if you are hired, start your employment records.</li>
        <li>To keep the website secure and prevent misuse of its forms.</li>
        <li>To meet our legal and regulatory obligations.</li>
      </ul>
      <p>We do not sell your personal data or use it for marketing.</p>"""),
    ("p-share", "Who we share it with", """<ul>
        <li>BWS staff who need it to handle your enquiry or application.</li>
        <li>Service providers that run our website, email and application system for us, under confidentiality obligations.</li>
        <li>Government or regulatory authorities, where the law requires it.</li>
      </ul>
      <p>Some of these providers, such as our email services, may store data on servers outside Malaysia. Where that happens, we take reasonable steps to make sure your data is protected to a standard comparable to Malaysian law.</p>"""),
    ("p-keep", "How long we keep it", """<ul>
        <li><strong>Enquiries</strong> are kept for as long as needed to deal with them and for our business records.</li>
        <li><strong>Job applications and CVs</strong> are kept for up to 12 months after they are received and then deleted, unless you join BWS. You can ask us to delete yours sooner.</li>
      </ul>"""),
    ("p-safe", "How we protect it", """<p>The website uses an encrypted connection (HTTPS). CVs and enquiries are kept in BWS’s own email and records, and only the staff who handle them can see them.</p>"""),
    ("p-rights", "Your rights", """<p>You may ask us to:</p>
      <ul>
        <li>give you access to the personal data we hold about you;</li>
        <li>correct data that is inaccurate, incomplete or out of date;</li>
        <li>stop or limit using your data, or withdraw your consent (we may then be unable to continue with your enquiry or application);</li>
        <li>delete your job application and CV.</li>
      </ul>
      <p>Email <a href="mailto:bws@bwsengineeringsb.com">bws@bwsengineeringsb.com</a> or write to our Miri office. We will reply within 21 days.</p>"""),
    ("p-changes", "Changes to this notice", """<p>We may update this notice from time to time. The latest version is always on this page, with the date it was last updated.</p>"""),
]

def privacy():
    blocks = "".join(f'''
    <section aria-labelledby="{sid}">
      <h2 id="{sid}">{title}</h2>
      {body}
    </section>''' for sid, title, body in PRIVACY_SECTIONS)
    return head("privacy.html", "Privacy Notice | BWS Engineering Sdn Bhd",
        "How BWS Engineering Sdn Bhd collects, uses and protects personal data under Malaysia’s Personal Data Protection Act 2010.") + header("") + page_hero(
        "Privacy Notice", "Privacy notice",
        "How we collect, use and protect your personal data, in line with the Personal Data Protection Act 2010.",
        ) + f'''

<section class="section">
  <div class="container measure privacy-doc">
    <p class="lead">This notice explains what personal data BWS Engineering Sdn Bhd collects through this website, why we collect it, and the choices and rights you have. It is published in English and Bahasa Melayu.</p>
    <p class="small">Last updated: {PRIVACY_VERSION}</p>{blocks}
  </div>
</section>''' + footer()

# ================================================================ VENDOR INFORMATION + CAPABILITY STATEMENT
# Registration details, as also shown on the HSE page. Tax numbers, bank details and financial statements
# are given to procurement teams on request only.
REGISTRATIONS = [
    ("ISO 9001:2015", "Quality management system, TÜV NORD CERT GmbH. Certificate no. 44100072059", "7 Feb 2028"),
    ("ISO 45001:2018", "Occupational health and safety management system, BSI. Certificate no. OHS 796482", "25 Sep 2027"),
    ("CIDB Grade G7", "Categories B, CE and ME, with PPK, SPKK and STB certificates. Registration no. 0120030415-SR082502", "7 Nov 2028"),
    ("PETRONAS licence", "Licensed to supply products and services to exploration and oil and gas companies in Malaysia", "30 Jul 2027"),
    ("PETROS", "Registered vendor of Petroleum Sarawak Berhad and its group. Registration no. P250528-S", "6 Dec 2028"),
    ("DOSH", "Competent Firm (Petroleum Contractor), KPD 01 and KPD 02. Registration no. JKKP/2022/26/76", "30 Mar 2028"),
    ("MOF", "Ministry of Finance registered supplier and Bumiputera company. Certificate no. KQ24038211643726829", "12 Mar 2027"),
    ("UPKJ Sarawak", "Class A contractor in the works (UPKJ/W/021609) and mechanical (UPKJ/M/001828) fields. Rescue Contractor status valid to 26 Aug 2028", "4 Jul 2028"),
    ("CIDB SCORE", "3-star rating for 2025", "1 Sep 2027"),
]

ON_REQUEST = ["The full company profile, with certificate copies",
              "Copies of the MOF, PETROS, UPKJ and DOSH certificates",
              "Contract values and client references for past projects",
              "Audited financial statements and bank details",
              "Tax (TIN) and SST registration details",
              "HSE statistics, procedures and the quality manual"]

PARTICULARS = [
    ("Company", "BWS Engineering Sdn Bhd"),
    ("Company no.", "200201029529 (597192-V)"),
    ("Incorporated", "29 October 2002, Malaysia"),
    ("Ownership", "Wholly owned Bumiputera company"),
    ("Paid-up capital", "RM5,000,000"),
    ("Main office", "Lot 1743, Block 3 MCLD, Piasau Industrial Estate Phase III, Jalan Prunus 1, 98000 Miri, Sarawak"),
    ("Fabrication yard", "Lot 782, Block 20, Kemena Land District, Jalan Tanjung Kidurong, 97007 Bintulu, Sarawak"),
    ("Telephone", "085-652743 (Miri) · 086-252476 (Bintulu)"),
    ("Email", "bws@bwsengineeringsb.com"),
]

CAPABILITY_PDF = "assets/docs/bws-capability-statement.pdf"

def vendor():
    parts = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in PARTICULARS)
    regs = "".join(f'<tr><th scope="row">{n}</th><td>{d}</td><td class="reg-valid">{v}</td></tr>' for n, d, v in REGISTRATIONS)
    req = "".join(f"<li>{x}</li>" for x in ON_REQUEST)
    has_pdf = os.path.exists(OUT + CAPABILITY_PDF)
    pdf = (f'<a class="btn btn--primary" href="{CAPABILITY_PDF}" download>{icon("doc")}Download the capability statement (PDF)</a>' if has_pdf else "")
    return head("vendor.html", "Vendor Information for Procurement Teams | BWS Engineering Sdn Bhd",
        "Company particulars, registrations and licences with validity dates, and the capability statement of BWS Engineering Sdn Bhd, for vendor registration and tender prequalification.") + header("") + page_hero(
        "Vendor information", "Vendor information",
        "Company particulars, registrations and a capability statement for procurement and vendor registration teams.",
        ) + f'''

<section class="section">
  <div class="container">
    <div class="vendor-downloads">
      <div>
        <h2>Capability statement</h2>
        <p class="mb-0">A summary of our services, registrations, safety record, featured projects and the full equipment register, ready to attach to a vendor registration or prequalification.</p>
      </div>
      <div class="btn-row">{pdf}<a class="btn btn--ghost" href="capability.html">View it in your browser</a></div>
    </div>
  </div>
</section>

<section class="section section--steel" aria-labelledby="part-title">
  <div class="container">
    <div class="section-head">{eyebrow("", "Company")}<h2 id="part-title">Company particulars</h2></div>
    <dl class="vendor-particulars">{parts}</dl>
  </div>
</section>

<section class="section" aria-labelledby="reg-title">
  <div class="container">
    <div class="section-head section-head--split">
      <div>{eyebrow("", "Registrations")}<h2 id="reg-title">Registrations and licences</h2></div>
      <p class="lead">Certificate details and how to verify them are on our <a href="hse.html#cert-title">HSE &amp; Quality</a> page.</p>
    </div>
    <!-- REGISTRATIONS: edit REGISTRATIONS in tools/generate_site.py when a certificate is renewed. -->
    <div class="fl-scroll"><table class="fl-table reg-table">
      <thead><tr><th scope="col">Registration</th><th scope="col">Details</th><th scope="col">Valid until</th></tr></thead>
      <tbody>{regs}</tbody>
    </table></div>
  </div>
</section>

<section class="section section--steel" aria-labelledby="req-title">
  <div class="container split">
    <div>
      {eyebrow("", "On request")}
      <h2 id="req-title">Documents available on request</h2>
      <p>For vendor registration, prequalification or a tender, we can provide:</p>
      <ul class="ticks">{req}</ul>
    </div>
    <aside class="callout-safety">
      <h3 style="font-size:1.2rem">Contact for procurement</h3>
      <p>Email <a href="mailto:bws@bwsengineeringsb.com?subject={quote("Vendor registration / prequalification")}">bws@bwsengineeringsb.com</a> with the documents you need, or call our Miri office on <a href="tel:+6085652743">085-652743</a>.</p>
      <p class="mb-0"><a class="link-arrow" href="contact.html#enquiry">Send an enquiry</a></p>
    </aside>
  </div>
</section>
''' + footer()

def capability():
    """Printable capability statement (A4). tools/make_capability_pdf.js renders it to CAPABILITY_PDF."""
    svc = "".join(f"<li><strong>{t}</strong>: {short}</li>" for _sid, _ic, t, short, *_ in SERVICES)
    regs = "".join(f"<tr><th>{n}</th><td>{d}</td><td>{v}</td></tr>" for n, d, v in REGISTRATIONS)
    hse = "".join(f"<li><strong>{n}</strong> {l}<span>{d}</span></li>" for n, l, d in HSE_RECORD)
    cases = "".join(f'''<article><h3>{c["title"]}</h3><p class="meta">{c["client"]} · {c["years"]} · {c["where"]}</p><p>{c["summary"]}</p>{("<p class=res>" + c["results"][0] + "</p>") if c["results"] else ""}</article>''' for c in CASE_STUDIES)
    recent = "".join(f"<tr><td>{yrs}</td><td>{title}</td><td>{client}</td></tr>" for yrs, client, title, *_ in PROJECTS[:14])
    equip = "".join(f'''<tr class="eq-cat"><th colspan="3">{cat}</th></tr>''' + "".join(f"<tr><td>{d}</td><td>{c or '–'}</td><td>{u:,}</td></tr>" for d, c, u in items) for _g, cat, items in EQUIPMENT)
    parts = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in PARTICULARS)
    return f'''<!doctype html>
<html lang="en-MY">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Capability Statement | BWS Engineering Sdn Bhd</title>
<meta name="description" content="Capability statement of BWS Engineering Sdn Bhd: services, registrations, HSE record, featured projects and equipment.">
<meta name="robots" content="noindex">
<link rel="canonical" href="{SITE}/capability.html">
<link rel="icon" href="assets/logo/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="assets/css/capability.css?v={ASSET_V}">
</head>
<body>
<header class="cs-head">
  <img src="assets/logo/logo.svg" width="96" height="72" alt="BWS Engineering">
  <div><h1>BWS Engineering Sdn Bhd</h1><p>Capability statement · {PRIVACY_VERSION}</p></div>
  <p class="cs-contact">Miri 085-652743 · Bintulu 086-252476<br>bws@bwsengineeringsb.com<br>www.bwsengineeringsb.com</p>
</header>
<main>
<section><p class="cs-lead">A wholly owned Bumiputera engineering construction and maintenance contractor for the oil and gas industries, operating from Miri and Bintulu, Sarawak, since October 2002. More than 80 contracts delivered for oil and gas operators, EPC contractors, industry and government.</p></section>
<section class="cs-cols">
  <div><h2>Company particulars</h2><dl class="cs-dl">{parts}</dl></div>
  <div><h2>Core services</h2><ul>{svc}</ul>
  <h2>Facilities</h2><ul><li><strong>Miri</strong>: main office, warehouse and fabrication workshop, Piasau Industrial Estate</li><li><strong>Bintulu</strong>: fabrication yard at Kidurong with covered fabrication shop, open fabrication area, storage, blasting and painting, and NDT facilities</li></ul></div>
</section>
<section><h2>Registrations and licences</h2><table class="cs-table"><thead><tr><th>Registration</th><th>Details</th><th>Valid until</th></tr></thead><tbody>{regs}</tbody></table></section>
<section><h2>HSE record</h2><p>HSE policy and ISO 45001:2018 certified management system. Milestones certified by our clients:</p><ul class="cs-hse">{hse}</ul></section>
<section><h2>Featured projects</h2><div class="cs-cases">{cases}</div></section>
<section><h2>Recent and current projects</h2><table class="cs-table"><thead><tr><th>Years</th><th>Project</th><th>Client</th></tr></thead><tbody>{recent}</tbody></table><p class="cs-note">Full list of {len(ALL_PROJECTS)} contracts since 2003: www.bwsengineeringsb.com/projects.html</p></section>
<section class="cs-break"><h2>Appendix: equipment register</h2><p>Company-owned plant and equipment, October 2026. Availability for a particular project is confirmed at tender stage.</p><table class="cs-table cs-equip"><thead><tr><th>Item</th><th>Capacity</th><th>Units</th></tr></thead><tbody>{equip}</tbody></table></section>
</main>
<footer class="cs-foot">BWS Engineering Sdn Bhd (597192-V) · Lot 1743, Block 3 MCLD, Piasau Industrial Estate Phase III, Jalan Prunus 1, 98000 Miri, Sarawak · Further documents on request: bws@bwsengineeringsb.com</footer>
</body>
</html>
'''

def offline():
    """Shown by the service worker when there is no connection and the page was never opened before."""
    return head("offline.html", "Offline | BWS Engineering Sdn Bhd", "You are offline.").replace('<meta name="robots" content="index, follow">', '<meta name="robots" content="noindex">') + header("") + f'''
<section class="section">
  <div class="container measure">
    {eyebrow("", "No connection")}
    <h1>You’re offline</h1>
    <p class="lead">This page hasn’t been saved on your device yet. Please check your connection and try again. Pages you have opened before will still work.</p>
    <p lang="ms">Anda di luar talian. Sila semak sambungan anda dan cuba lagi.</p>
    <p>Miri <a href="tel:+6085652743">085-652743</a> · Bintulu <a href="tel:+6086252476">086-252476</a> · <a href="mailto:bws@bwsengineeringsb.com">bws@bwsengineeringsb.com</a></p>
    <div class="btn-row"><a class="btn btn--primary" href="/">Home page</a></div>
  </div>
</section>''' + footer()

def offline_page():
    # Served in place of any page (also /ms/...), so every link and asset path must start at the site root
    html = offline()
    return re.sub(r'((?:src|href|srcset|imagesrcset)=")(?!https?:|/|#|mailto:|tel:|data:)', r"\1/", html).replace(", assets/", ", /assets/")

def write_service_worker():
    core = ["/offline.html", f"/assets/css/styles.css?v={ASSET_V}", f"/assets/js/main.js?v={ASSET_V}",
            "/assets/fonts/source-sans-3-latin.woff2", "/assets/fonts/source-serif-4-700-latin.woff2",
            "/assets/fonts/noto-naskh-arabic-500-jawi.woff2",
            "/assets/logo/logo.svg", "/assets/logo/logo-white.svg", "/assets/logo/favicon.svg"]
    tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sw_template.js"), encoding="utf-8").read()
    write("sw.js", tpl.replace("__VERSION__", ASSET_V).replace("__PRECACHE__", json.dumps(core)))

def notfound():
    return head("404.html", "Page not found | BWS Engineering Sdn Bhd", "The page you were looking for could not be found.").replace('<meta name="robots" content="index, follow">', '<meta name="robots" content="noindex">') + header("") + f'''
<section class="section">
  <div class="container measure">
    {eyebrow("404", "Page not found")}
    <h1>We couldn’t find that page</h1>
    <p class="lead">The link may be out of date. Try one of these instead:</p>
    <div class="btn-row"><a class="btn btn--primary" href="index.html">Home</a><a class="btn btn--ghost" href="services.html">Services</a><a class="btn btn--ghost" href="contact.html">Contact</a></div>
  </div>
</section>''' + footer()

for name, fn in [("index.html", home), ("about.html", about), ("services.html", services), ("clients.html", clients),
                 ("projects.html", projects), ("hse.html", hse), ("careers.html", careers), ("contact.html", contact), ("privacy.html", privacy), ("vendor.html", vendor), ("capability.html", capability), ("offline.html", offline_page), ("404.html", notfound)]:
    write(name, fn())

pages = ["", "about.html", "services.html", "clients.html", "projects.html", "hse.html", "careers.html", "contact.html", "privacy.html", "vendor.html"]
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
      "".join(f"  <url><loc>{SITE}/{p}</loc></url>\n" for p in pages) + "</urlset>\n")
write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
write("site.webmanifest", json.dumps({"name": "BWS Engineering Sdn Bhd", "short_name": "BWS Engineering", "icons": [
    {"src": "assets/logo/icon-192.png", "sizes": "192x192", "type": "image/png"},
    {"src": "assets/logo/icon-512.png", "sizes": "512x512", "type": "image/png"}],
    "theme_color": "#0A1240", "background_color": "#FFFFFF", "display": "browser"}, indent=2))

write_service_worker()

# Bahasa Melayu version (site/ms/) + language switch and hreflang on both versions
import build_ms
build_ms.build()

# Digital business cards (site/card/*.html) are written by hand, not by this script. Their stylesheets and
# script are cached for a year, so give each link a ?v= hash of the file it loads; nothing else is changed.
def stamp_cards():
    card_dir = OUT + "card/"
    if not os.path.isdir(card_dir):
        return
    def ver(m):
        return m.group(1) + "?v=" + _hl.md5(open(OUT + "assets/" + m.group(2), "rb").read()).hexdigest()[:8] + '"'
    for name in sorted(os.listdir(card_dir)):
        if name.endswith(".html"):
            path = card_dir + name
            html = open(path, encoding="utf-8").read()
            new = re.sub(r'(="\.\./assets/((?:css|js)/[\w.-]+\.(?:css|js)))(?:\?v=\w+)?"', ver, html)
            if new != html:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new)

stamp_cards()
