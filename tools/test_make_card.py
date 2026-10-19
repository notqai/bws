import tempfile
import unittest
from pathlib import Path

import make_card


def unfold(text):
    return text.replace("\r\n ", "")


class VCardTests(unittest.TestCase):
    def setUp(self):
        self.vcf = make_card.build_vcf(make_card.PEOPLE["mazinah"])

    def test_uses_crlf_only(self):
        self.assertTrue(self.vcf.startswith("BEGIN:VCARD\r\n"))
        self.assertTrue(self.vcf.endswith("END:VCARD\r\n"))
        self.assertNotIn("\n", self.vcf.replace("\r\n", ""))

    def test_core_fields(self):
        text = unfold(self.vcf)
        for line in [
            "VERSION:3.0",
            "N:Mohd Masri;Mazinah Binti;;;",
            "FN:Mazinah Binti Mohd Masri",
            "ORG:BWS Engineering Sdn Bhd",
            "TITLE:Executive Director / Personnel & Administration Manager",
            "TEL;TYPE=CELL,VOICE:+60198894946",
            "TEL;TYPE=WORK,VOICE:+6085652743",
            "EMAIL;TYPE=INTERNET,WORK:mazinahmasribws@gmail.com",
            "URL:https://www.bwsengineeringsb.com",
        ]:
            self.assertIn(line + "\r\n", text)

    def test_address_commas_are_escaped(self):
        text = unfold(self.vcf)
        self.assertIn(
            "ADR;TYPE=WORK:;;Lot 1743\\, Block 3 MCLD\\, Piasau Industrial Estate Phase III\\, Jalan Prunus 1;Miri;Sarawak;98000;Malaysia\r\n",
            text,
        )

    def test_lines_are_at_most_75_octets(self):
        for line in self.vcf.split("\r\n"):
            self.assertLessEqual(len(line.encode("utf-8")), 75, line)


class QrTests(unittest.TestCase):
    def test_svg_output(self):
        svg = make_card.build_qr_svg("https://example.com/card/mazinah")
        self.assertTrue(svg.lstrip().startswith("<svg"))
        self.assertIn("</svg>", svg)


class WriteAllTests(unittest.TestCase):
    def test_writes_vcf_and_qr_per_person(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_card.write_all(Path(tmp), "https://example.com")
            self.assertTrue((Path(tmp) / "mazinah.vcf").is_file())
            self.assertTrue((Path(tmp) / "mazinah-qr.svg").is_file())


if __name__ == "__main__":
    unittest.main()
