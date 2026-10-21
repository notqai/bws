import unittest
import xml.etree.ElementTree as ET

import make_locations

NS = "{http://www.w3.org/2000/svg}"


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
            east = lon + 100 / (math.cos(math.radians(lat)) * 111320)    # 100 m east of the office
            north = lat + 100 / 110540                                    # 100 m north of the office
            x0, y0 = make_locations.project(name, lat, lon)
            x1, y1 = make_locations.project(name, lat, east)
            x2, y2 = make_locations.project(name, north, lon)
            self.assertAlmostEqual(x1 - x0, 100 * site["scale"], places=6)
            self.assertAlmostEqual(y1, y0, places=6)
            self.assertAlmostEqual(y0 - y2, 100 * site["scale"], places=6)   # north is up

    def test_pin_percentages(self):
        for name, (x, y) in make_locations.PINS.items():
            self.assertEqual(make_locations.pin_style(name), f"--pin-x:{x / 8:.1f}%;--pin-y:{y / 5:.1f}%")


if __name__ == "__main__":
    unittest.main()
