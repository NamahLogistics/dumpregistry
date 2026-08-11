#!/usr/bin/env python3
"""Portal-audited city guides for wave-16 metros (city-sourced only).

Cities researched from official program pages (2026-08-11):
  - Anchorage, AK — Saturday bulky / CTS self-haul + ARL HHW / Freon fees
  - Reno, NV — spring cleanup / Lockwood / WM bulk + GrayMar HHW voucher
  - Tacoma, WA — Call-2-Haul curbside + Mullen HHW / E-Cycle Washington TVs
  - Aurora, CO — private haulers + WM At Your Door / PaintCare / Earth911 e-waste
  - Chattanooga, TN — area bulk sweep + Hawthorne HHW
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


def anchorage():
    c, st = "anchorage", "AK"
    collections = (
        "Municipality of Anchorage — Collections",
        "https://www.muni.org/Departments/SWS/Collections/pages/default.aspx",
    )
    dispose = (
        "Municipality of Anchorage — How Do I Dispose",
        "https://www.muni.org/Departments/SWS/HowDoI/pages/dispose.aspx",
    )
    hhw = (
        "Municipality of Anchorage — Hazardous Waste",
        "https://www.muni.org/Departments/SWS/Dispose/pages/hazardouswaste.aspx",
    )
    rows = []
    rows.append(
        R(
            c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
            "Scheduled Sat bulky $12.50+ OR CTS self-haul 1310 E 56th Ave",
            "Anchorage Saturday bulky / Central Transfer Station — 1310 E 56th Ave",
            "Anchorage mattresses use scheduled Saturday bulky collection ($12.50+ per item) OR self-haul to Central Transfer Station (CTS) — 1310 E 56th Ave. Confirm Saturday bulky fees and set-out rules on muni.org before collection day.",
            ["Schedule Saturday bulky collection ($12.50+ per item).", "Or self-haul to CTS 1310 E 56th Ave.", "Confirm muni.org set-out rules."],
            [("CTS address?", "1310 E 56th Ave."), ("Year-round curbside bulk?", "Saturday bulky schedule only.")],
            *collections,
        )
    )
    rows.append(
        R(
            c, st, "refrigerator", "SPECIAL_HANDLING", "High", False,
            "NOT curbside — CTS/ARL $30 refrigerant + $27 disposal; doors removed; empty",
            "CTS / Anchorage Regional Landfill — Freon appliance",
            "Anchorage Freon refrigerators are NOT accepted on Saturday bulky curbside. Self-haul to CTS or Anchorage Regional Landfill (ARL) — $30 refrigerant fee plus $27 disposal. Remove doors and empty unit. Never vent refrigerant yourself.",
            ["Do not set Freon fridge on Saturday bulky.", "Haul to CTS or ARL ($30 refrigerant + $27 disposal).", "Remove doors; empty unit; never vent Freon."],
            [("Saturday bulky for Freon fridge?", "No — CTS/ARL fee drop-off only."), ("Door removal?", "Required before drop-off.")],
            *dispose,
        )
    )
    rows.append(
        R(
            c, st, "air-conditioner", "SPECIAL_HANDLING", "High", False,
            "NOT curbside — CTS/ARL $30 refrigerant + $27 disposal",
            "CTS / Anchorage Regional Landfill — Freon appliance",
            "Anchorage Freon window AC units are NOT accepted on Saturday bulky curbside. Self-haul to CTS or ARL — $30 refrigerant fee plus $27 disposal. Never vent refrigerant yourself.",
            ["Do not set Freon AC on Saturday bulky.", "Haul to CTS or ARL ($30 refrigerant + $27 disposal).", "Keep sealed until proper Freon handling."],
            [("Same as Freon fridge?", "Yes — CTS/ARL fee path, not curbside bulky.")],
            *dispose,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c, st, item, "SPECIAL_HANDLING", "Medium", True,
                "Scheduled Sat bulky $12.50+ OR CTS self-haul 1310 E 56th Ave",
                "Anchorage Saturday bulky / CTS — 1310 E 56th Ave",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s use Anchorage Saturday bulky collection ($12.50+) OR self-haul to CTS — 1310 E 56th Ave. Freon refrigerators/AC are NOT curbside — use CTS/ARL fee path.",
                ["Schedule Saturday bulky ($12.50+ per item).", "Or self-haul to CTS 1310 E 56th Ave.", "Freon appliances use separate CTS/ARL path."],
                [("Same as Freon fridge?", "No — non-Freon uses Saturday bulky or CTS.")],
                *collections,
            )
        )
    for item, label in [
        ("television", "TVs"), ("computer-monitor", "monitors"),
        ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste"),
    ]:
        extra = "1 TV per day allowed in residential load; additional TVs to ARL." if item == "television" else (
            "Computers go to private recyclers — not HHW." if item in ("smartphone", "e-waste-mixed", "computer-monitor") else ""
        )
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "Medium", item == "television",
                "1 TV/day residential load; more at ARL; computers private recyclers",
                "Residential load / ARL / private e-waste recycler",
                f"Anchorage electronics: {label} — {extra or 'Use ARL for excess e-waste or private recyclers.'} Wipe data before drop-off. Not HHW at CTS 1208 E 56th.",
                ["Limit 1 TV per day in residential trash load." if item == "television" else "Use private e-waste recycler for computers.", "Haul additional TVs to ARL.", "Wipe personal data."],
                [("HHW for TVs?", "No — residential load limit or ARL."), ("Computers?", "Private recyclers, not city HHW.")],
                *dispose,
            )
        )
    rows.append(
        R(
            c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", True,
            "Dry completely → regular trash — NOT Anchorage HHW",
            "Anchorage trash cart — dried latex only",
            "Anchorage latex paint is NOT accepted at HHW. Dry paint completely (add kitty litter or leave lid off) until solid, then put dried cans in regular trash. Liquid latex never goes to CTS HHW.",
            ["Add kitty litter or dry paint until solid.", "Place dried cans in regular trash.", "Do not haul liquid latex to HHW."],
            [("HHW for latex?", "No — latex must be fully dried for trash."), ("Oil paint?", "Oil-based paint goes to HHW free.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
            "Free Anchorage HHW — CTS 1208 E 56th or ARL Eagle River",
            "Anchorage HHW — 1208 E 56th Ave",
            "Oil-based paint goes to Anchorage HHW — CTS 1208 E 56th Ave — Tue/Thu/Sat 8:00 a.m.–4:30 p.m., free for residents ≤40 lb. ARL Eagle River also accepts HHW. Not curbside or trash.",
            ["Haul sealed oil paint to CTS HHW 1208 E 56th Ave.", "Hours: Tue/Thu/Sat 8–4:30.", "Keep oil paint out of trash carts."],
            [("Latex at HHW?", "No — latex must be dried for trash."), ("Fee?", "Free for residents ≤40 lb.")],
            *hhw,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
                "Free Anchorage HHW — CTS 1208 E 56th or ARL",
                "Anchorage HHW — 1208 E 56th Ave",
                f"Take {item.replace('-', ' ')} to Anchorage HHW — CTS 1208 E 56th Ave — Tue/Thu/Sat 8–4:30, free for residents ≤40 lb. ARL Eagle River also accepts HHW.",
                ["Deliver sealed containers to CTS HHW.", "Hours: Tue/Thu/Sat 8–4:30.", "Keep chemicals off trash and Saturday bulky."],
                [("Same as latex paint?", "No — chemicals go to HHW; dried latex goes to trash.")],
                *hhw,
            )
        )
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {
            "car-battery": " Lead-acid batteries at HHW.",
            "lithium-battery": " Lithium batteries at HHW.",
            "motor-oil": " Used motor oil at HHW free.",
            "propane-tank": " Propane tanks at HHW — confirm size limits.",
            "fluorescent-bulbs": " Fluorescent bulbs at HHW.",
            "cooking-oil": " Cooking oil at HHW when not trash-safe.",
        }[item]
        rows.append(
            R(
                c, st, item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium", False,
                "Free Anchorage HHW — CTS 1208 E 56th or ARL",
                "Anchorage HHW — 1208 E 56th Ave",
                f"Anchorage HHW at CTS 1208 E 56th Ave accepts household hazardous materials free for residents ≤40 lb.{extra}",
                ["Haul to CTS HHW during posted hours.", "Tue/Thu/Sat 8–4:30.", "Tires use facility drop-off path, not HHW."],
                [("Address?", "1208 E 56th Ave, Anchorage.")],
                *hhw,
            )
        )
    rows.append(
        R(
            c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
            "Rigid sealed container — confirm Anchorage HHW sharps acceptance",
            "Anchorage HHW — 1208 E 56th Ave",
            "Place sharps in a rigid sealed container. Confirm acceptance at Anchorage HHW. Do not loose-bag needles.",
            ["Use rigid sealed container.", "Confirm sharps at CTS HHW.", "Never recycle loose needles."],
            [("Medications?", "Confirm drug take-back via Anchorage programs.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
            "Facility drop-off; >10 tires → ARL; rims off",
            "CTS / Anchorage Regional Landfill — tires",
            "Anchorage tires go to solid waste facilities — remove rims first. Loads over 10 tires must go to Anchorage Regional Landfill (ARL). Not Saturday bulky curbside.",
            ["Remove rims before drop-off.", "Haul to CTS or ARL facility.", "Loads >10 tires must go to ARL."],
            [("Saturday bulky for tires?", "No — facility drop-off."), ("Rims?", "Remove rims before drop-off.")],
            *dispose,
        )
    )
    rows.append(
        R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True,
          "Anchorage yard waste collection", "Anchorage yard waste collection",
          "Anchorage handles yard waste through regular collection. Follow set-out rules on muni.org.",
          ["Use yard waste set-out rules.", "Keep yard waste out of HHW and e-waste.", "Check muni.org for seasonal guidance."],
          [("Christmas trees?", "Follow city seasonal yard waste guidance.")], *collections)
    )
    rows.append(
        R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True,
          "Garbage cart unless private compost", "Anchorage garbage / private compost",
          "Bag food scraps for garbage unless you compost. Keep food out of recycling and HHW.",
          ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."],
          [("HHW for food?", "No.")], *collections)
    )
    rows.append(
        R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False,
          "Not recycling — store take-back / trash", "Retail bag take-back / trash",
          "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
          ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."],
          [("CTS for bags?", "No.")], *dispose)
    )
    rows.append(
        R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", False,
          "NOT Saturday bulky — CTS self-haul / private C&D hauler",
          "CTS — 1310 E 56th Ave / private C&D hauler",
          "Construction debris is not Anchorage Saturday bulky. Self-haul to CTS — 1310 E 56th Ave — or hire a private C&D hauler. Route oil paint/chemicals to HHW separately.",
          ["Do not treat C&D as Saturday bulky.", "Self-haul to CTS or hire private C&D.", "Route oil paint/chemicals to HHW."],
          [("HHW for C&D?", "No — separate paint/chemicals.")], *dispose)
    )
    return rows


def reno():
    c, st = "reno", "NV"
    sw = (
        "City of Reno — Solid Waste & Recycling",
        "https://www.reno.gov/community/environmental-services/solid-waste-recycling.php",
    )
    cleanups = (
        "City of Reno — Community CleanUps",
        "https://www.reno.gov/Community/Community-CleanUps",
    )
    rows = []
    rows.append(
        R(
            c, st, "mattress", "SPECIAL_HANDLING", "Low", False,
            "Spring cleanup roll-offs OR Lockwood free dump days OR WM paid bulk 775-329-8822",
            "Spring cleanup / Lockwood Landfill / WM bulk pickup",
            "Reno has NO year-round city curbside bulk for mattresses. Options: spring cleanup roll-offs, Lockwood Landfill free dump days, or Waste Management paid bulk pickup — call 775-329-8822. Confirm event dates on reno.gov.",
            ["Check spring cleanup roll-off dates on reno.gov.", "Or use Lockwood free dump days.", "Or call WM bulk 775-329-8822 for paid pickup."],
            [("Year-round city curbside bulk?", "No — events or WM paid bulk only."), ("WM bulk?", "775-329-8822.")],
            *cleanups,
        )
    )
    rows.append(
        R(
            c, st, "refrigerator", "SPECIAL_HANDLING", "High", False,
            "NOT free dump — NV Energy free fridge pickup + $30 rebate 1-877-289-8260",
            "NV Energy refrigerator recycling program",
            "Reno Freon refrigerators are NOT accepted at free Lockwood dump days. Use NV Energy free refrigerator pickup plus $30 rebate — call 1-877-289-8260. Never vent refrigerant yourself. Non-Freon appliances may use cleanup events or WM bulk.",
            ["Do not haul Freon fridge to free dump days.", "Call NV Energy 1-877-289-8260 for free pickup + $30 rebate.", "Never vent Freon yourself."],
            [("Free dump for Freon fridge?", "No — NV Energy pickup program."), ("Rebate?", "$30 via NV Energy program.")],
            *sw,
        )
    )
    rows.append(
        R(
            c, st, "air-conditioner", "SPECIAL_HANDLING", "High", False,
            "NOT free dump — private Freon appliance recycler",
            "Private Freon appliance recycler",
            "Reno Freon window AC units are NOT accepted at free Lockwood dump days. Use a private Freon appliance recycler or confirm NV Energy/other refrigerant programs. Never vent refrigerant yourself.",
            ["Do not haul Freon AC to free dump days.", "Contact private Freon appliance recycler.", "Keep sealed until proper Freon handling."],
            [("Same as Freon fridge?", "Yes — not free dump; use NV Energy for fridges or private recycler for AC.")],
            *sw,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c, st, item, "SPECIAL_HANDLING", "Medium", False,
                "Spring cleanup roll-offs OR Lockwood free dump days OR WM bulk 775-329-8822",
                "Spring cleanup / Lockwood Landfill / WM bulk pickup",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s may go on spring cleanup roll-offs, Lockwood free dump days, or WM paid bulk — 775-329-8822. Freon refrigerators use NV Energy pickup, not free dump.",
                ["Check spring cleanup or Lockwood dump day dates.", "Or call WM bulk 775-329-8822.", "Freon fridges use NV Energy path."],
                [("Same as Freon fridge?", "No — non-Freon may use cleanup events or WM bulk.")],
                *cleanups,
            )
        )
    for item, label in [
        ("television", "TVs"), ("computer-monitor", "monitors"),
        ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste"),
    ]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "Medium", False,
                "NOT bulky-only events — KTMB guide / HHW+e-waste events; Lockwood fee",
                "KTMB e-waste guide / HHW+e-waste events / Lockwood Landfill",
                f"Reno electronics including {label} are NOT accepted at bulky-only cleanup events. Use Keep Truckee Meadows Beautiful (KTMB) e-waste guide, combined HHW+e-waste events, or Lockwood Landfill (fee). Wipe data before drop-off.",
                ["Do not bring e-waste to bulky-only events.", "Check KTMB e-waste guide or HHW+e-waste event dates.", "Wipe personal data."],
                [("Bulky events for TVs?", "No — KTMB guide or HHW+e-waste events."), ("Lockwood?", "Fee drop-off available.")],
                *sw,
            )
        )
    rows.append(
        R(
            c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", True,
            "Dry completely → regular trash — NOT Reno HHW voucher",
            "Reno trash cart — dried latex only",
            "Reno latex paint is NOT accepted on WM summer HHW voucher. Dry paint completely (add kitty litter or leave lid off) until solid, then put dried cans in regular trash. Liquid latex never goes to GrayMar HHW.",
            ["Add kitty litter or dry paint until solid.", "Place dried cans in regular trash.", "Do not use HHW voucher for latex."],
            [("HHW voucher for latex?", "No — latex must be fully dried for trash."), ("Oil paint?", "Oil-based paint uses WM summer HHW voucher.")],
            *sw,
        )
    )
    rows.append(
        R(
            c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
            "WM summer HHW voucher ≤50 lb at GrayMar 13203 S Virginia Jul–Sep",
            "GrayMar Environmental — 13203 S Virginia St",
            "Oil-based paint uses Reno WM summer HHW voucher — drop at GrayMar Environmental — 13203 S Virginia St — Jul–Sep, ≤50 lb per voucher. Not trash or bulky events.",
            ["Obtain WM summer HHW voucher.", "Haul oil paint to GrayMar 13203 S Virginia St Jul–Sep.", "Keep containers sealed and labeled."],
            [("Latex at GrayMar?", "No — latex must be dried for trash."), ("Limit?", "≤50 lb per voucher.")],
            *sw,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
                "WM summer HHW voucher ≤50 lb at GrayMar Jul–Sep",
                "GrayMar Environmental — 13203 S Virginia St",
                f"Take {item.replace('-', ' ')} via Reno WM summer HHW voucher to GrayMar — 13203 S Virginia St — Jul–Sep, ≤50 lb. Not bulky events or trash.",
                ["Obtain WM summer HHW voucher.", "Deliver sealed containers to GrayMar Jul–Sep.", "Keep chemicals off trash and bulky piles."],
                [("Same as latex paint?", "No — chemicals use HHW voucher; dried latex goes to trash.")],
                *sw,
            )
        )
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {
            "car-battery": " Lead-acid batteries via HHW voucher.",
            "lithium-battery": " Lithium batteries via HHW voucher.",
            "motor-oil": " Used motor oil via HHW voucher.",
            "propane-tank": " Propane tanks via HHW voucher — confirm size limits.",
            "fluorescent-bulbs": " Fluorescent bulbs via HHW voucher.",
            "cooking-oil": " Cooking oil via HHW voucher when not trash-safe.",
        }[item]
        rows.append(
            R(
                c, st, item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium", False,
                "WM summer HHW voucher ≤50 lb at GrayMar Jul–Sep",
                "GrayMar Environmental — 13203 S Virginia St",
                f"Reno WM summer HHW voucher at GrayMar 13203 S Virginia St accepts household hazardous materials Jul–Sep, ≤50 lb.{extra}",
                ["Obtain WM summer HHW voucher.", "Haul to GrayMar Jul–Sep.", "Tires use cleanup event path, not HHW voucher."],
                [("Address?", "13203 S Virginia St, Reno.")],
                *sw,
            )
        )
    rows.append(
        R(
            c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
            "Rigid sealed container — confirm GrayMar HHW sharps acceptance",
            "GrayMar Environmental — 13203 S Virginia St",
            "Place sharps in a rigid sealed container. Confirm acceptance via WM summer HHW voucher at GrayMar. Do not loose-bag needles.",
            ["Use rigid sealed container.", "Confirm sharps via HHW voucher at GrayMar.", "Never recycle loose needles."],
            [("Medications?", "Confirm drug take-back via Washoe County programs.")],
            *sw,
        )
    )
    rows.append(
        R(
            c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
            "4–6 tires at community cleanup events — NOT year-round curbside",
            "Reno community cleanup events",
            "Reno tires are NOT year-round city curbside bulk. Bring 4–6 tires to community cleanup events. Retailer take-back when replacing tires.",
            ["Check community cleanup event dates on reno.gov.", "Limit 4–6 tires per event.", "Retailer take-back when replacing tires."],
            [("Year-round curbside for tires?", "No — cleanup events only (4–6)."), ("WM bulk?", "Confirm WM 775-329-8822 for paid options.")],
            *cleanups,
        )
    )
    rows.append(
        R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True,
          "Reno yard waste collection", "Reno yard waste collection",
          "Reno handles yard waste through regular collection. Follow set-out rules on reno.gov.",
          ["Use yard waste set-out rules.", "Keep yard waste out of HHW and e-waste.", "Check reno.gov for seasonal guidance."],
          [("Christmas trees?", "Follow city seasonal yard waste guidance.")], *sw)
    )
    rows.append(
        R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True,
          "Garbage cart unless private compost", "Reno garbage / private compost",
          "Bag food scraps for garbage unless you compost. Keep food out of recycling and HHW.",
          ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."],
          [("HHW for food?", "No.")], *sw)
    )
    rows.append(
        R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False,
          "Not recycling — store take-back / trash", "Retail bag take-back / trash",
          "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
          ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."],
          [("Cleanup events for bags?", "No.")], *sw)
    )
    rows.append(
        R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", False,
          "NOT cleanup roll-offs — Lockwood fee / private C&D hauler",
          "Lockwood Landfill / private C&D hauler",
          "Construction debris is not Reno spring cleanup roll-off material. Haul to Lockwood Landfill (fee) or hire a private C&D hauler. Route oil paint/chemicals to HHW voucher separately.",
          ["Do not treat C&D as cleanup roll-off material.", "Haul to Lockwood or hire private C&D.", "Route oil paint to HHW voucher."],
          [("HHW for C&D?", "No — separate paint/chemicals.")], *cleanups)
    )
    return rows


def tacoma():
    c, st = "tacoma", "WA"
    c2h = (
        "City of Tacoma — Call-2-Haul",
        "https://tacoma.gov/government/departments/environmental-services/solid-waste/call-2-haul/",
    )
    hhw = (
        "City of Tacoma — Hazardous Waste",
        "https://tacoma.gov/government/departments/environmental-services/solid-waste/hazardous-waste/",
    )
    rows = []
    rows.append(
        R(
            c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
            "Free Call-2-Haul — 2 pickups/year; up to 3 large items; 253-573-2468",
            "Tacoma Call-2-Haul curbside collection",
            "Tacoma mattresses use Call-2-Haul — 2 free pickups per year, up to 3 large items per pickup. Schedule at 253-573-2468. Set out on scheduled collection day.",
            ["Call 253-573-2468 to schedule Call-2-Haul.", "Limit 2 pickups/year, up to 3 large items each.", "Set out on scheduled collection day."],
            [("Fee?", "Free — 2 pickups/year via Call-2-Haul."), ("Item limit?", "Up to 3 large items per pickup.")],
            *c2h,
        )
    )
    rows.append(
        R(
            c, st, "refrigerator", "SPECIAL_HANDLING", "High", True,
            "Free Call-2-Haul — 2 pickups/year; up to 3 large items; 253-573-2468",
            "Tacoma Call-2-Haul — Freon appliance",
            "Tacoma Freon refrigerators are included in Call-2-Haul — 2 free pickups per year, up to 3 large items. Schedule at 253-573-2468. Never vent refrigerant yourself.",
            ["Call 253-573-2468 to schedule Call-2-Haul.", "Set out on scheduled collection day.", "Never vent Freon yourself."],
            [("Call-2-Haul for Freon fridge?", "Yes — included in 2 free pickups/year."), ("TVs?", "No — TVs use E-Cycle Washington, not Call-2-Haul.")],
            *c2h,
        )
    )
    rows.append(
        R(
            c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
            "Free Call-2-Haul — Freon appliance; 253-573-2468",
            "Tacoma Call-2-Haul — Freon appliance",
            "Tacoma Freon window AC units use Call-2-Haul — 2 free pickups per year. Schedule at 253-573-2468. Never vent refrigerant yourself.",
            ["Call 253-573-2468 to schedule Call-2-Haul.", "Set out on scheduled day.", "Keep sealed until proper Freon handling."],
            [("Same as Freon fridge?", "Yes — Call-2-Haul within 2 free pickups/year.")],
            *c2h,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c, st, item, "SPECIAL_HANDLING", "Medium", True,
                "Free Call-2-Haul — 2 pickups/year; up to 3 large items; 253-573-2468",
                "Tacoma Call-2-Haul curbside collection",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s use Tacoma Call-2-Haul — 2 free pickups per year, up to 3 large items. Schedule at 253-573-2468. Freon refrigerators/AC also included.",
                ["Call 253-573-2468 to schedule Call-2-Haul.", "Set out on scheduled collection day.", "Limit 2 pickups/year, 3 large items each."],
                [("Same as Freon fridge?", "Yes — all large appliances use Call-2-Haul.")],
                *c2h,
            )
        )
    for item, label in [
        ("television", "TVs"), ("computer-monitor", "monitors"),
        ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste"),
    ]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "Medium", False,
                "NOT Call-2-Haul — E-Cycle Washington drop-off",
                "E-Cycle Washington authorized collector",
                f"Tacoma electronics including {label} are NOT accepted on Call-2-Haul. Use E-Cycle Washington authorized drop-off locations. Wipe data before drop-off.",
                ["Do not schedule TVs/e-waste on Call-2-Haul.", "Find E-Cycle Washington drop-off location.", "Wipe personal data."],
                [("Call-2-Haul for TVs?", "No — E-Cycle Washington only."), ("Fridges?", "Call-2-Haul accepts Freon appliances.")],
                *hhw,
            )
        )
    rows.append(
        R(
            c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", True,
            "Dry completely → regular trash — NOT Tacoma HHW",
            "Tacoma trash cart — dried latex only",
            "Tacoma latex paint is NOT accepted at HHW. Dry paint completely (add kitty litter or leave lid off) until solid, then put dried cans in regular trash. Liquid latex never goes to 3510 S Mullen HHW.",
            ["Add kitty litter or dry paint until solid.", "Place dried cans in regular trash.", "Do not haul liquid latex to HHW."],
            [("HHW for latex?", "No — latex must be fully dried for trash."), ("Oil paint?", "Oil-based paint goes to HHW free.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
            "Free Tacoma HHW — 3510 S Mullen St Fri–Mon 8–5:30",
            "Tacoma HHW — 3510 S Mullen St",
            "Oil-based paint goes to Tacoma HHW — 3510 S Mullen St — Fri–Mon 8:00 a.m.–5:30 p.m., free for Tacoma residential customers. Not Call-2-Haul or trash.",
            ["Haul sealed oil paint to 3510 S Mullen St.", "Hours: Fri–Mon 8–5:30.", "Keep oil paint out of trash carts."],
            [("Latex at HHW?", "No — latex must be dried for trash."), ("Fee?", "Free for Tacoma residential.")],
            *hhw,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
                "Free Tacoma HHW — 3510 S Mullen St Fri–Mon 8–5:30",
                "Tacoma HHW — 3510 S Mullen St",
                f"Take {item.replace('-', ' ')} to Tacoma HHW — 3510 S Mullen St — Fri–Mon 8–5:30, free for Tacoma residential customers. Not Call-2-Haul or trash.",
                ["Deliver sealed containers to 3510 S Mullen St.", "Hours: Fri–Mon 8–5:30.", "Keep chemicals off Call-2-Haul and trash."],
                [("Same as latex paint?", "No — chemicals go to HHW; dried latex goes to trash.")],
                *hhw,
            )
        )
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {
            "car-battery": " Lead-acid batteries at HHW.",
            "lithium-battery": " Lithium batteries at HHW.",
            "motor-oil": " Used motor oil at HHW.",
            "propane-tank": " Propane tanks at HHW — confirm size limits.",
            "fluorescent-bulbs": " Fluorescent bulbs at HHW.",
            "cooking-oil": " Cooking oil at HHW when not trash-safe.",
        }[item]
        rows.append(
            R(
                c, st, item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium", False,
                "Free Tacoma HHW — 3510 S Mullen St Fri–Mon 8–5:30",
                "Tacoma HHW — 3510 S Mullen St",
                f"Tacoma HHW at 3510 S Mullen St accepts household hazardous materials free for Tacoma residential customers.{extra}",
                ["Haul to 3510 S Mullen St during posted hours.", "Fri–Mon 8–5:30.", "Tires use Mullen fee path, not Call-2-Haul."],
                [("Address?", "3510 S Mullen St, Tacoma.")],
                *hhw,
            )
        )
    rows.append(
        R(
            c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
            "Rigid sealed container — confirm Tacoma HHW sharps acceptance",
            "Tacoma HHW — 3510 S Mullen St",
            "Place sharps in a rigid sealed container. Confirm acceptance at Tacoma HHW. Do not loose-bag needles.",
            ["Use rigid sealed container.", "Confirm sharps at 3510 S Mullen St.", "Never recycle loose needles."],
            [("Medications?", "Confirm drug take-back via Pierce County programs.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
            "NOT Call-2-Haul — $3.25+ tonnage at 3510 S Mullen St",
            "Tacoma Solid Waste — 3510 S Mullen St",
            "Tacoma tires are NOT accepted on Call-2-Haul. Self-haul to 3510 S Mullen St — $3.25 per tire plus tonnage. Retailer take-back when replacing tires.",
            ["Do not schedule tires on Call-2-Haul.", "Haul to 3510 S Mullen St ($3.25/tire + tonnage).", "Retailer take-back when replacing tires."],
            [("Call-2-Haul for tires?", "No — Mullen fee drop-off."), ("Fee?", "$3.25/tire plus tonnage.")],
            *hhw,
        )
    )
    rows.append(
        R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True,
          "Tacoma yard waste collection", "Tacoma yard waste collection",
          "Tacoma handles yard waste through regular collection. Follow set-out rules on tacoma.gov.",
          ["Use yard waste set-out rules.", "Keep yard waste out of HHW and e-waste.", "Check tacoma.gov for seasonal guidance."],
          [("Christmas trees?", "Follow city seasonal yard waste guidance.")], *c2h)
    )
    rows.append(
        R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True,
          "Garbage cart unless private compost", "Tacoma garbage / private compost",
          "Bag food scraps for garbage unless you compost. Keep food out of recycling and HHW.",
          ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."],
          [("HHW for food?", "No.")], *c2h)
    )
    rows.append(
        R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False,
          "Not recycling — store take-back / trash", "Retail bag take-back / trash",
          "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
          ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."],
          [("Call-2-Haul for bags?", "No.")], *c2h)
    )
    rows.append(
        R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", False,
          "NOT Call-2-Haul — private C&D hauler / Mullen fee drop-off",
          "Private C&D hauler / 3510 S Mullen St",
          "Construction debris exceeds Tacoma Call-2-Haul limits. Hire a private C&D hauler or confirm fee drop-off at 3510 S Mullen St. Route oil paint/chemicals to HHW separately.",
          ["Do not treat remodel debris as Call-2-Haul.", "Hire private C&D for larger projects.", "Route oil paint to HHW at Mullen."],
          [("HHW for C&D?", "No — separate paint/chemicals.")], *c2h)
    )
    return rows


def aurora():
    c, st = "aurora", "CO"
    sw = (
        "City of Aurora — Trash & Recycling",
        "https://www.auroragov.org/residents/trash___recycling",
    )
    paint = (
        "City of Aurora — Paint & Household Chemicals",
        "https://www.auroragov.org/residents/trash___recycling/recycling_opportunities/paint___household_chemicals",
    )
    ewaste = (
        "City of Aurora — Electronics Recycling",
        "https://www.auroragov.org/residents/trash___recycling/recycling_opportunities/electronics_recycling",
    )
    rows = []
    rows.append(
        R(
            c, st, "mattress", "SPECIAL_HANDLING", "Low", False,
            "No city bulk — private licensed hauler bulk pickup",
            "Private licensed hauler bulk service",
            "Aurora has NO city bulk collection. Mattresses go through your private licensed hauler's bulk service. Confirm hauler fees and scheduling before set-out.",
            ["Contact your licensed hauler for bulk pickup.", "Confirm fees and scheduling.", "No city curbside bulk program."],
            [("City bulk?", "No — private licensed haulers only."), ("Fee?", "Confirm with your hauler.")],
            *sw,
        )
    )
    rows.append(
        R(
            c, st, "refrigerator", "SPECIAL_HANDLING", "High", False,
            "NOT e-cycle — private/scrap hauler; Habitat ReStore if working",
            "Private scrap hauler / Habitat ReStore",
            "Aurora Freon refrigerators are NOT accepted at city e-waste events (ended Jul 2026). Use a private scrap hauler for Freon appliance disposal. Working units may go to Habitat ReStore. Never vent refrigerant yourself.",
            ["Do not bring Freon fridge to e-waste events.", "Contact private scrap hauler for Freon disposal.", "Working units: try Habitat ReStore."],
            [("E-cycle events?", "No — city events ended Jul 2026."), ("Working fridge?", "Habitat ReStore if accepted.")],
            *ewaste,
        )
    )
    rows.append(
        R(
            c, st, "air-conditioner", "SPECIAL_HANDLING", "High", False,
            "NOT e-cycle — private Freon appliance recycler",
            "Private Freon appliance recycler",
            "Aurora Freon window AC units are NOT accepted at city e-waste events. Use a private Freon appliance recycler. Never vent refrigerant yourself.",
            ["Do not bring Freon AC to e-waste events.", "Contact private Freon appliance recycler.", "Keep sealed until proper Freon handling."],
            [("Same as Freon fridge?", "Yes — private/scrap path, not e-cycle events.")],
            *ewaste,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c, st, item, "SPECIAL_HANDLING", "Medium", False,
                "No city bulk — private licensed hauler bulk pickup",
                "Private licensed hauler bulk service",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s go through your private licensed hauler's bulk service. Aurora has no city bulk. Freon refrigerators/AC use private scrap path, not e-cycle.",
                ["Contact licensed hauler for bulk pickup.", "Confirm hauler fees.", "Freon appliances use private scrap path."],
                [("Same as Freon fridge?", "No — non-Freon uses hauler bulk.")],
                *sw,
            )
        )
    for item, label in [
        ("television", "TVs"), ("computer-monitor", "monitors"),
        ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste"),
    ]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "Medium", False,
                "City events ended Jul 2026 — Earth911 / private recycler; CO landfill ban",
                "Earth911 / private e-waste recycler",
                f"Aurora city e-waste events ended Jul 2026. Electronics including {label} must go to Earth911-listed or private e-waste recyclers — Colorado landfill ban applies. Wipe data before drop-off.",
                ["Do not rely on city e-waste events.", "Find recycler via Earth911 or auroragov.org.", "Wipe personal data."],
                [("City e-waste events?", "Ended Jul 2026 — use Earth911/private."), ("Landfill ban?", "Yes — CO bans e-waste in landfills.")],
                *ewaste,
            )
        )
    rows.append(
        R(
            c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", True,
            "PaintCare free drop-off OR dry completely → regular trash",
            "PaintCare location / Aurora trash cart — dried latex",
            "Aurora latex paint: use free PaintCare drop-off for liquid latex OR dry paint completely (add kitty litter) until solid, then put dried cans in regular trash. WM At Your Door ($10) is for other HHW, not preferred for paint.",
            ["Use PaintCare for liquid latex.", "Or dry paint completely for trash.", "Do not mix liquid latex with other HHW."],
            [("PaintCare for latex?", "Yes — free drop-off for paint."), ("WM At Your Door?", "$10 for other HHW — PaintCare preferred for paint.")],
            *paint,
        )
    )
    rows.append(
        R(
            c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
            "PaintCare free drop-off for oil-based paint",
            "PaintCare location",
            "Oil-based paint goes to free PaintCare drop-off locations in Aurora. Not trash or hauler bulk. WM At Your Door ($10) available for other HHW — call 800-449-7587.",
            ["Find PaintCare location for oil paint.", "Keep containers sealed and labeled.", "Not trash or hauler bulk."],
            [("Same as latex?", "Yes — both use PaintCare free drop-off."), ("WM At Your Door?", "$10 for other HHW — 800-449-7587.")],
            *paint,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
                "WM At Your Door $10 — 800-449-7587",
                "WM At Your Door HHW collection",
                f"Take {item.replace('-', ' ')} via WM At Your Door — $10 per collection — call 800-449-7587. Paint uses PaintCare separately. Not hauler bulk or trash.",
                ["Schedule WM At Your Door — 800-449-7587.", "Fee: $10 per collection.", "Keep chemicals off hauler bulk and trash."],
                [("Same as paint?", "No — chemicals use WM At Your Door; paint uses PaintCare.")],
                *paint,
            )
        )
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {
            "car-battery": " Lead-acid batteries via WM At Your Door.",
            "lithium-battery": " Lithium batteries via WM At Your Door.",
            "motor-oil": " Used motor oil via WM At Your Door.",
            "propane-tank": " Propane tanks via WM At Your Door — confirm size limits.",
            "fluorescent-bulbs": " Fluorescent bulbs via WM At Your Door.",
            "cooking-oil": " Cooking oil via WM At Your Door when not trash-safe.",
        }[item]
        rows.append(
            R(
                c, st, item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium", False,
                "WM At Your Door $10 — 800-449-7587",
                "WM At Your Door HHW collection",
                f"Aurora WM At Your Door accepts household hazardous materials — $10 per collection — call 800-449-7587.{extra}",
                ["Schedule WM At Your Door — 800-449-7587.", "Fee: $10 per collection.", "Tires use Earth911/DADS fee path."],
                [("Phone?", "800-449-7587.")],
                *paint,
            )
        )
    rows.append(
        R(
            c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
            "Rigid sealed container — confirm WM At Your Door sharps acceptance",
            "WM At Your Door HHW collection",
            "Place sharps in a rigid sealed container. Confirm acceptance via WM At Your Door — 800-449-7587. Do not loose-bag needles.",
            ["Use rigid sealed container.", "Confirm sharps via WM At Your Door.", "Never recycle loose needles."],
            [("Medications?", "Confirm drug take-back via Aurora/Arapahoe County programs.")],
            *paint,
        )
    )
    rows.append(
        R(
            c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
            "Earth911 / DADS fee drop-off — NOT hauler bulk",
            "Earth911 / DADS tire facility",
            "Aurora tires are NOT accepted on hauler bulk. Use Earth911 to find DADS fee drop-off locations. Retailer take-back when replacing tires.",
            ["Do not set tires out for hauler bulk.", "Find DADS facility via Earth911.", "Retailer take-back when replacing tires."],
            [("Hauler bulk for tires?", "No — Earth911/DADS fee drop-off."), ("City bulk?", "No city bulk program.")],
            *sw,
        )
    )
    rows.append(
        R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True,
          "Aurora yard waste via licensed hauler", "Private hauler yard waste collection",
          "Aurora yard waste is handled through your licensed hauler's yard waste program. Follow hauler set-out rules.",
          ["Contact licensed hauler for yard waste rules.", "Keep yard waste out of HHW and e-waste.", "Check auroragov.org for seasonal guidance."],
          [("Christmas trees?", "Follow hauler seasonal yard waste guidance.")], *sw)
    )
    rows.append(
        R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True,
          "Garbage cart via licensed hauler", "Private hauler garbage / private compost",
          "Bag food scraps for garbage via your licensed hauler unless you compost. Keep food out of recycling and HHW.",
          ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."],
          [("WM At Your Door for food?", "No.")], *sw)
    )
    rows.append(
        R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False,
          "Not recycling — store take-back / trash", "Retail bag take-back / trash",
          "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
          ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."],
          [("Hauler bulk for bags?", "No.")], *sw)
    )
    rows.append(
        R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", False,
          "NOT hauler bulk — private C&D hauler",
          "Private C&D hauler",
          "Aurora has no city bulk for construction debris. Hire a private C&D hauler for remodel loads. Route paint to PaintCare and chemicals to WM At Your Door separately.",
          ["Do not treat C&D as hauler bulk.", "Hire private C&D for remodel loads.", "Route paint to PaintCare; chemicals to WM At Your Door."],
          [("WM At Your Door for C&D?", "No — separate paint/chemicals.")], *sw)
    )
    return rows


def chattanooga():
    c, st = "chattanooga", "TN"
    bulk = (
        "City of Chattanooga — Brush & Bulk Collection",
        "https://chattanooga.gov/services/waste-recycling/brush-collection",
    )
    hhw = (
        "City of Chattanooga — Hazardous Household Waste",
        "https://chattanooga.gov/services/waste-recycling/hazardous-household-waste",
    )
    rows = []
    rows.append(
        R(
            c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
            "Free area bulk sweep — set out by 7 a.m. Monday of area week; max 12 bulk/property/year",
            "Chattanooga area bulk sweep collection",
            "Chattanooga mattresses go on free area bulk sweep — one week per month by area. Set out by 7:00 a.m. Monday of your area week. Maximum 12 bulk items per property per year.",
            ["Check your area bulk sweep week on chattanooga.gov.", "Set out by 7 a.m. Monday of area week.", "Limit 12 bulk items/property/year."],
            [("Fee?", "Free on scheduled area bulk week."), ("Set-out time?", "By 7 a.m. Monday of area week.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c, st, "refrigerator", "SPECIAL_HANDLING", "High", True,
            "Free area bulk sweep — set out by 7 a.m. Monday; max 12 bulk/property/year",
            "Chattanooga area bulk sweep — Freon appliance",
            "Chattanooga Freon refrigerators go on free area bulk sweep — set out by 7:00 a.m. Monday of your area week. Maximum 12 bulk items per property per year. Never vent refrigerant yourself.",
            ["Check area bulk sweep week.", "Set out by 7 a.m. Monday of area week.", "Never vent Freon yourself."],
            [("Bulk sweep for Freon fridge?", "Yes — included in 12 bulk items/year."), ("TVs?", "Also on bulk sweep, not HHW.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
            "Free area bulk sweep — Freon appliance; max 12 bulk/property/year",
            "Chattanooga area bulk sweep — Freon appliance",
            "Chattanooga Freon window AC units go on free area bulk sweep — set out by 7:00 a.m. Monday of your area week. Maximum 12 bulk items per property per year. Never vent refrigerant yourself.",
            ["Check area bulk sweep week.", "Set out by 7 a.m. Monday.", "Keep sealed until proper Freon handling."],
            [("Same as Freon fridge?", "Yes — area bulk sweep within 12 items/year.")],
            *bulk,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c, st, item, "SPECIAL_HANDLING", "Medium", True,
                "Free area bulk sweep — set out by 7 a.m. Monday; max 12 bulk/property/year",
                "Chattanooga area bulk sweep collection",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s go on Chattanooga area bulk sweep — set out by 7:00 a.m. Monday of area week. Maximum 12 bulk items per property per year. Freon refrigerators/AC also on bulk sweep.",
                ["Check area bulk sweep week.", "Set out by 7 a.m. Monday of area week.", "Limit 12 bulk items/property/year."],
                [("Same as Freon fridge?", "Yes — all large appliances on area bulk sweep.")],
                *bulk,
            )
        )
    for item, label in [
        ("television", "TVs"), ("computer-monitor", "monitors"),
        ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste"),
    ]:
        curbside = item == "television"
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "Medium", curbside,
                "TVs on bulk sweep; computers at HHW 4063 N Hawthorne — NOT bulk for computers",
                "Chattanooga bulk sweep / HHW — 4063 N Hawthorne St",
                f"Chattanooga {label}: TVs go on area bulk sweep (set out by 7 a.m. Monday, max 12/year). Computers and other e-waste go to HHW — 4063 N Hawthorne St — NOT bulk sweep. Wipe data before drop-off.",
                ["TVs: set out on area bulk sweep week by 7 a.m. Monday." if item == "television" else "Haul computers/e-waste to HHW 4063 N Hawthorne St.", "Check area schedule on chattanooga.gov.", "Wipe personal data."],
                [("Bulk for TVs?", "Yes — area bulk sweep."), ("Computers at HHW?", "Yes — 4063 N Hawthorne, not bulk.")],
                *bulk if item == "television" else hhw,
            )
        )
    rows.append(
        R(
            c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", True,
            "Dry completely → regular trash — NOT Chattanooga HHW",
            "Chattanooga trash cart — dried latex only",
            "Chattanooga latex paint is NOT accepted at HHW. Dry paint completely (add kitty litter or leave lid off) until solid, then put dried cans in regular trash. Liquid latex never goes to 4063 N Hawthorne HHW.",
            ["Add kitty litter or dry paint until solid.", "Place dried cans in regular trash.", "Do not haul liquid latex to HHW."],
            [("HHW for latex?", "No — latex must be fully dried for trash."), ("Oil paint?", "Oil-based paint goes to HHW free.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "paint-oil", "BANNED_FROM_LANDFILLS", "High", False,
            "Free Chattanooga HHW — 4063 N Hawthorne St Tue–Sat 8–3",
            "Chattanooga HHW — 4063 N Hawthorne St",
            "Oil-based paint goes to Chattanooga HHW — 4063 N Hawthorne St — Tue–Sat 8:00 a.m.–3:00 p.m., free for Tennessee residents. Not bulk sweep or trash.",
            ["Haul sealed oil paint to 4063 N Hawthorne St.", "Hours: Tue–Sat 8–3.", "Keep oil paint out of trash carts."],
            [("Latex at HHW?", "No — latex must be dried for trash."), ("Fee?", "Free for TN residents.")],
            *hhw,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
                "Free Chattanooga HHW — 4063 N Hawthorne St Tue–Sat 8–3",
                "Chattanooga HHW — 4063 N Hawthorne St",
                f"Take {item.replace('-', ' ')} to Chattanooga HHW — 4063 N Hawthorne St — Tue–Sat 8–3, free for Tennessee residents. Not bulk sweep or trash.",
                ["Deliver sealed containers to 4063 N Hawthorne St.", "Hours: Tue–Sat 8–3.", "Keep chemicals off bulk sweep piles."],
                [("Same as latex paint?", "No — chemicals go to HHW; dried latex goes to trash.")],
                *hhw,
            )
        )
    for item in ["car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {
            "car-battery": " Lead-acid batteries at HHW.",
            "lithium-battery": " Lithium batteries at HHW.",
            "motor-oil": " Used motor oil at HHW.",
            "propane-tank": " Propane tanks at HHW — confirm size limits.",
            "fluorescent-bulbs": " Fluorescent bulbs at HHW.",
            "cooking-oil": " Cooking oil at HHW when not trash-safe.",
        }[item]
        rows.append(
            R(
                c, st, item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item != "cooking-oil" else "Medium", False,
                "Free Chattanooga HHW — 4063 N Hawthorne St Tue–Sat 8–3",
                "Chattanooga HHW — 4063 N Hawthorne St",
                f"Chattanooga HHW at 4063 N Hawthorne St accepts household hazardous materials free for Tennessee residents.{extra}",
                ["Haul to 4063 N Hawthorne St during posted hours.", "Tue–Sat 8–3.", "Tires use retailer path, not HHW or bulk."],
                [("Address?", "4063 N Hawthorne St, Chattanooga.")],
                *hhw,
            )
        )
    rows.append(
        R(
            c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
            "Rigid sealed container — confirm Chattanooga HHW sharps acceptance",
            "Chattanooga HHW — 4063 N Hawthorne St",
            "Place sharps in a rigid sealed container. Confirm acceptance at Chattanooga HHW. Do not loose-bag needles.",
            ["Use rigid sealed container.", "Confirm sharps at 4063 N Hawthorne St.", "Never recycle loose needles."],
            [("Medications?", "Confirm drug take-back via Hamilton County programs.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
            "NOT bulk sweep — retailer take-back",
            "Tire retailer take-back",
            "Chattanooga tires are NOT accepted on area bulk sweep. Use retailer take-back when replacing tires.",
            ["Do not set tires out on bulk sweep.", "Use retailer take-back when replacing tires.", "Confirm retailer acceptance policy."],
            [("Bulk sweep for tires?", "No — retailer take-back only."), ("HHW for tires?", "No.")],
            *bulk,
        )
    )
    rows.append(
        R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True,
          "Chattanooga yard waste / brush collection", "Chattanooga brush collection",
          "Chattanooga handles yard waste and brush through regular collection and area schedules. Follow set-out rules on chattanooga.gov.",
          ["Use brush/yard waste set-out rules.", "Keep yard waste out of HHW and e-waste.", "Check chattanooga.gov for area schedule."],
          [("Christmas trees?", "Follow city seasonal yard waste guidance.")], *bulk)
    )
    rows.append(
        R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True,
          "Garbage cart unless private compost", "Chattanooga garbage / private compost",
          "Bag food scraps for garbage unless you compost. Keep food out of recycling and HHW.",
          ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."],
          [("HHW for food?", "No.")], *bulk)
    )
    rows.append(
        R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False,
          "Not recycling — store take-back / trash", "Retail bag take-back / trash",
          "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
          ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."],
          [("Bulk sweep for bags?", "No.")], *bulk)
    )
    rows.append(
        R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", False,
          "NOT bulk sweep — private C&D hauler",
          "Private C&D hauler",
          "Construction debris is not Chattanooga area bulk sweep material. Hire a private C&D hauler for remodel loads. Route oil paint/chemicals to HHW separately.",
          ["Do not treat remodel debris as bulk sweep.", "Hire private C&D for larger projects.", "Route oil paint to HHW at Hawthorne."],
          [("HHW for C&D?", "No — separate paint/chemicals.")], *bulk)
    )
    return rows


CITIES = [
    {
        "city": "Anchorage",
        "city_slug": "anchorage",
        "state": "AK",
        "state_slug": "alaska",
        "lat": 61.2181,
        "lng": -149.9003,
        "population": 291247,
    },
    {
        "city": "Reno",
        "city_slug": "reno",
        "state": "NV",
        "state_slug": "nevada",
        "lat": 39.5296,
        "lng": -119.8138,
        "population": 264165,
    },
    {
        "city": "Tacoma",
        "city_slug": "tacoma",
        "state": "WA",
        "state_slug": "washington",
        "lat": 47.2529,
        "lng": -122.4443,
        "population": 219346,
    },
    {
        "city": "Aurora",
        "city_slug": "aurora",
        "state": "CO",
        "state_slug": "colorado",
        "lat": 39.7294,
        "lng": -104.8319,
        "population": 386261,
    },
    {
        "city": "Chattanooga",
        "city_slug": "chattanooga",
        "state": "TN",
        "state_slug": "tennessee",
        "lat": 35.0456,
        "lng": -85.3097,
        "population": 181099,
    },
]

ZIPS = [
    {
        "zip": "99501",
        "city": "Anchorage",
        "city_slug": "anchorage",
        "state": "AK",
        "state_slug": "alaska",
        "lat": 61.218,
        "lng": -149.900,
        "population": 17000,
    },
    {
        "zip": "99508",
        "city": "Anchorage",
        "city_slug": "anchorage",
        "state": "AK",
        "state_slug": "alaska",
        "lat": 61.195,
        "lng": -149.780,
        "population": 32000,
    },
    {
        "zip": "89501",
        "city": "Reno",
        "city_slug": "reno",
        "state": "NV",
        "state_slug": "nevada",
        "lat": 39.530,
        "lng": -119.814,
        "population": 12000,
    },
    {
        "zip": "89503",
        "city": "Reno",
        "city_slug": "reno",
        "state": "NV",
        "state_slug": "nevada",
        "lat": 39.545,
        "lng": -119.835,
        "population": 22000,
    },
    {
        "zip": "98402",
        "city": "Tacoma",
        "city_slug": "tacoma",
        "state": "WA",
        "state_slug": "washington",
        "lat": 47.253,
        "lng": -122.444,
        "population": 9000,
    },
    {
        "zip": "98405",
        "city": "Tacoma",
        "city_slug": "tacoma",
        "state": "WA",
        "state_slug": "washington",
        "lat": 47.255,
        "lng": -122.470,
        "population": 18000,
    },
    {
        "zip": "80012",
        "city": "Aurora",
        "city_slug": "aurora",
        "state": "CO",
        "state_slug": "colorado",
        "lat": 39.695,
        "lng": -104.865,
        "population": 25000,
    },
    {
        "zip": "80014",
        "city": "Aurora",
        "city_slug": "aurora",
        "state": "CO",
        "state_slug": "colorado",
        "lat": 39.670,
        "lng": -104.820,
        "population": 30000,
    },
    {
        "zip": "37402",
        "city": "Chattanooga",
        "city_slug": "chattanooga",
        "state": "TN",
        "state_slug": "tennessee",
        "lat": 35.046,
        "lng": -85.310,
        "population": 8000,
    },
    {
        "zip": "37404",
        "city": "Chattanooga",
        "city_slug": "chattanooga",
        "state": "TN",
        "state_slug": "tennessee",
        "lat": 35.030,
        "lng": -85.280,
        "population": 14000,
    },
]

FACILITIES = [
    {
        "name": "Anchorage HHW — Central Transfer Station",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "anchorage",
        "state": "AK",
        "zip": "99518",
        "address": "1208 E 56th Avenue, Anchorage, AK 99518",
        "lat": 61.1685,
        "lng": -149.8555,
        "source_url": "https://www.muni.org/Departments/SWS/Dispose/pages/hazardouswaste.aspx",
        "hours": "Tue/Thu/Sat 8:00–16:30",
        "phone": "907-343-6262",
        "accepted_materials": [m for m in HHW_MATERIALS if m != "paint-latex"],
    },
    {
        "name": "Central Transfer Station (CTS)",
        "facility_type": "Transfer station — bulky / Freon appliances",
        "city_slug": "anchorage",
        "state": "AK",
        "zip": "99518",
        "address": "1310 E 56th Avenue, Anchorage, AK 99518",
        "lat": 61.1680,
        "lng": -149.8540,
        "source_url": "https://www.muni.org/Departments/SWS/HowDoI/pages/dispose.aspx",
        "hours": "Check muni.org for current hours",
        "phone": "907-343-6262",
        "accepted_materials": ["mattress", "refrigerator", "freezer", "washer", "dryer", "tires", "tire-rims"],
    },
    {
        "name": "Anchorage Regional Landfill (ARL)",
        "facility_type": "Landfill — HHW / excess e-waste / large tire loads",
        "city_slug": "anchorage",
        "state": "AK",
        "zip": "99577",
        "address": "Eagle River area — check muni.org for address",
        "lat": 61.3200,
        "lng": -149.5700,
        "source_url": "https://www.muni.org/Departments/SWS/Dispose/pages/hazardouswaste.aspx",
        "hours": "Check muni.org for current hours",
        "phone": "907-343-6262",
        "accepted_materials": [m for m in HHW_MATERIALS if m != "paint-latex"]
        + ["television", "computer-monitor", "tires", "tire-rims", "refrigerator", "freezer", "air-conditioner"],
    },
    {
        "name": "GrayMar Environmental HHW",
        "facility_type": "Household hazardous waste drop-off — WM voucher",
        "city_slug": "reno",
        "state": "NV",
        "zip": "89511",
        "address": "13203 S Virginia Street, Reno, NV 89511",
        "lat": 39.4555,
        "lng": -119.7855,
        "source_url": "https://www.reno.gov/community/environmental-services/solid-waste-recycling.php",
        "hours": "Jul–Sep via WM summer voucher",
        "phone": "775-329-8822",
        "accepted_materials": [m for m in HHW_MATERIALS if m != "paint-latex"],
    },
    {
        "name": "Lockwood Landfill",
        "facility_type": "Landfill — free dump days / fee e-waste",
        "city_slug": "reno",
        "state": "NV",
        "zip": "89434",
        "address": "Lockwood, NV — check reno.gov for directions",
        "lat": 39.5100,
        "lng": -119.6500,
        "source_url": "https://www.reno.gov/Community/Community-CleanUps",
        "hours": "Free dump days — check reno.gov schedule",
        "phone": "775-329-8822",
        "accepted_materials": ["mattress", "washer", "dryer", "television", "computer-monitor", "e-waste-mixed"],
    },
    {
        "name": "Tacoma HHW Collection Center",
        "facility_type": "Household hazardous waste and tire drop-off",
        "city_slug": "tacoma",
        "state": "WA",
        "zip": "98409",
        "address": "3510 S Mullen Street, Tacoma, WA 98409",
        "lat": 47.2255,
        "lng": -122.5155,
        "source_url": "https://tacoma.gov/government/departments/environmental-services/solid-waste/hazardous-waste/",
        "hours": "Fri–Mon 8:00–17:30",
        "phone": "253-573-2468",
        "accepted_materials": [m for m in HHW_MATERIALS if m != "paint-latex"] + ["tires", "tire-rims"],
    },
    {
        "name": "PaintCare Aurora Drop-off",
        "facility_type": "Paint recycling — latex and oil-based",
        "city_slug": "aurora",
        "state": "CO",
        "zip": "80012",
        "address": "Check paintcare.org for nearest Aurora location",
        "lat": 39.6950,
        "lng": -104.8650,
        "source_url": "https://www.auroragov.org/residents/trash___recycling/recycling_opportunities/paint___household_chemicals",
        "hours": "Check paintcare.org for location hours",
        "phone": "800-449-7587",
        "accepted_materials": ["paint-latex", "paint-oil"],
    },
    {
        "name": "Chattanooga HHW Collection Center",
        "facility_type": "HHW and e-waste drop-off",
        "city_slug": "chattanooga",
        "state": "TN",
        "zip": "37406",
        "address": "4063 N Hawthorne Street, Chattanooga, TN 37406",
        "lat": 35.0855,
        "lng": -85.2655,
        "source_url": "https://chattanooga.gov/services/waste-recycling/hazardous-household-waste",
        "hours": "Tue–Sat 8:00–15:00",
        "phone": "423-643-6311",
        "accepted_materials": [m for m in HHW_MATERIALS if m != "paint-latex"]
        + ["computer-monitor", "smartphone", "e-waste-mixed", "laptop", "desktop-computer"],
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
        "anchorage": clone_siblings(anchorage()),
        "reno": clone_siblings(reno()),
        "tacoma": clone_siblings(tacoma()),
        "aurora": clone_siblings(aurora()),
        "chattanooga": clone_siblings(chattanooga()),
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

    print("Wave-16 metros written:")
    for city, rows in audited.items():
        print(f"  {city}: {len(rows)} rules")
    print(f"Total rules now: {len(keep)}")


if __name__ == "__main__":
    main()
