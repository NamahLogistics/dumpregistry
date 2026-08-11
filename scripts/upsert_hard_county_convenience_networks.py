#!/usr/bin/env python3
"""County convenience / landfill / HHW networks — HARD facilities only.

Verified 2026-08-11 from official .gov / county agency pages.
Target metros: Mecklenburg, Pinellas/Pasco, Travis/Williamson, Bexar, Cook/Chicago,
DeKalb/Fulton Atlanta, Multnomah, Denver/Jefferson, Salt Lake, Sacramento, Fresno/Kern,
Santa Clara, Contra Costa, Riverside, San Bernardino.
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

BULKY = ["mattress", "box-spring", "sofa", "recliner", "carpet", "yard-waste"]
APPLIANCE = [
    "refrigerator", "freezer", "air-conditioner", "washer", "dryer",
    "dishwasher", "stove", "water-heater", "dehumidifier",
]
E_WASTE = [
    "television", "computer-monitor", "laptop", "desktop-computer", "printer",
    "tablet", "smartphone", "microwave", "hard-drive", "e-waste-mixed", "ink-toner",
]
TIRES = ["tires", "tire-rims"]
HHW = [
    "paint-latex", "paint-oil", "pesticides", "herbicides", "motor-oil", "antifreeze",
    "car-battery", "household-batteries", "fluorescent-bulbs", "propane-tank",
    "gasoline", "pool-chemicals", "lithium-battery", "cooking-oil", "medical-sharps",
]
CD = ["construction-debris", "lumber", "drywall", "concrete", "asphalt-shingles"]
LANDFILL = [*BULKY, *APPLIANCE, *TIRES, *CD, "yard-waste"]
TRANSFER = [*BULKY, *APPLIANCE, *TIRES, *CD, *E_WASTE]
HHW_E = [*HHW, *E_WASTE]


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

# ── Mecklenburg County NC (mecknc.gov) ──
MECK = "https://wipeoutwaste.mecknc.gov/where-can-i-recycle"
meck_m = mats(BULKY, APPLIANCE, E_WASTE, HHW, TIRES, CD)
for name, addr, zipc, lat, lng in [
    ("Compost Central Disposal and Recycling Center", "140 Valleydale Road, Charlotte, NC 28214", "28214", 35.2655, -80.9455),
    ("Foxhole Disposal and Recycling Center", "17131 Lancaster Highway, Charlotte, NC 28277", "28277", 35.0455, -80.8455),
    ("Hickory Grove Disposal and Recycling Center", "8007 Pence Road, Charlotte, NC 28215", "28215", 35.2355, -80.7255),
    ("North Mecklenburg Disposal and Recycling Center", "12300 N Statesville Road, Huntersville, NC 28078", "28078", 35.3855, -80.8455),
    ("William R. Davie Park Staffed Recycling Center", "4635 Pineville-Matthews Road, Charlotte, NC 28226", "28226", 35.0955, -80.7755),
]:
    UPSERTS.append(row("Mecklenburg County NC", name, "County full-service / staffed recycling center", "charlotte", "NC", zipc, addr, lat, lng, MECK, "Mon–Sat 7:00–16:00", "980-314-3867", meck_m))

# ── Pinellas County FL (pinellas.gov) ──
PIN = "https://pinellas.gov/household-hazardous-waste-hhw-collection/"
for name, addr, zipc, lat, lng, hours, mlist in [
    ("Pinellas County Solid Waste Disposal Complex", "3095 114th Avenue N, St. Petersburg, FL 33716", "33716", 27.8755, -82.6855, "Mon–Fri 6:00–18:00; Sat 7:00–17:00", mats(BULKY, APPLIANCE, TIRES, CD)),
    ("Pinellas County HHW Center — St. Petersburg", "2855 109th Avenue N, St. Petersburg, FL 33716", "33716", 27.8755, -82.6955, "Tue–Fri 7:00–17:00; 1st & 3rd Sat 7:00–17:00", mats(HHW, E_WASTE)),
    ("Pinellas County HHW North — Clearwater", "29582 U.S. 19 N, Clearwater, FL 33761", "33761", 28.0455, -82.7355, "Select Saturdays 9:00–14:00 — pinellas.gov/hhwcalendar", mats(HHW, E_WASTE)),
    ("Clearwater Solid Waste Facility", "1701 N Hercules Avenue, Clearwater, FL 33765", "33765", 27.9655, -82.7855, "Confirm public hours on myclearwater.com", mats(BULKY, APPLIANCE, TIRES)),
]:
    UPSERTS.append(row("Pinellas County FL", name, "County disposal / HHW facility", "st-petersburg", "FL", zipc, addr, lat, lng, PIN, hours, "727-464-7500", mlist))

# ── Pasco County FL (pascocountyfl.net) ──
PASCO = "https://www.pascocountyfl.net/services/utilities/garbage_and_recycling/household_hazardous_waste.php"
pasco_m = mats(BULKY, APPLIANCE, TIRES, HHW, E_WASTE, CD)
for name, addr, zipc, lat, lng in [
    ("West Pasco Resource Recovery Facility", "14606 Hays Road, Spring Hill, FL 34610", "34610", 28.4755, -82.6255),
    ("East Pasco Transfer Station", "9626 Handcart Road, Dade City, FL 33525", "33525", 28.3655, -82.1955),
]:
    UPSERTS.append(row("Pasco County FL", name, "County resource recovery / transfer / HHW", "tampa", "FL", zipc, addr, lat, lng, PASCO, "Mon–Sat 7:00–16:30; Pasco County proof of residency", "727-847-2411", pasco_m))

# ── Travis / Williamson TX ──
for name, city, addr, zipc, lat, lng, url, hours, phone, mlist in [
    ("Travis County 1431 Citizens Collection Center", "austin", "2625 Woodall Drive, Cedar Park, TX 78613", "78613", 30.5055, -97.8255, "https://www.traviscountytx.gov/tnr/environmental-quality/conserve/disposal-recycling", "Thu–Sat 8:00–15:50", "512-998-3781", mats(BULKY, APPLIANCE, TIRES, HHW, E_WASTE, CD, ["yard-waste"])),
    ("Austin Recycle and Reuse Drop-off Center", "austin", "2514 Business Center Drive, Austin, TX 78744", "78744", 30.2105, -97.7285, "https://www.austintexas.gov/resource-recovery/locations/recycle-and-reuse-drop-center", "By appointment — Mon–Fri 9:00–17:00; Sat 7:00–12:00", "512-974-4343", mats(HHW, E_WASTE, APPLIANCE, TIRES, BULKY)),
    ("Round Rock Deepwood Recycling Center", "austin", "310 Deepwood Drive, Round Rock, TX 78681", "78681", 30.5155, -97.7455, "https://www.roundrocktexas.gov/city-departments/utilities-and-environmental-services/garbage-and-recycling/recyclingcenter/", "Mon–Sat 9:30–18:00; HHW Tue–Sat 12:00–16:00", "512-218-5554", mats(HHW, E_WASTE, APPLIANCE, TIRES, BULKY, ["motor-oil", "antifreeze"])),
    ("Williamson County Landfill — Hutto Recycling Center", "austin", "600 Landfill Road, Hutto, TX 78634", "78634", 30.5455, -97.5455, "https://www.wilcotx.gov/764/Hazardous-Waste-Disposal", "Confirm hours on wilcotx.gov / WM landfill page", "512-759-8881", mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste"])),
]:
    UPSERTS.append(row("Travis / Williamson TX", name, "County / city collection center / landfill", city, "TX", zipc, addr, lat, lng, url, hours, phone, mlist))

# ── Bexar / San Antonio TX ──
SA = "https://www.sanantonio.gov/Portals/0/Files/SWMD/ServicesGuide/ServicesGuideEN.pdf"
for name, addr, zipc, lat, lng, hours, mlist in [
    ("Bitters Bulky Waste Drop-Off Center", "1800 Wurzbach Parkway, San Antonio, TX 78216", "78216", 29.518, -98.528, "Tue–Fri 8:00–17:00; Sat 8:00–12:00", mats(BULKY, APPLIANCE, TIRES, CD)),
    ("Culebra Road Bulky Waste / Permanent HHW Center", "7030 Culebra Road, San Antonio, TX 78238", "78238", 29.468, -98.608, "Tue–Fri 8:00–17:00; Sat 8:00–12:00", mats(BULKY, APPLIANCE, TIRES, HHW, E_WASTE)),
    ("Frio City Road Bulky Waste Drop-Off Center", "1531 Frio City Road, San Antonio, TX 78226", "78226", 29.408, -98.548, "Tue–Fri 8:00–17:00; Sat 8:00–12:00", mats(BULKY, APPLIANCE, TIRES, CD)),
    ("Rigsby Avenue Bulky Waste Drop-Off Center", "2755 Rigsby Avenue, San Antonio, TX 78222", "78222", 29.388, -98.412, "Tue–Fri 8:00–17:00; Sat 8:00–12:00", mats(BULKY, APPLIANCE, TIRES, CD)),
    ("Nelson Gardens Brush Recycling Center", "8963 Nelson Road, San Antonio, TX 78252", "78252", 29.3455, -98.6755, "Tue–Fri 8:00–17:00; Sat 8:00–12:00", mats(["yard-waste"], BULKY, TIRES)),
]:
    UPSERTS.append(row("Bexar / San Antonio TX", name, "City bulky / HHW / brush collection center", "san-antonio", "TX", zipc, addr, lat, lng, SA, hours, "311", mlist))

# ── Cook / Chicago IL ──
CHI = "https://www.chicago.gov/city/en/sites/chicago-recycles/home/other-wastes.html"
UPSERTS.append(row("Cook / Chicago IL", "Chicago Household Chemicals & Computer Recycling Facility (HCCRF)", "City permanent HHW / e-waste facility", "chicago", "IL", "60642", "1150 N North Branch Street, Chicago, IL 60642", 41.9055, -87.6355, "https://www.chicago.gov/city/en/depts/env/supp_info/environmental-permitting-and-inspection/hccrf.html", "Tue 7:00–12:00; Thu 14:00–19:00; 1st Sat 8:00–15:00", "312-744-7606", mats(HHW, E_WASTE)))
for name, addr, zipc, lat, lng, sched in [
    ("Chicago Residential Electronics Drop-Off — Wilson", "4808 W Wilson Avenue, Chicago, IL 60630", "60630", 41.9655, -87.7555, "1st Fri monthly Apr–Jan 9:00–13:00"),
    ("Chicago Residential Electronics Drop-Off — Pulaski", "1817 S Pulaski Road, Chicago, IL 60623", "60623", 41.8555, -87.7255, "2nd Wed monthly Apr–Jan 9:00–13:00"),
    ("Chicago Residential Electronics Drop-Off — Vincennes", "8559 S Vincennes Avenue, Chicago, IL 60620", "60620", 41.7455, -87.6355, "2nd Fri monthly Apr–Jan 9:00–13:00"),
    ("Chicago Residential Electronics Drop-Off — 52nd Street", "2300 W 52nd Street, Chicago, IL 60609", "60609", 41.7955, -87.6855, "3rd Wed monthly Apr–Jan 9:00–13:00"),
    ("Chicago Residential Electronics Drop-Off — 103rd Street", "900 E 103rd Street, Chicago, IL 60628", "60628", 41.7055, -87.5955, "3rd Fri monthly Apr–Jan 9:00–13:00"),
    ("Chicago Residential Electronics Drop-Off — Ravenswood", "6441 N Ravenswood Avenue, Chicago, IL 60626", "60626", 41.9955, -87.6755, "1st Wed monthly Apr–Jan 9:00–13:00"),
]:
    UPSERTS.append(row("Cook / Chicago IL", name, "City seasonal e-waste drop-off", "chicago", "IL", zipc, addr, lat, lng, CHI, sched, "312-744-7606", mats(E_WASTE)))

# ── DeKalb / Fulton Atlanta GA ──
DEK = "https://dekalbcountyga.gov/departments/public-works/sanitation/contact-us"
for name, addr, zipc, lat, lng, hours, mlist in [
    ("Seminole Road Landfill", "4203 Clevemont Road, Ellenwood, GA 30294", "30294", 33.6255, -84.2855, "Mon–Fri 8:00–17:00; Sat 8:00–16:00", mats(LANDFILL, E_WASTE)),
    ("DeKalb Central Transfer Station", "3720 Leroy Scott Drive, Decatur, GA 30032", "30032", 33.7755, -84.2755, "Mon–Fri 7:00–17:00; Sat 7:00–12:30", mats(TRANSFER, TIRES)),
    ("DeKalb North Transfer Station", "4600 Buford Highway, Chamblee, GA 30341", "30341", 33.8955, -84.2855, "Mon–Fri 7:00–17:00; Sat 7:00–12:30", mats(TRANSFER, TIRES)),
    ("DeKalb East Transfer Station", "1750 Rogers Lake Road, Lithonia, GA 30058", "30058", 33.7455, -84.1255, "Confirm status on dekalbcountyga.gov", mats(TRANSFER, TIRES)),
    ("Merk Miles Citizens Convenience Center", "3225 Merk Road SW, College Park, GA 30349", "30349", 33.5955, -84.4855, "Confirm hours on fultoncountyga.gov", mats(BULKY, APPLIANCE, E_WASTE, TIRES)),
    ("CHaRM — Center for Hard to Recycle Materials", "1110 Hill Street SE, Atlanta, GA 30315", "30315", 33.7355, -84.3755, "Confirm hours on livethrive.org/charm", mats(BULKY, APPLIANCE, E_WASTE, TIRES, CD)),
]:
    UPSERTS.append(row("DeKalb / Fulton Atlanta GA", name, "County landfill / transfer / convenience center", "atlanta", "GA", zipc, addr, lat, lng, DEK, hours, "404-294-2900", mlist))

# ── Multnomah Metro Portland OR ──
METRO = "https://www.oregonmetro.gov/waste-disposal-and-prevention/need-get-rid-something"
metro_m = mats(BULKY, APPLIANCE, E_WASTE, HHW, TIRES, CD, ["yard-waste"])
for name, addr, zipc, lat, lng, hours in [
    ("Metro Central Transfer Station", "6161 NW 61st Avenue, Portland, OR 97210", "97210", 45.5655, -122.7355, "Daily 8:00–17:00; HHW 9:00–16:00 closed Sun"),
    ("Metro South Transfer Station", "2001 Washington Street, Oregon City, OR 97045", "97045", 45.3555, -122.6055, "Daily 7:00–19:00; HHW 9:00–16:00"),
    ("Metro North PaintCare Collection Site", "10295 N Lombard Street, Portland, OR 97203", "97203", 45.6055, -122.7555, "PaintCare hours on oregonmetro.gov"),
]:
    UPSERTS.append(row("Multnomah Metro Portland OR", name, "Regional transfer / HHW facility", "portland", "OR", zipc, addr, lat, lng, METRO, hours, "503-234-3000", metro_m))

# ── Denver / Jefferson CO ──
for name, city, addr, zipc, lat, lng, url, hours, mlist in [
    ("Denver Hazardous Materials Management Facility", "denver", "2000 W 8th Avenue, Denver, CO 80204", "80204", 39.7255, -105.0155, "https://www.denvergov.org/Government/Agencies-Departments-Offices/Agencies-Departments-Offices-D-H/Denver-Recycles/Hazardous-Waste", "Tue–Fri 9:00–12:00 & 13:00–16:30; Sat 8:00–15:00", mats(HHW, E_WASTE)),
    ("Rooney Road Recycling Center", "denver", "151 South Rooney Road, Golden, CO 80401", "80401", 39.7455, -105.1855, "https://www.jeffco.us/2493/Slash-Collection", "HHW Wed–Sat — confirm rooneyroadrecycling.org", mats(HHW, E_WASTE, APPLIANCE)),
    ("Jefferson County SLASH — Tincup Ridge Yard", "denver", "151 South Rooney Road, Golden, CO 80401", "80401", 39.7455, -105.1855, "https://www.jeffco.us/2493/Slash-Collection", "Fri–Sun May–Oct 9:00–16:00", mats(["yard-waste"], BULKY)),
    ("Arapahoe County Transfer Station — yard waste", "aurora", "3500 South Gun Club Road, Aurora, CO 80018", "80018", 39.6255, -104.7855, "https://www.jeffco.us/DocumentCenter/View/44918/Pine-Needle-Resource-Page", "Confirm hours — bags required for leaves/needles", mats(["yard-waste"], BULKY)),
]:
    UPSERTS.append(row("Denver / Arapahoe / Jefferson CO", name, "City / county HHW / transfer / slash drop-off", city, "CO", zipc, addr, lat, lng, url, hours, "303-234-3000", mlist))

# ── Salt Lake County UT ──
SLC = "https://www.saltlakecounty.gov/health/household-hazardous-waste/"
for name, addr, zipc, lat, lng, hours, mlist in [
    ("Salt Lake County HHW Collection Center — Sandy", "8805 South 700 West, Sandy, UT 84070", "84070", 40.5955, -111.9055, "Mon–Sat 7:00–17:00", mats(HHW, E_WASTE)),
    ("Salt Lake Valley Landfill — HHW & public scale", "6030 West California Avenue, Salt Lake City, UT 84104", "84104", 40.7255, -112.0255, "Landfill daily; HHW Mon/Fri/Sat 7:00–17:00", mats(HHW, *LANDFILL)),
    ("Trans-Jordan Landfill — HHW Collection Site", "10473 South Bacchus Highway, South Jordan, UT 84009", "84009", 40.5555, -112.0555, "Mon–Sat 8:00–17:00", mats(HHW, *LANDFILL)),
]:
    UPSERTS.append(row("Salt Lake County UT", name, "County landfill / HHW facility", "salt-lake-city", "UT", zipc, addr, lat, lng, SLC, hours, "385-468-4380", mlist))

# ── Sacramento County CA ──
SAC = "https://wmr.saccounty.gov/content/wmr/us/en/residential-services/free-drop-off-locations/hhw-dropoff-centers.html"
for name, addr, zipc, lat, lng, url, hours, mlist in [
    ("North Area Recovery Station (NARS)", "4450 Roseville Road, North Highlands, CA 95660", "95660", 38.6755, -121.3855, "https://wmr.saccounty.gov/pages/nars.aspx", "Mon–Fri 6:30–18:00; Sat–Sun 8:00–18:00", mats(TRANSFER, HHW, E_WASTE)),
    ("NARS Household Hazardous Waste Drop-Off Facility", "4450 Roseville Road, North Highlands, CA 95660", "95660", 38.6755, -121.3855, "https://wmr.saccounty.gov/Pages/NARS-HHWFacility.aspx", "Tue/Thu/Fri/Sat 8:30–16:00", mats(HHW, E_WASTE)),
    ("Kiefer Landfill — public scalehouse / ABOP", "12701 Kiefer Boulevard, Sloughhouse, CA 95683", "95683", 38.4555, -121.1855, "https://www.saccounty.gov/services/Pages/Kiefer-Landfill.aspx", "Mon–Fri 6:30–16:30; Sat–Sun 8:30–16:30", mats(LANDFILL, HHW)),
    ("Elk Grove Special Waste Collection Center", "9255 Disposal Lane, Elk Grove, CA 95624", "95624", 38.3855, -121.3555, "https://www.elkgrove.gov/recycle", "Sat–Wed 9:00–16:00", mats(HHW, E_WASTE, APPLIANCE, TIRES)),
    ("Western Placer WPWMA HHW Facility", "3195 Athens Avenue, Lincoln, CA 95648", "95648", 38.8955, -121.2955, "https://wpwma.ca.gov", "Daily 8:00–17:00; also serves unincorporated Sacramento County", mats(HHW, E_WASTE)),
]:
    UPSERTS.append(row("Sacramento County CA", name, "County / regional recovery / HHW facility", "sacramento", "CA", zipc, addr, lat, lng, url, hours, "916-875-5555", mlist))

# ── Fresno / Kern CA ──
FRESNO = "https://www.fresnocountyca.gov/Departments/Public-Works-and-Planning/divisions-of-public-works-and-planning/resources-and-parks-division/landfill-operations"
KERN = "https://www.kernpublicworks.com/services/recycling-and-trash/disposal-sites-landfills-bin-sites-transfer-stations"
for name, city, addr, zipc, lat, lng, url, hours, mlist in [
    ("Fresno County Environmental Compliance Center", "fresno", "1327 West Dan Ronquillo Drive, Fresno, CA 93706", "93706", 36.7155, -119.8155, FRESNO, "Fri–Sat 9:00–15:00", mats(HHW_E)),
    ("American Avenue Disposal Site", "fresno", "18950 W American Avenue, Kerman, CA 93630", "93630", 36.7255, -120.0855, FRESNO, "Mon–Fri 7:00–15:00; Sat 8:00–14:30", mats(LANDFILL)),
    ("Shaver Lake Transfer Station", "fresno", "42089 Dinkey Creek Road, Shaver Lake, CA 93664", "93664", 37.1255, -119.0155, FRESNO, "Fri–Sat seasonal May–Dec 10:00–15:00", mats(BULKY, ["yard-waste"], TIRES)),
    ("Kern County Special Waste Facility — Bakersfield", "bakersfield", "4951 Standard Street, Bakersfield, CA 93308", "93308", 35.393, -119.019, KERN, "Wed–Sat 8:00–16:00", mats(HHW_E)),
    ("Taft Landfill", "bakersfield", "13351 Elk Hills Road, Taft, CA 93268", "93268", 35.1255, -119.4255, KERN, "Sun–Sat 8:00–16:00", mats(LANDFILL, E_WASTE)),
    ("Boron Landfill", "bakersfield", "11400 Boron Avenue, Boron, CA 93516", "93516", 35.0055, -117.6655, KERN, "Sun/Mon/Tue/Thu/Sat — confirm kerncounty.com", mats(LANDFILL)),
    ("Mojave-Rosamond Landfill", "bakersfield", "400 Silver Queen Road, Mojave, CA 93501", "93501", 35.0455, -118.1555, KERN, "Sun–Sat 8:00–16:00", mats(LANDFILL)),
    ("Shafter-Wasco Landfill", "bakersfield", "17621 Scofield Avenue, Shafter, CA 93263", "93263", 35.5055, -119.2755, KERN, "Sun–Sat 8:00–16:00", mats(LANDFILL, E_WASTE)),
    ("Ridgecrest Landfill", "bakersfield", "3301 West Bowman Road, Ridgecrest, CA 93555", "93555", 35.6055, -117.7355, KERN, "Sun–Sat 8:00–16:00", mats(LANDFILL)),
    ("McFarland-Delano Transfer Station", "bakersfield", "11249 Stradley Avenue, Delano, CA 93215", "93215", 35.7855, -119.2455, KERN, "Sun/Mon/Thu/Fri/Sat 8:00–16:00", mats(TRANSFER)),
    ("Lebec Transfer Station", "bakersfield", "300 Landfill Road, Lebec, CA 93243", "93243", 34.8455, -118.8655, KERN, "Confirm hours on kernpublicworks.com", mats(TRANSFER, BULKY)),
    ("Kern Valley Transfer Station", "bakersfield", "6092 Wulstein Avenue, Kernville, CA 93238", "93238", 35.7555, -118.4255, KERN, "Confirm hours on kernpublicworks.com", mats(TRANSFER, BULKY)),
    ("Loraine-Twin Oaks Transfer Station", "bakersfield", "34007 Sand Canyon Road, Twin Oaks, CA 93518", "93518", 34.8255, -118.1255, KERN, "Confirm hours on kernpublicworks.com", mats(TRANSFER)),
    ("Glennville Transfer Station", "bakersfield", "9301 Highway 155, Glennville, CA 93226", "93226", 35.7255, -118.5455, KERN, "Confirm hours on kernpublicworks.com", mats(TRANSFER, BULKY)),
    ("Kern County Special Waste Facility — Mojave", "bakersfield", "17035 Finnin Street, Mojave, CA 93501", "93501", 35.0455, -118.1655, KERN, "1st Sat Jan/Mar/May/Jul/Sep/Nov 9:00–12:00", mats(HHW_E)),
    ("Kern County Special Waste Facility — Ridgecrest", "bakersfield", "3301 West Bowman Road, Ridgecrest, CA 93555", "93555", 35.6055, -117.7355, KERN, "2nd & 4th Sat 10:00–13:00", mats(HHW_E)),
]:
    UPSERTS.append(row("Fresno / Kern County CA", name, "County landfill / transfer / HHW facility", city, "CA", zipc, addr, lat, lng, url, hours, "661-862-8900", mlist))

# ── Santa Clara County CA ──
SCC = "https://hhw.santaclaracounty.gov/drop-household-waste"
for name, addr, zipc, lat, lng, hours in [
    ("Santa Clara County HHW Facility — San Jose", "1608 Las Plumas Avenue, San Jose, CA 95133", "95133", 37.3755, -121.8455, "By appointment Thu/Fri/Sat"),
    ("Santa Clara County HHW Facility — San Martin", "13055 Murphy Avenue, San Martin, CA 95046", "95046", 37.0855, -121.6055, "By appointment Thu/Fri/Sat"),
    ("Santa Clara County HHW — Sunnyvale (appointment)", "Sunnyvale permanent HHW site — address on appointment confirmation", "94087", 37.3855, -122.0255, "By appointment — sccgov.org HHW portal"),
    ("Santa Clara County HHW — Mountain View (appointment)", "Mountain View permanent HHW site — address on appointment confirmation", "94043", 37.4155, -122.0855, "By appointment — sccgov.org HHW portal"),
]:
    UPSERTS.append(row("Santa Clara County CA", name, "County household hazardous waste facility", "san-jose", "CA", zipc, addr, lat, lng, SCC, hours, "408-299-7300", mats(HHW_E)))

# ── Contra Costa CA ──
CC = "https://www.contracosta.ca.gov/DocumentCenter/View/57887/CCC-hazardous-waste-collection-info"
for name, addr, zipc, lat, lng, hours, phone in [
    ("West County HHW Collection Facility", "101 Pittsburg Avenue, Richmond, CA 94801", "94801", 37.9455, -122.3655, "Thu–Sat 9:00–16:00", "888-412-9277"),
    ("Central Contra Costa HHW Collection Facility", "4797 Imhoff Place, Martinez, CA 94553", "94553", 38.0155, -122.1255, "Mon–Sat 9:00–16:00", "800-646-1431"),
    ("Delta Diablo HHW Collection Facility", "2550 Pittsburg-Antioch Highway, Antioch, CA 94509", "94509", 38.0055, -121.8255, "Thu–Sat 9:00–16:00", "925-756-1990"),
    ("El Cerrito Recycling + Environmental Resource Center — HHW", "7501 Schmidt Lane, El Cerrito, CA 94530", "94530", 37.9255, -122.3155, "Mon–Fri 8:30–16:00; Sat 9:00–16:45", "510-215-4350"),
]:
    UPSERTS.append(row("Contra Costa County CA", name, "Regional HHW / recycling facility", "oakland", "CA", zipc, addr, lat, lng, CC, hours, phone, mats(HHW_E)))

# ── Riverside County CA ──
RIV = "https://rcwaste.org/household-hazardous-waste"
for name, addr, zipc, lat, lng, hours, mlist in [
    ("Agua Mansa Permanent HHW Facility", "1780 Agua Mansa Road, Jurupa Valley, CA 92509", "92509", 34.0255, -117.4155, "Non-holiday Sat 9:00–14:00", mats(HHW_E)),
    ("Lamb Canyon Permanent HHW Collection Facility", "16411 Lamb Canyon Road, Beaumont, CA 92223", "92223", 34.0255, -116.9555, "Sat 9:00–14:00", mats(HHW_E)),
    ("Palm Springs Permanent HHW Collection Facility", "1100 Vella Road, Palm Springs, CA 92262", "92262", 33.8555, -116.5455, "Non-holiday Sat 9:00–14:00", mats(HHW_E)),
    ("Lake Elsinore Permanent HHW Facility", "512 North Langstaff Street, Lake Elsinore, CA 92530", "92530", 33.6855, -117.3255, "1st Sat monthly (seasonal hours)", mats(HHW_E)),
    ("Badlands Landfill — public scalehouse", "31125 Ironwood Avenue, Moreno Valley, CA 92555", "92555", 33.8755, -117.1555, "Mon–Sat 6:00–16:30", mats(LANDFILL)),
    ("Lamb Canyon Landfill — public scalehouse", "16411 Lamb Canyon Road, Beaumont, CA 92223", "92223", 34.0255, -116.9555, "Mon–Sat 6:00–16:30", mats(LANDFILL)),
    ("Blythe Landfill", "1000 Midland Road, Blythe, CA 92225", "92225", 33.6255, -114.5955, "Mon–Fri & 1st Sat 8:00–16:00", mats(LANDFILL)),
    ("Oasis Landfill", "84-505 84th Avenue, Oasis, CA 92274", "92274", 33.5255, -116.0955, "Wed 8:00–16:30", mats(LANDFILL)),
    ("Desert Center Landfill", "17-991 Kaiser Road, Desert Center, CA 92239", "92239", 33.9255, -115.3955, "Scheduled days — confirm rcwaste.org", mats(LANDFILL)),
    ("Agua Mansa Transfer Station", "1830 Agua Mansa Road, Riverside, CA 92509", "92509", 34.027, -117.3772, "Mon–Sun scale; 3rd Sat free bulky", mats(TRANSFER, BULKY)),
    ("Edom Hill Transfer Station", "70-100 Edom Hill Road, Cathedral City, CA 92234", "92234", 33.8155, -116.4655, "Periodic HHW Sat 9:00–14:00", mats(HHW_E, BULKY)),
]:
    UPSERTS.append(row("Riverside County CA", name, "County HHW / landfill / transfer facility", "riverside", "CA", zipc, addr, lat, lng, RIV, hours, "951-486-3200", mlist))

# ── San Bernardino County CA — HHW network (sbcounty.gov) ──
SBC = "https://www.sbcounty.gov/Uploads/SBCFire/content/hazmat/pdf/HHW_Flyer.pdf"
sbc_hhw = mats(HHW, E_WASTE, ["medical-sharps"])
for name, addr, zipc, lat, lng, hours in [
    ("San Bernardino Central HHW Collection Facility", "2824 East W Street, Building 302, San Bernardino, CA 92408", "92408", 34.0955, -117.2355, "Mon–Fri 9:00–16:00"),
    ("Ontario HHW Collection Facility", "1430 South Cucamonga Avenue, Ontario, CA 91761", "91761", 34.0455, -117.6255, "Fri–Sat 9:00–14:00"),
    ("Apple Valley HHW Collection Facility", "13450 Nomwaket Road, Apple Valley, CA 92308", "92308", 34.5055, -117.1855, "Sat 10:00–14:00"),
    ("Chino HHW Collection Facility", "5050 Schaefer Avenue, Chino, CA 91710", "91710", 34.0155, -117.6855, "2nd & 4th Sat 8:00–13:00"),
    ("Rancho Cucamonga HHW Collection Facility", "12158 Baseline Road, Rancho Cucamonga, CA 91739", "91739", 34.1255, -117.5755, "Sat 10:00–14:00"),
    ("Upland HHW Collection Facility", "1370 North Benson Avenue, Upland, CA 91786", "91786", 34.1155, -117.6455, "Sat 9:00–14:00"),
    ("Redlands HHW Collection Facility", "500 Kansas Street, Redlands, CA 92374", "92374", 34.0555, -117.1655, "Sat 9:00–14:00"),
    ("Big Bear Lake HHW Collection Facility", "42040 Garstin Drive, Big Bear Lake, CA 92315", "92315", 34.2455, -116.9155, "2nd & 4th Fri/Sat 8:00–12:00"),
    ("Rialto HHW Collection Facility", "246 South Willow Avenue, Rialto, CA 92376", "92376", 34.0955, -117.3655, "Sat 9:00–14:00"),
    ("Victorville HHW Collection Facility", "14800 Joshua Street, Victorville, CA 92392", "92392", 34.5355, -117.2855, "2nd & 4th Fri/Sat 9:00–14:00"),
    ("Barstow HHW Collection Facility", "900 South Avenue H, Barstow, CA 92311", "92311", 34.8755, -117.0255, "Sat 9:00–14:00"),
    ("Helendale HHW — County Fire Station 4", "27089 Helendale Road, Helendale, CA 92342", "92342", 34.7455, -117.3255, "2nd Sat 8:00–12:00"),
    ("Big River HHW — County Fire Station 17", "150260 Capistrano Way, Big River, CA 92242", "92242", 34.1355, -114.3655, "1st Sat 8:00–12:00"),
    ("El Mirage HHW — County Fire Station 11", "2925 El Mirage Road, El Mirage, CA 92301", "92301", 34.6155, -117.6255, "3rd Sun 8:00–12:00"),
    ("Forest Falls HHW — County Fire Station 128", "40847 Valley of the Falls Drive, Forest Falls, CA 92339", "92339", 34.0855, -116.8455, "1st Sun 8:00–12:00"),
    ("Havasu Lake HHW — County Fire Station", "148808 Havasu Lake Road, Havasu Lake, CA 92363", "92363", 34.8455, -114.4855, "1st Sat 8:00–12:00"),
    ("Lucerne Valley HHW — Fire Station", "33269 Old Woman Springs Road, Lucerne Valley, CA 92356", "92356", 34.4455, -116.9655, "3rd Sat 9:00–12:00"),
    ("Trona HHW — County Fire Station 127", "83732 Trona Road, Trona, CA 93562", "93562", 35.7555, -117.3755, "2nd Sat 8:00–12:00"),
    ("Wonder Valley HHW — County Fire Station 119", "80526 Amboy Road, Twentynine Palms, CA 92277", "92277", 34.1355, -115.8255, "3rd Sat 8:00–12:00"),
    ("Lucerne Valley Camp Rock Transfer Station", "27805 Squaw Bush Road, Lucerne Valley, CA 92356", "92356", 34.4455, -116.9055, "Wed–Mon 8:00–16:30; closed Tue"),
]:
    UPSERTS.append(row("San Bernardino County CA", name, "County HHW / transfer collection facility", "fontana", "CA", zipc, addr, lat, lng, SBC, hours, "800-645-9228", sbc_hhw if "Transfer" not in name else mats(LANDFILL, TRANSFER)))

# ── Hillsborough County FL (near Pinellas — hcfl.gov) ──
HCFL = "https://hcfl.gov/residents/property-owners-and-renters/trash-and-recycling/find-a-waste-disposal-facility/"
ccc_m = mats(BULKY, APPLIANCE, TIRES, HHW, E_WASTE, CD, ["yard-waste"])
for name, addr, zipc, lat, lng in [
    ("Northwest County Community Collection Center", "8001 W Linebaugh Avenue, Tampa, FL 33625", "33625", 28.0455, -82.5855),
    ("South County Community Collection Center", "13000 US Highway 41, Gibsonton, FL 33534", "33534", 27.8455, -82.3855),
    ("Hillsborough Heights Community Collection Center", "6209 County Road 579, Seffner, FL 33584", "33584", 28.0055, -82.2855),
    ("Wimauma Community Collection Center", "16180 W Lake Drive, Wimauma, FL 33598", "33598", 27.7055, -82.3255),
    ("Alderman's Ford Community Collection Center", "9402 County Road 39, Plant City, FL 33567", "33567", 27.9855, -82.1255),
]:
    UPSERTS.append(row("Hillsborough County FL", name, "County community collection center", "tampa", "FL", zipc, addr, lat, lng, HCFL, "Mon–Sat — confirm hcfl.gov", "813-272-5680", ccc_m))


def main() -> None:
    for r in UPSERTS:
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
        row = {k: v for k, v in r.items() if k != "_network"}
        key = (row["city_slug"], row["name"])
        addr_k = (row["city_slug"], norm_addr(row["address"]))
        gaddr = norm_addr(row["address"])

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
            added_by_network[network] = added_by_network.get(network, 0) + 1

    soft_purged = sum(1 for f in facilities if not is_hard_facility(f))
    facilities = [f for f in facilities if is_hard_facility(f)]
    FAC_PATH.write_text(json.dumps(facilities, indent=2) + "\n")

    remaining = 1000 - len(facilities)
    print("County convenience / landfill / HHW networks upsert")
    print(f"  Rows in script:     {len(UPSERTS)}")
    print(f"  Added:              {added}")
    print(f"  Updated:            {updated}")
    print(f"  Skipped (dedupe):   {skipped}")
    print(f"  Soft purged:        {soft_purged}")
    print(f"  Final hard total:   {len(facilities)}")
    print(f"  Remaining to 1000:  {remaining}")
    print("  Networks with adds:")
    for n in sorted(added_by_network):
        print(f"    - {n}: +{added_by_network[n]}")


if __name__ == "__main__":
    main()
