#!/usr/bin/env python3
"""Detailed-research hard facility wave (2026-08-12).

Verified from official .gov / county authority pages.
Networks: Kitsap WA, Thurston WA, Kent MI SafeChem satellites,
Utah County (North Pointe + South Utah Valley), DeKalb/Cobb GA,
plus Fairfax VA mistag purge from Hampton Roads metros.
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


# ── Kitsap County WA (kitsap.gov/pw) → seattle / tacoma ──
# Sources: Olympic View TS, Hansville/Olalla/Silverdale RAGFs, HHW Imperial Way
KITSAP = "https://www.kitsap.gov/pw/Pages/wastefacilities.aspx"
site(
    "Kitsap County Olympic View Transfer Station — Bremerton",
    "County transfer — bulky / appliances / tires / C&D / yard waste",
    "seattle",
    "WA",
    "98312",
    "9380 SW Barney White Road, Bremerton, WA 98312",
    47.505,
    -122.685,
    "https://kitsap.gov/pw/Pages/OlympicViewTransferStation.aspx",
    "Daily 8:00–17:00 — kitsap.gov",
    "360-674-7065",
    mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste", "cooking-oil"]),
)
site(
    "Kitsap County Olympic View Transfer Station (Tacoma hub)",
    "County transfer — tagged for Tacoma metro finder",
    "tacoma",
    "WA",
    "98312",
    "9380 SW Barney White Road, Bremerton, WA 98312",
    47.505,
    -122.685,
    "https://kitsap.gov/pw/Pages/OlympicViewTransferStation.aspx",
    "Daily 8:00–17:00 — kitsap.gov",
    "360-674-7065",
    mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste"]),
)
site(
    "Kitsap County Household Hazardous Waste Facility — Imperial Way",
    "County HHW — Kitsap / Mason / Jefferson residents",
    "seattle",
    "WA",
    "98312",
    "5551 SW Imperial Way, Bremerton, WA 98312",
    47.545,
    -122.665,
    "https://www.kitsap.gov/pw/pages/hhwfacility.aspx",
    "Confirm hours — kitsap.gov HHW facility",
    "360-337-5777",
    mats(HHW, E_WASTE),
)
site(
    "Kitsap County HHW Facility — Imperial Way (Tacoma hub)",
    "County HHW — Tacoma metro tag",
    "tacoma",
    "WA",
    "98312",
    "5551 SW Imperial Way, Bremerton, WA 98312",
    47.545,
    -122.665,
    "https://www.kitsap.gov/pw/pages/hhwfacility.aspx",
    "Confirm hours — kitsap.gov",
    "360-337-5777",
    mats(HHW, E_WASTE),
)
site(
    "Kitsap County Hansville Recycling & Garbage Facility",
    "County RAGF — residential garbage / limited bulky / used oil",
    "seattle",
    "WA",
    "98346",
    "7791 NE Ecology Road, Kingston, WA 98346",
    47.915,
    -122.545,
    "https://www.kitsap.gov/pw/Pages/NK_Recycle_Garbage_Facility.aspx",
    "Wed–Mon 8:30–16:00; closed Tue — kitsap.gov",
    "360-638-2710",
    mats(BULKY, ["motor-oil", "antifreeze", "car-battery"], TIRES),
)
site(
    "Kitsap County Olalla Recycling & Garbage Facility",
    "County RAGF — residential garbage / limited bulky",
    "tacoma",
    "WA",
    "98359",
    "2850 SE Burley-Olalla Road, Olalla, WA 98359",
    47.425,
    -122.545,
    "https://www.kitsap.gov/pw/Pages/sk_Recycle_Garbage_Facility.aspx",
    "Fri–Mon 8:30–16:00 — kitsap.gov",
    "253-857-5034",
    mats(BULKY, ["motor-oil", "antifreeze", "car-battery"], TIRES),
)
site(
    "Kitsap County Silverdale Recycling & Garbage Facility",
    "County RAGF — residential garbage / limited hard items",
    "seattle",
    "WA",
    "98383",
    "8843 NW Dickey Road, Silverdale, WA 98383",
    47.655,
    -122.695,
    KITSAP,
    "Confirm hours kcowa.us/dropoff — kitsap.gov",
    "360-337-5777",
    mats(BULKY, ["motor-oil", "antifreeze"], TIRES),
)

# ── Thurston County WA WARC / HazoHouse → seattle / tacoma ──
site(
    "Thurston County Waste and Recovery Center — Lacey",
    "County WARC — bulky / appliances / tires / C&D / yard waste",
    "seattle",
    "WA",
    "98516",
    "2420 Hogum Bay Road NE, Lacey, WA 98516",
    47.075,
    -122.765,
    "https://www.thurstoncountywa.gov/departments/public-works/garbage-recycling/garbage/waste-and-recover-center-warc",
    "Mon–Fri 7:00–16:45; Sat–Sun 8:00–16:45 — thurstoncountywa.gov",
    "360-867-2491",
    mats(BULKY, APPLIANCE, TIRES, CD, ["yard-waste"]),
)
site(
    "Thurston County HazoHouse — Household Hazardous Waste",
    "County HHW drive-thru at WARC south entrance",
    "seattle",
    "WA",
    "98516",
    "2420 Hogum Bay Road NE, Lacey, WA 98516",
    47.074,
    -122.764,
    "https://www.thurstoncountywa.gov/departments/public-works/garbage-recycling/household-hazardous-waste",
    "Daily 8:00–16:45; free for Thurston residents — thurstoncountywa.gov",
    "360-867-2491",
    mats(HHW, E_WASTE),
)
site(
    "Thurston County WARC / HazoHouse (Tacoma hub)",
    "County WARC + HHW — Tacoma metro tag",
    "tacoma",
    "WA",
    "98516",
    "2420 Hogum Bay Road NE, Lacey, WA 98516",
    47.075,
    -122.765,
    "https://www.thurstoncountywa.gov/departments/public-works/garbage-recycling/household-hazardous-waste",
    "WARC Mon–Fri 7:00–16:45; HazoHouse daily 8:00–16:45",
    "360-867-2491",
    mats(BULKY, APPLIANCE, TIRES, HHW, E_WASTE, CD),
)

# ── Kent County MI SafeChem satellites (kentcountymi.gov) → grand-rapids ──
KENT = "https://www.kentcountymi.gov/371/Locations-and-Hours"
site(
    "Kent County SafeChem HHW — Wealthy Street Grand Rapids",
    "County HHW SafeChem + Swap Shop",
    "grand-rapids",
    "MI",
    "49504",
    "1045 Wealthy Street SW, Grand Rapids, MI 49504",
    42.955,
    -85.685,
    "https://www.kentcountymi.gov/368/SafeChem",
    "Mon/Thu 13:30–17:30; Wed 7:30–11:30; 2nd Sat 8:30–11:00",
    "616-632-7920",
    mats(HHW, E_WASTE),
)
site(
    "Kent County SafeChem Collection — Kentwood Breton",
    "County SafeChem satellite — HHW (no electronics)",
    "grand-rapids",
    "MI",
    "49508",
    "5068 Breton SE, Kentwood, MI 49508",
    42.885,
    -85.595,
    KENT,
    "Tue 10:30–13:30 — kentcountymi.gov",
    "616-632-7920",
    mats(HHW),
)
site(
    "Kent County SafeChem Collection — Wyoming Ivanrest",
    "County SafeChem satellite — HHW",
    "grand-rapids",
    "MI",
    "49418",
    "2350 Ivanrest Avenue SW, Grandville, MI 49418",
    42.905,
    -85.755,
    KENT,
    "Mon 13:00–15:00; Thu 7:00–9:00 — kentcountymi.gov",
    "616-632-7920",
    mats(HHW),
)
site(
    "Kent County SafeChem at South Kent Landfill — Byron Center",
    "County SafeChem at South Kent Landfill",
    "grand-rapids",
    "MI",
    "49315",
    "10300 South Kent Drive SW, Byron Center, MI 49315",
    42.815,
    -85.725,
    KENT,
    "Mon 8:30–11:30 — kentcountymi.gov",
    "616-632-7920",
    mats(HHW, BULKY, APPLIANCE, TIRES, CD),
)
site(
    "Kent County SafeChem at North Kent — Rockford Friday HHW",
    "County SafeChem at North Kent Recycling & Waste Center",
    "grand-rapids",
    "MI",
    "49341",
    "2908 Ten Mile Road, Rockford, MI 49341",
    43.145,
    -85.575,
    "https://www.kentcountymi.gov/245/North-Kent-Recycling-Waste-Center",
    "Fri SafeChem 8:30–11:30; transfer Mon–Sat 7:30–17:00",
    "616-632-7920",
    mats(HHW, BULKY, APPLIANCE, TIRES),
)

# ── Utah County UT (npswssdut.gov / suvswd.org / health.utahcounty.gov) → salt-lake-city ──
site(
    "North Pointe Solid Waste Transfer Station — Lindon",
    "District transfer — bulky / C&D / HHW / yard waste",
    "salt-lake-city",
    "UT",
    "84042",
    "2000 West 200 South, Lindon, UT 84042",
    40.335,
    -111.725,
    "https://www.npswssdut.gov/contact-us",
    "Mon–Fri 7:00–17:30; Sat 7:30–15:30 — npswssdut.gov",
    "801-225-8538",
    mats(BULKY, APPLIANCE, TIRES, CD, HHW, ["yard-waste"]),
)
site(
    "North Pointe Construction & Demolition Landfill — Fairfield",
    "District C&D landfill — construction debris",
    "salt-lake-city",
    "UT",
    "84013",
    "471 N 18150 West, Fairfield, UT 84013",
    40.265,
    -112.095,
    "https://www.npswssdut.gov/contact-us",
    "Mon–Fri 7:00–16:30 — npswssdut.gov",
    "801-787-0669",
    mats(CD, ["lumber", "concrete", "drywall"]),
)
site(
    "South Utah Valley Dry Creek Transfer Station — Spanish Fork",
    "District transfer + HHW — south Utah County",
    "salt-lake-city",
    "UT",
    "84660",
    "518 West 3450 North, Spanish Fork, UT 84660",
    40.145,
    -111.665,
    "https://suvswd.org/",
    "Mon–Sat 7:00–18:00 — suvswd.org",
    "801-798-3901",
    mats(BULKY, APPLIANCE, TIRES, CD, HHW, E_WASTE, ["yard-waste"]),
)

# ── DeKalb County GA (dekalbcountyga.gov) → atlanta ──
site(
    "DeKalb County Seminole Road Landfill — Ellenwood",
    "County landfill — bulky / e-waste / residential disposal",
    "atlanta",
    "GA",
    "30294",
    "4203 Clevemont Road, Ellenwood, GA 30294",
    33.635,
    -84.275,
    "https://www.dekalbcountyga.gov/sanitation/electronics-recycling",
    "Mon–Fri 8:00–17:00; Sat 8:00–16:00; residency proof — dekalbcountyga.gov",
    "404-294-2900",
    mats(BULKY, APPLIANCE, TIRES, CD, E_WASTE),
)
site(
    "DeKalb County Central Transfer Station — Leroy Scott Drive",
    "County transfer / HHW event site",
    "atlanta",
    "GA",
    "30032",
    "3720 Leroy Scott Drive, Decatur, GA 30032",
    33.745,
    -84.265,
    "https://www.dekalbcountyga.gov/household-hazardous-waste-recycling-event",
    "Confirm hours; HHW at scheduled events — dekalbcountyga.gov",
    "404-294-2900",
    mats(BULKY, APPLIANCE, TIRES, CD, HHW),
)

# ── Cobb County GA (cobbcounty.gov) → atlanta ──
site(
    "Cobb County / GFL Transfer Station — County Services Parkway",
    "County-contracted transfer — bulky / tires / mattresses / e-waste",
    "atlanta",
    "GA",
    "30008",
    "1897 County Services Parkway, Marietta, GA 30008",
    33.905,
    -84.580,
    "https://www.cobbcounty.gov/swb/waste-disposal",
    "Mon–Fri 7:00–17:00; Sat 7:00–16:00 — cobbcounty.gov",
    "770-485-8940",
    mats(BULKY, APPLIANCE, TIRES, CD, E_WASTE, ["propane-tank"]),
)
site(
    "Cobb County Vegetative Waste Recovery Center — County Services",
    "County vegetative / yard waste grinding facility",
    "atlanta",
    "GA",
    "30008",
    "2150 County Services Parkway, Marietta, GA 30008",
    33.908,
    -84.575,
    "https://www.cobbcounty.gov/swb/waste-disposal",
    "Confirm hours — cobbcounty.gov / TAG Grinding",
    "770-528-2500",
    mats(["yard-waste", "christmas-tree"]),
)
site(
    "Cobb County / Keep Cobb Beautiful HHW Event — Jim Miller Park",
    "Annual county HHW collection event site",
    "atlanta",
    "GA",
    "30008",
    "2245 Callaway Road, Marietta, GA 30008",
    33.915,
    -84.555,
    "https://www.cobbcounty.gov/keep-cobb-beautiful/recycling/kcb-annual-household-hazardous-waste-hhw-event",
    "Annual registered HHW event — cobbcounty.gov",
    "678-581-5488",
    mats(HHW),
)

# ── SPSA Hampton Roads fill gaps (spsava.gov) → virginia-beach / norfolk / chesapeake ──
site(
    "SPSA Isle of Wight Transfer Station — Smithfield",
    "Regional transfer — bulky / residential MSW",
    "norfolk",
    "VA",
    "23430",
    "13191 Four Square Road, Smithfield, VA 23430",
    36.965,
    -76.635,
    "https://www.spsava.gov/187/Isle-of-Wight",
    "Mon–Fri 8:00–15:00; Sat 8:00–12:00 — spsava.gov",
    "757-961-3683",
    mats(BULKY, APPLIANCE, TIRES, CD),
)
site(
    "SPSA Franklin Transfer Station — HHW quarterly",
    "Regional transfer + quarterly HHW / e-waste",
    "chesapeake",
    "VA",
    "23851",
    "30521 General Thomas Highway, Franklin, VA 23851",
    36.675,
    -76.925,
    "https://www.spsava.gov/186/Franklin",
    "Mon–Fri 8:00–15:00; Sat 8:00–12:00; HHW last Thu Jan/Apr/Jul/Oct 9–12",
    "757-961-3683",
    mats(BULKY, APPLIANCE, TIRES, HHW, E_WASTE),
)
def purge_mistags(facilities: list[dict]) -> int:
    """Remove Fairfax County sites wrongly tagged to Hampton Roads metros."""
    keep = []
    dropped = 0
    for row in facilities:
        name = (row.get("name") or "").lower()
        addr = (row.get("address") or "").lower()
        slug = row.get("city_slug")
        if slug in {"chesapeake", "norfolk", "virginia-beach"} and (
            "fairfax" in name or "fairfax" in addr or "lorton" in addr or "west ox road" in addr
        ):
            dropped += 1
            continue
        keep.append(row)
    facilities[:] = keep
    return dropped


def main() -> None:
    existing = json.loads(FAC_PATH.read_text())
    mistag_dropped = purge_mistags(existing)

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
        # Skip commercial-only Oceana as soft-ish public value — keep if hard mats
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
        f"mistag_dropped={mistag_dropped} soft_dropped={soft_dropped} "
        f"hard_total={len(hard)} upserts={len(UPSERTS)}"
    )


if __name__ == "__main__":
    main()
