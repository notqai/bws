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

    def test_miri(self):
        self.check(make_locations.miri(), ["DWG BWS-LOC-01", "MIRI HQ", "PIASAU INDUSTRIAL ESTATE PH III",
                                           "JLN PRUNUS 1", "LOT 1743", "NOT TO SCALE", "4.4469° N  114.0116° E"])

    def test_bintulu(self):
        self.check(make_locations.bintulu(), ["DWG BWS-LOC-02", "BINTULU", "KIDURONG INDUSTRIAL ESTATE",
                                              "LOT 782", "LOT 124–128", "NOT TO SCALE", "3.2725° N  113.0802° E"])

    def test_pins_are_inside_the_drawing_area(self):
        for name, (x, y) in make_locations.PINS.items():
            self.assertTrue(0 < x < 800 and 0 < y < 430, name)  # above the title block

    def test_pin_percentages(self):
        self.assertEqual(make_locations.pin_style("miri"), "--pin-x:70%;--pin-y:70%")


if __name__ == "__main__":
    unittest.main()
