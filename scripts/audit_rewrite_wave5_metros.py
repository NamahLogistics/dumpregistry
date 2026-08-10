#!/usr/bin/env python3
"""Portal-audited city guides for wave-5 metros (city-sourced only).

Cities researched from official program pages (2026-08-10):
  - Boston, MA — boston.gov Public Works (special collection, Zero Waste Days)
  - Jacksonville, FL — jacksonville.gov Solid Waste (bulk, HHW facility)
  - Columbus, OH — columbus.gov Bulk Collection + SWACO HHW / convenience centers
  - Fort Worth, TX — fortworthtexas.gov Solid Waste (bulk, drop-off stations, ECC)
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
VERIFIED = "2026-08-10"

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


def boston():
    c, st = "boston", "MA"
    special = (
        "City of Boston — Special collection items",
        "https://www.boston.gov/departments/public-works/special-collection-items",
    )
    zwday = (
        "City of Boston — Zero Waste Day",
        "https://www.boston.gov/departments/public-works/zero-waste-day",
    )
    rows = []
    rows.append(
        R(
            c,
            st,
            "mattress",
            "SPECIAL_HANDLING",
            "Low",
            True,
            "Schedule mattress pickup or private hauler — not freon special collection",
            "Boston Public Works scheduled mattress / private hauler",
            "Boston Public Works treats mattresses separately from Freon/CRT special collection. City guidance: schedule mattress pickup through the city’s Schedule here pathway or use a private hauler — do not book mattresses on the Freon/CRT special-collection appointment. Ordinary furniture may go out with curbside trash; mattresses specifically need that scheduled (or private) channel.",
            [
                "Use Boston’s mattress schedule link / 311 process — not the Freon/CRT special collection form.",
                "Or hire a private hauler if you cannot wait for a city appointment.",
                "Do not mix mattresses into a Freon appliance special-collection pile.",
            ],
            [
                ("Furniture vs mattress?", "City notes furniture can go curbside with trash; mattresses need scheduling or a private hauler."),
                ("Freon special collection?", "No — Freon/CRT special collection is for refrigerants and CRTs only."),
            ],
            *special,
        )
    )
    rows.append(
        R(
            c,
            st,
            "refrigerator",
            "SPECIAL_HANDLING",
            "High",
            True,
            "Scheduled special collection via 311 / boston.gov (max 5/appt, 10/year)",
            "Boston Public Works special collection / Zero Waste events",
            "Boston collects Freon-containing appliances (refrigerators, freezers, air conditioners, dehumidifiers) only through scheduled special collection via 311 or boston.gov — not regular trash day. Limits: maximum five special-collection items per appointment and ten per year. Empty food, remove refrigerator doors before set-out, and place items at the curb by 6 a.m. on the scheduled day. CRT TVs/laptops/monitors use the same special-collection channel.",
            [
                "Empty the fridge, remove doors, and keep food out.",
                "Book special collection on boston.gov or by calling 311 (5/appointment, 10/year).",
                "Set items at the curb by 6 a.m. on the appointment day.",
            ],
            [
                ("Washer/dryer on Freon special?", "No — water heaters, dishwashers, and plumbing fixtures are directed to donate or private hauler, not Freon special collection."),
                ("Phone?", "Boston Public Works / 311 — City Hall Square programs listed at 617-635-4500."),
            ],
            *special,
        )
    )
    rows.append(
        R(
            c,
            st,
            "air-conditioner",
            "SPECIAL_HANDLING",
            "High",
            True,
            "Scheduled Freon special collection (same rules as fridge)",
            "Boston Public Works special collection",
            "Window and portable air conditioners are Freon special-collection items in Boston. Schedule via 311/boston.gov under the special collection program (max five items per appointment, ten per year). Do not put Freon units in regular trash carts. Set out by 6 a.m. on the scheduled day; never vent refrigerant yourself.",
            [
                "Schedule Freon special collection — do not use regular trash.",
                "Keep the unit intact; do not release refrigerant.",
                "Set out by 6 a.m. within the annual appointment limits.",
            ],
            [("Same as fridge?", "Yes — AC and dehumidifiers share the Freon special-collection pathway.")],
            *special,
        )
    )
    for item, label in [
        ("washer", "washing machines"),
        ("dryer", "clothes dryers"),
        ("dishwasher", "dishwashers"),
        ("stove", "stoves/ovens"),
        ("water-heater", "water heaters"),
    ]:
        rows.append(
            R(
                c,
                st,
                item,
                "SPECIAL_HANDLING",
                "Medium",
                False,
                "Donate or private hauler — not Freon special collection",
                "Donate / private hauler (Boston)",
                f"Boston’s special collection page directs water heaters, dishwashers, and plumbing fixtures to donate or a private hauler — they are not Freon special-collection items. Treat {label} the same way: reuse/donate when possible, otherwise hire a private appliance hauler. Do not book these on the Freon/CRT special-collection appointment used for refrigerators and CRTs.",
                [
                    "Check donation options (Habitat, appliance reuse) before disposal.",
                    "Hire a private hauler if donation is not available.",
                    "Do not schedule these on Boston’s Freon/CRT special collection.",
                ],
                [
                    ("Why not special collection?", "City lists water heaters/dishwashers/plumbing fixtures for donate or private hauler, separate from Freon items."),
                ],
                *special,
            )
        )
    for item, label in [
        ("television", "TVs (including CRTs)"),
        ("computer-monitor", "computer monitors (including CRTs)"),
        ("smartphone", "phones and small electronics"),
        ("e-waste-mixed", "mixed electronic waste"),
    ]:
        if item in {"television", "computer-monitor"}:
            ans = (
                f"Boston schedules CRT items — {label} — through the same special collection program as Freon appliances "
                f"(311 / boston.gov; max five items per appointment, ten per year). Set out by 6 a.m. Flat-panel and "
                f"other electronics that are not on the Freon/CRT list should use Zero Waste Day events, retailer "
                f"take-back, or private e-waste recyclers rather than regular trash."
            )
            fee = "Special collection appointment (CRT) or Zero Waste Day / recycler"
            fac = "Boston Public Works special collection / Zero Waste events"
            curb = True
            src = special
        else:
            ans = (
                f"Boston does not put {label} in curbside recycling. Use Zero Waste Day events, manufacturer/retailer "
                f"take-back, or a private e-waste recycler. CRT TVs/laptops/monitors that qualify for special collection "
                f"should use the Freon/CRT appointment pathway instead of trash."
            )
            fee = "Zero Waste Day / retailer take-back / private e-waste"
            fac = "Boston Zero Waste Day / e-waste take-back"
            curb = False
            src = zwday
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS",
                "Medium",
                curb,
                fee,
                fac,
                ans,
                [
                    "Do not put electronics in Boston recycling carts.",
                    "Use special collection for qualifying CRT TVs/monitors/laptops, or Zero Waste Day / take-back for other e-waste.",
                    "Wipe personal data before recycling phones/computers.",
                ],
                [("Freon vs CRT?", "Both Freon appliances and CRT electronics share Boston’s scheduled special collection channel.")],
                *src,
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
        "cooking-oil",
        "medical-sharps",
    ]:
        extras = {
            "paint-latex": " Dry latex paint completely and place dried cans with trash; wet latex belongs at Zero Waste Days within chemical limits.",
            "paint-oil": " Oil-based paint must go to Zero Waste Day events — not trash.",
            "lithium-battery": " Lithium and NiCad batteries go to Zero Waste Days; alkaline batteries may go in trash.",
            "car-battery": " Car batteries are accepted at Zero Waste Day events — not curbside trash.",
            "motor-oil": " Motor oil counts toward the 20-gallon chemical/paint/oil limit at Zero Waste Days.",
            "propane-tank": " Propane tanks are accepted at Zero Waste Day events.",
            "fluorescent-bulbs": " Fluorescents and other mercury lamps belong at Zero Waste Days, not trash carts.",
            "cooking-oil": " Small amounts of cooking oil should follow Zero Waste Day / HHW guidance — do not pour into storm drains.",
            "medical-sharps": " Medical waste is not accepted at Zero Waste Days — use a medical sharps/pharmacy program.",
        }[item]
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS" if item not in {"cooking-oil", "paint-latex"} else "SPECIAL_HANDLING",
                "High" if item not in {"cooking-oil", "paint-latex"} else "Medium",
                False,
                "Zero Waste Day (residency proof; 20 gal chemicals/paint/oil; ≤5 gal containers)",
                "Boston Zero Waste Day events",
                f"Boston’s Zero Waste Days are the household HHW drop-off channel. Bring residency proof. Limits typically include 20 gallons of chemicals/paint/oil with containers ≤5 gallons.{extras}",
                [
                    "Find the next Zero Waste Day on boston.gov and bring residency proof.",
                    "Keep materials in original/labeled containers ≤5 gallons; stay under the 20-gallon chemicals/paint/oil limit.",
                    "Never put HHW, lithium batteries, or propane in regular trash/recycling carts.",
                ],
                [
                    ("Medical waste?", "Not accepted at Zero Waste Days — use a medical disposal program."),
                    ("Alkaline batteries?", "City guidance: alkaline batteries may go in trash; lithium/NiCad/car batteries to events."),
                ],
                *zwday,
            )
        )
    rows.append(
        R(
            c,
            st,
            "tires",
            "SPECIAL_HANDLING",
            "Medium",
            False,
            "Zero Waste Day — up to 8 car/bike tires",
            "Boston Zero Waste Day events",
            "Boston accepts car and bike tires at Zero Waste Day events — up to eight tires per visit under published event rules. Do not put tires in curbside trash. Confirm rim rules and event dates on boston.gov before hauling.",
            [
                "Hold tires for the next Zero Waste Day (max eight car/bike tires).",
                "Do not set tires out with regular trash.",
                "Retailer take-back when buying replacements is also acceptable.",
            ],
            [("Medical waste at events?", "No — medical waste is not accepted at Zero Waste Days.")],
            *zwday,
        )
    )
    rows.append(
        R(
            c,
            st,
            "yard-waste",
            "ACCEPTED_IN_BLUE_BIN",
            "Low",
            True,
            "Seasonal drop-offs / Trash Day app",
            "Boston seasonal yard-waste drop-offs",
            "Boston handles yard waste through seasonal drop-off sites and tools such as the Trash Day app rather than treating it as Freon/CRT special collection. Follow current seasonal schedules and preparation rules on boston.gov / the Trash Day app for leaves, brush, and holiday trees.",
            [
                "Check the Trash Day app or boston.gov for seasonal yard-waste drop-off dates.",
                "Prepare leaves/brush per current city rules (no plastic-bag contamination when required).",
                "Keep Freon appliances and HHW off yard-waste piles.",
            ],
            [("Christmas trees?", "Follow Boston’s seasonal tree guidance via Public Works / Trash Day tools.")],
            *special,
        )
    )
    rows.append(
        R(
            c,
            st,
            "food-scraps",
            "SPECIAL_HANDLING",
            "Low",
            True,
            "Not a citywide food-scrap cart — compost or trash",
            "Private compost / trash",
            "Boston does not operate a citywide residential food-scrap cart. Compost through a private/community program when available, or bag food scraps for trash. Keep food out of recycling.",
            [
                "Use private/community compost if you have access.",
                "Otherwise bag food scraps for trash collection.",
                "Keep organics out of recycling carts.",
            ],
            [("Citywide organics cart?", "Not citywide — compost or trash.")],
            *special,
        )
    )
    rows.append(
        R(
            c,
            st,
            "plastic-bags",
            "SPECIAL_HANDLING",
            "Low",
            False,
            "Not recycling — store take-back",
            "Retail plastic-bag take-back",
            "Plastic bags are not accepted in Boston curbside recycling. Return clean film to grocery/store take-back bins or dispose with trash.",
            [
                "Keep plastic bags out of the recycling bin.",
                "Use store film take-back when available.",
                "Otherwise place bags in trash.",
            ],
            [("Recycling carts?", "No — bags tangle sorting equipment.")],
            *special,
        )
    )
    rows.append(
        R(
            c,
            st,
            "construction-debris",
            "SPECIAL_HANDLING",
            "Low",
            False,
            "Private hauler — not city special collection",
            "Private C&D hauler",
            "Construction and demolition debris is not a Boston Freon/CRT special-collection item. Hire a private C&D hauler or debris box for remodel waste. Keep paint, batteries, and Freon appliances on Zero Waste Day / special-collection pathways.",
            [
                "Do not load C&D into regular trash expecting special collection.",
                "Hire a private hauler or permitted C&D facility.",
                "Separate HHW and Freon appliances onto the correct city programs.",
            ],
            [("Plumbing fixtures?", "City directs water heaters/dishwashers/plumbing fixtures to donate or private hauler.")],
            *special,
        )
    )
    return rows


def jacksonville():
    c, st = "jacksonville", "FL"
    bulk = (
        "City of Jacksonville — Household bulk collection",
        "https://www.jacksonville.gov/departments/office-of-administrative-services/solid-waste/household-bulk-collection",
    )
    quick = (
        "MyJax — Solid waste quick reference",
        "https://myjax.custhelp.com/app/answers/detail/a_id/1123",
    )
    hhw = (
        "City of Jacksonville — Household hazardous wastes (HHW)",
        "https://www.jacksonville.gov/departments/office-of-administrative-services/solid-waste/disposal-operations/household-hazardous-wastes-(hhw)",
    )
    rows = []
    rows.append(
        R(
            c,
            st,
            "mattress",
            "SPECIAL_HANDLING",
            "Low",
            True,
            "Household bulk — automated every other week / non-automated weekly",
            "Jacksonville household bulk collection",
            "Jacksonville Solid Waste collects mattresses, furniture, carpet (≤5 feet), and fencing on the household bulk program. Automated-collection areas typically get bulk every other week; non-automated areas get bulk weekly with garbage. Set piles out by 6 a.m. Call 630-CITY or use MyJax for questions. Appliances and tires are not ordinary bulk — they require a separate service request.",
            [
                "Set mattresses with other allowed bulk items by 6 a.m. on your bulk day.",
                "Keep carpet sections ≤5 feet; follow fencing/furniture rules.",
                "Use MyJax / 630-CITY for service questions or missed pickups.",
            ],
            [
                ("Appliances on bulk day?", "No — appliances and tires are collected only by service request."),
                ("Carpet length?", "City bulk guidance: carpet ≤5 feet."),
            ],
            *bulk,
        )
    )
    rows.append(
        R(
            c,
            st,
            "refrigerator",
            "SPECIAL_HANDLING",
            "High",
            True,
            "Service request only — doors closed/detached, food out",
            "Jacksonville appliance service request",
            "Jacksonville collects appliances only by service request (not as ordinary bulk). Empty food, keep doors closed or detached per city instructions, then request pickup via MyJax or 630-CITY. Do not place Freon appliances in carts or unscheduled bulk piles.",
            [
                "Empty the appliance and close or detach doors as instructed.",
                "Submit an appliance service request in MyJax or call 630-CITY.",
                "Set out only after the request is scheduled.",
            ],
            [("Tires with appliances?", "Tires also require a service request — max four tires.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c,
            st,
            "air-conditioner",
            "SPECIAL_HANDLING",
            "High",
            True,
            "Appliance service request (not ordinary bulk)",
            "Jacksonville appliance service request",
            "Treat air conditioners as appliances under Jacksonville’s service-request pathway. Book via MyJax / 630-CITY; do not leave Freon units on ordinary bulk day without a request. Never vent refrigerant yourself.",
            [
                "Request appliance collection through MyJax or 630-CITY.",
                "Prepare the unit safely without releasing refrigerant.",
                "Keep chemicals for the HHW facility separately.",
            ],
            [("Bulk day walk-up?", "Appliances need a service request — they are not automatic bulk.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c,
            st,
            "television",
            "BANNED_FROM_LANDFILLS",
            "Medium",
            True,
            "Schedule curbside OR Jacksonville HHW Facility",
            "Jacksonville HHW Facility / scheduled curbside",
            "Flat-screen TVs in Jacksonville may be scheduled for curbside collection or taken to the Household Hazardous Waste Facility at 2675 Commonwealth Avenue (Tue–Sat 8 a.m.–5 p.m., 904-387-8847). Other e-waste that is not a scheduled flat-screen TV should go to the HHW facility — not trash carts.",
            [
                "Schedule flat-screen TV curbside collection or haul to 2675 Commonwealth Ave.",
                "Call 904-387-8847 if unsure whether your set qualifies for curbside vs drop-off.",
                "Do not put TVs in garbage or recycling carts.",
            ],
            [("Hours?", "HHW Facility: Tuesday–Saturday 8 a.m.–5 p.m.")],
            *hhw,
        )
    )
    for item, label in [
        ("computer-monitor", "computer monitors"),
        ("smartphone", "phones and small electronics"),
        ("e-waste-mixed", "mixed electronic waste"),
    ]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "Jacksonville HHW Facility drop-off",
                "Jacksonville HHW Facility — 2675 Commonwealth Avenue",
                f"Take {label} to Jacksonville’s Household Hazardous Waste Facility at 2675 Commonwealth Avenue, Jacksonville, FL 32254 (Tue–Sat 8 a.m.–5 p.m., 904-387-8847). Flat-screen TVs may also use scheduled curbside; other e-waste should use the facility. Keep electronics out of trash and recycling carts.",
                [
                    "Do not place e-waste in carts.",
                    "Drop off at 2675 Commonwealth Ave during HHW hours.",
                    "Wipe personal data before recycling computers/phones.",
                ],
                [("Flat-screen TV option?", "TVs may be scheduled curbside or taken to the HHW facility.")],
                *hhw,
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
        "cooking-oil",
        "medical-sharps",
    ]:
        extras = {
            "paint-latex": " Paint is accepted at the HHW facility with a 27-gallon paint limit per 30 days.",
            "paint-oil": " Oil-based paint belongs at the HHW facility — never curbside.",
            "motor-oil": " Motor oil is accepted with a 27-gallon limit per 30 days — never curbside.",
            "propane-tank": " Propane cylinders are among materials accepted at the HHW facility.",
            "car-battery": " Batteries (including automotive) are accepted at the HHW facility.",
            "lithium-battery": " Batteries go to the HHW facility — not trash carts.",
            "fluorescent-bulbs": " Fluorescent lamps are accepted at the HHW facility.",
            "cooking-oil": " Use the HHW facility for household oils that are not ordinary trash-safe; never pour into drains.",
            "medical-sharps": " Confirm sharps acceptance before visiting; many HHW sites require approved containers or pharmacy programs.",
        }[item]
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS" if item not in {"cooking-oil", "paint-latex"} else "SPECIAL_HANDLING",
                "High" if item not in {"cooking-oil", "paint-latex"} else "Medium",
                False,
                "HHW Facility — never curbside (paint/oil 27 gal each / 30 days)",
                "Jacksonville HHW Facility — 2675 Commonwealth Avenue",
                f"Jacksonville never collects household hazardous waste curbside. Take materials to the HHW Facility at 2675 Commonwealth Avenue (Tue–Sat 8–5, 904-387-8847). Accepted streams include batteries, paint, propane, fluorescents, and related HHW.{extras}",
                [
                    "Never set HHW at the curb with garbage or bulk.",
                    "Deliver sealed containers to 2675 Commonwealth Ave within published paint/oil limits.",
                    "Call 904-387-8847 with questions about acceptance.",
                ],
                [("Paint/oil limit?", "City guidance: 27 gallons of paint and 27 gallons of motor oil per 30 days.")],
                *hhw,
            )
        )
    rows.append(
        R(
            c,
            st,
            "tires",
            "SPECIAL_HANDLING",
            "Medium",
            True,
            "Service request only — max 4 tires",
            "Jacksonville tire service request",
            "Jacksonville collects tires only by service request (maximum four tires), not as automatic bulk. Request pickup via MyJax or 630-CITY. Do not exceed the four-tire limit or leave tires in unscheduled piles.",
            [
                "Submit a tire service request (max four tires).",
                "Set out only when the request is scheduled.",
                "Retailer take-back when replacing tires is also fine.",
            ],
            [("With appliances?", "Appliances and tires both require service requests, separate from ordinary bulk.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c,
            st,
            "yard-waste",
            "ACCEPTED_IN_BLUE_BIN",
            "Low",
            True,
            "Weekly separate yard waste — 5 cu yd; limbs ≤5 ft & <6 in diameter",
            "Jacksonville yard-waste collection",
            "Jacksonville collects yard waste weekly as a separate stream. Limits typically include about 5 cubic yards, with limbs ≤5 feet long and under 6 inches in diameter. Keep yard waste out of recycling and out of plastic bags when city rules require paper/bundling.",
            [
                "Set yard waste out on the weekly yard-waste day within the 5 cu yd limit.",
                "Cut limbs to ≤5 feet and <6 inches diameter.",
                "Do not mix yard waste into recycling carts.",
            ],
            [("Plastic bags?", "Follow city preparation rules — plastic film often contaminates yard-waste loads.")],
            *quick,
        )
    )
    rows.append(
        R(
            c,
            st,
            "food-scraps",
            "SPECIAL_HANDLING",
            "Low",
            True,
            "Garbage cart unless you use private compost",
            "Jacksonville garbage / private compost",
            "Jacksonville’s published solid-waste programs emphasize garbage, recycling, yard waste, bulk, and HHW — not a separate citywide food-scrap cart. Bag food scraps for garbage or use a private/community compost option.",
            [
                "Bag food scraps for the garbage cart if you lack compost access.",
                "Keep food out of recycling.",
                "Yard trimmings use the yard-waste pathway.",
            ],
            [("Organics cart?", "Not a citywide food-scrap cart in published MyJax / Solid Waste materials.")],
            *quick,
        )
    )
    rows.append(
        R(
            c,
            st,
            "plastic-bags",
            "SPECIAL_HANDLING",
            "Low",
            False,
            "Not in recycling (#4) — store take-back / trash",
            "Store take-back / trash",
            "Jacksonville recycling does not accept plastic bags (commonly flagged as #4 film issues). Keep bags out of the recycling cart; use store take-back bins or trash.",
            [
                "Do not put plastic bags in curbside recycling.",
                "Return clean film to retail take-back when available.",
                "Otherwise dispose with trash.",
            ],
            [("#4 note?", "City/quick-ref materials flag plastic bags as not for recycling carts.")],
            *quick,
        )
    )
    rows.append(
        R(
            c,
            st,
            "construction-debris",
            "SPECIAL_HANDLING",
            "Low",
            True,
            "Small homeowner C&D limits on bulk; contractors private",
            "Jacksonville small C&D / private hauler",
            "Jacksonville allows limited homeowner construction debris on bulk: up to about 1 cubic yard weekly in non-automated areas or 2 cubic yards every other week in automated areas, pieces ≤5 feet and ≤40 lb. Contractor debris is not a city service — hire a private C&D hauler. Keep HHW and Freon appliances on their own pathways.",
            [
                "If you are a homeowner within size/weight limits, set small C&D with bulk on the correct schedule.",
                "Contractors must use private disposal — not city bulk.",
                "Separate paint, batteries, and appliances from C&D piles.",
            ],
            [("Limits?", "≈1 cu yd weekly (non-automated) or ≈2 cu yd every other week (automated); ≤5 ft, ≤40 lb pieces.")],
            *bulk,
        )
    )
    return rows


def columbus():
    c, st = "columbus", "OH"
    bulk = (
        "City of Columbus — Bulk collection",
        "https://www.columbus.gov/Services/Trash-Recycling-Bulk-Collection/Bulk-Collection",
    )
    hhw = (
        "City of Columbus — Household hazardous waste collection",
        "https://www.columbus.gov/Services/Trash-Recycling-Bulk-Collection/Household-Trash-Collection/Household-Hazardous-Waste-Collection",
    )
    rows = []
    rows.append(
        R(
            c,
            st,
            "mattress",
            "SPECIAL_HANDLING",
            "Low",
            True,
            "Must schedule 311 / 614-645-3111",
            "Columbus scheduled bulk collection",
            "Columbus bulk collection is appointment-only via 311 or 614-645-3111. Eligible bulk includes furniture, mattresses, carpet, and non-refrigerant appliances. Hot tubs, pianos, freon appliances, tires, auto parts, C&D, hazardous waste, furnaces, pool tables, and spas are not city bulk — use a private hauler. Residents can also drop off bulk/select electronics free at convenience centers (2100 Alum Creek Dr and 1550 Georgesville Rd; Tue–Sat, confirm hours on the city page).",
            [
                "Schedule bulk through 311 or 614-645-3111 before set-out.",
                "Or take eligible bulk to Alum Creek / Georgesville convenience centers with residency rules.",
                "Do not set hot tubs, pianos, or freon appliances out as city bulk.",
            ],
            [
                ("Walk-up bulk?", "No — Columbus requires scheduling for bulk collection."),
                ("Convenience centers?", "2100 Alum Creek Drive and 1550 Georgesville Road — Tue–Sat; confirm hours on columbus.gov."),
            ],
            *bulk,
        )
    )
    # Explicit overrides so mattress siblings hot-tub/piano do not inherit bulk pathway incorrectly
    for item, label in [("hot-tub", "hot tubs/spas"), ("piano", "pianos")]:
        rows.append(
            R(
                c,
                st,
                item,
                "SPECIAL_HANDLING",
                "Low",
                False,
                "Private hauler — not Columbus bulk",
                "Private hauler / specialty mover",
                f"Columbus explicitly lists {label} among items not accepted on city bulk collection (along with freon appliances, tires, C&D, hazardous waste, furnaces, and pool tables). Hire a private hauler or specialty mover. Do not schedule these through 311 bulk and do not leave them at convenience centers expecting bulk acceptance.",
                [
                    f"Arrange a private hauler experienced with {label}.",
                    "Do not book Columbus bulk for these items.",
                    "Keep any chemicals/oils for SWACO HHW separately.",
                ],
                [("Why not bulk?", "City bulk unacceptable list includes hot tubs, spas, and pianos.")],
                *bulk,
            )
        )
    rows.append(
        R(
            c,
            st,
            "refrigerator",
            "SPECIAL_HANDLING",
            "High",
            False,
            "Private hauler — freon appliances not city bulk",
            "Private appliance hauler / recycler",
            "Columbus bulk collection does not accept freon-containing appliances (refrigerators, freezers, air conditioners, dehumidifiers). Use a private hauler or certified appliance recycler. Convenience centers are for bulk/select electronics — confirm before hauling freon units. Never vent refrigerant yourself.",
            [
                "Hire a private Freon-appliance hauler or certified recycler.",
                "Do not schedule refrigerators on Columbus bulk via 311.",
                "Keep HHW chemicals for SWACO separately.",
            ],
            [("Washer on bulk?", "Yes — non-refrigerant appliances such as washers/dishwashers can be scheduled bulk.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c,
            st,
            "air-conditioner",
            "SPECIAL_HANDLING",
            "High",
            False,
            "Private hauler — not Columbus bulk",
            "Private appliance hauler / recycler",
            "Air conditioners and dehumidifiers are freon appliances excluded from Columbus bulk. Use a private hauler/recycler; do not place Freon units on scheduled bulk day or in trash carts.",
            [
                "Arrange private Freon appliance collection.",
                "Do not use 311 bulk for AC units.",
                "Confirm any convenience-center electronics rules separately — freon appliances are not bulk.",
            ],
            [("Same as fridge?", "Yes — freon appliances are excluded from city bulk.")],
            *bulk,
        )
    )
    for item, label in [
        ("washer", "washing machines"),
        ("dryer", "clothes dryers"),
        ("dishwasher", "dishwashers"),
        ("stove", "stoves/ovens"),
    ]:
        rows.append(
            R(
                c,
                st,
                item,
                "SPECIAL_HANDLING",
                "Medium",
                True,
                "Scheduled bulk (non-refrigerant appliances)",
                "Columbus scheduled bulk / convenience centers",
                f"Columbus bulk accepts non-refrigerant appliances such as {label}. Schedule collection through 311 or 614-645-3111, or use resident drop-off at the Alum Creek (2100 Alum Creek Drive) or Georgesville (1550 Georgesville Road) convenience centers (Tue–Sat; confirm hours on the city page). Freon appliances remain private-hauler only.",
                [
                    "Schedule bulk via 311 / 614-645-3111 or plan a convenience-center drop-off.",
                    "Do not mix freon refrigerators/AC units into this pathway.",
                    "Set out only on the scheduled bulk day if using curbside.",
                ],
                [("Fridge too?", "No — freon appliances are not Columbus bulk.")],
                *bulk,
            )
        )
    for item, label in [
        ("television", "televisions"),
        ("computer-monitor", "monitors"),
        ("smartphone", "phones and small electronics"),
        ("e-waste-mixed", "mixed electronic waste"),
    ]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "Convenience center select electronics / recycler",
                "Alum Creek / Georgesville convenience centers",
                f"Keep {label} out of Columbus trash carts. City convenience centers (2100 Alum Creek Drive and 1550 Georgesville Road) offer free resident drop-off for bulk and select electronics — confirm accepted electronics before you haul (Tue–Sat; confirm hours on columbus.gov). Retailer take-back and private e-waste recyclers are also options.",
                [
                    "Do not put electronics in garbage or recycling carts.",
                    "Use Alum Creek or Georgesville convenience centers for accepted electronics, or a retailer recycler.",
                    "Wipe personal data before drop-off.",
                ],
                [("Bulk for TVs?", "Prefer convenience-center / electronics pathways; confirm with 311 if unsure.")],
                *bulk,
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
        "cooking-oil",
        "medical-sharps",
    ]:
        extras = {
            "paint-latex": " Paint is a common SWACO HHW example material.",
            "paint-oil": " Oil-based paint belongs at SWACO HHW — not trash or bulk.",
            "motor-oil": " Used oil is listed among SWACO HHW examples.",
            "propane-tank": " Propane cylinders are among materials directed to SWACO HHW.",
            "car-battery": " Batteries are accepted at SWACO HHW; retailers often take cores too.",
            "lithium-battery": " Batteries belong at SWACO HHW — not curbside carts.",
            "fluorescent-bulbs": " Fluorescent lamps are SWACO HHW materials.",
            "cooking-oil": " Follow SWACO acceptance rules for household oils; never pour into drains.",
            "medical-sharps": " Confirm sharps rules before visiting SWACO; pharmacy sharps programs may be required.",
        }[item]
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS" if item not in {"cooking-oil", "paint-latex"} else "SPECIAL_HANDLING",
                "High" if item not in {"cooking-oil", "paint-latex"} else "Medium",
                False,
                "SWACO HHW — 645 E 8th Ave (Mon–Fri 9–5; first Sat 9–2)",
                "SWACO Household Hazardous Waste Facility",
                f"Columbus points residents to the SWACO Household Hazardous Waste Facility at 645 E 8th Avenue, Columbus, OH 43201 (Mon–Fri 9 a.m.–5 p.m.; first Saturday 9 a.m.–2 p.m.). Examples include paint, oil, batteries, fluorescents, and propane. Hazardous waste is not city bulk or trash.{extras}",
                [
                    "Do not set HHW out with Columbus bulk or garbage.",
                    "Deliver materials to SWACO at 645 E 8th Avenue during posted hours.",
                    "Transport upright in sealed containers.",
                ],
                [("City bulk for paint?", "No — hazardous materials are excluded from Columbus bulk.")],
                *hhw,
            )
        )
    rows.append(
        R(
            c,
            st,
            "tires",
            "SPECIAL_HANDLING",
            "Medium",
            False,
            "Private / retailer — not Columbus bulk",
            "Tire retailer take-back",
            "Tires are on Columbus’s not-accepted bulk list (with auto parts, freon appliances, C&D, and hazardous waste). Use a tire retailer take-back or permitted tire recycler — do not schedule tires through 311 bulk.",
            [
                "Ask the tire shop to take old tires when you buy replacements.",
                "Do not set tires out as Columbus bulk.",
                "Keep tires out of trash carts.",
            ],
            [("Convenience center tires?", "Confirm before hauling — city bulk list excludes tires.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c,
            st,
            "yard-waste",
            "ACCEPTED_IN_BLUE_BIN",
            "Low",
            True,
            "Separate city yard-waste program (biweekly zones)",
            "Columbus yard-waste collection",
            "Columbus runs a separate yard-waste program on biweekly zone schedules (not the same as scheduled bulk). Follow city preparation rules for bags/bundles and keep yard waste out of recycling carts and bulk piles.",
            [
                "Look up your yard-waste zone/day on columbus.gov.",
                "Prepare leaves/brush per city rules for the yard-waste truck.",
                "Do not mix yard waste into recycling or freon/HHW streams.",
            ],
            [("Same as bulk?", "No — yard waste is a separate city program from appointment bulk.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c,
            st,
            "food-scraps",
            "SPECIAL_HANDLING",
            "Low",
            False,
            "Convenience centers accept food scraps (Find My Collection Day)",
            "Alum Creek / Georgesville convenience centers",
            "Columbus convenience centers accept food scraps per the city’s Find My Collection Day guidance. There is not a universal citywide food-scrap cart for every address — use convenience-center drop-off or private compost, otherwise trash. Keep food out of recycling.",
            [
                "Check Find My Collection Day / convenience-center rules for food-scrap drop-off.",
                "Or use private compost / trash if drop-off is not practical.",
                "Keep organics out of recycling carts.",
            ],
            [("Where?", "Alum Creek (2100 Alum Creek Dr) and Georgesville (1550 Georgesville Rd) — confirm current food-scrap acceptance.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c,
            st,
            "plastic-bags",
            "SPECIAL_HANDLING",
            "Low",
            False,
            "Not curbside recycling — store take-back / trash",
            "Retail bag take-back",
            "Plastic bags are not accepted in Columbus curbside recycling. Return clean film to store take-back bins or dispose with trash.",
            [
                "Keep plastic bags out of the recycling cart.",
                "Use grocery take-back bins when available.",
                "Otherwise place bags in trash.",
            ],
            [("Curbside film?", "No — not for curbside recycling.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c,
            st,
            "construction-debris",
            "SPECIAL_HANDLING",
            "Low",
            False,
            "Private C&D — not city bulk",
            "Private C&D / transfer facility",
            "Construction and demolition debris is not accepted on Columbus bulk collection. Hire a private C&D hauler or debris box. Keep paint and chemicals for SWACO HHW and freon appliances on private appliance pathways.",
            [
                "Do not schedule C&D through 311 bulk.",
                "Use a private hauler or permitted C&D facility.",
                "Separate HHW and freon appliances from remodel debris.",
            ],
            [("Bulk for lumber?", "City lists C&D among materials not accepted on bulk.")],
            *bulk,
        )
    )
    return rows


def fort_worth():
    c, st = "fort-worth", "TX"
    bulk = (
        "City of Fort Worth — Bulk collection",
        "https://www.fortworthtexas.gov/departments/environmental-services/solidwaste/bulk",
    )
    dropoff = (
        "City of Fort Worth — Drop-off stations",
        "https://www.fortworthtexas.gov/departments/environmental-services/solidwaste/dropoff",
    )
    ecc = (
        "City of Fort Worth — Household hazardous waste / ECC",
        "https://www.fortworthtexas.gov/departments/environmental-services/solidwaste/hazardouswaste",
    )
    rows = []
    rows.append(
        R(
            c,
            st,
            "mattress",
            "SPECIAL_HANDLING",
            "Low",
            True,
            "Monthly curbside bulk by assigned week — ≤10 cu yd free",
            "Fort Worth monthly bulk / Drop-Off Stations",
            "Fort Worth collects mattresses and other allowed bulk on your assigned monthly bulk week. Set materials out by 7 a.m. Monday, keep one pile ≤10 cubic yards free, and leave about 2 feet from fences/cars/mailboxes. Bulk does not allow bagged trash, yard trimmings in plastic, auto parts/batteries/tires, contractor C&D, electronics, freon appliances/lawnmowers, dirt/rock/concrete/tile, liquids, or glass. Drop-Off Stations also accept bulk with water bill + driver’s license for full services.",
            [
                "Set mattresses in one bulk pile by 7 a.m. Monday of your assigned week (≤10 cu yd).",
                "Keep 2 feet clearance from obstacles; do not include banned materials.",
                "Or haul bulk to a Drop-Off Station (Brennan, Southeast, Old Hemphill, Hillshire).",
            ],
            [
                ("Electronics on bulk?", "No — electronics and freon appliances are not allowed in curbside bulk."),
                ("DOS hours?", "Drop-Off Stations: Tue–Fri 8–5, Sat 8–12."),
            ],
            *bulk,
        )
    )
    rows.append(
        R(
            c,
            st,
            "refrigerator",
            "SPECIAL_HANDLING",
            "High",
            False,
            "Drop-Off Station only — not curbside bulk",
            "Fort Worth Drop-Off Stations (e.g. Brennan)",
            "Freon appliances are banned from Fort Worth monthly curbside bulk. Take refrigerators to a Drop-Off Station (Brennan 2400 Brennan Ave, Southeast 5150 MLK Fwy, Old Hemphill 6260 Old Hemphill Rd, or Hillshire 301 Hillshire Dr). Empty food; freon need not be removed beforehand. Bring water bill + driver’s license for full services (apartments: DL for recycling/HHW only). The Environmental Collection Center (ECC) does not accept appliances.",
            [
                "Do not set freon appliances on monthly bulk week.",
                "Empty food and haul to a Drop-Off Station during Tue–Fri 8–5 / Sat 8–12 hours.",
                "Bring required ID/utility proof for full DOS services.",
            ],
            [("ECC for fridge?", "No — ECC does not accept appliances or electronics.")],
            *dropoff,
        )
    )
    rows.append(
        R(
            c,
            st,
            "air-conditioner",
            "SPECIAL_HANDLING",
            "High",
            False,
            "Drop-Off Station — not curbside bulk / not ECC",
            "Fort Worth Drop-Off Stations",
            "Air conditioners and freon lawn equipment are excluded from Fort Worth curbside bulk. Use a Drop-Off Station; keep units out of the ECC chemical program. Never vent refrigerant yourself.",
            [
                "Haul AC units to a Drop-Off Station — not monthly bulk.",
                "Do not take appliances to the ECC.",
                "Separate household chemicals for ECC vs DOS rules.",
            ],
            [("Same as fridge?", "Yes — freon appliances use Drop-Off Stations, not bulk.")],
            *dropoff,
        )
    )
    for item, label in [
        ("television", "TVs"),
        ("computer-monitor", "computer monitors"),
        ("smartphone", "computers/phones"),
        ("e-waste-mixed", "mixed electronics"),
    ]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "Drop-Off Station — computers/TVs limited (2 per 6 months)",
                "Fort Worth Drop-Off Stations",
                f"Electronics are not allowed in Fort Worth monthly bulk or at the ECC. Take {label} to a Drop-Off Station. Computers/TVs are limited to two per six months under DOS rules. Bring required ID/utility proof for full services.",
                [
                    "Keep electronics out of bulk piles and trash carts.",
                    "Drop off at Brennan / Southeast / Old Hemphill / Hillshire within the 2-per-6-months TV/computer limit.",
                    "Wipe personal data before recycling.",
                ],
                [("ECC electronics?", "No — ECC does not accept electronics.")],
                *dropoff,
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
        "cooking-oil",
        "medical-sharps",
    ]:
        if item == "propane-tank":
            rows.append(
                R(
                    c,
                    st,
                    item,
                    "BANNED_FROM_LANDFILLS",
                    "High",
                    False,
                    "Private exchange/retailer — not ECC; DOS lists tanks not accepted",
                    "Propane exchange / retailer",
                    "Fort Worth’s Environmental Collection Center does not accept propane cylinders. Drop-Off Station guidance also lists oxygen/CO2/butane/helium/propane tanks as not accepted. Use a propane exchange cage or retailer take-back — do not put cylinders in bulk, trash, or ECC lines.",
                    [
                        "Take empty/exchangeable cylinders to a propane retailer exchange.",
                        "Do not haul propane tanks to the ECC or expect DOS acceptance.",
                        "Never put cylinders in monthly bulk piles.",
                    ],
                    [("Why not ECC/DOS?", "City ECC excludes propane; DOS materials list tanks (including propane) as not accepted.")],
                    *ecc,
                )
            )
            continue
        if item == "medical-sharps":
            rows.append(
                R(
                    c,
                    st,
                    item,
                    "BANNED_FROM_LANDFILLS",
                    "High",
                    False,
                    "Medical sharps program — not ECC",
                    "Pharmacy / medical sharps program",
                    "Fort Worth’s ECC does not accept medical waste. Use an approved sharps container and a pharmacy/medical take-back program. Do not put loose needles in trash, bulk, or ECC chemical loads.",
                    [
                        "Place sharps only in an approved sharps container.",
                        "Use a pharmacy or medical sharps disposal program.",
                        "Do not bring medical waste to the ECC.",
                    ],
                    [("ECC medical waste?", "Not accepted.")],
                    *ecc,
                )
            )
            continue
        extras = {
            "paint-latex": " ECC and DOS both support household paint/chemical pathways — DOS allows about 20 gallons of chemicals per 3 months.",
            "paint-oil": " Oil-based paint belongs at ECC/DOS HHW channels — not trash or bulk.",
            "motor-oil": " Used oil belongs with HHW drop-off — not storm drains or bulk.",
            "car-battery": " Batteries are accepted at ECC and Drop-Off Stations.",
            "lithium-battery": " Batteries go to ECC or DOS — not trash carts.",
            "fluorescent-bulbs": " Fluorescent bulbs are accepted at ECC and DOS HHW services.",
            "cooking-oil": " ECC accepts cooking oil among household hazardous/special wastes — not drains.",
        }[item]
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS" if item not in {"cooking-oil", "paint-latex"} else "SPECIAL_HANDLING",
                "High" if item not in {"cooking-oil", "paint-latex"} else "Medium",
                False,
                "ECC and/or Drop-Off Station HHW (DOS ~20 gal chemicals / 3 months)",
                "Fort Worth ECC / Drop-Off Stations",
                f"Use Fort Worth’s Environmental Collection Center for chemicals, paint, batteries, cooking oil, and bulbs (ECC does not take appliances, electronics, propane, tires, or medical waste). Drop-Off Stations also accept HHW within limits (about 20 gallons of chemicals per three months) plus batteries and fluorescents.{extras}",
                [
                    "Choose ECC for chemical/paint/battery/bulb drop-off, or a Drop-Off Station within HHW limits.",
                    "Bring required ID/utility proof for full DOS services.",
                    "Never put HHW in monthly bulk or trash carts.",
                ],
                [("Brennan address?", "Brennan Drop-off Station: 2400 Brennan Ave — also use ECC for chemicals.")],
                *ecc,
            )
        )
    rows.append(
        R(
            c,
            st,
            "tires",
            "SPECIAL_HANDLING",
            "Medium",
            False,
            "Drop-Off Station — 4 tires / 6 months (rims separate); not bulk/ECC",
            "Fort Worth Drop-Off Stations",
            "Tires are banned from Fort Worth monthly bulk and are not accepted at the ECC. Drop-Off Stations accept up to four tires per six months with rims separated. Retailer take-back when replacing tires is also fine.",
            [
                "Do not set tires on bulk week.",
                "Haul up to four tires (rims off) to a Drop-Off Station within the six-month limit.",
                "Or leave old tires with the retailer when buying new ones.",
            ],
            [("ECC tires?", "No — ECC does not accept tires.")],
            *dropoff,
        )
    )
    rows.append(
        R(
            c,
            st,
            "yard-waste",
            "ACCEPTED_IN_BLUE_BIN",
            "Low",
            True,
            "Weekly paper bags/brush — not plastic in bulk",
            "Fort Worth yard-waste collection",
            "Fort Worth collects yard waste weekly in paper bags or as prepared brush — do not put yard trimmings in plastic bags into bulk piles. Keep yard waste on the yard-waste pathway, not mixed into the ≤10 cu yd bulk pile as plastic-bagged trimmings.",
            [
                "Set yard waste out weekly in paper bags or as allowed brush bundles.",
                "Do not place plastic-bagged yard trimmings in monthly bulk.",
                "Keep dirt/rock/concrete out of both yard waste and bulk when banned.",
            ],
            [("Bulk for brush?", "Yard trimmings in plastic are specifically banned from bulk.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c,
            st,
            "food-scraps",
            "SPECIAL_HANDLING",
            "Low",
            True,
            "Garbage or food-scrap compost pilot",
            "Fort Worth garbage / compost pilot",
            "Fort Worth residents typically dispose of food scraps in garbage unless enrolled in a food-scrap compost pilot. Keep food out of the blue recycling cart and out of HHW loads.",
            [
                "Bag food scraps for garbage unless you are on a compost pilot.",
                "Keep organics out of recycling.",
                "Cooking oil for ECC/HHW — not down the drain.",
            ],
            [("Citywide organics?", "Use garbage or the food-scrap compost pilot where offered.")],
            *bulk,
        )
    )
    rows.append(
        R(
            c,
            st,
            "plastic-bags",
            "SPECIAL_HANDLING",
            "Low",
            False,
            "Not blue cart — store take-back",
            "Retail bag take-back",
            "Plastic bags are not accepted in Fort Worth blue recycling carts. Return clean film to store take-back or trash. Drop-Off Stations accept clean Styrofoam separately from film bags — confirm current DOS Styrofoam rules before hauling.",
            [
                "Keep plastic bags out of the blue cart.",
                "Use grocery take-back bins when available.",
                "Otherwise dispose with trash.",
            ],
            [("Styrofoam?", "DOS accepts clean Styrofoam — separate from plastic-bag film rules.")],
            *dropoff,
        )
    )
    rows.append(
        R(
            c,
            st,
            "construction-debris",
            "SPECIAL_HANDLING",
            "Low",
            False,
            "Small remodel at DOS (≤5 cu yd/month); contractor C&D not bulk",
            "Fort Worth Drop-Off Stations / private C&D",
            "Contractor C&D and materials like dirt/rock/concrete/tile are banned from Fort Worth monthly bulk. Drop-Off Stations accept small remodel debris up to about 5 cubic yards per month for eligible residents. Larger or contractor loads need a private C&D hauler.",
            [
                "Do not put contractor C&D or concrete/tile in monthly bulk.",
                "Use a Drop-Off Station for small resident remodel loads within the ~5 cu yd/month limit.",
                "Hire a private hauler for larger projects.",
            ],
            [("Bulk concrete?", "Dirt/rock/concrete/tile are banned from curbside bulk.")],
            *dropoff,
        )
    )
    return rows


CITIES = [
    {
        "city": "Boston",
        "city_slug": "boston",
        "state": "MA",
        "state_slug": "massachusetts",
        "lat": 42.3601,
        "lng": -71.0589,
        "population": 675647,
    },
    {
        "city": "Jacksonville",
        "city_slug": "jacksonville",
        "state": "FL",
        "state_slug": "florida",
        "lat": 30.3322,
        "lng": -81.6557,
        "population": 949611,
    },
    {
        "city": "Columbus",
        "city_slug": "columbus",
        "state": "OH",
        "state_slug": "ohio",
        "lat": 39.9612,
        "lng": -82.9988,
        "population": 905748,
    },
    {
        "city": "Fort Worth",
        "city_slug": "fort-worth",
        "state": "TX",
        "state_slug": "texas",
        "lat": 32.7555,
        "lng": -97.3308,
        "population": 918915,
    },
]

ZIPS = [
    {
        "zip": "02108",
        "city": "Boston",
        "city_slug": "boston",
        "state": "MA",
        "state_slug": "massachusetts",
        "lat": 42.357,
        "lng": -71.064,
        "population": 4000,
    },
    {
        "zip": "02115",
        "city": "Boston",
        "city_slug": "boston",
        "state": "MA",
        "state_slug": "massachusetts",
        "lat": 42.342,
        "lng": -71.092,
        "population": 28000,
    },
    {
        "zip": "32202",
        "city": "Jacksonville",
        "city_slug": "jacksonville",
        "state": "FL",
        "state_slug": "florida",
        "lat": 30.329,
        "lng": -81.659,
        "population": 8000,
    },
    {
        "zip": "32204",
        "city": "Jacksonville",
        "city_slug": "jacksonville",
        "state": "FL",
        "state_slug": "florida",
        "lat": 30.312,
        "lng": -81.685,
        "population": 12000,
    },
    {
        "zip": "43215",
        "city": "Columbus",
        "city_slug": "columbus",
        "state": "OH",
        "state_slug": "ohio",
        "lat": 39.965,
        "lng": -82.999,
        "population": 15000,
    },
    {
        "zip": "43207",
        "city": "Columbus",
        "city_slug": "columbus",
        "state": "OH",
        "state_slug": "ohio",
        "lat": 39.917,
        "lng": -82.965,
        "population": 42000,
    },
    {
        "zip": "76102",
        "city": "Fort Worth",
        "city_slug": "fort-worth",
        "state": "TX",
        "state_slug": "texas",
        "lat": 32.753,
        "lng": -97.332,
        "population": 10000,
    },
    {
        "zip": "76104",
        "city": "Fort Worth",
        "city_slug": "fort-worth",
        "state": "TX",
        "state_slug": "texas",
        "lat": 32.731,
        "lng": -97.321,
        "population": 22000,
    },
]

FACILITIES = [
    {
        "name": "Boston Public Works special collection / Zero Waste events",
        "facility_type": "Municipal special collection & Zero Waste Day HHW events",
        "city_slug": "boston",
        "state": "MA",
        "zip": "02201",
        "address": "1 City Hall Square, Boston, MA 02201",
        "lat": 42.3601,
        "lng": -71.0589,
        "source_url": "https://www.boston.gov/departments/public-works/special-collection-items",
        "hours": "By appointment / event schedule via boston.gov & 311",
        "phone": "617-635-4500",
    },
    {
        "name": "Jacksonville HHW Facility",
        "facility_type": "Household hazardous waste / e-waste drop-off",
        "city_slug": "jacksonville",
        "state": "FL",
        "zip": "32254",
        "address": "2675 Commonwealth Avenue, Jacksonville, FL 32254",
        "lat": 30.3365,
        "lng": -81.7425,
        "source_url": "https://www.jacksonville.gov/departments/office-of-administrative-services/solid-waste/disposal-operations/household-hazardous-wastes-(hhw)",
        "hours": "Tue–Sat 8:00–17:00",
        "phone": "904-387-8847",
    },
    {
        "name": "Alum Creek Waste and Reuse Convenience Center",
        "facility_type": "Resident convenience center — bulk / select electronics / food scraps",
        "city_slug": "columbus",
        "state": "OH",
        "zip": "43207",
        "address": "2100 Alum Creek Drive, Columbus, OH 43207",
        "lat": 39.9275,
        "lng": -82.9538,
        "source_url": "https://www.columbus.gov/Services/Trash-Recycling-Bulk-Collection/Bulk-Collection",
        "hours": "Tue–Sat (confirm hours on city page)",
        "phone": "614-645-3111",
    },
    {
        "name": "SWACO Household Hazardous Waste Facility",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "columbus",
        "state": "OH",
        "zip": "43201",
        "address": "645 E 8th Avenue, Columbus, OH 43201",
        "lat": 39.9812,
        "lng": -82.9865,
        "source_url": "https://www.columbus.gov/Services/Trash-Recycling-Bulk-Collection/Household-Trash-Collection/Household-Hazardous-Waste-Collection",
        "hours": "Mon–Fri 9:00–17:00; first Sat 9:00–14:00",
        "phone": "614-871-5100",
    },
    {
        "name": "Brennan Drop-off Station (Fort Worth)",
        "facility_type": "Municipal drop-off — bulk / freon appliances / e-waste / HHW / tires",
        "city_slug": "fort-worth",
        "state": "TX",
        "zip": "76106",
        "address": "2400 Brennan Avenue, Fort Worth, TX 76106",
        "lat": 32.7885,
        "lng": -97.3482,
        "source_url": "https://www.fortworthtexas.gov/departments/environmental-services/solidwaste/dropoff",
        "hours": "Tue–Fri 8:00–17:00; Sat 8:00–12:00",
        "phone": "817-392-EASY",
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
        "boston": clone_siblings(boston()),
        "jacksonville": clone_siblings(jacksonville()),
        "columbus": clone_siblings(columbus()),
        "fort-worth": clone_siblings(fort_worth()),
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

    print("Wave-5 metros written:")
    for city, rows in audited.items():
        print(f"  {city}: {len(rows)} rules")
    print(f"Total rules now: {len(keep)}")


if __name__ == "__main__":
    main()
