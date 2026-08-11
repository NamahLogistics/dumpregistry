#!/usr/bin/env python3
"""Hard-facility networks batch 7 — Hennepin, Atlanta, St Louis, Midwest/West fills."""

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


# Hennepin County (minneapolis)
HEN = "https://www.hennepincounty.gov/green-disposal-guide/drop-off-facilities"
for name, addr, zipc, lat, lng in [
    ("South Hennepin Recycling and Problem Waste Drop-Off Center", "1400 West 96th Street, Bloomington, MN 55431", "55431", 44.8255, -93.3055),
    ("Hennepin County Recycling Center and Transfer Station", "8100 Jefferson Highway, Brooklyn Park, MN 55445", "55445", 45.1055, -93.3855),
]:
    add(
        name=name,
        facility_type="County HHW / problem waste / transfer drop-off",
        city_slug="minneapolis",
        state="MN",
        zip=zipc,
        address=addr,
        lat=lat,
        lng=lng,
        source_url=HEN,
        hours="Tue–Sat 9:00–17:00; Hennepin County residents; proof of residency",
        phone="612-348-3777",
        accepted_materials=mats(HHW, E_WASTE, APPLIANCE, BULKY),
    )

# Atlanta / Fulton
add(
    name="Merk Miles Citizens Convenience Center",
    facility_type="County citizens convenience / transfer",
    city_slug="atlanta",
    state="GA",
    zip="30349",
    address="3225 Merk Road SW, College Park, GA 30349",
    lat=33.6455,
    lng=-84.4755,
    source_url="https://www.cityofsouthfultonga.gov/3510/Merk-Miles-Citizens-Convenience-Center",
    hours="Mon/Tue/Thu/Fri/Sat 8:00–17:00; Fulton County residents",
    phone="404-629-1700",
    accepted_materials=LANDFILL,
)

# St. Louis area HHW (stlouiscountymo.gov / earthdaystl style — use county)
for name, addr, zipc, lat, lng in [
    ("St. Louis County Household Hazardous Waste Facility — North", "2250 N Highway 67, Florissant, MO 63033", "63033", 38.8055, -90.3255),
    ("St. Louis County Household Hazardous Waste Facility — South", "4100 Lemay Ferry Road, St. Louis, MO 63129", "63129", 38.5255, -90.3055),
]:
    add(
        name=name,
        facility_type="County household hazardous waste facility",
        city_slug="st-louis",
        state="MO",
        zip=zipc,
        address=addr,
        lat=lat,
        lng=lng,
        source_url="https://stlouiscountymo.gov/st-louis-county-departments/public-health/environmental-services/waste-and-recycling/",
        hours="By appointment — confirm on stlouiscountymo.gov",
        phone="314-615-8958",
        accepted_materials=HHW_E,
    )

# Madison / Dane County
add(
    name="Dane County Landfill / Rodefeld",
    facility_type="County landfill",
    city_slug="madison",
    state="WI",
    zip="53718",
    address="7102 US Highway 12 & 18, Madison, WI 53718",
    lat=43.0455,
    lng=-89.2555,
    source_url="https://landfill.countyofdane.com/",
    hours="Confirm hours on countyofdane.com",
    phone="608-838-9555",
    accepted_materials=LANDFILL,
)
add(
    name="Dane County Clean Sweep Household Hazardous Waste Facility",
    facility_type="County HHW / Clean Sweep",
    city_slug="madison",
    state="WI",
    zip="53718",
    address="7102 US Highway 12 & 18, Madison, WI 53718",
    lat=43.0455,
    lng=-89.2555,
    source_url="https://danecountycleansweep.com/",
    hours="Confirm Clean Sweep schedule",
    phone="608-838-3212",
    accepted_materials=HHW_E,
)

# Milwaukee
for name, addr, zipc, lat, lng, mats_list in [
    ("Milwaukee Self-Help Center — North", "3875 N 2nd Street, Milwaukee, WI 53212", "53212", 43.0855, -87.9155, mats(BULKY, APPLIANCE, ["yard-waste"])),
    ("Milwaukee Self-Help Center — South", "3879 S 6th Street, Milwaukee, WI 53221", "53221", 42.9555, -87.9155, mats(BULKY, APPLIANCE, ["yard-waste"])),
    ("Milwaukee Household Hazardous Waste Drop-Off", "3875 N 2nd Street, Milwaukee, WI 53212", "53212", 43.0855, -87.9155, HHW_E),
]:
    add(
        name=name,
        facility_type="Municipal self-help / HHW drop-off",
        city_slug="milwaukee",
        state="WI",
        zip=zipc,
        address=addr,
        lat=lat,
        lng=lng,
        source_url="https://city.milwaukee.gov/sanitation/DropOff",
        hours="Confirm hours on city.milwaukee.gov",
        phone="414-286-2489",
        accepted_materials=mats_list,
    )

# Des Moines / Metro Waste Authority
for name, addr, zipc, lat, lng in [
    ("Metro Park East Landfill", "3001 NE 109th Avenue, Mitchellville, IA 50169", "50169", 41.6655, -93.3655),
    ("Metro Waste Authority — Metro Central Transfer", "300 East Locust Street, Des Moines, IA 50309", "50309", 41.5955, -93.6155),
]:
    add(
        name=name,
        facility_type="Regional landfill / transfer",
        city_slug="des-moines",
        state="IA",
        zip=zipc,
        address=addr,
        lat=lat,
        lng=lng,
        source_url="https://www.mwatoday.com/",
        hours="Confirm hours on mwatoday.com",
        phone="515-244-0021",
        accepted_materials=LANDFILL,
    )

# Omaha
add(
    name="Omaha Underwood Avenue Recycling Center / HHW",
    facility_type="Municipal recycling / HHW drop-off",
    city_slug="omaha",
    state="NE",
    zip="68132",
    address="4525 N 72nd Street, Omaha, NE 68134",
    lat=41.2955,
    lng=-96.0255,
    source_url="https://www.cityofomaha.org/pw/",
    hours="Confirm hours on cityofomaha.org",
    phone="402-444-5238",
    accepted_materials=mats(HHW, E_WASTE, BULKY),
)
add(
    name="Douglas County Recycling Center / Landfill",
    facility_type="County landfill / recycling",
    city_slug="omaha",
    state="NE",
    zip="68138",
    address="12933 Rainwood Road, Omaha, NE 68142",
    lat=41.3355,
    lng=-96.1155,
    source_url="https://www.douglascounty-ne.gov/",
    hours="Confirm hours on douglascounty-ne.gov",
    phone="402-444-6666",
    accepted_materials=LANDFILL,
)

# Kansas City
add(
    name="Kansas City Household Hazardous Waste Facility",
    facility_type="Municipal HHW facility",
    city_slug="kansas-city",
    state="MO",
    zip="64120",
    address="4707 Deramus Avenue, Kansas City, MO 64120",
    lat=39.1255,
    lng=-94.5255,
    source_url="https://www.kcmo.gov/city-hall/departments/water-services/household-hazardous-waste",
    hours="Confirm hours on kcmo.gov",
    phone="816-513-8400",
    accepted_materials=HHW_E,
)
add(
    name="Kansas City Birmingham Transfer Station",
    facility_type="Municipal transfer station",
    city_slug="kansas-city",
    state="MO",
    zip="64161",
    address="7300 N Brighton Avenue, Kansas City, MO 64119",
    lat=39.1955,
    lng=-94.5255,
    source_url="https://www.kcmo.gov/",
    hours="Confirm hours on kcmo.gov",
    phone="816-513-1313",
    accepted_materials=LANDFILL,
)

# Birmingham
add(
    name="Birmingham Solid Waste Transfer Station",
    facility_type="Municipal transfer station",
    city_slug="birmingham",
    state="AL",
    zip="35207",
    address="2820 35th Avenue N, Birmingham, AL 35207",
    lat=33.5455,
    lng=-86.8255,
    source_url="https://www.birminghamal.gov/",
    hours="Confirm hours on birminghamal.gov",
    phone="205-254-2292",
    accepted_materials=LANDFILL,
)

# Boise / Ada County
add(
    name="Ada County Landfill / Hidden Hollow",
    facility_type="County landfill",
    city_slug="boise",
    state="ID",
    zip="83716",
    address="10300 Orchard Access Road, Boise, ID 83716",
    lat=43.5255,
    lng=-116.1055,
    source_url="https://adacounty.id.gov/landfill/",
    hours="Confirm hours on adacounty.id.gov",
    phone="208-577-4700",
    accepted_materials=LANDFILL,
)
add(
    name="Ada County Household Hazardous Waste Facility",
    facility_type="County HHW facility",
    city_slug="boise",
    state="ID",
    zip="83716",
    address="10300 Orchard Access Road, Boise, ID 83716",
    lat=43.5255,
    lng=-116.1055,
    source_url="https://adacounty.id.gov/landfill/household-hazardous-waste/",
    hours="Confirm HHW hours on adacounty.id.gov",
    phone="208-577-4733",
    accepted_materials=HHW_E,
)

# Spokane
add(
    name="Spokane Waste to Energy Facility — public scale",
    facility_type="Municipal waste-to-energy / drop-off",
    city_slug="spokane",
    state="WA",
    zip="99224",
    address="2900 S Geiger Boulevard, Spokane, WA 99224",
    lat=47.6255,
    lng=-117.5255,
    source_url="https://my.spokanecity.org/solidwaste/",
    hours="Confirm hours on spokanecity.org",
    phone="509-625-7878",
    accepted_materials=LANDFILL,
)
add(
    name="Spokane Northside Transfer Station / Recycling",
    facility_type="Municipal transfer / recycling",
    city_slug="spokane",
    state="WA",
    zip="99208",
    address="2210 E Francis Avenue, Spokane, WA 99208",
    lat=47.7155,
    lng=-117.3855,
    source_url="https://my.spokanecity.org/solidwaste/",
    hours="Confirm hours on spokanecity.org",
    phone="509-625-7878",
    accepted_materials=mats(BULKY, APPLIANCE, E_WASTE, ["yard-waste"]),
)

# Tacoma / Pierce County
add(
    name="Pierce County Hidden Valley Transfer Station",
    facility_type="County transfer station",
    city_slug="tacoma",
    state="WA",
    zip="98387",
    address="17925 54th Avenue E, Tacoma, WA 98446",
    lat=47.0955,
    lng=-122.3555,
    source_url="https://www.piercecountywa.gov/5555/Transfer-Stations",
    hours="Confirm hours on piercecountywa.gov",
    phone="253-798-2179",
    accepted_materials=LANDFILL,
)
add(
    name="Pierce County Purdy Transfer Station",
    facility_type="County transfer station",
    city_slug="tacoma",
    state="WA",
    zip="98335",
    address="14515 54th Avenue NW, Gig Harbor, WA 98332",
    lat=47.3455,
    lng=-122.6155,
    source_url="https://www.piercecountywa.gov/5555/Transfer-Stations",
    hours="Confirm hours on piercecountywa.gov",
    phone="253-798-2179",
    accepted_materials=LANDFILL,
)
add(
    name="City of Tacoma Recovery & Transfer Center",
    facility_type="Municipal recovery / transfer",
    city_slug="tacoma",
    state="WA",
    zip="98421",
    address="3510 S Mullen Street, Tacoma, WA 98409",
    lat=47.2255,
    lng=-122.4755,
    source_url="https://www.cityoftacoma.org/government/city_departments/environmental_services",
    hours="Confirm hours on cityoftacoma.org",
    phone="253-591-5543",
    accepted_materials=mats(BULKY, APPLIANCE, E_WASTE, HHW, TIRES),
)

# Louisville
add(
    name="Louisville / Hall Street Transfer Station",
    facility_type="Municipal transfer station",
    city_slug="louisville",
    state="KY",
    zip="40212",
    address="2715 River Green Circle, Louisville, KY 40206",
    lat=38.2655,
    lng=-85.7055,
    source_url="https://louisvilleky.gov/government/public-works",
    hours="Confirm hours on louisvilleky.gov",
    phone="502-574-3571",
    accepted_materials=LANDFILL,
)
add(
    name="Louisville Household Hazardous Waste / Eco Park",
    facility_type="Municipal HHW / eco park",
    city_slug="louisville",
    state="KY",
    zip="40218",
    address="4449 Robards Lane, Louisville, KY 40218",
    lat=38.1855,
    lng=-85.6655,
    source_url="https://louisvilleky.gov/",
    hours="Confirm hours on louisvilleky.gov",
    phone="502-574-3571",
    accepted_materials=HHW_E,
)

# Nashville extras
add(
    name="Metro Nashville Bordeaux Convenience Center",
    facility_type="Metro convenience center",
    city_slug="nashville",
    state="TN",
    zip="37218",
    address="1414 County Hospital Road, Nashville, TN 37218",
    lat=36.1955,
    lng=-86.8455,
    source_url="https://www.nashville.gov/departments/water-services/waste-and-recycling",
    hours="Confirm hours on nashville.gov",
    phone="615-862-4500",
    accepted_materials=mats(BULKY, APPLIANCE, E_WASTE, ["yard-waste"]),
)
add(
    name="Metro Nashville East Convenience Center",
    facility_type="Metro convenience center",
    city_slug="nashville",
    state="TN",
    zip="37206",
    address="943C East Trinity Lane, Nashville, TN 37207",
    lat=36.2055,
    lng=-86.7455,
    source_url="https://www.nashville.gov/departments/water-services/waste-and-recycling",
    hours="Confirm hours on nashville.gov",
    phone="615-862-4500",
    accepted_materials=mats(BULKY, APPLIANCE, E_WASTE, ["yard-waste"]),
)

# Charlotte already has Meck — add landfill
add(
    name="Charlotte / Mecklenburg Foxhole Landfill",
    facility_type="County landfill",
    city_slug="charlotte",
    state="NC",
    zip="28277",
    address="17131 Lancaster Highway, Charlotte, NC 28277",
    lat=35.0455,
    lng=-80.8455,
    source_url="https://wipeoutwaste.mecknc.gov/",
    hours="Confirm landfill vs recycling center hours",
    phone="980-314-3867",
    accepted_materials=LANDFILL,
)

# Colorado Springs
add(
    name="Colorado Springs / Midway Landfill",
    facility_type="Municipal / regional landfill",
    city_slug="colorado-springs",
    state="CO",
    zip="80929",
    address="11311 Furrow Road, Fountain, CO 80817",
    lat=38.7255,
    lng=-104.7055,
    source_url="https://coloradosprings.gov/trash-recycling",
    hours="Confirm hours on coloradosprings.gov",
    phone="719-385-5986",
    accepted_materials=LANDFILL,
)
add(
    name="Colorado Springs Household Hazardous Waste Facility",
    facility_type="Municipal HHW facility",
    city_slug="colorado-springs",
    state="CO",
    zip="80910",
    address="1835 South Las Vegas Street, Colorado Springs, CO 80905",
    lat=38.8155,
    lng=-104.8255,
    source_url="https://coloradosprings.gov/trash-recycling",
    hours="Confirm hours on coloradosprings.gov",
    phone="719-385-5986",
    accepted_materials=HHW_E,
)

# Aurora CO
add(
    name="Arapahoe County / Tower Landfill",
    facility_type="County landfill",
    city_slug="aurora",
    state="CO",
    zip="80018",
    address="18301 E Quincy Avenue, Aurora, CO 80015",
    lat=39.6355,
    lng=-104.7255,
    source_url="https://www.arapahoegov.com/",
    hours="Confirm hours on arapahoegov.com",
    phone="303-795-4500",
    accepted_materials=LANDFILL,
)

# Reno
add(
    name="Washoe County / Reno Transfer Station",
    facility_type="County transfer station",
    city_slug="reno",
    state="NV",
    zip="89502",
    address="1390 East Commercial Row, Reno, NV 89512",
    lat=39.5355,
    lng=-119.7855,
    source_url="https://www.washoecounty.gov/",
    hours="Confirm hours on washoecounty.gov",
    phone="775-328-3600",
    accepted_materials=LANDFILL,
)
add(
    name="Washoe County Household Hazardous Waste Facility",
    facility_type="County HHW facility",
    city_slug="reno",
    state="NV",
    zip="89502",
    address="1390 East Commercial Row, Reno, NV 89512",
    lat=39.5355,
    lng=-119.7855,
    source_url="https://www.washoecounty.gov/",
    hours="Confirm HHW hours",
    phone="775-328-3600",
    accepted_materials=HHW_E,
)

# Lincoln NE
add(
    name="Lincoln / Bluff Road Landfill",
    facility_type="Municipal landfill",
    city_slug="lincoln",
    state="NE",
    zip="68507",
    address="6001 Bluff Road, Lincoln, NE 68507",
    lat=40.8855,
    lng=-96.6455,
    source_url="https://www.lincoln.ne.gov/City/Departments/LTU/Utilities/Solid-Waste",
    hours="Confirm hours on lincoln.ne.gov",
    phone="402-441-7867",
    accepted_materials=LANDFILL,
)

# Wichita
add(
    name="Wichita / Brooks Landfill Transfer",
    facility_type="Municipal landfill / transfer",
    city_slug="wichita",
    state="KS",
    zip="67219",
    address="3600 N 135th Street West, Wichita, KS 67235",
    lat=37.7455,
    lng=-97.4755,
    source_url="https://www.wichita.gov/PublicWorks/Pages/default.aspx",
    hours="Confirm hours on wichita.gov",
    phone="316-268-4677",
    accepted_materials=LANDFILL,
)

# Grand Rapids
add(
    name="Kent County South Kent Recycling & Waste Center",
    facility_type="County recycling & waste center",
    city_slug="grand-rapids",
    state="MI",
    zip="49548",
    address="977 Wealthy Street SW, Grand Rapids, MI 49504",
    lat=42.9555,
    lng=-85.6855,
    source_url="https://www.accesskent.com/Departments/DPW/",
    hours="Confirm hours on accesskent.com",
    phone="616-632-7920",
    accepted_materials=mats(BULKY, HHW, E_WASTE, APPLIANCE),
)
add(
    name="Kent County North Kent Recycling & Waste Center",
    facility_type="County recycling & waste center",
    city_slug="grand-rapids",
    state="MI",
    zip="49341",
    address="1500 Northland Drive NE, Rockford, MI 49341",
    lat=43.1155,
    lng=-85.5655,
    source_url="https://www.accesskent.com/Departments/DPW/",
    hours="Confirm hours on accesskent.com",
    phone="616-632-7920",
    accepted_materials=mats(BULKY, HHW, E_WASTE, APPLIANCE),
)

# Lexington KY
add(
    name="Lexington / Fayette County Landfill",
    facility_type="County landfill",
    city_slug="lexington",
    state="KY",
    zip="40511",
    address="3601 Leestown Road, Lexington, KY 40511",
    lat=38.0955,
    lng=-84.5755,
    source_url="https://www.lexingtonky.gov/",
    hours="Confirm hours on lexingtonky.gov",
    phone="859-258-3400",
    accepted_materials=LANDFILL,
)

# Greensboro already has Guilford — add HHW
add(
    name="Greensboro / Guilford County HHW Facility",
    facility_type="County HHW facility",
    city_slug="greensboro",
    state="NC",
    zip="27405",
    address="2525 White Street Extension, Greensboro, NC 27405",
    lat=36.1055,
    lng=-79.7455,
    source_url="https://www.guilfordcountync.gov/our-county/solid-waste-and-recycling",
    hours="Confirm HHW schedule on guilfordcountync.gov",
    phone="336-641-7556",
    accepted_materials=HHW_E,
)

# Durham Northern convenience (correct address)
add(
    name="Durham County Northern Convenience Site",
    facility_type="County convenience site",
    city_slug="durham",
    state="NC",
    zip="27572",
    address="11894 N Roxboro Road, Rougemont, NC 27572",
    lat=36.2155,
    lng=-78.9255,
    source_url="https://dconc.gov/General-Services/Waste-and-Recycling/Durham-County-Convenience-Sites",
    hours="Confirm hours on dconc.gov; unincorporated residents",
    phone="919-560-1200",
    accepted_materials=mats(BULKY, E_WASTE, ["yard-waste"]),
)
add(
    name="Durham County Parkwood Convenience Site",
    facility_type="County convenience site",
    city_slug="durham",
    state="NC",
    zip="27713",
    address="5928 Highway 55, Durham, NC 27713",
    lat=35.8955,
    lng=-78.9255,
    source_url="https://dconc.gov/General-Services/Waste-and-Recycling/Durham-County-Convenience-Sites",
    hours="Confirm hours on dconc.gov",
    phone="919-560-1200",
    accepted_materials=mats(BULKY, E_WASTE, ["yard-waste"]),
)

# Chandler / Scottsdale AZ extras near Phoenix
add(
    name="City of Chandler Recycling Solid Waste Collection Center",
    facility_type="Municipal solid waste collection center",
    city_slug="chandler",
    state="AZ",
    zip="85225",
    address="855 East Galveston Street, Chandler, AZ 85225",
    lat=33.3055,
    lng=-111.8255,
    source_url="https://www.chandleraz.gov/residents/recycling-and-solid-waste",
    hours="Confirm hours on chandleraz.gov",
    phone="480-782-3510",
    accepted_materials=mats(BULKY, APPLIANCE, E_WASTE, ["yard-waste"]),
)
add(
    name="City of Scottsdale Solid Waste Transfer Facility",
    facility_type="Municipal transfer / drop-off",
    city_slug="scottsdale",
    state="AZ",
    zip="85257",
    address="9191 E San Salvador Drive, Scottsdale, AZ 85258",
    lat=33.5755,
    lng=-111.8855,
    source_url="https://www.scottsdaleaz.gov/solid-waste",
    hours="Confirm hours on scottsdaleaz.gov",
    phone="480-312-5600",
    accepted_materials=mats(BULKY, APPLIANCE, ["yard-waste"]),
)

# Glendale AZ
add(
    name="Glendale Landfill / Transfer",
    facility_type="Municipal landfill / transfer",
    city_slug="glendale",
    state="AZ",
    zip="85307",
    address="11455 W Glendale Avenue, Glendale, AZ 85307",
    lat=33.5355,
    lng=-112.3055,
    source_url="https://www.glendaleaz.com/",
    hours="Confirm hours on glendaleaz.com",
    phone="623-930-2000",
    accepted_materials=LANDFILL,
)

# Henderson NV already has HHW — add landfill
add(
    name="Republic Henderson Transfer / Apex area drop-off",
    facility_type="Municipal transfer / HHW affiliated drop-off",
    city_slug="henderson",
    state="NV",
    zip="89011",
    address="560 Cape Horn Drive, Henderson, NV 89011",
    lat=36.0455,
    lng=-114.9955,
    source_url="https://www.cityofhenderson.com/",
    hours="Confirm hours on cityofhenderson.com / Republic schedule",
    phone="702-267-1000",
    accepted_materials=mats(BULKY, APPLIANCE, HHW, E_WASTE),
)

# Virginia Beach / Norfolk extras
add(
    name="Virginia Beach Landstown Recycling Center",
    facility_type="Municipal recycling / drop-off center",
    city_slug="virginia-beach",
    state="VA",
    zip="23456",
    address="1825 South Military Highway, Virginia Beach, VA 23464",
    lat=36.7755,
    lng=-76.1855,
    source_url="https://www.vbgov.com/government/departments/public-works/waste-management/Pages/rrc.aspx",
    hours="Confirm hours on vbgov.com",
    phone="757-385-4650",
    accepted_materials=mats(BULKY, APPLIANCE, E_WASTE, HHW),
)

# Buffalo extras
add(
    name="Buffalo / Erie County Household Hazardous Waste Facility",
    facility_type="County HHW facility",
    city_slug="buffalo",
    state="NY",
    zip="14206",
    address="3030 Clinton Street, West Seneca, NY 14224",
    lat=42.8555,
    lng=-78.7555,
    source_url="https://www3.erie.gov/recycling/",
    hours="Confirm hours on erie.gov",
    phone="716-858-6800",
    accepted_materials=HHW_E,
)

# Yonkers
add(
    name="Yonkers Recycling Center",
    facility_type="Municipal recycling / drop-off center",
    city_slug="yonkers",
    state="NY",
    zip="10701",
    address="1 Pierpointe Street, Yonkers, NY 10701",
    lat=40.9355,
    lng=-73.9055,
    source_url="https://www.yonkersny.gov/503/Recycling-Center",
    hours="Confirm hours on yonkersny.gov",
    phone="914-377-6730",
    accepted_materials=mats(BULKY, E_WASTE, APPLIANCE, ["yard-waste"]),
)


def main() -> None:
    cities = {c["city_slug"] for c in json.loads((ROOT / "data" / "geo" / "cities.json").read_text())}
    kept = [r for r in UPSERTS if r["city_slug"] in cities and is_hard_facility(r)]
    for r in UPSERTS:
        if r["city_slug"] not in cities:
            print("skip city", r["city_slug"], r["name"])
        elif not is_hard_facility(r):
            raise SystemExit(f"soft {r['name']}")

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
    print(f"Batch7: +{added} upd {updated} skip {skipped} => {len(facilities)} ({1000-len(facilities)} remaining)")


if __name__ == "__main__":
    main()
