# Generates the "site drawing" cards shown on the contact page in place of the Google maps, until the
# visitor clicks "Load interactive map". Same blueprint style as make_illustrations.py, 800 x 500 (16:10).
# Layouts are schematic (marked NOT TO SCALE): real coordinates and lot numbers, simplified roads and coast.
# Output: ../site/assets/illustrations/loc-miri.svg, loc-bintulu.svg
# Run: python3 tools/make_locations.py
import os

from make_illustrations import INK, BLUE, SKY, CYAN, FONT, OUT, line, rect, circle, text

W, H = 800, 500
MONO = 'font-family="ui-monospace, Menlo, Consolas, monospace"'
# Pin tip positions in drawing units; contact.html places the pulse ring here (see pin_style).
PINS = {"miri": (560, 350), "bintulu": (430, 330)}


def pin_style(key):
    x, y = PINS[key]
    return f"--pin-x:{round(x / W * 100)}%;--pin-y:{round(y / H * 100)}%"


def sheet(body, title):
    grid = []
    for x in range(0, W + 1, 20):
        grid.append(f'<path d="M{x} 0V{H}" stroke="{SKY}" stroke-opacity="{.16 if x % 100 == 0 else .06}"/>')
    for y in range(0, H + 1, 20):
        grid.append(f'<path d="M0 {y}H{W}" stroke="{SKY}" stroke-opacity="{.16 if y % 100 == 0 else .06}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{title}">'
            f'<title>{title}</title><rect width="{W}" height="{H}" fill="{INK}"/>'
            f'<g stroke-width="1">{"".join(grid)}</g>'
            f'<g fill="none" stroke-linecap="round" stroke-linejoin="round">{body}</g></svg>')


def rtext(x, y, s, angle, size=11, color=SKY):
    return (f'<text x="{x}" y="{y}" {FONT} font-size="{size}" font-weight="600" letter-spacing="2" fill="{color}" '
            f'stroke="none" text-anchor="middle" transform="rotate({angle} {x} {y})">{s}</text>')


def sea(coast_d, label_x, label_y):
    """Coastline path along the top of the sheet, wave strokes above it and the sea label."""
    out = f'<path d="{coast_d}" stroke="{CYAN}" stroke-width="2.5"/>'
    for y in (34, 62, 90):
        for x in range(30 + (y % 40), W - 40, 90):
            if abs(y - label_y) < 12 and x + 40 > label_x - 12 and x < label_x + 200:
                continue                                    # keep the sea label clear
            out += f'<path d="M{x} {y}q10 -7 20 0t20 0" stroke="{SKY}" stroke-width="1.2" stroke-opacity=".45"/>'
    return out + text(label_x, label_y, "SOUTH CHINA SEA", 12, SKY, "start", 700, 4)


def road(pts, w=16):
    """Double-line road: a wide cyan stroke with the ink sheet colour drawn down the middle."""
    return line(pts, CYAN, w, .9) + line(pts, INK, w - 4) + line(pts, SKY, 1, .5, dash="10 8")


def lots(x0, y0, cols, rows, w, h, gap=10):
    """Neighbouring plots in the estate, drawn faint and dashed."""
    out = ""
    for c in range(cols):
        for r in range(rows):
            out += rect(x0 + c * (w + gap), y0 + r * (h + gap), w, h, SKY, 1, "none", .35)
    return out


def plot(x, y, w, h, label, lx=None, ly=None):
    """The BWS plot: brand-blue fill, cyan outline, label underneath."""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{BLUE}" fill-opacity=".55" stroke="{CYAN}" stroke-width="2"/>'
            + text(lx if lx is not None else x + w / 2, ly if ly is not None else y + h + 18, label, 11, CYAN, "middle", 700, 2))


def pin(x, y):
    """Map pin whose tip touches (x, y)."""
    return (f'<path d="M{x} {y}c-4-10-18-22-18-36a18 18 0 0 1 36 0c0 14-14 26-18 36z" fill="{CYAN}" stroke="{INK}" stroke-width="2"/>'
            + circle(x, y - 36, 7, INK, 0, INK))


def north_arrow(x, y):
    return (circle(x, y, 22, SKY, 1.2, "none", .7)
            + f'<path d="M{x} {y - 18}l9 26-9-6-9 6z" fill="{CYAN}" stroke="none"/>'
            + text(x, y - 28, "N", 12, CYAN, "middle", 700, 0))


def scale_bar(x, y):
    out = ""
    for i in range(4):
        out += f'<rect x="{x + i * 30}" y="{y}" width="30" height="6" fill="{CYAN if i % 2 == 0 else INK}" stroke="{CYAN}" stroke-width="1"/>'
    return out + text(x, y - 8, "SCHEMATIC · NOT TO SCALE", 10, SKY, "start", 600, 2)


def coords(x, y, s):
    return (f'<text x="{x}" y="{y}" {MONO} font-size="12" font-weight="600" letter-spacing="1" fill="{CYAN}" '
            f'stroke="none" text-anchor="end">{s}</text>')


def title_block(dwg, site):
    """Engineering title block along the bottom. The right-hand cell is left blank: the HTML button sits there."""
    y, h = 440, 44
    out = rect(20, y, 760, h, CYAN, 1.5, INK)
    for x in (230, 430, 530):
        out += line([(x, y), (x, y + h)], CYAN, 1.5)
    out += text(36, y + 28, f"DWG {dwg}", 13, CYAN, "start", 700, 2)
    out += text(246, y + 28, site, 13, CYAN, "start", 700, 2)
    out += text(446, y + 28, "REV A", 13, SKY, "start", 700, 2)
    return out


def miri():
    b = sea("M0 138C160 106 300 150 460 128S700 96 800 114", 40, 70)
    b += road([(0, 250), (800, 250)])                       # estate trunk road
    b += road([(470, 250), (470, 430)])                     # Jalan Prunus 1
    b += rtext(452, 345, "JLN PRUNUS 1", -90)
    b += lots(40, 172, 6, 1, 60, 58) + lots(40, 280, 5, 2, 60, 45)
    b += lots(500, 172, 3, 1, 60, 58) + lots(650, 290, 2, 2, 50, 50)
    b += plot(500, 300, 120, 80, "LOT 1743")
    b += text(40, 160, "PIASAU INDUSTRIAL ESTATE PH III", 12, SKY, "start", 700, 3)
    b += pin(*PINS["miri"])
    b += north_arrow(740, 200) + scale_bar(40, 410) + coords(780, 422, "4.4469° N  114.0116° E")
    b += title_block("BWS-LOC-01", "MIRI HQ")
    return sheet(b, "Site drawing of the BWS Engineering main office location, Piasau Industrial Estate, Miri")


def bintulu():
    b = sea("M0 120C140 150 280 104 430 126S690 150 800 112", 40, 70)
    b += road([(0, 230), (800, 230)])                       # Jalan Tanjung Kidurong
    b += text(40, 214, "JLN TANJUNG KIDURONG", 11, SKY, "start", 600, 2)
    b += road([(330, 230), (330, 430)])                     # Jalan Kidurong
    b += rtext(312, 345, "JLN KIDURONG", -90)
    b += lots(40, 260, 3, 2, 60, 55) + lots(560, 160, 2, 1, 60, 55)
    b += plot(370, 260, 110, 70, "LOT 782 · OFFICE")
    b += plot(540, 280, 200, 90, "LOT 124–128 · FABRICATION YARD")
    b += text(40, 160, "KIDURONG INDUSTRIAL ESTATE", 12, SKY, "start", 700, 3)
    b += pin(*PINS["bintulu"])
    b += north_arrow(740, 190) + scale_bar(40, 410) + coords(780, 422, "3.2725° N  113.0802° E")
    b += title_block("BWS-LOC-02", "BINTULU")
    return sheet(b, "Site drawing of the BWS Engineering office and fabrication yard location, Kidurong, Bintulu")


if __name__ == "__main__":
    for name, fn in [("loc-miri", miri), ("loc-bintulu", bintulu)]:
        svg = fn()
        with open(os.path.join(OUT, name + ".svg"), "w") as f:
            f.write(svg)
        print(name, len(svg), pin_style(name[4:]))
