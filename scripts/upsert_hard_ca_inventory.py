#!/usr/bin/env python3
"""Hard-facility inventory for California metros already in DumpRegistry.

Official .gov / county solid-waste sources verified 2026-08-11:
- Alameda StopWaste HHW (Hayward, Livermore — completes 4-site network)
- LA County Sanitation Districts landfills & transfer/MRF
- Santa Clara County HHW (San Martin permanent facility)
- Sacramento County WMR (NARS HHW, Kiefer ABOP)
- San Bernardino County Fire HHW (Ontario, Central, Rancho Cucamonga, Chino)
- SF Environment / Recology transfer station
- Contra Costa County HHW (West County — Richmond)
- Riverside County Waste Resources (Moreno Valley transfer station listing)
- Kern County Public Works (Tehachapi Transfer Station)
- LA County Public Health (Culver City transfer/recycling station)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.facility_quality import is_hard_facility  # noqa: E402

FAC_PATH = ROOT / "data" / "facilities" / "all.json"
CITIES_PATH = ROOT / "data" / "geo" / "cities.json"

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


STOPWASTE_HHW = mats(
    HHW, E_WASTE, ["microwave", "lithium-battery", "gasoline", "pool-chemicals"]
)
SCC_HHW = mats(HHW, E_WASTE, ["microwave", "smartphone", "medical-sharps"])
SB_HHW = mats(HHW, E_WASTE, ["microwave", "smartphone"])
TRANSFER = mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste"])
LANDFILL = mats(BULKY, CD, ["yard-waste"], TIRES)
SF_TRANSFER = mats(BULKY, APPLIANCE, E_WASTE, ["car-battery", "fluorescent-bulbs", "carpet"])

UPSERTS: list[dict] = [
    # --- Alameda StopWaste HHW (stopwaste.org) — Hayward & Livermore complete the 4-site network ---
    {
        "name": "Alameda County HHW — Hayward Facility",
        "facility_type": "County HHW drop-off — paint / chemicals / e-waste",
        "city_slug": "oakland",
        "state": "CA",
        "zip": "94544",
        "address": "2091 West Winton Ave., Hayward, CA 94544",
        "lat": 37.653,
        "lng": -122.134,
        "source_url": "https://www.stopwaste.org/recycling-disposal/hazardous-waste/household-hazardous-waste/drop-off-facilities",
        "hours": "Thu–Fri 9:00–14:30; Sat 9:00–16:00; closed Sun–Wed",
        "phone": "1-800-606-6606",
        "accepted_materials": STOPWASTE_HHW,
    },
    {
        "name": "Alameda County HHW — Livermore Facility",
        "facility_type": "County HHW drop-off — paint / chemicals / e-waste",
        "city_slug": "fremont",
        "state": "CA",
        "zip": "94550",
        "address": "5584 La Ribera St., Livermore, CA 94550",
        "lat": 37.699,
        "lng": -121.725,
        "source_url": "https://www.stopwaste.org/recycling-disposal/hazardous-waste/household-hazardous-waste/drop-off-facilities",
        "hours": "Thu–Fri 9:00–14:30; Sat 9:00–16:00; closed Sun–Wed",
        "phone": "1-800-606-6606",
        "accepted_materials": STOPWASTE_HHW,
    },
    # --- LA County Sanitation Districts (lacsd.org) ---
    {
        "name": "Calabasas Landfill",
        "facility_type": "County landfill — green waste / C&D / inert",
        "city_slug": "glendale",
        "state": "CA",
        "zip": "91301",
        "address": "5300 Lost Hills Road, Agoura, CA 91301",
        "lat": 34.146,
        "lng": -118.706,
        "source_url": "https://www.lacsd.org/services/solid-waste/facilities/calabasas-landfill",
        "hours": "Mon–Fri 8:00–17:00; Sat per site; closed Sun & holidays",
        "phone": "562-908-4288",
        "accepted_materials": LANDFILL,
    },
    {
        "name": "Scholl Canyon Landfill",
        "facility_type": "County landfill — green waste / asphalt / clean dirt",
        "city_slug": "glendale",
        "state": "CA",
        "zip": "90041",
        "address": "7721 North Figueroa Street, Los Angeles, CA 90041",
        "lat": 34.145,
        "lng": -118.186,
        "source_url": "https://www.lacsd.org/services/solid-waste/facilities/scholl-canyon-landfill",
        "hours": "Mon–Fri 8:00–17:00; Sat 8:00–15:30; closed Sun & holidays",
        "phone": "818-243-9779",
        "accepted_materials": mats(CD, ["yard-waste", "concrete"]),
    },
    {
        "name": "South Gate Transfer Station",
        "facility_type": "County transfer station — municipal solid & inert waste",
        "city_slug": "los-angeles",
        "state": "CA",
        "zip": "90280",
        "address": "9530 Garfield Avenue, South Gate, CA 90280",
        "lat": 33.944,
        "lng": -118.166,
        "source_url": "https://www.lacsd.org/services/solid-waste/facilities/south-gate-transfer-station",
        "hours": "Mon–Sat 6:00–17:00; closed Sun & holidays",
        "phone": "562-908-4288",
        "accepted_materials": TRANSFER,
    },
    {
        "name": "Puente Hills Materials Recovery Facility",
        "facility_type": "County MRF / transfer — green waste / MSW consolidation",
        "city_slug": "los-angeles",
        "state": "CA",
        "zip": "90601",
        "address": "2808 S Workman Mill Road, Whittier, CA 90601",
        "lat": 34.001,
        "lng": -118.056,
        "source_url": "http://www.publichealth.lacounty.gov/eh/business/landfill-transfer-stations.htm",
        "hours": "Mon–Sat; call 562-908-4288 for current hours",
        "phone": "562-908-4288",
        "accepted_materials": mats(["yard-waste"], CD, BULKY),
    },
    {
        "name": "Culver City Transfer and Recycling Station",
        "facility_type": "Municipal transfer / recycling station — bulky / C&D",
        "city_slug": "los-angeles",
        "state": "CA",
        "zip": "90232",
        "address": "9255 W Jefferson Boulevard, Culver City, CA 90232",
        "lat": 34.026,
        "lng": -118.397,
        "source_url": "http://www.publichealth.lacounty.gov/eh/business/landfill-transfer-stations.htm",
        "hours": "Mon–Sat; call 310-253-6405 for current hours",
        "phone": "310-253-6405",
        "accepted_materials": TRANSFER,
    },
    # --- Santa Clara County HHW (hhw.santaclaracounty.gov) ---
    {
        "name": "Santa Clara County HHW — San Martin Facility",
        "facility_type": "County HHW collection facility (appointment required)",
        "city_slug": "san-jose",
        "state": "CA",
        "zip": "95046",
        "address": "13055 Murphy Avenue, San Martin, CA 95046",
        "lat": 37.085,
        "lng": -121.601,
        "source_url": "https://hhw.santaclaracounty.gov/drop-household-waste",
        "hours": "Thu–Sat by appointment; call 408-299-7300",
        "phone": "408-299-7300",
        "accepted_materials": SCC_HHW,
    },
    # --- Sacramento County WMR (wmr.saccounty.gov) ---
    {
        "name": "NARS Household Hazardous Waste Facility",
        "facility_type": "County HHW drop-off at North Area Recovery Station",
        "city_slug": "sacramento",
        "state": "CA",
        "zip": "95660",
        "address": "4450 Roseville Road, North Highlands, CA 95660",
        "lat": 38.641,
        "lng": -121.384,
        "source_url": "https://wmr.saccounty.gov/Pages/Contact-Us.aspx",
        "hours": "Tue, Thu, Fri, Sat 8:30–16:00; closed holidays",
        "phone": "916-875-5555",
        "accepted_materials": mats(HHW, E_WASTE, ["gasoline", "pesticides", "medical-sharps"]),
    },
    {
        "name": "Kiefer ABOP & Special Waste Facility",
        "facility_type": "County ABOP / special waste — paint, oil, batteries",
        "city_slug": "sacramento",
        "state": "CA",
        "zip": "95683",
        "address": "12701 Kiefer Boulevard, Sloughhouse, CA 95683",
        "lat": 38.451,
        "lng": -121.183,
        "source_url": "https://wmr.saccounty.gov/Pages/Contact-Us.aspx",
        "hours": "Tue–Sat 8:30–16:00; closed Thanksgiving, Christmas, New Year's",
        "phone": "916-875-5555",
        "accepted_materials": mats(
            ["paint-latex", "paint-oil", "motor-oil", "antifreeze", "car-battery", "household-batteries"]
        ),
    },
    # --- San Bernardino County Fire HHW (sbcfire.org) ---
    {
        "name": "San Bernardino County HHW — Ontario Facility",
        "facility_type": "County HHW collection center — e-waste / sharps",
        "city_slug": "fontana",
        "state": "CA",
        "zip": "91761",
        "address": "1430 South Cucamonga Avenue, Ontario, CA 91761",
        "lat": 34.048,
        "lng": -117.633,
        "source_url": "https://sbcfire.org/collectionfacilities/",
        "hours": "Fri–Sat 9:00–14:00",
        "phone": "1-800-645-9228",
        "accepted_materials": SB_HHW,
    },
    {
        "name": "San Bernardino County HHW — Central Facility",
        "facility_type": "County central HHW — e-waste / sharps / reuse exchange",
        "city_slug": "fontana",
        "state": "CA",
        "zip": "92408",
        "address": "2824 East W Street, San Bernardino, CA 92408",
        "lat": 34.104,
        "lng": -117.225,
        "source_url": "https://sbcfire.org/collectionfacilities/",
        "hours": "Mon–Fri 9:00–16:00",
        "phone": "909-382-5401",
        "accepted_materials": SB_HHW,
    },
    {
        "name": "San Bernardino County HHW — Rancho Cucamonga Facility",
        "facility_type": "County HHW collection center — e-waste / sharps",
        "city_slug": "fontana",
        "state": "CA",
        "zip": "91730",
        "address": "8794 Lion Street, Rancho Cucamonga, CA 91730",
        "lat": 34.094,
        "lng": -117.605,
        "source_url": "https://sbcfire.org/collectionfacilities/",
        "hours": "Sat 8:00–12:00",
        "phone": "909-919-2635",
        "accepted_materials": SB_HHW,
    },
    {
        "name": "San Bernardino County HHW — Chino Facility",
        "facility_type": "County HHW collection center — e-waste / sharps",
        "city_slug": "fontana",
        "state": "CA",
        "zip": "91710",
        "address": "5050 Schaefer Avenue, Chino, CA 91710",
        "lat": 34.012,
        "lng": -117.687,
        "source_url": "https://sbcfire.org/collectionfacilities/",
        "hours": "2nd & 4th Sat 8:00–13:00",
        "phone": "909-334-3266",
        "accepted_materials": SB_HHW,
    },
    # --- SF Environment / Recology (sfenvironment.org) ---
    {
        "name": "Recology San Francisco Transfer Station",
        "facility_type": "Municipal transfer station — bulky / appliances / e-waste / C&D",
        "city_slug": "san-francisco",
        "state": "CA",
        "zip": "94134",
        "address": "501 Tunnel Avenue, San Francisco, CA 94134",
        "lat": 37.732,
        "lng": -122.386,
        "source_url": "https://www.sfenvironment.org/sfrecycles/vendor/recology-san-francisco-transfer-station-public-dump",
        "hours": "Mon–Fri 7:00–16:30; Sat–Sun 7:30–16:00",
        "phone": "415-330-1400",
        "accepted_materials": SF_TRANSFER,
    },
    # --- Contra Costa County (cccrecycle.org) ---
    {
        "name": "West Contra Costa HHW Collection Facility",
        "facility_type": "County HHW drop-off — paint / chemicals / e-waste",
        "city_slug": "richmond",
        "state": "CA",
        "zip": "94801",
        "address": "101 Pittsburg Avenue, Richmond, CA 94801",
        "lat": 37.963,
        "lng": -122.376,
        "source_url": "https://cccrecycle.org/218/Dispose-of-Household-Hazardous-Waste",
        "hours": "Call 888-412-9277 for current drop-off hours",
        "phone": "888-412-9277",
        "accepted_materials": mats(HHW, E_WASTE, ["microwave"]),
    },
    # --- Riverside County Waste Resources (rcwaste.org) ---
    {
        "name": "Moreno Valley Transfer Station",
        "facility_type": "County-listed transfer station — household / C&D self-haul",
        "city_slug": "riverside",
        "state": "CA",
        "zip": "92551",
        "address": "17700 Indian Street, Moreno Valley, CA 92551",
        "lat": 33.865,
        "lng": -117.235,
        "source_url": "https://rcwaste.org/routine-waste",
        "hours": "Call 951-242-0421 for current hours and fees",
        "phone": "951-242-0421",
        "accepted_materials": TRANSFER,
    },
    # --- Kern County Public Works (kernpublicworks.com) ---
    {
        "name": "Tehachapi Transfer Station",
        "facility_type": "County transfer station — household self-haul",
        "city_slug": "bakersfield",
        "state": "CA",
        "zip": "93561",
        "address": "12001 Tehachapi Boulevard, Tehachapi, CA 93561",
        "lat": 35.133,
        "lng": -118.455,
        "source_url": "https://www.kernpublicworks.com/services/solid-waste/disposal-sites",
        "hours": "Sat 8:00–12:00; HHW events on select dates — call ahead",
        "phone": "661-862-8900",
        "accepted_materials": mats(BULKY, CD, ["yard-waste"], TIRES),
    },
]

NETWORKS = [
    "Alameda StopWaste HHW (Hayward + Livermore)",
    "LA County Sanitation Districts (Calabasas, Scholl Canyon, South Gate, Puente Hills MRF)",
    "LA County Public Health transfer stations (Culver City)",
    "Santa Clara County HHW (San Martin)",
    "Sacramento County WMR (NARS HHW, Kiefer ABOP)",
    "San Bernardino County Fire HHW (Ontario, Central, Rancho Cucamonga, Chino)",
    "SF Environment / Recology transfer station",
    "Contra Costa County HHW (West County — Richmond)",
    "Riverside County Waste Resources (Moreno Valley transfer)",
    "Kern County Public Works (Tehachapi Transfer Station)",
]


def valid_city_slugs() -> set[str]:
    cities = json.loads(CITIES_PATH.read_text())
    slugs = {c["city_slug"] for c in cities}
    for row in json.loads(FAC_PATH.read_text()):
        if row.get("city_slug"):
            slugs.add(row["city_slug"])
    return slugs


def main() -> None:
    allowed = valid_city_slugs()
    for row in UPSERTS:
        if row["city_slug"] not in allowed:
            raise SystemExit(f"unknown city_slug: {row['city_slug']} ({row['name']})")
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

    facilities = [f for f in facilities if is_hard_facility(f)]
    FAC_PATH.write_text(json.dumps(facilities, indent=2) + "\n")

    ca_metros = {
        "oakland", "fremont", "san-francisco", "san-jose", "san-diego", "chula-vista",
        "los-angeles", "anaheim", "irvine", "sacramento", "fresno", "bakersfield",
        "riverside", "fontana", "glendale", "richmond", "long-beach",
    }
    ca_hard = [f for f in facilities if f.get("city_slug") in ca_metros and is_hard_facility(f)]
    total_hard = len(facilities)

    print(f"Added: {added} | Updated: {updated} | Skipped (addr dedupe): {skipped}")
    print(f"CA metro hard facilities: {len(ca_hard)}")
    print(f"Total hard facilities: {total_hard}")
    print("Networks covered:")
    for n in NETWORKS:
        print(f"  - {n}")


if __name__ == "__main__":
    main()
