#!/usr/bin/env python3
"""Generate sitemap index + up to 40 sitemap files (≤50k URLs each)."""

from __future__ import annotations

import json
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SITE = (ROOT / "apps" / "web" / "public").resolve()
SITEMAP_DIR = SITE / "sitemaps"
BASE = "https://dumpregistry.org"
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
    cities = json.loads((ROOT / "data" / "geo" / "ca_cities.json").read_text())

    urls: list[tuple[str, str]] = [
        (f"{BASE}/", "1.0"),
        (f"{BASE}/about", "0.5"),
        (f"{BASE}/methodology", "0.5"),
        (f"{BASE}/sources", "0.5"),
        (f"{BASE}/california", "0.8"),
    ]
    for c in cities:
        urls.append((f"{BASE}/{c['state_slug']}/{c['city_slug']}", "0.7"))
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
    # Reserve naming through 040 even if empty placeholders are not written
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
        "month_1": {"sitemaps": ["sitemap-001.xml"], "region": "California verified pages"},
        "month_2": {"sitemaps": ["sitemap-002.xml", "sitemap-003.xml", "sitemap-004.xml"], "region": "TX, NY, FL (when verified)"},
        "month_3": {"sitemaps": [f"sitemap-{i:03d}.xml" for i in range(5, 11)], "region": "Midwest (when verified)"},
        "month_4_6": {"sitemaps": [f"sitemap-{i:03d}.xml" for i in range(11, 41)], "region": "Nationwide expansion"},
        "note": "Only submit sitemaps that contain verified/indexable URLs. Empty reserved names are not generated until needed.",
        "current_url_count": len(urls),
        "files_written": sitemap_names,
    }
    (ROOT / "data" / "publish_schedule.json").write_text(json.dumps(schedule, indent=2))
    print(f"Wrote {len(sitemap_names)} sitemap file(s), {len(urls)} URLs total")


if __name__ == "__main__":
    main()
