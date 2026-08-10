#!/usr/bin/env python3
"""Smoke checks for resolved pages, sitemaps, and schema-critical fields."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    pages = json.loads((ROOT / "data" / "resolved" / "pages.json").read_text())
    indexable = [p for p in pages if p["indexable"]]
    assert indexable, "No indexable pages"
    sample = next(p for p in indexable if p["city_slug"] == "los-angeles" and p["item_slug"] == "mattress")
    assert sample["source_url"]
    assert sample["last_verified_at"]
    assert len(sample["faqs"]) >= 3
    assert sample["answer"]
    thin = next(p for p in pages if not p["indexable"])
    assert thin["rule_source_level"] == "default"
    sitemap = ROOT / "apps" / "web" / "public" / "sitemap.xml"
    assert sitemap.exists(), "sitemap.xml missing — run generate_sitemaps.py"
    robots = ROOT / "apps" / "web" / "public" / "robots.txt"
    assert robots.exists(), "robots.txt missing"
    sitemap_body = sitemap.read_text()
    assert "sitemap-001.xml" in sitemap_body
    schedule = json.loads((ROOT / "data" / "publish_schedule.json").read_text())
    assert schedule["current_url_count"] > 0

    base = os.environ.get("SMOKE_BASE_URL")
    if base:
        paths = [
            "/",
            "/california/los-angeles/dispose/mattress",
            "/california/los-angeles/dispose/box-spring",
            "/methodology",
            "/robots.txt",
            "/sitemap.xml",
        ]
        for path in paths:
            url = base.rstrip("/") + path
            with urllib.request.urlopen(url, timeout=20) as resp:
                html = resp.read().decode("utf-8", errors="replace")
                assert resp.status == 200
            if path.endswith("mattress"):
                assert "FAQPage" in html
                assert "HowTo" in html
                assert "Banned from landfills" in html or "Special handling" in html
                assert "noindex" not in html.lower()
            if path.endswith("box-spring"):
                assert "noindex" in html.lower()

    print("SMOKE OK")
    print(f"  pages={len(pages)} indexable={len(indexable)}")
    print(f"  sample={sample['city']} / {sample['item_name']} indexable={sample['indexable']}")
    print(f"  sitemap={sitemap}")
    if base:
        print(f"  http checks against {base}")


if __name__ == "__main__":
    try:
        main()
    except urllib.error.URLError as exc:
        raise SystemExit(f"HTTP smoke failed: {exc}") from exc
