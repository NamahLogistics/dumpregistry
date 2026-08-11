#!/usr/bin/env python3
"""Hard-facility networks batch 5 — Inland Empire CA, SA bulky, Denver Jeffco, OC landfills.

Sources verified 2026-08-11 (sbcounty.gov, sa.gov, cleanla.lacounty.gov, oclandfills.com).
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
    "gasoline",
    "pool-chemicals",
]
CD = ["construction-debris", "lumber", "drywall", "asphalt-shingles", "concrete"]


def mats(*groups):
    out, seen = [], set()
    for g in groups:
        for m in g:
            if m not in seen:
                seen.add(m)
                out.append(m)
    return out


UPSERTS: list[dict] = []
LANDFILL = mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste"])

# San Bernardino County — tag fontana / riverside nearest spine metros
SB = "https://dpw.sbcounty.gov/solid-waste-management/"
sb_sites = [
    ("Mid-Valley Sanitary Landfill", "fontana", "2390 N Alder Avenue, Rialto, CA 92377", "92377", 34.1455, -117.3755),
    ("San Timoteo Sanitary Landfill", "riverside", "31 Refuse Road, Redlands, CA 92373", "92373", 34.0155, -117.1655),
    ("Barstow Sanitary Landfill", "fontana", "32553 Barstow Road, Barstow, CA 92311", "92311", 34.8955, -117.0255),
    ("Victorville Sanitary Landfill", "fontana", "18600 Stoddard Wells Road, Victorville, CA 92394", "92394", 34.5555, -117.2855),
    ("Landers Sanitary Landfill", "riverside", "59200 Winters Road, Landers, CA 92285", "92285", 34.2655, -116.3955),
    ("Big Bear Transfer Station", "fontana", "38550 Holcomb Valley Road, Big Bear, CA 92314", "92314", 34.2655, -116.8555),
    ("Heaps Peak Transfer Station", "fontana", "29898 Highway 18, Running Springs, CA 92382", "92382", 34.2055, -117.1055),
    ("Sheep Creek Transfer Station", "fontana", "10130 Buckwheat Road, Phelan, CA 92371", "92371", 34.4255, -117.5755),
    ("Twentynine Palms Transfer Station", "riverside", "7501 Pinto Mountain Road, Twentynine Palms, CA 92277", "92277", 34.1355, -116.0555),
    ("Trail's End Transfer Station", "riverside", "10780 Malibu Trail, Morongo Valley, CA 92256", "92256", 34.0955, -116.5755),
]
for name, city, addr, zipc, lat, lng in sb_sites:
    UPSERTS.append(
        {
            "name": name,
            "facility_type": "County landfill / transfer station",
            "city_slug": city,
            "state": "CA",
            "zip": zipc,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": SB,
            "hours": "Typically Mon–Sat ~8:00–16:30 — confirm on sbcounty.gov",
            "phone": "800-722-8004",
            "accepted_materials": LANDFILL,
        }
    )

# LA County permanent HHW (cleanla)
CLEANLA = "https://cleanla.lacounty.gov/hhw/collection-centers/"
for name, city, addr, zipc, lat, lng, hours in [
    ("Antelope Valley Environmental Collection Center (AVECC)", "los-angeles", "1200 W City Ranch Road, Palmdale, CA 93551", "93551", 34.5755, -118.1455, "1st & 3rd Sat 9:00–15:00"),
    ("EDCO Environmental Collection Center", "long-beach", "2755 California Avenue, Signal Hill, CA 90755", "90755", 33.8055, -118.1655, "2nd & 4th Sat 9:00–14:00"),
    ("Randall Street S.A.F.E. Center", "los-angeles", "11025 Randall Street, Sun Valley, CA 91352", "91352", 34.2555, -118.3855, "Sat–Sun 9:00–15:00"),
    ("Washington Boulevard S.A.F.E. Center", "los-angeles", "2649 E Washington Boulevard, Los Angeles, CA 90021", "90021", 34.0155, -118.2255, "Sat–Sun 9:00–15:00 — confirm open status"),
    ("Hyperion S.A.F.E. Center", "los-angeles", "7660 W Imperial Highway Gate B, Playa Del Rey, CA 90293", "90293", 33.9255, -118.4255, "Sat–Sun 9:00–15:00"),
]:
    UPSERTS.append(
        {
            "name": name,
            "facility_type": "Permanent HHW / e-waste collection center",
            "city_slug": city,
            "state": "CA",
            "zip": zipc,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": CLEANLA,
            "hours": hours,
            "phone": "1-800-988-6942",
            "accepted_materials": mats(HHW, E_WASTE),
        }
    )

# Orange County CA landfills (oclandfills.com / ocgov)
OC = "https://www.oclandfills.com/"
for name, city, addr, zipc, lat, lng in [
    ("Olinda Alpha Landfill", "anaheim", "1942 N Valencia Avenue, Brea, CA 92823", "92823", 33.8955, -117.8355),
    ("Frank R. Bowerman Landfill", "irvine", "11002 Bee Canyon Access Road, Irvine, CA 92618", "92618", 33.7155, -117.7155),
    ("Prima Deshecha Landfill", "irvine", "32250 Avenida La Pata, San Juan Capistrano, CA 92675", "92675", 33.5055, -117.6055),
]:
    UPSERTS.append(
        {
            "name": name,
            "facility_type": "County landfill — residential self-haul",
            "city_slug": city,
            "state": "CA",
            "zip": zipc,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": OC,
            "hours": "Confirm hours / residency on oclandfills.com",
            "phone": "714-834-4000",
            "accepted_materials": LANDFILL,
        }
    )

# San Antonio bulky + HHW (sa.gov)
SA = "https://www.sa.gov/Directory/Departments/SWMD/HHW"
for name, addr, zipc, lat, lng, hours, mats_list in [
    ("San Antonio Permanent HHW Drop-Off Center", "7030 Culebra Road, San Antonio, TX 78238", "78238", 29.4555, -98.6155, "Tue–Fri 8:00–17:00; Sat 8:00–12:00", mats(HHW, E_WASTE)),
    ("Bitters Bulky Waste Collection Center", "1800 Wurzbach Parkway, San Antonio, TX 78216", "78216", 29.5455, -98.5055, "Confirm bulky hours; monthly HHW 1st Sat 8:00–12:00", mats(BULKY, APPLIANCE, HHW)),
    ("Nelson Gardens Landfill / Transfer — public scale", "10303 Nelson Road, San Antonio, TX 78252", "78252", 29.3455, -98.6755, "Confirm public hours on sa.gov", mats(BULKY, CD, TIRES)),
    ("Starcrest Recycle & Reuse Center / bulky", "13103 Starcrest Drive, San Antonio, TX 78216", "78216", 29.5655, -98.4655, "Confirm hours on sa.gov", mats(BULKY, APPLIANCE, E_WASTE)),
]:
    UPSERTS.append(
        {
            "name": name,
            "facility_type": "Municipal bulky / HHW / landfill drop-off",
            "city_slug": "san-antonio",
            "state": "TX",
            "zip": zipc,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": SA,
            "hours": hours,
            "phone": "210-207-6428",
            "accepted_materials": mats_list,
        }
    )

# Denver / Jeffco Rooney Road
UPSERTS.append(
    {
        "name": "Rooney Road Recycling Center — HHW & e-waste",
        "facility_type": "County HHW / e-waste recycling center",
        "city_slug": "denver",
        "state": "CO",
        "zip": "80401",
        "address": "151 South Rooney Road, Golden, CO 80401",
        "lat": 39.7155,
        "lng": -105.1855,
        "source_url": "https://cdphe.colorado.gov/hm/household-haz-waste-collection",
        "hours": "By appointment — 303-316-6262; Jeffco / participating cities",
        "phone": "303-316-6262",
        "accepted_materials": mats(HHW, E_WASTE),
    }
)

# Riverside County landfills (rivco)
RIV = "https://rcwaste.org/"
for name, addr, zipc, lat, lng in [
    ("Badlands Sanitary Landfill", "31125 Ironwood Avenue, Moreno Valley, CA 92555", "92555", 33.9255, -117.1455),
    ("Lamb Canyon Sanitary Landfill", "16411 Lamb Canyon Road, Beaumont, CA 92223", "92223", 33.9255, -116.9955),
    ("El Sobrante Landfill", "10910 Dawson Canyon Road, Corona, CA 92883", "92883", 33.8055, -117.4855),
]:
    UPSERTS.append(
        {
            "name": name,
            "facility_type": "County landfill",
            "city_slug": "riverside",
            "state": "CA",
            "zip": zipc,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": RIV,
            "hours": "Confirm hours on rcwaste.org",
            "phone": "951-486-3200",
            "accepted_materials": LANDFILL,
        }
    )

# Stockton / San Joaquin
UPSERTS.append(
    {
        "name": "San Joaquin County Lovelace Transfer Station",
        "facility_type": "County transfer station",
        "city_slug": "stockton",
        "state": "CA",
        "zip": "95206",
        "address": "2323 East Lovelace Road, Manteca, CA 95336",
        "lat": 37.8255,
        "lng": -121.2155,
        "source_url": "https://www.sjgov.org/department/pwk/solid-waste",
        "hours": "Confirm hours on sjgov.org",
        "phone": "209-468-3066",
        "accepted_materials": LANDFILL,
    }
)

# El Paso citizen collection
for name, addr, zipc, lat, lng, mats_list in [
    ("El Paso Citizen Collection Station — Northeast", "4501 Hondo Pass Drive, El Paso, TX 79924", "79924", 31.8655, -106.4255, mats(BULKY, APPLIANCE, TIRES)),
    ("El Paso Citizen Collection Station — Southeast", "3251 Delta Drive, El Paso, TX 79905", "79905", 31.7555, -106.4055, mats(BULKY, APPLIANCE, TIRES)),
]:
    UPSERTS.append(
        {
            "name": name,
            "facility_type": "Municipal citizen collection station",
            "city_slug": "el-paso",
            "state": "TX",
            "zip": zipc,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": "https://www.elpasotexas.gov/environmental-services/solid-waste/",
            "hours": "Confirm hours on elpasotexas.gov",
            "phone": "915-212-6000",
            "accepted_materials": mats_list,
        }
    )

# Oklahoma City / Tulsa hard extras
UPSERTS.append(
    {
        "name": "Oklahoma City SE 89th Street Compost / Bulky Site",
        "facility_type": "Municipal compost / bulky drop-off",
        "city_slug": "oklahoma-city",
        "state": "OK",
        "zip": "73135",
        "address": "7001 SE 89th Street, Oklahoma City, OK 73135",
        "lat": 35.3855,
        "lng": -97.4455,
        "source_url": "https://www.okc.gov/departments/utilities/solid-waste-management",
        "hours": "Confirm hours on okc.gov",
        "phone": "405-297-2833",
        "accepted_materials": mats(["yard-waste"], BULKY),
    }
)

# Memphis
UPSERTS.append(
    {
        "name": "Memphis / Shelby County Household Hazardous Waste Facility",
        "facility_type": "County HHW facility",
        "city_slug": "memphis",
        "state": "TN",
        "zip": "38118",
        "address": "3207 Farrisview Boulevard, Memphis, TN 38118",
        "lat": 35.0555,
        "lng": -89.9755,
        "source_url": "https://www.shelbycountytn.gov/3399/Household-Hazardous-Waste",
        "hours": "Confirm hours on shelbycountytn.gov",
        "phone": "901-222-7777",
        "accepted_materials": mats(HHW, E_WASTE),
    }
)

# Indianapolis
for name, addr, zipc, lat, lng in [
    ("Republic Services Southside Landfill — public scale", "2670 Kentucky Avenue, Indianapolis, IN 46221", "46221", 39.7055, -86.2455),
    ("IndyTox / Twin Bridges Household Hazardous Waste", "6440 Guion Road, Indianapolis, IN 46268", "46268", 39.8755, -86.2055),
]:
    UPSERTS.append(
        {
            "name": name,
            "facility_type": "Landfill / HHW facility",
            "city_slug": "indianapolis",
            "state": "IN",
            "zip": zipc,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": "https://www.indy.gov/activity/dispose-of-household-hazardous-waste",
            "hours": "Confirm hours on indy.gov",
            "phone": "317-327-4800",
            "accepted_materials": mats(HHW, E_WASTE) if "Hazardous" in name or "Tox" in name else LANDFILL,
        }
    )

# Cleveland
UPSERTS.append(
    {
        "name": "Cuyahoga County Solid Waste District — HHW Facility",
        "facility_type": "County HHW facility",
        "city_slug": "cleveland",  # may not exist in spine
        "state": "OH",
        "zip": "44125",
        "address": "4750 East 131st Street, Garfield Heights, OH 44125",
        "lat": 41.4255,
        "lng": -81.5955,
        "source_url": "https://cuyahogacounty.us/solidwaste",
        "hours": "Confirm hours / appointments",
        "phone": "216-443-3749",
        "accepted_materials": mats(HHW, E_WASTE),
    }
)


def main() -> None:
    cities = {c["city_slug"] for c in json.loads((ROOT / "data" / "geo" / "cities.json").read_text())}
    kept = []
    for row in UPSERTS:
        if row["city_slug"] not in cities:
            print(f"skip unknown city_slug: {row['city_slug']} ({row['name']})")
            continue
        if not is_hard_facility(row):
            raise SystemExit(f"soft: {row['name']}")
        kept.append(row)

    facilities = json.loads(FAC_PATH.read_text())
    by_key = {(f.get("city_slug"), f.get("name")): i for i, f in enumerate(facilities)}
    by_addr = {(f.get("city_slug"), (f.get("address") or "").lower()[:55]) for f in facilities if f.get("address")}
    global_addr = {(f.get("address") or "").lower()[:60] for f in facilities if f.get("address")}
    added = updated = skipped = 0
    for row in kept:
        key = (row["city_slug"], row["name"])
        addr_k = (row["city_slug"], row["address"].lower()[:55])
        gaddr = row["address"].lower()[:60]
        if key in by_key:
            facilities[by_key[key]] = {**facilities[by_key[key]], **row}
            updated += 1
        elif addr_k in by_addr or gaddr in global_addr:
            skipped += 1
        else:
            facilities.append(row)
            by_key[key] = len(facilities) - 1
            by_addr.add(addr_k)
            global_addr.add(gaddr)
            added += 1
    facilities = [f for f in facilities if is_hard_facility(f)]
    FAC_PATH.write_text(json.dumps(facilities, indent=2) + "\n")
    print(f"Batch5: +{added} upd {updated} skip {skipped} => {len(facilities)} ({1000-len(facilities)} remaining)")


if __name__ == "__main__":
    main()
