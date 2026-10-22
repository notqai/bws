# Draws the "project locations" map on projects.html: a blueprint sheet of northern Borneo (Sarawak, Brunei,
# Sabah, Labuan) with a pin per place where BWS key projects are, plus an inset of Peninsular Malaysia.
# Same style as make_locations.py / make_illustrations.py. The SVG is inlined in the page by generate_site.py
# (import make_project_map; svg(PROJECTS)) so each pin can be a link that filters the Key projects list.
#
# Data:
#   - Projects: the 4th field (location) of PROJECTS in generate_site.py, read with ast (the generator is never
#     imported here, because importing it rebuilds the site). Each location is split into place names, which must
#     match a PLACES entry exactly; a location naming several places counts once for each.
#   - Coastline and borders: Natural Earth 1:10m land, admin-0 boundary lines and admin-1 boundary lines (public
#     domain, naturalearthdata.com), clipped to the two frames, simplified, cached in tools/data/ne-project-map.json.
#   - Place coordinates: OpenStreetMap Nominatim (© OpenStreetMap contributors, ODbL), cached in
#     tools/data/nominatim-places.json and copied (rounded) into PLACES below so the table stays reviewable.
# Run: python3 tools/make_project_map.py           (summary of places and counts; draws from the cache, no network)
#      python3 tools/make_project_map.py --fetch   (re-downloads Natural Earth and Nominatim, rewrites the cache)
import ast, html, json, math, os, re, sys, time

import make_locations as ml
from make_illustrations import INK, BLUE, SKY, CYAN, FONT

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
GEO_FILE = os.path.join(DATA, "ne-project-map.json")
PLACES_FILE = os.path.join(DATA, "nominatim-places.json")
GENERATOR = os.path.join(HERE, "generate_site.py")
USER_AGENT = ml.USER_AGENT
NE_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/{}.geojson"
NOMINATIM = "https://nominatim.openstreetmap.org/search"
LIST_ID = "track"                      # id of the Key projects section the pins link to
ATTRIBUTION = "© OpenStreetMap contributors · Natural Earth"

# Each place: EN name (a proper noun, also used in BM), lat/lon (from Nominatim unless marked manual),
# label offset (dx, dy) from the pin in drawing units (dx < 0: label ends there, dx > 0: starts there, 0: centred),
# match: the exact place names in PROJECTS locations that count for it, q: the Nominatim query used by --fetch,
# want: the Nominatim address types accepted (default: a settlement; Nominatim also returns same-named districts).
PLACES = {
    "kuching_division": {"name": "Kuching Division", "lat": 1.8053, "lon": 109.7783, "label": (8, -58),
                         "match": ["Kuching Division"], "q": "Sematan, Sarawak",
                         # manual choice of point: the only "Kuching Division" project is the Sematan Industrial
                         # Area, so the pin is at Sematan rather than the division's centroid (1.53 N 110.05 E)
                         "manual": True},
    "padawan":    {"name": "Padawan", "lat": 1.4277, "lon": 110.3256, "label": (6, 34), "match": ["Padawan"],
                   "q": "Padawan, Sarawak"},
    "samarahan":  {"name": "Samarahan", "lat": 1.4637, "lon": 110.4891, "label": (16, -4), "match": ["Samarahan"],
                   "q": "Kota Samarahan, Sarawak"},
    "bintulu":    {"name": "Bintulu", "lat": 3.1874, "lon": 113.0473, "label": (-30, -24), "match": ["Bintulu"],
                   "q": "Bintulu, Sarawak", "base": True},
    "miri":       {"name": "Miri", "lat": 4.3940, "lon": 113.9880, "label": (-22, 6), "match": ["Miri"],
                   "q": "Miri, Sarawak", "base": True},
    "mulu":       {"name": "Mulu", "lat": 4.0444, "lon": 114.8086, "label": (-12, 18), "match": ["Mulu"],
                   "q": "Mulu, Sarawak"},
    "telang_usan": {"name": "Telang Usan", "lat": 3.3172, "lon": 114.8258, "label": (10, 20), "match": ["Telang Usan"],
                    "q": "Telang Usan, Sarawak", "want": ("county",)},   # a district: the pin is its centroid
    "bario":      {"name": "Bario", "lat": 3.7479, "lon": 115.4604, "label": (12, 4), "match": ["Bario"],
                   "q": "Bario, Sarawak"},
    "lawas":      {"name": "Lawas", "lat": 4.8597, "lon": 115.4083, "label": (12, 16), "match": ["Lawas"],
                   "q": "Lawas, Sarawak"},
    "sipitang":   {"name": "Sipitang", "lat": 5.0764, "lon": 115.5494, "label": (12, -4), "match": ["Sipitang"],
                   "q": "Sipitang, Sabah"},
    "labuan":     {"name": "Labuan", "lat": 5.3168, "lon": 115.2199, "label": (12, -16), "match": ["Labuan"],
                   "q": "Labuan", "want": ("state",)},                 # the federal territory (island)
    "port_dickson": {"name": "Port Dickson", "lat": 2.5262, "lon": 101.8106, "label": (10, -10),
                     "match": ["Port Dickson"], "q": "Port Dickson, Negeri Sembilan"},
    "pengerang":  {"name": "Pengerang", "lat": 1.3944, "lon": 104.2155, "label": (12, -4), "match": ["Pengerang"],
                   "q": "Pengerang, Johor"},
}
# State / territory names in the location strings; they only say which state a place is in.
SETTLEMENT = ("city", "town", "village", "suburb", "hamlet", "municipality")
REGIONS = {"Sarawak", "Sabah", "Johor", "Negeri Sembilan"}

# Geographic frames (degrees). The main frame is northern Borneo; the inset is Peninsular Malaysia.
FRAMES = {
    "borneo":    {"lat0": 0.75, "lat1": 7.55, "lon0": 109.4, "lon1": 119.6},
    "peninsula": {"lat0": 1.05, "lat1": 6.75, "lon0": 99.6, "lon1": 106.6},   # east: room for labels
}
PENINSULA = {"port_dickson", "pengerang"}

W = 960
TB_H = 64                             # title block strip below the map


# ------------------------------------------------------------------ projects → places

def load_projects(path=GENERATOR):
    """PROJECTS from generate_site.py, parsed with ast (never imported: importing it rebuilds the site)."""
    with open(path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "PROJECTS" for t in node.targets):
            return ast.literal_eval(node.value)
    raise RuntimeError("PROJECTS not found in " + path)


_BY_NAME = {m: k for k, p in PLACES.items() for m in p["match"]}


def places_for(location):
    """Place keys named by one PROJECTS location string, e.g. "Bario, Mulu &amp; Telang Usan, Sarawak"."""
    s = html.unescape(location)
    keys = []
    for token in re.split(r"\s*(?:,|&|–|/)\s*", s):
        token = token.strip()
        if not token or token in REGIONS:
            continue
        if token not in _BY_NAME:
            raise ValueError(f"Unmapped project location {s!r}: no PLACES entry matches {token!r}. "
                             f"Add it to a 'match' list in tools/make_project_map.py")
        if _BY_NAME[token] not in keys:
            keys.append(_BY_NAME[token])
    if not keys:
        raise ValueError(f"Unmapped project location {s!r}: it names no place")
    return keys


def counts(projects):
    c = {k: 0 for k in PLACES}
    for p in projects:
        for k in places_for(p[3]):
            c[k] += 1
    return {k: n for k, n in c.items() if n}


# ------------------------------------------------------------------ projection

class Proj:
    """Local equirectangular projection (as make_locations.project), centred on a frame, north up, y down."""

    def __init__(self, frame, scale, ox=0.0, oy=0.0):
        f = FRAMES[frame]
        self.lat_c, self.lon_c = (f["lat0"] + f["lat1"]) / 2, (f["lon0"] + f["lon1"]) / 2
        self.cos = math.cos(math.radians(self.lat_c))
        self.s = scale                                       # drawing units per metre
        self.w = (f["lon1"] - f["lon0"]) * self.cos * ml.M_PER_DEG_LON * scale
        self.h = (f["lat1"] - f["lat0"]) * ml.M_PER_DEG_LAT * scale
        self.ox, self.oy = ox, oy                            # top-left corner of the frame in the drawing

    def __call__(self, lat, lon):
        return (self.ox + self.w / 2 + (lon - self.lon_c) * self.cos * ml.M_PER_DEG_LON * self.s,
                self.oy + self.h / 2 - (lat - self.lat_c) * ml.M_PER_DEG_LAT * self.s)

    def inv(self, x, y):
        return (round(self.lat_c - (y - self.oy - self.h / 2) / self.s / ml.M_PER_DEG_LAT, 4),
                round(self.lon_c + (x - self.ox - self.w / 2) / self.s / (self.cos * ml.M_PER_DEG_LON), 4))

    @property
    def box(self):
        return (self.ox, self.oy, self.ox + self.w, self.oy + self.h)


f0 = FRAMES["borneo"]
SCALE = W / ((f0["lon1"] - f0["lon0"]) * math.cos(math.radians((f0["lat0"] + f0["lat1"]) / 2)) * ml.M_PER_DEG_LON)
MAIN = Proj("borneo", SCALE)
MAP_H = round(MAIN.h)
H = MAP_H + TB_H
INSET_SCALE = SCALE * 0.5
INSET = Proj("peninsula", INSET_SCALE, 16, 16)


# ------------------------------------------------------------------ fetch + trim (network only with --fetch)

def http_get(url, params=None, tries=4):
    import urllib.parse, urllib.request
    if params:
        url += "?" + urllib.parse.urlencode(params)
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=180) as r:
                return r.read()
        except Exception as e:                      # flaky network: back off and retry
            last = e
            time.sleep(2 * (i + 1))
    raise SystemExit(f"BLOCKED: could not download {url} after {tries} tries ({last}). Cache left unchanged.")


def rings_of(geom):
    if not geom:
        return []
    if geom["type"] == "Polygon":
        return [geom["coordinates"][0]]
    if geom["type"] == "MultiPolygon":
        return [p[0] for p in geom["coordinates"]]
    return []


def lines_of(geom):
    if not geom:
        return []
    if geom["type"] == "LineString":
        return [geom["coordinates"]]
    if geom["type"] == "MultiLineString":
        return geom["coordinates"]
    return []


def simplify(pts, tol):
    """Douglas-Peucker like make_locations.simplify, but iterative: Natural Earth rings have thousands of points,
    too deep for the recursive version."""
    if len(pts) < 3:
        return list(pts)
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        i, j = stack.pop()
        (ax, ay), (bx, by) = pts[i], pts[j]
        L = math.hypot(bx - ax, by - ay)
        best, idx = -1.0, 0
        for k in range(i + 1, j):
            px, py = pts[k]
            d = abs((bx - ax) * (ay - py) - (ax - px) * (by - ay)) / L if L else math.hypot(px - ax, py - ay)
            if d > best:
                best, idx = d, k
        if best > tol:
            keep[idx] = True
            stack += [(i, idx), (idx, j)]
    return [p for p, k in zip(pts, keep) if k]


def area(pts):
    return abs(sum(p[0] * q[1] - q[0] * p[1] for p, q in zip(pts, pts[1:] + pts[:1]))) / 2


def trim_frame(frame, land, country, state, tol_m=250, min_area_km2=4, margin=0.25):
    """Clip the Natural Earth geometry to a frame (plus a margin, in degrees), simplify it (Douglas-Peucker, in
    metres) and drop tiny islets. Coordinates are stored as [lat, lon] to 4 dp (about 11 m)."""
    f = FRAMES[frame]
    p = Proj(frame, 1.0)                                       # drawing units = metres
    m = margin * ml.M_PER_DEG_LAT
    box = (-m, -m, p.w + m, p.h + m)
    lo0, lo1, la0, la1 = f["lon0"] - 1, f["lon1"] + 1, f["lat0"] - 1, f["lat1"] + 1
    near = lambda pts: any(lo0 <= x <= lo1 and la0 <= y <= la1 for x, y in pts[::5] + pts[-1:])
    out = {"land": [], "country": [], "state": []}
    for ring in land:
        if not near(ring):
            continue
        poly = ml.clip_polygon([p(lat, lon) for lon, lat in ring], box)
        if len(poly) < 3 or area(poly) < min_area_km2 * 1e6:
            continue
        poly = simplify(poly + poly[:1], tol_m)[:-1]
        if len(poly) >= 3:
            out["land"].append([list(p.inv(*q)) for q in poly])
    for kind, lines in (("country", country), ("state", state)):
        for ln in lines:
            if not near(ln):
                continue
            for run in ml.clip_line([p(lat, lon) for lon, lat in ln], box):
                run = simplify(run, tol_m)
                out[kind].append([list(p.inv(*q)) for q in run])
    return out


def fetch_geo():
    get = lambda name: json.loads(http_get(NE_URL.format(name)))
    land = [r for ft in get("ne_10m_land")["features"] for r in rings_of(ft["geometry"])]
    country = [ln for ft in get("ne_10m_admin_0_boundary_lines_land")["features"] for ln in lines_of(ft["geometry"])]
    state = [ln for ft in get("ne_10m_admin_1_states_provinces_lines")["features"]
             if (ft["properties"].get("ADM0_A3") == "MYS") for ln in lines_of(ft["geometry"])]
    data = {"source": "Natural Earth 1:10m land, admin-0 and admin-1 boundary lines (public domain), "
                      "clipped and simplified by tools/make_project_map.py --fetch",
            "frames": {fr: trim_frame(fr, land, country, state if fr == "borneo" else [])
                       for fr in FRAMES}}
    os.makedirs(DATA, exist_ok=True)
    with open(GEO_FILE, "w") as fh:
        fh.write('{"source": %s, "frames": {\n' % json.dumps(data["source"]))
        frs = []
        for fr, d in data["frames"].items():
            parts = [f'"{k}": [\n' + ",\n".join(json.dumps(x, separators=(",", ":")) for x in d[k]) + "\n]" for k in d]
            frs.append(f'"{fr}": {{\n' + ",\n".join(parts) + "\n}")
        fh.write(",\n".join(frs) + "\n}}\n")


def fetch_places():
    out = {}
    for key, p in PLACES.items():
        res = json.loads(http_get(NOMINATIM, {"format": "json", "q": p["q"], "countrycodes": "my", "limit": 5}))
        time.sleep(1.1)                                   # Nominatim usage policy: at most 1 request per second
        res = [r for r in res if (r.get("addresstype") or r.get("type")) in p.get("want", SETTLEMENT)]
        if not res:
            print(f"  {key}: Nominatim found no {'/'.join(p.get('want', SETTLEMENT))} for {p['q']!r}; set lat/lon manually")
            continue
        r = res[0]
        out[key] = {"q": p["q"], "lat": round(float(r["lat"]), 4), "lon": round(float(r["lon"]), 4),
                    "type": r.get("addresstype") or r.get("type"), "display_name": r["display_name"]}
    with open(PLACES_FILE, "w") as fh:
        json.dump({"source": "OpenStreetMap Nominatim (© OpenStreetMap contributors, ODbL)", "places": out},
                  fh, ensure_ascii=False, indent=1)
        fh.write("\n")


def check_places_against_cache(tol_km=2.0):
    """Places (not marked manual) must agree with the cached Nominatim result."""
    with open(PLACES_FILE, encoding="utf-8") as fh:
        cache = json.load(fh)["places"]
    bad = []
    for k, p in PLACES.items():
        c = cache.get(k)
        if c is None:
            bad.append(f"{k}: not in {os.path.basename(PLACES_FILE)}")
            continue
        d = math.hypot((p["lat"] - c["lat"]) * 110.54, (p["lon"] - c["lon"]) * 111.32 * math.cos(math.radians(p["lat"])))
        if d > tol_km and not p.get("manual"):
            bad.append(f"{k}: PLACES {p['lat']}, {p['lon']} is {d:.1f} km from Nominatim {c['lat']}, {c['lon']}")
    return bad


# ------------------------------------------------------------------ drawing

_geo = None


def geo():
    global _geo
    if _geo is None:
        with open(GEO_FILE, encoding="utf-8") as fh:
            _geo = json.load(fh)["frames"]
    return _geo


def rnd(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def pd(pts, close=False):
    """Compact path data: absolute start, then relative steps, one decimal."""
    if not pts:
        return ""
    q = [(round(x * 2) / 2, round(y * 2) / 2) for x, y in pts]      # half-unit grid keeps relative steps exact
    d = f"M{rnd(q[0][0])} {rnd(q[0][1])}"
    for (x0, y0), (x1, y1) in zip(q, q[1:]):
        dx, dy = x1 - x0, y1 - y0
        if dx or dy:
            d += f"l{rnd(dx)} {rnd(dy)}"
    return d + ("z" if close else "")


def land_paths(frame, proj, tol=.45):
    g = geo()[frame]
    land = "".join(pd(simplify([proj(*c) for c in r] + [proj(*r[0])], tol)[:-1], True) for r in g["land"])
    country = "".join(pd(simplify([proj(*c) for c in ln], tol)) for ln in g["country"])
    state = "".join(pd(simplify([proj(*c) for c in ln], tol)) for ln in g["state"])
    out = f'<path d="{land}" fill="{INK}" stroke="{CYAN}" stroke-width="1.3" stroke-linejoin="round"/>'
    if country:
        out += f'<path d="{country}" fill="none" stroke="{SKY}" stroke-width="1.3" stroke-opacity=".75" stroke-dasharray="7 3 2 3"/>'
    if state:
        out += f'<path d="{state}" fill="none" stroke="{SKY}" stroke-width="1.1" stroke-opacity=".6" stroke-dasharray="2 3"/>'
    return out


def defs():
    minor = "".join(f"M{v} 0V100M0 {v}H100" for v in (20, 40, 60, 80))
    return ('<defs>'
            f'<clipPath id="pm-clip"><rect width="{W}" height="{MAP_H}"/></clipPath>'
            f'<clipPath id="pm-clip-inset"><rect x="{rnd(INSET.ox)}" y="{rnd(INSET.oy)}" width="{rnd(INSET.w)}" height="{rnd(INSET.h)}"/></clipPath>'
            '<pattern id="pm-grid" width="100" height="100" patternUnits="userSpaceOnUse">'
            f'<path d="{minor}" stroke="{SKY}" stroke-opacity=".06" fill="none"/>'
            f'<path d="M0 0V100M0 0H100" stroke="{SKY}" stroke-opacity=".16" fill="none"/></pattern>'
            '<pattern id="pm-waves" width="80" height="52" patternUnits="userSpaceOnUse">'
            f'<path d="M-20 10q10-6 20 0t20 0M60 10q10-6 20 0t20 0M20 36q10-6 20 0t20 0" stroke="{SKY}" '
            'stroke-width="1.1" stroke-opacity=".3" fill="none"/></pattern>'
            '</defs>')


def sea(x, y, w, h):
    return (f'<rect x="{rnd(x)}" y="{rnd(y)}" width="{rnd(w)}" height="{rnd(h)}" fill="{BLUE}" fill-opacity=".3"/>'
            f'<rect x="{rnd(x)}" y="{rnd(y)}" width="{rnd(w)}" height="{rnd(h)}" fill="url(#pm-waves)"/>')


def faint(x, y, s, size=11, spacing=5, anchor="middle", op=.55):
    return (f'<text x="{rnd(x)}" y="{rnd(y)}" {FONT} font-size="{size}" font-weight="700" letter-spacing="{spacing}" '
            f'fill="{SKY}" fill-opacity="{op}" text-anchor="{anchor}">{s}</text>')


def graticule(proj, frame, step=2, inset=False):
    """Degree ticks and labels along the frame edges."""
    f = FRAMES[frame]
    x0, y0, x1, y1 = proj.box
    out, d = "", ""
    lon = math.ceil(f["lon0"] / step) * step
    while lon < f["lon1"]:
        x, _ = proj(f["lat0"], lon)
        d += f"M{rnd(x)} {rnd(y0)}v6M{rnd(x)} {rnd(y1)}v-6"
        if not inset:
            out += ml.halo_text(x + 3, y1 - 8, f"{lon}°E", 9.5, SKY, "start", 600, .5)
        lon += step
    lat = math.ceil(f["lat0"] / step) * step
    while lat < f["lat1"]:
        _, y = proj(lat, f["lon0"])
        d += f"M{rnd(x0)} {rnd(y)}h6M{rnd(x1)} {rnd(y)}h-6"
        if not inset:
            out += ml.halo_text(x1 - 9, y - 4, f"{lat}°N", 9.5, SKY, "end", 600, .5)
        lat += step
    return f'<path d="{d}" stroke="{CYAN}" stroke-width="1.2" fill="none"/>' + out


def radius(n):
    return max(6.0, 4.8 * math.sqrt(n))


def pin(key, n, proj, label_word):
    p = PLACES[key]
    x, y = proj(p["lat"], p["lon"])
    r = radius(n)
    dx, dy = p["label"]
    anchor = "end" if dx < 0 else "start" if dx > 0 else "middle"
    lx, ly = x + dx, y + dy
    name = p["name"]
    unit = "project" if n == 1 else "projects"
    body = ""
    gap = math.hypot(dx, dy)
    if gap > r + 14:                                   # leader from the circle edge towards the label
        ux, uy = dx / gap, dy / gap
        ex, ey = lx - ux * 4, ly - uy * 4
        body += (f'<path d="M{rnd(x + ux * (r + 2))} {rnd(y + uy * (r + 2))}L{rnd(ex)} {rnd(ey)}" stroke="{SKY}" '
                 'stroke-width="1" stroke-opacity=".8"/>')
    body += f'<circle class="pm-ring" cx="{rnd(x)}" cy="{rnd(y)}" r="{rnd(r + 5)}"/>'
    body += (f'<circle class="pm-dot" cx="{rnd(x)}" cy="{rnd(y)}" r="{rnd(r)}" fill="{BLUE}" fill-opacity=".6" '
             f'stroke="{CYAN}" stroke-width="2"/>')
    if p.get("base"):                                  # BWS base: dashed outer ring and a diamond, as on BWS-LOC-02
        body += (f'<circle cx="{rnd(x)}" cy="{rnd(y)}" r="{rnd(r + 9)}" stroke="{CYAN}" stroke-width="1.2" '
                 'fill="none" stroke-opacity=".8" stroke-dasharray="3 3"/>')
        body += (f'<rect x="{rnd(x - 4.5)}" y="{rnd(y - 4.5)}" width="9" height="9" fill="{CYAN}" '
                 f'transform="rotate(45 {rnd(x)} {rnd(y)})"/>')
    else:
        body += f'<circle cx="{rnd(x)}" cy="{rnd(y)}" r="2" fill="{CYAN}"/>'
    hit = max(r + 6, 14)                               # invisible, larger tap target
    body += f'<circle cx="{rnd(x)}" cy="{rnd(y)}" r="{rnd(hit)}" fill="#000" fill-opacity="0"/>'
    tag = (f'<tspan class="pm-b" x="{rnd(lx)}" dy="1.35em">{label_word}</tspan>') if p.get("base") else ""
    body += (f'<text class="pm-l" x="{rnd(lx)}" y="{rnd(ly)}" text-anchor="{anchor}" dominant-baseline="central">'
             f'<tspan>{name.upper()}</tspan><tspan class="pm-c"> · {n}</tspan>{tag}</text>')
    return (f'<a href="#{LIST_ID}" class="pm-pin" data-place="{name}" '
            f'aria-label="{name}: {n} {unit}, show {"it" if n == 1 else "them"} in the list">{body}</a>')


def scale_bar(x, y, km=200, parts=4):
    L = km * 1000 * SCALE
    seg = L / parts
    out = (f'<rect x="{rnd(x - 14)}" y="{rnd(y - 22)}" width="{rnd(L + 54)}" height="34" fill="{INK}" fill-opacity=".9" '
           f'stroke="{SKY}" stroke-width="1" stroke-opacity=".45"/>')
    for i in range(parts):
        out += (f'<rect x="{rnd(x + i * seg)}" y="{y}" width="{rnd(seg)}" height="6" fill="{CYAN if i % 2 == 0 else INK}" '
                f'stroke="{CYAN}" stroke-width="1"/>')
    out += ml.text(x, y - 7, "0", 11, SKY, "middle", 600, 0)
    out += ml.text(rnd(x + L / 2), y - 7, str(km // 2), 11, SKY, "middle", 600, 0)
    out += ml.text(rnd(x + L), y - 7, f"{km} km", 11, SKY, "middle", 700, 1)
    return out


def title_block(n_projects, n_places):
    y, h = MAP_H + 10, TB_H - 18
    out = ml.rect(16, y, W - 32, h, CYAN, 1.5, INK)
    cols = (16, 236, 556, 676)
    for x in cols[1:]:
        out += ml.line([(x, y), (x, y + h)], CYAN, 1.5)
    ty = y + 29
    out += ml.text(32, ty, "DWG BWS-PRJ-01", 13, CYAN, "start", 700, 2)
    out += ml.text(252, ty, "PROJECT LOCATIONS", 13, CYAN, "start", 700, 2)
    out += ml.text(572, ty, "REV A", 13, SKY, "start", 700, 2)
    out += ml.text(692, ty, "SARAWAK · SABAH · LABUAN", 12, SKY, "start", 700, 1.5)
    return f'<g class="pm-tb">{out}</g>'


def svg(projects=None):
    """The inline SVG for projects.html. projects: the PROJECTS list (read from generate_site.py if None)."""
    projects = load_projects() if projects is None else projects
    c = counts(projects)
    borneo = [k for k in c if k not in PENINSULA]
    peninsula = [k for k in c if k in PENINSULA]
    total = sum(c.values())

    m = sea(0, 0, W, MAP_H) + land_paths("borneo", MAIN)
    m += faint(*MAIN(2.0, 113.4), "SARAWAK", 13, 8)
    m += faint(*MAIN(4.9, 117.3), "SABAH", 13, 8)
    m += faint(*MAIN(4.5, 114.7), "BRUNEI", 9, 2.5)
    m += faint(*MAIN(1.35, 115.6), "INDONESIA", 12, 8, op=.4)
    m += faint(*MAIN(6.9, 114.9), "SOUTH CHINA SEA", 12, 7, op=.5)
    m += f'<rect width="{W}" height="{MAP_H}" fill="url(#pm-grid)"/>'
    m += graticule(MAIN, "borneo")
    # inset: Peninsular Malaysia, only if a project is there
    inset = ""
    if peninsula:
        x0, y0, x1, y1 = INSET.box
        inset += f'<rect x="{rnd(x0 - 6)}" y="{rnd(y0 - 6)}" width="{rnd(INSET.w + 12)}" height="{rnd(INSET.h + 12)}" fill="{INK}"/>'
        inset += f'<g clip-path="url(#pm-clip-inset)">{sea(x0, y0, INSET.w, INSET.h)}{land_paths("peninsula", INSET, .35)}'
        inset += faint(*INSET(5.0, 100.95), "THAILAND", 9, 3, op=.45) + faint(*INSET(1.45, 100.6), "SUMATRA", 9, 3, op=.4)
        inset += '</g>' + graticule(INSET, "peninsula", inset=True)
        inset += ml.rect(rnd(x0), rnd(y0), rnd(INSET.w), rnd(INSET.h), CYAN, 1.5)
        inset += ml.halo_text(x1 - 10, y0 + 22, "PENINSULAR MALAYSIA", 11, CYAN, "end", 700, 2)
    pins = "".join(pin(k, c[k], MAIN, "BWS BASE") for k in sorted(borneo, key=lambda k: -c[k]))
    pins += "".join(pin(k, c[k], INSET, "BWS BASE") for k in sorted(peninsula, key=lambda k: -c[k]))
    deco = (m + ml.north_arrow(W - 44, 50)
            + scale_bar(W - 290, MAP_H - 46) + ml.halo_text(W - 14, MAP_H - 12, ATTRIBUTION, 10.5, SKY, "end", 600, .5)
            + inset)
    title = "Map of BWS project locations"
    places_txt = ", ".join(f"{PLACES[k]['name']} {c[k]}" for k in sorted(c, key=lambda k: -c[k]))
    desc = (f"Blueprint map of northern Borneo with an inset of Peninsular Malaysia, marking the places of BWS key "
            f"projects. Each marker is a link that shows that place's projects in the list below.")
    body = (f'<g aria-hidden="true"><g clip-path="url(#pm-clip)">{deco}</g>'
            + ml.line([(0, MAP_H), (W, MAP_H)], SKY, 1, .35) + title_block(len(projects), len(c)) + '</g>'
            + f'<g class="pm-pins" {FONT} font-weight="700">{pins}</g>')
    return (f'<svg class="pm-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="group" '
            f'aria-labelledby="pm-title" aria-describedby="pm-desc">'
            f'<title id="pm-title">{title}</title><desc id="pm-desc">{desc}</desc>'
            f'{defs()}<rect width="{W}" height="{H}" fill="{INK}"/>{body}</svg>')


# Label sizes in drawing units: desktop, and phones (see .pm-l / .pm-b in src/css/07-page-additions.css)
LABEL_SIZES = {"desktop": (13, 1.5, 9.5, 2), "phone": (26, .5, 17, 1)}


def label_boxes(c, size, spacing, tag_size, tag_spacing):
    """Approximate boxes (x0, y0, x1, y1) of each pin's label and circle, for the overlap check."""
    boxes = []
    for k, n in c.items():
        p = PLACES[k]
        proj = INSET if k in PENINSULA else MAIN
        x, y = proj(p["lat"], p["lon"])
        r = radius(n) + (9 if p.get("base") else 0)
        boxes.append((k, "pin", (x - r, y - r, x + r, y + r)))
        dx, dy = p["label"]
        lx, ly = x + dx, y + dy
        lines = [(f"{p['name'].upper()} · {n}", size, spacing, ly)]
        if p.get("base"):
            lines.append(("PANGKALAN BWS", tag_size, tag_spacing, ly + 1.35 * tag_size))   # the longer (BM) tag
        for t, sz, sp, yy in lines:
            w = ml.text_width(t, sz, sp)
            x0 = lx - w if dx < 0 else lx if dx > 0 else lx - w / 2
            boxes.append((k, "label", (x0, yy - .42 * sz, x0 + w, yy + .42 * sz)))
    return boxes


def label_problems(c):
    """Labels that overlap another label or pin, leave the map, or (main map) run under the inset."""
    out = []
    ib = (INSET.ox - 6, INSET.oy - 6, INSET.ox + INSET.w + 6, INSET.oy + INSET.h + 6)
    hit = lambda a, b: a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]
    for mode, sizes in LABEL_SIZES.items():
        boxes = label_boxes(c, *sizes)
        for i, (k, kind, b) in enumerate(boxes):
            if kind != "label":
                continue
            if b[0] < 2 or b[1] < 2 or b[2] > W - 2 or b[3] > MAP_H - 2:
                out.append(f"{mode}: {k} label leaves the map")
            if k not in PENINSULA and hit(b, ib):
                out.append(f"{mode}: {k} label runs under the inset")
            for k2, kind2, b2 in boxes[i + 1:] + boxes[:i]:
                if k2 != k and hit(b, b2):
                    out.append(f"{mode}: {k} label overlaps {k2} {kind2}")
    return sorted(set(out))


def summary(projects):
    c = counts(projects)
    print(f"{len(projects)} key projects, {sum(c.values())} pins over {len(c)} places:")
    for k in sorted(c, key=lambda k: (-c[k], k)):
        p = PLACES[k]
        print(f"  {p['name']:<18}{c[k]:>3}   {p['lat']:.4f} N {p['lon']:.4f} E{'   (manual)' if p.get('manual') else ''}"
              f"{'   inset' if k in PENINSULA else ''}")
    unused = [k for k in PLACES if k not in c]
    if unused:
        print("  unused PLACES:", ", ".join(unused))


if __name__ == "__main__":
    if "--fetch" in sys.argv[1:]:
        print("fetching Natural Earth (large download) ...")
        fetch_geo()
        print("fetching Nominatim places (1 request per second) ...")
        fetch_places()
        for line in check_places_against_cache():
            print("  check:", line)
    projects = load_projects()
    summary(projects)
    s = svg(projects)
    print(f"SVG {len(s.encode())} bytes")
    for line in label_problems(counts(projects)):
        print("  label:", line)
