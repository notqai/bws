# Downloads IBM Plex (IBM's official release, SIL Open Font License 1.1) and writes the self-hosted web fonts:
#   site/assets/fonts/ibm-plex-serif-700-latin.woff2               headings
#   site/assets/fonts/ibm-plex-sans-{400,600,700}-latin.woff2      body and UI
#   tools/data/fonts/ibm-plex-mono-600-latin.woff2                 source for the drawing coordinates (not served)
#   site/assets/fonts/OFL.txt                                      the licence, as IBM ships it
# Each font is cut down to the Latin set Google Fonts serves as "latin", plus the few extra characters the site and
# the drawings use (⅛ ⅜ ⅝ ⅞ in the equipment register, Ω on the cable-laying drawing), without hinting (like the
# Source fonts before them). The drawing tools (make_illustrations.py, make_locations.py) subset these files again
# into each SVG, so they only need this to have been run once.
# It also prints the size-adjust / ascent-override / descent-override values for the size-matched fallback faces in
# src/css/00-fonts-tokens.css, measured on the site's own text.
# Run once (needs network and: pip install fonttools brotli):  python3 tools/fetch_fonts.py
#      python3 tools/fetch_fonts.py --metrics     (only print the fallback metrics, from the files already written)
import glob, hashlib, html, io, os, re, sys, urllib.request, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, "..", "site")
FONTS = os.path.join(SITE, "assets", "fonts")
TOOL_FONTS = os.path.join(HERE, "data", "fonts")
CACHE = os.environ.get("BWS_FONT_CACHE", os.path.join(os.path.expanduser("~"), ".cache", "bws-site-fonts"))
REL = "https://github.com/IBM/plex/releases/download/"

# Pinned releases (IBM/plex on GitHub) and the SHA-256 of each zip
RELEASES = {
    "sans":  ("%40ibm%2Fplex-sans%401.1.0/ibm-plex-sans.zip",
              "fb365d910566e6d199cc2c15579a7dd9a267128e18431a394ed81f1970c69200"),
    "serif": ("%40ibm%2Fplex-serif%402.0.0/ibm-plex-serif.zip",
              "c006b095c47b919c6c8d78319e9e628745033f5db94507c1c9dfe4b35dd51f1e"),
    "mono":  ("%40ibm%2Fplex-mono%402.5.0/ibm-plex-mono.zip",
              "6d23f01257663d8cc49a0d64c22ced630b79e0e2a0ac08a0da86e9a38bbc481c"),
}
# (family, style name in the release, output file)
OUTPUTS = [
    ("serif", "Bold", os.path.join(FONTS, "ibm-plex-serif-700-latin.woff2")),
    ("sans", "Regular", os.path.join(FONTS, "ibm-plex-sans-400-latin.woff2")),
    ("sans", "SemiBold", os.path.join(FONTS, "ibm-plex-sans-600-latin.woff2")),
    ("sans", "Bold", os.path.join(FONTS, "ibm-plex-sans-700-latin.woff2")),
    ("mono", "SemiBold", os.path.join(TOOL_FONTS, "ibm-plex-mono-600-latin.woff2")),
]
# Google Fonts' "latin" unicode-range, plus fractions used in the equipment register and Ω (drawings)
LATIN = ("U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,"
         "U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD")
EXTRA = "U+03A9,U+215B-215E"
UNICODE_RANGE = LATIN + "," + EXTRA         # also the unicode-range of the @font-face rules


def parse_ranges(spec):
    out = set()
    for part in spec.split(","):
        a, _, b = part.strip()[2:].partition("-")
        out.update(range(int(a, 16), int(b or a, 16) + 1))
    return out


def release_zip(family):
    path, sha = RELEASES[family]
    os.makedirs(CACHE, exist_ok=True)
    local = os.path.join(CACHE, path.rsplit("/", 1)[-1].replace(".zip", "-" + sha[:12] + ".zip"))
    if not os.path.exists(local):
        print("downloading", REL + path)
        req = urllib.request.Request(REL + path, headers={"User-Agent": "bws-site-build/1.0"})
        data = urllib.request.urlopen(req, timeout=120).read()
        if hashlib.sha256(data).hexdigest() != sha:
            raise SystemExit(f"checksum mismatch for {path}")
        with open(local, "wb") as f:
            f.write(data)
    return zipfile.ZipFile(local)


def subset(ttf_bytes, out_path, unicodes):
    from fontTools import subset as ftsubset
    from fontTools.ttLib import TTFont
    opts = ftsubset.Options()
    opts.flavor = "woff2"
    opts.hinting = False
    opts.desubroutinize = True
    opts.name_IDs = [0, 1, 2, 3, 4, 5, 6, 13, 14]      # keep the copyright and licence records
    opts.layout_features = ["ccmp", "locl", "kern", "liga", "frac", "numr", "dnom", "lnum", "onum", "zero"]
    font = TTFont(io.BytesIO(ttf_bytes), recalcTimestamp=False)
    for t in ("DSIG", "meta"):
        if t in font:
            del font[t]
    s = ftsubset.Subsetter(opts)
    s.populate(unicodes=unicodes)
    s.subset(font)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    font.flavor = "woff2"
    font.save(out_path)
    print(f"{os.path.relpath(out_path, os.path.join(HERE, '..'))}: {os.path.getsize(out_path)} bytes")


# ------------------------------------------------------------------ fallback metrics
def site_text(tags):
    """Visible text of the English pages inside the given tags, used to weight the average character width."""
    out = []
    for p in sorted(glob.glob(os.path.join(SITE, "*.html"))):
        doc = open(p, encoding="utf-8").read()
        doc = re.sub(r"<(script|style|svg)\b.*?</\1>", "", doc, flags=re.S)
        for m in re.finditer(rf"<({tags})\b[^>]*>(.*?)</\1>", doc, flags=re.S):
            out.append(html.unescape(re.sub(r"<[^>]+>", "", m.group(2))))
    return " ".join(" ".join(out).split())


def avg_width(font_path, text):
    from fontTools.ttLib import TTFont
    f = TTFont(font_path)
    cmap, hm, upm = f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm
    chars = [c for c in text if ord(c) in cmap]
    return sum(hm[cmap[ord(c)]][0] for c in chars) / len(chars) / upm


def fallback_rule(web, local, text):
    """size-adjust makes the fallback's average advance (over the site's text) match the web font's; the ascent and
    descent overrides then give the fallback the web font's line box (hhea metrics, as browsers use them here)."""
    from fontTools.ttLib import TTFont
    f = TTFont(web)
    upm = f["head"].unitsPerEm
    size = avg_width(web, text) / avg_width(local, text)
    asc, desc = f["hhea"].ascent / upm / size, -f["hhea"].descent / upm / size
    return (f"size-adjust: {size * 100:.2f}%; ascent-override: {asc * 100:.2f}%; descent-override: {desc * 100:.2f}%; "
            f"line-gap-override: 0%;")


SUPPLEMENTAL = "/System/Library/Fonts/Supplemental/"     # macOS; Windows: C:/Windows/Fonts/arial.ttf etc.


def metrics():
    body = site_text("p|li|dd|td|a|span|label|button")
    heads = site_text("h1|h2|h3")
    for name, web, local, text in [
            ("IBM Plex Sans Fallback (Arial)", "ibm-plex-sans-400-latin.woff2", "Arial.ttf", body),
            ("IBM Plex Serif Fallback (Georgia Bold)", "ibm-plex-serif-700-latin.woff2", "Georgia Bold.ttf", heads)]:
        print(f"{name}: {fallback_rule(os.path.join(FONTS, web), SUPPLEMENTAL + local, text)}")


def main():
    if "--metrics" not in sys.argv[1:]:
        unicodes = parse_ranges(UNICODE_RANGE)
        for family, style, out in OUTPUTS:
            z = release_zip(family)
            prefix = {"sans": "IBMPlexSans", "serif": "IBMPlexSerif", "mono": "IBMPlexMono"}[family]
            name = next(n for n in z.namelist() if n.endswith(f"/fonts/complete/ttf/{prefix}-{style}.ttf"))
            subset(z.read(name), out, unicodes)
        lic = next(n for n in release_zip("sans").namelist() if n.endswith("/LICENSE.txt"))
        with open(os.path.join(FONTS, "OFL.txt"), "wb") as f:
            f.write(release_zip("sans").read(lic))
    metrics()


if __name__ == "__main__":
    main()
