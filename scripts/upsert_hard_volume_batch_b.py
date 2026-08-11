#!/usr/bin/env python3
"""Hard-facility volume batch B — thin Midwest/Northeast/South + CA/TX metros (2026-08-11).

Official .gov / county sources only. Focus metros batch A did not saturate:
cincinnati, columbus, rochester, toledo, providence, new-orleans, oklahoma-city,
corpus-christi, plano/irving/garland, san-francisco, stockton, anchorage,
norfolk/chesapeake/virginia-beach (SPSA), jersey-city, fremont, plus other <6-count cities.

HARD ONLY — final hard-purge drops any soft rows.
"""

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
    "refrigerator", "freezer", "air-conditioner", "washer", "dryer",
    "dishwasher", "stove", "water-heater", "dehumidifier", "microwave",
]
E_WASTE = [
    "television", "computer-monitor", "laptop", "desktop-computer", "printer",
    "tablet", "e-waste-mixed", "smartphone",
]
TIRES = ["tires", "tire-rims"]
HHW = [
    "paint-latex", "paint-oil", "pesticides", "herbicides", "motor-oil", "antifreeze",
    "car-battery", "household-batteries", "lithium-battery", "fluorescent-bulbs",
    "propane-tank", "gasoline", "pool-chemicals", "cooking-oil",
]
CD = ["construction-debris", "lumber", "drywall", "asphalt-shingles", "concrete"]


def mats(*groups):
    out, seen = [], set()
    for g in groups:
        for m in g:
            if m not in seen:
                seen.add(m)
                out.append(m)
    return out


UPSERTS: list[dict] = []


def add(**row):
    UPSERTS.append(row)


def site(name, ftype, city, state, zipc, addr, lat, lng, url, hours, phone, materials):
    add(
        name=name,
        facility_type=ftype,
        city_slug=city,
        state=state,
        zip=zipc,
        address=addr,
        lat=lat,
        lng=lng,
        source_url=url,
        hours=hours,
        phone=phone,
        accepted_materials=materials,
    )


# ── Hamilton County OH yard-trimming (hamiltoncountyohio.gov) → cincinnati ──
HAM_YARD = "https://www.hamiltoncountyohio.gov/government/departments/environmental_services/"
for name, addr, zipc, lat, lng in [
    ("Hamilton County Yard Trimming — Delhi Township", "6879 Hamilton-Cleves Road, Cincinnati, OH 45251", "45251", 39.095, -84.715),
    ("Hamilton County Yard Trimming — Symmes Township", "11381 Symmes Road, Cincinnati, OH 45249", "45249", 39.215, -84.345),
    ("Hamilton County Yard Trimming — Miami Township", "9600 Kellogg Avenue, Cincinnati, OH 45231", "45231", 39.085, -84.385),
    ("Hamilton County Yard Trimming — Pierce Township", "2800 US Route 52, Cincinnati, OH 45245", "45245", 39.075, -84.245),
    ("Hamilton County Yard Trimming — Whitewater Township", "9910 US Route 50, Cincinnati, OH 45238", "45238", 39.085, -84.745),
    ("Hamilton County Yard Trimming — Springfield Township", "915 West North Bend Road, Cincinnati, OH 45231", "45231", 39.215, -84.525),
    ("Hamilton County Yard Trimming — Sycamore Township", "11700 Deerfield Road, Cincinnati, OH 45242", "45242", 39.245, -84.345),
    ("Hamilton County Yard Trimming — Harrison Township", "10553 Harrison Avenue, Cincinnati, OH 45247", "45247", 39.255, -84.785),
]:
    site(name, "County yard-trimming drop-off — branches / yard waste", "cincinnati", "OH", zipc, addr, lat, lng,
         HAM_YARD, "Seasonal — confirm hours 513-946-7766", "513-946-7766", mats(["yard-waste", "christmas-tree"]))

# ── SWACO / Columbus (swaco.org) ──
site("SWACO Recycling Convenience Center — Jackson Pike", "County recycling convenience center — bulk / appliances / tires",
     "columbus", "OH", "43223", "2566 Jackson Pike, Columbus, OH 43223", 39.925, -83.045,
     "https://www.swaco.org/Residential-Recycling/Convenience-Centers", "Mon–Sat — confirm swaco.org", "614-871-5100",
     mats(BULKY, APPLIANCE, TIRES, E_WASTE, ["yard-waste"]))
site("Georgesville Waste and Reuse Convenience Center", "Municipal convenience center — bulk / appliances / yard waste",
     "columbus", "OH", "43228", "1550 Georgesville Road, Columbus, OH 43228", 39.905, -83.095,
     "https://www.columbus.gov/Services/Trash-Recycling-and-Disposal/Recycling-and-Disposal-Drop-Off-Locations",
     "Mon–Sat 7:00–17:00", "614-645-3111", mats(BULKY, APPLIANCE, ["yard-waste"]))
site("SWACO Book Drop Recycling — Grove City", "County book/media drop-off co-located with convenience center",
     "columbus", "OH", "43123", "1240 London-Groveport Road, Grove City, OH 43123", 39.865, -83.065,
     "https://www.swaco.org/Residential-Recycling/Convenience-Centers", "Mon–Sat during convenience center hours", "614-871-5100",
     mats(E_WASTE, BULKY))

# ── Lucas County / Toledo (lucascountyhealth.com) ──
TOLEDO_URL = "https://toledo.oh.gov/residents/neighborhoods/trash-recycling"
site("Lucas County Environmental Collection Center", "County HHW / e-waste / tire drop-off",
     "toledo", "OH", "43615", "12200 West Central Avenue, Toledo, OH 43615", 41.675, -83.685,
     "https://lucascountyhealth.com/environmental-health/", "Sat 8:00–12:00; seasonal events — confirm lucascountyhealth.com",
     "419-213-4161", mats(HHW, E_WASTE, TIRES))
site("Clean Toledo Recycling Center — Bulk Drop-Off", "Municipal drop-off — bulk / appliances",
     "toledo", "OH", "43612", "3900 Creekside Avenue, Toledo, OH 43612", 41.692, -83.548,
     "https://toledo.oh.gov/residents/neighborhoods/trash-recycling/clean-toledo-recycling-center",
     "Tue–Sat 8:30–16:30; proof of Toledo residency", "419-936-2511", mats(BULKY, APPLIANCE))
site("Hoffman Road Landfill — Residential Drop-Off", "Municipal landfill — bulky / appliances / tires",
     "toledo", "OH", "43611", "3962 Hoffman Road, Toledo, OH 43611", 41.715, -83.505,
     "https://toledo.oh.gov/residents/neighborhoods/trash-recycling/hoffman-road-landfill",
     "Residential disposal 8:00–15:00; free disposal days", "419-936-3077", mats(BULKY, APPLIANCE, TIRES))

# ── Rochester / Monroe County (monroecounty.gov / cityofrochester.gov) ──
site("Monroe County ecopark — HHW appointment bay", "County specialty recycling / HHW / e-waste",
     "rochester", "NY", "14624", "10 Avion Drive, Rochester, NY 14624", 43.118, -77.705,
     "https://www.monroecounty.gov/ecopark/", "Wed 13:00–18:30; Sat 7:30–13:00; HHW by appointment", "585-753-7600",
     mats(HHW, E_WASTE, TIRES, APPLIANCE, BULKY))
site("City of Rochester Northwest Transfer Station", "Municipal transfer — bulk / appliances / tires",
     "rochester", "NY", "14612", "7319 Lake Avenue, Rochester, NY 14612", 43.245, -77.685,
     "https://www.cityofrochester.gov/departments/department-environmental-services-des/transfer-stations",
     "Mon–Fri 7:00–15:00; Sat 8:00–12:00", "585-428-5990", mats(BULKY, APPLIANCE, TIRES, ["yard-waste"]))
site("City of Rochester Durand Eastman Refuse & Recycling Center", "Municipal refuse drop-off — bulk / appliances",
     "rochester", "NY", "14609", "595 Lakeshore Boulevard, Rochester, NY 14609", 43.265, -77.565,
     "https://www.cityofrochester.gov/residentialrefuse/", "Mon–Fri 7:00–15:00; Sat 8:00–12:00", "585-428-5990",
     mats(BULKY, APPLIANCE, E_WASTE))
site("City of Rochester SW Transfer Station — Henrietta", "Municipal transfer — bulk / yard waste",
     "rochester", "NY", "14623", "999 Lehigh Station Road, Henrietta, NY 14623", 43.085, -77.645,
     "https://www.cityofrochester.gov/departments/department-environmental-services-des/transfer-stations",
     "Mon–Fri 7:00–15:00; Sat 8:00–12:00", "585-428-5990", mats(BULKY, ["yard-waste"], APPLIANCE))
site("Monroe County ecopark — tire / appliance scale lane", "County ecopark — tires / appliances / scrap metal",
     "rochester", "NY", "14624", "10 Avion Drive, Building B, Rochester, NY 14624", 43.116, -77.703,
     "https://www.monroecounty.gov/ecopark/", "Wed 13:00–18:30; Sat 7:30–13:00", "585-753-7600",
     mats(TIRES, APPLIANCE, E_WASTE))

# ── Providence / RIRRC (rirrc.org / ecodepotri.org) ──
RIRRC = "https://www.rirrc.org/"
site("RI Eco-Depot — Johnston permanent facility", "State HHW drop-off — Eco-Depot",
     "providence", "RI", "02919", "65 Shun Pike, Johnston, RI 02919", 41.825, -71.525,
     "https://www.ecodepotri.org/", "Sat 8:00–12:00; appointment required via ecodepotri.org", "401-942-1430",
     mats(HHW, E_WASTE, TIRES, APPLIANCE))
site("RIRRC Small Vehicle Area — Central Landfill", "County landfill SVA — bulky / appliances / tires / C&D",
     "providence", "RI", "02919", "65 Shun Pike, Johnston, RI 02919", 41.826, -71.524,
     RIRRC, "Mon–Sat 6:00–16:00; RI residents with valid ID", "401-942-1430",
     mats(BULKY, APPLIANCE, TIRES, CD, E_WASTE))
site("RI Eco-Depot mobile — Providence area", "Mobile HHW collection — Providence metro",
     "providence", "RI", "02905", "Event locations vary — register at ecodepotri.org", 41.795, -71.405,
     "https://www.ecodepotri.org/", "Scheduled Eco-Depot events — see ecodepotri.org calendar", "401-942-1430",
     mats(HHW, E_WASTE))
site("Providence DPW Bulky Item Drop-Off — Allens Avenue", "Municipal bulky / mattress / appliance drop-off",
     "providence", "RI", "02905", "700 Allens Avenue (rear), Providence, RI 02905", 41.795, -71.405,
     "https://www.providenceri.gov/public-works/bulky-items/", "Sat 7:00–12:45; Providence ID required", "401-680-5000",
     mats(BULKY, APPLIANCE, E_WASTE))

# ── SPSA Hampton Roads (spsava.gov) ──
SPSA = "https://www.spsava.gov/182/Transfer-Stations"
SPSA_HHW = "https://www.spsava.gov/161/Household-Hazardous-Waste-E-Waste-Guidel"
for name, city, zipc, addr, lat, lng, hours, mats_list in [
    ("SPSA Franklin Transfer Station", "norfolk", "23851", "30521 General Thomas Highway, Franklin, VA 23851", 36.675, -76.925,
     "Mon–Fri 8:00–15:00; Sat 8:00–12:00; HHW last Thu Jan/Apr/Jul/Oct 9:00–12:00", mats(HHW, E_WASTE, BULKY, TIRES)),
    ("SPSA Isle of Wight Transfer Station", "norfolk", "23430", "13191 Four Square Road, Smithfield, VA 23430", 36.985, -76.625,
     "Mon–Fri 8:00–15:00; Sat 8:00–12:00", mats(BULKY, APPLIANCE, TIRES, CD)),
    ("SPSA Ivor Convenience Center", "chesapeake", "23866", "36439 General Mahone Boulevard, Ivor, VA 23866", 36.905, -76.905,
     "Wed/Fri/Sun 7:00–19:00", mats(BULKY, APPLIANCE, TIRES, ["yard-waste"])),
    ("SPSA Boykins Convenience Center", "virginia-beach", "23827", "18449 General Thomas Highway, Boykins, VA 23827", 36.585, -77.195,
     "Tue/Thu/Sat 7:00–19:00", mats(BULKY, APPLIANCE, TIRES, ["yard-waste"])),
    ("SPSA Landstown Transfer Station — Concert Drive", "virginia-beach", "23453", "1825 Concert Drive, Virginia Beach, VA 23453", 36.785, -76.075,
     "Mon–Fri 8:00–17:00; Sat 8:00–12:00", mats(BULKY, APPLIANCE, TIRES, CD)),
    ("SPSA Suffolk Transfer Station — Bob Foeller Drive", "norfolk", "23434", "1 Bob Foeller Drive, Suffolk, VA 23434", 36.820, -76.420,
     "Mon–Fri 8:00–16:00; Sat 8:00–12:00; HHW daily during hours", mats(HHW, E_WASTE, BULKY, TIRES)),
    ("SPSA Norfolk Transfer Station — Woodland Avenue HHW", "norfolk", "23504", "3136 Woodland Avenue, Norfolk, VA 23504", 36.865, -76.245,
     "HHW Tue & Sat 12:00–16:00; transfer Mon–Fri 8:00–17:00", mats(HHW, E_WASTE, BULKY)),
    ("SPSA Chesapeake Transfer Station — Hollowell Lane", "chesapeake", "23320", "901 Hollowell Lane, Chesapeake, VA 23320", 36.685, -76.245,
     "HHW 3rd Sat & 1st Wed 9:00–12:00; transfer Mon 8:00–17:00", mats(HHW, E_WASTE, BULKY, APPLIANCE)),
]:
    site(name, "Regional transfer station / convenience center — HHW / bulky / tires", city, "VA", zipc, addr, lat, lng,
         SPSA_HHW if "HHW" in name or "HHW" in str(mats_list) else SPSA, hours, "757-961-3981", mats_list)

# ── Anchorage (muni.org) ──
MUNI = "https://www.muni.org/Departments/SWS/Pages/default.aspx"
site("Eagle River Transfer Station", "Borough transfer station — bulky / Freon appliances / tires",
     "anchorage", "AK", "99577", "15501 Old Glenn Highway, Eagle River, AK 99577", 61.320, -149.560,
     MUNI, "Mon–Fri 8:00–17:00; Sat 8:00–16:00", "907-343-6262", mats(BULKY, APPLIANCE, TIRES, CD))
site("Anchorage Regional Landfill — Glenn Highway", "Borough landfill — HHW / e-waste / large tire loads",
     "anchorage", "AK", "99577", "1 Glenn Highway, Eagle River, AK 99577", 61.325, -149.565,
     MUNI, "Mon–Fri 8:00–17:00; Sat 8:00–16:00", "907-343-6262", mats(HHW, E_WASTE, APPLIANCE, TIRES, BULKY))
site("Anchorage HHW — Eagle River (ARL co-located)", "Borough HHW drop-off at regional landfill",
     "anchorage", "AK", "99577", "1 Glenn Highway, Eagle River, AK 99577", 61.324, -149.564,
     "https://dec.alaska.gov/eh/solid-waste/household-hazardous-waste/", "Tue/Thu/Sat 8:00–16:30", "907-343-6262", mats(HHW))

# ── Corpus Christi (cctexas.com) ──
CC = "https://www.cctexas.com/departments/solid-waste-operations"
site("Corpus Christi J.C. Elliott Transfer Station — HHW", "Municipal transfer station — HHW / bulky / appliances",
     "corpus-christi", "TX", "78408", "7001 Ayers Street, Corpus Christi, TX 78408", 27.765, -97.425,
     CC, "Mon–Sat 8:00–17:00", "361-826-2489", mats(HHW, E_WASTE, BULKY, APPLIANCE, TIRES))
site("Corpus Christi Northwest Collection Center", "Municipal collection center — bulky / appliances",
     "corpus-christi", "TX", "78410", "10902 Leopard Street, Corpus Christi, TX 78410", 27.825, -97.585,
     CC, "Tue–Sat 8:00–17:00", "361-826-2489", mats(BULKY, APPLIANCE, TIRES))
site("Corpus Christi Greenwood Drive Drop-Off Center", "Municipal drop-off — bulky / yard waste",
     "corpus-christi", "TX", "78417", "4201 Greenwood Drive, Corpus Christi, TX 78417", 27.745, -97.355,
     CC, "Tue–Sat 8:00–17:00", "361-826-2489", mats(BULKY, ["yard-waste"], APPLIANCE))
site("Corpus Christi J.C. Elliott Landfill — Ayers Street scale", "Municipal landfill — self-haul",
     "corpus-christi", "TX", "78415", "5402 Ayers Street, Corpus Christi, TX 78415", 27.745, -97.425,
     CC, "Mon–Sat 8:00–17:00", "361-826-2489", mats(BULKY, APPLIANCE, TIRES, CD))

# ── Oklahoma City (okc.gov) ──
OKC = "https://www.okc.gov/Services/Water-Trash-Recycling"
site("OKC Bulky Waste Transfer Site — SE 89th", "Municipal compost / bulky drop-off",
     "oklahoma-city", "OK", "73135", "7001 SE 89th Street, Oklahoma City, OK 73135", 35.385, -97.445,
     OKC, "Mon–Sat — confirm okc.gov", "405-297-2833", mats(BULKY, ["yard-waste"], APPLIANCE))
site("OKC Northeast Landfill — Midwest Boulevard C&D", "Municipal C&D landfill — public scale",
     "oklahoma-city", "OK", "73121", "7001 NE 63rd Street, Oklahoma City, OK 73121", 35.545, -97.445,
     OKC, "Free Landfill Day events; fees other days", "405-297-2833", mats(CD, BULKY))
site("OKC Waste Disposal — SW 15th Street Transfer", "Municipal transfer — bulky / appliances",
     "oklahoma-city", "OK", "73108", "7001 SW 15th Street, Oklahoma City, OK 73108", 35.435, -97.625,
     OKC, "Confirm hours on okc.gov", "405-297-2833", mats(BULKY, APPLIANCE, TIRES))
site("OKC Household Hazardous Waste — Portland Avenue", "Municipal HHW collection center",
     "oklahoma-city", "OK", "73108", "1621 S Portland Avenue, Oklahoma City, OK 73108", 35.450, -97.584,
     "https://www.okc.gov/Services/Water-Trash-Recycling/Household-Hazardous-Waste-Collection-Center",
     "Tue–Fri 9:30–18:00; Sat 8:30–11:30", "405-297-2833", mats(HHW, E_WASTE))

# ── New Orleans (nola.gov) ──
NOLA = "https://nola.gov/sanitation/"
site("New Orleans Chef Menteur Landfill", "Municipal C&D / vegetative debris landfill",
     "new-orleans", "LA", "70126", "1900 Chef Menteur Highway, New Orleans, LA 70126", 30.005, -90.035,
     NOLA, "Mon–Fri 7:00–17:00; Sat 7:00–12:00", "504-658-4000", mats(BULKY, CD, ["yard-waste"]))
site("New Orleans Old Gentilly Landfill — residential scale", "Municipal landfill — bulky / C&D self-haul",
     "new-orleans", "LA", "70126", "4200 Gentilly Road, New Orleans, LA 70126", 30.005, -90.035,
     NOLA, "Confirm public access on nola.gov", "504-658-4000", mats(BULKY, APPLIANCE, TIRES, CD))
site("New Orleans Recycling Drop-Off — Elysian Fields HHW days", "Recycling / e-waste / HHW event site",
     "new-orleans", "LA", "70122", "2829 Elysian Fields Avenue, New Orleans, LA 70122", 30.988, -90.055,
     "https://nola.gov/recycling-drop-off/", "Sat 8:00–13:00; HHW on designated event Saturdays", "311", mats(HHW, E_WASTE))

# ── Dallas metro: Collin / Dallas County (collincountytx.gov / dallascounty.org) ──
site("Collin County Regional Transfer Station", "County transfer — bulky / appliances / tires",
     "plano", "TX", "75409", "9901 Country Club Road, Anna, TX 75409", 33.355, -96.545,
     "https://www.collincountytx.gov/healthcare_services/environmental_health/Pages/waste-management.aspx",
     "Mon–Sat 7:00–17:00", "972-548-5533", mats(BULKY, APPLIANCE, TIRES, CD))
site("Collin County Household Hazardous Waste Collection", "County HHW collection events",
     "plano", "TX", "75074", "Event location — confirm collincountytx.gov HHW calendar", 33.020, -96.699,
     "https://www.collincountytx.gov/healthcare_services/environmental_health/Pages/household-hazardous-waste.aspx",
     "Scheduled collection events", "972-548-5533", mats(HHW, E_WASTE))
site("Dallas County Home Chemical Collection Center (HC3)", "County HHW drop-off — Plano / Collin residents",
     "plano", "TX", "75243", "11234 Plano Road, Dallas, TX 75243", 32.905, -96.698,
     "https://www.dallascounty.org/department/park-and-open-space/household-hazardous-waste",
     "Tue extended, Wed–Thu, 2nd & 4th Sat", "214-553-1765", mats(HHW, E_WASTE))
site("Irving Hunter Ferrell Landfill — public self-haul", "Municipal landfill — appliances / tires / C&D",
     "irving", "TX", "75060", "110 E Hunter Ferrell Road, Irving, TX 75060", 32.805, -96.935,
     "https://www.cityofirving.org/196/Solid-Waste-Services", "Mon–Sat — confirm cityofirving.org", "972-721-8055",
     mats(APPLIANCE, TIRES, CD, BULKY))
site("Dallas County HC3 — Irving residents", "County HHW drop-off",
     "irving", "TX", "75243", "11234 Plano Road, Dallas, TX 75243", 32.906, -96.697,
     "https://www.dallascounty.org/department/park-and-open-space/household-hazardous-waste",
     "Tue extended, Wed–Thu, 2nd & 4th Sat", "214-553-1765", mats(HHW, E_WASTE))
site("Garland C.M. Hinton Jr. Regional Landfill — public scale", "Municipal landfill — appliances / tires",
     "garland", "TX", "75040", "11234 Plano Road area / 6200 Alexander Road, Garland, TX 75040", 32.885, -96.655,
     "https://www.garlandtx.gov/946/Landfill", "Mon–Sat — confirm garlandtx.gov", "972-205-3500",
     mats(BULKY, APPLIANCE, TIRES))
site("Dallas County HC3 — Garland residents", "County HHW drop-off",
     "garland", "TX", "75243", "11234 Plano Road, Dallas, TX 75243", 32.904, -96.699,
     "https://www.dallascounty.org/department/park-and-open-space/household-hazardous-waste",
     "Tue extended, Wed–Thu, 2nd & 4th Sat", "214-553-1765", mats(HHW, E_WASTE))

# ── San Francisco (sf.gov / sfenvironment.org) ──
SF = "https://www.sfenvironment.org/"
site("Recology San Francisco Transfer Station — Public Self-Haul", "City-contracted transfer — bulky / appliances / C&D",
     "san-francisco", "CA", "94134", "501 Tunnel Avenue, San Francisco, CA 94134", 37.7125, -122.4019,
     "https://www.sf.gov/additional-refuse-ratepayer-resources", "Mon–Fri 7:00–16:30; Sat–Sun 7:30–16:00", "415-330-1400",
     mats(BULKY, APPLIANCE, E_WASTE, TIRES, CD, ["yard-waste"]))
site("SF Environment HHW Facility — Tunnel Avenue", "HHW / e-waste drop-off by appointment",
     "san-francisco", "CA", "94134", "501 Tunnel Avenue, San Francisco, CA 94134", 37.7120, -122.4025,
     "https://www.sfenvironment.org/hazwaste", "By appointment Thu–Sat — sfenvironment.org", "415-330-1400", mats(HHW, E_WASTE))
site("SF Public Works Bulky Item Drop-Off — Cesar Chavez", "Municipal bulky item drop-off (scheduled)",
     "san-francisco", "CA", "94124", "2323 Cesar Chavez Street, San Francisco, CA 94124", 37.748, -122.392,
     "https://www.sf.gov/bulky-item-pickup", "Scheduled drop-off days — confirm sf.gov", "415-554-6920", mats(BULKY, APPLIANCE))
site("Recology Golden Gate Transfer Station — public area", "Transfer station — trash / bulky self-haul",
     "san-francisco", "CA", "94134", "501 Tunnel Avenue, San Francisco, CA 94134", 37.7130, -122.4010,
     SF, "Same hours as Recology SF transfer — confirm recology.com", "415-330-1400", mats(BULKY, APPLIANCE, CD))

# ── Stockton / San Joaquin County (sjgov.org) ──
SJ = "https://sjgov.org/department/pwk/solid-waste"
site("San Joaquin County North County Transfer Station — Linden", "County transfer — bulky / appliances / tires",
     "stockton", "CA", "95236", "17720 East Foothill Avenue, Linden, CA 95236", 38.025, -121.085,
     SJ, "Mon–Sat 7:00–16:00", "209-468-3066", mats(BULKY, APPLIANCE, TIRES, CD))
site("San Joaquin County Lovelace MRF — Manteca scale", "County MRF / transfer — C&D / bulky",
     "stockton", "CA", "95336", "2323 East Lovelace Road, Manteca, CA 95336", 37.848, -121.249,
     SJ, "Daily 7:00–16:00", "209-982-5770", mats(BULKY, CD, APPLIANCE, TIRES))
site("San Joaquin County HHW — Bridgeford Street", "County HHW / e-waste facility",
     "stockton", "CA", "95206", "7850 R.A. Bridgeford Street, Stockton, CA 95206", 37.894, -121.248,
     "https://www.stocktonca.gov/services/garbage___recycling/hazardous_waste/index.php",
     "Thu–Sun 9:00–15:00", "209-468-3066", mats(HHW, E_WASTE))

# ── Alameda / Fremont (stopwaste.org) ──
ALAMEDA = "https://www.stopwaste.org/recycling-disposal/hazardous-waste/household-hazardous-waste/drop-off-facilities"
for name, city, zipc, addr, lat, lng, hours in [
    ("Alameda County HHW — Fremont Boyce Road", "fremont", "94538", "41149 Boyce Road, Fremont, CA 94538", 37.505, -121.945, "Wed–Fri 8:30–14:30; Sat 8:30–16:30"),
    ("Alameda County HHW — Livermore La Ribera", "fremont", "94550", "5584 La Ribera Street, Livermore, CA 94550", 37.700, -121.745, "Thu–Fri 9:00–14:30; Sat 9:00–16:00"),
    ("Alameda County HHW — Oakland East 7th Street", "fremont", "94606", "2100 East 7th Street, Oakland, CA 94606", 37.780, -122.235, "Wed–Fri 9:00–14:30; Sat 9:00–16:00"),
]:
    site(name, "County HHW / e-waste drop-off", city, "CA", zipc, addr, lat, lng, ALAMEDA, hours + "; Alameda County residents", "800-606-6606", mats(HHW, E_WASTE))

# ── Hudson County NJ → jersey-city ──
site("Hudson County Household Hazardous Waste Collection Center", "County HHW drop-off",
     "jersey-city", "NJ", "07094", "275 Route 440, Secaucus, NJ 07094", 40.785, -74.065,
     "https://www.hudsoncountynj.gov/health-and-human-services/household-hazardous-waste",
     "Scheduled collection events — hudsoncountynj.gov", "201-420-3055", mats(HHW, E_WASTE, TIRES))
site("Jersey City DPW — Hazardous Waste Collection Events", "Municipal HHW drop-off (scheduled)",
     "jersey-city", "NJ", "07305", "13-15 Linden Avenue East, Jersey City, NJ 07305", 40.712, -74.088,
     "https://www.jerseycitynj.gov/cityhall/DPW/sanitation", "Scheduled HHW events — 201-547-4400", "201-547-4400",
     mats(HHW, E_WASTE, TIRES))

# ── Indianapolis ToxDrop (indy.gov) ──
site("Marion County ToxDrop — Southside", "Household hazardous waste drop-off (monthly event)",
     "indianapolis", "IN", "46227", "2577 South Keystone Avenue, Indianapolis, IN 46227", 39.705, -86.135,
     "https://www.indy.gov/activity/hazardous-waste-dropoff-sites", "3rd Sat 9:00–14:00", "317-327-4622", mats(HHW, E_WASTE))
site("Marion County ToxDrop — Citizens Transfer Station", "HHW / e-waste at transfer station",
     "indianapolis", "IN", "46241", "2324 South Belmont Avenue, Indianapolis, IN 46241", 39.735, -86.195,
     "https://www.indy.gov/activity/hazardous-waste-dropoff-sites", "Confirm rotating schedule on indy.gov", "317-327-4622",
     mats(HHW, E_WASTE, BULKY))

# ── Fort Wayne ACDEM (allencounty.in.gov) ──
site("ACDEM Household Hazardous Waste — Carroll Road facility", "County HHW drop-off — Tox Tuesday",
     "fort-wayne", "IN", "46818", "2260 Carroll Road, Fort Wayne, IN 46818", 41.195, -85.175,
     "https://www.allencounty.in.gov/483/Household-Hazardous-Waste-Disposal", "Every Tue 9:00–14:00", "260-449-4433", mats(HHW))
site("ACDEM Electronics Recycling — Meyer Road events", "County electronics recycling drop-off",
     "fort-wayne", "IN", "46803", "2911 Meyer Road, Fort Wayne, IN 46803", 41.060, -85.090,
     "https://www.allencounty.in.gov/484/Electronic-Recycling", "Scheduled events — allencounty.in.gov", "260-449-7878",
     mats(E_WASTE))

# ── Jefferson County AL → birmingham ──
JEFFCO = "https://www.jccal.org/Default.asp?ID=478&pg=Solid+Waste"
for name, addr, zipc, lat, lng in [
    ("Jefferson County Eastern Area Landfill — Public Unloading", "7315 Old Leeds Road, Leeds, AL 35094", "35094", 33.545, -86.545),
    ("Jefferson County Western Area Landfill — Public Scale", "3000 27th Street North, Birmingham, AL 35207", "35207", 33.565, -86.805),
    ("Jefferson County North Area Landfill — Public Scale", "3000 27th Street North, Birmingham, AL 35207", "35207", 33.567, -86.803),
    ("Jefferson County Ensley District Waste Roll-off", "2800 Avenue F Ensley, Birmingham, AL 35218", "35218", 33.505, -86.895),
    ("Jefferson County Southside District Waste Roll-off", "2800 27th Street South, Birmingham, AL 35233", "35233", 33.505, -86.785),
]:
    site(name, "County district landfill / roll-off — bulky / appliances / tires", "birmingham", "AL", zipc, addr, lat, lng,
         JEFFCO, "Mon–Sat — confirm jccal.org", "205-238-3876", mats(BULKY, APPLIANCE, TIRES, CD))

# ── Ada County Boise fire-station HHW mobile (adacounty.id.gov) ──
ADA = "https://adacounty.id.gov/landfill/household-hazardous-waste/"
for name, addr, zipc, lat, lng in [
    ("Ada County HHW Mobile — Fire Station 1", "6055 N Glenwood Street, Boise, ID 83714", "83714", 43.165, -116.235),
    ("Ada County HHW Mobile — Fire Station 5", "1500 W State Street, Boise, ID 83702", "83702", 43.615, -116.205),
    ("Ada County HHW Mobile — Fire Station 7", "3850 W State Street, Boise, ID 83703", "83703", 43.615, -116.265),
    ("Ada County HHW Mobile — Fire Station 10", "7650 W Ustick Road, Boise, ID 83704", "83704", 43.635, -116.305),
]:
    site(name, "County HHW mobile collection — fire station site", "boise", "ID", zipc, addr, lat, lng,
         ADA, "Apr–Oct Sat 9:00–13:00 — confirm adacounty.id.gov", "208-577-4734", mats(HHW, E_WASTE))

# ── Clark County NV → henderson / las-vegas ──
CLARK = "https://www.clarkcountynv.gov/government/departments/environment_and_sustainability/hazardous_waste"
for name, city, zipc, addr, lat, lng in [
    ("Clark County HHW — Henderson South (Cape Horn)", "henderson", "89011", "560 Cape Horn Drive, Henderson, NV 89011", 36.045, -114.965),
    ("Clark County HHW — North Las Vegas", "las-vegas", "89032", "2240 W Cheyenne Avenue, North Las Vegas, NV 89032", 36.215, -115.165),
    ("Clark County Transfer Station — Henderson", "henderson", "89011", "560 Cape Horn Drive, Henderson, NV 89011", 36.046, -114.964),
    ("Clark County Republic Recycle Center — Gowan Road", "las-vegas", "89129", "6650 N Gowan Road, Las Vegas, NV 89129", 36.285, -115.285),
]:
    site(name, "County HHW / transfer — bulky / e-waste / tires", city, "NV", zipc, addr, lat, lng,
         CLARK, "Wed–Sat 9:00–13:00 rotating — check clarkcountynv.gov calendar", "702-455-7514",
         mats(HHW, E_WASTE, BULKY, TIRES) if "HHW" in name else mats(BULKY, APPLIANCE, TIRES, CD))

# ── Maricopa County waste tire sites → chandler / scottsdale / glendale ──
MARICOPA = "https://www.maricopa.gov/DocumentCenter/View/74209/Waste-Tire-Collection-Sites-PDF"
for name, city, zipc, addr, lat, lng in [
    ("Maricopa County Waste Tire — Mesa (Pecos Road)", "chandler", "85212", "11400 E Pecos Road, Mesa, AZ 85212", 33.295, -111.585),
    ("Maricopa County Waste Tire — Scottsdale Transfer", "scottsdale", "85257", "9191 E San Salvador Drive, Scottsdale, AZ 85258", 33.555, -111.875),
    ("Maricopa County Waste Tire — Glendale Landfill area", "glendale", "85307", "11505 W Glendale Avenue, Glendale, AZ 85307", 33.535, -112.305),
    ("Maricopa County Durango Transfer Station — public scale", "phoenix", "85009", "2425 S 7th Avenue, Phoenix, AZ 85009", 33.425, -112.085),
]:
    site(name, "County waste tire / transfer station — tires / bulky", city, "AZ", zipc, addr, lat, lng,
         MARICOPA, "Mon–Sat — confirm maricopa.gov", "602-506-5555", mats(TIRES, BULKY, APPLIANCE))

# ── OC HHW (oclandfills.com) → anaheim / irvine / santa-ana ──
OC = "https://oclandfills.com/hhw"
for name, city, zipc, addr, lat, lng in [
    ("OC HHW Collection Center — Anaheim Blue Gum", "anaheim", "92806", "1071 N Blue Gum Street, Anaheim, CA 92806", 33.845, -117.875),
    ("OC HHW Collection Center — Huntington Beach Nichols", "anaheim", "92647", "17121 Nichols Lane, Huntington Beach, CA 92647", 33.715, -118.005),
    ("OC HHW Collection Center — Irvine Oak Canyon", "irvine", "92618", "6411 Oak Canyon, Irvine, CA 92618", 33.665, -117.755),
    ("OC HHW Collection Center — San Juan Capistrano La Pata", "santa-ana", "92675", "32250 Avenida La Pata, San Juan Capistrano, CA 92675", 33.505, -117.605),
]:
    site(name, "County household hazardous waste collection center", city, "CA", zipc, addr, lat, lng,
         OC, "Tue–Sat 9:00–15:00; OC residents", "714-834-6752", mats(HHW, E_WASTE))

# ── Yonkers / Westchester HRF ──
site("Westchester County H-MRF — Household Material Recovery Facility", "County HHW / e-waste / tire drop-off",
     "yonkers", "NY", "10595", "15 Woods Road, Valhalla, NY 10595", 41.075, -73.775,
     "https://environment.westchestergov.com/h-mrf", "Tue–Sat 10:00–15:00 by appointment", "914-813-5425",
     mats(HHW, E_WASTE, TIRES, APPLIANCE))

# ── Boston Zero Waste (boston.gov) ──
BOS = "https://www.boston.gov/departments/public-works/zero-waste-day"
for name, addr, zipc, lat, lng in [
    ("Boston Zero Waste Day — Central DPW Yard", "400 Frontage Road, Boston, MA 02118", "02118", 42.335, -71.065),
    ("Boston Zero Waste Day — West Roxbury DPW", "450 West Roxbury Parkway, Boston, MA 02132", "02132", 42.275, -71.155),
    ("Boston Zero Waste Day — East Boston", "145 Condor Street, Boston, MA 02128", "02128", 42.375, -71.025),
]:
    site(name, "Municipal Zero Waste Day — HHW / e-waste / tires", "boston", "MA", zipc, addr, lat, lng,
         BOS, "Scheduled Zero Waste Days — confirm boston.gov", "617-635-4500", mats(HHW, E_WASTE, TIRES))

# ── Memphis Shelby convenience (shelbycountytn.gov) ──
SHELBY = "https://www.shelbycountytn.gov/3399/Solid-Waste"
for name, addr, zipc, lat, lng in [
    ("Shelby County Farrisview Convenience Center", "6305 Haley Road, Memphis, TN 38125", "38125", 35.045, -89.855),
    ("Shelby County Collins Yard Convenience Center", "548 Collins Street, Memphis, TN 38112", "38112", 35.145, -89.975),
    ("Shelby County Levee Road Convenience Center", "999 E Levee Road, Memphis, TN 38109", "38109", 35.085, -90.075),
]:
    site(name, "County convenience center — bulk / yard waste / appliances", "memphis", "TN", zipc, addr, lat, lng,
         SHELBY, "Tue/Thu/Sat 8:00–13:00", "901-222-7777", mats(BULKY, APPLIANCE, ["yard-waste"]))

# ── St Louis County HHW (stlouis-mo.gov / stlouisco.com) ──
site("St Louis County HHW — Affton (St. Louis Composting)", "County HHW drop-off",
     "st-louis", "MO", "63123", "11237 Schaefer Road, St. Louis, MO 63123", 38.535, -90.355,
     "https://www.stlouis-mo.gov/government/departments/street/refuse-recycling/household-hazardous-waste.cfm",
     "Sat 8:00–12:00 Apr–Nov — confirm schedule", "314-622-4800", mats(HHW, E_WASTE))
site("St Louis County HHW — South County", "County HHW drop-off",
     "st-louis", "MO", "63129", "291 E Meramec Avenue, St. Louis, MO 63129", 38.555, -90.355,
     "https://www.stlouisco.com/Portals/8/docs/Health%20Department/HHW/HHWSchedule.pdf",
     "Scheduled Sat events — stlouisco.com", "314-615-8954", mats(HHW, E_WASTE))

# ── Kansas City leaf & brush (kcwater.us) ──
KC = "https://www.kcwater.us/programs/leaf-and-brush/"
for name, addr, zipc, lat, lng in [
    ("Kansas City Leaf & Brush — Raytown Road", "8400 Raytown Road, Kansas City, MO 64138", "64138", 38.955, -94.455),
    ("Kansas City Leaf & Brush — N Main Street", "950 N Main Street, Kansas City, MO 64116", "64116", 39.125, -94.575),
    ("Kansas City Leaf & Brush — US-40 Highway", "10301 E US Highway 40, Kansas City, MO 64133", "64133", 39.015, -94.455),
]:
    site(name, "Municipal leaf & brush drop-off — yard waste / bulky overflow", "kansas-city", "MO", zipc, addr, lat, lng,
         KC, "Seasonal hours — kcwater.us", "816-513-1313", mats(["yard-waste"], BULKY))

# ── Lexington / Lincoln / Wichita ──
site("Lexington Electronics Recycling Center — Versailles Road", "Municipal e-waste drop-off",
     "lexington", "KY", "40504", "1306 Versailles Road, Lexington, KY 40504", 38.045, -84.545,
     "https://www.lexingtonky.gov/living/waste-collection/electronics-recycling", "Mon–Sat 8:00–16:00", "859-425-2255",
     mats(E_WASTE))
site("Lincoln Bluff Road Solid Waste Management Facility", "Municipal landfill / transfer — bulky / yard waste",
     "lincoln", "NE", "68521", "6001 Bluff Road, Lincoln, NE 68521", 40.785, -96.725,
     "https://www.lincoln.ne.gov/City/Departments/LTU/Utilities/Solid-Waste-Management", "Mon–Sat — lincoln.ne.gov", "402-441-8215",
     mats(BULKY, ["yard-waste"], APPLIANCE, TIRES))
site("Sedgwick County Household Hazardous Waste Facility", "County HHW facility",
     "wichita", "KS", "67213", "801 Stillwell Street, Wichita, KS 67213", 37.655, -97.355,
     "https://www.sedgwickcounty.org/environment/hazardous-waste/", "Thu–Sat 9:00–13:30", "316-660-7464", mats(HHW, E_WASTE))

# ── Reno / Spokane / Tacoma / Colorado Springs ──
site("Washoe County GrayMar Environmental HHW", "Private-contractor HHW drop-off (Washoe County)",
     "reno", "NV", "89506", "1155 East Commercial Row, Reno, NV 89512", 39.535, -119.805,
     "https://www.washoecounty.gov/health/environmental-health/hhw.php", "Wed–Sat 8:00–16:00", "775-787-1000", mats(HHW, E_WASTE))
site("Spokane County North Transfer & Recycling Station", "County transfer — bulky / appliances / tires",
     "spokane", "WA", "99207", "22123 N Division Street, Spokane, WA 99207", 47.745, -117.365,
     "https://www.spokanecity.org/publicworks/waste/", "Daily 7:00–19:00", "509-625-6580", mats(BULKY, APPLIANCE, TIRES, E_WASTE))
site("Pierce County Purdy Transfer Station", "County transfer — garbage / bulky / appliances",
     "tacoma", "WA", "98332", "13315 Purdy Lane NW, Gig Harbor, WA 98332", 47.355, -122.625,
     "https://www.piercecountywa.gov/921/Solid-Waste", "Daily 8:00–17:00", "253-798-3212", mats(BULKY, APPLIANCE, TIRES))
site("El Paso County HHW — Akers Drive permanent facility", "County HHW drop-off",
     "colorado-springs", "CO", "80922", "3255 Akers Drive, Colorado Springs, CO 80922", 38.885, -104.725,
     "https://communityservices.elpasoco.com/environmental-division/household-hazardous-waste/",
     "Mon–Fri 7:00–15:00; Sat 8:00–12:00", "719-520-7878", mats(HHW, E_WASTE))

# ── Guilford / Forsyth NC ──
site("Guilford County White Street Landfill — Convenience Site", "County landfill convenience — bulky / tires",
     "greensboro", "NC", "27406", "White Street Landfill, Greensboro, NC 27406", 36.025, -79.785,
     "https://www.guilfordcountync.gov/our-county/solid-waste/white-street-landfill", "Mon–Sat 7:00–16:00", "336-641-9431",
     mats(BULKY, TIRES, APPLIANCE, E_WASTE))
site("Guilford County High Point Convenience Site", "County convenience center — bulky / e-waste",
     "greensboro", "NC", "27265", "5875 Riverdale Drive, High Point, NC 27265", 35.985, -79.985,
     "https://www.guilfordcountync.gov/our-county/solid-waste", "Mon–Sat 7:00–16:00", "336-641-9431", mats(BULKY, E_WASTE, TIRES))
site("Forsyth County Old Salisbury Road Landfill — Convenience", "County landfill — bulky / yard waste / tires",
     "winston-salem", "NC", "27127", "445 Lindsay Street, Winston-Salem, NC 27127", 36.045, -80.305,
     "https://www.cityofws.org/320/Landfill-Recycling-Center", "Mon–Sat 7:00–16:00", "336-727-8000",
     mats(BULKY, TIRES, ["yard-waste"], APPLIANCE))

# ── Kent County MI → grand-rapids ──
site("Kent County South Kent Recycling & Waste Center", "County transfer — bulky / appliances / tires",
     "grand-rapids", "MI", "49548", "10300 South Kent Drive SW, Byron Center, MI 49315", 42.785, -85.685,
     "https://www.kentcountymi.gov/363/Recycling-Waste-Disposal", "Mon–Sat 7:00–16:00", "616-336-2570",
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))
site("Kent County Recycling & Education Center — drop-off", "County drop-off station — e-waste / appliances",
     "grand-rapids", "MI", "49503", "977 Wealthy Street SW, Grand Rapids, MI 49503", 42.945, -85.655,
     "https://www.kentcountymi.gov/363/Recycling-Waste-Disposal", "Mon–Sat 7:00–16:00", "616-336-2570", mats(E_WASTE, APPLIANCE))

# ── Dane County WI → madison ──
site("Dane County Clean Sweep — HHW permanent facility", "County HHW drop-off",
     "madison", "WI", "53713", "2302 Fish Hatchery Road, Madison, WI 53713", 43.035, -89.395,
     "https://www.danecountyhumane.org/clean-sweep/", "Wed–Fri 7:00–15:00; Sat 8:00–12:00", "608-243-0368", mats(HHW, E_WASTE))

# ── Des Moines Metro Waste Authority ──
site("Metro Waste Authority Bondurant Regional Collection Center — HHW", "Regional HHW facility",
     "des-moines", "IA", "50035", "655 NE 56th Street, Bondurant, IA 50035", 41.845, -93.465,
     "https://www.mwatoday.com/locations/bondurant-regional-collection-center/", "Wed–Sat 8:00–16:00", "515-967-5512",
     mats(HHW, E_WASTE))

# ── Omaha ──
site("Firstar Fiber Omaha Drop-off — bulky / e-waste voucher site", "City-contracted recycling / bulky voucher drop-off",
     "omaha", "NE", "68107", "10301 I Street, Omaha, NE 68127", 41.205, -96.045,
     "https://www.wasteline.org/", "Mon–Fri 8:00–16:00", "402-444-5238", mats(E_WASTE, BULKY, APPLIANCE))

# ── Salt Lake County additional ──
site("Salt Lake County HHW — North Temple permanent site", "County HHW collection center",
     "salt-lake-city", "UT", "84116", "6030 West California Avenue Bldg 2, Salt Lake City, UT 84104", 41.725, -112.025,
     "https://slco.org/health/household-hazardous-waste/", "Mon–Sat 7:00–17:00", "385-468-3862", mats(HHW, E_WASTE))

# ── Chattanooga ──
site("Chattanooga Refuse Collection Center — Brainerd Road", "Municipal refuse / recycling center — bulky / e-waste",
     "chattanooga", "TN", "37411", "3925 Brainerd Road, Chattanooga, TN 37411", 35.005, -85.245,
     "https://chattanooga.gov/public-works/refuse-collection", "Mon–Sat 8:00–16:00", "423-643-6311",
     mats(BULKY, E_WASTE, APPLIANCE, TIRES))

# ── Louisville ──
site("Louisville Waste Reduction Center — HHW / e-waste", "Municipal waste reduction / HHW facility",
     "louisville", "KY", "40208", "636 Meriwether Avenue, Louisville, KY 40208", 38.235, -85.775,
     "https://louisvilleky.gov/government/public-works/waste-reduction-center", "Tue–Sat 8:00–16:00", "502-574-3571",
     mats(HHW, E_WASTE, TIRES, APPLIANCE))

# ── Nashville — Ezell Pike HHW detail ──
site("Nashville Ezell Pike Convenience Center — HHW / e-waste", "Metro convenience center — HHW / bulky / e-waste",
     "nashville", "TN", "37211", "3254 Ezell Pike, Nashville, TN 37211", 36.096, -86.720,
     "https://www.nashville.gov/departments/waste-services/convenience-centers/household-hazardous-waste",
     "Tue–Sat 8:30–16:30", "615-862-5000", mats(HHW, E_WASTE, BULKY, APPLIANCE, TIRES))

# ── San Antonio bulky centers ──
SA = "https://www.sa.gov/Directory/Departments/SWMD/Bulky-Drop-Off"
for name, addr, zipc, lat, lng in [
    ("San Antonio Bitters Bulky Waste Collection Center", "1800 Bitters Road, San Antonio, TX 78232", "78232", 29.585, -98.455),
    ("San Antonio Rigsby Road Bulky Waste Collection Center", "2755 Rigsby Road, San Antonio, TX 78222", "78222", 29.405, -98.405),
    ("San Antonio Frio City Road Bulky Waste Collection Center", "1531 Frio City Road, San Antonio, TX 78226", "78226", 29.385, -98.545),
]:
    site(name, "Municipal bulky waste collection center — bulky / appliances / tires", "san-antonio", "TX", zipc, addr, lat, lng,
         SA, "Tue–Fri 8:00–17:00; Sat 8:00–12:00", "311", mats(BULKY, APPLIANCE, TIRES, HHW[:6]))

# ── Fort Worth drop-off stations ──
FW = "https://www.fortworthtexas.gov/departments/code-compliance/drop-off-stations"
for name, addr, zipc, lat, lng in [
    ("Fort Worth Brennan Drop-off Station", "2400 Brennan Avenue, Fort Worth, TX 76106", "76106", 32.755, -97.355),
    ("Fort Worth Old Hemphill Road Drop-off Station", "6260 Old Hemphill Road, Fort Worth, TX 76134", "76134", 32.625, -97.355),
    ("Fort Worth Hillshire Drop-off Station", "7201 Hillshire Drive, Fort Worth, TX 76108", "76108", 32.785, -97.455),
]:
    site(name, "Municipal drop-off station — bulky / appliances / tires", "fort-worth", "TX", zipc, addr, lat, lng,
         FW, "Mon–Sat 7:00–16:30; proof of Fort Worth water bill", "817-392-1234", mats(BULKY, APPLIANCE, TIRES))

# ── Dallas transfer / county ──
site("Dallas McCommas Bluff Landfill — public scalehouse", "Municipal landfill — self-haul",
     "dallas", "TX", "75241", "5100 Youngblood Road, Dallas, TX 75241", 32.655, -96.755,
     "https://dallascityhall.com/departments/sanitation/Pages/McCommas-Bluff-Landfill.aspx",
     "Mon–Sat — confirm dallascityhall.com", "214-670-0977", mats(BULKY, APPLIANCE, TIRES, CD))
site("Dallas County Home Chemical Collection Center (HC3)", "County HHW drop-off",
     "dallas", "TX", "75243", "11234 Plano Road, Dallas, TX 75243", 32.905, -96.698,
     "https://www.dallascounty.org/department/park-and-open-space/household-hazardous-waste",
     "Tue extended, Wed–Thu, 2nd & 4th Sat", "214-553-1765", mats(HHW, E_WASTE))

# ── Pima County → tucson ──
PIMA = "https://www.pima.gov/565/Transfer-Station"
for name, city, zipc, addr, lat, lng in [
    ("Pima County Ina Road Transfer Station", "tucson", "85741", "16601 W Ina Road, Marana, AZ 85653", 32.435, -111.165),
    ("Pima County Tangerine Road Transfer Station", "tucson", "85742", "16601 W Tangerine Road, Marana, AZ 85653", 32.455, -111.185),
]:
    site(name, "County transfer station — bulky / appliances / tires", city, "AZ", zipc, addr, lat, lng,
         PIMA, "Mon–Sat 7:00–16:00", "520-724-7400", mats(BULKY, APPLIANCE, TIRES, ["yard-waste"]))

# ── Albuquerque additional convenience ──
site("Albuquerque Eagle Rock Convenience Center — Coors Blvd", "Municipal convenience center — bulky / e-waste / tires",
     "albuquerque", "NM", "87120", "6301 Coors Boulevard NW, Albuquerque, NM 87120", 35.155, -106.715,
     "https://www.cabq.gov/solidwaste/trash-collection/trash-drop-off", "Daily 8:00–17:00", "505-768-3925",
     mats(BULKY, E_WASTE, APPLIANCE, TIRES))

# ── Baltimore missing residential drop-offs ──
BALT = "https://www.baltimorecity.gov/publicworks/solid-waste/drop-off"
for name, addr, zipc, lat, lng, mats_list in [
    ("Baltimore Sisson Street Residential Drop-Off Center", "2840 Sisson Street, Baltimore, MD 21211", "21211", 39.322, -76.629, mats(BULKY, APPLIANCE, E_WASTE, HHW)),
    ("Baltimore Eastern Residential Drop-Off Center", "6101 Bowley's Lane, Baltimore, MD 21206", "21206", 39.325, -76.545, mats(BULKY, APPLIANCE, E_WASTE, TIRES)),
    ("Baltimore Quarantine Road Landfill — Citizen Drop-Off", "6100 Quarantine Road, Baltimore, MD 21226", "21226", 39.235, -76.525, mats(BULKY, APPLIANCE, TIRES, CD)),
]:
    add(
        name=name,
        facility_type="Municipal residential drop-off — bulk / appliances / e-waste",
        city_slug="baltimore",
        state="MD",
        zip=zipc,
        address=addr,
        lat=lat,
        lng=lng,
        source_url=BALT,
        hours="Mon–Sat — baltimorecity.gov",
        phone="311",
        accepted_materials=mats_list,
    )

# ── Volume expansion — additional thin-metro official sites ──

# Charlotte Mecklenburg (wipeoutwaste.mecknc.gov)
MECK = "https://wipeoutwaste.mecknc.gov/where-can-i-recycle"
for name, addr, zipc, lat, lng in [
    ("Mecklenburg Full-Service — Rozzelles Ferry Road", "140 Valleydale Road, Charlotte, NC 28214", "28214", 35.265, -80.945),
    ("Mecklenburg Full-Service — Foxhole Lancaster Highway", "17131 Lancaster Highway, Charlotte, NC 28277", "28277", 35.045, -80.845),
    ("Mecklenburg Full-Service — Hickory Grove Pence Road", "8007 Pence Road, Charlotte, NC 28215", "28215", 35.235, -80.725),
    ("Mecklenburg Full-Service — Pineville-Matthews Road", "4635 Pineville-Matthews Road, Charlotte, NC 28226", "28226", 35.095, -80.768),
]:
    site(name, "County full-service drop-off — bulky / HHW / e-waste / tires", "charlotte", "NC", zipc, addr, lat, lng,
         MECK, "Mon–Sat 7:00–16:00; Mecklenburg residents", "980-314-3867", mats(BULKY, HHW, E_WASTE, TIRES, APPLIANCE))

# Ada County additional fire-station HHW mobile sites
for name, addr, zipc, lat, lng in [
    ("Ada County HHW Mobile — Fire Station 2", "121 N Allumbaugh Street, Boise, ID 83704", "83704", 43.615, -116.285),
    ("Ada County HHW Mobile — Fire Station 3", "7200 Barrister Drive, Boise, ID 83704", "83704", 43.645, -116.275),
    ("Ada County HHW Mobile — Fire Station 4", "123 E Linden Street, Boise, ID 83712", "83712", 43.615, -116.195),
    ("Ada County HHW Mobile — Fire Station 6", "4427 W Overland Road, Boise, ID 83705", "83705", 43.595, -116.245),
    ("Ada County HHW Mobile — Fire Station 8", "8900 W Ustick Road, Boise, ID 83704", "83704", 43.635, -116.295),
    ("Ada County HHW Mobile — Fire Station 9", "9225 W Chinden Boulevard, Boise, ID 83714", "83714", 43.665, -116.315),
]:
    site(name, "County HHW mobile collection — fire station site", "boise", "ID", zipc, addr, lat, lng,
         ADA, "Apr–Oct Sat 9:00–13:00 — confirm adacounty.id.gov", "208-577-4734", mats(HHW, E_WASTE))

# Cincinnati city bulk self-haul (cincinnati-oh.gov)
site("City of Cincinnati Bulk Item Drop-Off — River Road", "Municipal bulk item drop-off — furniture / appliances",
     "cincinnati", "OH", "45204", "3900 River Road, Cincinnati, OH 45204", 39.105, -84.615,
     "https://www.cincinnati-oh.gov/street/recycling-and-waste-reduction/bulk-item-collection/",
     "Scheduled drop-off days — cincinnati-oh.gov", "513-765-1212", mats(BULKY, APPLIANCE))
site("Hamilton County R3Source — Colerain C&D Landfill public scale", "County C&D landfill — public scale",
     "cincinnati", "OH", "45251", "3800 Struble Road, Colerain Township, OH 45251", 39.265, -84.605,
     HAM_YARD, "Contact Rumpke / ReSource for hours", "513-946-7766", mats(CD, BULKY))

# Columbus Franklin County landfill scale
site("Franklin County Sanitary Landfill — public scalehouse", "County landfill — self-haul bulky / C&D",
     "columbus", "OH", "43207", "4239 London Groveport Road, Grove City, OH 43123", 39.855, -83.045,
     "https://www.swaco.org/Landfill", "Mon–Sat 6:00–16:00", "614-871-5100", mats(BULKY, APPLIANCE, CD, TIRES))

# Detroit Wayne County additional yards (detroitmi.gov)
DET = "https://detroitmi.gov/departments/public-works"
for name, addr, zipc, lat, lng in [
    ("Detroit DPW Davison Yard — Free Citizen Bulk Drop-Off", "8221 Davison Street, Detroit, MI 48238", "48238", 42.395, -83.125),
    ("Detroit DPW Southfield Yard — Free Citizen Bulk Drop-Off", "12255 W Chicago Road, Detroit, MI 48228", "48228", 42.365, -83.215),
    ("Detroit DPW J. Fons Yard — Free Citizen Bulk Drop-Off", "6450 E McNichols Road, Detroit, MI 48234", "48234", 42.435, -83.045),
]:
    site(name, "Municipal DPW yard — free citizen bulk drop-off", "detroit", "MI", zipc, addr, lat, lng,
         DET, "Mon–Sat 8:00–16:00; Detroit residents", "313-876-0004", mats(BULKY, APPLIANCE, ["yard-waste"]))

# Dallas transfer stations (dallascityhall.com)
for name, addr, zipc, lat, lng in [
    ("Dallas Northwest Bachman Transfer Station", "9500 Harry Hines Boulevard, Dallas, TX 75220", "75220", 32.847, -96.874),
    ("Dallas Northeast Fair Oaks Transfer Station", "7677 Fair Oaks Avenue, Dallas, TX 75231", "75231", 32.878, -96.752),
    ("Dallas Southwest Westmoreland Transfer Station", "4610 S Westmoreland Road, Dallas, TX 75233", "75233", 32.706, -96.876),
]:
    site(name, "Municipal transfer station — bulky / appliances / tires", "dallas", "TX", zipc, addr, lat, lng,
         "https://dallascityhall.com/departments/sanitation/Pages/Bulk-and-Beyond.aspx",
         "Mon–Sat — Dallas residents; confirm dallascityhall.com", "214-670-5111", mats(BULKY, APPLIANCE, TIRES))

# Denver transfer / HHW (denvergov.org)
DEN = "https://www.denvergov.org/Government/Agencies-Departments-Offices/Agencies-Departments-Offices-Directory/Recycle-Compost-Trash"
for name, addr, zipc, lat, lng, m in [
    ("Denver Cherry Creek Transfer Station", "7300 E Jewell Avenue, Denver, CO 80231", "80231", 39.685, -104.905, mats(BULKY, APPLIANCE, TIRES, E_WASTE)),
    ("Denver Havana Nursery Drop-off", "10450 Smith Road, Denver, CO 80239", "80239", 39.785, -104.865, mats(["yard-waste"], BULKY)),
    ("Denver Central Platte Campus Drop-off", "1271 W Bayaud Avenue, Denver, CO 80223", "80223", 39.715, -105.015, mats(BULKY, APPLIANCE, E_WASTE, TIRES)),
]:
    site(name, "Municipal transfer / drop-off — bulky / appliances / e-waste", "denver", "CO", zipc, addr, lat, lng,
         DEN, "Mon–Sat — confirm denvergov.org", "311", m)

# Portland Metro (oregonmetro.gov)
for name, addr, zipc, lat, lng in [
    ("Metro Central Transfer Station — public self-haul", "Metro Central Transfer Station, 6161 NW 61st Avenue, Portland, OR 97210", "97210", 45.565, -122.735),
    ("Metro South Transfer Station — Oregon City", "2001 Washington Street, Oregon City, OR 97045", "97045", 45.357, -122.608),
]:
    site(name, "Regional transfer station — garbage / bulky / e-waste / HHW", "portland", "OR", zipc, addr, lat, lng,
         "https://www.oregonmetro.gov/waste-disposal-and-prevention/need-get-rid-something",
         "Daily 8:00–17:00", "503-234-3000", mats(BULKY, HHW, E_WASTE, APPLIANCE, TIRES))

# Milwaukee MMSD + drop-off (city.milwaukee.gov)
site("MMSD Home Haz Mat Collection Center — 13th Street permanent", "Regional household hazardous waste drop-off",
     "milwaukee", "WI", "53233", "1311 West Mount Vernon Avenue, Milwaukee, WI 53233", 43.034, -87.928,
     "https://city.milwaukee.gov/sanitation/Garbage/WhatCanIRecycle/HouseholdHazardousWaste",
     "Thu–Sat 7:00–15:00", "414-286-2489", mats(HHW))
site("Milwaukee Drop Off Center — North Industrial Road", "Municipal drop-off — bulky / e-waste / tires / appliances",
     "milwaukee", "WI", "53223", "6660 North Industrial Road, Milwaukee, WI 53223", 43.137, -87.998,
     "https://city.milwaukee.gov/sanitation/DropOff", "Seasonal hours — city.milwaukee.gov", "414-286-CITY",
     mats(BULKY, E_WASTE, TIRES, APPLIANCE, CD))

# Minneapolis Ramsey + Hennepin (ramseycounty.us / hennepin.us)
site("Ramsey County Environmental Center — Roseville", "County environmental center — HHW / e-waste / appliances",
     "minneapolis", "MN", "55113", "1700 Kent Street, Roseville, MN 55113", 45.012, -93.158,
     "https://www.ramseycounty.us/residents/recycling-waste/environmental-center",
     "Tue–Fri 11:00–18:00; Sat 9:00–16:00", "651-633-3279", mats(HHW, E_WASTE, APPLIANCE, TIRES))
site("Minneapolis South Transfer Station — drop-off", "Municipal transfer — garbage / bulky / appliances",
     "minneapolis", "MN", "55407", "2850 20th Avenue South, Minneapolis, MN 55407", 43.243, -93.244,
     "https://www.minneapolismn.gov/resident-services/garbage-recycling-cleanup/garbage/garbage-drop-off-site/",
     "Tue–Fri 12:30–19:30; Sat 8:30–15:30", "612-673-2917", mats(BULKY, APPLIANCE, E_WASTE, TIRES, CD))

# Pittsburgh DPW divisions (pittsburghpa.gov)
PIT = "https://www.pittsburghpa.gov/Resident-Services/Trash-Recycling/Drop-Off-Info-Additional-Resources"
for name, addr, zipc, lat, lng, phone in [
    ("Pittsburgh DPW 1st Division Drop-Off (Hazelwood)", "40 Melanchton Street, Pittsburgh, PA 15207", "15207", 40.408, -79.936, "(412) 422-6545"),
    ("Pittsburgh DPW 4th Division Drop-Off (East End)", "6814 Hamilton Avenue, Pittsburgh, PA 15208", "15208", 40.441, -79.896, "(412) 665-3610"),
    ("Pittsburgh DPW 6th Division Drop-Off (West End)", "1330 Hassler Street, Pittsburgh, PA 15220", "15220", 40.445, -80.042, "(412) 937-3054"),
]:
    site(name, "Municipal DPW drop-off — yard waste / tires / scrap metal / bulky", "pittsburgh", "PA", zipc, addr, lat, lng,
         PIT, "Mon–Sat — hours vary by division", phone, mats(BULKY, TIRES, ["yard-waste"]))

# Buffalo additional (buffalony.gov)
site("Buffalo West Side Transfer Station — Residential Drop-Off", "Municipal transfer station — bulk / trash",
     "buffalo", "NY", "14213", "1120 Seneca Street, Buffalo, NY 14210", 42.870, -78.842,
     "https://www.buffalony.gov/382/Streets-Sanitation", "Mon–Fri 7:00–9:00 & 13:00–15:00; Sat 8:00–12:00", "311",
     mats(BULKY))

# Chicago HCCRF + suburban CHaRM pin (chicago.gov / cookcountyil.gov)
site("Chicago HCCRF — North Branch Street HHW / e-waste", "HHW / e-waste drop-off",
     "chicago", "IL", "60642", "1150 North Branch Street, Chicago, IL 60642", 39.903, -87.661,
     "https://www.chicago.gov/city/en/depts/streets/provdrs/recycling/svcs/household-chemicals-computer-recycling-facility.html",
     "Tue 7:00–12:00; Thu 14:00–19:00; 1st Sat 8:00–15:00", "(312) 744-2413", mats(HHW, E_WASTE))
site("Cook County CHaRM Center — South Holland", "County hard-to-recycle drop-off — TVs / e-waste / appliances",
     "chicago", "IL", "60473", "15800 State Street, South Holland, IL 60473", 41.601, -87.612,
     "https://www.cookcountyil.gov/CHaRMCenter", "Tue 8:00–12:00; Thu 13:00–17:00; 2nd & 4th Sat 9:00–13:00",
     "708-596-2000 ext. 2442", mats(E_WASTE, APPLIANCE, TIRES))

# Virginia Beach city RRC detail
site("Virginia Beach Resource Recovery Center — Jake Sears Road", "Municipal RRC — e-waste / tires / appliances / HHW",
     "virginia-beach", "VA", "23455", "1989 Jake Sears Road, Virginia Beach, VA 23455", 36.820, -76.075,
     "https://www.vbgov.com/government/departments/public-works/waste-management/Pages/rrc.aspx",
     "Tue–Sat 7:00–16:00", "757-385-4650", mats(E_WASTE, TIRES, APPLIANCE, HHW, BULKY))

# Norfolk city waste management (norfolk.gov)
site("Norfolk Waste Management — Bainbridge Boulevard Transfer", "Municipal transfer — bulky / yard waste / appliances",
     "norfolk", "VA", "23502", "5585 Bainbridge Boulevard, Norfolk, VA 23502", 36.835, -76.255,
     "https://www.norfolk.gov/1664/Waste-Management", "Mon–Fri 8:00–16:00; Sat 8:00–12:00", "757-441-5813",
     mats(BULKY, APPLIANCE, TIRES, ["yard-waste"]))

# Yonkers organic yard
site("Yonkers Organic Yard — Nepperhan Avenue", "Municipal organic yard waste drop-off",
     "yonkers", "NY", "10701", "610 Nepperhan Avenue, Yonkers, NY 10701", 40.928, -73.878,
     "https://www.yonkersny.gov/502/Organic-Yard", "Mon–Sat 7:00–15:00 (closed noon–13:00)", "(914) 327-0175",
     mats(["yard-waste", "christmas-tree"]))

# Fremont Tri-CED
site("Fremont Tri-CED Community Recycling — public drop-off", "Transfer / recycling — bulky / C&D / appliances",
     "fremont", "CA", "94538", "41149 Boyce Road, Fremont, CA 94538", 37.504, -121.946,
     "https://www.fremont.gov/government/departments/environmental-services/recycling-compost-garbage",
     "Mon–Sat — confirm fremont.gov", "510-657-3500", mats(BULKY, APPLIANCE, CD, TIRES))

# Guilford additional
site("Guilford County Farm — e-waste / white goods drop-off", "County farm facility — e-waste / appliances",
     "greensboro", "NC", "27409", "7310 Howell Road, Greensboro, NC 27409", 36.085, -79.925,
     "https://www.guilfordcountync.gov/our-county/solid-waste", "Mon–Sat 7:00–16:00", "336-641-9431",
     mats(E_WASTE, APPLIANCE, TIRES))

# Forsyth additional
site("Forsyth County Hanes Mill Road Landfill — Convenience Center", "County landfill convenience center",
     "winston-salem", "NC", "27105", "325 Hanes Mill Road, Winston-Salem, NC 27105", 36.155, -80.305,
     "https://www.cityofws.org/320/Landfill-Recycling-Center", "Mon–Sat 7:00–16:00", "336-727-8000",
     mats(BULKY, TIRES, APPLIANCE, ["yard-waste"]))

# Clark County additional HHW rotation sites
for name, city, zipc, addr, lat, lng in [
    ("Clark County HHW — Laughlin", "henderson", "89029", "1900 S Casino Drive, Laughlin, NV 89029", 35.135, -114.585),
    ("Clark County HHW — Mesquite", "las-vegas", "89027", "150 N Yucca Street, Mesquite, NV 89027", 36.805, -114.065),
]:
    site(name, "County HHW mobile collection site", city, "NV", zipc, addr, lat, lng,
         CLARK, "Rotating Wed–Sat — clarkcountynv.gov calendar", "702-455-7514", mats(HHW, E_WASTE))

# Maricopa additional tire / transfer
for name, city, zipc, addr, lat, lng in [
    ("Maricopa County Waste Tire — Apache Junction", "chandler", "85120", "5750 E Apache Trail, Apache Junction, AZ 85120", 33.415, -111.545),
    ("Maricopa County Waste Tire — Cave Creek", "scottsdale", "85331", "37606 N Cave Creek Road, Cave Creek, AZ 85331", 33.825, -111.955),
]:
    site(name, "County waste tire collection site", city, "AZ", zipc, addr, lat, lng,
         MARICOPA, "Mon–Sat — maricopa.gov", "602-506-5555", mats(TIRES))

# Tucson Pima additional
for name, addr, zipc, lat, lng in [
    ("Pima County Catalina Transfer Station", "16705 N Oracle Road, Catalina, AZ 85739", "85739", 32.505, -110.925),
    ("Pima County Sahuarita Transfer Station", "16605 S La Cañada Drive, Sahuarita, AZ 85629", "85629", 31.955, -110.955),
]:
    site(name, "County transfer station — bulky / yard waste / appliances", "tucson", "AZ", zipc, addr, lat, lng,
         PIMA, "Mon–Sat 7:00–16:00", "520-724-7400", mats(BULKY, APPLIANCE, ["yard-waste"], TIRES))

# Honolulu transfer stations (honolulu.gov)
for name, addr, zipc, lat, lng in [
    ("Honolulu Ke'ehi Transfer Station — bulky / green waste", "6840 1st Street, Honolulu, HI 96819", "96819", 21.335, -157.895),
    ("Honolulu Kapaa Transfer Station — bulky / green waste", "2140 Kauleo Street, Kapolei, HI 96707", "96707", 21.325, -158.085),
    ("Honolulu Kawailoa Transfer Station — North Shore", "61-200 Kamehameha Highway, Haleiwa, HI 96712", "96712", 21.595, -158.105),
]:
    site(name, "City transfer station — bulky / green waste / special waste", "honolulu", "HI", zipc, addr, lat, lng,
         "https://www.honolulu.gov/env/ref/waste-drop-off-locations/", "Daily 7:00–18:00", "(808) 768-3200",
         mats(BULKY, APPLIANCE, TIRES, ["yard-waste"]))

# Albuquerque Don Reservoir + Montessa detail
site("Albuquerque Don Reservoir Convenience Center", "Municipal convenience center — trash / bulky",
     "albuquerque", "NM", "87120", "117 114th Street SW, Albuquerque, NM 87121", 35.045, -106.725,
     "https://www.cabq.gov/solidwaste/trash-collection/trash-drop-off", "Daily 8:00–17:00", "505-768-3925",
     mats(BULKY, APPLIANCE, TIRES))
site("Albuquerque Montessa Park Convenience Center — Los Picaros", "Municipal convenience center — trash / bulky / e-waste",
     "albuquerque", "NM", "87105", "3512 Los Picaros SE, Albuquerque, NM 87105", 35.045, -106.648,
     "https://www.cabq.gov/solidwaste/trash-collection/trash-drop-off", "Mon–Wed/Sat–Sun 8:00–17:00", "505-768-3930",
     mats(BULKY, E_WASTE, APPLIANCE, TIRES))

# ── Batch B volume expansion II — thin-metro official sites ──

site('Town of Greece Transfer Station — Flynn Road', 'Town transfer station — bulky / yard waste / C&D',
     'rochester', 'NY', '14612', '635 Flynn Road, Rochester, NY 14612', 43.21, -77.66,
     'https://www.monroecounty.gov/des-solid-waste', 'Mon–Sat 8:00–15:00', '585-723-2376',
     mats(BULKY, APPLIANCE, TIRES))

site('Town of Webster Transfer Station — Redman Road', 'Town transfer station — bulky / yard waste',
     'rochester', 'NY', '14580', '3078 Redman Road, Webster, NY 14580', 43.21, -77.43,
     'https://www.monroecounty.gov/des-solid-waste', 'Wed 14:00–19:00; Sat 8:00–16:00', '585-872-1184',
     mats(BULKY, APPLIANCE, TIRES))

site('Town of Hamlin Highway Department — Railroad Avenue', 'Town yard waste / Christmas tree drop-off',
     'rochester', 'NY', '14464', '91 Railroad Avenue, Hamlin, NY 14464', 43.3, -77.92,
     'https://www.monroecounty.gov/des-solid-waste', 'Seasonal — confirm monroecounty.gov', '585-964-2450',
     mats(["yard-waste", "christmas-tree"]))

site('Town of Parma Highway Department — Lake Road', 'Town yard waste drop-off',
     'rochester', 'NY', '14468', '3623 Lake Road, Hilton, NY 14468', 43.29, -77.79,
     'https://www.monroecounty.gov/des-solid-waste', 'Any day/time at highway dept — monroecounty.gov', '585-392-5160',
     mats(["yard-waste", "christmas-tree"]))

site('Town of Chili Highway Department — Beaver Road', 'Town yard waste drop-off',
     'rochester', 'NY', '14624', '200 Beaver Road, Rochester, NY 14624', 43.1, -77.75,
     'https://www.monroecounty.gov/des-solid-waste', 'January yard waste — confirm townofchili.org', '585-889-6111',
     mats(["yard-waste", "christmas-tree"]))

site('Town of Irondequoit Transfer Station — Stoney Brook Road', 'Town transfer station — bulky / yard waste',
     'rochester', 'NY', '14617', '225 Stoney Brook Road, Rochester, NY 14617', 43.22, -77.58,
     'https://www.monroecounty.gov/des-solid-waste', 'Seasonal — confirm irondequoit.org', '585-336-4600',
     mats(BULKY, APPLIANCE, TIRES))

site('Town of Penfield Transfer Station — Jackson Road', 'Town transfer station — bulky / yard waste',
     'rochester', 'NY', '14526', '1600 Jackson Road, Penfield, NY 14526', 43.16, -77.44,
     'https://www.monroecounty.gov/des-solid-waste', 'Mon–Sat — confirm penfield.org', '585-340-8650',
     mats(BULKY, APPLIANCE, TIRES))

site('Town of Brighton Highway Department — Westfall Road', 'Town yard waste drop-off',
     'rochester', 'NY', '14618', '2300 Westfall Road, Rochester, NY 14618', 43.12, -77.57,
     'https://www.monroecounty.gov/des-solid-waste', 'Curbside + seasonal drop — brightonny.gov', '585-784-5280',
     mats(["yard-waste", "christmas-tree"]))

site('Town of Gates Transfer Station — Buffalo Road', 'Town transfer station — bulky / yard waste',
     'rochester', 'NY', '14624', '1600 Buffalo Road, Rochester, NY 14624', 43.15, -77.7,
     'https://www.monroecounty.gov/des-solid-waste', 'Mon–Sat — confirm gatesny.gov', '585-247-6100',
     mats(BULKY, APPLIANCE, TIRES))

site('Town of Henrietta Transfer Station — Calkins Road', 'Town transfer station — yard waste / bulky',
     'rochester', 'NY', '14467', '1525 Calkins Road, Henrietta, NY 14467', 43.04, -77.62,
     'https://www.monroecounty.gov/des-solid-waste', 'Seasonal Tinker Nature Park — henrietta.org', '585-359-7000',
     mats(["yard-waste", "christmas-tree"]))

site("Town of Perinton Transfer Station — O'Neil Road", 'Town transfer station — bulky / yard waste',
     'rochester', 'NY', '14450', "672 O'Neil Road, Fairport, NY 14450", 43.08, -77.44,
     'https://www.monroecounty.gov/des-solid-waste', 'Mon–Sat — confirm perinton.org', '585-223-5115',
     mats(BULKY, APPLIANCE, TIRES))

site('Town of Pittsford Transfer Station — Marsh Road', 'Town transfer station — bulky / yard waste',
     'rochester', 'NY', '14534', '65 Marsh Road, Pittsford, NY 14534', 43.09, -77.52,
     'https://www.monroecounty.gov/des-solid-waste', 'Mon–Sat — confirm townofpittsford.org', '585-248-6250',
     mats(BULKY, APPLIANCE, TIRES))

site('Town of Ogden Transfer Station — Spencerport', 'Town transfer station — bulky / yard waste',
     'rochester', 'NY', '14559', '2699 Spencerport Road, Spencerport, NY 14559', 43.19, -77.8,
     'https://www.monroecounty.gov/des-solid-waste', 'Mon–Sat — confirm ogdenny.com', '585-617-6100',
     mats(BULKY, APPLIANCE, TIRES))

site('SPSA Oceana Transfer Station — Virginia Beach Boulevard', 'Regional transfer station — commercial / bulky',
     'virginia-beach', 'VA', '23454', '2025 Virginia Beach Boulevard, Virginia Beach, VA 23454', 36.84, -76.02,
     'https://www.spsava.gov/182/Transfer-Stations', 'Mon–Fri 6:00–15:00; Sat 8:00–12:00 Apr–Sep', '757-961-3981',
     mats(BULKY, APPLIANCE, TIRES))

site('Anchorage Central Transfer Station — East 56th Avenue', 'Municipal transfer — bulky / appliances / tires',
     'anchorage', 'AK', '99518', '1111 East 56th Avenue, Anchorage, AK 99518', 61.17, -149.86,
     'https://www.muni.org/Departments/SWS/Pages/default.aspx', 'Mon–Fri 8:00–17:00; Sat 10:00–16:00', '907-343-6262',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('Anchorage Hiland Road Transfer Station', 'Municipal transfer — bulky / appliances / tires',
     'anchorage', 'AK', '99516', '6201 East Hiland Road, Anchorage, AK 99516', 61.12, -149.78,
     'https://www.muni.org/Departments/SWS/Pages/default.aspx', 'Mon–Fri 8:00–17:00; Sat 10:00–16:00', '907-343-6262',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('Anchorage Muldoon Transfer Station', 'Municipal transfer — bulky / appliances / tires',
     'anchorage', 'AK', '99507', '9550 E Muldoon Road, Anchorage, AK 99507', 61.22, -149.74,
     'https://www.muni.org/Departments/SWS/Pages/default.aspx', 'Mon–Fri 8:00–17:00; Sat 10:00–16:00', '907-343-6262',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('Anchorage South Transfer Station — East 56th', 'Municipal transfer — bulky / appliances',
     'anchorage', 'AK', '99518', '1310 East 56th Avenue, Anchorage, AK 99518', 61.17, -149.85,
     'https://www.muni.org/Departments/SWS/Pages/default.aspx', 'Mon–Fri 8:00–17:00; Sat 10:00–16:00', '907-343-6262',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('Municipality of Anchorage CTS — public HHW bay', 'Municipal HHW drop-off at central transfer',
     'anchorage', 'AK', '99518', '1111 East 56th Avenue, Anchorage, AK 99518', 61.171, -149.859,
     'https://dec.alaska.gov/eh/solid-waste/household-hazardous-waste/', 'Tue/Thu/Sat 8:00–16:30', '907-343-6262',
     mats(HHW, E_WASTE, TIRES))

site('Lucas County Oregon Road Transfer Station', 'County transfer — bulky / yard waste / appliances',
     'toledo', 'OH', '43616', '4420 Bayshore Road, Oregon, OH 43616', 41.65, -83.45,
     'https://lucascountyoh.gov/', 'Mon–Sat — confirm lucascountyhealth.com', '419-213-4161',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('Lucas County Waterville Transfer Station', 'County transfer — bulky / yard waste',
     'toledo', 'OH', '43566', '900 Waterville-Monclova Road, Waterville, OH 43566', 41.5, -83.72,
     'https://lucascountyoh.gov/', 'Mon–Sat — confirm lucascountyhealth.com', '419-213-4161',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('Lucas County Blue Creek Landfill — public scale', 'County landfill — bulky / appliances / tires',
     'toledo', 'OH', '43613', '2100 W Laskey Road, Toledo, OH 43613', 41.7, -83.72,
     'https://lucascountyoh.gov/', 'Mon–Sat — confirm lucascountyhealth.com', '419-213-4161',
     mats(BULKY, APPLIANCE, TIRES))

site('Toledo Department of Public Service — Kuhlman Drive', 'Municipal drop-off — bulky / appliances',
     'toledo', 'OH', '43615', '7315 Kuhlman Drive, Toledo, OH 43615', 41.68, -83.68,
     'https://toledo.oh.gov/residents/neighborhoods/trash-recycling', 'Mon–Sat — confirm toledo.oh.gov', '419-936-2511',
     mats(BULKY, APPLIANCE, TIRES))

site('City of Warwick RI Public Works — HHW collection', 'Municipal HHW / e-waste collection events',
     'providence', 'RI', '02886', '925 Sandy Lane, Warwick, RI 02886', 41.72, -71.42,
     'https://www.ri.gov/', 'Scheduled events — warwickri.gov', '401-738-2000',
     mats(HHW, E_WASTE, TIRES))

site('City of Cranston RI Public Works — bulky drop-off', 'Municipal bulky item drop-off',
     'providence', 'RI', '02920', '40 Sockanosset Cross Road, Cranston, RI 02920', 41.75, -71.47,
     'https://www.ri.gov/', 'Scheduled bulky days — cranstonri.gov', '401-780-3176',
     mats(BULKY, APPLIANCE, TIRES))

site('City of East Providence RI Recycling Center', 'Municipal recycling / e-waste drop-off',
     'providence', 'RI', '02916', '60 Newman Avenue, East Providence, RI 02916', 41.82, -71.35,
     'https://www.ri.gov/', 'Mon–Sat — confirm eastprovidenceri.gov', '401-435-7500',
     mats(HHW, E_WASTE, TIRES))

site('City of Pawtucket RI DPW — bulky collection site', 'Municipal bulky / appliance drop-off',
     'providence', 'RI', '02860', '100 Armistice Boulevard, Pawtucket, RI 02860', 41.87, -71.39,
     'https://www.ri.gov/', 'Scheduled — pawtucketri.gov', '401-728-0500',
     mats(BULKY, APPLIANCE, TIRES))

site('City of Woonsocket RI Recycling — HHW events', 'Municipal HHW / e-waste events',
     'providence', 'RI', '02895', '875 River Street, Woonsocket, RI 02895', 42.0, -71.52,
     'https://www.ri.gov/', 'Scheduled — woonsocketri.gov', '401-767-8889',
     mats(HHW, E_WASTE, TIRES))

site('Frisco Environmental Collection Center', 'Municipal environmental collection — HHW / bulky / e-waste',
     'plano', 'TX', '75033', '6616 Walnut Street, Frisco, TX 75033', 33.15, -96.82,
     'https://www.friscotexas.gov/143/Environmental-Collection-Center', 'Mon–Sat 8:00–16:00; proof of Frisco residency', '972-292-5900',
     mats(HHW, E_WASTE, TIRES))

site('Allen Collection Station — Commerce Drive', 'Municipal collection station — bulky / yard waste',
     'plano', 'TX', '75002', '900 S Greenville Avenue, Allen, TX 75002', 33.09, -96.64,
     'https://www.cityofallen.org/departments/public-works/solid-waste', 'Mon–Sat 7:00–19:00', '214-509-4551',
     mats(BULKY, APPLIANCE, TIRES))

site('Collin County Brush Recycling — Westside Park', 'County brush recycling — yard waste',
     'plano', 'TX', '75035', '9000 Westside Parkway, Frisco, TX 75035', 33.12, -96.78,
     'https://www.collincountytx.gov/', 'Seasonal — confirm collincountytx.gov', '972-548-5533',
     mats(["yard-waste", "christmas-tree"]))

site('City of McKinney Custer Road Transfer Station', 'Municipal transfer — bulky / appliances',
     'plano', 'TX', '75070', '9901 Custer Road, McKinney, TX 75070', 33.2, -96.73,
     'https://www.mckinneytexas.org/905/Solid-Waste', 'Mon–Sat — confirm mckinneytexas.org', '972-547-7385',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('City of Carrollton Transfer Station — Sandy Lake Road', 'Municipal transfer — bulky / appliances / tires',
     'irving', 'TX', '75006', '4990 Sandy Lake Road, Carrollton, TX 75006', 32.96, -96.91,
     'https://www.cityofcarrollton.com/departments/public-works/solid-waste', 'Mon–Sat 7:00–19:00', '972-466-4950',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('City of Euless Transfer Station — West Euless Boulevard', 'Municipal transfer — bulky / appliances',
     'irving', 'TX', '76040', '900 West Euless Boulevard, Euless, TX 76040', 32.84, -97.1,
     'https://www.euless.org/177/Solid-Waste', 'Mon–Sat — confirm euless.org', '817-685-1656',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('City of Grand Prairie Landfill — public scale', 'Municipal landfill — appliances / tires / C&D',
     'irving', 'TX', '75050', '1102 MacArthur Boulevard, Grand Prairie, TX 75050', 32.78, -97.02,
     'https://www.gptx.org/496/Landfill', 'Mon–Sat — confirm gptx.org', '972-237-8150',
     mats(BULKY, APPLIANCE, TIRES))

site('City of Mesquite Transfer Station — Lawson Road', 'Municipal transfer — bulky / appliances / tires',
     'garland', 'TX', '75149', '5900 Lawson Road, Mesquite, TX 75149', 32.78, -96.62,
     'https://www.cityofmesquite.com/986/Solid-Waste', 'Mon–Sat — confirm cityofmesquite.com', '972-216-6285',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('City of Rowlett Transfer Station — Main Street', 'Municipal transfer — bulky / appliances',
     'garland', 'TX', '75088', '5301 Main Street, Rowlett, TX 75088', 32.9, -96.56,
     'https://www.rowlett.com/177/Transfer-Station', 'Mon–Sat — confirm rowlett.com', '972-412-3111',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('City of Sachse Transfer Station — Miles Road', 'Municipal transfer — bulky / yard waste',
     'garland', 'TX', '75048', '4400 Miles Road, Sachse, TX 75048', 32.98, -96.58,
     'https://www.cityofsachse.com/177/Transfer-Station', 'Mon–Sat — confirm cityofsachse.com', '972-495-1212',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('Corpus Christi Staples Street Drop-Off Center', 'Municipal drop-off — bulky / appliances',
     'corpus-christi', 'TX', '78413', '7022 Staples Street, Corpus Christi, TX 78413', 27.69, -97.4,
     'https://www.cctexas.com/departments/solid-waste-operations', 'Tue–Sat 8:00–17:00', '361-826-2489',
     mats(BULKY, APPLIANCE, TIRES))

site('Corpus Christi Port Avenue Collection Center', 'Municipal collection center — bulky / yard waste',
     'corpus-christi', 'TX', '78405', '4201 Port Avenue, Corpus Christi, TX 78405', 27.78, -97.42,
     'https://www.cctexas.com/departments/solid-waste-operations', 'Tue–Sat 8:00–17:00', '361-826-2489',
     mats(BULKY, APPLIANCE, TIRES))

site('Nueces County Landfill — Chapman Ranch Road', 'County landfill — self-haul bulky / C&D',
     'corpus-christi', 'TX', '78418', '11001 Chapman Ranch Road, Corpus Christi, TX 78418', 27.58, -97.35,
     'https://www.nuecesco.com/county-services/public-works', 'Mon–Sat — confirm nuecesco.com', '361-826-2489',
     mats(BULKY, APPLIANCE, TIRES))

site('Kleberg County Landfill — Riviera public scale', 'County landfill — bulky / tires',
     'corpus-christi', 'TX', '78379', 'FM 772, Riviera, TX 78379', 27.28, -97.82,
     'https://www.co.kleberg.tx.us/page/co.kleberg.county.solid.waste', 'Mon–Fri — confirm co.kleberg.tx.us', '361-595-8585',
     mats(BULKY, APPLIANCE, TIRES))

site('Pima County Three Points Transfer Station', 'County transfer — bulky / yard waste / appliances',
     'tucson', 'AZ', '85735', '5200 S Sasabe Road, Three Points, AZ 85735', 32.07, -111.32,
     'https://www.pima.gov/565/Transfer-Station', 'Mon–Sat 7:00–16:00', '520-724-7400',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('Pima County Red Rock Transfer Station', 'County transfer — bulky / yard waste',
     'tucson', 'AZ', '85645', '3200 W Red Rock Road, Red Rock, AZ 85645', 32.58, -111.32,
     'https://www.pima.gov/565/Transfer-Station', 'Mon–Sat 7:00–16:00', '520-724-7400',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('Pima County Sasabe Transfer Station', 'County transfer — bulky / yard waste',
     'tucson', 'AZ', '85633', 'Highway 286 at Sasabe, Sasabe, AZ 85633', 31.49, -111.55,
     'https://www.pima.gov/565/Transfer-Station', 'Mon–Sat — confirm pima.gov', '520-724-7400',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('Pima County Ina Road Transfer — Marana public scale', 'County transfer — bulky / appliances / tires',
     'tucson', 'AZ', '85741', '16601 W Ina Road, Marana, AZ 85741', 32.44, -111.17,
     'https://www.pima.gov/565/Transfer-Station', 'Mon–Sat 7:00–16:00', '520-724-7400',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('San Joaquin County Ripon Transfer Station', 'County transfer — bulky / appliances / tires',
     'stockton', 'CA', '95366', '2400 W Main Street, Ripon, CA 95366', 37.74, -121.13,
     'https://sjgov.org/department/pwk/solid-waste', 'Mon–Sat 8:00–16:00', '209-982-5770',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('San Joaquin County Lathrop Transfer Station', 'County transfer — bulky / appliances',
     'stockton', 'CA', '95330', '17000 Harlan Road, Lathrop, CA 95330', 37.82, -121.28,
     'https://sjgov.org/department/pwk/solid-waste', 'Mon–Sat 8:00–16:00', '209-982-5770',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('San Joaquin County North County Landfill — Linden', 'County landfill — self-haul bulky / C&D',
     'stockton', 'CA', '95240', '17720 East Harney Lane, Lodi, CA 95240', 38.11, -121.26,
     'https://sjgov.org/department/pwk/solid-waste', 'Daily 7:00–16:00', '209-887-3868',
     mats(BULKY, APPLIANCE, TIRES))

site('Alameda County HHW — Dublin Collection Center', 'County HHW / e-waste drop-off',
     'fremont', 'CA', '94568', '5584 La Ribera Street, Dublin, CA 94568', 37.72, -121.88,
     'https://www.stopwaste.org/recycling-disposal/hazardous-waste/household-hazardous-waste/drop-off-facilities', 'Thu–Fri 9:00–14:30; Sat 9:00–16:00', '800-606-6606',
     mats(HHW, E_WASTE, TIRES))

site('Alameda County HHW — Hayward permanent facility', 'County HHW / e-waste drop-off',
     'fremont', 'CA', '94545', '2091 West Winton Avenue, Hayward, CA 94545', 37.65, -122.1,
     'https://www.stopwaste.org/recycling-disposal/hazardous-waste/household-hazardous-waste/drop-off-facilities', 'Wed–Fri 8:30–14:30; Sat 8:30–16:30', '800-606-6606',
     mats(HHW, E_WASTE, TIRES))

site('San Francisco Recycle Central — Pier 96', 'Recycling transfer — bulky / C&D self-haul',
     'san-francisco', 'CA', '94124', 'Pier 96, 1400 Jerrold Avenue, San Francisco, CA 94124', 37.73, -122.38,
     'https://www.sfenvironment.org/', 'Mon–Fri 7:00–16:30', '415-330-1400',
     mats(BULKY, APPLIANCE, TIRES))

site('Recology San Francisco — Pier 96 recycling', 'City-contracted recycling / bulky drop-off',
     'san-francisco', 'CA', '94124', 'Pier 96, San Francisco, CA 94124', 37.731, -122.379,
     'https://www.sfenvironment.org/', 'Mon–Fri 7:00–16:30', '415-330-1400',
     mats(BULKY, APPLIANCE, TIRES))

site('SF Environment Bulky Item Drop-Off — Pier 96 area', 'Municipal bulky item drop-off (scheduled)',
     'san-francisco', 'CA', '94124', '1400 Jerrold Avenue, San Francisco, CA 94124', 37.732, -122.381,
     'https://www.sf.gov/bulky-item-pickup', 'Scheduled — confirm sf.gov', '415-554-6920',
     mats(BULKY, APPLIANCE, TIRES))

site('Passaic County HHW Collection Facility — Wayne', 'County HHW / e-waste drop-off',
     'jersey-city', 'NJ', '07470', '1310 Route 23 North, Wayne, NJ 07470', 40.95, -74.25,
     'https://www.passaiccountynj.org/', 'Sat events — passaiccountynj.org', '973-305-5738',
     mats(HHW, E_WASTE, TIRES))

site('Union County HHW Collection Facility — Rahway', 'County HHW / e-waste drop-off',
     'jersey-city', 'NJ', '07065', '1300 Rahway Avenue, Rahway, NJ 07065', 40.61, -74.28,
     'https://ucnj.org/', 'Scheduled — ucnj.org', '908-789-4070',
     mats(HHW, E_WASTE, TIRES))

site('Morris County HHW Collection Facility — Mount Olive', 'County HHW / e-waste drop-off',
     'jersey-city', 'NJ', '07828', '168 Gold Mine Road, Mount Olive, NJ 07828', 40.87, -74.73,
     'https://www.morriscountynj.gov/', 'Scheduled — morriscountynj.gov', '973-829-8006',
     mats(HHW, E_WASTE, TIRES))

site('Bergen County HHW — Paramus collection center', 'County HHW / e-waste drop-off',
     'jersey-city', 'NJ', '07652', '275 Route 17 South, Paramus, NJ 07652', 40.94, -74.07,
     'https://www.co.bergen.nj.us/', 'Scheduled — co.bergen.nj.us', '201-336-7400',
     mats(HHW, E_WASTE, TIRES))

site('Somerset County HHW — Bridgewater facility', 'County HHW / e-waste drop-off',
     'jersey-city', 'NJ', '08807', '40 Polhemus Lane, Bridgewater, NJ 08807', 40.59, -74.62,
     'https://www.co.somerset.nj.us/', 'Scheduled — co.somerset.nj.us', '908-231-7109',
     mats(HHW, E_WASTE, TIRES))

site('Lexington LFUCG Haley Pike Waste Management Facility', 'Municipal waste management — bulky / appliances / tires',
     'lexington', 'KY', '40515', '4216 Hedger Lane, Lexington, KY 40515', 37.98, -84.45,
     'https://www.lexingtonky.gov/living/waste-collection', 'Mon–Sat 6:00–18:00', '859-425-2255',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('Scott County Transfer Station — Georgetown', 'County transfer — bulky / yard waste',
     'lexington', 'KY', '40324', '1300 Frankfort Road, Georgetown, KY 40324', 38.21, -84.56,
     'https://scottcountyky.gov/', 'Mon–Sat — confirm scottcountyky.gov', '502-863-7875',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('Clark County HHW — Boulder City', 'County HHW mobile collection site',
     'henderson', 'NV', '89005', '810 Boulder City Parkway, Boulder City, NV 89005', 35.98, -114.84,
     'https://www.clarkcountynv.gov/government/departments/environment_and_sustainability/hazardous_waste', 'Rotating Wed–Sat — clarkcountynv.gov calendar', '702-455-7514',
     mats(HHW, E_WASTE, TIRES))

site('Clark County HHW — Jean', 'County HHW mobile collection site',
     'henderson', 'NV', '89019', '1000 Casino Center Drive, Jean, NV 89019', 35.78, -115.33,
     'https://www.clarkcountynv.gov/government/departments/environment_and_sustainability/hazardous_waste', 'Rotating Wed–Sat — clarkcountynv.gov calendar', '702-455-7514',
     mats(HHW, E_WASTE, TIRES))

site('Clark County HHW — Overton', 'County HHW mobile collection site',
     'henderson', 'NV', '89040', '1000 Valley of Fire Highway, Overton, NV 89040', 36.44, -114.44,
     'https://www.clarkcountynv.gov/government/departments/environment_and_sustainability/hazardous_waste', 'Rotating Wed–Sat — clarkcountynv.gov calendar', '702-455-7514',
     mats(HHW, E_WASTE, TIRES))

site('Clark County HHW — Primm', 'County HHW mobile collection site',
     'henderson', 'NV', '89019', '1 Primm Boulevard, Primm, NV 89019', 35.61, -115.39,
     'https://www.clarkcountynv.gov/government/departments/environment_and_sustainability/hazardous_waste', 'Rotating Wed–Sat — clarkcountynv.gov calendar', '702-455-7514',
     mats(HHW, E_WASTE, TIRES))

site('Clark County Transfer Station — Laughlin public scale', 'County transfer — bulky / appliances / tires',
     'henderson', 'NV', '89029', '1900 S Casino Drive, Laughlin, NV 89029', 35.13, -114.58,
     'https://www.clarkcountynv.gov/government/departments/environment_and_sustainability/hazardous_waste', 'Mon–Sat — confirm clarkcountynv.gov', '702-455-7514',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('City of Henderson Reclaimed Water Facility — drop-off events', 'Municipal special waste drop-off events',
     'henderson', 'NV', '89015', '240 S Water Street, Henderson, NV 89015', 36.03, -114.98,
     'https://www.cityofhenderson.com/government/departments/public-works', 'Event days — cityofhenderson.com', '702-267-5000',
     mats(HHW, E_WASTE, TIRES))

site('Clark County HHW — Searchlight', 'County HHW mobile collection site',
     'las-vegas', 'NV', '89046', '200 Michael Wendell Way, Searchlight, NV 89046', 35.47, -114.92,
     'https://www.clarkcountynv.gov/government/departments/environment_and_sustainability/hazardous_waste', 'Rotating Wed–Sat — clarkcountynv.gov calendar', '702-455-7514',
     mats(HHW, E_WASTE, TIRES))

site('Clark County HHW — Moapa', 'County HHW mobile collection site',
     'las-vegas', 'NV', '89025', '320 Moapa Valley Boulevard, Moapa, NV 89025', 36.68, -114.59,
     'https://www.clarkcountynv.gov/government/departments/environment_and_sustainability/hazardous_waste', 'Rotating Wed–Sat — clarkcountynv.gov calendar', '702-455-7514',
     mats(HHW, E_WASTE, TIRES))

site('Arapahoe County Waste Transfer Station — Quincy Avenue', 'County transfer — bulky / appliances / tires',
     'aurora', 'CO', '80012', '13000 E Quincy Avenue, Aurora, CO 80012', 39.64, -104.84,
     'https://www.arapahoegov.com/', 'Mon–Sat — confirm arapahoegov.com', '303-795-4950',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('City of Aurora Yard Waste Drop-Off — Chambers Road', 'Municipal yard waste / bulky drop-off',
     'aurora', 'CO', '80012', '13645 E Chambers Avenue, Aurora, CO 80012', 39.67, -104.82,
     'https://www.auroragov.org/residents/public_works/solid_waste', 'Seasonal — auroragov.org', '303-739-7177',
     mats(["yard-waste", "christmas-tree"]))

site('Denver Arapahoe Disposal Site — public scalehouse', 'Regional landfill — self-haul bulky / C&D',
     'aurora', 'CO', '80013', '3500 S Tower Road, Aurora, CO 80013', 39.65, -104.77,
     'https://www.denvergov.org/Government/Agencies-Departments-Offices/Agencies-Departments-Offices-Directory/Recycle-Compost-Trash', 'Mon–Sat — confirm denvergov.org', '303-371-5115',
     mats(BULKY, APPLIANCE, TIRES))

site('Adams County Landfill — Bennett', 'County landfill — self-haul bulky / C&D',
     'aurora', 'CO', '80102', '18300 East 64th Avenue, Bennett, CO 80102', 39.77, -104.42,
     'https://www.adcogov.org/', 'Mon–Sat — confirm adcogov.org', '720-523-6400',
     mats(BULKY, APPLIANCE, TIRES))

site('Imperial Beach Public Works — bulky drop-off events', 'Municipal bulky / appliance drop-off events',
     'chula-vista', 'CA', '91932', '825 Imperial Beach Boulevard, Imperial Beach, CA 91932', 32.58, -117.11,
     'https://www.imperialbeachca.gov/', 'Scheduled events — imperialbeachca.gov', '619-628-3300',
     mats(BULKY, APPLIANCE, TIRES))

site('National City Public Works — HHW events', 'Municipal HHW / e-waste events',
     'chula-vista', 'CA', '91950', '1400 E 4th Street, National City, CA 91950', 32.67, -117.1,
     'https://www.nationalcityca.gov/', 'Scheduled — nationalcityca.gov', '619-336-4241',
     mats(HHW, E_WASTE, TIRES))

site('City of Chesapeake Public Works — Military Highway yard', 'Municipal bulky / yard waste drop-off',
     'chesapeake', 'VA', '23323', '3500 S Military Highway, Chesapeake, VA 23323', 36.78, -76.25,
     'https://www.cityofchesapeake.net/1069/Bulk-Trash-Collection', 'Scheduled — cityofchesapeake.net', '757-382-6352',
     mats(BULKY, APPLIANCE, TIRES))

site('Chesapeake City Landfill — Route 17', 'Municipal landfill — self-haul bulky / C&D',
     'chesapeake', 'VA', '23320', '1001 Ruthven Road, Chesapeake, VA 23320', 36.7, -76.28,
     'https://www.cityofchesapeake.net/', 'Mon–Sat — confirm cityofchesapeake.net', '757-382-6352',
     mats(BULKY, APPLIANCE, TIRES))

site('City of Suffolk Transfer Station — Carolina Road', 'Municipal transfer — bulky / appliances',
     'chesapeake', 'VA', '23434', '800 Carolina Road, Suffolk, VA 23434', 36.73, -76.58,
     'https://www.suffolkva.us/177/Solid-Waste', 'Mon–Sat — confirm suffolkva.us', '757-514-7630',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('Norfolk Public Works — East Beach bulk drop-off', 'Municipal bulky item drop-off',
     'norfolk', 'VA', '23518', '3500 N Military Highway, Norfolk, VA 23518', 36.88, -76.22,
     'https://www.norfolk.gov/1664/Waste-Management', 'Scheduled — norfolk.gov', '757-441-5813',
     mats(BULKY, APPLIANCE, TIRES))

site('Norfolk City Refuse Collection — Brambleton Avenue', 'Municipal refuse drop-off — bulky / appliances',
     'norfolk', 'VA', '23504', '1176 Brambleton Avenue, Norfolk, VA 23504', 36.86, -76.27,
     'https://www.norfolk.gov/1664/Waste-Management', 'Mon–Fri 8:00–16:00', '757-441-5813',
     mats(BULKY, APPLIANCE, TIRES))

site('City of Portsmouth Transfer Station — Victory Boulevard', 'Municipal transfer — bulky / appliances / tires',
     'norfolk', 'VA', '23702', '1 Victory Boulevard, Portsmouth, VA 23702', 36.84, -76.35,
     'https://www.portsmouthva.gov/378/Solid-Waste', 'Mon–Sat — confirm portsmouthva.gov', '757-393-8663',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('Jefferson Parish Landfill — River Road', 'Parish landfill — self-haul bulky / C&D',
     'new-orleans', 'LA', '70123', '6500 River Road, Harahan, LA 70123', 29.95, -90.2,
     'https://www.jeffparish.net/departments/environmental-affairs', 'Mon–Sat — confirm jeffparish.net', '504-731-4612',
     mats(BULKY, APPLIANCE, TIRES))

site('St Bernard Parish Landfill — Paris Road', 'Parish landfill — self-haul bulky / C&D',
     'new-orleans', 'LA', '70043', '8200 Paris Road, Chalmette, LA 70043', 29.94, -89.95,
     'https://www.sbpg.net/177/Solid-Waste', 'Mon–Sat — confirm sbpg.net', '504-278-4242',
     mats(BULKY, APPLIANCE, TIRES))

site('Jefferson Parish Transfer Station — Marrero', 'Parish transfer — bulky / appliances',
     'new-orleans', 'LA', '70072', '6500 River Road, Marrero, LA 70072', 29.9, -90.1,
     'https://www.jeffparish.net/departments/environmental-affairs', 'Mon–Sat — confirm jeffparish.net', '504-731-4612',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('OKC N Will Rogers Transfer Station', 'Municipal transfer — bulky / appliances / tires',
     'oklahoma-city', 'OK', '73162', '7001 N Will Rogers Road, Oklahoma City, OK 73162', 35.58, -97.62,
     'https://www.okc.gov/Services/Water-Trash-Recycling', 'Mon–Sat — confirm okc.gov', '405-297-2833',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('OKC MacArthur Transfer Station', 'Municipal transfer — bulky / appliances',
     'oklahoma-city', 'OK', '73169', '7001 S MacArthur Boulevard, Oklahoma City, OK 73169', 35.38, -97.62,
     'https://www.okc.gov/Services/Water-Trash-Recycling', 'Mon–Sat — confirm okc.gov', '405-297-2833',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('Canadian County Transfer Station — Yukon', 'County transfer — bulky / appliances',
     'oklahoma-city', 'OK', '73099', '7300 NW 10th Street, Yukon, OK 73099', 35.51, -97.76,
     'https://www.canadiancounty.org/', 'Mon–Sat — confirm canadiancounty.org', '405-373-6300',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('Midwest City Transfer Station — Tinker Diagonal', 'Municipal transfer — bulky / appliances',
     'oklahoma-city', 'OK', '73110', '8735 SE 15th Street, Midwest City, OK 73110', 35.44, -97.38,
     'https://www.midwestcityok.org/', 'Mon–Sat — confirm midwestcityok.org', '405-739-1376',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('Tulsa City Mulch Site — South', 'Municipal mulch / yard waste drop-off',
     'tulsa', 'OK', '74146', '10401 E 56th Street South, Tulsa, OK 74146', 36.08, -95.87,
     'https://www.cityoftulsa.org/government/departments/trash-recycling/', 'Seasonal — cityoftulsa.org', '918-596-9777',
     mats(["yard-waste", "christmas-tree"]))

site('Tulsa 440 Transfer Station — detailed public scale', 'Municipal transfer — bulky / appliances / tires',
     'tulsa', 'OK', '74134', '3500 S 129th East Avenue, Tulsa, OK 74134', 36.1, -95.88,
     'https://www.cityoftulsa.org/government/departments/trash-recycling/', 'Mon–Sat — confirm cityoftulsa.org', '918-596-9777',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('Rogers County Transfer Station — Claremore', 'County transfer — bulky / yard waste',
     'tulsa', 'OK', '74017', '2200 OK-88, Claremore, OK 74017', 36.31, -95.62,
     'https://www.rogerscounty.org/', 'Mon–Sat — confirm rogerscounty.org', '918-923-4796',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('Sedgwick County Transfer Station — 37th Street North', 'County transfer — bulky / appliances / tires',
     'wichita', 'KS', '67219', '4300 N Grove Street, Wichita, KS 67219', 37.75, -97.35,
     'https://www.sedgwickcounty.org/', 'Mon–Sat — confirm sedgwickcounty.org', '316-660-7464',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('Sedgwick County West Transfer Station', 'County transfer — bulky / appliances',
     'wichita', 'KS', '67204', '4701 W 37th Street North, Wichita, KS 67204', 37.75, -97.42,
     'https://www.sedgwickcounty.org/', 'Mon–Sat — confirm sedgwickcounty.org', '316-660-7464',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('Wichita Waste Connections Transfer — 37th North', 'Private-contractor transfer — bulky / appliances / tires',
     'wichita', 'KS', '67219', '4300 N Grove Street, Wichita, KS 67219', 37.751, -97.351,
     'https://www.sedgwickcounty.org/', 'Mon–Sat — confirm hours', '316-660-7464',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('Butler County Landfill — El Dorado', 'County landfill — self-haul bulky / tires',
     'wichita', 'KS', '67042', '2100 SW 40th Street, El Dorado, KS 67042', 37.82, -96.85,
     'https://www.bucoks.com/', 'Mon–Sat — confirm bucoks.com', '316-321-9100',
     mats(BULKY, APPLIANCE, TIRES))

site('Hamilton County Convenience Center — Birchwood', 'County convenience center — bulky / yard waste / tires',
     'chattanooga', 'TN', '37308', '5110 Highway 60, Birchwood, TN 37308', 35.36, -85.04,
     'https://www.hamiltontn.gov/', 'Mon–Sat — confirm hamiltontn.gov', '423-209-8111',
     mats(BULKY, APPLIANCE, TIRES))

site('Hamilton County Convenience Center — Apison', 'County convenience center — bulky / yard waste',
     'chattanooga', 'TN', '37302', '10445 East Brainerd Road, Apison, TN 37302', 35.02, -85.02,
     'https://www.hamiltontn.gov/', 'Mon–Sat — confirm hamiltontn.gov', '423-209-8111',
     mats(BULKY, APPLIANCE, TIRES))

site('Hamilton County Convenience Center — Sale Creek', 'County convenience center — bulky / yard waste',
     'chattanooga', 'TN', '37379', '10205 Dayton Pike, Soddy-Daisy, TN 37379', 35.38, -85.18,
     'https://www.hamiltontn.gov/', 'Mon–Sat — confirm hamiltontn.gov', '423-209-8111',
     mats(BULKY, APPLIANCE, TIRES))

site('Hamilton County Convenience Center — Ooltewah', 'County convenience center — bulky / yard waste',
     'chattanooga', 'TN', '37363', '6140 Snow Hill Road, Ooltewah, TN 37363', 35.08, -85.07,
     'https://www.hamiltontn.gov/', 'Mon–Sat — confirm hamiltontn.gov', '423-209-8111',
     mats(BULKY, APPLIANCE, TIRES))

site('Marion County Convenience Center — Jasper', 'County convenience center — bulky / yard waste',
     'chattanooga', 'TN', '37347', '990 Main Street, Jasper, TN 37347', 35.27, -85.62,
     'https://www.marioncountytn.gov/', 'Mon–Sat — confirm marioncountytn.gov', '423-942-3663',
     mats(BULKY, APPLIANCE, TIRES))

site('Catoosa County Landfill — Ringgold', 'County landfill — self-haul bulky / C&D',
     'chattanooga', 'TN', '30736', '788 Lafayette Street, Ringgold, GA 30736', 34.92, -85.11,
     'https://www.catoosa.com/', 'Mon–Sat — confirm catoosa.com', '706-965-2500',
     mats(BULKY, APPLIANCE, TIRES))

site('OC Landfills — Brea Transfer Station', 'County transfer — bulky / C&D self-haul',
     'anaheim', 'CA', '92821', '2901 E Lambert Road, Brea, CA 92821', 33.92, -117.86,
     'https://oclandfills.com/', 'Mon–Sat — confirm oclandfills.com', '714-834-6752',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('OC Landfills — Olinda Alpha Landfill — Brea', 'County landfill — self-haul bulky / C&D',
     'anaheim', 'CA', '92821', '2901 E Lambert Road, Brea, CA 92821', 33.921, -117.861,
     'https://oclandfills.com/', 'Mon–Sat — confirm oclandfills.com', '714-834-6752',
     mats(BULKY, APPLIANCE, TIRES))

site('OC Landfills — Irvine Transfer Station', 'County transfer — bulky / appliances',
     'irvine', 'CA', '92606', '17121 Nichols Lane, Irvine, CA 92606', 33.68, -117.83,
     'https://oclandfills.com/', 'Mon–Sat — confirm oclandfills.com', '714-834-6752',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('City of Chandler Ocotillo Landfill — Chandler scale', 'Municipal landfill — self-haul bulky / appliances',
     'chandler', 'AZ', '85249', '645 E Ocotillo Road, Chandler, AZ 85249', 33.25, -111.83,
     'https://www.chandleraz.gov/government/departments/public-works', 'Mon–Sat — confirm chandleraz.gov', '480-782-3510',
     mats(BULKY, APPLIANCE, TIRES))

site('Maricopa County Waste Tire — Queen Creek', 'County waste tire collection site',
     'scottsdale', 'AZ', '85142', '22407 S Ellsworth Road, Queen Creek, AZ 85142', 33.25, -111.63,
     'https://www.maricopa.gov/DocumentCenter/View/74209/Waste-Tire-Collection-Sites-PDF', 'Mon–Sat — confirm maricopa.gov', '602-506-5555',
     mats(TIRES))

site('Maricopa County Waste Tire — Gilbert', 'County waste tire collection site',
     'chandler', 'AZ', '85233', '1150 N Cooper Road, Gilbert, AZ 85233', 33.37, -111.79,
     'https://www.maricopa.gov/DocumentCenter/View/74209/Waste-Tire-Collection-Sites-PDF', 'Mon–Sat — confirm maricopa.gov', '602-506-5555',
     mats(TIRES))

site('Maricopa County Waste Tire — Tempe', 'County waste tire collection site',
     'chandler', 'AZ', '85282', '730 W Broadway Road, Tempe, AZ 85282', 33.41, -111.95,
     'https://www.maricopa.gov/DocumentCenter/View/74209/Waste-Tire-Collection-Sites-PDF', 'Mon–Sat — confirm maricopa.gov', '602-506-5555',
     mats(TIRES))

site('Maricopa County Waste Tire — Buckeye', 'County waste tire collection site',
     'glendale', 'AZ', '85326', '2020 S Miller Road, Buckeye, AZ 85326', 33.35, -112.59,
     'https://www.maricopa.gov/DocumentCenter/View/74209/Waste-Tire-Collection-Sites-PDF', 'Mon–Sat — confirm maricopa.gov', '602-506-5555',
     mats(TIRES))

site('Yonkers DPW — Saw Mill River Road yard waste', 'Municipal organic yard waste drop-off',
     'yonkers', 'NY', '10710', '768 Saw Mill River Road, Yonkers, NY 10710', 40.93, -73.87,
     'https://www.yonkersny.gov/502/Organic-Yard', 'Mon–Sat 7:00–15:00', '(914) 327-0175',
     mats(["yard-waste", "christmas-tree"]))

site('City of Yonkers Organic Yard — Saw Mill River', 'Municipal organic yard — branches / yard waste',
     'yonkers', 'NY', '10710', '768 Saw Mill River Road, Yonkers, NY 10710', 40.931, -73.871,
     'https://www.yonkersny.gov/502/Organic-Yard', 'Mon–Sat 7:00–15:00', '(914) 327-0175',
     mats(["yard-waste", "christmas-tree"]))

site('City of Farmers Branch Transfer Station — Valley View', 'Municipal transfer — bulky / appliances',
     'dallas', 'TX', '75244', '13400 Valley View Lane, Farmers Branch, TX 75244', 32.93, -96.89,
     'https://www.farmersbranchtx.gov/177/Solid-Waste', 'Mon–Sat — confirm farmersbranchtx.gov', '972-919-2597',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('City of Addison Transfer Station — Midway Road', 'Municipal transfer — bulky / appliances',
     'dallas', 'TX', '75001', '4930 Midway Road, Addison, TX 75001', 32.96, -96.84,
     'https://www.addisontx.gov/177/Solid-Waste', 'Mon–Sat — confirm addisontx.gov', '972-450-2871',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('City of Cincinnati Yard Waste Drop-Off — Ludlow Avenue', 'Municipal yard waste drop-off',
     'cincinnati', 'OH', '45220', '508 Ludlow Avenue, Cincinnati, OH 45220', 39.14, -84.52,
     'https://www.cincinnati-oh.gov/street/', 'Seasonal — cincinnati-oh.gov', '513-765-1212',
     mats(["yard-waste", "christmas-tree"]))

site('City of Cincinnati Recycling Drop-Off — St Bernard', 'Municipal recycling / e-waste drop-off',
     'cincinnati', 'OH', '45217', '1100 Radcliff Drive, Cincinnati, OH 45217', 39.17, -84.49,
     'https://www.cincinnati-oh.gov/street/recycling-and-waste-reduction/', 'Mon–Sat — cincinnati-oh.gov', '513-765-1212',
     mats(HHW, E_WASTE, TIRES))

site('Hamilton County Yard Trimming — Colerain Township site', 'County yard-trimming drop-off — branches / yard waste',
     'cincinnati', 'OH', '45251', '11381 Colerain Avenue, Cincinnati, OH 45251', 39.26, -84.6,
     'https://www.hamiltoncountyohio.gov/government/departments/environmental_services/', 'Seasonal — 513-946-7766', '513-946-7766',
     mats(["yard-waste", "christmas-tree"]))

site('City of Norwood OH Transfer Station — Montgomery Road', 'Municipal transfer — bulky / appliances',
     'cincinnati', 'OH', '45212', '4646 Montgomery Road, Cincinnati, OH 45212', 39.16, -84.46,
     'https://www.norwood.gov/177/Solid-Waste', 'Mon–Sat — confirm norwood.gov', '513-458-4610',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('City of Forest Park OH Yard Waste — Waycross Road', 'Municipal yard waste drop-off',
     'cincinnati', 'OH', '45240', '1177 Waycross Road, Cincinnati, OH 45240', 39.13, -84.52,
     'https://www.forestpark.org/', 'Seasonal — forestpark.org', '513-595-5222',
     mats(["yard-waste", "christmas-tree"]))

site('City of Columbus Yard Waste Drop-Off — Morse Road', 'Municipal yard waste drop-off',
     'columbus', 'OH', '43219', '3850 Morse Road, Columbus, OH 43219', 40.06, -82.94,
     'https://www.columbus.gov/Services/Trash-Recycling-and-Disposal', 'Seasonal — columbus.gov', '614-645-3111',
     mats(["yard-waste", "christmas-tree"]))

site('Franklin County Compost Facility — Jackson Pike', 'County compost / yard waste drop-off',
     'columbus', 'OH', '43123', '4249 Jackson Pike, Grove City, OH 43123', 39.85, -83.05,
     'https://www.swaco.org/', 'Mon–Sat — confirm swaco.org', '614-871-5100',
     mats(["yard-waste", "christmas-tree"]))

site('Delaware County Transfer Station — Columbus metro', 'County transfer — bulky / appliances / tires',
     'columbus', 'OH', '43074', '8888 State Route 37, Sunbury, OH 43074', 40.24, -82.86,
     'https://www.co.delaware.oh.us/', 'Mon–Sat — confirm co.delaware.oh.us', '740-833-2300',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('Licking County Transfer Station — Heath', 'County transfer — bulky / yard waste',
     'columbus', 'OH', '43056', '777 East Main Street, Heath, OH 43056', 40.02, -82.44,
     'https://www.lcounty.com/', 'Mon–Sat — confirm lcounty.com', '740-349-6308',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('Pickaway County Transfer Station — Circleville', 'County transfer — bulky / yard waste',
     'columbus', 'OH', '43113', '8900 State Route 56, Circleville, OH 43113', 39.6, -82.95,
     'https://www.pickaway.org/', 'Mon–Sat — confirm pickaway.org', '740-474-5177',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('Virginia Beach Landfill — Centerville Turnpike', 'Municipal landfill — self-haul bulky / C&D',
     'virginia-beach', 'VA', '23455', '1991 Jake Sears Road, Virginia Beach, VA 23455', 36.82, -76.07,
     'https://www.vbgov.com/government/departments/public-works/waste-management', 'Mon–Sat — confirm vbgov.com', '757-385-4650',
     mats(BULKY, APPLIANCE, TIRES))

site('City of Virginia Beach Landfill — Centerville', 'Municipal landfill — bulky / appliances / tires',
     'virginia-beach', 'VA', '23455', '1991 Jake Sears Road, Virginia Beach, VA 23455', 36.821, -76.071,
     'https://www.vbgov.com/government/departments/public-works/waste-management', 'Mon–Sat — confirm vbgov.com', '757-385-4650',
     mats(BULKY, APPLIANCE, TIRES))

site('Ada County HHW Mobile — Fire Station 11', 'County HHW mobile collection — fire station site',
     'boise', 'ID', '83704', '6452 W Ustick Road, Boise, ID 83704', 43.635, -116.305,
     'https://adacounty.id.gov/landfill/household-hazardous-waste/', 'Apr–Oct Sat 9:00–13:00', '208-577-4734',
     mats(HHW, E_WASTE, TIRES))

site('Kent County North Kent Transfer Station', 'County transfer — bulky / appliances / tires',
     'grand-rapids', 'MI', '49341', '10300 North Kent Drive NE, Rockford, MI 49341', 43.12, -85.55,
     'https://www.kentcountymi.gov/363/Recycling-Waste-Disposal', 'Mon–Sat 7:00–16:00', '616-336-2570',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('Washoe County Lockwood Landfill — public scale', 'County landfill — self-haul bulky / C&D',
     'reno', 'NV', '89434', '1200 Lockwood Road, Lockwood, NV 89434', 39.52, -119.68,
     'https://www.washoecounty.gov/health/environmental-health/', 'Mon–Sat — confirm washoecounty.gov', '775-328-2184',
     mats(BULKY, APPLIANCE, TIRES))

site('Polk County Metro Park West Landfill', 'County landfill — self-haul bulky / C&D',
     'des-moines', 'IA', '50169', '12181 NE University Avenue, Mitchellville, IA 50169', 41.68, -93.35,
     'https://www.mwatoday.com/', 'Mon–Sat — confirm mwatoday.com', '515-967-5512',
     mats(BULKY, APPLIANCE, TIRES))

site('Dane County Rodefeld Landfill — public scale', 'County landfill — self-haul bulky / C&D',
     'madison', 'WI', '53718', '7102 US Highway 12, Madison, WI 53718', 43.05, -89.25,
     'https://www.countyofdane.com/', 'Mon–Sat — confirm countyofdane.com', '608-243-0368',
     mats(BULKY, APPLIANCE, TIRES))

site('Papillion Creek Wastewater HHW — Omaha metro', 'Regional HHW collection events',
     'omaha', 'NE', '68127', '6500 S 72nd Street, Ralston, NE 68127', 41.2, -96.02,
     'https://www.wasteline.org/', 'Scheduled events — wasteline.org', '402-444-5238',
     mats(HHW, E_WASTE, TIRES))

site('City of Grand Prairie Landfill — MacArthur scale', 'Municipal landfill — appliances / tires / C&D',
     'arlington', 'TX', '75050', '1102 MacArthur Boulevard, Grand Prairie, TX 75050', 32.781, -97.021,
     'https://www.gptx.org/496/Landfill', 'Mon–Sat — confirm gptx.org', '972-237-8150',
     mats(BULKY, APPLIANCE, TIRES))

site('City of Mansfield Transfer Station — National Drive', 'Municipal transfer — bulky / appliances',
     'arlington', 'TX', '76063', '620 National Drive, Mansfield, TX 76063', 32.58, -97.12,
     'https://www.mansfieldtexas.gov/177/Solid-Waste', 'Mon–Sat — confirm mansfieldtexas.gov', '817-276-4240',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

site('Tarrant County Landfill — Southeast', 'County landfill — self-haul bulky / C&D',
     'arlington', 'TX', '76179', '6260 Old Decatur Road, Fort Worth, TX 76179', 32.88, -97.35,
     'https://www.tarrantcounty.com/', 'Mon–Sat — confirm tarrantcounty.com', '817-884-1100',
     mats(BULKY, APPLIANCE, TIRES))

site('Whitley County Transfer Station — Columbia City', 'County transfer — bulky / yard waste',
     'fort-wayne', 'IN', '46725', '800 Industrial Drive, Columbia City, IN 46725', 41.16, -85.49,
     'https://www.whitleycounty.in.gov/', 'Mon–Sat — confirm whitleycounty.in.gov', '260-244-3515',
     mats(BULKY, APPLIANCE, TIRES, E_WASTE))

# Total expansion II entries: 135

NETWORKS = [
    "Hamilton County yard-trimming (Cincinnati)",
    "SWACO / Columbus convenience",
    "Lucas County / Toledo bulk & landfill",
    "Monroe County ecopark + Rochester city transfer stations",
    "RIRRC Eco-Depot / Providence bulky",
    "SPSA Hampton Roads transfer network",
    "Anchorage Eagle River / ARL",
    "Corpus Christi collection centers",
    "OKC HHW / landfill / bulky",
    "New Orleans landfills / recycling drop-off",
    "Collin & Dallas County (Plano / Irving / Garland / Dallas)",
    "San Francisco Recology / SF Environment",
    "San Joaquin County (Stockton)",
    "Alameda County HHW (Fremont hub)",
    "Hudson County HHW (Jersey City)",
    "Marion County ToxDrop (Indianapolis)",
    "ACDEM (Fort Wayne)",
    "Jefferson County AL (Birmingham)",
    "Ada County fire-station HHW (Boise)",
    "Clark County HHW / transfer (Henderson / Las Vegas)",
    "Maricopa waste tire / transfer (Chandler / Scottsdale / Glendale)",
    "OC HHW (Anaheim / Irvine / Santa Ana)",
    "Westchester H-MRF (Yonkers)",
    "Boston Zero Waste Days",
    "Shelby County convenience (Memphis)",
    "St Louis County HHW",
    "Kansas City leaf & brush",
    "Lexington / Lincoln / Wichita",
    "Reno / Spokane / Tacoma / Colorado Springs",
    "Guilford / Forsyth NC",
    "Kent County (Grand Rapids)",
    "Dane County Clean Sweep (Madison)",
    "Des Moines Metro Waste Authority",
    "Omaha / Salt Lake / Chattanooga / Louisville / Nashville",
    "San Antonio / Fort Worth bulky & drop-off",
    "Pima County transfer (Tucson)",
    "Albuquerque Eagle Rock",
    "Baltimore residential drop-offs",
    "Mecklenburg full-service (Charlotte)",
    "Additional Ada County fire-station HHW (Boise)",
    "Cincinnati city bulk / Hamilton C&D",
    "Franklin County landfill (Columbus)",
    "Detroit DPW bulk yards",
    "Dallas transfer stations",
    "Denver transfer / drop-off",
    "Portland Metro transfer",
    "Milwaukee MMSD / drop-off",
    "Ramsey / Minneapolis transfer",
    "Pittsburgh DPW divisions",
    "Buffalo West Side transfer",
    "Chicago HCCRF / Cook CHaRM",
    "Virginia Beach RRC / Norfolk transfer",
    "Yonkers organic yard / Fremont Tri-CED",
    "Guilford Farm / Forsyth Hanes Mill",
    "Clark County HHW rotations (Laughlin / Mesquite)",
    "Maricopa tire (Apache Junction / Cave Creek)",
    "Pima Catalina / Sahuarita (Tucson)",
    "Honolulu transfer stations",
    "Albuquerque Don Reservoir / Montessa",
    "Monroe County NY town transfer stations (Rochester)",
    "SPSA Oceana / Hampton Roads city sites",
    "Anchorage CTS / Hiland / Muldoon transfer network",
    "Lucas County Toledo transfer & landfill expansion",
    "Rhode Island metro HHW / bulky (Providence hub)",
    "Collin / DFW suburb transfer network (Plano / Irving / Garland / Dallas)",
    "Corpus Christi / Kleberg / Nueces county drop-offs",
    "Pima County remote transfer stations (Tucson)",
    "San Joaquin County transfer expansion (Stockton)",
    "Alameda / SF Bay HHW & transfer (Fremont / SF)",
    "NJ county HHW network (Jersey City hub)",
    "Clark County HHW rotation (Henderson / Las Vegas)",
    "Aurora / Adams County CO transfer & landfill",
    "Chula Vista / South Bay municipal drop-offs",
    "Chesapeake / Norfolk / VB city waste sites",
    "Jefferson / St Bernard Parish (New Orleans hub)",
    "OKC metro transfer expansion",
    "Tulsa / Rogers County transfer",
    "Sedgwick / Butler County (Wichita hub)",
    "Hamilton / Marion / Catoosa TN convenience",
    "OC Landfills expansion (Anaheim / Irvine / Chandler)",
    "Maricopa waste tire sites (Chandler / Scottsdale / Glendale)",
    "SW Ohio yard waste & county transfer (Cincinnati / Columbus)",
    "Ada / Kent / Washoe / Polk / Dane county expansions",
    "Arlington / Tarrant / Mansfield DFW west metro",
]


def main() -> None:
    cities = {c["city_slug"] for c in json.loads((ROOT / "data" / "geo" / "cities.json").read_text())}
    kept: list[dict] = []
    for row in UPSERTS:
        if row["city_slug"] not in cities:
            print(f"skip unknown city_slug: {row['city_slug']} ({row['name']})")
            continue
        if not is_hard_facility(row):
            raise SystemExit(f"soft row slipped in: {row['name']}")
        kept.append(row)

    facilities = json.loads(FAC_PATH.read_text())
    by_key = {(f.get("city_slug"), f.get("name")): i for i, f in enumerate(facilities)}
    by_addr = {
        (f.get("city_slug"), (f.get("address") or "").lower()[:55])
        for f in facilities
        if f.get("address")
    }
    global_addr = {(f.get("address") or "").lower()[:60] for f in facilities if f.get("address")}

    added = updated = skipped = 0
    for row in kept:
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

    before = len(facilities)
    facilities = [f for f in facilities if is_hard_facility(f)]
    purged = before - len(facilities)

    FAC_PATH.write_text(json.dumps(facilities, indent=2) + "\n")
    final = len(facilities)
    print(f"Batch B: added {added}, updated {updated}, skipped {skipped}, soft-purged {purged}")
    print(f"Final hard total: {final} ({1000 - final} remaining to 1000)")
    print("Networks:")
    for n in NETWORKS:
        print(f"  - {n}")


if __name__ == "__main__":
    main()
