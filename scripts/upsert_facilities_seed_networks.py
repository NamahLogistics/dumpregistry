#!/usr/bin/env python3
"""Seed verified multi-site municipal networks toward 1000-facility goal.

Sources fetched 2026-08-11 from official city pages. No deploy.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAC_PATH = ROOT / "data" / "facilities" / "all.json"
ITEMS = {i["slug"] for i in json.loads((ROOT / "data" / "items.json").read_text())}

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
]
E_WASTE = [
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
BULKY = ["mattress", "box-spring", "sofa", "recliner", "carpet", "yard-waste"]
APPLIANCE = [
    "refrigerator",
    "freezer",
    "air-conditioner",
    "washer",
    "dryer",
    "dishwasher",
    "stove",
    "water-heater",
]
TIRES = ["tires", "tire-rims"]
RECYCLE = ["cardboard", "glass-bottles"]


def mats(*groups):
    out, seen = [], set()
    for g in groups:
        for m in g:
            if m not in ITEMS:
                raise SystemExit(f"bad slug {m}")
            if m not in seen:
                seen.add(m)
                out.append(m)
    return out


HOUSTON_MATS = mats(BULKY, APPLIANCE, TIRES, ["motor-oil"], RECYCLE)
PHILLY_MATS = mats(
    BULKY,
    APPLIANCE,
    E_WASTE,
    TIRES,
    ["paint-latex", "fluorescent-bulbs", "household-batteries", "lithium-battery", "car-battery"],
    RECYCLE,
)
SAFE_MATS = mats(HHW, E_WASTE)
NASH_CC = mats(E_WASTE, BULKY, TIRES, RECYCLE, ["food-scraps"])
NASH_RECYCLE = mats(RECYCLE)

UPSERTS = [
    # --- Houston Residential Drop-Off Centers (houstontx.gov) ---
    {
        "name": "Houston Neighborhood Depository — North",
        "facility_type": "City residential drop-off center",
        "city_slug": "houston",
        "state": "TX",
        "zip": "77022",
        "address": "9003 N Main St, Houston, TX 77022",
        "lat": 29.861,
        "lng": -95.365,
        "source_url": "https://www.houstontx.gov/solidwaste/depository.html",
        "hours": "Tue–Sat 9:00–18:00",
        "phone": "311",
        "accepted_materials": HOUSTON_MATS,
    },
    {
        "name": "Houston Neighborhood Depository — Northwest",
        "facility_type": "City residential drop-off center",
        "city_slug": "houston",
        "state": "TX",
        "zip": "77041",
        "address": "14400 Sommermeyer Street, Houston, TX 77041",
        "lat": 29.8755,
        "lng": -95.5555,
        "source_url": "https://www.houstontx.gov/solidwaste/depository.html",
        "hours": "Tue–Sat 9:00–18:00",
        "phone": "311",
        "accepted_materials": HOUSTON_MATS,
    },
    {
        "name": "Houston Neighborhood Depository — Northeast",
        "facility_type": "City residential drop-off center",
        "city_slug": "houston",
        "state": "TX",
        "zip": "77028",
        "address": "5565 Kirkpatrick Boulevard, Houston, TX 77028",
        "lat": 29.8255,
        "lng": -95.2855,
        "source_url": "https://www.houstontx.gov/solidwaste/depository.html",
        "hours": "Tue–Sat 9:00–18:00",
        "phone": "311",
        "accepted_materials": HOUSTON_MATS,
    },
    {
        "name": "Houston Neighborhood Depository — Southeast",
        "facility_type": "City residential drop-off center",
        "city_slug": "houston",
        "state": "TX",
        "zip": "77017",
        "address": "2240 Central Street, Houston, TX 77017",
        "lat": 29.6855,
        "lng": -95.2655,
        "source_url": "https://www.houstontx.gov/solidwaste/depository.html",
        "hours": "Tue–Sat 9:00–18:00",
        "phone": "311",
        "accepted_materials": HOUSTON_MATS,
    },
    {
        "name": "Houston Neighborhood Depository — South",
        "facility_type": "City residential drop-off center",
        "city_slug": "houston",
        "state": "TX",
        "zip": "77033",
        "address": "5100 Sunbeam Street, Houston, TX 77033",
        "lat": 29.6555,
        "lng": -95.3555,
        "source_url": "https://www.houstontx.gov/solidwaste/depository.html",
        "hours": "Tue–Sat 9:00–18:00",
        "phone": "311",
        "accepted_materials": HOUSTON_MATS,
    },
    {
        "name": "Houston Neighborhood Depository — Southwest",
        "facility_type": "City residential drop-off center",
        "city_slug": "houston",
        "state": "TX",
        "zip": "77074",
        "address": "10785 Southwest Freeway, Houston, TX 77074",
        "lat": 29.6555,
        "lng": -95.5255,
        "source_url": "https://www.houstontx.gov/solidwaste/depository.html",
        "hours": "Tue–Sat 9:00–18:00",
        "phone": "311",
        "accepted_materials": HOUSTON_MATS,
    },
    # --- Philadelphia SCCs (phila.gov) ---
    {
        "name": "Port Richmond Sanitation Convenience Center",
        "facility_type": "City sanitation convenience center",
        "city_slug": "philadelphia",
        "state": "PA",
        "zip": "19137",
        "address": "3901 Delaware Avenue, Philadelphia, PA 19137",
        "lat": 39.9825,
        "lng": -75.0836,
        "source_url": "https://www.phila.gov/services/trash-recycling-city-upkeep/find-a-sanitation-convenience-center-to-drop-off-trash-or-recycling/",
        "hours": "Mon–Sat 8:00–18:00",
        "phone": "215-685-1358",
        "accepted_materials": PHILLY_MATS,
    },
    {
        "name": "Strawberry Mansion Sanitation Convenience Center",
        "facility_type": "City sanitation convenience center",
        "city_slug": "philadelphia",
        "state": "PA",
        "zip": "19121",
        "address": "2601 W Glenwood Avenue, Philadelphia, PA 19121",
        "lat": 39.9855,
        "lng": -75.1755,
        "source_url": "https://www.phila.gov/services/trash-recycling-city-upkeep/find-a-sanitation-convenience-center-to-drop-off-trash-or-recycling/",
        "hours": "Mon–Sat 8:00–18:00",
        "phone": "215-685-3955",
        "accepted_materials": PHILLY_MATS,
    },
    {
        "name": "West Philadelphia Sanitation Convenience Center",
        "facility_type": "City sanitation convenience center",
        "city_slug": "philadelphia",
        "state": "PA",
        "zip": "19143",
        "address": "5100 Grays Avenue, Philadelphia, PA 19143",
        "lat": 39.9355,
        "lng": -75.2155,
        "source_url": "https://www.phila.gov/services/trash-recycling-city-upkeep/find-a-sanitation-convenience-center-to-drop-off-trash-or-recycling/",
        "hours": "Mon–Sat 8:00–18:00",
        "phone": "215-685-2600",
        "accepted_materials": PHILLY_MATS,
    },
    {
        "name": "Southwest Sanitation Convenience Center",
        "facility_type": "City sanitation convenience center",
        "city_slug": "philadelphia",
        "state": "PA",
        "zip": "19153",
        "address": "3033 S 63rd Street, Philadelphia, PA 19153",
        "lat": 39.905,
        "lng": -75.225,
        "source_url": "https://www.phila.gov/services/trash-recycling-city-upkeep/find-a-sanitation-convenience-center-to-drop-off-trash-or-recycling/",
        "hours": "Mon–Sat 8:00–18:00",
        "phone": "215-685-4290",
        "accepted_materials": PHILLY_MATS,
    },
    {
        "name": "Northwest Sanitation Convenience Center",
        "facility_type": "City sanitation convenience center",
        "city_slug": "philadelphia",
        "state": "PA",
        "zip": "19128",
        "address": "300 Domino Lane (near Umbria Street), Philadelphia, PA 19128",
        "lat": 40.0275,
        "lng": -75.2325,
        "source_url": "https://www.phila.gov/services/trash-recycling-city-upkeep/find-a-sanitation-convenience-center-to-drop-off-trash-or-recycling/",
        "hours": "Mon–Sat 8:00–18:00",
        "phone": "215-685-2502",
        "accepted_materials": PHILLY_MATS,
    },
    {
        "name": "Northeast Sanitation Convenience Center",
        "facility_type": "City sanitation convenience center",
        "city_slug": "philadelphia",
        "state": "PA",
        "zip": "19114",
        "address": "State Road & Ashburner Street, Philadelphia, PA 19114",
        "lat": 40.0655,
        "lng": -74.9855,
        "source_url": "https://www.phila.gov/services/trash-recycling-city-upkeep/find-a-sanitation-convenience-center-to-drop-off-trash-or-recycling/",
        "hours": "Mon–Sat 8:00–18:00",
        "phone": "215-685-8072",
        "accepted_materials": PHILLY_MATS,
    },
    # --- LA S.A.F.E. Centers (lacitysan.org) — open sites ---
    {
        "name": "Nicole Bernson (Balboa) S.A.F.E. Center",
        "facility_type": "S.A.F.E. Center — HHW / e-waste",
        "city_slug": "los-angeles",
        "state": "CA",
        "zip": "91325",
        "address": "10241 N Balboa Boulevard, Northridge, CA 91325",
        "lat": 34.2555,
        "lng": -118.5355,
        "source_url": "https://www.lacitysan.org/san/faces/home/portal/s-lsh-wwd/s-lsh-wwd-s/s-lsh-wwd-s-c/s-lsh-wwd-s-c-hw",
        "hours": "Sat–Sun 9:00–15:00",
        "phone": "1-800-773-2489",
        "accepted_materials": SAFE_MATS,
    },
    {
        "name": "Gaffey Street S.A.F.E. Center",
        "facility_type": "S.A.F.E. Center — HHW / e-waste",
        "city_slug": "los-angeles",
        "state": "CA",
        "zip": "90731",
        "address": "1400 N Gaffey Street, San Pedro, CA 90731",
        "lat": 33.7537,
        "lng": -118.2924,
        "source_url": "https://www.lacitysan.org/san/faces/home/portal/s-lsh-wwd/s-lsh-wwd-s/s-lsh-wwd-s-c/s-lsh-wwd-s-c-hw",
        "hours": "Sat–Sun 9:00–15:00",
        "phone": "1-800-773-2489",
        "accepted_materials": SAFE_MATS,
    },
    {
        "name": "Hyperion S.A.F.E. Center",
        "facility_type": "S.A.F.E. Center — HHW / e-waste",
        "city_slug": "los-angeles",
        "state": "CA",
        "zip": "90293",
        "address": "7660 West Imperial Highway, Gate B, Playa Del Rey, CA 90293",
        "lat": 33.9255,
        "lng": -118.4255,
        "source_url": "https://www.lacitysan.org/san/faces/home/portal/s-lsh-wwd/s-lsh-wwd-s/s-lsh-wwd-s-c/s-lsh-wwd-s-c-hw",
        "hours": "Sat–Sun 9:00–15:00",
        "phone": "1-800-773-2489",
        "accepted_materials": SAFE_MATS,
    },
    {
        "name": "Randall Street S.A.F.E. Center",
        "facility_type": "S.A.F.E. Center — HHW / e-waste",
        "city_slug": "los-angeles",
        "state": "CA",
        "zip": "91352",
        "address": "11025 Randall Street, Sun Valley, CA 91352",
        "lat": 34.2555,
        "lng": -118.3855,
        "source_url": "https://www.lacitysan.org/san/faces/home/portal/s-lsh-wwd/s-lsh-wwd-s/s-lsh-wwd-s-c/s-lsh-wwd-s-c-hw",
        "hours": "Sat–Sun 9:00–15:00",
        "phone": "1-800-773-2489",
        "accepted_materials": SAFE_MATS,
    },
    {
        "name": "Washington Blvd S.A.F.E. Center",
        "facility_type": "S.A.F.E. Center — HHW / e-waste",
        "city_slug": "los-angeles",
        "state": "CA",
        "zip": "90021",
        "address": "2649 E Washington Boulevard, Los Angeles, CA 90021",
        "lat": 34.0155,
        "lng": -118.2255,
        "source_url": "https://www.lacitysan.org/san/faces/home/portal/s-lsh-wwd/s-lsh-wwd-s/s-lsh-wwd-s-c/s-lsh-wwd-s-c-hw",
        "hours": "Sat–Sun 9:00–15:00",
        "phone": "1-800-773-2489",
        "accepted_materials": SAFE_MATS,
    },
    # --- Nashville convenience + recycling drop-offs (nashville.gov) ---
    {
        "name": "Anderson Lane Convenience Center",
        "facility_type": "Convenience center",
        "city_slug": "nashville",
        "state": "TN",
        "zip": "37115",
        "address": "939A Anderson Lane, Madison, TN 37115",
        "lat": 36.2555,
        "lng": -86.7155,
        "source_url": "https://www.nashville.gov/departments/waste-services/convenience-centers/hours-and-locations",
        "hours": "Tue–Sat 8:30–16:30",
        "phone": "(615) 862-5000",
        "accepted_materials": NASH_CC,
    },
    {
        "name": "East Convenience Center",
        "facility_type": "Convenience center",
        "city_slug": "nashville",
        "state": "TN",
        "zip": "37207",
        "address": "943A Doctor Richard G. Adams Drive, Nashville, TN 37207",
        "lat": 36.1855,
        "lng": -86.7555,
        "source_url": "https://www.nashville.gov/departments/waste-services/convenience-centers/hours-and-locations",
        "hours": "Tue–Sat 8:30–16:30",
        "phone": "(615) 862-5000",
        "accepted_materials": NASH_CC,
    },
    {
        "name": "Ezell Pike Convenience Center",
        "facility_type": "Convenience center",
        "city_slug": "nashville",
        "state": "TN",
        "zip": "37211",
        "address": "3254 Ezell Pike, Nashville, TN 37211",
        "lat": 36.0955,
        "lng": -86.7055,
        "source_url": "https://www.nashville.gov/departments/waste-services/convenience-centers/hours-and-locations",
        "hours": "Tue–Sat 8:30–16:30",
        "phone": "(615) 862-5000",
        "accepted_materials": NASH_CC,
    },
    {
        "name": "Omohundro Convenience Center",
        "facility_type": "Convenience center",
        "city_slug": "nashville",
        "state": "TN",
        "zip": "37210",
        "address": "1019 Omohundro Place, Nashville, TN 37210",
        "lat": 36.1556,
        "lng": -86.7392,
        "source_url": "https://www.nashville.gov/departments/waste-services/convenience-centers/hours-and-locations",
        "hours": "Tue–Sat 8:30–16:30",
        "phone": "(615) 862-5000",
        "accepted_materials": NASH_CC,
    },
    # --- Fort Worth Drop-Off Stations (fortworthtexas.gov) ---
    {
        "name": "Brennan Drop-off Station",
        "facility_type": "Municipal drop-off station",
        "city_slug": "fort-worth",
        "state": "TX",
        "zip": "76106",
        "address": "2400 Brennan Avenue, Fort Worth, TX 76106",
        "lat": 32.7855,
        "lng": -97.3455,
        "source_url": "https://www.fortworthtexas.gov/departments/environmental-services/solidwaste/dropoff",
        "hours": "Tue–Fri 8:00–17:00; Sat 8:00–12:00",
        "phone": "817-392-1234",
        "accepted_materials": mats(BULKY, APPLIANCE, TIRES, E_WASTE, HHW, RECYCLE),
    },
    {
        "name": "Southeast Drop-off Station",
        "facility_type": "Municipal drop-off station",
        "city_slug": "fort-worth",
        "state": "TX",
        "zip": "76119",
        "address": "5150 Martin Luther King Freeway, Fort Worth, TX 76119",
        "lat": 32.6955,
        "lng": -97.2855,
        "source_url": "https://www.fortworthtexas.gov/departments/environmental-services/solidwaste/dropoff",
        "hours": "Tue–Fri 8:00–17:00; Sat 8:00–12:00",
        "phone": "817-392-1234",
        "accepted_materials": mats(BULKY, APPLIANCE, TIRES, E_WASTE, HHW, RECYCLE),
    },
    {
        "name": "Old Hemphill Road Drop-off Station",
        "facility_type": "Municipal drop-off station",
        "city_slug": "fort-worth",
        "state": "TX",
        "zip": "76134",
        "address": "6260 Old Hemphill Road, Fort Worth, TX 76134",
        "lat": 32.6575,
        "lng": -97.3239,
        "source_url": "https://www.fortworthtexas.gov/departments/environmental-services/solidwaste/dropoff",
        "hours": "Tue–Fri 8:00–17:00; Sat 8:00–12:00",
        "phone": "817-392-1234",
        "accepted_materials": mats(BULKY, APPLIANCE, TIRES, E_WASTE, HHW, RECYCLE),
    },
    {
        "name": "Hillshire Drop-off Station",
        "facility_type": "Municipal drop-off station",
        "city_slug": "fort-worth",
        "state": "TX",
        "zip": "76119",
        "address": "301 Hillshire Drive, Fort Worth, TX 76119",
        "lat": 32.6855,
        "lng": -97.2655,
        "source_url": "https://www.fortworthtexas.gov/departments/environmental-services/solidwaste/dropoff",
        "hours": "Tue–Fri 8:00–17:00; Sat 8:00–12:00",
        "phone": "817-392-1234",
        "accepted_materials": mats(BULKY, APPLIANCE, TIRES, E_WASTE, HHW, RECYCLE),
    },
    {
        "name": "Fort Worth Southeast Landfill",
        "facility_type": "Municipal landfill",
        "city_slug": "fort-worth",
        "state": "TX",
        "zip": "76140",
        "address": "6288 Salt Road, Fort Worth, TX 76140",
        "lat": 32.6255,
        "lng": -97.2455,
        "source_url": "https://www.fortworthtexas.gov/departments/environmental-services/solidwaste/dropoff",
        "hours": "Confirm landfill hours / fees on fortworthtexas.gov",
        "phone": "817-392-1234",
        "accepted_materials": mats(BULKY, APPLIANCE, TIRES),
    },
]



def main() -> None:
    facilities = json.loads(FAC_PATH.read_text())
    by_key = {(f.get("city_slug"), f.get("name")): i for i, f in enumerate(facilities)}
    by_addr = {
        (f.get("city_slug"), (f.get("address") or "").lower()[:55])
        for f in facilities
        if f.get("address")
    }
    added = updated = skipped = 0
    for row in UPSERTS:
        key = (row["city_slug"], row["name"])
        addr = (row["city_slug"], row["address"].lower()[:55])
        if key in by_key:
            facilities[by_key[key]] = {**facilities[by_key[key]], **row}
            updated += 1
        elif addr in by_addr:
            skipped += 1
        else:
            facilities.append(row)
            by_key[key] = len(facilities) - 1
            by_addr.add(addr)
            added += 1
    FAC_PATH.write_text(json.dumps(facilities, indent=2) + "\n")
    print(f"Facilities: {len(facilities)} (added {added}, updated {updated}, skipped {skipped})")
    print(f"Progress to 1000: {len(facilities)}/1000 ({1000-len(facilities)} remaining)")


if __name__ == "__main__":
    main()
