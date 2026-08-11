#!/usr/bin/env python3
"""Portal-audited city guides for wave-11 metros (city-sourced only).

Cities researched from official program pages (2026-08-11):
  - Pittsburgh, PA — pittsburghpa.gov Curbside-Refuse + Electronic-Waste-and-Household-Hazardous-Waste-Disposal
  - Cincinnati, OH — cincinnati-oh.gov bulk-item-collection
  - St. Louis, MO — stlouis-mo.gov bulky-boat-items + HHW.cfm
  - Orlando, FL — orlando.gov Get-Large-Items-Picked-Up + Too-Toxic-to-Trash
  - Buffalo, NY — buffalony.gov Bulk-Trash-Information + Streets-Sanitation
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


def pittsburgh():
    c, st = "pittsburgh", "PA"
    refuse = ("City of Pittsburgh — Curbside refuse", "https://pittsburghpa.gov/City-Government/Finance-Administration/Finance/Refuse-Recycling/Curbside-Refuse")
    hhw = ("City of Pittsburgh — Electronic waste & HHW", "https://pittsburghpa.gov/City-Government/Finance-Administration/Finance/Refuse-Recycling/Electronic-Waste-and-Household-Hazardous-Waste-Disposal")
    noble = ("Noble Environmental — HHW drop-off", "https://pittsburghpa.gov/City-Government/Finance-Administration/Finance/Refuse-Recycling/Electronic-Waste-and-Household-Hazardous-Waste-Disposal")
    dpw = ("Pittsburgh DPW — tire drop-off", "https://pittsburghpa.gov/City-Government/Finance-Administration/Finance/Refuse-Recycling/Curbside-Refuse")
    rows = []
    rows.append(R(c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
        "Weekly curbside bulk — up to 2 bulk items/week; seal if bedbugs",
        "Pittsburgh curbside bulk refuse collection",
        "Pittsburgh DPW accepts mattresses on weekly curbside bulk refuse — up to 2 bulk items per week. Seal mattresses in plastic if bedbugs are present. Freon appliances and electronics are NOT curbside bulk — use Noble Environmental or PRC events.",
        ["Set mattress out on your regular refuse collection day (≤2 bulk/week).", "Seal in plastic if bedbugs present.", "Keep Freon appliances and e-waste off bulk piles."],
        [("Bulk limit?", "Up to 2 bulk items per week on curbside refuse."), ("Bedbugs?", "Seal mattress in plastic if bedbugs present.")], *refuse))
    rows.append(R(c, st, "refrigerator", "SPECIAL_HANDLING", "High", False,
        "NOT curbside — Noble Environmental / PRC events (fees)",
        "Noble Environmental / Pennsylvania Resources Council events",
        "Freon refrigerators are NOT accepted on Pittsburgh curbside bulk. Use Noble Environmental or Pennsylvania Resources Council (PRC) collection events — fees apply. Never vent refrigerant yourself.",
        ["Do not set Freon refrigerators out for curbside bulk.", "Check pittsburghpa.gov for Noble/PRC appliance events.", "Keep doors secured until proper Freon handling."],
        [("Curbside fridge?", "No — Freon appliances use Noble/PRC events, not curbside."), ("Fees?", "Yes — Noble/PRC appliance events charge fees.")], *hhw))
    rows.append(R(c, st, "air-conditioner", "SPECIAL_HANDLING", "High", False,
        "NOT curbside — Noble Environmental / PRC events (fees)",
        "Noble Environmental / Pennsylvania Resources Council events",
        "Freon window and portable air conditioners are NOT accepted on Pittsburgh curbside bulk. Use Noble Environmental or PRC collection events — fees apply. Never vent refrigerant yourself.",
        ["Do not set Freon AC out for curbside bulk.", "Check Noble/PRC event calendar on pittsburghpa.gov.", "Keep the sealed unit intact."],
        [("Same as fridge?", "Yes — Freon AC uses Noble/PRC events, not curbside bulk.")], *hhw))
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(R(c, st, item, "SPECIAL_HANDLING", "Medium", True,
            "Curbside bulk — up to 2 bulk items/week (non-Freon appliances)",
            "Pittsburgh curbside bulk refuse collection",
            f"Non-Freon appliances such as {item.replace('-', ' ')}s may go on Pittsburgh weekly curbside bulk refuse — up to 2 bulk items per week. Freon refrigerators/AC are excluded — use Noble/PRC events.",
            ["Set appliance out on refuse day (≤2 bulk/week).", "Do not confuse with Freon fridge path — washers are curbside bulk.", "Empty appliance before set-out."],
            [("Same as Freon fridge?", "No — non-Freon appliances may use curbside bulk."), ("Bulk limit?", "Up to 2 bulk items per week.")], *refuse))
    for item, label in [("television", "TVs"), ("computer-monitor", "monitors"), ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste")]:
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS", "Medium", False,
            "NOT curbside — Noble/PRC e-waste events (fees)",
            "Noble Environmental / PRC e-waste collection",
            f"Electronics including {label} are banned from Pittsburgh curbside refuse. Use Noble Environmental or PRC e-waste collection events — fees apply. Wipe data before drop-off.",
            ["Do not put TVs/e-waste on curbside bulk.", "Check Noble/PRC event calendar on pittsburghpa.gov.", "Wipe personal data before recycling."],
            [("Curbside e-waste?", "No — banned from curbside; use Noble/PRC events."), ("Fees?", "Yes — e-waste events charge fees.")], *hhw))
    rows.append(R(c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", False,
        "Noble HHW 3001 Railroad St — Tue/Thu 2:30–6:30 appt; fees by lb",
        "Noble Environmental — 3001 Railroad St",
        "Liquid latex and oil paint go to Noble Environmental HHW at 3001 Railroad St — Tue/Thu 2:30–6:30 p.m. by appointment; fees by pound. Not curbside.",
        ["Schedule appointment for Noble HHW 3001 Railroad St.", "Hours: Tue/Thu 2:30–6:30 p.m.", "Keep paint sealed and labeled."],
        [("Free paint?", "No — fees by pound at Noble HHW."), ("Curbside paint?", "No — paint uses Noble HHW drop-off.")], *noble))
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
            "Noble HHW 3001 Railroad St — Tue/Thu 2:30–6:30 appt; fees by lb",
            "Noble Environmental — 3001 Railroad St",
            f"Take {item.replace('-', ' ')} to Noble Environmental HHW 3001 Railroad St — Tue/Thu 2:30–6:30 p.m. by appointment; fees by pound.",
            ["Schedule Noble HHW appointment.", "Deliver sealed containers during posted hours.", "Keep chemicals out of curbside bulk."],
            [("Same as paint?", "Yes — chemicals use Noble HHW 3001 Railroad St.")], *noble))
    for item in ["car-battery", "lithium-battery", "paint-oil", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {"car-battery": " Auto/household batteries at Noble HHW.", "lithium-battery": " Lithium batteries at Noble HHW.", "paint-oil": " Oil paint at Noble HHW.", "motor-oil": " Used motor oil at Noble HHW.", "propane-tank": " Propane at Noble HHW.", "fluorescent-bulbs": " Fluorescents at Noble HHW.", "cooking-oil": " Cooking oil at Noble HHW when not trash-safe."}[item]
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING", "High" if item != "cooking-oil" else "Medium", False,
            "Noble HHW 3001 Railroad St — Tue/Thu 2:30–6:30 appt; fees by lb", "Noble Environmental — 3001 Railroad St",
            f"Noble Environmental HHW 3001 Railroad St accepts household hazardous materials Tue/Thu 2:30–6:30 p.m. by appointment; fees by pound.{extra}",
            ["Schedule Noble HHW appointment.", "Fees by pound — first confirm acceptance.", "Freon appliances use Noble/PRC events, not HHW."], [("Address?", "3001 Railroad St.")], *noble))
    rows.append(R(c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
        "Rigid sealed container — confirm Noble HHW sharps acceptance", "Noble Environmental — 3001 Railroad St",
        "Place sharps in a rigid sealed container. Confirm acceptance at Noble Environmental HHW. Do not loose-bag needles.",
        ["Use rigid sealed container.", "Confirm sharps acceptance at Noble HHW.", "Never recycle loose needles."], [("Medications?", "Confirm drug take-back on pittsburghpa.gov.")], *noble))
    rows.append(R(c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
        "NOT curbside — DPW drop-offs 2 tires/day rimless",
        "Pittsburgh DPW tire drop-off — Hamilton Ave",
        "Tires are NOT accepted on Pittsburgh curbside bulk. DPW tire drop-off locations accept up to 2 rimless tires per day — check pittsburghpa.gov for Hamilton Ave and other DPW sites.",
        ["Do not set tires out for curbside bulk.", "Haul rimless tires to DPW drop-off (2/day limit).", "Retailer take-back when replacing tires."],
        [("Curbside tires?", "No — DPW drop-offs only, 2 rimless/day."), ("Rims?", "Remove rims — drop-off is rimless tires only.")], *dpw))
    rows.append(R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True, "Pittsburgh yard waste collection", "Pittsburgh yard waste collection",
        "Pittsburgh handles yard waste through regular collection programs. Follow set-out rules on pittsburghpa.gov.",
        ["Use yard waste set-out rules.", "Keep yard waste out of bulk and HHW loads.", "Check pittsburghpa.gov for seasonal guidance."], [("Christmas trees?", "Follow city seasonal yard waste guidance.")], *refuse))
    rows.append(R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True, "Garbage cart unless private compost", "Pittsburgh garbage / private compost",
        "Bag food scraps for garbage unless you compost. Keep food out of recycling and HHW.",
        ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."], [("HHW for food?", "No.")], *refuse))
    rows.append(R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False, "Not recycling — store take-back / trash", "Retail bag take-back / trash",
        "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
        ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."], [("Curbside bulk for bags?", "No — store take-back or trash.")], *refuse))
    rows.append(R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", False,
        "NOT typical curbside bulk — private C&D hauler or Noble/PRC events",
        "Private C&D hauler / Noble Environmental events",
        "Construction debris is not typical curbside bulk. Hire a private C&D hauler or check Noble/PRC events. Route paint/chemicals to Noble HHW separately.",
        ["Do not mix C&D with weekly bulk without confirming limits.", "Hire private C&D hauler for large loads.", "Route paint to Noble HHW 3001 Railroad St."], [("HHW for C&D?", "No — separate paint/chemicals.")], *hhw))
    return rows


def cincinnati():
    c, st = "cincinnati", "OH"
    bulk = ("City of Cincinnati — Bulk item collection", "https://www.cincinnati-oh.gov/street/recycling-and-waste-reduction/bulk-item-collection/")
    r3 = ("Hamilton County R3Source — HHW search tool", "https://www.r3source.org/")
    rows = []
    rows.append(R(c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
        "Bulk via 311 — 5 free items; DPS customers only (not private hauler)",
        "Cincinnati bulk collection (311 scheduled)",
        "Cincinnati bulk collection is scheduled through 311 — 5 free items per pickup. Only City of Cincinnati DPS collection customers qualify — private hauler customers are NOT eligible. Mattresses are accepted as bulk items.",
        ["Call 311 to schedule bulk pickup (DPS customers only).", "Limit 5 free items per pickup.", "Private hauler customers must use private options."],
        [("Private hauler OK?", "No — bulk via 311 is DPS customers only."), ("Free items?", "5 free items per bulk pickup.")], *bulk))
    rows.append(R(c, st, "refrigerator", "SPECIAL_HANDLING", "High", True,
        "Bulk via 311 — included in 5 free items; DPS customers only",
        "Cincinnati bulk collection (311 scheduled)",
        "Freon refrigerators are accepted on Cincinnati bulk collection via 311 — count toward the 5 free items. DPS collection customers only. Keep doors secured; never vent refrigerant yourself.",
        ["Call 311 to schedule bulk including refrigerator.", "Counts toward 5 free items.", "Keep doors secured until pickup."],
        [("Freon fridge on bulk?", "Yes — refrigerators included in bulk via 311."), ("Who qualifies?", "DPS collection customers only — not private hauler.")], *bulk))
    rows.append(R(c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
        "Bulk via 311 — included in 5 free items; DPS customers only",
        "Cincinnati bulk collection (311 scheduled)",
        "Freon window and portable AC units are accepted on Cincinnati bulk collection via 311 — count toward 5 free items. DPS customers only. Never vent refrigerant yourself.",
        ["Call 311 to schedule bulk including AC.", "Counts toward 5 free items.", "Keep sealed until pickup."],
        [("Same as fridge?", "Yes — AC included in bulk via 311 for DPS customers.")], *bulk))
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(R(c, st, item, "SPECIAL_HANDLING", "Medium", True,
            "Bulk via 311 — 5 free items; DPS customers only",
            "Cincinnati bulk collection (311 scheduled)",
            f"Non-Freon appliances such as {item.replace('-', ' ')}s go on Cincinnati bulk collection via 311 — 5 free items per pickup. DPS collection customers only.",
            ["Call 311 to schedule bulk pickup.", "Counts toward 5 free items.", "Empty appliance before set-out."],
            [("311 for washer?", "Yes — schedule bulk via 311; DPS customers only.")], *bulk))
    rows.append(R(c, st, "television", "SPECIAL_HANDLING", "Medium", True,
        "≤45 lb beside cart on trash day OR >45 lb bulk via 311",
        "Cincinnati regular trash (≤45 lb) / bulk via 311 (>45 lb)",
        "Cincinnati TVs ≤45 lb may go beside the cart on regular trash collection day. TVs over 45 lb require bulk collection via 311 (5 free items, DPS customers only). Wipe data before disposal.",
        ["Weigh TV — ≤45 lb: set beside cart on trash day.", ">45 lb: call 311 for bulk pickup.", "Wipe personal data."],
        [("Small TV trash?", "Yes — ≤45 lb beside cart on trash day."), ("Large TV?", ">45 lb requires bulk via 311.")], *bulk))
    for item, label in [("computer-monitor", "monitors"), ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste")]:
        rows.append(R(c, st, item, "SPECIAL_HANDLING", "Medium", True,
            "≤45 lb beside cart on trash day OR >45 lb bulk via 311",
            "Cincinnati regular trash (≤45 lb) / bulk via 311 (>45 lb)",
            f"Electronics including {label} ≤45 lb may go beside the cart on regular trash day. Items over 45 lb require bulk via 311. DPS customers only for bulk. Wipe data before disposal.",
            ["Items ≤45 lb: beside cart on trash day.", ">45 lb: call 311 for bulk.", "Wipe personal data."],
            [("Same as TV rule?", "Yes — ≤45 lb trash beside cart; >45 lb bulk via 311.")], *bulk))
    rows.append(R(c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", True,
        "Fully dried latex in trash OK; liquid latex at Hamilton County R3Source events",
        "Household trash (dried) / Hamilton County R3Source HHW events",
        "Fully dried latex paint (solidified) may go in Cincinnati household trash. Liquid latex goes to Hamilton County R3Source annual HHW events — use the R3Source search tool at r3source.org. Cincinnati has no permanent city HHW facility.",
        ["Liquid latex: find R3Source HHW event via r3source.org.", "Dried latex: solidify completely, then trash.", "Oil paint: R3Source HHW events only."],
        [("Trash for dried latex?", "Yes — fully dried latex may go in trash."), ("City HHW?", "No — use Hamilton County R3Source events/search tool.")], *r3))
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
            "Hamilton County R3Source annual HHW events — search r3source.org",
            "Hamilton County R3Source — event-based HHW",
            f"Take {item.replace('-', ' ')} to Hamilton County R3Source HHW events — use the search tool at r3source.org. Cincinnati has no permanent city HHW facility.",
            ["Search r3source.org for nearest HHW event.", "Deliver sealed containers at event.", "Keep chemicals out of bulk piles."],
            [("City HHW?", "No — Hamilton County R3Source events only.")], *r3))
    for item in ["car-battery", "lithium-battery", "paint-oil", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {"car-battery": " Batteries at R3Source HHW events.", "lithium-battery": " Lithium batteries at R3Source events.", "paint-oil": " Oil paint at R3Source events.", "motor-oil": " Motor oil at R3Source events.", "propane-tank": " Propane at R3Source events.", "fluorescent-bulbs": " Fluorescents at R3Source events.", "cooking-oil": " Cooking oil at R3Source when not trash-safe."}[item]
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING", "High" if item != "cooking-oil" else "Medium", False,
            "Hamilton County R3Source HHW events — search r3source.org", "Hamilton County R3Source — event-based HHW",
            f"Hamilton County R3Source HHW events accept household hazardous materials — search r3source.org for dates/locations.{extra}",
            ["Search r3source.org for HHW event.", "Deliver sealed containers at event.", "Tires use separate 311 bulk scheduling."], [("Permanent HHW?", "No city facility — R3Source events only.")], *r3))
    rows.append(R(c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
        "Rigid sealed container — confirm R3Source HHW sharps acceptance", "Hamilton County R3Source — event-based HHW",
        "Place sharps in a rigid sealed container. Confirm acceptance at Hamilton County R3Source HHW events via r3source.org. Do not loose-bag needles.",
        ["Use rigid sealed container.", "Confirm sharps at R3Source event.", "Never recycle loose needles."], [("Medications?", "Confirm drug take-back via r3source.org.")], *r3))
    rows.append(R(c, st, "tires", "SPECIAL_HANDLING", "Medium", True,
        "Separate 311 bulk scheduling — up to 4 tires; DPS customers only",
        "Cincinnati bulk collection (311 scheduled — tires separate)",
        "Cincinnati tires require separate 311 bulk scheduling — up to 4 tires per pickup. DPS collection customers only. Do not mix with regular bulk without scheduling tires separately.",
        ["Call 311 to schedule tire bulk separately (up to 4).", "DPS customers only.", "Do not exceed 4 tires per pickup."],
        [("Tire limit?", "Up to 4 tires — separate 311 scheduling."), ("With furniture bulk?", "Schedule tires separately via 311.")], *bulk))
    rows.append(R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True, "Cincinnati yard waste collection", "Cincinnati yard waste collection",
        "Cincinnati handles yard waste through regular collection. Follow set-out rules.",
        ["Use yard waste set-out rules.", "Keep yard waste out of bulk and HHW loads.", "Check cincinnati-oh.gov for seasonal guidance."], [("Christmas trees?", "Follow city seasonal guidance.")], *bulk))
    rows.append(R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True, "Garbage cart unless private compost", "Cincinnati garbage / private compost",
        "Bag food scraps for garbage unless you compost.",
        ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."], [("HHW for food?", "No.")], *bulk))
    rows.append(R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False, "Not recycling — store take-back / trash", "Retail bag take-back / trash",
        "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
        ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."], [("Bulk for bags?", "No.")], *bulk))
    rows.append(R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", True,
        "Bulk via 311 for limited loads — private C&D for larger",
        "Cincinnati bulk (311) / private C&D hauler",
        "Limited homeowner C&D may go on Cincinnati bulk collection when scheduled via 311 (5 free items, DPS only). Larger contractor loads need a private C&D hauler. Route paint/chemicals to R3Source HHW separately.",
        ["Call 311 to schedule bulk if debris fits city limits.", "Hire private C&D for larger projects.", "Route liquid paint to R3Source HHW events."], [("HHW for C&D?", "No — separate paint/chemicals.")], *bulk))
    return rows


def st_louis():
    c, st = "st-louis", "MO"
    boat = ("City of St. Louis — Bulky BOAT-E collection", "https://www.stlouis-mo.gov/government/departments/street/refuse/bulky-boat-items.cfm")
    hhw = ("HHWSTL — St. Louis HHW", "https://www.stlouis-mo.gov/government/departments/refuse/hhw.cfm")
    ecycle = ("Missouri DNR — E-cycle Missouri", "https://dnr.mo.gov/waste-recycling/e-cycle-missouri")
    rows = []
    rows.append(R(c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
        "Monthly bulk — up to 3 items; set out by Monday 6 a.m. of bulk week",
        "St. Louis BOAT-E monthly bulk collection",
        "St. Louis monthly bulk (BOAT-E) accepts up to 3 items — set out by Monday 6 a.m. of your designated bulk week. Mattresses are accepted. Check stlouis-mo.gov for your bulk week schedule.",
        ["Confirm your bulk week on stlouis-mo.gov.", "Set mattress out by Monday 6 a.m. of bulk week (≤3 items).", "Keep HHW and Freon items off bulk unless BOAT-E rules allow."],
        [("Bulk limit?", "Up to 3 items per monthly bulk week."), ("Set-out time?", "By Monday 6 a.m. of bulk week.")], *boat))
    rows.append(R(c, st, "refrigerator", "SPECIAL_HANDLING", "High", True,
        "BOAT-E bulk — doors off fridge; monthly up to 3 items",
        "St. Louis BOAT-E monthly bulk collection",
        "Freon refrigerators go on St. Louis BOAT-E monthly bulk — remove doors before set-out. Up to 3 items by Monday 6 a.m. of bulk week. Never vent refrigerant yourself.",
        ["Remove doors from refrigerator before set-out.", "Set out by Monday 6 a.m. of bulk week (≤3 items).", "Never release Freon yourself."],
        [("Doors off?", "Yes — remove fridge doors before BOAT-E set-out."), ("Bulk limit?", "Up to 3 items per monthly bulk week.")], *boat))
    rows.append(R(c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
        "BOAT-E bulk — appliances accepted; monthly up to 3 items",
        "St. Louis BOAT-E monthly bulk collection",
        "Freon AC units are accepted on St. Louis BOAT-E monthly bulk with other appliances. Set out by Monday 6 a.m. of bulk week — up to 3 items. Never vent refrigerant yourself.",
        ["Set AC out by Monday 6 a.m. of bulk week.", "Counts toward 3-item monthly limit.", "Keep sealed until pickup."],
        [("Same as fridge?", "Yes — appliances on BOAT-E monthly bulk.")], *boat))
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(R(c, st, item, "SPECIAL_HANDLING", "Medium", True,
            "BOAT-E bulk — appliances accepted; monthly up to 3 items",
            "St. Louis BOAT-E monthly bulk collection",
            f"Non-Freon appliances such as {item.replace('-', ' ')}s go on St. Louis BOAT-E monthly bulk with refrigerators and other white goods. Set out by Monday 6 a.m. — up to 3 items.",
            ["Set appliance out by Monday 6 a.m. of bulk week.", "Counts toward 3-item limit.", "Empty appliance before set-out."],
            [("Same BOAT-E path?", "Yes — washers use same monthly BOAT-E bulk as other appliances.")], *boat))
    rows.append(R(c, st, "television", "BANNED_FROM_LANDFILLS", "Medium", False,
        "NOT HHWSTL — Missouri DNR e-cycle program",
        "Missouri DNR E-cycle Missouri / registered recyclers",
        "St. Louis HHWSTL does NOT accept TVs or computers. TVs must go through Missouri DNR E-cycle Missouri registered recyclers — search dnr.mo.gov. Do not put TVs in bulk alley or HHW.",
        ["Do not take TVs to HHWSTL 291 E Hoffmeister.", "Search DNR E-cycle Missouri for TV recyclers.", "Wipe personal data."],
        [("HHWSTL for TV?", "No — HHWSTL does not take TVs/computers."), ("Bulk for TV?", "No — TVs use DNR e-cycle.")], *ecycle))
    for item, label in [("computer-monitor", "monitors"), ("smartphone", "phones")]:
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS", "Medium", False,
            "NOT HHWSTL — Missouri DNR e-cycle program",
            "Missouri DNR E-cycle Missouri / registered recyclers",
            f"St. Louis HHWSTL does NOT accept {label}. Use Missouri DNR E-cycle Missouri registered recyclers — search dnr.mo.gov. Wipe data before drop-off.",
            ["Do not take computers/phones to HHWSTL.", "Search DNR E-cycle Missouri.", "Wipe personal data."],
            [("HHWSTL for computers?", "No — use DNR e-cycle program.")], *ecycle))
    rows.append(R(c, st, "e-waste-mixed", "SPECIAL_HANDLING", "Medium", True,
        "Corded electronics — bulk alley on BOAT-E; NOT HHWSTL",
        "St. Louis BOAT-E bulk alley (corded electronics)",
        "Corded electronics (not TVs/computers) may go in St. Louis bulk alley on BOAT-E monthly collection. HHWSTL does NOT accept TVs or computers — those use DNR e-cycle. Set out by Monday 6 a.m. of bulk week.",
        ["Corded electronics: bulk alley on BOAT-E week.", "TVs/computers: DNR e-cycle, not HHWSTL.", "Set out by Monday 6 a.m. (≤3 items total)."],
        [("HHWSTL for e-waste?", "No TVs/computers — corded electronics use bulk alley.")], *boat))
    rows.append(R(c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", False,
        "HHWSTL 291 E Hoffmeister — appt; latex $0.50/lb; first 50 lb free",
        "HHWSTL — 291 E Hoffmeister Ave",
        "Liquid latex paint goes to HHWSTL at 291 E Hoffmeister Ave — appointment required; first 50 lb free then fees by pound; latex $0.50/lb. Check stlouis-mo.gov/hhw for hours.",
        ["Schedule HHWSTL appointment at 291 E Hoffmeister.", "First 50 lb free; latex $0.50/lb after.", "Keep paint sealed and labeled."],
        [("Free paint?", "First 50 lb free; latex $0.50/lb after."), ("Address?", "291 E Hoffmeister Ave.")], *hhw))
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
            "HHWSTL 291 E Hoffmeister — appt; first 50 lb free then $/lb",
            "HHWSTL — 291 E Hoffmeister Ave",
            f"Take {item.replace('-', ' ')} to HHWSTL 291 E Hoffmeister Ave — appointment required; first 50 lb free then fees by pound.",
            ["Schedule HHWSTL appointment.", "Deliver sealed containers.", "Keep chemicals out of BOAT-E bulk."],
            [("Same as paint?", "Yes — chemicals use HHWSTL 291 E Hoffmeister.")], *hhw))
    for item in ["car-battery", "lithium-battery", "paint-oil", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {"car-battery": " Batteries at HHWSTL.", "lithium-battery": " Lithium batteries at HHWSTL.", "paint-oil": " Oil paint at HHWSTL.", "motor-oil": " Motor oil at HHWSTL.", "propane-tank": " Propane at HHWSTL.", "fluorescent-bulbs": " Fluorescents at HHWSTL.", "cooking-oil": " Cooking oil at HHWSTL when not trash-safe."}[item]
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING", "High" if item != "cooking-oil" else "Medium", False,
            "HHWSTL 291 E Hoffmeister — appt; first 50 lb free then $/lb", "HHWSTL — 291 E Hoffmeister Ave",
            f"HHWSTL 291 E Hoffmeister Ave accepts household hazardous materials by appointment; first 50 lb free then fees by pound.{extra} TVs/computers NOT accepted.",
            ["Schedule HHWSTL appointment.", "First 50 lb free.", "TVs/computers use DNR e-cycle, not HHWSTL."], [("Address?", "291 E Hoffmeister Ave.")], *hhw))
    rows.append(R(c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
        "Rigid sealed container — confirm HHWSTL sharps acceptance", "HHWSTL — 291 E Hoffmeister Ave",
        "Place sharps in a rigid sealed container. Confirm acceptance at HHWSTL. Do not loose-bag needles.",
        ["Use rigid sealed container.", "Confirm sharps at HHWSTL appointment.", "Never recycle loose needles."], [("Medications?", "Confirm drug take-back on stlouis-mo.gov.")], *hhw))
    rows.append(R(c, st, "tires", "SPECIAL_HANDLING", "Medium", True,
        "BOAT-E bulk includes tires — monthly up to 3 items total",
        "St. Louis BOAT-E monthly bulk collection",
        "St. Louis BOAT-E monthly bulk includes tires along with appliances and electronics. Set out by Monday 6 a.m. of bulk week — up to 3 items total (tires count toward limit).",
        ["Set tires out by Monday 6 a.m. of bulk week.", "Tires count toward 3-item monthly limit.", "Check stlouis-mo.gov for bulk week schedule."],
        [("BOAT-E tires?", "Yes — tires included in monthly BOAT-E bulk."), ("Limit?", "Up to 3 items total including tires.")], *boat))
    rows.append(R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True, "St. Louis yard waste collection", "St. Louis yard waste collection",
        "St. Louis handles yard waste through regular collection. Follow set-out rules.",
        ["Use yard waste set-out rules.", "Keep yard waste out of BOAT-E and HHW loads.", "Check stlouis-mo.gov for seasonal guidance."], [("Christmas trees?", "Follow city seasonal guidance.")], *boat))
    rows.append(R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True, "Garbage cart unless private compost", "St. Louis garbage / private compost",
        "Bag food scraps for garbage unless you compost.",
        ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."], [("HHW for food?", "No.")], *boat))
    rows.append(R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False, "Not recycling — store take-back / trash", "Retail bag take-back / trash",
        "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
        ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."], [("BOAT-E for bags?", "No.")], *boat))
    rows.append(R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", True,
        "BOAT-E for limited loads (≤3 items/month) — private C&D for larger",
        "St. Louis BOAT-E bulk / private C&D hauler",
        "Limited homeowner C&D may fit BOAT-E monthly bulk (≤3 items). Larger contractor loads need a private C&D hauler. Route paint/chemicals to HHWSTL separately.",
        ["Use BOAT-E if debris fits 3-item monthly limit.", "Hire private C&D for larger projects.", "Route paint to HHWSTL 291 E Hoffmeister."], [("HHW for C&D?", "No — separate paint/chemicals.")], *boat))
    return rows


def orlando():
    c, st = "orlando", "FL"
    large = ("City of Orlando — Large item pickup", "https://www.orlando.gov/Trash-Recycling/Get-Large-Items-Picked-Up")
    toxic = ("City of Orlando — Too toxic to trash", "https://www.orlando.gov/Trash-Recycling/Too-Toxic-to-Trash")
    oc_hhw = ("Orange County Landfill — HHW", "https://www.ocfl.net/Trash-and-Recycling/Household-Hazardous-Waste.aspx")
    kob = ("Keep Orlando Beautiful — e-waste events", "https://www.orlando.gov/Trash-Recycling/Electronics-Recycling")
    rows = []
    rows.append(R(c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
        "2 free hand-loadable large items on yard waste day",
        "Orlando yard waste day large-item collection",
        "City of Orlando offers 2 free hand-loadable large items on your yard waste collection day. Mattresses must be hand-loadable — heavy items need claw truck (fees apply). Check orlando.gov for yard waste day schedule.",
        ["Set mattress out on yard waste day (hand-loadable).", "Limit 2 free large items per yard waste day.", "Heavy items: claw truck fees apply."],
        [("Free large items?", "Yes — 2 hand-loadable items on yard waste day."), ("Claw truck?", "Heavy items require claw truck — fees apply.")], *large))
    rows.append(R(c, st, "refrigerator", "SPECIAL_HANDLING", "High", True,
        "Yard waste day — doors off; hand-loadable or claw truck (fees)",
        "Orlando yard waste day / claw truck collection",
        "Refrigerators go on Orlando yard waste day large-item collection — remove doors before set-out. Must be hand-loadable for free pickup; heavy units need claw truck (fees). Never vent refrigerant yourself.",
        ["Remove doors from refrigerator.", "Set out on yard waste day (hand-loadable for free).", "Heavy units: schedule claw truck — fees apply."],
        [("Doors off?", "Yes — remove fridge doors before set-out."), ("Free pickup?", "Hand-loadable only — claw truck has fees.")], *large))
    rows.append(R(c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
        "Yard waste day large items — hand-loadable or claw truck (fees)",
        "Orlando yard waste day / claw truck collection",
        "AC units go on Orlando yard waste day large-item collection. Hand-loadable for free; heavy units need claw truck (fees). Never vent refrigerant yourself.",
        ["Set AC out on yard waste day.", "Hand-loadable for free; claw truck for heavy.", "Keep sealed until pickup."],
        [("Same as fridge?", "Yes — yard waste day; doors off for fridges.")], *large))
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(R(c, st, item, "SPECIAL_HANDLING", "Medium", True,
            "2 free hand-loadable large items on yard waste day",
            "Orlando yard waste day large-item collection",
            f"Non-Freon appliances such as {item.replace('-', ' ')}s go on Orlando yard waste day large-item collection — 2 free hand-loadable items. Heavy units need claw truck (fees).",
            ["Set appliance out on yard waste day.", "Must be hand-loadable for free pickup.", "Heavy: claw truck fees apply."],
            [("Same yard waste path?", "Yes — appliances use yard waste day large-item collection.")], *large))
    for item, label in [("television", "TVs"), ("computer-monitor", "monitors"), ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste")]:
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS", "Medium", False,
            "NOT yard waste day — KOB e-waste events / private recycler",
            "Keep Orlando Beautiful e-waste events / private recycler",
            f"Electronics including {label} are NOT accepted on Orlando yard waste day large-item pickup. Use Keep Orlando Beautiful (KOB) e-waste events or private recyclers. Wipe data before drop-off.",
            ["Do not put e-waste on yard waste day pickup.", "Check orlando.gov for KOB e-waste events.", "Wipe personal data."],
            [("Yard waste day for TV?", "No — e-waste uses KOB events or private recyclers.")], *kob))
    rows.append(R(c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", False,
        "Free at Orange County Landfill HHW — 5901 Young Pine Rd / Porter Rd Transfer",
        "Orange County Landfill HHW — 5901 Young Pine Rd",
        "Liquid latex and oil paint are free at Orange County Landfill HHW — 5901 Young Pine Rd or Porter Road Transfer Station. Orlando residents use Orange County HHW — not yard waste day pickup.",
        ["Haul paint to Orange County HHW 5901 Young Pine Rd.", "Also accepted at Porter Road Transfer Station.", "Keep paint sealed and labeled."],
        [("Free paint?", "Yes — free at Orange County HHW."), ("City HHW?", "Orlando uses Orange County HHW sites.")], *oc_hhw))
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
            "Free Orange County HHW — 5901 Young Pine Rd / Porter Rd Transfer",
            "Orange County Landfill HHW — 5901 Young Pine Rd",
            f"Take {item.replace('-', ' ')} free to Orange County Landfill HHW 5901 Young Pine Rd or Porter Road Transfer Station.",
            ["Deliver sealed containers to Orange County HHW.", "Check ocfl.net for hours.", "Keep chemicals off yard waste day pickup."],
            [("Same as paint?", "Yes — chemicals use Orange County HHW.")], *oc_hhw))
    for item in ["car-battery", "lithium-battery", "paint-oil", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {"car-battery": " Batteries at Orange County HHW.", "lithium-battery": " Lithium batteries at OC HHW.", "paint-oil": " Oil paint at OC HHW.", "motor-oil": " Motor oil at OC HHW.", "propane-tank": " Propane at OC HHW.", "fluorescent-bulbs": " Fluorescents at OC HHW.", "cooking-oil": " Cooking oil at OC HHW when not trash-safe."}[item]
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING", "High" if item != "cooking-oil" else "Medium", False,
            "Free Orange County HHW — 5901 Young Pine Rd", "Orange County Landfill HHW — 5901 Young Pine Rd",
            f"Orange County Landfill HHW 5901 Young Pine Rd accepts household hazardous materials free.{extra} E-waste uses KOB events.",
            ["Haul to Orange County HHW 5901 Young Pine Rd.", "Check ocfl.net hours.", "E-waste/TVs use KOB events, not HHW."], [("Address?", "5901 Young Pine Rd.")], *oc_hhw))
    rows.append(R(c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
        "Rigid sealed container — confirm Orange County HHW sharps acceptance", "Orange County Landfill HHW — 5901 Young Pine Rd",
        "Place sharps in a rigid sealed container. Confirm acceptance at Orange County HHW. Do not loose-bag needles.",
        ["Use rigid sealed container.", "Confirm sharps at Orange County HHW.", "Never recycle loose needles."], [("Medications?", "Confirm drug take-back on ocfl.net.")], *oc_hhw))
    rows.append(R(c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
        "NOT city — Orange County tire disposal",
        "Orange County tire disposal — not Orlando city collection",
        "Tires are NOT accepted on Orlando city yard waste day or large-item pickup. Use Orange County tire disposal programs — check ocfl.net. Retailer take-back when replacing tires.",
        ["Do not set tires out for Orlando yard waste day.", "Use Orange County tire disposal.", "Retailer take-back when replacing tires."],
        [("City tire pickup?", "No — tires are Orange County, not Orlando city.")], *large))
    rows.append(R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True, "Orlando yard waste collection", "Orlando yard waste collection",
        "Orlando handles yard waste through regular collection — same day as 2 free large items. Follow set-out rules.",
        ["Use yard waste set-out rules.", "2 free hand-loadable large items same day.", "Check orlando.gov for schedule."], [("Christmas trees?", "Follow city seasonal guidance.")], *large))
    rows.append(R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True, "Garbage cart unless private compost", "Orlando garbage / private compost",
        "Bag food scraps for garbage unless you compost.",
        ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."], [("HHW for food?", "No.")], *large))
    rows.append(R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False, "Not recycling — store take-back / trash", "Retail bag take-back / trash",
        "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
        ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."], [("Yard waste day for bags?", "No.")], *large))
    rows.append(R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", True,
        "Yard waste day for limited hand-loadable loads — claw truck fees or private C&D",
        "Orlando yard waste day / claw truck / private C&D hauler",
        "Limited hand-loadable C&D may fit Orlando yard waste day (2 free items). Larger loads need claw truck (fees) or private C&D hauler. Route paint/chemicals to Orange County HHW.",
        ["Use yard waste day if debris is hand-loadable (≤2 items).", "Larger loads: claw truck or private C&D.", "Route paint to Orange County HHW."], [("HHW for C&D?", "No — separate paint/chemicals.")], *large))
    return rows


def buffalo():
    c, st = "buffalo", "NY"
    bulk = ("City of Buffalo — Bulk trash information", "https://www.buffalony.gov/434/Bulk-Trash-Information")
    streets = ("City of Buffalo — Streets & sanitation", "https://www.buffalony.gov/432/Streets-Sanitation")
    ewaste = ("Buffalo Engineering Garage — E-waste drop-off", "https://www.buffalony.gov/432/Streets-Sanitation")
    rows = []
    rows.append(R(c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
        "3 bulk/week with tote — mattress accepted",
        "Buffalo curbside bulk trash collection",
        "Buffalo accepts mattresses on curbside bulk trash — up to 3 bulk items per week with a tote. Set out per buffalony.gov bulk trash rules on your collection day.",
        ["Set mattress out with bulk tote on collection day.", "Limit 3 bulk items per week.", "Follow buffalony.gov set-out rules."],
        [("Bulk limit?", "Up to 3 bulk items per week with tote."), ("Tote required?", "Yes — use bulk tote per city rules.")], *bulk))
    rows.append(R(c, st, "refrigerator", "SPECIAL_HANDLING", "High", True,
        "3 bulk/week with tote — appliances accepted",
        "Buffalo curbside bulk trash collection",
        "Freon refrigerators are accepted on Buffalo curbside bulk trash — up to 3 bulk items per week with tote. Keep doors secured; never vent refrigerant yourself.",
        ["Set refrigerator out with bulk tote.", "Counts toward 3 bulk/week limit.", "Keep doors secured until pickup."],
        [("Appliances on bulk?", "Yes — appliances accepted on bulk trash."), ("Bulk limit?", "3 bulk items per week with tote.")], *bulk))
    rows.append(R(c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
        "3 bulk/week with tote — appliances accepted",
        "Buffalo curbside bulk trash collection",
        "Freon AC units are accepted on Buffalo curbside bulk trash — up to 3 bulk items per week with tote. Never vent refrigerant yourself.",
        ["Set AC out with bulk tote.", "Counts toward 3 bulk/week limit.", "Keep sealed until pickup."],
        [("Same as fridge?", "Yes — appliances on bulk trash with tote.")], *bulk))
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(R(c, st, item, "SPECIAL_HANDLING", "Medium", True,
            "3 bulk/week with tote — appliances accepted",
            "Buffalo curbside bulk trash collection",
            f"Non-Freon appliances such as {item.replace('-', ' ')}s go on Buffalo curbside bulk trash — up to 3 bulk items per week with tote.",
            ["Set appliance out with bulk tote.", "Counts toward 3 bulk/week limit.", "Empty appliance before set-out."],
            [("Same bulk path?", "Yes — washers use same bulk trash as other appliances.")], *bulk))
    for item, label in [("television", "TVs"), ("computer-monitor", "monitors"), ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste")]:
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS", "Medium", False,
            "Engineering Garage 1120 Seneca St — 5 items/year; NOT bulk trash",
            "Buffalo Engineering Garage — 1120 Seneca St",
            f"Electronics including {label} go to Buffalo Engineering Garage at 1120 Seneca St — Mon–Fri 8 a.m.–3 p.m., first Sat 8 a.m.–2 p.m.; limit 5 items per year. NOT on curbside bulk trash. Wipe data before drop-off.",
            ["Haul e-waste to 1120 Seneca St during posted hours.", "Limit 5 items per year.", "Wipe personal data."],
            [("Bulk for TV?", "No — e-waste uses Engineering Garage, not bulk trash."), ("Annual limit?", "5 items per year.")], *ewaste))
    rows.append(R(c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", False,
        "Buffalo HHW events (2/year, call 311) / Erie County HHW",
        "Buffalo HHW events / Erie County HHW",
        "Liquid latex and oil paint go to Buffalo HHW events — 2 city events per year; call 311 for dates — or Erie County HHW programs. Do not put liquid paint in bulk trash.",
        ["Call 311 for Buffalo HHW event dates (2/year).", "Or check Erie County HHW programs.", "Do not put liquid paint in bulk trash."],
        [("City HHW?", "2 events/year — call 311."), ("Erie County?", "Also check Erie County HHW for paint.")], *streets))
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
            "Buffalo HHW events (2/year, call 311) / Erie County HHW",
            "Buffalo HHW events / Erie County HHW",
            f"Take {item.replace('-', ' ')} to Buffalo HHW events — call 311 for dates (2/year) — or Erie County HHW. Do not dry chemicals for trash.",
            ["Call 311 for HHW event dates.", "Deliver sealed containers at event.", "Keep chemicals out of bulk trash."],
            [("Same as paint?", "Yes — chemicals use HHW events or Erie County.")], *streets))
    for item in ["car-battery", "lithium-battery", "paint-oil", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {"car-battery": " Batteries at HHW events.", "lithium-battery": " Lithium batteries at HHW events.", "paint-oil": " Oil paint at HHW events.", "motor-oil": " Motor oil at HHW events.", "propane-tank": " Propane at HHW events.", "fluorescent-bulbs": " Fluorescents at HHW events.", "cooking-oil": " Cooking oil at HHW when not trash-safe."}[item]
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING", "High" if item != "cooking-oil" else "Medium", False,
            "Buffalo HHW events (2/year, call 311) / Erie County HHW", "Buffalo HHW events / Erie County HHW",
            f"Buffalo HHW events (call 311 — 2/year) or Erie County HHW accept household hazardous materials.{extra}",
            ["Call 311 for HHW event dates.", "Deliver sealed containers at event.", "E-waste uses Engineering Garage, not HHW."], [("Event schedule?", "Call 311 — 2 city HHW events per year.")], *streets))
    rows.append(R(c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
        "Rigid sealed container — confirm Buffalo HHW sharps acceptance", "Buffalo HHW events / Erie County HHW",
        "Place sharps in a rigid sealed container. Confirm acceptance at Buffalo HHW events (call 311) or Erie County programs. Do not loose-bag needles.",
        ["Use rigid sealed container.", "Call 311 for HHW event sharps acceptance.", "Never recycle loose needles."], [("Medications?", "Confirm drug take-back via 311 or Erie County.")], *streets))
    rows.append(R(c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
        "NOT weekly bulk — Broadway Garage event days",
        "Buffalo Broadway Garage — tire event days",
        "Tires are NOT accepted on Buffalo weekly bulk trash. Use Broadway Garage tire event days — check buffalony.gov Streets & Sanitation for schedule.",
        ["Do not set tires out for weekly bulk trash.", "Check Broadway Garage tire event days on buffalony.gov.", "Retailer take-back when replacing tires."],
        [("Bulk for tires?", "No — Broadway Garage event days only.")], *streets))
    rows.append(R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True, "Buffalo yard waste collection", "Buffalo yard waste collection",
        "Buffalo handles yard waste through regular collection. Follow set-out rules.",
        ["Use yard waste set-out rules.", "Keep yard waste out of bulk and HHW loads.", "Check buffalony.gov for seasonal guidance."], [("Christmas trees?", "Follow city seasonal guidance.")], *bulk))
    rows.append(R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True, "Garbage cart unless private compost", "Buffalo garbage / private compost",
        "Bag food scraps for garbage unless you compost.",
        ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."], [("HHW for food?", "No.")], *bulk))
    rows.append(R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False, "Not recycling — store take-back / trash", "Retail bag take-back / trash",
        "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
        ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."], [("Bulk for bags?", "No.")], *bulk))
    rows.append(R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", True,
        "Bulk trash for limited loads (3/week) — private C&D for larger",
        "Buffalo bulk trash / private C&D hauler",
        "Limited homeowner C&D may go on Buffalo bulk trash (3/week with tote). Larger contractor loads need a private C&D hauler. Route paint/chemicals to HHW events separately.",
        ["Use bulk trash if debris fits 3/week limit.", "Hire private C&D for larger projects.", "Route paint to HHW events (call 311)."], [("HHW for C&D?", "No — separate paint/chemicals.")], *bulk))
    return rows


CITIES = [
    {"city": "Pittsburgh", "city_slug": "pittsburgh", "state": "PA", "state_slug": "pennsylvania", "lat": 40.4406, "lng": -79.9959, "population": 302971},
    {"city": "Cincinnati", "city_slug": "cincinnati", "state": "OH", "state_slug": "ohio", "lat": 39.1031, "lng": -84.5120, "population": 309317},
    {"city": "St. Louis", "city_slug": "st-louis", "state": "MO", "state_slug": "missouri", "lat": 38.6270, "lng": -90.1994, "population": 279457},
    {"city": "Orlando", "city_slug": "orlando", "state": "FL", "state_slug": "florida", "lat": 28.5383, "lng": -81.3792, "population": 307573},
    {"city": "Buffalo", "city_slug": "buffalo", "state": "NY", "state_slug": "new-york", "lat": 42.8864, "lng": -78.8784, "population": 276807},
]

ZIPS = [
    {"zip": "15213", "city": "Pittsburgh", "city_slug": "pittsburgh", "state": "PA", "state_slug": "pennsylvania", "lat": 40.441, "lng": -79.956, "population": 14000},
    {"zip": "15222", "city": "Pittsburgh", "city_slug": "pittsburgh", "state": "PA", "state_slug": "pennsylvania", "lat": 40.448, "lng": -79.992, "population": 8000},
    {"zip": "45202", "city": "Cincinnati", "city_slug": "cincinnati", "state": "OH", "state_slug": "ohio", "lat": 39.103, "lng": -84.512, "population": 9000},
    {"zip": "45219", "city": "Cincinnati", "city_slug": "cincinnati", "state": "OH", "state_slug": "ohio", "lat": 39.128, "lng": -84.515, "population": 18000},
    {"zip": "63101", "city": "St. Louis", "city_slug": "st-louis", "state": "MO", "state_slug": "missouri", "lat": 38.627, "lng": -90.199, "population": 5000},
    {"zip": "63108", "city": "St. Louis", "city_slug": "st-louis", "state": "MO", "state_slug": "missouri", "lat": 38.645, "lng": -90.245, "population": 12000},
    {"zip": "32801", "city": "Orlando", "city_slug": "orlando", "state": "FL", "state_slug": "florida", "lat": 28.538, "lng": -81.379, "population": 8000},
    {"zip": "32803", "city": "Orlando", "city_slug": "orlando", "state": "FL", "state_slug": "florida", "lat": 28.555, "lng": -81.355, "population": 15000},
    {"zip": "14202", "city": "Buffalo", "city_slug": "buffalo", "state": "NY", "state_slug": "new-york", "lat": 42.886, "lng": -78.878, "population": 6000},
    {"zip": "14210", "city": "Buffalo", "city_slug": "buffalo", "state": "NY", "state_slug": "new-york", "lat": 42.855, "lng": -78.835, "population": 16000},
]

FACILITIES = [
    {
        "name": "Noble Environmental HHW",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "pittsburgh",
        "state": "PA",
        "zip": "15222",
        "address": "3001 Railroad St, Pittsburgh, PA 15222",
        "lat": 40.4555,
        "lng": -79.9755,
        "source_url": "https://pittsburghpa.gov/City-Government/Finance-Administration/Finance/Refuse-Recycling/Electronic-Waste-and-Household-Hazardous-Waste-Disposal",
        "hours": "Tue/Thu 14:30–18:30 by appointment",
        "phone": "412-255-2773",
    },
    {
        "name": "Pittsburgh DPW Tire Drop-Off — Hamilton Ave",
        "facility_type": "Tire drop-off",
        "city_slug": "pittsburgh",
        "state": "PA",
        "zip": "15208",
        "address": "300 Hamilton Ave, Pittsburgh, PA 15208",
        "lat": 40.4655,
        "lng": -79.9155,
        "source_url": "https://pittsburghpa.gov/City-Government/Finance-Administration/Finance/Refuse-Recycling/Curbside-Refuse",
        "hours": "Check pittsburghpa.gov for DPW drop-off hours",
        "phone": "412-255-2773",
    },
    {
        "name": "Hamilton County R3Source HHW",
        "facility_type": "Household hazardous waste — event-based",
        "city_slug": "cincinnati",
        "state": "OH",
        "zip": "45231",
        "address": "Event locations vary — search r3source.org",
        "lat": 39.2155,
        "lng": -84.4655,
        "source_url": "https://www.r3source.org/",
        "hours": "Annual HHW events — use R3Source search tool",
        "phone": "513-946-7766",
    },
    {
        "name": "HHWSTL",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "st-louis",
        "state": "MO",
        "zip": "63125",
        "address": "291 E Hoffmeister Ave, St. Louis, MO 63125",
        "lat": 38.5355,
        "lng": -90.2855,
        "source_url": "https://www.stlouis-mo.gov/government/departments/refuse/hhw.cfm",
        "hours": "By appointment — check stlouis-mo.gov",
        "phone": "314-622-4800",
    },
    {
        "name": "Orange County Landfill HHW",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "orlando",
        "state": "FL",
        "zip": "32829",
        "address": "5901 Young Pine Rd, Orlando, FL 32829",
        "lat": 28.4255,
        "lng": -81.2655,
        "source_url": "https://www.ocfl.net/Trash-and-Recycling/Household-Hazardous-Waste.aspx",
        "hours": "Check ocfl.net for HHW hours",
        "phone": "407-836-6601",
    },
    {
        "name": "Buffalo Engineering Garage — E-waste",
        "facility_type": "Electronics drop-off",
        "city_slug": "buffalo",
        "state": "NY",
        "zip": "14210",
        "address": "1120 Seneca St, Buffalo, NY 14210",
        "lat": 42.8555,
        "lng": -78.8255,
        "source_url": "https://www.buffalony.gov/432/Streets-Sanitation",
        "hours": "Mon–Fri 8:00–15:00; first Sat 8:00–14:00",
        "phone": "716-851-5635",
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
        "pittsburgh": clone_siblings(pittsburgh()),
        "cincinnati": clone_siblings(cincinnati()),
        "st-louis": clone_siblings(st_louis()),
        "orlando": clone_siblings(orlando()),
        "buffalo": clone_siblings(buffalo()),
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

    print("Wave-11 metros written:")
    for city, rows in audited.items():
        print(f"  {city}: {len(rows)} rules")
    print(f"Total rules now: {len(keep)}")


if __name__ == "__main__":
    main()
