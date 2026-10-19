# Page generator for the BWS static site: writes plain HTML into ../site.
# Optional. If you edit the HTML files by hand, do NOT re-run this (it overwrites them).
import json, os
from urllib.parse import quote

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site") + "/"
SITE = "https://www.bwsengineeringsb.com"
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
    return f'<svg{c} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{P}</svg>'

PANELS = '<span class="panels" aria-hidden="true"><i></i><i></i><i></i></span>'

def eyebrow(num, label):
    # num is ignored: sections are labelled, not numbered
    return f'<p class="eyebrow">{PANELS}{label}</p>'

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
FONT_JAWI = "https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@500&display=swap&text=" + quote(JAWI.replace(" ", ""))

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
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONT_JAWI}">
{preload}<link rel="stylesheet" href="assets/css/styles.css">
<script src="assets/js/main.js" defer></script>
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
        <span class="brand-name">BWS Engineering Sdn Bhd</span>
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
      <h2 id="cta-title">Have a project in mind? Let’s talk.</h2>
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
      <span class="brand-name">BWS Engineering Sdn Bhd</span>
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
      <a class="social" href="https://www.facebook.com/bwsengineeringsdnbhd/" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M13.5 21v-7.5h2.5l.4-3h-2.9V8.6c0-.9.3-1.5 1.5-1.5h1.5V4.4c-.3 0-1.2-.1-2.2-.1-2.2 0-3.7 1.3-3.7 3.8v2.4H8v3h2.6V21z"/></svg>Facebook<span class="visually-hidden"> (opens in a new tab)</span></a>
    </nav>
  </div>
  <div class="container footer-bottom">
    <p>© <span data-year>2026</span> BWS Engineering Sdn Bhd (597192-V). All rights reserved.</p>
    <p>Miri · Bintulu · Sarawak, Malaysia</p>
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

def page_hero(crumb, title, lead, illus, *_unused):
    return f'''
<section class="page-hero on-dark">
  <div class="container page-hero-grid">
    <div class="page-hero-inner">
      <ol class="breadcrumb"><li><a href="index.html">Home</a></li><li aria-current="page">{crumb}</li></ol>
      <h1>{title}</h1>
      <p>{lead}</p>
    </div>
    {illus_panels(illus)}
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
     "BWS provides construction and maintenance services for industrial plants, built on our founders’ many years of experience in the oil and gas industry. Our scope covers oil and gas facilities, power generation plants and wood-based factories, supported from our bases in Miri and Bintulu. Every job is carried out under our HSE policy and our ISO 9001:2015 Quality Management System.",
     ("hero-column-erection", "Crane lifting a process column into position inside its scaffolding during plant construction", 800, 600)),
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
          <tbody data-fl-body>{rows}</tbody>
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
      <li>{icon("badge")}<div>PETRONAS Licensed<span>Valid PETRONAS licence</span></div></li>
      <li>{icon("doc")}<div>CIDB Grade G7<span>Building · Civil · M&amp;E</span></div></li>
      <li>{icon("shield")}<div>ISO 9001 · ISO 45001<span>TÜV NORD · BSI certified</span></div></li>
      <li>{icon("calendar")}<div>Est. 2002<span>Formed October 2002</span></div></li>
      <li>{icon("flag")}<div>Bumiputera Company<span>Wholly owned · CIDB STB certified</span></div></li>
    </ul>
  </div>
</section>'''

# ================================================================ HOME
def home():
    svc_cards = "".join(f'''
      <a class="card card--media" href="services.html#{sid}">
        <div class="card-photo">{img(ph[0], "", ph[2], ph[3], "(min-width: 75rem) 25vw, (min-width: 40rem) 50vw, 100vw")}</div>
        <div class="card-body">
          <span class="card-icon">{icon(ic)}</span>
          <h3>{t}</h3>
          <p>{blurb}</p>
          <span class="link-arrow">View scope</span>
        </div>
      </a>''' for (sid, ic, t, blurb, _sc, _in, ph) in SERVICES)
    work = [("power-import-aerial-1", 675, 520, "Plant · MLNG", "Power Import Project, Bintulu"),
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
        key = logo or n
        if key in brands: brands[key][3].append(n)
        else: brands[key] = (logo, w, h, [n])
    marq = lambda alt: "".join(f'<li>{client_logo(logo, w, h, ", ".join(names) if alt else "")}</li>' for logo, w, h, names in brands.values())
    return head("index.html",
        "BWS Engineering Sdn Bhd | Oil &amp; Gas Construction &amp; Maintenance Contractor, Miri, Sarawak",
        "Bumiputera engineering construction and maintenance contractor for oil &amp; gas, based in Miri and Bintulu, Sarawak since 2002. PETRONAS licensed, CIDB registered, ISO 9001:2015 (TÜV NORD).") + header("index.html") + f'''
<section class="hero on-dark" aria-labelledby="hero-title">
  <div class="container hero-grid">
  <div class="hero-inner">
    <p class="eyebrow">{PANELS} Miri &amp; Bintulu, Sarawak</p>
    <h1 id="hero-title">Engineering, Construction &amp; Maintenance for Oil&nbsp;&amp;&nbsp;Gas, <span class="accent">Since&nbsp;2002.</span></h1>
    <p class="sub">Bumiputera contractor based in Miri &amp; Bintulu, Sarawak. <b>PETRONAS licensed · CIDB registered · ISO 9001:2015.</b></p>
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
      <div class="stat"><dt class="visually-hidden">Years of experience</dt><dd class="mb-0" style="margin:0"><span class="stat-num" data-count="20" data-suffix="+">20+</span><span class="stat-label">Years Experience</span><span class="stat-note">Operating since October 2002</span></dd></div>
      <div class="stat"><dt class="visually-hidden">Operating bases</dt><dd style="margin:0"><span class="stat-num" data-count="2">2</span><span class="stat-label">Operating Bases</span><span class="stat-note">Miri &amp; Bintulu, Sarawak</span></dd></div>
      <div class="stat"><dt class="visually-hidden">Contracts delivered</dt><dd style="margin:0"><span class="stat-num" data-count="80" data-suffix="+">80+</span><span class="stat-label">Contracts Delivered</span><span class="stat-note">Oil &amp; gas, industry and government</span></dd></div>
      <div class="stat"><dt class="visually-hidden">Major clients</dt><dd style="margin:0"><span class="stat-num" data-count="15" data-suffix="+">15+</span><span class="stat-label">Major Clients</span><span class="stat-note">Operators, EPC &amp; industry</span></dd></div>
    </dl>
  </div>
</section>

<section class="section" aria-labelledby="svc-title">
  <div class="container">
    <div class="section-head section-head--split">
      <div>{eyebrow("01", "Services")}<h2 id="svc-title">Four disciplines, one accountable contractor</h2></div>
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
      <h2 id="about-title">A wholly owned Bumiputera contractor, built by people from the industry</h2>
      <p class="lead">BWS Engineering Sdn. Bhd. was formed in October 2002 by a group of Bumiputera with many years of experience in the oil and gas industry, particularly in construction and maintenance services.</p>
      <p>The company is run by its shareholders, who sit on the Board of Directors and in Management, and employs qualified professionals with thorough experience across engineering and construction disciplines.</p>
      <a class="btn btn--ghost mt-5" href="about.html">Read more about us {icon("arrow")}</a>
    </div>
    <figure class="media media--framed ratio-4x3 reveal">
      {img("hse-site-walk", "BWS supervisors in hard hats and coveralls walking a cleared construction site", 577, 564)}
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
      <div>{eyebrow("", "On site")}<h2 id="work-title">Recent work from our teams</h2></div>
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
  <div class="marquee">
    <div class="marquee-track">
      <ul role="list" aria-label="Main clients">{marq(True)}</ul>
      <ul aria-hidden="true">{marq(False)}</ul>
    </div>
  </div>
</section>

<section class="section section--steel" aria-labelledby="fac-title">
  <div class="container">
    <div class="section-head section-head--split">
      <div>{eyebrow("04", "Facilities")}<h2 id="fac-title">Our own workshop and fabrication yard</h2></div>
      <p class="lead">Owning our facilities in Miri and Bintulu means fabrication, storage and preparation stay under our own control.</p>
    </div>
    <div class="grid grid--2 reveal-stagger">
      <article class="facility">
        {img("facility-miri-hq", "BWS Engineering main office and workshop building at Piasau Industrial Estate, Miri", 800, 600, "(min-width: 60rem) 50vw, 100vw", big=True)}
        <div class="facility-body">
          <span class="tag">Miri · Main Office</span>
          <h3>Office, Warehouse &amp; Fabrication Workshop</h3>
          <address>Piasau Industrial Estate Phase III, Miri</address>
          <p class="mb-0">Our own industrial building serves as the main office, warehouse and fabrication workshop for civil, building, structural, mechanical, piping, and electrical &amp; instrumentation work.</p>
        </div>
      </article>
      <article class="facility">
        {img("facility-bintulu-yard", "Entrance to the BWS Engineering fabrication yard at Kidurong Industrial Estate, Bintulu", 800, 800, "(min-width: 60rem) 50vw, 100vw", big=True)}
        <div class="facility-body">
          <span class="tag">Bintulu · Fabrication Yard</span>
          <h3>Kidurong Fabrication Yard</h3>
          <address>Kidurong Industrial Estate, Bintulu</address>
          <ul class="ticks mb-0">
            <li>Offices and covered fabrication shop</li>
            <li>Open fabrication area</li>
            <li>Covered and open storage</li>
            <li>Blasting and painting facilities</li>
            <li>NDT facilities</li>
          </ul>
        </div>
      </article>
    </div>
  </div>
</section>

<section class="hse-banner on-dark" aria-labelledby="hse-title">
  <div class="hero-media">{img("hse-toolbox-talk", "", 1600, 1200, "100vw", big=True)}</div>
  <div class="container hse-banner-inner">
    <div class="reveal">
      {eyebrow("05", "Health, Safety &amp; Environment")}
      <h2 id="hse-title">Safety is a condition of every job, not a line item</h2>
      <p>Health, safety and the environment come first, in our Quality Management System and on every site.</p>
      <a class="btn btn--outline-light mt-5" href="hse.html">Our HSE &amp; Quality commitment {icon("arrow")}</a>
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

<section class="section section--ink" aria-labelledby="obj-title">
  <div class="container measure center" style="margin-inline:auto">
    {eyebrow("02", "Our objective").replace('class="eyebrow"', 'class="eyebrow" style="justify-content:center"')}
    <h2 id="obj-title" class="visually-hidden">Our objective</h2>
    <p style="font-family:var(--font-head);font-size:clamp(1.5rem,1.2rem + 1.6vw,2.5rem);line-height:1.25;color:#fff;margin:0 0 var(--space-4)">“Become one of the major contractors in the construction industry.”</p>
    <p class="mb-0">We look forward to serving you better.</p>
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
    <!-- ORGANISATION CHARTS: structure from the BWS Company Profile (updated 10.26). Roles only, no names. -->
    <figure class="org" aria-labelledby="org-title">
      <div class="org-top">
        <div class="org-node org-node--lead">Managing Director</div>
        <div class="org-staff"><span class="org-staff-line" aria-hidden="true"></span><div class="org-node org-node--staff">HSE Secretary</div></div>
      </div>
      <ul class="org-sections" role="list">
        <li><ol class="org-chain"><li class="org-node org-node--section">Personnel &amp; Administration Section</li><li class="org-node">Personnel &amp; Administration Manager</li><li class="org-node">Administration Support</li><li class="org-split"><span class="org-node org-node--leaf">Miri Office</span><span class="org-node org-node--leaf">Bintulu Office</span></li></ol></li>
        <li><ol class="org-chain"><li class="org-node org-node--section">Account Section</li><li class="org-node">Accounts Manager</li><li class="org-node">Accounts Assistants</li></ol></li>
        <li><ol class="org-chain"><li class="org-node org-node--section">Engineering / Contract Section</li><li class="org-split org-split--sub"><ol class="org-chain"><li class="org-node">Engineering / Project</li><li class="org-node">Project Manager</li><li class="org-node org-node--leaf">Project Team</li></ol><ol class="org-chain"><li class="org-node">Contract / Procurement</li><li class="org-node">Contract Manager</li><li class="org-node org-node--leaf">Procurement</li></ol></li></ol></li>
        <li><ol class="org-chain"><li class="org-node org-node--section">Quality Assurance Section</li><li class="org-node">Quality Management Representative (QMR)</li></ol></li>
        <li><ol class="org-chain"><li class="org-node org-node--section org-node--hse">Health, Safety &amp; Environment Section</li><li class="org-node">HSE Officer</li><li class="org-split"><span class="org-node org-node--leaf">Site Safety Supervisors</span><span class="org-node org-node--leaf">HSE Committee</span></li></ol></li>
      </ul>
    </figure>

    <h3 class="org-subtitle" id="porg-title">Project organisation</h3>
    <p class="small">How BWS staffs a typical project.</p>
    <figure class="org org--project" aria-labelledby="porg-title">
      <div class="org-top"><div class="org-node org-node--lead">Project Manager</div></div>
      <ul class="org-sections" role="list" style="--cols: 6">
        <li><ol class="org-chain"><li class="org-node org-node--section">Engineering Design</li><li class="org-node org-node--leaf">Consultant</li></ol></li>
        <li><ol class="org-chain"><li class="org-node org-node--section">Quantity Surveyor</li><li class="org-node">Material Coordinator</li></ol></li>
        <li><ol class="org-chain"><li class="org-node org-node--section">Planning &amp; Measurement Engineers</li><li class="org-node">Document Controller</li></ol></li>
        <li><ol class="org-chain"><li class="org-node org-node--section">Construction Superintendent</li><li class="org-node">Construction Engineers</li><li class="org-node">Construction Supervisor</li><li class="org-node org-node--leaf">Civil &amp; Structural · Mechanical &amp; Piping · E&amp;I teams</li></ol></li>
        <li><ol class="org-chain"><li class="org-node org-node--section">QA/QC Engineer</li><li class="org-node">QA/QC Inspectors</li></ol></li>
        <li><ol class="org-chain"><li class="org-node org-node--section org-node--hse">HSE Manager</li><li class="org-node">Site Safety Supervisors</li></ol></li>
      </ul>
    </figure>
  </div>
</section>

<section class="section section--tint" aria-labelledby="lic-title">
  <div class="container">
    <div class="section-head">{eyebrow("05", "Licences &amp; certification")}<h2 id="lic-title">Licensed, registered and certified</h2></div>
    <div class="grid grid--3 reveal-stagger">
      <div class="card"><span class="card-icon">{icon("badge")}</span><h3>PETRONAS &amp; PETROS</h3><p class="mb-0">PETRONAS licensed since 2004 for onshore pipeline, fabrication, inspection and repair work, and a registered vendor of Petroleum Sarawak (PETROS).</p></div>
      <div class="card"><span class="card-icon">{icon("doc")}</span><h3>CIDB Grade G7</h3><p class="mb-0">Registered with CIDB since 2003 at Grade G7, the highest grade, in Building, Civil Engineering and Mechanical &amp; Electrical. Registration no. 0120030415-SR082502. <a href="hse.html#cert-title">Details</a></p></div>
      <div class="card"><span class="card-icon">{icon("shield")}</span><h3>ISO 9001 &amp; ISO 45001</h3><p class="mb-0">Quality management certified by TÜV NORD since 2007, and occupational health &amp; safety management certified by BSI since 2024. <a href="hse.html#quality">Details</a></p></div>
    </div>
  </div>
</section>
{CTA}''' + footer()

# ================================================================ SERVICES
def services():
    nav = "".join(f'<li><a href="#{sid}">{t}</a></li>' for sid, _i, t, *_ in SERVICES)
    secs = ""
    for i, (sid, ic, t, blurb, scope, intro, photo) in enumerate(SERVICES, 1):
        key, alt, w, h = photo
        scope_li = "".join(f"<li>{s}</li>" for s in scope)
        rel = [p for p in PROJECTS if sid in p[5]][:5]
        related_html = ("" if not rel else
            '<div class="related"><h3 class="related-title">Selected projects</h3><ul class="related-list" role="list">'
            + "".join(f'<li><span>{p[0]}</span>{p[2]} <em>· {p[1]}</em></li>' for p in rel) + '</ul><a class="link-arrow" href="projects.html#track">All key projects</a></div>')
        secs += f'''
<section class="service" id="{sid}" aria-labelledby="{sid}-title">
  <div class="container service-grid">
    <div>
      <div class="service-head"><span class="card-icon">{icon(ic)}</span><h2 id="{sid}-title">{t}</h2></div>
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
      <div>{eyebrow("", "Plant &amp; equipment")}<h2 id="equip-title">Our own fleet and tools</h2></div>
      <p class="lead">Owning our lifting, welding and testing equipment keeps schedules in our hands. Highlights from our equipment list:</p>
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
      <div>{eyebrow("01", "Clients")}<h2 id="cl-title">Who we work for</h2></div>
    </div>
    {client_grid()}
  </div>
</section>

<section class="section section--steel" aria-labelledby="why-title">
  <div class="container">
    <div class="section-head">{eyebrow("02", "What clients get")}<h2 id="why-title">What our clients can rely on</h2></div>
    <div class="grid grid--3 reveal-stagger">
      <div class="card"><span class="card-icon">{icon("shield")}</span><h3>Safety first</h3><p class="mb-0">No work starts or continues without ensuring a safe and healthy workplace and protection of the environment.</p></div>
      <div class="card"><span class="card-icon">{icon("badge")}</span><h3>Certified quality</h3><p class="mb-0">An ISO 9001:2015 Quality Management System, certified by TÜV NORD and continually improved.</p></div>
      <div class="card"><span class="card-icon">{icon("factory")}</span><h3>Our own facilities</h3><p class="mb-0">A workshop in Miri and a fabrication yard with blasting, painting and NDT facilities in Bintulu.</p></div>
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
    ("mech", "ill:blasting-painting", 800, 600, "Blasting and painting", "Illustration: a steel beam being spray painted after blasting"),
    ("civil", "civil-rebar", 800, 460, "Foundation reinforcement", "Construction crew tying reinforcement steel for a foundation"),
    ("civil", "civil-foundation-slab", 800, 488, "Concrete foundation slab", "Large concrete slab with formwork and an excavator at the edge of the site"),
    ("civil", "civil-excavation-formwork", 800, 563, "Excavation and formwork", "Excavator working beside timber formwork in an excavation"),
    ("civil", "civil-concrete-finishing", 800, 481, "Concrete finishing", "Workers in coveralls and boots finishing a concrete surface"),
    ("civil", "civil-drainage", 640, 480, "Drainage works", "Drainage channel under construction along a slope"),
    ("civil", "building-scaffold", 800, 600, "Building construction", "Two-storey building wrapped in scaffolding beside a container yard"),
    ("civil", "building-interior", 800, 534, "Building fit-out", "Interior of a building under fit-out with steel roof structure"),
    ("ei", "ei-switchgear", 800, 599, "Switchgear installation", "Row of electrical switchgear panels in a substation room"),
    ("ei", "ill:cable-laying", 800, 600, "Cable laying and testing", "Illustration: a cable drum paying out cable into a trench, with an insulation tester"),
    ("ei", "ill:instrument-calibration", 800, 600, "Instrument calibration", "Illustration: a pressure transmitter calibrated on a bench against a reference gauge"),
    ("hse", "hse-toolbox-talk", 800, 600, "Toolbox talk", "Workers seated under a site tent for a safety briefing"),
    ("hse", "hse-site-walk", 577, 564, "Site inspection", "Supervisors in hard hats walking a cleared site"),
    ("hse", "hse-fire-drill", 800, 600, "Fire extinguisher drill", "Crew in coveralls and hard hats during a fire extinguisher drill"),
]
CATS = [("all", "All"), ("plant", "Plant"), ("mech", "Mechanical &amp; Piping"), ("civil", "Civil &amp; Structural"),
        ("ei", "Electrical &amp; Instrumentation"), ("hse", "HSE")]
CATNAME = dict(CATS)

def projects():
    cnt = lambda k: len(GALLERY) if k == "all" else sum(1 for g in GALLERY if g[0] == k)
    btns = "".join(f'<button class="filter-btn" type="button" data-filter="{k}" aria-pressed="{str(k == "all").lower()}">{v}<span class="count">({cnt(k)})</span></button>' for k, v in CATS)
    lis = ""
    for cat, key, w, h, title, alt in GALLERY:
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
def hse():
    return head("hse.html", "HSE &amp; Quality | ISO 9001:2015 | BWS Engineering Sdn Bhd",
        "BWS Engineering’s HSE, Quality, Anti-Corruption and Sustainability policies. ISO 9001:2015 (TÜV NORD) and ISO 45001:2018 (BSI) certified, with national OSH awards.") + header("hse.html") + page_hero(
        "HSE &amp; Quality", "Health, safety, environment and quality",
        "No work shall commence or continue without ensuring a safe and healthy workplace and protection of the environment.",
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
          <span class="cert-seal" aria-hidden="true">{icon("shield")}</span>
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
          <span class="cert-seal cert-seal--safety" aria-hidden="true">{icon("hat")}</span>
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
          <span class="cert-seal" aria-hidden="true">{icon("doc")}</span>
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
          <span class="cert-seal" aria-hidden="true">{icon("badge")}</span>
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
    <ul class="reg-list" role="list">
      <li><strong>PETROS</strong><span>Registered vendor of Petroleum Sarawak Berhad and its group, valid to Dec 2028: building &amp; structure construction, onshore maintenance &amp; modification, onshore pipeline fabrication &amp; construction</span></li>
      <li><strong>DOSH</strong><span>Registered Competent Firm (Petroleum Contractor): KPD 01 onshore pipelines and KPD 02 onshore reticulation piping, valid to Mar 2028</span></li>
      <li><strong>UPKJ Sarawak</strong><span>Class A registered contractor with the Sarawak State Financial Secretary, and recognised as a Rescue Contractor for works and mechanical fields</span></li>
      <li><strong>MOF</strong><span>Ministry of Finance registered supplier, valid to Mar 2027</span></li>
      <li><strong>CIDB SCORE</strong><span>3-star rating for 2025 from CIDB and SME Corp: good management and technical capability</span></li>
      <li><strong>SSM</strong><span>Company no. 200201029529 (597192-V), incorporated 29 October 2002</span></li>
    </ul>
    <details class="reg-detail">
      <summary>Registration details for procurement teams</summary>
      <dl class="reg-codes">
        <div><dt>CIDB G7 specialisations: Building</dt><dd>B01 · B02 · B04 · B05 · B12</dd></div>
        <div><dt>CIDB G7 specialisations: Civil Engineering</dt><dd>CE01 · CE02 · CE03 · CE09 · CE20 · CE21 · CE36 · CE41</dd></div>
        <div><dt>CIDB G7 specialisations: Mechanical &amp; Electrical</dt><dd>E03 · E05 · E06 · E10 · E11 · E16 · E32 · M01 · M02 · M12 · M14 · M15 · M20 · M21</dd></div>
        <div><dt>PETRONAS licence codes</dt><dd>15141911S non-metallic piping · 15141700S onshore pipeline · 27131100S onshore pipeline inspection &amp; repair · 24241010S cleaning, repair &amp; maintenance · 27111000S minor onshore fabrication · 11141700S slope protection · 15141610S major fabrication · 15141910S metallic piping (carbon &amp; stainless steel)</dd></div>
        <div><dt>PETROS work categories</dt><dd>SB200001 building &amp; structure construction · SO100005 onshore maintenance, construction &amp; modification (minor onshore fabrication) · SK500007 onshore pipeline fabrication &amp; construction</dd></div>
        <div><dt>MOF supply / service fields</dt><dd>020101 furniture &amp; fittings · 080101 civil engineering, construction &amp; public amenities equipment · 220502 maintenance &amp; repair of containers and tanks · 220503 electrical systems and equipment · 220506 fuel tank repair · 220507 pumps, water pipes &amp; components</dd></div>
        <div><dt>DOSH competent firm scope</dt><dd>KPD 01 onshore pipeline · KPD 02 onshore reticulation piping (registration JKKP/2022/26/76)</dd></div>
        <div><dt>UPKJ Sarawak</dt><dd>Certificate UPKJ/W/021609 · Class A · Rescue Contractor for the works and mechanical fields (2026)</dd></div>
      </dl>
    </details>
  </div>
</section>

<section class="section section--ink" id="awards" aria-labelledby="awards-title">
  <div class="container">
    <div class="section-head section-head--split">
      <div>{eyebrow("", "Recognition")}<h2 id="awards-title">Awards &amp; recognition</h2></div>
      <p class="lead">Recognised by government, industry and our clients for safety performance and quality of work.</p>
    </div>
    <!-- AWARDS: from the BWS Company Profile (Oct 2026), "List of Awards". -->
    <ul class="award-grid reveal-stagger" role="list">
      <li class="award award--lead"><span class="award-year">2025</span><h3>PSIEA Silver Award</h3><p>Premier of Sarawak Industry Excellence Awards, Large Enterprise category.</p></li>
      <li class="award award--lead"><span class="award-year">2023</span><h3>National OSH Award</h3><p>Anugerah Keselamatan dan Kesihatan Pekerjaan Negara 2023, for the OSH management system at the workplace.</p></li>
      <li class="award award--lead"><span class="award-year">2023</span><h3>MSOSH Gold Class 1 Award</h3><p>Malaysian Society for Occupational Safety and Health, for very good OSH performance on the MLNG Power Import Project (Transgrid-BWS JV).</p></li>
      <li class="award"><span class="award-year">2023</span><h3>PTTEP CEO SSHE Excellence Award</h3><p>For safety, security, health and environment performance excellence.</p></li>
      <li class="award"><span class="award-year">2023</span><h3>Samsung E&amp;A appreciation</h3><p>For contribution to the National OSH Award by NCOSH on the Rosmari-Marjoram Onshore Gas Plant Project.</p></li>
      <li class="award"><span class="award-year">2022</span><h3>IRSO West Coast Mega HSE Council</h3><p>Top 5 Best Project HSE Performance, Sabah Sarawak Gas Pipeline KP220 &amp; KP265.</p></li>
      <li class="award"><span class="award-year">2022</span><h3>PETRONAS certificate of appreciation</h3><p>Successful completion of the mechanical scope, 30" SSGP pipeline replacement at KP220.</p></li>
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
      <div class="callout-safety"><strong>Stop and check.</strong> Under our HSE policy, safety, health and the environment are considered before any job starts and throughout the work.</div>
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
      <h2 id="work-title">Working with experienced people</h2>
      <p class="lead">BWS employs qualified professionals with thorough experience in various engineering and construction disciplines, working from our main office and workshop in Miri and our fabrication yard in Bintulu.</p>
      <p>Our work spans industrial plant construction and maintenance, mechanical and piping, civil and structural steel, and electrical and instrumentation, for some of the region’s major oil and gas operators and EPC contractors.</p>
    </div>
    <aside class="callout-safety" aria-labelledby="safe-title">
      <span class="safety-tag">{icon("hat")} Safety-first culture</span>
      <h3 id="safe-title" style="font-size:1.2rem">Everyone goes home safe</h3>
      <p class="mb-0">No work shall commence or continue without ensuring a safe and healthy workplace and protection of the environment, and every member of the team is expected to uphold that.</p>
    </aside>
  </div>
</section>

<section class="section section--steel" id="apply" aria-labelledby="apply-title">
  <div class="container">
    <div class="apply-card">
      <div>
        {eyebrow("", "Join us")}
        <h2 id="apply-title">Send your CV</h2>
        <p class="lead">We welcome applications from experienced engineering and construction professionals. Email your CV and certificates to our recruitment team, and tell us the position or discipline you’re applying for.</p>
        <p class="apply-address">{icon("mail")}<a href="mailto:bwsesbhr@gmail.com">bwsesbhr@gmail.com</a></p>
      </div>
      <div class="apply-actions">
        <p class="small">Choose how to send. Each option opens a new email to our recruitment team with the subject already filled in.</p>
        {compose_links("bwsesbhr@gmail.com", "Job Application – [Position]", cv_body)}
      </div>
    </div>
  </div>
</section>
{CTA}''' + footer()

# ================================================================ CONTACT
# Exact pins: coordinates and listings of BWS's own Google Maps business entries (verified Oct 2026).
MIRI_LL, BTU_LL = "4.446917,114.011563", "3.2724729,113.0802423"
MIRI_PLACE = "https://www.google.com/maps/place/Bws+Engineering+Sdn.+Bhd./@4.446917,114.011563,17z/data=!4m6!3m5!1s0x321f4eff4ad03523:0x3a7d83606d409313!8m2!3d4.446917!4d114.011563"
BTU_PLACE = "https://www.google.com/maps/place/BWS+Engineering+Sdn.+Bhd./@3.2724729,113.0802423,17z/data=!4m6!3m5!1s0x321dc31223ffffff:0x53e0ada3f9e5e7f2!8m2!3d3.2724729!4d113.0802423"

def maps_embed(ll):
    return f"https://maps.google.com/maps?q={ll}&z=17&hl=en&output=embed"

def contact():
    miri_q = "Lot 1743, Block 3 MCLD, Piasau Industrial Estate Phase III, Jalan Prunus 1, 98000 Miri, Sarawak"
    btu_q = "Lot 782, Block 20, Kemena Land District, Jalan Tanjung Kidurong, 97007 Bintulu, Sarawak"
    opts = "".join(f'<option value="{t.replace("&amp;", "&")}" data-key="{sid}">{t}</option>' for sid, _i, t, *_ in SERVICES)
    ld = [{"@context": "https://schema.org", "@type": "ContactPage", "url": SITE + "/contact.html", "about": {"@id": SITE + "/#organization"}}]
    return head("contact.html", "Contact Us | Miri &amp; Bintulu Offices | BWS Engineering Sdn Bhd",
        "Contact BWS Engineering Sdn Bhd. Main office and workshop in Piasau Industrial Estate, Miri (085-652743) and fabrication yard in Kidurong, Bintulu (086-252476). Email bwsesb@gmail.com.", ld) + header("contact.html") + page_hero(
        "Contact", "Contact us",
        "Talk to our Miri or Bintulu office, or send an enquiry and we’ll route it to the right team.",
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
        <div class="map-wrap"><iframe class="map" src="{maps_embed(MIRI_LL)}" title="Map: BWS Engineering main office, Piasau Industrial Estate, Miri" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div>
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
        <div class="map-wrap"><iframe class="map" src="{maps_embed(BTU_LL)}" title="Map: BWS Engineering fabrication yard, Kidurong, Bintulu" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div>
      </article>
    </div>
  </div>
</section>

<section class="section section--steel" id="enquiry" aria-labelledby="form-title">
  <div class="container split split--wide-text" style="align-items:start">
    <div>
      {eyebrow("02", "Enquiry")}
      <h2 id="form-title">Request a quote or send an enquiry</h2>
      <!-- CONTACT FORM: replace YOUR_FORM_ID in the action below with your Formspree form ID
           (https://formspree.io → New form → copy the endpoint). Until then the form opens
           the visitor's email app with the message pre-filled, addressed to data-mailto. -->
      <form class="form" action="https://formspree.io/f/YOUR_FORM_ID" method="POST" data-contact-form data-mailto="bws@bwsengineeringsb.com">
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
        <p class="form-note mb-0"><span aria-hidden="true">*</span> Required fields.</p>
        <div><button class="btn btn--primary" type="submit">Send enquiry {icon("arrow")}</button></div>
        <div class="form-status" role="status" aria-live="polite" hidden></div>
      </form>
    </div>
    <aside class="card" aria-labelledby="direct-title" style="margin-top:var(--space-6)">
      <h3 id="direct-title">Prefer to email directly?</h3>
      <ul class="contact-list" role="list">
        <li>{icon("mail")}<span>General enquiries<br><a href="mailto:bws@bwsengineeringsb.com">bws@bwsengineeringsb.com</a><br><a href="mailto:bwsesb@gmail.com">bwsesb@gmail.com</a></span></li>
        <li>{icon("briefcase")}<span>Job applications<br><a href="mailto:bwsesbhr@gmail.com">bwsesbhr@gmail.com</a></span></li>
        <li>{icon("phone")}<span>Miri <a href="tel:+6085652743">085-652743</a><br>Bintulu <a href="tel:+6086252476">086-252476</a></span></li>
      </ul>
    </aside>
  </div>
</section>
''' + footer()

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
                 ("projects.html", projects), ("hse.html", hse), ("careers.html", careers), ("contact.html", contact), ("404.html", notfound)]:
    write(name, fn())

pages = ["", "about.html", "services.html", "clients.html", "projects.html", "hse.html", "careers.html", "contact.html"]
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
      "".join(f"  <url><loc>{SITE}/{p}</loc></url>\n" for p in pages) + "</urlset>\n")
write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
write("site.webmanifest", json.dumps({"name": "BWS Engineering Sdn Bhd", "short_name": "BWS Engineering", "icons": [
    {"src": "assets/logo/icon-192.png", "sizes": "192x192", "type": "image/png"},
    {"src": "assets/logo/icon-512.png", "sizes": "512x512", "type": "image/png"}],
    "theme_color": "#0A1240", "background_color": "#FFFFFF", "display": "browser"}, indent=2))

# Bahasa Melayu version (site/ms/) + language switch and hreflang on both versions
import sys as _sys
_sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_ms
build_ms.build()
