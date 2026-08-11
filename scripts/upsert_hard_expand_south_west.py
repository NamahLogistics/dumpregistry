#!/usr/bin/env python3
"""South + West hard facility expansion — unsaturated county networks (2026-08-11).

Official .gov / county sources. HARD ONLY. No prod deploy.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.facility_quality import is_hard_facility  # noqa: E402

FAC_PATH = ROOT / "data" / "facilities" / "all.json"

BULKY = ["mattress", "box-spring", "sofa", "recliner", "carpet", "yard-waste"]
APPLIANCE = [
    "refrigerator", "freezer", "air-conditioner", "washer", "dryer",
    "dishwasher", "stove", "water-heater", "dehumidifier", "microwave",
]
E_WASTE = [
    "television", "computer-monitor", "laptop", "desktop-computer", "printer",
    "tablet", "e-waste-mixed", "smartphone",
]
TIRES = ["tires", "tire-rims"]
HHW = [
    "paint-latex", "paint-oil", "pesticides", "herbicides", "motor-oil", "antifreeze",
    "car-battery", "household-batteries", "lithium-battery", "fluorescent-bulbs",
    "propane-tank", "gasoline", "pool-chemicals", "cooking-oil",
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


def norm_addr(addr: str) -> str:
    a = addr.lower()
    a = re.sub(r"\bst\b\.?", "street", a)
    a = re.sub(r"\bave\b\.?", "avenue", a)
    a = re.sub(r"\brd\b\.?", "road", a)
    a = re.sub(r"\bblvd\b\.?", "boulevard", a)
    a = re.sub(r"\bdr\b\.?", "drive", a)
    a = re.sub(r"\bln\b\.?", "lane", a)
    a = re.sub(r"[^a-z0-9]", "", a)
    return a[:60]


UPSERTS: list[dict] = []


def site(name, ftype, city, state, zipc, addr, lat, lng, url, hours, phone, materials):
    UPSERTS.append(
        {
            "name": name,
            "facility_type": ftype,
            "city_slug": city,
            "state": state,
            "zip": zipc,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": url,
            "hours": hours,
            "phone": phone,
            "accepted_materials": materials,
        }
    )


# ── Clackamas County OR (clackamas.us / oregonmetro.gov) → portland ──
site(
    "Clackamas County Garbage & Recycling Transfer Station — Sandy",
    "County transfer — bulky / appliances / tires / C&D",
    "portland",
    "OR",
    "97055",
    "19600 SE Canyon Valley Road, Sandy, OR 97055",
    45.375,
    -122.225,
    "https://www.clackamas.us/recycling/cc-transfer-station",
    "Confirm hours 503-260-1577 — clackamas.us",
    "503-260-1577",
    mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste"]),
)
site(
    "Metro South Transfer Station — Oregon City",
    "Regional Metro transfer — bulky / C&D / appliances",
    "portland",
    "OR",
    "97045",
    "2001 Washington Street, Oregon City, OR 97045",
    45.355,
    -122.595,
    "https://www.oregonmetro.gov/waste-disposal-and-prevention/need-get-rid-something/metro-south-transfer-station",
    "Daily 7:00–19:00 — oregonmetro.gov",
    "503-234-3000",
    mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste"]),
)
site(
    "Metro South Household Hazardous Waste Facility — Oregon City",
    "Regional Metro HHW / e-waste / paint / chemicals",
    "portland",
    "OR",
    "97045",
    "2001 Washington Street, Oregon City, OR 97045",
    45.355,
    -122.595,
    "https://www.clackamas.us/recycling/transferstation",
    "Daily 9:00–16:00 HHW — oregonmetro.gov",
    "503-234-3000",
    mats(HHW, E_WASTE),
)

# ── Snohomish County WA detail → seattle ──
SNO = "https://www.snohomishcountywa.gov/SWLocations"
site(
    "Snohomish County North County Recycling & Transfer — Arlington",
    "County transfer — bulky / appliances / tires / C&D",
    "seattle",
    "WA",
    "98223",
    "19600 63rd Avenue NE, Arlington, WA 98223",
    48.175,
    -122.155,
    SNO,
    "Daily 7:00–16:30 — snohomishcountywa.gov",
    "425-388-3425",
    mats(BULKY, APPLIANCE, TIRES, CD),
)
site(
    "Snohomish County Airport Road Recycling & Transfer — Everett",
    "County transfer — bulky / appliances / tires / C&D",
    "seattle",
    "WA",
    "98204",
    "10700 Minuteman Drive, Everett, WA 98204",
    47.915,
    -122.275,
    SNO,
    "Daily 7:00–16:30 — snohomishcountywa.gov",
    "425-388-3425",
    mats(BULKY, APPLIANCE, TIRES, CD),
)
site(
    "Snohomish County Southwest Recycling & Transfer — Mountlake Terrace",
    "County transfer — bulky / appliances / tires / C&D",
    "seattle",
    "WA",
    "98043",
    "21311 61st Place West, Mountlake Terrace, WA 98043",
    47.795,
    -122.325,
    SNO,
    "Daily 7:00–16:30 — snohomishcountywa.gov",
    "425-388-3425",
    mats(BULKY, APPLIANCE, TIRES, CD),
)
site(
    "Snohomish County Household Hazardous Waste Drop-Off — Everett",
    "County HHW permanent station",
    "seattle",
    "WA",
    "98201",
    "3434 McDougall Avenue, Everett, WA 98201",
    47.975,
    -122.205,
    "https://snohomishcountywa.gov/477/Hazardous-Waste",
    "Wed–Sat 8:00–16:00 households — snohomishcountywa.gov",
    "425-388-6050",
    mats(HHW, E_WASTE),
)
site(
    "Snohomish County Dubuque Road Drop Box",
    "County drop box — bulky / yard waste / residential MSW",
    "seattle",
    "WA",
    "98290",
    "19619 Dubuque Road, Snohomish, WA 98290",
    47.975,
    -121.925,
    SNO,
    "Fri–Tue 7:00–16:30 — snohomishcountywa.gov",
    "425-388-3425",
    mats(BULKY, ["yard-waste"], TIRES),
)
site(
    "Snohomish County Granite Falls Drop Box",
    "County drop box — bulky / yard waste",
    "seattle",
    "WA",
    "98252",
    "7526 Menzel Lake Road, Granite Falls, WA 98252",
    48.085,
    -121.965,
    SNO,
    "Thu/Sat/Sun 7:00–16:30 — snohomishcountywa.gov",
    "425-388-3425",
    mats(BULKY, ["yard-waste"], TIRES),
)
site(
    "Snohomish County Sultan Drop Box",
    "County drop box — bulky / yard waste",
    "seattle",
    "WA",
    "98294",
    "33014 Cascade View Drive, Sultan, WA 98294",
    47.865,
    -121.815,
    SNO,
    "Wed–Sun 7:00–16:30 — snohomishcountywa.gov",
    "425-388-3425",
    mats(BULKY, ["yard-waste"], TIRES),
)

# ── El Paso County CO (elpasoco.com) → colorado-springs ──
site(
    "El Paso County Household Hazardous Waste Facility — Akers Drive",
    "County HHW — El Paso / Teller residents",
    "colorado-springs",
    "CO",
    "80922",
    "3255 Akers Drive, Colorado Springs, CO 80922",
    38.885,
    -104.715,
    "https://communityresources.elpasoco.com/environmental-division/household-hazardous-waste/",
    "Mon/Tue/Thu/Fri 8:30–12:00 & 13:00–16:00 — elpasoco.com",
    "719-520-7878",
    mats(HHW, E_WASTE),
)
site(
    "Colorado Springs Landfill — Blaney Road",
    "Municipal landfill — bulky / appliances / Freon / C&D",
    "colorado-springs",
    "CO",
    "80929",
    "1010 Blaney Road, Colorado Springs, CO 80929",
    38.775,
    -104.705,
    "https://coloradosprings.gov/",
    "Confirm hours 719-683-2600",
    "719-683-2600",
    mats(BULKY, APPLIANCE, TIRES, CD),
)
site(
    "WM Midway Landfill — Fountain / Colorado Springs",
    "Regional landfill — bulky / C&D / residential MSW",
    "colorado-springs",
    "CO",
    "80817",
    "8925 Rancho Colorado Boulevard, Fountain, CO 80817",
    38.665,
    -104.695,
    "https://www.wm.com/",
    "Confirm hours 719-382-8383",
    "719-382-8383",
    mats(BULKY, APPLIANCE, TIRES, CD),
)
site(
    "Fountain Landfill — Squirrel Creek Road",
    "Regional landfill — bulky / C&D / residential MSW",
    "colorado-springs",
    "CO",
    "80817",
    "10525 Squirrel Creek Road, Fountain, CO 80817",
    38.685,
    -104.655,
    "https://www.wasteconnections.com/fountain-landfill",
    "Confirm hours — wasteconnections.com",
    "719-382-9661",
    mats(BULKY, APPLIANCE, TIRES, CD),
)

# ── Gwinnett County GA landfills/transfers → atlanta ──
GWIN = "https://gwinnettcb.org/landfills-list/"
site(
    "Republic Services Buford Landfill — Richland Creek",
    "Regional landfill — bulky / C&D (no tires/batteries/paint)",
    "atlanta",
    "GA",
    "30518",
    "5691 South Richland Creek Road, Buford, GA 30518",
    34.085,
    -84.025,
    GWIN,
    "Mon–Fri 7:00–15:30; Sat 6:00–11:30 — gwinnettcb.org",
    "678-963-2800",
    mats(BULKY, APPLIANCE, CD),
)
site(
    "B.J. Transfer Station — Norcross / Gwinnett",
    "Transfer station — bulky / C&D residential",
    "atlanta",
    "GA",
    "30071",
    "6461 Corley Road NW, Norcross, GA 30071",
    33.935,
    -84.225,
    GWIN,
    "Mon–Fri early open–16:30; Sat 6:00–11:30 — gwinnettcb.org",
    "770-448-3997",
    mats(BULKY, CD, ["carpet", "mattress"]),
)
site(
    "Central Gwinnett Transfer Station — Lawrenceville",
    "Transfer station — bulky / C&D",
    "atlanta",
    "GA",
    "30044",
    "535 Seaboard Industrial Drive, Lawrenceville, GA 30044",
    33.945,
    -84.015,
    GWIN,
    "Mon–Fri 6:30–15:45 — gwinnettcb.org",
    "770-237-8477",
    mats(BULKY, APPLIANCE, CD),
)
site(
    "WM Transfer Station — Maltbie Industrial / Lawrenceville",
    "Transfer station — bulky / residential MSW",
    "atlanta",
    "GA",
    "30046",
    "350 Maltbie Industrial Boulevard, Lawrenceville, GA 30046",
    33.955,
    -83.995,
    GWIN,
    "Mon–Fri 6:00–15:30 — gwinnettcb.org",
    "770-513-2442",
    mats(BULKY, CD),
)
site(
    "Gwinnett County HHW Collection Day — Fairgrounds",
    "County biannual HHW event site — Lawrenceville",
    "atlanta",
    "GA",
    "30045",
    "2405 Sugarloaf Parkway, Lawrenceville, GA 30045",
    33.955,
    -84.045,
    "https://gwinnettcb.org/events/household-hazardous-waste-collection-day/",
    "Scheduled HHW collection days — gwinnettcb.org / gwinnettcounty.com",
    "770-822-8840",
    mats(HHW),
)

# ── Tulsa HPCF detail → tulsa ──
site(
    "City of Tulsa Household Pollutant Collection Facility",
    "Municipal HHW / paint / chemicals — appointment",
    "tulsa",
    "OK",
    "74107",
    "4502 S Galveston Avenue, Tulsa, OK 74107",
    36.095,
    -96.005,
    "https://www.cityoftulsa.org/government/departments/public-works/household-pollutant-collection-facility/",
    "Wed & Sat 8:00–11:30 & 12:00–16:30 by appointment — cityoftulsa.org",
    "918-591-4325",
    mats(HHW, E_WASTE),
)

# ── Jefferson County CO Rooney Road for aurora thin metro ──
site(
    "Rooney Road Recycling Center — Jefferson County HHW (Aurora hub)",
    "County HHW / e-waste — Jeffco + partner cities",
    "aurora",
    "CO",
    "80401",
    "151 South Rooney Road, Golden, CO 80401",
    39.715,
    -105.185,
    "https://www.rooneyroadrecycling.org/",
    "Wed & Sat 8:00–14:00 by appointment — rooneyroadrecycling.org",
    "303-316-6262",
    mats(HHW, E_WASTE),
)

# ── Pierce County WA HHW detail for tacoma ──
site(
    "Tacoma Recovery & Transfer Center — Household Hazardous Waste",
    "Municipal transfer + HHW — Tacoma residents",
    "tacoma",
    "WA",
    "98409",
    "3510 S Mullen Street, Tacoma, WA 98409",
    47.225,
    -122.505,
    "https://www.cityoftacoma.org/government/city_departments/environmentalservices/solid_waste/hazardous_waste",
    "Fri–Mon 8:00–17:30 HHW — cityoftacoma.org",
    "253-502-2100",
    mats(HHW, E_WASTE, BULKY, APPLIANCE, TIRES),
)
site(
    "Pierce County Hidden Valley Transfer — HHW Facility",
    "County/LRI HHW at Hidden Valley transfer",
    "tacoma",
    "WA",
    "98375",
    "17925 Meridian Avenue E, Puyallup, WA 98375",
    47.105,
    -122.295,
    "https://www.lriservices.com/lri-hidden-valley/household-hazardous-waste-facility",
    "Tue & Thu 8:00–12:00 & 13:00–17:00 — piercecountywa.gov",
    "253-847-7555",
    mats(HHW, E_WASTE),
)

# ── Ada County ID HHW detail → boise ──
site(
    "Ada County Household Hazardous Waste Facility — Seamans Gulch",
    "County HHW at landfill campus",
    "boise",
    "ID",
    "83714",
    "10300 N Seamans Gulch Road, Boise, ID 83714",
    43.665,
    -116.275,
    "https://adacounty.id.gov/landfill/waste-types-solutions/hazardous-waste/",
    "Fri & Sat 8:00–18:00 — adacounty.id.gov",
    "208-577-4737",
    mats(HHW, E_WASTE),
)
site(
    "Ada County Landfill — North Ravine / Hidden Hollow campus",
    "County landfill — bulky / appliances / tires / C&D",
    "boise",
    "ID",
    "83714",
    "10300 N Seamans Gulch Road, Boise, ID 83714",
    43.664,
    -116.274,
    "https://adacounty.id.gov/landfill/contact-connect/landfill-hours-of-operations/",
    "Confirm landfill hours — adacounty.id.gov",
    "208-577-4725",
    mats(BULKY, APPLIANCE, TIRES, CD),
)

# ── Bernalillo / Albuquerque detail ──
site(
    "City of Albuquerque Cerro Colorado Landfill",
    "Municipal landfill — bulky / C&D / appliances / tires",
    "albuquerque",
    "NM",
    "87121",
    "18000 Cerro Colorado SW, Albuquerque, NM 87121",
    35.015,
    -106.825,
    "https://www.cabq.gov/solidwaste",
    "Confirm hours — cabq.gov/solidwaste",
    "505-761-8300",
    mats(BULKY, APPLIANCE, TIRES, CD),
)
site(
    "City of Albuquerque Household Hazardous Waste Collection Center — Safety-Kleen",
    "Municipal/county HHW drop-off — Safety-Kleen contract",
    "albuquerque",
    "NM",
    "87107",
    "2720 Girard NE, Albuquerque, NM 87107",
    35.105,
    -106.615,
    "https://www.cabq.gov/solidwaste/hazardous-waste",
    "Mon/Wed/Fri 8:00–14:00; Sat 8:00–15:00 — cabq.gov",
    "505-884-2277",
    mats(HHW, E_WASTE),
)

# ── Washoe / Reno tire & transfer detail ──
site(
    "WM Lockwood Regional Landfill — Sparks / Washoe",
    "Regional landfill — bulky / C&D / appliances / tires",
    "reno",
    "NV",
    "89434",
    "2700 East Mustang Road, Sparks, NV 89434",
    39.515,
    -119.575,
    "https://www.wm.com/us/en/facilities/lockwood-landfill",
    "Mon–Sat 8:00–16:30 — wm.com",
    "775-342-0401",
    mats(BULKY, APPLIANCE, TIRES, CD),
)

# ── Henderson / Clark County NV ──
site(
    "Republic Services Apex Landfill — Clark County",
    "Regional landfill — bulky / C&D / residential MSW",
    "henderson",
    "NV",
    "89018",
    "1 Apex Landfill Way, Las Vegas, NV 89124",
    36.385,
    -114.915,
    "https://www.republicservices.com/",
    "Confirm hours — Republic Services Apex",
    "702-642-0200",
    mats(BULKY, APPLIANCE, TIRES, CD),
)
site(
    "City of Henderson Transfer Station / Public Works drop-off",
    "Municipal transfer / bulky drop-off",
    "henderson",
    "NV",
    "89015",
    "240 S Water Street, Henderson, NV 89015",
    36.035,
    -114.985,
    "https://www.cityofhenderson.com/",
    "Confirm hours — cityofhenderson.com",
    "702-267-1200",
    mats(BULKY, APPLIANCE, TIRES, ["yard-waste"]),
)


def main() -> None:
    existing = json.loads(FAC_PATH.read_text())
    by_key = {}
    by_addr = {}
    for i, row in enumerate(existing):
        key = (row.get("city_slug"), (row.get("name") or "").strip().lower())
        by_key[key] = i
        na = norm_addr(row.get("address") or "")
        if na:
            by_addr[(row.get("city_slug"), na)] = i

    added = updated = skipped_soft = 0
    for row in UPSERTS:
        if not is_hard_facility(row):
            skipped_soft += 1
            continue
        key = (row["city_slug"], row["name"].strip().lower())
        na = norm_addr(row.get("address") or "")
        addr_key = (row["city_slug"], na) if na else None
        if key in by_key:
            i = by_key[key]
            existing[i] = {**existing[i], **row}
            updated += 1
        elif addr_key and addr_key in by_addr:
            i = by_addr[addr_key]
            existing[i] = {**existing[i], **row}
            updated += 1
        else:
            existing.append(row)
            by_key[key] = len(existing) - 1
            if addr_key:
                by_addr[addr_key] = len(existing) - 1
            added += 1

    hard = [r for r in existing if is_hard_facility(r)]
    soft_dropped = len(existing) - len(hard)
    FAC_PATH.write_text(json.dumps(hard, indent=2, ensure_ascii=False) + "\n")
    print(
        f"added={added} updated={updated} skipped_soft={skipped_soft} "
        f"soft_dropped={soft_dropped} hard_total={len(hard)} upserts={len(UPSERTS)}"
    )


if __name__ == "__main__":
    main()
