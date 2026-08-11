#!/usr/bin/env python3
"""Authentic finder growth: verified secondary drop-offs + enrich accepted_materials.

Portal-sourced only (2026-08-11). Places/API candidates not used — verified .gov paths.
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
BULKY = ["mattress", "box-spring", "sofa", "recliner", "carpet"]
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


# Upsert by (city_slug, name)
UPSERTS = [
    # --- enrich existing ---
    {
        "name": "El Paso County HHW",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "colorado-springs",
        "state": "CO",
        "zip": "80922",
        "address": "3255 Akers Dr, Colorado Springs, CO 80922",
        "lat": 38.876,
        "lng": -104.716,
        "source_url": "https://communityresources.elpasoco.com/environmental-division/household-hazardous-waste/",
        "hours": "Mon/Tue/Thu/Fri 8:30–12:00 & 13:00–16:00; limited Sat dates — check county page",
        "phone": "719-520-7878",
        "accepted_materials": mats(HHW, ["television"], ["e-waste-mixed"]),
    },
    {
        "name": "Sedgwick County HHW",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "wichita",
        "state": "KS",
        "zip": "67213",
        "address": "801 Stillwell St, Wichita, KS 67213",
        "lat": 37.6705,
        "lng": -97.3555,
        "source_url": "https://www.sedgwickcounty.org/environment/recycling-guide/",
        "hours": "Tue–Fri 9:00–17:00; Sat 9:00–15:00",
        "phone": "316-660-7458",
        "accepted_materials": mats(HHW),
    },
    {
        "name": "Fort Worth Environmental Collection Center",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "arlington",
        "state": "TX",
        "zip": "76112",
        "address": "6400 Bridge St, Fort Worth, TX 76112",
        "lat": 32.7555,
        "lng": -97.2455,
        "source_url": "https://www.fortworthtexas.gov/departments/code-compliance/household-hazardous-waste",
        "hours": "Thu–Fri 11:00–19:00; Sat 9:00–15:00; Arlington residents 1 visit/month",
        "phone": "",
        "accepted_materials": mats(HHW),
    },
    {
        "name": "New Orleans Recycling Drop-Off Center",
        "facility_type": "Recycling drop-off / HHW event days",
        "city_slug": "new-orleans",
        "state": "LA",
        "zip": "70122",
        "address": "2829 Elysian Fields Ave, New Orleans, LA 70122",
        "lat": 29.9885,
        "lng": -90.0555,
        "source_url": "https://nola.gov/recycling-drop-off/",
        "hours": "Sat 8:00–13:00 recycling/e-waste; HHW chemicals on designated event Saturdays only",
        "phone": "311",
        "accepted_materials": mats(E_WASTE, TIRES, HHW),
    },
    {
        "name": "Hillsborough County HHW — Sheldon Rd",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "tampa",
        "state": "FL",
        "zip": "33615",
        "address": "9805 Sheldon Rd, Tampa, FL 33615",
        "lat": 28.0455,
        "lng": -82.5825,
        "source_url": "https://hcfl.gov/residents/property-owners-and-renters/trash-and-recycling/discarding-household-hazardous-waste",
        "hours": "1st Saturday each month 8:00–14:00 (rotating county schedule)",
        "phone": "813-272-5680",
        "accepted_materials": mats(HHW),
    },
    {
        "name": "McKay Bay Scale House",
        "facility_type": "City drop-off — bulky / appliances",
        "city_slug": "tampa",
        "state": "FL",
        "zip": "33605",
        "address": "114 S 34th St, Tampa, FL 33605",
        "lat": 27.9455,
        "lng": -82.4155,
        "source_url": "https://www.tampa.gov/solid-waste/info/mckay-bay/mckay-bay-scalehouse",
        "hours": "Confirm on city page; Tampa utility account + ID required",
        "phone": "813-242-5320",
        "accepted_materials": mats(BULKY, APPLIANCE),
    },
    # --- new sites ---
    {
        "name": "Colorado Springs Landfill (Waste Management)",
        "facility_type": "Landfill — bulky / Freon appliances / tires (fees)",
        "city_slug": "colorado-springs",
        "state": "CO",
        "zip": "80929",
        "address": "1010 Blaney Rd, Colorado Springs, CO 80929",
        "lat": 38.878,
        "lng": -104.719,
        "source_url": "https://admin.elpasoco.com/winter-wind-resources/",
        "hours": "Mon–Fri 7:00–17:00; Sat 7:00–15:00 — call to confirm fees",
        "phone": "719-683-2600",
        "accepted_materials": mats(BULKY, APPLIANCE, TIRES),
    },
    {
        "name": "Brooks Landfill",
        "facility_type": "Landfill — mattress / Freon appliances / tires / e-waste (fees)",
        "city_slug": "wichita",
        "state": "KS",
        "zip": "67205",
        "address": "4100 N West St, Wichita, KS 67205",
        "lat": 37.722,
        "lng": -97.389,
        "source_url": "https://www.wichita.gov/712/Brooks-Landfill",
        "hours": "Mar–Oct Mon–Fri 7:30–17:00 Sat 8:00–12:00; winter hours shorter",
        "phone": "316-350-3225",
        "accepted_materials": mats(BULKY, APPLIANCE, TIRES, E_WASTE),
    },
    {
        "name": "Arlington Landfill",
        "facility_type": "City landfill — bulky / tires / appliances",
        "city_slug": "arlington",
        "state": "TX",
        "zip": "76040",
        "address": "800 Mosier Valley Rd, Euless, TX 76040",
        "lat": 32.823,
        "lng": -97.078,
        "source_url": "https://www.arlingtontx.gov/News-Articles/2026/June/Arlington-Residents-Get-3-Free-Landfill-Drop-Offs-Per-Year",
        "hours": "Mon–Sat 7:00–16:30; 3 free visits/year with water account + TX ID",
        "phone": "817-354-2305",
        "accepted_materials": mats(BULKY, APPLIANCE, TIRES),
    },
    {
        "name": "Northwest County Solid Waste Facility (CCC)",
        "facility_type": "Hillsborough County Community Collection Center",
        "city_slug": "tampa",
        "state": "FL",
        "zip": "33625",
        "address": "8001 W Linebaugh Ave, Tampa, FL 33625",
        "lat": 28.040,
        "lng": -82.572,
        "source_url": "https://hcfl.gov/residents/property-owners-and-renters/trash-and-recycling/discarding-paint-and-electronics",
        "hours": "Mon–Sat 7:30–17:00",
        "phone": "813-272-5680",
        "accepted_materials": mats(E_WASTE, ["paint-latex", "paint-oil"], TIRES),
    },
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
        "phone": "713-551-7355",
        "accepted_materials": mats(BULKY, APPLIANCE, TIRES, ["motor-oil"]),
    },
    {
        "name": "27th Avenue Transfer Station",
        "facility_type": "City transfer station — appliances / CRT TVs / tires",
        "city_slug": "phoenix",
        "state": "AZ",
        "zip": "85009",
        "address": "3060 S 27th Ave, Phoenix, AZ 85009",
        "lat": 33.418,
        "lng": -112.088,
        "source_url": "https://www.phoenix.gov/administration/departments/publicworks/about-us/transfer-stations.html",
        "hours": "Mon–Fri 5:30–17:00; Sat 6:00–15:00",
        "phone": "(602) 262-7251",
        "accepted_materials": mats(["television"], APPLIANCE, TIRES),
    },
    {
        "name": "CHaRM (Center for Hard to Recycle Materials)",
        "facility_type": "Hard-to-recycle drop-off (appointment; fees)",
        "city_slug": "atlanta",
        "state": "GA",
        "zip": "30315",
        "address": "1110 Hill St SE, Atlanta, GA 30315",
        "lat": 33.731,
        "lng": -84.377,
        "source_url": "https://www.fultoncountyga.gov/services/water-services/public-education-and-outreach/pollution-prevention",
        "hours": "By appointment — check livethrive.org/charm",
        "phone": "404-600-6386",
        "accepted_materials": mats(
            ["paint-latex", "paint-oil", "pesticides", "motor-oil", "fluorescent-bulbs", "propane-tank"],
            E_WASTE,
            BULKY,
            TIRES,
        ),
    },
    {
        "name": "Southwest Sanitation Convenience Center",
        "facility_type": "City sanitation convenience center",
        "city_slug": "philadelphia",
        "state": "PA",
        "zip": "19153",
        "address": "3033 S 63rd St, Philadelphia, PA 19153",
        "lat": 39.905,
        "lng": -75.225,
        "source_url": "https://www.phila.gov/services/trash-recycling-city-upkeep/find-a-sanitation-convenience-center-to-drop-off-trash-or-recycling/",
        "hours": "Mon–Sat 8:00–18:00",
        "phone": "215-685-4290",
        "accepted_materials": mats(
            E_WASTE,
            BULKY,
            APPLIANCE,
            TIRES,
            ["household-batteries", "fluorescent-bulbs", "paint-latex"],
        ),
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

    # Tag any remaining untagged HHW-ish rows
    for f in facilities:
        if f.get("accepted_materials"):
            continue
        t = (f.get("facility_type") or "").lower()
        if "hhw" in t or "hazard" in t:
            f["accepted_materials"] = mats(HHW)
        elif "e-waste" in t or "electronics" in t or "cyber" in t:
            f["accepted_materials"] = mats(E_WASTE)
        elif "bulky" in t or "convenience" in t or "transfer" in t or "landfill" in t:
            f["accepted_materials"] = mats(BULKY, APPLIANCE)

    FAC_PATH.write_text(json.dumps(facilities, indent=2) + "\n")
    print(f"Facilities: {len(facilities)} (added {added}, updated {updated})")


if __name__ == "__main__":
    main()
