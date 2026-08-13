#!/usr/bin/env python3
"""Fill the top-30 density hole: Washington, D.C. had one facility.

Adds official DC DPW special-waste events plus the Montgomery / Fairfax /
Prince George's drop-offs the metro actually uses. Does not invent a
countywide DC HHW plant. Does not list Benning Road or the closed PG HHW lot
as open. No new city (not city 301).
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAC_PATH = ROOT / "data" / "facilities" / "all.json"
ITEMS = {i["slug"] for i in json.loads((ROOT / "data" / "items.json").read_text())}

HHW = [
    "paint-latex",
    "paint-oil",
    "pesticides",
    "herbicides",
    "pool-chemicals",
    "gasoline",
    "motor-oil",
    "antifreeze",
    "car-battery",
    "household-batteries",
    "lithium-battery",
    "fluorescent-bulbs",
    "propane-tank",
    "cooking-oil",
]
E_WASTE = [
    "television",
    "computer-monitor",
    "laptop",
    "desktop-computer",
    "printer",
    "tablet",
    "smartphone",
    "microwave",
    "hard-drive",
    "e-waste-mixed",
]
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
TIRES = ["tires"]


def mats(*groups):
    out, seen = [], set()
    for g in groups:
        for m in g:
            if m not in ITEMS:
                raise SystemExit(f"bad slug {m}")
            if m not in seen:
                seen.add(m)
                out.append(m)
    return out


UPSERTS = [
    {
        "name": "Fort Totten Transfer Station",
        "facility_type": "Municipal transfer station — bulky / trash / recycling",
        "city_slug": "washington",
        "state": "DC",
        "zip": "20011",
        "address": "4900 John McCormack Road NE, Washington, DC 20011",
        "lat": 38.9486,
        "lng": -77.0078,
        "source_url": "https://dpw.dc.gov/service/fort-totten-transfer-station",
        "hours": "Residents: Tue–Fri 10:00–14:00; Sat 7:00–14:00. Confirm on dpw.dc.gov. No HHW or e-waste.",
        "phone": "311",
        "accepted_materials": mats(BULKY, APPLIANCE, TIRES, ["yard-waste"]),
    },
    {
        "name": "DC DPW Special Waste Collection — RFK Parking Lot 8",
        "facility_type": "Municipal HHW / e-waste collection event",
        "city_slug": "washington",
        "state": "DC",
        "zip": "20003",
        "address": "RFK Parking Lot 8, 2500 Independence Avenue SE, Washington, DC 20003",
        "lat": 38.8822,
        "lng": -76.9714,
        "source_url": "https://dpw.dc.gov/service/household-hazardous-waste-hhw-e-cycling-document-shredding",
        "hours": "Posted Thursday and Saturday events; registration required. DC residents only. Confirm the calendar on dpw.dc.gov.",
        "phone": "311",
        "accepted_materials": mats(HHW, E_WASTE),
    },
    {
        "name": "Montgomery County Shady Grove Transfer Station",
        "facility_type": "County transfer station — bulky / trash / recycling",
        "city_slug": "washington",
        "state": "MD",
        "zip": "20855",
        "address": "16101 Frederick Road, Derwood, MD 20855",
        "lat": 39.1184,
        "lng": -77.1762,
        "source_url": "https://www.montgomerycountymd.gov/department-environmental-protection/trash-recycling-yard-trim/trash-drop-hours-events",
        "hours": "Confirm residential hours on montgomerycountymd.gov. Montgomery County residents.",
        "phone": "(240) 777-6410",
        "accepted_materials": mats(BULKY, APPLIANCE, ["yard-waste", "construction-debris"]),
    },
    {
        "name": "Montgomery County Household Hazardous Waste — Shady Grove",
        "facility_type": "County HHW drop-off",
        "city_slug": "washington",
        "state": "MD",
        "zip": "20855",
        "address": "Shady Grove HHW compound, 16101 Frederick Road, Derwood, MD 20855",
        "lat": 39.1191,
        "lng": -77.1754,
        "source_url": "https://www.montgomerycountymd.gov/department-environmental-protection/trash-recycling-yard-trim/trash-recycling-facilities/shady-grove-processing-facility-transfer-station/hazardous-waste-drop",
        "hours": "Open with transfer-station hours for residents. Enter from Frederick Road / Route 355 and follow Recycling / HHW signs.",
        "phone": "(240) 777-6587",
        "accepted_materials": mats(HHW),
    },
    {
        "name": "Fairfax County I-66 Transfer Station / HHW",
        "facility_type": "County transfer / HHW",
        "city_slug": "washington",
        "state": "VA",
        "zip": "22030",
        "address": "4618 West Ox Road, Fairfax, VA 22030",
        "lat": 38.8594,
        "lng": -77.3721,
        "source_url": "https://www.fairfaxcounty.gov/publicworks/recycling-trash/I-66-transfer-station",
        "hours": "Confirm residential and HHW hours on fairfaxcounty.gov. Fairfax County residents.",
        "phone": "(703) 631-1179",
        "accepted_materials": mats(BULKY, APPLIANCE, HHW, E_WASTE, ["yard-waste"]),
    },
    {
        "name": "Fairfax County I-95 Landfill Complex / HHW — Lorton",
        "facility_type": "County landfill / HHW",
        "city_slug": "washington",
        "state": "VA",
        "zip": "22079",
        "address": "9850 Furnace Road, Lorton, VA 22079",
        "lat": 38.6952,
        "lng": -77.2374,
        "source_url": "https://www.fairfaxcounty.gov/publicworks/recycling-trash/household-hazardous-waste",
        "hours": "Confirm HHW and landfill hours on fairfaxcounty.gov. Fairfax County residents.",
        "phone": "(703) 690-1703",
        "accepted_materials": mats(BULKY, APPLIANCE, HHW, E_WASTE),
    },
    {
        "name": "Prince George's County Brown Station Road Convenience Center",
        "facility_type": "County convenience center — bulky / e-waste / oil",
        "city_slug": "washington",
        "state": "MD",
        "zip": "20772",
        "address": "3501 Brown Station Road, Upper Marlboro, MD 20772",
        "lat": 38.8312,
        "lng": -76.7654,
        "source_url": "https://www.princegeorgescountymd.gov/departments-offices/environment/waste-recycling",
        "hours": "Mon–Sat 7:00–18:00. The landfill HHW lot is closed for construction — HHW is event-only. Confirm on princegeorgescountymd.gov.",
        "phone": "311",
        "accepted_materials": mats(BULKY, APPLIANCE, E_WASTE, ["motor-oil", "cooking-oil"]),
    },
]


def main() -> None:
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
    FAC_PATH.write_text(json.dumps(facilities, indent=2) + "\n")
    dc = [f for f in facilities if f.get("city_slug") == "washington"]
    print(f"Facilities: {len(facilities)} (added {added}, updated {updated}, skipped {skipped})")
    print(f"washington density: {len(dc)}")


if __name__ == "__main__":
    main()
