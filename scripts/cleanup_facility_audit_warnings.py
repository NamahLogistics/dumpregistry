#!/usr/bin/env python3
"""Cleanup facility audit warnings: far hub tags + fixable coord bugs.

Actions:
  1) Fix known bad lat/lng that falsely trip distance_far.
  2) Retag clear wrong-hub rows onto a better city in cities.json when possible.
  3) Purge remaining facilities > max_distance_warn from their hub centroid.

Does not touch soft/hard classification. Re-run audit_facilities.py after.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.audit_facilities import haversine_mi  # noqa: E402

FAC_PATH = ROOT / "data" / "facilities" / "all.json"
CITIES_PATH = ROOT / "data" / "geo" / "cities.json"
MAX_DISTANCE_WARN = 100.0

# (city_slug, name) -> (lat, lng)
COORD_FIXES: dict[tuple[str, str], tuple[float, float]] = {
    (
        "minneapolis",
        "Minneapolis South Transfer Station",
    ): (44.95106, -93.24375),
    (
        "sacramento",
        "L&D Landfill — Public Disposal",
    ): (38.5272, -121.4145),
}

# (city_slug, name_substring or exact name) -> new city_slug
# Applied before distance purge; exact name match preferred.
RETAG_EXACT: dict[tuple[str, str], str] = {
    ("fresno", "Kern County Bena Landfill (Fresno hub)"): "bakersfield",
    ("fresno", "Kern County Mount Vernon Landfill (Fresno hub)"): "bakersfield",
}


def main() -> None:
    cities = {c["city_slug"]: c for c in json.loads(CITIES_PATH.read_text())}
    rows = json.loads(FAC_PATH.read_text())
    kept: list[dict] = []
    fixed_coords = 0
    retagged = 0
    purged: list[str] = []

    for r in rows:
        slug = r.get("city_slug") or ""
        name = r.get("name") or ""
        key = (slug, name)

        if key in COORD_FIXES:
            lat, lng = COORD_FIXES[key]
            r["lat"], r["lng"] = lat, lng
            fixed_coords += 1

        if key in RETAG_EXACT:
            new_slug = RETAG_EXACT[key]
            if new_slug in cities:
                r["city_slug"] = new_slug
                # Drop "(Fresno hub)" style suffixes after retag.
                if name.endswith("(Fresno hub)"):
                    r["name"] = name.replace(" (Fresno hub)", "").strip()
                slug = new_slug
                name = r["name"]
                retagged += 1

        city = cities.get(slug)
        if not city:
            purged.append(f"unknown_city:{slug}:{name}")
            continue

        lat, lng = r.get("lat"), r.get("lng")
        miles = None
        if lat is not None and lng is not None:
            try:
                miles = haversine_mi(
                    float(city["lat"]),
                    float(city["lng"]),
                    float(lat),
                    float(lng),
                )
            except (TypeError, ValueError):
                miles = None

        if miles is not None and miles > MAX_DISTANCE_WARN:
            purged.append(f"distance_far:{miles:.0f}mi:{slug}:{name}")
            continue

        kept.append(r)

    FAC_PATH.write_text(json.dumps(kept, indent=2, ensure_ascii=False) + "\n")
    print(f"kept {len(kept)} (was {len(rows)})")
    print(f"fixed_coords {fixed_coords}")
    print(f"retagged {retagged}")
    print(f"purged {len(purged)}")
    for line in purged[:40]:
        print(f"  - {line}")
    if len(purged) > 40:
        print(f"  … {len(purged) - 40} more")


if __name__ == "__main__":
    main()
