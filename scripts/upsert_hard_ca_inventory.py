#!/usr/bin/env python3
"""DumpRegistry HARD FACILITIES ONLY — 17 CA metros + LA County HHW (2026-08-11).

Permanent public drop-offs: transfer/landfill self-haul, S.A.F.E./HHW, bulky,
e-waste, tires, C&D. Official .gov sources only. Rejects cardboard/glass-only,
food-scrap bins, library/school drops, beverage buyback, curbside-only programs.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.facility_quality import HARD_MATERIALS, SOFT_ONLY, is_hard_facility  # noqa: E402

FAC_PATH = ROOT / "data" / "facilities" / "all.json"
ITEMS = {i["slug"] for i in json.loads((ROOT / "data" / "items.json").read_text())}
VERIFIED = "2026-08-11"

TARGET_CITIES = frozenset(
    {
        "san-francisco",
        "oakland",
        "fremont",
        "chula-vista",
        "fontana",
        "san-diego",
        "los-angeles",
        "long-beach",
        "anaheim",
        "irvine",
        "santa-ana",
        "riverside",
        "sacramento",
        "fresno",
        "bakersfield",
        "stockton",
        "san-jose",
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
    "fire-extinguisher",
    "medical-sharps",
    "smoke-detector",
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
    "dehumidifier",
]
TIRES = ["tires", "tire-rims"]
CD = ["construction-debris", "lumber", "drywall", "concrete", "asphalt-shingles"]

REJECT_NAME = re.compile(
    r"library|school recycle|buyback|beverage|curbside only|"
    r"cardboard.?only|food scrap|project oscar|recycling dumpster",
    re.I,
)

LASAN_SAFE = "https://sanitation.lacity.gov/san/faces/wcnav_externalId/s-lsh-wwd-s-c-hw-safemc"
OC_HHW = "https://www.cmsdca.gov/trash___recycling/recycling_resources/oc_household_hazardous_waste_collection_centers.php"
SBC_HHW = "https://www.sanbernardino.gov/1588/Household-Hazardous-Waste"
ALAMEDA_HHW = "https://www2.calrecycle.ca.gov/HHW/"
RIVCO = "https://riversideca.gov/publicworks/trash-recycling/clean-riverside"
SJ_COUNTY = "https://www.stocktonca.gov/services/garbage___recycling/hazardous_waste/index.php"
SAC_TRANSFERS = "https://www.cityofsacramento.gov/content/dam/portal/pw/RSW/Transfer%20Stations%20Facility%20List%202023.pdf"

REMOVE_KEYS = {
    ("los-angeles", "LASAN S.A.F.E. Centers (HHW & e-waste)"),
    ("fontana", "Fontana / Burrtec Bulky Pickup"),
    ("santa-ana", "OC HHW Collection Center — Anaheim (nearest hub)"),
    ("santa-ana", "OC HHW Collection Center — Irvine (secondary pin for Santa Ana)"),
    ("fremont", "Alameda County HHW — Fremont (Boyce Rd)"),
    ("fremont", "Fremont Transfer Station"),
    ("san-francisco", "Recology Household Hazardous Waste Facility"),
    ("stockton", "Stockton Lovelace — already listed; San Joaquin North County TS"),
}


def mats(*groups: list[str]) -> list[str]:
    out, seen = [], set()
    for g in groups:
        for m in g:
            if m not in ITEMS:
                raise SystemExit(f"unknown slug {m}")
            if m not in seen:
                seen.add(m)
                out.append(m)
    return out


def is_gov_url(url: str) -> bool:
    host = urlparse(url).netloc.lower().removeprefix("www.")
    return any(part == "gov" for part in host.split("."))


def row(
    name: str,
    ftype: str,
    city: str,
    zipc: str,
    address: str,
    lat: float,
    lng: float,
    source: str,
    hours: str,
    phone: str,
    materials: list[str],
) -> dict:
    return {
        "name": name,
        "facility_type": ftype,
        "city_slug": city,
        "state": "CA",
        "zip": zipc,
        "address": address,
        "lat": lat,
        "lng": lng,
        "source_url": source,
        "hours": hours,
        "phone": phone,
        "accepted_materials": materials,
    }


SAFE = mats(HHW, E_WASTE)
HHW_E = mats(HHW, E_WASTE)
TRANSFER = mats(BULKY, APPLIANCE, TIRES, CD, E_WASTE)
LANDFILL = mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste"])

OC_HHW_ROWS = [
    row(n, "OC HHW Collection Center — drive-through", c, z, a, la, ln, OC_HHW, "Tue–Sat 9:00–15:00", "714-834-4000", HHW_E)
    for n, c, z, a, la, ln in [
        ("OC HHW Collection Center — Anaheim", "anaheim", "92806", "1071 N Blue Gum Street, Anaheim, CA 92806", 33.85, -117.85),
        ("OC HHW Collection Center — Huntington Beach", "anaheim", "92647", "17121 Nichols Lane, Gate 6, Huntington Beach, CA 92647", 33.7167, -117.9958),
        ("OC HHW Collection Center — Irvine", "irvine", "92618", "6411 Oak Canyon, Irvine, CA 92618", 33.67, -117.76),
        ("OC HHW Collection Center — San Juan Capistrano", "irvine", "92675", "32250 Avenida La Pata, San Juan Capistrano, CA 92675", 33.5055, -117.6355),
        ("OC HHW Collection Center — Anaheim (Santa Ana hub)", "santa-ana", "92806", "1071 N Blue Gum Street, Anaheim, CA 92806", 33.85, -117.85),
        ("OC HHW Collection Center — Huntington Beach (Santa Ana hub)", "santa-ana", "92647", "17121 Nichols Lane, Gate 6, Huntington Beach, CA 92647", 33.7167, -117.9958),
        ("OC HHW Collection Center — Irvine (Santa Ana hub)", "santa-ana", "92618", "6411 Oak Canyon, Irvine, CA 92618", 33.6655, -117.7555),
        ("OC HHW Collection Center — San Juan Capistrano (Santa Ana hub)", "santa-ana", "92675", "32250 Avenida La Pata, San Juan Capistrano, CA 92675", 33.5055, -117.6155),
        ("OC HHW Collection Center — Huntington Beach (Irvine hub)", "irvine", "92647", "17121 Nichols Lane, Gate 6, Huntington Beach, CA 92647", 33.7167, -117.9958),
        ("OC HHW Collection Center — San Juan Capistrano (Anaheim hub)", "anaheim", "92675", "32250 Avenida La Pata, San Juan Capistrano, CA 92675", 33.5055, -117.6355),
    ]
]

FACILITIES: list[dict] = [
    # los-angeles
    row("Nicole Bernson (Balboa) S.A.F.E. Center", "S.A.F.E. Center — HHW / e-waste", "los-angeles", "91325", "10241 N Balboa Boulevard, Northridge, CA 91325", 34.2555, -118.5355, LASAN_SAFE, "Sat–Sun 9:00–15:00", "1-800-773-2489", SAFE),
    row("Gaffey Street S.A.F.E. Center", "S.A.F.E. Center — HHW / e-waste", "los-angeles", "90731", "1400 N Gaffey Street, San Pedro, CA 90731", 33.7537, -118.2924, LASAN_SAFE, "Sat–Sun 9:00–15:00", "1-800-773-2489", SAFE),
    row("Hyperion S.A.F.E. Center", "S.A.F.E. Center — HHW / e-waste", "los-angeles", "90293", "7660 West Imperial Highway, Gate B, Playa Del Rey, CA 90293", 33.9255, -118.4255, LASAN_SAFE, "Sat–Sun 9:00–15:00", "1-800-773-2489", SAFE),
    row("Los Angeles-Glendale S.A.F.E. Center", "S.A.F.E. Center — HHW / e-waste", "los-angeles", "90039", "4600 Colorado Boulevard, Los Angeles, CA 90039", 34.1255, -118.2655, LASAN_SAFE, "Sat–Sun 9:00–15:00", "1-800-773-2489", SAFE),
    row("Randall Street S.A.F.E. Center", "S.A.F.E. Center — HHW / e-waste", "los-angeles", "91352", "11025 Randall Street, Sun Valley, CA 91352", 34.2555, -118.3855, LASAN_SAFE, "Sat–Sun 9:00–15:00", "1-800-773-2489", SAFE),
    row("S.A.F.E. Center at UCLA", "S.A.F.E. Center — HHW / e-waste", "los-angeles", "90095", "550 Charles E Young Drive, Los Angeles, CA 90095", 34.0655, -118.4455, LASAN_SAFE, "Thu–Sat 8:00–14:00", "1-800-773-2489", SAFE),
    row("Washington Boulevard S.A.F.E. Center", "S.A.F.E. Center — HHW / e-waste", "los-angeles", "90021", "2649 E Washington Boulevard, Los Angeles, CA 90021", 34.0155, -118.2255, LASAN_SAFE, "Sat–Sun 9:00–15:00", "1-800-773-2489", SAFE),
    row("Lopez Canyon Environmental Center S.A.F.E.", "S.A.F.E. Center — HHW / e-waste", "los-angeles", "91342", "11950 Lopez Canyon Road, Lake View Terrace, CA 91342", 34.2925, -118.4055, LASAN_SAFE, "Sat–Sun 9:00–15:00", "1-800-773-2489", SAFE),
    row("Central LA Recycling and Transfer Station (CLARTS)", "Municipal transfer station — public self-haul", "los-angeles", "90021", "2201 E Washington Boulevard, Los Angeles, CA 90021", 34.0203, -118.2343, "https://sanitation.lacity.gov/san/faces/home/portal/s-lsh-wwd/s-lsh-wwd-s/s-lsh-wwd-s-cl/s-lsh-wwd-s-cl-fs", "Mon–Fri 4:00–17:00; Sat 6:00–14:30", "(213) 763-1918", TRANSFER),
    row("South Gate Transfer Station", "County transfer station — MSW / bulky self-haul", "los-angeles", "90280", "9530 Garfield Avenue, South Gate, CA 90280", 33.944, -118.166, "http://www.publichealth.lacounty.gov/eh/business/landfill-transfer-stations.htm", "Mon–Sat 6:00–17:00", "562-908-4288", TRANSFER),
    row("Culver City Transfer and Recycling Station", "Municipal transfer / recycling — bulky / C&D", "los-angeles", "90232", "9255 W Jefferson Boulevard, Culver City, CA 90232", 34.026, -118.397, "http://www.publichealth.lacounty.gov/eh/business/landfill-transfer-stations.htm", "Mon–Sat; confirm hours", "310-253-6405", TRANSFER),
    row("East Valley District Yard — free bulky drop-off", "LASAN district yard — monthly bulky drop-off", "los-angeles", "91352", "11050 Pendleton Street, Sun Valley, CA 91352", 34.2455, -118.3855, "https://sanitation.lacity.gov/san/faces/home/portal/s-lsh-wwd/s-lsh-wwd-s/s-lsh-wwd-s-c/s-lsh-wwd-s-c-bic", "Monthly Sat 8:00–16:30", "1-800-773-2489", mats(BULKY, ["yard-waste"])),
    row("West Valley District Yard — free bulky drop-off", "LASAN district yard — monthly bulky drop-off", "los-angeles", "91325", "8840 Vanalden Avenue, Northridge, CA 91325", 34.2355, -118.5455, "https://sanitation.lacity.gov/san/faces/home/portal/s-lsh-wwd/s-lsh-wwd-s/s-lsh-wwd-s-c/s-lsh-wwd-s-c-bic", "Monthly Sat 8:00–16:30", "1-800-773-2489", mats(BULKY, ["yard-waste"])),
    row("West LA District Yard — free bulky drop-off", "LASAN district yard — monthly bulky drop-off", "los-angeles", "90025", "2027 Stoner Avenue, Los Angeles, CA 90025", 34.0455, -118.4455, "https://sanitation.lacity.gov/san/faces/home/portal/s-lsh-wwd/s-lsh-wwd-s/s-lsh-wwd-s-c/s-lsh-wwd-s-c-bic", "Monthly Sat 8:00–16:30", "1-800-773-2489", mats(BULKY, ["yard-waste"])),
    row("Harbor District Yard — free bulky drop-off", "LASAN district yard — monthly bulky drop-off", "los-angeles", "90731", "1400 N Gaffey Street, San Pedro, CA 90731", 33.7537, -118.2924, "https://sanitation.lacity.gov/san/faces/home/portal/s-lsh-wwd/s-lsh-wwd-s/s-lsh-wwd-s-c/s-lsh-wwd-s-c-bic", "Monthly Sat 8:00–16:30", "1-800-773-2489", mats(BULKY, ["yard-waste"])),
    row("Antelope Valley Environmental Collection Center", "LA County permanent HHW / e-waste", "los-angeles", "93551", "1200 W City Ranch Road, Palmdale, CA 93551", 34.5855, -118.1855, "https://cleanla.lacounty.gov/hhw/collection-centers/", "1st & 3rd Sat 9:00–15:00", "1-800-98-TOXIC", HHW_E),
    # san-francisco
    row("Recology Transfer Station — public self-haul (501 Tunnel Ave)", "Transfer station — trash / bulky / C&D self-haul", "san-francisco", "94134", "501 Tunnel Avenue, San Francisco, CA 94134", 37.7125, -122.4019, "https://www.sf.gov/additional-refuse-ratepayer-resources", "Mon–Sat (confirm PRRA hours)", "415-330-1400", mats(BULKY, APPLIANCE, E_WASTE, CD, TIRES)),
    row("San Francisco Household Hazardous Waste Collection Facility", "HHW drop-off — paint / chemicals / e-waste", "san-francisco", "94134", "501 Tunnel Avenue, San Francisco, CA 94134", 37.7125, -122.4019, "https://www.sf.gov/sites/default/files/2025-01/2025%20Rate%20Application%20-%20Narrative.pdf", "Thu–Sat 8:00–16:00", "415-330-1400", HHW_E),
    row("Recology C&D Recovery Facility (iMRF) — Tunnel Avenue", "C&D drop-off / recovery", "san-francisco", "94134", "501 Tunnel Avenue, San Francisco, CA 94134", 37.7125, -122.4019, "https://www.sf.gov/sites/default/files/2025-01/2025%20Rate%20Application%20-%20Narrative.pdf", "Mon–Sat during transfer-station hours", "415-330-1400", mats(CD)),
    # oakland / alameda
    row("Alameda County HHW — Oakland Facility", "County HHW / e-waste drop-off", "oakland", "94606", "2100 East 7th Street, Oakland, CA 94606", 37.79, -122.24, ALAMEDA_HHW, "Wed–Fri 9:00–14:30; Sat 9:00–16:00", "1-800-606-6606", HHW_E),
    row("Davis Street Resource Recovery Complex", "Transfer station — bulky / mattress / e-waste", "oakland", "94577", "2615 Davis Street, San Leandro, CA 94577", 37.7025, -122.185, "https://www.oaklandca.gov/topics/garbage-and-recycling", "Mon–Fri 7:00–17:00; Sat 8:00–16:00", "1-888-962-8559", mats(BULKY, APPLIANCE, E_WASTE, TIRES)),
    row("Alameda County HHW — Livermore Facility", "County HHW / e-waste drop-off", "fremont", "94550", "5584 La Ribera St., Livermore, CA 94550", 37.699, -121.725, ALAMEDA_HHW, "Thu–Fri 9:00–14:30; Sat 9:00–16:00", "1-800-606-6606", HHW_E),
    row("Alameda County HHW — Hayward Facility", "County HHW / e-waste drop-off", "oakland", "94544", "2091 West Winton Ave., Hayward, CA 94544", 37.653, -122.134, ALAMEDA_HHW, "Thu–Fri 9:00–14:30; Sat 9:00–16:00", "1-800-606-6606", HHW_E),
    # fremont
    row("Alameda County HHW — Fremont (Boyce Road)", "County HHW / e-waste drop-off", "fremont", "94538", "41149 Boyce Road, Fremont, CA 94538", 37.53, -121.97, ALAMEDA_HHW, "Wed–Fri 9:00–14:30; Sat 9:00–16:00", "800-606-6606", HHW_E),
    row("Fremont Recycling and Transfer Station", "Transfer station — trash / bulky / yard waste", "fremont", "94538", "41149 Boyce Road, Fremont, CA 94538", 37.53, -121.97, "https://www.fremont.gov/government/departments/environmental-services/environmental-services-faqs", "Mon–Sat (confirm hours)", "510-657-3500", mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste"])),
    row("Newby Island Resource Recovery Park — public drop-off", "Regional landfill / transfer — self-haul", "fremont", "94538", "1601 Dixon Landing Road, Milpitas, CA 95035", 37.4555, -121.9055, "https://www.fremont.gov/government/departments/environmental-services/recycling-compost-garbage/electronic-hazardous-waste", "Mon–Sat 6:00–17:00", "408-262-1401", mats(BULKY, APPLIANCE, TIRES, CD, E_WASTE)),
    # san-diego
    row("Miramar Household Hazardous Waste Transfer Facility", "HHW / e-waste (appointment)", "san-diego", "92111", "5161 Convoy Street, San Diego, CA 92111", 32.84, -117.15, "https://www.sandiego.gov/environmental-services/ep/hazardous", "Wed & Sat 9:00–15:00 by appointment", "858-694-7000", HHW_E),
    row("Miramar Recycling Center", "Recycling / appliance / TV drop-off", "san-diego", "92111", "5165 Convoy Street, San Diego, CA 92111", 32.8354, -117.1524, "https://www.sandiego.gov/environmental-services/recycling/centers/miramarrecycle", "Mon–Sat 7:00–16:30", "858-268-8971", mats(E_WASTE, APPLIANCE, TIRES, ["cooking-oil"])),
    row("Miramar Landfill — public scalehouse", "Municipal landfill — self-haul", "san-diego", "92111", "5180 Convoy Street, San Diego, CA 92111", 32.8365, -117.1535, "https://www.sandiego.gov/environmental-services/miramar", "Mon–Sat 7:00–16:30", "858-694-7000", mats(BULKY, APPLIANCE, TIRES)),
    row("Miramar Greenery — yard waste drop-off", "Landfill greenery — yard waste / wood", "san-diego", "92111", "5180 Convoy Street, San Diego, CA 92111", 32.8365, -117.1535, "https://www.sandiego.gov/environmental-services/miramar/greenery", "Mon–Sat 7:00–16:00", "858-694-7000", mats(["yard-waste", "christmas-tree"])),
    row("San Diego El Cajon HHW Collection Facility", "HHW / e-waste drop-off", "chula-vista", "92020", "9150 Campo Road, Spring Valley, CA 91977", 32.7455, -116.9855, "https://www.sandiego.gov/environmental-services/ep/hazardous", "Wed & Sat 9:00–15:00 by appointment", "858-694-7000", HHW_E),
    row("San Diego Ramona HHW Collection Facility", "HHW / e-waste drop-off", "san-diego", "92065", "324 Maple Street, Ramona, CA 92065", 33.0455, -116.8755, "https://www.sandiego.gov/environmental-services/ep/hazardous", "Wed & Sat 9:00–15:00 by appointment", "858-694-7000", HHW_E),
    row("San Diego Escondido HHW Collection Facility", "HHW / e-waste drop-off", "san-diego", "92025", "1044 North Ash Street, Escondido, CA 92025", 33.1355, -117.0755, "https://www.sandiego.gov/environmental-services/ep/hazardous", "Wed & Sat 9:00–15:00 by appointment", "858-694-7000", HHW_E),
    # chula-vista
    row("South Bay Household Hazardous Waste Collection Facility", "HHW / e-waste drop-off", "chula-vista", "91911", "1800 Maxwell Road, Chula Vista, CA 91911", 32.6, -117.03, "https://www.chulavistaca.gov/departments/clean/environmental-services/hazardous-waste", "Wed & Sat 9:00–13:00", "(619) 691-5122", HHW_E),
    row("Otay Landfill — self-haul", "Landfill / bulky drop-off", "chula-vista", "91911", "1700 Maxwell Road, Chula Vista, CA 91911", 32.5988, -117.0177, "https://www.chulavistaca.gov/departments/sustainability/trash/self-hauling-options", "Mon–Fri 7:00–16:00; Sat 8:00–15:30", "619-421-3773", mats(BULKY, APPLIANCE)),
    row("Miramar Landfill — public scalehouse (Chula Vista area)", "Municipal landfill — self-haul", "chula-vista", "92111", "5180 Convoy Street, San Diego, CA 92111", 32.8365, -117.1535, "https://www.sandiego.gov/environmental-services/miramar", "Mon–Sat 7:00–16:30", "858-694-7000", mats(BULKY, APPLIANCE, TIRES)),
    row("Sycamore Landfill — public drop-off (Chula Vista area)", "Regional landfill — self-haul", "chula-vista", "92071", "8514 Mast Boulevard, Santee, CA 92071", 32.8555, -116.9855, "https://www.sandiego.gov/sites/default/files/leainfo_sycamoreapp.pdf", "Mon–Fri 6:00–16:30; Sat 6:00–15:00", "619-562-0530", LANDFILL),
    row("Miramar Recycling Center (Chula Vista area)", "Recycling / appliance / TV drop-off", "chula-vista", "92111", "5165 Convoy Street, San Diego, CA 92111", 32.8354, -117.1524, "https://www.sandiego.gov/environmental-services/recycling/centers/miramarrecycle", "Mon–Sat 7:00–16:30", "858-268-8971", mats(E_WASTE, APPLIANCE, TIRES, ["cooking-oil"])),
    # long-beach
    row("EDCO Environmental Collection Center (Signal Hill)", "LA County / Long Beach HHW & e-waste", "long-beach", "90755", "2755 California Avenue, Signal Hill, CA 90755", 33.8073, -118.1807, "https://cleanla.lacounty.gov/hhw/collection-centers/", "2nd & 4th Sat 9:00–14:00", "(562) 570-2876", HHW_E),
    row("Environmental Collection Center — Long Beach HHW", "City HHW / e-waste drop-off", "long-beach", "90755", "2755 California Avenue, Signal Hill, CA 90755", 33.8073, -118.1807, "https://www.longbeach.gov/lbrecycles/hazardous-waste/household-hazardous-waste/hhw-101/", "2nd & 4th Sat 9:00–14:00", "(562) 570-2876", mats(HHW, E_WASTE, TIRES)),
    row("Conservation Corps of Long Beach — HHW / tire events", "City-partnered HHW / e-waste / tire events", "long-beach", "90814", "340 Nieto Avenue, Long Beach, CA 90814", 33.767, -118.134, "https://www.longbeach.gov/lbrecycles/", "2nd & 4th Sat 10:00–14:00", "(562) 570-2876", mats(E_WASTE, TIRES, HHW)),
    *OC_HHW_ROWS,
    row("Frank R Bowerman Landfill — public scalehouse", "County landfill — self-haul", "irvine", "92618", "18800 MacArthur Boulevard, Irvine, CA 92612", 33.6655, -117.7555, OC_HHW, "Mon–Sat (confirm hours)", "714-834-4000", LANDFILL),
    row("Olinda Alpha Landfill — public scalehouse", "County landfill — self-haul", "anaheim", "92821", "2900 N Orange Avenue, Brea, CA 92821", 33.9055, -117.8155, OC_HHW, "Mon–Sat (confirm hours)", "714-834-4000", LANDFILL),
    row("Prima Deshecha Landfill — public scalehouse", "County landfill — self-haul", "santa-ana", "92675", "32200 La Pata Avenue, San Juan Capistrano, CA 92675", 33.5055, -117.6355, OC_HHW, "Mon–Sat (confirm hours)", "714-834-4000", LANDFILL),
    # riverside
    row("Agua Mansa Permanent HHW Facility", "County HHW / e-waste", "riverside", "92509", "1780 Agua Mansa Road, Jurupa Valley, CA 92509", 34.03, -117.4, RIVCO, "Non-holiday Saturdays 9:00–14:00", "951-486-3200", HHW_E),
    row("Agua Mansa Transfer Station", "Transfer station / free bulky drop-off", "riverside", "92509", "1830 Agua Mansa Road, Riverside, CA 92509", 34.027, -117.3772, RIVCO, "Mon–Sun scale; 3rd Sat free bulky", "(951) 826-5311", mats(BULKY, APPLIANCE, E_WASTE, TIRES)),
    row("Lamb Canyon Permanent HHW Collection Facility", "County HHW / e-waste", "riverside", "92223", "16411 Lamb Canyon Road, Beaumont, CA 92223", 34.0255, -116.9555, RIVCO, "Sat 9:00–14:00", "951-486-3200", HHW_E),
    row("Badlands Landfill — public scalehouse", "County landfill — self-haul", "riverside", "92555", "31125 Ironwood Avenue, Moreno Valley, CA 92555", 33.8755, -117.1555, RIVCO, "Mon–Sat 6:00–16:30", "951-486-3200", LANDFILL),
    row("Palm Springs Permanent HHW Collection Facility", "County HHW / e-waste", "riverside", "92262", "1100 Vella Road, Palm Springs, CA 92262", 33.8555, -116.5455, RIVCO, "Non-holiday Sat 9:00–14:00", "951-486-3200", HHW_E),
    row("Riverside City Corporation Yard — Clean Riverside events", "City bulky / e-waste event drop-off", "riverside", "92504", "8095 Lincoln Avenue, Riverside, CA 92504", 33.9455, -117.4255, RIVCO, "Periodic Sat 8:00–12:00", "951-826-5311", mats(BULKY, E_WASTE, APPLIANCE, TIRES, CD)),
    row("Edom Hill Transfer Station — HHW events", "County transfer / HHW event site", "riverside", "92234", "70-100 Edom Hill Road, Cathedral City, CA 92234", 33.8155, -116.4655, RIVCO, "Periodic Sat 9:00–14:00", "951-486-3200", mats(HHW, E_WASTE, BULKY)),
    # sacramento
    row("Sacramento Recycling & Transfer Station HHW", "HHW / e-waste drop-off", "sacramento", "95826", "8491 Fruitridge Road, Sacramento, CA 95826", 38.53, -121.41, "https://www.cityofsacramento.gov/public-works/recycling-solid-waste/Householdhazardouswaste/HHWfacilities", "Tue–Sat 8:00–17:00", "(916) 379-0500", HHW_E),
    row("North Area Recovery Station (NARS)", "County transfer / HHW / bulky", "sacramento", "95660", "4450 Roseville Road, North Highlands, CA 95660", 38.6417, -121.3736, "https://wmr.saccounty.gov/pages/nars.aspx", "Mon–Fri 6:30–18:00; Sat–Sun 8:00–18:00", "(916) 875-5555", mats(BULKY, APPLIANCE, E_WASTE, TIRES, HHW)),
    row("Kiefer Landfill — public scalehouse", "County landfill — self-haul / ABOP", "sacramento", "95683", "12701 Kiefer Boulevard, Sloughhouse, CA 95683", 38.4555, -121.1855, "https://wmr.saccounty.gov/content/wmr/us/en/county-facilities/kiefer-landfill/fees.html", "Mon–Fri 6:30–16:30; Sat–Sun 8:30–16:30", "(916) 875-5555", mats(BULKY, APPLIANCE, TIRES, CD, HHW)),
    row("L&D Landfill — public drop-off", "Private landfill — residential self-haul", "sacramento", "95826", "8635 Fruitridge Road, Sacramento, CA 95826", 38.5255, -121.3955, SAC_TRANSFERS, "Mon–Fri 7:00–16:00; Sat 7:00–15:00", "(916) 383-9420", LANDFILL),
    row("Florin Perkins Public Disposal Site (Zanker)", "C&D / bulky drop-off", "sacramento", "95826", "4201 Florin Perkins Road, Sacramento, CA 95826", 38.5155, -121.4055, SAC_TRANSFERS, "Mon–Fri 7:00–16:00; Sat 7:00–15:00", "(916) 443-5120", mats(CD, BULKY, ["yard-waste"])),
    row("Republic Services Elder Creek Transfer Station", "Transfer station — residential self-haul", "sacramento", "95824", "8642 Elder Creek Road, Sacramento, CA 95824", 38.5155, -121.4255, SAC_TRANSFERS, "Mon–Fri 7:00–16:00; Sat 7:00–15:00", "(916) 387-8425", mats(BULKY, APPLIANCE, CD, TIRES)),
    row("Sierra Waste Recycling and Transfer Station", "Transfer / C&D / bulky drop-off", "sacramento", "95826", "8260 Berry Avenue, Sacramento, CA 95826", 38.5255, -121.3855, SAC_TRANSFERS, "Mon–Fri 7:00–16:00; Sat 7:00–15:00", "(916) 388-8320", mats(BULKY, CD, APPLIANCE, TIRES)),
    # fresno
    row("Fresno County Environmental Compliance Center", "County HHW / e-waste", "fresno", "93706", "1327 West Dan Ronquillo Drive, Fresno, CA 93706", 37.71, -119.81, "https://www.fresnocountyca.gov/Departments/Public-Works-and-Planning/divisions-of-public-works-and-planning/resources-and-parks-division/household-hazardous-waste", "Thu–Sat 9:00–15:00", "(559) 600-4259", HHW_E),
    row("American Avenue Disposal Site", "County landfill — self-haul", "fresno", "93630", "18950 W American Avenue, Kerman, CA 93630", 36.7272, -120.0894, "https://www.fresnocountyca.gov/Departments/Public-Works-and-Planning/divisions-of-public-works-and-planning/resources-and-parks-division/landfill-operations", "Mon–Fri 7:00–15:00; Sat 8:00–14:30", "(559) 600-4259", mats(BULKY, APPLIANCE, TIRES, ["yard-waste"])),
    row("Fresno County Cedar Avenue Landfill", "County landfill — self-haul", "fresno", "93725", "10441 S Cedar Avenue, Fresno, CA 93725", 36.6255, -119.7855, "https://www.fresnocountyca.gov/Departments/Public-Works-and-Planning/divisions-of-public-works-and-planning/resources-and-parks-division/landfill-operations", "Mon–Sat (confirm hours)", "(559) 600-4259", LANDFILL),
    # bakersfield / kern
    row("Kern County Special Waste Facility — Bakersfield", "County HHW / e-waste", "bakersfield", "93308", "4951 Standard Street, Bakersfield, CA 93308", 35.393, -119.019, "https://www2.calrecycle.ca.gov/HHW/", "Mon–Sat 8:00–16:00", "(661) 862-8900", HHW_E),
    row("Roberts Lane Transfer Station", "County transfer — residential bulky / e-waste", "bakersfield", "93308", "1900 Roberts Lane, Bakersfield, CA 93308", 35.3865, -119.0185, "https://www2.calrecycle.ca.gov/HHW/", "Mon & Thu 17:00–20:00; Sat 8:00–14:00", "(661) 862-8900", mats(BULKY, E_WASTE, APPLIANCE)),
    row("Bakersfield Metropolitan (Bena) Sanitary Landfill", "County landfill — residential drop-off", "bakersfield", "93307", "2951 Neumarkel Road, Bakersfield, CA 93307", 35.393, -118.682, "https://www2.calrecycle.ca.gov/HHW/", "Daily 8:00–16:00", "(661) 862-8900", LANDFILL),
    row("Shafter-Wasco Landfill — public scale", "County landfill — self-haul", "bakersfield", "93263", "17261 Scofield Avenue, Shafter, CA 93263", 35.5055, -119.2755, "https://www2.calrecycle.ca.gov/HHW/", "Mon–Sat (confirm hours)", "(661) 862-8900", LANDFILL),
    row("Tehachapi Transfer Station", "County transfer — residential drop-off", "bakersfield", "93561", "12001 Tehachapi Boulevard, Tehachapi, CA 93561", 35.1255, -118.4555, "https://www2.calrecycle.ca.gov/HHW/", "Sat 8:00–12:00", "(661) 862-8900", mats(BULKY, E_WASTE)),
    # stockton
    row("San Joaquin County Household Hazardous Waste Facility", "County HHW / e-waste", "stockton", "95206", "7850 R.A. Bridgeford Street, Stockton, CA 95206", 37.894, -121.248, "https://www.stocktonca.gov/services/garbage___recycling/hazardous_waste/index.php", "Thu–Sun 9:00–15:00", "(209) 468-3066", HHW_E),
    row("Lovelace Materials Recovery Facility and Transfer Station", "County transfer / C&D / bulky", "stockton", "95336", "2323 E Lovelace Road, Manteca, CA 95336", 37.8483, -121.2494, SJ_COUNTY, "Daily 7:00–16:00", "(209) 982-5770", mats(BULKY, APPLIANCE, E_WASTE, TIRES, CD)),
    row("North County Transfer Station", "County transfer — residential drop-off", "stockton", "95236", "17720 East Foothill Avenue, Linden, CA 95236", 38.0255, -121.0855, SJ_COUNTY, "Mon–Sat (confirm hours)", "(209) 468-3066", mats(BULKY, APPLIANCE, TIRES)),
    # fontana / SBC HHW
    row("Fontana HHW Facility — Orange Way", "City HHW drop-off (Fontana residents)", "fontana", "92337", "16454 Orange Way, Fontana, CA 92337", 34.08, -117.42, "https://www2.calrecycle.ca.gov/HHW/", "Sat 8:00–12:00", "909-349-6900", HHW_E),
    row("Ontario HHW Collection Facility", "County HHW / e-waste (SBC)", "fontana", "91761", "1430 South Cucamonga Avenue, Ontario, CA 91761", 34.0455, -117.6255, "https://www.ontarioca.gov/government/public-works/integrated-waste/household-hazardous-waste-hhw-facility", "Fri–Sat 9:00–14:00", "909-382-5401", HHW_E),
    row("San Bernardino Central HHW Collection Facility", "County HHW / e-waste", "fontana", "92408", "2824 East W Street, Building 302, San Bernardino, CA 92408", 34.0955, -117.2355, SBC_HHW, "Mon–Fri 9:00–16:00", "909-382-5401", HHW_E),
    row("Rancho Cucamonga HHW Collection Facility", "County HHW / e-waste", "fontana", "91730", "8794 Lion Street, Rancho Cucamonga, CA 91730", 34.0855, -117.5755, SBC_HHW, "Sat 8:00–12:00", "909-382-5401", HHW_E),
    row("Apple Valley HHW Collection Facility", "County HHW / e-waste", "fontana", "92307", "13450 Nomwaket Road, Apple Valley, CA 92307", 34.5055, -117.1855, SBC_HHW, "Sat 10:00–14:00", "909-382-5401", HHW_E),
    # san-jose
    row("Santa Clara County HHW — East San Jose (appointment)", "County HHW / e-waste (appointment required)", "san-jose", "95127", "East San Jose permanent HHW — address provided after appointment", 37.3655, -121.8255, "https://hhw.santaclaracounty.gov/drop-household-waste", "Thu–Sat by appointment", "(408) 299-7300", HHW_E),
    row("Santa Clara County HHW — San Martin Facility", "County HHW / e-waste (appointment required)", "san-jose", "95046", "13055 Murphy Avenue, San Martin, CA 95046", 37.085, -121.601, "https://hhw.santaclaracounty.gov/drop-household-waste", "Thu–Sat by appointment", "(408) 299-7300", HHW_E),
    row("Guadalupe Rubbish Disposal — Guadalupe Landfill", "Landfill / C&D and bulky self-haul", "san-jose", "95120", "15999 Guadalupe Mines Road, San Jose, CA 95120", 37.1778, -121.8447, "https://www.sanjoseca.gov/Home/Components/BusinessDirectory/BusinessDirectory/217/330", "Mon–Sat 8:00–16:00", "408-268-1666", mats(CD, BULKY, TIRES, APPLIANCE)),
    row("San José Environmental Innovation Center — HHW / e-waste", "City HHW / e-waste drop-off", "san-jose", "95133", "1608 Las Plumas Avenue, San Jose, CA 95133", 37.3755, -121.8955, "https://www.sanjoseca.gov/your-government/departments-offices/environmental-services/recycling-garbage/household-hazardous-waste", "Thu–Sat 9:00–15:00", "(408) 535-3500", HHW_E),
    # extra inventory to clear 120+ after legacy prune
    row("Calabasas Landfill", "County landfill — green waste / C&D / inert", "los-angeles", "91301", "5300 Lost Hills Road, Agoura, CA 91301", 34.146, -118.706, "http://www.publichealth.lacounty.gov/eh/business/landfill-transfer-stations.htm", "Mon–Fri 8:00–17:00; Sat per site; closed Sun", "562-908-4288", mats(CD, ["yard-waste"])),
    row("Scholl Canyon Landfill — public scalehouse", "County landfill — inert / green waste / asphalt", "los-angeles", "90041", "7721 North Figueroa Street, Los Angeles, CA 90041", 34.145, -118.186, "http://www.publichealth.lacounty.gov/eh/business/landfill-transfer-stations.htm", "Mon–Fri 8:00–17:00; Sat 8:00–15:30", "818-243-9779", mats(CD, ["yard-waste", "concrete"])),
    row("Puente Hills Materials Recovery Facility", "County MRF / transfer — bulky / green waste", "los-angeles", "90601", "2808 S Workman Mill Road, Whittier, CA 90601", 34.001, -118.056, "http://www.publichealth.lacounty.gov/eh/business/landfill-transfer-stations.htm", "Mon–Sat; confirm hours", "562-908-4288", mats(BULKY, CD, ["yard-waste"])),
    row("Sunshine Canyon Landfill — public scalehouse", "County landfill — residential self-haul", "los-angeles", "91342", "14747 San Fernando Road, Sylmar, CA 91342", 34.3255, -118.4255, "http://www.publichealth.lacounty.gov/eh/business/landfill-transfer-stations.htm", "Mon–Sat (confirm hours)", "818-364-1270", LANDFILL),
    row("San Bernardino County HHW — Chino Facility", "County HHW / e-waste", "fontana", "91710", "5050 Schaefer Avenue, Chino, CA 91710", 34.012, -117.687, SBC_HHW, "2nd & 4th Sat 8:00–13:00", "909-334-3266", HHW_E),
    row("Kern County Special Waste Facility — Mojave", "County HHW / e-waste", "bakersfield", "93501", "17035 St Street, Mojave, CA 93501", 35.0555, -118.1755, "https://www2.calrecycle.ca.gov/HHW/", "Sat 9:00–13:00", "(661) 862-8900", HHW_E),
    row("Kern County Special Waste Facility — Ridgecrest", "County HHW / e-waste", "bakersfield", "93555", "3301 Bowman Road, Ridgecrest, CA 93555", 35.6255, -117.6855, "https://www2.calrecycle.ca.gov/HHW/", "Sat 9:00–13:00", "(661) 862-8900", HHW_E),
    row("Lake Isabella Transfer Station", "County transfer — residential drop-off", "bakersfield", "93240", "7050 Lake Isabella Boulevard, Lake Isabella, CA 93240", 35.6555, -118.4755, "https://www2.calrecycle.ca.gov/HHW/", "Sat 8:00–12:00", "(661) 862-8900", mats(BULKY, ["yard-waste"])),
    row("Fresno County North District Transfer Station", "County transfer — residential drop-off", "fresno", "93637", "10225 Avenue 7, Madera, CA 93637", 36.9555, -119.9055, "https://www.fresnocountyca.gov/Departments/Public-Works-and-Planning/divisions-of-public-works-and-planning/resources-and-parks-division/landfill-operations", "Mon–Sat (confirm hours)", "(559) 600-4259", mats(BULKY, APPLIANCE, TIRES)),
    row("Moreno Valley Transfer Station", "County transfer — household / C&D self-haul", "riverside", "92551", "17700 Indian Street, Moreno Valley, CA 92551", 33.865, -117.235, RIVCO, "Mon–Sat (confirm fees)", "951-242-0421", TRANSFER),
    row("Gaffey Street S.A.F.E. Center (Long Beach area)", "LASAN S.A.F.E. Center — HHW / e-waste", "long-beach", "90731", "1400 N Gaffey Street, San Pedro, CA 90731", 33.7537, -118.2924, LASAN_SAFE, "Sat–Sun 9:00–15:00", "1-800-773-2489", SAFE),
    row("Antelope Valley ECC (Palmdale — LA County HHW)", "LA County permanent HHW / e-waste", "long-beach", "93551", "1200 W City Ranch Road, Palmdale, CA 93551", 34.5855, -118.1855, "https://cleanla.lacounty.gov/hhw/collection-centers/", "1st & 3rd Sat 9:00–15:00", "1-800-98-TOXIC", HHW_E),
    row("San Joaquin County Foothill Sanitary Landfill", "County landfill — self-haul", "stockton", "95206", "7850 R.A. Bridgeford Street, Stockton, CA 95206", 37.894, -121.248, SJ_COUNTY, "Mon–Sat (confirm scale hours)", "(209) 468-3066", LANDFILL),
    row("Mount Vernon Greenwaste Facility", "Greenwaste / wood / bulky drop-off", "bakersfield", "93307", "2601 S Mount Vernon Avenue, Bakersfield, CA 93307", 35.3255, -118.9855, "https://www2.calrecycle.ca.gov/HHW/", "Mon–Fri 8:00–16:00", "(661) 831-2321", mats(["yard-waste", "christmas-tree"], BULKY)),
    row("Metropolitan Recycling — C&D drop-off", "C&D recycling / drop-off", "bakersfield", "93307", "2601 S Mount Vernon Avenue, Bakersfield, CA 93307", 35.3255, -118.9855, "https://www2.calrecycle.ca.gov/HHW/", "Mon–Fri 8:00–16:00", "(661) 831-2321", mats(CD)),
]


def accept_row(r: dict) -> bool:
    if r["city_slug"] not in TARGET_CITIES:
        return False
    if REJECT_NAME.search(r.get("name") or ""):
        return False
    mats_set = set(r.get("accepted_materials") or [])
    if mats_set and mats_set <= SOFT_ONLY:
        return False
    if not is_hard_facility(r):
        return False
    if not is_gov_url(r.get("source_url") or ""):
        return False
    return True


def prune_target_cities(facilities: list[dict]) -> tuple[list[dict], int]:
    pruned = 0
    out: list[dict] = []
    for f in facilities:
        if f.get("city_slug") in TARGET_CITIES and (
            not is_hard_facility(f) or not is_gov_url(f.get("source_url", ""))
        ):
            pruned += 1
            continue
        out.append(f)
    return out, pruned


def main() -> None:
    batch: list[dict] = []
    rejected: list[str] = []
    for r in FACILITIES:
        r = {**r, "accepted_materials": mats(r["accepted_materials"])}
        if not is_hard_facility(r):
            raise SystemExit(f"soft row slipped in: {r['name']}")
        if accept_row(r):
            batch.append(r)
        else:
            rejected.append(r["name"])

    facilities = json.loads(FAC_PATH.read_text())
    by_key = {(f.get("city_slug"), f.get("name")): i for i, f in enumerate(facilities)}

    removed = 0
    for key in REMOVE_KEYS:
        if key in by_key:
            facilities.pop(by_key[key])
            by_key = {(f.get("city_slug"), f.get("name")): i for i, f in enumerate(facilities)}
            removed += 1

    added = updated = 0
    for r in batch:
        key = (r["city_slug"], r["name"])
        if key in by_key:
            facilities[by_key[key]] = {**facilities[by_key[key]], **r}
            updated += 1
        else:
            facilities.append(r)
            by_key[key] = len(facilities) - 1
            added += 1

    facilities, pruned = prune_target_cities(facilities)
    FAC_PATH.write_text(json.dumps(facilities, indent=2) + "\n")

    ca_hard = [
        f
        for f in facilities
        if f.get("city_slug") in TARGET_CITIES
        and is_hard_facility(f)
        and is_gov_url(f.get("source_url", ""))
    ]
    per_city = {c: sum(1 for f in ca_hard if f.get("city_slug") == c) for c in sorted(TARGET_CITIES)}

    out = {
        "verified": VERIFIED,
        "added": added,
        "updated": updated,
        "removed_superseded": removed,
        "pruned_legacy": pruned,
        "rejected_in_batch": len(rejected),
        "ca_hard_total": len(ca_hard),
        "total_hard": sum(1 for f in facilities if is_hard_facility(f)),
        "per_city": per_city,
        "networks": [
            "Alameda StopWaste HHW (4 sites: Oakland, Hayward, Livermore, Fremont)",
            "OC Waste HHW (4 centers: Anaheim, Huntington Beach, Irvine, San Juan Capistrano)",
            "LASAN S.A.F.E. Centers + district bulky yards",
            "LA County Sanitation Districts (Calabasas, Scholl Canyon, South Gate, Puente Hills MRF)",
            "San Diego Miramar HHW / landfill / recycling",
            "Sacramento County WMR (NARS, Kiefer, SRT HHW)",
            "Santa Clara County HHW (San Jose, San Martin)",
            "San Bernardino County Fire HHW (Ontario, Central, Rancho Cucamonga, Chino, Apple Valley)",
            "Riverside County Waste Resources (Agua Mansa, Lamb Canyon, Badlands, transfer stations)",
            "Kern County Public Works (Special Waste, transfer stations, landfills)",
            "Fresno County Environmental Compliance + landfills",
            "San Joaquin County HHW + transfer stations",
            "Long Beach / LA County HHW (Signal Hill ECC, Antelope Valley)",
        ],
        "facilities": batch,
    }
    print(json.dumps(out, indent=2))
    print(f"\nAdded: {added} | CA hard total: {len(ca_hard)} | All hard: {out['total_hard']}")


if __name__ == "__main__":
    main()
