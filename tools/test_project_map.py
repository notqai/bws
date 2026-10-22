import html
import math
import os
import re
import unittest
from unittest import mock
import xml.etree.ElementTree as ET

import make_project_map as pm

SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site")
NS = "{http://www.w3.org/2000/svg}"


def page(rel):
    with open(os.path.join(SITE, rel), encoding="utf-8") as f:
        return f.read()


def map_svg(doc):
    m = re.search(r'<svg class="pm-svg".*?</svg>', doc, re.S)
    assert m, "project map SVG not found"
    return m.group(0)


class ProjectMapDataTests(unittest.TestCase):
    def setUp(self):
        self.contracts = pm.load_contracts()        # ALL_PROJECTS, parsed with ast (the generator is not imported)

    def test_every_contract_has_a_place_entry(self):
        self.assertEqual(len(self.contracts), 77)
        self.assertEqual(pm.check(self.contracts), [])
        for row in self.contracts:
            self.assertIn(row[0], pm.CONTRACT_PLACES, row)
        self.assertEqual(sorted(pm.CONTRACT_PLACES), sorted(r[0] for r in self.contracts))

    def test_place_keys_exist(self):
        for no, keys in pm.CONTRACT_PLACES.items():
            for k in keys:
                self.assertIn(k, pm.PLACES, no)

    def test_missing_entry_fails_loudly(self):
        extra = self.contracts + [(99, "2027", "New contract", "Client", "og")]
        self.assertIn("ALL_PROJECTS no. 99 ('New contract') has no CONTRACT_PLACES entry", pm.check(extra))
        with self.assertRaisesRegex(ValueError, "no. 99"):
            pm.counts(extra)
        with mock.patch.dict(pm.CONTRACT_PLACES, {4: ["sibu_town"]}):
            self.assertTrue(any("unknown place 'sibu_town'" in x for x in pm.check(self.contracts)))

    def test_pin_counts_match_the_assignments(self):
        c = pm.counts(self.contracts)
        for k in pm.PLACES:
            n = sum(1 for keys in pm.CONTRACT_PLACES.values() if k in keys)
            self.assertEqual(c.get(k, 0), n, k)
        labels = dict(re.findall(r'aria-label="([^":]+): (\d+) contracts?, show', map_svg(page("projects.html"))))
        self.assertEqual({k: int(v) for k, v in labels.items()}, {pm.PLACES[k]["name"]: n for k, n in c.items()})
        self.assertEqual(c["bintulu"], 39)
        self.assertEqual(c["miri"], 12)
        self.assertEqual(c["telang_usan"], 1)                 # no. 78 counts once for each named place

    def test_placed_plus_unplaced_is_all(self):
        un = pm.unplaced(self.contracts)
        placed = [r for r in self.contracts if pm.places_of(r)]
        self.assertEqual(len(placed) + len(un), len(self.contracts))
        self.assertEqual([r[0] for r in un], [8, 9, 14, 25, 29, 41, 55, 71])

    def test_caption_numbers(self):
        cap = pm.caption(self.contracts)
        self.assertEqual(pm.first_year(self.contracts), 2003)
        self.assertIn(f"from all {len(self.contracts)} contracts since 2003.", cap)
        self.assertIn(f"{len(pm.unplaced(self.contracts))} contracts with no single location", cap)
        self.assertIn(f'<figcaption class="small">{cap}</figcaption>', page("projects.html"))

    def test_places_agree_with_nominatim_cache_and_known_geography(self):
        self.assertEqual(pm.check_places_against_cache(), [])
        known = {"bintulu": (3.17, 113.04), "miri": (4.40, 113.99), "lawas": (4.86, 115.41), "sipitang": (5.08, 115.55),
                 "labuan": (5.30, 115.23), "port_dickson": (2.52, 101.80), "sibu": (2.30, 111.83),
                 "betong": (1.41, 111.53), "melaka": (2.19, 102.25), "tanjung_manis": (2.13, 111.34),
                 "long_lama": (3.77, 114.40), "sematan": (1.80, 109.78)}
        for k, (lat, lon) in known.items():
            p = pm.PLACES[k]
            d = math.hypot((p["lat"] - lat) * 110.54, (p["lon"] - lon) * 111.32 * math.cos(math.radians(lat)))
            self.assertLess(d, 15, k)

    def test_labels_do_not_overlap(self):
        self.assertEqual(pm.label_problems(pm.counts(self.contracts)), [])

    def test_circle_area_is_proportional_with_a_cap_and_a_minimum(self):
        self.assertAlmostEqual(pm.radius(16) ** 2 / pm.radius(4) ** 2, 4)
        self.assertLessEqual(pm.radius(1000), pm.R_MAX)
        self.assertGreaterEqual(pm.radius(1), pm.R_MIN)
        self.assertGreaterEqual(pm.HIT_MIN, 20)


class ProjectMapPageTests(unittest.TestCase):
    def setUp(self):
        self.doc = page("projects.html")
        self.svg = map_svg(self.doc)

    def test_svg_is_well_formed_and_labelled(self):
        root = ET.fromstring(self.svg)
        self.assertEqual(root.get("role"), "group")      # not "img": that would hide the pin links
        self.assertIsNotNone(root.find(NS + "title"))
        self.assertIsNotNone(root.find(NS + "desc"))
        for s in ("DWG BWS-PRJ-01", "PROJECT LOCATIONS", "REV A", "BWS BASE", "PENINSULAR MALAYSIA",
                  "© OpenStreetMap contributors · Natural Earth"):
            self.assertIn(s, self.svg)

    def test_pins_link_to_the_full_table(self):
        ids = set(re.findall(r'\bid="([^"]+)"', self.doc))
        pins = re.findall(r"<a ([^>]*data-place[^>]*)>", self.svg)
        self.assertEqual(len(pins), len(pm.counts(pm.load_contracts())))
        for attrs in pins:
            href = re.search(r'href="#([^"]+)"', attrs)
            self.assertTrue(href and href.group(1) in ids, attrs)
            self.assertEqual(href.group(1), "all-projects")
            self.assertRegex(attrs, r'aria-label="[^"]+: \d+ contracts?, show (it|them) in the list"')
        self.assertIn('<details class="full-list" id="all-projects">', self.doc)

    def test_table_rows_carry_their_places(self):
        rows = re.findall(r'<tr data-sector="\w+" data-places="([^"]*)">', self.doc)
        contracts = pm.load_contracts()
        self.assertEqual(len(rows), len(contracts))
        self.assertEqual(sum(1 for r in rows if not r), len(pm.unplaced(contracts)))
        for k, n in pm.counts(contracts).items():
            name = pm.PLACES[k]["name"]
            self.assertEqual(sum(1 for r in rows if name in html.unescape(r).split("|")), n, name)
            self.assertIn(f'data-place="{name}"', self.svg)
        self.assertIn("data-pm-bar", self.doc)
        self.assertNotIn('<li class="proj" data-places', self.doc)      # the old Key-projects filter is gone

    def test_no_amber(self):
        self.assertNotIn("#F2A900", self.svg.upper())

    def test_bm_page_is_translated(self):
        doc = page("ms/projects.html")
        ms = map_svg(doc)
        for s in ("LOKASI PROJEK", "PANGKALAN BWS", "SEMENANJUNG MALAYSIA", "Peta lokasi projek BWS",
                  "Bintulu: 39 kontrak, tunjukkan dalam senarai", "Sibu: 1 kontrak, tunjukkan dalam senarai"):
            self.assertIn(s, ms)
        self.assertNotIn("show them in the list", ms)
        self.assertNotIn("contract", ms)
        self.assertIn('data-place="Bintulu"', ms)           # place names stay as proper nouns
        self.assertIn("daripada kesemua 77 kontrak sejak 2003. 8 kontrak tanpa satu lokasi tertentu", doc)
        self.assertIn("Tunjukkan semua kontrak", doc)
        self.assertNotIn("Circle area", doc)

    def test_page_svg_matches_the_tool(self):
        self.assertEqual(self.svg, pm.svg())


class ProjectMapOfflineTests(unittest.TestCase):
    def test_cached_data_exists_and_drawing_needs_no_network(self):
        for f in (pm.GEO_FILE, pm.PLACES_FILE):
            self.assertTrue(os.path.getsize(f) > 0, f)
        pm._geo = None
        boom = mock.Mock(side_effect=AssertionError("network used"))
        with mock.patch("urllib.request.urlopen", boom), mock.patch("socket.create_connection", boom):
            s = pm.svg()
        self.assertFalse(boom.called)
        size = len(s.encode())
        self.assertTrue(30_000 <= size <= 60_000, size)


if __name__ == "__main__":
    unittest.main()
