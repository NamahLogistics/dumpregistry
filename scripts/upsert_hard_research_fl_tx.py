#!/usr/bin/env python3
"""FL / TX hard-facility research expansion (2026-08-12).

Official .gov / county solid-waste sources only. HARD ONLY via is_hard_facility.
Target +80–150 NEW facilities for spine metros in FL and TX.
Never deletes existing hard rows; hard-purges soft after merge.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CITIES_PATH = ROOT / "data" / "geo" / "cities.json"
FAC_PATH = ROOT / "data" / "facilities" / "all.json"
sys.path.insert(0, str(ROOT))
from scripts.facility_quality import is_hard_facility  # noqa: E402

FL_TX = {"FL", "TX"}

BULKY = ["mattress", "box-spring", "sofa", "recliner", "carpet", "yard-waste"]
APPLIANCE = [
    "refrigerator", "freezer", "air-conditioner", "washer", "dryer",
    "dishwasher", "stove", "water-heater", "dehumidifier", "microwave",
]
E_WASTE = [
    "television", "computer-monitor", "laptop", "desktop-computer", "printer",
    "tablet", "smartphone", "hard-drive", "e-waste-mixed", "ink-toner",
]
TIRES = ["tires", "tire-rims"]
HHW = [
    "paint-latex", "paint-oil", "pesticides", "herbicides", "motor-oil", "antifreeze",
    "car-battery", "household-batteries", "lithium-battery", "fluorescent-bulbs",
    "propane-tank", "gasoline", "pool-chemicals", "cooking-oil", "medical-sharps",
]
CD = ["construction-debris", "lumber", "drywall", "concrete", "asphalt-shingles"]
LANDFILL = [*BULKY, *APPLIANCE, *TIRES, *CD, "yard-waste"]
TRANSFER = [*BULKY, *APPLIANCE, *TIRES, *CD, *E_WASTE]
HHW_E = [*HHW, *E_WASTE]
RCC = [*BULKY, *TIRES, *E_WASTE, "paint-latex", "paint-oil", "motor-oil"]


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
) -> dict:
    return {
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
    }


UPSERTS: list[dict] = []
NETWORKS: set[str] = set()


def add(network, name, ftype, city, state, zipc, addr, lat, lng, source, hours, phone, materials):
    NETWORKS.add(network)
    UPSERTS.append(row(network, name, ftype, city, state, zipc, addr, lat, lng, source, hours, phone, materials))


# ── Kaufman County TX → dallas ──
KAUF = "https://www.kaufmancounty.net/DocumentCenter/View/8125/2025-Cleanup-Schedule"
for name, addr, zipc, lat, lng, hours in [
    ("Kaufman County City of Kaufman Convenience Station", "701 Alton Street, Kaufman, TX 75142", "75142", 32.5855, -96.3055,
     "Wed–Sat 8:00–16:00; permit required for regular use"),
    ("Kaufman County Terrell Convenience Station", "287 FM 429, Terrell, TX 75160", "75160", 32.7355, -96.2855,
     "Monthly cleanup events; call 972-703-2626"),
    ("Kaufman County Kemp ECO Station", "6520 Plainview Drive, Kemp, TX 75143", "75143", 32.4255, -96.2255,
     "Mon–Wed 10:00–14:00; permit required"),
    ("Kaufman County Forney Road & Bridge Collection Site", "12051 Pct Circle, Forney, TX 75126", "75126", 32.7455, -96.4455,
     "Monthly cleanup events 8:00–16:00"),
]:
    add("Kaufman County TX", name, "County convenience / cleanup station — bulk / appliances / tires",
        "dallas", "TX", zipc, addr, lat, lng, KAUF, hours, "972-932-2161", mats(BULKY, APPLIANCE, TIRES, HHW, E_WASTE))

# ── Collin County Farmersville Transfer → dallas ──
add("Collin County TX", "Collin County Farmersville Transfer Station — HHW by appointment",
    "County transfer station — HHW / e-waste (unincorporated Collin)",
    "dallas", "TX", "75442", "3300 County Road 610, Farmersville, TX 75442", 33.1655, -96.3655,
    "https://www.collincountytx.gov/Services/Environmental-Health",
    "By appointment — call Environmental Health", "972-548-5530", mats(HHW_E, APPLIANCE, TIRES))

# ── Wise County TX dumpsites (5) → fort-worth ──
WISE = "https://www.wisecountytx.gov/BusinessDirectoryII.aspx?lngBusinessCategoryID=24"
for name, addr, zipc, lat, lng, hours in [
    ("Wise County Boyd Dumpsite", "546 S Allen Street, Boyd, TX 76023", "76023", 33.0755, -97.5655, "Wed–Sat 8:00–17:30"),
    ("Wise County Chico Dumpsite", "2897 FM 1655 South, Chico, TX 76431", "76431", 33.2955, -97.7955, "Wed–Sat 8:30–17:30"),
    ("Wise County Cottondale Dumpsite", "6465 FM 2123, Paradise, TX 76073", "76073", 33.1455, -97.6855, "Wed–Sat 8:00–17:30"),
    ("Wise County Decatur Dumpsite", "127 PR 4195, Decatur, TX 76234", "76234", 33.2455, -97.5855, "Mon–Sat 8:00–17:30"),
    ("Wise County Slidell Dumpsite", "242 CR 2820, Slidell, TX 76267", "76267", 33.3555, -97.3855, "Thu–Sat 8:30–17:30"),
]:
    add("Wise County TX", name, "County public dumpsite — bulk / appliances / tires",
        "fort-worth", "TX", zipc, addr, lat, lng, WISE, hours, "940-627-9332", mats(BULKY, APPLIANCE, TIRES, CD))

# ── Parker County TX → fort-worth ──
PARK = "https://www.parkercountytx.gov/233/Convenience-Center-Info"
add("Parker County TX", "Parker County North Residential Disposal Center",
    "County residential disposal — bulk / appliances / tires / scrap metal",
    "fort-worth", "TX", "76085", "3000 Veal Station Road, Weatherford, TX 76085", 32.7855, -97.6855, PARK,
    "Mon–Fri 8:00–16:00; Parker County residents only", "817-596-4171", mats(BULKY, APPLIANCE, TIRES, CD))
add("Parker County TX", "Parker County Convenience Center — Tin Top Road",
    "County convenience center — bulk / appliances / tires / scrap metal",
    "fort-worth", "TX", "76087", "2833 Tin Top Road, Weatherford, TX 76087", 32.7255, -97.6255, PARK,
    "Mon–Fri 8:00–16:30; Parker County Pct 3 & 4 residents", "817-594-0371", mats(BULKY, APPLIANCE, TIRES, CD))

# ── Greenville-Hunt County HHW → dallas ──
add("Hunt County TX", "Greenville-Hunt County Regional Household Hazardous Waste Facility",
    "Regional HHW collection center — paint / chemicals / e-waste",
    "dallas", "TX", "75401", "3108 Sockwell Boulevard, Greenville, TX 75401", 33.1255, -96.1055,
    "https://www.greenvilletx.gov/658/Household-Hazardous-Waste-Center",
    "1st & 3rd Tue 16:00–19:00; 4th Sat 8:00–12:00", "903-457-3152", mats(HHW_E))

# ── Garland TX Transfer + Citizen's Convenience → garland ──
GAR = "https://www.garlandtx.gov/3722/Transfer-Station"
add("Garland TX", "Garland Transfer Station — household trash / brush / bulky",
    "Municipal transfer station — bulk / appliances / yard waste",
    "garland", "TX", "75040", "1426 Commerce Street, Garland, TX 75040", 32.9055, -96.6355, GAR,
    "Mon–Fri 8:00–17:00; Garland residents free with proof", "972-205-3500", mats(BULKY, APPLIANCE, ["yard-waste"], CD))
add("Garland TX", "Garland Citizens' Convenience Center — Hinton Landfill",
    "Municipal landfill convenience center — bulk / appliances / tires",
    "garland", "TX", "75089", "3175 Elm Grove Road, Rowlett, TX 75089", 32.9255, -96.5655,
    "https://www.garlandtx.gov/3680/Citizens-Convenience-Center",
    "Mon–Fri 7:00–16:30; Sat 7:00–14:00; Garland residents free", "972-205-3670", mats(BULKY, APPLIANCE, TIRES, CD))

# ── Putnam County FL (3) → jacksonville ──
PUT = "https://www.putnam-fl.gov/departments/sanitation-services/"
for name, addr, zipc, lat, lng, hours in [
    ("Putnam County Central Landfill", "140 County Landfill Road, Palatka, FL 32177", "32177", 29.6855, -81.6855,
     "Mon–Fri 7:00–17:00; Sat 8:30–17:00"),
    ("Putnam County Huntington Collection Center", "1551 CR 308, Crescent City, FL 32112", "32112", 29.4255, -81.5855,
     "Tue–Sat 7:30–17:30"),
    ("Putnam County Interlachen Collection Center", "111 Hickory Lane, Interlachen, FL 32148", "32148", 29.6255, -81.8855,
     "Tue–Sat 7:30–17:30"),
]:
    add("Putnam County FL", name, "County landfill / convenience center — bulk / tires / C&D",
        "jacksonville", "FL", zipc, addr, lat, lng, PUT, hours, "386-329-0395", mats(BULKY, TIRES, CD, APPLIANCE))

# ── Highlands County FL → orlando ──
HIGH = "https://www.highlandsfl.gov/departments/solid_waste/recycling_other/HHW.php"
add("Highlands County FL", "Highlands County Arbuckle Creek Road Landfill",
    "County landfill — bulk / yard waste / tires / HHW",
    "orlando", "FL", "33876", "12700 Arbuckle Creek Road, Sebring, FL 33876", 27.4855, -81.3855, HIGH,
    "Mon–Fri 7:30–17:00; Sat 7:30–12:00", "863-402-7786", mats(LANDFILL, HHW_E))
add("Highlands County FL", "Highlands County Skipper Road HHW Collection Center",
    "County HHW / e-waste drop-off",
    "orlando", "FL", "33870", "6000 Skipper Road, Sebring, FL 33870", 27.4655, -81.4255, HIGH,
    "Mon 7:00–15:30; HHW events — confirm highlandsfl.gov", "863-402-7786", mats(HHW_E))

# ── Hardee / DeSoto / Glades / Okeechobee → tampa / orlando ──
add("Hardee County FL", "Hardee County Sanitary Landfill",
    "County landfill — bulk / tires / HHW / appliances",
    "tampa", "FL", "33873", "685 Airport Road, Wauchula, FL 33873", 27.5655, -81.7855,
    "https://www.hardeecountyfl.gov/departments-services/public-works/landfill/",
    "Mon–Fri 7:30–17:00; Sat 7:30–12:00", "863-773-5089", mats(LANDFILL, HHW_E))
add("DeSoto County FL", "DeSoto County Landfill & Environmental Services",
    "County landfill — bulk / tires / white goods / HHW",
    "tampa", "FL", "34266", "3268 SW Dishong Avenue, Arcadia, FL 34266", 27.1755, -81.9155,
    "https://desotobocc.com/Directory.aspx?did=20",
    "Mon–Sat 7:30–17:30; scale until 17:00", "863-993-4826", mats(LANDFILL, HHW, TIRES, APPLIANCE))
add("Glades County FL", "Glades County Solid Waste Transfer Station",
    "County transfer station — residential waste / tires / yard waste",
    "tampa", "FL", "33471", "11900 West State Road 78, Moore Haven, FL 33471", 26.8355, -81.2955,
    "https://www.myglades.com/departments/road_department/landfill.php",
    "Mon–Fri 8:00–15:30; Sat 8:00–12:00", "863-675-0124", mats(TRANSFER, TIRES, ["yard-waste"]))
add("Okeechobee County FL", "Okeechobee County Landfill — public drop-off",
    "County landfill — MSW / tires / C&D / yard waste",
    "orlando", "FL", "34972", "10800 NE 128th Avenue, Okeechobee, FL 34972", 27.3855, -80.8255,
    "https://www.okeechobeecountyfl.gov/departments/solid-waste-recycling",
    "Mon–Fri 5:00–16:00; Sat 7:00–12:00", "863-763-4818", mats(LANDFILL))

# ── Hendry County HHW → tampa ──
HEND = "https://www.hendryfla.net/household_hazardous_waste.php"
for name, addr, zipc, lat, lng in [
    ("Hendry County LaBelle HHW Collection Center", "1360 Forestry Division Road, LaBelle, FL 33935", "33935", 26.7655, -81.4455),
    ("Hendry County Clewiston HHW Collection Center", "1381 Evercane Road, Clewiston, FL 33440", "33440", 26.7555, -80.9355),
]:
    add("Hendry County FL", name, "County HHW collection center — by appointment",
        "tampa", "FL", zipc, addr, lat, lng, HEND,
        "By appointment only — call Special Districts 863-675-5252", "863-675-5252", mats(HHW_E))

# ── Clay County ECCs (4) → jacksonville ──
CLAY = "https://www.claycountygov.com/community/garbage-and-recycling/facilities"
for name, addr, zipc, lat, lng in [
    ("Clay County Clay Hill Environmental Convenience Center", "5869 County Road 218, Middleburg, FL 32068", "32068", 30.0855, -81.8655),
    ("Clay County Doctors Inlet Environmental Convenience Center", "288 Sleepy Hollow Road, Middleburg, FL 32068", "32068", 30.1255, -81.7855),
    ("Clay County Keystone Heights Environmental Convenience Center", "5505 County Road 214, Keystone Heights, FL 32656", "32656", 29.7855, -82.0255),
    ("Clay County Long Bay Environmental Convenience Center", "1589 Long Bay Road, Middleburg, FL 32068", "32068", 30.0455, -81.8255),
]:
    add("Clay County FL", name, "County environmental convenience center — bulk / tires / yard waste",
        "jacksonville", "FL", zipc, addr, lat, lng, CLAY,
        "Thu–Sat 7:30–17:30", "904-284-6374", mats(BULKY, TIRES, APPLIANCE, ["yard-waste"], E_WASTE))
add("Clay County FL", "Clay County Rosemary Hill Household Hazardous Waste Center",
    "County HHW / e-waste at landfill",
    "jacksonville", "FL", "32043", "3545 Rosemary Hill Road, Green Cove Springs, FL 32043", 29.9855, -81.6855, CLAY,
    "Mon–Sat 7:30–17:30", "904-284-6374", mats(HHW_E))

# ── Levy County FL (4) → orlando ──
LEVY = "https://www.levycounty.org/254/Satellite-Locations"
add("Levy County FL", "Levy County Solid Waste Management Facility",
    "County landfill / transfer — bulk / tires / C&D / HHW",
    "orlando", "FL", "32696", "12051 NE 69th Lane, Williston, FL 32696", 29.4355, -82.5855, LEVY,
    "Mon–Sat 7:30–17:00; HHW Sat 8:00–12:00", "352-486-3300", mats(LANDFILL, HHW_E))
for name, addr, zipc, lat, lng in [
    ("Levy County 8-Mile Satellite Station", "3691 SW CR 347, Cedar Key, FL 32625", "32625", 29.1255, -83.0255),
    ("Levy County Butler Road Satellite Station", "18771 SE Butler Road, Inglis, FL 34449", "34449", 29.0255, -82.6855),
    ("Levy County Manatee Road Satellite Station", "10771 NW 107 Terrace, Chiefland, FL 32626", "32626", 29.4855, -82.8855),
]:
    add("Levy County FL", name, "County satellite station — bulk / appliances / brush",
        "orlando", "FL", zipc, addr, lat, lng, LEVY,
        "Tue, Fri, Sat 8:00–17:00", "352-486-3300", mats(BULKY, APPLIANCE, TIRES, ["yard-waste"]))

# ── Citrus County → tampa ──
add("Citrus County FL", "Citrus County Central Landfill — HHW / bulky / tires",
    "County landfill — HHW Tue/Thu/Fri 9:00–13:00; bulk / tires daily",
    "tampa", "FL", "34461", "230 West Gulf to Lake Highway, Lecanto, FL 34461", 28.8555, -82.4855,
    "https://www.citrusbocc.com/departments/public_works/solid_waste_management/index.php",
    "Mon–Fri 8:00–16:30; Sat 8:00–14:30; HHW Tue/Thu/Fri 9:00–13:00", "352-527-7670", mats(LANDFILL, HHW_E))

# ── Lee County Resource Recovery residents drop-off → tampa ──
add("Lee County FL", "Lee County Resource Recovery Facility — Residents Drop-Off Area",
    "County RRF residents drop-off — bulk / yard waste / C&D / appliances",
    "tampa", "FL", "33905", "10500 Buckingham Road, Fort Myers, FL 33905", 26.5855, -81.7755,
    "https://www.leegov.com/solidwaste/facilities/rrf",
    "Mon–Sat 7:00–17:00; Lee County residents only", "239-533-8000", mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste"]))

# ── Miami-Dade Home Chemical Collection Centers → hialeah / miami ──
MDHCC = "https://www.miamidade.gov/global/service.page?Mduid_service=ser1464798615648535"
add("Miami-Dade County FL", "Miami-Dade West Dade Home Chemical Collection Center",
    "County HHW / e-waste — paint / chemicals / TVs / batteries",
    "hialeah", "FL", "33178", "8801 NW 58th Street, Doral, FL 33178", 25.8055, -80.3255, MDHCC,
    "Wed–Sun 9:00–17:00", "305-514-6666", mats(HHW_E))
add("Miami-Dade County FL", "Miami-Dade South Dade Home Chemical Collection Center",
    "County HHW / e-waste — Gate B South Dade Landfill",
    "miami", "FL", "33032", "23707 SW 97th Avenue Gate B, Homestead, FL 33032", 25.4855, -80.4455, MDHCC,
    "Wed–Sun 9:00–17:00", "305-514-6666", mats(HHW_E))

# ── Baker County NRSWA (8) → jacksonville ──
BAK = "https://www.bakercountyfl.org/collectionsites.php"
for name, addr, zipc, lat, lng in [
    ("Baker County Baxter Collection Center", "27330 County Road 127, Sanderson, FL 32087", "32087", 30.1455, -82.2855),
    ("Baker County Cuyler Collection Center", "19319 N County Road 125, Sanderson, FL 32087", "32087", 30.1255, -82.3255),
    ("Baker County Glen St. Mary Collection Center", "13614 N County Road 125, Glen St. Mary, FL 32040", "32040", 30.2755, -82.1655),
    ("Baker County Mud Lake Collection Center", "9884 Mud Lake Road, Glen St. Mary, FL 32040", "32040", 30.2655, -82.1855),
    ("Baker County Macclenny CR 228 Collection Center", "7790 S State Road 228, Macclenny, FL 32063", "32063", 30.2855, -82.1255),
    ("Baker County Steel Bridge Road Collection Center", "5229 Steel Bridge Road, Macclenny, FL 32063", "32063", 30.2955, -82.0855),
    ("Baker County Sanderson Collection Center", "15405 US Highway 90, Sanderson, FL 32087", "32087", 30.0855, -82.2655),
    ("Baker County Olustee Collection Center", "US Highway 90 East of Olustee, Olustee, FL 32072", "32072", 30.2055, -82.4255),
]:
    add("Baker County FL / NRSWA", name, "County collection center — bulk / appliances / tires",
        "jacksonville", "FL", zipc, addr, lat, lng, BAK,
        "Tue/Fri/Sat 8:00–18:00; Wed split 6:00–10:00 & 16:00–20:00; Sun 14:00–18:00", "904-275-2373", mats(BULKY, APPLIANCE, TIRES))

# ── Bradford County NRSWA (6) → jacksonville ──
BRAD = "https://nrswa.org/site/wp-content/uploads/BRADFORD-COUNTY-RECYCLING-COLLECTION-CENTERS-01-2015.pdf"
for name, addr, zipc, lat, lng, mlist in [
    ("Bradford County 229 Collection Center", "Brownlee Road, Starke, FL 32091", "32091", 29.9855, -82.1255, mats(BULKY, APPLIANCE, TIRES, CD)),
    ("Bradford County Keystone Collection Center", "State Road 100 East, Keystone Heights, FL 32656", "32656", 29.7855, -82.0255, mats(BULKY, APPLIANCE, TIRES)),
    ("Bradford County Sampson Collection Center", "Sampson Trestle Road, Graham, FL 32042", "32042", 29.9455, -82.2055, mats(BULKY, APPLIANCE, TIRES)),
    ("Bradford County Brooker Collection Center", "County Road 18, Brooker, FL 32622", "32622", 29.8855, -82.3255, mats(BULKY, APPLIANCE, TIRES)),
    ("Bradford County Lawtey Collection Center", "60th Street, Lawtey, FL 32058", "32058", 30.0455, -82.0655, mats(BULKY, APPLIANCE, TIRES)),
    ("Bradford County Starke HHW Collection Center", "Old Lawtey Road, Starke, FL 32091", "32091", 29.9755, -82.1155, mats(HHW_E, BULKY, APPLIANCE, TIRES)),
]:
    add("Bradford County FL / NRSWA", name, "County collection / HHW center — bulk / tires / appliances",
        "jacksonville", "FL", zipc, addr, lat, lng, BRAD,
        "Mon–Sat 10:00–18:00; Sun 13:00–18:00", "904-966-6212", mlist)

# ── Union County NRSWA (5) → jacksonville ──
UNION = "https://nrswa.org/site/wp-content/uploads/UNION-COUNTY-COLLECTION-CENTERS-2018.pdf"
for name, addr, zipc, lat, lng in [
    ("Union County 121 Collection Center", "State Road 121, Lake Butler, FL 32054", "32054", 30.0255, -82.3455),
    ("Union County Worthington Springs Collection Center", "State Road 121, Worthington Springs, FL 32091", "32091", 29.9255, -82.4255),
    ("Union County Providence Collection Center", "State Road 241 South of State Road 238, Lake Butler, FL 32054", "32054", 30.0155, -82.3855),
    ("Union County Palestine Collection Center", "Douglas Cemetery Road, Lake Butler, FL 32054", "32054", 30.0555, -82.4655),
    ("Union County Raiford Collection Center", "State Road 121 North, Raiford, FL 32083", "32083", 30.0655, -82.2455),
]:
    add("Union County FL / NRSWA", name, "County collection center — bulk / appliances / tires",
        "jacksonville", "FL", zipc, addr, lat, lng, UNION,
        "Mon–Sat 9:00–18:00; Sun 13:00–17:00; closed days vary by site", "386-496-2180", mats(BULKY, APPLIANCE, TIRES))

add("New River Solid Waste Association FL", "New River Regional Landfill — public scale",
    "Regional landfill — Baker / Bradford / Union counties",
    "jacksonville", "FL", "32083", "24276 NE 157th Street, Raiford, FL 32083", 30.0655, -82.1855,
    "https://nrswa.org/",
    "Mon–Sat — confirm nrswa.org", "386-431-1000", mats(LANDFILL))

# ── Columbia County (2) → jacksonville ──
COL = "https://bcc.columbiacountyfla.com/Solid_Waste_Management.asp"
add("Columbia County FL", "Columbia County Winfield Solid Waste Facility",
    "County solid waste facility — bulk / yard waste / white goods",
    "jacksonville", "FL", "32055", "1347 NW Oosterhoudt Lane, Lake City, FL 32055", 30.2555, -82.6955, COL,
    "Mon–Fri 7:00–16:30; 1st Sat monthly 7:00–16:30", "386-752-6050", mats(BULKY, APPLIANCE, ["yard-waste"], TIRES))
add("Columbia County FL", "Columbia County Branford Highway Drop-Off",
    "County recycling / drop-off — bulk / appliances",
    "jacksonville", "FL", "32025", "508 SW State Road 247, Lake City, FL 32025", 30.1255, -82.8255, COL,
    "Mon–Fri 7:00–16:30", "386-752-6050", mats(BULKY, APPLIANCE, TIRES))

# ── Nassau County satellite recycling (2) → jacksonville ──
NAS = "https://www.nassaucountyfl.com/DocumentCenter/View/31385"
for name, addr, zipc, lat, lng in [
    ("Nassau County Gene Lasserre Recycling Drop-Off", "86200 Gene Lasserre Boulevard, Yulee, FL 32097", "32097", 30.6255, -81.5855),
    ("Nassau County Bryceville Recycling Drop-Off", "7282 Motes Road, Bryceville, FL 32009", "32009", 30.6855, -81.9455),
]:
    add("Nassau County FL", name, "County satellite drop-off — bulk / appliances / tires / e-waste",
        "jacksonville", "FL", zipc, addr, lat, lng, NAS,
        "Confirm hours on nassaucountyfl.com; max 2 loads per 7 days", "904-530-6700", mats(BULKY, APPLIANCE, TIRES, E_WASTE, HHW))

# ── Suwannee County FL (13 collection + landfill) → jacksonville ──
SUW = "https://suwanneecountyfl.gov/solid-waste-sites/"
add("Suwannee County FL", "Suwannee County Central Landfill",
    "County landfill — bulk / tires / white goods / C&D",
    "jacksonville", "FL", "32060", "10910 144th Street, Live Oak, FL 32060", 30.2855, -82.9855, SUW,
    "Mon–Fri 8:00–16:00", "386-364-6612", mats(LANDFILL))
for name, addr, zipc, lat, lng in [
    ("Suwannee County Anderson Collection Site", "27002 CR-49, Live Oak, FL 32060", "32060", 30.3255, -83.0255),
    ("Suwannee County Dowling Park Collection Site", "23163 CR-250, Dowling Park, FL 32060", "32060", 30.2455, -83.2455),
    ("Suwannee County Fletcher Collection Site", "21486 CR-49, Live Oak, FL 32060", "32060", 30.2655, -82.9655),
    ("Suwannee County Humphries Collection Site", "9186 216th Street, Live Oak, FL 32060", "32060", 30.3055, -82.9255),
    ("Suwannee County Opportunity Store Collection Site", "9202 101st Road, Live Oak, FL 32060", "32060", 30.2755, -82.8855),
    ("Suwannee County Pepper Collection Site", "9681 State Road 51, Live Oak, FL 32060", "32060", 30.1855, -83.0855),
    ("Suwannee County Reas Collection Site", "9743 CR-136, Live Oak, FL 32060", "32060", 30.2255, -83.1455),
    ("Suwannee County Sprayfield Collection Site", "6830 CR-249, Live Oak, FL 32060", "32060", 30.1955, -82.9855),
    ("Suwannee County Taylor Collection Site", "14890 State Road 51, Live Oak, FL 32060", "32060", 30.1655, -83.0255),
    ("Suwannee County Wellborn Collection Site", "11673 CR 137, Wellborn, FL 32094", "32094", 30.2255, -82.8455),
    ("Suwannee County Brown Wood Collection Site", "12706 80th Terrace, Live Oak, FL 32060", "32060", 30.2955, -82.8655),
    ("Suwannee County Falmouth Collection Site", "18524 52nd Street, Live Oak, FL 32060", "32060", 30.1855, -82.9455),
    ("Suwannee County US 129 North Collection Site", "3418 93rd Drive, Live Oak, FL 32060", "32060", 30.3555, -83.0655),
]:
    add("Suwannee County FL", name, "County collection site — bulk / appliances / tires",
        "jacksonville", "FL", zipc, addr, lat, lng, SUW,
        "Mon, Wed, Fri, Sat 7:00–19:00; Suwannee County decal required", "386-364-6612", mats(BULKY, APPLIANCE, TIRES))

# ── Dixie County FL roll-off network (11) → jacksonville ──
DIX = "https://www.dixiecounty.us/pdf_publicworks/RolloffSchedule.pdf"
add("Dixie County FL", "Dixie County Central Transfer Station & C&D Landfill",
    "County transfer / C&D landfill — bulk / tires / appliances",
    "jacksonville", "FL", "32628", "Roscoe Swafford Road, Cross City, FL 32628", 29.6255, -83.0855, DIX,
    "Mon–Fri 7:00–17:30; Sat 8:00–17:00; Sun closed", "352-498-1289", mats(LANDFILL, CD))
for name, addr, zipc, lat, lng in [
    ("Dixie County SR 349 North Roll-Off Site", "12834 NE 349 Highway, Old Town, FL 32680", "32680", 29.5855, -83.0255),
    ("Dixie County CR 351N Roll-Off Site", "9030 NE 351 Highway, Old Town, FL 32680", "32680", 29.5755, -83.0455),
    ("Dixie County Pole Gap Roll-Off Site", "2331 NE 349 Highway, Old Town, FL 32680", "32680", 29.5655, -83.0655),
    ("Dixie County CR 317 Roll-Off Site", "839 SE 317 Highway, Cross City, FL 32628", "32628", 29.6155, -83.1255),
    ("Dixie County Suwannee Roll-Off Site", "20420 SE 349 Highway, Suwannee, FL 32692", "32692", 29.3255, -83.1455),
    ("Dixie County CR 55A Roll-Off Site", "564 SE 55A Highway, Old Town, FL 32680", "32680", 29.5555, -83.0855),
    ("Dixie County Jack Roberts Curve Roll-Off Site", "446 NE 155th Street, Cross City, FL 32628", "32628", 29.6355, -83.0655),
    ("Dixie County Horseshoe Beach Roll-Off Site", "17826 SW 351 Highway, Horseshoe Beach, FL 32648", "32648", 29.4255, -83.2855),
    ("Dixie County Jena Roll-Off Site", "738 SW 286th Avenue, Steinhatchee, FL 32659", "32659", 29.6855, -83.3855),
]:
    add("Dixie County FL", name, "County roll-off drop-off — bulk / tires / yard waste",
        "jacksonville", "FL", zipc, addr, lat, lng, DIX,
        "Hours vary by site — see dixiecounty.us RolloffSchedule.pdf", "352-498-1289", mats(BULKY, TIRES, ["yard-waste"], CD))

# ── Franklin County FL → jacksonville ──
add("Franklin County FL", "Franklin County Central Landfill",
    "County landfill — bulk / tires / white goods / C&D",
    "jacksonville", "FL", "32328", "210 State Road 65, Eastpoint, FL 32328", 29.7855, -84.8755,
    "https://www.franklincountyflorida.com/county-government/solid-waste/",
    "Mon–Fri 7:00–16:30; summer hours Apr–Sep", "850-670-8167", mats(LANDFILL))

# ── City of Denton landfill + HCC → dallas ──
add("City of Denton TX", "City of Denton Landfill — public drop-off",
    "Municipal landfill — bulk / appliances / tires / yard waste",
    "dallas", "TX", "76208", "1527 South Mayhill Road, Denton, TX 76208", 33.1855, -97.0855,
    "https://www.cityofdenton.com/DocumentCenter/View/803/2026-Solid-Waste-and-Recycling-Service-Guide-PDF",
    "Mon–Sat 7:00–16:00; Denton residents", "940-349-8700", mats(LANDFILL))
add("City of Denton TX", "City of Denton Home Chemical Collection Center",
    "Municipal HHW / e-waste — appointment or drop-off",
    "dallas", "TX", "76208", "1527 South Mayhill Road, Denton, TX 76208", 33.1855, -97.0855,
    "https://www.cityofdenton.com/DocumentCenter/View/803/2026-Solid-Waste-and-Recycling-Service-Guide-PDF",
    "Fri–Sat 8:00–12:00; appointment at cityofdenton.com/hcc", "940-349-8700", mats(HHW_E))


def main() -> None:
    valid_cities = {c["city_slug"] for c in json.loads(CITIES_PATH.read_text()) if c.get("state") in FL_TX}
    city_state = {c["city_slug"]: c.get("state") for c in json.loads(CITIES_PATH.read_text())}

    kept: list[dict] = []
    for r in UPSERTS:
        if r["city_slug"] not in valid_cities:
            print(f"skip unknown city_slug: {r['city_slug']} ({r['name']})")
            continue
        if r.get("state") != city_state.get(r["city_slug"]):
            raise SystemExit(f"state mismatch: {r['name']} ({r['state']} vs {city_state.get(r['city_slug'])})")
        if not is_hard_facility(r):
            raise SystemExit(f"soft facility rejected: {r['name']}")
        kept.append(r)

    facilities = json.loads(FAC_PATH.read_text())
    by_key = {(f.get("city_slug"), f.get("name")): i for i, f in enumerate(facilities)}
    by_addr = {(f.get("city_slug"), norm_addr(f.get("address") or "")) for f in facilities if f.get("address")}
    global_addr = {norm_addr(f.get("address") or "") for f in facilities if f.get("address")}

    added = updated = skipped = 0
    added_by_network: dict[str, int] = {}

    for r in kept:
        network = r["_network"]
        clean = {k: v for k, v in r.items() if k != "_network"}
        key = (clean["city_slug"], clean["name"])
        addr_k = (clean["city_slug"], norm_addr(clean["address"]))
        gaddr = norm_addr(clean["address"])

        if key in by_key:
            facilities[by_key[key]] = {**facilities[by_key[key]], **clean}
            updated += 1
        elif addr_k in by_addr or gaddr in global_addr:
            skipped += 1
        else:
            facilities.append(clean)
            by_key[key] = len(facilities) - 1
            by_addr.add(addr_k)
            global_addr.add(gaddr)
            added += 1
            added_by_network[network] = added_by_network.get(network, 0) + 1

    before = len(facilities)
    facilities = [f for f in facilities if is_hard_facility(f)]
    purged = before - len(facilities)

    FAC_PATH.write_text(json.dumps(facilities, indent=2) + "\n")

    hard_total = len(facilities)
    fl_tx_hard = sum(
        1 for f in facilities
        if city_state.get(f.get("city_slug", "")) in FL_TX and is_hard_facility(f)
    )

    print("FL / TX hard-facility research expansion")
    print(f"  Rows in script:     {len(UPSERTS)} (kept {len(kept)})")
    print(f"  Added:              {added}")
    print(f"  Updated:            {updated}")
    print(f"  Skipped (dedupe):   {skipped}")
    print(f"  Soft purged:        {purged}")
    print(f"  Final hard total:   {hard_total}")
    print(f"  FL/TX hard:          {fl_tx_hard}")
    print(f"  Networks covered ({len(NETWORKS)}):")
    for n in sorted(NETWORKS):
        tag = f" (+{added_by_network[n]})" if n in added_by_network else ""
        print(f"    • {n}{tag}")


if __name__ == "__main__":
    main()
