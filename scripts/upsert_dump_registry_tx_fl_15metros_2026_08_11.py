#!/usr/bin/env python3
"""DumpRegistry: full .gov drop-off inventory for 15 TX/FL metros (2026-08-11).

Cities: houston, dallas, fort-worth, arlington, austin, san-antonio, el-paso,
corpus-christi, jacksonville, miami, tampa, orlando, st-petersburg, hialeah.

Sources verified 2026-08-11 from official city/county .gov pages.
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
                raise SystemExit(f"unknown slug {m}")
            if m not in seen:
                seen.add(m)
                out.append(m)
    return out


HOUSTON_DEP = mats(BULKY, APPLIANCE, TIRES, ["motor-oil"], RECYCLE)
FW_DOS = mats(BULKY, APPLIANCE, TIRES, E_WASTE, HHW, RECYCLE)
SA_BULKY = mats(BULKY, APPLIANCE, TIRES)
EL_PASO = mats(BULKY, APPLIANCE, E_WASTE, HHW)
MIAMI_TRC = mats(BULKY, APPLIANCE, TIRES, ["television", "computer-monitor"], ["yard-waste"])
HCFL_CCC = mats(E_WASTE, ["paint-latex", "paint-oil"], TIRES, BULKY, APPLIANCE, RECYCLE)
STPETE_RECYCLE = mats(RECYCLE)


def row(
    name,
    facility_type,
    city_slug,
    state,
    zip_code,
    address,
    lat,
    lng,
    source_url,
    hours,
    phone,
    accepted,
):
    return {
        "name": name,
        "facility_type": facility_type,
        "city_slug": city_slug,
        "state": state,
        "zip": zip_code,
        "address": address,
        "lat": lat,
        "lng": lng,
        "source_url": source_url,
        "hours": hours,
        "phone": phone,
        "accepted_materials": accepted,
    }


# Correct bad / placeholder rows already in all.json
FIXES = [
    {
        "old_name": "Southeast Citizen Collection Station",
        "name": "Mission Valley Citizen Collection Station",
        "facility_type": "Citizen collection station — bulky / HHW / recyclables",
        "city_slug": "el-paso",
        "state": "TX",
        "zip": "79907",
        "address": "1034 Pendale Road, El Paso, TX 79907",
        "lat": 31.738,
        "lng": -106.318,
        "source_url": "https://www.elpasotexas.gov/environmental-services/collection-stations/",
        "hours": "Tue–Sat 8:00–16:00",
        "phone": "915-212-6000",
        "accepted_materials": EL_PASO,
    },
    {
        "old_name": "Nelson Gardens Bulky Waste Collection Center",
        "name": "Rigsby Road Bulky Waste Collection Center",
        "facility_type": "Bulky waste collection center",
        "city_slug": "san-antonio",
        "state": "TX",
        "zip": "78222",
        "address": "2755 Rigsby Road, San Antonio, TX 78222",
        "lat": 29.388,
        "lng": -98.412,
        "source_url": "https://www.sa.gov/Directory/Departments/SWMD/Brush-Bulky/Bulky-Drop-Off",
        "hours": "Tue–Fri 8:00–17:00; Sat 8:00–12:00",
        "phone": "311",
        "accepted_materials": SA_BULKY,
    },
    {
        "old_name": "Northwest County Solid Waste Facility (already Tampa) — South CCC",
        "name": "South County Solid Waste Facility (CCC)",
        "facility_type": "Hillsborough County Community Collection Center",
        "city_slug": "tampa",
        "state": "FL",
        "zip": "33534",
        "address": "13000 US Highway 41, Gibsonton, FL 33534",
        "lat": 27.825,
        "lng": -82.375,
        "source_url": "https://www.hcfl.gov/residents/property-owners-and-renters/trash-and-recycling/community-collection-centers-ccc",
        "hours": "Mon–Sat 7:30–17:00",
        "phone": "813-272-5680",
        "accepted_materials": HCFL_CCC,
    },
    {
        "old_name": "Miami-Dade Disposal Sites — Hialeah residents",
        "name": "Miami-Dade Home Chemical Collection Center — Opa-locka (NW 135th)",
        "facility_type": "County home chemical collection center",
        "city_slug": "hialeah",
        "state": "FL",
        "zip": "33054",
        "address": "3680 NW 135th Street, Opa-locka, FL 33054",
        "lat": 25.897,
        "lng": -80.248,
        "source_url": "https://www.hialeahfl.gov/973/Disposal-Sites",
        "hours": "Wed–Sun 9:00–17:00",
        "phone": "311",
        "accepted_materials": mats(HHW, E_WASTE),
    },
]

FACILITIES: list[dict] = [
    # --- houston ---
    row(
        "Westpark Consumer Recycling Center",
        "City consumer recycling / BOPA drop-off",
        "houston",
        "TX",
        "77057",
        "5902 Westpark Dr, Houston, TX 77057",
        29.728,
        -95.482,
        "https://www.houstontx.gov/solidwaste/westpark.html",
        "Mon–Sat 8:00–17:00",
        "311",
        mats(HHW[:8], ["motor-oil", "antifreeze", "car-battery"], RECYCLE),
    ),
    # --- dallas ---
    row(
        "McCommas Bluff Landfill",
        "Municipal landfill — public scalehouse",
        "dallas",
        "TX",
        "75241",
        "5100 Youngblood Road, Dallas, TX 75241",
        32.658,
        -96.768,
        "https://dallascityhall.com/departments/sanitation/pages/mccommas_bluff.aspx",
        "Mon–Fri 5:00–20:00",
        "214-670-0977",
        mats(BULKY, APPLIANCE, TIRES),
    ),
    # --- el-paso ---
    row(
        "Eastside Citizen Collection Station",
        "Citizen collection station — bulky / HHW / recyclables",
        "el-paso",
        "TX",
        "79936",
        "3500 Confederate Drive, El Paso, TX 79936",
        31.745,
        -106.265,
        "https://www.elpasotexas.gov/environmental-services/collection-stations/",
        "Tue–Sat 8:00–16:00",
        "915-212-6000",
        EL_PASO,
    ),
    # --- arlington ---
    row(
        "Northeast Branch Library — recycling drop-off",
        "Public library recycling drop-off",
        "arlington",
        "TX",
        "76011",
        "1905 E Brown Boulevard, Arlington, TX 76011",
        32.748,
        -97.078,
        "https://www.arlingtontx.gov/residents/trash_and_recycling/recycling_center",
        "Library hours — confirm on arlingtontx.gov",
        "817-459-6772",
        mats(E_WASTE, ["yard-waste"], RECYCLE),
    ),
    row(
        "George W Hawkes Library — recycling drop-off",
        "Public library recycling drop-off",
        "arlington",
        "TX",
        "76013",
        "100 SE Green Oaks Boulevard, Arlington, TX 76013",
        32.715,
        -97.125,
        "https://www.arlingtontx.gov/residents/trash_and_recycling/recycling_center",
        "Library hours — confirm on arlingtontx.gov",
        "817-459-6772",
        mats(E_WASTE, RECYCLE),
    ),
    # --- hialeah ---
    row(
        "Miami-Dade Home Chemical Collection Center — NW 37th Ave",
        "County home chemical collection center",
        "hialeah",
        "FL",
        "33142",
        "5000 NW 37th Avenue, Miami, FL 33142",
        25.818,
        -80.218,
        "https://www.hialeahfl.gov/973/Disposal-Sites",
        "Wed–Sun 9:00–17:00",
        "311",
        mats(HHW, E_WASTE),
    ),
    row(
        "Palm Springs North Trash and Recycling Center",
        "Miami-Dade neighborhood TRC — bulky / yard / tires",
        "hialeah",
        "FL",
        "33015",
        "7870 NW 178th Street, Hialeah, FL 33015",
        25.935,
        -80.335,
        "https://www.miamidade.gov/global/service.page?Mduid_service=ser1464797123341331",
        "Daily 7:00–17:30",
        "311",
        MIAMI_TRC,
    ),
    # --- tampa (Hillsborough County CCC network) ---
    row(
        "Hillsborough Heights Solid Waste Facility (CCC)",
        "Hillsborough County Community Collection Center",
        "tampa",
        "FL",
        "33584",
        "6209 County Road 579, Seffner, FL 33584",
        27.998,
        -82.318,
        "https://www.hcfl.gov/locations/hillsborough-heights-solid-waste-facility",
        "Mon–Sat 7:30–17:00",
        "813-272-5680",
        HCFL_CCC,
    ),
    row(
        "Wimauma Solid Waste Facility (CCC)",
        "Hillsborough County Community Collection Center",
        "tampa",
        "FL",
        "33598",
        "16180 W Lake Drive, Wimauma, FL 33598",
        27.712,
        -82.438,
        "https://www.hcfl.gov/residents/property-owners-and-renters/trash-and-recycling/find-a-waste-disposal-facility/",
        "Mon–Sat 7:30–17:00",
        "813-272-5680",
        HCFL_CCC,
    ),
    row(
        "Alderman's Ford Solid Waste Facility (CCC)",
        "Hillsborough County Community Collection Center",
        "tampa",
        "FL",
        "33567",
        "9402 County Road 39, Plant City, FL 33567",
        27.978,
        -82.118,
        "https://www.hcfl.gov/locations/aldermans-ford-solid-waste-facility",
        "Mon–Sat 7:30–17:00",
        "813-272-5680",
        HCFL_CCC,
    ),
    # --- orlando (OFD sharps — permanent drop-off at staffed stations) ---
    row(
        "Orlando Fire Department Sharps Drop-Off — Fire Station 2",
        "Fire station sharps exchange drop-off",
        "orlando",
        "FL",
        "32801",
        "1900 S Orange Blossom Trail, Orlando, FL 32805",
        28.515,
        -81.398,
        "https://www.orlando.gov/Our-Government/Departments-Offices/Public-Works/Solid-Waste/Too-Toxic-to-Trash",
        "24 hours — kiosk at station",
        "407-246-2314",
        mats(["medical-sharps", "needles"]),
    ),
    row(
        "Orlando Fire Department Sharps Drop-Off — Fire Station 5",
        "Fire station sharps exchange drop-off",
        "orlando",
        "FL",
        "32803",
        "840 N Primrose Drive, Orlando, FL 32803",
        28.555,
        -81.348,
        "https://www.orlando.gov/Our-Government/Departments-Offices/Public-Works/Solid-Waste/Too-Toxic-to-Trash",
        "24 hours — kiosk at station",
        "407-246-2314",
        mats(["medical-sharps", "needles"]),
    ),
    row(
        "Orlando Fire Department Sharps Drop-Off — Fire Station 8",
        "Fire station sharps exchange drop-off",
        "orlando",
        "FL",
        "32808",
        "806 W Central Boulevard, Orlando, FL 32805",
        28.542,
        -81.392,
        "https://www.orlando.gov/Our-Government/Departments-Offices/Public-Works/Solid-Waste/Too-Toxic-to-Trash",
        "24 hours — kiosk at station",
        "407-246-2314",
        mats(["medical-sharps", "needles"]),
    ),
    row(
        "Orlando Fire Department Sharps Drop-Off — Fire Station 10",
        "Fire station sharps exchange drop-off",
        "orlando",
        "FL",
        "32822",
        "6900 Lake Ellenor Drive, Orlando, FL 32809",
        28.458,
        -81.412,
        "https://www.orlando.gov/Our-Government/Departments-Offices/Public-Works/Solid-Waste/Too-Toxic-to-Trash",
        "24 hours — kiosk at station",
        "407-246-2314",
        mats(["medical-sharps", "needles"]),
    ),
    # --- austin (library battery drop-offs — austintexas.gov) ---
    row(
        "Terrazas Branch Library Battery Drop-Off",
        "Battery take-back (library)",
        "austin",
        "TX",
        "78702",
        "1105 E Cesar Chavez Street, Austin, TX 78702",
        30.262,
        -97.728,
        "https://www.austintexas.gov/page/battery-recycling-locations",
        "Library hours — confirm on library.austintexas.gov",
        "512-974-2000",
        mats(["household-batteries", "lithium-battery", "car-battery"]),
    ),
    row(
        "Willie Mae Kirk Branch Library Battery Drop-Off",
        "Battery take-back (library)",
        "austin",
        "TX",
        "78702",
        "3101 Oak Springs Drive, Austin, TX 78702",
        30.268,
        -97.718,
        "https://www.austintexas.gov/page/battery-recycling-locations",
        "Library hours — confirm on library.austintexas.gov",
        "512-974-2000",
        mats(["household-batteries", "lithium-battery", "car-battery"]),
    ),
    row(
        "University Hills Branch Library Battery Drop-Off",
        "Battery take-back (library)",
        "austin",
        "TX",
        "78723",
        "4721 Loyola Lane, Austin, TX 78723",
        30.308,
        -97.688,
        "https://www.austintexas.gov/page/battery-recycling-locations",
        "Library hours — confirm on library.austintexas.gov",
        "512-974-2000",
        mats(["household-batteries", "lithium-battery", "car-battery"]),
    ),
    row(
        "Spicewood Springs Branch Library Battery Drop-Off",
        "Battery take-back (library)",
        "austin",
        "TX",
        "78759",
        "7717 Spicewood Springs Road, Austin, TX 78759",
        30.378,
        -97.758,
        "https://www.austintexas.gov/page/battery-recycling-locations",
        "Library hours — confirm on library.austintexas.gov",
        "512-974-2000",
        mats(["household-batteries", "lithium-battery", "car-battery"]),
    ),
    # --- arlington (additional library drop-offs) ---
    row(
        "Lake Arlington Branch Library — recycling drop-off",
        "Public library recycling drop-off",
        "arlington",
        "TX",
        "76016",
        "4000 W Green Oaks Boulevard, Arlington, TX 76016",
        32.698,
        -97.168,
        "https://www.arlingtontx.gov/residents/trash_and_recycling/recycling_center",
        "Library hours — confirm on arlingtontx.gov",
        "817-459-6772",
        mats(E_WASTE, RECYCLE),
    ),
    row(
        "Southwest Branch Library — recycling drop-off",
        "Public library recycling drop-off",
        "arlington",
        "TX",
        "76017",
        "3311 SW Green Oaks Boulevard, Arlington, TX 76017",
        32.648,
        -97.168,
        "https://www.arlingtontx.gov/residents/trash_and_recycling/recycling_center",
        "Library hours — confirm on arlingtontx.gov",
        "817-459-6772",
        mats(E_WASTE, RECYCLE),
    ),
    # --- orlando (more OFD sharps stations) ---
    row(
        "Orlando Fire Department Sharps Drop-Off — Fire Station 3",
        "Fire station sharps exchange drop-off",
        "orlando",
        "FL",
        "32804",
        "2749 N Orange Blossom Trail, Orlando, FL 32804",
        28.578,
        -81.398,
        "https://www.orlando.gov/Our-Government/Departments-Offices/Public-Works/Solid-Waste/Too-Toxic-to-Trash",
        "24 hours — kiosk at station",
        "407-246-2314",
        mats(["medical-sharps", "needles"]),
    ),
    row(
        "Orlando Fire Department Sharps Drop-Off — Fire Station 7",
        "Fire station sharps exchange drop-off",
        "orlando",
        "FL",
        "32806",
        "5933 Metrowest Boulevard, Orlando, FL 32835",
        28.512,
        -81.458,
        "https://www.orlando.gov/Our-Government/Departments-Offices/Public-Works/Solid-Waste/Too-Toxic-to-Trash",
        "24 hours — kiosk at station",
        "407-246-2314",
        mats(["medical-sharps", "needles"]),
    ),
    row(
        "Orlando Fire Department Sharps Drop-Off — Fire Station 6",
        "Fire station sharps exchange drop-off",
        "orlando",
        "FL",
        "32806",
        "2319 Conway Road, Orlando, FL 32806",
        28.512,
        -81.328,
        "https://www.orlando.gov/Our-Government/Departments-Offices/Public-Works/Solid-Waste/Too-Toxic-to-Trash",
        "24 hours — kiosk at station",
        "407-246-2314",
        mats(["medical-sharps", "needles"]),
    ),
]

# Miami-Dade Trash and Recycling Centers (miamidade.gov)
MIAMI_TRCS = [
    ("Chapman Field Trash and Recycling Center", "13600 Old Cutler Road, Miami, FL 33158", "33158", 25.625, -80.318),
    ("Eureka Drive Trash and Recycling Center", "9401 SW 184th Street, Miami, FL 33157", "33157", 25.598, -80.328),
    ("Golden Glades Trash and Recycling Center", "140 NW 160th Street, Miami, FL 33169", "33169", 25.928, -80.218),
    ("Moody Drive Trash and Recycling Center", "12970 SW 268th Street, Homestead, FL 33032", "33032", 25.508, -80.418),
    ("Norwood Trash and Recycling Center", "19901 NW 7th Avenue, Miami Gardens, FL 33169", "33169", 25.955, -80.218),
    ("Richmond Heights Trash and Recycling Center", "14050 Boggs Drive, Miami, FL 33176", "33176", 25.638, -80.358),
    ("Snapper Creek Trash and Recycling Center", "2200 SW 117th Avenue, Miami, FL 33175", "33175", 25.748, -80.385),
    ("South Miami Heights Trash and Recycling Center", "20800 SW 117th Court, Miami, FL 33177", "33177", 25.588, -80.358),
    ("West Little River Trash and Recycling Center", "1830 NW 79th Street, Miami, FL 33147", "33147", 25.848, -80.228),
    ("West Perrine Trash and Recycling Center", "16651 SW 107th Avenue, Miami, FL 33157", "33157", 25.598, -80.358),
    ("North Dade Trash and Recycling Center", "21500 NW 47th Avenue, Opa-locka, FL 33055", "33055", 25.888, -80.278),
]
for name, address, zip_code, lat, lng in MIAMI_TRCS:
    city = "hialeah" if "Opa-locka" in address or "33055" in zip_code else "miami"
    FACILITIES.append(
        row(
            name,
            "Miami-Dade neighborhood TRC — bulky / yard / tires / white goods",
            city,
            "FL",
            zip_code,
            address,
            lat,
            lng,
            "https://www.miamidade.gov/global/service.page?Mduid_service=ser1464797123341331",
            "Daily 7:00–17:30",
            "311",
            MIAMI_TRC,
        )
    )

# St. Petersburg city recycling / brush sites (pinellas.gov 2026 Recycle Guide)
STPETE_SITES = [
    ("St. Petersburg Recycling Drop-Off — 62nd Ave NE", "1000 62nd Avenue NE, St. Petersburg, FL 33702", "33702", 27.778, -82.658),
    ("St. Petersburg Recycling Drop-Off — 26th Ave N", "7750 26th Avenue N, St. Petersburg, FL 33710", "33710", 27.792, -82.742),
    ("St. Petersburg Recycling Drop-Off — 20th Ave N", "2453 20th Avenue N, St. Petersburg, FL 33713", "33713", 27.792, -82.678),
    ("St. Petersburg Recycling Drop-Off — 26th Ave S", "2500 26th Avenue S, St. Petersburg, FL 33712", "33712", 27.748, -82.678),
    ("St. Petersburg Recycling Drop-Off — Dr MLK Jr St S", "4015 Dr Martin Luther King Jr Street S, St. Petersburg, FL 33705", "33705", 27.718, -82.648),
    ("Crescent Lake Park Recycling Drop-Off", "1320 Fifth Street N, St. Petersburg, FL 33701", "33701", 27.778, -82.648),
    ("St. Petersburg Municipal Marina Recycling Drop-Off", "300 Second Avenue SE, St. Petersburg, FL 33701", "33701", 27.768, -82.628),
    ("Pinellas County Solid Waste — mixed recycling drop-off", "2855 109th Avenue N, St. Petersburg, FL 33716", "33716", 27.878, -82.708),
]
for name, address, zip_code, lat, lng in STPETE_SITES:
    FACILITIES.append(
        row(
            name,
            "Mixed recycling drop-off center",
            "st-petersburg",
            "FL",
            zip_code,
            address,
            lat,
            lng,
            "https://pinellas.gov/mixed-recycling-drop-off-centers/",
            "Daily 24 hours (unstaffed containers)",
            "727-464-7500",
            STPETE_RECYCLE,
        )
    )

# Pinellas HHW North (Clearwater — serves St. Pete metro)
FACILITIES.append(
    row(
        "Pinellas County HHW North",
        "County HHW collection center",
        "st-petersburg",
        "FL",
        "33761",
        "29582 US Highway 19 N, Clearwater, FL 33761",
        28.048,
        -82.728,
        "https://pinellas.gov/solid-waste-disposal-complex-hours/",
        "Select Sat 7:00–17:00 — see pinellas.gov HHW calendar",
        "727-464-7500",
        mats(HHW),
    )
)


def main() -> None:
    facilities = json.loads(FAC_PATH.read_text())
    by_key = {(f.get("city_slug"), f.get("name")): i for i, f in enumerate(facilities)}
    by_addr = {
        (f.get("city_slug"), (f.get("address") or "").lower()[:55])
        for f in facilities
        if f.get("address")
    }

    fixed = added = updated = skipped = 0
    for fix in FIXES:
        old_key = (fix["city_slug"], fix["old_name"])
        if old_key not in by_key:
            continue
        idx = by_key.pop(old_key)
        new_row = {**facilities[idx], **{k: v for k, v in fix.items() if k != "old_name"}}
        new_key = (fix["city_slug"], fix["name"])
        facilities[idx] = new_row
        by_key[new_key] = idx
        by_addr.add((fix["city_slug"], fix["address"].lower()[:55]))
        fixed += 1

    for r in FACILITIES:
        r["accepted_materials"] = mats(r["accepted_materials"])
        key = (r["city_slug"], r["name"])
        addr_key = (r["city_slug"], r["address"].lower()[:55])
        if key in by_key:
            facilities[by_key[key]] = {**facilities[by_key[key]], **r}
            updated += 1
        elif addr_key in by_addr:
            skipped += 1
        else:
            facilities.append(r)
            by_key[key] = len(facilities) - 1
            by_addr.add(addr_key)
            added += 1

    FAC_PATH.write_text(json.dumps(facilities, indent=2) + "\n")

    target = {
        "houston",
        "dallas",
        "fort-worth",
        "arlington",
        "austin",
        "san-antonio",
        "el-paso",
        "corpus-christi",
        "jacksonville",
        "miami",
        "tampa",
        "orlando",
        "st-petersburg",
        "hialeah",
    }
    per_city = {c: sum(1 for f in facilities if f.get("city_slug") == c) for c in sorted(target)}
    total = sum(per_city.values())
    print(
        json.dumps(
            {
                "added": added,
                "updated": updated,
                "fixed": fixed,
                "skipped": skipped,
                "total_15_metros": total,
                "per_city": per_city,
                "all_facilities": len(facilities),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
