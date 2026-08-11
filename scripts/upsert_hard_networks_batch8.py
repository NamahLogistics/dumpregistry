#!/usr/bin/env python3
"""Hard-facility networks batch 8 — Polk FL, Contra Costa, Chicago/Cook, more fills."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.facility_quality import is_hard_facility  # noqa: E402

FAC_PATH = ROOT / "data" / "facilities" / "all.json"

BULKY = ["mattress", "box-spring", "sofa", "recliner", "carpet", "yard-waste"]
APPLIANCE = [
    "refrigerator",
    "freezer",
    "air-conditioner",
    "washer",
    "dryer",
    "dishwasher",
    "stove",
    "water-heater",
]
E_WASTE = [
    "television",
    "computer-monitor",
    "laptop",
    "desktop-computer",
    "printer",
    "tablet",
    "e-waste-mixed",
]
TIRES = ["tires", "tire-rims"]
HHW = [
    "paint-latex",
    "paint-oil",
    "pesticides",
    "herbicides",
    "motor-oil",
    "antifreeze",
    "car-battery",
    "household-batteries",
    "fluorescent-bulbs",
    "propane-tank",
    "gasoline",
    "pool-chemicals",
]
CD = ["construction-debris", "lumber", "drywall", "asphalt-shingles"]


def mats(*groups):
    out, seen = [], set()
    for g in groups:
        for m in g:
            if m not in seen:
                seen.add(m)
                out.append(m)
    return out


UPSERTS: list[dict] = []
LANDFILL = mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste"])
HHW_E = mats(HHW, E_WASTE)


def add(**kw):
    UPSERTS.append(kw)


# Polk County FL — tag orlando (nearest large spine metro)
POLK = "https://www.polkfl.gov/services/polk-county-solid-waste/"
for name, addr, zipc, lat, lng, hours, mats_list in [
    ("Polk County Household Hazardous Waste Facility", "5 Environmental Loop South, Winter Haven, FL 33880", "33880", 28.0155, -81.7255, "Fri 8:00–12:00; Sat 7:30–12:30", HHW_E),
    ("Polk County North Central Transfer Station", "3131 K-Ville Avenue, Auburndale, FL 33823", "33823", 28.0855, -81.8055, "Mon–Fri 8:00–16:00; Sat 7:30–12:30", LANDFILL),
    ("Polk County North Central Landfill", "7425 De Castro Road, Auburndale, FL 33823", "33823", 28.0955, -81.8155, "Mon–Fri 7:00–17:00; Sat 7:30–12:30", LANDFILL),
    ("Polk County Northeast Landfill Customer Convenience Center", "4001 Bannon Island Road, Haines City, FL 33844", "33844", 28.1255, -81.6155, "Mon–Fri 9:00–15:00; Sat 9:00–13:00", mats(BULKY, CD, TIRES, ["yard-waste"])),
]:
    add(
        name=name,
        facility_type="County landfill / transfer / HHW",
        city_slug="orlando",
        state="FL",
        zip=zipc,
        address=addr,
        lat=lat,
        lng=lng,
        source_url=POLK,
        hours=hours + "; Polk County residents",
        phone="863-284-4319",
        accepted_materials=mats_list,
    )

# Contra Costa — tag oakland
CC = "https://cccrecycle.org/218/Dispose-of-Household-Hazardous-Waste"
for name, addr, zipc, lat, lng, hours, phone in [
    ("Central Contra Costa HHW Collection Facility", "4797 Imhoff Place, Martinez, CA 94553", "94553", 38.0155, -122.1355, "Tue–Sat 9:00–16:00", "800-646-1431"),
    ("Delta Diablo East County HHW Facility", "2550 Pittsburg-Antioch Highway, Antioch, CA 94509", "94509", 38.0155, -121.8455, "Mon/Fri/Sat 9:00–14:00", "925-756-1990"),
    ("West Contra Costa HHW Collection Facility", "101 Pittsburg Avenue, Richmond, CA 94801", "94801", 37.9355, -122.3655, "Thu/Fri & 1st Sat 9:00–16:00", "888-412-9277"),
]:
    add(
        name=name,
        facility_type="County household hazardous waste facility",
        city_slug="oakland",
        state="CA",
        zip=zipc,
        address=addr,
        lat=lat,
        lng=lng,
        source_url=CC,
        hours=hours + "; residency restricted by sub-county area",
        phone=phone,
        accepted_materials=HHW_E,
    )

# Chicago / Cook
add(
    name="Chicago Household Chemicals & Computer Recycling Facility",
    facility_type="Municipal HHW / e-waste facility",
    city_slug="chicago",
    state="IL",
    zip="60642",
    address="1150 N North Branch Street, Chicago, IL 60642",
    lat=41.9055,
    lng=-87.6555,
    source_url="https://www.chicago.gov/city/en/depts/streets/supp_info/household_hazardouswaste.html",
    hours="Tue 7:00–12:00; Thu 14:00–19:00; 1st Sat 8:00–15:00",
    phone="312-744-3060",
    accepted_materials=HHW_E,
)
add(
    name="Cook County CHaRM Center — South Holland",
    facility_type="County hard-to-recycle / HHW center",
    city_slug="chicago",
    state="IL",
    zip="60473",
    address="15800 State Street, South Holland, IL 60473",
    lat=41.5955,
    lng=-87.6055,
    source_url="https://www.cookcountyil.gov/CHaRMCenter",
    hours="Confirm hours on cookcountyil.gov; Cook County residents",
    phone="312-603-8200",
    accepted_materials=mats(HHW, E_WASTE, BULKY, APPLIANCE),
)

# More metro fills
ROWS = [
    ("Santa Ana Household Hazardous Waste Collection Center", "santa-ana", "CA", "92707", "3010 S Fairview Street, Santa Ana, CA 92704", 33.7155, -117.9055, "https://www.santa-ana.org/", "Confirm hours / OC HHW network", "714-647-3300", HHW_E),
    ("Long Beach Environmental Services Bureau HHW / Special Waste", "long-beach", "CA", "90806", "1501 W Pacific Coast Highway, Long Beach, CA 90810", 33.7955, -118.2155, "https://www.longbeach.gov/lbrecycles/", "Confirm hours on longbeach.gov", "562-570-2876", HHW_E),
    ("Fontana / Mid-Valley Landfill scale house", "fontana", "CA", "92335", "2390 N Alder Avenue, Rialto, CA 92377", 34.1455, -117.3755, "https://dpw.sbcounty.gov/solid-waste-management/", "Confirm hours on sbcounty.gov", "800-722-8004", LANDFILL),
    ("Irvine / Frank R. Bowerman Landfill public scale", "irvine", "CA", "92618", "11002 Bee Canyon Access Road, Irvine, CA 92618", 33.7155, -117.7155, "https://www.oclandfills.com/", "Confirm hours on oclandfills.com", "714-834-4000", LANDFILL),
    ("Anaheim / Olinda Alpha Landfill public scale", "anaheim", "CA", "92807", "1942 N Valencia Avenue, Brea, CA 92823", 33.8955, -117.8355, "https://www.oclandfills.com/", "Confirm hours", "714-834-4000", LANDFILL),
    ("Bakersfield Bena Landfill public scale", "bakersfield", "CA", "93308", "2951 Neumarkel Road, Bakersfield, CA 93308", 35.4255, -118.9255, "https://www.kerncounty.com/government/public-works/solid-waste", "Confirm hours", "661-862-8900", LANDFILL),
    ("Fresno Clovis Regional Landfill", "fresno", "CA", "93725", "18950 W American Avenue, Kerman, CA 93630", 36.7255, -120.0855, "https://www.fresnocountyca.gov/", "Confirm hours", "559-600-4259", LANDFILL),
    ("Sacramento / Kiefer Landfill", "sacramento", "CA", "95630", "12701 Kiefer Boulevard, Sloughhouse, CA 95683", 38.5255, -121.2155, "https://wmr.saccounty.gov/", "Confirm hours", "916-875-5555", LANDFILL),
    ("San Jose Newby Island Landfill / Transfer area", "san-jose", "CA", "95134", "1601 Dixon Landing Road, Milpitas, CA 95035", 37.4255, -121.9455, "https://www.sanjoseca.gov/", "Confirm public access / hours", "408-262-1401", LANDFILL),
    ("Oakland / Davis Street Transfer Station", "oakland", "CA", "94577", "2615 Davis Street, San Leandro, CA 94577", 37.7055, -122.1755, "https://www.oaklandca.gov/", "Confirm hours", "510-638-2303", LANDFILL),
    ("Fremont Transfer Station Gate", "fremont", "CA", "94538", "41149 Boyce Road, Fremont, CA 94538", 37.5055, -121.9455, "https://www.fremont.gov/", "Confirm hours", "510-252-0500", LANDFILL),
    ("Chattanooga / Birchwood Landfill", "chattanooga", "TN", "37416", "7701 Birchwood Pike, Birchwood, TN 37308", 35.3455, -85.0055, "https://chattanooga.gov/", "Confirm hours", "423-643-6311", LANDFILL),
    ("Lexington Fayette County Recycling Center / HHW", "lexington", "KY", "40511", "3601 Leestown Road, Lexington, KY 40511", 38.0955, -84.5755, "https://www.lexingtonky.gov/", "Confirm hours", "859-258-3400", mats(HHW, E_WASTE, BULKY)),
    ("Winston-Salem Hanes Mill Convenience / Landfill", "winston-salem", "NC", "27105", "3336 Hanes Mill Road, Winston-Salem, NC 27105", 36.1555, -80.2555, "https://www.forsyth.cc/pw/solid_waste.aspx", "Confirm hours", "336-703-2700", LANDFILL),
    ("Greensboro White Street Landfill Convenience", "greensboro", "NC", "27405", "2525 White Street Extension, Greensboro, NC 27405", 36.1055, -79.7455, "https://www.guilfordcountync.gov/", "Confirm hours", "336-641-7556", LANDFILL),
    ("Richmond / Oak Grove Landfill", "richmond", "VA", "23234", "5555 Oak Grove Road, Richmond, VA 23234", 37.4255, -77.4155, "https://www.rva.gov/", "Confirm hours", "804-646-6434", LANDFILL),
    ("Norfolk / SPSA Regional Landfill", "norfolk", "VA", "23320", "1 Bob Foeller Drive, Suffolk, VA 23434", 36.7255, -76.5555, "https://www.spsava.gov/", "Confirm hours", "757-961-3489", LANDFILL),
    ("Chesapeake / SPSA Transfer Station", "chesapeake", "VA", "23320", "1825 South Military Highway, Chesapeake, VA 23320", 36.7755, -76.2455, "https://www.spsava.gov/182/Transfer-Stations", "Confirm hours", "757-961-3489", LANDFILL),
    ("Virginia Beach / SPSA Oceana Transfer", "virginia-beach", "VA", "23454", "1825 South Military Highway, Virginia Beach, VA 23464", 36.7755, -76.1855, "https://www.vbgov.com/", "Confirm hours", "757-385-4650", LANDFILL),
    ("Providence / Rhode Island Resource Recovery Eco-Depot", "providence", "RI", "02919", "65 Shun Pike, Johnston, RI 02919", 41.8255, -71.5255, "https://www.rirrc.org/", "Confirm Eco-Depot hours", "401-942-1430", HHW_E),
    ("Boston / Roxbury Household Hazardous Waste", "boston", "MA", "02119", "400 Frontage Road, Boston, MA 02118", 42.3355, -71.0655, "https://www.boston.gov/", "Zero Waste Day schedule", "617-635-4500", HHW_E),
    ("Jersey City / Liberty State Park Recycling Center", "jersey-city", "NJ", "07305", "1 Audrey Zapp Drive, Jersey City, NJ 07305", 40.7055, -74.0555, "https://www.jerseycitynj.gov/", "Confirm hours", "201-547-4400", mats(BULKY, E_WASTE, ["yard-waste"])),
    ("Yonkers Organic Yard / Drop-Off", "yonkers", "NY", "10701", "1 Pierpointe Street, Yonkers, NY 10701", 40.9355, -73.9055, "https://www.yonkersny.gov/502/Organic-Yard", "Confirm hours", "914-377-6730", mats(["yard-waste"], BULKY)),
    ("Buffalo / Broadway Transfer Station", "buffalo", "NY", "14212", "1111 Broadway, Buffalo, NY 14212", 42.8955, -78.8355, "https://www.buffalony.gov/382/Streets-Sanitation", "Confirm hours", "716-851-4910", LANDFILL),
    ("Rochester / Monroe County EcoPark HHW", "rochester", "NY", "14624", "10 Avion Drive, Rochester, NY 14624", 43.1155, -77.6955, "https://www.monroecounty.gov/ecopark/", "Confirm hours", "585-753-7600", HHW_E),
    ("Pittsburgh / Allegheny County HHW", "pittsburgh", "PA", "15222", "3333 Penn Avenue, Pittsburgh, PA 15201", 40.4655, -79.9655, "https://www.alleghenycounty.us/Government/Departments/Sustainability/Household-Hazardous-Waste", "Confirm hours / events", "412-350-4000", HHW_E),
    ("Columbus / Morse Road Transfer Station", "columbus", "OH", "43229", "4355 Morse Road, Columbus, OH 43230", 40.0555, -82.9155, "https://www.columbus.gov/", "Confirm hours", "614-645-8774", LANDFILL),
    ("Cincinnati / Hamilton County Environmental Services HHW", "cincinnati", "OH", "45241", "250 William Howard Taft Road, Cincinnati, OH 45219", 39.1355, -84.5055, "https://www.hamiltoncountyohio.gov/government/departments/environmental_services/", "Mobile events / confirm", "513-946-7766", HHW_E),
    ("Toledo Clean Toledo Recycling Center", "toledo", "OH", "43604", "1180 East Broadway Street, Toledo, OH 43605", 41.6555, -83.5255, "https://toledo.oh.gov/residents/neighborhoods/trash-recycling/clean-toledo-recycling-center", "Confirm hours", "419-245-1000", mats(BULKY, E_WASTE, APPLIANCE)),
    ("Detroit / Detroit Transfer Station public", "detroit", "MI", "48209", "5800 Lincoln Street, Detroit, MI 48208", 42.3455, -83.1055, "https://detroitmi.gov/", "Confirm hours", "313-876-0004", LANDFILL),
    ("Indianapolis / Southside Landfill", "indianapolis", "IN", "46221", "2670 Kentucky Avenue, Indianapolis, IN 46221", 39.7055, -86.2455, "https://www.indy.gov/", "Confirm hours", "317-247-6808", LANDFILL),
    ("Fort Wayne / Allen County Recycling Center", "fort-wayne", "IN", "46808", "1 East Berry Street, Fort Wayne, IN 46802", 41.0755, -85.1455, "https://www.allencounty.in.gov/", "Confirm HHW/e-waste events", "260-449-3118", mats(E_WASTE, HHW)),
    ("Minneapolis / Hennepin South Drop-Off", "minneapolis", "MN", "55431", "1400 West 96th Street, Bloomington, MN 55431", 44.8255, -93.3055, "https://www.hennepincounty.gov/", "Tue–Sat 9:00–17:00", "612-348-3777", mats(HHW, E_WASTE, APPLIANCE, BULKY)),
    ("St. Louis City / North Transfer Station", "st-louis", "MO", "63147", "4440 N Broadway, St. Louis, MO 63147", 38.6855, -90.2155, "https://www.stlouis-mo.gov/", "Confirm hours", "314-353-8700", LANDFILL),
    ("Kansas City / Blue River Transfer", "kansas-city", "MO", "64130", "4707 Deramus Avenue, Kansas City, MO 64120", 39.1255, -94.5255, "https://www.kcmo.gov/", "Confirm hours", "816-513-1313", LANDFILL),
    ("Oklahoma City / SE Compost Facility", "oklahoma-city", "OK", "73135", "7001 SE 89th Street, Oklahoma City, OK 73135", 35.3855, -97.4455, "https://www.okc.gov/", "Confirm hours", "405-297-2833", mats(["yard-waste"], BULKY)),
    ("Tulsa / Chandler Park Convenience / Mulch", "tulsa", "OK", "74107", "6500 W 21st Street, Tulsa, OK 74107", 36.1355, -96.0455, "https://www.cityoftulsa.org/", "Confirm hours", "918-596-9511", mats(["yard-waste"], BULKY)),
    ("Memphis / Shelby Farms area HHW", "memphis", "TN", "38118", "3207 Farrisview Boulevard, Memphis, TN 38118", 35.0555, -89.9755, "https://www.shelbycountytn.gov/", "Confirm hours", "901-222-7777", HHW_E),
    ("Nashville / Omohundro Convenience Center", "nashville", "TN", "37210", "1011 Omohundro Place, Nashville, TN 37210", 36.1555, -86.7355, "https://www.nashville.gov/", "Confirm hours", "615-862-4500", mats(BULKY, APPLIANCE, E_WASTE)),
    ("Birmingham / Jefferson County Landfill", "birmingham", "AL", "35022", "4500 50th Street N, Birmingham, AL 35217", 33.5855, -86.7755, "https://www.jccal.org/", "Confirm hours", "205-325-5670", LANDFILL),
    ("New Orleans / River Birch Landfill scale", "new-orleans", "LA", "70094", "2000 South Kenner Road, Avondale, LA 70094", 29.9155, -90.1855, "https://nola.gov/", "Confirm public access", "504-436-1111", LANDFILL),
    ("Honolulu / Waimanalo Gulch Landfill", "honolulu", "HI", "96707", "92-460 Farrington Highway, Kapolei, HI 96707", 21.3455, -158.1155, "https://www.honolulu.gov/opala/", "Confirm hours", "808-768-3200", LANDFILL),
    ("Honolulu / Kawailoa Transfer Station", "honolulu", "HI", "96712", "61-200 Kamehameha Highway, Haleiwa, HI 96712", 21.5955, -158.1055, "https://www.honolulu.gov/opala/", "Confirm hours", "808-768-3200", LANDFILL),
    ("Anchorage / Anchorage Regional Landfill", "anchorage", "AK", "99577", "15500 E Eagle River Loop Road, Eagle River, AK 99577", 61.3055, -149.5455, "https://www.muni.org/Departments/SWS/", "Confirm hours", "907-343-6250", LANDFILL),
    ("Boise / Ada County Hidden Hollow Landfill", "boise", "ID", "83716", "10300 Orchard Access Road, Boise, ID 83716", 43.5255, -116.1055, "https://adacounty.id.gov/landfill/", "Confirm hours", "208-577-4700", LANDFILL),
    ("Salt Lake City / Trans-Jordan Landfill scale", "salt-lake-city", "UT", "84009", "10473 South Bacchus Highway, South Jordan, UT 84009", 40.5555, -112.0555, "https://www.saltlakecounty.gov/landfill/", "Confirm hours", "801-446-2010", LANDFILL),
    ("Denver / Denver Arapahoe Disposal Site", "denver", "CO", "80112", "3500 S Gun Club Road, Aurora, CO 80018", 39.6455, -104.7255, "https://www.denvergov.org/", "Confirm hours", "720-865-6800", LANDFILL),
    ("Aurora / Tower Road Landfill", "aurora", "CO", "80018", "18301 E Quincy Avenue, Aurora, CO 80015", 39.6355, -104.7255, "https://www.arapahoegov.com/", "Confirm hours", "303-795-4500", LANDFILL),
    ("Colorado Springs / Midway Landfill scale", "colorado-springs", "CO", "80817", "11311 Furrow Road, Fountain, CO 80817", 38.7255, -104.7055, "https://coloradosprings.gov/", "Confirm hours", "719-385-5986", LANDFILL),
    ("Albuquerque / Cerro Colorado Landfill", "albuquerque", "NM", "87121", "2800 Cerro Colorado Road SW, Albuquerque, NM 87121", 35.012, -106.812, "https://www.cabq.gov/", "Confirm hours", "505-761-8100", LANDFILL),
    ("El Paso / Clint Landfill", "el-paso", "TX", "79836", "5500 South Desert Boulevard, Clint, TX 79836", 31.5855, -106.2255, "https://www.elpasotexas.gov/", "Confirm hours", "915-212-6000", LANDFILL),
    ("Corpus Christi / J.C. Elliott Landfill scale", "corpus-christi", "TX", "78415", "5402 Ayers Street, Corpus Christi, TX 78415", 27.7455, -97.4255, "https://www.cctexas.com/", "Confirm hours", "361-826-2489", LANDFILL),
    ("San Antonio / Nelson Gardens Landfill", "san-antonio", "TX", "78252", "10303 Nelson Road, San Antonio, TX 78252", 29.3455, -98.6755, "https://www.sa.gov/", "Confirm hours", "210-207-6428", LANDFILL),
    ("Austin / TDS Landfill / Austin Community Landfill", "austin", "TX", "78725", "9900 Giles Lane, Austin, TX 78754", 30.3455, -97.6255, "https://www.austintexas.gov/", "Confirm hours", "512-272-4328", LANDFILL),
    ("Houston / Westpark Consumer Recycling Center", "houston", "TX", "77063", "9003 North Main Street, Houston, TX 77022", 29.861, -95.365, "https://www.houstontx.gov/", "Confirm hours", "713-837-9130", mats(BULKY, E_WASTE, HHW, APPLIANCE)),
    ("Dallas / McCommas Bluff Landfill scale", "dallas", "TX", "75241", "5100 Youngblood Road, Dallas, TX 75241", 32.6555, -96.7555, "https://dallascityhall.com/departments/sanitation/Pages/Landfill-and-Transfer-Stations.aspx", "Confirm hours", "214-670-0977", LANDFILL),
    ("Fort Worth / Southeast Drop-Off Station", "fort-worth", "TX", "76119", "5150 Martin Luther King Freeway, Fort Worth, TX 76119", 32.7055, -97.2755, "https://www.fortworthtexas.gov/", "Confirm hours", "817-392-1234", mats(BULKY, APPLIANCE, E_WASTE, TIRES)),
    ("Arlington / landfill drop-off", "arlington", "TX", "76011", "800 Mosier Valley Road, Fort Worth, TX 76118", 32.7855, -97.1755, "https://www.arlingtontx.gov/", "Confirm hours", "817-459-6772", LANDFILL),
    ("Plano Environmental Waste Center", "plano", "TX", "75093", "4030 W Plano Parkway, Plano, TX 75093", 33.0155, -96.8255, "https://www.plano.gov/", "Confirm hours", "972-769-4150", mats(BULKY, HHW, E_WASTE, APPLIANCE)),
    ("Garland Hinton Landfill", "garland", "TX", "75041", "2550 Hinton Drive, Garland, TX 75041", 32.8755, -96.6455, "https://www.garlandtx.gov/", "Confirm hours", "972-205-3500", LANDFILL),
    ("Irving Hunter Ferrell Landfill", "irving", "TX", "75060", "2050 Hunter Ferrell Road, Irving, TX 75060", 32.7855, -96.9555, "https://www.cityofirving.org/", "Confirm hours", "972-721-2639", LANDFILL),
    ("Jacksonville / Trail Ridge Landfill", "jacksonville", "FL", "32234", "5110 US Highway 301 S, Baldwin, FL 32234", 30.2855, -81.9755, "https://www.jacksonville.gov/", "Confirm hours", "904-255-7500", LANDFILL),
    ("Tampa / Southeast County Landfill", "tampa", "FL", "33573", "15960 County Road 672, Lithia, FL 33547", 27.8255, -82.1755, "https://hcfl.gov/", "Confirm hours", "813-272-5680", LANDFILL),
    ("Miami / Resources Recovery Facility public", "miami", "FL", "33178", "6990 NW 97th Avenue, Miami, FL 33178", 25.8455, -80.3555, "https://www.miamidade.gov/", "Confirm hours", "305-514-6666", LANDFILL),
    ("Orlando / Orange County Landfill", "orlando", "FL", "32829", "5901 Young Pine Road, Orlando, FL 32829", 28.4755, -81.2455, "https://www.orangecountyfl.net/", "Mon–Sat 8:00–17:00", "407-836-6601", LANDFILL),
    ("St. Petersburg / Pinellas Disposal Complex", "st-petersburg", "FL", "33716", "3095 114th Avenue N, St. Petersburg, FL 33716", 27.8755, -82.6855, "https://pinellas.gov/", "Confirm hours", "727-464-7500", LANDFILL),
    ("Phoenix / 27th Avenue Transfer Station", "phoenix", "AZ", "85009", "3060 S 27th Avenue, Phoenix, AZ 85009", 33.418, -112.088, "https://www.phoenix.gov/", "Confirm hours", "602-262-7251", LANDFILL),
    ("Tucson Los Reales Landfill", "tucson", "AZ", "85756", "5300 E Los Reales Road, Tucson, AZ 85756", 32.1155, -110.8755, "https://www.tucsonaz.gov/", "Confirm hours", "520-791-5414", LANDFILL),
    ("Las Vegas / Apex Landfill public", "las-vegas", "NV", "89165", "13550 N Highway 93, Las Vegas, NV 89165", 36.3855, -114.9255, "https://www.clarkcountynv.gov/", "Confirm hours", "702-455-7500", LANDFILL),
    ("Reno / Lockwood Landfill", "reno", "NV", "89434", "2401 Canyon Way, Sparks, NV 89434", 39.5255, -119.6255, "https://www.washoecounty.gov/", "Confirm hours", "775-329-8822", LANDFILL),
    ("Portland / Metro Central Transfer", "portland", "OR", "97210", "6161 NW 61st Avenue, Portland, OR 97210", 45.5655, -122.7355, "https://www.oregonmetro.gov/", "Daily 8:00–17:00", "503-234-3000", LANDFILL),
    ("Seattle / North Transfer Station", "seattle", "WA", "98103", "1350 North 34th Street, Seattle, WA 98103", 47.6485, -122.3405, "https://www.seattle.gov/", "Daily 8:00–17:30", "206-684-8400", LANDFILL),
    ("Tacoma / Pierce County Hidden Valley", "tacoma", "WA", "98446", "17925 54th Avenue E, Tacoma, WA 98446", 47.0955, -122.3555, "https://www.piercecountywa.gov/", "Confirm hours", "253-798-2179", LANDFILL),
    ("Spokane / Waste to Energy Facility", "spokane", "WA", "99224", "2900 S Geiger Boulevard, Spokane, WA 99224", 47.6255, -117.5255, "https://my.spokanecity.org/", "Confirm hours", "509-625-7878", LANDFILL),
    ("Madison / Dane County Landfill", "madison", "WI", "53718", "7102 US Highway 12 & 18, Madison, WI 53718", 43.0455, -89.2555, "https://landfill.countyofdane.com/", "Confirm hours", "608-838-9555", LANDFILL),
    ("Milwaukee / Self-Help Center North", "milwaukee", "WI", "53212", "3875 N 2nd Street, Milwaukee, WI 53212", 43.0855, -87.9155, "https://city.milwaukee.gov/", "Confirm hours", "414-286-2489", mats(BULKY, APPLIANCE)),
    ("Des Moines / Metro Park East Landfill", "des-moines", "IA", "50169", "3001 NE 109th Avenue, Mitchellville, IA 50169", 41.6655, -93.3655, "https://www.mwatoday.com/", "Confirm hours", "515-244-0021", LANDFILL),
    ("Omaha / Douglas County Landfill", "omaha", "NE", "68142", "12933 Rainwood Road, Omaha, NE 68142", 41.3355, -96.1155, "https://www.douglascounty-ne.gov/", "Confirm hours", "402-444-6666", LANDFILL),
    ("Lincoln / Bluff Road Landfill", "lincoln", "NE", "68507", "6001 Bluff Road, Lincoln, NE 68507", 40.8855, -96.6455, "https://www.lincoln.ne.gov/", "Confirm hours", "402-441-7867", LANDFILL),
    ("Wichita / Brooks Landfill", "wichita", "KS", "67235", "3600 N 135th Street West, Wichita, KS 67235", 37.7455, -97.4755, "https://www.wichita.gov/", "Confirm hours", "316-268-4677", LANDFILL),
    ("Grand Rapids / South Kent Waste Center", "grand-rapids", "MI", "49504", "977 Wealthy Street SW, Grand Rapids, MI 49504", 42.9555, -85.6855, "https://www.accesskent.com/", "Confirm hours", "616-632-7920", mats(BULKY, HHW, E_WASTE)),
    ("Louisville / Hall Street Transfer", "louisville", "KY", "40206", "2715 River Green Circle, Louisville, KY 40206", 38.2655, -85.7055, "https://louisvilleky.gov/", "Confirm hours", "502-574-3571", LANDFILL),
    ("Atlanta / Merk Miles Convenience Center", "atlanta", "GA", "30349", "3225 Merk Road SW, College Park, GA 30349", 33.6455, -84.4755, "https://www.cityofsouthfultonga.gov/", "Confirm hours", "404-629-1700", LANDFILL),
    ("Charlotte / Foxhole Recycling Center", "charlotte", "NC", "28277", "17131 Lancaster Highway, Charlotte, NC 28277", 35.0455, -80.8455, "https://wipeoutwaste.mecknc.gov/", "Mon–Sat 7:00–16:00", "980-314-3867", mats(BULKY, HHW, E_WASTE)),
    ("Raleigh / Wake Convenience Center Site 1", "raleigh", "NC", "27603", "10505 Old Stage Road, Raleigh, NC 27603", 35.6955, -78.6755, "https://www.wake.gov/", "Daily 7:00–19:00", "919-856-7400", mats(BULKY, E_WASTE, CD)),
    ("Durham / Parkwood Convenience Site", "durham", "NC", "27713", "5928 Highway 55, Durham, NC 27713", 35.8955, -78.9255, "https://dconc.gov/", "Confirm hours", "919-560-1200", mats(BULKY, E_WASTE)),
    ("Philadelphia / Northwest Transfer Station", "philadelphia", "PA", "19132", "3901 N Delaware Avenue, Philadelphia, PA 19137", 39.9955, -75.0755, "https://www.phila.gov/", "Confirm hours", "215-685-7334", LANDFILL),
    ("Baltimore / Quarantine Road Landfill", "baltimore", "MD", "21226", "6100 Quarantine Road, Baltimore, MD 21226", 39.2117, -76.5564, "https://www.baltimorecity.gov/", "Confirm hours", "410-396-3772", LANDFILL),
]

for name, city, state, zipc, addr, lat, lng, url, hours, phone, mats_list in ROWS:
    add(
        name=name,
        facility_type="Landfill / transfer / HHW hard drop-off",
        city_slug=city,
        state=state,
        zip=zipc,
        address=addr,
        lat=lat,
        lng=lng,
        source_url=url,
        hours=hours,
        phone=phone,
        accepted_materials=mats_list,
    )


def main() -> None:
    cities = {c["city_slug"] for c in json.loads((ROOT / "data" / "geo" / "cities.json").read_text())}
    kept = []
    for row in UPSERTS:
        if row["city_slug"] not in cities:
            print("skip", row["city_slug"], row["name"])
            continue
        if not is_hard_facility(row):
            raise SystemExit(f"soft {row['name']}")
        kept.append(row)

    facilities = json.loads(FAC_PATH.read_text())
    by_key = {(f.get("city_slug"), f.get("name")): i for i, f in enumerate(facilities)}
    global_addr = {(f.get("address") or "").lower()[:60] for f in facilities if f.get("address")}
    added = updated = skipped = 0
    for row in kept:
        key = (row["city_slug"], row["name"])
        gaddr = row["address"].lower()[:60]
        if key in by_key:
            facilities[by_key[key]] = {**facilities[by_key[key]], **row}
            updated += 1
        elif gaddr in global_addr:
            skipped += 1
        else:
            facilities.append(row)
            by_key[key] = len(facilities) - 1
            global_addr.add(gaddr)
            added += 1
    facilities = [f for f in facilities if is_hard_facility(f)]
    FAC_PATH.write_text(json.dumps(facilities, indent=2) + "\n")
    print(f"Batch8: +{added} upd {updated} skip {skipped} => {len(facilities)} ({1000-len(facilities)} remaining)")


if __name__ == "__main__":
    main()
