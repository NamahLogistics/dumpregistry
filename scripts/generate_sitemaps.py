#!/usr/bin/env python3
"""Generate sitemap index — verified city-sourced URLs only."""

from __future__ import annotations

import json
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SITE = (ROOT / "apps" / "web" / "public").resolve()
SITEMAP_DIR = SITE / "sitemaps"
BASE = "https://www.dumpregistry.org"
MAX_URLS = 50_000


def url_entry(loc: str, priority: str = "0.6") -> str:
    return (
        "  <url>\n"
        f"    <loc>{escape(loc)}</loc>\n"
        f"    <changefreq>monthly</changefreq>\n"
        f"    <priority>{priority}</priority>\n"
        "  </url>\n"
    )


def main() -> None:
    pages = json.loads((ROOT / "data" / "resolved" / "pages.json").read_text())
    zip_hubs = json.loads((ROOT / "data" / "resolved" / "zip_hubs.json").read_text())
    covered_cities = sorted({(p["state_slug"], p["city_slug"]) for p in pages if p.get("indexable")})

    states = sorted({s for s, _ in covered_cities})
    items = json.loads((ROOT / "data" / "items.json").read_text())
    guides_dir = ROOT / "content" / "guides"
    guide_slugs = sorted(p.stem for p in guides_dir.glob("*.md")) if guides_dir.exists() else []

    urls: list[tuple[str, str]] = [
        (f"{BASE}/", "1.0"),
        (f"{BASE}/about", "0.5"),
        (f"{BASE}/methodology", "0.5"),
        (f"{BASE}/sources", "0.5"),
        (f"{BASE}/partners", "0.6"),
        (f"{BASE}/cities", "0.8"),
        (f"{BASE}/materials", "0.85"),
        (f"{BASE}/centers", "0.85"),
        (f"{BASE}/guides", "0.8"),
    ]
    for item in items:
        slug = item.get("slug")
        if slug:
            urls.append((f"{BASE}/materials/{slug}", "0.7"))
    for slug in guide_slugs:
        urls.append((f"{BASE}/guides/{slug}", "0.65"))
    for state_slug in states:
        urls.append((f"{BASE}/{state_slug}", "0.75"))
    for state_slug, city_slug in covered_cities:
        urls.append((f"{BASE}/{state_slug}/{city_slug}", "0.7"))
    for z in zip_hubs:
        if z.get("indexable"):
            urls.append((f"{BASE}/{z['state_slug']}/{z['city_slug']}/{z['zip']}", "0.55"))
    for p in pages:
        if not p.get("indexable"):
            continue
        urls.append(
            (
                f"{BASE}/{p['state_slug']}/{p['city_slug']}/dispose/{p['item_slug']}",
                "0.8",
            )
        )

    SITEMAP_DIR.mkdir(parents=True, exist_ok=True)
    for old in SITEMAP_DIR.glob("sitemap-*.xml"):
        old.unlink()

    chunks = [urls[i : i + MAX_URLS] for i in range(0, max(len(urls), 1), MAX_URLS)]
    sitemap_names = []
    for idx, chunk in enumerate(chunks, start=1):
        name = f"sitemap-{idx:03d}.xml"
        body = '<?xml version="1.0" encoding="UTF-8"?>\n'
        body += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        body += "".join(url_entry(u, p) for u, p in chunk)
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
        "policy": "Only verified city-sourced URLs",
        "current_url_count": len(urls),
        "files_written": sitemap_names,
        "covered_city_count": len(covered_cities),
    }
    (ROOT / "data" / "publish_schedule.json").write_text(json.dumps(schedule, indent=2))
    print(f"Wrote {len(sitemap_names)} sitemap file(s), {len(urls)} URLs total")


if __name__ == "__main__":
    main()
