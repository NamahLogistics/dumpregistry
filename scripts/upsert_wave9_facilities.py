#!/usr/bin/env python3
"""Add secondary verified drop-off sites for wave-9 metros + tag accepted_materials."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAC_PATH = ROOT / "data" / "facilities" / "all.json"

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
BULKY = [
    "mattress",
    "box-spring",
    "sofa",
    "recliner",
    "carpet",
    "yard-waste",
]
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


def mats(*groups):
    out, seen = [], set()
    for g in groups:
        for m in g:
            if m not in seen:
                seen.add(m)
                out.append(m)
    return out


NEW = [
    {
        "name": "Clark County HHW — Henderson (South)",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "las-vegas",
        "state": "NV",
        "zip": "89011",
        "address": "560 Cape Horn Dr, Henderson, NV 89011",
        "lat": 36.0145,
        "lng": -114.9855,
        "source_url": "https://www.republicservices.com/municipality/southern-nevada",
        "hours": "Wed–Sat 9:00–13:00; rotating with North site — check calendar",
        "phone": "702-734-5400",
        "accepted_materials": mats(HHW),
    },
    {
        "name": "Cheyenne Transfer Station — free electronics drop-off",
        "facility_type": "E-waste / transfer station",
        "city_slug": "las-vegas",
        "state": "NV",
        "zip": "89030",
        "address": "315 W Cheyenne Ave, North Las Vegas, NV 89030",
        "lat": 36.1915,
        "lng": -115.1485,
        "source_url": "https://www.republicservices.com/municipality/southern-nevada",
        "hours": "Daily 7:00–15:00 — electronics free; refrigerators fee",
        "phone": "702-734-5400",
        "accepted_materials": mats(E_WASTE, APPLIANCE),
    },
    {
        "name": "Wake County Multi-Material Recycling Facility — South Wake",
        "facility_type": "MMRF — appliances / e-waste / recyclables",
        "city_slug": "raleigh",
        "state": "NC",
        "zip": "27539",
        "address": "6150 Old Smithfield Rd, Apex, NC 27539",
        "lat": 35.6555,
        "lng": -78.7555,
        "source_url": "https://www.wake.gov/departments-government/waste-recycling/facilities/multi-material-recycling-facilities",
        "hours": "Mon–Sat 8:00–16:00",
        "phone": "919-856-7400",
        "accepted_materials": mats(E_WASTE, APPLIANCE),
    },
    {
        "name": "Wake County Multi-Material Recycling Facility — East Wake",
        "facility_type": "MMRF — appliances / e-waste / tires",
        "city_slug": "raleigh",
        "state": "NC",
        "zip": "27591",
        "address": "5051 Wendell Blvd, Wendell, NC 27591",
        "lat": 35.7805,
        "lng": -78.3705,
        "source_url": "https://www.wake.gov/departments-government/waste-recycling/facilities/multi-material-recycling-facilities",
        "hours": "Sat–Sun 8:00–16:00",
        "phone": "919-856-7400",
        "accepted_materials": mats(E_WASTE, APPLIANCE, TIRES),
    },
    {
        "name": "Hennepin County HHW — Brooklyn Park",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "minneapolis",
        "state": "MN",
        "zip": "55445",
        "address": "8100 Jefferson Hwy, Brooklyn Park, MN 55445",
        "lat": 45.1055,
        "lng": -93.3805,
        "source_url": "https://www.hennepin.us/green-disposal-guide/drop-off-facilities",
        "hours": "Tue–Sat 9:00–17:00",
        "phone": "612-348-3777",
        "accepted_materials": mats(HHW, E_WASTE),
    },
    {
        "name": "River City Recycling Transfer Station — Omaha bulky vouchers",
        "facility_type": "Bulky material drop-off (city voucher program)",
        "city_slug": "omaha",
        "state": "NE",
        "zip": "68107",
        "address": "6404 S 60th St, Omaha, NE 68107",
        "lat": 41.2055,
        "lng": -96.0105,
        "source_url": "https://wasteline.org/special-waste-information/bulky-item-disposal/",
        "hours": "Confirm hours on wasteline; city cost-share vouchers required",
        "phone": "",
        "accepted_materials": mats(BULKY),
    },
    {
        "name": "Virginia Beach Resource Recovery Center — e-cycling & tires",
        "facility_type": "E-waste / tires / freon appliances",
        "city_slug": "virginia-beach",
        "state": "VA",
        "zip": "23455",
        "address": "1989 Jake Sears Rd, Virginia Beach, VA 23455",
        "lat": 36.8655,
        "lng": -76.0555,
        "source_url": "https://pw.virginiabeach.gov/trash-recycling/landfill-and-rrc/resource-recovery-center",
        "hours": "Tue–Sat 7:00–16:30",
        "phone": "757-385-4650",
        "accepted_materials": mats(E_WASTE, APPLIANCE, TIRES),
    },
]


def main() -> None:
    facilities = json.loads(FAC_PATH.read_text())
    keys = {(f.get("city_slug"), f.get("name")) for f in facilities}
    added = 0
    for f in NEW:
        key = (f["city_slug"], f["name"])
        if key in keys:
            # refresh fields
            for i, cur in enumerate(facilities):
                if (cur.get("city_slug"), cur.get("name")) == key:
                    facilities[i] = {**cur, **f}
                    break
        else:
            facilities.append(f)
            keys.add(key)
            added += 1

    # Ensure existing wave-9 singles have materials tags
    for f in facilities:
        if f.get("accepted_materials"):
            continue
        t = (f.get("facility_type") or "").lower()
        if "hhw" in t or "hazard" in t:
            f["accepted_materials"] = mats(HHW)
        elif "e-waste" in t or "electronics" in t:
            f["accepted_materials"] = mats(E_WASTE)
        elif "bulky" in t:
            f["accepted_materials"] = mats(BULKY)

    FAC_PATH.write_text(json.dumps(facilities, indent=2) + "\n")
    print(f"Facilities now: {len(facilities)} (added {added})")


if __name__ == "__main__":
    main()
