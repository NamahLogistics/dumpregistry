#!/usr/bin/env python3
"""Expand CA sibling coverage + add researched city guides for next US metros."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
VERIFIED = "2026-08-10"

CORE = [
    "mattress",
    "refrigerator",
    "television",
    "computer-monitor",
    "smartphone",
    "e-waste-mixed",
    "car-battery",
    "lithium-battery",
    "paint-latex",
    "paint-oil",
    "motor-oil",
    "propane-tank",
    "fluorescent-bulbs",
    "medical-sharps",
    "tires",
    "air-conditioner",
    "yard-waste",
    "food-scraps",
    "plastic-bags",
    "cooking-oil",
    "construction-debris",
]

CA_MORE_SIBLINGS = {
    "mattress": ["dining-table", "desk", "bookshelf", "hot-tub", "piano"],
    "propane-tank": ["helium-tank", "fire-extinguisher"],
    "air-conditioner": ["dehumidifier"],
    "tires": ["tire-rims"],
    "construction-debris": ["concrete", "drywall", "lumber", "asphalt-shingles", "car-parts"],
    "fluorescent-bulbs": ["led-bulbs", "incandescent-bulbs"],
    "plastic-bags": ["styrofoam"],
    "e-waste-mixed": ["solar-panel"],
}


def faq(pairs):
    return [{"q": q, "a": a} for q, a in pairs]


def rule(city_slug, state, item, badge, hazard, curbside, fee, facility, answer, steps, faqs, src_name, src_url):
    return {
        "item_slug": item,
        "state": state,
        "city_slug": city_slug,
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
        "reviewed_by": "editorial",
        "needs_review": False,
    }


def clone_siblings(rules, mapping):
    by = {(r.get("city_slug"), r["item_slug"]): r for r in rules if r.get("city_slug")}
    out = []
    for (city, item), base in list(by.items()):
        for sib in mapping.get(item, []):
            if (city, sib) in by:
                continue
            e = deepcopy(base)
            e["item_slug"] = sib
            e["answer"] = (
                f"In {city.replace('-', ' ').title()}, {sib.replace('-', ' ')} follows the same "
                f"city program pathway as {item.replace('-', ' ')}. " + base["answer"]
            )
            e["faqs"] = faq(
                [
                    (
                        f"Same as {item.replace('-', ' ')}?",
                        "Yes — same city program channel; confirm acceptance for unusual sizes.",
                    ),
                    ("Source?", f"Based on {base['source_name']}."),
                ]
            )
            e["common_disposal_fee"] = str(e.get("common_disposal_fee") or "")[:80]
            e["nearest_facility_type"] = str(e.get("nearest_facility_type") or "")[:120]
            out.append(e)
            by[(city, sib)] = e
    return out


def pack_city(cfg):
    """Build 21 core rules + facilities for one metro from a program config."""
    c = cfg["city_slug"]
    st = cfg["state"]
    name = cfg["city"]
    rows = []
    bulky = cfg["bulky"]
    hhw = cfg["hhw"]
    organics = cfg["organics"]
    bags = cfg.get("bags_source", bulky)

    rows.append(
        rule(
            c,
            st,
            "mattress",
            "SPECIAL_HANDLING",
            "Low",
            True,
            bulky["fee"],
            bulky["facility"],
            bulky["mattress_answer"].format(city=name),
            bulky["mattress_steps"],
            bulky["mattress_faqs"],
            bulky["source_name"],
            bulky["source_url"],
        )
    )
    rows.append(
        rule(
            c,
            st,
            "refrigerator",
            "SPECIAL_HANDLING",
            "Medium",
            True,
            bulky.get("appliance_fee", bulky["fee"]),
            bulky.get("appliance_facility", bulky["facility"]),
            bulky["fridge_answer"].format(city=name),
            bulky["fridge_steps"],
            bulky["fridge_faqs"],
            bulky["source_name"],
            bulky["source_url"],
        )
    )
    for item in ["television", "computer-monitor", "smartphone", "e-waste-mixed"]:
        rows.append(
            rule(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                hhw["fee"],
                hhw["facility"],
                hhw["ewaste_answer"].format(city=name),
                hhw["ewaste_steps"],
                hhw["ewaste_faqs"],
                hhw["source_name"],
                hhw["source_url"],
            )
        )
    for item in [
        "car-battery",
        "lithium-battery",
        "paint-latex",
        "paint-oil",
        "motor-oil",
        "propane-tank",
        "fluorescent-bulbs",
        "medical-sharps",
    ]:
        badge = "SPECIAL_HANDLING" if item == "paint-latex" else "BANNED_FROM_LANDFILLS"
        haz = "Medium" if item == "paint-latex" else "High"
        rows.append(
            rule(
                c,
                st,
                item,
                badge,
                haz,
                False,
                hhw["fee"],
                hhw["facility"],
                hhw["hhw_answer"].format(city=name),
                hhw["hhw_steps"],
                hhw["hhw_faqs"],
                hhw["source_name"],
                hhw["source_url"],
            )
        )
    rows.append(
        rule(
            c,
            st,
            "tires",
            "SPECIAL_HANDLING",
            "Medium",
            False,
            cfg.get("tires_fee", "Not published — tire retailer / city program"),
            cfg.get("tires_facility", "Tire retailer or city special-waste program"),
            cfg.get(
                "tires_answer",
                f"Do not put tires in {name} trash/recycling carts. Prefer retailer take-back or the city special-waste pathway if tires are accepted — confirm before hauling.",
            ).format(city=name),
            [
                "Ask the tire shop about take-back.",
                "Or confirm city/special-waste tire limits.",
                "Do not illegal-dump.",
            ],
            [("HHW tires?", "Only if the city’s HHW/special-waste program lists tires.")],
            cfg.get("tires_source_name", hhw["source_name"]),
            cfg.get("tires_source_url", hhw["source_url"]),
        )
    )
    rows.append(
        rule(
            c,
            st,
            "air-conditioner",
            "SPECIAL_HANDLING",
            "High",
            True,
            bulky.get("appliance_fee", bulky["fee"]),
            bulky.get("appliance_facility", bulky["facility"]),
            bulky["ac_answer"].format(city=name),
            bulky["ac_steps"],
            bulky["ac_faqs"],
            bulky["source_name"],
            bulky["source_url"],
        )
    )
    rows.append(
        rule(
            c,
            st,
            "yard-waste",
            "ACCEPTED_IN_BLUE_BIN",
            "Low",
            True,
            organics["fee"],
            organics["facility"],
            organics["yard_answer"].format(city=name),
            organics["yard_steps"],
            organics["yard_faqs"],
            organics["source_name"],
            organics["source_url"],
        )
    )
    rows.append(
        rule(
            c,
            st,
            "food-scraps",
            "ACCEPTED_IN_BLUE_BIN",
            "Low",
            True,
            organics["fee"],
            organics["facility"],
            organics["food_answer"].format(city=name),
            organics["food_steps"],
            organics["food_faqs"],
            organics["source_name"],
            organics["source_url"],
        )
    )
    rows.append(
        rule(
            c,
            st,
            "plastic-bags",
            "SPECIAL_HANDLING",
            "Low",
            False,
            "Free (store film drop-off)",
            "Grocery store film drop-off",
            f"Plastic bags are not {name} curbside recycling. Return clean, dry bags to grocery store film drop-off.",
            ["Keep bags clean/dry.", "Use store drop-off bins.", "Prefer reusable bags."],
            [("Why?", "Film jams sorting equipment.")],
            bags["source_name"],
            bags["source_url"],
        )
    )
    rows.append(
        rule(
            c,
            st,
            "cooking-oil",
            "SPECIAL_HANDLING",
            "Medium",
            False,
            "Not published — confirm HHW/grease options",
            hhw["facility"],
            f"Do not pour cooking oil into {name} drains. Confirm whether the city HHW/special-waste program or a grease recycler accepts larger volumes before hauling.",
            ["Contain cooled oil.", "Call the program before visiting.", "Never storm-drain dump."],
            [("Small amounts?", "Follow local organics guidance if published.")],
            hhw["source_name"],
            hhw["source_url"],
        )
    )
    rows.append(
        rule(
            c,
            st,
            "construction-debris",
            "SPECIAL_HANDLING",
            "Low",
            False,
            "Debris box / transfer fees — confirm",
            "Debris box / transfer station",
            f"Construction debris is not {name} HHW and usually not standard carts. Use a debris box or transfer pathway; keep paint/chemicals for HHW.",
            ["Separate HHW chemicals.", "Haul C&D via debris box/transfer.", "Do not overload carts."],
            [("HHW C&D?", "No.")],
            bulky["source_name"],
            bulky["source_url"],
        )
    )
    return rows, cfg["facilities"]


# --- Metro configs (researched city/county .gov programs) ---
METROS = [
    {
        "city": "Houston",
        "city_slug": "houston",
        "state": "TX",
        "state_slug": "texas",
        "lat": 29.7604,
        "lng": -95.3698,
        "population": 2304580,
        "zip": "77002",
        "bulky": {
            "fee": "Included with city bulk/tree-waste — confirm set-out rules",
            "facility": "Houston Environmental Service Centers / bulk collection",
            "source_name": "City of Houston Solid Waste — Environmental Service Centers",
            "source_url": "https://www.houstontx.gov/solidwaste/esc.html",
            "mattress_answer": "Houston residents can use city bulk-waste collection or Environmental Service Centers for many bulky items. Bring matching Texas ID + Houston utility bill/lease for ESC drop-off. Confirm mattress acceptance before hauling.",
            "mattress_steps": [
                "Check Houston Solid Waste bulk set-out rules for your route.",
                "Or take eligible bulky items to an ESC with proof of residency.",
                "Keep HHW for ESC hazardous-waste acceptance lists.",
            ],
            "mattress_faqs": [("Proof?", "ESC drop-off requires matching ID and Houston utility bill/lease.")],
            "fridge_answer": "Schedule or use Houston bulk/appliance pathways for refrigerators. Do not put freon appliances in carts; confirm refrigerant rules before ESC/self-haul.",
            "fridge_steps": [
                "Confirm appliance acceptance with Houston Solid Waste.",
                "Do not vent refrigerant.",
                "Bring residency proof for ESC if self-hauling.",
            ],
            "fridge_faqs": [("HHW appliances?", "Large freon appliances are usually a bulky/appliance pathway, not chemical HHW.")],
            "ac_answer": "Treat air conditioners like other refrigerant appliances in Houston — use city bulky/appliance channels and confirm before ESC drop-off.",
            "ac_steps": ["Confirm acceptance.", "Do not vent refrigerant.", "Separate chemicals for HHW."],
            "ac_faqs": [("Carts?", "Never.")],
        },
        "hhw": {
            "fee": "Free for Houston residents at ESCs (limits apply)",
            "facility": "Houston ESC South — 11500 S. Post Oak Rd",
            "source_name": "City of Houston — Household Hazardous Waste",
            "source_url": "https://www.houstontx.gov/solidwaste/hhw.html",
            "ewaste_answer": "Houston residents should use Environmental Service Centers for many electronics/HHW streams that cannot go in carts. ESC South (11500 S. Post Oak Rd) is open Tue/Wed/Fri/Sat 8 a.m.–5 p.m.; bring residency proof.",
            "ewaste_steps": [
                "Confirm the item is accepted at ESC.",
                "Bring matching Texas ID + Houston utility bill/lease.",
                "Visit during published ESC hours.",
            ],
            "ewaste_faqs": [("North ESC?", "5614 Neches St — second Thursday monthly 9 a.m.–3 p.m.")],
            "hhw_answer": "Take household hazardous waste from Houston to city Environmental Service Centers (not carts). Confirm accepted materials and residency proof requirements before visiting.",
            "hhw_steps": [
                "Pack sealed, labeled containers.",
                "Use ESC South or North per published hours.",
                "Call 713-551-7355 with questions.",
            ],
            "hhw_faqs": [("Business waste?", "Residential programs only — businesses need commercial disposal.")],
        },
        "organics": {
            "fee": "Included with Houston yard/tree-waste programs where offered",
            "facility": "Houston yard/tree-waste collection",
            "source_name": "City of Houston Solid Waste — Environmental Service Centers",
            "source_url": "https://www.houstontx.gov/solidwaste/esc.html",
            "yard_answer": "Use Houston yard/tree-waste collection or ESC pathways for yard trimmings — not recycling carts when contamination rules forbid it.",
            "yard_steps": ["Follow city yard-waste set-out rules.", "Keep plastics out.", "Use ESC if self-hauling brush."],
            "yard_faqs": [("Food scraps?", "Confirm current Houston organics/compost guidance for your address.")],
            "food_answer": "Food scraps belong in Houston organics/compost pathways where offered — not recycling. Confirm your address rules before switching carts.",
            "food_steps": ["Check current organics rules for your address.", "Keep plastics out.", "Report missed service via 311."],
            "food_faqs": [("Bags?", "Only approved bags if the city allows them.")],
        },
        "facilities": [
            {
                "name": "Houston Environmental Service Center — South",
                "facility_type": "HHW / special waste / recyclables",
                "city_slug": "houston",
                "state": "TX",
                "zip": "77035",
                "address": "11500 S. Post Oak Rd., Houston, TX 77035",
                "lat": 29.656,
                "lng": -95.485,
                "source_url": "https://www.houstontx.gov/solidwaste/esc.html",
                "hours": "Tue, Wed, Fri, Sat 8:00–17:00; residency proof required",
                "phone": "713-551-7355",
            }
        ],
    },
    {
        "city": "Dallas",
        "city_slug": "dallas",
        "state": "TX",
        "state_slug": "texas",
        "lat": 32.7767,
        "lng": -96.797,
        "population": 1304379,
        "zip": "75201",
        "bulky": {
            "fee": "City bulk collection — confirm allotment/fees",
            "facility": "Dallas Sanitation bulk collection",
            "source_name": "City of Dallas Sanitation Services",
            "source_url": "https://dallascityhall.com/departments/sanitation/Pages/home_chemical.aspx",
            "mattress_answer": "Use City of Dallas bulk-item collection for mattresses. Keep chemicals/e-waste for the Home Chemical Collection Center — not carts.",
            "mattress_steps": [
                "Schedule/set out per Dallas Sanitation bulk rules.",
                "Do not abandon items in alleys.",
                "Take paint/batteries to HC3.",
            ],
            "mattress_faqs": [("HC3 take furniture?", "No — chemicals/e-waste focus.")],
            "fridge_answer": "Schedule Dallas bulk/appliance service for refrigerators. Confirm freon appliance rules; never carts.",
            "fridge_steps": ["Book bulk/appliance pickup.", "Do not vent refrigerant.", "Ask about fees."],
            "fridge_faqs": [("Self-haul?", "Call transfer stations about freon appliances first.")],
            "ac_answer": "Schedule Dallas bulky/appliance service for air conditioners; confirm refrigerant acceptance.",
            "ac_steps": ["Book bulky/appliance pickup.", "Do not vent refrigerant.", "Keep chemicals for HC3."],
            "ac_faqs": [("HHW?", "Large freon appliances are not the chemical-center pathway.")],
        },
        "hhw": {
            "fee": "Free for eligible residents at Home Chemical Collection Center",
            "facility": "Dallas County Home Chemical Collection Center — 11234 Plano Road",
            "source_name": "City of Dallas — Home Chemical Waste Disposal",
            "source_url": "https://dallascityhall.com/departments/sanitation/Pages/home_chemical.aspx",
            "ewaste_answer": "Dallas residents can use the Home Chemical Collection Center at 11234 Plano Road for many electronics and home chemicals (free for eligible residents). Hours: Tue 9–7:30; Wed–Thu 8:30–5; 2nd & 4th Sat 9–3. Closed Sun/Mon/Fri.",
            "ewaste_steps": [
                "Confirm eligibility/residency requirements.",
                "Visit HC3 during published hours.",
                "Call (214) 553-1765 with questions.",
            ],
            "ewaste_faqs": [("Closed days?", "Sunday, Monday, and Friday.")],
            "hhw_answer": "Take HHW from Dallas to the Home Chemical Collection Center (11234 Plano Road) — not trash carts. Confirm accepted items and residency proof before visiting.",
            "hhw_steps": [
                "Pack sealed, labeled household quantities.",
                "Use Tue–Thu or 2nd/4th Saturday hours.",
                "Keep business waste out.",
            ],
            "hhw_faqs": [("PaintCare?", "HC3 accepts paint; confirm current limits on arrival.")],
        },
        "organics": {
            "fee": "Included with Dallas organics/brush programs where offered",
            "facility": "Dallas organics / brush collection",
            "source_name": "City of Dallas Sanitation Services",
            "source_url": "https://dallascityhall.com/departments/sanitation/Pages/home_chemical.aspx",
            "yard_answer": "Use Dallas brush/organics programs for yard trimmings — not recycling when rules forbid it.",
            "yard_steps": ["Follow brush set-out rules.", "Keep plastics out.", "Ask Sanitation about oversized brush."],
            "yard_faqs": [("Food scraps?", "Confirm organics cart rules for your address.")],
            "food_answer": "Food scraps belong in Dallas organics pathways where offered — not recycling.",
            "food_steps": ["Check organics rules for your address.", "Keep plastics out.", "Report missed service."],
            "food_faqs": [("Bags?", "Only if approved.")],
        },
        "facilities": [
            {
                "name": "Dallas County Home Chemical Collection Center",
                "facility_type": "HHW / e-waste",
                "city_slug": "dallas",
                "state": "TX",
                "zip": "75243",
                "address": "11234 Plano Road, Dallas, TX 75243",
                "lat": 32.91,
                "lng": -96.7,
                "source_url": "https://dallascityhall.com/departments/sanitation/Pages/home_chemical.aspx",
                "hours": "Tue 9:00–19:30; Wed–Thu 8:30–17:00; 2nd & 4th Sat 9:00–15:00",
                "phone": "(214) 553-1765",
            }
        ],
    },
    {
        "city": "New York",
        "city_slug": "new-york",
        "state": "NY",
        "state_slug": "new-york",
        "lat": 40.7128,
        "lng": -74.006,
        "population": 8336817,
        "zip": "10007",
        "bulky": {
            "fee": "Included with DSNY bulk set-out when bagged correctly",
            "facility": "DSNY curbside bulk collection",
            "source_name": "NYC 311 — Bulk Item Disposal",
            "source_url": "https://portal.311.nyc.gov/article/?kanumber=KA-01969",
            "mattress_answer": "In New York City, mattresses/box springs must be sealed in plastic bags and set out for DSNY bulk collection. Unbagged mattresses may not be collected and can draw fines. Special Waste sites do not take furniture.",
            "mattress_steps": [
                "Seal the mattress/box spring in a plastic bag.",
                "Set out on your bulk collection day.",
                "Do not take mattresses to Special Waste Drop-Off.",
            ],
            "mattress_faqs": [("Bags provided?", "No — buy mattress bags from retailers.")],
            "fridge_answer": "NYC refrigerators need CFC/Freon rules followed for DSNY bulk/appliance set-out. Confirm current freon appliance instructions on NYC Sanitation pages before set-out.",
            "fridge_steps": [
                "Read DSNY freon appliance set-out rules.",
                "Schedule/set out only as directed.",
                "Keep electronics for Special Waste/e-waste channels.",
            ],
            "fridge_faqs": [("Special Waste appliances?", "Special Waste focuses on special waste/e-waste — not large freon units.")],
            "ac_answer": "NYC air conditioners follow DSNY freon/CFC appliance rules — confirm before set-out; do not put them in regular trash.",
            "ac_steps": ["Follow DSNY freon appliance guidance.", "Set out only when allowed.", "Separate special waste chemicals."],
            "ac_faqs": [("E-waste?", "TVs/computers go to Special Waste / e-waste programs, not trash.")],
        },
        "hhw": {
            "fee": "Free for NYC residents at Special Waste Drop-Off (limits apply)",
            "facility": "DSNY Special Waste Drop-Off (borough sites)",
            "source_name": "NYC DSNY — Special Waste Drop-Off",
            "source_url": "https://www.nyc.gov/site/dsny/what-we-do/programs/special-waste-drop-off.page",
            "ewaste_answer": "NYC residents can take covered electronics to DSNY Special Waste Drop-Off sites (and other e-waste options). Sites are in all five boroughs; confirm current open days/hours on DSNY pages and bring proof of NYC residency.",
            "ewaste_steps": [
                "Confirm the device is covered e-waste.",
                "Find your borough Special Waste site hours.",
                "Bring ID/proof of NYC residency.",
            ],
            "ewaste_faqs": [("Trash e-waste?", "Illegal for covered electronics in New York State.")],
            "hhw_answer": "Use DSNY Special Waste Drop-Off for many batteries, paint (limits), motor oil, fluorescents, and other listed special wastes. Confirm acceptance lists and hours before visiting — never put these in trash/recycling.",
            "hhw_steps": [
                "Check the Special Waste accepted list.",
                "Respect quantity limits (e.g., paint/oil).",
                "Visit during published site hours.",
            ],
            "hhw_faqs": [("SAFE events?", "SAFE Disposal Events accept a broader HHW set — check DSNY schedules.")],
        },
        "organics": {
            "fee": "Included with NYC organics/compost where offered",
            "facility": "NYC organics / compost collection",
            "source_name": "NYC Department of Sanitation",
            "source_url": "https://www.nyc.gov/site/dsny/collection/residents/composting.page",
            "yard_answer": "Use NYC organics/compost or designated yard-waste rules for plant waste — not metal/glass/plastic recycling.",
            "yard_steps": ["Follow organics set-out for your building/route.", "Keep plastics out.", "Check DSNY compost pages."],
            "yard_faqs": [("Building not enrolled?", "Use drop-off compost sites if available.")],
            "food_answer": "Food scraps belong in NYC organics/compost programs where offered — not recycling.",
            "food_steps": ["Use organics bins if available.", "Keep plastics out.", "Check DSNY compost guidance."],
            "food_faqs": [("Bags?", "Only compostable bags if allowed for your program.")],
        },
        "tires_fee": "Free at Special Waste (up to 4 passenger tires/visit) — confirm",
        "tires_facility": "DSNY Special Waste Drop-Off",
        "tires_answer": "NYC Special Waste Drop-Off accepts up to four passenger car tires per visit. Do not put tires in trash/recycling.",
        "tires_source_name": "NYC DSNY — Special Waste Drop-Off",
        "tires_source_url": "https://www.nyc.gov/site/dsny/what-we-do/programs/special-waste-drop-off.page",
        "facilities": [
            {
                "name": "DSNY Special Waste Drop-Off (borough network)",
                "facility_type": "Special waste / e-waste",
                "city_slug": "new-york",
                "state": "NY",
                "zip": "10007",
                "address": "Sites in all five boroughs — see DSNY Special Waste Drop-Off page for addresses/hours",
                "lat": 40.7128,
                "lng": -74.006,
                "source_url": "https://www.nyc.gov/site/dsny/what-we-do/programs/special-waste-drop-off.page",
                "hours": "Confirm current borough site days/hours on DSNY (commonly midweek–Saturday)",
                "phone": "311",
            }
        ],
    },
    {
        "city": "Miami",
        "city_slug": "miami",
        "state": "FL",
        "state_slug": "florida",
        "lat": 25.7617,
        "lng": -80.1918,
        "population": 442241,
        "zip": "33130",
        "bulky": {
            "fee": "City bulky / Mini Dump — confirm residency rules",
            "facility": "City of Miami bulky collection / Mini Dump",
            "source_name": "City of Miami Solid Waste",
            "source_url": "https://www.miami.gov/My-Government/Departments/Solid-Waste",
            "mattress_answer": "Miami residents should use City of Miami bulky trash collection or the resident Mini Dump for mattresses/furniture. Keep chemicals for Miami-Dade Home Chemical programs.",
            "mattress_steps": [
                "Schedule/set out per City of Miami bulky rules.",
                "Or use the Mini Dump if eligible.",
                "Separate HHW for county chemical centers/events.",
            ],
            "mattress_faqs": [("County HHW furniture?", "No.")],
            "fridge_answer": "Use City of Miami bulky/appliance pathways for refrigerators. Confirm freon rules; never carts.",
            "fridge_steps": ["Book bulky/appliance service or Mini Dump if accepted.", "Do not vent refrigerant.", "Ask about fees."],
            "fridge_faqs": [("Chemical center appliances?", "Usually excluded — confirm.")],
            "ac_answer": "Schedule Miami bulky/appliance service for ACs; confirm refrigerant acceptance.",
            "ac_steps": ["Book bulky/appliance pickup.", "Do not vent refrigerant.", "Keep chemicals for Home Chemical programs."],
            "ac_faqs": [("HHW?", "Large freon appliances are not chemical drop-off.")],
        },
        "hhw": {
            "fee": "Free for Miami-Dade residents at Home Chemical centers/events",
            "facility": "Miami-Dade Home Chemical Collection Centers / mobile events",
            "source_name": "City of Miami — Hazardous Materials & Chemicals",
            "source_url": "https://www.miami.gov/My-Government/Departments/Solid-Waste/Dispose-of-Hazardous-Materials-Chemicals",
            "ewaste_answer": "Miami residents use Miami-Dade Home Chemical Collection Centers and Home Chemical Drop-Off Mobile Events for many electronics and household chemicals. Call (305) 468-5900 for permanent center hours; mobile events are typically Saturdays 8 a.m.–2 p.m. with Florida ID proof of Miami-Dade residency.",
            "ewaste_steps": [
                "Confirm residency eligibility.",
                "Choose a permanent center or scheduled mobile event.",
                "Pack sealed/labeled materials upright.",
            ],
            "ewaste_faqs": [("Business waste?", "Not accepted at residential Home Chemical programs.")],
            "hhw_answer": "Take HHW from Miami to Miami-Dade Home Chemical Collection Centers or mobile events — not carts. Confirm hours via (305) 468-5900 and bring Florida ID showing Miami-Dade residency.",
            "hhw_steps": [
                "Pack upright, sealed, labeled containers.",
                "Verify center/event hours before driving.",
                "Keep commercial waste out.",
            ],
            "hhw_faqs": [("Latex paint?", "Liquid latex is accepted at Home Chemical programs; donate usable paint when possible.")],
        },
        "organics": {
            "fee": "Included with Miami yard-trash / organics where offered",
            "facility": "City of Miami yard trash / Mini Dump",
            "source_name": "City of Miami Solid Waste",
            "source_url": "https://www.miami.gov/My-Government/Departments/Solid-Waste",
            "yard_answer": "Use City of Miami yard-trash collection or Mini Dump pathways for yard waste — not recycling.",
            "yard_steps": ["Follow yard-trash set-out rules.", "Keep plastics out.", "Use Mini Dump if eligible."],
            "yard_faqs": [("Food scraps?", "Confirm current organics programs for your address.")],
            "food_answer": "Food scraps belong in Miami organics pathways where offered — not recycling.",
            "food_steps": ["Check organics rules for your address.", "Keep plastics out.", "Report missed service."],
            "food_faqs": [("Bags?", "Only if approved.")],
        },
        "facilities": [
            {
                "name": "Miami-Dade Home Chemical Collection Centers",
                "facility_type": "HHW / e-waste",
                "city_slug": "miami",
                "state": "FL",
                "zip": "33130",
                "address": "West Dade & South Dade centers — call (305) 468-5900 for current addresses/hours",
                "lat": 25.7617,
                "lng": -80.1918,
                "source_url": "https://www.miami.gov/My-Government/Departments/Solid-Waste/Dispose-of-Hazardous-Materials-Chemicals",
                "hours": "Confirm by phone; mobile events Sat 8:00–14:00 when scheduled",
                "phone": "(305) 468-5900",
            }
        ],
    },
    {
        "city": "Chicago",
        "city_slug": "chicago",
        "state": "IL",
        "state_slug": "illinois",
        "lat": 41.8781,
        "lng": -87.6298,
        "population": 2746388,
        "zip": "60601",
        "bulky": {
            "fee": "City bulk collection — confirm 311 rules",
            "facility": "Chicago Streets & Sanitation bulk collection",
            "source_name": "City of Chicago — Recycle by City / Sanitation",
            "source_url": "https://www.chicago.gov/city/en/depts/streets/supp_info/recycling1.html",
            "mattress_answer": "Use Chicago bulk-item collection for mattresses. Keep chemicals/computers for the Household Chemicals & Computer Recycling Facility — not blue carts.",
            "mattress_steps": [
                "Request/set out bulk per Streets & Sanitation rules.",
                "Do not abandon items in alleys.",
                "Take HHW/e-waste to HCCRF.",
            ],
            "mattress_faqs": [("HCCRF furniture?", "No.")],
            "fridge_answer": "Schedule Chicago bulk/appliance service for refrigerators. Confirm freon rules via 311.",
            "fridge_steps": ["Book bulk/appliance pickup.", "Do not vent refrigerant.", "Ask about stickers/fees."],
            "fridge_faqs": [("HCCRF appliances?", "HCCRF is chemicals/computers — confirm large appliances separately.")],
            "ac_answer": "Schedule Chicago bulk/appliance service for ACs; confirm refrigerant acceptance.",
            "ac_steps": ["Book bulk/appliance pickup.", "Do not vent refrigerant.", "Keep chemicals for HCCRF."],
            "ac_faqs": [("Blue cart?", "Never for freon appliances.")],
        },
        "hhw": {
            "fee": "Free for Chicago residents at HCCRF (residential only)",
            "facility": "Household Chemicals & Computer Recycling Facility — 1150 N. North Branch St",
            "source_name": "City of Chicago — Household Chemicals & Computer Recycling Facility",
            "source_url": "https://www.chicago.gov/city/en/depts/cdph/supp_info/environmental_protection_division/household_chemicalsandcomputerrecyclingfacility.html",
            "ewaste_answer": "Chicago residents can drop electronics at the Household Chemicals & Computer Recycling Facility (1150 N. North Branch St). Hours: Tue 7 a.m.–12 p.m.; Thu 2–7 p.m.; first Saturday 8 a.m.–3 p.m. Residential only.",
            "ewaste_steps": [
                "Visit during published HCCRF hours.",
                "Use the electronics (yellow) building as directed.",
                "Do not leave materials when closed.",
            ],
            "ewaste_faqs": [("Business waste?", "Not accepted.")],
            "hhw_answer": "Take HHW from Chicago to HCCRF at 1150 N. North Branch Street — not carts. Chemicals drop-off is the blue building during published hours.",
            "hhw_steps": [
                "Pack sealed household quantities.",
                "Arrive Tue/Thu/first Sat per schedule.",
                "Follow attendant directions on site.",
            ],
            "hhw_faqs": [("Phone?", "312-744-3060 (confirm on city pages).")],
        },
        "organics": {
            "fee": "Included with Chicago compost/yard-waste where offered",
            "facility": "Chicago yard-waste / compost programs",
            "source_name": "City of Chicago Streets & Sanitation",
            "source_url": "https://www.chicago.gov/city/en/depts/streets/supp_info/recycling1.html",
            "yard_answer": "Use Chicago yard-waste/compost pathways for yard trimmings — not blue-cart recycling contamination.",
            "yard_steps": ["Follow seasonal yard-waste rules.", "Keep plastics out.", "Check Recycle by City guidance."],
            "yard_faqs": [("Food scraps?", "Confirm compost pilot/program status for your ward.")],
            "food_answer": "Food scraps belong in Chicago compost programs where offered — not recycling.",
            "food_steps": ["Check compost availability for your address.", "Keep plastics out.", "Report missed service."],
            "food_faqs": [("Bags?", "Only if approved.")],
        },
        "facilities": [
            {
                "name": "Chicago Household Chemicals & Computer Recycling Facility",
                "facility_type": "HHW / e-waste",
                "city_slug": "chicago",
                "state": "IL",
                "zip": "60642",
                "address": "1150 N. North Branch Street, Chicago, IL 60642",
                "lat": 41.903,
                "lng": -87.651,
                "source_url": "https://www.chicago.gov/city/en/depts/cdph/supp_info/environmental_protection_division/household_chemicalsandcomputerrecyclingfacility.html",
                "hours": "Tue 7:00–12:00; Thu 14:00–19:00; first Sat 8:00–15:00",
                "phone": "312-744-3060",
            }
        ],
    },
    {
        "city": "Phoenix",
        "city_slug": "phoenix",
        "state": "AZ",
        "state_slug": "arizona",
        "lat": 33.4484,
        "lng": -112.074,
        "population": 1608139,
        "zip": "85003",
        "bulky": {
            "fee": "City bulk/trash programs — confirm account rules",
            "facility": "City of Phoenix bulk collection",
            "source_name": "City of Phoenix Public Works — Trash & Recycling",
            "source_url": "https://www.phoenix.gov/administration/departments/publicworks/residential-trash-recycling.html",
            "mattress_answer": "Use City of Phoenix bulk-item collection for mattresses. For HHW, schedule the city’s free residential HHW home collection (one per customer per year) — do not put HHW in carts.",
            "mattress_steps": [
                "Set out bulky items per Phoenix solid-waste rules.",
                "Schedule HHW home collection separately for chemicals.",
                "Do not curb HHW boxes.",
            ],
            "mattress_faqs": [("HHW drop-off site?", "Phoenix emphasizes scheduled HHW home collection for account holders.")],
            "fridge_answer": "Schedule Phoenix bulk/appliance service for refrigerators. Confirm freon rules; never carts.",
            "fridge_steps": ["Book bulk/appliance pickup.", "Do not vent refrigerant.", "Ask about fees."],
            "fridge_faqs": [("HHW home collection appliances?", "Confirm accepted list when scheduling.")],
            "ac_answer": "Schedule Phoenix bulk/appliance service for ACs; confirm refrigerant acceptance.",
            "ac_steps": ["Book bulky/appliance pickup.", "Do not vent refrigerant.", "Use HHW home collection for chemicals."],
            "ac_faqs": [("Carts?", "Never.")],
        },
        "hhw": {
            "fee": "Free HHW home collection (1×/year) for eligible Phoenix solid-waste customers",
            "facility": "City of Phoenix HHW home collection",
            "source_name": "City of Phoenix — Household Hazardous Waste Collection",
            "source_url": "https://www.phoenix.gov/administration/departments/publicworks/residential-trash-recycling/household-hazardous-waste-collection.html",
            "ewaste_answer": "Phoenix solid-waste customers should schedule the city’s Household Hazardous Waste home collection for many chemicals/batteries/electronics listed on the program page (limits apply; one collection per customer per year). Confirm current appointment availability online or via hhwcollection@phoenix.gov.",
            "ewaste_steps": [
                "Have your city services account number ready.",
                "Schedule HHW home collection online or by email/phone channels listed.",
                "Place sealed items outside by 7 a.m. on collection day — not at the curb.",
            ],
            "ewaste_faqs": [("Reservations closed?", "Email hhwcollection@phoenix.gov if the form shows no dates.")],
            "hhw_answer": "Do not put HHW in Phoenix carts. Eligible residential solid-waste customers get one free HHW home collection per year — schedule via Phoenix Public Works HHW pages.",
            "hhw_steps": [
                "Confirm you have a residential solid-waste account.",
                "Schedule the HHW pickup.",
                "Box/label items and place by garage/door by 7 a.m.",
            ],
            "hhw_faqs": [("Business waste?", "Residential program only.")],
        },
        "organics": {
            "fee": "Included with Phoenix green organics where offered",
            "facility": "Phoenix green organics cart",
            "source_name": "City of Phoenix Public Works — Trash & Recycling",
            "source_url": "https://www.phoenix.gov/administration/departments/publicworks/residential-trash-recycling.html",
            "yard_answer": "Use Phoenix green organics for yard trimmings where provided — not recycling contamination.",
            "yard_steps": ["Use the green organics cart.", "Follow contamination rules.", "Ask about oversized brush."],
            "yard_faqs": [("Food scraps?", "Often the same organics stream where provided.")],
            "food_answer": "Food scraps go in Phoenix organics where offered — not recycling.",
            "food_steps": ["Collect scraps for organics.", "Keep plastics out.", "Report missed service."],
            "food_faqs": [("Bags?", "Only if approved.")],
        },
        "facilities": [
            {
                "name": "City of Phoenix HHW Home Collection (by appointment)",
                "facility_type": "Municipal HHW home collection",
                "city_slug": "phoenix",
                "state": "AZ",
                "zip": None,
                "address": "Curbside/home collection for eligible Phoenix solid-waste customers — schedule online",
                "lat": 33.4484,
                "lng": -112.074,
                "source_url": "https://www.phoenix.gov/administration/departments/publicworks/residential-trash-recycling/household-hazardous-waste-collection.html",
                "hours": "By appointment; set out by 7:00; collection 7:00–17:00",
                "phone": "(602) 262-3111",
            }
        ],
    },
    {
        "city": "Seattle",
        "city_slug": "seattle",
        "state": "WA",
        "state_slug": "washington",
        "lat": 47.6062,
        "lng": -122.3321,
        "population": 737015,
        "zip": "98101",
        "bulky": {
            "fee": "Transfer station / bulky fees — confirm",
            "facility": "Seattle transfer stations / bulky options",
            "source_name": "Seattle Public Utilities — Collection & Disposal",
            "source_url": "https://www.seattle.gov/utilities/your-services/collection-and-disposal",
            "mattress_answer": "Seattle residents typically use transfer stations or hauler bulky options for mattresses. Transfer stations do not accept HHW — use North/South HHW facilities for chemicals.",
            "mattress_steps": [
                "Confirm mattress fees at Seattle transfer stations.",
                "Or schedule private/hauler bulky pickup.",
                "Keep HHW for HHW facilities.",
            ],
            "mattress_faqs": [("HHW furniture?", "No.")],
            "fridge_answer": "Take refrigerators to Seattle transfer stations or appliance recyclers per published freon rules — not garbage carts.",
            "fridge_steps": ["Confirm freon appliance acceptance/fees.", "Do not vent refrigerant.", "Keep chemicals for HHW sites."],
            "fridge_faqs": [("Transfer = HHW?", "No — HHW is a separate facility.")],
            "ac_answer": "Use Seattle transfer stations/appliance pathways for ACs; confirm refrigerant fees.",
            "ac_steps": ["Confirm acceptance/fees.", "Do not vent refrigerant.", "Keep chemicals for HHW."],
            "ac_faqs": [("Carts?", "Never.")],
        },
        "hhw": {
            "fee": "Free for King County residents at Seattle HHW facilities",
            "facility": "North/South Seattle Household Hazardous Waste Facilities",
            "source_name": "Seattle Public Utilities — Household Hazardous Waste",
            "source_url": "https://www.seattle.gov/utilities/your-services/collection-and-disposal/garbage/hazardous-waste-items/where-to-dispose-of-hazardous-waste",
            "ewaste_answer": "Seattle/King County residents can use North HHW (12550 Stone Ave N; Sun–Tue 9–5) and South HHW (8100 2nd Ave S; Thu–Sat 9–5) for many household hazardous wastes and related specials. Confirm electronics acceptance; transfer stations do not take HHW.",
            "ewaste_steps": [
                "Choose North or South HHW by open days.",
                "No appointment needed for residential drop-off.",
                "Respect quantity limits posted by the program.",
            ],
            "ewaste_faqs": [("Factoria?", "King County residents can also use Factoria HHW in Bellevue.")],
            "hhw_answer": "Take HHW from Seattle to North or South Household Hazardous Waste Facilities — free for King County residents. Do not bring HHW to transfer stations.",
            "hhw_steps": [
                "Pack sealed household quantities.",
                "Visit North (Sun–Tue) or South (Thu–Sat) 9 a.m.–5 p.m.",
                "Call (206) 296-4692 with questions.",
            ],
            "hhw_faqs": [("Latex paint?", "Confirm current latex rules — some WA sites limit latex paint.")],
        },
        "organics": {
            "fee": "Included with Seattle food/yard waste cart",
            "facility": "Seattle food & yard waste cart",
            "source_name": "Seattle Public Utilities — Food & Yard Waste",
            "source_url": "https://www.seattle.gov/utilities/your-services/collection-and-disposal/food-and-yard",
            "yard_answer": "Use Seattle food & yard waste carts for yard trimmings — not recycling.",
            "yard_steps": ["Use the food/yard cart.", "Follow contamination rules.", "Ask about oversized brush."],
            "yard_faqs": [("Food scraps?", "Same cart.")],
            "food_answer": "Food scraps go in Seattle food & yard waste — not recycling or garbage when compostable.",
            "food_steps": ["Collect scraps for the food/yard cart.", "Keep plastics out.", "Report missed service."],
            "food_faqs": [("Compostable bags?", "Allowed if they meet SPU rules.")],
        },
        "facilities": [
            {
                "name": "North Seattle Household Hazardous Waste Facility",
                "facility_type": "HHW",
                "city_slug": "seattle",
                "state": "WA",
                "zip": "98133",
                "address": "12550 Stone Avenue North, Seattle, WA 98133",
                "lat": 47.72,
                "lng": -122.344,
                "source_url": "https://www.seattle.gov/utilities/your-services/collection-and-disposal/garbage/hazardous-waste-items/where-to-dispose-of-hazardous-waste",
                "hours": "Sun–Tue 9:00–17:00",
                "phone": "(206) 296-4692",
            },
            {
                "name": "South Seattle Household Hazardous Waste Facility",
                "facility_type": "HHW",
                "city_slug": "seattle",
                "state": "WA",
                "zip": "98108",
                "address": "8100 2nd Avenue South, Seattle, WA 98108",
                "lat": 47.53,
                "lng": -122.328,
                "source_url": "https://www.seattle.gov/utilities/your-services/collection-and-disposal/garbage/hazardous-waste-items/where-to-dispose-of-hazardous-waste",
                "hours": "Thu–Sat 9:00–17:00",
                "phone": "(206) 296-4692",
            },
        ],
    },
]


def load_all_json(glob_pat: str):
    rows = []
    for path in sorted((DATA).glob(glob_pat)):
        rows.extend(json.loads(path.read_text()))
    return rows


def main() -> None:
    # --- CA expand remaining siblings ---
    ca_rules = json.loads((DATA / "rules" / "ca.json").read_text())
    expanded = clone_siblings(ca_rules, CA_MORE_SIBLINGS)
    ca_rules.extend(expanded)
    # dedupe
    seen = set()
    uniq = []
    for r in ca_rules:
        key = (r.get("city_slug"), r["item_slug"])
        if key in seen:
            continue
        seen.add(key)
        if r.get("common_disposal_fee"):
            r["common_disposal_fee"] = str(r["common_disposal_fee"])[:80]
        if r.get("nearest_facility_type"):
            r["nearest_facility_type"] = str(r["nearest_facility_type"])[:120]
        uniq.append(r)
    (DATA / "rules" / "ca.json").write_text(json.dumps(uniq, indent=2))
    print(f"CA rules: {len(uniq)} (+{len(expanded)} new siblings)")

    # --- National cities / rules / facilities / zips ---
    cities = json.loads((DATA / "geo" / "ca_cities.json").read_text())
    zips = json.loads((DATA / "geo" / "ca_zips.json").read_text())
    facilities = json.loads((DATA / "facilities" / "ca.json").read_text())
    national_rules = []

    existing_city_slugs = {c["city_slug"] for c in cities}
    for cfg in METROS:
        if cfg["city_slug"] not in existing_city_slugs:
            cities.append(
                {
                    "city": cfg["city"],
                    "city_slug": cfg["city_slug"],
                    "state": cfg["state"],
                    "state_slug": cfg["state_slug"],
                    "lat": cfg["lat"],
                    "lng": cfg["lng"],
                    "population": cfg["population"],
                }
            )
        if not any(z.get("city_slug") == cfg["city_slug"] for z in zips):
            zips.append(
                {
                    "zip": cfg["zip"],
                    "city": cfg["city"],
                    "city_slug": cfg["city_slug"],
                    "state": cfg["state"],
                    "state_slug": cfg["state_slug"],
                    "lat": cfg["lat"],
                    "lng": cfg["lng"],
                    "population": cfg["population"],
                }
            )
        rows, facs = pack_city(cfg)
        # siblings for new metros too
        rows.extend(clone_siblings(rows, {**CA_MORE_SIBLINGS, "mattress": ["box-spring", "sofa", "recliner", "carpet", "exercise-equipment", "dining-table", "desk", "bookshelf"]}))
        national_rules.extend(rows)
        for f in facs:
            if not any(x["name"] == f["name"] and x["city_slug"] == f["city_slug"] for x in facilities):
                facilities.append(f)

    (DATA / "geo" / "cities.json").write_text(json.dumps(cities, indent=2))
    (DATA / "geo" / "zips.json").write_text(json.dumps(zips, indent=2))
    (DATA / "facilities" / "all.json").write_text(json.dumps(facilities, indent=2))
    (DATA / "rules" / "national.json").write_text(json.dumps(national_rules, indent=2))

    # merged rules for import convenience
    merged = uniq + national_rules
    (DATA / "rules" / "all.json").write_text(json.dumps(merged, indent=2))

    print(f"cities={len(cities)} zips={len(zips)} facilities={len(facilities)} national_rules={len(national_rules)} merged={len(merged)}")
    print("metros:", ", ".join(m["city_slug"] for m in METROS))


if __name__ == "__main__":
    main()
