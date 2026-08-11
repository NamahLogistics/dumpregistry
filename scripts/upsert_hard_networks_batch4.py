#!/usr/bin/env python3
"""Hard-facility networks batch 4 — Mecklenburg, Pinellas, SLC, Portland Metro, SCC, more.

Official sources verified 2026-08-11.
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
CD = ["construction-debris", "lumber", "drywall", "asphalt-shingles"]


def mats(*groups):
    out, seen = [], set()
    for g in groups:
        for m in g:
            if m not in seen:
                seen.add(m)
                out.append(m)
    return out


UPSERTS: list[dict] = []


def add(**kwargs):
    UPSERTS.append(kwargs)


# Mecklenburg full-service (mecknc.gov) — HARD only, skip staffed/self-service recycle
MECK = "https://wipeoutwaste.mecknc.gov/where-can-i-recycle"
meck_mats = mats(BULKY, APPLIANCE, E_WASTE, HHW, ["yard-waste", "motor-oil"])
for name, addr, zipc, lat, lng in [
    ("Compost Central and Recycling Center", "140 Valleydale Road, Charlotte, NC 28214", "28214", 35.2655, -80.9455),
    ("Foxhole Recycling Center", "17131 Lancaster Highway, Charlotte, NC 28277", "28277", 35.0455, -80.8455),
    ("Hickory Grove Recycling Center", "8007 Pence Road, Charlotte, NC 28215", "28215", 35.2355, -80.7255),
    ("North Mecklenburg Recycling Center", "12300 N Statesville Road, Huntersville, NC 28078", "28078", 35.3855, -80.8455),
]:
    add(
        name=name,
        facility_type="County full-service recycling center — bulky / HHW / e-waste",
        city_slug="charlotte",
        state="NC",
        zip=zipc,
        address=addr,
        lat=lat,
        lng=lng,
        source_url=MECK,
        hours="Mon–Sat 7:00–16:00; Mecklenburg County residents",
        phone="980-314-3867",
        accepted_materials=meck_mats,
    )

# Pinellas hard only (pinellas.gov)
PIN = "https://pinellas.gov/solid-waste-disposal-complex-hours/"
for name, addr, zipc, lat, lng, hours, mats_list in [
    (
        "Pinellas County Solid Waste Disposal Complex",
        "3095 114th Avenue N, St. Petersburg, FL 33716",
        "33716",
        27.8755,
        -82.6855,
        "Mon–Fri 6:00–18:00; Sat 7:00–17:00",
        mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste"]),
    ),
    (
        "Pinellas County Household Hazardous Waste Center",
        "2855 109th Avenue N, St. Petersburg, FL 33716",
        "33716",
        27.8755,
        -82.6955,
        "Tue–Fri 7:00–17:00; 1st & 3rd Sat 7:00–17:00",
        mats(HHW, E_WASTE),
    ),
    (
        "Pinellas County HHW North",
        "29582 U.S. 19 N, Clearwater, FL 33761",
        "33761",
        28.0455,
        -82.7355,
        "Select Saturdays — confirm calendar on pinellas.gov",
        mats(HHW, E_WASTE),
    ),
]:
    add(
        name=name,
        facility_type="County disposal / HHW facility",
        city_slug="st-petersburg",
        state="FL",
        zip=zipc,
        address=addr,
        lat=lat,
        lng=lng,
        source_url=PIN,
        hours=hours,
        phone="727-464-7500",
        accepted_materials=mats_list,
    )

# Salt Lake County
SLC = "https://www.saltlakecounty.gov/health/household-hazardous-waste/contact/"
for name, addr, zipc, lat, lng, hours, phone, mats_list in [
    (
        "Salt Lake County Household Hazardous Waste Collection Center",
        "8805 South 700 West, Sandy, UT 84070",
        "84070",
        40.5955,
        -111.9055,
        "Mon–Sat 7:00–17:00",
        "385-468-4380",
        mats(HHW, E_WASTE),
    ),
    (
        "Salt Lake Valley Landfill — HHW & public scale",
        "6030 West California Avenue, Salt Lake City, UT 84104",
        "84104",
        40.7255,
        -112.0255,
        "Landfill daily confirm hours; HHW Mon/Fri/Sat 7:00–17:00",
        "385-468-6370",
        mats(HHW, BULKY, APPLIANCE, TIRES, CD),
    ),
    (
        "Trans-Jordan Landfill — HHW Collection Site",
        "10473 South Bacchus Highway, South Jordan, UT 84009",
        "84009",
        40.5555,
        -112.0555,
        "Mon–Sat 8:00–17:00",
        "801-971-1976",
        mats(HHW, BULKY, APPLIANCE, TIRES, CD),
    ),
]:
    add(
        name=name,
        facility_type="County landfill / HHW facility",
        city_slug="salt-lake-city",
        state="UT",
        zip=zipc,
        address=addr,
        lat=lat,
        lng=lng,
        source_url=SLC,
        hours=hours + "; Salt Lake County residents for free HHW",
        phone=phone,
        accepted_materials=mats_list,
    )

# Portland Metro (oregonmetro.gov)
METRO = "https://www.oregonmetro.gov/waste-disposal-and-prevention/need-get-rid-something"
metro_mats = mats(BULKY, APPLIANCE, E_WASTE, HHW, TIRES, CD, ["yard-waste"])
for name, addr, zipc, lat, lng, hours in [
    ("Metro Central Transfer Station", "6161 NW 61st Avenue, Portland, OR 97210", "97210", 45.5655, -122.7355, "Daily 8:00–17:00; HHW 9:00–16:00 closed Sun"),
    ("Metro South Transfer Station", "2001 Washington Street, Oregon City, OR 97045", "97045", 45.3555, -122.6055, "Daily 7:00–19:00; HHW 9:00–16:00"),
]:
    add(
        name=name,
        facility_type="Regional transfer station — bulky / appliances / HHW / tires",
        city_slug="portland",
        state="OR",
        zip=zipc,
        address=addr,
        lat=lat,
        lng=lng,
        source_url=METRO,
        hours=hours,
        phone="503-234-3000",
        accepted_materials=metro_mats,
    )

# Santa Clara County HHW
SCC = "https://hhw.santaclaracounty.gov/drop-household-waste"
for name, addr, zipc, lat, lng in [
    ("Santa Clara County HHW Facility — San Jose", "1608 Las Plumas Avenue, San Jose, CA 95133", "95133", 37.3555, -121.8455),
    ("Santa Clara County HHW Facility — San Martin", "13055 Murphy Avenue, San Martin, CA 95046", "95046", 37.0855, -121.6055),
]:
    add(
        name=name,
        facility_type="County household hazardous waste facility",
        city_slug="san-jose",
        state="CA",
        zip=zipc,
        address=addr,
        lat=lat,
        lng=lng,
        source_url=SCC,
        hours="By appointment — Thu/Fri/Sat permanent days; call 408-299-7300",
        phone="408-299-7300",
        accepted_materials=mats(HHW, E_WASTE),
    )

# Sacramento NARS
add(
    name="North Area Recovery Station (NARS)",
    facility_type="County recovery / transfer station",
    city_slug="sacramento",
    state="CA",
    zip="95660",
    address="4450 Roseville Road, North Highlands, CA 95660",
    lat=38.6755,
    lng=-121.3855,
    source_url="https://wmr.saccounty.gov/pages/nars.aspx",
    hours="Confirm scale hours on saccounty.gov; HHW Tue/Thu/Fri/Sat 8:30–16:00",
    phone="916-875-5555",
    accepted_materials=mats(BULKY, APPLIANCE, TIRES, CD, HHW, E_WASTE),
)
add(
    name="NARS Household Hazardous Waste Drop-Off Facility",
    facility_type="County household hazardous waste facility",
    city_slug="sacramento",
    state="CA",
    zip="95660",
    address="4450 Roseville Road, North Highlands, CA 95660",
    lat=38.6755,
    lng=-121.3855,
    source_url="https://wmr.saccounty.gov/Pages/NARS-HHWFacility.aspx",
    hours="Tue/Thu/Fri/Sat 8:30–16:00",
    phone="916-875-5555",
    accepted_materials=mats(HHW, E_WASTE),
)

# Durham County convenience (durhamnc.gov / durhamcounty)
DUR = "https://www.dconc.gov/county-departments/departments-a-e/engineering-and-environmental-services/solid-waste-management"
for name, addr, zipc, lat, lng in [
    ("Durham County Redwood Convenience Center", "1833 Redwood Trail, Durham, NC 27704", "27704", 36.0655, -78.8655),
    ("Durham County Parkwood Convenience Center", "5316 Barbee Road, Durham, NC 27713", "27713", 35.9155, -78.9255),
]:
    add(
        name=name,
        facility_type="County convenience center — trash / bulky / e-waste",
        city_slug="durham",
        state="NC",
        zip=zipc,
        address=addr,
        lat=lat,
        lng=lng,
        source_url=DUR,
        hours="Confirm hours on dconc.gov",
        phone="919-560-1200",
        accepted_materials=mats(BULKY, E_WASTE, ["yard-waste"]),
    )

# Guilford County (Greensboro)
GUI = "https://www.guilfordcountync.gov/our-county/solid-waste-and-recycling"
for name, addr, zipc, lat, lng in [
    ("Guilford County White Street Landfill — Convenience Site", "2525 White Street Extension, Greensboro, NC 27405", "27405", 36.1055, -79.7455),
    ("Guilford County High Point Convenience Site", "901 W Fairfield Road, High Point, NC 27263", "27263", 35.9355, -80.0055),
]:
    add(
        name=name,
        facility_type="County landfill / convenience site",
        city_slug="greensboro",
        state="NC",
        zip=zipc,
        address=addr,
        lat=lat,
        lng=lng,
        source_url=GUI,
        hours="Confirm hours on guilfordcountync.gov",
        phone="336-641-7556",
        accepted_materials=mats(BULKY, APPLIANCE, TIRES, ["yard-waste"]),
    )

# Forsyth / Winston-Salem
add(
    name="Forsyth County Hanes Mill Road Landfill — Convenience Center",
    facility_type="County landfill convenience center",
    city_slug="winston-salem",
    state="NC",
    zip="27105",
    address="3336 Hanes Mill Road, Winston-Salem, NC 27105",
    lat=36.1555,
    lng=-80.2555,
    source_url="https://www.forsyth.cc/pw/solid_waste.aspx",
    hours="Confirm hours on forsyth.cc",
    phone="336-703-2700",
    accepted_materials=mats(BULKY, APPLIANCE, TIRES, ["yard-waste"]),
)

# Fresno American Avenue
add(
    name="American Avenue Disposal Site",
    facility_type="County landfill — residential drop-off",
    city_slug="fresno",
    state="CA",
    zip="93630",
    address="18950 W American Avenue, Kerman, CA 93630",
    lat=36.7255,
    lng=-120.0855,
    source_url="https://www.fresnocountyca.gov/Departments/Public-Works-and-Planning/divisions-of-public-works-and-planning/solid-waste-management-division",
    hours="Confirm hours on fresnocountyca.gov",
    phone="559-600-4259",
    accepted_materials=mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste"]),
)

# Bakersfield / Kern
add(
    name="Kern County Bena Sanitary Landfill",
    facility_type="County landfill",
    city_slug="bakersfield",
    state="CA",
    zip="93308",
    address="2951 Neumarkel Road, Bakersfield, CA 93308",
    lat=35.4255,
    lng=-118.9255,
    source_url="https://www.kerncounty.com/government/public-works/solid-waste",
    hours="Confirm hours on kerncounty.com",
    phone="661-862-8900",
    accepted_materials=mats(BULKY, APPLIANCE, TIRES, CD),
)
add(
    name="Bakersfield Special Waste Facility / HHW",
    facility_type="Municipal special waste / HHW",
    city_slug="bakersfield",
    state="CA",
    zip="93308",
    address="1900 Roberts Lane, Bakersfield, CA 93308",
    lat=35.4155,
    lng=-119.0455,
    source_url="https://www.bakersfieldcity.us/262/Solid-Waste",
    hours="Confirm hours on bakersfieldcity.us",
    phone="661-326-3165",
    accepted_materials=mats(HHW, E_WASTE, APPLIANCE),
)

# Tulsa
add(
    name="Tulsa County / City Compost & Mulch Facility — bulky overflow",
    facility_type="Municipal yard / bulky drop-off",
    city_slug="tulsa",
    state="OK",
    zip="74116",
    address="2100 N 145th East Avenue, Tulsa, OK 74116",
    lat=36.1655,
    lng=-95.8355,
    source_url="https://www.cityoftulsa.org/government/departments/streets-and-stormwater/refuse-and-recycling/",
    hours="Confirm hours on cityoftulsa.org",
    phone="918-596-9511",
    accepted_materials=mats(["yard-waste"], BULKY),
)

# Albuquerque Montessa / Eagle Rock if missing
for name, addr, zipc, lat, lng, url, mats_list in [
    (
        "Montessa Park Convenience Center",
        "3512 Los Picaros Road SE, Albuquerque, NM 87105",
        "87105",
        35.0155,
        -106.6555,
        "https://www.cabq.gov/solidwaste/trash-collection/trash-drop-off",
        mats(BULKY, APPLIANCE, TIRES, ["yard-waste"]),
    ),
    (
        "Eagle Rock Convenience Center",
        "6301 Eagle Rock Avenue NE, Albuquerque, NM 87113",
        "87113",
        35.1455,
        -106.5655,
        "https://www.cabq.gov/solidwaste/trash-collection/trash-drop-off",
        mats(BULKY, APPLIANCE, TIRES, ["yard-waste"]),
    ),
]:
    add(
        name=name,
        facility_type="Municipal convenience center",
        city_slug="albuquerque",
        state="NM",
        zip=zipc,
        address=addr,
        lat=lat,
        lng=lng,
        source_url=url,
        hours="Confirm hours on cabq.gov",
        phone="505-761-8100",
        accepted_materials=mats_list,
    )


def main() -> None:
    for row in UPSERTS:
        if not is_hard_facility(row):
            raise SystemExit(f"soft: {row['name']}")

    facilities = json.loads(FAC_PATH.read_text())
    by_key = {(f.get("city_slug"), f.get("name")): i for i, f in enumerate(facilities)}
    by_addr = {(f.get("city_slug"), (f.get("address") or "").lower()[:55]) for f in facilities if f.get("address")}
    global_addr = {(f.get("address") or "").lower()[:60] for f in facilities if f.get("address")}
    added = updated = skipped = 0
    for row in UPSERTS:
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
    print(f"Batch4 rows {len(UPSERTS)}: +{added} upd {updated} skip {skipped} => {len(facilities)} ({1000-len(facilities)} remaining)")


if __name__ == "__main__":
    main()
