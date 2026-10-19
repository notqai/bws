# Joins the stylesheet partials (src/css/*.css, in file-name order) into site/assets/css/styles.css.
# Run automatically by generate_site.py; can also be run on its own after a CSS-only change.
import glob, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "site", "assets", "css", "styles.css")

def build():
    parts = sorted(glob.glob(os.path.join(ROOT, "src", "css", "*.css")))
    if not parts:
        raise SystemExit("build_css: no partials found in src/css/")
    css = "".join(open(p, encoding="utf-8").read() for p in parts)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(css)

if __name__ == "__main__":
    build()
