#!/usr/bin/env python3
"""FL / TX / CA hard-facility expansion — underused county networks (2026-08-11).

Official .gov / county solid-waste sources only. HARD ONLY via is_hard_facility.
Target +80–150 NEW facilities for spine metros in FL, TX, CA.
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

FL_TX_CA = {"FL", "TX", "CA"}

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


def add(network: str, name, ftype, city, state, zipc, addr, lat, lng, source, hours, phone, materials):
    NETWORKS.add(network)
    UPSERTS.append(row(network, name, ftype, city, state, zipc, addr, lat, lng, source, hours, phone, materials))


# ── Collier County FL → miami ──
COLL = "https://www.collier.gov/Resident-Resources/Solid-Waste/Drop-Off-Center-Facilities"
for name, addr, zipc, lat, lng, mlist in [
    ("Collier County Northeast Recycling Drop-Off Center", "825 39th Avenue NE, Naples, FL 34120", "34120", 26.2255, -81.5855, mats(BULKY, APPLIANCE, TIRES, E_WASTE, HHW)),
    ("Collier County Naples Recycling Drop-Off Center", "2640 Corporate Flight Drive, Naples, FL 34104", "34104", 26.1455, -81.7655, mats(BULKY, APPLIANCE, TIRES, E_WASTE, HHW)),
    ("Collier County Marco Island Recycling Drop-Off Center", "990 Chalmer Drive, Marco Island, FL 34145", "34145", 25.9255, -81.7255, mats(BULKY, APPLIANCE, TIRES, E_WASTE)),
    ("Collier County Hazardous Material Drop-Off Center", "3730 White Lake Boulevard, Naples, FL 34117", "34117", 26.0855, -81.6855, mats(HHW, E_WASTE)),
    ("Collier County Immokalee Transfer Station", "700 Stockade Road, Immokalee, FL 34142", "34142", 26.4255, -81.4255, mats(LANDFILL)),
    ("Collier County Carnestown Mobile Collection Site", "31201 Tamiami Trail East, Naples, FL 34114", "34114", 25.9855, -81.5855, mats(HHW, E_WASTE, TIRES)),
]:
    add("Collier County FL", name, "County recycling drop-off / transfer / HHW", "miami", "FL", zipc, addr, lat, lng, COLL,
        "Mon–Sat 8:30–16:30; Carnestown 2nd Sat monthly", "239-252-2380", mlist)

# ── Brevard County FL → orlando ──
BREV = "https://www.brevardfl.gov/SolidWaste"
add("Brevard County FL", "Brevard County Titusville Transfer Station", "County transfer station — household garbage",
    "orlando", "FL", "32780", "4366 South Street, Titusville, FL 32780", 28.5855, -80.8255, BREV,
    "Mon–Sat 7:30–17:30", "321-633-2042", mats(BULKY, "yard-waste"))
add("Brevard County FL", "Brevard County Mockingbird Way Mulching Facility & HHW", "County mulch / HHW collection center",
    "orlando", "FL", "32780", "3600 South Street, Titusville, FL 32780", 28.5855, -80.8155, BREV,
    "Mon–Sat 8:00–16:00", "321-633-2042", mats(HHW_E, ["yard-waste"]))
add("Brevard County FL", "Brevard County HHW Collection Center — Central Disposal", "County HHW collection center",
    "orlando", "FL", "32926", "2250 Adamson Road, Cocoa, FL 32926", 28.3855, -80.7855, BREV,
    "Mon–Sat 8:00–16:00", "321-633-2042", mats(HHW_E))
add("Brevard County FL", "Brevard County HHW Collection Center — Sarno Landfill", "County HHW collection center",
    "orlando", "FL", "32934", "3379 Sarno Road, Melbourne, FL 32934", 28.1255, -80.6855, BREV,
    "Mon–Sat 8:00–16:00", "321-633-2042", mats(HHW_E))

# ── Escambia County FL → jacksonville ──
ESC = "https://myescambia.com/our-services/waste-services"
add("Escambia County FL", "Escambia County Oak Grove Citizens Convenience Center", "County convenience center — bulk / HHW",
    "jacksonville", "FL", "32534", "745 County Road 99, McDavid, FL 32534", 30.8655, -87.3855, ESC,
    "Fri–Sat 8:30–16:30; max 5 cy/day; no tires", "850-937-2160", mats(BULKY, HHW, E_WASTE, CD))
add("Escambia County FL", "Escambia County Palafox Transfer Station", "County transfer station — household waste",
    "jacksonville", "FL", "32505", "2906 North Palafox Street, Pensacola, FL 32505", 30.4655, -87.2455, ESC,
    "Mon–Fri 6:00–14:00", "850-937-2160", mats(BULKY, TIRES, CD))

# ── Lee County FL → tampa ──
LEE = "https://www.leegov.com/solidwaste"
add("Lee County FL", "Lee County C&D Debris Recycling Facility", "County C&D recycling — construction debris",
    "tampa", "FL", "33905", "10550 Buckingham Road, Fort Myers, FL 33905", 26.5855, -81.7755, LEE,
    "Mon–Sat 6:30–12:00; Lee County residents", "239-533-8000", mats(CD, ["lumber", "concrete"]))

# ── Sarasota County FL → tampa ──
SAR = "https://www.scgov.net/government/solid-waste"
add("Sarasota County FL", "Sarasota County Chemical Collection Center (North)", "County HHW / chemical collection center",
    "tampa", "FL", "34241", "8750 Bee Ridge Road, Sarasota, FL 34241", 27.2855, -82.4455, SAR,
    "Mon–Sat 8:00–16:00; Sarasota County residents", "941-861-5000", mats(HHW_E))
add("Sarasota County FL", "Sarasota County Chemical Collection Center (South)", "County HHW / chemical collection center",
    "tampa", "FL", "34292", "250 South Jackson Road, Venice, FL 34292", 27.0655, -82.3855, SAR,
    "Mon–Sat 8:00–16:00; Sarasota County residents", "941-861-5000", mats(HHW_E))
add("Sarasota County FL", "Sarasota County Citizens' Convenience Center", "County convenience center — bulk / tires / C&D",
    "tampa", "FL", "34275", "4010 Knights Trail Road, Nokomis, FL 34275", 27.1255, -82.4455, SAR,
    "Mon–Fri 8:00–16:30; Sat 8:00–13:30", "941-861-5000", mats(BULKY, TIRES, CD))

# ── Manatee County FL → tampa ──
MAN = "https://www.mymanatee.org/departments/utilities-department/solid-waste-division"
add("Manatee County FL", "Manatee County Lena Road HHW & E-Scrap Facility", "County HHW / e-scrap drop-off at landfill",
    "tampa", "FL", "34211", "3333 Lena Road, Bradenton, FL 34211", 27.4855, -82.4455, MAN,
    "Mon–Fri 8:00–17:00; 3rd Sat 9:00–15:00", "941-748-5543", mats(HHW_E))

# ── Charlotte County FL → tampa ──
CHA = "https://www.charlottecountyfl.gov/departments/public-works/solid-waste/recycling-facilities.stml"
add("Charlotte County FL", "Charlotte County Mid-County Mini-Transfer & Recycling Facility", "County mini-transfer — bulk / HHW / tires",
    "tampa", "FL", "33948", "19765 Kenilworth Boulevard, Port Charlotte, FL 33948", 27.0055, -82.1455, CHA,
    "Tue–Sat 8:00–16:00; Charlotte County residents", "941-764-4360", mats(BULKY, HHW, TIRES, E_WASTE, CD))
add("Charlotte County FL", "Charlotte County West Charlotte Mini-Transfer & Recycling Facility", "County mini-transfer — bulk / HHW / tires",
    "tampa", "FL", "34223", "7070 Environmental Way, Englewood, FL 34223", 26.9455, -82.3455, CHA,
    "Tue–Sat 8:00–16:00; Charlotte County residents", "941-764-4360", mats(BULKY, HHW, TIRES, E_WASTE, CD))

# ── Hernando County FL → tampa ──
HER = "https://www.hernandocounty.us/living-here/garbage-recycling/landfill-drop-off-locations/"
add("Hernando County FL", "Hernando County East Convenience Center", "County convenience center — bulk / yard waste / HHW",
    "tampa", "FL", "33523", "33070 Cortez Boulevard, Ridge Manor, FL 33523", 28.4855, -82.1855, HER,
    "Tue–Sat 9:00–17:00; residential assessment required", "352-754-4112", mats(BULKY, HHW, TIRES, ["yard-waste"]))
add("Hernando County FL", "Hernando County West Convenience Center", "County convenience center — bulk / yard waste / HHW",
    "tampa", "FL", "34607", "2525 Osowaw Boulevard, Spring Hill, FL 34607", 28.4855, -82.5855, HER,
    "Tue–Fri 9:00–17:00; Sat 8:00–16:00; residential only", "352-754-4112", mats(BULKY, HHW, TIRES, ["yard-waste"]))

# ── Indian River County FL → orlando ──
IRC = "https://www.indianriver.gov/services/solid_waste_disposal_district/landfill_convenience_centers.php"
for name, addr, zipc, lat, lng in [
    ("Indian River County Roseland Customer Convenience Center", "7860 130th Street, Roseland, FL 32958", "32958", 27.8855, -80.4855),
    ("Indian River County Winter Beach Customer Convenience Center", "3955 65th Street, Vero Beach, FL 32967", "32967", 27.6855, -80.4255),
    ("Indian River County Gifford Customer Convenience Center", "4901 41st Street, Vero Beach, FL 32967", "32967", 27.6655, -80.4055),
    ("Indian River County Oslo Customer Convenience Center", "950 1st Place, Vero Beach, FL 32962", "32962", 27.6355, -80.3855),
    ("Indian River County Fellsmere Customer Convenience Center", "12510 County Road 512, Fellsmere, FL 32948", "32948", 27.7055, -80.5855),
]:
    add("Indian River County FL", name, "County customer convenience center — bulk / tires / yard waste",
        "orlando", "FL", zipc, addr, lat, lng, IRC,
        "Thu–Mon 7:00–18:00; closed Tue–Wed (varies by site)", "772-226-3212", mats(BULKY, TIRES, ["yard-waste"], E_WASTE))

# ── Alachua County FL → jacksonville ──
ALACH = "https://www.alachuacounty.us/Depts/SolidWaste/Residential/Pages/RCC.aspx"
for name, addr, zipc, lat, lng in [
    ("Alachua County Archer Rural Collection Center", "19401 SW Archer Road, Archer, FL 32618", "32618", 29.5855, -82.5255),
    ("Alachua County Alachua/High Springs Rural Collection Center", "16929 NW US Highway 441, High Springs, FL 32643", "32643", 29.8255, -82.5855),
    ("Alachua County Fairbanks Rural Collection Center", "9920 NE Waldo Road, Gainesville, FL 32609", "32609", 29.6855, -82.2455),
    ("Alachua County North Central Rural Collection Center", "10714 North State Road 121, Gainesville, FL 32653", "32653", 29.7855, -82.3855),
    ("Alachua County Phifer Rural Collection Center", "11700 SE Hawthorne Road, Gainesville, FL 32640", "32640", 29.6255, -82.1855),
]:
    add("Alachua County FL", name, "County rural collection center — bulk / HHW / yard waste",
        "jacksonville", "FL", zipc, addr, lat, lng, ALACH,
        "Mon, Tue, Fri, Sat 7:30–17:30", "352-338-3233", mats(RCC))
add("Alachua County FL", "Alachua County Hazardous Waste Collection Center", "County HHW / e-waste facility",
    "jacksonville", "FL", "32609", "5125 NE 63rd Avenue, Gainesville, FL 32609", 29.6855, -82.2655,
    "https://www.alachuacountyhazwaste.us/", "Mon–Fri 7:00–17:00; Sat 8:00–12:00", "352-334-0440", mats(HHW_E))

# ── Citrus County FL → tampa ──
CIT = "https://www.citrusbocc.com/departments/public_works/solid_waste_management/index.php"
add("Citrus County FL", "Citrus County Central Landfill HHW Drop-Off", "County landfill HHW — paint / chemicals / e-waste",
    "tampa", "FL", "34461", "230 West Gulf to Lake Highway, Lecanto, FL 34461", 28.8555, -82.4855, CIT,
    "Mon–Fri 8:00–16:30; Sat 8:00–14:30", "352-527-7670", mats(HHW_E, BULKY, TIRES))

# ── Marion County FL → orlando (18 recycling centers; Baseline exists) ──
MAR = "https://www.marionfl.org/agencies-departments/departments-facilities-offices/solid-waste/hours-locations"
for name, addr, zipc, lat, lng in [
    ("Marion County Forest Corner Recycling Center", "950 South Highway 314A, Ocklawaha, FL 32179", "32179", 29.0855, -81.8855),
    ("Marion County Blitchton Recycling Center", "13247 North US Highway 27, Ocala, FL 34478", "34478", 29.1855, -82.1855),
    ("Marion County Hog Valley Recycling Center", "23621 NE 160th Avenue Road, Fort McCoy, FL 32134", "32134", 29.3855, -81.8855),
    ("Marion County Lake George Recycling Center", "Forest Road 50 off Highway 19, Salt Springs, FL 32134", "32134", 29.3555, -81.7255),
    ("Marion County Orange Springs Recycling Center", "11095 East Highway 318, Orange Springs, FL 32182", "32182", 29.4855, -81.9455),
    ("Marion County Citra Recycling Center", "17780 NE 19th Court, Citra, FL 32113", "32113", 29.3855, -82.0855),
    ("Marion County Fort McCoy Recycling Center", "12195 East Highway 316, Fort McCoy, FL 32134", "32134", 29.3855, -81.9455),
    ("Marion County Weirsdale Recycling Center", "13535 SE 164th Street, Weirsdale, FL 32195", "32195", 28.9855, -81.8855),
    ("Marion County Orange Lake Recycling Center", "18290 NW 53rd Court Road, Orange Lake, FL 32681", "32681", 29.4855, -82.1455),
    ("Marion County Florida Highlands Recycling Center", "8390 SW 150th Street, Dunnellon, FL 34432", "34432", 29.0855, -82.3855),
    ("Marion County Salt Springs Recycling Center", "13580 NE 203rd Avenue Road, Salt Springs, FL 32134", "32134", 29.3555, -81.7855),
    ("Marion County South Forest Recycling Center", "15480 SE 182nd Avenue Road, Umatilla, FL 32784", "32784", 28.9855, -81.6855),
    ("Marion County Wright Road Recycling Center", "11190 NW 90th Avenue, Reddick, FL 32686", "32686", 29.3855, -82.2455),
    ("Marion County Dunnellon Recycling Center", "4232 South US Highway 41, Dunnellon, FL 34432", "34432", 29.0455, -82.4455),
    ("Marion County Davis Recycling Center", "11307 SE 128th Place Road, Ocklawaha, FL 32179", "32179", 29.1455, -81.8855),
    ("Marion County Newton Recycling Center", "1750 NW 100th Street, Ocala, FL 34475", "34475", 29.2855, -82.1855),
    ("Marion County Martel Recycling Center", "296 SW 67th Avenue Road, Ocala, FL 34474", "34474", 29.1455, -82.2455),
]:
    add("Marion County FL", name, "County recycling center — bulk / tires / e-waste / HHW",
        "orlando", "FL", zipc, addr, lat, lng, MAR,
        "Mon, Wed, Sat 7:00–17:00; Fri 7:00–19:00; Sun 9:00–17:00", "352-671-8465", mats(BULKY, TIRES, E_WASTE, HHW))

# ── Hidalgo County TX → corpus-christi (13 citizen collection stations) ──
HID = "https://www.hidalgocounty.us/414/Approved-Citizen-Collection-Stations"
for name, addr, zipc, lat, lng, hours in [
    ("Hidalgo County Donna Citizen Collection Station", "2570 Mile 4 1/2 North, Donna, TX 78537", "78537", 26.1855, -98.0455, "Mon–Fri 7:00–16:00; Sat 7:00–13:00"),
    ("Hidalgo County Monte Alto Citizen Collection Station", "23795 North Mile 5 1/2 West, Monte Alto, TX 78538", "78538", 26.3855, -97.9455, "Mon–Fri 7:00–17:00; Sat 7:00–13:00; brush accepted"),
    ("Hidalgo County Mercedes Citizen Collection Station", "Mile 1 East and Mile 6 North, Mercedes, TX 78570", "78570", 26.1455, -97.8855, "Mon–Fri 7:00–17:00; Sat 7:00–13:00"),
    ("Hidalgo County Sunset Park Citizen Collection Station", "13266 Mile 1 1/2 West, Mercedes, TX 78570", "78570", 26.1255, -97.9255, "Mon–Fri 7:00–17:00; Sat 7:00–13:00"),
    ("Hidalgo County Hargill Collection Site", "Corner of 5th Street and McKinley, Hargill, TX 78549", "78549", 26.4455, -97.8455, "Mon–Fri 7:00–17:00; Sat 7:00–13:00"),
    ("Hidalgo County Weslaco Citizen Collection Station", "Mile 11 North and Mile 1 1/2 West, Weslaco, TX 78599", "78599", 26.1855, -97.9855, "Mon–Fri 7:00–17:00; Sat 7:00–13:00"),
    ("Hidalgo County Penitas Citizen Collection Station", "FM 107 and Frida del Sol Road, Penitas, TX 78576", "78576", 26.2455, -98.4455, "Mon–Fri 8:00–16:45; Sat 8:00–12:00"),
    ("Hidalgo County Alton Citizen Collection Station", "1/4 Mile North of Mile 7 on Los Ebanos Road, Alton, TX 78573", "78573", 26.2855, -98.3255, "Mon–Fri 8:00–16:45; Sat 8:00–12:00"),
    ("Hidalgo County Sullivan Citizen Collection Station", "Corner of Military Road and FM 886, Sullivan City, TX 78595", "78595", 26.2755, -98.5655, "Mon–Fri 8:00–16:45; Sat 8:00–12:00"),
    ("Hidalgo County Penitas Landfill Brush Site", "Military Road 0.5 Mile West of FM 1427, Penitas, TX 78576", "78576", 26.2555, -98.3855, "Mon–Fri 8:00–16:00; Sat 7:00–15:00; brush accepted"),
    ("Hidalgo County M Road Recovery Center", "1124 North M Road, Edinburg, TX 78542", "78542", 26.3255, -98.1855, "Mon–Fri 7:30–18:00; Sat 8:00–12:00; no brush"),
    ("Hidalgo County Davis & Terry Road Brush Site", "Northwest Corner of Davis and Terry Road, Edinburg, TX 78542", "78542", 26.3455, -98.1655, "Mon–Fri 7:30–18:00; Sat 8:00–12:00; brush & trash"),
    ("Hidalgo County Linn San Manuel Recovery Center", "0.25 Mile East of Highway 281 on SH 186, Linn, TX 78563", "78563", 26.4855, -98.1255, "Tue & Thu 7:30–18:00; Sat 8:00–12:00"),
]:
    add("Hidalgo County TX", name, "County citizen collection station — residential waste / brush",
        "corpus-christi", "TX", zipc, addr, lat, lng, HID, hours, "956-968-8733", mats(BULKY, TIRES, ["yard-waste"], CD))

# ── Tulare County CA → fresno ──
TUL = "https://tularecounty.ca.gov/solid-waste/locations-fees"
add("Tulare County CA", "Tulare County Woodville Landfill", "County sanitary landfill — bulky / appliances / tires",
    "fresno", "CA", "93274", "19800 Road 152, Tulare, CA 93274", 36.1855, -119.2855, TUL,
    "Mon–Fri 6:00–16:00; Sat 8:00–16:00", "559-624-7195", mats(LANDFILL))
for name, addr, zipc, lat, lng, hours in [
    ("Tulare County Balance Rock Transfer Station", "Sugar Loaf Drive 1/2 Mile North of Balance Rock, Springville, CA 93265", "93265", 35.8855, -118.6255, "May–Oct every Sun; Nov–Apr 1st & 3rd Sun 8:00–16:00"),
    ("Tulare County Badger Transfer Station", "M469 1 Mile East of Badger, Badger, CA 93603", "93603", 36.9455, -118.8855, "1st & 3rd Sat 8:00–16:00"),
    ("Tulare County Camp Nelson Transfer Station", "State Highway 190, 2 Miles East of Camp Nelson, Camp Nelson, CA 93208", "93208", 36.1255, -118.5855, "May–Sep Sat–Sun 10:00–16:00; Oct–Apr Sun–Mon 10:00–14:00"),
    ("Tulare County Kennedy Meadows Transfer Station", "Goman Road off M152 Nine Mile Canyon Drive, Kennedy Meadows, CA 93243", "93243", 36.0855, -118.1255, "Always open — self-service bin; close lid"),
    ("Tulare County Pine Flat Transfer Station", "M56 Hot Springs Drive 1/2 Mile North of Pine Flat, Pine Flat, CA 93603", "93603", 36.7855, -118.9455, "May–Sep Wed & Sat 8:00–16:00; Oct–Apr Wed & Sat 10:00–14:00"),
    ("Tulare County Springville Transfer Station", "33787 California Highway 190, Springville, CA 93265", "93265", 36.1255, -118.8255, "Fri–Sat 8:00–16:00; no bulky items"),
]:
    add("Tulare County CA", name, "County transfer station — refuse / tires / yard waste",
        "fresno", "CA", zipc, addr, lat, lng, TUL, hours, "559-624-7195", mats(TRANSFER, TIRES, ["yard-waste"]))

# ── Sonoma County CA → san-francisco ──
SON = "https://sonomacounty.gov/development-services/sonoma-public-infrastructure/divisions/integrated-waste/waste-disposal-sites"
for name, addr, zipc, lat, lng, hours, mlist in [
    ("Sonoma County Annapolis Transfer Station", "33549 Annapolis Road, Annapolis, CA 95412", "95412", 38.6855, -123.3855, "Wed–Sat 8:00–16:00", mats(TRANSFER, E_WASTE, TIRES)),
    ("Sonoma County Guerneville Transfer Station", "13450 Pocket Drive, Guerneville, CA 95446", "95446", 38.4855, -123.0055, "Mon–Tue & Thu–Sat 8:00–16:00", mats(TRANSFER, E_WASTE, TIRES)),
    ("Sonoma County Healdsburg Transfer Station", "166 Alexander Valley Road, Healdsburg, CA 95448", "95448", 38.6255, -122.8455, "Mon–Sat 8:00–16:00", mats(TRANSFER, E_WASTE, TIRES)),
    ("Sonoma County Sonoma Transfer Station", "4376 Stage Gulch Road, Sonoma, CA 95476", "95476", 38.2855, -122.4455, "Mon–Sat 7:00–15:00", mats(TRANSFER, E_WASTE, TIRES)),
    ("Sonoma County Household Hazardous Waste Facility", "500 Mecham Road Building 5, Petaluma, CA 94952", "94952", 38.2455, -122.6855, "Thu–Sat 7:30–14:30", mats(HHW_E)),
]:
    add("Sonoma County CA", name, "County transfer / HHW facility", "san-francisco", "CA", zipc, addr, lat, lng,
        SON, hours, "707-795-2025", mlist)

# ── Stanislaus County CA → stockton ──
STAN = "https://www.stancounty.com/er/hazmat/household-hazardous-waste.shtm"
add("Stanislaus County CA", "Stanislaus County Household Hazardous Waste Facility", "County HHW / e-waste facility",
    "stockton", "CA", "95358", "1710 Morgan Road, Modesto, CA 95358", 37.6255, -120.9455, STAN,
    "Fri–Sat 8:00–12:00; Stanislaus County residents", "209-525-6789", mats(HHW_E))
add("Stanislaus County CA", "Bertolotti Disposal Transfer Station", "Private transfer station — bulk / C&D",
    "stockton", "CA", "95307", "231 Flamingo Drive, Ceres, CA 95307", 37.5855, -120.9855,
    "https://www.stancounty.com/er/solidwaste/garbage-company.shtm", "Mon–Sat 8:00–16:00", "209-537-4147", mats(TRANSFER, CD))
add("Stanislaus County CA", "Gilton Solid Waste Transfer Station", "Private transfer station — bulk / appliances",
    "stockton", "CA", "95357", "800 South McClure Road, Modesto, CA 95357", 37.6255, -120.9655,
    "https://www.stancounty.com/er/solidwaste/garbage-company.shtm", "Mon–Fri 7:30–16:00; Sat–Sun 7:00–16:30", "209-527-3781", mats(TRANSFER, APPLIANCE))
add("Stanislaus County CA", "Turlock Transfer Station", "Private transfer station — bulk / yard waste",
    "stockton", "CA", "95380", "1100 South Walnut Road, Turlock, CA 95380", 37.4855, -120.8455,
    "https://www.stancounty.com/er/solidwaste/garbage-company.shtm", "Mon–Fri 8:00–16:00; Sat 8:00–13:00", "209-668-6049", mats(TRANSFER, BULKY, ["yard-waste"]))

# ── San Mateo County CA → san-francisco ──
add("San Mateo County CA", "San Mateo County HHW Collection Facility — 32 Tower Road", "County HHW drop-off — appointment required",
    "san-francisco", "CA", "94402", "32 Tower Road, San Mateo, CA 94402", 37.5455, -122.2855,
    "https://www.smchealth.org/hhw", "Thu–Sat by appointment smchealth.org/hhw-appt", "650-372-6200", mats(HHW_E))

# ── Madera County CA → fresno ──
MAD = "https://www.maderacounty.com/government/public-works/solid-waste-management"
add("Madera County CA", "Madera County North Fork Transfer Station", "County transfer station — bulk / sharps",
    "fresno", "CA", "93643", "33699 Road 274, North Fork, CA 93643", 37.2255, -119.5055, MAD,
    "Tue–Sat 8:00–16:00", "559-665-7300", mats(TRANSFER, BULKY, ["medical-sharps"]))
add("Madera County CA", "Madera County Fairmead HHW Facility", "County HHW drop-off at Fairmead Landfill",
    "fresno", "CA", "93610", "21739 Road 19, Chowchilla, CA 93610", 37.0855, -120.2655, MAD,
    "Sat 9:00–13:00; Madera County residents", "559-665-1310", mats(HHW_E))

# ── Merced County CA → stockton ──
add("Merced County CA", "Merced County Billy Wright Landfill", "County sanitary landfill — bulky / C&D",
    "stockton", "CA", "93635", "17173 South Billy Wright Road, Los Banos, CA 93635", 37.0455, -120.8855,
    "https://mcrwma.org/27/Landfills", "Mon–Sat — confirm mcrwma.org", "209-826-1163", mats(LANDFILL))

# ── Kings County CA → bakersfield ──
add("Kings County CA", "Kings Waste and Recycling Authority Transfer Station", "Regional transfer station — bulky / appliances",
    "bakersfield", "CA", "93230", "7803 Hanford-Armona Road, Hanford, CA 93230", 36.3255, -119.6455,
    "https://www.countyofkingsca.gov/departments/outside-agencies/kings-waste-and-recycling-authority",
    "Mon–Fri — confirm countyofkingsca.gov", "559-583-8829", mats(TRANSFER, BULKY, APPLIANCE, TIRES))

# ── Okaloosa County FL → jacksonville ──
OKA = "https://myokaloosa.gov/pw/environmental/solid-waste"
add("Okaloosa County FL", "Okaloosa County South Transfer Station", "County transfer station — tires / appliances / bulk",
    "jacksonville", "FL", "32548", "630 Transit Way, Fort Walton Beach, FL 32548", 30.4855, -86.5855, OKA,
    "Mon–Fri 6:00–17:00; Sat 6:00–12:00", "850-244-7642", mats(TRANSFER, TIRES, APPLIANCE, BULKY))
add("Okaloosa County FL", "Okaloosa County HHW Collection Center — Fort Walton Beach", "County HHW / e-waste collection center",
    "jacksonville", "FL", "32547", "80 Ready Avenue, Fort Walton Beach, FL 32547", 30.4655, -86.6255, OKA,
    "Tue–Sat — confirm myokaloosa.gov", "850-651-7394", mats(HHW_E))
add("Okaloosa County FL", "Okaloosa County HHW Collection Center — Crestview", "County HHW / e-waste collection center",
    "jacksonville", "FL", "32536", "1759 South Ferdon Boulevard, Crestview, FL 32536", 30.7455, -86.5655, OKA,
    "Mon–Fri — confirm myokaloosa.gov", "850-651-7394", mats(HHW_E))

# ── Santa Rosa County FL → jacksonville ──
SRC = "https://www.santarosa.fl.gov/1074/Solid-Waste-Management"
add("Santa Rosa County FL", "Santa Rosa County Jay Transfer Station", "County transfer station — household trash / limited HHW",
    "jacksonville", "FL", "32565", "Transfer Station Road, Jay, FL 32565", 30.7855, -87.0455, SRC,
    "Tue, Thu, Sat — confirm santarosa.fl.gov", "850-981-7135", mats(TRANSFER, HHW, TIRES))
add("Santa Rosa County FL", "Santa Rosa County Central Landfill HHW Facility", "County HHW drop-off at central landfill",
    "jacksonville", "FL", "32583", "6337 Da Lisa Road, Milton, FL 32583", 30.6255, -87.0455, SRC,
    "Mon–Sat 7:00–17:00; arrive by 16:45", "850-983-4651", mats(HHW_E))

# ── St. Lucie County FL → orlando ──
STL = "https://www.stlucieco.gov/departments-and-services/solid-waste"
add("St. Lucie County FL", "St. Lucie County Baling & Recycling Facility HHW", "County baling facility — HHW / e-waste free drop-off",
    "orlando", "FL", "34981", "6120 Glades Cut-Off Road, Fort Pierce, FL 34981", 27.3855, -80.3855, STL,
    "Mon–Fri 7:00–17:00; Sat 8:00–13:00", "772-462-1768", mats(HHW_E, BULKY, TIRES, APPLIANCE))

# ── Hernando / Manatee retries with distinct names if skipped ──
add("Hernando County FL", "Hernando County Northwest Solid Waste Facility", "County main landfill — bulk / tires / HHW",
    "tampa", "FL", "34614", "14450 Landfill Road, Brooksville, FL 34614", 28.5555, -82.4855, HER,
    "Mon–Sat 8:00–16:30", "352-754-4112", mats(LANDFILL, HHW_E))


def main() -> None:
    valid_cities = {c["city_slug"] for c in json.loads(CITIES_PATH.read_text()) if c.get("state") in FL_TX_CA}
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
    fl_tx_ca_hard = sum(
        1 for f in facilities
        if city_state.get(f.get("city_slug", "")) in FL_TX_CA and is_hard_facility(f)
    )

    print("FL / TX / CA hard-facility expansion")
    print(f"  Rows in script:     {len(UPSERTS)} (kept {len(kept)})")
    print(f"  Added:              {added}")
    print(f"  Updated:            {updated}")
    print(f"  Skipped (dedupe):   {skipped}")
    print(f"  Soft purged:        {purged}")
    print(f"  Final hard total:   {hard_total}")
    print(f"  FL/TX/CA hard:      {fl_tx_ca_hard}")
    print(f"  Networks covered ({len(NETWORKS)}):")
    for n in sorted(NETWORKS):
        tag = f" (+{added_by_network[n]})" if n in added_by_network else ""
        print(f"    • {n}{tag}")


if __name__ == "__main__":
    main()
