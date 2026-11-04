#!/usr/bin/env python3
"""Validate the site.

Usage:  python3 tools/check.py            (full report)
        python3 tools/check.py --missing  (only the missing-media list)

Checks:
  1. data/projects.json has the expected fields and types, unique slugs,
     media slots that name real paths, and sections that point at real slots.
  2. Every internal link and asset path in the generated HTML (and CSS) exists,
     including #anchors.
  3. Reports which expected media files are present and which are missing.
  4. Home page weight without media (HTML + CSS + JS + fonts + icon) is under 150 KB.

Exit code 1 if there are errors. Missing media is reported but is not an error.
Standard library only.
"""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import parse_embed  # noqa: E402

BUDGET_KB = 150
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MEDIA_TYPES = {"video", "image", "compare", "embed"}
SECTION_TYPES = {"text", "list", "steps", "pipeline", "compare", "gallery", "film", "stats"}
PROJECT_FIELDS = {
    "slug": str, "title": str, "year": str, "role": str, "tools": list, "summary": str,
    "sections": list, "media": list, "published": bool, "order": int,
}
OPTIONAL_FIELDS = {
    "card_title": str, "category": str, "dates": str, "featured": bool, "wip": bool, "palette": list,
    "tagline": str, "brief": str, "what_i_did": list, "note": str, "note_prominent": bool,
    "results": list, "credits": list, "links": list, "card_stats": bool,
}

errors: list[str] = []
warnings: list[str] = []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


# --------------------------------------------------------------------------
# 1. data
# --------------------------------------------------------------------------

def slot_paths(slot: dict) -> list[tuple[str, str]]:
    """(kind, path) pairs a slot expects on disk."""
    t = slot.get("type")
    out = []
    if t == "video":
        out += [("video", slot.get("src", "")), ("poster", slot.get("poster", ""))]
    elif t == "image":
        out += [("image", slot.get("src", ""))]
    elif t == "compare":
        out += [("before", slot.get("before", "")), ("after", slot.get("after", ""))]
    elif t == "embed":
        out += [("video", slot.get("src", "")), ("poster", slot.get("poster", ""))]
    return [(k, p) for k, p in out if p]


def check_slot(where: str, slot: dict) -> None:
    t = slot.get("type")
    if t not in MEDIA_TYPES:
        err(f"{where}: media type '{t}' must be one of {sorted(MEDIA_TYPES)}")
        return
    if not slot.get("id"):
        err(f"{where}: media slot without an 'id'")
    need = {"video": ["src"], "image": ["src"], "compare": ["before", "after"], "embed": []}[t]
    for k in need:
        if not slot.get(k):
            err(f"{where}: {t} slot '{slot.get('id')}' needs '{k}'")
    if t == "embed" and not slot.get("url") and not slot.get("src"):
        err(f"{where}: embed slot '{slot.get('id')}' needs 'url' or a local 'src'")
    for kind, p in slot_paths(slot):
        if not p.startswith("media/"):
            err(f"{where}: '{p}' should live under media/")
        if p.startswith("/") or ".." in p:
            err(f"{where}: '{p}' must be a relative path inside the repo")
    for key in ("url", "embed"):
        u = slot.get(key)
        if u and not parse_embed(u):
            err(f"{where}: '{u}' is not a YouTube or Vimeo URL")
    if t in ("video", "image") and not slot.get("alt"):
        warn(f"{where}: slot '{slot.get('id')}' has no alt text")
    if t == "compare" and not (slot.get("alt_before") and slot.get("alt_after")):
        warn(f"{where}: compare slot '{slot.get('id')}' should have alt_before and alt_after")


def check_data() -> tuple[dict, list]:
    path = ROOT / "data" / "projects.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        err(f"data/projects.json is not valid JSON: {e}")
        return {}, []
    site = data.get("site", {})
    for k in ("name", "role", "location", "url", "title", "description", "headline", "email", "linkedin", "github", "showreel", "about"):
        if k not in site:
            err(f"site.{k} is missing")
    if site.get("url") and not site["url"].endswith("/"):
        err("site.url must end with '/'")
    if "showreel" in site:
        check_slot("site.showreel", site["showreel"])
    if site.get("showreel_full"):
        check_slot("site.showreel_full", site["showreel_full"])
    if site.get("about", {}).get("portrait"):
        check_slot("site.about.portrait", site["about"]["portrait"])

    pipelines = data.get("pipelines", {})
    for key, pipe in pipelines.items():
        if not pipe.get("nodes"):
            err(f"pipelines.{key} has no nodes")
        for i, n in enumerate(pipe.get("nodes", [])):
            if not n.get("label"):
                err(f"pipelines.{key}.nodes[{i}] needs a label")

    projects = data.get("projects", [])
    slugs, orders = set(), {}
    for i, p in enumerate(projects):
        where = f"projects[{i}] ({p.get('slug', '?')})"
        for f, typ in PROJECT_FIELDS.items():
            if f not in p:
                err(f"{where}: missing field '{f}'")
            elif not isinstance(p[f], typ) or (typ is int and isinstance(p[f], bool)):
                err(f"{where}: '{f}' should be {typ.__name__}")
        for f, typ in OPTIONAL_FIELDS.items():
            if f in p and not isinstance(p[f], typ):
                err(f"{where}: '{f}' should be {typ.__name__}")
        known = set(PROJECT_FIELDS) | set(OPTIONAL_FIELDS)
        for f in p:
            if f not in known:
                warn(f"{where}: unknown field '{f}' (ignored by build.py)")
        slug = p.get("slug", "")
        if not SLUG_RE.match(slug):
            err(f"{where}: slug '{slug}' must be lowercase letters, digits and hyphens")
        if slug in slugs:
            err(f"{where}: duplicate slug '{slug}'")
        slugs.add(slug)
        if p.get("published"):
            o = p.get("order")
            if o in orders:
                warn(f"{where}: order {o} is also used by '{orders[o]}'")
            orders[o] = slug
            if not p.get("year"):
                warn(f"{where}: 'year' is empty (it's hidden on the page; fill it in when known)")
            if not p.get("tools"):
                warn(f"{where}: 'tools' is empty (the Tools chips are hidden)")
            if not p.get("brief"):
                warn(f"{where}: no 'brief' paragraph")
        ids = set()
        for m in p.get("media", []):
            check_slot(where, m)
            if m.get("id") in ids:
                err(f"{where}: duplicate media id '{m.get('id')}'")
            ids.add(m.get("id"))
        if p.get("media") and "hero" not in ids and not p.get("card_stats"):
            warn(f"{where}: no media slot with id 'hero' (the first slot is used as the hero)")
        for j, s in enumerate(p.get("sections", [])):
            sw = f"{where}.sections[{j}]"
            t = s.get("type")
            if t not in SECTION_TYPES:
                err(f"{sw}: type '{t}' must be one of {sorted(SECTION_TYPES)}")
                continue
            refs = s.get("media")
            refs = [refs] if isinstance(refs, str) else (refs or [])
            if t in ("compare", "gallery", "film") and not refs:
                err(f"{sw}: '{t}' section needs 'media'")
            for r in refs:
                if r not in ids:
                    err(f"{sw}: media '{r}' is not a slot id in this project")
            if t == "compare":
                for r in refs:
                    slot = next((m for m in p.get("media", []) if m.get("id") == r), {})
                    if slot and slot.get("type") != "compare":
                        err(f"{sw}: '{r}' is not a compare slot")
            if t == "pipeline" and s.get("pipeline") not in pipelines:
                err(f"{sw}: pipeline '{s.get('pipeline')}' is not defined under 'pipelines'")
            if t == "steps" and not s.get("items"):
                err(f"{sw}: steps section needs 'items'")
            if t == "stats" and not s.get("stats"):
                err(f"{sw}: stats section needs 'stats'")
        for l in p.get("links", []):
            u = l.get("url", "")
            if not u.startswith(("http://", "https://", "mailto:")):
                target = ROOT / u
                if not (target.is_file() or (target / "index.html").is_file()):
                    err(f"{where}: link '{u}' does not resolve to a page (run build.py?)")
    return data, projects


# --------------------------------------------------------------------------
# 2. links in generated HTML
# --------------------------------------------------------------------------

class Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs: list[tuple[str, str]] = []
        self.ids: set[str] = set()
        self.imgs_without_alt = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        for k in ("href", "src", "poster", "data-embed"):
            if a.get(k):
                if k == "data-embed":
                    continue
                if tag == "link" and a.get("rel") in ("canonical",):
                    continue
                self.refs.append((tag, a[k]))
        if tag == "img" and "alt" not in a:
            self.imgs_without_alt += 1


def html_pages() -> list[Path]:
    pages = [ROOT / "index.html", ROOT / "404.html", ROOT / "about" / "index.html"]
    pages += sorted((ROOT / "work").glob("*/index.html"))
    return [p for p in pages if p.is_file()]


def resolve(page: Path, ref: str) -> tuple[Path | None, str]:
    u = urlparse(ref)
    if u.scheme or ref.startswith("//"):
        return None, ""
    path = unquote(u.path)
    if path == "":
        target = page
    elif path.startswith("/"):
        target = ROOT / path.lstrip("/")
    else:
        target = (page.parent / path).resolve()
    if target.is_dir() or path.endswith("/") or path == "":
        target = target / "index.html" if target.is_dir() or path.endswith("/") else target
    return target, u.fragment


def check_links(expected_pages: list[str]) -> None:
    parsed: dict[Path, Collector] = {}
    for page in html_pages():
        c = Collector()
        c.feed(page.read_text(encoding="utf-8"))
        parsed[page.resolve()] = c
        if c.imgs_without_alt:
            err(f"{page.relative_to(ROOT)}: {c.imgs_without_alt} <img> without alt")
    for rel in expected_pages:
        if not (ROOT / rel).is_file():
            err(f"expected page {rel} was not generated (run tools/build.py)")
    for page, c in parsed.items():
        prel = page.relative_to(ROOT)
        for tag, ref in c.refs:
            if ref.startswith(("mailto:", "tel:", "javascript:")):
                continue
            target, frag = resolve(page, ref)
            if target is None:
                continue
            target = target.resolve()
            if not target.is_file():
                err(f"{prel}: <{tag}> '{ref}' -> {target.relative_to(ROOT) if ROOT in target.parents else target} not found")
                continue
            if frag:
                tc = parsed.get(target)
                if tc is None and target.suffix == ".html":
                    tc = Collector()
                    tc.feed(target.read_text(encoding="utf-8"))
                if tc is not None and frag not in tc.ids:
                    err(f"{prel}: '{ref}' points at #{frag}, which doesn't exist on that page")
    css = ROOT / "assets" / "css" / "site.css"
    css_text = re.sub(r"url\(\s*\"data:[^\"]*\"\s*\)", "", css.read_text(encoding="utf-8"))
    for ref in re.findall(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)", css_text):
        if ref.startswith("data:"):
            continue
        if not (css.parent / ref).resolve().is_file():
            err(f"assets/css/site.css: url({ref}) not found")


# --------------------------------------------------------------------------
# 3. media report
# --------------------------------------------------------------------------

def media_report(data: dict, projects: list) -> tuple[list, list]:
    rows = []
    site = data.get("site", {})
    site_slots = [("Home: showreel", site.get("showreel")), ("Home: full showreel (optional)", site.get("showreel_full")),
                  ("About: portrait", site.get("about", {}).get("portrait"))]
    for label, slot in site_slots:
        if slot:
            for kind, p in slot_paths(slot):
                rows.append((label, slot.get("id"), kind, p))
    for p in sorted(projects, key=lambda x: x.get("order", 999)):
        if not p.get("published"):
            continue
        for m in p.get("media", []):
            for kind, path in slot_paths(m):
                rows.append((p["title"], m.get("id"), kind, path))
    seen, uniq = set(), []
    for r in rows:
        if r[3] not in seen:
            seen.add(r[3])
            uniq.append(r)
    present = [r for r in uniq if (ROOT / r[3]).is_file()]
    missing = [r for r in uniq if not (ROOT / r[3]).is_file()]
    media_dir = ROOT / "media"
    if media_dir.is_dir():
        for f in sorted(media_dir.rglob("*")):
            if f.is_file() and f.name not in (".gitkeep", "README.md") and str(f.relative_to(ROOT)) not in seen:
                warn(f"{f.relative_to(ROOT)} is in media/ but no slot in projects.json uses it")
    for r in present:
        size = (ROOT / r[3]).stat().st_size
        if r[2] == "video" and size > 8 * 1024 * 1024:
            warn(f"{r[3]} is {size / 1048576:.1f} MB; loops should be under 8 MB (see ADD_MEDIA.md)")
        if r[2] in ("image", "poster", "before", "after") and size > 600 * 1024:
            warn(f"{r[3]} is {size // 1024} KB; aim for under 400 KB (see ADD_MEDIA.md)")
    return present, missing


# --------------------------------------------------------------------------
# 4. page weight
# --------------------------------------------------------------------------

def page_weight() -> int:
    home = ROOT / "index.html"
    if not home.is_file():
        return 0
    total = home.stat().st_size
    c = Collector()
    c.feed(home.read_text(encoding="utf-8"))
    counted = set()
    for tag, ref in c.refs:
        if tag not in ("link", "script"):
            continue
        u = urlparse(ref)
        if u.scheme:
            continue
        f = (ROOT / unquote(u.path).lstrip("/")).resolve()
        if f.suffix in (".css", ".js", ".woff2", ".svg") and f.is_file() and f not in counted:
            counted.add(f)
            total += f.stat().st_size
    # fonts loaded by the stylesheet
    for f in (ROOT / "assets" / "fonts").glob("*.woff2"):
        if f.resolve() not in counted:
            counted.add(f.resolve())
            total += f.stat().st_size
    return total


def main() -> int:
    only_missing = "--missing" in sys.argv
    data, projects = check_data()
    published = [p for p in projects if p.get("published")]
    expected = ["index.html", "404.html", "about/index.html", "sitemap.xml", "robots.txt"]
    expected += [f"work/{p['slug']}/index.html" for p in published if p.get("slug")]
    for p in projects:
        if not p.get("published") and (ROOT / "work" / p.get("slug", "") / "index.html").is_file():
            warn(f"work/{p['slug']}/ exists but the project is unpublished (run tools/build.py to remove it)")
    check_links(expected)
    present, missing = media_report(data, projects)
    weight = page_weight()

    if only_missing:
        for r in missing:
            print(r[3])
        return 0

    print("Site check\n==========")
    print(f"Projects: {len(published)} published, {len(projects) - len(published)} hidden")
    print(f"Pages checked: {len(html_pages())}")
    kb = weight / 1024
    status = "OK" if kb <= BUDGET_KB else "OVER BUDGET"
    print(f"Home page weight without media: {kb:.1f} KB (budget {BUDGET_KB} KB) {status}")
    if kb > BUDGET_KB:
        err(f"home page weight {kb:.1f} KB is over the {BUDGET_KB} KB budget")

    print(f"\nMedia: {len(present)} present, {len(missing)} missing (placeholders shown)")
    if missing:
        w = max(len(r[3]) for r in missing)
        for r in missing:
            print(f"  [ ] {r[3]:<{w}}  {r[0]} · {r[1]} · {r[2]}")
    for r in present:
        print(f"  [x] {r[3]}")

    if warnings:
        print(f"\nWarnings ({len(warnings)})")
        for w_ in warnings:
            print(f"  - {w_}")
    if errors:
        print(f"\nErrors ({len(errors)})")
        for e in errors:
            print(f"  ! {e}")
        print("\nFAILED")
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
