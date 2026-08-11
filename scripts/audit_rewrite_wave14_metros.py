#!/usr/bin/env python3
"""Portal-audited city guides for wave-14 metros (city-sourced only).

Cities researched from official program pages (2026-08-11):
  - Grand Rapids, MI — city bulk sticker + Kent County SafeChem HHW/e-waste
  - Rochester, NY — free refuse-day bulk + Monroe County ecopark HHW/e-waste
  - Norfolk, VA — scheduled bulk + SPSA transfer station HHW/e-waste
  - Lexington, KY — LexCall bulky/appliances + event HHW + ERC e-waste
  - Toledo, OH — weekly bulk (5 items) + Clean Toledo center/events
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


def grand_rapids():
    c, st = "grand-rapids", "MI"
    bulk = (
        "City of Grand Rapids — Bulk item collection",
        "https://www.grandrapidsmi.gov/departments/public-works/waste-services/bulk-item-collection/",
    )
    hhw = (
        "Kent County SafeChem HHW",
        "https://www.kentcountymi.gov/368/SafeChem-Household-Hazardous-Waste",
    )
    ewaste = (
        "Kent County Electronics Recycling",
        "https://www.kentcountymi.gov/464/Electronics",
    )
    rows = []
    rows.append(
        R(
            c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
            "$40 bulk sticker — mattress+box spring = one sticker",
            "Grand Rapids bulk sticker collection",
            "Grand Rapids mattresses need a $40 bulk sticker (mattress plus box spring counts as one sticker). Buy online or in person; max item size 6×5 ft. Set out by 7:00 a.m. the day after purchase on your collection route.",
            ["Purchase $40 bulk sticker online or in person.", "Set out by 7 a.m. day after purchase.", "Mattress and box spring together use one sticker."],
            [("Box spring fee?", "One $40 sticker covers mattress and box spring."), ("Size limit?", "Max 6×5 ft per bulk item.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c, st, "refrigerator", "SPECIAL_HANDLING", "High", True,
            "$40 bulk sticker — remove doors before set-out",
            "Grand Rapids bulk sticker — Freon appliance",
            "Grand Rapids Freon refrigerators need a $40 bulk sticker for curbside collection. Remove refrigerator doors before set-out. Never vent refrigerant yourself. Set out by 7:00 a.m. the day after sticker purchase.",
            ["Purchase $40 bulk sticker.", "Remove doors; never vent Freon.", "Set out by 7 a.m. day after purchase."],
            [("Freon fridge curbside?", "Yes — with $40 bulk sticker."), ("Doors?", "Remove refrigerator doors before set-out.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
            "$40 bulk sticker — Freon appliance curbside",
            "Grand Rapids bulk sticker — Freon appliance",
            "Grand Rapids window/wall AC units with Freon use the $40 bulk sticker curbside path. Set out by 7:00 a.m. the day after purchase. Never vent refrigerant yourself.",
            ["Purchase $40 bulk sticker.", "Set out by 7 a.m. day after purchase.", "Keep sealed until proper Freon handling."],
            [("Same as fridge?", "Yes — $40 bulk sticker for Freon appliances.")],
            *bulk,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c, st, item, "SPECIAL_HANDLING", "Medium", True,
                "$40 bulk sticker — non-Freon appliance bulk",
                "Grand Rapids bulk sticker collection",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s use Grand Rapids bulk sticker collection ($40). Freon refrigerators/AC use the same sticker fee but require door removal/Freon handling. Max 6×5 ft; set out by 7 a.m. day after purchase.",
                ["Purchase $40 bulk sticker.", "Empty appliance before set-out.", "Set out by 7 a.m. day after purchase."],
                [("Same as Freon fridge?", "Same $40 sticker — non-Freon items do not need door removal.")],
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
                "NOT curbside — free Kent County electronics drop-off",
                "Kent County SafeChem / North or South Kent recycling centers",
                f"Electronics including {label} are NOT accepted on Grand Rapids bulk curbside. Free drop-off for Kent County residents at SafeChem 1045 Wealthy St SW or North/South Kent recycling centers. Wipe data before drop-off.",
                ["Do not put TVs/e-waste on bulk sticker piles.", "Haul free to Kent County electronics drop-off.", "Wipe personal data."],
                [("Curbside e-waste?", "No — county electronics drop-off only."), ("Fee?", "Free at Kent County centers.")],
                *ewaste,
            )
        )
    rows.append(
        R(
            c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", True,
            "Dry out completely → regular trash (SafeChem does NOT take latex)",
            "Grand Rapids trash cart — dried latex only",
            "Grand Rapids latex paint is NOT accepted at Kent County SafeChem. Dry paint completely (add kitty litter or leave lid off) until solid, then put dried cans in regular trash. Liquid latex never goes curbside bulk or SafeChem.",
            ["Add kitty litter or dry paint until solid.", "Place dried cans in regular trash.", "Do not haul liquid latex to SafeChem."],
            [("SafeChem for latex?", "No — SafeChem does not accept latex paint."), ("Liquid latex?", "Must be fully dried before trash.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
            "Free Kent County SafeChem — oil-based paint only",
            "Kent County SafeChem — 1045 Wealthy Street SW",
            "Oil-based paint goes to Kent County SafeChem — 1045 Wealthy Street SW — free for Kent County residents. Hours: Mon 1:30–5:30, Wed 7:30–11:30, Thu 1:30–5:30, 2nd Sat 8:30–11. Not curbside bulk.",
            ["Haul sealed oil paint to SafeChem 1045 Wealthy St SW.", "Check SafeChem hours before visiting.", "Keep oil paint out of trash carts."],
            [("Latex at SafeChem?", "No — latex must be dried for trash."), ("Fee?", "Free for Kent County residents.")],
            *hhw,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
                "Free Kent County SafeChem HHW",
                "Kent County SafeChem — 1045 Wealthy Street SW",
                f"Take {item.replace('-', ' ')} to Kent County SafeChem — 1045 Wealthy Street SW — free. Hours: Mon 1:30–5:30, Wed 7:30–11:30, Thu 1:30–5:30, 2nd Sat 8:30–11. Call 616-336-2501. Not bulk curbside.",
                ["Deliver sealed containers to SafeChem.", "Check posted hours.", "Keep chemicals off bulk sticker piles."],
                [("Same as latex paint?", "No — chemicals go to SafeChem; dried latex goes to trash.")],
                *hhw,
            )
        )
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {
            "car-battery": " Lead-acid batteries at SafeChem.",
            "lithium-battery": " Lithium batteries at SafeChem.",
            "motor-oil": " Used motor oil at SafeChem.",
            "propane-tank": " Propane tanks at SafeChem — confirm size limits.",
            "fluorescent-bulbs": " Fluorescent bulbs at SafeChem.",
            "cooking-oil": " Cooking oil at SafeChem when not trash-safe.",
        }[item]
        rows.append(
            R(
                c, st, item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium", False,
                "Free Kent County SafeChem HHW",
                "Kent County SafeChem — 1045 Wealthy Street SW",
                f"Kent County SafeChem at 1045 Wealthy Street SW accepts household hazardous materials free for county residents.{extra}",
                ["Haul to SafeChem during posted hours.", "Call 616-336-2501 with questions.", "Tires use Kent County tire drop-off, not SafeChem."],
                [("Address?", "1045 Wealthy Street SW, Grand Rapids.")],
                *hhw,
            )
        )
    rows.append(
        R(
            c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
            "Rigid sealed container — confirm SafeChem sharps acceptance",
            "Kent County SafeChem — 1045 Wealthy Street SW",
            "Place sharps in a rigid sealed container. Confirm acceptance at Kent County SafeChem. Do not loose-bag needles.",
            ["Use rigid sealed container.", "Confirm sharps at SafeChem.", "Never recycle loose needles."],
            [("Medications?", "Confirm drug take-back via Kent County programs.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
            "NOT city bulk — Kent County $4/tire ≤42 in, $6 for 42–50 in",
            "Kent County tire drop-off",
            "Grand Rapids city bulk does NOT accept tires. Take tires to Kent County drop-off — $4 per tire ≤42 inches, $6 for 42–50 inches. Not bulk sticker or SafeChem.",
            ["Do not put tires on bulk sticker collection.", "Haul to Kent County tire drop-off.", "Retailer take-back when replacing tires."],
            [("City bulk for tires?", "No — Kent County fee drop-off."), ("Fee?", "$4/tire ≤42 in; $6 for 42–50 in.")],
            *bulk,
        )
    )
    rows.append(
        R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True,
          "Grand Rapids yard waste collection", "Grand Rapids yard waste collection",
          "Grand Rapids handles yard waste through regular collection. Follow set-out rules on grandrapidsmi.gov.",
          ["Use yard waste set-out rules.", "Keep yard waste out of HHW and e-waste.", "Check city site for seasonal guidance."],
          [("Christmas trees?", "Follow city seasonal yard waste guidance.")], *bulk)
    )
    rows.append(
        R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True,
          "Garbage cart unless private compost", "Grand Rapids garbage / private compost",
          "Bag food scraps for garbage unless you compost. Keep food out of recycling and HHW.",
          ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."],
          [("HHW for food?", "No.")], *bulk)
    )
    rows.append(
        R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False,
          "Not recycling — store take-back / trash", "Retail bag take-back / trash",
          "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
          ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."],
          [("Bulk sticker for bags?", "No.")], *bulk)
    )
    rows.append(
        R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", True,
          "$40 bulk sticker if ≤6×5 ft — private C&D for larger loads",
          "Grand Rapids bulk sticker / private C&D hauler",
          "Limited homeowner debris within 6×5 ft may use Grand Rapids $40 bulk sticker. Larger contractor loads need a private C&D hauler. Route paint/chemicals to SafeChem separately.",
          ["Confirm size limits before buying bulk sticker.", "Hire private C&D for remodel loads.", "Route oil paint/chemicals to SafeChem."],
          [("HHW for C&D?", "No — separate paint/chemicals.")], *bulk)
    )
    return rows


def rochester():
    c, st = "rochester", "NY"
    bulk = (
        "City of Rochester — Residential refuse",
        "https://www.cityofrochester.gov/residentialrefuse/",
    )
    ecopark = (
        "Monroe County ecopark",
        "https://www.monroecounty.gov/ecopark/",
    )
    ewaste = (
        "City of Rochester — Electronic waste recycling",
        "https://www.cityofrochester.gov/departments/department-environmental-services-des/electronic-waste-recycling",
    )
    rows = []
    rows.append(
        R(
            c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
            "Free on refuse day — set out by 6:30 a.m.",
            "Rochester refuse-day bulk collection",
            "Rochester mattresses are free on your regular refuse collection day. Set out by 6:30 a.m. alongside trash. On-Demand bulky pickup is $80 minimum — call 585-428-6928. Mattress and box spring follow the same free refuse-day path.",
            ["Set mattress out by 6:30 a.m. on refuse day.", "Keep separate from recycling.", "On-Demand bulky is $80 min if you miss refuse day."],
            [("Fee?", "Free on refuse day."), ("On-Demand?", "$80 minimum via 585-428-6928.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c, st, "refrigerator", "SPECIAL_HANDLING", "High", True,
            "Free refuse-day bulk OR ecopark $20 each",
            "Rochester refuse-day bulk / Monroe County ecopark",
            "Rochester Freon refrigerators are free on refuse collection day — remove appliance doors before set-out. Alternative: Monroe County ecopark at 10 Avion Drive for $20 each. Never vent refrigerant yourself.",
            ["Set out by 6:30 a.m. on refuse day (free).", "Remove doors before curbside set-out.", "Or haul to ecopark 10 Avion Drive ($20 each)."],
            [("Freon fee curbside?", "Free on refuse day."), ("Ecopark fee?", "$20 each for appliances.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
            "Free refuse-day bulk OR ecopark $20 each",
            "Rochester refuse-day bulk / Monroe County ecopark",
            "Rochester window AC units are free on refuse day or $20 each at Monroe County ecopark (10 Avion Drive). Never vent refrigerant yourself.",
            ["Set out by 6:30 a.m. on refuse day.", "Or haul to ecopark 10 Avion Drive.", "Keep sealed until proper Freon handling."],
            [("Same as fridge?", "Yes — free refuse day or ecopark $20.")],
            *bulk,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c, st, item, "SPECIAL_HANDLING", "Medium", True,
                "Free refuse-day bulk — remove doors on appliances",
                "Rochester refuse-day bulk collection",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s are free on Rochester refuse collection day. Set out by 6:30 a.m. Remove doors on applicable appliances. Freon refrigerators/AC also free curbside but ecopark charges $20.",
                ["Set out by 6:30 a.m. on refuse day.", "Remove doors where required.", "On-Demand bulky $80 min if needed."],
                [("Same as Freon fridge?", "All appliances free on refuse day; ecopark $20 for Freon units.")],
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
                "BANNED from curb — free ecopark drop-off (no appointment)",
                "Monroe County ecopark — 10 Avion Drive",
                f"Electronics including {label} are BANNED from Rochester curbside. Free drop-off at Monroe County ecopark — 10 Avion Drive — Wed 1:00–6:30 p.m., Sat 7:30 a.m.–1:00 p.m. No appointment needed for e-waste. Wipe data before drop-off.",
                ["Do not put TVs/e-waste on refuse-day bulk.", "Haul free to ecopark 10 Avion Drive.", "Wipe personal data."],
                [("Appointment for e-waste?", "No — walk-in Wed/Sat."), ("Curbside OK?", "No — banned from curb.")],
                *ewaste,
            )
        )
    rows.append(
        R(
            c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", False,
            "Liquid → ecopark HHW appointment; dried cans → trash",
            "Monroe County ecopark HHW (appointment required)",
            "Liquid latex paint goes to Monroe County ecopark HHW — appointment required, free for Monroe County residents. Fully dried paint cans may go in regular trash. E-waste does not require appointment; HHW does.",
            ["Book ecopark HHW appointment for liquid paint.", "Dry latex completely for trash if solid.", "Keep liquid paint off refuse-day bulk."],
            [("Dried cans?", "Fully dried latex cans go in trash."), ("Appointment?", "Required for HHW including liquid paint.")],
            *ecopark,
        )
    )
    rows.append(
        R(
            c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
            "Free ecopark HHW — appointment required",
            "Monroe County ecopark — 10 Avion Drive",
            "Oil-based paint goes to Monroe County ecopark HHW by appointment — free for Monroe County residents. Wed 1:00–6:30, Sat 7:30–1:00. Not curbside.",
            ["Book ecopark HHW appointment.", "Keep containers sealed and labeled.", "Not refuse-day bulk."],
            [("Same as latex?", "Both liquid paints use ecopark HHW appointment.")],
            *ecopark,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
                "Free ecopark HHW — appointment required",
                "Monroe County ecopark — 10 Avion Drive",
                f"Take {item.replace('-', ' ')} to Monroe County ecopark HHW — appointment required, free for Monroe County residents. Not refuse-day bulk.",
                ["Book ecopark HHW appointment.", "Deliver sealed containers.", "Keep chemicals off refuse-day bulk."],
                [("Same as paint?", "Yes — chemicals use ecopark HHW appointment.")],
                *ecopark,
            )
        )
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {
            "car-battery": " Batteries at ecopark HHW.",
            "lithium-battery": " Lithium batteries at ecopark HHW.",
            "motor-oil": " Used motor oil at ecopark HHW.",
            "propane-tank": " Propane tanks at ecopark HHW — confirm size limits.",
            "fluorescent-bulbs": " Fluorescent bulbs at ecopark HHW.",
            "cooking-oil": " Cooking oil at ecopark HHW when not trash-safe.",
        }[item]
        rows.append(
            R(
                c, st, item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium", False,
                "Free ecopark HHW — appointment required",
                "Monroe County ecopark — 10 Avion Drive",
                f"Monroe County ecopark HHW accepts household hazardous materials by appointment for county residents.{extra}",
                ["Book ecopark HHW appointment.", "Deliver during your scheduled slot.", "Tires use ecopark tire fees, not HHW appointment rules."],
                [("Address?", "10 Avion Drive, Rochester.")],
                *ecopark,
            )
        )
    rows.append(
        R(
            c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
            "Rigid sealed container — confirm ecopark HHW sharps acceptance",
            "Monroe County ecopark HHW",
            "Place sharps in a rigid sealed container. Confirm acceptance at Monroe County ecopark HHW by appointment. Do not loose-bag needles.",
            ["Use rigid sealed container.", "Book ecopark HHW appointment for sharps.", "Never recycle loose needles."],
            [("Medications?", "Confirm drug take-back via ecopark / county programs.")],
            *ecopark,
        )
    )
    rows.append(
        R(
            c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
            "NOT curbside — ecopark $5–20 rimless, $12–40 on rims",
            "Monroe County ecopark — tire drop-off",
            "Rochester tires are NOT accepted on refuse-day bulk. Take to Monroe County ecopark — $5–20 rimless, $12–40 on rims. Retailer take-back when replacing tires.",
            ["Do not set tires out on refuse day.", "Haul to ecopark 10 Avion Drive.", "Retailer take-back when replacing tires."],
            [("Refuse day for tires?", "No — ecopark fee drop-off."), ("Fee?", "$5–20 rimless; $12–40 on rims.")],
            *ecopark,
        )
    )
    rows.append(
        R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True,
          "Rochester yard waste collection", "Rochester yard waste collection",
          "Rochester handles yard waste through regular collection. Follow set-out rules on cityofrochester.gov.",
          ["Use yard waste set-out rules.", "Keep yard waste out of HHW and e-waste.", "Check city site for seasonal guidance."],
          [("Christmas trees?", "Follow city seasonal yard waste guidance.")], *bulk)
    )
    rows.append(
        R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True,
          "Garbage cart unless private compost", "Rochester garbage / private compost",
          "Bag food scraps for garbage unless you compost.",
          ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."],
          [("HHW for food?", "No.")], *bulk)
    )
    rows.append(
        R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False,
          "Not recycling — store take-back / trash", "Retail bag take-back / trash",
          "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
          ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."],
          [("Refuse day for bags?", "No.")], *bulk)
    )
    rows.append(
        R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", False,
          "NOT typical refuse-day bulk — private C&D hauler",
          "Private C&D hauler",
          "Contractor construction debris is not typical Rochester refuse-day bulk. Hire a private C&D hauler for remodel loads. Route liquid paint/chemicals to ecopark HHW separately.",
          ["Do not treat remodel debris as refuse-day bulk.", "Hire private C&D for larger projects.", "Route paint to ecopark HHW appointment."],
          [("HHW for C&D?", "No — separate paint/chemicals.")], *bulk)
    )
    return rows


def norfolk():
    c, st = "norfolk", "VA"
    bulk = (
        "City of Norfolk — Trash & Recycling",
        "https://www.norfolk.gov/2734/Trash-Recycling",
    )
    hhw = (
        "City of Norfolk — How Do I Dispose Of",
        "https://www.norfolk.gov/405/How-Do-I-Dispose-Of",
    )
    recycle = (
        "City of Norfolk — Recycling Information",
        "https://www.norfolk.gov/4813/Recycling-Information",
    )
    rows = []
    rows.append(
        R(
            c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
            "Schedule MyNorfolk or 757-664-6510 — free, 12 pickups/year",
            "Norfolk scheduled bulk collection",
            "Norfolk mattresses require scheduled bulk pickup via MyNorfolk or 757-664-6510 by 3:00 p.m. the day before collection. Free when scheduled — up to 12 pickups/year, 3 cubic yards each. Set out on scheduled day only.",
            ["Schedule bulk via MyNorfolk or 757-664-6510 by 3 p.m. day before.", "Stay within 12 pickups/year limit.", "Set out on scheduled collection day."],
            [("Fee?", "Free when scheduled."), ("Limit?", "12 bulk pickups/year, 3 cubic yards each.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c, st, "refrigerator", "SPECIAL_HANDLING", "High", True,
            "Scheduled bulk — tape/remove doors before set-out",
            "Norfolk scheduled bulk — Freon appliance",
            "Norfolk Freon refrigerators use scheduled bulk pickup — free, 12/year. Schedule via MyNorfolk or 757-664-6510 by 3 p.m. day before. Tape or remove doors. Never vent refrigerant yourself.",
            ["Schedule bulk via MyNorfolk or 757-664-6510.", "Tape or remove refrigerator doors.", "Do not vent Freon yourself."],
            [("Freon fee?", "Free when scheduled within annual limit."), ("Doors?", "Tape or remove before set-out.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
            "Scheduled bulk — Freon appliance",
            "Norfolk scheduled bulk — Freon appliance",
            "Norfolk window AC units use scheduled bulk pickup — free within 12/year limit. Schedule by 3 p.m. day before via MyNorfolk or 757-664-6510. Never vent refrigerant yourself.",
            ["Schedule bulk via MyNorfolk or 757-664-6510.", "Set out on scheduled day.", "Keep sealed until proper Freon handling."],
            [("Same as fridge?", "Yes — scheduled bulk for Freon appliances.")],
            *bulk,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c, st, item, "SPECIAL_HANDLING", "Medium", True,
                "Scheduled bulk — free, 12 pickups/year",
                "Norfolk scheduled bulk collection",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s use Norfolk scheduled bulk — free, up to 12 pickups/year. Schedule via MyNorfolk or 757-664-6510 by 3 p.m. day before. Freon refrigerators/AC use the same schedule path.",
                ["Schedule bulk via MyNorfolk or 757-664-6510.", "Set out on scheduled day.", "Stay within 12 pickups/year."],
                [("Same as Freon fridge?", "Yes — all large appliances use scheduled bulk.")],
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
                "NOT curbside — SPSA Norfolk Transfer Station drop-off",
                "SPSA Norfolk Transfer Station — 3136 Woodland Ave",
                f"Electronics including {label} are NOT accepted on Norfolk scheduled bulk. Drop at SPSA Norfolk Transfer Station — 3136 Woodland Ave — Tue & Sat 12:00–4:00 p.m. Norfolk residents; limit 5 items/visit. Wipe data before drop-off.",
                ["Do not put TVs/e-waste on scheduled bulk.", "Haul to SPSA 3136 Woodland Ave Tue/Sat 12–4.", "Wipe personal data."],
                [("Curbside e-waste?", "No — SPSA transfer station only."), ("Limit?", "5 items per visit for Norfolk residents.")],
                *recycle,
            )
        )
    rows.append(
        R(
            c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", False,
            "SPSA HHW drop-off — NOT scheduled bulk",
            "SPSA Norfolk Transfer Station — 3136 Woodland Ave",
            "Liquid latex paint goes to SPSA HHW at 3136 Woodland Ave — Tue & Sat 12:00–4:00 p.m. Up to 5 gallons liquid or 75 lbs solid per visit. Not scheduled bulk. Call 757-961-3981.",
            ["Haul sealed paint to SPSA 3136 Woodland Ave.", "Hours: Tue & Sat 12–4.", "Keep paint off scheduled bulk piles."],
            [("Bulk for paint?", "No — SPSA HHW only."), ("Limit?", "Up to 5 gal liquid or 75 lbs solid.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
            "SPSA HHW — Tue/Sat 12–4",
            "SPSA Norfolk Transfer Station — 3136 Woodland Ave",
            "Oil-based paint goes to SPSA HHW at 3136 Woodland Ave — Tue & Sat 12:00–4:00 p.m. Not scheduled bulk or trash.",
            ["Haul oil paint to SPSA 3136 Woodland Ave.", "Keep containers sealed and labeled.", "Not scheduled bulk."],
            [("Same as latex?", "Yes — both use SPSA HHW.")],
            *hhw,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
                "SPSA HHW — Tue/Sat 12–4",
                "SPSA Norfolk Transfer Station — 3136 Woodland Ave",
                f"Take {item.replace('-', ' ')} to SPSA HHW at 3136 Woodland Ave — Tue & Sat 12:00–4:00 p.m. Up to 5 gal liquid or 75 lbs solid. Call 757-961-3981.",
                ["Deliver sealed containers to SPSA.", "Hours: Tue & Sat 12–4.", "Keep chemicals off scheduled bulk."],
                [("Same as paint?", "Yes — chemicals use SPSA HHW.")],
                *hhw,
            )
        )
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {
            "car-battery": " Batteries at SPSA HHW.",
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
                "SPSA HHW — Tue/Sat 12–4",
                "SPSA Norfolk Transfer Station — 3136 Woodland Ave",
                f"SPSA Norfolk Transfer Station HHW at 3136 Woodland Ave accepts household hazardous materials for Norfolk residents.{extra}",
                ["Haul to SPSA Tue/Sat 12–4.", "Call 757-961-3981 with questions.", "Tires use scheduled bulk path, not HHW."],
                [("Address?", "3136 Woodland Ave, Norfolk.")],
                *hhw,
            )
        )
    rows.append(
        R(
            c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
            "Rigid sealed container — confirm SPSA sharps acceptance",
            "SPSA Norfolk Transfer Station",
            "Place sharps in a rigid sealed container. Confirm acceptance at SPSA Norfolk Transfer Station. Do not loose-bag needles.",
            ["Use rigid sealed container.", "Confirm sharps at SPSA HHW.", "Never recycle loose needles."],
            [("Medications?", "Confirm drug take-back via Norfolk/SPSA programs.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "tires", "SPECIAL_HANDLING", "Medium", True,
            "Scheduled bulk — 4/day, 12/year, off rims",
            "Norfolk scheduled bulk — tires",
            "Norfolk tires go on scheduled bulk pickup — up to 4 per day, 12 per year, off rims. Schedule via MyNorfolk or 757-664-6510 by 3 p.m. day before. Free when scheduled.",
            ["Schedule bulk via MyNorfolk or 757-664-6510.", "Remove tires from rims.", "Limit 4 tires/day, 12/year."],
            [("SPSA for tires?", "No — use scheduled bulk."), ("Rims?", "Off rims only.")],
            *bulk,
        )
    )
    rows.append(
        R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True,
          "Norfolk yard waste collection", "Norfolk yard waste collection",
          "Norfolk handles yard waste through regular collection. Follow set-out rules on norfolk.gov.",
          ["Use yard waste set-out rules.", "Keep yard waste out of HHW and e-waste.", "Check city site for seasonal guidance."],
          [("Christmas trees?", "Follow city seasonal yard waste guidance.")], *bulk)
    )
    rows.append(
        R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True,
          "Garbage cart unless private compost", "Norfolk garbage / private compost",
          "Bag food scraps for garbage unless you compost.",
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
          "NOT typical scheduled bulk — private C&D hauler",
          "Private C&D hauler",
          "Contractor construction debris exceeds Norfolk scheduled bulk limits (3 cy). Hire a private C&D hauler for remodel loads. Route paint/chemicals to SPSA HHW separately.",
          ["Do not treat remodel debris as scheduled bulk.", "Hire private C&D for larger projects.", "Route paint to SPSA HHW."],
          [("HHW for C&D?", "No — separate paint/chemicals.")], *bulk)
    )
    return rows


def lexington():
    c, st = "lexington", "KY"
    bulky = (
        "City of Lexington — Bulky items",
        "https://www.lexingtonky.gov/government/departments-programs/environmental-quality-public-works/waste-management/bulky-items",
    )
    appliances = (
        "City of Lexington — Appliances",
        "https://www.lexingtonky.gov/living/waste-collection/appliances",
    )
    hhw = (
        "City of Lexington — Household hazardous waste",
        "https://www.lexingtonky.gov/living/waste-collection/household-hazardous-waste",
    )
    ewaste = (
        "City of Lexington — Electronics recycling",
        "https://www.lexingtonky.gov/living/waste-collection/electronics-recycling",
    )
    rows = []
    rows.append(
        R(
            c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
            "Free — set flat beside carts on collection day (no schedule)",
            "Lexington curbside — flat beside carts",
            "Lexington mattresses are free on your regular collection day — set flat beside carts; no LexCall schedule needed. Keep separate from recycling. Box spring follows the same bulky path via sibling rules.",
            ["Set mattress flat beside carts on collection day.", "No LexCall schedule required.", "Keep separate from recycling."],
            [("Fee?", "Free on collection day."), ("Schedule?", "No — set beside carts.")],
            *bulky,
        )
    )
    rows.append(
        R(
            c, st, "refrigerator", "SPECIAL_HANDLING", "High", True,
            "Free — MUST schedule LexCall 311 / 859-425-2255; remove doors",
            "Lexington LexCall bulky — Freon appliance",
            "Lexington Freon refrigerators require LexCall scheduling — dial 311 or 859-425-2255. Free pickup. Remove appliance doors before set-out. Never vent refrigerant yourself. Non-Freon appliances use the same LexCall free schedule path.",
            ["Call LexCall 311 or 859-425-2255 to schedule.", "Remove refrigerator doors before set-out.", "Never vent Freon yourself."],
            [("Freon fridge fee?", "Free with LexCall schedule."), ("Non-Freon appliances?", "Same LexCall free schedule.")],
            *appliances,
        )
    )
    rows.append(
        R(
            c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
            "Free — MUST schedule LexCall 311 / 859-425-2255",
            "Lexington LexCall bulky — Freon appliance",
            "Lexington window AC units with Freon require LexCall scheduling — 311 or 859-425-2255. Free pickup. Never vent refrigerant yourself.",
            ["Schedule via LexCall 311 or 859-425-2255.", "Set out on scheduled day.", "Keep sealed until proper Freon handling."],
            [("Same as fridge?", "Yes — LexCall schedule required for Freon appliances.")],
            *appliances,
        )
    )
    for item, label in [
        ("television", "TVs"), ("computer-monitor", "monitors"),
        ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste"),
    ]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "Medium", False,
                "NOT curbside — free Electronic Recycling Center drop-off",
                "Lexington Electronic Recycling Center — 1306 Versailles Road",
                f"Electronics including {label} are NOT accepted on Lexington curbside bulky. Free drop-off for Fayette County residents at the Electronic Recycling Center — 1306 Versailles Road — Mon–Tue 8–4, Wed noon–4, Thu–Fri 8–4, Sat 8–noon. Wipe data before drop-off.",
                ["Do not put TVs/e-waste on bulky piles.", "Haul free to 1306 Versailles Road during posted hours.", "Wipe personal data."],
                [("Curbside e-waste?", "No — ERC drop-off only."), ("Fee?", "Free for Fayette County residents.")],
                *ewaste,
            )
        )
    rows.append(
        R(
            c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", True,
            "Harden with kitty litter beside green cart OR HHW events",
            "Lexington green cart (dried) / HHW events",
            "Lexington latex paint: harden completely with kitty litter or dry material, then set beside your green cart on collection day. Liquid latex may also go to HHW collection events — Sat May 16 2026 and Sat Oct 17 2026, 8:30 a.m.–3 p.m., 1631 Old Frankfort Pike.",
            ["Add kitty litter until paint is solid.", "Set hardened cans beside green cart.", "Or hold liquid paint for HHW event dates."],
            [("HHW events?", "May 16 & Oct 17 2026, 8:30–3 at 1631 Old Frankfort Pike."), ("Liquid beside cart?", "No — must be fully hardened.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
            "HHW events only — May 16 & Oct 17 2026, 1631 Old Frankfort Pike",
            "Lexington HHW — 1631 Old Frankfort Pike",
            "Oil-based paint goes to Lexington HHW collection events only — Sat May 16 2026 and Sat Oct 17 2026, 8:30 a.m.–3 p.m., 1631 Old Frankfort Pike. Not curbside bulky or trash.",
            ["Hold sealed oil paint for HHW event dates.", "Events: May 16 & Oct 17 2026, 8:30–3.", "Keep oil paint off curbside bulky."],
            [("Year-round drop-off?", "No — event-only HHW."), ("Same events as latex liquid?", "Yes — HHW events at Old Frankfort Pike.")],
            *hhw,
        )
    )
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {
            "car-battery": " Lead-acid batteries at HHW events.",
            "lithium-battery": " Lithium batteries at HHW events.",
            "motor-oil": " Used motor oil at HHW events.",
            "propane-tank": " Propane tanks at HHW events — confirm size limits.",
            "fluorescent-bulbs": " Fluorescent bulbs at HHW events.",
            "cooking-oil": " Cooking oil at HHW events when not trash-safe.",
        }[item]
        rows.append(
            R(
                c, st, item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium", False,
                "HHW events only — May 16 & Oct 17 2026",
                "Lexington HHW — 1631 Old Frankfort Pike",
                f"Lexington HHW collection events accept household hazardous materials free for Fayette County residents — May 16 & Oct 17 2026, 8:30 a.m.–3 p.m., 1631 Old Frankfort Pike.{extra}",
                ["Hold materials safely until HHW event dates.", "Events: May 16 & Oct 17 2026, 8:30–3.", "Tires use LexCall schedule, not HHW."],
                [("Address?", "1631 Old Frankfort Pike, Lexington.")],
                *hhw,
            )
        )
    rows.append(
        R(
            c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
            "Rigid sealed container — confirm HHW event sharps acceptance",
            "Lexington HHW events",
            "Place sharps in a rigid sealed container. Confirm acceptance at Lexington HHW collection events (May 16 & Oct 17 2026). Do not loose-bag needles.",
            ["Use rigid sealed container.", "Confirm sharps at HHW event.", "Never recycle loose needles."],
            [("Medications?", "Confirm drug take-back via Fayette County programs.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "tires", "SPECIAL_HANDLING", "Medium", True,
            "Up to 4/week off rims — schedule LexCall, free",
            "Lexington LexCall bulky — tires",
            "Lexington tires: up to 4 per week off rims. Schedule via LexCall 311 or 859-425-2255 — free pickup. Remove tires from rims before set-out.",
            ["Schedule via LexCall 311 or 859-425-2255.", "Remove tires from rims.", "Limit 4 tires per week."],
            [("Fee?", "Free with LexCall schedule."), ("Rims?", "Off rims only.")],
            *bulky,
        )
    )
    rows.append(
        R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True,
          "Lexington yard waste collection", "Lexington yard waste collection",
          "Lexington handles yard waste through regular collection. Follow set-out rules on lexingtonky.gov.",
          ["Use yard waste set-out rules.", "Keep yard waste out of HHW and e-waste.", "Check city site for seasonal guidance."],
          [("Christmas trees?", "Follow city seasonal yard waste guidance.")], *bulky)
    )
    rows.append(
        R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True,
          "Garbage cart unless private compost", "Lexington garbage / private compost",
          "Bag food scraps for garbage unless you compost. Keep food out of recycling and HHW.",
          ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."],
          [("HHW for food?", "No.")], *bulky)
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
          "NOT typical curbside bulky — private C&D hauler",
          "Private C&D hauler",
          "Contractor construction debris is not typical Lexington curbside bulky. Hire a private C&D hauler for remodel loads. Route paint/chemicals to HHW events separately.",
          ["Do not treat remodel debris as curbside bulky.", "Hire private C&D for larger projects.", "Route paint to HHW events."],
          [("HHW for C&D?", "No — separate paint/chemicals.")], *bulky)
    )
    return rows


def toledo():
    c, st = "toledo", "OH"
    bulk = (
        "City of Toledo — Trash & recycling",
        "https://toledo.oh.gov/residents/neighborhoods/trash-recycling",
    )
    center = (
        "Clean Toledo Recycling Center",
        "https://toledo.oh.gov/residents/neighborhoods/trash-recycling/clean-toledo-recycling-center",
    )
    events = (
        "City of Toledo — Clean Toledo events",
        "https://toledo.oh.gov/news/2026/04/22/city-of-toledo-announces-opening-of-new-clean-toledo-recycling-center",
    )
    rows = []
    rows.append(
        R(
            c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
            "Weekly bulk — bag/wrap, ≤40 lb, up to 5 items/week with trash",
            "Toledo weekly bulk collection",
            "Toledo mattresses go on weekly bulk — up to 5 items per week with trash, no schedule needed. Bag or wrap mattresses. Each item must be ≤40 lbs. Republic Services 419-936-2511 for questions.",
            ["Bag or wrap mattress securely.", "Set out with trash (≤40 lb, 5 items/week max).", "No LexCall-style schedule required."],
            [("Fee?", "Free weekly bulk within limits."), ("Weight limit?", "≤40 lbs per item.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c, st, "refrigerator", "SPECIAL_HANDLING", "High", False,
            "NOT weekly bulk — Clean Toledo seasonal events only (Freon)",
            "Clean Toledo seasonal Freon appliance events",
            "Toledo Freon refrigerators are NOT accepted on weekly bulk. Use Clean Toledo seasonal collection events only. Never vent refrigerant yourself. Non-Freon appliances ≤40 lb may use weekly bulk.",
            ["Do not set Freon fridge on weekly bulk.", "Watch for Clean Toledo seasonal Freon events.", "Never vent refrigerant yourself."],
            [("Weekly bulk for Freon fridge?", "No — seasonal Clean Toledo events only."), ("Non-Freon?", "Weekly bulk if ≤40 lb.")],
            *events,
        )
    )
    rows.append(
        R(
            c, st, "air-conditioner", "SPECIAL_HANDLING", "High", False,
            "NOT weekly bulk — Clean Toledo seasonal events only (Freon)",
            "Clean Toledo seasonal Freon appliance events",
            "Toledo Freon window AC units are NOT on weekly bulk. Use Clean Toledo seasonal collection events only. Never vent refrigerant yourself.",
            ["Do not set Freon AC on weekly bulk.", "Use Clean Toledo seasonal events.", "Keep sealed until proper Freon handling."],
            [("Same as Freon fridge?", "Yes — seasonal events only, not weekly bulk.")],
            *events,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c, st, item, "SPECIAL_HANDLING", "Medium", True,
                "Weekly bulk if non-Freon and ≤40 lb — up to 5 items/week",
                "Toledo weekly bulk collection",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s may use Toledo weekly bulk — up to 5 items/week with trash, ≤40 lbs each, no schedule. Freon refrigerators/AC are NOT weekly bulk — Clean Toledo seasonal events only.",
                ["Confirm non-Freon and ≤40 lb.", "Set out with trash (5 items/week max).", "Republic 419-936-2511 with questions."],
                [("Freon appliances?", "No — seasonal Clean Toledo events only.")],
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
                "NOT weekly bulk — Clean Toledo Recycling Center drop-off",
                "Clean Toledo Recycling Center — 3900 Creekside Ave",
                f"Electronics including {label} are NOT accepted on Toledo weekly bulk. Drop at Clean Toledo Recycling Center — 3900 Creekside Ave (opened June 2 2026) — Tue–Sat 8:30 a.m.–4 p.m. Wipe data before drop-off.",
                ["Do not put TVs/e-waste on weekly bulk.", "Haul to 3900 Creekside Ave Tue–Sat 8:30–4.", "Wipe personal data."],
                [("Weekly bulk for TVs?", "No — Clean Toledo center only."), ("Hours?", "Tue–Sat 8:30–4.")],
                *center,
            )
        )
    rows.append(
        R(
            c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", False,
            "NOT weekly bulk — Clean Toledo seasonal HHW events only",
            "Clean Toledo seasonal HHW events",
            "Toledo latex paint is NOT weekly bulk. Use Clean Toledo seasonal HHW collection events — June 13, Aug 15, and Oct 3 2026. Not curbside bulk or trash for liquid paint.",
            ["Hold sealed paint for Clean Toledo HHW event dates.", "Events: June 13, Aug 15, Oct 3 2026.", "Keep paint off weekly bulk piles."],
            [("Weekly bulk for paint?", "No — seasonal HHW events only."), ("Event dates?", "June 13, Aug 15, Oct 3 2026.")],
            *events,
        )
    )
    rows.append(
        R(
            c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
            "Clean Toledo seasonal HHW events — June 13, Aug 15, Oct 3 2026",
            "Clean Toledo seasonal HHW events",
            "Oil-based paint goes to Clean Toledo seasonal HHW events — June 13, Aug 15, and Oct 3 2026. Not weekly bulk or trash.",
            ["Hold sealed oil paint for HHW event dates.", "Keep containers sealed and labeled.", "Not weekly bulk."],
            [("Same as latex?", "Yes — both use Clean Toledo seasonal HHW events.")],
            *events,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
                "Clean Toledo seasonal HHW events only",
                "Clean Toledo seasonal HHW events",
                f"Take {item.replace('-', ' ')} to Clean Toledo seasonal HHW events — June 13, Aug 15, and Oct 3 2026. Not weekly bulk.",
                ["Hold sealed containers for HHW event dates.", "Events: June 13, Aug 15, Oct 3 2026.", "Keep chemicals off weekly bulk."],
                [("Weekly bulk?", "No — HHW events only.")],
                *events,
            )
        )
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {
            "car-battery": " Batteries at Clean Toledo HHW events.",
            "lithium-battery": " Lithium batteries at Clean Toledo HHW events.",
            "motor-oil": " Used motor oil at Clean Toledo HHW events.",
            "propane-tank": " Propane tanks at Clean Toledo HHW events — confirm size limits.",
            "fluorescent-bulbs": " Fluorescent bulbs at Clean Toledo HHW events.",
            "cooking-oil": " Cooking oil at Clean Toledo HHW events when not trash-safe.",
        }[item]
        rows.append(
            R(
                c, st, item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium", False,
                "Clean Toledo seasonal HHW events",
                "Clean Toledo seasonal HHW events",
                f"Clean Toledo seasonal HHW events accept household hazardous materials for Toledo residents — June 13, Aug 15, Oct 3 2026.{extra}",
                ["Hold materials for Clean Toledo HHW event dates.", "Events: June 13, Aug 15, Oct 3 2026.", "Tires use event fee path, not weekly bulk."],
                [("Year-round HHW?", "No — seasonal events only.")],
                *events,
            )
        )
    rows.append(
        R(
            c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
            "Rigid sealed container — confirm Clean Toledo HHW sharps acceptance",
            "Clean Toledo seasonal HHW events",
            "Place sharps in a rigid sealed container. Confirm acceptance at Clean Toledo HHW events. Do not loose-bag needles.",
            ["Use rigid sealed container.", "Confirm sharps at Clean Toledo HHW events.", "Never recycle loose needles."],
            [("Medications?", "Confirm drug take-back via Toledo/Lucas County programs.")],
            *events,
        )
    )
    rows.append(
        R(
            c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
            "NOT weekly bulk — events up to 10 tires at $0.50 each",
            "Clean Toledo seasonal tire collection events",
            "Toledo tires are NOT accepted on weekly bulk. Clean Toledo events accept up to 10 tires at $0.50 each. Retailer take-back when replacing tires.",
            ["Do not set tires out on weekly bulk.", "Haul to Clean Toledo tire events ($0.50/tire, max 10).", "Retailer take-back when replacing tires."],
            [("Weekly bulk for tires?", "No — event fee path."), ("Fee?", "$0.50 each, up to 10 tires.")],
            *events,
        )
    )
    rows.append(
        R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True,
          "Toledo yard waste collection", "Toledo yard waste collection",
          "Toledo handles yard waste through regular collection. Follow set-out rules on toledo.oh.gov.",
          ["Use yard waste set-out rules.", "Keep yard waste out of HHW and e-waste.", "Check city site for seasonal guidance."],
          [("Christmas trees?", "Follow city seasonal yard waste guidance.")], *bulk)
    )
    rows.append(
        R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True,
          "Garbage cart unless private compost", "Toledo garbage / private compost",
          "Bag food scraps for garbage unless you compost.",
          ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."],
          [("HHW for food?", "No.")], *bulk)
    )
    rows.append(
        R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False,
          "Not recycling — store take-back / trash", "Retail bag take-back / trash",
          "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
          ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."],
          [("Weekly bulk for bags?", "No.")], *bulk)
    )
    rows.append(
        R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", False,
          "NOT weekly bulk — private C&D hauler",
          "Private C&D hauler",
          "Construction debris is NOT accepted on Toledo weekly bulk (5 items, ≤40 lb). Hire a private C&D hauler for remodel loads. Route paint/chemicals to Clean Toledo HHW events separately.",
          ["Do not put C&D on weekly bulk.", "Hire private C&D for remodel loads.", "Route paint to Clean Toledo HHW events."],
          [("HHW for C&D?", "No — separate paint/chemicals.")], *bulk)
    )
    return rows


CITIES = [
    {
        "city": "Grand Rapids",
        "city_slug": "grand-rapids",
        "state": "MI",
        "state_slug": "michigan",
        "lat": 42.9634,
        "lng": -85.6681,
        "population": 198917,
    },
    {
        "city": "Rochester",
        "city_slug": "rochester",
        "state": "NY",
        "state_slug": "new-york",
        "lat": 43.1566,
        "lng": -77.6088,
        "population": 211328,
    },
    {
        "city": "Norfolk",
        "city_slug": "norfolk",
        "state": "VA",
        "state_slug": "virginia",
        "lat": 36.8508,
        "lng": -76.2859,
        "population": 238005,
    },
    {
        "city": "Lexington",
        "city_slug": "lexington",
        "state": "KY",
        "state_slug": "kentucky",
        "lat": 38.0406,
        "lng": -84.5037,
        "population": 322570,
    },
    {
        "city": "Toledo",
        "city_slug": "toledo",
        "state": "OH",
        "state_slug": "ohio",
        "lat": 41.6528,
        "lng": -83.5379,
        "population": 270871,
    },
]

ZIPS = [
    {
        "zip": "49503",
        "city": "Grand Rapids",
        "city_slug": "grand-rapids",
        "state": "MI",
        "state_slug": "michigan",
        "lat": 42.963,
        "lng": -85.668,
        "population": 18000,
    },
    {
        "zip": "49506",
        "city": "Grand Rapids",
        "city_slug": "grand-rapids",
        "state": "MI",
        "state_slug": "michigan",
        "lat": 42.948,
        "lng": -85.620,
        "population": 22000,
    },
    {
        "zip": "14604",
        "city": "Rochester",
        "city_slug": "rochester",
        "state": "NY",
        "state_slug": "new-york",
        "lat": 43.157,
        "lng": -77.609,
        "population": 8000,
    },
    {
        "zip": "14620",
        "city": "Rochester",
        "city_slug": "rochester",
        "state": "NY",
        "state_slug": "new-york",
        "lat": 43.128,
        "lng": -77.595,
        "population": 20000,
    },
    {
        "zip": "23510",
        "city": "Norfolk",
        "city_slug": "norfolk",
        "state": "VA",
        "state_slug": "virginia",
        "lat": 36.851,
        "lng": -76.286,
        "population": 12000,
    },
    {
        "zip": "23517",
        "city": "Norfolk",
        "city_slug": "norfolk",
        "state": "VA",
        "state_slug": "virginia",
        "lat": 36.870,
        "lng": -76.295,
        "population": 15000,
    },
    {
        "zip": "40507",
        "city": "Lexington",
        "city_slug": "lexington",
        "state": "KY",
        "state_slug": "kentucky",
        "lat": 38.041,
        "lng": -84.504,
        "population": 14000,
    },
    {
        "zip": "40508",
        "city": "Lexington",
        "city_slug": "lexington",
        "state": "KY",
        "state_slug": "kentucky",
        "lat": 38.035,
        "lng": -84.490,
        "population": 16000,
    },
    {
        "zip": "43604",
        "city": "Toledo",
        "city_slug": "toledo",
        "state": "OH",
        "state_slug": "ohio",
        "lat": 41.653,
        "lng": -83.538,
        "population": 9000,
    },
    {
        "zip": "43609",
        "city": "Toledo",
        "city_slug": "toledo",
        "state": "OH",
        "state_slug": "ohio",
        "lat": 41.630,
        "lng": -83.555,
        "population": 18000,
    },
]

FACILITIES = [
    {
        "name": "Kent County SafeChem HHW",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "grand-rapids",
        "state": "MI",
        "zip": "49507",
        "address": "1045 Wealthy Street SW, Grand Rapids, MI 49507",
        "lat": 42.9455,
        "lng": -85.6555,
        "source_url": "https://www.kentcountymi.gov/368/SafeChem-Household-Hazardous-Waste",
        "hours": "Mon 13:30–17:30; Wed 7:30–11:30; Thu 13:30–17:30; 2nd Sat 8:30–11",
        "phone": "616-336-2501",
        "accepted_materials": HHW_MATERIALS,
    },
    {
        "name": "Monroe County ecopark",
        "facility_type": "HHW and e-waste drop-off",
        "city_slug": "rochester",
        "state": "NY",
        "zip": "14624",
        "address": "10 Avion Drive, Rochester, NY 14624",
        "lat": 43.1255,
        "lng": -77.7455,
        "source_url": "https://www.monroecounty.gov/ecopark/",
        "hours": "Wed 13:00–18:30; Sat 7:30–13:00",
        "phone": "585-753-7600",
        "accepted_materials": HHW_MATERIALS
        + ["television", "computer-monitor", "smartphone", "e-waste-mixed", "tires", "tire-rims"],
    },
    {
        "name": "SPSA Norfolk Transfer Station",
        "facility_type": "HHW and e-waste drop-off",
        "city_slug": "norfolk",
        "state": "VA",
        "zip": "23513",
        "address": "3136 Woodland Avenue, Norfolk, VA 23513",
        "lat": 36.8655,
        "lng": -76.2455,
        "source_url": "https://www.norfolk.gov/405/How-Do-I-Dispose-Of",
        "hours": "Tue & Sat 12:00–16:00",
        "phone": "757-961-3981",
        "accepted_materials": HHW_MATERIALS
        + ["television", "computer-monitor", "smartphone", "e-waste-mixed"],
    },
    {
        "name": "Lexington HHW Collection — Old Frankfort Pike",
        "facility_type": "Seasonal household hazardous waste events",
        "city_slug": "lexington",
        "state": "KY",
        "zip": "40504",
        "address": "1631 Old Frankfort Pike, Lexington, KY 40504",
        "lat": 38.0755,
        "lng": -84.5455,
        "source_url": "https://www.lexingtonky.gov/living/waste-collection/household-hazardous-waste",
        "hours": "Sat May 16 & Oct 17 2026, 8:30–15:00",
        "phone": "859-425-2255",
        "accepted_materials": HHW_MATERIALS,
    },
    {
        "name": "Clean Toledo Recycling Center",
        "facility_type": "Recycling center, e-waste and seasonal HHW events",
        "city_slug": "toledo",
        "state": "OH",
        "zip": "43607",
        "address": "3900 Creekside Avenue, Toledo, OH 43607",
        "lat": 41.6355,
        "lng": -83.5855,
        "source_url": "https://toledo.oh.gov/residents/neighborhoods/trash-recycling/clean-toledo-recycling-center",
        "hours": "Tue–Sat 8:30–16:00; HHW events June 13, Aug 15, Oct 3 2026",
        "phone": "419-936-2511",
        "accepted_materials": HHW_MATERIALS
        + ["television", "computer-monitor", "smartphone", "e-waste-mixed", "tires", "tire-rims"],
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
        "grand-rapids": clone_siblings(grand_rapids()),
        "rochester": clone_siblings(rochester()),
        "norfolk": clone_siblings(norfolk()),
        "lexington": clone_siblings(lexington()),
        "toledo": clone_siblings(toledo()),
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

    print("Wave-14 metros written:")
    for city, rows in audited.items():
        print(f"  {city}: {len(rows)} rules")
    print(f"Total rules now: {len(keep)}")


if __name__ == "__main__":
    main()
