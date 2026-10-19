# Lists every translatable string in the generated English pages (text nodes + alt/aria-label/placeholder/title/meta).
# Used to build tools/ms.json. Run: python3 tools/i18n_extract.py > /tmp/strings.txt
import os, re, sys, json
from html.parser import HTMLParser

SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site")
PAGES = ["index.html", "about.html", "services.html", "clients.html", "projects.html", "hse.html", "careers.html", "contact.html", "404.html"]
ATTRS = ("alt", "aria-label", "placeholder", "title")
SKIP_TAGS = {"script", "style"}

def norm(t):
    return re.sub(r"\s+", " ", t).strip()

def translatable(t):
    if not t or not re.search(r"[A-Za-z]{2,}", t):
        return False
    if re.fullmatch(r"[\w.+-]+@[\w.-]+", t) or t.startswith("http"):
        return False
    if re.search(r"[؀-ۿ]", t):  # Jawi
        return False
    return True

class X(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.stack = []; self.out = []
    def handle_starttag(self, tag, attrs):
        self.stack.append(tag)
        a = dict(attrs)
        for k in ATTRS:
            if a.get(k) and translatable(norm(a[k])): self.out.append(norm(a[k]))
        if tag == "meta" and a.get("content") and (a.get("name") in ("description", "twitter:title", "twitter:description") or a.get("property") in ("og:title", "og:description", "og:image:alt")):
            self.out.append(norm(a["content"]))
        if tag in ("img", "meta", "link", "input", "br", "hr", "source"): self.stack.pop()
    def handle_endtag(self, tag):
        while self.stack and self.stack.pop() != tag: pass
    def handle_data(self, d):
        if self.stack and self.stack[-1] in SKIP_TAGS: return
        t = norm(d)
        if translatable(t): self.out.append(t)

if __name__ == "__main__":
    seen = {}
    for p in PAGES:
        x = X(); x.feed(open(os.path.join(SITE, p), encoding="utf-8").read())
        for t in x.out: seen.setdefault(t, p)
    for t, p in seen.items():
        print(json.dumps(t, ensure_ascii=False))
    print(len(seen), file=sys.stderr)
