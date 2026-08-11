#!/usr/bin/env python3
"""MW/Northeast metro full .gov drop-off inventory (2026-08-11).

Cities: new-york, philadelphia, boston, baltimore, pittsburgh, buffalo, rochester,
yonkers, jersey-city, chicago, detroit, milwaukee, minneapolis, columbus, cincinnati,
toledo, indianapolis, fort-wayne. (Cleveland skipped — SWACO/Columbus area.)

Sources verified against official .gov pages only.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAC_PATH = ROOT / "data" / "facilities" / "all.json"
ITEMS = {i["slug"] for i in json.loads((ROOT / "data" / "items.json").read_text())}

HHW = [
    "paint-latex", "paint-oil", "pesticides", "herbicides", "pool-chemicals",
    "gasoline", "motor-oil", "antifreeze", "car-battery", "household-batteries",
    "lithium-battery", "fluorescent-bulbs", "propane-tank", "cooking-oil",
]
E_WASTE = [
    "television", "computer-monitor", "laptop", "desktop-computer", "printer",
    "tablet", "smartphone", "microwave", "hard-drive", "e-waste-mixed", "ink-toner",
]
BULKY = ["mattress", "box-spring", "sofa", "recliner", "carpet", "yard-waste"]
APPLIANCE = [
    "refrigerator", "freezer", "air-conditioner", "washer", "dryer",
    "dishwasher", "stove", "water-heater",
]
TIRES = ["tires", "tire-rims"]
RECYCLE = ["cardboard", "glass-bottles", "plastic-bags"]
FOOD = ["food-scraps"]


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


DSNY_GARAGE_URL = "https://www.nyc.gov/site/dsny/about/about-dsny/garage-locations.page"
DSNY_SW_URL = "https://www.nyc.gov/site/dsny/what-we-do/programs/special-waste-drop-off.page"
DSNY_TIRE_URL = "https://www.nyc.gov/site/dsny/collection/get-rid-of/automotive-waste.page"

# Unique DSNY district-garage addresses (tire drop-off Mon–Sat 10:00–17:30)
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

PROJECT_OSCAR = [
    ("Project Oscar — Beacon Hill", "200 Cambridge Street, Boston, MA 02114", "02114", 42.361, -71.068),
    ("Project Oscar — Brighton (Faneuil Gardens)", "Faneuil Gardens Apartments, Brighton, MA 02135", "02135", 42.348, -71.156),
    ("Project Oscar — Brighton (Boston Green Academy)", "Boston Green Academy, Cambridge Street, Brighton, MA 02135", "02135", 42.349, -71.145),
    ("Project Oscar — Brighton (Commonwealth Ave)", "1825 Commonwealth Avenue, Brighton, MA 02135", "02135", 42.342, -71.152),
    ("Project Oscar — Charlestown", "31 Austin Street, Charlestown, MA 02129", "02129", 42.374, -71.063),
    ("Project Oscar — Chinatown", "240 Hudson Street, Boston, MA 02111", "02111", 42.350, -71.062),
    ("Project Oscar — City Hall Plaza", "1 City Hall Square, Boston, MA 02201", "02201", 42.360, -71.058),
    ("Project Oscar — Dorchester (Codman Square)", "690 Washington Street, Dorchester, MA 02124", "02124", 42.287, -71.071),
    ("Project Oscar — East Boston", "Memorial Stadium Park, Thompson Drive, East Boston, MA 02128", "02128", 42.385, -71.016),
    ("Project Oscar — Fenway", "New Edgerly Plaza, Fenway, Boston, MA 02215", "02215", 42.343, -71.097),
    ("Project Oscar — Hyde Park", "1234 Hyde Park Avenue, Hyde Park, MA 02136", "02136", 42.254, -71.125),
    ("Project Oscar — Jamaica Plain (Curtis Hall)", "20 South Street, Jamaica Plain, MA 02130", "02130", 42.309, -71.115),
    ("Project Oscar — Jamaica Plain (Centre St)", "490 Centre Street, Jamaica Plain, MA 02130", "02130", 42.313, -71.113),
    ("Project Oscar — Mission Hill", "1481 Tremont Street, Mission Hill, Boston, MA 02120", "02120", 42.333, -71.099),
    ("Project Oscar — North End", "30 North Bennet Street, North End, Boston, MA 02113", "02113", 42.364, -71.054),
    ("Project Oscar — Roslindale", "4210 Washington Street, Roslindale, MA 02131", "02131", 42.287, -71.130),
    ("Project Oscar — Roxbury", "3042 Washington Street, Roxbury, MA 02119", "02119", 42.322, -71.079),
    ("Project Oscar — South Boston", "450 West Broadway, South Boston, MA 02127", "02127", 42.336, -71.049),
    ("Project Oscar — South End", "685 Tremont Street, South End, Boston, MA 02118", "02118", 42.341, -71.073),
    ("Project Oscar — West End", "Causeway Street at Lovejoy Wharf, West End, Boston, MA 02114", "02114", 42.366, -71.060),
]

CINCINNATI_DUMPSTERS = [
    ("Public Recycling Dumpster — French Park", "3012 Section Road, Cincinnati, OH 45237", "45237", 39.200, -84.418),
    ("Public Recycling Dumpster — Lebo's", "5869 Kellogg Avenue, Cincinnati, OH 45230", "45230", 39.065, -84.405),
    ("Public Recycling Dumpster — River Metals Recycling", "2815 Spring Grove Avenue, Cincinnati, OH 45214", "45214", 39.128, -84.542),
    ("Public Recycling Dumpster — Downtown", "Third Street & Central Avenue (NE corner), Cincinnati, OH 45202", "45202", 39.100, -84.512),
    ("Public Recycling Dumpster — Mt. Echo Park", "202 Crestline Avenue, Cincinnati, OH 45205", "45205", 39.108, -84.563),
    ("Public Recycling Dumpster — Madisonville Recreation Center", "5320 Stewart Avenue, Cincinnati, OH 45227", "45227", 39.168, -84.378),
    ("Public Recycling Dumpster — Madisonville Recycle", "6300 Warrick Street, Cincinnati, OH 45227", "45227", 39.165, -84.382),
    ("Public Recycling Dumpster — Mount Airy Forest", "5083 Colerain Avenue, Cincinnati, OH 45223", "45223", 39.185, -84.548),
    ("Public Recycling Dumpster — Ault Park", "5090 Observatory Avenue, Cincinnati, OH 45208", "45208", 39.139, -84.410),
    ("Public Recycling Dumpster — Building Value", "4040 Spring Grove Avenue, Cincinnati, OH 45223", "45223", 39.162, -84.542),
    ("Public Recycling Dumpster — Parks Maintenance Facility", "2080 Sinton Road, Cincinnati, OH 45206", "45206", 39.125, -84.472),
    ("Public Recycling Dumpster — Lincoln Recreation Center", "1027 Linn Street, Cincinnati, OH 45203", "45203", 39.108, -84.526),
    ("Public Recycling Dumpster — Dunham Recreation Center", "1945 Dunham Way, Cincinnati, OH 45238", "45238", 39.127, -84.598),
    ("Public Recycling Dumpster — Maple Ridge Lodge", "3040 Westwood Northern Boulevard, Cincinnati, OH 45211", "45211", 39.152, -84.598),
]

COLUMBUS_FOOD_SCRAPS = [
    ("Food Scraps Drop-Off — Bill McDonald Athletic Complex", "4990 Olentangy River Road, Columbus, OH 43214", "43214", 40.068, -83.025),
    ("Food Scraps Drop-Off — Dodge Park Community Center", "667 Sullivant Avenue, Columbus, OH 43215", "43215", 39.956, -83.016),
    ("Food Scraps Drop-Off — Scioto Southland Park", "3901 Parsons Avenue, Columbus, OH 43207", "43207", 39.887, -82.984),
    ("Food Scraps Drop-Off — Beatty Park Recreation Center", "247 N. Ohio Avenue, Columbus, OH 43203", "43203", 39.968, -82.967),
    ("Food Scraps Drop-Off — Northeast Park", "2505 Cassady Avenue, Columbus, OH 43219", "43219", 39.985, -82.934),
    ("Food Scraps Drop-Off — Linden Park Community Center", "1350 Briarwood Avenue, Columbus, OH 43211", "43211", 40.008, -82.964),
    ("Food Scraps Drop-Off — Carriage Place Park", "4900 Sawmill Road, Columbus, OH 43235", "43235", 40.063, -83.091),
]

BUFFALO_FOOD_SCRAPS = [
    ("Scrap It! Food Scraps — Massachusetts Ave Project", "387 Massachusetts Avenue, Buffalo, NY 14213", "14213", 42.918, -78.882),
    ("Scrap It! Food Scraps — Dog Ears Bookstore", "688 Abbott Road, Buffalo, NY 14220", "14220", 42.842, -78.823),
    ("Scrap It! Food Scraps — Eugene V. Debs Hall", "483 Peckham Street, Buffalo, NY 14206", "14206", 42.886, -78.808),
    ("Scrap It! Food Scraps — Elmwood & St. James", "Corner of Elmwood Avenue & St. James Place, Buffalo, NY 14222", "14222", 42.918, -78.877),
]

TOLEDO_FOOD = [
    ("Food Waste Drop-Off — Glass City Metropark", "701 Front Street, Toledo, OH 43605", "43605", 41.635, -83.515),
    ("Food Waste Drop-Off — Toledo Botanical Garden", "5430 W Bancroft Street, Toledo, OH 43615", "43615", 41.663, -83.628),
    ("Food Waste Drop-Off — Swan Creek Metropark", "4301 Airport Highway, Toledo, OH 43615", "43615", 41.618, -83.644),
]


def _dsny_garages():
    rows = []
    for name, addr, zip_, lat, lng in DSNY_GARAGES:
        rows.append({
            "name": name,
            "facility_type": "DSNY district garage — tire drop-off",
            "city_slug": "new-york",
            "state": "NY",
            "zip": zip_,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": DSNY_TIRE_URL,
            "hours": "Mon–Sat 10:00–17:30 (closed holidays); NYC resident ID + vehicle registration required",
            "phone": "311",
            "accepted_materials": mats(TIRES),
        })
    return rows


def _project_oscar():
    url = "https://www.boston.gov/departments/public-works/project-oscar"
    return [
        {
            "name": name,
            "facility_type": "Community food-scrap drop-off bin (Project Oscar)",
            "city_slug": "boston",
            "state": "MA",
            "zip": zip_,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": url,
            "hours": "24/7; lock code 2-1-4",
            "phone": "617-635-4500",
            "accepted_materials": mats(FOOD),
        }
        for name, addr, zip_, lat, lng in PROJECT_OSCAR
    ]


def _cincinnati():
    url = "https://www.cincinnati-oh.gov/recycling/public-dropoff/public-recycling-dumpsters/"
    return [
        {
            "name": name,
            "facility_type": "Public recycling drop-off dumpster",
            "city_slug": "cincinnati",
            "state": "OH",
            "zip": zip_,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": url,
            "hours": "See cincinnati-oh.gov for site hours",
            "phone": "513-765-1212",
            "accepted_materials": mats(RECYCLE),
        }
        for name, addr, zip_, lat, lng in CINCINNATI_DUMPSTERS
    ]


def _columbus_food():
    url = "https://www.columbus.gov/Services/Trash-Recycling-Bulk-Collection/Household-Trash-Collection/Food-Waste-Prevention"
    return [
        {
            "name": name,
            "facility_type": "Food-scrap drop-off (24-hour)",
            "city_slug": "columbus",
            "state": "OH",
            "zip": zip_,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": url,
            "hours": "24 hours/day",
            "phone": "(614) 645-3111",
            "accepted_materials": mats(FOOD),
        }
        for name, addr, zip_, lat, lng in COLUMBUS_FOOD_SCRAPS
    ]


def _buffalo_food():
    url = "https://www.buffalony.gov/CivicAlerts.aspx?AID=1170"
    return [
        {
            "name": name,
            "facility_type": "Food-scrap drop-off (Scrap It!)",
            "city_slug": "buffalo",
            "state": "NY",
            "zip": zip_,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": url,
            "hours": "Permanent drop-off — check buffalony.gov for access",
            "phone": "311",
            "accepted_materials": mats(FOOD),
        }
        for name, addr, zip_, lat, lng in BUFFALO_FOOD_SCRAPS
    ]


def _toledo_food():
    url = "https://toledo.oh.gov/residents/neighborhoods/trash-recycling"
    return [
        {
            "name": name,
            "facility_type": "Food-scrap drop-off (GoZERO tote)",
            "city_slug": "toledo",
            "state": "OH",
            "zip": zip_,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": url,
            "hours": "Metropark hours (approx. 7:00–dark)",
            "phone": "419-936-2511",
            "accepted_materials": mats(FOOD),
        }
        for name, addr, zip_, lat, lng in TOLEDO_FOOD
    ]


UPSERTS = [
    # --- NYC special waste (full 5-borough inventory) ---
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
    # --- Chicago (official 2 recycling + HCCRF) ---
    {
        "name": "Chicago Residential Recycling Drop-Off — Far North Side",
        "facility_type": "Municipal recycling drop-off center",
        "city_slug": "chicago", "state": "IL", "zip": "60660",
        "address": "6441 N Ravenswood Avenue, Chicago, IL 60660",
        "lat": 41.999, "lng": -87.675,
        "source_url": "https://www.chicago.gov/city/en/sites/chicago-recycles/home/residential-recycling.html",
        "hours": "7 days/week during daylight hours",
        "phone": "(312) 744-2413",
        "accepted_materials": mats(RECYCLE),
    },
    {
        "name": "Chicago Residential Recycling Drop-Off — Near South",
        "facility_type": "Municipal recycling drop-off center",
        "city_slug": "chicago", "state": "IL", "zip": "60616",
        "address": "1758 S Clark Street, Chicago, IL 60616",
        "lat": 41.857, "lng": -87.631,
        "source_url": "https://www.chicago.gov/city/en/sites/chicago-recycles/home/residential-recycling.html",
        "hours": "7 days/week during daylight hours",
        "phone": "(312) 744-2413",
        "accepted_materials": mats(RECYCLE),
    },
    {
        "name": "Chicago Household Chemicals & Computer Recycling Facility (HCCRF)",
        "facility_type": "HHW / e-waste drop-off",
        "city_slug": "chicago", "state": "IL", "zip": "60642",
        "address": "1150 N North Branch Street, Chicago, IL 60642",
        "lat": 41.903, "lng": -87.661,
        "source_url": "https://www.chicago.gov/content/city/en/depts/streets/provdrs/recycling/svcs/residential-electronics-recycling-program.html",
        "hours": "Tue 7:00–12:00; Thu 14:00–19:00; 1st Sat 8:00–15:00",
        "phone": "(312) 744-2413",
        "accepted_materials": mats(HHW, E_WASTE),
    },
    # --- Detroit bulk yards + HHW ---
    {
        "name": "DPW Davison Yard — Free Citizen Bulk Drop-Off",
        "facility_type": "Municipal bulk / yard waste drop-off center",
        "city_slug": "detroit", "state": "MI", "zip": "48238",
        "address": "8221 W Davison Avenue, Detroit, MI 48238",
        "lat": 42.396, "lng": -83.140,
        "source_url": "https://detroitmi.gov/departments/department-public-works/refuse-collection/bulk-yard-waste/free-citizen-bulk-drop-centers",
        "hours": "Mon–Sat; Apr 1–Oct 31 8:00–18:00; Nov 1–Mar 31 8:00–16:00",
        "phone": "(313) 876-0004",
        "accepted_materials": mats(BULKY, TIRES),
    },
    {
        "name": "DPW Southfield Yard — Free Citizen Bulk Drop-Off",
        "facility_type": "Municipal bulk / yard waste drop-off center",
        "city_slug": "detroit", "state": "MI", "zip": "48227",
        "address": "12255 Southfield Road, Detroit, MI 48227",
        "lat": 42.372, "lng": -83.224,
        "source_url": "https://detroitmi.gov/departments/general-services-department/free-dumping-detroiters",
        "hours": "Mon–Sat; Apr 1–Oct 31 8:00–18:00; Nov 1–Mar 31 8:00–16:00",
        "phone": "(313) 876-0004",
        "accepted_materials": mats(BULKY, TIRES),
    },
    {
        "name": "DPW J. Fons Transfer Station — Free Citizen Bulk Drop-Off",
        "facility_type": "Municipal bulk / yard waste drop-off center",
        "city_slug": "detroit", "state": "MI", "zip": "48234",
        "address": "6451 E McNichols Road, Detroit, MI 48234",
        "lat": 42.416, "lng": -83.048,
        "source_url": "https://detroitmi.gov/departments/general-services-department/free-dumping-detroiters",
        "hours": "Mon–Fri 8:00–16:00; Sat 8:00–12:00",
        "phone": "(313) 876-0004",
        "accepted_materials": mats(BULKY, TIRES),
    },
    {
        "name": "DPW Household Hazardous Waste Receiving Facility",
        "facility_type": "Household hazardous waste / e-waste drop-off",
        "city_slug": "detroit", "state": "MI", "zip": "48207",
        "address": "2000 E Ferry Street, Detroit, MI 48207",
        "lat": 42.358, "lng": -83.019,
        "source_url": "https://detroitmi.gov/departments/department-public-works/refuse-collection/household-hazardous-waste-information",
        "hours": "Thu 7:30–14:00; 4th Sat 8:00–14:00",
        "phone": "(313) 923-2240",
        "accepted_materials": mats(HHW, E_WASTE),
    },
    # --- Pittsburgh DPW divisions + glass ---
    {
        "name": "Pittsburgh DPW 2nd Division Drop-Off (East End)",
        "facility_type": "Municipal recycling / yard / tire drop-off",
        "city_slug": "pittsburgh", "state": "PA", "zip": "15208",
        "address": "6814 Hamilton Avenue, Pittsburgh, PA 15208",
        "lat": 40.441, "lng": -79.896,
        "source_url": "https://www.pittsburghpa.gov/Resident-Services/Trash-Recycling/Drop-Off-Info-Additional-Resources/Recycling-Drop-Off-Locations",
        "hours": "Mon–Sat 8:00–13:30",
        "phone": "(412) 665-3610",
        "accepted_materials": mats(RECYCLE, BULKY, TIRES),
    },
    {
        "name": "Pittsburgh DPW 3rd Division Drop-Off (Hazelwood)",
        "facility_type": "Municipal recycling / yard / tire drop-off",
        "city_slug": "pittsburgh", "state": "PA", "zip": "15207",
        "address": "40 Melanchton Street, Pittsburgh, PA 15207",
        "lat": 40.408, "lng": -79.936,
        "source_url": "https://www.pittsburghpa.gov/Resident-Services/Trash-Recycling/Drop-Off-Info-Additional-Resources/Recycling-Drop-Off-Locations",
        "hours": "Mon–Fri 8:00–13:30",
        "phone": "(412) 422-6545",
        "accepted_materials": mats(RECYCLE, BULKY, TIRES),
    },
    {
        "name": "Pittsburgh DPW 5th Division Drop-Off (West End)",
        "facility_type": "Municipal recycling / yard / tire drop-off",
        "city_slug": "pittsburgh", "state": "PA", "zip": "15220",
        "address": "1330 Hassler Street, Pittsburgh, PA 15220",
        "lat": 40.445, "lng": -80.042,
        "source_url": "https://www.pittsburghpa.gov/Resident-Services/Trash-Recycling/Drop-Off-Info-Additional-Resources/Recycling-Drop-Off-Locations",
        "hours": "Mon–Fri 8:00–14:00; Sat 7:00–15:00",
        "phone": "(412) 937-3054",
        "accepted_materials": mats(RECYCLE, BULKY, TIRES),
    },
    {
        "name": "Strip District Glass Recycling Drop-Off",
        "facility_type": "Glass recycling drop-off (24-hour)",
        "city_slug": "pittsburgh", "state": "PA", "zip": "15201",
        "address": "3001 Railroad Street, Pittsburgh, PA 15201",
        "lat": 40.456, "lng": -79.976,
        "source_url": "https://www.pittsburghpa.gov/Resident-Services/Trash-Recycling/Drop-Off-Info-Additional-Resources/Recycling-Drop-Off-Locations",
        "hours": "24 hours / 7 days",
        "phone": "(412) 255-2631",
        "accepted_materials": mats(["glass-bottles"]),
    },
    {
        "name": "Construction Junction Recycling Drop-Off",
        "facility_type": "Recycling drop-off center",
        "city_slug": "pittsburgh", "state": "PA", "zip": "15208",
        "address": "214 North Lexington Street, Pittsburgh, PA 15208",
        "lat": 40.441, "lng": -79.898,
        "source_url": "https://www.pittsburghpa.gov/Resident-Services/Trash-Recycling/Drop-Off-Info-Additional-Resources/Recycling-Drop-Off-Locations",
        "hours": "Mon–Sat 9:00–17:00",
        "phone": "(412) 243-5025",
        "accepted_materials": mats(RECYCLE),
    },
    # --- Buffalo ---
    {
        "name": "Buffalo Engineering Garage — E-Waste Drop-Off",
        "facility_type": "Electronics / universal waste drop-off",
        "city_slug": "buffalo", "state": "NY", "zip": "14210",
        "address": "1120 Seneca Street, Buffalo, NY 14210",
        "lat": 42.870, "lng": -78.842,
        "source_url": "https://www.buffalony.gov/DocumentCenter/View/3937/COB-recycling-flier",
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
        "source_url": "https://www.buffalony.gov/382/Streets-Sanitation",
        "hours": "Mon–Fri 7:00–9:00 & 13:00–15:00; Sat 8:00–12:00",
        "phone": "311",
        "accepted_materials": mats(BULKY),
    },
    # --- Milwaukee ---
    {
        "name": "Milwaukee North Drop Off Center",
        "facility_type": "Municipal drop-off — bulky / e-waste / C&D / tires",
        "city_slug": "milwaukee", "state": "WI", "zip": "53223",
        "address": "6660 N Industrial Road, Milwaukee, WI 53223",
        "lat": 43.137, "lng": -87.998,
        "source_url": "https://city.milwaukee.gov/sanitation/DropOff",
        "hours": "Seasonal hours — check city.milwaukee.gov",
        "phone": "414-286-CITY",
        "accepted_materials": mats(BULKY, E_WASTE, TIRES, APPLIANCE),
    },
    {
        "name": "Milwaukee South Drop Off Center",
        "facility_type": "Municipal drop-off — bulky / e-waste / C&D / tires / MMSD HHW",
        "city_slug": "milwaukee", "state": "WI", "zip": "53215",
        "address": "3879 W Lincoln Avenue, Milwaukee, WI 53215",
        "lat": 43.003, "lng": -87.964,
        "source_url": "https://city.milwaukee.gov/sanitation/DropOff",
        "hours": "Seasonal hours — check city.milwaukee.gov; MMSD HHW Thu–Sat 7:00–15:00",
        "phone": "414-286-CITY",
        "accepted_materials": mats(BULKY, E_WASTE, TIRES, APPLIANCE, HHW),
    },
    # --- Indianapolis ToxDrop (3rd site) ---
    {
        "name": "Marion County ToxDrop — IMPD Training Facility",
        "facility_type": "Household hazardous waste drop-off (monthly event)",
        "city_slug": "indianapolis", "state": "IN", "zip": "46219",
        "address": "9049 E 10th Street, Indianapolis, IN 46219",
        "lat": 39.781, "lng": -86.010,
        "source_url": "https://www.indy.gov/activity/hazardous-waste-dropoff-sites",
        "hours": "3rd Sat 9:00–14:00 (Marion County residents only)",
        "phone": "(317) 327-4622",
        "accepted_materials": mats(HHW, E_WASTE),
    },
    # --- Fort Wayne ACDEM ---
    {
        "name": "ACDEM Northwest Recycling Hub",
        "facility_type": "County community recycling drop-off",
        "city_slug": "fort-wayne", "state": "IN", "zip": "46818",
        "address": "2260 Carroll Road, Fort Wayne, IN 46818",
        "lat": 41.199, "lng": -85.175,
        "source_url": "https://www.allencounty.in.gov/468/Community-Recycling-Drop-off-Sites",
        "hours": "Mon–Fri 8:00–16:00",
        "phone": "(260) 449-7878",
        "accepted_materials": mats(RECYCLE),
    },
    {
        "name": "ACDEM Republic Services — MacBeth Road Drop-Off",
        "facility_type": "County community recycling drop-off",
        "city_slug": "fort-wayne", "state": "IN", "zip": "46809",
        "address": "6231 MacBeth Road, Fort Wayne, IN 46809",
        "lat": 41.030, "lng": -85.220,
        "source_url": "https://www.allencounty.in.gov/468/Community-Recycling-Drop-off-Sites",
        "hours": "Mon–Fri 8:00–13:00 & 13:30–16:30",
        "phone": "(260) 449-7878",
        "accepted_materials": mats(RECYCLE),
    },
    {
        "name": "ACDEM Republic Services MRF — Pontiac Street Drop-Off",
        "facility_type": "County community recycling drop-off",
        "city_slug": "fort-wayne", "state": "IN", "zip": "46803",
        "address": "2509 East Pontiac Street, Fort Wayne, IN 46803",
        "lat": 41.062, "lng": -85.105,
        "source_url": "https://www.allencounty.in.gov/468/Community-Recycling-Drop-off-Sites",
        "hours": "Mon–Fri 6:00–15:30 (no attendant)",
        "phone": "(260) 449-7878",
        "accepted_materials": mats(RECYCLE),
    },
    # --- Baltimore (Reedbird limited Saturday) ---
    {
        "name": "Reedbird Residential Recycling Center (Western)",
        "facility_type": "Residential recycling / bulky drop-off",
        "city_slug": "baltimore", "state": "MD", "zip": "21225",
        "address": "701 Reedbird Avenue, Baltimore, MD 21225",
        "lat": 39.238, "lng": -76.612,
        "source_url": "https://www.baltimorecity.gov/publicworks/solid-waste/drop-off",
        "hours": "Sat 9:00–19:00 (limited schedule during modernization)",
        "phone": "(410) 396-3367",
        "accepted_materials": mats(BULKY, E_WASTE, RECYCLE, APPLIANCE, TIRES),
    },
    # --- Rochester ecopark ---
    {
        "name": "Monroe County ecopark",
        "facility_type": "County specialty recycling / HHW / e-waste drop-off",
        "city_slug": "rochester", "state": "NY", "zip": "14624",
        "address": "10 Avion Drive, Rochester, NY 14624",
        "lat": 43.118, "lng": -77.705,
        "source_url": "https://www.monroecounty.gov/ecopark/",
        "hours": "Wed 13:00–18:30; Sat 7:30–13:00 (HHW by appointment)",
        "phone": "(585) 753-7600",
        "accepted_materials": mats(HHW, E_WASTE, TIRES, APPLIANCE, RECYCLE),
    },
    # --- Yonkers ---
    {
        "name": "Yonkers Recycling Center",
        "facility_type": "Municipal recycling / bulk / e-waste drop-off",
        "city_slug": "yonkers", "state": "NY", "zip": "10710",
        "address": "735 Saw Mill River Road, Yonkers, NY 10710",
        "lat": 40.948, "lng": -73.869,
        "source_url": "https://www.yonkersny.gov/503/Recycling-Center",
        "hours": "Mon–Sat 7:30–16:15",
        "phone": "(914) 377-6752",
        "accepted_materials": mats(RECYCLE, BULKY, E_WASTE, TIRES, APPLIANCE),
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
    # --- SWACO Columbus area (skip Cleveland) ---
    {
        "name": "SWACO Household Hazardous Waste Facility",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "columbus", "state": "OH", "zip": "43201",
        "address": "645 E 8th Avenue, Columbus, OH 43201",
        "lat": 39.976, "lng": -82.978,
        "source_url": "https://www.columbus.gov/Services/Trash-Recycling-Bulk-Collection/How-to-Dispose-or-Recycle/Other-Recycling-Options/Waste-and-Reuse-Convenience-Centers",
        "hours": "Mon–Fri 9:00–17:00; 1st Sat 9:00–14:00",
        "phone": "(614) 871-5100",
        "accepted_materials": mats(HHW),
    },
    {
        "name": "SWACO Recycling Convenience Center — Jackson Pike",
        "facility_type": "County recycling drop-off center",
        "city_slug": "columbus", "state": "OH", "zip": "43223",
        "address": "2566 Jackson Pike, Columbus, OH 43223",
        "lat": 39.928, "lng": -83.058,
        "source_url": "https://www.columbus.gov/Services/Trash-Recycling-Bulk-Collection/Household-Trash-Collection/Food-Waste-Prevention",
        "hours": "Check SWACO/columbus.gov for current hours",
        "phone": "(614) 871-5100",
        "accepted_materials": mats(RECYCLE, FOOD),
    },
    # --- Toledo permanent ---
    {
        "name": "Clean Toledo Recycling Center",
        "facility_type": "Municipal recycling / bulk drop-off center",
        "city_slug": "toledo", "state": "OH", "zip": "43612",
        "address": "3900 Creekside Avenue, Toledo, OH 43612",
        "lat": 41.692, "lng": -83.548,
        "source_url": "https://toledo.oh.gov/residents/neighborhoods/trash-recycling/clean-toledo-recycling-center",
        "hours": "Tue–Sat 8:30–16:30; proof of Toledo residency required",
        "phone": "419-936-2511",
        "accepted_materials": mats(BULKY, RECYCLE),
    },
]

UPSERTS.extend(_dsny_garages())
UPSERTS.extend(_project_oscar())
UPSERTS.extend(_cincinnati())
UPSERTS.extend(_columbus_food())
UPSERTS.extend(_buffalo_food())
UPSERTS.extend(_toledo_food())


def main() -> None:
    facilities = json.loads(FAC_PATH.read_text())
    by_key = {(f.get("city_slug"), f.get("name")): i for i, f in enumerate(facilities)}
    by_addr = {
        (f.get("city_slug"), (f.get("address") or "").lower()[:50])
        for f in facilities
        if f.get("address")
    }
    added = updated = skipped = 0
    for row in UPSERTS:
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
    print(f"Facilities: {len(facilities)} (added {added}, updated {updated}, skipped {skipped})")
    print(f"Upsert rows prepared: {len(UPSERTS)}")


if __name__ == "__main__":
    main()
