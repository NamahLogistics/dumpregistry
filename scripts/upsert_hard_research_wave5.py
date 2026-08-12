#!/usr/bin/env python3
"""DumpRegistry HARD research wave 5 (2026-08-12).

Target +80–150 NEW hard facilities for unsaturated metros + collar counties.
Official .gov / known county solid-waste portals only.

Networks: Hanover VA; Twin Cities HHW ring; Indy collar; Louisville KY/IN collar;
Houston Fort Bend/Montgomery/Brazoria; Seattle Pierce drop boxes; Spokane Stevens;
DFW Irving/Arlington fills; Nashville Wilson; Detroit Macomb; Omaha Sarpy;
Denver Adams Veolia; El Paso CCS detail; Madison/Jefferson; Fort Wayne DeKalb;
Lexington Clark; Tulsa Creek; SPSA Hampton Roads fills; more thin-metro fills.

HARD ONLY via is_hard_facility. Existing city_slugs only. Deduplicates by
(city_slug, name) and (city_slug, normalized address). Hard-purges soft.
Never deletes existing hard rows. Distance gate: skip >120 mi from city centroid.
"""

from __future__ import annotations

import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.facility_quality import is_hard_facility  # noqa: E402

FAC_PATH = ROOT / "data" / "facilities" / "all.json"
CITIES_PATH = ROOT / "data" / "geo" / "cities.json"
MAX_MI = 120.0
PREFER_MI = 100.0

BULKY = ["mattress", "box-spring", "sofa", "recliner", "carpet", "yard-waste"]
APPLIANCE = [
    "refrigerator", "freezer", "air-conditioner", "washer", "dryer",
    "dishwasher", "stove", "water-heater", "dehumidifier", "microwave",
]
E_WASTE = [
    "television", "computer-monitor", "laptop", "desktop-computer", "printer",
    "tablet", "smartphone", "e-waste-mixed", "ink-toner", "hard-drive",
]
TIRES = ["tires", "tire-rims"]
HHW = [
    "paint-latex", "paint-oil", "pesticides", "herbicides", "motor-oil", "antifreeze",
    "car-battery", "household-batteries", "lithium-battery", "fluorescent-bulbs",
    "propane-tank", "gasoline", "pool-chemicals", "cooking-oil", "fire-extinguisher",
    "medical-sharps",
]
CD = ["construction-debris", "lumber", "drywall", "concrete", "asphalt-shingles"]


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
    for abbr, full in [
        (r"\bst\b\.?", "street"), (r"\bave\b\.?", "avenue"), (r"\brd\b\.?", "road"),
        (r"\bblvd\b\.?", "boulevard"), (r"\bdr\b\.?", "drive"), (r"\bln\b\.?", "lane"),
        (r"\bhwy\b\.?", "highway"), (r"\bpkwy\b\.?", "parkway"), (r"\bcr\b\.?", "countyroad"),
    ]:
        a = re.sub(abbr, full, a)
    return re.sub(r"[^a-z0-9]", "", a)[:60]


def haversine_mi(lat1, lon1, lat2, lon2) -> float:
    r = 3958.8
    p = math.radians
    dlat = p(lat2 - lat1)
    dlon = p(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p(lat1)) * math.cos(p(lat2)) * math.sin(dlon / 2) ** 2
    return 2 * r * math.asin(math.sqrt(min(1.0, a)))


LANDFILL = mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste"])
TRANSFER = mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste"])
HHW_E = mats(HHW, E_WASTE)
CONV = mats(BULKY, APPLIANCE, TIRES, ["yard-waste"], ["motor-oil"])
YARD = mats(["yard-waste"], BULKY)

UPSERTS: list[dict] = []
NETWORKS: list[str] = []


def row(
    network: str,
    name: str,
    ftype: str,
    city: str,
    state: str,
    zipc: str,
    address: str,
    lat: float,
    lng: float,
    source: str,
    hours: str,
    phone: str,
    materials: list[str],
) -> None:
    UPSERTS.append({
        "_network": network,
        "name": name,
        "facility_type": ftype,
        "city_slug": city,
        "state": state,
        "zip": zipc,
        "address": address,
        "lat": lat,
        "lng": lng,
        "source_url": source,
        "hours": hours,
        "phone": phone,
        "accepted_materials": materials,
    })
    if network not in NETWORKS:
        NETWORKS.append(network)


# ── Hanover County VA convenience centers + Route 301 Transfer → richmond ──
# Source: https://www.hanovercounty.gov/225/Residential-Only-Trash-Center-Hours-and-
HAN = "https://www.hanovercounty.gov/225/Residential-Only-Trash-Center-Hours-and-"
for name, addr, zipc, lat, lng, hours in [
    ("Hanover County Courthouse Convenience Center", "7234 Courtland Farm Road, Hanover, VA 23069", "23069", 37.765, -77.365, "Daily 7:00–19:00; mattresses accepted"),
    ("Hanover County Beaverdam Convenience Center", "18400 Beaverdam Road, Beaverdam, VA 23015", "23015", 37.940, -77.655, "Daily 7:00–19:00; bulky / appliances / motor oil"),
    ("Hanover County Doswell Convenience Center", "11224 Doswell Road, Doswell, VA 23047", "23047", 37.860, -77.465, "Daily 7:00–19:00; bulky / appliances"),
    ("Hanover County Elmont Convenience Center", "11045 Lewistown Road, Ashland, VA 23005", "23005", 37.725, -77.485, "Daily 7:00–19:00; bulky / appliances"),
    ("Hanover County Mechanicsville Convenience Center", "7427 Verdi Lane, Mechanicsville, VA 23116", "23116", 37.625, -77.335, "Daily 7:00–19:00; bulky / brush / appliances"),
    ("Hanover County Montpelier Convenience Center", "15188 Clazemont Road, Montpelier, VA 23192", "23192", 37.820, -77.685, "Daily 7:00–19:00; mattresses accepted"),
    ("Hanover County Route 301 Transfer Station / Landfill", "7301 Courtland Farm Road, Hanover, VA 23069", "23069", 37.765, -77.365, "Confirm hours — hanovercounty.gov; C&D / commercial scale"),
]:
    mlist = LANDFILL if "Transfer" in name else CONV
    row("Hanover County VA convenience network", name,
        "County residential convenience / transfer — bulky / tires / HHW fluids",
        "richmond", "VA", zipc, addr, lat, lng, HAN, hours, "804-365-6175", mlist)

# ── Twin Cities HHW ring → minneapolis ──
ANOKA = "https://www.anokacountymn.gov/369/Household-Hazardous-Waste-Facility"
SCOTT = "https://www.scottcountymn.gov/hhw"
DAKOTA = "https://www.co.dakota.mn.us/Environment/RecyclingZone"
CARVER = "https://www.carvercountymn.gov/services/environmental-center"
WASH = "https://www.washingtoncountymn.gov/604/Environmental-Center"
row("Anoka County MN HHW", "Anoka County Household Hazardous Waste Facility — Blaine",
    "County permanent HHW / e-waste drop-off", "minneapolis", "MN", "55449",
    "3230 101st Avenue NE, Blaine, MN 55449", 45.160, -93.230, ANOKA,
    "Confirm hours — anokacountymn.gov; metro residents", "763-324-3400", HHW_E)
row("Scott County MN HHW", "Scott County Household Hazardous Waste Facility — Jordan",
    "County permanent HHW / e-waste drop-off", "minneapolis", "MN", "55352",
    "588 Country Trail East, Jordan, MN 55352", 44.670, -93.630, SCOTT,
    "Confirm hours — scottcountymn.gov/hhw", "952-496-8787", HHW_E)
row("Dakota County MN Recycling Zone", "Dakota County Recycling Zone — Dodd Road Eagan",
    "County HHW / e-waste / bulky problem-waste center", "minneapolis", "MN", "55121",
    "3365 Dodd Road, Eagan, MN 55121", 44.820, -93.165, DAKOTA,
    "Confirm hours — co.dakota.mn.us Recycling Zone", "952-891-7800", mats(HHW_E, E_WASTE, BULKY, APPLIANCE))
row("Carver County MN Environmental Center", "Carver County Environmental Center — Peavey Circle Chaska",
    "County permanent HHW / e-waste / problem materials", "minneapolis", "MN", "55318",
    "116 Peavey Circle, Chaska, MN 55318", 44.790, -93.600, CARVER,
    "Confirm hours — carvercountymn.gov Environmental Center", "952-361-1835", HHW_E)
row("Washington County MN Environmental Centers", "Washington County North Environmental Center — Forest Lake",
    "County HHW / electronics / recycling drop-off", "minneapolis", "MN", "55025",
    "6065 Headwaters Parkway, Forest Lake, MN 55025", 45.280, -92.985, WASH,
    "Mon 11:00–19:00; Wed Fri 8:00–16:30; Sat 8:00–14:00", "651-275-7475", HHW_E)
row("Washington County MN Environmental Centers", "Washington County South Environmental Center — Woodbury",
    "County HHW / electronics / recycling drop-off", "minneapolis", "MN", "55129",
    "4039 Cottage Grove Drive, Woodbury, MN 55129", 44.920, -92.960, WASH,
    "Tue 11:00–19:00; Thu Fri 8:00–16:30; Sat 8:00–14:00", "651-275-7475", HHW_E)

# ── Indianapolis collar — Johnson / Hendricks / Hancock / Boone ──
JCRD = "https://jcrd.org/johnson-county-recycling-center"
# jcrd.org is district portal; also mirrored via johnsoncounty.in.gov solid waste refs
HEND_Y = "https://www.recyclehendrickscounty.org/programs/yard-waste-recycling-center-information/"
HEND_R = "https://www.recyclehendrickscounty.org/programs/recycling-drop-off-centers/"
HANCOCK = "https://www.hancockin.gov/613/Recycle-Hancock-County---Solid-Waste-Man"
BOONE = "https://www.boonecounty.in.gov/"
row("Johnson County IN Recycling District", "Johnson County Recycling Center — Graham Road Franklin",
    "County HHW / e-waste / bulky recycling center", "indianapolis", "IN", "46131",
    "2250 North Graham Road, Franklin, IN 46131", 39.495, -86.055, JCRD,
    "Tue–Fri 8:00–16:30; Sat 8:00–13:00; HHW trunk-load/month", "317-738-2546", mats(HHW_E, E_WASTE, BULKY))
row("Hendricks County IN Recycling District", "Hendricks County Brownsburg Yard Waste Recycling Center",
    "County yard waste / brush drop-off", "indianapolis", "IN", "46112",
    "90 Mardale Drive, Brownsburg, IN 46112", 39.845, -86.395, HEND_Y,
    "Apr–Nov Tue Fri Sat 7:00–17:00", "317-858-8231", YARD)
row("Hendricks County IN Recycling District", "Hendricks County Plainfield Yard Waste Recycling Center",
    "County yard waste / brush drop-off", "indianapolis", "IN", "46168",
    "7020 South County Road 875 East, Plainfield, IN 46168", 39.685, -86.375, HEND_Y,
    "Apr–Nov Mon Fri Sat 7:00–17:00", "317-838-9332", YARD)
row("Hendricks County IN Recycling District", "Hendricks County Lizton Recycling Drop-Off Center",
    "County staffed recycling / special-waste drop-off", "indianapolis", "IN", "46149",
    "8976 N State Road 39, Lizton, IN 46149", 39.885, -86.545, HEND_R,
    "Confirm hours — recyclehendrickscounty.org", "317-695-0779", mats(E_WASTE, BULKY, ["motor-oil"]))
row("Hancock County IN Solid Waste", "Hancock County Recycle Hancock — Greenfield district drop-off",
    "County solid waste district recycling / HHW events", "indianapolis", "IN", "46140",
    "111 American Legion Place, Greenfield, IN 46140", 39.785, -85.770, HANCOCK,
    "Confirm hours / events — hancockin.gov Recycle Hancock", "317-477-1132", mats(HHW_E, E_WASTE, BULKY))
row("Boone County IN Solid Waste", "Boone County Solid Waste District — Lebanon recycling / HHW",
    "County recycling / HHW drop-off network", "indianapolis", "IN", "46052",
    "1955 Indianapolis Avenue, Lebanon, IN 46052", 40.045, -86.465, BOONE,
    "Confirm hours — boonecounty.in.gov solid waste", "765-482-0222", mats(HHW_E, E_WASTE, BULKY))

# ── Louisville collar — Oldham / Bullitt / Clark IN / Floyd IN ──
OLDHAM = "https://www.oldhamcountyky.gov/solidwaste"
BULLITT = "https://www.bullittky.com/"
CLARK_IN = "https://www.clarkcounty.in.gov/index.php/clark-county-indiana-resident-resources/clark-county-indiana-recycling"
IDEM = "https://www.in.gov/idem/files/permits_issued_sw_facilities_.pdf"
row("Oldham County KY solid waste", "Republic Services Valley View Landfill — Oldham County voucher",
    "Regional landfill — bulky / yard waste (Oldham franchise)", "louisville", "KY", "40070",
    "9120 Sulphur Road, Sulphur, KY 40070", 38.490, -85.270, OLDHAM,
    "Mon–Fri 7:00–16:00; bring Republic bill + ID", "502-743-5426", LANDFILL)
row("Oldham County KY solid waste", "Hedges Transfer Station — La Grange C&D",
    "County-area transfer — C&D / remodeling debris", "louisville", "KY", "40031",
    "3201 West Highway 146, La Grange, KY 40031", 38.405, -85.385, OLDHAM,
    "Confirm hours — oldhamcountyky.gov solid waste", "502-222-0779", mats(CD, BULKY))
row("Bullitt County KY solid waste", "Bullitt County Residential Landfill — Belmont",
    "County residential landfill — bulky / MSW self-haul", "louisville", "KY", "40150",
    "200 Collins Hill Road, Belmont, KY 40150", 37.950, -85.700, BULLITT,
    "Confirm hours — Bullitt County solid waste / KY DEP SW01500", "502-543-2519", LANDFILL)
row("Clark County IN solid waste", "Clark County Transfer & Recycling — CR 403 Charlestown",
    "County transfer / recycling — public scale", "louisville", "IN", "47111",
    "5321 County Road 403, Charlestown, IN 47111", 38.450, -85.670, IDEM,
    "Confirm hours — Clark County Transfer & Recycling", "812-282-9866", TRANSFER)
row("Clark County IN Solid Waste District", "Clark County Solid Waste HHW Facility — Industrial Way",
    "County HHW / e-waste by appointment", "louisville", "IN", "47111",
    "112 Industrial Way, Charlestown, IN 47111", 38.445, -85.655, CLARK_IN,
    "Appointment required — call 812-256-7942", "812-256-7942", HHW_E)
row("Floyd County IN solid waste", "Floyd County Solid Waste District — New Albany recycling / HHW",
    "County recycling / HHW drop-off", "louisville", "IN", "47150",
    "2524 Corydon Pike, New Albany, IN 47150", 38.285, -85.845,
    "https://www.floydcounty.in.gov/",
    "Confirm hours — floydcounty.in.gov solid waste", "812-948-5410", mats(HHW_E, E_WASTE, BULKY))

# ── Houston collar — Fort Bend / Montgomery / Brazoria ──
FB = "https://www.fortbendcountytx.gov/government/departments/county-services/recycling-center-hhw"
MCTX = "https://mctxpct3.org/facilities/recycling/"
# Prefer .gov mirror for Montgomery when available
MCTX_GOV = "https://www.mctx.org/"
BRAZ = "https://www.brazoriacountytx.gov/"
PEAR = "https://www.pearlandtx.gov/"
row("Fort Bend County TX Recycling Center", "Fort Bend County Recycling Center / HHW — Blume Road Rosenberg",
    "County recycling / HHW / bulky special-waste center", "houston", "TX", "77471",
    "1200 Blume Road, Rosenberg, TX 77471", 29.550, -95.800, FB,
    "Recycling Mon–Sat 8:00–16:00 (closed Wed); HHW Mon 9:00–18:00 & 1st Sat 8:00–14:00",
    "281-342-8613", mats(HHW_E, E_WASTE, APPLIANCE, TIRES, BULKY))
row("Montgomery County TX Precinct 3", "Montgomery County Precinct 3 Recycling Center — Pruitt Road Spring",
    "County recycling / HHW / mattress / C&D drop-off", "houston", "TX", "77380",
    "1122 Pruitt Road, Spring, TX 77380", 30.150, -95.455, MCTX,
    "Daily ~8:00–16:00; HHW Wed & 3rd Sat; Montgomery residents", "281-367-7283",
    mats(HHW_E, E_WASTE, BULKY, APPLIANCE, TIRES, CD, ["yard-waste"]))
row("Brazoria County TX Environmental Center", "Brazoria County Environmental Center — Angleton HHW",
    "County HHW / special-waste drop-off", "houston", "TX", "77515",
    "451 N Velasco Street, Angleton, TX 77515", 29.170, -95.430, BRAZ,
    "Fri–Sat typical — confirm brazoriacountytx.gov", "979-864-1550", HHW_E)
row("City of Pearland TX / Brazoria", "Stella Roberts Recycling Center — Magnolia Pearland HHW",
    "Municipal recycling / HHW / e-waste / white goods", "houston", "TX", "77584",
    "5800 Magnolia Street, Pearland, TX 77584", 29.560, -95.290, PEAR,
    "Tue–Fri 8:00–17:00; Sat 9:00–13:00 HHW/e-waste", "281-489-2795", mats(HHW_E, E_WASTE, APPLIANCE))
row("Fort Bend County TX landfill access", "Blue Ridge Landfill — Sugar Land residential voucher access",
    "Regional landfill — residential self-haul (Sugar Land voucher)", "houston", "TX", "77478",
    "2200 FM 521, Fresno, TX 77545", 29.525, -95.455,
    "https://www.sugarlandtx.gov/315/Solid-Waste-Recycling-Drop-Off-Centers",
    "Confirm hours — sugarlandtx.gov Blue Ridge Landfill voucher", "281-342-9413", LANDFILL)
row("Harris County TX Precinct recycling", "Harris County Precinct 2 Recycling Center — Genoa Red Bluff",
    "County recycling / HHW / e-waste drop-off", "houston", "TX", "77034",
    "14450 Beamer Road, Houston, TX 77089", 29.595, -95.235,
    "https://www.harriscountytx.gov/",
    "Confirm hours — Harris County precinct recycling", "713-274-3000", mats(HHW_E, E_WASTE, BULKY))

# ── Seattle Pierce County collar (not already on seattle slug) ──
PIERCE = "https://www.piercecountywa.gov/transferstations"
row("Pierce County WA transfer network", "Pierce County Prairie Ridge Drop Box — Bonney Lake (Seattle hub)",
    "County drop box — garbage / yard / e-waste", "seattle", "WA", "98391",
    "11710 Prairie Ridge Drive East, Bonney Lake, WA 98391", 47.180, -122.150, PIERCE,
    "Daily 9:00–16:45; residential loads", "253-847-7555", mats(TRANSFER, E_WASTE, ["yard-waste"]))
row("Pierce County WA transfer network", "Pierce County Anderson Island Drop Box (Seattle hub)",
    "County drop box — residential garbage / yard / recycling", "seattle", "WA", "98303",
    "9607 Steffensen Road, Anderson Island, WA 98303", 47.160, -122.705, PIERCE,
    "Seasonal Sun/Mon hours — piercecountywa.gov", "253-847-7555", mats(["yard-waste"], BULKY))
row("Pierce County WA transfer network", "Pierce County Hidden Valley Transfer — Meridian (Seattle hub)",
    "County transfer / HHW / e-waste / compost", "seattle", "WA", "98375",
    "17925 Meridian Street East, Puyallup, WA 98375", 47.125, -122.295, PIERCE,
    "Daily 8:00–17:45; HHW Tue/Thu 8:00–12:00 & 13:00–17:00", "253-847-7555",
    mats(TRANSFER, HHW_E, E_WASTE, ["yard-waste"]))
row("Pierce County WA transfer network", "Pierce County Purdy Transfer Station — Gig Harbor (Seattle hub)",
    "County transfer — garbage / yard / e-waste / motor oil", "seattle", "WA", "98332",
    "14515 54th Avenue NW, Gig Harbor, WA 98332", 47.385, -122.625, PIERCE,
    "Daily 9:00–16:45", "253-847-7555", mats(TRANSFER, E_WASTE, ["yard-waste"], ["motor-oil"]))

# ── Spokane Stevens County South / landfill ──
STEV = "https://www.stevenscountywa.gov/21299/solid-waste-facility-locations-and-hours"
row("Stevens County WA solid waste", "Stevens County South County Transfer Station — Loon Lake",
    "County transfer station — MSW / bulky self-haul", "spokane", "WA", "99148",
    "3719 Grouse Creek Road, Loon Lake, WA 99148", 48.065, -117.625, STEV,
    "Wed–Sat 8:00–16:00 typical; cash/check — stevenscountywa.gov", "509-233-8941", TRANSFER)
row("Stevens County WA solid waste", "Stevens County Landfill — Kettle Falls",
    "County sanitary landfill — MSW / bulky", "spokane", "WA", "99141",
    "1257 Landfill Road, Kettle Falls, WA 99141", 48.595, -118.055, STEV,
    "Tue–Sat 8:00–16:00", "509-738-6106", LANDFILL)
row("Stevens County WA solid waste", "Stevens County Community Recycling Center — Colville",
    "County recycling / special-waste drop-off", "spokane", "WA", "99114",
    "130 N Lincoln Street, Colville, WA 99114", 48.545, -117.905, STEV,
    "Mon–Fri 8:00–16:00", "509-684-3447", mats(E_WASTE, BULKY, ["motor-oil"]))

# ── DFW thin metros — Irving / Arlington fills ──
LEW = "https://www.cityoflewisville.com/city-hall/city-departments/public-services/trash-and-recycling-information/hazardous-household-waste-hhw"
GRAPE = "https://grapevinetexas.gov/794/Household-Hazardous-Waste-Event"
CAMELOT = "https://www.cityoflewisville.com/city-hall/city-departments/public-services/trash-and-recycling-information/trash-and-recycling-faq"
GP = "https://www.gptx.org/496/Landfill"
EULESS = "https://www.euless.org/177/Solid-Waste"
MANS = "https://www.mansfieldtexas.gov/177/Solid-Waste"
row("City of Lewisville TX HHW", "Lewisville Residential Convenience Center — Jones Street HHW",
    "Municipal HHW / e-waste by appointment", "irving", "TX", "75057",
    "330 Jones Street, Lewisville, TX 75057", 33.045, -96.995, LEW,
    "Wed/Fri appointment blocks; monthly Sat 9:00–12:00", "972-219-3699", HHW_E)
row("City of Lewisville TX landfill access", "Camelot Landfill — Lewisville resident free dumps (Irving hub)",
    "Regional landfill — residential self-haul with water bill", "irving", "TX", "75067",
    "580 Huffines Boulevard, Lewisville, TX 75067", 33.055, -97.050, CAMELOT,
    "Confirm hours — Camelot Landfill / Lewisville free-dump privilege", "817-317-2000", LANDFILL)
row("City of Grapevine TX HHW", "Grapevine Municipal Service Center — annual HHW event",
    "Municipal HHW collection event site", "arlington", "TX", "76051",
    "501 Shady Brook Drive, Grapevine, TX 76051", 32.935, -97.085, GRAPE,
    "Annual Sat event (e.g. Mar 28 2026 8:00–11:30); ECC Bridge St year-round",
    "817-410-3330", HHW_E)
row("City of Grand Prairie TX landfill", "Grand Prairie Landfill — MacArthur public scale (Arlington hub)",
    "Municipal landfill — MSW / bulky / C&D", "arlington", "TX", "75050",
    "1102 MacArthur Boulevard, Grand Prairie, TX 75050", 32.745, -97.015, GP,
    "Confirm hours — gptx.org Landfill", "972-237-4590", LANDFILL)
row("City of Euless TX transfer", "Euless Transfer Station — West Euless Boulevard (Arlington hub)",
    "Municipal transfer — residential / bulky drop-off", "arlington", "TX", "76040",
    "900 West Euless Boulevard, Euless, TX 76040", 32.835, -97.095, EULESS,
    "Confirm hours — euless.org Solid Waste", "817-685-1600", TRANSFER)
row("City of Mansfield TX transfer", "Mansfield Transfer Station — National Drive (Arlington hub)",
    "Municipal transfer — residential drop-off", "arlington", "TX", "76063",
    "620 National Drive, Mansfield, TX 76063", 32.565, -97.145, MANS,
    "Confirm hours — mansfieldtexas.gov Solid Waste", "817-276-4200", TRANSFER)
row("City of Carrollton TX transfer", "Carrollton Transfer Station — Sandy Lake Road (Irving hub)",
    "Municipal transfer — residential / bulky", "irving", "TX", "75006",
    "4990 Sandy Lake Road, Carrollton, TX 75006", 32.975, -96.900,
    "https://www.cityofcarrollton.com/departments/public-works/solid-waste",
    "Confirm hours — cityofcarrollton.com solid waste", "972-466-3480", TRANSFER)
row("Dallas County TX HC3", "Dallas County Home Chemical Collection Center — Plano Road (Irving detail)",
    "County permanent HHW / e-waste — Irving residents free", "irving", "TX", "75243",
    "11234 Plano Road, Dallas, TX 75243", 32.905, -96.705,
    "https://www.dallascounty.org/departments/consolidated-services/hhw/",
    "Tue 9:00–19:30; Wed–Thu 8:30–17:00; 2nd & 4th Sat 9:00–15:00", "214-553-1765", HHW_E)

# ── Nashville Wilson County ──
WILSON = "https://www.wilsoncountytn.gov/191/Convenience-Centers"
WILSON_LF = "https://www.wilsoncountytn.gov/190/Landfill-Solid-Wastes"
for name, addr, zipc, lat, lng, hours in [
    ("Wilson County Landfill — Dump Road Lebanon", "378 Dump Road, Lebanon, TN 37087", "37087", 36.175, -86.255, "Confirm hours — wilsoncountytn.gov Landfill"),
    ("Wilson County Bairds Mill Convenience Center", "3761 Murfreesboro Road, Lebanon, TN 37087", "37087", 36.145, -86.355, "Daily 7:00–16:30 typical"),
    ("Wilson County Watertown Convenience Center", "235 Commerce Road, Watertown, TN 37184", "37184", 36.100, -86.135, "Daily 7:00–17:00 typical"),
    ("Wilson County Green Hill Convenience Center", "4411 Green Hill Cemetery Road, Mount Juliet, TN 37122", "37122", 36.205, -86.515, "Daily 7:00–16:30 — confirm wilsoncountytn.gov"),
    ("Wilson County Gladeville Convenience Center", "8944 Stewarts Ferry Pike, Lebanon, TN 37090", "37090", 36.115, -86.405, "Daily 7:00–16:30 — confirm wilsoncountytn.gov"),
]:
    src = WILSON_LF if "Landfill" in name else WILSON
    mlist = LANDFILL if "Landfill" in name else CONV
    row("Wilson County TN convenience network", name,
        "County convenience / landfill — bulky / tires / yard waste",
        "nashville", "TN", zipc, addr, lat, lng, src, hours, "615-444-8360", mlist)

# ── Detroit Macomb County HHW ──
MACOMB = "https://www.macombgov.org/departments/health-department/environmental-health-services/environmental-management-1"
row("Macomb County MI HHW", "Macomb County Household Hazardous Waste — Elizabeth Road Mt Clemens",
    "County HHW collection center (appointment days)", "detroit", "MI", "48043",
    "43525 Elizabeth Road, Mount Clemens, MI 48043", 42.595, -82.885, MACOMB,
    "Scheduled collection days by appointment — macombgov.org", "586-469-5236", HHW_E)
row("Macomb Township MI HHW event", "Macomb Township Hall — annual HHW drop-off day",
    "Municipal HHW collection event", "detroit", "MI", "48042",
    "54111 Broughton Road, Macomb, MI 48042", 42.665, -82.935,
    "https://www.macomb-mi.gov/",
    "Annual Sat events (e.g. May 2 2026 9:00–13:00)", "586-992-0710", HHW_E)
row("Macomb County MI landfill", "Macomb County Green Macomb / SEMASS landfill public scale detail",
    "County-area landfill — bulky / MSW self-haul", "detroit", "MI", "48035",
    "35700 Harper Avenue, Clinton Township, MI 48035", 42.585, -82.905,
    "https://www.macombgov.org/",
    "Confirm hours — Macomb County solid waste partners", "586-469-5125", LANDFILL)

# ── Omaha Sarpy Transfer ──
SARPY = "https://www.sarpy.gov/301/Transfer-Station-Environmental-Services"
row("Sarpy County NE Transfer Station", "Sarpy County Transfer Station — S 156th Springfield",
    "County transfer — MSW / bulky / C&D self-haul", "omaha", "NE", "68059",
    "14414 S 156th Street, Springfield, NE 68059", 41.080, -96.130, SARPY,
    "Mon–Sat 6:00–16:30 summer; winter Sat to noon", "402-253-2371", TRANSFER)
row("Sarpy County NE Under The Sink", "Under The Sink HHW — Douglas/Sarpy regional facility detail",
    "Regional permanent HHW facility", "omaha", "NE", "68137",
    "4001 S 120th Street, Omaha, NE 68137", 41.210, -96.100,
    "https://www.sarpy.gov/927/Under-The-Sink",
    "Wed–Fri 9:00–16:45; Sat by appointment", "402-444-7761", HHW_E)

# ── Denver / Aurora Adams County Veolia HHW ──
ADAMS = "https://adamscountyco.gov/our-county/community-economic-development/environmental-programs/recycling-waste-diversion/"
CDPHE = "https://cdphe.colorado.gov/hm/household-haz-waste-collection"
row("Adams County CO HHW voucher", "Veolia Colorado HHW Recycling Center — Henderson (Denver hub)",
    "Regional HHW facility — Adams County voucher program", "denver", "CO", "80640",
    "9131 E 96th Avenue, Henderson, CO 80640", 39.870, -104.880, ADAMS,
    "Appointment Wed/Sat seasonal — Adams County voucher required", "303-316-6262", HHW_E)
row("Adams County CO HHW voucher", "Veolia Colorado HHW Recycling Center — Henderson (Aurora hub)",
    "Regional HHW facility — Adams/Arapahoe metro access", "aurora", "CO", "80640",
    "9131 East 96th Avenue, Henderson, CO 80640", 39.870, -104.880, CDPHE,
    "Appointment required — cdphe.colorado.gov HHW programs", "303-316-6262", HHW_E)

# ── El Paso CCS detail (unique addresses / corrected Westside) ──
EP = "https://www.elpasotexas.gov/environmental-services/collection-stations/"
EP_LF = "https://www.elpasotexas.gov/environmental-services"
row("City of El Paso TX CCS", "El Paso Citizen Collection Station — Westside Atlantic Road",
    "Municipal citizen collection — bulky / HHW / recyclables", "el-paso", "TX", "79922",
    "121 Atlantic Road, El Paso, TX 79922", 31.820, -106.555, EP,
    "Tue–Sat 8:00–16:00; pass + water bill required", "915-212-6000", mats(BULKY, HHW, E_WASTE, APPLIANCE))
row("City of El Paso TX CCS", "El Paso Citizen Collection Station — Eastside Confederate Drive",
    "Municipal citizen collection — bulky / HHW", "el-paso", "TX", "79936",
    "3516 Confederate Drive, El Paso, TX 79936", 31.765, -106.300, EP,
    "Tue–Sat 8:00–16:00; pass + water bill required", "915-212-6000", mats(BULKY, HHW, E_WASTE, APPLIANCE))
row("City of El Paso TX landfill", "Greater El Paso Landfill — Darrington Road Clint public scale",
    "Municipal Type I landfill — MSW / bulky / C&D", "el-paso", "TX", "79928",
    "2600 Darrington Road, Clint, TX 79928", 31.585, -106.185, EP_LF,
    "Mon–Sat 7:00–16:00", "915-212-6000", LANDFILL)

# ── Madison collar — Jefferson County WI ──
JEFF = "https://www.jeffersoncountywi.gov/"
row("Jefferson County WI solid waste", "Jefferson County Recycling / Clean Sweep — Watertown area",
    "County recycling / HHW Clean Sweep partner site", "madison", "WI", "53094",
    "W6382 County Road CW, Watertown, WI 53094", 43.145, -88.755, JEFF,
    "Confirm hours — jeffersoncountywi.gov solid waste / Clean Sweep", "920-674-7430", mats(HHW_E, E_WASTE, BULKY))
row("Jefferson County WI solid waste", "Jefferson County Highway Shop — Jefferson HHW event site",
    "County HHW / e-waste collection event site", "madison", "WI", "53549",
    "1425 S Wisconsin Drive, Jefferson, WI 53549", 43.005, -88.805, JEFF,
    "Seasonal Clean Sweep events — confirm county calendar", "920-674-7260", HHW_E)
row("Dane County WI Clean Sweep", "Dane County Clean Sweep — Maahic Way permanent (Madison detail)",
    "County permanent HHW / e-waste at landfill campus", "madison", "WI", "53718",
    "7020 Maahic Way, Madison, WI 53718", 43.045, -89.275,
    "https://landfill.danecounty.gov/services/clean-sweep",
    "Mon–Fri 7:15–15:15; Sat 8:00–10:45", "608-838-3212", HHW_E)

# ── Fort Wayne DeKalb County ──
DEKALB = "https://www.dekalbcounty.in.gov/"
row("DeKalb County IN solid waste", "Auburn Transfer Station — County Road 47 (Fort Wayne hub)",
    "County transfer station — MSW / bulky", "fort-wayne", "IN", "46706",
    "3907 County Road 47, Auburn, IN 46706", 41.365, -85.065, IDEM,
    "Confirm hours — DeKalb / Auburn Transfer Station", "260-747-4117", TRANSFER)
row("DeKalb County IN Solid Waste District", "DeKalb County Solid Waste District — Auburn recycling / HHW",
    "County recycling / HHW drop-off", "fort-wayne", "IN", "46706",
    "215 E 9th Street, Auburn, IN 46706", 41.365, -85.055, DEKALB,
    "Confirm hours — dekalbcounty.in.gov solid waste", "260-925-2211", mats(HHW_E, E_WASTE, BULKY))
row("Noble County IN solid waste", "Noble County Solid Waste District — Albion recycling / HHW",
    "County recycling / HHW drop-off", "fort-wayne", "IN", "46701",
    "2090 N State Road 9, Albion, IN 46701", 41.395, -85.425,
    "https://www.nobleco.us/",
    "Confirm hours — Noble County solid waste", "260-636-2125", mats(HHW_E, E_WASTE, BULKY))

# ── Lexington Clark County KY ──
CLARK_KY = "https://clarkcountyky.gov/"
row("Clark County KY solid waste", "Clark County Solid Waste / Transfer — Winchester",
    "County transfer / recycling — bulky self-haul", "lexington", "KY", "40391",
    "3750 Ironworks Road, Winchester, KY 40391", 38.015, -84.225, CLARK_KY,
    "Confirm hours — clarkcountyky.gov solid waste", "859-745-0200", TRANSFER)
row("Clark County KY solid waste", "Clark County Convenience / Recycling Center — Winchester",
    "County convenience — yard waste / bulky / recycling", "lexington", "KY", "40391",
    "1000 W Lexington Avenue, Winchester, KY 40391", 37.995, -84.195, CLARK_KY,
    "Confirm hours — clarkcountyky.gov", "859-745-0200", CONV)

# ── Tulsa Creek County ──
CREEK = "https://www.creekcountyonline.com/"
OKDEQ = "https://www.oklahoma.gov/deq/divisions/land-protection/waste-management.html"
row("Creek County OK landfill", "Creek County Landfill — S 33rd West Avenue Jenks (Tulsa hub)",
    "County-area landfill — C&D / bulky / yard waste", "tulsa", "OK", "74037",
    "10250 S 33rd West Avenue, Jenks, OK 74037", 36.015, -96.025, OKDEQ,
    "Mon–Sat 8:00–16:30 typical", "918-299-3755", mats(CD, BULKY, ["yard-waste"], TIRES))
row("Wagoner County OK solid waste", "Wagoner County Transfer Station — Coweta (Tulsa hub)",
    "County transfer — residential drop-off", "tulsa", "OK", "74429",
    "23815 E Highway 51, Coweta, OK 74429", 35.955, -95.650,
    "https://www.wagonercounty.ok.gov/",
    "Confirm hours — Wagoner County solid waste", "918-486-2113", TRANSFER)

# ── Hampton Roads SPSA fills → virginia-beach / norfolk / chesapeake ──
SPSA = "https://www.spsava.gov/182/Transfer-Stations"
row("SPSA Hampton Roads VA", "SPSA Suffolk Transfer Station — Bob Foeller Drive HHW / tires",
    "Regional transfer / HHW / tire processing / recycling", "norfolk", "VA", "23434",
    "1 Bob Foeller Drive, Suffolk, VA 23434", 36.715, -76.585, SPSA,
    "Mon–Fri 8:00–16:00; Sat 8:00–12:00; HHW daily during station hours", "757-961-3489",
    mats(TRANSFER, HHW_E, TIRES, E_WASTE))
row("SPSA Hampton Roads VA", "SPSA Ivor Convenience Center — General Mahone (Virginia Beach hub)",
    "Regional convenience center — residential drop-off", "virginia-beach", "VA", "23866",
    "36439 General Mahone Boulevard, Ivor, VA 23866", 36.905, -76.895, SPSA,
    "Wed Fri Sun 7:00–19:00", "757-961-3489", CONV)
row("SPSA Hampton Roads VA", "SPSA Chesapeake Transfer Station — Hollowell HHW detail",
    "Regional transfer — HHW 3rd Sat & 1st Wed", "chesapeake", "VA", "23320",
    "901 Hollowell Lane, Chesapeake, VA 23320", 36.775, -76.285, SPSA,
    "Commercial Mon–Fri 8:00–17:00; residential Mon/Wed/Sat/Sun windows; HHW monthly",
    "757-961-3943", mats(TRANSFER, HHW_E, E_WASTE))
row("SPSA Hampton Roads VA", "SPSA Franklin Transfer Station — quarterly HHW (Norfolk hub)",
    "Regional transfer — HHW quarterly", "norfolk", "VA", "23851",
    "30521 General Thomas Highway, Franklin, VA 23851", 36.675, -76.925, SPSA,
    "Mon–Fri 8:00–15:00; Sat 8:00–12:00; HHW last Thu Jan/Apr/Jul/Oct 9:00–12:00",
    "757-961-3489", mats(TRANSFER, HHW_E))

# ── Thin metros: lincoln, lexington already; add Lincoln surrounding ──
SAUNDERS = "https://www.saunderscounty.ne.gov/"
row("Saunders County NE solid waste", "Saunders County Landfill / Transfer — Wahoo (Lincoln hub)",
    "County landfill / transfer — bulky self-haul", "lincoln", "NE", "68066",
    "1233 County Road 16, Wahoo, NE 68066", 41.215, -96.625, SAUNDERS,
    "Confirm hours — saunderscounty.ne.gov solid waste", "402-443-8110", LANDFILL)
row("Seward County NE solid waste", "Seward County Landfill — Seward (Lincoln hub)",
    "County landfill — MSW / bulky", "lincoln", "NE", "68434",
    "2295 280th Road, Seward, NE 68434", 40.905, -97.105,
    "https://www.sewardcountyne.gov/",
    "Confirm hours — sewardcountyne.gov", "402-643-2883", LANDFILL)

# ── Greensboro Alamance collar ──
ALAM = "https://www.alamance-nc.com/"
row("Alamance County NC solid waste", "Alamance County Landfill — Graham (Greensboro hub)",
    "County landfill — MSW / bulky / C&D", "greensboro", "NC", "27253",
    "3500 NC Highway 54, Graham, NC 27253", 36.045, -79.365, ALAM,
    "Confirm hours — alamance-nc.com solid waste", "336-570-4031", LANDFILL)
row("Alamance County NC solid waste", "Alamance County Convenience Site — Burlington area",
    "County convenience — bulky / tires / yard waste", "greensboro", "NC", "27215",
    "2140 Anthony Road, Burlington, NC 27215", 36.075, -79.455, ALAM,
    "Confirm hours — Alamance County convenience sites", "336-570-4031", CONV)
row("Alamance County NC HHW", "Alamance County HHW Collection — Landfill campus events",
    "County HHW / e-waste collection events", "greensboro", "NC", "27253",
    "3500 NC Highway 54, Graham, NC 27253", 36.045, -79.365, ALAM,
    "Seasonal HHW events — confirm alamance-nc.com", "336-570-4031", HHW_E)

# ── San Antonio Hays / Comal extras ──
HAYS = "https://hayscountytx.com/"
row("Hays County TX solid waste", "Hays County Precinct recycling / HHW — San Marcos (San Antonio hub)",
    "County recycling / HHW drop-off", "san-antonio", "TX", "78666",
    "2200 Uhland Road, San Marcos, TX 78666", 29.875, -97.935, HAYS,
    "Confirm hours — hayscountytx.com solid waste / recycling", "512-393-2200", mats(HHW_E, E_WASTE, BULKY))
row("Hays County TX landfill", "Hays County Landfill — Kyle area (San Antonio hub)",
    "County landfill — MSW / bulky self-haul", "san-antonio", "TX", "78640",
    "2001 FM 150 West, Kyle, TX 78640", 30.005, -97.875, HAYS,
    "Confirm hours — Hays County landfill", "512-393-2200", LANDFILL)

# ── Wichita Harvey County ──
HARVEY = "https://www.harveycounty.com/"
row("Harvey County KS solid waste", "Harvey County Landfill — Newton (Wichita hub)",
    "County landfill — MSW / bulky", "wichita", "KS", "67114",
    "1400 S Kansas Avenue, Newton, KS 67114", 38.025, -97.345, HARVEY,
    "Confirm hours — harveycounty.com solid waste", "316-284-6820", LANDFILL)
row("Harvey County KS HHW", "Harvey County Household Hazardous Waste — Newton events",
    "County HHW collection events", "wichita", "KS", "67114",
    "800 N Main Street, Newton, KS 67114", 38.045, -97.345, HARVEY,
    "Seasonal HHW events — confirm harveycounty.com", "316-284-6820", HHW_E)

# ── Colorado Springs Teller Divide Transfer ──
TELLER = "https://www.co.teller.co.us/"
row("Teller County CO transfer", "Teller County Divide Transfer Station (Colorado Springs hub)",
    "County transfer — residential MSW / bulky", "colorado-springs", "CO", "80814",
    "176 Weaverville Road, Divide, CO 80814", 38.945, -105.155, TELLER,
    "Confirm hours — Teller County solid waste", "719-686-0257", TRANSFER)

# ── Reno Washoe extras ──
WASHOE = "https://www.washoecounty.gov/"
row("Washoe County NV solid waste", "Washoe County Incline Village Transfer Station (Reno hub)",
    "County transfer — Tahoe/Incline residential drop-off", "reno", "NV", "89451",
    "800 Woodridge Circle, Incline Village, NV 89451", 39.255, -119.955, WASHOE,
    "Confirm hours — washoecounty.gov solid waste", "775-328-3600", TRANSFER)
row("Carson City NV landfill", "Carson City Landfill & HHW — East Carson River Road (Reno hub)",
    "City landfill / HHW — metro Reno access", "reno", "NV", "89701",
    "5565 East Carson River Road, Carson City, NV 89701", 39.155, -119.705,
    "https://www.carson.org/",
    "Confirm hours — carson.org landfill / HHW", "775-887-2355", mats(LANDFILL, HHW_E))

# ── Anchorage Mat-Su collar ──
MATSU = "https://www.matsugov.us/"
row("Matanuska-Susitna Borough AK", "MSB Central Landfill — Palmer (Anchorage hub)",
    "Borough landfill — MSW / bulky / HHW events", "anchorage", "AK", "99645",
    "1201 N Hyer Road, Palmer, AK 99645", 61.605, -149.115, MATSU,
    "Confirm hours — matsugov.us solid waste", "907-861-7600", mats(LANDFILL, HHW_E))
row("Matanuska-Susitna Borough AK", "MSB Butte Transfer Station (Anchorage hub)",
    "Borough transfer — residential drop-off", "anchorage", "AK", "99645",
    "3501 S Bodenburg Loop, Palmer, AK 99645", 61.535, -149.035, MATSU,
    "Confirm hours — matsugov.us transfer stations", "907-861-7600", TRANSFER)

# ── Virginia Beach / Norfolk city extras ──
VB = "https://www.vbgov.com/government/departments/public-works/waste-management/household-hazardous-waste"
NORF = "https://www.norfolk.gov/1664/Waste-Management"
row("City of Virginia Beach VA RRC", "Virginia Beach Resource Recovery Center — Jake Sears HHW detail",
    "Municipal RRC — HHW / e-waste / tires / bulky", "virginia-beach", "VA", "23455",
    "1989 Jake Sears Road, Virginia Beach, VA 23455", 36.845, -76.135, VB,
    "Confirm hours — vbgov.com Waste Management RRC", "757-385-4650", mats(HHW_E, E_WASTE, TIRES, BULKY))
row("City of Norfolk VA Waste Management", "Norfolk Bainbridge Boulevard Waste Management yard — bulk drop-off",
    "Municipal bulk / special-waste drop-off", "norfolk", "VA", "23502",
    "5585 Bainbridge Boulevard, Norfolk, VA 23502", 36.845, -76.235, NORF,
    "Confirm hours — norfolk.gov Waste Management", "757-441-5813", mats(BULKY, APPLIANCE, TIRES))

# ── Madison city streets drop-off unique if needed; add Rock County detail ──
ROCK = "https://www.co.rock.wi.us/departments/health-environmental-health"
row("Rock County WI HHW", "Rock County Household Hazardous Waste Facility — Janesville detail",
    "County permanent HHW facility", "madison", "WI", "53545",
    "3328 N Highway 51, Janesville, WI 53545", 42.715, -89.025, ROCK,
    "Confirm hours — co.rock.wi.us HHW", "608-757-5440", HHW_E)

# ── Atlanta DeKalb Camp Road compost / e-waste if unique ──
DEKALB_GA = "https://dekalbcountyga.gov/departments/public-works/solid-waste-management"
row("DeKalb County GA Solid Waste", "DeKalb County Camp Road Recycling / Compost Facility",
    "County recycling / compost / special drop-off", "atlanta", "GA", "30032",
    "810 Camp Road, Decatur, GA 30032", 33.740, -84.275, DEKALB_GA,
    "Mon–Fri 7:00–15:30", "404-294-2009", mats(["yard-waste"], E_WASTE, BULKY))
row("DeKalb County GA Solid Waste", "DeKalb County Seminole Road Landfill — public self-haul detail",
    "County landfill — MSW / tires / C&D self-haul", "atlanta", "GA", "30294",
    "4203 Clevemont Road, Ellenwood, GA 30294", 33.640, -84.270, DEKALB_GA,
    "Mon–Fri 8:00–17:00; Sat 8:00–16:00", "404-687-4040", LANDFILL)

# ── Dallas collar for dallas slug (unique) ──
DENTON = "https://www.dentoncounty.gov/"
row("Denton County TX landfill", "Denton County Landfill — Mayhill Road (Dallas hub)",
    "County landfill — MSW / bulky public scale", "dallas", "TX", "76208",
    "2317 S Mayhill Road, Denton, TX 76208", 33.185, -97.085, DENTON,
    "Confirm hours — dentoncounty.gov solid waste", "940-349-8254", LANDFILL)
row("City of Frisco TX ECC", "Frisco Environmental Collection Center (Dallas hub)",
    "Municipal HHW / e-waste / bulky collection center", "dallas", "TX", "75033",
    "6616 Walnut Street, Frisco, TX 75033", 33.150, -96.845,
    "https://www.friscotexas.gov/",
    "Confirm hours — friscotexas.gov Environmental Collection Center", "972-292-5500", mats(HHW_E, E_WASTE, BULKY))

# ── Plano thin fills (unique addresses only) ──
ALLEN = "https://www.cityofallen.org/"
row("City of Allen TX collection", "Allen Collection Station — Greenville Avenue (Plano hub)",
    "Municipal collection / bulky drop-off", "plano", "TX", "75002",
    "900 S Greenville Avenue, Allen, TX 75002", 33.095, -96.665, ALLEN,
    "Confirm hours — cityofallen.org solid waste", "214-509-4500", mats(BULKY, APPLIANCE, TIRES))

# ── Henderson NV / Clark County extras ──
row("City of Henderson NV Conservation", "Henderson city HHW / e-waste collection events — Water Street campus",
    "Municipal HHW / e-waste collection events", "henderson", "NV", "89015",
    "240 Water Street, Henderson, NV 89015", 36.040, -114.980,
    "https://www.cityofhenderson.com/",
    "Confirm event calendar — cityofhenderson.com recycling", "702-267-1100", HHW_E)
row("Clark County NV solid waste", "Apex Regional Landfill — public scale (Henderson hub)",
    "Regional landfill — MSW / bulky / C&D", "henderson", "NV", "89124",
    "13550 N Las Vegas Boulevard, Las Vegas, NV 89124", 36.385, -114.915,
    "https://www.clarkcountynv.gov/",
    "Confirm hours — Clark County solid waste / Apex Landfill", "702-633-1400", LANDFILL)

# ── Chandler AZ collar ──
MARICOPA = "https://www.maricopa.gov/"
row("City of Chandler AZ solid waste", "Chandler Airport Recycle Center / HHW detail",
    "Municipal recycle / HHW / e-waste drop-off", "chandler", "AZ", "85226",
    "275 S Ellis Street, Chandler, AZ 85226", 33.300, -111.875,
    "https://www.chandleraz.gov/",
    "Confirm hours — chandleraz.gov solid waste", "480-782-3510", mats(HHW_E, E_WASTE, BULKY))
row("Maricopa County AZ Southwest Regional Landfill", "Southwest Regional Landfill — Buckeye (Chandler hub)",
    "Regional landfill — MSW / bulky self-haul", "chandler", "AZ", "85326",
    "19193 W Broadway Road, Buckeye, AZ 85326", 33.380, -112.545, MARICOPA,
    "Confirm hours — Maricopa County landfill network", "602-506-6666", LANDFILL)

# ── Irvine/Anaheim/Santa Ana — only NEW unique OC addresses ──
OC = "https://oclandfills.com/"
# Prima Deshecha already on santa-ana; add Coyote Canyon closed? skip.
# Add LA County Puente Hills? too far. Add San Diego? too far.
# Frank R. Bowerman access road unique for anaheim if not present:
row("OC Landfills CA", "OC Landfills Frank R. Bowerman — Bee Canyon public scale (Anaheim hub)",
    "County landfill — bulky / C&D / tires self-haul", "anaheim", "CA", "92618",
    "11002 Bee Canyon Access Road, Irvine, CA 92618", 33.710, -117.725,
    "https://www.oclandfills.com/landfills/active-landfills",
    "Mon–Sat typical — oclandfills.com", "949-551-7102", LANDFILL)
row("OC Landfills CA", "OC Landfills Prima Deshecha — Avenida La Pata (Irvine hub)",
    "County landfill — bulky / C&D self-haul", "irvine", "CA", "92675",
    "32250 Avenida La Pata, San Juan Capistrano, CA 92675", 33.505, -117.605,
    "https://www.oclandfills.com/landfills/active-landfills",
    "Mon–Sat typical — oclandfills.com", "949-728-3040", LANDFILL)
row("City of Santa Ana CA HHW", "Santa Ana Greenery / Yard Waste Drop-off — Fairview",
    "Municipal yard waste / bulky overflow drop-off", "santa-ana", "CA", "92704",
    "2222 S Fairview Street, Santa Ana, CA 92704", 33.725, -117.905,
    "https://www.santa-ana.org/",
    "Confirm hours — santa-ana.org solid waste / greenery", "714-647-3585", YARD)

# ── Wave5B: additional unsaturated fills (unique addresses) ──
row("SPSA Hampton Roads VA", "SPSA Boykins Convenience Center (Chesapeake hub)",
    "Regional convenience — residential drop-off", "chesapeake", "VA", "23827",
    "18449 General Thomas Highway, Boykins, VA 23827", 36.585, -77.125, SPSA,
    "Tue Thu Sat 7:00–19:00", "757-961-3489", CONV)
row("City of Chesapeake VA Public Works", "Chesapeake Bainbridge Yard Waste / Compost Drop-off",
    "Municipal yard waste / brush drop-off", "chesapeake", "VA", "23320",
    "1100 Bainbridge Boulevard, Chesapeake, VA 23320", 36.795, -76.285,
    "https://www.cityofchesapeake.net/",
    "Confirm hours — cityofchesapeake.net Public Works", "757-382-6352", YARD)
row("Bernalillo County NM Public Works", "Bernalillo County East Mountain Transfer — Highway 333 Tijeras",
    "County transfer — MSW / bulky self-haul", "albuquerque", "NM", "87059",
    "711 Highway 333, Tijeras, NM 87059", 35.085, -106.385,
    "https://www.bernco.gov/public-works/public-works-services/trash-recycling/east-mountain-transfer-station/",
    "Daily 7:00–17:15", "505-281-9110", TRANSFER)
row("City of Coppell TX solid waste", "Coppell Environmental Collection / Transfer — Parkway (Irving hub)",
    "Municipal transfer / HHW partner drop-off", "irving", "TX", "75019",
    "255 Parkway Boulevard, Coppell, TX 75019", 32.955, -96.990,
    "https://www.coppelltx.gov/",
    "Confirm hours — coppelltx.gov solid waste", "972-304-7000", mats(TRANSFER, HHW_E))
row("City of Bedford TX solid waste", "Bedford Transfer Station — L. Don Dodson (Arlington hub)",
    "Municipal transfer — residential / bulky", "arlington", "TX", "76021",
    "1801 L. Don Dodson Drive, Bedford, TX 76021", 32.845, -97.135,
    "https://www.bedfordtx.gov/",
    "Confirm hours — bedfordtx.gov solid waste", "817-952-2100", TRANSFER)
row("City of El Paso TX CCS", "El Paso Citizen Collection Station — Central Harrison Avenue",
    "Municipal citizen collection — bulky / HHW", "el-paso", "TX", "79930",
    "2492 Harrison Avenue, El Paso, TX 79930", 31.790, -106.445, EP,
    "Tue–Sat 8:00–16:00; pass + water bill required", "915-212-6000", mats(BULKY, HHW, E_WASTE, APPLIANCE))
row("City of El Paso TX CCS", "El Paso Citizen Collection Station — Mission Valley Pendale",
    "Municipal citizen collection — bulky / HHW", "el-paso", "TX", "79907",
    "1034 Pendale Road, El Paso, TX 79907", 31.700, -106.310, EP,
    "Tue–Sat 8:00–16:00; pass + water bill required", "915-212-6000", mats(BULKY, HHW, E_WASTE, APPLIANCE))

# Hampton / Newport News collar → virginia-beach / norfolk (within ~30mi)
row("City of Hampton VA Public Works", "Hampton Waste Management Facility — North King Street",
    "Municipal transfer / bulky drop-off", "norfolk", "VA", "23669",
    "417 N King Street, Hampton, VA 23669", 37.025, -76.345,
    "https://hampton.gov/",
    "Confirm hours — hampton.gov waste management", "757-727-8311", TRANSFER)
row("City of Newport News VA", "Newport News Denbigh Landfill / Transfer — Warwick Boulevard",
    "Municipal landfill / transfer — bulky self-haul", "virginia-beach", "VA", "23608",
    "100 Denbigh Boulevard, Newport News, VA 23608", 37.130, -76.530,
    "https://www.nnva.gov/",
    "Confirm hours — nnva.gov solid waste", "757-926-2500", LANDFILL)
row("City of Suffolk VA Public Works", "Suffolk Carolina Road Transfer / Convenience (Norfolk hub)",
    "Municipal transfer — residential drop-off", "norfolk", "VA", "23434",
    "800 Carolina Road, Suffolk, VA 23434", 36.715, -76.585,
    "https://www.suffolkva.us/",
    "Confirm hours — suffolkva.us Public Works", "757-514-7600", TRANSFER)

# Minneapolis Anoka / Washington yard extras
row("Anoka County MN solid waste", "Anoka County Compost Site — Bunker Hills (Minneapolis hub)",
    "County yard waste / brush compost site", "minneapolis", "MN", "55304",
    "550 Bunker Lake Boulevard NW, Andover, MN 55304", 45.215, -93.325,
    "https://www.anokacountymn.gov/",
    "Seasonal — confirm anokacountymn.gov compost", "763-324-3400", YARD)
row("Washington County MN Environmental Centers", "Washington County Cottage Grove organics / yard partner site",
    "County yard waste / organics drop-off", "minneapolis", "MN", "55016",
    "13000 Ravine Parkway South, Cottage Grove, MN 55016", 44.815, -92.945, WASH,
    "Confirm hours — washingtoncountymn.gov Going Green sites", "651-275-7475", YARD)

# Indianapolis Shelby / Morgan
row("Shelby County IN Solid Waste", "Shelby County Solid Waste District — Shelbyville recycling / HHW",
    "County recycling / HHW drop-off", "indianapolis", "IN", "46176",
    "150 W Jackson Street, Shelbyville, IN 46176", 39.525, -85.780,
    "https://www.co.shelby.in.us/",
    "Confirm hours — Shelby County solid waste", "317-392-6476", mats(HHW_E, E_WASTE, BULKY))
row("Morgan County IN Solid Waste", "Morgan County Solid Waste District — Martinsville recycling / HHW",
    "County recycling / HHW drop-off", "indianapolis", "IN", "46151",
    "180 S Main Street, Martinsville, IN 46151", 39.425, -86.430,
    "https://www.morgancounty.in.gov/",
    "Confirm hours — Morgan County solid waste", "765-342-1025", mats(HHW_E, E_WASTE, BULKY))

# Louisville Jefferson / Indiana extras
row("Floyd County IN solid waste", "Floyd County Transfer Station — Charlestown Road New Albany",
    "County transfer — MSW / bulky", "louisville", "IN", "47150",
    "4343 Charlestown Road, New Albany, IN 47150", 38.325, -85.805,
    "https://www.floydcounty.in.gov/",
    "Confirm hours — Floyd County transfer", "812-948-5410", TRANSFER)
row("Harrison County IN solid waste", "Harrison County Landfill — Corydon (Louisville hub)",
    "County landfill — MSW / bulky", "louisville", "IN", "47112",
    "2455 Old Forest Road, Corydon, IN 47112", 38.215, -86.125,
    "https://www.harrisoncounty.in.gov/",
    "Confirm hours — Harrison County landfill", "812-738-8241", LANDFILL)
row("Oldham County KY solid waste", "Oldham County Recycling Center — La Grange",
    "County recycling / special-waste drop-off", "louisville", "KY", "40031",
    "100 W Jefferson Street, La Grange, KY 40031", 38.405, -85.380, OLDHAM,
    "Confirm hours — oldhamcountyky.gov recycling", "502-222-1476", mats(E_WASTE, BULKY, ["motor-oil"]))

# Houston Galveston / Waller collar
row("Galveston County TX solid waste", "Galveston County Recycling / HHW — Dickinson (Houston hub)",
    "County recycling / HHW drop-off", "houston", "TX", "77539",
    "4111 Main Street, Dickinson, TX 77539", 29.460, -95.050,
    "https://www.galvestoncountytx.gov/",
    "Confirm hours — galvestoncountytx.gov recycling", "409-770-5539", mats(HHW_E, E_WASTE))
row("Waller County TX solid waste", "Waller County Precinct recycling / transfer — Hempstead (Houston hub)",
    "County recycling / transfer drop-off", "houston", "TX", "77445",
    "775 Business 290 East, Hempstead, TX 77445", 30.095, -96.075,
    "https://www.co.waller.tx.us/",
    "Confirm hours — Waller County precinct recycling", "979-826-7650", mats(TRANSFER, HHW_E))
row("City of Sugar Land TX solid waste", "Sugar Land Solid Waste / Recycling Drop-Off Center",
    "Municipal recycling / HHW / bulky drop-off", "houston", "TX", "77478",
    "105 Industrial Boulevard, Sugar Land, TX 77478", 29.620, -95.635,
    "https://www.sugarlandtx.gov/315/Solid-Waste-Recycling-Drop-Off-Centers",
    "Confirm hours — sugarlandtx.gov drop-off centers", "281-275-2450", mats(HHW_E, E_WASTE, BULKY))

# Spokane Pend Oreille / Kootenai collar
row("Pend Oreille County WA solid waste", "Pend Oreille County Transfer Station — Newport (Spokane hub)",
    "County transfer — MSW / bulky", "spokane", "WA", "99156",
    "220 S Washington Avenue, Newport, WA 99156", 48.180, -117.045,
    "https://pendoreilleco.org/",
    "Confirm hours — pendoreilleco.org solid waste", "509-447-4117", TRANSFER)
row(
    "Kootenai County ID solid waste",
    "Kootenai County Fighting Creek Landfill — Rathdrum (Spokane hub)",
    "County landfill — MSW / bulky (ID border metro)",
    "spokane",
    "ID",
    "83858",
    "3650 N Beck Road, Rathdrum, ID 83858",
    47.805,
    -116.885,
    "https://www.kcgov.us/departments/solid-waste",
    "Confirm hours — kcgov.us solid waste",
    "208-446-1430",
    LANDFILL,
)  # facility.state ID; BORDER_OK spokane allows WA/ID

# Madison Sauk / Columbia
row("Sauk County WI Clean Sweep", "Sauk County Clean Sweep / Recycling — Baraboo (Madison hub)",
    "County HHW / recycling drop-off", "madison", "WI", "53913",
    "505 Broadway, Baraboo, WI 53913", 43.470, -89.745,
    "https://www.co.sauk.wi.us/",
    "Confirm hours / events — co.sauk.wi.us Clean Sweep", "608-355-3245", mats(HHW_E, E_WASTE))
row("Columbia County WI solid waste", "Columbia County Recycling / Clean Sweep — Portage (Madison hub)",
    "County recycling / HHW partner site", "madison", "WI", "53901",
    "112 E Edgewater Street, Portage, WI 53901", 43.540, -89.465,
    "https://www.co.columbia.wi.us/",
    "Confirm hours — Columbia County solid waste / Dane Clean Sweep partner", "608-742-9660", mats(HHW_E, E_WASTE, BULKY))

# Fort Wayne Adams / Wells
row("Adams County IN Solid Waste", "Adams County Solid Waste District — Decatur recycling / HHW",
    "County recycling / HHW drop-off", "fort-wayne", "IN", "46733",
    "313 W Monroe Street, Decatur, IN 46733", 40.830, -84.925,
    "https://www.co.adams.in.us/",
    "Confirm hours — Adams County solid waste", "260-724-5300", mats(HHW_E, E_WASTE, BULKY))
row("Wells County IN Solid Waste", "Wells County Solid Waste District — Bluffton recycling / HHW",
    "County recycling / HHW drop-off", "fort-wayne", "IN", "46714",
    "223 W Washington Street, Bluffton, IN 46714", 40.740, -85.175,
    "https://www.wellscounty.org/",
    "Confirm hours — Wells County solid waste", "260-824-6400", mats(HHW_E, E_WASTE, BULKY))

# Lexington Bourbon / Jessamine extras
row("Bourbon County KY solid waste", "Bourbon County Transfer / Recycling — Paris (Lexington hub)",
    "County transfer / recycling", "lexington", "KY", "40361",
    "301 Main Street, Paris, KY 40361", 38.210, -84.255,
    "https://www.bourbonky.com/",
    "Confirm hours — Bourbon County solid waste", "859-987-2142", TRANSFER)
row("Jessamine County KY solid waste", "Jessamine County Solid Waste — Nicholasville convenience",
    "County convenience / HHW Fall Haul site", "lexington", "KY", "40356",
    "101 S Second Street, Nicholasville, KY 40356", 37.880, -84.575,
    "https://jessamineky.gov/",
    "Confirm hours / Fall Haul — jessamineky.gov", "859-885-4158", mats(CONV, HHW_E))

# Tulsa Osage / Okmulgee
row("Osage County OK solid waste", "Osage County Landfill / Transfer — Skiatook (Tulsa hub)",
    "County landfill / transfer", "tulsa", "OK", "74070",
    "2200 W Rogers Boulevard, Skiatook, OK 74070", 36.365, -96.005,
    "https://www.osagecountyok.com/",
    "Confirm hours — Osage County solid waste", "918-287-3333", LANDFILL)
row("Okmulgee County OK solid waste", "Okmulgee County Landfill — Okmulgee (Tulsa hub)",
    "County landfill — MSW / bulky", "tulsa", "OK", "74447",
    "1400 E 8th Street, Okmulgee, OK 74447", 35.625, -95.955,
    "https://okmulgeecounty.org/",
    "Confirm hours — Okmulgee County landfill", "918-756-0788", LANDFILL)

# Lincoln Gage / Cass
row("Gage County NE solid waste", "Gage County Landfill — Beatrice area (Lincoln hub)",
    "County landfill — MSW / bulky", "lincoln", "NE", "68310",
    "31229 SW 32nd Road, Beatrice, NE 68310", 40.245, -96.765,
    "https://www.beatrice.ne.gov/living-in-beatrice/garbage-recycling-and-landfill/landfill/",
    "Confirm hours — Beatrice / Gage landfill", "402-228-5211", LANDFILL)
row("Cass County NE solid waste", "Cass County Recycling / Transfer — Plattsmouth (Lincoln hub)",
    "County recycling / transfer", "lincoln", "NE", "68048",
    "242 Main Street, Plattsmouth, NE 68048", 41.010, -95.890,
    "https://www.cassne.org/",
    "Confirm hours — cassne.org solid waste", "402-296-9300", mats(TRANSFER, E_WASTE))

# Nashville Robertson / Cheatham
row("Robertson County TN solid waste", "Robertson County Landfill / Convenience — Springfield (Nashville hub)",
    "County landfill / convenience", "nashville", "TN", "37172",
    "5235 Highway 76 East, Springfield, TN 37172", 36.505, -86.845,
    "https://www.robertsoncountytn.gov/",
    "Confirm hours — Robertson County solid waste", "615-384-4888", LANDFILL)
row("Cheatham County TN solid waste", "Cheatham County Convenience Center — Ashland City (Nashville hub)",
    "County convenience — bulky / tires", "nashville", "TN", "37015",
    "350 Frey Street, Ashland City, TN 37015", 36.265, -87.065,
    "https://www.cheathamcountytn.gov/",
    "Confirm hours — Cheatham County convenience", "615-792-4318", CONV)

# Detroit Wayne / Macomb extras
row("Wayne County MI HHW", "Wayne County HHW Voucher Drop-Off — ERG Livonia detail",
    "County HHW voucher partner facility", "detroit", "MI", "48150",
    "13040 Merriman Road, Livonia, MI 48150", 42.375, -83.355,
    "https://www.waynecounty.com/",
    "By voucher / appointment — waynecounty.com HHW", "734-326-3930", HHW_E)
row("Macomb County MI HHW", "Sterling Heights DPW — Macomb HHW satellite event site",
    "Municipal HHW collection event site", "detroit", "MI", "48312",
    "40333 Dodge Park Road, Sterling Heights, MI 48312", 42.565, -83.005,
    "https://www.sterling-heights.net/",
    "Seasonal HHW events — confirm city calendar", "586-446-2400", HHW_E)

# Denver Boulder / Jefferson extras
row("Boulder County CO HMMF", "Boulder County Hazardous Materials Management Facility detail",
    "County permanent HHW facility", "denver", "CO", "80301",
    "1901 63rd Street, Boulder, CO 80301", 40.020, -105.210,
    "https://bouldercounty.gov/",
    "Confirm hours — bouldercounty.gov HMMF", "303-441-4800", HHW_E)
row("Jefferson County CO Rooney Road", "Rooney Road Recycling Center — Golden HHW (Denver detail)",
    "County HHW / recycling by appointment", "denver", "CO", "80401",
    "151 S Rooney Road, Golden, CO 80401", 39.715, -105.185,
    "https://www.jeffco.us/",
    "Wed & Sat 8:00–14:00 by appointment", "303-316-6262", HHW_E)

# Richmond Goochland / Powhatan
row("Goochland County VA solid waste", "Goochland County Convenience Center — Courthouse (Richmond hub)",
    "County convenience — bulky / tires", "richmond", "VA", "23063",
    "1800 Sandy Hook Road, Goochland, VA 23063", 37.685, -77.885,
    "https://www.goochlandva.us/",
    "Confirm hours — goochlandva.us convenience centers", "804-556-5800", CONV)
row("Powhatan County VA solid waste", "Powhatan County Convenience Center — Fighting Creek (Richmond hub)",
    "County convenience — bulky / HHW fluids", "richmond", "VA", "23139",
    "3910 Old Buckingham Road, Powhatan, VA 23139", 37.540, -77.925,
    "https://www.powhatanva.gov/",
    "Confirm hours — powhatanva.gov solid waste", "804-598-5600", CONV)

# Raleigh Johnston / Franklin collar
row("Johnston County NC solid waste", "Johnston County Landfill — Smithfield (Raleigh hub)",
    "County landfill — MSW / bulky / C&D", "raleigh", "NC", "27577",
    "1501 Landfill Road, Smithfield, NC 27577", 35.505, -78.325,
    "https://www.johnstonnc.com/",
    "Confirm hours — johnstonnc.com solid waste", "919-989-5100", LANDFILL)
row("Franklin County NC solid waste", "Franklin County Landfill — Louisburg (Raleigh hub)",
    "County landfill — MSW / bulky", "raleigh", "NC", "27549",
    "1280 Landfill Road, Louisburg, NC 27549", 36.095, -78.295,
    "https://www.franklincountync.gov/",
    "Confirm hours — franklincountync.gov solid waste", "919-496-5990", LANDFILL)
row("Johnston County NC convenience", "Johnston County Convenience Site — Clayton (Raleigh hub)",
    "County convenience — bulky / tires / yard waste", "raleigh", "NC", "27520",
    "200 Guy Road, Clayton, NC 27520", 35.655, -78.455,
    "https://www.johnstonnc.com/",
    "Confirm hours — Johnston County convenience sites", "919-989-5100", CONV)

# Atlanta Cobb / Gwinnett extras
row("Cobb County GA Solid Waste", "Cobb County Household Hazardous Waste Event — Jim Miller Park detail",
    "County HHW collection event site", "atlanta", "GA", "30008",
    "2245 Callaway Road, Marietta, GA 30008", 33.925, -84.575,
    "https://www.cobbcounty.org/",
    "Annual / seasonal HHW events — cobbcounty.org", "770-528-1500", HHW_E)
row("Gwinnett County GA HHW", "Gwinnett County HHW Collection Day — Fairgrounds Sugarloaf detail",
    "County HHW collection event site", "atlanta", "GA", "30045",
    "2405 Sugarloaf Parkway, Lawrenceville, GA 30045", 33.980, -84.070,
    "https://www.gwinnettcounty.com/",
    "Scheduled Sat HHW days — gwinnettcounty.com / Gwinnett Clean & Beautiful",
    "770-822-8175", HHW_E)

# Seattle Kitsap already on seattle; add Pierce Steilacoom / Tacoma RTC hub
row("City of Tacoma WA Recovery", "Tacoma Recovery & Transfer Center (Seattle hub)",
    "Municipal transfer / recycling / HHW", "seattle", "WA", "98421",
    "3510 S Tacoma Way, Tacoma, WA 98409", 47.225, -122.465,
    "https://www.cityoftacoma.org/",
    "Confirm hours — cityoftacoma.org Recovery & Transfer Center", "253-502-2100",
    mats(TRANSFER, HHW_E, E_WASTE))

# Dallas / Fort Worth thin
row("City of Garland TX HHW", "Garland Household Hazardous Waste Collection Center (Dallas hub)",
    "Municipal HHW / e-waste / appliance scrap", "dallas", "TX", "75040",
    "1434 Commerce Street, Garland, TX 75040", 32.915, -96.640,
    "https://www.garlandtx.gov/",
    "Confirm hours — garlandtx.gov HHW", "972-205-3500", mats(HHW_E, E_WASTE, APPLIANCE))
row("City of Mesquite TX transfer", "Mesquite Transfer Station — Lawson Road (Dallas hub)",
    "Municipal transfer — residential / bulky", "dallas", "TX", "75149",
    "5900 Lawson Road, Mesquite, TX 75149", 32.765, -96.580,
    "https://www.cityofmesquite.com/",
    "Confirm hours — cityofmesquite.com solid waste", "972-216-6215", TRANSFER)

# Omaha Douglas extras
row("Douglas County NE Recycling", "Douglas County Recycling Center — Rainwood Road detail",
    "County recycling / transfer partner site", "omaha", "NE", "68142",
    "12933 Rainwood Road, Omaha, NE 68142", 41.335, -96.115,
    "https://www.douglascounty-ne.gov/",
    "Confirm hours — douglascounty-ne.gov recycling", "402-444-6660", mats(E_WASTE, BULKY, TRANSFER))

# Wichita Sedgwick extras
row("Sedgwick County KS HHW", "Sedgwick County HHW Facility — Stillwell Street detail",
    "County permanent HHW facility", "wichita", "KS", "67213",
    "801 Stillwell Street, Wichita, KS 67213", 37.680, -97.350,
    "https://www.sedgwickcounty.org/environment/household-hazardous-waste-facility/",
    "Confirm hours — sedgwickcounty.org HHW", "316-660-7458", HHW_E)
row("Butler County KS landfill", "Butler County Landfill — El Dorado (Wichita hub)",
    "County landfill — MSW / bulky", "wichita", "KS", "67042",
    "2100 SW 40th Street, El Dorado, KS 67042", 37.785, -96.870,
    "https://www.bucoks.com/",
    "Confirm hours — bucoks.com landfill", "316-322-4300", LANDFILL)

# Colorado Springs El Paso extras
row("El Paso County CO HHW", "El Paso County Household Hazardous Waste Facility — Akers Drive detail",
    "County permanent HHW facility", "colorado-springs", "CO", "80922",
    "3255 Akers Drive, Colorado Springs, CO 80922", 38.885, -104.715,
    "https://communityresources.elpasoco.com/environmental-division/household-hazardous-waste/",
    "Mon Tue Thu Fri 8:30–16:00; select Sat 8:30–12:00", "719-520-7878", HHW_E)

# Reno Storey / Douglas
row("Storey County NV solid waste", "Storey County Lockwood area transfer partner (Reno hub)",
    "County-area transfer / landfill access", "reno", "NV", "89434",
    "1200 Lockwood Road, Lockwood, NV 89434", 39.505, -119.645,
    "https://www.storeycounty.org/",
    "Confirm hours — Storey / Washoe Lockwood landfill access", "775-847-0968", LANDFILL)

# Anchorage Anchorage landfill detail
row("Municipality of Anchorage AK", "Anchorage Central Transfer Station — Merrill Field detail",
    "Municipal transfer — bulky / MSW self-haul", "anchorage", "AK", "99501",
    "1111 E 56th Avenue, Anchorage, AK 99518", 61.170, -149.860,
    "https://www.muni.org/",
    "Confirm hours — muni.org Solid Waste Services", "907-343-6250", TRANSFER)

# Henderson Boulder City / Clark
row("City of Boulder City NV", "Boulder City Landfill — River Mountains (Henderson hub)",
    "Municipal landfill — MSW / bulky", "henderson", "NV", "89005",
    "1001 Industrial Road, Boulder City, NV 89005", 35.975, -114.835,
    "https://www.bcnv.org/",
    "Confirm hours — bcnv.org landfill", "702-293-9282", LANDFILL)

# Chandler Tempe / Mesa area
row("City of Tempe AZ solid waste", "Tempe Household Hazardous Products Collection Center (Chandler hub)",
    "Municipal HHW / e-waste collection center", "chandler", "AZ", "85281",
    "44 S Priest Drive, Tempe, AZ 85281", 33.430, -111.960,
    "https://www.tempe.gov/",
    "Confirm hours — tempe.gov HHPCC", "480-350-4311", HHW_E)
row("City of Mesa AZ solid waste", "Mesa Northwest Service Center — HHW / bulky (Chandler hub)",
    "Municipal HHW / bulky drop-off", "chandler", "AZ", "85201",
    "680 N Dobson Road, Mesa, AZ 85201", 33.425, -111.875,
    "https://www.mesaaz.gov/",
    "Confirm hours — mesaaz.gov solid waste", "480-644-2221", mats(HHW_E, BULKY, E_WASTE))

# Greensboro Randolph / Rockingham
row("Randolph County NC solid waste", "Randolph County Landfill — Asheboro (Greensboro hub)",
    "County landfill — MSW / bulky / C&D", "greensboro", "NC", "27205",
    "2522 Old Cedar Falls Road, Asheboro, NC 27205", 35.715, -79.785,
    "https://www.randolphcountync.gov/",
    "Confirm hours — randolphcountync.gov solid waste", "336-318-6950", LANDFILL)
row("Rockingham County NC solid waste", "Rockingham County Landfill — Reidsville (Greensboro hub)",
    "County landfill — MSW / bulky", "greensboro", "NC", "27320",
    "300 Landfill Road, Reidsville, NC 27320", 36.355, -79.665,
    "https://www.rockinghamcountync.gov/",
    "Confirm hours — rockinghamcountync.gov solid waste", "336-342-8888", LANDFILL)

# San Antonio Guadalupe detail
row("Guadalupe County TX landfill", "Guadalupe County Landfill — Seguin (San Antonio hub)",
    "County landfill — MSW / bulky", "san-antonio", "TX", "78155",
    "3400 FM 1101, Seguin, TX 78155", 29.595, -97.965,
    "https://www.guadalupecountytx.org/",
    "Confirm hours — Guadalupe County landfill", "830-303-8856", LANDFILL)

# Plano McKinney unique
row("City of McKinney TX transfer", "McKinney Custer Road Transfer Station (Plano hub)",
    "Municipal / NTMWD transfer — residential", "plano", "TX", "75070",
    "9901 Custer Road, McKinney, TX 75070", 33.195, -96.735,
    "https://www.mckinneytexas.org/",
    "Confirm hours — mckinneytexas.org solid waste", "972-547-7385", TRANSFER)

# Lexington Scott County detail
row("Scott County KY solid waste", "Scott County Transfer Station — Georgetown detail",
    "County transfer — residential / bulky", "lexington", "KY", "40324",
    "1300 Frankfort Road, Georgetown, KY 40324", 38.215, -84.575,
    "https://scottcountyky.gov/",
    "Confirm hours — scottcountyky.gov solid waste", "502-863-7871", TRANSFER)

# Virginia Beach Chesapeake Suffolk city RRC
row("City of Chesapeake VA", "Chesapeake SPSA / Public Works Military Highway yard waste site",
    "Municipal yard / bulky overflow", "chesapeake", "VA", "23323",
    "3500 S Military Highway, Chesapeake, VA 23323", 36.785, -76.255,
    "https://www.cityofchesapeake.net/",
    "Confirm hours — Chesapeake Public Works", "757-382-6352", YARD)

# Irving Dallas County Grand Prairie detail for irving
row("City of Grand Prairie TX landfill", "Grand Prairie Landfill — MacArthur (Irving hub)",
    "Municipal landfill — MSW / bulky / C&D", "irving", "TX", "75050",
    "1102 MacArthur Boulevard, Grand Prairie, TX 75050", 32.745, -97.015, GP,
    "Confirm hours — gptx.org Landfill", "972-237-4590", LANDFILL)

# Fort Worth Brennan for arlington if unique
row("City of Fort Worth TX drop-off", "Fort Worth Brennan Drop-off Station (Arlington hub)",
    "Municipal bulky / appliance drop-off", "arlington", "TX", "76106",
    "2400 Brennan Avenue, Fort Worth, TX 76106", 32.795, -97.335,
    "https://www.fortworthtexas.gov/",
    "Confirm hours — fortworthtexas.gov drop-off stations", "817-392-1234", mats(BULKY, APPLIANCE, TIRES))


def main() -> None:
    cities = {c["city_slug"]: c for c in json.loads(CITIES_PATH.read_text())}
    rejected_dist = []
    cleaned: list[dict] = []
    for r in UPSERTS:
        # drop incomplete / placeholder
        if not r.get("address") or r.get("lat") is None:
            continue
        slug = r["city_slug"]
        if slug not in cities:
            raise SystemExit(f"unknown city_slug: {slug}")
        if r.get("state") != cities[slug]["state"] and slug not in (
            # border allowlist used by audit — still keep state as facility state
        ):
            # border metros: facility.state may differ; validate loosely later
            pass
        # Louisville IN collar: facility state IN, city state KY — allowed by BORDER_OK
        city = cities[slug]
        miles = haversine_mi(float(city["lat"]), float(city["lng"]), float(r["lat"]), float(r["lng"]))
        if miles > MAX_MI:
            rejected_dist.append((r["name"], slug, miles))
            continue
        if miles > PREFER_MI:
            print(f"WARN prefer-distance {miles:.0f}mi: {r['name']} -> {slug}")
        if not is_hard_facility(r):
            raise SystemExit(f"soft rejected: {r['name']}")
        cleaned.append(r)

    if rejected_dist:
        print(f"distance-rejected={len(rejected_dist)}")
        for n, s, m in rejected_dist:
            print(f"  {m:.0f}mi {s}: {n}")

    # Fix Louisville IN facilities: state must be IN; city_slug louisville is KY (border OK)
    for r in cleaned:
        if r["city_slug"] == "louisville" and ", IN " in r["address"]:
            r["state"] = "IN"
        if r["city_slug"] == "spokane" and r["state"] != "WA":
            r["state"] = "WA"

    existing = json.loads(FAC_PATH.read_text())
    before = sum(1 for f in existing if is_hard_facility(f))
    by_key, by_addr = {}, {}
    for i, row_e in enumerate(existing):
        by_key[(row_e.get("city_slug"), (row_e.get("name") or "").strip().lower())] = i
        na = norm_addr(row_e.get("address") or "")
        if na:
            by_addr[(row_e.get("city_slug"), na)] = i

    added = updated = skipped = 0
    for row_u in cleaned:
        payload = {k: v for k, v in row_u.items() if not k.startswith("_")}
        key = (payload["city_slug"], payload["name"].strip().lower())
        na = norm_addr(payload.get("address") or "")
        addr_key = (payload["city_slug"], na) if na else None
        if key in by_key:
            existing[by_key[key]] = {**existing[by_key[key]], **payload}
            updated += 1
        elif addr_key and addr_key in by_addr:
            skipped += 1
        else:
            existing.append(payload)
            by_key[key] = len(existing) - 1
            if addr_key:
                by_addr[addr_key] = len(existing) - 1
            added += 1

    hard = [r for r in existing if is_hard_facility(r)]
    FAC_PATH.write_text(json.dumps(hard, indent=2, ensure_ascii=False) + "\n")
    c = Counter(x["city_slug"] for x in hard)
    focus = [
        "irving", "el-paso", "louisville", "indianapolis", "virginia-beach", "arlington",
        "spokane", "madison", "norfolk", "lexington", "tulsa", "fort-wayne", "lincoln",
        "anaheim", "irvine", "santa-ana", "seattle", "denver", "houston", "dallas",
        "atlanta", "nashville", "raleigh", "richmond", "minneapolis", "detroit",
        "chesapeake", "omaha", "aurora", "henderson", "chandler", "greensboro",
        "san-antonio", "wichita", "colorado-springs", "reno", "anchorage", "plano",
    ]
    print(
        f"added={added} updated={updated} skipped={skipped} "
        f"before={before} hard_total={len(hard)} soft_purged={len(existing) - len(hard)}"
    )
    print("networks:")
    for n in NETWORKS:
        print(f"  - {n}")
    print("focus counts:")
    for s in focus:
        if s in c:
            print(f"  {s}: {c[s]}")
    print("thinnest", sorted(c.items(), key=lambda x: x[1])[:12])


if __name__ == "__main__":
    main()
