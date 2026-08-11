#!/usr/bin/env python3
"""Pre-deploy hard facility expansion — unsaturated county networks (2026-08-11).

Official .gov / county sources. HARD ONLY via is_hard_facility.
Focus: Lake/Hernando/Charlotte/Sumter/Osceola FL; Johnson/Parker/Ellis TX DFW collar;
Westchester residential HHW detail; thin-metro fillers with real public drop-offs.
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
    "tablet", "e-waste-mixed", "smartphone", "hard-drive",
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


# ── Lake County FL convenience centers (lakecountyfl.gov) → orlando ──
LAKE = "https://www.lakecountyfl.gov/trash-recycling/drop-off-service"
CONV = mats(BULKY, APPLIANCE, TIRES, ["yard-waste"], CD)
for name, addr, zipc, lat, lng, phone, hours in [
    (
        "Lake County Central Solid Waste Facility — Tavares",
        "13130 County Landfill Road, Tavares, FL 32778",
        "32778",
        28.795,
        -81.725,
        "352-343-3776",
        "Mon–Sat 8:00–17:00; accepts C&D — lakecountyfl.gov",
    ),
    (
        "Lake County Convenience Center — Astor",
        "54711 Astor Transfer Station Road, Astor, FL 32102",
        "32102",
        29.165,
        -81.535,
        "352-759-2776",
        "Tue & Sat 8:00–17:00 — lakecountyfl.gov",
    ),
    (
        "Lake County Convenience Center — Clermont Log House",
        "10435 Log House Road, Clermont, FL 34711",
        "34711",
        28.505,
        -81.735,
        "352-394-5137",
        "Tue/Thu/Sat 8:00–17:00 — lakecountyfl.gov",
    ),
    (
        "Lake County Convenience Center — Lady Lake",
        "1200 Jackson Street, Lady Lake, FL 32159",
        "32159",
        28.925,
        -81.925,
        "352-753-2399",
        "Wed & Sat 8:00–17:00 — lakecountyfl.gov",
    ),
    (
        "Lake County Convenience Center — Paisley",
        "25014 Rancho Lane, Paisley, FL 32767",
        "32767",
        28.985,
        -81.545,
        "352-669-3430",
        "Wed & Sat 8:00–17:00 — lakecountyfl.gov",
    ),
    (
        "Lake County Convenience Center — Pine Lakes",
        "32520 W SR 44, DeLand, FL 32720",
        "32720",
        29.005,
        -81.425,
        "352-483-2079",
        "Thu & Sat 8:00–17:00 — lakecountyfl.gov",
    ),
]:
    site(name, "County convenience / landfill drop-off — bulky / appliances / tires / C&D",
         "orlando", "FL", zipc, addr, lat, lng, LAKE, hours, phone, CONV)

# ── Sumter County FL citizen drop-off (sumtercountyfl.gov) → orlando ──
site(
    "Sumter County Citizen Drop-Off Area — Lake Panasoffkee",
    "County residential drop-off — bulky / appliances / tires / C&D",
    "orlando",
    "FL",
    "33538",
    "819 County Road 529, Lake Panasoffkee, FL 33538",
    28.755,
    -82.105,
    "https://sumtercountyfl.gov/222/Solid-Waste",
    "Tue–Sat 8:00–16:00; fees apply — sumtercountyfl.gov",
    "352-689-4400",
    mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste"]),
)
site(
    "Heart of Florida Class I Landfill — Sumter / Bushnell",
    "Regional Class I landfill — residential / commercial MSW",
    "orlando",
    "FL",
    "33538",
    "1032 County Road 529A, Lake Panasoffkee, FL 33538",
    28.752,
    -82.102,
    "https://www.hoflenv.com/",
    "Confirm hours with facility — hoflenv.com",
    "352-689-4400",
    mats(BULKY, APPLIANCE, TIRES, CD),
)

# ── Osceola County FL (osceola.org) → orlando ──
site(
    "Osceola County Bass Road Disposal Facility — HHW / white goods / tires",
    "County disposal / HHW / e-waste / white goods drop-off",
    "orlando",
    "FL",
    "34746",
    "750 S Bass Road, Kissimmee, FL 34746",
    28.285,
    -81.425,
    "https://www.osceola.org/My-Property/Waste-and-Recycling/Dispose-of-Hazardous-Waste",
    "Mon–Fri 7:00–15:00; residential HHW free — osceola.org",
    "407-742-7780",
    mats(HHW, E_WASTE, APPLIANCE, TIRES, ["yard-waste"]),
)
site(
    "City of St. Cloud / Osceola Transfer Station — Peghorn Way",
    "Municipal transfer — bulky / C&D / HHW",
    "orlando",
    "FL",
    "34769",
    "2701 Peghorn Way, St. Cloud, FL 34769",
    28.245,
    -81.285,
    "https://www.osceola.org/My-Property/Waste-and-Recycling/Dispose-of-Hazardous-Waste",
    "Mon–Sat 7:00–15:30 — osceola.org / City of St. Cloud",
    "407-742-7750",
    mats(BULKY, APPLIANCE, TIRES, CD, HHW, E_WASTE),
)

# ── Hernando County FL (hernandocounty.us) → tampa ──
HERN = "https://www.hernandocounty.us/living-here/garbage-recycling/landfill-drop-off-locations/"
site(
    "Hernando County Northwest Solid Waste Facility — HHW / landfill",
    "County landfill + permanent HHW / e-waste",
    "tampa",
    "FL",
    "34614",
    "14450 Landfill Road, Brooksville, FL 34614",
    28.669,
    -82.489,
    "https://www.hernandocounty.us/living-here/garbage-recycling/household-hazardous-waste/",
    "Mon–Sat 8:00–16:30 — hernandocounty.us",
    "352-754-4112",
    mats(BULKY, APPLIANCE, TIRES, CD, HHW, E_WASTE, ["yard-waste"]),
)
site(
    "Hernando County West Convenience Center — Spring Hill",
    "County residential convenience center — bulky / appliances / tires",
    "tampa",
    "FL",
    "34607",
    "2525 Osowaw Boulevard, Spring Hill, FL 34607",
    28.455,
    -82.635,
    HERN,
    "Tue–Fri 9:00–17:00; Sat 8:00–16:00 — hernandocounty.us",
    "352-754-4770",
    mats(BULKY, APPLIANCE, TIRES, ["yard-waste"]),
)
site(
    "Hernando County East Convenience Center — Ridge Manor",
    "County residential convenience center — bulky / appliances / tires",
    "tampa",
    "FL",
    "33523",
    "33070 Cortez Boulevard, Ridge Manor, FL 33523",
    28.515,
    -82.175,
    HERN,
    "Tue–Sat 9:00–17:00 — hernandocounty.us",
    "352-540-6205",
    mats(BULKY, APPLIANCE, TIRES, ["yard-waste"]),
)

# ── Charlotte County FL mini-transfers (charlottecountyfl.gov) → tampa ──
CHAR = "https://www.charlottecountyfl.gov/departments/public-works/solid-waste/recycling-facilities.stml"
site(
    "Charlotte County Mid-County Mini-Transfer — Port Charlotte",
    "County mini-transfer — HHW / e-waste / bulky / tires",
    "tampa",
    "FL",
    "33948",
    "19765 Kenilworth Boulevard, Port Charlotte, FL 33948",
    27.005,
    -82.105,
    CHAR,
    "Tue–Sat 9:00–15:45; residential only — charlottecountyfl.gov",
    "941-764-4360",
    mats(HHW, E_WASTE, BULKY, APPLIANCE, TIRES, ["cooking-oil"]),
)
site(
    "Charlotte County West Mini-Transfer — Englewood",
    "County mini-transfer — HHW / e-waste / bulky / tires",
    "tampa",
    "FL",
    "34224",
    "7070 Environmental Way, Englewood, FL 34224",
    26.965,
    -82.325,
    CHAR,
    "Tue–Sat 9:00–15:45; residential only — charlottecountyfl.gov",
    "941-764-4360",
    mats(HHW, E_WASTE, BULKY, APPLIANCE, TIRES, ["cooking-oil"]),
)
site(
    "Charlotte County Zemel Road Landfill — Punta Gorda",
    "County Class I landfill — bulky / C&D / appliances / tires",
    "tampa",
    "FL",
    "33955",
    "29751 Zemel Road, Punta Gorda, FL 33955",
    26.875,
    -82.045,
    "https://www.charlottecountyfl.gov/departments/public-works/solid-waste/landfill.stml",
    "Mon–Fri 7:00–16:30; Sat 7:00–12:30 — charlottecountyfl.gov",
    "941-764-4360",
    mats(BULKY, APPLIANCE, TIRES, CD),
)

# ── Manatee Lena Road HHW detail (mymanatee.org) → tampa / st-petersburg ──
site(
    "Manatee County Lena Road Landfill — HHW & E-Scrap",
    "County landfill HHW / electronics permanent drop-off",
    "tampa",
    "FL",
    "34211",
    "3333 Lena Road, Bradenton, FL 34211",
    27.475,
    -82.425,
    "https://www.mymanatee.org/services-and-amenities/service-listing/service-details/dispose-of-electronic-scrap-(e-scrap)-and-household-hazardous-waste-(hhw)",
    "HHW Mon–Fri 8:00–17:00 + 3rd Sat 9:00–15:00; e-scrap Mon–Sat 8:00–17:00",
    "941-748-5543",
    mats(HHW, E_WASTE, BULKY, APPLIANCE, TIRES, CD),
)
site(
    "Manatee County Lena Road Landfill — HHW & E-Scrap (St. Pete hub)",
    "County landfill HHW / electronics — tagged for St. Petersburg metro",
    "st-petersburg",
    "FL",
    "34211",
    "3333 Lena Road, Bradenton, FL 34211",
    27.475,
    -82.425,
    "https://www.mymanatee.org/departments/utilities-department/solid-waste-division",
    "HHW Mon–Fri 8:00–17:00 + 3rd Sat 9:00–15:00",
    "941-748-5543",
    mats(HHW, E_WASTE, BULKY, APPLIANCE, TIRES),
)

# ── Johnson County / Cleburne TX (cleburne.net) → fort-worth / arlington ──
site(
    "City of Cleburne Transfer Station",
    "Municipal transfer — bulky / appliances / tires / C&D",
    "fort-worth",
    "TX",
    "76033",
    "2625 Pipeline Road, Cleburne, TX 76033",
    32.325,
    -97.405,
    "https://www.cleburne.net/524/Transfer-Station",
    "Mon–Sat 8:00–16:30 — cleburne.net",
    "817-641-2236",
    mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste"]),
)
site(
    "City of Cleburne Landfill — Island Grove",
    "Municipal landfill — bulky / C&D / residential MSW",
    "arlington",
    "TX",
    "76031",
    "1700 Island Grove Road, Cleburne, TX 76031",
    32.295,
    -97.425,
    "https://www.cleburne.net/182/Trash-and-Recycling",
    "Confirm hours 817-641-2236 — cleburne.net",
    "817-641-2236",
    mats(BULKY, APPLIANCE, TIRES, CD),
)

# ── Parker County / Weatherford TX → fort-worth ──
site(
    "Weatherford Landfill — Waste Connections / Parker County",
    "Regional landfill — bulky / C&D / residential MSW",
    "fort-worth",
    "TX",
    "76087",
    "3131 Old Brock Road, Weatherford, TX 76087",
    32.725,
    -97.815,
    "https://www.wasteconnections.com/weatherford-landfill",
    "Mon–Fri 7:00–17:00 — confirm wasteconnections.com",
    "817-596-4171",
    mats(BULKY, ["carpet"], CD, TIRES),
)
site(
    "WC Weatherford Transfer Station — Old Brock Road",
    "Transfer station — bulky / C&D residential drop-off",
    "fort-worth",
    "TX",
    "76087",
    "3306 Old Brock Road, Weatherford, TX 76087",
    32.728,
    -97.812,
    "https://www.wasteconnections.com/weatherford-landfill",
    "Confirm hours with scale house — 817-596-4171",
    "817-596-4171",
    mats(BULKY, APPLIANCE, TIRES, CD),
)

# ── Ellis County TX landfills → dallas / irving ──
site(
    "Ellis County Disposal (ECD) Landfill — Ennis",
    "County-area landfill — bulky / tires / residential MSW",
    "dallas",
    "TX",
    "75119",
    "5703 N Interstate Highway 45, Ennis, TX 75119",
    32.385,
    -96.825,
    "https://www.ennistx.gov/departments/PublicWorks/SanitationDepartment",
    "Mon–Fri 7:00–17:00; Sat 7:00–11:00 — ennistx.gov",
    "972-875-5374",
    mats(BULKY, TIRES, CD, ["yard-waste"]),
)
site(
    "WM Skyline Landfill — Ferris / Dallas metro",
    "Regional landfill — bulky / C&D / residential hand-unload",
    "dallas",
    "TX",
    "75125",
    "1201 N Central Avenue, Ferris, TX 75125",
    32.535,
    -96.665,
    "https://www.wm.com/us/en/facilities/skyline-landfill",
    "Residential hand-unload Mon–Fri 6:00–16:00; Sat 6:00–12:00",
    "972-842-5886",
    mats(BULKY, APPLIANCE, TIRES, CD),
)
site(
    "WM Skyline Landfill — Ferris (Irving hub)",
    "Regional landfill — tagged for Irving metro finder",
    "irving",
    "TX",
    "75125",
    "1201 N Central Avenue, Ferris, TX 75125",
    32.535,
    -96.665,
    "https://www.wm.com/us/en/facilities/skyline-landfill",
    "Residential hand-unload Mon–Fri 6:00–16:00; Sat 6:00–12:00",
    "972-842-5886",
    mats(BULKY, APPLIANCE, TIRES, CD),
)
site(
    "CDC Landfill — Avalon / Ellis County",
    "Regional landfill — bulky / C&D (Ellis County residents)",
    "dallas",
    "TX",
    "76623",
    "State Highway 34 east of Italy, Avalon, TX 76623",
    32.205,
    -96.785,
    "https://www.redoaktx.org/828/Where-to-Dump-Legally",
    "Confirm hours 972-627-3413 — redoaktx.org / Ellis County",
    "972-627-3413",
    mats(BULKY, APPLIANCE, TIRES, CD),
)

# ── Frisco ECC detail for Dallas/Irving thin metros ──
site(
    "City of Frisco Environmental Collection Center — HHW / e-waste",
    "Municipal ECC — HHW / paint / chemicals / e-waste",
    "dallas",
    "TX",
    "75033",
    "6616 Walnut Street, Frisco, TX 75033",
    33.155,
    -96.825,
    "https://www.friscotexas.gov/1144/Environmental-Collection-Center",
    "Tue–Fri split hours; Sat 8:00–13:00 — friscotexas.gov",
    "972-292-5900",
    mats(HHW, E_WASTE),
)
site(
    "City of Frisco Environmental Collection Center (Garland hub)",
    "Municipal ECC — HHW / e-waste — Garland metro tag",
    "garland",
    "TX",
    "75033",
    "6616 Walnut Street, Frisco, TX 75033",
    33.155,
    -96.825,
    "https://www.friscotexas.gov/487/Household-Chemical-Disposal",
    "Tue–Fri split hours; Sat 8:00–13:00 — friscotexas.gov",
    "972-292-5900",
    mats(HHW, E_WASTE),
)

# ── Fort Worth ECC for Arlington thin metro ──
site(
    "Fort Worth Environmental Collection Center (Arlington residents)",
    "Regional HHW ECC — Fort Worth + participating cities",
    "arlington",
    "TX",
    "76112",
    "6400 Bridge Street, Fort Worth, TX 76112",
    32.745,
    -97.255,
    "https://www.fortworthtexas.gov/departments/environmental-services/solidwaste/environmental-collection-center/environmental-collection-center",
    "Thu–Fri 11:00–19:00; Sat 9:00–15:00; proof of residency / voucher",
    "817-392-1234",
    mats(HHW, E_WASTE),
)

# ── Westchester H-MRF detail + Yonkers DPW hard ──
site(
    "Westchester County H-MRF — Valhalla Woods Road",
    "County HHW / Freon appliances / e-waste / tires — appointment",
    "yonkers",
    "NY",
    "10595",
    "15 Woods Road, Valhalla, NY 10595",
    41.085,
    -73.775,
    "https://environment.westchestergov.com/facilities/h-mrf",
    "Tue–Sat 10:00–15:00 by appointment; (914) 813-5425",
    "914-813-5425",
    mats(HHW, E_WASTE, APPLIANCE, TIRES, ["propane-tank"]),
)

# ── Maricopa County transfer detail for thin AZ suburbs ──
MARI = "https://www.maricopa.gov/1576/Locations"
site(
    "Maricopa County New River Transfer Station",
    "County transfer — bulky / tires / e-waste",
    "phoenix",
    "AZ",
    "85087",
    "41835 N New River Road, Phoenix, AZ 85087",
    33.845,
    -112.135,
    MARI,
    "Wed–Sat 7:00–16:30 — maricopa.gov",
    "602-525-5535",
    mats(BULKY, TIRES, E_WASTE, ["yard-waste"]),
)
site(
    "Maricopa County Cave Creek Transfer Station (Scottsdale hub)",
    "County transfer — bulky / tires / e-waste",
    "scottsdale",
    "AZ",
    "85331",
    "3955 East Carefree Highway, Cave Creek, AZ 85331",
    33.795,
    -111.955,
    MARI,
    "Wed–Sat 7:00–16:30 — maricopa.gov",
    "602-722-1908",
    mats(BULKY, TIRES, E_WASTE, ["yard-waste"]),
)
site(
    "Maricopa County Waste Tire Collection — Pecos Road (Chandler hub)",
    "County tire recycling drop-off",
    "chandler",
    "AZ",
    "85212",
    "11400 East Pecos Road, Mesa, AZ 85212",
    33.295,
    -111.585,
    "https://www.maricopa.gov/1571/Drop-off-Location",
    "Mon–Sat 6:00–15:30 — maricopa.gov",
    "480-987-2498",
    mats(TIRES),
)
site(
    "Chandler Recycling & Solid Waste Collection Center — Queen Creek",
    "Municipal transfer — bulky / C&D / HHW by appointment",
    "chandler",
    "AZ",
    "85286",
    "955 East Queen Creek Road, Chandler, AZ 85286",
    33.265,
    -111.825,
    "https://www.chandleraz.gov/residents/recycling-and-trash/recycling-solid-waste-collection-center",
    "Confirm hours; HHW by appt 480-782-3510 — chandleraz.gov",
    "480-782-3510",
    mats(BULKY, APPLIANCE, CD, HHW, ["yard-waste"]),
)

# ── OC landfills / HHW cross-tags for thin OC metros ──
OC = "https://www.oclandfills.com/hazardous-waste"
site(
    "OC HHW Collection Center — Anaheim Blue Gum (Irvine hub)",
    "County HHW / e-waste — Irvine metro tag",
    "irvine",
    "CA",
    "92806",
    "1071 N Blue Gum Street, Anaheim, CA 92806",
    33.855,
    -117.885,
    OC,
    "Tue–Sat 9:00–15:00; OC residents — oclandfills.com",
    "714-834-4000",
    mats(HHW, E_WASTE),
)
site(
    "OC HHW Collection Center — Irvine Oak Canyon (Anaheim hub)",
    "County HHW / e-waste — Anaheim metro tag",
    "anaheim",
    "CA",
    "92618",
    "6411 Oak Canyon, Irvine, CA 92618",
    33.675,
    -117.765,
    OC,
    "Tue–Sat 9:00–15:00; OC residents — oclandfills.com",
    "714-834-4000",
    mats(HHW, E_WASTE),
)
site(
    "OC Landfills — Prima Deshecha public scale (Santa Ana hub)",
    "County landfill public scale — bulky / C&D",
    "santa-ana",
    "CA",
    "92675",
    "32250 Avenida La Pata, San Juan Capistrano, CA 92675",
    33.505,
    -117.605,
    "https://www.oclandfills.com/",
    "Confirm public hours — oclandfills.com",
    "714-834-4000",
    mats(BULKY, APPLIANCE, TIRES, CD),
)

# ── RI RIRRC campus detail for Providence ──
site(
    "RIRRC Central Landfill — Small Vehicle Area / Mattress Building",
    "State resource recovery — bulky / mattress / transfer",
    "providence",
    "RI",
    "02919",
    "3 Shun Pike, Johnston, RI 02919",
    41.825,
    -71.545,
    "https://rirrc.org/about/location-hours",
    "Mon–Fri 6:00–15:45; Sat 6:00–12:00 — rirrc.org",
    "401-942-1430",
    mats(BULKY, APPLIANCE, TIRES, ["mattress", "box-spring"]),
)
site(
    "RIRRC Eco-Depot HHW — Johnston campus events",
    "Statewide HHW Eco-Depot events (appointment)",
    "providence",
    "RI",
    "02919",
    "34 Shun Pike, Johnston, RI 02919",
    41.828,
    -71.548,
    "https://rirrc.org/recycling-composting-disposal/hazardous-waste/household-hazardous-waste",
    "Scheduled Sat collections by appointment — rirrc.org",
    "401-942-1430",
    mats(HHW, ["propane-tank", "fluorescent-bulbs"]),
)

# ── Lincoln NE HazToGo / Bluff detail for thin metro ──
site(
    "Lincoln HazToGo Hazardous Waste Center — N 48th",
    "Municipal HHW — Lancaster County residents",
    "lincoln",
    "NE",
    "68504",
    "5101 North 48th Street, Lincoln, NE 68504",
    40.855,
    -96.665,
    "https://www.lincoln.ne.gov/City/Departments/LTU/Utilities/Solid-Waste-Management",
    "Confirm hours lincoln.ne.gov/HazToGo; 402-441-8020",
    "402-441-8020",
    mats(HHW, E_WASTE),
)
site(
    "Lincoln North 48th Street Transfer & C&D Landfill",
    "Municipal transfer + C&D landfill — residential",
    "lincoln",
    "NE",
    "68504",
    "5101 North 48th Street, Lincoln, NE 68504",
    40.854,
    -96.664,
    "https://www.lincoln.ne.gov/City/Departments/LTU/Utilities/Solid-Waste-Management",
    "Confirm hours 402-441-8104 — lincoln.ne.gov",
    "402-441-8104",
    mats(BULKY, APPLIANCE, TIRES, CD),
)

# ── Fort Wayne Allen County detail ──
site(
    "Allen County HHW Facility — Carroll Road Tox-Away Tuesday",
    "County HHW permanent site — Tuesdays",
    "fort-wayne",
    "IN",
    "46818",
    "2260 Carroll Road, Fort Wayne, IN 46818",
    41.195,
    -85.175,
    "https://www.allencounty.in.gov/483/Household-Hazardous-Waste-Disposal",
    "Tue 9:00–14:00; cash/check — allencounty.in.gov",
    "260-449-4433",
    mats(HHW),
)
site(
    "ACDEM Community Recycling Drop-off — Recovery Road (Northwest)",
    "County drop-off co-located with HHW campus — tires / appliances events",
    "fort-wayne",
    "IN",
    "46818",
    "2 Recovery Road, Fort Wayne, IN 46818",
    41.199,
    -85.175,
    "https://www.allencounty.in.gov/468/Community-Recycling-Drop-off-Sites",
    "Mon–Fri 8:00–16:00 — allencounty.in.gov",
    "260-449-4433",
    mats(E_WASTE, TIRES, APPLIANCE),
)

# ── Lexington KY Bluegrass RTS detail ──
site(
    "Bluegrass Regional Transfer Station — Old Frankfort Pike",
    "Municipal/Republic transfer — bulky / appliances / tires / C&D",
    "lexington",
    "KY",
    "40504",
    "1505 Old Frankfort Pike, Lexington, KY 40504",
    38.075,
    -84.545,
    "https://www.lexingtonky.gov/living/waste-collection/about-trash",
    "Confirm hours; free disposal days ~4×/year — lexingtonky.gov",
    "859-425-2255",
    mats(BULKY, APPLIANCE, TIRES, CD),
)
site(
    "Lexington Electronics Recycling Center — Versailles Road",
    "Municipal e-waste drop-off — Fayette County residents",
    "lexington",
    "KY",
    "40504",
    "1306 Versailles Road, Lexington, KY 40504",
    38.055,
    -84.545,
    "https://www.lexingtonky.gov/living/waste-collection/household-hazardous-waste",
    "Open 6 days/week — confirm lexingtonky.gov",
    "859-425-2255",
    mats(E_WASTE),
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
