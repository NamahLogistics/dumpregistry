#!/usr/bin/env python3
"""Authentic finder growth wave 2: secondary drop-offs for priority metros.

Portal-sourced only (2026-08-11). Adds transfer / landfill / convenience /
special-waste sites so nearest-center is not a single HHW pin per city.
"""

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


def mats(*groups):
    out, seen = [], set()
    for g in groups:
        for m in g:
            if m not in seen:
                seen.add(m)
                out.append(m)
    return out


UPSERTS = [
    {
        "name": "Central LA Recycling and Transfer Station (CLARTS)",
        "facility_type": "Municipal transfer station — public self-haul",
        "city_slug": "los-angeles",
        "state": "CA",
        "zip": "90021",
        "address": "2201 E. Washington Boulevard, Los Angeles, CA 90021",
        "lat": 34.0203,
        "lng": -118.2343,
        "source_url": "https://sanitation.lacity.gov/san/faces/home/portal/s-lsh-wwd/s-lsh-wwd-s/s-lsh-wwd-s-cl/s-lsh-wwd-s-cl-fs",
        "hours": "Mon–Fri 4:00–17:00; Sat 6:00–14:30; closed major holidays",
        "phone": "(213) 763-1918",
        "accepted_materials": mats(BULKY, APPLIANCE, ["television", "computer-monitor", "e-waste-mixed"]),
    },
    {
        "name": "DSNY Special Waste Drop-Off — Queens (College Point)",
        "facility_type": "Special waste / e-waste / HHW drop-off",
        "city_slug": "new-york",
        "state": "NY",
        "zip": "11354",
        "address": "30th Avenue between 120th and 122nd Streets (DSNY Queens District 7 Garage), College Point, NY 11354",
        "lat": 40.7761,
        "lng": -73.845,
        "source_url": "https://www.nyc.gov/site/dsny/what-we-do/programs/special-waste-drop-off.page",
        "hours": "Tue–Sat 9:00–15:00; NYC residents only; closed legal holidays and severe weather",
        "phone": "311",
        "accepted_materials": mats(
            [
                "paint-latex",
                "paint-oil",
                "motor-oil",
                "gasoline",
                "pesticides",
                "herbicides",
                "fluorescent-bulbs",
                "household-batteries",
                "lithium-battery",
                "car-battery",
                "propane-tank",
            ],
            E_WASTE,
            TIRES,
        ),
    },
    {
        "name": "Chicago Residential Recycling Drop-Off Center — Far North",
        "facility_type": "Municipal recycling drop-off center",
        "city_slug": "chicago",
        "state": "IL",
        "zip": "60626",
        "address": "6441 N. Ravenswood Avenue, Chicago, IL 60626",
        "lat": 41.9993,
        "lng": -87.6742,
        "source_url": "https://www.chicago.gov/city/en/sites/chicago-recycles/home/residential-recycling.html",
        "hours": "7 days/week during daylight hours",
        "phone": "(312) 744-2413",
        # Recycling drop-off — keep to electronics; bulky/Freon go to HHW facility
        "accepted_materials": mats(E_WASTE),
    },
    {
        "name": "South Transfer Station",
        "facility_type": "Municipal transfer station — garbage / bulky / yard waste",
        "city_slug": "seattle",
        "state": "WA",
        "zip": "98108",
        "address": "130 South Kenyon Street, Seattle, WA 98108",
        "lat": 47.5331,
        "lng": -122.3328,
        "source_url": "https://www.seattle.gov/utilities/your-services/collection-and-disposal/transfer-stations/south-station",
        "hours": "Daily 8:00–17:30 (first Wed of month opens 10:00); closed Thanksgiving, Christmas, New Year's Day",
        "phone": "(206) 684-8400",
        "accepted_materials": mats(BULKY, APPLIANCE, ["television", "computer-monitor"], TIRES),
    },
    {
        "name": "Central DPW Facility — Zero Waste Day Drop-Off",
        "facility_type": "Municipal Zero Waste Day event site (HHW / e-waste / tires)",
        "city_slug": "boston",
        "state": "MA",
        "zip": "02118",
        "address": "400 Frontage Road, Lower Roxbury, Boston, MA 02118 (event entrance at 200 Frontage Road)",
        "lat": 42.3412,
        "lng": -71.0609,
        "source_url": "https://www.boston.gov/departments/public-works/zero-waste-day",
        "hours": "Scheduled Zero Waste Days Sat 8:30–12:00 (confirm dates on boston.gov)",
        "phone": "617-635-4500",
        "accepted_materials": mats(
            [
                "paint-oil",
                "motor-oil",
                "gasoline",
                "pesticides",
                "herbicides",
                "fluorescent-bulbs",
                "propane-tank",
                "car-battery",
                "household-batteries",
                "lithium-battery",
            ],
            E_WASTE,
            TIRES,
            ["refrigerator"],
        ),
    },
    {
        "name": "DPW J. Fons Yard — Free Citizen Bulk Drop-Off",
        "facility_type": "Municipal bulk / yard waste drop-off center",
        "city_slug": "detroit",
        "state": "MI",
        "zip": "48211",
        "address": "6451 E. McNichols Street, Detroit, MI 48211",
        "lat": 42.4193,
        "lng": -83.0363,
        "source_url": "https://detroitmi.gov/departments/department-public-works/refuse-collection/bulk-yard-waste/free-citizen-bulk-drop-centers",
        "hours": "Mon–Sat year-round; Mon–Fri 8:00–16:00, Sat 8:00–12:00",
        "phone": "(313) 876-0004",
        "accepted_materials": mats(BULKY, TIRES, ["television", "refrigerator"]),
    },
    {
        "name": "Metro South Transfer Station",
        "facility_type": "Regional transfer station — garbage / bulky / e-waste / HHW",
        "city_slug": "portland",
        "state": "OR",
        "zip": "97045",
        "address": "2001 Washington Street, Oregon City, OR 97045",
        "lat": 45.3695,
        "lng": -122.5907,
        "source_url": "https://www.oregonmetro.gov/waste-disposal-and-prevention/need-get-rid-something/metro-south-transfer-station",
        "hours": "General public daily 8:00–17:00; HHW co-located 9:00–16:00 daily; closed major holidays",
        "phone": "503-234-3000",
        "accepted_materials": mats(
            BULKY,
            APPLIANCE,
            E_WASTE,
            TIRES,
            [
                "motor-oil",
                "antifreeze",
                "paint-latex",
                "paint-oil",
                "pesticides",
                "gasoline",
            ],
        ),
    },
    {
        "name": "Quarantine Road Landfill — Citizen Drop-Off Center",
        "facility_type": "Landfill / residential drop-off — bulky / appliances / e-waste",
        "city_slug": "baltimore",
        "state": "MD",
        "zip": "21226",
        "address": "6100 Quarantine Road, Baltimore, MD 21226",
        "lat": 39.2117,
        "lng": -76.5564,
        "source_url": "https://www.baltimorecity.gov/publicworks/disposal-services",
        "hours": "Mon–Sat 7:30–15:30 (citizen drop-off center)",
        "phone": "410-396-3772",
        "accepted_materials": mats(
            BULKY,
            APPLIANCE,
            ["television", "computer-monitor", "laptop"],
            TIRES,
            ["motor-oil"],
        ),
    },
    {
        "name": "North Drop Off Center",
        "facility_type": "Municipal drop-off — bulky / e-waste / C&D / tires",
        "city_slug": "milwaukee",
        "state": "WI",
        "zip": "53224",
        "address": "6660 N. Industrial Road (enter from Mill Road), Milwaukee, WI 53224",
        "lat": 43.1398,
        "lng": -87.9952,
        "source_url": "https://city.milwaukee.gov/sanitation/DropOff",
        "hours": "Summer Tue–Sun 7:00–15:00; Winter Tue–Sat 7:00–15:00; closed city holidays",
        "phone": "414-286-2489",
        "accepted_materials": mats(
            E_WASTE,
            APPLIANCE,
            BULKY,
            TIRES,
            ["motor-oil", "antifreeze", "car-battery"],
        ),
    },
    {
        "name": "Minneapolis South Transfer Station",
        "facility_type": "Municipal transfer station — garbage / bulky / appliances / e-waste",
        "city_slug": "minneapolis",
        "state": "MN",
        "zip": "55407",
        "address": "2850 20th Avenue South, Minneapolis, MN 55407",
        "lat": 44.9505,
        "lng": -93.2442,
        "source_url": "https://www.minneapolismn.gov/resident-services/garbage-recycling-cleanup/garbage/garbage-drop-off-site/drop-off-items-and-fees/",
        "hours": "Tue–Fri 12:30–19:30; Sat 8:30–15:30; city garbage/water customers (voucher or pay-per-use)",
        "phone": "612-673-2917",
        "accepted_materials": mats(BULKY, APPLIANCE, E_WASTE, TIRES),
    },
    {
        "name": "Sunset Kendall Trash and Recycling Center",
        "facility_type": "County neighborhood TRC — bulky / yard / tires / white goods",
        "city_slug": "miami",
        "state": "FL",
        "zip": "33173",
        "address": "8000 SW 107th Avenue, Miami, FL 33173",
        "lat": 25.6957,
        "lng": -80.3693,
        "source_url": "https://www.miamidade.gov/global/service.page?Mduid_service=ser1464797123341331",
        "hours": "Daily 7:00–17:30; closed select holidays",
        "phone": "311",
        "accepted_materials": mats(BULKY, APPLIANCE, ["television", "computer-monitor"], TIRES),
    },
    {
        "name": "Cherry Creek Recycling and Compost Drop-off",
        "facility_type": "Municipal recycling / compost drop-off",
        "city_slug": "denver",
        "state": "CO",
        "zip": "80231",
        "address": "7400 Cherry Creek South Drive, Denver, CO 80231",
        "lat": 39.6829,
        "lng": -104.9004,
        "source_url": "https://www.denvergov.org/Government/Agencies-Departments-Offices/Agencies-Departments-Offices-Directory/Recycle-Compost-Trash/Recycle/Cherry-Creek-Recycling-and-Compost-Drop-off",
        "hours": "Tue–Fri 9:00–12:00 & 13:00–16:30; Sat 8:00–12:00 & 13:00–15:00; Denver residents only",
        "phone": "720-913-1311",
        # Conservatively e-waste + yard; not a bulk landfill
        "accepted_materials": mats(["yard-waste"], E_WASTE),
    },
    {
        "name": "Foxhole Disposal and Recycling Center",
        "facility_type": "County full-service drop-off — bulky / e-waste / HHW / yard waste",
        "city_slug": "charlotte",
        "state": "NC",
        "zip": "28277",
        "address": "17131 Lancaster Highway, Charlotte, NC 28277",
        "lat": 35.0156,
        "lng": -80.8496,
        "source_url": "https://wipeoutwaste.mecknc.gov/facility/foxhole-disposal-and-recycling-center",
        "hours": "Mon–Sat 7:00–16:00",
        "phone": "980-314-3867",
        "accepted_materials": mats(HHW, E_WASTE, BULKY, APPLIANCE, TIRES),
    },
    {
        "name": "Omohundro Convenience Center",
        "facility_type": "Convenience center — bulky / e-waste / C&D",
        "city_slug": "nashville",
        "state": "TN",
        "zip": "37210",
        "address": "1019 Omohundro Place, Nashville, TN 37210",
        "lat": 36.1556,
        "lng": -86.7392,
        "source_url": "https://www.nashville.gov/departments/waste-services/convenience-centers/hours-and-locations",
        "hours": "Tue–Sat 8:30–16:30; closed Metro holidays; cash not accepted",
        "phone": "(615) 862-5000",
        "accepted_materials": mats(E_WASTE, BULKY, TIRES),
    },
]


def main() -> None:
    facilities = json.loads(FAC_PATH.read_text())
    by_key = {(f.get("city_slug"), f.get("name")): i for i, f in enumerate(facilities)}
    added = updated = 0
    for row in UPSERTS:
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


if __name__ == "__main__":
    main()
