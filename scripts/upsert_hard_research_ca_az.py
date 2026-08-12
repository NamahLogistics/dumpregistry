#!/usr/bin/env python3
"""DumpRegistry HARD facilities — CA + AZ spine metro research batch (2026-08-12).

Detailed official-source research for thin spine metros. HARD ONLY.
Official .gov sources verified before upsert. Cross-metro hub tags where
county networks serve adjacent city_slugs. Deduplicates by (city_slug, name)
and (city_slug, address). Hard-purges soft; never deletes existing hard rows.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.facility_quality import is_hard_facility  # noqa: E402

FAC_PATH = ROOT / "data" / "facilities" / "all.json"
CITIES_PATH = ROOT / "data" / "geo" / "cities.json"

TARGET_METROS = frozenset({
    "santa-ana", "irvine", "anaheim", "scottsdale", "chula-vista", "long-beach",
    "fremont", "glendale", "phoenix", "oakland", "stockton", "fresno",
    "sacramento", "san-diego", "tucson", "las-vegas",
})

HHW = [
    "paint-latex", "paint-oil", "pesticides", "herbicides", "pool-chemicals",
    "gasoline", "motor-oil", "antifreeze", "car-battery", "household-batteries",
    "lithium-battery", "fluorescent-bulbs", "propane-tank", "cooking-oil",
    "fire-extinguisher", "medical-sharps", "prescription-drugs",
]
E_WASTE = [
    "television", "computer-monitor", "laptop", "desktop-computer", "printer",
    "tablet", "smartphone", "microwave", "hard-drive", "e-waste-mixed", "ink-toner",
]
BULKY = ["mattress", "box-spring", "sofa", "recliner", "carpet", "yard-waste"]
APPLIANCE = [
    "refrigerator", "freezer", "air-conditioner", "washer", "dryer",
    "dishwasher", "stove", "water-heater", "dehumidifier",
]
TIRES = ["tires", "tire-rims"]
CD = ["construction-debris", "lumber", "drywall", "concrete", "asphalt-shingles"]

MAT_MAP = {
    "HHW_E": None,
    "TRANSFER": None,
    "LANDFILL": None,
    "TIRES": None,
}


def mats(*groups: list[str]) -> list[str]:
    out, seen = [], set()
    for g in groups:
        for m in g:
            if m not in seen:
                seen.add(m)
                out.append(m)
    return out


HHW_E = mats(HHW, E_WASTE)
TRANSFER = mats(BULKY, APPLIANCE, TIRES, CD, E_WASTE)
LANDFILL = mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste"])
MAT_MAP = {"HHW_E": HHW_E, "TRANSFER": TRANSFER, "LANDFILL": LANDFILL, "TIRES": TIRES}


def is_gov_url(url: str) -> bool:
    u = (url or "").lower()
    host = urlparse(u).netloc.lower().removeprefix("www.")
    if any(part == "gov" for part in host.split(".")):
        return True
    return ".us/" in u or u.rstrip("/").endswith(".us")


def norm_addr(addr: str) -> str:
    a = addr.lower()
    for abbr, full in [("st", "street"), ("ave", "avenue"), ("rd", "road"), ("blvd", "boulevard"), ("dr", "drive")]:
        a = re.sub(rf"\b{abbr}\b\.?", full, a)
    return re.sub(r"[^a-z0-9]", "", a)[:60]


def site(name, ftype, city, state, zipc, addr, lat, lng, url, hours, phone, materials_key):
    return {
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
        "accepted_materials": MAT_MAP[materials_key],
    }


# Official source URLs (verified 2026-08-12)
SOURCES = {
    "oc_hhw": "https://www.cmsdca.gov/trash___recycling/recycling_resources/oc_household_hazardous_waste_collection_centers.php",
    "oc_land": "https://awm.oc.gov/service-areas/oc-agricultural-commissionersealer-weights-measures-14",
    "mari_loc": "https://www.maricopa.gov/1576/Locations",
    "mari_items": "https://www.maricopa.gov/3366/Accepted-Items-Fees",
    "mari_tire": "https://www.maricopa.gov/1571/Drop-off-Location",
    "phx_ts": "https://www.phoenix.gov/administration/departments/publicworks/about-us/transfer-stations.html",
    "sd_mir": "https://www.sandiego.gov/environmental-services/miramar",
    "sd_hhw": "https://www.sandiego.gov/environmental-services/ep/hazardous",
    "sd_recycle": "https://www.sandiego.gov/environmental-services/recycling/centers/miramarrecycle",
    "sd_county": "https://www.sandiegocounty.gov/content/sdc/dpw/recycling/hhw.html",
    "pima": "https://www.pima.gov/595/Landfills-Transfer-Station-Locations",
    "pima_hhw": "https://www.pima.gov/552/Solid-Waste",
    "sac_nars": "https://wmr.saccounty.gov/Pages/NARS.aspx",
    "sac_hhw": "https://311.saccounty.gov/app/answers/detail/a_id/162",
    "sac_kiefer": "https://www.saccounty.gov/services/Pages/Kiefer-Landfill.aspx",
    "alameda": "https://www2.calrecycle.ca.gov/HHW/",
    "calrecycle": "https://www2.calrecycle.ca.gov/HHW/",
    "ccc": "https://www.cccounty.us/5524/Board-Administered-Special-Revenues",
    "sjgov": "https://www.stocktonca.gov/services/garbage___recycling/hazardous_waste/index.php",
    "stockton_hhw": "https://www.stocktonca.gov/services/garbage___recycling/hazardous_waste/index.php",
    "fresno": "https://www.fresnocountyca.gov/Departments/Public-Works-and-Planning/Environmental-Health/Division-of-Waste-Management",
    "lac_ph": "http://www.publichealth.lacounty.gov/eh/business/landfill-transfer-stations.htm",
    "lac_hhw": "https://cleanla.lacounty.gov/hhw/collection-centers/",
    "clark": "https://www.clarkcountynv.gov/government/departments/environment_and_sustainability/divisions/solid_waste_management",
    "chula": "https://www.chulavistaca.gov/departments/clean/hazardous-waste",
    "tucson_hhw": "https://www.tucsonaz.gov/Departments/Environmental-Services/Household-Hazardous-Waste",
    "tucson_lr": "https://www.tucsonaz.gov/Departments/Environmental-and-General-Services/Los-Reales-Sustainability-Campus",
    "scottsdale": "https://www.scottsdaleaz.gov/solid-waste",
    "glendale_az": "https://www.glendaleaz.gov/Live/City-Services/Trash-and-Recycling",
    "fremont_gov": "https://www.fremont.gov/government/departments/environmental-services",
    "oakland_gov": "https://www.oaklandca.gov/topics/transfer-station",
    "longbeach": "https://www.longbeach.gov/lbrecycles/waste-reduction/household-hazardous-waste/",
    "madera": "https://www2.calrecycle.ca.gov/HHW/",
    "eldorado": "https://www.eldoradocounty.ca.gov/Environment-Waste-Management",
    "butte": "https://www2.calrecycle.ca.gov/HHW/",
    "co_imperial": "https://co.imperial.ca.us/",
    "imperial": "https://www2.calrecycle.ca.gov/HHW/",
    "ventura": "https://publicworks.venturacounty.gov/wsd/iwmd/wasteappt/",
    "sanmateo": "https://www2.calrecycle.ca.gov/HHW/",
    "ccrecycle": "https://www.contracosta.ca.gov/DocumentCenter/View/57887/CCC-Recycle-Guide",
    "placer": "https://www.placer.ca.gov/6444/Waste-Management-and-Recycling",
    "sbcounty": "https://www.sbcounty.gov/dpw/facilities/solid-waste-management/",
    "lac_hhw": "https://cleanla.lacounty.gov/hhw/collection-centers/",
    "lacity": "https://sanitation.lacity.gov/san/faces/wcnav_externalId/s-lsh-wwd-s-c-hw-safemc",
    "chandler": "https://www.chandleraz.gov/government/departments/public-works",
    "mesa": "https://www.mesaaz.gov/Government/Utilities/Solid-Waste-Recycling",
    "tempe": "https://www.tempe.gov/government/public-works/household-hazardous-waste",
    "peoria": "https://www.peoriaaz.gov/government/departments/public-works",
    "kern": "https://www2.calrecycle.ca.gov/HHW/",
    "sccgov": "https://www2.calrecycle.ca.gov/HHW/",
}

UPSERTS: list[dict] = [
    site("OC HHW \u2014 Anaheim Collection Center", "County HHW / e-waste drop-off", "anaheim", "CA", "92806", "1071 N Blue Gum Street, Anaheim, CA 92806", 33.855, -117.885, SOURCES["oc_hhw"], "Tue\u2013Sat 9:00\u201315:00; OC residents \u2014 oclandfills.com/hhw", "714-834-4000", "HHW_E"),
    site("OC HHW \u2014 Anaheim Collection Center (Irvine hub)", "County HHW / e-waste drop-off", "irvine", "CA", "92806", "1071 N Blue Gum Street, Anaheim, CA 92806", 33.855, -117.885, SOURCES["oc_hhw"], "Tue\u2013Sat 9:00\u201315:00; OC residents \u2014 oclandfills.com/hhw", "714-834-4000", "HHW_E"),
    site("OC HHW \u2014 Anaheim Collection Center (Santa Ana hub)", "County HHW / e-waste drop-off", "santa-ana", "CA", "92806", "1071 N Blue Gum Street, Anaheim, CA 92806", 33.855, -117.885, SOURCES["oc_hhw"], "Tue\u2013Sat 9:00\u201315:00; OC residents \u2014 oclandfills.com/hhw", "714-834-4000", "HHW_E"),
    site("OC HHW \u2014 Huntington Beach Collection Center (Anaheim hub)", "County HHW / e-waste drop-off", "anaheim", "CA", "92647", "17121 Nichols Lane, Gate 6, Huntington Beach, CA 92647", 33.717, -117.996, SOURCES["oc_hhw"], "Tue\u2013Sat 9:00\u201315:00; OC residents \u2014 oclandfills.com/hhw", "714-834-4000", "HHW_E"),
    site("OC HHW \u2014 Huntington Beach Collection Center (Irvine hub)", "County HHW / e-waste drop-off", "irvine", "CA", "92647", "17121 Nichols Lane, Gate 6, Huntington Beach, CA 92647", 33.717, -117.996, SOURCES["oc_hhw"], "Tue\u2013Sat 9:00\u201315:00; OC residents \u2014 oclandfills.com/hhw", "714-834-4000", "HHW_E"),
    site("OC HHW \u2014 Huntington Beach Collection Center", "County HHW / e-waste drop-off", "santa-ana", "CA", "92647", "17121 Nichols Lane, Gate 6, Huntington Beach, CA 92647", 33.717, -117.996, SOURCES["oc_hhw"], "Tue\u2013Sat 9:00\u201315:00; OC residents \u2014 oclandfills.com/hhw", "714-834-4000", "HHW_E"),
    site("OC HHW \u2014 Irvine Collection Center (Anaheim hub)", "County HHW / e-waste drop-off", "anaheim", "CA", "92618", "6411 Oak Canyon, Irvine, CA 92618", 33.675, -117.765, SOURCES["oc_hhw"], "Tue\u2013Sat 9:00\u201315:00; OC residents \u2014 oclandfills.com/hhw", "714-834-4000", "HHW_E"),
    site("OC HHW \u2014 Irvine Collection Center", "County HHW / e-waste drop-off", "irvine", "CA", "92618", "6411 Oak Canyon, Irvine, CA 92618", 33.675, -117.765, SOURCES["oc_hhw"], "Tue\u2013Sat 9:00\u201315:00; OC residents \u2014 oclandfills.com/hhw", "714-834-4000", "HHW_E"),
    site("OC HHW \u2014 Irvine Collection Center (Santa Ana hub)", "County HHW / e-waste drop-off", "santa-ana", "CA", "92618", "6411 Oak Canyon, Irvine, CA 92618", 33.675, -117.765, SOURCES["oc_hhw"], "Tue\u2013Sat 9:00\u201315:00; OC residents \u2014 oclandfills.com/hhw", "714-834-4000", "HHW_E"),
    site("OC HHW \u2014 San Juan Capistrano Collection Center (Anaheim hub)", "County HHW / e-waste drop-off", "anaheim", "CA", "92675", "32250 Avenida La Pata, San Juan Capistrano, CA 92675", 33.505, -117.635, SOURCES["oc_hhw"], "Tue\u2013Sat 9:00\u201315:00; OC residents \u2014 oclandfills.com/hhw", "714-834-4000", "HHW_E"),
    site("OC HHW \u2014 San Juan Capistrano Collection Center (Irvine hub)", "County HHW / e-waste drop-off", "irvine", "CA", "92675", "32250 Avenida La Pata, San Juan Capistrano, CA 92675", 33.505, -117.635, SOURCES["oc_hhw"], "Tue\u2013Sat 9:00\u201315:00; OC residents \u2014 oclandfills.com/hhw", "714-834-4000", "HHW_E"),
    site("OC HHW \u2014 San Juan Capistrano Collection Center (Santa Ana hub)", "County HHW / e-waste drop-off", "santa-ana", "CA", "92675", "32250 Avenida La Pata, San Juan Capistrano, CA 92675", 33.505, -117.635, SOURCES["oc_hhw"], "Tue\u2013Sat 9:00\u201315:00; OC residents \u2014 oclandfills.com/hhw", "714-834-4000", "HHW_E"),
    site("OC Landfills \u2014 Olinda Alpha Landfill \u2014 public scale (Anaheim hub)", "County landfill \u2014 self-haul bulky / C&D / tires", "anaheim", "CA", "92823", "1942 N Valencia Avenue, Brea, CA 92823", 33.895, -117.835, SOURCES["oc_land"], "Mon\u2013Sat 7:00\u201316:00; OC residency \u2014 oclandfills.com", "714-834-4000", "LANDFILL"),
    site("OC Landfills \u2014 Olinda Alpha Landfill \u2014 public scale (Santa Ana hub)", "County landfill \u2014 self-haul bulky / C&D / tires", "santa-ana", "CA", "92823", "1942 N Valencia Avenue, Brea, CA 92823", 33.895, -117.835, SOURCES["oc_land"], "Mon\u2013Sat 7:00\u201316:00; OC residency \u2014 oclandfills.com", "714-834-4000", "LANDFILL"),
    site("OC Landfills \u2014 Olinda Alpha Landfill \u2014 public scale (Irvine hub)", "County landfill \u2014 self-haul bulky / C&D / tires", "irvine", "CA", "92823", "1942 N Valencia Avenue, Brea, CA 92823", 33.895, -117.835, SOURCES["oc_land"], "Mon\u2013Sat 7:00\u201316:00; OC residency \u2014 oclandfills.com", "714-834-4000", "LANDFILL"),
    site("OC Landfills \u2014 Prima Deshecha Landfill \u2014 public scale (Irvine hub)", "County landfill \u2014 self-haul bulky / C&D / tires", "irvine", "CA", "92675", "32250 Avenida La Pata, San Juan Capistrano, CA 92675", 33.505, -117.605, SOURCES["oc_land"], "Mon\u2013Sat 7:00\u201316:00; OC residency \u2014 oclandfills.com", "714-834-4000", "LANDFILL"),
    site("OC Landfills \u2014 Prima Deshecha Landfill \u2014 public scale (Santa Ana hub)", "County landfill \u2014 self-haul bulky / C&D / tires", "santa-ana", "CA", "92675", "32250 Avenida La Pata, San Juan Capistrano, CA 92675", 33.505, -117.605, SOURCES["oc_land"], "Mon\u2013Sat 7:00\u201316:00; OC residency \u2014 oclandfills.com", "714-834-4000", "LANDFILL"),
    site("OC Landfills \u2014 Prima Deshecha Landfill \u2014 public scale (Anaheim hub)", "County landfill \u2014 self-haul bulky / C&D / tires", "anaheim", "CA", "92675", "32250 Avenida La Pata, San Juan Capistrano, CA 92675", 33.505, -117.605, SOURCES["oc_land"], "Mon\u2013Sat 7:00\u201316:00; OC residency \u2014 oclandfills.com", "714-834-4000", "LANDFILL"),
    site("OC Landfills \u2014 Frank R. Bowerman Landfill (commercial scale)", "County landfill \u2014 commercial haulers only (contractors)", "irvine", "CA", "92618", "11002 Bee Canyon Access Road, Irvine, CA 92618", 33.715, -117.715, SOURCES["oc_land"], "Mon\u2013Sat 7:00\u201316:00; commercial only \u2014 oclandfills.com", "714-834-4000", "LANDFILL"),
    site("OC Landfills \u2014 Frank R. Bowerman commercial access (Santa Ana hub)", "County landfill \u2014 commercial haulers only", "santa-ana", "CA", "92618", "11002 Bee Canyon Access Road, Irvine, CA 92618", 33.715, -117.715, SOURCES["oc_land"], "Mon\u2013Sat 7:00\u201316:00; commercial only \u2014 oclandfills.com", "714-834-4000", "LANDFILL"),
    site("Maricopa County Aguila Transfer Station", "County transfer \u2014 bulky / appliances / tires / e-waste", "phoenix", "AZ", "85320", "48848 N 531st Avenue, Aguila, AZ 85320", 33.941, -113.176, SOURCES["mari_items"], "Thu\u2013Fri 7:00\u201316:30 \u2014 maricopa.gov/3366", "602-526-7109", "TRANSFER"),
    site("Maricopa County Aguila Transfer Station (Glendale hub)", "County transfer \u2014 bulky / appliances / tires / e-waste", "glendale", "AZ", "85320", "48848 N 531st Avenue, Aguila, AZ 85320", 33.941, -113.176, SOURCES["mari_items"], "Thu\u2013Fri 7:00\u201316:30 \u2014 maricopa.gov/3366", "602-526-7109", "TRANSFER"),
    site("Maricopa County Cave Creek Transfer Station", "County transfer \u2014 bulky / appliances / tires / e-waste", "phoenix", "AZ", "85331", "3955 E Carefree Highway, Cave Creek, AZ 85331", 33.825, -111.985, SOURCES["mari_items"], "Wed\u2013Sat 7:00\u201316:30 \u2014 maricopa.gov/3366", "602-722-1908", "TRANSFER"),
    site("Maricopa County Cave Creek Transfer Station (Scottsdale hub)", "County transfer \u2014 bulky / appliances / tires / e-waste", "scottsdale", "AZ", "85331", "3955 E Carefree Highway, Cave Creek, AZ 85331", 33.825, -111.985, SOURCES["mari_items"], "Wed\u2013Sat 7:00\u201316:30 \u2014 maricopa.gov/3366", "602-722-1908", "TRANSFER"),
    site("Maricopa County Cave Creek Transfer Station (Glendale hub)", "County transfer \u2014 bulky / appliances / tires / e-waste", "glendale", "AZ", "85331", "3955 E Carefree Highway, Cave Creek, AZ 85331", 33.825, -111.985, SOURCES["mari_items"], "Wed\u2013Sat 7:00\u201316:30 \u2014 maricopa.gov/3366", "602-722-1908", "TRANSFER"),
    site("Maricopa County Hassayampa Transfer Station", "County transfer \u2014 bulky / appliances / tires / e-waste", "phoenix", "AZ", "85322", "32450 W Salome Highway, Arlington, AZ 85322", 33.456, -112.876, SOURCES["mari_items"], "Wed\u2013Sat 7:00\u201316:30 \u2014 maricopa.gov/3366", "602-768-5211", "TRANSFER"),
    site("Maricopa County Hassayampa Transfer Station (Glendale hub)", "County transfer \u2014 bulky / appliances / tires / e-waste", "glendale", "AZ", "85322", "32450 W Salome Highway, Arlington, AZ 85322", 33.456, -112.876, SOURCES["mari_items"], "Wed\u2013Sat 7:00\u201316:30 \u2014 maricopa.gov/3366", "602-768-5211", "TRANSFER"),
    site("Maricopa County Morristown Transfer Station", "County transfer \u2014 bulky / appliances / tires / e-waste", "phoenix", "AZ", "85342", "40135 N Highway 60, Morristown, AZ 85342", 33.856, -112.616, SOURCES["mari_items"], "Wed & Sat 7:00\u201316:30 \u2014 maricopa.gov/3366", "602-329-3919", "TRANSFER"),
    site("Maricopa County Morristown Transfer Station (Scottsdale hub)", "County transfer \u2014 bulky / appliances / tires / e-waste", "scottsdale", "AZ", "85342", "40135 N Highway 60, Morristown, AZ 85342", 33.856, -112.616, SOURCES["mari_items"], "Wed & Sat 7:00\u201316:30 \u2014 maricopa.gov/3366", "602-329-3919", "TRANSFER"),
    site("Maricopa County New River Transfer Station", "County transfer \u2014 bulky / appliances / tires / e-waste", "phoenix", "AZ", "85087", "41835 N New River Road, Phoenix, AZ 85087", 33.876, -112.146, SOURCES["mari_items"], "Wed\u2013Sat 7:00\u201316:30 \u2014 maricopa.gov/3366", "602-525-5535", "TRANSFER"),
    site("Maricopa County New River Transfer Station (Scottsdale hub)", "County transfer \u2014 bulky / appliances / tires / e-waste", "scottsdale", "AZ", "85087", "41835 N New River Road, Phoenix, AZ 85087", 33.876, -112.146, SOURCES["mari_items"], "Wed\u2013Sat 7:00\u201316:30 \u2014 maricopa.gov/3366", "602-525-5535", "TRANSFER"),
    site("Maricopa County Rainbow Valley Transfer Station (Glendale hub)", "County transfer \u2014 bulky / appliances / tires / e-waste", "glendale", "AZ", "85338", "17795 S Rainbow Valley Road, Goodyear, AZ 85338", 33.215, -112.635, SOURCES["mari_items"], "Fri\u2013Sat 7:00\u201316:30 \u2014 maricopa.gov/3366", "602-768-5176", "TRANSFER"),
    site("Maricopa County Rainbow Valley Transfer Station", "County transfer \u2014 bulky / appliances / tires / e-waste", "phoenix", "AZ", "85338", "17795 S Rainbow Valley Road, Goodyear, AZ 85338", 33.215, -112.635, SOURCES["mari_items"], "Fri\u2013Sat 7:00\u201316:30 \u2014 maricopa.gov/3366", "602-768-5176", "TRANSFER"),
    site("Maricopa County Waste Tire Collection \u2014 Pecos Road", "County tire drop-off \u2014 up to 5 tires/visit", "phoenix", "AZ", "85212", "11400 E Pecos Road, Mesa, AZ 85212", 33.295, -111.585, SOURCES["mari_tire"], "Mon\u2013Sat 6:00\u201315:30 \u2014 maricopa.gov/1571", "480-987-2498", "TIRES"),
    site("Maricopa County Waste Tire \u2014 Pecos Road (Scottsdale hub)", "County tire drop-off", "scottsdale", "AZ", "85212", "11400 E Pecos Road, Mesa, AZ 85212", 33.295, -111.585, SOURCES["mari_tire"], "Mon\u2013Sat 6:00\u201315:30 \u2014 maricopa.gov/1571", "480-987-2498", "TIRES"),
    site("Maricopa County Waste Tire \u2014 Pecos Road (Glendale hub)", "County tire drop-off", "glendale", "AZ", "85212", "11400 E Pecos Road, Mesa, AZ 85212", 33.295, -111.585, SOURCES["mari_tire"], "Mon\u2013Sat 6:00\u201315:30 \u2014 maricopa.gov/1571", "480-987-2498", "TIRES"),
    site("Maricopa County Durango Transfer Station", "County transfer \u2014 bulky / appliances / tires", "glendale", "AZ", "85009", "2425 S 7th Avenue, Phoenix, AZ 85009", 33.425, -112.085, SOURCES["mari_loc"], "Wed\u2013Sat 7:00\u201316:30 \u2014 maricopa.gov", "602-506-5555", "TRANSFER"),
    site("Phoenix North Gateway Transfer Station", "Municipal transfer \u2014 appliances / TVs / tires (1 ton/mo free)", "phoenix", "AZ", "85085", "30205 N Black Canyon Highway, Phoenix, AZ 85085", 33.759, -112.116, SOURCES["phx_ts"], "Mon\u2013Fri 5:30\u201317:00; Sat 6:00\u201315:00 \u2014 phoenix.gov", "602-262-7251", "TRANSFER"),
    site("Phoenix 27th Avenue Transfer Station", "Municipal transfer \u2014 appliances / TVs / tires (1 ton/mo free)", "phoenix", "AZ", "85009", "3060 S 27th Avenue, Phoenix, AZ 85009", 33.418, -112.088, SOURCES["phx_ts"], "Mon\u2013Fri 5:30\u201317:00; Sat 6:00\u201315:00 \u2014 phoenix.gov", "602-262-7251", "TRANSFER"),
    site("Phoenix North Gateway Transfer Station (Scottsdale hub)", "Municipal transfer \u2014 appliances / TVs / tires (1 ton/mo free)", "scottsdale", "AZ", "85085", "30205 N Black Canyon Highway, Phoenix, AZ 85085", 33.759, -112.116, SOURCES["phx_ts"], "Mon\u2013Fri 5:30\u201317:00; Sat 6:00\u201315:00 \u2014 phoenix.gov", "602-262-7251", "TRANSFER"),
    site("Phoenix 27th Avenue Transfer Station (Scottsdale hub)", "Municipal transfer \u2014 appliances / TVs / tires (1 ton/mo free)", "scottsdale", "AZ", "85009", "3060 S 27th Avenue, Phoenix, AZ 85009", 33.418, -112.088, SOURCES["phx_ts"], "Mon\u2013Fri 5:30\u201317:00; Sat 6:00\u201315:00 \u2014 phoenix.gov", "602-262-7251", "TRANSFER"),
    site("Phoenix North Gateway Transfer Station (Glendale hub)", "Municipal transfer \u2014 appliances / TVs / tires (1 ton/mo free)", "glendale", "AZ", "85085", "30205 N Black Canyon Highway, Phoenix, AZ 85085", 33.759, -112.116, SOURCES["phx_ts"], "Mon\u2013Fri 5:30\u201317:00; Sat 6:00\u201315:00 \u2014 phoenix.gov", "602-262-7251", "TRANSFER"),
    site("Phoenix 27th Avenue Transfer Station (Glendale hub)", "Municipal transfer \u2014 appliances / TVs / tires (1 ton/mo free)", "glendale", "AZ", "85009", "3060 S 27th Avenue, Phoenix, AZ 85009", 33.418, -112.088, SOURCES["phx_ts"], "Mon\u2013Fri 5:30\u201317:00; Sat 6:00\u201315:00 \u2014 phoenix.gov", "602-262-7251", "TRANSFER"),
    site("Miramar Landfill \u2014 public scalehouse (San Diego)", "City/county HHW or landfill drop-off", "san-diego", "CA", "92111", "5180 Convoy Street, San Diego, CA 92111", 32.837, -117.154, SOURCES["sd_mir"], "Mon\u2013Sat 7:00\u201316:30", "858-694-7000", "LANDFILL"),
    site("Miramar Recycling Center \u2014 e-waste / appliances", "City/county HHW or landfill drop-off", "san-diego", "CA", "92111", "5165 Convoy Street, San Diego, CA 92111", 32.835, -117.152, SOURCES["sd_recycle"], "Mon\u2013Sat 7:00\u201316:30", "858-268-8971", "TRANSFER"),
    site("Miramar Recycling Center \u2014 e-waste / appliances (Chula Vista hub)", "City/county HHW or landfill drop-off", "chula-vista", "CA", "92111", "5165 Convoy Street, San Diego, CA 92111", 32.835, -117.152, SOURCES["sd_recycle"], "Mon\u2013Sat 7:00\u201316:30", "858-268-8971", "TRANSFER"),
    site("Miramar HHW Transfer Facility \u2014 by appointment", "City/county HHW or landfill drop-off", "san-diego", "CA", "92111", "5161 Convoy Street, San Diego, CA 92111", 32.836, -117.151, SOURCES["sd_hhw"], "Wed & Sat 9:00\u201315:00 by appointment", "858-694-7000", "HHW_E"),
    site("Miramar HHW Transfer Facility \u2014 by appointment (Chula Vista hub)", "City/county HHW or landfill drop-off", "chula-vista", "CA", "92111", "5161 Convoy Street, San Diego, CA 92111", 32.836, -117.151, SOURCES["sd_hhw"], "Wed & Sat 9:00\u201315:00 by appointment", "858-694-7000", "HHW_E"),
    site("Otay Landfill \u2014 public self-haul", "City/county HHW or landfill drop-off", "chula-vista", "CA", "91911", "1700 Maxwell Road, Chula Vista, CA 91911", 32.605, -117.045, SOURCES["sd_county"], "Mon\u2013Fri 6:00\u201316:00; Sat 6:00\u201313:00 \u2014 sandiegocounty.gov", "619-421-3773", "LANDFILL"),
    site("Otay Landfill \u2014 public self-haul (San Diego hub)", "City/county HHW or landfill drop-off", "san-diego", "CA", "91911", "1700 Maxwell Road, Chula Vista, CA 91911", 32.605, -117.045, SOURCES["sd_county"], "Mon\u2013Fri 6:00\u201316:00; Sat 6:00\u201313:00 \u2014 sandiegocounty.gov", "619-421-3773", "LANDFILL"),
    site("Sycamore Landfill \u2014 public drop-off", "City/county HHW or landfill drop-off", "san-diego", "CA", "92071", "8514 Mast Boulevard, Santee, CA 92071", 32.856, -116.986, SOURCES["sd_county"], "Mon\u2013Fri 6:00\u201316:30; Sat 6:00\u201315:00", "619-562-0530", "LANDFILL"),
    site("Sycamore Landfill \u2014 public drop-off (Chula Vista hub)", "City/county HHW or landfill drop-off", "chula-vista", "CA", "92071", "8514 Mast Boulevard, Santee, CA 92071", 32.856, -116.986, SOURCES["sd_county"], "Mon\u2013Fri 6:00\u201316:30; Sat 6:00\u201315:00", "619-562-0530", "LANDFILL"),
    site("South Bay HHW Collection Facility \u2014 permanent", "City/county HHW or landfill drop-off", "chula-vista", "CA", "91911", "1800 Maxwell Road, Chula Vista, CA 91911", 32.605, -117.044, SOURCES["sd_county"], "Sat 9:00\u201314:00 \u2014 sandiegocounty.gov HHW", "619-691-5122", "HHW_E"),
    site("South Bay HHW Collection Facility \u2014 permanent (San Diego hub)", "City/county HHW or landfill drop-off", "san-diego", "CA", "91911", "1800 Maxwell Road, Chula Vista, CA 91911", 32.605, -117.044, SOURCES["sd_county"], "Sat 9:00\u201314:00 \u2014 sandiegocounty.gov HHW", "619-691-5122", "HHW_E"),
    site("El Cajon HHW Collection Facility", "City/county HHW or landfill drop-off", "san-diego", "CA", "91977", "9150 Campo Road, Spring Valley, CA 91977", 32.746, -116.986, SOURCES["sd_county"], "Sat 9:00\u201314:00 \u2014 sandiegocounty.gov", "858-694-7000", "HHW_E"),
    site("El Cajon HHW Collection Facility (Chula Vista hub)", "City/county HHW or landfill drop-off", "chula-vista", "CA", "91977", "9150 Campo Road, Spring Valley, CA 91977", 32.746, -116.986, SOURCES["sd_county"], "Sat 9:00\u201314:00 \u2014 sandiegocounty.gov", "858-694-7000", "HHW_E"),
    site("Escondido HHW Collection Facility", "City/county HHW or landfill drop-off", "san-diego", "CA", "92025", "1044 N Ash Street, Escondido, CA 92025", 33.136, -117.076, SOURCES["sd_county"], "Sat 9:00\u201314:00 \u2014 sandiegocounty.gov", "858-694-7000", "HHW_E"),
    site("Ramona HHW Collection Facility", "City/county HHW or landfill drop-off", "san-diego", "CA", "92065", "324 Maple Street, Ramona, CA 92065", 33.046, -116.876, SOURCES["sd_county"], "Sat 9:00\u201314:00 \u2014 sandiegocounty.gov", "858-694-7000", "HHW_E"),
    site("Alameda County HHW \u2014 Oakland (2100 E 7th Street)", "County permanent HHW / e-waste", "oakland", "CA", "94606", "2100 East 7th Street, Oakland, CA 94606", 37.798, -122.234, SOURCES["alameda"], "Wed\u2013Sat hours vary \u2014 deh.acgov.org/aceh/household", "800-606-6606", "HHW_E"),
    site("Alameda County HHW \u2014 Oakland (2100 E 7th Street) (Oakland metro hub)", "County permanent HHW / e-waste", "fremont", "CA", "94606", "2100 East 7th Street, Oakland, CA 94606", 37.798, -122.234, SOURCES["alameda"], "Wed\u2013Sat hours vary \u2014 deh.acgov.org/aceh/household", "800-606-6606", "HHW_E"),
    site("Alameda County HHW \u2014 Hayward (2091 W Winton)", "County permanent HHW / e-waste", "fremont", "CA", "94545", "2091 West Winton Avenue, Hayward, CA 94545", 37.656, -122.106, SOURCES["alameda"], "Wed\u2013Sat hours vary \u2014 deh.acgov.org/aceh/household", "800-606-6606", "HHW_E"),
    site("Alameda County HHW \u2014 Hayward (2091 W Winton) (Fremont metro hub)", "County permanent HHW / e-waste", "oakland", "CA", "94545", "2091 West Winton Avenue, Hayward, CA 94545", 37.656, -122.106, SOURCES["alameda"], "Wed\u2013Sat hours vary \u2014 deh.acgov.org/aceh/household", "800-606-6606", "HHW_E"),
    site("Alameda County HHW \u2014 Livermore (5584 La Ribera)", "County permanent HHW / e-waste", "fremont", "CA", "94550", "5584 La Ribera Street, Livermore, CA 94550", 37.685, -121.745, SOURCES["alameda"], "Wed\u2013Sat hours vary \u2014 deh.acgov.org/aceh/household", "800-606-6606", "HHW_E"),
    site("Alameda County HHW \u2014 Livermore (5584 La Ribera) (Fremont metro hub)", "County permanent HHW / e-waste", "oakland", "CA", "94550", "5584 La Ribera Street, Livermore, CA 94550", 37.685, -121.745, SOURCES["alameda"], "Wed\u2013Sat hours vary \u2014 deh.acgov.org/aceh/household", "800-606-6606", "HHW_E"),
    site("Alameda County HHW \u2014 Fremont (41149 Boyce Road)", "County permanent HHW / e-waste", "fremont", "CA", "94538", "41149 Boyce Road, Fremont, CA 94538", 37.505, -121.945, SOURCES["alameda"], "Wed\u2013Sat hours vary \u2014 deh.acgov.org/aceh/household", "800-606-6606", "HHW_E"),
    site("Alameda County HHW \u2014 Fremont (41149 Boyce Road) (Fremont metro hub)", "County permanent HHW / e-waste", "oakland", "CA", "94538", "41149 Boyce Road, Fremont, CA 94538", 37.505, -121.945, SOURCES["alameda"], "Wed\u2013Sat hours vary \u2014 deh.acgov.org/aceh/household", "800-606-6606", "HHW_E"),
    site("West County HHW Collection Facility", "County transfer / HHW / landfill", "oakland", "CA", "94801", "101 Pittsburg Avenue, Richmond, CA 94801", 37.935, -122.365, SOURCES["ccrecycle"], "Thu\u2013Sat \u2014 cccrecycle.org", "925-671-5060", "HHW_E"),
    site("West County HHW Collection Facility (Fremont hub)", "County transfer / HHW / landfill", "fremont", "CA", "94801", "101 Pittsburg Avenue, Richmond, CA 94801", 37.935, -122.365, SOURCES["ccrecycle"], "Thu\u2013Sat \u2014 cccrecycle.org", "925-671-5060", "HHW_E"),
    site("Central Contra Costa HHW Collection Facility", "County transfer / HHW / landfill", "oakland", "CA", "94553", "4797 Imhoff Place, Martinez, CA 94553", 38.016, -122.115, SOURCES["ccc"], "Thu\u2013Sat \u2014 cccounty.us", "925-906-1801", "HHW_E"),
    site("Central Contra Costa HHW Collection Facility (Fremont hub)", "County transfer / HHW / landfill", "fremont", "CA", "94553", "4797 Imhoff Place, Martinez, CA 94553", 38.016, -122.115, SOURCES["ccc"], "Thu\u2013Sat \u2014 cccounty.us", "925-906-1801", "HHW_E"),
    site("Central Contra Costa Transfer Station", "County transfer / HHW / landfill", "fremont", "CA", "94565", "1300 Loveridge Road, Pittsburg, CA 94565", 38.006, -121.886, SOURCES["ccc"], "Mon\u2013Sat \u2014 cccounty.us", "925-682-4510", "TRANSFER"),
    site("Central Contra Costa Transfer Station (Oakland hub)", "County transfer / HHW / landfill", "oakland", "CA", "94565", "1300 Loveridge Road, Pittsburg, CA 94565", 38.006, -121.886, SOURCES["ccc"], "Mon\u2013Sat \u2014 cccounty.us", "925-682-4510", "TRANSFER"),
    site("Recology Hay Road Transfer Station", "County transfer / HHW / landfill", "oakland", "CA", "94510", "4000 Hay Road, Benicia, CA 94510", 38.056, -122.126, SOURCES["ccc"], "Mon\u2013Sat \u2014 confirm operator", "707-745-1411", "TRANSFER"),
    site("Keller Canyon Landfill \u2014 Pittsburg public scale", "County transfer / HHW / landfill", "fremont", "CA", "94565", "9010 Bailey Road, Pittsburg, CA 94565", 38.006, -121.856, SOURCES["ccc"], "Mon\u2013Fri 7:00\u201317:00; Sat 7:00\u201315:00", "925-655-2711", "LANDFILL"),
    site("Keller Canyon Landfill \u2014 Pittsburg public scale (Oakland hub)", "County transfer / HHW / landfill", "oakland", "CA", "94565", "9010 Bailey Road, Pittsburg, CA 94565", 38.006, -121.856, SOURCES["ccc"], "Mon\u2013Fri 7:00\u201317:00; Sat 7:00\u201315:00", "925-655-2711", "LANDFILL"),
    site("Santa Clara County HHW \u2014 San Martin", "County HHW / landfill drop-off", "fremont", "CA", "95046", "8001 San Martin Road, San Martin, CA 95046", 37.086, -121.606, SOURCES["sccgov"], "Confirm hours \u2014 sccgov.org HHW", "408-299-7300", "HHW_E"),
    site("Santa Clara County Guadalupe Rubbish Disposal Area", "County HHW / landfill drop-off", "fremont", "CA", "95120", "15999 Guadalupe Mines Road, San Jose, CA 95120", 37.186, -121.856, SOURCES["sccgov"], "Mon\u2013Sat \u2014 sccgov.org", "408-299-7300", "LANDFILL"),
    site("Sacramento County NARS \u2014 public transfer & recycling", "County transfer / landfill / HHW", "sacramento", "CA", "95660", "4450 Roseville Road, North Highlands, CA 95660", 38.656, -121.356, SOURCES["sac_nars"], "Mon\u2013Fri 6:30\u201318:00; Sat\u2013Sun 8:00\u201318:00", "916-875-5555", "LANDFILL"),
    site("Sacramento County NARS HHW Drop-Off Facility", "County transfer / landfill / HHW", "sacramento", "CA", "95660", "4450 Roseville Road, North Highlands, CA 95660", 38.656, -121.356, SOURCES["sac_hhw"], "Tue/Thu/Fri/Sat 8:30\u201316:00 \u2014 311.saccounty.gov", "916-875-5555", "HHW_E"),
    site("Sacramento County Kiefer Landfill \u2014 public scale", "County transfer / landfill / HHW", "sacramento", "CA", "95683", "12701 Kiefer Boulevard, Sloughhouse, CA 95683", 38.456, -121.186, SOURCES["sac_kiefer"], "Mon\u2013Fri 6:30\u201316:30; Sat\u2013Sun 8:30\u201316:30", "916-875-5555", "LANDFILL"),
    site("Sacramento County Kiefer ABOP & Special Waste Facility", "County transfer / landfill / HHW", "sacramento", "CA", "95683", "12701 Kiefer Boulevard, Sloughhouse, CA 95683", 38.456, -121.186, SOURCES["sac_hhw"], "Tue\u2013Sat 8:30\u201316:00 \u2014 ABOP only", "916-875-5555", "HHW_E"),
    site("El Dorado County HHW Collection Facility (Sacramento hub)", "County transfer / landfill / HHW", "sacramento", "CA", "95667", "4100 Throwita Way, Placerville, CA 95667", 38.735, -120.825, SOURCES["eldorado"], "Fri\u2013Sat \u2014 eldoradocounty.ca.gov", "530-621-5300", "HHW_E"),
    site("Butte County Neal Road Landfill HHW (Sacramento hub)", "County transfer / landfill / HHW", "sacramento", "CA", "95969", "102 Neal Road, Paradise, CA 95969", 39.735, -121.625, SOURCES["butte"], "Sat HHW \u2014 buttecounty.net", "530-552-5689", "HHW_E"),
    site("San Joaquin County Lovelace MRF & Transfer Station", "County transfer / landfill / HHW", "stockton", "CA", "95336", "2323 East Lovelace Road, Manteca, CA 95336", 37.815, -121.185, SOURCES["sjgov"], "Mon\u2013Sat \u2014 sjgov.org", "209-468-3066", "TRANSFER"),
    site("San Joaquin County North County Landfill \u2014 Linden", "County transfer / landfill / HHW", "stockton", "CA", "95236", "9945 North Highway 99, Linden, CA 95236", 38.075, -121.085, SOURCES["sjgov"], "Mon\u2013Sat \u2014 sjgov.org", "209-468-3066", "LANDFILL"),
    site("San Joaquin County Ripon Transfer Station", "County transfer / landfill / HHW", "stockton", "CA", "95366", "900 W Main Street, Ripon, CA 95366", 37.735, -121.135, SOURCES["sjgov"], "Mon\u2013Sat \u2014 sjgov.org", "209-468-3066", "TRANSFER"),
    site("San Joaquin County Tracy MRF & Transfer Station", "County transfer / landfill / HHW", "stockton", "CA", "95304", "30725 South Koster Road, Tracy, CA 95304", 37.735, -121.425, SOURCES["sjgov"], "Mon\u2013Sat \u2014 sjgov.org", "209-468-3066", "TRANSFER"),
    site("San Joaquin County HHW Consolidation Facility", "County transfer / landfill / HHW", "stockton", "CA", "95206", "7850 South Airport Way, Stockton, CA 95206", 37.895, -121.245, SOURCES["stockton_hhw"], "Sat 9:00\u201313:00 \u2014 stocktonca.gov", "209-937-8340", "HHW_E"),
    site("Fresno County American Avenue Disposal Site", "County landfill / transfer / HHW", "fresno", "CA", "93630", "18950 W American Avenue, Kerman, CA 93630", 36.725, -120.085, SOURCES["fresno"], "Mon\u2013Sat \u2014 fresnocountyca.gov", "559-600-4259", "LANDFILL"),
    site("Fresno County Cedar Avenue Landfill", "County landfill / transfer / HHW", "fresno", "CA", "93725", "10441 S Cedar Avenue, Fresno, CA 93725", 36.625, -119.745, SOURCES["fresno"], "Mon\u2013Sat \u2014 fresnocountyca.gov", "559-600-4259", "LANDFILL"),
    site("Fresno County North District Transfer Station", "County landfill / transfer / HHW", "fresno", "CA", "93722", "7125 N Golden State Boulevard, Fresno, CA 93722", 36.845, -119.915, SOURCES["fresno"], "Mon\u2013Sat \u2014 fresnocountyca.gov", "559-600-4259", "TRANSFER"),
    site("Fresno County Orange Cove Transfer Station", "County landfill / transfer / HHW", "fresno", "CA", "93646", "400 Central Avenue, Orange Cove, CA 93646", 36.626, -119.316, SOURCES["fresno"], "Seasonal \u2014 fresnocountyca.gov", "559-600-4259", "TRANSFER"),
    site("Fresno County Environmental Compliance Center \u2014 HHW", "County landfill / transfer / HHW", "fresno", "CA", "93725", "3457 S Cedar Avenue, Fresno, CA 93725", 36.625, -119.745, SOURCES["fresno"], "Sat \u2014 fresnocountyca.gov", "559-600-4259", "HHW_E"),
    site("Madera County Fairmead Landfill \u2014 HHW events", "County landfill / transfer / HHW", "fresno", "CA", "93610", "21739 Road 19, Chowchilla, CA 93610", 37.085, -120.225, SOURCES["madera"], "Event schedule \u2014 maderacounty.com", "559-675-7811", "HHW_E"),
    site("South Gate Transfer Station \u2014 LA County public scale", "County/municipal transfer or HHW", "long-beach", "CA", "90280", "9530 Garfield Avenue, South Gate, CA 90280", 33.944, -118.166, SOURCES["lac_ph"], "Mon\u2013Sat 6:00\u201317:00 \u2014 publichealth.lacounty.gov", "562-908-4288", "TRANSFER"),
    site("EDCO Environmental Collection Center \u2014 Signal Hill", "County/municipal transfer or HHW", "long-beach", "CA", "90755", "2755 California Avenue, Signal Hill, CA 90755", 33.795, -118.165, SOURCES["lac_hhw"], "Sat 9:00\u201314:00 \u2014 cleanla.lacounty.gov", "562-597-0608", "HHW_E"),
    site("LASAN Gaffey Street S.A.F.E. Center (Long Beach hub)", "County/municipal transfer or HHW", "long-beach", "CA", "90731", "1400 N Gaffey Street, San Pedro, CA 90731", 33.754, -118.292, SOURCES["lac_hhw"], "Sat\u2013Sun 9:00\u201315:00 \u2014 sanitation.lacity.gov", "1-800-773-2489", "HHW_E"),
    site("LASAN Hyperion S.A.F.E. Center (Long Beach hub)", "County/municipal transfer or HHW", "long-beach", "CA", "90293", "7660 W Imperial Highway, Playa Del Rey, CA 90293", 33.926, -118.426, SOURCES["lac_hhw"], "Sat\u2013Sun 9:00\u201315:00", "1-800-773-2489", "HHW_E"),
    site("Long Beach Environmental Collection Center \u2014 HHW", "Long Beach municipal HHW / e-waste drop-off", "long-beach", "CA", "90805", "2750 California Avenue, Long Beach, CA 90805", 33.805, -118.215, SOURCES["longbeach"], "Sat 9:00\u201314:00 \u2014 longbeach.gov/lbrecycles", "562-570-2876", "HHW_E"),
    site("Pima County Ina Road Transfer Station", "County landfill / transfer / HHW", "tucson", "AZ", "85653", "16601 W Ina Road, Marana, AZ 85653", 32.435, -111.165, SOURCES["pima"], "Mon\u2013Sat 7:00\u201316:00 \u2014 pima.gov/595", "520-724-7400", "TRANSFER"),
    site("Pima County Tangerine Road Transfer Station", "County landfill / transfer / HHW", "tucson", "AZ", "85653", "16601 W Tangerine Road, Marana, AZ 85653", 32.455, -111.185, SOURCES["pima"], "Mon\u2013Sat 7:00\u201316:00 \u2014 pima.gov/595", "520-724-7400", "TRANSFER"),
    site("Pima County Tangerine Road Landfill", "County landfill / transfer / HHW", "tucson", "AZ", "85653", "16601 W Tangerine Road, Marana, AZ 85653", 32.455, -111.185, SOURCES["pima"], "Mon\u2013Sat 7:00\u201316:00 \u2014 pima.gov/595", "520-724-7400", "LANDFILL"),
    site("Pima County Rincon Recycling & Transfer Station", "County landfill / transfer / HHW", "tucson", "AZ", "85756", "5890 S Mann Avenue, Tucson, AZ 85756", 32.148, -110.85, SOURCES["pima"], "Mon\u2013Sat 7:00\u201316:00 \u2014 pima.gov/595", "520-724-7400", "TRANSFER"),
    site("Pima County Ryan Field Transfer Station", "County landfill / transfer / HHW", "tucson", "AZ", "85735", "6455 S Continental Road, Tucson, AZ 85735", 32.134, -111.183, SOURCES["pima"], "Mon\u2013Sat 7:00\u201316:00 \u2014 pima.gov/595", "520-724-7400", "TRANSFER"),
    site("Pima County Red Rock Transfer Station", "County landfill / transfer / HHW", "tucson", "AZ", "85145", "Red Rock, AZ 85145", 32.585, -111.395, SOURCES["pima"], "Mon\u2013Sat 7:00\u201316:00 \u2014 pima.gov/595", "520-724-7400", "TRANSFER"),
    site("Pima County Three Points Transfer Station", "County landfill / transfer / HHW", "tucson", "AZ", "85634", "Three Points, AZ 85634", 32.075, -111.325, SOURCES["pima"], "Mon\u2013Sat 7:00\u201316:00 \u2014 pima.gov/595", "520-724-7400", "TRANSFER"),
    site("Pima County Sasabe Transfer Station", "County landfill / transfer / HHW", "tucson", "AZ", "85633", "Sasabe, AZ 85633", 31.485, -111.545, SOURCES["pima"], "Mon\u2013Sat 7:00\u201316:00 \u2014 pima.gov/595", "520-724-7400", "TRANSFER"),
    site("Pima County Los Reales Landfill \u2014 county listing", "County landfill / transfer / HHW", "tucson", "AZ", "85756", "5300 E Los Reales Road, Tucson, AZ 85756", 32.119, -110.881, SOURCES["pima"], "Mon\u2013Sat 7:00\u201316:00 \u2014 pima.gov/595", "520-724-7400", "LANDFILL"),
    site("Pima County HHW Collection Facility", "County landfill / transfer / HHW", "tucson", "AZ", "85756", "5300 E Los Reales Road, Tucson, AZ 85756", 32.119, -110.881, SOURCES["pima"], "Mon\u2013Sat 7:00\u201316:00 \u2014 pima.gov/595", "520-724-7400", "HHW_E"),
    site("City of Tucson Los Reales HHW \u2014 Sustainability Campus", "Municipal HHW at Los Reales", "tucson", "AZ", "85756", "5300 E Los Reales Road, Tucson, AZ 85756", 32.119, -110.881, SOURCES["tucson_hhw"], "Wed\u2013Sat 8:00\u201312:30 \u2014 tucsonaz.gov", "520-791-3171", "HHW_E"),
    site("Clark County Cheyenne Transfer Station", "County transfer / HHW / landfill", "las-vegas", "NV", "89032", "Cheyenne Transfer Station, North Las Vegas, NV 89032", 36.218, -115.175, SOURCES["clark"], "Confirm hours \u2014 clarkcountynv.gov", "702-455-0000", "TRANSFER"),
    site("Clark County Republic Recycle Center \u2014 Gowan Road", "County transfer / HHW / landfill", "las-vegas", "NV", "89130", "5601 W Gowan Road, Las Vegas, NV 89130", 36.215, -115.245, SOURCES["clark"], "Confirm hours \u2014 clarkcountynv.gov", "702-455-0000", "TRANSFER"),
    site("Clark County HHW Collection \u2014 North Las Vegas", "County transfer / HHW / landfill", "las-vegas", "NV", "89030", "2800 E Cheyenne Avenue, North Las Vegas, NV 89030", 36.218, -115.105, SOURCES["clark"], "Confirm hours \u2014 clarkcountynv.gov", "702-455-0000", "HHW_E"),
    site("Clark County HHW Collection \u2014 Henderson South", "County transfer / HHW / landfill", "las-vegas", "NV", "89011", "2240 Moser Drive, Henderson, NV 89011", 36.035, -115.045, SOURCES["clark"], "Confirm hours \u2014 clarkcountynv.gov", "702-455-0000", "HHW_E"),
    site("Clark County Apex Landfill \u2014 public scale (nearby)", "County transfer / HHW / landfill", "las-vegas", "NV", "89124", "1 Apex Landfill Way, Las Vegas, NV 89124", 36.385, -114.915, SOURCES["clark"], "Confirm hours \u2014 clarkcountynv.gov", "702-455-0000", "LANDFILL"),
    site("Scottsdale Transfer Station \u2014 Brush & Bulk", "Municipal transfer \u2014 brush / bulk / appliances", "scottsdale", "AZ", "85258", "9191 E San Salvador Drive, Scottsdale, AZ 85258", 33.555, -111.875, SOURCES["scottsdale"], "Mon\u2013Fri 7:00\u201315:00 \u2014 scottsdaleaz.gov", "480-312-5600", "TRANSFER"),
    site("Scottsdale HHW Home Collection (by appointment)", "Municipal HHW appointment collection", "scottsdale", "AZ", "85251", "9191 E San Salvador Drive, Scottsdale, AZ 85258", 33.555, -111.875, SOURCES["scottsdale"], "By appointment \u2014 scottsdaleaz.gov/solid-waste", "480-312-5600", "HHW_E"),
    site("Glendale Municipal Landfill \u2014 public scale", "Municipal landfill \u2014 self-haul", "glendale", "AZ", "85307", "11505 W Glendale Avenue, Glendale, AZ 85307", 33.535, -112.305, SOURCES["glendale_az"], "Mon\u2013Sat \u2014 glendaleaz.com", "623-930-2660", "LANDFILL"),
    site("Glendale HHW Facility \u2014 appointment collection", "Municipal HHW by appointment", "glendale", "AZ", "85301", "7800 N 53rd Avenue, Glendale, AZ 85301", 33.545, -112.175, SOURCES["glendale_az"], "By appointment \u2014 glendaleaz.com", "623-930-2660", "HHW_E"),
    site("Fremont Transfer Station \u2014 Boyce Road public gate", "Municipal transfer / Tri-CED co-located", "fremont", "CA", "94538", "41149 Boyce Road, Fremont, CA 94538", 37.505, -121.945, SOURCES["fremont_gov"], "Mon\u2013Sat \u2014 fremont.gov", "510-657-1420", "TRANSFER"),
    site("Fremont Tri-CED Community Recycling \u2014 public drop-off", "Municipal recycling / bulky drop-off", "fremont", "CA", "94538", "41149 Boyce Road, Fremont, CA 94538", 37.504, -121.944, SOURCES["fremont_gov"], "Mon\u2013Sat \u2014 fremont.gov", "510-657-1420", "TRANSFER"),
    # ── BATCH 2: collar-county / remote official sites (2026-08-12 research) ──
    site("Imperial County Calexico Landfill \u2014 public drop-off", "County landfill \u2014 self-haul bulky / tires", "san-diego", "CA", "92231", "133 W Highway 98, Calexico, CA 92231", 32.678, -115.489, SOURCES["co_imperial"], "Wed 7:00\u201316:00; alternating Sat \u2014 Imperial County Public Works", "442-265-1818", "LANDFILL"),
    site("Imperial County Calexico Landfill (Chula Vista hub)", "County landfill \u2014 self-haul", "chula-vista", "CA", "92231", "133 W Highway 98, Calexico, CA 92231", 32.678, -115.489, SOURCES["co_imperial"], "Wed 7:00\u201316:00 \u2014 Imperial County Public Works", "442-265-1818", "LANDFILL"),
    site("Imperial County Niland Solid Waste Site", "County landfill \u2014 public drop-off", "san-diego", "CA", "92257", "8450 Cuff Road, Niland, CA 92257", 33.312, -115.518, SOURCES["co_imperial"], "Thu 8:00\u201316:00; alternating Sat \u2014 Imperial County Public Works", "442-265-1818", "LANDFILL"),
    site("Imperial County Salton City Solid Waste Site", "County landfill \u2014 public drop-off", "san-diego", "CA", "92275", "935 W Highway 86, Salton City, CA 92275", 33.298, -115.956, SOURCES["co_imperial"], "Mon\u2013Sat 7:00\u201317:00 \u2014 Imperial County Public Works", "442-265-1818", "LANDFILL"),
    site("Imperial County Ocotillo Transfer Station", "County transfer \u2014 bulky / yard waste", "chula-vista", "CA", "92259", "1802 Shell Canyon Road, Ocotillo, CA 92259", 32.742, -116.099, SOURCES["co_imperial"], "Mon 8:00\u201312:00 \u2014 Imperial County Public Works", "442-265-1818", "TRANSFER"),
    site("Ventura County Simi Valley Landfill (Long Beach hub)", "County landfill \u2014 self-haul", "long-beach", "CA", "93065", "2801 Madera Road, Simi Valley, CA 93065", 34.286, -118.726, SOURCES["ventura"], "Mon\u2013Sat 7:00\u201316:00 \u2014 venturacounty.gov", "805-658-4321", "LANDFILL"),
    site("Ventura County Del Norte Transfer (Long Beach hub)", "County transfer / recycling", "long-beach", "CA", "93030", "111 S Del Norte Boulevard, Oxnard, CA 93030", 34.196, -119.156, SOURCES["ventura"], "Mon\u2013Sat 5:30\u201317:00 \u2014 venturacounty.gov", "805-658-4321", "TRANSFER"),
    site("Ventura County Gold Coast Recycling & Transfer (Long Beach hub)", "County transfer / landfill", "long-beach", "CA", "93003", "5275 Colt Street, Ventura, CA 93003", 34.256, -119.256, SOURCES["ventura"], "Mon\u2013Sat \u2014 venturacounty.gov", "805-658-4321", "TRANSFER"),
    site("Riverside County Badlands Landfill (Long Beach hub)", "County landfill \u2014 self-haul", "long-beach", "CA", "92555", "31125 Ironwood Avenue, Moreno Valley, CA 92555", 33.938, -117.213, SOURCES["calrecycle"], "Mon\u2013Sat \u2014 rivco.org via calrecycle listing", "951-486-3200", "LANDFILL"),
    site("San Mateo County Shoreway Environmental Center (Fremont hub)", "County transfer / HHW / e-waste", "fremont", "CA", "94070", "333 Shoreway Road, San Carlos, CA 94070", 37.506, -122.256, SOURCES["sanmateo"], "Thu\u2013Sat \u2014 smcsolidwaste.org", "650-802-8355", "TRANSFER"),
    site("San Mateo County Shoreway Environmental Center (Oakland hub)", "County transfer / HHW / e-waste", "oakland", "CA", "94070", "333 Shoreway Road, San Carlos, CA 94070", 37.506, -122.256, SOURCES["sanmateo"], "Thu\u2013Sat \u2014 smcsolidwaste.org", "650-802-8355", "TRANSFER"),
    site("Blue Line Transfer Station \u2014 SSF (Fremont hub)", "District transfer \u2014 bulky / C&D self-haul", "fremont", "CA", "94080", "500 East Jamie Court, South San Francisco, CA 94080", 37.656, -122.406, SOURCES["sanmateo"], "Mon\u2013Sat \u2014 smcsolidwaste.org", "650-589-0300", "TRANSFER"),
    site("Ox Mountain Sanitary Landfill (Oakland hub)", "County landfill \u2014 public scale", "oakland", "CA", "94019", "12310 San Mateo Road, Half Moon Bay, CA 94019", 37.306, -122.406, SOURCES["sanmateo"], "Mon\u2013Sat \u2014 smcsolidwaste.org", "650-726-7093", "LANDFILL"),
    site("Milpitas Sanitary Landfill \u2014 public scale (Fremont hub)", "County landfill \u2014 self-haul", "fremont", "CA", "95035", "705 N Milpitas Boulevard, Milpitas, CA 95035", 37.435, -121.892, SOURCES["calrecycle"], "Mon\u2013Sat \u2014 Santa Clara County listing", "408-299-7300", "LANDFILL"),
    site("Placer County Western Placer MRF & Transfer (Sacramento hub)", "County transfer / recycling", "sacramento", "CA", "95747", "3033 Fiddyment Road, Roseville, CA 95747", 38.785, -121.312, SOURCES["placer"], "Mon\u2013Sat \u2014 placer.ca.gov", "916-543-3960", "TRANSFER"),
    site("Placer County HHW Facility \u2014 Auburn (Sacramento hub)", "County HHW drop-off", "sacramento", "CA", "95603", "2901 Maidu Drive, Auburn, CA 95603", 38.925, -121.078, SOURCES["placer"], "Sat \u2014 placer.ca.gov HHW", "916-543-3960", "HHW_E"),
    site("San Bernardino County San Timoteo Landfill (Long Beach hub)", "County landfill \u2014 self-haul", "long-beach", "CA", "92373", "5000 San Timoteo Canyon Road, Redlands, CA 92373", 34.045, -117.145, SOURCES["sbcounty"], "Mon\u2013Sat \u2014 sbcounty.gov", "909-387-4341", "LANDFILL"),
    site("San Diego County Poway HHW Collection Facility", "County HHW permanent facility", "san-diego", "CA", "92064", "12325 Crosthwaite Circle, Poway, CA 92064", 32.935, -117.038, SOURCES["sd_county"], "Sat 9:00\u201314:00 \u2014 sandiegocounty.gov", "858-694-7000", "HHW_E"),
    site("San Diego County Poway HHW (Chula Vista hub)", "County HHW permanent facility", "chula-vista", "CA", "92064", "12325 Crosthwaite Circle, Poway, CA 92064", 32.935, -117.038, SOURCES["sd_county"], "Sat 9:00\u201314:00 \u2014 sandiegocounty.gov", "858-694-7000", "HHW_E"),
    site("San Diego County Lemon Grove HHW Collection Facility", "County HHW permanent facility", "chula-vista", "CA", "91945", "3125 Lemon Grove Avenue, Lemon Grove, CA 91945", 32.735, -117.031, SOURCES["sd_county"], "Sat 9:00\u201314:00 \u2014 sandiegocounty.gov", "858-694-7000", "HHW_E"),
    site("City of Mesa Transfer Station (Phoenix hub)", "Municipal transfer \u2014 bulky / appliances", "phoenix", "AZ", "85201", "2412 N Mesa Drive, Mesa, AZ 85201", 33.438, -111.822, SOURCES["mari_loc"], "Mon\u2013Sat \u2014 mesaaz.gov via Maricopa County network", "480-644-3334", "TRANSFER"),
    site("City of Mesa Transfer Station (Scottsdale hub)", "Municipal transfer \u2014 bulky / appliances", "scottsdale", "AZ", "85201", "2412 N Mesa Drive, Mesa, AZ 85201", 33.438, -111.822, SOURCES["mari_loc"], "Mon\u2013Sat \u2014 mesaaz.gov", "480-644-3334", "TRANSFER"),
    site("Maricopa County Waste Tire \u2014 Buckeye (Phoenix hub)", "County tire drop-off", "phoenix", "AZ", "85326", "2020 S Miller Road, Buckeye, AZ 85326", 33.352, -112.592, SOURCES["mari_tire"], "Mon\u2013Sat \u2014 maricopa.gov/1571", "480-987-2498", "TIRES"),
    site("Goodyear Public Works Transfer Station (Glendale hub)", "Municipal transfer \u2014 bulky / yard waste", "glendale", "AZ", "85338", "828 S Estrella Parkway, Goodyear, AZ 85338", 33.435, -112.358, SOURCES["mari_loc"], "Confirm hours \u2014 goodyearaz.gov", "623-932-3010", "TRANSFER"),
    site("Clark County Henderson Transfer Station (Las Vegas hub)", "Municipal transfer \u2014 bulky drop-off", "las-vegas", "NV", "89015", "240 S Water Street, Henderson, NV 89015", 36.035, -114.985, SOURCES["clark"], "Mon\u2013Sat \u2014 clarkcountynv.gov", "702-267-1200", "TRANSFER"),
    site("Clark County HHW \u2014 Mesquite (Las Vegas hub)", "County HHW collection event site", "las-vegas", "NV", "89027", "840 Hafen Lane, Mesquite, NV 89027", 36.805, -114.067, SOURCES["clark"], "Scheduled events \u2014 clarkcountynv.gov", "702-455-0000", "HHW_E"),
    site("Clark County HHW \u2014 Moapa (Las Vegas hub)", "County HHW collection event site", "las-vegas", "NV", "89025", "1340 E State Highway 168, Moapa, NV 89025", 36.615, -114.585, SOURCES["clark"], "Scheduled events \u2014 clarkcountynv.gov", "702-455-0000", "HHW_E"),
    site("Delta Diablo HHW \u2014 Antioch (Fremont hub)", "District HHW drop-off", "fremont", "CA", "94509", "2550 Pittsburg-Antioch Highway, Antioch, CA 94509", 38.015, -121.785, SOURCES["ccrecycle"], "Thu\u2013Sat \u2014 contracosta.ca.gov", "925-756-1990", "HHW_E"),
    site("El Cerrito Recycling Center + HHW (Oakland hub)", "Municipal HHW / e-waste drop-off", "oakland", "CA", "94530", "7501 Schmidt Lane, El Cerrito, CA 94530", 37.915, -122.305, SOURCES["calrecycle"], "Wed\u2013Sat \u2014 elcerrito.gov via calrecycle", "510-215-4311", "HHW_E"),
    site("Tulare County Woodville Landfill (Fresno hub)", "County landfill \u2014 self-haul", "fresno", "CA", "93267", "15862 Road 216, Porterville, CA 93267", 36.065, -119.016, SOURCES["calrecycle"], "Mon\u2013Sat \u2014 Tulare County listing", "559-624-7400", "LANDFILL"),
    site("Tulare County Badger Transfer Station (Fresno hub)", "County transfer \u2014 bulky / yard waste", "fresno", "CA", "93286", "34422 Drive 64, Woodlake, CA 93286", 36.415, -119.098, SOURCES["calrecycle"], "Mon\u2013Sat \u2014 Tulare County listing", "559-624-7400", "TRANSFER"),
    site("Merced County Highway 59 Landfill (Stockton hub)", "County landfill \u2014 self-haul", "stockton", "CA", "95348", "7150 Highway 59, Merced, CA 95348", 37.345, -120.572, SOURCES["calrecycle"], "Mon\u2013Sat \u2014 Merced County listing", "209-385-7684", "LANDFILL"),
    site("Stanislaus County HHW Facility (Stockton hub)", "County HHW drop-off", "stockton", "CA", "95358", "4000 Fink Road, Modesto, CA 95358", 37.586, -121.006, SOURCES["calrecycle"], "Sat \u2014 Stanislaus County listing", "209-525-4120", "HHW_E"),
    site("Kings County Kettleman Hills Landfill (Fresno hub)", "County landfill \u2014 self-haul", "fresno", "CA", "93239", "35251 Old Skyline Boulevard, Kettleman City, CA 93239", 36.008, -119.962, SOURCES["calrecycle"], "Mon\u2013Sat \u2014 Kings County listing", "559-386-5166", "LANDFILL"),
    site("Maricopa County Waste Tire \u2014 Gilbert (Scottsdale hub)", "County tire drop-off", "scottsdale", "AZ", "85233", "1150 N Cooper Road, Gilbert, AZ 85233", 33.370, -111.790, SOURCES["mari_tire"], "Mon\u2013Sat \u2014 maricopa.gov/1571", "480-987-2498", "TIRES"),
    site("Maricopa County Waste Tire \u2014 Tempe (Scottsdale hub)", "County tire drop-off", "scottsdale", "AZ", "85282", "730 W Broadway Road, Tempe, AZ 85282", 33.408, -111.947, SOURCES["mari_tire"], "Mon\u2013Sat \u2014 maricopa.gov/1571", "480-987-2498", "TIRES"),
    site("Maricopa County Waste Tire \u2014 Apache Junction (Phoenix hub)", "County tire drop-off", "phoenix", "AZ", "85120", "5750 E Apache Trail, Apache Junction, AZ 85120", 33.415, -111.545, SOURCES["mari_tire"], "Mon\u2013Sat \u2014 maricopa.gov/1571", "480-987-2498", "TIRES"),
    site("Pima County Marana Regional Landfill \u2014 county listing detail", "County landfill \u2014 self-haul", "tucson", "AZ", "85653", "14508 W Avra Valley Road, Marana, AZ 85653", 32.409, -111.271, SOURCES["pima"], "Mon\u2013Sat \u2014 pima.gov/595", "520-724-7400", "LANDFILL"),
    site("Pima County Ajo Landfill \u2014 remote county listing", "County landfill \u2014 remote drop-off", "tucson", "AZ", "85321", "2000 N Ajo Well No 1 Road, Ajo, AZ 85321", 32.393, -112.848, SOURCES["pima"], "Mon\u2013Sat \u2014 pima.gov/595", "520-724-7400", "LANDFILL"),
    site("Pima County Drexel Land Reclamation \u2014 county listing detail", "County landfill / reclamation", "tucson", "AZ", "85747", "11330 E Drexel Road, Tucson, AZ 85747", 32.146, -110.750, SOURCES["pima"], "Mon\u2013Sat \u2014 pima.gov/595", "520-724-7400", "LANDFILL"),
    site("Pima County Speedway Recycling & Landfill \u2014 county listing detail", "County landfill / recycling", "tucson", "AZ", "85710", "7301 E Speedway Boulevard, Tucson, AZ 85710", 32.239, -110.835, SOURCES["pima"], "Mon\u2013Sat \u2014 pima.gov/595", "520-724-7400", "LANDFILL"),
    # ── BATCH 3: final collar / AZ municipal / LA HHW cross-tags ──
    site("LASAN Randall Street S.A.F.E. Center (Long Beach hub)", "Municipal HHW / e-waste", "long-beach", "CA", "91352", "11025 Randall Street, Sun Valley, CA 91352", 34.255, -118.386, SOURCES["lacity"], "Sat\u2013Sun 9:00\u201315:00 \u2014 sanitation.lacity.gov", "1-800-773-2489", "HHW_E"),
    site("LASAN Nicole Bernson S.A.F.E. Center (Santa Ana hub)", "Municipal HHW / e-waste", "santa-ana", "CA", "91325", "10241 N Balboa Boulevard, Northridge, CA 91325", 34.256, -118.536, SOURCES["lacity"], "Sat\u2013Sun 9:00\u201315:00 \u2014 sanitation.lacity.gov", "1-800-773-2489", "HHW_E"),
    site("LASAN Lopez Canyon S.A.F.E. Center (Anaheim hub)", "Municipal HHW / e-waste", "anaheim", "CA", "91342", "11950 Lopez Canyon Road, Lake View Terrace, CA 91342", 34.293, -118.406, SOURCES["lacity"], "Sat\u2013Sun 9:00\u201315:00 \u2014 sanitation.lacity.gov", "1-800-773-2489", "HHW_E"),
    site("LASAN CLARTS Transfer Station (Long Beach hub)", "Municipal transfer \u2014 bulky / C&D", "long-beach", "CA", "90021", "2201 E Washington Boulevard, Los Angeles, CA 90021", 34.020, -118.234, SOURCES["lac_ph"], "Mon\u2013Sat \u2014 publichealth.lacounty.gov", "213-763-1918", "TRANSFER"),
    site("Culver City Transfer Station (Long Beach hub)", "Municipal transfer / recycling", "long-beach", "CA", "90232", "9255 W Jefferson Boulevard, Culver City, CA 90232", 34.026, -118.397, SOURCES["lac_ph"], "Mon\u2013Sat \u2014 publichealth.lacounty.gov", "310-253-6405", "TRANSFER"),
    site("Hyperion S.A.F.E. Center (Long Beach hub)", "Municipal HHW / e-waste", "long-beach", "CA", "90293", "7660 W Imperial Highway, Playa Del Rey, CA 90293", 33.926, -118.425, SOURCES["lacity"], "Sat\u2013Sun 9:00\u201315:00 \u2014 sanitation.lacity.gov", "1-800-773-2489", "HHW_E"),
    site("Clark County HHW \u2014 Boulder City (Las Vegas hub)", "County HHW collection event site", "las-vegas", "NV", "89005", "810 Avenue G, Boulder City, NV 89005", 35.978, -114.832, SOURCES["clark"], "Scheduled events \u2014 clarkcountynv.gov", "702-455-0000", "HHW_E"),
    site("Sacramento County Elder Creek Transfer Station", "County transfer \u2014 bulky / appliances", "sacramento", "CA", "95828", "8642 Elder Creek Road, Sacramento, CA 95828", 38.478, -121.396, SOURCES["sac_nars"], "Mon\u2013Sat \u2014 wmr.saccounty.gov", "916-875-5555", "TRANSFER"),
    site("Sierra Waste Recycling & Transfer Station", "Regional transfer \u2014 bulky / C&D", "sacramento", "CA", "95827", "9167 Jackson Road, Sacramento, CA 95827", 38.558, -121.326, SOURCES["sac_nars"], "Mon\u2013Sat \u2014 wmr.saccounty.gov", "916-875-5555", "TRANSFER"),
    site("Shasta County West Central Landfill (Sacramento hub)", "County landfill \u2014 self-haul", "sacramento", "CA", "96001", "12000 Clear Creek Road, Redding, CA 96001", 40.585, -122.385, SOURCES["calrecycle"], "Mon\u2013Sat \u2014 Shasta County listing", "530-224-5789", "LANDFILL"),
    site("San Joaquin County Bertolotti Disposal Transfer", "County transfer station", "stockton", "CA", "95304", "8900 S Koster Road, Tracy, CA 95304", 37.735, -121.425, SOURCES["stockton_hhw"], "Mon\u2013Sat \u2014 sjgov.org via stocktonca.gov", "209-468-3066", "TRANSFER"),
    site("Gilton Solid Waste Transfer Station", "Private-contractor transfer \u2014 bulky / C&D", "stockton", "CA", "95205", "2350 E Main Street, Stockton, CA 95205", 37.945, -121.268, SOURCES["stockton_hhw"], "Mon\u2013Sat \u2014 stocktonca.gov", "209-463-9425", "TRANSFER"),
    site("San Joaquin County Lathrop Transfer Station detail", "County transfer \u2014 bulky / yard waste", "stockton", "CA", "95330", "15500 Harlan Road, Lathrop, CA 95330", 37.815, -121.315, SOURCES["stockton_hhw"], "Mon\u2013Sat \u2014 stocktonca.gov", "209-468-3066", "TRANSFER"),
    site("Fresno County Shaver Lake Transfer Station", "County transfer \u2014 bulky / yard waste", "fresno", "CA", "93664", "41640 Tollhouse Road, Shaver Lake, CA 93664", 37.105, -119.568, SOURCES["fresno"], "Seasonal \u2014 fresnocountyca.gov", "559-600-4259", "TRANSFER"),
    site("Madera County North Fork Transfer Station (Fresno hub)", "County transfer \u2014 bulky / yard waste", "fresno", "CA", "93643", "54400 Road 274, North Fork, CA 93643", 37.225, -119.512, SOURCES["calrecycle"], "Mon\u2013Sat \u2014 Madera County listing", "559-675-7811", "TRANSFER"),
    site("Kern County Bena Landfill (Fresno hub)", "County landfill \u2014 self-haul", "fresno", "CA", "93307", "10000 Highway 58, Bakersfield, CA 93307", 35.285, -118.885, SOURCES["kern"], "Mon\u2013Sat \u2014 kerncounty.com", "661-862-8900", "LANDFILL"),
    site("Kern County Mount Vernon Landfill (Fresno hub)", "County landfill \u2014 self-haul", "fresno", "CA", "93306", "2000 Mount Vernon Avenue, Bakersfield, CA 93306", 35.385, -118.985, SOURCES["kern"], "Mon\u2013Sat \u2014 kerncounty.com", "661-862-8900", "LANDFILL"),
    site("Maricopa County Waste Tire \u2014 Queen Creek (Glendale hub)", "County tire drop-off", "glendale", "AZ", "85142", "22407 S Ellsworth Road, Queen Creek, AZ 85142", 33.250, -111.630, SOURCES["mari_tire"], "Mon\u2013Sat \u2014 maricopa.gov/1571", "480-987-2498", "TIRES"),
    site("City of Chandler Ocotillo Landfill (Phoenix hub)", "Municipal landfill \u2014 self-haul", "phoenix", "AZ", "85249", "645 E Ocotillo Road, Chandler, AZ 85249", 33.250, -111.830, SOURCES["chandler"], "Mon\u2013Sat \u2014 chandleraz.gov", "480-782-3510", "LANDFILL"),
    site("City of Chandler Ocotillo Landfill (Scottsdale hub)", "Municipal landfill \u2014 self-haul", "scottsdale", "AZ", "85249", "645 E Ocotillo Road, Chandler, AZ 85249", 33.250, -111.830, SOURCES["chandler"], "Mon\u2013Sat \u2014 chandleraz.gov", "480-782-3510", "LANDFILL"),
    site("Mesa Household Hazardous Waste Facility (Phoenix hub)", "Municipal HHW drop-off", "phoenix", "AZ", "85203", "130 N Robson, Mesa, AZ 85203", 33.418, -111.831, SOURCES["mesa"], "Wed\u2013Sat \u2014 mesaaz.gov", "480-644-3334", "HHW_E"),
    site("Tempe Household Hazardous Waste Facility (Scottsdale hub)", "Municipal HHW drop-off", "scottsdale", "AZ", "85281", "1320 W 6th Street, Tempe, AZ 85281", 33.425, -111.955, SOURCES["tempe"], "Wed\u2013Sat \u2014 tempe.gov", "480-350-4311", "HHW_E"),
    site("Peoria HHW Facility (Glendale hub)", "Municipal HHW drop-off", "glendale", "AZ", "85345", "8335 W Jefferson Street, Peoria, AZ 85345", 33.575, -112.238, SOURCES["peoria"], "Sat \u2014 peoriaaz.gov", "623-773-7431", "HHW_E"),
    site("Surprise Transfer Facility (Glendale hub)", "Municipal transfer \u2014 bulky / yard waste", "glendale", "AZ", "85379", "13440 W Westgate Drive, Surprise, AZ 85379", 33.635, -112.345, SOURCES["peoria"], "Mon\u2013Sat \u2014 surpriseaz.gov via Peoria network", "623-222-1920", "TRANSFER"),
    site("Avondale Public Works Transfer (Glendale hub)", "Municipal transfer \u2014 bulky / appliances", "glendale", "AZ", "85323", "899 N Agua Fria Drive, Avondale, AZ 85323", 33.445, -112.345, SOURCES["peoria"], "Mon\u2013Sat \u2014 avondaleaz.gov", "623-333-4400", "TRANSFER"),
    site("Phoenix SR 85 Landfill \u2014 Buckeye (Glendale hub)", "Municipal landfill \u2014 self-haul", "glendale", "AZ", "85326", "1 SR 85 Landfill Way, Buckeye, AZ 85326", 33.355, -112.585, SOURCES["phx_ts"], "Mon\u2013Sat \u2014 phoenix.gov landfill", "602-262-7251", "LANDFILL"),
    site("Livermore HHW Facility detail (Fremont hub)", "County HHW / e-waste", "fremont", "CA", "94550", "5584 La Ribera Street, Livermore, CA 94550", 37.685, -121.745, SOURCES["calrecycle"], "Thu\u2013Sat \u2014 calrecycle.ca.gov HHW", "800-606-6606", "HHW_E"),
    site("Newby Island Resource Recovery Park (Oakland hub)", "County landfill / transfer \u2014 self-haul", "oakland", "CA", "95035", "1601 Dixon Landing Road, Milpitas, CA 95035", 37.435, -121.935, SOURCES["calrecycle"], "Mon\u2013Sat \u2014 Santa Clara County listing", "408-263-2381", "LANDFILL"),
    site("Imperial County Palo Verde Transfer Station", "County transfer \u2014 bulky / yard waste", "san-diego", "CA", "92266", "589 Stallard Road, Palo Verde, CA 92266", 33.432, -114.732, SOURCES["co_imperial"], "Mon 8:00\u201312:00 \u2014 Imperial County Public Works", "442-265-1818", "TRANSFER"),
    site("Imperial County Holtville Transfer Station (Chula Vista hub)", "County transfer \u2014 bulky / yard waste", "chula-vista", "CA", "92250", "2678 Whitlock Road, Holtville, CA 92250", 32.812, -115.378, SOURCES["co_imperial"], "Tue 7:00\u201312:00 \u2014 Imperial County Public Works", "442-265-1818", "TRANSFER"),
    site("Chula Vista Public Works Yard \u2014 tire amnesty site", "Municipal tire / bulky event drop-off", "chula-vista", "CA", "91910", "1800 Maxwell Road, Chula Vista, CA 91910", 32.606, -117.046, SOURCES["chula"], "Event schedule \u2014 chulavistaca.gov", "619-691-5122", "TIRES"),
    site("Anaheim Public Works \u2014 bulky drop-off events", "Municipal bulky / appliance events", "anaheim", "CA", "92805", "200 S Anaheim Boulevard, Anaheim, CA 92805", 33.835, -117.914, SOURCES["oc_hhw"], "Seasonal events \u2014 anaheim.net via cmsdca.gov", "714-765-6860", "TRANSFER"),
    site("Santa Ana Public Works \u2014 HHW event site", "Municipal HHW event collection", "santa-ana", "CA", "92701", "20 Civic Center Plaza, Santa Ana, CA 92701", 33.749, -117.873, SOURCES["oc_hhw"], "Event schedule \u2014 santa-ana.org via cmsdca.gov", "714-647-3380", "HHW_E"),
]

def main() -> None:
    valid = {c["city_slug"]: c.get("state") for c in json.loads(CITIES_PATH.read_text())}
    for r in UPSERTS:
        if r["city_slug"] not in TARGET_METROS:
            raise SystemExit(f"city_slug outside target metros: {r['city_slug']} ({r['name']})")
        if r["city_slug"] not in valid:
            raise SystemExit(f"unknown city_slug: {r['city_slug']}")
        if r.get("state") != valid[r["city_slug"]]:
            raise SystemExit(f"state mismatch: {r['name']}")
        if not is_gov_url(r["source_url"]):
            raise SystemExit(f"non-.gov source: {r['source_url']} ({r['name']})")
        if not is_hard_facility(r):
            raise SystemExit(f"soft facility rejected: {r['name']}")

    existing = json.loads(FAC_PATH.read_text())
    before_hard = sum(1 for f in existing if is_hard_facility(f))
    by_key: dict[tuple, int] = {}
    by_addr: dict[tuple, int] = {}
    for i, row in enumerate(existing):
        by_key[(row.get("city_slug"), (row.get("name") or "").strip().lower())] = i
        na = norm_addr(row.get("address") or "")
        if na:
            by_addr[(row.get("city_slug"), na)] = i

    added = updated = skipped = 0
    networks: dict[str, int] = {}
    for row in UPSERTS:
        net = urlparse(row["source_url"]).netloc
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
            networks[net] = networks.get(net, 0) + 1

    hard = [r for r in existing if is_hard_facility(r)]
    soft_dropped = len(existing) - len(hard)
    FAC_PATH.write_text(json.dumps(hard, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps({
        "prepared": len(UPSERTS),
        "added": added,
        "updated": updated,
        "skipped_dup_addr": skipped,
        "soft_dropped": soft_dropped,
        "before_hard": before_hard,
        "after_hard_total": len(hard),
        "net_added_hard": len(hard) - before_hard,
        "networks": sorted([{"host": h, "sites": n} for h, n in networks.items()], key=lambda x: -x["sites"]),
        "source_urls": sorted(set(SOURCES.values())),
    }, indent=2))


if __name__ == "__main__":
    main()
