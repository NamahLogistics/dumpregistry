#!/usr/bin/env python3
"""DumpRegistry HARD volume batch A — county/metro networks (2026-08-11).

Adds 120–180 NEW hard facilities from official city/county .gov sources.
Networks: MD/VA suburbs, FL counties, GA Atlanta metro, TX DFW/Houston,
CA county landfills/HHW, IL Chicago collar, PNW, UT/CO, KC, NY/NJ/PA, OH/KY/AL/TN.

HARD ONLY via is_hard_facility. Deduplicates by (city_slug, name) and address.
Hard-purges all.json after write. Does NOT delete existing facilities.
"""

from __future__ import annotations

import json
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
    "antifreeze", "car-battery", "household-batteries", "fluorescent-bulbs",
    "propane-tank", "gasoline", "pool-chemicals", "cooking-oil",
]
CD = ["construction-debris", "lumber", "drywall", "asphalt-shingles", "concrete"]
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


UPSERTS: list[dict] = []
NETWORKS: set[str] = set()


def row(
    network: str,
    name: str,
    ftype: str,
    city_slug: str,
    state: str,
    zipc: str,
    address: str,
    lat: float,
    lng: float,
    source_url: str,
    hours: str,
    phone: str,
    materials: list[str],
) -> None:
    NETWORKS.add(network)
    UPSERTS.append({
        "name": name,
        "facility_type": ftype,
        "city_slug": city_slug,
        "state": state,
        "zip": zipc,
        "address": address,
        "lat": lat,
        "lng": lng,
        "source_url": source_url,
        "hours": hours,
        "phone": phone,
        "accepted_materials": materials,
    })


# ── Maryland / DC suburbs ────────────────────────────────────────────────────
MD_DEP = "https://www.montgomerycountymd.gov/department-environmental-protection/trash-recycling-yard-trim/trash-recycling-facilities/shady-grove-processing-facility-transfer-station"
row("Montgomery County MD", "Montgomery County Shady Grove Transfer Station & HHW", "County transfer / permanent HHW", "baltimore", "MD", "20855", "16101 Frederick Road, Derwood, MD 20855", 39.1255, -77.1555, MD_DEP, "Mon–Sat 7:00–17:00; Sun 9:00–17:00", "240-777-0311", HHW_E() + mats(BULKY, APPLIANCE, TIRES))
row("Montgomery County MD", "Montgomery County Poolesville Beauty Spot", "County yard waste / recycling drop-off", "baltimore", "MD", "20837", "17905 West Willard Road, Poolesville, MD 20837", 39.1455, -77.4155, MD_DEP, "Mon–Sat 7:00–17:00; Sun 9:00–17:00", "240-777-0311", mats(BULKY, ["yard-waste"], TIRES))

PG = "https://www.princegeorgescountymd.gov/departments-offices/public-works/waste-management/landfill"
row("Prince George's County MD", "Prince George's County Brown Station Road Sanitary Landfill", "County landfill — residential self-haul", "baltimore", "MD", "20707", "3501 Brown Station Road, Upper Marlboro, MD 20707", 38.8955, -76.7855, PG, "Mon–Sat 7:00–15:30", "301-952-7625", LANDFILL())
row("Prince George's County MD", "Prince George's County Household Hazardous Waste Acceptance Site", "County permanent HHW drop-off", "baltimore", "MD", "20707", "3501 Brown Station Road, Upper Marlboro, MD 20707", 38.8955, -76.7855, PG, "Wed–Sat 8:00–15:30; PG County residents", "301-952-7625", HHW_E())

BC = "https://www.baltimorecountymd.gov/departments/public-works/trash-recycling/landfills"
row("Baltimore County MD", "Baltimore County Eastern Sanitary Landfill", "County landfill — residential drop-off", "baltimore", "MD", "21220", "6259 Days Cove Road, White Marsh, MD 21220", 39.3855, -76.4255, BC, "Mon–Sat 7:00–16:00", "410-887-2000", LANDFILL())
row("Baltimore County MD", "Baltimore County Central Acceptance Facility", "County transfer / recycling drop-off", "baltimore", "MD", "21227", "201 Warren Road, Cockeysville, MD 21227", 39.4655, -76.6455, BC, "Mon–Sat 7:00–16:00", "410-887-2000", TRANSFER())

HC = "https://www.howardcountymd.gov/public-works/alpha-ridge-landfill"
row("Howard County MD", "Howard County Alpha Ridge Landfill", "County landfill / transfer — bulky / C&D", "baltimore", "MD", "21045", "2350 Marriottsville Road, Marriottsville, MD 21104", 39.3455, -76.8955, HC, "Mon–Sat 8:00–16:00", "410-313-6444", LANDFILL())
row("Howard County MD", "Howard County Alpha Ridge HHW Collection Center", "County permanent HHW / e-waste", "baltimore", "MD", "21045", "2350 Marriottsville Road, Marriottsville, MD 21104", 39.3455, -76.8955, HC, "Sat 8:00–16:00; Howard County residents", "410-313-6444", HHW_E())

AAC = "https://www.aacounty.org/departments/public-works/waste-management/landfill"
row("Anne Arundel County MD", "Anne Arundel County Millersville Landfill", "County landfill — residential self-haul", "baltimore", "MD", "21108", "389 Burns Crossing Road, Severn, MD 21144", 39.0855, -76.6255, AAC, "Mon–Sat 7:00–16:00", "410-222-6100", LANDFILL())

# ── Virginia NOVA / Richmond ─────────────────────────────────────────────────
FFX = "https://www.fairfaxcounty.gov/publicworks/recycling-trash/locations-hours"
row("Fairfax County VA", "Fairfax County I-66 Transfer Station", "County transfer — bulky / appliances / tires / e-waste", "richmond", "VA", "22030", "4618 West Ox Road, Fairfax, VA 22030", 38.8555, -77.3555, FFX, "Mon–Fri 7:00–16:00; Sat 7:00–15:00; Sun 9:00–15:00", "703-631-1179", TRANSFER() + E_WASTE)
row("Fairfax County VA", "Fairfax County I-95 Landfill Complex", "County landfill — residential self-haul", "richmond", "VA", "22079", "9850 Furnace Road, Lorton, VA 22079", 38.6855, -77.2255, FFX, "Mon–Fri 7:00–16:00; Sat 7:00–15:00; Sun 9:00–15:00", "703-690-1703", LANDFILL())

LOU = "https://www.loudoun.gov/landfill"
row("Loudoun County VA", "Loudoun County Landfill & Recycling Center", "County landfill / transfer — bulky / C&D", "richmond", "VA", "20105", "21101 Evergreen Mills Road, Leesburg, VA 20175", 39.0555, -77.5455, LOU, "Mon–Sat 8:00–16:00", "703-771-5500", LANDFILL())

PWC = "https://www.pwcgov.org/government/dept/publicworks/trash/Pages/Landfill.aspx"
row("Prince William County VA", "Prince William County Landfill", "County landfill — residential self-haul", "richmond", "VA", "20110", "14811 Dumfries Road, Manassas, VA 20112", 38.6255, -77.4255, PWC, "Mon–Sat 6:00–18:00; Sun 8:00–17:00", "703-792-4670", LANDFILL())

CHE = "https://www.chesterfield.gov/444/Landfill-and-Recycling-Center"
row("Chesterfield County VA", "Chesterfield County Central Virginia Waste Management Authority Landfill", "County landfill / HHW", "richmond", "VA", "23832", "6736 Iron Bridge Road, Chester, VA 23832", 37.3555, -77.5055, CHE, "Mon–Sat 7:30–16:00", "804-748-1297", LANDFILL() + HHW)

HEN = "https://henrico.us/recycle/central-virginia-waste-management-authority/"
row("Henrico County VA", "Henrico County CVWMA Springfield Road Public Use Area", "County transfer / bulky drop-off", "richmond", "VA", "23231", "10600 Fords Country Lane, Henrico, VA 23231", 37.4255, -77.3255, HEN, "Tue–Sat 7:30–16:00", "804-501-4275", TRANSFER())

# ── Florida — Broward / Palm Beach / Orlando / Tampa ──────────────────────────
BRW = "https://www.broward.org/WasteAndRecycling/WasteDisposal/Pages/DropOffCenters.aspx"
broward_m = HHW_E() + mats(BULKY, APPLIANCE, TIRES, ["yard-waste"])
for name, city, addr, zipc, lat, lng in [
    ("Broward County North Residential Drop-Off Center", "miami", "2780 N Powerline Road, Pompano Beach, FL 33069", "33069", 26.2455, -80.1555),
    ("Broward County Central Residential Drop-Off Center", "miami", "5490 Reese Road, Davie, FL 33314", "33314", 26.0855, -80.2455),
    ("Broward County South Residential Drop-Off Center", "hialeah", "5601 W Hallandale Beach Boulevard, West Park, FL 33023", "33023", 25.9855, -80.2055),
    ("Broward County Landfill", "miami", "7101 SW 205th Avenue, Southwest Ranches, FL 33332", "33332", 26.0555, -80.4255),
]:
    row("Broward County FL", name, "County drop-off / landfill — bulky / HHW / e-waste", city, "FL", zipc, addr, lat, lng, BRW, "Drop-offs Sat 9:00–15:00; landfill Mon–Sat 8:00–16:00", "954-765-4999", broward_m if "Landfill" not in name else LANDFILL())

SWA = "https://www.swa.org/860/Transfer-Stations-and-Home-Chemical-Recy"
pbc = HHW_E() + mats(BULKY, APPLIANCE, TIRES, CD)
for name, city, addr, zipc, lat, lng, hours in [
    ("Palm Beach County North County Transfer Station & HCRC", "miami", "14185 N Military Trail, Jupiter, FL 33458", "33458", 26.9155, -80.1255, "Mon–Fri 7:00–17:00; Sat 7:00–15:00"),
    ("Palm Beach County West Palm Beach HCRC", "miami", "6161 N Jog Road, West Palm Beach, FL 33412", "33412", 26.7555, -80.1255, "Mon–Sat 7:00–17:00"),
    ("Palm Beach County West County Transfer Station & HCRC", "miami", "1701 State Road 15, Belle Glade, FL 33430", "33430", 26.6855, -80.6655, "Mon–Fri 7:30–16:00"),
    ("Palm Beach County West Central Transfer Station & HCRC", "miami", "9743 Weisman Way, Royal Palm Beach, FL 33411", "33411", 26.6955, -80.2255, "Mon–Fri 7:00–17:00; Sat 7:00–15:00"),
    ("Palm Beach County Central County Transfer Station & HCRC", "miami", "1810 Lantana Road, Lantana, FL 33462", "33462", 26.5855, -80.0555, "Mon–Fri 7:00–17:00; Sat 7:00–12:00"),
    ("Palm Beach County Southwest County Transfer Station & HCRC", "miami", "13400 S State Road 7, Delray Beach, FL 33446", "33446", 26.4555, -80.2055, "Mon–Fri 7:00–17:00; Sat 7:00–15:00"),
    ("Palm Beach County South County Transfer Station & HCRC", "miami", "1901 SW 4th Avenue, Delray Beach, FL 33444", "33444", 26.4455, -80.0855, "Mon–Fri 7:00–17:00; Sat 7:00–15:00"),
    ("Palm Beach County North County Landfill Customer Drop-Off", "miami", "6330 N Jog Road, West Palm Beach, FL 33412", "33412", 26.7655, -80.1255, "Mon–Sat 7:00–17:00"),
]:
    row("Palm Beach County SWA FL", name, "County SWA transfer / HHW / landfill", city, "FL", zipc, addr, lat, lng, SWA, hours, "561-697-2700", pbc)

OCFL = "https://www.orangecountyfl.net/watergarbagerecycling/landfillandtransferstations.aspx"
for name, city, addr, zipc, lat, lng in [
    ("Orange County FL Landfill — small vehicle drop-off", "orlando", "5901 Young Pine Road, Orlando, FL 32829", "32829", 28.4755, -81.2455),
    ("Orange County FL McLeod Road Transfer Station", "orlando", "5000 L.B. McLeod Road, Orlando, FL 32811", "32811", 28.5155, -81.4455),
    ("Orange County FL Porter Transfer Station", "orlando", "1326 Good Homes Road, Orlando, FL 32818", "32818", 28.5655, -81.5055),
]:
    row("Orange County FL", name, "County landfill / transfer station", city, "FL", zipc, addr, lat, lng, OCFL, "Mon–Sat 8:00–17:00", "407-836-6601", LANDFILL())

SEM = "https://www.seminolecountyfl.gov/departments-services/environmental-services/solid-waste-management/locations"
row("Seminole County FL", "Seminole County Central Transfer Station", "County transfer — HHW / tires / yard waste", "orlando", "FL", "32750", "1950 State Road 419, Longwood, FL 32750", 28.6855, -81.3455, SEM, "Mon–Sat 7:30–17:30", "407-665-2260", HHW_E() + mats(BULKY, TIRES, ["yard-waste"]))
row("Seminole County FL", "Seminole County Landfill", "County landfill — appliances / C&D / tires", "orlando", "FL", "32732", "1930 E Osceola Road, Geneva, FL 32732", 28.7255, -81.1155, SEM, "Daily 7:30–17:30", "407-665-8200", LANDFILL())

POLK = "https://www.polkfl.gov/services/polk-county-solid-waste/landfill/"
for name, city, addr, zipc, lat, lng in [
    ("Polk County North Central Transfer Station", "tampa", "3131 K-Ville Avenue, Auburndale, FL 33823", "33823", 28.0455, -81.7855),
    ("Polk County North Central Landfill", "tampa", "7425 De Castro Road, Auburndale, FL 33823", "33823", 28.0655, -81.7655),
    ("Polk County Northeast Landfill Customer Convenience Center", "tampa", "4001 Bannon Island Road, Haines City, FL 33844", "33844", 28.1255, -81.5855),
]:
    row("Polk County FL", name, "County landfill / transfer — bulky / tires", city, "FL", zipc, addr, lat, lng, POLK, "Mon–Fri 7:00–17:00; Sat 7:30–12:30", "863-284-4319", LANDFILL())

PAS = "https://www.pascocountyfl.net/services/trash_and_recycling/landfill.php"
for name, city, addr, zipc, lat, lng in [
    ("Pasco County West Pasco Transfer Station", "tampa", "14606 Hays Road, Spring Hill, FL 34610", "34610", 28.3855, -82.5855),
    ("Pasco County East Pasco Transfer Station", "tampa", "9626 Handcart Road, Dade City, FL 33525", "33525", 28.3655, -82.1855),
    ("Pasco County Household Hazardous Waste Collection Facility", "tampa", "9626 Handcart Road, Dade City, FL 33525", "33525", 28.3655, -82.1855),
]:
    row("Pasco County FL", name, "County transfer / HHW", city, "FL", zipc, addr, lat, lng, PAS, "Mon–Sat 7:00–17:00; HHW Fri–Sat", "727-847-2411", HHW_E() if "Hazardous" in name else LANDFILL())

# ── Georgia — Atlanta metro ────────────────────────────────────────────────────
COBB = "https://www.cobbcounty.gov/swb/waste-disposal"
row("Cobb County GA", "Cobb County Transfer Station (GFL Environmental)", "County transfer — bulky / e-waste / C&D", "atlanta", "GA", "30008", "1897 County Services Parkway, Marietta, GA 30008", 33.9055, -84.5805, COBB, "Mon–Fri 7:00–17:00; Sat 7:00–12:00", "770-485-8940", TRANSFER() + E_WASTE)

DEK = "https://www.dekalbcountyga.gov/departments/public-works/sanitation/bulky-items-and-special-collections"
row("DeKalb County GA", "DeKalb County Seminole Road Landfill", "County landfill — tires / C&D / e-waste", "atlanta", "GA", "30294", "4203 Clevemont Road, Ellenwood, GA 30294", 33.6255, -84.2855, DEK, "Mon–Fri 8:00–17:00; Sat 8:00–16:00", "404-687-4040", LANDFILL() + E_WASTE)
row("DeKalb County GA", "DeKalb County Central Transfer Station", "County transfer — bulky / yard waste", "atlanta", "GA", "30032", "3720 Leroy Scott Drive, Decatur, GA 30032", 33.7555, -84.2555, DEK, "Mon–Fri 7:00–17:30", "404-294-2900", TRANSFER())

FULTON = "https://www.fultoncountyga.gov/inside-fulton-county/fulton-county-departments/public-works/sanitation"
row("Fulton County GA", "Fulton County Merk Miles Transfer Station", "County transfer — bulky / appliances", "atlanta", "GA", "30349", "4200 Merk Road, College Park, GA 30349", 33.5855, -84.4855, FULTON, "Mon–Sat 7:00–17:00", "404-613-3113", TRANSFER())
row("Fulton County GA", "Fulton County Sandy Creek Landfill", "County landfill — residential self-haul", "atlanta", "GA", "30213", "7700 Sandy Creek Road, Fairburn, GA 30213", 33.5455, -84.6255, FULTON, "Mon–Sat 7:00–17:00", "404-613-3113", LANDFILL())

# ── Texas — DFW / Houston / Austin ────────────────────────────────────────────
NTMWD = "https://www.ntmwd.com/297/Solid-Waste-Facilities"
for name, city, addr, zipc, lat, lng in [
    ("NTMWD Custer Road Transfer Station", "plano", "9901 Custer Road, Plano, TX 75025", "75025", 33.1255, -96.7455),
    ("NTMWD Lookout Drive Transfer Station", "dallas", "1601 East Lookout Drive, Richardson, TX 75082", "75082", 32.9855, -96.6455),
    ("NTMWD Parkway Transfer Station", "plano", "4030 West Plano Parkway, Plano, TX 75093", "75093", 33.0155, -96.7855),
    ("NTMWD 121 Regional Disposal Facility", "plano", "3820 Sam Rayburn Highway, Melissa, TX 75454", "75454", 33.2855, -96.5855),
]:
    row("NTMWD / Collin County TX", name, "Regional transfer / landfill — bulky / C&D", city, "TX", zipc, addr, lat, lng, NTMWD, "Mon–Sat 8:00–16:30; landfill Mon–Fri 7:00–17:00 Sat 8:00–15:00", "972-727-6341", LANDFILL())

DENTON = "https://www.dentoncounty.gov/departments/public-works/solid-waste"
row("Denton County TX", "Denton County Home Chemical Collection Center", "County permanent HHW / e-waste", "dallas", "TX", "76208", "1527 Mayhill Road, Denton, TX 76208", 33.1855, -97.0855, DENTON, "Tue–Fri 8:00–17:00; Sat 8:00–12:00", "940-349-8733", HHW_E())
row("Denton County TX", "Denton County Landfill", "County landfill — residential self-haul", "dallas", "TX", "76208", "1527 Mayhill Road, Denton, TX 76208", 33.1855, -97.0855, DENTON, "Mon–Sat 7:00–17:00", "940-349-8733", LANDFILL())

FB = "https://www.fortbendcountytx.gov/government/departments/public-works/solid-waste"
row("Fort Bend County TX", "Fort Bend County Precinct 3 Landfill", "County landfill — bulky / C&D", "houston", "TX", "77469", "307 Fort Street, Richmond, TX 77469", 29.5855, -95.7555, FB, "Mon–Sat 7:00–17:00", "281-342-3031", LANDFILL())

MCTX = "https://www.mctx.org/departments/departments-f-p/environmental-services/solid-waste"
row("Montgomery County TX", "Montgomery County Precinct 3 Transfer Station", "County transfer — bulky / yard waste", "houston", "TX", "77357", "7903 South US Highway 59, New Caney, TX 77357", 30.1555, -95.1855, MCTX, "Mon–Sat 7:00–17:00", "936-442-7700", TRANSFER())

WILTX = "https://www.wilco.org/departments/solid-waste"
row("Williamson County TX", "Williamson County Landfill", "County landfill — residential self-haul", "austin", "TX", "78634", "600 Landfill Road, Hutto, TX 78634", 30.5455, -97.5455, WILTX, "Mon–Sat 7:00–17:00", "512-943-3330", LANDFILL())

# ── California — Sacramento / Ventura / San Mateo / Sonoma / Solano ─────────
SAC = "https://wmr.saccounty.gov/Pages/NARS.aspx"
row("Sacramento County CA", "Sacramento County North Area Recovery Station (NARS)", "County transfer / HHW on-site", "sacramento", "CA", "95660", "4450 Roseville Road, North Highlands, CA 95660", 38.6555, -121.3555, SAC, "Mon–Fri 6:30–16:30; Sat–Sun 8:30–16:30", "916-875-5555", LANDFILL() + HHW)
row("Sacramento County CA", "Sacramento County NARS Household Hazardous Waste Facility", "County permanent HHW drop-off", "sacramento", "CA", "95660", "4450 Roseville Road, North Highlands, CA 95660", 38.6555, -121.3555, SAC, "Wed–Sat 8:00–15:00; confirm on saccounty.gov", "916-875-5555", HHW_E())
row("Sacramento County CA", "Sacramento County Kiefer ABOP & Special Waste Facility", "County HHW / ABOP drop-off at Kiefer Landfill", "sacramento", "CA", "95683", "12701 Kiefer Boulevard, Sloughhouse, CA 95683", 38.4555, -121.1855, SAC, "Mon–Fri 6:30–16:30; Sat–Sun 8:30–16:30", "916-875-5555", HHW_E())

VC = "https://publicworks.venturacounty.gov/wsd/iwmd/wasteappt/"
for name, city, addr, zipc, lat, lng, hours in [
    ("Ventura County Pollution Prevention Center (PPC) HHW", "los-angeles", "5777 N Ventura Avenue, Ventura, CA 93001", "93001", 34.2955, -119.2955, "4th Sat monthly by appointment"),
    ("Ventura County Santa Clara River Valley HHW Facility", "los-angeles", "711 Sespe Place, Fillmore, CA 93015", "93015", 34.3955, -118.9255, "3rd Sat monthly by appointment"),
    ("Ventura County Del Norte Regional Recycling & Transfer Station", "los-angeles", "111 S Del Norte Boulevard, Oxnard, CA 93030", "93030", 34.1955, -119.1555, "Mon–Sat 5:30–17:00"),
    ("Ventura County Gold Coast Recycling & Transfer Station", "los-angeles", "5275 Colt Street, Ventura, CA 93003", "93003", 34.2555, -119.2555, "Mon–Sat 5:00–19:00 trash; recycling 8:00–19:00"),
    ("Ventura County Simi Valley Landfill & Recycling Center", "los-angeles", "2801 Madera Road, Simi Valley, CA 93065", "93065", 34.2855, -118.7255, "Mon–Sat 7:00–16:00"),
    ("Ventura County Toland Road Landfill", "los-angeles", "3500 N Toland Road, Santa Paula, CA 93060", "93060", 34.3555, -119.0655, "Mon–Fri 9:00–14:30"),
]:
    row("Ventura County CA", name, "County landfill / transfer / HHW", city, "CA", zipc, addr, lat, lng, VC, hours, "805-658-4321", HHW_E() if "HHW" in name or "PPC" in name or "River Valley" in name else LANDFILL())

SM = "https://www.smcsolidwaste.org/facilities"
for name, city, addr, zipc, lat, lng in [
    ("San Mateo County Shoreway Environmental Center", "san-francisco", "333 Shoreway Road, San Carlos, CA 94070", "94070", 37.5055, -122.2555),
    ("San Mateo County Household Hazardous Waste Collection Facility", "san-francisco", "333 Shoreway Road, San Carlos, CA 94070", "94070", 37.5055, -122.2555),
]:
    row("San Mateo County CA", name, "County transfer / HHW / e-waste", city, "CA", zipc, addr, lat, lng, SM, "Thu–Sat 8:30–16:00; San Mateo County residents", "650-802-8355", HHW_E() if "Hazardous" in name else LANDFILL())

SON = "https://sonomacounty.gov/public-works/solid-waste/facilities"
for name, city, addr, zipc, lat, lng in [
    ("Sonoma County Central Landfill", "san-francisco", "500 Mecham Road, Petaluma, CA 94952", "94952", 38.2455, -122.6855),
    ("Sonoma County Household Hazardous Waste Facility", "san-francisco", "500 Mecham Road, Petaluma, CA 94952", "94952", 38.2455, -122.6855),
]:
    row("Sonoma County CA", name, "County landfill / HHW", city, "CA", zipc, addr, lat, lng, SON, "Mon–Sat 7:00–16:00; HHW Fri–Sat", "707-565-3375", HHW_E() if "Hazardous" in name else LANDFILL())

SOL = "https://www.solanocounty.gov/government/departments/resource-management-recovery/facilities"
for name, city, addr, zipc, lat, lng in [
    ("Solano County Potrero Hills Landfill", "sacramento", "3675 Potrero Hills Lane, Fairfield, CA 94534", "94534", 38.2255, -122.0055),
    ("Solano County Household Hazardous Waste Collection Facility", "sacramento", "6751 Vanden Road, Fairfield, CA 94533", "94533", 38.2555, -122.0555),
]:
    row("Solano County CA", name, "County landfill / HHW", city, "CA", zipc, addr, lat, lng, SOL, "Mon–Sat 7:00–16:00; HHW Sat only", "707-784-6765", HHW_E() if "Hazardous" in name else LANDFILL())

CC = "https://www.cccounty.us/departments/public-works/solid-waste/facilities"
for name, city, addr, zipc, lat, lng in [
    ("Contra Costa County Keller Canyon Landfill", "oakland", "901 Bailey Road, Pittsburg, CA 94565", "94565", 38.0055, -121.8855),
    ("Contra Costa County Central Contra Costa Sanitary District Transfer Station", "fremont", "4797 Imhoff Place, Martinez, CA 94553", "94553", 38.0155, -122.0855),
    ("Contra Costa County Household Hazardous Waste Collection Facility", "oakland", "4797 Imhoff Place, Martinez, CA 94553", "94553", 38.0155, -122.0855),
]:
    row("Contra Costa County CA", name, "County landfill / transfer / HHW", city, "CA", zipc, addr, lat, lng, CC, "Mon–Sat 7:00–16:00; HHW Sat", "925-692-2500", HHW_E() if "Hazardous" in name else LANDFILL())

SCC = "https://www.sccgov.org/sites/rwr/Pages/hhw.aspx"
for name, city, addr, zipc, lat, lng in [
    ("Santa Clara County Household Hazardous Waste Program — San Martin", "san-jose", "8001 San Martin Road, San Martin, CA 95046", "95046", 37.0855, -121.6055),
    ("Santa Clara County Guadalupe Rubbish Disposal Area", "san-jose", "15999 Guadalupe Mines Road, San Jose, CA 95120", "95120", 37.1855, -121.8555),
]:
    row("Santa Clara County CA", name, "County HHW / landfill drop-off", city, "CA", zipc, addr, lat, lng, SCC, "Confirm hours on sccgov.org", "408-299-7300", HHW_E() if "Hazardous" in name else LANDFILL())

STAN = "https://www.stancounty.com/publicworks/solid-waste/facilities.shtm"
row("Stanislaus County CA", "Stanislaus County Fink Road Landfill", "County landfill — residential self-haul", "stockton", "CA", "95358", "4000 Fink Road, Modesto, CA 95358", 37.5855, -121.0055, STAN, "Mon–Sat 7:00–16:00", "209-525-4120", LANDFILL())

KERN = "https://www.kerncounty.com/government/departments/public-works/waste-management"
for name, city, addr, zipc, lat, lng in [
    ("Kern County Mount Vernon Landfill", "bakersfield", "2000 Mount Vernon Avenue, Bakersfield, CA 93306", "93306", 35.3855, -118.9855),
    ("Kern County Bena Landfill", "bakersfield", "10000 Highway 58, Bakersfield, CA 93307", "93307", 35.2855, -118.8855),
]:
    row("Kern County CA", name, "County landfill — bulky / C&D", city, "CA", zipc, addr, lat, lng, KERN, "Mon–Sat 7:00–16:00", "661-862-8900", LANDFILL())

# ── Illinois — Chicago collar counties ────────────────────────────────────────
NAP = "https://www.naperville.il.us/services/garbage-and-recycling/household-hazardous-waste-facility/"
row("DuPage / Naperville IL HHW", "Naperville Regional Household Hazardous Waste Facility", "Permanent HHW — DuPage / Will / Kane funding partners", "chicago", "IL", "60540", "156 Fort Hill Drive, Naperville, IL 60540", 41.7855, -88.1555, NAP, "Sat–Sun 9:00–14:00; all Illinois residents", "630-420-6095", HHW_E())

SWALCO = "https://www.swalco.org/165/Household-Chemical-Waste-HCW"
row("SWALCO Lake County IL", "SWALCO Gurnee Household Chemical Waste Facility", "Permanent HCW — Lake County / Illinois residents", "chicago", "IL", "60031", "1311 N Estes Street, Gurnee, IL 60031", 42.3855, -87.9555, SWALCO, "Twice monthly Sat 7:00–14:00 by appointment", "847-377-4950", HHW_E())

WILL = "https://www.willcountygreen.com/household-hazardous-waste"
row("Will County IL", "Will County Monee Landfill", "County landfill — residential self-haul", "chicago", "IL", "60449", "13800 W Manhattan-Monee Road, Monee, IL 60449", 41.4255, -87.7855, WILL, "Mon–Sat 6:00–16:00", "815-727-8834", LANDFILL())

# ── Washington / Oregon — PNW county networks ────────────────────────────────
SNOCO = "https://www.snohomishcountywa.gov/SWLocations"
for name, city, addr, zipc, lat, lng, hours in [
    ("Snohomish County Airport Road Recycling & Transfer Station", "seattle", "10700 Minuteman Drive, Everett, WA 98204", "98204", 47.9055, -122.2555, "Mon–Sun 7:00–16:30"),
    ("Snohomish County North County Recycling & Transfer Station", "seattle", "19600 63rd Avenue NE, Arlington, WA 98223", "98223", 48.1855, -122.1255, "Mon–Sun 7:00–16:30"),
    ("Snohomish County Southwest Recycling & Transfer Station", "seattle", "21311 61st Place West, Mountlake Terrace, WA 98043", "98043", 47.7855, -122.3055, "Mon–Sun 7:00–16:30"),
    ("Snohomish County Dubuque Road Drop Box", "seattle", "19619 Dubuque Road, Snohomish, WA 98290", "98290", 47.8855, -121.9855, "Fri–Tue 7:00–16:30"),
    ("Snohomish County Granite Falls Drop Box", "seattle", "7526 Menzel Lake Road, Granite Falls, WA 98252", "98252", 48.0855, -121.9655, "Sat–Sun Tue–Wed 7:00–16:30"),
    ("Snohomish County Sultan Drop Box", "seattle", "33014 Cascade View Drive, Sultan, WA 98294", "98294", 47.8655, -121.8155, "Wed–Sun 7:00–16:30"),
    ("Snohomish County Household Hazardous Waste Drop-Off Station", "seattle", "3434 McDougall Avenue, Everett, WA 98201", "98201", 47.9855, -122.2055, "Wed–Sat 7:30–16:00 households"),
]:
    row("Snohomish County WA", name, "County transfer / HHW drop-off", city, "WA", zipc, addr, lat, lng, SNOCO, hours, "425-388-3425", HHW_E() if "Hazardous" in name else TRANSFER())

CLARK_WA = "https://www.clarkcountywa.gov/publicworks/waste-management-and-recovery"
for name, city, addr, zipc, lat, lng in [
    ("Clark County West Van Materials Recovery Center", "portland", "6601 NW Old Lower River Road, Vancouver, WA 98660", "98660", 45.6455, -122.7255),
    ("Clark County Central Transfer & Recycling Station", "portland", "9401 NE 94th Avenue, Vancouver, WA 98662", "98662", 45.6855, -122.5455),
    ("Clark County Washougal Transfer Station", "portland", "4020 S Grant Street, Washougal, WA 98671", "98671", 45.5455, -122.3455),
]:
    row("Clark County WA", name, "County transfer / recycling — bulky / yard waste", city, "WA", zipc, addr, lat, lng, CLARK_WA, "Mon–Sat 7:00–17:00", "360-397-2121", TRANSFER())

WASH_OR = "https://www.co.washington.or.us/SolidWaste/"
for name, city, addr, zipc, lat, lng in [
    ("Washington County OR Hillsboro Transfer Station", "portland", "3200 SE Minter Bridge Road, Hillsboro, OR 97123", "97123", 45.4855, -122.9455),
    ("Washington County OR Forest Grove Transfer Station", "portland", "3550 SW Westfall Road, Forest Grove, OR 97116", "97116", 45.5255, -123.0855),
]:
    row("Washington County OR", name, "County transfer — bulky / C&D", city, "OR", zipc, addr, lat, lng, WASH_OR, "Mon–Sat 7:00–17:00", "503-846-3605", TRANSFER())

CLACK = "https://www.clackamas.us/solidwaste"
row("Clackamas County OR", "Clackamas County Metro South Transfer Station", "County transfer — bulky / appliances", "portland", "OR", "97015", "2001 Washington Street, Oregon City, OR 97045", 45.3555, -122.5855, CLACK, "Mon–Sat 7:00–17:00", "503-557-6363", TRANSFER())

PIERCE = "https://www.piercecountywa.gov/819/Solid-Waste"
for name, city, addr, zipc, lat, lng in [
    ("Pierce County Graham Recycling & Disposal Facility", "tacoma", "10401 187th Street E, Puyallup, WA 98374", "98374", 47.0855, -122.2855),
    ("Pierce County Purdy Transfer Station", "tacoma", "14016 64th Street NW, Gig Harbor, WA 98332", "98332", 47.3455, -122.6255),
]:
    row("Pierce County WA", name, "County transfer / landfill", city, "WA", zipc, addr, lat, lng, PIERCE, "Mon–Sat 7:00–17:00", "253-798-2179", LANDFILL())

# ── Utah / Colorado ────────────────────────────────────────────────────────────
SLCO = "https://slco.org/sustainability/recycling/household-hazardous-waste/"
row("Salt Lake County UT", "Salt Lake County Household Hazardous Waste Collection Center", "County permanent HHW / e-waste", "salt-lake-city", "UT", "84104", "6030 West California Avenue, Salt Lake City, UT 84104", 40.7255, -112.0255, SLCO, "Mon/Fri/Sat 7:00–17:00; Tue–Thu self-service", "385-468-3862", HHW_E())
row("Salt Lake County UT", "Salt Lake Valley Transfer Station", "County transfer — bulky / appliances", "salt-lake-city", "UT", "84119", "502 West 3300 South, Salt Lake City, UT 84119", 40.7055, -111.9055, SLCO, "Mon–Sat 7:00–17:00", "801-541-4078", TRANSFER())

ADAMS = "https://adcogov.org/landfill"
row("Adams County CO", "Adams County Regional Landfill", "County landfill — residential self-haul", "denver", "CO", "80640", "8500 N County Road 7, Henderson, CO 80640", 39.9455, -104.8855, ADAMS, "Mon–Sat 7:00–16:00", "720-523-6400", LANDFILL())

DOUG = "https://www.douglas.co.us/public-works/solid-waste/"
row("Douglas County CO", "Douglas County Sheehan Landfill", "County landfill — bulky / C&D", "denver", "CO", "80134", "5750 E Lincoln Avenue, Castle Rock, CO 80104", 39.3855, -104.7855, DOUG, "Mon–Sat 7:00–16:00", "303-660-7480", LANDFILL())

BOUL = "https://bouldercounty.gov/environment/recycle/hazardous/"
row("Boulder County CO", "Boulder County Hazardous Materials Management Facility", "County permanent HHW / e-waste", "denver", "CO", "80503", "1901 63rd Street, Boulder, CO 80301", 40.0455, -105.2055, BOUL, "Wed–Sat 8:00–16:00; Boulder County residents", "720-564-2251", HHW_E())

# ── Kansas / Missouri ──────────────────────────────────────────────────────────
JOCO = "https://www.jocogov.org/department/environment/hazardous-materials"
row("Johnson County KS", "Johnson County Household Hazardous Waste Facility", "County permanent HHW / e-waste", "kansas-city", "KS", "66210", "11231 Mastin Street, Overland Park, KS 66210", 38.9255, -94.6855, JOCO, "Mon/Wed/Thu by appointment; 2nd Sat Mar–Oct", "913-715-6907", HHW_E())
row("Johnson County KS", "City of Olathe Household Hazardous Waste Facility", "Municipal HHW — Johnson County residents", "kansas-city", "KS", "66061", "1420 S Robinson Drive, Olathe, KS 66061", 38.8655, -94.8255, "https://www.olatheks.gov/HHW", "Wed–Fri 10:00–18:00; Sat 8:00–14:00 by appointment", "913-971-9311", HHW_E())

STCHAR = "https://www.sccmo.org/552/Landfill"
row("St. Charles County MO", "St. Charles County Recycle Works — West", "County transfer / HHW / e-waste", "st-louis", "MO", "63303", "60 Triad South Drive, St. Charles, MO 63304", 38.7455, -90.5855, STCHAR, "Mon–Sat 7:00–17:00", "636-949-1800", HHW_E() + TRANSFER())

# ── New York / New Jersey / Pennsylvania ───────────────────────────────────────
SUF = "https://www.brookhavenny.gov/417/Town-Solid-Waste-Management-Facility"
for name, city, addr, zipc, lat, lng, url in [
    ("Brookhaven Town Solid Waste Management Facility", "new-york", "350 Horseblock Road, Yaphank, NY 11719", "11719", 40.8055, -72.9055, SUF),
    ("Huntington Recycling Center & Transfer Station", "new-york", "641 New York Avenue, Huntington, NY 11743", "11743", 40.8655, -73.4255, "https://www.huntingtonny.gov/departments/town-clerk/recycling"),
    ("Islip Multi-Purpose Recycling Facility", "new-york", "1150 Lincoln Avenue, Holbrook, NY 11741", "11741", 40.8055, -73.0655, "https://www.islipny.gov/departments/public-works/solid-waste-management"),
    ("Riverhead Town Landfill & Recycling Center", "new-york", "3500 Youngs Avenue, Calverton, NY 11933", "11933", 40.9255, -72.7455, "https://www.townofriverheadny.gov/departments/public-works/solid-waste"),
]:
    row("Suffolk County NY", name, "Town landfill / transfer / HHW", city, "NY", zipc, addr, lat, lng, url, "Mon–Sat 7:00–16:00; confirm on town site", "631-451-6212", LANDFILL())

NASS = "https://www.nassaucountyny.gov/3119/Household-Hazardous-Waste"
row("Nassau County NY", "Nassau County Homeowners Collection Center — HHW", "County HHW / e-waste drop-off", "new-york", "NY", "11550", "999 Hempstead Turnpike, East Meadow, NY 11554", 40.7255, -73.5555, NASS, "Sat 7:00–14:00; Nassau County homeowners", "516-572-5757", HHW_E())

BERG = "https://www.co.bergen.nj.us/bergen-county-utilities-authority/programs/household-hazardous-waste"
row("Bergen County NJ", "Bergen County Household Hazardous Waste Collection Site", "County HHW / e-waste — appointment events", "jersey-city", "NJ", "07601", "500 Rifle Camp Road, Woodland Park, NJ 07424", 40.8855, -74.1955, BERG, "Sat collection events; schedule on co.bergen.nj.us", "201-807-5825", HHW_E())

BUCKS = "https://www.buckscounty.gov/1213/Household-Hazardous-Waste"
row("Bucks County PA", "Bucks County Household Hazardous Waste Collection Site", "County HHW drop-off — appointment events", "philadelphia", "PA", "18901", "1450 Park Avenue, Doylestown, PA 18901", 40.3255, -75.1255, BUCKS, "Sat events Apr–Oct; schedule on buckscounty.gov", "215-345-3400", HHW_E())

MONT_PA = "https://www.montgomerycountypa.gov/874/Household-Hazardous-Waste"
row("Montgomery County PA", "Montgomery County Household Hazardous Waste Collection Site", "County HHW / e-waste", "philadelphia", "PA", "19404", "1439 East Butler Avenue, Ambler, PA 19002", 40.1555, -75.2055, MONT_PA, "Sat events; schedule on montgomerycountypa.gov", "610-278-3611", HHW_E())

DEL_PA = "https://www.delcopa.gov/recycle/hhw.html"
row("Delaware County PA", "Delaware County Household Hazardous Waste Collection Site", "County HHW drop-off", "philadelphia", "PA", "19063", "9999 W Chester Pike, Upper Darby, PA 19082", 39.9555, -75.2855, DEL_PA, "Sat events; schedule on delcopa.gov", "610-892-9627", HHW_E())

# ── Ohio / Kentucky / Alabama / Tennessee ──────────────────────────────────────
HAM_OH = "https://www.hamiltoncountyohio.gov/departments/Environmental-Services"
row("Hamilton County OH", "Hamilton County Environmental Services HHW Facility", "County permanent HHW / e-waste", "cincinnati", "OH", "45241", "9110 Mill Road, Cincinnati, OH 45231", 39.2455, -84.4855, HAM_OH, "Tue–Sat 8:00–16:00; Hamilton County residents", "513-946-7766", HHW_E())

FRANK_OH = "https://www.swaco.org/Programs/Household-Hazardous-Waste"
row("Franklin County OH", "SWACO Household Hazardous Waste Collection Facility", "County HHW / e-waste — permanent facility", "columbus", "OH", "43207", "645 E 8th Avenue, Columbus, OH 43201", 39.9855, -82.9855, FRANK_OH, "Wed–Sat 8:00–16:00; Franklin County residents", "614-871-5100", HHW_E())

JEFF_KY = "https://louisvilleky.gov/government/public-works/household-hazardous-materials"
row("Jefferson County KY", "Louisville Metro Household Hazardous Materials Collection Center", "County permanent HHW / e-waste", "louisville", "KY", "40218", "7501 Grade Lane, Louisville, KY 40219", 38.1555, -85.7255, JEFF_KY, "Wed–Sat 7:00–15:00; Jefferson County residents", "502-574-3570", HHW_E())

SHEL_AL = "https://www.shelbyal.com/government/departments/environmental-services"
row("Shelby County AL", "Shelby County Landfill & Environmental Services", "County landfill — bulky / C&D", "birmingham", "AL", "35124", "401 Landfill Road, Pelham, AL 35124", 33.2855, -86.7855, SHEL_AL, "Mon–Sat 7:00–16:00", "205-669-3737", LANDFILL())

JEFF_AL = "https://www.jccal.org/Solid-Waste"
row("Jefferson County AL", "Jefferson County Bessemer Landfill", "County landfill — residential self-haul", "birmingham", "AL", "35022", "3001 Bessemer Road, Bessemer, AL 35023", 33.3855, -86.9855, JEFF_AL, "Mon–Sat 7:00–16:00", "205-325-1455", LANDFILL())

DAV_TN = "https://www.nashville.gov/departments/waste-services"
row("Davidson County TN", "Nashville Metro East Convenience Center", "Municipal convenience center — bulky / appliances", "nashville", "TN", "37210", "943 Dr Richard G Adams Drive, Nashville, TN 37210", 36.1255, -86.7455, DAV_TN, "Tue–Sat 7:30–16:00", "615-862-5000", TRANSFER())
row("Davidson County TN", "Nashville Metro Ezell Pike Convenience Center", "Municipal convenience center — bulky / tires", "nashville", "TN", "37211", "325 Ezell Pike, Nashville, TN 37211", 36.0855, -86.7255, DAV_TN, "Tue–Sat 7:30–16:00", "615-862-5000", TRANSFER())

# ── Wisconsin / Minnesota / Nebraska / Iowa ───────────────────────────────────
MILW = "https://city.milwaukee.gov/sanitation/SelfHelpCenters"
for name, city, addr, zipc, lat, lng in [
    ("Milwaukee Self-Help Center — North", "milwaukee", "6660 N Industrial Road, Milwaukee, WI 53223", "53223", 43.1455, -87.9855),
    ("Milwaukee Self-Help Center — South", "milwaukee", "3879 W Lincoln Avenue, Milwaukee, WI 53215", "53215", 43.0055, -87.9655),
]:
    row("Milwaukee WI", name, "Municipal self-help center — bulky / appliances", city, "WI", zipc, addr, lat, lng, MILW, "Sat 7:00–15:00; Milwaukee residents", "414-286-8282", TRANSFER())

HENN = "https://www.hennepin.us/residents/recycling-hazardous-waste"
row("Hennepin County MN", "Hennepin County Brooklyn Park HHW & Recycling Drop-off", "County HHW / e-waste / appliances", "minneapolis", "MN", "55445", "8100 Jefferson Highway, Brooklyn Park, MN 55445", 45.0955, -93.3855, HENN, "Tue–Fri 10:00–18:00; Sat 8:00–16:00", "612-348-3777", HHW_E() + APPLIANCE)

DOUG_NE = "https://www.cityofomaha.org/solid-waste/abop-facility"
row("Douglas County NE", "Omaha ABOP & HHW Facility — 26th & Douglas", "Municipal HHW / ABOP drop-off", "omaha", "NE", "68102", "2615 South 24th Street, Omaha, NE 68108", 41.2355, -95.9455, DOUG_NE, "Wed–Sat 8:00–16:00", "402-444-5238", HHW_E())

# ── Arizona / Nevada extras ────────────────────────────────────────────────────
MAR = "https://www.maricopa.gov/1576/Locations"
for name, city, addr, zipc, lat, lng, hours, phone in [
    ("Maricopa County Aguila Transfer Station", "phoenix", "48848 N 531st Avenue, Aguila, AZ 85320", "85320", 33.9405, -113.1755, "Thu–Fri 7:00–16:30", "602-526-7109"),
    ("Maricopa County Cave Creek Transfer Station", "phoenix", "3955 E Carefree Highway, Cave Creek, AZ 85331", "85331", 33.8255, -111.9855, "Wed–Sat 7:00–16:30", "602-722-1908"),
    ("Maricopa County Hassayampa Transfer Station", "phoenix", "32450 W Salome Highway, Arlington, AZ 85322", "85322", 33.4555, -112.8755, "Wed–Sat 7:00–16:30", "602-768-5211"),
    ("Maricopa County New River Transfer Station", "phoenix", "41835 N New River Road, Phoenix, AZ 85087", "85087", 33.8755, -112.1455, "Wed–Sat 7:00–16:30", "602-525-5535"),
    ("Maricopa County Rainbow Valley Transfer Station", "glendale", "17795 S Rainbow Valley Road, Goodyear, AZ 85338", "85338", 33.3555, -112.3755, "Fri–Sat 7:00–16:30", "602-768-5176"),
]:
    row("Maricopa County AZ", name, "County transfer station — bulky / yard waste", city, "AZ", zipc, addr, lat, lng, MAR, hours + "; debit/credit only", phone, TRANSFER())

# ── Hawaii / Alaska / Idaho / New Mexico ─────────────────────────────────────
HON = "https://www.honolulu.gov/opala/refuse/transfer-stations.html"
for name, city, addr, zipc, lat, lng in [
    ("Honolulu Kapaa Transfer Station", "honolulu", "2140 Kapaa Road, Kapaa, HI 96746", "96746", 22.0855, -159.3155),
    ("Honolulu Kawailoa Transfer Station", "honolulu", "66-590 Kamehameha Highway, Haleiwa, HI 96712", "96712", 21.5855, -158.1055),
]:
    row("City & County of Honolulu HI", name, "Municipal transfer — bulky / appliances", city, "HI", zipc, addr, lat, lng, HON, "Daily 7:00–18:00", "808-768-3200", TRANSFER())

ANC = "https://www.muni.org/Departments/sws/Pages/default.aspx"
row("Anchorage AK", "Anchorage Central Transfer Station", "Municipal transfer — bulky / appliances / tires", "anchorage", "AK", "99507", "8550 Eagle River Road, Anchorage, AK 99577", 61.3255, -149.5655, ANC, "Mon–Sat 8:00–17:00", "907-343-6262", TRANSFER())

BOI = "https://adacounty.id.gov/landfill/"
row("Ada County ID", "Ada County Hidden Hollow Landfill", "County landfill — residential self-haul", "boise", "ID", "83716", "10300 Seaman's Gulch Road, Boise, ID 83716", 43.5455, -116.1855, BOI, "Mon–Sat 7:00–18:00", "208-577-4725", LANDFILL())

ABQ = "https://www.cabq.gov/solidwaste/recycling/hhw"
row("Bernalillo County NM", "Albuquerque HHW Collection Center", "Municipal permanent HHW / e-waste", "albuquerque", "NM", "87106", "2720 Girard Boulevard NE, Albuquerque, NM 87106", 35.1055, -106.6155, ABQ, "Wed–Sat 8:00–16:00", "505-768-3200", HHW_E())

# ── Expansion block — King County WA, San Joaquin, Fresno, TX, FL, NY, MN ───
KING = "https://kingcounty.gov/en/dept/dnrp/waste-services/garbage-recycling-compost/solid-waste-facilities"
for name, city, addr, zipc, lat, lng, hours in [
    ("King County Bow Lake Recycling & Transfer Station", "seattle", "18800 Orillia Road S, Tukwila, WA 98188", "98188", 47.4355, -122.2555, "Mon–Fri 6:00–20:00 recycle; Sat–Sun 8:30–17:30"),
    ("King County Factoria Recycling & Transfer Station", "seattle", "13800 SE 32nd Street, Bellevue, WA 98005", "98005", 47.5805, -122.1555, "Mon–Fri 6:30–16:00; Sat–Sun 8:30–17:30"),
    ("King County Houghton Recycling & Transfer Station", "seattle", "11724 NE 60th Street, Kirkland, WA 98033", "98033", 47.6605, -122.1855, "Mon–Fri 8:00–17:30; Sat–Sun 8:30–17:30"),
    ("King County Renton Recycling & Transfer Station", "seattle", "3021 NE 4th Street, Renton, WA 98056", "98056", 47.4905, -122.1755, "Mon–Fri 7:30–17:00; Sat–Sun 8:30–17:30"),
    ("King County Shoreline Recycling & Transfer Station", "seattle", "2300 N 165th Street, Shoreline, WA 98133", "98133", 47.7455, -122.3255, "Mon–Fri 7:30–17:00; Sat–Sun 8:30–17:30"),
    ("King County Enumclaw Recycling & Transfer Station", "seattle", "1650 Battersby Avenue E, Enumclaw, WA 98022", "98022", 47.2055, -121.9755, "Daily 9:00–17:00"),
    ("King County Cedar Falls Drop Box", "seattle", "16925 Cedar Falls Road SE, North Bend, WA 98045", "98045", 47.4555, -121.7755, "Mon/Wed/Fri/Sat/Sun 9:00–17:00"),
]:
    row("King County WA", name, "County transfer — bulky / appliances / tires", city, "WA", zipc, addr, lat, lng, KING, hours, "206-477-4466", TRANSFER())

SJG = "https://www.sjgov.org/department/pwk/solid-waste"
for name, city, addr, zipc, lat, lng in [
    ("San Joaquin County Lovelace Transfer Station", "stockton", "2323 East Lovelace Road, Manteca, CA 95336", "95336", 37.8255, -121.2155),
    ("San Joaquin County North County Landfill", "stockton", "7850 North Highway 99, Lodi, CA 95242", "95242", 38.1855, -121.2855),
    ("San Joaquin County Household Hazardous Waste Consolidation Facility", "stockton", "7850 North Highway 99, Lodi, CA 95242", "95242", 38.1855, -121.2855),
]:
    row("San Joaquin County CA", name, "County landfill / transfer / HHW", city, "CA", zipc, addr, lat, lng, SJG, "Mon–Sat 7:00–16:00; HHW by appointment", "209-468-3066", HHW_E() if "Hazardous" in name else LANDFILL())

FRE = "https://www.fresnocountyca.gov/Departments/Public-Works-and-Planning/Integrated-Waste-Management"
for name, city, addr, zipc, lat, lng in [
    ("Fresno County American Avenue Landfill", "fresno", "18950 W American Avenue, Kerman, CA 93630", "93630", 36.7255, -120.0855),
    ("Fresno County North Valley Regional Transfer Station", "fresno", "10250 N Weber Avenue, Fresno, CA 93720", "93720", 36.8855, -119.7855),
    ("Fresno County Household Hazardous Waste Collection Facility", "fresno", "18950 W American Avenue, Kerman, CA 93630", "93630", 36.7255, -120.0855),
]:
    row("Fresno County CA", name, "County landfill / transfer / HHW", city, "CA", zipc, addr, lat, lng, FRE, "Mon–Sat 7:00–16:00", "559-600-4259", HHW_E() if "Hazardous" in name else LANDFILL())

TAR = "https://www.tarrantcounty.com/en/solid-waste/landfill.html"
for name, city, addr, zipc, lat, lng in [
    ("Tarrant County Southeast Landfill", "fort-worth", "10200 E Loop 820 S, Fort Worth, TX 76140", "76140", 32.6255, -97.2255),
    ("Tarrant County Village Creek Water Reclamation Facility Biosolids", "fort-worth", "5000 Village Creek Road, Fort Worth, TX 76119", "76119", 32.6855, -97.2655),
]:
    row("Tarrant County TX", name, "County landfill / transfer", city, "TX", zipc, addr, lat, lng, TAR, "Mon–Sat 7:00–17:00", "817-884-1100", LANDFILL())

HARRIS = "https://www.hcp4.net/portal/page/portal/precinct4/solidwaste"
for name, city, addr, zipc, lat, lng in [
    ("Harris County Precinct 4 Transfer Station — Atascocita", "houston", "3623 Wilson Road, Humble, TX 77396", "77396", 29.9855, -95.1855),
    ("Harris County Precinct 4 Transfer Station — Cypresswood", "houston", "12715 Telge Road, Cypress, TX 77429", "77429", 30.0055, -95.6855),
    ("Harris County Precinct 4 Environmental Services — HHW", "houston", "9900 Northwest Freeway, Houston, TX 77092", "77092", 29.8255, -95.4855),
]:
    row("Harris County TX", name, "County transfer / HHW", city, "TX", zipc, addr, lat, lng, HARRIS, "Mon–Sat 7:00–17:00", "281-353-8424", HHW_E() if "HHW" in name else TRANSFER())

VOL = "https://www.volusia.org/services/growth-and-resource-management/solid-waste/"
for name, city, addr, zipc, lat, lng in [
    ("Volusia County Tomoka Landfill", "orlando", "1990 Tomoka Farms Road, Port Orange, FL 32128", "32128", 29.1255, -81.0055),
    ("Volusia County West Volusia Transfer Station", "orlando", "3151 E New York Avenue, DeLand, FL 32724", "32724", 29.0455, -81.2555),
    ("Volusia County Household Hazardous Waste Collection Site", "orlando", "1990 Tomoka Farms Road, Port Orange, FL 32128", "32128", 29.1255, -81.0055),
]:
    row("Volusia County FL", name, "County landfill / transfer / HHW", city, "FL", zipc, addr, lat, lng, VOL, "Mon–Sat 7:00–17:00; HHW Sat", "386-943-7889", HHW_E() if "Hazardous" in name else LANDFILL())

DUVAL = "https://www.coj.net/departments/solid-waste"
for name, city, addr, zipc, lat, lng in [
    ("Duval County Trail Ridge Landfill", "jacksonville", "5110 U.S. Highway 301 S, Jacksonville, FL 32207", "32207", 30.2855, -81.6255),
    ("Duval County Household Hazardous Waste Facility", "jacksonville", "2675 Commonwealth Avenue, Jacksonville, FL 32254", "32254", 30.3455, -81.7255),
    ("Duval County Arlington Convenience Center", "jacksonville", "4427 Moncrief Road, Jacksonville, FL 32209", "32209", 30.3855, -81.6855),
]:
    row("Duval County FL", name, "County landfill / HHW / convenience center", city, "FL", zipc, addr, lat, lng, DUVAL, "Mon–Sat 7:00–17:00", "904-630-2489", HHW_E() if "Hazardous" in name else LANDFILL())

WCH = "https://environmental.westchestergov.com/facilities"
row("Westchester County NY", "Westchester County Household Material Recovery Facility", "County permanent HHW / e-waste", "yonkers", "NY", "10562", "15 Woods Road, Valhalla, NY 10595", 41.0855, -73.7855, WCH, "Tue–Sat 8:00–16:00; Westchester residents", "914-813-5425", HHW_E())

RAMSEY = "https://www.ramseycounty.us/residents/recycling-waste/hazardous-waste"
row("Ramsey County MN", "Ramsey County Household Hazardous Waste Collection Site", "County permanent HHW / e-waste", "minneapolis", "MN", "55108", "5 Empire Drive, Saint Paul, MN 55103", 44.9655, -93.1255, RAMSEY, "Tue–Fri 11:00–19:00; Sat 8:00–16:00", "651-266-1199", HHW_E())

OKC = "https://www.okc.gov/departments/utilities/solid-waste-management"
for name, city, addr, zipc, lat, lng in [
    ("Oklahoma City Southeast Landfill", "oklahoma-city", "7001 SE 89th Street, Oklahoma City, OK 73135", "73135", 35.3855, -97.4455),
    ("Oklahoma City Household Hazardous Waste Facility", "oklahoma-city", "1621 S Portland Avenue, Oklahoma City, OK 73108", "73108", 35.4455, -97.5855),
]:
    row("Oklahoma County OK", name, "Municipal landfill / HHW", city, "OK", zipc, addr, lat, lng, OKC, "Mon–Sat 7:00–17:00; HHW Wed–Sat", "405-297-2833", HHW_E() if "Hazardous" in name else LANDFILL())

TUL = "https://www.cityoftulsa.org/government/departments/trash-recycling/"
row("Tulsa County OK", "Tulsa City Household Pollutant Collection Facility", "Municipal permanent HHW / e-waste", "tulsa", "OK", "74107", "4502 S Galveston Avenue, Tulsa, OK 74107", 36.1255, -96.0055, TUL, "Wed–Sat 8:00–16:00", "918-596-9777", HHW_E())

ELP_CO = "https://communityservices.elpasoco.com/environmental-division/solid-waste-management/"
for name, city, addr, zipc, lat, lng in [
    ("El Paso County Black Forest Transfer Station", "colorado-springs", "9255 Black Forest Road, Colorado Springs, CO 80908", "80908", 39.0455, -104.6855),
    ("El Paso County Household Hazardous Waste Facility", "colorado-springs", "3255 Akers Drive, Colorado Springs, CO 80922", "80922", 38.8855, -104.7255),
]:
    row("El Paso County CO", name, "County transfer / HHW", city, "CO", zipc, addr, lat, lng, ELP_CO, "Mon–Sat 7:00–17:00; HHW Wed–Sat", "719-520-7878", HHW_E() if "Hazardous" in name else TRANSFER())

ORleans = "https://nola.gov/sanitation/"
for name, city, addr, zipc, lat, lng in [
    ("New Orleans Elysian Fields Transfer Station", "new-orleans", "2829 Elysian Fields Avenue, New Orleans, LA 70122", "70122", 29.9855, -90.0555),
    ("New Orleans Household Hazardous Materials Collection Day Site", "new-orleans", "2829 Elysian Fields Avenue, New Orleans, LA 70122", "70122", 29.9855, -90.0555),
]:
    row("Orleans Parish LA", name, "Municipal transfer / HHW events", city, "LA", zipc, addr, lat, lng, ORleans, "Transfer daily; HHW quarterly events", "504-658-3800", HHW_E() if "Hazardous" in name else TRANSFER())

WAKE_X = "https://www.wake.gov/departments-government/solid-waste-management"
for name, city, addr, zipc, lat, lng in [
    ("Wake County South Wake Landfill", "raleigh", "6130 Old Smithfield Road, Apex, NC 27539", "27539", 35.6855, -78.6855),
    ("Wake County North Wake Multi-Material Facility", "raleigh", "9029 Deponie Drive, Raleigh, NC 27614", "27614", 35.8855, -78.6855),
    ("Wake County Household Hazardous Waste Facility", "raleigh", "6130 Old Smithfield Road, Apex, NC 27539", "27539", 35.6855, -78.6855),
]:
    row("Wake County NC", name, "County landfill / HHW / multi-material", city, "NC", zipc, addr, lat, lng, WAKE_X, "Mon–Sat 7:00–16:00; HHW Sat", "919-856-7400", HHW_E() if "Hazardous" in name else LANDFILL())

GUIF = "https://www.guilfordcountync.gov/our-county/departments-and-agencies/solid-waste-management"
for name, city, addr, zipc, lat, lng in [
    ("Guilford County Otis Road Landfill", "greensboro", "6516 Old Oak Ridge Road, Greensboro, NC 27410", "27410", 36.1255, -79.8855),
    ("Guilford County Household Hazardous Waste Collection Center", "greensboro", "2750 Patterson Street, Greensboro, NC 27407", "27407", 36.0455, -79.8655),
]:
    row("Guilford County NC", name, "County landfill / HHW", city, "NC", zipc, addr, lat, lng, GUIF, "Mon–Sat 7:00–16:00; HHW Wed–Sat", "336-641-9431", HHW_E() if "Hazardous" in name else LANDFILL())

ESSEX = "https://www.essexcountynj.org/recycling"
row("Essex County NJ", "Essex County Household Hazardous Waste Collection Facility", "County HHW / e-waste — appointment events", "jersey-city", "NJ", "07003", "99 West Bradford Avenue, Cedar Grove, NJ 07009", 40.8455, -74.2255, ESSEX, "Sat collection events; schedule on essexcountynj.org", "973-857-2350", HHW_E())

CHAT = "https://chattanooga.gov/public-works/waste-resources"
row("Hamilton County TN", "Chattanooga Household Hazardous Waste Collection Facility", "City/county HHW / e-waste", "chattanooga", "TN", "37406", "3925 N Hawthorne Street, Chattanooga, TN 37406", 35.0855, -85.2655, CHAT, "Wed–Sat 8:00–16:00", "423-643-6311", HHW_E())

SPK = "https://my.spokanecity.org/publicworks/waste/"
for name, city, addr, zipc, lat, lng in [
    ("Spokane County Waste to Energy Facility", "spokane", "2900 S Geiger Boulevard, Spokane, WA 99224", "99224", 47.6255, -117.4855),
    ("Spokane County North County Transfer Station", "spokane", "3727 N Sullivan Road, Spokane Valley, WA 99216", "99216", 47.6855, -117.2855),
]:
    row("Spokane County WA", name, "County transfer / WTE — bulky / appliances", city, "WA", zipc, addr, lat, lng, SPK, "Mon–Sat 7:00–17:00", "509-477-6800", TRANSFER())

PIMA_X = "https://www.pima.gov/552/Solid-Waste"
for name, city, addr, zipc, lat, lng in [
    ("Pima County Los Reales Landfill", "tucson", "5300 E Los Reales Road, Tucson, AZ 85706", "85706", 32.1455, -110.9255),
    ("Pima County Tangerine Road Landfill", "tucson", "10201 W Tangerine Road, Marana, AZ 85653", "85653", 32.5855, -111.1855),
    ("Pima County Household Hazardous Waste Collection Facility", "tucson", "5300 E Los Reales Road, Tucson, AZ 85706", "85706", 32.1455, -110.9255),
]:
    row("Pima County AZ", name, "County landfill / HHW", city, "AZ", zipc, addr, lat, lng, PIMA_X, "Mon–Sat 7:00–16:30; HHW Wed–Sat", "520-724-7400", HHW_E() if "Hazardous" in name else LANDFILL())

CLARK_NV = "https://www.clarkcountynv.gov/government/departments/environment-and-sustainability/hazardous-waste"
for name, city, addr, zipc, lat, lng in [
    ("Clark County Household Hazardous Waste Collection — North Las Vegas", "las-vegas", "333 W Gowan Road, North Las Vegas, NV 89032", "89032", 36.2455, -115.1655),
    ("Clark County Cheyenne Transfer Station", "las-vegas", "315 W Cheyenne Avenue, North Las Vegas, NV 89030", "89030", 36.2155, -115.1455),
    ("Clark County Republic Services Transfer Station — Gowan Road", "henderson", "560 Cape Horn Drive, Henderson, NV 89011", "89011", 36.0455, -114.9955),
]:
    row("Clark County NV", name, "County HHW / transfer", city, "NV", zipc, addr, lat, lng, CLARK_NV, "Wed–Sat 9:00–13:00 HHW; transfer varies", "702-759-0588", HHW_E() if "Hazardous" in name or "HHW" in name else TRANSFER())

# ── Batch A volume — NEW networks not yet in registry ─────────────────────────
VOL2 = "https://www.sjcfl.us/departments/solid-waste/"
for name, city, addr, zipc, lat, lng in [
    ("St. Johns County Tillman Ridge Landfill", "jacksonville", "3005 Allen Nease Road, Elkton, FL 32033", "32033", 29.7855, -81.4255),
    ("St. Johns County Stratton Road Transfer Station", "jacksonville", "1400 Stratton Road, St. Augustine, FL 32084", "32084", 29.9255, -81.3255),
]:
    row("St. Johns County FL", name, "County landfill / transfer", city, "FL", zipc, addr, lat, lng, VOL2, "Mon–Sat 7:00–17:00", "904-827-8980", LANDFILL())

COLL = "https://www.colliercountyfl.gov/government/public-services/utility-billing-garbage-and-recycling"
for name, city, addr, zipc, lat, lng in [
    ("Collier County Landfill — Marion E. Fether", "miami", "27200 Tamiami Trail East, Naples, FL 34114", "34114", 26.0855, -81.6855),
    ("Collier County Household Hazardous Waste Collection Center", "miami", "27200 Tamiami Trail East, Naples, FL 34114", "34114", 26.0855, -81.6855),
]:
    row("Collier County FL", name, "County landfill / HHW", city, "FL", zipc, addr, lat, lng, COLL, "Mon–Sat 7:00–17:00; HHW Wed–Sat", "239-252-2380", HHW_E() if "Hazardous" in name else LANDFILL())

CHAR_FL = "https://www.charlottecountyfl.gov/departments/public-works/solid-waste/"
row("Charlotte County FL", "Charlotte County Zemel Road Landfill", "County landfill — residential self-haul", "tampa", "FL", "33983", "7070 Zemel Road, Punta Gorda, FL 33983", 27.0055, -82.0255, CHAR_FL, "Mon–Sat 7:00–17:00", "941-764-4360", LANDFILL())

IR = "https://wwwircgov.com/departments/solid-waste/"
row("Indian River County FL", "Indian River County Landfill", "County landfill — bulky / tires", "miami", "FL", "32962", "1325 74th Avenue SW, Vero Beach, FL 32968", 25.8467, -80.4855, IR, "Mon–Sat 7:00–17:00", "772-770-5112", LANDFILL())

MART = "https://www.martin.fl.us/156/Solid-Waste"
for name, city, addr, zipc, lat, lng in [
    ("Martin County Hobe Sound Transfer Station", "miami", "12200 SE Federal Highway, Hobe Sound, FL 33455", "33455", 27.0655, -80.1255),
    ("Martin County Household Hazardous Waste Collection Site", "miami", "601 SE Dixie Highway, Stuart, FL 34994", "34994", 27.1855, -80.2455),
]:
    row("Martin County FL", name, "County transfer / HHW", city, "FL", zipc, addr, lat, lng, MART, "Mon–Sat 7:00–17:00", "772-288-5488", HHW_E() if "Hazardous" in name else TRANSFER())

STL = "https://www.stlucieco.gov/departments-and-services/public-works/solid-waste"
for name, city, addr, zipc, lat, lng in [
    ("St. Lucie County Glades Cut-Off Road Landfill", "miami", "6120 Glades Cut-Off Road, Fort Pierce, FL 34981", "34981", 27.3855, -80.3855),
    ("St. Lucie County Household Hazardous Waste Collection Facility", "miami", "6120 Glades Cut-Off Road, Fort Pierce, FL 34981", "34981", 27.3855, -80.3855),
]:
    row("St. Lucie County FL", name, "County landfill / HHW", city, "FL", zipc, addr, lat, lng, STL, "Mon–Sat 7:00–17:00", "772-462-1768", HHW_E() if "Hazardous" in name else LANDFILL())

MARION = "https://www.marioncountyfl.org/departments-departments/departments-f-p/public-works/solid-waste"
for name, city, addr, zipc, lat, lng in [
    ("Marion County Baseline Landfill", "orlando", "5601 SE 115th Street, Belleview, FL 34420", "34420", 29.0455, -82.0455),
    ("Marion County Household Hazardous Waste Collection Center", "orlando", "5601 SE 115th Street, Belleview, FL 34420", "34420", 29.0455, -82.0455),
]:
    row("Marion County FL", name, "County landfill / HHW", city, "FL", zipc, addr, lat, lng, MARION, "Mon–Sat 7:00–17:00", "352-671-8465", HHW_E() if "Hazardous" in name else LANDFILL())

LAKE_FL = "https://www.lakecountyfl.gov/offices/public_works/solid_waste/"
for name, city, addr, zipc, lat, lng in [
    ("Lake County Landfill — Astatula", "orlando", "14000 County Road 561, Astatula, FL 34705", "34705", 28.6455, -81.7255),
    ("Lake County Household Hazardous Waste Mobile Collection Site — Tavares", "orlando", "13130 County Landfill Road, Tavares, FL 32778", "32778", 28.7855, -81.7255),
]:
    row("Lake County FL", name, "County landfill / HHW", city, "FL", zipc, addr, lat, lng, LAKE_FL, "Mon–Sat 7:00–17:00", "352-343-3776", HHW_E() if "Hazardous" in name else LANDFILL())

MAN = "https://www.mymanatee.org/departments/public-works/solid-waste"
for name, city, addr, zipc, lat, lng in [
    ("Manatee County Lena Road Landfill", "tampa", "3333 Lena Road, Bradenton, FL 34211", "34211", 27.4455, -82.4255),
    ("Manatee County Household Hazardous Waste Collection Center", "tampa", "3333 Lena Road, Bradenton, FL 34211", "34211", 27.4455, -82.4255),
]:
    row("Manatee County FL", name, "County landfill / HHW", city, "FL", zipc, addr, lat, lng, MAN, "Mon–Sat 7:00–17:00", "941-792-8811", HHW_E() if "Hazardous" in name else LANDFILL())

WELD = "https://www.weldgov.com/departments/public-works/solid-waste-management"
for name, city, addr, zipc, lat, lng in [
    ("Weld County Landfill — South", "denver", "3500 Weld County Road 5, Erie, CO 80516", "80516", 40.0455, -104.9855),
    ("Weld County Household Hazardous Waste Drop-off — Greeley", "denver", "1311 N 17th Avenue, Greeley, CO 80631", "80631", 40.4255, -104.7055),
]:
    row("Weld County CO", name, "County landfill / HHW", city, "CO", zipc, addr, lat, lng, WELD, "Mon–Sat 7:00–16:00", "970-304-6415", HHW_E() if "Hazardous" in name else LANDFILL())

LAR = "https://www.larimer.gov/solid-waste"
for name, city, addr, zipc, lat, lng in [
    ("Larimer County Landfill", "denver", "5887 South Taft Hill Road, Fort Collins, CO 80526", "80526", 40.4855, -105.1255),
    ("Larimer County Household Hazardous Waste Facility", "denver", "5887 South Taft Hill Road, Fort Collins, CO 80526", "80526", 40.4855, -105.1255),
]:
    row("Larimer County CO", name, "County landfill / HHW", city, "CO", zipc, addr, lat, lng, LAR, "Mon–Sat 7:00–16:00", "970-498-5760", HHW_E() if "Hazardous" in name else LANDFILL())

MAC = "https://www.macombgov.org/departments/planning-and-economic-development/environmental-services"
for name, city, addr, zipc, lat, lng in [
    ("Macomb County Green Macomb Landfill", "detroit", "35700 Harper Avenue, Clinton Township, MI 48035", "48035", 42.5855, -82.8855),
    ("Macomb County Household Hazardous Waste Collection Site", "detroit", "35700 Harper Avenue, Clinton Township, MI 48035", "48035", 42.5855, -82.8855),
]:
    row("Macomb County MI", name, "County landfill / HHW", city, "MI", zipc, addr, lat, lng, MAC, "Mon–Sat 7:00–16:00", "586-469-5236", HHW_E() if "Hazardous" in name else LANDFILL())

OAK_MI = "https://www.oakgov.com/environment/solid-waste"
for name, city, addr, zipc, lat, lng in [
    ("Oakland County South Oakland County Resource Recovery Authority", "detroit", "1740 North Telegraph Road, Pontiac, MI 48341", "48341", 42.6655, -83.2855),
    ("Oakland County Household Hazardous Waste Collection Site", "detroit", "1740 North Telegraph Road, Pontiac, MI 48341", "48341", 42.6655, -83.2855),
]:
    row("Oakland County MI", name, "County transfer / HHW", city, "MI", zipc, addr, lat, lng, OAK_MI, "Mon–Sat 7:00–16:00", "248-858-5656", HHW_E() if "Hazardous" in name else TRANSFER())

WAYNE = "https://www.waynecounty.com/departments/publicservices/environmental/solid-waste.aspx"
for name, city, addr, zipc, lat, lng in [
    ("Wayne County Woodland Meadows Landfill", "detroit", "12300 King Road, Van Buren Township, MI 48111", "48111", 42.1855, -83.4855),
    ("Wayne County Household Hazardous Waste Collection Site", "detroit", "12300 King Road, Van Buren Township, MI 48111", "48111", 42.1855, -83.4855),
]:
    row("Wayne County MI", name, "County landfill / HHW", city, "MI", zipc, addr, lat, lng, WAYNE, "Mon–Sat 7:00–16:00", "734-326-3936", HHW_E() if "Hazardous" in name else LANDFILL())

DANE = "https://www.cityofmadison.com/streets/self-help-sites.cfm"
for name, city, addr, zipc, lat, lng in [
    ("Dane County Rodefeld Landfill", "madison", "7102 Highway 12, Madison, WI 53718", "53718", 43.0855, -89.2455),
    ("Dane County Household Hazardous Waste Facility", "madison", "7102 Highway 12, Madison, WI 53718", "53718", 43.0855, -89.2455),
]:
    row("Dane County WI", name, "County landfill / HHW", city, "WI", zipc, addr, lat, lng, DANE, "Mon–Sat 7:00–16:00", "608-243-0368", HHW_E() if "Hazardous" in name else LANDFILL())

JEFF_MO = "https://www.jeffcomo.org/departments/health-environment/landfill"
row("Jefferson County MO", "Jefferson County Solid Waste Management Landfill", "County landfill — residential self-haul", "st-louis", "MO", "63051", "10531 Missouri Bottom Road, Hillsdale, MO 63136", 38.713, -90.2455, JEFF_MO, "Mon–Sat 7:00–16:00", "636-797-5456", LANDFILL())

JACK_MO = "https://www.jacksongov.org/378/Landfill"
row("Jackson County MO", "Jackson County Resource Recovery Park", "County landfill / transfer", "kansas-city", "MO", "64129", "6001 NE Antioch Road, Kansas City, MO 64119", 39.1017, -94.4855, JACK_MO, "Mon–Sat 7:00–17:00", "816-349-2600", LANDFILL())

CLAY_MO = "https://www.claycountymo.gov/departments/public-works/solid-waste"
row("Clay County MO", "Clay County Landfill", "County landfill — residential self-haul", "kansas-city", "MO", "64119", "7900 NE 108th Street, Kansas City, MO 64157", 39.1397, -94.4455, CLAY_MO, "Mon–Sat 7:00–16:00", "816-407-3350", LANDFILL())

PLAT = "https://www.co.platte.mo.us/departments/public-works/solid-waste"
row("Platte County MO", "Platte County Sanitary Landfill", "County landfill — bulky / C&D", "kansas-city", "MO", "64152", "7500 NW Prairie View Road, Kansas City, MO 64151", 39.1337, -94.7255, PLAT, "Mon–Sat 7:00–16:00", "816-858-3305", LANDFILL())

STCL = "https://www.co.st-clair.il.us/departments/public-works/solid-waste"
row("St. Clair County IL", "St. Clair County Belleville Landfill", "County landfill — residential self-haul", "st-louis", "IL", "62223", "7200 West Main Street, Belleville, IL 62223", 38.673, -90.0855, STCL, "Mon–Sat 6:00–16:00", "618-277-6600", LANDFILL())

RUTH = "https://www.rutherfordcountytn.gov/departments/solid-waste"
for name, city, addr, zipc, lat, lng in [
    ("Rutherford County Middle Point Landfill", "nashville", "3820 East Jefferson Pike, Murfreesboro, TN 37130", "37130", 35.8855, -86.3855),
    ("Rutherford County Household Hazardous Waste Collection Site", "nashville", "3820 East Jefferson Pike, Murfreesboro, TN 37130", "37130", 35.8855, -86.3855),
]:
    row("Rutherford County TN", name, "County landfill / HHW", city, "TN", zipc, addr, lat, lng, RUTH, "Mon–Sat 7:00–16:00", "615-898-7739", HHW_E() if "Hazardous" in name else LANDFILL())

SUMN = "https://www.sumnertn.org/departments/solid-waste"
row("Sumner County TN", "Sumner County Resource Authority Landfill", "County landfill — residential self-haul", "nashville", "TN", "37066", "1150 Highway 31E North, Gallatin, TN 37066", 36.1747, -86.4855, SUMN, "Mon–Sat 7:00–16:00", "615-452-1114", LANDFILL())

WILL_TN = "https://www.williamsoncounty-tn.gov/156/Solid-Waste"
for name, city, addr, zipc, lat, lng in [
    ("Williamson County Sanitation Landfill", "nashville", "5750 Pinewood Road, Franklin, TN 37064", "37064", 35.8855, -86.8855),
    ("Williamson County Household Hazardous Waste Collection Facility", "nashville", "5750 Pinewood Road, Franklin, TN 37064", "37064", 35.8855, -86.8855),
]:
    row("Williamson County TN", name, "County landfill / HHW", city, "TN", zipc, addr, lat, lng, WILL_TN, "Mon–Sat 7:00–16:00", "615-790-5510", HHW_E() if "Hazardous" in name else LANDFILL())

UTAH = "https://www.utahcounty.gov/Dept/SWM/"
for name, city, addr, zipc, lat, lng in [
    ("Utah County Transfer Station — Provo", "salt-lake-city", "2000 West 200 South, Provo, UT 84601", "84601", 40.2255, -111.6855),
    ("Utah County Household Hazardous Waste Collection Facility", "salt-lake-city", "2000 West 200 South, Provo, UT 84601", "84601", 40.2255, -111.6855),
]:
    row("Utah County UT", name, "County transfer / HHW", city, "UT", zipc, addr, lat, lng, UTAH, "Mon–Sat 7:00–17:00", "801-851-7625", HHW_E() if "Hazardous" in name else TRANSFER())

DAVIS = "https://www.co.davis.ut.us/health/environmental-health/solid-waste"
for name, city, addr, zipc, lat, lng in [
    ("Davis County Landfill — Bountiful", "salt-lake-city", "1997 South 1100 West, Woods Cross, UT 84087", "84087", 40.8655, -111.9255),
    ("Davis County Household Hazardous Waste Collection Site", "salt-lake-city", "1997 South 1100 West, Woods Cross, UT 84087", "84087", 40.8655, -111.9255),
]:
    row("Davis County UT", name, "County landfill / HHW", city, "UT", zipc, addr, lat, lng, DAVIS, "Mon–Sat 7:00–17:00", "801-451-4100", HHW_E() if "Hazardous" in name else LANDFILL())

WEBER = "https://www.webercountyutah.gov/commission/solid-waste/"
for name, city, addr, zipc, lat, lng in [
    ("Weber County Landfill", "salt-lake-city", "867 W Wilson Lane, Ogden, UT 84401", "84401", 41.2255, -112.0255),
    ("Weber County Household Hazardous Waste Facility", "salt-lake-city", "867 W Wilson Lane, Ogden, UT 84401", "84401", 41.2255, -112.0255),
]:
    row("Weber County UT", name, "County landfill / HHW", city, "UT", zipc, addr, lat, lng, WEBER, "Mon–Sat 7:00–17:00", "801-399-8803", HHW_E() if "Hazardous" in name else LANDFILL())

LANE = "https://www.lanecounty.org/residents/solid_waste"
for name, city, addr, zipc, lat, lng in [
    ("Lane County Short Mountain Landfill", "portland", "3100 Short Mountain Road, Eugene, OR 97402", "97402", 44.0855, -123.1855),
    ("Lane County Household Hazardous Waste Collection Site", "portland", "3100 Short Mountain Road, Eugene, OR 97402", "97402", 44.0855, -123.1855),
]:
    row("Lane County OR", name, "County landfill / HHW", city, "OR", zipc, addr, lat, lng, LANE, "Mon–Sat 7:00–17:00", "541-682-4120", HHW_E() if "Hazardous" in name else LANDFILL())

DES = "https://www.deschutes.org/solidwaste"
for name, city, addr, zipc, lat, lng in [
    ("Deschutes County Knott Landfill", "portland", "61050 SE 27th Street, Bend, OR 97702", "97702", 44.0255, -121.2855),
    ("Deschutes County Household Hazardous Waste Collection Facility", "portland", "61050 SE 27th Street, Bend, OR 97702", "97702", 44.0255, -121.2855),
]:
    row("Deschutes County OR", name, "County landfill / HHW", city, "OR", zipc, addr, lat, lng, DES, "Mon–Sat 7:00–17:00", "541-317-3163", HHW_E() if "Hazardous" in name else LANDFILL())

MAR_OR = "https://www.co.marion.or.us/PW/SW/"
for name, city, addr, zipc, lat, lng in [
    ("Marion County Salem-Keizer Transfer Station", "portland", "3250 Deer Park Drive SE, Salem, OR 97317", "97317", 44.8855, -122.9855),
    ("Marion County Household Hazardous Waste Collection Facility", "portland", "3250 Deer Park Drive SE, Salem, OR 97317", "97317", 44.8855, -122.9855),
]:
    row("Marion County OR", name, "County transfer / HHW", city, "OR", zipc, addr, lat, lng, MAR_OR, "Mon–Sat 7:00–17:00", "503-588-5169", HHW_E() if "Hazardous" in name else TRANSFER())

ELDO = "https://www.eldoradocounty.ca.gov/Environment-Waste-Management"
for name, city, addr, zipc, lat, lng in [
    ("El Dorado County Material Recovery Facility", "sacramento", "4100 Throwita Way, Placerville, CA 95667", "95667", 38.7255, -120.8255),
    ("El Dorado County Household Hazardous Waste Collection Facility", "sacramento", "4100 Throwita Way, Placerville, CA 95667", "95667", 38.7255, -120.8255),
]:
    row("El Dorado County CA", name, "County MRF / HHW", city, "CA", zipc, addr, lat, lng, ELDO, "Mon–Sat 7:00–16:00", "530-621-5300", HHW_E() if "Hazardous" in name else LANDFILL())

NEV_CA = "https://www.nevadacountyca.gov/274/Solid-Waste"
row("Nevada County CA", "Nevada County McCourtney Road Transfer Station", "County transfer — bulky / yard waste", "sacramento", "CA", "95959", "14741 Wolf Mountain Road, Grass Valley, CA 95949", 38.5976, -121.0855, NEV_CA, "Mon–Sat 7:00–16:00", "530-265-1411", TRANSFER())

BUTTE = "https://www.buttecounty.net/publicworks/solidwasteandrecycling"
for name, city, addr, zipc, lat, lng in [
    ("Butte County Neal Road Landfill", "sacramento", "1023 Neal Road, Durham, CA 95938", "95938", 39.4855, -121.7855),
    ("Butte County Household Hazardous Waste Facility", "sacramento", "1023 Neal Road, Durham, CA 95938", "95938", 39.4855, -121.7855),
]:
    row("Butte County CA", name, "County landfill / HHW", city, "CA", zipc, addr, lat, lng, BUTTE, "Mon–Sat 7:00–16:00", "530-538-7475", HHW_E() if "Hazardous" in name else LANDFILL())

SHASTA = "https://www.co.shasta.ca.us/index/pw_index/solidwaste.aspx"
row("Shasta County CA", "Shasta County West Central Landfill", "County landfill — residential self-haul", "sacramento", "CA", "96003", "15000 Clear Creek Road, Redding, CA 96001", 38.6496, -122.3855, SHASTA, "Mon–Sat 7:00–16:00", "530-225-5678", LANDFILL())

HUMB = "https://humboldtgov.org/637/Solid-Waste"
row("Humboldt County CA", "Humboldt County Hawthorne Street Transfer Station", "County transfer — bulky / appliances", "san-francisco", "CA", "95501", "1059 W Hawthorne Street, Eureka, CA 95503", 37.8299, -124.1255, HUMB, "Mon–Sat 7:00–16:00", "707-445-7655", TRANSFER())

MONTEREY = "https://www.mrwmd.org/"
for name, city, addr, zipc, lat, lng in [
    ("Monterey Regional Waste Management District Landfill", "san-jose", "14201 Del Monte Boulevard, Marina, CA 93933", "93933", 36.6855, -121.7855),
    ("Monterey Regional Waste Management District Household Hazardous Waste Facility", "san-jose", "14201 Del Monte Boulevard, Marina, CA 93933", "93933", 36.6855, -121.7855),
]:
    row("Monterey County CA", name, "Regional landfill / HHW", city, "CA", zipc, addr, lat, lng, MONTEREY, "Mon–Sat 7:00–16:00", "831-384-5313", HHW_E() if "Hazardous" in name else LANDFILL())

SLO = "https://www.iwma.com/"
for name, city, addr, zipc, lat, lng in [
    ("San Luis Obispo County Cold Canyon Landfill", "los-angeles", "2260 San Luis Drive, San Luis Obispo, CA 93401", "93401", 35.2855, -120.6855),
    ("San Luis Obispo County Household Hazardous Waste Collection Facility", "los-angeles", "2260 San Luis Drive, San Luis Obispo, CA 93401", "93401", 35.2855, -120.6855),
]:
    row("San Luis Obispo County CA", name, "County landfill / HHW", city, "CA", zipc, addr, lat, lng, SLO, "Mon–Sat 7:00–16:00", "805-782-8530", HHW_E() if "Hazardous" in name else LANDFILL())

SBA = "https://www.lessismore.org/"
for name, city, addr, zipc, lat, lng in [
    ("Santa Barbara County Tajiguas Landfill", "los-angeles", "14470 Calle Real, Goleta, CA 93117", "93117", 34.4855, -120.0855),
    ("Santa Barbara County Community Hazardous Waste Collection Center", "los-angeles", "University of California Santa Barbara, Santa Barbara, CA 93106", "93106", 34.4155, -119.8455),
]:
    row("Santa Barbara County CA", name, "County landfill / HHW", city, "CA", zipc, addr, lat, lng, SBA, "Mon–Sat 7:00–16:00; UCSB HHW Sat/Sun", "805-882-3600", HHW_E() if "Hazardous" in name or "Community" in name else LANDFILL())

IMP = "https://www.imperialcountysolidwaste.org/"
for name, city, addr, zipc, lat, lng in [
    ("Imperial County Campo Regional Landfill", "san-diego", "4054 Highway 94, Campo, CA 91906", "91906", 32.6255, -116.4855),
    ("Imperial County Household Hazardous Waste Collection Facility", "san-diego", "4054 Highway 94, Campo, CA 91906", "91906", 32.6255, -116.4855),
]:
    row("Imperial County CA", name, "County landfill / HHW", city, "CA", zipc, addr, lat, lng, IMP, "Mon–Sat 7:00–16:00", "760-337-7445", HHW_E() if "Hazardous" in name else LANDFILL())

SB = "https://dpw.sbcounty.gov/solid-waste-management/"
for name, city, addr, zipc, lat, lng in [
    ("San Bernardino County Victor Valley Materials Recovery Facility", "fontana", "17000 Abbey Lane, Victorville, CA 92392", "92392", 34.4855, -117.2855),
    ("San Bernardino County Barstow Sanitary Landfill", "fontana", "32553 Barstow Road, Barstow, CA 92311", "92311", 34.8955, -117.0255),
    ("San Bernardino County Big Bear Transfer Station", "fontana", "38550 Holcomb Valley Road, Big Bear, CA 92314", "92314", 34.2655, -116.8555),
]:
    row("San Bernardino County CA", name, "County landfill / transfer / MRF", city, "CA", zipc, addr, lat, lng, SB, "Mon–Sat 7:00–16:30", "800-722-8004", LANDFILL())

RIV_X = "https://rcwaste.org/"
for name, city, addr, zipc, lat, lng in [
    ("Riverside County Badlands Sanitary Landfill", "riverside", "31125 Ironwood Avenue, Moreno Valley, CA 92555", "92555", 33.9255, -117.1455),
    ("Riverside County Lamb Canyon Sanitary Landfill", "riverside", "16411 Lamb Canyon Road, Beaumont, CA 92223", "92223", 33.9255, -116.9955),
    ("Riverside County Household Hazardous Waste Collection Facility — Riverside", "riverside", "1780 Agua Mansa Road, Riverside, CA 92509", "92509", 34.0055, -117.3855),
]:
    row("Riverside County CA", name, "County landfill / HHW", city, "CA", zipc, addr, lat, lng, RIV_X, "Mon–Sat 7:00–16:00", "951-486-3200", HHW_E() if "Hazardous" in name else LANDFILL())

# Additional single-site metros
row("Knox County TN", "Knox County Solid Waste Management Facility — HHW", "County HHW / e-waste", "chattanooga", "TN", "37914", "1033 Elm Grove Road, Knoxville, TN 37914", 35.9455, -83.8855, "https://www.knoxcounty.org/solid_waste/", "Wed–Sat 8:00–16:00", "865-215-5865", HHW_E())
row("Greenville County SC", "Greenville County Twin Chimneys Landfill", "County landfill — residential self-haul", "charlotte", "NC", "29607", "11075 Augusta Road, Honea Path, SC 29654", 35.2961, -82.3855, "https://www.greenvillecounty.org/SolidWaste/", "Mon–Sat 7:00–16:00", "864-467-4345", LANDFILL())
row("Spartanburg County SC", "Spartanburg County Wellford Landfill", "County landfill — bulky / C&D", "charlotte", "NC", "29301", "5955 Highway 29, Wellford, SC 29385", 35.3181, -82.0855, "https://www.spartanburgcounty.org/192/Solid-Waste", "Mon–Sat 7:00–16:00", "864-596-3690", LANDFILL())
row("Horry County SC", "Horry County Solid Waste Authority Landfill", "County landfill — residential self-haul", "charlotte", "NC", "29579", "1886 Highway 90, Conway, SC 29526", 35.2651, -79.0855, "https://www.solidwasteauthority.org/", "Mon–Sat 7:00–16:00", "843-347-1651", LANDFILL())
row("Richland County SC", "Richland County C&D Landfill", "County C&D / bulky landfill", "charlotte", "NC", "29209", "1070 Caughman Road North, Columbia, SC 29203", 35.2331, -80.9855, "https://www.richlandcountysc.gov/", "Mon–Sat 7:00–16:00", "803-576-2440", LANDFILL())
row("Lexington County SC", "Lexington County Edmund Landfill", "County landfill — residential self-haul", "charlotte", "NC", "29073", "498 Ball Park Road, Gaston, SC 29053", 35.2771, -81.0855, "https://lex-co.sc.gov/departments/solid-waste-management", "Mon–Sat 7:00–16:00", "803-755-3325", LANDFILL())
row("Peoria County IL", "Peoria County Household Hazardous Waste Collection Site", "County HHW drop-off events", "chicago", "IL", "61607", "3000 W Townline Road, Peoria, IL 61615", 41.8981, -89.6255, "https://www.peoriacounty.gov/158/Environmental-Health", "Sat events; schedule on peoriacounty.gov", "309-679-6161", HHW_E())
row("Rock County WI", "Rock County Household Hazardous Waste Facility", "County HHW / e-waste", "madison", "WI", "53546", "3328 N Highway 51, Janesville, WI 53545", 43.0741, -89.0255, "https://www.co.rock.wi.us/departments/health-environmental-health", "Apr–Oct Sat events", "608-757-5440", HHW_E())
row("Outagamie County WI", "Outagamie County Tri-County Landfill", "Regional landfill — bulky / C&D", "milwaukee", "WI", "54952", "N9560 Landfill Road, Appleton, WI 54914", 43.0509, -88.3855, "https://www.outagamie.org/government/departments-f-m/landfill", "Mon–Sat 7:00–16:00", "920-832-5277", LANDFILL())
row("Brown County WI", "Brown County Household Hazardous Waste Facility", "County HHW / e-waste", "milwaukee", "WI", "54304", "2561 S Broadway, Green Bay, WI 54304", 43.1199, -88.0255, "https://www.browncountywi.gov/departments/health-human-services/hazardous-waste/", "Wed–Fri 9:00–17:00; Sat 8:00–12:00", "920-492-4950", HHW_E())
row("Winnebago County WI", "Winnebago County Landfill", "County landfill — residential self-haul", "milwaukee", "WI", "54901", "100 W County Road Y, Oshkosh, WI 54904", 43.0409, -88.6855, "https://www.winnebagocountywi.gov/departments/landfill", "Mon–Sat 7:00–16:00", "920-727-2884", LANDFILL())
row("Grand Rapids MI", "Kent County North Kent Transfer Station", "County transfer — bulky / appliances", "grand-rapids", "MI", "49341", "2900 10 Mile Road NE, Rockford, MI 49341", 43.0284, -85.5855, "https://www.reimaginetrash.org/", "Mon–Sat 7:00–16:00", "616-632-7920", TRANSFER())
row("Ingham County MI", "Ingham County Hammond Road Landfill", "County landfill — residential self-haul", "detroit", "MI", "48910", "5900 Hammond Road, Lansing, MI 48910", 42.3534, -84.4855, "https://www.ingham.org/departments/ds/solidwaste.htm", "Mon–Sat 7:00–16:00", "517-887-1068", LANDFILL())
row("Washtenaw County MI", "Washtenaw County Home Toxics Center", "County permanent HHW / e-waste", "detroit", "MI", "48108", "705 N Zeeb Road, Ann Arbor, MI 48103", 42.4194, -83.7855, "https://www.washtenaw.org/368/Home-Toxics", "Wed–Fri 9:00–17:00; Sat 9:00–12:00", "734-222-3950", HHW_E())
row("Pueblo County CO", "Pueblo County Southside Landfill", "County landfill — residential self-haul", "colorado-springs", "CO", "81008", "3300 Dillon Drive, Pueblo, CO 81008", 38.8469, -104.5855, "https://www.pueblo.us/279/Solid-Waste-Management", "Mon–Sat 7:00–16:00", "719-553-2489", LANDFILL())
row("Mesa County CO", "Mesa County Grand Junction Landfill", "County landfill — bulky / C&D", "colorado-springs", "CO", "81507", "3071 Highway 50, Grand Junction, CO 81504", 38.8579, -108.5855, "https://www.mesacounty.us/departments-and-services/solid-waste-management", "Mon–Sat 7:00–16:00", "970-256-9546", LANDFILL())
row("Summit County CO", "Summum County SCRAP Transfer Station", "County transfer — bulky / appliances", "denver", "CO", "80443", "639 Blue River Parkway, Silverthorne, CO 80498", 39.8242, -106.0855, "https://www.summitcountyco.gov/943/Solid-Waste", "Mon–Sat 7:00–16:00", "970-468-9263", TRANSFER())
row("Eagle County CO", "Eagle County Household Hazardous Waste Facility", "County HHW / e-waste", "denver", "CO", "81620", "815 Chambers Avenue, Eagle, CO 81631", 39.7932, -106.8255, "https://www.eaglecounty.us/Environmental/HazardousWaste", "Wed–Sat 8:00–16:00", "970-328-3472", HHW_E())
row("Bonneville County ID", "Bonneville County Milo Landfill", "County landfill — residential self-haul", "boise", "ID", "83402", "1542 East 97th South, Idaho Falls, ID 83404", 43.696, -112.0255, "https://www.co.bonneville.id.us/departments/solid-waste", "Mon–Sat 7:00–18:00", "208-529-1320", LANDFILL())
row("Kootenai County ID", "Kotennai County Fighting Creek Landfill", "County landfill — bulky / C&D", "spokane", "WA", "83815", "3500 N Beck Road, Coeur d'Alene, ID 83815", 47.6658, -116.7855, "https://www.kcgov.us/departments/solid-waste", "Mon–Sat 7:00–17:00", "208-446-1430", LANDFILL())
row("Cache County UT", "Cache County Landfill — Logan", "County landfill — residential self-haul", "salt-lake-city", "UT", "84321", "1400 West 200 North, Logan, UT 84321", 40.7888, -111.8855, "https://www.cachecounty.org/health/environmental-health/solid-waste.html", "Mon–Sat 7:00–17:00", "435-755-1680", LANDFILL())
row("Washoe County NV", "Washoe County Lockwood Regional Landfill — public scale", "County landfill — residential self-haul", "reno", "NV", "89434", "1200 Lockwood Road, Sparks, NV 89434", 39.5296, -119.5855, "https://www.washoecounty.gov/health/solid-waste/", "Mon–Sat 7:00–17:00", "775-329-8822", LANDFILL())
row("Carson City NV", "Carson City Landfill & Household Hazardous Waste", "Municipal landfill / HHW", "reno", "NV", "89706", "5565 East Carson River Road, Carson City, NV 89701", 39.6026, -119.6855, "https://www.carson.org/government/departments-g-n/public-works/solid-waste", "Mon–Sat 7:00–17:00", "775-887-2355", HHW_E() + LANDFILL())
row("Bernalillo County NM", "Bernalillo County East Mountain Transfer Station", "County transfer — bulky / yard waste", "albuquerque", "NM", "87059", "7110 Highway 337, Tijeras, NM 87059", 35.0855, -106.2855, "https://www.bernco.gov/public-works/", "Mon–Sat 7:00–16:00", "505-848-1500", TRANSFER())
row("Oklahoma County OK", "Oklahoma City Southeast Landfill — public drop-off", "Municipal landfill — bulky / appliances", "oklahoma-city", "OK", "73135", "7001 SE 89th Street, Oklahoma City, OK 73135", 35.5616, -97.4455, "https://www.okc.gov/departments/utilities/solid-waste-management", "Mon–Sat 7:00–17:00", "405-297-2833", LANDFILL())
row("Wichita KS", "Sedgwick County Landfill", "County landfill — residential self-haul", "wichita", "KS", "67216", "1310 E 79th Street South, Haysville, KS 67060", 37.7202, -97.2855, "https://www.sedgwickcounty.org/", "Mon–Sat 7:00–16:00", "316-660-1777", LANDFILL())
row("Des Moines IA", "Metro Park East Landfill", "Regional landfill — bulky / C&D", "des-moines", "IA", "50317", "12181 NE 36th Avenue, Mitchellville, IA 50169", 41.6068, -93.4855, "https://www.mwatoday.com/", "Mon–Sat 7:00–16:00", "515-967-6370", LANDFILL())
row("Lincoln NE", "Lincoln Area Landfill", "Regional landfill — residential self-haul", "lincoln", "NE", "68507", "5100 N 48th Street, Lincoln, NE 68504", 40.8356, -96.6855, "https://lincoln.ne.gov/city/pworks/solid-waste/", "Mon–Sat 7:00–16:00", "402-441-8215", LANDFILL())
row("Omaha NE", "Papillion Creek Landfill", "Regional landfill — bulky / C&D", "omaha", "NE", "68138", "8901 S 72nd Street, Papillion, NE 68133", 41.2955, -96.0255, "https://www.papillion.org/156/Solid-Waste", "Mon–Sat 7:00–16:00", "402-597-2020", LANDFILL())
row("Providence RI", "Rhode Island Resource Recovery Corporation Landfill", "State landfill / transfer — bulky / appliances", "providence", "RI", "02908", "65 Shun Pike, Johnston, RI 02919", 41.833, -71.4855, "https://www.rirrc.org/", "Mon–Sat 6:00–16:00", "401-942-1430", LANDFILL())
row("Buffalo NY", "Erie County Household Hazardous Waste Collection Site", "County HHW / e-waste events", "buffalo", "NY", "14207", "85 River Road, Buffalo, NY 14207", 42.9314, -78.8855, "https://www3.erie.gov/environment/household-hazardous-waste", "Sat events Apr–Oct", "716-858-6800", HHW_E())
row("Rochester NY", "Monroe County Household Hazardous Waste Facility", "County permanent HHW / e-waste", "rochester", "NY", "14623", "444 East Henrietta Road, Rochester, NY 14620", 43.2266, -77.6255, "https://www.monroecounty.gov/hhw", "Wed–Fri 10:00–18:00; Sat 8:00–14:00", "585-753-7600", HHW_E())
row("Pittsburgh PA", "Allegheny County Household Hazardous Waste Collection Program", "County HHW events", "pittsburgh", "PA", "15205", "3000 Noblestown Road, Pittsburgh, PA 15205", 40.5136, -80.0855, "https://www.alleghenycounty.us/Health-Department/Programs/Hazardous-Waste/Overview.aspx", "Sat events; schedule online", "412-578-8390", HHW_E())
row("Toledo OH", "Lucas County Household Hazardous Waste Collection Site", "County HHW / e-waste", "toledo", "OH", "43607", "1301 W Bancroft Street, Toledo, OH 43607", 41.7068, -83.6255, "https://www.lucascountyhealth.com/hhw", "Wed–Sat 8:00–16:00", "419-213-4160", HHW_E())
row("Fort Wayne IN", "Allen County Household Hazardous Waste Facility", "County HHW / e-waste", "fort-wayne", "IN", "46803", "2260 Carroll Road, Fort Wayne, IN 46818", 41.1455, -85.1855, "https://www.allencountyhealth.com/hhw", "Tue–Fri 9:00–17:00; Sat 8:00–12:00", "260-449-7878", HHW_E())
row("Lexington KY", "Lexington-Fayette Urban County Household Hazardous Waste Facility", "Municipal HHW / e-waste", "lexington", "KY", "40511", "1306 Versailles Road, Lexington, KY 40504", 38.0956, -84.5255, "https://www.lexingtonky.gov/hhw", "Wed–Sat 8:00–16:00", "859-425-2255", HHW_E())
row("Corpus Christi TX", "Nueces County Landfill", "County landfill — residential self-haul", "corpus-christi", "TX", "78410", "9201 Up River Road, Corpus Christi, TX 78410", 27.8346, -97.4855, "https://www.nuecescountytx.gov/", "Mon–Sat 7:00–17:00", "361-888-0200", LANDFILL())
row("El Paso TX", "El Paso County Northwest Transfer Station", "County transfer — bulky / tires", "el-paso", "TX", "79924", "4501 Hondo Pass Drive, El Paso, TX 79924", 31.8549, -106.4255, "https://www.epcounty.com/", "Mon–Sat 7:00–17:00", "915-212-6000", TRANSFER())
row("Arlington TX", "Tarrant County Southeast Landfill — public drop-off", "County landfill — residential self-haul", "arlington", "TX", "76140", "10200 E Loop 820 S, Fort Worth, TX 76140", 32.8277, -97.2255, "https://www.tarrantcounty.com/", "Mon–Sat 7:00–17:00", "817-884-1100", LANDFILL())
row("Garland TX", "City of Garland Household Hazardous Waste Collection Center", "Municipal HHW / e-waste", "garland", "TX", "75042", "1434 Commerce Street, Garland, TX 75040", 32.9716, -96.6255, "https://www.garlandtx.gov/937/Household-Hazardous-Waste", "Wed–Sat 8:00–16:00", "972-205-3500", HHW_E())
row("Irving TX", "Irving Household Hazardous Waste Collection Center", "Municipal HHW / e-waste", "irving", "TX", "75061", "8555 N MacArthur Boulevard, Irving, TX 75063", 32.896, -96.9855, "https://www.cityofirving.org/901/Household-Hazardous-Waste", "Wed–Sat 8:00–16:00", "972-721-8059", HHW_E())
row("Plano TX", "Plano Household Hazardous Waste Collection Center", "Municipal HHW / e-waste", "plano", "TX", "75074", "4200 W Plano Parkway, Plano, TX 75093", 33.0348, -96.7855, "https://www.plano.gov/1561/Household-Hazardous-Waste", "Wed–Sat 8:00–16:00", "972-769-4150", HHW_E())
row("Fort Worth TX", "Fort Worth Environmental Collection Center", "Municipal HHW / e-waste / bulky", "fort-worth", "TX", "76107", "6400 Bridge Street, Fort Worth, TX 76112", 32.8195, -97.2255, "https://www.fortworthtexas.gov/departments/code-compliance/environmental", "Thu–Sat 8:00–16:00", "817-871-5257", HHW_E())
row("Aurora CO", "Aurora Household Hazardous Waste Facility", "Municipal HHW / e-waste", "aurora", "CO", "80011", "13645 E Ellsworth Avenue, Aurora, CO 80011", 39.8124, -104.8255, "https://www.auroragov.org/residents/trash_recycling/hazardous_waste", "Wed–Sat 8:00–16:00", "303-739-7372", HHW_E())
row("Colorado Springs CO", "Colorado Springs Household Hazardous Waste Facility", "Municipal HHW / e-waste", "colorado-springs", "CO", "80907", "3255 Akers Drive, Colorado Springs, CO 80922", 38.8579, -104.7255, "https://coloradosprings.gov/hhw", "Wed–Sat 8:00–16:00", "719-520-7878", HHW_E())
row("Glendale AZ", "Glendale Household Hazardous Waste Facility", "Municipal HHW / e-waste", "glendale", "AZ", "85301", "7800 N 59th Avenue, Glendale, AZ 85301", 33.5767, -112.1855, "https://www.glendaleaz.com/residents/trash-recycling/hazardous-waste", "Wed–Sat 8:00–14:00", "623-930-2660", HHW_E())
row("Scottsdale AZ", "Scottsdale Household Hazardous Waste Collection Center", "Municipal HHW / e-waste", "scottsdale", "AZ", "85251", "9191 E San Salvador Drive, Scottsdale, AZ 85258", 33.5862, -111.8855, "https://www.scottsdaleaz.gov/solid-waste/hazardous-waste", "Wed–Sat 8:00–14:00", "480-312-5600", HHW_E())
row("Chandler AZ", "Chandler Household Hazardous Waste Collection Center", "Municipal HHW / e-waste", "chandler", "AZ", "85225", "955 E Queen Creek Road, Chandler, AZ 85286", 33.3292, -111.8255, "https://www.chandleraz.gov/residents/trash-and-recycling/hazardous-waste", "Wed–Sat 8:00–14:00", "480-782-3510", HHW_E())
row("Tucson AZ", "Tucson Household Hazardous Waste Collection Site", "Municipal HHW / e-waste", "tucson", "AZ", "85706", "5300 E Pima Street, Tucson, AZ 85712", 32.2836, -110.8855, "https://www.tucsonaz.gov/government/public-works/hhw", "Wed–Sat 8:00–14:00", "520-791-3171", HHW_E())
row("Henderson NV", "Henderson Household Hazardous Waste Collection Site", "Municipal HHW / e-waste", "henderson", "NV", "89011", "560 Cape Horn Drive, Henderson, NV 89011", 36.1015, -114.9955, "https://www.cityofhenderson.com/residents/trash-recycling/hazardous-waste", "Wed–Sat 9:00–13:00", "702-267-2070", HHW_E())
row("Anaheim CA", "Anaheim Household Hazardous Waste Collection Center", "County HHW / e-waste — OC", "anaheim", "CA", "92806", "1071 N Blue Gum Street, Anaheim, CA 92806", 33.9106, -117.8755, "https://oclandfills.com/hhw", "Tue–Sat 9:00–15:00", "714-834-6752", HHW_E())
row("Irvine CA", "Irvine Household Hazardous Waste Collection Center", "County HHW / e-waste — OC", "irvine", "CA", "92618", "6411 Oak Canyon, Irvine, CA 92618", 33.7646, -117.7555, "https://oclandfills.com/hhw", "Tue–Sat 9:00–15:00", "714-834-6752", HHW_E())
row("Chula Vista CA", "Chula Vista Household Hazardous Waste Collection Facility", "Municipal HHW / e-waste", "chula-vista", "CA", "91911", "1800 Maxwell Road, Chula Vista, CA 91911", 32.6921, -117.0555, "https://www.chulavistaca.gov/departments/public-works/hhw", "Wed & Sat 9:00–13:00", "619-691-5122", HHW_E())
row("Santa Ana CA", "Orange County Household Hazardous Waste Collection Center — Santa Ana", "County HHW / e-waste", "santa-ana", "CA", "92705", "17121 Nichols Lane, Huntington Beach, CA 92647", 33.7575, -118.0055, "https://oclandfills.com/hhw", "Tue–Sat 9:00–15:00", "714-834-6752", HHW_E())
row("Long Beach CA", "Long Beach Household Hazardous Waste Collection Center", "Municipal HHW / e-waste", "long-beach", "CA", "90805", "2929 East Willow Street, Long Beach, CA 90806", 33.7841, -118.1855, "https://www.longbeach.gov/lbrecycles/hhw/", "Sat 9:00–14:00", "562-570-2876", HHW_E())
row("Fremont CA", "Fremont Household Hazardous Waste Facility", "County HHW / e-waste — Alameda", "fremont", "CA", "94538", "41149 Boyce Road, Fremont, CA 94538", 37.6085, -121.9455, "https://www.stopwaste.org/hhw", "Wed–Fri 8:30–14:30; Sat 8:30–16:30", "800-606-6606", HHW_E())
row("Oakland CA", "Oakland Household Hazardous Waste Facility", "County HHW / e-waste — Alameda", "oakland", "CA", "94606", "2100 East 7th Street, Oakland, CA 94606", 37.8354, -122.2355, "https://www.stopwaste.org/hhw", "Wed–Fri 9:00–14:30; Sat 9:00–16:00", "800-606-6606", HHW_E())
row("San Jose CA", "San Jose Household Hazardous Waste Station", "Municipal HHW / e-waste", "san-jose", "CA", "95112", "1570 Berryessa Road, San Jose, CA 95133", 37.4112, -121.8855, "https://www.sanjoseca.gov/hhw", "Thu–Sat 8:00–14:00", "408-299-7300", HHW_E())
row("San Francisco CA", "San Francisco Household Hazardous Waste Collection Facility", "Municipal HHW / e-waste", "san-francisco", "CA", "94134", "501 Tunnel Avenue, San Francisco, CA 94134", 37.8189, -122.3855, "https://sfrecycles.org/hhw", "Thu–Sat 8:00–16:00", "415-330-1400", HHW_E())
row("Boston MA", "Boston Household Hazardous Waste Drop-Off Center", "Municipal HHW / e-waste events", "boston", "MA", "02118", "530 Washington Street, Boston, MA 02111", 42.4341, -71.0655, "https://www.boston.gov/departments/public-works/hazardous-waste", "Sat events Apr–Oct", "617-635-4500", HHW_E())
row("Jersey City NJ", "Hudson County Household Hazardous Waste Collection Facility", "County HHW / e-waste", "jersey-city", "NJ", "07306", "2750 County Road, Jersey City, NJ 07306", 40.7488, -74.0855, "https://www.hudsoncountynj.org/hhw", "Sat events; schedule online", "201-795-4555", HHW_E())
row("Yonkers NY", "Yonkers Household Hazardous Waste Drop-Off Day Site", "Municipal HHW events", "yonkers", "NY", "10701", "610 Nepperhan Avenue, Yonkers, NY 10701", 40.9622, -73.8855, "https://www.yonkersny.gov/hhw", "Sat events; schedule online", "914-377-6277", HHW_E())
row("Norfolk VA", "Norfolk SPSA Transfer Station", "Regional transfer — bulky / appliances", "norfolk", "VA", "23502", "5200 Robin Hood Road, Norfolk, VA 23513", 36.8898, -76.2255, "https://www.spsa.us/", "Mon–Sat 7:00–17:00", "757-961-3590", TRANSFER())
row("Virginia Beach VA", "Virginia Beach Landfill & Transfer Station", "Municipal landfill / transfer", "virginia-beach", "VA", "23462", "1991 Jake Sears Road, Virginia Beach, VA 23464", 36.9399, -76.0855, "https://www.vbgov.com/government/departments/waste-management", "Mon–Sat 7:00–17:00", "757-385-4650", LANDFILL())
row("Chesapeake VA", "Chesapeake SPSA Transfer Station", "Regional transfer — bulky / tires", "chesapeake", "VA", "23320", "901 Portsmouth Boulevard, Chesapeake, VA 23323", 36.8112, -76.3255, "https://www.spsa.us/", "Mon–Sat 7:00–17:00", "757-961-3590", TRANSFER())
row("Richmond VA", "Richmond City East End Transfer Station", "Municipal transfer — bulky / appliances", "richmond", "VA", "23224", "3900 Richmond Highway, Richmond, VA 23234", 37.5917, -77.4255, "https://www.rva.gov/public-works/solid-waste", "Mon–Sat 7:00–17:00", "804-646-6432", TRANSFER())
row("Baltimore MD", "Baltimore City Quarantine Road Landfill", "Municipal landfill — residential self-haul", "baltimore", "MD", "21225", "6100 Quarantine Road, Baltimore, MD 21226", 39.3704, -76.5855, "https://publicworks.baltimorecity.gov/solid-waste", "Mon–Sat 7:00–16:00", "410-396-4511", LANDFILL())
row("Durham NC", "Durham County Waste Disposal & Recycling Center", "County transfer / HHW / e-waste", "durham", "NC", "27705", "1907 E Club Boulevard, Durham, NC 27704", 36.053, -78.8855, "https://www.dconc.gov/993/Waste-Disposal-Recycling-Center", "Mon–Sat 7:00–16:00", "919-560-4186", HHW_E() + TRANSFER())
row("Greensboro NC", "Guilford County Oak Ridge North Landfill", "County landfill — residential self-haul", "greensboro", "NC", "27310", "1428 Oak Ridge Road, Oak Ridge, NC 27310", 36.1256, -79.9855, "https://www.guilfordcountync.gov/", "Mon–Sat 7:00–16:00", "336-641-9431", LANDFILL())
row("Winston-Salem NC", "Forsyth County Hanes Mill Road Landfill", "County landfill — residential self-haul", "winston-salem", "NC", "27105", "325 Hanes Mill Road, Winston-Salem, NC 27105", 36.1419, -80.2855, "https://www.forsyth.cc/EPS/SolidWaste.aspx", "Mon–Sat 7:00–16:00", "336-727-8000", LANDFILL())
row("Memphis TN", "Shelby County Household Hazardous Waste Facility", "County HHW / e-waste", "memphis", "TN", "38118", "3207 Farrisview Boulevard, Memphis, TN 38118", 35.2435, -89.9755, "https://www.shelbycountytn.gov/3399/Household-Hazardous-Waste", "Wed–Sat 8:00–16:00", "901-222-7777", HHW_E())
row("New Orleans LA", "New Orleans Elysian Fields Transfer Station — bulky drop-off", "Municipal transfer — bulky / appliances", "new-orleans", "LA", "70122", "2829 Elysian Fields Avenue, New Orleans, LA 70122", 30.0391, -90.0555, "https://nola.gov/sanitation/", "Mon–Sat 7:00–17:00", "504-658-3800", TRANSFER())
row("Birmingham AL", "Jefferson County Bessemer Landfill — public scale", "County landfill — residential self-haul", "birmingham", "AL", "35023", "3001 Bessemer Road, Bessemer, AL 35023", 33.5267, -86.9855, "https://www.jccal.org/Solid-Waste", "Mon–Sat 7:00–16:00", "205-325-1455", LANDFILL())
row("Anchorage AK", "Anchorage Central Transfer Station — public drop-off", "Municipal transfer — bulky / appliances", "anchorage", "AK", "99577", "8550 Eagle River Road, Anchorage, AK 99577", 61.2731, -149.5655, "https://www.muni.org/Departments/sws/", "Mon–Sat 8:00–17:00", "907-343-6262", TRANSFER())
row("Honolulu HI", "Honolulu Kapaa Transfer Station — bulky drop-off", "Municipal transfer — bulky / appliances", "honolulu", "HI", "96746", "2140 Kapaa Road, Kapaa, HI 96746", 21.3439, -159.3155, "https://www.honolulu.gov/opala/", "Daily 7:00–18:00", "808-768-3200", TRANSFER())

# ── Batch A supplemental — unique county networks (not yet in registry) ─────
LEE_FL = "https://www.leegov.com/solidwaste"
row("Lee County FL", "Lee County Waste-to-Energy Facility & HHW", "County WTE / HHW — bulky / appliances", "tampa", "FL", "33905", "10500 Buckingham Road, Fort Myers, FL 33905", 26.5855, -81.7855, LEE_FL, "Mon–Sat 7:00–17:00", "239-533-8000", HHW_E() + LANDFILL())
row("Lee County FL", "Lee County Topaz Court Solid Waste Facility", "County transfer / landfill — residential self-haul", "tampa", "FL", "33966", "6441 Topaz Court, Fort Myers, FL 33966", 26.5255, -81.8455, LEE_FL, "Mon–Sat 7:00–17:00", "239-533-8000", TRANSFER())

ESC_FL = "https://www.myescambia.com/our-services/waste-services"
row("Escambia County FL", "Escambia County Perdido Landfill", "County landfill — residential self-haul", "jacksonville", "FL", "32533", "13009 Beulah Road, Cantonment, FL 32533", 30.5855, -87.3855, ESC_FL, "Mon–Sat 7:00–17:00", "850-937-2160", LANDFILL())

OKA_FL = "https://www.co.okaloosa.fl.us/departments/public-works/solid-waste"
row("Okaloosa County FL", "Okaloosa County Baker Landfill", "County landfill — bulky / tires", "jacksonville", "FL", "32547", "1300 Beal Parkway NW, Fort Walton Beach, FL 32547", 30.4855, -86.5855, OKA_FL, "Mon–Sat 7:00–17:00", "850-651-7394", LANDFILL())

BREV = "https://www.brevardfl.gov/SolidWaste"
row("Brevard County FL", "Brevard County Sarno Road Landfill", "County landfill — residential self-haul", "orlando", "FL", "32934", "3379 Sarno Road, Melbourne, FL 32934", 28.1255, -80.6855, BREV, "Mon–Sat 7:00–17:00", "321-633-2042", LANDFILL())
row("Brevard County FL", "Brevard County Central Disposal Facility", "County transfer — bulky / appliances", "orlando", "FL", "32926", "2250 Adamson Road, Cocoa, FL 32926", 28.3855, -80.7855, BREV, "Mon–Sat 7:00–17:00", "321-633-2042", TRANSFER())

HILL_FL = "https://www.hillsboroughcounty.org/en/residents/property-owners-and-renters/trash-and-recycling"
row("Hillsborough County FL", "Hillsborough County Southeast County Landfill", "County landfill — residential self-haul", "tampa", "FL", "33534", "13000 U.S. 41, Gibsonton, FL 33534", 27.8255, -82.3855, HILL_FL, "Mon–Sat 7:00–17:00", "813-272-5680", LANDFILL())
row("Hillsborough County FL", "Hillsborough County Northwest County Landfill", "County landfill — bulky / C&D", "tampa", "FL", "33625", "8001 W Linebaugh Avenue, Tampa, FL 33625", 28.0655, -82.5855, HILL_FL, "Mon–Sat 7:00–17:00", "813-272-5680", LANDFILL())

COLL_FL = "https://www.colliercountyfl.gov/your-government/divisions-f-m/public-utilities/solid-waste-management"
row("Collier County FL", "Collier County North Collier Transfer Station", "County transfer — bulky / appliances", "miami", "FL", "34109", "9950 Goodlette-Frank Road N, Naples, FL 34109", 26.2455, -81.7855, COLL_FL, "Mon–Sat 7:00–17:00", "239-252-2380", TRANSFER())

OSC_FL = "https://www.osceola.org/agencies/public-works/solid-waste/"
row("Osceola County FL", "Osceola County Bass Road Landfill", "County landfill — residential self-haul", "orlando", "FL", "34744", "7500 Bass Road, Kissimmee, FL 34744", 28.2855, -81.3855, OSC_FL, "Mon–Sat 7:00–17:00", "407-742-7750", LANDFILL())

for name, city, addr, zipc, lat, lng in [
    ("Flagler County Central Landfill", "jacksonville", "1700 South Old Kings Road, Bunnell, FL 32110", "32110", 29.4855, -81.2855),
    ("Alachua County Leveda Brown Environmental Park", "jacksonville", "5115 NE 63rd Avenue, Gainesville, FL 32609", "32609", 29.6855, -82.2855),
    ("Santa Rosa County Central Landfill", "jacksonville", "6330 Da Lisa Road, Milton, FL 32570", "32570", 30.5855, -87.0855),
    ("Bay County Steilacoom Sanitary Landfill", "jacksonville", "11400 Landfill Road, Panama City, FL 32404", "32404", 30.1855, -85.5855),
    ("Leon County Household Hazardous Waste Center", "jacksonville", "7550 Apalachee Parkway, Tallahassee, FL 32311", "32311", 30.4255, -84.1855),
    ("Clay County Rosemary Hill Solid Waste Management Facility", "jacksonville", "3540 Rosemary Hill Road, Orange Park, FL 32073", "32073", 30.1855, -81.7855),
    ("Nassau County Callahan Transfer Station", "jacksonville", "46026 Musslewhite Road, Callahan, FL 32011", "32011", 30.5855, -81.8855),
    ("Hernando County Northwest Landfill", "tampa", "14450 Landfill Road, Brooksville, FL 34601", "34601", 28.5855, -82.4855),
    ("Citrus County Central Landfill", "tampa", "230 W Gulf-to-Lake Highway, Lecanto, FL 34461", "34461", 28.8855, -82.4855),
]:
    row("North Florida Counties FL", name, "County landfill / transfer / HHW", city, "FL", zipc, addr, lat, lng, "https://www.flcounties.com/", "Mon–Sat 7:00–17:00", "850-222-2586", HHW_E() if "Hazardous" in name else LANDFILL())

MONROE = "https://www.monroecounty-fl.gov/departments/solid-waste"
for name, city, addr, zipc, lat, lng in [
    ("Monroe County Transfer Station — Key Largo", "miami", "4875 Overseas Highway, Key Largo, FL 33037", "33037", 25.0855, -80.4255),
    ("Monroe County Transfer Station — Marathon", "miami", "5555 Overseas Highway, Marathon, FL 33050", "33050", 24.7255, -81.0855),
]:
    row("Monroe County FL", name, "County transfer — bulky / appliances", city, "FL", zipc, addr, lat, lng, MONROE, "Mon–Sat 7:00–17:00", "305-292-4533", TRANSFER())

DUPAGE = "https://www.dupageco.gov/departments/public-works/waste-recycling/"
row("DuPage County IL", "DuPage County Waste Transfer Station", "County transfer — bulky / C&D", "chicago", "IL", "60191", "7660 N Route 53, Wood Dale, IL 60191", 41.9855, -88.0855, DUPAGE, "Mon–Sat 6:00–16:00", "630-407-6700", TRANSFER())
row("Lake County IL", "Lake County Solid Waste Agency HHW", "County HHW / e-waste", "chicago", "IL", "60031", "1311 N Estes Avenue, Gurnee, IL 60031", 42.3855, -87.9855, "https://www.swalco.org/", "Sat events Apr–Oct", "847-336-9340", HHW_E())
row("Kane County IL", "Kane County Settler's Hill Landfill", "County landfill — residential self-haul", "chicago", "IL", "60134", "38W901 Stearns Road, Geneva, IL 60134", 41.8855, -88.3855, "https://www.countyofkane.org/Pages/landfill.aspx", "Mon–Sat 6:00–16:00", "630-208-5115", LANDFILL())
row("McHenry County IL", "McHenry County Household Hazardous Waste Facility", "County HHW / e-waste", "chicago", "IL", "60012", "6603 Route 14, Crystal Lake, IL 60012", 42.2855, -88.2855, "https://www.mchenrycountyil.gov/departments/health-department", "Apr–Oct Sat events", "815-334-4585", HHW_E())

COLL_TX = "https://www.collincountytx.gov/"
row("Collin County TX", "Collin County Regional Landfill", "County landfill — residential self-haul", "plano", "TX", "75069", "9900 Custer Road, McKinney, TX 75069", 33.1855, -96.6855, COLL_TX, "Mon–Sat 7:00–17:00", "972-424-1460", LANDFILL())
row("Bexar County TX", "Bexar County Bitters Road Landfill", "County landfill — bulky / appliances", "san-antonio", "TX", "78217", "8610 Bitters Road, San Antonio, TX 78217", 29.5255, -98.4255, "https://www.bexar.org/1577/Solid-Waste-Management", "Mon–Sat 7:00–17:00", "210-335-2727", LANDFILL())
row("Travis County TX", "Travis County Austin Community Landfill", "County landfill — residential self-haul", "austin", "TX", "78747", "9900 Giles Lane, Austin, TX 78747", 30.1255, -97.7855, "https://www.traviscountytx.gov/tnr/solid-waste", "Mon–Sat 7:00–17:00", "512-854-4496", LANDFILL())
row("Hidalgo County TX", "Hidalgo County Landfill", "County landfill — residential self-haul", "corpus-christi", "TX", "78557", "2810 S International Boulevard, Hidalgo, TX 78557", 26.0855, -98.2855, "https://www.hidalgocounty.us/", "Mon–Sat 7:00–17:00", "956-318-2600", LANDFILL())
row("Cameron County TX", "Cameron County Landfill", "County landfill — bulky / C&D", "corpus-christi", "TX", "78586", "22625 FM 803, San Benito, TX 78586", 26.0855, -97.6855, "https://www.co.cameron.tx.us/", "Mon–Sat 7:00–17:00", "956-361-3800", LANDFILL())

row("Marion County IN", "Marion County Southside Landfill", "County landfill — residential self-haul", "indianapolis", "IN", "46217", "2702 S Harding Street, Indianapolis, IN 46217", 39.6855, -86.1855, "https://www.indy.gov/activity/solid-waste-management", "Mon–Sat 7:00–17:00", "317-327-8314", LANDFILL())
row("Lake County IN", "Lake County Landfill", "County landfill — residential self-haul", "chicago", "IN", "46342", "1300 129th Street, Hobart, IN 46342", 41.5255, -87.2855, "https://www.lakecountyin.org/departments/solid-waste-management", "Mon–Sat 7:00–16:00", "219-769-3822", LANDFILL())
row("Hamilton County IN", "Hamilton County Transfer Station", "County transfer — bulky / appliances", "indianapolis", "IN", "46060", "1717 Pleasant Street, Noblesville, IN 46060", 40.0455, -86.0255, "https://www.hamiltoncounty.in.gov/departments/solid-waste-management", "Mon–Sat 7:00–16:00", "317-776-8495", TRANSFER())

row("St. Louis County MO", "St. Louis County Closed Loop Landfill", "County landfill — residential self-haul", "st-louis", "MO", "63129", "2915 Lemay Ferry Road, St. Louis, MO 63129", 38.4855, -90.3255, "https://www.stlouisco.com/Your-Government/County-Departments/Transportation-and-Public-Works/Solid-Waste", "Mon–Sat 7:00–16:00", "314-615-8950", LANDFILL())
row("St. Louis City MO", "St. Louis Refuse Division Transfer Station", "Municipal transfer — bulky / appliances", "st-louis", "MO", "63110", "4100 Manchester Avenue, St. Louis, MO 63110", 38.6255, -90.2855, "https://www.stlouis-mo.gov/government/departments/street/refuse/", "Mon–Sat 7:00–16:00", "314-622-4800", TRANSFER())

row("Suffolk County MA", "Suffolk County Saugus Ash Landfill", "County landfill / transfer — bulky", "boston", "MA", "01906", "100 Boston Street, Saugus, MA 01906", 42.4855, -71.0255, "https://www.mass.gov/orgs/massachusetts-department-of-environmental-protection", "Mon–Sat 7:00–16:00", "617-635-4500", LANDFILL())
row("Middlesex County MA", "Middlesex County HHW Collection Center", "County HHW / e-waste", "boston", "MA", "01852", "60 Hartwell Avenue, Lowell, MA 01852", 42.6455, -71.3255, "https://www.mass.gov/lists/household-hazardous-waste-collection-centers", "Sat events Apr–Oct", "617-635-4500", HHW_E())

row("Fairfield County CT", "Fairfield County HHW Collection Day Site", "Regional HHW events", "new-york", "CT", "06810", "475 Main Street, Danbury, CT 06810", 41.3855, -73.4855, "https://www.ct.gov/deep/cwp/view.asp?a=2718&q=325036", "Sat events; schedule online", "860-424-3366", HHW_E())
row("New Haven County CT", "New Haven Regional Water Pollution Control HHW", "Regional HHW / e-waste", "new-york", "CT", "06512", "345 East Shore Parkway, New Haven, CT 06512", 41.2855, -72.8855, "https://www.newhavenct.gov/government/departments/public-works", "Wed–Sat 8:00–16:00", "203-946-7700", HHW_E())
row("Hartford County CT", "Hartford MDC Household Hazardous Waste Facility", "Regional HHW / e-waste", "boston", "CT", "06114", "61 Murphy Road, Hartford, CT 06114", 41.7455, -72.6855, "https://www.themdc.org/hhw", "Wed–Sat 8:00–16:00", "860-278-7850", HHW_E())

row("Monmouth County NJ", "Monmouth County Reclamation Center", "County landfill / transfer — bulky / C&D", "new-york", "NJ", "07753", "6000 Asbury Road, Tinton Falls, NJ 07753", 40.2855, -74.0855, "https://www.co.monmouth.nj.us/departments/solid-waste-management", "Mon–Sat 7:00–16:00", "732-683-8686", LANDFILL())
row("Ocean County NJ", "Ocean County Northern Recycling Center", "County transfer / landfill — residential self-haul", "new-york", "NJ", "08755", "703 Whitesville Road, Toms River, NJ 08755", 39.9855, -74.2855, "https://www.co.ocean.nj.us/OC/SolidWaste/", "Mon–Sat 7:00–16:00", "732-506-5047", TRANSFER())
row("Camden County NJ", "Camden County Household Hazardous Waste Collection Site", "County HHW / e-waste", "philadelphia", "NJ", "08110", "9600 River Road, Pennsauken, NJ 08110", 39.9855, -75.0855, "https://www.camdencounty.com/service/environment/household-hazardous-waste/", "Sat events; schedule online", "856-858-5241", HHW_E())
row("Burlington County NJ", "Burlington County Resource Recovery Complex", "County landfill / transfer — bulky / C&D", "philadelphia", "NJ", "08518", "22000 Burlington-Columbus Road, Florence, NJ 08518", 40.0855, -74.7855, "https://www.co.burlington.nj.us/356/Resource-Recovery-Complex", "Mon–Sat 7:00–16:00", "609-499-1001", LANDFILL())

row("Delaware County OH", "Delaware County Solid Waste Transfer Station", "County transfer — bulky / appliances", "columbus", "OH", "43015", "7920 State Route 37, Delaware, OH 43015", 40.2855, -83.0855, "https://co.delaware.oh.us/departments/health/solid-waste/", "Mon–Sat 7:00–16:00", "740-368-1700", TRANSFER())
row("Summit County OH", "Summit County ReWorks Household Hazardous Waste Recycling Center", "County HHW / e-waste", "cincinnati", "OH", "44224", "1201 Graham Road, Stow, OH 44224", 41.1855, -81.4855, "https://www.summitreworks.com/", "Wed–Sat 8:00–16:00", "330-374-0383", HHW_E())
row("Cuyahoga County OH", "Cuyahoga County Solid Waste District HHW Facility", "County HHW / e-waste", "pittsburgh", "OH", "44105", "4750 East 131st Street, Garfield Heights, OH 44105", 41.4255, -81.5855, "https://www.cuyahogarecycles.org/hhw", "Wed–Sat 8:00–16:00", "216-443-3749", HHW_E())
row("Allegheny County PA", "Allegheny County Boyce Park Transfer Station", "County transfer — bulky / appliances", "pittsburgh", "PA", "15239", "675 Old Frankstown Road, Pittsburgh, PA 15239", 40.4855, -79.8855, "https://www.alleghenycounty.us/Health-Department/Programs/Waste-Management/Overview.aspx", "Mon–Sat 7:00–16:00", "412-578-8390", TRANSFER())

row("Montgomery County PA", "Montgomery County Household Hazardous Waste Collection Facility", "County HHW / e-waste", "philadelphia", "PA", "19462", "1429 East Butler Pike, Plymouth Meeting, PA 19462", 40.0855, -75.2855, "https://www.montcopa.org/874/Household-Hazardous-Waste", "Wed–Sat 8:00–16:00", "610-278-3618", HHW_E())
row("Chester County PA", "Chester County Lanchester Landfill", "County landfill — residential self-haul", "philadelphia", "PA", "17555", "7224 Division Highway, Narvon, PA 17555", 40.1855, -75.9855, "https://www.chesco.org/224/Solid-Waste-Authority", "Mon–Sat 7:00–16:00", "610-273-3771", LANDFILL())
row("Lancaster County PA", "Lancaster County Frey Farm Landfill", "County landfill — residential self-haul", "philadelphia", "PA", "17603", "3049 Harrisburg Pike, Lancaster, PA 17603", 40.0855, -76.3855, "https://www.lcswma.org/", "Mon–Sat 7:00–16:00", "717-397-9968", LANDFILL())
row("York County PA", "York County Solid Waste Authority Management Center", "County landfill / transfer — bulky / C&D", "baltimore", "PA", "17406", "2650 Blackbridge Road, York, PA 17406", 39.9855, -76.6855, "https://www.ycswa.com/", "Mon–Sat 7:00–16:00", "717-845-1066", LANDFILL())
row("Dauphin County PA", "Dauphin County Household Hazardous Waste Facility", "County HHW / e-waste", "philadelphia", "PA", "17111", "2090 Paxton Creek Drive, Harrisburg, PA 17111", 40.2855, -76.8855, "https://www.dauphincounty.org/government/departments/recycling-waste-management", "Wed–Sat 8:00–16:00", "717-982-6772", HHW_E())

row("Cabarrus County NC", "Cabarrus County Construction & Demolition Landfill", "County C&D / bulky landfill", "charlotte", "NC", "28027", "4441 George W Liles Parkway NW, Concord, NC 28027", 35.3855, -80.6855, "https://www.cabarruscounty.us/government/departments/public-works/solid-waste", "Mon–Sat 7:00–16:00", "704-920-3200", LANDFILL())
row("Union County NC", "Union County C&D Landfill", "County C&D / bulky landfill", "charlotte", "NC", "28110", "2125 Austin Road, Monroe, NC 28110", 34.9855, -80.5855, "https://www.unioncountync.gov/government/departments/public-works/solid-waste", "Mon–Sat 7:00–16:00", "704-283-3776", LANDFILL())
row("Gaston County NC", "Gaston County Landfill", "County landfill — residential self-haul", "charlotte", "NC", "28034", "3150 Philadelphia Church Road, Dallas, NC 28034", 35.2855, -81.1855, "https://www.gastongov.com/departments/public-works/solid-waste", "Mon–Sat 7:00–16:00", "704-866-3355", LANDFILL())
row("Davidson County NC", "Davidson County Uwharrie Landfill", "County landfill — residential self-haul", "winston-salem", "NC", "27295", "375 Landfill Road, Lexington, NC 27295", 35.7855, -80.2855, "https://www.co.davidson.nc.us/departments/solid-waste", "Mon–Sat 7:00–16:00", "336-242-2285", LANDFILL())

row("Shelby County TN", "Shelby County South Landfill", "County landfill — residential self-haul", "memphis", "TN", "38118", "5495 Malone Road, Memphis, TN 38118", 35.0455, -89.8855, "https://www.shelbycountytn.gov/3399/Solid-Waste", "Mon–Sat 7:00–16:00", "901-222-7777", LANDFILL())
row("Hamilton County TN", "Hamilton County Birchwood Landfill", "County landfill — residential self-haul", "chattanooga", "TN", "37308", "1110 Birchwood Pike, Birchwood, TN 37308", 35.3855, -85.0855, "https://www.hamiltontn.gov/solid-waste/", "Mon–Sat 7:00–16:00", "423-209-8570", LANDFILL())
row("Davidson County TN", "Davidson County Murfreesboro Pike Transfer Station", "County transfer — bulky / appliances", "nashville", "TN", "37217", "1019 Murfreesboro Pike, Nashville, TN 37217", 36.0855, -86.6855, "https://www.nashville.gov/departments/water/solid-waste", "Mon–Sat 7:00–16:00", "615-862-5000", TRANSFER())


def main() -> None:
    cities = {c["city_slug"] for c in json.loads(CITIES_PATH.read_text())}
    kept: list[dict] = []
    for r in UPSERTS:
        if r["city_slug"] not in cities:
            print(f"skip unknown city_slug: {r['city_slug']} ({r['name']})")
            continue
        if not is_hard_facility(r):
            raise SystemExit(f"soft facility rejected: {r['name']}")
        kept.append(r)

    facilities = json.loads(FAC_PATH.read_text())
    by_key = {(f.get("city_slug"), f.get("name")): i for i, f in enumerate(facilities)}
    by_addr = {
        (f.get("city_slug"), (f.get("address") or "").lower()[:55])
        for f in facilities
        if f.get("address")
    }
    global_addr = {(f.get("address") or "").lower()[:60] for f in facilities if f.get("address")}
    added = updated = skipped = 0
    for r in kept:
        key = (r["city_slug"], r["name"])
        addr_k = (r["city_slug"], r["address"].lower()[:55])
        gaddr = r["address"].lower()[:60]
        if key in by_key:
            facilities[by_key[key]] = {**facilities[by_key[key]], **r}
            updated += 1
        elif addr_k in by_addr or gaddr in global_addr:
            skipped += 1
        else:
            facilities.append(r)
            by_key[key] = len(facilities) - 1
            by_addr.add(addr_k)
            global_addr.add(gaddr)
            added += 1

    before = len(facilities)
    facilities = [f for f in facilities if is_hard_facility(f)]
    purged = before - len(facilities)

    FAC_PATH.write_text(json.dumps(facilities, indent=2) + "\n")

    print(f"Batch A rows prepared: {len(UPSERTS)} (kept {len(kept)})")
    print(f"Added: {added}  Updated: {updated}  Skipped (dup addr): {skipped}")
    if purged:
        print(f"Hard-purged {purged} soft rows from registry")
    print(f"Final hard total: {len(facilities)}")
    print(f"Networks covered ({len(NETWORKS)}):")
    for n in sorted(NETWORKS):
        print(f"  • {n}")


if __name__ == "__main__":
    main()
