#!/usr/bin/env python3
"""Ping IndexNow (Bing/Yandex) for recently published URLs."""

from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.dumpregistry.org"
# Stable default key (also written under apps/web/public/<key>.txt).
# Override with INDEXNOW_KEY in production if rotated.
DEFAULT_KEY = "13b10182db1fb5e834bd89f1fb2041da"
KEY = os.environ.get("INDEXNOW_KEY", DEFAULT_KEY)


def collect_urls(limit: int = 10_000) -> list[str]:
    pages = json.loads((ROOT / "data" / "resolved" / "pages.json").read_text())
    urls = [
        f"{BASE}/{p['state_slug']}/{p['city_slug']}/dispose/{p['item_slug']}"
        for p in pages
        if p.get("indexable")
    ]
    # Prefer newest verified first when timestamps exist
    pages_sorted = sorted(
        [p for p in pages if p.get("indexable")],
        key=lambda p: p.get("last_verified_at") or "",
        reverse=True,
    )
    urls = [
        f"{BASE}/{p['state_slug']}/{p['city_slug']}/dispose/{p['item_slug']}"
        for p in pages_sorted
    ]
    # Materials + guides + centers hub
    urls.append(f"{BASE}/materials")
    urls.append(f"{BASE}/centers")
    urls.append(f"{BASE}/guides")
    guides = ROOT / "content" / "guides"
    if guides.exists():
        for p in sorted(guides.glob("*.md")):
            urls.append(f"{BASE}/guides/{p.stem}")
    # Dedupe preserve order
    seen: set[str] = set()
    out: list[str] = []
    for u in urls:
        if u in seen:
            continue
        seen.add(u)
        out.append(u)
        if len(out) >= limit:
            break
    return out


def main() -> None:
    urls = collect_urls()
    key_file = ROOT / "apps" / "web" / "public" / f"{KEY}.txt"
    key_file.write_text(KEY + "\n")

    # IndexNow accepts max 10k URLs per request; batch 100 for reliability
    batch_size = 100
    dry = os.environ.get("INDEXNOW_DRY_RUN", "1") == "1"

    if dry:
        print(f"DRY RUN: would ping IndexNow with {len(urls)} URLs (key={KEY})")
        print("Set INDEXNOW_DRY_RUN=0 to send.")
        return

    for i in range(0, len(urls), batch_size):
        batch = urls[i : i + batch_size]
        payload = {
            "host": "www.dumpregistry.org",
            "key": KEY,
            "keyLocation": f"{BASE}/{KEY}.txt",
            "urlList": batch,
        }
        req = urllib.request.Request(
            "https://api.indexnow.org/indexnow",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"IndexNow batch {i // batch_size + 1}: status {resp.status} ({len(batch)} URLs)")


if __name__ == "__main__":
    main()
