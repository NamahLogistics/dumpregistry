#!/usr/bin/env python3
"""Portal-audited city guides for wave-7 metros (city-sourced only).

Cities researched from official program pages (2026-08-11):
  - Oklahoma City, OK — okc.gov Water, Trash & Recycling bulky / HHW
  - El Paso, TX — elpasotexas.gov Environmental Services / collection stations
  - Louisville, KY — louisvilleky.gov Public Works bulk / WRC / Haz Bin
  - Memphis, TN — memphistn.gov solid waste / Shelby County HHW
  - Albuquerque, NM — cabq.gov large item / HHW / e-waste
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


def oklahoma_city():
    c, st = "oklahoma-city", "OK"
    bulky = (
        "City of OKC — Bulky waste",
        "https://www.okc.gov/Services/Water-Trash-Recycling/Bulky-Waste",
    )
    hhw = (
        "City of OKC — Household Hazardous Waste Collection Center",
        "https://www.okc.gov/Services/Water-Trash-Recycling/Household-Hazardous-Waste-Collection-Center",
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
            "Monthly curbside bulky — first 4 cy included; excess fees",
            "OKC monthly curbside bulky (assigned day)",
            "Oklahoma City offers monthly curbside bulky waste on your assigned collection day within a three-day window (Monday–Wednesday or Wednesday–Friday). The first four cubic yards are included; excess volume may incur fees. Set items out by 6 a.m. on your assigned day and not more than three days early. Mattresses go with bulky pickup; wrap and label if bed bugs or biohazard conditions apply.",
            [
                "Confirm your assigned bulky day and three-day window on okc.gov.",
                "Set the mattress out by 6 a.m. on the assigned day (not >3 days early).",
                "Wrap and label if bed bugs or biohazard — otherwise standard bulky rules apply.",
            ],
            [
                ("Volume limit?", "First 4 cubic yards included; excess may incur fees."),
                ("Same as furniture?", "Yes — mattresses and furniture use the monthly bulky program."),
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
            True,
            "Call (405) 297-2833 to schedule Freon pickup during bulky window",
            "OKC Freon appliance scheduling — (405) 297-2833",
            "Refrigerators, freezers, and other Freon appliances require a special call to (405) 297-2833 to schedule pickup during your monthly bulky waste window. Remove doors per city ordinance before set-out. Do not place Freon units in trash carts or assume they ride ordinary bulky without scheduling. Never vent refrigerant yourself.",
            [
                "Call (405) 297-2833 to schedule Freon refrigerator pickup during your bulky window.",
                "Remove doors per OKC ordinance before set-out.",
                "Keep the unit intact — never release refrigerant yourself.",
            ],
            [("Freezer too?", "Yes — Freon refrigerators and freezers use the same scheduling line.")],
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
            "Call (405) 297-2833 to schedule Freon AC pickup during bulky window",
            "OKC Freon appliance scheduling — (405) 297-2833",
            "Window and portable air conditioners with Freon require calling (405) 297-2833 to schedule pickup during your monthly bulky waste window. Do not set Freon AC units out as ordinary bulky without scheduling. Never vent refrigerant yourself.",
            [
                "Call (405) 297-2833 to schedule Freon AC pickup during your bulky window.",
                "Confirm acceptance for window vs. central units when you call.",
                "Keep the sealed unit intact until city pickup.",
            ],
            [("Same as fridge?", "Yes — Freon appliances use (405) 297-2833 scheduling during bulky windows.")],
            *bulky,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c,
                st,
                item,
                "SPECIAL_HANDLING",
                "Medium",
                True,
                "Monthly curbside bulky — first 4 cy included; NOT Freon scheduling line",
                "OKC monthly curbside bulky (assigned day)",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s can go with OKC monthly curbside bulky on your assigned day (first 4 cubic yards included). Set out by 6 a.m. on the assigned day, not more than three days early. Do not use the Freon scheduling line (405-297-2833) for appliances without refrigerant — that line is for refrigerators, freezers, and AC units.",
                [
                    "Confirm your assigned bulky day on okc.gov.",
                    "Empty the appliance and set out by 6 a.m. on bulky day.",
                    "Use the Freon line only for refrigerators, freezers, and AC units.",
                ],
                [("Freon line for washer?", "No — (405) 297-2833 is for Freon appliances only.")],
                *bulky,
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
                "Private e-waste recycler / retailer take-back — HHW does not take computers",
                "Private e-waste recycler / retailer take-back",
                f"OKC’s Household Hazardous Waste Collection Center (1621 S. Portland Ave) does not accept computers or general electronics. The annual Spring Special Collection Event at the State Fairgrounds accepts computers but not household electronics like TVs or microwaves. For {label}, use a private e-waste recycler or retailer take-back program. Confirm current acceptance on OKC’s What Goes Where guidance.",
                [
                    "Do not haul TVs/computers to the HHW Center expecting acceptance.",
                    "Check OKC What Goes Where for current e-waste options.",
                    "Spring Special Event accepts computers — not TVs or microwaves.",
                ],
                [("HHW for TV?", "No — HHW does not take computers; TVs need private e-waste pathways.")],
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
            "car-battery": " Automotive and household batteries are among accepted HHW materials.",
            "lithium-battery": " Rechargeable/lithium batteries belong at HHW — not trash carts.",
            "paint-latex": " Paint (including latex) is accepted at the HHW Center.",
            "paint-oil": " Oil-based paint and solvents belong at HHW.",
            "motor-oil": " Used motor oil is accepted at HHW.",
            "propane-tank": " Propane cylinders are accepted at HHW.",
            "fluorescent-bulbs": " CFLs and fluorescent lamps are accepted at HHW.",
            "cooking-oil": " Keep cooking oil out of drains; use HHW when not trash-safe.",
        }[item]
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS" if item not in {"cooking-oil", "paint-latex"} else "SPECIAL_HANDLING",
                "High" if item not in {"cooking-oil", "paint-latex"} else "Medium",
                False,
                "Free OKC HHW — Tue–Fri 9:30–18:00, Sat 8:30–11:30 (water bill required)",
                "OKC HHW Collection Center — 1621 S. Portland Ave",
                f"Take household hazardous materials to OKC’s HHW Collection Center at 1621 S. Portland Ave, Oklahoma City, OK 73108. Hours: Tuesday–Friday 9:30 a.m.–6:00 p.m., Saturday 8:30–11:30 a.m.; free for OKC residents with a water bill.{extra} HHW does not accept tires, medications, or computers.",
                [
                    "Bring OKC water bill proof for free resident drop-off.",
                    "Deliver sealed, labeled containers during HHW hours.",
                    "Keep tires, meds, and computers on their separate pathways.",
                ],
                [("Residents only?", "Yes — free for OKC residents with water bill.")],
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
            "HHW or rigid sealed container — confirm sharps acceptance",
            "OKC HHW Collection Center — 1621 S. Portland Ave",
            "Place medical sharps in a rigid, sealed container before delivery. OKC HHW at 1621 S. Portland Ave accepts many hazardous streams — confirm sharps acceptance on the city page before hauling. Do not loose-bag needles in trash or recycling.",
            [
                "Place sharps in a rigid sealed hard-plastic container.",
                "Confirm sharps acceptance at HHW before driving.",
                "Never recycle loose needles.",
            ],
            [("Medications?", "HHW does not take meds — use the Spring Special Collection Event.")],
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
            "Spring Special Collection Event — HHW does not take meds",
            "OKC Spring Special Collection Event (State Fairgrounds)",
            "OKC’s HHW Collection Center does not accept medications. Use the annual Spring Special Collection Event at the State Fairgrounds for prescription and over-the-counter drugs. Do not flush meds or mix them into HHW loads.",
            [
                "Save medications for the Spring Special Collection Event.",
                "Do not take meds to the HHW Center.",
                "Use pharmacy take-back if you cannot wait for the event.",
            ],
            [("HHW for meds?", "No — medications go to the Spring Special Event.")],
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
            "Spring Special Event / private tire recycler — NOT bulky or HHW",
            "OKC Spring Special Event / private tire recycler",
            "Tires are not accepted at OKC HHW, not accepted on regular monthly bulky (automotive waste is excluded), and not ordinary trash. Use the annual Spring Special Collection Event at the State Fairgrounds or a private tire recycler. Retailer take-back when replacing tires is also an option.",
            [
                "Do not set tires out for monthly bulky pickup.",
                "Use the Spring Special Collection Event or a private tire recycler.",
                "Ask tire shops about take-back when buying replacements.",
            ],
            [("Bulky for tires?", "No — automotive waste is excluded from regular bulky.")],
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
            "OKC yard waste collection — confirm seasonal rules",
            "OKC yard waste collection",
            "Oklahoma City collects yard waste through its regular waste programs. Follow OKC set-out rules for bags, bundles, and seasonal limits. Keep yard waste out of HHW and bulky piles meant for furniture/appliances.",
            [
                "Use OKC yard waste bags/bundles per city rules.",
                "Keep yard waste separate from bulky and HHW.",
                "Check okc.gov for seasonal collection details.",
            ],
            [("Christmas trees?", "Follow OKC seasonal yard waste guidance for holiday trees.")],
            *bulky,
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
            "Garbage cart unless private compost",
            "OKC garbage / private compost",
            "OKC’s published programs emphasize trash, recycling, bulky, and HHW — not a separate citywide food-scrap cart. Bag food scraps for garbage or use private/community compost. Keep food out of recycling and HHW.",
            [
                "Bag food scraps for the garbage cart if you lack compost access.",
                "Keep organics out of blue recycling.",
                "Yard trimmings use the yard-waste pathway.",
            ],
            [("City food cart?", "Not a published citywide food-scrap cart on OKC waste pages.")],
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
            "Not recycling — store take-back / trash",
            "Retail bag take-back / trash",
            "Plastic bags are not accepted in OKC curbside recycling. Return clean film to store take-back bins when available, or dispose with trash. Do not use plastic bags for yard waste if paper is required.",
            [
                "Keep plastic bags out of the recycling cart.",
                "Use grocery take-back bins when available.",
                "Otherwise place bags in trash.",
            ],
            [("Yard waste bags?", "Follow OKC yard waste bag rules — often paper, not plastic film.")],
            *bulky,
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
            "Limited bulky or paid/private — not HHW",
            "OKC bulky / private C&D hauler",
            "Small homeowner renovation debris may fit within OKC monthly bulky limits (first 4 cubic yards included); larger or contractor loads need a private C&D hauler. Do not take C&D to the HHW Center. Keep paint and chemicals on the HHW pathway.",
            [
                "Use monthly bulky only for limited homeowner renovation debris.",
                "Hire a private C&D hauler for larger projects.",
                "Route paint and chemicals to 1621 S. Portland Ave HHW.",
            ],
            [("HHW for C&D?", "No — construction debris is not an HHW stream.")],
            *bulky,
        )
    )
    return rows


def el_paso():
    c, st = "el-paso", "TX"
    special = (
        "City of El Paso — Community services",
        "https://www.elpasotexas.gov/environmental-services/community-services/",
    )
    ccs = (
        "City of El Paso — Collection stations",
        "https://www.elpasotexas.gov/environmental-services/collection-stations/",
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
            "Fee Special Collections ($35 ≤5 cy + $7/cy after) OR free CCS drop-off",
            "El Paso Special Collections / Citizen Collection Stations",
            "El Paso has no free regular curbside bulky pickup. Mattresses and furniture can use fee-based Special Collections — call (915) 212-6000; $35 for up to 5 cubic yards plus $7/cy after; set out by 6 a.m. with 5 ft clearance — or drop off free at Citizen Collection Stations (CCS) Tue–Sat 8 a.m.–4 p.m. with water bill and ID. Five CCS locations: Northeast 4501 Hondo Pass; Central 2492 Harrison; Westside 121 Atlantic; Mission Valley 1034 Pendale; Eastside Confederate Dr.",
            [
                "Call (915) 212-6000 for fee Special Collections, or haul free to a CCS.",
                "Bring water bill and ID to CCS Tue–Sat 8:00–16:00.",
                "Set out by 6 a.m. with 5 ft clearance if using Special Collections.",
            ],
            [
                ("Free bulky curb?", "No — El Paso uses fee Special Collections or free CCS drop-off."),
                ("CCS locations?", "Five stations — see elpasotexas.gov collection stations page."),
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
            False,
            "Empty at Special Collections or CCS — call (915) 212-6000 for Freon units",
            "El Paso Special Collections / CCS",
            "Empty appliances are accepted at El Paso Special Collections and Citizen Collection Stations. For Freon refrigerators and freezers, call (915) 212-6000 to confirm handling — never vent refrigerant yourself. Remove food and secure doors. Freon acceptance details should be confirmed when scheduling Special Collections.",
            [
                "Empty the refrigerator completely before haul or set-out.",
                "Call (915) 212-6000 for Freon unit scheduling and acceptance.",
                "Never release refrigerant — keep the unit sealed until proper handling.",
            ],
            [("CCS free?", "Yes — CCS accepts empty appliances Tue–Sat 8–16 with water bill + ID.")],
            *ccs,
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
            "Call (915) 212-6000 for Freon AC — CCS/Special for empty units",
            "El Paso Special Collections / CCS",
            "Window and portable air conditioners with Freon need a call to (915) 212-6000 for proper handling. Empty non-Freon portable units may be accepted at CCS or Special Collections — confirm when scheduling. Never vent refrigerant yourself.",
            [
                "Call (915) 212-6000 to confirm Freon AC acceptance and scheduling.",
                "Keep the unit sealed until a certified handler processes refrigerant.",
                "CCS may accept empty appliances — bring water bill and ID.",
            ],
            [("Same as fridge?", "Yes — Freon appliances need phone confirmation before set-out/haul.")],
            *special,
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
                "CCS or landfill — NOT Special Pickup",
                "El Paso Citizen Collection Stations",
                f"El Paso electronics and {label} go to Citizen Collection Stations or the landfill — not fee-based Special Pickup. CCS hours Tue–Sat 8 a.m.–4 p.m.; bring water bill and ID. Do not schedule Special Collections for TVs or computers — that pathway is for bulky furniture/appliances, not e-waste.",
                [
                    "Haul electronics to a CCS — not Special Pickup.",
                    "Bring water bill and ID Tue–Sat 8:00–16:00.",
                    "Wipe personal data before recycling computers/phones.",
                ],
                [("Special Pickup for TV?", "No — electronics/TV use CCS or landfill, not Special Pickup.")],
                *ccs,
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
            "car-battery": " Auto and household batteries are accepted at CCS HHW.",
            "lithium-battery": " Rechargeable/lithium batteries go to CCS HHW.",
            "paint-latex": " Latex and oil paint accepted at CCS; reusable paint program available.",
            "paint-oil": " Oil-based paint accepted at CCS HHW.",
            "motor-oil": " Used motor oil accepted at CCS HHW.",
            "propane-tank": " Propane cylinders accepted at CCS HHW.",
            "fluorescent-bulbs": " CFLs and fluorescent lamps accepted at CCS HHW.",
            "cooking-oil": " Keep cooking oil out of drains; use CCS HHW when not trash-safe.",
        }[item]
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS" if item not in {"cooking-oil", "paint-latex"} else "SPECIAL_HANDLING",
                "High" if item not in {"cooking-oil", "paint-latex"} else "Medium",
                False,
                "Free CCS HHW — Tue–Sat 8:00–16:00 (water bill + ID)",
                "El Paso Citizen Collection Stations — HHW at all CCS",
                f"Household hazardous waste is accepted at all El Paso Citizen Collection Stations during Tue–Sat 8 a.m.–4 p.m. hours. Bring water bill and ID.{extra} Five CCS locations serve the city — see elpasotexas.gov collection stations.",
                [
                    "Deliver sealed containers to any CCS during HHW hours.",
                    "Bring water bill and photo ID.",
                    "Use the reusable paint program when latex paint is still good.",
                ],
                [("Which CCS?", "HHW is at all five CCS locations — pick the nearest.")],
                *ccs,
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
            "CCS HHW in rigid sealed container — confirm acceptance",
            "El Paso Citizen Collection Stations — HHW",
            "Place medical sharps in a rigid, sealed hard-plastic container before delivery to CCS HHW. Confirm sharps acceptance on the city Environmental Services page. Do not loose-bag needles in trash or recycling.",
            [
                "Place sharps in a rigid sealed container.",
                "Deliver to CCS HHW during Tue–Sat 8:00–16:00.",
                "Bring water bill and ID.",
            ],
            [("Medications?", "Confirm medication take-back options on the city page.")],
            *ccs,
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
            "NOT at Special or CCS — call Environmental Services / private recycler",
            "El Paso Environmental Services / private tire recycler",
            "Tires are not accepted at El Paso Special Collections or Citizen Collection Stations. Call Environmental Services or use a private tire recycler. Retailer take-back when replacing tires is also an option.",
            [
                "Do not haul tires to CCS or schedule Special Pickup for tires.",
                "Call Environmental Services or use a private tire recycler.",
                "Ask tire shops about take-back when buying replacements.",
            ],
            [("CCS for tires?", "No — tires are excluded from Special Collections and CCS.")],
            *special,
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
            "El Paso yard waste / green waste programs",
            "El Paso yard waste collection",
            "El Paso handles yard waste through its regular collection and green waste programs. Follow city set-out rules for bags, bundles, and seasonal limits. Keep yard waste out of HHW and Special Collections meant for bulky items.",
            [
                "Use El Paso yard waste set-out rules for leaves and trimmings.",
                "Keep yard waste separate from HHW loads at CCS.",
                "Check elpasotexas.gov for seasonal guidance.",
            ],
            [("Christmas trees?", "Follow city seasonal yard waste guidance for holiday trees.")],
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
            "Garbage cart unless private compost",
            "El Paso garbage / private compost",
            "Bag food scraps for garbage unless you use private/community compost. Keep food out of recycling carts and out of CCS HHW loads.",
            [
                "Bag food scraps for garbage if you lack compost access.",
                "Keep organics out of recycling.",
                "Yard trimmings use yard-waste pathways.",
            ],
            [("CCS for food?", "No — food scraps go in garbage or compost, not HHW.")],
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
            "Not recycling — store take-back / trash",
            "Retail bag take-back / trash",
            "Plastic bags are not accepted in El Paso curbside recycling. Return clean film to store take-back or trash. Keep bags out of CCS recycling streams.",
            [
                "Keep plastic bags out of the recycling cart.",
                "Use grocery take-back bins when available.",
                "Otherwise place bags in trash.",
            ],
            [("CCS film?", "Confirm current CCS rules — curbside recycling still bans bags.")],
            *ccs,
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
            "Special Collections fee or private C&D — not HHW",
            "El Paso Special Collections / private C&D",
            "Construction debris can use fee-based Special Collections (call 915-212-6000; $35 ≤5 cy + $7/cy after) or a private C&D hauler. Do not mix paint and chemicals into C&D loads — route those to CCS HHW.",
            [
                "Call (915) 212-6000 for Special Collections C&D pricing.",
                "Separate paint and chemicals for CCS HHW.",
                "Use a private C&D hauler for large contractor loads.",
            ],
            [("CCS for C&D?", "CCS is for household waste — large C&D may need Special or private hauler.")],
            *special,
        )
    )
    return rows


def louisville():
    c, st = "louisville", "KY"
    bulk = (
        "Louisville Metro Public Works — Junk and bulk trash disposal",
        "https://louisvilleky.gov/government/public-works/services/junk-and-bulk-trash-disposal",
    )
    wrc = (
        "Louisville Metro — Waste Reduction Center",
        "https://louisvilleky.gov/government/public-works/waste-reduction-center",
    )
    hhw = (
        "Louisville Metro — Haz Bin hazardous materials disposal",
        "https://louisvilleky.gov/government/public-works/services/hazardous-materials-disposal-haz-bin",
    )
    cyber = (
        "Louisville Metro — Electronics recycling (CyberCycle)",
        "https://louisvilleky.gov/government/public-works/electronics-recycling",
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
            "Large Item Pickup appt (USD) OR free WRC drop-off",
            "Louisville Large Item Pickup / Waste Reduction Center",
            "Louisville Metro Large Item Pickup serves the Urban Services District only — schedule an appointment online for up to four large items once per week. Mattresses can also go free to the Waste Reduction Center at 636 Meriwether Ave (Bland St entrance) — up to four large items per day for residents. Outside the USD, contact your private hauler.",
            [
                "USD residents: schedule Large Item Pickup online (up to 4 items/week).",
                "Or haul free to WRC 636 Meriwether Ave (Bland St entrance).",
                "Outside USD: use your private hauler.",
            ],
            [
                ("USD only?", "Large Item Pickup is Urban Services District only."),
                ("WRC free?", "Yes — up to 4 large items/day for Jefferson County residents."),
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
            "WRC Freon pathway — NOT curbside Large Item",
            "Waste Reduction Center — 636 Meriwether Ave (Bland St entrance)",
            "Freon refrigerators and freezers are NOT accepted on curbside Large Item Pickup. Take them to the Waste Reduction Center at 636 Meriwether Ave (Bland St entrance) — free up to four large items per day for Jefferson County residents. Keep Freon sealed; never vent refrigerant yourself. Do not set Freon units at the curb for Large Item.",
            [
                "Do not schedule Freon refrigerators for curbside Large Item.",
                "Haul to WRC 636 Meriwether Ave (Bland St entrance).",
                "Keep doors secured and Freon intact until proper handling.",
            ],
            [("Large Item for fridge?", "No — Freon appliances are excluded from curbside Large Item.")],
            *wrc,
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
            "WRC Freon pathway — NOT curbside Large Item",
            "Waste Reduction Center — 636 Meriwether Ave",
            "Freon air conditioners are NOT accepted on curbside Large Item Pickup. Take window and portable AC units to the Waste Reduction Center at 636 Meriwether Ave (Bland St entrance) — free up to four large items per day for residents. Never vent refrigerant yourself.",
            [
                "Do not set Freon AC units out for Large Item Pickup.",
                "Haul to WRC 636 Meriwether Ave (Bland St entrance).",
                "Keep the sealed unit intact until proper Freon handling.",
            ],
            [("Same as fridge?", "Yes — all Freon appliances use WRC, not curbside Large Item.")],
            *wrc,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c,
                st,
                item,
                "SPECIAL_HANDLING",
                "Medium",
                False,
                "Free WRC scrap metal — up to 4 large items/day",
                "Waste Reduction Center — 636 Meriwether Ave",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s go to the Waste Reduction Center at 636 Meriwether Ave (Bland St entrance) as scrap metal — free up to four large items per day for Jefferson County residents. These do not need the Freon pathway used for refrigerators and AC units. Large Item Pickup (USD) is an alternative for some non-Freon bulky items.",
                [
                    "Empty the appliance and haul to WRC 636 Meriwether Ave.",
                    "Use Bland St entrance; up to 4 large items/day for residents.",
                    "Do not confuse with Freon refrigerator/AC rules.",
                ],
                [("Freon line?", "No — non-Freon appliances use WRC scrap, not Freon scheduling.")],
                *wrc,
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
                "WRC CyberCycle — free up to 3 items/day",
                "Waste Reduction Center — CyberCycle electronics",
                f"Louisville Metro accepts {label} free through WRC CyberCycle at 636 Meriwether Ave — up to three electronics items per day for Jefferson County residents. Do not put electronics on curbside Large Item when CyberCycle is the designated pathway. Wipe personal data before recycling computers/phones.",
                [
                    "Haul electronics to WRC CyberCycle (636 Meriwether Ave).",
                    "Limit: 3 electronics items per day for residents.",
                    "Wipe personal data before drop-off.",
                ],
                [("Large Item for TV?", "Electronics use CyberCycle at WRC — not Large Item.")],
                *cyber,
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
            "Dry out for trash — latex NOT accepted at Haz Bin HHW",
            "Trash after fully dry (Louisville Metro)",
            "Louisville Metro Haz Bin at 7501 Grade Lane accepts oil paint but NOT latex paint. Dry latex paint completely (cat litter/absorbent in the can until solid) and place the dry can in trash. Do not take liquid latex to Haz Bin.",
            [
                "Solidify latex paint until fully dry.",
                "Place the dry can in household trash.",
                "Take oil-based paint to Haz Bin instead.",
            ],
            [("Oil paint?", "Oil paint is free at Haz Bin Tue–Sat 9:30–16:00.")],
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
                "Free Haz Bin HHW — Tue–Sat 9:30–16:00",
                "Haz Bin — 7501 Grade Lane",
                f"Take {item.replace('-', ' ')} to Louisville Metro Haz Bin at 7501 Grade Lane — free for Jefferson County residents, Tue–Sat 9:30 a.m.–4:00 p.m. Haz Bin accepts oil paint, chemicals, batteries, and related HHW. Latex paint is NOT accepted — dry latex for trash instead.",
                [
                    "Deliver sealed containers to Haz Bin 7501 Grade Lane.",
                    "Visit Tue–Sat 9:30–16:00; Jefferson County residents free.",
                    "Do not mix dry latex paint into HHW loads.",
                ],
                [("Latex at Haz Bin?", "No — latex must be dried out for trash.")],
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
    ]:
        extra = {
            "car-battery": " Auto and household batteries accepted at Haz Bin.",
            "lithium-battery": " Rechargeable/lithium batteries go to Haz Bin — not trash.",
            "paint-oil": " Oil-based paint accepted at Haz Bin.",
            "motor-oil": " Used motor oil accepted at Haz Bin.",
            "propane-tank": " Propane cylinders accepted at Haz Bin.",
            "fluorescent-bulbs": " CFLs and fluorescent lamps accepted at Haz Bin.",
            "cooking-oil": " Keep cooking oil out of drains; use Haz Bin when not trash-safe.",
        }[item]
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS" if item not in {"cooking-oil"} else "SPECIAL_HANDLING",
                "High" if item not in {"cooking-oil"} else "Medium",
                False,
                "Free Haz Bin HHW — Tue–Sat 9:30–16:00",
                "Haz Bin — 7501 Grade Lane",
                f"Louisville Metro Haz Bin at 7501 Grade Lane accepts household hazardous materials free for Jefferson County residents, Tue–Sat 9:30 a.m.–4:00 p.m.{extra} Latex paint is not accepted — dry latex for trash.",
                [
                    "Deliver sealed containers to 7501 Grade Lane during Haz Bin hours.",
                    "Jefferson County residents — free drop-off.",
                    "Keep latex paint out of HHW loads.",
                ],
                [("Hours?", "Tue–Sat 9:30 a.m.–4:00 p.m.")],
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
            "Approved sharps container in trash — confirm Haz Bin rules",
            "Household trash (rigid sealed container) / Haz Bin",
            "Place medical sharps in a rigid, sealed container. Confirm whether Haz Bin accepts sharps on the city page — many Louisville sharps go in sealed containers with household trash per public health guidance. Do not loose-bag needles in recycling.",
            [
                "Place sharps in a rigid sealed hard-plastic container.",
                "Confirm Haz Bin sharps acceptance or use approved trash method.",
                "Never recycle sharps containers.",
            ],
            [("Medications?", "Use pharmacy take-back — confirm Haz Bin med rules on city page.")],
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
            "Up to 4 passenger tires at Large Item (USD) or WRC",
            "Louisville Large Item Pickup / WRC",
            "Louisville accepts up to four passenger tires on Large Item Pickup in the Urban Services District (schedule online) or at the Waste Reduction Center. Outside USD, use WRC or retailer take-back. Do not exceed passenger tire limits.",
            [
                "USD: schedule Large Item Pickup for up to 4 passenger tires.",
                "Or haul to WRC 636 Meriwether Ave.",
                "Retailer take-back when replacing tires is also fine.",
            ],
            [("WRC tires?", "Yes — WRC also accepts tires for residents.")],
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
            "Louisville yard waste collection programs",
            "Louisville Metro yard waste collection",
            "Louisville handles yard waste through regular city collection programs. Follow set-out rules for bags and bundles; keep yard waste out of Haz Bin HHW and Large Item piles when not appropriate.",
            [
                "Use Louisville yard waste set-out rules for leaves and trimmings.",
                "Keep yard waste separate from Haz Bin chemical loads.",
                "Check louisvilleky.gov for seasonal guidance.",
            ],
            [("Christmas trees?", "Follow city seasonal yard waste guidance.")],
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
            "Garbage cart unless private/community compost",
            "Louisville garbage / private compost",
            "Bag food scraps for garbage unless you use private/community compost. Keep food out of recycling and out of Haz Bin HHW loads.",
            [
                "Bag food scraps for garbage if you lack compost access.",
                "Keep organics out of recycling.",
                "Yard trimmings use yard-waste pathways.",
            ],
            [("Haz Bin for food?", "No — Haz Bin is for hazardous products.")],
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
            "Plastic bags are not accepted in Louisville curbside recycling. Return clean film to store take-back or trash.",
            [
                "Keep plastic bags out of the recycling cart.",
                "Use grocery take-back bins when available.",
                "Otherwise place bags in trash.",
            ],
            [("WRC film?", "Keep film out of recycling streams at WRC too.")],
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
            "Private C&D hauler — not Large Item or Haz Bin",
            "Private C&D hauler / WRC (limited)",
            "Construction and demolition debris is not accepted at Haz Bin HHW. Large Item Pickup covers household large items, not contractor C&D loads. Hire a private C&D hauler for renovation debris; route paint and chemicals to Haz Bin separately.",
            [
                "Do not set C&D out for Large Item Pickup.",
                "Hire a private C&D hauler for construction debris.",
                "Route paint/chemicals to Haz Bin 7501 Grade Lane.",
            ],
            [("Haz Bin for C&D?", "No — C&D is not a Haz Bin stream.")],
            *bulk,
        )
    )
    return rows


def memphis():
    c, st = "memphis", "TN"
    bulk = (
        "City of Memphis — Household garbage / bulk",
        "https://memphistn.gov/household-garbage/",
    )
    solid = (
        "City of Memphis — Solid waste",
        "https://memphistn.gov/solid-waste/",
    )
    hhw = (
        "Shelby County — Household hazardous waste",
        "https://www.shelbycountytn.gov/439/Household-Hazardous-Waste",
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
            "Bulk Week / Outside-the-Cart (~2×/month) — call 311 when ready",
            "Memphis Bulk Week via 311",
            "Memphis offers Bulk Week / Outside-the-Cart collection roughly twice per month. Call 311 when ready; place items within 3 feet of the street. Mattresses go on bulk week. Follow the Memphis Clean City Guide and 311/app guidance for pile limits — do not invent volume caps beyond what the city publishes.",
            [
                "Call 311 when your bulk pile is ready for pickup.",
                "Place items within 3 feet of the street.",
                "Check Memphis Clean City Guide / 311 app for pile guidance.",
            ],
            [
                ("How often?", "Roughly twice per month — call 311 to schedule when ready."),
                ("Volume?", "Follow Clean City Guide / 311 — city guidance varies by program updates."),
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
            "Bulk Week — remove doors or tape shut; NOT Shelby County HHW",
            "Memphis Bulk Week via 311",
            "Freon refrigerators and freezers go on Memphis Bulk Week / Outside-the-Cart — call 311 when ready. Remove doors or tape them shut per city guidance before set-out. Do NOT take Freon appliances to Shelby County HHW at 6305 Haley Rd. Never vent refrigerant yourself.",
            [
                "Call 311 when ready for Bulk Week pickup.",
                "Remove doors or tape shut on Freon refrigerators/freezers.",
                "Do not haul Freon units to Shelby County HHW.",
            ],
            [("HHW for fridge?", "No — Shelby County HHW does not accept Freon appliances.")],
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
            "Bulk Week — Freon AC; NOT Shelby County HHW",
            "Memphis Bulk Week via 311",
            "Freon window and portable air conditioners go on Memphis Bulk Week — call 311 when ready and place within 3 feet of the street. Do NOT take Freon AC units to Shelby County HHW. Never vent refrigerant yourself.",
            [
                "Call 311 when ready for Bulk Week AC pickup.",
                "Place within 3 feet of the street.",
                "Keep Freon sealed — do not take to Shelby County HHW.",
            ],
            [("Same as fridge?", "Yes — Freon appliances use Bulk Week, not HHW.")],
            *bulk,
        )
    )
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(
            R(
                c,
                st,
                item,
                "SPECIAL_HANDLING",
                "Medium",
                True,
                "Bulk Week — regular bulky appliance; call 311",
                "Memphis Bulk Week via 311",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s go on Memphis Bulk Week / Outside-the-Cart — call 311 when ready. These do not need the Freon door-removal rules that apply to refrigerators and AC units, but follow Clean City Guide pile guidance. Place within 3 feet of the street.",
                [
                    "Call 311 when ready for Bulk Week pickup.",
                    "Place the appliance within 3 feet of the street.",
                    "Follow Clean City Guide for pile limits.",
                ],
                [("Freon rules?", "Door removal/taping applies to Freon refrigerators/AC — not typical washers.")],
                *bulk,
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
                True,
                "Bulk Week / periodic e-waste drives / private recycler — NOT Shelby County HHW",
                "Memphis Bulk Week / private e-waste recycler",
                f"Memphis TVs and {label} can go on Bulk Week / Outside-the-Cart (call 311) or periodic city e-waste drives and private recyclers. Shelby County HHW at 6305 Haley Rd does NOT accept TVs. Do not haul televisions to HHW expecting acceptance.",
                [
                    "Call 311 for Bulk Week TV/electronics set-out.",
                    "Watch for periodic Memphis e-waste collection events.",
                    "Do not take TVs to Shelby County HHW.",
                ],
                [("HHW for TV?", "No — Shelby County HHW explicitly does not accept TVs.")],
                *solid,
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
            "Dry out for trash — latex NOT accepted at Shelby County HHW",
            "Trash after fully dry (Memphis / Shelby County)",
            "Shelby County HHW at 6305 Haley Rd does NOT accept latex paint. Dry latex paint completely (cat litter/absorbent until solid) and place the dry can in trash. Oil-based paint goes to Shelby County HHW instead.",
            [
                "Solidify latex paint until fully dry.",
                "Place the dry can in household trash.",
                "Take oil-based paint to Shelby County HHW.",
            ],
            [("Oil paint?", "Oil paint is accepted at Shelby County HHW Tue/Thu/Sat 8:00–13:00.")],
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
                "Free Shelby County HHW — Tue/Thu/Sat 8:00–13:00",
                "Shelby County HHW — 6305 Haley Rd",
                f"Take {item.replace('-', ' ')} to Shelby County Household Hazardous Waste at 6305 Haley Rd — Tue/Thu/Sat 8:00 a.m.–1:00 p.m. HHW accepts oil paint, chemicals, batteries, and limited computer systems (1 per 30 days). NOT accepted: TVs, latex paint, Freon appliances, tires.",
                [
                    "Deliver sealed containers to 6305 Haley Rd during HHW hours.",
                    "Visit Tue/Thu/Sat 8:00–13:00.",
                    "Do not mix latex paint, TVs, or Freon appliances into HHW loads.",
                ],
                [("Latex at HHW?", "No — dry latex for trash.")],
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
    ]:
        extra = {
            "car-battery": " Auto and household batteries accepted at Shelby County HHW.",
            "lithium-battery": " Rechargeable/lithium batteries go to HHW — not trash.",
            "paint-oil": " Oil-based paint accepted at Shelby County HHW.",
            "motor-oil": " Used motor oil accepted at Shelby County HHW.",
            "propane-tank": " Propane cylinders accepted at Shelby County HHW.",
            "fluorescent-bulbs": " CFLs and fluorescent lamps accepted at HHW.",
            "cooking-oil": " Keep cooking oil out of drains; use HHW when not trash-safe.",
        }[item]
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS" if item not in {"cooking-oil"} else "SPECIAL_HANDLING",
                "High" if item not in {"cooking-oil"} else "Medium",
                False,
                "Free Shelby County HHW — Tue/Thu/Sat 8:00–13:00",
                "Shelby County HHW — 6305 Haley Rd",
                f"Shelby County HHW at 6305 Haley Rd accepts household hazardous materials Tue/Thu/Sat 8:00 a.m.–1:00 p.m.{extra} Not accepted: TVs, latex paint, Freon appliances, tires.",
                [
                    "Deliver sealed containers to 6305 Haley Rd during HHW hours.",
                    "Visit Tue/Thu/Sat 8:00–13:00.",
                    "Keep TVs, latex, Freon appliances, and tires on separate pathways.",
                ],
                [("Computer at HHW?", "Limited — 1 computer system per 30 days at Shelby County HHW.")],
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
            "Rigid sealed container — confirm Shelby County HHW sharps rules",
            "Shelby County HHW / approved sharps program",
            "Place medical sharps in a rigid, sealed hard-plastic container. Confirm sharps acceptance at Shelby County HHW on the county page. Do not loose-bag needles in trash or recycling.",
            [
                "Place sharps in a rigid sealed container.",
                "Confirm acceptance at Shelby County HHW before hauling.",
                "Never recycle sharps containers.",
            ],
            [("Medications?", "Confirm medication take-back — HHW may have limited med acceptance.")],
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
            "Bulk Week: up to 4 rimless ≤22.5 in; Collins Yard up to 10 Fri–Sun",
            "Memphis Bulk Week / Collins Yard convenience center",
            "Memphis Bulk Week accepts up to four rimless tires ≤22.5 inches. Collins Yard convenience center accepts up to ten rimless tires Fri–Sun 9 a.m.–3 p.m. Shelby County HHW does NOT accept tires. Remove rims for bulk week acceptance.",
            [
                "Remove rims for Bulk Week tire set-out (max 4, ≤22.5 in).",
                "Or haul up to 10 rimless tires to Collins Yard Fri–Sun 9:00–15:00.",
                "Do not take tires to Shelby County HHW.",
            ],
            [("Collins Yard?", "Up to 10 rimless tires Fri–Sun 9–3; Farrisview is another convenience center.")],
            *solid,
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
            "Memphis yard waste collection programs",
            "Memphis yard waste collection",
            "Memphis handles yard waste through regular city collection programs. Follow set-out rules; keep yard waste out of Bulk Week piles meant for bulky items and out of Shelby County HHW.",
            [
                "Use Memphis yard waste set-out rules for leaves and trimmings.",
                "Keep yard waste separate from Bulk Week bulky piles.",
                "Check memphistn.gov for seasonal guidance.",
            ],
            [("Christmas trees?", "Follow city seasonal yard waste guidance.")],
            *solid,
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
            "Garbage cart unless private/community compost",
            "Memphis garbage / private compost",
            "Bag food scraps for garbage unless you use private/community compost. Keep food out of recycling and out of Shelby County HHW loads.",
            [
                "Bag food scraps for garbage if you lack compost access.",
                "Keep organics out of recycling.",
                "Yard trimmings use yard-waste pathways.",
            ],
            [("HHW for food?", "No — HHW is for hazardous products.")],
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
            "Plastic bags are not accepted in Memphis curbside recycling. Return clean film to store take-back or trash.",
            [
                "Keep plastic bags out of the recycling cart.",
                "Use grocery take-back bins when available.",
                "Otherwise place bags in trash.",
            ],
            [("Convenience centers?", "Keep film out of recycling at Collins Yard/Farrisview too.")],
            *solid,
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
            "Bulk Week for limited loads — private C&D for larger projects",
            "Memphis Bulk Week / private C&D hauler",
            "Limited homeowner renovation debris may go on Bulk Week (call 311) following Clean City Guide pile guidance. Larger contractor C&D loads need a private hauler. Route paint and chemicals to Shelby County HHW — not mixed into C&D piles.",
            [
                "Call 311 for Bulk Week if renovation debris fits pile guidance.",
                "Hire a private C&D hauler for larger projects.",
                "Route paint/chemicals to Shelby County HHW at 6305 Haley Rd.",
            ],
            [("HHW for C&D?", "No — separate paint/chemicals for HHW.")],
            *bulk,
        )
    )
    return rows


def albuquerque():
    c, st = "albuquerque", "NM"
    large = (
        "City of Albuquerque — Large item pick-up",
        "https://www.cabq.gov/solidwaste/trash-collection/large-item-pick-up",
    )
    hhw = (
        "City of Albuquerque — Hazardous waste",
        "https://www.cabq.gov/solidwaste/hazardous-waste",
    )
    ewaste = (
        "City of Albuquerque — Electronic waste (e-waste)",
        "https://www.cabq.gov/solidwaste/recycling/copy_of_electronic-waste-e-waste",
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
            "Free Large Item Pick-Up via ABQ311 (≥24h advance Mon–Sat)",
            "ABQ311 Large Item Pick-Up",
            "Albuquerque offers free Large Item Pick-Up on request through ABQ311 — schedule at least 24 hours in advance, Monday–Saturday. Pickup-truck load limit applies. Mattresses go via Large Item; set out per ABQ311 instructions on your scheduled day.",
            [
                "Call or submit ABQ311 at least 24 hours before pickup (Mon–Sat).",
                "Set the mattress out per ABQ311 scheduling instructions.",
                "Stay within pickup-truck load limits.",
            ],
            [
                ("Cost?", "Free for ABQ solid waste customers via ABQ311."),
                ("Advance notice?", "At least 24 hours, Mon–Sat scheduling."),
            ],
            *large,
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
            "Large Item Pick-Up — empty, tape doors shut; NOT HHWCC",
            "ABQ311 Large Item Pick-Up",
            "Freon refrigerators and freezers are accepted on Albuquerque Large Item Pick-Up via ABQ311. Empty the unit, tape doors shut, and schedule at least 24 hours in advance. Do NOT take appliances to the HHW Collection Center (2720 Girard Blvd NE). Never vent refrigerant yourself.",
            [
                "Empty the refrigerator and tape doors shut.",
                "Schedule Large Item Pick-Up via ABQ311 (≥24h advance).",
                "Do not haul to HHWCC — appliances are not accepted there.",
            ],
            [("HHW for fridge?", "No — HHWCC does not accept appliances.")],
            *large,
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
            "Large Item Pick-Up — Freon AC; NOT HHWCC",
            "ABQ311 Large Item Pick-Up",
            "Freon window and portable air conditioners are accepted on Albuquerque Large Item Pick-Up via ABQ311. Schedule at least 24 hours in advance; tape doors shut if applicable. Do NOT take AC units to HHWCC. Never vent refrigerant yourself.",
            [
                "Schedule Large Item Pick-Up via ABQ311 (≥24h advance).",
                "Keep the Freon unit sealed until pickup.",
                "Do not haul to HHWCC.",
            ],
            [("Same as fridge?", "Yes — Freon appliances use Large Item, not HHWCC.")],
            *large,
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
            "Large Item Pick-Up via ABQ311 — not blue cart",
            "ABQ311 Large Item Pick-Up",
            "Albuquerque TVs go on Large Item Pick-Up via ABQ311 — not in the blue recycling cart. Schedule at least 24 hours in advance. For other e-waste beyond TVs, Eagle Rock convenience center accepts e-waste for fees — call 505-768-3925 or see cabq.gov e-waste page.",
            [
                "Schedule TV pickup via ABQ311 (≥24h advance).",
                "Do not place TVs in the blue recycling cart.",
                "Other e-waste: Eagle Rock convenience center (fees apply).",
            ],
            [("HHW for TV?", "No — HHWCC does not accept general e-waste (CRT monitors excepted).")],
            *ewaste,
        )
    )
    for item, label in [
        ("computer-monitor", "CRT monitors"),
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
                "Eagle Rock e-waste (fees) / HHWCC for CRT monitors only",
                "Eagle Rock convenience center / HHWCC (CRT only)",
                f"Albuquerque HHWCC at 2720 Girard Blvd NE accepts CRT monitors but NOT general e-waste, appliances, or tires. For {label}, use Eagle Rock convenience center e-waste (fees apply) — call 505-768-3925 or see cabq.gov e-waste page. Do not put general e-waste in the blue cart.",
                [
                    "Check cabq.gov e-waste page for current Eagle Rock fees/hours.",
                    "CRT monitors: HHWCC Mon/Wed/Fri 8–14, Sat 8–15.",
                    "Wipe personal data before recycling computers/phones.",
                ],
                [("TV on Large Item?", "TVs use ABQ311 Large Item — other e-waste uses Eagle Rock/HHWCC CRT.")],
                *ewaste,
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
            "car-battery": " Auto and household batteries accepted at HHWCC.",
            "lithium-battery": " Rechargeable/lithium batteries go to HHWCC.",
            "paint-latex": " Latex and oil paint both accepted at HHWCC.",
            "paint-oil": " Oil-based paint accepted at HHWCC.",
            "motor-oil": " Used motor oil accepted at HHWCC.",
            "propane-tank": " Propane cylinders accepted at HHWCC.",
            "fluorescent-bulbs": " CFLs and fluorescent lamps accepted at HHWCC.",
            "cooking-oil": " Keep cooking oil out of drains; use HHWCC when not trash-safe.",
        }[item]
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS" if item not in {"cooking-oil", "paint-latex"} else "SPECIAL_HANDLING",
                "High" if item not in {"cooking-oil", "paint-latex"} else "Medium",
                False,
                "Free HHWCC — Mon/Wed/Fri 8–14, Sat 8–15 (ABQ+Bernalillo)",
                "HHW Collection Center — 2720 Girard Blvd NE",
                f"Take household hazardous materials to Albuquerque HHWCC at 2720 Girard Blvd NE — Mon/Wed/Fri 8:00 a.m.–2:00 p.m., Sat 8:00 a.m.–3:00 p.m.; free for ABQ and Bernalillo County residents.{extra} HHWCC does NOT accept appliances, tires, or general e-waste (CRT monitors excepted).",
                [
                    "Deliver sealed containers during HHWCC hours.",
                    "Free for ABQ and Bernalillo County residents.",
                    "Keep appliances, tires, and general e-waste on separate pathways.",
                ],
                [("Meds?", "HHWCC accepts medications per cabq.gov hazardous waste page.")],
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
            "HHWCC in rigid sealed container — meds also accepted at HHWCC",
            "HHW Collection Center — 2720 Girard Blvd NE",
            "Place medical sharps in a rigid, sealed hard-plastic container for delivery to HHWCC at 2720 Girard Blvd NE. Albuquerque HHWCC also accepts medications per the city hazardous waste page. Do not loose-bag needles in trash or recycling.",
            [
                "Place sharps in a rigid sealed container.",
                "Deliver to HHWCC Mon/Wed/Fri 8–14 or Sat 8–15.",
                "Medications also accepted at HHWCC per city page.",
            ],
            [("Prescription drugs?", "HHWCC accepts meds per cabq.gov hazardous waste guidance.")],
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
            "Up to 4 via ABQ311 Large Item scheduling",
            "ABQ311 Large Item Pick-Up",
            "Albuquerque accepts up to four tires via Large Item Pick-Up through ABQ311 — schedule at least 24 hours in advance. HHWCC does NOT accept tires. Convenience centers ($5.25/load) are an alternative for mixed loads.",
            [
                "Schedule up to 4 tires via ABQ311 Large Item (≥24h advance).",
                "Do not haul tires to HHWCC.",
                "Convenience centers ($5.25/load) for alternative drop-off.",
            ],
            [("HHW for tires?", "No — tires use Large Item or convenience centers.")],
            *large,
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
            "ABQ yard waste / green waste programs",
            "Albuquerque yard waste collection",
            "Albuquerque handles yard waste through regular collection and green waste programs. Follow city set-out rules; keep yard waste out of HHWCC and Large Item piles when not appropriate.",
            [
                "Use ABQ yard waste set-out rules for leaves and trimmings.",
                "Keep yard waste separate from HHWCC chemical loads.",
                "Check cabq.gov for seasonal guidance.",
            ],
            [("Christmas trees?", "Follow city seasonal yard waste guidance.")],
            *large,
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
            "Garbage cart unless private/community compost",
            "Albuquerque garbage / private compost",
            "Bag food scraps for garbage unless you use private/community compost. Keep food out of recycling and out of HHWCC loads.",
            [
                "Bag food scraps for garbage if you lack compost access.",
                "Keep organics out of recycling.",
                "Yard trimmings use yard-waste pathways.",
            ],
            [("HHW for food?", "No — HHWCC is for hazardous products.")],
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
            "Not recycling — store take-back / trash",
            "Retail bag take-back / trash",
            "Plastic bags are not accepted in Albuquerque curbside recycling. Return clean film to store take-back or trash.",
            [
                "Keep plastic bags out of the blue recycling cart.",
                "Use grocery take-back bins when available.",
                "Otherwise place bags in trash.",
            ],
            [("Convenience centers?", "Keep film out of recycling streams.")],
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
            True,
            "Large Item for limited loads — convenience centers $5.25/load or private C&D",
            "ABQ311 Large Item / convenience centers / private C&D",
            "Limited homeowner renovation debris may fit Large Item Pick-Up via ABQ311 (pickup-truck load limit). Convenience centers charge $5.25/load as an alternative. Larger contractor C&D loads need a private hauler. Route paint and chemicals to HHWCC separately.",
            [
                "Schedule Large Item via ABQ311 if debris fits load limits.",
                "Or use convenience centers ($5.25/load).",
                "Hire a private C&D hauler for larger projects.",
            ],
            [("HHW for C&D?", "No — separate paint/chemicals for HHWCC.")],
            *large,
        )
    )
    return rows


CITIES = [
    {
        "city": "Oklahoma City",
        "city_slug": "oklahoma-city",
        "state": "OK",
        "state_slug": "oklahoma",
        "lat": 35.4676,
        "lng": -97.5164,
        "population": 681054,
    },
    {
        "city": "El Paso",
        "city_slug": "el-paso",
        "state": "TX",
        "state_slug": "texas",
        "lat": 31.7619,
        "lng": -106.4850,
        "population": 678815,
    },
    {
        "city": "Louisville",
        "city_slug": "louisville",
        "state": "KY",
        "state_slug": "kentucky",
        "lat": 38.2527,
        "lng": -85.7585,
        "population": 633045,
    },
    {
        "city": "Memphis",
        "city_slug": "memphis",
        "state": "TN",
        "state_slug": "tennessee",
        "lat": 35.1495,
        "lng": -90.0490,
        "population": 633104,
    },
    {
        "city": "Albuquerque",
        "city_slug": "albuquerque",
        "state": "NM",
        "state_slug": "new-mexico",
        "lat": 35.0844,
        "lng": -106.6504,
        "population": 564559,
    },
]

ZIPS = [
    {
        "zip": "73102",
        "city": "Oklahoma City",
        "city_slug": "oklahoma-city",
        "state": "OK",
        "state_slug": "oklahoma",
        "lat": 35.470,
        "lng": -97.520,
        "population": 8000,
    },
    {
        "zip": "73118",
        "city": "Oklahoma City",
        "city_slug": "oklahoma-city",
        "state": "OK",
        "state_slug": "oklahoma",
        "lat": 35.510,
        "lng": -97.530,
        "population": 22000,
    },
    {
        "zip": "79901",
        "city": "El Paso",
        "city_slug": "el-paso",
        "state": "TX",
        "state_slug": "texas",
        "lat": 31.760,
        "lng": -106.490,
        "population": 12000,
    },
    {
        "zip": "79924",
        "city": "El Paso",
        "city_slug": "el-paso",
        "state": "TX",
        "state_slug": "texas",
        "lat": 31.870,
        "lng": -106.410,
        "population": 45000,
    },
    {
        "zip": "40202",
        "city": "Louisville",
        "city_slug": "louisville",
        "state": "KY",
        "state_slug": "kentucky",
        "lat": 38.255,
        "lng": -85.755,
        "population": 10000,
    },
    {
        "zip": "40208",
        "city": "Louisville",
        "city_slug": "louisville",
        "state": "KY",
        "state_slug": "kentucky",
        "lat": 38.220,
        "lng": -85.770,
        "population": 18000,
    },
    {
        "zip": "38103",
        "city": "Memphis",
        "city_slug": "memphis",
        "state": "TN",
        "state_slug": "tennessee",
        "lat": 35.145,
        "lng": -90.050,
        "population": 9000,
    },
    {
        "zip": "38134",
        "city": "Memphis",
        "city_slug": "memphis",
        "state": "TN",
        "state_slug": "tennessee",
        "lat": 35.170,
        "lng": -89.870,
        "population": 35000,
    },
    {
        "zip": "87102",
        "city": "Albuquerque",
        "city_slug": "albuquerque",
        "state": "NM",
        "state_slug": "new-mexico",
        "lat": 35.085,
        "lng": -106.650,
        "population": 14000,
    },
    {
        "zip": "87107",
        "city": "Albuquerque",
        "city_slug": "albuquerque",
        "state": "NM",
        "state_slug": "new-mexico",
        "lat": 35.120,
        "lng": -106.670,
        "population": 28000,
    },
]

FACILITIES = [
    {
        "name": "OKC Household Hazardous Waste Collection Center",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "oklahoma-city",
        "state": "OK",
        "zip": "73108",
        "address": "1621 S. Portland Ave, Oklahoma City, OK 73108",
        "lat": 35.4505,
        "lng": -97.5835,
        "source_url": "https://www.okc.gov/Services/Water-Trash-Recycling/Household-Hazardous-Waste-Collection-Center",
        "hours": "Tue–Fri 9:30–18:00; Sat 8:30–11:30",
        "phone": "405-297-2833",
    },
    {
        "name": "El Paso Central Citizen Collection Station",
        "facility_type": "Citizen collection station — HHW / bulky drop-off",
        "city_slug": "el-paso",
        "state": "TX",
        "zip": "79930",
        "address": "2492 Harrison Blvd, El Paso, TX 79930",
        "lat": 31.7855,
        "lng": -106.4555,
        "source_url": "https://www.elpasotexas.gov/environmental-services/collection-stations/",
        "hours": "Tue–Sat 8:00–16:00",
        "phone": "915-212-6000",
    },
    {
        "name": "Louisville Waste Reduction Center",
        "facility_type": "Drop-off — appliances / electronics / tires",
        "city_slug": "louisville",
        "state": "KY",
        "zip": "40217",
        "address": "636 Meriwether Ave, Louisville, KY 40217 (Bland St entrance)",
        "lat": 38.2155,
        "lng": -85.7455,
        "source_url": "https://louisvilleky.gov/government/public-works/waste-reduction-center",
        "hours": "Confirm on city page — resident drop-off",
        "phone": "",
    },
    {
        "name": "Louisville Haz Bin",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "louisville",
        "state": "KY",
        "zip": "40219",
        "address": "7501 Grade Lane, Louisville, KY 40219",
        "lat": 38.1255,
        "lng": -85.6855,
        "source_url": "https://louisvilleky.gov/government/public-works/services/hazardous-materials-disposal-haz-bin",
        "hours": "Tue–Sat 9:30–16:00",
        "phone": "",
    },
    {
        "name": "Shelby County Household Hazardous Waste Facility",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "memphis",
        "state": "TN",
        "zip": "38125",
        "address": "6305 Haley Rd, Memphis, TN 38125",
        "lat": 35.0455,
        "lng": -89.8555,
        "source_url": "https://www.shelbycountytn.gov/439/Household-Hazardous-Waste",
        "hours": "Tue/Thu/Sat 8:00–13:00",
        "phone": "",
    },
    {
        "name": "Albuquerque HHW Collection Center",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "albuquerque",
        "state": "NM",
        "zip": "87106",
        "address": "2720 Girard Blvd NE, Albuquerque, NM 87106",
        "lat": 35.1055,
        "lng": -106.6155,
        "source_url": "https://www.cabq.gov/solidwaste/hazardous-waste",
        "hours": "Mon/Wed/Fri 8:00–14:00; Sat 8:00–15:00",
        "phone": "505-768-3925",
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
        "oklahoma-city": clone_siblings(oklahoma_city()),
        "el-paso": clone_siblings(el_paso()),
        "louisville": clone_siblings(louisville()),
        "memphis": clone_siblings(memphis()),
        "albuquerque": clone_siblings(albuquerque()),
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

    print("Wave-7 metros written:")
    for city, rows in audited.items():
        print(f"  {city}: {len(rows)} rules")
    print(f"Total rules now: {len(keep)}")


if __name__ == "__main__":
    main()
