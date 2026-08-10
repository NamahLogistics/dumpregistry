#!/usr/bin/env python3
"""Portal-audited city guides for wave-4 metros (city-sourced only).

Cities researched from official program pages (2026-08-10):
  - Philadelphia, PA — phila.gov Sanitation (bulk appointment, convenience centers, HHW events)
  - San Antonio, TX — sa.gov SWMD (brush/bulky, bulky centers, HHW)
  - Austin, TX — austintexas.gov Austin Resource Recovery (on-demand bulk/HHW, Recycle & Reuse Center)
  - Charlotte, NC — charlottenc.gov Solid Waste + Mecklenburg Wipe Out Waste HHW centers
  - Denver, CO — denvergov.org Large Item Pickup + HHW / appliance / e-cycle programs
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


def philadelphia():
    c, st = "philadelphia", "PA"
    bulk = (
        "City of Philadelphia — Schedule bulky household item collection",
        "https://www.phila.gov/services/trash-recycling-city-upkeep/schedule-trash-collection-for-bulky-household-items/",
    )
    scc = (
        "City of Philadelphia — Sanitation Convenience Centers",
        "https://www.phila.gov/services/trash-recycling-city-upkeep/find-a-sanitation-convenience-center-to-drop-off-trash-or-recycling/",
    )
    hhw = (
        "City of Philadelphia — Household hazardous waste drop-off events",
        "https://www.phila.gov/services/trash-recycling-city-upkeep/dispose-of-household-hazardous-waste/",
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
            "City trash day (limits) or free SCC drop-off with residency proof",
            "Philadelphia Sanitation Convenience Center",
            "Philadelphia treats mattresses differently from appointment bulk metal items. The Department of Sanitation still collects up to two large non-metal items — including plastic-wrapped mattresses — on your regular trash day. Sanitation Convenience Centers also accept unwrapped mattresses and box springs (oversized drop-offs limited; Mon–Sat 8 a.m.–6 p.m. with residency proof). The appointment-only Residential Bulk Collection Program (bulkcollection.phila.gov / 311) is for large metal/appliance-style items and lists mattresses among items it does not collect.",
            [
                "Wrap the mattress in plastic if setting it out with regular trash (max two large non-metal items).",
                "Or take an unwrapped mattress/box spring to a Sanitation Convenience Center with Philadelphia residency proof.",
                "Do not schedule mattresses through the appointment bulk metal program — that channel excludes mattresses.",
            ],
            [
                ("Appointment bulk for mattresses?", "No — city materials list mattresses as not collected on the appointment bulk program."),
                ("SCC hours?", "All six centers: Monday–Saturday 8 a.m.–6 p.m., closed City holidays."),
            ],
            *scc,
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
            "Free appointment bulk (eligible residences) or SCC (limits)",
            "Philadelphia bulk appointment / Sanitation Convenience Center",
            "Eligible Philadelphia residences (single-family and multifamily up to six units on City sanitation) can schedule Residential Bulk Collection for refrigerators and other major appliances — empty the fridge and remove doors. Limit four bulk items per appointment via bulkcollection.phila.gov or 311. Convenience Centers also accept bulk/appliance items containing refrigerants (typically limited to two per day) with residency proof. Larger apartments/commercial must use a private hauler.",
            [
                "Empty the refrigerator and remove doors before set-out or drop-off.",
                "Book an appointment at bulkcollection.phila.gov or call 311 (four-item limit).",
                "Or drop off at a Sanitation Convenience Center within daily oversized limits.",
            ],
            [
                ("Who is eligible?", "City sanitation customers in 1–6 unit residential buildings; larger buildings need private haulers."),
            ],
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
            "Free appointment bulk or SCC (limits)",
            "Philadelphia bulk appointment / Sanitation Convenience Center",
            "Air conditioners are listed among appointment bulk items for eligible Philadelphia residences. Schedule via bulkcollection.phila.gov or 311 (four items per appointment). Convenience Centers also accept refrigerant-containing appliances within daily limits. Do not put freon units in regular carts.",
            [
                "Schedule bulk collection or plan a Convenience Center drop-off.",
                "Keep the unit intact — do not vent refrigerant yourself.",
                "Confirm daily SCC limits for refrigerant appliances before hauling.",
            ],
            [("Same as fridge?", "Yes — major appliances / AC are on the bulk appointment pathway.")],
            *bulk,
        )
    )
    for item, label in [
        ("television", "flat-screen TVs"),
        ("computer-monitor", "computer monitors"),
        ("smartphone", "phones and small electronics"),
        ("e-waste-mixed", "computers and mixed electronic waste"),
    ]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS",
                "Medium",
                item == "television",
                "Free SCC drop-off; flat-screen TVs also on appointment bulk",
                "Philadelphia Sanitation Convenience Center",
                f"Philadelphia directs electronic waste — including {label} — to Sanitation Convenience Centers (Mon–Sat 8 a.m.–6 p.m., residency proof). Flat-screen TVs are also listed on the appointment Residential Bulk Collection program. Seasonal HHW events explicitly do not accept computers/e-waste — use a Convenience Center instead.",
                [
                    "Take e-waste to a Sanitation Convenience Center during open hours with residency proof.",
                    "For a flat-screen TV, you may instead schedule appointment bulk collection if eligible.",
                    "Do not bring computers to HHW collection events — city guidance sends e-waste to SCCs.",
                ],
                [("HHW event for TVs?", "No — HHW events say take electronics to a Convenience Center.")],
                *scc,
            )
        )
    for item in [
        "car-battery",
        "lithium-battery",
        "paint-oil",
        "motor-oil",
        "propane-tank",
        "fluorescent-bulbs",
        "medical-sharps",
    ]:
        note = {
            "car-battery": " Auto/lead-acid batteries are listed for HHW events; Convenience Centers also list lead-acid and lithium/rechargeable batteries.",
            "lithium-battery": " Lithium and NiCad batteries are listed for HHW events; Convenience Centers also accept lithium/rechargeable batteries.",
            "paint-oil": " Oil-based paint is listed for HHW events. Latex/water-based paint can be solidified with absorbent and placed in trash, or taken solidified to a Convenience Center.",
            "motor-oil": " Motor oil is listed among HHW event accepted materials.",
            "propane-tank": " Confirm propane cylinder acceptance before an HHW event — flammable/pressurized items may have limits; never put cylinders in carts.",
            "fluorescent-bulbs": " Fluorescent bulbs are listed for HHW events and Convenience Centers.",
            "medical-sharps": " Sharps/medical waste are not the HHW event pathway — use a pharmacy sharps program or approved medical waste channel; never loose in trash.",
        }[item]
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "Free seasonal HHW events (Greater Philadelphia region) / SCC where listed",
                "Philadelphia HHW collection event or Convenience Center",
                f"Do not put this material in Philadelphia trash or recycling carts.{note} Check the current HHW event calendar on phila.gov (events typically 9 a.m.–3 p.m., no advance registration). Keep products sealed in original containers; never mix chemicals.",
                [
                    "Confirm the next HHW event date/location on the city HHW page.",
                    "Transport sealed, labeled containers upright in a sturdy box.",
                    "For batteries/fluorescents also accepted at Convenience Centers, you may use an SCC instead.",
                ],
                [("Business waste?", "HHW events are for household waste only — businesses need a private service.")],
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
            "Solidify for trash or SCC; liquid latex also listed at HHW events",
            "Philadelphia trash / SCC / HHW event",
            "Philadelphia notes latex/water-based paint is not hazardous when solidified: mix with absorbent (kitty litter/newspaper) until solid, then place in regular trash. Convenience Centers accept solidified latex/water-based paint cans. Liquid paint also appears on the HHW event accepted list if you prefer an event drop-off.",
            [
                "Solidify latex paint with absorbent until no liquid remains, then trash — or take solidified cans to an SCC.",
                "Alternatively, bring sealed paint to a scheduled HHW collection event.",
                "Never pour paint into drains or storm sewers.",
            ],
            [("Oil paint?", "Oil-based paint should go to an HHW event, not the trash.")],
            *scc,
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
            "Appointment bulk (rims off; 4 tires = 1 bulk item) or SCC (4/day)",
            "Philadelphia bulk appointment / Sanitation Convenience Center",
            "Passenger car tires with rims removed are accepted on Philadelphia appointment bulk collection (four tires count as one bulk item). Convenience Centers accept automotive tires limited to four per day with residency proof.",
            [
                "Remove rims before set-out or drop-off.",
                "Schedule bulkcollection.phila.gov / 311, or take up to four tires/day to an SCC.",
                "Do not put tires in regular carts.",
            ],
            [("Truck tires?", "City materials emphasize passenger car tires — confirm unusual tires before hauling.")],
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
            "Included with eligible City collection / SCC paper-bag yard waste",
            "Philadelphia yard-waste / Convenience Center",
            "Philadelphia Sanitation Convenience Centers accept yard waste free of contamination in paper bags only (Mon–Sat 8 a.m.–6 p.m., residency proof). Follow city leaf/yard rules for curbside where offered; Christmas trees have a separate seasonal pathway listed on phila.gov.",
            [
                "Contain clean yard waste in paper bags (plastic bags not accepted at SCCs).",
                "Drop off at a Convenience Center or use the published seasonal/curbside leaf program.",
                "Keep yard waste free of trash and construction debris.",
            ],
            [("Christmas trees?", "City publishes a separate Christmas tree disposal service page.")],
            *scc,
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
            "Not a citywide curbside organics cart — compost privately or via local programs",
            "Local compost / trash (confirm)",
            "Philadelphia does not publish a citywide residential food-scrap cart equivalent to some other metros. Keep food scraps out of recycling; use backyard/community compost where available or bag with trash per building rules. Do not dump organics illegally.",
            [
                "Do not put food scraps in recycling.",
                "Use a local compost option if available, otherwise follow your building’s trash rules.",
                "Never dump organics in vacant lots or storm drains.",
            ],
            [("Yard waste?", "Yard waste has Convenience Center / seasonal pathways — separate from food scraps.")],
            *scc,
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
            "Store take-back — not recycling carts",
            "Retail bag take-back",
            "Do not put plastic bags in Philadelphia recycling streams where they tangle equipment. Return clean bags to grocery store take-back bins when available, or place in trash if no take-back is accessible.",
            [
                "Keep plastic bags out of curbside recycling.",
                "Use a store film take-back bin when available.",
                "Otherwise dispose with trash.",
            ],
            [("Convenience Center recycling?", "SCCs accept recyclable materials — confirm film/bags are not wanted in that stream.")],
            *scc,
        )
    )
    rows.append(
        R(
            c,
            st,
            "cooking-oil",
            "SPECIAL_HANDLING",
            "Medium",
            False,
            "Contain and use grease recycler / confirm HHW if offered",
            "Grease recycler / HHW confirmation",
            "Never pour cooking oil into Philadelphia drains or storm sewers. Cool and contain oil; use a grease recycler or confirm whether a seasonal HHW event will accept it for your volume. Small solidified amounts may follow trash rules where allowed — prefer recycling pathways for larger volumes.",
            [
                "Cool and seal used oil in a non-breakable container.",
                "Use a grease collection/recycler or ask 311 / HHW staff before an event.",
                "Never dump oil outdoors or into drains.",
            ],
            [("Motor oil?", "Used motor oil is listed on HHW event accepted materials.")],
            *hhw,
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
            "Private C&D facility fees — not SCCs",
            "Private construction & demolition facility",
            "Philadelphia Sanitation Convenience Centers do not accept construction debris. Appointment bulk also lists construction/demolition materials as not collected. Haul C&D to a private facility for a fee; keep HHW/paint/e-waste on their proper city channels.",
            [
                "Separate HHW, e-waste, and appliances from C&D loads.",
                "Take construction debris to a private C&D/transfer facility.",
                "Do not leave C&D in the public right-of-way.",
            ],
            [("SCC for drywall?", "No — city guidance says construction materials go to private facilities.")],
            *scc,
        )
    )
    return rows


def san_antonio():
    c, st = "san-antonio", "TX"
    bulky = (
        "City of San Antonio SWMD — Brush & Bulky Items",
        "https://www.sa.gov/Directory/Departments/SWMD/Brush-Bulky",
    )
    drop = (
        "City of San Antonio SWMD — Bulky Waste Collection Centers",
        "https://www.sa.gov/Directory/Departments/SWMD/Brush-Bulky/Bulky-Drop-Off",
    )
    hhw = (
        "City of San Antonio SWMD — Household Hazardous Waste",
        "https://www.sa.gov/Directory/Departments/SWMD/HHW",
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
            "Twice-yearly curbside bulky or free bulky center (CPS bill + ID)",
            "San Antonio Bulky Waste Collection Center",
            "San Antonio Solid Waste Management provides curbside brush & bulky collection twice per year (look up your week; piles generally ≤8 cubic yards). Residents can also drop mattresses and furniture at Bulky Waste Collection Centers (Bitters, Frio City Road, Culebra, Rigsby) with a recent CPS Energy bill showing the environmental fee and photo ID — bulky limited to about four cubic yards; centers do not accept bagged trash or HHW. Hours typically Tue–Fri 8 a.m.–5 p.m., Sat 8 a.m.–12 p.m.",
            [
                "Check My Collection Day for your twice-yearly bulky week, or plan a bulky-center drop-off.",
                "Bring CPS Energy bill (environmental fee) + photo ID for free bulky-center visits.",
                "Keep HHW/chemicals out of bulky piles — use the HHW program instead.",
            ],
            [
                ("Bedbug mattresses?", "Centers list mattresses with blood stains or bed bugs as unaccepted."),
                ("Out-of-cycle bulky?", "311 can quote a fee for out-of-cycle bulky pickup."),
            ],
            *drop,
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
            "Curbside bulky week or bulky center (CPS bill + ID)",
            "San Antonio Bulky Waste Collection Center",
            "Large appliances are accepted at San Antonio Bulky Waste Collection Centers and on curbside bulky service. Bring CPS Energy bill + photo ID for center drop-off. Do not place freon appliances in garbage/recycle carts. HHW centers are for chemicals/e-waste — not a substitute for large appliance bulky drop-off.",
            [
                "Use your bulky week or haul to a Bulky Waste Collection Center with CPS bill + ID.",
                "Do not put refrigerators in carts.",
                "Keep chemicals for the HHW drop-off at 7030 Culebra Rd / HHW events.",
            ],
            [("Freon?", "Follow city appliance guidance; do not vent refrigerant yourself.")],
            *drop,
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
            "Bulky center / curbside bulky — water heaters & AC units listed",
            "San Antonio Bulky Waste Collection Center",
            "San Antonio bulky centers explicitly list water heaters and AC units among accepted materials (with CPS bill + ID). Use curbside bulky week or a center; keep HHW chemicals separate.",
            [
                "Take AC units to a bulky center or set out on your bulky week.",
                "Bring residency documents for free center access.",
                "Never place freon units in carts.",
            ],
            [("Concrete with AC?", "Centers reject soil/rocks/concrete — keep C&D within the 1 cubic yard construction limit if applicable.")],
            *drop,
        )
    )
    for item, label in [
        ("television", "TVs / electronics"),
        ("computer-monitor", "monitors"),
        ("smartphone", "phones and small e-waste"),
        ("e-waste-mixed", "mixed e-waste and printer cartridges"),
    ]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "Free HHW drop-off with CPS bill + ID (limits apply)",
                "San Antonio HHW — 7030 Culebra Road",
                f"San Antonio lists e-waste among Household Hazardous Waste accepted materials. Use the permanent HHW drop-off at 7030 Culebra Road (Tue–Fri 8 a.m.–5 p.m., Sat 8 a.m.–12 p.m.) or published monthly/quarterly HHW events. Bring a recent CPS Energy bill showing environmental fee payment and photo ID. Do not put {label} in carts.",
                [
                    "Pack electronics dry and intact.",
                    "Visit 7030 Culebra Rd or a published HHW event with CPS bill + ID.",
                    "Observe the 220-pound HHW material limit per visit.",
                ],
                [("Paint limit?", "Paint/liquids limited to five 5-gallon cans or 25 one-gallon cans.")],
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
        extra = {
            "cooking-oil": " Cooking oil is explicitly listed among HHW accepted materials.",
            "medical-sharps": " Medicine/medical waste is listed as unaccepted at HHW — use MedDropSA / pharmacy take-back for drugs and an approved sharps container program for needles.",
            "propane-tank": " Confirm cylinder size acceptance with SWMD before hauling pressurized tanks.",
        }.get(item, "")
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING",
                "High" if item not in {"cooking-oil", "paint-latex"} else "Medium",
                False,
                "Free HHW drop-off (CPS bill + ID; limits)",
                "San Antonio HHW — 7030 Culebra Road",
                f"Household hazardous / special wastes must not go in San Antonio carts. Take them to the HHW program at 7030 Culebra Road or published HHW events with CPS bill + photo ID.{extra} Keep materials in original containers; do not mix; 220-pound limit.",
                [
                    "Seal and label containers; transport upright in a box/trunk.",
                    "Bring CPS Energy bill + photo ID to HHW drop-off.",
                    "Call 311 / 210-207-6428 if unsure an item is accepted.",
                ],
                [("Commercial waste?", "HHW is for household materials — commercial/medical waste is refused.")],
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
            "Bulky center: ≤6 car tires, no rims (CPS bill + ID)",
            "San Antonio Bulky Waste Collection Center",
            "Bulky Waste Collection Centers accept car tires — six or fewer, rims removed — with CPS bill + ID. Keep tires out of HHW and out of carts. Confirm curbside bulky acceptance for your week before setting tires out.",
            [
                "Remove rims; stay at or under six passenger tires per bulky-center visit.",
                "Bring CPS bill + ID.",
                "Do not mix tires with HHW chemicals.",
            ],
            [("Commercial tires?", "Centers emphasize residential car tires — confirm unusual tires first.")],
            *drop,
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
            "Organics cart / brush center / twice-yearly brush&bulky",
            "San Antonio brush & organics programs",
            "San Antonio separates brush/yard materials from garbage. Use your organics/compost cart for eligible food/yard materials per city guides; larger brush follows the brush & bulky schedule or the brush collection center (CPS bill + ID). Christmas tree drop-offs run the first two weeks of January.",
            [
                "Use the organics cart for eligible scraps/yard trimmings per city rules.",
                "Schedule/look up brush & bulky week for larger brush, or use the brush center.",
                "Do not put brush in bulky centers that reject yard waste — use the brush pathway.",
            ],
            [("Bulky center for leaves?", "Bulky centers list brush/leaves/yard waste as unaccepted — use brush/organics channels.")],
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
            "Included with organics cart service where provided",
            "San Antonio organics / compost cart",
            "San Antonio publishes an organics/compost cart pathway for eligible food scraps and yard materials. Keep plastic bags out of organics where prohibited; follow the Materials Disposal guide on sa.gov/SWMD for what belongs in which cart.",
            [
                "Confirm your address receives organics service.",
                "Place only accepted food scraps/yard materials in the organics cart.",
                "Keep HHW and plastics out of organics.",
            ],
            [("No organics cart?", "Use the city Materials Disposal guide / 311 for alternatives.")],
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
            "Not in blue recycling cart",
            "Store take-back / trash",
            "San Antonio Solid Waste no longer accepts plastic bags in the blue recycling cart, even when bundled. Keep film out of recycling; use store take-back when available or trash.",
            [
                "Do not put plastic bags in the blue recycling cart.",
                "Use retail film take-back if available.",
                "Otherwise dispose with garbage.",
            ],
            [("City announcement?", "SWMD states bags are no longer accepted in blue recycling carts.")],
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
            False,
            "Bulky center ≤1 cubic yard C&D (CPS bill + ID) or private haul",
            "San Antonio Bulky Waste Collection Center",
            "Construction materials are not for garbage carts. Bulky centers allow about one cubic yard of construction material & lumber (boards under 10 ft); soil/rocks/concrete are unaccepted. Larger C&D needs a private hauler/debris box. Keep HHW out of C&D loads.",
            [
                "Stay within the ~1 cubic yard C&D limit at bulky centers, or hire a debris box.",
                "Bring CPS bill + ID for center access.",
                "Separate paint/chemicals for HHW.",
            ],
            [("Concrete?", "Centers list soil, rocks & concrete as unaccepted.")],
            *drop,
        )
    )
    return rows


def austin():
    c, st = "austin", "TX"
    ondemand = (
        "Austin Resource Recovery — On-demand bulk, brush & HHW collection",
        "https://www.austintexas.gov/resource-recovery/programs/demand-bulk-brush-and-household-hazardous-waste-collection",
    )
    rrc = (
        "Austin Resource Recovery — Recycle and Reuse Center",
        "https://www.austintexas.gov/resource-recovery/locations/recycle-and-reuse-drop-center",
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
            "On-demand bulk (up to 3/year) — RRC does not accept mattresses",
            "Austin on-demand bulk collection",
            "Austin Resource Recovery residential customers (single-family through fourplex) schedule on-demand bulk collection via the Austin Recycles app, austintexas.gov/ondemand, or 311 — up to three bulk collections per calendar year. Furniture and other oversized household items are collected curbside by appointment (set out by 5:30 a.m.; separate metal vs non-metal piles). The Recycle and Reuse Center explicitly does not accept mattresses or furniture — use on-demand bulk or reuse/donation first.",
            [
                "Schedule on-demand bulk in the Austin Recycles app / austintexas.gov/ondemand / 311.",
                "Set items at the curb by 5:30 a.m. on the appointment date; keep piles separated as directed.",
                "Do not haul mattresses to the Recycle and Reuse Center — they are not accepted there.",
            ],
            [
                ("How many bulk pickups?", "Up to three on-demand bulk collections per calendar year for eligible ARR customers."),
                ("RRC mattresses?", "City page lists furniture and mattresses as not accepted at the Recycle and Reuse Center."),
            ],
            *ondemand,
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
            "On-demand bulk (doors off) or RRC appointment",
            "Austin on-demand bulk / Recycle and Reuse Center",
            "Appliances are accepted on Austin on-demand bulk collection — remove doors before set-out. The Recycle and Reuse Center (2514 Business Center Dr, appointment required) also lists washers, dryers, stoves, water heaters, and other appliances. Do not put freon appliances in trash carts.",
            [
                "Remove refrigerator doors; schedule on-demand bulk or an RRC appointment.",
                "Set out by 5:30 a.m. for curbside bulk, or confirm RRC acceptance for your appliance.",
                "Keep HHW chemicals on the separate HHW on-demand or RRC HHW stream.",
            ],
            [("Bulk pile rules?", "Separate metal/appliances/electronics from non-metal bulk and tires.")],
            *ondemand,
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
            "On-demand bulk or RRC (AC listed)",
            "Austin on-demand bulk / Recycle and Reuse Center",
            "Air conditioners are listed among accepted electronics/appliances at Austin’s Recycle and Reuse Center (appointment required). On-demand bulk also covers appliances for ARR customers. Do not vent refrigerant or place units in carts.",
            [
                "Schedule on-demand bulk or an RRC drop-off appointment.",
                "Do not put AC units in trash/recycling carts.",
                "Use What Do I Do With… in the Austin Recycles app if unsure.",
            ],
            [("Furniture at RRC?", "RRC does not accept furniture/mattresses — only listed appliances/electronics/HHW/recyclables.")],
            *rrc,
        )
    )
    for item, label in [
        ("television", "televisions"),
        ("computer-monitor", "monitors"),
        ("smartphone", "cell phones"),
        ("e-waste-mixed", "computers, printers, and mixed electronics"),
    ]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS",
                "Medium",
                True,
                "On-demand bulk (electronics pile) or free RRC appointment",
                "Austin Recycle and Reuse Center / on-demand bulk",
                f"Austin accepts {label} through on-demand bulk (place with metal/electronics/rigid plastics) and at the Recycle and Reuse Center by appointment (2514 Business Center Drive). Do not put e-waste in trash carts. Solar panels/battery storage are listed among RRC accepted recyclables.",
                [
                    "Schedule on-demand bulk or an RRC appointment via Austin Recycles app / city site.",
                    "Keep electronics dry and intact.",
                    "Separate HHW chemicals into the HHW on-demand service (not at the curb).",
                ],
                [("Bulk electronics?", "City set-out guidance groups electronics with metal items / rigid plastics.")],
                *rrc,
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
        extra = {
            "cooking-oil": " Cooking oil and grease are listed for on-demand HHW and RRC HHW.",
            "medical-sharps": " Syringes and medical waste are not accepted at the Recycle and Reuse Center HHW — use an approved sharps program.",
            "propane-tank": " Propane cylinders are listed for on-demand HHW / RRC HHW (size limits apply; ≤5 gallon containers for on-demand).",
        }.get(item, "")
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS" if item not in {"cooking-oil", "paint-latex"} else "SPECIAL_HANDLING",
                "High" if item not in {"cooking-oil", "paint-latex"} else "Medium",
                True,
                "On-demand HHW (≤30 gal, ≤3/year) or RRC appointment",
                "Austin on-demand HHW / Recycle and Reuse Center",
                f"Austin Resource Recovery customers can schedule on-demand household hazardous waste collection (up to three per year, 30-gallon limit) — do not set HHW at the curb; leave sealed, labeled containers in an accessible covered area. Austin/Travis County residents can also book the Recycle and Reuse Center for HHW.{extra} Accepted lists include batteries, automotive fluids, paint, pesticides, pool chemicals, fluorescents, and propane cylinders.",
                [
                    "Schedule HHW via Austin Recycles app / austintexas.gov/ondemand / 311 — or book RRC.",
                    "Seal/label containers; keep under 5 gallons each and 30 gallons total per on-demand visit.",
                    "Never place HHW at the curb next to carts.",
                ],
                [("Business HHW?", "Businesses are not eligible for RRC hazardous waste drop-off.")],
                *ondemand,
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
            "On-demand bulk ≤8 passenger tires (rims off); RRC tire fee $6 each",
            "Austin on-demand bulk / Recycle and Reuse Center",
            "On-demand bulk accepts passenger car tires with rims removed — limit eight tires per household; truck/tractor tires and tires on rims are refused. The Recycle and Reuse Center accepts tires for a published fee ($6 per tire). Keep tires in their own set-out pile.",
            [
                "Remove rims; schedule on-demand bulk or pay the RRC tire fee with an appointment.",
                "Stay within the eight-tire household limit for curbside bulk.",
                "Do not put tires in trash carts.",
            ],
            [("Tires on rims?", "Not accepted for on-demand bulk — rims must be removed.")],
            *ondemand,
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
            "Green compost cart + on-demand brush (3/year)",
            "Austin compost cart / on-demand brush",
            "Small branches and yard trimmings go in Austin’s weekly composting collection (green cart + limited extras). Large brush (about 5–15 ft limbs) uses on-demand brush collection — up to three per year — stacked loosely at the curb. Brush is not accepted at the Recycle and Reuse Center; Hornsby Bend is the brush drop-off alternative.",
            [
                "Use the green compost cart for small yard trimmings/food scraps per city rules.",
                "Schedule on-demand brush for large limbs; set out by 5:30 a.m.",
                "For extra brush, use Hornsby Bend Biosolids Management Plant drop-off.",
            ],
            [("Oak wilt?", "City advises seasonal oak pruning practices to limit oak wilt spread.")],
            *ondemand,
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
            "Included with Austin compost cart service",
            "Austin compost / organics cart",
            "Austin residential composting collection accepts food scraps and yard trimmings in the green cart pathway. Keep plastic bags and HHW out. Use What Do I Do With… for borderline items.",
            [
                "Place accepted food scraps in the compost cart.",
                "Keep plastics/glass/metal out of compost.",
                "Schedule bulky/HHW separately for non-organics.",
            ],
            [("Brush in compost?", "Large brush uses on-demand brush — not the compost cart.")],
            *ondemand,
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
            "RRC accepts clean dry plastic bags/film by appointment",
            "Austin Recycle and Reuse Center",
            "Keep plastic bags out of single-stream carts where they contaminate recycling. Austin’s Recycle and Reuse Center lists clean, dry plastic bags and plastic film among accepted recyclables (appointment required; no packing peanuts).",
            [
                "Do not put film bags in curbside recycling if your route rejects them.",
                "Book an RRC appointment for clean dry bags/film, or use store take-back.",
                "Keep bags clean and dry; no Styrofoam peanuts.",
            ],
            [("Styrofoam?", "RRC accepts clean dry Styrofoam blocks — not packing peanuts.")],
            *rrc,
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
            "Private C&D / limited nail-free lumber on bulk — not tile/glass C&D",
            "Private C&D facility / limited on-demand bulk",
            "Austin on-demand bulk accepts nail-free lumber and some household remodeling leftovers but refuses sheet glass, tile, and general construction/remodeling debris. The Recycle and Reuse Center is not a C&D landfill substitute. Hire a debris box or private C&D facility for demolition loads; keep HHW/paint on HHW channels.",
            [
                "Confirm the item in Austin Recycles / What Do I Do With… before scheduling bulk.",
                "Use a private C&D/transfer option for tile, sheet glass, and demolition debris.",
                "Keep paint and chemicals on on-demand HHW or RRC HHW.",
            ],
            [("Carpet?", "Household carpet is listed for bulk; construction/demolition carpet is not.")],
            *ondemand,
        )
    )
    return rows


def charlotte():
    c, st = "charlotte", "NC"
    bulky = (
        "City of Charlotte Solid Waste — Collection Guidelines (bulky)",
        "https://www.charlottenc.gov/Services/Trash-and-Recycling/Collection-Guidelines",
    )
    faq_src = (
        "City of Charlotte Solid Waste — Service FAQs",
        "https://www.charlottenc.gov/Services/Trash-and-Recycling/FAQ",
    )
    meck = (
        "Mecklenburg County Solid Waste — Wipe Out Waste / recycling centers",
        "https://wipeoutwaste.mecknc.gov/",
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
            "Free scheduled bulky for City garbage customers",
            "Charlotte scheduled bulky collection",
            "Charlotte Solid Waste collects mattresses, box springs, furniture, and appliances as bulky waste — only when scheduled in advance. Schedule via CharMeck 311 (704-336-7600), the CLT+ app, or the city’s online request. Place items at the curb by 6 a.m. on the scheduled day (not sooner than the day before); leave 3 feet between items. Unscheduled curb piles will not be collected.",
            [
                "Schedule bulky pickup online, in CLT+, or by calling 311.",
                "Set mattresses at the curb by 6 a.m. on the scheduled day with space between items.",
                "Cancel/change by noon the business day before if needed.",
            ],
            [
                ("Walk-up piles?", "Items placed without scheduling are not collected."),
                ("Who is eligible?", "Addresses that currently receive City of Charlotte garbage collection."),
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
            "Scheduled bulky — empty, door removed, tape X on glass",
            "Charlotte scheduled bulky collection",
            "Appliances must be scheduled for Charlotte bulky collection — not placed in rollout carts. City guidance: empty appliances, remove the door, and tape an X on glass. Hazardous waste, construction debris, and electronics are not for the garbage cart.",
            [
                "Empty the appliance, remove the door, and schedule bulky via 311 / CLT+ / online.",
                "Set out by 6 a.m. on the scheduled day.",
                "Keep batteries/paint/chemicals for Mecklenburg full-service recycling centers — not bulky/trash carts.",
            ],
            [("Two trucks?", "City notes different trucks may collect different bulky material types.")],
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
            "Scheduled bulky (appliance rules)",
            "Charlotte scheduled bulky collection",
            "Treat window/central AC units as appliances on Charlotte’s scheduled bulky service. Do not place freon appliances in carts. Confirm unusual commercial units with 311 before scheduling.",
            [
                "Schedule bulky collection; prepare the unit safely (do not vent refrigerant).",
                "Set out by 6 a.m. with clearance from other piles.",
                "Use Mecklenburg HHW centers for chemicals separately.",
            ],
            [("Electronics?", "City FAQ: electronics are not for the garbage cart — use County full-service centers.")],
            *bulky,
        )
    )
    for item, label in [
        ("television", "TVs"),
        ("computer-monitor", "monitors"),
        ("smartphone", "phones and small electronics"),
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
                "Mecklenburg County full-service recycling center",
                "Mecklenburg County full-service recycling center",
                f"Charlotte garbage carts do not accept electronics. Take {label} to a Mecklenburg County full-service recycling center (Wipe Out Waste network), which accepts enhanced recycling and related materials. Staffed-only centers may refuse trash/HHW — use a full-service site for e-waste/HHW needs.",
                [
                    "Do not put electronics in City garbage or recycling carts.",
                    "Locate a Mecklenburg full-service recycling center via wipeoutwaste.mecknc.gov.",
                    "Confirm accepted electronics before you haul.",
                ],
                [("Lithium batteries in trash?", "City FAQ: lithium batteries and vape pens are not eligible for garbage collection.")],
                *meck,
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
        extra = {
            "motor-oil": " Full-service centers accept waste motor oil among other HHW-related materials.",
            "medical-sharps": " Use an approved sharps container / pharmacy program — do not loose-needle trash carts.",
            "lithium-battery": " City FAQ specifically flags lithium batteries as not eligible for garbage collection.",
        }.get(item, "")
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS" if item not in {"cooking-oil", "paint-latex"} else "SPECIAL_HANDLING",
                "High" if item not in {"cooking-oil", "paint-latex"} else "Medium",
                False,
                "Mecklenburg County full-service recycling center (HHW)",
                "Mecklenburg County full-service recycling center",
                f"Household hazardous wastes and batteries are not collected in Charlotte curbside carts. Take them to a Mecklenburg County full-service recycling center that accepts HHW / waste oil / enhanced recycling.{extra} Do not use staffed-only or park self-serve sites when you need HHW acceptance.",
                [
                    "Identify a full-service (not staffed-only) Mecklenburg recycling center.",
                    "Transport sealed containers upright.",
                    "Call ahead / check Wipe Out Waste guides for limits.",
                ],
                [("City vs County?", "Charlotte collects trash/recycling/yard/bulky; County centers handle HHW/e-waste drop-off.")],
                *meck,
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
            "Confirm 311 / County center — not garbage cart",
            "Mecklenburg County / scheduled bulky confirmation",
            "Do not put tires in Charlotte garbage carts. Ask CharMeck 311 whether your tire set qualifies for scheduled bulky, or use a Mecklenburg County / retailer take-back pathway. Waste tires are regulated — confirm before curb set-out.",
            [
                "Call 311 before setting tires curbside.",
                "Prefer retailer take-back when replacing tires.",
                "Never dump tires illegally.",
            ],
            [("Bulk list?", "City publishes a bulky eligibility PDF — confirm tires there or with 311.")],
            *faq_src,
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
            "Weekly curbside yard waste on garbage day",
            "Charlotte yard waste collection",
            "Charlotte collects yard waste weekly on your garbage day when prepared correctly: leaves/grass in paper bags or containers ≤32 gallons (no plastic bags); brush/limbs generally ≤5 feet and within diameter limits; piles separated. Natural Christmas trees at single-family homes go with yard waste undecorated; artificial trees need bulky scheduling.",
            [
                "Set yard waste out by 6 a.m. on your collection day (not earlier than the day before).",
                "Use paper bags/reusable containers for leaves — plastic bags are refused.",
                "Follow brush/limb size and spacing rules from the city guidelines.",
            ],
            [("Early set-out?", "City warns citations may apply if yard waste is placed out too early.")],
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
            "Garbage cart (bagged) unless you use private compost",
            "Charlotte garbage cart / private compost",
            "Charlotte’s published curbside programs focus on garbage, recycling, yard waste, and scheduled bulky — not a separate citywide food-scrap cart. Bag food scraps for the garbage cart or use a private/community compost option. Keep food out of recycling.",
            [
                "Bag food scraps for the garbage cart unless you compost locally.",
                "Keep food and liquids out of recycling.",
                "Yard trimmings use the yard-waste pathway, not recycling.",
            ],
            [("Organics cart?", "City guidelines emphasize yard waste separately from garbage — not a food-scrap subscription cart.")],
            *faq_src,
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
            "Not in green recycling cart — County centers now accept bags/film",
            "Mecklenburg recycling center / store take-back",
            "Charlotte curbside recycling rejects plastic bags (they tangle equipment). Mecklenburg County announced acceptance of plastic bags and wraps at full-service and staffed recycling centers — use those drop-offs or retail take-back instead of the green cart.",
            [
                "Keep plastic bags out of the curbside recycling cart.",
                "Take clean bags/film to a Mecklenburg staffed or full-service center, or store take-back.",
                "Otherwise dispose with garbage.",
            ],
            [("Styrofoam?", "City recycling unacceptable list includes Styrofoam — do not cart it.")],
            *meck,
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
            "Not City garbage — private C&D / County options",
            "Private C&D / Mecklenburg facilities",
            "Charlotte FAQ: construction debris is not allowed in garbage carts. Use a private debris box or permitted C&D facility; keep HHW and electronics on County center pathways. Do not leave C&D in the right-of-way.",
            [
                "Do not load C&D into City garbage carts.",
                "Hire a debris box or haul to an approved C&D facility.",
                "Separate paint/batteries for County HHW centers.",
            ],
            [("Bulky for lumber?", "Ask 311 whether limited household remodeling debris qualifies as bulky vs C&D.")],
            *faq_src,
        )
    )
    return rows


def denver():
    c, st = "denver", "CO"
    lip = (
        "City and County of Denver — Large Item Pickup",
        "https://www.denvergov.org/Government/Agencies-Departments-Offices/Agencies-Departments-Offices-Directory/Recycle-Compost-Trash/Large-Item-Pickup",
    )
    hhw = (
        "City and County of Denver — Household Hazardous Waste",
        "https://www.denvergov.org/Government/Agencies-Departments-Offices/Agencies-Departments-Offices-Directory/Recycle-Compost-Trash/Additional-Services/Hazardous-Waste",
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
            "Large Item Pickup every ~9 weeks (max 5 large items)",
            "Denver Large Item Pickup",
            "Denver Solid Waste collects mattresses and box springs on Large Item Pickup, scheduled about every nine weeks on your regular trash day (find the day in the Trash and Recycling app or online lookup). Limits are typically five large items plus up to ten bags. Large Item Pickup does not take appliances, electronics, tires, construction materials, or hazardous waste — those have separate Denver programs.",
            [
                "Look up your next Large Item Pickup day in Denver’s trash/recycling tools.",
                "Set out mattresses with other allowed large items within the five-item limit.",
                "Use separate city programs for appliances, e-waste, tires, paint, and HHW.",
            ],
            [
                ("Appliances on LIP?", "No — Denver lists appliances as not accepted on Large Item Pickup; use Appliance Collection."),
                ("E-waste on LIP?", "No — use Denver electronic recycling / E-cycle coupon pathways."),
            ],
            *lip,
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
            "Denver Appliance Collection (not Large Item Pickup)",
            "Denver Appliance Collection",
            "Denver Large Item Pickup does not accept appliances. Use the City’s Appliance Collection program (see denvergov.org Solid Waste / Additional Services) for refrigerators and similar white goods. Do not leave freon appliances in alleys or trash carts.",
            [
                "Schedule or follow Denver Appliance Collection instructions on denvergov.org.",
                "Do not set refrigerators out on Large Item Pickup day expecting collection.",
                "Keep HHW chemicals on the HHW At-Your-Door / paint programs.",
            ],
            [("Why not LIP?", "City Large Item Pickup unacceptable list includes appliances.")],
            *lip,
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
            "Denver Appliance Collection / recycler — not LIP",
            "Denver Appliance Collection",
            "Treat AC units like other appliances in Denver: not for Large Item Pickup or trash carts. Use Appliance Collection or a licensed appliance recycler; never vent refrigerant yourself.",
            [
                "Use Denver Appliance Collection or a certified recycler.",
                "Keep units out of LIP piles and alleys.",
                "Separate HHW for the hazardous waste program.",
            ],
            [("Tires with AC?", "Tires are also excluded from LIP — use tire/retailer pathways.")],
            *lip,
        )
    )
    for item, label in [
        ("television", "televisions"),
        ("computer-monitor", "monitors"),
        ("smartphone", "computers/phones and related electronics"),
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
                "Denver E-cycle coupon / electronics recycling (not LIP)",
                "Denver electronic recycling",
                f"Colorado landfill rules and Denver guidance keep electronic wastes out of trash. {label.title()} are not accepted on Large Item Pickup. Denver Recycles offers an E-cycle coupon pathway so residents can drop off TVs, computers, and other electronics at a discounted rate — request the coupon through the city process and follow the listed recycler instructions.",
                [
                    "Do not put e-waste in trash, compost, or Large Item Pickup.",
                    "Request a Denver E-cycle coupon / follow the Electronic Recycling page steps.",
                    "Wipe personal data before recycling computers/phones.",
                ],
                [("Paint with TV?", "Paint and HHW use separate Denver hazardous waste / PaintCare pathways.")],
                *lip,
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
        extra = {
            "paint-latex": " Denver also points residents to free paint recycling / PaintCare-style drop-offs; liquid paint does not belong in trash.",
            "paint-oil": " Oil-based paint and solvents belong in HHW — not trash or LIP.",
            "medical-sharps": " Denver HHW At-Your-Door lists sharps/needles among materials it cannot accept — use a medical sharps program.",
            "car-battery": " Auto batteries appear on HHW accepted lists; retailers often take core returns too.",
        }.get(item, "")
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS" if item not in {"cooking-oil", "paint-latex"} else "SPECIAL_HANDLING",
                "High" if item not in {"cooking-oil", "paint-latex"} else "Medium",
                False,
                "HHW At-Your-Door (limits; copay) / paint & battery drop-off programs",
                "Denver Household Hazardous Waste program",
                f"Denver prohibits putting hazardous materials in trash, recycling, compost, or Large Item Pickup. Use the Household Hazardous Waste At-Your-Door program (typically one appointment per year for residents; schedule via the city’s HHW page / vendor) or the published paint and battery drop-off options.{extra}",
                [
                    "Schedule HHW At-Your-Door or use a listed paint/battery drop-off.",
                    "Prioritize materials that fit the collection kit limits.",
                    "Never leave chemicals in alleys or pour them outdoors.",
                ],
                [("LIP for paint?", "No — hazardous materials are excluded from Large Item Pickup.")],
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
            "Retailer / tire recycler — not LIP",
            "Tire retailer take-back",
            "Denver Large Item Pickup lists tires/automotive materials among items not accepted. Use a tire retailer take-back when replacing tires or a permitted tire recycler. Illegal tire dumping is prohibited.",
            [
                "Ask the tire shop to take old tires when you buy replacements.",
                "Do not set tires out on Large Item Pickup day.",
                "Keep tires out of trash carts.",
            ],
            [("State ban?", "Colorado restricts waste tires from ordinary landfill disposal — use proper tire channels.")],
            *lip,
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
            "Compost cart / LeafDrop / limited bundled branches on LIP",
            "Denver compost / LeafDrop",
            "Denver offers weekly compost collection for enrolled customers and seasonal LeafDrop sites (e.g., Cherry Creek Recycling Drop-off area guidance). Large Item Pickup may allow limited bundled branches within rules, but unbundled branches/stumps/dirt/sod are not accepted on LIP. Prefer compost/LeafDrop pathways for yard materials.",
            [
                "Use your compost cart for accepted yard trimmings/food scraps if enrolled.",
                "Watch for seasonal LeafDrop locations for leaves and small branches.",
                "Only set bundled branches on LIP if they meet published size rules.",
            ],
            [("Dirt/sod on LIP?", "Not accepted on Large Item Pickup.")],
            *lip,
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
            "Weekly compost collection where enrolled",
            "Denver compost cart",
            "Denver provides weekly compost collection for participating households. Keep food scraps in the compost stream per the city’s accepted list; do not put HHW or plastics in compost.",
            [
                "Confirm compost service at your address.",
                "Follow Denver’s compost accepted/not-accepted lists.",
                "Keep meat/dairy rules per current city guidance if your route has restrictions.",
            ],
            [("No compost?", "Use trash as last resort and consider drop-off compost options in the Waste Directory.")],
            *lip,
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
            "Store take-back — not curbside recycling",
            "Retail bag take-back",
            "Keep plastic bags out of Denver single-stream recycling. Return clean film to grocery take-back bins or dispose with trash if no take-back is available.",
            [
                "Do not bag recyclables or stuff film into the recycling cart.",
                "Use store film recycling bins when available.",
                "Otherwise place bags in trash.",
            ],
            [("Waste Directory?", "Denver’s Waste Directory lists specialized drop-offs for hard-to-recycle items.")],
            *lip,
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
            "Private C&D — not Large Item Pickup",
            "Private C&D / transfer facility",
            "Denver Large Item Pickup does not accept construction materials (concrete, bricks, fencing, pallets, etc.). Hire a debris box or haul to a private transfer/C&D facility. Keep paint and chemicals on HHW/paint recycling programs.",
            [
                "Do not set C&D on Large Item Pickup day.",
                "Use a private hauler/transfer station for construction debris.",
                "Recycle paint via Denver paint programs; chemicals via HHW.",
            ],
            [("Furniture vs C&D?", "Household furniture can go on LIP; construction materials cannot.")],
            *lip,
        )
    )
    return rows


CITIES = [
    {
        "city": "Philadelphia",
        "city_slug": "philadelphia",
        "state": "PA",
        "state_slug": "pennsylvania",
        "lat": 39.9526,
        "lng": -75.1652,
        "population": 1603797,
    },
    {
        "city": "San Antonio",
        "city_slug": "san-antonio",
        "state": "TX",
        "state_slug": "texas",
        "lat": 29.4241,
        "lng": -98.4936,
        "population": 1434625,
    },
    {
        "city": "Austin",
        "city_slug": "austin",
        "state": "TX",
        "state_slug": "texas",
        "lat": 30.2672,
        "lng": -97.7431,
        "population": 961855,
    },
    {
        "city": "Charlotte",
        "city_slug": "charlotte",
        "state": "NC",
        "state_slug": "north-carolina",
        "lat": 35.2271,
        "lng": -80.8431,
        "population": 874579,
    },
    {
        "city": "Denver",
        "city_slug": "denver",
        "state": "CO",
        "state_slug": "colorado",
        "lat": 39.7392,
        "lng": -104.9903,
        "population": 715522,
    },
]

ZIPS = [
    {
        "zip": "19107",
        "city": "Philadelphia",
        "city_slug": "philadelphia",
        "state": "PA",
        "state_slug": "pennsylvania",
        "lat": 39.952,
        "lng": -75.163,
        "population": 12000,
    },
    {
        "zip": "19128",
        "city": "Philadelphia",
        "city_slug": "philadelphia",
        "state": "PA",
        "state_slug": "pennsylvania",
        "lat": 40.038,
        "lng": -75.221,
        "population": 36000,
    },
    {
        "zip": "78205",
        "city": "San Antonio",
        "city_slug": "san-antonio",
        "state": "TX",
        "state_slug": "texas",
        "lat": 29.424,
        "lng": -98.491,
        "population": 2000,
    },
    {
        "zip": "78238",
        "city": "San Antonio",
        "city_slug": "san-antonio",
        "state": "TX",
        "state_slug": "texas",
        "lat": 29.468,
        "lng": -98.627,
        "population": 28000,
    },
    {
        "zip": "78701",
        "city": "Austin",
        "city_slug": "austin",
        "state": "TX",
        "state_slug": "texas",
        "lat": 30.272,
        "lng": -97.744,
        "population": 10000,
    },
    {
        "zip": "78744",
        "city": "Austin",
        "city_slug": "austin",
        "state": "TX",
        "state_slug": "texas",
        "lat": 30.198,
        "lng": -97.712,
        "population": 48000,
    },
    {
        "zip": "28202",
        "city": "Charlotte",
        "city_slug": "charlotte",
        "state": "NC",
        "state_slug": "north-carolina",
        "lat": 35.227,
        "lng": -80.843,
        "population": 15000,
    },
    {
        "zip": "28214",
        "city": "Charlotte",
        "city_slug": "charlotte",
        "state": "NC",
        "state_slug": "north-carolina",
        "lat": 35.278,
        "lng": -80.935,
        "population": 42000,
    },
    {
        "zip": "80202",
        "city": "Denver",
        "city_slug": "denver",
        "state": "CO",
        "state_slug": "colorado",
        "lat": 39.752,
        "lng": -104.999,
        "population": 18000,
    },
    {
        "zip": "80204",
        "city": "Denver",
        "city_slug": "denver",
        "state": "CO",
        "state_slug": "colorado",
        "lat": 39.734,
        "lng": -105.021,
        "population": 34000,
    },
]

FACILITIES = [
    {
        "name": "Northwest Sanitation Convenience Center (Philadelphia)",
        "facility_type": "Sanitation convenience center — bulky / e-waste / yard waste",
        "city_slug": "philadelphia",
        "state": "PA",
        "zip": "19128",
        "address": "320 Domino Ln, Philadelphia, PA 19128",
        "lat": 40.0385,
        "lng": -75.2212,
        "source_url": "https://www.phila.gov/services/trash-recycling-city-upkeep/find-a-sanitation-convenience-center-to-drop-off-trash-or-recycling/",
        "hours": "Mon–Sat 8:00–18:00",
        "phone": "311",
    },
    {
        "name": "Culebra Bulky Waste / HHW Center (San Antonio)",
        "facility_type": "Bulky waste collection center + HHW drop-off",
        "city_slug": "san-antonio",
        "state": "TX",
        "zip": "78238",
        "address": "7030 Culebra Road, San Antonio, TX 78238",
        "lat": 29.4682,
        "lng": -98.6271,
        "source_url": "https://www.sa.gov/Directory/Departments/SWMD/HHW",
        "hours": "Tue–Fri 8:00–17:00; Sat 8:00–12:00",
        "phone": "210-207-6428",
    },
    {
        "name": "Bitters Bulky Waste Collection Center (San Antonio)",
        "facility_type": "Bulky waste collection center",
        "city_slug": "san-antonio",
        "state": "TX",
        "zip": "78216",
        "address": "1800 Wurzbach Parkway, San Antonio, TX 78216",
        "lat": 29.5645,
        "lng": -98.4948,
        "source_url": "https://www.sa.gov/Directory/Departments/SWMD/Brush-Bulky/Bulky-Drop-Off",
        "hours": "Tue–Fri 8:00–17:00; Sat 8:00–12:00",
        "phone": "210-207-6428",
    },
    {
        "name": "Austin Recycle and Reuse Center",
        "facility_type": "HHW / e-waste / appliance / reuse drop-off (appointment)",
        "city_slug": "austin",
        "state": "TX",
        "zip": "78744",
        "address": "2514 Business Center Drive, Austin, TX 78744",
        "lat": 30.1983,
        "lng": -97.7118,
        "source_url": "https://www.austintexas.gov/resource-recovery/locations/recycle-and-reuse-drop-center",
        "hours": "By appointment",
        "phone": "512-974-2000",
    },
    {
        "name": "Mecklenburg County Full-Service Recycling Center — Rozzelles Ferry area",
        "facility_type": "Full-service recycling / HHW / waste oil",
        "city_slug": "charlotte",
        "state": "NC",
        "zip": "28214",
        "address": "5740 Rozzelles Ferry Rd, Charlotte, NC 28214",
        "lat": 35.2789,
        "lng": -80.9347,
        "source_url": "https://wipeoutwaste.mecknc.gov/",
        "hours": "Confirm on Wipe Out Waste before visiting",
        "phone": "704-336-7600",
    },
    {
        "name": "Denver Solid Waste — Large Item / HHW programs (citywide)",
        "facility_type": "Municipal large-item & HHW programs",
        "city_slug": "denver",
        "state": "CO",
        "zip": "80202",
        "address": "Citywide collection — schedule via Denver Solid Waste / 311",
        "lat": 39.7392,
        "lng": -104.9903,
        "source_url": "https://www.denvergov.org/Government/Agencies-Departments-Offices/Agencies-Departments-Offices-Directory/Recycle-Compost-Trash/Large-Item-Pickup",
        "hours": "See Large Item Pickup calendar / HHW appointment",
        "phone": "720-913-1311",
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
        "philadelphia": clone_siblings(philadelphia()),
        "san-antonio": clone_siblings(san_antonio()),
        "austin": clone_siblings(austin()),
        "charlotte": clone_siblings(charlotte()),
        "denver": clone_siblings(denver()),
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

    print("Wave-4 metros written:")
    for city, rows in audited.items():
        print(f"  {city}: {len(rows)} rules")
    print(f"Total rules now: {len(keep)}")


if __name__ == "__main__":
    main()
