#!/usr/bin/env python3
"""Static SEO/AISO checks for the site in docs/.

Run from the repository root (or anywhere):

    python3 design/seo_check.py

Exit code 0 means every check passed. The checks encode the rules the site
already follows, so a future edit cannot quietly reintroduce the faults the
SEO audit found: wrong canonical host, a noindex directive slipping onto an
indexable page, titles/descriptions out of range, FAQ schema drifting from the
visible questions, stale or invalid sitemap entries, dead links in llms.txt,
missing or inaccessible search favicons, or em dashes returning to the copy.
"""

import json
import re
import struct
import sys
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
BASE = "https://www.justsimpleapps.online"
ROBOTS_META_NAMES = {"robots", "googlebot", "bingbot"}
# Stable, root-level raster icons. SVG is a browser enhancement, not a
# supported Google Search favicon format. The ICO advertises every embedded size.
FAVICON_SIZES = {
    "/favicon-96x96.png": {(96, 96)},
    "/favicon.ico": {(16, 16), (32, 32), (48, 48)},
}
ICON_RELS = {"icon", "shortcut", "apple-touch-icon", "apple-touch-icon-precomposed"}

# Matches the em dash itself plus the named/numeric HTML entities that render
# as one. chr() keeps this guard file free of the character it looks for.
EM_DASH_RE = re.compile(
    re.escape(chr(0x2014)) + r"|&[m]dash;?|&#(?:0*8212|x0*2014);?", re.I)
SITE_TEXT_SUFFIXES = {
    ".html", ".txt", ".css", ".js", ".json", ".xml", ".webmanifest", ".svg",
}

INDEXABLE = {
    "index.html": BASE + "/",
    "namaaz-reminder.html": BASE + "/namaaz-reminder",
    "screen-time-reminder.html": BASE + "/screen-time-reminder",
    "subscription-tracker.html": BASE + "/subscription-tracker",
    "vaccine-routine.html": BASE + "/vaccine-routine",
    "water-reminder.html": BASE + "/water-reminder",
    "steps-reminder.html": BASE + "/steps-reminder",
    "remindme.html": BASE + "/remindme",
    "arabic-clock.html": BASE + "/arabic-clock",
    "privacy.html": BASE + "/privacy",
}

# Every app page, i.e. everything except the collection home and privacy.
APP_PAGES = [f for f in INDEXABLE
             if f not in ("index.html", "privacy.html")]

problems = []
notes = []


def fail(msg):
    problems.append(msg)


def norm(s):
    return " ".join((s or "").split())


def robots_directives(content):
    """Return normalized robots directives without substring false positives."""
    return {
        token.lower()
        for token in re.split(r"[,;\s]+", content or "")
        if token
    }


def robots_blocks_indexing(content):
    """Whether a robots value explicitly excludes the page from search."""
    return bool(robots_directives(content) & {"noindex", "none"})


def robots_explicitly_allows_indexing(content):
    """Require an explicit index/all directive and reject any noindex override."""
    directives = robots_directives(content)
    return bool(directives & {"index", "all"}) and not bool(
        directives & {"noindex", "none"})


def indexability_meta_errors(meta_tags):
    """Validate general, Googlebot and Bingbot robots meta directives."""
    robot_tags = []
    for meta in meta_tags:
        name = (meta.get("name") or "").strip().lower()
        if name in ROBOTS_META_NAMES:
            robot_tags.append((name, meta.get("content", "")))

    general = [content for name, content in robot_tags if name == "robots"]
    errors = []
    if not general:
        errors.append("meta robots tag is missing")
    elif not any(robots_explicitly_allows_indexing(value) for value in general):
        errors.append("meta robots must explicitly allow indexing")

    for name, content in robot_tags:
        if robots_blocks_indexing(content):
            errors.append(f"meta {name} directive blocks indexing ({content!r})")
    return errors


def meta_blocks_indexing(meta_tags):
    """Whether any general, Googlebot or Bingbot meta tag says noindex/none."""
    return any(
        (meta.get("name") or "").strip().lower() in ROBOTS_META_NAMES
        and robots_blocks_indexing(meta.get("content", ""))
        for meta in meta_tags
    )


def favicon_link_errors(links):
    """Require stable, correctly sized raster icons in addition to any SVG."""
    errors = []
    icons = {}
    for link in links:
        rels = set((link.get("rel") or "").lower().split())
        if not rels & ICON_RELS:
            continue
        href = link.get("href") or ""
        parsed = urlparse(href)
        if (not href.startswith("/") or href.startswith("//") or parsed.scheme
                or parsed.netloc or parsed.query or parsed.fragment):
            errors.append(f"icon URL must be stable and root-relative: {href!r}")
        if href in icons:
            errors.append(f"duplicate icon declaration: {href}")
            continue
        icons[href] = rels
        if Path(href).suffix.lower() == ".svg":
            continue
        sizes = set()
        for token in (link.get("sizes") or "").lower().split():
            match = re.fullmatch(r"([1-9]\d*)x([1-9]\d*)", token)
            if match:
                sizes.add(tuple(map(int, match.groups())))
        if not sizes:
            errors.append(f"raster icon has no valid sizes: {href}")
        elif href in FAVICON_SIZES and sizes != FAVICON_SIZES[href]:
            errors.append(f"incorrect declared sizes for {href}: {sorted(sizes)}")
        elif any(w != h or w < 8 for w, h in sizes):
            errors.append(f"icon must be square and at least 8px: {href}")
        if href == "/favicon-96x96.png" and link.get("type") != "image/png":
            errors.append("the 96px search icon must have type=image/png")
    for href in FAVICON_SIZES:
        if not icons.get(href, set()) & {"icon", "shortcut"}:
            errors.append(f"missing rel=icon declaration for {href}")
    return errors


def favicon_file_errors(path):
    """Read PNG/ICO headers without adding an image-library dependency to CI."""
    if not path.is_file():
        return [f"icon file is missing: {path.name}"]
    data = path.read_bytes()
    if path.suffix.lower() == ".svg":
        return []
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24 and data[12:16] == b"IHDR":
        sizes = {struct.unpack(">II", data[16:24])}
    elif data.startswith(b"\x00\x00\x01\x00") and len(data) >= 6:
        count = struct.unpack("<H", data[4:6])[0]
        if not count or len(data) < 6 + count * 16:
            return [f"truncated or empty ICO: {path.name}"]
        sizes = {(data[6 + i * 16] or 256, data[7 + i * 16] or 256)
                 for i in range(count)}
    else:
        return [f"not a valid PNG or ICO header: {path.name}"]
    errors = []
    expected = FAVICON_SIZES.get("/" + path.name)
    if expected is not None and sizes != expected:
        errors.append(f"incorrect actual sizes for {path.name}: {sorted(sizes)}")
    if any(w != h or w < 8 for w, h in sizes):
        errors.append(f"icon must be square and at least 8px: {path.name}")
    return errors


def favicon_crawl_errors(robots_text, urls):
    """Google needs both the page and its icon, not just ordinary Googlebot."""
    robots = RobotFileParser()
    robots.parse(robots_text.splitlines())
    return [f"{agent}: robots.txt blocks {url}"
            for agent in ("Googlebot", "Googlebot-Image")
            for url in sorted(set(urls)) if not robots.can_fetch(agent, url)]


def check_favicons():
    robots_text = (DOCS / "robots.txt").read_text(encoding="utf-8")
    urls = {BASE + "/"}
    for page in sorted(DOCS.glob("*.html")):
        parsed, _, _ = parse(page)
        errors = favicon_link_errors(parsed.head_links)
        for link in parsed.head_links:
            if not set((link.get("rel") or "").lower().split()) & ICON_RELS:
                continue
            href = link.get("href") or ""
            parsed_url = urlparse(href)
            if not href.startswith("/") or href.startswith("//"):
                continue
            icon = (DOCS / parsed_url.path.lstrip("/")).resolve()
            if not icon.is_relative_to(DOCS.resolve()):
                errors.append(f"icon escapes the site directory: {href}")
                continue
            errors.extend(favicon_file_errors(icon))
            if not parsed_url.query and not parsed_url.fragment:
                urls.add(BASE + parsed_url.path)
        for error in errors:
            fail(f"{page.name}: favicon: {error}")
    for error in favicon_crawl_errors(robots_text, urls):
        fail(f"favicon: {error}")


class PageParser(HTMLParser):
    """Collects the handful of facts each check needs."""

    def __init__(self):
        super().__init__()
        self.meta = []          # list of dicts
        self.links = []         # <link> dicts
        self.head_links = []    # icon declarations must be in <head>
        self._in_head = False
        self.canonical = None
        self.h1_count = 0
        self.html_lang = None
        self.schema_blocks = []
        self._in_schema = False
        self._schema_buf = []
        self.details = []       # visible FAQ (q, a)
        self._det = None
        self._in_summary = False
        self._in_p = False
        self.ids = set()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "head":
            self._in_head = True
        if self._in_head and tag == "link":
            self.head_links.append(d)
        if tag == "html" and d.get("lang"):
            self.html_lang = d["lang"]
        elif tag == "meta":
            self.meta.append(d)
        elif tag == "link":
            self.links.append(d)
            if d.get("rel") == "canonical":
                self.canonical = d.get("href")
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "script" and d.get("type") == "application/ld+json":
            self._in_schema = True
            self._schema_buf = []
        elif tag == "details":
            self._det = {"q": "", "a": ""}
        elif tag == "summary" and self._det is not None:
            self._in_summary = True
        elif tag == "p" and self._det is not None:
            self._in_p = True
        if d.get("id"):
            self.ids.add(d["id"])
        if tag == "a" and d.get("href"):
            self.hrefs.append(d["href"])

    def handle_endtag(self, tag):
        if tag == "head":
            self._in_head = False
        if tag == "script" and self._in_schema:
            self._in_schema = False
            self.schema_blocks.append("".join(self._schema_buf))
        elif tag == "details" and self._det is not None:
            self.details.append((norm(self._det["q"]), norm(self._det["a"])))
            self._det = None
        elif tag == "summary":
            self._in_summary = False
        elif tag == "p" and self._det is not None:
            self._in_p = False

    def handle_data(self, data):
        if self._in_schema:
            self._schema_buf.append(data)
        if self._det is not None:
            if self._in_summary:
                self._det["q"] += data
            elif self._in_p:
                self._det["a"] += data


def parse(path):
    text = path.read_text(encoding="utf-8")
    p = PageParser()
    p.feed(text)
    # <title> text
    m = re.search(r"<title>(.*?)</title>", text, re.S)
    title = norm(m.group(1)) if m else ""
    return p, text, title


def meta_content(p, name=None, prop=None):
    for m in p.meta:
        if name and m.get("name") == name:
            return m.get("content", "")
        if prop and m.get("property") == prop:
            return m.get("content", "")
    return None


def check_page(fname, canonical_url):
    path = DOCS / fname
    if not path.exists():
        fail(f"{fname}: file missing")
        return None
    p, text, title = parse(path)

    # -- banned hosts: the github.io fault must never come back
    for bad in ("github.io", "localhost", "127.0.0.1", "example.com"):
        if bad in text:
            fail(f"{fname}: contains banned host/substring {bad!r}")

    # -- language
    if not p.html_lang:
        fail(f"{fname}: <html> has no lang attribute")

    # -- exactly one h1
    if p.h1_count != 1:
        fail(f"{fname}: expected exactly one <h1>, found {p.h1_count}")

    # -- title
    if not title:
        fail(f"{fname}: missing <title>")
    elif not 20 <= len(title) <= 65:
        fail(f"{fname}: title length {len(title)} outside 20-65: {title!r}")

    # -- meta description
    desc = meta_content(p, name="description")
    if desc is None:
        fail(f"{fname}: missing meta description")
    elif not 70 <= len(desc) <= 170:
        fail(f"{fname}: description length {len(desc)} outside 70-170: {desc!r}")

    # -- robots: exact directives matter; `noindex` contains the substring `index`
    # and must never be mistaken for an indexing permission.
    for error in indexability_meta_errors(p.meta):
        fail(f"{fname}: {error}")

    # -- canonical / og:url
    if p.canonical != canonical_url:
        fail(f"{fname}: canonical {p.canonical!r} != {canonical_url!r}")
    og_url = meta_content(p, prop="og:url")
    if og_url != canonical_url:
        fail(f"{fname}: og:url {og_url!r} != {canonical_url!r}")

    # -- social images must be absolute on the canonical host and exist
    for prop in ("og:image", "twitter:image"):
        img = meta_content(p, prop=prop) or meta_content(p, name=prop)
        if not img:
            fail(f"{fname}: missing {prop}")
            continue
        if not img.startswith(BASE + "/"):
            fail(f"{fname}: {prop} not on {BASE}: {img!r}")
        else:
            rel = img[len(BASE) + 1:]
            if not (DOCS / rel).exists():
                fail(f"{fname}: {prop} target does not exist: {rel}")

    # -- og:title / twitter:title present
    for prop in ("og:title", "og:description"):
        if meta_content(p, prop=prop) is None:
            fail(f"{fname}: missing {prop}")

    # -- JSON-LD parses
    graphs = []
    for block in p.schema_blocks:
        try:
            data = json.loads(block)
        except json.JSONDecodeError as e:
            fail(f"{fname}: JSON-LD does not parse: {e}")
            continue
        graphs.extend(data.get("@graph", [data]))
    if not graphs:
        fail(f"{fname}: no JSON-LD found")

    # -- FAQ schema must match visible <details> exactly
    schema_faq = []
    for node in graphs:
        if node.get("@type") == "FAQPage":
            for q in node.get("mainEntity", []):
                schema_faq.append((norm(q["name"]),
                                   norm(q.get("acceptedAnswer", {}).get("text"))))
    if schema_faq or p.details:
        if schema_faq != p.details:
            sv, vv = set(schema_faq), set(p.details)
            for q in sorted(vv - sv):
                fail(f"{fname}: visible FAQ not in schema: {q!r}")
            for q in sorted(sv - vv):
                fail(f"{fname}: schema FAQ not visible on page: {q!r}")
            if sv == vv and schema_faq != p.details:
                fail(f"{fname}: FAQ order differs between schema and page")

    # -- every internal link resolves to a file or an id on the target page
    for href in p.hrefs:
        if href.startswith(("http://", "https://", "mailto:")):
            continue
        if href.startswith("#"):
            if href[1:] and href[1:] not in p.ids:
                fail(f"{fname}: anchor {href} has no target id")
            continue
        target, _, frag = href.partition("#")
        if target in ("", "./", "/"):
            tfile = DOCS / "index.html"
        elif target.startswith("/"):
            rel = target[1:]
            cand = DOCS / (rel + ".html")
            tfile = cand if cand.exists() else DOCS / rel / "index.html"
        else:
            tfile = DOCS / target.lstrip("./")
        if not tfile.exists():
            fail(f"{fname}: internal link {href} does not resolve")
            continue
        if frag:
            tp, _, _ = parse(tfile)
            if frag not in tp.ids:
                fail(f"{fname}: link {href} targets missing id #{frag}")

    return p, graphs


def page_modified_date(fname):
    """Read a page's WebPage/CollectionPage dateModified from its JSON-LD."""
    p, _, _ = parse(DOCS / fname)
    for block in p.schema_blocks:
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue  # check_page reports malformed structured data separately
        for node in data.get("@graph", [data]):
            if node.get("@type") in {"WebPage", "CollectionPage"}:
                modified = node.get("dateModified")
                if modified:
                    return str(modified)
    return None


def parse_sitemap_lastmod(value):
    """Parse the ISO date or datetime formats allowed by the sitemap protocol."""
    value = (value or "").strip()
    try:
        return date.fromisoformat(value)
    except ValueError:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
        except ValueError:
            return None


def check_sitemap():
    path = DOCS / "sitemap.xml"
    if not path.exists():
        fail("sitemap.xml missing")
        return
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as error:
        fail(f"sitemap: invalid XML ({error})")
        return

    sitemap_namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    if root.tag != sitemap_namespace + "urlset":
        fail("sitemap: root must be a sitemap.org urlset")

    expected = {url: fname for fname, url in INDEXABLE.items()}
    seen = set()
    for entry in root.findall(sitemap_namespace + "url"):
        loc_element = entry.find(sitemap_namespace + "loc")
        lastmod_element = entry.find(sitemap_namespace + "lastmod")
        loc = (loc_element.text or "").strip() if loc_element is not None else ""
        lastmod = (lastmod_element.text or "").strip() if lastmod_element is not None else ""
        if not loc:
            fail("sitemap: <url> entry has no <loc>")
            continue
        if loc in seen:
            fail(f"sitemap: duplicate loc entry: {loc}")
        seen.add(loc)
        if not loc.startswith(BASE + "/") and loc != BASE + "/":
            fail(f"sitemap: loc off canonical host: {loc}")
        if loc not in expected:
            fail(f"sitemap: loc has no indexable page: {loc}")
            continue

        if not lastmod:
            fail(f"sitemap: missing lastmod for {loc}")
            continue
        sitemap_date = parse_sitemap_lastmod(lastmod)
        if sitemap_date is None:
            fail(f"sitemap: invalid lastmod {lastmod!r} for {loc}")
            continue

        page_file = DOCS / expected[loc]
        if not page_file.exists():
            fail(f"sitemap: indexed page file is missing: {expected[loc]}")
            continue
        page_date_value = page_modified_date(expected[loc])
        page_date = parse_sitemap_lastmod(page_date_value)
        if page_date is None:
            fail(f"sitemap: {expected[loc]} has no valid JSON-LD dateModified")
        elif sitemap_date != page_date:
            fail(f"sitemap: lastmod for {loc} ({sitemap_date}) does not match "
                 f"page dateModified ({page_date})")

    for url in expected:
        if url not in seen:
            fail(f"sitemap: page not listed: {url}")


def check_robots():
    path = DOCS / "robots.txt"
    if not path.exists():
        fail("robots.txt missing")
        return
    text = path.read_text(encoding="utf-8")
    if f"Sitemap: {BASE}/sitemap.xml" not in text:
        fail("robots.txt: sitemap line missing or off canonical host")
    if "User-agent: *" not in text or "Allow: /" not in text:
        fail("robots.txt: missing blanket allow")
    for bot in ("GPTBot", "ClaudeBot", "PerplexityBot", "OAI-SearchBot"):
        if bot not in text:
            fail(f"robots.txt: AI crawler {bot} not listed")


def check_llms():
    path = DOCS / "llms.txt"
    if not path.exists():
        fail("llms.txt missing")
        return
    text = path.read_text(encoding="utf-8")
    for url in re.findall(r"https://[^\s)>]+", text):
        host = urlparse(url).netloc
        if host != urlparse(BASE).netloc:
            continue  # external links (GitHub) are not checked offline
        rel = urlparse(url).path.lstrip("/")
        frag = urlparse(url).fragment
        if rel in ("", None):
            tfile = DOCS / "index.html"
        else:
            cand = DOCS / (rel + ".html")
            tfile = cand if cand.exists() else DOCS / rel / "index.html"
        if not tfile.exists():
            fail(f"llms.txt: URL has no page: {url}")
            continue
        if frag:
            tp, _, _ = parse(tfile)
            if frag not in tp.ids:
                fail(f"llms.txt: URL targets missing id: {url}")


def check_entity_consistency(index_graphs):
    """App pages must carry the same Organization @id/values as the home page."""
    org_index = next((n for n in index_graphs
                      if n.get("@type") == "Organization"), None)
    if org_index is None:
        fail("index.html: no Organization node")
        return
    for fname in INDEXABLE:
        if fname in ("index.html", "404.html"):
            continue
        _, text, _ = parse(DOCS / fname) or (None, "", "")
        try:
            blocks = re.findall(
                r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>',
                text, re.S)
            nodes = []
            for b in blocks:
                nodes.extend(json.loads(b).get("@graph", []))
        except json.JSONDecodeError:
            continue  # already reported by check_page
        org = next((n for n in nodes if n.get("@type") == "Organization"), None)
        if org is None:
            fail(f"{fname}: no Organization node (entity unresolvable on its own)")
            continue
        for key in ("@id", "name", "url", "alternateName"):
            if org.get(key) != org_index.get(key):
                fail(f"{fname}: Organization.{key} differs from index.html")


def check_itemlist_parity(index_graphs):
    """Home ItemList entries must mirror each app page's SoftwareApplication node.

    Guards the @id unification (…/#software vs …#software) and keeps
    softwareVersion / downloadUrl / sameAs identical on both sides.
    """
    il = next((n for n in index_graphs if n.get("@type") == "ItemList"), None)
    if il is None:
        fail("index.html: no ItemList node")
        return
    home = {}
    for entry in il.get("itemListElement", []):
        item = entry.get("item") or {}
        if item.get("url"):
            home[item["url"]] = item
    for fname in APP_PAGES:
        _, text, _ = parse(DOCS / fname) or (None, "", "")
        try:
            blocks = re.findall(
                r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>',
                text, re.S)
            nodes = []
            for b in blocks:
                nodes.extend(json.loads(b).get("@graph", []))
        except json.JSONDecodeError:
            continue  # already reported by check_page
        app = next((n for n in nodes if n.get("@type") == "SoftwareApplication"),
                   None)
        if app is None:
            fail(f"{fname}: no SoftwareApplication node")
            continue
        item = home.get(app.get("url"))
        if item is None:
            fail(f"index.html: ItemList missing app {app.get('url')}")
            continue
        for key in ("@id", "softwareVersion", "downloadUrl", "sameAs"):
            if item.get(key) != app.get(key):
                fail(f"index.html: ItemList[{app.get('url')}].{key} "
                     f"= {item.get(key)!r} but {fname} has {app.get(key)!r}")


def check_discovery():
    """Each app page is reachable from the hub and from every sibling.

    Internal linking is what turns eight thin pages into one crawlable
    cluster, and E-E-A-T metadata (author, publication date, speakable
    passages) is what an answer engine quotes. Both are easy to lose in a
    hand edit, so they are checked here.
    """
    hub, _, _ = parse(DOCS / "index.html")
    for fname in APP_PAGES:
        path = "/" + fname[:-5]
        if path not in hub.hrefs:
            fail(f"index.html: no internal link to {path}")
    for fname in APP_PAGES:
        page, text, _ = parse(DOCS / fname)
        siblings = {"/" + f[:-5] for f in APP_PAGES if f != fname}
        linked = siblings & set(page.hrefs)
        if linked != siblings:
            fail(f"{fname}: links to {len(linked)} of {len(siblings)} "
                 f"sibling app pages (missing "
                 f"{', '.join(sorted(siblings - linked))})")
        if meta_content(page, name="author") != "Owais Khan":
            fail(f"{fname}: missing <meta name=author content='Owais Khan'>")
        graphs = []
        for block in page.schema_blocks:
            try:
                graphs.extend(json.loads(block).get("@graph", []))
            except json.JSONDecodeError:
                pass
        web = next((n for n in graphs if n.get("@type") == "WebPage"), None)
        if web is None:
            fail(f"{fname}: no WebPage node")
            continue
        for key in ("datePublished", "dateModified"):
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(web.get(key, ""))):
                fail(f"{fname}: WebPage.{key} missing or malformed "
                     f"({web.get(key)!r})")
        if "speakable" not in web:
            fail(f"{fname}: WebPage has no speakable passages")


def check_uniqueness():
    """No two pages may share a <title> or a meta description.

    Eight near-identical app pages make it easy to copy a title and forget to
    change it, which is exactly the duplicate-content fault this site exists
    to avoid.
    """
    titles, descs = {}, {}
    for fname in INDEXABLE:
        p, _, title = parse(DOCS / fname)
        titles.setdefault(title, []).append(fname)
        descs.setdefault(meta_content(p, name="description") or "", []).append(fname)
        if fname != "index.html" and meta_content(p, name="author") != "Owais Khan":
            fail(f"{fname}: missing <meta name=author content='Owais Khan'>")
    for title, pages in titles.items():
        if len(pages) > 1:
            fail(f"duplicate <title> {title!r} on {', '.join(pages)}")
    for desc, pages in descs.items():
        if len(pages) > 1:
            fail(f"duplicate meta description on {', '.join(pages)}")


def check_speakable():
    """Every WebPage node must say which passages may be quoted or read out."""
    for fname in INDEXABLE:
        p, _, _ = parse(DOCS / fname)
        graphs = []
        for block in p.schema_blocks:
            try:
                graphs.extend(json.loads(block).get("@graph", []))
            except json.JSONDecodeError:
                return  # reported by check_page
        pages = [n for n in graphs
                 if n.get("@type") in ("WebPage", "CollectionPage")]
        if not pages:
            fail(f"{fname}: no WebPage/CollectionPage node")
            continue
        for node in pages:
            if "speakable" not in node:
                fail(f"{fname}: {node.get('@type')} has no speakable passages")


HTML_VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
             "link", "meta", "param", "source", "track", "wbr"}
# Elements whose end tag may be omitted, per the HTML spec.
HTML_OPTIONAL = {"li", "p", "dt", "dd", "tr", "td", "th", "option", "thead",
                 "tbody", "tfoot", "colgroup", "caption", "rt", "rp"}


def check_faq_questions():
    """No two pages may ask the same FAQ question.

    A question like "Is it free?" repeated on eight pages is ambiguous to an
    answer engine: it cannot tell which product the snippet is about. Each
    question therefore names its app, and this check keeps it that way.
    """
    seen = {}
    for fname in INDEXABLE:
        page, _, _ = parse(DOCS / fname)
        for question, _answer in page.details:
            if question in seen:
                fail(f"FAQ question asked twice: {question!r} "
                     f"on {seen[question]} and {fname}")
            seen[question] = fname


def check_markup():
    """Catch stray or unclosed block tags (a misplaced </div> once shipped)."""
    from html.parser import HTMLParser as _HP

    class Stack(_HP):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.stack = []
            self.errs = []

        def handle_starttag(self, tag, attrs):
            if tag in HTML_VOID:
                return
            if tag in HTML_OPTIONAL and self.stack and self.stack[-1] == tag:
                self.stack.pop()
            self.stack.append(tag)

        def handle_endtag(self, tag):
            if tag in HTML_VOID:
                return
            if tag in self.stack:
                while self.stack and self.stack[-1] != tag:
                    open_tag = self.stack.pop()
                    if open_tag not in HTML_OPTIONAL:
                        self.errs.append(f"<{open_tag}> left open before </{tag}>")
                if self.stack:
                    self.stack.pop()
            elif tag not in HTML_OPTIONAL:
                self.errs.append(f"stray </{tag}>")

    for path in sorted(DOCS.glob("*.html")):
        parser = Stack()
        parser.feed(path.read_text(encoding="utf-8"))
        leftovers = [t for t in parser.stack if t not in HTML_OPTIONAL]
        errs = parser.errs + [f"<{t}> never closed" for t in leftovers]
        for err in errs:
            fail(f"{path.name}: {err}")


def check_404():
    """The branded not-found page is noindex but still worth a real description."""
    path = DOCS / "404.html"
    if not path.exists():
        fail("404.html missing")
        return
    p, _, _ = parse(path)
    desc = meta_content(p, name="description")
    if not desc or len(desc) < 70:
        fail("404.html: missing or too-short meta description")
    if not meta_content(p, prop="og:image"):
        fail("404.html: missing og:image")
    if not meta_blocks_indexing(p.meta):
        fail("404.html: must have a robots/googlebot noindex or none directive")


def check_typography():
    """Page copy, metadata and generated assets must not contain em dashes."""
    paths = [p for p in DOCS.rglob("*")
             if p.is_file() and p.suffix.lower() in SITE_TEXT_SUFFIXES]
    paths.extend([p for p in (ROOT / "design").rglob("*")
                  if p.is_file() and p.suffix.lower() in SITE_TEXT_SUFFIXES])
    paths.append(ROOT / "README.md")
    for path in paths:
        text = path.read_text(encoding="utf-8")
        match = EM_DASH_RE.search(text)
        if match:
            fail(f"{path.relative_to(ROOT)}: contains an em dash token "
                 f"({match.group(0)!r}); use plain punctuation instead")


def main():
    index_graphs = []
    for fname, url in INDEXABLE.items():
        res = check_page(fname, url)
        if res and fname == "index.html":
            index_graphs = res[1]
    # 404: check_404() requires an exact noindex/none robots directive.
    check_sitemap()
    check_robots()
    check_favicons()
    check_llms()
    check_entity_consistency(index_graphs)
    check_itemlist_parity(index_graphs)
    check_discovery()
    check_uniqueness()
    check_speakable()
    check_faq_questions()
    check_markup()
    check_404()
    check_typography()

    if problems:
        print(f"SEO check FAILED: {len(problems)} problem(s):\n")
        for pr in problems:
            print(f"  ✗ {pr}")
        sys.exit(1)
    print(f"SEO check passed: {len(INDEXABLE)} indexable pages, "
          f"robots directives, sitemap dates, links and entity graphs consistent.")


if __name__ == "__main__":
    main()
