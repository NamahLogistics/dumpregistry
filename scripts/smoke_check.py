#!/usr/bin/env python3
"""Smoke checks for zero-fake city-sourced publish set."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    pages = json.loads((ROOT / "data" / "resolved" / "pages.json").read_text())
    assert pages, "No pages"
    assert all(p["rule_source_level"] == "city" for p in pages)
    assert all(p.get("source_url") and p.get("last_verified_at") for p in pages)
    indexable = [p for p in pages if p.get("indexable")]
    noindex = [p for p in pages if not p.get("indexable")]
    assert indexable, "No indexable pages"
    assert noindex, "True-alias noindex set is empty"
    sofa = next(p for p in pages if p["city_slug"] == "houston" and p["item_slug"] == "sofa")
    assert sofa["indexable"] is False
    mattress = next(p for p in pages if p["city_slug"] == "houston" and p["item_slug"] == "mattress")
    assert mattress["indexable"] is True
    helium = next(p for p in pages if p["city_slug"] == "houston" and p["item_slug"] == "helium-tank")
    assert helium["indexable"] is True, "false aliases stay indexable until rewritten"
    assert not any("statewide guidance only" in (p.get("answer") or "").lower() for p in pages)

    sample = next(p for p in pages if p["city_slug"] == "los-angeles" and p["item_slug"] == "mattress")
    assert "LASAN" in sample["answer"] or "MyLA311" in sample["answer"]

    sitemap = ROOT / "apps" / "web" / "public" / "sitemap.xml"
    robots = ROOT / "apps" / "web" / "public" / "robots.txt"
    assert sitemap.exists() and robots.exists()
    chunk = (ROOT / "apps" / "web" / "public" / "sitemaps" / "sitemap-001.xml").read_text()
    assert "/texas/houston/dispose/mattress" in chunk
    assert "/texas/houston/dispose/sofa" not in chunk
    assert "/texas/houston/dispose/helium-tank" in chunk

    base = os.environ.get("SMOKE_BASE_URL")
    if base:
        for path in [
            "/",
            "/california/los-angeles/dispose/mattress",
            "/california",
            "/sitemap.xml",
        ]:
            with urllib.request.urlopen(base.rstrip("/") + path, timeout=20) as resp:
                assert resp.status == 200
                body = resp.read().decode("utf-8", errors="replace")
            if path.endswith("mattress"):
                assert "FAQPage" in body
                assert "noindex" not in body.lower()
        # Covered city guide must be indexable
        with urllib.request.urlopen(
            base.rstrip("/") + "/california/san-jose/dispose/mattress", timeout=20
        ) as resp:
            assert resp.status == 200
            sj = resp.read().decode("utf-8", errors="replace")
            assert "noindex" not in sj.lower()
            assert "statewide guidance" not in sj.lower()

        # Unknown item slug must 404
        try:
            urllib.request.urlopen(
                base.rstrip("/") + "/california/los-angeles/dispose/not-a-real-item", timeout=20
            )
            raise AssertionError("expected 404 for unknown dispose page")
        except urllib.error.HTTPError as exc:
            assert exc.code == 404

    cities = {p["city_slug"] for p in pages}
    states = {p["state_slug"] for p in pages}
    assert "california" in states
    if "houston" in cities:
        assert any(p["city_slug"] == "houston" and p["item_slug"] == "mattress" for p in pages)

    print("SMOKE OK")
    print(
        f"  pages={len(pages)} indexable={len(indexable)} noindex={len(noindex)} "
        f"cities={len(cities)} states={sorted(states)}"
    )


if __name__ == "__main__":
    try:
        main()
    except urllib.error.URLError as exc:
        raise SystemExit(f"HTTP smoke failed: {exc}") from exc
