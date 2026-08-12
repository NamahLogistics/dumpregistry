#!/usr/bin/env python3
"""Generate sitemap index — verified city-sourced URLs only."""

from __future__ import annotations

import json
import re
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SITE = (ROOT / "apps" / "web" / "public").resolve()
SITEMAP_DIR = SITE / "sitemaps"
BASE = "https://www.dumpregistry.org"
MAX_URLS = 50_000


def facility_slug(city_slug: str, name: str, address: str | None) -> str:
    raw = f"{city_slug}-{name}-{address or ''}".lower()
    raw = raw.replace("&", " and ")
    raw = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")[:96]
    return raw or f"{city_slug}-facility"


def url_entry(loc: str, priority: str = "0.6", lastmod: str | None = None) -> str:
    lines = [
        "  <url>\n",
        f"    <loc>{escape(loc)}</loc>\n",
    ]
    if lastmod:
        # ISO date only
        day = lastmod[:10] if len(lastmod) >= 10 else lastmod
        lines.append(f"    <lastmod>{escape(day)}</lastmod>\n")
    lines.append("    <changefreq>monthly</changefreq>\n")
    lines.append(f"    <priority>{priority}</priority>\n")
    lines.append("  </url>\n")
    return "".join(lines)


def main() -> None:
    pages = json.loads((ROOT / "data" / "resolved" / "pages.json").read_text())
    zip_hubs = json.loads((ROOT / "data" / "resolved" / "zip_hubs.json").read_text())
    facilities = json.loads((ROOT / "data" / "facilities" / "all.json").read_text())
    covered_cities = sorted({(p["state_slug"], p["city_slug"]) for p in pages if p.get("indexable")})
    city_state = {c: s for s, c in covered_cities}

    states = sorted({s for s, _ in covered_cities})
    items = json.loads((ROOT / "data" / "items.json").read_text())
    guides_dir = ROOT / "content" / "guides"
    guide_slugs = sorted(p.stem for p in guides_dir.glob("*.md")) if guides_dir.exists() else []

    # lastmod for dispose pages by city/item
    page_lastmod: dict[tuple[str, str, str], str] = {}
    for p in pages:
        if not p.get("indexable"):
            continue
        key = (p["state_slug"], p["city_slug"], p["item_slug"])
        verified = p.get("last_verified_at") or ""
        if verified and (key not in page_lastmod or verified > page_lastmod[key]):
            page_lastmod[key] = verified

    urls: list[tuple[str, str, str | None]] = [
        (f"{BASE}/", "1.0", None),
        (f"{BASE}/about", "0.5", None),
        (f"{BASE}/methodology", "0.5", None),
        (f"{BASE}/sources", "0.5", None),
        (f"{BASE}/partners", "0.6", None),
        (f"{BASE}/cities", "0.8", None),
        (f"{BASE}/materials", "0.85", None),
        (f"{BASE}/centers", "0.85", None),
        (f"{BASE}/guides", "0.8", None),
    ]
    for item in items:
        slug = item.get("slug")
        if slug:
            urls.append((f"{BASE}/materials/{slug}", "0.7", None))
    for slug in guide_slugs:
        urls.append((f"{BASE}/guides/{slug}", "0.65", None))
    for state_slug in states:
        urls.append((f"{BASE}/{state_slug}", "0.75", None))
    for state_slug, city_slug in covered_cities:
        urls.append((f"{BASE}/{state_slug}/{city_slug}", "0.7", None))
    for z in zip_hubs:
        if z.get("indexable"):
            urls.append((f"{BASE}/{z['state_slug']}/{z['city_slug']}/{z['zip']}", "0.55", None))
    for p in pages:
        if not p.get("indexable"):
            continue
        key = (p["state_slug"], p["city_slug"], p["item_slug"])
        urls.append(
            (
                f"{BASE}/{p['state_slug']}/{p['city_slug']}/dispose/{p['item_slug']}",
                "0.8",
                page_lastmod.get(key),
            )
        )

    seen_fac: set[str] = set()
    for f in facilities:
        slug_city = f.get("city_slug") or ""
        state_slug = city_state.get(slug_city)
        if not state_slug:
            continue
        if f.get("lat") is None or f.get("lng") is None:
            continue
        fs = facility_slug(slug_city, f.get("name") or "", f.get("address"))
        if fs in seen_fac:
            continue
        seen_fac.add(fs)
        urls.append((f"{BASE}/centers/{fs}", "0.55", None))

    SITEMAP_DIR.mkdir(parents=True, exist_ok=True)
    for old in SITEMAP_DIR.glob("sitemap-*.xml"):
        old.unlink()

    chunks = [urls[i : i + MAX_URLS] for i in range(0, max(len(urls), 1), MAX_URLS)]
    sitemap_names = []
    for idx, chunk in enumerate(chunks, start=1):
        name = f"sitemap-{idx:03d}.xml"
        body = '<?xml version="1.0" encoding="UTF-8"?>\n'
        body += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        body += "".join(url_entry(u, p, lm) for u, p, lm in chunk)
        body += "</urlset>\n"
        (SITEMAP_DIR / name).write_text(body)
        sitemap_names.append(name)

    index = '<?xml version="1.0" encoding="UTF-8"?>\n'
    index += '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for name in sitemap_names:
        index += "  <sitemap>\n"
        index += f"    <loc>{BASE}/sitemaps/{name}</loc>\n"
        index += "  </sitemap>\n"
    index += "</sitemapindex>\n"
    (SITE / "sitemap.xml").write_text(index)

    schedule = {
        "policy": "Only verified city-sourced URLs + hard facility detail pages",
        "current_url_count": len(urls),
        "files_written": sitemap_names,
        "covered_city_count": len(covered_cities),
        "facility_page_count": len(seen_fac),
    }
    (ROOT / "data" / "publish_schedule.json").write_text(json.dumps(schedule, indent=2) + "\n")
    print(f"Wrote {len(urls)} URLs across {len(sitemap_names)} sitemap file(s)")


if __name__ == "__main__":
    main()
