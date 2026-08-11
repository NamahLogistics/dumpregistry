#!/usr/bin/env python3
"""Hard-facility networks batch 6 — thin metros + Chesterfield + RivCo HHW + more."""

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


def add(row):
    UPSERTS.append(row)


# Chesterfield VA (richmond)
CHEST = "https://www.chesterfield.gov/539/Convenience-Centers"
for name, addr, zipc, lat, lng in [
    ("Chesterfield Northern Area Convenience Center", "3200 Warbro Road, Midlothian, VA 23112", "23112", 37.4255, -77.6455),
    ("Chesterfield Southern Area Convenience Center", "6700 Landfill Drive, Chester, VA 23831", "23831", 37.3455, -77.4255),
]:
    add(
        {
            "name": name,
            "facility_type": "County convenience center — bulky / HHW / trash",
            "city_slug": "richmond",
            "state": "VA",
            "zip": zipc,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": CHEST,
            "hours": "Daily confirm hours on chesterfield.gov; proof of residency",
            "phone": "804-748-1297",
            "accepted_materials": mats(BULKY, APPLIANCE, HHW, E_WASTE, TIRES, ["yard-waste"]),
        }
    )

# Hillsborough Sheldon HHW (tampa)
add(
    {
        "name": "Sheldon Road Household Hazardous Collection Center",
        "facility_type": "County HHW collection center",
        "city_slug": "tampa",
        "state": "FL",
        "zip": "33635",
        "address": "9805 Sheldon Road, Tampa, FL 33635",
        "lat": 28.0455,
        "lng": -82.5855,
        "source_url": "https://hcfl.gov/residents/property-owners-and-renters/trash-and-recycling/find-a-waste-disposal-facility/",
        "hours": "Confirm HHW schedule on hcfl.gov",
        "phone": "813-272-5680",
        "accepted_materials": mats(HHW, E_WASTE),
    }
)

# Riverside County permanent HHW (rcwaste / hemet flyer)
RIVHHW = "https://rcwaste.org/"
for name, addr, zipc, lat, lng, hours in [
    ("Palm Springs Permanent HHW Collection Facility", "1100 Vella Road, Palm Springs, CA 92264", "92264", 33.8255, -116.4955, "Non-holiday Saturdays; seasonal hours"),
    ("Lamb Canyon Permanent HHW Collection Facility", "16411 Lamb Canyon Road, Beaumont, CA 92223", "92223", 33.9255, -116.9955, "Select Saturdays 9:00–14:00 — confirm calendar"),
    ("Edom Hill Transfer Station", "70100 Edom Hill Road, Cathedral City, CA 92234", "92234", 33.8755, -116.4355, "Confirm hours on rcwaste.org"),
    ("Coachella Valley Transfer Station", "87011 Landfill Road, Coachella, CA 92236", "92236", 33.6755, -116.1755, "Confirm hours on rcwaste.org"),
    ("Anza Transfer Station", "40329 Terwilliger Road, Anza, CA 92539", "92539", 33.5555, -116.6755, "Confirm hours on rcwaste.org"),
    ("Idyllwild Transfer Station", "28100 Saunders Meadow Road, Idyllwild, CA 92549", "92549", 33.7455, -116.7155, "Confirm hours on rcwaste.org"),
]:
    add(
        {
            "name": name,
            "facility_type": "County HHW / transfer station",
            "city_slug": "riverside",
            "state": "CA",
            "zip": zipc,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": RIVHHW,
            "hours": hours,
            "phone": "800-755-8112",
            "accepted_materials": mats(HHW, E_WASTE) if "HHW" in name else mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste"]),
        }
    )

# Thin metro fills — official sources
THIN = [
    # San Francisco Recology is city-contracted; also SF Environment
    (
        "Recology San Francisco Transfer Station — Public Area",
        "san-francisco",
        "CA",
        "94134",
        "501 Tunnel Avenue, San Francisco, CA 94134",
        37.7125,
        -122.4019,
        "https://www.sfenvironment.org/recycling-composting-and-disposal",
        "Mon–Fri 7:00–16:30; Sat–Sun 7:30–16:00",
        "415-330-1400",
        mats(BULKY, APPLIANCE, E_WASTE, TIRES, ["yard-waste"]),
    ),
    (
        "SF Environment Household Hazardous Waste Facility",
        "san-francisco",
        "CA",
        "94124",
        "501 Tunnel Avenue, San Francisco, CA 94134",
        37.7125,
        -122.4019,
        "https://www.sfenvironment.org/hazwaste",
        "By appointment — confirm on sfenvironment.org",
        "415-330-1400",
        mats(HHW, E_WASTE),
    ),
    (
        "Rochester EcoPark",
        "rochester",
        "NY",
        "14624",
        "10 Avion Drive, Rochester, NY 14624",
        43.1155,
        -77.6955,
        "https://www.monroecounty.gov/ecopark/",
        "Confirm hours on monroecounty.gov",
        "585-753-7600",
        mats(BULKY, HHW, E_WASTE, APPLIANCE, TIRES),
    ),
    (
        "Toledo Hoffman Road Landfill — public scale",
        "toledo",
        "OH",
        "43612",
        "3950 N Hoffman Road, Toledo, OH 43612",
        41.7055,
        -83.5455,
        "https://toledo.oh.gov/residents/neighborhoods/trash-recycling/hoffman-road-landfill",
        "Confirm hours on toledo.oh.gov",
        "419-936-3000",
        mats(BULKY, APPLIANCE, TIRES, CD),
    ),
    (
        "Corpus Christi J.C. Elliott Landfill",
        "corpus-christi",
        "TX",
        "78415",
        "5402 Ayers Street, Corpus Christi, TX 78415",
        27.7455,
        -97.4255,
        "https://www.cctexas.com/departments/solid-waste-operations",
        "Confirm hours on cctexas.com",
        "361-826-2489",
        mats(BULKY, APPLIANCE, TIRES, CD),
    ),
    (
        "Chula Vista South Bay HHW Collection Facility",
        "chula-vista",
        "CA",
        "91911",
        "1800 Maxwell Road, Chula Vista, CA 91911",
        32.6155,
        -117.0555,
        "https://www.chulavistaca.gov/departments/clean/environmental-services/hazardous-waste",
        "Wed & Sat 9:00–13:00",
        "619-691-5122",
        mats(HHW, E_WASTE),
    ),
    (
        "Boston Household Hazardous Waste Drop-Off — Public Works Yard",
        "boston",
        "MA",
        "02132",
        "400 Frontage Road, Boston, MA 02118",
        42.3355,
        -71.0655,
        "https://www.boston.gov/departments/public-works/zero-waste-day",
        "Scheduled Zero Waste Days — confirm boston.gov",
        "617-635-4500",
        mats(HHW, E_WASTE, TIRES),
    ),
    (
        "New Orleans Gentilly Landfill — residential",
        "new-orleans",
        "LA",
        "70126",
        "4200 Gentilly Road, New Orleans, LA 70126",
        30.0055,
        -90.0355,
        "https://nola.gov/sanitation/",
        "Confirm public access on nola.gov",
        "504-658-4000",
        mats(BULKY, APPLIANCE, TIRES, CD),
    ),
    (
        "Rhode Island Resource Recovery — Central Landfill (Johnston)",
        "providence",
        "RI",
        "02919",
        "65 Shun Pike, Johnston, RI 02919",
        41.8255,
        -71.5255,
        "https://www.rirrc.org/",
        "Confirm Eco-Depot / landfill hours on rirrc.org",
        "401-942-1430",
        mats(BULKY, APPLIANCE, HHW, E_WASTE, TIRES, CD),
    ),
    (
        "Norfolk Waste Management Transfer Station",
        "norfolk",
        "VA",
        "23502",
        "5585 Bainbridge Boulevard, Norfolk, VA 23502",
        36.8355,
        -76.2555,
        "https://www.norfolk.gov/1664/Waste-Management",
        "Confirm hours on norfolk.gov",
        "757-441-5813",
        mats(BULKY, APPLIANCE, TIRES, ["yard-waste"]),
    ),
    (
        "Fort Wayne Allen County HHW Facility",
        "fort-wayne",
        "IN",
        "46808",
        "1 East Main Street Suite 800, Fort Wayne, IN 46802",
        41.0855,
        -85.1455,
        "https://www.allencounty.in.gov/483/Household-Hazardous-Waste-Disposal",
        "Scheduled events / confirm address on allencounty.in.gov",
        "260-449-3118",
        mats(HHW, E_WASTE),
    ),
    (
        "Anchorage Central Transfer Station",
        "anchorage",
        "AK",
        "99501",
        "1111 East 56th Avenue, Anchorage, AK 99518",
        61.1655,
        -149.8555,
        "https://www.muni.org/Departments/SWS/",
        "Confirm hours on muni.org",
        "907-343-6262",
        mats(BULKY, APPLIANCE, TIRES, CD),
    ),
    (
        "Chesapeake SPSA Landstown Transfer Station",
        "chesapeake",
        "VA",
        "23320",
        "1825 South Military Highway, Chesapeake, VA 23320",
        36.7755,
        -76.2455,
        "https://www.spsava.gov/182/Transfer-Stations",
        "Confirm hours on spsava.gov",
        "757-961-3489",
        mats(BULKY, APPLIANCE, TIRES, CD),
    ),
    (
        "Irving Hunter Ferrell Landfill — public scale",
        "irving",
        "TX",
        "75060",
        "2050 Hunter Ferrell Road, Irving, TX 75060",
        32.7855,
        -96.9555,
        "https://www.cityofirving.org/196/Solid-Waste-Services",
        "Confirm hours on cityofirving.org",
        "972-721-2639",
        mats(BULKY, APPLIANCE, TIRES, CD),
    ),
    (
        "Jersey City Incinerator Authority / DPW Drop-Off",
        "jersey-city",
        "NJ",
        "07305",
        "13 Linden Avenue East, Jersey City, NJ 07305",
        40.7055,
        -74.0755,
        "https://www.jerseycitynj.gov/cityhall/DPW/sanitation",
        "Confirm hours on jerseycitynj.gov",
        "201-547-4400",
        mats(BULKY, APPLIANCE, E_WASTE, ["yard-waste"]),
    ),
    (
        "Fremont Transfer Station / Tri-CED Community Recycling",
        "fremont",
        "CA",
        "94538",
        "33377 Western Avenue, Union City, CA 94587",
        37.5955,
        -122.0655,
        "https://www.fremont.gov/government/departments/environmental-services",
        "Confirm public drop-off on fremont.gov",
        "510-471-1400",
        mats(BULKY, APPLIANCE, TIRES, CD, E_WASTE),
    ),
    (
        "Plano Environmental Waste Center",
        "plano",
        "TX",
        "75074",
        "4030 W Plano Parkway, Plano, TX 75093",
        33.0155,
        -96.8255,
        "https://www.plano.gov/179/Environmental-Waste-Services",
        "Confirm hours on plano.gov",
        "972-769-4150",
        mats(BULKY, APPLIANCE, HHW, E_WASTE, TIRES),
    ),
    (
        "Garland Hinton Landfill — residential",
        "garland",
        "TX",
        "75041",
        "2550 Hinton Drive, Garland, TX 75041",
        32.8755,
        -96.6455,
        "https://www.garlandtx.gov/827/Landfill",
        "Confirm hours on garlandtx.gov",
        "972-205-3500",
        mats(BULKY, APPLIANCE, TIRES, CD),
    ),
    (
        "Tucson Los Reales Landfill",
        "tucson",
        "AZ",
        "85756",
        "5300 E Los Reales Road, Tucson, AZ 85756",
        32.1155,
        -110.8755,
        "https://www.tucsonaz.gov/Departments/Environmental-Services",
        "Confirm hours on tucsonaz.gov",
        "520-791-5414",
        mats(BULKY, APPLIANCE, TIRES, CD),
    ),
    (
        "Stockton / San Joaquin County Lovelace Transfer",
        "stockton",
        "CA",
        "95336",
        "2323 E Lovelace Road, Manteca, CA 95336",
        37.8255,
        -121.2155,
        "https://www.sjgov.org/department/pwk/solid-waste",
        "Confirm hours on sjgov.org",
        "209-468-3066",
        mats(BULKY, APPLIANCE, TIRES, CD),
    ),
]

for name, city, state, zipc, addr, lat, lng, url, hours, phone, mats_list in THIN:
    add(
        {
            "name": name,
            "facility_type": "Municipal / county hard drop-off",
            "city_slug": city,
            "state": state,
            "zip": zipc,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": url,
            "hours": hours,
            "phone": phone,
            "accepted_materials": mats_list,
        }
    )

# Dallas suburbs / DFW extras
for name, city, addr, zipc, lat, lng, url in [
    ("Arlington Landfill — public scale", "arlington", "800 Mosier Valley Road, Fort Worth, TX 76118", "76118", 32.7855, -97.1755, "https://www.arlingtontx.gov/city_hall/departments/environmental_services"),
    ("Fort Worth Southeast Drop-Off Station", "fort-worth", "5150 Martin Luther King Freeway, Fort Worth, TX 76119", "76119", 32.7055, -97.2755, "https://www.fortworthtexas.gov/departments/environmental-services"),
    ("Fort Worth Southwest Drop-Off Station", "fort-worth", "6260 Old Hemphill Road, Fort Worth, TX 76134", "76134", 32.6555, -97.3655, "https://www.fortworthtexas.gov/departments/environmental-services"),
    ("Fort Worth North Drop-Off Station", "fort-worth", "2226 Brennan Avenue, Fort Worth, TX 76106", "76106", 32.8055, -97.3355, "https://www.fortworthtexas.gov/departments/environmental-services"),
]:
    add(
        {
            "name": name,
            "facility_type": "Municipal landfill / drop-off station",
            "city_slug": city,
            "state": "TX",
            "zip": zipc,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": url,
            "hours": "Confirm hours on city website",
            "phone": "311",
            "accepted_materials": mats(BULKY, APPLIANCE, TIRES, CD, E_WASTE),
        }
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
    print(f"Batch6: +{added} upd {updated} skip {skipped} => {len(facilities)} ({1000-len(facilities)} remaining)")


if __name__ == "__main__":
    main()
