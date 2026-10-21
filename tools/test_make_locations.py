import math
import os
import tempfile
import unittest
from unittest import mock
import xml.etree.ElementTree as ET

import make_locations

NS = "{http://www.w3.org/2000/svg}"


def haversine(lat1, lon1, lat2, lon2, r=6371008.8):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


class LocationDrawingTests(unittest.TestCase):
    def check(self, svg, must_contain):
        root = ET.fromstring(svg)  # well-formed XML
        self.assertEqual(root.get("viewBox"), "0 0 800 500")
        self.assertIsNotNone(root.find(NS + "title"))
        for s in must_contain:
            self.assertIn(s, svg)
        self.assertNotIn("NOT TO SCALE", svg)

    def test_miri(self):
        self.check(make_locations.miri(), ["DWG BWS-LOC-01", "MIRI HQ", "JLN PRUNUS 1", "LOT 1743",
                                           "© OpenStreetMap contributors", "4.4469° N  114.0116° E"])

    def test_bintulu(self):
        self.check(make_locations.bintulu(), ["DWG BWS-LOC-02", "BINTULU", "LOT 782",
                                              "© OpenStreetMap contributors", "3.2725° N  113.0802° E"])

    def test_pins_are_inside_the_drawing_area(self):
        for name, (x, y) in make_locations.PINS.items():
            self.assertTrue(0 < x < 800 and 60 < y < 430, name)  # whole pin above the title block

    def test_office_projects_to_the_pin(self):
        for name, site in make_locations.SITES.items():
            x, y = make_locations.project(name, site["lat"], site["lon"])
            self.assertAlmostEqual(x, make_locations.PINS[name][0], places=6)
            self.assertAlmostEqual(y, make_locations.PINS[name][1], places=6)

    def test_projection_is_to_scale(self):
        import math
        for name, site in make_locations.SITES.items():
            lat, lon = site["lat"], site["lon"]
            # WGS84 local radii of curvature: N (east-west, prime vertical) and M (north-south, meridian)
            e2 = 0.00669437999014
            sin2 = math.sin(math.radians(lat)) ** 2
            n_rad = 6378137 / math.sqrt(1 - e2 * sin2)
            m_rad = 6378137 * (1 - e2) / (1 - e2 * sin2) ** 1.5
            east = lon + math.degrees(100 / (n_rad * math.cos(math.radians(lat))))   # ~100 m east
            north = lat + math.degrees(100 / m_rad)                                   # ~100 m north
            x0, y0 = make_locations.project(name, lat, lon)
            x1, y1 = make_locations.project(name, lat, east)
            x2, y2 = make_locations.project(name, north, lon)
            self.assertAlmostEqual(y1, y0, places=6)
            self.assertLess(y2, y0)   # north is up
            for drawn, (la, lo), r in ((x1 - x0, (lat, east), n_rad), (y0 - y2, (north, lon), m_rad)):
                true_m = haversine(lat, lon, la, lo, r)
                self.assertAlmostEqual(drawn / site["scale"] / true_m, 1, delta=0.005)

    def test_pin_style_literals(self):
        self.assertEqual(make_locations.pin_style("miri"), "--pin-x:45.0%;--pin-y:48.0%")
        self.assertEqual(make_locations.pin_style("bintulu"), "--pin-x:62.5%;--pin-y:22.0%")

    def test_html_pins_match_pin_style(self):
        root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site")
        for page in ("contact.html", os.path.join("ms", "contact.html")):
            with open(os.path.join(root, page), encoding="utf-8") as f:
                html = f.read()
            for key in make_locations.SITES:
                self.assertIn('style="' + make_locations.pin_style(key) + '"', html, f"{page} {key}")

    def test_trim_save_load_round_trip(self):
        s = make_locations.SITES["miri"]
        la, lo = s["lat"], s["lon"]
        d = 0.0003
        raw = {"elements": [
            {"type": "way", "tags": {"highway": "residential", "name": "Test Road"},
             "geometry": [{"lat": la - d, "lon": lo - d}, {"lat": la + d, "lon": lo + d}]},
            {"type": "way", "tags": {"building": "yes"},
             "geometry": [{"lat": la + d, "lon": lo + d}, {"lat": la + d, "lon": lo + 2 * d},
                          {"lat": la + 2 * d, "lon": lo + 2 * d}, {"lat": la + d, "lon": lo + d}]},
        ]}
        trimmed = make_locations.trim(raw, "miri")
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(make_locations, "DATA", tmp), \
                mock.patch.dict(make_locations._cache, clear=True):
            make_locations.save(trimmed, "miri")
            loaded = make_locations.load("miri")
        roads = [f for f in loaded if f["kind"].startswith("road:")]
        blds = [f for f in loaded if f["kind"] == "building"]
        self.assertEqual(len(roads), 1)
        self.assertEqual(roads[0]["name"], "Test Road")
        self.assertEqual(len(blds), 1)
        for f in roads + blds:
            for x, y in f["pts"]:
                self.assertTrue(0 <= x <= 800 and 0 <= y <= 430, (x, y))

    def test_no_amber_and_title_block_cell_is_empty(self):
        for name, svg in (("miri", make_locations.miri()), ("bintulu", make_locations.bintulu())):
            self.assertNotIn("#F2A900", svg)
            for t in ET.fromstring(svg).iter(NS + "text"):
                x, y = float(t.get("x", 0)), float(t.get("y", 0))
                self.assertFalse(530 <= x <= 780 and 440 <= y <= 484, f"{name}: text at {x},{y}")

    def test_pin_percentages(self):
        for name, (x, y) in make_locations.PINS.items():
            self.assertEqual(make_locations.pin_style(name), f"--pin-x:{x / 8:.1f}%;--pin-y:{y / 5:.1f}%")


if __name__ == "__main__":
    unittest.main()
