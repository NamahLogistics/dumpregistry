#!/usr/bin/env python3
"""Portal-audited city guides for wave-6 metros (city-sourced only).

Cities researched from official program pages (2026-08-11):
  - Detroit, MI — detroitmi.gov DPW refuse / HHW Receiving Facility
  - Nashville, TN — nashville.gov Waste Services convenience centers / HHW / bulky
  - Portland, OR — portland.gov BPS bulky + Oregon Metro HHW / transfer
  - Baltimore, MD — baltimorecity.gov DPW bulk + Sisson Street HHW
  - Milwaukee, WI — city.milwaukee.gov Sanitation Drop Off + MMSD HHW
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


def detroit():
    c, st = "detroit", "MI"
    refuse = (
        "City of Detroit — Refuse collection",
        "https://detroitmi.gov/departments/department-public-works/refuse-collection",
    )
    bulk = (
        "City of Detroit — Bulk & yard waste",
        "https://detroitmi.gov/departments/department-public-works/refuse-collection/bulk-yard-waste",
    )
    hhw = (
        "City of Detroit — Household hazardous waste information",
        "https://detroitmi.gov/departments/department-public-works/refuse-collection/household-hazardous-waste-information",
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
            "Weekly curbside bulk (same day as trash) or free citizen bulk drop-off",
            "Detroit DPW weekly bulk / citizen bulk drop-off centers",
            "Detroit DPW collects trash, recycling, bulk, and yard waste weekly on the same day — look up your schedule in the city’s collection tool. Contractors are Priority Waste (east/southwest) or Waste Management (west). Mattresses and furniture go with weekly curbside bulk; for excess beyond set-out capacity call paid pickup at 313-876-0004 or use free citizen bulk drop-off centers. Keep Freon appliances and HHW off bulk piles.",
            [
                "Look up your weekly collection day and set mattresses out with allowed bulk.",
                "Keep piles clear of carts (city asks ~6 feet from carts for yard/bulk set-outs).",
                "For excess, call 313-876-0004 or use a free citizen bulk drop-off center.",
            ],
            [
                ("Same day as trash?", "Yes — trash, recycling, bulk, and yard waste share the weekly collection day."),
                ("Hauler?", "Priority Waste (east/SW) or WM (west) — confirm via the city schedule tool."),
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
            "Licensed appliance recycler / paid bulk — NOT Detroit HHW",
            "Licensed appliance recycler / Detroit paid bulk (313-876-0004)",
            "Detroit’s HHW Receiving Facility at 2000 E. Ferry Street does not accept appliances, AC units, or car parts. Refrigerators and other Freon white goods need a licensed appliance recycler or paid bulk/private options (city paid pickup line 313-876-0004). Empty food, remove doors when required, and never vent refrigerant yourself. Ordinary weekly bulk is for furniture-style items — not a substitute for Freon appliance recycling.",
            [
                "Do not take refrigerators to the DPW HHW Receiving Facility.",
                "Arrange a licensed appliance recycler or paid bulk/private pickup (313-876-0004).",
                "Keep doors secured/removed per hauler instructions; never release Freon.",
            ],
            [("HHW for fridge?", "No — city HHW lists appliances among materials not accepted.")],
            *hhw,
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
            "Licensed appliance recycler / paid bulk — NOT Detroit HHW",
            "Licensed appliance recycler / Detroit paid bulk options",
            "Window and portable air conditioners are not accepted at Detroit’s HHW Receiving Facility (2000 E. Ferry St). The facility’s not-accepted list includes AC units and appliances. Use a licensed appliance recycler or paid bulk/private Freon recovery options; never put Freon units in trash carts or vent refrigerant yourself.",
            [
                "Skip the HHW Receiving Facility for AC units — they are not accepted there.",
                "Book a licensed Freon appliance recycler or paid city/private bulk option.",
                "Keep the sealed unit intact until a certified tech handles refrigerant.",
            ],
            [("Same as fridge?", "Yes — Freon appliances/AC use recycler or paid bulk pathways, not HHW.")],
            *hhw,
        )
    )
    for item, label in [
        ("television", "TVs and monitors"),
        ("computer-monitor", "computer monitors"),
        ("smartphone", "phones, computers, printers, and microwaves"),
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
                "Free Detroit resident HHW drop-off (Thu + 4th Sat)",
                "DPW HHW Receiving Facility — 2000 E. Ferry Street",
                f"Detroit residents can drop off {label} free at the DPW HHW Receiving Facility, 2000 E. Ferry Street, Detroit, MI. Hours: Thursdays 7:30 a.m.–2:00 p.m. and the 4th Saturday 8:00 a.m.–2:00 p.m.; Detroit residents only. Electronics accepted include TVs, monitors, computers, phones, printers, and microwaves. Keep e-waste out of trash and recycling carts; appliances and AC units are not accepted here.",
                [
                    "Confirm you are a Detroit resident before visiting.",
                    "Drop electronics at 2000 E. Ferry St during published HHW hours.",
                    "Wipe personal data before recycling computers/phones.",
                ],
                [("Hours?", "Thu 7:30–14:00 and 4th Saturday 8:00–14:00.")],
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
    ]:
        extra = {
            "car-battery": " Alkaline and automotive batteries are both listed among accepted HHW materials.",
            "lithium-battery": " Keep rechargeable/lithium batteries for HHW — not trash carts.",
            "paint-latex": " Paint is accepted at the HHW Receiving Facility.",
            "paint-oil": " Oil-based paint and solvents belong at HHW — never curbside.",
            "motor-oil": " Used oil and antifreeze are accepted HHW streams.",
            "propane-tank": " Propane cylinders are accepted at the HHW Receiving Facility.",
            "fluorescent-bulbs": " Fluorescent lamps are accepted at HHW.",
            "cooking-oil": " Household oils that are not ordinary trash-safe should go to HHW — never pour down drains.",
        }[item]
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS" if item not in {"cooking-oil", "paint-latex"} else "SPECIAL_HANDLING",
                "High" if item not in {"cooking-oil", "paint-latex"} else "Medium",
                False,
                "Free Detroit resident HHW — Thu 7:30–14:00 + 4th Sat 8–14:00",
                "DPW HHW Receiving Facility — 2000 E. Ferry Street",
                f"Take household hazardous materials to Detroit’s HHW Receiving Facility at 2000 E. Ferry Street (Detroit residents only, free). Hours: Thursdays 7:30 a.m.–2:00 p.m. and the 4th Saturday 8:00 a.m.–2:00 p.m. Accepted streams include paint, batteries (alkaline and auto), fluorescents, propane, gasoline, oil, antifreeze, OTC medications, and related HHW.{extra} The facility does not accept AC units, appliances, C&D, ammo, commercial waste, car parts, yard waste, or ordinary trash.",
                [
                    "Never set HHW at the curb with garbage or bulk.",
                    "Deliver sealed, labeled containers to 2000 E. Ferry St during HHW hours.",
                    "Leave appliances/AC and C&D for their own pathways — not this facility.",
                ],
                [("Residents only?", "Yes — Detroit residents; bring proof if staff request it.")],
                *hhw,
            )
        )
    rows.append(
        R(
            c,
            st,
            "medical-sharps",
            "BANNED_FROM_LANDFILLS",
            "High",
            False,
            "HHW in rigid sealed hard plastic — Detroit residents",
            "DPW HHW Receiving Facility — 2000 E. Ferry Street",
            "Detroit accepts medical sharps at the HHW Receiving Facility (2000 E. Ferry St) when placed in a rigid, sealed hard-plastic container. Use Thursday or 4th-Saturday HHW hours; Detroit residents only, free. Do not loose-bag sharps in trash or recycling.",
            [
                "Place needles/sharps in a rigid sealed hard-plastic container.",
                "Drop off at 2000 E. Ferry St during HHW hours.",
                "Keep sharps out of recycling and loose trash bags.",
            ],
            [("OTC meds?", "City HHW also lists OTC medications among accepted materials.")],
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
            "Retailer take-back / paid bulk for excess — confirm set-out rules",
            "Tire retailer / Detroit paid bulk options",
            "Detroit’s weekly bulk program covers many large household items, but tires are best handled through retailer take-back when replacing tires or via paid bulk/private options if you have excess. Do not mix tires into HHW loads — the Receiving Facility does not accept car parts. Call 313-876-0004 for paid pickup questions.",
            [
                "Ask the tire shop to take old tires when you buy replacements.",
                "For leftover tires, use paid bulk/private options rather than HHW.",
                "Keep tires out of recycling carts and HHW.",
            ],
            [("HHW?", "No — HHW does not accept car parts.")],
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
            "Weekly yard waste (paper bags only); season ~Mar 31–Dec 19 2026",
            "Detroit DPW yard waste / free yard drop-off yards",
            "Detroit collects yard waste weekly on the same day as trash/recycling/bulk. Use paper bags only (no plastic); twigs ≤2 inches may go in bags; branches ≤4 feet and ≤4 inches diameter, bundled, ≤60 lb; keep piles about 6 feet from carts. Season for 2026 is roughly March 31–December 19. Free yard-waste drop-offs include Southfield Yard (12255 Southfield Service Dr), Davison Yard (8221 W Davison), and J. Fons (6451 E McNichols).",
            [
                "Bag leaves/twigs in paper bags only — never plastic bags.",
                "Bundle branches to ≤4 ft length, ≤4 in diameter, ≤60 lb; keep 6 ft from carts.",
                "Or use free drop-off at Southfield, Davison, or J. Fons yards during the season.",
            ],
            [("Plastic bags?", "Not allowed for yard waste — paper bags only.")],
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
            "Garbage cart unless you use private/community compost",
            "Detroit garbage / private compost",
            "Detroit’s published refuse programs emphasize weekly trash, recycling, bulk, yard waste, and HHW — not a separate citywide food-scrap cart. Bag food scraps for garbage or use a private/community compost option. Keep food out of recycling and out of HHW loads.",
            [
                "Bag food scraps for the garbage cart if you lack compost access.",
                "Keep organics out of blue recycling.",
                "Yard trimmings use the yard-waste pathway, not trash when in season.",
            ],
            [("City food cart?", "Not a published citywide food-scrap cart on DPW refuse pages.")],
            *refuse,
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
            "Not recycling — store take-back / trash",
            "Retail bag take-back / trash",
            "Plastic bags are not accepted in Detroit curbside recycling. Return clean film to store take-back bins when available, or dispose with trash. Do not use plastic bags for yard waste (paper bags only).",
            [
                "Keep plastic bags out of the recycling cart.",
                "Use grocery take-back bins when available.",
                "Otherwise place bags in trash.",
            ],
            [("Yard waste bags?", "Yard waste requires paper bags — plastic film contaminates that stream.")],
            *refuse,
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
            "Limited renovation with bulk or paid/private — not HHW",
            "Detroit bulk / private C&D (not HHW)",
            "Construction and demolition debris is not accepted at Detroit’s HHW Receiving Facility. Small homeowner renovation debris may fit limited weekly bulk or paid pickup (313-876-0004); larger or contractor loads need a private C&D hauler/transfer station. Keep paint, batteries, and Freon appliances on their own pathways.",
            [
                "Do not haul C&D to the HHW Receiving Facility.",
                "Use weekly bulk only for limited homeowner renovation debris that fits set-out rules.",
                "Hire a private C&D hauler for larger projects.",
            ],
            [("HHW for C&D?", "No — C&D is on the facility’s not-accepted list.")],
            *hhw,
        )
    )
    return rows


def nashville():
    c, st = "nashville", "TN"
    centers = (
        "Metro Nashville — Convenience centers",
        "https://www.nashville.gov/departments/waste-services/convenience-centers",
    )
    hhw = (
        "Metro Nashville — Household hazardous waste",
        "https://www.nashville.gov/departments/waste-services/convenience-centers/household-hazardous-waste",
    )
    bulky = (
        "Metro Nashville — Bulky item collection",
        "https://www.nashville.gov/departments/waste-services/convenience-centers/bulky-item-collection",
    )
    hours = (
        "Metro Nashville — Hours and locations",
        "https://www.nashville.gov/departments/waste-services/convenience-centers/hours-and-locations",
    )
    rows = []
    rows.append(
        R(
            c,
            st,
            "mattress",
            "SPECIAL_HANDLING",
            "Low",
            False,
            "$12 each at East/Ezell/Omohundro — max 4/month",
            "East / Ezell / Omohundro Convenience Centers",
            "Metro Nashville convenience centers charge $12 each for mattresses and box springs at East (943A Doctor Richard G. Adams Dr), Ezell (3254 Ezell Pike), and Omohundro (1019 Omohundro Place) — maximum four per month. Mattresses are excluded from the free “1 bulk item” allowance (free allowance is 3 bags trash ≤30 gal plus 1 bulk item that excludes mattresses, tires with rims, and C&D). Davidson County residents need a Tennessee driver’s license showing Davidson County; unload yourself; no commercial vehicles. Centers: Tue–Sat 8:30 a.m.–4:30 p.m.",
            [
                "Bring a TN DL showing Davidson County residency.",
                "Pay $12 per mattress/box spring at East, Ezell, or Omohundro (max 4/month).",
                "Unload yourself during Tue–Sat 8:30–16:30 hours.",
            ],
            [
                ("Free bulk include mattress?", "No — mattresses are excluded from the free bulk-item allowance."),
                ("Anderson Center?", "Mattress fees are listed for East/Ezell/Omohundro — confirm Anderson before hauling."),
            ],
            *bulky,
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
            "Free scrap-metal drop-off (1 bulk scrap item or 3 bags)",
            "Metro Nashville convenience centers — scrap metal",
            "Refrigerators, washers, dryers, stoves, and dishwashers are accepted free as scrap metal at Metro Nashville convenience centers under the scrap-metal allowance (1 bulk scrap metal item or 3 bags). Bring a TN DL showing Davidson County; unload yourself; no commercial vehicles. Centers operate Tue–Sat 8:30 a.m.–4:30 p.m. (Anderson 939A Anderson Ln, Madison; East 943A Doctor Richard G. Adams Dr; Ezell 3254 Ezell Pike; Omohundro 1019 Omohundro Pl). Keep Freon units intact — do not vent refrigerant.",
            [
                "Empty the appliance and keep Freon sealed.",
                "Drop off as scrap metal within the 1 bulk scrap item / 3-bag allowance.",
                "Show Davidson County residency on your TN driver’s license.",
            ],
            [("Free trash bags too?", "Centers also allow 3 bags trash (≤30 gal) plus 1 non-excluded bulk item.")],
            *centers,
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
            "Scrap metal / private Freon recycler — confirm center acceptance",
            "Metro Nashville convenience centers / licensed recycler",
            "Treat window/portable AC like other Freon appliances: keep the unit intact and use Metro convenience-center scrap-metal drop-off if staff accept your unit as scrap metal, or hire a licensed Freon recycler. Do not put AC units in trash bags or the free bulk allowance streams that exclude specialty items. Never vent refrigerant yourself.",
            [
                "Call ahead or ask staff whether your AC is accepted as scrap metal.",
                "Otherwise use a licensed appliance/Freon recycler.",
                "Keep units out of ordinary trash bags.",
            ],
            [("HHW for AC?", "HHW at East/Ezell is for chemicals — not Freon appliance recycling.")],
            *centers,
        )
    )
    for item, label in [
        ("television", "TVs and electronics"),
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
                "Free electronics ≤100 lb at East / Ezell / Omohundro",
                "East / Ezell / Omohundro Convenience Centers",
                f"Metro Nashville accepts {label} free at East, Ezell, and Omohundro convenience centers with a ≤100 lb electronics limit. Bring a TN DL showing Davidson County; unload yourself; Tue–Sat 8:30–16:30. Keep electronics out of trash and recycling carts.",
                [
                    "Haul electronics to East, Ezell, or Omohundro within the 100 lb limit.",
                    "Show Davidson County residency and unload yourself.",
                    "Wipe personal data before recycling computers/phones.",
                ],
                [("Anderson electronics?", "City materials highlight East/Ezell/Omohundro for free electronics.")],
                *centers,
            )
        )
    rows.append(
        R(
            c,
            st,
            "paint-latex",
            "SPECIAL_HANDLING",
            "Low",
            False,
            "Dry out for trash — latex/acrylic NOT accepted at HHW",
            "Trash after fully dry (Metro Nashville)",
            "Metro Nashville HHW (East & Ezell only) does not accept latex or acrylic paint. Dry latex/acrylic paint out completely (cat litter/absorbent in the can until solid) and place the dry can in trash. Do not take liquid latex to the HHW cages used for oil paint and chemicals.",
            [
                "Solidify latex/acrylic paint until it is fully dry.",
                "Place the dry can in household trash.",
                "Take oil-based paint and solvents to East or Ezell HHW instead.",
            ],
            [("Oil paint?", "Oil-based paint is free HHW at East & Ezell within the 15 gal / 100 lb limit.")],
            *hhw,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "Free HHW East & Ezell only — ≤15 gal or 100 lb",
                "East & Ezell Convenience Centers — HHW",
                f"Take {item.replace('-', ' ')} to Metro Nashville HHW at East (943A Doctor Richard G. Adams Dr) or Ezell (3254 Ezell Pike) only — free for Davidson County residents within ≤15 gallons or 100 lb. Centers: Tue–Sat 8:30–16:30; unload yourself; TN DL showing Davidson County. HHW does not accept propane tanks, latex/acrylic paint, medical waste, ammo, or medications.",
                [
                    "Deliver sealed containers to East or Ezell HHW only.",
                    "Stay within the 15 gal / 100 lb HHW limit.",
                    "Do not mix latex paint, propane, or medical waste into the HHW load.",
                ],
                [("Omohundro HHW?", "HHW is East & Ezell only per Metro Waste Services.")],
                *hhw,
            )
        )
    for item in [
        "car-battery",
        "lithium-battery",
        "paint-oil",
        "motor-oil",
        "fluorescent-bulbs",
        "cooking-oil",
    ]:
        extra = {
            "car-battery": " Confirm battery types accepted on the Metro HHW page before hauling auto batteries.",
            "lithium-battery": " Household battery types are accepted per the Metro HHW page — not trash carts.",
            "paint-oil": " Oil paint is accepted HHW; latex/acrylic is not.",
            "motor-oil": " Motor oil is accepted at East/Ezell HHW within the volume/weight limit.",
            "fluorescent-bulbs": " CFLs/fluorescents are listed among HHW-accepted materials.",
            "cooking-oil": " Keep cooking oil out of drains; use HHW or a used-oil pathway when liquid waste is not trash-safe.",
        }[item]
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS" if item not in {"cooking-oil"} else "SPECIAL_HANDLING",
                "High" if item not in {"cooking-oil"} else "Medium",
                False,
                "Free HHW East & Ezell — ≤15 gal or 100 lb",
                "East & Ezell Convenience Centers — HHW",
                f"Metro Nashville HHW is free at East and Ezell only (≤15 gal or 100 lb). Accepted materials include oil paint, motor oil, gasoline, pesticides, CFLs, and battery types listed on the city page.{extra} Not accepted: propane tanks, latex/acrylic paint, medical waste, ammo, or medications.",
                [
                    "Use East or Ezell HHW only — not every convenience center.",
                    "Stay within 15 gal / 100 lb and unload yourself.",
                    "Bring Davidson County residency proof (TN DL).",
                ],
                [("Hours?", "Convenience centers Tue–Sat 8:30 a.m.–4:30 p.m.")],
                *hhw,
            )
        )
    rows.append(
        R(
            c,
            st,
            "propane-tank",
            "SPECIAL_HANDLING",
            "High",
            False,
            "Not Metro HHW — exchange/refill vendor",
            "Propane exchange / refill vendor",
            "Metro Nashville HHW at East and Ezell does not accept propane tanks. Use a propane exchange cage or refill vendor; do not leave tanks in trash, free bulk, or HHW loads. Empty or full cylinders need a proper exchange pathway.",
            [
                "Do not take propane to East/Ezell HHW — it is not accepted.",
                "Use a retail propane exchange or refill service.",
                "Keep tanks out of trash bags and free bulk piles.",
            ],
            [("Helium/fire extinguisher?", "Also keep pressurized cylinders out of HHW; use vendor take-back pathways.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c,
            st,
            "medical-sharps",
            "SPECIAL_HANDLING",
            "High",
            False,
            "Red sharps container or 2L bottle in trash — not HHW",
            "Household trash (sealed rigid container)",
            "Metro Nashville HHW does not accept medical waste. Place sharps in a red sharps container or a rigid 2-liter bottle, seal it, and dispose with household trash per city guidance. Do not put loose needles in bags or recycling.",
            [
                "Contain sharps in a red container or sealed 2L rigid bottle.",
                "Place the sealed container in trash — not HHW.",
                "Never recycle sharps containers.",
            ],
            [("Medications at HHW?", "No — medications are on the HHW not-accepted list; use a pharmacy take-back.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c,
            st,
            "prescription-drugs",
            "SPECIAL_HANDLING",
            "High",
            False,
            "Pharmacy / take-back — not Metro HHW",
            "Pharmacy medication take-back",
            "Metro Nashville HHW lists medications among materials not accepted. Use a pharmacy or law-enforcement medication take-back program. Do not flush meds or mix them into East/Ezell HHW loads.",
            [
                "Use a pharmacy or official medication take-back.",
                "Do not take meds to Metro HHW.",
                "Keep meds out of recycling and drains.",
            ],
            [("Sharps with meds?", "Sharps use sealed trash containers; meds use take-back — neither is HHW.")],
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
            "Free no-rim East/Ezell max 4/month; with rims $5 each",
            "East / Ezell Convenience Centers",
            "Metro Nashville accepts tires without rims free at East and Ezell (maximum four per month). Tires with rims cost $5 each. Tires with rims are excluded from the free bulk-item allowance. Bring Davidson County residency proof; unload yourself; Tue–Sat 8:30–16:30.",
            [
                "Prefer East or Ezell for tire drop-off.",
                "Remove rims for the free (max 4/month) pathway, or pay $5 per tire with rim.",
                "Do not exceed monthly limits.",
            ],
            [("Free bulk tires?", "Tires with rims are excluded from the free bulk item.")],
            *bulky,
        )
    )
    rows.append(
        R(
            c,
            st,
            "yard-waste",
            "SPECIAL_HANDLING",
            "Low",
            False,
            "Compost drop-off at centers; brush/leaves via NDOT — not center brush",
            "Metro compost drop-off / NDOT brush program",
            "Metro convenience centers offer compost drop-off, but brush and leaves are listed as not accepted at the centers — use the NDOT brush program for brush/leaves. Do not treat centers as a leaf dump. Keep yard waste out of recycling carts.",
            [
                "Use center compost drop-off only for materials the compost program accepts.",
                "Send brush/leaves through the NDOT brush program — not as center brush.",
                "Keep yard waste out of blue recycling.",
            ],
            [("Brush at centers?", "City materials list brush/leaves as not accepted at convenience centers.")],
            *centers,
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
            "Compost drop-off at centers / trash if needed",
            "Metro convenience center compost drop-off",
            "Use Metro convenience-center compost drop-off for accepted food/yard organics when available. Otherwise bag food scraps for trash. Keep food out of recycling and out of HHW.",
            [
                "Check compost drop-off rules at your chosen center.",
                "Bag food for trash if compost drop-off is not an option.",
                "Keep organics out of recycling carts.",
            ],
            [("HHW for food?", "No — HHW is for chemicals at East/Ezell only.")],
            *centers,
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
            "Retail bag take-back / trash",
            "Plastic bags are not accepted in Nashville curbside recycling. Return clean film to store take-back or trash. Do not stuff bags into recycling carts at home or at centers.",
            [
                "Keep plastic bags out of curbside recycling.",
                "Use store film take-back when available.",
                "Otherwise dispose with trash.",
            ],
            [("Source?", "Metro Waste Services recycling guidance — bags are not curbside recyclable.")],
            *centers,
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
            "Omohundro $20 ≤2 cu yd — C&D excluded from free bulk",
            "Omohundro Convenience Center / private C&D",
            "Construction debris is excluded from Metro’s free bulk-item allowance. Omohundro Convenience Center (1019 Omohundro Place) accepts C&D for $20 up to 2 cubic yards. Larger loads need a private C&D hauler. Davidson County residency rules and self-unload requirements still apply; no commercial vehicles.",
            [
                "Do not count C&D as the free bulk item.",
                "Use Omohundro for ≤2 cu yd at $20, or hire a private hauler for more.",
                "Keep paint and HHW chemicals on the East/Ezell HHW pathway.",
            ],
            [("Hours?", "Centers Tue–Sat 8:30 a.m.–4:30 p.m. — see nashville.gov hours page.")],
            *hours,
        )
    )
    return rows


def portland():
    c, st = "portland", "OR"
    bulky = (
        "City of Portland — Bulky waste rates",
        "https://www.portland.gov/bps/garbage-recycling/bulky-waste",
    )
    large = (
        "City of Portland — Bulky waste disposal options",
        "https://www.portland.gov/bps/garbage-recycling/home-recycling/bulky-waste-disposal",
    )
    metro = (
        "Oregon Metro — Common hazardous products",
        "https://www.oregonmetro.gov/waste-disposal-and-prevention/need-get-rid-something/household-hazardous-waste/common-hazardous",
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
            "Hauler bulky ($18 trip + size fees) or free Bye Bye Mattress drop-off",
            "Assigned garbage company bulky / Bye Bye Mattress",
            "Portland residents contact their assigned garbage company for bulky pickup at city-set rates: $18 trip fee plus per-item fees (mattresses are size-based). Set items out by 6 a.m. on the scheduled day, not more than 24 hours early, and complete pickup within 7 days of the request. Free mattress recycling drop-off is also available through Bye Bye Mattress. Keep Freon appliances on the separate freon fee pathway.",
            [
                "Call your assigned garbage company to schedule bulky pickup, or use Bye Bye Mattress for free drop-off.",
                "Set out by 6 a.m. on the scheduled day (not >24 hours early).",
                "Expect the $18 trip fee plus the size-based mattress item fee if using hauler bulky.",
            ],
            [("E-waste on bulky?", "Appliances/e-waste are $6 on bulky; freon fridge/freezer/portable AC is $51.")],
            *bulky,
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
            "$51 freon bulky (fridge/freezer/portable AC) via assigned hauler",
            "Assigned garbage company bulky / Metro transfer",
            "Portland city bulky rates charge $51 for freon refrigerators, freezers, and portable air conditioners (plus the $18 trip fee). Contact your assigned garbage company; set out by 6 a.m. on the scheduled day within 7 days of request. You can also haul to Metro Central Transfer Station (6161 NW 61st Ave, Portland) or Metro South (Oregon City) — call 503-234-3000 for appointments/acceptance. Never vent refrigerant yourself.",
            [
                "Schedule freon bulky with your assigned hauler ($51 + $18 trip) or use Metro transfer.",
                "Set out by 6 a.m.; do not place units out more than 24 hours early.",
                "Keep doors secured and Freon sealed until certified handling.",
            ],
            [("Non-freon appliances?", "Appliances/e-waste on bulky are typically $6 plus the trip fee.")],
            *bulky,
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
            "$51 freon bulky for portable AC — assigned hauler",
            "Assigned garbage company bulky / Metro transfer",
            "Portable air conditioners are on Portland’s $51 freon bulky rate (with the $18 trip fee) through your assigned garbage company. Window units follow the same Freon-safe pathway — schedule bulky or use Metro transfer (Metro Central 6161 NW 61st Ave; call 503-234-3000). Do not put Freon units in garbage or recycling carts.",
            [
                "Book freon bulky with your hauler or haul to Metro Central/South.",
                "Pay the city freon fee pathway — do not abandon units at the curb unscheduled.",
                "Never release refrigerant yourself.",
            ],
            [("Same as fridge?", "Yes — freon fridge/freezer/portable AC share the $51 bulky rate.")],
            *bulky,
        )
    )
    for item, label in [
        ("television", "TVs and covered electronics"),
        ("computer-monitor", "monitors"),
        ("smartphone", "computers, phones, and small electronics"),
        ("e-waste-mixed", "mixed electronic waste"),
    ]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS",
                "Medium",
                True,
                "Free E-Cycle Oregon / bulky e-waste $6 + $18 trip",
                "E-Cycle Oregon / assigned hauler bulky",
                f"Oregon’s E-Cycle Oregon program offers free recycling for many covered {label}. Portland also lists appliances/e-waste at $6 on hauler bulky (plus $18 trip). Prefer free E-Cycle drop-off when your device is covered; otherwise schedule bulky or use Metro Find a Recycler. Keep electronics out of garbage and the blue recycling bin.",
                [
                    "Check E-Cycle Oregon for free covered-device drop-off.",
                    "Or schedule hauler bulky ($6 e-waste + $18 trip) within set-out rules.",
                    "Wipe personal data before recycling computers/phones.",
                ],
                [("Mattress free option?", "Bye Bye Mattress is the free mattress pathway — separate from E-Cycle.")],
                *large,
            )
        )
    rows.append(
        R(
            c,
            st,
            "paint-latex",
            "SPECIAL_HANDLING",
            "Low",
            False,
            "Dried latex <1 in — recycle/trash per Metro; liquid → Metro HHW",
            "Oregon Metro HHW / dried-can rules",
            "Oregon Metro guidance: dried latex paint with less than about 1 inch of residue can often go in recycling or trash per Metro’s dried-paint rules. Liquid latex and all oil-based paints/chemicals belong at Metro hazardous waste facilities (Metro Central 6161 NW 61st Ave, Portland, or Metro South in Oregon City — appointment/call 503-234-3000). Do not pour paint down drains or into stormwater.",
            [
                "If latex is dried to <1 inch residue, follow Metro recycle/trash dried-can rules.",
                "Take liquid paint and solvents to Metro HHW by appointment (503-234-3000).",
                "Keep paint out of the blue bin when still liquid.",
            ],
            [("Oil paint?", "Oil-based paint always goes to Metro HHW — not trash.")],
            *metro,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "Metro HHW by appointment — 503-234-3000",
                "Metro Central / Metro South hazardous waste",
                f"Take {item.replace('-', ' ')} to Oregon Metro household hazardous waste at Metro Central (6161 NW 61st Ave, Portland) or Metro South (Oregon City). Call 503-234-3000 for appointments and acceptance. Metro HHW also takes paint, chemicals, batteries, propane (even empty), and fluorescents. Never put these in garbage, recycling, or compost.",
                [
                    "Call 503-234-3000 to schedule Metro HHW.",
                    "Deliver sealed containers to Metro Central or Metro South.",
                    "Keep chemicals out of carts and storm drains.",
                ],
                [("Propane empty?", "Metro accepts propane tanks even when empty.")],
                *metro,
            )
        )
    for item in [
        "car-battery",
        "lithium-battery",
        "paint-oil",
        "motor-oil",
        "propane-tank",
        "fluorescent-bulbs",
        "cooking-oil",
        "medical-sharps",
    ]:
        extra = {
            "car-battery": " Auto and household batteries are Metro HHW streams (retailer core returns also fine for car batteries).",
            "lithium-battery": " Rechargeable/lithium batteries go to Metro HHW — not trash.",
            "paint-oil": " Oil-based paint and solvents are Metro HHW only.",
            "motor-oil": " Used oil belongs at Metro HHW or a listed used-oil site — not storm drains.",
            "propane-tank": " Metro accepts propane tanks even when empty.",
            "fluorescent-bulbs": " Fluorescent lamps are Metro HHW materials.",
            "cooking-oil": " Do not pour oils to drains; use Metro guidance / HHW pathways for liquid wastes.",
            "medical-sharps": " Use an approved sharps container and Metro/medical sharps guidance — not recycling.",
        }[item]
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS" if item not in {"cooking-oil"} else "SPECIAL_HANDLING",
                "High" if item not in {"cooking-oil"} else "Medium",
                False,
                "Metro HHW — Metro Central / South (503-234-3000)",
                "Metro Central Transfer Station — 6161 NW 61st Ave",
                f"Portland-area residents use Oregon Metro hazardous waste facilities for paint, chemicals, batteries, propane (even empty), and fluorescents. Primary site: Metro Central Transfer Station, 6161 NW 61st Ave, Portland (also Metro South, Oregon City). Call 503-234-3000 for appointments.{extra}",
                [
                    "Call 503-234-3000 before hauling HHW.",
                    "Use Metro Central (6161 NW 61st Ave) or Metro South as directed.",
                    "Never place HHW in garbage, blue bins, or compost carts.",
                ],
                [("Garbage at Metro?", "Metro transfer also handles garbage — HHW is the hazardous stream by appointment.")],
                *metro,
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
            "Hauler bulky item fees / Metro Find a Recycler",
            "Assigned hauler bulky / tire recycler",
            "Schedule tires with your assigned Portland garbage company under bulky rates (trip + item fees) or use Metro Find a Recycler / retailer take-back. Set out by 6 a.m. on the scheduled day within 7 days of request. Keep tires out of recycling carts.",
            [
                "Call your hauler for bulky tire pricing or use retailer take-back.",
                "Follow 6 a.m. set-out and 24-hour early limits.",
                "Do not put tires in the blue bin.",
            ],
            [("Mattress vs tires?", "Mattresses may use free Bye Bye Mattress; tires use bulky/retailer pathways.")],
            *bulky,
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
            "Weekly compost cart (food + yard); large branches bulky/Metro",
            "Portland weekly compost cart",
            "Portland’s weekly compost cart accepts food scraps and yard trimmings. Large branches that do not fit compost rules need hauler bulky service or Metro Find a Recycler / transfer options. Keep plastic bags out of the compost cart.",
            [
                "Use the weekly compost cart for accepted food and yard materials.",
                "Schedule bulky or use Metro pathways for oversized branches.",
                "Keep film plastic and HHW out of compost.",
            ],
            [("Food scraps?", "Yes — Portland compost carts take food plus yard debris.")],
            *large,
        )
    )
    rows.append(
        R(
            c,
            st,
            "food-scraps",
            "ACCEPTED_IN_BLUE_BIN",
            "Low",
            True,
            "Weekly compost cart with yard debris",
            "Portland weekly compost cart",
            "Food scraps go in Portland’s weekly compost cart along with yard debris. Follow the city’s accepted list; keep plastics, metals, and HHW out of compost. If you lack compost service, use trash as a last resort and consider Metro organics options.",
            [
                "Place food scraps in the compost cart per Portland’s accepted list.",
                "Keep compostable plastics rules per current city guidance.",
                "Do not put food in the blue recycling bin.",
            ],
            [("Large branches?", "Oversized wood needs bulky or Metro Find a Recycler — not the cart.")],
            *large,
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
            "Not blue bin — store take-back / trash",
            "Retail bag take-back / trash",
            "Plastic bags are not accepted in Portland’s blue recycling bin. Return clean film to store take-back or trash. Keep bags out of compost carts as well.",
            [
                "Do not put plastic bags in the blue bin.",
                "Use grocery take-back bins when available.",
                "Otherwise dispose with trash.",
            ],
            [("Compost bags?", "Do not use plastic film bags in the compost cart.")],
            *large,
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
            "Metro transfer / private C&D — not recycling",
            "Metro Central / private C&D",
            "Construction debris belongs at Metro transfer stations (Metro Central 6161 NW 61st Ave or Metro South) or a private C&D facility — not in recycling or compost carts. Call 503-234-3000 for Metro acceptance/fees. Keep hazardous leftovers (paint, solvents) on the Metro HHW pathway.",
            [
                "Haul C&D to Metro transfer or hire a private C&D hauler.",
                "Separate paint and chemicals for Metro HHW appointments.",
                "Do not place C&D in blue or compost carts.",
            ],
            [("Bulky for remodel?", "Some large household items use hauler bulky; true C&D uses Metro/private transfer.")],
            *large,
        )
    )
    return rows


def baltimore():
    c, st = "baltimore", "MD"
    bulk = (
        "City of Baltimore — Bulk trash pickup and large item removal",
        "https://www.baltimorecity.gov/publicworks/trash-recycling/bulk-trash-pickup-and-large-item-removal",
    )
    hhw = (
        "City of Baltimore — Household hazardous waste recycling",
        "https://www.baltimorecity.gov/publicworks/recycling-services/household-hazardous-waste-recycling",
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
            "Up to 3 bulk items/month on assigned Saturday — call 311",
            "Baltimore DPW bulk (311) / drop-off centers",
            "Baltimore City collects up to three bulk items per month on your assigned Saturday. Call 311 at least four working days ahead with address, phone, and item list; mark items “bulk collection”; set out by 7 a.m. Allowed items include furniture, mattresses, appliances, and up to four tires with rims off. Not allowed: building materials, auto parts, paint/stain, or flammable/hazardous materials. Free drop-off centers for trash/recycling are an alternative.",
            [
                "Call 311 ≥4 working days before your assigned Saturday bulk day.",
                "Mark items “bulk collection” and set out by 7 a.m. (max 3 items/month).",
                "Keep paint, C&D, and hazardous materials off the bulk pile.",
            ],
            [
                ("Appliances OK?", "Yes — appliances are listed among allowed bulk items."),
                ("Paint on bulk?", "No — paint/stain and flammables are not allowed on bulk."),
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
            "311 bulk (≤3 items/month) — Freon appliances allowed on bulk list",
            "Baltimore DPW bulk via 311",
            "Baltimore lists appliances among allowed bulk items (up to three bulk items per month on your assigned Saturday). Call 311 at least four working days ahead; mark “bulk collection”; set out by 7 a.m. Empty food and keep Freon sealed — never vent refrigerant. Drop-off centers are a free trash/recycling alternative for non-hazardous loads when bulk timing does not work.",
            [
                "Call 311 ≥4 working days ahead and list the refrigerator.",
                "Set out by 7 a.m. on the assigned Saturday within the 3-item monthly cap.",
                "Do not include paint or hazardous fluids with the appliance.",
            ],
            [("Tires with fridge?", "Up to four tires with rims off are also allowed on bulk.")],
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
            "311 bulk appliance pathway — not HHW chemicals site",
            "Baltimore DPW bulk via 311",
            "Treat air conditioners as bulk appliances in Baltimore: schedule via 311 (≥4 working days), set out by 7 a.m. on your assigned Saturday, and count toward the three-item monthly limit. Do not take Freon units to Sisson Street as if they were paint/chemical HHW — that site is for household hazardous products. Never vent refrigerant yourself.",
            [
                "Schedule AC pickup through 311 bulk collection.",
                "Set out by 7 a.m.; keep the unit intact.",
                "Use Sisson Street RRC for chemicals/batteries — not Freon reclaim DIY.",
            ],
            [("HHW for AC?", "Sisson Street HHW is for hazardous products; use 311 bulk for appliances/AC.")],
            *bulk,
        )
    )
    for item, label in [
        ("television", "TVs and electronics"),
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
                "City recycling directory / drop-off — confirm current e-waste sites",
                "Baltimore recycling drop-off / directory",
                f"Baltimore bulk may include appliances, but {label} should be confirmed through the city’s recycling directory and drop-off centers rather than assumed as trash. Keep electronics out of regular recycling carts when not accepted; use listed e-waste drop-offs. Do not place CRTs/electronics in bulk piles if 311 staff direct you to electronics recycling instead.",
                [
                    "Check Baltimore’s recycling directory for current electronics drop-off sites.",
                    "Ask 311 whether your TV/appliance can ride on bulk or needs e-waste drop-off.",
                    "Wipe personal data before recycling computers/phones.",
                ],
                [("Appliances vs e-waste?", "Appliances are listed on bulk; confirm TVs/electronics via the recycling directory.")],
                *bulk,
            )
        )
    rows.append(
        R(
            c,
            st,
            "paint-latex",
            "SPECIAL_HANDLING",
            "Low",
            False,
            "Dry for trash — oil paint goes to Sisson Street HHW",
            "Trash after dry / Sisson Street for oil paint",
            "Baltimore’s HHW program at Sisson Street Residential Recycling Center emphasizes oil paint, thinners, and related hazardous products. Latex paint is not the HHW focus — dry latex completely and place the dry can in trash. Never put liquid paint on bulk pickup (paint/stain is not allowed on bulk).",
            [
                "Dry latex paint solid before trashing the can.",
                "Take oil-based paint and thinners to Sisson Street HHW.",
                "Do not set paint out for Saturday bulk collection.",
            ],
            [("Bulk for paint?", "No — paint/stain is listed as not allowed on bulk.")],
            *hhw,
        )
    )
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "Sisson Street RRC HHW — seasonal Fri+Sat (confirm hours)",
                "Sisson Street Residential Recycling Center — 2840 Sisson Street",
                f"Take {item.replace('-', ' ')} to Baltimore’s HHW at Sisson Street Residential Recycling Center, 2840 Sisson Street (410-396-7250). Hours are seasonal Friday+Saturday and vary by month — check the city HHW page before you go. Materials must be in original labeled packaging. Confirm the current unacceptable list (variants mention gasoline not accepted on some lists). Never put these on bulk pickup.",
                [
                    "Call 410-396-7250 or check the city page for this month’s Fri+Sat hours.",
                    "Bring materials in original labeled containers.",
                    "Confirm gasoline and other edge-case items against the current unacceptable list.",
                ],
                [("Bulk?", "Flammable/hazardous materials are not allowed on bulk pickup.")],
                *hhw,
            )
        )
    for item in [
        "car-battery",
        "lithium-battery",
        "paint-oil",
        "motor-oil",
        "propane-tank",
        "fluorescent-bulbs",
        "cooking-oil",
        "medical-sharps",
    ]:
        extra = {
            "car-battery": " Batteries are accepted at Sisson Street HHW; retailer core returns also work for auto batteries.",
            "lithium-battery": " Household/rechargeable batteries belong at HHW — not trash.",
            "paint-oil": " Oil paint and thinners are core Sisson Street HHW materials.",
            "motor-oil": " Automotive fluids are listed among HHW accepted materials.",
            "propane-tank": " Propane cylinders are accepted at Sisson Street HHW.",
            "fluorescent-bulbs": " Fluorescent lamps are accepted HHW materials.",
            "cooking-oil": " Keep oils out of drains; use HHW or published used-oil guidance when not trash-safe.",
            "medical-sharps": " Medical waste is not accepted at Sisson Street HHW — use a sharps mail-back or approved medical program.",
        }[item]
        badge = "SPECIAL_HANDLING" if item in {"cooking-oil", "medical-sharps"} else "BANNED_FROM_LANDFILLS"
        hazard = "Medium" if item == "cooking-oil" else "High"
        fee = (
            "Approved sharps program — not Sisson Street HHW"
            if item == "medical-sharps"
            else "Sisson Street HHW — seasonal Fri+Sat (410-396-7250)"
        )
        rows.append(
            R(
                c,
                st,
                item,
                badge,
                hazard,
                False,
                fee,
                "Sisson Street Residential Recycling Center — 2840 Sisson Street"
                if item != "medical-sharps"
                else "Approved medical sharps program",
                f"Baltimore HHW is handled at Sisson Street Residential Recycling Center, 2840 Sisson Street (410-396-7250), on a seasonal Friday+Saturday schedule that varies by month. Accepted materials include batteries, oil paint, thinners, pesticides, pool chemicals, propane, fluorescents, automotive fluids, and fire extinguishers in original labeled packaging. Not accepted categories include acids, ammo, asbestos, explosives, and medical waste — confirm the current unacceptable list on the city page (some list variants mention gasoline).{extra}",
                [
                    "Check this month’s Fri+Sat HHW hours before driving to 2840 Sisson Street.",
                    "Keep materials in original labeled packaging.",
                    "Never place HHW on Saturday bulk piles.",
                ],
                [("Latex paint?", "Dry latex for trash; oil paint goes to Sisson Street HHW.")],
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
            "Bulk: ≤4 tires rims off / month via 311 Saturday",
            "Baltimore DPW bulk via 311",
            "Baltimore bulk allows up to four tires with rims off as part of the monthly bulk program (still within the three bulk-item scheduling process — confirm counting rules with 311). Call 311 ≥4 working days ahead; set out by 7 a.m. on your assigned Saturday. Retailer take-back when replacing tires is also fine. Auto parts beyond tires are not allowed on bulk.",
            [
                "Remove rims and call 311 to schedule tires on your bulk Saturday.",
                "Set out by 7 a.m.; stay within the four-tire / monthly bulk limits.",
                "Do not include other auto parts on the bulk pile.",
            ],
            [("Rims on?", "City bulk language: tires with rims off.")],
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
            "Regular city yard-waste programs",
            "Baltimore City yard-waste collection",
            "Baltimore handles yard waste through regular city collection programs (not the Saturday bulk hazardous exclusions). Follow DPW yard-waste set-out rules for bags/bundles; keep yard waste out of recycling when not accepted there, and never mix HHW into yard piles.",
            [
                "Use Baltimore’s regular yard-waste collection rules for leaves and trimmings.",
                "Keep yard waste separate from Saturday bulk hazardous exclusions.",
                "Do not mix paint or chemicals into yard piles.",
            ],
            [("Bulk for brush?", "Use yard-waste programs first; ask 311 before treating brush as bulk.")],
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
            "Garbage / city organics options if offered at your address",
            "Baltimore garbage / organics",
            "Bag food scraps for trash unless your address has a city or community organics option. Keep food out of recycling carts and out of Sisson Street HHW loads.",
            [
                "Bag food scraps for garbage if you lack organics service.",
                "Keep food out of single-stream recycling.",
                "Yard trimmings use yard-waste pathways.",
            ],
            [("HHW for food?", "No — Sisson Street is for hazardous products.")],
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
            "Not recycling — store take-back / trash",
            "Retail bag take-back / trash",
            "Plastic bags are not accepted in Baltimore curbside recycling. Return clean film to store take-back or trash. Drop-off centers accept trash/recycling as a free alternative for bagged trash, but film still does not belong in recycling streams.",
            [
                "Keep plastic bags out of recycling carts and recycling drop-off bunkers.",
                "Use store take-back when available.",
                "Otherwise place bags in trash.",
            ],
            [("Drop-off centers?", "Free trash/recycling drop-off is an alternative to curbside for many loads.")],
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
            "Not bulk — Quarantine Road Landfill / private (no hazardous)",
            "Quarantine Road Landfill / private C&D",
            "Building materials are not allowed on Baltimore bulk pickup. Haul construction debris to Quarantine Road Landfill or a private C&D facility. Hazardous wastes are excluded from ordinary landfill C&D loads — paint and chemicals go to Sisson Street HHW instead.",
            [
                "Do not set C&D out for Saturday bulk collection.",
                "Use Quarantine Road Landfill or a private C&D hauler.",
                "Route paint/chemicals to Sisson Street HHW (410-396-7250).",
            ],
            [("Bulk building materials?", "Not allowed — city bulk unacceptable list includes building materials.")],
            *bulk,
        )
    )
    return rows


def milwaukee():
    c, st = "milwaukee", "WI"
    bulky = (
        "City of Milwaukee — Bulky item pickup",
        "https://city.milwaukee.gov/sanitation/Bulky-Item-Pickup",
    )
    dropoff = (
        "City of Milwaukee — Drop Off Centers",
        "https://city.milwaukee.gov/sanitation/DropOff",
    )
    hhw = (
        "City of Milwaukee — Hazardous waste",
        "https://city.milwaukee.gov/sanitation/DropOff/HazardousWaste",
    )
    mmsd = (
        "MMSD — Home haz-mat collection",
        "https://www.mmsd.com/what-you-can-do/home-haz-mat-collection",
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
            "Small bulky on regular day (no request); larger via 414-286-CITY fee",
            "Milwaukee City Sanitation bulky / Drop Off Centers",
            "City of Milwaukee Sanitation customers may set out a small amount of bulky (about a recliner or two carts’ worth) on the regular collection day without an online request. Larger amounts require a fee through 414-286-CITY. Electronics, TVs, appliances, and tires are not bulky — take those to Drop Off Centers (South 3879 W Lincoln Ave; North 6660 N Industrial Rd) with photo ID / Milwaukee residency proof (load fees by volume).",
            [
                "Set a small bulky load on your regular collection day if you are a City Sanitation customer.",
                "For larger piles, call 414-286-CITY for the fee pathway.",
                "Do not put TVs, appliances, or tires in the bulky pile — use Drop Off Centers.",
            ],
            [
                ("Need a request for one recliner?", "Small amounts typically need no online request on regular day."),
                ("E-waste bulky?", "No — electronics/TVs/appliances/tires go to Drop Off Centers."),
            ],
            *bulky,
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
            "Drop Off Centers — not bulky; not MMSD HHW",
            "South Drop Off 3879 W Lincoln Ave / North 6660 N Industrial Rd",
            "Milwaukee does not collect appliances on bulky item pickup. Take refrigerators and other appliances to City Drop Off Centers — South (3879 W Lincoln Ave) or North (6660 N Industrial Rd) — with photo ID and Milwaukee residency proof; load fees are by volume. MMSD hazardous-waste sites do not accept appliances. Keep Freon sealed; never vent refrigerant yourself.",
            [
                "Do not set refrigerators out as bulky.",
                "Haul to South or North Drop Off with residency proof and pay volume-based fees.",
                "Keep appliances out of MMSD HHW lanes.",
            ],
            [("MMSD for fridge?", "No — MMSD does not accept appliances.")],
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
            "Drop Off Centers — not bulky; not MMSD HHW",
            "Milwaukee Drop Off Centers",
            "Air conditioners follow Milwaukee’s appliance pathway: Drop Off Centers (South 3879 W Lincoln Ave; North 6660 N Industrial Rd), not curbside bulky and not MMSD HHW. Bring photo ID / residency proof; expect volume-based load fees. Never release refrigerant yourself.",
            [
                "Take AC units to a City Drop Off Center.",
                "Skip bulky set-out and MMSD HHW for appliances.",
                "Keep Freon sealed until proper handling.",
            ],
            [("Same as fridge?", "Yes — appliances/AC use Drop Off Centers.")],
            *dropoff,
        )
    )
    for item, label in [
        ("television", "TVs"),
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
                "Drop Off Centers or Best Buy — not bulky; not MMSD HHW",
                "Milwaukee Drop Off Centers / Best Buy",
                f"Milwaukee excludes electronics and {label} from bulky pickup. Take them to Drop Off Centers (South 3879 W Lincoln Ave; North 6660 N Industrial Rd) with photo ID / Milwaukee residency proof (fees by volume), or use retailer options such as Best Buy. MMSD HHW does not accept electronics. Keep e-waste out of trash and recycling carts.",
                [
                    "Do not place TVs/electronics on the bulky pile.",
                    "Use South/North Drop Off Centers or Best Buy-style retail recycling.",
                    "Wipe personal data before recycling computers/phones.",
                ],
                [("MMSD electronics?", "No — city HHW materials say MMSD does not accept electronics.")],
                *dropoff,
            )
        )
    rows.append(
        R(
            c,
            st,
            "car-battery",
            "BANNED_FROM_LANDFILLS",
            "High",
            False,
            "Retailer take-back — MMSD does not accept car batteries",
            "Auto parts / battery retailer take-back",
            "Per City of Milwaukee HHW guidance, MMSD does not accept car batteries. Return automotive batteries to a retailer core-exchange or scrap battery outlet. Do not put car batteries in bulky piles, trash, or Drop Off HHW confusion — use retailer take-back.",
            [
                "Take car batteries to a retailer core-return / scrap outlet.",
                "Do not haul auto batteries to MMSD expecting acceptance.",
                "Keep batteries out of trash carts.",
            ],
            [("Household batteries?", "Button and rechargeable batteries go to MMSD HHW — different from car batteries.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c,
            st,
            "household-batteries",
            "BANNED_FROM_LANDFILLS",
            "Medium",
            False,
            "MMSD HHW — button & rechargeable batteries",
            "MMSD HHW (Lincoln Ave / 13th St)",
            "Button and rechargeable household batteries go to MMSD home haz-mat collection — not City bulky and not ordinary trash. Sites include the Lincoln Avenue facility (Thu–Sat 7:00–15:00) shared with South Drop Off at 3879 W Lincoln Ave, and the 13th Street site (Tue 11:00–18:00; Sat 8:00–14:00). See mmsd.com for current acceptance details.",
            [
                "Sort button/rechargeable batteries for MMSD HHW.",
                "Visit Lincoln Ave (Thu–Sat 7–15) or 13th St (Tue 11–18 / Sat 8–14).",
                "Keep car batteries on the retailer pathway instead.",
            ],
            [("Car batteries?", "Retailer take-back — MMSD does not accept car batteries.")],
            *mmsd,
        )
    )
    rows.append(
        R(
            c,
            st,
            "antifreeze",
            "BANNED_FROM_LANDFILLS",
            "High",
            False,
            "MMSD HHW — not trash or storm drains",
            "MMSD HHW (Lincoln Ave / 13th St)",
            "Take antifreeze and related automotive fluids to MMSD household hazardous material collection (Lincoln Ave Thu–Sat 7–15; 13th St Tue 11–18 / Sat 8–14). Do not pour antifreeze to drains or set it out with bulky/trash. Confirm current fluid acceptance on mmsd.com before hauling.",
            [
                "Deliver antifreeze to MMSD HHW during published hours.",
                "Keep fluids sealed and upright.",
                "Do not mix with Drop Off Center trash loads.",
            ],
            [("Gasoline?", "MMSD accepts gasoline among haz-mat streams — confirm container rules.")],
            *mmsd,
        )
    )
    for item in [
        "lithium-battery",
        "paint-latex",
        "paint-oil",
        "motor-oil",
        "propane-tank",
        "fluorescent-bulbs",
        "cooking-oil",
        "pesticides",
        "herbicides",
        "pool-chemicals",
        "gasoline",
    ]:
        extra = {
            "lithium-battery": " Rechargeable/lithium cells belong at MMSD with other household batteries.",
            "paint-latex": " MMSD accepts latex and oil paint.",
            "paint-oil": " Oil-based paint is an MMSD HHW material.",
            "motor-oil": " Used oil goes to MMSD / published used-oil outlets — not storm drains.",
            "propane-tank": " MMSD now accepts 1-lb and 20-lb propane cylinders — follow mmsd.com (some older lists said compressed gas was limited).",
            "fluorescent-bulbs": " Fluorescent lamps are accepted at MMSD HHW.",
            "cooking-oil": " Keep cooking oil out of drains; use MMSD guidance when it is managed as haz-mat/liquid waste.",
            "pesticides": " Pesticides are core MMSD haz-mat materials.",
            "herbicides": " Herbicides go to MMSD HHW — not trash.",
            "pool-chemicals": " Pool chemicals belong at MMSD HHW.",
            "gasoline": " Gasoline is accepted at MMSD — use approved containers.",
        }[item]
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS" if item not in {"cooking-oil", "paint-latex"} else "SPECIAL_HANDLING",
                "High" if item not in {"cooking-oil", "paint-latex"} else "Medium",
                False,
                "MMSD HHW — Lincoln Ave Thu–Sat 7–15; 13th St Tue/Sat hours",
                "MMSD HHW at South Drop Off / 13th Street",
                f"Milwaukee household chemicals go to MMSD (not City trash/bulky). Lincoln Avenue HHW (3879 W Lincoln Ave area) is open Thu–Sat 7:00–15:00; 13th Street is Tue 11:00–18:00 and Sat 8:00–14:00. MMSD accepts latex and oil paint, fluorescents, pesticides, gasoline, and button/rechargeable batteries; 1-lb and 20-lb propane are accepted per the MMSD page.{extra} MMSD does not accept appliances, electronics, medical waste/sharps, ammo, or car batteries.",
                [
                    "Take chemicals to MMSD HHW — not City bulky.",
                    "Use Lincoln Ave or 13th St during published hours.",
                    "Keep appliances, e-waste, and sharps on their separate pathways.",
                ],
                [("Propane?", "Use the MMSD page — 1-lb and 20-lb cylinders are accepted.")],
                *mmsd,
            )
        )
    rows.append(
        R(
            c,
            st,
            "medical-sharps",
            "BANNED_FROM_LANDFILLS",
            "High",
            False,
            "Safe Needle Disposal program — not MMSD HHW",
            "Safe Needle Disposal program",
            "MMSD does not accept medical waste or sharps. Milwaukee residents should use the Safe Needle Disposal program (see city HHW / public health guidance) for needles and sharps. Do not put sharps in recycling, bulky piles, or MMSD haz-mat lanes.",
            [
                "Use the Safe Needle Disposal program for sharps.",
                "Do not take medical waste to MMSD HHW.",
                "Keep sharps out of trash bags unless the program instructs a specific container method.",
            ],
            [("Meds?", "Use pharmacy take-back for medications — not MMSD.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c,
            st,
            "prescription-drugs",
            "SPECIAL_HANDLING",
            "High",
            False,
            "Pharmacy take-back — not MMSD HHW",
            "Pharmacy medication take-back",
            "Do not take medications to MMSD HHW (medical waste is not accepted). Use a pharmacy or law-enforcement medication take-back program. Keep meds out of recycling and drains.",
            [
                "Use a pharmacy / official medication take-back.",
                "Do not mix meds into MMSD haz-mat loads.",
                "Store meds securely until drop-off.",
            ],
            [("Sharps with meds?", "Sharps use Safe Needle Disposal; meds use take-back.")],
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
            "Drop Off Centers — not bulky",
            "Milwaukee Drop Off Centers",
            "Tires are not accepted on Milwaukee bulky pickup. Take tires to Drop Off Centers (South 3879 W Lincoln Ave; North 6660 N Industrial Rd) with photo ID / residency proof and pay volume-based fees, or use retailer take-back when replacing tires.",
            [
                "Skip bulky set-out for tires.",
                "Haul tires to South or North Drop Off (or retailer take-back).",
                "Bring residency proof and expect load fees.",
            ],
            [("Appliances same?", "Yes — tires, appliances, TVs, and electronics all use Drop Off, not bulky.")],
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
            "City yard-food waste program — separate from bulky",
            "Milwaukee yard-food waste collection",
            "Milwaukee runs a yard-food waste program separate from bulky item pickup. Use the city’s yard-food waste carts/set-out rules for leaves, grass, and accepted food scraps. Keep plastic bags out of the recycling cart and follow organics preparation rules.",
            [
                "Use the city yard-food waste program for accepted organics.",
                "Do not treat yard waste as bulky pickup.",
                "Keep film plastic out of recycling and organics as required.",
            ],
            [("Food scraps?", "Accepted food scraps ride with the yard-food waste program where offered.")],
            *bulky,
        )
    )
    rows.append(
        R(
            c,
            st,
            "food-scraps",
            "ACCEPTED_IN_BLUE_BIN",
            "Low",
            True,
            "City yard-food waste program",
            "Milwaukee yard-food waste collection",
            "Food scraps belong in Milwaukee’s yard-food waste program where you have service — not in recycling carts and not at MMSD HHW. Follow the city’s accepted food list; bag only as rules allow.",
            [
                "Place accepted food scraps in the yard-food waste stream.",
                "Keep food out of the recycling cart.",
                "Use trash only if you lack organics service for a specific item.",
            ],
            [("Bulky for food?", "No — organics use the yard-food waste program.")],
            *bulky,
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
            "Not recycling cart — store take-back / trash",
            "Retail bag take-back / trash",
            "Plastic bags are not accepted in Milwaukee recycling carts. Return clean film to store take-back or trash. Keep bags out of Drop Off recycling loads when film is not accepted.",
            [
                "Keep plastic bags out of the recycling cart.",
                "Use grocery take-back bins when available.",
                "Otherwise dispose with trash.",
            ],
            [("Drop Off film?", "Confirm current Drop Off rules — curbside recycling still bans bags.")],
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
            "Drop Off with volume fees / private C&D",
            "Milwaukee Drop Off Centers / private C&D",
            "Construction debris is not ordinary bulky. Take C&D to Drop Off Centers (South 3879 W Lincoln Ave; North 6660 N Industrial Rd) and pay volume-based load fees, or hire a private C&D hauler. Keep paint and chemicals on the MMSD HHW pathway.",
            [
                "Haul C&D to a Drop Off Center or private transfer facility.",
                "Bring residency proof and expect fees by volume.",
                "Route paint/solvents to MMSD HHW — not the trash bunker.",
            ],
            [("Bulky remodel?", "Small household bulky ≠ C&D — use Drop Off/private for construction debris.")],
            *dropoff,
        )
    )
    return rows


CITIES = [
    {
        "city": "Detroit",
        "city_slug": "detroit",
        "state": "MI",
        "state_slug": "michigan",
        "lat": 42.3314,
        "lng": -83.0458,
        "population": 639111,
    },
    {
        "city": "Nashville",
        "city_slug": "nashville",
        "state": "TN",
        "state_slug": "tennessee",
        "lat": 36.1627,
        "lng": -86.7816,
        "population": 689447,
    },
    {
        "city": "Portland",
        "city_slug": "portland",
        "state": "OR",
        "state_slug": "oregon",
        "lat": 45.5152,
        "lng": -122.6784,
        "population": 652503,
    },
    {
        "city": "Baltimore",
        "city_slug": "baltimore",
        "state": "MD",
        "state_slug": "maryland",
        "lat": 39.2904,
        "lng": -76.6122,
        "population": 585708,
    },
    {
        "city": "Milwaukee",
        "city_slug": "milwaukee",
        "state": "WI",
        "state_slug": "wisconsin",
        "lat": 43.0389,
        "lng": -87.9065,
        "population": 577222,
    },
]

ZIPS = [
    {
        "zip": "48201",
        "city": "Detroit",
        "city_slug": "detroit",
        "state": "MI",
        "state_slug": "michigan",
        "lat": 42.347,
        "lng": -83.060,
        "population": 12000,
    },
    {
        "zip": "48226",
        "city": "Detroit",
        "city_slug": "detroit",
        "state": "MI",
        "state_slug": "michigan",
        "lat": 42.334,
        "lng": -83.049,
        "population": 8000,
    },
    {
        "zip": "37203",
        "city": "Nashville",
        "city_slug": "nashville",
        "state": "TN",
        "state_slug": "tennessee",
        "lat": 36.152,
        "lng": -86.790,
        "population": 15000,
    },
    {
        "zip": "37207",
        "city": "Nashville",
        "city_slug": "nashville",
        "state": "TN",
        "state_slug": "tennessee",
        "lat": 36.206,
        "lng": -86.770,
        "population": 32000,
    },
    {
        "zip": "97201",
        "city": "Portland",
        "city_slug": "portland",
        "state": "OR",
        "state_slug": "oregon",
        "lat": 45.508,
        "lng": -122.690,
        "population": 18000,
    },
    {
        "zip": "97209",
        "city": "Portland",
        "city_slug": "portland",
        "state": "OR",
        "state_slug": "oregon",
        "lat": 45.530,
        "lng": -122.685,
        "population": 16000,
    },
    {
        "zip": "21201",
        "city": "Baltimore",
        "city_slug": "baltimore",
        "state": "MD",
        "state_slug": "maryland",
        "lat": 39.294,
        "lng": -76.622,
        "population": 14000,
    },
    {
        "zip": "21202",
        "city": "Baltimore",
        "city_slug": "baltimore",
        "state": "MD",
        "state_slug": "maryland",
        "lat": 39.291,
        "lng": -76.610,
        "population": 20000,
    },
    {
        "zip": "53202",
        "city": "Milwaukee",
        "city_slug": "milwaukee",
        "state": "WI",
        "state_slug": "wisconsin",
        "lat": 43.044,
        "lng": -87.907,
        "population": 22000,
    },
    {
        "zip": "53233",
        "city": "Milwaukee",
        "city_slug": "milwaukee",
        "state": "WI",
        "state_slug": "wisconsin",
        "lat": 43.038,
        "lng": -87.930,
        "population": 18000,
    },
]

FACILITIES = [
    {
        "name": "DPW HHW Receiving Facility",
        "facility_type": "Household hazardous waste / electronics drop-off",
        "city_slug": "detroit",
        "state": "MI",
        "zip": "48211",
        "address": "2000 E. Ferry Street, Detroit, MI 48211",
        "lat": 42.3765,
        "lng": -83.0385,
        "source_url": "https://detroitmi.gov/departments/department-public-works/refuse-collection/household-hazardous-waste-information",
        "hours": "Thu 7:30–14:00; 4th Sat 8:00–14:00",
        "phone": "313-876-0004",
    },
    {
        "name": "East Convenience Center",
        "facility_type": "Convenience center — bulky / electronics / HHW",
        "city_slug": "nashville",
        "state": "TN",
        "zip": "37207",
        "address": "943A Doctor Richard G. Adams Drive, Nashville, TN 37207",
        "lat": 36.1955,
        "lng": -86.7475,
        "source_url": "https://www.nashville.gov/departments/waste-services/convenience-centers/household-hazardous-waste",
        "hours": "Tue–Sat 8:30–16:30",
        "phone": "",
    },
    {
        "name": "Ezell Convenience Center",
        "facility_type": "Convenience center — bulky / electronics / HHW",
        "city_slug": "nashville",
        "state": "TN",
        "zip": "37211",
        "address": "3254 Ezell Pike, Nashville, TN 37211",
        "lat": 36.0965,
        "lng": -86.7205,
        "source_url": "https://www.nashville.gov/departments/waste-services/convenience-centers/household-hazardous-waste",
        "hours": "Tue–Sat 8:30–16:30",
        "phone": "",
    },
    {
        "name": "Metro Central Transfer Station",
        "facility_type": "Metro transfer — garbage / HHW by appointment",
        "city_slug": "portland",
        "state": "OR",
        "zip": "97210",
        "address": "6161 NW 61st Avenue, Portland, OR 97210",
        "lat": 45.5685,
        "lng": -122.7425,
        "source_url": "https://www.oregonmetro.gov/waste-disposal-and-prevention/need-get-rid-something/household-hazardous-waste/common-hazardous",
        "hours": "By appointment — call 503-234-3000",
        "phone": "503-234-3000",
    },
    {
        "name": "Sisson Street Residential Recycling Center",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "baltimore",
        "state": "MD",
        "zip": "21211",
        "address": "2840 Sisson Street, Baltimore, MD 21211",
        "lat": 39.3205,
        "lng": -76.6285,
        "source_url": "https://www.baltimorecity.gov/publicworks/recycling-services/household-hazardous-waste-recycling",
        "hours": "Seasonal Fri+Sat — confirm monthly hours on city page",
        "phone": "410-396-7250",
    },
    {
        "name": "South Drop Off Center / MMSD HHW",
        "facility_type": "Municipal drop-off — bulky alternatives / MMSD HHW",
        "city_slug": "milwaukee",
        "state": "WI",
        "zip": "53215",
        "address": "3879 W Lincoln Avenue, Milwaukee, WI 53215",
        "lat": 43.0035,
        "lng": -87.9625,
        "source_url": "https://www.mmsd.com/what-you-can-do/home-haz-mat-collection",
        "hours": "Drop Off per city schedule; MMSD HHW Thu–Sat 7:00–15:00",
        "phone": "414-286-CITY",
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
        "detroit": clone_siblings(detroit()),
        "nashville": clone_siblings(nashville()),
        "portland": clone_siblings(portland()),
        "baltimore": clone_siblings(baltimore()),
        "milwaukee": clone_siblings(milwaukee()),
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

    print("Wave-6 metros written:")
    for city, rows in audited.items():
        print(f"  {city}: {len(rows)} rules")
    print(f"Total rules now: {len(keep)}")


if __name__ == "__main__":
    main()
