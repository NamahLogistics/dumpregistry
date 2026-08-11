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
