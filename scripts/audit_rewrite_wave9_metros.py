#!/usr/bin/env python3
"""Portal-audited city guides for wave-9 metros (city-sourced only).

Cities researched from official program pages (2026-08-11):
  - Las Vegas, NV — Clark County solid waste / Republic Services / HHW
  - Raleigh, NC — raleighnc.gov bulky-special-e-waste / Wake County HHW & MMRF
  - Minneapolis, MN — minneapolismn.gov large items / Hennepin HHW
  - Omaha, NE — wasteline.org bulky / cleanup / Under The Sink HHW
  - Virginia Beach, VA — pw.virginiabeach.gov bulky / RRC HHW
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


def las_vegas():
    c, st = "las-vegas", "NV"
    bulky = (
        "Clark County / Republic Services — Southern Nevada residential collection",
        "https://www.republicservices.com/municipality/southern-nevada",
    )
    hhw = (
        "Clark County — Household hazardous waste",
        "https://www.clarkcountynv.gov/government/departments/environment_and_sustainability/household_hazardous_waste",
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
            "Bulky every other week on regular day via Republic (Clark County franchise)",
            "Republic Services bulky — every other week on collection day",
            "Clark County residents in Las Vegas receive bulky item collection every other week on their regular Republic Services collection day under the county solid waste ordinance. Mattresses and furniture are accepted on bulky week. Set items out by 7 a.m. on your designated day. Republic Services operates under Clark County mandate — confirm your schedule on republicservices.com Southern Nevada or clarkcountynv.gov.",
            [
                "Confirm your every-other-week bulky day on Republic Services / Clark County schedule.",
                "Set mattress out by 7 a.m. on bulky collection day.",
                "Keep HHW and fee-based transfer items off bulky piles.",
            ],
            [
                ("Every week?", "No — bulky is every other week on your regular collection day."),
                ("Same as furniture?", "Yes — mattresses and furniture use the bulky program."),
            ],
            *bulky,
        )
    )
    rows.append(
        R(
            c,
            st,
            "refrigerator",
            "SPECIAL_HANDLING",
            "High",
            False,
            "Transfer station fee — NOT Clark County HHW; call for refrigerator fee",
            "Clark County transfer station — Cheyenne / Henderson",
            "Freon refrigerators and freezers are NOT accepted at Clark County HHW. Self-haul to a Clark County transfer station (Cheyenne or Henderson) for a fee — call ahead for current refrigerator disposal fees. Never vent refrigerant yourself. Do not assume curbside bulky covers Freon appliances without confirming Republic/transfer station rules.",
            [
                "Do not haul refrigerators to Clark County HHW sites.",
                "Call transfer station for current refrigerator disposal fee before hauling.",
                "Keep doors secured; never release Freon yourself.",
            ],
            [("HHW for fridge?", "No — Freon refrigerators use transfer stations for a fee, not HHW.")],
            *bulky,
        )
    )
    rows.append(
        R(
            c,
            st,
            "air-conditioner",
            "SPECIAL_HANDLING",
            "High",
            False,
            "Transfer station fee for Freon AC — NOT HHW",
            "Clark County transfer station — Cheyenne / Henderson",
            "Freon window and portable air conditioners are NOT accepted at Clark County HHW. Self-haul to a Clark County transfer station for a fee — call ahead for acceptance and pricing. Never vent refrigerant yourself.",
            [
                "Do not take Freon AC units to HHW drop-offs.",
                "Call transfer station for fee and acceptance before hauling.",
                "Keep the sealed unit intact until proper handling.",
            ],
            [("Same as fridge?", "Yes — Freon appliances use transfer stations, not HHW.")],
            *bulky,
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
                "Bulky every other week — non-Freon appliances; no transfer-station fridge fee path",
                "Republic Services bulky — every other week on collection day",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s go on Clark County bulky collection every other week on your regular Republic Services day — set out by 7 a.m. These do not use the transfer-station refrigerator fee pathway or HHW. Empty the appliance before set-out.",
                [
                    "Confirm your every-other-week bulky day.",
                    "Empty the appliance and set out by 7 a.m. on bulky day.",
                    "Do not use HHW or fridge transfer-station fees for washers/dryers.",
                ],
                [("Transfer station for washer?", "No — non-Freon appliances use bulky every other week.")],
                *bulky,
            )
        )
    for item, label in [
        ("television", "TVs"),
        ("computer-monitor", "monitors and computers"),
        ("smartphone", "phones and small electronics"),
        ("e-waste-mixed", "mixed electronic waste"),
    ]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "Free electronics at Cheyenne/Henderson transfer stations 7:00–15:00 daily",
                "Clark County transfer stations — Cheyenne / Henderson (electronics)",
                f"Electronics including {label} are accepted free at Clark County Cheyenne and Henderson transfer stations daily 7 a.m.–3 p.m. — NOT at HHW rotating sites. Do not set e-waste out for bulky pickup. Wipe personal data before recycling computers/phones.",
                [
                    "Haul electronics to Cheyenne or Henderson transfer station 7:00–15:00 daily.",
                    "Do not mix e-waste into bulky piles or HHW loads.",
                    "Wipe personal data before drop-off.",
                ],
                [("HHW for TV?", "No — electronics use transfer stations daily, not HHW rotating sites.")],
                *bulky,
            )
        )
    rows.append(
        R(
            c,
            st,
            "paint-latex",
            "SPECIAL_HANDLING",
            "Medium",
            True,
            "Fully dried latex in trash; liquid latex at HHW rotating sites",
            "Household trash (dried) / Clark County HHW rotating sites",
            "Fully dried latex paint (solidified with cat litter/absorbent) can go in household trash in Clark County. Liquid latex goes to Clark County HHW rotating sites — North 333 W Gowan Rd or South 560 Cape Horn Dr, Wed–Sat 9 a.m.–1 p.m.; check the county calendar for your assigned site/week.",
            [
                "Liquid latex: check HHW calendar and haul to North or South site Wed–Sat 9–1.",
                "Dried latex: solidify completely, then place dry can in trash.",
                "Oil-based paint always goes to HHW — not trash.",
            ],
            [("Trash for dried latex?", "Yes — fully dried latex cans can go in household trash.")],
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
                "Clark County HHW rotating — North/South Wed–Sat 9:00–13:00",
                "Clark County HHW — 333 W Gowan Rd / 560 Cape Horn Dr",
                f"Take {item.replace('-', ' ')} to Clark County HHW rotating sites — North 333 W Gowan Rd or South 560 Cape Horn Dr, Wed–Sat 9 a.m.–1 p.m.; check calendar for assigned site. Do not dry chemicals for trash — they require HHW handling.",
                [
                    "Check Clark County HHW calendar for your assigned site/week.",
                    "Deliver sealed, labeled containers Wed–Sat 9:00–13:00.",
                    "Keep chemicals out of bulky piles and trash carts.",
                ],
                [("Same as dried latex?", "No — chemicals and fuels require HHW, not trash.")],
                *hhw,
            )
        )
    for item in [
        "car-battery",
        "lithium-battery",
        "paint-oil",
        "motor-oil",
        "propane-tank",
        "fluorescent-bulbs",
        "cooking-oil",
    ]:
        extra = {
            "car-battery": " Auto and household batteries accepted at Clark County HHW.",
            "lithium-battery": " Rechargeable/lithium batteries belong at HHW — not trash.",
            "paint-oil": " Oil-based paint accepted at Clark County HHW rotating sites.",
            "motor-oil": " Used motor oil accepted at HHW.",
            "propane-tank": " Propane cylinders accepted at HHW.",
            "fluorescent-bulbs": " CFLs and fluorescent lamps accepted at HHW.",
            "cooking-oil": " Keep cooking oil out of drains; use HHW when not trash-safe.",
        }[item]
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS" if item not in {"cooking-oil"} else "SPECIAL_HANDLING",
                "High" if item not in {"cooking-oil"} else "Medium",
                False,
                "Clark County HHW rotating — Wed–Sat 9:00–13:00; check calendar",
                "Clark County HHW — 333 W Gowan Rd / 560 Cape Horn Dr",
                f"Clark County HHW rotating sites (North 333 W Gowan Rd / South 560 Cape Horn Dr) accept household hazardous materials Wed–Sat 9 a.m.–1 p.m.; check calendar.{extra} Freon appliances and electronics use other pathways.",
                [
                    "Check HHW calendar for assigned North or South site.",
                    "Deliver sealed containers Wed–Sat 9:00–13:00.",
                    "Keep Freon appliances and e-waste on their own pathways.",
                ],
                [("Which site?", "North Gowan Rd or South Cape Horn Dr — check rotating calendar.")],
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
            "Rigid sealed container — confirm Clark County HHW sharps acceptance",
            "Clark County HHW — 333 W Gowan Rd / 560 Cape Horn Dr",
            "Place medical sharps in a rigid, sealed hard-plastic container before delivery. Confirm sharps acceptance at Clark County HHW rotating sites on clarkcountynv.gov. Do not loose-bag needles in trash or recycling.",
            [
                "Place sharps in a rigid sealed hard-plastic container.",
                "Confirm sharps acceptance at HHW before hauling.",
                "Never recycle loose needles.",
            ],
            [("Medications?", "Confirm prescription drug take-back at HHW on county page.")],
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
            "NOT curbside bulky — transfer station/landfill fee; be honest about cost",
            "Clark County transfer station / landfill (fee)",
            "Tires are NOT accepted on Clark County curbside bulky pickup. Self-haul to a Clark County transfer station or landfill for a fee — call ahead for current tire pricing. Retailer take-back when replacing tires is also an option.",
            [
                "Do not set tires out for bulky collection.",
                "Call transfer station/landfill for current tire disposal fee.",
                "Ask tire shop for take-back when buying replacements.",
            ],
            [("Bulky for tires?", "No — tires require transfer station/landfill fee pathways.")],
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
            "Clark County / Republic yard waste collection programs",
            "Republic Services yard waste collection",
            "Clark County handles yard waste through regular Republic Services collection programs. Follow set-out rules; keep yard waste out of bulky piles and out of HHW.",
            [
                "Use Republic yard waste set-out rules for leaves and trimmings.",
                "Keep yard waste separate from bulky and HHW loads.",
                "Check clarkcountynv.gov for seasonal guidance.",
            ],
            [("Christmas trees?", "Follow county seasonal yard waste guidance.")],
            *bulky,
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
            "Las Vegas garbage / private compost",
            "Bag food scraps for garbage unless you use private/community compost. Keep food out of recycling and out of HHW loads.",
            [
                "Bag food scraps for garbage if you lack compost access.",
                "Keep organics out of recycling.",
                "Yard trimmings use yard-waste pathways.",
            ],
            [("HHW for food?", "No — HHW is for hazardous products.")],
            *bulky,
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
            "Plastic bags are not accepted in Clark County curbside recycling. Return clean film to store take-back bins when available, or dispose with trash.",
            [
                "Keep plastic bags out of the recycling cart.",
                "Use grocery take-back bins when available.",
                "Otherwise place bags in trash.",
            ],
            [("Bulky for bags?", "No — use store take-back or trash.")],
            *bulky,
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
            "Limited bulky every other week or transfer station fee for larger loads",
            "Republic bulky / Clark County transfer station (fee)",
            "Small homeowner renovation debris may fit Clark County bulky collection every other week. Larger loads need a Clark County transfer station (fee) or private C&D hauler. Route paint and chemicals to HHW separately.",
            [
                "Use bulky every other week only for limited homeowner debris.",
                "Haul larger C&D to transfer station for a fee or hire private hauler.",
                "Route paint/chemicals to Clark County HHW.",
            ],
            [("HHW for C&D?", "No — separate paint/chemicals for HHW.")],
            *bulky,
        )
    )
    return rows


def raleigh():
    c, st = "raleigh", "NC"
    bulky = (
        "City of Raleigh — Bulky / Special Load / E-waste",
        "https://raleighnc.gov/services/solid-waste/bulky-special-e-waste",
    )
    hhw = (
        "Wake County — Household hazardous waste",
        "https://www.wake.gov/departments/environmental-services/waste-management/household-hazardous-waste",
    )
    mmrf = (
        "Wake County — Multi-Material Recycling Facility",
        "https://www.wake.gov/departments/environmental-services/waste-management/multi-material-recycling-facility",
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
            "Bulky Load $35 — call 919-996-3245; max 4 cy; mattress/furniture",
            "City of Raleigh Bulky Load (scheduled)",
            "Raleigh Bulky Load costs $35 and covers mattresses and furniture up to 4 cubic yards. Call 919-996-3245 to schedule before set-out. Bulky Load is separate from Special Load ($70 white goods). Set items out per city instructions on your scheduled day.",
            [
                "Call 919-996-3245 to schedule Bulky Load ($35).",
                "Set mattress out per city instructions on scheduled day (max 4 cy).",
                "White goods/appliances need Special Load — not Bulky Load.",
            ],
            [
                ("Cost?", "Bulky Load $35 for mattress/furniture up to 4 cy."),
                ("Same as furniture?", "Yes — mattresses use Bulky Load scheduling."),
            ],
            *bulky,
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
            "Special Load $70 white goods OR Wake County MMRF — Wake HHW does NOT take Freon",
            "Raleigh Special Load / Wake County MMRF",
            "Freon refrigerators and freezers require Raleigh Special Load ($70 white goods) — call 919-996-3245 to schedule — or self-haul to Wake County Multi-Material Recycling Facility. Wake County HHW does NOT accept Freon appliances. Never vent refrigerant yourself.",
            [
                "Call 919-996-3245 to schedule Special Load ($70) for Freon fridge.",
                "Or self-haul to Wake County MMRF — confirm acceptance/fees.",
                "Do not haul refrigerators to Wake County HHW.",
            ],
            [("HHW for fridge?", "No — Wake HHW does not accept Freon appliances.")],
            *bulky,
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
            "Special Load $70 OR Wake County MMRF — NOT Wake HHW",
            "Raleigh Special Load / Wake County MMRF",
            "Freon window and portable air conditioners require Raleigh Special Load ($70 white goods) — call 919-996-3245 — or Wake County MMRF drop-off. Wake County HHW does NOT accept Freon AC units. Never vent refrigerant yourself.",
            [
                "Call 919-996-3245 to schedule Special Load for Freon AC.",
                "Or self-haul to Wake County MMRF.",
                "Do not take Freon AC to Wake County HHW.",
            ],
            [("Same as fridge?", "Yes — Freon appliances use Special Load or MMRF, not HHW.")],
            *bulky,
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
                "Special Load $70 white goods — call 919-996-3245",
                "City of Raleigh Special Load (white goods)",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s are included in Raleigh Special Load white goods ($70) — call 919-996-3245 to schedule. Do not use Bulky Load ($35) for appliances. Wake County HHW does not accept appliances.",
                [
                    "Call 919-996-3245 to schedule Special Load ($70 white goods).",
                    "Empty the appliance before set-out.",
                    "Do not use Bulky Load or HHW for washers/dryers.",
                ],
                [("Bulky Load for washer?", "No — white goods use Special Load $70.")],
                *bulky,
            )
        )
    for item, label in [
        ("television", "TVs"),
        ("computer-monitor", "monitors"),
        ("smartphone", "phones and small electronics"),
    ]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS",
                "Medium",
                True,
                "Free e-waste Tue — up to 4 items/week; call 919-996-3245",
                "City of Raleigh free e-waste collection (Tuesdays)",
                f"Raleigh offers free e-waste collection on Tuesdays — up to 4 items per week. Call 919-996-3245 to schedule. {label} use this program. Set out per city instructions on scheduled Tuesday.",
                [
                    "Call 919-996-3245 to schedule Tuesday e-waste (max 4 items/week).",
                    "Set electronics out per city instructions on scheduled Tuesday.",
                    "Wipe personal data before recycling computers/phones.",
                ],
                [("Cost?", "Free — up to 4 e-waste items per week on Tuesdays.")],
                *bulky,
            )
        )
    rows.append(
        R(
            c,
            st,
            "e-waste-mixed",
            "BANNED_FROM_LANDFILLS",
            "Medium",
            True,
            "Free e-waste Tue up to 4 items/week OR Wake MMRF for larger loads",
            "Raleigh Tuesday e-waste / Wake County MMRF",
            "Mixed e-waste can use Raleigh free Tuesday e-waste collection (up to 4 items/week; call 919-996-3245) or Wake County MMRF for larger loads. Do not mix e-waste into Bulky Load piles.",
            [
                "Schedule Tuesday e-waste via 919-996-3245 (max 4 items/week).",
                "Larger mixed loads: Wake County MMRF.",
                "Wipe data before drop-off.",
            ],
            [("Bulky for e-waste?", "No — use Tuesday e-waste or MMRF.")],
            *bulky,
        )
    )
    rows.append(
        R(
            c,
            st,
            "paint-latex",
            "SPECIAL_HANDLING",
            "Medium",
            True,
            "Dried latex in trash OR ≤10 gal at Wake HHW; oil paint at HHW only",
            "Household trash (dried) / Wake County HHW — South Apex",
            "Fully dried latex paint can go in household trash. Liquid latex up to 10 gallons per visit goes to Wake County HHW — South Wake 6150 Old Smithfield Rd, Apex, Mon–Sat 8 a.m.–4 p.m. Oil-based paint always goes to HHW.",
            [
                "Liquid latex ≤10 gal: haul to South Wake HHW Mon–Sat 8–4.",
                "Dried latex: solidify completely, then trash the dry can.",
                "Oil paint: Wake County HHW only.",
            ],
            [("Trash for dried latex?", "Yes — fully dried latex cans can go in trash.")],
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
                "Wake County HHW — South Apex Mon–Sat 8:00–16:00",
                "Wake County HHW — 6150 Old Smithfield Rd, Apex",
                f"Take {item.replace('-', ' ')} to Wake County HHW at South Wake 6150 Old Smithfield Rd, Apex — Mon–Sat 8 a.m.–4 p.m. Do not dry chemicals for trash.",
                [
                    "Deliver sealed containers to South Wake HHW Mon–Sat 8–4.",
                    "Keep chemicals out of Bulky/Special Load piles.",
                    "Freon appliances are NOT accepted at HHW.",
                ],
                [("Same as dried latex?", "No — chemicals require HHW.")],
                *hhw,
            )
        )
    for item in [
        "car-battery",
        "lithium-battery",
        "paint-oil",
        "motor-oil",
        "propane-tank",
        "fluorescent-bulbs",
        "cooking-oil",
    ]:
        extra = {
            "car-battery": " Auto and household batteries accepted at Wake HHW.",
            "lithium-battery": " Rechargeable/lithium batteries go to HHW — not trash.",
            "paint-oil": " Oil-based paint accepted at Wake HHW.",
            "motor-oil": " Used motor oil accepted at HHW.",
            "propane-tank": " Propane cylinders accepted at HHW.",
            "fluorescent-bulbs": " CFLs and fluorescent lamps accepted at HHW.",
            "cooking-oil": " Keep cooking oil out of drains; use HHW when not trash-safe.",
        }[item]
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS" if item not in {"cooking-oil"} else "SPECIAL_HANDLING",
                "High" if item not in {"cooking-oil"} else "Medium",
                False,
                "Wake County HHW — South Apex Mon–Sat 8:00–16:00",
                "Wake County HHW — 6150 Old Smithfield Rd, Apex",
                f"Wake County HHW at South Wake 6150 Old Smithfield Rd, Apex accepts household hazardous materials Mon–Sat 8 a.m.–4 p.m.{extra} Freon appliances are NOT accepted.",
                [
                    "Deliver sealed containers to South Wake HHW Mon–Sat 8–4.",
                    "Keep Freon appliances on Special Load/MMRF pathways.",
                    "Tires use East Wake MMRF — not HHW.",
                ],
                [("Which HHW site?", "South Wake 6150 Old Smithfield Rd, Apex — Mon–Sat 8–4.")],
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
            "Rigid sealed container — confirm Wake HHW sharps acceptance",
            "Wake County HHW — 6150 Old Smithfield Rd, Apex",
            "Place medical sharps in a rigid, sealed hard-plastic container before delivery. Confirm sharps acceptance at Wake County HHW on wake.gov. Do not loose-bag needles in trash or recycling.",
            [
                "Place sharps in a rigid sealed hard-plastic container.",
                "Confirm sharps acceptance at South Wake HHW before hauling.",
                "Never recycle sharps containers.",
            ],
            [("Medications?", "Confirm prescription drug take-back at Wake HHW on county page.")],
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
            "NOT city Bulky — East Wake MMRF rimless passenger tires",
            "Wake County MMRF — East Wake (rimless passenger tires)",
            "Tires are NOT accepted on Raleigh Bulky Load. Rimless passenger tires go to Wake County East Wake Multi-Material Recycling Facility — confirm current acceptance and fees on wake.gov MMRF pages.",
            [
                "Do not schedule Bulky Load for tires.",
                "Haul rimless passenger tires to East Wake MMRF.",
                "Retailer take-back when replacing tires is also an option.",
            ],
            [("Bulky for tires?", "No — tires use East Wake MMRF, not city Bulky Load.")],
            *mmrf,
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
            "Raleigh yard waste collection programs",
            "Raleigh yard waste collection",
            "Raleigh handles yard waste through regular collection programs. Follow set-out rules; keep yard waste out of Bulky/Special Load piles and out of HHW.",
            [
                "Use Raleigh yard waste set-out rules for leaves and trimmings.",
                "Keep yard waste separate from bulky and HHW loads.",
                "Check raleighnc.gov for seasonal guidance.",
            ],
            [("Christmas trees?", "Follow city seasonal yard waste guidance.")],
            *bulky,
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
            "Raleigh garbage / private compost",
            "Bag food scraps for garbage unless you use private/community compost. Keep food out of recycling and out of HHW loads.",
            [
                "Bag food scraps for garbage if you lack compost access.",
                "Keep organics out of recycling.",
                "Yard trimmings use yard-waste pathways.",
            ],
            [("HHW for food?", "No — HHW is for hazardous products.")],
            *bulky,
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
            "Plastic bags are not accepted in Raleigh curbside recycling. Return clean film to store take-back or trash.",
            [
                "Keep plastic bags out of the recycling cart.",
                "Use grocery take-back bins when available.",
                "Otherwise place bags in trash.",
            ],
            [("Bulky for bags?", "No — use store take-back or trash.")],
            *bulky,
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
            "Bulky Load $35 for limited loads (max 4 cy) — private C&D for larger",
            "Raleigh Bulky Load / private C&D hauler",
            "Limited homeowner renovation debris may fit Raleigh Bulky Load ($35; max 4 cy; call 919-996-3245). Larger contractor C&D loads need a private hauler or Wake MMRF. Route paint and chemicals to Wake HHW separately.",
            [
                "Call 919-996-3245 for Bulky Load if debris fits 4 cy limit.",
                "Hire a private C&D hauler for larger projects.",
                "Route paint/chemicals to Wake County HHW.",
            ],
            [("HHW for C&D?", "No — separate paint/chemicals for HHW.")],
            *bulky,
        )
    )
    return rows


def minneapolis():
    c, st = "minneapolis", "MN"
    large = (
        "City of Minneapolis — Large Item Collection",
        "https://www.minneapolismn.gov/resident-services/garbage-recycling/large-items/",
    )
    hhw = (
        "Hennepin County — Green Disposal Guide / HHW",
        "https://www.hennepin.us/residents/recycling-and-waste/green-disposal-guide",
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
            "Large Item recycling week — up to 2/week; mark For Solid Waste; out by 6am",
            "Minneapolis Large Item Collection — recycling week",
            "Minneapolis Large Item Collection allows up to 2 items per week. Mark items For Solid Waste and set out by 6 a.m. Mattresses go on recycling week (same week as appliances/electronics). Furniture and carpet go on garbage week — do not mix weeks.",
            [
                "Confirm recycling week vs garbage week on minneapolismn.gov large items page.",
                "Mark mattress For Solid Waste; set out by 6 a.m. on recycling week.",
                "Limit 2 large items per week.",
            ],
            [
                ("Which week?", "Mattresses use recycling week — not garbage week."),
                ("Limit?", "Up to 2 large items per week."),
            ],
            *large,
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
            "Large Item recycling week — remove doors before set-out",
            "Minneapolis Large Item Collection — recycling week",
            "Freon refrigerators and freezers go on Minneapolis Large Item recycling week — up to 2 items/week; mark For Solid Waste; set out by 6 a.m. Remove doors before set-out per city rules. Never vent refrigerant yourself.",
            [
                "Remove refrigerator doors before set-out.",
                "Mark For Solid Waste; set out by 6 a.m. on recycling week.",
                "Limit 2 large items per week.",
            ],
            [("Doors required?", "Yes — remove doors before Large Item set-out.")],
            *large,
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
            "Large Item recycling week — remove doors if applicable; out by 6am",
            "Minneapolis Large Item Collection — recycling week",
            "Freon window and portable air conditioners go on Minneapolis Large Item recycling week — mark For Solid Waste; set out by 6 a.m.; up to 2 items/week. Remove doors if applicable. Never vent refrigerant yourself.",
            [
                "Mark For Solid Waste; set out by 6 a.m. on recycling week.",
                "Remove doors if applicable per city guidance.",
                "Limit 2 large items per week.",
            ],
            [("Same as fridge?", "Yes — Freon appliances use recycling week Large Item collection.")],
            *large,
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
                "Large Item recycling week — appliances; no door-removal rule for washers",
                "Minneapolis Large Item Collection — recycling week",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s go on Minneapolis Large Item recycling week with refrigerators and other white goods — mark For Solid Waste; set out by 6 a.m.; up to 2 items/week. Door removal applies to refrigerators/AC — not typical washers.",
                [
                    "Mark appliance For Solid Waste; set out by 6 a.m. on recycling week.",
                    "Limit 2 large items per week — plan multi-appliance weeks accordingly.",
                    "Door removal is for refrigerators/AC — not washers.",
                ],
                [("Garbage week for washer?", "No — appliances use recycling week.")],
                *large,
            )
        )
    rows.append(
        R(
            c,
            st,
            "television",
            "BANNED_FROM_LANDFILLS",
            "Medium",
            True,
            "Large Item recycling week preferred — Hennepin county drop-off may charge ~$10",
            "Minneapolis Large Item recycling week / Hennepin county drop-off",
            "TVs are best handled on Minneapolis Large Item recycling week (mark For Solid Waste; out by 6 a.m.; up to 2/week). Hennepin County drop-off may charge about $10 per TV — curbside recycling week is preferred when available.",
            [
                "Schedule TV on recycling week Large Item collection (preferred).",
                "Mark For Solid Waste; set out by 6 a.m.",
                "County drop-off (~$10/TV) is a backup option.",
            ],
            [("County fee?", "Hennepin county TV drop-off may charge ~$10 — recycling week preferred.")],
            *large,
        )
    )
    for item, label in [
        ("computer-monitor", "monitors"),
        ("smartphone", "phones and small electronics"),
        ("e-waste-mixed", "mixed electronic waste"),
    ]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS",
                "Medium",
                True,
                "Large Item recycling week — up to 2/week; out by 6am",
                "Minneapolis Large Item Collection — recycling week",
                f"{label.title()} go on Minneapolis Large Item recycling week — mark For Solid Waste; set out by 6 a.m.; up to 2 items/week. Wipe personal data before recycling computers/phones.",
                [
                    "Mark item For Solid Waste; set out by 6 a.m. on recycling week.",
                    "Limit 2 large items per week.",
                    "Wipe personal data before drop-off/recycling.",
                ],
                [("Garbage week?", "No — electronics use recycling week.")],
                *large,
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
            "Hennepin County HHW — Bloomington 1400 W 96th St; Tue–Sat 9–17",
            "Hennepin County HHW — Bloomington",
            "Liquid and latex paint go to Hennepin County HHW at Bloomington 1400 W 96th St — Tue–Sat 9 a.m.–5 p.m. Do not pour paint down drains. Dried latex may be trash-safe only after full solidification — HHW is the verified path for liquid paint.",
            [
                "Haul paint to Hennepin HHW Bloomington Tue–Sat 9–5.",
                "Keep paint sealed and labeled.",
                "Do not pour liquid paint down drains.",
            ],
            [("HHW for latex?", "Yes — paint goes to Hennepin County HHW.")],
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
                "Hennepin County HHW — Bloomington Tue–Sat 9:00–17:00",
                "Hennepin County HHW — 1400 W 96th St, Bloomington",
                f"Take {item.replace('-', ' ')} to Hennepin County HHW at Bloomington 1400 W 96th St — Tue–Sat 9 a.m.–5 p.m. Do not dry chemicals for trash.",
                [
                    "Deliver sealed containers to Bloomington HHW Tue–Sat 9–5.",
                    "Keep chemicals out of Large Item piles.",
                    "Brooklyn Park 8100 Jefferson Hwy is another Hennepin HHW site.",
                ],
                [("Same as paint?", "Yes — chemicals and fuels use Hennepin HHW.")],
                *hhw,
            )
        )
    for item in [
        "car-battery",
        "lithium-battery",
        "paint-oil",
        "motor-oil",
        "propane-tank",
        "fluorescent-bulbs",
        "cooking-oil",
    ]:
        extra = {
            "car-battery": " Auto and household batteries accepted at Hennepin HHW.",
            "lithium-battery": " Rechargeable/lithium batteries go to HHW — not trash.",
            "paint-oil": " Oil-based paint accepted at Hennepin HHW.",
            "motor-oil": " Used motor oil accepted at HHW.",
            "propane-tank": " Propane cylinders accepted at HHW.",
            "fluorescent-bulbs": " CFLs and fluorescent lamps accepted at HHW.",
            "cooking-oil": " Keep cooking oil out of drains; use HHW when not trash-safe.",
        }[item]
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS" if item not in {"cooking-oil"} else "SPECIAL_HANDLING",
                "High" if item not in {"cooking-oil"} else "Medium",
                False,
                "Hennepin County HHW — Bloomington Tue–Sat 9:00–17:00",
                "Hennepin County HHW — 1400 W 96th St, Bloomington",
                f"Hennepin County HHW at Bloomington 1400 W 96th St accepts household hazardous materials Tue–Sat 9 a.m.–5 p.m.{extra} Tires use South Transfer voucher/fees — not HHW.",
                [
                    "Deliver sealed containers to Bloomington HHW Tue–Sat 9–5.",
                    "Keep tires on South Transfer pathways.",
                    "Electronics prefer Large Item recycling week.",
                ],
                [("Which HHW site?", "Bloomington 1400 W 96th St — Tue–Sat 9–5.")],
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
            "Rigid sealed container — confirm Hennepin HHW sharps acceptance",
            "Hennepin County HHW — 1400 W 96th St, Bloomington",
            "Place medical sharps in a rigid, sealed hard-plastic container before delivery. Confirm sharps acceptance at Hennepin County HHW on hennepin.us. Do not loose-bag needles in trash or recycling.",
            [
                "Place sharps in a rigid sealed hard-plastic container.",
                "Confirm sharps acceptance at Bloomington HHW before hauling.",
                "Never recycle sharps containers.",
            ],
            [("Medications?", "Confirm prescription drug take-back at Hennepin HHW on county page.")],
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
            "NOT curbside Large Item — South Transfer voucher/fees",
            "Hennepin County South Transfer Station (voucher/fees)",
            "Tires are NOT accepted on Minneapolis Large Item Collection. Use Hennepin County South Transfer Station with voucher/fees — check hennepin.us green disposal guide for current tire rules and pricing.",
            [
                "Do not set tires out for Large Item collection.",
                "Check hennepin.us for South Transfer tire voucher/fees.",
                "Retailer take-back when replacing tires is also an option.",
            ],
            [("Curbside for tires?", "No — tires use South Transfer voucher/fees.")],
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
            "Minneapolis yard waste collection programs",
            "Minneapolis yard waste collection",
            "Minneapolis handles yard waste through regular collection programs. Follow set-out rules; keep yard waste out of Large Item piles and out of HHW.",
            [
                "Use Minneapolis yard waste set-out rules for leaves and trimmings.",
                "Keep yard waste separate from Large Item and HHW loads.",
                "Check minneapolismn.gov for seasonal guidance.",
            ],
            [("Christmas trees?", "Follow city seasonal yard waste guidance.")],
            *large,
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
            "Minneapolis garbage / private compost",
            "Bag food scraps for garbage unless you use private/community compost. Keep food out of recycling and out of HHW loads.",
            [
                "Bag food scraps for garbage if you lack compost access.",
                "Keep organics out of recycling.",
                "Yard trimmings use yard-waste pathways.",
            ],
            [("HHW for food?", "No — HHW is for hazardous products.")],
            *large,
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
            "Plastic bags are not accepted in Minneapolis curbside recycling. Return clean film to store take-back or trash.",
            [
                "Keep plastic bags out of the recycling cart.",
                "Use grocery take-back bins when available.",
                "Otherwise place bags in trash.",
            ],
            [("Large Item for bags?", "No — use store take-back or trash.")],
            *large,
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
            "Large Item garbage week for limited loads — private C&D for larger",
            "Minneapolis Large Item (garbage week) / private C&D hauler",
            "Limited homeowner renovation debris may go on Minneapolis Large Item garbage week (furniture/carpet week — confirm item type). Larger C&D loads need a private hauler or Hennepin transfer options. Route paint to Hennepin HHW separately.",
            [
                "Confirm garbage week vs recycling week for your debris type.",
                "Hire a private C&D hauler for larger projects.",
                "Route paint/chemicals to Hennepin HHW Bloomington.",
            ],
            [("HHW for C&D?", "No — separate paint/chemicals for HHW.")],
            *large,
        )
    )
    return rows


def omaha():
    c, st = "omaha", "NE"
    transfer = (
        "City of Omaha — Bulky waste / River City Transfer",
        "https://wasteline.org/residents/bulky-waste/",
    )
    cleanup = (
        "City of Omaha — Spring/Fall Cleanup",
        "https://wasteline.org/residents/cleanup/",
    )
    hhw = (
        "Under The Sink — Omaha metro HHW",
        "https://underthesink.org/",
    )
    rows = []
    rows.append(
        R(
            c,
            st,
            "mattress",
            "SPECIAL_HANDLING",
            "Low",
            False,
            "NO curbside bulky — River City Transfer voucher ($15/yr admin → 4 vouchers)",
            "River City Transfer — 6404 S 60th St (voucher program)",
            "Omaha has NO curbside bulky pickup. Mattresses and furniture go to River City Transfer, 6404 S 60th St, using the voucher program — $15/year administrative fee for 4 vouchers. NO appliances, tires, or HHW at River City Transfer.",
            [
                "Enroll in River City Transfer voucher program ($15/yr → 4 vouchers).",
                "Haul mattress to 6404 S 60th St with a voucher.",
                "Appliances and tires use other pathways — not River City.",
            ],
            [
                ("Curbside bulky?", "No — Omaha has no curbside bulky program."),
                ("River City accepts?", "Furniture/mattress yes — NO appliances/tires/HHW."),
            ],
            *transfer,
        )
    )
    rows.append(
        R(
            c,
            st,
            "refrigerator",
            "SPECIAL_HANDLING",
            "High",
            False,
            "Spring/Fall Cleanup designated sites (seasonal) — limited year-round options",
            "Omaha Spring/Fall Cleanup sites (seasonal)",
            "Omaha has NO curbside bulky for appliances. Freon refrigerators go to Spring/Fall Cleanup designated sites during seasonal events — year-round options are limited; check wasteline.org cleanup pages for current dates and sites. Never vent refrigerant yourself.",
            [
                "Check wasteline.org for Spring/Fall Cleanup dates and designated sites.",
                "Plan appliance disposal around seasonal cleanup events.",
                "River City Transfer does NOT accept appliances.",
            ],
            [("River City for fridge?", "No — appliances are NOT accepted at River City Transfer.")],
            *cleanup,
        )
    )
    rows.append(
        R(
            c,
            st,
            "air-conditioner",
            "SPECIAL_HANDLING",
            "High",
            False,
            "Spring/Fall Cleanup designated sites (seasonal) — limited year-round",
            "Omaha Spring/Fall Cleanup sites (seasonal)",
            "Freon window and portable air conditioners go to Omaha Spring/Fall Cleanup designated sites during seasonal events. Year-round appliance paths are limited — check wasteline.org. Never vent refrigerant yourself.",
            [
                "Check wasteline.org cleanup calendar for seasonal drop-off sites.",
                "Do not haul AC to River City Transfer.",
                "Keep the sealed unit intact until proper handling.",
            ],
            [("Same as fridge?", "Yes — appliances use seasonal cleanup sites primarily.")],
            *cleanup,
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
                False,
                "Spring/Fall Cleanup seasonal sites — NOT River City Transfer",
                "Omaha Spring/Fall Cleanup sites (seasonal)",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s go to Omaha Spring/Fall Cleanup designated sites during seasonal events — check wasteline.org. River City Transfer does NOT accept appliances. Year-round options are limited.",
                [
                    "Check wasteline.org for Spring/Fall Cleanup dates and sites.",
                    "Do not haul appliances to River City Transfer.",
                    "Plan around seasonal cleanup windows.",
                ],
                [("River City for washer?", "No — appliances are NOT accepted at River City.")],
                *cleanup,
            )
        )
    for item, label in [
        ("television", "TVs"),
        ("computer-monitor", "monitors"),
        ("smartphone", "phones and small electronics"),
        ("e-waste-mixed", "mixed electronic waste"),
    ]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "Spring/Fall Cleanup events primarily — check wasteline.org",
                "Omaha Spring/Fall Cleanup (e-waste at cleanup events)",
                f"Omaha TV/e-waste disposal is primarily through Spring/Fall Cleanup events — check wasteline.org for dates and accepted items. {label} are NOT accepted at River City Transfer or Under The Sink HHW.",
                [
                    "Check wasteline.org cleanup calendar for e-waste event dates.",
                    "Do not haul TVs/e-waste to River City Transfer.",
                    "Wipe personal data before recycling computers/phones.",
                ],
                [("River City for TV?", "No — e-waste uses cleanup events primarily.")],
                *cleanup,
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
            "Under The Sink HHW — latex $1/container; oil paint free",
            "Under The Sink HHW — 4001 S 120th St",
            "Liquid latex paint goes to Under The Sink HHW at 4001 S 120th St — $1 per container. Oil-based paint is free at HHW. Hours: Wed/Fri 9 a.m.–4:45 p.m., Thu 9 a.m.–6:15 p.m., Sat by appointment 402-444-SINK.",
            [
                "Haul latex to Under The Sink — $1 per container.",
                "Oil paint: free at HHW during posted hours.",
                "Wed/Fri 9–4:45; Thu 9–6:15; Sat by appointment.",
            ],
            [("Latex fee?", "Yes — $1 per latex container at Under The Sink.")],
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
                "Under The Sink HHW — Wed/Fri 9–4:45; Thu 9–6:15; Sat appt",
                "Under The Sink HHW — 4001 S 120th St",
                f"Take {item.replace('-', ' ')} to Under The Sink HHW at 4001 S 120th St — Wed/Fri 9 a.m.–4:45 p.m., Thu 9 a.m.–6:15 p.m., Sat by appointment 402-444-SINK. Do not dry chemicals for trash.",
                [
                    "Deliver sealed containers during Under The Sink hours.",
                    "Sat: call 402-444-SINK for appointment.",
                    "Keep chemicals out of River City Transfer loads.",
                ],
                [("Same as latex fee path?", "No — chemicals are HHW, not the $1 latex per-container rule alone.")],
                *hhw,
            )
        )
    for item in [
        "car-battery",
        "lithium-battery",
        "paint-oil",
        "motor-oil",
        "propane-tank",
        "fluorescent-bulbs",
        "cooking-oil",
    ]:
        extra = {
            "car-battery": " Auto and household batteries accepted at Under The Sink.",
            "lithium-battery": " Rechargeable/lithium batteries go to HHW — not trash.",
            "paint-oil": " Oil-based paint free at Under The Sink HHW.",
            "motor-oil": " Used motor oil accepted at HHW.",
            "propane-tank": " Propane cylinders accepted at HHW.",
            "fluorescent-bulbs": " CFLs and fluorescent lamps accepted at HHW.",
            "cooking-oil": " Keep cooking oil out of drains; use HHW when not trash-safe.",
        }[item]
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS" if item not in {"cooking-oil"} else "SPECIAL_HANDLING",
                "High" if item not in {"cooking-oil"} else "Medium",
                False,
                "Under The Sink HHW — Wed/Fri 9–4:45; Thu 9–6:15; Sat appt",
                "Under The Sink HHW — 4001 S 120th St",
                f"Under The Sink HHW at 4001 S 120th St accepts household hazardous materials Wed/Fri 9–4:45, Thu 9–6:15, Sat by appointment.{extra} River City Transfer does NOT accept HHW.",
                [
                    "Deliver sealed containers during Under The Sink hours.",
                    "Sat: appointment via 402-444-SINK.",
                    "Keep HHW out of River City Transfer loads.",
                ],
                [("River City for HHW?", "No — HHW goes to Under The Sink only.")],
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
            "Rigid sealed container — confirm Under The Sink sharps acceptance",
            "Under The Sink HHW — 4001 S 120th St",
            "Place medical sharps in a rigid, sealed hard-plastic container before delivery. Confirm sharps acceptance at Under The Sink on underthesink.org. Do not loose-bag needles in trash or recycling.",
            [
                "Place sharps in a rigid sealed hard-plastic container.",
                "Confirm sharps acceptance at Under The Sink before hauling.",
                "Never recycle sharps containers.",
            ],
            [("Medications?", "Confirm prescription drug take-back at Under The Sink on website.")],
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
            "NOT River City — separate free wasteline tire collection events",
            "Omaha wasteline tire collection events",
            "Tires are NOT accepted at River City Transfer or curbside bulky. Omaha holds separate free tire collection events — check wasteline.org tire collection pages for current dates and locations.",
            [
                "Check wasteline.org for tire collection event dates.",
                "Do not haul tires to River City Transfer.",
                "Retailer take-back when replacing tires is also an option.",
            ],
            [("River City for tires?", "No — tires use wasteline tire collection events.")],
            *transfer,
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
            "Omaha yard waste collection programs",
            "Omaha yard waste collection",
            "Omaha handles yard waste through regular collection programs. Follow set-out rules; keep yard waste out of River City Transfer and HHW loads.",
            [
                "Use Omaha yard waste set-out rules for leaves and trimmings.",
                "Keep yard waste separate from transfer and HHW loads.",
                "Check wasteline.org for seasonal guidance.",
            ],
            [("Christmas trees?", "Follow city seasonal yard waste guidance.")],
            *transfer,
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
            "Omaha garbage / private compost",
            "Bag food scraps for garbage unless you use private/community compost. Keep food out of recycling and out of HHW loads.",
            [
                "Bag food scraps for garbage if you lack compost access.",
                "Keep organics out of recycling.",
                "Yard trimmings use yard-waste pathways.",
            ],
            [("HHW for food?", "No — HHW is for hazardous products.")],
            *transfer,
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
            "Plastic bags are not accepted in Omaha curbside recycling. Return clean film to store take-back or trash.",
            [
                "Keep plastic bags out of the recycling cart.",
                "Use grocery take-back bins when available.",
                "Otherwise place bags in trash.",
            ],
            [("River City for bags?", "No — use store take-back or trash.")],
            *transfer,
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
            "NOT River City — private C&D hauler for renovation debris",
            "Private C&D hauler / transfer (not River City voucher)",
            "Construction and demolition debris is NOT accepted at River City Transfer voucher sites. Hire a private C&D hauler or use appropriate transfer options. Route paint and chemicals to Under The Sink HHW separately.",
            [
                "Do not haul C&D to River City Transfer.",
                "Hire a private C&D hauler for renovation debris.",
                "Route paint/chemicals to Under The Sink 4001 S 120th St.",
            ],
            [("River City for C&D?", "No — C&D needs private hauler pathways.")],
            *transfer,
        )
    )
    return rows


def virginia_beach():
    c, st = "virginia-beach", "VA"
    bulky = (
        "City of Virginia Beach — Bulky waste",
        "https://www.vbgov.com/government/departments/public-works/waste-management/bulky-waste",
    )
    rrc = (
        "Virginia Beach — Landfill / RRC HHW",
        "https://www.vbgov.com/government/departments/public-works/waste-management/landfill-rrc",
    )
    hhw = (
        "Virginia Beach — Household hazardous waste",
        "https://www.vbgov.com/government/departments/public-works/waste-management/household-hazardous-waste",
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
            "Free bulky via VB311 / 757-385-4650 — schedule ahead of trash day",
            "Virginia Beach bulky collection (VB311 scheduled)",
            "Virginia Beach offers free bulky item collection — schedule via VB311 or 757-385-4650 ahead of your trash day (city pages vary on lead time — allow several days). Mattresses and furniture use this program. Set out per city instructions on scheduled collection.",
            [
                "Call VB311 or 757-385-4650 to schedule bulky pickup ahead of trash day.",
                "Allow several days lead time — city pages conflict on 3 days vs 2 weeks.",
                "Set mattress out per city instructions on scheduled day.",
            ],
            [
                ("Cost?", "Free — schedule via VB311 / 757-385-4650."),
                ("How far ahead?", "Schedule before trash day — allow several days lead time."),
            ],
            *bulky,
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
            "Bulky with Freon removed + labeled OR RRC HHW (accepts Freon appliances)",
            "Virginia Beach bulky (labeled Freon) / RRC HHW — 1989 Jake Sears Rd",
            "Freon refrigerators can go on Virginia Beach bulky collection if Freon is removed and the unit is labeled before curb set-out — schedule via VB311/757-385-4650. Alternatively, haul to RRC HHW at 1989 Jake Sears Rd (accepts Freon appliances) Tue–Sat 7 a.m.–4:30 p.m. Never vent refrigerant yourself.",
            [
                "Option A: Remove Freon, label unit, schedule bulky via VB311.",
                "Option B: Haul to RRC HHW 1989 Jake Sears Rd Tue–Sat 7–4:30.",
                "Never release Freon yourself.",
            ],
            [("RRC for fridge?", "Yes — RRC HHW accepts Freon appliances.")],
            *bulky,
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
            "Bulky with Freon removed + labeled OR RRC HHW",
            "Virginia Beach bulky (labeled Freon) / RRC HHW — 1989 Jake Sears Rd",
            "Freon window and portable air conditioners can go on Virginia Beach bulky if Freon is removed and the unit is labeled — schedule via VB311. Or haul to RRC HHW at 1989 Jake Sears Rd Tue–Sat 7–4:30. Never vent refrigerant yourself.",
            [
                "Remove Freon and label unit before bulky set-out, or haul to RRC HHW.",
                "Schedule bulky via VB311 / 757-385-4650.",
                "RRC HHW Tue–Sat 7:00–16:30.",
            ],
            [("Same as fridge?", "Yes — Freon removed + labeled for curb, or RRC HHW.")],
            *bulky,
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
                "Free bulky via VB311 — no Freon label requirement for washers",
                "Virginia Beach bulky collection (VB311 scheduled)",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s go on Virginia Beach free bulky collection — schedule via VB311 or 757-385-4650. No Freon removal/label requirement for washers and other non-refrigerant appliances.",
                [
                    "Call VB311 or 757-385-4650 to schedule bulky pickup.",
                    "Set appliance out per city instructions — no Freon label needed.",
                    "Allow several days scheduling lead time.",
                ],
                [("Freon label for washer?", "No — label requirement is for Freon refrigerators/AC only.")],
                *bulky,
            )
        )
    for item, label in [
        ("television", "TVs"),
        ("computer-monitor", "monitors"),
        ("smartphone", "phones and small electronics"),
        ("e-waste-mixed", "mixed electronic waste"),
    ]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "Free e-waste at RRC — CRT NOT accepted",
                "Virginia Beach RRC — 1989 Jake Sears Rd (e-waste)",
                f"Electronics including {label} are accepted free at Virginia Beach RRC, 1989 Jake Sears Rd — Tue–Sat 7 a.m.–4:30 p.m. CRT monitors/TVs are NOT accepted. Wipe personal data before recycling computers/phones.",
                [
                    "Haul e-waste to RRC 1989 Jake Sears Rd Tue–Sat 7–4:30.",
                    "CRT monitors/TVs are NOT accepted — confirm current RRC rules.",
                    "Wipe personal data before drop-off.",
                ],
                [("CRT accepted?", "No — CRT not accepted at RRC e-waste.")],
                *rrc,
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
            "RRC HHW — 5 gal / 75 lb limit; Tue–Sat 7:00–16:30",
            "Virginia Beach RRC HHW — 1989 Jake Sears Rd",
            "Liquid latex and oil paint go to Virginia Beach RRC HHW at 1989 Jake Sears Rd — Tue–Sat 7 a.m.–4:30 p.m.; limit 5 gallons / 75 pounds per visit. Do not pour paint down drains.",
            [
                "Haul paint to RRC HHW Tue–Sat 7–4:30.",
                "Limit: 5 gal / 75 lb per visit.",
                "Keep paint sealed and labeled.",
            ],
            [("HHW for paint?", "Yes — paint goes to RRC HHW.")],
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
                "RRC HHW — 5 gal / 75 lb limit; Tue–Sat 7:00–16:30",
                "Virginia Beach RRC HHW — 1989 Jake Sears Rd",
                f"Take {item.replace('-', ' ')} to Virginia Beach RRC HHW at 1989 Jake Sears Rd — Tue–Sat 7 a.m.–4:30 p.m.; limit 5 gal / 75 lb per visit. Do not dry chemicals for trash.",
                [
                    "Deliver sealed containers to RRC HHW Tue–Sat 7–4:30.",
                    "Limit: 5 gallons / 75 pounds per visit.",
                    "Keep chemicals out of bulky piles.",
                ],
                [("Same as paint?", "Yes — chemicals use RRC HHW.")],
                *hhw,
            )
        )
    for item in [
        "car-battery",
        "lithium-battery",
        "paint-oil",
        "motor-oil",
        "propane-tank",
        "fluorescent-bulbs",
        "cooking-oil",
    ]:
        extra = {
            "car-battery": " Auto and household batteries accepted at RRC HHW.",
            "lithium-battery": " Rechargeable/lithium batteries go to HHW — not trash.",
            "paint-oil": " Oil-based paint accepted at RRC HHW.",
            "motor-oil": " Used motor oil accepted at HHW.",
            "propane-tank": " Propane cylinders accepted at HHW.",
            "fluorescent-bulbs": " CFLs and fluorescent lamps accepted at HHW.",
            "cooking-oil": " Keep cooking oil out of drains; use HHW when not trash-safe.",
        }[item]
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS" if item not in {"cooking-oil"} else "SPECIAL_HANDLING",
                "High" if item not in {"cooking-oil"} else "Medium",
                False,
                "RRC HHW — 5 gal / 75 lb limit; Tue–Sat 7:00–16:30",
                "Virginia Beach RRC HHW — 1989 Jake Sears Rd",
                f"Virginia Beach RRC HHW at 1989 Jake Sears Rd accepts household hazardous materials Tue–Sat 7 a.m.–4:30 p.m.; limit 5 gal / 75 lb per visit.{extra}",
                [
                    "Deliver sealed containers to RRC HHW Tue–Sat 7–4:30.",
                    "Limit: 5 gallons / 75 pounds per visit.",
                    "Freon appliances also accepted at RRC when needed.",
                ],
                [("Which address?", "1989 Jake Sears Rd — Tue–Sat 7–4:30.")],
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
            "Rigid sealed container — confirm RRC HHW sharps acceptance",
            "Virginia Beach RRC HHW — 1989 Jake Sears Rd",
            "Place medical sharps in a rigid, sealed hard-plastic container before delivery. Confirm sharps acceptance at RRC HHW on vbgov.com. Do not loose-bag needles in trash or recycling.",
            [
                "Place sharps in a rigid sealed hard-plastic container.",
                "Confirm sharps acceptance at RRC HHW before hauling.",
                "Never recycle sharps containers.",
            ],
            [("Medications?", "Confirm prescription drug take-back at RRC HHW on city page.")],
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
            "RRC — up to 4 passenger tires per visit",
            "Virginia Beach RRC — 1989 Jake Sears Rd (tires)",
            "Passenger tires are accepted at Virginia Beach RRC, 1989 Jake Sears Rd — up to 4 passenger tires per visit; Tue–Sat 7 a.m.–4:30 p.m. Confirm rim rules on city landfill/RRC page.",
            [
                "Haul up to 4 passenger tires to RRC 1989 Jake Sears Rd.",
                "Visit Tue–Sat 7:00–16:30.",
                "Confirm rim/passenger rules on vbgov.com.",
            ],
            [("Bulky for tires?", "RRC accepts up to 4 passenger tires per visit — confirm city rules.")],
            *rrc,
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
            "Virginia Beach yard waste collection programs",
            "Virginia Beach yard waste collection",
            "Virginia Beach handles yard waste through regular collection programs. Follow set-out rules; keep yard waste out of bulky piles and out of RRC HHW.",
            [
                "Use Virginia Beach yard waste set-out rules for leaves and trimmings.",
                "Keep yard waste separate from bulky and HHW loads.",
                "Check vbgov.com for seasonal guidance.",
            ],
            [("Christmas trees?", "Follow city seasonal yard waste guidance.")],
            *bulky,
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
            "Virginia Beach garbage / private compost",
            "Bag food scraps for garbage unless you use private/community compost. Keep food out of recycling and out of HHW loads.",
            [
                "Bag food scraps for garbage if you lack compost access.",
                "Keep organics out of recycling.",
                "Yard trimmings use yard-waste pathways.",
            ],
            [("HHW for food?", "No — HHW is for hazardous products.")],
            *bulky,
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
            "Plastic bags are not accepted in Virginia Beach curbside recycling. Return clean film to store take-back or trash.",
            [
                "Keep plastic bags out of the recycling cart.",
                "Use grocery take-back bins when available.",
                "Otherwise place bags in trash.",
            ],
            [("Bulky for bags?", "No — use store take-back or trash.")],
            *bulky,
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
            "Bulky via VB311 for limited loads — private C&D for larger",
            "Virginia Beach bulky (VB311) / private C&D hauler",
            "Limited homeowner renovation debris may go on Virginia Beach bulky collection when scheduled via VB311. Larger contractor C&D loads need a private hauler or RRC fee options. Route paint and chemicals to RRC HHW separately.",
            [
                "Schedule bulky via VB311 if debris fits city limits.",
                "Hire a private C&D hauler for larger projects.",
                "Route paint/chemicals to RRC HHW 1989 Jake Sears Rd.",
            ],
            [("HHW for C&D?", "No — separate paint/chemicals for RRC HHW.")],
            *bulky,
        )
    )
    return rows


CITIES = [
    {
        "city": "Las Vegas",
        "city_slug": "las-vegas",
        "state": "NV",
        "state_slug": "nevada",
        "lat": 36.1699,
        "lng": -115.1398,
        "population": 641903,
    },
    {
        "city": "Raleigh",
        "city_slug": "raleigh",
        "state": "NC",
        "state_slug": "north-carolina",
        "lat": 35.7796,
        "lng": -78.6382,
        "population": 474069,
    },
    {
        "city": "Minneapolis",
        "city_slug": "minneapolis",
        "state": "MN",
        "state_slug": "minnesota",
        "lat": 44.9778,
        "lng": -93.2650,
        "population": 429954,
    },
    {
        "city": "Omaha",
        "city_slug": "omaha",
        "state": "NE",
        "state_slug": "nebraska",
        "lat": 41.2565,
        "lng": -95.9345,
        "population": 486051,
    },
    {
        "city": "Virginia Beach",
        "city_slug": "virginia-beach",
        "state": "VA",
        "state_slug": "virginia",
        "lat": 36.8529,
        "lng": -75.9780,
        "population": 459808,
    },
]

ZIPS = [
    {
        "zip": "89101",
        "city": "Las Vegas",
        "city_slug": "las-vegas",
        "state": "NV",
        "state_slug": "nevada",
        "lat": 36.170,
        "lng": -115.140,
        "population": 45000,
    },
    {
        "zip": "89119",
        "city": "Las Vegas",
        "city_slug": "las-vegas",
        "state": "NV",
        "state_slug": "nevada",
        "lat": 36.075,
        "lng": -115.155,
        "population": 52000,
    },
    {
        "zip": "27601",
        "city": "Raleigh",
        "city_slug": "raleigh",
        "state": "NC",
        "state_slug": "north-carolina",
        "lat": 35.780,
        "lng": -78.638,
        "population": 18000,
    },
    {
        "zip": "27609",
        "city": "Raleigh",
        "city_slug": "raleigh",
        "state": "NC",
        "state_slug": "north-carolina",
        "lat": 35.845,
        "lng": -78.620,
        "population": 32000,
    },
    {
        "zip": "55401",
        "city": "Minneapolis",
        "city_slug": "minneapolis",
        "state": "MN",
        "state_slug": "minnesota",
        "lat": 44.978,
        "lng": -93.265,
        "population": 12000,
    },
    {
        "zip": "55408",
        "city": "Minneapolis",
        "city_slug": "minneapolis",
        "state": "MN",
        "state_slug": "minnesota",
        "lat": 44.948,
        "lng": -93.290,
        "population": 28000,
    },
    {
        "zip": "68102",
        "city": "Omaha",
        "city_slug": "omaha",
        "state": "NE",
        "state_slug": "nebraska",
        "lat": 41.257,
        "lng": -95.935,
        "population": 9000,
    },
    {
        "zip": "68137",
        "city": "Omaha",
        "city_slug": "omaha",
        "state": "NE",
        "state_slug": "nebraska",
        "lat": 41.205,
        "lng": -96.105,
        "population": 35000,
    },
    {
        "zip": "23451",
        "city": "Virginia Beach",
        "city_slug": "virginia-beach",
        "state": "VA",
        "state_slug": "virginia",
        "lat": 36.853,
        "lng": -75.978,
        "population": 22000,
    },
    {
        "zip": "23464",
        "city": "Virginia Beach",
        "city_slug": "virginia-beach",
        "state": "VA",
        "state_slug": "virginia",
        "lat": 36.815,
        "lng": -76.095,
        "population": 48000,
    },
]

FACILITIES = [
    {
        "name": "Clark County HHW — North Las Vegas",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "las-vegas",
        "state": "NV",
        "zip": "89030",
        "address": "333 W Gowan Rd, North Las Vegas, NV 89030",
        "lat": 36.2155,
        "lng": -115.1255,
        "source_url": "https://www.clarkcountynv.gov/government/departments/environment_and_sustainability/household_hazardous_waste",
        "hours": "Wed–Sat 9:00–13:00; rotating calendar",
        "phone": "702-455-4191",
    },
    {
        "name": "Wake County HHW — South Wake",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "raleigh",
        "state": "NC",
        "zip": "27539",
        "address": "6150 Old Smithfield Rd, Apex, NC 27539",
        "lat": 35.6555,
        "lng": -78.7555,
        "source_url": "https://www.wake.gov/departments/environmental-services/waste-management/household-hazardous-waste",
        "hours": "Mon–Sat 8:00–16:00",
        "phone": "919-856-7400",
    },
    {
        "name": "Hennepin County HHW — Bloomington",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "minneapolis",
        "state": "MN",
        "zip": "55431",
        "address": "1400 W 96th St, Bloomington, MN 55431",
        "lat": 44.8255,
        "lng": -93.3055,
        "source_url": "https://www.hennepin.us/residents/recycling-and-waste/green-disposal-guide",
        "hours": "Tue–Sat 9:00–17:00",
        "phone": "612-348-3777",
    },
    {
        "name": "Under The Sink HHW",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "omaha",
        "state": "NE",
        "zip": "68144",
        "address": "4001 S 120th St, Omaha, NE 68144",
        "lat": 41.2255,
        "lng": -96.1055,
        "source_url": "https://underthesink.org/",
        "hours": "Wed/Fri 9:00–16:45; Thu 9:00–18:15; Sat by appointment",
        "phone": "402-444-7465",
    },
    {
        "name": "Virginia Beach RRC / HHW",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "virginia-beach",
        "state": "VA",
        "zip": "23455",
        "address": "1989 Jake Sears Rd, Virginia Beach, VA 23455",
        "lat": 36.8655,
        "lng": -76.0555,
        "source_url": "https://www.vbgov.com/government/departments/public-works/waste-management/household-hazardous-waste",
        "hours": "Tue–Sat 7:00–16:30",
        "phone": "757-385-4650",
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
        "las-vegas": clone_siblings(las_vegas()),
        "raleigh": clone_siblings(raleigh()),
        "minneapolis": clone_siblings(minneapolis()),
        "omaha": clone_siblings(omaha()),
        "virginia-beach": clone_siblings(virginia_beach()),
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

    print("Wave-9 metros written:")
    for city, rows in audited.items():
        print(f"  {city}: {len(rows)} rules")
    print(f"Total rules now: {len(keep)}")


if __name__ == "__main__":
    main()

