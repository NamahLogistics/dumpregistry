#!/usr/bin/env python3
"""Resolve publishable city×item pages — city-sourced rules only (zero fake local pages)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_merged(preferred: Path, *fallbacks: Path):
    if preferred.exists():
        return load(preferred)
    rows = []
    for path in fallbacks:
        if path.exists():
            rows.extend(load(path))
    return rows


def main() -> None:
    items = {i["slug"]: i for i in load(DATA / "items.json")}
    cities_rows = load_merged(
        DATA / "geo" / "cities.json",
        DATA / "geo" / "ca_cities.json",
    )
    cities = {c["city_slug"]: c for c in cities_rows}
    zips = load_merged(DATA / "geo" / "zips.json", DATA / "geo" / "ca_zips.json")
    rules = load_merged(
        DATA / "rules" / "all.json",
        DATA / "rules" / "ca.json",
        DATA / "rules" / "national.json",
    )
    facilities = load_merged(
        DATA / "facilities" / "all.json",
        DATA / "facilities" / "ca.json",
    )
    aliases = load(DATA / "seo" / "item_aliases.json")
    true_aliases = set(aliases.get("true_aliases") or {})

    fac_by_city: dict[str, list] = {}
    for f in facilities:
        if not f.get("source_url"):
            continue
        if not (f.get("address") or f.get("source_url")):
            continue
        fac_by_city.setdefault(f["city_slug"], []).append(f)

    zip_by_city: dict[str, list] = {}
    for z in zips:
        zip_by_city.setdefault(z["city_slug"], []).append(z)

    pages = []
    for r in rules:
        city_slug = r.get("city_slug")
        if not city_slug:
            continue
        city = cities.get(city_slug)
        item = items.get(r["item_slug"])
        if not city or not item:
            continue
        if not r.get("source_url") or not r.get("source_name") or not r.get("last_verified_at"):
            continue
        if not r.get("answer") or not r.get("steps"):
            continue

        city_facilities = fac_by_city.get(city_slug, [])
        pages.append(
            {
                "state_slug": city["state_slug"],
                "city_slug": city_slug,
                "zip": None,
                "item_slug": item["slug"],
                "city": city["city"],
                "state": city["state"],
                "item_name": item["name"],
                "category": item["category"],
                "is_curbside_allowed": bool(r["is_curbside_allowed"]),
                "nearest_facility_type": r["nearest_facility_type"],
                "common_disposal_fee": r["common_disposal_fee"],
                "badge": r["badge"],
                "hazard_rating": r["hazard_rating"],
                "answer": r["answer"],
                "steps": r.get("steps") or [],
                "faqs": r.get("faqs") or [],
                "rule_source_level": "city",
                "source_url": r["source_url"],
                "source_name": r["source_name"],
                "last_verified_at": r["last_verified_at"],
                "lat": city.get("lat"),
                "lng": city.get("lng"),
                "indexable": item["slug"] not in true_aliases,
                "needs_review": bool(r.get("needs_review")),
                "facilities": city_facilities[:5],
                "nearby_zips": [z["zip"] for z in zip_by_city.get(city_slug, [])[:5]],
            }
        )

    covered_cities = {p["city_slug"] for p in pages}
    cities_with_facilities = {c for c, rows in fac_by_city.items() if rows}

    zip_hubs = []
    for z in zips:
        if z["city_slug"] not in covered_cities or z["city_slug"] not in cities_with_facilities:
            continue
        zip_hubs.append(
            {
                "state_slug": z["state_slug"],
                "city_slug": z["city_slug"],
                "zip": z["zip"],
                "city": z["city"],
                "state": z["state"],
                "lat": z.get("lat"),
                "lng": z.get("lng"),
                "population": z.get("population", 0),
                "indexable": True,
                "facilities": fac_by_city.get(z["city_slug"], [])[:5],
            }
        )

    coverage = {
        "cities_with_guides": sorted(covered_cities),
        "page_count": len(pages),
        "zip_hub_count": len(zip_hubs),
        "items_by_city": {},
        "states": sorted({p["state_slug"] for p in pages}),
    }
    for p in pages:
        coverage["items_by_city"].setdefault(p["city_slug"], []).append(p["item_slug"])

    out_dir = DATA / "resolved"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "pages.json").write_text(json.dumps(pages, indent=2))
    (out_dir / "zip_hubs.json").write_text(json.dumps(zip_hubs, indent=2))
    (out_dir / "coverage.json").write_text(json.dumps(coverage, indent=2))
    print(f"Resolved {len(pages)} city-sourced pages only, {len(zip_hubs)} ZIP hubs")
    print(f"States: {', '.join(coverage['states']) or '(none)'}")
    print(f"Cities: {', '.join(sorted(covered_cities)) or '(none)'}")


if __name__ == "__main__":
    main()
