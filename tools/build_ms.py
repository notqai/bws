# Builds the Bahasa Melayu site (site/ms/*.html) from the generated English pages, and adds the
# EN | BM language switch + hreflang links to both versions. Run automatically by generate_site.py.
import html, os, re, sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ms_strings import MS, MONTHS

SITE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site")
SITE = "https://www.bwsengineeringsb.com"
PAGES = ["index.html", "about.html", "services.html", "clients.html", "projects.html", "hse.html", "careers.html", "contact.html", "privacy.html", "vendor.html", "404.html"]
missing = set()

def tr(t):
    """Translate one normalised string (exact match, then patterns). Unknown strings stay English."""
    if t in MS:
        return MS[t]
    m = re.fullmatch(r"Team of (\d+)", t)
    if m: return f"Pasukan {m.group(1)} orang"
    m = re.fullmatch(r"Teams of up to (\d+)", t)
    if m: return f"Pasukan sehingga {m.group(1)} orang"
    m = re.fullmatch(r"Illustration (.+) \(enlarge\)", t)
    if m: return f"Ilustrasi {tr(m.group(1))} (besarkan)"
    m = re.fullmatch(r"(.+) \(enlarge photo\)", t)
    if m:
        rest = m.group(1)
        for cat in ("Electrical & Instrumentation", "Mechanical & Piping", "Civil & Structural", "Plant", "HSE"):
            if rest.startswith(cat + " "):
                return f"{tr(cat)} {tr(rest[len(cat) + 1:])} (besarkan foto)"
        return f"{tr(rest)} (besarkan foto)"
    m = re.fullmatch(r"(.+) \(illustration\)", t)
    if m: return f"{tr(m.group(1))} (ilustrasi)"
    m = re.fullmatch(r": (.+)", t)
    if m: return ": " + tr(m.group(1))
    m = re.fullmatch(r"· (.+)", t)
    if m: return "· " + tr(m.group(1))
    m = re.fullmatch(r"(\d{1,2}) (" + "|".join(MONTHS) + r") (\d{4})", t)
    if m: return f"{m.group(1)} {MONTHS[m.group(2)]} {m.group(3)}"
    m = re.fullmatch(r"(.+): (\d+) contracts?, show (?:it|them) in the list", t)   # project map pins
    if m: return f"{m.group(1)}: {m.group(2)} kontrak, tunjukkan dalam senarai"
    m = re.fullmatch(r"Circle area shows the number of contracts at each place, from all (\d+) contracts since (\d{4})\. "
                     r"(\d+) contracts? with no single location \(for example Sarawak-wide maintenance agreements\) (?:is|are) not shown\.", t)
    if m: return (f"Saiz bulatan menunjukkan bilangan kontrak di setiap lokasi, daripada kesemua {m.group(1)} kontrak sejak "
                  f"{m.group(2)}. {m.group(3)} kontrak tanpa satu lokasi tertentu (contohnya perjanjian penyelenggaraan "
                  f"di seluruh Sarawak) tidak ditunjukkan.")
    m = re.fullmatch(r"View all (\d+) projects since (\d{4})", t)
    if m: return f"Lihat kesemua {m.group(1)} projek sejak {m.group(2)}"
    if re.search(r"[a-z]{3,}", t) and not re.match(r"https?:|[\w.+-]+@|width=|index,|noindex|summary_|website$", t): missing.add(t)
    return t

def tr_text(raw):
    """Translate a raw HTML text chunk, keeping surrounding whitespace and entity escaping."""
    if not raw.strip(): return raw
    lead = raw[:len(raw) - len(raw.lstrip())]; trail = raw[len(raw.rstrip()):]
    val = re.sub(r"\s+", " ", html.unescape(raw.strip()))
    out = tr(val)
    if out == val: return raw
    return lead + html.escape(out, quote=False) + trail

def tr_attr(m):
    name, val = m.group(1), m.group(2)
    plain = re.sub(r"\s+", " ", html.unescape(val)).strip()
    out = tr(plain)
    return f'{name}="{html.escape(out, quote=True)}"' if out != plain else m.group(0)

def translate_html(doc):
    parts = re.split(r"(<script\b.*?</script>|<style\b.*?</style>)", doc, flags=re.S)
    for i in range(0, len(parts), 2):
        seg = parts[i]
        seg = re.sub(r'\b(alt|aria-label|placeholder|title|data-title|content)="([^"]*)"', tr_attr, seg)
        seg = re.sub(r">([^<>]+)<", lambda m: ">" + tr_text(m.group(1)) + "<", seg)
        parts[i] = seg
    return "".join(parts)

def fix_paths(doc):
    doc = re.sub(r'((?:src|href|data-full)=")(assets/|favicon\.ico|site\.webmanifest)', r"\1../\2", doc)
    doc = doc.replace('data-fallback="contact.php"', 'data-fallback="../contact.php"')
    doc = doc.replace('href="capability.html"', 'href="../capability.html"')  # English-only document
    doc = re.sub(r'((?:srcset|imagesrcset)=")([^"]*)"', lambda m: m.group(1) + re.sub(r"(^|,\s*)assets/", r"\1../assets/", m.group(2)) + '"', doc)
    return doc

def url_for(page, lang):
    path = "" if page == "index.html" else page
    return f"{SITE}/{'ms/' if lang == 'ms' else ''}{path}"

def alternates(page):
    return (f'<link rel="alternate" hreflang="en" href="{url_for(page, "en")}">\n'
            f'<link rel="alternate" hreflang="ms" href="{url_for(page, "ms")}">\n'
            f'<link rel="alternate" hreflang="x-default" href="{url_for(page, "en")}">\n')

def switch(page, lang):
    if lang == "en":
        return (f'<a class="lang-switch" href="ms/{page}" hreflang="ms" lang="ms">'
                f'<span aria-hidden="true">BM</span><span class="visually-hidden">Baca dalam Bahasa Melayu</span></a>')
    return (f'<a class="lang-switch" href="../{page}" hreflang="en" lang="en">'
            f'<span aria-hidden="true">EN</span><span class="visually-hidden">Read in English</span></a>')

# Email templates in compose links (careers) — URL-encoded in the English pages
CV_EN_SUBJ = quote("Job Application – [Position]")
CV_MS_SUBJ = quote("Permohonan Kerja – [Jawatan]")
CV_EN_BODY = quote("Position / discipline:\nYears of experience:\nCurrent location:\nPhone number:\n\n(Please attach your CV and certificates.)", safe="")
CV_MS_BODY = quote("Jawatan / disiplin:\nTahun pengalaman:\nLokasi semasa:\nNo. telefon:\n\n(Sila lampirkan CV dan sijil anda.)", safe="")

def add_switch_and_alternates(doc, page, lang):
    doc = doc.replace('<link rel="canonical"', alternates(page) + '<link rel="canonical"', 1)
    sw = switch(page, lang)
    doc = doc.replace('<a class="btn btn--primary header-cta"', sw + '\n    <a class="btn btn--primary header-cta"', 1)
    doc = doc.replace('<button class="nav-toggle"', sw.replace('class="lang-switch"', 'class="lang-switch lang-switch--mobile"') + '\n    <button class="nav-toggle"', 1)
    return doc

def build():
    os.makedirs(os.path.join(SITE_DIR, "ms"), exist_ok=True)
    for page in PAGES:
        src = os.path.join(SITE_DIR, page)
        en = open(src, encoding="utf-8").read()
        if 'class="lang-switch"' in en:  # already processed this run
            en = re.sub(r'<a class="lang-switch[^>]*>.*?</a>\n[ \t]*', "", en)
            en = re.sub(r'<link rel="alternate" hreflang="[^"]+" href="[^"]+">\n', "", en)
        ms = translate_html(en)
        ms = fix_paths(ms)
        ms = ms.replace('<html lang="en-MY">', '<html lang="ms-MY">', 1)
        ms = ms.replace('content="en_MY"', 'content="ms_MY"')
        ms = re.sub(r'(<link rel="canonical" href=")' + re.escape(SITE) + r'/', r"\1" + SITE + "/ms/", ms, count=1)
        ms = re.sub(r'(<meta property="og:url" content=")' + re.escape(SITE) + r'/', r"\1" + SITE + "/ms/", ms, count=1)
        ms = ms.replace(CV_EN_SUBJ, CV_MS_SUBJ).replace(CV_EN_BODY, CV_MS_BODY)
        ms = add_switch_and_alternates(ms, page, "ms")
        en = add_switch_and_alternates(en, page, "en")
        open(src, "w", encoding="utf-8").write(en)
        open(os.path.join(SITE_DIR, "ms", page), "w", encoding="utf-8").write(ms)
    # sitemap with both languages
    pages = [p for p in PAGES if p != "404.html"]
    urls = "".join(f"  <url><loc>{url_for(p, l)}</loc>"
                   f'<xhtml:link rel="alternate" hreflang="en" href="{url_for(p, "en")}"/>'
                   f'<xhtml:link rel="alternate" hreflang="ms" href="{url_for(p, "ms")}"/></url>\n'
                   for p in pages for l in ("en", "ms"))
    open(os.path.join(SITE_DIR, "sitemap.xml"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + urls + "</urlset>\n")
    # Kept in the repo so `git diff` shows any newly untranslated English text after a build
    report = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ms_untranslated.txt")
    open(report, "w", encoding="utf-8").write("".join(t + "\n" for t in sorted(missing)))
    print(f"build_ms: {len(missing)} strings kept in English (project/client names etc.), listed in tools/ms_untranslated.txt")

if __name__ == "__main__":
    build()
