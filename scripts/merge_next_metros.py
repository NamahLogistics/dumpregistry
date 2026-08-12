#!/usr/bin/env python3
"""Merge top-N entries from data/geo/next_metros.json into cities.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CITIES = ROOT / "data" / "geo" / "cities.json"
NEXT = ROOT / "data" / "geo" / "next_metros.json"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=25)
    args = ap.parse_args()

    cities = json.loads(CITIES.read_text())
    existing = {(c["city_slug"], c["state_slug"]) for c in cities}
    slug_taken = {c["city_slug"] for c in cities}
    nxt = json.loads(NEXT.read_text())
    nxt = sorted(nxt, key=lambda r: (r.get("priority", 99), -(r.get("population") or 0)))

    added = []
    for row in nxt:
        key = (row["city_slug"], row["state_slug"])
        if key in existing:
            continue
        slug = row["city_slug"]
        # city_slug must be globally unique (resolve/audit key by slug alone).
        if slug in slug_taken:
            slug = f"{slug}-{row['state_slug'].split('-')[0][:2]}"
            if slug in slug_taken:
                slug = f"{row['city_slug']}-{row['state_slug']}"
            print(f"slug collision avoided: {row['city_slug']} -> {slug}")
        cities.append(
            {
                "city": row["city"],
                "city_slug": slug,
                "state": row["state"],
                "state_slug": row["state_slug"],
                "lat": row["lat"],
                "lng": row["lng"],
                "population": row["population"],
            }
        )
        existing.add(key)
        slug_taken.add(slug)
        added.append(f"{row['city']}, {row['state']} ({slug})")
        if len(added) >= args.top:
            break

    cities.sort(key=lambda c: (-(c.get("population") or 0), c["city"]))
    CITIES.write_text(json.dumps(cities, indent=2) + "\n")
    print(f"cities.json now {len(cities)} (+{len(added)})")
    for a in added:
        print(f"  + {a}")


if __name__ == "__main__":
    main()
