# Re-encodes the site's WebP photos (name-480/800/1600.webp) with tuned cwebp settings and keeps a
# file only if the new one is smaller. Smaller sizes are rebuilt from the largest sibling at their own
# pixel size, so the width/height in the HTML stay valid. og-image.jpg and client logos are not touched.
# Needs cwebp (brew install webp). Run: python3 tools/optimize_images.py
import os, re, shutil, subprocess, sys, tempfile

IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site", "assets", "img")
QUALITY = {480: 75, 800: 75, 1600: 72}
NAME_RE = re.compile(r"^(?P<stem>.+)-(?P<w>480|800|1600)\.webp$")


def dims(path):
    """(width, height) from the WebP header (VP8, VP8L or VP8X)."""
    with open(path, "rb") as f:
        b = f.read(30)
    kind = b[12:16]
    if kind == b"VP8X":
        return 1 + int.from_bytes(b[24:27], "little"), 1 + int.from_bytes(b[27:30], "little")
    if kind == b"VP8 ":
        return int.from_bytes(b[26:28], "little") & 0x3FFF, int.from_bytes(b[28:30], "little") & 0x3FFF
    if kind == b"VP8L":
        bits = int.from_bytes(b[21:25], "little")
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    raise ValueError(f"not a WebP file: {path}")


def encode(src, w, h, q, dst):
    subprocess.run(["cwebp", "-quiet", "-q", str(q), "-m", "6", "-af", "-mt", "-resize", str(w), str(h), src, "-o", dst],
                   check=True)


def optimise(img_dir=IMG_DIR):
    """Returns [(file name, old bytes, new bytes)]."""
    groups = {}
    for name in sorted(os.listdir(img_dir)):
        m = NAME_RE.match(name)
        if m:
            groups.setdefault(m["stem"], {})[int(m["w"])] = os.path.join(img_dir, name)
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        for stem, sizes in groups.items():
            master = sizes[max(sizes)]
            mw, mh = dims(master)
            # smallest first, so every size is cut from the untouched master before the master itself is re-encoded
            for w, path in sorted(sizes.items()):
                tw, th = dims(path)
                src = master if abs(tw / th - mw / mh) < 0.01 else path  # different crop: re-encode from itself
                out = os.path.join(tmp, os.path.basename(path))
                encode(src, tw, th, QUALITY[w], out)
                old, new = os.path.getsize(path), os.path.getsize(out)
                if new < old:
                    shutil.copyfile(out, path)
                rows.append((os.path.basename(path), old, min(old, new)))
    return rows


if __name__ == "__main__":
    rows = optimise(sys.argv[1] if len(sys.argv) > 1 else IMG_DIR)
    for name, old, new in sorted(rows, key=lambda r: r[1] - r[2], reverse=True):
        print(f"{name:45} {old / 1024:7.1f} KB -> {new / 1024:7.1f} KB")
    before, after = sum(r[1] for r in rows), sum(r[2] for r in rows)
    if before:
        print(f"{'TOTAL':45} {before / 1024:7.1f} KB -> {after / 1024:7.1f} KB  (-{(1 - after / before) * 100:.0f}%)")
    else:
        print("No matching WebP files found.")
