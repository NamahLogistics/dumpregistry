#!/usr/bin/env python3
"""Validate rule JSON and print coverage stats."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    rules = json.loads((ROOT / "data" / "rules" / "ca.json").read_text())
    items = {i["slug"] for i in json.loads((ROOT / "data" / "items.json").read_text())}
    required = ["item_slug", "state", "source_url", "source_name", "last_verified_at", "answer"]
    errors = []
    for i, r in enumerate(rules):
        for key in required:
            if not r.get(key):
                errors.append(f"rule[{i}] missing {key}")
        if r["item_slug"] not in items:
            errors.append(f"rule[{i}] unknown item {r['item_slug']}")
    state_count = sum(1 for r in rules if not r.get("city_slug"))
    city_count = sum(1 for r in rules if r.get("city_slug"))
    print(f"Rules OK: {len(rules)} (state={state_count}, city={city_count})")
    if errors:
        print("ERRORS:")
        for e in errors:
            print(" -", e)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
