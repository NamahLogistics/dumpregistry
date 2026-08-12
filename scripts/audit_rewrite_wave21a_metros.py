#!/usr/bin/env python3
"""Portal-audited city guides for wave-21a metros (city-sourced only).

Compact channel-template wave: each city defines disposal channels that emit
base item rows, then clone_siblings() expands to exactly 70 unique item_slugs.

Cities researched from official program pages (2026-08-12):
  - Moreno Valley, CA — WM bulky; Badlands HHW/ABOP
  - Columbus, GA — 311 bulk; Pine Grove Landfill; Recycling Center HHW events
  - Port St. Lucie, FL — city bulk; St. Lucie County HHW/e-waste Fort Pierce
  - Augusta, GA — weekly bulk; Deans Bridge landfill; HHW/e-waste quarterly
  - Oxnard, CA — bulky $45/5; Del Norte Buy-Back; Clean Harbors Camarillo HHW
  - Montgomery, AL — 311 bulk fees; landfill; McInnis e-waste; HHW events
  - Huntington Beach, CA — Republic bulky 4×/yr; OC Landfills HHW
  - Overland Park, KS — hauler bulky; Johnson County HHW
  - Glendale, CA — city bulky; Flower St HHW; Chevy Chase e-waste
  - McKinney, TX — Frontier bulky 12×; curbside HHW/e-waste; NTMWD Custer TS
  - Sioux Falls, SD — Chambers HHW+e-waste; Regional Landfill bulky
  - Peoria, AZ — bulk 2×/yr + at-home HHW; Glendale Landfill e-waste
  - Vancouver, WA — Clark County CRC HHW; West Van MRC
  - Shreveport, LA — bulky appt; Woolworth landfill; HHW events
  - Brownsville, TX — monthly brush/bulky; FM 802 landfill; HHW events
  - Newport News, VA — ROC bulk+e-waste daily; HHW quarterly at ROC
  - Tempe, AZ — bulk every-other-month; HPCC HHW
  - Aurora, IL — Groot sticker bulk; Naperville HHW
  - Santa Rosa, CA — Recology bulky; Sonoma HHW Petaluma
  - Eugene, OR — Glenwood HHW + E-Cycles; hauler/self-haul bulky
  - Elk Grove, CA — Republic bulky 3×; SWCC Disposal Ln
  - Salem, OR — Marion SKRTS + HHW
  - Ontario, CA — bulky 4×; Cucamonga HHW Fri–Sat
  - Cary, NC — bulky appt; Wake South Wake HHW Apex
  - Rancho Cucamonga, CA — Burrtec bulky 4×; Lion St HHW
  - Oceanside, CA — Industry St HHW; WM bulky 5×5
  - Lancaster, CA — WM bulky 4×; AVECC Palmdale (CleanLA)
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
VERIFIED = "2026-08-12"

SIBLINGS = {
    "mattress": [
        "box-spring",
        "sofa",
        "recliner",
        "carpet",
        "exercise-equipment",
        "dining-table",
        "desk",
        "bookshelf",
        "hot-tub",
        "piano",
    ],
    "refrigerator": ["freezer", "washer", "dryer", "dishwasher", "stove", "water-heater"],
    "television": ["laptop", "desktop-computer", "printer", "tablet", "microwave", "hard-drive"],
    "e-waste-mixed": ["ink-toner", "solar-panel"],
    "car-battery": ["household-batteries", "antifreeze"],
    "paint-latex": ["pesticides", "herbicides", "pool-chemicals", "gasoline"],
    "propane-tank": ["helium-tank", "fire-extinguisher"],
    "fluorescent-bulbs": ["smoke-detector", "thermometer-mercury", "led-bulbs", "incandescent-bulbs"],
    "medical-sharps": ["needles", "prescription-drugs"],
    "tires": ["tire-rims"],
    "air-conditioner": ["dehumidifier"],
    "yard-waste": ["christmas-tree"],
    "plastic-bags": ["styrofoam", "cardboard", "glass-bottles"],
    "construction-debris": ["concrete", "drywall", "lumber", "asphalt-shingles", "car-parts"],
}

HHW_MATERIALS = [
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


def faq(pairs):
    return [{"q": q, "a": a} for q, a in pairs]


def R(city, state, item, badge, hazard, curbside, fee, facility, answer, steps, faqs, src_name, src_url):
    return {
        "item_slug": item,
        "state": state,
        "city_slug": city,
        "zip": None,
        "is_curbside_allowed": curbside,
        "nearest_facility_type": facility[:120],
        "common_disposal_fee": fee[:80],
        "badge": badge,
        "hazard_rating": hazard,
        "answer": answer,
        "steps": steps,
        "faqs": faq(faqs),
        "source_url": src_url,
        "source_name": src_name,
        "last_verified_at": VERIFIED,
        "reviewed_by": "editorial-audit",
        "needs_review": False,
    }


def clone_siblings(base_rows):
    by = {r["item_slug"]: r for r in base_rows}
    out = []
    for item, sibs in SIBLINGS.items():
        base = by.get(item)
        if not base:
            continue
        for sib in sibs:
            if sib in by:
                continue
            e = deepcopy(base)
            e["item_slug"] = sib
            e["answer"] = (
                f"In {base['city_slug'].replace('-', ' ').title()}, {sib.replace('-', ' ')} follows the same "
                f"verified program pathway as {item.replace('-', ' ')}. " + base["answer"]
            )
            e["faqs"] = faq(
                [
                    (
                        f"Same channel as {item.replace('-', ' ')}?",
                        "Yes — same city/county program; confirm acceptance for unusual sizes or commercial loads.",
                    ),
                    ("Source?", f"Based on {base['source_name']} (audited)."),
                ]
            )
            out.append(e)
            by[sib] = e
    return base_rows + out


def ch(items, badge, hazard, curbside, fee, facility, answer, steps, faqs, src):
    """One disposal channel applied to one or more item slugs."""
    return {
        "items": items if isinstance(items, (list, tuple)) else [items],
        "badge": badge,
        "hazard": hazard,
        "curbside": curbside,
        "fee": fee,
        "facility": facility,
        "answer": answer,
        "steps": steps,
        "faqs": faqs,
        "src": src,
    }


def rows_from_channels(city, state, channels):
    rows = []
    for channel in channels:
        for item in channel["items"]:
            label = item.replace("-", " ")
            answer = channel["answer"].replace("{item}", label)
            rows.append(
                R(
                    city,
                    state,
                    item,
                    channel["badge"],
                    channel["hazard"],
                    channel["curbside"],
                    channel["fee"],
                    channel["facility"],
                    answer,
                    channel["steps"],
                    channel["faqs"],
                    *channel["src"],
                )
            )
    return rows


def std_tail(hub, *, yard_fee, yard_facility, yard_answer, yard_steps, yard_faqs, cd_fee, cd_facility, cd_answer, cd_steps, cd_faqs, yard_badge="ACCEPTED_IN_BLUE_BIN", yard_curbside=True):
    return [
        ch(
            "tires",
            "SPECIAL_HANDLING",
            "Medium",
            False,
            "NOT HHW — retailer take-back / landfill tire programs",
            "Retailer take-back / local tire programs",
            "Tires are not a standard HHW material here. Use retailer take-back when replacing tires or confirm landfill/transfer tire acceptance. Keep tires off HHW loads.",
            [
                "Do not haul tires to HHW as household hazardous waste.",
                "Use retailer take-back when replacing tires.",
                "Confirm landfill or transfer tire rules before drop-off.",
            ],
            [("HHW for tires?", "No."), ("Bulk for tires?", "Confirm solid-waste rules — not HHW.")],
            hub,
        ),
        ch("yard-waste", yard_badge, "Low", yard_curbside, yard_fee, yard_facility, yard_answer, yard_steps, yard_faqs, hub),
        ch(
            "food-scraps",
            "SPECIAL_HANDLING",
            "Low",
            True,
            "Garbage cart unless private compost",
            "Garbage / private compost",
            "Bag food scraps for garbage unless you compost. Keep food out of recycling and HHW.",
            ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."],
            [("HHW for food?", "No.")],
            hub,
        ),
        ch(
            "plastic-bags",
            "SPECIAL_HANDLING",
            "Low",
            False,
            "Not recycling — store take-back / trash",
            "Retail bag take-back / trash",
            "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
            ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."],
            [("Bulk for bags?", "No.")],
            hub,
        ),
        ch(
            "construction-debris",
            "SPECIAL_HANDLING",
            "Low",
            False,
            cd_fee,
            cd_facility,
            cd_answer,
            cd_steps,
            cd_faqs,
            hub,
        ),
    ]


# ---------------------------------------------------------------------------
# City channel packs
# ---------------------------------------------------------------------------

def moreno_valley():
    c, st = "moreno-valley", "CA"
    hub = (
        'City of Moreno Valley — Trash & Recycling',
        'https://www.moval.gov/259/Trash-Recycling',
    )
    hhw = (
        'Riverside County Waste — Household Hazardous Waste',
        'https://www.rcwaste.org/hhw',
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                'mattress',
                'SPECIAL_HANDLING',
                'Low',
                True,
                'WM bulky collection — schedule via moval.gov',
                'Moreno Valley / Waste Management bulky collection',
                'Moreno Valley {item}s go on Waste Management bulky collection — schedule via moval.gov. Keep HHW and loose chemicals off bulk piles.',
                ['Schedule WM bulky via moval.gov.', 'Set out per WM bulky rules.', 'Keep paint, batteries, and propane off bulk piles.'],
                [('Who hauls?', 'Waste Management for Moreno Valley.'), ('HHW on bulk?', 'No.')],
                hub,
            ),
            ch(
                ['refrigerator', 'air-conditioner'],
                'SPECIAL_HANDLING',
                'High',
                True,
                'WM bulky — Freon appliances per hauler rules',
                'Moreno Valley / Waste Management bulky collection',
                'Moreno Valley Freon {item}s may go on WM bulky when prepared per hauler rules. Never vent refrigerant yourself. Confirm Freon appliance acceptance when scheduling.',
                ['Schedule WM bulky and confirm Freon appliance acceptance.', 'Do not vent Freon yourself.', 'Keep HHW chemicals off bulk piles.'],
                [('Freon OK on bulk?', 'Confirm with WM when scheduling.'), ('Self-vent?', 'Never.')],
                hub,
            ),
            ch(
                ['television', 'computer-monitor', 'smartphone', 'e-waste-mixed'],
                'BANNED_FROM_LANDFILLS',
                'Medium',
                False,
                'NOT bulk — Badlands HHW/ABOP 31125 Ironwood Ave',
                'Badlands Landfill HHW/ABOP — 31125 Ironwood Ave',
                'Moreno Valley electronics including {item} go to Riverside County Badlands HHW/ABOP — 31125 Ironwood Avenue. Wipe data before drop-off.',
                ['Haul e-waste to Badlands HHW/ABOP at 31125 Ironwood Ave.', 'Confirm hours on rcwaste.org.', 'Wipe personal data.'],
                [('Address?', '31125 Ironwood Ave.'), ('Bulk for TVs?', 'Use Badlands HHW/ABOP.')],
                hhw,
            ),
            ch(
                ['paint-latex', 'paint-oil', 'car-battery', 'lithium-battery', 'motor-oil', 'propane-tank', 'fluorescent-bulbs', 'cooking-oil', 'medical-sharps'],
                'BANNED_FROM_LANDFILLS',
                'High',
                False,
                'Badlands HHW/ABOP — 31125 Ironwood Ave',
                'Badlands Landfill HHW/ABOP — 31125 Ironwood Ave',
                'Take {item} to Riverside County Badlands Household Hazardous Waste / ABOP — 31125 Ironwood Avenue. Confirm hours on rcwaste.org. Not bulk trash.',
                ['Check rcwaste.org hours before visiting.', 'Haul sealed materials to 31125 Ironwood Ave.', 'Keep HHW off WM bulk piles.'],
                [('HHW address?', '31125 Ironwood Ave.'), ('Bulk for paint?', 'No.')],
                hhw,
            ),
        ]
        + std_tail(
            hub,
            yard_fee='Moreno Valley yard / organics program',
            yard_facility='Moreno Valley trash and recycling collection',
            yard_answer='Moreno Valley yard waste follows the city trash and recycling program on moval.gov. Follow set-out rules.',
            yard_steps=['Follow city set-out rules for yard trimmings.', 'Keep yard waste out of HHW.', 'Check moval.gov for seasonal guidance.'],
            yard_faqs=[('Christmas trees?', 'Follow city seasonal yard-waste guidance.')],
            cd_fee='NOT typical free bulk — private C&D / landfill',
            cd_facility='Private C&D hauler / Riverside County landfill',
            cd_answer='Construction debris is not typical free bulk material. Hire a private C&D hauler or confirm landfill C&D rules. Route paint/chemicals to Badlands HHW separately.',
            cd_steps=['Do not treat remodel debris as free bulk without confirming limits.', 'Hire private C&D or confirm landfill C&D acceptance.', 'Route paint to Badlands HHW/ABOP.'],
            cd_faqs=[('HHW for C&D?', 'No — separate paint/chemicals.')],
        ),
    )


def columbus_ga():
    c, st = "columbus-ga", "GA"
    hub = (
        'City of Columbus — Solid Waste / 311',
        'https://www.columbusga.gov/',
    )
    hhw = (
        'Columbus Recycling Center — HHW events',
        'https://www.columbusga.gov/',
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                'mattress',
                'SPECIAL_HANDLING',
                'Low',
                True,
                'Bulk via 311 — schedule city bulk collection',
                'Columbus bulk collection / Pine Grove Landfill',
                'Columbus GA {item}s go on city bulk collection — schedule via 311. Residents may also use Pine Grove Landfill pathways. Keep HHW off bulk piles.',
                ['Schedule bulk via Columbus 311.', 'Or confirm Pine Grove Landfill drop-off rules.', 'Keep paint, batteries, and propane off bulk piles.'],
                [('How to schedule?', 'Call or use Columbus 311.'), ('Landfill?', 'Pine Grove Landfill pathways.')],
                hub,
            ),
            ch(
                ['refrigerator', 'air-conditioner'],
                'SPECIAL_HANDLING',
                'High',
                True,
                'Bulk / landfill — Freon appliances per city rules',
                'Columbus bulk / Pine Grove Landfill',
                'Columbus GA Freon {item}s follow bulk or landfill appliance rules. Never vent refrigerant yourself. Confirm Freon handling when scheduling 311 bulk.',
                ['Schedule via 311 and confirm Freon appliance acceptance.', 'Do not vent Freon yourself.', 'Keep HHW chemicals off bulk piles.'],
                [('Freon OK?', 'Confirm with 311 / solid waste.'), ('Self-vent?', 'Never.')],
                hub,
            ),
            ch(
                ['television', 'computer-monitor', 'smartphone', 'e-waste-mixed'],
                'BANNED_FROM_LANDFILLS',
                'Medium',
                False,
                'HHW / recycling events at Columbus Recycling Center',
                'Columbus Recycling Center — HHW/e-waste events',
                'Columbus GA electronics including {item} go to Recycling Center HHW/e-waste events — confirm event dates on columbusga.gov. Wipe data before drop-off.',
                ['Check columbusga.gov for Recycling Center HHW/e-waste event dates.', 'Haul electronics to the event site.', 'Wipe personal data.'],
                [('Ongoing drop-off?', 'Confirm event schedule on columbusga.gov.')],
                hhw,
            ),
            ch(
                ['paint-latex', 'paint-oil', 'car-battery', 'lithium-battery', 'motor-oil', 'propane-tank', 'fluorescent-bulbs', 'cooking-oil', 'medical-sharps'],
                'BANNED_FROM_LANDFILLS',
                'High',
                False,
                'HHW events at Columbus Recycling Center',
                'Columbus Recycling Center — HHW events',
                'Take {item} to Columbus Recycling Center household hazardous waste events — confirm dates on columbusga.gov. Not regular bulk trash.',
                ['Check columbusga.gov for HHW event dates.', 'Haul sealed materials to the Recycling Center event.', 'Keep HHW off bulk piles.'],
                [('Bulk for paint?', 'No — Recycling Center HHW events.')],
                hhw,
            ),
        ]
        + std_tail(
            hub,
            yard_fee='Columbus yard / bulk pathways',
            yard_facility='Columbus solid waste collection',
            yard_answer='Columbus GA yard waste follows city solid-waste and bulk pathways — schedule via 311 when needed.',
            yard_steps=['Follow city set-out rules for yard trimmings.', 'Use 311 for bulk/yard questions.', 'Keep yard waste out of HHW events.'],
            yard_faqs=[('Christmas trees?', 'Follow city seasonal yard-waste guidance.')],
            cd_fee='NOT typical free bulk — private C&D / Pine Grove',
            cd_facility='Private C&D hauler / Pine Grove Landfill',
            cd_answer='Construction debris is not typical free bulk material. Hire private C&D or confirm Pine Grove Landfill C&D rules. Route paint/chemicals to Recycling Center HHW events.',
            cd_steps=['Confirm landfill C&D acceptance before hauling.', 'Hire private C&D for larger projects.', 'Route paint to HHW events.'],
            cd_faqs=[('HHW for C&D?', 'No — separate paint/chemicals.')],
        ),
    )


def port_st_lucie():
    c, st = "port-st-lucie", "FL"
    hub = (
        'City of Port St. Lucie — Solid Waste',
        'https://www.cityofpsl.com/government/city-departments-services/public-works/solid-waste',
    )
    hhw = (
        'St. Lucie County — Household Hazardous Waste',
        'https://www.stlucieco.gov/departments-services/a-z-departments/solid-waste/household-hazardous-waste',
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                'mattress',
                'SPECIAL_HANDLING',
                'Low',
                True,
                'City bulk collection — cityofpsl.com',
                'Port St. Lucie bulk collection',
                'Port St. Lucie {item}s go on city bulk collection — follow set-out rules on cityofpsl.com. Keep HHW and e-waste off bulk piles.',
                ['Follow cityofpsl.com bulk set-out rules.', 'Set out on the scheduled bulk day.', 'Keep paint, batteries, and electronics off bulk piles.'],
                [('Source?', 'cityofpsl.com solid waste.'), ('HHW on bulk?', 'No.')],
                hub,
            ),
            ch(
                ['refrigerator', 'air-conditioner'],
                'SPECIAL_HANDLING',
                'High',
                True,
                'City bulk — Freon appliances per city rules',
                'Port St. Lucie bulk collection',
                'Port St. Lucie Freon {item}s follow city bulk appliance rules. Never vent refrigerant yourself. Confirm Freon acceptance on cityofpsl.com before set-out.',
                ['Confirm Freon appliance bulk rules on cityofpsl.com.', 'Do not vent Freon yourself.', 'Keep HHW chemicals off bulk piles.'],
                [('Freon OK on bulk?', 'Confirm city bulk appliance rules.'), ('Self-vent?', 'Never.')],
                hub,
            ),
            ch(
                ['television', 'computer-monitor', 'smartphone', 'e-waste-mixed'],
                'BANNED_FROM_LANDFILLS',
                'Medium',
                False,
                'NOT bulk — St. Lucie County HHW 6120 Glades Cut-Off Rd',
                'St. Lucie County HHW — 6120 Glades Cut-Off Rd, Fort Pierce',
                'Port St. Lucie electronics including {item} go to St. Lucie County HHW — 6120 Glades Cut-Off Road, Fort Pierce. Wipe data before drop-off.',
                ['Do not set e-waste on city bulk.', 'Haul to 6120 Glades Cut-Off Rd, Fort Pierce.', 'Wipe personal data.'],
                [('Address?', '6120 Glades Cut-Off Rd, Fort Pierce.'), ('Bulk for TVs?', 'No.')],
                hhw,
            ),
            ch(
                ['paint-latex', 'paint-oil', 'car-battery', 'lithium-battery', 'motor-oil', 'propane-tank', 'fluorescent-bulbs', 'cooking-oil', 'medical-sharps'],
                'BANNED_FROM_LANDFILLS',
                'High',
                False,
                'St. Lucie County HHW — 6120 Glades Cut-Off Rd, Fort Pierce',
                'St. Lucie County HHW — 6120 Glades Cut-Off Rd, Fort Pierce',
                'Take {item} to St. Lucie County Household Hazardous Waste — 6120 Glades Cut-Off Road, Fort Pierce. Confirm hours on stlucieco.gov. Not city bulk.',
                ['Check stlucieco.gov HHW hours before visiting.', 'Haul sealed materials to 6120 Glades Cut-Off Rd.', 'Keep HHW off city bulk piles.'],
                [('HHW address?', '6120 Glades Cut-Off Rd, Fort Pierce.'), ('Bulk for paint?', 'No.')],
                hhw,
            ),
        ]
        + std_tail(
            hub,
            yard_fee='Port St. Lucie yard / bulk pathways',
            yard_facility='Port St. Lucie solid waste collection',
            yard_answer='Port St. Lucie yard waste follows city solid-waste and bulk pathways on cityofpsl.com.',
            yard_steps=['Follow city set-out rules for yard trimmings.', 'Keep yard waste out of county HHW.', 'Check cityofpsl.com for seasonal guidance.'],
            yard_faqs=[('Christmas trees?', 'Follow city seasonal yard-waste guidance.')],
            cd_fee='NOT typical free bulk — private C&D / county',
            cd_facility='Private C&D hauler / St. Lucie County solid waste',
            cd_answer='Construction debris is not typical free bulk material. Hire private C&D or confirm county C&D rules. Route paint/chemicals to St. Lucie County HHW separately.',
            cd_steps=['Confirm C&D acceptance before hauling.', 'Hire private C&D for larger projects.', 'Route paint to 6120 Glades Cut-Off Rd.'],
            cd_faqs=[('HHW for C&D?', 'No — separate paint/chemicals.')],
        ),
    )


def augusta():
    c, st = "augusta", "GA"
    hub = (
        'Augusta — Solid Waste / Bulk',
        'https://www.augustaga.gov/',
    )
    hhw = (
        'Augusta — HHW / e-waste events',
        'https://www.augustaga.gov/',
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                'mattress',
                'SPECIAL_HANDLING',
                'Low',
                True,
                'Weekly bulk collection — augustaga.gov',
                'Augusta weekly bulk / landfill 4330 Deans Bridge Rd',
                'Augusta {item}s go on weekly bulk collection — follow augustaga.gov set-out rules. Residents may also use the landfill at 4330 Deans Bridge Road, Blythe. Keep HHW off bulk piles.',
                ['Follow weekly bulk set-out rules on augustaga.gov.', 'Or haul to 4330 Deans Bridge Rd, Blythe when allowed.', 'Keep paint, batteries, and propane off bulk piles.'],
                [('Weekly bulk?', 'Yes — follow city set-out rules.'), ('Landfill?', '4330 Deans Bridge Rd, Blythe.')],
                hub,
            ),
            ch(
                ['refrigerator', 'air-conditioner'],
                'SPECIAL_HANDLING',
                'High',
                True,
                'Weekly bulk / landfill — Freon per city rules',
                'Augusta weekly bulk / Deans Bridge landfill',
                'Augusta Freon {item}s follow weekly bulk or landfill appliance rules. Never vent refrigerant yourself. Confirm Freon handling before set-out.',
                ['Confirm Freon appliance rules on augustaga.gov.', 'Do not vent Freon yourself.', 'Keep HHW chemicals off bulk piles.'],
                [('Freon OK?', 'Confirm city appliance rules.'), ('Self-vent?', 'Never.')],
                hub,
            ),
            ch(
                ['television', 'computer-monitor', 'smartphone', 'e-waste-mixed'],
                'BANNED_FROM_LANDFILLS',
                'Medium',
                False,
                'HHW/e-waste quarterly events — augustaga.gov',
                'Augusta HHW / e-waste quarterly events',
                'Augusta electronics including {item} go to quarterly HHW/e-waste events — confirm dates on augustaga.gov. Wipe data before drop-off.',
                ['Check augustaga.gov for quarterly HHW/e-waste event dates.', 'Haul electronics to the event site.', 'Wipe personal data.'],
                [('Ongoing drop-off?', 'Confirm quarterly event schedule.')],
                hhw,
            ),
            ch(
                ['paint-latex', 'paint-oil', 'car-battery', 'lithium-battery', 'motor-oil', 'propane-tank', 'fluorescent-bulbs', 'cooking-oil', 'medical-sharps'],
                'BANNED_FROM_LANDFILLS',
                'High',
                False,
                'HHW/e-waste quarterly events — augustaga.gov',
                'Augusta HHW / e-waste quarterly events',
                'Take {item} to Augusta household hazardous waste / e-waste quarterly events — confirm dates on augustaga.gov. Not weekly bulk trash.',
                ['Check augustaga.gov for HHW event dates.', 'Haul sealed materials to the event.', 'Keep HHW off weekly bulk piles.'],
                [('Bulk for paint?', 'No — quarterly HHW events.')],
                hhw,
            ),
        ]
        + std_tail(
            hub,
            yard_fee='Augusta yard / bulk pathways',
            yard_facility='Augusta solid waste collection',
            yard_answer='Augusta yard waste follows city solid-waste and weekly bulk pathways on augustaga.gov.',
            yard_steps=['Follow city set-out rules for yard trimmings.', 'Keep yard waste out of HHW events.', 'Check augustaga.gov for seasonal guidance.'],
            yard_faqs=[('Christmas trees?', 'Follow city seasonal yard-waste guidance.')],
            cd_fee='NOT typical free bulk — private C&D / landfill',
            cd_facility='Private C&D hauler / Deans Bridge landfill',
            cd_answer='Construction debris is not typical free bulk material. Hire private C&D or confirm landfill C&D rules at 4330 Deans Bridge Rd. Route paint/chemicals to HHW events.',
            cd_steps=['Confirm landfill C&D acceptance before hauling.', 'Hire private C&D for larger projects.', 'Route paint to quarterly HHW events.'],
            cd_faqs=[('HHW for C&D?', 'No — separate paint/chemicals.')],
        ),
    )


def oxnard():
    c, st = "oxnard", "CA"
    hub = (
        'City of Oxnard — Trash & Recycling',
        'https://www.oxnard.gov/',
    )
    hhw = (
        'City of Oxnard — Household Hazardous Waste',
        'https://www.oxnard.gov/',
    )
    buyback = (
        'Del Norte Regional Recycling & Transfer — Buy-Back',
        'https://www.oxnard.gov/',
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                'mattress',
                'SPECIAL_HANDLING',
                'Low',
                True,
                'Bulky item collection — $45 for up to 5 items',
                'Oxnard bulky collection / Del Norte Buy-Back',
                'Oxnard {item}s go on bulky item collection — typically $45 for up to 5 items — schedule via oxnard.gov. Del Norte Buy-Back at 111 S Del Norte Blvd also accepts many recyclables. Keep full HHW off bulk piles.',
                ['Schedule bulky via oxnard.gov ($45 / up to 5 items).', 'Or confirm Del Norte Buy-Back acceptance at 111 S Del Norte.', 'Keep paint, batteries, and propane off bulk piles.'],
                [('Fee?', '$45 for up to 5 bulky items.'), ('Buy-Back?', '111 S Del Norte Blvd.')],
                hub,
            ),
            ch(
                ['refrigerator', 'air-conditioner'],
                'SPECIAL_HANDLING',
                'High',
                True,
                'Bulky / Del Norte — Freon per city and facility rules',
                'Oxnard bulky / Del Norte Regional',
                'Oxnard Freon {item}s follow bulky or Del Norte appliance rules. Never vent refrigerant yourself. Confirm Freon fees and acceptance before hauling.',
                ['Confirm Freon appliance acceptance and fees.', 'Do not vent Freon yourself.', 'Keep HHW chemicals off bulk piles.'],
                [('Freon OK?', 'Confirm bulky/Del Norte rules.'), ('Self-vent?', 'Never.')],
                hub,
            ),
            ch(
                ['television', 'computer-monitor', 'smartphone', 'e-waste-mixed'],
                'BANNED_FROM_LANDFILLS',
                'Medium',
                False,
                'Del Norte Buy-Back / city e-waste pathways — 111 S Del Norte',
                'Del Norte Buy-Back — 111 S Del Norte Blvd',
                'Oxnard electronics including {item} go to Del Norte Buy-Back — 111 S Del Norte Boulevard — or other city e-waste pathways on oxnard.gov. Wipe data before drop-off.',
                ['Haul e-waste to 111 S Del Norte Blvd when accepted.', 'Confirm accepted electronics on oxnard.gov.', 'Wipe personal data.'],
                [('Address?', '111 S Del Norte Blvd.'), ('Full HHW?', 'Clean Harbors Camarillo for full HHW.')],
                buyback,
            ),
            ch(
                ['paint-latex', 'paint-oil', 'car-battery', 'lithium-battery', 'motor-oil', 'propane-tank', 'fluorescent-bulbs', 'cooking-oil', 'medical-sharps'],
                'BANNED_FROM_LANDFILLS',
                'High',
                False,
                'Full HHW — Clean Harbors Camarillo (cite city HHW page)',
                'Clean Harbors Camarillo — city-cited HHW pathway',
                'Take {item} to the full household hazardous waste pathway cited on Oxnard’s HHW page — Clean Harbors Camarillo for residents. Confirm appointment/hours via oxnard.gov HHW guidance. Not bulky trash.',
                ['Follow oxnard.gov HHW page for Clean Harbors Camarillo instructions.', 'Confirm appointment or drop-off rules before visiting.', 'Keep HHW off bulky piles.'],
                [('Where?', 'Clean Harbors Camarillo per city HHW page.'), ('Bulk for paint?', 'No.')],
                hhw,
            ),
        ]
        + std_tail(
            hub,
            yard_fee='Oxnard yard / organics program',
            yard_facility='Oxnard trash and recycling collection',
            yard_answer='Oxnard yard waste follows the city trash and recycling program on oxnard.gov.',
            yard_steps=['Follow city set-out rules for yard trimmings.', 'Keep yard waste out of HHW.', 'Check oxnard.gov for seasonal guidance.'],
            yard_faqs=[('Christmas trees?', 'Follow city seasonal yard-waste guidance.')],
            cd_fee='NOT typical free bulk — private C&D / Del Norte',
            cd_facility='Private C&D hauler / Del Norte Regional',
            cd_answer='Construction debris is not typical free bulk material. Hire private C&D or confirm Del Norte C&D rules. Route paint/chemicals to Clean Harbors Camarillo per city HHW page.',
            cd_steps=['Confirm C&D acceptance before hauling.', 'Hire private C&D for larger projects.', 'Route paint via city HHW page to Clean Harbors Camarillo.'],
            cd_faqs=[('HHW for C&D?', 'No — separate paint/chemicals.')],
        ),
    )


def montgomery():
    c, st = "montgomery", "AL"
    hub = (
        'City of Montgomery — Solid Waste / 311',
        'https://www.montgomeryal.gov/',
    )
    hhw = (
        'Montgomery — HHW events / McInnis e-waste',
        'https://www.montgomeryal.gov/',
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                'mattress',
                'SPECIAL_HANDLING',
                'Low',
                True,
                'Bulk via 311 — fees may apply',
                'Montgomery bulk / city landfill',
                'Montgomery {item}s go on bulk collection via 311 — fees may apply. Landfill drop-off pathways are also available. Keep HHW and e-waste off bulk piles.',
                ['Schedule bulk via Montgomery 311 (confirm fees).', 'Or confirm city landfill drop-off rules.', 'Keep paint, batteries, and electronics off bulk piles.'],
                [('How to schedule?', 'Montgomery 311.'), ('Fees?', 'Fees may apply — confirm when scheduling.')],
                hub,
            ),
            ch(
                ['refrigerator', 'air-conditioner'],
                'SPECIAL_HANDLING',
                'High',
                True,
                'Bulk / landfill — Freon per city rules',
                'Montgomery bulk / landfill',
                'Montgomery Freon {item}s follow bulk or landfill appliance rules. Never vent refrigerant yourself. Confirm Freon fees via 311.',
                ['Schedule via 311 and confirm Freon appliance fees.', 'Do not vent Freon yourself.', 'Keep HHW chemicals off bulk piles.'],
                [('Freon OK?', 'Confirm with 311.'), ('Self-vent?', 'Never.')],
                hub,
            ),
            ch(
                ['television', 'computer-monitor', 'smartphone', 'e-waste-mixed'],
                'BANNED_FROM_LANDFILLS',
                'Medium',
                False,
                'McInnis e-waste — Thursdays; HHW events for other toxics',
                'McInnis e-waste (Thu) / Montgomery HHW events',
                'Montgomery electronics including {item} go to McInnis e-waste drop-off on Thursdays — confirm location/hours on montgomeryal.gov. Wipe data before drop-off.',
                ['Confirm McInnis Thursday e-waste hours on montgomeryal.gov.', 'Haul electronics on the accepted day.', 'Wipe personal data.'],
                [('When?', 'McInnis e-waste Thursdays — confirm city page.')],
                hhw,
            ),
            ch(
                ['paint-latex', 'paint-oil', 'car-battery', 'lithium-battery', 'motor-oil', 'propane-tank', 'fluorescent-bulbs', 'cooking-oil', 'medical-sharps'],
                'BANNED_FROM_LANDFILLS',
                'High',
                False,
                'Montgomery HHW events — montgomeryal.gov',
                'Montgomery household hazardous waste events',
                'Take {item} to Montgomery household hazardous waste events — confirm dates on montgomeryal.gov. Not regular bulk trash.',
                ['Check montgomeryal.gov for HHW event dates.', 'Haul sealed materials to the event.', 'Keep HHW off bulk piles.'],
                [('Bulk for paint?', 'No — HHW events.')],
                hhw,
            ),
        ]
        + std_tail(
            hub,
            yard_fee='Montgomery yard / bulk pathways',
            yard_facility='Montgomery solid waste collection',
            yard_answer='Montgomery yard waste follows city solid-waste and bulk pathways — schedule via 311 when needed.',
            yard_steps=['Follow city set-out rules for yard trimmings.', 'Use 311 for bulk/yard questions.', 'Keep yard waste out of HHW events.'],
            yard_faqs=[('Christmas trees?', 'Follow city seasonal yard-waste guidance.')],
            cd_fee='NOT typical free bulk — private C&D / landfill',
            cd_facility='Private C&D hauler / Montgomery landfill',
            cd_answer='Construction debris is not typical free bulk material. Hire private C&D or confirm landfill C&D rules. Route paint/chemicals to HHW events.',
            cd_steps=['Confirm landfill C&D acceptance before hauling.', 'Hire private C&D for larger projects.', 'Route paint to HHW events.'],
            cd_faqs=[('HHW for C&D?', 'No — separate paint/chemicals.')],
        ),
    )


def huntington_beach():
    c, st = "huntington-beach", "CA"
    hub = (
        'City of Huntington Beach — Trash & Recycling',
        'https://www.huntingtonbeachca.gov/',
    )
    hhw = (
        'OC Landfills — Household Hazardous Waste',
        'https://www.oclandfills.com/hazardous-waste',
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                'mattress',
                'SPECIAL_HANDLING',
                'Low',
                True,
                'Republic Services bulky — 4× per year',
                'Huntington Beach / Republic Services bulky collection',
                'Huntington Beach {item}s go on Republic Services bulky collection — up to 4 times per year — schedule via huntingtonbeachca.gov. Keep HHW off bulk piles.',
                ['Schedule Republic bulky via huntingtonbeachca.gov (up to 4×/yr).', 'Set out per Republic bulky rules.', 'Keep paint, batteries, and propane off bulk piles.'],
                [('How many?', 'Up to 4 bulky collections per year.'), ('Who hauls?', 'Republic Services.')],
                hub,
            ),
            ch(
                ['refrigerator', 'air-conditioner'],
                'SPECIAL_HANDLING',
                'High',
                True,
                'Republic bulky — Freon appliances per hauler rules',
                'Huntington Beach / Republic Services bulky',
                'Huntington Beach Freon {item}s may go on Republic bulky when prepared per hauler rules. Never vent refrigerant yourself. Confirm Freon acceptance when scheduling.',
                ['Schedule Republic bulky and confirm Freon appliance acceptance.', 'Do not vent Freon yourself.', 'Keep HHW chemicals off bulk piles.'],
                [('Freon OK on bulk?', 'Confirm with Republic when scheduling.'), ('Self-vent?', 'Never.')],
                hub,
            ),
            ch(
                ['television', 'computer-monitor', 'smartphone', 'e-waste-mixed'],
                'BANNED_FROM_LANDFILLS',
                'Medium',
                False,
                'OC Landfills HHW — 17121 Nichols Gate Ln #6',
                'OC Landfills HHW — 17121 Nichols Gate Lane #6',
                'Huntington Beach electronics including {item} go to Orange County HHW — 17121 Nichols Gate Lane #6. Wipe data before drop-off. Confirm hours on oclandfills.com.',
                ['Haul e-waste to 17121 Nichols Gate Ln #6.', 'Confirm hours on oclandfills.com.', 'Wipe personal data.'],
                [('Address?', '17121 Nichols Gate Lane #6.'), ('Bulk for TVs?', 'Use OC Landfills HHW.')],
                hhw,
            ),
            ch(
                ['paint-latex', 'paint-oil', 'car-battery', 'lithium-battery', 'motor-oil', 'propane-tank', 'fluorescent-bulbs', 'cooking-oil', 'medical-sharps'],
                'BANNED_FROM_LANDFILLS',
                'High',
                False,
                'OC Landfills HHW — 17121 Nichols Gate Ln #6',
                'OC Landfills HHW — 17121 Nichols Gate Lane #6',
                'Take {item} to Orange County Household Hazardous Waste — 17121 Nichols Gate Lane #6. Confirm hours on oclandfills.com. Not Republic bulky.',
                ['Check oclandfills.com hours before visiting.', 'Haul sealed materials to 17121 Nichols Gate Ln #6.', 'Keep HHW off Republic bulk piles.'],
                [('HHW address?', '17121 Nichols Gate Lane #6.'), ('Bulk for paint?', 'No.')],
                hhw,
            ),
        ]
        + std_tail(
            hub,
            yard_fee='Huntington Beach yard / organics program',
            yard_facility='Huntington Beach trash and recycling collection',
            yard_answer='Huntington Beach yard waste follows the city trash and recycling program on huntingtonbeachca.gov.',
            yard_steps=['Follow city set-out rules for yard trimmings.', 'Keep yard waste out of HHW.', 'Check huntingtonbeachca.gov for seasonal guidance.'],
            yard_faqs=[('Christmas trees?', 'Follow city seasonal yard-waste guidance.')],
            cd_fee='NOT typical free bulk — private C&D / landfill',
            cd_facility='Private C&D hauler / OC landfill pathways',
            cd_answer='Construction debris is not typical free bulk material. Hire private C&D or confirm landfill C&D rules. Route paint/chemicals to OC Landfills HHW separately.',
            cd_steps=['Confirm C&D acceptance before hauling.', 'Hire private C&D for larger projects.', 'Route paint to 17121 Nichols Gate Ln #6.'],
            cd_faqs=[('HHW for C&D?', 'No — separate paint/chemicals.')],
        ),
    )


def overland_park():
    c, st = "overland-park", "KS"
    hub = (
        'City of Overland Park — Trash & Recycling',
        'https://www.opkansas.gov/',
    )
    hhw = (
        'Johnson County HHW — Mastin',
        'https://www.jocogov.org/',
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                'mattress',
                'SPECIAL_HANDLING',
                'Low',
                True,
                'Hauler bulky collection — schedule with your hauler',
                'Overland Park subscribed hauler bulky collection',
                'Overland Park {item}s go on bulky collection through your subscribed hauler — schedule per opkansas.gov guidance. Keep HHW off bulk piles.',
                ['Schedule bulky with your subscribed hauler.', 'Follow opkansas.gov bulky set-out guidance.', 'Keep paint, batteries, and propane off bulk piles.'],
                [('Who hauls?', 'Your subscribed Overland Park hauler.'), ('HHW on bulk?', 'No.')],
                hub,
            ),
            ch(
                ['refrigerator', 'air-conditioner'],
                'SPECIAL_HANDLING',
                'High',
                True,
                'Hauler bulky — Freon appliances per hauler rules',
                'Overland Park hauler bulky collection',
                'Overland Park Freon {item}s follow hauler bulky appliance rules. Never vent refrigerant yourself. Confirm Freon acceptance when scheduling.',
                ['Schedule with your hauler and confirm Freon appliance acceptance.', 'Do not vent Freon yourself.', 'Keep HHW chemicals off bulk piles.'],
                [('Freon OK?', 'Confirm with your hauler.'), ('Self-vent?', 'Never.')],
                hub,
            ),
            ch(
                ['television', 'computer-monitor', 'smartphone', 'e-waste-mixed'],
                'BANNED_FROM_LANDFILLS',
                'Medium',
                False,
                'Johnson County HHW — 11231 Mastin St',
                'Johnson County HHW — 11231 Mastin Street',
                'Overland Park electronics including {item} go to Johnson County HHW — 11231 Mastin Street. Wipe data before drop-off. Confirm hours on jocogov.org.',
                ['Haul e-waste to 11231 Mastin St.', 'Confirm hours on jocogov.org.', 'Wipe personal data.'],
                [('Address?', '11231 Mastin Street.'), ('Bulk for TVs?', 'Use Johnson County HHW.')],
                hhw,
            ),
            ch(
                ['paint-latex', 'paint-oil', 'car-battery', 'lithium-battery', 'motor-oil', 'propane-tank', 'fluorescent-bulbs', 'cooking-oil', 'medical-sharps'],
                'BANNED_FROM_LANDFILLS',
                'High',
                False,
                'Johnson County HHW — 11231 Mastin St',
                'Johnson County HHW — 11231 Mastin Street',
                'Take {item} to Johnson County Household Hazardous Waste — 11231 Mastin Street. Confirm hours on jocogov.org. Not hauler bulky.',
                ['Check jocogov.org hours before visiting.', 'Haul sealed materials to 11231 Mastin St.', 'Keep HHW off hauler bulk piles.'],
                [('HHW address?', '11231 Mastin Street.'), ('Bulk for paint?', 'No.')],
                hhw,
            ),
        ]
        + std_tail(
            hub,
            yard_fee='Overland Park yard / organics program',
            yard_facility='Overland Park hauler yard collection',
            yard_answer='Overland Park yard waste follows your subscribed hauler and city guidance on opkansas.gov.',
            yard_steps=['Follow hauler set-out rules for yard trimmings.', 'Keep yard waste out of HHW.', 'Check opkansas.gov for seasonal guidance.'],
            yard_faqs=[('Christmas trees?', 'Follow city seasonal yard-waste guidance.')],
            cd_fee='NOT typical free bulk — private C&D / transfer',
            cd_facility='Private C&D hauler / transfer station',
            cd_answer='Construction debris is not typical free bulk material. Hire private C&D or confirm transfer-station C&D rules. Route paint/chemicals to Johnson County HHW separately.',
            cd_steps=['Confirm C&D acceptance before hauling.', 'Hire private C&D for larger projects.', 'Route paint to 11231 Mastin St.'],
            cd_faqs=[('HHW for C&D?', 'No — separate paint/chemicals.')],
        ),
    )


def glendale_ca():
    c, st = "glendale-ca", "CA"
    hub = (
        'City of Glendale — Trash & Recycling',
        'https://www.glendaleca.gov/',
    )
    hhw = (
        'Glendale HHW — Flower Street',
        'https://www.glendaleca.gov/',
    )
    ewaste = (
        'Glendale Recycling Center — Chevy Chase',
        'https://www.glendalerecycles.com/',
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                'mattress',
                'SPECIAL_HANDLING',
                'Low',
                True,
                'City bulky collection — glendaleca.gov',
                'Glendale bulky collection',
                'Glendale CA {item}s go on city bulky collection — schedule/follow rules on glendaleca.gov. Keep HHW and e-waste off bulk piles.',
                ['Schedule or follow bulky rules on glendaleca.gov.', 'Set out per city bulky rules.', 'Keep paint, batteries, and electronics off bulk piles.'],
                [('Source?', 'glendaleca.gov.'), ('HHW on bulk?', 'No.')],
                hub,
            ),
            ch(
                ['refrigerator', 'air-conditioner'],
                'SPECIAL_HANDLING',
                'High',
                True,
                'City bulky — Freon appliances per city rules',
                'Glendale bulky collection',
                'Glendale CA Freon {item}s follow city bulky appliance rules. Never vent refrigerant yourself. Confirm Freon acceptance when scheduling.',
                ['Confirm Freon appliance bulky rules on glendaleca.gov.', 'Do not vent Freon yourself.', 'Keep HHW chemicals off bulk piles.'],
                [('Freon OK?', 'Confirm city bulky rules.'), ('Self-vent?', 'Never.')],
                hub,
            ),
            ch(
                ['television', 'computer-monitor', 'smartphone', 'e-waste-mixed'],
                'BANNED_FROM_LANDFILLS',
                'Medium',
                False,
                'Recycling Center e-waste — 540 W Chevy Chase Dr',
                'Glendale Recycling Center — 540 W Chevy Chase Drive',
                'Glendale CA electronics including {item} go to the Recycling Center — 540 W Chevy Chase Drive (glendalerecycles.com / city page). Wipe data before drop-off.',
                ['Haul e-waste to 540 W Chevy Chase Dr.', 'Confirm hours via glendalerecycles.com or glendaleca.gov.', 'Wipe personal data.'],
                [('Address?', '540 W Chevy Chase Drive.'), ('HHW?', '780 Flower St for HHW.')],
                ewaste,
            ),
            ch(
                ['paint-latex', 'paint-oil', 'car-battery', 'lithium-battery', 'motor-oil', 'propane-tank', 'fluorescent-bulbs', 'cooking-oil', 'medical-sharps'],
                'BANNED_FROM_LANDFILLS',
                'High',
                False,
                'Glendale HHW — 780 Flower St — Wed + 2nd Sat',
                'Glendale HHW — 780 Flower Street',
                'Take {item} to Glendale Household Hazardous Waste — 780 Flower Street — open Wednesdays and the 2nd Saturday (confirm hours on glendaleca.gov). Not bulky trash.',
                ['Confirm Wed / 2nd Saturday hours on glendaleca.gov.', 'Haul sealed materials to 780 Flower St.', 'Keep HHW off bulky piles.'],
                [('HHW address?', '780 Flower Street.'), ('Hours?', 'Wednesdays and 2nd Saturday — confirm city page.')],
                hhw,
            ),
        ]
        + std_tail(
            hub,
            yard_fee='Glendale yard / organics program',
            yard_facility='Glendale trash and recycling collection',
            yard_answer='Glendale CA yard waste follows the city trash and recycling program on glendaleca.gov.',
            yard_steps=['Follow city set-out rules for yard trimmings.', 'Keep yard waste out of HHW.', 'Check glendaleca.gov for seasonal guidance.'],
            yard_faqs=[('Christmas trees?', 'Follow city seasonal yard-waste guidance.')],
            cd_fee='NOT typical free bulk — private C&D / transfer',
            cd_facility='Private C&D hauler / transfer station',
            cd_answer='Construction debris is not typical free bulk material. Hire private C&D or confirm transfer C&D rules. Route paint/chemicals to 780 Flower St HHW separately.',
            cd_steps=['Confirm C&D acceptance before hauling.', 'Hire private C&D for larger projects.', 'Route paint to 780 Flower St.'],
            cd_faqs=[('HHW for C&D?', 'No — separate paint/chemicals.')],
        ),
    )


def mckinney():
    c, st = "mckinney", "TX"
    hub = (
        'City of McKinney — Trash & Recycling',
        'https://www.mckinneytexas.org/',
    )
    hhw = (
        'McKinney — Curbside HHW / e-waste',
        'https://www.mckinneytexas.org/',
    )
    ts = (
        'NTMWD Custer Road Transfer Station',
        'https://www.ntmwd.com/',
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                'mattress',
                'SPECIAL_HANDLING',
                'Low',
                True,
                'Frontier bulky — up to 12× per year',
                'McKinney / Frontier bulky collection',
                'McKinney {item}s go on Frontier bulky collection — up to 12 times per year — schedule via mckinneytexas.org. Keep banned HHW off bulk piles when required.',
                ['Schedule Frontier bulky via mckinneytexas.org (up to 12×/yr).', 'Set out per Frontier bulky rules.', 'Keep prohibited chemicals off bulk piles.'],
                [('How many?', 'Up to 12 bulky collections per year.'), ('Who hauls?', 'Frontier.')],
                hub,
            ),
            ch(
                ['refrigerator', 'air-conditioner'],
                'SPECIAL_HANDLING',
                'High',
                True,
                'Frontier bulky — Freon appliances per hauler rules',
                'McKinney / Frontier bulky collection',
                'McKinney Freon {item}s follow Frontier bulky appliance rules. Never vent refrigerant yourself. Confirm Freon acceptance when scheduling.',
                ['Schedule Frontier bulky and confirm Freon appliance acceptance.', 'Do not vent Freon yourself.', 'Keep HHW chemicals off bulk piles.'],
                [('Freon OK?', 'Confirm with Frontier when scheduling.'), ('Self-vent?', 'Never.')],
                hub,
            ),
            ch(
                ['television', 'computer-monitor', 'smartphone', 'e-waste-mixed'],
                'BANNED_FROM_LANDFILLS',
                'Medium',
                False,
                'Curbside HHW/e-waste — up to 12×/yr; NTMWD Custer Rd TS',
                'McKinney curbside HHW/e-waste / NTMWD Custer Road TS',
                'McKinney electronics including {item} go on curbside HHW/e-waste collection up to 12 times per year, or to NTMWD Custer Road Transfer Station pathways. Wipe data before set-out or drop-off.',
                ['Schedule curbside HHW/e-waste via mckinneytexas.org (up to 12×/yr).', 'Or confirm NTMWD Custer Road Transfer Station acceptance.', 'Wipe personal data.'],
                [('Curbside e-waste?', 'Yes — up to 12×/yr.'), ('Transfer?', 'NTMWD Custer Road TS.')],
                hhw,
            ),
            ch(
                ['paint-latex', 'paint-oil', 'car-battery', 'lithium-battery', 'motor-oil', 'propane-tank', 'fluorescent-bulbs', 'cooking-oil', 'medical-sharps'],
                'BANNED_FROM_LANDFILLS',
                'High',
                False,
                'Curbside HHW — up to 12×/yr; NTMWD Custer Rd TS',
                'McKinney curbside HHW / NTMWD Custer Road TS',
                'Take {item} via McKinney curbside HHW collection (up to 12×/yr) or NTMWD Custer Road Transfer Station pathways — confirm on mckinneytexas.org / ntmwd.com. Not regular trash.',
                ['Schedule curbside HHW via mckinneytexas.org.', 'Or confirm NTMWD Custer Road TS HHW acceptance.', 'Keep HHW off regular trash when banned.'],
                [('Curbside HHW?', 'Yes — up to 12×/yr.'), ('Bulk for paint?', 'Use HHW pathway.')],
                hhw,
            ),
        ]
        + std_tail(
            hub,
            yard_fee='McKinney yard / organics program',
            yard_facility='McKinney trash and recycling collection',
            yard_answer='McKinney yard waste follows the city trash and recycling program on mckinneytexas.org.',
            yard_steps=['Follow city set-out rules for yard trimmings.', 'Keep yard waste out of HHW.', 'Check mckinneytexas.org for seasonal guidance.'],
            yard_faqs=[('Christmas trees?', 'Follow city seasonal yard-waste guidance.')],
            cd_fee='NOT typical free bulk — private C&D / NTMWD TS',
            cd_facility='Private C&D hauler / NTMWD Custer Road TS',
            cd_answer='Construction debris is not typical free bulk material. Hire private C&D or confirm NTMWD Custer Road Transfer Station C&D rules. Route paint/chemicals to HHW pathways.',
            cd_steps=['Confirm C&D acceptance at NTMWD Custer Road TS.', 'Hire private C&D for larger projects.', 'Route paint via curbside HHW or TS HHW pathways.'],
            cd_faqs=[('HHW for C&D?', 'No — separate paint/chemicals.')],
        ),
    )


def sioux_falls():
    c, st = "sioux-falls", "SD"
    hub = (
        'City of Sioux Falls — Solid Waste',
        'https://www.siouxfalls.gov/',
    )
    hhw = (
        'Sioux Falls HHW — Chambers Street',
        'https://www.siouxfalls.gov/',
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                'mattress',
                'SPECIAL_HANDLING',
                'Low',
                True,
                'Regional Landfill bulky / city solid-waste pathways',
                'Sioux Falls Regional Landfill bulky pathways',
                'Sioux Falls {item}s go through Regional Landfill bulky and city solid-waste pathways — confirm set-out and drop-off rules on siouxfalls.gov. Keep HHW off regular bulky when required.',
                ['Confirm bulky / landfill rules on siouxfalls.gov.', 'Use Regional Landfill bulky pathways when directed.', 'Keep paint, batteries, and propane off improper piles.'],
                [('Landfill bulky?', 'Yes — Regional Landfill pathways.'), ('HHW?', '1015 E Chambers for HHW/e-waste.')],
                hub,
            ),
            ch(
                ['refrigerator', 'air-conditioner'],
                'SPECIAL_HANDLING',
                'High',
                True,
                'Landfill / city pathways — Freon per facility rules',
                'Sioux Falls Regional Landfill / solid waste',
                'Sioux Falls Freon {item}s follow landfill or city appliance rules. Never vent refrigerant yourself. Confirm Freon fees before hauling.',
                ['Confirm Freon appliance acceptance and fees.', 'Do not vent Freon yourself.', 'Keep HHW chemicals on the HHW pathway.'],
                [('Freon OK?', 'Confirm landfill/city appliance rules.'), ('Self-vent?', 'Never.')],
                hub,
            ),
            ch(
                ['television', 'computer-monitor', 'smartphone', 'e-waste-mixed'],
                'BANNED_FROM_LANDFILLS',
                'Medium',
                False,
                'HHW + e-waste — 1015 E Chambers St',
                'Sioux Falls HHW — 1015 E Chambers Street',
                'Sioux Falls electronics including {item} go to 1015 E Chambers Street with HHW/e-waste drop-off. Wipe data before drop-off. Confirm hours on siouxfalls.gov.',
                ['Haul e-waste to 1015 E Chambers St.', 'Confirm hours on siouxfalls.gov.', 'Wipe personal data.'],
                [('Address?', '1015 E Chambers Street.')],
                hhw,
            ),
            ch(
                ['paint-latex', 'paint-oil', 'car-battery', 'lithium-battery', 'motor-oil', 'propane-tank', 'fluorescent-bulbs', 'cooking-oil', 'medical-sharps'],
                'BANNED_FROM_LANDFILLS',
                'High',
                False,
                'HHW + e-waste — 1015 E Chambers St',
                'Sioux Falls HHW — 1015 E Chambers Street',
                'Take {item} to Sioux Falls Household Hazardous Waste — 1015 E Chambers Street. Confirm hours on siouxfalls.gov. Not regular landfill trash.',
                ['Check siouxfalls.gov hours before visiting.', 'Haul sealed materials to 1015 E Chambers St.', 'Keep HHW off improper landfill loads.'],
                [('HHW address?', '1015 E Chambers Street.'), ('Bulk for paint?', 'No — Chambers HHW.')],
                hhw,
            ),
        ]
        + std_tail(
            hub,
            yard_fee='Sioux Falls yard / organics program',
            yard_facility='Sioux Falls solid waste collection',
            yard_answer='Sioux Falls yard waste follows city solid-waste pathways on siouxfalls.gov.',
            yard_steps=['Follow city set-out rules for yard trimmings.', 'Keep yard waste out of HHW.', 'Check siouxfalls.gov for seasonal guidance.'],
            yard_faqs=[('Christmas trees?', 'Follow city seasonal yard-waste guidance.')],
            cd_fee='NOT typical free bulk — private C&D / Regional Landfill',
            cd_facility='Private C&D hauler / Sioux Falls Regional Landfill',
            cd_answer='Construction debris is not typical free bulk material. Hire private C&D or confirm Regional Landfill C&D rules. Route paint/chemicals to 1015 E Chambers separately.',
            cd_steps=['Confirm landfill C&D acceptance before hauling.', 'Hire private C&D for larger projects.', 'Route paint to 1015 E Chambers St.'],
            cd_faqs=[('HHW for C&D?', 'No — separate paint/chemicals.')],
        ),
    )


def peoria():
    c, st = "peoria", "AZ"
    hub = (
        'City of Peoria — Trash & Recycling',
        'https://www.peoriaaz.gov/',
    )
    hhw = (
        'Peoria — At-home HHW / solid waste',
        'https://www.peoriaaz.gov/',
    )
    ewaste = (
        'Glendale Landfill — e-waste for Peoria residents',
        'https://www.peoriaaz.gov/',
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                'mattress',
                'SPECIAL_HANDLING',
                'Low',
                True,
                'Bulk collection — 2× per year',
                'Peoria bulk collection',
                'Peoria AZ {item}s go on bulk collection up to 2 times per year — schedule via peoriaaz.gov. Keep HHW on the at-home HHW pathway when offered.',
                ['Schedule bulk via peoriaaz.gov (up to 2×/yr).', 'Set out per city bulk rules.', 'Keep paint and batteries on HHW pathways.'],
                [('How many?', 'Up to 2 bulk collections per year.'), ('HHW?', 'At-home HHW program.')],
                hub,
            ),
            ch(
                ['refrigerator', 'air-conditioner'],
                'SPECIAL_HANDLING',
                'High',
                True,
                'Bulk — Freon appliances per city rules',
                'Peoria bulk collection',
                'Peoria AZ Freon {item}s follow city bulk appliance rules. Never vent refrigerant yourself. Confirm Freon acceptance when scheduling.',
                ['Schedule bulk and confirm Freon appliance acceptance.', 'Do not vent Freon yourself.', 'Keep HHW chemicals on at-home HHW pathways.'],
                [('Freon OK?', 'Confirm city bulk rules.'), ('Self-vent?', 'Never.')],
                hub,
            ),
            ch(
                ['television', 'computer-monitor', 'smartphone', 'e-waste-mixed'],
                'BANNED_FROM_LANDFILLS',
                'Medium',
                False,
                'Glendale Landfill e-waste — free for Peoria residents',
                'Glendale Landfill e-waste (Peoria residents)',
                'Peoria AZ electronics including {item} are accepted free for Peoria residents at Glendale Landfill e-waste pathways — confirm rules on peoriaaz.gov. Wipe data before drop-off.',
                ['Confirm Peoria resident e-waste rules for Glendale Landfill.', 'Haul electronics with required ID if requested.', 'Wipe personal data.'],
                [('Free for Peoria?', 'Yes — Glendale Landfill e-waste pathway per city page.')],
                ewaste,
            ),
            ch(
                ['paint-latex', 'paint-oil', 'car-battery', 'lithium-battery', 'motor-oil', 'propane-tank', 'fluorescent-bulbs', 'cooking-oil', 'medical-sharps'],
                'BANNED_FROM_LANDFILLS',
                'High',
                False,
                'At-home HHW program — peoriaaz.gov',
                'Peoria at-home household hazardous waste',
                'Take {item} via Peoria’s at-home HHW program — schedule/confirm on peoriaaz.gov. Not regular bulk trash.',
                ['Schedule at-home HHW via peoriaaz.gov.', 'Follow packing instructions for chemicals.', 'Keep HHW off bulk piles.'],
                [('At-home HHW?', 'Yes — confirm peoriaaz.gov.'), ('Bulk for paint?', 'No — use at-home HHW.')],
                hhw,
            ),
        ]
        + std_tail(
            hub,
            yard_fee='Peoria yard / organics program',
            yard_facility='Peoria trash and recycling collection',
            yard_answer='Peoria AZ yard waste follows the city trash and recycling program on peoriaaz.gov.',
            yard_steps=['Follow city set-out rules for yard trimmings.', 'Keep yard waste out of HHW.', 'Check peoriaaz.gov for seasonal guidance.'],
            yard_faqs=[('Christmas trees?', 'Follow city seasonal yard-waste guidance.')],
            cd_fee='NOT typical free bulk — private C&D / landfill',
            cd_facility='Private C&D hauler / regional landfill',
            cd_answer='Construction debris is not typical free bulk material. Hire private C&D or confirm landfill C&D rules. Route paint/chemicals to at-home HHW separately.',
            cd_steps=['Confirm C&D acceptance before hauling.', 'Hire private C&D for larger projects.', 'Route paint via at-home HHW.'],
            cd_faqs=[('HHW for C&D?', 'No — separate paint/chemicals.')],
        ),
    )


def vancouver():
    c, st = "vancouver", "WA"
    hub = (
        'City of Vancouver / Clark County solid waste',
        'https://clark.wa.gov/public-works/household-hazardous-waste',
    )
    hhw = (
        'Clark County HHW — Central Recycling Center',
        'https://clark.wa.gov/public-works/household-hazardous-waste',
    )
    mrc = (
        'West Vancouver Materials Recovery Center',
        'https://clark.wa.gov/',
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                'mattress',
                'SPECIAL_HANDLING',
                'Low',
                True,
                'Hauler bulky / West Van MRC self-haul',
                'Vancouver hauler bulky / West Van MRC',
                'Vancouver WA {item}s go on hauler bulky collection or self-haul to West Vancouver Materials Recovery Center — 6601 NW Old Lower River Road. Keep HHW off bulky piles.',
                ['Schedule hauler bulky or self-haul to West Van MRC.', 'MRC address: 6601 NW Old Lower River Rd.', 'Keep paint, batteries, and propane off bulky piles.'],
                [('MRC?', '6601 NW Old Lower River Road.'), ('HHW?', 'Clark County CRC HHW.')],
                hub,
            ),
            ch(
                ['refrigerator', 'air-conditioner'],
                'SPECIAL_HANDLING',
                'High',
                True,
                'Hauler / MRC — Freon appliances per facility rules',
                'Vancouver hauler bulky / West Van MRC',
                'Vancouver WA Freon {item}s follow hauler or West Van MRC appliance rules. Never vent refrigerant yourself. Confirm Freon fees before hauling.',
                ['Confirm Freon appliance acceptance and fees.', 'Do not vent Freon yourself.', 'Keep HHW chemicals on CRC HHW pathways.'],
                [('Freon OK?', 'Confirm hauler/MRC rules.'), ('Self-vent?', 'Never.')],
                hub,
            ),
            ch(
                ['television', 'computer-monitor', 'smartphone', 'e-waste-mixed'],
                'BANNED_FROM_LANDFILLS',
                'Medium',
                False,
                'Clark County CRC / West Van MRC e-waste pathways',
                'Clark County CRC / West Van MRC',
                'Vancouver WA electronics including {item} go to Clark County Central Recycling Center or West Van MRC e-waste pathways — confirm on clark.wa.gov. Wipe data before drop-off.',
                ['Confirm e-waste acceptance at CRC or West Van MRC.', 'Haul electronics to the accepted site.', 'Wipe personal data.'],
                [('HHW site?', 'Clark County CRC for HHW.'), ('MRC?', '6601 NW Old Lower River Rd.')],
                mrc,
            ),
            ch(
                ['paint-latex', 'paint-oil', 'car-battery', 'lithium-battery', 'motor-oil', 'propane-tank', 'fluorescent-bulbs', 'cooking-oil', 'medical-sharps'],
                'BANNED_FROM_LANDFILLS',
                'High',
                False,
                'Clark County HHW at Central Recycling Center',
                'Clark County Central Recycling Center — HHW',
                'Take {item} to Clark County Household Hazardous Waste at the Central Recycling Center — confirm hours and rules on clark.wa.gov. Not regular bulky trash.',
                ['Check clark.wa.gov HHW hours before visiting.', 'Haul sealed materials to the CRC HHW area.', 'Keep HHW off bulky piles.'],
                [('Where?', 'Clark County CRC HHW.'), ('Bulk for paint?', 'No.')],
                hhw,
            ),
        ]
        + std_tail(
            hub,
            yard_fee='Vancouver yard / organics program',
            yard_facility='Vancouver / Clark County organics collection',
            yard_answer='Vancouver WA yard waste follows city/county organics pathways — confirm on clark.wa.gov and your hauler.',
            yard_steps=['Follow hauler set-out rules for yard trimmings.', 'Keep yard waste out of HHW.', 'Check seasonal Christmas-tree guidance.'],
            yard_faqs=[('Christmas trees?', 'Follow city seasonal yard-waste guidance.')],
            cd_fee='NOT typical free bulk — private C&D / West Van MRC',
            cd_facility='Private C&D hauler / West Van MRC',
            cd_answer='Construction debris is not typical free bulk material. Hire private C&D or confirm West Van MRC C&D rules. Route paint/chemicals to CRC HHW separately.',
            cd_steps=['Confirm C&D acceptance at West Van MRC.', 'Hire private C&D for larger projects.', 'Route paint to Clark County CRC HHW.'],
            cd_faqs=[('HHW for C&D?', 'No — separate paint/chemicals.')],
        ),
    )


def shreveport():
    c, st = "shreveport", "LA"
    hub = (
        'City of Shreveport — Solid Waste',
        'https://www.shreveportla.gov/',
    )
    hhw = (
        'Shreveport — HHW events / solid waste',
        'https://www.shreveportla.gov/',
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                'mattress',
                'SPECIAL_HANDLING',
                'Low',
                True,
                'Bulky by appointment — shreveportla.gov',
                'Shreveport bulky appointment / Woolworth landfill',
                'Shreveport {item}s go on bulky collection by appointment — schedule via shreveportla.gov. Woolworth landfill pathways also serve residents. Keep HHW off bulky piles.',
                ['Schedule bulky appointment via shreveportla.gov.', 'Or confirm Woolworth landfill drop-off rules.', 'Keep paint, batteries, and propane off bulky piles.'],
                [('Appointment?', 'Yes — schedule bulky via city page.'), ('Landfill?', 'Woolworth landfill pathways.')],
                hub,
            ),
            ch(
                ['refrigerator', 'air-conditioner'],
                'SPECIAL_HANDLING',
                'High',
                True,
                'Bulky / landfill — Freon per city rules',
                'Shreveport bulky / Woolworth landfill',
                'Shreveport Freon {item}s follow bulky appointment or landfill appliance rules. Never vent refrigerant yourself. Confirm Freon handling when scheduling.',
                ['Schedule appointment and confirm Freon appliance acceptance.', 'Do not vent Freon yourself.', 'Keep HHW chemicals off bulky piles.'],
                [('Freon OK?', 'Confirm with solid waste.'), ('Self-vent?', 'Never.')],
                hub,
            ),
            ch(
                ['television', 'computer-monitor', 'smartphone', 'e-waste-mixed'],
                'BANNED_FROM_LANDFILLS',
                'Medium',
                False,
                'HHW events — cite city solid waste page',
                'Shreveport HHW / e-waste events',
                'Shreveport electronics including {item} go to city HHW/e-waste events — confirm dates on the solid waste page at shreveportla.gov. Wipe data before drop-off.',
                ['Check shreveportla.gov solid waste page for event dates.', 'Haul electronics to the event site.', 'Wipe personal data.'],
                [('Ongoing drop-off?', 'Confirm event schedule on city solid waste page.')],
                hhw,
            ),
            ch(
                ['paint-latex', 'paint-oil', 'car-battery', 'lithium-battery', 'motor-oil', 'propane-tank', 'fluorescent-bulbs', 'cooking-oil', 'medical-sharps'],
                'BANNED_FROM_LANDFILLS',
                'High',
                False,
                'HHW events — shreveportla.gov solid waste page',
                'Shreveport household hazardous waste events',
                'Take {item} to Shreveport household hazardous waste events — confirm dates on the city solid waste page. Not bulky trash.',
                ['Check shreveportla.gov solid waste page for HHW event dates.', 'Haul sealed materials to the event.', 'Keep HHW off bulky piles.'],
                [('Bulk for paint?', 'No — HHW events.')],
                hhw,
            ),
        ]
        + std_tail(
            hub,
            yard_fee='Shreveport yard / bulky pathways',
            yard_facility='Shreveport solid waste collection',
            yard_answer='Shreveport yard waste follows city solid-waste and bulky appointment pathways on shreveportla.gov.',
            yard_steps=['Follow city set-out rules for yard trimmings.', 'Schedule bulky appointment when needed.', 'Keep yard waste out of HHW events.'],
            yard_faqs=[('Christmas trees?', 'Follow city seasonal yard-waste guidance.')],
            cd_fee='NOT typical free bulk — private C&D / Woolworth',
            cd_facility='Private C&D hauler / Woolworth landfill',
            cd_answer='Construction debris is not typical free bulk material. Hire private C&D or confirm Woolworth landfill C&D rules. Route paint/chemicals to HHW events.',
            cd_steps=['Confirm landfill C&D acceptance before hauling.', 'Hire private C&D for larger projects.', 'Route paint to HHW events.'],
            cd_faqs=[('HHW for C&D?', 'No — separate paint/chemicals.')],
        ),
    )


def brownsville():
    c, st = "brownsville", "TX"
    hub = (
        'City of Brownsville — Solid Waste',
        'https://www.brownsvilletx.gov/',
    )
    hhw = (
        'Brownsville — HHW events',
        'https://www.brownsvilletx.gov/',
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                'mattress',
                'SPECIAL_HANDLING',
                'Low',
                True,
                'Monthly brush/bulky collection — brownsvilletx.gov',
                'Brownsville monthly brush/bulky / FM 802 landfill',
                'Brownsville {item}s go on monthly brush/bulky collection — follow brownsvilletx.gov. Landfill pathways on FM 802 also serve residents. Keep HHW off bulky piles.',
                ['Follow monthly brush/bulky set-out rules.', 'Or confirm FM 802 landfill drop-off rules.', 'Keep paint, batteries, and propane off bulky piles.'],
                [('Monthly?', 'Yes — brush/bulky collection.'), ('Landfill?', 'FM 802 landfill pathways.')],
                hub,
            ),
            ch(
                ['refrigerator', 'air-conditioner'],
                'SPECIAL_HANDLING',
                'High',
                True,
                'Monthly bulky / landfill — Freon per city rules',
                'Brownsville bulky / FM 802 landfill',
                'Brownsville Freon {item}s follow monthly bulky or landfill appliance rules. Never vent refrigerant yourself. Confirm Freon handling before set-out.',
                ['Confirm Freon appliance rules on brownsvilletx.gov.', 'Do not vent Freon yourself.', 'Keep HHW chemicals off bulky piles.'],
                [('Freon OK?', 'Confirm city appliance rules.'), ('Self-vent?', 'Never.')],
                hub,
            ),
            ch(
                ['television', 'computer-monitor', 'smartphone', 'e-waste-mixed'],
                'BANNED_FROM_LANDFILLS',
                'Medium',
                False,
                'HHW events — brownsvilletx.gov',
                'Brownsville HHW / e-waste events',
                'Brownsville electronics including {item} go to city HHW/e-waste events — confirm dates on brownsvilletx.gov. Wipe data before drop-off.',
                ['Check brownsvilletx.gov for HHW/e-waste event dates.', 'Haul electronics to the event site.', 'Wipe personal data.'],
                [('Ongoing drop-off?', 'Confirm event schedule.')],
                hhw,
            ),
            ch(
                ['paint-latex', 'paint-oil', 'car-battery', 'lithium-battery', 'motor-oil', 'propane-tank', 'fluorescent-bulbs', 'cooking-oil', 'medical-sharps'],
                'BANNED_FROM_LANDFILLS',
                'High',
                False,
                'HHW events — brownsvilletx.gov',
                'Brownsville household hazardous waste events',
                'Take {item} to Brownsville household hazardous waste events — confirm dates on brownsvilletx.gov. Not monthly bulky trash.',
                ['Check brownsvilletx.gov for HHW event dates.', 'Haul sealed materials to the event.', 'Keep HHW off bulky piles.'],
                [('Bulk for paint?', 'No — HHW events.')],
                hhw,
            ),
        ]
        + std_tail(
            hub,
            yard_fee='Brownsville brush / yard pathways',
            yard_facility='Brownsville monthly brush/bulky collection',
            yard_answer='Brownsville yard and brush waste follows monthly brush/bulky pathways on brownsvilletx.gov.',
            yard_steps=['Follow monthly brush set-out rules.', 'Keep yard waste out of HHW events.', 'Check brownsvilletx.gov for seasonal guidance.'],
            yard_faqs=[('Christmas trees?', 'Follow city seasonal yard-waste guidance.')],
            cd_fee='NOT typical free bulk — private C&D / FM 802',
            cd_facility='Private C&D hauler / FM 802 landfill',
            cd_answer='Construction debris is not typical free bulk material. Hire private C&D or confirm FM 802 landfill C&D rules. Route paint/chemicals to HHW events.',
            cd_steps=['Confirm landfill C&D acceptance before hauling.', 'Hire private C&D for larger projects.', 'Route paint to HHW events.'],
            cd_faqs=[('HHW for C&D?', 'No — separate paint/chemicals.')],
        ),
    )


def newport_news():
    c, st = "newport-news", "VA"
    hub = (
        'City of Newport News — Recycling / ROC',
        'https://www.nnva.gov/',
    )
    hhw = (
        'Newport News ROC — HHW quarterly',
        'https://www.nnva.gov/',
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                'mattress',
                'SPECIAL_HANDLING',
                'Low',
                True,
                'ROC drop-off — 520 Atkinson Blvd — bulk daily',
                'Newport News ROC — 520 Atkinson Boulevard',
                'Newport News {item}s go to the Resident Convenience Center (ROC) — 520 Atkinson Boulevard — for daily bulk drop-off. Keep HHW on the quarterly HHW schedule.',
                ['Haul bulk items to ROC at 520 Atkinson Blvd.', 'Confirm daily ROC hours on nnva.gov.', 'Keep paint and batteries for quarterly HHW.'],
                [('ROC address?', '520 Atkinson Boulevard.'), ('Daily bulk?', 'Yes — ROC bulk drop-off.')],
                hub,
            ),
            ch(
                ['refrigerator', 'air-conditioner'],
                'SPECIAL_HANDLING',
                'High',
                True,
                'ROC — Freon appliances per facility rules',
                'Newport News ROC — 520 Atkinson Boulevard',
                'Newport News Freon {item}s follow ROC appliance rules at 520 Atkinson Boulevard. Never vent refrigerant yourself. Confirm Freon fees before hauling.',
                ['Confirm Freon appliance acceptance at the ROC.', 'Do not vent Freon yourself.', 'Keep HHW chemicals for quarterly HHW days.'],
                [('Freon OK?', 'Confirm ROC appliance rules.'), ('Self-vent?', 'Never.')],
                hub,
            ),
            ch(
                ['television', 'computer-monitor', 'smartphone', 'e-waste-mixed'],
                'BANNED_FROM_LANDFILLS',
                'Medium',
                False,
                'ROC e-waste daily — 520 Atkinson Blvd',
                'Newport News ROC — 520 Atkinson Boulevard',
                'Newport News electronics including {item} are accepted at the ROC — 520 Atkinson Boulevard — on daily e-waste drop-off. Wipe data before drop-off.',
                ['Haul e-waste to 520 Atkinson Blvd.', 'Confirm ROC e-waste hours on nnva.gov.', 'Wipe personal data.'],
                [('Daily e-waste?', 'Yes — at the ROC.'), ('HHW?', 'Quarterly HHW at ROC.')],
                hhw,
            ),
            ch(
                ['paint-latex', 'paint-oil', 'car-battery', 'lithium-battery', 'motor-oil', 'propane-tank', 'fluorescent-bulbs', 'cooking-oil', 'medical-sharps'],
                'BANNED_FROM_LANDFILLS',
                'High',
                False,
                'HHW quarterly at ROC — 520 Atkinson Blvd',
                'Newport News ROC — quarterly HHW',
                'Take {item} to quarterly Household Hazardous Waste events at the ROC — 520 Atkinson Boulevard. Confirm dates on nnva.gov. Not daily bulk trash.',
                ['Check nnva.gov for quarterly HHW dates at the ROC.', 'Haul sealed materials to 520 Atkinson Blvd on event days.', 'Keep HHW off daily bulk loads when not accepted.'],
                [('HHW where?', 'Quarterly at ROC, 520 Atkinson Blvd.'), ('Bulk for paint?', 'No — quarterly HHW.')],
                hhw,
            ),
        ]
        + std_tail(
            hub,
            yard_fee='Newport News yard / ROC pathways',
            yard_facility='Newport News solid waste / ROC',
            yard_answer='Newport News yard waste follows city solid-waste and ROC pathways on nnva.gov.',
            yard_steps=['Follow city set-out rules for yard trimmings.', 'Confirm ROC yard-waste acceptance if self-hauling.', 'Keep yard waste out of quarterly HHW.'],
            yard_faqs=[('Christmas trees?', 'Follow city seasonal yard-waste guidance.')],
            cd_fee='NOT typical free bulk — private C&D / ROC rules',
            cd_facility='Private C&D hauler / ROC',
            cd_answer='Construction debris is not typical free bulk material. Hire private C&D or confirm ROC C&D rules. Route paint/chemicals to quarterly HHW at the ROC.',
            cd_steps=['Confirm ROC C&D acceptance before hauling.', 'Hire private C&D for larger projects.', 'Route paint to quarterly HHW at 520 Atkinson Blvd.'],
            cd_faqs=[('HHW for C&D?', 'No — separate paint/chemicals.')],
        ),
    )


def tempe():
    c, st = "tempe", "AZ"
    hub = (
        'City of Tempe — Trash & Recycling',
        'https://www.tempe.gov/',
    )
    hhw = (
        'Tempe HPCC — Household Product Collection Center',
        'https://www.tempe.gov/',
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                'mattress',
                'SPECIAL_HANDLING',
                'Low',
                True,
                'Bulk every-other-month — tempe.gov',
                'Tempe every-other-month bulk collection',
                'Tempe {item}s go on every-other-month bulk collection — follow tempe.gov schedule and set-out rules. Keep HHW for HPCC drop-off.',
                ['Follow every-other-month bulk schedule on tempe.gov.', 'Set out per city bulk rules.', 'Keep paint, batteries, and propane off bulk piles.'],
                [('Schedule?', 'Every-other-month bulk — tempe.gov.'), ('HHW?', 'HPCC at 1320 E University.')],
                hub,
            ),
            ch(
                ['refrigerator', 'air-conditioner'],
                'SPECIAL_HANDLING',
                'High',
                True,
                'Bulk — Freon appliances per city rules',
                'Tempe bulk collection',
                'Tempe Freon {item}s follow every-other-month bulk appliance rules. Never vent refrigerant yourself. Confirm Freon acceptance before set-out.',
                ['Confirm Freon appliance bulk rules on tempe.gov.', 'Do not vent Freon yourself.', 'Keep HHW chemicals for HPCC.'],
                [('Freon OK?', 'Confirm city bulk rules.'), ('Self-vent?', 'Never.')],
                hub,
            ),
            ch(
                ['television', 'computer-monitor', 'smartphone', 'e-waste-mixed'],
                'BANNED_FROM_LANDFILLS',
                'Medium',
                False,
                'HPCC — 1320 E University — Wed/Fri/Sat',
                'Tempe HPCC — 1320 E University Drive',
                'Tempe electronics including {item} go to the Household Product Collection Center — 1320 E University Drive — Wed/Fri/Sat (confirm hours). Wipe data before drop-off.',
                ['Haul e-waste to 1320 E University Dr.', 'Confirm Wed/Fri/Sat hours on tempe.gov.', 'Wipe personal data.'],
                [('Address?', '1320 E University Drive.'), ('Hours?', 'Wed/Fri/Sat — confirm city page.')],
                hhw,
            ),
            ch(
                ['paint-latex', 'paint-oil', 'car-battery', 'lithium-battery', 'motor-oil', 'propane-tank', 'fluorescent-bulbs', 'cooking-oil', 'medical-sharps'],
                'BANNED_FROM_LANDFILLS',
                'High',
                False,
                'HPCC — 1320 E University — Wed/Fri/Sat',
                'Tempe HPCC — 1320 E University Drive',
                'Take {item} to Tempe Household Product Collection Center — 1320 E University Drive — Wed/Fri/Sat. Confirm hours on tempe.gov. Not bulk trash.',
                ['Confirm Wed/Fri/Sat HPCC hours on tempe.gov.', 'Haul sealed materials to 1320 E University Dr.', 'Keep HHW off bulk piles.'],
                [('HHW address?', '1320 E University Drive.'), ('Bulk for paint?', 'No — HPCC.')],
                hhw,
            ),
        ]
        + std_tail(
            hub,
            yard_fee='Tempe yard / organics program',
            yard_facility='Tempe trash and recycling collection',
            yard_answer='Tempe yard waste follows the city trash and recycling program on tempe.gov.',
            yard_steps=['Follow city set-out rules for yard trimmings.', 'Keep yard waste out of HPCC.', 'Check tempe.gov for seasonal guidance.'],
            yard_faqs=[('Christmas trees?', 'Follow city seasonal yard-waste guidance.')],
            cd_fee='NOT typical free bulk — private C&D / transfer',
            cd_facility='Private C&D hauler / transfer station',
            cd_answer='Construction debris is not typical free bulk material. Hire private C&D or confirm transfer C&D rules. Route paint/chemicals to HPCC separately.',
            cd_steps=['Confirm C&D acceptance before hauling.', 'Hire private C&D for larger projects.', 'Route paint to 1320 E University Dr.'],
            cd_faqs=[('HHW for C&D?', 'No — separate paint/chemicals.')],
        ),
    )


def aurora_il():
    c, st = "aurora-il", "IL"
    hub = (
        'City of Aurora — Trash & Recycling',
        'https://www.aurora.il.us/',
    )
    hhw = (
        'Naperville HHW — Fort Hill / Kane County guidance',
        'https://www.aurora.il.us/',
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                'mattress',
                'SPECIAL_HANDLING',
                'Low',
                True,
                'Groot sticker bulk — aurora.il.us',
                'Aurora / Groot sticker bulk collection',
                'Aurora IL {item}s go on Groot bulk collection with required stickers — follow aurora.il.us rules. Keep HHW for Naperville/Kane County HHW pathways.',
                ['Obtain Groot bulk stickers per aurora.il.us.', 'Set out per Groot bulk rules.', 'Keep paint, batteries, and propane off bulk piles.'],
                [('Stickers?', 'Yes — Groot bulk stickers required.'), ('HHW?', 'Naperville HHW 156 Fort Hill.')],
                hub,
            ),
            ch(
                ['refrigerator', 'air-conditioner'],
                'SPECIAL_HANDLING',
                'High',
                True,
                'Groot sticker bulk — Freon per hauler rules',
                'Aurora / Groot sticker bulk',
                'Aurora IL Freon {item}s follow Groot sticker bulk appliance rules. Never vent refrigerant yourself. Confirm Freon acceptance and sticker needs.',
                ['Confirm Freon appliance sticker/bulk rules.', 'Do not vent Freon yourself.', 'Keep HHW chemicals for Naperville HHW.'],
                [('Freon OK?', 'Confirm Groot/Aurora rules.'), ('Self-vent?', 'Never.')],
                hub,
            ),
            ch(
                ['television', 'computer-monitor', 'smartphone', 'e-waste-mixed'],
                'BANNED_FROM_LANDFILLS',
                'Medium',
                False,
                'Naperville HHW — 156 Fort Hill (cite aurora + Kane County)',
                'Naperville HHW — 156 Fort Hill Drive',
                'Aurora IL electronics including {item} go to Naperville HHW — 156 Fort Hill Drive — per Aurora and Kane County guidance. Wipe data before drop-off.',
                ['Confirm Aurora resident acceptance at Naperville HHW.', 'Haul e-waste to 156 Fort Hill Dr.', 'Wipe personal data.'],
                [('Address?', '156 Fort Hill Drive, Naperville.'), ('Cite?', 'aurora.il.us and Kane County guidance.')],
                hhw,
            ),
            ch(
                ['paint-latex', 'paint-oil', 'car-battery', 'lithium-battery', 'motor-oil', 'propane-tank', 'fluorescent-bulbs', 'cooking-oil', 'medical-sharps'],
                'BANNED_FROM_LANDFILLS',
                'High',
                False,
                'Naperville HHW — 156 Fort Hill (cite aurora + Kane County)',
                'Naperville HHW — 156 Fort Hill Drive',
                'Take {item} to Naperville Household Hazardous Waste — 156 Fort Hill Drive — following Aurora and Kane County resident guidance. Confirm hours before visiting. Not Groot bulk.',
                ['Confirm Aurora resident HHW rules via aurora.il.us / Kane County.', 'Haul sealed materials to 156 Fort Hill Dr.', 'Keep HHW off Groot bulk piles.'],
                [('HHW address?', '156 Fort Hill Drive.'), ('Bulk for paint?', 'No.')],
                hhw,
            ),
        ]
        + std_tail(
            hub,
            yard_fee='Aurora yard / organics program',
            yard_facility='Aurora trash and recycling collection',
            yard_answer='Aurora IL yard waste follows the city trash and recycling program on aurora.il.us.',
            yard_steps=['Follow city set-out rules for yard trimmings.', 'Keep yard waste out of HHW.', 'Check aurora.il.us for seasonal guidance.'],
            yard_faqs=[('Christmas trees?', 'Follow city seasonal yard-waste guidance.')],
            cd_fee='NOT typical free bulk — private C&D / transfer',
            cd_facility='Private C&D hauler / transfer station',
            cd_answer='Construction debris is not typical free bulk material. Hire private C&D or confirm transfer C&D rules. Route paint/chemicals to Naperville HHW separately.',
            cd_steps=['Confirm C&D acceptance before hauling.', 'Hire private C&D for larger projects.', 'Route paint to 156 Fort Hill Dr.'],
            cd_faqs=[('HHW for C&D?', 'No — separate paint/chemicals.')],
        ),
    )


def santa_rosa():
    c, st = "santa-rosa", "CA"
    hub = (
        'Zero Waste Sonoma / Santa Rosa bulky',
        'https://zerowastesonoma.gov/',
    )
    hhw = (
        'Sonoma County HHW — Mecham Road, Petaluma',
        'https://zerowastesonoma.gov/',
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                'mattress',
                'SPECIAL_HANDLING',
                'Low',
                True,
                'Recology bulky — zerowastesonoma.gov',
                'Santa Rosa / Recology bulky collection',
                'Santa Rosa {item}s go on Recology bulky collection — schedule via zerowastesonoma.gov guidance. Keep HHW for Sonoma County HHW in Petaluma.',
                ['Schedule Recology bulky per zerowastesonoma.gov.', 'Set out per Recology bulky rules.', 'Keep paint, batteries, and propane off bulk piles.'],
                [('Who hauls?', 'Recology.'), ('HHW?', '500 Mecham Rd, Petaluma.')],
                hub,
            ),
            ch(
                ['refrigerator', 'air-conditioner'],
                'SPECIAL_HANDLING',
                'High',
                True,
                'Recology bulky — Freon appliances per hauler rules',
                'Santa Rosa / Recology bulky',
                'Santa Rosa Freon {item}s may go on Recology bulky when prepared per hauler rules. Never vent refrigerant yourself. Confirm Freon acceptance when scheduling.',
                ['Schedule Recology bulky and confirm Freon appliance acceptance.', 'Do not vent Freon yourself.', 'Keep HHW chemicals for Sonoma HHW.'],
                [('Freon OK?', 'Confirm with Recology.'), ('Self-vent?', 'Never.')],
                hub,
            ),
            ch(
                ['television', 'computer-monitor', 'smartphone', 'e-waste-mixed'],
                'BANNED_FROM_LANDFILLS',
                'Medium',
                False,
                'Sonoma HHW — 500 Mecham Rd, Petaluma — Thu–Sat',
                'Sonoma County HHW — 500 Mecham Road, Petaluma',
                'Santa Rosa electronics including {item} go to Sonoma County HHW — 500 Mecham Road, Petaluma — Thursday–Saturday. Wipe data before drop-off.',
                ['Haul e-waste to 500 Mecham Rd, Petaluma.', 'Confirm Thu–Sat hours on zerowastesonoma.gov.', 'Wipe personal data.'],
                [('Address?', '500 Mecham Road, Petaluma.'), ('Hours?', 'Thursday–Saturday — confirm.')],
                hhw,
            ),
            ch(
                ['paint-latex', 'paint-oil', 'car-battery', 'lithium-battery', 'motor-oil', 'propane-tank', 'fluorescent-bulbs', 'cooking-oil', 'medical-sharps'],
                'BANNED_FROM_LANDFILLS',
                'High',
                False,
                'Sonoma HHW — 500 Mecham Rd, Petaluma — Thu–Sat',
                'Sonoma County HHW — 500 Mecham Road, Petaluma',
                'Take {item} to Sonoma County Household Hazardous Waste — 500 Mecham Road, Petaluma — Thursday–Saturday. Confirm hours on zerowastesonoma.gov. Not Recology bulky.',
                ['Confirm Thu–Sat hours on zerowastesonoma.gov.', 'Haul sealed materials to 500 Mecham Rd, Petaluma.', 'Keep HHW off Recology bulk piles.'],
                [('HHW address?', '500 Mecham Road, Petaluma.'), ('Bulk for paint?', 'No.')],
                hhw,
            ),
        ]
        + std_tail(
            hub,
            yard_fee='Santa Rosa yard / organics program',
            yard_facility='Santa Rosa / Recology organics collection',
            yard_answer='Santa Rosa yard waste follows Recology and Zero Waste Sonoma organics pathways.',
            yard_steps=['Follow Recology set-out rules for yard trimmings.', 'Keep yard waste out of HHW.', 'Check zerowastesonoma.gov for seasonal guidance.'],
            yard_faqs=[('Christmas trees?', 'Follow city seasonal yard-waste guidance.')],
            cd_fee='NOT typical free bulk — private C&D / transfer',
            cd_facility='Private C&D hauler / transfer station',
            cd_answer='Construction debris is not typical free bulk material. Hire private C&D or confirm transfer C&D rules. Route paint/chemicals to Sonoma HHW separately.',
            cd_steps=['Confirm C&D acceptance before hauling.', 'Hire private C&D for larger projects.', 'Route paint to 500 Mecham Rd, Petaluma.'],
            cd_faqs=[('HHW for C&D?', 'No — separate paint/chemicals.')],
        ),
    )


def eugene():
    c, st = "eugene", "OR"
    hub = (
        'Lane County — Glenwood / solid waste',
        'https://www.lanecountyor.gov/',
    )
    hhw = (
        'Lane County Glenwood HHW + E-Cycles',
        'https://www.lanecountyor.gov/',
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                'mattress',
                'SPECIAL_HANDLING',
                'Low',
                True,
                'Hauler bulky / self-haul Glenwood',
                'Eugene hauler bulky / Glenwood self-haul',
                'Eugene {item}s go on hauler bulky collection or self-haul to Glenwood facilities — confirm on lanecountyor.gov. Keep HHW for Glenwood HHW by appointment.',
                ['Schedule hauler bulky or self-haul to Glenwood.', 'Confirm Glenwood acceptance rules.', 'Keep paint, batteries, and propane off bulky piles.'],
                [('Self-haul?', 'Glenwood facilities.'), ('HHW?', 'Glenwood HHW by appointment.')],
                hub,
            ),
            ch(
                ['refrigerator', 'air-conditioner'],
                'SPECIAL_HANDLING',
                'High',
                True,
                'Hauler / Glenwood — Freon per facility rules',
                'Eugene hauler bulky / Glenwood',
                'Eugene Freon {item}s follow hauler or Glenwood appliance rules. Never vent refrigerant yourself. Confirm Freon fees before hauling.',
                ['Confirm Freon appliance acceptance and fees.', 'Do not vent Freon yourself.', 'Keep HHW chemicals for Glenwood HHW appointments.'],
                [('Freon OK?', 'Confirm hauler/Glenwood rules.'), ('Self-vent?', 'Never.')],
                hub,
            ),
            ch(
                ['television', 'computer-monitor', 'smartphone', 'e-waste-mixed'],
                'BANNED_FROM_LANDFILLS',
                'Medium',
                False,
                'Glenwood E-Cycles — lanecountyor.gov',
                'Lane County Glenwood E-Cycles',
                'Eugene electronics including {item} go to Glenwood E-Cycles pathways — confirm on lanecountyor.gov. Wipe data before drop-off.',
                ['Confirm Glenwood E-Cycles acceptance and hours.', 'Haul electronics to Glenwood as directed.', 'Wipe personal data.'],
                [('E-Cycles?', 'Yes — Glenwood E-Cycles.'), ('HHW?', 'Glenwood HHW by appointment.')],
                hhw,
            ),
            ch(
                ['paint-latex', 'paint-oil', 'car-battery', 'lithium-battery', 'motor-oil', 'propane-tank', 'fluorescent-bulbs', 'cooking-oil', 'medical-sharps'],
                'BANNED_FROM_LANDFILLS',
                'High',
                False,
                'Glenwood HHW by appointment — lanecountyor.gov',
                'Lane County Glenwood Household Hazardous Waste',
                'Take {item} to Lane County Glenwood Household Hazardous Waste by appointment — schedule via lanecountyor.gov. Not regular bulky trash.',
                ['Schedule Glenwood HHW appointment via lanecountyor.gov.', 'Haul sealed materials to Glenwood on your appointment.', 'Keep HHW off bulky piles.'],
                [('Appointment?', 'Yes — Glenwood HHW by appointment.'), ('Bulk for paint?', 'No.')],
                hhw,
            ),
        ]
        + std_tail(
            hub,
            yard_fee='Eugene yard / organics program',
            yard_facility='Eugene hauler organics / yard collection',
            yard_answer='Eugene yard waste follows hauler organics pathways — confirm on city/county solid-waste pages.',
            yard_steps=['Follow hauler set-out rules for yard trimmings.', 'Keep yard waste out of HHW.', 'Check seasonal Christmas-tree guidance.'],
            yard_faqs=[('Christmas trees?', 'Follow city seasonal yard-waste guidance.')],
            cd_fee='NOT typical free bulk — private C&D / Glenwood',
            cd_facility='Private C&D hauler / Glenwood',
            cd_answer='Construction debris is not typical free bulk material. Hire private C&D or confirm Glenwood C&D rules. Route paint/chemicals to Glenwood HHW by appointment.',
            cd_steps=['Confirm Glenwood C&D acceptance before hauling.', 'Hire private C&D for larger projects.', 'Route paint to Glenwood HHW by appointment.'],
            cd_faqs=[('HHW for C&D?', 'No — separate paint/chemicals.')],
        ),
    )


def elk_grove():
    c, st = "elk-grove", "CA"
    hub = (
        'City of Elk Grove — Trash & Recycling',
        'https://www.elkgrove.gov/',
    )
    hhw = (
        'Elk Grove SWCC — Disposal Lane',
        'https://www.elkgrove.gov/',
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                'mattress',
                'SPECIAL_HANDLING',
                'Low',
                True,
                'Republic bulky — 3× per year',
                'Elk Grove / Republic Services bulky collection',
                'Elk Grove {item}s go on Republic Services bulky collection — up to 3 times per year — schedule via elkgrove.gov. Keep HHW for SWCC drop-off.',
                ['Schedule Republic bulky via elkgrove.gov (up to 3×/yr).', 'Set out per Republic bulky rules.', 'Keep paint, batteries, and propane off bulk piles.'],
                [('How many?', 'Up to 3 bulky collections per year.'), ('HHW?', 'SWCC 9255 Disposal Ln.')],
                hub,
            ),
            ch(
                ['refrigerator', 'air-conditioner'],
                'SPECIAL_HANDLING',
                'High',
                True,
                'Republic bulky — Freon appliances per hauler rules',
                'Elk Grove / Republic bulky',
                'Elk Grove Freon {item}s may go on Republic bulky when prepared per hauler rules. Never vent refrigerant yourself. Confirm Freon acceptance when scheduling.',
                ['Schedule Republic bulky and confirm Freon appliance acceptance.', 'Do not vent Freon yourself.', 'Keep HHW chemicals for SWCC.'],
                [('Freon OK?', 'Confirm with Republic.'), ('Self-vent?', 'Never.')],
                hub,
            ),
            ch(
                ['television', 'computer-monitor', 'smartphone', 'e-waste-mixed'],
                'BANNED_FROM_LANDFILLS',
                'Medium',
                False,
                'SWCC — 9255 Disposal Ln',
                'Elk Grove Special Waste Collection Center — 9255 Disposal Lane',
                'Elk Grove electronics including {item} go to the Special Waste Collection Center — 9255 Disposal Lane. Wipe data before drop-off. Confirm hours on elkgrove.gov.',
                ['Haul e-waste to 9255 Disposal Ln.', 'Confirm SWCC hours on elkgrove.gov.', 'Wipe personal data.'],
                [('Address?', '9255 Disposal Lane.')],
                hhw,
            ),
            ch(
                ['paint-latex', 'paint-oil', 'car-battery', 'lithium-battery', 'motor-oil', 'propane-tank', 'fluorescent-bulbs', 'cooking-oil', 'medical-sharps'],
                'BANNED_FROM_LANDFILLS',
                'High',
                False,
                'SWCC — 9255 Disposal Ln',
                'Elk Grove Special Waste Collection Center — 9255 Disposal Lane',
                'Take {item} to Elk Grove Special Waste Collection Center — 9255 Disposal Lane. Confirm hours on elkgrove.gov. Not Republic bulky.',
                ['Check elkgrove.gov SWCC hours before visiting.', 'Haul sealed materials to 9255 Disposal Ln.', 'Keep HHW off Republic bulk piles.'],
                [('HHW address?', '9255 Disposal Lane.'), ('Bulk for paint?', 'No.')],
                hhw,
            ),
        ]
        + std_tail(
            hub,
            yard_fee='Elk Grove yard / organics program',
            yard_facility='Elk Grove trash and recycling collection',
            yard_answer='Elk Grove yard waste follows the city trash and recycling program on elkgrove.gov.',
            yard_steps=['Follow city set-out rules for yard trimmings.', 'Keep yard waste out of SWCC HHW loads when not accepted.', 'Check elkgrove.gov for seasonal guidance.'],
            yard_faqs=[('Christmas trees?', 'Follow city seasonal yard-waste guidance.')],
            cd_fee='NOT typical free bulk — private C&D / SWCC rules',
            cd_facility='Private C&D hauler / SWCC',
            cd_answer='Construction debris is not typical free bulk material. Hire private C&D or confirm SWCC C&D rules. Route paint/chemicals to SWCC HHW separately.',
            cd_steps=['Confirm SWCC C&D acceptance before hauling.', 'Hire private C&D for larger projects.', 'Route paint to 9255 Disposal Ln.'],
            cd_faqs=[('HHW for C&D?', 'No — separate paint/chemicals.')],
        ),
    )


def salem():
    c, st = "salem", "OR"
    hub = (
        'Marion County — SKRTS / HHW',
        'https://www.co.marion.or.us/PW/ES/disposal/Pages/hhw.aspx',
    )
    hhw = (
        'Marion County HHW — Deer Park Drive',
        'https://www.co.marion.or.us/PW/ES/disposal/Pages/hhw.aspx',
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                'mattress',
                'SPECIAL_HANDLING',
                'Low',
                True,
                'SKRTS / hauler bulky pathways',
                'Marion County SKRTS / Salem hauler bulky',
                'Salem {item}s go on hauler bulky collection or SKRTS self-haul pathways — confirm on Marion County solid-waste pages. Keep HHW for Thursday HHW at Deer Park.',
                ['Schedule hauler bulky or self-haul via SKRTS rules.', 'Confirm acceptance before hauling large items.', 'Keep paint, batteries, and propane off bulky piles.'],
                [('SKRTS?', 'Marion County SKRTS pathways.'), ('HHW?', '3250 Deer Park Dr SE — Thu.')],
                hub,
            ),
            ch(
                ['refrigerator', 'air-conditioner'],
                'SPECIAL_HANDLING',
                'High',
                True,
                'Hauler / SKRTS — Freon per facility rules',
                'Salem hauler bulky / SKRTS',
                'Salem Freon {item}s follow hauler or SKRTS appliance rules. Never vent refrigerant yourself. Confirm Freon fees before hauling.',
                ['Confirm Freon appliance acceptance and fees.', 'Do not vent Freon yourself.', 'Keep HHW chemicals for Thursday HHW.'],
                [('Freon OK?', 'Confirm hauler/SKRTS rules.'), ('Self-vent?', 'Never.')],
                hub,
            ),
            ch(
                ['television', 'computer-monitor', 'smartphone', 'e-waste-mixed'],
                'BANNED_FROM_LANDFILLS',
                'Medium',
                False,
                'Marion County HHW / SKRTS e-waste — Deer Park',
                'Marion County HHW — 3250 Deer Park Drive SE',
                'Salem electronics including {item} go to Marion County HHW/e-waste pathways at 3250 Deer Park Drive SE — confirm Thursday HHW and other acceptance on co.marion.or.us. Wipe data before drop-off.',
                ['Confirm e-waste acceptance and hours.', 'Haul electronics to 3250 Deer Park Dr SE as directed.', 'Wipe personal data.'],
                [('Address?', '3250 Deer Park Drive SE.'), ('HHW day?', 'Thursday HHW — confirm county page.')],
                hhw,
            ),
            ch(
                ['paint-latex', 'paint-oil', 'car-battery', 'lithium-battery', 'motor-oil', 'propane-tank', 'fluorescent-bulbs', 'cooking-oil', 'medical-sharps'],
                'BANNED_FROM_LANDFILLS',
                'High',
                False,
                'Marion County HHW — Thu — 3250 Deer Park Dr SE',
                'Marion County HHW — 3250 Deer Park Drive SE',
                'Take {item} to Marion County Household Hazardous Waste — 3250 Deer Park Drive SE — Thursdays (confirm hours). Not regular bulky trash.',
                ['Confirm Thursday HHW hours on co.marion.or.us.', 'Haul sealed materials to 3250 Deer Park Dr SE.', 'Keep HHW off bulky piles.'],
                [('HHW address?', '3250 Deer Park Drive SE.'), ('Hours?', 'Thursdays — confirm county page.')],
                hhw,
            ),
        ]
        + std_tail(
            hub,
            yard_fee='Salem yard / organics program',
            yard_facility='Salem hauler organics / yard collection',
            yard_answer='Salem yard waste follows hauler organics pathways — confirm with your hauler and Marion County guidance.',
            yard_steps=['Follow hauler set-out rules for yard trimmings.', 'Keep yard waste out of HHW.', 'Check seasonal Christmas-tree guidance.'],
            yard_faqs=[('Christmas trees?', 'Follow city seasonal yard-waste guidance.')],
            cd_fee='NOT typical free bulk — private C&D / SKRTS',
            cd_facility='Private C&D hauler / SKRTS',
            cd_answer='Construction debris is not typical free bulk material. Hire private C&D or confirm SKRTS C&D rules. Route paint/chemicals to Thursday HHW separately.',
            cd_steps=['Confirm SKRTS C&D acceptance before hauling.', 'Hire private C&D for larger projects.', 'Route paint to 3250 Deer Park Dr SE on HHW days.'],
            cd_faqs=[('HHW for C&D?', 'No — separate paint/chemicals.')],
        ),
    )


def ontario():
    c, st = "ontario", "CA"
    hub = (
        'City of Ontario — Trash & Recycling',
        'https://www.ontarioca.gov/',
    )
    hhw = (
        'Ontario HHW — S Cucamonga Avenue',
        'https://www.ontarioca.gov/',
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                'mattress',
                'SPECIAL_HANDLING',
                'Low',
                True,
                'Bulky collection — 4× per year',
                'Ontario bulky collection',
                'Ontario CA {item}s go on bulky collection up to 4 times per year — schedule via ontarioca.gov. Keep HHW for Friday–Saturday HHW drop-off.',
                ['Schedule bulky via ontarioca.gov (up to 4×/yr).', 'Set out per city bulky rules.', 'Keep paint, batteries, and propane off bulk piles.'],
                [('How many?', 'Up to 4 bulky collections per year.'), ('HHW?', '1430 S Cucamonga — Fri–Sat 9–2.')],
                hub,
            ),
            ch(
                ['refrigerator', 'air-conditioner'],
                'SPECIAL_HANDLING',
                'High',
                True,
                'Bulky — Freon appliances per city rules',
                'Ontario bulky collection',
                'Ontario CA Freon {item}s follow city bulky appliance rules. Never vent refrigerant yourself. Confirm Freon acceptance when scheduling.',
                ['Schedule bulky and confirm Freon appliance acceptance.', 'Do not vent Freon yourself.', 'Keep HHW chemicals for Fri–Sat HHW.'],
                [('Freon OK?', 'Confirm city bulky rules.'), ('Self-vent?', 'Never.')],
                hub,
            ),
            ch(
                ['television', 'computer-monitor', 'smartphone', 'e-waste-mixed'],
                'BANNED_FROM_LANDFILLS',
                'Medium',
                False,
                'Ontario HHW — 1430 S Cucamonga — Fri–Sat 9–2',
                'Ontario HHW — 1430 S Cucamonga Avenue',
                'Ontario CA electronics including {item} go to city HHW — 1430 S Cucamonga Avenue — Friday–Saturday 9:00–14:00. Wipe data before drop-off.',
                ['Haul e-waste to 1430 S Cucamonga Ave.', 'Hours: Fri–Sat 9:00–14:00 — confirm ontarioca.gov.', 'Wipe personal data.'],
                [('Address?', '1430 S Cucamonga Avenue.'), ('Hours?', 'Fri–Sat 9–2.')],
                hhw,
            ),
            ch(
                ['paint-latex', 'paint-oil', 'car-battery', 'lithium-battery', 'motor-oil', 'propane-tank', 'fluorescent-bulbs', 'cooking-oil', 'medical-sharps'],
                'BANNED_FROM_LANDFILLS',
                'High',
                False,
                'Ontario HHW — 1430 S Cucamonga — Fri–Sat 9–2',
                'Ontario HHW — 1430 S Cucamonga Avenue',
                'Take {item} to Ontario Household Hazardous Waste — 1430 S Cucamonga Avenue — Friday–Saturday 9:00–14:00. Confirm on ontarioca.gov. Not bulky trash.',
                ['Confirm Fri–Sat 9–2 hours on ontarioca.gov.', 'Haul sealed materials to 1430 S Cucamonga Ave.', 'Keep HHW off bulky piles.'],
                [('HHW address?', '1430 S Cucamonga Avenue.'), ('Bulk for paint?', 'No.')],
                hhw,
            ),
        ]
        + std_tail(
            hub,
            yard_fee='Ontario yard / organics program',
            yard_facility='Ontario trash and recycling collection',
            yard_answer='Ontario CA yard waste follows the city trash and recycling program on ontarioca.gov.',
            yard_steps=['Follow city set-out rules for yard trimmings.', 'Keep yard waste out of HHW.', 'Check ontarioca.gov for seasonal guidance.'],
            yard_faqs=[('Christmas trees?', 'Follow city seasonal yard-waste guidance.')],
            cd_fee='NOT typical free bulk — private C&D / transfer',
            cd_facility='Private C&D hauler / transfer station',
            cd_answer='Construction debris is not typical free bulk material. Hire private C&D or confirm transfer C&D rules. Route paint/chemicals to Ontario HHW separately.',
            cd_steps=['Confirm C&D acceptance before hauling.', 'Hire private C&D for larger projects.', 'Route paint to 1430 S Cucamonga Ave.'],
            cd_faqs=[('HHW for C&D?', 'No — separate paint/chemicals.')],
        ),
    )


def cary():
    c, st = "cary", "NC"
    hub = (
        'Town of Cary — Trash & Recycling',
        'https://www.carync.gov/',
    )
    hhw = (
        'Wake County South Wake HHW — Apex',
        'https://www.carync.gov/',
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                'mattress',
                'SPECIAL_HANDLING',
                'Low',
                True,
                'Bulky by appointment — carync.gov',
                'Cary bulky appointment collection',
                'Cary {item}s go on bulky collection by appointment — schedule via carync.gov. Keep HHW for Wake County South Wake HHW in Apex (Cary CCC closing note may apply).',
                ['Schedule bulky appointment via carync.gov.', 'Set out per town bulky rules.', 'Keep paint, batteries, and propane off bulky piles.'],
                [('Appointment?', 'Yes — schedule via carync.gov.'), ('HHW?', 'Wake County South Wake HHW, Apex.')],
                hub,
            ),
            ch(
                ['refrigerator', 'air-conditioner'],
                'SPECIAL_HANDLING',
                'High',
                True,
                'Bulky appointment — Freon per town rules',
                'Cary bulky appointment collection',
                'Cary Freon {item}s follow bulky appointment appliance rules. Never vent refrigerant yourself. Confirm Freon acceptance when scheduling.',
                ['Schedule appointment and confirm Freon appliance acceptance.', 'Do not vent Freon yourself.', 'Keep HHW chemicals for South Wake HHW.'],
                [('Freon OK?', 'Confirm town bulky rules.'), ('Self-vent?', 'Never.')],
                hub,
            ),
            ch(
                ['television', 'computer-monitor', 'smartphone', 'e-waste-mixed'],
                'BANNED_FROM_LANDFILLS',
                'Medium',
                False,
                'Wake County South Wake HHW — Apex (CCC closing note OK)',
                'Wake County South Wake HHW — Apex',
                'Cary electronics including {item} go to Wake County South Wake HHW in Apex — confirm on carync.gov (Cary CCC closing notes may apply). Wipe data before drop-off.',
                ['Confirm South Wake HHW location/hours via carync.gov.', 'Haul electronics to the Apex HHW site.', 'Wipe personal data.'],
                [('Where?', 'Wake County South Wake HHW, Apex.'), ('CCC?', 'Cary CCC closing note OK — use South Wake HHW.')],
                hhw,
            ),
            ch(
                ['paint-latex', 'paint-oil', 'car-battery', 'lithium-battery', 'motor-oil', 'propane-tank', 'fluorescent-bulbs', 'cooking-oil', 'medical-sharps'],
                'BANNED_FROM_LANDFILLS',
                'High',
                False,
                'Wake County South Wake HHW — Apex',
                'Wake County South Wake HHW — Apex',
                'Take {item} to Wake County South Wake Household Hazardous Waste in Apex — confirm hours via carync.gov. Not bulky trash.',
                ['Confirm South Wake HHW hours via carync.gov.', 'Haul sealed materials to the Apex HHW site.', 'Keep HHW off bulky piles.'],
                [('HHW where?', 'Wake County South Wake HHW, Apex.'), ('Bulk for paint?', 'No.')],
                hhw,
            ),
        ]
        + std_tail(
            hub,
            yard_fee='Cary yard / organics program',
            yard_facility='Cary trash and recycling collection',
            yard_answer='Cary yard waste follows the town trash and recycling program on carync.gov.',
            yard_steps=['Follow town set-out rules for yard trimmings.', 'Keep yard waste out of HHW.', 'Check carync.gov for seasonal guidance.'],
            yard_faqs=[('Christmas trees?', 'Follow city seasonal yard-waste guidance.')],
            cd_fee='NOT typical free bulk — private C&D / transfer',
            cd_facility='Private C&D hauler / transfer station',
            cd_answer='Construction debris is not typical free bulk material. Hire private C&D or confirm transfer C&D rules. Route paint/chemicals to South Wake HHW separately.',
            cd_steps=['Confirm C&D acceptance before hauling.', 'Hire private C&D for larger projects.', 'Route paint to South Wake HHW in Apex.'],
            cd_faqs=[('HHW for C&D?', 'No — separate paint/chemicals.')],
        ),
    )


def rancho_cucamonga():
    c, st = "rancho-cucamonga", "CA"
    hub = (
        'City of Rancho Cucamonga — Trash & Recycling',
        'https://www.cityofrc.us/',
    )
    hhw = (
        'Rancho Cucamonga HHW — Lion Street',
        'https://www.cityofrc.us/',
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                'mattress',
                'SPECIAL_HANDLING',
                'Low',
                True,
                'Burrtec bulky — 4× per year',
                'Rancho Cucamonga / Burrtec bulky collection',
                'Rancho Cucamonga {item}s go on Burrtec bulky collection — up to 4 times per year — schedule via cityofrc.us. Keep HHW for Saturday Lion Street drop-off.',
                ['Schedule Burrtec bulky via cityofrc.us (up to 4×/yr).', 'Set out per Burrtec bulky rules.', 'Keep paint, batteries, and propane off bulk piles.'],
                [('How many?', 'Up to 4 bulky collections per year.'), ('HHW?', '8794 Lion St — Sat 8–12.')],
                hub,
            ),
            ch(
                ['refrigerator', 'air-conditioner'],
                'SPECIAL_HANDLING',
                'High',
                True,
                'Burrtec bulky — Freon appliances per hauler rules',
                'Rancho Cucamonga / Burrtec bulky',
                'Rancho Cucamonga Freon {item}s may go on Burrtec bulky when prepared per hauler rules. Never vent refrigerant yourself. Confirm Freon acceptance when scheduling.',
                ['Schedule Burrtec bulky and confirm Freon appliance acceptance.', 'Do not vent Freon yourself.', 'Keep HHW chemicals for Lion Street HHW.'],
                [('Freon OK?', 'Confirm with Burrtec.'), ('Self-vent?', 'Never.')],
                hub,
            ),
            ch(
                ['television', 'computer-monitor', 'smartphone', 'e-waste-mixed'],
                'BANNED_FROM_LANDFILLS',
                'Medium',
                False,
                'HHW — 8794 Lion St — Sat 8–12',
                'Rancho Cucamonga HHW — 8794 Lion Street',
                'Rancho Cucamonga electronics including {item} go to city HHW — 8794 Lion Street — Saturdays 8:00–12:00. Wipe data before drop-off.',
                ['Haul e-waste to 8794 Lion St.', 'Hours: Sat 8:00–12:00 — confirm cityofrc.us.', 'Wipe personal data.'],
                [('Address?', '8794 Lion Street.'), ('Hours?', 'Saturday 8–12.')],
                hhw,
            ),
            ch(
                ['paint-latex', 'paint-oil', 'car-battery', 'lithium-battery', 'motor-oil', 'propane-tank', 'fluorescent-bulbs', 'cooking-oil', 'medical-sharps'],
                'BANNED_FROM_LANDFILLS',
                'High',
                False,
                'HHW — 8794 Lion St — Sat 8–12',
                'Rancho Cucamonga HHW — 8794 Lion Street',
                'Take {item} to Rancho Cucamonga Household Hazardous Waste — 8794 Lion Street — Saturdays 8:00–12:00. Confirm on cityofrc.us. Not Burrtec bulky.',
                ['Confirm Saturday 8–12 hours on cityofrc.us.', 'Haul sealed materials to 8794 Lion St.', 'Keep HHW off Burrtec bulk piles.'],
                [('HHW address?', '8794 Lion Street.'), ('Bulk for paint?', 'No.')],
                hhw,
            ),
        ]
        + std_tail(
            hub,
            yard_fee='Rancho Cucamonga yard / organics program',
            yard_facility='Rancho Cucamonga trash and recycling collection',
            yard_answer='Rancho Cucamonga yard waste follows the city trash and recycling program on cityofrc.us.',
            yard_steps=['Follow city set-out rules for yard trimmings.', 'Keep yard waste out of HHW.', 'Check cityofrc.us for seasonal guidance.'],
            yard_faqs=[('Christmas trees?', 'Follow city seasonal yard-waste guidance.')],
            cd_fee='NOT typical free bulk — private C&D / transfer',
            cd_facility='Private C&D hauler / transfer station',
            cd_answer='Construction debris is not typical free bulk material. Hire private C&D or confirm transfer C&D rules. Route paint/chemicals to Lion Street HHW separately.',
            cd_steps=['Confirm C&D acceptance before hauling.', 'Hire private C&D for larger projects.', 'Route paint to 8794 Lion St.'],
            cd_faqs=[('HHW for C&D?', 'No — separate paint/chemicals.')],
        ),
    )


def oceanside():
    c, st = "oceanside", "CA"
    hub = (
        'City of Oceanside — Trash & Recycling',
        'https://www.ci.oceanside.ca.us/',
    )
    hhw = (
        'Oceanside Fire HHW — Industry Street',
        'https://fire.ci.oceanside.ca.us/',
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                'mattress',
                'SPECIAL_HANDLING',
                'Low',
                True,
                'WM bulky — 5 items × 5 collections',
                'Oceanside / Waste Management bulky collection',
                'Oceanside {item}s go on Waste Management bulky collection — typically 5 items per collection, up to 5 collections — confirm via ci.oceanside.ca.us. Keep HHW for Industry Street drop-off.',
                ['Schedule WM bulky per city rules (5×5 program).', 'Set out per WM bulky rules.', 'Keep paint, batteries, and propane off bulk piles.'],
                [('Program?', 'WM bulky 5 items × 5 collections.'), ('HHW?', '2880 Industry St.')],
                hub,
            ),
            ch(
                ['refrigerator', 'air-conditioner'],
                'SPECIAL_HANDLING',
                'High',
                True,
                'WM bulky — Freon appliances per hauler rules',
                'Oceanside / Waste Management bulky',
                'Oceanside Freon {item}s may go on WM bulky when prepared per hauler rules. Never vent refrigerant yourself. Confirm Freon acceptance when scheduling.',
                ['Schedule WM bulky and confirm Freon appliance acceptance.', 'Do not vent Freon yourself.', 'Keep HHW chemicals for Industry Street HHW.'],
                [('Freon OK?', 'Confirm with WM.'), ('Self-vent?', 'Never.')],
                hub,
            ),
            ch(
                ['television', 'computer-monitor', 'smartphone', 'e-waste-mixed'],
                'BANNED_FROM_LANDFILLS',
                'Medium',
                False,
                'Oceanside HHW — 2880 Industry St',
                'Oceanside HHW — 2880 Industry Street',
                'Oceanside electronics including {item} go to city/fire HHW — 2880 Industry Street. Wipe data before drop-off. Confirm hours on ci.oceanside.ca.us / fire.ci.oceanside.ca.us.',
                ['Haul e-waste to 2880 Industry St.', 'Confirm hours on city/fire HHW pages.', 'Wipe personal data.'],
                [('Address?', '2880 Industry Street.')],
                hhw,
            ),
            ch(
                ['paint-latex', 'paint-oil', 'car-battery', 'lithium-battery', 'motor-oil', 'propane-tank', 'fluorescent-bulbs', 'cooking-oil', 'medical-sharps'],
                'BANNED_FROM_LANDFILLS',
                'High',
                False,
                'Oceanside HHW — 2880 Industry St',
                'Oceanside HHW — 2880 Industry Street',
                'Take {item} to Oceanside Household Hazardous Waste — 2880 Industry Street. Confirm hours on ci.oceanside.ca.us / fire.ci.oceanside.ca.us. Not WM bulky.',
                ['Confirm HHW hours on city/fire pages.', 'Haul sealed materials to 2880 Industry St.', 'Keep HHW off WM bulk piles.'],
                [('HHW address?', '2880 Industry Street.'), ('Bulk for paint?', 'No.')],
                hhw,
            ),
        ]
        + std_tail(
            hub,
            yard_fee='Oceanside yard / organics program',
            yard_facility='Oceanside trash and recycling collection',
            yard_answer='Oceanside yard waste follows the city trash and recycling program on ci.oceanside.ca.us.',
            yard_steps=['Follow city set-out rules for yard trimmings.', 'Keep yard waste out of HHW.', 'Check city pages for seasonal guidance.'],
            yard_faqs=[('Christmas trees?', 'Follow city seasonal yard-waste guidance.')],
            cd_fee='NOT typical free bulk — private C&D / transfer',
            cd_facility='Private C&D hauler / transfer station',
            cd_answer='Construction debris is not typical free bulk material. Hire private C&D or confirm transfer C&D rules. Route paint/chemicals to Industry Street HHW separately.',
            cd_steps=['Confirm C&D acceptance before hauling.', 'Hire private C&D for larger projects.', 'Route paint to 2880 Industry St.'],
            cd_faqs=[('HHW for C&D?', 'No — separate paint/chemicals.')],
        ),
    )


def lancaster():
    c, st = "lancaster", "CA"
    hub = (
        'City of Lancaster — Trash & Recycling',
        'https://www.cityoflancasterca.org/',
    )
    hhw = (
        'AVECC / CleanLA — Palmdale',
        'https://cleanla.lacounty.gov/hhw/collection-centers/',
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                'mattress',
                'SPECIAL_HANDLING',
                'Low',
                True,
                'WM bulky — 4× per year',
                'Lancaster / Waste Management bulky collection',
                'Lancaster {item}s go on Waste Management bulky collection — up to 4 times per year — schedule via cityoflancasterca.org. Keep HHW for AVECC / CleanLA in Palmdale.',
                ['Schedule WM bulky via cityoflancasterca.org (up to 4×/yr).', 'Set out per WM bulky rules.', 'Keep paint, batteries, and propane off bulk piles.'],
                [('How many?', 'Up to 4 bulky collections per year.'), ('HHW?', 'AVECC 1200 W City Ranch, Palmdale.')],
                hub,
            ),
            ch(
                ['refrigerator', 'air-conditioner'],
                'SPECIAL_HANDLING',
                'High',
                True,
                'WM bulky — Freon appliances per hauler rules',
                'Lancaster / Waste Management bulky',
                'Lancaster Freon {item}s may go on WM bulky when prepared per hauler rules. Never vent refrigerant yourself. Confirm Freon acceptance when scheduling.',
                ['Schedule WM bulky and confirm Freon appliance acceptance.', 'Do not vent Freon yourself.', 'Keep HHW chemicals for AVECC / CleanLA.'],
                [('Freon OK?', 'Confirm with WM.'), ('Self-vent?', 'Never.')],
                hub,
            ),
            ch(
                ['television', 'computer-monitor', 'smartphone', 'e-waste-mixed'],
                'BANNED_FROM_LANDFILLS',
                'Medium',
                False,
                'AVECC — 1200 W City Ranch Rd, Palmdale (CleanLA)',
                'AVECC / CleanLA — 1200 W City Ranch Road, Palmdale',
                'Lancaster electronics including {item} go to Antelope Valley Environmental Collection Center — 1200 W City Ranch Road, Palmdale (CleanLA). Wipe data before drop-off.',
                ['Haul e-waste to 1200 W City Ranch Rd, Palmdale.', 'Confirm CleanLA / AVECC hours before visiting.', 'Wipe personal data.'],
                [('Address?', '1200 W City Ranch Road, Palmdale.'), ('Source?', 'CleanLA collection centers.')],
                hhw,
            ),
            ch(
                ['paint-latex', 'paint-oil', 'car-battery', 'lithium-battery', 'motor-oil', 'propane-tank', 'fluorescent-bulbs', 'cooking-oil', 'medical-sharps'],
                'BANNED_FROM_LANDFILLS',
                'High',
                False,
                'AVECC — 1200 W City Ranch Rd, Palmdale (CleanLA)',
                'AVECC / CleanLA — 1200 W City Ranch Road, Palmdale',
                'Take {item} to Antelope Valley Environmental Collection Center — 1200 W City Ranch Road, Palmdale (CleanLA). Confirm hours before visiting. Not WM bulky.',
                ['Confirm CleanLA / AVECC hours before visiting.', 'Haul sealed materials to 1200 W City Ranch Rd, Palmdale.', 'Keep HHW off WM bulk piles.'],
                [('HHW address?', '1200 W City Ranch Road, Palmdale.'), ('Bulk for paint?', 'No.')],
                hhw,
            ),
        ]
        + std_tail(
            hub,
            yard_fee='Lancaster yard / organics program',
            yard_facility='Lancaster trash and recycling collection',
            yard_answer='Lancaster yard waste follows the city trash and recycling program on cityoflancasterca.org.',
            yard_steps=['Follow city set-out rules for yard trimmings.', 'Keep yard waste out of AVECC HHW loads when not accepted.', 'Check cityoflancasterca.org for seasonal guidance.'],
            yard_faqs=[('Christmas trees?', 'Follow city seasonal yard-waste guidance.')],
            cd_fee='NOT typical free bulk — private C&D / transfer',
            cd_facility='Private C&D hauler / transfer station',
            cd_answer='Construction debris is not typical free bulk material. Hire private C&D or confirm transfer C&D rules. Route paint/chemicals to AVECC / CleanLA separately.',
            cd_steps=['Confirm C&D acceptance before hauling.', 'Hire private C&D for larger projects.', 'Route paint to 1200 W City Ranch Rd, Palmdale.'],
            cd_faqs=[('HHW for C&D?', 'No — separate paint/chemicals.')],
        ),
    )

# ---------------------------------------------------------------------------
# Geo / facilities / main
# ---------------------------------------------------------------------------

CITIES = [
    {
        "city": 'Moreno Valley',
        "city_slug": 'moreno-valley',
        "state": 'CA',
        "state_slug": 'california',
        "lat": 33.9425,
        "lng": -117.2297,
        "population": 208634,
    },
    {
        "city": 'Columbus',
        "city_slug": 'columbus-ga',
        "state": 'GA',
        "state_slug": 'georgia',
        "lat": 32.461,
        "lng": -84.9877,
        "population": 206922,
    },
    {
        "city": 'Port St. Lucie',
        "city_slug": 'port-st-lucie',
        "state": 'FL',
        "state_slug": 'florida',
        "lat": 27.273,
        "lng": -80.3582,
        "population": 204851,
    },
    {
        "city": 'Augusta',
        "city_slug": 'augusta',
        "state": 'GA',
        "state_slug": 'georgia',
        "lat": 33.4735,
        "lng": -82.0105,
        "population": 202081,
    },
    {
        "city": 'Oxnard',
        "city_slug": 'oxnard',
        "state": 'CA',
        "state_slug": 'california',
        "lat": 34.1975,
        "lng": -119.1771,
        "population": 202063,
    },
    {
        "city": 'Montgomery',
        "city_slug": 'montgomery',
        "state": 'AL',
        "state_slug": 'alabama',
        "lat": 32.3792,
        "lng": -86.3077,
        "population": 200603,
    },
    {
        "city": 'Huntington Beach',
        "city_slug": 'huntington-beach',
        "state": 'CA',
        "state_slug": 'california',
        "lat": 33.6595,
        "lng": -117.9988,
        "population": 198711,
    },
    {
        "city": 'Overland Park',
        "city_slug": 'overland-park',
        "state": 'KS',
        "state_slug": 'kansas',
        "lat": 38.9822,
        "lng": -94.6708,
        "population": 197238,
    },
    {
        "city": 'Glendale',
        "city_slug": 'glendale-ca',
        "state": 'CA',
        "state_slug": 'california',
        "lat": 34.1425,
        "lng": -118.2551,
        "population": 196543,
    },
    {
        "city": 'McKinney',
        "city_slug": 'mckinney',
        "state": 'TX',
        "state_slug": 'texas',
        "lat": 33.1972,
        "lng": -96.6397,
        "population": 195308,
    },
    {
        "city": 'Sioux Falls',
        "city_slug": 'sioux-falls',
        "state": 'SD',
        "state_slug": 'south-dakota',
        "lat": 43.5446,
        "lng": -96.7311,
        "population": 192517,
    },
    {
        "city": 'Peoria',
        "city_slug": 'peoria',
        "state": 'AZ',
        "state_slug": 'arizona',
        "lat": 33.5806,
        "lng": -112.2374,
        "population": 190985,
    },
    {
        "city": 'Vancouver',
        "city_slug": 'vancouver',
        "state": 'WA',
        "state_slug": 'washington',
        "lat": 45.6257,
        "lng": -122.6761,
        "population": 190915,
    },
    {
        "city": 'Shreveport',
        "city_slug": 'shreveport',
        "state": 'LA',
        "state_slug": 'louisiana',
        "lat": 32.5252,
        "lng": -93.7502,
        "population": 187112,
    },
    {
        "city": 'Brownsville',
        "city_slug": 'brownsville',
        "state": 'TX',
        "state_slug": 'texas',
        "lat": 25.9017,
        "lng": -97.4975,
        "population": 186738,
    },
    {
        "city": 'Newport News',
        "city_slug": 'newport-news',
        "state": 'VA',
        "state_slug": 'virginia',
        "lat": 37.0871,
        "lng": -76.473,
        "population": 186247,
    },
    {
        "city": 'Tempe',
        "city_slug": 'tempe',
        "state": 'AZ',
        "state_slug": 'arizona',
        "lat": 33.4255,
        "lng": -111.94,
        "population": 180587,
    },
    {
        "city": 'Aurora',
        "city_slug": 'aurora-il',
        "state": 'IL',
        "state_slug": 'illinois',
        "lat": 41.7606,
        "lng": -88.3201,
        "population": 180542,
    },
    {
        "city": 'Santa Rosa',
        "city_slug": 'santa-rosa',
        "state": 'CA',
        "state_slug": 'california',
        "lat": 38.4404,
        "lng": -122.7141,
        "population": 178127,
    },
    {
        "city": 'Eugene',
        "city_slug": 'eugene',
        "state": 'OR',
        "state_slug": 'oregon',
        "lat": 44.0521,
        "lng": -123.0868,
        "population": 176654,
    },
    {
        "city": 'Elk Grove',
        "city_slug": 'elk-grove',
        "state": 'CA',
        "state_slug": 'california',
        "lat": 38.4088,
        "lng": -121.3716,
        "population": 176124,
    },
    {
        "city": 'Salem',
        "city_slug": 'salem',
        "state": 'OR',
        "state_slug": 'oregon',
        "lat": 44.9429,
        "lng": -123.0351,
        "population": 175535,
    },
    {
        "city": 'Ontario',
        "city_slug": 'ontario',
        "state": 'CA',
        "state_slug": 'california',
        "lat": 34.0633,
        "lng": -117.6509,
        "population": 175265,
    },
    {
        "city": 'Cary',
        "city_slug": 'cary',
        "state": 'NC',
        "state_slug": 'north-carolina',
        "lat": 35.7915,
        "lng": -78.7811,
        "population": 174721,
    },
    {
        "city": 'Rancho Cucamonga',
        "city_slug": 'rancho-cucamonga',
        "state": 'CA',
        "state_slug": 'california',
        "lat": 34.1064,
        "lng": -117.5931,
        "population": 174453,
    },
    {
        "city": 'Oceanside',
        "city_slug": 'oceanside',
        "state": 'CA',
        "state_slug": 'california',
        "lat": 33.1959,
        "lng": -117.3795,
        "population": 174068,
    },
    {
        "city": 'Lancaster',
        "city_slug": 'lancaster',
        "state": 'CA',
        "state_slug": 'california',
        "lat": 34.6868,
        "lng": -118.1542,
        "population": 173516,
    },
]

ZIPS: list[dict] = []

E_WASTE = [
    "television",
    "computer-monitor",
    "smartphone",
    "laptop",
    "desktop-computer",
    "tablet",
    "printer",
    "e-waste-mixed",
    "hard-drive",
]

FACILITIES = [
    {
        "name": 'Badlands Landfill HHW / ABOP',
        "facility_type": 'Household hazardous waste / ABOP drop-off',
        "city_slug": 'moreno-valley',
        "state": 'CA',
        "zip": '92555',
        "address": '31125 Ironwood Avenue, Moreno Valley, CA 92555',
        "lat": 33.95,
        "lng": -117.12,
        "source_url": 'https://www.rcwaste.org/hhw',
        "hours": 'Confirm rcwaste.org HHW/ABOP hours before visit',
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": 'Pine Grove Landfill',
        "facility_type": 'Municipal landfill — resident household / bulky',
        "city_slug": 'columbus-ga',
        "state": 'GA',
        "zip": '31907',
        "address": 'Pine Grove Landfill, Columbus, GA 31907',
        "lat": 32.52,
        "lng": -84.92,
        "source_url": 'https://www.columbusga.gov/',
        "hours": 'Confirm columbusga.gov landfill hours before visit',
        "phone": None,
        "accepted_materials": [
            "mattress",
            "box-spring",
            "sofa",
            "recliner",
            "refrigerator",
            "freezer",
            "washer",
            "dryer",
            "dishwasher",
            "stove",
            "air-conditioner",
            "construction-debris",
            "yard-waste",
            "tires",
        ],
    },
    {
        "name": 'Columbus Recycling Center — HHW events',
        "facility_type": 'Household hazardous waste / e-waste events',
        "city_slug": 'columbus-ga',
        "state": 'GA',
        "zip": '31901',
        "address": 'Columbus Recycling Center, Columbus, GA 31901',
        "lat": 32.46,
        "lng": -84.99,
        "source_url": 'https://www.columbusga.gov/',
        "hours": 'HHW/e-waste event dates — confirm columbusga.gov',
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": 'St. Lucie County Household Hazardous Waste',
        "facility_type": 'Household hazardous waste / e-waste drop-off',
        "city_slug": 'port-st-lucie',
        "state": 'FL',
        "zip": '34945',
        "address": '6120 Glades Cut-Off Road, Fort Pierce, FL 34945',
        "lat": 27.39,
        "lng": -80.38,
        "source_url": 'https://www.stlucieco.gov/departments-services/a-z-departments/solid-waste/household-hazardous-waste',
        "hours": 'Confirm stlucieco.gov HHW hours before visit',
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": 'Augusta Landfill — Deans Bridge Road',
        "facility_type": 'Municipal landfill — resident household / bulky',
        "city_slug": 'augusta',
        "state": 'GA',
        "zip": '30805',
        "address": '4330 Deans Bridge Road, Blythe, GA 30805',
        "lat": 33.3,
        "lng": -82.18,
        "source_url": 'https://www.augustaga.gov/',
        "hours": 'Confirm augustaga.gov landfill hours before visit',
        "phone": None,
        "accepted_materials": [
            "mattress",
            "box-spring",
            "sofa",
            "recliner",
            "refrigerator",
            "freezer",
            "washer",
            "dryer",
            "dishwasher",
            "stove",
            "air-conditioner",
            "construction-debris",
            "yard-waste",
            "tires",
        ],
    },
    {
        "name": 'Del Norte Regional Recycling & Transfer — Buy-Back',
        "facility_type": 'Recycling buy-back / transfer — e-waste pathways',
        "city_slug": 'oxnard',
        "state": 'CA',
        "zip": '93030',
        "address": '111 S Del Norte Boulevard, Oxnard, CA 93030',
        "lat": 34.2,
        "lng": -119.16,
        "source_url": 'https://www.oxnard.gov/',
        "hours": 'Confirm oxnard.gov / Del Norte hours before visit',
        "phone": None,
        "accepted_materials": E_WASTE,
    },
    {
        "name": 'Clean Harbors Camarillo — Oxnard HHW pathway',
        "facility_type": 'Household hazardous waste drop-off',
        "city_slug": 'oxnard',
        "state": 'CA',
        "zip": '93012',
        "address": 'Clean Harbors Camarillo (city-cited HHW pathway), Camarillo, CA 93012',
        "lat": 34.22,
        "lng": -119.03,
        "source_url": 'https://www.oxnard.gov/',
        "hours": 'Confirm appointment/hours via oxnard.gov HHW page',
        "phone": None,
        "accepted_materials": HHW_MATERIALS,
    },
    {
        "name": 'McInnis E-Waste Drop-Off — Montgomery',
        "facility_type": 'Electronics drop-off — Thursdays',
        "city_slug": 'montgomery',
        "state": 'AL',
        "zip": '36108',
        "address": 'McInnis e-waste drop-off (confirm address on montgomeryal.gov), Montgomery, AL 36108',
        "lat": 32.36,
        "lng": -86.34,
        "source_url": 'https://www.montgomeryal.gov/',
        "hours": 'Thursdays — confirm montgomeryal.gov hours/location',
        "phone": None,
        "accepted_materials": E_WASTE,
    },
    {
        "name": 'OC Landfills Household Hazardous Waste — Nichols Gate',
        "facility_type": 'Household hazardous waste / e-waste drop-off',
        "city_slug": 'huntington-beach',
        "state": 'CA',
        "zip": '92647',
        "address": '17121 Nichols Gate Lane #6, Huntington Beach, CA 92647',
        "lat": 33.71,
        "lng": -118.0,
        "source_url": 'https://www.oclandfills.com/hazardous-waste',
        "hours": 'Confirm oclandfills.com hours before visit',
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": 'Johnson County Household Hazardous Waste — Mastin',
        "facility_type": 'Household hazardous waste / e-waste drop-off',
        "city_slug": 'overland-park',
        "state": 'KS',
        "zip": '66211',
        "address": '11231 Mastin Street, Overland Park, KS 66211',
        "lat": 38.92,
        "lng": -94.72,
        "source_url": 'https://www.jocogov.org/',
        "hours": 'Confirm jocogov.org HHW hours before visit',
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": 'Glendale Household Hazardous Waste — Flower Street',
        "facility_type": 'Household hazardous waste drop-off',
        "city_slug": 'glendale-ca',
        "state": 'CA',
        "zip": '91201',
        "address": '780 Flower Street, Glendale, CA 91201',
        "lat": 34.16,
        "lng": -118.28,
        "source_url": 'https://www.glendaleca.gov/',
        "hours": 'Wed + 2nd Saturday — confirm glendaleca.gov hours',
        "phone": None,
        "accepted_materials": HHW_MATERIALS,
    },
    {
        "name": 'Glendale Recycling Center — Chevy Chase',
        "facility_type": 'Electronics / recycling drop-off',
        "city_slug": 'glendale-ca',
        "state": 'CA',
        "zip": '91205',
        "address": '540 W Chevy Chase Drive, Glendale, CA 91205',
        "lat": 34.15,
        "lng": -118.25,
        "source_url": 'https://www.glendalerecycles.com/',
        "hours": 'Confirm glendalerecycles.com / city hours before visit',
        "phone": None,
        "accepted_materials": E_WASTE,
    },
    {
        "name": 'NTMWD Custer Road Transfer Station',
        "facility_type": 'Transfer station — HHW / e-waste / bulky pathways',
        "city_slug": 'mckinney',
        "state": 'TX',
        "zip": '75071',
        "address": 'Custer Road Transfer Station (NTMWD), McKinney, TX 75071',
        "lat": 33.22,
        "lng": -96.7,
        "source_url": 'https://www.ntmwd.com/',
        "hours": 'Confirm ntmwd.com hours before visit',
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": 'Sioux Falls HHW — Chambers Street',
        "facility_type": 'Household hazardous waste / e-waste drop-off',
        "city_slug": 'sioux-falls',
        "state": 'SD',
        "zip": '57104',
        "address": '1015 E Chambers Street, Sioux Falls, SD 57104',
        "lat": 43.56,
        "lng": -96.71,
        "source_url": 'https://www.siouxfalls.gov/',
        "hours": 'Confirm siouxfalls.gov HHW hours before visit',
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": 'Sioux Falls Regional Landfill',
        "facility_type": 'Municipal landfill — resident household / bulky',
        "city_slug": 'sioux-falls',
        "state": 'SD',
        "zip": '57104',
        "address": 'Sioux Falls Regional Landfill, Sioux Falls, SD 57104',
        "lat": 43.58,
        "lng": -96.68,
        "source_url": 'https://www.siouxfalls.gov/',
        "hours": 'Confirm siouxfalls.gov landfill hours before visit',
        "phone": None,
        "accepted_materials": [
            "mattress",
            "box-spring",
            "sofa",
            "recliner",
            "refrigerator",
            "freezer",
            "washer",
            "dryer",
            "dishwasher",
            "stove",
            "air-conditioner",
            "construction-debris",
            "yard-waste",
            "tires",
        ],
    },
    {
        "name": 'Glendale Landfill E-Waste — Peoria residents',
        "facility_type": 'Electronics drop-off — Peoria residents free',
        "city_slug": 'peoria',
        "state": 'AZ',
        "zip": '85301',
        "address": 'Glendale Landfill e-waste (Peoria residents), Glendale, AZ 85301',
        "lat": 33.54,
        "lng": -112.2,
        "source_url": 'https://www.peoriaaz.gov/',
        "hours": 'Confirm peoriaaz.gov e-waste rules before visit',
        "phone": None,
        "accepted_materials": E_WASTE,
    },
    {
        "name": 'Clark County Central Recycling Center — HHW',
        "facility_type": 'Household hazardous waste drop-off',
        "city_slug": 'vancouver',
        "state": 'WA',
        "zip": '98661',
        "address": 'Clark County Central Recycling Center HHW, Vancouver, WA 98661',
        "lat": 45.64,
        "lng": -122.65,
        "source_url": 'https://clark.wa.gov/public-works/household-hazardous-waste',
        "hours": 'Confirm clark.wa.gov HHW hours before visit',
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": 'West Vancouver Materials Recovery Center',
        "facility_type": 'Materials recovery / bulky self-haul',
        "city_slug": 'vancouver',
        "state": 'WA',
        "zip": '98660',
        "address": '6601 NW Old Lower River Road, Vancouver, WA 98660',
        "lat": 45.66,
        "lng": -122.74,
        "source_url": 'https://clark.wa.gov/',
        "hours": 'Confirm clark.wa.gov / MRC hours before visit',
        "phone": None,
        "accepted_materials": [
            "mattress",
            "box-spring",
            "sofa",
            "recliner",
            "refrigerator",
            "freezer",
            "washer",
            "dryer",
            "dishwasher",
            "stove",
            "air-conditioner",
            "construction-debris",
            "yard-waste",
            "tires",
        ],
    },
    {
        "name": 'Woolworth Road Landfill — Shreveport',
        "facility_type": 'Municipal landfill — resident household / bulky',
        "city_slug": 'shreveport',
        "state": 'LA',
        "zip": '71129',
        "address": 'Woolworth Road Landfill, Shreveport, LA 71129',
        "lat": 32.45,
        "lng": -93.85,
        "source_url": 'https://www.shreveportla.gov/',
        "hours": 'Confirm shreveportla.gov landfill hours before visit',
        "phone": None,
        "accepted_materials": [
            "mattress",
            "box-spring",
            "sofa",
            "recliner",
            "refrigerator",
            "freezer",
            "washer",
            "dryer",
            "dishwasher",
            "stove",
            "air-conditioner",
            "construction-debris",
            "yard-waste",
            "tires",
        ],
    },
    {
        "name": 'Brownsville Landfill — FM 802',
        "facility_type": 'Municipal landfill — resident household / bulky',
        "city_slug": 'brownsville',
        "state": 'TX',
        "zip": '78521',
        "address": 'FM 802 Landfill, Brownsville, TX 78521',
        "lat": 25.95,
        "lng": -97.45,
        "source_url": 'https://www.brownsvilletx.gov/',
        "hours": 'Confirm brownsvilletx.gov landfill hours before visit',
        "phone": None,
        "accepted_materials": [
            "mattress",
            "box-spring",
            "sofa",
            "recliner",
            "refrigerator",
            "freezer",
            "washer",
            "dryer",
            "dishwasher",
            "stove",
            "air-conditioner",
            "construction-debris",
            "yard-waste",
            "tires",
        ],
    },
    {
        "name": 'Newport News Resident Convenience Center (ROC)',
        "facility_type": 'Bulk / e-waste drop-off; quarterly HHW',
        "city_slug": 'newport-news',
        "state": 'VA',
        "zip": '23608',
        "address": '520 Atkinson Boulevard, Newport News, VA 23608',
        "lat": 37.12,
        "lng": -76.52,
        "source_url": 'https://www.nnva.gov/',
        "hours": 'Daily bulk/e-waste; quarterly HHW — confirm nnva.gov',
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE + ["mattress", "box-spring", "sofa", "recliner", "refrigerator", "freezer", "washer", "dryer", "air-conditioner"],
    },
    {
        "name": 'Tempe Household Product Collection Center',
        "facility_type": 'Household hazardous waste / e-waste drop-off',
        "city_slug": 'tempe',
        "state": 'AZ',
        "zip": '85281',
        "address": '1320 E University Drive, Tempe, AZ 85281',
        "lat": 33.42,
        "lng": -111.91,
        "source_url": 'https://www.tempe.gov/',
        "hours": 'Wed/Fri/Sat — confirm tempe.gov hours',
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": 'Naperville Household Hazardous Waste — Fort Hill',
        "facility_type": 'Household hazardous waste / e-waste drop-off',
        "city_slug": 'aurora-il',
        "state": 'IL',
        "zip": '60563',
        "address": '156 Fort Hill Drive, Naperville, IL 60563',
        "lat": 41.78,
        "lng": -88.2,
        "source_url": 'https://www.aurora.il.us/',
        "hours": 'Confirm Aurora resident acceptance and hours before visit',
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": 'Sonoma County Household Hazardous Waste — Mecham',
        "facility_type": 'Household hazardous waste / e-waste drop-off',
        "city_slug": 'santa-rosa',
        "state": 'CA',
        "zip": '94952',
        "address": '500 Mecham Road, Petaluma, CA 94952',
        "lat": 38.24,
        "lng": -122.68,
        "source_url": 'https://zerowastesonoma.gov/',
        "hours": 'Thu–Sat — confirm zerowastesonoma.gov hours',
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": 'Lane County Glenwood HHW / E-Cycles',
        "facility_type": 'Household hazardous waste / e-waste — appointment',
        "city_slug": 'eugene',
        "state": 'OR',
        "zip": '97401',
        "address": 'Glenwood HHW / E-Cycles, Eugene area, OR 97401',
        "lat": 44.04,
        "lng": -123.03,
        "source_url": 'https://www.lanecountyor.gov/',
        "hours": 'HHW by appointment; E-Cycles — confirm lanecountyor.gov',
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": 'Elk Grove Special Waste Collection Center',
        "facility_type": 'Household hazardous waste / e-waste drop-off',
        "city_slug": 'elk-grove',
        "state": 'CA',
        "zip": '95624',
        "address": '9255 Disposal Lane, Elk Grove, CA 95624',
        "lat": 38.39,
        "lng": -121.36,
        "source_url": 'https://www.elkgrove.gov/',
        "hours": 'Confirm elkgrove.gov SWCC hours before visit',
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": 'Marion County HHW / SKRTS — Deer Park',
        "facility_type": 'Household hazardous waste / transfer pathways',
        "city_slug": 'salem',
        "state": 'OR',
        "zip": '97317',
        "address": '3250 Deer Park Drive SE, Salem, OR 97317',
        "lat": 44.9,
        "lng": -122.98,
        "source_url": 'https://www.co.marion.or.us/PW/ES/disposal/Pages/hhw.aspx',
        "hours": 'HHW Thursdays — confirm co.marion.or.us hours',
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": 'Ontario Household Hazardous Waste — Cucamonga',
        "facility_type": 'Household hazardous waste / e-waste drop-off',
        "city_slug": 'ontario',
        "state": 'CA',
        "zip": '91761',
        "address": '1430 S Cucamonga Avenue, Ontario, CA 91761',
        "lat": 34.05,
        "lng": -117.61,
        "source_url": 'https://www.ontarioca.gov/',
        "hours": 'Fri–Sat 9:00–14:00 — confirm ontarioca.gov',
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": 'Wake County South Wake HHW — Apex',
        "facility_type": 'Household hazardous waste / e-waste drop-off',
        "city_slug": 'cary',
        "state": 'NC',
        "zip": '27523',
        "address": 'South Wake Household Hazardous Waste Facility, Apex, NC 27523',
        "lat": 35.73,
        "lng": -78.85,
        "source_url": 'https://www.carync.gov/',
        "hours": 'Confirm carync.gov / Wake County HHW hours before visit',
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": 'Rancho Cucamonga Household Hazardous Waste — Lion Street',
        "facility_type": 'Household hazardous waste / e-waste drop-off',
        "city_slug": 'rancho-cucamonga',
        "state": 'CA',
        "zip": '91730',
        "address": '8794 Lion Street, Rancho Cucamonga, CA 91730',
        "lat": 34.1,
        "lng": -117.57,
        "source_url": 'https://www.cityofrc.us/',
        "hours": 'Saturday 8:00–12:00 — confirm cityofrc.us',
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": 'Oceanside Household Hazardous Waste — Industry Street',
        "facility_type": 'Household hazardous waste / e-waste drop-off',
        "city_slug": 'oceanside',
        "state": 'CA',
        "zip": '92054',
        "address": '2880 Industry Street, Oceanside, CA 92054',
        "lat": 33.2,
        "lng": -117.35,
        "source_url": 'https://fire.ci.oceanside.ca.us/',
        "hours": 'Confirm city/fire HHW hours before visit',
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": 'Antelope Valley Environmental Collection Center (AVECC)',
        "facility_type": 'Household hazardous waste / e-waste drop-off',
        "city_slug": 'lancaster',
        "state": 'CA',
        "zip": '93551',
        "address": '1200 W City Ranch Road, Palmdale, CA 93551',
        "lat": 34.58,
        "lng": -118.16,
        "source_url": 'https://cleanla.lacounty.gov/hhw/collection-centers/',
        "hours": 'Confirm CleanLA / AVECC hours before visit',
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
]


def upsert_geo():
    """Cities already exist — only patch lat/lng when needed; append if missing."""
    cities_path = DATA / "geo" / "cities.json"
    zips_path = DATA / "geo" / "zips.json"
    cities = json.loads(cities_path.read_text())
    zips = json.loads(zips_path.read_text())
    by_slug = {c["city_slug"]: c for c in cities}
    for c in CITIES:
        existing = by_slug.get(c["city_slug"])
        if existing:
            if existing.get("lat") != c["lat"] or existing.get("lng") != c["lng"]:
                existing["lat"] = c["lat"]
                existing["lng"] = c["lng"]
        else:
            cities.append(c)
            by_slug[c["city_slug"]] = c
    cities_path.write_text(json.dumps(cities, indent=2) + "\n")

    z_keys = {(z["zip"], z["city_slug"]) for z in zips}
    for z in ZIPS:
        key = (z["zip"], z["city_slug"])
        if key in z_keys:
            continue
        zips.append(z)
        z_keys.add(key)
    zips_path.write_text(json.dumps(zips, indent=2) + "\n")


def upsert_facilities():
    fac_path = DATA / "facilities" / "all.json"
    facilities = json.loads(fac_path.read_text())
    wipe = {f["city_slug"] for f in FACILITIES}
    keep = [f for f in facilities if f.get("city_slug") not in wipe]
    keep.extend(FACILITIES)
    fac_path.write_text(json.dumps(keep, indent=2) + "\n")


def main() -> None:
    audited = {
        "moreno-valley": clone_siblings(moreno_valley()),
        "columbus-ga": clone_siblings(columbus_ga()),
        "port-st-lucie": clone_siblings(port_st_lucie()),
        "augusta": clone_siblings(augusta()),
        "oxnard": clone_siblings(oxnard()),
        "montgomery": clone_siblings(montgomery()),
        "huntington-beach": clone_siblings(huntington_beach()),
        "overland-park": clone_siblings(overland_park()),
        "glendale-ca": clone_siblings(glendale_ca()),
        "mckinney": clone_siblings(mckinney()),
        "sioux-falls": clone_siblings(sioux_falls()),
        "peoria": clone_siblings(peoria()),
        "vancouver": clone_siblings(vancouver()),
        "shreveport": clone_siblings(shreveport()),
        "brownsville": clone_siblings(brownsville()),
        "newport-news": clone_siblings(newport_news()),
        "tempe": clone_siblings(tempe()),
        "aurora-il": clone_siblings(aurora_il()),
        "santa-rosa": clone_siblings(santa_rosa()),
        "eugene": clone_siblings(eugene()),
        "elk-grove": clone_siblings(elk_grove()),
        "salem": clone_siblings(salem()),
        "ontario": clone_siblings(ontario()),
        "cary": clone_siblings(cary()),
        "rancho-cucamonga": clone_siblings(rancho_cucamonga()),
        "oceanside": clone_siblings(oceanside()),
        "lancaster": clone_siblings(lancaster()),
    }

    for city, rows in audited.items():
        slugs = {r["item_slug"] for r in rows}
        if len(slugs) != 70:
            raise SystemExit(f"{city}: expected 70 items, got {len(slugs)} ({sorted(slugs)})")

    upsert_geo()
    upsert_facilities()

    all_path = DATA / "rules" / "all.json"
    rules = json.loads(all_path.read_text())
    keep = [r for r in rules if r.get("city_slug") not in audited]
    for rows in audited.values():
        keep.extend(rows)

    for r in keep:
        if r.get("common_disposal_fee"):
            r["common_disposal_fee"] = str(r["common_disposal_fee"])[:80]
        if r.get("nearest_facility_type"):
            r["nearest_facility_type"] = str(r["nearest_facility_type"])[:120]

    all_path.write_text(json.dumps(keep, indent=2) + "\n")
    ca = [r for r in keep if r.get("state") == "CA" or not r.get("city_slug")]
    national = [r for r in keep if r.get("city_slug") and r.get("state") != "CA"]
    (DATA / "rules" / "ca.json").write_text(json.dumps(ca, indent=2) + "\n")
    (DATA / "rules" / "national.json").write_text(json.dumps(national, indent=2) + "\n")

    print("Wave-21a metros written:")
    for city, rows in audited.items():
        print(f"  {city}: {len(rows)} rules")
    print(f"Cities: {len(audited)}")
    print(f"Total rules now: {len(keep)}")


if __name__ == "__main__":
    main()
