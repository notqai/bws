# Draws the "project locations" map on projects.html: a blueprint sheet of northern Borneo (Sarawak, Brunei,
# Sabah, Labuan) with a pin per place where BWS has carried out contracts, plus an inset of Peninsular Malaysia.
# Same style as make_locations.py / make_illustrations.py. The SVG is inlined in the page by generate_site.py
# (import make_project_map; svg(ALL_PROJECTS)) so each pin can be a link that filters the full project table.
#
# Data:
#   - Contracts: ALL_PROJECTS in generate_site.py (BWS's full work-experience record), read with ast (the generator
#     is never imported here, because importing it rebuilds the site). The record gives no location field, so
#     CONTRACT_PLACES below assigns each row number its places, with the evidence for each. A contract naming
#     several places counts once for each; [] means it has no single location and is left off the map.
#   - Coastline and borders: Natural Earth 1:10m land, admin-0 boundary lines and admin-1 boundary lines (public
#     domain, naturalearthdata.com), clipped to the two frames, simplified, cached in tools/data/ne-project-map.json.
#   - Place coordinates: OpenStreetMap Nominatim (© OpenStreetMap contributors, ODbL), cached in
#     tools/data/nominatim-places.json and copied (rounded) into PLACES below so the table stays reviewable.
# Run: python3 tools/make_project_map.py           (place counts, unplaced rows, label check; no network)
#      python3 tools/make_project_map.py --fetch   (re-downloads Natural Earth and Nominatim, rewrites the cache)
#      python3 tools/make_project_map.py --fetch-new-places   (Nominatim only, for PLACES not yet in the cache)
import ast, json, math, os, re, sys, time

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
LIST_ID = "all-projects"               # id of the "View all projects" table (a <details>) the pins link to
ATTRIBUTION = "© OpenStreetMap contributors · Natural Earth"

# Each place: EN name (a proper noun, also used in BM), lat/lon (from Nominatim unless marked manual),
# label offset (dx, dy) from the pin in drawing units (dx < 0: label ends there, dx > 0: starts there, 0: centred),
# q: the Nominatim query used by --fetch, want: the Nominatim address types accepted (default: a settlement;
# Nominatim also returns same-named districts).
PLACES = {
    "sematan":    {"name": "Sematan", "lat": 1.8053, "lon": 109.7783, "label": (-28, -98, "start"), "q": "Sematan, Sarawak"},
    "padawan":    {"name": "Padawan", "lat": 1.4277, "lon": 110.3256, "label": (-79, 32, "start"), "q": "Padawan, Sarawak"},
    "samarahan":  {"name": "Samarahan", "lat": 1.4637, "lon": 110.4891, "label": (12, -30),
                   "q": "Kota Samarahan, Sarawak"},
    "betong":     {"name": "Betong", "lat": 1.4116, "lon": 111.5281, "label": (12, 4), "q": "Betong, Sarawak"},
    "sibu":       {"name": "Sibu", "lat": 2.2906, "lon": 111.8256, "label": (12, 4), "q": "Sibu, Sarawak"},
    "tanjung_manis": {"name": "Tanjung Manis", "lat": 2.1338, "lon": 111.3357, "label": (-62, -38, "start"),
                      "q": "Tanjung Manis, Sarawak", "want": ("suburb",)},
    "bintulu":    {"name": "Bintulu", "lat": 3.1874, "lon": 113.0473, "label": (-40, -24),
                   "q": "Bintulu, Sarawak", "base": True},
    "miri":       {"name": "Miri", "lat": 4.3940, "lon": 113.9880, "label": (-22, 6), "q": "Miri, Sarawak", "base": True},
    "long_lama":  {"name": "Long Lama", "lat": 3.7624, "lon": 114.4052, "label": (-12, 0), "q": "Long Lama, Sarawak"},
    "mulu":       {"name": "Mulu", "lat": 4.0444, "lon": 114.8086, "label": (12, -10), "q": "Mulu, Sarawak"},
    "telang_usan": {"name": "Telang Usan", "lat": 3.3172, "lon": 114.8258, "label": (10, 20),
                    "q": "Telang Usan, Sarawak", "want": ("county",)},   # a district: the pin is its centroid
    "bario":      {"name": "Bario", "lat": 3.7479, "lon": 115.4604, "label": (12, 4), "q": "Bario, Sarawak"},
    "lawas":      {"name": "Lawas", "lat": 4.8597, "lon": 115.4083, "label": (12, 16), "q": "Lawas, Sarawak"},
    "sipitang":   {"name": "Sipitang", "lat": 5.0764, "lon": 115.5494, "label": (12, -4), "q": "Sipitang, Sabah"},
    "labuan":     {"name": "Labuan", "lat": 5.3168, "lon": 115.2199, "label": (12, -16),
                   "q": "Labuan", "want": ("state",)},                 # the federal territory (island)
    "port_dickson": {"name": "Port Dickson", "lat": 2.5262, "lon": 101.8106, "label": (6, -32, "middle"),
                     "q": "Port Dickson, Negeri Sembilan"},
    "melaka":     {"name": "Melaka", "lat": 2.1943, "lon": 102.2487, "label": (0, 28), "q": "Melaka"},
    "pengerang":  {"name": "Pengerang", "lat": 1.3944, "lon": 104.2155, "label": (-12, 0), "q": "Pengerang, Johor"},
}
SETTLEMENT = ("city", "town", "village", "suburb", "hamlet", "municipality")

# Where each ALL_PROJECTS contract was carried out, keyed by its row number (the first field). BWS to confirm.
# Evidence, cited in each comment, is one of:
#   title  - a place named in the row's own text
#   known  - a facility whose location is unambiguous and well known (e.g. MCOT, the PETRONAS LNG Complex), or a
#            client with a single plant (Malaysia LNG: the PETRONAS LNG Complex, Bintulu; Shell MDS: Bintulu)
#   site   - a location this website states for the same project elsewhere (PROJECTS, CASE_STUDIES)
# [] = no single location (e.g. a Sarawak-wide maintenance agreement, or no site given): not on the map. No guesses.
CONTRACT_PLACES = {
    4:  ["bintulu"],        # title: Bintulu Integrated Facilities (BIF); site: PROJECTS says Bintulu
    5:  ["bintulu"],        # title: Bintulu Airport
    6:  ["sibu"],           # title: Sibu Depot
    7:  ["miri"],           # title: Miri Aviation Depot
    8:  [],                 # PETRONAS service stations, Sarawak: many sites
    9:  [],                 # PCSB Sarawak Operations: on-call, many sites
    10: ["miri"],           # known: MCOT = Miri Crude Oil Terminal (Lutong, Miri); site: PROJECTS says Miri
    11: ["miri"],           # known: MCOT, Miri
    12: ["miri"],           # known: MCOT, Miri
    13: ["labuan"],         # title: Labuan Crude Oil Terminal
    14: [],                 # UHP water jetting: no site given
    15: ["bintulu"],        # title: MLNG Tiga plant; known: PETRONAS LNG Complex, Bintulu
    16: ["long_lama"],      # title: Lapok – Long Lama Road; pinned at Long Lama, the camp's point on the road is not given
    17: ["miri"],           # known: MCOT, Miri
    18: ["bintulu"],        # title: Bintulu Compressor Station
    19: ["bintulu"],        # title: MLNG Tiga; known: PETRONAS LNG Complex, Bintulu
    20: ["bintulu"],        # known (client): Malaysia LNG field station extension; MLNG's plant is in Bintulu
    21: ["bintulu"],        # known (client): Malaysia LNG plant change PC12303 (B-Track headers), Bintulu
    22: ["bintulu"],        # known (client): Malaysia LNG Trunkline 1 beach valve, at the Bintulu shore
    23: ["miri"],           # known: MCOT, Miri
    24: ["miri"],           # known: MCOT, Miri
    25: [],                 # classroom cabins, Ministry of Education stimulus package: schools not named
    26: ["bintulu"],        # title: PETRONAS LNG Complex (Bintulu)
    27: ["bintulu"],        # title: MLNG-2 and Bintulu Integrated Facilities
    28: ["bintulu"],        # known (client): Malaysia LNG plant change PC20555 (MCHE), Bintulu
    29: [],                 # C1/U1 area: plant not named
    30: ["bintulu"],        # known (client): Malaysia LNG slugcatcher SC1, Bintulu
    31: ["bintulu"],        # title: MLNG & MLNG Dua Common Reclaimer; known: PETRONAS LNG Complex, Bintulu
    32: ["bintulu"],        # title: Jalan Kidurong, MLNG; site: PROJECTS says Bintulu
    33: ["bintulu"],        # title: New Common Reclaimer Project (MLNG, as no. 31), Bintulu
    34: ["bintulu"],        # title: PETRONAS LNG Complex (Bintulu)
    35: ["bintulu"],        # title: MLNG 2 & 3; known: PETRONAS LNG Complex, Bintulu
    36: ["tanjung_manis"],  # title: Tanjung Manis OGC Jetty, Mukah (Division)
    37: ["bintulu"],        # title: MLNG Turnaround 2014; known: PETRONAS LNG Complex, Bintulu
    38: ["bintulu"],        # title: PETRONAS LNG Train 9; site: PROJECTS says Train 9 is in Bintulu
    39: ["bintulu"],        # title: SMDS = Shell MDS, Bintulu; site: PROJECTS says Bintulu
    40: ["bintulu"],        # known (client): Shell MDS, PTA village for the SMDS Rejuvenation Project, Bintulu
    41: [],                 # Substation 7: Sarawak Shell has several sites
    42: ["miri"],           # title: PDB Miri Fuel Terminal
    43: ["bintulu"],        # title: SMDS Rejuvenation Project; site: PROJECTS says Bintulu
    44: ["bintulu"],        # title: MLNG Dua; known: PETRONAS LNG Complex, Bintulu
    45: ["bintulu"],        # title: PETRONAS LNG Complex (Bintulu); site: PROJECTS says Bintulu
    46: ["bintulu"],        # title: MLNG reclaimer unit; known: PETRONAS LNG Complex, Bintulu
    47: ["miri"],           # title: Miri
    48: ["pengerang"],      # title: RAPID = PETRONAS RAPID / PRPC, Pengerang, Johor
    49: ["betong"],         # title: Betong
    50: ["bintulu"],        # known (client): Shell MDS café and lab pantry, at its Bintulu plant
    51: ["pengerang"],      # title: RAPID, Pengerang; site: PROJECTS says Pengerang
    52: ["bintulu"],        # title: Bintulu Onshore Receiving Facility
    53: ["port_dickson"],   # known: Hengyuan refinery, Port Dickson; site: PROJECTS says Port Dickson
    54: ["bintulu"],        # title: ABF = ASEAN Bintulu Fertilizer; site: PROJECTS says Bintulu
    55: [],                 # minor works for PETRONAS onshore facilities: many sites
    56: ["miri"],           # title: Miri Water Supply; site: PROJECTS and case study say Miri
    57: ["samarahan"],      # title: Kampung Sadong Jaya, Samarahan (Division)
    58: ["pengerang"],      # title: PRPC UF = PRPC Utilities & Facilities, RAPID, Pengerang; site: PROJECTS
    59: ["bintulu"],        # title: MLNG Dua; site: PROJECTS says Bintulu
    60: ["miri", "bintulu"],  # site: PROJECTS says Miri – Bintulu (pipeline KP-210 to KP-503)
    61: ["melaka"],         # title: Melaka Refinery (PETRONAS, Sungai Udang, Melaka)
    62: ["bintulu"],        # title: PETRONAS LNG Complex (Bintulu); site: PROJECTS says Bintulu
    63: ["sematan"],        # title: Sematan Industrial Area
    64: ["port_dickson"],   # known: Hengyuan refinery, Port Dickson
    65: ["padawan"],        # title: Padawan
    66: ["bintulu"],        # title: Bintulu Onshore Receiving Facility
    67: ["bintulu"],        # title: PETRONAS LNG Complex (Bintulu)
    68: ["bintulu"],        # site: the PROJECTS entry and the Power Import case study say Bintulu
    70: ["bintulu"],        # site: Shell OGP (Rosmari-Marjoram Onshore Gas Plant), PROJECTS says Bintulu
    71: [],                 # piping system PC40008 for PETRONAS Carigali: no site given
    72: ["bintulu"],        # site: Shell OGP, PROJECTS says Bintulu
    73: ["samarahan"],      # title: Gedong Baru, Samarahan
    74: ["miri"],           # title: PM5 metering station, Miri
    75: ["bintulu"],        # title: Train 9 LNG (MLNG); site: PROJECTS says Bintulu
    76: ["sipitang"],       # title: Sipitang scraper station
    77: ["bintulu"],        # title: Bintulu Integrated Facilities (Shell OGP)
    78: ["bario", "mulu", "telang_usan"],  # title: Bario / Mulu / Telang Usan
    79: ["lawas"],          # title: Lawas
    80: ["bintulu"],        # site: Project Rejuv MECH03 for Shell MDS, PROJECTS says Bintulu
    81: ["lawas"],          # title: Lawas
}

# Geographic frames (degrees). The main frame is northern Borneo; the inset is Peninsular Malaysia.
FRAMES = {
    "borneo":    {"lat0": 0.75, "lat1": 7.55, "lon0": 109.4, "lon1": 119.6},
    "peninsula": {"lat0": 0.95, "lat1": 4.35, "lon0": 100.0, "lon1": 104.75},  # southern part: all its places are there
}
PENINSULA = {"port_dickson", "melaka", "pengerang"}

W = 960
TB_H = 64                             # title block strip below the map


# ------------------------------------------------------------------ contracts → places

def load_contracts(path=GENERATOR, name="ALL_PROJECTS"):
    """ALL_PROJECTS from generate_site.py, parsed with ast (never imported: importing it rebuilds the site)."""
    with open(path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise RuntimeError(f"{name} not found in {path}")


def places_of(row):
    """Place keys of one ALL_PROJECTS row, from CONTRACT_PLACES. Raises if the row has no entry."""
    no = row[0]
    if no not in CONTRACT_PLACES:
        raise ValueError(f"ALL_PROJECTS no. {no} ({row[2]!r}) has no CONTRACT_PLACES entry in "
                         f"tools/make_project_map.py: add its places with the evidence, or [] if it has no single location")
    return CONTRACT_PLACES[no]


def check(contracts):
    """Problems with CONTRACT_PLACES against the contract list: missing or stale rows, unknown place keys."""
    nos = [c[0] for c in contracts]
    out = [f"ALL_PROJECTS no. {c[0]} ({c[2]!r}) has no CONTRACT_PLACES entry" for c in contracts if c[0] not in CONTRACT_PLACES]
    out += [f"CONTRACT_PLACES no. {n} is not in ALL_PROJECTS" for n in CONTRACT_PLACES if n not in nos]
    out += [f"CONTRACT_PLACES no. {n}: unknown place {k!r}" for n, ks in CONTRACT_PLACES.items() for k in ks if k not in PLACES]
    out += [f"CONTRACT_PLACES no. {n}: {k!r} listed twice" for n, ks in CONTRACT_PLACES.items() for k in set(ks) if ks.count(k) > 1]
    return out


def counts(contracts):
    c = {k: 0 for k in PLACES}
    for row in contracts:
        for k in places_of(row):
            c[k] += 1
    return {k: n for k, n in c.items() if n}


def unplaced(contracts):
    return [row for row in contracts if not places_of(row)]


def first_year(contracts):
    return min(int(re.match(r"\d{4}", c[1]).group(0)) for c in contracts)


def caption(contracts):
    n, m = len(contracts), len(unplaced(contracts))
    return (f"Circle area shows the number of contracts at each place, from all {n} contracts since "
            f"{first_year(contracts)}. {m} contract{' with no single location (for example Sarawak-wide maintenance agreements) is' if m == 1 else 's with no single location (for example Sarawak-wide maintenance agreements) are'} not shown.")


def place_names(row):
    """data-places value for a table row: the names of its places, | separated ("" if none)."""
    return "|".join(PLACES[k]["name"] for k in places_of(row))


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
INSET_SCALE = SCALE * 0.75
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


def fetch_places(only_new=False):
    """Nominatim lookups for PLACES (1 request per second). only_new: just the places not yet cached, merged in."""
    with open(PLACES_FILE, encoding="utf-8") as fh:
        cached = json.load(fh)["places"]
    out = {k: v for k, v in cached.items() if k in PLACES} if only_new else {}
    for key, p in PLACES.items():
        if only_new and key in out:
            continue
        res = json.loads(http_get(NOMINATIM, {"format": "json", "q": p["q"], "countrycodes": "my", "limit": 5}))
        time.sleep(1.1)                                   # Nominatim usage policy: at most 1 request per second
        res = [r for r in res if (r.get("addresstype") or r.get("type")) in p.get("want", SETTLEMENT)]
        if not res:
            print(f"  {key}: Nominatim found no {'/'.join(p.get('want', SETTLEMENT))} for {p['q']!r}; set lat/lon manually")
            continue
        r = res[0]
        out[key] = {"q": p["q"], "lat": round(float(r["lat"]), 4), "lon": round(float(r["lon"]), 4),
                    "type": r.get("addresstype") or r.get("type"), "display_name": r["display_name"]}
    out = {k: out[k] for k in PLACES if k in out}                 # same order as PLACES
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


R_PER = 4.4          # circle radius per sqrt(contract): area is proportional to the count ...
R_MIN = 5.0          # ... except a single contract, drawn a little larger so it stays visible
R_MAX = 30.0         # cap, so a dominant place (Bintulu) cannot swamp its neighbours
HIT_MIN = 20.0       # invisible tap target radius (the label is part of the link too)


def radius(n):
    return min(R_MAX, max(R_MIN, R_PER * math.sqrt(n)))


# Region names drawn faintly on the map: (text, lat, lon, size, letter spacing, opacity, frame).
# Also obstacles for the label check, at the width of the longer of the EN and BM texts.
REGION_NAMES = [
    ("SARAWAK", 2.0, 113.4, 13, 8, .55, "borneo"),
    ("SABAH", 4.75, 117.75, 13, 8, .55, "borneo"),      # south-east of the Sipitang / Lawas labels
    ("BRUNEI", 4.5, 114.7, 9, 2.5, .55, "borneo"),
    ("INDONESIA", 1.35, 115.6, 12, 8, .4, "borneo"),
    ("SOUTH CHINA SEA", 6.9, 114.9, 12, 7, .5, "borneo"),
    ("SUMATRA", 1.1, 100.75, 9, 3, .4, "peninsula"),
]

# Label sizes in drawing units: (name size, letter spacing, tag size, tag spacing) on desktop and on phones
# (see .pm-l / .pm-b in src/css/07-page-additions.css: phones draw the labels twice as large).
LABEL_SIZES = {"desktop": (13, 1.5, 9.5, 2), "phone": (26, .5, 17, 1)}
BASE_TAG = "PANGKALAN BWS"            # the longer (BM) base tag, for the check


def label_box(text, x, y, anchor, size, spacing):
    w = ml.text_width(text, size, spacing)
    x0 = x - w if anchor == "end" else x if anchor == "start" else x - w / 2
    return (x0, y - .42 * size, x0 + w, y + .42 * size)


def layout(key, n):
    """Geometry of one pin: centre, circle radius, label point and anchor, the label boxes per size, and the
    leader (or None). PLACES label = (dx, dy) or (dx, dy, anchor); default anchor from the sign of dx."""
    p = PLACES[key]
    proj = INSET if key in PENINSULA else MAIN
    x, y = proj(p["lat"], p["lon"])
    r = radius(n)
    dx, dy = p["label"][:2]
    anchor = p["label"][2] if len(p["label"]) > 2 else "end" if dx < 0 else "start" if dx > 0 else "middle"
    lx, ly = x + dx, y + dy
    boxes = {}
    for mode, (sz, sp, tsz, tsp) in LABEL_SIZES.items():
        bs = [label_box(f"{p['name'].upper()} · {n}", lx, ly, anchor, sz, sp)]
        if p.get("base"):
            bs.append(label_box(BASE_TAG, lx, ly + 1.35 * tsz, anchor, tsz, tsp))
        boxes[mode] = bs
    # leader: from the circle edge to 3 units short of the nearest point of the (larger) phone label box
    b = boxes["phone"][0]
    tx, ty = min(max(x, b[0]), b[2]), min(max(y, b[1]), b[3])
    d = math.hypot(tx - x, ty - y)
    leader = None
    if d - r > 12:
        ux, uy = (tx - x) / d, (ty - y) / d
        leader = (x + ux * (r + 2), y + uy * (r + 2), tx - ux * 3, ty - uy * 3)
    return {"x": x, "y": y, "r": r, "lx": lx, "ly": ly, "anchor": anchor, "boxes": boxes, "leader": leader}


def pin(key, n, label_word):
    p = PLACES[key]
    g = layout(key, n)
    x, y, r, lx, ly = g["x"], g["y"], g["r"], g["lx"], g["ly"]
    name = p["name"]
    unit = "contract" if n == 1 else "contracts"
    body = ""
    if g["leader"]:
        x0, y0, x1, y1 = g["leader"]
        body += (f'<path d="M{rnd(x0)} {rnd(y0)}L{rnd(x1)} {rnd(y1)}" stroke="{SKY}" '
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
    hit = max(r + 6, HIT_MIN)                          # invisible, larger tap target (the label is tappable too)
    body += f'<circle cx="{rnd(x)}" cy="{rnd(y)}" r="{rnd(hit)}" fill="#000" fill-opacity="0"/>'
    tag = (f'<tspan class="pm-b" x="{rnd(lx)}" dy="1.35em">{label_word}</tspan>') if p.get("base") else ""
    body += (f'<text class="pm-l" x="{rnd(lx)}" y="{rnd(ly)}" text-anchor="{g["anchor"]}" dominant-baseline="central">'
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


def svg(contracts=None):
    """The inline SVG for projects.html. contracts: the ALL_PROJECTS list (read from generate_site.py if None)."""
    contracts = load_contracts() if contracts is None else contracts
    c = counts(contracts)
    borneo = [k for k in c if k not in PENINSULA]
    peninsula = [k for k in c if k in PENINSULA]
    total = sum(c.values())

    m = sea(0, 0, W, MAP_H) + land_paths("borneo", MAIN)
    m += "".join(faint(*MAIN(la, lo), t, sz, sp, op=op) for t, la, lo, sz, sp, op, fr in REGION_NAMES if fr == "borneo")
    m += f'<rect width="{W}" height="{MAP_H}" fill="url(#pm-grid)"/>'
    m += graticule(MAIN, "borneo")
    # inset: Peninsular Malaysia, only if a project is there
    inset = ""
    if peninsula:
        x0, y0, x1, y1 = INSET.box
        inset += f'<rect x="{rnd(x0 - 6)}" y="{rnd(y0 - 6)}" width="{rnd(INSET.w + 12)}" height="{rnd(INSET.h + 12)}" fill="{INK}"/>'
        inset += f'<g clip-path="url(#pm-clip-inset)">{sea(x0, y0, INSET.w, INSET.h)}{land_paths("peninsula", INSET, .35)}'
        inset += "".join(faint(*INSET(la, lo), t, sz, sp, op=op) for t, la, lo, sz, sp, op, fr in REGION_NAMES
                         if fr == "peninsula")
        inset += '</g>' + graticule(INSET, "peninsula", inset=True)
        inset += ml.rect(rnd(x0), rnd(y0), rnd(INSET.w), rnd(INSET.h), CYAN, 1.5)
        inset += ml.halo_text(x1 - 10, y0 + 22, "PENINSULAR MALAYSIA", 11, CYAN, "end", 700, 2)
    pins = "".join(pin(k, c[k], "BWS BASE") for k in sorted(borneo, key=lambda k: -c[k]))
    pins += "".join(pin(k, c[k], "BWS BASE") for k in sorted(peninsula, key=lambda k: -c[k]))
    deco = (m + ml.north_arrow(W - 44, 50)
            + scale_bar(W - 290, MAP_H - 46) + ml.halo_text(W - 14, MAP_H - 12, ATTRIBUTION, 10.5, SKY, "end", 600, .5)
            + inset)
    title = "Map of BWS project locations"
    places_txt = ", ".join(f"{PLACES[k]['name']} {c[k]}" for k in sorted(c, key=lambda k: -c[k]))
    desc = ("Blueprint map of northern Borneo with an inset of Peninsular Malaysia, marking the places of BWS "
            "contracts. Each marker is a link that shows that place's contracts in the full project list below.")
    body = (f'<g aria-hidden="true"><g clip-path="url(#pm-clip)">{deco}</g>'
            + ml.line([(0, MAP_H), (W, MAP_H)], SKY, 1, .35) + title_block(len(contracts), len(c)) + '</g>'
            + f'<g class="pm-pins" {FONT} font-weight="700">{pins}</g>')
    return (f'<svg class="pm-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="group" '
            f'aria-labelledby="pm-title" aria-describedby="pm-desc">'
            f'<title id="pm-title">{title}</title><desc id="pm-desc">{desc}</desc>'
            f'{defs()}<rect width="{W}" height="{H}" fill="{INK}"/>{body}</svg>')


def _seg_hits_box(x0, y0, x1, y1, b, steps=40):
    return any(b[0] < x0 + (x1 - x0) * i / steps < b[2] and b[1] < y0 + (y1 - y0) * i / steps < b[3]
               for i in range(steps + 1))


def label_problems(c):
    """Labels that overlap another label, a pin, a region name or the scale bar, leave the map, cross the inset
    frame (main-map labels must stay outside it, inset labels inside), and leaders that cross a label or a pin."""
    try:
        from ms_strings import MS
    except ImportError:
        MS = {}
    out = []
    ib = (INSET.ox - 6, INSET.oy - 6, INSET.ox + INSET.w + 6, INSET.oy + INSET.h + 6)
    inner = (INSET.ox + 6, INSET.oy + 6, INSET.ox + INSET.w - 8, INSET.oy + INSET.h - 6)   # clear of the frame line
    hit = lambda a, b: a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]
    inside = lambda a, b: b[0] <= a[0] and b[1] <= a[1] and a[2] <= b[2] and a[3] <= b[3]
    geo_ = {k: layout(k, n) for k, n in c.items()}
    fixed = []                                           # (name, frame, box)
    for t, la, lo, sz, sp, _op, fr in REGION_NAMES:
        px, py = (MAIN if fr == "borneo" else INSET)(la, lo)
        w = max(ml.text_width(t, sz, sp), ml.text_width(MS.get(t, t), sz, sp))
        fixed.append((t, fr, (px - w / 2, py - .75 * sz, px + w / 2, py + .1 * sz)))   # baseline text
        fb = (0, 0, W, MAP_H) if fr == "borneo" else inner
        if not inside(fixed[-1][2], fb):
            out.append(f"region name {t} is cut off by its frame")
    f = FRAMES["borneo"]                                 # graticule labels along the bottom and right edges
    for lon in range(math.ceil(f["lon0"] / 2) * 2, math.ceil(f["lon1"]), 2):
        x = MAIN(f["lat0"], lon)[0] + 3
        fixed.append((f"{lon}°E", "borneo", (x, MAP_H - 16, x + ml.text_width(f"{lon}°E", 9.5, .5), MAP_H - 6)))
    for lat in range(math.ceil(f["lat0"] / 2) * 2, math.ceil(f["lat1"]), 2):
        y = MAIN(lat, f["lon0"])[1] - 4
        fixed.append((f"{lat}°N", "borneo", (W - 9 - ml.text_width(f"{lat}°N", 9.5, .5), y - 8, W - 9, y + 1)))
    sx, sy = W - 290, MAP_H - 46
    fixed.append(("scale bar", "borneo", (sx - 14, sy - 22, sx + 200_000 * SCALE + 40, sy + 12)))
    for mode in LABEL_SIZES:
        items = []                                       # (key, kind, box)
        for k, g in geo_.items():
            rr = g["r"] + (9 if PLACES[k].get("base") else 0)
            items.append((k, "pin", (g["x"] - rr, g["y"] - rr, g["x"] + rr, g["y"] + rr)))
            items += [(k, "label", b) for b in g["boxes"][mode]]
        for i, (k, kind, b) in enumerate(items):
            if kind != "label":
                continue
            fr = "peninsula" if k in PENINSULA else "borneo"
            if b[0] < 2 or b[1] < 2 or b[2] > W - 2 or b[3] > MAP_H - 2:
                out.append(f"{mode}: {k} label leaves the map")
            if fr == "borneo" and hit(b, ib):
                out.append(f"{mode}: {k} label runs under the inset")
            if fr == "peninsula" and not inside(b, inner):
                out.append(f"{mode}: {k} label crosses the inset frame")
            for k2, kind2, b2 in items:
                if k2 != k and hit(b, b2):
                    out.append(f"{mode}: {k} label overlaps {k2} {kind2}")
            for name, fr2, b2 in fixed:
                if fr2 == fr and hit(b, b2):
                    out.append(f"{mode}: {k} label overlaps {name}")
        for k, g in geo_.items():
            if g["leader"]:
                for k2, kind2, b2 in items:
                    if k2 != k and _seg_hits_box(*g["leader"], b2):
                        out.append(f"{mode}: {k} leader crosses {k2} {kind2}")
    return sorted(set(out))


def summary(contracts):
    c = counts(contracts)
    un = unplaced(contracts)
    print(f"{len(contracts)} contracts since {first_year(contracts)}: {len(contracts) - len(un)} placed, {len(un)} unplaced; "
          f"{sum(c.values())} pin counts over {len(c)} places:")
    for k in sorted(c, key=lambda k: (-c[k], k)):
        p = PLACES[k]
        print(f"  {p['name']:<18}{c[k]:>3}   {p['lat']:.4f} N {p['lon']:.4f} E{'   (manual)' if p.get('manual') else ''}"
              f"{'   inset' if k in PENINSULA else ''}")
    unused = [k for k in PLACES if k not in c]
    if unused:
        print("  unused PLACES:", ", ".join(unused))
    print("unplaced (no single location):")
    for row in un:
        print(f"  no. {row[0]:>2}  {row[2]}")


if __name__ == "__main__":
    if "--fetch" in sys.argv[1:]:
        print("fetching Natural Earth (large download) ...")
        fetch_geo()
    if "--fetch" in sys.argv[1:] or "--fetch-new-places" in sys.argv[1:]:
        print("fetching Nominatim places (1 request per second) ...")
        fetch_places(only_new="--fetch" not in sys.argv[1:])
        for line in check_places_against_cache():
            print("  check:", line)
    contracts = load_contracts()
    problems = check(contracts)
    if problems:
        raise SystemExit("\n".join(problems))
    summary(contracts)
    s = svg(contracts)
    print(f"SVG {len(s.encode())} bytes")
    for line in label_problems(counts(contracts)):
        print("  label:", line)
