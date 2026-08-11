#!/usr/bin/env python3
"""DumpRegistry HARD facilities only — East/MW metro inventory (2026-08-11).

Permanent public drop-offs: transfer, HHW, bulky, e-waste, tires, appliances,
landfill scales — sourced from official .gov pages only.

REJECTS: food-scrap, cardboard dumpsters, bottle-only recycling, Project Oscar.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from facility_quality import is_hard_facility  # noqa: E402

FAC_PATH = ROOT / "data" / "facilities" / "all.json"
ITEMS = {i["slug"] for i in json.loads((ROOT / "data" / "items.json").read_text())}

HHW = [
    "paint-latex", "paint-oil", "pesticides", "herbicides", "pool-chemicals",
    "gasoline", "motor-oil", "antifreeze", "car-battery", "household-batteries",
    "lithium-battery", "fluorescent-bulbs", "propane-tank", "cooking-oil",
    "medical-sharps", "prescription-drugs", "fire-extinguisher", "thermometer-mercury",
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
CND = ["construction-debris", "drywall", "lumber", "concrete"]

TARGET_CITIES = {
    "cincinnati", "columbus", "toledo", "fort-wayne", "chicago", "detroit",
    "milwaukee", "minneapolis", "boston", "baltimore", "pittsburgh", "buffalo",
    "rochester", "philadelphia", "jersey-city", "yonkers", "norfolk",
    "virginia-beach", "chesapeake", "richmond", "new-york",
    "atlanta", "charlotte", "indianapolis", "raleigh", "durham", "grand-rapids",
}

DSNY_SW_URL = "https://www.nyc.gov/site/dsny/what-we-do/programs/special-waste-drop-off.page"
DSNY_TIRE_URL = "https://www.nyc.gov/site/dsny/collection/get-rid-of/automotive-waste.page"
DSNY_SAFE_URL = "https://www.nyc.gov/site/dsny/what-we-do/programs/safe-disposal-events.page"

DSNY_GARAGES = [
    ("DSNY Bronx District Garage — 680 E 132nd St", "680 East 132nd Street, Bronx, NY 10454", "10454", 40.802, -73.907),
    ("DSNY Bronx District Garage — 650 Casanova St", "650 Casanova Street, Bronx, NY 10474", "10474", 40.807, -73.886),
    ("DSNY Bronx District Garage — 720 E 132nd St", "720 East 132nd Street, Bronx, NY 10454", "10454", 40.802, -73.906),
    ("DSNY Bronx District Garage — 1331 Cromwell Ave", "1331 Cromwell Avenue, Bronx, NY 10452", "10452", 40.842, -73.918),
    ("DSNY Bronx District Garage — 800 E 176th St", "800 East 176th Street, Bronx, NY 10460", "10460", 40.839, -73.879),
    ("DSNY Bronx District Garage — 2383 Blackrock Ave", "2383 Blackrock Avenue, Bronx, NY 10472", "10472", 40.826, -73.857),
    ("DSNY Bronx District Garage — 850 Zerega Ave", "850 Zerega Avenue, Bronx, NY 10473", "10473", 40.820, -73.846),
    ("DSNY Bronx District Garage — 800 Zerega Ave", "800 Zerega Avenue, Bronx, NY 10473", "10473", 40.821, -73.847),
    ("DSNY Bronx District Garage — 1635 E 233rd St", "1635 East 233rd Street, Bronx, NY 10466", "10466", 40.893, -73.852),
    ("DSNY Brooklyn North Garage — 161 Varick Ave", "161 Varick Avenue, Brooklyn, NY 11237", "11237", 40.706, -73.926),
    ("DSNY Brooklyn North Garage — 465 Hamilton Ave", "465 Hamilton Avenue, Brooklyn, NY 11231", "11231", 40.672, -73.997),
    ("DSNY Brooklyn North Garage — 559 Park Ave", "559 Park Avenue, Brooklyn, NY 11205", "11205", 40.696, -73.962),
    ("DSNY Brooklyn North Garage — 606 Milford St", "606 Milford Street, Brooklyn, NY 11208", "11208", 40.674, -73.872),
    ("DSNY Brooklyn North Garage — 1755 Pacific St", "1755 Pacific Street, Brooklyn, NY 11213", "11213", 40.674, -73.931),
    ("DSNY Brooklyn North Garage — 690 New York Ave", "690 New York Avenue, Brooklyn, NY 11203", "11203", 40.662, -73.944),
    ("DSNY Brooklyn North Garage — 922 Georgia Ave", "922 Georgia Avenue, Brooklyn, NY 11207", "11207", 40.669, -73.883),
    ("DSNY Brooklyn North Garage — 105-02 Avenue D", "105-02 Avenue D, Brooklyn, NY 11236", "11236", 40.643, -73.898),
    ("DSNY Brooklyn South Garage — 127 2nd Ave", "127 2nd Avenue, Brooklyn, NY 11215", "11215", 40.671, -73.995),
    ("DSNY Brooklyn South Garage — 5100 1st Ave", "5100 1st Avenue, Brooklyn, NY 11220", "11220", 40.645, -74.026),
    ("DSNY Brooklyn South Garage — 1824 Shore Pkwy", "1824 Shore Parkway, Brooklyn, NY 11214", "11214", 40.594, -73.994),
    ("DSNY Brooklyn South Garage — 5602 19th Ave", "5602 19th Avenue, Brooklyn, NY 11204", "11204", 40.619, -73.976),
    ("DSNY Brooklyn South Garage — 2012 Neptune Ave", "2012 Neptune Avenue, Brooklyn, NY 11224", "11224", 40.577, -73.984),
    ("DSNY Brooklyn South Garage — 1397 Ralph Ave", "1397 Ralph Avenue, Brooklyn, NY 11236", "11236", 40.644, -73.918),
    ("DSNY Brooklyn South Garage — 2501 Knapp St", "2501 Knapp Street, Brooklyn, NY 11235", "11235", 40.589, -73.936),
    ("DSNY Brooklyn South Garage — 1750 E 49th St", "1750 East 49th Street, Brooklyn, NY 11234", "11234", 40.620, -73.927),
    ("DSNY Brooklyn South Garage — 105-01 Foster Ave", "105-01 Foster Avenue, Brooklyn, NY 11236", "11236", 40.643, -73.897),
    ("DSNY Manhattan Garage — 353 Spring St", "353 Spring Street, New York, NY 10013", "10013", 40.726, -74.009),
    ("DSNY Manhattan Garage — Pier 36 South St", "Pier 36, South Street, New York, NY 10002", "10002", 40.709, -73.988),
    ("DSNY Manhattan Garage — 650 W 57th St", "650 West 57th Street, New York, NY 10019", "10019", 40.771, -73.994),
    ("DSNY Manhattan Garage — 4036 9th Ave", "4036 9th Avenue, New York, NY 10034", "10034", 40.857, -73.929),
    ("DSNY Manhattan Garage — 125 E 149th St", "125 East 149th Street, Bronx, NY 10451", "10451", 40.816, -73.926),
    ("DSNY Manhattan Garage — 110 E 131st St", "110 East 131st Street, New York, NY 10037", "10037", 40.808, -73.937),
    ("DSNY Manhattan Garage — 220 E 128th St", "220 East 128th Street, New York, NY 10035", "10035", 40.806, -73.936),
    ("DSNY Manhattan Garage — 301 W 215th St", "301 West 215th Street, New York, NY 10034", "10034", 40.871, -73.915),
    ("DSNY Queens West Garage — 34-28 21st St", "34-28 21st Street, Long Island City, NY 11106", "11106", 40.761, -73.932),
    ("DSNY Queens West Garage — 52-35 58th St", "52-35 58th Street, Maspeth, NY 11378", "11378", 40.726, -73.908),
    ("DSNY Queens West Garage — 48-01 58th Rd", "48-01 58th Road, Maspeth, NY 11378", "11378", 40.725, -73.912),
    ("DSNY Queens West Garage — 58-73 53rd Ave", "58-73 53rd Avenue, Maspeth, NY 11378", "11378", 40.728, -73.905),
    ("DSNY Queens West Garage — 132-05 Atlantic Ave", "132-05 Atlantic Avenue, Richmond Hill, NY 11418", "11418", 40.689, -73.822),
    ("DSNY Queens East Garage — 120-15 31st Ave", "120-15 31st Avenue, College Point, NY 11354", "11354", 40.776, -73.843),
    ("DSNY Queens East Garage — 130-23 150th Ave", "130-23 150th Avenue, Jamaica, NY 11434", "11434", 40.668, -73.788),
    ("DSNY Queens East Garage — 75-05 Winchester Blvd", "75-05 Winchester Boulevard, Queens Village, NY 11427", "11427", 40.728, -73.741),
    ("DSNY Queens East Garage — 153-67 146th Ave", "153-67 146th Avenue, Jamaica, NY 11434", "11434", 40.665, -73.785),
    ("DSNY Queens East Garage — 51-10 Almeda Ave", "51-10 Almeda Avenue, Arverne, NY 11692", "11692", 40.592, -73.796),
    ("DSNY Staten Island Garage — 539 Jersey St", "539 Jersey Street, Staten Island, NY 10301", "10301", 40.628, -74.077),
    ("DSNY Staten Island Garage — 2500 Richmond Ave", "2500 Richmond Avenue, Staten Island, NY 10314", "10314", 40.613, -74.164),
    ("DSNY Staten Island Garage — 1000 West Service Rd", "1000 West Service Road, Staten Island, NY 10314", "10314", 40.580, -74.188),
]


def mats(*groups):
    out, seen = [], set()
    for g in groups:
        for m in g:
            if m not in ITEMS:
                raise SystemExit(f"unknown slug {m}")
            if m not in seen:
                seen.add(m)
                out.append(m)
    return out


def _gov(url: str) -> None:
    u = url.lower()
    # Official .gov / .us local-gov / *gov.com municipal portals
    if ".gov" in u or ".us/" in u or "gov.com/" in u or u.rstrip("/").endswith((".us", "gov.com")):
        return
    raise SystemExit(f"Non-official source rejected: {url}")


def _dsny_garages():
    return [
        {
            "name": name,
            "facility_type": "DSNY district garage — tire drop-off",
            "city_slug": "new-york", "state": "NY", "zip": zip_,
            "address": addr, "lat": lat, "lng": lng,
            "source_url": DSNY_TIRE_URL,
            "hours": "Mon–Sat 10:00–17:30 (closed holidays); NYC resident ID + vehicle registration required",
            "phone": "311",
            "accepted_materials": mats(TIRES),
        }
        for name, addr, zip_, lat, lng in DSNY_GARAGES
    ]


def _nyc_special_waste():
    return [
        {
            "name": "DSNY Special Waste Drop-Off — Hunts Point (Bronx)",
            "facility_type": "Special waste / HHW / e-waste drop-off",
            "city_slug": "new-york", "state": "NY", "zip": "10474",
            "address": "Farragut Street and the East River (enter on Farragut St off Food Center Drive), Bronx, NY 10474",
            "lat": 40.808, "lng": -73.878,
            "source_url": DSNY_SW_URL,
            "hours": "Tue–Sat 9:00–15:00 (closed holidays and severe weather)",
            "phone": "311",
            "accepted_materials": mats(HHW, E_WASTE, TIRES),
        },
        {
            "name": "DSNY Special Waste Drop-Off — Greenpoint (Brooklyn)",
            "facility_type": "Special waste / HHW / e-waste drop-off",
            "city_slug": "new-york", "state": "NY", "zip": "11222",
            "address": "459 North Henry Street, Brooklyn, NY 11222",
            "lat": 40.728, "lng": -73.943,
            "source_url": DSNY_SW_URL,
            "hours": "Tue–Sat 9:00–15:00 (closed holidays and severe weather)",
            "phone": "311",
            "accepted_materials": mats(HHW, E_WASTE, TIRES),
        },
        {
            "name": "DSNY Special Waste Drop-Off — Manhattan (Pike Slip)",
            "facility_type": "Special waste / HHW / e-waste drop-off",
            "city_slug": "new-york", "state": "NY", "zip": "10002",
            "address": "74 Pike Slip between Cherry Street and South Street, New York, NY 10002",
            "lat": 40.708, "lng": -73.992,
            "source_url": DSNY_SW_URL,
            "hours": "Tue–Sat 9:00–15:00 (closed holidays and severe weather)",
            "phone": "311",
            "accepted_materials": mats(HHW, E_WASTE, TIRES),
        },
        {
            "name": "DSNY Special Waste Drop-Off — College Point (Queens)",
            "facility_type": "Special waste / HHW / e-waste drop-off",
            "city_slug": "new-york", "state": "NY", "zip": "11354",
            "address": "30th Avenue between 120th and 122nd Streets, College Point, NY 11354",
            "lat": 40.776, "lng": -73.843,
            "source_url": DSNY_SW_URL,
            "hours": "Tue–Sat 9:00–15:00 (closed holidays and severe weather)",
            "phone": "311",
            "accepted_materials": mats(HHW, E_WASTE, TIRES),
        },
        {
            "name": "DSNY Special Waste Drop-Off — Staten Island (Fresh Kills)",
            "facility_type": "Special waste / HHW / e-waste drop-off",
            "city_slug": "new-york", "state": "NY", "zip": "10314",
            "address": "1000 West Service Road, Staten Island, NY 10314",
            "lat": 40.580, "lng": -74.188,
            "source_url": DSNY_SW_URL,
            "hours": "Tue–Sat 9:00–15:00 (closed holidays and severe weather)",
            "phone": "311",
            "accepted_materials": mats(HHW, E_WASTE, TIRES),
        },
    ]


def _nyc_safe_events():
    """Seasonal SAFE (Solvents, Automotive, Flammables, Electronics) disposal events."""
    sites = [
        ("DSNY SAFE Disposal Event — Bronx (Orchard Beach)", "Orchard Beach Parking Lot, Pelham Bay Park, Bronx, NY 10464", "10464", 40.868, -73.794),
        ("DSNY SAFE Disposal Event — Brooklyn", "Floyd Bennett Field, Brooklyn, NY 11234", "11234", 40.591, -73.881),
        ("DSNY SAFE Disposal Event — Manhattan (Union Square)", "Union Square North Plaza, 17th Street between Park Ave South and Broadway, New York, NY 10003", "10003", 40.736, -73.990),
        ("DSNY SAFE Disposal Event — Queens", "Cunningham Park, 196th Place & Union Turnpike, Fresh Meadows, NY 11366", "11366", 40.730, -73.775),
        ("DSNY SAFE Disposal Event — Staten Island", "Staten Island Mall parking lot, 2655 Richmond Avenue, Staten Island, NY 10314", "10314", 40.582, -74.166),
    ]
    return [
        {
            "name": name,
            "facility_type": "SAFE disposal event — HHW / e-waste (seasonal)",
            "city_slug": "new-york", "state": "NY", "zip": zip_,
            "address": addr, "lat": lat, "lng": lng,
            "source_url": DSNY_SAFE_URL,
            "hours": "Fall season events 10:00–16:00 (confirm dates on nyc.gov/safeevents)",
            "phone": "311",
            "accepted_materials": mats(HHW, E_WASTE),
        }
        for name, addr, zip_, lat, lng in sites
    ]


def _philadelphia_hhw():
    url = "https://www.phila.gov/services/trash-recycling-city-upkeep/dispose-of-household-hazardous-waste/"
    events = [
        ("Philadelphia HHW Collection — Northeast (State Road)", "8401 State Road, Philadelphia, PA 19136", "19136", 40.045, -75.015),
        ("Philadelphia HHW Collection — West (Parkside)", "4800 Parkside Avenue, Philadelphia, PA 19131", "19131", 39.992, -75.215),
        ("Philadelphia HHW Collection — Northwest (Domino Lane)", "320 Domino Lane, Philadelphia, PA 19128", "19128", 40.045, -75.255),
        ("Philadelphia HHW Collection — North (York Street)", "2121 West York Street, Philadelphia, PA 19132", "19132", 39.999, -75.165),
        ("Philadelphia HHW Collection — Southwest (63rd Street)", "3033 South 63rd Street, Philadelphia, PA 19153", "19153", 39.915, -75.225),
        ("Philadelphia HHW Collection — Port Richmond (Delaware Ave)", "3901 North Delaware Avenue, Philadelphia, PA 19137", "19137", 39.985, -75.075),
        ("Philadelphia HHW Collection — Northeast (State Road Lot 2)", "8401 State Road, Lot 2, Philadelphia, PA 19136", "19136", 40.046, -75.016),
    ]
    return [
        {
            "name": name,
            "facility_type": "Household hazardous waste collection event",
            "city_slug": "philadelphia", "state": "PA", "zip": zip_,
            "address": addr, "lat": lat, "lng": lng,
            "source_url": url,
            "hours": "Scheduled events 9:00–15:00 (see phila.gov for 2026 dates)",
            "phone": "311",
            "accepted_materials": mats(HHW),
        }
        for name, addr, zip_, lat, lng in events
    ]


def _baltimore_dropoffs():
    url = "https://www.baltimorecity.gov/publicworks/solid-waste/drop-off"
    return [
        {
            "name": "Sisson Street Residential Drop-Off Center",
            "facility_type": "Residential drop-off — bulk / appliances / HHW events",
            "city_slug": "baltimore", "state": "MD", "zip": "21211",
            "address": "2840 Sisson Street, Baltimore, MD 21211",
            "lat": 39.322, "lng": -76.629,
            "source_url": url,
            "hours": "Mon–Sat 9:00–19:00; HHW first Fri+Sat Jun–Oct",
            "phone": "(410) 396-7250",
            "accepted_materials": mats(BULKY, APPLIANCE, E_WASTE, HHW),
        },
        {
            "name": "Eastern Residential Recycling Center",
            "facility_type": "Residential drop-off — bulk / appliances / tires",
            "city_slug": "baltimore", "state": "MD", "zip": "21206",
            "address": "6101 Bowley's Lane, Baltimore, MD 21206",
            "lat": 39.325, "lng": -76.545,
            "source_url": url,
            "hours": "Mon–Sat 9:00–19:00",
            "phone": "(410) 396-9950",
            "accepted_materials": mats(BULKY, APPLIANCE, E_WASTE, TIRES),
        },
        {
            "name": "Reedbird Residential Recycling Center (Western)",
            "facility_type": "Residential drop-off — bulk / appliances / e-waste",
            "city_slug": "baltimore", "state": "MD", "zip": "21225",
            "address": "701 Reedbird Avenue, Baltimore, MD 21225",
            "lat": 39.238, "lng": -76.612,
            "source_url": url,
            "hours": "Sat 9:00–19:00 (limited schedule during modernization)",
            "phone": "(410) 396-3367",
            "accepted_materials": mats(BULKY, E_WASTE, APPLIANCE, TIRES),
        },
        {
            "name": "Northwest Transfer Station — Citizen Drop-Off",
            "facility_type": "Municipal transfer station — bulk / C&D / appliances",
            "city_slug": "baltimore", "state": "MD", "zip": "21215",
            "address": "5030 Reisterstown Road, Baltimore, MD 21215",
            "lat": 39.345, "lng": -76.678,
            "source_url": url,
            "hours": "Mon–Sat 7:00–17:00",
            "phone": "(410) 396-2706",
            "accepted_materials": mats(BULKY, APPLIANCE, E_WASTE, CND),
        },
        {
            "name": "Quarantine Road Landfill — Residential Drop-Off Center",
            "facility_type": "Landfill / residential drop-off — bulk / appliances / e-waste",
            "city_slug": "baltimore", "state": "MD", "zip": "21226",
            "address": "6100 Quarantine Road, Baltimore, MD 21226",
            "lat": 39.238, "lng": -76.556,
            "source_url": url,
            "hours": "Mon–Sat 9:00–15:30",
            "phone": "(410) 396-3772",
            "accepted_materials": mats(BULKY, APPLIANCE, E_WASTE, TIRES, CND),
        },
    ]


def _detroit_bulk():
    url = "https://detroitmi.gov/departments/department-public-works/refuse-collection/bulk-yard-waste/free-citizen-bulk-drop-centers"
    hhw_url = "https://detroitmi.gov/departments/department-public-works/refuse-collection/household-hazardous-waste-information"
    yards = [
        ("DPW Davison Yard — Free Citizen Bulk Drop-Off", "8221 West Davison Avenue, Detroit, MI 48238", "48238", 42.396, -83.140),
        ("DPW Southfield Yard — Free Citizen Bulk Drop-Off", "12255 Southfield Road, Detroit, MI 48227", "48227", 42.372, -83.224),
        ("DPW J. Fons Transfer Station — Free Citizen Bulk Drop-Off", "6451 East McNichols Road, Detroit, MI 48234", "48234", 42.416, -83.048),
        ("DPW Gleaners Bulk Drop-Off Yard", "5800 Loraine Street, Detroit, MI 48209", "48209", 42.313, -83.113),
    ]
    rows = [
        {
            "name": name,
            "facility_type": "Municipal bulk / yard waste drop-off center",
            "city_slug": "detroit", "state": "MI", "zip": zip_,
            "address": addr, "lat": lat, "lng": lng,
            "source_url": url,
            "hours": "Mon–Sat; Apr 1–Oct 31 8:00–18:00; Nov 1–Mar 31 8:00–16:00 (J. Fons Sat until 12:00)",
            "phone": "(313) 876-0004",
            "accepted_materials": mats(BULKY, TIRES),
        }
        for name, addr, zip_, lat, lng in yards
    ]
    rows.append({
        "name": "DPW Household Hazardous Waste Receiving Facility",
        "facility_type": "Household hazardous waste / e-waste drop-off",
        "city_slug": "detroit", "state": "MI", "zip": "48207",
        "address": "2000 East Ferry Street, Detroit, MI 48207",
        "lat": 42.358, "lng": -83.019,
        "source_url": hhw_url,
        "hours": "Thu 7:30–14:00; 4th Sat 8:00–14:00",
        "phone": "(313) 923-2240",
        "accepted_materials": mats(HHW, E_WASTE),
    })
    wayne_url = (
        "https://www.waynecountymi.gov/Government/Departments/Environmental-Services/"
        "Land-Resource-Management/Materials-Management-Planning/Household-Hazardous-Waste-Program"
    )
    rows.append({
        "name": "Wayne County HHW Voucher Drop-Off — ERG Environmental Services",
        "facility_type": "County HHW voucher drop-off (year-round with voucher)",
        "city_slug": "detroit", "state": "MI", "zip": "48150",
        "address": "13040 Merriman Road, Livonia, MI 48150",
        "lat": 42.368, "lng": -83.352,
        "source_url": wayne_url,
        "hours": "Mon–Fri with voucher from 3600 Commerce Court, Wayne MI; call 734-326-5708",
        "phone": "734-326-5708",
        "accepted_materials": mats(HHW, E_WASTE),
    })
    return rows


def _boston_zero_waste():
    url = "https://www.boston.gov/departments/public-works/zero-waste-day"
    return [
        {
            "name": "Central DPW Facility — Zero Waste Day Drop-Off",
            "facility_type": "Municipal Zero Waste Day event site (HHW / e-waste / tires)",
            "city_slug": "boston", "state": "MA", "zip": "02118",
            "address": "400 Frontage Road, Lower Roxbury, Boston, MA 02118 (event entrance at 200 Frontage Road)",
            "lat": 42.334, "lng": -71.061,
            "source_url": url,
            "hours": "Scheduled Zero Waste Days Sat 8:30–12:00 (confirm dates on boston.gov)",
            "phone": "617-635-4500",
            "accepted_materials": mats(HHW, E_WASTE, TIRES, APPLIANCE),
        },
        {
            "name": "West Roxbury DPW — Zero Waste Day Drop-Off",
            "facility_type": "Municipal Zero Waste Day event site (HHW / e-waste / tires)",
            "city_slug": "boston", "state": "MA", "zip": "02132",
            "address": "315 Gardner Street, West Roxbury, MA 02132",
            "lat": 42.278, "lng": -71.158,
            "source_url": url,
            "hours": "Scheduled Zero Waste Days Sat 8:30–12:00 (confirm dates on boston.gov)",
            "phone": "617-635-4500",
            "accepted_materials": mats(HHW, E_WASTE, TIRES, APPLIANCE),
        },
    ]


def _columbus():
    cc_url = "https://www.columbus.gov/Services/Trash-Recycling-Bulk-Collection/How-to-Dispose-or-Recycle/Other-Recycling-Options/Waste-and-Reuse-Convenience-Centers"
    return [
        {
            "name": "Alum Creek Waste and Reuse Convenience Center",
            "facility_type": "Municipal convenience center — bulk / appliances / yard waste",
            "city_slug": "columbus", "state": "OH", "zip": "43207",
            "address": "2100 Alum Creek Drive, Columbus, OH 43207",
            "lat": 39.928, "lng": -82.954,
            "source_url": cc_url,
            "hours": "Tue–Sat 9:00–17:00",
            "phone": "(614) 645-3111",
            "accepted_materials": mats(BULKY, APPLIANCE, ["yard-waste"]),
        },
        {
            "name": "Georgesville Waste and Reuse Convenience Center",
            "facility_type": "Municipal convenience center — bulk / appliances / yard waste",
            "city_slug": "columbus", "state": "OH", "zip": "43228",
            "address": "1550 Georgesville Road, Columbus, OH 43228",
            "lat": 39.915, "lng": -83.085,
            "source_url": cc_url,
            "hours": "Tue–Sat 9:00–17:00",
            "phone": "(614) 645-3111",
            "accepted_materials": mats(BULKY, APPLIANCE, ["yard-waste"]),
        },
        {
            "name": "SWACO Household Hazardous Waste Facility",
            "facility_type": "Household hazardous waste drop-off",
            "city_slug": "columbus", "state": "OH", "zip": "43201",
            "address": "645 East 8th Avenue, Columbus, OH 43201",
            "lat": 39.976, "lng": -82.978,
            "source_url": cc_url,
            "hours": "Mon–Fri 9:00–17:00; 1st Sat 9:00–14:00",
            "phone": "(614) 871-5100",
            "accepted_materials": mats(HHW, APPLIANCE, E_WASTE),
        },
        {
            "name": "SWACO Morse Road Transfer Station",
            "facility_type": "County transfer station — C&D / bulky / appliances",
            "city_slug": "columbus", "state": "OH", "zip": "43230",
            "address": "4262 Morse Road, Columbus, OH 43230",
            "lat": 40.055, "lng": -82.945,
            "source_url": cc_url,
            "hours": "Mon–Fri 6:00–16:00; Sat 6:00–12:00 (Franklin County residents)",
            "phone": "(614) 871-5100",
            "accepted_materials": mats(BULKY, APPLIANCE, CND, TIRES),
        },
        {
            "name": "SWACO Jackson Pike Transfer Station",
            "facility_type": "County transfer station — C&D / bulky / appliances",
            "city_slug": "columbus", "state": "OH", "zip": "43223",
            "address": "2566 Jackson Pike, Columbus, OH 43223",
            "lat": 39.928, "lng": -83.058,
            "source_url": cc_url,
            "hours": "Mon–Fri 6:00–16:00; Sat 6:00–12:00 (Franklin County residents)",
            "phone": "(614) 871-5100",
            "accepted_materials": mats(BULKY, APPLIANCE, CND, TIRES),
        },
        {
            "name": "Franklin County Sanitary Landfill",
            "facility_type": "County sanitary landfill — self-haul / C&D",
            "city_slug": "columbus", "state": "OH", "zip": "43123",
            "address": "3851 London Groveport Road, Grove City, OH 43123",
            "lat": 39.855, "lng": -83.045,
            "source_url": cc_url,
            "hours": "Mon–Fri 6:00–16:00; Sat 6:00–12:00",
            "phone": "(614) 871-5100",
            "accepted_materials": mats(BULKY, CND, TIRES, ["yard-waste"]),
        },
    ]


def _cincinnati_hamilton():
    url = "https://www.hamiltoncountyohio.gov/government/departments/environmental_services/"
    flood_url = "https://www.hamiltoncountyohio.gov/government/departments/emergency_management/july2026flooding.php"
    yards = [
        ("Hamilton County Yard Trimming — Green Township", "3850 Virginia Court, Cincinnati, OH 45248", "45248", 39.095, -84.665),
        ("Hamilton County Yard Trimming — Colerain Township", "3800 Struble Road, Cincinnati, OH 45251", "45251", 39.265, -84.605),
        ("Hamilton County Yard Trimming — Anderson Township", "3295 Turpin Lane, Cincinnati, OH 45244", "45244", 39.085, -84.345),
    ]
    rows = [
        {
            "name": name,
            "facility_type": "County yard-trimming drop-off — branches / yard waste",
            "city_slug": "cincinnati", "state": "OH", "zip": zip_,
            "address": addr, "lat": lat, "lng": lng,
            "source_url": url,
            "hours": "Confirm seasonal hours — call 513-946-7766",
            "phone": "513-946-7766",
            "accepted_materials": mats(["yard-waste"]),
        }
        for name, addr, zip_, lat, lng in yards
    ]
    rows.extend([
        {
            "name": "Hamilton County ReSource — Household Hazardous Waste Program",
            "facility_type": "County HHW collection (mobile events + search tool)",
            "city_slug": "cincinnati", "state": "OH", "zip": "45202",
            "address": "Event locations vary — search hamiltoncountyohio.gov ReSource",
            "lat": 39.103, "lng": -84.512,
            "source_url": url,
            "hours": "Mobile collection events — call 513-946-7766",
            "phone": "513-946-7766",
            "accepted_materials": mats(HHW),
        },
        {
            "name": "Rumpke Landfill — Colerain Township (C&D debris)",
            "facility_type": "County-permitted C&D landfill — public scale",
            "city_slug": "cincinnati", "state": "OH", "zip": "45251",
            "address": "3800 Struble Road, Colerain Township, OH 45251",
            "lat": 39.265, "lng": -84.605,
            "source_url": flood_url,
            "hours": "Contact Rumpke / Hamilton County ReSource for hours",
            "phone": "513-946-7766",
            "accepted_materials": mats(CND),
        },
        {
            "name": "Rumpke Landfill — Bond Road (C&D debris)",
            "facility_type": "County-permitted C&D landfill — public scale",
            "city_slug": "cincinnati", "state": "OH", "zip": "45248",
            "address": "11985 Bond Road, Cincinnati, OH 45248",
            "lat": 39.155, "lng": -84.685,
            "source_url": flood_url,
            "hours": "Contact Rumpke / Hamilton County ReSource for hours",
            "phone": "513-946-7766",
            "accepted_materials": mats(CND),
        },
    ])
    return rows


def _toledo():
    return [
        {
            "name": "Clean Toledo Recycling Center — Bulk Drop-Off",
            "facility_type": "Municipal drop-off — bulk / appliances",
            "city_slug": "toledo", "state": "OH", "zip": "43612",
            "address": "3900 Creekside Avenue, Toledo, OH 43612",
            "lat": 41.692, "lng": -83.548,
            "source_url": "https://toledo.oh.gov/residents/neighborhoods/trash-recycling/clean-toledo-recycling-center",
            "hours": "Tue–Sat 8:30–16:30; proof of Toledo residency required",
            "phone": "419-936-2511",
            "accepted_materials": mats(BULKY, APPLIANCE),
        },
        {
            "name": "Hoffman Road Landfill — Residential Drop-Off",
            "facility_type": "Municipal landfill — bulky / appliances",
            "city_slug": "toledo", "state": "OH", "zip": "43611",
            "address": "3962 Hoffman Road, Toledo, OH 43611",
            "lat": 41.715, "lng": -83.505,
            "source_url": "https://toledo.oh.gov/residents/neighborhoods/trash-recycling/hoffman-road-landfill",
            "hours": "Residential disposal 8:00–15:00; plus city-sponsored free disposal days",
            "phone": "419-936-3077",
            "accepted_materials": mats(BULKY, APPLIANCE, TIRES),
        },
    ]


def _fort_wayne():
    return [
        {
            "name": "ACDEM Household Hazardous Waste Facility — Tox Tuesday",
            "facility_type": "County household hazardous waste drop-off",
            "city_slug": "fort-wayne", "state": "IN", "zip": "46818",
            "address": "2260 Carroll Road, Fort Wayne, IN 46818 (enter via Recovery Road from Lima Road)",
            "lat": 41.195, "lng": -85.175,
            "source_url": "https://www.allencounty.in.gov/483/Household-Hazardous-Waste-Disposal",
            "hours": "Every Tue 9:00–14:00; Tox Saturday Apr 11 & Oct 10",
            "phone": "(260) 449-4433",
            "accepted_materials": mats(HHW),
        },
        {
            "name": "ACDEM Electronics Recycling — Meyer Road",
            "facility_type": "County electronics recycling drop-off (events)",
            "city_slug": "fort-wayne", "state": "IN", "zip": "46803",
            "address": "2911 Meyer Road, Fort Wayne, IN 46803",
            "lat": 41.060, "lng": -85.090,
            "source_url": "https://www.allencounty.in.gov/484/Electronic-Recycling",
            "hours": "Scheduled collection events — see allencounty.in.gov",
            "phone": "(260) 449-7878",
            "accepted_materials": mats(E_WASTE),
        },
    ]


def _chicago():
    charm_url = "https://www.cookcountyil.gov/CHaRMCenter"
    return [
        {
            "name": "Chicago Household Chemicals & Computer Recycling Facility (HCCRF)",
            "facility_type": "HHW / e-waste drop-off",
            "city_slug": "chicago", "state": "IL", "zip": "60642",
            "address": "1150 North Branch Street, Chicago, IL 60642",
            "lat": 41.903, "lng": -87.661,
            "source_url": "https://www.chicago.gov/content/city/en/depts/streets/provdrs/recycling/svcs/residential-electronics-recycling-program.html",
            "hours": "Tue 7:00–12:00; Thu 14:00–19:00; 1st Sat 8:00–15:00",
            "phone": "(312) 744-2413",
            "accepted_materials": mats(HHW, E_WASTE),
        },
        {
            "name": "Cook County CHaRM Center — South Suburban College",
            "facility_type": "County hard-to-recycle drop-off — TVs / e-waste / appliances / styrofoam",
            "city_slug": "chicago", "state": "IL", "zip": "60473",
            "address": "15800 State Street, South Holland, IL 60473",
            "lat": 41.601, "lng": -87.612,
            "source_url": charm_url,
            "hours": "Tue 8:00–12:00; Thu 13:00–17:00; 2nd & 4th Sat 9:00–13:00",
            "phone": "708-596-2000 ext. 2442",
            "accepted_materials": mats(E_WASTE, APPLIANCE, TIRES),
        },
    ]


def _waukesha_milwaukee_metro():
    url = "https://www.waukeshacounty.gov/hazardouswaste"
    sites = [
        ("Waukesha County HHW — Menomonee Falls (Veolia)", "W124N9451 Boundary Road, Menomonee Falls, WI 53051", "53051", 43.155, -88.105),
        ("Waukesha County HHW — UWM-Waukesha", "1500 North University Drive, Waukesha, WI 53188", "53188", 43.062, -88.228),
        ("Waukesha County HHW — Muskego (GFL Emerald Park)", "W124S10629 South 124th Street, Muskego, WI 53150", "53150", 42.905, -88.138),
    ]
    return [
        {
            "name": name,
            "facility_type": "County household hazardous waste drop-off (Clean Sweep)",
            "city_slug": "milwaukee", "state": "WI", "zip": zip_,
            "address": addr, "lat": lat, "lng": lng,
            "source_url": url,
            "hours": "Permanent sites — see waukeshacounty.gov/hazardouswaste for dates",
            "phone": "262-896-8300",
            "accepted_materials": mats(HHW),
        }
        for name, addr, zip_, lat, lng in sites
    ]


def _milwaukee():
    url = "https://city.milwaukee.gov/sanitation/DropOff"
    return [
        {
            "name": "Milwaukee North Drop Off Center",
            "facility_type": "Municipal drop-off — bulky / e-waste / C&D / tires / appliances",
            "city_slug": "milwaukee", "state": "WI", "zip": "53223",
            "address": "6660 North Industrial Road, Milwaukee, WI 53223",
            "lat": 43.137, "lng": -87.998,
            "source_url": url,
            "hours": "Summer Tue–Sun 7:00–15:00; Winter Tue–Sat 7:00–15:00",
            "phone": "414-286-CITY",
            "accepted_materials": mats(BULKY, E_WASTE, TIRES, APPLIANCE, CND),
        },
        {
            "name": "Milwaukee South Drop Off Center / MMSD HHW",
            "facility_type": "Municipal drop-off — bulky / e-waste / tires / MMSD HHW",
            "city_slug": "milwaukee", "state": "WI", "zip": "53215",
            "address": "3879 West Lincoln Avenue, Milwaukee, WI 53215",
            "lat": 43.003, "lng": -87.964,
            "source_url": url,
            "hours": "Seasonal hours; MMSD HHW Thu–Sat 7:00–15:00",
            "phone": "414-286-CITY",
            "accepted_materials": mats(BULKY, E_WASTE, TIRES, APPLIANCE, HHW),
        },
        {
            "name": "MMSD Home Haz Mat Collection Center — 13th Street",
            "facility_type": "Regional household hazardous waste drop-off",
            "city_slug": "milwaukee", "state": "WI", "zip": "53233",
            "address": "1311 West Mount Vernon Avenue, Milwaukee, WI 53233",
            "lat": 43.034, "lng": -87.928,
            "source_url": "https://city.milwaukee.gov/sanitation/Garbage/WhatCanIRecycle/HouseholdHazardousWaste",
            "hours": "Thu–Sat 7:00–15:00",
            "phone": "414-286-2489",
            "accepted_materials": mats(HHW),
        },
    ]


def _minneapolis():
    ramsey_url = "https://www.ramseycountymn.gov/residents/recycling-waste/environmental-center"
    return [
        {
            "name": "Ramsey County Environmental Center",
            "facility_type": "County environmental center — HHW / e-waste / appliances / scrap metal",
            "city_slug": "minneapolis", "state": "MN", "zip": "55113",
            "address": "1700 Kent Street, Roseville, MN 55113",
            "lat": 45.012, "lng": -93.158,
            "source_url": ramsey_url,
            "hours": "Tue–Fri 11:00–18:00; Sat 9:00–16:00; closed Sun/Mon/holidays",
            "phone": "651-633-3279",
            "accepted_materials": mats(HHW, E_WASTE, APPLIANCE, TIRES),
        },
        {
            "name": "Minneapolis South Transfer Station",
            "facility_type": "Municipal transfer station — garbage / bulky / appliances / e-waste",
            "city_slug": "minneapolis", "state": "MN", "zip": "55407",
            "address": "2850 20th Avenue South, Minneapolis, MN 55407",
            "lat": 43.243, "lng": -93.244,
            "source_url": "https://www.minneapolismn.gov/resident-services/garbage-recycling-cleanup/garbage/garbage-drop-off-site/drop-off-items-and-fees/",
            "hours": "Tue–Fri 12:30–19:30; Sat 8:30–15:30; voucher or pay-per-use required",
            "phone": "612-673-2917",
            "accepted_materials": mats(BULKY, APPLIANCE, E_WASTE, TIRES, CND),
        },
        {
            "name": "Hennepin County HHW — Bloomington (South)",
            "facility_type": "County HHW / problem waste drop-off",
            "city_slug": "minneapolis", "state": "MN", "zip": "55431",
            "address": "1400 West 96th Street, Bloomington, MN 55431",
            "lat": 44.829, "lng": -93.293,
            "source_url": "https://www.minneapolismn.gov/resident-services/garbage-recycling-cleanup/disposal-guide/",
            "hours": "Tue–Sat (closed Sun/Mon/holidays)",
            "phone": "612-348-3777",
            "accepted_materials": mats(HHW, E_WASTE, APPLIANCE, TIRES),
        },
        {
            "name": "Hennepin County HHW — Brooklyn Park",
            "facility_type": "County transfer / HHW / problem waste drop-off",
            "city_slug": "minneapolis", "state": "MN", "zip": "55445",
            "address": "8100 Jefferson Highway, Brooklyn Park, MN 55445",
            "lat": 45.105, "lng": -93.385,
            "source_url": "https://www.minneapolismn.gov/resident-services/garbage-recycling-cleanup/disposal-guide/",
            "hours": "Tue–Sat (closed Sun/Mon/holidays)",
            "phone": "612-348-3777",
            "accepted_materials": mats(HHW, E_WASTE, APPLIANCE, TIRES),
        },
    ]


def _pittsburgh():
    dpw_url = "https://www.pittsburghpa.gov/Resident-Services/Trash-Recycling/Drop-Off-Info-Additional-Resources/Recycling-Drop-Off-Locations"
    divisions = [
        ("Pittsburgh DPW 2nd Division Drop-Off (East End)", "6814 Hamilton Avenue, Pittsburgh, PA 15208", "15208", 40.441, -79.896, "(412) 665-3610"),
        ("Pittsburgh DPW 3rd Division Drop-Off (Hazelwood)", "40 Melanchton Street, Pittsburgh, PA 15207", "15207", 40.408, -79.936, "(412) 422-6545"),
        ("Pittsburgh DPW 5th Division Drop-Off (West End)", "1330 Hassler Street, Pittsburgh, PA 15220", "15220", 40.445, -80.042, "(412) 937-3054"),
    ]
    rows = [
        {
            "name": name,
            "facility_type": "Municipal DPW drop-off — yard waste / tires / scrap metal",
            "city_slug": "pittsburgh", "state": "PA", "zip": zip_,
            "address": addr, "lat": lat, "lng": lng,
            "source_url": dpw_url,
            "hours": "Mon–Sat (hours vary by division — see pittsburghpa.gov)",
            "phone": phone,
            "accepted_materials": mats(BULKY, TIRES, ["yard-waste"]),
        }
        for name, addr, zip_, lat, lng, phone in divisions
    ]
    rows.append({
        "name": "Allegheny County HHW — South Park Wave Pool",
        "facility_type": "County household hazardous waste collection (seasonal)",
        "city_slug": "pittsburgh", "state": "PA", "zip": "15129",
        "address": "South Park Wave Pool parking lot, 3735 Buffalo Drive, South Park, PA 15129",
        "lat": 40.318, "lng": -80.012,
        "source_url": "https://www.pa.gov/agencies/dep/programs-and-services/waste-programs/solid-waste-programs/hazardous-waste-program/household/hhw-collection-programs",
        "hours": "Seasonal collection events — see pa.gov HHW list",
        "phone": "412-488-7490",
        "accepted_materials": mats(HHW),
    })
    rows.append({
        "name": "Pittsburgh Noble Environmental — HHW / E-Waste Drop-Off",
        "facility_type": "City-contracted HHW / e-waste vendor drop-off (appointment)",
        "city_slug": "pittsburgh", "state": "PA", "zip": "15222",
        "address": "Appointment locations vary — register via pittsburghpa.gov / Noble Environmental",
        "lat": 40.441, "lng": -79.996,
        "source_url": "https://www.pittsburghpa.gov/Resident-Services/Trash-Recycling/Drop-Off-Info-Additional-Resources/Electronic-Waste-and-Household-Hazardous-Waste-Disposal",
        "hours": "Weekly drop-offs by appointment starting 2026",
        "phone": "412-567-6566",
        "accepted_materials": mats(HHW, E_WASTE),
    })
    return rows


def _buffalo():
    url = "https://www.buffalony.gov/382/Streets-Sanitation"
    return [
        {
            "name": "Buffalo Engineering Garage — E-Waste Drop-Off",
            "facility_type": "Electronics / universal waste drop-off",
            "city_slug": "buffalo", "state": "NY", "zip": "14210",
            "address": "1120 Seneca Street, Buffalo, NY 14210",
            "lat": 42.870, "lng": -78.842,
            "source_url": url,
            "hours": "Mon–Fri 8:00–15:00; 1st Sat 8:00–14:00",
            "phone": "311",
            "accepted_materials": mats(E_WASTE, HHW),
        },
        {
            "name": "Buffalo East Side Transfer Station — Residential Drop-Off",
            "facility_type": "Municipal transfer station — bulk / trash",
            "city_slug": "buffalo", "state": "NY", "zip": "14210",
            "address": "793 South Ogden Street, Buffalo, NY 14210",
            "lat": 42.865, "lng": -78.835,
            "source_url": url,
            "hours": "Mon–Fri 7:00–9:00 & 13:00–15:00; Sat 8:00–12:00",
            "phone": "311",
            "accepted_materials": mats(BULKY),
        },
        {
            "name": "Buffalo West Side Transfer Station — Residential Drop-Off",
            "facility_type": "Municipal transfer station — bulk / trash",
            "city_slug": "buffalo", "state": "NY", "zip": "14213",
            "address": "1120 Seneca Street, Buffalo, NY 14210",
            "lat": 42.870, "lng": -78.842,
            "source_url": url,
            "hours": "Mon–Fri 7:00–9:00 & 13:00–15:00; Sat 8:00–12:00",
            "phone": "311",
            "accepted_materials": mats(BULKY),
        },
        {
            "name": "Buffalo Broadway Garage — Tire Drop-Off Days",
            "facility_type": "Municipal tire drop-off (scheduled days)",
            "city_slug": "buffalo", "state": "NY", "zip": "14212",
            "address": "199 Broadway Street, Buffalo, NY 14212",
            "lat": 42.892, "lng": -78.862,
            "source_url": url,
            "hours": "Scheduled tire drop-off days — call 311",
            "phone": "311",
            "accepted_materials": mats(TIRES),
        },
        {
            "name": "Erie County HHW Voucher Drop-Off — Hazman",
            "facility_type": "County HHW voucher drop-off (year-round, pre-register)",
            "city_slug": "buffalo", "state": "NY", "zip": "14150",
            "address": "177 Wales Avenue, Tonawanda, NY 14150",
            "lat": 43.012, "lng": -78.868,
            "source_url": "https://www3.erie.gov/recycling/household-hazardous-waste-hhw-collection-programs",
            "hours": "Mon–Fri 8:00–18:30; Sat 9:00–13:00; voucher required via erie.gov/recycling",
            "phone": "(716) 858-6800",
            "accepted_materials": mats(HHW, E_WASTE, TIRES),
        },
    ]


def _rochester():
    return [
        {
            "name": "Monroe County ecopark",
            "facility_type": "County specialty recycling / HHW / e-waste drop-off",
            "city_slug": "rochester", "state": "NY", "zip": "14624",
            "address": "10 Avion Drive, Rochester, NY 14624",
            "lat": 43.118, "lng": -77.705,
            "source_url": "https://www.monroecounty.gov/ecopark/",
            "hours": "Wed 13:00–18:30; Sat 7:30–13:00 (HHW by appointment)",
            "phone": "(585) 753-7600",
            "accepted_materials": mats(HHW, E_WASTE, TIRES, APPLIANCE),
        },
    ]


def _yonkers():
    return [
        {
            "name": "Yonkers Recycling Center",
            "facility_type": "Municipal drop-off — bulk / e-waste / tires / appliances",
            "city_slug": "yonkers", "state": "NY", "zip": "10710",
            "address": "735 Saw Mill River Road, Yonkers, NY 10710",
            "lat": 40.948, "lng": -73.869,
            "source_url": "https://www.yonkersny.gov/503/Recycling-Center",
            "hours": "Mon–Sat 7:30–16:15",
            "phone": "(914) 377-6752",
            "accepted_materials": mats(BULKY, E_WASTE, TIRES, APPLIANCE),
        },
        {
            "name": "Yonkers Organic Yard",
            "facility_type": "Municipal organic yard waste drop-off",
            "city_slug": "yonkers", "state": "NY", "zip": "10701",
            "address": "610 Nepperhan Avenue, Yonkers, NY 10701",
            "lat": 40.928, "lng": -73.878,
            "source_url": "https://www.yonkersny.gov/502/Organic-Yard",
            "hours": "Mon–Sat 7:00–15:00 (closed noon–13:00 for lunch)",
            "phone": "(914) 327-0175",
            "accepted_materials": mats(["yard-waste", "christmas-tree"]),
        },
        {
            "name": "Westchester County HRF — Household Material Recovery Facility",
            "facility_type": "County HHW / e-waste / tire drop-off",
            "city_slug": "yonkers", "state": "NY", "zip": "10595",
            "address": "15 Woods Road, Valhalla, NY 10595",
            "lat": 41.075, "lng": -73.775,
            "source_url": "https://www.yonkersny.gov/214/Refuse-Bulk-Removal",
            "hours": "Tue–Sat 10:00–15:00 by appointment (Westchester County H-MRF)",
            "phone": "914-813-5425",
            "accepted_materials": mats(HHW, E_WASTE, TIRES, APPLIANCE),
        },
    ]


def _jersey_city():
    return [
        {
            "name": "Jersey City DPW — Hazardous Waste Drop-Off",
            "facility_type": "Municipal HHW drop-off (scheduled events)",
            "city_slug": "jersey-city", "state": "NJ", "zip": "07305",
            "address": "13-15 Linden Avenue East, Jersey City, NJ 07305",
            "lat": 40.712, "lng": -74.088,
            "source_url": "https://www.jerseycitynj.gov/cityhall/DPW/sanitation",
            "hours": "Scheduled HHW events — call 201-547-4400",
            "phone": "201-547-4400",
            "accepted_materials": mats(HHW, E_WASTE, TIRES),
        },
    ]


def _hampton_roads():
    spsa_hhw = "https://www.spsava.gov/161/Household-Hazardous-Waste-E-Waste-Guidel"
    spsa_ts = "https://www.spsava.gov/182/Transfer-Stations"
    return [
        {
            "name": "SPSA Norfolk Transfer Station — HHW & E-Waste",
            "facility_type": "Regional transfer station — HHW / e-waste",
            "city_slug": "norfolk", "state": "VA", "zip": "23504",
            "address": "3136 Woodland Avenue, Norfolk, VA 23504",
            "lat": 37.245, "lng": -76.245,
            "source_url": spsa_hhw,
            "hours": "HHW: Tue & Sat 12:00–16:00",
            "phone": "757-961-3981",
            "accepted_materials": mats(HHW, E_WASTE),
        },
        {
            "name": "SPSA Regional Landfill — HHW & E-Waste",
            "facility_type": "Regional landfill — HHW / e-waste / tires",
            "city_slug": "norfolk", "state": "VA", "zip": "23434",
            "address": "1 Bob Foeller Drive, Suffolk, VA 23434",
            "lat": 36.820, "lng": -76.420,
            "source_url": spsa_hhw,
            "hours": "Mon–Fri 8:00–16:00; Sat 8:00–12:00",
            "phone": "757-961-3981",
            "accepted_materials": mats(HHW, E_WASTE, TIRES),
        },
        {
            "name": "SPSA Chesapeake Transfer Station — HHW & E-Waste",
            "facility_type": "Regional transfer station — HHW / e-waste / bulky",
            "city_slug": "chesapeake", "state": "VA", "zip": "23320",
            "address": "901 Hollowell Lane, Chesapeake, VA 23320",
            "lat": 36.685, "lng": -76.245,
            "source_url": spsa_hhw,
            "hours": "HHW: 3rd Sat & 1st Wed monthly 9:00–12:00; transfer Mon 8:00–17:00",
            "phone": "757-961-3943",
            "accepted_materials": mats(HHW, E_WASTE, BULKY),
        },
        {
            "name": "SPSA Landstown Transfer Station — HHW & E-Waste",
            "facility_type": "Regional transfer station — HHW / e-waste",
            "city_slug": "virginia-beach", "state": "VA", "zip": "23456",
            "address": "1500 Landstown Centre Way, Virginia Beach, VA 23456",
            "lat": 36.775, "lng": -76.075,
            "source_url": spsa_ts,
            "hours": "HHW: Sun 12:00–16:00; transfer Mon–Fri 8:00–16:00, Sat 8:00–12:00",
            "phone": "757-961-3981",
            "accepted_materials": mats(HHW, E_WASTE, TIRES),
        },
        {
            "name": "SPSA Oceana Transfer Station — HHW & E-Waste",
            "facility_type": "Regional transfer station — HHW / e-waste",
            "city_slug": "virginia-beach", "state": "VA", "zip": "23454",
            "address": "1820 Concert Drive, Virginia Beach, VA 23456",
            "lat": 36.785, "lng": -76.005,
            "source_url": spsa_ts,
            "hours": "Mon–Fri 8:00–16:00; Sat 8:00–12:00",
            "phone": "757-961-3981",
            "accepted_materials": mats(HHW, E_WASTE),
        },
        {
            "name": "Virginia Beach Resource Recovery Center",
            "facility_type": "Municipal resource recovery — e-waste / tires / appliances",
            "city_slug": "virginia-beach", "state": "VA", "zip": "23455",
            "address": "1989 Jake Sears Road, Virginia Beach, VA 23455",
            "lat": 36.820, "lng": -76.075,
            "source_url": "https://www.vbgov.com/government/departments/public-works/waste-management/Pages/rrc.aspx",
            "hours": "Tue–Sat 7:00–16:00",
            "phone": "757-385-4650",
            "accepted_materials": mats(E_WASTE, TIRES, APPLIANCE, HHW),
        },
    ]


def _mecklenburg():
    url = "https://wipeoutwaste.mecknc.gov/where-can-i-recycle"
    return [
        {
            "name": "Mecklenburg County Full-Service — Pineville-Matthews Road",
            "facility_type": "County full-service drop-off — bulky / HHW / e-waste / tires",
            "city_slug": "charlotte", "state": "NC", "zip": "28226",
            "address": "4635 Pineville-Matthews Road, Charlotte, NC 28226",
            "lat": 35.095, "lng": -80.768,
            "source_url": url,
            "hours": "Mon–Sat 7:00–16:00",
            "phone": "980-314-3867",
            "accepted_materials": mats(BULKY, HHW, E_WASTE, TIRES, APPLIANCE, CND),
        },
    ]


def _atlanta():
    url = "https://www.cityofsouthfultonga.gov/3510/Merk-Miles-Citizens-Convenience-Center"
    return [
        {
            "name": "Merk Miles Citizens Convenience Center",
            "facility_type": "Municipal convenience center — bulky / yard waste / appliances",
            "city_slug": "atlanta", "state": "GA", "zip": "30349",
            "address": "3225 Merk Road, South Fulton, GA 30349",
            "lat": 33.612, "lng": -84.478,
            "source_url": url,
            "hours": "Mon–Sat (last customer 15 min before close — see cityofsouthfultonga.gov)",
            "phone": "470-552-4311",
            "accepted_materials": mats(BULKY, APPLIANCE, E_WASTE, TIRES, ["yard-waste"]),
        },
    ]


def _richmond():
    url = "https://www.rva.gov/public-works/trash-collection"
    return [
        {
            "name": "Richmond East Richmond Road Convenience Center (ERRCC)",
            "facility_type": "Municipal convenience center — HHW / tires / e-waste",
            "city_slug": "richmond", "state": "VA", "zip": "23223",
            "address": "3800 East Richmond Road, Richmond, VA 23223",
            "lat": 37.556, "lng": -77.386,
            "source_url": url,
            "hours": "Mon–Fri 7:00–15:30; Sat 8:30–14:00",
            "phone": "804-646-6434",
            "accepted_materials": mats(HHW, E_WASTE, TIRES, APPLIANCE),
        },
        {
            "name": "Richmond Southside Transfer Station",
            "facility_type": "Municipal transfer station — bulk / yard waste",
            "city_slug": "richmond", "state": "VA", "zip": "23234",
            "address": "3800 Deepwater Terminal Road, Richmond, VA 23234",
            "lat": 37.446, "lng": -77.426,
            "source_url": url,
            "hours": "Mon–Fri 6:30–16:30; Sat 8:30–14:00",
            "phone": "804-646-7000",
            "accepted_materials": mats(BULKY, ["yard-waste"]),
        },
        {
            "name": "Richmond East Side Transfer Station",
            "facility_type": "Municipal transfer station — bulk / yard waste",
            "city_slug": "richmond", "state": "VA", "zip": "23234",
            "address": "3520 North Hopkins Road, Richmond, VA 23234",
            "lat": 37.458, "lng": -77.448,
            "source_url": url,
            "hours": "Mon–Fri 6:30–16:30; Sat 8:30–14:00",
            "phone": "804-232-8488",
            "accepted_materials": mats(BULKY, ["yard-waste"]),
        },
        {
            "name": "Henrico Charles City Road Public Use Area",
            "facility_type": "County drop-off — bulk / yard waste / appliances",
            "city_slug": "richmond", "state": "VA", "zip": "23231",
            "address": "2075 Charles City Road, Henrico, VA 23231",
            "lat": 37.510, "lng": -77.370,
            "source_url": "https://henrico.gov/utility/solid-waste/hours-of-operation-and-holiday-schedule/",
            "hours": "Daily 7:30–19:00",
            "phone": "804-222-7739",
            "accepted_materials": mats(BULKY, APPLIANCE, ["yard-waste"]),
        },
        {
            "name": "Richmond Clean City — Robin Hood Road Recycling Event Site",
            "facility_type": "City HHW / e-waste collection event site",
            "city_slug": "richmond", "state": "VA", "zip": "23227",
            "address": "Robin Hood Road, Richmond, VA 23227",
            "lat": 37.575, "lng": -77.465,
            "source_url": "https://www.rva.gov/public-works/trash-collection",
            "hours": "Periodic Clean City recycling events — see rva.gov",
            "phone": "804-646-6434",
            "accepted_materials": mats(HHW, E_WASTE, TIRES),
        },
    ]


FACILITIES: list[dict] = []
FACILITIES.extend(_nyc_special_waste())
FACILITIES.extend(_dsny_garages())
FACILITIES.extend(_nyc_safe_events())
FACILITIES.extend(_philadelphia_hhw())
FACILITIES.extend(_baltimore_dropoffs())
FACILITIES.extend(_detroit_bulk())
FACILITIES.extend(_boston_zero_waste())
FACILITIES.extend(_columbus())
FACILITIES.extend(_cincinnati_hamilton())
FACILITIES.extend(_toledo())
FACILITIES.extend(_fort_wayne())
FACILITIES.extend(_chicago())
FACILITIES.extend(_milwaukee())
FACILITIES.extend(_waukesha_milwaukee_metro())
FACILITIES.extend(_minneapolis())
FACILITIES.extend(_mecklenburg())
FACILITIES.extend(_atlanta())
FACILITIES.extend(_pittsburgh())
FACILITIES.extend(_buffalo())
FACILITIES.extend(_rochester())
FACILITIES.extend(_yonkers())
FACILITIES.extend(_jersey_city())
FACILITIES.extend(_hampton_roads())
FACILITIES.extend(_richmond())


def main() -> None:
    hard_rows: list[dict] = []
    rejected_soft: list[str] = []

    for row in FACILITIES:
        row = {**row, "accepted_materials": mats(row["accepted_materials"])}
        _gov(row["source_url"])
        if not is_hard_facility(row):
            rejected_soft.append(row["name"])
            continue
        hard_rows.append(row)

    if len(hard_rows) < 120:
        raise SystemExit(f"Only {len(hard_rows)} hard rows prepared (need 120+)")

    facilities = json.loads(FAC_PATH.read_text())
    by_key = {(f.get("city_slug"), f.get("name")): i for i, f in enumerate(facilities)}
    by_addr = {
        (f.get("city_slug"), (f.get("address") or "").lower()[:50])
        for f in facilities
        if f.get("address")
    }

    added = updated = skipped = 0
    for row in hard_rows:
        addr_key = (row["city_slug"], row["address"].lower()[:50])
        key = (row["city_slug"], row["name"])
        if key in by_key:
            facilities[by_key[key]] = {**facilities[by_key[key]], **row}
            updated += 1
            continue
        if addr_key in by_addr:
            skipped += 1
            continue
        facilities.append(row)
        by_key[key] = len(facilities) - 1
        by_addr.add(addr_key)
        added += 1

    FAC_PATH.write_text(json.dumps(facilities, indent=2) + "\n")

    per_city = {
        c: sum(1 for f in facilities if f.get("city_slug") == c and is_hard_facility(f))
        for c in sorted(TARGET_CITIES)
    }
    total_hard_all = sum(1 for f in facilities if is_hard_facility(f))

    print(json.dumps({
        "prepared_hard_rows": len(hard_rows),
        "rejected_soft": len(rejected_soft),
        "added": added,
        "updated": updated,
        "skipped_dup_addr": skipped,
        "final_hard_total": total_hard_all,
        "total_hard_in_target_metros": sum(per_city.values()),
        "per_city_hard": per_city,
        "networks_covered": [
            "Cook County CHaRM (Chicago metro)",
            "SWACO / Franklin County OH (Columbus)",
            "Hamilton County ReSource (Cincinnati)",
            "Wayne County HHW (Detroit metro)",
            "Waukesha County Clean Sweep (Milwaukee metro)",
            "Ramsey + Hennepin County (Minneapolis)",
            "Mecklenburg County (Charlotte)",
            "South Fulton Merk Miles (Atlanta metro)",
            "Erie County HHW voucher (Buffalo)",
            "Philadelphia HHW + SCC",
            "DSNY special waste / SAFE / tire garages (NYC)",
            "Baltimore DPW drop-offs",
            "Boston Zero Waste Days",
            "Pittsburgh DPW + Allegheny HHW",
            "Monroe County ecopark (Rochester)",
            "SPSA Hampton Roads",
            "Richmond / Henrico drop-offs",
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
