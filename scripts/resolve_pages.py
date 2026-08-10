#!/usr/bin/env python3
"""Resolve city×item pages with rule inheritance and indexability gates."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    items = load(DATA / "items.json")
    cities = load(DATA / "geo" / "ca_cities.json")
    zips = load(DATA / "geo" / "ca_zips.json")
    rules = load(DATA / "rules" / "ca.json")
    facilities = load(DATA / "facilities" / "ca.json")

    items_by_slug = {i["slug"]: i for i in items}
    state_rules = {}
    city_rules = {}
    for r in rules:
        key = r["item_slug"]
        if r.get("city_slug"):
            city_rules[(r["city_slug"], key)] = r
        else:
            state_rules[key] = r

    fac_by_city = {}
    for f in facilities:
        fac_by_city.setdefault(f["city_slug"], []).append(f)

    zip_by_city = {}
    for z in zips:
        zip_by_city.setdefault(z["city_slug"], []).append(z)

    pages = []
    for city in cities:
        for item in items:
            state_rule = state_rules.get(item["slug"])
            city_rule = city_rules.get((city["city_slug"], item["slug"]))
            # Index ONLY city-sourced rules. State/default can power the wizard but must not rank as local pages.
            if city_rule:
                rule = city_rule
                source_level = "city"
                badge = rule["badge"]
                hazard = rule["hazard_rating"]
                curbside = bool(rule["is_curbside_allowed"])
                fee = rule["common_disposal_fee"]
                facility = rule["nearest_facility_type"]
                answer = rule["answer"]
                steps = rule.get("steps") or []
                faqs = rule.get("faqs") or []
                source_url = rule.get("source_url")
                source_name = rule.get("source_name")
                last_verified = rule.get("last_verified_at")
                needs_review = bool(rule.get("needs_review"))
                indexable = True
            elif state_rule:
                rule = state_rule
                source_level = "state"
                badge = rule["badge"]
                hazard = rule["hazard_rating"]
                curbside = bool(rule["is_curbside_allowed"])
                fee = rule["common_disposal_fee"]
                facility = rule["nearest_facility_type"]
                answer = (
                    f"{rule['answer']} Note: this is statewide guidance only — we do not yet have a "
                    f"verified {city['city']}-specific program source for this item."
                )
                steps = rule.get("steps") or []
                faqs = rule.get("faqs") or []
                source_url = rule.get("source_url")
                source_name = rule.get("source_name")
                last_verified = rule.get("last_verified_at")
                needs_review = True
                indexable = False
            else:
                badge = item["badge_default"]
                hazard = item["hazard_default"]
                curbside = bool(item["curbside_default"])
                fee = item["fee_band_default"]
                facility = item["facility_type_default"]
                answer = (
                    f"{item['summary_default']} We do not yet have a verified "
                    f"{city['city']}, {city['state']} source for this item — treat this as general guidance."
                )
                steps = [
                    "Check your city sanitation or hauler website for this item.",
                    "If hazardous, use a household hazardous waste program.",
                    "Suggest a correction on this page if you find an official update.",
                ]
                faqs = [
                    {
                        "q": f"Is this official for {city['city']}?",
                        "a": "Not yet verified locally. Use the correction form with a .gov source.",
                    },
                    {
                        "q": "Can I put it in my regular cart?",
                        "a": "Follow the badge and summary; when unsure, assume special handling.",
                    },
                    {
                        "q": "Where should I go?",
                        "a": f"Start with a {facility.lower()} near {city['city']}.",
                    },
                ]
                source_url = None
                source_name = None
                last_verified = None
                needs_review = True
                indexable = False

            city_facilities = fac_by_city.get(city["city_slug"], [])
            # ZIP pages only when we have coordinates (facility distance usefulness)
            pages.append(
                {
                    "state_slug": city["state_slug"],
                    "city_slug": city["city_slug"],
                    "zip": None,
                    "item_slug": item["slug"],
                    "city": city["city"],
                    "state": city["state"],
                    "item_name": item["name"],
                    "category": item["category"],
                    "is_curbside_allowed": curbside,
                    "nearest_facility_type": facility,
                    "common_disposal_fee": fee,
                    "badge": badge,
                    "hazard_rating": hazard,
                    "answer": answer,
                    "steps": steps,
                    "faqs": faqs,
                    "rule_source_level": source_level,
                    "source_url": source_url,
                    "source_name": source_name,
                    "last_verified_at": last_verified,
                    "lat": city.get("lat"),
                    "lng": city.get("lng"),
                    "indexable": indexable,
                    "needs_review": needs_review,
                    "facilities": city_facilities[:3],
                    "nearby_zips": [z["zip"] for z in zip_by_city.get(city["city_slug"], [])[:5]],
                }
            )

    # ZIP hubs only indexable when the city has real facility rows (not empty placeholders)
    cities_with_facilities = {c for c, rows in fac_by_city.items() if rows}
    zip_hubs = []
    for z in zips:
        has_facilities = z["city_slug"] in cities_with_facilities
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
                "indexable": has_facilities,
                "facilities": fac_by_city.get(z["city_slug"], [])[:5],
            }
        )

    out_dir = DATA / "resolved"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "pages.json").write_text(json.dumps(pages, indent=2))
    (out_dir / "zip_hubs.json").write_text(json.dumps(zip_hubs, indent=2))
    indexable = sum(1 for p in pages if p["indexable"])
    print(f"Resolved {len(pages)} city×item pages ({indexable} indexable), {len(zip_hubs)} ZIP hubs")
    print(f"Wrote {out_dir / 'pages.json'}")


if __name__ == "__main__":
    main()
