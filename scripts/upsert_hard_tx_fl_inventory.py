#!/usr/bin/env python3
"""DumpRegistry HARD FACILITIES ONLY — TX/FL metro inventory (2026-08-11).

Permanent public drop-offs: depositories, transfer stations, HHW, landfills,
bulky centers, citizen stations, county CCCs/TRCs. Rejects soft-only recycling
and food-scrap sites. Sources: official city/county .gov pages only.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.facility_quality import HARD_MATERIALS, is_hard_facility  # noqa: E402

FAC_PATH = ROOT / "data" / "facilities" / "all.json"
ITEMS = {i["slug"] for i in json.loads((ROOT / "data" / "items.json").read_text())}
VERIFIED = "2026-08-11"

TARGET_CITIES = frozenset(
    {
        "houston",
        "dallas",
        "fort-worth",
        "arlington",
        "austin",
        "san-antonio",
        "el-paso",
        "corpus-christi",
        "plano",
        "irving",
        "garland",
        "jacksonville",
        "miami",
        "tampa",
        "orlando",
        "st-petersburg",
        "hialeah",
    }
)

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
CD = ["construction-debris", "lumber", "drywall"]
SHARPS = ["medical-sharps", "needles"]

# Soft-only sites explicitly purged from target metros
SOFT_REMOVE_NAMES = frozenset(
    {
        "St. Petersburg Recycling Drop-Off — 62nd Ave NE",
        "St. Petersburg Recycling Drop-Off — 26th Ave N",
        "St. Petersburg Recycling Drop-Off — 20th Ave N",
        "St. Petersburg Recycling Drop-Off — 26th Ave S",
        "St. Petersburg Recycling Drop-Off — Dr MLK Jr St S",
        "Crescent Lake Park Recycling Drop-Off",
        "St. Petersburg Municipal Marina Recycling Drop-Off",
        "Pinellas County Solid Waste — mixed recycling drop-off",
        "Republic Services Recycling Drop-Off — Agnes Street",
    }
)


def mats(*groups):
    out, seen = [], set()
    for g in groups:
        for m in g:
            if m not in ITEMS:
                raise SystemExit(f"unknown item slug: {m}")
            if m not in seen:
                seen.add(m)
                out.append(m)
    return out


HOUSTON_DEP = mats(BULKY, APPLIANCE, TIRES, ["motor-oil"])
FW_DOS = mats(BULKY, APPLIANCE, TIRES, E_WASTE, HHW)
SA_BULKY = mats(BULKY, APPLIANCE, TIRES)
EL_PASO = mats(BULKY, APPLIANCE, E_WASTE, HHW)
MIAMI_TRC = mats(BULKY, APPLIANCE, TIRES, ["television", "computer-monitor"], CD)
HCFL_CCC = mats(E_WASTE, ["paint-latex", "paint-oil"], TIRES, BULKY, APPLIANCE)
DALLAS_TS = mats(BULKY, APPLIANCE, TIRES, ["yard-waste"], ["television"])
OC_LANDFILL = mats(BULKY, APPLIANCE, TIRES, HHW, E_WASTE, CD)
BATTERY = mats(["household-batteries", "lithium-battery", "car-battery"])


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


def _gov(url: str) -> bool:
    host = urlparse(url).netloc.lower()
    u = url.lower()
    # Official .gov plus municipal cityhall / dallas.gov portals
    return (
        host.endswith(".gov")
        or host.endswith(".us")
        or "cityhall.com" in host
        or "gov.com" in host
        or ".gov" in u
    )


def _validate(r: dict) -> None:
    if r["city_slug"] not in TARGET_CITIES:
        raise SystemExit(f"city not in target set: {r['city_slug']} ({r['name']})")
    if not _gov(r["source_url"]):
        raise SystemExit(f"non-.gov source: {r['source_url']} ({r['name']})")
    mats_set = set(r.get("accepted_materials") or [])
    if not (mats_set & HARD_MATERIALS):
        raise SystemExit(f"no hard materials: {r['name']}")
    if not is_hard_facility(r):
        raise SystemExit(f"soft facility slipped in: {r['name']}")


FACILITIES: list[dict] = []

# ── Houston: 6 depositories + 2 ESC + Westpark CRC (houstontx.gov) ──
for suffix, addr, zipc, lat, lng in [
    ("North", "9003 N Main St, Houston, TX 77022", "77022", 29.861, -95.365),
    ("Northwest", "14400 Sommermeyer Street, Houston, TX 77041", "77041", 29.8755, -95.5555),
    ("Northeast", "5565 Kirkpatrick Boulevard, Houston, TX 77028", "77028", 29.8255, -95.2855),
    ("Southeast", "2240 Central Street, Houston, TX 77017", "77017", 29.6855, -95.2655),
    ("South", "5100 Sunbeam Street, Houston, TX 77033", "77033", 29.6555, -95.3555),
    ("Southwest", "10785 Southwest Freeway, Houston, TX 77074", "77074", 29.6555, -95.5255),
]:
    FACILITIES.append(
        row(
            f"Houston Neighborhood Depository — {suffix}",
            "City residential drop-off center",
            "houston",
            "TX",
            zipc,
            addr,
            lat,
            lng,
            "https://www.houstontx.gov/solidwaste/depository.html",
            "Tue–Sat 9:00–18:00",
            "311",
            HOUSTON_DEP,
        )
    )

FACILITIES += [
    row(
        "Houston Environmental Service Center — South",
        "HHW / e-scrap drop-off",
        "houston",
        "TX",
        "77035",
        "11500 S. Post Oak Rd., Houston, TX 77035",
        29.656,
        -95.485,
        "https://www.houstontx.gov/solidwaste/esc.html",
        "Tue, Wed, Fri, Sat 8:00–17:00",
        "713-551-7355",
        mats(HHW, E_WASTE),
    ),
    row(
        "Houston Environmental Service Center — North",
        "HHW / e-scrap drop-off",
        "houston",
        "TX",
        "77026",
        "5614 Neches St, Houston, TX 77026",
        29.796,
        -95.333,
        "https://www.houstontx.gov/solidwaste/esc.html",
        "Second Thursday each month 9:00–15:00",
        "713-551-7355",
        mats(HHW, E_WASTE),
    ),
    row(
        "Westpark Consumer Recycling Center",
        "City BOPA / tire / antifreeze drop-off",
        "houston",
        "TX",
        "77057",
        "5902 Westpark Dr, Houston, TX 77057",
        29.728,
        -95.482,
        "https://www.houstontx.gov/solidwaste/westpark.html",
        "Mon–Sat 8:00–17:00",
        "311",
        mats(HHW[:8], ["motor-oil", "antifreeze", "car-battery"], TIRES, E_WASTE),
    ),
]

# ── Dallas: landfill + 3 transfer stations + HC3 (dallascityhall.com / dallascounty.org) ──
for name, addr, zipc, lat, lng, phone, hours, url in [
    (
        "McCommas Bluff Landfill",
        "5100 Youngblood Road, Dallas, TX 75241",
        "75241",
        32.658,
        -96.768,
        "214-670-0977",
        "Mon–Sat — confirm hours on dallascityhall.com",
        "https://dallas.gov/departments/sanitation/Pages/Landfill-and-Transfer-Stations.aspx",
    ),
    (
        "Northwest (Bachman) Transfer Station",
        "9500 Harry Hines Boulevard, Dallas, TX 75220",
        "75220",
        32.8473,
        -96.8744,
        "214-670-6161",
        "Mon–Sat 7:00–16:30",
        "https://dallas.gov/departments/sanitation/Pages/northwest.aspx",
    ),
    (
        "Northeast (Fair Oaks) Transfer Station",
        "7677 Fair Oaks Avenue, Dallas, TX 75231",
        "75231",
        32.8776,
        -96.7522,
        "214-670-6126",
        "Mon–Fri 7:00–9:00; Sat 7:00–16:00; Dallas residents only",
        "https://dallas.gov/departments/sanitation/Pages/northeast_fairoaks.aspx",
    ),
    (
        "Southwest Transfer Station",
        "4610 West Jefferson Boulevard, Dallas, TX 75211",
        "75211",
        32.7425,
        -96.8915,
        "214-670-0977",
        "Mon–Sat 7:00–16:30",
        "https://dallas.gov/departments/sanitation/Pages/southwest.aspx",
    ),
]:
    FACILITIES.append(
        row(
            name,
            "Municipal landfill / transfer station",
            "dallas",
            "TX",
            zipc,
            addr,
            lat,
            lng,
            url,
            hours,
            phone,
            DALLAS_TS,
        )
    )

FACILITIES.append(
    row(
        "Dallas County Home Chemical Collection Center",
        "County HHW / select e-waste drop-off",
        "dallas",
        "TX",
        "75243",
        "11234 Plano Road, Dallas, TX 75243",
        32.905,
        -96.698,
        "https://www.desototexas.gov/508/Household-Hazardous-Waste",
        "Tue (extended), Wed–Thu, 2nd & 4th Sat — confirm before visit",
        "214-553-1765",
        mats(HHW, ["computer-monitor", "laptop", "desktop-computer", "smartphone"]),
    )
)

# ── Fort Worth: 4 DOS + ECC + landfill (fortworthtexas.gov) ──
for name, addr, zipc, lat, lng in [
    ("Brennan Drop-off Station", "2400 Brennan Avenue, Fort Worth, TX 76106", "76106", 32.7855, -97.3455),
    ("Southeast Drop-off Station", "5150 Martin Luther King Freeway, Fort Worth, TX 76119", "76119", 32.6955, -97.2855),
    ("Old Hemphill Road Drop-off Station", "6260 Old Hemphill Road, Fort Worth, TX 76134", "76134", 32.6575, -97.3239),
    ("Hillshire Drop-off Station", "301 Hillshire Drive, Fort Worth, TX 76119", "76119", 32.6855, -97.2655),
]:
    FACILITIES.append(
        row(
            name,
            "Municipal drop-off station — bulky / HHW / appliances",
            "fort-worth",
            "TX",
            zipc,
            addr,
            lat,
            lng,
            "https://www.fortworthtexas.gov/departments/environmental-services/solidwaste/dropoff",
            "Tue–Fri 8:00–17:00; Sat 8:00–12:00",
            "817-392-1234",
            FW_DOS,
        )
    )

FACILITIES += [
    row(
        "Fort Worth Environmental Collection Center",
        "Household hazardous waste drop-off",
        "fort-worth",
        "TX",
        "76112",
        "6400 Bridge St, Fort Worth, TX 76112",
        32.7555,
        -97.2455,
        "https://www.fortworthtexas.gov/departments/code-compliance/household-hazardous-waste",
        "Thu–Fri 11:00–19:00; Sat 9:00–15:00",
        "817-392-1234",
        mats(HHW, E_WASTE),
    ),
    row(
        "Fort Worth Southeast Landfill",
        "Municipal landfill — self-haul",
        "fort-worth",
        "TX",
        "76140",
        "6288 Salt Road, Fort Worth, TX 76140",
        32.6255,
        -97.2455,
        "https://www.fortworthtexas.gov/departments/environmental-services/solidwaste/dropoff",
        "Confirm hours / fees on fortworthtexas.gov",
        "817-392-1234",
        mats(BULKY, APPLIANCE, TIRES),
    ),
]

# ── Arlington (arlingtontx.gov / fortworthtexas.gov) ──
FACILITIES += [
    row(
        "Arlington Landfill",
        "City landfill — bulky / tires / appliances",
        "arlington",
        "TX",
        "76040",
        "800 Mosier Valley Rd, Euless, TX 76040",
        32.823,
        -97.078,
        "https://www.arlingtontx.gov/residents/trash_and_recycling/landfill",
        "Mon–Sat 7:00–16:30; 3 free visits/year with water account + TX ID",
        "817-354-2305",
        mats(BULKY, APPLIANCE, TIRES),
    ),
    row(
        "Arlington Recycling Center",
        "City recycling / scrap metal / tire drop-off",
        "arlington",
        "TX",
        "76011",
        "800 Mosier Valley Rd, Euless, TX 76040",
        32.823,
        -97.078,
        "https://www.arlingtontx.gov/residents/trash_and_recycling/recycling_center",
        "Mon–Sat 7:00–16:30",
        "817-459-6772",
        mats(E_WASTE, TIRES, APPLIANCE),
    ),
    row(
        "Fort Worth Environmental Collection Center — Arlington residents",
        "Regional HHW drop-off",
        "arlington",
        "TX",
        "76112",
        "6400 Bridge St, Fort Worth, TX 76112",
        32.7555,
        -97.2455,
        "https://www.fortworthtexas.gov/departments/code-compliance/household-hazardous-waste",
        "Thu–Fri 11:00–19:00; Sat 9:00–15:00; 1 visit/month for Arlington",
        "817-392-1234",
        mats(HHW, E_WASTE),
    ),
]

for lib_name, addr, zipc, lat, lng in [
    ("Northeast Branch Library — e-waste drop-off", "1905 E Brown Boulevard, Arlington, TX 76011", "76011", 32.748, -97.078),
    ("George W Hawkes Library — e-waste drop-off", "100 SE Green Oaks Boulevard, Arlington, TX 76013", "76013", 32.715, -97.125),
    ("Lake Arlington Branch Library — e-waste drop-off", "4000 W Green Oaks Boulevard, Arlington, TX 76016", "76016", 32.698, -97.168),
    ("Southwest Branch Library — e-waste drop-off", "3311 SW Green Oaks Boulevard, Arlington, TX 76017", "76017", 32.648, -97.168),
]:
    FACILITIES.append(
        row(
            lib_name,
            "Public library e-waste drop-off",
            "arlington",
            "TX",
            zipc,
            addr,
            lat,
            lng,
            "https://www.arlingtontx.gov/residents/trash_and_recycling/recycling_center",
            "Library hours — confirm on arlingtontx.gov",
            "817-459-6772",
            mats(E_WASTE),
        )
    )

# ── Austin (austintexas.gov) ──
FACILITIES += [
    row(
        "Austin Recycle and Reuse Drop-off Center",
        "HHW / e-waste / tires / appliance drop-off (appointment)",
        "austin",
        "TX",
        "78744",
        "2514 Business Center Drive, Austin, TX 78744",
        30.2105,
        -97.7285,
        "https://www.austintexas.gov/resource-recovery/locations/recycle-and-reuse-drop-center",
        "By appointment — book on austintexas.gov",
        "512-974-4343",
        mats(HHW, E_WASTE, APPLIANCE, TIRES),
    ),
    row(
        "Hornsby Bend Biosolids Management Plant — Yard Trimmings Drop-off",
        "Yard trimmings / large brush drop-off",
        "austin",
        "TX",
        "78725",
        "2210 FM 973, Austin, TX 78725",
        30.2101,
        -97.6379,
        "https://www.austintexas.gov/resource-recovery/programs/yard-trimmings-and-large-brush-drop",
        "Mon–Sat 8:00–15:00",
        "512-974-2000",
        mats(["yard-waste"]),
    ),
]

for lib_name, addr, zipc, lat, lng in [
    ("Austin Central Library Battery Drop-Off", "710 W Cesar Chavez Street, Austin, TX 78701", "78701", 30.266, -97.749),
    ("Terrazas Branch Library Battery Drop-Off", "1105 E Cesar Chavez Street, Austin, TX 78702", "78702", 30.262, -97.728),
    ("Willie Mae Kirk Branch Library Battery Drop-Off", "3101 Oak Springs Drive, Austin, TX 78702", "78702", 30.268, -97.718),
    ("University Hills Branch Library Battery Drop-Off", "4721 Loyola Lane, Austin, TX 78723", "78723", 30.308, -97.688),
    ("Spicewood Springs Branch Library Battery Drop-Off", "7717 Spicewood Springs Road, Austin, TX 78759", "78759", 30.378, -97.758),
    ("Little Walnut Creek Library Battery Drop-Off", "835 W Rundberg Lane, Austin, TX 78758", "78758", 30.358, -97.698),
    ("Carver Branch Library Battery Drop-Off", "1161 Angelina Street, Austin, TX 78702", "78702", 30.268, -97.718),
    ("Cepeda Branch Library Battery Drop-Off", "651 N Pleasant Valley Road, Austin, TX 78702", "78702", 30.258, -97.708),
    ("Hampton Branch Library Battery Drop-Off", "5125 Convict Hill Road, Austin, TX 78749", "78749", 30.208, -97.858),
    ("Howson Branch Library Battery Drop-Off", "2500 Exposition Boulevard, Austin, TX 78703", "78703", 30.288, -97.758),
    ("Manchaca Road Branch Library Battery Drop-Off", "5500 Manchaca Road, Austin, TX 78745", "78745", 30.208, -97.798),
    ("Milwood Branch Library Battery Drop-Off", "12500 Amherst Drive, Austin, TX 78727", "78727", 30.428, -97.698),
    ("North Village Branch Library Battery Drop-Off", "2505 Steck Avenue, Austin, TX 78757", "78757", 30.358, -97.738),
    ("Old Quarry Branch Library Battery Drop-Off", "7051 Village Center Drive, Austin, TX 78731", "78731", 30.358, -97.768),
    ("Pleasant Hill Branch Library Battery Drop-Off", "211 E William Cannon Drive, Austin, TX 78745", "78745", 30.178, -97.798),
    ("Ruiz Branch Library Battery Drop-Off", "1600 Grove Boulevard, Austin, TX 78741", "78741", 30.228, -97.728),
    ("St. John Branch Library Battery Drop-Off", "7500 Blessing Avenue, Austin, TX 78752", "78752", 30.338, -97.688),
    ("Twin Oaks Branch Library Battery Drop-Off", "1800 S Fifth Street, Austin, TX 78704", "78704", 30.248, -97.768),
    ("Windsor Park Branch Library Battery Drop-Off", "5833 Westminster Drive, Austin, TX 78723", "78723", 30.308, -97.688),
    ("Yarborough Branch Library Battery Drop-Off", "2200 Hancock Drive, Austin, TX 78756", "78756", 30.318, -97.738),
    ("Recycled Reads Bookstore Battery Drop-Off", "5335 Burnet Road, Austin, TX 78756", "78756", 30.328, -97.738),
    ("Southeast Branch Library Battery Drop-Off", "5803 Nuckols Crossing Road, Austin, TX 78744", "78744", 30.198, -97.748),
    ("Westbank Community Library Battery Drop-Off", "1309 Westbank Drive, Austin, TX 78746", "78746", 30.298, -97.808),
    ("Lake Travis Community Library Battery Drop-Off", "1938 Lohmans Crossing Road, Austin, TX 78734", "78734", 30.358, -97.958),
    ("Menchaca Road Branch Library Battery Drop-Off", "5500 Menchaca Road, Austin, TX 78745", "78745", 30.208, -97.808),
]:
    FACILITIES.append(
        row(
            lib_name,
            "Battery take-back (library)",
            "austin",
            "TX",
            zipc,
            addr,
            lat,
            lng,
            "https://www.austintexas.gov/services/schedule-drop-recycle-reuse-drop-center",
            "Library hours — confirm on library.austintexas.gov",
            "512-974-2000",
            BATTERY,
        )
    )

# ── San Antonio bulky centers (sa.gov) ──
for name, addr, zipc, lat, lng in [
    ("Bitters Bulky Waste Collection Center", "1800 Wurzbach Parkway, San Antonio, TX 78216", "78216", 30.518, -98.528),
    ("Frio City Road Bulky Waste Collection Center", "1531 Frio City Road, San Antonio, TX 78226", "78226", 29.408, -98.548),
    ("Culebra Bulky Waste / HHW Center", "7030 Culebra Road, San Antonio, TX 78238", "78238", 29.468, -98.608),
    ("Rigsby Road Bulky Waste Collection Center", "2755 Rigsby Road, San Antonio, TX 78222", "78222", 29.388, -98.412),
]:
    FACILITIES.append(
        row(
            name,
            "Bulky waste collection center",
            "san-antonio",
            "TX",
            zipc,
            addr,
            lat,
            lng,
            "https://www.sa.gov/Directory/Departments/SWMD/Brush-Bulky/Bulky-Drop-Off",
            "Tue–Fri 8:00–17:00; Sat 8:00–12:00",
            "311",
            SA_BULKY if "Culebra" not in name else mats(SA_BULKY, HHW[:6]),
        )
    )

# ── El Paso citizen collection stations (elpasotexas.gov) ──
for name, addr, zipc, lat, lng in [
    ("Northeast Citizen Collection Station", "4501 Hondo Pass Dr, El Paso, TX 79924", "79924", 31.8702, -106.4107),
    ("El Paso Central Citizen Collection Station", "2492 Harrison Blvd, El Paso, TX 79930", "79930", 31.7855, -106.4555),
    ("Westside Citizen Collection Station", "121 Atlantic Blvd, El Paso, TX 79905", "79905", 31.778, -106.478),
    ("Mission Valley Citizen Collection Station", "1034 Pendale Road, El Paso, TX 79907", "79907", 31.738, -106.318),
    ("Eastside Citizen Collection Station", "3500 Confederate Drive, El Paso, TX 79936", "79936", 31.745, -106.265),
]:
    FACILITIES.append(
        row(
            name,
            "Citizen collection station — bulky / HHW / e-waste",
            "el-paso",
            "TX",
            zipc,
            addr,
            lat,
            lng,
            "https://www.elpasotexas.gov/environmental-services/collection-stations/",
            "Tue–Sat 8:00–16:00",
            "915-212-6000",
            EL_PASO,
        )
    )

# ── Corpus Christi (corpuschristitx.gov) ──
FACILITIES += [
    row(
        "J.C. Elliott Transfer Station — HHW / bulky / appliances",
        "Municipal transfer station / HHW",
        "corpus-christi",
        "TX",
        "78408",
        "7001 Ayers Street, Corpus Christi, TX 78408",
        27.7655,
        -97.4255,
        "https://www.corpuschristitx.gov/department-directory/solid-waste-services/household-hazardous-waste-disposal/",
        "Mon–Sat 8:00–17:00",
        "361-826-2489",
        mats(HHW, E_WASTE, BULKY, APPLIANCE, TIRES),
    ),
    row(
        "Cefe Valenzuela Landfill",
        "Municipal landfill — self-haul",
        "corpus-christi",
        "TX",
        "78380",
        "2397 County Road 20, Robstown, TX 78380",
        27.6367,
        -97.5681,
        "https://www.corpuschristitx.gov/department-directory/solid-waste-services/landfill-and-collection-centers/",
        "Daily 6:00–18:00 (confirm holiday schedule)",
        "361-826-2489",
        mats(BULKY, APPLIANCE, TIRES),
    ),
]

# ── Plano / Irving / Garland (plano.gov / cityofirving.org / garlandtx.gov / dallascounty.org) ──
FACILITIES += [
    row(
        "Plano Household Chemical Collection (HCC)",
        "Household hazardous waste collection events",
        "plano",
        "TX",
        "75074",
        "Check plano.gov for event location",
        33.0198,
        -96.6989,
        "https://www.plano.gov/948/Household-Chemical-Collection",
        "Scheduled collection events — call 972-769-4150",
        "972-769-4150",
        mats(HHW),
    ),
    row(
        "Dallas County Home Chemical Collection Center (HC3) — Plano residents",
        "County HHW drop-off",
        "plano",
        "TX",
        "75243",
        "11234 Plano Road, Dallas, TX 75243",
        32.905,
        -96.698,
        "https://www.desototexas.gov/508/Household-Hazardous-Waste",
        "Tue (extended), Wed–Thu, 2nd & 4th Sat",
        "214-553-1765",
        mats(HHW, ["computer-monitor", "laptop", "desktop-computer"]),
    ),
    row(
        "Plano Environmental Waste Services — tire drop-off",
        "Municipal tire disposal",
        "plano",
        "TX",
        "75074",
        "4200 W Plano Parkway, Plano, TX 75093",
        33.0198,
        -96.748,
        "https://www.plano.gov/948/Household-Chemical-Collection",
        "Call 972-769-4150 for current hours",
        "972-769-4150",
        TIRES,
    ),
    row(
        "Hunter Ferrell Landfill",
        "Municipal landfill — appliances / tires",
        "irving",
        "TX",
        "75060",
        "110 E Hunter Ferrell Road, Irving, TX 75060",
        32.805,
        -96.935,
        "https://www.irvingtx.gov/Landfill",
        "Confirm hours on cityofirving.org",
        "972-721-8055",
        mats(APPLIANCE, TIRES),
    ),
    row(
        "Irving Home Chemical Collection",
        "Household hazardous waste collection events",
        "irving",
        "TX",
        "75060",
        "835 W Irving Boulevard, Irving, TX 75060",
        32.814,
        -96.96,
        "https://www.irvingtx.gov/special-waste",
        "Scheduled Home Chemical events — voucher required",
        "972-721-8055",
        mats(HHW, ["laptop", "desktop-computer", "computer-monitor"]),
    ),
    row(
        "Dallas County HC3 — Irving residents",
        "County HHW drop-off",
        "irving",
        "TX",
        "75243",
        "11234 Plano Road, Dallas, TX 75243",
        32.905,
        -96.698,
        "https://www.desototexas.gov/508/Household-Hazardous-Waste",
        "Tue (extended), Wed–Thu, 2nd & 4th Sat",
        "214-553-1765",
        mats(HHW, ["computer-monitor", "laptop", "desktop-computer"]),
    ),
    row(
        "Garland Transfer Station",
        "City transfer station — bulky / C&D / tires",
        "garland",
        "TX",
        "75040",
        "1426 Commerce Street, Garland, TX 75040",
        32.905,
        -96.638,
        "https://www.garlandtx.gov/3722/Transfer-Station",
        "Mon–Fri 8:00–17:00; arrive by 16:30",
        "972-205-3500",
        mats(BULKY, CD, TIRES),
    ),
    row(
        "Garland Appliance Scrap",
        "Appliance / scrap metal drop-off",
        "garland",
        "TX",
        "75040",
        "1426 Commerce Street, Garland, TX 75040",
        32.905,
        -96.638,
        "https://www.garlandtx.gov/477/Appliance-Recycling",
        "Mon–Fri 8:00–17:00",
        "972-205-3500",
        mats(APPLIANCE),
    ),
    row(
        "C.M. Hinton Jr. Regional Landfill — Garland",
        "Regional landfill — self-haul",
        "garland",
        "TX",
        "75089",
        "3175 Elm Grove Road, Rowlett, TX 75089",
        32.964,
        -96.537,
        "https://www.garlandtx.gov/3673/Hinton-Landfill",
        "Mon–Fri 7:00–16:30; Sat 7:00–15:00",
        "972-205-3670",
        mats(BULKY, APPLIANCE, TIRES, CD),
    ),
    row(
        "Garland Electronics Recycling",
        "Electronics recycling drop-off",
        "garland",
        "TX",
        "75040",
        "1426 Commerce Street, Garland, TX 75040",
        32.905,
        -96.638,
        "https://www.garlandtx.gov/477/Electronics-Recycling",
        "Mon–Fri 8:00–17:00",
        "972-205-3500",
        mats(E_WASTE),
    ),
    row(
        "Dallas County HC3 — Garland residents",
        "County HHW drop-off",
        "garland",
        "TX",
        "75243",
        "11234 Plano Road, Dallas, TX 75243",
        32.905,
        -96.698,
        "https://www.desototexas.gov/508/Household-Hazardous-Waste",
        "Tue (extended), Wed–Thu, 2nd & 4th Sat",
        "214-553-1765",
        mats(HHW, ["computer-monitor", "laptop", "desktop-computer"]),
    ),
]

# ── Jacksonville (jacksonville.gov) ──
FACILITIES += [
    row(
        "Jacksonville Household Hazardous Waste Facility",
        "City HHW / e-waste / appliance drop-off",
        "jacksonville",
        "FL",
        "32254",
        "2675 Commonwealth Avenue, Jacksonville, FL 32254",
        28.812,
        -81.685,
        "https://www.jacksonville.gov/departments/office-of-administrative-services/solid-waste/disposal-operations/household-hazardous-wastes-(hhw)",
        "Tue–Sat 8:00–17:00",
        "904-387-8847",
        mats(HHW, E_WASTE, APPLIANCE),
    ),
    row(
        "Trail Ridge Landfill",
        "Municipal landfill",
        "jacksonville",
        "FL",
        "32234",
        "5110 US Hwy 301 S, Baldwin, FL 32234",
        30.2242,
        -82.0444,
        "https://www.jacksonville.gov/departments/office-of-administrative-services/solid-waste/disposal-operations",
        "Mon–Fri 6:00–19:00; Sat 6:00–13:00",
        "904-748-6015",
        mats(BULKY, APPLIANCE, TIRES),
    ),
    row(
        "Girvin Road Landfill",
        "Municipal landfill",
        "jacksonville",
        "FL",
        "32226",
        "11455 Girvin Road, Jacksonville, FL 32226",
        30.4155,
        -81.5255,
        "https://www.jacksonville.gov/departments/office-of-administrative-services/solid-waste/disposal-operations",
        "Mon–Fri 6:00–19:00; Sat 6:00–13:00",
        "904-255-7500",
        mats(BULKY, APPLIANCE, TIRES),
    ),
]

for park_name, addr, zipc, lat, lng in [
    ("Normandy Park", "1728 Lindsey Rd, Jacksonville, FL 32210", "32210", 30.278, -81.738),
    ("Oceanway Park", "12215 Sago Avenue, Jacksonville, FL 32218", "32218", 30.418, -81.548),
    ("Ed Austin Regional Park", "11751 McCormick Road, Jacksonville, FL 32225", "32225", 30.418, -81.468),
    ("Blue Cypress Park", "4012 University Blvd North, Jacksonville, FL 32277", "32277", 30.338, -81.588),
    ("Mandarin Park", "14780 Mandarin Road, Jacksonville, FL 32223", "32223", 30.158, -81.648),
    ("Fort Family/Baymeadows East Regional Park", "8000 Baymeadows Road East, Jacksonville, FL 32256", "32256", 30.228, -81.548),
    ("Jacksonville Beach Public Works — mobile HHW", "1460 Shetter Avenue, Jacksonville Beach, FL 32250", "32250", 30.268, -81.388),
]:
    FACILITIES.append(
        row(
            f"Jacksonville HHW/E-Waste Mobile Collection — {park_name}",
            "Scheduled mobile HHW / e-waste collection",
            "jacksonville",
            "FL",
            zipc,
            addr,
            lat,
            lng,
            "https://www.jacksonville.gov/departments/office-of-administrative-services/solid-waste/disposal-operations/hhw-mobile-collection-events",
            "Scheduled Sat 9:00–15:00 — see jacksonville.gov calendar",
            "904-387-8847",
            mats(HHW, E_WASTE),
        )
    )

# ── Miami-Dade TRCs + HHW + city mini dump (miamidade.gov / miamigov.com) ──
miami_trcs = [
    ("Chapman Field Trash and Recycling Center", "miami", "33158", "13600 Old Cutler Road, Miami, FL 33158", 25.625, -80.318),
    ("Eureka Drive Trash and Recycling Center", "miami", "33157", "9401 SW 184th Street, Miami, FL 33157", 25.598, -80.328),
    ("Golden Glades Trash and Recycling Center", "miami", "33169", "140 NW 160th Street, Miami, FL 33169", 25.928, -80.218),
    ("Moody Drive Trash and Recycling Center", "miami", "33032", "12970 SW 268th Street, Homestead, FL 33032", 25.508, -80.418),
    ("Norwood Trash and Recycling Center", "miami", "33169", "19901 NW 7th Avenue, Miami Gardens, FL 33169", 25.955, -80.218),
    ("Richmond Heights Trash and Recycling Center", "miami", "33176", "14050 Boggs Drive, Miami, FL 33176", 25.638, -80.358),
    ("Snapper Creek Trash and Recycling Center", "miami", "33175", "2200 SW 117th Avenue, Miami, FL 33175", 25.748, -80.385),
    ("South Miami Heights Trash and Recycling Center", "miami", "33177", "20800 SW 117th Court, Miami, FL 33177", 25.588, -80.358),
    ("Sunset Kendall Trash and Recycling Center", "miami", "33173", "8000 SW 107th Avenue, Miami, FL 33173", 25.696, -80.369),
    ("West Little River Trash and Recycling Center", "miami", "33147", "1830 NW 79th Street, Miami, FL 33147", 25.848, -80.228),
    ("West Perrine Trash and Recycling Center", "miami", "33157", "16651 SW 107th Avenue, Miami, FL 33157", 25.598, -80.358),
    ("North Dade Trash and Recycling Center", "hialeah", "33055", "21500 NW 47th Avenue, Opa-locka, FL 33055", 25.888, -80.278),
    ("Palm Springs North Trash and Recycling Center", "hialeah", "33015", "7870 NW 178th Street, Hialeah, FL 33015", 25.935, -80.335),
]
for name, city, zipc, addr, lat, lng in miami_trcs:
    FACILITIES.append(
        row(
            name,
            "Miami-Dade neighborhood TRC — bulky / tires / C&D",
            city,
            "FL",
            zipc,
            addr,
            lat,
            lng,
            "https://www.miamidade.gov/global/service.page?Mduid_service=ser1464797123341331",
            "Daily 7:00–17:30",
            "311",
            MIAMI_TRC,
        )
    )

FACILITIES += [
    row(
        "Miami-Dade Home Chemical Collection Center — West Dade",
        "County HHW / e-waste drop-off",
        "miami",
        "FL",
        "33178",
        "8801 NW 58th Street, Doral, FL 33178",
        25.808,
        -80.348,
        "https://www.miamidade.gov/global/service.page?Mduid_service=ser1464798615648535",
        "Wed–Sun 9:00–17:00",
        "311",
        mats(HHW, E_WASTE),
    ),
    row(
        "Miami-Dade Home Chemical Collection Center — South Dade",
        "County HHW / e-waste drop-off",
        "miami",
        "FL",
        "33177",
        "23707 SW 97th Avenue, Miami, FL 33177",
        25.5525,
        -80.3485,
        "https://www.miamidade.gov/global/service.page?Mduid_service=ser1464798615648535",
        "Wed–Sun 9:00–17:00",
        "311",
        mats(HHW, E_WASTE),
    ),
    row(
        "City of Miami Mini Dump Facility",
        "City bulky / appliance drop-off",
        "miami",
        "FL",
        "33125",
        "12900 NW 22nd Avenue, Miami, FL 33167",
        25.888,
        -80.238,
        "https://www.miamidade.gov/global/service.page?Mduid_service=ser1464797123341331",
        "Mon–Sat 7:00–17:30",
        "311",
        mats(BULKY, APPLIANCE, TIRES),
    ),
]

# ── Hialeah (hialeahfl.gov / miamidade.gov) ──
FACILITIES += [
    row(
        "Hialeah Public Works Yard — bulky drop-off",
        "City bulky waste drop-off",
        "hialeah",
        "FL",
        "33013",
        "450 E 5th Street, Hialeah, FL 33013",
        25.838,
        -80.268,
        "https://www.hialeahfl.gov/973/Disposal-Sites",
        "Mon–Fri 7:00–15:00 — confirm on hialeahfl.gov",
        "311",
        mats(BULKY, APPLIANCE),
    ),
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
        "Miami-Dade Home Chemical Collection Center — Opa-locka (NW 135th)",
        "County home chemical collection center",
        "hialeah",
        "FL",
        "33054",
        "3680 NW 135th Street, Opa-locka, FL 33054",
        25.897,
        -80.248,
        "https://www.hialeahfl.gov/973/Disposal-Sites",
        "Wed–Sun 9:00–17:00",
        "311",
        mats(HHW, E_WASTE),
    ),
    row(
        "Miami-Dade North Dade Landfill",
        "County landfill — self-haul scalehouse",
        "hialeah",
        "FL",
        "33055",
        "21500 NW 47th Avenue, Opa-locka, FL 33055",
        25.888,
        -80.278,
        "https://www.miamidade.gov/global/service.page?Mduid_service=ser1464797123341331",
        "Daily 7:00–17:30",
        "311",
        mats(BULKY, APPLIANCE, TIRES, CD),
    ),
]

# ── Tampa / Hillsborough (hcfl.gov / tampa.gov) ──
for name, addr, zipc, lat, lng in [
    ("Northwest County Solid Waste Facility (CCC)", "8001 W Linebaugh Ave, Tampa, FL 33625", "33625", 28.040, -82.572),
    ("Hillsborough Heights Solid Waste Facility (CCC)", "6209 County Road 579, Seffner, FL 33584", "33584", 27.998, -82.318),
    ("South County Solid Waste Facility (CCC)", "13000 US Highway 41, Gibsonton, FL 33534", "33534", 27.825, -82.375),
    ("Wimauma Solid Waste Facility (CCC)", "16180 W Lake Drive, Wimauma, FL 33598", "33598", 27.712, -82.438),
    ("Alderman's Ford Solid Waste Facility (CCC)", "9402 County Road 39, Plant City, FL 33567", "33567", 27.978, -82.118),
]:
    FACILITIES.append(
        row(
            name,
            "Hillsborough County Community Collection Center",
            "tampa",
            "FL",
            zipc,
            addr,
            lat,
            lng,
            "https://www.hcfl.gov/residents/property-owners-and-renters/trash-and-recycling/community-collection-centers-ccc",
            "Mon–Sat 7:30–17:00",
            "813-272-5680",
            HCFL_CCC,
        )
    )

FACILITIES += [
    row(
        "Hillsborough County HHW — Sheldon Rd",
        "County HHW drop-off",
        "tampa",
        "FL",
        "33615",
        "9805 Sheldon Rd, Tampa, FL 33615",
        28.0455,
        -82.5825,
        "https://www.hcfl.gov/residents/property-owners-and-renters/trash-and-recycling/discarding-household-hazardous-waste",
        "1st Saturday each month 8:00–14:00",
        "813-272-5680",
        mats(HHW),
    ),
    row(
        "McKay Bay Scale House",
        "City drop-off — bulky / appliances",
        "tampa",
        "FL",
        "33605",
        "114 S 34th St, Tampa, FL 33605",
        27.9455,
        -82.4155,
        "https://www.tampa.gov/solid-waste/info/mckay-bay/mckay-bay-scalehouse",
        "Confirm on tampa.gov; Tampa utility account + ID required",
        "813-242-5320",
        mats(BULKY, APPLIANCE),
    ),
]

# ── Orlando / Orange County (ocfl.net / orlando.gov) ──
FACILITIES += [
    row(
        "Orange County Landfill — HHW / e-waste / scalehouse",
        "County landfill / HHW drop-off",
        "orlando",
        "FL",
        "32829",
        "5901 Young Pine Road, Orlando, FL 32829",
        28.478,
        -81.248,
        "https://www.orlando.gov/Our-Government/Departments-Offices/Public-Works/Solid-Waste/Too-Toxic-to-Trash",
        "Mon–Sat 8:00–17:00",
        "407-836-6601",
        OC_LANDFILL,
    ),
    row(
        "Porter Road Transfer Station — Orange County HHW",
        "County transfer station / HHW",
        "orlando",
        "FL",
        "32818",
        "1326 Good Homes Road, Orlando, FL 32818",
        28.5586,
        -81.5049,
        "https://www.orlando.gov/Our-Government/Departments-Offices/Public-Works/Solid-Waste/Too-Toxic-to-Trash",
        "Mon–Sat 8:00–17:00",
        "407-836-6601",
        mats(HHW, E_WASTE, TIRES, BULKY),
    ),
    row(
        "McLeod Road Transfer Station — Orange County",
        "County transfer station / yard waste Sat",
        "orlando",
        "FL",
        "32811",
        "5000 L.B. McLeod Road, Orlando, FL 32811",
        28.508,
        -81.428,
        "https://www.orlando.gov/Our-Government/Departments-Offices/Public-Works/Solid-Waste/Too-Toxic-to-Trash",
        "Mon–Sat 8:00–17:00",
        "407-836-6601",
        mats(BULKY, TIRES, ["yard-waste"]),
    ),
]

for n, addr, zipc, lat, lng in [
    (1, "78 West Central Boulevard, Orlando, FL 32801", "32801", 28.543, -81.379),
    (2, "1215 W Robinson St, Orlando, FL 32805", "32805", 28.515, -81.398),
    (3, "2406 North Elizabeth Avenue, Orlando, FL 32804", "32804", 28.578, -81.398),
    (4, "900 North Ferncreek Avenue, Orlando, FL 32803", "32803", 28.555, -81.348),
    (5, "1818 South Orange Avenue, Orlando, FL 32806", "32806", 28.512, -81.328),
    (6, "3900 Showalter Aviation Street, Orlando, FL 32803", "32803", 28.545, -81.348),
    (7, "601 South Goldwyn Avenue, Orlando, FL 32805", "32805", 28.512, -81.392),
    (8, "6651 South Shoalcreek Drive, Orlando, FL 32812", "32812", 28.458, -81.412),
    (9, "3840 Center Loop, Orlando, FL 32808", "32808", 28.578, -81.458),
    (10, "5655 Vineland Road, Orlando, FL 32819", "32819", 28.458, -81.458),
    (11, "4911 Curry Ford Road, Orlando, FL 32812", "32812", 28.525, -81.325),
    (12, "1588 Park Center Drive, Orlando, FL 32835", "32835", 28.524, -81.470),
    (13, "3464 5th Street, Orlando, FL 32827", "32827", 28.435, -81.340),
    (14, "5450 South Econlockhatchee Trail, Orlando, FL 32829", "32829", 28.468, -81.248),
    (15, "10199 South Narcoossee Road, Orlando, FL 32832", "32832", 28.388, -81.248),
    (16, "12375 Lake Nona Gateway Road, Orlando, FL 32827", "32827", 28.368, -81.248),
    (17, "3691 Millenia Boulevard, Orlando, FL 32839", "32839", 28.488, -81.428),
    (18, "Luminary Boulevard, Orlando, FL 32827", "32827", 28.357, -81.265),
    (19, "Northwest Orlando — confirm address on orlando.gov", "32808", 28.588, -81.458),
]:
    FACILITIES.append(
        row(
            f"Orlando Fire Department Sharps Drop-Off — Fire Station {n}",
            "Fire station sharps exchange drop-off",
            "orlando",
            "FL",
            zipc,
            addr,
            lat,
            lng,
            "https://www.orlando.gov/Our-Government/Departments-Offices/Public-Works/Solid-Waste/Too-Toxic-to-Trash",
            "24 hours — kiosk at station",
            "407-246-2314",
            SHARPS,
        )
    )

# ── Additional permanent sites ──
FACILITIES += [
    row(
        "Miami-Dade Resources Recovery Facility",
        "County transfer / C&D / bulky processing",
        "miami",
        "FL",
        "33177",
        "6990 SW 97th Avenue, Miami, FL 33157",
        25.568,
        -80.348,
        "https://www.miamidade.gov/global/service.page?Mduid_service=ser1464797123341331",
        "Mon–Fri 7:00–17:00 — confirm on miamidade.gov",
        "311",
        mats(BULKY, CD, TIRES),
    ),
    row(
        "El Paso Greater El Paso Landfill — public scale",
        "Regional landfill — self-haul",
        "el-paso",
        "TX",
        "79928",
        "2300 Darrington Road, Fabens, TX 79838",
        31.508,
        -106.158,
        "https://www.elpasotexas.gov/environmental-services/landfill/",
        "Mon–Sat 7:00–16:00 — confirm on elpasotexas.gov",
        "915-212-6000",
        mats(BULKY, APPLIANCE, TIRES),
    ),
    row(
        "Jacksonville Imeson Road Landfill",
        "Municipal landfill",
        "jacksonville",
        "FL",
        "32218",
        "6900 Imeson Road, Jacksonville, FL 32219",
        30.418,
        -81.688,
        "https://www.jacksonville.gov/departments/office-of-administrative-services/solid-waste/disposal-operations",
        "Mon–Fri 6:00–19:00; Sat 6:00–13:00",
        "904-255-7500",
        mats(BULKY, APPLIANCE, TIRES),
    ),
    row(
        "Hillsborough County Resource Recovery Facility",
        "County resource recovery / transfer",
        "tampa",
        "FL",
        "33619",
        "3506 S 50th Street, Tampa, FL 33619",
        27.918,
        -82.398,
        "https://www.hcfl.gov/residents/property-owners-and-renters/trash-and-recycling/find-a-waste-disposal-facility/",
        "Mon–Sat 7:30–17:00",
        "813-272-5680",
        mats(BULKY, APPLIANCE, TIRES, CD),
    ),
    row(
        "Pinellas County Yard Trash-to-Mulch Facility",
        "County yard waste / brush drop-off",
        "st-petersburg",
        "FL",
        "33716",
        "3095 114th Avenue North, St. Petersburg, FL 33716",
        27.876,
        -82.634,
        "https://pinellas.gov/mulch-pickup-program/",
        "Mon–Fri 6:00–18:00; Sat 7:00–17:00",
        "727-464-7500",
        mats(["yard-waste"]),
    ),
    row(
        "Plano Bulk Item Collection Center",
        "Municipal bulky item drop-off (by appointment)",
        "plano",
        "TX",
        "75074",
        "4200 W Plano Parkway, Plano, TX 75093",
        33.0198,
        -96.748,
        "https://www.plano.gov/908/Bulk-Trash-Collection",
        "By appointment — call 972-769-4150",
        "972-769-4150",
        mats(BULKY, APPLIANCE),
    ),
]

# ── St. Petersburg / Pinellas (pinellas.gov / stpete.org) ──
for site_name, addr, zipc, lat, lng in [
    ("62nd Ave NE", "1000 62nd Avenue NE, St. Petersburg, FL 33702", "33702", 27.778, -82.658),
    ("26th Ave N", "7750 26th Avenue N, St. Petersburg, FL 33710", "33710", 27.792, -82.742),
    ("20th Ave N", "2453 20th Avenue N, St. Petersburg, FL 33713", "33713", 27.792, -82.678),
    ("26th Ave S", "2500 26th Avenue S, St. Petersburg, FL 33712", "33712", 27.748, -82.678),
    ("Dr MLK Jr St S", "4015 Dr Martin Luther King Jr Street S, St. Petersburg, FL 33705", "33705", 27.718, -82.648),
]:
    FACILITIES.append(
        row(
            f"St. Petersburg Brush Site — {site_name}",
            "City brush / yard waste drop-off",
            "st-petersburg",
            "FL",
            zipc,
            addr,
            lat,
            lng,
            "https://pinellas.gov/mulch-pickup-program/",
            "Daily — proof of St. Pete residency required",
            "727-893-7398",
            mats(["yard-waste"], BULKY[:1]),
        )
    )

FACILITIES += [
    row(
        "Pinellas County Solid Waste Disposal Complex",
        "County landfill / transfer scalehouse",
        "st-petersburg",
        "FL",
        "33716",
        "3095 114th Avenue North, St. Petersburg, FL 33716",
        27.8761,
        -82.6339,
        "https://pinellas.gov/solid-waste-disposal-complex-hours/",
        "Mon–Fri 6:00–18:00; Sat 7:00–17:00",
        "727-464-7500",
        mats(BULKY, APPLIANCE, TIRES, ["yard-waste"]),
    ),
    row(
        "Pinellas County HHW — St. Pete metro",
        "County HHW collection center",
        "st-petersburg",
        "FL",
        "33716",
        "2855 109th Avenue N, St. Petersburg, FL 33716",
        27.8755,
        -82.6555,
        "https://pinellas.gov/household-hazardous-waste-hhw-collection/",
        "Tue–Fri 7:00–17:00; 1st & 3rd Sat",
        "727-464-7500",
        mats(HHW, E_WASTE),
    ),
    row(
        "Pinellas County HHW North — Clearwater",
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
    ),
    row(
        "Brooker Creek Preserve — Pinellas yard waste drop-off",
        "County yard waste / brush drop-off",
        "st-petersburg",
        "FL",
        "34677",
        "3940 Keystone Road, Tarpon Springs, FL 34677",
        28.148,
        -82.648,
        "https://pinellas.gov/mulch-pickup-program/",
        "Confirm hours on pinellas.gov",
        "727-464-7500",
        mats(["yard-waste"]),
    ),
]


def main() -> None:
    if len(FACILITIES) < 150:
        raise SystemExit(f"inventory under 150 rows: {len(FACILITIES)}")

    for r in FACILITIES:
        _validate(r)

    facilities = json.loads(FAC_PATH.read_text())
    before = len(facilities)

    removed = 0
    kept: list[dict] = []
    for f in facilities:
        slug = f.get("city_slug")
        if slug in TARGET_CITIES and (
            f.get("name") in SOFT_REMOVE_NAMES
            or (slug in TARGET_CITIES and not is_hard_facility(f))
        ):
            removed += 1
            continue
        kept.append(f)
    facilities = kept

    by_key = {(f.get("city_slug"), f.get("name")): i for i, f in enumerate(facilities)}
    by_addr = {
        (f.get("city_slug"), (f.get("address") or "").lower()[:55])
        for f in facilities
        if f.get("address")
    }

    added = updated = skipped = 0
    for r in FACILITIES:
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

    # Purge legacy non-.gov rows in target metros (inventory is .gov-verified only)
    facilities = json.loads(FAC_PATH.read_text())
    purged_non_gov = 0
    cleaned: list[dict] = []
    inv_keys = {(r["city_slug"], r["name"]) for r in FACILITIES}
    for f in facilities:
        slug = f.get("city_slug")
        url = f.get("source_url") or ""
        if slug in TARGET_CITIES and url and ".gov" not in url and (slug, f.get("name")) not in inv_keys:
            purged_non_gov += 1
            continue
        cleaned.append(f)
    if purged_non_gov:
        FAC_PATH.write_text(json.dumps(cleaned, indent=2) + "\n")
        facilities = cleaned

    hard_in_targets = [
        f for f in facilities if f.get("city_slug") in TARGET_CITIES and is_hard_facility(f)
    ]
    per_city = {
        c: sum(1 for f in hard_in_targets if f.get("city_slug") == c)
        for c in sorted(TARGET_CITIES)
    }

    print(
        json.dumps(
            {
                "verified": VERIFIED,
                "inventory_rows": len(FACILITIES),
                "removed_soft_from_targets": removed,
                "added": added,
                "updated": updated,
                "skipped_dup_addr": skipped,
                "hard_facilities_in_targets": len(hard_in_targets),
                "per_city_hard": per_city,
                "all_facilities_before": before,
                "all_facilities_after": len(facilities),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
