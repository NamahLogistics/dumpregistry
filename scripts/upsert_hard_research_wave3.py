#!/usr/bin/env python3
"""Detailed-research hard facility wave 3 (2026-08-12).

Verified official sources for thin spine metros:
- Maricopa / Phoenix transfer network → scottsdale (maricopa.gov, phoenix.gov)
- Miami-Dade TRCs → hialeah (miamidade.gov)
- Metro Waste Authority → des-moines (mwatoday.com / .gov cross-refs)
- Forsyth / Stokes / Davie → winston-salem (cityofws.org, county .gov)
- Allen County National Serv-All + NISWMD Ashley → fort-wayne
- Westchester H-MRF enrichment + municipal e-waste pods → yonkers
- BASWA Beatrice landfill → lincoln (beatrice.ne.gov)
- Louisville Haz Bin / Waste Reduction Center enrichment (louisvilleky.gov)
- Shelby County HHW / Liberty Tire → memphis (shelbycountytn.gov)

Also purges known mistags from prior FL/TX merge.
HARD ONLY. No prod deploy.
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
CITIES_PATH = ROOT / "data" / "geo" / "cities.json"

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


TRANSFER = mats(BULKY, APPLIANCE, TIRES, CD, E_WASTE)
LANDFILL = mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste"])
HHW_E = mats(HHW, E_WASTE)
HHW_ONLY = mats(HHW)
TIRES_ONLY = mats(TIRES)
E_ONLY = mats(E_WASTE)

# ── Scottsdale / Phoenix hard network ──
PHX_TS = "https://www.phoenix.gov/administration/departments/publicworks/about-us/transfer-stations.html"
MARI = "https://www.maricopa.gov/1576/Locations"
MARI_ITEMS = "https://www.maricopa.gov/3366/Accepted-Items-Fees"
MARI_TIRE = "https://www.maricopa.gov/1571/Drop-off-Location"

site(
    "Phoenix North Gateway Transfer Station (Scottsdale hub)",
    "Municipal transfer — appliances / TVs / tires / bulky",
    "scottsdale", "AZ", "85085",
    "30205 N Black Canyon Highway, Phoenix, AZ 85085",
    33.759, -112.116, PHX_TS,
    "Mon–Fri 5:30–17:00; Sat 6:00–15:00 — phoenix.gov",
    "602-262-7251", TRANSFER,
)
site(
    "Phoenix 27th Avenue Transfer Station (Scottsdale hub)",
    "Municipal transfer — appliances / TVs / tires / bulky",
    "scottsdale", "AZ", "85009",
    "3060 S 27th Avenue, Phoenix, AZ 85009",
    33.418, -112.088, PHX_TS,
    "Mon–Fri 5:30–17:00; Sat 6:00–15:00 — phoenix.gov",
    "602-262-7251", TRANSFER,
)
site(
    "Maricopa County New River Transfer Station (Scottsdale hub)",
    "County transfer — bulky / appliances / tires",
    "scottsdale", "AZ", "85087",
    "41835 N New River Road, Phoenix, AZ 85087",
    33.876, -112.146, MARI_ITEMS,
    "Wed–Sat 7:00–16:30 — maricopa.gov/3366",
    "602-525-5535", TRANSFER,
)
site(
    "Maricopa County Morristown Transfer Station (Scottsdale hub)",
    "County transfer — bulky / appliances / tires",
    "scottsdale", "AZ", "85342",
    "40135 N Highway 60, Morristown, AZ 85342",
    33.856, -112.616, MARI_ITEMS,
    "Wed & Sat 7:00–16:30 — maricopa.gov/3366",
    "602-329-3919", TRANSFER,
)
site(
    "Maricopa County Waste Tire — Pecos Road (Scottsdale hub)",
    "County tire drop-off — up to 5 tires/visit",
    "scottsdale", "AZ", "85212",
    "11400 E Pecos Road, Mesa, AZ 85212",
    33.295, -111.585, MARI_TIRE,
    "Mon–Sat 6:00–15:30 — maricopa.gov/1571",
    "480-987-2498", TIRES_ONLY,
)

# ── Hialeah / Miami-Dade TRC fills ──
MDC = "https://www.miamidade.gov/global/solidwaste/contact.page"
MDC_HOURS = "Daily 7:00–17:30 — miamidade.gov Trash & Recycling Centers"
MDC_PHONE = "305-468-5900"
for name, addr, zipc, lat, lng in [
    ("Golden Glades Trash and Recycling Center (Hialeah hub)", "140 NW 160th Street, Miami, FL 33169", "33169", 25.921, -80.204),
    ("Norwood Trash and Recycling Center (Hialeah hub)", "19901 NW 7th Avenue, Miami Gardens, FL 33169", "33169", 25.958, -80.209),
    ("West Little River Trash and Recycling Center (Hialeah hub)", "1830 NW 79th Street, Miami, FL 33147", "33147", 25.846, -80.227),
    ("Snapper Creek Trash and Recycling Center (Hialeah hub)", "2200 SW 117 Avenue, Miami, FL 33165", "33165", 25.750, -80.383),
    ("Sunset Kendall Trash and Recycling Center (Hialeah hub)", "8000 SW 107th Avenue, Miami, FL 33173", "33173", 25.696, -80.365),
]:
    site(name, "County TRC — bulky / appliances / tires / residential drop-off",
         "hialeah", "FL", zipc, addr, lat, lng, MDC, MDC_HOURS, MDC_PHONE, TRANSFER)

# ── Des Moines / Metro Waste Authority ──
site(
    "Metro Waste Authority — Metro Northwest Transfer Station (Grimes)",
    "Regional transfer — HHW by appointment / recycling",
    "des-moines", "IA", "50111",
    "4105 SE Beisser Drive, Grimes, IA 50111",
    41.685, -93.785,
    "https://www.mwatoday.com/locations/metro-northwest-transfer-station/",
    "HHW by appt (call 515-244-0021); 2nd Sat Mar–Nov 8:00–12:00 — mwatoday.com",
    "515-244-0021", HHW_E,
)
site(
    "Metro Waste Authority — Metro Hazardous Waste Drop-Off (Bondurant)",
    "Regional permanent HHW / e-waste drop-off",
    "des-moines", "IA", "50035",
    "1105 Prairie Drive SW, Bondurant, IA 50035",
    41.705, -93.565,
    "https://www.mwatoday.com/locations/metro-hazardous-waste-drop-offs/",
    "Tue–Fri 10:00–18:00; Sat 8:00–12:00 — mwatoday.com",
    "515-967-5512", HHW_E,
)
site(
    "Metro Waste Authority — Metro Park West Landfill (Perry)",
    "Regional landfill — self-haul",
    "des-moines", "IA", "50220",
    "20 335th Street, Perry, IA 50220",
    41.845, -94.105,
    "https://www.mwatoday.com/locations/metro-park-west-landfill/",
    "Mon–Fri 8:00–16:00; 1st Sat 9:00–12:00 — mwatoday.com",
    "515-333-5618", LANDFILL,
)
site(
    "Metro Waste Authority — Metro Park East Landfill (Mitchellville)",
    "Regional landfill — self-haul bulky / C&D",
    "des-moines", "IA", "50169",
    "12181 NE University Avenue, Mitchellville, IA 50169",
    41.665, -93.385,
    "https://www.mwatoday.com/locations/metro-park-east-landfill/",
    "Mon–Fri 6:30–16:30; Sat seasonal — mwatoday.com",
    "515-967-2076", LANDFILL,
)

# ── Winston-Salem / Forsyth collar ──
site(
    "Winston-Salem Hanes Mill Road Landfill — tires & white goods",
    "Municipal MSW landfill — tires / appliances / bulky",
    "winston-salem", "NC", "27105",
    "325 West Hanes Mill Road, Winston-Salem, NC 27105",
    36.155, -80.275,
    "https://www.cityofws.org/1256/Solid-Waste-Disposal",
    "Mon–Fri 7:00–16:30; Sat 8:00–12:00 — cityofws.org",
    "336-661-4900", mats(LANDFILL, APPLIANCE, TIRES),
)
site(
    "Winston-Salem Old Salisbury Road C&D Landfill",
    "Municipal C&D landfill — construction debris",
    "winston-salem", "NC", "27127",
    "3336 Old Salisbury Road, Winston-Salem, NC 27127",
    36.045, -80.275,
    "https://www.cityofws.org/1256/Solid-Waste-Disposal",
    "Mon–Fri 7:00–16:00 — cityofws.org",
    "336-727-8000", mats(CD, BULKY),
)
site(
    "3RC EnviroStation — Forsyth HHW & e-waste",
    "Municipal HHW / e-waste (Forsyth residents)",
    "winston-salem", "NC", "27107",
    "1401 S Martin Luther King Jr Drive, Winston-Salem, NC 27107",
    36.075, -80.235,
    "https://www.co.forsyth.nc.us/EAP/solid_waste.aspx",
    "Wed–Sat 9:00–15:00 — Forsyth residents free",
    "336-784-4300", HHW_E,
)
site(
    "Stokes County Waste Transfer & Recycling Station (Winston-Salem hub)",
    "County transfer — residential trash / C&D",
    "winston-salem", "NC", "27019",
    "2015 Sizemore Road, Germanton, NC 27019",
    36.265, -80.245,
    "https://www.co.stokes.nc.us/departments/waste_transfer___recycling_station.php",
    "Mon–Fri 8:30–16:30; Sat 8:30–12:00; Stokes residents — co.stokes.nc.us",
    "336-994-2357", TRANSFER,
)
site(
    "Davie County Solid Waste Transfer Station (Winston-Salem hub)",
    "County transfer — residential trash / metals / e-waste events",
    "winston-salem", "NC", "27028",
    "360 Dalton Road, Mocksville, NC 27028",
    35.879, -80.519,
    "https://www.daviecountync.gov/661/Solid-Waste-Transfer-Station",
    "Mon–Fri 7:30–16:30; Sat 7:30–12:00; Davie residents — daviecountync.gov",
    "336-998-6467", TRANSFER,
)

# ── Fort Wayne / Allen County ──
site(
    "Republic Services National Serv-All Landfill — Fort Wayne",
    "Regional landfill — MSW / C&D / residential self-haul",
    "fort-wayne", "IN", "46809",
    "6231 Macbeth Road, Fort Wayne, IN 46809",
    41.030, -85.220,
    "https://www.allencounty.in.gov/468/Community-Recycling-Drop-off-Sites",
    "Mon–Fri 8:00–17:00; Sat 8:00–12:00 — republicservices.com / ACDEM",
    "260-747-4117", LANDFILL,
)
site(
    "ACDEM Household Hazardous Waste Facility — Carroll Road",
    "County permanent HHW (Tox Tuesday + regular hours)",
    "fort-wayne", "IN", "46818",
    "2260 Carroll Road, Fort Wayne, IN 46818",
    41.195, -85.175,
    "https://www.allencounty.in.gov/483/Household-Hazardous-Waste-Disposal",
    "Tue 9:00–14:00 typical Tox Tuesday; call 260-449-4433 — allencounty.in.gov",
    "260-449-4433", HHW_ONLY,
)
site(
    "NISWMD Ashley Convenience Center — HHW & e-waste (Fort Wayne hub)",
    "District HHW / e-waste / residential solid waste",
    "fort-wayne", "IN", "46705",
    "2320 West 800 South, Ashley, IN 46705",
    41.525, -85.065,
    "https://www.niswmd.org/hazardous-waste/",
    "HHW Fridays 8:00–12:00; trash Mon–Fri 8:00–16:00 — DeKalb/Noble/Steuben/LaGrange",
    "260-587-3063", mats(HHW_E, BULKY),
)
site(
    "Whitley County Solid Waste Transfer Station — Columbia City",
    "County transfer — residential drop-off",
    "fort-wayne", "IN", "46725",
    "800 Industrial Drive, Columbia City, IN 46725",
    41.155, -85.485,
    "https://www.whitleygov.com/",
    "Confirm hours — Whitley County solid waste",
    "260-248-3100", TRANSFER,
)

# ── Yonkers / Westchester ──
WC_HMRF = "https://environment.westchestercountyny.gov/facilities/h-mrf"
site(
    "Westchester County Household Material Recovery Facility (H-MRF)",
    "County HHW / e-waste / Freon appliances / tires — appointment",
    "yonkers", "NY", "10595",
    "15 Woods Road, Valhalla, NY 10595",
    41.075, -73.785, WC_HMRF,
    "Tue–Sat 10:00–15:00 by appointment — environment.westchestercountyny.gov",
    "914-813-5425", mats(HHW_E, APPLIANCE, TIRES),
)
site(
    "Yonkers Recycling Center — Saw Mill River Road e-waste & bulk",
    "Municipal recycling / e-waste / bulk drop-off",
    "yonkers", "NY", "10710",
    "735 Saw Mill River Road, Yonkers, NY 10710",
    40.965, -73.865,
    "https://www.yonkersny.gov/",
    "Confirm hours — Yonkers A–Z Recycling & Refuse Guide",
    "914-377-4357", mats(E_WASTE, BULKY, APPLIANCE),
)
site(
    "White Plains e-waste collection pod (Yonkers hub)",
    "Municipal electronics drop-off pod — Westchester residents",
    "yonkers", "NY", "10605",
    "87 Gedney Way, White Plains, NY 10605",
    41.015, -73.755,
    "https://environment.westchestercountyny.gov/residents/recycling-guidelines/electronics-monitors-tvs",
    "Confirm municipal hours — Westchester e-waste pods",
    "914-813-5425", E_ONLY,
)
site(
    "Tuckahoe e-waste collection pod (Yonkers hub)",
    "Municipal electronics drop-off pod — Westchester residents",
    "yonkers", "NY", "10707",
    "15 Marbledale Road, Tuckahoe, NY 10707",
    40.955, -73.825,
    "https://environment.westchestercountyny.gov/residents/recycling-guidelines/electronics-monitors-tvs",
    "Confirm municipal hours — Westchester e-waste pods",
    "914-813-5425", E_ONLY,
)
site(
    "Dobbs Ferry e-waste collection pod (Yonkers hub)",
    "Municipal electronics drop-off pod — Westchester residents",
    "yonkers", "NY", "10522",
    "1 Stanley Avenue, Dobbs Ferry, NY 10522",
    41.015, -73.875,
    "https://environment.westchestercountyny.gov/residents/recycling-guidelines/electronics-monitors-tvs",
    "Confirm municipal hours — Westchester e-waste pods",
    "914-813-5425", E_ONLY,
)

# ── Lincoln collar ──
site(
    "BASWA / Beatrice Area Solid Waste Agency Landfill (Lincoln hub)",
    "Regional landfill — MSW; tires/white goods separated",
    "lincoln", "NE", "68310",
    "31229 SW 32nd Road, Beatrice, NE 68310",
    40.225, -96.785,
    "https://www.beatrice.ne.gov/living-in-beatrice/garbage-recycling-and-landfill/landfill/",
    "Mon–Fri 8:00–16:00; select Sat 9:00–12:30 — beatrice.ne.gov",
    "402-223-2267", LANDFILL,
)
site(
    "Lincoln Bluff Road Solid Waste Management Facility — public scale",
    "Municipal landfill / transfer — bulky / C&D",
    "lincoln", "NE", "68517",
    "6001 Bluff Road, Lincoln, NE 68517",
    40.785, -96.655,
    "https://www.lincoln.ne.gov/City/Departments/LTU/Utilities/Solid-Waste",
    "Confirm hours — lincoln.ne.gov Solid Waste",
    "402-441-7867", LANDFILL,
)
site(
    "Lincoln North 48th Street Transfer & C&D / HazToGo",
    "Municipal transfer / C&D / HazToGo HHW",
    "lincoln", "NE", "68504",
    "5101 N 48th Street, Lincoln, NE 68504",
    40.855, -96.655,
    "https://www.lincoln.ne.gov/City/Departments/LTU/Utilities/Solid-Waste",
    "Confirm hours — lincoln.ne.gov HazToGo",
    "402-441-8215", mats(TRANSFER, HHW_E),
)

# ── Louisville enrichments ──
site(
    "Louisville Metro Haz Bin — Grade Lane HHW",
    "Municipal permanent HHW drop-off",
    "louisville", "KY", "40213",
    "7501 Grade Lane, Louisville, KY 40213",
    38.155, -85.715,
    "https://louisvilleky.gov/government/public-works/services/hazardous-materials-disposal-haz-bin",
    "Tue–Sat 9:30–16:00; Jefferson County residents — louisvilleky.gov",
    "502-574-3572", HHW_ONLY,
)
site(
    "Louisville Metro Waste Reduction Center — Meriwether",
    "Municipal bulky / tires / e-waste / C&D drop-off",
    "louisville", "KY", "40208",
    "636 Meriwether Avenue, Louisville, KY 40208",
    38.225, -85.765,
    "https://louisvilleky.gov/government/public-works/waste-reduction-center",
    "Tue–Fri 8:00–17:00; Sat 8:00–15:00; entrance on Bland Street",
    "502-574-3572", mats(BULKY, APPLIANCE, TIRES, E_WASTE, CD),
)
site(
    "Louisville Outer Loop Recycling & Disposal Facility",
    "Regional landfill / recycling — self-haul",
    "louisville", "KY", "40219",
    "2673 Outer Loop, Louisville, KY 40219",
    38.125, -85.685,
    "https://louisvilleky.gov/government/public-works/services/junk-and-bulk-trash-disposal",
    "Confirm hours — Louisville Solid Waste",
    "502-574-3572", LANDFILL,
)

# ── Memphis enrichments ──
site(
    "Shelby County Household Hazardous Waste Facility — Haley Road",
    "County permanent HHW / limited e-waste",
    "memphis", "TN", "38134",
    "6305 Haley Road, Memphis, TN 38134",
    35.195, -89.855,
    "https://www.shelbycountytn.gov/439/Household-Hazardous-Waste",
    "Tue/Thu/Sat 8:00–13:00; Shelby County residents — shelbycountytn.gov",
    "901-222-7729", HHW_E,
)
site(
    "Shelby County Waste Tire Collection — Liberty Tire (Elvis Presley)",
    "County waste-tire collection site",
    "memphis", "TN", "38106",
    "3000 Elvis Presley Boulevard, Memphis, TN 38106",
    35.085, -90.025,
    "https://www.shelbycountytn.gov/3904/Waste-Tire-Program",
    "Mon–Fri 8:00–17:00 — shelbycountytn.gov Waste Tire Program",
    "901-396-5448", TIRES_ONLY,
)
site(
    "Memphis Solid Waste Convenience Center — Collins Street",
    "Municipal convenience center — bulky drop-off",
    "memphis", "TN", "38112",
    "304 Collins Street, Memphis, TN 38112",
    35.145, -90.035,
    "https://www.memphistn.gov/",
    "Fri–Sun 9:00–15:00 typical — City of Memphis Solid Waste",
    "901-636-4400", TRANSFER,
)
site(
    "Memphis Solid Waste Convenience Center — Farrisview",
    "Municipal convenience center — bulky drop-off",
    "memphis", "TN", "38118",
    "3207 Farrisview Boulevard, Memphis, TN 38118",
    35.055, -89.955,
    "https://www.memphistn.gov/",
    "Fri–Sun 9:00–15:00 typical — City of Memphis Solid Waste",
    "901-636-4400", TRANSFER,
)

# ── OC thin metro public landfills (correct public sites) ──
OC_LAND = "https://www.oclandfills.com/landfills/active-landfills"
OC_HHW = "https://oclandfills.com/hhw"
for city in ("santa-ana", "irvine", "anaheim"):
    site(
        f"OC Landfills — Olinda Alpha public scale ({city.replace('-', ' ').title()} hub)",
        "County landfill — public self-haul bulky / C&D",
        city, "CA", "92823",
        "1942 N Valencia Avenue, Brea, CA 92823",
        33.895, -117.835, OC_LAND,
        "Mon–Sat 7:00–16:00; OC residents — oclandfills.com",
        "714-834-4000", LANDFILL,
    )
    site(
        f"OC Landfills — Prima Deshecha public scale ({city.replace('-', ' ').title()} hub)",
        "County landfill — public self-haul bulky / C&D",
        city, "CA", "92675",
        "32250 Avenida La Pata, San Juan Capistrano, CA 92675",
        33.505, -117.605, OC_LAND,
        "Mon–Sat 7:00–17:00; OC residents — oclandfills.com",
        "714-834-4000", LANDFILL,
    )


def purge_mistags(rows: list[dict]) -> tuple[list[dict], int]:
    """Remove corrupted / wrongly-geo-tagged rows."""
    kept = []
    purged = 0
    for r in rows:
        name = (r.get("name") or "").lower()
        slug = r.get("city_slug")
        addr = (r.get("address") or "").lower()
        state = r.get("state")
        # Corrupted Nassau FL Callahan fused onto NYC
        if "callahan" in name and slug == "new-york":
            purged += 1
            continue
        if "musslewhite" in addr and state == "NY":
            purged += 1
            continue
        kept.append(r)
    # Retag distant St. Lucie landfill from miami → orlando (closer spine metro)
    for r in kept:
        if "glades cut-off" in (r.get("name") or "").lower() and r.get("city_slug") == "miami":
            r["city_slug"] = "orlando"
        # Hendry/Lee Clewiston & LaBelle transfers closer to Tampa corridor than Miami
        if r.get("city_slug") == "miami" and any(
            k in (r.get("name") or "") for k in ("Lee/Hendry", "Hendry County", "Clewiston", "LaBelle Transfer")
        ):
            if "Lee/Hendry" in (r.get("name") or "") or "Clewiston Transfer" in (r.get("name") or "") or "LaBelle Transfer" in (r.get("name") or ""):
                r["city_slug"] = "tampa"
    return kept, purged


def main() -> None:
    valid = {c["city_slug"]: c.get("state") for c in json.loads(CITIES_PATH.read_text())}
    for r in UPSERTS:
        if r["city_slug"] not in valid:
            raise SystemExit(f"unknown city_slug: {r['city_slug']}")
        if r.get("state") != valid[r["city_slug"]]:
            raise SystemExit(f"state mismatch: {r['name']} {r['state']} vs {valid[r['city_slug']]}")
        if not is_hard_facility(r):
            raise SystemExit(f"soft facility rejected: {r['name']}")

    existing = json.loads(FAC_PATH.read_text())
    existing, purged = purge_mistags(existing)
    before_hard = sum(1 for f in existing if is_hard_facility(f))

    by_key: dict[tuple, int] = {}
    by_addr: dict[tuple, int] = {}
    for i, row in enumerate(existing):
        by_key[(row.get("city_slug"), (row.get("name") or "").strip().lower())] = i
        na = norm_addr(row.get("address") or "")
        if na:
            by_addr[(row.get("city_slug"), na)] = i

    added = updated = skipped = 0
    for row in UPSERTS:
        key = (row["city_slug"], row["name"].strip().lower())
        na = norm_addr(row.get("address") or "")
        addr_key = (row["city_slug"], na) if na else None
        if key in by_key:
            existing[by_key[key]] = {**existing[by_key[key]], **row}
            updated += 1
        elif addr_key and addr_key in by_addr:
            skipped += 1
        else:
            existing.append(row)
            by_key[key] = len(existing) - 1
            if addr_key:
                by_addr[addr_key] = len(existing) - 1
            added += 1

    hard = [r for r in existing if is_hard_facility(r)]
    soft_dropped = len(existing) - len(hard)
    FAC_PATH.write_text(json.dumps(hard, indent=2, ensure_ascii=False) + "\n")

    from collections import Counter
    c = Counter(x["city_slug"] for x in hard)
    thin = sorted(c.items(), key=lambda x: x[1])[:12]
    print(
        f"added={added} updated={updated} skipped_dup={skipped} "
        f"mistags_purged={purged} soft_dropped={soft_dropped} "
        f"before_hard={before_hard} hard_total={len(hard)} upserts={len(UPSERTS)}"
    )
    print("thinnest", thin)


if __name__ == "__main__":
    main()
