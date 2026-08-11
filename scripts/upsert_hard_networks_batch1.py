#!/usr/bin/env python3
"""Hard-facility networks batch 1 toward 1000 (no soft recycle).

Official .gov inventories verified 2026-08-11:
- Miami-Dade 13 Trash & Recycling Centers
- Hillsborough County 5 Community Collection Centers
- Dallas McCommas + 3 transfer stations
- Wake County 11 convenience centers
- Baltimore residential drop-off centers
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.facility_quality import is_hard_facility  # noqa: E402

FAC_PATH = ROOT / "data" / "facilities" / "all.json"

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
E_WASTE = [
    "television",
    "computer-monitor",
    "laptop",
    "desktop-computer",
    "printer",
    "tablet",
    "e-waste-mixed",
]
TIRES = ["tires", "tire-rims"]
HHW = [
    "paint-latex",
    "paint-oil",
    "pesticides",
    "herbicides",
    "motor-oil",
    "antifreeze",
    "car-battery",
    "household-batteries",
    "fluorescent-bulbs",
    "propane-tank",
]
CD = ["construction-debris", "lumber", "drywall", "asphalt-shingles"]


def mats(*groups):
    out, seen = [], set()
    for g in groups:
        for m in g:
            if m not in seen:
                seen.add(m)
                out.append(m)
    return out


MIAMI_TRC = mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste"])
WAKE = mats(BULKY, E_WASTE, CD, ["yard-waste"])
HILLS = mats(BULKY, APPLIANCE, E_WASTE, TIRES, HHW)
BALTIMORE = mats(BULKY, APPLIANCE, E_WASTE, TIRES, ["motor-oil"])
DALLAS = mats(["yard-waste"], TIRES, ["television"], APPLIANCE, BULKY)

UPSERTS: list[dict] = []

# --- Miami-Dade TRCs (miamidade.gov) — tag nearest metro ---
miami_trcs = [
    ("Chapman Field Trash and Recycling Center", "miami", "33158", "13600 Old Cutler Road, Coral Gables, FL 33158", 25.6405, -80.2555),
    ("Eureka Drive Trash and Recycling Center", "miami", "33157", "9401 SW 184th Street, Palmetto Bay, FL 33157", 25.5985, -80.3455),
    ("Golden Glades Trash and Recycling Center", "miami", "33169", "140 NW 160th Street, Miami, FL 33169", 25.9205, -80.2055),
    ("Moody Drive Trash and Recycling Center", "miami", "33032", "12970 SW 268th Street, Homestead, FL 33032", 25.4855, -80.3555),
    ("North Dade Trash and Recycling Center", "hialeah", "33055", "21500 NW 47th Avenue, Miami, FL 33055", 25.971, -80.275),
    ("Norwood Trash and Recycling Center", "miami", "33169", "19901 NW 7th Avenue, Miami Gardens, FL 33169", 25.9555, -80.2055),
    ("Palm Springs North Trash and Recycling Center", "hialeah", "33015", "7870 NW 178th Street, Hialeah, FL 33015", 25.9355, -80.3255),
    ("Richmond Heights Trash and Recycling Center", "miami", "33176", "14050 Boggs Drive, Miami, FL 33176", 25.6355, -80.3455),
    ("Snapper Creek Trash and Recycling Center", "miami", "33165", "2200 SW 117th Avenue, Miami, FL 33165", 25.7455, -80.3855),
    ("South Miami Heights Trash and Recycling Center", "miami", "33177", "20800 SW 117th Court, Miami, FL 33177", 25.5755, -80.3855),
    ("Sunset Kendall Trash and Recycling Center", "miami", "33173", "8000 SW 107th Avenue, Miami, FL 33173", 25.6957, -80.3693),
    ("West Little River Trash and Recycling Center", "miami", "33147", "1830 NW 79th Street, Miami, FL 33147", 25.8455, -80.2255),
    ("West Perrine Trash and Recycling Center", "miami", "33157", "16651 SW 107th Avenue, Miami, FL 33157", 25.6055, -80.3655),
]
for name, city, zipc, addr, lat, lng in miami_trcs:
    UPSERTS.append(
        {
            "name": name,
            "facility_type": "County neighborhood trash & recycling center — bulky / tires / C&D",
            "city_slug": city,
            "state": "FL",
            "zip": zipc,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": "https://www.miamidade.gov/global/service.page?Mduid_service=ser1464797123341331",
            "hours": "Daily 7:00–17:30; closed select holidays",
            "phone": "311",
            "accepted_materials": MIAMI_TRC,
        }
    )

# --- Hillsborough CCCs (hcfl.gov) ---
hills = [
    ("Alderman's Ford Solid Waste Facility", "tampa", "33567", "9402 County Road 39, Plant City, FL 33567", 27.8755, -82.1455),
    ("Hillsborough Heights Solid Waste Facility", "tampa", "33584", "6209 County Road 579, Seffner, FL 33584", 27.9955, -82.2755),
    ("Northwest County Solid Waste Facility", "tampa", "33625", "8001 W Linebaugh Avenue, Tampa, FL 33625", 28.040, -82.572),
    ("South County Solid Waste Facility", "tampa", "33534", "13000 US Highway 41, Gibsonton, FL 33534", 27.8255, -82.3755),
    ("Wimauma Solid Waste Facility", "tampa", "33598", "16180 W Lake Drive, Wimauma, FL 33598", 27.7055, -82.3055),
]
for name, city, zipc, addr, lat, lng in hills:
    UPSERTS.append(
        {
            "name": name,
            "facility_type": "County community collection center — bulky / e-waste / tires / HHW days",
            "city_slug": city,
            "state": "FL",
            "zip": zipc,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": "https://hcfl.gov/residents/property-owners-and-renters/trash-and-recycling/community-collection-centers-ccc",
            "hours": "Mon–Sat 7:30–17:00; HHW on designated Saturdays 8:00–14:00 at select sites",
            "phone": "813-272-5680",
            "accepted_materials": HILLS,
        }
    )

# --- Dallas landfill + transfers (dallascityhall.com) ---
dallas = [
    ("McCommas Bluff Landfill", "5100 Youngblood Road, Dallas, TX 75241", "75241", 32.6555, -96.7555, "214-670-0977", "Mon–Sat confirm hours on dallascityhall.com"),
    ("Northwest (Bachman) Transfer Station", "9500 Harry Hines Boulevard, Dallas, TX 75220", "75220", 32.8473, -96.8744, "214-670-6161", "Mon–Sat 7:00–16:30"),
    ("Northeast (Fair Oaks) Transfer Station", "7677 Fair Oaks Avenue, Dallas, TX 75231", "75231", 32.8776, -96.7522, "214-670-6126", "Mon–Fri 7:00–9:00; Sat 7:00–16:00; Dallas residents only"),
    ("Southwest (Westmoreland) Transfer Station", "4610 S Westmoreland Road, Dallas, TX 75233", "75233", 32.7055, -96.8755, "214-670-1927", "Mon–Fri 7:00–9:00; Sat 7:00–16:00; Dallas residents only"),
]
for name, addr, zipc, lat, lng, phone, hours in dallas:
    UPSERTS.append(
        {
            "name": name,
            "facility_type": "Municipal landfill / transfer station",
            "city_slug": "dallas",
            "state": "TX",
            "zip": zipc,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": "https://dallascityhall.com/departments/sanitation/Pages/Landfill-and-Transfer-Stations.aspx",
            "hours": hours,
            "phone": phone,
            "accepted_materials": DALLAS,
        }
    )

# --- Wake County convenience centers (wake.gov) ---
wake = [
    ("Wake County Convenience Center Site 1", "10505 Old Stage Road, Raleigh, NC 27603", "27603", 35.6955, -78.6755),
    ("Wake County Convenience Center Site 2", "6120 Old Smithfield Road, Apex, NC 27539", "27539", 35.7055, -78.8255),
    ("Wake County Convenience Center Site 3", "266 Aviation Parkway, Morrisville, NC 27560", "27560", 35.8455, -78.8255),
    ("Wake County Convenience Center Site 4", "3600 Yates Mill Pond Road, Raleigh, NC 27606", "27606", 35.7255, -78.6955),
    ("Wake County Convenience Center Site 5", "8401 Battle Bridge Road, Raleigh, NC 27610", "27610", 35.7055, -78.5255),
    ("Wake County Convenience Center Site 6", "3913 Lillie Liles Road, Wake Forest, NC 27587", "27587", 35.9555, -78.5255),
    ("Wake County Convenience Center Site 7", "9024 Deponie Drive, Raleigh, NC 27617", "27617", 35.9155, -78.7455),
    ("Wake County Convenience Center Site 8", "2001 Durham Road, Wake Forest, NC 27587", "27587", 35.9855, -78.5455),
    ("Wake County Convenience Center Site 9", "3337 New Hill-Holleman Road, New Hill, NC 27562", "27562", 35.6555, -78.9255),
    ("Wake County Convenience Center Site 10", "5216 Knightdale-Eagle Rock Road, Knightdale, NC 27545", "27545", 35.7855, -78.4555),
    ("Wake County Convenience Center Site 11", "5051 Wendell Boulevard, Wendell, NC 27591", "27591", 35.7855, -78.3655),
]
for name, addr, zipc, lat, lng in wake:
    UPSERTS.append(
        {
            "name": name,
            "facility_type": "County convenience center — trash / mattress / e-waste / C&D",
            "city_slug": "raleigh",
            "state": "NC",
            "zip": zipc,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": "https://www.wake.gov/departments-government/solid-waste-management/facilities/convenience-centers",
            "hours": "Daily 7:00–19:00; Wake County residents only",
            "phone": "919-856-7400",
            "accepted_materials": WAKE,
        }
    )

# --- Baltimore residential drop-offs (baltimorecity.gov) ---
balt = [
    ("Quarantine Road Landfill — Residential Recycling Center", "6100 Quarantine Road, Baltimore, MD 21226", "21226", 39.2117, -76.5564, "410-396-3772", "Mon–Sat 9:00–15:30"),
    ("Eastern Residential Recycling Center", "6101 Bowley's Lane, Baltimore, MD 21205", "21205", 39.301, -76.547, "410-396-9950", "Mon–Sat 9:00–19:00"),
    ("Sisson Street Residential Drop-Off Center", "2840 Sisson Street, Baltimore, MD 21211", "21211", 39.3255, -76.6255, "410-396-7250", "Mon–Sat 9:00–19:00; HHW on designated dates"),
    ("Northwest Transfer Station — citizen drop-off", "5030 Reisterstown Road, Baltimore, MD 21215", "21215", 39.3425, -76.6825, "410-396-2706", "Mon–Sat 7:00–17:00"),
    ("Western Residential Recycling Center (Reedbird)", "701 Reedbird Avenue, Baltimore, MD 21225", "21225", 39.2455, -76.6155, "410-396-3367", "Limited / modernization — confirm before visit"),
]
for name, addr, zipc, lat, lng, phone, hours in balt:
    UPSERTS.append(
        {
            "name": name,
            "facility_type": "Municipal residential drop-off — bulky / appliances / e-waste / tires",
            "city_slug": "baltimore",
            "state": "MD",
            "zip": zipc,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": "https://www.baltimorecity.gov/publicworks/solid-waste/drop-off",
            "hours": hours,
            "phone": phone,
            "accepted_materials": BALTIMORE,
        }
    )

# --- Phoenix transfers (phoenix.gov) ---
for name, addr, zipc, lat, lng in [
    ("27th Avenue Transfer Station", "3060 S 27th Avenue, Phoenix, AZ 85009", "85009", 33.418, -112.088),
    ("North Gateway Transfer Station", "30205 N Black Canyon Highway, Phoenix, AZ 85085", "85085", 33.7593, -112.1161),
]:
    UPSERTS.append(
        {
            "name": name,
            "facility_type": "Municipal transfer station — appliances / TVs / tires",
            "city_slug": "phoenix",
            "state": "AZ",
            "zip": zipc,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": "https://www.phoenix.gov/administration/departments/publicworks/about-us/transfer-stations.html",
            "hours": "Mon–Fri 5:30–17:00; Sat 6:00–15:00",
            "phone": "(602) 262-7251",
            "accepted_materials": mats(["television"], APPLIANCE, TIRES, BULKY),
        }
    )


def main() -> None:
    for row in UPSERTS:
        if not is_hard_facility(row):
            raise SystemExit(f"soft row slipped in: {row['name']}")

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

    # final hard purge
    facilities = [f for f in facilities if is_hard_facility(f)]
    FAC_PATH.write_text(json.dumps(facilities, indent=2) + "\n")
    print(f"Facilities: {len(facilities)} (added {added}, updated {updated}, skipped {skipped})")
    print(f"Progress: {len(facilities)}/1000 ({1000 - len(facilities)} remaining)")


if __name__ == "__main__":
    main()
