#!/usr/bin/env python3
"""Ping IndexNow (Bing/Yandex) for recently published URLs."""

from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://dumpregistry.org"
KEY = os.environ.get("INDEXNOW_KEY", "dumpregistry-indexnow-key-placeholder")


def main() -> None:
    pages = json.loads((ROOT / "data" / "resolved" / "pages.json").read_text())
    urls = [
        f"{BASE}/{p['state_slug']}/{p['city_slug']}/dispose/{p['item_slug']}"
        for p in pages
        if p.get("indexable")
    ][:100]

    key_file = ROOT / "apps" / "web" / "public" / f"{KEY}.txt"
    key_file.write_text(KEY)

    payload = {
        "host": "dumpregistry.org",
        "key": KEY,
        "keyLocation": f"{BASE}/{KEY}.txt",
        "urlList": urls,
    }
    dry = os.environ.get("INDEXNOW_DRY_RUN", "1") == "1"
    if dry:
        print(f"DRY RUN: would ping IndexNow with {len(urls)} URLs")
        print(json.dumps(payload, indent=2)[:500], "...")
        return

    req = urllib.request.Request(
        "https://api.indexnow.org/indexnow",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        print("IndexNow status", resp.status)


if __name__ == "__main__":
    main()
