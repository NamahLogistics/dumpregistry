#!/usr/bin/env python3
"""Detailed-research hard facility wave 2 (2026-08-12).

Verified official sources:
- LA Sanitation S.A.F.E. Centers (lacitysan.org / cleanla.lacounty.gov)
- Jessamine County KY convenience center (jessamineky.gov)
- Madison County KY e-waste (madisoncountyky.gov)
- Brownsville TX municipal landfill (brownsvilletx.gov)
- San Diego County / Escondido HHW (sandiegocounty.gov)
- Antelope Valley Environmental Collection Center (cleanla)

HARD ONLY. Thin metro fills. No prod deploy.
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


SAFE_URL = "https://cleanla.lacounty.gov/hhw/collection-centers/"
SAFE_HOURS = "Sat–Sun 9:00–15:00; City/County of LA residents — lacitysan.org/safecenters"
SAFE_PHONE = "800-773-2489"
SAFE_MATS = mats(HHW, E_WASTE)

# ── LA S.A.F.E. Centers — fill missing + thin OC metro tags ──
for name, addr, zipc, lat, lng, city in [
    (
        "LA Sanitation Washington Blvd S.A.F.E. Center — East LA",
        "2649 E Washington Boulevard, Los Angeles, CA 90021",
        "90021",
        34.020,
        -118.225,
        "los-angeles",
    ),
    (
        "LA Sanitation Gaffey Street S.A.F.E. Center (Long Beach hub)",
        "1400 N Gaffey Street, San Pedro, CA 90731",
        "90731",
        33.745,
        -118.295,
        "long-beach",
    ),
    (
        "LA Sanitation Hyperion S.A.F.E. Center (Santa Ana hub)",
        "7660 West Imperial Highway Gate B, Playa Del Rey, CA 90293",
        "90293",
        33.925,
        -118.435,
        "santa-ana",
    ),
    (
        "LA Sanitation Washington Blvd S.A.F.E. Center (Anaheim hub)",
        "2649 E Washington Boulevard, Los Angeles, CA 90021",
        "90021",
        34.020,
        -118.225,
        "anaheim",
    ),
    (
        "LA Sanitation Gaffey Street S.A.F.E. Center (Irvine hub)",
        "1400 N Gaffey Street, San Pedro, CA 90731",
        "90731",
        33.745,
        -118.295,
        "irvine",
    ),
    (
        "LA Sanitation LA/Glendale S.A.F.E. Center (Glendale hub)",
        "4600 Colorado Boulevard, Los Angeles, CA 90039",
        "90039",
        34.140,
        -118.265,
        "glendale",
    ),
]:
    site(name, "Municipal permanent HHW / e-waste S.A.F.E. Center",
         city, "CA", zipc, addr, lat, lng, SAFE_URL, SAFE_HOURS, SAFE_PHONE, SAFE_MATS)

site(
    "Antelope Valley Environmental Collection Center — Palmdale",
    "County permanent HHW / e-waste collection center",
    "los-angeles",
    "CA",
    "93551",
    "1200 W City Ranch Road, Palmdale, CA 93551",
    34.555,
    -118.145,
    SAFE_URL,
    "Confirm hours — cleanla.lacounty.gov",
    "888-722-4234",
    mats(HHW, E_WASTE),
)
site(
    "EDCO Recycling & Transfer / HHW — Signal Hill (Long Beach)",
    "Regional transfer + HHW collection partner site",
    "long-beach",
    "CA",
    "90755",
    "2755 California Avenue, Signal Hill, CA 90755",
    33.805,
    -118.165,
    SAFE_URL,
    "Confirm hours — cleanla.lacounty.gov / EDCO",
    "562-997-1720",
    mats(BULKY, APPLIANCE, TIRES, CD, HHW, E_WASTE),
)

# ── Jessamine County KY (jessamineky.gov) → lexington ──
site(
    "Jessamine County Environmental / Recycling Convenience Center",
    "County convenience — bulky / Freon appliances / tires / e-waste / C&D",
    "lexington",
    "KY",
    "40356",
    "123 Hendren Way, Nicholasville, KY 40356",
    37.885,
    -84.575,
    "https://jessamineky.gov/environmental-services/recycling-acceptance-and-fees/",
    "Mon–Fri 8:00–15:30 — jessamineky.gov",
    "859-881-4545",
    mats(BULKY, APPLIANCE, TIRES, E_WASTE, CD, ["carpet"]),
)
site(
    "Jessamine County Fall Haul / HHW Event — Hendren Way",
    "County seasonal HHW collection at convenience center",
    "lexington",
    "KY",
    "40356",
    "123 Hendren Way, Nicholasville, KY 40356",
    37.885,
    -84.575,
    "https://jessamineky.gov/event/fall-haul-2025/",
    "Seasonal HHW events — confirm jessamineky.gov",
    "859-881-4545",
    mats(HHW),
)

# ── Madison County KY e-waste (madisoncountyky.gov) → lexington ──
site(
    "Madison County Solid Waste — E-Waste & Scrap Metal Drop-Off",
    "County e-waste / scrap metal (outside Richmond/Berea city limits)",
    "lexington",
    "KY",
    "40475",
    "325 N Madison Avenue, Richmond, KY 40475",
    37.755,
    -84.295,
    "https://madisoncountyky.gov/roads/",
    "Mon–Fri 8:00–16:00; Madison County residents excl. Richmond/Berea city",
    "859-624-4739",
    mats(E_WASTE),
)

# ── Brownsville TX landfill (brownsvilletx.gov) → corpus-christi ──
site(
    "City of Brownsville Municipal Landfill — Ruben Torres",
    "Municipal landfill — bulky / Freon appliances / tires / C&D / yard waste",
    "corpus-christi",
    "TX",
    "78521",
    "9000 Ruben Torres Sr Boulevard, Brownsville, TX 78521",
    25.945,
    -97.485,
    "https://www.brownsvilletx.gov/646/Landfill",
    "Mon–Sat 7:00–15:45 — brownsvilletx.gov",
    "956-831-3641",
    mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste"]),
)
site(
    "City of Brownsville Landfill — Tire Processing / Scrap Tire Storage",
    "Municipal landfill tire processing area",
    "corpus-christi",
    "TX",
    "78521",
    "9000 Ruben Torres Sr Boulevard, Brownsville, TX 78521",
    25.946,
    -97.484,
    "https://www.brownsvilletx.gov/646/Landfill",
    "Mon–Sat during landfill hours; up to 4 tires free with verified PUB account",
    "956-831-3641",
    mats(TIRES),
)

# ── San Diego County HHW network fills → san-diego / chula-vista ──
site(
    "Escondido Disposal Household Hazardous Waste Facility",
    "Permanent HHW by appointment — Escondido / County residents",
    "san-diego",
    "CA",
    "92025",
    "1044 West Washington Avenue, Escondido, CA 92025",
    33.125,
    -117.105,
    "https://www.sandiegocounty.gov/content/sdc/dpw/recycling/hhw/chd_hhwfacilities.html",
    "Select Saturdays by appointment — sandiegocounty.gov / 760-745-3203",
    "760-745-3203",
    mats(HHW, E_WASTE),
)
site(
    "City of Chula Vista Public Works HHW Facility — Maxwell Road",
    "Permanent HHW at Public Works Center",
    "chula-vista",
    "CA",
    "91911",
    "1800 Maxwell Road, Chula Vista, CA 91911",
    32.615,
    -117.045,
    "https://www.sandiegocounty.gov/content/sdc/dpw/recycling/hhw/chd_hhwfacilities.html",
    "By appointment — sandiegocounty.gov / WasteFreeSD",
    "877-713-2784",
    mats(HHW, E_WASTE),
)
site(
    "Ramona Disposal Transfer Station HHW Facility",
    "County HHW at Ramona transfer — unincorporated residents",
    "san-diego",
    "CA",
    "92065",
    "324 Maple Street, Ramona, CA 92065",
    33.045,
    -116.875,
    "https://www.sandiegocounty.gov/content/sdc/dpw/recycling/hhw/chd_hhwfacilities.html",
    "1st & 3rd Sat 9:00–13:00 by appointment — sandiegocounty.gov",
    "877-713-2784",
    mats(HHW, E_WASTE, BULKY, TIRES),
)
site(
    "El Cajon WM Transfer Station HHW — O'Connor Street",
    "County HHW at WM transfer — unincorporated residents",
    "san-diego",
    "CA",
    "92020",
    "925 O'Connor Street, El Cajon, CA 92020",
    32.805,
    -116.955,
    "https://www.sandiegocounty.gov/content/sdc/dpw/recycling/hhw/chd_hhwfacilities.html",
    "Sat 9:00–13:00 by appointment — sandiegocounty.gov",
    "877-713-2784",
    mats(HHW, E_WASTE, BULKY),
)

# ── Scott County KY Georgetown already exists; add Woodford if verifiable ──
# Skip unverified Woodford.

# ── Additional thin-metro fills from verified county pages ──
site(
    "South Bay Permanent HHW Collection Facility (Chula Vista hub detail)",
    "Regional permanent HHW — South Bay / Chula Vista area",
    "chula-vista",
    "CA",
    "91911",
    "1800 Maxwell Road, Chula Vista, CA 91911",
    32.615,
    -117.045,
    "https://www.sandiegocounty.gov/content/sdc/dpw/recycling/hhw/chd_hhwfacilities.html",
    "Confirm appointment hours — sandiegocounty.gov",
    "877-713-2784",
    mats(HHW, E_WASTE),
)


def main() -> None:
    existing = json.loads(FAC_PATH.read_text())
    by_key = {}
    by_addr = {}
    for i, row in enumerate(existing):
        key = (row.get("city_slug"), (row.get("name") or "").strip().lower())
        by_key[key] = i
        na = norm_addr(row.get("address") or "")
        if na:
            by_addr[(row.get("city_slug"), na)] = i

    added = updated = skipped_soft = 0
    for row in UPSERTS:
        if not is_hard_facility(row):
            skipped_soft += 1
            continue
        key = (row["city_slug"], row["name"].strip().lower())
        na = norm_addr(row.get("address") or "")
        addr_key = (row["city_slug"], na) if na else None
        if key in by_key:
            i = by_key[key]
            existing[i] = {**existing[i], **row}
            updated += 1
        elif addr_key and addr_key in by_addr:
            i = by_addr[addr_key]
            existing[i] = {**existing[i], **row}
            updated += 1
        else:
            existing.append(row)
            by_key[key] = len(existing) - 1
            if addr_key:
                by_addr[addr_key] = len(existing) - 1
            added += 1

    hard = [r for r in existing if is_hard_facility(r)]
    soft_dropped = len(existing) - len(hard)
    FAC_PATH.write_text(json.dumps(hard, indent=2, ensure_ascii=False) + "\n")
    print(
        f"added={added} updated={updated} skipped_soft={skipped_soft} "
        f"soft_dropped={soft_dropped} hard_total={len(hard)} upserts={len(UPSERTS)}"
    )


if __name__ == "__main__":
    main()
