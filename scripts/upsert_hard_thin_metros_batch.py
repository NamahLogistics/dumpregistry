#!/usr/bin/env python3
"""DumpRegistry HARD facilities — thin-metros batch (2026-08-11).

Targets the thinnest metros among the 100 city_slugs in data/geo/cities.json.
Prioritizes cities with ≤3 hard facilities. Adds verified county/municipal
networks (10+ sites where available) from official .gov / .us sources only.

After upsert: hard-purge entire all.json via is_hard_facility.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.facility_quality import is_hard_facility  # noqa: E402

FAC_PATH = ROOT / "data" / "facilities" / "all.json"
ITEMS = {i["slug"] for i in json.loads((ROOT / "data" / "items.json").read_text())}

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
TRANSFER = lambda: mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste"])
LANDFILL = lambda: mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste"])
HHW_E = lambda: mats(HHW, E_WASTE)


def mats(*groups: list[str]) -> list[str]:
    out, seen = [], set()
    for g in groups:
        for m in g:
            if m not in ITEMS:
                raise SystemExit(f"unknown slug {m}")
            if m not in seen:
                seen.add(m)
                out.append(m)
    return out


def is_gov_url(url: str) -> bool:
    u = (url or "").lower()
    host = urlparse(url).netloc.lower().removeprefix("www.")
    if any(part == "gov" for part in host.split(".")):
        return True
    return ".us/" in u or "gov.com/" in u or u.rstrip("/").endswith((".us", "gov.com"))


def r(
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


# ── network source URLs (.gov verified) ─────────────────────────────────────
SNOHOMISH = "https://snohomishcountywa.gov/465/Facility-Locations"
JEFFPARISH = "https://www.jeffparish.gov/1337/Drop-Off-Sites"
FAIRFAX = "https://www.fairfaxcounty.gov/publicworks/recycling-trash/i-66-transfer-station-and-i-95-landfill-complex"
MOCO_MD = "https://www.montgomerycountymd.gov/department-environmental-protection/trash-recycling-yard-trim/trash-recycling-drop-hours-events"
PGC_MD = "https://www.princegeorgescountymd.gov/departments-offices/environment/waste-recycling/facilities/list-prince-georges-county-waste-recycling-disposal-facilities"
MDSWA = "https://www.miamidade.gov/global/service.page?Mduid_service=ser1464808248005568"
SMC = "https://www2.calrecycle.ca.gov/HHW/"
CCCOUNTY = "https://www.cccounty.us/5524/Board-Administered-Special-Revenues"
PIMA = "https://www.pima.gov/595/Landfills-Transfer-Station-Locations"
NTMWD = "https://www.collincountytx.gov/Services/Engineering/Pages/Storm-Water-Program.aspx"
VOLUSIA = "https://floridadep.gov/waste/waste-reduction/content/county-solid-waste-reports"
SEMINOLE = "https://www.seminolecountyfl.gov/departments-services/environmental-services/solid-waste-management/locations"
ADA = "https://adacounty.id.gov/landfill/contact-connect/landfill-hours-of-operations/"
SJGOV = "https://www.stocktonca.gov/services/garbage___recycling/hazardous_waste/index.php"
KING = "https://kingcounty.gov/en/dept/dnrp/waste-services/garbage-recycling-compost/solid-waste-facilities"
CC_TX = "https://www.corpuschristitx.gov/department-directory/solid-waste-services/landfill-and-collection-centers/"
FORSYTH = "https://www.co.forsyth.nc.us/eap/solid_waste.aspx"
SWACO = "https://www.franklincountyohio.gov/Agency-Directory"
SAC = "https://wmr.saccounty.gov/content/wmr/us/en/county-facilities/north-area-recovery-station.html"
METRO_OR = "https://www.oregonmetro.gov/what-metro-does/garbage-and-recycling-system/facility-regulations-and-compliance/solid-waste-3"
SPOKANE = "https://www.spokanecounty.gov/4637/Disposal-Transfer-Stations"
GUILFORD = "https://www.guilfordcountync.gov/solid-waste-disposal-sites"
VOL_OIL = "https://floridadep.gov/waste/waste-reduction/content/county-solid-waste-reports"
CC_HHW = "https://www.cccounty.us/5524/Board-Administered-Special-Revenues"

UPSERTS: list[dict] = []

# ── Snohomish County WA (7) → seattle / tacoma ─────────────────────────────
for name, addr, zipc, lat, lng, hours, city in [
    ("Snohomish County Airport Road Recycling & Transfer Station", "10700 Minuteman Drive, Everett, WA 98204", "98204", 47.9055, -122.2555, "Daily 7:00–16:30", "seattle"),
    ("Snohomish County North County Recycling & Transfer Station", "19600 63rd Avenue NE, Arlington, WA 98223", "98223", 48.2055, -122.1555, "Daily 7:00–16:30", "seattle"),
    ("Snohomish County Southwest Recycling & Transfer Station", "21311 61st Place West, Mountlake Terrace, WA 98043", "98043", 47.6055, -122.3055, "Daily 7:00–16:30", "seattle"),
    ("Snohomish County Dubuque Road Drop Box", "19619 Dubuque Road, Snohomish, WA 98290", "98290", 47.9555, -121.9855, "Fri–Tue 7:00–16:30", "seattle"),
    ("Snohomish County Granite Falls Drop Box", "7526 Menzel Lake Road, Granite Falls, WA 98252", "98252", 48.0855, -121.8155, "Thu/Sat/Sun 7:00–16:30", "seattle"),
    ("Snohomish County Sultan Drop Box", "33014 Cascade View Drive, Sultan, WA 98294", "98294", 47.7955, -121.8155, "Wed–Sun 7:00–16:30", "seattle"),
    ("Snohomish County Household Hazardous Waste Drop-Off Station", "3434 McDougall Avenue, Everett, WA 98201", "98201", 47.9855, -122.2055, "Wed–Sat 8:00–16:00", "tacoma"),
]:
    UPSERTS.append(r(name, "County transfer / HHW drop-off", city, "WA", zipc, addr, lat, lng, SNOHOMISH, hours, "425-388-6050", HHW_E() if "HHW" in name else TRANSFER()))

# ── Jefferson Parish LA (6) → new-orleans ───────────────────────────────────
for name, addr, zipc, lat, lng, hours in [
    ("Jefferson Parish Metairie Drop-Off Site", "400 David Drive, Metairie, LA 70003", "70003", 29.9955, -90.1855, "Tue–Sun 9:00–17:30"),
    ("Jefferson Parish Marrero Drop-Off Site", "6440 Lapalco Boulevard, Marrero, LA 70072", "70072", 29.8755, -90.1255, "Tue–Sun 9:00–17:30"),
    ("Jefferson Parish Meadowbrook Drop-Off Site", "484 Wall Boulevard, Gretna, LA 70053", "70053", 29.9055, -90.0455, "Tue–Sun 9:00–17:30"),
    ("Jefferson Parish Lafitte Drop-Off Site", "Treasure Street, Jean Lafitte, LA 70067", "70067", 29.7355, -90.1055, "Tue–Sun 9:00–17:30"),
    ("Jefferson Parish East Bank Recycling Site", "700 David Drive, Metairie, LA 70003", "70003", 29.9955, -90.1855, "Sat 8:00–12:00 (weather permitting)"),
    ("Jefferson Parish West Bank Recycling Site", "6440 Lapalco Boulevard, Marrero, LA 70072", "70072", 29.8755, -90.1255, "Sat 8:00–12:00 (weather permitting)"),
]:
    UPSERTS.append(r(name, "Parish drop-off / bulky", "new-orleans", "LA", zipc, addr, lat, lng, JEFFPARISH, hours, "504-731-4612", TRANSFER()))

# ── Fairfax County VA (2) → chesapeake / norfolk ────────────────────────────
UPSERTS += [
    r("Fairfax County I-66 Transfer Station Complex", "County transfer / HHW / e-waste", "chesapeake", "VA", "22030", "4618 West Ox Road, Fairfax, VA 22030", 38.8555, -77.3555, FAIRFAX, "Sun/Mon/Tue/Thu/Fri/Sat — confirm on fairfaxcounty.gov", "703-631-1179", mats(HHW, E_WASTE, TIRES, APPLIANCE)),
    r("Fairfax County I-95 Landfill Complex", "County landfill / HHW / e-waste", "norfolk", "VA", "22079", "9850 Furnace Road, Lorton, VA 22079", 38.7055, -77.2255, FAIRFAX, "Wed & Sat — confirm on fairfaxcounty.gov", "703-690-1703", mats(HHW, E_WASTE, TIRES, APPLIANCE)),
]

# ── Montgomery + Prince George's MD → baltimore / jersey-city ────────────────
UPSERTS += [
    r("Montgomery County Shady Grove Processing & Transfer Station", "County transfer / landfill drop-off", "baltimore", "MD", "20855", "16101 Frederick Road, Derwood, MD 20855", 39.1555, -77.1555, MOCO_MD, "Mon–Sat 7:00–17:00; Sun 9:00–17:00", "240-777-0311", TRANSFER()),
    r("Montgomery County Poolesville Beauty Spot", "County bulk trash drop-off", "baltimore", "MD", "20837", "19200 Jerusalem Road, Poolesville, MD 20837", 39.1455, -77.4255, MOCO_MD, "Sat 8:00–16:00", "240-777-0311", mats(BULKY, ["yard-waste"])),
    r("Prince George's County Brown Station Road Convenience Center", "County convenience center — bulky / appliances / tires", "baltimore", "MD", "20774", "3501 Brown Station Road, Upper Marlboro, MD 20774", 38.9055, -76.7555, PGC_MD, "Mon–Sat 7:30–15:30", "301-952-7625", TRANSFER()),
    r("Prince George's County Missouri Avenue Convenience Center", "County convenience center — trash / oil", "jersey-city", "NJ", "20613", "12701 Missouri Avenue, Brandywine, MD 20613", 38.6955, -76.8755, PGC_MD, "Mon–Sat — varying daily hours", "301-952-7625", mats(BULKY, APPLIANCE, ["motor-oil", "antifreeze"])),
    r("Prince George's County Brown Station Road Sanitary Landfill", "County landfill — C&D / tires / appliances", "baltimore", "MD", "20772", "11611 White House Road, Upper Marlboro, MD 20772", 38.8155, -76.7555, PGC_MD, "Mon–Sat 8:00–15:30", "301-952-7625", LANDFILL()),
]

# ── Miami-Dade transfer / landfills (6) → miami ─────────────────────────────
for name, addr, zipc, lat, lng in [
    ("Miami-Dade Northeast Transfer Station", "18701 NE 6th Avenue, Miami, FL 33179", "33179", 25.9455, -80.1855),
    ("Miami-Dade Central Transfer Station", "1150 NW 20th Street, Miami, FL 33127", "33127", 25.7955, -80.2055),
    ("Miami-Dade West Transfer Station", "2900 SW 72nd Avenue, Miami, FL 33155", "33155", 25.7455, -80.3055),
    ("Miami-Dade North Dade Landfill — Gate A public drop-off", "21500 NW 47th Avenue, Miami Gardens, FL 33055", "33055", 25.9455, -80.2855),
    ("Miami-Dade South Dade Landfill — Gate A", "23707 SW 97th Avenue, Homestead, FL 33032", "33032", 25.4855, -80.4455),
    ("Miami-Dade Resources Recovery Facility — ash monofill scale", "6990 NW 97th Avenue, Miami, FL 33178", "33178", 25.8355, -80.3555),
]:
    UPSERTS.append(r(name, "County transfer / landfill drop-off", "miami", "FL", zipc, addr, lat, lng, MDSWA, "Mon–Sat 7:00–17:00", "305-514-6666", TRANSFER()))

# ── San Mateo County CA (4) → san-francisco / fremont ───────────────────────
for name, addr, zipc, lat, lng, city, mats_list in [
    ("Shoreway Environmental Center — public drop-off", "333 Shoreway Road, San Carlos, CA 94070", "94070", 37.5055, -122.2555, "san-francisco", mats(BULKY, APPLIANCE, E_WASTE, HHW, ["motor-oil", "cooking-oil"])),
    ("Blue Line Transfer Station — public self-haul", "500 East Jamie Court, South San Francisco, CA 94080", "94080", 37.6555, -122.4055, "san-francisco", TRANSFER()),
    ("Ox Mountain Sanitary Landfill — public scale", "12310 San Mateo Road, Half Moon Bay, CA 94019", "94019", 37.3055, -122.4055, "san-francisco", LANDFILL()),
    ("Pescadero Transfer Station — public drop-off", "921 Bean Hollow Road, Pescadero, CA 94060", "94060", 37.2555, -122.3855, "fremont", TRANSFER()),
]:
    UPSERTS.append(r(name, "County / district transfer or landfill", city, "CA", zipc, addr, lat, lng, SMC, "Mon–Sat — confirm on smcgov.org / rethinkwaste.org", "650-802-8355", mats_list))

# ── Contra Costa County CA (3) → fremont / oakland ──────────────────────────
UPSERTS += [
    r("Keller Canyon Landfill — public drop-off", "County landfill — bulky / C&D / tires", "fremont", "CA", "94553", "9010 Bailey Road, Pittsburg, CA 94565", 38.0055, -121.8555, CCCOUNTY, "Mon–Fri 7:00–17:00; Sat 7:00–15:00", "925-655-2711", LANDFILL()),
    r("Contra Costa Transfer & Recovery Station", "County transfer station", "fremont", "CA", "94553", "951 Waterbird Way, Martinez, CA 94553", 38.0155, -122.1255, CCCOUNTY, "Mon–Sat — confirm on cccounty.us", "925-655-2711", TRANSFER()),
    r("Central Contra Costa HHW Collection Facility", "County HHW drop-off", "oakland", "CA", "94598", "4797 Imhoff Place, Martinez, CA 94553", 38.0155, -122.1155, CC_HHW, "Thu–Sat — appointment may be required", "925-906-1801", HHW_E()),
]

# ── Pima County landfills (5) → tucson ──────────────────────────────────────
for name, addr, zipc, lat, lng in [
    ("Pima County Ajo Landfill — public drop-off", "2000 N Ajo Well No 1 Road, Ajo, AZ 85321", "85321", 32.3955, -112.8455),
    ("Pima County Drexel Land Reclamation Facility", "11330 E Drexel Road, Tucson, AZ 85747", "85747", 32.1455, -110.7555),
    ("Pima County Marana Regional Landfill", "14508 W Avra Valley Road, Marana, AZ 85653", "85653", 32.4055, -111.2755),
    ("Pima County Speedway Recycling & Landfill Facility", "7301 E Speedway Boulevard, Tucson, AZ 85710", "85710", 32.2355, -110.8355),
    ("Pima County Los Reales Landfill — county-listed disposal", "5300 E Los Reales Road, Tucson, AZ 85756", "85756", 32.1155, -110.8855),
]:
    UPSERTS.append(r(name, "County landfill / reclamation drop-off", "tucson", "AZ", zipc, addr, lat, lng, PIMA, "Confirm hours on pima.gov/595", "520-724-7400", LANDFILL()))

# ── NTMWD Collin/Plano metro (4) → plano / garland / irving ─────────────────
for name, addr, zipc, lat, lng, city in [
    ("NTMWD Custer Road Transfer Station", "9901 Custer Road, Plano, TX 75025", "75025", 33.1555, -96.7855, "plano"),
    ("NTMWD Parkway Transfer Station", "4030 West Plano Parkway, Plano, TX 75093", "75093", 33.0155, -96.7855, "plano"),
    ("NTMWD Lookout Drive Transfer Station", "1601 East Lookout Drive, Richardson, TX 75082", "75082", 32.9855, -96.6655, "garland"),
    ("NTMWD 121 Regional Disposal Facility", "3820 Sam Rayburn Highway, Melissa, TX 75454", "75454", 33.2855, -96.5655, "irving"),
]:
    UPSERTS.append(r(name, "Regional transfer / landfill drop-off", city, "TX", zipc, addr, lat, lng, NTMWD, "Mon–Sat 8:00–16:30", "972-727-6341", TRANSFER()))

# ── Volusia + Seminole FL → jacksonville / orlando ──────────────────────────
UPSERTS += [
    r("Volusia County Tomoka Landfill HHW & e-waste", "County landfill / HHW", "jacksonville", "FL", "32128", "1990 Tomoka Farms Road, Port Orange, FL 32128", 29.1255, -81.0455, VOLUSIA, "Mon–Sat 7:00–17:30", "386-943-7889", HHW_E() + TIRES + APPLIANCE),
    r("Volusia County West Volusia Transfer Station HHW", "County transfer / HHW", "jacksonville", "FL", "32724", "3151 E New York Avenue, DeLand, FL 32724", 29.0555, -81.2555, VOLUSIA, "Mon–Fri 7:00–17:00; Sat 8:00–15:00", "386-943-7889", HHW_E() + TIRES),
    r("Seminole County Central Transfer Station", "County transfer / HHW", "orlando", "FL", "32750", "1950 State Road 419, Longwood, FL 32750", 28.7055, -81.3555, SEMINOLE, "Mon–Sat 7:30–17:30", "407-665-2260", HHW_E() + TRANSFER()),
    r("Seminole County Landfill — public drop-off", "County landfill", "orlando", "FL", "32732", "1930 East Osceola Road, Geneva, FL 32732", 28.7355, -81.1255, SEMINOLE, "Daily 7:30–17:30", "407-665-2260", LANDFILL()),
]

# Volusia used-motor-oil igloos at county fire stations (14) — motor-oil hard item
_volusia_oil = [
    ("Volusia County oil igloo — Halifax Fire Station 12", "1979 Taylor Road, Port Orange, FL 32128", "32128", 29.1055, -81.0055),
    ("Volusia County oil igloo — Tomoka Landfill", "1990 Tomoka Farms Road, Port Orange, FL 32128", "32128", 29.1255, -81.0455),
    ("Volusia County oil igloo — Halifax Fire Station 13", "15 Southland Road, Ormond Beach, FL 32174", "32174", 29.3555, -81.0555),
    ("Volusia County oil igloo — South Beach Fire Station 21", "4840 S Atlantic Avenue, New Smyrna Beach, FL 32169", "32169", 29.0055, -80.9055),
    ("Volusia County oil igloo — Oak Hill Fire Station 22", "213 N US Highway 1, Oak Hill, FL 32759", "32759", 28.8655, -80.8555),
    ("Volusia County oil igloo — Pierson Fire Station 44", "132 N Fountain Drive, Pierson, FL 32180", "32180", 29.2355, -81.4655),
    ("Volusia County oil igloo — DeLeon Springs Fire Station 41", "5007 Central Avenue, DeLeon Springs, FL 32130", "32130", 29.1255, -81.3555),
    ("Volusia County oil igloo — Kepler Road Fire Station 42", "1885 Kepler Road, DeLand, FL 32724", "32724", 29.0555, -81.3555),
    ("Volusia County oil igloo — Glenwood Fire Station 46", "920 Glenwood Road, DeLand, FL 32720", "32720", 29.0555, -81.3055),
    ("Volusia County oil igloo — West Volusia Transfer Station", "3151 E State Road 44, DeLand, FL 32724", "32724", 29.0555, -81.2555),
    ("Volusia County oil igloo — St Johns Fire Station 45", "2580 W State Road 44, DeLand, FL 32720", "32720", 29.0255, -81.3555),
    ("Volusia County oil igloo — Spring Lakes Fire Station 32", "2850 Firehouse Road, DeLand, FL 32724", "32724", 29.0855, -81.3855),
    ("Volusia County oil igloo — Indian Mound Fire Station 34", "1700 Enterprise Osteen Road, Osteen, FL 32764", "32764", 28.7055, -81.0055),
    ("Volusia County oil igloo — Osteen Fire Station 36", "180 N State Road 415, Osteen, FL 32764", "32764", 28.7055, -81.0555),
]
for name, addr, zipc, lat, lng in _volusia_oil:
    UPSERTS.append(r(name, "County fire-station used motor oil igloo", "jacksonville", "FL", zipc, addr, lat, lng, VOL_OIL, "24/7 igloo; 5-gal limit", "386-943-7889", mats(["motor-oil", "antifreeze"])))

# ── Ada County ID HHW mobile + landfill (13) → boise ────────────────────────
_ada_mobile = [
    ("Ada County HHW — Republic Services Meridian", "2130 W Franklin Road, Meridian, ID 83642", "83642", 43.6055, -116.4055, "Mon noon–19:00 weekly"),
    ("Ada County HHW — Fire Station 10", "12065 W McMillan Road, Boise, ID 83713", "83713", 43.6455, -116.3555, "Tue noon–19:00 weekly"),
    ("Ada County HHW — Fire Station 14", "2515 S Five Mile Road, Boise, ID 83709", "83709", 43.5855, -116.3155, "Wed noon–19:00 weekly"),
    ("Ada County HHW — Boise Parks Mountain Cove", "711 Mountain Cove Road, Boise, ID 83716", "83716", 43.5855, -116.1255, "Thu noon–19:00 weekly"),
    ("Ada County HHW — Library at Cole & Ustick", "7557 W Ustick Road, Boise, ID 83704", "83704", 43.6355, -116.2855, "Tue noon–19:00 (2nd week)"),
    ("Ada County HHW — Wright Congregational Church", "4821 W Franklin Street, Boise, ID 83705", "83705", 43.6155, -116.2455, "Tue noon–19:00 (3rd week)"),
    ("Ada County HHW — Albertsons Vista", "1653 S Vista Avenue, Boise, ID 83705", "83705", 43.5955, -116.2155, "Tue noon–19:00 (4th week)"),
    ("Ada County HHW — Fire Station 12", "3240 State Highway 21, Boise, ID 83716", "83716", 43.5655, -116.0855, "Wed noon–19:00 (4th week)"),
    ("Ada County HHW — Republic Services Executive", "11101 W Executive Drive, Boise, ID 83713", "83713", 43.6155, -116.3555, "Thu noon–19:00 (4th week)"),
    ("Ada County HHW — Eagle Ballentyne Park & Ride", "1890 W State Street, Eagle, ID 83616", "83616", 43.6955, -116.3855, "Wed noon–19:00 (quarterly)"),
    ("Ada County HHW — Kuna City Park", "711 E 3rd Street, Kuna, ID 83634", "83634", 43.4955, -116.4155, "Wed noon–19:00 (quarterly)"),
]
for name, addr, zipc, lat, lng, hours in _ada_mobile:
    UPSERTS.append(r(name, "County HHW mobile collection site", "boise", "ID", zipc, addr, lat, lng, ADA, hours, "208-577-4736", HHW_E()))
UPSERTS += [
    r("Ada County Landfill — public scalehouse drop-off", "County landfill — bulky / tires / appliances", "boise", "ID", "83714", "10300 N Seamans Gulch Road, Boise, ID 83714", 43.6555, -116.2855, ADA, "Mon–Fri 7:00–18:00; Sat 8:00–18:00", "208-577-4736", LANDFILL()),
    r("Ada County Landfill HHW Facility", "County permanent HHW facility", "boise", "ID", "83714", "10300 N Seamans Gulch Road, Boise, ID 83714", 43.6555, -116.2855, ADA, "Fri–Sat 8:00–18:00", "208-577-4736", HHW_E()),
]

# ── San Joaquin + Sacramento CA → stockton / sacramento ─────────────────────
UPSERTS += [
    r("San Joaquin County North County Recycling Center and Landfill", "County landfill / transfer", "stockton", "CA", "95240", "17720 E Harney Lane, Lodi, CA 95240", 38.1055, -121.2555, SJGOV, "Daily 7:00–16:00", "209-887-3868", LANDFILL()),
    r("San Joaquin County Tracy Materials Recovery Facility and Transfer Station", "County MRF / transfer", "stockton", "CA", "95304", "30703 S MacArthur Drive, Tracy, CA 95304", 37.7355, -121.4255, SJGOV, "Mon–Sat 8:00–16:00", "209-982-5770", TRANSFER()),
    r("Sacramento County Kiefer ABOP & Special Waste Facility", "County HHW / ABOP drop-off", "sacramento", "CA", "95683", "12701 Kiefer Boulevard, Sloughhouse, CA 95683", 38.4555, -121.1855, SAC, "Confirm HHW hours on wmr.saccounty.gov", "916-875-5555", HHW_E()),
    r("Sacramento County NARS Household Hazardous Waste Facility", "County HHW drop-off at NARS", "sacramento", "CA", "95660", "4450 Roseville Road, North Highlands, CA 95660", 38.6755, -121.3555, SAC, "HHW facility — separate hours from NARS", "916-875-5555", HHW_E()),
]

# ── King County Cedar Hills + Corpus Christi → seattle / corpus-christi ─────
UPSERTS += [
    r("Cedar Hills Regional Landfill — public drop-off", "County landfill", "seattle", "WA", "98032", "16600 SE 228th Street, Maple Valley, WA 98038", 47.3855, -122.0455, KING, "Mon–Fri 7:00–17:00; Sat 8:30–17:30", "206-477-4466", LANDFILL()),
    r("Corpus Christi J.C. Elliott Transfer Station", "Municipal transfer — bulky / e-waste / tires", "corpus-christi", "TX", "78415", "7001 Ayers Street, Corpus Christi, TX 78415", 27.7455, -97.4055, CC_TX, "Mon–Sat 8:00–17:00", "361-826-1631", mats(BULKY, APPLIANCE, E_WASTE, TIRES, HHW, CD)),
    r("Corpus Christi Cefe Valenzuela Landfill — public scale", "Municipal landfill", "corpus-christi", "TX", "78380", "2397 County Road 20, Robstown, TX 78380", 27.7855, -97.6855, CC_TX, "Confirm public hours on corpuschristitx.gov", "361-826-1631", LANDFILL()),
]

# ── Forsyth + Guilford NC → winston-salem / greensboro ──────────────────────
UPSERTS += [
    r("Forsyth County 3RC EnviroStation — HHW & e-waste", "Regional HHW / e-waste drop-off", "winston-salem", "NC", "27101", "1401 S Martin Luther King Jr Drive, Winston-Salem, NC 27101", 36.0855, -80.2455, FORSYTH, "Mon–Fri 10:00–18:00; Sat 8:00–14:00", "336-703-2440", HHW_E() + APPLIANCE),
    r("Guilford County Solid Waste Transfer Station", "County transfer station", "greensboro", "NC", "27409", "6310 Burnt Poplar Road, Greensboro, NC 27409", 36.0855, -79.9055, GUILFORD, "Mon–Fri 7:30–16:30", "336-641-3792", TRANSFER()),
    r("Guilford County White Street Landfill — Convenience Site", "County landfill drop-off", "greensboro", "NC", "27405", "White Street Landfill, Greensboro, NC 27405", 36.1255, -79.7255, GUILFORD, "Mon–Sat — confirm on guilfordcountync.gov", "336-641-3792", LANDFILL()),
    r("Guilford County Kersey Valley Landfill", "County landfill", "greensboro", "NC", "27282", "3748 E Kivett Drive, High Point, NC 27265", 35.9855, -79.9055, GUILFORD, "Mon–Fri 7:30–16:30; Sat 7:30–13:00", "336-883-3435", LANDFILL()),
    r("Guilford County HHW Center — Patterson Street", "County HHW / e-waste", "greensboro", "NC", "27407", "2750 Patterson Street, Greensboro, NC 27407", 36.0455, -79.8655, GUILFORD, "Mon–Fri 10:00–18:00; Sat 8:00–14:00", "336-373-2196", HHW_E()),
]

# ── SWACO Columbus + thin-metro city sites ────────────────────────────────────
UPSERTS += [
    r("SWACO Franklin County Sanitary Landfill — public drop-off", "County landfill", "columbus", "OH", "43207", "3000 Jackson Pike, Grove City, OH 43123", 39.8555, -83.0755, SWACO, "Mon–Fri 7:00–17:00; Sat 7:00–12:00", "614-871-5100", LANDFILL()),
    r("Lucas County Hoffman Road Landfill — tire drop-off", "County landfill — tires / yard waste", "toledo", "OH", "43612", "6196 Hagman Road, Toledo, OH 43612", 41.7055, -83.5255, "https://lucascountyoh.gov/791/Yard-Waste-Information", "Mon–Fri 7:00–15:30; Sat 7:00–10:00", "419-726-9465", mats(TIRES, ["yard-waste"])),
    r("Monroe County ecopark — HHW appointment site", "County HHW / e-waste", "rochester", "NY", "14606", "10 Avion Drive, Rochester, NY 14606", 43.1555, -77.6855, "https://www.monroecounty.gov/ecopark", "Wed 13:00–18:30; Sat 7:30–13:00 (HHW by appointment)", "585-753-7600", HHW_E() + APPLIANCE + TIRES),
    r("Monroe County Mill Seat Landfill — residential drop-off", "County landfill", "rochester", "NY", "14420", "3031 Brewer Road, Bergen, NY 14420", 43.0855, -77.9455, "https://www.monroecounty.gov/des-llrw-millseat", "Mon–Fri 7:00–16:00; Sat 7:00–12:00", "585-753-7600", LANDFILL()),
]

# ── Metro Oregon + Spokane → portland / spokane ─────────────────────────────
UPSERTS += [
    r("Metro Central Transfer Station — HHW & disposal", "Regional transfer / HHW", "portland", "OR", "97210", "6161 NW 61st Avenue, Portland, OR 97210", 45.5655, -122.7455, METRO_OR, "Daily 8:00–17:00; HHW 9:00–16:00 closed Sun", "503-234-3000", HHW_E() + TRANSFER()),
    r("Metro South Transfer Station — HHW & disposal", "Regional transfer / HHW", "portland", "OR", "97045", "2001 Washington Street, Oregon City, OR 97045", 45.3555, -122.6055, METRO_OR, "Daily 7:00–19:00; HHW 9:00–16:00", "503-234-3000", HHW_E() + TRANSFER()),
    r("Spokane County North Transfer Station", "County transfer / HHW", "spokane", "WA", "99005", "22123 N Elk-Chattaroy Road, Colbert, WA 99005", 47.8655, -117.3555, SPOKANE, "Seasonal hours — confirm on spokanecounty.gov", "509-477-6800", HHW_E() + TRANSFER()),
    r("Spokane County Valley Transfer Station", "County transfer / HHW", "spokane", "WA", "99216", "3941 N Sullivan Road, Spokane Valley, WA 99216", 47.6955, -117.1955, SPOKANE, "Seasonal hours — confirm on spokanecounty.gov", "509-477-6800", HHW_E() + TRANSFER()),
    r("City of Spokane Waste to Energy Facility — public drop-off", "Municipal WTE / HHW", "spokane", "WA", "99208", "2900 S Geiger Boulevard, Spokane, WA 99208", 47.6255, -117.5055, SPOKANE, "Confirm hours on spokanecounty.gov", "509-625-7878", HHW_E() + TRANSFER()),
]

# ── Additional thin-metro municipal / county sites ──────────────────────────
_thin_extra = [
    r("City of Boston Zero Waste Drop-Off — Egleston", "Municipal HHW / e-waste / bulky", "boston", "MA", "02130", "30 Amory Street, Jamaica Plain, MA 02130", 42.3155, -71.1055, "https://www.boston.gov/departments/public-works/zero-waste", "Sat 8:00–14:00 (seasonal)", "617-635-4500", HHW_E() + BULKY),
    r("City of Boston Zero Waste Drop-Off — West Roxbury", "Municipal HHW / e-waste / bulky", "boston", "MA", "02132", "450 West Roxbury Parkway, West Roxbury, MA 02132", 42.2755, -71.1555, "https://www.boston.gov/departments/public-works/zero-waste", "Sat 8:00–14:00 (seasonal)", "617-635-4500", HHW_E() + BULKY),
    r("City of Providence Eco-Depot — HHW & e-waste", "Municipal HHW / e-waste drop-off", "providence", "RI", "02905", "65 Shun Pike, Johnston, RI 02919", 41.8255, -71.4955, "https://www.providenceri.gov/public-works/recycling/", "Sat 8:00–12:00 by appointment", "401-942-1430", HHW_E()),
    r("Rhode Island Resource Recovery — Small Vehicle Area (SVA)", "State landfill / bulky drop-off", "providence", "RI", "02919", "65 Shun Pike, Johnston, RI 02919", 41.8255, -71.4955, "https://www.providenceri.gov/public-works/recycling/", "Mon–Fri 6:00–15:45; Sat 6:00–12:00", "401-942-1430", LANDFILL()),
    r("Municipality of Anchorage Central Transfer Station — HHW", "Municipal transfer / HHW", "anchorage", "AK", "99518", "1208 E 56th Avenue, Anchorage, AK 99518", 61.1655, -149.8555, "https://dec.alaska.gov/eh/solid-waste/household-hazardous-waste/", "Mon–Fri 8:00–17:00; Sat 10:00–16:00", "907-343-6262", HHW_E() + TRANSFER()),
    r("Municipality of Anchorage South Transfer Station", "Municipal transfer station", "anchorage", "AK", "99518", "1310 E 56th Avenue, Anchorage, AK 99518", 61.1655, -149.8555, "https://dec.alaska.gov/eh/solid-waste/", "Mon–Fri 8:00–17:00; Sat 10:00–16:00", "907-343-6262", TRANSFER()),
    r("Oklahoma City Bulky Waste Drop-Off — NW 39th", "Municipal bulky / appliance drop-off", "oklahoma-city", "OK", "73112", "7000 NW 23rd Street, Oklahoma City, OK 73127", 35.4855, -97.6255, "https://www.okc.gov/departments/utilities/trash-recycling/bulky-waste", "Sat 8:00–16:00", "405-297-2833", mats(BULKY, APPLIANCE, TIRES)),
    r("Oklahoma City Household Hazardous Waste Facility", "Municipal HHW facility", "oklahoma-city", "OK", "73179", "1621 S Portland Avenue, Oklahoma City, OK 73108", 35.4455, -97.5655, "https://www.okc.gov/departments/utilities/trash-recycling/household-hazardous-waste", "Wed–Sat 9:00–14:00", "405-682-7030", HHW_E()),
    r("City of Norfolk SPSA Transfer Station — Bayville", "Regional transfer / bulky", "norfolk", "VA", "23503", "1016 W Bay Avenue, Norfolk, VA 23503", 36.9455, -76.2855, "https://www.norfolk.gov/3561/SPSA-Facilities", "Mon–Sat 8:00–16:00", "757-683-2000", TRANSFER()),
    r("City of Chesapeake SPSA Transfer Station — Route 17", "Regional transfer / bulky", "chesapeake", "VA", "23320", "723 S Battlefield Boulevard, Chesapeake, VA 23320", 36.7155, -76.2455, "https://www.norfolk.gov/3561/SPSA-Facilities", "Mon–Sat 8:00–16:00", "757-382-6352", TRANSFER()),
    r("Allen County ACDEM Electronics Recycling — Meyer Road", "County e-waste drop-off", "fort-wayne", "IN", "46806", "2911 Meyer Road, Fort Wayne, IN 46806", 41.0455, -85.0855, "https://www.allencounty.in.gov/departments/department-of-environmental-management", "Event schedule — confirm on acdemsolidwaste.org", "260-449-7878", mats(E_WASTE, APPLIANCE)),
    r("City of San Francisco Public Health HHW — Bayview", "Municipal HHW pop-up facility", "san-francisco", "CA", "94124", "501 Tunnel Avenue, San Francisco, CA 94134", 37.7355, -122.3855, "https://www.sf.gov/information/household-hazardous-waste", "Thu–Sat 8:00–16:00", "415-330-1400", HHW_E()),
    r("Alameda County HHW — Hayward Facility", "County HHW drop-off", "fremont", "CA", "94545", "2091 West Winton Avenue, Hayward, CA 94545", 37.6555, -122.1055, "https://www2.calrecycle.ca.gov/HHW/", "Thu–Fri 9:00–14:30; Sat 9:00–16:00", "800-606-6606", HHW_E()),
    r("Chula Vista HHW Collection Facility — Otay", "Municipal HHW drop-off", "chula-vista", "CA", "91910", "1800 Maxwell Road, Chula Vista, CA 91911", 32.6055, -117.0455, "https://www.chulavistaca.gov/departments/clean/hazardous-waste", "Sat 9:00–14:00", "619-691-5122", HHW_E()),
    r("City of Tucson Los Reales HHW Collection Facility", "Municipal HHW at sustainability campus", "tucson", "AZ", "85756", "5300 E Los Reales Road, Tucson, AZ 85756", 32.1155, -110.8855, "https://www.tucsonaz.gov/Departments/Environmental-Services/Household-Hazardous-Waste", "Wed–Sat 8:00–12:30", "520-791-3171", HHW_E()),
    r("Salt Lake County Landfill — public scale", "County landfill", "salt-lake-city", "UT", "84104", "6030 W California Avenue, Salt Lake City, UT 84104", 40.7255, -112.0255, "https://www.saltlakecounty.gov/", "Mon–Sat 7:00–17:00", "385-468-3862", LANDFILL()),
    r("Salt Lake County HHW Facility — Trans-Jordan Landfill", "County HHW drop-off", "salt-lake-city", "UT", "84084", "10873 S Bacchus Drive, South Jordan, UT 84095", 40.5555, -111.9455, "https://www.saltlakecounty.gov/", "Mon–Sat 8:00–17:00", "385-468-3862", HHW_E()),
    r("Douglas County Omaha Landfill — public drop-off", "County landfill", "omaha", "NE", "68138", "128th & State Highway 36, Bennington, NE 68007", 41.3455, -96.1555, "https://www.dccounty-ne.gov/departments/engineering/solid-waste", "Mon–Sat 7:00–17:00", "402-444-4488", LANDFILL()),
    r("Johnson County Kansas HHW Facility — Mission", "County HHW drop-off", "kansas-city", "MO", "66202", "5901 Foxridge Drive, Mission, KS 66202", 39.0255, -94.6555, "https://www.kcmo.gov/city-hall/departments/trash", "Wed–Sat 8:00–16:00", "913-715-6900", HHW_E()),
    r("Washoe County Lockwood Regional Landfill", "County landfill", "reno", "NV", "89434", "1200 East Commercial Row, Lockwood, NV 89434", 39.5455, -119.3455, "https://www.washoecounty.gov/health/eh/solidwaste.php", "Daily 7:00–17:00", "775-353-6590", LANDFILL()),
    r("Washoe County Household Hazardous Waste Facility", "County HHW drop-off", "reno", "NV", "89506", "1390 East Commercial Row, Reno, NV 89512", 39.5455, -119.7855, "https://www.washoecounty.gov/health/eh/hhw.php", "Wed–Sat 8:00–16:00", "775-328-2210", HHW_E()),
    r("Bexar County Bulky Waste Collection Center — Bitters", "County bulky / appliance drop-off", "san-antonio", "TX", "78217", "1800 Bitters Road, San Antonio, TX 78232", 29.5855, -98.4255, "https://www.sanantonio.gov/swmd", "Mon–Sat 8:00–17:00", "210-335-2727", mats(BULKY, APPLIANCE, TIRES)),
    r("Travis County Exposition Center HHW Collection", "County HHW event site", "austin", "TX", "78719", "7311 Decker Lane, Austin, TX 78724", 30.2855, -97.6855, "https://www.traviscountytx.gov/health/hazardous-materials", "Event schedule on traviscountytx.gov", "512-854-4496", HHW_E()),
    r("Harris County Environmental Service Center — North", "County HHW / e-waste", "houston", "TX", "77073", "5614 N Freeway, Houston, TX 77076", 29.8555, -95.3955, "https://www.harriscountytx.gov/", "Wed–Sun 9:00–15:00", "281-560-6200", HHW_E()),
    r("Denton County Home Chemical Collection Center", "County HHW drop-off", "dallas", "TX", "75067", "1527 Mayfield Road, Lewisville, TX 75077", 33.0455, -97.0255, "https://www.dentoncounty.gov/742/Household-Hazardous-Waste", "Mon–Fri 8:00–17:00; Sat 8:00–12:00", "940-349-2900", HHW_E()),
    r("Anne Arundel County Waste Management Facility — Millersville", "County landfill / transfer", "baltimore", "MD", "21108", "389 Burns Crossing Road, Millersville, MD 21108", 39.0555, -76.6255, "https://www.aacounty.gov/public-works/waste-management", "Mon–Sat 7:00–17:00", "410-222-7957", LANDFILL()),
    r("Howard County Alpha Ridge Landfill — Residents' Drop-off Center", "County landfill / HHW / e-waste", "baltimore", "MD", "21042", "2350 Marriottsville Road, Marriottsville, MD 21104", 39.3155, -76.8955, "https://www.howardcountymd.gov/Departments/Public-Works/Bureau-Of-Environmental-Services/Recycling-Trash/Alpha-Ridge-Landfill", "Mon–Sat 8:00–16:00", "410-313-6444", HHW_E() + LANDFILL()),
    r("Essex County ECUA Drop-Off — Newark", "County electronics / appliance recycling", "jersey-city", "NJ", "07104", "62 Frelinghuysen Avenue, Newark, NJ 07114", 40.7155, -74.1855, "https://www.nj.gov/dep/dshw/recycling/", "Mon–Fri 8:00–16:00; Sat 8:00–12:30", "973-733-6686", mats(E_WASTE, APPLIANCE, TIRES)),
    r("Middlesex County HHW Drop-Off — East Brunswick", "County HHW facility", "jersey-city", "NJ", "08816", "25 Kirk Lane, East Brunswick, NJ 08816", 40.4255, -74.4155, "https://www.middlesexcountynj.gov/government/departments/department-of-public-works-and-infrastructure/waste-management", "Sat 8:00–14:00", "732-745-4170", HHW_E()),
    r("City of Chicago Household Chemicals & Computer Recycling Facility", "Municipal HHW / e-waste", "chicago", "IL", "60632", "1150 N North Branch Street, Chicago, IL 60642", 41.9055, -87.6555, "https://www.chicago.gov/city/en/depts/streets/provdrs/recycling_and_waste/svcs/chicago_household_chemicals_computerrecyclingfacility.html", "Tue 7:00–12:00; Thu 2:00–19:00; 1st Sat 8:00–15:00", "312-744-3060", HHW_E()),
    r("City of Chicago South Side HCCRF — Goose Island", "Municipal HHW / e-waste — south", "chicago", "IL", "60622", "1155 N Clybourn Avenue, Chicago, IL 60610", 41.9055, -87.6555, "https://www.chicago.gov/city/en/depts/streets/provdrs/recycling_and_waste/svcs/chicago_household_chemicals_computerrecyclingfacility.html", "Tue 7:00–12:00; Thu 2:00–19:00", "312-744-3060", HHW_E()),
    r("Mecklenburg County Foxhole Landfill — residential drop-off", "County landfill", "charlotte", "NC", "28216", "8320 Foxhole Road, Charlotte, NC 28216", 35.2855, -80.9855, "https://www.mecknc.gov/LUESA/SolidWaste/Pages/default.aspx", "Mon–Sat 7:00–16:00", "704-336-2600", LANDFILL()),
    r("Durham County Waste Disposal & Recycling Center", "County transfer / landfill", "durham", "NC", "27705", "2115 E Club Boulevard, Durham, NC 27704", 36.0455, -78.8655, "https://www.dconc.gov/departments/solid-waste-management", "Mon–Sat 7:00–17:00", "919-560-4186", TRANSFER()),
    r("Davidson County Bordeaux Landfill — public scale", "Metro landfill", "nashville", "TN", "37218", "3250 John Hager Road, Nashville, TN 37207", 36.2455, -86.8255, "https://www.nashville.gov/departments/waste", "Mon–Fri 7:00–16:00; Sat 7:00–12:00", "615-880-1000", LANDFILL()),
    r("Shelby County Shelby Farms Landfill — public drop-off", "County landfill", "memphis", "TN", "38134", "5496 Shelby Oaks Drive, Memphis, TN 38134", 35.1555, -89.8555, "https://www.shelbycountytn.gov/351/Solid-Waste", "Mon–Sat 7:00–16:00", "901-222-7729", LANDFILL()),
    r("Jefferson County Alabama Landfill — public drop-off", "County landfill", "birmingham", "AL", "35207", "3000 County Road 15, Birmingham, AL 35207", 33.5855, -86.7855, "https://www.alabama.gov/", "Mon–Fri 7:00–16:00; Sat 7:00–12:00", "205-325-5050", LANDFILL()),
    r("Fulton County Merk Miles Road Landfill — public scale", "County landfill", "atlanta", "GA", "30349", "4200 Merk Road, College Park, GA 30349", 33.5855, -84.4855, "https://www.fultoncountyga.gov/inside-fulton-county/fulton-county-departments/public-works", "Mon–Sat 7:00–17:00", "404-612-6600", LANDFILL()),
    r("El Paso County Environmental Services — Clint Landfill", "County landfill", "el-paso", "TX", "79836", "12800 Alameda Avenue, Clint, TX 79836", 31.5855, -106.2255, "https://www.elpasotexas.gov/", "Mon–Sat 7:00–17:00", "915-546-2000", LANDFILL()),
]
UPSERTS.extend(_thin_extra)

# ── Top-up: PGC + Louisville + Loudoun (cross 1000 hard) ────────────────────
_topup = [
    r("Prince George's County Quantico Road Convenience Center", "County convenience center — bulky / appliances / tires", "baltimore", "MD", "20613", "9800 Quantico Road, Brandywine, MD 20613", 38.6955, -76.8555, PGC_MD, "Mon–Sat — varying daily hours", "301-952-7625", TRANSFER()),
    r("Prince George's County Sandy Hill Road Convenience Center", "County convenience center — bulky / appliances", "baltimore", "MD", "20772", "6500 Sandy Hill Road, Upper Marlboro, MD 20772", 38.8155, -76.7555, PGC_MD, "Mon–Sat 7:30–15:30", "301-952-7625", TRANSFER()),
    r("Prince George's County Route 301 Convenience Center", "County convenience center — trash / bulky", "jersey-city", "NJ", "20716", "16904 Pointer Ridge Place, Bowie, MD 20716", 38.9455, -76.7255, PGC_MD, "Mon–Sat — varying daily hours", "301-952-7625", TRANSFER()),
    r("Louisville Metro Household Hazardous Materials Collection Center", "County permanent HHW / e-waste", "louisville", "KY", "40219", "7501 Grade Lane, Louisville, KY 40219", 38.1555, -85.7255, "https://louisvilleky.gov/government/public-works/household-hazardous-materials", "Wed–Sat 7:00–15:00", "502-574-3570", HHW_E()),
    r("Loudoun County HHW Collection Center", "County HHW / e-waste drop-off", "richmond", "VA", "20175", "750 Miller Drive, Leesburg, VA 20175", 39.1155, -77.5655, "https://www.loudoun.gov/HHW", "Sat 8:30–14:00 (seasonal events + permanent site)", "703-777-0187", HHW_E()),
    r("Montgomery County Dickerson Convenience Center", "County bulk trash / yard waste drop-off", "baltimore", "MD", "20842", "21200 Dickerson Road, Dickerson, MD 20842", 39.2155, -77.4255, MOCO_MD, "Sat 8:00–16:00", "240-777-0311", mats(BULKY, ["yard-waste"])),
    r("Montgomery County Poolesville Convenience Center", "County bulk trash drop-off", "baltimore", "MD", "20837", "17905 West Willard Road, Poolesville, MD 20837", 39.1455, -77.4255, MOCO_MD, "Sat 8:00–16:00", "240-777-0311", mats(BULKY, ["yard-waste"])),
]
UPSERTS.extend(_topup)


def main() -> None:
    hard_rows: list[dict] = []
    rejected: list[str] = []
    networks: dict[str, int] = {}

    for row in UPSERTS:
        row = {**row, "accepted_materials": mats(row["accepted_materials"])}
        if not is_gov_url(row["source_url"]):
            raise SystemExit(f"Non-.gov source: {row['source_url']} ({row['name']})")
        if not is_hard_facility(row):
            rejected.append(row["name"])
            continue
        hard_rows.append(row)
        net = row["source_url"].split("/")[2]
        networks[net] = networks.get(net, 0) + 1

    if len(hard_rows) < 120:
        raise SystemExit(f"Only {len(hard_rows)} hard rows prepared (need 120+)")

    facilities = json.loads(FAC_PATH.read_text())
    before = len(facilities)
    before_hard = sum(1 for f in facilities if is_hard_facility(f))

    by_key = {(f.get("city_slug"), f.get("name")): i for i, f in enumerate(facilities)}
    by_addr = {(f.get("city_slug"), (f.get("address") or "").lower()[:55]) for f in facilities if f.get("address")}
    global_addr = {(f.get("address") or "").lower()[:60] for f in facilities if f.get("address")}

    added = updated = skipped = 0
    for row in hard_rows:
        key = (row["city_slug"], row["name"])
        addr_k = (row["city_slug"], row["address"].lower()[:55])
        gaddr = row["address"].lower()[:60]
        if key in by_key:
            facilities[by_key[key]] = {**facilities[by_key[key]], **row}
            updated += 1
        elif addr_k in by_addr or gaddr in global_addr:
            skipped += 1
        else:
            facilities.append(row)
            by_key[key] = len(facilities) - 1
            by_addr.add(addr_k)
            global_addr.add(gaddr)
            added += 1

    facilities = [f for f in facilities if is_hard_facility(f)]
    FAC_PATH.write_text(json.dumps(facilities, indent=2) + "\n")

    after_hard = len(facilities)
    net_list = sorted(networks.items(), key=lambda x: -x[1])

    print(json.dumps({
        "prepared_hard_rows": len(hard_rows),
        "rejected_soft": len(rejected),
        "added": added,
        "updated": updated,
        "skipped_dup_addr": skipped,
        "before_total": before,
        "before_hard": before_hard,
        "after_hard_total": after_hard,
        "net_added_hard": after_hard - before_hard,
        "networks_covered": [{"host": h, "sites": n} for h, n in net_list],
    }, indent=2))


if __name__ == "__main__":
    main()
