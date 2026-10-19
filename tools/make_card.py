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
