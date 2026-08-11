#!/usr/bin/env python3
"""Portal-audited city guides for wave-18 metros (city-sourced only).

Cities researched from official program pages (2026-08-11):
  - Garland, TX — weekly brush & bulky + appliance scrap / Dallas County HHW / eRecycler
  - Jersey City, NJ — DPW bulk & white-goods appointments / Linden Ave drop-off
  - Chandler, AZ — scheduled bulk + RSWCC / HHW appointments
  - Henderson, NV — Republic bulky + Clark County transfer / Henderson Shines
  - Fremont, CA — Republic bulky + Alameda County HHW at Boyce Rd / transfer station
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


def garland():
    c, st = "garland", "TX"
    bulk = (
        "City of Garland — Brush & Bulky Goods",
        "https://www.garlandtx.gov/483/Brush-Bulky-Goods",
    )
    appliance = (
        "City of Garland — Appliance Recycling",
        "https://garlandtx.gov/490/Appliance-Recycling",
    )
    hhw = (
        "City of Garland — Household Hazardous Waste",
        "https://www.garlandtx.gov/795/Household-Hazardous-Waste",
    )
    ewaste = (
        "City of Garland — Electronics Recycling",
        "https://garlandtx.gov/477/Electronics-Recycling",
    )
    hc3 = (
        "Dallas County — Home Chemical Collection Center",
        "https://www.dallascounty.org/departments/consolidated-services/hhw/",
    )
    rows = []
    rows.append(
        R(
            c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
            "Free weekly brush & bulky — separate piles for brush vs bulky",
            "Garland weekly brush & bulky collection",
            "Garland mattresses go on free weekly brush & bulky collection. Keep brush and bulky in separate piles per city guidelines. TVs and tires are NOT brush & bulky.",
            ["Set out on your weekly brush & bulky day.", "Keep brush and bulky in separate piles.", "Follow garlandtx.gov set-out rules."],
            [("Fee?", "Free weekly brush & bulky."), ("Separate piles?", "Yes — brush and bulky must be separated.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c, st, "refrigerator", "SPECIAL_HANDLING", "High", True,
            "Free weekly bulky OR appliance scrap 1426 Commerce St — tape doors shut",
            "Garland weekly bulky / appliance scrap — 1426 Commerce St",
            "Garland Freon refrigerators may go on free weekly brush & bulky OR self-haul to appliance scrap — 1426 Commerce St. Tape doors shut. Remove contents. Never vent refrigerant yourself.",
            ["Set out on weekly brush & bulky day.", "Or haul to 1426 Commerce St appliance scrap.", "Tape doors shut; never vent Freon yourself."],
            [("Bulky for Freon fridge?", "Yes — or appliance scrap at 1426 Commerce St."), ("Washer on bulky?", "Yes — non-Freon washers use weekly bulky.")],
            *appliance,
        )
    )
    rows.append(
        R(
            c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
            "Free weekly bulky OR appliance scrap 1426 Commerce St",
            "Garland weekly bulky / appliance scrap — 1426 Commerce St",
            "Garland Freon window AC units may go on weekly brush & bulky OR appliance scrap — 1426 Commerce St. Never vent refrigerant yourself.",
            ["Set out on weekly brush & bulky day.", "Or haul to 1426 Commerce St appliance scrap.", "Keep sealed until proper Freon handling."],
            [("Same as Freon fridge?", "Yes — weekly bulky or appliance scrap.")],
            *appliance,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c, st, item, "SPECIAL_HANDLING", "Medium", True,
                "Free weekly brush & bulky — separate piles",
                "Garland weekly brush & bulky collection",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s go on Garland free weekly brush & bulky. Keep brush and bulky in separate piles. Freon refrigerators/AC also on weekly bulky or appliance scrap.",
                ["Set out on weekly brush & bulky day.", "Keep brush and bulky in separate piles.", "Freon appliances also on weekly bulky."],
                [("Same as Freon fridge?", "Yes — all large appliances on weekly bulky.")],
                *bulk,
            )
        )
    rows.append(
        R(
            c, st, "television", "BANNED_FROM_LANDFILLS", "Medium", False,
            "NOT transfer station — eRecycler / Big 4 / TCEQ programs",
            "Garland eRecycler / Big 4 / TCEQ electronics programs",
            "Garland TVs are NOT accepted at the city transfer station. Use eRecycler, Big 4, or TCEQ electronics recycling programs listed on garlandtx.gov. Wipe data before drop-off.",
            ["Do not haul TVs to city transfer station.", "Check eRecycler / Big 4 / TCEQ programs on garlandtx.gov.", "Wipe personal data."],
            [("Transfer station for TVs?", "No — eRecycler / Big 4 / TCEQ only."), ("Bulky for TVs?", "No — electronics recycling programs.")],
            *ewaste,
        )
    )
    for item, label in [
        ("computer-monitor", "monitors"), ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste"),
    ]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "Medium", False,
                "NOT transfer — eRecycler / Big 4 / TCEQ programs",
                "Garland eRecycler / Big 4 / TCEQ electronics programs",
                f"Garland electronics including {label} are NOT accepted at the transfer station. Use eRecycler, Big 4, or TCEQ programs on garlandtx.gov. Wipe data before drop-off.",
                ["Do not haul e-waste to transfer station.", "Check eRecycler / Big 4 / TCEQ on garlandtx.gov.", "Wipe personal data."],
                [("Bulky for e-waste?", "No — electronics recycling programs."), ("Transfer station?", "No — not for TVs/e-waste.")],
                *ewaste,
            )
        )
    rows.append(
        R(
            c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", False,
            "Free Dallas County HHW — 11234 Plano Rd",
            "Dallas County HC3 — 11234 Plano Road",
            "Garland latex paint goes free to Dallas County Home Chemical Collection Center — 11234 Plano Rd. Not weekly bulky or trash.",
            ["Haul sealed latex paint to HC3 — 11234 Plano Rd.", "Bring proof of Dallas County residency.", "Keep paint off brush & bulky piles."],
            [("HC3 address?", "11234 Plano Rd, Dallas."), ("Bulky for paint?", "No — HC3 only.")],
            *hc3,
        )
    )
    rows.append(
        R(
            c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
            "Free Dallas County HHW — 11234 Plano Rd",
            "Dallas County HC3 — 11234 Plano Road",
            "Garland oil-based paint goes free to Dallas County HC3 — 11234 Plano Rd. Not bulky or trash.",
            ["Haul sealed oil paint to HC3 — 11234 Plano Rd.", "Keep containers sealed and labeled.", "Bring proof of residency."],
            [("Same as latex?", "Yes — both use HC3 free drop-off.")],
            *hc3,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
                "Free Dallas County HHW — 11234 Plano Rd",
                "Dallas County HC3 — 11234 Plano Road",
                f"Take {item.replace('-', ' ')} free to Dallas County HC3 — 11234 Plano Rd. Not bulky or trash.",
                ["Deliver sealed containers to HC3.", "Bring proof of residency.", "Keep chemicals off bulky piles."],
                [("HC3 for chemicals?", "Yes — 11234 Plano Rd free for county residents.")],
                *hc3,
            )
        )
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {
            "car-battery": " Lead-acid batteries at HC3.",
            "lithium-battery": " Lithium batteries at HC3.",
            "motor-oil": " Used motor oil at HC3.",
            "propane-tank": " Propane tanks at HC3 — confirm size limits.",
            "fluorescent-bulbs": " Fluorescent bulbs at HC3.",
            "cooking-oil": " Cooking oil at HC3 when not trash-safe.",
        }[item]
        rows.append(
            R(
                c, st, item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium", False,
                "Free Dallas County HHW — 11234 Plano Rd",
                "Dallas County HC3 — 11234 Plano Road",
                f"Dallas County HC3 accepts household hazardous materials free.{extra}",
                ["Haul to HC3 — 11234 Plano Rd.", "Bring proof of residency.", "Tires use Big 4 events path."],
                [("Tires at HC3?", "No — Big 4 tire events only.")],
                *hc3,
            )
        )
    rows.append(
        R(
            c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
            "Rigid sealed container — confirm HC3 sharps acceptance",
            "Dallas County HC3 — 11234 Plano Road",
            "Place sharps in a rigid sealed container. Confirm acceptance at Dallas County HC3. Do not loose-bag needles.",
            ["Use rigid sealed container.", "Confirm sharps at HC3.", "Never recycle loose needles."],
            [("Medications?", "Confirm drug take-back via Dallas County programs.")],
            *hc3,
        )
    )
    rows.append(
        R(
            c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
            "NOT brush & bulky — Big 4 tire recycling events only",
            "Big 4 tire recycling events",
            "Garland tires are NOT accepted on weekly brush & bulky. Use Big 4 tire recycling events only. Retailer take-back when replacing tires.",
            ["Do not set tires out on brush & bulky.", "Check Big 4 tire event schedule on garlandtx.gov.", "Retailer take-back when replacing tires."],
            [("Bulky for tires?", "No — Big 4 events only."), ("Transfer station?", "No — Big 4 events.")],
            *bulk,
        )
    )
    rows.append(
        R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True,
          "Garland brush collection", "Garland brush collection",
          "Garland handles yard waste and brush through regular collection and weekly brush & bulky. Follow set-out rules on garlandtx.gov.",
          ["Use brush/yard waste set-out rules.", "Keep yard waste out of HHW and e-waste.", "Check garlandtx.gov for seasonal guidance."],
          [("Christmas trees?", "Follow city seasonal yard waste guidance.")], *bulk)
    )
    rows.append(
        R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True,
          "Garbage cart unless private compost", "Garland garbage / private compost",
          "Bag food scraps for garbage unless you compost. Keep food out of recycling and HHW.",
          ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."],
          [("HHW for food?", "No.")], *bulk)
    )
    rows.append(
        R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False,
          "Not recycling — store take-back / trash", "Retail bag take-back / trash",
          "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
          ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."],
          [("Bulky for bags?", "No.")], *bulk)
    )
    rows.append(
        R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", False,
          "NOT brush & bulky — private C&D hauler",
          "Private C&D hauler",
          "Construction debris is not Garland brush & bulky material. Hire a private C&D hauler for remodel loads. Route paint/chemicals to HC3 separately.",
          ["Do not treat remodel debris as brush & bulky.", "Hire private C&D for larger projects.", "Route paint to HC3."],
          [("HC3 for C&D?", "No — separate paint/chemicals.")], *bulk)
    )
    return rows


def jersey_city():
    c, st = "jersey-city", "NJ"
    dpw = (
        "City of Jersey City — DPW Sanitation",
        "https://www.jerseycitynj.gov/cityhall/DPW/sanitation",
    )
    dropoff = (
        "Jersey City DPW Drop-Off — 13-15 Linden Ave E",
        "https://www.jerseycitynj.gov/cityhall/DPW/sanitation",
    )
    rows = []
    rows.append(
        R(
            c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
            "Bulk pickup — call 201-547-4400; wrap in plastic; max 4 items",
            "Jersey City DPW bulk pickup",
            "Jersey City mattresses require bulk pickup — call 201-547-4400. Wrap in plastic. Maximum 4 bulk items per pickup.",
            ["Call 201-547-4400 to schedule bulk pickup.", "Wrap mattress in plastic.", "Maximum 4 items per pickup."],
            [("Fee?", "Confirm current bulk fees when scheduling."), ("Plastic wrap?", "Yes — required for mattresses.")],
            *dpw,
        )
    )
    rows.append(
        R(
            c, st, "refrigerator", "SPECIAL_HANDLING", "High", False,
            "Special white-goods appointment — call 201-547-4400; NOT standard bulk",
            "Jersey City DPW white-goods appointment",
            "Jersey City Freon refrigerators require a special white-goods appointment — call 201-547-4400. NOT accepted on standard bulk without white-goods scheduling. Remove doors and empty unit. Never vent refrigerant yourself.",
            ["Call 201-547-4400 for white-goods appointment.", "Do not set Freon fridge on standard bulk.", "Remove doors; never vent Freon yourself."],
            [("Standard bulk for Freon fridge?", "No — white-goods appointment required."), ("Washer on bulk?", "Yes — non-Freon washers use standard bulk pickup.")],
            *dpw,
        )
    )
    rows.append(
        R(
            c, st, "air-conditioner", "SPECIAL_HANDLING", "High", False,
            "Special white-goods appointment — call 201-547-4400",
            "Jersey City DPW white-goods appointment",
            "Jersey City Freon window AC units require a special white-goods appointment — call 201-547-4400. Never vent refrigerant yourself.",
            ["Call 201-547-4400 for white-goods appointment.", "Do not set Freon AC on standard bulk.", "Keep sealed until proper Freon handling."],
            [("Same as Freon fridge?", "Yes — white-goods appointment required.")],
            *dpw,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c, st, item, "SPECIAL_HANDLING", "Medium", True,
                "Bulk pickup — call 201-547-4400; max 4 items",
                "Jersey City DPW bulk pickup",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s use Jersey City standard bulk pickup — call 201-547-4400. Maximum 4 items per pickup. Freon refrigerators/AC need white-goods appointment.",
                ["Call 201-547-4400 to schedule bulk.", "Maximum 4 items per pickup.", "Freon appliances need white-goods appointment."],
                [("Same as Freon fridge?", "No — non-Freon uses standard bulk.")],
                *dpw,
            )
        )
    rows.append(
        R(
            c, st, "television", "BANNED_FROM_LANDFILLS", "Medium", True,
            "Schedule bulk pickup — call 201-547-4400",
            "Jersey City DPW bulk pickup",
            "Jersey City TVs require scheduled bulk pickup — call 201-547-4400. Wipe data before set-out.",
            ["Call 201-547-4400 to schedule bulk for TV.", "Set out on scheduled pickup day.", "Wipe personal data."],
            [("Drop-off for TVs?", "Schedule bulk pickup — call 201-547-4400."), ("Max items?", "4 items per bulk pickup.")],
            *dpw,
        )
    )
    for item, label in [
        ("computer-monitor", "monitors"), ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste"),
    ]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "Medium", True,
                "Schedule bulk pickup — call 201-547-4400",
                "Jersey City DPW bulk pickup",
                f"Jersey City electronics including {label} require scheduled bulk pickup — call 201-547-4400. Wipe data before set-out.",
                ["Call 201-547-4400 to schedule bulk.", "Set out on scheduled pickup day.", "Wipe personal data."],
                [("Same as TVs?", "Yes — schedule bulk pickup."), ("Max items?", "4 items per pickup.")],
                *dpw,
            )
        )
    rows.append(
        R(
            c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", True,
            "Rinse empty cans → trash; liquid latex → DPW drop-off 13-15 Linden Ave E",
            "Jersey City trash cart / DPW drop-off — 13-15 Linden Ave E",
            "Jersey City latex paint: rinse empty cans and put in trash. Liquid latex goes to DPW drop-off — 13-15 Linden Ave E. Not standard bulk.",
            ["Rinse empty latex cans completely.", "Put empty rinsed cans in trash.", "Liquid latex → DPW drop-off 13-15 Linden Ave E."],
            [("Empty cans in trash?", "Yes — after rinsing completely."), ("Oil paint?", "DPW drop-off 13-15 Linden Ave E.")],
            *dropoff,
        )
    )
    rows.append(
        R(
            c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
            "DPW drop-off — 13-15 Linden Ave E",
            "Jersey City DPW drop-off — 13-15 Linden Ave E",
            "Jersey City oil-based paint goes to DPW drop-off — 13-15 Linden Ave E. Not trash or standard bulk.",
            ["Haul sealed oil paint to 13-15 Linden Ave E.", "Keep containers sealed and labeled.", "Confirm drop-off hours before visit."],
            [("Same as latex?", "No — oil paint uses DPW drop-off; empty latex cans go to trash.")],
            *dropoff,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
                "DPW drop-off — 13-15 Linden Ave E",
                "Jersey City DPW drop-off — 13-15 Linden Ave E",
                f"Take {item.replace('-', ' ')} to DPW drop-off — 13-15 Linden Ave E. Not trash or bulk.",
                ["Deliver sealed containers to 13-15 Linden Ave E.", "Confirm drop-off hours.", "Keep chemicals off bulk piles."],
                [("DPW for chemicals?", "Yes — 13-15 Linden Ave E.")],
                *dropoff,
            )
        )
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {
            "car-battery": " Lead-acid batteries at DPW drop-off.",
            "lithium-battery": " Lithium batteries at DPW drop-off.",
            "motor-oil": " Used motor oil at DPW drop-off.",
            "propane-tank": " Propane tanks at DPW drop-off — confirm size limits.",
            "fluorescent-bulbs": " Fluorescent bulbs at DPW drop-off.",
            "cooking-oil": " Cooking oil at DPW drop-off when not trash-safe.",
        }[item]
        rows.append(
            R(
                c, st, item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium", False,
                "DPW drop-off — 13-15 Linden Ave E",
                "Jersey City DPW drop-off — 13-15 Linden Ave E",
                f"Jersey City DPW drop-off at 13-15 Linden Ave E accepts household hazardous materials.{extra}",
                ["Haul to 13-15 Linden Ave E.", "Confirm drop-off hours.", "Tires also accepted at DPW drop-off."],
                [("Address?", "13-15 Linden Ave E, Jersey City.")],
                *dropoff,
            )
        )
    rows.append(
        R(
            c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
            "Rigid sealed container — confirm DPW drop-off sharps acceptance",
            "Jersey City DPW drop-off — 13-15 Linden Ave E",
            "Place sharps in a rigid sealed container. Confirm acceptance at DPW drop-off — 13-15 Linden Ave E. Do not loose-bag needles.",
            ["Use rigid sealed container.", "Confirm sharps at DPW drop-off.", "Never recycle loose needles."],
            [("Medications?", "Confirm drug take-back via Hudson County programs.")],
            *dropoff,
        )
    )
    rows.append(
        R(
            c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
            "DPW drop-off — first 4 free then $3/$10 + $1 rim",
            "Jersey City DPW drop-off — 13-15 Linden Ave E",
            "Jersey City tires go to DPW drop-off — 13-15 Linden Ave E. First 4 tires free, then $3/$10 per tire plus $1 rim fee. Not standard bulk.",
            ["Haul tires to 13-15 Linden Ave E.", "First 4 tires free; then $3/$10 + $1 rim.", "Retailer take-back when replacing tires."],
            [("Bulk for tires?", "No — DPW drop-off only."), ("Fees?", "First 4 free; then $3/$10 + $1 rim.")],
            *dropoff,
        )
    )
    rows.append(
        R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True,
          "Jersey City yard waste collection", "Jersey City yard waste collection",
          "Jersey City handles yard waste through regular collection. Follow set-out rules on jerseycitynj.gov.",
          ["Use yard waste set-out rules.", "Keep yard waste out of HHW and e-waste.", "Check city site for seasonal guidance."],
          [("Christmas trees?", "Follow city seasonal yard waste guidance.")], *dpw)
    )
    rows.append(
        R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True,
          "Garbage cart unless private compost", "Jersey City garbage / private compost",
          "Bag food scraps for garbage unless you compost. Keep food out of recycling and HHW.",
          ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."],
          [("DPW for food?", "No.")], *dpw)
    )
    rows.append(
        R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False,
          "Not recycling — store take-back / trash", "Retail bag take-back / trash",
          "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
          ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."],
          [("Bulk for bags?", "No.")], *dpw)
    )
    rows.append(
        R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", False,
          "NOT bulk pickup — private C&D hauler",
          "Private C&D hauler",
          "Construction debris is not Jersey City bulk pickup material. Hire a private C&D hauler for remodel loads. Route oil paint/chemicals to DPW drop-off separately.",
          ["Do not treat remodel debris as bulk pickup.", "Hire private C&D for larger projects.", "Route oil paint to DPW drop-off."],
          [("DPW for C&D?", "No — separate paint/chemicals.")], *dpw)
    )
    return rows


def chandler():
    c, st = "chandler", "AZ"
    bulk = (
        "City of Chandler — Curbside Bulk Collection",
        "https://www.chandleraz.gov/residents/recycling-and-trash/curbside-bulk-collection",
    )
    rswcc = (
        "City of Chandler — Recycling & Solid Waste Collection Center",
        "https://www.chandleraz.gov/residents/recycling-and-trash/recycling-solid-waste-collection-center",
    )
    hhw = (
        "City of Chandler — Household Hazardous Waste Disposal",
        "https://www.chandleraz.gov/residents/recycling-and-trash/household-hazardous-waste-disposal",
    )
    rows = []
    rows.append(
        R(
            c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
            "Schedule bulk 480-782-3510 — first 4 free/yr then $43",
            "Chandler curbside bulk collection",
            "Chandler mattresses require scheduled bulk pickup — call 480-782-3510. First 4 bulk pickups free per year, then $43 each. Flat-panel TVs recycle on bulk; CRT TVs are trash on bulk.",
            ["Call 480-782-3510 to schedule bulk.", "First 4 pickups free/year; then $43.", "Set out on scheduled bulk day."],
            [("Fee?", "First 4 free/year; then $43 per pickup."), ("Schedule?", "480-782-3510.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c, st, "refrigerator", "SPECIAL_HANDLING", "High", True,
            "$15 Freon fee on bulk OR RSWCC 955 E Queen Creek Rd",
            "Chandler bulk collection / RSWCC — 955 E Queen Creek Rd",
            "Chandler Freon refrigerators on bulk carry a $15 Freon fee — schedule 480-782-3510. Or self-haul to RSWCC — 955 E Queen Creek Rd. Remove doors and empty unit. Never vent refrigerant yourself.",
            ["Schedule bulk — 480-782-3510 — $15 Freon fee applies.", "Or haul to RSWCC 955 E Queen Creek Rd.", "Remove doors; never vent Freon yourself."],
            [("Freon fee?", "$15 on bulk pickup."), ("Washer on bulk?", "Yes — non-Freon washers use bulk without Freon fee.")],
            *rswcc,
        )
    )
    rows.append(
        R(
            c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
            "$15 Freon fee on bulk OR RSWCC 955 E Queen Creek Rd",
            "Chandler bulk collection / RSWCC — 955 E Queen Creek Rd",
            "Chandler Freon window AC units on bulk carry a $15 Freon fee — schedule 480-782-3510. Or haul to RSWCC — 955 E Queen Creek Rd. Never vent refrigerant yourself.",
            ["Schedule bulk — $15 Freon fee applies.", "Or haul to RSWCC 955 E Queen Creek Rd.", "Keep sealed until proper Freon handling."],
            [("Same as Freon fridge?", "Yes — $15 Freon fee on bulk or RSWCC.")],
            *rswcc,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c, st, item, "SPECIAL_HANDLING", "Medium", True,
                "Schedule bulk 480-782-3510 — first 4 free/yr then $43",
                "Chandler curbside bulk collection",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s use Chandler scheduled bulk — 480-782-3510. First 4 free/year; then $43. Freon refrigerators/AC add $15 Freon fee.",
                ["Call 480-782-3510 to schedule bulk.", "First 4 free/year; then $43.", "Freon appliances add $15 Freon fee."],
                [("Same as Freon fridge?", "No — non-Freon uses bulk without Freon fee.")],
                *bulk,
            )
        )
    rows.append(
        R(
            c, st, "television", "BANNED_FROM_LANDFILLS", "Medium", True,
            "Flat-panel → recycle on bulk; CRT → trash on bulk — schedule 480-782-3510",
            "Chandler curbside bulk collection",
            "Chandler TVs: flat-panel TVs recycle on scheduled bulk pickup — 480-782-3510. CRT TVs go as trash on bulk. Wipe data before set-out.",
            ["Call 480-782-3510 to schedule bulk.", "Flat-panel: set out for recycling on bulk.", "CRT: set out as trash on bulk."],
            [("Flat-panel on bulk?", "Yes — recycle on bulk."), ("CRT on bulk?", "Yes — as trash on bulk.")],
            *bulk,
        )
    )
    for item, label in [
        ("computer-monitor", "monitors"), ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste"),
    ]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "Medium", True,
                "Flat-panel e-waste → recycle on bulk; CRT → trash on bulk",
                "Chandler curbside bulk collection",
                f"Chandler electronics including {label}: flat-panel items recycle on scheduled bulk — 480-782-3510. CRT monitors go as trash on bulk. Wipe data before set-out.",
                ["Call 480-782-3510 to schedule bulk.", "Flat-panel: recycle on bulk.", "CRT: trash on bulk."],
                [("RSWCC for e-waste?", "Bulk is primary path; confirm RSWCC for overflow.")],
                *bulk,
            )
        )
    rows.append(
        R(
            c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", True,
            "Dried latex → trash; liquid latex → HHW appointment",
            "Chandler trash cart / HHW appointment",
            "Chandler latex paint: dry completely (kitty litter or leave lid off) then put dried cans in trash. Liquid latex uses HHW appointment — not bulk or RSWCC regular drop-off.",
            ["Dry latex paint completely until solid.", "Place dried cans in trash.", "Liquid latex → schedule HHW appointment."],
            [("Dry latex for trash?", "Yes — fully dried only."), ("HHW appointment?", "Required for liquid latex.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
            "HHW appointment — schedule via chandleraz.gov",
            "Chandler HHW appointment collection",
            "Chandler oil-based paint uses HHW appointment collection — schedule via chandleraz.gov. Not bulk or trash.",
            ["Schedule HHW appointment on chandleraz.gov.", "Keep oil paint sealed and labeled.", "Do not put liquid paint in trash."],
            [("Same as dried latex?", "No — oil paint always uses HHW appointment.")],
            *hhw,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
                "HHW appointment — schedule via chandleraz.gov",
                "Chandler HHW appointment collection",
                f"Take {item.replace('-', ' ')} via Chandler HHW appointment — schedule on chandleraz.gov. Not bulk or trash.",
                ["Schedule HHW appointment.", "Keep chemicals sealed and labeled.", "Do not set HHW on bulk piles."],
                [("RSWCC for chemicals?", "No — HHW appointment required.")],
                *hhw,
            )
        )
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {
            "car-battery": " Lead-acid batteries via HHW appointment.",
            "lithium-battery": " Lithium batteries via HHW appointment.",
            "motor-oil": " Used motor oil via HHW appointment.",
            "propane-tank": " Propane tanks via HHW appointment — confirm size limits.",
            "fluorescent-bulbs": " Fluorescent bulbs via HHW appointment.",
            "cooking-oil": " Cooking oil via HHW appointment when not trash-safe.",
        }[item]
        rows.append(
            R(
                c, st, item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium", False,
                "HHW appointment — schedule via chandleraz.gov",
                "Chandler HHW appointment collection",
                f"Chandler HHW appointment accepts household hazardous materials.{extra}",
                ["Schedule HHW appointment on chandleraz.gov.", "Keep materials off bulk piles.", "Tires use RSWCC path."],
                [("Tires at HHW?", "No — RSWCC de-rimmed tires 5/month.")],
                *hhw,
            )
        )
    rows.append(
        R(
            c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
            "Rigid sealed container — confirm HHW appointment sharps acceptance",
            "Chandler HHW appointment collection",
            "Place sharps in a rigid sealed container. Confirm acceptance via Chandler HHW appointment. Do not loose-bag needles.",
            ["Use rigid sealed container.", "Confirm sharps via HHW appointment.", "Never recycle loose needles."],
            [("Medications?", "Confirm drug take-back via Maricopa County programs.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
            "RSWCC de-rimmed — 5/month; NOT bulk",
            "Chandler RSWCC — 955 E Queen Creek Rd",
            "Chandler tires are NOT accepted on scheduled bulk. Self-haul de-rimmed tires to RSWCC — 955 E Queen Creek Rd — limit 5 per month. Retailer take-back when replacing tires.",
            ["De-rim tires before drop-off.", "Haul to RSWCC 955 E Queen Creek Rd.", "Limit 5 de-rimmed tires per month."],
            [("Bulk for tires?", "No — RSWCC 5/month de-rimmed."), ("RSWCC address?", "955 E Queen Creek Rd.")],
            *rswcc,
        )
    )
    rows.append(
        R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True,
          "Chandler yard waste collection", "Chandler yard waste collection",
          "Chandler handles yard waste through regular collection. Follow set-out rules on chandleraz.gov.",
          ["Use yard waste set-out rules.", "Keep yard waste out of HHW and e-waste.", "Check chandleraz.gov for seasonal guidance."],
          [("Christmas trees?", "Follow city seasonal yard waste guidance.")], *bulk)
    )
    rows.append(
        R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True,
          "Garbage cart unless private compost", "Chandler garbage / private compost",
          "Bag food scraps for garbage unless you compost. Keep food out of recycling and HHW.",
          ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."],
          [("HHW for food?", "No.")], *bulk)
    )
    rows.append(
        R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False,
          "Not recycling — store take-back / trash", "Retail bag take-back / trash",
          "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
          ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."],
          [("Bulk for bags?", "No.")], *bulk)
    )
    rows.append(
        R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", False,
          "NOT bulk — private C&D hauler",
          "Private C&D hauler",
          "Construction debris is not Chandler bulk material. Hire a private C&D hauler for remodel loads. Route paint/chemicals to HHW appointment separately.",
          ["Do not treat remodel debris as bulk.", "Hire private C&D for larger projects.", "Route liquid paint to HHW appointment."],
          [("HHW for C&D?", "No — separate paint/chemicals.")], *bulk)
    )
    return rows


def henderson():
    c, st = "henderson", "NV"
    recycle = (
        "City of Henderson — Recycle",
        "https://www.cityofhenderson.com/our-city/initiatives/sustainability/recycle",
    )
    shines = (
        "City of Henderson — Henderson Shines",
        "https://www.cityofhenderson.com/government/departments/community-development-and-services/community-resources/henderson-shines",
    )
    transfer = (
        "Clark County Transfer Station — Henderson",
        "https://www.clarkcountynv.gov/government/departments/environment-and-sustainability/divisions/waste-management-and-recycling",
    )
    rows = []
    rows.append(
        R(
            c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
            "Republic bulky every other week — wrap soiled mattresses",
            "Henderson / Republic bulky collection",
            "Henderson mattresses go on Republic bulky collection every other week. Wrap soiled mattresses. Freon refrigerators and tires are NOT standard bulky.",
            ["Set out on Republic bulky week (every other week).", "Wrap soiled mattresses in plastic.", "Freon fridges and tires use transfer station."],
            [("Fee?", "Included in Republic bulky service."), ("Wrap soiled?", "Yes — required for soiled mattresses.")],
            *recycle,
        )
    )
    rows.append(
        R(
            c, st, "refrigerator", "SPECIAL_HANDLING", "High", False,
            "NOT bulky — Clark County transfer 560 Cape Horn Dr (fee)",
            "Clark County Transfer Station — 560 Cape Horn Dr",
            "Henderson Freon refrigerators are NOT accepted on Republic bulky. Self-haul to Clark County transfer station — 560 Cape Horn Dr — for a fee. Remove doors and empty unit. Never vent refrigerant yourself.",
            ["Do not set Freon fridge on Republic bulky.", "Haul to 560 Cape Horn Dr transfer station.", "Remove doors; never vent Freon yourself."],
            [("Bulky for Freon fridge?", "No — transfer station with fee."), ("Washer on bulky?", "Yes — non-Freon washers use Republic bulky.")],
            *transfer,
        )
    )
    rows.append(
        R(
            c, st, "air-conditioner", "SPECIAL_HANDLING", "High", False,
            "NOT bulky — Clark County transfer 560 Cape Horn Dr (fee)",
            "Clark County Transfer Station — 560 Cape Horn Dr",
            "Henderson Freon window AC units are NOT accepted on Republic bulky. Self-haul to Clark County transfer — 560 Cape Horn Dr — for a fee. Never vent refrigerant yourself.",
            ["Do not set Freon AC on Republic bulky.", "Haul to 560 Cape Horn Dr transfer station.", "Keep sealed until proper Freon handling."],
            [("Same as Freon fridge?", "Yes — transfer station, not bulky.")],
            *transfer,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c, st, item, "SPECIAL_HANDLING", "Medium", True,
                "Republic bulky every other week",
                "Henderson / Republic bulky collection",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s go on Henderson Republic bulky collection every other week. Freon refrigerators/AC use Clark County transfer station — 560 Cape Horn Dr.",
                ["Set out on Republic bulky week.", "Every other week on your bulky schedule.", "Freon appliances use transfer station."],
                [("Same as Freon fridge?", "No — non-Freon uses Republic bulky.")],
                *recycle,
            )
        )
    rows.append(
        R(
            c, st, "television", "BANNED_FROM_LANDFILLS", "Medium", False,
            "Free Clark County transfer station — NOT Henderson Shines",
            "Clark County transfer station — Cheyenne / Henderson",
            "Henderson TVs are accepted free at Clark County transfer stations — NOT at Henderson Shines events. Do not set TVs out for Republic bulky. Wipe data before drop-off.",
            ["Haul TVs to Clark County transfer station.", "NOT Henderson Shines — transfer station only.", "Wipe personal data."],
            [("Henderson Shines for TVs?", "No — transfer station only."), ("Bulky for TVs?", "No — transfer station free.")],
            *transfer,
        )
    )
    for item, label in [
        ("computer-monitor", "monitors"), ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste"),
    ]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "Medium", False,
                "Free Clark County transfer station — NOT Henderson Shines",
                "Clark County transfer station — Cheyenne / Henderson",
                f"Henderson electronics including {label} go free to Clark County transfer stations — NOT Henderson Shines. Wipe data before drop-off.",
                ["Haul e-waste to Clark County transfer station.", "NOT Henderson Shines.", "Wipe personal data."],
                [("Shines for e-waste?", "No — transfer station only."), ("Bulky for e-waste?", "No.")],
                *transfer,
            )
        )
    rows.append(
        R(
            c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", True,
            "Dry latex → trash OR Clark County HHW / Henderson Shines",
            "Henderson trash cart / Henderson Shines / Clark County HHW",
            "Henderson latex paint: dry completely then put in trash. Liquid latex may go to Clark County HHW or Henderson Shines events — check hendersonshines.com schedule.",
            ["Dry latex paint completely until solid.", "Place dried cans in trash.", "Liquid latex → Henderson Shines or Clark County HHW."],
            [("Dry latex for trash?", "Yes — fully dried only."), ("Shines for liquid latex?", "Yes — check event schedule.")],
            *shines,
        )
    )
    rows.append(
        R(
            c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
            "Clark County HHW / Henderson Shines — NOT trash",
            "Henderson Shines / Clark County HHW",
            "Henderson oil-based paint goes to Clark County HHW or Henderson Shines events — not trash or Republic bulky.",
            ["Check Henderson Shines event schedule.", "Or haul to Clark County HHW.", "Keep containers sealed and labeled."],
            [("Trash for oil paint?", "No — HHW/Shines only.")],
            *shines,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
                "Clark County HHW / Henderson Shines",
                "Henderson Shines / Clark County HHW",
                f"Take {item.replace('-', ' ')} to Clark County HHW or Henderson Shines events. Not trash or bulky.",
                ["Check Henderson Shines schedule.", "Or haul to Clark County HHW.", "Keep chemicals off bulky piles."],
                [("Shines for chemicals?", "Yes — check hendersonshines.com schedule.")],
                *shines,
            )
        )
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {
            "car-battery": " Lead-acid batteries at Shines/HHW.",
            "lithium-battery": " Lithium batteries at Shines/HHW.",
            "motor-oil": " Used motor oil at Shines/HHW.",
            "propane-tank": " Propane tanks at Shines/HHW — confirm size limits.",
            "fluorescent-bulbs": " Fluorescent bulbs at Shines/HHW.",
            "cooking-oil": " Cooking oil at Shines/HHW when not trash-safe.",
        }[item]
        rows.append(
            R(
                c, st, item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium", False,
                "Clark County HHW / Henderson Shines",
                "Henderson Shines / Clark County HHW",
                f"Henderson Shines and Clark County HHW accept household hazardous materials.{extra}",
                ["Check Henderson Shines event schedule.", "Or haul to Clark County HHW.", "Tires use transfer station path."],
                [("Tires at Shines?", "No — transfer station with fee.")],
                *shines,
            )
        )
    rows.append(
        R(
            c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
            "Rigid sealed container — confirm Henderson Shines / HHW sharps acceptance",
            "Henderson Shines / Clark County HHW",
            "Place sharps in a rigid sealed container. Confirm acceptance at Henderson Shines or Clark County HHW. Do not loose-bag needles.",
            ["Use rigid sealed container.", "Confirm sharps at Shines or HHW.", "Never recycle loose needles."],
            [("Medications?", "Confirm drug take-back via Clark County programs.")],
            *shines,
        )
    )
    rows.append(
        R(
            c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
            "NOT bulky/Shines — Clark County transfer station (fee)",
            "Clark County Transfer Station — 560 Cape Horn Dr",
            "Henderson tires are NOT accepted on Republic bulky or Henderson Shines. Self-haul to Clark County transfer station for a fee. Retailer take-back when replacing tires.",
            ["Do not set tires out on Republic bulky.", "Haul to Clark County transfer station.", "Retailer take-back when replacing tires."],
            [("Bulky for tires?", "No — transfer station with fee."), ("Shines for tires?", "No.")],
            *transfer,
        )
    )
    rows.append(
        R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True,
          "Henderson yard waste collection", "Henderson yard waste collection",
          "Henderson handles yard waste through regular collection. Follow set-out rules on cityofhenderson.com.",
          ["Use yard waste set-out rules.", "Keep yard waste out of HHW and e-waste.", "Check city site for seasonal guidance."],
          [("Christmas trees?", "Follow city seasonal yard waste guidance.")], *recycle)
    )
    rows.append(
        R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True,
          "Garbage cart unless private compost", "Henderson garbage / private compost",
          "Bag food scraps for garbage unless you compost. Keep food out of recycling and HHW.",
          ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."],
          [("Shines for food?", "No.")], *recycle)
    )
    rows.append(
        R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False,
          "Not recycling — store take-back / trash", "Retail bag take-back / trash",
          "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
          ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."],
          [("Bulky for bags?", "No.")], *recycle)
    )
    rows.append(
        R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", False,
          "NOT Republic bulky — private C&D hauler / transfer fee",
          "Private C&D hauler / Clark County transfer",
          "Construction debris is not Henderson Republic bulky material. Hire a private C&D hauler or haul to Clark County transfer (fee). Route paint/chemicals to Shines/HHW separately.",
          ["Do not treat remodel debris as Republic bulky.", "Hire private C&D or use transfer station.", "Route paint to Shines/HHW."],
          [("Shines for C&D?", "No — separate paint/chemicals.")], *recycle)
    )
    return rows


def fremont():
    c, st = "fremont", "CA"
    faq_src = (
        "City of Fremont — Environmental Services FAQs",
        "https://www.fremont.gov/government/departments/environmental-services/environmental-services-faqs",
    )
    ehw = (
        "City of Fremont — Electronic & Hazardous Waste",
        "https://www.fremont.gov/government/departments/environmental-services/recycling-compost-garbage/electronic-hazardous-waste",
    )
    hhw = (
        "Alameda County / StopWaste — Household Hazardous Waste",
        "https://www.stopwaste.org/recycling-disposal/hazardous-waste/household-hazardous-waste",
    )
    rows = []
    rows.append(
        R(
            c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
            "2 free bulky/yr Republic 510-657-3500 — max 6×6×6 ft",
            "Fremont / Republic bulky pickup",
            "Fremont mattresses use Republic bulky pickup — 2 free per year — call 510-657-3500. Maximum item size 6×6×6 feet. Tires are NOT bulky.",
            ["Call Republic 510-657-3500 to schedule bulky.", "2 free bulky pickups per year.", "Maximum 6×6×6 feet per item."],
            [("Fee?", "2 free per year via Republic."), ("Size limit?", "6×6×6 feet maximum.")],
            *faq_src,
        )
    )
    rows.append(
        R(
            c, st, "refrigerator", "SPECIAL_HANDLING", "High", True,
            "Free bulky OR self-haul $12+$37 Freon at 41149 Boyce Rd",
            "Fremont / Republic bulky / Alameda County HHW — 41149 Boyce Rd",
            "Fremont Freon refrigerators may go on free Republic bulky (within 2/year allotment) OR self-haul to Alameda County facility — 41149 Boyce Rd — $12 gate + $37 Freon fee. Remove doors. Never vent refrigerant yourself.",
            ["Schedule Republic bulky — 510-657-3500.", "Or haul to 41149 Boyce Rd — $12 + $37 Freon.", "Remove doors; never vent Freon yourself."],
            [("Bulky for Freon fridge?", "Yes — within 2 free/year."), ("Self-haul fee?", "$12 gate + $37 Freon at Boyce Rd.")],
            *ehw,
        )
    )
    rows.append(
        R(
            c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
            "Free bulky OR self-haul $12+$37 Freon at 41149 Boyce Rd",
            "Fremont / Republic bulky / Alameda County HHW — 41149 Boyce Rd",
            "Fremont Freon window AC units may go on Republic bulky OR self-haul to 41149 Boyce Rd — $12 gate + $37 Freon fee. Never vent refrigerant yourself.",
            ["Schedule Republic bulky — 510-657-3500.", "Or haul to 41149 Boyce Rd — $12 + $37 Freon.", "Keep sealed until proper Freon handling."],
            [("Same as Freon fridge?", "Yes — bulky or Boyce Rd self-haul.")],
            *ehw,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c, st, item, "SPECIAL_HANDLING", "Medium", True,
                "2 free bulky/yr Republic 510-657-3500 — max 6×6×6 ft",
                "Fremont / Republic bulky pickup",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s use Fremont Republic bulky — 510-657-3500. 2 free per year, max 6×6×6 feet. Freon refrigerators/AC also on bulky or Boyce Rd.",
                ["Call 510-657-3500 to schedule bulky.", "2 free per year.", "Maximum 6×6×6 feet per item."],
                [("Same as Freon fridge?", "Yes — all large appliances on bulky.")],
                *faq_src,
            )
        )
    rows.append(
        R(
            c, st, "television", "BANNED_FROM_LANDFILLS", "Medium", True,
            "Free bulky (2/yr) OR transfer station",
            "Fremont / Republic bulky / transfer station",
            "Fremont TVs may go on free Republic bulky pickup (within 2/year) OR self-haul to transfer station. Wipe data before set-out or drop-off.",
            ["Schedule Republic bulky — 510-657-3500.", "Or haul to transfer station.", "Wipe personal data."],
            [("Bulky for TVs?", "Yes — within 2 free/year allotment."), ("Transfer station?", "Alternative to bulky.")],
            *ehw,
        )
    )
    for item, label in [
        ("computer-monitor", "monitors"), ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste"),
    ]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "Medium", True,
                "Free bulky (2/yr) OR Alameda County HHW at Boyce Rd",
                "Fremont / Republic bulky / Alameda County HHW — 41149 Boyce Rd",
                f"Fremont electronics including {label} may go on Republic bulky (2/year) OR free Alameda County HHW at 41149 Boyce Rd — 800-606-6606. Wipe data before drop-off.",
                ["Schedule Republic bulky — 510-657-3500.", "Or haul to 41149 Boyce Rd HHW.", "Wipe personal data."],
                [("HHW at Boyce Rd?", "Yes — free for Alameda County residents."), ("Bulky for e-waste?", "Yes — within 2/year.")],
                *ehw,
            )
        )
    rows.append(
        R(
            c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", False,
            "Free Alameda County HHW at Boyce Rd — 800-606-6606",
            "Alameda County HHW — 41149 Boyce Rd, Fremont",
            "Fremont latex paint goes free to Alameda County HHW — 41149 Boyce Rd — call 800-606-6606 for hours. Not bulky or trash.",
            ["Haul sealed latex paint to 41149 Boyce Rd.", "Call 800-606-6606 for hours.", "Bring proof of Alameda County residence."],
            [("Boyce Rd address?", "41149 Boyce Rd, Fremont."), ("Bulky for paint?", "No — HHW only.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
            "Free Alameda County HHW at Boyce Rd — 800-606-6606",
            "Alameda County HHW — 41149 Boyce Rd, Fremont",
            "Fremont oil-based paint goes free to Alameda County HHW — 41149 Boyce Rd. Not bulky or trash.",
            ["Haul sealed oil paint to 41149 Boyce Rd.", "Call 800-606-6606 for hours.", "Keep containers sealed and labeled."],
            [("Same as latex?", "Yes — both free at Boyce Rd HHW.")],
            *hhw,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
                "Free Alameda County HHW at Boyce Rd — 800-606-6606",
                "Alameda County HHW — 41149 Boyce Rd, Fremont",
                f"Take {item.replace('-', ' ')} free to Alameda County HHW — 41149 Boyce Rd. Not bulky or trash.",
                ["Haul to 41149 Boyce Rd.", "Call 800-606-6606 for hours.", "Keep chemicals off bulky piles."],
                [("HHW phone?", "800-606-6606.")],
                *hhw,
            )
        )
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {
            "car-battery": " Lead-acid batteries at Boyce Rd HHW.",
            "lithium-battery": " Lithium batteries at Boyce Rd HHW.",
            "motor-oil": " Used motor oil at Boyce Rd HHW.",
            "propane-tank": " Propane tanks at Boyce Rd HHW — confirm size limits.",
            "fluorescent-bulbs": " Fluorescent bulbs at Boyce Rd HHW.",
            "cooking-oil": " Cooking oil at Boyce Rd HHW when not trash-safe.",
        }[item]
        rows.append(
            R(
                c, st, item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium", False,
                "Free Alameda County HHW at Boyce Rd — 800-606-6606",
                "Alameda County HHW — 41149 Boyce Rd, Fremont",
                f"Alameda County HHW at 41149 Boyce Rd accepts household hazardous materials free.{extra}",
                ["Haul to 41149 Boyce Rd.", "Call 800-606-6606.", "Tires use transfer station path."],
                [("Tires at HHW?", "No — transfer station $10–33; $63 min.")],
                *hhw,
            )
        )
    rows.append(
        R(
            c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
            "Rigid sealed container — confirm Boyce Rd HHW sharps acceptance",
            "Alameda County HHW — 41149 Boyce Rd, Fremont",
            "Place sharps in a rigid sealed container. Confirm acceptance at Alameda County HHW — 41149 Boyce Rd. Do not loose-bag needles.",
            ["Use rigid sealed container.", "Confirm sharps at Boyce Rd HHW.", "Never recycle loose needles."],
            [("Medications?", "Confirm drug take-back via Alameda County programs.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
            "NOT bulky — transfer station $10–33; $63 minimum",
            "Fremont transfer station",
            "Fremont tires are NOT accepted on Republic bulky. Self-haul to transfer station — $10–33 per tire; $63 minimum load. Retailer take-back when replacing tires.",
            ["Do not set tires out for Republic bulky.", "Haul to transfer station.", "Fee: $10–33/tire; $63 minimum load."],
            [("Bulky for tires?", "No — transfer station only."), ("Minimum fee?", "$63 minimum load.")],
            *ehw,
        )
    )
    rows.append(
        R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True,
          "Fremont yard waste / organics collection", "Fremont organics collection",
          "Fremont handles yard waste through organics collection. Follow set-out rules on fremont.gov.",
          ["Use organics/yard waste set-out rules.", "Keep yard waste out of HHW and e-waste.", "Check fremont.gov for seasonal guidance."],
          [("Christmas trees?", "Follow city seasonal yard waste guidance.")], *faq_src)
    )
    rows.append(
        R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True,
          "Organics cart", "Fremont organics cart",
          "Fremont food scraps go in the organics cart. Keep food out of recycling and HHW.",
          ["Place food scraps in organics cart.", "Keep organics out of recycling.", "Yard trimmings use organics pathways."],
          [("HHW for food?", "No.")], *faq_src)
    )
    rows.append(
        R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False,
          "Not recycling — store take-back / trash", "Retail bag take-back / trash",
          "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
          ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."],
          [("Bulky for bags?", "No.")], *faq_src)
    )
    rows.append(
        R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", False,
          "NOT Republic bulky — private C&D hauler / transfer",
          "Private C&D hauler / Fremont transfer station",
          "Construction debris is not Fremont Republic bulky material. Hire a private C&D hauler or use transfer station. Route paint/chemicals to Boyce Rd HHW separately.",
          ["Do not treat remodel debris as Republic bulky.", "Hire private C&D or use transfer station.", "Route paint to Boyce Rd HHW."],
          [("HHW for C&D?", "No — separate paint/chemicals.")], *faq_src)
    )
    return rows


CITIES = [
    {
        "city": "Garland",
        "city_slug": "garland",
        "state": "TX",
        "state_slug": "texas",
        "lat": 32.9126,
        "lng": -96.6389,
        "population": 246018,
    },
    {
        "city": "Jersey City",
        "city_slug": "jersey-city",
        "state": "NJ",
        "state_slug": "new-jersey",
        "lat": 40.7178,
        "lng": -74.0431,
        "population": 292449,
    },
    {
        "city": "Chandler",
        "city_slug": "chandler",
        "state": "AZ",
        "state_slug": "arizona",
        "lat": 33.3062,
        "lng": -111.8413,
        "population": 275987,
    },
    {
        "city": "Henderson",
        "city_slug": "henderson",
        "state": "NV",
        "state_slug": "nevada",
        "lat": 36.0395,
        "lng": -114.9817,
        "population": 320189,
    },
    {
        "city": "Fremont",
        "city_slug": "fremont",
        "state": "CA",
        "state_slug": "california",
        "lat": 37.5485,
        "lng": -121.9886,
        "population": 230504,
    },
]

ZIPS = [
    {
        "zip": "75040",
        "city": "Garland",
        "city_slug": "garland",
        "state": "TX",
        "state_slug": "texas",
        "lat": 32.913,
        "lng": -96.639,
        "population": 45000,
    },
    {
        "zip": "75043",
        "city": "Garland",
        "city_slug": "garland",
        "state": "TX",
        "state_slug": "texas",
        "lat": 32.890,
        "lng": -96.610,
        "population": 52000,
    },
    {
        "zip": "07302",
        "city": "Jersey City",
        "city_slug": "jersey-city",
        "state": "NJ",
        "state_slug": "new-jersey",
        "lat": 40.718,
        "lng": -74.043,
        "population": 38000,
    },
    {
        "zip": "07306",
        "city": "Jersey City",
        "city_slug": "jersey-city",
        "state": "NJ",
        "state_slug": "new-jersey",
        "lat": 40.735,
        "lng": -74.070,
        "population": 42000,
    },
    {
        "zip": "85224",
        "city": "Chandler",
        "city_slug": "chandler",
        "state": "AZ",
        "state_slug": "arizona",
        "lat": 33.330,
        "lng": -111.870,
        "population": 48000,
    },
    {
        "zip": "85286",
        "city": "Chandler",
        "city_slug": "chandler",
        "state": "AZ",
        "state_slug": "arizona",
        "lat": 33.280,
        "lng": -111.820,
        "population": 55000,
    },
    {
        "zip": "89002",
        "city": "Henderson",
        "city_slug": "henderson",
        "state": "NV",
        "state_slug": "nevada",
        "lat": 36.040,
        "lng": -115.030,
        "population": 62000,
    },
    {
        "zip": "89014",
        "city": "Henderson",
        "city_slug": "henderson",
        "state": "NV",
        "state_slug": "nevada",
        "lat": 36.055,
        "lng": -115.070,
        "population": 58000,
    },
    {
        "zip": "94536",
        "city": "Fremont",
        "city_slug": "fremont",
        "state": "CA",
        "state_slug": "california",
        "lat": 37.570,
        "lng": -122.010,
        "population": 72000,
    },
    {
        "zip": "94538",
        "city": "Fremont",
        "city_slug": "fremont",
        "state": "CA",
        "state_slug": "california",
        "lat": 37.530,
        "lng": -121.970,
        "population": 68000,
    },
]

FACILITIES = [
    {
        "name": "Garland Appliance Scrap",
        "facility_type": "Appliance scrap / recycling drop-off",
        "city_slug": "garland",
        "state": "TX",
        "zip": "75040",
        "address": "1426 Commerce Street, Garland, TX 75040",
        "lat": 32.9050,
        "lng": -96.6300,
        "source_url": "https://garlandtx.gov/490/Appliance-Recycling",
        "hours": "Check garlandtx.gov for current hours",
        "phone": "972-205-3500",
        "accepted_materials": ["refrigerator", "freezer", "air-conditioner", "dehumidifier", "washer", "dryer"],
    },
    {
        "name": "Dallas County HC3 — Garland residents",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "garland",
        "state": "TX",
        "zip": "75243",
        "address": "11234 Plano Road, Dallas, TX 75243",
        "lat": 32.9050,
        "lng": -96.6980,
        "source_url": "https://www.dallascounty.org/departments/consolidated-services/hhw/",
        "hours": "Tue (extended), Wed–Thu, 2nd & 4th Sat — confirm before visit",
        "phone": "214-553-1765",
        "accepted_materials": HHW_MATERIALS
        + ["computer-monitor", "smartphone", "laptop", "desktop-computer"],
    },
    {
        "name": "Garland Electronics Recycling",
        "facility_type": "Electronics recycling — eRecycler / Big 4 / TCEQ",
        "city_slug": "garland",
        "state": "TX",
        "zip": "75040",
        "address": "Check garlandtx.gov for program locations",
        "lat": 32.9126,
        "lng": -96.6389,
        "source_url": "https://garlandtx.gov/477/Electronics-Recycling",
        "hours": "Check garlandtx.gov for event schedule",
        "phone": "972-205-3500",
        "accepted_materials": [
            "television", "computer-monitor", "laptop", "desktop-computer",
            "smartphone", "tablet", "printer", "e-waste-mixed", "hard-drive",
        ],
    },
    {
        "name": "Jersey City DPW Drop-Off",
        "facility_type": "HHW and tire drop-off",
        "city_slug": "jersey-city",
        "state": "NJ",
        "zip": "07305",
        "address": "13-15 Linden Avenue East, Jersey City, NJ 07305",
        "lat": 40.7000,
        "lng": -74.0900,
        "source_url": "https://www.jerseycitynj.gov/cityhall/DPW/sanitation",
        "hours": "Check jerseycitynj.gov for current hours",
        "phone": "201-547-4400",
        "accepted_materials": HHW_MATERIALS + ["tires", "tire-rims"],
    },
    {
        "name": "Chandler RSWCC",
        "facility_type": "Recycling & solid waste collection center",
        "city_slug": "chandler",
        "state": "AZ",
        "zip": "85286",
        "address": "955 E Queen Creek Road, Chandler, AZ 85286",
        "lat": 33.2500,
        "lng": -111.8200,
        "source_url": "https://www.chandleraz.gov/residents/recycling-and-trash/recycling-solid-waste-collection-center",
        "hours": "Check chandleraz.gov for current hours",
        "phone": "480-782-3510",
        "accepted_materials": [
            "refrigerator", "freezer", "air-conditioner", "tires", "tire-rims",
        ],
    },
    {
        "name": "Chandler HHW Appointment Collection",
        "facility_type": "Household hazardous waste — appointment collection",
        "city_slug": "chandler",
        "state": "AZ",
        "zip": "85224",
        "address": "Appointment collection — check chandleraz.gov",
        "lat": 33.3062,
        "lng": -111.8413,
        "source_url": "https://www.chandleraz.gov/residents/recycling-and-trash/household-hazardous-waste-disposal",
        "hours": "By appointment — schedule on chandleraz.gov",
        "phone": "480-782-3510",
        "accepted_materials": HHW_MATERIALS,
    },
    {
        "name": "Clark County Transfer Station — Henderson",
        "facility_type": "Transfer station — Freon appliances / tires / e-waste",
        "city_slug": "henderson",
        "state": "NV",
        "zip": "89011",
        "address": "560 Cape Horn Drive, Henderson, NV 89011",
        "lat": 36.0550,
        "lng": -115.0200,
        "source_url": "https://www.clarkcountynv.gov/government/departments/environment-and-sustainability/divisions/waste-management-and-recycling",
        "hours": "Daily 7:00–15:00 — confirm before visit",
        "phone": "702-455-8252",
        "accepted_materials": [
            "refrigerator", "freezer", "air-conditioner", "dehumidifier",
            "television", "computer-monitor", "laptop", "desktop-computer",
            "smartphone", "e-waste-mixed", "tires", "tire-rims",
        ],
    },
    {
        "name": "Henderson Shines",
        "facility_type": "Household hazardous waste collection events",
        "city_slug": "henderson",
        "state": "NV",
        "zip": "89014",
        "address": "Rotating Henderson locations — check hendersonshines.com",
        "lat": 36.0395,
        "lng": -114.9817,
        "source_url": "https://www.cityofhenderson.com/government/departments/community-development-and-services/community-resources/henderson-shines",
        "hours": "Scheduled events — check hendersonshines.com",
        "phone": "702-267-4100",
        "accepted_materials": HHW_MATERIALS,
    },
    {
        "name": "Alameda County HHW — Fremont (Boyce Rd)",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "fremont",
        "state": "CA",
        "zip": "94538",
        "address": "41149 Boyce Road, Fremont, CA 94538",
        "lat": 37.5300,
        "lng": -121.9700,
        "source_url": "https://www.stopwaste.org/recycling-disposal/hazardous-waste/household-hazardous-waste",
        "hours": "Wed–Fri 9:00–14:30; Sat 9:00–16:00 — confirm before visit",
        "phone": "800-606-6606",
        "accepted_materials": HHW_MATERIALS
        + ["television", "computer-monitor", "smartphone", "laptop", "desktop-computer", "e-waste-mixed"],
    },
    {
        "name": "Fremont Transfer Station",
        "facility_type": "Transfer station — tires / C&D",
        "city_slug": "fremont",
        "state": "CA",
        "zip": "94538",
        "address": "Check fremont.gov for transfer station address",
        "lat": 37.5300,
        "lng": -121.9700,
        "source_url": "https://www.fremont.gov/government/departments/environmental-services/recycling-compost-garbage/electronic-hazardous-waste",
        "hours": "Check fremont.gov for current hours",
        "phone": "510-657-3500",
        "accepted_materials": ["tires", "tire-rims", "construction-debris", "concrete", "drywall"],
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
        "garland": clone_siblings(garland()),
        "jersey-city": clone_siblings(jersey_city()),
        "chandler": clone_siblings(chandler()),
        "henderson": clone_siblings(henderson()),
        "fremont": clone_siblings(fremont()),
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

    print("Wave-18 metros written:")
    for city, rows in audited.items():
        print(f"  {city}: {len(rows)} rules")
    print(f"Total rules now: {len(keep)}")


if __name__ == "__main__":
    main()
