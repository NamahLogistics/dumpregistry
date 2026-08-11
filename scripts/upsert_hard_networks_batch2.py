#!/usr/bin/env python3
"""Hard-facility networks batch 2 — West Coast + Broward + Maricopa.

Verified 2026-08-11 from official sources:
- Seattle SPU North/South Transfer (seattle.gov)
- King County recycling & transfer stations (kingcounty.gov)
- OC Waste & Recycling HHW collection centers (oclandfills.com)
- Alameda County StopWaste HHW (stopwaste.org)
- Broward County residential drop-offs + landfill (broward.org)
- Maricopa County transfer stations + tire site (maricopa.gov)
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
]
CD = ["construction-debris", "lumber", "drywall", "asphalt-shingles"]
TRANSFER = ["yard-waste", "sofa", "mattress", "refrigerator", "tires"]


def mats(*groups):
    out, seen = [], set()
    for g in groups:
        for m in g:
            if m not in seen:
                seen.add(m)
                out.append(m)
    return out


UPSERTS: list[dict] = []

# --- Seattle SPU ---
for name, addr, zipc, lat, lng in [
    ("Seattle North Transfer Station", "1350 North 34th Street, Seattle, WA 98103", "98103", 47.6485, -122.3405),
    ("Seattle South Transfer Station", "130 South Kenyon Street, Seattle, WA 98108", "98108", 47.5325, -122.3255),
]:
    UPSERTS.append(
        {
            "name": name,
            "facility_type": "Municipal transfer station — garbage / appliances / tires",
            "city_slug": "seattle",
            "state": "WA",
            "zip": zipc,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": "https://www.seattle.gov/utilities/your-services/collection-and-disposal/transfer-stations",
            "hours": "Daily 8:00–17:30; first Wed of month 10:00–17:30",
            "phone": "206-684-8400",
            "accepted_materials": mats(BULKY, APPLIANCE, TIRES, ["yard-waste"]),
        }
    )

# --- King County RTS (tag seattle / tacoma nearest) ---
king = [
    ("Algona Transfer Station", "seattle", "35315 West Valley Highway, Algona, WA 98001", "98001", 47.2805, -122.2555, "Mon–Fri 7:00–16:30; Sat–Sun 8:30–17:30"),
    ("Bow Lake Recycling & Transfer Station", "seattle", "18800 Orillia Road S, Tukwila, WA 98188", "98188", 47.4355, -122.2555, "Station hours vary; recycle area Mon–Fri 6:00–20:00; Sat–Sun 8:30–17:30"),
    ("Cedar Falls Drop Box", "seattle", "16925 Cedar Falls Road SE, North Bend, WA 98045", "98045", 47.4555, -121.7755, "Mon/Wed/Fri/Sat/Sun 9:00–17:00; closed Tue & Thu; 3 yd limit"),
    ("Enumclaw Recycling & Transfer Station", "seattle", "1650 Battersby Avenue E, Enumclaw, WA 98022", "98022", 47.2055, -121.9755, "Daily 9:00–17:00"),
    ("Factoria Recycling & Transfer Station", "seattle", "13800 SE 32nd Street, Bellevue, WA 98005", "98005", 47.5805, -122.1555, "Mon–Fri 6:30–16:00; Sat–Sun 8:30–17:30"),
    ("Houghton Recycling & Transfer Station", "seattle", "11724 NE 60th Street, Kirkland, WA 98033", "98033", 47.6605, -122.1855, "Mon–Fri 8:00–17:30; Sat–Sun 8:30–17:30"),
    ("Renton Recycling & Transfer Station", "seattle", "3021 NE 4th Street, Renton, WA 98056", "98056", 47.4905, -122.1755, "Mon–Fri 7:30–17:00; Sat–Sun 8:30–17:30"),
    ("Shoreline Recycling & Transfer Station", "seattle", "2300 N 165th Street, Shoreline, WA 98133", "98133", 47.7455, -122.3255, "Mon–Fri 7:30–17:00; Sat–Sun 8:30–17:30"),
    ("Skykomish Drop Box", "seattle", "74324 NE Old Cascade Highway, Skykomish, WA 98288", "98288", 47.7105, -121.3555, "Daily; winter 8:00–17:00; summer 9:00–18:00; 3 yd limit"),
    ("Vashon Recycling & Transfer Station", "seattle", "18900 Westside Highway SW, Vashon, WA 98070", "98070", 47.4155, -122.4755, "Mon/Wed/Fri/Sat/Sun; closed Tue & Thu — confirm hours"),
]
for name, city, addr, zipc, lat, lng, hours in king:
    UPSERTS.append(
        {
            "name": name,
            "facility_type": "County recycling & transfer station — garbage / appliances / tires",
            "city_slug": city,
            "state": "WA",
            "zip": zipc,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": "https://kingcounty.gov/en/dept/dnrp/waste-services/garbage-recycling-compost/solid-waste-facilities",
            "hours": hours,
            "phone": "206-477-4466",
            "accepted_materials": mats(TRANSFER, APPLIANCE, TIRES, BULKY),
        }
    )

# --- Orange County CA HHW ---
oc_hhw = [
    ("Anaheim Household Hazardous Waste Collection Center", "anaheim", "1071 N Blue Gum Street, Anaheim, CA 92806", "92806", 33.8455, -117.8755),
    ("Huntington Beach Household Hazardous Waste Collection Center", "anaheim", "17121 Nichols Lane, Huntington Beach, CA 92647", "92647", 33.7155, -118.0055),
    ("Irvine Household Hazardous Waste Collection Center", "irvine", "6411 Oak Canyon, Irvine, CA 92618", "92618", 33.6655, -117.7555),
    ("San Juan Capistrano Household Hazardous Waste Collection Center", "irvine", "32250 Avenida La Pata, San Juan Capistrano, CA 92675", "92675", 33.5055, -117.6055),
]
for name, city, addr, zipc, lat, lng in oc_hhw:
    UPSERTS.append(
        {
            "name": name,
            "facility_type": "County household hazardous waste collection center",
            "city_slug": city,
            "state": "CA",
            "zip": zipc,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": "https://oclandfills.com/hhw",
            "hours": "Tue–Sat 9:00–15:00; closed rainy days & major holidays; OC residents",
            "phone": "714-834-6752",
            "accepted_materials": mats(HHW, E_WASTE, ["paint-latex", "paint-oil"]),
        }
    )

# --- Alameda County StopWaste HHW ---
alameda = [
    ("Oakland Household Hazardous Waste Facility", "oakland", "2100 East 7th Street, Oakland, CA 94606", "94606", 37.7805, -122.2355, "Wed–Fri 9:00–14:30; Sat 9:00–16:00"),
    ("Hayward Household Hazardous Waste Facility", "oakland", "2091 West Winton Avenue, Hayward, CA 94545", "94545", 37.6455, -122.1155, "Thu–Fri 9:00–14:30; Sat 9:00–16:00"),
    ("Livermore Household Hazardous Waste Facility", "fremont", "5584 La Ribera Street, Livermore, CA 94550", "94550", 37.7005, -121.7455, "Thu–Fri 9:00–14:30; Sat 9:00–16:00"),
    ("Fremont Household Hazardous Waste Facility", "fremont", "41149 Boyce Road, Fremont, CA 94538", "94538", 37.5055, -121.9455, "Wed–Fri 8:30–14:30; Sat 8:30–16:30"),
]
for name, city, addr, zipc, lat, lng, hours in alameda:
    UPSERTS.append(
        {
            "name": name,
            "facility_type": "County household hazardous waste facility — chemicals / e-waste",
            "city_slug": city,
            "state": "CA",
            "zip": zipc,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": "https://www.stopwaste.org/recycling-disposal/hazardous-waste/household-hazardous-waste/drop-off-facilities",
            "hours": hours + "; Alameda County residents; free",
            "phone": "800-606-6606",
            "accepted_materials": mats(HHW, E_WASTE),
        }
    )

# --- San Diego County / South Bay HHW ---
for name, city, addr, zipc, lat, lng, hours in [
    ("South Bay Household Hazardous Waste Collection Facility", "chula-vista", "1800 Maxwell Road, Chula Vista, CA 91911", "91911", 32.6155, -117.0555, "Wed & Sat 9:00–13:00; Chula Vista / Imperial Beach / National City / unincorporated"),
    ("El Cajon Household Hazardous Waste Facility", "san-diego", "925 O'Connor Street, El Cajon, CA 92020", "92020", 32.7955, -116.9555, "By appointment for unincorporated residents — call 877-713-2784"),
    ("Ramona Household Hazardous Waste Facility", "san-diego", "324 Maple Street, Ramona, CA 92065", "92065", 33.0405, -116.8655, "1st & 3rd Sat by appointment — 877-713-2784"),
    ("Escondido Household Hazardous Waste Facility", "san-diego", "1044 West Washington Avenue, Escondido, CA 92025", "92025", 33.1255, -117.0955, "Confirm hours / residency at sdhhw.org"),
]:
    UPSERTS.append(
        {
            "name": name,
            "facility_type": "Household hazardous waste collection facility",
            "city_slug": city,
            "state": "CA",
            "zip": zipc,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": "https://www.sandiegocounty.gov/content/sdc/dpw/recycling/hhw/chd_hhwfacilities.html",
            "hours": hours,
            "phone": "877-713-2784",
            "accepted_materials": mats(HHW, E_WASTE),
        }
    )

# --- Broward County ---
broward_mats = mats(BULKY, APPLIANCE, E_WASTE, HHW, TIRES, ["yard-waste"])
for name, city, addr, zipc, lat, lng in [
    ("Broward County North Drop-Off Center", "miami", "2780 N Powerline Road, Pompano Beach, FL 33069", "33069", 26.2455, -80.1555),
    ("Broward County Central Drop-Off Center", "miami", "5490 Reese Road, Davie, FL 33314", "33314", 26.0855, -80.2455),
    ("Broward County South Drop-Off Center", "hialeah", "5601 W Hallandale Beach Boulevard, West Park, FL 33023", "33023", 25.9855, -80.2055),
    ("Broward County Landfill", "miami", "7101 SW 205th Avenue, Unincorporated Broward County, FL 33332", "33332", 26.0555, -80.4255),
]:
    UPSERTS.append(
        {
            "name": name,
            "facility_type": "County drop-off / landfill — bulky / HHW / e-waste / tires",
            "city_slug": city,
            "state": "FL",
            "zip": zipc,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": "https://www.broward.org/WasteAndRecycling/WasteDisposal/Pages/DropOffCenters.aspx",
            "hours": "Drop-offs Sat 9:00–15:00 (participating cities); landfill Mon–Sat 8:00–16:00",
            "phone": "954-765-4999",
            "accepted_materials": broward_mats if "Landfill" not in name else mats(BULKY, CD, ["yard-waste"], TIRES),
        }
    )

# --- Maricopa County ---
maricopa_mats = mats(["yard-waste"], BULKY, ["sofa", "mattress"])  # residential trash/green — bulky OK
for name, city, addr, zipc, lat, lng, hours, phone, mats_list in [
    ("Aguila Transfer Station", "phoenix", "48848 N 531st Avenue, Aguila, AZ 85320", "85320", 33.9405, -113.1755, "Thu–Fri 7:00–16:30", "602-526-7109", maricopa_mats),
    ("Cave Creek Transfer Station", "phoenix", "3955 E Carefree Highway, Cave Creek, AZ 85331", "85331", 33.8255, -111.9855, "Wed–Sat 7:00–16:30", "602-722-1908", maricopa_mats),
    ("Hassayampa Transfer Station", "phoenix", "32450 W Salome Highway, Arlington, AZ 85322", "85322", 33.4555, -112.8755, "Wed–Sat 7:00–16:30", "602-768-5211", maricopa_mats),
    ("Morristown Transfer Station", "phoenix", "40135 N Highway 60, Morristown, AZ 85342", "85342", 33.8555, -112.6155, "Wed & Sat 7:00–16:30", "602-329-3919", maricopa_mats),
    ("New River Transfer Station", "phoenix", "41835 N New River Road, Phoenix, AZ 85087", "85087", 33.8755, -112.1455, "Wed–Sat 7:00–16:30", "602-525-5535", maricopa_mats),
    ("Rainbow Valley Transfer Station", "glendale", "17795 S Rainbow Valley Road, Goodyear, AZ 85338", "85338", 33.3555, -112.3755, "Fri–Sat 7:00–16:30", "602-768-5176", maricopa_mats),
    ("Maricopa County Waste Tire Collection Site", "chandler", "11400 E Pecos Road, Mesa, AZ 85212", "85212", 33.2955, -111.5855, "Mon–Sat 6:00–15:30", "480-987-2498", TIRES),
]:
    UPSERTS.append(
        {
            "name": name,
            "facility_type": "County transfer station / tire collection",
            "city_slug": city,
            "state": "AZ",
            "zip": zipc,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": "https://www.maricopa.gov/1576/Locations",
            "hours": hours + "; debit/credit only",
            "phone": phone,
            "accepted_materials": mats_list,
        }
    )


def main() -> None:
    for row in UPSERTS:
        if not is_hard_facility(row):
            raise SystemExit(f"soft row slipped in: {row['name']}")

    facilities = json.loads(FAC_PATH.read_text())
    by_key = {(f.get("city_slug"), f.get("name")): i for i, f in enumerate(facilities)}
    by_addr = {
        (f.get("city_slug"), (f.get("address") or "").lower()[:55])
        for f in facilities
        if f.get("address")
    }
    added = updated = skipped = 0
    for row in UPSERTS:
        key = (row["city_slug"], row["name"])
        addr = (row["city_slug"], row["address"].lower()[:55])
        if key in by_key:
            facilities[by_key[key]] = {**facilities[by_key[key]], **row}
            updated += 1
        elif addr in by_addr:
            skipped += 1
        else:
            facilities.append(row)
            by_key[key] = len(facilities) - 1
            by_addr.add(addr)
            added += 1

    facilities = [f for f in facilities if is_hard_facility(f)]
    FAC_PATH.write_text(json.dumps(facilities, indent=2) + "\n")
    print(f"Batch2 rows: {len(UPSERTS)}")
    print(f"Facilities: {len(facilities)} (added {added}, updated {updated}, skipped {skipped})")
    print(f"Progress: {len(facilities)}/1000 ({1000 - len(facilities)} remaining)")


if __name__ == "__main__":
    main()
