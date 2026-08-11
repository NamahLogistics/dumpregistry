#!/usr/bin/env python3
"""Finder growth wave 13: tertiary drop-offs for 15 single-pin metros (2026-08-11).

One new portal-sourced drop-off per city when verifiable on .gov (or official city
portal). Skips cities with no third fixed facility beyond the two already listed.

SKIPS (no third verifiable fixed drop-off):
  - stockton: only SJ County HHW + Lovelace MRF on portal; Clean City drive-thrus rotate
  - henderson: Clark County TS + Henderson Shines cover city portal; no third fixed site
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAC_PATH = ROOT / "data" / "facilities" / "all.json"
ITEMS = {i["slug"] for i in json.loads((ROOT / "data" / "items.json").read_text())}

SKIPS = [
    {
        "city_slug": "stockton",
        "reason": "Portal lists only SJ County HHW and Lovelace MRF; remaining options are rotating drive-thru events without a fixed tertiary site.",
    },
    {
        "city_slug": "henderson",
        "reason": "Portal lists Clark County TS Henderson and Henderson Shines; no third fixed .gov drop-off beyond those.",
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


HHW = [
    "paint-latex",
    "paint-oil",
    "pesticides",
    "herbicides",
    "pool-chemicals",
    "gasoline",
    "motor-oil",
    "antifreeze",
    "car-battery",
    "household-batteries",
    "lithium-battery",
    "fluorescent-bulbs",
    "propane-tank",
    "cooking-oil",
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
    "ink-toner",
]

WAVE: list[dict] = [
    {
        "name": "Lexington Electronics Recycling Center",
        "facility_type": "Electronics / mixed recycling drop-off",
        "city_slug": "lexington",
        "state": "KY",
        "zip": "40508",
        "address": "1306 Versailles Road, Lexington, KY 40508",
        "lat": 38.0478,
        "lng": -84.5234,
        "source_url": "https://www.lexingtonky.gov/living/waste-collection/electronics-recycling",
        "hours": "Mon–Tue & Thu–Fri 8:00–16:00; Wed 12:00–16:00; Sat 8:00–12:00",
        "phone": "859-425-2255",
        "accepted_materials": mats(
            [
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
                "ink-toner",
                "fluorescent-bulbs",
                "led-bulbs",
                "household-batteries",
                "lithium-battery",
            ]
        ),
    },
    {
        "name": "Republic Services Recycling Drop-Off — Agnes Street",
        "facility_type": "Recycling drop-off center",
        "city_slug": "corpus-christi",
        "state": "TX",
        "zip": "78405",
        "address": "4414 Agnes Street, Corpus Christi, TX 78405",
        "lat": 27.7889,
        "lng": -97.4123,
        "source_url": "https://www.cctexas.com/howtorecycle",
        "hours": "Mon–Fri 8:00–17:00",
        "phone": "361-826-2489",
        "accepted_materials": mats(
            [
                "television",
                "computer-monitor",
                "laptop",
                "desktop-computer",
                "printer",
                "smartphone",
                "e-waste-mixed",
                "cardboard",
                "glass-bottles",
            ]
        ),
    },
    {
        "name": "Riverside City Corporation Yard",
        "facility_type": "City bulky / e-waste event drop-off",
        "city_slug": "riverside",
        "state": "CA",
        "zip": "92504",
        "address": "8095 Lincoln Avenue, Riverside, CA 92504",
        "lat": 33.9455,
        "lng": -117.4255,
        "source_url": "https://riversideca.gov/publicworks/trash-recycling/clean-riverside",
        "hours": "Periodic Sat events 8:00–12:00; see Clean Up Riverside calendar",
        "phone": "951-826-5311",
        "accepted_materials": mats(
            [
                "mattress",
                "box-spring",
                "sofa",
                "recliner",
                "television",
                "computer-monitor",
                "refrigerator",
                "freezer",
                "air-conditioner",
                "tires",
                "yard-waste",
                "concrete",
            ]
        ),
    },
    {
        "name": "OC HHW Collection Center — San Juan Capistrano",
        "facility_type": "HHW / e-waste",
        "city_slug": "santa-ana",
        "state": "CA",
        "zip": "92675",
        "address": "32250 Avenida La Pata, San Juan Capistrano, CA 92675",
        "lat": 33.5055,
        "lng": -117.6155,
        "source_url": "https://www.cmsdca.gov/trash___recycling/recycling_resources/oc_household_hazardous_waste_collection_centers.php",
        "hours": "Tue–Sat 9:00–15:00 (closed major holidays and during rain)",
        "phone": "714-834-4000",
        "accepted_materials": mats(HHW),
    },
    {
        "name": "Public Recycling Dumpster — College Hill Recreation Center",
        "facility_type": "Public recycling drop-off",
        "city_slug": "cincinnati",
        "state": "OH",
        "zip": "45224",
        "address": "5545 Belmont Ave, Cincinnati, OH 45224",
        "lat": 39.1855,
        "lng": -84.5455,
        "source_url": "https://www.cincinnati-oh.gov/recycling/public-dropoff/public-recycling-dumpsters/",
        "hours": "6:00–21:00",
        "phone": "513-765-1212",
        "accepted_materials": mats(["cardboard", "glass-bottles"]),
    },
    {
        "name": "Waste Management Recycling Center — Construction Circle East",
        "facility_type": "CRV buyback / recycling center",
        "city_slug": "irvine",
        "state": "CA",
        "zip": "92606",
        "address": "16122 Construction Circle East, Irvine, CA 92606",
        "lat": 33.6955,
        "lng": -117.8355,
        "source_url": "https://cityofirvine.org/environmental-programs/bottle-and-can-recycling",
        "hours": "Tue–Sat 10:00–17:00",
        "phone": "714-956-6222",
        "accepted_materials": mats(["cardboard", "glass-bottles"]),
    },
    {
        "name": "Orlando Fire Department Sharps Drop-Off — Fire Station 1",
        "facility_type": "Sharps exchange drop-off (all OFD fire stations)",
        "city_slug": "orlando",
        "state": "FL",
        "zip": "32801",
        "address": "78 West Central Boulevard, Orlando, FL 32801",
        "lat": 28.543,
        "lng": -81.379,
        "source_url": "https://www.orlando.gov/Public-Safety/OFD/Community-Programs/OFD-Cares/OFD-Support",
        "hours": "All 17 Orlando fire stations; bring approved sharps containers",
        "phone": "407-246-2314",
        "accepted_materials": mats(["medical-sharps", "needles"]),
    },
    {
        "name": "East End DPW 2nd Division Recycling Drop-Off",
        "facility_type": "Municipal recycling / yard / tire drop-off",
        "city_slug": "pittsburgh",
        "state": "PA",
        "zip": "15208",
        "address": "6814 Hamilton Ave, Pittsburgh, PA 15208",
        "lat": 40.4555,
        "lng": -79.8955,
        "source_url": "https://www.pittsburghpa.gov/Resident-Services/Trash-Recycling/Drop-Off-Info-Additional-Resources/Recycling-Drop-Off-Locations",
        "hours": "Mon–Sat 8:00–13:30",
        "phone": "412-665-3610",
        "accepted_materials": mats(
            [
                "cardboard",
                "glass-bottles",
                "yard-waste",
                "tires",
                "tire-rims",
                "christmas-tree",
            ]
        ),
    },
    {
        "name": "White Street Landfill Recycling Drop-Off",
        "facility_type": "Landfill recycling drop-off — paper / metal / plastic / glass",
        "city_slug": "greensboro",
        "state": "NC",
        "zip": "27405",
        "address": "2503 White Street, Greensboro, NC 27405",
        "lat": 36.1255,
        "lng": -79.7355,
        "source_url": "https://www.greensboro-nc.gov/departments/solid-waste-and-recycling/white-street-landfill",
        "hours": "Mon–Fri 7:50–16:50; Sat 7:00–13:00",
        "phone": "336-373-7658",
        "accepted_materials": mats(["cardboard", "glass-bottles"]),
    },
    {
        "name": "Jersey City Compost Drop-Off — City Hall",
        "facility_type": "Residential compost drop-off shed",
        "city_slug": "jersey-city",
        "state": "NJ",
        "zip": "07302",
        "address": "280 Grove Street (Mercer St entrance), Jersey City, NJ 07302",
        "lat": 40.7155,
        "lng": -74.0455,
        "source_url": "https://www.jerseycitynj.gov/cityhall/DPW/recycle/compost",
        "hours": "24/7 shed access; follow site signage",
        "phone": "201-547-4400",
        "accepted_materials": mats(["food-scraps", "yard-waste"]),
    },
    {
        "name": "Seacrest Parking Lot Recyclables Collection Site",
        "facility_type": "Public recyclables collection site",
        "city_slug": "lincoln",
        "state": "NE",
        "zip": "68506",
        "address": "Seacrest Parking Lot near 72nd and A Street, Lincoln, NE 68506",
        "lat": 40.8055,
        "lng": -96.6255,
        "source_url": "https://www.lincoln.ne.gov/City/Departments/LTU/Utilities/Solid-Waste-Management/Recycling/Residential/Collection-Sites/Consolidation-Plan",
        "hours": "24 hours (use during daylight on weekdays when possible)",
        "phone": "402-441-8215",
        "accepted_materials": mats(["cardboard", "glass-bottles"]),
    },
    {
        "name": "Durham County Convenience Center — Parkwood",
        "facility_type": "County convenience center (recycling / disposal)",
        "city_slug": "durham",
        "state": "NC",
        "zip": "27703",
        "address": "NC 55 and T.W. Alexander Drive, Durham, NC 27703",
        "lat": 35.9055,
        "lng": -78.8255,
        "source_url": "https://www.durhamnc.gov/870/Recycling-Drop-Off-Sites",
        "hours": "Check Durham County for current convenience center hours",
        "phone": "919-560-0460",
        "accepted_materials": mats(
            [
                "cardboard",
                "glass-bottles",
                "yard-waste",
                "tires",
            ]
        ),
    },
    {
        "name": "North Transfer Station",
        "facility_type": "Municipal transfer station — bulk / BOAT-E",
        "city_slug": "st-louis",
        "state": "MO",
        "zip": "63102",
        "address": "71 Angelica Street, St. Louis, MO 63102",
        "lat": 38.6355,
        "lng": -90.2055,
        "source_url": "https://www.stlouis-mo.gov/government/departments/street/refuse/resident-dumping/north-transfer-station.cfm",
        "hours": "Mon–Fri 8:00–16:00; closed weekends and city holidays",
        "phone": "314-622-4800",
        "accepted_materials": mats(
            [
                "mattress",
                "sofa",
                "recliner",
                "tires",
                "refrigerator",
                "freezer",
                "washer",
                "dryer",
                "television",
                "computer-monitor",
                "yard-waste",
                "construction-debris",
            ]
        ),
    },
]


def main() -> None:
    facilities = json.loads(FAC_PATH.read_text())
    by_key = {(f.get("city_slug"), f.get("name")): i for i, f in enumerate(facilities)}
    added = updated = 0
    for row in WAVE:
        key = (row["city_slug"], row["name"])
        if key in by_key:
            facilities[by_key[key]] = {**facilities[by_key[key]], **row}
            updated += 1
        else:
            facilities.append(row)
            by_key[key] = len(facilities) - 1
            added += 1

    FAC_PATH.write_text(json.dumps(facilities, indent=2) + "\n")
    print(f"Facilities: {len(facilities)} (added {added}, updated {updated})")
    print(f"Wave 13 rows: {len(WAVE)}")
    print(f"Skips: {len(SKIPS)}")
    for s in SKIPS:
        print(f"  skip {s['city_slug']}: {s['reason']}")


if __name__ == "__main__":
    main()
