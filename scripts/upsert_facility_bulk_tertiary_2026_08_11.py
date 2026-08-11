#!/usr/bin/env python3
"""Tertiary .gov drop-offs for 15 metros — one new verified site per city (2026-08-11).

Skips when no third distinct permanent .gov drop-off exists beyond EXISTING pairs.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAC_PATH = ROOT / "data" / "facilities" / "all.json"
ITEMS = {i["slug"] for i in json.loads((ROOT / "data" / "items.json").read_text())}

SKIPS = [
    {
        "city_slug": "oakland",
        "reason": "City pages only list Alameda HHW (2100 E 7th) and Davis Street transfer — no third distinct permanent .gov drop-off.",
    },
    {
        "city_slug": "tulsa",
        "reason": "Only permanent drop-offs are HPCF and Mulch Site; bulky is curbside-scheduled, not a facility.",
    },
]

FACILITIES: list[dict] = [
    {
        "name": "Recycling Drop Off Center — Pleasant Valley Park (North)",
        "facility_type": "Community recycling drop-off center",
        "city_slug": "kansas-city",
        "state": "MO",
        "zip": "64119",
        "address": "5601 NE Pleasant Valley Road, Kansas City, MO 64119",
        "lat": 39.1472,
        "lng": -94.5341,
        "source_url": "https://www.kcmo.gov/city-hall/trash/recycling",
        "hours": "Wed–Sat 9:00–17:00; closed Sun–Tue and listed holidays",
        "phone": "816-561-1087",
        "accepted_materials": [
            "cardboard",
            "glass-bottles",
        ],
    },
    {
        "name": "Hartsfield Yard Debris Processing Facility",
        "facility_type": "Yard trimmings drop-off",
        "city_slug": "atlanta",
        "state": "GA",
        "zip": "30318",
        "address": "2175 James Jackson Parkway NW, Atlanta, GA 30318",
        "lat": 33.664,
        "lng": -84.459,
        "source_url": "https://www.atlantaga.gov/Home/Components/News/News/13793/1338",
        "hours": "Mon–Fri 7:30–16:30; Atlanta residents only — valid ID required",
        "phone": "404-330-6240",
        "accepted_materials": ["yard-waste"],
    },
    {
        "name": "Oma-Gro Production Facility — yard waste drop-off",
        "facility_type": "Yard waste / compost feedstock drop-off",
        "city_slug": "omaha",
        "state": "NE",
        "zip": "68117",
        "address": "6502 S 60th Street, Omaha, NE 68117",
        "lat": 41.195,
        "lng": -96.007,
        "source_url": "https://www.wasteline.org/yard-waste-information/",
        "hours": "Weekdays 7:00–15:00 winter / 7:00–18:00 summer; closed City of Omaha holidays; yard receiving closes seasonally — check wasteline",
        "phone": "",
        "accepted_materials": ["yard-waste"],
    },
    {
        "name": "Black Forest Slash & Mulch Site",
        "facility_type": "County slash / yard debris drop-off (seasonal)",
        "city_slug": "colorado-springs",
        "state": "CO",
        "zip": "80908",
        "address": "Shoup Road & Herring Road, Colorado Springs, CO 80908",
        "lat": 39.012,
        "lng": -104.682,
        "source_url": "https://communityresources.elpasoco.com/environmental-division/black-forest-slash-mulch/",
        "hours": "Seasonal May–Sep — check elpasoco.com; $10/load; El Paso/Teller County ID required",
        "phone": "719-520-7878",
        "accepted_materials": ["yard-waste"],
    },
    {
        "name": "Conservation Corps of Long Beach — tire & e-waste events",
        "facility_type": "City-partnered tire / e-waste collection site",
        "city_slug": "long-beach",
        "state": "CA",
        "zip": "90814",
        "address": "340 Nieto Avenue, Long Beach, CA 90814",
        "lat": 33.767,
        "lng": -118.134,
        "source_url": "https://longbeach.gov/globalassets/long-beach-recycles/media-library/documents/hhw/esb_flyertemplate_hhw",
        "hours": "2nd & 4th Sat 10:00–14:00 (no 4th Sat Nov–Dec)",
        "phone": "(562) 570-2876",
        "accepted_materials": [
            "tires",
            "television",
            "computer-monitor",
            "laptop",
            "desktop-computer",
            "printer",
            "tablet",
            "smartphone",
            "microwave",
            "e-waste-mixed",
        ],
    },
    {
        "name": "West Neck Recycling Center",
        "facility_type": "Neighborhood recycling drop-off",
        "city_slug": "virginia-beach",
        "state": "VA",
        "zip": "23452",
        "address": "2500 West Neck Road, Virginia Beach, VA 23452",
        "lat": 36.867,
        "lng": -76.13,
        "source_url": "https://pw.virginiabeach.gov/trash-recycling/recycling-information",
        "hours": "Mon–Sat 7:00–16:30; trailers not permitted",
        "phone": "757-385-4650",
        "accepted_materials": [
            "cardboard",
            "glass-bottles",
        ],
    },
    {
        "name": "Bakersfield Metropolitan (Bena) Sanitary Landfill",
        "facility_type": "County landfill / residential drop-off",
        "city_slug": "bakersfield",
        "state": "CA",
        "zip": "93307",
        "address": "2951 Neumarkel Road, Bakersfield, CA 93307",
        "lat": 35.393,
        "lng": -118.682,
        "source_url": "https://www.kernpublicworks.com/Home/Components/FacilityDirectory/FacilityDirectory/242/36513",
        "hours": "Daily 8:00–16:00; closed New Year's, Easter, 4th of July, Thanksgiving, Christmas",
        "phone": "(661) 862-8900",
        "accepted_materials": [
            "mattress",
            "box-spring",
            "sofa",
            "recliner",
            "carpet",
            "yard-waste",
            "tires",
            "television",
            "computer-monitor",
            "laptop",
            "desktop-computer",
            "printer",
            "tablet",
            "smartphone",
            "microwave",
            "e-waste-mixed",
            "refrigerator",
            "washer",
            "dryer",
            "stove",
            "construction-debris",
            "paint-latex",
            "paint-oil",
            "motor-oil",
        ],
    },
    {
        "name": "Waste Disposal Transfer Station",
        "facility_type": "Transfer station / self-haul drop-off",
        "city_slug": "wichita",
        "state": "KS",
        "zip": "67217",
        "address": "5550 W 55th Street South, Wichita, KS 67217",
        "lat": 37.655,
        "lng": -97.424,
        "source_url": "https://www.wichita.gov/Archive.aspx?ADID=1680",
        "hours": "Call 316-522-3633 to confirm hours and fees",
        "phone": "316-522-3633",
        "accepted_materials": [
            "mattress",
            "box-spring",
            "sofa",
            "recliner",
            "carpet",
            "yard-waste",
            "construction-debris",
        ],
    },
    {
        "name": "Northeast Branch Library — recycling drop-off",
        "facility_type": "Public library recycling drop-off",
        "city_slug": "arlington",
        "state": "TX",
        "zip": "76011",
        "address": "1905 E Brown Boulevard, Arlington, TX 76011",
        "lat": 32.774,
        "lng": -97.081,
        "source_url": "https://www.arlingtontx.gov/city_hall/departments/garbage_recycling/recycling_information/drop_off_locations",
        "hours": "During library open hours — confirm on arlingtontx.gov",
        "phone": "817-317-2000",
        "accepted_materials": [
            "cardboard",
            "glass-bottles",
        ],
    },
    {
        "name": "Pedal Point LifeCycle Solutions — city e-cycle events",
        "facility_type": "Electronics recycling drop-off (city event pricing)",
        "city_slug": "aurora",
        "state": "CO",
        "zip": "80011",
        "address": "3251 Lewiston Street, Suite 10, Aurora, CO 80011",
        "lat": 39.754,
        "lng": -104.806,
        "source_url": "https://www.auroragov.org/residents/trash___recycling/recycling_opportunities/electronics_recycling",
        "hours": "City e-cycle event weeks Mon–Fri 8:00–16:30; last residential drop-off program ends July 2026 — check auroragov.org",
        "phone": "303-482-2207",
        "accepted_materials": [
            "television",
            "computer-monitor",
            "laptop",
            "desktop-computer",
            "printer",
            "tablet",
            "smartphone",
            "microwave",
            "hard-drive",
            "e-waste-mixed",
        ],
    },
    {
        "name": "RiverBirch Landfill",
        "facility_type": "C&D / vegetative debris landfill (fee)",
        "city_slug": "new-orleans",
        "state": "LA",
        "zip": "70094",
        "address": "2000 S Kenner Avenue, Avondale, LA 70094",
        "lat": 29.908,
        "lng": -90.203,
        "source_url": "https://nola.gov/trash/",
        "hours": "Mon–Fri 7:00–17:00; Sat 7:00–12:00 — confirm with operator",
        "phone": "(504) 436-1288",
        "accepted_materials": [
            "construction-debris",
            "lumber",
            "drywall",
            "concrete",
            "asphalt-shingles",
            "yard-waste",
        ],
    },
    {
        "name": "Waimānalo Convenience Center",
        "facility_type": "City convenience center — bulky / green waste / select special waste",
        "city_slug": "honolulu",
        "state": "HI",
        "zip": "96795",
        "address": "41-241 Hihimanu Street, Waimanalo, HI 96795",
        "lat": 21.334,
        "lng": -157.718,
        "source_url": "https://www.honolulu.gov/env/ref/waste-drop-off-locations/",
        "hours": "Daily 7:00–18:00",
        "phone": "(808) 259-7182",
        "accepted_materials": [
            "mattress",
            "box-spring",
            "sofa",
            "recliner",
            "desk",
            "dining-table",
            "bookshelf",
            "carpet",
            "yard-waste",
            "car-battery",
            "household-batteries",
            "propane-tank",
            "tires",
            "construction-debris",
        ],
    },
    {
        "name": "Ponce Recycling — State College Blvd",
        "facility_type": "CalRecycle-certified beverage container buyback",
        "city_slug": "anaheim",
        "state": "CA",
        "zip": "92806",
        "address": "1098 N State College Boulevard, Anaheim, CA 92806",
        "lat": 33.853,
        "lng": -117.889,
        "source_url": "https://www2.calrecycle.ca.gov/BevContainer/RecyclingCenters/Details?AccountLocationID=54340",
        "hours": "Daily 9:00–17:00",
        "phone": "(323) 533-4862",
        "accepted_materials": [
            "glass-bottles",
            "plastic-bags",
        ],
    },
]


def mats(*groups):
    out, seen = [], set()
    for g in groups:
        for m in g:
            if m not in ITEMS:
                raise SystemExit(f"unknown material slug: {m}")
            if m not in seen:
                seen.add(m)
                out.append(m)
    return out


def main() -> None:
    for row in FACILITIES:
        row["accepted_materials"] = mats(row["accepted_materials"])

    facilities = json.loads(FAC_PATH.read_text())
    by_key = {(f.get("city_slug"), f.get("name")): i for i, f in enumerate(facilities)}
    added = updated = 0
    for row in FACILITIES:
        key = (row["city_slug"], row["name"])
        if key in by_key:
            facilities[by_key[key]] = {**facilities[by_key[key]], **row}
            updated += 1
        else:
            facilities.append(row)
            by_key[key] = len(facilities) - 1
            added += 1

    FAC_PATH.write_text(json.dumps(facilities, indent=2) + "\n")
    print(json.dumps({"added": added, "updated": updated, "skips": SKIPS}, indent=2))


if __name__ == "__main__":
    main()
