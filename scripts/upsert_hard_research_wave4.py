#!/usr/bin/env python3
"""Detailed-research hard facility wave 4 (2026-08-12).

Focus: thin OC metros (Riverside County public landfills) + Tulsa / Irving fills.
Official sources: rcwaste.org / calrecycle.ca.gov, brokenarrowok.gov, metrecycle.com,
cityoftulsa.org cross-refs.

HARD ONLY. No prod deploy.
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
CITIES_PATH = ROOT / "data" / "geo" / "cities.json"

BULKY = ["mattress", "box-spring", "sofa", "recliner", "carpet", "yard-waste"]
APPLIANCE = [
    "refrigerator", "freezer", "air-conditioner", "washer", "dryer",
    "dishwasher", "stove", "water-heater", "dehumidifier", "microwave",
]
E_WASTE = [
    "television", "computer-monitor", "laptop", "desktop-computer", "printer",
    "tablet", "e-waste-mixed", "smartphone", "hard-drive",
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


UPSERTS: list[dict] = []


def site(name, ftype, city, state, zipc, addr, lat, lng, url, hours, phone, materials):
    UPSERTS.append(
        {
            "name": name,
            "facility_type": ftype,
            "city_slug": city,
            "state": state,
            "zip": zipc,
            "address": addr,
            "lat": lat,
            "lng": lng,
            "source_url": url,
            "hours": hours,
            "phone": phone,
            "accepted_materials": materials,
        }
    )


LANDFILL = mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste"])
TRANSFER = mats(BULKY, APPLIANCE, TIRES, CD, E_WASTE)
HHW_E = mats(HHW, E_WASTE)

RC = "https://rcwaste.org/routine-waste"
RC_LAMB = "https://rcwaste.org/routine-waste/lamb-canyon-landfill"
RC_EL = "https://rcwaste.org/routine-waste/el-sobrante-landfill"
CAL_BAD = "https://www2.calrecycle.ca.gov/SolidWaste/Site/Details/2367"

# Riverside County landfills — public self-haul; hub-tag thin OC metros
for city in ("anaheim", "irvine", "santa-ana"):
    hub = city.replace("-", " ").title()
    site(
        f"Riverside County Badlands Landfill ({hub} hub)",
        "County landfill — public self-haul bulky / C&D / tires",
        city, "CA", "92555",
        "31125 Ironwood Avenue, Moreno Valley, CA 92555",
        33.953, -117.118, CAL_BAD,
        "Mon–Sat 6:00–16:00 typical — rcwaste.org / calrecycle.ca.gov",
        "951-486-3200", LANDFILL,
    )
    site(
        f"Riverside County Lamb Canyon Landfill ({hub} hub)",
        "County landfill — public self-haul bulky / C&D / tires",
        city, "CA", "92223",
        "16411 Lamb Canyon Road, Beaumont, CA 92223",
        33.905, -117.005, RC_LAMB,
        "Mon–Sat 6:00–16:30 — rcwaste.org",
        "951-486-3200", LANDFILL,
    )
    site(
        f"El Sobrante Landfill — public scale ({hub} hub)",
        "Private landfill open to public — bulky / C&D",
        city, "CA", "92883",
        "10910 Dawson Canyon Road, Corona, CA 92883",
        33.805, -117.485, RC_EL,
        "Mon–Sat 6:00–18:00 — rcwaste.org (WM-operated)",
        "951-277-1701", LANDFILL,
    )

# Tulsa fills
site(
    "Tulsa Recycle & Transfer — Peoria (Indoor Dump)",
    "Licensed public transfer — MSW / C&D / recyclables",
    "tulsa", "OK", "74106",
    "1150 N Peoria Avenue, Tulsa, OK 74106",
    36.165, -95.975,
    "https://www.metrecycle.com/transfer-stations",
    "Confirm hours — metrecycle.com / Tulsa Indoor Dump",
    "918-583-3867", TRANSFER,
)
site(
    "Waste Management Quarry Landfill — Broken Arrow passes (Tulsa hub)",
    "Regional landfill — household waste (Broken Arrow landfill passes)",
    "tulsa", "OK", "74116",
    "13720 E 46th Street North, Tulsa, OK 74116",
    36.225, -95.825,
    "https://www.brokenarrowok.gov/government/solid-waste-and-recycling/landfill-passes",
    "Confirm hours — brokenarrowok.gov landfill passes / WM Quarry",
    "918-438-7800", LANDFILL,
)
site(
    "City of Tulsa Household Pollutant Collection Facility — Galveston",
    "Municipal permanent HHW / pollutant drop-off",
    "tulsa", "OK", "74107",
    "4502 S Galveston Avenue, Tulsa, OK 74107",
    36.095, -96.015,
    "https://www.cityoftulsa.org/government/departments/streets-and-stormwater/household-pollutant-collection-facility/",
    "Confirm hours — cityoftulsa.org HPCF; metro voucher via M.e.t.",
    "918-596-9488", HHW_E,
)
site(
    "Rogers County Transfer Station — Claremore (Tulsa hub)",
    "County transfer — residential drop-off",
    "tulsa", "OK", "74017",
    "2404 N Sioux Avenue, Claremore, OK 74017",
    36.335, -95.615,
    "https://www.rogerscounty.org/",
    "Confirm hours — Rogers County solid waste",
    "918-923-4790", TRANSFER,
)

# Irving / DFW collar hard sites (irvingtx.gov / dallascounty.org)
site(
    "City of Irving Hunter Ferrell Landfill — public scale",
    "Municipal landfill — MSW / tires / bulky self-haul",
    "irving", "TX", "75060",
    "110 E Hunter Ferrell Road, Irving, TX 75060",
    32.785, -96.975,
    "https://irvingtx.gov/sws",
    "Confirm hours — irvingtx.gov Solid Waste / Waste Disposal Division",
    "972-721-7322", LANDFILL,
)
site(
    "Dallas County Home Chemical Collection Center (Irving hub)",
    "County permanent HHW / e-waste — Irving residents free",
    "irving", "TX", "75243",
    "11234 Plano Road, Dallas, TX 75243",
    32.905, -96.705,
    "https://www.dallascounty.org/departments/consolidated-services/hhw/",
    "Tue 9:00–19:30; Wed–Thu 8:30–17:00; 2nd & 4th Sat 9:00–15:00 — dallascounty.org",
    "214-553-1765", HHW_E,
)


def main() -> None:
    valid = {c["city_slug"]: c.get("state") for c in json.loads(CITIES_PATH.read_text())}
    for r in UPSERTS:
        if r["city_slug"] not in valid:
            raise SystemExit(f"unknown city_slug: {r['city_slug']}")
        if r.get("state") != valid[r["city_slug"]]:
            raise SystemExit(f"state mismatch: {r['name']}")
        if not is_hard_facility(r):
            raise SystemExit(f"soft rejected: {r['name']}")

    existing = json.loads(FAC_PATH.read_text())
    before = sum(1 for f in existing if is_hard_facility(f))
    by_key, by_addr = {}, {}
    for i, row in enumerate(existing):
        by_key[(row.get("city_slug"), (row.get("name") or "").strip().lower())] = i
        na = norm_addr(row.get("address") or "")
        if na:
            by_addr[(row.get("city_slug"), na)] = i

    added = updated = skipped = 0
    for row in UPSERTS:
        key = (row["city_slug"], row["name"].strip().lower())
        na = norm_addr(row.get("address") or "")
        addr_key = (row["city_slug"], na) if na else None
        if key in by_key:
            existing[by_key[key]] = {**existing[by_key[key]], **row}
            updated += 1
        elif addr_key and addr_key in by_addr:
            skipped += 1
        else:
            existing.append(row)
            by_key[key] = len(existing) - 1
            if addr_key:
                by_addr[addr_key] = len(existing) - 1
            added += 1

    hard = [r for r in existing if is_hard_facility(r)]
    FAC_PATH.write_text(json.dumps(hard, indent=2, ensure_ascii=False) + "\n")
    from collections import Counter
    c = Counter(x["city_slug"] for x in hard)
    print(
        f"added={added} updated={updated} skipped={skipped} "
        f"before={before} hard_total={len(hard)} soft={len(existing)-len(hard)}"
    )
    for s in ("anaheim", "irvine", "santa-ana", "tulsa", "irving"):
        print(f"  {s}: {c[s]}")
    print("thinnest", sorted(c.items(), key=lambda x: x[1])[:8])


if __name__ == "__main__":
    main()
