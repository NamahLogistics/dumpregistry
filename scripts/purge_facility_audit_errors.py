#!/usr/bin/env python3
"""Purge/fix clear facility audit errors so CI gate can enforce.

Actions:
  1) Drop rows > max_distance_error from metro centroid (wrong hub tags).
  2) Drop CA facilities mistagged onto glendale AZ / richmond VA.
  3) Drop Prince George's MD rows mistagged onto jersey-city.
  4) Sync facility.state from address state token when in border allowlist.

Does not delete hard rows that pass distance + state checks.
"""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.audit_facilities import (  # noqa: E402
    BORDER_OK,
    address_state,
    haversine_mi,
)
from scripts.facility_quality import is_hard_facility  # noqa: E402

FAC_PATH = ROOT / "data" / "facilities" / "all.json"
CITIES_PATH = ROOT / "data" / "geo" / "cities.json"
MAX_DISTANCE_ERROR = 250.0


def main() -> None:
    cities = {c["city_slug"]: c for c in json.loads(CITIES_PATH.read_text())}
    rows = json.loads(FAC_PATH.read_text())
    kept: list[dict] = []
    purged: list[str] = []
    synced = 0

    for r in rows:
        slug = r.get("city_slug") or ""
        name = r.get("name") or ""
        city = cities.get(slug)
        if not city:
            purged.append(f"unknown_city:{slug}:{name}")
            continue

        lat, lng = r.get("lat"), r.get("lng")
        miles = None
        if lat is not None and lng is not None:
            try:
                miles = haversine_mi(float(city["lat"]), float(city["lng"]), float(lat), float(lng))
            except (TypeError, ValueError):
                miles = None

        # Extreme distance = wrong metro tag
        if miles is not None and miles > MAX_DISTANCE_ERROR:
            purged.append(f"distance_extreme:{miles:.0f}mi:{slug}:{name}")
            continue

        # Explicit cross-coast / wrong-city patterns
        state = (r.get("state") or "").upper()
        addr_st = address_state(r.get("address") or "")
        if slug == "glendale" and state == "CA":
            purged.append(f"glendale_az_ca:{name}")
            continue
        if slug == "richmond" and state == "CA":
            purged.append(f"richmond_va_ca:{name}")
            continue
        if slug == "jersey-city" and ("Prince George" in name or addr_st == "MD"):
            purged.append(f"jersey_city_md:{name}")
            continue

        # Sync state from address when border-allowed
        border = BORDER_OK.get(slug, frozenset())
        if addr_st and addr_st in border and city["state"] in border and state != addr_st:
            r["state"] = addr_st
            synced += 1

        if not is_hard_facility(r):
            purged.append(f"soft:{slug}:{name}")
            continue

        kept.append(r)

    FAC_PATH.write_text(json.dumps(kept, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({
        "before": len(rows),
        "after": len(kept),
        "purged": len(purged),
        "state_synced": synced,
        "purge_samples": purged[:40],
    }, indent=2))


if __name__ == "__main__":
    main()
