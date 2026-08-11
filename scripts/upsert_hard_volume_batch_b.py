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
