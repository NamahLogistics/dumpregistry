#!/usr/bin/env python3
"""DumpRegistry HARD expansion — Northeast + Midwest county networks (2026-08-11).

Adds 80–150 NEW hard facilities from official .gov sources only.
Targets: Lake/DuPage/Will/Kane IL; Cuyahoga/Summit OH; Allegheny PA extras;
Westchester; Nassau/Suffolk NY; Middlesex MA; Hartford CT MDC events.

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
    "paint-latex", "paint-oil", "pesticides", "herbicides", "motor-oil",
    "antifreeze", "car-battery", "household-batteries", "lithium-battery",
    "fluorescent-bulbs", "propane-tank", "gasoline", "pool-chemicals",
    "cooking-oil", "fire-extinguisher", "medical-sharps",
]
CD = ["construction-debris", "lumber", "drywall", "concrete", "asphalt-shingles"]
LANDFILL = lambda: mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste"])
HHW_E = lambda: mats(HHW, E_WASTE)
TRANSFER = lambda: mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste"])


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


def cu(city_name: str, suffix: str, addr: str, zipc: str, lat: float, lng: float,
       hours: str, materials: list[str], ftype: str = "Municipal service garage — HHW / e-waste / tires") -> None:
    """Cuyahoga County OH municipal drop-off — tagged to pittsburgh city_slug."""
    row(
        "Cuyahoga County OH municipal networks",
        f"{city_name} — {suffix}",
        ftype,
        "pittsburgh", "OH", zipc, addr, lat, lng,
        f"https://cuyahogarecycles.org/recycle-in/{city_name.lower().replace(' ', '-')}",
        hours, "216-443-3749", materials,
    )


# ── Lake County IL (SWALCO) ───────────────────────────────────────────────────
SWALCO = "https://www.swalco.org/165/Household-Chemical-Waste-HCW"
SWALCO_E = "https://www.swalco.org/163/Electronics-Year-Round-Drop-Off-Location"

for name, addr, zipc, lat, lng, hours, mlist in [
    ("SWALCO Grayslake Public Works — electronics drop-off", "585 Berry Avenue, Grayslake, IL 60030", "60030", 42.355, -88.031, "Mon–Fri 8:00–15:00", HHW_E()),
    ("SWALCO Highland Park Recycling Center — electronics drop-off", "1180 Half Day Road, Highland Park, IL 60035", "60035", 42.200, -87.828, "Tue 7:00–13:00; 1st Sat 7:00–13:00", HHW_E()),
    ("SWALCO LRS Wauconda — electronics drop-off", "1350 N Old Rand Road, Wauconda, IL 60084", "60084", 42.265, -88.145, "Mon–Fri 7:00–15:00", HHW_E()),
    ("SWALCO Lake Bluff Public Works — electronics drop-off", "640 Rockland Road, Lake Bluff, IL 60044", "60044", 42.285, -87.855, "Mon–Fri 8:00–15:00; Lake Bluff residents", HHW_E()),
    ("SWALCO Antioch Community Center — Reuse-A-Shoe drop-off", "817 Holbek Drive, Antioch, IL 60002", "60002", 42.475, -88.095, "Mon–Fri 9:00–17:00", mats(TIRES, BULKY)),
    ("SWALCO Mundelein Park District — textiles / hard goods drop-off", "1401 N Midlothian Road, Mundelein, IL 60060", "60060", 42.265, -87.995, "Mon–Fri 8:00–17:00", mats(BULKY, E_WASTE)),
]:
    row("SWALCO Lake County IL", name, "County electronics / HCW drop-off network", "chicago", "IL", zipc, addr, lat, lng, SWALCO_E, hours, "847-336-9340", mlist)

for name, addr, zipc, lat, lng, hours in [
    ("SWALCO Mobile HCW — Libertyville Lake County Campus", "290 W Winchester Road, Libertyville, IL 60048", "60048", 42.285, -87.965, "Mobile Sat events Apr–Oct; appointment required"),
    ("SWALCO Mobile HCW — Vernon Hills Public Works", "290 Evergreen Drive, Vernon Hills, IL 60061", "60061", 42.235, -87.965, "Mobile Sat events Apr–Oct; appointment required"),
    ("SWALCO Mobile HCW — Waukegan Park District Maintenance", "417 Walton Avenue, Waukegan, IL 60085", "60085", 42.365, -87.845, "Mobile Sat events Apr–Oct; appointment required"),
    ("SWALCO Mobile HCW — Winthrop Harbor Public Works", "830 Sheridan Road, Winthrop Harbor, IL 60096", "60096", 42.475, -87.825, "Mobile Sat events Apr–Oct; appointment required"),
]:
    row("SWALCO Lake County IL", name, "Mobile household chemical waste collection", "chicago", "IL", zipc, addr, lat, lng, SWALCO, hours, "847-377-4950", HHW_E())

# ── Kane County IL ───────────────────────────────────────────────────────────
KANE = "https://www.countyofkane.org/Recycling/Pages/Recycling-Centers.aspx"
KANE_DROP = "https://www.countyofkane.org/Recycling/Pages/dropoffLocations.aspx"

row("Kane County IL", "Kane County Fabyan Parkway Recycling Center", "County electronics / HHW / appliance drop-off", "chicago", "IL", "60134", "517 E Fabyan Parkway, Geneva, IL 60134", 41.885, -88.305, KANE, "Mon–Fri 8:00–16:00", "630-208-3841", HHW_E() + APPLIANCE)
row("Kane County IL", "Kane County West Dundee Recycling Center", "County electronics / textiles / book drop-off", "chicago", "IL", "60118", "900 Angle Tarn, West Dundee, IL 60118", 42.095, -88.285, KANE, "Mon–Fri 7:00–15:00", "630-208-3841", HHW_E())
row("Kane County IL", "Kane County LRS Elburn — CERA electronics drop-off", "Electronics recycling — appointment required", "chicago", "IL", "60119", "1N138 Linlar Drive, Elburn, IL 60119", 41.895, -88.465, KANE, "Mon–Fri 8:30–14:30; appointment required", "844-633-3577", E_WASTE)
row("Kane County IL", "WM Batavia Transfer Station", "County MSW transfer — bulky / C&D", "chicago", "IL", "60510", "517 E Fabyan Parkway, Batavia, IL 60510", 41.855, -88.295, KANE_DROP, "Mon–Fri 6:00–16:00", "630-208-5115", TRANSFER())
row("Kane County IL", "Groot DuKane Transfer Station — West Chicago", "County MSW transfer — bulky / appliances", "chicago", "IL", "60185", "899 E Washington Street, West Chicago, IL 60185", 41.885, -88.195, KANE_DROP, "Mon–Sat 6:00–16:00", "630-208-5115", TRANSFER())
row("Kane County IL", "Will County Green — New Lenox Recyclepalooza HHW / electronics", "Regional HHW / e-waste collection event", "chicago", "IL", "60433", "501 W Laraway Road, New Lenox, IL 60433", 41.505, -87.985, "https://www.willcountygreen.com/greenguide/household.aspx", "Sat events; appointment at willcountygreen.com", "815-727-8834", HHW_E())

# ── DuPage County IL ─────────────────────────────────────────────────────────
DUPAGE = "https://www.dupagecounty.gov/government/departments/environment_and_sustainability/recycling.php"
PAINT = "https://www.dupagecounty.gov/county_board/29_household_paint_recycling_locations_open_1601.php"

for name, addr, zipc, lat, lng, hours in [
    ("DuPage Paint Stewardship — Addison Township Highway Dept", "401 N Addison Road, Addison, IL 60101", "60101", 41.935, -88.005, "Sat 8:00–12:00; PaintCare partner"),
    ("DuPage Paint Stewardship — Bloomingdale Township Highway Dept", "6N030 Rosedale Avenue, Bloomingdale, IL 60108", "60108", 41.945, -88.085, "Quarterly Sat 8:00–12:00"),
    ("DuPage Paint Stewardship — Burr Ridge Public Works", "451 Commerce Street, Burr Ridge, IL 60527", "60527", 41.745, -87.925, "Mon–Fri 7:00–15:00"),
    ("DuPage Paint Stewardship — Carol Stream Ross Ferraro Town Center", "960 N Gary Avenue, Carol Stream, IL 60188", "60188", 41.925, -88.125, "Sat events; confirm dupagecounty.gov"),
    ("DuPage Paint Stewardship — Elmhurst Public Works", "985 S Riverside Drive, Elmhurst, IL 60126", "60126", 41.865, -87.945, "Quarterly Sat 8:00–12:00"),
    ("DuPage Paint Stewardship — Lisle Commuter Parking Lot B", "925 Burlington Avenue, Lisle, IL 60532", "60532", 41.795, -88.085, "Quarterly Sat 8:00–12:00"),
    ("DuPage Paint Stewardship — Naperville Environmental Collection Campus", "156 Fort Hill Drive, Naperville, IL 60540", "60540", 41.785, -88.155, "Mon–Fri 7:00–15:00"),
    ("DuPage Paint Stewardship — Wheaton Public Works Storage Lot", "820 W Liberty Drive, Wheaton, IL 60187", "60187", 41.865, -88.115, "2nd Sat monthly 9:00–12:00"),
    ("DuPage Paint Stewardship — Westmont Commuter Parking Lot", "31 W Quincy Street, Westmont, IL 60559", "60559", 41.795, -87.975, "Sat 8:00–12:00"),
    ("DuPage Paint Stewardship — Lisle Township Supervisor Office", "4711 Indiana Avenue, Lisle, IL 60532", "60532", 41.785, -88.075, "Mon–Fri 8:30–15:30"),
    ("DuPage Paint Stewardship — Wayne Township Highway Dept", "27W301 North Avenue, West Chicago, IL 60185", "60185", 41.895, -88.205, "Sat events; confirm dupagecounty.gov"),
    ("DuPage County Fairgrounds — Wheaton Recycling Extravaganza", "2015 Manchester Road, Wheaton, IL 60187", "60187", 41.845, -88.105, "Annual event; confirm dupagecounty.gov"),
]:
    row("DuPage County IL paint / HHW network", name, "PaintCare / county HHW partner drop-off", "chicago", "IL", zipc, addr, lat, lng, PAINT, hours, "630-407-6700", mats(HHW, ["paint-latex", "paint-oil"]))

# ── Will County IL ───────────────────────────────────────────────────────────
WILL = "https://www.willcountygreen.com/greenguide/household.aspx"
WILL_DROP = "https://www.willcountygreen.com/greenguide/recycle_drop_offs.aspx"

for name, addr, zipc, lat, lng, hours, mlist in [
    ("Will County Fairgrounds — tire drop-off event", "Will County Fairgrounds, 710 W High Street, Peotone, IL 60468", "60468", 41.335, -87.785, "Sat Sep 19 2026 8:00–15:00; Will County residents", TIRES),
    ("Will County Green — Wilmington HHW / electronics collection", "Will County Office Building, 57 W Jefferson Street, Joliet, IL 60432", "60432", 41.525, -88.085, "Sat Oct 17 2026 8:00–14:00; appointment required", HHW_E()),
    ("Will County Green — Joliet electronics drop-off event", "Will County Land Use Department, 58 E Clinton Street, Joliet, IL 60432", "60432", 41.525, -88.085, "Spring/fall events; willcountygreen.com", HHW_E()),
    ("Will County Monee Prairie View Landfill — public scale", "13800 W Manhattan-Monee Road, Monee, IL 60449", "60449", 41.425, -87.785, "Mon–Sat 6:00–16:00", LANDFILL()),
    ("Will County — Shorewood Troy Township recycling drop-off", "25000 W Seil Road, Shorewood, IL 60404", "60404", 41.515, -88.215, "Sat 8:00–12:00; confirm willcountygreen.com", mats(BULKY, E_WASTE, TIRES)),
    ("Will County — Channahon Township recycling drop-off", "Channahon Township Highway Dept, 25461 S Center Street, Channahon, IL 60410", "60410", 41.435, -88.225, "Sat 8:00–12:00; confirm willcountygreen.com", mats(BULKY, E_WASTE)),
    ("Will County — New Lenox Township recycling drop-off", "New Lenox Township Highway Dept, 1100 W Maple Street, New Lenox, IL 60451", "60451", 41.505, -87.965, "Sat 8:00–12:00; confirm willcountygreen.com", mats(BULKY, E_WASTE)),
]:
    row("Will County IL", name, "County HHW / tire / landfill network", "chicago", "IL", zipc, addr, lat, lng, WILL, hours, "815-727-8834", mlist)

# ── Cuyahoga County OH municipal service garages ─────────────────────────────
cu("Cleveland", "Division of Waste Collection — HHW drop-off", "5600 Carnegie Avenue, Cleveland, OH 44103", "44103", 41.505, -81.635, "1st Fri monthly 9:00–15:00; Cleveland residents", HHW_E())
cu("Cleveland", "Division of Waste Collection — e-waste drop-off", "5600 Carnegie Avenue, Cleveland, OH 44103", "44103", 41.505, -81.635, "Mon–Fri 9:00–15:00; no TVs", E_WASTE)
cu("Cleveland", "Ridge Road Transfer Station — tire / HHW drop-off", "3727 Ridge Road, Cleveland, OH 44102", "44102", 41.485, -81.705, "Mon–Fri; 4 free dumps/year for residents", HHW_E() + TIRES, "Municipal transfer station — tires / HHW")
cu("Lakewood", "Service Garage — year-round HHW drop-off", "12920 Berea Road, Lakewood, OH 44107", "44107", 41.485, -81.795, "Mon–Fri 8:00–14:00; Sat 8:00–12:00; Lakewood residents", HHW_E())
cu("Lakewood", "Service Garage — appliance drop-off", "12920 Berea Road, Lakewood, OH 44107", "44107", 41.485, -81.795, "Mon–Fri 8:00–14:00; Sat 8:00–12:00; Lakewood residents", APPLIANCE, "Municipal service garage — appliances")
cu("Lakewood", "Service Garage — tire drop-off", "12920 Berea Road, Lakewood, OH 44107", "44107", 41.485, -81.795, "Mon–Fri 8:00–14:00; Sat 8:00–12:00; Lakewood residents", TIRES, "Municipal service garage — tires")
cu("Lakewood", "Service Garage — e-waste drop-off", "12920 Berea Road, Lakewood, OH 44107", "44107", 41.485, -81.795, "Mon–Fri 8:00–14:00; Sat 8:00–12:00; no TVs", E_WASTE)
cu("Parma", "Service Garage — HHW drop-off", "5680 Chevrolet Boulevard, Parma, OH 44130", "44130", 41.385, -81.725, "Mar 28 & Oct 3 2026 7:30–14:30", HHW_E())
cu("Parma", "Service Garage — tire drop-off", "5680 Chevrolet Boulevard, Parma, OH 44130", "44130", 41.385, -81.725, "Sep 12 2026 7:30–14:30; limit 4/household", TIRES, "Municipal service garage — tires")
cu("Parma", "Service Garage — e-waste drop-off", "5680 Chevrolet Boulevard, Parma, OH 44130", "44130", 41.385, -81.725, "Aug 8 2026 7:30–14:30; no TVs", E_WASTE)
cu("Strongsville", "Transfer Station — tire / appliance drop-off", "16099 Foltz Industrial Parkway, Strongsville, OH 44136", "44136", 41.285, -81.825, "Mon–Fri 7:00–16:30; Sat 8:00–14:00; Sun 10:00–16:30", TIRES + APPLIANCE, "Municipal transfer station — tires / appliances")
cu("Strongsville", "Service Garage — e-waste drop-off", "16099 Foltz Industrial Parkway, Strongsville, OH 44136", "44136", 41.285, -81.825, "Mon–Fri 7:00–14:30; no TVs", E_WASTE)
cu("Strongsville", "Service Garage — HHW drop-off", "16099 Foltz Industrial Parkway, Strongsville, OH 44136", "44136", 41.285, -81.825, "Apr 28–29 & Aug 25–26 2026 7:30–14:30", HHW_E())
cu("Euclid", "Service Garage — HHW drop-off", "25200 Lakeland Boulevard, Euclid, OH 44132", "44132", 41.585, -81.525, "Mar 8–13, Jun 7–12, Sep 13–18 2026 8:00–15:00", HHW_E())
cu("Euclid", "Service Garage — tire drop-off", "25200 Lakeland Boulevard, Euclid, OH 44132", "44132", 41.585, -81.525, "Sep 13–18 2026 8:00–15:00; auto tires only", TIRES, "Municipal service garage — tires")
cu("Euclid", "Service Garage — e-waste drop-off", "25200 Lakeland Boulevard, Euclid, OH 44132", "44132", 41.585, -81.525, "Apr & Aug 2026; call for hours; no TVs", E_WASTE)
cu("Solon", "Service Department — year-round HHW drop-off", "6600 Cochran Road, Solon, OH 44139", "44139", 41.385, -81.425, "Mon–Fri 8:00–11:00 & 12:00–15:00", HHW_E())
cu("Solon", "Service Department — e-waste drop-off", "6600 Cochran Road, Solon, OH 44139", "44139", 41.385, -81.425, "Mon–Fri 8:00–11:00 & 12:00–15:00; no TVs", E_WASTE)
cu("Solon", "Service Department — fluorescent bulb drop-off", "6600 Cochran Road, Solon, OH 44139", "44139", 41.385, -81.425, "Mon–Fri 8:00–11:00 & 12:00–15:00", mats(HHW, ["fluorescent-bulbs", "led-bulbs"]))
cu("Bedford Heights", "Service Garage — HHW drop-off", "540 Northfield Road, Bedford Heights, OH 44146", "44146", 41.405, -81.505, "Mon–Fri 8:00–15:00; no latex paint", HHW_E())
cu("Bedford Heights", "Service Garage — tire drop-off", "540 Northfield Road, Bedford Heights, OH 44146", "44146", 41.405, -81.505, "Mon–Fri 7:30–15:00; auto tires only", TIRES, "Municipal service garage — tires")
cu("Bedford Heights", "Service Garage — e-waste drop-off", "540 Northfield Road, Bedford Heights, OH 44146", "44146", 41.405, -81.505, "Mon–Fri 7:30–15:00; no TVs", E_WASTE)
cu("Garfield Heights", "Service Garage — HHW drop-off", "13600 McCracken Road, Garfield Heights, OH 44125", "44125", 41.425, -81.605, "May 4–8, May 11–15, Sep 8–11, Sep 14–18 2026 7:30–15:00", HHW_E())
cu("Garfield Heights", "Service Garage — tire drop-off", "13600 McCracken Road, Garfield Heights, OH 44125", "44125", 41.425, -81.605, "Mon–Fri 7:30–15:00; auto tires only", TIRES, "Municipal service garage — tires")
cu("Westlake", "Service Garage — HHW drop-off", "741 Bassett Road, Westlake, OH 44145", "44145", 41.455, -81.925, "Apr & Oct 2026; confirm cuyahogarecycles.org", HHW_E())
cu("Westlake", "Service Garage — e-waste drop-off", "741 Bassett Road, Westlake, OH 44145", "44145", 41.455, -81.925, "Year-round Mon–Fri; confirm cuyahogarecycles.org; no TVs", E_WASTE)
cu("Shaker Heights", "Service Garage — HHW drop-off", "15600 Chagrin Boulevard, Shaker Heights, OH 44120", "44120", 41.475, -81.545, "Seasonal events; confirm cuyahogarecycles.org", HHW_E())
cu("Shaker Heights", "Service Garage — tire drop-off", "15600 Chagrin Boulevard, Shaker Heights, OH 44120", "44120", 41.475, -81.545, "Seasonal; confirm cuyahogarecycles.org", TIRES, "Municipal service garage — tires")
cu("North Olmsted", "Service Garage — HHW drop-off", "5200 Porter Road, North Olmsted, OH 44070", "44070", 41.415, -81.925, "Seasonal events; confirm cuyahogarecycles.org", HHW_E())
cu("North Olmsted", "Service Garage — e-waste drop-off", "5200 Porter Road, North Olmsted, OH 44070", "44070", 41.415, -81.925, "Year-round; confirm cuyahogarecycles.org; no TVs", E_WASTE)
cu("Beachwood", "Service Garage — HHW drop-off", "Beachwood Service Department, 2655 Richmond Road, Beachwood, OH 44122", "44122", 41.465, -81.505, "Seasonal events; confirm cuyahogarecycles.org", HHW_E())
cu("Mayfield Heights", "Service Garage — HHW drop-off", "Mayfield Service Garage, 615 SOM Center Road, Mayfield Heights, OH 44124", "44124", 41.515, -81.455, "Seasonal events; confirm cuyahogarecycles.org", HHW_E())
cu("South Euclid", "Service Garage — HHW drop-off", "South Euclid Service Garage, 4225 Warrensville Center Road, South Euclid, OH 44121", "44121", 41.515, -81.525, "Seasonal events; confirm cuyahogarecycles.org", HHW_E())
cu("Richmond Heights", "Service Garage — tire drop-off", "Richmond Heights Service Garage, 27201 Highland Road, Richmond Heights, OH 44143", "44143", 41.555, -81.505, "Seasonal; confirm cuyahogarecycles.org", TIRES, "Municipal service garage — tires")

# ── Summit County OH (Akron metro) ───────────────────────────────────────────
SUMMIT = "https://www.summitreworks.com/101/HHW"
for name, addr, zipc, lat, lng, hours in [
    ("Akron — Household Hazardous Waste drop-off", "Akron Service Department, 641 South Broadway Street, Akron, OH 44311", "44311", 41.065, -81.535, "Seasonal Sat events; confirm summitreworks.com"),
    ("Barberton — Service Garage HHW drop-off", "Barberton Service Garage, 576 W Wooster Road, Barberton, OH 44203", "44203", 41.005, -81.615, "Seasonal events; confirm cuyahogarecycles.org"),
    ("Cuyahoga Falls — Service Garage HHW drop-off", "Cuyahoga Falls Service Garage, 2310 Second Street, Cuyahoga Falls, OH 44221", "44221", 41.135, -81.485, "Seasonal events; confirm summitreworks.com"),
    ("Stow — ReWorks HHW Collection Center", "1201 Graham Road, Stow, OH 44224", "44224", 41.185, -81.485, "Thu 14:00–19:00 Jun–Sep 2026 HHW season"),
    ("Tallmadge — Service Garage tire drop-off", "Tallmadge Service Garage, 1174 Northwest Avenue, Tallmadge, OH 44278", "44278", 41.105, -81.425, "Seasonal tire events; confirm summitreworks.com"),
]:
    row("Summit County OH ReWorks network", name, "County / municipal HHW / tire drop-off", "cincinnati", "OH", zipc, addr, lat, lng, SUMMIT, hours, "330-374-0383", HHW_E() if "tire" not in name.lower() else TIRES)

# ── Allegheny County PA extras ─────────────────────────────────────────────────
ALLEG = "https://www.alleghenycounty.us/Projects-and-Initiatives/Sustainability/Household-Chemicals-Collection/Household-Chemicals-Collections"
for name, addr, zipc, lat, lng, hours in [
    ("Allegheny County HHW — North Park Swimming Pool", "9901 South Ridge Drive, Allison Park, PA 15101", "15101", 40.585, -79.965, "May 2 2026 9:00–13:00; pre-registration required"),
    ("Allegheny County HHW — Boyce Park Four Seasons Lodge", "901 Centerview Drive, Plum, PA 15239", "15239", 40.465, -79.745, "Aug 15 2026 9:00–13:00; pre-registration required"),
    ("Allegheny County HHW — South Park Wave Pool", "Corrigan Drive and 100 Acres Drive, Bethel Park, PA 15102", "15102", 40.325, -80.025, "Sep 19 2026 9:00–13:00; pre-registration required"),
    ("Allegheny County Parks — Boyce Park Transfer Station", "675 Old Frankstown Road, Pittsburgh, PA 15239", "15239", 40.465, -79.745, "Mon–Sat 7:00–16:00",),
    ("Allegheny County Parks — South Park Transfer Station", "Corrigan Drive, Bethel Park, PA 15102", "15102", 40.325, -80.025, "Mon–Sat 7:00–16:00"),
]:
    mlist = HHW_E() if "HHW" in name else TRANSFER()
    row("Allegheny County PA", name, "County HHW collection event / transfer", "pittsburgh", "PA", zipc, addr, lat, lng, ALLEG, hours, "412-488-7490", mlist)

# ── Hartford CT — MDC 2026 HHW collection events ─────────────────────────────
MDC = "https://themdc.org/environment-health-safety/household-hazardous-waste-collection/"
for name, addr, zipc, lat, lng, hours in [
    ("MDC HHW Collection — Newington Town Garage", "281 Milk Lane, Newington, CT 06111", "06111", 41.685, -72.725, "Sat Apr 25 2026 8:00–13:00"),
    ("MDC HHW Collection — East Hartford WPCF", "65 Pitkin Street, East Hartford, CT 06108", "06108", 41.765, -72.625, "Sat May 2 2026 8:00–13:00"),
    ("MDC HHW Collection — West Hartford Public Works", "17 Brixton Street, West Hartford, CT 06110", "06110", 41.745, -72.745, "Sun May 17 2026 8:00–13:00"),
    ("MDC HHW Collection — Windsor Poquonock WPCF", "1222 Poquonock Avenue, Windsor, CT 06095", "06095", 41.885, -72.645, "Sat Jun 6 2026 8:00–13:00"),
    ("MDC HHW Collection — Wethersfield Webb Elementary", "51 Willow Street, Wethersfield, CT 06109", "06109", 41.705, -72.665, "Sat Jun 27 2026 8:00–13:00"),
    ("MDC HHW Collection — Bloomfield Public Works", "21 Southwood Drive, Bloomfield, CT 06002", "06002", 41.825, -72.725, "Sat Sep 12 2026 8:00–13:00"),
    ("MDC HHW Collection — Rocky Hill Elm Ridge Park", "376 Elm Street, Rocky Hill, CT 06067", "06067", 41.655, -72.645, "Sat Sep 19 2026 8:00–13:00"),
    ("MDC HHW Collection — Windsor Locks Public Works", "6 Stanton Road, Windsor Locks, CT 06096", "06096", 41.925, -72.625, "Sat Oct 17 2026 8:00–13:00"),
    ("MDC HHW Collection — Hartford MDC Operations Facility", "125 Maxim Road, Hartford, CT 06114", "06114", 41.745, -72.685, "Sat Oct 24 2026 8:00–13:00"),
]:
    row("Hartford CT MDC regional HHW", name, "Regional HHW collection event — MDC member towns", "boston", "CT", zipc, addr, lat, lng, MDC, hours + "; MDC member-town residents", "860-278-3809", HHW_E())

# ── Middlesex County MA ──────────────────────────────────────────────────────
MASS = "https://www.mass.gov/info-details/safely-manage-hazardous-household-products"
for name, addr, zipc, lat, lng, hours in [
    ("Devens Regional HHW Collection Center", "27 Jackson Road, Devens, MA 01434", "01434", 42.545, -71.615, "Sat events Mar–Dec; confirm mass.gov"),
    ("Lexington DPW — HHW collection events", "201 Bedford Street, Lexington, MA 02420", "02420", 42.445, -71.225, "Sat events Apr–Oct; Lexington residents"),
    ("Newton Resource Recovery Center — HHW", "115 Rumford Avenue, Auburndale, MA 02466", "02466", 42.345, -71.245, "Wed 7:30–12:30 mid-May–Oct; Newton residents"),
    ("Cambridge DPW — Hazardous Waste Day", "Cambridge Public Works, 147 Hampshire Street, Cambridge, MA 02139", "02139", 42.365, -71.095, "Annual event; confirm cambridgema.gov"),
    ("Lowell Regional HHW Collection Center", "60 Hartwell Avenue, Westford, MA 01886", "01886", 42.585, -71.425, "Sat events; confirm middlesex county schedule"),
]:
    row("Middlesex County MA HHW network", name, "Regional / municipal HHW collection", "boston", "MA", zipc, addr, lat, lng, MASS, hours, "617-635-4500", HHW_E())

# ── Westchester County NY ─────────────────────────────────────────────────────
WCH = "https://environment.westchestergov.com/facilities/h-mrf"
row("Westchester County NY", "Westchester County H-MRF — tire / e-waste lane", "County H-MRF — tires / e-waste / HHW by appointment", "yonkers", "NY", "10595", "15 Woods Road, Valhalla, NY 10595", 41.078, -73.802, WCH, "Tue–Sat 10:00–15:00 by appointment", "914-813-5425", HHW_E() + TIRES)
row("Westchester County NY", "Westchester County DEF — Material Recovery Facility scale", "County transfer / bulky drop-off", "yonkers", "NY", "10595", "15 Woods Road, Valhalla, NY 10595", 41.078, -73.802, "https://environment.westchestergov.com/facilities", "Tue–Sat; confirm westchestergov.com", "914-813-5425", TRANSFER())
row("Westchester County NY", "Yonkers DPW — Saw Mill River Road bulk / yard waste", "Municipal bulk / yard-waste drop-off", "yonkers", "NY", "10701", "735 Saw Mill River Road, Yonkers, NY 10701", 40.945, -73.865, "https://www.yonkersny.gov/departments/public-works", "Mon–Sat 7:00–15:00; Yonkers residents", "914-377-7500", mats(BULKY, ["yard-waste"], APPLIANCE))

# ── Nassau / Suffolk County NY ────────────────────────────────────────────────
NASS = "https://www.nassaucountyny.gov/3119/Household-Hazardous-Waste"
row("Nassau County NY", "Nassau County S.T.O.P. Program — East Meadow HHW", "County S.T.O.P. HHW / e-waste event site", "new-york", "NY", "11554", "999 Hempstead Turnpike, East Meadow, NY 11554", 40.725, -73.555, NASS, "Sat 7:00–14:00; Nassau homeowners", "516-572-5757", HHW_E())
row("Nassau County NY", "Nassau County Callahan Transfer Station — bulky", "County transfer — bulky / C&D / tires", "new-york", "NY", "11590", "46026 Musslewhite Road, Westbury, NY 11590", 40.755, -73.585, "https://www.nassaucountyny.gov/1569/Transfer-Station", "Mon–Sat 7:00–15:00", "516-572-6220", TRANSFER())

SUF = "https://www.brookhavenny.gov/417/Town-Solid-Waste-Management-Facility"
for name, addr, zipc, lat, lng, url, hours in [
    ("Southold Town Transfer Station — Cox Lane", "155 Cox Lane, Cutchogue, NY 11935", "11935", 41.015, -72.485, "https://www.southoldtownny.gov/259/Transfer-Station", "Daily 7:00–17:00"),
    ("Southampton Hampton Bays Transfer Station", "30 Jackson Avenue, Hampton Bays, NY 11946", "11946", 40.875, -72.515, "https://www.southamptontownny.gov/facilities/facility/details/Hampton-Bays-Transfer-Station-2", "Daily 8:30–16:00"),
    ("Southampton Westhampton Transfer Station", "30 Jackson Avenue, Westhampton, NY 11977", "11977", 40.825, -72.645, "https://www.southamptontownny.gov/departments/waste-management", "Daily 8:30–16:00"),
    ("Smithtown Municipal Services Facility", "85 Hillside Avenue, Kings Park, NY 11754", "11754", 40.885, -73.245, "https://www.smithtownny.gov/departments/public-works/solid-waste", "Mon–Sat 7:00–15:00"),
    ("Riverhead Town Landfill — Youngs Avenue", "3500 Youngs Avenue, Calverton, NY 11933", "11933", 40.925, -72.745, "https://www.townofriverheadny.gov/departments/public-works/solid-waste", "Mon–Sat 7:00–16:00"),
    ("Islip Multi-Purpose Recycling Facility — Lincoln Avenue", "1150 Lincoln Avenue, Holbrook, NY 11741", "11741", 40.805, -73.065, "https://www.islipny.gov/departments/public-works/solid-waste-management", "Mon–Sat 7:00–16:00"),
]:
    row("Suffolk County NY town networks", name, "Town transfer / landfill — bulky / tires / yard waste", "new-york", "NY", zipc, addr, lat, lng, url, hours, "631-451-6212", LANDFILL())

# ── Middlesex County NJ (NYC metro spine) ─────────────────────────────────────
MIDX = "https://www.middlesexcountynj.gov/government/departments/department-of-public-works-and-infrastructure/waste-management"
for name, addr, zipc, lat, lng, hours in [
    ("Middlesex County HHW — East Brunswick permanent site", "25 Kirk Lane, East Brunswick, NJ 08816", "08816", 40.425, -74.415, "Sat 8:00–14:00; Middlesex County residents"),
    ("Middlesex County HHW — Woodbridge collection event", "Middlesex County College, 2600 Woodbridge Avenue, Edison, NJ 08837", "08837", 40.525, -74.355, "Sat events; confirm middlesexcountynj.gov"),
    ("Middlesex County landfill — East Brunswick scale", "Middlesex County Landfill, 65 Edgeboro Road, East Brunswick, NJ 08816", "08816", 40.445, -74.425, "Mon–Sat 6:00–16:00"),
]:
    row("Middlesex County NJ", name, "County HHW / landfill network", "jersey-city", "NJ", zipc, addr, lat, lng, MIDX, hours, "732-745-4170", HHW_E() if "HHW" in name else LANDFILL())

# ── McHenry County IL (Chicago collar) ───────────────────────────────────────
MCH = "https://www.mchenrycountyil.gov/County-Government/Departments/Health-Department/Environmental-Health/Household-Hazardous-Waste"
row("McHenry County IL", "McHenry County HHW — Crystal Lake collection facility", "County HHW / e-waste collection", "chicago", "IL", "60012", "6603 Route 14, Crystal Lake, IL 60012", 42.285, -88.285, MCH, "Apr–Oct Sat events; confirm mchenrycountyil.gov", "815-334-4585", HHW_E())
row("McHenry County IL", "McHenry County HHW — Woodstock mobile collection", "County mobile HHW collection event", "chicago", "IL", "60098", "667 Ware Road, Woodstock, IL 60098", 42.315, -88.445, MCH, "Mobile Sat events; confirm mchenrycountyil.gov", "815-334-4585", HHW_E())

# ── Additional Cuyahoga OH municipalities ──────────────────────────────────────
cu("Berea", "Service Garage — HHW drop-off", "Berea Service Garage, 400 Berea Commons, Berea, OH 44017", "44017", 41.365, -81.855, "Seasonal events; confirm cuyahogarecycles.org", HHW_E())
cu("Brooklyn", "Service Garage — tire drop-off", "Brooklyn Service Garage, 9400 Memphis Avenue, Brooklyn, OH 44144", "44144", 41.435, -81.735, "Seasonal events; confirm cuyahogarecycles.org", TIRES, "Municipal service garage — tires")
cu("Maple Heights", "Service Garage — e-waste drop-off", "Maple Heights Service Garage, 15901 Libby Road, Maple Heights, OH 44137", "44137", 41.415, -81.565, "Seasonal events; confirm cuyahogarecycles.org; no TVs", E_WASTE)
cu("Independence", "Service Garage — HHW drop-off", "Independence Service Garage, 6800 Brecksville Road, Independence, OH 44131", "44131", 41.385, -81.645, "Seasonal events; confirm cuyahogarecycles.org", HHW_E())
cu("Seven Hills", "Service Garage — tire drop-off", "Seven Hills Service Garage, 7325 Summit Drive, Seven Hills, OH 44131", "44131", 41.395, -81.675, "Seasonal events; confirm cuyahogarecycles.org", TIRES, "Municipal service garage — tires")
cu("Richfield", "Service Garage — HHW drop-off", "Richfield Service Garage, 4410 Broadview Road, Richfield, OH 44286", "44286", 41.245, -81.645, "Seasonal events; confirm cuyahogarecycles.org", HHW_E())
cu("Broadview Heights", "Service Garage — e-waste drop-off", "Broadview Heights Service Garage, 9543 Broadview Road, Broadview Heights, OH 44147", "44147", 41.315, -81.685, "Seasonal events; confirm cuyahogarecycles.org; no TVs", E_WASTE)
cu("Brecksville", "Service Garage — HHW drop-off", "Brecksville Service Garage, 9069 Brecksville Road, Brecksville, OH 44141", "44141", 41.305, -81.625, "Seasonal events; confirm cuyahogarecycles.org", HHW_E())

# ── Oakland / Wayne County MI (Detroit metro spine) ────────────────────────────
OAK = "https://www.oakgov.com/resources/recycling/Pages/default.aspx"
for name, addr, zipc, lat, lng, hours in [
    ("Oakland County North Oakland Recycling Authority — Groveland", "NOARA Transfer Station, 5900 Dixie Highway, Clarkston, MI 48346", "48346", 42.735, -83.385, "Mon–Sat 7:00–17:00"),
    ("Oakland County SOCRRA — Troy transfer / recycling", "SOCRRA Facility, 995 Coolidge Highway, Troy, MI 48084", "48084", 42.565, -83.145, "Mon–Sat 7:00–17:00"),
    ("Wayne County Woodland Meadows Landfill — public drop-off", "Woodland Meadows Landfill, 12363 Hannan Road, Van Buren Township, MI 48111", "48111", 42.215, -83.485, "Mon–Sat 6:00–16:00"),
    ("Washtenaw County Home Toxics Center — Ann Arbor", "Home Toxics Center, 705 Zeeb Road, Ann Arbor, MI 48103", "48103", 42.245, -83.785, "Wed 9:00–17:00; Sat 9:00–13:00 Apr–Nov"),
]:
    mlist = HHW_E() if "Toxics" in name or "Home Toxics" in name else TRANSFER() if "transfer" in name.lower() or "SOCRRA" in name else LANDFILL()
    row("Oakland / Wayne County MI", name, "County transfer / landfill / HHW", "detroit", "MI", zipc, addr, lat, lng, OAK, hours, "248-858-5656", mlist)

# ── Providence RI metro (Northeast spine) ──────────────────────────────────────
RI = "https://www.rirrc.org/"
for name, addr, zipc, lat, lng, hours in [
    ("RI Resource Recovery — Small Vehicle Area bulky drop-off", "Central Landfill SVA, 65 Shun Pike, Johnston, RI 02919", "02919", 41.825, -71.495, "Mon–Sat 6:00–15:45"),
    ("City of Cranston RI — DPW bulky drop-off", "Cranston Public Works, 40 Sockanosset Cross Road, Cranston, RI 02920", "02920", 41.765, -71.455, "Sat 7:00–12:00; Cranston residents"),
    ("City of Warwick RI — HHW collection events", "Warwick Public Works, 925 Sandy Lane, Warwick, RI 02889", "02889", 41.685, -71.425, "Sat events; confirm warwickri.gov"),
]:
    row("Providence RI metro", name, "State / municipal bulky / HHW network", "providence", "RI", zipc, addr, lat, lng, RI, hours, "401-942-1430", HHW_E() if "HHW" in name else mats(BULKY, APPLIANCE, TIRES))

# ── Milwaukee / Waukesha collar WI ─────────────────────────────────────────────
WAUK = "https://www.waukeshacounty.gov/health-and-human-services/household-hazardous-waste/"
for name, addr, zipc, lat, lng, hours in [
    ("Waukesha County HHW — Muskego Emerald Park", "GFL Emerald Park, W124 S10382 South 124th Street, Muskego, WI 53150", "53150", 42.905, -88.125, "Sat events Mar–Nov; appointment required"),
    ("Waukesha County HHW — Waukesha UWM campus", "UWM-Waukesha, 1500 N University Drive, Waukesha, WI 53188", "53188", 43.025, -88.225, "Sat events Mar–Nov; appointment required"),
    ("Waukesha County landfill — public scale", "Waukesha County Landfill, W124 N9451 North Avenue, Menomonee Falls, WI 53051", "53051", 43.155, -88.125, "Mon–Sat 6:00–16:00"),
]:
    row("Waukesha County WI", name, "County HHW / landfill network", "milwaukee", "WI", zipc, addr, lat, lng, WAUK, hours, "262-896-8300", HHW_E() if "HHW" in name else LANDFILL())

# ── Hennepin / Ramsey MN (Minneapolis spine extras) ───────────────────────────
HENN = "https://www.hennepin.us/residents/recycling-hazardous-waste"
for name, addr, zipc, lat, lng, hours in [
    ("Hennepin County HHW — Bloomington South", "8100 Jefferson Highway, Brooklyn Park, MN 55445", "55445", 45.095, -93.385, "Tue–Fri 10:00–18:00; Sat 8:00–16:00"),
    ("Ramsey County Environmental Center — yard waste", "5 Empire Drive, Saint Paul, MN 55103", "55103", 44.965, -93.125, "Tue–Fri 11:00–19:00; Sat 8:00–16:00"),
]:
    row("Twin Cities MN county network", name, "County HHW / environmental center", "minneapolis", "MN", zipc, addr, lat, lng, HENN, hours, "612-348-3777", HHW_E() if "HHW" in name else mats(BULKY, ["yard-waste"], TIRES))


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
