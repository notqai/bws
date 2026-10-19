# Checks the built site for mistakes that are easy to miss when editing by hand:
#   - links, images, scripts and form actions pointing at files that don't exist
#   - "#section" links pointing at an id that isn't on the target page
#   - images without alt text, and duplicate ids on a page
# Run: python3 tools/check_site.py   (exits with status 1 if anything is wrong)
import os, re, sys
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote

SITE_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site"))
URL_ATTRS = {"href", "src", "data-full", "action", "poster"}

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs, self.ids, self.dupes, self.no_alt = [], set(), set(), []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            (self.dupes if a["id"] in self.ids else self.ids).add(a["id"])
        if tag == "img" and a.get("alt") is None:
            self.no_alt.append(a.get("src", "?"))
        for k, v in attrs:
            if v is None: continue
            if k in URL_ATTRS: self.refs.append(v)
            elif k in ("srcset", "imagesrcset"):
                self.refs += [part.split()[0] for part in v.split(",") if part.strip()]

def local_target(page_path, ref):
    """Return (file path, fragment) for a link on this site, or None for external / special links."""
    u = urlsplit(ref)
    if u.scheme or u.netloc or ref.startswith(("mailto:", "tel:", "data:", "javascript:")):
        return None
    path = unquote(u.path)
    if not path:
        target = page_path
    elif path.startswith("/"):
        target = os.path.join(SITE_DIR, path.lstrip("/"))
    else:
        target = os.path.join(os.path.dirname(page_path), path)
    target = os.path.normpath(target)
    if os.path.isdir(target):
        target = os.path.join(target, "index.html")
    return target, u.fragment

def main():
    pages = {}
    for root, _dirs, files in os.walk(SITE_DIR):
        for f in files:
            if f.endswith(".html"):
                p = os.path.join(root, f)
                parser = Page()
                parser.feed(open(p, encoding="utf-8").read())
                pages[os.path.normpath(p)] = parser

    problems = []
    for p, page in sorted(pages.items()):
        rel = os.path.relpath(p, SITE_DIR)
        for i in sorted(page.dupes):
            problems.append(f"{rel}: duplicate id \"{i}\"")
        for src in page.no_alt:
            problems.append(f"{rel}: <img src=\"{src}\"> has no alt attribute")
        for ref in page.refs:
            t = local_target(p, ref)
            if not t: continue
            target, frag = t
            if not target.startswith(SITE_DIR):
                problems.append(f"{rel}: \"{ref}\" points outside the site folder")
            elif not os.path.exists(target):
                problems.append(f"{rel}: \"{ref}\" not found")
            elif frag and target in pages and frag not in pages[target].ids:
                problems.append(f"{rel}: \"{ref}\" has no element with id=\"{frag}\"")

    for line in problems:
        print(line)
    print(f"check_site: {len(pages)} pages checked, {len(problems)} problem(s)")
    return 1 if problems else 0

if __name__ == "__main__":
    sys.exit(main())
