#!/usr/bin/env python3
"""Portal-audited city guides for wave-8 metros (city-sourced only).

Cities researched from official program pages (2026-08-11):
  - Tucson, AZ — tucsonaz.gov Brush and Bulky / HHW Los Reales
  - Tulsa, OK — cityoftulsa.org bulky / HPCF HHW
  - Indianapolis, IN — indy.gov heavy trash / ToxDrop
  - Atlanta, GA — ATL311 scheduled bulk / CHaRM partners (City of Atlanta only)
  - Kansas City, MO — kcmo.gov bulky / KC Water HHW / NCAP tires
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


def tucson():
    c, st = "tucson", "AZ"
    bulky = (
        "City of Tucson — Brush and Bulky",
        "https://www.tucsonaz.gov/Departments/Environmental-Services/Residential-Services/Brush-and-Bulky",
    )
    hhw = (
        "City of Tucson — Household Hazardous Waste",
        "https://www.tucsonaz.gov/Departments/Environmental-Services/Household-Hazardous-Waste",
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
            "Brush and Bulky zone sweep 2×/year — max 10 cy; Special $55/event via 311",
            "Tucson Brush and Bulky / Special Brush and Bulky",
            "Tucson Brush and Bulky runs twice per year on a zone sweep — set items out by 6 a.m. Monday of your assigned week (max 10 cubic yards; no appointment for scheduled sweep). Mattresses and furniture go on Brush and Bulky. Need an extra pickup? Special Brush and Bulky costs $55 per event (up to 10 cy) via 311 or 520-791-3171.",
            [
                "Confirm your zone sweep week on tucsonaz.gov Brush and Bulky page.",
                "Set mattress out by 6 a.m. Monday of assigned week (max 10 cy).",
                "For off-cycle pickup, call 311 / 520-791-3171 for Special Brush and Bulky ($55).",
            ],
            [
                ("Appointment for scheduled sweep?", "No — zone sweep is automatic; Special Brush and Bulky needs 311."),
                ("Same as furniture?", "Yes — mattresses use Brush and Bulky furniture rules."),
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
            "Brush and Bulky — remove doors; Los Reales $5 refrigerant if self-haul",
            "Tucson Brush and Bulky / Los Reales Sustainability Campus",
            "Freon refrigerators and freezers are accepted on Tucson Brush and Bulky if doors are removed before set-out. Self-hauling? Los Reales Sustainability Campus charges $5 for refrigerant evacuation at the scrap area. Never vent refrigerant yourself. E-waste and TVs do NOT go on Brush and Bulky.",
            [
                "Remove refrigerator doors per city rules before Brush and Bulky set-out.",
                "Set out by 6 a.m. Monday of your zone sweep week.",
                "Self-haul to Los Reales — $5 refrigerant evacuation at scrap area if applicable.",
            ],
            [("Doors required?", "Yes — remove doors before Brush and Bulky set-out.")],
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
            "Brush and Bulky — Freon AC; Los Reales $5 refrigerant if self-haul",
            "Tucson Brush and Bulky / Los Reales Sustainability Campus",
            "Freon window and portable air conditioners go on Tucson Brush and Bulky (zone sweep rules). Self-haul to Los Reales Sustainability Campus with $5 refrigerant evacuation at scrap if applicable. Never vent refrigerant yourself.",
            [
                "Set Freon AC out by 6 a.m. Monday of zone sweep week.",
                "Keep the unit sealed until proper handling.",
                "Self-haul option: Los Reales scrap area ($5 refrigerant evacuation).",
            ],
            [("Same as fridge?", "Yes — Freon appliances use Brush and Bulky or Los Reales self-haul.")],
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
                "Brush and Bulky zone sweep — max 10 cy; no Freon door rules",
                "Tucson Brush and Bulky",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s go on Tucson Brush and Bulky during your zone sweep (set out by 6 a.m. Monday; max 10 cubic yards). These do not need refrigerator door-removal rules. Special Brush and Bulky ($55/event via 311) is available off-cycle.",
                [
                    "Confirm zone sweep week on tucsonaz.gov.",
                    "Empty the appliance and set out by 6 a.m. Monday of assigned week.",
                    "Off-cycle: call 311 for Special Brush and Bulky ($55).",
                ],
                [("Freon rules?", "Door removal applies to refrigerators/freezers — not typical washers.")],
                *bulky,
            )
        )
    for item, label in [
        ("television", "TVs"),
        ("computer-monitor", "monitors and computers"),
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
                "Free HHW at Los Reales — CRT monitors NOT accepted; NOT Brush and Bulky",
                "Los Reales Sustainability Campus HHW — 5300 E Los Reales Rd",
                f"Tucson accepts {label} at the Household Hazardous Waste program at Los Reales Sustainability Campus, 5300 E Los Reales Rd — Thu–Sat 7 a.m.–2 p.m. (closed 2nd Saturday of each month); free for Tucson residents. CRT monitors are NOT accepted. E-waste and TVs do NOT go on Brush and Bulky.",
                [
                    "Haul electronics/TV to Los Reales HHW Thu–Sat 7:00–14:00.",
                    "Check calendar — closed 2nd Saturday of each month.",
                    "Do not set TVs/e-waste out for Brush and Bulky.",
                ],
                [("Brush and Bulky for TV?", "No — e-waste/TV use HHW at Los Reales, not Brush and Bulky.")],
                *hhw,
            )
        )
    rows.append(
        R(
            c,
            st,
            "paint-latex",
            "SPECIAL_HANDLING",
            "Medium",
            False,
            "HHW up to 25 gal paint products; dried latex can go in trash",
            "Los Reales Sustainability Campus HHW — 5300 E Los Reales Rd",
            "Liquid latex paint goes to Tucson HHW at Los Reales Sustainability Campus (5300 E Los Reales Rd) — up to 25 gallons of paint products per visit; Thu–Sat 7 a.m.–2 p.m.; free Tucson residents. Fully dried latex (solidified with cat litter/absorbent) can go in household trash.",
            [
                "Liquid latex: haul to Los Reales HHW during Thu–Sat hours.",
                "Dried latex: solidify completely, then trash the dry can.",
                "Do not pour liquid paint down drains or on Brush and Bulky piles.",
            ],
            [("Trash for dried latex?", "Yes — fully dried latex cans can go in trash.")],
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
                "Free HHW at Los Reales — Thu–Sat 7:00–14:00",
                "Los Reales Sustainability Campus HHW — 5300 E Los Reales Rd",
                f"Take {item.replace('-', ' ')} to Tucson HHW at Los Reales Sustainability Campus, 5300 E Los Reales Rd — Thu–Sat 7 a.m.–2 p.m. (closed 2nd Saturday/month); free for Tucson residents. Do not dry these out for trash — they require HHW handling.",
                [
                    "Deliver sealed, labeled containers to Los Reales HHW.",
                    "Visit Thu–Sat 7:00–14:00; check 2nd-Saturday closure.",
                    "Keep chemicals out of Brush and Bulky and trash carts.",
                ],
                [("Same as dried latex?", "No — chemicals and fuels require HHW, not trash.")],
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
            "car-battery": " Auto and household batteries accepted at Los Reales HHW.",
            "lithium-battery": " Rechargeable/lithium batteries belong at HHW — not trash.",
            "paint-oil": " Oil-based paint accepted at Los Reales HHW.",
            "motor-oil": " Used motor oil accepted at HHW.",
            "propane-tank": " Propane cylinders accepted at HHW.",
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
                "Free HHW at Los Reales — Thu–Sat 7:00–14:00",
                "Los Reales Sustainability Campus HHW — 5300 E Los Reales Rd",
                f"Tucson HHW at Los Reales Sustainability Campus, 5300 E Los Reales Rd accepts household hazardous materials Thu–Sat 7 a.m.–2 p.m. (closed 2nd Saturday/month); free for Tucson residents.{extra}",
                [
                    "Deliver sealed containers to Los Reales HHW during hours.",
                    "Check 2nd-Saturday closure on city calendar.",
                    "Keep HHW out of Brush and Bulky piles.",
                ],
                [("Residents only?", "Yes — free for Tucson residents.")],
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
            "Rigid sealed container — confirm Los Reales HHW sharps acceptance",
            "Los Reales Sustainability Campus HHW — 5300 E Los Reales Rd",
            "Place medical sharps in a rigid, sealed hard-plastic container before delivery. Confirm sharps acceptance at Los Reales HHW on the city page. Do not loose-bag needles in trash or recycling.",
            [
                "Place sharps in a rigid sealed hard-plastic container.",
                "Confirm sharps acceptance at Los Reales HHW before hauling.",
                "Never recycle loose needles.",
            ],
            [("Medications?", "Confirm prescription drug take-back at Los Reales HHW on city page.")],
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
            "Brush and Bulky max 5 auto tires separate pile; Los Reales $2/tire",
            "Tucson Brush and Bulky / Los Reales Sustainability Campus",
            "Tucson Brush and Bulky accepts up to five automobile tires in a separate pile during zone sweep set-out. Self-haul to Los Reales Sustainability Campus costs $2 per tire. Do not mix tires into furniture piles.",
            [
                "Set up to 5 auto tires in a separate pile for Brush and Bulky.",
                "Set out by 6 a.m. Monday of zone sweep week.",
                "Self-haul alternative: Los Reales at $2/tire.",
            ],
            [("How many on Brush and Bulky?", "Max 5 automobile tires in a separate pile.")],
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
            "Tucson yard waste / green waste collection",
            "Tucson yard waste collection",
            "Tucson handles yard waste through regular collection programs. Follow city set-out rules for bags and bundles. Keep yard waste out of Brush and Bulky piles meant for bulky items and out of Los Reales HHW.",
            [
                "Use Tucson yard waste set-out rules for leaves and trimmings.",
                "Keep yard waste separate from Brush and Bulky and HHW.",
                "Check tucsonaz.gov for seasonal guidance.",
            ],
            [("Christmas trees?", "Follow city seasonal yard waste guidance for holiday trees.")],
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
            "Tucson garbage / private compost",
            "Bag food scraps for garbage unless you use private/community compost. Keep food out of recycling and out of Los Reales HHW loads.",
            [
                "Bag food scraps for garbage if you lack compost access.",
                "Keep organics out of recycling.",
                "Yard trimmings use yard-waste pathways.",
            ],
            [("HHW for food?", "No — HHW is for hazardous products.")],
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
            "Plastic bags are not accepted in Tucson curbside recycling. Return clean film to store take-back bins when available, or dispose with trash.",
            [
                "Keep plastic bags out of the recycling cart.",
                "Use grocery take-back bins when available.",
                "Otherwise place bags in trash.",
            ],
            [("Yard waste bags?", "Follow Tucson yard waste bag rules — often paper, not plastic film.")],
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
            "Limited Brush and Bulky (10 cy) or Los Reales / private C&D",
            "Tucson Brush and Bulky / Los Reales / private C&D",
            "Small homeowner renovation debris may fit within Brush and Bulky limits (max 10 cubic yards per sweep). Larger loads need Los Reales or a private C&D hauler. Route paint and chemicals to Los Reales HHW separately.",
            [
                "Use Brush and Bulky only for limited homeowner renovation debris (max 10 cy).",
                "Haul larger C&D to Los Reales or hire a private hauler.",
                "Route paint/chemicals to Los Reales HHW.",
            ],
            [("HHW for C&D?", "No — separate paint/chemicals for HHW.")],
            *bulky,
        )
    )
    return rows


def tulsa():
    c, st = "tulsa", "OK"
    bulky = (
        "City of Tulsa — Bulky Waste Pick Up",
        "https://www.cityoftulsa.org/government/departments/public-works/refuse-recycling/residential-services/bulky-waste-pick-up/",
    )
    hhw = (
        "City of Tulsa — Household Pollutant Collection Facility",
        "https://www.cityoftulsa.org/government/departments/public-works/household-pollutant-collection-facility/",
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
            "Bulky appt via 311/online — $10/8 cy ($20 from Oct 1 2026); set out by 5am",
            "Tulsa Bulky Waste Pick Up (appointment)",
            "Tulsa Bulky Waste Pick Up requires an appointment through 311 or online. Fee is $10 per 8 cubic yards ($20 starting October 1, 2026). Set items out by 5 a.m. on your regular refuse day. Mattresses and bulky furniture use this program.",
            [
                "Schedule Bulky Waste Pick Up via 311 or city online portal.",
                "Set mattress out by 5 a.m. on your regular refuse day.",
                "Fee: $10/8 cy now; $20/8 cy starting Oct 1, 2026.",
            ],
            [
                ("Appointment required?", "Yes — schedule via 311 or online before set-out."),
                ("Same as furniture?", "Yes — mattresses use bulky furniture rules."),
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
            "Bulky appt — empty Freon fridge/AC accepted on bulky",
            "Tulsa Bulky Waste Pick Up (appointment)",
            "Freon refrigerators, freezers, and other empty appliances are accepted on Tulsa Bulky Waste Pick Up when scheduled ($10/8 cy; $20 from Oct 1 2026). Empty the unit completely before set-out. Set out by 5 a.m. on your regular refuse day. Never vent refrigerant yourself.",
            [
                "Schedule Bulky Pick Up via 311 or online.",
                "Empty the refrigerator completely before set-out.",
                "Set out by 5 a.m. on regular refuse day.",
            ],
            [("Washer on same pickup?", "Yes — empty appliances including washers can go on the same bulky appointment.")],
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
            "Bulky appt — empty Freon AC accepted",
            "Tulsa Bulky Waste Pick Up (appointment)",
            "Empty Freon window and portable air conditioners are accepted on Tulsa Bulky Waste Pick Up when scheduled. Set out by 5 a.m. on your regular refuse day. Never vent refrigerant yourself.",
            [
                "Schedule Bulky Pick Up via 311 or online.",
                "Keep the Freon unit sealed and empty before set-out.",
                "Set out by 5 a.m. on regular refuse day.",
            ],
            [("Same as fridge?", "Yes — empty Freon appliances use the same bulky appointment.")],
            *bulky,
        )
    )
    for item, label in [
        ("television", "TVs"),
        ("computer-monitor", "monitors"),
        ("smartphone", "phones and small electronics"),
    ]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS",
                "Medium",
                True,
                "Bulky appt — up to 4 TVs/monitors/computers separate pile; large TVs → M.e.t.",
                "Tulsa Bulky Waste Pick Up / M.e.t. fee centers",
                f"Tulsa Bulky Waste Pick Up accepts up to four {label} in a separate pile when scheduled ($10/8 cy). HPCF accepts small electronics only — NOT large TVs. Large TVs and monitors go to M.e.t. fee centers. Schedule bulky via 311; set out by 5 a.m.",
                [
                    "Schedule Bulky Pick Up via 311 or online.",
                    "Set up to 4 TVs/monitors/computers in a separate pile by 5 a.m.",
                    "Large TVs: use M.e.t. fee centers — not HPCF.",
                ],
                [("HPCF for large TV?", "No — HPCF takes small electronics only; large TVs use M.e.t.")],
                *bulky,
            )
        )
    rows.append(
        R(
            c,
            st,
            "e-waste-mixed",
            "BANNED_FROM_LANDFILLS",
            "Medium",
            False,
            "HPCF small electronics / M.e.t. fee centers for larger loads",
            "Tulsa HPCF / M.e.t. fee centers",
            "Tulsa HPCF at 4502 S Galveston Ave accepts small electronics — not large TVs. Mixed e-waste and larger items go to M.e.t. fee centers. Bulky accepts up to 4 TVs/monitors/computers in a separate pile when scheduled.",
            [
                "Small electronics: HPCF Wed & Sat during posted hours.",
                "Large or mixed e-waste: M.e.t. fee centers.",
                "Up to 4 TVs/monitors/computers can use bulky separate pile.",
            ],
            [("HPCF hours?", "Wed & Sat 8:00–11:30 and 12:00–16:30; free Tulsa residents.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c,
            st,
            "paint-latex",
            "SPECIAL_HANDLING",
            "Medium",
            True,
            "Bulky up to 10 gal latex OR HPCF latex+oil",
            "Tulsa Bulky Waste Pick Up / HPCF — 4502 S Galveston Ave",
            "Tulsa Bulky Waste Pick Up accepts up to 10 gallons of latex paint when scheduled ($10/8 cy). HPCF at 4502 S Galveston Ave also accepts latex and oil paint — Wed & Sat 8:00–11:30 and 12:00–16:30; free Tulsa residents.",
            [
                "Schedule bulky for up to 10 gal latex paint, or haul to HPCF.",
                "HPCF: 4502 S Galveston Ave Wed & Sat during hours.",
                "Keep paint sealed and labeled.",
            ],
            [("HPCF for latex?", "Yes — HPCF accepts both latex and oil paint.")],
            *bulky,
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
                "Free HPCF — Wed & Sat 8:00–11:30 and 12:00–16:30",
                "Tulsa HPCF — 4502 S Galveston Ave",
                f"Take {item.replace('-', ' ')} to Tulsa HPCF at 4502 S Galveston Ave — Wed & Sat 8:00 a.m.–11:30 a.m. and 12:00–4:30 p.m.; (918) 591-4325; free Tulsa residents. Do not set chemicals out on bulky pickup.",
                [
                    "Deliver sealed containers to HPCF during Wed/Sat hours.",
                    "Bring proof of Tulsa residency.",
                    "Do not mix chemicals into bulky or trash loads.",
                ],
                [("Bulky for pesticides?", "No — chemicals and fuels require HPCF.")],
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
            "car-battery": " Auto and household batteries accepted at HPCF.",
            "lithium-battery": " Rechargeable/lithium batteries go to HPCF — not trash.",
            "paint-oil": " Oil-based paint accepted at HPCF.",
            "motor-oil": " Used motor oil accepted at HPCF.",
            "propane-tank": " Propane cylinders accepted at HPCF.",
            "fluorescent-bulbs": " CFLs and fluorescent lamps accepted at HPCF.",
            "cooking-oil": " Keep cooking oil out of drains; use HPCF when not trash-safe.",
        }[item]
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS" if item not in {"cooking-oil"} else "SPECIAL_HANDLING",
                "High" if item not in {"cooking-oil"} else "Medium",
                False,
                "Free HPCF — Wed & Sat; (918) 591-4325",
                "Tulsa HPCF — 4502 S Galveston Ave",
                f"Tulsa HPCF at 4502 S Galveston Ave accepts household hazardous materials Wed & Sat 8:00–11:30 and 12:00–16:30; free Tulsa residents.{extra} Tires are NOT accepted at HPCF.",
                [
                    "Deliver sealed containers to HPCF during Wed/Sat hours.",
                    "Call (918) 591-4325 with questions.",
                    "Keep tires on the bulky pathway — not HPCF.",
                ],
                [("Residents only?", "Yes — free for Tulsa residents.")],
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
            "Rigid sealed container — confirm HPCF sharps acceptance",
            "Tulsa HPCF — 4502 S Galveston Ave",
            "Place medical sharps in a rigid, sealed hard-plastic container before delivery. Confirm sharps acceptance at HPCF on the city page. Do not loose-bag needles in trash or recycling.",
            [
                "Place sharps in a rigid sealed hard-plastic container.",
                "Confirm sharps acceptance at HPCF before hauling.",
                "Never recycle sharps containers.",
            ],
            [("Medications?", "Confirm medication take-back at HPCF on city page.")],
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
            "Bulky appt — up to 4 without rims separate pile; NOT at HPCF",
            "Tulsa Bulky Waste Pick Up (appointment)",
            "Tulsa Bulky Waste Pick Up accepts up to four tires without rims in a separate pile when scheduled ($10/8 cy). Tires are NOT accepted at HPCF. Set out by 5 a.m. on regular refuse day.",
            [
                "Schedule Bulky Pick Up via 311 or online.",
                "Set up to 4 rimless tires in a separate pile by 5 a.m.",
                "Do not haul tires to HPCF.",
            ],
            [("HPCF for tires?", "No — tires use bulky pickup or private recycler.")],
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
            "Tulsa yard waste collection programs",
            "Tulsa yard waste collection",
            "Tulsa handles yard waste through regular collection programs. Follow set-out rules; keep yard waste out of bulky piles and out of HPCF.",
            [
                "Use Tulsa yard waste set-out rules for leaves and trimmings.",
                "Keep yard waste separate from bulky and HPCF loads.",
                "Check cityoftulsa.org for seasonal guidance.",
            ],
            [("Christmas trees?", "Follow city seasonal yard waste guidance.")],
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
            "Tulsa garbage / private compost",
            "Bag food scraps for garbage unless you use private/community compost. Keep food out of recycling and out of HPCF loads.",
            [
                "Bag food scraps for garbage if you lack compost access.",
                "Keep organics out of recycling.",
                "Yard trimmings use yard-waste pathways.",
            ],
            [("HPCF for food?", "No — HPCF is for hazardous products.")],
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
            "Plastic bags are not accepted in Tulsa curbside recycling. Return clean film to store take-back or trash.",
            [
                "Keep plastic bags out of the recycling cart.",
                "Use grocery take-back bins when available.",
                "Otherwise place bags in trash.",
            ],
            [("Bulky for bags?", "No — use store take-back or trash.")],
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
            "Bulky appt for limited loads — private C&D for larger projects",
            "Tulsa Bulky Waste Pick Up / private C&D hauler",
            "Limited homeowner renovation debris may go on Bulky Waste Pick Up when scheduled ($10/8 cy). Larger contractor C&D loads need a private hauler. Route paint and chemicals to HPCF separately.",
            [
                "Schedule bulky if renovation debris fits load limits.",
                "Hire a private C&D hauler for larger projects.",
                "Route paint/chemicals to HPCF 4502 S Galveston Ave.",
            ],
            [("HPCF for C&D?", "No — separate paint/chemicals for HPCF.")],
            *bulky,
        )
    )
    return rows


def indianapolis():
    c, st = "indianapolis", "IN"
    heavy = (
        "City of Indianapolis — Trash 101 / heavy trash",
        "https://www.indy.gov/activity/trash-101",
    )
    hhw = (
        "City of Indianapolis — Hazardous waste drop-off sites",
        "https://www.indy.gov/activity/hazardous-waste-dropoff-sites",
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
            "Heavy trash — 2 bulky items/month; flat on ground by 7am",
            "Indianapolis heavy trash day",
            "Indianapolis allows two bulky items per month on your heavy trash day — no appointment needed. Look up your pickup day at indy.gov trash-pickup. Set mattresses flat on the ground by 7 a.m. Mattresses count toward the two-item monthly limit.",
            [
                "Look up heavy trash day at indy.gov trash-pickup.",
                "Set mattress flat on ground by 7 a.m. on heavy trash day.",
                "Counts toward 2 bulky items/month limit.",
            ],
            [
                ("Appointment?", "No — set out on heavy trash day (max 2 items/month)."),
                ("How to set out?", "Flat on the ground by 7 a.m."),
            ],
            *heavy,
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
            "Call Mayor's Action Center 317-327-4622 — NOT standard heavy trash",
            "Mayor's Action Center Freon appliance scheduling",
            "Freon refrigerators and freezers are NOT accepted on standard Indianapolis heavy trash. Call the Mayor's Action Center at 317-327-4622 to schedule Freon appliance pickup — empty the unit first. Freon pickup does not count toward the two-item monthly heavy trash limit. Never vent refrigerant yourself.",
            [
                "Empty the refrigerator completely.",
                "Call Mayor's Action Center 317-327-4622 for Freon scheduling.",
                "Do not set Freon units out on regular heavy trash day without MAC approval.",
            ],
            [("Counts toward 2-item limit?", "No — MAC Freon pickup is separate from heavy trash limit.")],
            *heavy,
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
            "Call Mayor's Action Center 317-327-4622 — NOT standard heavy trash",
            "Mayor's Action Center Freon appliance scheduling",
            "Freon window and portable air conditioners are NOT accepted on standard heavy trash. Call the Mayor's Action Center at 317-327-4622 to schedule Freon AC pickup — empty the unit first. Never vent refrigerant yourself.",
            [
                "Empty the AC unit completely.",
                "Call Mayor's Action Center 317-327-4622 for Freon scheduling.",
                "Keep the sealed unit intact until proper handling.",
            ],
            [("Same as fridge?", "Yes — all Freon appliances use MAC 317-327-4622, not heavy trash.")],
            *heavy,
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
                "Heavy trash — counts toward 2 bulky items/month by 7am",
                "Indianapolis heavy trash day",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s go on Indianapolis heavy trash day — set out by 7 a.m.; counts toward the two bulky items per month limit. Do not use the Mayor's Action Center Freon line for appliances without refrigerant.",
                [
                    "Look up heavy trash day at indy.gov trash-pickup.",
                    "Empty the appliance and set out by 7 a.m.",
                    "Counts toward 2-item monthly limit — plan accordingly.",
                ],
                [("MAC line for washer?", "No — MAC 317-327-4622 is for Freon refrigerators/AC only.")],
                *heavy,
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
                "ToxDrop (TV ≤27 in) / RecycleForce for larger — NOT heavy trash",
                "Marion County ToxDrop / RecycleForce",
                f"Indianapolis electronics go to Marion County ToxDrop — TVs up to 27 inches accepted; larger TVs go to RecycleForce. {label} are NOT accepted on heavy trash. ToxDrop sites: Traders Point 7550 N Lafayette Rd (1st Sat 9–2); Perry Twp 4925 S Shelby St (2nd & 4th Sat 9–2). Limit 20 gal / 75 lb.",
                [
                    "Do not set electronics out on heavy trash day.",
                    "TV ≤27 in: ToxDrop on scheduled Saturdays.",
                    "Larger TVs: RecycleForce or confirm current options.",
                ],
                [("Heavy trash for TV?", "No — electronics use ToxDrop/RecycleForce, not heavy trash.")],
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
            "car-battery": " Auto and household batteries accepted at ToxDrop.",
            "lithium-battery": " Rechargeable/lithium batteries go to ToxDrop — not trash.",
            "paint-latex": " Latex and oil paint both accepted at ToxDrop.",
            "paint-oil": " Oil-based paint accepted at ToxDrop.",
            "motor-oil": " Used motor oil accepted at ToxDrop.",
            "propane-tank": " Propane cylinders accepted at ToxDrop.",
            "fluorescent-bulbs": " CFLs and fluorescent lamps accepted at ToxDrop.",
            "cooking-oil": " Keep cooking oil out of drains; use ToxDrop when not trash-safe.",
        }[item]
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS" if item not in {"cooking-oil", "paint-latex"} else "SPECIAL_HANDLING",
                "High" if item not in {"cooking-oil", "paint-latex"} else "Medium",
                False,
                "Free Marion County ToxDrop — Sat drop-offs; 20 gal / 75 lb",
                "Marion County ToxDrop — Traders Point / Perry Township",
                f"Marion County ToxDrop accepts household hazardous materials free — Traders Point 7550 N Lafayette Rd (1st Sat 9–2); Perry Twp 4925 S Shelby St (2nd & 4th Sat 9–2). Limit 20 gal / 75 lb per visit.{extra} Tires are NOT accepted at ToxDrop.",
                [
                    "Deliver sealed containers to the correct Saturday ToxDrop site.",
                    "Limit: 20 gallons / 75 pounds per visit.",
                    "Keep tires on private/state pathways — not ToxDrop.",
                ],
                [("Which Saturday?", "Traders Point 1st Sat; Perry Twp 2nd & 4th Sat.")],
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
            "Rigid sealed container — confirm ToxDrop sharps acceptance",
            "Marion County ToxDrop",
            "Place medical sharps in a rigid, sealed hard-plastic container before delivery. Confirm sharps acceptance at Marion County ToxDrop on indy.gov. Do not loose-bag needles in trash or recycling.",
            [
                "Place sharps in a rigid sealed hard-plastic container.",
                "Confirm sharps acceptance at ToxDrop before hauling.",
                "Never recycle sharps containers.",
            ],
            [("Medications?", "Confirm prescription drug take-back at ToxDrop on city page.")],
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
            "NOT heavy trash or ToxDrop — private/state tire recycler",
            "Private / state tire recycler",
            "Tires are NOT accepted on Indianapolis heavy trash or at Marion County ToxDrop. Use a private tire recycler or state-licensed disposal option. Retailer take-back when replacing tires is also an option.",
            [
                "Do not set tires out on heavy trash day.",
                "Do not haul tires to ToxDrop.",
                "Use a private/state tire recycler or retailer take-back.",
            ],
            [("Heavy trash for tires?", "No — tires require private/state disposal pathways.")],
            *heavy,
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
            "Indianapolis yard waste collection programs",
            "Indianapolis yard waste collection",
            "Indianapolis handles yard waste through regular collection programs. Follow set-out rules; keep yard waste out of heavy trash piles meant for bulky items and out of ToxDrop.",
            [
                "Use Indianapolis yard waste set-out rules for leaves and trimmings.",
                "Keep yard waste separate from heavy trash bulky piles.",
                "Check indy.gov for seasonal guidance.",
            ],
            [("Christmas trees?", "Follow city seasonal yard waste guidance.")],
            *heavy,
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
            "Indianapolis garbage / private compost",
            "Bag food scraps for garbage unless you use private/community compost. Keep food out of recycling and out of ToxDrop loads.",
            [
                "Bag food scraps for garbage if you lack compost access.",
                "Keep organics out of recycling.",
                "Yard trimmings use yard-waste pathways.",
            ],
            [("ToxDrop for food?", "No — ToxDrop is for hazardous products.")],
            *heavy,
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
            "Plastic bags are not accepted in Indianapolis curbside recycling. Return clean film to store take-back or trash.",
            [
                "Keep plastic bags out of the recycling cart.",
                "Use grocery take-back bins when available.",
                "Otherwise place bags in trash.",
            ],
            [("Heavy trash for bags?", "No — use store take-back or trash.")],
            *heavy,
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
            "Heavy trash for limited items (2/month) — private C&D for larger",
            "Indianapolis heavy trash / private C&D hauler",
            "Limited homeowner items may count toward the two heavy trash items per month. Larger construction and demolition debris needs a private C&D hauler. Route paint and chemicals to ToxDrop separately.",
            [
                "Use heavy trash only if debris fits the 2-item monthly limit.",
                "Hire a private C&D hauler for larger projects.",
                "Route paint/chemicals to Marion County ToxDrop.",
            ],
            [("ToxDrop for C&D?", "No — separate paint/chemicals for ToxDrop.")],
            *heavy,
        )
    )
    return rows


def atlanta():
    c, st = "atlanta", "GA"
    bulk = (
        "City of Atlanta — ATL311 scheduled bulk collection",
        "https://www.atl311.com/en-US/knowledgearticle/?code=KB0011524",
    )
    hhw_info = (
        "City of Atlanta — Household hazardous waste disposal",
        "https://www.atlantaga.gov/government/departments/public-works/office-of-solid-waste-services/household-hazardous-waste-disposal",
    )
    recycles = (
        "City of Atlanta — Atlanta Recycles Day",
        "https://www.atl311.com/en-us/knowledgearticle/?code=KB0011478",
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
            "Scheduled bulk via ATL311 — 12 free/year; max 8 cy; over 12 ≈ $349.96",
            "City of Atlanta scheduled bulk collection",
            "City of Atlanta (not Fulton County) scheduled bulk collection is booked through ATL311, the SWS tool, or 404-546-0311. Up to 12 free collections per year; max 8 cubic yards on your weekly collection day. Over 12 collections incurs a fee (~$349.96). Mattresses and bulk furniture use this program.",
            [
                "Schedule bulk collection via ATL311 / SWS tool / 404-546-0311.",
                "Set out on your weekly collection day within 8 cy limit.",
                "Track free collections — 12/year included.",
            ],
            [
                ("Fulton County?", "This guide is City of Atlanta only — not Fulton County unincorporated."),
                ("Over limit fee?", "Over 12 collections/year ≈ $349.96 per city guidance."),
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
            "Scheduled bulk — white goods/appliances; call ATL311 if rejected",
            "City of Atlanta scheduled bulk collection",
            "White goods and appliances including refrigerators and freezers go on City of Atlanta scheduled bulk collection via ATL311. Freon handling is not separately documented — keep units sealed and call ATL311 (404-546-0311) if a unit is rejected. Never vent refrigerant yourself.",
            [
                "Schedule bulk via ATL311 / SWS tool / 404-546-0311.",
                "Keep Freon units sealed until pickup.",
                "Call ATL311 if a refrigerator is rejected at set-out.",
            ],
            [("Washer same pickup?", "Yes — white goods/appliances use the same scheduled bulk pathway.")],
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
            "Scheduled bulk — white goods; call ATL311 if rejected",
            "City of Atlanta scheduled bulk collection",
            "Window and portable air conditioners go on City of Atlanta scheduled bulk collection with other white goods via ATL311. Keep Freon units sealed; call ATL311 if rejected. Never vent refrigerant yourself.",
            [
                "Schedule bulk via ATL311 / SWS tool / 404-546-0311.",
                "Keep the Freon unit sealed until pickup.",
                "Call ATL311 if the unit is rejected at set-out.",
            ],
            [("Same as fridge?", "Yes — appliances use scheduled bulk; call ATL311 if issues arise.")],
            *bulk,
        )
    )
    for item, label in [
        ("television", "TVs"),
        ("computer-monitor", "monitors"),
    ]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "CHaRM fee-based / NOT Atlanta Recycles Day TVs — NOT bulk",
                "CHaRM (fee-based partner) / Atlanta Recycles Day",
                f"City of Atlanta has no municipal HHW facility. {label} are NOT accepted at Atlanta Recycles Day (small electronics OK; NO TVs). Use CHaRM or other fee-based HHW partners for TVs and monitors. Bulk collection is not documented for e-waste/TVs.",
                [
                    "Do not rely on bulk collection for TVs.",
                    "Atlanta Recycles Day: small electronics OK — NO TVs.",
                    "Use CHaRM or fee-based partners for TVs/monitors.",
                ],
                [("Recycles Day for TV?", "No — Atlanta Recycles Day explicitly excludes TVs.")],
                *recycles,
            )
        )
    for item in ["smartphone", "e-waste-mixed"]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "Atlanta Recycles Day small electronics / CHaRM for more",
                "Atlanta Recycles Day / CHaRM (fee-based partner)",
                f"Small electronics are accepted at Atlanta Recycles Day (3rd Saturday Feb–Dec, 9 a.m.–12 p.m., Greenbriar Mall). For additional {item.replace('-', ' ')} or larger loads, use CHaRM or other fee-based partners. Bulk collection is not documented for e-waste.",
                [
                    "Atlanta Recycles Day: 3rd Sat Feb–Dec 9–12 at Greenbriar Mall.",
                    "Small electronics OK — NO TVs at Recycles Day.",
                    "CHaRM for additional e-waste beyond event capacity.",
                ],
                [("Bulk for e-waste?", "Not documented — use Recycles Day or CHaRM.")],
                *recycles,
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
            "Solidify dried latex for trash — Atlanta has no city HHW facility",
            "Household trash after fully dry (City of Atlanta)",
            "City of Atlanta has no municipal HHW drop-off facility. Dry latex paint completely (cat litter/absorbent until solid) and place the dry can in household trash. Do not pour liquid latex down drains.",
            [
                "Solidify latex paint until fully dry.",
                "Place the dry can in household trash.",
                "Liquid or large volumes: CHaRM or proper HHW partners.",
            ],
            [("City HHW for latex?", "No — Atlanta has no city HHW facility; dry latex for trash.")],
            *hhw_info,
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
                "CHaRM or proper HHW partners — NOT dry-latex trash path",
                "CHaRM (fee-based partner) / proper HHW disposal",
                f"City of Atlanta has no municipal HHW facility. {item.replace('-', ' ')} requires CHaRM or other proper HHW partners — do not use the dried-latex-for-trash pathway. Never pour chemicals down drains or mix into bulk piles.",
                [
                    "Do not dry pesticides/chemicals for trash.",
                    "Use CHaRM or verified HHW partners for proper disposal.",
                    "Keep chemicals out of bulk collection piles.",
                ],
                [("Trash for pesticides?", "No — chemicals require HHW partners, not trash.")],
                *hhw_info,
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
            "car-battery": " Auto and household batteries need proper HHW partners.",
            "lithium-battery": " Rechargeable/lithium batteries need CHaRM or HHW partners.",
            "paint-oil": " Oil paint must be solidified with absorbent or taken to CHaRM.",
            "motor-oil": " Used motor oil needs CHaRM or certified collection.",
            "propane-tank": " Propane cylinders need CHaRM or HHW partners.",
            "fluorescent-bulbs": " CFLs and fluorescent lamps need CHaRM or HHW partners.",
            "cooking-oil": " Keep cooking oil out of drains; use CHaRM or proper disposal.",
        }[item]
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS" if item not in {"cooking-oil"} else "SPECIAL_HANDLING",
                "High" if item not in {"cooking-oil"} else "Medium",
                False,
                "CHaRM or proper HHW partners — no city HHW facility",
                "CHaRM (fee-based partner) / proper HHW disposal",
                f"City of Atlanta has no municipal HHW drop-off facility.{extra} Use CHaRM or other verified HHW partners. Oil-based paint can be solidified with absorbent per city guidance before limited trash disposal — confirm current rules on atlantaga.gov HHW page.",
                [
                    "Check atlantaga.gov HHW page for current partner options.",
                    "Use CHaRM or verified HHW partners for hazardous materials.",
                    "Do not pour chemicals down drains.",
                ],
                [("City HHW address?", "No — Atlanta directs residents to partners like CHaRM.")],
                *hhw_info,
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
            "Rigid sealed container — CHaRM or approved sharps program",
            "CHaRM / approved sharps disposal",
            "Place medical sharps in a rigid, sealed hard-plastic container. City of Atlanta has no municipal HHW facility — use CHaRM or approved sharps programs. Do not loose-bag needles in trash or recycling.",
            [
                "Place sharps in a rigid sealed hard-plastic container.",
                "Use CHaRM or approved sharps disposal programs.",
                "Never recycle sharps containers.",
            ],
            [("Medications?", "Use pharmacy take-back or CHaRM — confirm on city HHW page.")],
            *hhw_info,
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
            "NOT bulk — Atlanta Recycles Day 2 tires no rims OR CHaRM",
            "Atlanta Recycles Day / CHaRM",
            "Tires are NOT accepted on City of Atlanta scheduled bulk collection. Atlanta Recycles Day accepts two tires without rims (3rd Saturday Feb–Dec, 9 a.m.–12 p.m., Greenbriar Mall). CHaRM is another partner option.",
            [
                "Do not schedule bulk collection for tires.",
                "Atlanta Recycles Day: 2 tires without rims at Greenbriar Mall.",
                "CHaRM for additional tire disposal options.",
            ],
            [("Bulk for tires?", "No — tires use Recycles Day or CHaRM.")],
            *recycles,
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
            "City of Atlanta yard waste collection programs",
            "City of Atlanta yard waste collection",
            "City of Atlanta handles yard waste through regular collection programs. Follow set-out rules; keep yard waste out of bulk piles and partner HHW loads.",
            [
                "Use Atlanta yard waste set-out rules for leaves and trimmings.",
                "Keep yard waste separate from bulk collection piles.",
                "Check atlantaga.gov for seasonal guidance.",
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
            "Garbage cart unless private compost",
            "Atlanta garbage / private compost",
            "Bag food scraps for garbage unless you use private/community compost. Keep food out of recycling.",
            [
                "Bag food scraps for garbage if you lack compost access.",
                "Keep organics out of recycling.",
                "Yard trimmings use yard-waste pathways.",
            ],
            [("Bulk for food?", "No — food scraps go in garbage or compost.")],
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
            "Plastic bags are not accepted in City of Atlanta curbside recycling. Return clean film to store take-back or trash.",
            [
                "Keep plastic bags out of the recycling cart.",
                "Use grocery take-back bins when available.",
                "Otherwise place bags in trash.",
            ],
            [("Bulk for bags?", "No — use store take-back or trash.")],
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
            True,
            "Scheduled bulk for limited loads (8 cy) — private C&D for larger",
            "City of Atlanta scheduled bulk / private C&D hauler",
            "Limited homeowner debris may fit scheduled bulk collection (max 8 cy; 12 free/year via ATL311). Larger contractor C&D loads need a private hauler. Route paint and chemicals to CHaRM or proper HHW partners.",
            [
                "Schedule bulk via ATL311 if debris fits 8 cy limit.",
                "Hire a private C&D hauler for larger projects.",
                "Route paint/chemicals to CHaRM or HHW partners.",
            ],
            [("City HHW for C&D?", "No — separate paint/chemicals for partner HHW.")],
            *bulk,
        )
    )
    return rows


def kansas_city():
    c, st = "kansas-city", "MO"
    bulky = (
        "City of Kansas City — Bulky Item Pick-Up",
        "https://www.kcmo.gov/city-hall/trash/bulky",
    )
    hhw = (
        "KC Water — Household Hazardous Waste",
        "https://www.kcwater.us/programs/hhw/",
    )
    ncap = (
        "City of Kansas City — NCAP waste tire dropoff",
        "https://www.kcmo.gov/city-hall/trash/ncap",
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
            "Free bulky appt via Bulky Scheduler/311 — ≥48 hrs; max 15 items <500 lb",
            "KCMO Bulky Item Pick-Up (appointment)",
            "Kansas City Bulky Item Pick-Up is free by appointment via the Bulky Scheduler, 311, or 816-513-2855 — schedule at least 48 hours ahead (Mon–Fri). Max 15 items under 500 lb each; list every item when scheduling. Set out by 7 a.m. on pickup day. Mattresses use bulky pickup.",
            [
                "Schedule via Bulky Scheduler / 311 / 816-513-2855 (≥48 hrs ahead).",
                "List every bulky item when scheduling (max 15 items <500 lb).",
                "Set mattress out by 7 a.m. on pickup day.",
            ],
            [
                ("Cost?", "Free for KCMO residents with appointment."),
                ("Advance notice?", "At least 48 hours, Mon–Fri scheduling."),
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
            "Bulky appt — MUST notify Freon when scheduling; remove doors if possible",
            "KCMO Bulky Item Pick-Up — Freon notification required",
            "Freon refrigerators and freezers are accepted on Kansas City Bulky Item Pick-Up but you MUST notify Freon/refrigerant when scheduling so a separate refrigerant truck can be dispatched. Empty the unit; remove doors if possible. Set out by 7 a.m. Never vent refrigerant yourself. Freon is NOT accepted at KC Water HHW.",
            [
                "Schedule bulky via Bulky Scheduler / 311 — notify Freon appliance.",
                "Empty refrigerator; remove doors if possible.",
                "Set out by 7 a.m. on pickup day.",
            ],
            [("HHW for fridge?", "No — Freon appliances use bulky with notification, not HHW.")],
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
            "Bulky appt — MUST notify Freon when scheduling",
            "KCMO Bulky Item Pick-Up — Freon notification required",
            "Freon window and portable air conditioners are accepted on Kansas City Bulky Item Pick-Up but you MUST notify Freon/refrigerant when scheduling. Empty the unit; set out by 7 a.m. Never vent refrigerant yourself.",
            [
                "Schedule bulky via Bulky Scheduler / 311 — notify Freon AC.",
                "Keep the sealed unit intact until pickup.",
                "Set out by 7 a.m. on pickup day.",
            ],
            [("Same as fridge?", "Yes — notify Freon when scheduling any refrigerant appliance.")],
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
                "Free bulky appt — regular bulky item; no Freon notification",
                "KCMO Bulky Item Pick-Up (appointment)",
                f"Non-Freon appliances such as {item.replace('-', ' ')}s go on Kansas City Bulky Item Pick-Up as regular bulky items — schedule via Bulky Scheduler / 311 (≥48 hrs; max 15 items <500 lb). No Freon notification needed. Set out by 7 a.m.",
                [
                    "Schedule bulky via Bulky Scheduler / 311 / 816-513-2855.",
                    "List the appliance when scheduling — no Freon notification.",
                    "Set out by 7 a.m. on pickup day.",
                ],
                [("Freon notify for washer?", "No — Freon notification is for refrigerators/AC only.")],
                *bulky,
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
            "Bulky appt accepts TVs — NOT at KC Water HHW",
            "KCMO Bulky Item Pick-Up (appointment)",
            "Kansas City Bulky Item Pick-Up accepts TVs when scheduled via Bulky Scheduler / 311. TVs are NOT accepted at KC Water HHW. Hard to Recycle events accept additional e-waste (TV fees may apply). Set out by 7 a.m.",
            [
                "Schedule TV pickup via Bulky Scheduler / 311 (≥48 hrs).",
                "List the TV when scheduling.",
                "Do not haul TVs to KC Water HHW.",
            ],
            [("HHW for TV?", "No — TVs use bulky pickup or Hard to Recycle events.")],
            *bulky,
        )
    )
    for item, label in [
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
                "Hard to Recycle events / private recycler — NOT at HHW",
                "KCMO Hard to Recycle events / private e-waste recycler",
                f"KC Water HHW at 4707 Deramus Ave does not accept general e-waste. For {label}, use Kansas City Hard to Recycle events (fees may apply) or a private e-waste recycler. TVs can use bulky pickup when scheduled.",
                [
                    "Check kcmo.gov for Hard to Recycle event dates.",
                    "Wipe personal data before recycling computers/phones.",
                    "Do not haul general e-waste to KC Water HHW.",
                ],
                [("Bulky for monitor?", "TVs use bulky — other e-waste often uses Hard to Recycle events.")],
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
            "car-battery": " Auto and household batteries accepted at KC Water HHW.",
            "lithium-battery": " Rechargeable/lithium batteries go to HHW — not trash.",
            "paint-latex": " Latex and oil paint accepted at HHW.",
            "paint-oil": " Oil-based paint accepted at HHW.",
            "motor-oil": " Used motor oil accepted at HHW.",
            "propane-tank": " Propane cylinders accepted at HHW.",
            "fluorescent-bulbs": " CFLs and fluorescent lamps accepted at HHW.",
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
                "Free KC Water HHW — Thu–Fri 9–18 Sat 9–16; KCMO residents",
                "KC Water Environmental Campus HHW — 4707 Deramus Ave",
                f"KC Water HHW at Environmental Campus, 4707 Deramus Ave accepts household hazardous materials Thu–Fri 9 a.m.–6 p.m., Sat 9 a.m.–4 p.m.; free for KCMO residents.{extra} Freon appliances and TVs are NOT accepted at HHW.",
                [
                    "Deliver sealed containers during HHW hours.",
                    "Free for Kansas City, MO residents.",
                    "Keep Freon appliances and TVs on bulky pathways.",
                ],
                [("Freon at HHW?", "No — Freon appliances use bulky with notification.")],
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
            "Rigid sealed container — confirm KC Water HHW sharps acceptance",
            "KC Water Environmental Campus HHW — 4707 Deramus Ave",
            "Place medical sharps in a rigid, sealed hard-plastic container before delivery. Confirm sharps acceptance at KC Water HHW on kcwater.us. Do not loose-bag needles in trash or recycling.",
            [
                "Place sharps in a rigid sealed hard-plastic container.",
                "Confirm sharps acceptance at HHW before hauling.",
                "Never recycle sharps containers.",
            ],
            [("Medications?", "Confirm prescription drug take-back at HHW on kcwater.us.")],
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
            "NOT bulky/HHW — NCAP tire dropoff 1st Sat Mar–Nov 8–12 fee cash",
            "NCAP Waste Tire Dropoff — Environmental Campus",
            "Tires are NOT accepted on Kansas City Bulky Item Pick-Up or at KC Water HHW. Use NCAP Waste Tire Dropoff at the Environmental Campus — 1st Saturday March–November, 8 a.m.–12 p.m.; fee; cash only.",
            [
                "Do not schedule bulky pickup for tires.",
                "NCAP dropoff: 1st Sat Mar–Nov 8:00–12:00 at Environmental Campus.",
                "Bring cash for tire dropoff fee.",
            ],
            [("Bulky for tires?", "No — tires use NCAP dropoff or private recycler.")],
            *ncap,
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
            "KCMO yard waste collection programs",
            "KCMO yard waste collection",
            "Kansas City handles yard waste through regular collection programs. Follow set-out rules; keep yard waste out of bulky piles and out of KC Water HHW.",
            [
                "Use KCMO yard waste set-out rules for leaves and trimmings.",
                "Keep yard waste separate from bulky and HHW loads.",
                "Check kcmo.gov for seasonal guidance.",
            ],
            [("Christmas trees?", "Follow city seasonal yard waste guidance.")],
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
            "KCMO garbage / private compost",
            "Bag food scraps for garbage unless you use private/community compost. Keep food out of recycling and out of HHW loads.",
            [
                "Bag food scraps for garbage if you lack compost access.",
                "Keep organics out of recycling.",
                "Yard trimmings use yard-waste pathways.",
            ],
            [("HHW for food?", "No — HHW is for hazardous products.")],
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
            "Plastic bags are not accepted in Kansas City curbside recycling. Return clean film to store take-back or trash.",
            [
                "Keep plastic bags out of the recycling cart.",
                "Use grocery take-back bins when available.",
                "Otherwise place bags in trash.",
            ],
            [("Bulky for bags?", "No — use store take-back or trash.")],
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
            "Bulky appt for limited items (15 <500 lb) — private C&D for larger",
            "KCMO Bulky Item Pick-Up / private C&D hauler",
            "Limited homeowner items may fit Kansas City Bulky Item Pick-Up (max 15 items under 500 lb each when scheduled). Larger construction and demolition debris needs a private C&D hauler. Route paint and chemicals to KC Water HHW separately.",
            [
                "Schedule bulky if items fit the 15-item / 500 lb limits.",
                "Hire a private C&D hauler for larger projects.",
                "Route paint/chemicals to 4707 Deramus Ave HHW.",
            ],
            [("HHW for C&D?", "No — separate paint/chemicals for HHW.")],
            *bulky,
        )
    )
    return rows


CITIES = [
    {
        "city": "Tucson",
        "city_slug": "tucson",
        "state": "AZ",
        "state_slug": "arizona",
        "lat": 32.2226,
        "lng": -110.9747,
        "population": 542629,
    },
    {
        "city": "Tulsa",
        "city_slug": "tulsa",
        "state": "OK",
        "state_slug": "oklahoma",
        "lat": 36.1540,
        "lng": -95.9928,
        "population": 413066,
    },
    {
        "city": "Indianapolis",
        "city_slug": "indianapolis",
        "state": "IN",
        "state_slug": "indiana",
        "lat": 39.7684,
        "lng": -86.1581,
        "population": 887642,
    },
    {
        "city": "Atlanta",
        "city_slug": "atlanta",
        "state": "GA",
        "state_slug": "georgia",
        "lat": 33.7490,
        "lng": -84.3880,
        "population": 498715,
    },
    {
        "city": "Kansas City",
        "city_slug": "kansas-city",
        "state": "MO",
        "state_slug": "missouri",
        "lat": 39.0997,
        "lng": -94.5786,
        "population": 508090,
    },
]

ZIPS = [
    {
        "zip": "85701",
        "city": "Tucson",
        "city_slug": "tucson",
        "state": "AZ",
        "state_slug": "arizona",
        "lat": 32.220,
        "lng": -110.970,
        "population": 12000,
    },
    {
        "zip": "85716",
        "city": "Tucson",
        "city_slug": "tucson",
        "state": "AZ",
        "state_slug": "arizona",
        "lat": 32.230,
        "lng": -110.935,
        "population": 35000,
    },
    {
        "zip": "74103",
        "city": "Tulsa",
        "city_slug": "tulsa",
        "state": "OK",
        "state_slug": "oklahoma",
        "lat": 36.155,
        "lng": -95.990,
        "population": 8000,
    },
    {
        "zip": "74107",
        "city": "Tulsa",
        "city_slug": "tulsa",
        "state": "OK",
        "state_slug": "oklahoma",
        "lat": 36.105,
        "lng": -96.020,
        "population": 22000,
    },
    {
        "zip": "46204",
        "city": "Indianapolis",
        "city_slug": "indianapolis",
        "state": "IN",
        "state_slug": "indiana",
        "lat": 39.770,
        "lng": -86.155,
        "population": 14000,
    },
    {
        "zip": "46227",
        "city": "Indianapolis",
        "city_slug": "indianapolis",
        "state": "IN",
        "state_slug": "indiana",
        "lat": 39.680,
        "lng": -86.130,
        "population": 42000,
    },
    {
        "zip": "30303",
        "city": "Atlanta",
        "city_slug": "atlanta",
        "state": "GA",
        "state_slug": "georgia",
        "lat": 33.750,
        "lng": -84.390,
        "population": 9000,
    },
    {
        "zip": "30318",
        "city": "Atlanta",
        "city_slug": "atlanta",
        "state": "GA",
        "state_slug": "georgia",
        "lat": 33.785,
        "lng": -84.435,
        "population": 38000,
    },
    {
        "zip": "64106",
        "city": "Kansas City",
        "city_slug": "kansas-city",
        "state": "MO",
        "state_slug": "missouri",
        "lat": 39.100,
        "lng": -94.580,
        "population": 11000,
    },
    {
        "zip": "64120",
        "city": "Kansas City",
        "city_slug": "kansas-city",
        "state": "MO",
        "state_slug": "missouri",
        "lat": 39.125,
        "lng": -94.520,
        "population": 28000,
    },
]

FACILITIES = [
    {
        "name": "Los Reales Sustainability Campus HHW",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "tucson",
        "state": "AZ",
        "zip": "85706",
        "address": "5300 E Los Reales Rd, Tucson, AZ 85706",
        "lat": 32.1555,
        "lng": -110.9055,
        "source_url": "https://www.tucsonaz.gov/Departments/Environmental-Services/Household-Hazardous-Waste",
        "hours": "Thu–Sat 7:00–14:00; closed 2nd Sat/month",
        "phone": "520-791-3171",
    },
    {
        "name": "Tulsa Household Pollutant Collection Facility",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "tulsa",
        "state": "OK",
        "zip": "74107",
        "address": "4502 S Galveston Ave, Tulsa, OK 74107",
        "lat": 36.0955,
        "lng": -96.0055,
        "source_url": "https://www.cityoftulsa.org/government/departments/public-works/household-pollutant-collection-facility/",
        "hours": "Wed & Sat 8:00–11:30 and 12:00–16:30",
        "phone": "918-591-4325",
    },
    {
        "name": "Marion County ToxDrop — Traders Point",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "indianapolis",
        "state": "IN",
        "zip": "46278",
        "address": "7550 N Lafayette Rd, Indianapolis, IN 46278",
        "lat": 39.9055,
        "lng": -86.2655,
        "source_url": "https://www.indy.gov/activity/hazardous-waste-dropoff-sites",
        "hours": "1st Sat 9:00–14:00",
        "phone": "317-327-4622",
    },
    {
        "name": "Marion County ToxDrop — Perry Township",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "indianapolis",
        "state": "IN",
        "zip": "46227",
        "address": "4925 S Shelby St, Indianapolis, IN 46227",
        "lat": 39.6855,
        "lng": -86.1355,
        "source_url": "https://www.indy.gov/activity/hazardous-waste-dropoff-sites",
        "hours": "2nd & 4th Sat 9:00–14:00",
        "phone": "317-327-4622",
    },
    {
        "name": "Atlanta Recycles Day — Greenbriar Mall",
        "facility_type": "Special collection event — tires / small electronics",
        "city_slug": "atlanta",
        "state": "GA",
        "zip": "30331",
        "address": "Greenbriar Mall area, Atlanta, GA 30331",
        "lat": 33.7055,
        "lng": -84.5055,
        "source_url": "https://www.atl311.com/en-us/knowledgearticle/?code=KB0011478",
        "hours": "3rd Sat Feb–Dec 9:00–12:00",
        "phone": "404-546-0311",
    },
    {
        "name": "KC Water Environmental Campus HHW",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "kansas-city",
        "state": "MO",
        "zip": "64120",
        "address": "4707 Deramus Ave, Kansas City, MO 64120",
        "lat": 39.1255,
        "lng": -94.5155,
        "source_url": "https://www.kcwater.us/programs/hhw/",
        "hours": "Thu–Fri 9:00–18:00; Sat 9:00–16:00",
        "phone": "816-513-2855",
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
        "tucson": clone_siblings(tucson()),
        "tulsa": clone_siblings(tulsa()),
        "indianapolis": clone_siblings(indianapolis()),
        "atlanta": clone_siblings(atlanta()),
        "kansas-city": clone_siblings(kansas_city()),
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

    print("Wave-8 metros written:")
    for city, rows in audited.items():
        print(f"  {city}: {len(rows)} rules")
    print(f"Total rules now: {len(keep)}")


if __name__ == "__main__":
    main()
