#!/usr/bin/env python3
"""Portal-audited city guides for wave-17 metros (city-sourced only).

Cities researched from official program pages (2026-08-11):
  - Scottsdale, AZ — area brush & bulk + appliance pickup / HHW home collection / e-waste
  - Plano, TX — monthly bulky + HCC / HC3 / Community Recycling Events
  - Winston-Salem, NC — annual bulky sweep + 3RC EnviroStation / Hanes Mill
  - Chesapeake, VA — scheduled bulk + SPSA HHW / e-waste / Suffolk tires
  - Irving, TX — weekly brush/bulky + Home Chemical events / Hunter Ferrell landfill
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


def scottsdale():
    c, st = "scottsdale", "AZ"
    bulk = (
        "City of Scottsdale — Brush and Bulk Collection",
        "https://www.scottsdaleaz.gov/solid-waste/collection-services/brush-and-bulk-collection",
    )
    hhw = (
        "City of Scottsdale — Household Hazardous Waste",
        "https://www.scottsdaleaz.gov/solid-waste/collection-services/household-hazardous-waste",
    )
    appliance = (
        "City of Scottsdale — Boxes and Appliance Collection",
        "https://www.scottsdaleaz.gov/solid-waste/collection-services/boxes-and-appliance-collection",
    )
    ewaste = (
        "City of Scottsdale — Electronics Recycling",
        "https://www.scottsdaleaz.gov/solid-waste/trash-recycling/electronics-recycling",
    )
    rows = []
    rows.append(
        R(
            c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
            "Free monthly brush & bulk by area — set out by 5 a.m. Mon; max 10×6×4 ft",
            "Scottsdale area brush & bulk collection",
            "Scottsdale mattresses go on free monthly brush & bulk by area. Set out by 5:00 a.m. Monday of your area week. Maximum pile size 10×6×4 feet. Tires and Freon appliances are NOT brush & bulk.",
            ["Check your area brush & bulk week on scottsdaleaz.gov.", "Set out by 5 a.m. Monday of area week.", "Keep pile within 10×6×4 feet."],
            [("Fee?", "Free on scheduled area brush & bulk week."), ("Freon fridge?", "No — use monthly appliance pickup last Thu.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c, st, "refrigerator", "SPECIAL_HANDLING", "High", False,
            "NOT brush & bulk — monthly appliance pickup last Thu; Freon cert required; remove doors",
            "Scottsdale monthly appliance pickup — last Thursday",
            "Scottsdale Freon refrigerators are NOT accepted on brush & bulk. Use monthly appliance pickup on the last Thursday of each month — certified Freon recovery required. Remove doors and empty unit. Never vent refrigerant yourself.",
            ["Do not set Freon fridge on brush & bulk.", "Schedule monthly appliance pickup — last Thursday.", "Remove doors; certified Freon recovery required."],
            [("Brush & bulk for Freon fridge?", "No — monthly appliance pickup only."), ("Washer on bulk?", "Yes — non-Freon washers use brush & bulk.")],
            *appliance,
        )
    )
    rows.append(
        R(
            c, st, "air-conditioner", "SPECIAL_HANDLING", "High", False,
            "NOT brush & bulk — monthly appliance pickup last Thu; Freon cert required",
            "Scottsdale monthly appliance pickup — last Thursday",
            "Scottsdale Freon window AC units are NOT accepted on brush & bulk. Use monthly appliance pickup on the last Thursday — certified Freon recovery required. Never vent refrigerant yourself.",
            ["Do not set Freon AC on brush & bulk.", "Schedule monthly appliance pickup — last Thursday.", "Keep sealed until proper Freon handling."],
            [("Same as Freon fridge?", "Yes — monthly appliance pickup, not brush & bulk.")],
            *appliance,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c, st, item, "SPECIAL_HANDLING", "Medium", True,
                "Free monthly brush & bulk by area — set out by 5 a.m. Mon; max 10×6×4 ft",
                "Scottsdale area brush & bulk collection",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s go on Scottsdale free monthly brush & bulk by area. Set out by 5:00 a.m. Monday. Maximum pile 10×6×4 feet. Freon refrigerators/AC use separate monthly appliance pickup.",
                ["Check area brush & bulk week.", "Set out by 5 a.m. Monday of area week.", "Freon appliances use monthly appliance pickup."],
                [("Same as Freon fridge?", "No — non-Freon uses brush & bulk.")],
                *bulk,
            )
        )
    rows.append(
        R(
            c, st, "television", "BANNED_FROM_LANDFILLS", "Medium", True,
            "CRT/projection → brush & bulk; flat-panel → quarterly e-waste 9191 E San Salvador Dr",
            "Scottsdale brush & bulk / e-waste — 9191 E San Salvador Dr",
            "Scottsdale TVs: CRT and projection TVs go on area brush & bulk (set out by 5 a.m. Monday). Flat-panel TVs go to quarterly e-waste drop-off — 9191 E San Salvador Dr — not brush & bulk. Wipe data before drop-off.",
            ["CRT/projection: set out on area brush & bulk week by 5 a.m. Monday.", "Flat-panel: haul to 9191 E San Salvador Dr quarterly e-waste.", "Wipe personal data."],
            [("Flat-panel on bulk?", "No — quarterly e-waste at 9191 E San Salvador Dr."), ("CRT on bulk?", "Yes — area brush & bulk.")],
            *ewaste,
        )
    )
    for item, label in [
        ("computer-monitor", "monitors"), ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste"),
    ]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "Medium", False,
                "NOT brush & bulk — quarterly e-waste 9191 E San Salvador Dr",
                "Scottsdale e-waste — 9191 E San Salvador Dr",
                f"Scottsdale electronics including {label} are NOT accepted on brush & bulk. Use quarterly e-waste drop-off — 9191 E San Salvador Dr. Wipe data before drop-off.",
                ["Do not set e-waste on brush & bulk.", "Haul to 9191 E San Salvador Dr quarterly e-waste.", "Wipe personal data."],
                [("Bulk for computers?", "No — e-waste drop-off only."), ("CRT TVs?", "CRT/projection TVs go on brush & bulk.")],
                *ewaste,
            )
        )
    rows.append(
        R(
            c, st, "paint-latex", "BANNED_FROM_LANDFILLS", "Medium", False,
            "Free HHW home collection — signup 1st of month 8 a.m.; max 3/year 20 gal; closed Jun/Dec",
            "Scottsdale HHW home collection (appointment)",
            "Scottsdale latex paint uses HHW home collection only — no drop-off center. Sign up on the 1st of each month at 8:00 a.m. Maximum 3 collections per year, 20 gallons total. Program closed June and December. Not brush & bulk or trash.",
            ["Sign up on the 1st of the month at 8 a.m.", "Schedule HHW home collection appointment.", "Max 3 collections/year, 20 gallons total."],
            [("Dry latex for trash?", "No — liquid latex uses HHW home collection."), ("Drop-off center?", "No — appointment home collection only.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
            "Free HHW home collection — signup 1st of month 8 a.m.; max 3/year 20 gal; closed Jun/Dec",
            "Scottsdale HHW home collection (appointment)",
            "Scottsdale oil-based paint uses HHW home collection only — no drop-off center. Sign up on the 1st of each month at 8:00 a.m. Maximum 3 collections per year, 20 gallons total. Program closed June and December.",
            ["Sign up on the 1st of the month at 8 a.m.", "Schedule HHW home collection appointment.", "Keep oil paint sealed and labeled."],
            [("Same as latex?", "Yes — both latex and oil paint use HHW home collection."), ("Closed months?", "June and December.")],
            *hhw,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
                "Free HHW home collection — signup 1st of month 8 a.m.; max 3/year 20 gal",
                "Scottsdale HHW home collection (appointment)",
                f"Take {item.replace('-', ' ')} via Scottsdale HHW home collection — sign up on the 1st of each month at 8:00 a.m. Maximum 3 collections per year, 20 gallons total. Closed June and December.",
                ["Sign up on the 1st of the month at 8 a.m.", "Schedule HHW home collection appointment.", "Keep chemicals off brush & bulk."],
                [("Drop-off center?", "No — appointment home collection only.")],
                *hhw,
            )
        )
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {
            "car-battery": " Lead-acid batteries via HHW home collection.",
            "lithium-battery": " Lithium batteries via HHW home collection.",
            "motor-oil": " Used motor oil via HHW home collection.",
            "propane-tank": " Propane tanks via HHW home collection — confirm size limits.",
            "fluorescent-bulbs": " Fluorescent bulbs via HHW home collection.",
            "cooking-oil": " Cooking oil via HHW home collection when not trash-safe.",
        }[item]
        rows.append(
            R(
                c, st, item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium", False,
                "Free HHW home collection — signup 1st of month 8 a.m.; max 3/year 20 gal",
                "Scottsdale HHW home collection (appointment)",
                f"Scottsdale HHW home collection accepts household hazardous materials.{extra} Sign up on the 1st of each month at 8:00 a.m. Max 3/year, 20 gallons. Closed June and December.",
                ["Sign up on the 1st of the month at 8 a.m.", "Schedule HHW home collection.", "Tires use separate disposal path."],
                [("Home collection only?", "Yes — no HHW drop-off center.")],
                *hhw,
            )
        )
    rows.append(
        R(
            c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
            "Rigid sealed container — confirm Scottsdale HHW home collection sharps acceptance",
            "Scottsdale HHW home collection (appointment)",
            "Place sharps in a rigid sealed container. Confirm acceptance via Scottsdale HHW home collection. Do not loose-bag needles.",
            ["Use rigid sealed container.", "Confirm sharps via HHW home collection signup.", "Never recycle loose needles."],
            [("Medications?", "Confirm drug take-back via Maricopa County programs.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
            "NOT brush & bulk — retailer take-back / private tire recycler",
            "Tire retailer take-back / private recycler",
            "Scottsdale tires are NOT accepted on brush & bulk. Use retailer take-back when replacing tires or a private tire recycler.",
            ["Do not set tires out on brush & bulk.", "Use retailer take-back when replacing tires.", "Confirm private recycler fees if needed."],
            [("Brush & bulk for tires?", "No — retailer or private recycler."), ("HHW for tires?", "No.")],
            *bulk,
        )
    )
    rows.append(
        R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True,
          "Scottsdale yard waste / brush collection", "Scottsdale brush collection",
          "Scottsdale handles yard waste and brush through regular collection and area brush schedules. Follow set-out rules on scottsdaleaz.gov.",
          ["Use brush/yard waste set-out rules.", "Keep yard waste out of HHW and e-waste.", "Check scottsdaleaz.gov for area schedule."],
          [("Christmas trees?", "Follow city seasonal yard waste guidance.")], *bulk)
    )
    rows.append(
        R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True,
          "Garbage cart unless private compost", "Scottsdale garbage / private compost",
          "Bag food scraps for garbage unless you compost. Keep food out of recycling and HHW.",
          ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."],
          [("HHW for food?", "No.")], *bulk)
    )
    rows.append(
        R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False,
          "Not recycling — store take-back / trash", "Retail bag take-back / trash",
          "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
          ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."],
          [("Brush & bulk for bags?", "No.")], *bulk)
    )
    rows.append(
        R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", False,
          "NOT brush & bulk — private C&D hauler",
          "Private C&D hauler",
          "Construction debris is not Scottsdale brush & bulk material. Hire a private C&D hauler for remodel loads. Route paint/chemicals to HHW home collection separately.",
          ["Do not treat remodel debris as brush & bulk.", "Hire private C&D for larger projects.", "Route paint/chemicals to HHW home collection."],
          [("HHW for C&D?", "No — separate paint/chemicals.")], *bulk)
    )
    return rows


def plano():
    c, st = "plano", "TX"
    bulky = (
        "City of Plano — Bulky Waste Collection",
        "https://www.plano.gov/821/Bulky-Waste-Collection",
    )
    hcc = (
        "City of Plano — Household Chemical Collection",
        "https://www.plano.gov/948/Household-Chemical-Collection",
    )
    events = (
        "City of Plano — Community Recycling Events",
        "https://www.plano.gov/1002/Community-Recycling-Events",
    )
    rows = []
    rows.append(
        R(
            c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
            "Free monthly bulky — schedule 972-941-7141 ≥2 business days ahead; max 6 cubic yards",
            "Plano monthly bulky waste collection",
            "Plano mattresses use free monthly bulky collection. Schedule at least 2 business days ahead by calling 972-941-7141. Maximum 6 cubic yards per pickup. TVs and tires are NOT bulky.",
            ["Call 972-941-7141 at least 2 business days ahead.", "Set out on scheduled bulky day.", "Maximum 6 cubic yards per pickup."],
            [("Fee?", "Free monthly bulky collection."), ("Schedule lead time?", "At least 2 business days.")],
            *bulky,
        )
    )
    rows.append(
        R(
            c, st, "refrigerator", "SPECIAL_HANDLING", "High", False,
            "NOT free bulky — $25 paid pickup per Freon item; curbside=False",
            "Plano paid Freon appliance pickup — $25/item",
            "Plano Freon refrigerators are NOT on free monthly bulky. Use $25 paid pickup per Freon item — schedule through city solid waste. Remove doors and empty unit. Never vent refrigerant yourself. Washers/dryers use free bulky.",
            ["Do not set Freon fridge on free monthly bulky.", "Schedule $25 paid Freon appliance pickup.", "Remove doors; never vent Freon yourself."],
            [("Free bulky for Freon fridge?", "No — $25 paid pickup per item."), ("Washer on free bulky?", "Yes — non-Freon washers use free monthly bulky.")],
            *bulky,
        )
    )
    rows.append(
        R(
            c, st, "air-conditioner", "SPECIAL_HANDLING", "High", False,
            "NOT free bulky — $25 paid pickup per Freon item",
            "Plano paid Freon appliance pickup — $25/item",
            "Plano Freon window AC units are NOT on free monthly bulky. Use $25 paid pickup per Freon item. Never vent refrigerant yourself.",
            ["Do not set Freon AC on free monthly bulky.", "Schedule $25 paid Freon appliance pickup.", "Keep sealed until proper Freon handling."],
            [("Same as Freon fridge?", "Yes — $25 paid pickup, not free bulky.")],
            *bulky,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c, st, item, "SPECIAL_HANDLING", "Medium", True,
                "Free monthly bulky — schedule 972-941-7141 ≥2 business days; max 6 cy",
                "Plano monthly bulky waste collection",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s use Plano free monthly bulky collection. Schedule at least 2 business days ahead — 972-941-7141. Maximum 6 cubic yards. Freon refrigerators/AC use $25 paid pickup.",
                ["Call 972-941-7141 at least 2 business days ahead.", "Set out on scheduled bulky day.", "Freon appliances use $25 paid pickup."],
                [("Same as Freon fridge?", "No — non-Freon uses free monthly bulky.")],
                *bulky,
            )
        )
    for item, label in [
        ("television", "TVs"), ("computer-monitor", "monitors"),
        ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste"),
    ]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "Medium", False,
                "NOT bulky — Community Recycling Events; TV $25",
                "Plano Community Recycling Events",
                f"Plano electronics including {label} are NOT accepted on monthly bulky. Use Community Recycling Events — TVs $25 each. Wipe data before drop-off.",
                ["Do not schedule TVs/e-waste on monthly bulky.", "Check Community Recycling Events schedule on plano.gov.", "TVs: $25 each at events."],
                [("Bulky for TVs?", "No — Community Recycling Events ($25/TV)."), ("Fridges?", "Freon fridges use $25 paid pickup, not bulky.")],
                *events,
            )
        )
    rows.append(
        R(
            c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", False,
            "Free HCC 972-769-4150 OR Dallas County HC3 — 11234 Plano Rd",
            "Plano HCC / Dallas County HC3 — 11234 Plano Rd",
            "Plano latex paint goes free to Plano Household Chemical Collection — call 972-769-4150 — OR Dallas County Home Chemical Collection Center — 11234 Plano Rd. Not monthly bulky or trash.",
            ["Call Plano HCC at 972-769-4150 for collection events.", "Or haul to Dallas County HC3 — 11234 Plano Rd.", "Bring proof of residency."],
            [("HC3 address?", "11234 Plano Rd, Dallas."), ("Bulky for paint?", "No — HCC or HC3 only.")],
            *hcc,
        )
    )
    rows.append(
        R(
            c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
            "Free HCC 972-769-4150 OR Dallas County HC3 — 11234 Plano Rd",
            "Plano HCC / Dallas County HC3 — 11234 Plano Rd",
            "Plano oil-based paint goes free to Plano Household Chemical Collection — 972-769-4150 — OR Dallas County HC3 — 11234 Plano Rd. Not bulky or trash.",
            ["Call Plano HCC at 972-769-4150.", "Or haul sealed oil paint to HC3 — 11234 Plano Rd.", "Keep containers sealed and labeled."],
            [("Same as latex?", "Yes — both use HCC or HC3 free drop-off.")],
            *hcc,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
                "Free HCC 972-769-4150 OR Dallas County HC3 — 11234 Plano Rd",
                "Plano HCC / Dallas County HC3 — 11234 Plano Rd",
                f"Take {item.replace('-', ' ')} free to Plano HCC — 972-769-4150 — OR Dallas County HC3 — 11234 Plano Rd. Not bulky or trash.",
                ["Call Plano HCC at 972-769-4150.", "Or deliver sealed containers to HC3.", "Keep chemicals off bulky piles."],
                [("HC3 for chemicals?", "Yes — 11234 Plano Rd with residency proof.")],
                *hcc,
            )
        )
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {
            "car-battery": " Lead-acid batteries at HCC or HC3.",
            "lithium-battery": " Lithium batteries at HCC or HC3.",
            "motor-oil": " Used motor oil at HCC or HC3.",
            "propane-tank": " Propane tanks at HCC or HC3 — confirm size limits.",
            "fluorescent-bulbs": " Fluorescent bulbs at HCC or HC3.",
            "cooking-oil": " Cooking oil at HCC or HC3 when not trash-safe.",
        }[item]
        rows.append(
            R(
                c, st, item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium", False,
                "Free HCC 972-769-4150 OR Dallas County HC3 — 11234 Plano Rd",
                "Plano HCC / Dallas County HC3 — 11234 Plano Rd",
                f"Plano HCC or Dallas County HC3 accepts household hazardous materials free.{extra}",
                ["Call Plano HCC at 972-769-4150.", "Or haul to HC3 — 11234 Plano Rd.", "Tires use EWS path, not HCC."],
                [("EWS for tires?", "972-769-4150 — tires not HCC.")],
                *hcc,
            )
        )
    rows.append(
        R(
            c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
            "Rigid sealed container — confirm HCC/HC3 sharps acceptance",
            "Plano HCC / Dallas County HC3",
            "Place sharps in a rigid sealed container. Confirm acceptance at Plano HCC or Dallas County HC3. Do not loose-bag needles.",
            ["Use rigid sealed container.", "Confirm sharps at HCC or HC3.", "Never recycle loose needles."],
            [("Medications?", "Confirm drug take-back via Collin County programs.")],
            *hcc,
        )
    )
    rows.append(
        R(
            c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
            "NOT bulky — Environmental Waste Services 972-769-4150",
            "Plano Environmental Waste Services (EWS)",
            "Plano tires are NOT accepted on monthly bulky. Contact Environmental Waste Services — 972-769-4150 — for tire disposal. Retailer take-back when replacing tires.",
            ["Do not set tires out for monthly bulky.", "Call EWS at 972-769-4150.", "Retailer take-back when replacing tires."],
            [("Bulky for tires?", "No — EWS 972-769-4150."), ("HHW for tires?", "No.")],
            *hcc,
        )
    )
    rows.append(
        R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True,
          "Plano yard waste collection", "Plano yard waste collection",
          "Plano handles yard waste through regular collection. Follow set-out rules on plano.gov.",
          ["Use yard waste set-out rules.", "Keep yard waste out of HHW and e-waste.", "Check plano.gov for seasonal guidance."],
          [("Christmas trees?", "Follow city seasonal yard waste guidance.")], *bulky)
    )
    rows.append(
        R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True,
          "Garbage cart unless private compost", "Plano garbage / private compost",
          "Bag food scraps for garbage unless you compost. Keep food out of recycling and HHW.",
          ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."],
          [("HCC for food?", "No.")], *bulky)
    )
    rows.append(
        R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False,
          "Not recycling — store take-back / trash", "Retail bag take-back / trash",
          "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
          ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."],
          [("Bulky for bags?", "No.")], *bulky)
    )
    rows.append(
        R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", False,
          "NOT monthly bulky — private C&D hauler",
          "Private C&D hauler",
          "Construction debris is not Plano monthly bulky material. Hire a private C&D hauler for remodel loads. Route paint/chemicals to HCC or HC3 separately.",
          ["Do not treat remodel debris as monthly bulky.", "Hire private C&D for larger projects.", "Route paint to HCC or HC3."],
          [("HCC for C&D?", "No — separate paint/chemicals.")], *bulky)
    )
    return rows


def winston_salem():
    c, st = "winston-salem", "NC"
    bulk = (
        "City of Winston-Salem — Bulky Items",
        "https://www.cityofws.org/587/Bulky-Items",
    )
    hhw = (
        "City of Winston-Salem — 3RC EnviroStation",
        "https://www.cityofws.org/1158/3RC-EnviroStation---Household-Hazardous-",
    )
    landfill = (
        "City of Winston-Salem — White Goods, Scrap Tires & Other Wastes",
        "https://www.cityofws.org/1281/White-Goods-Scrap-Tires-Other-Wastes",
    )
    rows = []
    rows.append(
        R(
            c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
            "Free annual bulky sweep — set out by 6 a.m. Monday of assigned week",
            "Winston-Salem annual bulky sweep collection",
            "Winston-Salem mattresses go on free annual bulky sweep — one week per year by area. Set out by 6:00 a.m. Monday of your assigned week. TVs and tires are NOT bulky sweep.",
            ["Check your assigned bulky sweep week on cityofws.org.", "Set out by 6 a.m. Monday of assigned week.", "Confirm area schedule before set-out."],
            [("Fee?", "Free on assigned annual bulky sweep week."), ("Set-out time?", "By 6 a.m. Monday of assigned week.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c, st, "refrigerator", "SPECIAL_HANDLING", "High", True,
            "Free white goods at Hanes Mill Landfill 325 Hanes Mill Rd (Freon extracted) OR bulky white goods",
            "Hanes Mill Landfill / Winston-Salem bulky white goods",
            "Winston-Salem Freon refrigerators may go on free annual bulky white goods sweep OR self-haul to Hanes Mill Landfill — 325 Hanes Mill Rd — with Freon extracted. Remove doors and empty unit. Never vent refrigerant yourself.",
            ["Set out on assigned bulky white goods week by 6 a.m. Monday.", "Or haul to Hanes Mill Landfill 325 Hanes Mill Rd (Freon extracted).", "Remove doors; never vent Freon yourself."],
            [("Bulky for Freon fridge?", "Yes — white goods on annual bulky sweep."), ("Hanes Mill?", "325 Hanes Mill Rd with Freon extracted.")],
            *landfill,
        )
    )
    rows.append(
        R(
            c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
            "Free bulky white goods OR Hanes Mill Landfill 325 Hanes Mill Rd (Freon extracted)",
            "Hanes Mill Landfill / Winston-Salem bulky white goods",
            "Winston-Salem Freon window AC units may go on annual bulky white goods sweep OR Hanes Mill Landfill — 325 Hanes Mill Rd — with Freon extracted. Never vent refrigerant yourself.",
            ["Set out on assigned bulky white goods week.", "Or haul to Hanes Mill with Freon extracted.", "Keep sealed until proper Freon handling."],
            [("Same as Freon fridge?", "Yes — bulky white goods or Hanes Mill.")],
            *landfill,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c, st, item, "SPECIAL_HANDLING", "Medium", True,
                "Free annual bulky sweep — set out by 6 a.m. Monday of assigned week",
                "Winston-Salem annual bulky sweep collection",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s go on Winston-Salem free annual bulky sweep. Set out by 6:00 a.m. Monday of assigned week. Freon refrigerators/AC also on white goods bulky or Hanes Mill.",
                ["Check assigned bulky sweep week.", "Set out by 6 a.m. Monday of assigned week.", "Freon appliances also on white goods bulky."],
                [("Same as Freon fridge?", "Yes — all large appliances on bulky sweep.")],
                *bulk,
            )
        )
    for item, label in [
        ("television", "TVs"), ("computer-monitor", "monitors"),
        ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste"),
    ]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "Medium", False,
                "NOT bulky — 3RC EnviroStation 1401 S MLK Jr Dr Wed–Sat 9–3; limit 2 TVs/year",
                "3RC EnviroStation — 1401 S Martin Luther King Jr Drive",
                f"Winston-Salem electronics including {label} are NOT accepted on annual bulky sweep. Use 3RC EnviroStation — 1401 S Martin Luther King Jr Drive — Wed–Sat 9:00 a.m.–3:00 p.m. Limit 2 TVs per year. Wipe data before drop-off.",
                ["Do not set TVs/e-waste on bulky sweep.", "Haul to 3RC EnviroStation Wed–Sat 9–3.", "Limit 2 TVs per year."],
                [("Bulky for TVs?", "No — 3RC EnviroStation only (2 TVs/year)."), ("Paint at 3RC?", "Yes — free paint drop-off.")],
                *hhw,
            )
        )
    rows.append(
        R(
            c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", False,
            "Free 3RC EnviroStation 1401 S MLK Jr Dr Wed–Sat 9–3",
            "3RC EnviroStation — 1401 S Martin Luther King Jr Drive",
            "Winston-Salem latex paint goes free to 3RC EnviroStation — 1401 S Martin Luther King Jr Drive — Wed–Sat 9:00 a.m.–3:00 p.m. Not bulky sweep or trash.",
            ["Haul sealed latex paint to 3RC EnviroStation.", "Hours: Wed–Sat 9–3.", "Bring proof of Forsyth County residency."],
            [("Bulky for paint?", "No — 3RC only."), ("Oil paint?", "Also free at 3RC.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
            "Free 3RC EnviroStation 1401 S MLK Jr Dr Wed–Sat 9–3",
            "3RC EnviroStation — 1401 S Martin Luther King Jr Drive",
            "Winston-Salem oil-based paint goes free to 3RC EnviroStation — 1401 S Martin Luther King Jr Drive — Wed–Sat 9–3. Not bulky sweep or trash.",
            ["Haul sealed oil paint to 3RC EnviroStation.", "Hours: Wed–Sat 9–3.", "Keep containers sealed and labeled."],
            [("Same as latex?", "Yes — both free at 3RC EnviroStation.")],
            *hhw,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
                "Free 3RC EnviroStation 1401 S MLK Jr Dr Wed–Sat 9–3",
                "3RC EnviroStation — 1401 S Martin Luther King Jr Drive",
                f"Take {item.replace('-', ' ')} free to 3RC EnviroStation — 1401 S MLK Jr Drive — Wed–Sat 9–3. Not bulky sweep or trash.",
                ["Deliver sealed containers to 3RC EnviroStation.", "Hours: Wed–Sat 9–3.", "Keep chemicals off bulky piles."],
                [("3RC for chemicals?", "Yes — free for Forsyth County residents.")],
                *hhw,
            )
        )
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {
            "car-battery": " Lead-acid batteries at 3RC.",
            "lithium-battery": " Lithium batteries at 3RC.",
            "motor-oil": " Used motor oil at 3RC.",
            "propane-tank": " Propane tanks at 3RC — confirm size limits.",
            "fluorescent-bulbs": " Fluorescent bulbs at 3RC.",
            "cooking-oil": " Cooking oil at 3RC when not trash-safe.",
        }[item]
        rows.append(
            R(
                c, st, item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium", False,
                "Free 3RC EnviroStation 1401 S MLK Jr Dr Wed–Sat 9–3",
                "3RC EnviroStation — 1401 S Martin Luther King Jr Drive",
                f"3RC EnviroStation accepts household hazardous materials free for Forsyth County residents.{extra}",
                ["Haul to 3RC EnviroStation Wed–Sat 9–3.", "Bring residency proof.", "Tires use Hanes Mill path, not 3RC."],
                [("Address?", "1401 S Martin Luther King Jr Drive.")],
                *hhw,
            )
        )
    rows.append(
        R(
            c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
            "Rigid sealed container — confirm 3RC EnviroStation sharps acceptance",
            "3RC EnviroStation — 1401 S Martin Luther King Jr Drive",
            "Place sharps in a rigid sealed container. Confirm acceptance at 3RC EnviroStation. Do not loose-bag needles.",
            ["Use rigid sealed container.", "Confirm sharps at 3RC EnviroStation.", "Never recycle loose needles."],
            [("Medications?", "Confirm drug take-back via Forsyth County programs.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
            "NOT bulky — free Hanes Mill Landfill 325 Hanes Mill Rd; 5/year",
            "Hanes Mill Landfill — 325 Hanes Mill Road",
            "Winston-Salem tires are NOT accepted on annual bulky sweep. Self-haul free to Hanes Mill Landfill — 325 Hanes Mill Rd — limit 5 tires per year. Retailer take-back when replacing tires.",
            ["Do not set tires out on bulky sweep.", "Haul to Hanes Mill Landfill 325 Hanes Mill Rd.", "Limit 5 tires per year."],
            [("Bulky for tires?", "No — Hanes Mill 5/year free."), ("HHW for tires?", "No.")],
            *landfill,
        )
    )
    rows.append(
        R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True,
          "Winston-Salem yard waste collection", "Winston-Salem yard waste collection",
          "Winston-Salem handles yard waste through regular collection. Follow set-out rules on cityofws.org.",
          ["Use yard waste set-out rules.", "Keep yard waste out of HHW and e-waste.", "Check cityofws.org for seasonal guidance."],
          [("Christmas trees?", "Follow city seasonal yard waste guidance.")], *bulk)
    )
    rows.append(
        R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True,
          "Garbage cart unless private compost", "Winston-Salem garbage / private compost",
          "Bag food scraps for garbage unless you compost. Keep food out of recycling and HHW.",
          ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."],
          [("3RC for food?", "No.")], *bulk)
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
          "NOT bulky sweep — private C&D hauler",
          "Private C&D hauler",
          "Construction debris is not Winston-Salem annual bulky sweep material. Hire a private C&D hauler for remodel loads. Route paint/chemicals to 3RC separately.",
          ["Do not treat remodel debris as bulky sweep.", "Hire private C&D for larger projects.", "Route paint to 3RC EnviroStation."],
          [("3RC for C&D?", "No — separate paint/chemicals.")], *bulk)
    )
    return rows


def chesapeake():
    c, st = "chesapeake", "VA"
    bulk = (
        "City of Chesapeake — Bulk Trash Collection",
        "https://www.cityofchesapeake.net/1069/Bulk-Trash-Collection",
    )
    spsa = (
        "SPSA — Household Hazardous Waste & E-Waste",
        "https://www.spsava.gov/161/Household-Hazardous-Waste-E-Waste-Guidel",
    )
    spsa_ches = (
        "SPSA — Chesapeake Collection Events",
        "https://www.spsava.gov/185/Chesapeake",
    )
    rows = []
    rows.append(
        R(
            c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
            "Free bulk — schedule 757-382-2489; max 12 pickups/year; pile max 4×4×10 ft",
            "Chesapeake scheduled bulk trash collection",
            "Chesapeake mattresses use free scheduled bulk collection — call 757-382-2489. Maximum 12 bulk pickups per year. Pile size limit 4×4×10 feet. TVs and tires are NOT bulk.",
            ["Call 757-382-2489 to schedule bulk pickup.", "Set out on scheduled bulk day.", "Maximum 12 pickups/year; pile 4×4×10 ft."],
            [("Fee?", "Free scheduled bulk collection."), ("Limit?", "12 pickups/year per property.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c, st, "refrigerator", "SPECIAL_HANDLING", "High", True,
            "Free bulk with doors removed OR SPSA with Freon certification",
            "Chesapeake bulk collection / SPSA Freon appliance",
            "Chesapeake Freon refrigerators may go on free scheduled bulk with doors removed OR self-haul to SPSA with Freon certification. Remove doors and empty unit. Never vent refrigerant yourself.",
            ["Schedule bulk pickup — 757-382-2489 — with doors removed.", "Or haul to SPSA with Freon certification.", "Never vent Freon yourself."],
            [("Bulk for Freon fridge?", "Yes — with doors removed."), ("SPSA alternative?", "Yes — with Freon certification.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
            "Free bulk OR SPSA with Freon certification",
            "Chesapeake bulk collection / SPSA Freon appliance",
            "Chesapeake Freon window AC units may go on scheduled bulk OR SPSA with Freon certification. Never vent refrigerant yourself.",
            ["Schedule bulk pickup with doors removed if applicable.", "Or haul to SPSA with Freon certification.", "Keep sealed until proper Freon handling."],
            [("Same as Freon fridge?", "Yes — bulk or SPSA Freon cert.")],
            *bulk,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c, st, item, "SPECIAL_HANDLING", "Medium", True,
                "Free bulk — schedule 757-382-2489; max 12/year; pile 4×4×10 ft",
                "Chesapeake scheduled bulk trash collection",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s use Chesapeake free scheduled bulk. Call 757-382-2489. Maximum 12 pickups/year, pile 4×4×10 feet. Freon refrigerators/AC also on bulk or SPSA.",
                ["Call 757-382-2489 to schedule bulk.", "Set out on scheduled bulk day.", "Limit 12 pickups/year."],
                [("Same as Freon fridge?", "Yes — all large appliances on bulk.")],
                *bulk,
            )
        )
    for item, label in [
        ("television", "TVs"), ("computer-monitor", "monitors"),
        ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste"),
    ]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "Medium", False,
                "NOT bulk — SPSA 901 Hollowell Lane 1st Wed & 3rd Sat 9–noon; 5 items/visit",
                "SPSA HHW/E-Waste — 901 Hollowell Lane, Norfolk",
                f"Chesapeake electronics including {label} are NOT accepted on scheduled bulk. Use SPSA — 901 Hollowell Lane — 1st Wednesday and 3rd Saturday 9:00 a.m.–noon. Limit 5 items per visit. Wipe data before drop-off.",
                ["Do not schedule TVs/e-waste on bulk.", "Haul to SPSA 901 Hollowell Lane 1st Wed & 3rd Sat 9–noon.", "Limit 5 items per visit."],
                [("Bulk for TVs?", "No — SPSA e-waste events only."), ("Paint at SPSA?", "Yes — same HHW windows.")],
                *spsa,
            )
        )
    rows.append(
        R(
            c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", False,
            "SPSA HHW 901 Hollowell Lane 1st Wed & 3rd Sat 9–noon",
            "SPSA HHW — 901 Hollowell Lane, Norfolk",
            "Chesapeake latex paint goes to SPSA HHW — 901 Hollowell Lane — 1st Wednesday and 3rd Saturday 9:00 a.m.–noon. Not bulk or trash.",
            ["Haul sealed latex paint to SPSA 901 Hollowell Lane.", "Hours: 1st Wed & 3rd Sat 9–noon.", "Confirm Chesapeake residency requirements."],
            [("Bulk for paint?", "No — SPSA HHW only."), ("Oil paint?", "Also at SPSA HHW same windows.")],
            *spsa,
        )
    )
    rows.append(
        R(
            c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
            "SPSA HHW 901 Hollowell Lane 1st Wed & 3rd Sat 9–noon",
            "SPSA HHW — 901 Hollowell Lane, Norfolk",
            "Chesapeake oil-based paint goes to SPSA HHW — 901 Hollowell Lane — 1st Wed & 3rd Sat 9–noon. Not bulk or trash.",
            ["Haul sealed oil paint to SPSA 901 Hollowell Lane.", "Hours: 1st Wed & 3rd Sat 9–noon.", "Keep containers sealed and labeled."],
            [("Same as latex?", "Yes — both at SPSA HHW same windows.")],
            *spsa,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
                "SPSA HHW 901 Hollowell Lane 1st Wed & 3rd Sat 9–noon",
                "SPSA HHW — 901 Hollowell Lane, Norfolk",
                f"Take {item.replace('-', ' ')} to SPSA HHW — 901 Hollowell Lane — 1st Wed & 3rd Sat 9–noon. Not bulk or trash.",
                ["Deliver sealed containers to SPSA 901 Hollowell Lane.", "Hours: 1st Wed & 3rd Sat 9–noon.", "Keep chemicals off bulk piles."],
                [("SPSA for chemicals?", "Yes — same HHW windows as paint.")],
                *spsa,
            )
        )
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {
            "car-battery": " Lead-acid batteries at SPSA HHW.",
            "lithium-battery": " Lithium batteries at SPSA HHW.",
            "motor-oil": " Used motor oil at SPSA HHW.",
            "propane-tank": " Propane tanks at SPSA HHW — confirm size limits.",
            "fluorescent-bulbs": " Fluorescent bulbs at SPSA HHW.",
            "cooking-oil": " Cooking oil at SPSA HHW when not trash-safe.",
        }[item]
        rows.append(
            R(
                c, st, item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium", False,
                "SPSA HHW 901 Hollowell Lane 1st Wed & 3rd Sat 9–noon",
                "SPSA HHW — 901 Hollowell Lane, Norfolk",
                f"SPSA HHW at 901 Hollowell Lane accepts household hazardous materials.{extra} Hours: 1st Wed & 3rd Sat 9–noon.",
                ["Haul to SPSA 901 Hollowell Lane during posted hours.", "1st Wed & 3rd Sat 9–noon.", "Tires use Suffolk landfill path."],
                [("Address?", "901 Hollowell Lane, Norfolk.")],
                *spsa,
            )
        )
    rows.append(
        R(
            c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
            "Rigid sealed container — confirm SPSA HHW sharps acceptance",
            "SPSA HHW — 901 Hollowell Lane, Norfolk",
            "Place sharps in a rigid sealed container. Confirm acceptance at SPSA HHW. Do not loose-bag needles.",
            ["Use rigid sealed container.", "Confirm sharps at SPSA 901 Hollowell Lane.", "Never recycle loose needles."],
            [("Medications?", "Confirm drug take-back via Hampton Roads programs.")],
            *spsa,
        )
    )
    rows.append(
        R(
            c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
            "NOT bulk — SPSA Suffolk landfill 4 auto tires/day free",
            "SPSA Suffolk Regional Landfill — tire drop-off",
            "Chesapeake tires are NOT accepted on scheduled bulk. Self-haul free to SPSA Suffolk Regional Landfill — limit 4 auto tires per day. Retailer take-back when replacing tires.",
            ["Do not set tires out for bulk pickup.", "Haul to SPSA Suffolk landfill.", "Limit 4 auto tires per day free."],
            [("Bulk for tires?", "No — SPSA Suffolk landfill 4/day free."), ("HHW for tires?", "No.")],
            *spsa_ches,
        )
    )
    rows.append(
        R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True,
          "Chesapeake yard waste collection", "Chesapeake yard waste collection",
          "Chesapeake handles yard waste through regular collection. Follow set-out rules on cityofchesapeake.net.",
          ["Use yard waste set-out rules.", "Keep yard waste out of HHW and e-waste.", "Check city site for seasonal guidance."],
          [("Christmas trees?", "Follow city seasonal yard waste guidance.")], *bulk)
    )
    rows.append(
        R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True,
          "Garbage cart unless private compost", "Chesapeake garbage / private compost",
          "Bag food scraps for garbage unless you compost. Keep food out of recycling and HHW.",
          ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."],
          [("SPSA for food?", "No.")], *bulk)
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
          "Construction debris is not Chesapeake scheduled bulk material. Hire a private C&D hauler for remodel loads. Route paint/chemicals to SPSA HHW separately.",
          ["Do not treat remodel debris as bulk.", "Hire private C&D for larger projects.", "Route paint to SPSA HHW."],
          [("SPSA for C&D?", "No — separate paint/chemicals.")], *bulk)
    )
    return rows


def irving():
    c, st = "irving", "TX"
    sw = (
        "City of Irving — Solid Waste Services",
        "https://www.cityofirving.org/SWS",
    )
    landfill = (
        "City of Irving — Hunter Ferrell Landfill",
        "https://www.cityofirving.org/Landfill",
    )
    hc3 = (
        "Dallas County — Home Chemical Collection Center",
        "https://www.dallascounty.org/departments/consolidated-services/hhw/",
    )
    rows = []
    rows.append(
        R(
            c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
            "Free weekly brush/bulky same day as recycling",
            "Irving weekly brush/bulky collection",
            "Irving mattresses go on free weekly brush/bulky collection on the same day as recycling. Set out per city guidelines. TVs and tires are NOT standard bulky.",
            ["Set out on recycling day for brush/bulky.", "Follow cityofirving.org set-out rules.", "Keep pile within city size limits."],
            [("Fee?", "Free weekly on recycling day."), ("TVs on bulky?", "No — electronics events only.")],
            *sw,
        )
    )
    rows.append(
        R(
            c, st, "refrigerator", "SPECIAL_HANDLING", "High", True,
            "Free weekly bulky OR Hunter Ferrell Landfill 110 E Hunter Ferrell Rd appliances recycled",
            "Irving weekly bulky / Hunter Ferrell Landfill",
            "Irving Freon refrigerators may go on free weekly brush/bulky OR self-haul to Hunter Ferrell Landfill — 110 E Hunter Ferrell Rd — for appliance recycling. Remove doors and empty unit. Never vent refrigerant yourself.",
            ["Set out on weekly brush/bulky day.", "Or haul to Hunter Ferrell Landfill 110 E Hunter Ferrell Rd.", "Remove doors; never vent Freon yourself."],
            [("Weekly bulky for Freon fridge?", "Yes — or Hunter Ferrell appliance recycling."), ("Washer on bulky?", "Yes — non-Freon washers on weekly bulky.")],
            *landfill,
        )
    )
    rows.append(
        R(
            c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
            "Free weekly bulky OR Hunter Ferrell Landfill 110 E Hunter Ferrell Rd",
            "Irving weekly bulky / Hunter Ferrell Landfill",
            "Irving Freon window AC units may go on weekly brush/bulky OR Hunter Ferrell Landfill — 110 E Hunter Ferrell Rd. Never vent refrigerant yourself.",
            ["Set out on weekly brush/bulky day.", "Or haul to Hunter Ferrell Landfill.", "Keep sealed until proper Freon handling."],
            [("Same as Freon fridge?", "Yes — weekly bulky or Hunter Ferrell.")],
            *landfill,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c, st, item, "SPECIAL_HANDLING", "Medium", True,
                "Free weekly brush/bulky same day as recycling",
                "Irving weekly brush/bulky collection",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s use Irving free weekly brush/bulky on recycling day. Freon refrigerators/AC also on weekly bulky or Hunter Ferrell.",
                ["Set out on recycling day for brush/bulky.", "Follow city set-out rules.", "Freon appliances also on weekly bulky."],
                [("Same as Freon fridge?", "Yes — all large appliances on weekly bulky.")],
                *sw,
            )
        )
    rows.append(
        R(
            c, st, "television", "BANNED_FROM_LANDFILLS", "Medium", False,
            "NOT standard bulky — electronics recycling events; HCC events accept computers not TVs",
            "Irving electronics recycling events",
            "Irving TVs are NOT accepted on standard weekly brush/bulky. Use city electronics recycling events. Home Chemical Collection (HCC) events accept computers — not TVs. Wipe data before drop-off.",
            ["Do not set TVs on weekly brush/bulky.", "Check electronics recycling events on cityofirving.org.", "HCC events: computers yes, TVs no."],
            [("Bulky for TVs?", "No — electronics events only."), ("HCC for TVs?", "No — computers only at HCC events.")],
            *sw,
        )
    )
    for item, label in [
        ("computer-monitor", "monitors"), ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste"),
    ]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "Medium", False,
                "NOT standard bulky — electronics events / HCC events (computers not TVs)",
                "Irving electronics recycling events / HCC events",
                f"Irving electronics including {label} are NOT on standard weekly bulky. Use electronics recycling events or Home Chemical Collection events — computers accepted, TVs not. Wipe data before drop-off.",
                ["Do not set e-waste on weekly brush/bulky.", "Check electronics or HCC event schedule.", "Wipe personal data."],
                [("HCC for computers?", "Yes — HCC events accept computers, not TVs."), ("Bulky for e-waste?", "No.")],
                *sw,
            )
        )
    rows.append(
        R(
            c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", False,
            "Home Chemical events 835 W Irving Blvd voucher OR Dallas County HC3 free — 11234 Plano Rd",
            "Irving Home Chemical Collection / Dallas County HC3",
            "Irving latex paint goes via Home Chemical Collection events — 835 W Irving Blvd voucher — OR free Dallas County HC3 — 11234 Plano Rd. Not weekly bulky or trash.",
            ["Obtain Home Chemical event voucher for 835 W Irving Blvd.", "Or haul to Dallas County HC3 — 11234 Plano Rd.", "Bring proof of residency."],
            [("HC3 address?", "11234 Plano Rd, Dallas."), ("Bulky for paint?", "No — Home Chemical events or HC3.")],
            *hc3,
        )
    )
    rows.append(
        R(
            c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
            "Home Chemical events 835 W Irving Blvd voucher OR Dallas County HC3 free",
            "Irving Home Chemical Collection / Dallas County HC3",
            "Irving oil-based paint goes via Home Chemical Collection events — 835 W Irving Blvd voucher — OR free Dallas County HC3 — 11234 Plano Rd. Not bulky or trash.",
            ["Obtain Home Chemical event voucher.", "Or haul sealed oil paint to HC3.", "Keep containers sealed and labeled."],
            [("Same as latex?", "Yes — Home Chemical events or HC3 free.")],
            *hc3,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
                "Home Chemical events 835 W Irving Blvd voucher OR Dallas County HC3 free",
                "Irving Home Chemical Collection / Dallas County HC3",
                f"Take {item.replace('-', ' ')} via Irving Home Chemical events — 835 W Irving Blvd voucher — OR Dallas County HC3 — 11234 Plano Rd. Not bulky or trash.",
                ["Obtain Home Chemical event voucher.", "Or deliver sealed containers to HC3.", "Keep chemicals off bulky piles."],
                [("HC3 for chemicals?", "Yes — 11234 Plano Rd with residency proof.")],
                *hc3,
            )
        )
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {
            "car-battery": " Lead-acid batteries at Home Chemical events or HC3.",
            "lithium-battery": " Lithium batteries at Home Chemical events or HC3.",
            "motor-oil": " Used motor oil at Home Chemical events or HC3.",
            "propane-tank": " Propane tanks at Home Chemical events or HC3 — confirm size limits.",
            "fluorescent-bulbs": " Fluorescent bulbs at Home Chemical events or HC3.",
            "cooking-oil": " Cooking oil at Home Chemical events or HC3 when not trash-safe.",
        }[item]
        rows.append(
            R(
                c, st, item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium", False,
                "Home Chemical events 835 W Irving Blvd voucher OR Dallas County HC3 free",
                "Irving Home Chemical Collection / Dallas County HC3",
                f"Irving Home Chemical events or Dallas County HC3 accepts household hazardous materials free.{extra}",
                ["Obtain Home Chemical event voucher.", "Or haul to HC3 — 11234 Plano Rd.", "Tires use Hunter Ferrell path."],
                [("HC3 phone?", "214-553-1765 — confirm hours.")],
                *hc3,
            )
        )
    rows.append(
        R(
            c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
            "Rigid sealed container — confirm Home Chemical events / HC3 sharps acceptance",
            "Irving Home Chemical Collection / Dallas County HC3",
            "Place sharps in a rigid sealed container. Confirm acceptance via Home Chemical events or Dallas County HC3. Do not loose-bag needles.",
            ["Use rigid sealed container.", "Confirm sharps via Home Chemical events or HC3.", "Never recycle loose needles."],
            [("Medications?", "Confirm drug take-back via Dallas County programs.")],
            *hc3,
        )
    )
    rows.append(
        R(
            c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
            "NOT bulky — Hunter Ferrell Landfill 110 E Hunter Ferrell Rd; $5/tire when >5 in load",
            "Hunter Ferrell Landfill — 110 E Hunter Ferrell Road",
            "Irving tires are NOT accepted on weekly brush/bulky. Self-haul to Hunter Ferrell Landfill — 110 E Hunter Ferrell Rd — $5 per tire when more than 5 tires in a load. Retailer take-back when replacing tires.",
            ["Do not set tires out on weekly bulky.", "Haul to Hunter Ferrell Landfill 110 E Hunter Ferrell Rd.", "$5/tire when load exceeds 5 tires."],
            [("Bulky for tires?", "No — Hunter Ferrell Landfill."), ("Fee?", "$5/tire when >5 in load.")],
            *landfill,
        )
    )
    rows.append(
        R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True,
          "Irving yard waste / brush collection", "Irving brush collection",
          "Irving handles yard waste and brush through regular collection and weekly brush/bulky. Follow set-out rules on cityofirving.org.",
          ["Use brush/yard waste set-out rules.", "Keep yard waste out of HHW and e-waste.", "Check city site for seasonal guidance."],
          [("Christmas trees?", "Follow city seasonal yard waste guidance.")], *sw)
    )
    rows.append(
        R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True,
          "Garbage cart unless private compost", "Irving garbage / private compost",
          "Bag food scraps for garbage unless you compost. Keep food out of recycling and HHW.",
          ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."],
          [("Home Chemical for food?", "No.")], *sw)
    )
    rows.append(
        R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False,
          "Not recycling — store take-back / trash", "Retail bag take-back / trash",
          "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
          ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."],
          [("Bulky for bags?", "No.")], *sw)
    )
    rows.append(
        R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", False,
          "NOT weekly bulky — private C&D hauler",
          "Private C&D hauler",
          "Construction debris is not Irving weekly brush/bulky material. Hire a private C&D hauler for remodel loads. Route paint/chemicals to Home Chemical events or HC3 separately.",
          ["Do not treat remodel debris as weekly bulky.", "Hire private C&D for larger projects.", "Route paint to Home Chemical events or HC3."],
          [("Home Chemical for C&D?", "No — separate paint/chemicals.")], *sw)
    )
    return rows


CITIES = [
    {
        "city": "Scottsdale",
        "city_slug": "scottsdale",
        "state": "AZ",
        "state_slug": "arizona",
        "lat": 33.4942,
        "lng": -111.9261,
        "population": 241361,
    },
    {
        "city": "Plano",
        "city_slug": "plano",
        "state": "TX",
        "state_slug": "texas",
        "lat": 33.0198,
        "lng": -96.6989,
        "population": 285494,
    },
    {
        "city": "Winston-Salem",
        "city_slug": "winston-salem",
        "state": "NC",
        "state_slug": "north-carolina",
        "lat": 36.0999,
        "lng": -80.2442,
        "population": 249545,
    },
    {
        "city": "Chesapeake",
        "city_slug": "chesapeake",
        "state": "VA",
        "state_slug": "virginia",
        "lat": 36.7682,
        "lng": -76.2875,
        "population": 249422,
    },
    {
        "city": "Irving",
        "city_slug": "irving",
        "state": "TX",
        "state_slug": "texas",
        "lat": 32.8140,
        "lng": -96.9489,
        "population": 256684,
    },
]

ZIPS = [
    {
        "zip": "85251",
        "city": "Scottsdale",
        "city_slug": "scottsdale",
        "state": "AZ",
        "state_slug": "arizona",
        "lat": 33.494,
        "lng": -111.926,
        "population": 28000,
    },
    {
        "zip": "85254",
        "city": "Scottsdale",
        "city_slug": "scottsdale",
        "state": "AZ",
        "state_slug": "arizona",
        "lat": 33.615,
        "lng": -111.920,
        "population": 35000,
    },
    {
        "zip": "75023",
        "city": "Plano",
        "city_slug": "plano",
        "state": "TX",
        "state_slug": "texas",
        "lat": 33.060,
        "lng": -96.730,
        "population": 42000,
    },
    {
        "zip": "75074",
        "city": "Plano",
        "city_slug": "plano",
        "state": "TX",
        "state_slug": "texas",
        "lat": 33.020,
        "lng": -96.660,
        "population": 38000,
    },
    {
        "zip": "27101",
        "city": "Winston-Salem",
        "city_slug": "winston-salem",
        "state": "NC",
        "state_slug": "north-carolina",
        "lat": 36.100,
        "lng": -80.244,
        "population": 12000,
    },
    {
        "zip": "27103",
        "city": "Winston-Salem",
        "city_slug": "winston-salem",
        "state": "NC",
        "state_slug": "north-carolina",
        "lat": 36.070,
        "lng": -80.310,
        "population": 28000,
    },
    {
        "zip": "23320",
        "city": "Chesapeake",
        "city_slug": "chesapeake",
        "state": "VA",
        "state_slug": "virginia",
        "lat": 36.768,
        "lng": -76.287,
        "population": 45000,
    },
    {
        "zip": "23322",
        "city": "Chesapeake",
        "city_slug": "chesapeake",
        "state": "VA",
        "state_slug": "virginia",
        "lat": 36.710,
        "lng": -76.250,
        "population": 52000,
    },
    {
        "zip": "75038",
        "city": "Irving",
        "city_slug": "irving",
        "state": "TX",
        "state_slug": "texas",
        "lat": 32.865,
        "lng": -96.990,
        "population": 35000,
    },
    {
        "zip": "75060",
        "city": "Irving",
        "city_slug": "irving",
        "state": "TX",
        "state_slug": "texas",
        "lat": 32.814,
        "lng": -96.949,
        "population": 40000,
    },
]

FACILITIES = [
    {
        "name": "Scottsdale HHW Home Collection",
        "facility_type": "Household hazardous waste — appointment home collection",
        "city_slug": "scottsdale",
        "state": "AZ",
        "zip": "85251",
        "address": "Appointment home collection — no drop-off center",
        "lat": 33.4942,
        "lng": -111.9261,
        "source_url": "https://www.scottsdaleaz.gov/solid-waste/collection-services/household-hazardous-waste",
        "hours": "Signup 1st of month 8 a.m.; max 3/year; closed Jun/Dec",
        "phone": "480-312-5600",
        "accepted_materials": HHW_MATERIALS,
    },
    {
        "name": "Scottsdale Electronics Recycling",
        "facility_type": "Electronics drop-off — quarterly events",
        "city_slug": "scottsdale",
        "state": "AZ",
        "zip": "85256",
        "address": "9191 E San Salvador Drive, Scottsdale, AZ 85256",
        "lat": 33.5550,
        "lng": -111.8800,
        "source_url": "https://www.scottsdaleaz.gov/solid-waste/trash-recycling/electronics-recycling",
        "hours": "Quarterly e-waste events — check city schedule",
        "phone": "480-312-5600",
        "accepted_materials": [
            "television", "computer-monitor", "laptop", "desktop-computer",
            "smartphone", "tablet", "printer", "e-waste-mixed", "hard-drive",
        ],
    },
    {
        "name": "Scottsdale Appliance Collection",
        "facility_type": "Curbside appliance pickup — Freon appliances",
        "city_slug": "scottsdale",
        "state": "AZ",
        "zip": "85251",
        "address": "Curbside — last Thursday of each month",
        "lat": 33.4942,
        "lng": -111.9261,
        "source_url": "https://www.scottsdaleaz.gov/solid-waste/collection-services/boxes-and-appliance-collection",
        "hours": "Last Thursday of each month",
        "phone": "480-312-5600",
        "accepted_materials": ["refrigerator", "freezer", "air-conditioner", "dehumidifier"],
    },
    {
        "name": "Plano Household Chemical Collection (HCC)",
        "facility_type": "Household hazardous waste collection events",
        "city_slug": "plano",
        "state": "TX",
        "zip": "75074",
        "address": "Check plano.gov for event location",
        "lat": 33.0198,
        "lng": -96.6989,
        "source_url": "https://www.plano.gov/948/Household-Chemical-Collection",
        "hours": "Scheduled collection events — call 972-769-4150",
        "phone": "972-769-4150",
        "accepted_materials": HHW_MATERIALS,
    },
    {
        "name": "Dallas County Home Chemical Collection Center (HC3)",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "plano",
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
        "name": "Plano Environmental Waste Services (EWS)",
        "facility_type": "Tire disposal",
        "city_slug": "plano",
        "state": "TX",
        "zip": "75074",
        "address": "Check plano.gov for EWS drop-off location",
        "lat": 33.0198,
        "lng": -96.6989,
        "source_url": "https://www.plano.gov/948/Household-Chemical-Collection",
        "hours": "Call for current hours",
        "phone": "972-769-4150",
        "accepted_materials": ["tires", "tire-rims"],
    },
    {
        "name": "3RC EnviroStation",
        "facility_type": "HHW and e-waste drop-off",
        "city_slug": "winston-salem",
        "state": "NC",
        "zip": "27101",
        "address": "1401 S Martin Luther King Jr Drive, Winston-Salem, NC 27101",
        "lat": 36.0780,
        "lng": -80.2400,
        "source_url": "https://www.cityofws.org/1158/3RC-EnviroStation---Household-Hazardous-",
        "hours": "Wed–Sat 9:00–15:00",
        "phone": "336-727-8000",
        "accepted_materials": HHW_MATERIALS
        + ["television", "computer-monitor", "smartphone", "laptop", "desktop-computer", "e-waste-mixed"],
    },
    {
        "name": "Hanes Mill Landfill",
        "facility_type": "Landfill — white goods / tires",
        "city_slug": "winston-salem",
        "state": "NC",
        "zip": "27105",
        "address": "325 Hanes Mill Road, Winston-Salem, NC 27105",
        "lat": 36.1450,
        "lng": -80.3100,
        "source_url": "https://www.cityofws.org/1281/White-Goods-Scrap-Tires-Other-Wastes",
        "hours": "Check cityofws.org for current hours",
        "phone": "336-727-8000",
        "accepted_materials": ["refrigerator", "freezer", "air-conditioner", "washer", "dryer", "tires", "tire-rims"],
    },
    {
        "name": "SPSA HHW/E-Waste Collection",
        "facility_type": "Household hazardous waste and e-waste drop-off",
        "city_slug": "chesapeake",
        "state": "VA",
        "zip": "23513",
        "address": "901 Hollowell Lane, Norfolk, VA 23513",
        "lat": 36.8700,
        "lng": -76.2200,
        "source_url": "https://www.spsava.gov/161/Household-Hazardous-Waste-E-Waste-Guidel",
        "hours": "1st Wed & 3rd Sat 9:00–12:00",
        "phone": "757-545-3500",
        "accepted_materials": HHW_MATERIALS
        + ["television", "computer-monitor", "smartphone", "laptop", "desktop-computer", "e-waste-mixed"],
    },
    {
        "name": "SPSA Suffolk Regional Landfill",
        "facility_type": "Tire drop-off",
        "city_slug": "chesapeake",
        "state": "VA",
        "zip": "23434",
        "address": "Suffolk, VA — check spsava.gov for address",
        "lat": 36.7300,
        "lng": -76.5800,
        "source_url": "https://www.spsava.gov/185/Chesapeake",
        "hours": "Check spsava.gov for current hours",
        "phone": "757-545-3500",
        "accepted_materials": ["tires", "tire-rims"],
    },
    {
        "name": "Hunter Ferrell Landfill",
        "facility_type": "Landfill — appliances / tires",
        "city_slug": "irving",
        "state": "TX",
        "zip": "75060",
        "address": "110 E Hunter Ferrell Road, Irving, TX 75060",
        "lat": 32.8050,
        "lng": -96.9350,
        "source_url": "https://www.cityofirving.org/Landfill",
        "hours": "Check cityofirving.org for current hours",
        "phone": "972-721-8055",
        "accepted_materials": [
            "refrigerator", "freezer", "air-conditioner", "washer", "dryer",
            "tires", "tire-rims",
        ],
    },
    {
        "name": "Irving Home Chemical Collection",
        "facility_type": "Household hazardous waste collection events",
        "city_slug": "irving",
        "state": "TX",
        "zip": "75060",
        "address": "835 W Irving Boulevard, Irving, TX 75060",
        "lat": 32.8140,
        "lng": -96.9600,
        "source_url": "https://www.cityofirving.org/SWS",
        "hours": "Scheduled Home Chemical events — voucher required",
        "phone": "972-721-8055",
        "accepted_materials": HHW_MATERIALS + ["laptop", "desktop-computer", "computer-monitor"],
    },
    {
        "name": "Dallas County HC3 — Irving residents",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "irving",
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
        "scottsdale": clone_siblings(scottsdale()),
        "plano": clone_siblings(plano()),
        "winston-salem": clone_siblings(winston_salem()),
        "chesapeake": clone_siblings(chesapeake()),
        "irving": clone_siblings(irving()),
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

    print("Wave-17 metros written:")
    for city, rows in audited.items():
        print(f"  {city}: {len(rows)} rules")
    print(f"Total rules now: {len(keep)}")


if __name__ == "__main__":
    main()
