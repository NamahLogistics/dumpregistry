#!/usr/bin/env python3
"""Bi-annual change-flag stub for top city .gov portal homepages."""

from __future__ import annotations

import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "resolved" / "portal_flags.json"

PORTALS = [
    {"city": "Los Angeles", "url": "https://www.lacitysan.org/"},
    {"city": "San Diego", "url": "https://www.sandiego.gov/environmental-services"},
    {"city": "San Jose", "url": "https://www.sanjoseca.gov/your-government/departments-offices/environmental-services"},
    {"city": "San Francisco", "url": "https://www.sfenvironment.org/"},
    {"city": "Sacramento", "url": "https://www.cityofsacramento.gov/public-works/recycling-solid-waste"},
    {"city": "Oakland", "url": "https://www.oaklandca.gov/topics/recycling-and-waste"},
    # Extend toward top 100 over time
]

PATTERNS = [
    re.compile(r"new fee", re.I),
    re.compile(r"fee structural update", re.I),
    re.compile(r"electronics ban", re.I),
    re.compile(r"banned from", re.I),
    re.compile(r"rate change", re.I),
    re.compile(r"organics", re.I),
]


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "DumpRegistryFreshnessBot/0.1"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        return resp.read().decode("utf-8", errors="replace")


def main() -> None:
    dry = True  # default safe: do not hammer portals unless explicitly enabled
    import os

    dry = os.environ.get("SCRAPE_LIVE", "0") != "1"
    results = []
    for portal in PORTALS:
        entry = {
            "city": portal["city"],
            "url": portal["url"],
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "matched_patterns": [],
            "needs_review": False,
            "error": None,
        }
        if dry:
            entry["matched_patterns"] = ["(dry-run stub — set SCRAPE_LIVE=1 to fetch)"]
            results.append(entry)
            continue
        try:
            html = fetch(portal["url"])
            matched = [p.pattern for p in PATTERNS if p.search(html)]
            entry["matched_patterns"] = matched
            entry["needs_review"] = bool(matched)
        except Exception as exc:  # noqa: BLE001
            entry["error"] = str(exc)
        results.append(entry)

    # Flag pages in resolved dataset when city matches
    pages_path = ROOT / "data" / "resolved" / "pages.json"
    if pages_path.exists() and not dry:
        pages = json.loads(pages_path.read_text())
        flagged_cities = {r["city"] for r in results if r.get("needs_review")}
        for p in pages:
            if p.get("city") in flagged_cities:
                p["needs_review"] = True
        pages_path.write_text(json.dumps(pages, indent=2))

    OUT.write_text(json.dumps(results, indent=2))
    print(f"Wrote {OUT} ({len(results)} portals; dry={dry})")


if __name__ == "__main__":
    main()
