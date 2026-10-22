import os
import random
import shutil
import subprocess
import tempfile
import unittest

import optimize_images


def make_ppm(path, w, h, seed=1):
    """Gradient plus noise, so quality settings make a real size difference."""
    rnd = random.Random(seed)
    rows = bytearray()
    for y in range(h):
        for x in range(w):
            n = rnd.randint(-25, 25)
            rows += bytes(max(0, min(255, v + n)) for v in (x * 255 // w, y * 255 // h, 128))
    with open(path, "wb") as f:
        f.write(f"P6\n{w} {h}\n255\n".encode() + rows)


def make_webp(path, w, h, q):
    with tempfile.TemporaryDirectory() as tmp:
        ppm = os.path.join(tmp, "src.ppm")
        make_ppm(ppm, w, h)
        subprocess.run(["cwebp", "-quiet", "-q", str(q), ppm, "-o", path], check=True)


class OptimiseTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_dims_reads_webp_header(self):
        p = os.path.join(self.dir, "a-800.webp")
        make_webp(p, 320, 200, 90)
        self.assertEqual(optimize_images.dims(p), (320, 200))

    def test_shrinks_heavy_files_and_keeps_dimensions(self):
        big = os.path.join(self.dir, "photo-1600.webp")
        mid = os.path.join(self.dir, "photo-800.webp")
        make_webp(big, 640, 400, 100)
        make_webp(mid, 320, 200, 100)
        before = {p: os.path.getsize(p) for p in (big, mid)}
        optimize_images.optimise(self.dir)
        for p in (big, mid):
            self.assertLess(os.path.getsize(p), before[p])
        self.assertEqual(optimize_images.dims(big), (640, 400))
        self.assertEqual(optimize_images.dims(mid), (320, 200))

    def test_never_grows_a_file(self):
        p = os.path.join(self.dir, "tiny-800.webp")
        make_webp(p, 320, 200, 5)
        before = os.path.getsize(p)
        optimize_images.optimise(self.dir)
        self.assertLessEqual(os.path.getsize(p), before)

    def test_ignores_other_files(self):
        other = os.path.join(self.dir, "og-image.jpg")
        open(other, "wb").write(b"not an image")
        rows = optimize_images.optimise(self.dir)
        self.assertEqual(rows, [])
        self.assertEqual(open(other, "rb").read(), b"not an image")


if __name__ == "__main__":
    unittest.main()
