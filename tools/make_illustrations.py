# Generates the blueprint-style line illustrations used in the inner-page headers.
# Output: ../site/assets/illustrations/*.svg  (800 x 600, navy drawing sheet with grid)
# Run: python3 tools/make_illustrations.py
import math, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site", "assets", "illustrations")
os.makedirs(OUT, exist_ok=True)

INK, BLUE, SKY, CYAN, AMBER = "#0A1240", "#0A18D9", "#4797E6", "#E4FCFC", "#F2A900"
W, H = 800, 600
FONT = "font-family=\"Arial, Helvetica, sans-serif\""


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


def line(pts, color=CYAN, w=2, op=1, fill="none", close=False, dash=None):
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + (" Z" if close else "")
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" stroke="{color}" stroke-width="{w}" stroke-opacity="{op}" fill="{fill}"{da}/>'


def rect(x, y, w, h, color=CYAN, sw=2, fill="none", op=1):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" stroke="{color}" stroke-width="{sw}" fill="{fill}" stroke-opacity="{op}"/>'


def circle(cx, cy, r, color=CYAN, sw=2, fill="none", op=1, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" stroke="{color}" stroke-width="{sw}" fill="{fill}" stroke-opacity="{op}"{da}/>'


def text(x, y, s, size=13, color=SKY, anchor="start", weight=600, spacing=2):
    return (f'<text x="{x}" y="{y}" {FONT} font-size="{size}" font-weight="{weight}" letter-spacing="{spacing}" '
            f'fill="{color}" stroke="none" text-anchor="{anchor}">{s}</text>')


def dim_h(x1, x2, y, label="", lx=None):
    """Horizontal dimension line with ticks."""
    out = line([(x1, y), (x2, y)], SKY, 1, .8)
    for x in (x1, x2):
        out += line([(x - 5, y + 5), (x + 5, y - 5)], SKY, 1, .8) + line([(x, y - 9), (x, y + 9)], SKY, 1, .5)
    if label:
        out += text(lx if lx is not None else (x1 + x2) / 2, y - 8, label, 11, SKY, "middle")
    return out


def dim_v(y1, y2, x, label=""):
    out = line([(x, y1), (x, y2)], SKY, 1, .8)
    for y in (y1, y2):
        out += line([(x - 5, y + 5), (x + 5, y - 5)], SKY, 1, .8) + line([(x - 9, y), (x + 9, y)], SKY, 1, .5)
    if label:
        out += (f'<text x="{x - 10}" y="{(y1 + y2) / 2}" {FONT} font-size="11" font-weight="600" letter-spacing="2" fill="{SKY}" '
                f'stroke="none" text-anchor="middle" transform="rotate(-90 {x - 10} {(y1 + y2) / 2})">{label}</text>')
    return out


def ground(y=520, x1=0, x2=W):
    out = line([(x1, y), (x2, y)], CYAN, 2)
    for x in range(int(x1), int(x2), 16):
        out += line([(x, y + 2), (x - 10, y + 12)], SKY, 1, .45)
    return out


def ladder(x, y1, y2, w=10):
    out = line([(x, y1), (x, y2)], SKY, 1.2) + line([(x + w, y1), (x + w, y2)], SKY, 1.2)
    for y in range(int(min(y1, y2)) + 6, int(max(y1, y2)), 10):
        out += line([(x, y), (x + w, y)], SKY, 1, .7)
    return out


def hatch(x, y, w, h, step=10, color=SKY, op=.25):
    out = ""
    for k in range(-int(h), int(w), step):
        x1, y1 = x + max(k, 0), y + max(-k, 0)
        x2, y2 = x + min(k + h, w), y + min(h, w - k)
        if x2 > x1:
            out += line([(x1, y1), (x2, y2)], color, 1, op)
    return out


# ------------------------------------------------------------------ services: process plant
def plant():
    b = ground(520)
    # storage tank (left)
    b += rect(70, 400, 150, 120, fill=BLUE, op=1).replace('fill="' + BLUE + '"', f'fill="{BLUE}" fill-opacity=".25"')
    b += line([(70, 400), (145, 375), (220, 400)])
    for y in (430, 460, 490):
        b += line([(70, y), (220, y)], SKY, 1, .5)
    b += line([(200, 400), (200, 520)], SKY, 1, .6) + ladder(200, 400, 520, 8)
    # tall distillation column
    cx = 330
    b += line([(cx - 32, 520), (cx - 32, 140), (cx - 24, 118), (cx + 24, 118), (cx + 32, 140), (cx + 32, 520)])
    b += f'<path d="M{cx-32} 520V140L{cx-24} 118H{cx+24}L{cx+32} 140V520Z" fill="{BLUE}" fill-opacity=".22" stroke="none"/>'
    for y in (190, 260, 330, 400, 470):
        b += line([(cx - 52, y), (cx + 52, y)], CYAN, 1.5) + line([(cx - 52, y), (cx - 52, y - 16)], SKY, 1) + line([(cx + 52, y), (cx + 52, y - 16)], SKY, 1)
        b += line([(cx - 52, y - 16), (cx + 52, y - 16)], SKY, 1, .6)
    b += ladder(cx + 40, 118, 520, 9)
    b += line([(cx, 118), (cx, 96), (cx + 120, 96), (cx + 120, 210)], SKY, 3)
    # second column
    c2 = 470
    b += f'<path d="M{c2-24} 520V230A24 24 0 0 1 {c2+24} 230V520Z" fill="{BLUE}" fill-opacity=".22" stroke="{CYAN}" stroke-width="2"/>'
    for y in (300, 380, 450):
        b += line([(c2 - 40, y), (c2 + 40, y)], CYAN, 1.5)
    # sphere
    b += circle(640, 420, 62, fill=BLUE).replace(f'fill="{BLUE}"', f'fill="{BLUE}" fill-opacity=".25"')
    b += f'<ellipse cx="640" cy="420" rx="62" ry="16" stroke="{SKY}" stroke-width="1" fill="none"/>'
    for x in (595, 625, 655, 685):
        b += line([(x, 470), (x, 520)], CYAN, 2)
    b += line([(590, 495), (690, 495)], SKY, 1, .6)
    # flare stack
    b += line([(745, 520), (745, 90)], CYAN, 2) + line([(733, 520), (745, 90), (757, 520)], SKY, 1, .5)
    b += f'<path d="M745 90c-9-16 2-26 0-40 10 12 12 26 0 40z" fill="{SKY}" fill-opacity=".5" stroke="{CYAN}" stroke-width="1.5"/>'
    # pipe rack
    b += line([(60, 360), (720, 360)], CYAN, 2) + line([(60, 372), (720, 372)], SKY, 1.5)
    for x in range(80, 720, 80):
        b += line([(x, 360), (x, 520)], SKY, 1.2, .55)
    b += line([(cx + 32, 300), (c2 - 24, 300)], SKY, 3) + line([(c2 + 24, 330), (600, 330), (600, 370)], SKY, 3)
    b += dim_v(118, 520, 410, "COLUMN")
    b += dim_h(578, 702, 335, "SPHERE", lx=660)
    return sheet(b, "Line drawing of a process plant with columns, tanks, a sphere, pipe rack and flare stack")


# ------------------------------------------------------------------ projects: crane lift
def crane():
    b = ground(520)
    # crawler crane base
    b += f'<rect x="70" y="470" width="190" height="34" rx="17" stroke="{CYAN}" stroke-width="2" fill="{BLUE}" fill-opacity=".25"/>'
    for x in range(92, 250, 26):
        b += circle(x, 487, 9, SKY, 1.2)
    b += line([(90, 470), (110, 420), (240, 420), (250, 470)], CYAN, 2) + rect(180, 395, 50, 25)
    # lattice boom
    x0, y0, x1, y1 = 130, 425, 560, 70
    n = 12
    dx, dy = (x1 - x0) / n, (y1 - y0) / n
    nx, ny = -dy, dx
    L = math.hypot(nx, ny); nx, ny = nx / L * 14, ny / L * 14
    top = [(x0 + dx * i + nx, y0 + dy * i + ny) for i in range(n + 1)]
    bot = [(x0 + dx * i - nx, y0 + dy * i - ny) for i in range(n + 1)]
    b += line(top) + line(bot)
    for i in range(n):
        b += line([top[i], bot[i + 1]], SKY, 1.2) + line([bot[i + 1], top[i + 1]], SKY, 1, .6)
    b += line([(205, 395), (300, 160), (x1, y1)], SKY, 1.2, .8)
    # hook + vessel
    b += line([(x1, y1), (x1, 270)], CYAN, 1.5) + line([(x1 - 4, y1), (x1 - 4, 270)], CYAN, 1.5)
    b += f'<path d="M{x1-12} 270h24l-4 18a8 8 0 1 1-16 0z" stroke="{CYAN}" stroke-width="2" fill="none"/>'
    b += line([(x1 - 2, 296), (480, 336)], SKY, 1.5) + line([(x1 - 2, 296), (640, 336)], SKY, 1.5)
    b += f'<path d="M470 336h180a40 40 0 0 1 0 80H470a40 40 0 0 1 0-80z" stroke="{CYAN}" stroke-width="2" fill="{BLUE}" fill-opacity=".3"/>'
    for x in (520, 560, 600):
        b += line([(x, 336), (x, 416)], SKY, 1, .55)
    b += line([(560, 416), (560, 470)], SKY, 1, .6, dash="4 6")
    # scaffold tower right
    sx, sy = 640, 160
    for i in range(5):
        b += line([(sx + i * 30, sy), (sx + i * 30, 520)], SKY, 1.3, .9)
    for j in range(0, 361, 45):
        b += line([(sx, sy + j), (sx + 120, sy + j)], SKY, 1.3, .9)
        if j < 360:
            b += line([(sx, sy + j), (sx + 120, sy + j + 45)], SKY, 1, .35)
    b += f'<rect x="{sx}" y="{sy}" width="120" height="360" fill="{BLUE}" fill-opacity=".12" stroke="none"/>'
    b += dim_h(430, 690, 445, "LIFT")
    return sheet(b, "Line drawing of a crawler crane lifting a vessel beside a scaffold tower")


# ------------------------------------------------------------------ about: workshop building elevation
def building():
    b = ground(520)
    # workshop portal frame (right)
    b += f'<path d="M330 520V250L545 190L760 250V520" stroke="{CYAN}" stroke-width="2" fill="{BLUE}" fill-opacity=".18"/>'
    for k in range(9):
        x = 330 + k * 53.75
        y = 250 - (60 * (k / 4) if k <= 4 else 60 * ((8 - k) / 4))
        b += line([(x, y), (x, y + 18)], SKY, 1, .6)
    b += line([(330, 268), (545, 208), (760, 268)], SKY, 1.2, .7)
    for x0 in (370, 560):
        b += rect(x0, 360, 150, 160, SKY, 1.5)
        for y in range(372, 520, 12):
            b += line([(x0, y), (x0 + 150, y)], SKY, 1, .45)
    # office block (left, two storeys)
    b += rect(60, 300, 270, 220, fill=BLUE).replace(f'fill="{BLUE}"', f'fill="{BLUE}" fill-opacity=".28"')
    b += line([(50, 300), (340, 300)], CYAN, 3) + line([(60, 410), (330, 410)], CYAN, 1.5)
    b += line([(60, 390), (330, 390)], SKY, 1.2) + line([(60, 380), (330, 380)], SKY, 1, .6)
    for x in range(70, 330, 14):
        b += line([(x, 380), (x, 410)], SKY, 1, .4)
    for x in (85, 150, 215, 270):
        b += rect(x, 320, 42, 46, CYAN, 1.5) + line([(x + 21, 320), (x + 21, 366)], SKY, 1, .7)
    for x in (85, 270):
        b += rect(x, 430, 42, 46, CYAN, 1.5)
    b += rect(160, 430, 70, 90, CYAN, 1.5) + line([(195, 430), (195, 520)], SKY, 1, .7)
    b += rect(150, 270, 90, 22, SKY, 1.2) + text(195, 286, "BWS", 13, CYAN, "middle", 700, 4)
    # flagpoles
    for i, x in enumerate((20, 38)):
        b += line([(x, 520), (x, 200 + i * 10)], SKY, 1.5)
        b += f'<path d="M{x} {200+i*10}h26l-6 9 6 9h-26" stroke="{SKY}" stroke-width="1.2" fill="none"/>'
    b += dim_h(60, 330, 250, "OFFICE")
    b += dim_h(330, 760, 160, "WORKSHOP", lx=450)
    return sheet(b, "Line drawing of the BWS office and fabrication workshop building in elevation")


# ------------------------------------------------------------------ clients: offshore platform
def platform():
    b = ""
    # sea
    for i, y in enumerate((470, 492, 514, 536)):
        pts = [(x, y + 5 * math.sin((x + i * 40) / 28)) for x in range(0, W + 1, 8)]
        b += line(pts, SKY, 1.5 if i == 0 else 1, .9 - i * .2)
    # jacket legs (battered)
    legs = [(250, 300, 200, 590), (550, 300, 600, 590)]
    for x1, y1, x2, y2 in legs:
        b += line([(x1, y1), (x2, y2)], CYAN, 2.5)
    b += line([(350, 300), (335, 590)], CYAN, 1.5, .8) + line([(450, 300), (465, 590)], CYAN, 1.5, .8)
    levels = [300, 370, 450, 530, 590]
    def xat(leg, y):
        x1, y1, x2, y2 = leg
        return x1 + (x2 - x1) * (y - y1) / (y2 - y1)
    for i in range(len(levels) - 1):
        ya, yb = levels[i], levels[i + 1]
        La, Lb = xat(legs[0], ya), xat(legs[0], yb)
        Ra, Rb = xat(legs[1], ya), xat(legs[1], yb)
        b += line([(La, ya), (Ra, ya)], SKY, 1.5)
        b += line([(La, ya), (Rb, yb)], SKY, 1.2, .7) + line([(Ra, ya), (Lb, yb)], SKY, 1.2, .7)
    # topsides
    b += f'<rect x="200" y="230" width="400" height="70" stroke="{CYAN}" stroke-width="2" fill="{BLUE}" fill-opacity=".28"/>'
    b += line([(200, 265), (600, 265)], SKY, 1.2)
    for x in range(220, 600, 40):
        b += line([(x, 230), (x + 20, 265), (x + 40, 230)], SKY, 1, .5)
    b += rect(230, 150, 150, 80, CYAN, 2, BLUE).replace(f'fill="{BLUE}"', f'fill="{BLUE}" fill-opacity=".22"')
    for x in (245, 285, 325):
        b += rect(x, 168, 26, 18, SKY, 1.2)
    b += rect(420, 175, 110, 55, CYAN, 1.8)
    # helideck
    b += line([(560, 150), (690, 150)], CYAN, 3) + line([(570, 150), (600, 230)], SKY, 1.2) + line([(680, 150), (600, 230)], SKY, 1.2)
    b += text(625, 140, "H", 18, CYAN, "middle", 700, 0)
    # pedestal crane
    b += line([(400, 150), (400, 110)], CYAN, 2) + line([(400, 110), (300, 40)], CYAN, 2) + line([(404, 118), (304, 48)], SKY, 1)
    b += line([(300, 40), (300, 110)], SKY, 1, .7, dash="3 5")
    # flare boom
    b += line([(200, 240), (90, 130)], CYAN, 2) + line([(200, 260), (90, 130)], SKY, 1, .6)
    b += f'<path d="M90 130c-12-14-2-30 2-40 6 14 14 24-2 40z" fill="{SKY}" fill-opacity=".5" stroke="{CYAN}" stroke-width="1.5"/>'
    b += text(700, 465, "MSL", 11, SKY, "end")
    return sheet(b, "Line drawing of an offshore oil and gas platform on a braced jacket")


# ------------------------------------------------------------------ hse: hard hat
def hardhat():
    b = ""
    cx, cy = 400, 330
    for r, op in ((250, .18), (200, .25), (150, .35)):
        b += circle(cx, cy, r, SKY, 1, op=op, dash="2 8" if r == 250 else None)
    b += line([(cx - 280, cy), (cx + 280, cy)], SKY, 1, .35) + line([(cx, cy - 280), (cx, cy + 260)], SKY, 1, .35)
    # shell
    b += (f'<path d="M230 380C230 250 300 180 400 180S570 250 570 380Z" stroke="{CYAN}" stroke-width="2.5" '
          f'fill="{BLUE}" fill-opacity=".35"/>')
    b += f'<path d="M370 186C362 240 360 310 362 380M430 186C438 240 440 310 438 380" stroke="{SKY}" stroke-width="1.5" fill="none"/>'
    b += f'<path d="M370 186Q400 176 430 186" stroke="{CYAN}" stroke-width="2" fill="none"/>'
    # brim with amber band (HSE accent)
    b += f'<path d="M180 380H620C620 402 600 412 580 412H220C200 412 180 402 180 380Z" stroke="{CYAN}" stroke-width="2.5" fill="{INK}"/>'
    b += f'<path d="M238 352H562" stroke="{AMBER}" stroke-width="10"/>'
    # harness hint
    b += f'<path d="M260 412Q400 470 540 412" stroke="{SKY}" stroke-width="1.5" stroke-dasharray="5 6" fill="none"/>'
    # shield + check badge
    b += (f'<path d="M560 150l44-16 44 16v34c0 30-19 48-44 56-25-8-44-26-44-56z" stroke="{AMBER}" stroke-width="2.5" fill="{INK}"/>'
          f'<path d="M585 186l14 14 25-28" stroke="{AMBER}" stroke-width="3" fill="none"/>')
    b += dim_h(180, 620, 470, "PPE")
    b += text(cx, 540, "SAFETY · HEALTH · ENVIRONMENT", 13, SKY, "middle", 700, 4)
    return sheet(b, "Line drawing of a safety hard hat with a safety shield badge")


# ------------------------------------------------------------------ careers: engineer's tools
def tools():
    b = ""
    # pressure gauge
    cx, cy, r = 400, 280, 140
    b += circle(cx, cy, r + 14, CYAN, 2.5, BLUE).replace(f'fill="{BLUE}"', f'fill="{BLUE}" fill-opacity=".25"')
    b += circle(cx, cy, r, SKY, 1.5)
    for i in range(41):
        a = math.radians(225 - i * 6.75)
        r1 = r - (22 if i % 5 == 0 else 12)
        b += line([(cx + r1 * math.cos(a), cy - r1 * math.sin(a)), (cx + (r - 4) * math.cos(a), cy - (r - 4) * math.sin(a))],
                  CYAN if i % 5 == 0 else SKY, 2 if i % 5 == 0 else 1)
    for i, v in enumerate(range(0, 9)):
        a = math.radians(225 - i * 33.75)
        b += text(cx + (r - 42) * math.cos(a), cy - (r - 42) * math.sin(a) + 5, str(v * 25), 13, SKY, "middle", 600, 0)
    a = math.radians(225 - 27 * 6.75)
    b += line([(cx - 20 * math.cos(a), cy + 20 * math.sin(a)), (cx + (r - 30) * math.cos(a), cy - (r - 30) * math.sin(a))], CYAN, 3)
    b += circle(cx, cy, 10, CYAN, 2, INK)
    b += text(cx, cy + 62, "BAR", 12, SKY, "middle", 700, 3)
    b += rect(cx - 22, cy + r + 14, 44, 40, CYAN, 2) + line([(cx - 30, cy + r + 54), (cx + 30, cy + r + 54)], CYAN, 2.5)
    # wrench (left, diagonal)
    b += (f'<g transform="translate(-30 90) rotate(-35 150 330)"><path d="M70 312h150a18 18 0 0 1 0 36H70z" stroke="{CYAN}" stroke-width="2" '
          f'fill="{BLUE}" fill-opacity=".25"/><path d="M220 300a40 40 0 1 1 0 60l18-14v-32z" stroke="{CYAN}" stroke-width="2" fill="{INK}"/>'
          f'<path d="M70 312a18 18 0 0 0 0 36" stroke="{CYAN}" stroke-width="2"/></g>')
    # scale rule (bottom)
    b += rect(120, 500, 560, 44, CYAN, 2, BLUE).replace(f'fill="{BLUE}"', f'fill="{BLUE}" fill-opacity=".2"')
    for i in range(57):
        x = 130 + i * 9.6
        b += line([(x, 500), (x, 500 + (18 if i % 10 == 0 else 10 if i % 5 == 0 else 6))], SKY, 1.2)
    # pipe fitting (right): tee
    b += (f'<path d="M600 230h140v56H700v80h-56v-80H600z" stroke="{CYAN}" stroke-width="2" fill="{BLUE}" fill-opacity=".25"/>'
          f'<path d="M600 222v72M740 222v72M636 366h72" stroke="{SKY}" stroke-width="3"/>')
    b += dim_h(600, 740, 205, "TEE")
    return sheet(b, "Line drawing of an engineer's tools: a pressure gauge, a wrench, a scale rule and a pipe tee")


# ------------------------------------------------------------------ contact: Sarawak coast map (Miri & Bintulu)
def coast_map():
    lon0, lon1, lat0, lat1 = 112.70, 114.71, 2.90, 4.90
    sx = W / (lon1 - lon0)
    sy = H / (lat1 - lat0)
    P = lambda lon, lat: ((lon - lon0) * sx, (lat1 - lat) * sy)
    coast = [(112.70, 2.98), (112.85, 3.06), (112.98, 3.13), (113.03, 3.17), (113.06, 3.24), (113.09, 3.29),
             (113.17, 3.34), (113.30, 3.44), (113.42, 3.55), (113.55, 3.70), (113.68, 3.86), (113.80, 4.03),
             (113.90, 4.20), (113.96, 4.33), (113.99, 4.40), (114.01, 4.47), (114.06, 4.56), (114.10, 4.59),
             (114.20, 4.64), (114.32, 4.69), (114.50, 4.76), (114.71, 4.83)]
    land = coast + [(114.71, 2.90), (112.70, 2.90)]
    b = ""
    b += line([P(*c) for c in land], SKY, 0, 0, fill=BLUE, close=True).replace('fill="' + BLUE + '"', f'fill="{BLUE}" fill-opacity=".22"')
    # offset contour lines in the sea
    for k, op in ((0.05, .5), (0.11, .3), (0.18, .18)):
        b += line([P(lon - k * .55, lat + k) for lon, lat in coast], SKY, 1, op)
    b += line([P(*c) for c in coast], CYAN, 2.5)
    # lat / lon graticule labels
    for lat in (3, 4):
        x, y = P(lon0, lat)
        b += line([(0, y), (W, y)], SKY, 1, .35, dash="4 6") + text(12, y - 8, f"{lat}°N", 12, SKY)
    for lon in (113, 114):
        x, y = P(lon, lat0)
        b += line([(x, 0), (x, H)], SKY, 1, .35, dash="4 6") + text(x + 8, H - 14, f"{lon}°E", 12, SKY)
    # route between the two bases
    m, bt = P(114.011563, 4.446917), P(113.0802423, 3.2724729)
    b += f'<path d="M{bt[0]:.1f} {bt[1]:.1f}Q{(m[0]+bt[0])/2+70:.1f} {(m[1]+bt[1])/2+40:.1f} {m[0]:.1f} {m[1]:.1f}" stroke="{CYAN}" stroke-width="1.5" stroke-dasharray="2 7" fill="none"/>'
    for (x, y), name, dx, anchor in ((m, "MIRI", -24, "end"), (bt, "BINTULU", 24, "start")):
        b += circle(x, y, 26, SKY, 1, op=.5) + circle(x, y, 14, CYAN, 1.5, op=.8)
        b += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{CYAN}" stroke="none"/>'
        b += text(x + dx, y + 5, name, 16, CYAN, anchor, 700, 4)
    b += text(P(113.05, 4.55)[0], P(113.05, 4.55)[1], "SOUTH CHINA SEA", 13, SKY, "middle", 600, 6)
    b += text(P(113.85, 3.35)[0], P(113.85, 3.35)[1], "SARAWAK", 15, SKY, "middle", 700, 8)
    # north arrow
    b += f'<path d="M740 70l14 40-14-10-14 10z" stroke="{CYAN}" stroke-width="1.5" fill="{SKY}" fill-opacity=".4"/>' + text(740, 60, "N", 13, CYAN, "middle", 700, 0)
    return sheet(b, "Map of the Sarawak coast showing BWS bases in Miri and Bintulu")



# ------------------------------------------------------------------ gallery: blasting & painting
def blasting():
    b = ground(520)
    # I-beam on trestles (end view + length)
    b += f'<path d="M150 300h420v18H150zM150 382h420v18H150z" stroke="{CYAN}" stroke-width="2" fill="{BLUE}" fill-opacity=".3"/>'
    b += line([(150, 318), (150, 382)], SKY, 1.5) + rect(150, 318, 420, 64, SKY, 1, op=.4)
    b += f'<path d="M352 318h16v64h-16z" stroke="{CYAN}" stroke-width="1.5" fill="{BLUE}" fill-opacity=".45"/>'
    for x in (190, 530):
        b += line([(x - 30, 520), (x, 400), (x + 30, 520)], CYAN, 2) + line([(x - 20, 480), (x + 20, 480)], SKY, 1.2)
    # coated half vs bare half
    b += hatch(360, 300, 210, 100, 8, CYAN, .35)
    # spray gun + hose
    b += (f'<path d="M640 190l-60 26 6 16 60-26z" stroke="{CYAN}" stroke-width="2" fill="{INK}"/>'
          f'<path d="M640 190l40-6 8 36-34 8M664 214l10 46h22l-8-42" stroke="{CYAN}" stroke-width="2" fill="none"/>'
          f'<path d="M688 260c40 30 50 120 10 200s-40 60-60 60" stroke="{SKY}" stroke-width="2" fill="none"/>')
    # spray cone
    b += line([(582, 220), (430, 300)], SKY, 1, .6, dash="3 6") + line([(586, 230), (470, 312)], SKY, 1, .6, dash="3 6")
    import random
    random.seed(7)
    for _ in range(140):
        t = random.random(); spread = random.uniform(-.5, .5)
        x = 584 - t * 140 + spread * 30 * t; y = 225 + t * 80 + spread * 40 * t
        b += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{random.uniform(.8, 2.2):.1f}" fill="{SKY}" fill-opacity="{random.uniform(.3,.9):.2f}" stroke="none"/>'
    b += dim_h(150, 360, 270, "BLASTED")
    b += dim_h(360, 570, 440, "PAINTED")
    return sheet(b, "Line drawing of a steel I-beam being spray painted after blasting")


# ------------------------------------------------------------------ gallery: cable laying
def cable():
    b = ground(470)
    # cable drum on jack stand
    cx, cy = 210, 330
    b += circle(cx, cy, 120, CYAN, 2.5, BLUE).replace(f'fill="{BLUE}"', f'fill="{BLUE}" fill-opacity=".25"')
    b += circle(cx, cy, 70, SKY, 1.5) + circle(cx, cy, 16, CYAN, 2)
    for a in range(0, 360, 45):
        r = math.radians(a)
        b += line([(cx + 16 * math.cos(r), cy + 16 * math.sin(r)), (cx + 120 * math.cos(r), cy + 120 * math.sin(r))], SKY, 1, .5)
    b += line([(cx - 90, 470), (cx, cy), (cx + 90, 470)], CYAN, 2) + line([(cx - 60, 430), (cx + 60, 430)], SKY, 1.2)
    # cable paying out over rollers into a trench / tray
    b += f'<path d="M{cx} {cy - 120}C330 200 400 380 470 430H760" stroke="{CYAN}" stroke-width="5" fill="none"/>'
    b += f'<path d="M{cx} {cy - 120}C330 200 400 380 470 430H760" stroke="{INK}" stroke-width="1.5" fill="none"/>'
    for x in (520, 610, 700):
        b += circle(x, 440, 9, SKY, 1.5) + line([(x - 14, 470), (x, 449), (x + 14, 470)], SKY, 1.2)
    # trench section
    b += f'<path d="M450 470v70h330v-70" stroke="{SKY}" stroke-width="1.5" fill="none" stroke-dasharray="6 5"/>'
    b += hatch(450, 520, 330, 20, 9, SKY, .35)
    # tester
    b += rect(600, 250, 120, 80, CYAN, 2, INK) + rect(614, 264, 92, 30, SKY, 1.2)
    b += text(660, 285, "MΩ", 16, CYAN, "middle", 700, 0)
    b += line([(620, 330), (600, 400), (560, 430)], SKY, 1.5) + line([(700, 330), (720, 400), (740, 430)], SKY, 1.5)
    b += dim_h(470, 760, 395, "CABLE ROUTE")
    return sheet(b, "Line drawing of a cable drum paying out cable into a trench, with an insulation tester")


# ------------------------------------------------------------------ gallery: instrument calibration
def calibration():
    b = ground(500)
    # bench
    b += rect(80, 400, 640, 18, CYAN, 2, BLUE).replace(f'fill="{BLUE}"', f'fill="{BLUE}" fill-opacity=".3"')
    for x in (110, 690):
        b += line([(x, 418), (x, 500)], CYAN, 2)
    # pressure transmitter on stand
    b += line([(250, 400), (250, 330)], CYAN, 2) + rect(220, 310, 60, 20, SKY, 1.5)
    b += f'<path d="M210 250h80v60h-80z" stroke="{CYAN}" stroke-width="2" fill="{BLUE}" fill-opacity=".3"/>'
    b += circle(250, 210, 40, CYAN, 2, INK) + circle(250, 210, 28, SKY, 1.2)
    b += text(250, 216, "4–20", 13, CYAN, "middle", 700, 0) + text(250, 270, "PT", 12, SKY, "middle", 700, 3)
    # hand pump / calibrator
    b += rect(470, 300, 150, 100, CYAN, 2, INK) + rect(488, 316, 114, 40, SKY, 1.2)
    b += text(545, 344, "10.00", 18, CYAN, "middle", 700, 1) + text(545, 368, "BAR", 11, SKY, "middle", 700, 3)
    for i, x in enumerate((500, 530, 560, 590)):
        b += circle(x, 386, 5, SKY, 1.2)
    # hoses / leads
    b += f'<path d="M280 290C360 300 400 340 470 350" stroke="{SKY}" stroke-width="2.5" fill="none"/>'
    b += f'<path d="M290 270C380 240 430 280 470 320" stroke="{AMBER if False else CYAN}" stroke-width="1.5" fill="none" stroke-dasharray="4 5"/>'
    # reference gauge
    b += circle(680, 250, 50, CYAN, 2, INK)
    for i in range(11):
        a = math.radians(210 - i * 24)
        b += line([(680 + 36 * math.cos(a), 250 - 36 * math.sin(a)), (680 + 46 * math.cos(a), 250 - 46 * math.sin(a))], SKY, 1.2)
    b += line([(680, 250), (680 + 34 * math.cos(math.radians(60)), 250 - 34 * math.sin(math.radians(60)))], CYAN, 2.5)
    b += line([(680, 300), (680, 400)], CYAN, 2) + line([(620, 360), (680, 360)], SKY, 2)
    b += dim_h(210, 290, 160, "TRANSMITTER") + dim_h(630, 730, 180, "REFERENCE")
    return sheet(b, "Line drawing of a pressure transmitter being calibrated on a bench against a reference gauge")

for name, fn in [("plant", plant), ("crane-lift", crane), ("workshop", building), ("offshore", platform),
                 ("hard-hat", hardhat), ("tools", tools), ("coast-map", coast_map),
                 ("blasting-painting", blasting), ("cable-laying", cable), ("instrument-calibration", calibration)]:
    svg = fn()
    with open(os.path.join(OUT, name + ".svg"), "w") as f:
        f.write(svg)
    print(name, len(svg))
