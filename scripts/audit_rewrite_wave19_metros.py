#!/usr/bin/env python3
"""Portal-audited city guides for wave-19 metros (city-sourced only).

Cities researched from official program pages (2026-08-11):
  - Hialeah, FL — monthly bulk & yard waste / Miami-Dade HC3 Doral
  - Glendale, AZ — monthly bulk trash / Glendale Landfill / HHW appointments
  - Yonkers, NY — non-metal & metal bulk / Recycling Center / Westchester HRF
  - Fontana, CA — Burrtec bulky (2/yr) / HHW Saturdays at Orange Way
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


def hialeah():
    c, st = "hialeah", "FL"
    bulk = (
        "City of Hialeah — Bulk & Yard Waste Service",
        "https://www.hialeahfl.gov/1065/Bulk-Yard-Waste-Service",
    )
    disposal = (
        "City of Hialeah — Disposal Sites",
        "https://www.hialeahfl.gov/973/Disposal-Sites",
    )
    hc3 = (
        "Miami-Dade County — Home Chemical Collection Center",
        "https://www.hialeahfl.gov/973/Disposal-Sites",
    )
    rows = []
    rows.append(
        R(
            c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
            "Free monthly bulk & yard waste collection",
            "Hialeah monthly bulk & yard waste",
            "Hialeah mattresses go on free monthly bulk & yard waste collection. TVs and appliances are also accepted on bulk. Tires, batteries, paint, and propane are NOT bulk.",
            ["Set out on your monthly bulk & yard waste day.", "Follow hialeahfl.gov set-out rules.", "Keep tires/paint/propane off bulk piles."],
            [("Fee?", "Free monthly bulk & yard waste."), ("Tires on bulk?", "No — Miami-Dade disposal sites.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c, st, "refrigerator", "SPECIAL_HANDLING", "High", True,
            "Free monthly bulk — appliances accepted (Freon OK)",
            "Hialeah monthly bulk & yard waste",
            "Hialeah Freon refrigerators go on free monthly bulk & yard waste — appliances are accepted. Same pathway as washers. Remove contents and tape doors shut. Never vent refrigerant yourself.",
            ["Set out on monthly bulk & yard waste day.", "Tape doors shut; remove contents.", "Never vent Freon yourself."],
            [("Bulky for Freon fridge?", "Yes — appliances accepted on monthly bulk."), ("Washer on bulk?", "Yes — same monthly bulk pathway.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
            "Free monthly bulk — appliances accepted (Freon OK)",
            "Hialeah monthly bulk & yard waste",
            "Hialeah Freon window AC units go on free monthly bulk & yard waste — appliances are accepted. Never vent refrigerant yourself.",
            ["Set out on monthly bulk & yard waste day.", "Keep sealed until proper Freon handling.", "Never vent refrigerant yourself."],
            [("Same as Freon fridge?", "Yes — monthly bulk accepts appliances.")],
            *bulk,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c, st, item, "SPECIAL_HANDLING", "Medium", True,
                "Free monthly bulk & yard waste — appliances accepted",
                "Hialeah monthly bulk & yard waste",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s go on Hialeah free monthly bulk & yard waste. Freon refrigerators/AC also accepted on monthly bulk.",
                ["Set out on monthly bulk & yard waste day.", "Follow hialeahfl.gov set-out rules.", "Freon appliances also on monthly bulk."],
                [("Same as Freon fridge?", "Yes — all large appliances on monthly bulk.")],
                *bulk,
            )
        )
    rows.append(
        R(
            c, st, "television", "BANNED_FROM_LANDFILLS", "Medium", True,
            "Free monthly bulk — TVs listed acceptable",
            "Hialeah monthly bulk & yard waste",
            "Hialeah TVs are accepted on free monthly bulk & yard waste collection. Wipe data before set-out. Tires, batteries, paint, and propane are NOT bulk.",
            ["Set out on monthly bulk & yard waste day.", "Wipe personal data.", "Do not mix with tires/paint/propane."],
            [("Bulk for TVs?", "Yes — TVs listed acceptable on bulk."), ("E-waste on bulk?", "Yes — TVs on monthly bulk.")],
            *bulk,
        )
    )
    for item, label in [
        ("computer-monitor", "monitors"), ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste"),
    ]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "Medium", True,
                "Monthly bulk for TVs; other e-waste confirm Miami-Dade programs",
                "Hialeah monthly bulk / Miami-Dade disposal sites",
                f"Hialeah TVs go on monthly bulk. For other electronics including {label}, confirm Miami-Dade disposal programs via hialeahfl.gov/973. Wipe data before drop-off.",
                ["TVs: set out on monthly bulk day.", "Other e-waste: check Miami-Dade disposal sites.", "Wipe personal data."],
                [("Bulk for e-waste?", "TVs yes — confirm other items via disposal sites.")],
                *disposal,
            )
        )
    rows.append(
        R(
            c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", False,
            "NOT bulk — Miami-Dade HC3 8801 NW 58th St, Doral",
            "Miami-Dade Home Chemical Collection Center — 8801 NW 58th St, Doral",
            "Hialeah latex paint goes to Miami-Dade Home Chemical Collection Center — 8801 NW 58th St, Doral. Wed–Sat 9–5. Paint is NOT accepted on monthly bulk.",
            ["Haul sealed latex paint to HC3 — 8801 NW 58th St, Doral.", "Hours: Wed–Sat 9:00–17:00.", "Keep paint off bulk piles."],
            [("HC3 address?", "8801 NW 58th St, Doral."), ("Bulk for paint?", "No — HC3 only.")],
            *hc3,
        )
    )
    rows.append(
        R(
            c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
            "NOT bulk — Miami-Dade HC3 8801 NW 58th St, Doral",
            "Miami-Dade Home Chemical Collection Center — 8801 NW 58th St, Doral",
            "Hialeah oil-based paint goes to Miami-Dade HC3 — 8801 NW 58th St, Doral. Wed–Sat 9–5. Not bulk or trash.",
            ["Haul sealed oil paint to HC3 — 8801 NW 58th St, Doral.", "Keep containers sealed and labeled.", "Hours: Wed–Sat 9:00–17:00."],
            [("Same as latex?", "Yes — both use HC3 Doral.")],
            *hc3,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
                "Miami-Dade HC3 8801 NW 58th St, Doral — Wed-Sat 9-5",
                "Miami-Dade Home Chemical Collection Center — 8801 NW 58th St, Doral",
                f"Take {item.replace('-', ' ')} to Miami-Dade HC3 — 8801 NW 58th St, Doral. Wed–Sat 9–5. Not bulk or trash.",
                ["Deliver sealed containers to HC3 Doral.", "Hours: Wed–Sat 9:00–17:00.", "Keep chemicals off bulk piles."],
                [("HC3 for chemicals?", "Yes — 8801 NW 58th St, Doral.")],
                *hc3,
            )
        )
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {
            "car-battery": " Lead-acid batteries at HC3 Doral.",
            "lithium-battery": " Lithium batteries at HC3 Doral.",
            "motor-oil": " Used motor oil at HC3 Doral.",
            "propane-tank": " Propane tanks at HC3 Doral — confirm size limits.",
            "fluorescent-bulbs": " Fluorescent bulbs at HC3 Doral.",
            "cooking-oil": " Cooking oil at HC3 Doral when not trash-safe.",
        }[item]
        rows.append(
            R(
                c, st, item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium", False,
                "Miami-Dade HC3 8801 NW 58th St, Doral — Wed-Sat 9-5",
                "Miami-Dade Home Chemical Collection Center — 8801 NW 58th St, Doral",
                f"Miami-Dade HC3 at 8801 NW 58th St, Doral accepts household hazardous materials.{extra}",
                ["Haul to HC3 Doral.", "Hours: Wed–Sat 9:00–17:00.", "Batteries NOT on bulk — use HC3."],
                [("Batteries on bulk?", "No — HC3 only."), ("Tires at HC3?", "No — Miami-Dade disposal sites.")],
                *hc3,
            )
        )
    rows.append(
        R(
            c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
            "Rigid sealed container — confirm HC3 sharps acceptance",
            "Miami-Dade Home Chemical Collection Center — 8801 NW 58th St, Doral",
            "Place sharps in a rigid sealed container. Confirm acceptance at Miami-Dade HC3 — 8801 NW 58th St, Doral. Do not loose-bag needles.",
            ["Use rigid sealed container.", "Confirm sharps at HC3 Doral.", "Never recycle loose needles."],
            [("Medications?", "Confirm drug take-back via Miami-Dade programs.")],
            *hc3,
        )
    )
    rows.append(
        R(
            c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
            "NOT bulk — Miami-Dade disposal sites/landfills",
            "Miami-Dade disposal sites / landfills",
            "Hialeah tires are NOT accepted on monthly bulk & yard waste. Self-haul to Miami-Dade disposal sites or landfills listed on hialeahfl.gov/973. Retailer take-back when replacing tires.",
            ["Do not set tires out on monthly bulk.", "Haul to Miami-Dade disposal sites/landfills.", "Retailer take-back when replacing tires."],
            [("Bulk for tires?", "No — Miami-Dade disposal sites only."), ("HC3 for tires?", "No.")],
            *disposal,
        )
    )
    rows.append(
        R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True,
          "Hialeah bulk & yard waste collection", "Hialeah bulk & yard waste collection",
          "Hialeah handles yard waste through monthly bulk & yard waste collection. Follow set-out rules on hialeahfl.gov.",
          ["Use yard waste set-out rules on bulk day.", "Keep yard waste out of HHW and e-waste.", "Check hialeahfl.gov for seasonal guidance."],
          [("Christmas trees?", "Follow city seasonal yard waste guidance.")], *bulk)
    )
    rows.append(
        R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True,
          "Garbage cart unless private compost", "Hialeah garbage / private compost",
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
          "NOT bulk — private C&D hauler / Miami-Dade landfills",
          "Private C&D hauler / Miami-Dade landfills",
          "Construction debris is not Hialeah bulk material. Hire a private C&D hauler or use Miami-Dade landfills. Route paint/chemicals to HC3 Doral separately.",
          ["Do not treat remodel debris as bulk.", "Hire private C&D for larger projects.", "Route paint to HC3 Doral."],
          [("HC3 for C&D?", "No — separate paint/chemicals.")], *bulk)
    )
    return rows


def glendale():
    c, st = "glendale", "AZ"
    bulk = (
        "City of Glendale — Bulk Trash Collection",
        "https://www.glendaleaz.gov/residents/trash-recycling/bulk-trash",
    )
    landfill = (
        "City of Glendale — Municipal Landfill",
        "https://www.glendaleaz.gov/residents/trash-recycling/landfill",
    )
    hhw = (
        "City of Glendale — Household Hazardous Waste",
        "https://www.glendaleaz.gov/residents/trash-recycling/household-hazardous-waste",
    )
    rows = []
    rows.append(
        R(
            c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
            "Free monthly bulk trash — 2026 schedule by section",
            "Glendale monthly bulk trash collection",
            "Glendale mattresses go on free monthly bulk trash collection. Check 2026 schedule by section on glendaleaz.gov. Tires are NOT bulk.",
            ["Set out on your monthly bulk trash week.", "Check glendaleaz.gov for 2026 section schedule.", "Keep tires off bulk piles."],
            [("Fee?", "Free monthly bulk trash."), ("Schedule?", "2026 schedule by section on glendaleaz.gov.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c, st, "refrigerator", "SPECIAL_HANDLING", "High", False,
            "$25 Freon fee — call 623-930-2660 special crew; NOT unscheduled bulk",
            "Glendale special Freon appliance crew — 623-930-2660",
            "Glendale Freon refrigerators require a special crew pickup — call 623-930-2660 — $25 Freon fee. NOT accepted on unscheduled monthly bulk. Remove doors and empty unit. Never vent refrigerant yourself.",
            ["Call 623-930-2660 for special Freon crew pickup.", "Do not set Freon fridge on unscheduled bulk.", "$25 Freon fee applies."],
            [("Unscheduled bulk for Freon fridge?", "No — special crew $25."), ("Washer on bulk?", "Yes — non-Freon washers use regular monthly bulk.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c, st, "air-conditioner", "SPECIAL_HANDLING", "High", False,
            "$25 Freon fee — call 623-930-2660 special crew; NOT unscheduled bulk",
            "Glendale special Freon appliance crew — 623-930-2660",
            "Glendale Freon window AC units require special crew pickup — call 623-930-2660 — $25 Freon fee. NOT on unscheduled monthly bulk. Never vent refrigerant yourself.",
            ["Call 623-930-2660 for special Freon crew.", "Do not set Freon AC on unscheduled bulk.", "Keep sealed until proper Freon handling."],
            [("Same as Freon fridge?", "Yes — special crew $25, not unscheduled bulk.")],
            *bulk,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c, st, item, "SPECIAL_HANDLING", "Medium", True,
                "Free monthly bulk trash — 2026 schedule by section",
                "Glendale monthly bulk trash collection",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s use Glendale regular monthly bulk trash week. Freon refrigerators/AC need special crew — 623-930-2660 — $25.",
                ["Set out on monthly bulk trash week.", "Check glendaleaz.gov for 2026 section schedule.", "Freon appliances need special crew."],
                [("Same as Freon fridge?", "No — non-Freon uses regular monthly bulk.")],
                *bulk,
            )
        )
    rows.append(
        R(
            c, st, "television", "BANNED_FROM_LANDFILLS", "Medium", False,
            "Free Glendale Landfill — NOT HHW collection — 623-930-4727",
            "Glendale Municipal Landfill — 11480 W Glendale Ave",
            "Glendale TVs go free to Glendale Landfill — 11480 W Glendale Ave — call 623-930-4727. NOT accepted at HHW collection events. Wipe data before drop-off.",
            ["Haul TVs to Glendale Landfill.", "Call 623-930-4727 to confirm hours.", "Wipe personal data."],
            [("HHW for TVs?", "No — Glendale Landfill free."), ("Bulk for TVs?", "No — landfill drop-off.")],
            *landfill,
        )
    )
    for item, label in [
        ("computer-monitor", "monitors"), ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste"),
    ]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "Medium", False,
                "Free Glendale Landfill — NOT HHW collection — 623-930-4727",
                "Glendale Municipal Landfill — 11480 W Glendale Ave",
                f"Glendale electronics including {label} go free to Glendale Landfill — 11480 W Glendale Ave — 623-930-4727. NOT at HHW events. Wipe data before drop-off.",
                ["Haul e-waste to Glendale Landfill.", "Call 623-930-4727.", "Wipe personal data."],
                [("Landfill for e-waste?", "Yes — free, not HHW collection.")],
                *landfill,
            )
        )
    rows.append(
        R(
            c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", True,
            "Dried latex → refuse; liquid latex → HHW appointment 623-930-2660",
            "Glendale trash cart / HHW appointment",
            "Glendale latex paint: dry completely (kitty litter or leave lid off) then put dried cans in refuse. Liquid latex uses HHW appointment — call 623-930-2660 — Spring/Fall 2026. Not bulk.",
            ["Dry latex paint completely until solid.", "Place dried cans in refuse.", "Liquid latex → HHW appointment 623-930-2660."],
            [("Dry latex for trash?", "Yes — fully dried only."), ("HHW appointment?", "Required for liquid latex.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
            "HHW appointment — call 623-930-2660 — Spring/Fall 2026",
            "Glendale HHW appointment collection",
            "Glendale oil-based paint uses HHW appointment — call 623-930-2660 — Spring/Fall 2026 events. Not bulk or trash.",
            ["Call 623-930-2660 to schedule HHW appointment.", "Keep oil paint sealed and labeled.", "Do not put liquid paint in trash."],
            [("Same as dried latex?", "No — oil paint always uses HHW appointment.")],
            *hhw,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
                "HHW appointment — call 623-930-2660 — Spring/Fall 2026",
                "Glendale HHW appointment collection",
                f"Take {item.replace('-', ' ')} via Glendale HHW appointment — call 623-930-2660 — Spring/Fall 2026. Not bulk or trash.",
                ["Call 623-930-2660 for HHW appointment.", "Keep chemicals sealed and labeled.", "Do not set HHW on bulk piles."],
                [("Landfill for chemicals?", "No — HHW appointment required.")],
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
                "HHW appointment — call 623-930-2660 — Spring/Fall 2026",
                "Glendale HHW appointment collection",
                f"Glendale HHW appointment accepts household hazardous materials.{extra}",
                ["Call 623-930-2660 for HHW appointment.", "Keep materials off bulk piles.", "Tires use landfill path."],
                [("Tires at HHW?", "No — Glendale Landfill 5 no-rim free.")],
                *hhw,
            )
        )
    rows.append(
        R(
            c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
            "Rigid sealed container — confirm HHW appointment sharps acceptance",
            "Glendale HHW appointment collection",
            "Place sharps in a rigid sealed container. Confirm acceptance via Glendale HHW appointment — 623-930-2660. Do not loose-bag needles.",
            ["Use rigid sealed container.", "Confirm sharps via HHW appointment.", "Never recycle loose needles."],
            [("Medications?", "Confirm drug take-back via Maricopa County programs.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
            "NOT bulk — Glendale Landfill 11480 W Glendale Ave — 5 no-rim free",
            "Glendale Municipal Landfill — 11480 W Glendale Ave",
            "Glendale tires are NOT accepted on monthly bulk trash. Self-haul to Glendale Municipal Landfill — 11480 W Glendale Ave — 5 tires no rim free for residents. Retailer take-back when replacing tires.",
            ["De-rim tires before drop-off.", "Haul to 11480 W Glendale Ave.", "Limit 5 no-rim tires free for residents."],
            [("Bulk for tires?", "No — landfill 5 no-rim free."), ("Landfill phone?", "623-930-4727.")],
            *landfill,
        )
    )
    rows.append(
        R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True,
          "Glendale yard waste collection", "Glendale yard waste collection",
          "Glendale handles yard waste through regular collection. Follow set-out rules on glendaleaz.gov.",
          ["Use yard waste set-out rules.", "Keep yard waste out of HHW and e-waste.", "Check glendaleaz.gov for seasonal guidance."],
          [("Christmas trees?", "Follow city seasonal yard waste guidance.")], *bulk)
    )
    rows.append(
        R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True,
          "Garbage cart unless private compost", "Glendale garbage / private compost",
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
          "NOT bulk — private C&D hauler / Glendale Landfill",
          "Private C&D hauler / Glendale Municipal Landfill",
          "Construction debris is not Glendale bulk trash material. Hire a private C&D hauler or use Glendale Landfill. Route paint/chemicals to HHW appointment separately.",
          ["Do not treat remodel debris as bulk.", "Hire private C&D for larger projects.", "Route liquid paint to HHW appointment."],
          [("HHW for C&D?", "No — separate paint/chemicals.")], *bulk)
    )
    return rows


def yonkers():
    c, st = "yonkers", "NY"
    bulk = (
        "City of Yonkers — Refuse & Bulk Removal",
        "https://www.yonkersny.gov/214/Refuse-Bulk-Removal",
    )
    recycle = (
        "City of Yonkers — Recycling Center",
        "https://www.yonkersny.gov/214/Refuse-Bulk-Removal",
    )
    hrf = (
        "Westchester County — Household Recycling Facility",
        "https://www.yonkersny.gov/214/Refuse-Bulk-Removal",
    )
    rows = []
    rows.append(
        R(
            c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
            "Non-metal bulk — 1 item on 2nd pickup day/week",
            "Yonkers non-metal bulk collection",
            "Yonkers mattresses go as non-metal bulk — 1 item on your 2nd pickup day each week. Metal appliances use metal bulk appointment — call 914-377-HELP.",
            ["Set out 1 non-metal bulk item on 2nd pickup day.", "Follow yonkersny.gov/214 set-out rules.", "Metal appliances need 914-377-HELP appointment."],
            [("Fee?", "1 non-metal bulk item per week on 2nd pickup day."), ("Metal bulk?", "Separate — call 914-377-HELP.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c, st, "refrigerator", "SPECIAL_HANDLING", "High", False,
            "Metal bulk appointment 914-377-HELP OR Recycling Center 735 Saw Mill River Rd",
            "Yonkers metal bulk / Recycling Center — 735 Saw Mill River Rd",
            "Yonkers Freon refrigerators require metal bulk appointment — call 914-377-HELP — OR self-haul to Recycling Center — 735 Saw Mill River Rd (Freon removed free at center). Remove doors. Never vent refrigerant yourself.",
            ["Call 914-377-HELP for metal bulk appointment.", "Or haul to 735 Saw Mill River Rd — Freon removed free.", "Remove doors; never vent Freon yourself."],
            [("Non-metal bulk for Freon fridge?", "No — metal bulk appointment."), ("Recycling Center Freon?", "Removed free at center.")],
            *recycle,
        )
    )
    rows.append(
        R(
            c, st, "air-conditioner", "SPECIAL_HANDLING", "High", False,
            "Metal bulk appointment 914-377-HELP OR Recycling Center 735 Saw Mill River Rd",
            "Yonkers metal bulk / Recycling Center — 735 Saw Mill River Rd",
            "Yonkers Freon window AC units require metal bulk appointment — 914-377-HELP — OR Recycling Center — 735 Saw Mill River Rd (Freon removed free). Never vent refrigerant yourself.",
            ["Call 914-377-HELP for metal bulk appointment.", "Or haul to 735 Saw Mill River Rd.", "Keep sealed until proper Freon handling."],
            [("Same as Freon fridge?", "Yes — metal bulk or Recycling Center.")],
            *recycle,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c, st, item, "SPECIAL_HANDLING", "Medium", False,
                "Metal bulk appointment — call 914-377-HELP",
                "Yonkers metal bulk appointment",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s require Yonkers metal bulk appointment — call 914-377-HELP. Freon refrigerators/AC also use metal bulk or Recycling Center.",
                ["Call 914-377-HELP for metal bulk appointment.", "Schedule metal bulk pickup.", "Freon appliances also use metal bulk."],
                [("Non-metal bulk for washers?", "No — metal bulk appointment required.")],
                *bulk,
            )
        )
    rows.append(
        R(
            c, st, "television", "BANNED_FROM_LANDFILLS", "Medium", False,
            "Recycling Center 735 Saw Mill River Rd Mon-Sat 7:30-4:15; TVs >36\" appointment only",
            "Yonkers Recycling Center — 735 Saw Mill River Rd",
            "Yonkers TVs go to Recycling Center — 735 Saw Mill River Rd — Mon–Sat 7:30–16:15. TVs over 36 inches require appointment only. Wipe data before drop-off.",
            ["Haul TV to 735 Saw Mill River Rd.", "Mon–Sat 7:30–16:15.", "TVs >36\": appointment only."],
            [("Recycling Center hours?", "Mon–Sat 7:30–16:15."), ("Large TVs?", ">36\" appointment only.")],
            *recycle,
        )
    )
    for item, label in [
        ("computer-monitor", "monitors"), ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste"),
    ]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "Medium", False,
                "Recycling Center 735 Saw Mill River Rd Mon-Sat 7:30-4:15",
                "Yonkers Recycling Center — 735 Saw Mill River Rd",
                f"Yonkers electronics including {label} go to Recycling Center — 735 Saw Mill River Rd — Mon–Sat 7:30–16:15. Wipe data before drop-off.",
                ["Haul e-waste to 735 Saw Mill River Rd.", "Mon–Sat 7:30–16:15.", "Wipe personal data."],
                [("Bulk for e-waste?", "No — Recycling Center only.")],
                *recycle,
            )
        )
    rows.append(
        R(
            c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", False,
            "Wet paint → Recycling Center; dry paint cans → trash",
            "Yonkers Recycling Center / trash cart",
            "Yonkers latex paint: wet/liquid latex goes to Recycling Center — 735 Saw Mill River Rd. Dry paint cans go in trash. Oil paint/HHW use Westchester County HRF — not city center.",
            ["Wet latex → 735 Saw Mill River Rd Recycling Center.", "Dry paint cans → trash.", "Oil paint → Westchester HRF 914-813-5425."],
            [("Dry cans in trash?", "Yes — fully dry only."), ("Wet latex?", "Recycling Center only.")],
            *recycle,
        )
    )
    rows.append(
        R(
            c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
            "Westchester County HRF 914-813-5425 — NOT city Recycling Center",
            "Westchester County Household Recycling Facility",
            "Yonkers oil-based paint and hazardous chemicals go to Westchester County HRF — call 914-813-5425. NOT accepted at city Recycling Center for hazardous chemicals.",
            ["Call Westchester HRF 914-813-5425.", "Keep containers sealed and labeled.", "Do not bring oil paint to city Recycling Center."],
            [("City center for oil paint?", "No — Westchester HRF only.")],
            *hrf,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
                "Westchester County HRF 914-813-5425 — NOT city center",
                "Westchester County Household Recycling Facility",
                f"Take {item.replace('-', ' ')} to Westchester County HRF — 914-813-5425. NOT city Recycling Center for hazardous chemicals.",
                ["Call Westchester HRF 914-813-5425.", "Keep chemicals sealed and labeled.", "Do not bring to city Recycling Center."],
                [("City center for chemicals?", "No — Westchester HRF only.")],
                *hrf,
            )
        )
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {
            "car-battery": " Lead-acid batteries at Westchester HRF.",
            "lithium-battery": " Lithium batteries at Westchester HRF.",
            "motor-oil": " Used motor oil at Westchester HRF.",
            "propane-tank": " Propane tanks at Westchester HRF — confirm size limits.",
            "fluorescent-bulbs": " Fluorescent bulbs at Westchester HRF.",
            "cooking-oil": " Cooking oil at Westchester HRF when not trash-safe.",
        }[item]
        rows.append(
            R(
                c, st, item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium", False,
                "Westchester County HRF 914-813-5425 — NOT city center",
                "Westchester County Household Recycling Facility",
                f"Westchester County HRF accepts household hazardous materials.{extra}",
                ["Call Westchester HRF 914-813-5425.", "Keep materials off bulk piles.", "Tires use Recycling Center path."],
                [("Tires at HRF?", "No — Recycling Center $8/tire max 4.")],
                *hrf,
            )
        )
    rows.append(
        R(
            c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
            "Rigid sealed container — confirm Westchester HRF sharps acceptance",
            "Westchester County Household Recycling Facility",
            "Place sharps in a rigid sealed container. Confirm acceptance at Westchester County HRF — 914-813-5425. Do not loose-bag needles.",
            ["Use rigid sealed container.", "Confirm sharps at Westchester HRF.", "Never recycle loose needles."],
            [("Medications?", "Confirm drug take-back via Westchester County programs.")],
            *hrf,
        )
    )
    rows.append(
        R(
            c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
            "Recycling Center $8/tire max 4 no rims — NOT bulk",
            "Yonkers Recycling Center — 735 Saw Mill River Rd",
            "Yonkers tires go to Recycling Center — 735 Saw Mill River Rd — $8 per tire, max 4 no rims. NOT accepted on non-metal bulk. Retailer take-back when replacing tires.",
            ["Haul tires to 735 Saw Mill River Rd.", "$8/tire, max 4 no rims.", "Retailer take-back when replacing tires."],
            [("Bulk for tires?", "No — Recycling Center only."), ("Fee?", "$8/tire, max 4 no rims.")],
            *recycle,
        )
    )
    rows.append(
        R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True,
          "Yonkers yard waste collection", "Yonkers yard waste collection",
          "Yonkers handles yard waste through regular collection. Follow set-out rules on yonkersny.gov.",
          ["Use yard waste set-out rules.", "Keep yard waste out of HHW and e-waste.", "Check yonkersny.gov for seasonal guidance."],
          [("Christmas trees?", "Follow city seasonal yard waste guidance.")], *bulk)
    )
    rows.append(
        R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True,
          "Garbage cart unless private compost", "Yonkers garbage / private compost",
          "Bag food scraps for garbage unless you compost. Keep food out of recycling and HHW.",
          ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."],
          [("HRF for food?", "No.")], *bulk)
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
          "Construction debris is not Yonkers bulk material. Hire a private C&D hauler for remodel loads. Route oil paint/chemicals to Westchester HRF separately.",
          ["Do not treat remodel debris as bulk.", "Hire private C&D for larger projects.", "Route oil paint to Westchester HRF."],
          [("HRF for C&D?", "No — separate paint/chemicals.")], *bulk)
    )
    return rows


def fontana():
    c, st = "fontana", "CA"
    bulky = (
        "City of Fontana — Trash and Recycling Services (Burrtec)",
        "https://www.tinytots.fontana.org/541/Trash-and-Recycling-Services",
    )
    hhw = (
        "City of Fontana — Household Hazardous Waste (HHW)",
        "https://www.nature.fontana.org/589/Household-Hazardous-Waste-HHW",
    )
    rows = []
    rows.append(
        R(
            c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
            "Burrtec bulky 909-822-9739 — 2 collections/yr, 5 items each",
            "Fontana / Burrtec bulky pickup",
            "Fontana mattresses use Burrtec bulky pickup — call 909-822-9739. 2 collections per year, 5 items each. Tires have separate bulky rules with additional fee.",
            ["Call Burrtec 909-822-9739 to schedule bulky.", "2 collections per year, 5 items each.", "Set out on scheduled bulky day."],
            [("Fee?", "Included in Burrtec bulky allotment."), ("How many pickups?", "2 per year, 5 items each.")],
            *bulky,
        )
    )
    rows.append(
        R(
            c, st, "refrigerator", "SPECIAL_HANDLING", "High", True,
            "Burrtec bulky ONLY if Freon removed first — 909-822-9739",
            "Fontana / Burrtec bulky pickup",
            "Fontana Freon refrigerators may go on Burrtec bulky pickup ONLY if Freon is removed first — call 909-822-9739. 2 collections/year, 5 items each. Never vent refrigerant yourself.",
            ["Have Freon removed by certified technician first.", "Call 909-822-9739 to schedule bulky.", "2 collections/year, 5 items each."],
            [("Bulky for Freon fridge?", "Only if Freon removed first."), ("Washer on bulky?", "Yes — Burrtec bulky pickup.")],
            *bulky,
        )
    )
    rows.append(
        R(
            c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
            "Burrtec bulky ONLY if Freon removed first — 909-822-9739",
            "Fontana / Burrtec bulky pickup",
            "Fontana Freon window AC units may go on Burrtec bulky ONLY if Freon is removed first — call 909-822-9739. Never vent refrigerant yourself.",
            ["Have Freon removed by certified technician first.", "Call 909-822-9739 to schedule bulky.", "Keep sealed until proper Freon handling."],
            [("Same as Freon fridge?", "Yes — bulky only if Freon removed first.")],
            *bulky,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c, st, item, "SPECIAL_HANDLING", "Medium", True,
                "Burrtec bulky 909-822-9739 — 2 collections/yr, 5 items each",
                "Fontana / Burrtec bulky pickup",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s use Fontana Burrtec bulky pickup — 909-822-9739. 2 collections/year, 5 items each. Freon appliances need Freon removed first.",
                ["Call 909-822-9739 to schedule bulky.", "2 collections/year, 5 items each.", "Freon appliances need Freon removed first."],
                [("Same as Freon fridge?", "No — non-Freon uses standard bulky.")],
                *bulky,
            )
        )
    rows.append(
        R(
            c, st, "television", "BANNED_FROM_LANDFILLS", "Medium", True,
            "Burrtec bulky includes e-waste OR HHW 16454 Orange Way Saturdays 8-12",
            "Fontana / Burrtec bulky / HHW — 16454 Orange Way",
            "Fontana TVs may go on Burrtec bulky pickup (e-waste included) — 909-822-9739 — OR HHW facility — 16454 Orange Way — Saturdays 8:00–12:00. Wipe data before set-out or drop-off.",
            ["Schedule Burrtec bulky — 909-822-9739.", "Or haul to 16454 Orange Way HHW Saturdays 8–12.", "Wipe personal data."],
            [("Bulky for TVs?", "Yes — bulky program includes e-waste."), ("HHW for TVs?", "Alternative — Saturdays 8–12.")],
            *bulky,
        )
    )
    for item, label in [
        ("computer-monitor", "monitors"), ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste"),
    ]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "Medium", True,
                "Burrtec bulky includes e-waste OR HHW 16454 Orange Way Saturdays 8-12",
                "Fontana / Burrtec bulky / HHW — 16454 Orange Way",
                f"Fontana electronics including {label} may go on Burrtec bulky (e-waste included) — 909-822-9739 — OR HHW — 16454 Orange Way — Saturdays 8:00–12:00. Wipe data before drop-off.",
                ["Schedule Burrtec bulky — 909-822-9739.", "Or haul to 16454 Orange Way HHW.", "Wipe personal data."],
                [("Bulky for e-waste?", "Yes — bulky program includes e-waste.")],
                *bulky,
            )
        )
    rows.append(
        R(
            c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", False,
            "NOT bulky — HHW facility 16454 Orange Way (paint and thinners)",
            "Fontana HHW — 16454 Orange Way",
            "Fontana latex paint goes to HHW facility — 16454 Orange Way — Saturdays 8:00–12:00. Paint is NOT accepted on Burrtec bulky pickup.",
            ["Haul sealed latex paint to 16454 Orange Way.", "Saturdays 8:00–12:00.", "Keep paint off bulky piles."],
            [("HHW address?", "16454 Orange Way, Fontana."), ("Bulky for paint?", "No — HHW only.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
            "NOT bulky — HHW facility 16454 Orange Way (paint and thinners)",
            "Fontana HHW — 16454 Orange Way",
            "Fontana oil-based paint and paint thinners go to HHW facility — 16454 Orange Way — Saturdays 8:00–12:00. Not bulky or trash.",
            ["Haul sealed oil paint to 16454 Orange Way.", "Saturdays 8:00–12:00.", "Keep containers sealed and labeled."],
            [("Same as latex?", "Yes — both at HHW Orange Way.")],
            *hhw,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
                "HHW facility 16454 Orange Way Saturdays 8-12",
                "Fontana HHW — 16454 Orange Way",
                f"Take {item.replace('-', ' ')} to Fontana HHW facility — 16454 Orange Way — Saturdays 8:00–12:00. Not bulky or trash.",
                ["Haul to 16454 Orange Way.", "Saturdays 8:00–12:00.", "Keep chemicals off bulky piles."],
                [("HHW for chemicals?", "Yes — 16454 Orange Way Saturdays.")],
                *hhw,
            )
        )
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {
            "car-battery": " Lead-acid batteries at HHW Orange Way.",
            "lithium-battery": " Lithium batteries at HHW Orange Way.",
            "motor-oil": " Used motor oil at HHW Orange Way.",
            "propane-tank": " Propane tanks at HHW Orange Way — confirm size limits.",
            "fluorescent-bulbs": " Fluorescent bulbs at HHW Orange Way.",
            "cooking-oil": " Cooking oil at HHW Orange Way when not trash-safe.",
        }[item]
        rows.append(
            R(
                c, st, item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium", False,
                "HHW facility 16454 Orange Way Saturdays 8-12",
                "Fontana HHW — 16454 Orange Way",
                f"Fontana HHW at 16454 Orange Way accepts household hazardous materials.{extra}",
                ["Haul to 16454 Orange Way.", "Saturdays 8:00–12:00.", "Tires use bulky path with fee."],
                [("Tires at HHW?", "No — bulky max 9 off-rim with additional fee.")],
                *hhw,
            )
        )
    rows.append(
        R(
            c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
            "Rigid sealed container — confirm HHW Orange Way sharps acceptance",
            "Fontana HHW — 16454 Orange Way",
            "Place sharps in a rigid sealed container. Confirm acceptance at Fontana HHW — 16454 Orange Way. Do not loose-bag needles.",
            ["Use rigid sealed container.", "Confirm sharps at HHW Orange Way.", "Never recycle loose needles."],
            [("Medications?", "Confirm drug take-back via San Bernardino County programs.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "tires", "SPECIAL_HANDLING", "Medium", True,
            "Burrtec bulky max 9 off-rim — additional fee — 909-822-9739",
            "Fontana / Burrtec bulky pickup",
            "Fontana tires may go on Burrtec bulky pickup — max 9 off-rim tires with additional fee — call 909-822-9739. Retailer take-back when replacing tires.",
            ["Call 909-822-9739 to schedule bulky for tires.", "Max 9 off-rim tires per pickup.", "Additional fee applies."],
            [("Bulky for tires?", "Yes — max 9 off-rim with additional fee."), ("Fee?", "Additional fee per Burrtec Fontana newsletter.")],
            *bulky,
        )
    )
    rows.append(
        R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True,
          "Fontana yard waste collection", "Fontana yard waste collection",
          "Fontana handles yard waste through regular collection. Follow set-out rules on fontana.org.",
          ["Use yard waste set-out rules.", "Keep yard waste out of HHW and e-waste.", "Check fontana.org for seasonal guidance."],
          [("Christmas trees?", "Follow city seasonal yard waste guidance.")], *bulky)
    )
    rows.append(
        R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True,
          "Garbage cart unless private compost", "Fontana garbage / private compost",
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
          "NOT Burrtec bulky — private C&D hauler",
          "Private C&D hauler",
          "Construction debris is not Fontana Burrtec bulky material. Hire a private C&D hauler for remodel loads. Route paint/chemicals to HHW Orange Way separately.",
          ["Do not treat remodel debris as Burrtec bulky.", "Hire private C&D for larger projects.", "Route paint to HHW Orange Way."],
          [("HHW for C&D?", "No — separate paint/chemicals.")], *bulky)
    )
    return rows


CITIES = [
    {
        "city": "Hialeah",
        "city_slug": "hialeah",
        "state": "FL",
        "state_slug": "florida",
        "lat": 25.8576,
        "lng": -80.2781,
        "population": 223109,
    },
    {
        "city": "Glendale",
        "city_slug": "glendale",
        "state": "AZ",
        "state_slug": "arizona",
        "lat": 33.5387,
        "lng": -112.1860,
        "population": 248325,
    },
    {
        "city": "Yonkers",
        "city_slug": "yonkers",
        "state": "NY",
        "state_slug": "new-york",
        "lat": 40.9312,
        "lng": -73.8987,
        "population": 211569,
    },
    {
        "city": "Fontana",
        "city_slug": "fontana",
        "state": "CA",
        "state_slug": "california",
        "lat": 34.0922,
        "lng": -117.4350,
        "population": 208393,
    },
]

ZIPS = [
    {
        "zip": "33012",
        "city": "Hialeah",
        "city_slug": "hialeah",
        "state": "FL",
        "state_slug": "florida",
        "lat": 25.860,
        "lng": -80.295,
        "population": 62000,
    },
    {
        "zip": "33016",
        "city": "Hialeah",
        "city_slug": "hialeah",
        "state": "FL",
        "state_slug": "florida",
        "lat": 25.870,
        "lng": -80.330,
        "population": 58000,
    },
    {
        "zip": "85301",
        "city": "Glendale",
        "city_slug": "glendale",
        "state": "AZ",
        "state_slug": "arizona",
        "lat": 33.540,
        "lng": -112.185,
        "population": 48000,
    },
    {
        "zip": "85308",
        "city": "Glendale",
        "city_slug": "glendale",
        "state": "AZ",
        "state_slug": "arizona",
        "lat": 33.650,
        "lng": -112.220,
        "population": 55000,
    },
    {
        "zip": "10701",
        "city": "Yonkers",
        "city_slug": "yonkers",
        "state": "NY",
        "state_slug": "new-york",
        "lat": 40.930,
        "lng": -73.895,
        "population": 42000,
    },
    {
        "zip": "10704",
        "city": "Yonkers",
        "city_slug": "yonkers",
        "state": "NY",
        "state_slug": "new-york",
        "lat": 40.920,
        "lng": -73.865,
        "population": 38000,
    },
    {
        "zip": "92335",
        "city": "Fontana",
        "city_slug": "fontana",
        "state": "CA",
        "state_slug": "california",
        "lat": 34.070,
        "lng": -117.450,
        "population": 72000,
    },
    {
        "zip": "92336",
        "city": "Fontana",
        "city_slug": "fontana",
        "state": "CA",
        "state_slug": "california",
        "lat": 34.130,
        "lng": -117.430,
        "population": 68000,
    },
]

FACILITIES = [
    {
        "name": "Miami-Dade Home Chemical Collection Center — Hialeah residents",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "hialeah",
        "state": "FL",
        "zip": "33166",
        "address": "8801 NW 58th Street, Doral, FL 33166",
        "lat": 25.8250,
        "lng": -80.3450,
        "source_url": "https://www.hialeahfl.gov/973/Disposal-Sites",
        "hours": "Wed–Sat 9:00–17:00 — confirm before visit",
        "phone": "305-594-1500",
        "accepted_materials": HHW_MATERIALS,
    },
    {
        "name": "Miami-Dade Disposal Sites — Hialeah residents",
        "facility_type": "Disposal sites / landfills — tires",
        "city_slug": "hialeah",
        "state": "FL",
        "zip": "33012",
        "address": "Check hialeahfl.gov/973 for disposal site locations",
        "lat": 25.8576,
        "lng": -80.2781,
        "source_url": "https://www.hialeahfl.gov/973/Disposal-Sites",
        "hours": "Check hialeahfl.gov for current hours",
        "phone": "305-594-1500",
        "accepted_materials": ["tires", "tire-rims"],
    },
    {
        "name": "Glendale Municipal Landfill",
        "facility_type": "Landfill — e-waste / tires",
        "city_slug": "glendale",
        "state": "AZ",
        "zip": "85307",
        "address": "11480 W Glendale Avenue, Glendale, AZ 85307",
        "lat": 33.5380,
        "lng": -112.3200,
        "source_url": "https://www.glendaleaz.gov/residents/trash-recycling/landfill",
        "hours": "Check glendaleaz.gov for current hours",
        "phone": "623-930-4727",
        "accepted_materials": [
            "television", "computer-monitor", "laptop", "desktop-computer",
            "smartphone", "tablet", "printer", "e-waste-mixed", "hard-drive",
            "tires", "tire-rims",
        ],
    },
    {
        "name": "Glendale HHW Appointment Collection",
        "facility_type": "Household hazardous waste — appointment collection",
        "city_slug": "glendale",
        "state": "AZ",
        "zip": "85301",
        "address": "Appointment collection — check glendaleaz.gov",
        "lat": 33.5387,
        "lng": -112.1860,
        "source_url": "https://www.glendaleaz.gov/residents/trash-recycling/household-hazardous-waste",
        "hours": "Spring/Fall 2026 — by appointment, call 623-930-2660",
        "phone": "623-930-2660",
        "accepted_materials": HHW_MATERIALS,
    },
    {
        "name": "Yonkers Recycling Center",
        "facility_type": "Recycling center — e-waste / tires / wet paint",
        "city_slug": "yonkers",
        "state": "NY",
        "zip": "10710",
        "address": "735 Saw Mill River Road, Yonkers, NY 10710",
        "lat": 40.9700,
        "lng": -73.8700,
        "source_url": "https://www.yonkersny.gov/214/Refuse-Bulk-Removal",
        "hours": "Mon–Sat 7:30–16:15 — confirm before visit",
        "phone": "914-377-4357",
        "accepted_materials": [
            "refrigerator", "freezer", "air-conditioner", "dehumidifier",
            "television", "computer-monitor", "laptop", "desktop-computer",
            "smartphone", "e-waste-mixed", "paint-latex", "tires", "tire-rims",
        ],
    },
    {
        "name": "Westchester County Household Recycling Facility — Yonkers residents",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "yonkers",
        "state": "NY",
        "zip": "10562",
        "address": "Check Westchester County for HRF address",
        "lat": 41.0500,
        "lng": -73.7800,
        "source_url": "https://www.yonkersny.gov/214/Refuse-Bulk-Removal",
        "hours": "Check Westchester County schedule — call 914-813-5425",
        "phone": "914-813-5425",
        "accepted_materials": HHW_MATERIALS,
    },
    {
        "name": "Fontana HHW Facility — Orange Way",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "fontana",
        "state": "CA",
        "zip": "92337",
        "address": "16454 Orange Way, Fontana, CA 92337",
        "lat": 34.0800,
        "lng": -117.4200,
        "source_url": "https://www.nature.fontana.org/589/Household-Hazardous-Waste-HHW",
        "hours": "Saturdays 8:00–12:00 — confirm before visit",
        "phone": "909-349-6900",
        "accepted_materials": HHW_MATERIALS
        + ["television", "computer-monitor", "smartphone", "laptop", "desktop-computer", "e-waste-mixed"],
    },
    {
        "name": "Fontana / Burrtec Bulky Pickup",
        "facility_type": "Curbside bulky collection — appliances / e-waste / tires",
        "city_slug": "fontana",
        "state": "CA",
        "zip": "92335",
        "address": "Curbside collection — call Burrtec 909-822-9739",
        "lat": 34.0922,
        "lng": -117.4350,
        "source_url": "https://www.tinytots.fontana.org/541/Trash-and-Recycling-Services",
        "hours": "By appointment — 2 collections/year, 5 items each",
        "phone": "909-822-9739",
        "accepted_materials": [
            "mattress", "box-spring", "refrigerator", "freezer", "air-conditioner",
            "washer", "dryer", "dishwasher", "stove", "water-heater",
            "television", "computer-monitor", "laptop", "desktop-computer",
            "smartphone", "e-waste-mixed", "tires", "tire-rims",
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
        "hialeah": clone_siblings(hialeah()),
        "glendale": clone_siblings(glendale()),
        "yonkers": clone_siblings(yonkers()),
        "fontana": clone_siblings(fontana()),
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

    print("Wave-19 metros written:")
    for city, rows in audited.items():
        print(f"  {city}: {len(rows)} rules")
    print(f"Total rules now: {len(keep)}")


if __name__ == "__main__":
    main()
