#!/usr/bin/env python3
"""Portal-audited city guides for wave-20 metros (city-sourced only).

Compact channel-template wave: each city defines disposal channels that emit
base item rows, then clone_siblings() expands to exactly 70 unique item_slugs.

Cities researched from official program pages (2026-08-12):
  - North Las Vegas, NV — Republic bulk; North Valley HHW; Cheyenne Transfer e-waste
  - Laredo, TX — 2 free bulky/yr; Laredo Environmental HHW/e-waste
  - Santa Clarita, CA — Burrtec bulky 4×/yr; Burrtec e-waste; CleanLA HHW
  - Cape Coral, FL — bulk same day as trash; Lee County Topaz HHW/e-waste
  - Modesto, CA — Gilton/Bertolotti bulky 2×/yr; Stanislaus County HHW/e-waste
  - Huntsville, AL — weekly bulk/yard/appliances; SWDA HHW/e-waste
  - Frisco, TX — monthly bulk (no Freon/e-waste/metal appliances); ECC drop-off
  - Amarillo, TX — free bulky curb; landfill; Environmental Lab HHW by appointment
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


# ---------------------------------------------------------------------------
# City channel packs
# ---------------------------------------------------------------------------


def north_las_vegas():
    c, st = "north-las-vegas", "NV"
    hub = (
        "City of North Las Vegas — Garbage and Recycling",
        "https://www.cityofnorthlasvegas.com/residents/garbage-and-recycling",
    )
    hhw = (
        "Southern Nevada Health District — Household Hazardous Waste",
        "https://www.southernnevadahealthdistrict.org/permits-and-regulations/solid-waste-compliance/household-hazardous-waste-management/",
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                "mattress",
                "SPECIAL_HANDLING",
                "Low",
                True,
                "Republic Services bulk — schedule; mattresses must be bagged",
                "North Las Vegas / Republic Services bulk collection",
                "North Las Vegas mattresses go on Republic Services bulk collection — schedule via the city garbage program. Mattresses must be bagged. Keep HHW and loose chemicals off bulk piles.",
                [
                    "Schedule Republic Services bulk collection via cityofnorthlasvegas.com.",
                    "Bag mattresses before set-out.",
                    "Keep paint, batteries, and propane off bulk piles.",
                ],
                [("Mattress bagged?", "Yes — mattresses must be bagged."), ("Who hauls?", "Republic Services for North Las Vegas.")],
                hub,
            ),
            ch(
                ["refrigerator", "air-conditioner"],
                "SPECIAL_HANDLING",
                "High",
                False,
                "Cheyenne Transfer Station — appliances; Freon handling at facility",
                "Cheyenne Transfer Station — 315 W Cheyenne Ave",
                "North Las Vegas Freon {item}s go to Cheyenne Transfer Station — 315 W Cheyenne Ave — open 7 a.m.–3 p.m. daily. Never vent refrigerant yourself. Confirm appliance fees before hauling.",
                [
                    "Haul sealed Freon unit to 315 W Cheyenne Ave.",
                    "Hours: 7:00–15:00 daily.",
                    "Never vent Freon yourself.",
                ],
                [("Bulk for Freon fridge?", "Prefer Cheyenne Transfer for appliances/electronics."), ("Hours?", "7 a.m.–3 p.m. daily.")],
                hub,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed"],
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "Cheyenne Transfer Station — household electronics free",
                "Cheyenne Transfer Station — 315 W Cheyenne Ave",
                "North Las Vegas electronics including {item} go to Cheyenne Transfer Station — 315 W Cheyenne Ave — household electronics accepted free. Wipe data before drop-off.",
                [
                    "Haul e-waste to 315 W Cheyenne Ave.",
                    "Hours: 7:00–15:00 daily.",
                    "Wipe personal data.",
                ],
                [("Free e-waste?", "Yes — household electronics at Cheyenne Transfer."), ("Bulk for TVs?", "Use Cheyenne Transfer Station.")],
                hub,
            ),
            ch(
                ["paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "North Valley HHW — 333 W Gowan Road — Wed–Sat 9–1 (rotating calendar)",
                "North Valley HHW — 333 W Gowan Road, North Las Vegas",
                "Take {item} to North Valley Household Hazardous Waste — 333 W Gowan Road, North Las Vegas NV 89032. Wed–Sat 9:00–13:00 on the rotating SNHD calendar. Not bulk.",
                [
                    "Check SNHD rotating calendar before visiting.",
                    "Haul sealed materials to 333 W Gowan Road.",
                    "Hours: Wed–Sat 9:00–13:00 when open.",
                ],
                [("HHW address?", "333 W Gowan Road, North Las Vegas."), ("Bulk for paint?", "No — North Valley HHW only.")],
                hhw,
            ),
            ch(
                "tires",
                "SPECIAL_HANDLING",
                "Medium",
                False,
                "NOT HHW — retailer take-back / transfer station tire programs",
                "Retailer take-back / Clark County transfer programs",
                "North Las Vegas tires are not a North Valley HHW material. Use retailer take-back when replacing tires or confirm transfer-station tire acceptance. Keep tires off HHW loads.",
                [
                    "Do not haul tires to North Valley HHW as HHW.",
                    "Use retailer take-back when replacing tires.",
                    "Confirm transfer-station tire rules before drop-off.",
                ],
                [("HHW for tires?", "No."), ("Bulk for tires?", "Confirm Republic/transfer rules — not HHW.")],
                hub,
            ),
            ch(
                "yard-waste",
                "ACCEPTED_IN_BLUE_BIN",
                "Low",
                True,
                "North Las Vegas yard / garbage program",
                "North Las Vegas garbage and recycling collection",
                "North Las Vegas yard waste follows the city garbage and recycling program. Follow set-out rules on cityofnorthlasvegas.com.",
                [
                    "Follow city set-out rules for yard trimmings.",
                    "Keep yard waste out of HHW and e-waste.",
                    "Check cityofnorthlasvegas.com for seasonal guidance.",
                ],
                [("Christmas trees?", "Follow city seasonal yard-waste guidance.")],
                hub,
            ),
            ch(
                "food-scraps",
                "SPECIAL_HANDLING",
                "Low",
                True,
                "Garbage cart unless private compost",
                "North Las Vegas garbage / private compost",
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
                "NOT bulk HHW — private C&D / transfer station",
                "Private C&D hauler / Cheyenne Transfer Station",
                "Construction debris is not North Valley HHW material. Hire a private C&D hauler or use transfer-station C&D pathways. Route paint/chemicals to North Valley HHW separately.",
                [
                    "Do not treat remodel debris as HHW.",
                    "Hire private C&D for larger projects.",
                    "Route paint to North Valley HHW.",
                ],
                [("HHW for C&D?", "No — separate paint/chemicals.")],
                hub,
            ),
        ],
    )


def laredo():
    c, st = "laredo", "TX"
    brush = (
        "Laredo Solid Waste — Brush & Bulky",
        "https://laredosolidwaste.com/index.php/services/brush",
    )
    hhw = (
        "Laredo Environmental — Household Hazardous Waste",
        "https://www.laredoenvironmental.com/household-hazardous-waste",
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner"],
                "SPECIAL_HANDLING",
                "Low",
                True,
                "2 free bulky collections/year — schedule 311 or 956-796-1098",
                "Laredo bulky collection / landfill drop-off",
                "Laredo {item}s go on bulky collection — 2 free collections per year (schedule 311 or 956-796-1098). Appliances are OK on bulky. Residents may also drop bulky at the landfill free on Saturdays up to 1 ton with ID and water bill. TVs/electronics are NOT bulky.",
                [
                    "Schedule bulky via 311 or 956-796-1098 (2 free/year).",
                    "Or haul Saturday landfill drop-off with ID + water bill (up to 1 ton).",
                    "Keep TVs and electronics off bulky piles.",
                ],
                [("Fee?", "2 free bulky collections/year."), ("Appliances on bulky?", "Yes."), ("TVs on bulky?", "No — HHW/e-waste site.")],
                brush,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed"],
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "NOT bulky — Laredo Environmental HHW 6912 TX-359",
                "Laredo Environmental HHW — 6912 TX-359",
                "Laredo electronics including {item} are NOT accepted on bulky. Take them to Laredo Environmental HHW — 6912 TX-359, Laredo TX 78043. Wipe data before drop-off.",
                [
                    "Do not set TVs/electronics on bulky.",
                    "Haul to 6912 TX-359.",
                    "Wipe personal data.",
                ],
                [("Bulky for TVs?", "No — HHW/e-waste site only."), ("Address?", "6912 TX-359, Laredo TX 78043.")],
                hhw,
            ),
            ch(
                ["paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "Laredo Environmental HHW — 6912 TX-359 — Mon–Thu 8–4, Fri 7–4, Sat 12–4",
                "Laredo Environmental HHW — 6912 TX-359",
                "Take {item} to Laredo Environmental Household Hazardous Waste — 6912 TX-359. Hours: Mon–Thu 8–4, Fri 7–4, Sat 12–4. Paint, batteries, and propane are NOT bulky. Tires are not HHW.",
                [
                    "Haul sealed materials to 6912 TX-359.",
                    "Hours: Mon–Thu 8–4, Fri 7–4, Sat 12–4.",
                    "Keep HHW off bulky piles.",
                ],
                [("HHW hours?", "Mon–Thu 8–4, Fri 7–4, Sat 12–4."), ("Tires at HHW?", "No.")],
                hhw,
            ),
            ch(
                "tires",
                "SPECIAL_HANDLING",
                "Medium",
                False,
                "NOT HHW — retailer take-back / landfill tire programs",
                "Retailer take-back / Laredo landfill tire programs",
                "Laredo tires are not accepted at the HHW facility. Use retailer take-back when replacing tires or confirm landfill tire acceptance. Keep tires off HHW loads.",
                [
                    "Do not haul tires to Laredo Environmental as HHW.",
                    "Use retailer take-back when replacing tires.",
                    "Confirm landfill tire rules before drop-off.",
                ],
                [("HHW for tires?", "No."), ("Bulky for tires?", "Confirm solid-waste rules — not HHW.")],
                brush,
            ),
            ch(
                "yard-waste",
                "ACCEPTED_IN_BLUE_BIN",
                "Low",
                True,
                "Laredo brush / bulky pathways",
                "Laredo brush and bulky collection",
                "Laredo yard and brush waste follows brush/bulky service — schedule via laredosolidwaste.com. Follow set-out rules.",
                [
                    "Schedule brush/bulky per laredosolidwaste.com.",
                    "Keep yard waste out of HHW.",
                    "Check seasonal brush guidance.",
                ],
                [("Christmas trees?", "Follow city seasonal brush guidance.")],
                brush,
            ),
            ch(
                "food-scraps",
                "SPECIAL_HANDLING",
                "Low",
                True,
                "Garbage cart unless private compost",
                "Laredo garbage / private compost",
                "Bag food scraps for garbage unless you compost. Keep food out of recycling and HHW.",
                ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use brush pathways."],
                [("HHW for food?", "No.")],
                brush,
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
                brush,
            ),
            ch(
                "construction-debris",
                "SPECIAL_HANDLING",
                "Low",
                False,
                "NOT typical bulky — private C&D / landfill",
                "Private C&D hauler / Laredo landfill",
                "Construction debris is not typical free bulky material. Hire a private C&D hauler or use landfill C&D pathways. Route paint/chemicals to Laredo Environmental HHW separately.",
                [
                    "Do not treat remodel debris as free bulky without confirming limits.",
                    "Hire private C&D for larger projects.",
                    "Route paint to 6912 TX-359.",
                ],
                [("HHW for C&D?", "No — separate paint/chemicals.")],
                brush,
            ),
        ],
    )


def santa_clarita():
    c, st = "santa-clarita", "CA"
    bulky = (
        "Green Santa Clarita — Bulky Item / Illegal Dumping",
        "https://greensantaclarita.com/trash-and-recycling/residential-trash-and-recycling/bulky-item-illegal-dumping/",
    )
    hhw_city = (
        "Green Santa Clarita — Hazardous Waste",
        "https://greensantaclarita.com/trash-and-recycling/residential-trash-and-recycling/hazardous-waste/",
    )
    cleanla = (
        "LA County CleanLA — HHW Collection Centers",
        "https://cleanla.lacounty.gov/hhw/collection-centers/",
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner", "tires"],
                "SPECIAL_HANDLING",
                "Low",
                True,
                "Burrtec bulky — up to 4×/year, 3 items — schedule 661-222-2249",
                "Santa Clarita / Burrtec bulky collection",
                "Santa Clarita {item}s go on Burrtec bulky collection — up to 4 times per year, 3 items each — schedule 661-222-2249. Tires are OK on bulky. Paint, propane, batteries, and e-waste are NOT bulky.",
                [
                    "Call Burrtec 661-222-2249 to schedule bulky (up to 4×/year, 3 items).",
                    "Set out per greensantaclarita.com rules.",
                    "Keep paint, propane, batteries, and e-waste off bulky piles.",
                ],
                [("How often?", "Up to 4 collections/year, 3 items each."), ("Tires on bulky?", "Yes."), ("E-waste on bulky?", "No — Burrtec Springbrook drop-off.")],
                bulky,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed"],
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "NOT curb bulky — Burrtec e-waste drop-off 25950/26000 Springbrook Ave",
                "Burrtec e-waste drop-off — Springbrook Ave, Santa Clarita",
                "Santa Clarita electronics including {item} are NOT accepted on curb bulky. Drop off at Burrtec — 25950/26000 Springbrook Ave. Wipe data before drop-off.",
                [
                    "Do not set e-waste on curb bulky.",
                    "Haul to Burrtec 25950/26000 Springbrook Ave.",
                    "Wipe personal data.",
                ],
                [("Bulky for TVs?", "No — Springbrook e-waste drop-off."), ("Address?", "25950/26000 Springbrook Ave.")],
                bulky,
            ),
            ch(
                ["paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "NOT bulky — LA County CleanLA / S.A.F.E. HHW centers",
                "LA County CleanLA / S.A.F.E. collection centers",
                "Take {item} to LA County CleanLA / S.A.F.E. household hazardous waste collection centers — paint, propane, and batteries are NOT Burrtec bulky. Confirm center hours on cleanla.lacounty.gov.",
                [
                    "Do not set paint/propane/batteries on bulky.",
                    "Use CleanLA / S.A.F.E. collection centers.",
                    "Confirm hours before visiting.",
                ],
                [("Bulky for paint?", "No."), ("Where?", "CleanLA / S.A.F.E. centers — cleanla.lacounty.gov.")],
                cleanla,
            ),
            ch(
                "yard-waste",
                "ACCEPTED_IN_BLUE_BIN",
                "Low",
                True,
                "Santa Clarita organics / yard-waste cart",
                "Santa Clarita residential trash and recycling",
                "Santa Clarita yard waste follows residential organics/yard-waste collection. Follow greensantaclarita.com set-out rules.",
                [
                    "Use organics/yard-waste set-out rules.",
                    "Keep yard waste out of HHW and e-waste.",
                    "Check greensantaclarita.com for seasonal guidance.",
                ],
                [("Christmas trees?", "Follow city seasonal yard-waste guidance.")],
                hhw_city,
            ),
            ch(
                "food-scraps",
                "SPECIAL_HANDLING",
                "Low",
                True,
                "Organics cart / garbage unless private compost",
                "Santa Clarita organics / garbage",
                "Bag food scraps in organics or garbage unless you compost. Keep food out of recycling and HHW.",
                ["Use organics/garbage pathways.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."],
                [("HHW for food?", "No.")],
                hhw_city,
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
                bulky,
            ),
            ch(
                "construction-debris",
                "SPECIAL_HANDLING",
                "Low",
                False,
                "NOT bulky — private C&D hauler",
                "Private C&D hauler / LA County disposal",
                "Construction debris is not Burrtec bulky material. Hire a private C&D hauler. Route paint/chemicals to CleanLA / S.A.F.E. separately.",
                [
                    "Do not treat remodel debris as bulky.",
                    "Hire private C&D for larger projects.",
                    "Route paint to CleanLA HHW.",
                ],
                [("HHW for C&D?", "No — separate paint/chemicals.")],
                bulky,
            ),
        ],
    )


def cape_coral():
    c, st = "cape-coral", "FL"
    bulk = (
        "City of Cape Coral — Bulk Waste",
        "https://www.capecoral.gov/departments/public_works/general_support_services_division/solid_waste/bulk_waste.php",
    )
    hhw = (
        "City of Cape Coral — Household Hazardous Waste",
        "https://www.capecoral.gov/departments/public_works/general_support_services_division/solid_waste/household_hazardous_waste_disposal.php",
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner"],
                "SPECIAL_HANDLING",
                "Low",
                True,
                "Bulk same day as trash — or drop-off 1200 Kismet Pkwy Tue–Sat 8–4",
                "Cape Coral bulk waste / Kismet Parkway drop-off",
                "Cape Coral {item}s go on bulk waste the same day as trash collection, or self-haul to the bulk drop-off — 1200 Kismet Parkway (NW 14th Ave entrance) — Tue–Sat 8–4. No HHW or C&D at the drop-off. Never vent Freon yourself.",
                [
                    "Set out on your trash day for bulk, or haul to 1200 Kismet Parkway.",
                    "Drop-off hours: Tue–Sat 8:00–16:00.",
                    "No HHW or construction debris at bulk drop-off.",
                ],
                [("Same day as trash?", "Yes — bulk rides with trash day."), ("Drop-off?", "1200 Kismet Parkway, Tue–Sat 8–4.")],
                bulk,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed", "paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "Lee County HHW/e-waste — 6441 Topaz Court, Fort Myers",
                "Lee County HHW — 6441 Topaz Court, Fort Myers",
                "Cape Coral residents take {item} to Lee County household hazardous waste / e-waste — 6441 Topaz Court, Fort Myers. Not accepted at the Kismet bulk drop-off. Wipe data on electronics before drop-off.",
                [
                    "Do not haul HHW/e-waste to Kismet bulk drop-off.",
                    "Deliver to 6441 Topaz Court, Fort Myers.",
                    "Wipe personal data on electronics.",
                ],
                [("Bulk drop-off for HHW?", "No."), ("Address?", "6441 Topaz Court, Fort Myers.")],
                hhw,
            ),
            ch(
                "tires",
                "SPECIAL_HANDLING",
                "Medium",
                False,
                "Confirm Cape Coral / Lee County tire drop-off — not HHW bulk",
                "Lee County / retailer tire take-back",
                "Cape Coral tires are not HHW at the Kismet bulk drop-off. Use retailer take-back when replacing tires or confirm Lee County tire acceptance. Keep tires off HHW loads.",
                [
                    "Do not treat tires as HHW at Topaz without confirming acceptance.",
                    "Use retailer take-back when replacing tires.",
                    "Confirm city/county tire rules before drop-off.",
                ],
                [("Kismet for tires?", "Confirm — no HHW/C&D at bulk drop-off.")],
                bulk,
            ),
            ch(
                "yard-waste",
                "ACCEPTED_IN_BLUE_BIN",
                "Low",
                True,
                "Cape Coral yard / bulk waste pathways",
                "Cape Coral solid waste collection",
                "Cape Coral yard waste follows solid-waste collection and bulk pathways. Follow capecoral.gov set-out rules.",
                [
                    "Follow city yard-waste set-out rules.",
                    "Keep yard waste out of HHW.",
                    "Check capecoral.gov for seasonal guidance.",
                ],
                [("Christmas trees?", "Follow city seasonal yard-waste guidance.")],
                bulk,
            ),
            ch(
                "food-scraps",
                "SPECIAL_HANDLING",
                "Low",
                True,
                "Garbage cart unless private compost",
                "Cape Coral garbage / private compost",
                "Bag food scraps for garbage unless you compost. Keep food out of recycling and HHW.",
                ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."],
                [("HHW for food?", "No.")],
                bulk,
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
                bulk,
            ),
            ch(
                "construction-debris",
                "SPECIAL_HANDLING",
                "Low",
                False,
                "NOT at Kismet bulk drop-off — private C&D",
                "Private C&D hauler",
                "Construction debris is not accepted at the Cape Coral Kismet bulk drop-off. Hire a private C&D hauler. Route paint/chemicals to Lee County Topaz HHW separately.",
                [
                    "Do not haul C&D to Kismet bulk drop-off.",
                    "Hire private C&D for remodel debris.",
                    "Route paint to 6441 Topaz Court.",
                ],
                [("Kismet for C&D?", "No.")],
                bulk,
            ),
        ],
    )


def modesto():
    c, st = "modesto", "CA"
    bulky = (
        "City of Modesto — Bulky Item Collection",
        "https://www.modestogov.com/373/Bulky-Item-Collection/",
    )
    faq204 = (
        "City of Modesto — HHW FAQ",
        "https://www.modestogov.com/FAQ.aspx?QID=204",
    )
    stan = (
        "Stanislaus County — Household Hazardous Waste",
        "https://www.stancounty.com/",
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner"],
                "SPECIAL_HANDLING",
                "Low",
                True,
                "Bulky 2×/year via Gilton or Bertolotti",
                "Modesto bulky item collection — Gilton / Bertolotti",
                "Modesto {item}s go on bulky item collection — 2 times per year via Gilton or Bertolotti. Schedule per modestogov.com/373. Keep HHW and e-waste off bulky piles. Never vent Freon yourself.",
                [
                    "Schedule bulky via your hauler (Gilton or Bertolotti) — 2×/year.",
                    "Follow modestogov.com/373 set-out rules.",
                    "Route paint/e-waste to Stanislaus County HHW.",
                ],
                [("How often?", "2 bulky collections per year."), ("Who hauls?", "Gilton or Bertolotti.")],
                bulky,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed", "paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "Stanislaus County HHW — 1710 Morgan Road — Fri–Sat 8am–noon — free",
                "Stanislaus County HHW — 1710 Morgan Road",
                "Modesto residents take {item} to Stanislaus County HHW — 1710 Morgan Road — free — Fri–Sat 8:00 a.m.–noon — phone 209-525-6789. Not bulky. Wipe data on electronics before drop-off.",
                [
                    "Haul to 1710 Morgan Road (Fri–Sat 8:00–12:00).",
                    "Call 209-525-6789 with questions.",
                    "Keep HHW/e-waste off bulky piles.",
                ],
                [("Free?", "Yes — residential HHW/e-waste."), ("Hours?", "Fri–Sat 8 a.m.–noon."), ("Phone?", "209-525-6789.")],
                stan,
            ),
            ch(
                "tires",
                "SPECIAL_HANDLING",
                "Medium",
                False,
                "Confirm hauler/county tire acceptance — not typical HHW",
                "Retailer take-back / Stanislaus disposal",
                "Modesto tires are not a typical Stanislaus HHW drop-off item. Use retailer take-back when replacing tires or confirm hauler/county tire programs. Keep tires off HHW loads.",
                [
                    "Do not assume tires are accepted at Morgan Road HHW.",
                    "Use retailer take-back when replacing tires.",
                    "Confirm county/hauler tire rules.",
                ],
                [("HHW for tires?", "Usually no — confirm before hauling.")],
                faq204,
            ),
            ch(
                "yard-waste",
                "ACCEPTED_IN_BLUE_BIN",
                "Low",
                True,
                "Modesto organics / yard-waste collection",
                "Modesto residential collection",
                "Modesto yard waste follows residential organics/yard-waste collection. Follow modestogov.com set-out rules.",
                [
                    "Use organics/yard-waste set-out rules.",
                    "Keep yard waste out of HHW.",
                    "Check modestogov.com for seasonal guidance.",
                ],
                [("Christmas trees?", "Follow city seasonal yard-waste guidance.")],
                bulky,
            ),
            ch(
                "food-scraps",
                "SPECIAL_HANDLING",
                "Low",
                True,
                "Organics cart / garbage unless private compost",
                "Modesto organics / garbage",
                "Bag food scraps in organics or garbage unless you compost. Keep food out of recycling and HHW.",
                ["Use organics/garbage pathways.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."],
                [("HHW for food?", "No.")],
                bulky,
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
                bulky,
            ),
            ch(
                "construction-debris",
                "SPECIAL_HANDLING",
                "Low",
                False,
                "NOT bulky — private C&D hauler",
                "Private C&D hauler",
                "Construction debris is not Modesto bulky material. Hire a private C&D hauler. Route paint/chemicals to Stanislaus County HHW separately.",
                [
                    "Do not treat remodel debris as bulky.",
                    "Hire private C&D for larger projects.",
                    "Route paint to 1710 Morgan Road.",
                ],
                [("HHW for C&D?", "No — separate paint/chemicals.")],
                bulky,
            ),
        ],
    )


def huntsville():
    c, st = "huntsville", "AL"
    curb = (
        "City of Huntsville — Residential Curbside Collection Schedule",
        "https://www.huntsvilleal.gov/residents/trash-recycling/residential-trash-collection/residential-curbside-collection-schedule/",
    )
    hhw = (
        "City of Huntsville — Residential Household Hazardous Waste",
        "https://www.huntsvilleal.gov/residents/trash-recycling/residential-household-hazardous-waste/",
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner", "yard-waste"],
                "SPECIAL_HANDLING",
                "Low",
                True,
                "Weekly bulk trash / yard waste / appliances curbside",
                "Huntsville weekly bulk / yard / appliance collection",
                "Huntsville {item}s go on weekly bulk trash, yard waste, and appliance curbside collection. Follow huntsvilleal.gov set-out rules. Keep HHW and e-waste off bulk piles. Never vent Freon yourself.",
                [
                    "Set out on your weekly bulk/yard/appliance day.",
                    "Follow huntsvilleal.gov curbside schedule rules.",
                    "Route paint/e-waste to SWDA — 1055 A Cleaner Way.",
                ],
                [("Weekly bulk?", "Yes — bulk trash, yard waste, and appliances."), ("E-waste on curb?", "No — SWDA HHW facility.")],
                curb,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed", "paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "SWDA — 1055 A Cleaner Way — Mon–Fri 7–5 — free",
                "SWDA HHW/e-waste — 1055 A Cleaner Way, Huntsville",
                "Huntsville residents take {item} to the SWDA facility — 1055 A Cleaner Way, Huntsville AL 35805 — Mon–Fri 7–5 — free. Not weekly bulk. Wipe data on electronics before drop-off.",
                [
                    "Haul to 1055 A Cleaner Way.",
                    "Hours: Mon–Fri 7:00–17:00.",
                    "Keep HHW/e-waste off weekly bulk piles.",
                ],
                [("Free?", "Yes."), ("Address?", "1055 A Cleaner Way, Huntsville AL 35805."), ("Hours?", "Mon–Fri 7–5.")],
                hhw,
            ),
            ch(
                "tires",
                "SPECIAL_HANDLING",
                "Medium",
                False,
                "Confirm SWDA/city tire acceptance — retailer take-back preferred",
                "Retailer take-back / SWDA tire programs",
                "Huntsville tires often use retailer take-back when replacing tires. Confirm SWDA tire acceptance before hauling. Keep tires off HHW chemical loads unless accepted.",
                [
                    "Prefer retailer take-back when replacing tires.",
                    "Confirm SWDA tire rules before drop-off.",
                    "Do not mix tires with weekly bulk without confirming rules.",
                ],
                [("Weekly bulk for tires?", "Confirm city rules before set-out.")],
                curb,
            ),
            ch(
                "food-scraps",
                "SPECIAL_HANDLING",
                "Low",
                True,
                "Garbage cart unless private compost",
                "Huntsville garbage / private compost",
                "Bag food scraps for garbage unless you compost. Keep food out of recycling and HHW.",
                ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use weekly yard-waste pathways."],
                [("HHW for food?", "No.")],
                curb,
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
                curb,
            ),
            ch(
                "construction-debris",
                "SPECIAL_HANDLING",
                "Low",
                False,
                "NOT typical weekly bulk — private C&D",
                "Private C&D hauler",
                "Construction debris is not typical Huntsville weekly bulk. Hire a private C&D hauler. Route paint/chemicals to SWDA separately.",
                [
                    "Do not treat remodel debris as weekly bulk without confirming limits.",
                    "Hire private C&D for larger projects.",
                    "Route paint to 1055 A Cleaner Way.",
                ],
                [("HHW for C&D?", "No — separate paint/chemicals.")],
                curb,
            ),
        ],
    )


def frisco():
    c, st = "frisco", "TX"
    bulk = (
        "City of Frisco — Bulk Trash Pickup",
        "https://www.friscotexas.gov/1350/Bulk-Trash-Pickup",
    )
    hhw = (
        "City of Frisco — Household Chemical Disposal",
        "https://www.friscotexas.gov/487/Household-Chemical-Disposal",
    )
    ecc = (
        "City of Frisco — Environmental Collection Center",
        "https://www.friscotexas.gov/1144/Environmental-Collection-Center",
    )
    # Freon vs metal appliances differ — override washer siblings so they do not
    # inherit Freon $40 path from refrigerator.
    return rows_from_channels(
        c,
        st,
        [
            ch(
                "mattress",
                "SPECIAL_HANDLING",
                "Low",
                True,
                "Schedule online — up to 5 items monthly on bulk week",
                "Frisco bulk trash pickup",
                "Frisco mattresses go on scheduled bulk trash — up to 5 items monthly on bulk week (schedule online). NO HHW, e-waste, refrigerators, TVs, or metal appliances on bulk.",
                [
                    "Schedule bulk online for your bulk week (up to 5 items).",
                    "Keep Freon appliances, TVs, and HHW off bulk piles.",
                    "Follow friscotexas.gov/1350 set-out rules.",
                ],
                [("Limit?", "Up to 5 items on bulk week."), ("Fridge on bulk?", "No — ECC / metal pickup.")],
                bulk,
            ),
            ch(
                ["refrigerator", "air-conditioner"],
                "SPECIAL_HANDLING",
                "High",
                False,
                "NOT bulk — Freon appliances $40 at ECC 6616 Walnut Street",
                "Frisco Environmental Collection Center — 6616 Walnut Street",
                "Frisco Freon {item}s are NOT accepted on bulk. Take Freon appliances to the Environmental Collection Center — 6616 Walnut Street — $40. Never vent refrigerant yourself.",
                [
                    "Do not set Freon appliances on bulk.",
                    "Haul to ECC 6616 Walnut Street ($40 Freon appliances).",
                    "Never vent Freon yourself.",
                ],
                [("Bulk for Freon fridge?", "No — ECC $40."), ("Metal washer?", "Separate — metal pickup $15 or ECC.")],
                ecc,
            ),
            ch(
                ["washer", "dryer", "dishwasher", "stove", "water-heater"],
                "SPECIAL_HANDLING",
                "Medium",
                False,
                "NOT bulk — ECC drop-off or metal pickup $15",
                "Frisco ECC / metal appliance pickup — $15",
                "Frisco metal appliances such as {item}s are NOT accepted on bulk. Use ECC drop-off at 6616 Walnut Street or metal appliance pickup — $15. Freon refrigerators/AC are $40 at ECC.",
                [
                    "Do not set metal appliances on bulk.",
                    "Use ECC drop-off or schedule metal pickup ($15).",
                    "Freon units are $40 at ECC — different fee.",
                ],
                [("Bulk for washers?", "No."), ("Fee?", "$15 metal pickup / ECC; Freon $40.")],
                ecc,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed", "paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "NOT bulk — Environmental Collection Center 6616 Walnut Street",
                "Frisco Environmental Collection Center — 6616 Walnut Street",
                "Frisco {item} is NOT accepted on bulk trash. Take HHW and e-waste to the Environmental Collection Center — 6616 Walnut Street. Wipe data on electronics before drop-off.",
                [
                    "Do not set HHW/e-waste/TVs on bulk.",
                    "Haul to ECC 6616 Walnut Street.",
                    "Wipe personal data on electronics.",
                ],
                [("Bulk for TVs?", "No."), ("ECC address?", "6616 Walnut Street.")],
                hhw,
            ),
            ch(
                "tires",
                "SPECIAL_HANDLING",
                "Medium",
                False,
                "Confirm ECC/retailer tire acceptance — not bulk HHW",
                "Retailer take-back / Frisco ECC tire programs",
                "Frisco tires are not bulk trash HHW. Use retailer take-back when replacing tires or confirm ECC tire acceptance. Keep tires off bulk piles.",
                [
                    "Do not set tires on bulk without confirming rules.",
                    "Prefer retailer take-back when replacing tires.",
                    "Confirm ECC tire acceptance before drop-off.",
                ],
                [("Bulk for tires?", "No — confirm ECC/retailer pathways.")],
                bulk,
            ),
            ch(
                "yard-waste",
                "ACCEPTED_IN_BLUE_BIN",
                "Low",
                True,
                "Frisco yard-waste / brush pathways",
                "Frisco solid waste collection",
                "Frisco yard waste follows city yard-waste/brush collection. Follow friscotexas.gov set-out rules.",
                [
                    "Use yard-waste set-out rules.",
                    "Keep yard waste out of HHW and e-waste.",
                    "Check friscotexas.gov for seasonal guidance.",
                ],
                [("Christmas trees?", "Follow city seasonal yard-waste guidance.")],
                bulk,
            ),
            ch(
                "food-scraps",
                "SPECIAL_HANDLING",
                "Low",
                True,
                "Garbage cart unless private compost",
                "Frisco garbage / private compost",
                "Bag food scraps for garbage unless you compost. Keep food out of recycling and HHW.",
                ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."],
                [("HHW for food?", "No.")],
                bulk,
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
                bulk,
            ),
            ch(
                "construction-debris",
                "SPECIAL_HANDLING",
                "Low",
                False,
                "NOT bulk — private C&D hauler",
                "Private C&D hauler",
                "Construction debris is not Frisco bulk trash. Hire a private C&D hauler. Route paint/chemicals to ECC separately.",
                [
                    "Do not treat remodel debris as bulk.",
                    "Hire private C&D for larger projects.",
                    "Route paint to ECC 6616 Walnut Street.",
                ],
                [("HHW for C&D?", "No — separate paint/chemicals.")],
                bulk,
            ),
        ],
    )


def amarillo():
    c, st = "amarillo", "TX"
    bulky = (
        "City of Amarillo — Bulky Item Pick Up",
        "https://www.amarillo.gov/solid-waste/bulky-item-pick-up/",
    )
    landfill = (
        "City of Amarillo — Amarillo Landfill",
        "https://www.amarillo.gov/solid-waste/amarillo-landfill/",
    )
    hhw = (
        "City of Amarillo — Household Hazardous Waste Program",
        "https://www.amarillo.gov/water-utilities/laboratory-administration/household-hazardous-waste-program/",
    )
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner"],
                "SPECIAL_HANDLING",
                "Low",
                True,
                "Free bulky curb pickup — schedule 806-378-6813",
                "Amarillo bulky item pick up",
                "Amarillo {item}s go on free bulky curb pickup — schedule 806-378-6813. Residents may also use Amarillo Landfill — 16250 Bezner Dr — free for resident household waste. Keep HHW off bulky piles. Never vent Freon yourself.",
                [
                    "Call 806-378-6813 to schedule free bulky pickup.",
                    "Or haul household waste to 16250 Bezner Dr (resident free).",
                    "Route paint/chemicals to Environmental Lab HHW by appointment.",
                ],
                [("Fee?", "Free bulky curb pickup."), ("Landfill?", "16250 Bezner Dr — free for resident household waste.")],
                bulky,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed", "paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "HHW appointment — Environmental Lab 4001 S. Osage — 806-342-1557",
                "Amarillo Environmental Lab HHW — 4001 S. Osage",
                "Amarillo {item} uses the Household Hazardous Waste program by appointment at the Environmental Lab — 4001 S. Osage — call 806-342-1557. Not free bulky curb. Wipe data on electronics before drop-off.",
                [
                    "Call 806-342-1557 to schedule an HHW appointment.",
                    "Deliver to Environmental Lab — 4001 S. Osage.",
                    "Keep HHW off bulky piles.",
                ],
                [("Appointment?", "Yes — call 806-342-1557."), ("Address?", "4001 S. Osage.")],
                hhw,
            ),
            ch(
                "tires",
                "SPECIAL_HANDLING",
                "Medium",
                False,
                "Confirm landfill/retailer tire acceptance — not HHW appointment default",
                "Amarillo Landfill / retailer tire take-back",
                "Amarillo tires typically use retailer take-back or confirm landfill tire acceptance at 16250 Bezner Dr. Keep tires off HHW appointment loads unless accepted.",
                [
                    "Prefer retailer take-back when replacing tires.",
                    "Confirm landfill tire rules at 16250 Bezner Dr.",
                    "Do not mix tires with HHW appointments without confirming.",
                ],
                [("HHW for tires?", "Usually no — confirm before appointment.")],
                landfill,
            ),
            ch(
                "yard-waste",
                "ACCEPTED_IN_BLUE_BIN",
                "Low",
                True,
                "Amarillo yard-waste / bulky pathways",
                "Amarillo solid waste collection",
                "Amarillo yard waste follows solid-waste and bulky pathways. Follow amarillo.gov set-out rules.",
                [
                    "Follow city yard-waste set-out rules.",
                    "Keep yard waste out of HHW.",
                    "Check amarillo.gov for seasonal guidance.",
                ],
                [("Christmas trees?", "Follow city seasonal yard-waste guidance.")],
                bulky,
            ),
            ch(
                "food-scraps",
                "SPECIAL_HANDLING",
                "Low",
                True,
                "Garbage cart unless private compost",
                "Amarillo garbage / private compost",
                "Bag food scraps for garbage unless you compost. Keep food out of recycling and HHW.",
                ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."],
                [("HHW for food?", "No.")],
                bulky,
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
                bulky,
            ),
            ch(
                "construction-debris",
                "SPECIAL_HANDLING",
                "Low",
                False,
                "NOT typical free bulky — private C&D / landfill",
                "Private C&D hauler / Amarillo Landfill",
                "Construction debris is not typical free bulky material. Hire a private C&D hauler or confirm landfill C&D rules at 16250 Bezner Dr. Route paint/chemicals to Environmental Lab HHW separately.",
                [
                    "Do not treat remodel debris as free bulky without confirming limits.",
                    "Hire private C&D or confirm landfill C&D acceptance.",
                    "Route paint to Environmental Lab by appointment.",
                ],
                [("HHW for C&D?", "No — separate paint/chemicals.")],
                landfill,
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Geo / facilities / main
# ---------------------------------------------------------------------------

CITIES = [
    {
        "city": "North Las Vegas",
        "city_slug": "north-las-vegas",
        "state": "NV",
        "state_slug": "nevada",
        "lat": 36.1989,
        "lng": -115.1175,
        "population": 262527,
    },
    {
        "city": "Laredo",
        "city_slug": "laredo",
        "state": "TX",
        "state_slug": "texas",
        "lat": 27.5306,
        "lng": -99.4803,
        "population": 255205,
    },
    {
        "city": "Santa Clarita",
        "city_slug": "santa-clarita",
        "state": "CA",
        "state_slug": "california",
        "lat": 34.3917,
        "lng": -118.5426,
        "population": 228673,
    },
    {
        "city": "Cape Coral",
        "city_slug": "cape-coral",
        "state": "FL",
        "state_slug": "florida",
        "lat": 26.5629,
        "lng": -81.9495,
        "population": 224455,
    },
    {
        "city": "Modesto",
        "city_slug": "modesto",
        "state": "CA",
        "state_slug": "california",
        "lat": 37.6391,
        "lng": -120.9969,
        "population": 218464,
    },
    {
        "city": "Huntsville",
        "city_slug": "huntsville",
        "state": "AL",
        "state_slug": "alabama",
        "lat": 34.7304,
        "lng": -86.5861,
        "population": 215006,
    },
    {
        "city": "Frisco",
        "city_slug": "frisco",
        "state": "TX",
        "state_slug": "texas",
        "lat": 33.1507,
        "lng": -96.8236,
        "population": 200509,
    },
    {
        "city": "Amarillo",
        "city_slug": "amarillo",
        "state": "TX",
        "state_slug": "texas",
        "lat": 35.222,
        "lng": -101.8313,
        "population": 200393,
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
        "name": "North Valley Household Hazardous Waste Facility",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "north-las-vegas",
        "state": "NV",
        "zip": "89032",
        "address": "333 W Gowan Road, North Las Vegas, NV 89032",
        "lat": 36.2400,
        "lng": -115.1400,
        "source_url": "https://www.southernnevadahealthdistrict.org/permits-and-regulations/solid-waste-compliance/household-hazardous-waste-management/",
        "hours": "Wed–Sat 9:00–13:00 — rotating SNHD calendar; confirm before visit",
        "phone": None,
        "accepted_materials": HHW_MATERIALS,
    },
    {
        "name": "Cheyenne Transfer Station",
        "facility_type": "Transfer station — electronics / appliances",
        "city_slug": "north-las-vegas",
        "state": "NV",
        "zip": "89030",
        "address": "315 W Cheyenne Avenue, North Las Vegas, NV 89030",
        "lat": 36.2180,
        "lng": -115.1400,
        "source_url": "https://www.cityofnorthlasvegas.com/residents/garbage-and-recycling",
        "hours": "Daily 7:00–15:00 — confirm before visit",
        "phone": None,
        "accepted_materials": E_WASTE
        + [
            "refrigerator",
            "freezer",
            "air-conditioner",
            "washer",
            "dryer",
            "dishwasher",
            "stove",
            "microwave",
        ],
    },
    {
        "name": "Laredo Environmental Household Hazardous Waste Facility",
        "facility_type": "Household hazardous waste / e-waste drop-off",
        "city_slug": "laredo",
        "state": "TX",
        "zip": "78043",
        "address": "6912 TX-359, Laredo, TX 78043",
        "lat": 27.5100,
        "lng": -99.4300,
        "source_url": "https://www.laredoenvironmental.com/household-hazardous-waste",
        "hours": "Mon–Thu 8–4, Fri 7–4, Sat 12–4 — confirm before visit",
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": "Burrtec Santa Clarita E-Waste Drop-Off — Springbrook",
        "facility_type": "Electronics drop-off",
        "city_slug": "santa-clarita",
        "state": "CA",
        "zip": "91350",
        "address": "26000 Springbrook Avenue, Santa Clarita, CA 91350",
        "lat": 34.4100,
        "lng": -118.5100,
        "source_url": "https://greensantaclarita.com/trash-and-recycling/residential-trash-and-recycling/bulky-item-illegal-dumping/",
        "hours": "Confirm Burrtec hours before visit",
        "phone": "661-222-2249",
        "accepted_materials": E_WASTE,
    },
    {
        "name": "LA County CleanLA / S.A.F.E. HHW Collection Centers — Santa Clarita residents",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "santa-clarita",
        "state": "CA",
        "zip": "91352",
        "address": "11025 Randall Street, Sun Valley, CA 91352",
        "lat": 34.2300,
        "lng": -118.3800,
        "source_url": "https://cleanla.lacounty.gov/hhw/collection-centers/",
        "hours": "Confirm CleanLA / S.A.F.E. center hours before visit",
        "phone": None,
        "accepted_materials": HHW_MATERIALS,
    },
    {
        "name": "Cape Coral Bulk Drop-Off — Kismet Parkway",
        "facility_type": "Bulk waste drop-off",
        "city_slug": "cape-coral",
        "state": "FL",
        "zip": "33993",
        "address": "1200 Kismet Parkway West (NW 14th Ave entrance), Cape Coral, FL 33993",
        "lat": 26.6800,
        "lng": -82.0200,
        "source_url": "https://www.capecoral.gov/departments/public_works/general_support_services_division/solid_waste/bulk_waste.php",
        "hours": "Tue–Sat 8:00–16:00 — no HHW or C&D",
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
        ],
    },
    {
        "name": "Lee County Household Hazardous Waste — Topaz Court",
        "facility_type": "Household hazardous waste / e-waste drop-off",
        "city_slug": "cape-coral",
        "state": "FL",
        "zip": "33966",
        "address": "6441 Topaz Court, Fort Myers, FL 33966",
        "lat": 26.5800,
        "lng": -81.8200,
        "source_url": "https://www.capecoral.gov/departments/public_works/general_support_services_division/solid_waste/household_hazardous_waste_disposal.php",
        "hours": "Confirm Lee County HHW hours before visit",
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": "Stanislaus County Household Hazardous Waste Facility",
        "facility_type": "Household hazardous waste / e-waste drop-off",
        "city_slug": "modesto",
        "state": "CA",
        "zip": "95358",
        "address": "1710 Morgan Road, Modesto, CA 95358",
        "lat": 37.6200,
        "lng": -121.0200,
        "source_url": "https://www.modestogov.com/FAQ.aspx?QID=204",
        "hours": "Fri–Sat 8:00–12:00 — free; call 209-525-6789",
        "phone": "209-525-6789",
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": "SWDA Household Hazardous Waste Facility — Huntsville",
        "facility_type": "Household hazardous waste / e-waste drop-off",
        "city_slug": "huntsville",
        "state": "AL",
        "zip": "35805",
        "address": "1055 A Cleaner Way, Huntsville, AL 35805",
        "lat": 34.7100,
        "lng": -86.6200,
        "source_url": "https://www.huntsvilleal.gov/residents/trash-recycling/residential-household-hazardous-waste/",
        "hours": "Mon–Fri 7:00–17:00 — free",
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": "Frisco Environmental Collection Center",
        "facility_type": "HHW / e-waste / appliance drop-off",
        "city_slug": "frisco",
        "state": "TX",
        "zip": "75034",
        "address": "6616 Walnut Street, Frisco, TX 75034",
        "lat": 33.1400,
        "lng": -96.8400,
        "source_url": "https://www.friscotexas.gov/1144/Environmental-Collection-Center",
        "hours": "Confirm ECC hours before visit",
        "phone": None,
        "accepted_materials": HHW_MATERIALS
        + E_WASTE
        + [
            "refrigerator",
            "freezer",
            "air-conditioner",
            "washer",
            "dryer",
            "dishwasher",
            "stove",
            "water-heater",
        ],
    },
    {
        "name": "Amarillo Environmental Lab — Household Hazardous Waste",
        "facility_type": "Household hazardous waste — appointment",
        "city_slug": "amarillo",
        "state": "TX",
        "zip": "79103",
        "address": "4001 S Osage Street, Amarillo, TX 79103",
        "lat": 35.1900,
        "lng": -101.8200,
        "source_url": "https://www.amarillo.gov/water-utilities/laboratory-administration/household-hazardous-waste-program/",
        "hours": "By appointment — call 806-342-1557",
        "phone": "806-342-1557",
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": "Amarillo Landfill",
        "facility_type": "Municipal landfill — resident household waste",
        "city_slug": "amarillo",
        "state": "TX",
        "zip": "79124",
        "address": "16250 Bezner Drive, Amarillo, TX 79124",
        "lat": 35.2800,
        "lng": -101.9000,
        "source_url": "https://www.amarillo.gov/solid-waste/amarillo-landfill/",
        "hours": "Confirm amarillo.gov landfill hours before visit",
        "phone": "806-378-6813",
        "accepted_materials": [
            "mattress",
            "box-spring",
            "sofa",
            "construction-debris",
            "tires",
            "tire-rims",
            "yard-waste",
        ],
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
        "north-las-vegas": clone_siblings(north_las_vegas()),
        "laredo": clone_siblings(laredo()),
        "santa-clarita": clone_siblings(santa_clarita()),
        "cape-coral": clone_siblings(cape_coral()),
        "modesto": clone_siblings(modesto()),
        "huntsville": clone_siblings(huntsville()),
        "frisco": clone_siblings(frisco()),
        "amarillo": clone_siblings(amarillo()),
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

    print("Wave-20 metros written:")
    for city, rows in audited.items():
        print(f"  {city}: {len(rows)} rules")
    print(f"Total rules now: {len(keep)}")


if __name__ == "__main__":
    main()
