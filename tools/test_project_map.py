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
        self.projects = pm.load_projects()          # parsed with ast, the generator is not imported

    def test_every_location_maps_to_a_place(self):
        for p in self.projects:
            keys = pm.places_for(p[3])
            self.assertTrue(keys, p[3])
            self.assertTrue(all(k in pm.PLACES for k in keys))

    def test_several_places_count_once_each(self):
        self.assertEqual(pm.places_for("Bario, Mulu &amp; Telang Usan, Sarawak"), ["bario", "mulu", "telang_usan"])
        self.assertEqual(pm.places_for("Miri – Bintulu, Sarawak"), ["miri", "bintulu"])
        self.assertEqual(pm.places_for("Labuan"), ["labuan"])

    def test_unmapped_location_raises(self):
        with self.assertRaisesRegex(ValueError, "Unmapped project location 'Sibu, Sarawak'"):
            pm.places_for("Sibu, Sarawak")
        with self.assertRaises(ValueError):
            pm.places_for("Sarawak")

    def test_total_pin_count(self):
        expected = sum(len(pm.places_for(p[3])) for p in self.projects)
        self.assertEqual(sum(pm.counts(self.projects).values()), expected)
        labels = re.findall(r'aria-label="[^"]+: (\d+) projects?, show', map_svg(page("projects.html")))
        self.assertEqual(sum(map(int, labels)), expected)

    def test_places_agree_with_nominatim_cache_and_known_geography(self):
        self.assertEqual(pm.check_places_against_cache(), [])
        known = {"bintulu": (3.17, 113.04), "miri": (4.40, 113.99), "lawas": (4.86, 115.41), "sipitang": (5.08, 115.55),
                 "labuan": (5.30, 115.23), "port_dickson": (2.52, 101.80)}
        for k, (lat, lon) in known.items():
            p = pm.PLACES[k]
            d = math.hypot((p["lat"] - lat) * 110.54, (p["lon"] - lon) * 111.32 * math.cos(math.radians(lat)))
            self.assertLess(d, 15, k)

    def test_labels_do_not_overlap(self):
        self.assertEqual(pm.label_problems(pm.counts(self.projects)), [])


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

    def test_pins_link_to_the_list(self):
        ids = set(re.findall(r'\bid="([^"]+)"', self.doc))
        pins = re.findall(r"<a ([^>]*data-place[^>]*)>", self.svg)
        self.assertEqual(len(pins), len(pm.counts(pm.load_projects())))
        for attrs in pins:
            href = re.search(r'href="#([^"]+)"', attrs)
            self.assertTrue(href and href.group(1) in ids, attrs)
            self.assertRegex(attrs, r'aria-label="[^"]+: \d+ projects?, show (it|them) in the list"')

    def test_list_rows_carry_their_places(self):
        rows = re.findall(r'<li class="proj" data-places="([^"]*)"', self.doc)
        c = pm.counts(pm.load_projects())
        for k, n in c.items():
            name = pm.PLACES[k]["name"]
            self.assertEqual(sum(1 for r in rows if name in html.unescape(r).split("|")), n, name)
            self.assertIn(f'data-place="{name}"', self.svg)

    def test_no_amber(self):
        self.assertNotIn("#F2A900", self.svg.upper())

    def test_bm_page_is_translated(self):
        ms = map_svg(page("ms/projects.html"))
        for s in ("LOKASI PROJEK", "PANGKALAN BWS", "SEMENANJUNG MALAYSIA", "Peta lokasi projek BWS",
                  "projek, tunjukkan dalam senarai"):
            self.assertIn(s, ms)
        self.assertNotIn("show them in the list", ms)
        self.assertIn('data-place="Bintulu"', ms)           # place names stay as proper nouns

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
