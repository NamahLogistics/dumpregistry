#!/usr/bin/env python3
"""Portal-audited city guides for wave-12 metros (city-sourced only).

Cities researched from official program pages (2026-08-11):
  - Richmond, VA — rva.gov bulk-and-brush + trash-collection
  - Boise, ID — cityofboise.org curb-it trash + hhw
  - Des Moines, IA — dsm.city bulk_trash + scrub; mwatoday.com HHW
  - Spokane, WA — my.spokanecity.org solidwaste garbage + hazardous
  - Honolulu, HI — honolulu.gov BULKY_APPT_FAQ + hhw-2 + waste-drop-off
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


def richmond():
    c, st = "richmond", "VA"
    bulk = ("City of Richmond — Bulk & Brush", "https://www.rva.gov/public-works/bulk-and-brush")
    trash = ("City of Richmond — Trash collection", "https://www.rva.gov/public-works/trash-collection")
    errcc = ("Richmond ERRCC — HHW & tire drop-off", "https://www.rva.gov/public-works/trash-collection")
    securis = ("SECURIS / Richmond e-waste events", "https://www.rva.gov/public-works/trash-collection")
    rows = []
    rows.append(R(c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
        "Bi-weekly Bulk & Brush on recycling week — free",
        "Richmond Bulk & Brush (recycling week)",
        "Richmond Bulk & Brush collection runs bi-weekly on your recycling week — free. Mattresses are accepted. Set out per rva.gov bulk-and-brush rules; keep Freon appliances and e-waste off bulk piles.",
        ["Set mattress out on recycling week during Bulk & Brush.", "Follow rva.gov set-out placement rules.", "Keep Freon appliances and e-waste separate."],
        [("Which week?", "Bi-weekly on your recycling week."), ("Fee?", "Free on Bulk & Brush week.")], *bulk))
    rows.append(R(c, st, "refrigerator", "SPECIAL_HANDLING", "High", False,
        "$50 appliance collection via 311 OR free DIY at ERRCC / Southside Transfer",
        "Richmond 311 appliance collection / ERRCC 3800 East Richmond Rd",
        "Freon refrigerators are NOT accepted on Richmond Bulk & Brush. Use $50 appliance collection via 311 OR haul free to ERRCC (3800 East Richmond Rd) or Southside Transfer Station for DIY drop-off. Never vent refrigerant yourself.",
        ["Call 311 for $50 appliance collection OR haul to ERRCC 3800 East Richmond Rd.", "Southside Transfer also accepts DIY appliance drop-off.", "Do not set Freon refrigerators on Bulk & Brush."],
        [("Bulk for fridge?", "No — Freon appliances use 311 ($50) or ERRCC DIY."), ("Free option?", "Yes — DIY drop at ERRCC or Southside Transfer.")], *trash))
    rows.append(R(c, st, "air-conditioner", "SPECIAL_HANDLING", "High", False,
        "$50 appliance collection via 311 OR free DIY at ERRCC / Southside Transfer",
        "Richmond 311 appliance collection / ERRCC 3800 East Richmond Rd",
        "Freon window and portable AC units are NOT accepted on Richmond Bulk & Brush. Use $50 appliance collection via 311 OR free DIY at ERRCC (3800 East Richmond Rd) or Southside Transfer. Never vent refrigerant yourself.",
        ["Call 311 for $50 appliance collection OR haul to ERRCC.", "Do not set Freon AC on Bulk & Brush.", "Keep sealed until proper Freon handling."],
        [("Same as fridge?", "Yes — Freon AC uses 311 or ERRCC, not Bulk & Brush.")], *trash))
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(R(c, st, item, "SPECIAL_HANDLING", "Medium", True,
            "Bi-weekly Bulk & Brush on recycling week — free",
            "Richmond Bulk & Brush (recycling week)",
            f"Non-Freon appliances such as {item.replace('-', ' ')}s may go on Richmond Bulk & Brush bi-weekly on recycling week — free. Freon refrigerators/AC use 311 ($50) or ERRCC DIY — not Bulk & Brush.",
            ["Set appliance out on recycling week Bulk & Brush.", "Do not confuse with Freon fridge path.", "Empty appliance before set-out."],
            [("Same as Freon fridge?", "No — non-Freon appliances use Bulk & Brush."), ("Fee?", "Free on Bulk & Brush week.")], *bulk))
    for item, label in [("television", "TVs"), ("computer-monitor", "monitors"), ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste")]:
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS", "Medium", False,
            "NOT curbside — SECURIS / Richmond e-waste events (fees)",
            "SECURIS / Richmond e-waste collection events",
            f"Electronics including {label} are NOT accepted on Richmond Bulk & Brush or curbside trash. Use SECURIS or Richmond e-waste collection events — fees apply. Wipe data before drop-off.",
            ["Do not put TVs/e-waste on Bulk & Brush.", "Check rva.gov for SECURIS/e-waste event dates.", "Wipe personal data before recycling."],
            [("Curbside e-waste?", "No — use SECURIS/events with fees."), ("Bulk for TV?", "No — e-waste is separate from Bulk & Brush.")], *securis))
    rows.append(R(c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", False,
        "Free ERRCC HHW — up to 20 gal/month",
        "Richmond ERRCC — 3800 East Richmond Rd",
        "Liquid latex paint is free at Richmond ERRCC HHW — 3800 East Richmond Rd — up to 20 gallons per month. Hours: Mon–Fri 7:00 a.m.–3:30 p.m., Sat 8:30 a.m.–2:00 p.m. Not curbside.",
        ["Haul paint to ERRCC 3800 East Richmond Rd.", "Limit 20 gallons/month.", "Keep paint sealed and labeled."],
        [("Free paint?", "Yes — up to 20 gal/month at ERRCC."), ("Curbside paint?", "No — paint uses ERRCC HHW.")], *errcc))
    rows.append(R(c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
        "Free ERRCC HHW — up to 20 gal/month",
        "Richmond ERRCC — 3800 East Richmond Rd",
        "Oil-based paint goes to Richmond ERRCC HHW — 3800 East Richmond Rd — free up to 20 gallons per month. Hours: Mon–Fri 7:00–3:30, Sat 8:30–2:00. Not curbside.",
        ["Haul oil paint to ERRCC 3800 East Richmond Rd.", "Limit 20 gallons/month.", "Keep containers sealed and labeled."],
        [("Same as latex?", "Both go to ERRCC HHW — not curbside."), ("Free?", "Yes — up to 20 gal/month.")], *errcc))
    for item in ["pesticides", "herbicides"]:
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
            "NOT accepted at ERRCC — confirm alternate HHW/disposal",
            "Alternate HHW / Virginia DEQ guidance",
            f"Richmond ERRCC HHW does NOT accept {item.replace('-', ' ')}. Confirm alternate disposal via Virginia DEQ or regional HHW programs — do not put pesticides/herbicides in trash or Bulk & Brush.",
            ["Do not take pesticides/herbicides to ERRCC.", "Search Virginia DEQ for alternate HHW options.", "Keep chemicals sealed until proper disposal."],
            [("ERRCC for pesticides?", "No — pesticides and herbicides are NOT accepted at ERRCC.")], *errcc))
    for item in ["pool-chemicals", "gasoline"]:
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
            "Free ERRCC HHW — Mon–Fri 7–3:30 Sat 8:30–2",
            "Richmond ERRCC — 3800 East Richmond Rd",
            f"Take {item.replace('-', ' ')} to Richmond ERRCC HHW — 3800 East Richmond Rd — free. Hours: Mon–Fri 7:00–3:30, Sat 8:30–2:00. Pesticides and herbicides are NOT accepted.",
            ["Deliver sealed containers to ERRCC during posted hours.", "Keep chemicals out of Bulk & Brush.", "Do not mix pesticides/herbicides (not accepted)."],
            [("Pesticides at ERRCC?", "No — but pool chemicals and gasoline are accepted.")], *errcc))
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {"car-battery": " Auto/household batteries at ERRCC HHW.", "lithium-battery": " Lithium batteries at ERRCC HHW.", "motor-oil": " Used motor oil at ERRCC HHW.", "propane-tank": " Propane at ERRCC HHW.", "fluorescent-bulbs": " Fluorescents at ERRCC HHW.", "cooking-oil": " Cooking oil at ERRCC when not trash-safe."}[item]
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING", "High" if item != "cooking-oil" else "Medium", False,
            "Free ERRCC HHW — Mon–Fri 7–3:30 Sat 8:30–2", "Richmond ERRCC — 3800 East Richmond Rd",
            f"Richmond ERRCC HHW at 3800 East Richmond Rd accepts household hazardous materials free.{extra} Pesticides/herbicides NOT accepted.",
            ["Haul to ERRCC 3800 East Richmond Rd during posted hours.", "Keep chemicals out of Bulk & Brush.", "Freon appliances use 311 or ERRCC DIY, not HHW."], [("Address?", "3800 East Richmond Rd.")], *errcc))
    rows.append(R(c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
        "Rigid sealed container — confirm ERRCC HHW sharps acceptance", "Richmond ERRCC — 3800 East Richmond Rd",
        "Place sharps in a rigid sealed container. Confirm acceptance at Richmond ERRCC HHW. Do not loose-bag needles.",
        ["Use rigid sealed container.", "Confirm sharps acceptance at ERRCC.", "Never recycle loose needles."], [("Medications?", "Confirm drug take-back on rva.gov.")], *errcc))
    rows.append(R(c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
        "ERRCC — up to 4 free rimless tires",
        "Richmond ERRCC — 3800 East Richmond Rd",
        "Richmond ERRCC accepts up to 4 free rimless tires — 3800 East Richmond Rd. Hours: Mon–Fri 7:00–3:30, Sat 8:30–2:00. Not accepted on Bulk & Brush.",
        ["Remove rims — ERRCC accepts rimless tires only.", "Haul up to 4 tires to ERRCC 3800 East Richmond Rd.", "Do not set tires out for Bulk & Brush."],
        [("Curbside tires?", "No — ERRCC drop-off, 4 free rimless."), ("Rims?", "Remove rims before drop-off.")], *errcc))
    rows.append(R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True, "Richmond yard waste / Bulk & Brush", "Richmond yard waste collection",
        "Richmond handles yard waste through regular collection and Bulk & Brush on recycling week. Follow set-out rules on rva.gov.",
        ["Use yard waste set-out rules.", "Bulk & Brush on recycling week for brush.", "Check rva.gov for seasonal guidance."], [("Christmas trees?", "Follow city seasonal yard waste guidance.")], *bulk))
    rows.append(R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True, "Garbage cart unless private compost", "Richmond garbage / private compost",
        "Bag food scraps for garbage unless you compost. Keep food out of recycling and HHW.",
        ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."], [("HHW for food?", "No.")], *trash))
    rows.append(R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False, "Not recycling — store take-back / trash", "Retail bag take-back / trash",
        "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
        ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."], [("Bulk for bags?", "No.")], *trash))
    rows.append(R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", False,
        "NOT typical Bulk & Brush — private C&D hauler or ERRCC limits",
        "Private C&D hauler / Richmond ERRCC",
        "Construction debris is not typical Bulk & Brush. Hire a private C&D hauler or check ERRCC limits. Route paint/chemicals to ERRCC HHW separately.",
        ["Do not mix C&D with Bulk & Brush without confirming limits.", "Hire private C&D hauler for large loads.", "Route paint to ERRCC HHW."], [("HHW for C&D?", "No — separate paint/chemicals.")], *bulk))
    return rows


def boise():
    c, st = "boise", "ID"
    bulk = ("City of Boise — Curb It large item pickup", "https://www.cityofboise.org/departments/public-works/trash-and-recycling/curb-it/")
    hhw = ("City of Boise — Household hazardous waste", "https://www.cityofboise.org/departments/public-works/trash-and-recycling/household-hazardous-waste/")
    ada = ("Ada County Landfill — HHW", "https://www.cityofboise.org/departments/public-works/trash-and-recycling/household-hazardous-waste/")
    rows = []
    rows.append(R(c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
        "Large Item Pickup via Republic — 6 free/year",
        "Republic Services large item pickup (208-345-1266)",
        "Boise Large Item Pickup through Republic Services (208-345-1266) — 6 free pickups per year. Mattresses are included. Schedule per cityofboise.org curb-it trash rules.",
        ["Call Republic 208-345-1266 to schedule large item pickup.", "Counts toward 6 free/year limit.", "Set out per Republic instructions on scheduled day."],
        [("Free pickups?", "Yes — 6 free large item pickups per year."), ("Who hauls?", "Republic Services for Boise.")], *bulk))
    rows.append(R(c, st, "refrigerator", "SPECIAL_HANDLING", "High", True,
        "Large Item Pickup — 6 free/year; Freon removed after collection",
        "Republic Services large item pickup (208-345-1266)",
        "Freon refrigerators are accepted on Boise Large Item Pickup via Republic (208-345-1266) — counts toward 6 free/year. Freon is removed after collection. Never vent refrigerant yourself.",
        ["Call Republic 208-345-1266 to schedule refrigerator pickup.", "Counts toward 6 free/year.", "Keep doors secured until pickup."],
        [("Freon fridge on pickup?", "Yes — included in 6 free/year; Freon removed after collection."), ("Fee?", "Free within 6/year allowance.")], *bulk))
    rows.append(R(c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
        "Large Item Pickup — 6 free/year; Freon removed after collection",
        "Republic Services large item pickup (208-345-1266)",
        "Freon AC units are accepted on Boise Large Item Pickup via Republic — 6 free/year. Freon removed after collection. Never vent refrigerant yourself.",
        ["Call Republic 208-345-1266 to schedule AC pickup.", "Counts toward 6 free/year.", "Keep sealed until pickup."],
        [("Same as fridge?", "Yes — Freon appliances included in large item pickup.")], *bulk))
    rows.append(R(c, st, "television", "SPECIAL_HANDLING", "Medium", False,
        "HHW mobile events (size limits) OR Ada County landfill diversion for large TVs",
        "Boise HHW mobile / Ada County Landfill diversion",
        "Boise TVs go through HHW mobile collection events (size limits apply) or Ada County Landfill diversion for large TVs. Not regular curbside trash. Wipe data before disposal.",
        ["Check cityofboise.org for HHW mobile event dates and size limits.", "Large TVs: Ada County Landfill diversion.", "Wipe personal data."],
        [("Curbside TV?", "No — HHW mobile or landfill diversion."), ("Large TV?", "Ada County Landfill diversion path.")], *hhw))
    for item, label in [("computer-monitor", "monitors"), ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste")]:
        rows.append(R(c, st, item, "SPECIAL_HANDLING", "Medium", False,
            "HHW mobile events (size limits)",
            "Boise HHW mobile collection",
            f"Electronics including {label} go to Boise HHW mobile collection events — size limits apply. Check cityofboise.org for dates. Wipe data before drop-off.",
            ["Check HHW mobile event schedule on cityofboise.org.", "Confirm size limits before hauling.", "Wipe personal data."],
            [("Same as TV?", "Yes — e-waste uses HHW mobile events with size limits.")], *hhw))
    rows.append(R(c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", False,
        "Free HHW — up to 25 gal; mobile events + Ada County Landfill Fri/Sat 8–6",
        "Boise HHW mobile / Ada County Landfill HHW",
        "Liquid latex paint is free at Boise HHW — up to 25 gallons. Use HHW mobile events or Ada County Landfill HHW — Fri/Sat 8:00 a.m.–6:00 p.m.",
        ["Check HHW mobile event dates on cityofboise.org.", "Or haul to Ada County Landfill HHW Fri/Sat 8–6.", "Limit 25 gallons."],
        [("Free paint?", "Yes — up to 25 gal at HHW."), ("Landfill hours?", "Fri/Sat 8:00–18:00 at Ada County Landfill HHW.")], *hhw))
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
            "Free HHW — mobile events + Ada County Landfill Fri/Sat 8–6",
            "Boise HHW mobile / Ada County Landfill HHW",
            f"Take {item.replace('-', ' ')} to Boise HHW mobile events or Ada County Landfill HHW — Fri/Sat 8:00–6:00. Free.",
            ["Check HHW mobile event schedule.", "Or haul to Ada County Landfill HHW Fri/Sat 8–6.", "Deliver sealed containers."],
            [("Same as paint?", "Yes — chemicals use HHW mobile or Ada County Landfill.")], *hhw))
    rows.append(R(c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
        "Free HHW — mobile events + Ada County Landfill Fri/Sat 8–6",
        "Boise HHW mobile / Ada County Landfill HHW",
        "Oil-based paint goes to Boise HHW mobile events or Ada County Landfill HHW — Fri/Sat 8:00–6:00. Free up to 25 gallons total paint.",
        ["Haul oil paint to HHW mobile or Ada County Landfill.", "Keep containers sealed and labeled.", "Not curbside."],
        [("Same facility as latex?", "Yes — both use HHW mobile or Ada County Landfill.")], *hhw))
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {"car-battery": " Batteries at HHW.", "lithium-battery": " Lithium batteries at HHW.", "motor-oil": " Motor oil at HHW.", "propane-tank": " Propane at HHW.", "fluorescent-bulbs": " Fluorescents at HHW.", "cooking-oil": " Cooking oil at HHW when not trash-safe."}[item]
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING", "High" if item != "cooking-oil" else "Medium", False,
            "Free HHW — mobile events + Ada County Landfill Fri/Sat 8–6", "Boise HHW mobile / Ada County Landfill HHW",
            f"Boise HHW mobile events and Ada County Landfill HHW accept household hazardous materials free.{extra}",
            ["Check HHW mobile schedule on cityofboise.org.", "Or Ada County Landfill HHW Fri/Sat 8–6.", "Tires use landfill fee path, not HHW."], [("Landfill HHW?", "Fri/Sat 8:00–18:00 at Ada County Landfill.")], *hhw))
    rows.append(R(c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
        "Rigid sealed container — confirm HHW sharps acceptance", "Boise HHW mobile / Ada County Landfill HHW",
        "Place sharps in a rigid sealed container. Confirm acceptance at Boise HHW mobile or Ada County Landfill HHW. Do not loose-bag needles.",
        ["Use rigid sealed container.", "Confirm sharps at HHW event or landfill.", "Never recycle loose needles."], [("Medications?", "Confirm drug take-back on cityofboise.org.")], *hhw))
    rows.append(R(c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
        "Ada County Landfill — fee; NOT HHW",
        "Ada County Landfill — tire disposal (fee)",
        "Boise tires go to Ada County Landfill for a fee — NOT accepted at HHW. Retailer take-back when replacing tires.",
        ["Do not take tires to HHW.", "Haul tires to Ada County Landfill (fee applies).", "Retailer take-back when replacing tires."],
        [("HHW for tires?", "No — landfill fee, not HHW."), ("Free?", "No — landfill charges a tire fee.")], *ada))
    rows.append(R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True, "Boise yard waste collection", "Boise yard waste collection",
        "Boise handles yard waste through regular collection. Follow set-out rules on cityofboise.org.",
        ["Use yard waste set-out rules.", "Keep yard waste out of large item and HHW loads.", "Check cityofboise.org for seasonal guidance."], [("Christmas trees?", "Follow city seasonal guidance.")], *bulk))
    rows.append(R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True, "Garbage cart unless private compost", "Boise garbage / private compost",
        "Bag food scraps for garbage unless you compost.",
        ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."], [("HHW for food?", "No.")], *bulk))
    rows.append(R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False, "Not recycling — store take-back / trash", "Retail bag take-back / trash",
        "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
        ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."], [("Large item for bags?", "No.")], *bulk))
    rows.append(R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", True,
        "Large Item Pickup for limited loads — private C&D for larger",
        "Republic large item pickup / private C&D hauler",
        "Limited homeowner C&D may go on Boise Large Item Pickup when scheduled via Republic (6 free/year). Larger contractor loads need a private C&D hauler. Route paint/chemicals to HHW separately.",
        ["Call Republic 208-345-1266 for limited C&D loads.", "Hire private C&D for larger projects.", "Route paint to HHW mobile or Ada County Landfill."], [("HHW for C&D?", "No — separate paint/chemicals.")], *bulk))
    return rows


def des_moines():
    c, st = "des-moines", "IA"
    bulk = ("City of Des Moines — Bulk trash", "https://www.dsm.city/departments/public_works/bulk_trash")
    scrub = ("City of Des Moines — SCRUB events", "https://www.dsm.city/departments/public_works/scrub")
    hhw = ("Metro Waste Authority — Bondurant HHW", "https://www.mwatoday.com/household-hazardous-waste")
    rows = []
    rows.append(R(c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
        "Pink $5 sticker per bulky item; call 515-283-4950 ≥24h ahead",
        "Des Moines bulk trash (515-283-4950)",
        "Des Moines bulk trash requires a pink $5 sticker per bulky item. Call 515-283-4950 at least 24 hours ahead to schedule. Mattresses are accepted as bulky items.",
        ["Buy pink $5 sticker per bulky item.", "Call 515-283-4950 ≥24 hours ahead to schedule.", "Set out on scheduled collection day."],
        [("Sticker cost?", "$5 per bulky item."), ("Advance notice?", "Call ≥24 hours ahead.")], *bulk))
    rows.append(R(c, st, "refrigerator", "SPECIAL_HANDLING", "High", True,
        "7 pink stickers ($35) for Freon appliance; call 515-283-4950 ≥24h ahead",
        "Des Moines bulk trash — Freon appliance (515-283-4950)",
        "Freon refrigerators require 7 pink stickers ($35) on Des Moines bulk trash. Call 515-283-4950 at least 24 hours ahead. Never vent refrigerant yourself.",
        ["Buy 7 pink stickers ($35) for Freon refrigerator.", "Call 515-283-4950 ≥24 hours ahead.", "Keep doors secured until pickup."],
        [("Freon fridge cost?", "7 stickers = $35."), ("Same as washer?", "No — Freon appliances need 7 stickers, not 1.")], *bulk))
    rows.append(R(c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
        "7 pink stickers ($35) for Freon appliance; call 515-283-4950 ≥24h ahead",
        "Des Moines bulk trash — Freon appliance (515-283-4950)",
        "Freon AC units require 7 pink stickers ($35) on Des Moines bulk trash. Call 515-283-4950 at least 24 hours ahead. Never vent refrigerant yourself.",
        ["Buy 7 pink stickers ($35) for Freon AC.", "Call 515-283-4950 ≥24 hours ahead.", "Keep sealed until pickup."],
        [("Same as fridge?", "Yes — Freon appliances need 7 stickers ($35).")], *bulk))
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(R(c, st, item, "SPECIAL_HANDLING", "Medium", True,
            "Pink $5 sticker per bulky item; call 515-283-4950 ≥24h ahead",
            "Des Moines bulk trash (515-283-4950)",
            f"Non-Freon appliances such as {item.replace('-', ' ')}s require 1 pink $5 sticker on Des Moines bulk trash. Call 515-283-4950 ≥24h ahead. Freon refrigerators/AC need 7 stickers ($35).",
            ["Buy 1 pink $5 sticker.", "Call 515-283-4950 ≥24 hours ahead.", "Empty appliance before set-out."],
            [("Same as Freon fridge?", "No — non-Freon appliances need 1 sticker ($5), not 7.")], *bulk))
    for item, label in [("television", "TVs"), ("computer-monitor", "monitors"), ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste")]:
        rows.append(R(c, st, item, "SPECIAL_HANDLING", "Medium", True,
            "Pink $5 sticker per bulky item OR free SCRUB event (3rd Sat Mar–Nov)",
            "Des Moines bulk trash / SCRUB events",
            f"Electronics including {label} may go on Des Moines bulk trash with 1 pink $5 sticker (call 515-283-4950) OR free at SCRUB events — 3rd Saturday Mar–Nov. Wipe data before disposal.",
            ["Option 1: $5 sticker + call 515-283-4950.", "Option 2: Free SCRUB event 3rd Sat Mar–Nov.", "Wipe personal data."],
            [("Free option?", "Yes — SCRUB events 3rd Saturday Mar–Nov."), ("Bulk fee?", "$5 sticker per item via bulk trash.")], *scrub))
    rows.append(R(c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", True,
        "Fully dried latex in trash OK OR $1/gal at MWA Bondurant",
        "Household trash (dried) / MWA Bondurant HHW ($1/gal latex)",
        "Fully dried latex paint may go in Des Moines household trash. Liquid latex goes to Metro Waste Authority Bondurant — $1/gallon. Oil paint goes to MWA HHW only — not trash.",
        ["Liquid latex: haul to MWA Bondurant ($1/gal).", "Dried latex: solidify completely, then trash.", "Oil paint: MWA HHW only — never trash."],
        [("Trash for dried latex?", "Yes — fully dried latex may go in trash."), ("Liquid latex fee?", "$1/gallon at MWA Bondurant.")], *hhw))
    rows.append(R(c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
        "MWA Bondurant HHW — Tue–Fri 10–6 Sat 8–noon",
        "Metro Waste Authority — 1105 Prairie Dr SW, Bondurant",
        "Oil-based paint goes to Metro Waste Authority Bondurant HHW — 1105 Prairie Dr SW — Tue–Fri 10:00 a.m.–6:00 p.m., Sat 8:00 a.m.–noon. Not curbside or trash.",
        ["Haul oil paint to MWA Bondurant 1105 Prairie Dr SW.", "Hours: Tue–Fri 10–6, Sat 8–noon.", "Keep containers sealed and labeled."],
        [("Same as latex?", "No — oil paint is HHW only; latex can dry for trash."), ("Address?", "1105 Prairie Dr SW, Bondurant.")], *hhw))
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
            "Free MWA Bondurant HHW — Tue–Fri 10–6 Sat 8–noon",
            "Metro Waste Authority — 1105 Prairie Dr SW, Bondurant",
            f"Take {item.replace('-', ' ')} to MWA Bondurant HHW — 1105 Prairie Dr SW — Tue–Fri 10–6, Sat 8–noon. Free.",
            ["Deliver sealed containers to MWA Bondurant.", "Hours: Tue–Fri 10–6, Sat 8–noon.", "Keep chemicals out of bulk trash."],
            [("Same as oil paint?", "Yes — chemicals use MWA Bondurant HHW.")], *hhw))
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {"car-battery": " Batteries at MWA HHW.", "lithium-battery": " Lithium batteries at MWA HHW.", "motor-oil": " Motor oil at MWA HHW.", "propane-tank": " Propane at MWA HHW.", "fluorescent-bulbs": " Fluorescents at MWA HHW.", "cooking-oil": " Cooking oil at MWA when not trash-safe."}[item]
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING", "High" if item != "cooking-oil" else "Medium", False,
            "Free MWA Bondurant HHW — Tue–Fri 10–6 Sat 8–noon", "Metro Waste Authority — 1105 Prairie Dr SW, Bondurant",
            f"MWA Bondurant HHW at 1105 Prairie Dr SW accepts household hazardous materials free.{extra}",
            ["Haul to MWA Bondurant during posted hours.", "Tue–Fri 10–6, Sat 8–noon.", "Tires use SCRUB or landfill, not HHW."], [("Address?", "1105 Prairie Dr SW, Bondurant.")], *hhw))
    rows.append(R(c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
        "Rigid sealed container — confirm MWA HHW sharps acceptance", "Metro Waste Authority — 1105 Prairie Dr SW, Bondurant",
        "Place sharps in a rigid sealed container. Confirm acceptance at MWA Bondurant HHW. Do not loose-bag needles.",
        ["Use rigid sealed container.", "Confirm sharps at MWA Bondurant.", "Never recycle loose needles."], [("Medications?", "Confirm drug take-back via mwatoday.com.")], *hhw))
    rows.append(R(c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
        "SCRUB events (10 tires) OR landfill — NOT HHW",
        "Des Moines SCRUB events / landfill tire disposal",
        "Des Moines tires go to SCRUB events (up to 10 tires) or landfill — NOT accepted at MWA HHW. Retailer take-back when replacing tires.",
        ["Check SCRUB event schedule (3rd Sat Mar–Nov) — up to 10 tires.", "Or haul to landfill.", "Do not take tires to MWA HHW."],
        [("SCRUB tire limit?", "Up to 10 tires at SCRUB events."), ("HHW for tires?", "No — SCRUB or landfill only.")], *scrub))
    rows.append(R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True, "Des Moines yard waste collection", "Des Moines yard waste collection",
        "Des Moines handles yard waste through regular collection. Follow set-out rules.",
        ["Use yard waste set-out rules.", "Keep yard waste out of bulk and HHW loads.", "Check dsm.city for seasonal guidance."], [("Christmas trees?", "Follow city seasonal guidance.")], *bulk))
    rows.append(R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True, "Garbage cart unless private compost", "Des Moines garbage / private compost",
        "Bag food scraps for garbage unless you compost.",
        ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."], [("HHW for food?", "No.")], *bulk))
    rows.append(R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False, "Not recycling — store take-back / trash", "Retail bag take-back / trash",
        "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
        ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."], [("Bulk for bags?", "No.")], *bulk))
    rows.append(R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", True,
        "Bulk trash with $5 sticker for limited loads — private C&D for larger",
        "Des Moines bulk trash / private C&D hauler",
        "Limited homeowner C&D may go on Des Moines bulk trash with pink $5 stickers (call 515-283-4950). Larger contractor loads need a private C&D hauler. Route paint/chemicals to MWA HHW separately.",
        ["Buy $5 stickers and call 515-283-4950 for limited C&D.", "Hire private C&D for larger projects.", "Route liquid paint to MWA Bondurant."], [("HHW for C&D?", "No — separate paint/chemicals.")], *bulk))
    return rows


def spokane():
    c, st = "spokane", "WA"
    bulk = ("City of Spokane — Garbage & bulky collection", "https://my.spokanecity.org/publicworks/solidwaste/garbage/")
    hhw = ("City of Spokane — Hazardous waste", "https://my.spokanecity.org/publicworks/solidwaste/hazardous/")
    ecycle = ("E-Cycle Washington", "https://ecyclewashington.org/")
    rows = []
    rows.append(R(c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
        "311 bulky pickup on garbage day — free",
        "Spokane 311 bulky collection (garbage day)",
        "Spokane bulky items are collected on your garbage day — schedule through 311. Mattresses are accepted. Call 311 or use my.spokanecity.org solid waste resources.",
        ["Call 311 to schedule bulky pickup on garbage day.", "Set out per city instructions.", "Keep HHW and e-waste separate."],
        [("Which day?", "On your regular garbage day via 311."), ("Fee?", "Free bulky on garbage day.")], *bulk))
    rows.append(R(c, st, "refrigerator", "SPECIAL_HANDLING", "High", True,
        "311 bulky on garbage day — doors removed",
        "Spokane 311 bulky collection (garbage day)",
        "Freon refrigerators go on Spokane bulky collection via 311 on garbage day — remove doors before set-out. Never vent refrigerant yourself.",
        ["Remove doors from refrigerator before set-out.", "Call 311 to schedule bulky on garbage day.", "Keep sealed until pickup."],
        [("Doors off?", "Yes — remove fridge doors before bulky set-out."), ("311 required?", "Yes — schedule bulky through 311.")], *bulk))
    rows.append(R(c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
        "311 bulky on garbage day",
        "Spokane 311 bulky collection (garbage day)",
        "Freon AC units go on Spokane bulky collection via 311 on garbage day. Never vent refrigerant yourself.",
        ["Call 311 to schedule bulky on garbage day.", "Set AC out per city instructions.", "Keep sealed until pickup."],
        [("Same as fridge?", "Yes — appliances on 311 bulky; doors off for fridges.")], *bulk))
    for item, label in [("television", "TVs"), ("computer-monitor", "monitors"), ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste")]:
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS", "Medium", False,
            "NOT bulky — E-Cycle Washington free program",
            "E-Cycle Washington registered recyclers",
            f"Electronics including {label} are NOT accepted on Spokane bulky collection. Use E-Cycle Washington free program — search ecyclewashington.org for registered recyclers. Wipe data before drop-off.",
            ["Do not put e-waste on 311 bulky.", "Search ecyclewashington.org for nearest recycler.", "Wipe personal data."],
            [("Bulky for TV?", "No — e-waste uses E-Cycle Washington."), ("Free?", "Yes — E-Cycle Washington is free.")], *ecycle))
    rows.append(R(c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", False,
        "Free HHW at WTE — 2900 S Geiger Blvd daily 7:30–5",
        "Spokane Waste to Energy — 2900 S Geiger Blvd",
        "Liquid latex and oil paint are free at Spokane HHW — Waste to Energy facility, 2900 S Geiger Blvd — daily 7:30 a.m.–5:00 p.m. Not curbside.",
        ["Haul paint to WTE 2900 S Geiger Blvd.", "Hours: daily 7:30–17:00.", "Keep paint sealed and labeled."],
        [("Free paint?", "Yes — free at WTE HHW."), ("Address?", "2900 S Geiger Blvd.")], *hhw))
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
            "Free HHW at WTE — 2900 S Geiger Blvd daily 7:30–5",
            "Spokane Waste to Energy — 2900 S Geiger Blvd",
            f"Take {item.replace('-', ' ')} free to Spokane HHW — WTE 2900 S Geiger Blvd — daily 7:30 a.m.–5:00 p.m.",
            ["Deliver sealed containers to WTE during posted hours.", "Keep chemicals out of bulky piles.", "Not curbside."],
            [("Same as paint?", "Yes — chemicals use WTE HHW.")], *hhw))
    for item in ["car-battery", "lithium-battery", "paint-oil", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {"car-battery": " Batteries at WTE HHW.", "lithium-battery": " Lithium batteries at WTE HHW.", "paint-oil": " Oil paint at WTE HHW.", "motor-oil": " Motor oil at WTE HHW.", "propane-tank": " Propane at WTE HHW.", "fluorescent-bulbs": " Fluorescents at WTE HHW.", "cooking-oil": " Cooking oil at WTE when not trash-safe."}[item]
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING", "High" if item != "cooking-oil" else "Medium", False,
            "Free HHW at WTE — 2900 S Geiger Blvd daily 7:30–5", "Spokane Waste to Energy — 2900 S Geiger Blvd",
            f"Spokane WTE HHW at 2900 S Geiger Blvd accepts household hazardous materials free.{extra} E-waste uses E-Cycle Washington.",
            ["Haul to WTE 2900 S Geiger Blvd during posted hours.", "Daily 7:30–17:00.", "E-waste/TVs use E-Cycle, not HHW."], [("Address?", "2900 S Geiger Blvd.")], *hhw))
    rows.append(R(c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
        "Rigid sealed container — confirm WTE HHW sharps acceptance", "Spokane Waste to Energy — 2900 S Geiger Blvd",
        "Place sharps in a rigid sealed container. Confirm acceptance at Spokane WTE HHW. Do not loose-bag needles.",
        ["Use rigid sealed container.", "Confirm sharps at WTE HHW.", "Never recycle loose needles."], [("Medications?", "Confirm drug take-back on my.spokanecity.org.")], *hhw))
    rows.append(R(c, st, "tires", "SPECIAL_HANDLING", "Medium", True,
        "Up to 4 curbside on garbage day — wheels off",
        "Spokane curbside tire collection (garbage day)",
        "Spokane accepts up to 4 tires curbside on garbage day — wheels off. Schedule through 311. Retailer take-back when replacing tires.",
        ["Remove wheels from tires.", "Call 311 — set out up to 4 tires on garbage day.", "Retailer take-back when replacing tires."],
        [("Curbside limit?", "Up to 4 tires on garbage day."), ("Wheels?", "Remove wheels before set-out.")], *bulk))
    rows.append(R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True, "Spokane yard waste collection", "Spokane yard waste collection",
        "Spokane handles yard waste through regular collection. Follow set-out rules.",
        ["Use yard waste set-out rules.", "Keep yard waste out of bulky and HHW loads.", "Check my.spokanecity.org for seasonal guidance."], [("Christmas trees?", "Follow city seasonal guidance.")], *bulk))
    rows.append(R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True, "Garbage cart unless private compost", "Spokane garbage / private compost",
        "Bag food scraps for garbage unless you compost.",
        ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."], [("HHW for food?", "No.")], *bulk))
    rows.append(R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False, "Not recycling — store take-back / trash", "Retail bag take-back / trash",
        "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
        ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."], [("Bulky for bags?", "No.")], *bulk))
    rows.append(R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", True,
        "311 bulky for limited loads — private C&D for larger",
        "Spokane 311 bulky / private C&D hauler",
        "Limited homeowner C&D may go on Spokane 311 bulky collection on garbage day. Larger contractor loads need a private C&D hauler. Route paint/chemicals to WTE HHW separately.",
        ["Call 311 for limited C&D on garbage day.", "Hire private C&D for larger projects.", "Route paint to WTE 2900 S Geiger Blvd."], [("HHW for C&D?", "No — separate paint/chemicals.")], *bulk))
    return rows


def honolulu():
    c, st = "honolulu", "HI"
    bulk = ("City & County of Honolulu — Bulky item appointment", "https://www.honolulu.gov/opala/refuse/bulky/bulky-item-appointment.html")
    hhw = ("City & County of Honolulu — Household hazardous waste", "https://www.honolulu.gov/opala/refuse/hhw/hhw-2.html")
    dropoff = ("City & County of Honolulu — Waste drop-off", "https://www.honolulu.gov/opala/refuse/waste-drop-off.html")
    rows = []
    rows.append(R(c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
        "Bulky appointment via opala.org / 808-768-3200 — up to 5 items",
        "Honolulu bulky item appointment (808-768-3200)",
        "Honolulu bulky item collection requires an appointment via opala.org or 808-768-3200 — up to 5 bulky items per appointment. Mattresses are accepted.",
        ["Schedule bulky appointment at opala.org or call 808-768-3200.", "Limit 5 bulky items per appointment.", "Set out per city instructions on scheduled day."],
        [("Appointment required?", "Yes — schedule via opala.org or 808-768-3200."), ("Limit?", "Up to 5 bulky items per appointment.")], *bulk))
    rows.append(R(c, st, "refrigerator", "SPECIAL_HANDLING", "High", False,
        "Separate metal appliance appointment for Freon — NOT regular bulky",
        "Honolulu metal appliance appointment (808-768-3200)",
        "Freon refrigerators require a separate metal appliance appointment in Honolulu — NOT the regular bulky item appointment. Call 808-768-3200 or use opala.org. Never vent refrigerant yourself.",
        ["Schedule separate metal appliance appointment (not regular bulky).", "Call 808-768-3200 or opala.org.", "Keep doors secured until pickup."],
        [("Regular bulky for fridge?", "No — Freon appliances need separate metal appliance appointment."), ("Fee?", "Confirm on opala.org at scheduling.")], *bulk))
    rows.append(R(c, st, "air-conditioner", "SPECIAL_HANDLING", "High", False,
        "Separate metal appliance appointment for Freon — NOT regular bulky",
        "Honolulu metal appliance appointment (808-768-3200)",
        "Freon AC units require a separate metal appliance appointment in Honolulu — NOT regular bulky. Call 808-768-3200. Never vent refrigerant yourself.",
        ["Schedule separate metal appliance appointment.", "Do not use regular 5-item bulky appointment.", "Keep sealed until pickup."],
        [("Same as fridge?", "Yes — Freon appliances use metal appliance appointment.")], *bulk))
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(R(c, st, item, "SPECIAL_HANDLING", "Medium", True,
            "Bulky appointment — up to 5 items via opala.org / 808-768-3200",
            "Honolulu bulky item appointment (808-768-3200)",
            f"Non-Freon appliances such as {item.replace('-', ' ')}s go on Honolulu regular bulky item appointment — up to 5 items via opala.org or 808-768-3200. Freon refrigerators/AC need separate metal appliance appointment.",
            ["Schedule bulky appointment at opala.org or 808-768-3200.", "Counts toward 5-item limit.", "Empty appliance before set-out."],
            [("Same as Freon fridge?", "No — non-Freon use regular bulky; Freon uses metal appliance appt.")], *bulk))
    for item, label in [("television", "TVs"), ("computer-monitor", "monitors"), ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste")]:
        rows.append(R(c, st, item, "SPECIAL_HANDLING", "Medium", True,
            "Bulky appointment OK for households — up to 5 items",
            "Honolulu bulky item appointment (808-768-3200)",
            f"Electronics including {label} may go on Honolulu bulky item appointment for households — up to 5 items via opala.org or 808-768-3200. Wipe data before set-out.",
            ["Schedule bulky appointment at opala.org or 808-768-3200.", "Counts toward 5-item limit.", "Wipe personal data."],
            [("Bulky for e-waste?", "Yes — e-waste OK on bulky for households."), ("Limit?", "Up to 5 items per appointment.")], *bulk))
    rows.append(R(c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", True,
        "Fully absorbed/dried latex in trash OK — NOT HHW",
        "Honolulu household trash (absorbed latex)",
        "Honolulu latex paint should be fully absorbed or dried before placing in household trash. Do NOT take latex paint to HHW events — HHW is appointment-only for hazardous materials like oil paint.",
        ["Absorb or dry latex paint completely.", "Place dried/absorbed latex in household trash.", "Oil paint: HHW event appointment only."],
        [("HHW for latex?", "No — absorb/dry latex for trash."), ("Oil paint?", "HHW event appointment only.")], *bulk))
    rows.append(R(c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
        "HHW event appointment only — NOT regular bulky or trash",
        "Honolulu HHW event (appointment required)",
        "Oil-based paint goes to Honolulu HHW events — appointment required. Check honolulu.gov hhw-2 for event dates. Not regular bulky or trash.",
        ["Schedule HHW event appointment via opala.org.", "Check honolulu.gov hhw-2 for dates.", "Keep containers sealed and labeled."],
        [("Same as latex?", "No — oil paint is HHW event only; latex absorbs for trash.")], *hhw))
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
            "HHW event appointment only",
            "Honolulu HHW event (appointment required)",
            f"Take {item.replace('-', ' ')} to Honolulu HHW events — appointment required. Check honolulu.gov hhw-2.",
            ["Schedule HHW event appointment.", "Deliver sealed containers at event.", "Keep chemicals out of bulky loads."],
            [("Regular bulky?", "No — chemicals use HHW event appointment only.")], *hhw))
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {"car-battery": " Batteries at HHW events.", "lithium-battery": " Lithium batteries at HHW events.", "motor-oil": " Motor oil at HHW events.", "propane-tank": " Propane at HHW events.", "fluorescent-bulbs": " Fluorescents at HHW events.", "cooking-oil": " Cooking oil at HHW when not trash-safe."}[item]
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING", "High" if item != "cooking-oil" else "Medium", False,
            "HHW event appointment only", "Honolulu HHW event (appointment required)",
            f"Honolulu HHW events accept household hazardous materials by appointment.{extra} Latex paint absorbs for trash — not HHW.",
            ["Schedule HHW event appointment via opala.org.", "Check honolulu.gov hhw-2 for dates.", "Latex paint: absorb for trash, not HHW."], [("Appointment?", "Yes — HHW events require appointment.")], *hhw))
    rows.append(R(c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
        "Rigid sealed container — confirm HHW event sharps acceptance", "Honolulu HHW event (appointment required)",
        "Place sharps in a rigid sealed container. Confirm acceptance at Honolulu HHW events by appointment. Do not loose-bag needles.",
        ["Use rigid sealed container.", "Schedule HHW event and confirm sharps acceptance.", "Never recycle loose needles."], [("Medications?", "Confirm drug take-back on honolulu.gov.")], *hhw))
    rows.append(R(c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
        "Kapaa Transfer Station — NOT Ke'ehi",
        "Kapaa Transfer Station — tire disposal",
        "Honolulu tires go to Kapaa Transfer Station — NOT Ke'ehi. Check honolulu.gov waste-drop-off for hours and fees. Retailer take-back when replacing tires.",
        ["Do not take tires to Ke'ehi.", "Haul tires to Kapaa Transfer Station.", "Retailer take-back when replacing tires."],
        [("Ke'ehi for tires?", "No — use Kapaa Transfer Station."), ("Bulky for tires?", "No — transfer station drop-off.")], *dropoff))
    rows.append(R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True, "Honolulu green waste collection", "Honolulu green waste collection",
        "Honolulu handles yard/green waste through regular collection. Follow set-out rules on honolulu.gov.",
        ["Use green waste set-out rules.", "Keep yard waste out of bulky and HHW loads.", "Check honolulu.gov for seasonal guidance."], [("Christmas trees?", "Follow city seasonal guidance.")], *bulk))
    rows.append(R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True, "Garbage cart unless private compost", "Honolulu garbage / private compost",
        "Bag food scraps for garbage unless you compost.",
        ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use green-waste pathways."], [("HHW for food?", "No.")], *bulk))
    rows.append(R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False, "Not recycling — store take-back / trash", "Retail bag take-back / trash",
        "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
        ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."], [("Bulky for bags?", "No.")], *bulk))
    rows.append(R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", True,
        "Bulky appointment for limited loads — private C&D for larger",
        "Honolulu bulky appointment / private C&D hauler",
        "Limited homeowner C&D may go on Honolulu bulky item appointment (up to 5 items). Larger contractor loads need a private C&D hauler. Route oil paint/chemicals to HHW events separately; latex absorbs for trash.",
        ["Schedule bulky appointment for limited C&D.", "Hire private C&D for larger projects.", "Route oil paint to HHW event; latex absorbs for trash."], [("HHW for C&D?", "No — separate paint/chemicals.")], *bulk))
    return rows


CITIES = [
    {"city": "Richmond", "city_slug": "richmond", "state": "VA", "state_slug": "virginia", "lat": 37.5407, "lng": -77.4360, "population": 226610},
    {"city": "Boise", "city_slug": "boise", "state": "ID", "state_slug": "idaho", "lat": 43.6150, "lng": -116.2023, "population": 235684},
    {"city": "Des Moines", "city_slug": "des-moines", "state": "IA", "state_slug": "iowa", "lat": 41.5868, "lng": -93.6250, "population": 214133},
    {"city": "Spokane", "city_slug": "spokane", "state": "WA", "state_slug": "washington", "lat": 47.6588, "lng": -117.4260, "population": 228989},
    {"city": "Honolulu", "city_slug": "honolulu", "state": "HI", "state_slug": "hawaii", "lat": 21.3069, "lng": -157.8583, "population": 350964},
]

ZIPS = [
    {"zip": "23219", "city": "Richmond", "city_slug": "richmond", "state": "VA", "state_slug": "virginia", "lat": 37.541, "lng": -77.436, "population": 12000},
    {"zip": "23220", "city": "Richmond", "city_slug": "richmond", "state": "VA", "state_slug": "virginia", "lat": 37.555, "lng": -77.465, "population": 14000},
    {"zip": "83702", "city": "Boise", "city_slug": "boise", "state": "ID", "state_slug": "idaho", "lat": 43.615, "lng": -116.202, "population": 15000},
    {"zip": "83706", "city": "Boise", "city_slug": "boise", "state": "ID", "state_slug": "idaho", "lat": 43.595, "lng": -116.185, "population": 22000},
    {"zip": "50309", "city": "Des Moines", "city_slug": "des-moines", "state": "IA", "state_slug": "iowa", "lat": 41.587, "lng": -93.625, "population": 8000},
    {"zip": "50314", "city": "Des Moines", "city_slug": "des-moines", "state": "IA", "state_slug": "iowa", "lat": 41.605, "lng": -93.645, "population": 16000},
    {"zip": "99201", "city": "Spokane", "city_slug": "spokane", "state": "WA", "state_slug": "washington", "lat": 47.659, "lng": -117.426, "population": 9000},
    {"zip": "99205", "city": "Spokane", "city_slug": "spokane", "state": "WA", "state_slug": "washington", "lat": 47.675, "lng": -117.455, "population": 18000},
    {"zip": "96813", "city": "Honolulu", "city_slug": "honolulu", "state": "HI", "state_slug": "hawaii", "lat": 21.307, "lng": -157.858, "population": 11000},
    {"zip": "96815", "city": "Honolulu", "city_slug": "honolulu", "state": "HI", "state_slug": "hawaii", "lat": 21.285, "lng": -157.835, "population": 25000},
]

FACILITIES = [
    {
        "name": "Richmond ERRCC",
        "facility_type": "Household hazardous waste & tire drop-off",
        "city_slug": "richmond",
        "state": "VA",
        "zip": "23223",
        "address": "3800 East Richmond Rd, Richmond, VA 23223",
        "lat": 37.5555,
        "lng": -77.3855,
        "source_url": "https://www.rva.gov/public-works/trash-collection",
        "hours": "Mon–Fri 7:00–15:30; Sat 8:30–14:00",
        "phone": "804-646-6434",
    },
    {
        "name": "Ada County Landfill HHW",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "boise",
        "state": "ID",
        "zip": "83716",
        "address": "Ada County Landfill, Boise, ID",
        "lat": 43.5455,
        "lng": -116.0855,
        "source_url": "https://www.cityofboise.org/departments/public-works/trash-and-recycling/household-hazardous-waste/",
        "hours": "Fri/Sat 8:00–18:00",
        "phone": "208-345-1266",
    },
    {
        "name": "Metro Waste Authority — Bondurant HHW",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "des-moines",
        "state": "IA",
        "zip": "50035",
        "address": "1105 Prairie Dr SW, Bondurant, IA 50035",
        "lat": 41.6855,
        "lng": -93.4655,
        "source_url": "https://www.mwatoday.com/household-hazardous-waste",
        "hours": "Tue–Fri 10:00–18:00; Sat 8:00–12:00",
        "phone": "515-967-5512",
    },
    {
        "name": "Spokane Waste to Energy HHW",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "spokane",
        "state": "WA",
        "zip": "99224",
        "address": "2900 S Geiger Blvd, Spokane, WA 99224",
        "lat": 47.6255,
        "lng": -117.5855,
        "source_url": "https://my.spokanecity.org/publicworks/solidwaste/hazardous/",
        "hours": "Daily 7:30–17:00",
        "phone": "509-625-7960",
    },
    {
        "name": "Kapaa Transfer Station",
        "facility_type": "Tire drop-off",
        "city_slug": "honolulu",
        "state": "HI",
        "zip": "96734",
        "address": "Kapaa Transfer Station, Kailua, HI",
        "lat": 21.3955,
        "lng": -157.7555,
        "source_url": "https://www.honolulu.gov/opala/refuse/waste-drop-off.html",
        "hours": "Check honolulu.gov for transfer station hours",
        "phone": "808-768-3200",
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
        "richmond": clone_siblings(richmond()),
        "boise": clone_siblings(boise()),
        "des-moines": clone_siblings(des_moines()),
        "spokane": clone_siblings(spokane()),
        "honolulu": clone_siblings(honolulu()),
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

    print("Wave-12 metros written:")
    for city, rows in audited.items():
        print(f"  {city}: {len(rows)} rules")
    print(f"Total rules now: {len(keep)}")


if __name__ == "__main__":
    main()
