# Generates the "site drawing" cards shown for each office on the contact page (the "Open in Google Maps"
# link next to them goes to the live listing). Same blueprint style as make_illustrations.py, 800 x 500 (16:10).
# The geometry is traced from OpenStreetMap (© OpenStreetMap contributors, ODbL), cached in tools/data/osm-*.json,
# and drawn to true scale on a local equirectangular projection centred on each office, north up.
# Output: ../site/assets/illustrations/loc-miri.svg, loc-bintulu.svg
# Run: python3 tools/make_locations.py            (draws from the cached data, no network)
#      python3 tools/make_locations.py --fetch    (re-downloads from the Overpass API and rewrites the cache first)
import json, math, os, sys

from make_illustrations import INK, BLUE, SKY, CYAN, FONT, OUT, line, rect, circle, text

W, H = 800, 500
MAP_H = 430                                   # map area is y 0-430; the title block sits below it
MONO = 'font-family="ui-monospace, Menlo, Consolas, monospace"'
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SOURCE = "© OpenStreetMap contributors, ODbL. Trimmed Overpass API extract, see tools/make_locations.py --fetch"
OVERPASS = "https://overpass-api.de/api/interpreter"
USER_AGENT = "bws-site-build/1.0 (static site map drawing)"

# lat/lon: the office point. scale: drawing units per metre. pin: where the office lands (the pin tip).
SITES = {
    "miri":    {"lat": 4.446917, "lon": 114.011563, "scale": 1.15, "pin": (360, 240)},
    "bintulu": {"lat": 3.2724729, "lon": 113.0802423, "scale": 1 / 3.5, "pin": (500, 110)},
}
# Pin tip positions in drawing units; contact.html places the pulse ring here (see pin_style).
PINS = {k: s["pin"] for k, s in SITES.items()}

MAJOR = ("trunk", "primary", "secondary", "tertiary")
MINOR = ("residential", "unclassified", "living_street", "road")
LINKS = tuple(c + "_link" for c in MAJOR)
PATHS = ("track", "path", "footway")


# metres per degree of longitude at the equator / of latitude
M_PER_DEG_LON = 111320
M_PER_DEG_LAT = 110540


def pin_style(key):
    x, y = PINS[key]
    return f"--pin-x:{x / W * 100:.1f}%;--pin-y:{y / H * 100:.1f}%"


def project(key, lat, lon):
    """Local equirectangular projection centred on the office, in drawing units (y down, north up)."""
    s = SITES[key]
    xm = (lon - s["lon"]) * math.cos(math.radians(s["lat"])) * M_PER_DEG_LON
    ym = (lat - s["lat"]) * M_PER_DEG_LAT
    return s["pin"][0] + xm * s["scale"], s["pin"][1] - ym * s["scale"]


# ------------------------------------------------------------------ geometry helpers (drawing units)

def clip_segment(p, q, box):
    """Liang-Barsky: the part of segment p-q inside box (x0, y0, x1, y1), or None."""
    x0, y0, x1, y1 = box
    dx, dy = q[0] - p[0], q[1] - p[1]
    t0, t1 = 0.0, 1.0
    for pk, qk in ((-dx, p[0] - x0), (dx, x1 - p[0]), (-dy, p[1] - y0), (dy, y1 - p[1])):
        if pk == 0:
            if qk < 0:
                return None
        else:
            t = qk / pk
            if pk < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
    if t0 > t1:
        return None
    return (p[0] + t0 * dx, p[1] + t0 * dy), (p[0] + t1 * dx, p[1] + t1 * dy)


def clip_line(pts, box):
    """Split a polyline into the runs that lie inside box, cut exactly at the box edge."""
    runs, cur = [], []
    for p, q in zip(pts, pts[1:]):
        seg = clip_segment(p, q, box)
        if seg is None:
            if cur:
                runs.append(cur)
                cur = []
            continue
        a, b = seg
        if not cur:
            cur = [a]
        elif math.dist(cur[-1], a) > 1e-9:          # left and re-entered within one segment
            runs.append(cur)
            cur = [a]
        cur.append(b)
        if b != q:                                  # segment leaves the box here
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    return [r for r in runs if len(r) > 1]


def clip_polygon(pts, box):
    """Sutherland-Hodgman clip of a closed polygon to box."""
    x0, y0, x1, y1 = box
    edges = [(lambda p: p[0] >= x0, lambda p, q: (x0, p[1] + (q[1] - p[1]) * (x0 - p[0]) / (q[0] - p[0]))),
             (lambda p: p[0] <= x1, lambda p, q: (x1, p[1] + (q[1] - p[1]) * (x1 - p[0]) / (q[0] - p[0]))),
             (lambda p: p[1] >= y0, lambda p, q: (p[0] + (q[0] - p[0]) * (y0 - p[1]) / (q[1] - p[1]), y0)),
             (lambda p: p[1] <= y1, lambda p, q: (p[0] + (q[0] - p[0]) * (y1 - p[1]) / (q[1] - p[1]), y1))]
    out = list(pts[:-1] if pts[0] == pts[-1] else pts)
    for inside, cut in edges:
        src, out = out, []
        for i, q in enumerate(src):
            p = src[i - 1]
            if inside(q):
                if not inside(p):
                    out.append(cut(p, q))
                out.append(q)
            elif inside(p):
                out.append(cut(p, q))
        if not out:
            return []
    return out


def simplify(pts, tol=0.35):
    """Douglas-Peucker in drawing units, so tiny wiggles don't bloat the SVG."""
    if len(pts) < 3:
        return pts
    (ax, ay), (bx, by) = pts[0], pts[-1]
    L = math.hypot(bx - ax, by - ay)
    best, idx = -1, 0
    for i in range(1, len(pts) - 1):
        px, py = pts[i]
        d = abs((bx - ax) * (ay - py) - (ax - px) * (by - ay)) / L if L else math.hypot(px - ax, py - ay)
        if d > best:
            best, idx = d, i
    if best <= tol:
        return [pts[0], pts[-1]]
    return simplify(pts[:idx + 1], tol)[:-1] + simplify(pts[idx:], tol)


def path_d(pts, close=False):
    d, last = "", None
    for i, (x, y) in enumerate(pts):
        cur = f"{x:.1f} {y:.1f}"
        if cur != last:
            d += ("M" if i == 0 else "L") + cur
        last = cur
    return d + ("Z" if close else "")


def inside_polygon(pt, poly):
    x, y = pt
    r = False
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[i - 1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            r = not r
    return r


# ------------------------------------------------------------------ OSM data: fetch, trim, load

def view_radius(key):
    """Metres from the office to the farthest corner of the map area, plus a margin, so nothing stops short."""
    s = SITES[key]
    px, py = s["pin"]
    return round(max(math.hypot(x - px, y - py) for x in (0, W) for y in (0, MAP_H)) / s["scale"] * 1.1)


def overpass_query(key):
    s = SITES[key]
    a = f'{s["lat"]},{s["lon"]}'
    r = view_radius(key)
    return (f'[out:json][timeout:90];('
            f'way["highway"](around:{r},{a});way["building"](around:{r},{a});way["landuse"](around:{r},{a});'
            f'way["natural"="coastline"](around:4000,{a});way["waterway"](around:{max(r, 2000)},{a});'
            f'way["natural"="water"](around:{max(r, 1500)},{a}););out geom;')


def fetch(key):
    import urllib.parse, urllib.request
    body = urllib.parse.urlencode({"data": overpass_query(key)}).encode()
    req = urllib.request.Request(OVERPASS, data=body, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def kind_of(tags):
    if "building" in tags:
        return "building"
    hw = tags.get("highway")
    if hw in MAJOR + MINOR + LINKS + PATHS + ("service",):
        return "road:" + hw
    if tags.get("natural") == "coastline":
        return "coastline"
    if tags.get("natural") == "water":
        return "water"
    if tags.get("waterway") in ("river", "canal"):
        return "river"
    if tags.get("waterway") in ("stream", "drain", "ditch"):
        return "stream"
    if tags.get("landuse") == "industrial":
        return "industrial"
    return None


AREAS = ("building", "water", "industrial")


def join_coastline(ways):
    """Chain coastline ways end to start (OSM keeps land on the left), so a coast can be closed against the frame."""
    chains = [list(w) for w in ways]
    merged = True
    while merged:
        merged = False
        for i, a in enumerate(chains):
            for j, b in enumerate(chains):
                if i != j and a[-1] == b[0]:
                    chains[i] = a + b[1:]
                    del chains[j]
                    merged = True
                    break
            if merged:
                break
    return chains


def trim(raw, key, margin=60):
    """Keep only the ways that are drawn, clipped to the drawing area plus a margin, coordinates to 6 dp."""
    box = (-margin, -margin, W + margin, MAP_H + margin)
    s = SITES[key]
    cosl = math.cos(math.radians(s["lat"]))

    def unproject(x, y):
        return (round(s["lat"] - (y - s["pin"][1]) / s["scale"] / M_PER_DEG_LAT, 6),
                round(s["lon"] + (x - s["pin"][0]) / s["scale"] / (cosl * M_PER_DEG_LON), 6))

    feats, coast = [], []
    for el in raw["elements"]:
        if el.get("type") != "way" or "geometry" not in el:
            continue
        tags = el.get("tags", {})
        kind = kind_of(tags)
        if kind is None:
            continue
        ll = [(p["lat"], p["lon"]) for p in el["geometry"]]
        if kind == "coastline":
            coast.append(ll)
            continue
        pts = [project(key, *p) for p in ll]
        name = tags.get("name") if kind.startswith("road:") or kind in ("river", "stream") else None
        if kind in AREAS and ll[0] == ll[-1]:
            poly = clip_polygon(pts, box)
            if len(poly) >= 3:
                exact = poly == pts[:-1]
                coords = [[round(a, 6), round(b, 6)] for a, b in ll] if exact else [list(unproject(*p)) for p in poly + poly[:1]]
                feats.append({"kind": kind, "coords": coords})
            continue
        for run in clip_line(pts, box):
            f = {"kind": kind, "coords": [list(unproject(*p)) for p in run]}
            if name:
                f["name"] = name
            feats.append(f)
    for chain in join_coastline(coast):
        for run in clip_line([project(key, *p) for p in chain], box):
            feats.append({"kind": "coastline", "coords": [list(unproject(*p)) for p in run]})
    order = ["industrial", "water", "river", "stream", "coastline", "building"]
    feats.sort(key=lambda f: (order.index(f["kind"]) if f["kind"] in order else len(order), f["kind"], f.get("name", "")))
    return {"source": SOURCE, "site": key, "lat": s["lat"], "lon": s["lon"], "features": feats}


def data_path(key):
    return os.path.join(DATA, f"osm-{key}.json")


def save(data, key):
    os.makedirs(DATA, exist_ok=True)
    with open(data_path(key), "w") as f:
        f.write('{"source": %s, "site": %s, "lat": %s, "lon": %s, "features": [\n' % (
            json.dumps(data["source"], ensure_ascii=False), json.dumps(key), data["lat"], data["lon"]))
        f.write(",\n".join(json.dumps(ft, ensure_ascii=False, separators=(",", ":")) for ft in data["features"]))
        f.write("\n]}\n")


_cache = {}


def load(key):
    if key not in _cache:
        with open(data_path(key)) as f:
            data = json.load(f)
        _cache[key] = [dict(f, pts=[project(key, la, lo) for la, lo in f["coords"]]) for f in data["features"]]
    return _cache[key]


# ------------------------------------------------------------------ drawing

VIEW = (0, 0, W, MAP_H)


def sheet(body, title, key):
    grid = []
    for x in range(0, W + 1, 20):
        grid.append(f'<path d="M{x} 0V{H}" stroke="{SKY}" stroke-opacity="{.16 if x % 100 == 0 else .06}"/>')
    for y in range(0, H + 1, 20):
        grid.append(f'<path d="M0 {y}H{W}" stroke="{SKY}" stroke-opacity="{.16 if y % 100 == 0 else .06}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{title}">'
            f'<title>{title}</title>'
            f'<defs><clipPath id="map-{key}"><rect width="{W}" height="{MAP_H}"/></clipPath>'
            f'<pattern id="hatch-{key}" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            f'<path d="M0 0V8" stroke="{SKY}" stroke-width="1" stroke-opacity=".16"/></pattern></defs>'
            f'<rect width="{W}" height="{H}" fill="{INK}"/>'
            f'<g stroke-width="1">{"".join(grid)}</g>'
            f'<g fill="none" stroke-linecap="round" stroke-linejoin="round">{body}</g></svg>')


def feats(key, *kinds):
    return [f for f in load(key) if f["kind"] in kinds]


def perimeter_t(p):
    """Clockwise position of a point on the frame, from the top-left corner."""
    x, y = p
    e = 1e-6
    if abs(y) < e:
        return x
    if abs(x - W) < e:
        return W + y
    if abs(y - MAP_H) < e:
        return W + MAP_H + (W - x)
    return 2 * W + MAP_H + (MAP_H - y)


CORNERS = [(0, (0, 0)), (W, (W, 0)), (W + MAP_H, (W, MAP_H)), (2 * W + MAP_H, (0, MAP_H))]


def sea_polygons(key):
    """Close each stretch of coastline against the frame. OSM coastlines keep the sea on the right, so walking the
    frame clockwise from where the coast leaves the view to where it next enters encloses the sea."""
    runs = [r for f in feats(key, "coastline") for r in clip_line(f["pts"], VIEW)
            if on_frame(r[0]) and on_frame(r[-1])]
    polys, used = [], set()
    total = 2 * (W + MAP_H)
    for start in range(len(runs)):
        if start in used:
            continue
        poly, i = [], start
        while i not in used:
            used.add(i)
            poly += runs[i]
            t_exit = perimeter_t(runs[i][-1])
            # next entry clockwise from the exit point
            nxt = min(range(len(runs)), key=lambda j: (perimeter_t(runs[j][0]) - t_exit) % total)
            t_next = perimeter_t(runs[nxt][0])
            span = (t_next - t_exit) % total
            for t, c in sorted(CORNERS, key=lambda tc: (tc[0] - t_exit) % total):
                if 0 < (t - t_exit) % total < span:
                    poly.append(c)
            i = nxt
        polys.append(poly)
    return polys


def on_frame(p):
    e = 1e-6
    return abs(p[0]) < e or abs(p[0] - W) < e or abs(p[1]) < e or abs(p[1] - MAP_H) < e


def draw_sea(key):
    polys = sea_polygons(key)
    if not polys:
        return ""
    d = "".join(path_d(simplify(p), True) for p in polys)
    waves = ""
    for row, y in enumerate(range(10, MAP_H, 26)):
        for x in range(-20 + (row % 2) * 40, W, 80):
            waves += f"M{x} {y}q10 -6 20 0t20 0"
    return (f'<clipPath id="sea-{key}"><path d="{d}"/></clipPath>'
            f'<path d="{d}" fill="{BLUE}" fill-opacity=".16" stroke="none"/>'
            f'<path d="{waves}" stroke="{SKY}" stroke-width="1.1" stroke-opacity=".4" clip-path="url(#sea-{key})"/>'
            + "".join(line(simplify(r), CYAN, 2.2) for f in feats(key, "coastline") for r in clip_line(f["pts"], VIEW)))


def draw_land(key):
    out = ""
    for f in feats(key, "industrial"):
        out += f'<path d="{path_d(simplify(f["pts"]), True)}" fill="url(#hatch-{key})" stroke="{SKY}" stroke-width="1" stroke-opacity=".3" stroke-dasharray="4 4"/>'
    for f in feats(key, "water"):
        out += f'<path d="{path_d(simplify(f["pts"]), True)}" fill="{SKY}" fill-opacity=".14" stroke="{SKY}" stroke-width="1.2" stroke-opacity=".8"/>'
    for f in feats(key, "river"):
        out += line(simplify(f["pts"]), SKY, 2.4, .9)
    for f in feats(key, "stream"):
        out += line(simplify(f["pts"]), SKY, 1.3, .75)
    return out


def draw_buildings(key, highlight=None):
    d = "".join(path_d(simplify(f["pts"], .2), True) for f in feats(key, "building") if f is not highlight)
    return f'<path d="{d}" stroke="{SKY}" stroke-width=".9" stroke-opacity=".5" fill="{SKY}" fill-opacity=".05"/>' if d else ""


ROAD_W = {"trunk": 11, "primary": 11, "secondary": 9.5, "tertiary": 9.5,
          **{c: 6.5 for c in LINKS}, **{c: 6.5 for c in MINOR}}


def draw_roads(key):
    roads = [f for f in load(key) if f["kind"].startswith("road:")]
    cls = lambda f: f["kind"][5:]
    service = "".join(path_d(simplify(f["pts"])) for f in roads if cls(f) == "service")
    paths = "".join(path_d(simplify(f["pts"])) for f in roads if cls(f) in PATHS)
    out = f'<path d="{paths}" stroke="{SKY}" stroke-width="1" stroke-opacity=".45" stroke-dasharray="3 4"/>' if paths else ""
    out += f'<path d="{service}" stroke="{SKY}" stroke-width="1.3" stroke-opacity=".75"/>' if service else ""
    double = sorted((f for f in roads if cls(f) in ROAD_W), key=lambda f: ROAD_W[cls(f)])
    by_w = {}
    for f in double:
        by_w.setdefault(ROAD_W[cls(f)], []).append(path_d(simplify(f["pts"])))
    for w, ds in by_w.items():                      # cased: cyan edges, ink carriageway
        out += f'<path d="{"".join(ds)}" stroke="{CYAN}" stroke-width="{w}" stroke-opacity=".9"/>'
    for w, ds in by_w.items():
        out += f'<path d="{"".join(ds)}" stroke="{INK}" stroke-width="{w - 2.6}"/>'
    major = [path_d(simplify(f["pts"])) for f in double if cls(f) in MAJOR]
    if major:                                       # centre line on the main roads
        out += f'<path d="{"".join(major)}" stroke="{SKY}" stroke-width="1" stroke-opacity=".5" stroke-dasharray="8 7"/>'
    return out


def halo_text(x, y, s, size=10, color=SKY, anchor="middle", weight=700, spacing=2, angle=0):
    rot = f' transform="rotate({angle:.1f} {x:.1f} {y:.1f})"' if angle else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" {FONT} font-size="{size}" font-weight="{weight}" letter-spacing="{spacing}" '
            f'fill="{color}" stroke="{INK}" stroke-width="3.5" stroke-opacity=".9" paint-order="stroke" '
            f'text-anchor="{anchor}"{rot}>{s}</text>')


def road_label(key, osm_name, label, near, offset=0, size=10.5, kinds=None, spacing=1.5):
    """Label a named OSM way at the point of it nearest `near`, rotated along it and kept upright.
    Returns "" if the way isn't in view."""
    best = None
    for f in load(key):
        if f.get("name") != osm_name or (kinds and f["kind"] not in kinds):
            continue
        for r in clip_line(f["pts"], VIEW):
            for p, q in zip(r, r[1:]):
                dx, dy = q[0] - p[0], q[1] - p[1]
                L2 = dx * dx + dy * dy
                if L2 == 0:
                    continue
                t = max(0, min(1, ((near[0] - p[0]) * dx + (near[1] - p[1]) * dy) / L2))
                c = (p[0] + t * dx, p[1] + t * dy)
                dist = math.dist(c, near)
                if best is None or dist < best[0]:
                    best = (dist, c, math.degrees(math.atan2(dy, dx)))
    if best is None:
        return ""
    _, (x, y), a = best
    if a > 90:
        a -= 180
    elif a <= -90:
        a += 180
    nx, ny = -math.sin(math.radians(a)), math.cos(math.radians(a))     # "below" the text baseline
    x, y = x + nx * offset, y + ny * offset
    # vertical centre on the road: shift the baseline down by ~0.35 em along the text's own normal
    x, y = x + nx * size * .35, y + ny * size * .35
    return halo_text(x, y, label, size, CYAN, spacing=spacing, angle=a)


def pin(x, y):
    """Map pin whose tip touches (x, y). The ink outline is painted under the fill so the cyan tip is exact."""
    return (f'<path d="M{x} {y}c-4-10-18-22-18-36a18 18 0 0 1 36 0c0 14-14 26-18 36z" fill="{CYAN}" stroke="{INK}" '
            f'stroke-width="2.5" paint-order="stroke"/>'
            + circle(x, y - 36, 7, INK, 0, INK))


def north_arrow(x, y):
    return (circle(x, y, 22, SKY, 1.2, INK, .7)
            + f'<path d="M{x} {y - 18}l9 26-9-6-9 6z" fill="{CYAN}" stroke="none"/>'
            + halo_text(x, y - 28, "N", 12, CYAN, "middle", 700, 0))


def scale_bar(key, x, y, metres, parts=4):
    """True-length scale bar: `metres` at the site's scale, split into alternating blocks."""
    L = metres * SITES[key]["scale"]
    seg = L / parts
    out = (f'<rect x="{x - 12}" y="{y - 20}" width="{L + 40:.1f}" height="32" fill="{INK}" fill-opacity=".88" '
           f'stroke="{SKY}" stroke-width="1" stroke-opacity=".45"/>')
    for i in range(parts):
        out += (f'<rect x="{x + i * seg:.1f}" y="{y}" width="{seg:.1f}" height="6" fill="{CYAN if i % 2 == 0 else INK}" '
                f'stroke="{CYAN}" stroke-width="1"/>')
    out += text(x, y - 7, "0", 11, SKY, "middle", 600, 0)
    out += text(round(x + L, 1), y - 7, f"{metres} m", 11, SKY, "middle", 700, 1)
    return out


# Arial Bold advance widths (per 1000 em) for the capitals, digits and space used in labels
_AW = dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", (722, 722, 722, 722, 667, 611, 778, 722, 278, 556, 722, 611, 833, 722,
                                               778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611)), **{" ": 278})


def text_width(s, size, spacing):
    return sum(_AW.get(c, 556) for c in s) * size / 1000 + spacing * len(s)


def plate(x, y, s, size=12, spacing=3, color=SKY):
    """Area label on a small ink plate with a hairline border, so it reads cleanly over the line work."""
    w = text_width(s, size, spacing) + 13
    return (f'<rect x="{x - 8}" y="{y - size - 5}" width="{w:.0f}" height="{size + 12}" fill="{INK}" fill-opacity=".88" '
            f'stroke="{SKY}" stroke-width="1" stroke-opacity=".45"/>' + text(x, y, s, size, color, "start", 700, spacing))


def attribution(x, y):
    return halo_text(x, y, "© OpenStreetMap contributors", 10.5, SKY, "start", 600, .5)


def coords(x, y, s):
    return (f'<text x="{x}" y="{y}" {MONO} font-size="12" font-weight="600" letter-spacing="1" fill="{CYAN}" '
            f'stroke="{INK}" stroke-width="3.5" paint-order="stroke" text-anchor="end">{s}</text>')


def title_block(dwg, site, sheet):
    """Engineering title block along the bottom: drawing number, site, revision, sheet."""
    y, h = 440, 44
    out = rect(20, y, 760, h, CYAN, 1.5, INK)
    for x in (230, 430, 530):
        out += line([(x, y), (x, y + h)], CYAN, 1.5)
    out += text(36, y + 28, f"DWG {dwg}", 13, CYAN, "start", 700, 2)
    out += text(246, y + 28, site, 13, CYAN, "start", 700, 2)
    out += text(446, y + 28, "REV A", 13, SKY, "start", 700, 2)
    out += text(546, y + 28, f"SHEET {sheet} OF 2", 13, SKY, "start", 700, 2)
    return out


def bws_building(key):
    """The building polygon that contains the office point, or the nearest one."""
    px, py = PINS[key]
    best = None
    for f in feats(key, "building"):
        pts = f["pts"]
        if inside_polygon((px, py), pts):
            return f
        d = min(math.dist((px, py), p) for p in pts)
        if best is None or d < best[0]:
            best = (d, f)
    return best[1] if best else None


def map_frame(body, key):
    return (f'<g clip-path="url(#map-{key})">{body}</g>'
            + line([(0, MAP_H), (W, MAP_H)], SKY, 1, .35))


def miri():
    k = "miri"
    hl = bws_building(k)
    m = draw_land(k) + draw_sea(k) + draw_buildings(k, hl) + draw_roads(k)
    m += f'<path d="{path_d(hl["pts"], True)}" fill="{BLUE}" fill-opacity=".55" stroke="{CYAN}" stroke-width="2"/>'
    m += road_label(k, "Jalan Prunus 1", "JLN PRUNUS 1", (330, 215), offset=11)
    m += road_label(k, "Jalan Pujut-Lutong", "JLN PUJUT-LUTONG", (640, 150), offset=-14, kinds=("road:trunk",))
    m += plate(40, 36, "PIASAU INDUSTRIAL ESTATE PH III")
    xs = [p[0] for p in hl["pts"]]
    m += halo_text(max(xs) + 8, min(p[1] for p in hl["pts"]) - 4, "BWS · LOT 1743", 12, CYAN, "start", 700, 2)
    m += pin(*PINS[k])
    m += scale_bar(k, 46, 398, 200) + attribution(40, 422)
    m += north_arrow(740, 62) + coords(780, 422, "4.4469° N  114.0116° E")
    b = map_frame(m, k) + title_block("BWS-LOC-01", "MIRI HQ", 1)
    return sheet(b, "Site drawing of the BWS Engineering main office location, Piasau Industrial Estate, Miri", k)


def bintulu():
    k = "bintulu"
    m = draw_land(k) + draw_sea(k) + draw_buildings(k) + draw_roads(k)
    x, y = PINS[k]
    m += circle(x, y, 16, CYAN, 1, "none", .7, dash="3 3")
    m += f'<rect x="{x - 9}" y="{y - 9}" width="18" height="18" fill="{BLUE}" fill-opacity=".55" stroke="{CYAN}" stroke-width="2" transform="rotate(45 {x} {y})"/>'
    m += road_label(k, "MLNG Road", "MLNG ROAD", (468, 36), offset=-11, size=10)
    m += halo_text(x + 26, y + 26, "BWS · LOT 782", 12, CYAN, "start", 700, 2)
    m += plate(40, 36, "KIDURONG INDUSTRIAL ESTATE")
    m += pin(x, y)
    m += scale_bar(k, 612, 380, 500, 5) + attribution(40, 422)
    m += north_arrow(740, 62) + coords(780, 422, "3.2725° N  113.0802° E")
    b = map_frame(m, k) + title_block("BWS-LOC-02", "BINTULU", 2)
    return sheet(b, "Site drawing of the BWS Engineering office location, Kidurong, Bintulu", k)


if __name__ == "__main__":
    if "--fetch" in sys.argv[1:]:
        for key in SITES:
            print("fetching", key)
            save(trim(fetch(key), key), key)
    for name, fn in [("loc-miri", miri), ("loc-bintulu", bintulu)]:
        svg = fn()
        with open(os.path.join(OUT, name + ".svg"), "w") as f:
            f.write(svg)
        print(name, len(svg.encode()), pin_style(name[4:]))
