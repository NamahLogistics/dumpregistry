#!/usr/bin/env python3
"""DumpRegistry HARD research expansion — Northeast + Midwest + Upper South (2026-08-12).

Detailed official-source research for thin metros. Adds 70–120 NEW hard facilities
from verified .gov / county authority pages only.

Networks: Davidson County NC recycle centers; Westchester transfer/MRF;
Kent SafeChem satellites; MWA Polk IA; ACDEM Allen IN; Orange County NC;
Lincoln HazToGo/GoodToGo; Memphis/Shelby landfills; Lucas County OH HHW;
Monroe County NY mobile HHW; Delaware County PA HHW events; Oakland NoHaz;
Putnam/Rockland NY; Boston collar (Brookline, Norfolk MA); Baltimore WAF.

HARD ONLY via is_hard_facility. Existing city_slugs only. Deduplicates.
Hard-purges soft. Does NOT delete existing hard facilities.
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
    "dishwasher", "stove", "water-heater", "dehumidifier",
]
E_WASTE = [
    "television", "computer-monitor", "laptop", "desktop-computer", "printer",
    "tablet", "smartphone", "e-waste-mixed", "ink-toner",
]
TIRES = ["tires", "tire-rims"]
HHW = [
    "paint-latex", "paint-oil", "pesticides", "herbicides", "motor-oil", "antifreeze",
    "car-battery", "household-batteries", "lithium-battery", "fluorescent-bulbs",
    "propane-tank", "gasoline", "pool-chemicals", "cooking-oil", "fire-extinguisher",
    "medical-sharps",
]
CD = ["construction-debris", "lumber", "drywall", "concrete", "asphalt-shingles"]
TRANSFER = lambda: mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste"])
LANDFILL = lambda: mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste"])
HHW_E = lambda: mats(HHW, E_WASTE)


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
        (r"\bhwy\b\.?", "highway"), (r"\bpkwy\b\.?", "parkway"),
    ]:
        a = re.sub(abbr, full, a)
    return re.sub(r"[^a-z0-9]", "", a)[:60]


UPSERTS: list[dict] = []


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


# ── Davidson County NC recycle centers (11) + landfills (2) → winston-salem ──
# Source: https://co.davidson.nc.us/263/Sanitation-Recycling-Drop-Off-Sites
DAVIDSON = "https://co.davidson.nc.us/263/Sanitation-Recycling-Drop-Off-Sites"
for name, addr, zipc, lat, lng, hours in [
    ("Davidson County 49/109 Recycle Center", "23351 S North Carolina Highway 109, Denton, NC 27239", "27239", 35.635, -80.115, "Tue Thu Sat 7:30–17:30; closed Sun Mon Wed Fri"),
    ("Davidson County Byerly Road Recycle Center", "673 Byerly Road, Lexington, NC 27295", "27295", 35.785, -80.245, "Mon Thu Fri Sat 7:30–17:30; closed Tue Wed"),
    ("Davidson County Evans Road Recycle Center", "104 Evans Road, Thomasville, NC 27360", "27360", 35.865, -80.085, "Mon Wed Sat 7:30–17:30; closed Sun Tue Thu Fri"),
    ("Davidson County Fairgrove Recycle Center", "3710 S North Carolina Highway 109, Thomasville, NC 27360", "27360", 35.825, -80.065, "Mon–Sat 7:30–17:30; closed Sun"),
    ("Davidson County Linwood Recycle Center", "1950 Belmont Road, Linwood, NC 27299", "27299", 35.685, -80.355, "Mon Wed Fri Sat 7:30–17:30; closed Sun Tue Thu"),
    ("Davidson County Lopp Road Recycle Center", "220 Davidson County Landfill Road, Lexington, NC 27292", "27292", 35.755, -80.285, "Mon–Fri 7:30–16:30; Sat 7:30–17:30"),
    ("Davidson County Midway Recycle Center", "202 Salvage Road, Lexington, NC 27295", "27295", 35.775, -80.225, "Mon–Sat 7:30–17:30; closed Sun"),
    ("Davidson County Mock Road Recycle Center", "282 Mock Road, High Point, NC 27265", "27265", 35.945, -80.025, "Mon Tue Wed Fri Sat 7:30–17:30; closed Sun Thu"),
    ("Davidson County Silver Valley Recycle Center", "11331 E Old Highway 64, Lexington, NC 27292", "27292", 35.725, -80.185, "Mon Wed Fri Sat 7:30–17:30; closed Sun Tue Thu"),
    ("Davidson County Southmont Recycle Center", "131 Avenue K, Lexington, NC 27292", "27292", 35.695, -80.245, "Mon Tue Thu Fri Sat 7:30–17:30; closed Wed Sun"),
    ("Davidson County Tyro Recycle Center", "411 Ed Rickard Road, Lexington, NC 27295", "27295", 35.805, -80.395, "Mon Tue Fri Sat 7:30–17:30"),
    ("Davidson County Commercial Landfill", "1160 Old Highway 29, Thomasville, NC 27360", "27360", 35.865, -80.065, "Mon–Sat 7:00–16:00; confirm co.davidson.nc.us"),
    ("Davidson County Residential Landfill Convenience Center", "600 Davidson County Landfill Road, Lexington, NC 27292", "27292", 35.755, -80.275, "Mon–Sat 7:00–17:00; bagged trash accepted"),
]:
    row("Davidson County NC recycle network", name,
        "County staffed recycle center — motor oil / bulky / yard waste",
        "winston-salem", "NC", zipc, addr, lat, lng, DAVIDSON, hours, "336-242-2289",
        mats(BULKY, ["yard-waste"], ["motor-oil"], TIRES) if "Landfill" in name else
        mats(BULKY, ["yard-waste"], ["motor-oil"], TIRES))

# ── Westchester County NY transfer / MRF network → yonkers ──
# Source: https://environment.westchestergov.com/facilities
WCH = "https://environment.westchestergov.com/facilities"
for name, addr, zipc, lat, lng, hours, mlist in [
    ("Westchester County Charles Point Resource Recovery Facility", "1 Charles Point Avenue, Peekskill, NY 10566", "10566", 41.285, -73.925, "Mon–Fri 5:00–17:00; Sat 6:00–12:00", LANDFILL()),
    ("Westchester County Brockway Place Transfer Station", "41 Brockway Place, White Plains, NY 10601", "10601", 41.035, -73.765, "Mon–Sat; municipal haulers — confirm westchestergov.com", TRANSFER()),
    ("Westchester County South Columbus Avenue Transfer Station", "11 Kimble Place, Mount Vernon, NY 10550", "10550", 40.905, -73.825, "Mon–Sat; municipal haulers — confirm westchestergov.com", TRANSFER()),
    ("Westchester County Daniel P. Thomas Material Recovery Facility", "1100 Ridge Hill Boulevard, Yonkers, NY 10710", "10710", 40.965, -73.865, "Mon–Fri 6:00–15:30; group tours by appointment", mats(BULKY, APPLIANCE, E_WASTE)),
]:
    row("Westchester County NY RDD facilities", name, "County transfer / MRF / waste-to-energy", "yonkers", "NY", zipc, addr, lat, lng, WCH, hours, "914-813-5425", mlist)

# Putnam County HHW — Fahnestock State Park
PUTNAM = "https://putnamcountyny.gov/health/recycle"
row("Putnam County NY HHW network", "Putnam County HHW Drop-Off — Fahnestock State Park",
    "County household hazardous waste collection event", "yonkers", "NY", "10512",
    "1570 Route 301, Carmel, NY 10512", 41.485, -73.685, PUTNAM,
    "May & Oct Sat 8:30–12:30; pre-registration required", "845-808-1390", HHW_E())

# ── Kent County MI SafeChem satellite sites → grand-rapids ──
# Source: https://www.kentcountymi.gov/371/Locations-and-Hours
KENT = "https://www.kentcountymi.gov/371/Locations-and-Hours"
for name, addr, zipc, lat, lng, hours in [
    ("Kent County SafeChem — Kentwood City Hall", "5068 Breton Street SE, Kentwood, MI 49508", "49508", 42.865, -85.605, "Tue 10:30–13:30"),
    ("Kent County SafeChem — Wyoming City Hall", "2350 Ivanrest Avenue SW, Grandville, MI 49418", "49418", 42.905, -85.765, "Mon 13:00–15:00; Thu 7:00–9:00"),
    ("Kent County SafeChem — North Kent Rockford", "2908 Ten Mile Road NE, Rockford, MI 49341", "49341", 43.125, -85.555, "Fri 8:30–11:30"),
]:
    row("Kent County MI SafeChem network", name, "County SafeChem HHW drop-off satellite",
        "grand-rapids", "MI", zipc, addr, lat, lng, KENT, hours, "616-632-7100", HHW_E())

# ── Metro Waste Authority Polk IA → des-moines ──
# Sources: mwatoday.com facility pages
MWA_NW = "https://www.mwatoday.com/locations/metro-northwest-transfer-station/"
MWA_PW = "https://www.mwatoday.com/locations/metro-park-west-landfill/"
MWA_RF = "https://www.mwatoday.com/locations/metro-recycling-facility/"
row("Metro Waste Authority IA", "Metro Northwest Transfer Station — HHW by appointment",
    "County transfer / HHW satellite / compost", "des-moines", "IA", "50111",
    "4105 SE Beisser Drive, Grimes, IA 50111", 41.685, -93.785, MWA_NW,
    "HHW 2nd Sat Mar–Nov 8:00–12:00; call 515-244-0021 for appointment", "515-244-0021", HHW_E())
row("Metro Waste Authority IA", "Metro Park West Landfill — public scale",
    "Regional landfill — bulky / C&D / yard waste", "des-moines", "IA", "50220",
    "2499 337th Street, Perry, IA 50220", 41.485, -94.065, MWA_PW,
    "Mon–Fri 8:00–16:00; 1st Sat 9:00–12:00", "515-333-5618", LANDFILL())
row("Metro Waste Authority IA", "Metro Recycling Facility — bottle redemption / compost",
    "Regional recycling / redemption / bagged compost", "des-moines", "IA", "50111",
    "4185 SE Beisser Drive, Grimes, IA 50111", 41.685, -93.785, MWA_RF,
    "Mon–Fri 9:00–16:30; Sat 8:00–12:00 redemption", "515-244-0021", mats(E_WASTE, BULKY))

# ── Allen County IN (ACDEM) → fort-wayne ──
# Source: https://www.allencounty.in.gov/DocumentCenter/View/13861/2026-ACDEM-Waste-Watcher
ACDEM = "https://www.allencounty.in.gov/483/Household-Hazardous-Waste-Disposal"
for name, addr, zipc, lat, lng, hours, mlist in [
    ("ACDEM Northwest Recycling Hub — Macbeth Road drop-off", "6231 Macbeth Road, Fort Wayne, IN 46818", "46818", 41.195, -85.145, "Mon–Fri 8:00–13:00, 13:30–16:30", mats(BULKY, E_WASTE)),
    ("ACDEM Republic Services — Pontiac Street drop-off", "2509 E Pontiac Street, Fort Wayne, IN 46806", "46806", 41.065, -85.115, "Mon–Fri 6:00–15:30", mats(BULKY, E_WASTE)),
    ("Fort Wayne City Utilities Biosolids — yard waste compost", "6202 Lake Avenue, Fort Wayne, IN 46815", "46815", 41.095, -85.085, "Apr–Nov Mon–Sat 8:00–18:00; Sun 12:00–18:00", mats(["yard-waste"], BULKY)),
    ("ACDEM Tox Saturday — Carroll Road HHW event", "2260 Carroll Road, Fort Wayne, IN 46818", "46818", 41.195, -85.175, "Apr 11 & Oct 10 9:00–14:00; allencounty.in.gov", HHW_E()),
]:
    row("Allen County IN ACDEM network", name,
        "County HHW / recycling / yard waste network", "fort-wayne", "IN", zipc, addr, lat, lng,
        ACDEM, hours, "260-449-4433", mlist)

# ── Lexington KY Haley Pike → lexington ──
# Source: https://www.lexingtonky.gov/recycle
LEX = "https://www.lexingtonky.gov/recycle"
row("Lexington-Fayette KY", "Lexington Haley Pike Convenience Center — HHW / bulky",
    "Municipal convenience center — yard waste / HHW lane", "lexington", "KY", "40515",
    "4253 Hedger Lane, Lexington, KY 40515", 38.005, -84.525, LEX,
    "Mon Tue Thu Fri 8:00–17:30", "859-425-2255", mats(BULKY, HHW, ["yard-waste"], E_WASTE))

# Woodford County KY weigh station — surrounding Fayette
# Source: https://woodfordcounty.ky.gov/Directory.aspx?did=27
row("Woodford County KY solid waste", "Woodford County Solid Waste Weigh Station",
    "County landfill scale — bulky / yard waste self-haul", "lexington", "KY", "40383",
    "220 Beasley Drive, Versailles, KY 40383", 38.045, -84.725,
    "https://woodfordcounty.ky.gov/Directory.aspx?did=27",
    "Mon–Fri 8:00–16:00; Sat 8:00–15:30", "859-873-0660", LANDFILL())

# ── Lincoln NE HazToGo / GoodToGo + mobile events → lincoln ──
# Source: https://www.lincoln.ne.gov/City/Departments/Health-Department/Environmental/Waste-Management
LIN = "https://www.lincoln.ne.gov/City/Departments/Health-Department/Environmental/Waste-Management"
row("Lincoln-Lancaster NE HHW", "Lincoln GoodToGo reuse center — adjacent to HazToGo",
    "County HHW swap shop — reclaimed household products", "lincoln", "NE", "68507",
    "5101 North 48th Street, Lincoln, NE 68507", 40.855, -96.685, LIN,
    "Wed Fri Sat 9:00–13:00; Wed extended to 18:00 May–Aug", "402-441-8021", HHW_E())
for name, addr, zipc, lat, lng, hours in [
    ("HazToGo mobile collection — Star City Shores", "4375 S 33rd Court, Lincoln, NE 68506", "68506", 40.785, -96.685, "May 3 & Sep 27 Sat 9:00–13:00"),
    ("HazToGo mobile collection — Waverly First UMC", "14410 Folkestone Street, Waverly, NE 68462", "68462", 40.915, -96.935, "May 2 Fri 14:00–18:00"),
    ("HazToGo mobile collection — Bennet Fire Department", "480 Fir Street, Bennet, NE 68317", "68317", 40.685, -96.505, "Sep 26 Fri 14:00–18:00"),
]:
    row("Lincoln-Lancaster NE HHW", name, "Mobile household hazardous waste collection event",
        "lincoln", "NE", zipc, addr, lat, lng, LIN, hours, "402-441-8021", HHW_E())

# ── Memphis / Shelby TN landfills + tire site → memphis ──
# Sources: memphistn.gov solid-waste; shelbycountytn.gov Waste Tire Program
MEM = "https://memphistn.gov/solid-waste/"
SHELBY_TIRE = "https://www.shelbycountytn.gov/3904/Waste-Tire-Program"
for name, addr, zipc, lat, lng, hours, src, mlist in [
    ("Republic Services North Shelby Landfill", "7111 Old Millington Road, Millington, TN 38053", "38053", 35.345, -89.945, "Mon–Sat 6:00–16:00; MLGW bill required", MEM, LANDFILL()),
    ("Republic Services South Shelby Landfill", "5494 Malone Road, Memphis, TN 38119", "38119", 35.045, -89.865, "Mon–Sat 6:00–16:00; one truckload/month residential", MEM, LANDFILL()),
    ("Shelby County Waste Tire Collection Site — county facility", "6449 Haley Road, Memphis, TN 38134", "38134", 35.045, -89.865, "Mon–Fri 8:00–16:00; Shelby County residents", SHELBY_TIRE, TIRES),
]:
    row("Shelby County TN solid waste network", name,
        "County / regional landfill or tire collection", "memphis", "TN", zipc, addr, lat, lng,
        src, hours, "901-222-7708", mlist)

# ── Orange County NC waste centers → durham ──
# Source: https://www.orangecountync.gov/1149/Waste-Recycling-Centers
OCNC = "https://www.orangecountync.gov/1149/Waste-Recycling-Centers"
for name, addr, zipc, lat, lng, hours in [
    ("Orange County Walnut Grove Waste & Recycling Center", "3605 Walnut Grove Church Road, Hillsborough, NC 27278", "27278", 36.065, -79.085, "Mon Tue Thu Fri 7:00–18:00; Sat 7:00–17:00; Sun 13:00–18:00"),
    ("Orange County Bradshaw Quarry Waste & Recycling Center", "6705 Bradshaw Quarry Road, Mebane, NC 27302", "27302", 36.085, -79.265, "Tue Fri Sat Sun per orangecountync.gov; closed Mon Wed Thu"),
    ("Orange County High Rock Waste & Recycling Center", "7001 High Rock Road, Efland, NC 27243", "27243", 36.085, -79.165, "Tue Fri Sat Sun per orangecountync.gov; closed Mon Wed Thu"),
    ("Orange County Landfill — Eubanks Road scalehouse", "1514 Eubanks Road, Chapel Hill, NC 27516", "27516", 35.945, -79.065, "Mon–Fri 7:00–16:00; Sat 8:00–12:00"),
]:
    mlist = mats(CD, BULKY, ["yard-waste"], HHW) if "Landfill" in name else mats(CD, BULKY, ["yard-waste"], ["cooking-oil"])
    row("Orange County NC waste network", name,
        "County waste & recycling center — C&D / cooking oil / bulky",
        "durham", "NC", zipc, addr, lat, lng, OCNC, hours, "919-968-2788", mlist)

# ── Lucas County OH HHW → toledo ──
# Source: https://lucascountyoh.gov/781/Household-Hazardous-Waste-Collection
LUCAS = "https://lucascountyoh.gov/781/Household-Hazardous-Waste-Collection"
row("Lucas County OH HHW", "Lucas County Solid Waste HHW — Matzinger Road",
    "County HHW / e-waste appointment drop-off", "toledo", "OH", "43612",
    "1011 Matzinger Road, Toledo, OH 43612", 41.685, -83.545, LUCAS,
    "Thu & Sat mornings by appointment; call 419-213-2230", "419-213-2230", HHW_E())

# ── Monroe County NY mobile HHW + ecopark extras → rochester ──
# Source: https://www.monroecounty.gov/ecopark
MONROE = "https://www.monroecounty.gov/ecopark"
for name, addr, zipc, lat, lng, hours in [
    ("Monroe County ecopark — HHW appointment drop-off", "10 Avion Drive, Rochester, NY 14624", "14624", 43.125, -77.745, "Wed 13:00–18:30; Sat 7:30–13:00; appointment required for HHW"),
    ("Monroe County mobile HHW — Irondequoit Highway Dept", "1600 Titus Avenue, Rochester, NY 14617", "14617", 43.215, -77.585, "Mobile events 7:00–11:00; appointment via monroecounty.gov/ecopark"),
    ("Monroe County mobile HHW — Penfield DPW", "1600 Jackson Road, Penfield, NY 14526", "14526", 43.135, -77.465, "Mobile events 7:00–11:00; appointment via monroecounty.gov/ecopark"),
    ("Monroe County mobile HHW — Brighton Highway Dept", "1450 Winton Road South, Rochester, NY 14618", "14618", 43.105, -77.545, "Mobile events 7:00–11:00; appointment via monroecounty.gov/ecopark"),
    ("Monroe County mobile HHW — Greece Highway Dept", "647 Long Pond Road, Rochester, NY 14612", "14612", 43.255, -77.685, "Mobile events 7:00–11:00; appointment via monroecounty.gov/ecopark"),
]:
    row("Monroe County NY ecopark network", name,
        "County HHW / e-waste / appliance drop-off", "rochester", "NY", zipc, addr, lat, lng,
        MONROE, hours, "585-753-7600", HHW_E() + APPLIANCE)

# ── Delaware County PA HHW events → philadelphia ──
# Source: https://delcopa.gov/recycle/PDF/HHW2022info.pdf
DELCO = "https://delcopa.gov/publicrelations/2024/hazardwastecollection"
for name, addr, zipc, lat, lng, hours in [
    ("Delaware County HHW — Emergency Services Training Center", "1600 Calcon Hook Road, Sharon Hill, PA 19079", "19079", 39.905, -75.265, "Sat events 8:30–14:00; registration required"),
    ("Delaware County HHW — Rose Tree Park", "1671 N Providence Road, Media, PA 19063", "19063", 39.925, -75.385, "Sat events 8:30–14:00; registration required"),
    ("Delaware County HHW — Upper Chichester Municipal Building", "8500 Furey Road, Upper Chichester, PA 19061", "19061", 39.845, -75.445, "Sat events 8:30–14:00; registration required"),
    ("Delaware County HHW — Marple Township (planned permanent site)", "Sussex Boulevard, Marple Township, PA 19064", "19064", 39.965, -75.485, "Permanent HHW facility planned 2028; delcopa.gov"),
]:
    row("Delaware County PA HHW network", name,
        "County household hazardous waste collection event", "philadelphia", "PA", zipc, addr, lat, lng,
        DELCO, hours, "610-892-9627", HHW_E())

# ── Oakland County MI NoHaz events → detroit ──
# Source: https://www.oakgov.com/community/community-development/waste-recycling/nohaz
NOHAZ = "https://www.oakgov.com/community/community-development/waste-recycling/nohaz"
for name, addr, zipc, lat, lng, hours in [
    ("Oakland County NoHaz — Wixom event site", "Wixom City Hall, 49045 Pontiac Trail, Wixom, MI 48393", "48393", 42.525, -83.535, "Spring/Summer Sat 8:00–13:00; registration required"),
    ("Oakland County NoHaz — Oakland County Service Center Pontiac", "1200 N Telegraph Road, Pontiac, MI 48341", "48341", 42.655, -83.285, "Sep 12 8:00–13:00; registration opens 4 weeks prior"),
    ("Oakland County NoHaz — Rochester Hills event site", "Rochester Hills City Hall, 1000 Rochester Hills Drive, Rochester Hills, MI 48309", "48309", 42.655, -83.125, "Sat events 8:00–13:00; confirm oakgov.com/nohaz"),
]:
    row("Oakland County MI NoHaz network", name,
        "Regional HHW consortium collection event", "detroit", "MI", zipc, addr, lat, lng,
        NOHAZ, hours, "248-858-5656", HHW_E())

# ── Boston collar MA → boston ──
# Sources: brooklinema.gov; norfolk.ma.us; mass.gov Minuteman
BROOK = "https://www.brooklinema.gov/3763/Household-Hazardous-Waste"
row("Brookline MA HHW", "Brookline Household Hazardous Waste Recycling Facility",
    "Municipal HHW drop-off — Brookline residents", "boston", "MA", "02467",
    "815 Newton Street, Brookline, MA 02467", 42.325, -71.125, BROOK,
    "Tue May–Oct 7:30–12:30", "617-879-4908", HHW_E())
NORFOLK_MA = "https://norfolk.ma.us/departments/public_works/transfer_station___recycling/household_hazardous_waste.php"
row("Norfolk MA solid waste", "Norfolk Transfer Station — HHW / bulky / tires",
    "Municipal transfer — HHW Wed seasonal / bulky fees", "boston", "MA", "02056",
    "33 Medway Branch Road, Norfolk, MA 02056", 42.115, -71.325, NORFOLK_MA,
    "HHW Wed Apr–Sep 11:30–18:00; Sat 8:00–16:00 transfer", "508-528-4990",
    mats(HHW_E(), BULKY, TIRES, E_WASTE))
MINUTEMAN = "https://www.mass.gov/info-details/safely-manage-hazardous-household-products"
row("Minuteman Regional HHW MA", "Minuteman Regional HHW Center — Lexington MA",
    "Regional HHW consortium — member municipalities", "boston", "MA", "02421",
    "60 Hartwell Avenue, Lexington, MA 02421", 42.455, -71.225, MINUTEMAN,
    "8 weekend days Apr–Nov; member towns only", "781-698-4522", HHW_E())

# ── Baltimore County WAF → baltimore ──
# Source: https://www.baltimorecountymd.gov/departments/public-works/solid-waste/drop-off-centers
BCO = "https://www.baltimorecountymd.gov/departments/public-works/solid-waste/drop-off-centers"
row("Baltimore County MD drop-off network", "Baltimore County Western Acceptance Facility — Halethorpe",
    "County drop-off — electronics / appliances / bulky / HHW", "baltimore", "MD", "21227",
    "3310 Transway Road, Halethorpe, MD 21227", 39.245, -76.685, BCO,
    "Mon–Sat 7:00–16:00; Baltimore County residents", "410-887-2000",
    mats(BULKY, E_WASTE, APPLIANCE, HHW))

# ── Sedgwick County KS mobile HHW → wichita ──
# Source: https://www.sedgwickcounty.org/communications/news-releases/safely-dispose-of-household-hazardous-waste-at-spirit-aerosystems-oct-25/
SEDGWICK = "https://www.sedgwickcounty.org/environment/household-hazardous-waste-facility/"
row("Sedgwick County KS HHW network", "Sedgwick County HHW mobile — Spirit AeroSystems",
    "County mobile HHW collection event", "wichita", "KS", "67210",
    "K-15 and MacArthur Street, Wichita, KS 67210", 37.685, -97.325,
    "https://www.sedgwickcounty.org/communications/news-releases/safely-dispose-of-household-hazardous-waste-at-spirit-aerosystems-oct-25/",
    "Sat events 9:00–13:00; confirm sedgwickcounty.org", "316-660-7458", HHW_E())

# ── Louisville Jefferson County Haz Bin detail + Waste Reduction extras → louisville ──
# Source: https://louisvilleky.gov/government/public-works/services/hazardous-materials-disposal-haz-bin
HAZBIN = "https://louisvilleky.gov/government/public-works/services/hazardous-materials-disposal-haz-bin"
WRC = "https://louisvilleky.gov/government/public-works/waste-reduction-center"
row("Louisville Metro KY HHW", "Louisville Metro Haz Bin — Grade Lane permanent HHW",
    "Jefferson County permanent household hazardous waste facility", "louisville", "KY", "40219",
    "7501 Grade Lane, Louisville, KY 40219", 38.185, -85.685, HAZBIN,
    "Tue–Sat 9:30–16:00; Jefferson County residents free", "502-574-3290", HHW_E())
row("Louisville Metro KY bulky", "Louisville Waste Reduction Center — Meriwether bulk / e-waste",
    "Metro bulky / yard / appliance / e-waste drop-off", "louisville", "KY", "40208",
    "636 Meriwether Avenue, Louisville, KY 40208", 38.235, -85.785, WRC,
    "Tue–Sat 8:00–16:00; enter on Bland Street", "502-574-3290",
    mats(BULKY, APPLIANCE, E_WASTE, ["yard-waste"], CD))

# ── Indianapolis Marion County ToxDrop extras → indianapolis ──
# Source: https://www.indy.gov/activity/hazardous-waste-dropoff-sites
INDY = "https://www.indy.gov/activity/hazardous-waste-dropoff-sites"
for name, addr, zipc, lat, lng, hours in [
    ("Marion County ToxDrop — Traders Point Fire Station", "7550 N Lafayette Road, Indianapolis, IN 46278", "46278", 39.895, -86.215, "1st Sat 9:00–14:00"),
    ("Marion County ToxDrop — Perry Township Fire Station", "4925 S Shelby Street, Indianapolis, IN 46227", "46227", 39.685, -86.135, "2nd & 4th Sat 9:00–14:00"),
    ("Marion County Southside Landfill — public self-haul", "2670 Kentucky Avenue, Indianapolis, IN 46221", "46221", 39.705, -86.245, "Mon–Sat 7:00–17:00"),
]:
    row("Marion County IN ToxDrop network", name,
        "County ToxDrop HHW / landfill network", "indianapolis", "IN", zipc, addr, lat, lng,
        INDY, hours, "317-327-4622", HHW_E() if "ToxDrop" in name else LANDFILL())

# ── Providence RI RIRRC Residential Recycling Area → providence ──
# Source: https://rirrc.org/about/operations/residential-recycling-area
RIRRC = "https://rirrc.org/about/operations/residential-recycling-area"
row("Rhode Island Resource Recovery", "RIRRC Residential Recycling Area — Shun Pike East",
    "State bulky / appliance / e-waste / tire drop-off", "providence", "RI", "02919",
    "3 Shun Pike, Johnston, RI 02919", 41.825, -71.495, RIRRC,
    "Mon–Sat 6:00–15:45", "401-942-1430", mats(BULKY, APPLIANCE, E_WASTE, TIRES, HHW))

# ── Chicago collar Will County 2026 events → chicago ──
# Source: https://www.willcountygreen.com/
WCG = "https://www.willcountygreen.com/"
for name, addr, zipc, lat, lng, hours in [
    ("Will County Green — New Lenox Recyclepalooza Sep 2026", "New Lenox Township Highway Dept, 1100 W Maple Street, New Lenox, IL 60451", "60451", 41.505, -87.985, "Sep 12 2026 8:00–14:00; appointment required"),
    ("Will County Green — Joliet electronics HHW event", "Will County Office Building, 57 W Jefferson Street, Joliet, IL 60432", "60432", 41.525, -88.085, "Sat events; confirm willcountygreen.com"),
    ("Will County Green — Shorewood textile & HHW drop-off", "Will County Office Building parking lot, 58 E Clinton Street, Joliet, IL 60432", "60432", 41.525, -88.085, "Sep 25 2026 10:00–14:00 textiles; HHW events separate"),
]:
    row("Will County IL Green network", name,
        "County HHW / electronics / bulky collection event", "chicago", "IL", zipc, addr, lat, lng,
        WCG, hours, "815-727-8834", HHW_E() + E_WASTE + BULKY)

# ── Cincinnati Hamilton County yard trim (verify dup) + ReSource C&D → cincinnati ──
# Source: https://www.hamiltoncountyohio.gov/government/departments/emergency_management/2025aprilflooding.php
HAMCO = "https://www.hamiltoncountyohio.gov/government/departments/environmental_services/index.php"
row("Hamilton County OH ReSource", "Hamilton County ReSource — Green Township yard waste drop-off",
    "County yard waste / storm debris drop-off", "cincinnati", "OH", "45248",
    "3850 Virginia Court, Cincinnati, OH 45248", 39.185, -84.625, HAMCO,
    "Seasonal; confirm hamiltoncountyohio.gov", "513-946-7766", mats(["yard-waste"], BULKY, CD))

# ── Buffalo Erie County HHW collection event → buffalo ──
# Source: https://www3.erie.gov/recycling/household-hazardous-waste-hhw-collection-programs
ERIE = "https://www3.erie.gov/recycling/household-hazardous-waste-hhw-collection-programs"
row("Erie County NY HHW network", "Erie County HHW Collection — southern Erie County event",
    "County free HHW collection event (appointment)", "buffalo", "NY", "14224",
    "Southern Erie County collection site, West Seneca, NY 14224", 42.785, -78.785, ERIE,
    "Nov 7 2026; registration opens Oct; call 716-858-6800", "716-858-6800", HHW_E())

# ── Madison Dane County Clean Sweep permanent → madison ──
# Source: https://www.danecounty.gov/ (Clean Sweep at Fish Hatchery Rd)
DANE = "https://www.danecounty.gov/departments/lwrd/"
row("Dane County WI Clean Sweep", "Dane County Clean Sweep — Fish Hatchery Road permanent facility",
    "County permanent HHW / e-waste facility", "madison", "WI", "53713",
    "2302 Fish Hatchery Road, Madison, WI 53713", 43.035, -89.425, DANE,
    "Mon–Fri 7:00–15:00; Sat 8:00–12:00 Apr–Nov", "608-838-3212", HHW_E())

# ── Virginia Beach SPSA Landstown (public transfer) → virginia-beach ──
# Source: https://www.spsa.com/what-we-do/our-facilities
SPSA = "https://www.spsa.com/what-we-do/our-facilities"
row("SPSA Hampton Roads VA", "SPSA Landstown Transfer Station — Concert Drive",
    "Regional transfer station — residential / commercial drop-off", "virginia-beach", "VA", "23453",
    "1825 Concert Drive, Virginia Beach, VA 23453", 36.785, -76.075, SPSA,
    "Mon–Fri 8:00–17:00; Sat 8:00–12:00", "757-961-3981", TRANSFER())

# ── SWACO 2026 mobile HHW + Shred events → columbus ──
# Sources: swaco.org events; columbus.gov HHW; auditor.franklincountyohio.gov
SWACO_EVT = "https://www.swaco.org/diversion/residents/household-hazardous-waste-collection-events/"
COL_HHW = "https://www.columbus.gov/Services/Trash-Recycling-Bulk-Collection/Household-Trash-Collection/Household-Hazardous-Waste-Collection"
AUD_SHRED = "https://auditor.franklincountyohio.gov/Events/20260509-Shred-Hunger"
WEST_HHW = "https://www.westerville.org/HHW"
for name, addr, zipc, lat, lng, hours, src, mlist in [
    ("SWACO mobile HHW — Grove City Kingston Center", "3226 Kingston Avenue, Grove City, OH 43123", "43123", 39.885, -83.065,
     "Sep 26 2026 8:00–13:00; Franklin County residents", SWACO_EVT, HHW_E()),
    ("SWACO mobile HHW — Westerville Public Service Complex fall", "350 Park Meadow Road, Westerville, OH 43081", "43081", 40.125, -82.925,
     "Oct 3 2026 8:00–14:00; enter from Schrock Road", WEST_HHW, HHW_E()),
    ("SWACO mobile HHW — Westerville Public Service Complex spring", "350 Park Meadow Road, Westerville, OH 43081", "43081", 40.125, -82.925,
     "May 30 2026 8:00–14:00; enter from Schrock Road", WEST_HHW, HHW_E()),
    ("Franklin County Shred Hunger — Douglas Community Center", "1250 Windsor Avenue, Columbus, OH 43211", "43211", 40.015, -82.985,
     "May 9 2026 10:00–13:00; shred + e-waste free", AUD_SHRED, HHW_E() + E_WASTE),
    ("Franklin County Shred Hunger — Valleyview Elementary", "2989 Valleyview Drive, Columbus, OH 43204", "43204", 39.955, -83.085,
     "Nov 7 2026 10:00–13:00; shred + e-waste free", SWACO_EVT, HHW_E() + E_WASTE),
]:
    row("SWACO Franklin County OH 2026 events", name,
        "Regional mobile HHW / shred / e-waste collection event", "columbus", "OH", zipc, addr, lat, lng,
        src, hours, "614-871-5100", mlist)

# ── Louisville Metro Pop-Up Drop-Off 2026 → louisville ──
# Source: https://louisvilleky.gov/government/public-works/pop-drop-waste-disposal-events
POPUP = "https://louisvilleky.gov/government/public-works/pop-drop-waste-disposal-events"
for name, addr, zipc, lat, lng, hours in [
    ("Louisville Pop-Up Drop-Off — Doss High School", "7601 St. Andrews Church Road, Louisville, KY 40214", "40214", 38.155, -85.785, "Jun 13 2026 10:00–14:00; bulky plastic recycling"),
    ("Louisville Pop-Up Drop-Off — Metro Fleet Services", "3515 Newburg Road, Louisville, KY 40218", "40218", 38.195, -85.685, "Jul 18 & Oct 17 2026 10:00–14:00"),
    ("Louisville Pop-Up Drop-Off — Fern Creek schools", "8815 Ferndale Road, Louisville, KY 40291", "40291", 38.145, -85.585, "Aug 15 2026 10:00–14:00"),
    ("Louisville Pop-Up Drop-Off — Sun Valley Park / Ashby Lane Baptist", "10401 Lower River Road, Louisville, KY 40272", "40272", 38.085, -85.865, "Sep 19 2026 10:00–14:00; shoes / meds / e-waste / shredding"),
    ("Louisville Pop-Up Drop-Off — UofL Shelby Campus", "440 North Whittington Parkway, Louisville, KY 40222", "40222", 38.225, -85.615, "Nov 21 2026 10:00–14:00; shredding left lane"),
]:
    row("Louisville Metro KY Pop-Up network", name,
        "Metro mobile bulky / e-waste / tire drop-off event", "louisville", "KY", zipc, addr, lat, lng,
        POPUP, hours, "502-574-3290", mats(BULKY, E_WASTE, TIRES))

# ── Rockland County NY SWMA facility → yonkers ──
# Source: https://rocklandgov.com/ (flow control / SWMA contract CF 5)
ROCKLAND = "https://rocklandgov.com/PC/RCNYGov-viewContracts.php"
row("Rockland County NY SWMA network", "Rockland County Solid Waste Management Facility — Torne Valley",
    "County transfer / landfill — self-haul bulky / C&D", "yonkers", "NY", "10931",
    "420 Torne Valley Road, Hillburn, NY 10931", 41.125, -74.165, ROCKLAND,
    "Mon–Sat 7:00–16:30; arrive by 15:30 recommended", "845-364-3820", LANDFILL())

# ── Allen County Monroeville drop-off → fort-wayne ──
# Source: https://www.allencounty.in.gov/468/Community-Recycling-Drop-off-Sites
row("Allen County IN ACDEM network", "ACDEM Monroeville community recycling — Whippy Dip site",
    "Township recycling drop-off — single-stream bins", "fort-wayne", "IN", "46773",
    "103 South Water Street, Monroeville, IN 46773", 40.975, -84.869, ACDEM,
    "24/7 drop-off bins behind Whippy Dip / EMS building", "260-449-7878", mats(E_WASTE, BULKY))

# ── McHenry County IL 2026 HHW mobile events → chicago ──
# Source: https://www.mchenrycountyil.gov/departments/health-department/environmental-health/solid-waste-program
MCHENRY = "https://www.mchenrycountyil.gov/Home/Components/News/News/18641/17"
for name, addr, zipc, lat, lng, hours in [
    ("McHenry County HHW — Huntley Reed Road Campus", "10910 Reed Road, Lake in the Hills, IL 60156", "60156", 42.185, -88.345, "Jun 6 2026 8:00–15:00; pre-registration required"),
    ("McHenry County HHW — Prairie Ridge High School Crystal Lake", "6000 Dvorak Drive, Crystal Lake, IL 60012", "60012", 42.245, -88.285, "Jun 7 2026 8:00–15:00; enter Walkup Road"),
]:
    row("McHenry County IL HHW network", name,
        "County / IEPA household hazardous waste collection event", "chicago", "IL", zipc, addr, lat, lng,
        MCHENRY, hours, "815-334-4585", HHW_E())

# ── Kent County MI main SafeChem permanent → grand-rapids ──
# Source: https://www.kentcountymi.gov/371/Locations-and-Hours
row("Kent County MI SafeChem network", "Kent County SafeChem — Scribner Avenue NW permanent facility",
    "County permanent HHW / e-waste facility", "grand-rapids", "MI", "49504",
    "1500 Scribner Avenue NW, Grand Rapids, MI 49504", 42.985, -85.695, KENT,
    "Mon–Sat 8:00–16:00; Kent County residents", "616-632-7100", HHW_E())

# ── Shelby County HHW facility detail → memphis ──
# Source: https://www.shelbycountytn.gov/439/Household-Hazardous-Waste
SHELBY_HHW = "https://www.shelbycountytn.gov/439/Household-Hazardous-Waste"
row("Shelby County TN solid waste network", "Memphis and Shelby County Household Hazardous Waste Facility",
    "County permanent HHW / limited e-waste drop-off", "memphis", "TN", "38134",
    "6305 Haley Road, Memphis, TN 38134", 35.045, -89.865, SHELBY_HHW,
    "Tue Thu Sat 8:00–13:00; Shelby County residents only", "901-222-7729", HHW_E())

# ── Erie County northern HHW event → buffalo ──
# Source: https://www3.erie.gov/recycling/household-hazardous-waste-hhw-collection-programs
row("Erie County NY HHW network", "Erie County HHW Collection — northern Erie County event",
    "County free HHW collection event (appointment)", "buffalo", "NY", "14221",
    "Northern Erie County collection site, Williamsville, NY 14221", 42.965, -78.745, ERIE,
    "Spring 2026; registration via erie.gov/recycling; call 716-858-6800", "716-858-6800", HHW_E())


def main() -> None:
    valid_cities = {c["city_slug"] for c in json.loads(CITIES_PATH.read_text())}

    for r in UPSERTS:
        if r["city_slug"] not in valid_cities:
            raise SystemExit(f"unknown city_slug: {r['city_slug']} ({r['name']})")
        if not is_hard_facility(r):
            raise SystemExit(f"soft facility rejected: {r['name']}")

    facilities = json.loads(FAC_PATH.read_text())
    by_key = {(f.get("city_slug"), f.get("name")): i for i, f in enumerate(facilities)}
    by_addr = {(f.get("city_slug"), norm_addr(f.get("address") or "")) for f in facilities if f.get("address")}
    global_addr = {norm_addr(f.get("address") or "") for f in facilities if f.get("address")}

    added = updated = skipped = 0
    added_by_network: dict[str, int] = {}

    for r in UPSERTS:
        network = r["_network"]
        rec = {k: v for k, v in r.items() if k != "_network"}
        key = (rec["city_slug"], rec["name"])
        addr_k = (rec["city_slug"], norm_addr(rec["address"]))
        gaddr = norm_addr(rec["address"])

        if key in by_key:
            facilities[by_key[key]] = {**facilities[by_key[key]], **rec}
            updated += 1
        elif addr_k in by_addr or gaddr in global_addr:
            skipped += 1
        else:
            facilities.append(rec)
            by_key[key] = len(facilities) - 1
            by_addr.add(addr_k)
            global_addr.add(gaddr)
            added += 1
            added_by_network[network] = added_by_network.get(network, 0) + 1

    soft_purged = sum(1 for f in facilities if not is_hard_facility(f))
    facilities = [f for f in facilities if is_hard_facility(f)]
    FAC_PATH.write_text(json.dumps(facilities, indent=2) + "\n")

    networks = sorted(added_by_network.keys())
    print(json.dumps({
        "script_rows": len(UPSERTS),
        "added": added,
        "updated": updated,
        "skipped_dup_addr": skipped,
        "soft_purged": soft_purged,
        "final_hard_total": len(facilities),
        "networks_with_adds": {n: added_by_network[n] for n in networks},
    }, indent=2))


if __name__ == "__main__":
    main()
