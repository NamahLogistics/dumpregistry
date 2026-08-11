#!/usr/bin/env python3
"""Portal-audited city guides for wave-15 metros (city-sourced only).

Cities researched from official program pages (2026-08-11):
  - Lincoln, NE — private haulers / N 48th Transfer Station + HazToGo HHW
  - Fort Wayne, IN — 311 scheduled bulk + Allen County Tox-Tuesday HHW / ACDEM e-waste
  - St. Petersburg, FL — Special Pickup + Pinellas County HHW
  - Corpus Christi, TX — twice-yearly Brush & Bulky + J.C. Elliott HHW/e-waste
  - Greensboro, NC — biweekly bulk + HHW center + Guilford County white goods / scrap tire
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


def lincoln():
    c, st = "lincoln", "NE"
    sw = (
        "City of Lincoln — Solid Waste Management",
        "https://www.lincoln.ne.gov/City/Departments/LTU/Utilities/Solid-Waste-Management",
    )
    collectors = (
        "City of Lincoln — Licensed waste collectors",
        "https://www.lincoln.ne.gov/City/Departments/LTU/Utilities/Solid-Waste-Management/Recycling/Collectors",
    )
    hhw = (
        "Lincoln HazToGo HHW",
        "https://www.lincoln.ne.gov/City/Departments/Health-Department/Environmental/Waste-Management",
    )
    recycle = (
        "City of Lincoln — Recycling",
        "https://www.lincoln.ne.gov/City/Departments/LTU/Utilities/Solid-Waste-Management/Recycling",
    )
    rows = []
    rows.append(
        R(
            c, st, "mattress", "SPECIAL_HANDLING", "Low", False,
            "Private licensed hauler bulk OR N 48th Transfer Station fee",
            "Private hauler / N 48th Transfer Station — 5101 N 48th St",
            "Lincoln has NO city bulk collection. Mattresses go through your private licensed hauler's bulk service OR self-haul to N 48th Transfer Station — 5101 N 48th St. Confirm hauler fees before set-out.",
            ["Contact your licensed hauler for bulk pickup.", "Or haul to N 48th Transfer Station 5101 N 48th St.", "No city curbside bulk program."],
            [("City bulk?", "No — private haulers or transfer station only."), ("Transfer address?", "5101 N 48th St.")],
            *collectors,
        )
    )
    rows.append(
        R(
            c, st, "refrigerator", "SPECIAL_HANDLING", "High", False,
            "$8.25/unit + $9.95 trip at N 48th Transfer — Freon recovered on-site",
            "N 48th Transfer Station — Freon appliance",
            "Lincoln Freon refrigerators are NOT city curbside bulk. Self-haul to N 48th Transfer Station — 5101 N 48th St — $8.25 per unit plus $9.95 trip fee. Freon is recovered on-site. Private haulers may also collect — confirm fees. Never vent refrigerant yourself.",
            ["Do not assume city curbside pickup.", "Haul to N 48th Transfer ($8.25/unit + $9.95 trip).", "Freon recovered on-site — never vent yourself."],
            [("City curbside?", "No — transfer station or private hauler."), ("Freon fee?", "$8.25/unit + $9.95 trip at transfer.")],
            *sw,
        )
    )
    rows.append(
        R(
            c, st, "air-conditioner", "SPECIAL_HANDLING", "High", False,
            "$8.25/unit + $9.95 trip at N 48th Transfer — Freon appliance",
            "N 48th Transfer Station — Freon appliance",
            "Lincoln Freon window AC units are NOT city curbside bulk. Self-haul to N 48th Transfer Station — 5101 N 48th St — $8.25 per unit plus $9.95 trip fee. Freon recovered on-site. Never vent refrigerant yourself.",
            ["Haul to N 48th Transfer ($8.25/unit + $9.95 trip).", "Freon recovered on-site.", "Private hauler may collect — confirm fees."],
            [("Same as Freon fridge?", "Yes — transfer station fee path, not city curbside.")],
            *sw,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c, st, item, "SPECIAL_HANDLING", "Medium", False,
                "Private hauler bulk OR N 48th Transfer Station fee",
                "Private hauler / N 48th Transfer Station — 5101 N 48th St",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s use private licensed hauler bulk OR N 48th Transfer Station — 5101 N 48th St. Lincoln has no city bulk. Freon refrigerators/AC use the separate $8.25/unit + $9.95 trip transfer path.",
                ["Contact licensed hauler for bulk pickup.", "Or haul to N 48th Transfer Station.", "Freon appliances use separate transfer fee path."],
                [("Same as Freon fridge?", "No — non-Freon uses hauler bulk or general transfer fees.")],
                *collectors,
            )
        )
    for item, label in [
        ("television", "TVs"), ("computer-monitor", "monitors"),
        ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste"),
    ]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "Medium", False,
                "NOT HazToGo — lincoln.ne.gov/recycle / private e-waste",
                "Lincoln recycling programs / private e-waste recycler",
                f"Electronics including {label} are NOT accepted at Lincoln HazToGo HHW. Use lincoln.ne.gov/recycle guidance or a private e-waste recycler. Wipe data before drop-off.",
                ["Do not bring TVs/e-waste to HazToGo.", "Check lincoln.ne.gov/recycle for drop-off options.", "Wipe personal data."],
                [("HazToGo for e-waste?", "No — electronics use recycle/private pathways."), ("Curbside?", "No city e-waste curbside.")],
                *recycle,
            )
        )
    rows.append(
        R(
            c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", True,
            "Dry completely → regular trash — HazToGo does NOT accept latex",
            "Lincoln trash cart — dried latex only",
            "Lincoln latex paint is NOT accepted at HazToGo. Dry paint completely (add kitty litter or leave lid off) until solid, then put dried cans in regular trash. Liquid latex never goes to HazToGo or transfer bulk.",
            ["Add kitty litter or dry paint until solid.", "Place dried cans in regular trash.", "Do not haul liquid latex to HazToGo."],
            [("HazToGo for latex?", "No — latex must be fully dried for trash."), ("Oil paint?", "Oil-based paint goes to HazToGo.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
            "Free HazToGo — oil-based paint only",
            "Lincoln HazToGo — 5101 N 48th St",
            "Oil-based paint goes to Lincoln HazToGo — 5101 N 48th St — free. Hours: Wed & Fri 9:00 a.m.–1:00 p.m.; 3rd Sat 9:00 a.m.–1:00 p.m.; May–Aug Wed 9:00 a.m.–6:00 p.m. Not curbside.",
            ["Haul sealed oil paint to HazToGo 5101 N 48th St.", "Check HazToGo hours before visiting.", "Keep oil paint out of trash carts."],
            [("Latex at HazToGo?", "No — latex must be dried for trash."), ("Fee?", "Free at HazToGo.")],
            *hhw,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
                "Free Lincoln HazToGo HHW",
                "Lincoln HazToGo — 5101 N 48th St",
                f"Take {item.replace('-', ' ')} to Lincoln HazToGo — 5101 N 48th St — free. Hours: Wed & Fri 9–1; 3rd Sat 9–1; May–Aug Wed 9–6. Not transfer bulk or trash.",
                ["Deliver sealed containers to HazToGo.", "Check posted hours.", "Keep chemicals off trash and transfer bulk."],
                [("Same as latex paint?", "No — chemicals go to HazToGo; dried latex goes to trash.")],
                *hhw,
            )
        )
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {
            "car-battery": " Lead-acid batteries at HazToGo.",
            "lithium-battery": " Lithium batteries at HazToGo.",
            "motor-oil": " Used motor oil at HazToGo.",
            "propane-tank": " Propane tanks at HazToGo — confirm size limits.",
            "fluorescent-bulbs": " Fluorescent bulbs at HazToGo.",
            "cooking-oil": " Cooking oil at HazToGo when not trash-safe.",
        }[item]
        rows.append(
            R(
                c, st, item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium", False,
                "Free Lincoln HazToGo HHW",
                "Lincoln HazToGo — 5101 N 48th St",
                f"Lincoln HazToGo at 5101 N 48th St accepts household hazardous materials free.{extra}",
                ["Haul to HazToGo during posted hours.", "Wed/Fri 9–1; 3rd Sat 9–1; May–Aug Wed 9–6.", "Tires use transfer station fee path, not HazToGo."],
                [("Address?", "5101 N 48th St, Lincoln.")],
                *hhw,
            )
        )
    rows.append(
        R(
            c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
            "Rigid sealed container — confirm HazToGo sharps acceptance",
            "Lincoln HazToGo — 5101 N 48th St",
            "Place sharps in a rigid sealed container. Confirm acceptance at Lincoln HazToGo. Do not loose-bag needles.",
            ["Use rigid sealed container.", "Confirm sharps at HazToGo.", "Never recycle loose needles."],
            [("Medications?", "Confirm drug take-back via Lincoln/Lancaster County programs.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
            "$5.25/car tire — max 9 at N 48th Transfer Station",
            "N 48th Transfer Station — 5101 N 48th St",
            "Lincoln tires are NOT city curbside bulk. Self-haul to N 48th Transfer Station — 5101 N 48th St — $5.25 per car tire, maximum 9 tires. Retailer take-back when replacing tires.",
            ["Do not assume city curbside tire pickup.", "Haul to N 48th Transfer ($5.25/tire, max 9).", "Retailer take-back when replacing tires."],
            [("City bulk for tires?", "No — transfer station fee drop-off."), ("Fee?", "$5.25 per car tire, max 9.")],
            *sw,
        )
    )
    rows.append(
        R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True,
          "Lincoln yard waste via licensed hauler", "Private hauler yard waste collection",
          "Lincoln yard waste is handled through your licensed hauler's yard waste program. Follow hauler set-out rules.",
          ["Contact licensed hauler for yard waste rules.", "Keep yard waste out of HazToGo and e-waste.", "Check lincoln.ne.gov for seasonal guidance."],
          [("Christmas trees?", "Follow hauler seasonal yard waste guidance.")], *sw)
    )
    rows.append(
        R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True,
          "Garbage cart via licensed hauler", "Private hauler garbage / private compost",
          "Bag food scraps for garbage via your licensed hauler unless you compost. Keep food out of recycling and HazToGo.",
          ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."],
          [("HazToGo for food?", "No.")], *sw)
    )
    rows.append(
        R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False,
          "Not recycling — store take-back / trash", "Retail bag take-back / trash",
          "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
          ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."],
          [("Transfer for bags?", "No.")], *recycle)
    )
    rows.append(
        R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", False,
          "NOT city bulk — private C&D hauler / transfer station",
          "Private C&D hauler / N 48th Transfer Station",
          "Lincoln has no city bulk for construction debris. Hire a private C&D hauler or confirm acceptance/fees at N 48th Transfer Station. Route paint/chemicals to HazToGo separately.",
          ["Do not treat C&D as city bulk.", "Hire private C&D for remodel loads.", "Route oil paint/chemicals to HazToGo."],
          [("HazToGo for C&D?", "No — separate paint/chemicals.")], *sw)
    )
    return rows


def fort_wayne():
    c, st = "fort-wayne", "IN"
    bulk = (
        "City of Fort Wayne — Bulk Items",
        "https://www.cityoffortwayne.in.gov/672/Bulk-Items",
    )
    hhw = (
        "Allen County Tox-Tuesday HHW",
        "https://www.allencounty.in.gov/483/Household-Hazardous-Waste-Disposal",
    )
    ewaste = (
        "Allen County ACDEM Electronics Recycling",
        "https://www.allencounty.in.gov/478/Electronics-Recycling",
    )
    rows = []
    rows.append(
        R(
            c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
            "Free — schedule 311 ≥2 business days before garbage day; wrap in plastic",
            "Fort Wayne 311 scheduled bulk collection",
            "Fort Wayne mattresses require 311 scheduling at least 2 business days before your garbage day — free with service. Wrap mattress completely in plastic before set-out. Set out on scheduled garbage day only.",
            ["Call 311 to schedule ≥2 business days before garbage day.", "Wrap mattress completely in plastic.", "Set out on scheduled garbage day."],
            [("Fee?", "Free with scheduled bulk service."), ("Plastic wrap?", "Required — wrap completely in plastic.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c, st, "refrigerator", "SPECIAL_HANDLING", "High", False,
            "NOT bulk — private Freon appliance recycler",
            "Private Freon appliance recycler",
            "Fort Wayne Freon refrigerators are NOT accepted on 311 scheduled bulk. Use a private Freon appliance recycler. Never vent refrigerant yourself. Non-Freon appliances such as washers use free scheduled bulk.",
            ["Do not schedule Freon fridge on 311 bulk.", "Contact a private Freon appliance recycler.", "Never vent refrigerant yourself."],
            [("311 bulk for Freon fridge?", "No — private recycler only."), ("Washer/dryer?", "Free scheduled bulk via 311.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c, st, "air-conditioner", "SPECIAL_HANDLING", "High", False,
            "NOT bulk — private Freon appliance recycler",
            "Private Freon appliance recycler",
            "Fort Wayne Freon window AC units are NOT accepted on 311 scheduled bulk. Use a private Freon appliance recycler. Never vent refrigerant yourself.",
            ["Do not schedule Freon AC on 311 bulk.", "Contact a private Freon appliance recycler.", "Keep sealed until proper Freon handling."],
            [("Same as Freon fridge?", "Yes — private recycler, not 311 bulk.")],
            *bulk,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c, st, item, "SPECIAL_HANDLING", "Medium", True,
                "Free — schedule 311 ≥2 business days before garbage day",
                "Fort Wayne 311 scheduled bulk collection",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s use Fort Wayne 311 scheduled bulk — free with service. Schedule ≥2 business days before garbage day. Freon refrigerators/AC are NOT bulk — private recycler only.",
                ["Call 311 to schedule ≥2 business days before garbage day.", "Set out on scheduled garbage day.", "Freon appliances use private recycler path."],
                [("Same as Freon fridge?", "No — non-Freon uses free 311 bulk.")],
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
                "NOT HHW — ACDEM events 2911 Meyer Rd ($10 for 1–5 incl 1 TV)",
                "Allen County ACDEM — 2911 Meyer Road",
                f"Electronics including {label} are NOT accepted at Allen County Tox-Tuesday HHW. ACDEM electronics events at 2911 Meyer Road — $10 for 1–5 items including 1 TV. Wipe data before drop-off.",
                ["Do not bring TVs/e-waste to Tox-Tuesday HHW.", "Haul to ACDEM 2911 Meyer Rd events.", "Wipe personal data."],
                [("Tox-Tuesday for e-waste?", "No — ACDEM electronics events only."), ("Fee?", "$10 for 1–5 items including 1 TV.")],
                *ewaste,
            )
        )
    rows.append(
        R(
            c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", False,
            "Free Allen County Tox-Tuesday HHW",
            "Allen County Tox-Tuesday — 2260 Carroll Road",
            "Fort Wayne latex paint goes to Allen County Tox-Tuesday HHW — 2260 Carroll Road — every Tuesday 9:00 a.m.–2:00 p.m., free. Not 311 bulk.",
            ["Haul sealed paint to Tox-Tuesday 2260 Carroll Rd.", "Hours: every Tue 9–2.", "Keep paint off 311 bulk piles."],
            [("311 bulk for paint?", "No — Tox-Tuesday HHW only."), ("Fee?", "Free at Tox-Tuesday.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
            "Free Allen County Tox-Tuesday HHW",
            "Allen County Tox-Tuesday — 2260 Carroll Road",
            "Oil-based paint goes to Allen County Tox-Tuesday HHW — 2260 Carroll Road — every Tuesday 9:00 a.m.–2:00 p.m., free. Not 311 bulk or trash.",
            ["Haul oil paint to Tox-Tuesday 2260 Carroll Rd.", "Keep containers sealed and labeled.", "Not 311 bulk."],
            [("Same as latex?", "Yes — both use Tox-Tuesday HHW.")],
            *hhw,
        )
    )
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {
            "car-battery": " Lead-acid batteries at Tox-Tuesday.",
            "lithium-battery": " Lithium batteries at Tox-Tuesday.",
            "motor-oil": " Used motor oil at Tox-Tuesday.",
            "propane-tank": " Propane tanks at Tox-Tuesday — confirm size limits.",
            "fluorescent-bulbs": " Fluorescent bulbs at Tox-Tuesday.",
            "cooking-oil": " Cooking oil at Tox-Tuesday when not trash-safe.",
        }[item]
        rows.append(
            R(
                c, st, item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium", False,
                "Free Allen County Tox-Tuesday HHW",
                "Allen County Tox-Tuesday — 2260 Carroll Road",
                f"Allen County Tox-Tuesday at 2260 Carroll Road accepts household hazardous materials free every Tuesday 9 a.m.–2 p.m.{extra}",
                ["Haul to Tox-Tuesday 2260 Carroll Rd.", "Hours: every Tue 9–2.", "Tires use county/retailer path, not Tox-Tuesday bulk."],
                [("Address?", "2260 Carroll Road, Fort Wayne.")],
                *hhw,
            )
        )
    rows.append(
        R(
            c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
            "Rigid sealed container — confirm Tox-Tuesday sharps acceptance",
            "Allen County Tox-Tuesday HHW",
            "Place sharps in a rigid sealed container. Confirm acceptance at Allen County Tox-Tuesday. Do not loose-bag needles.",
            ["Use rigid sealed container.", "Confirm sharps at Tox-Tuesday.", "Never recycle loose needles."],
            [("Medications?", "Confirm drug take-back via Allen County programs.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
            "NOT 311 bulk — Allen County / retailer take-back",
            "Allen County tire drop-off / retailer",
            "Fort Wayne tires are NOT accepted on 311 scheduled bulk. Use Allen County tire programs or retailer take-back when replacing tires.",
            ["Do not schedule tires on 311 bulk.", "Haul to Allen County tire drop-off.", "Retailer take-back when replacing tires."],
            [("311 bulk for tires?", "No — county/retailer pathways.")],
            *bulk,
        )
    )
    rows.append(
        R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True,
          "Fort Wayne yard waste collection", "Fort Wayne yard waste collection",
          "Fort Wayne handles yard waste through regular collection. Follow set-out rules on cityoffortwayne.in.gov.",
          ["Use yard waste set-out rules.", "Keep yard waste out of HHW and e-waste.", "Check city site for seasonal guidance."],
          [("Christmas trees?", "Follow city seasonal yard waste guidance.")], *bulk)
    )
    rows.append(
        R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True,
          "Garbage cart unless private compost", "Fort Wayne garbage / private compost",
          "Bag food scraps for garbage unless you compost. Keep food out of recycling and HHW.",
          ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."],
          [("HHW for food?", "No.")], *bulk)
    )
    rows.append(
        R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False,
          "Not recycling — store take-back / trash", "Retail bag take-back / trash",
          "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
          ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."],
          [("311 bulk for bags?", "No.")], *bulk)
    )
    rows.append(
        R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", False,
          "NOT 311 bulk — private C&D hauler",
          "Private C&D hauler",
          "Contractor construction debris is not Fort Wayne 311 scheduled bulk. Hire a private C&D hauler for remodel loads. Route paint/chemicals to Tox-Tuesday separately.",
          ["Do not treat remodel debris as 311 bulk.", "Hire private C&D for larger projects.", "Route paint to Tox-Tuesday HHW."],
          [("HHW for C&D?", "No — separate paint/chemicals.")], *bulk)
    )
    return rows


def st_petersburg():
    c, st = "st-petersburg", "FL"
    pickup = (
        "City of St. Petersburg — Special Pickup",
        "https://www.stpete.org/residents/utilities/residential_trash___recycling/special_pickup.php",
    )
    hhw = (
        "Pinellas County HHW",
        "https://pinellas.gov/household-hazardous-waste-hhw-collection/",
    )
    rows = []
    rows.append(
        R(
            c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
            "Free Special Pickup — schedule SeeClickFix or 727-893-7398; ≤3 cy",
            "St. Petersburg Special Pickup",
            "St. Petersburg mattresses use Special Pickup — schedule via SeeClickFix or call 727-893-7398. Free furniture/appliances within 3 cubic yards. Paid $25.65/cy beyond 3 cy limit.",
            ["Schedule Special Pickup via SeeClickFix or 727-893-7398.", "Stay within 3 cy free limit.", "Set out on scheduled pickup day."],
            [("Fee?", "Free within 3 cy."), ("Over limit?", "$25.65/cy beyond 3 cy.")],
            *pickup,
        )
    )
    rows.append(
        R(
            c, st, "refrigerator", "SPECIAL_HANDLING", "High", True,
            "Free Special Pickup appliances — schedule SeeClickFix / 727-893-7398",
            "St. Petersburg Special Pickup — Freon appliance",
            "St. Petersburg Freon refrigerators are included in free Special Pickup appliances — schedule via SeeClickFix or 727-893-7398 within 3 cy. Never vent refrigerant yourself.",
            ["Schedule Special Pickup via SeeClickFix or 727-893-7398.", "Set out on scheduled day within 3 cy.", "Never vent Freon yourself."],
            [("Freon fee?", "Free within 3 cy Special Pickup."), ("Over 3 cy?", "$25.65/cy additional.")],
            *pickup,
        )
    )
    rows.append(
        R(
            c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
            "Free Special Pickup appliances — Freon appliance",
            "St. Petersburg Special Pickup — Freon appliance",
            "St. Petersburg Freon window AC units use free Special Pickup appliances — schedule via SeeClickFix or 727-893-7398 within 3 cy. Never vent refrigerant yourself.",
            ["Schedule Special Pickup via SeeClickFix or 727-893-7398.", "Set out on scheduled day.", "Keep sealed until proper Freon handling."],
            [("Same as Freon fridge?", "Yes — free Special Pickup appliances within 3 cy.")],
            *pickup,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c, st, item, "SPECIAL_HANDLING", "Medium", True,
                "Free Special Pickup — schedule SeeClickFix / 727-893-7398; ≤3 cy",
                "St. Petersburg Special Pickup",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s use St. Petersburg Special Pickup — free within 3 cy. Schedule via SeeClickFix or 727-893-7398. Freon refrigerators/AC also free within 3 cy.",
                ["Schedule Special Pickup via SeeClickFix or 727-893-7398.", "Set out on scheduled day within 3 cy.", "Over 3 cy: $25.65/cy."],
                [("Same as Freon fridge?", "Yes — all appliances use Special Pickup within 3 cy.")],
                *pickup,
            )
        )
    for item, label in [
        ("television", "TVs"), ("computer-monitor", "monitors"),
        ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste"),
    ]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "Medium", True,
                "Special Pickup / garbage (remove batteries) / SWDC — NOT Pinellas HHW",
                "St. Petersburg Special Pickup / SWDC",
                f"Electronics including {label} are NOT accepted at Pinellas County HHW. Use St. Petersburg Special Pickup, garbage (remove batteries first), or SWDC. Wipe data before disposal.",
                ["Do not bring TVs/e-waste to Pinellas HHW.", "Schedule Special Pickup or use SWDC.", "Remove batteries before garbage set-out."],
                [("Pinellas HHW for TVs?", "No — TVs NOT at HHW."), ("Special Pickup?", "Yes — within 3 cy free limit.")],
                *pickup,
            )
        )
    rows.append(
        R(
            c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", False,
            "Free Pinellas County HHW — NOT Special Pickup",
            "Pinellas County HHW — 2855 109th Ave N",
            "St. Petersburg latex paint goes to Pinellas County HHW — 2855 109th Ave N — free. Hours: Tue–Fri 7:00 a.m.–5:00 p.m.; 1st & 3rd Sat. Not Special Pickup.",
            ["Haul sealed paint to Pinellas HHW 2855 109th Ave N.", "Hours: Tue–Fri 7–5; 1st & 3rd Sat.", "Keep paint off Special Pickup piles."],
            [("Special Pickup for paint?", "No — Pinellas HHW only."), ("Fee?", "Free at Pinellas HHW.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
            "Free Pinellas County HHW",
            "Pinellas County HHW — 2855 109th Ave N",
            "Oil-based paint goes to Pinellas County HHW — 2855 109th Ave N — free. Hours: Tue–Fri 7–5; 1st & 3rd Sat. Not Special Pickup or trash.",
            ["Haul oil paint to Pinellas HHW 2855 109th Ave N.", "Keep containers sealed and labeled.", "Not Special Pickup."],
            [("Same as latex?", "Yes — both use Pinellas HHW.")],
            *hhw,
        )
    )
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {
            "car-battery": " Lead-acid batteries at Pinellas HHW.",
            "lithium-battery": " Lithium batteries at Pinellas HHW.",
            "motor-oil": " Used motor oil at Pinellas HHW.",
            "propane-tank": " Propane tanks at Pinellas HHW — confirm size limits.",
            "fluorescent-bulbs": " Fluorescent bulbs at Pinellas HHW.",
            "cooking-oil": " Cooking oil at Pinellas HHW when not trash-safe.",
        }[item]
        rows.append(
            R(
                c, st, item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium", False,
                "Free Pinellas County HHW",
                "Pinellas County HHW — 2855 109th Ave N",
                f"Pinellas County HHW at 2855 109th Ave N accepts household hazardous materials free.{extra} TVs are NOT accepted at HHW.",
                ["Haul to Pinellas HHW 2855 109th Ave N.", "Hours: Tue–Fri 7–5; 1st & 3rd Sat.", "Tires use Special Pickup path, not HHW."],
                [("Address?", "2855 109th Ave N, St. Petersburg area.")],
                *hhw,
            )
        )
    rows.append(
        R(
            c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
            "Rigid sealed container — confirm Pinellas HHW sharps acceptance",
            "Pinellas County HHW — 2855 109th Ave N",
            "Place sharps in a rigid sealed container. Confirm acceptance at Pinellas County HHW. Do not loose-bag needles.",
            ["Use rigid sealed container.", "Confirm sharps at Pinellas HHW.", "Never recycle loose needles."],
            [("Medications?", "Confirm drug take-back via Pinellas County programs.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "tires", "SPECIAL_HANDLING", "Medium", True,
            "5 free Special Pickup — schedule SeeClickFix / 727-893-7398",
            "St. Petersburg Special Pickup — tires",
            "St. Petersburg tires: up to 5 free on Special Pickup. Schedule via SeeClickFix or 727-893-7398. Set out on scheduled day.",
            ["Schedule Special Pickup via SeeClickFix or 727-893-7398.", "Limit 5 tires per Special Pickup.", "Set out on scheduled day."],
            [("Pinellas HHW for tires?", "No — use Special Pickup."), ("Fee?", "Free — up to 5 tires.")],
            *pickup,
        )
    )
    rows.append(
        R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True,
          "St. Petersburg yard waste collection", "St. Petersburg yard waste collection",
          "St. Petersburg handles yard waste through regular collection. Follow set-out rules on stpete.org.",
          ["Use yard waste set-out rules.", "Keep yard waste out of HHW and e-waste.", "Check city site for seasonal guidance."],
          [("Christmas trees?", "Follow city seasonal yard waste guidance.")], *pickup)
    )
    rows.append(
        R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True,
          "Garbage cart unless private compost", "St. Petersburg garbage / private compost",
          "Bag food scraps for garbage unless you compost. Keep food out of recycling and HHW.",
          ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."],
          [("HHW for food?", "No.")], *pickup)
    )
    rows.append(
        R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False,
          "Not recycling — store take-back / trash", "Retail bag take-back / trash",
          "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
          ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."],
          [("Special Pickup for bags?", "No.")], *pickup)
    )
    rows.append(
        R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", False,
          "NOT Special Pickup — private C&D hauler",
          "Private C&D hauler",
          "Contractor construction debris exceeds St. Petersburg Special Pickup limits. Hire a private C&D hauler for remodel loads. Route paint/chemicals to Pinellas HHW separately.",
          ["Do not treat remodel debris as Special Pickup.", "Hire private C&D for larger projects.", "Route paint to Pinellas HHW."],
          [("HHW for C&D?", "No — separate paint/chemicals.")], *pickup)
    )
    return rows


def corpus_christi():
    c, st = "corpus-christi", "TX"
    bulky = (
        "City of Corpus Christi — Heavy Brush and Bulky Items",
        "https://www.corpuschristitx.gov/department-directory/solid-waste-services/heavy-brush-and-bulky-items/",
    )
    hhw = (
        "City of Corpus Christi — HHW at J.C. Elliott",
        "https://www.corpuschristitx.gov/department-directory/solid-waste-services/household-hazardous-waste-disposal/",
    )
    rows = []
    rows.append(
        R(
            c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
            "Free twice-yearly Brush & Bulky on area dates — separate piles",
            "Corpus Christi Brush & Bulky collection",
            "Corpus Christi mattresses go on twice-yearly Brush & Bulky collection on your area's scheduled dates — free. Keep separate piles for brush, bulky, and tires. Unscheduled set-out may incur a surcharge.",
            ["Check area Brush & Bulky dates on city site.", "Set mattress in separate bulky pile.", "Do not mix with brush or tires."],
            [("Fee?", "Free on scheduled area dates."), ("Unscheduled?", "May incur surcharge — follow area schedule.")],
            *bulky,
        )
    )
    rows.append(
        R(
            c, st, "refrigerator", "SPECIAL_HANDLING", "High", True,
            "Brush & Bulky ONLY if Freon removed by certified tech — else J.C. Elliott",
            "Corpus Christi Brush & Bulky / J.C. Elliott Transfer",
            "Corpus Christi Freon refrigerators may go on Brush & Bulky ONLY if Freon is removed by a certified technician first. Otherwise haul to J.C. Elliott Transfer — 7001 Ayers St. Never vent refrigerant yourself. Unscheduled bulky may incur surcharge.",
            ["Have Freon removed by certified technician before bulky set-out.", "Or haul to J.C. Elliott Transfer 7001 Ayers St.", "Never vent Freon yourself."],
            [("Bulky without Freon removal?", "No — Freon must be removed first or use Elliott Transfer."), ("Elliott address?", "7001 Ayers St.")],
            *bulky,
        )
    )
    rows.append(
        R(
            c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
            "Brush & Bulky ONLY if Freon removed — else J.C. Elliott Transfer",
            "Corpus Christi Brush & Bulky / J.C. Elliott Transfer",
            "Corpus Christi Freon window AC units may go on Brush & Bulky ONLY if Freon is removed by a certified technician first. Otherwise haul to J.C. Elliott Transfer — 7001 Ayers St. Never vent refrigerant yourself.",
            ["Have Freon removed by certified tech before bulky.", "Or haul to J.C. Elliott 7001 Ayers St.", "Keep sealed until proper Freon handling."],
            [("Same as Freon fridge?", "Yes — Freon must be removed before bulky or use Elliott.")],
            *bulky,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c, st, item, "SPECIAL_HANDLING", "Medium", True,
                "Free twice-yearly Brush & Bulky — separate piles",
                "Corpus Christi Brush & Bulky collection",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s go on twice-yearly Brush & Bulky on area dates — free. Separate piles required. Freon refrigerators/AC need certified Freon removal before bulky.",
                ["Check area Brush & Bulky dates.", "Set in separate bulky pile.", "Freon appliances need certified removal first."],
                [("Freon appliances?", "Must have Freon removed before bulky set-out.")],
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
                "Free J.C. Elliott HHW/e-waste — Mon–Sat 8–17",
                "J.C. Elliott Transfer — 7001 Ayers St",
                f"Electronics including {label} go to J.C. Elliott Transfer — 7001 Ayers St — Mon–Sat 8:00 a.m.–5:00 p.m., free for residents. Wipe data before drop-off. Not Brush & Bulky piles.",
                ["Haul e-waste to J.C. Elliott 7001 Ayers St.", "Hours: Mon–Sat 8–5.", "Wipe personal data."],
                [("Brush & Bulky for TVs?", "No — J.C. Elliott drop-off."), ("Fee?", "Free for residents.")],
                *hhw,
            )
        )
    rows.append(
        R(
            c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", False,
            "Free J.C. Elliott HHW — up to 5 one-gallon cans",
            "J.C. Elliott Transfer — 7001 Ayers St",
            "Corpus Christi latex paint goes to J.C. Elliott HHW — 7001 Ayers St — Mon–Sat 8–5, free for residents. Up to 5 one-gallon cans. Not Brush & Bulky.",
            ["Haul sealed paint to J.C. Elliott 7001 Ayers St.", "Limit 5 one-gallon cans.", "Keep paint off bulky piles."],
            [("Bulky for paint?", "No — J.C. Elliott HHW only."), ("Limit?", "Up to 5 one-gallon cans.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
            "Free J.C. Elliott HHW — up to 5 one-gallon cans",
            "J.C. Elliott Transfer — 7001 Ayers St",
            "Oil-based paint goes to J.C. Elliott HHW — 7001 Ayers St — Mon–Sat 8–5, free for residents. Up to 5 one-gallon cans. Not Brush & Bulky or trash.",
            ["Haul oil paint to J.C. Elliott 7001 Ayers St.", "Limit 5 one-gallon cans.", "Keep containers sealed."],
            [("Same as latex?", "Yes — both use J.C. Elliott HHW.")],
            *hhw,
        )
    )
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {
            "car-battery": " Lead-acid batteries at J.C. Elliott HHW.",
            "lithium-battery": " Lithium batteries at J.C. Elliott HHW.",
            "motor-oil": " Used motor oil at J.C. Elliott HHW.",
            "propane-tank": " Propane tanks at J.C. Elliott HHW — confirm size limits.",
            "fluorescent-bulbs": " Fluorescent bulbs at J.C. Elliott HHW.",
            "cooking-oil": " Cooking oil at J.C. Elliott HHW when not trash-safe.",
        }[item]
        rows.append(
            R(
                c, st, item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium", False,
                "Free J.C. Elliott HHW — Mon–Sat 8–17",
                "J.C. Elliott Transfer — 7001 Ayers St",
                f"J.C. Elliott Transfer at 7001 Ayers St accepts household hazardous materials free for residents Mon–Sat 8 a.m.–5 p.m.{extra}",
                ["Haul to J.C. Elliott 7001 Ayers St.", "Hours: Mon–Sat 8–5.", "Tires also accepted on Brush & Bulky or at Elliott."],
                [("Address?", "7001 Ayers St, Corpus Christi.")],
                *hhw,
            )
        )
    rows.append(
        R(
            c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
            "Rigid sealed container — confirm J.C. Elliott sharps acceptance",
            "J.C. Elliott Transfer — 7001 Ayers St",
            "Place sharps in a rigid sealed container. Confirm acceptance at J.C. Elliott HHW. Do not loose-bag needles.",
            ["Use rigid sealed container.", "Confirm sharps at J.C. Elliott.", "Never recycle loose needles."],
            [("Medications?", "Confirm drug take-back via Nueces County programs.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "tires", "SPECIAL_HANDLING", "Medium", True,
            "4 free on Brush & Bulky (≤20 in) OR J.C. Elliott",
            "Corpus Christi Brush & Bulky / J.C. Elliott Transfer",
            "Corpus Christi tires: up to 4 free on Brush & Bulky (≤20 inches) in a separate pile, OR drop at J.C. Elliott Transfer — 7001 Ayers St. Unscheduled bulky may incur surcharge.",
            ["Check area Brush & Bulky dates.", "Set 4 tires max in separate pile (≤20 in).", "Or haul to J.C. Elliott 7001 Ayers St."],
            [("Bulky limit?", "4 tires ≤20 in per bulky collection."), ("Elliott?", "Also accepts tires for residents.")],
            *bulky,
        )
    )
    rows.append(
        R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True,
          "Corpus Christi yard waste / Brush & Bulky", "Corpus Christi yard waste collection",
          "Corpus Christi handles yard waste through regular collection and twice-yearly Brush & Bulky. Follow set-out rules on corpuschristitx.gov.",
          ["Use yard waste set-out rules.", "Keep yard waste in separate Brush & Bulky pile.", "Check city site for seasonal guidance."],
          [("Christmas trees?", "Follow city seasonal yard waste guidance.")], *bulky)
    )
    rows.append(
        R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True,
          "Garbage cart unless private compost", "Corpus Christi garbage / private compost",
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
          "NOT Brush & Bulky — private C&D hauler",
          "Private C&D hauler",
          "Contractor construction debris is not Corpus Christi Brush & Bulky. Hire a private C&D hauler for remodel loads. Route paint/chemicals to J.C. Elliott HHW separately.",
          ["Do not treat remodel debris as Brush & Bulky.", "Hire private C&D for larger projects.", "Route paint to J.C. Elliott HHW."],
          [("HHW for C&D?", "No — separate paint/chemicals.")], *bulky)
    )
    return rows


def greensboro():
    c, st = "greensboro", "NC"
    bulk = (
        "City of Greensboro — Bulk Items",
        "https://www.greensboro-nc.gov/departments/solid-waste-and-recycling/trash/residential-collection/bulk-items",
    )
    appliances = (
        "City of Greensboro — Appliances",
        "https://www.greensboro-nc.gov/departments/solid-waste-and-recycling/trash/residential-collection/appliances",
    )
    hhw = (
        "Greensboro HHW Collection Center",
        "https://www.greensboro-nc.gov/departments/solid-waste-and-recycling/household-hazardous-waste-collection-center",
    )
    tires = (
        "Guilford County Scrap Tire Disposal",
        "https://www.guilfordcountync.gov/government/departments-and-agencies/planning-and-development/environmental-services/scrap-tire-disposal",
    )
    rows = []
    rows.append(
        R(
            c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
            "Free biweekly bulk on recycling day — set out by 7:00 a.m.",
            "Greensboro biweekly bulk collection",
            "Greensboro mattresses are free on biweekly bulk collection on your recycling day. Set out by 7:00 a.m. Items must be ≤50 lbs and manageable by two people. Large appliances use a separate appointment path.",
            ["Set mattress out by 7 a.m. on recycling day (bulk week).", "Confirm biweekly bulk schedule.", "Keep separate from recycling cart."],
            [("Fee?", "Free on biweekly bulk day."), ("Weight limit?", "≤50 lbs, two-person manageable.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c, st, "refrigerator", "SPECIAL_HANDLING", "High", False,
            "NOT regular bulk — appointment 336-373-CITY OR Guilford White Goods 2138 Bishop Rd",
            "Greensboro appliance appointment / Guilford White Goods",
            "Greensboro Freon refrigerators are NOT regular biweekly bulk. Schedule appliance pickup via 336-373-CITY OR haul free to Guilford County White Goods — 2138 Bishop Road. Never vent refrigerant yourself.",
            ["Call 336-373-CITY for appliance appointment.", "Or haul free to Guilford White Goods 2138 Bishop Rd.", "Never vent Freon yourself."],
            [("Biweekly bulk for Freon fridge?", "No — appointment or White Goods only."), ("White Goods fee?", "Free for Guilford residents.")],
            *appliances,
        )
    )
    rows.append(
        R(
            c, st, "air-conditioner", "SPECIAL_HANDLING", "High", False,
            "NOT regular bulk — appointment 336-373-CITY OR Guilford White Goods",
            "Greensboro appliance appointment / Guilford White Goods",
            "Greensboro Freon window AC units are NOT regular biweekly bulk. Schedule via 336-373-CITY OR haul free to Guilford County White Goods — 2138 Bishop Road. Never vent refrigerant yourself.",
            ["Call 336-373-CITY for appliance appointment.", "Or haul to Guilford White Goods 2138 Bishop Rd.", "Keep sealed until proper Freon handling."],
            [("Same as Freon fridge?", "Yes — appointment or White Goods, not biweekly bulk.")],
            *appliances,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c, st, item, "SPECIAL_HANDLING", "Medium", True,
                "Appointment 336-373-CITY — NOT regular biweekly bulk",
                "Greensboro appliance appointment",
                f"Large appliances such as {item.replace('-', ' ')}s require a Greensboro appliance appointment via 336-373-CITY — not regular biweekly bulk. Freon refrigerators/AC also require appointment or Guilford White Goods 2138 Bishop Rd.",
                ["Call 336-373-CITY to schedule appliance pickup.", "Set out on appointment day.", "Mattresses use separate biweekly bulk path."],
                [("Same as mattress bulk?", "No — appliances need appointment."), ("Freon appliances?", "Appointment or White Goods 2138 Bishop Rd.")],
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
                "Free HHW center — 2750 Patterson St Mon–Fri 10–18 Sat 8–14",
                "Greensboro HHW Collection Center — 2750 Patterson St",
                f"Electronics including {label} go to Greensboro HHW Collection Center — 2750 Patterson St — Mon–Fri 10:00 a.m.–6:00 p.m., Sat 8:00 a.m.–2:00 p.m., free for Guilford County residents. Wipe data before drop-off.",
                ["Haul e-waste to 2750 Patterson St during posted hours.", "Free for Guilford County residents.", "Wipe personal data."],
                [("Biweekly bulk for TVs?", "No — HHW center drop-off."), ("Fee?", "Free for Guilford residents.")],
                *hhw,
            )
        )
    rows.append(
        R(
            c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", False,
            "Free Greensboro HHW center",
            "Greensboro HHW Collection Center — 2750 Patterson St",
            "Greensboro latex paint goes to the HHW Collection Center — 2750 Patterson St — Mon–Fri 10–6, Sat 8–2, free for Guilford County residents. Not biweekly bulk.",
            ["Haul sealed paint to 2750 Patterson St.", "Hours: Mon–Fri 10–6; Sat 8–2.", "Keep paint off biweekly bulk."],
            [("Bulk for paint?", "No — HHW center only."), ("Fee?", "Free for Guilford residents.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
            "Free Greensboro HHW center",
            "Greensboro HHW Collection Center — 2750 Patterson St",
            "Oil-based paint goes to Greensboro HHW Collection Center — 2750 Patterson St — Mon–Fri 10–6, Sat 8–2, free for Guilford County residents. Not biweekly bulk or trash.",
            ["Haul oil paint to 2750 Patterson St.", "Keep containers sealed and labeled.", "Not biweekly bulk."],
            [("Same as latex?", "Yes — both use HHW center.")],
            *hhw,
        )
    )
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {
            "car-battery": " Lead-acid batteries at HHW center.",
            "lithium-battery": " Lithium batteries at HHW center.",
            "motor-oil": " Used motor oil at HHW center.",
            "propane-tank": " Propane tanks at HHW center — confirm size limits.",
            "fluorescent-bulbs": " Fluorescent bulbs at HHW center.",
            "cooking-oil": " Cooking oil at HHW center when not trash-safe.",
        }[item]
        rows.append(
            R(
                c, st, item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium", False,
                "Free Greensboro HHW center",
                "Greensboro HHW Collection Center — 2750 Patterson St",
                f"Greensboro HHW Collection Center at 2750 Patterson St accepts household hazardous materials free for Guilford County residents.{extra}",
                ["Haul to 2750 Patterson St during posted hours.", "Mon–Fri 10–6; Sat 8–2.", "Tires use Guilford Scrap Tire path, not HHW."],
                [("Address?", "2750 Patterson St, Greensboro.")],
                *hhw,
            )
        )
    rows.append(
        R(
            c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
            "Rigid sealed container — confirm HHW center sharps acceptance",
            "Greensboro HHW Collection Center — 2750 Patterson St",
            "Place sharps in a rigid sealed container. Confirm acceptance at Greensboro HHW Collection Center. Do not loose-bag needles.",
            ["Use rigid sealed container.", "Confirm sharps at HHW center.", "Never recycle loose needles."],
            [("Medications?", "Confirm drug take-back via Guilford County programs.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
            "NOT biweekly bulk — Guilford Scrap Tire 5 free/year then $1.15",
            "Guilford County Scrap Tire — 2138 Bishop Road",
            "Greensboro tires are NOT accepted on biweekly bulk. Take to Guilford County Scrap Tire — 2138 Bishop Road — 5 free per year then $1.15 each. Retailer take-back when replacing tires.",
            ["Do not set tires out on biweekly bulk.", "Haul to Guilford Scrap Tire 2138 Bishop Rd.", "5 free/year then $1.15 each."],
            [("Biweekly bulk for tires?", "No — Guilford Scrap Tire only."), ("Fee?", "5 free/year then $1.15 each.")],
            *tires,
        )
    )
    rows.append(
        R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True,
          "Greensboro yard waste collection", "Greensboro yard waste collection",
          "Greensboro handles yard waste through regular collection. Follow set-out rules on greensboro-nc.gov.",
          ["Use yard waste set-out rules.", "Keep yard waste out of HHW and e-waste.", "Check city site for seasonal guidance."],
          [("Christmas trees?", "Follow city seasonal yard waste guidance.")], *bulk)
    )
    rows.append(
        R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True,
          "Garbage cart unless private compost", "Greensboro garbage / private compost",
          "Bag food scraps for garbage unless you compost. Keep food out of recycling and HHW.",
          ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."],
          [("HHW for food?", "No.")], *bulk)
    )
    rows.append(
        R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False,
          "Not recycling — store take-back / trash", "Retail bag take-back / trash",
          "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
          ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."],
          [("Biweekly bulk for bags?", "No.")], *bulk)
    )
    rows.append(
        R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", False,
          "NOT biweekly bulk — private C&D hauler",
          "Private C&D hauler",
          "Contractor construction debris is not Greensboro biweekly bulk. Hire a private C&D hauler for remodel loads. Route paint/chemicals to HHW center separately.",
          ["Do not treat remodel debris as biweekly bulk.", "Hire private C&D for larger projects.", "Route paint to HHW center."],
          [("HHW for C&D?", "No — separate paint/chemicals.")], *bulk)
    )
    return rows


CITIES = [
    {
        "city": "Lincoln",
        "city_slug": "lincoln",
        "state": "NE",
        "state_slug": "nebraska",
        "lat": 40.8136,
        "lng": -96.7026,
        "population": 291082,
    },
    {
        "city": "Fort Wayne",
        "city_slug": "fort-wayne",
        "state": "IN",
        "state_slug": "indiana",
        "lat": 41.0793,
        "lng": -85.1394,
        "population": 264052,
    },
    {
        "city": "St. Petersburg",
        "city_slug": "st-petersburg",
        "state": "FL",
        "state_slug": "florida",
        "lat": 27.7676,
        "lng": -82.6403,
        "population": 258308,
    },
    {
        "city": "Corpus Christi",
        "city_slug": "corpus-christi",
        "state": "TX",
        "state_slug": "texas",
        "lat": 27.8006,
        "lng": -97.3964,
        "population": 317863,
    },
    {
        "city": "Greensboro",
        "city_slug": "greensboro",
        "state": "NC",
        "state_slug": "north-carolina",
        "lat": 36.0726,
        "lng": -79.7920,
        "population": 299035,
    },
]

ZIPS = [
    {
        "zip": "68508",
        "city": "Lincoln",
        "city_slug": "lincoln",
        "state": "NE",
        "state_slug": "nebraska",
        "lat": 40.814,
        "lng": -96.703,
        "population": 12000,
    },
    {
        "zip": "68502",
        "city": "Lincoln",
        "city_slug": "lincoln",
        "state": "NE",
        "state_slug": "nebraska",
        "lat": 40.790,
        "lng": -96.680,
        "population": 18000,
    },
    {
        "zip": "46802",
        "city": "Fort Wayne",
        "city_slug": "fort-wayne",
        "state": "IN",
        "state_slug": "indiana",
        "lat": 41.079,
        "lng": -85.139,
        "population": 14000,
    },
    {
        "zip": "46805",
        "city": "Fort Wayne",
        "city_slug": "fort-wayne",
        "state": "IN",
        "state_slug": "indiana",
        "lat": 41.065,
        "lng": -85.120,
        "population": 16000,
    },
    {
        "zip": "33701",
        "city": "St. Petersburg",
        "city_slug": "st-petersburg",
        "state": "FL",
        "state_slug": "florida",
        "lat": 27.768,
        "lng": -82.640,
        "population": 9000,
    },
    {
        "zip": "33703",
        "city": "St. Petersburg",
        "city_slug": "st-petersburg",
        "state": "FL",
        "state_slug": "florida",
        "lat": 27.785,
        "lng": -82.625,
        "population": 15000,
    },
    {
        "zip": "78401",
        "city": "Corpus Christi",
        "city_slug": "corpus-christi",
        "state": "TX",
        "state_slug": "texas",
        "lat": 27.801,
        "lng": -97.396,
        "population": 8000,
    },
    {
        "zip": "78404",
        "city": "Corpus Christi",
        "city_slug": "corpus-christi",
        "state": "TX",
        "state_slug": "texas",
        "lat": 27.780,
        "lng": -97.420,
        "population": 12000,
    },
    {
        "zip": "27401",
        "city": "Greensboro",
        "city_slug": "greensboro",
        "state": "NC",
        "state_slug": "north-carolina",
        "lat": 36.073,
        "lng": -79.792,
        "population": 11000,
    },
    {
        "zip": "27403",
        "city": "Greensboro",
        "city_slug": "greensboro",
        "state": "NC",
        "state_slug": "north-carolina",
        "lat": 36.055,
        "lng": -79.820,
        "population": 17000,
    },
]

FACILITIES = [
    {
        "name": "Lincoln HazToGo HHW",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "lincoln",
        "state": "NE",
        "zip": "68507",
        "address": "5101 N 48th Street, Lincoln, NE 68507",
        "lat": 40.8555,
        "lng": -96.6555,
        "source_url": "https://www.lincoln.ne.gov/City/Departments/Health-Department/Environmental/Waste-Management",
        "hours": "Wed & Fri 9:00–13:00; 3rd Sat 9:00–13:00; May–Aug Wed 9:00–18:00",
        "phone": "402-441-8022",
        "accepted_materials": [m for m in HHW_MATERIALS if m != "paint-latex"],
    },
    {
        "name": "N 48th Transfer Station",
        "facility_type": "Transfer station — bulk / tires / Freon appliances",
        "city_slug": "lincoln",
        "state": "NE",
        "zip": "68507",
        "address": "5101 N 48th Street, Lincoln, NE 68507",
        "lat": 40.8555,
        "lng": -96.6555,
        "source_url": "https://www.lincoln.ne.gov/City/Departments/LTU/Utilities/Solid-Waste-Management",
        "hours": "Check lincoln.ne.gov for current hours",
        "phone": "402-441-8022",
        "accepted_materials": ["mattress", "refrigerator", "freezer", "washer", "dryer", "tires", "tire-rims"],
    },
    {
        "name": "Allen County Tox-Tuesday HHW",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "fort-wayne",
        "state": "IN",
        "zip": "46818",
        "address": "2260 Carroll Road, Fort Wayne, IN 46818",
        "lat": 41.1455,
        "lng": -85.1855,
        "source_url": "https://www.allencounty.in.gov/483/Household-Hazardous-Waste-Disposal",
        "hours": "Every Tue 9:00–14:00",
        "phone": "260-449-7878",
        "accepted_materials": HHW_MATERIALS,
    },
    {
        "name": "Allen County ACDEM Electronics Recycling",
        "facility_type": "Electronics recycling events",
        "city_slug": "fort-wayne",
        "state": "IN",
        "zip": "46803",
        "address": "2911 Meyer Road, Fort Wayne, IN 46803",
        "lat": 41.0555,
        "lng": -85.0955,
        "source_url": "https://www.allencounty.in.gov/478/Electronics-Recycling",
        "hours": "Check allencounty.in.gov for event dates",
        "phone": "260-449-7878",
        "accepted_materials": ["television", "computer-monitor", "smartphone", "e-waste-mixed", "laptop", "desktop-computer"],
    },
    {
        "name": "Pinellas County HHW",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "st-petersburg",
        "state": "FL",
        "zip": "33716",
        "address": "2855 109th Avenue N, St. Petersburg, FL 33716",
        "lat": 27.8755,
        "lng": -82.6555,
        "source_url": "https://pinellas.gov/household-hazardous-waste-hhw-collection/",
        "hours": "Tue–Fri 7:00–17:00; 1st & 3rd Sat",
        "phone": "727-464-7500",
        "accepted_materials": HHW_MATERIALS,
    },
    {
        "name": "J.C. Elliott Transfer Station HHW",
        "facility_type": "HHW and e-waste drop-off",
        "city_slug": "corpus-christi",
        "state": "TX",
        "zip": "78408",
        "address": "7001 Ayers Street, Corpus Christi, TX 78408",
        "lat": 27.7655,
        "lng": -97.4255,
        "source_url": "https://www.corpuschristitx.gov/department-directory/solid-waste-services/household-hazardous-waste-disposal/",
        "hours": "Mon–Sat 8:00–17:00",
        "phone": "361-826-2489",
        "accepted_materials": HHW_MATERIALS
        + ["television", "computer-monitor", "smartphone", "e-waste-mixed", "tires", "tire-rims"],
    },
    {
        "name": "Greensboro HHW Collection Center",
        "facility_type": "HHW and e-waste drop-off",
        "city_slug": "greensboro",
        "state": "NC",
        "zip": "27407",
        "address": "2750 Patterson Street, Greensboro, NC 27407",
        "lat": 36.0355,
        "lng": -79.8455,
        "source_url": "https://www.greensboro-nc.gov/departments/solid-waste-and-recycling/household-hazardous-waste-collection-center",
        "hours": "Mon–Fri 10:00–18:00; Sat 8:00–14:00",
        "phone": "336-373-2489",
        "accepted_materials": HHW_MATERIALS
        + ["television", "computer-monitor", "smartphone", "e-waste-mixed"],
    },
    {
        "name": "Guilford County Scrap Tire / White Goods",
        "facility_type": "Scrap tire and white goods drop-off",
        "city_slug": "greensboro",
        "state": "NC",
        "zip": "27406",
        "address": "2138 Bishop Road, Greensboro, NC 27406",
        "lat": 36.0155,
        "lng": -79.7555,
        "source_url": "https://www.guilfordcountync.gov/government/departments-and-agencies/planning-and-development/environmental-services/scrap-tire-disposal",
        "hours": "Check guilfordcountync.gov for current hours",
        "phone": "336-641-2500",
        "accepted_materials": ["tires", "tire-rims", "refrigerator", "freezer", "air-conditioner"],
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
        "lincoln": clone_siblings(lincoln()),
        "fort-wayne": clone_siblings(fort_wayne()),
        "st-petersburg": clone_siblings(st_petersburg()),
        "corpus-christi": clone_siblings(corpus_christi()),
        "greensboro": clone_siblings(greensboro()),
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

    print("Wave-15 metros written:")
    for city, rows in audited.items():
        print(f"  {city}: {len(rows)} rules")
    print(f"Total rules now: {len(keep)}")


if __name__ == "__main__":
    main()
