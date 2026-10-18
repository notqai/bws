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
    "email": "bwsesb@gmail.com",
    "telephone": "+60-85-652743",
    "faxNumber": "+60-85-652709",
    "areaServed": "Malaysia",
    "knowsAbout": ["Industrial plant construction and maintenance", "Mechanical and piping work",
                   "Civil, building and structural steel construction", "Electrical and instrumentation work"],
    "address": {"@type": "PostalAddress", "streetAddress": "Lot 1743, Block 3 MCLD, Piasau Industrial Estate Phase III, Jalan Prunus 1",
                "addressLocality": "Miri", "postalCode": "98000", "addressRegion": "Sarawak", "addressCountry": "MY"},
    "subOrganization": [
        {"@type": "LocalBusiness", "@id": SITE + "/#miri", "name": "BWS Engineering Sdn Bhd: Main Office cum Workshop (Miri)",
         "image": SITE + "/assets/img/facility-miri-hq-1600.webp", "telephone": "+60-85-652743", "faxNumber": "+60-85-652709", "email": "bwsesb@gmail.com",
         "address": {"@type": "PostalAddress", "streetAddress": "Lot 1743, Block 3 MCLD, Piasau Industrial Estate Phase III, Jalan Prunus 1",
                     "addressLocality": "Miri", "postalCode": "98000", "addressRegion": "Sarawak", "addressCountry": "MY"}},
        {"@type": "LocalBusiness", "@id": SITE + "/#bintulu", "name": "BWS Engineering Sdn Bhd: Bintulu Office cum Fabrication Yard",
         "image": SITE + "/assets/img/facility-bintulu-yard-1600.webp", "telephone": "+60-86-252476", "email": "bwsesb@gmail.com",
         "address": {"@type": "PostalAddress", "streetAddress": "Lot 782, Block 20, Kemena Land District, Jalan Tanjung Kidurong",
                     "addressLocality": "Bintulu", "postalCode": "97007", "addressRegion": "Sarawak", "addressCountry": "MY"}},
    ],
}

HEROES = {"index.html": "hero-column-erection", "about.html": "facility-miri-hq", "services.html": "mech-heavy-lift",
          "clients.html": "plant-tanks-piping", "projects.html": "civil-rebar", "hse.html": "hse-fire-drill",
          "careers.html": "civil-concrete-finishing", "contact.html": "facility-bintulu-yard"}

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
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
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
    <p class="mobile-menu-contact">Miri <a href="tel:+6085652743">085-652743</a> · Bintulu <a href="tel:+6086252476">086-252476</a><br><a href="mailto:bwsesb@gmail.com">bwsesb@gmail.com</a></p>
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
          <li>Enquiries: <a href="mailto:bwsesb@gmail.com">bwsesb@gmail.com</a></li>
          <li>Careers: <a href="mailto:bwsesbhr@gmail.com">bwsesbhr@gmail.com</a></li>
        </ul>
      </div>
    </div>
    <nav aria-label="Footer">
      <h2>Quick links</h2>
      <ul>{links}</ul>
    </nav>
  </div>
  <div class="container footer-bottom">
    <p>© <span data-year>2026</span> BWS Engineering Sdn Bhd. All rights reserved.</p>
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

def page_hero(crumb, title, lead, photo, alt, w, h):
    return f'''
<section class="page-hero on-dark">
  <div class="container page-hero-grid">
    <div class="page-hero-inner">
      <ol class="breadcrumb"><li><a href="index.html">Home</a></li><li aria-current="page">{crumb}</li></ol>
      <h1>{title}</h1>
      <p>{lead}</p>
    </div>
    {panels(photo, w, h, "(min-width: 60rem) 40vw, 100vw", cls="bws-panels--page")}
  </div>
</section>'''

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
     ("civil-rebar", "Construction crew in coveralls tying reinforcement steel for a foundation, with an excavator behind", 800, 541)),
    ("electrical", "ei", "Electrical and Instrumentation Work",
     "Cable laying, equipment installation, instrument calibration and testing, and commissioning assistance.",
     ["Cable laying and testing", "Electrical equipment installation and testing", "Instrument calibration, installation and testing", "Commissioning assistance"],
     "Our electrical and instrumentation team carries out cable laying and testing, and the installation and testing of electrical equipment. We calibrate, install and test instruments, and provide commissioning assistance to help bring systems safely into service.",
     ("ei-switchgear", "Row of electrical switchgear panels installed in a substation room", 800, 599)),
]

# (name, logo file in assets/img/clients/, intrinsic width, height, note)
# Logos are the clients' current brand marks (PETRONAS subsidiaries use the group mark).
CLIENTS = [
    ("Malaysia LNG Sdn Bhd", "petronas.svg", 544, 558, "PETRONAS Group"),
    ("PETRONAS Carigali Sdn Bhd", "petronas.svg", 544, 558, ""),
    ("PETRONAS Dagangan Berhad", "petronas.svg", 544, 558, ""),
    ("JX Nippon Oil &amp; Gas Exploration (M) Ltd", "eneos-xplora.webp", 640, 91, "Now ENEOS Xplora"),
    ("ASEAN Bintulu Fertilizer Sdn Bhd", "abf.webp", 150, 97, ""),
    ("PT Rekayasa Industri", "rekind.webp", 360, 404, "Rekind"),
    ("Sarawak Shell Berhad &amp; Sabah Shell Petroleum Co. Ltd", "shell.svg", 150, 139, ""),
    ("JGC Corporation", "jgc.svg", 373, 202, ""),
    ("Chiyoda Malaysia Sdn Bhd", "chiyoda.svg", 201, 64, ""),
    ("Mitsui &amp; Co. Ltd", "mitsui.svg", 512, 636, ""),
    ("Taihei Dengyo Kaisha, Ltd", "taihei-dengyo.webp", 122, 90, ""),
]

def client_logo(logo, w, h, alt=""):
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
      <li>{icon("doc")}<div>CIDB Registered<span>Various construction categories</span></div></li>
      <li>{icon("shield")}<div>ISO 9001:2015<span>Certified by TÜV NORD</span></div></li>
      <li>{icon("calendar")}<div>Est. 2002<span>Formed October 2002</span></div></li>
      <li>{icon("flag")}<div>Bumiputera Company<span>Wholly owned</span></div></li>
    </ul>
  </div>
</section>'''

# ================================================================ HOME
def home():
    svc_cards = "".join(f'''
      <a class="card card--media" href="services.html#{sid}">
        <span class="card-photo">{img(ph[0], "", ph[2], ph[3], "(min-width: 75rem) 25vw, (min-width: 40rem) 50vw, 100vw")}</span>
        <span class="card-body">
          <span class="card-icon">{icon(ic)}</span>
          <h3>{t}</h3>
          <p>{blurb}</p>
          <span class="link-arrow">View scope</span>
        </span>
      </a>''' for (sid, ic, t, blurb, _sc, _in, ph) in SERVICES)
    marq = lambda alt: "".join(f'<li>{client_logo(logo, w, h, n if alt else "")}</li>' for n, logo, w, h, _ in CLIENTS)
    return head("index.html",
        "BWS Engineering Sdn Bhd | Oil &amp; Gas Construction &amp; Maintenance Contractor, Miri, Sarawak",
        "Bumiputera engineering construction and maintenance contractor for oil &amp; gas, based in Miri and Bintulu, Sarawak since 2002. PETRONAS licensed, CIDB registered, ISO 9001:2015 (TÜV NORD).") + header("index.html") + f'''
<section class="hero on-dark" aria-labelledby="hero-title">
  <div class="container hero-grid">
  <div class="hero-inner">
    <p class="eyebrow">{PANELS} Miri &amp; Bintulu, Sarawak</p>
    <h1 id="hero-title">Engineering, Construction &amp; Maintenance for Oil &amp; Gas, <span class="accent">Since 2002.</span></h1>
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
      <div class="stat"><dt class="visually-hidden">Core disciplines</dt><dd style="margin:0"><span class="stat-num" data-count="4">4</span><span class="stat-label">Core Disciplines</span><span class="stat-note">Plant · Mechanical · Civil · E&amp;I</span></dd></div>
      <div class="stat"><dt class="visually-hidden">Major clients</dt><dd style="margin:0"><span class="stat-num" data-count="10" data-suffix="+">10+</span><span class="stat-label">Major Clients</span><span class="stat-note">Operators, EPC &amp; industry</span></dd></div>
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
      <p>“No job shall start or continue without due regard to Safety, Health and Environment.”</p>
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
        "facility-miri-hq", "", 1600, 1200) + f'''

<section class="section" aria-labelledby="profile-title">
  <div class="container split split--wide-text">
    <div>
      {eyebrow("01", "Company profile")}
      <h2 id="profile-title">Who we are</h2>
      <p class="lead">BWS Engineering Sdn. Bhd. is a wholly owned Bumiputera company whose core business is engineering construction and maintenance services for the oil and gas industries.</p>
      <p>The company was formed in October 2002 by a group of Bumiputera with many years of experience in the oil and gas industry, particularly in construction and maintenance services.</p>
      <p>The company is run by its shareholders, who are members of the Board of Directors and Management. It also employs qualified professionals with thorough experience in various engineering and construction disciplines.</p>
    </div>
    <div>
      <dl class="facts reveal-stagger">
        <div><dt>Formed</dt><dd>October 2002</dd></div>
        <div><dt>Ownership</dt><dd>Wholly owned Bumiputera</dd></div>
        <div><dt>Bases</dt><dd>Miri &amp; Bintulu, Sarawak</dd></div>
        <div><dt>Quality</dt><dd>ISO 9001:2015 · TÜV NORD</dd></div>
        <div><dt>Licensing</dt><dd>PETRONAS licensed · CIDB registered</dd></div>
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
    <div class="section-head section-head--split">
      <div>{eyebrow("04", "Organisation")}<h2 id="org-title">Organisation chart</h2></div>
      <p class="lead">Led by shareholders who serve on the Board of Directors and in Management.</p>
    </div>
    <!-- PLACEHOLDER ORG CHART: replace the boxes below with the real structure,
         or swap the whole <div class="org"> for an image:
         <img src="assets/img/org-chart.webp" alt="BWS Engineering organisation chart" width="1600" height="900" loading="lazy"> -->
    <div class="org" role="img" aria-label="Organisation chart placeholder: Board of Directors, Management, and departments to be confirmed">
      <div class="org-row"><div class="org-node">Board of Directors<span>Shareholders</span></div></div>
      <div class="org-line"></div>
      <div class="org-row"><div class="org-node">Management<span>Shareholders</span></div></div>
      <div class="org-line"></div>
      <div class="org-row">
        <div class="org-node" style="border-style:dashed">[Department]<span>To be supplied</span></div>
        <div class="org-node" style="border-style:dashed">[Department]<span>To be supplied</span></div>
        <div class="org-node" style="border-style:dashed">[Department]<span>To be supplied</span></div>
        <div class="org-node" style="border-style:dashed">[Department]<span>To be supplied</span></div>
      </div>
    </div>
  </div>
</section>

<section class="section section--tint" aria-labelledby="lic-title">
  <div class="container">
    <div class="section-head">{eyebrow("05", "Licences &amp; certification")}<h2 id="lic-title">Licensed, registered and certified</h2></div>
    <div class="grid grid--3 reveal-stagger">
      <div class="card"><span class="card-icon">{icon("badge")}</span><h3>PETRONAS Licence</h3><p class="mb-0">BWS holds a valid PETRONAS licence.</p></div>
      <div class="card"><span class="card-icon">{icon("doc")}</span><h3>CIDB Registration</h3><p class="mb-0">Registered with the Construction Industry Development Board (CIDB) for various categories of construction activities.</p></div>
      <div class="card"><span class="card-icon">{icon("shield")}</span><h3>ISO 9001:2015</h3><p class="mb-0">Quality Management System certified by TÜV NORD. <a href="hse.html#quality">Quality policy</a></p></div>
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
        secs += f'''
<section class="service" id="{sid}" aria-labelledby="{sid}-title">
  <div class="container service-grid">
    <div>
      <div class="service-head"><span class="card-icon">{icon(ic)}</span><h2 id="{sid}-title">{t}</h2></div>
      <p class="lead">{intro}</p>
      <h3 class="visually-hidden">Scope</h3>
      <ul class="scope reveal-stagger" role="list">{scope_li}</ul>
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
        "Four core disciplines delivered from our Miri workshop and Bintulu fabrication yard.",
        "mech-heavy-lift", "", 1600, 1200) + f'''
<nav class="service-nav" aria-label="Services on this page"><div class="container"><ul>{nav}</ul></div></nav>
{secs}
{CTA}''' + footer()

# ================================================================ CLIENTS
def clients():
    return head("clients.html", "Clients | BWS Engineering Sdn Bhd",
        "BWS Engineering’s main clients include Malaysia LNG, PETRONAS Carigali, PETRONAS Dagangan, Sarawak Shell, JGC, Chiyoda and other oil &amp; gas operators and EPC contractors.") + header("clients.html") + page_hero(
        "Clients", "Our main clients",
        "Oil and gas operators, EPC contractors and industrial companies have trusted BWS with construction and maintenance work since 2002.",
        "plant-tanks-piping", "", 800, 532) + f'''

<section class="section" aria-labelledby="cl-title">
  <div class="container">
    <div class="section-head section-head--split">
      <div>{eyebrow("01", "Clients")}<h2 id="cl-title">Who we work for</h2></div>
      <p class="lead">Listed in no particular order.</p>
    </div>
    {client_grid()}
  </div>
</section>

<section class="section section--steel" aria-labelledby="why-title">
  <div class="container">
    <div class="section-head">{eyebrow("02", "What clients get")}<h2 id="why-title">What our clients can rely on</h2></div>
    <div class="grid grid--3 reveal-stagger">
      <div class="card"><span class="card-icon">{icon("shield")}</span><h3>Safety first</h3><p class="mb-0">No job starts or continues without due regard to Safety, Health and Environment.</p></div>
      <div class="card"><span class="card-icon">{icon("badge")}</span><h3>Certified quality</h3><p class="mb-0">An ISO 9001:2015 Quality Management System, certified by TÜV NORD and continually improved.</p></div>
      <div class="card"><span class="card-icon">{icon("factory")}</span><h3>Our own facilities</h3><p class="mb-0">A workshop in Miri and a fabrication yard with blasting, painting and NDT facilities in Bintulu.</p></div>
    </div>
  </div>
</section>
{CTA}''' + footer()

# ================================================================ PROJECTS
GALLERY = [
    # (category, image key, w, h, title, alt) or (category, None, ..., placeholder text)
    ("plant", "hero-column-erection", 800, 600, "Process column erection", "Crane lifting a process column into position inside its scaffolding"),
    ("plant", "plant-tanks-piping", 800, 532, "Storage tanks and piping", "White storage tanks with yellow piping and access stairways"),
    ("plant", "plant-firewater-tank", 800, 532, "Firewater tank and pump shelter", "Firewater tank and green-roofed pump shelter at a facility"),
    ("mech", "mech-heavy-lift", 800, 600, "Heavy lift of a vessel", "Mobile crane lifting a large cylindrical vessel on site"),
    ("mech", "mech-pump-skid", 448, 336, "Pump installation", "Electric pump and pipework installed on a skid"),
    ("mech", "piping-spool", 448, 336, "Large-bore piping", "Large-bore white piping with flanged connections"),
    ("mech", "mech-container-unloading", 800, 554, "Material receiving", "Crew in PPE unloading materials from a shipping container"),
    ("mech", None, 0, 0, "Blasting and painting", "Blasting and painting work at the Bintulu yard"),
    ("civil", "civil-rebar", 800, 541, "Foundation reinforcement", "Construction crew tying reinforcement steel for a foundation"),
    ("civil", "civil-foundation-slab", 800, 555, "Concrete foundation slab", "Large concrete slab with formwork and an excavator at the edge of the site"),
    ("civil", "civil-excavation-formwork", 800, 563, "Excavation and formwork", "Excavator working beside timber formwork in an excavation"),
    ("civil", "civil-concrete-finishing", 800, 554, "Concrete finishing", "Workers in coveralls and boots finishing a concrete surface"),
    ("civil", "civil-drainage", 640, 480, "Drainage works", "Drainage channel under construction along a slope"),
    ("civil", "building-scaffold", 800, 600, "Building construction", "Two-storey building wrapped in scaffolding beside a container yard"),
    ("civil", "building-interior", 800, 600, "Building fit-out", "Interior of a building under fit-out with steel roof structure"),
    ("ei", "ei-switchgear", 800, 599, "Switchgear installation", "Row of electrical switchgear panels in a substation room"),
    ("ei", None, 0, 0, "Cable laying and testing", "Cable laying or termination work on site"),
    ("ei", None, 0, 0, "Instrument calibration", "Instrument calibration on the bench or in the field"),
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
        if key:
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
        "civil-rebar", "", 800, 541) + f'''

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
        "BWS Engineering’s HSE policy and Quality policy. ISO 9001:2015 certified by TÜV NORD. No job shall start or continue without due regard to Safety, Health and Environment.") + header("hse.html") + page_hero(
        "HSE &amp; Quality", "Health, safety, environment and quality",
        "No job shall start or continue without due regard to Safety, Health and Environment.",
        "hse-fire-drill", "", 1600, 1200) + f'''

<section class="section" id="hse" aria-labelledby="hsep-title">
  <div class="container split">
    <div>
      {eyebrow("01", "HSE policy")}
      <h2 id="hsep-title">Our HSE policy</h2>
      <div class="policy policy--hse">
        <span class="safety-tag">{icon("warn")} Health · Safety · Environment</span>
        <blockquote>
          <p>BWS Engineering Sdn Bhd conducts its business only after taking account of the health and safety of its employees and giving due regard to the protection of the environment.</p>
          <p>No job shall start or continue without due regard to Safety, Health and Environment.</p>
        </blockquote>
      </div>
    </div>
    <figure class="media media--framed ratio-4x3 reveal">
      {img("hse-toolbox-talk", "Workers seated under a site tent for a safety briefing before work", 800, 600)}
      <figcaption>Safety briefing on site.</figcaption>
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
      </div>
      <p class="mt-5 mb-0">The company is ISO 9001:2015 certified by TÜV NORD.</p>
    </div>
    <div>
      <!-- PLACEHOLDER: scan of the ISO 9001:2015 certificate (TÜV NORD). Replace with:
           <img src="assets/img/iso-certificate.webp" alt="ISO 9001:2015 certificate issued by TÜV NORD to BWS Engineering Sdn Bhd" width="800" height="1131" loading="lazy"> -->
      <div class="ph" style="aspect-ratio:3/4;max-width:24rem;margin-inline:auto" role="img" aria-label="ISO 9001:2015 certificate image coming soon"><div><strong>Certificate placeholder</strong>ISO 9001:2015 certificate (TÜV NORD)</div></div>
    </div>
  </div>
</section>

<section class="section" aria-labelledby="cert-title">
  <div class="container">
    <div class="section-head">{eyebrow("03", "Licences &amp; certification")}<h2 id="cert-title">Licences and registrations</h2></div>
    <div class="grid grid--3 reveal-stagger">
      <div class="card"><span class="card-icon">{icon("shield")}</span><h3>ISO 9001:2015</h3><p class="mb-0">Quality Management System certified by TÜV NORD.</p></div>
      <div class="card"><span class="card-icon">{icon("badge")}</span><h3>PETRONAS Licence</h3><p class="mb-0">Valid PETRONAS licence.</p></div>
      <div class="card"><span class="card-icon">{icon("doc")}</span><h3>CIDB Registration</h3><p class="mb-0">Registered with the Construction Industry Development Board for various categories of construction activities.</p></div>
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
  </div>
</section>
{CTA}''' + footer()

# ================================================================ CAREERS
JOBS = [
    # PLACEHOLDER positions: replace with real openings (title, location, type, one-line summary)
    ("Site Supervisor (Mechanical &amp; Piping)", "Miri / Bintulu", "Full-time", "Example listing: replace with the real role summary."),
    ("Safety Officer", "Miri / Bintulu", "Full-time", "Example listing: replace with the real role summary."),
    ("QA/QC Inspector", "Bintulu", "Full-time", "Example listing: replace with the real role summary."),
]

def careers():
    jobs = ""
    for t, loc, typ, summ in JOBS:
        plain = t.replace("&amp;", "&")
        jobs += f'''
      <article class="job">
        <div>
          <h3>{t}</h3>
          <ul class="job-meta" role="list"><li>{icon("pin")}{loc}</li><li>{icon("clock")}{typ}</li></ul>
          <p>{summ}</p>
        </div>
        <a class="btn btn--primary" data-apply="{plain}" href="mailto:bwsesbhr@gmail.com?subject={quote("Job Application – " + plain)}">Apply via email<span class="visually-hidden">: {t}</span></a>
      </article>'''
    return head("careers.html", "Careers | Jobs in Oil &amp; Gas Construction, Miri &amp; Bintulu | BWS Engineering",
        "Join BWS Engineering Sdn Bhd in Miri and Bintulu, Sarawak. A safety-first oil &amp; gas construction and maintenance contractor. Apply by email to bwsesbhr@gmail.com.") + header("careers.html") + page_hero(
        "Careers", "Build your career with BWS",
        "Join a Sarawak contractor that has been building and maintaining oil and gas facilities since 2002.",
        "civil-concrete-finishing", "", 800, 554) + f'''

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
      <p class="mb-0">We conduct our business only after taking account of the health and safety of our employees. No job shall start or continue without due regard to Safety, Health and Environment, and every member of the team is expected to uphold that.</p>
    </aside>
  </div>
</section>

<section class="section section--steel" id="openings" aria-labelledby="open-title">
  <div class="container">
    <div class="section-head section-head--split">
      <div>{eyebrow("02", "Open positions")}<h2 id="open-title">Current openings</h2></div>
      <p class="lead">Send your CV with the position title in the subject line to <a href="mailto:bwsesbhr@gmail.com">bwsesbhr@gmail.com</a>.</p>
    </div>
    <!-- JOB OPENINGS: one <article class="job"> per position.
         To add a role: copy an <article>, change the <h3> title, location, type and summary,
         and set data-apply="Exact Position Title" on the button (it builds the email subject
         "Job Application – Exact Position Title"). Update the href to match for no-JS visitors.
         The three roles below are PLACEHOLDERS: replace or delete before going live. -->
    <div class="jobs">{jobs}
      <article class="job job--general">
        <div>
          <h3>Don’t see your role?</h3>
          <p>We welcome general applications from experienced engineering and construction professionals. Tell us the discipline you work in.</p>
        </div>
        <a class="btn btn--ghost" data-apply="General Application" href="mailto:bwsesbhr@gmail.com?subject={quote("Job Application – General Application")}">Send your CV</a>
      </article>
    </div>
  </div>
</section>
{CTA}''' + footer()

# ================================================================ CONTACT
def maps_embed(q):
    return f"https://www.google.com/maps?q={quote(q)}&output=embed"

def contact():
    miri_q = "Lot 1743, Block 3 MCLD, Piasau Industrial Estate Phase III, Jalan Prunus 1, 98000 Miri, Sarawak"
    btu_q = "Lot 782, Block 20, Kemena Land District, Jalan Tanjung Kidurong, 97007 Bintulu, Sarawak"
    opts = "".join(f'<option value="{t.replace("&amp;", "&")}" data-key="{sid}">{t}</option>' for sid, _i, t, *_ in SERVICES)
    ld = [{"@context": "https://schema.org", "@type": "ContactPage", "url": SITE + "/contact.html", "about": {"@id": SITE + "/#organization"}}]
    return head("contact.html", "Contact Us | Miri &amp; Bintulu Offices | BWS Engineering Sdn Bhd",
        "Contact BWS Engineering Sdn Bhd. Main office and workshop in Piasau Industrial Estate, Miri (085-652743) and fabrication yard in Kidurong, Bintulu (086-252476). Email bwsesb@gmail.com.", ld) + header("contact.html") + page_hero(
        "Contact", "Contact us",
        "Talk to our Miri or Bintulu office, or send an enquiry and we’ll route it to the right team.",
        "facility-bintulu-yard", "", 1600, 1599) + f'''

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
            <li>{icon("mail")}<a href="mailto:bwsesb@gmail.com">bwsesb@gmail.com</a></li>
          </ul>
          <p class="mt-5 mb-0"><a class="link-arrow" href="https://www.google.com/maps/search/?api=1&amp;query={quote(miri_q)}" target="_blank" rel="noopener">Open in Google Maps<span class="visually-hidden"> (opens in a new tab)</span></a></p>
        </div>
        <div class="map-wrap"><iframe class="map" src="{maps_embed(miri_q)}" title="Map: BWS Engineering main office, Piasau Industrial Estate, Miri" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div>
      </article>
      <article class="office" aria-labelledby="btu-title">
        <div class="office-body">
          <span class="tag">Fabrication Yard</span>
          <h3 id="btu-title">Bintulu: Office cum Fabrication Yard</h3>
          <ul class="contact-list" role="list">
            <li>{icon("pin")}<address>Lot 782, Block 20, Kemena Land District, Jalan Tanjung Kidurong, 97007 Bintulu, Sarawak, Malaysia</address></li>
            <li>{icon("phone")}<a href="tel:+6086252476">086-252476</a></li>
            <li>{icon("mail")}<a href="mailto:bwsesb@gmail.com">bwsesb@gmail.com</a></li>
          </ul>
          <p class="mt-5 mb-0"><a class="link-arrow" href="https://www.google.com/maps/search/?api=1&amp;query={quote(btu_q)}" target="_blank" rel="noopener">Open in Google Maps<span class="visually-hidden"> (opens in a new tab)</span></a></p>
        </div>
        <div class="map-wrap"><iframe class="map" src="{maps_embed(btu_q)}" title="Map: BWS Engineering fabrication yard, Kidurong, Bintulu" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div>
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
      <form class="form" action="https://formspree.io/f/YOUR_FORM_ID" method="POST" data-contact-form data-mailto="bwsesb@gmail.com">
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
        <li>{icon("mail")}<span>General enquiries<br><a href="mailto:bwsesb@gmail.com">bwsesb@gmail.com</a></span></li>
        <li>{icon("briefcase")}<span>Job applications<br><a href="mailto:bwsesbhr@gmail.com">bwsesbhr@gmail.com</a></span></li>
        <li>{icon("phone")}<span>Miri <a href="tel:+6085652743">085-652743</a><br>Bintulu <a href="tel:+6086252476">086-252476</a></span></li>
      </ul>
    </aside>
  </div>
</section>
<script>
  // Pre-select the service when arriving from a Services page button (contact.html?service=civil)
  (function () {{
    var k = new URLSearchParams(location.search).get("service");
    if (!k) return;
    var o = document.querySelector('#f-service option[data-key="' + k + '"]');
    if (o) o.selected = true;
  }})();
</script>''' + footer()

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
