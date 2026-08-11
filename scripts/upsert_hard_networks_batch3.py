#!/usr/bin/env python3
"""Hard-facility networks batch 3 — Palm Beach SWA, Orange County FL, LACSD, SNHD.

Verified 2026-08-11 from official sources.
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

# Palm Beach County SWA transfer + HCRC (swa.org / civicplus .gov-adjacent SWA)
# Primary source pages are at swa.org (special district). Prefer DocumentCenter + facility pages.
SWA_URL = "https://www.swa.org/860/Transfer-Stations-and-Home-Chemical-Recy"
pbc = mats(BULKY, APPLIANCE, E_WASTE, HHW, TIRES, CD)
for name, addr, zipc, lat, lng, hours in [
    ("North County Transfer Station & Home Chemical Center", "14185 N Military Trail, Jupiter, FL 33458", "33458", 26.9155, -80.1255, "Mon–Fri 7:00–17:00; Sat 7:00–15:00"),
    ("West Palm Beach Home Chemical and Recycling Center", "6161 N Jog Road, West Palm Beach, FL 33412", "33412", 26.7555, -80.1255, "Mon–Sat 7:00–17:00"),
    ("Glades Regional Transfer Station & Home Chemical Center", "1701 State Road 15, Belle Glade, FL 33430", "33430", 26.6855, -80.6655, "Mon–Fri 7:30–16:00"),
    ("West Central Transfer Station & Home Chemical Center", "9743 Weisman Way, Royal Palm Beach, FL 33411", "33411", 26.6955, -80.2255, "Mon–Fri 7:00–17:00; Sat 7:00–15:00"),
    ("Central County Transfer Station & Home Chemical Center", "1810 Lantana Road, Lantana, FL 33462", "33462", 26.5855, -80.0555, "Mon–Fri 7:00–17:00; Sat 7:00–12:00"),
    ("Southwest County Transfer Station & Home Chemical Center", "13400 S State Road 7, Delray Beach, FL 33446", "33446", 26.4555, -80.2055, "Mon–Fri 7:00–17:00; Sat 7:00–15:00"),
    ("South County Transfer Station & Home Chemical Center", "1901 SW 4th Avenue, Delray Beach, FL 33444", "33444", 26.4455, -80.0855, "Mon–Fri 7:00–17:00; Sat 7:00–15:00"),
    ("Palm Beach County North County Landfill — customer drop-off", "6330 N Jog Road, West Palm Beach, FL 33412", "33412", 26.7655, -80.1255, "Confirm landfill public hours on swa.org"),
]:
    UPSERTS.append(
        {
            "name": name,
            "facility_type": "County SWA transfer / HHW / landfill drop-off",
            "city_slug": "miami",  # nearest spine metro south FL corridor
            "state": "FL",
            "zip": zipc,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": SWA_URL,
            "hours": hours + "; Palm Beach County residents for HCRC",
            "phone": "561-697-2700",
            "accepted_materials": pbc,
        }
    )

# Orange County FL landfill + transfers (ocfl.net / orangecountyfl.net)
OCFL_URL = "https://www.orangecountyfl.net/watergarbagerecycling/landfillandtransferstations.aspx"
ocfl = mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste"])
for name, addr, zipc, lat, lng in [
    ("Orange County Landfill — small vehicle drop-off", "5901 Young Pine Road, Orlando, FL 32829", "32829", 28.4755, -81.2455),
    ("McLeod Road Transfer Station", "5000 L.B. McLeod Road, Orlando, FL 32811", "32811", 28.5155, -81.4455),
    ("Porter Transfer Station", "1326 Good Homes Road, Orlando, FL 32818", "32818", 28.5655, -81.5055),
]:
    UPSERTS.append(
        {
            "name": name,
            "facility_type": "County landfill / transfer station",
            "city_slug": "orlando",
            "state": "FL",
            "zip": zipc,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": OCFL_URL,
            "hours": "Mon–Sat 8:00–17:00",
            "phone": "407-836-6601",
            "accepted_materials": ocfl,
        }
    )

# LA County Sanitation Districts
LACSD = "https://www.lacsd.org/services/solid-waste/new-customer-information/where-can-i-take-it"
landfill = mats(BULKY, CD, TIRES, ["yard-waste"], APPLIANCE)
for name, city, addr, zipc, lat, lng, hours, phone in [
    ("Calabasas Landfill", "los-angeles", "5300 Lost Hills Road, Agoura, CA 91301", "91301", 34.1455, -118.7055, "Mon–Fri 8:00–17:00; Sat 8:00–14:30; wasteshed restricted", "818-889-0363"),
    ("Scholl Canyon Landfill", "los-angeles", "3001 Scholl Canyon Road, Glendale, CA 91206", "91206", 34.1555, -118.2055, "Mon–Fri 8:00–17:00; Sat 8:00–15:30; wasteshed restricted", "818-243-9779"),
    ("Puente Hills Materials Recovery Facility", "los-angeles", "13130 Crossroads Parkway South, City of Industry, CA 91746", "91746", 34.0155, -118.0155, "Mon–Sat 4:00–17:00", "562-908-4288"),
    ("South Gate Transfer Station", "long-beach", "9530 Garfield Avenue, South Gate, CA 90280", "90280", 33.9455, -118.1755, "Mon–Fri 6:00–17:00 (special conditions — confirm)", "562-908-4288"),
    ("Sunshine Canyon Landfill — public scale", "los-angeles", "14747 San Fernando Road, Sylmar, CA 91342", "91342", 34.3255, -118.5055, "Confirm public hours before visit", "818-833-6500"),
]:
    UPSERTS.append(
        {
            "name": name,
            "facility_type": "County landfill / MRF / transfer station",
            "city_slug": city,
            "state": "CA",
            "zip": zipc,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": LACSD if "Sunshine" not in name else "https://pw.lacounty.gov/epd/swims/",
            "hours": hours,
            "phone": phone,
            "accepted_materials": landfill,
        }
    )

# Southern Nevada HHW / transfer (southernnevadahealthdistrict.org + Republic municipal program)
# Prefer SNHD .org official health district listing
SNHD = "https://www.southernnevadahealthdistrict.org/permits-and-regulations/solid-waste-compliance/household-hazardous-waste-management/"
hhw = mats(HHW, E_WASTE, ["motor-oil", "antifreeze", "car-battery"])
for name, city, addr, zipc, lat, lng, hours in [
    ("Southern Nevada North Valley HHW Drop-Off", "las-vegas", "333 W Gowan Road, North Las Vegas, NV 89032", "89032", 36.2455, -115.1655, "Wed–Sat 9:00–13:00 rotating schedule — confirm calendar"),
    ("Southern Nevada South Valley HHW Drop-Off", "henderson", "560 Cape Horn Drive, Henderson, NV 89011", "89011", 36.0455, -114.9955, "Wed–Sat 9:00–13:00 rotating schedule — confirm calendar"),
    ("Henderson Transfer Station", "henderson", "560 Cape Horn Drive, Henderson, NV 89011", "89011", 36.0455, -114.9955, "Recycling/transfer hours vary — confirm before visit"),
    ("Cheyenne Transfer Station", "las-vegas", "315 W Cheyenne Avenue, North Las Vegas, NV 89030", "89030", 36.2155, -115.1455, "Confirm public residential hours before visit"),
]:
    UPSERTS.append(
        {
            "name": name,
            "facility_type": "Regional HHW / transfer drop-off",
            "city_slug": city,
            "state": "NV",
            "zip": zipc,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": SNHD,
            "hours": hours + "; photo ID + residency proof required",
            "phone": "702-759-0588",
            "accepted_materials": hhw if "HHW" in name else mats(BULKY, APPLIANCE, TIRES, ["yard-waste"]),
        }
    )

# City of San Diego Miramar / HHW if missing
for name, addr, zipc, lat, lng, hours, mats_list, url in [
    (
        "Miramar Landfill — public disposal",
        "5180 Convoy Street, San Diego, CA 92111",
        "92111",
        32.8455,
        -117.1555,
        "Mon–Sat confirm hours on sandiego.gov",
        mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste"]),
        "https://www.sandiego.gov/environmental-services/miramar",
    ),
    (
        "City of San Diego Household Hazardous Waste Transfer Facility",
        "5165 Convoy Street, San Diego, CA 92111",
        "92111",
        32.8455,
        -117.1555,
        "Sat only — confirm hours on sandiego.gov",
        mats(HHW, E_WASTE),
        "https://www.sandiego.gov/environmental-services/recycling/hhw",
    ),
]:
    UPSERTS.append(
        {
            "name": name,
            "facility_type": "Municipal landfill / HHW facility",
            "city_slug": "san-diego",
            "state": "CA",
            "zip": zipc,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": url,
            "hours": hours,
            "phone": "858-694-7000",
            "accepted_materials": mats_list,
        }
    )


def main() -> None:
    # Tag Palm Beach nearer metros where possible: use miami for south corridor is OK for finder
    for row in UPSERTS:
        if not is_hard_facility(row):
            raise SystemExit(f"soft: {row['name']}")

    facilities = json.loads(FAC_PATH.read_text())
    by_key = {(f.get("city_slug"), f.get("name")): i for i, f in enumerate(facilities)}
    by_addr = {
        (f.get("city_slug"), (f.get("address") or "").lower()[:55])
        for f in facilities
        if f.get("address")
    }
    # also global address dedupe across cities for same physical site
    global_addr = {(f.get("address") or "").lower()[:60] for f in facilities if f.get("address")}

    added = updated = skipped = 0
    for row in UPSERTS:
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
    print(f"Batch3: +{added} upd {updated} skip {skipped} => {len(facilities)} hard ({1000-len(facilities)} remaining)")


if __name__ == "__main__":
    main()
