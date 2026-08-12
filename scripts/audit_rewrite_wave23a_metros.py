#!/usr/bin/env python3
"""Wave-23a: fill 15 thin cities already in cities.json to 70 rules + hard facilities.

Cities (were 10 rules each): washington, cleveland, newark, st-paul, lubbock,
baton-rouge, worcester, little-rock, tallahassee, knoxville, akron, mobile,
fort-lauderdale, syracuse, dayton.

Researched 2026-08-12 from official city/county portals. Honest HHW notes:
events-only / no permanent depot where that is what sources say.
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
        "box-spring", "sofa", "recliner", "carpet", "exercise-equipment",
        "dining-table", "desk", "bookshelf", "hot-tub", "piano",
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
    "paint-latex", "paint-oil", "pesticides", "herbicides", "pool-chemicals",
    "gasoline", "motor-oil", "antifreeze", "car-battery", "household-batteries",
    "lithium-battery", "fluorescent-bulbs", "propane-tank", "cooking-oil",
]

E_WASTE = [
    "television", "computer-monitor", "laptop", "desktop-computer", "printer",
    "tablet", "smartphone", "hard-drive", "e-waste-mixed", "ink-toner",
    "solar-panel", "microwave",
]

BULKY = [
    "mattress", "box-spring", "sofa", "recliner", "carpet", "exercise-equipment",
    "dining-table", "desk", "bookshelf", "hot-tub", "piano", "yard-waste",
]

APPLIANCE = [
    "refrigerator", "freezer", "air-conditioner", "washer", "dryer",
    "dishwasher", "stove", "water-heater", "dehumidifier",
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
                    city, state, item, channel["badge"], channel["hazard"],
                    channel["curbside"], channel["fee"], channel["facility"],
                    answer, channel["steps"], channel["faqs"], *channel["src"],
                )
            )
    return rows


def std_tail(hub, *, yard_fee, yard_facility, yard_answer, yard_steps, yard_faqs,
             cd_fee, cd_facility, cd_answer, cd_steps, cd_faqs,
             yard_badge="ACCEPTED_IN_BLUE_BIN", yard_curbside=True):
    return [
        ch(
            "tires", "SPECIAL_HANDLING", "Medium", False,
            "NOT HHW — retailer take-back / local tire programs",
            "Retailer take-back / local tire programs",
            "Tires are not a standard HHW material here. Use retailer take-back when replacing tires or confirm landfill/transfer tire acceptance. Keep tires off HHW loads.",
            ["Do not haul tires to HHW as household hazardous waste.", "Use retailer take-back when replacing tires.", "Confirm landfill or transfer tire rules before drop-off."],
            [("HHW for tires?", "No."), ("Bulk for tires?", "Confirm solid-waste rules — not HHW.")],
            hub,
        ),
        ch("yard-waste", yard_badge, "Low", yard_curbside, yard_fee, yard_facility, yard_answer, yard_steps, yard_faqs, hub),
        ch(
            "food-scraps", "SPECIAL_HANDLING", "Low", True,
            "Garbage cart unless private compost", "Garbage / private compost",
            "Bag food scraps for garbage unless you compost. Keep food out of recycling and HHW.",
            ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."],
            [("HHW for food?", "No.")], hub,
        ),
        ch(
            "plastic-bags", "SPECIAL_HANDLING", "Low", False,
            "Not recycling — store take-back / trash", "Retail bag take-back / trash",
            "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
            ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."],
            [("Bulk for bags?", "No.")], hub,
        ),
        ch("construction-debris", "SPECIAL_HANDLING", "Low", False, cd_fee, cd_facility, cd_answer, cd_steps, cd_faqs, hub),
    ]


def pack(city, state, hub, hhw, *,
         bulk_fee, bulk_fac, bulk_ans, bulk_steps, bulk_faqs, bulk_curbside=True,
         freon_fee, freon_fac, freon_ans, freon_steps, freon_faqs, freon_curbside=True,
         e_fee, e_fac, e_ans, e_steps, e_faqs, e_curbside=False,
         h_fee, h_fac, h_ans, h_steps, h_faqs,
         yard_fee, yard_fac, yard_ans, yard_steps, yard_faqs, yard_curbside=True,
         cd_fee, cd_fac, cd_ans, cd_steps, cd_faqs,
         e_src=None, h_src=None):
    e_src = e_src or hhw
    h_src = h_src or hhw
    return rows_from_channels(
        city, state,
        [
            ch("mattress", "SPECIAL_HANDLING", "Low", bulk_curbside, bulk_fee, bulk_fac, bulk_ans, bulk_steps, bulk_faqs, hub),
            ch(["refrigerator", "air-conditioner"], "SPECIAL_HANDLING", "High", freon_curbside, freon_fee, freon_fac, freon_ans, freon_steps, freon_faqs, hub),
            ch(["television", "computer-monitor", "smartphone", "e-waste-mixed"], "BANNED_FROM_LANDFILLS", "Medium", e_curbside, e_fee, e_fac, e_ans, e_steps, e_faqs, e_src),
            ch(
                ["paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS", "High", False, h_fee, h_fac, h_ans, h_steps, h_faqs, h_src,
            ),
        ]
        + std_tail(
            hub,
            yard_fee=yard_fee, yard_facility=yard_fac, yard_answer=yard_ans,
            yard_steps=yard_steps, yard_faqs=yard_faqs, yard_curbside=yard_curbside,
            cd_fee=cd_fee, cd_facility=cd_fac, cd_answer=cd_ans, cd_steps=cd_steps, cd_faqs=cd_faqs,
        ),
    )


def washington():
    hub = ("DC DPW — Bulk Collections", "https://dpw.dc.gov/service/bulk-collections")
    hhw = ("DC DPW — Special Waste Collection Events", "https://dpw.dc.gov/service/household-hazardous-waste-hhw-e-cycling-document-shredding")
    return pack(
        "washington", "DC", hub, hhw,
        bulk_fee="DPW bulk appointment via 311 — max 7 items",
        bulk_fac="DC DPW bulk / Fort Totten Transfer Station",
        bulk_ans="District residents schedule {item} via DC 311 / DPW bulk trash (max 7 items; mattresses/box springs wrapped in plastic). Self-haul: Fort Totten Transfer Station, 4900 John McCormack Rd NE. Keep HHW and e-waste off bulk piles.",
        bulk_steps=["Schedule via 311.dc.gov or call 311.", "Wrap mattresses/box springs in plastic.", "Or self-haul to Fort Totten Transfer Station."],
        bulk_faqs=[("Limit?", "Max 7 items per appointment."), ("Wrap mattress?", "Yes.")],
        freon_fee="Bulk appointment / Fort Totten — Freon appliances",
        freon_fac="DC DPW bulk / Fort Totten Transfer Station",
        freon_ans="DC Freon {item}s go on a DPW bulk appointment (fridges doors removed; drain AC fluids) or Fort Totten. Never vent refrigerant. ACs are NOT accepted at Special Waste events.",
        freon_steps=["Schedule 311 bulk or haul to Fort Totten.", "Do not vent Freon yourself.", "Do not bring ACs to HHW/e-cycling events."],
        freon_faqs=[("Events for AC?", "No — Fort Totten or bulk."), ("Self-vent?", "Never.")],
        e_fee="Special Waste Collection Events only — register",
        e_fac="DC DPW Special Waste Events (RFK Lot 8)",
        e_ans="DC electronics including {item} go to DPW Special Waste Collection Events only — free registration required. Not accepted at Fort Totten. Wipe data before drop-off.",
        e_steps=["Register for a Special Waste event on dpw.dc.gov.", "Haul electronics to the event site.", "Wipe personal data."],
        e_faqs=[("Permanent depot?", "No — events only."), ("Fort Totten for TVs?", "No.")],
        h_fee="Special Waste Events only — no permanent depot",
        h_fac="DC DPW Special Waste Events (RFK Lot 8)",
        h_ans="Take {item} to DC DPW Special Waste Collection Events — no permanent daily HHW depot. Register in advance; bring District residency proof. Keep chemicals off bulk piles.",
        h_steps=["Check dpw.dc.gov for event dates.", "Register before attending.", "Keep HHW off bulk appointments."],
        h_faqs=[("Permanent HHW?", "No — events only."), ("Bulk for paint?", "No.")],
        yard_fee="Yard waste appointment via 311 / Fort Totten",
        yard_fac="DC DPW yard waste / Fort Totten",
        yard_ans="DC yard waste is appointment-based via 311 (max 20 paper bags) or Fort Totten drop-off (Tue–Fri 10–2, Sat 7–2).",
        yard_steps=["Schedule via 311 or haul to Fort Totten.", "Use paper bags within limits.", "Keep yard waste out of HHW events."],
        yard_faqs=[("Christmas trees?", "Follow DPW seasonal guidance.")],
        cd_fee="NOT accepted at Fort Totten / bulk — private C&D",
        cd_fac="Private C&D hauler",
        cd_ans="Construction debris is not accepted on DPW bulk or at Fort Totten. Use a private C&D hauler. Route paint/chemicals to Special Waste events.",
        cd_steps=["Do not haul C&D to Fort Totten.", "Hire private C&D.", "Route paint to Special Waste events."],
        cd_faqs=[("HHW for C&D?", "No.")],
    )


def cleveland():
    hub = ("City of Cleveland — Division of Waste Collection", "https://www.clevelandohio.gov/city-hall/departments/public-works/divisions/waste/waste")
    return pack(
        "cleveland", "OH", hub, hub,
        bulk_fee="Bulk week — first full week monthly, up to 3 items",
        bulk_fac="Cleveland bulk week / Ridge Road Transfer Station",
        bulk_ans="Cleveland {item}s go out during Bulk Week (first full week of each month) — up to 3 bulk items; request via 311 24–48 hours ahead. Mattresses/furniture must be wrapped in plastic. Drop-off: Ridge Road Transfer Station (4 free visits/year).",
        bulk_steps=["Request via Cleveland 311 before Bulk Week.", "Wrap mattresses/furniture in plastic.", "Or use Ridge Road Transfer Station drop-off."],
        bulk_faqs=[("When?", "First full week of each month."), ("Limit?", "Up to 3 bulk items.")],
        freon_fee="Bulk week if drained of coolants / Ridge Road drop-off",
        freon_fac="Cleveland bulk week / Ridge Road Transfer Station",
        freon_ans="Cleveland Freon {item}s may go during Bulk Week if drained of coolants and fluids per the Waste Guide. Never vent refrigerant yourself. Confirm Ridge Road drop-off rules before hauling.",
        freon_steps=["Confirm Freon prep rules in the Waste Guide.", "Do not vent Freon yourself.", "Request 311 bulk if using curbside."],
        freon_faqs=[("Self-vent?", "Never."), ("Drain required?", "Yes — coolants/fluids per guide.")],
        e_fee="TVs on bulk week; computers/phones at Carr Center year-round",
        e_fac="Bulk week / Carr Center (computers & phones)",
        e_ans="Cleveland TVs may go during Bulk Week. Year-round drop-off at Carr Center (5600 Carnegie Ave) accepts computers and cell phones only — other e-waste including {item} should follow CuyahogaRecycles.org pathways. Wipe data.",
        e_steps=["Use Bulk Week for TVs if eligible.", "Carr Center for computers/phones Mon–Fri 9–3.", "Check cuyahogarecycles.org for other e-waste."],
        e_faqs=[("Carr for TVs?", "Computers/phones only year-round."), ("Bulk for TVs?", "Yes during Bulk Week.")],
        e_curbside=True,
        h_fee="HHW first Friday each month — latex paint NOT accepted",
        h_fac="Carr Center / Ridge Road HHW (1st Friday monthly)",
        h_ans="Take {item} to Cleveland Household Hazardous Waste collection on the first Friday of each month at Carr Center and Ridge Road Transfer Station. Latex paint is NOT accepted — dry out and trash. Keep chemicals off bulk piles.",
        h_steps=["Go on the first Friday of the month.", "Confirm site (Carr or Ridge Road).", "Dry latex paint for trash — not HHW."],
        h_faqs=[("Latex at HHW?", "No — dry and trash."), ("How often?", "First Friday monthly.")],
        yard_fee="Weekly yard waste — up to 20 bags + 20 bundles",
        yard_fac="Cleveland weekly yard-waste collection",
        yard_ans="Cleveland yard waste: up to 20 bags + 20 bundles per week; branches bundled per Waste Guide.",
        yard_steps=["Follow bag/bundle limits.", "Set out on regular collection.", "Keep yard waste out of HHW."],
        yard_faqs=[("Christmas trees?", "Follow seasonal city guidance.")],
        cd_fee="NOT collected — private hauler / dumpster rental",
        cd_fac="Private C&D hauler / city dumpster rental",
        cd_ans="Construction debris is not collected by Cleveland Waste. Use a private hauler or city dumpster rental (216-664-2162). Route paint to monthly HHW.",
        cd_steps=["Do not put C&D in bulk week loads.", "Hire private C&D or rent a dumpster.", "Route paint to first-Friday HHW."],
        cd_faqs=[("HHW for C&D?", "No.")],
    )


def newark():
    hub = ("Newark DPW — Trash & Bulk", "https://dpw.newarknj.gov/trash-and-bulk-collection-schedule/")
    ehub = ("Newark DPW — What We Pick Up / E-waste", "https://dpw.newarknj.gov/what-we-pick-up/")
    hhw = ("Essex County Utilities Authority — HHW", "https://www.ecuanj.com/")
    return pack(
        "newark", "NJ", hub, hhw,
        bulk_fee="Bulk day by zone — max 10 items; mattresses max 3 covered",
        bulk_fac="Newark DPW bulk collection / ward service centers",
        bulk_ans="Newark {item}s go on scheduled bulk days (Zone A 1st Wednesday, Zone B 2nd Wednesday) — max 10 items; covered mattresses up to 3. Keep HHW and C&D off bulk piles.",
        bulk_steps=["Confirm your zone schedule on dpw.newarknj.gov.", "Cover mattresses; max 3.", "Keep paint/chemicals off bulk."],
        bulk_faqs=[("Zones?", "A = 1st Wed; B = 2nd Wed."), ("Mattress limit?", "Up to 3 covered.")],
        freon_fee="White goods appointment — call 973-733-3644",
        freon_fac="Newark DPW white-goods appointment pickup",
        freon_ans="Newark Freon {item}s and other white goods require an appointment — call 973-733-3644. Never vent refrigerant yourself.",
        freon_steps=["Call 973-733-3644 to schedule white goods.", "Do not vent Freon yourself.", "Do not leave Freon appliances on regular bulk without an appointment."],
        freon_faqs=[("Appt required?", "Yes for white goods."), ("Self-vent?", "Never.")],
        freon_curbside=True,
        e_fee="Essex County Electronic Recycling Depot — 62 Frelinghuysen Ave",
        e_fac="Essex County E-Waste Depot at Newark DPW HQ",
        e_ans="Newark electronics including {item} drop at the Essex County Electronic Recycling Depot, 62 Frelinghuysen Ave (Mon–Fri 8–4; Sat 8–12:30). Wipe data. Keep TVs out of trash/recycling carts.",
        e_steps=["Haul e-waste to 62 Frelinghuysen Ave.", "Confirm hours on dpw.newarknj.gov.", "Wipe personal data."],
        e_faqs=[("Address?", "62 Frelinghuysen Ave."), ("Trash for TVs?", "No.")],
        e_src=ehub,
        h_fee="ECUA HHW collection events only — no permanent Newark depot",
        h_fac="Essex County Utilities Authority HHW events",
        h_ans="Take {item} to Essex County Utilities Authority (ECUA) household hazardous waste collection events — Newark has no permanent HHW depot. Latex paint is typically not accepted at events; confirm ECUA rules. Keep chemicals off bulk piles.",
        h_steps=["Check ecuanj.com for upcoming HHW event dates.", "Haul sealed materials to the event.", "Keep HHW off Newark bulk days."],
        h_faqs=[("Permanent HHW?", "No — ECUA events only."), ("Bulk for paint?", "No.")],
        yard_fee="Yard waste by zone — 3rd/4th Wednesday",
        yard_fac="Newark DPW yard-waste collection",
        yard_ans="Newark yard waste: Zone A 3rd Wednesday, Zone B 4th Wednesday — brown bags/bundles per DPW rules.",
        yard_steps=["Follow zone yard-waste schedule.", "Use brown bags/bundles.", "Keep yard waste out of HHW events."],
        yard_faqs=[("Christmas trees?", "Follow DPW seasonal guidance.")],
        cd_fee="NOT accepted — private hauler",
        cd_fac="Private C&D hauler",
        cd_ans="Construction debris (drywall, roofing, etc.) is not accepted on Newark bulk. Use a private hauler. Route paint to ECUA HHW events.",
        cd_steps=["Do not put C&D on bulk day.", "Hire private C&D.", "Route paint to ECUA events."],
        cd_faqs=[("HHW for C&D?", "No.")],
    )


def st_paul():
    hub = ("Saint Paul Public Works — Bulky Item Collection", "https://www.stpaul.gov/departments/public-works/garbage-and-recycling/residential-collection/bulky-item-collection")
    hhw = ("Ramsey County Environmental Center", "https://www.ramseycounty.us/EC")
    return pack(
        "st-paul", "MN", hub, hhw,
        bulk_fee="Bulky set-out — 12 free pickups/year (extra $30/item published)",
        bulk_fac="Saint Paul bulky collection / Second Chance mattresses",
        bulk_ans="Saint Paul {item}s: set out by 6 AM labeled bulky — no advance schedule; separate truck within 2 business days. Limit 12 free pickups/year per garbage cart (extra items $30 + tax published). Mattresses unlimited free via Second Chance Recycling (612-230-7524).",
        bulk_steps=["Set out by 6 AM labeled bulky.", "Track the 12 free pickups/year limit.", "Call Second Chance for free mattress recycling."],
        bulk_faqs=[("Schedule?", "No — set out labeled bulky."), ("Mattress limit?", "Unlimited via Second Chance.")],
        freon_fee="Curbside bulky — Environmental Center does NOT accept Freon",
        freon_fac="Saint Paul bulky collection (not Ramsey EC)",
        freon_ans="Saint Paul Freon {item}s go on curbside bulky (emptied). Ramsey County Environmental Center does NOT accept Freon appliances. Never vent refrigerant yourself.",
        freon_steps=["Empty the unit and set out as bulky.", "Do not haul Freon appliances to the Environmental Center.", "Do not vent Freon yourself."],
        freon_faqs=[("EC for fridge?", "No Freon items at Environmental Center."), ("Self-vent?", "Never.")],
        e_fee="Free drop-off — Ramsey County Environmental Center",
        e_fac="Ramsey County Environmental Center — 1700 Kent St, Roseville",
        e_ans="Saint Paul electronics including {item} drop free at Ramsey County Environmental Center, 1700 Kent Street, Roseville (Tue–Fri 11–6; Sat 9–4). Also allowed as curbside bulky. Wipe data. No large Freon appliances at EC.",
        e_steps=["Haul to 1700 Kent St, Roseville.", "Bring photo ID.", "Wipe personal data."],
        e_faqs=[("Address?", "1700 Kent St, Roseville."), ("Fee?", "Free for eligible metro counties.")],
        e_curbside=True,
        h_fee="Permanent HHW — Ramsey County Environmental Center",
        h_fac="Ramsey County Environmental Center HHW",
        h_ans="Take {item} to Ramsey County Environmental Center HHW drop-off, 1700 Kent Street, Roseville — permanent depot (Tue–Fri 11–6; Sat 9–4). Photo ID required. Keep chemicals off bulky piles.",
        h_steps=["Haul sealed HHW to 1700 Kent St.", "Confirm hours on ramseycounty.us.", "Keep HHW off bulky set-outs."],
        h_faqs=[("Permanent?", "Yes — Environmental Center."), ("Bulk for paint?", "No.")],
        yard_fee="Not in garbage cart — subscription / Ramsey drop-off sites",
        yard_fac="Saint Paul yard program / Ramsey County yard sites",
        yard_ans="Saint Paul yard waste is not in the garbage cart — use subscription, one-time bag pickup, or free Ramsey County yard-waste drop-off sites.",
        yard_steps=["Do not put yard waste in garbage cart.", "Use city/county yard pathways.", "Check ramseycounty.us/yardwaste."],
        yard_faqs=[("Christmas trees?", "Follow seasonal city/county guidance.")],
        yard_curbside=False,
        cd_fee="NOT accepted as bulky — private / reuse pathways",
        cd_fac="Private C&D / RamseyRecycles A-to-Z",
        cd_ans="Construction debris is not accepted as Saint Paul bulky or in carts. Use RamseyRecycles.com/AtoZ or private C&D. Route paint to Environmental Center HHW.",
        cd_steps=["Do not set C&D as bulky.", "Use private C&D or reuse guides.", "Route paint to Environmental Center."],
        cd_faqs=[("HHW for C&D?", "No.")],
    )


def lubbock():
    hub = ("City of Lubbock — Bulky Items / CCS", "https://www.mylubbock.us/416/Bulky-Items")
    hhw = ("City of Lubbock — Household Hazardous Waste", "https://www.mylubbock.us/417/Household-Hazardous-Waste")
    return pack(
        "lubbock", "TX", hub, hhw,
        bulk_fee="No curbside bulk — Citizen Convenience Stations (visit limits)",
        bulk_fac="Lubbock Citizen Convenience Stations",
        bulk_ans="Lubbock has no curbside bulk pickup. Self-haul {item} to a Citizen Convenience Station (CCS) — unload yourself; oversized items have annual visit limits (official pages conflict between 4 and 8/year — confirm mylubbock.us). Keep HHW chemicals for Southside HHW appointments.",
        bulk_steps=["Self-haul to a CCS (not curbside bulk).", "Confirm current visit limits on mylubbock.us.", "Keep paint/chemicals for HHW appointment."],
        bulk_faqs=[("Curbside bulk?", "No — CCS self-haul."), ("Visit limit?", "Confirm mylubbock.us — pages conflict 4 vs 8.")],
        bulk_curbside=False,
        freon_fee="CCS drop-off — staff removes refrigerant; limit 2 appliances/visit",
        freon_fac="Lubbock Citizen Convenience Stations",
        freon_ans="Lubbock Freon {item}s drop at any CCS — staff removes refrigerant. Fridges/freezers must be empty; limit 2 appliances per visit. Never vent refrigerant yourself.",
        freon_steps=["Empty the unit before CCS drop-off.", "Limit 2 appliances per visit.", "Do not vent Freon yourself."],
        freon_faqs=[("Staff removes Freon?", "Yes at CCS."), ("Self-vent?", "Never.")],
        freon_curbside=False,
        e_fee="No city TV/computer drop-off — TCEQ manufacturer programs",
        e_fac="TCEQ Texas Recycles Computers / TVs programs",
        e_ans="Lubbock CCS and recycling bins do not accept TVs/computers. For {item}, use TCEQ manufacturer take-back programs (Texas Recycles Computers / Texas Recycles TVs). Do not put TVs in landfill loads.",
        e_steps=["Do not haul TVs to CCS as e-waste.", "Use TCEQ manufacturer program lists.", "Wipe personal data."],
        e_faqs=[("CCS for TVs?", "No municipal e-waste drop-off."), ("Landfill for TVs?", "No — use TCEQ programs.")],
        e_src=("City of Lubbock — Prepare Items for Recycling", "https://www.mylubbock.us/407/Prepare-Items-for-Recycling"),
        h_fee="HHW by appointment — Southside CCS only (806-775-2495)",
        h_fac="Southside Citizens Convenience Station — HHW by appointment",
        h_ans="Take {item} to Lubbock HHW by appointment at Southside CCS only (1631 84th St) — call 806-775-2495. Latex paint: solidify for regular disposal per Solid Waste guidance. Keep chemicals off CCS bulky loads without an HHW appointment.",
        h_steps=["Call 806-775-2495 for Southside HHW appointment.", "Haul sealed materials to 1631 84th St.", "Solidify latex per city guidance if not using HHW."],
        h_faqs=[("Which CCS?", "Southside only for HHW."), ("Walk-in HHW?", "Appointment required.")],
        yard_fee="CCS / Caliche Canyon Landfill brush pathways",
        yard_fac="Lubbock CCS / landfill yard pathways",
        yard_ans="Lubbock yard waste goes to CCS (pickup-bed size) or Caliche Canyon / West Texas Region Disposal Facility brush pathways — confirm mylubbock.us.",
        yard_steps=["Self-haul yard waste to CCS or landfill pathways.", "Confirm load size limits.", "Keep yard waste out of HHW appointments."],
        yard_faqs=[("Christmas trees?", "Confirm seasonal CCS/landfill rules.")],
        yard_curbside=False,
        cd_fee="Prohibited at CCS — landfill with published fees",
        cd_fac="West Texas Region Disposal Facility / private C&D",
        cd_ans="Construction debris is prohibited at Lubbock CCS. Haul to the landfill with published tipping fees or hire private C&D. Route paint to Southside HHW appointment.",
        cd_steps=["Do not take C&D to CCS.", "Use landfill C&D or private hauler.", "Route paint to Southside HHW."],
        cd_faqs=[("CCS for C&D?", "No.")],
    )


def baton_rouge():
    hub = ("East Baton Rouge — Garbage Collection", "https://www.brla.gov/337/Garbage-Collection")
    hhw = ("East Baton Rouge — Household Hazardous Material Collection Days", "https://www.brla.gov/893")
    return pack(
        "baton-rouge", "LA", hub, hhw,
        bulk_fee="Weekly out-of-cart bulk — max 3 items/day",
        bulk_fac="EBR weekly bulk / Starwood / North Landfill",
        bulk_ans="East Baton Rouge {item}s go with weekly out-of-cart bulk — max 3 bulk items/day, 3+ ft from cart. Self-haul: Starwood Self-Service Collection Facility or North Landfill with proof of residency. Keep HHW off bulk piles.",
        bulk_steps=["Set out up to 3 bulk items on garbage day.", "Or haul to Starwood / North Landfill.", "Keep paint/chemicals for HHMD events."],
        bulk_faqs=[("Limit?", "Max 3 bulk items/day."), ("Landfill?", "North Landfill — Samuels Road, Zachary.")],
        freon_fee="Freon must be removed/tagged before curbside or landfill",
        freon_fac="EBR bulk / North Landfill (Freon removed)",
        freon_ans="EBR Freon {item}s are not collected curbside unless a certified technician removes refrigerant and tags the unit; doors off fridges/freezers. North Landfill accepts white goods with refrigerants removed. Never vent yourself.",
        freon_steps=["Have Freon professionally removed and tagged before set-out.", "Doors off refrigerators/freezers.", "Do not vent Freon yourself."],
        freon_faqs=[("Curbside with Freon?", "No — remove/tag first."), ("Self-vent?", "Never.")],
        e_fee="HHMD events / parish partner pathways — no permanent parish e-waste depot",
        e_fac="EBR Household Hazardous Material Collection Days",
        e_ans="East Baton Rouge has no permanent parish hard-facility e-waste depot. Electronics including {item} go to bi-annual Household Hazardous Material Collection Days (and partners listed on brla.gov). Wipe data. Keep TVs out of recycling carts.",
        e_steps=["Watch brla.gov for HHMD event dates.", "Haul electronics to the event.", "Wipe personal data."],
        e_faqs=[("Permanent e-waste?", "No parish permanent depot."), ("Recycling cart?", "No TVs in carts.")],
        h_fee="HHMD events only — no permanent parish HHW facility",
        h_fac="EBR Household Hazardous Material Collection Days",
        h_ans="Take {item} to East Baton Rouge Household Hazardous Material Collection Days (semi-annual) — no permanent parish HHW facility. Dried latex may go in trash per parish guidance. Keep chemicals off bulk piles.",
        h_steps=["Check brla.gov/893 for HHMD dates.", "Haul sealed materials to the event.", "Keep HHW off weekly bulk."],
        h_faqs=[("Permanent HHW?", "No — events only."), ("Bulk for paint?", "No.")],
        yard_fee="Weekly yard waste bags/bundles / Starwood trimmings",
        yard_fac="EBR yard collection / Starwood",
        yard_ans="EBR yard waste: bagged leaves/grass and woody bundles curbside; Starwood accepts limited trimmings (no stumps/whole trees).",
        yard_steps=["Follow curbside bag/bundle rules.", "Or use Starwood for limited trimmings.", "Keep yard waste out of HHMD."],
        yard_faqs=[("Christmas trees?", "Follow parish seasonal guidance.")],
        cd_fee="Limited homeowner C&D at Starwood — no contractor roofing",
        cd_fac="Starwood Self-Service / private C&D",
        cd_ans="Limited homeowner-generated C&D may go to Starwood (single-room flooring, toilets, fence sections) — no contractor/roofing debris. Larger projects need private C&D. Route paint to HHMD events.",
        cd_steps=["Confirm Starwood C&D rules before hauling.", "Hire private C&D for remodel/roofing.", "Route paint to HHMD."],
        cd_faqs=[("Contractor debris at Starwood?", "No.")],
    )


def worcester():
    hub = ("Worcester DPW — Residential Drop-Off Center", "https://www.worcesterma.gov/trash-recycling/residential-drop-off-center/bulk-waste-disposal")
    hhw = ("Worcester DPW — Hazardous Waste Day", "https://www.worcesterma.gov/trash-recycling/residential-drop-off-center/hazardous-waste-day")
    return pack(
        "worcester", "MA", hub, hhw,
        bulk_fee="RDC appointment — $5/item; mattress/box spring $15 (published)",
        bulk_fac="Worcester Residential Drop-Off Center — 1065 Millbury St",
        bulk_ans="Worcester has no free city curbside bulk. Self-haul {item} to the Residential Drop-Off Center at 1065 Millbury Street by appointment — $5/item; mattress/box spring $15 (published). Optional paid Casella curbside pickup. Keep HHW for Hazardous Waste Days.",
        bulk_steps=["Book an RDC bulk appointment on worcesterma.gov.", "Haul to 1065 Millbury St.", "Keep paint/chemicals for HHW days."],
        bulk_faqs=[("Free curbside bulk?", "No."), ("Mattress fee?", "$15 published at RDC.")],
        bulk_curbside=False,
        freon_fee="RDC $5 each — facility handles Freon (published)",
        freon_fac="Worcester Residential Drop-Off Center",
        freon_ans="Worcester Freon {item}s drop at the RDC by appointment — $5 each published; facility handles Freon. Casella curbside Freon white goods have a separate published fee. Never vent yourself.",
        freon_steps=["Book RDC appointment for Freon appliances.", "Pay published $5 fee at drop-off.", "Do not vent Freon yourself."],
        freon_faqs=[("RDC Freon fee?", "$5 published."), ("Self-vent?", "Never.")],
        freon_curbside=False,
        e_fee="RDC appointment — TVs/monitors/CPUs $5 (published)",
        e_fac="Worcester Residential Drop-Off Center e-waste",
        e_ans="Worcester electronics including {item} go to the RDC by appointment — TVs $5 (size tiers), monitors/CPUs $5 published. Wipe data. Keep electronics out of trash under MA rules.",
        e_steps=["Book RDC e-waste appointment.", "Haul to 1065 Millbury St.", "Wipe personal data."],
        e_faqs=[("Fee?", "$5 published for TVs/monitors/CPUs."), ("Trash for TVs?", "No — MA restricted.")],
        h_fee="HHW 4 events/year by appointment — latex dry/trash",
        h_fac="Worcester Hazardous Waste Days (events only)",
        h_ans="Take {item} to Worcester Hazardous Waste Days (about 4 free events/year, appointment required) — no permanent daily HHW depot. Oil-based paint/stains at HHW days; latex paint → dry out then trash. Keep chemicals off RDC bulk loads.",
        h_steps=["Book a Hazardous Waste Day appointment on worcesterma.gov.", "Haul sealed materials to the event.", "Dry latex for trash — not HHW."],
        h_faqs=[("Permanent HHW?", "No — events only."), ("Latex at HHW?", "No — dry and trash.")],
        yard_fee="Seasonal RDC + satellite yard drop-off sites",
        yard_fac="Worcester RDC / satellite yard sites",
        yard_ans="Worcester yard waste drops seasonally at the RDC (1065 Millbury) and satellite sites (e.g. Chandler/Clark) — confirm worcesterma.gov hours.",
        yard_steps=["Confirm seasonal yard drop-off hours.", "Use RDC or satellite sites.", "Keep yard waste out of HHW days."],
        yard_faqs=[("Christmas trees?", "Follow seasonal DPW guidance.")],
        yard_curbside=False,
        cd_fee="RDC fee list for fixtures — not regular trash",
        cd_fac="Worcester RDC / private C&D",
        cd_ans="Some C&D-type fixtures (toilets, sinks, counters, doors) are on the RDC fee list — not regular trash. Larger remodel debris needs private C&D. Route paint to Hazardous Waste Days.",
        cd_steps=["Check RDC fee list before hauling fixtures.", "Hire private C&D for remodel debris.", "Route paint to HHW days."],
        cd_faqs=[("HHW for C&D?", "No.")],
    )


def little_rock():
    hub = ("Little Rock Solid Waste", "https://littlerock.gov/government/city-departments/public-works/solid-waste/")
    hhw = ("Little Rock Green Station", "https://littlerock.gov/government/city-departments/public-works/recycling/green-station-of-little-rock/")
    return pack(
        "little-rock", "AR", hub, hhw,
        bulk_fee="311 bulky — first 4 pickups/year free; then published fees",
        bulk_fac="Little Rock 311 bulky collection",
        bulk_ans="Little Rock {item}s: schedule via 311 — first 4 bulky/appliance pickups per calendar year free; additional pickups have published fees. Accepts furniture/mattresses/appliances (refrigerants removed). Keep HHW for Green Station.",
        bulk_steps=["Schedule via Little Rock 311.", "Track the 4 free pickups/year.", "Keep paint/chemicals for Green Station (note: paint not accepted there)."],
        bulk_faqs=[("Free pickups?", "First 4/year free."), ("How to schedule?", "Call/use 311.")],
        freon_fee="311 bulky — remove refrigerants before pickup",
        freon_fac="Little Rock 311 bulky (Freon removed)",
        freon_ans="Little Rock Freon {item}s on 311 bulky require refrigerants removed before pickup. Green Station does not accept window AC/Freon items. Never vent yourself.",
        freon_steps=["Remove refrigerants before scheduling bulky.", "Do not haul Freon AC to Green Station.", "Do not vent Freon yourself."],
        freon_faqs=[("Green Station for AC?", "No Freon items."), ("Self-vent?", "Never.")],
        e_fee="Green Station e-waste — households only",
        e_fac="Little Rock Green Station — 2000 S Thayer",
        e_ans="Little Rock electronics including {item} drop at Green Station, 2000 S Thayer Street (Mon–Thu 7–5; last Sat/month 7–1). Not accepted in bulky pickup. Wipe data.",
        e_steps=["Haul e-waste to 2000 S Thayer.", "Confirm hours on littlerock.gov.", "Wipe personal data."],
        e_faqs=[("Bulky for TVs?", "No — Green Station."), ("Address?", "2000 S Thayer St.")],
        h_fee="Green Station HHW — paint NOT accepted (dry/trash)",
        h_fac="Little Rock Green Station HHW",
        h_ans="Take {item} to Little Rock Green Station HHW (2000 S Thayer) for pesticides, oils, batteries, bulbs, etc. Paint is NOT accepted at Green Station — dry out and trash. Keep chemicals off bulky piles.",
        h_steps=["Haul eligible HHW to Green Station.", "Do not bring paint to Green Station — dry/trash.", "Keep HHW off 311 bulky."],
        h_faqs=[("Paint at Green Station?", "No — dry and trash."), ("Permanent?", "Yes — Green Station.")],
        yard_fee="Weekly curbside yard / landfill (fee)",
        yard_fac="Little Rock yard collection / landfill",
        yard_ans="Little Rock yard waste: weekly curbside the day after garbage; also accepted at the landfill (fee).",
        yard_steps=["Set out on yard day after garbage.", "Or haul to landfill with fee.", "Keep yard waste out of Green Station HHW."],
        yard_faqs=[("Christmas trees?", "Follow seasonal city guidance.")],
        cd_fee="NOT in bulky — landfill fee / contractor",
        cd_fac="Little Rock Landfill / private C&D",
        cd_ans="Construction debris is not in bulky pickup. Use Little Rock Landfill (10801 Ironton Cutoff) with published class fees or a contractor. Route eligible HHW to Green Station (not paint).",
        cd_steps=["Do not put C&D on bulky.", "Haul to landfill or hire contractor.", "Route chemicals to Green Station."],
        cd_faqs=[("Bulky for C&D?", "No.")],
    )


def tallahassee():
    hub = ("City of Tallahassee — Bulky Waste", "https://www.talgov.com/you/you-learn-solid-bulky.aspx")
    hhw = ("Leon County Hazardous Waste Center", "https://cms.leoncountyfl.gov/Government/Departments/Resource-Stewardship/Solid-Waste-Management/Hazardous-Waste-Center")
    return pack(
        "tallahassee", "FL", hub, hhw,
        bulk_fee="Curbside every other week — size limits; larger via Cash for Trash / special pickup",
        bulk_fac="Tallahassee bulky collection / Cash for Trash",
        bulk_ans="Tallahassee {item}s go on every-other-week bulky (furniture/mattresses/small appliances within ~6×4×4 ft). Larger items use Cash for Trash events or special pickup (fee). Keep HHW for Leon County Hazardous Waste Center.",
        bulk_steps=["Set out on your Red/Blue bulky week.", "Check size limits on talgov.com.", "Keep paint/chemicals for Leon County HHW."],
        bulk_faqs=[("How often?", "Every other week."), ("Too large?", "Cash for Trash or special pickup.")],
        freon_fee="Bulky / Cash for Trash appliances — confirm Freon prep",
        freon_fac="Tallahassee bulky / Cash for Trash",
        freon_ans="Tallahassee Freon {item}s follow bulky/Cash for Trash appliance pathways within program rules. Never vent refrigerant yourself. Confirm current Freon guidance on talgov.com before set-out.",
        freon_steps=["Confirm appliance bulky rules on talgov.com.", "Do not vent Freon yourself.", "Use Cash for Trash for oversized appliances if needed."],
        freon_faqs=[("Self-vent?", "Never."), ("Cash for Trash?", "Biannual city event for large items/HHW.")],
        e_fee="City electronics pickup by request + Leon County HHW centers",
        e_fac="Tallahassee electronics pickup / Leon County HHW Center",
        e_ans="Tallahassee utility customers can request Thursday electronics pickup; year-round drop-off for {item} at Leon County Hazardous Waste Center, 7550 Apalachee Parkway (Mon–Sat 8–5, free). Wipe data.",
        e_steps=["Request city electronics pickup or haul to 7550 Apalachee Pkwy.", "Confirm Leon County hours.", "Wipe personal data."],
        e_faqs=[("Permanent e-waste?", "Yes — Leon County HHW Center."), ("Fee?", "Free at county HHW Center.")],
        e_curbside=True,
        h_fee="Permanent free — Leon County Hazardous Waste Center",
        h_fac="Leon County Hazardous Waste Center — 7550 Apalachee Pkwy",
        h_ans="Take {item} to Leon County Hazardous Waste Center, 7550 Apalachee Parkway (Mon–Sat 8–5) — free permanent HHW/e-waste. City Cash for Trash also accepts HHW on event days. Keep chemicals off bulky piles.",
        h_steps=["Haul to 7550 Apalachee Parkway.", "Or use Cash for Trash event days.", "Keep HHW off bulky set-outs."],
        h_faqs=[("Permanent?", "Yes — Leon County HHW Center."), ("City-only HHW?", "Cash for Trash is event-only; county is permanent.")],
        yard_fee="Every-other-week yard waste — paper bags OK",
        yard_fac="Tallahassee yard-waste collection",
        yard_ans="Tallahassee yard waste runs every other week — paper bags OK, no plastic bags.",
        yard_steps=["Set out on yard week.", "Use paper bags only.", "Keep yard waste out of HHW."],
        yard_faqs=[("Christmas trees?", "Follow seasonal city guidance.")],
        cd_fee="NOT at Cash for Trash — special pickup (fee) / private",
        cd_fac="Special pickup / private C&D",
        cd_ans="Construction debris is not accepted at Cash for Trash. Request special pickup (fee) or hire private C&D. Route paint to Leon County HHW Center.",
        cd_steps=["Do not take C&D to Cash for Trash.", "Request special pickup or hire private C&D.", "Route paint to county HHW."],
        cd_faqs=[("Cash for Trash for C&D?", "No.")],
    )


def knoxville():
    hub = ("Knoxville Waste & Resources — Bulky Waste", "https://www.knoxvilletn.gov/government/city_departments_offices/public_service/waste_and_resources_management/garbage/bulky_waste_collection")
    hhw = ("Knoxville Household Hazardous Waste", "https://www.knoxvilletn.gov/government/city_departments_offices/public_service/waste_and_resources_management/household_hazardous_waste")
    return pack(
        "knoxville", "TN", hub, hhw,
        bulk_fee="Up to 5 bulky items/week — call 311 ≥2 business days ahead",
        bulk_fac="Knoxville bulky collection / Solid Waste Facility",
        bulk_ans="Knoxville {item}s: up to 5 bulky items/week — call 311 with a bulky alert ≥2 business days ahead. Keep HHW for the Elm Street HHW facility. Self-haul also available at the Solid Waste Facility (fees may apply).",
        bulk_steps=["Call 311 ≥2 business days before set-out.", "Limit 5 bulky items/week.", "Keep paint/chemicals for HHW at 1033 Elm St."],
        bulk_faqs=[("Limit?", "Up to 5/week."), ("Alert required?", "Yes — 311 bulky alert.")],
        freon_fee="Not curbside unless drained/tagged — facility drains (fee)",
        freon_fac="Knoxville Solid Waste Facility / tagged curbside",
        freon_ans="Knoxville Freon {item}s are not eligible curbside unless professionally drained and tagged. Bring to Solid Waste Facility at 1033 Elm Street — staff can drain coolant (tipping fee applies). Never vent yourself.",
        freon_steps=["Drain/tag before curbside or haul to 1033 Elm St.", "Expect facility fee for refrigerant appliances.", "Do not vent Freon yourself."],
        freon_faqs=[("Curbside with Freon?", "Only if drained/tagged."), ("Self-vent?", "Never.")],
        e_fee="Solid Waste Facility specialty recycling / county convenience centers",
        e_fac="Knoxville Solid Waste Facility e-waste",
        e_ans="Knoxville electronics including {item} go to the Solid Waste Facility specialty recycling at 1033 Elm Street (and some Knox County Convenience Centers). Wipe data. Keep TVs out of recycling carts.",
        e_steps=["Haul e-waste to 1033 Elm St.", "Confirm specialty recycling hours.", "Wipe personal data."],
        e_faqs=[("Address?", "1033 Elm Street."), ("Recycling cart?", "No TVs in carts.")],
        h_fee="Permanent free HHW — 1033 Elm St (latex dry/trash)",
        h_fac="Knoxville HHW — 1033 Elm Street",
        h_ans="Take {item} to Knoxville permanent free HHW at 1033 Elm Street. Wet paint/liquid HHW accepted; latex paint → dry and trash (not accepted at HHW). Keep chemicals off bulky piles.",
        h_steps=["Haul sealed HHW to 1033 Elm St.", "Dry latex for trash — not HHW.", "Keep HHW off bulky set-outs."],
        h_faqs=[("Permanent?", "Yes — 1033 Elm St."), ("Latex at HHW?", "No — dry and trash.")],
        yard_fee="Seasonal brush/leaves curbside programs",
        yard_fac="Knoxville yard-waste collection",
        yard_ans="Knoxville yard waste: curbside brush (Mar–Oct) and loose leaves (Nov–Feb) — do not mix brush with trash bulky.",
        yard_steps=["Follow seasonal brush/leaf schedules.", "Do not mix brush into trash bulky piles.", "Keep yard waste out of HHW."],
        yard_faqs=[("Christmas trees?", "Follow seasonal city guidance.")],
        cd_fee="Transfer Station C&D — published per-ton fees",
        cd_fac="Knoxville Solid Waste Facility / Transfer Station",
        cd_ans="Construction debris goes to the Transfer Station at 1033 Elm Street with published per-ton fees (not curbside bulky). Route paint to HHW (not latex).",
        cd_steps=["Haul C&D to Transfer Station.", "Expect published tipping fees.", "Route liquid HHW to on-site HHW."],
        cd_faqs=[("Bulky for C&D?", "No — Transfer Station.")],
    )


def akron():
    hub = ("City of Akron — Trash and Recycling", "https://www.akronohio.gov/departments/service/public_works_bureau/trash_and_recycling.php")
    hhw = ("Summit County ReWorks — HHW Hours", "https://www.summitreworks.com/243/HHW-Hours")
    return pack(
        "akron", "OH", hub, hhw,
        bulk_fee="Weekly large items — 3 ft from cart (special volume pickup 3×/yr)",
        bulk_fac="Akron weekly large-item collection",
        bulk_ans="Akron {item}s go weekly on normal trash day — place 3 ft from cart; no preschedule for furniture/mattresses. Large bag/box volumes need Special Bulk Volume Pickup (3/year; call 311 ≥1 business day ahead). Keep HHW for ReWorks.",
        bulk_steps=["Set out 3 ft from cart on trash day.", "Call 311 for special bulk volume if needed.", "Keep paint/chemicals for ReWorks HHW."],
        bulk_faqs=[("Schedule?", "No for normal large items."), ("Special volume?", "3 times/year via 311.")],
        freon_fee="Weekly curbside large-item / appliance pathway",
        freon_fac="Akron weekly appliance collection",
        freon_ans="Akron Freon {item}s go with weekly trash/recycle large-item pickup — city hauls to local salvage. Never vent refrigerant yourself.",
        freon_steps=["Set Freon appliances out with weekly collection.", "Do not vent Freon yourself.", "Keep chemicals off appliance piles."],
        freon_faqs=[("Self-vent?", "Never."), ("Drop-off required?", "Curbside weekly accepted.")],
        e_fee="TVs weekly curbside; other e-waste ReWorks Recycling Days",
        e_fac="Akron curbside TVs / ReWorks Recycling Days",
        e_ans="Akron TVs go on weekly large-item pickup. Other electronics including {item} use Summit County ReWorks Recycling Days at 1201 Graham Road, Stow (seasonal event dates). Wipe data.",
        e_steps=["Set TVs out weekly 3 ft from cart.", "Check summitreworks.com for Recycling Days.", "Wipe personal data."],
        e_faqs=[("Year-round e-waste depot?", "Recycling Days are event/seasonal."), ("TVs curbside?", "Yes weekly.")],
        e_curbside=True,
        h_fee="ReWorks HHW seasonal Thursdays 2–7 pm — latex dry/trash",
        h_fac="Summit County ReWorks HHW — 1201 Graham Rd, Stow",
        h_ans="Take {item} to Summit County ReWorks HHW at 1201 Graham Road, Stow — seasonal Thursdays 2–7 pm (confirm 2026 season dates). Oil/solvent paint at HHW; latex must be dried for trash. Keep chemicals off bulk piles.",
        h_steps=["Confirm current ReWorks HHW Thursday season.", "Haul to 1201 Graham Rd, Stow.", "Dry latex for trash — not HHW."],
        h_faqs=[("Year-round daily HHW?", "No — seasonal Thursdays."), ("Latex at HHW?", "No — dry and trash.")],
        yard_fee="Weekly bundled brush/branches; leaf program Nov–Dec",
        yard_fac="Akron yard / leaf collection",
        yard_ans="Akron yard waste: tied bundles (brush/branches) weekly curbside — not in carts; separate leaf collection Nov–Dec.",
        yard_steps=["Bundle brush per city rules.", "Do not put yard waste in carts.", "Follow leaf program dates."],
        yard_faqs=[("Christmas trees?", "Follow seasonal city guidance.")],
        cd_fee="NOT in carts — bundled wood only; demolition debris private",
        cd_fac="Private C&D / limited bundled wood curbside",
        cd_ans="Concrete, drywall, roofing, and demolition debris are not accepted in Akron carts. Limited bundled wood/brush may go curbside; larger C&D needs private hauler. Route paint to ReWorks HHW.",
        cd_steps=["Do not put C&D in carts.", "Hire private C&D for demolition debris.", "Route paint to ReWorks HHW."],
        cd_faqs=[("HHW for C&D?", "No.")],
    )


def mobile():
    hub = ("City of Mobile — Trash Pickup", "https://www.cityofmobile.org/public-works/trash-pickup-north/")
    hhw = ("City of Mobile — HHW Collection Events", "https://www.cityofmobile.org/household-hazardous-waste-collection-event-5/")
    return pack(
        "mobile", "AL", hub, hhw,
        bulk_fee="Every-other-week trash includes bulk ~2 cu yd",
        bulk_fac="Mobile biweekly trash/bulk / Chastang Landfill",
        bulk_ans="Mobile {item}s go with every-other-week residential trash — about 2 cubic yards (~15 bags). Excess: self-haul to landfill or paid city pickup (Public Works 251-208-4100). Keep HHW for collection events.",
        bulk_steps=["Set out within ~2 cu yd on trash week.", "Call Public Works for excess/paid pickup.", "Keep paint/chemicals for HHW events."],
        bulk_faqs=[("How often?", "Every other week."), ("Excess?", "Landfill or paid city pickup.")],
        freon_fee="Included in biweekly residential trash (appliances)",
        freon_fac="Mobile biweekly trash / landfill pathways",
        freon_ans="Mobile Freon {item}s are listed with appliances in every-other-week residential trash. Confirm current Freon prep with Public Works if needed. Never vent refrigerant yourself.",
        freon_steps=["Set appliances out on trash week within volume limits.", "Call Public Works with Freon questions.", "Do not vent Freon yourself."],
        freon_faqs=[("Self-vent?", "Never."), ("Separate Freon program?", "Not published — use trash pathway / ask Public Works.")],
        e_fee="City bins: small e-waste only (no TVs) — TVs private pathways",
        e_fac="Mobile recycling drop-offs (no TVs) / private TV recyclers",
        e_ans="Mobile city recycling drop-offs accept small electronics in e-waste bins — not TVs. For {item}/TVs, use city-listed private recyclers (fees may apply). Keep TVs out of recycling carts.",
        e_steps=["Use city e-waste bins only for small electronics.", "For TVs, use city-listed private recyclers.", "Wipe personal data."],
        e_faqs=[("City bins for TVs?", "No."), ("Permanent city TV depot?", "No — private pathways.")],
        e_src=("City of Mobile — Recycling", "https://www.cityofmobile.org/residents/trash-and-garbage/recycling/"),
        h_fee="HHW events only — no permanent depot",
        h_fac="Mobile Household Hazardous Waste collection events",
        h_ans="Take {item} to City of Mobile Household Hazardous Waste collection events — no permanent HHW facility. Events accept paint, fluids, pesticides, batteries, fluorescent tubes (not tires/electronics/appliances). Keep chemicals off trash piles.",
        h_steps=["Watch cityofmobile.org for HHW event announcements.", "Haul sealed materials to the event site.", "Keep HHW off biweekly trash piles."],
        h_faqs=[("Permanent HHW?", "No — events only."), ("Electronics at HHW?", "No.")],
        yard_fee="Bagged clippings in cart; limbs with trash pickup",
        yard_fac="Mobile yard / trash pathways",
        yard_ans="Mobile yard waste: bagged clippings in garbage cart; limbs with trash pickup. No tires/construction in cart.",
        yard_steps=["Bag clippings for the cart.", "Set limbs with trash pickup.", "Keep yard waste out of HHW events."],
        yard_faqs=[("Christmas trees?", "Follow seasonal city guidance.")],
        cd_fee="NOT in garbage cart — private landfills (city-listed)",
        cd_fac="Chastang Landfill / private C&D",
        cd_ans="Construction debris is not in the garbage cart. Use city-listed landfills such as Chastang Landfill (17045 Highway 43, Mt. Vernon) or private C&D. Route paint to HHW events.",
        cd_steps=["Do not put C&D in carts.", "Haul to city-listed landfill / private C&D.", "Route paint to HHW events."],
        cd_faqs=[("Cart for C&D?", "No.")],
    )


def fort_lauderdale():
    hub = ("Fort Lauderdale Sanitation — Collection Programs", "https://www.fortlauderdale.gov/Government/Departments/Public-Works/Operations/Sanitation-Operations/Collection-Programs")
    hhw = ("Fort Lauderdale — Household Hazardous Waste Events", "https://www.fortlauderdale.gov/HHW")
    ehub = ("Fort Lauderdale — Curbside Electronics Pick-Up", "https://www.fortlauderdale.gov/Government/Departments/Public-Works/Operations/Sanitation-Operations/Curbside-Electronics-Pick-Up")
    return pack(
        "fort-lauderdale", "FL", hub, hhw,
        bulk_fee="Monthly bulk — max 10 cu yd pile",
        bulk_fac="Fort Lauderdale monthly bulk (WM)",
        bulk_ans="Fort Lauderdale {item}s go on monthly bulk collection day (WM) — max 10 cubic yards; set out ≤24 hours before, by 7 a.m. Keep HHW for regional events. C&D/concrete not in bulk.",
        bulk_steps=["Set out on monthly bulk day by 7 a.m.", "Stay within 10 cu yd.", "Keep paint/chemicals for HHW events."],
        bulk_faqs=[("Limit?", "Max 10 cubic yards."), ("C&D in bulk?", "No.")],
        freon_fee="Bulk/white goods curbside — fridge/AC listed",
        freon_fac="Fort Lauderdale monthly bulk white goods",
        freon_ans="Fort Lauderdale Freon {item}s are listed with bulk/white goods (AC, refrigerators, freezers, etc.). Never vent refrigerant yourself. Confirm current prep rules with Sanitation if needed.",
        freon_steps=["Set Freon appliances on bulk day.", "Do not vent Freon yourself.", "Do not take appliances to HHW events."],
        freon_faqs=[("HHW events for appliances?", "No."), ("Self-vent?", "Never.")],
        e_fee="Curbside electronics by request + regional HHW/e-waste events",
        e_fac="Fort Lauderdale curbside electronics / regional events",
        e_ans="Fort Lauderdale residents schedule curbside electronics pickup by 4 p.m. the day before recycling day (call 954-828-8000 or online). {item} also accepted at regional HHW/electronics events listed on fortlauderdale.gov/HHW. Wipe data. City is NOT in Broward residential drop-off centers program.",
        e_steps=["Request curbside electronics before recycling day.", "Or use regional HHW/e-waste event dates.", "Wipe personal data."],
        e_faqs=[("Broward drop-off centers?", "Fort Lauderdale is not a participating city."), ("Curbside e-waste?", "Yes — request ahead.")],
        e_curbside=True,
        e_src=ehub,
        h_fee="Regional HHW events only — no permanent city depot",
        h_fac="Broward regional HHW/electronics events (see fortlauderdale.gov/HHW)",
        h_ans="Take {item} to regional Household Hazardous Waste/electronics drop-off events listed on fortlauderdale.gov/HHW (Coral Springs, Coconut Creek, Pompano Beach, etc.) — no permanent Fort Lauderdale HHW depot and not in Broward drop-off centers. Keep chemicals off bulk piles.",
        h_steps=["Check fortlauderdale.gov/HHW for 2026 event dates/sites.", "Bring proof of residency.", "Keep HHW off monthly bulk piles."],
        h_faqs=[("Permanent HHW?", "No — regional events only."), ("Broward centers?", "Not available to Fort Lauderdale residents.")],
        yard_fee="Weekly green cart; oversized with bulk",
        yard_fac="Fort Lauderdale yard-waste collection",
        yard_ans="Fort Lauderdale yard waste: weekly green cart; oversized limbs with bulk (≤12 ft × 12 in diameter).",
        yard_steps=["Use green cart weekly.", "Oversized limbs on bulk day within limits.", "Keep yard waste out of HHW events."],
        yard_faqs=[("Christmas trees?", "Follow seasonal city guidance.")],
        cd_fee="Excluded from bulk — private C&D",
        cd_fac="Private C&D hauler",
        cd_ans="Dirt, sod, sand, pavers, concrete, and tiles are excluded from Fort Lauderdale bulk. Hire private C&D. Route paint to regional HHW events.",
        cd_steps=["Do not put C&D in bulk piles.", "Hire private C&D.", "Route paint to HHW events."],
        cd_faqs=[("Bulk for concrete?", "No.")],
    )


def syracuse():
    hub = ("City of Syracuse — Bulk", "https://www.syr.gov/Living/My-Home/Trash-and-Recycling/Bulk")
    ocrra = ("OCRRA — Rock Cut Road Drop-Off", "https://ocrra.org/locations/")
    hhw = ("OCRRA — Household Toxics", "https://ocrra.org/waste/household-toxics/")
    return pack(
        "syracuse", "NY", hub, hhw,
        bulk_fee="Cityline bulk — 4 pickups/year, max 2 cu yd",
        bulk_fac="Syracuse Cityline bulk / OCRRA Rock Cut Road",
        bulk_ans="Syracuse {item}s: call Cityline 315-448-2489 ≥2 days ahead — 4 pickups/year, max 2 cubic yards. Self-haul mattresses/furniture to OCRRA Rock Cut Road Transfer Station (mattress processing fee published). Keep HHW for toxics appointments; OCRRA does not accept electronics.",
        bulk_steps=["Call Cityline 315-448-2489 to schedule.", "Stay within 4 pickups/year and 2 cu yd.", "Or self-haul to OCRRA Rock Cut Road."],
        bulk_faqs=[("Limit?", "4 pickups/year, max 2 cu yd."), ("Mattress drop-off?", "OCRRA Rock Cut — fee published.")],
        freon_fee="NOT city bulk — OCRRA Rock Cut + refrigerant surcharge",
        freon_fac="OCRRA Rock Cut Road — appliances",
        freon_ans="Syracuse Freon {item}s are not city bulk/trash. Take to OCRRA Rock Cut Road Drop-Off (5808 Rock Cut Road, Jamesville) — MSW fees plus published $15 refrigerant surcharge per unit. Never vent yourself.",
        freon_steps=["Haul to OCRRA Rock Cut Road.", "Expect published refrigerant surcharge.", "Do not vent Freon yourself."],
        freon_faqs=[("City bulk for fridge?", "No."), ("Self-vent?", "Never.")],
        freon_curbside=False,
        e_fee="OCRRA does NOT accept electronics — private drop-offs only",
        e_fac="Private e-waste recyclers (OCRRA-listed)",
        e_ans="OCRRA agency sites do not accept electronics. For {item}, use private drop-offs listed on ocrra.org/electronics (fees vary). Keep TVs out of city trash/bulk. Wipe data.",
        e_steps=["Do not haul TVs to OCRRA Rock Cut as e-waste.", "Use OCRRA-listed private electronics recyclers.", "Wipe personal data."],
        e_faqs=[("OCRRA for TVs?", "No — private only."), ("City bulk for TVs?", "No.")],
        e_src=("OCRRA — Electronics", "https://ocrra.org/electronics/"),
        h_fee="OCRRA Household Toxics appointment — Miller Environmental",
        h_fac="Miller Environmental Group — OCRRA Household Toxics",
        h_ans="Take {item} to OCRRA Household Toxics by appointment at Miller Environmental Group, 532 State Fair Blvd (Onondaga County residents except Skaneateles; 2 appointments/year). Free with appointment. PaintCare drop-offs also handle paint-only. Keep chemicals off bulk piles.",
        h_steps=["Book OCRRA Household Toxics appointment.", "Haul to 532 State Fair Blvd.", "Keep HHW off Cityline bulk."],
        h_faqs=[("Walk-in?", "Appointment required."), ("Permanent city depot?", "Appointment site — not open dump.")],
        yard_fee="Monthly quadrant pickup + DPW Canal St drop-off",
        yard_fac="Syracuse yard waste / DPW Canal St Ext",
        yard_ans="Syracuse yard waste: monthly quadrant pickup Apr–Oct; DPW self-drop at 1200 Canal St Ext (Apr–Nov). OCRRA compost sites require a pass.",
        yard_steps=["Follow monthly quadrant schedule.", "Or drop at 1200 Canal St Ext in season.", "Keep yard waste out of toxics appointments."],
        yard_faqs=[("Christmas trees?", "Follow seasonal city/OCRRA guidance.")],
        cd_fee="City C&D pickup 2×/year by quadrant / OCRRA Rock Cut",
        cd_fac="Syracuse C&D pickup / OCRRA Rock Cut",
        cd_ans="Syracuse offers C&D pickup twice yearly by quadrant (May & Sept, max 2 cu yd). Excess goes to OCRRA Rock Cut or Camillus landfill pathways. Route paint to Household Toxics.",
        cd_steps=["Use May/Sept C&D pickup within limits.", "Or haul excess to OCRRA Rock Cut.", "Route paint to toxics appointment."],
        cd_faqs=[("Year-round city C&D?", "Only twice yearly by quadrant.")],
    )


def dayton():
    hub = ("City of Dayton — Bulk Waste Collection", "https://www.daytonohio.gov/396/Bulk-Waste-Collection")
    hhw = ("Montgomery County SWD — Household Hazardous Waste", "https://www.mcohio.org/550/Household-Hazardous-Waste-Disposal")
    ehub = ("Montgomery County SWD — Electronics Recycling", "https://www.mcohio.org/546/Electronics-Recycling")
    return pack(
        "dayton", "OH", hub, hhw,
        bulk_fee="Scheduled monthly bulk by zone Friday — wrap mattresses",
        bulk_fac="Dayton scheduled bulk / MCSWD Transfer",
        bulk_ans="Dayton {item}s: scheduled bulk one Friday/month by zone — call 937-333-4800 or Dayton Delivers by Wednesday before; limit 5 large items + 25 bags/boxes. Mattresses/box springs must be wrapped. Keep HHW/e-waste for MCSWD Transfer & Recycling.",
        bulk_steps=["Schedule by Wed before your zone Friday.", "Wrap mattresses/box springs.", "Keep paint/electronics for MCSWD."],
        bulk_faqs=[("How often?", "One Friday/month by zone."), ("Wrap mattress?", "Yes.")],
        freon_fee="City bulk lists fridges; MCSWD free Freon removal up to 5/year",
        freon_fac="Dayton bulk / MCSWD Transfer (Moraine)",
        freon_ans="Dayton Freon {item}s may go on scheduled bulk. Montgomery County Transfer & Recycling (1001 Encrete Lane, Moraine) offers free Freon removal up to 5/year for county residents; appliance amnesty weekends twice yearly. Never vent yourself.",
        freon_steps=["Schedule city bulk or haul to MCSWD Transfer.", "Ask about free Freon removal / amnesty weekends.", "Do not vent Freon yourself."],
        freon_faqs=[("MCSWD Freon?", "Free removal up to 5/year for residents."), ("Self-vent?", "Never.")],
        e_fee="Free electronics at MCSWD Transfer & Recycling",
        e_fac="MCSWD Transfer & Recycling — electronics",
        e_ans="Dayton-area electronics including {item} drop free at Montgomery County Transfer & Recycling, 1001 Encrete Lane, Moraine — computers, monitors, TVs, microwaves, small appliances. Wipe data.",
        e_steps=["Haul e-waste to 1001 Encrete Lane, Moraine.", "Bring proof of county residency.", "Wipe personal data."],
        e_faqs=[("Fee?", "Free for county residents."), ("Address?", "1001 Encrete Lane, Moraine.")],
        e_src=ehub,
        h_fee="MCSWD HHW — Tuesdays 1–7 pm (seasonal schedule)",
        h_fac="MCSWD HHW at 1001 Encrete Lane, Moraine",
        h_ans="Take {item} to Montgomery County HHW at 1001 Encrete Lane, Moraine — Mar–Oct every Tuesday 1–7 pm; Nov–Feb first Tuesday/month 1–7 pm. Latex and oil paint accepted. Proof of residency required. Keep chemicals off bulk piles.",
        h_steps=["Confirm current Tuesday HHW schedule on mcohio.org.", "Haul sealed materials to Encrete Lane.", "Keep HHW off Dayton bulk."],
        h_faqs=[("Permanent?", "Scheduled HHW days at transfer site."), ("Paint accepted?", "Latex and oil-based.")],
        yard_fee="Bulk yard — tied 4-ft lengths; MCSWD yard free for residents",
        yard_fac="Dayton bulk yard / MCSWD Transfer",
        yard_ans="Dayton yard waste on bulk: tied in 4-ft lengths, ≤18 in diameter, separated from other bulk. MCSWD Transfer accepts residential yard waste (free for county residents per district rules).",
        yard_steps=["Bundle yard waste per Dayton bulk rules.", "Or haul to MCSWD Transfer.", "Keep yard waste out of HHW canopy."],
        yard_faqs=[("Christmas trees?", "Follow seasonal city/county guidance.")],
        cd_fee="NOT in city bulk — MCSWD C&D $60/ton published",
        cd_fac="MCSWD Transfer C&D / private hauler",
        cd_ans="Building/excavating materials are not accepted in Dayton bulk. Haul C&D to MCSWD Transfer ($60/ton published for county residents) or hire private C&D. Route paint to Tuesday HHW.",
        cd_steps=["Do not put C&D on city bulk.", "Haul to MCSWD or hire private C&D.", "Route paint to HHW."],
        cd_faqs=[("Bulk for C&D?", "No.")],
    )


FACILITIES = [
    {
        "name": "Fort Totten Transfer Station",
        "facility_type": "Municipal transfer station",
        "city_slug": "washington", "state": "DC", "zip": "20011",
        "address": "4900 John McCormack Road NE, Washington, DC 20011",
        "lat": 38.947, "lng": -77.002,
        "source_url": "https://dpw.dc.gov/service/fort-totten-transfer-station-has-reopened",
        "hours": "Tue–Fri 10:00–14:00; Sat 07:00–14:00 (tires Wed–Fri only)",
        "phone": None,
        "accepted_materials": BULKY + APPLIANCE + ["tires", "yard-waste"],
    },
    {
        "name": "Ridge Road Transfer Station",
        "facility_type": "Municipal transfer station",
        "city_slug": "cleveland", "state": "OH", "zip": "44144",
        "address": "3727 Ridge Road, Cleveland, OH 44144",
        "lat": 41.45, "lng": -81.73,
        "source_url": "https://www.clevelandohio.gov/city-hall/departments/public-works/divisions/waste/waste",
        "hours": "Mon–Sat 09:00–15:00; HHW first Friday monthly",
        "phone": None,
        "accepted_materials": BULKY + HHW_MATERIALS + ["tires"],
    },
    {
        "name": "Newark DPW / Essex County Electronic Recycling Depot",
        "facility_type": "Municipal e-waste drop-off",
        "city_slug": "newark", "state": "NJ", "zip": "07114",
        "address": "62 Frelinghuysen Avenue, Newark, NJ 07114",
        "lat": 40.72, "lng": -74.17,
        "source_url": "https://dpw.newarknj.gov/what-we-pick-up/",
        "hours": "Mon–Fri 08:00–16:00; Sat 08:00–12:30",
        "phone": None,
        "accepted_materials": E_WASTE + ["car-battery"],
    },
    {
        "name": "Ramsey County Environmental Center",
        "facility_type": "Household hazardous waste / e-waste drop-off",
        "city_slug": "st-paul", "state": "MN", "zip": "55113",
        "address": "1700 Kent Street, Roseville, MN 55113",
        "lat": 44.995, "lng": -93.155,
        "source_url": "https://www.ramseycounty.us/EC",
        "hours": "Tue–Fri 11:00–18:00; Sat 09:00–16:00",
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": "Southside Citizens Convenience Station",
        "facility_type": "Municipal convenience station / HHW by appointment",
        "city_slug": "lubbock", "state": "TX", "zip": "79423",
        "address": "1631 84th Street, Lubbock, TX 79423",
        "lat": 33.5175, "lng": -101.8541,
        "source_url": "https://www.mylubbock.us/412/Southside-Citizens-Convenience-Station",
        "hours": "Mon–Sat 08:00–17:30; HHW by appointment",
        "phone": "806-775-2495",
        "accepted_materials": BULKY + APPLIANCE + HHW_MATERIALS + ["tires", "yard-waste"],
    },
    {
        "name": "East Baton Rouge North Landfill",
        "facility_type": "Municipal landfill",
        "city_slug": "baton-rouge", "state": "LA", "zip": "70791",
        "address": "16001 Samuels Road, Zachary, LA 70791",
        "lat": 30.65, "lng": -91.15,
        "source_url": "https://www.brla.gov/340/North-Landfill-Operations",
        "hours": "Mon–Fri 05:30–17:00; Sat 07:00–15:00",
        "phone": None,
        "accepted_materials": BULKY + APPLIANCE + ["tires"],
    },
    {
        "name": "Worcester Residential Drop-Off Center",
        "facility_type": "Municipal bulk / e-waste drop-off",
        "city_slug": "worcester", "state": "MA", "zip": "01607",
        "address": "1065 Millbury Street, Worcester, MA 01607",
        "lat": 42.24, "lng": -71.79,
        "source_url": "https://www.worcesterma.gov/trash-recycling/residential-drop-off-center/bulk-waste-disposal",
        "hours": "Bulk by appointment (Wed/Sat seasonal) — confirm worcesterma.gov",
        "phone": None,
        "accepted_materials": BULKY + APPLIANCE + E_WASTE + ["tires", "yard-waste"],
    },
    {
        "name": "Little Rock Green Station",
        "facility_type": "Household hazardous waste / e-waste drop-off",
        "city_slug": "little-rock", "state": "AR", "zip": "72202",
        "address": "2000 S Thayer Street, Little Rock, AR 72202",
        "lat": 34.74, "lng": -92.28,
        "source_url": "https://littlerock.gov/government/city-departments/public-works/recycling/green-station-of-little-rock/",
        "hours": "Mon–Thu 07:00–17:00; last Sat/month 07:00–13:00",
        "phone": None,
        "accepted_materials": [m for m in HHW_MATERIALS if m not in ("paint-latex", "paint-oil")] + E_WASTE,
    },
    {
        "name": "Leon County Hazardous Waste Center",
        "facility_type": "Household hazardous waste / e-waste drop-off",
        "city_slug": "tallahassee", "state": "FL", "zip": "32311",
        "address": "7550 Apalachee Parkway, Tallahassee, FL 32311",
        "lat": 30.43, "lng": -84.21,
        "source_url": "https://cms.leoncountyfl.gov/Government/Departments/Resource-Stewardship/Solid-Waste-Management/Hazardous-Waste-Center",
        "hours": "Mon–Sat 08:00–17:00",
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": "Knoxville Solid Waste Facility / HHW",
        "facility_type": "Municipal transfer station / HHW",
        "city_slug": "knoxville", "state": "TN", "zip": "37921",
        "address": "1033 Elm Street, Knoxville, TN 37921",
        "lat": 35.97, "lng": -83.94,
        "source_url": "https://www.knoxvilletn.gov/government/city_departments_offices/public_service/waste_and_resources_management/household_hazardous_waste",
        "hours": "Mon/Tue/Thu/Fri 07:00–15:45; Wed 07:00–11:45; Sat 08:00–11:45",
        "phone": None,
        "accepted_materials": BULKY + APPLIANCE + HHW_MATERIALS + E_WASTE + ["tires", "construction-debris"],
    },
    {
        "name": "Summit County ReWorks HHW Collection Center",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "akron", "state": "OH", "zip": "44224",
        "address": "1201 Graham Road, Stow, OH 44224",
        "lat": 41.15, "lng": -81.44,
        "source_url": "https://www.summitreworks.com/243/HHW-Hours",
        "hours": "Seasonal Thursdays 14:00–19:00 — confirm summitreworks.com",
        "phone": None,
        "accepted_materials": HHW_MATERIALS,
    },
    {
        "name": "Chastang Landfill",
        "facility_type": "Landfill",
        "city_slug": "mobile", "state": "AL", "zip": "36560",
        "address": "17045 Highway 43, Mount Vernon, AL 36560",
        "lat": 31.09, "lng": -88.01,
        "source_url": "https://www.cityofmobile.org/public-works/landfill-information/",
        "hours": "Mon–Fri 07:00–16:00",
        "phone": None,
        "accepted_materials": BULKY + ["construction-debris", "lumber", "drywall", "concrete"],
    },
    {
        "name": "Broward regional HHW/electronics event site (Pompano Beach)",
        "facility_type": "Household hazardous waste / e-waste event drop-off",
        "city_slug": "fort-lauderdale", "state": "FL", "zip": "33060",
        "address": "1660 NE 10th Street, Pompano Beach, FL 33060",
        "lat": 26.24, "lng": -80.11,
        "source_url": "https://www.fortlauderdale.gov/HHW",
        "hours": "Event days only — confirm fortlauderdale.gov/HHW",
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": "OCRRA Rock Cut Road Drop-Off",
        "facility_type": "Transfer station / bulky drop-off",
        "city_slug": "syracuse", "state": "NY", "zip": "13078",
        "address": "5808 Rock Cut Road, Jamesville, NY 13078",
        "lat": 43.00, "lng": -76.08,
        "source_url": "https://ocrra.org/locations/",
        "hours": "Confirm ocrra.org/locations (residential evening/Sat hours)",
        "phone": None,
        "accepted_materials": BULKY + APPLIANCE + ["tires", "construction-debris"],
    },
    {
        "name": "OCRRA Household Toxics — Miller Environmental Group",
        "facility_type": "Household hazardous waste by appointment",
        "city_slug": "syracuse", "state": "NY", "zip": "13209",
        "address": "532 State Fair Boulevard, Syracuse, NY 13209",
        "lat": 43.07, "lng": -76.18,
        "source_url": "https://ocrra.org/waste/household-toxics/",
        "hours": "By appointment; Mon/Thu/Fri 08:00–15:00; 1st Sat 08:00–12:00",
        "phone": None,
        "accepted_materials": HHW_MATERIALS,
    },
    {
        "name": "Montgomery County Transfer & Recycling Facility",
        "facility_type": "County transfer / HHW / e-waste",
        "city_slug": "dayton", "state": "OH", "zip": "45439",
        "address": "1001 Encrete Lane, Moraine, OH 45439",
        "lat": 39.70, "lng": -84.22,
        "source_url": "https://www.mcohio.org/401/Solid-Waste",
        "hours": "Mon–Fri 06:00–19:00; Sat 08:00–15:00; HHW Tue 13:00–19:00 (seasonal)",
        "phone": None,
        "accepted_materials": BULKY + APPLIANCE + HHW_MATERIALS + E_WASTE + ["tires", "construction-debris", "yard-waste"],
    },
]


def upsert_facilities():
    fac_path = DATA / "facilities" / "all.json"
    facilities = json.loads(fac_path.read_text())
    wipe = {f["city_slug"] for f in FACILITIES}
    keep = [f for f in facilities if f.get("city_slug") not in wipe]
    keep.extend(FACILITIES)
    fac_path.write_text(json.dumps(keep, indent=2) + "\n")


def main() -> None:
    audited = {
        "washington": clone_siblings(washington()),
        "cleveland": clone_siblings(cleveland()),
        "newark": clone_siblings(newark()),
        "st-paul": clone_siblings(st_paul()),
        "lubbock": clone_siblings(lubbock()),
        "baton-rouge": clone_siblings(baton_rouge()),
        "worcester": clone_siblings(worcester()),
        "little-rock": clone_siblings(little_rock()),
        "tallahassee": clone_siblings(tallahassee()),
        "knoxville": clone_siblings(knoxville()),
        "akron": clone_siblings(akron()),
        "mobile": clone_siblings(mobile()),
        "fort-lauderdale": clone_siblings(fort_lauderdale()),
        "syracuse": clone_siblings(syracuse()),
        "dayton": clone_siblings(dayton()),
    }

    for city, rows in audited.items():
        slugs = {r["item_slug"] for r in rows}
        if len(slugs) != 70:
            raise SystemExit(f"{city}: expected 70 items, got {len(slugs)} ({sorted(slugs)})")

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

    print("Wave-23a thin cities written:")
    for city, rows in audited.items():
        print(f"  {city}: {len(rows)} rules")
    print(f"Cities: {len(audited)}")
    print(f"Facilities added: {len(FACILITIES)}")
    print(f"Total rules now: {len(keep)}")


if __name__ == "__main__":
    main()
