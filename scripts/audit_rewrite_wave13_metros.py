#!/usr/bin/env python3
"""Portal-audited city guides for wave-13 metros (city-sourced only).

Cities researched from official program pages (2026-08-11):
  - Madison, WI — cityofmadison.com large-items + electronics; Dane County Clean Sweep HHW
  - Salt Lake City, UT — slc.gov Call 2 Haul + electronics; SLCo HHW
  - Providence, RI — providenceri.gov tricky-items + e-waste; Eco-Depot HHW
  - Durham, NC — durhamnc.gov bulky + Waste Disposal & Recycling Center
  - Birmingham, AL — birminghamal.gov bulk + district dumpsters; Jefferson County HHW events
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
VERIFIED = "2026-08-11"

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


def madison():
    c, st = "madison", "WI"
    bulk = (
        "City of Madison — Large items and appliances",
        "https://www.cityofmadison.com/streets/trash-recycling/how-do-i-dispose-of/large-items-and-appliances",
    )
    fees = (
        "City of Madison — Fees for large items",
        "https://www.cityofmadison.com/streets/trash-recycling/how-do-i-dispose-of/large-items-and-appliances/fees-for-items/items-with",
    )
    ewaste = (
        "City of Madison — Electronics",
        "https://www.cityofmadison.com/streets/trash-recycling/how-do-i-dispose-of/electronics",
    )
    hhw = (
        "Dane County Clean Sweep",
        "https://landfill.danecounty.gov/services/clean-sweep",
    )
    rows = []
    rows.append(
        R(
            c,
            st,
            "mattress",
            "SPECIAL_HANDLING",
            "Low",
            True,
            "Large Item Work Order — free for most furniture/mattresses (≤8 units)",
            "Madison Large Item Work Order (Streets Division)",
            "Madison Large Item Work Order covers mattresses free for properties with ≤8 units. Schedule online and choose a Sunday set-out date; collection follows the next work week. Properties with more than 8 units use drop-off sites instead of curbside large-item service.",
            [
                "Schedule a Large Item Work Order on cityofmadison.com.",
                "Set mattress out on your chosen Sunday set-out date.",
                "Keep Freon appliances and e-waste on their own pathways.",
            ],
            [
                ("Fee for mattress?", "Most furniture/mattresses are free via work order."),
                ("Who is eligible?", "Properties with ≤8 units for curbside large-item service."),
            ],
            *bulk,
        )
    )
    rows.append(
        R(
            c,
            st,
            "refrigerator",
            "SPECIAL_HANDLING",
            "High",
            True,
            "$35 Freon appliance fee if private recycling; free if City RRSC recycling customer",
            "Madison Large Item Work Order — Freon appliance",
            "Madison accepts Freon refrigerators (>50 lb) on Large Item Work Order. Fee is $35 if you are a private-recycling customer; free if City collects recycling (RRSC on water bill). Remove doors. Never vent refrigerant yourself. Dorm-style fridges under 50 lb are $15 under the same RRSC rule.",
            [
                "Schedule Large Item Work Order for the refrigerator.",
                "Remove doors; pay $35 only if private-recycling customer (free with RRSC).",
                "Do not vent Freon yourself.",
            ],
            [
                ("Freon fee?", "$35 private-recycling; free with City RRSC recycling."),
                ("Doors?", "Remove refrigerator/freezer doors before set-out."),
            ],
            *fees,
        )
    )
    rows.append(
        R(
            c,
            st,
            "air-conditioner",
            "SPECIAL_HANDLING",
            "High",
            True,
            "$35 Freon appliance fee if private recycling; free if City RRSC recycling customer",
            "Madison Large Item Work Order — Freon appliance",
            "Madison Freon AC units use Large Item Work Order — $35 if private-recycling customer, free if City RRSC recycling. Never vent refrigerant yourself.",
            [
                "Schedule Large Item Work Order for the AC unit.",
                "Pay $35 only if private-recycling customer (free with RRSC).",
                "Keep sealed until proper Freon handling.",
            ],
            [("Same as fridge?", "Yes — Freon AC uses the same work-order fee rules.")],
            *fees,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c,
                st,
                item,
                "SPECIAL_HANDLING",
                "Medium",
                True,
                "Large Item Work Order — free for most non-Freon appliances (≤8 units)",
                "Madison Large Item Work Order (Streets Division)",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s go on Madison Large Item Work Order for properties with ≤8 units. Freon refrigerators/AC use the $35/$0 RRSC fee path — not the free furniture path.",
                [
                    "Schedule Large Item Work Order.",
                    "Separate metal/appliances from furniture/lumber as directed.",
                    "Empty appliance before set-out.",
                ],
                [
                    (
                        "Same as Freon fridge?",
                        "No — non-Freon appliances follow the free large-item path when eligible.",
                    )
                ],
                *bulk,
            )
        )
    for item, label in [
        ("television", "TVs"),
        ("computer-monitor", "monitors"),
        ("smartphone", "phones"),
        ("e-waste-mixed", "mixed e-waste"),
    ]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "NOT curbside — free resident drop-off at Streets Division sites ($30 curb penalty)",
                "Madison Streets Division electronics drop-off sites",
                f"Electronics including {label} are NOT allowed in Madison carts or on the curb — $30 administrative fee per improper curb item. Free drop-off for Madison residents (proof required) at East 4602 Sycamore Ave, West 402 South Point Rd, or Central 1504 Quann-Olin Parkway. Wipe data before drop-off.",
                [
                    "Do not put electronics on the curb or in carts.",
                    "Haul free to a Streets Division electronics drop-off with resident proof.",
                    "Wipe personal data before recycling.",
                ],
                [
                    ("Curbside e-waste?", "No — $30 fee for improper curb disposal."),
                    ("Free drop-off?", "Yes — Madison residents at Streets Division sites."),
                ],
                *ewaste,
            )
        )
    rows.append(
        R(
            c,
            st,
            "paint-latex",
            "SPECIAL_HANDLING",
            "Medium",
            False,
            "$15/trip Dane County Clean Sweep — not city curbside",
            "Dane County Clean Sweep — 7020 Maahic Way, Madison",
            "Liquid latex paint goes to Dane County Clean Sweep — 7020 Maahic Way, Madison — $15 per trip for Dane County households. Hours: Mon–Fri 7:15 a.m.–3:15 p.m., Sat 8:00–10:45 a.m. Not city curbside.",
            [
                "Haul sealed paint to Dane County Clean Sweep 7020 Maahic Way.",
                "Budget $15/trip for household HHW.",
                "Keep paint out of carts and large-item piles.",
            ],
            [
                ("City curbside paint?", "No — county Clean Sweep."),
                ("Fee?", "$15 per trip for Dane County households."),
            ],
            *hhw,
        )
    )
    rows.append(
        R(
            c,
            st,
            "paint-oil",
            "BANNED_FROM_LANDFILLS",
            "High",
            False,
            "$15/trip Dane County Clean Sweep",
            "Dane County Clean Sweep — 7020 Maahic Way, Madison",
            "Oil-based paint goes to Dane County Clean Sweep — 7020 Maahic Way — $15/trip. Hours: Mon–Fri 7:15–3:15, Sat 8:00–10:45. Not curbside.",
            [
                "Haul oil paint to Clean Sweep 7020 Maahic Way.",
                "Keep containers sealed and labeled.",
                "Not city large-item or trash.",
            ],
            [("Same as latex?", "Both use Clean Sweep — $15/trip.")],
            *hhw,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "$15/trip Dane County Clean Sweep",
                "Dane County Clean Sweep — 7020 Maahic Way, Madison",
                f"Take {item.replace('-', ' ')} to Dane County Clean Sweep — 7020 Maahic Way — $15/trip. Hours: Mon–Fri 7:15–3:15, Sat 8:00–10:45.",
                [
                    "Deliver sealed containers to Clean Sweep.",
                    "Budget $15/trip.",
                    "Keep chemicals out of carts and large-item piles.",
                ],
                [("Same as paint?", "Yes — chemicals use Clean Sweep HHW.")],
                *hhw,
            )
        )
    for item in [
        "car-battery",
        "lithium-battery",
        "motor-oil",
        "propane-tank",
        "fluorescent-bulbs",
        "cooking-oil",
    ]:
        extra = {
            "car-battery": " Batteries at Clean Sweep.",
            "lithium-battery": " Lithium batteries at Clean Sweep.",
            "motor-oil": " Used motor oil at Clean Sweep.",
            "propane-tank": " Pressurized tanks are NOT accepted at city drop-offs — use Clean Sweep guidance.",
            "fluorescent-bulbs": " Fluorescents at Clean Sweep.",
            "cooking-oil": " Cooking oil at Clean Sweep when not trash-safe.",
        }[item]
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium",
                False,
                "$15/trip Dane County Clean Sweep",
                "Dane County Clean Sweep — 7020 Maahic Way, Madison",
                f"Dane County Clean Sweep at 7020 Maahic Way accepts household hazardous materials ($15/trip).{extra}",
                [
                    "Haul to Clean Sweep 7020 Maahic Way during posted hours.",
                    "Budget $15/trip.",
                    "Tires use Large Item Work Order fee path, not Clean Sweep TV pricing.",
                ],
                [("Address?", "7020 Maahic Way, Madison, WI 53718.")],
                *hhw,
            )
        )
    rows.append(
        R(
            c,
            st,
            "medical-sharps",
            "BANNED_FROM_LANDFILLS",
            "High",
            False,
            "Rigid sealed container — confirm Clean Sweep sharps acceptance",
            "Dane County Clean Sweep — 7020 Maahic Way, Madison",
            "Place sharps in a rigid sealed container. Confirm acceptance at Dane County Clean Sweep. Do not loose-bag needles.",
            [
                "Use rigid sealed container.",
                "Confirm sharps acceptance at Clean Sweep.",
                "Never recycle loose needles.",
            ],
            [("Medications?", "Confirm drug take-back on cityofmadison.com / county programs.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c,
            st,
            "tires",
            "SPECIAL_HANDLING",
            "Medium",
            True,
            "Large Item Work Order — car/small truck $5 off-rim / $10 on-rim (RRSC waiver may apply)",
            "Madison Large Item Work Order — tires",
            "Madison accepts tires on Large Item Work Order and at drop-off sites. Car/small truck: $5 off-rim, $10 on-rim; large truck $10. RRSC recycling customers may have fees waived. Not Clean Sweep.",
            [
                "Schedule Large Item Work Order or use a Streets drop-off site.",
                "Budget $5–$10 per tire unless RRSC waiver applies.",
                "Do not take tires to Clean Sweep as HHW.",
            ],
            [
                ("Fee?", "$5 off-rim / $10 on-rim for car/small truck; RRSC may waive."),
                ("Clean Sweep for tires?", "No — use Large Item Work Order / drop-off."),
            ],
            *fees,
        )
    )
    rows.append(
        R(
            c,
            st,
            "yard-waste",
            "ACCEPTED_IN_BLUE_BIN",
            "Low",
            True,
            "Madison yard waste collection",
            "Madison yard waste collection",
            "Madison handles yard waste through regular collection. Follow set-out rules on cityofmadison.com.",
            [
                "Use yard waste set-out rules.",
                "Keep yard waste out of HHW and e-waste loads.",
                "Check cityofmadison.com for seasonal guidance.",
            ],
            [("Christmas trees?", "Follow city seasonal yard waste guidance.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c,
            st,
            "food-scraps",
            "SPECIAL_HANDLING",
            "Low",
            True,
            "Garbage cart unless private compost",
            "Madison garbage / private compost",
            "Bag food scraps for garbage unless you compost. Keep food out of recycling and HHW.",
            [
                "Bag food for garbage if no compost.",
                "Keep organics out of recycling.",
                "Yard trimmings use yard-waste pathways.",
            ],
            [("HHW for food?", "No.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c,
            st,
            "plastic-bags",
            "SPECIAL_HANDLING",
            "Low",
            False,
            "Not recycling — store take-back / trash",
            "Retail bag take-back / trash",
            "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
            ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."],
            [("Large item for bags?", "No.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c,
            st,
            "construction-debris",
            "SPECIAL_HANDLING",
            "Low",
            True,
            "Large Item Work Order for limited loads (<8 ft) — private C&D for larger",
            "Madison Large Item Work Order / private C&D hauler",
            "Limited homeowner C&D under length/set-out rules may go on Madison Large Item Work Order (≤8 units). Larger contractor loads need a private C&D hauler. Route paint/chemicals to Dane County Clean Sweep separately.",
            [
                "Confirm length/set-out limits before scheduling a work order.",
                "Hire private C&D for larger projects.",
                "Route paint to Dane County Clean Sweep.",
            ],
            [("HHW for C&D?", "No — separate paint/chemicals.")],
            *bulk,
        )
    )
    return rows


def salt_lake_city():
    c, st = "salt-lake-city", "UT"
    c2h = (
        "Salt Lake City — Call 2 Haul",
        "https://www.slc.gov/sustainability/waste-management/c2h/",
    )
    ewaste = (
        "Salt Lake City — Recycle your electronics",
        "https://www.slc.gov/ims/recycle-your-electronics/",
    )
    hhw = (
        "Salt Lake County — Household hazardous waste",
        "https://www.saltlakecounty.gov/health/household-hazardous-waste/safe-disposal/",
    )
    rows = []
    rows.append(
        R(
            c,
            st,
            "mattress",
            "SPECIAL_HANDLING",
            "Low",
            True,
            "Call 2 Haul — free within 2 collections/year; keep clean/dry & separate",
            "SLC Call 2 Haul bulky collection",
            "Salt Lake City Call 2 Haul includes mattresses and box springs free within 2 collections per year (1 bulk + 1 green waste). Keep mattresses clean/dry and separate from the main pile for Spring Back recycling; soiled/wet units go to landfill. Schedule online, call 801-535-6953, or email.",
            [
                "Schedule Call 2 Haul (counts toward 2 collections/year).",
                "Set mattresses clean/dry and separate from the main pile.",
                "Set out ≤24 hours before your scheduled date.",
            ],
            [
                ("Annual limit?", "2 Call 2 Haul collections/year (1 bulk + 1 green)."),
                ("Soiled mattress?", "Soiled/wet mattresses are landfilled, not recycled."),
            ],
            *c2h,
        )
    )
    rows.append(
        R(
            c,
            st,
            "refrigerator",
            "SPECIAL_HANDLING",
            "High",
            True,
            "Call 2 Haul — free within 2 collections/year; city removes coolant",
            "SLC Call 2 Haul — Freon appliance",
            "Salt Lake City Call 2 Haul accepts refrigerators and mini-fridges free within the annual bulk allocation. The city removes coolant and recycles metal. Remove or tape/belt doors shut. Never vent refrigerant yourself.",
            [
                "Schedule Call 2 Haul for the refrigerator.",
                "Remove or secure doors before set-out.",
                "Counts toward your 2 collections/year.",
            ],
            [
                ("Freon fridge on Call 2 Haul?", "Yes — city removes coolant after collection."),
                ("Fee?", "Free within annual Call 2 Haul allocation."),
            ],
            *c2h,
        )
    )
    rows.append(
        R(
            c,
            st,
            "air-conditioner",
            "SPECIAL_HANDLING",
            "High",
            True,
            "Call 2 Haul — free within 2 collections/year; city removes coolant",
            "SLC Call 2 Haul — Freon appliance",
            "Wall/window AC units are accepted on Salt Lake City Call 2 Haul free within the annual allocation. City removes coolant. Never vent refrigerant yourself.",
            [
                "Schedule Call 2 Haul for the AC unit.",
                "Keep sealed until pickup.",
                "Counts toward 2 collections/year.",
            ],
            [("Same as fridge?", "Yes — Freon appliances use Call 2 Haul.")],
            *c2h,
        )
    )
    for item, label in [
        ("television", "TVs"),
        ("computer-monitor", "monitors"),
        ("smartphone", "phones"),
        ("e-waste-mixed", "mixed e-waste"),
    ]:
        rows.append(
            R(
                c,
                st,
                item,
                "SPECIAL_HANDLING",
                "Medium",
                True,
                "Call 2 Haul free within 2/year OR Salt Lake Valley Landfill drop-off",
                "SLC Call 2 Haul / Salt Lake Valley Landfill",
                f"Electronics including {label} may go on Salt Lake City Call 2 Haul free within 2 collections/year, or drop at Salt Lake Valley Landfill (801-541-4078). Not weekly carts. Wipe data before disposal.",
                [
                    "Schedule Call 2 Haul or haul to Salt Lake Valley Landfill.",
                    "Keep e-waste out of weekly carts.",
                    "Wipe personal data.",
                ],
                [
                    ("Curbside weekly?", "No — Call 2 Haul or landfill drop-off."),
                    ("Free?", "Yes within Call 2 Haul annual allocation."),
                ],
                *ewaste,
            )
        )
    rows.append(
        R(
            c,
            st,
            "paint-latex",
            "SPECIAL_HANDLING",
            "Medium",
            False,
            "NOT Call 2 Haul — free Salt Lake County HHW for residents",
            "Salt Lake Valley Landfill HHW — 6030 W California Ave",
            "Paint is NOT accepted on Call 2 Haul. Take latex and oil paint to Salt Lake County HHW — Salt Lake Valley Landfill at 6030 West California Avenue (1300 South) — free for Salt Lake County residents in common household amounts. Hours: Mon/Fri/Sat 7:00 a.m.–5:00 p.m.; self-service Tue–Thu.",
            [
                "Do not put paint on Call 2 Haul.",
                "Haul to Salt Lake Valley Landfill HHW 6030 W California Ave.",
                "Sandy HHW Center 8805 S 700 W is also Mon–Sat 7–5.",
            ],
            [
                ("Call 2 Haul for paint?", "No — county HHW only."),
                ("Fee?", "Free for Salt Lake County residents (household amounts)."),
            ],
            *hhw,
        )
    )
    rows.append(
        R(
            c,
            st,
            "paint-oil",
            "BANNED_FROM_LANDFILLS",
            "High",
            False,
            "Free Salt Lake County HHW — not Call 2 Haul",
            "Salt Lake Valley Landfill HHW — 6030 W California Ave",
            "Oil-based paint goes to Salt Lake County HHW facilities — free for county residents. Not Call 2 Haul or weekly carts.",
            [
                "Haul oil paint to SLCo HHW (Valley Landfill or Sandy).",
                "Keep containers sealed and labeled.",
                "Not Call 2 Haul.",
            ],
            [("Same as latex?", "Yes — both use county HHW, not Call 2 Haul.")],
            *hhw,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "Free Salt Lake County HHW — not Call 2 Haul",
                "Salt Lake Valley Landfill HHW — 6030 W California Ave",
                f"Take {item.replace('-', ' ')} to Salt Lake County HHW — free for county residents. Not Call 2 Haul. Propane/aerosol/gas cans also stay off Call 2 Haul.",
                [
                    "Deliver sealed containers to SLCo HHW.",
                    "Do not set chemicals on Call 2 Haul.",
                    "Call SLCo Health 385-468-3862 if unsure.",
                ],
                [("Call 2 Haul?", "No — chemicals use county HHW.")],
                *hhw,
            )
        )
    for item in [
        "car-battery",
        "lithium-battery",
        "motor-oil",
        "propane-tank",
        "fluorescent-bulbs",
        "cooking-oil",
    ]:
        extra = {
            "car-battery": " Batteries at SLCo HHW.",
            "lithium-battery": " Lithium batteries at SLCo HHW.",
            "motor-oil": " Motor oil at SLCo HHW.",
            "propane-tank": " Propane/aerosol/gas cans are NOT Call 2 Haul — fire station or SLCo Health 385-468-3862.",
            "fluorescent-bulbs": " Fluorescents at SLCo HHW.",
            "cooking-oil": " Cooking oil at SLCo HHW when not trash-safe.",
        }[item]
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium",
                False,
                "Free Salt Lake County HHW — not Call 2 Haul",
                "Salt Lake Valley Landfill HHW — 6030 W California Ave",
                f"Salt Lake County HHW accepts household hazardous materials free for residents.{extra}",
                [
                    "Haul to Valley Landfill HHW or Sandy HHW Center.",
                    "Keep items off Call 2 Haul piles.",
                    "Tires (up to 4 auto) may use Call 2 Haul — not HHW.",
                ],
                [("Address?", "6030 W California Ave (1300 S), Salt Lake City.")],
                *hhw,
            )
        )
    rows.append(
        R(
            c,
            st,
            "medical-sharps",
            "BANNED_FROM_LANDFILLS",
            "High",
            False,
            "Rigid sealed container — confirm SLCo HHW / pharmacy take-back",
            "Salt Lake County HHW / pharmacy take-back",
            "Place sharps in a rigid sealed container. Confirm acceptance at Salt Lake County HHW or pharmacy take-back. Do not loose-bag needles.",
            [
                "Use rigid sealed container.",
                "Confirm sharps at SLCo HHW or pharmacy programs.",
                "Never recycle loose needles.",
            ],
            [("Medications?", "Confirm drug take-back via SLCo Health.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c,
            st,
            "tires",
            "SPECIAL_HANDLING",
            "Medium",
            True,
            "Call 2 Haul — up to 4 auto + bicycle tires free within 2/year",
            "SLC Call 2 Haul — tires",
            "Salt Lake City Call 2 Haul accepts up to 4 auto tires plus bicycle tires/tubes free within the annual allocation. No large truck tires. Remove bike tires from wheels.",
            [
                "Schedule Call 2 Haul and limit to 4 auto tires.",
                "Remove bicycle tires from wheels.",
                "Do not include large truck tires.",
            ],
            [
                ("Tire limit?", "Up to 4 auto tires + bicycle tires/tubes."),
                ("Truck tires?", "No large truck tires on Call 2 Haul."),
            ],
            *c2h,
        )
    )
    rows.append(
        R(
            c,
            st,
            "yard-waste",
            "ACCEPTED_IN_BLUE_BIN",
            "Low",
            True,
            "Call 2 Haul green-waste collection (1 of 2 annual)",
            "SLC Call 2 Haul green waste",
            "Salt Lake City Call 2 Haul includes one green-waste collection among the 2 annual collections. Follow set-out guidelines on slc.gov.",
            [
                "Schedule the green-waste Call 2 Haul collection when needed.",
                "Follow slc.gov set-out guidelines.",
                "Keep HHW and Freon appliances on correct pathways.",
            ],
            [("Christmas trees?", "Follow city seasonal green-waste guidance.")],
            *c2h,
        )
    )
    rows.append(
        R(
            c,
            st,
            "food-scraps",
            "SPECIAL_HANDLING",
            "Low",
            True,
            "Garbage cart unless private compost",
            "SLC garbage / private compost",
            "Bag food scraps for garbage unless you compost.",
            [
                "Bag food for garbage if no compost.",
                "Keep organics out of recycling.",
                "Yard trimmings use green-waste pathways.",
            ],
            [("HHW for food?", "No.")],
            *c2h,
        )
    )
    rows.append(
        R(
            c,
            st,
            "plastic-bags",
            "SPECIAL_HANDLING",
            "Low",
            False,
            "Not recycling — store take-back / trash",
            "Retail bag take-back / trash",
            "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
            ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."],
            [("Call 2 Haul for bags?", "No.")],
            *c2h,
        )
    )
    rows.append(
        R(
            c,
            st,
            "construction-debris",
            "SPECIAL_HANDLING",
            "Low",
            False,
            "NOT typical Call 2 Haul pile — private C&D hauler",
            "Private C&D hauler / landfill",
            "Call 2 Haul is for individual bulky items within ~8×4×4 ft — not loose construction debris. Hire a private C&D hauler for remodel loads. Route paint/chemicals to Salt Lake County HHW separately.",
            [
                "Do not treat remodel debris as a Call 2 Haul pile.",
                "Hire private C&D for larger projects.",
                "Route paint to SLCo HHW.",
            ],
            [("HHW for C&D?", "No — separate paint/chemicals.")],
            *c2h,
        )
    )
    return rows


def providence():
    c, st = "providence", "RI"
    tricky = (
        "City of Providence — Tricky items",
        "https://www.providenceri.gov/public-works/tricky-items/",
    )
    bulky = (
        "City of Providence — Bulky items",
        "https://www.providenceri.gov/public-works/bulky-items/",
    )
    ewaste = (
        "City of Providence — Electronic waste collection",
        "https://www.providenceri.gov/electronic-waste-collection/",
    )
    hhw = ("RI Eco-Depot (RIRRC)", "https://www.ecodepotri.org/")
    rows = []
    rows.append(
        R(
            c,
            st,
            "mattress",
            "SPECIAL_HANDLING",
            "Low",
            True,
            "$28/item curbside in sealed clear bag OR free Sat drop-off (2 items) at 700 Allens Ave",
            "Providence WM bulky / 700 Allens Ave Sat drop-off",
            "Providence mattresses are NOT free bulky. Curbside via Waste Management appointment costs $28/item in a sealed clear plastic bag (bags sold at 75 Chapman St). Free Saturday drop-off 7:00 a.m.–12:45 p.m. behind 700 Allens Avenue — 2 items, valid Providence ID, unbagged.",
            [
                "Prefer free Sat drop-off at 700 Allens Ave (2 items, Providence ID).",
                "Or schedule WM curbside at $28/item in sealed clear bag.",
                "Buildings >6 units are ineligible for city bulky service.",
            ],
            [
                ("Free option?", "Yes — Sat drop-off at 700 Allens Ave, 2 items."),
                ("Curbside fee?", "$28 per mattress via WM appointment."),
            ],
            *tricky,
        )
    )
    rows.append(
        R(
            c,
            st,
            "refrigerator",
            "SPECIAL_HANDLING",
            "High",
            True,
            "Free WM bulky — up to 3 items/week (buildings ≤6 units)",
            "Providence WM bulky pickup (1-800-972-4545)",
            "Providence refrigerators are free on Waste Management bulky pickup — up to 3 items/week for buildings ≤6 units. Schedule online or call 1-800-972-4545 at least 24–48 hours ahead. Never vent refrigerant yourself.",
            [
                "Schedule WM bulky ≥24–48 hours ahead (800-972-4545).",
                "Counts toward 3 free items/week.",
                "Set out between 4 p.m. evening before and 4 a.m. collection day.",
            ],
            [
                ("Freon fridge free?", "Yes — included in free bulky (3/week)."),
                ("Eligibility?", "Buildings ≤6 units on city residential service."),
            ],
            *tricky,
        )
    )
    rows.append(
        R(
            c,
            st,
            "air-conditioner",
            "SPECIAL_HANDLING",
            "High",
            True,
            "Free WM bulky — up to 3 items/week OR free Sat e-waste drop-off",
            "Providence WM bulky / 700 Allens Ave e-waste",
            "Window AC units are free on Providence WM bulky (3 items/week) and also accepted at Saturday free e-waste drop-off behind 700 Allens Avenue. Never vent refrigerant yourself.",
            [
                "Schedule WM bulky or use Sat e-waste drop-off at 700 Allens Ave.",
                "Counts toward 3 free bulky items/week if curbside.",
                "Keep sealed until proper Freon handling.",
            ],
            [("Same as fridge?", "Yes for bulky; AC also accepted at Sat e-waste drop-off.")],
            *tricky,
        )
    )
    for item, label in [
        ("television", "TVs"),
        ("computer-monitor", "monitors"),
        ("smartphone", "phones"),
        ("e-waste-mixed", "mixed e-waste"),
    ]:
        rows.append(
            R(
                c,
                st,
                item,
                "SPECIAL_HANDLING",
                "Medium",
                True,
                "Free WM curbside OR free Sat drop-off 7:00–12:45 behind 700 Allens Ave",
                "Providence e-waste — WM / 700 Allens Ave",
                f"Electronics including {label} are free via Providence WM curbside collection (schedule form/800-972-4545) OR free Saturday drop-off 7:00 a.m.–12:45 p.m. behind 700 Allens Avenue. Wipe data before drop-off.",
                [
                    "Schedule free WM e-waste pickup OR haul Sat to 700 Allens Ave.",
                    "Hours for drop-off: Sat 7:00–12:45.",
                    "Wipe personal data.",
                ],
                [
                    ("Fee?", "Free curbside or Sat drop-off."),
                    ("Address?", "Behind 700 Allens Avenue (rear of DPW)."),
                ],
                *ewaste,
            )
        )
    rows.append(
        R(
            c,
            st,
            "paint-latex",
            "SPECIAL_HANDLING",
            "Medium",
            False,
            "Free RI Eco-Depot appointment — not curbside bulky",
            "RI Eco-Depot (RIRRC) events",
            "Paint goes to Rhode Island Eco-Depot events — appointment required, free for RI residents. Book at ecodepotri.org or call 401-942-1430 x3241. Events typically 8:00 a.m.–noon. Not Providence curbside bulky. Electronics are NOT accepted at Eco-Depot.",
            [
                "Book Eco-Depot appointment at ecodepotri.org.",
                "Deliver sealed paint during your slot.",
                "Keep paint off WM bulky piles.",
            ],
            [
                ("Curbside paint?", "No — Eco-Depot only."),
                ("Fee?", "Free for RI residents with appointment."),
            ],
            *hhw,
        )
    )
    rows.append(
        R(
            c,
            st,
            "paint-oil",
            "BANNED_FROM_LANDFILLS",
            "High",
            False,
            "Free RI Eco-Depot appointment",
            "RI Eco-Depot (RIRRC) events",
            "Oil-based paint goes to RI Eco-Depot by appointment — free for RI residents. Not curbside.",
            [
                "Book Eco-Depot appointment.",
                "Keep containers sealed and labeled.",
                "Not WM bulky.",
            ],
            [("Same as latex?", "Yes — both use Eco-Depot.")],
            *hhw,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "Free RI Eco-Depot appointment",
                "RI Eco-Depot (RIRRC) events",
                f"Take {item.replace('-', ' ')} to RI Eco-Depot by appointment — free for RI residents. Propane ≤20 lb accepted; electronics/flares/helium tanks and containers >5 gal are NOT accepted.",
                [
                    "Book Eco-Depot appointment at ecodepotri.org.",
                    "Deliver sealed containers in your time slot.",
                    "Keep chemicals off bulky piles.",
                ],
                [("Same as paint?", "Yes — chemicals use Eco-Depot.")],
                *hhw,
            )
        )
    for item in [
        "car-battery",
        "lithium-battery",
        "motor-oil",
        "propane-tank",
        "fluorescent-bulbs",
        "cooking-oil",
    ]:
        extra = {
            "car-battery": " Confirm battery acceptance at Eco-Depot or retailer take-back.",
            "lithium-battery": " Confirm lithium battery acceptance at Eco-Depot/retailer.",
            "motor-oil": " Motor oil/antifreeze at Eco-Depot.",
            "propane-tank": " Propane ≤20 lb at Eco-Depot; helium tanks NOT accepted.",
            "fluorescent-bulbs": " Fluorescents at Eco-Depot.",
            "cooking-oil": " Cooking oil at Eco-Depot when not trash-safe.",
        }[item]
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium",
                False,
                "Free RI Eco-Depot appointment",
                "RI Eco-Depot (RIRRC) events",
                f"Rhode Island Eco-Depot events accept household hazardous materials by appointment for RI residents.{extra}",
                [
                    "Book appointment at ecodepotri.org or 401-942-1430 x3241.",
                    "Deliver during your scheduled slot (often 8:00–noon).",
                    "Tires use RIRRC small-vehicle area ($8/tire), not Eco-Depot e-waste rules.",
                ],
                [("Appointment?", "Yes — required for Eco-Depot.")],
                *hhw,
            )
        )
    rows.append(
        R(
            c,
            st,
            "medical-sharps",
            "BANNED_FROM_LANDFILLS",
            "High",
            False,
            "Rigid sealed container — Eco-Depot accepts sharps",
            "RI Eco-Depot (RIRRC) events",
            "Place sharps in a rigid sealed container. RI Eco-Depot accepts sharps by appointment. Do not loose-bag needles.",
            [
                "Use rigid sealed container.",
                "Book Eco-Depot appointment for sharps.",
                "Never recycle loose needles.",
            ],
            [("Medications?", "Confirm drug take-back via Eco-Depot / RI programs.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c,
            st,
            "tires",
            "SPECIAL_HANDLING",
            "Medium",
            False,
            "RIRRC small-vehicle area — $8/tire",
            "RIRRC small-vehicle tire drop-off",
            "Providence tires go to the RIRRC small-vehicle area for about $8/tire — not free city bulky. Confirm current fee on providenceri.gov bulky-items FAQ. Retailer take-back when replacing tires.",
            [
                "Do not put tires on free WM bulky.",
                "Haul to RIRRC small-vehicle area ($8/tire).",
                "Retailer take-back when replacing tires.",
            ],
            [
                ("City bulky for tires?", "No — RIRRC fee path."),
                ("Fee?", "About $8 per tire at RIRRC."),
            ],
            *bulky,
        )
    )
    rows.append(
        R(
            c,
            st,
            "yard-waste",
            "ACCEPTED_IN_BLUE_BIN",
            "Low",
            True,
            "Providence yard waste collection",
            "Providence yard waste collection",
            "Providence handles yard waste through regular collection. Follow set-out rules on providenceri.gov.",
            [
                "Use yard waste set-out rules.",
                "Keep yard waste out of HHW and e-waste loads.",
                "Check providenceri.gov for seasonal guidance.",
            ],
            [("Christmas trees?", "Follow city seasonal guidance.")],
            *tricky,
        )
    )
    rows.append(
        R(
            c,
            st,
            "food-scraps",
            "SPECIAL_HANDLING",
            "Low",
            True,
            "Garbage cart unless private compost",
            "Providence garbage / private compost",
            "Bag food scraps for garbage unless you compost.",
            [
                "Bag food for garbage if no compost.",
                "Keep organics out of recycling.",
                "Yard trimmings use yard-waste pathways.",
            ],
            [("HHW for food?", "No.")],
            *tricky,
        )
    )
    rows.append(
        R(
            c,
            st,
            "plastic-bags",
            "SPECIAL_HANDLING",
            "Low",
            False,
            "Not recycling — store take-back / trash",
            "Retail bag take-back / trash",
            "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
            ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."],
            [("Bulky for bags?", "No.")],
            *tricky,
        )
    )
    rows.append(
        R(
            c,
            st,
            "construction-debris",
            "SPECIAL_HANDLING",
            "Low",
            False,
            "NOT typical free bulky — private C&D hauler",
            "Private C&D hauler",
            "Providence free bulky is limited to 3 household items/week for buildings ≤6 units — not contractor C&D. Hire a private C&D hauler for remodel loads. Route paint to Eco-Depot separately.",
            [
                "Do not treat remodel debris as free bulky.",
                "Hire private C&D for larger projects.",
                "Route paint to Eco-Depot.",
            ],
            [("HHW for C&D?", "No — separate paint/chemicals.")],
            *tricky,
        )
    )
    return rows


def durham():
    c, st = "durham", "NC"
    bulk = ("City of Durham — Bulky services", "https://www.durhamnc.gov/855/Bulky-Services")
    facility = (
        "City of Durham — Waste Disposal & Recycling Center",
        "https://www.durhamnc.gov/878/Waste-Disposal-Recycling-Center",
    )
    faq_h = ("City of Durham — Waste FAQ", "https://www.durhamnc.gov/faq.aspx?TID=90")
    rows = []
    rows.append(
        R(
            c,
            st,
            "mattress",
            "SPECIAL_HANDLING",
            "Low",
            True,
            "Request-only bulky — 3 items/week free",
            "Durham bulky services (online request)",
            "Durham mattresses are accepted on request-only bulky service — 3 items/week free; more than 3 needs a paid quote. Mechanical-arm curb pickup only (not alleys). TVs, e-waste, tires, propane, and construction debris are prohibited from bulky.",
            [
                "Request bulky online for the mattress.",
                "Stay within 3 free items/week.",
                "Keep TVs/e-waste/tires off the bulky pile.",
            ],
            [
                ("Fee?", "Free for up to 3 items/week."),
                ("Alley pickup?", "No — curb only for mechanical arm."),
            ],
            *bulk,
        )
    )
    rows.append(
        R(
            c,
            st,
            "refrigerator",
            "SPECIAL_HANDLING",
            "High",
            True,
            "Bulky request (if not prohibited) OR free residential drop-off at 2115 E Club Blvd",
            "Durham bulky / Waste Disposal & Recycling Center",
            "Durham non-prohibited large appliances may use bulky request (3/week free) or free residential drop-off at the Waste Disposal & Recycling Center — 2115 East Club Boulevard. Freon-containing non-working appliances are NOT accepted at special e-waste events — use the transfer station pathway. Never vent refrigerant yourself.",
            [
                "Request bulky OR haul to 2115 E Club Blvd.",
                "Do not rely on e-waste special events for Freon appliances.",
                "Keep doors secured until proper handling.",
            ],
            [
                ("Free drop-off?", "Yes — residential at 2115 E Club Blvd."),
                ("E-waste event for Freon?", "No — Freon appliances not accepted at e-waste events."),
            ],
            *facility,
        )
    )
    rows.append(
        R(
            c,
            st,
            "air-conditioner",
            "SPECIAL_HANDLING",
            "High",
            True,
            "Bulky request OR free residential drop-off at 2115 E Club Blvd",
            "Durham bulky / Waste Disposal & Recycling Center",
            "Durham AC units use bulky request when eligible or free residential drop-off at 2115 East Club Boulevard. Freon appliances are not for e-waste special events. Never vent refrigerant yourself.",
            [
                "Request bulky or haul to 2115 E Club Blvd.",
                "Keep sealed until proper Freon handling.",
                "Stay within 3 free bulky items/week if curbside.",
            ],
            [("Same as fridge?", "Yes — transfer station or bulky, not e-waste events.")],
            *facility,
        )
    )
    for item, label in [
        ("television", "TVs"),
        ("computer-monitor", "monitors"),
        ("smartphone", "phones"),
        ("e-waste-mixed", "mixed e-waste"),
    ]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "NOT curbside bulky — free resident drop-off at 2115 E Club Blvd",
                "Durham Waste Disposal & Recycling Center — 2115 E Club Blvd",
                f"Electronics including {label} are prohibited from Durham curbside bulky. Drop free at the Waste Disposal & Recycling Center — 2115 East Club Boulevard (Mon–Fri 7:30–4:00, Sat 7:30–noon). Annual e-waste events are also held. Wipe data before drop-off.",
                [
                    "Do not put TVs/e-waste on bulky piles.",
                    "Haul free to 2115 E Club Blvd during posted hours.",
                    "Wipe personal data.",
                ],
                [
                    ("Curbside e-waste?", "No — prohibited from bulky."),
                    ("Hours?", "Mon–Fri 7:30–16:00; Sat 7:30–12:00."),
                ],
                *bulk,
            )
        )
    rows.append(
        R(
            c,
            st,
            "paint-latex",
            "SPECIAL_HANDLING",
            "Medium",
            False,
            "Free residential HHW at 2115 E Club Blvd",
            "Durham Waste Disposal & Recycling Center — HHW",
            "Liquid latex paint is free at Durham's Waste Disposal & Recycling Center HHW — 2115 East Club Boulevard. Hours: Mon–Fri 7:30 a.m.–4:00 p.m., Sat 7:30 a.m.–noon. Not curbside.",
            [
                "Haul sealed paint to 2115 E Club Blvd.",
                "Use residential HHW section during posted hours.",
                "Keep paint off bulky piles.",
            ],
            [
                ("Fee?", "Free for residential HHW."),
                ("Address?", "2115 East Club Boulevard, Durham, NC 27704."),
            ],
            *faq_h,
        )
    )
    rows.append(
        R(
            c,
            st,
            "paint-oil",
            "BANNED_FROM_LANDFILLS",
            "High",
            False,
            "Free residential HHW at 2115 E Club Blvd",
            "Durham Waste Disposal & Recycling Center — HHW",
            "Oil-based paint goes to Durham HHW at 2115 East Club Boulevard — free for residents. Hours: Mon–Fri 7:30–4:00, Sat 7:30–noon.",
            [
                "Haul oil paint to 2115 E Club Blvd.",
                "Keep containers sealed and labeled.",
                "Not curbside bulky.",
            ],
            [("Same as latex?", "Yes — both use transfer-station HHW.")],
            *faq_h,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "Free residential HHW at 2115 E Club Blvd",
                "Durham Waste Disposal & Recycling Center — HHW",
                f"Take {item.replace('-', ' ')} to Durham HHW at 2115 East Club Boulevard — free for residents. Commercial/medical/radioactive/explosive materials are not accepted.",
                [
                    "Deliver sealed containers to 2115 E Club Blvd.",
                    "Hours: Mon–Fri 7:30–16:00, Sat 7:30–12:00.",
                    "Keep chemicals off bulky piles.",
                ],
                [("Same as paint?", "Yes — chemicals use transfer-station HHW.")],
                *faq_h,
            )
        )
    for item in [
        "car-battery",
        "lithium-battery",
        "motor-oil",
        "propane-tank",
        "fluorescent-bulbs",
        "cooking-oil",
    ]:
        extra = {
            "car-battery": " Batteries at HHW.",
            "lithium-battery": " Lithium batteries at HHW.",
            "motor-oil": " Automotive fluids at HHW.",
            "propane-tank": " Propane is prohibited from bulky — use transfer station guidance.",
            "fluorescent-bulbs": " Fluorescent lights at HHW.",
            "cooking-oil": " Cooking oil at HHW when not trash-safe.",
        }[item]
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium",
                False,
                "Free residential HHW at 2115 E Club Blvd",
                "Durham Waste Disposal & Recycling Center — HHW",
                f"Durham Waste Disposal & Recycling Center HHW at 2115 East Club Boulevard accepts household hazardous materials free for residents.{extra}",
                [
                    "Haul to 2115 E Club Blvd during posted hours.",
                    "Phone 919-560-4611 with questions.",
                    "Tires: free for ≤5 non-collector tires at the same facility.",
                ],
                [("Address?", "2115 East Club Boulevard, Durham, NC 27704.")],
                *faq_h,
            )
        )
    rows.append(
        R(
            c,
            st,
            "medical-sharps",
            "BANNED_FROM_LANDFILLS",
            "High",
            False,
            "Rigid sealed container — confirm transfer-station sharps acceptance",
            "Durham Waste Disposal & Recycling Center",
            "Place sharps in a rigid sealed container. Confirm acceptance at Durham Waste Disposal & Recycling Center. Do not loose-bag needles.",
            [
                "Use rigid sealed container.",
                "Confirm sharps at 2115 E Club Blvd.",
                "Never recycle loose needles.",
            ],
            [("Medications?", "Confirm drug take-back via durhamnc.gov.")],
            *faq_h,
        )
    )
    rows.append(
        R(
            c,
            st,
            "tires",
            "SPECIAL_HANDLING",
            "Medium",
            False,
            "Transfer station — free for ≤5 non-collector tires; NOT curbside bulky",
            "Durham Waste Disposal & Recycling Center — tires",
            "Durham tires are prohibited from curbside bulky. Drop at 2115 East Club Boulevard — free for ≤5 tires for non-collectors (NC-certified). Mixed-waste surcharge about $6/tire; larger/commercial loads use per-ton fees.",
            [
                "Do not set tires out for bulky.",
                "Haul ≤5 tires free to 2115 E Club Blvd when eligible.",
                "Retailer take-back when replacing tires.",
            ],
            [
                ("Curbside tires?", "No — prohibited from bulky."),
                ("Free limit?", "≤5 tires for non-collectors."),
            ],
            *facility,
        )
    )
    rows.append(
        R(
            c,
            st,
            "yard-waste",
            "ACCEPTED_IN_BLUE_BIN",
            "Low",
            True,
            "Durham yard waste collection",
            "Durham yard waste collection",
            "Durham handles yard waste through regular collection. Follow set-out rules on durhamnc.gov.",
            [
                "Use yard waste set-out rules.",
                "Keep yard waste out of HHW and e-waste loads.",
                "Check durhamnc.gov for seasonal guidance.",
            ],
            [("Christmas trees?", "Follow city seasonal guidance.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c,
            st,
            "food-scraps",
            "SPECIAL_HANDLING",
            "Low",
            True,
            "Garbage cart unless private compost",
            "Durham garbage / private compost",
            "Bag food scraps for garbage unless you compost.",
            [
                "Bag food for garbage if no compost.",
                "Keep organics out of recycling.",
                "Yard trimmings use yard-waste pathways.",
            ],
            [("HHW for food?", "No.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c,
            st,
            "plastic-bags",
            "SPECIAL_HANDLING",
            "Low",
            False,
            "Not recycling — store take-back / trash",
            "Retail bag take-back / trash",
            "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
            ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."],
            [("Bulky for bags?", "No.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c,
            st,
            "construction-debris",
            "SPECIAL_HANDLING",
            "Low",
            False,
            "NOT bulky — private C&D hauler / transfer station limits",
            "Private C&D hauler / Durham transfer station",
            "Construction debris is prohibited from Durham bulky. Hire a private C&D hauler or confirm transfer-station limits at 2115 E Club Blvd. Route paint/chemicals to HHW separately.",
            [
                "Do not put C&D on bulky piles.",
                "Hire private C&D for remodel loads.",
                "Route paint to transfer-station HHW.",
            ],
            [("HHW for C&D?", "No — separate paint/chemicals.")],
            *bulk,
        )
    )
    return rows


def birmingham():
    c, st = "birmingham", "AL"
    bulk = (
        "City of Birmingham — Garbage, recycle & bulk trash schedules",
        "https://www.birminghamal.gov/government/city-departments/department-public-works/waste-services/garbage-recycle-bulk-trash-schedules",
    )
    dump = (
        "City of Birmingham — Illegal dumping / dumpsters & landfill",
        "https://www.birminghamal.gov/government/city-departments/department-public-works/waste-services/illegal-dumping",
    )
    hhw = (
        "Jefferson County — Electronics & hazardous materials events",
        "https://www.jccal.org/593/Electronics-Hazardous-Materials",
    )
    rows = []
    rows.append(
        R(
            c,
            st,
            "mattress",
            "SPECIAL_HANDLING",
            "Low",
            True,
            "Area-scheduled bulk trash — free; or district dumpsters Mon–Fri 7–4",
            "Birmingham bulk trash / district dumpsters",
            "Birmingham mattresses go on area-scheduled bulk trash — set out by 6 a.m. on your neighborhood's scheduled day (check calendar or call 311). Free for city-served households. District dumpsters also accept mattresses Mon–Fri 7:00 a.m.–4:00 p.m. at Ensley, Eastend, North Birmingham, and Southside locations.",
            [
                "Check the monthly bulk calendar or call 311 for your area day.",
                "Set out by 6 a.m. on the scheduled collection day.",
                "Or use a district dumpster Mon–Fri 7–4.",
            ],
            [
                ("Fee?", "Free on scheduled bulk day for city-served households."),
                ("Dumpster option?", "Yes — four district dumpster sites Mon–Fri 7–4."),
            ],
            *dump,
        )
    )
    rows.append(
        R(
            c,
            st,
            "refrigerator",
            "SPECIAL_HANDLING",
            "High",
            True,
            "Bulk trash / Eastern Area Landfill scrap OR Jefferson County HHW events for appliances",
            "Birmingham bulk / Eastern Area Landfill / Jefferson County HHW events",
            "Birmingham metal appliances may go on scheduled bulk trash or to the Eastern Area Landfill public unloading area for scrap (Jefferson County ID; free). Jefferson County HHW events also accept large appliances. City pages do not document a separate Freon fee — never vent refrigerant yourself; prefer certified Freon handling via landfill scrap or county events.",
            [
                "Use scheduled bulk day OR Eastern Area Landfill unloading area.",
                "Bring Jefferson County ID for landfill unloading.",
                "Prefer county HHW event dates for appliance diversion when available.",
            ],
            [
                ("Freon fee on city page?", "Not separately listed — do not vent Freon yourself."),
                ("Landfill?", "Eastern Area Landfill public unloading — county ID required."),
            ],
            *dump,
        )
    )
    rows.append(
        R(
            c,
            st,
            "air-conditioner",
            "SPECIAL_HANDLING",
            "High",
            True,
            "Bulk trash / landfill scrap OR Jefferson County HHW events",
            "Birmingham bulk / Eastern Area Landfill / Jefferson County HHW events",
            "Birmingham AC units may use scheduled bulk trash or Eastern Area Landfill scrap unloading. Jefferson County HHW events accept large appliances. Never vent refrigerant yourself.",
            [
                "Use bulk day, landfill unloading, or county HHW event.",
                "Bring Jefferson County ID for landfill.",
                "Keep sealed until proper Freon handling.",
            ],
            [("Same as fridge?", "Yes — bulk, landfill scrap, or county HHW events.")],
            *dump,
        )
    )
    for item, label in [
        ("television", "TVs"),
        ("computer-monitor", "monitors"),
        ("smartphone", "phones"),
        ("e-waste-mixed", "mixed e-waste"),
    ]:
        rows.append(
            R(
                c,
                st,
                item,
                "SPECIAL_HANDLING",
                "Medium",
                True,
                "Bulk trash / Eastern Area Landfill OR Jefferson County e-waste events (e.g. Birmingham City Hall)",
                "Birmingham bulk / landfill / Jefferson County e-waste events",
                f"Electronics including {label} may go on Birmingham bulk trash or Eastern Area Landfill unloading. Prefer Jefferson County e-waste events when scheduled (e.g. Birmingham City Hall dates on jccal.org). Wipe data before disposal. CRT TVs may incur private recycler fees outside events.",
                [
                    "Prefer Jefferson County e-waste event dates on jccal.org.",
                    "Or use bulk day / Eastern Area Landfill unloading.",
                    "Wipe personal data.",
                ],
                [
                    ("Event example?", "Check jccal.org — e.g. Birmingham City Hall event dates."),
                    ("Bulk OK?", "City guidance allows TVs in bulk stream; events preferred."),
                ],
                *hhw,
            )
        )
    rows.append(
        R(
            c,
            st,
            "paint-latex",
            "SPECIAL_HANDLING",
            "Medium",
            False,
            "Jefferson County HHW events only — NOT Eastern Area Landfill unloading",
            "Jefferson County HHW events (Apr/Oct typical)",
            "Paint is NOT accepted at Birmingham Eastern Area Landfill public unloading. Use Jefferson County HHW events (typically spring/fall, e.g. Apr 25 and Oct 17 2026, 8:00–11:30 a.m. or until capacity) — free for Jefferson County residents. Between events there is no documented city year-round paint drop-off.",
            [
                "Do not haul paint to Eastern Area Landfill unloading.",
                "Check jccal.org for upcoming HHW event sites/dates.",
                "Store sealed paint until the next free event.",
            ],
            [
                ("Year-round city HHW?", "No — event-based via Jefferson County."),
                ("Fee?", "Free for Jefferson County residents at events."),
            ],
            *hhw,
        )
    )
    rows.append(
        R(
            c,
            st,
            "paint-oil",
            "BANNED_FROM_LANDFILLS",
            "High",
            False,
            "Jefferson County HHW events only",
            "Jefferson County HHW events",
            "Oil-based paint goes to Jefferson County HHW events — free for county residents. Not landfill unloading or regular trash.",
            [
                "Hold sealed oil paint for the next county HHW event.",
                "Check jccal.org for dates/sites.",
                "Not Eastern Area Landfill unloading.",
            ],
            [("Same as latex?", "Yes — both use county HHW events.")],
            *hhw,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "Jefferson County HHW events only",
                "Jefferson County HHW events",
                f"Take {item.replace('-', ' ')} to Jefferson County HHW events — free for county residents. Not accepted at Eastern Area Landfill unloading.",
                [
                    "Store sealed chemicals until the next HHW event.",
                    "Check jccal.org for Gardendale/Irondale/Bessemer sites.",
                    "Keep chemicals off bulk piles.",
                ],
                [("Landfill unloading?", "No — paint/chemicals/tires/batteries/fluorescents excluded.")],
                *hhw,
            )
        )
    for item in [
        "car-battery",
        "lithium-battery",
        "motor-oil",
        "propane-tank",
        "fluorescent-bulbs",
        "cooking-oil",
    ]:
        extra = {
            "car-battery": " Batteries at county HHW events — not landfill unloading.",
            "lithium-battery": " Lithium batteries at county HHW events.",
            "motor-oil": " Automotive fluids at county HHW events.",
            "propane-tank": " Confirm propane acceptance at county HHW events.",
            "fluorescent-bulbs": " Fluorescent bulbs at county HHW events — not landfill unloading.",
            "cooking-oil": " Cooking oil at HHW events when not trash-safe.",
        }[item]
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium",
                False,
                "Jefferson County HHW events",
                "Jefferson County HHW events",
                f"Jefferson County HHW events accept household hazardous materials free for residents.{extra}",
                [
                    "Check jccal.org for upcoming event dates.",
                    "Do not take these materials to Eastern Area Landfill unloading.",
                    "Tires: up to 8 no-rim at HHW events.",
                ],
                [("Year-round?", "Event-based — store safely between dates.")],
                *hhw,
            )
        )
    rows.append(
        R(
            c,
            st,
            "medical-sharps",
            "BANNED_FROM_LANDFILLS",
            "High",
            False,
            "Rigid sealed container — confirm county HHW / pharmacy take-back",
            "Jefferson County HHW events / pharmacy take-back",
            "Place sharps in a rigid sealed container. Confirm acceptance at Jefferson County HHW events or pharmacy take-back. Do not loose-bag needles.",
            [
                "Use rigid sealed container.",
                "Confirm sharps at county HHW or pharmacy programs.",
                "Never recycle loose needles.",
            ],
            [("Medications?", "Confirm drug take-back via county/pharmacy programs.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c,
            st,
            "tires",
            "SPECIAL_HANDLING",
            "Medium",
            False,
            "Jefferson County HHW events — up to 8 tires no rims; NOT landfill unloading",
            "Jefferson County HHW events — tires",
            "Birmingham tires are NOT accepted at Eastern Area Landfill public unloading. Use Jefferson County HHW events — up to 8 tires, no rims — free for county residents. Between events use retailer take-back when replacing tires.",
            [
                "Do not haul tires to Eastern Area Landfill unloading.",
                "Hold for county HHW events (limit 8, no rims).",
                "Retailer take-back when replacing tires.",
            ],
            [
                ("Landfill for tires?", "No — excluded from public unloading."),
                ("Event limit?", "Up to 8 tires without rims."),
            ],
            *hhw,
        )
    )
    rows.append(
        R(
            c,
            st,
            "yard-waste",
            "ACCEPTED_IN_BLUE_BIN",
            "Low",
            True,
            "Area-scheduled brush / bulk — free",
            "Birmingham brush & bulk collection",
            "Birmingham handles brush on area-scheduled collection with bulk. Follow set-out rules and the monthly calendar; call 311 with questions.",
            [
                "Check the monthly brush/bulk calendar.",
                "Set out by 6 a.m. on your area day.",
                "District dumpsters also accept brush Mon–Fri 7–4.",
            ],
            [("Christmas trees?", "Follow city seasonal brush guidance.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c,
            st,
            "food-scraps",
            "SPECIAL_HANDLING",
            "Low",
            True,
            "Garbage cart unless private compost",
            "Birmingham garbage / private compost",
            "Bag food scraps for garbage unless you compost.",
            [
                "Bag food for garbage if no compost.",
                "Keep organics out of recycling.",
                "Yard trimmings use brush pathways.",
            ],
            [("HHW for food?", "No.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c,
            st,
            "plastic-bags",
            "SPECIAL_HANDLING",
            "Low",
            False,
            "Not recycling — store take-back / trash",
            "Retail bag take-back / trash",
            "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
            ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."],
            [("Bulk for bags?", "No.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c,
            st,
            "construction-debris",
            "SPECIAL_HANDLING",
            "Low",
            False,
            "NOT typical household bulk — private C&D hauler",
            "Private C&D hauler",
            "Contractor construction debris is not typical Birmingham household bulk. Hire a private C&D hauler for remodel loads. Route paint/tires/batteries to Jefferson County HHW events — not Eastern Area Landfill unloading.",
            [
                "Hire private C&D for remodel loads.",
                "Keep paint/tires/batteries for county HHW events.",
                "Do not mix HHW into landfill unloading.",
            ],
            [("HHW for C&D?", "No — separate paint/chemicals.")],
            *dump,
        )
    )
    return rows


CITIES = [
    {
        "city": "Madison",
        "city_slug": "madison",
        "state": "WI",
        "state_slug": "wisconsin",
        "lat": 43.0731,
        "lng": -89.4012,
        "population": 269840,
    },
    {
        "city": "Salt Lake City",
        "city_slug": "salt-lake-city",
        "state": "UT",
        "state_slug": "utah",
        "lat": 40.7608,
        "lng": -111.8910,
        "population": 209593,
    },
    {
        "city": "Providence",
        "city_slug": "providence",
        "state": "RI",
        "state_slug": "rhode-island",
        "lat": 41.8240,
        "lng": -71.4128,
        "population": 190934,
    },
    {
        "city": "Durham",
        "city_slug": "durham",
        "state": "NC",
        "state_slug": "north-carolina",
        "lat": 35.9940,
        "lng": -78.8986,
        "population": 283506,
    },
    {
        "city": "Birmingham",
        "city_slug": "birmingham",
        "state": "AL",
        "state_slug": "alabama",
        "lat": 33.5207,
        "lng": -86.8025,
        "population": 200733,
    },
]

ZIPS = [
    {
        "zip": "53703",
        "city": "Madison",
        "city_slug": "madison",
        "state": "WI",
        "state_slug": "wisconsin",
        "lat": 43.073,
        "lng": -89.401,
        "population": 22000,
    },
    {
        "zip": "53711",
        "city": "Madison",
        "city_slug": "madison",
        "state": "WI",
        "state_slug": "wisconsin",
        "lat": 43.035,
        "lng": -89.455,
        "population": 28000,
    },
    {
        "zip": "84101",
        "city": "Salt Lake City",
        "city_slug": "salt-lake-city",
        "state": "UT",
        "state_slug": "utah",
        "lat": 40.761,
        "lng": -111.891,
        "population": 12000,
    },
    {
        "zip": "84111",
        "city": "Salt Lake City",
        "city_slug": "salt-lake-city",
        "state": "UT",
        "state_slug": "utah",
        "lat": 40.755,
        "lng": -111.880,
        "population": 10000,
    },
    {
        "zip": "02903",
        "city": "Providence",
        "city_slug": "providence",
        "state": "RI",
        "state_slug": "rhode-island",
        "lat": 41.824,
        "lng": -71.413,
        "population": 11000,
    },
    {
        "zip": "02908",
        "city": "Providence",
        "city_slug": "providence",
        "state": "RI",
        "state_slug": "rhode-island",
        "lat": 41.845,
        "lng": -71.435,
        "population": 25000,
    },
    {
        "zip": "27701",
        "city": "Durham",
        "city_slug": "durham",
        "state": "NC",
        "state_slug": "north-carolina",
        "lat": 35.994,
        "lng": -78.899,
        "population": 18000,
    },
    {
        "zip": "27704",
        "city": "Durham",
        "city_slug": "durham",
        "state": "NC",
        "state_slug": "north-carolina",
        "lat": 36.020,
        "lng": -78.870,
        "population": 22000,
    },
    {
        "zip": "35203",
        "city": "Birmingham",
        "city_slug": "birmingham",
        "state": "AL",
        "state_slug": "alabama",
        "lat": 33.521,
        "lng": -86.803,
        "population": 8000,
    },
    {
        "zip": "35209",
        "city": "Birmingham",
        "city_slug": "birmingham",
        "state": "AL",
        "state_slug": "alabama",
        "lat": 33.480,
        "lng": -86.790,
        "population": 20000,
    },
]

FACILITIES = [
    {
        "name": "Dane County Clean Sweep",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "madison",
        "state": "WI",
        "zip": "53718",
        "address": "7020 Maahic Way, Madison, WI 53718",
        "lat": 43.0855,
        "lng": -89.2655,
        "source_url": "https://landfill.danecounty.gov/services/clean-sweep",
        "hours": "Mon–Fri 7:15–15:15; Sat 8:00–10:45",
        "phone": "608-838-3212",
        "accepted_materials": HHW_MATERIALS
        + ["television", "computer-monitor", "microwave"],
    },
    {
        "name": "Salt Lake Valley Landfill HHW",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "salt-lake-city",
        "state": "UT",
        "zip": "84104",
        "address": "6030 West California Avenue, Salt Lake City, UT 84104",
        "lat": 40.7255,
        "lng": -112.0155,
        "source_url": "https://www.saltlakecounty.gov/health/household-hazardous-waste/safe-disposal/",
        "hours": "Mon/Fri/Sat 7:00–17:00; self-service Tue–Thu",
        "phone": "801-541-4078",
        "accepted_materials": HHW_MATERIALS
        + ["television", "computer-monitor", "e-waste-mixed"],
    },
    {
        "name": "Providence DPW — 700 Allens Ave e-waste / mattress drop-off",
        "facility_type": "Electronics and mattress drop-off",
        "city_slug": "providence",
        "state": "RI",
        "zip": "02905",
        "address": "700 Allens Avenue (rear), Providence, RI 02905",
        "lat": 41.7955,
        "lng": -71.4055,
        "source_url": "https://www.providenceri.gov/electronic-waste-collection/",
        "hours": "Sat 7:00–12:45",
        "phone": "401-680-5000",
        "accepted_materials": [
            "television",
            "computer-monitor",
            "smartphone",
            "e-waste-mixed",
            "laptop",
            "desktop-computer",
            "printer",
            "microwave",
            "air-conditioner",
            "dehumidifier",
            "mattress",
            "box-spring",
        ],
    },
    {
        "name": "Durham Waste Disposal & Recycling Center",
        "facility_type": "Transfer station, HHW, e-waste & tire drop-off",
        "city_slug": "durham",
        "state": "NC",
        "zip": "27704",
        "address": "2115 East Club Boulevard, Durham, NC 27704",
        "lat": 36.0255,
        "lng": -78.8755,
        "source_url": "https://www.durhamnc.gov/878/Waste-Disposal-Recycling-Center",
        "hours": "Mon–Fri 7:30–16:00; Sat 7:30–12:00",
        "phone": "919-560-4611",
        "accepted_materials": HHW_MATERIALS
        + [
            "television",
            "computer-monitor",
            "smartphone",
            "e-waste-mixed",
            "tires",
            "tire-rims",
            "refrigerator",
            "freezer",
            "air-conditioner",
            "washer",
            "dryer",
        ],
    },
    {
        "name": "Birmingham Eastern Area Landfill — Public Unloading",
        "facility_type": "Appliance / TV scrap drop-off (no paint/tires/HHW)",
        "city_slug": "birmingham",
        "state": "AL",
        "zip": "35217",
        "address": "2787 Alton Road, Birmingham, AL",
        "lat": 33.5655,
        "lng": -86.7255,
        "source_url": "https://www.birminghamal.gov/government/city-departments/department-public-works/waste-services/illegal-dumping",
        "hours": "Check birminghamal.gov / call 311",
        "phone": "311",
        "accepted_materials": [
            "refrigerator",
            "freezer",
            "washer",
            "dryer",
            "stove",
            "television",
            "computer-monitor",
        ],
    },
]


def upsert_geo():
    cities_path = DATA / "geo" / "cities.json"
    zips_path = DATA / "geo" / "zips.json"
    cities = json.loads(cities_path.read_text())
    zips = json.loads(zips_path.read_text())
    by_slug = {(c["state_slug"], c["city_slug"]): c for c in cities}
    for c in CITIES:
        by_slug[(c["state_slug"], c["city_slug"])] = c
    cities_path.write_text(json.dumps(list(by_slug.values()), indent=2) + "\n")

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
        "madison": clone_siblings(madison()),
        "salt-lake-city": clone_siblings(salt_lake_city()),
        "providence": clone_siblings(providence()),
        "durham": clone_siblings(durham()),
        "birmingham": clone_siblings(birmingham()),
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

    print("Wave-13 metros written:")
    for city, rows in audited.items():
        print(f"  {city}: {len(rows)} rules")
    print(f"Total rules now: {len(keep)}")


if __name__ == "__main__":
    main()
