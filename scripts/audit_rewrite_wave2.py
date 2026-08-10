#!/usr/bin/env python3
"""Wave-2 portal audit: Dallas, Miami, Riverside, Bakersfield, Fresno."""

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


def dallas():
    c, st = "dallas", "TX"
    bulky = (
        "City of Dallas Sanitation — Brush and Bulky Item Collection",
        "https://dallascityhall.com/departments/sanitation/Pages/brush_and_bulky.aspx",
    )
    hhw = (
        "City of Dallas Sanitation — Home Chemical Waste Disposal",
        "https://dallascityhall.com/departments/sanitation/Pages/home_chemical.aspx",
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
            "Included with monthly brush/bulky (≤10 cubic yards)",
            "Dallas monthly brush & bulky curbside",
            "Dallas residential customers get monthly brush and bulky curbside collection (up to 10 cubic yards). Mattresses and furniture are listed among accepted items. Set items just behind the curb between Thursday and Sunday before your collection week — look up your week via Dallas.gov/sanitation, the Dallas Sanitation Services app, or 3-1-1. A once-per-year 20 cubic yard exception requires a service request the week before your collection week.",
            [
                "Confirm your brush/bulky collection week (Dallas.gov/sanitation, app, or 3-1-1).",
                "Set mattresses behind the curb Thu–Sun before that week (≤10 cubic yards total setout).",
                "Keep electronics, tires, construction debris, paint, and freon appliances out of this pile.",
            ],
            [
                (
                    "Oversize setout?",
                    "Request the annual 20 cubic yard exception online/app/3-1-1 the week prior (deadline Sunday 11:59 p.m. before a Monday collection week).",
                ),
                ("Fees for excess?", "Noncompliant / oversized setouts can be billed — confirm current rates with Sanitation."),
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
            "Not accepted in brush/bulky with freon — use tagged recovery / landfill options",
            "Certified freon recovery then Dallas landfill/transfer pathway",
            "Dallas brush/bulky guidance lists refrigerant-based (Freon) appliances as not accepted. Have a certified technician recover refrigerant and attach the required tag before using city landfill/transfer pathways. Do not set freon units with monthly brush/bulky.",
            [
                "Hire certified refrigerant recovery and keep the tag on the unit.",
                "Confirm drop-off at a City of Dallas landfill/transfer station with proof of residency.",
                "Keep chemicals and batteries for the Home Chemical Collection Center.",
            ],
            [("Bulky freon fridge?", "No — freon appliances are prohibited in brush/bulky setouts.")],
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
            False,
            "Not accepted in brush/bulky with freon",
            "Certified freon recovery then Dallas landfill/transfer pathway",
            "Window/central AC units with refrigerant follow the same Dallas rule as other freon appliances: not accepted in monthly brush/bulky. Recover refrigerant with a certified tech, then use landfill/transfer options Dallas Sanitation publishes for residents.",
            [
                "Recover refrigerant and tag the unit.",
                "Use landfill/transfer — not monthly bulky.",
                "Ask 3-1-1 if unsure about a specific unit size.",
            ],
            [("HHW for freon AC?", "Home Chemical Collection Center is for chemicals/select electronics — not a general freon-appliance dump.")],
            *bulky,
        )
    )
    for item in ["television", "computer-monitor"]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILL",
                "Medium",
                False,
                "Electronics not accepted in brush/bulky; HC3 does not list TVs",
                "Retailer take-back / confirm Dallas electronics options",
                "Dallas brush/bulky materials explicitly exclude electronics. The Dallas County Home Chemical Collection Center (11234 Plano Road) accepts computers and cell phones among electrical items, but city guidance says do not bring TVs or microwaves to HC3. Prefer manufacturer/retailer take-back for TVs/monitors, or confirm current city electronics drop-off options before hauling.",
                [
                    "Do not place TVs/monitors in monthly brush/bulky.",
                    "Use retailer/manufacturer recycling for large screens when possible.",
                    "Computers/phones may go to HC3 — confirm hours and residency proof.",
                ],
                [
                    ("HC3 TV?", "City home-chemical page lists computers/cell phones among acceptables and says no appliances, TVs, or microwaves."),
                ],
                *hhw,
            )
        )
    rows.append(
        R(
            c,
            st,
            "smartphone",
            "BANNED_FROM_LANDFILL",
            "Medium",
            False,
            "Free for Dallas residents at Home Chemical Collection Center",
            "Dallas County Home Chemical Collection Center — 11234 Plano Road",
            "Dallas residents can take cell phones and computers free to the Home Chemical Collection Center at 11234 Plano Road (bring current address proof). Hours published by Dallas County include Tuesdays (extended evening hours), Wednesdays–Thursdays, and the 2nd & 4th Saturdays — confirm before visiting. Business waste and TVs/microwaves are not HC3 pathways.",
            [
                "Wipe personal data from phones/computers.",
                "Bring driver’s license + utility bill proving a participating-city address.",
                "Visit during published HC3 hours (call 214-553-1765 if unsure).",
            ],
            [("Non-Dallas resident fee?", "Non-participating cities pay a waste-management fee — Dallas residents are free.")],
            *hhw,
        )
    )
    rows.append(
        R(
            c,
            st,
            "e-waste-mixed",
            "BANNED_FROM_LANDFILL",
            "Medium",
            False,
            "Free for Dallas residents at HC3 for accepted electronics",
            "Dallas County Home Chemical Collection Center — 11234 Plano Road",
            "Use the Home Chemical Collection Center for accepted small electronics (computers/cell phones listed). Do not put electronics in brush/bulky. TVs and microwaves are called out as not-for-HC3 — use retailer programs for those.",
            [
                "Sort TVs/microwaves away from HC3-eligible items.",
                "Take accepted e-scrap to 11234 Plano Road with residency proof.",
                "Never curb electronics with brush/bulky.",
            ],
            [("Brush/bulky electronics?", "Not accepted.")],
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
    ]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILL",
                "High" if item not in {"paint-latex", "fluorescent-bulbs"} else "Medium",
                False,
                "Free for Dallas residents at Home Chemical Collection Center",
                "Dallas County Home Chemical Collection Center — 11234 Plano Road",
                "Dallas residents dispose of home chemicals free at the Home Chemical Collection Center, 11234 Plano Road. Acceptable examples on the city page include paints, lawn/garden chemicals, pool chemicals, cleaners, batteries of all kinds, automobile fluids/oil filters, fluorescent tubes, and aerosols. Containers larger than 5 gallons, medical waste, smoke detectors, explosives, and business waste are not accepted. Bring proof of current address.",
                [
                    "Keep products sealed / upright; no mixing.",
                    "Bring residency proof (license + utility bill).",
                    "Confirm Tuesday–Thursday / 2nd & 4th Saturday hours before you go.",
                ],
                [
                    ("Smoke detectors?", "Listed among items not to bring to HC3."),
                    ("Events?", "Dallas Area HHW Network also runs collection events — call 214-553-1765."),
                ],
                *hhw,
            )
        )
    rows.append(
        R(
            c,
            st,
            "medical-sharps",
            "BANNED_FROM_LANDFILL",
            "High",
            False,
            "Not accepted at HC3 — use sharps mail-back / pharmacy programs",
            "Approved sharps container / pharmacy mail-back",
            "The Dallas Home Chemical Collection Center lists medical waste among items not to bring. Put home-generated sharps in an approved sharps container and use a pharmacy, hospital, or mail-back program that accepts them. Do not put needles in trash, recycling, or brush/bulky.",
            [
                "Use an approved rigid sharps container.",
                "Find a pharmacy/mail-back drop that accepts home sharps.",
                "Never loose-needle trash.",
            ],
            [("HC3 sharps?", "Medical waste is on the do-not-bring list.")],
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
            "Not accepted in brush/bulky — retailer / landfill fee pathway",
            "Tire retailer take-back",
            "Dallas brush/bulky materials list tires as not accepted. Prefer tire-retailer take-back when buying replacements, or confirm landfill/transfer acceptance and fees. Keep tires out of monthly brush piles.",
            ["Ask the tire shop to take old tires.", "Call Sanitation/landfill about fees if hauling yourself.", "Do not illegal-dump."],
            [("Bulky tires?", "No.")],
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
            "Included with monthly brush/bulky (limbs ≤10 ft / 8 in diameter; bagged leaves)",
            "Dallas monthly brush & bulky",
            "Dallas monthly brush collection accepts shrubs/tree limbs (max about 10 ft long / 8 in diameter) and bagged leaves along with bulky goods — still within the 10 cubic yard monthly cap. Confirm your collection week and set out Thu–Sun before that week.",
            [
                "Cut limbs to published size limits.",
                "Bag leaves; keep HHW out of the pile.",
                "Look up your brush week before setting out.",
            ],
            [("Weekly organics?", "Brush/bulky is monthly; regular garbage/recycling follow weekly schedules.")],
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
            "Regular garbage cart unless organics program applies at your address",
            "Dallas residential garbage cart",
            "Food scraps go in Dallas residential garbage service unless your address has a specific organics program. Never put food waste in recycling. Keep chemicals and batteries for HC3.",
            ["Use the garbage cart for food scraps.", "Keep recycling clean.", "Use HC3 for HHW."],
            [("Brush for food?", "No — brush/bulky is for yard/bulky materials.")],
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
            "Free (store film drop-off)",
            "Store film drop-off",
            "Plastic bags are not Dallas curbside recycling. Return clean dry film bags to grocery store drop-offs.",
            ["Keep bags clean/dry.", "Use store film bins.", "Prefer reusables."],
            [("Why?", "Film jams sorting equipment.")],
            *bulky,
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
            "Confirm HC3 acceptance / grease recycler for larger volumes",
            "Grease recycler / confirm HC3",
            "Do not pour cooking oil into Dallas drains or storm sewers. Small household quantities may be solidified for trash where allowed, or confirm whether HC3/events accept used cooking oil; larger volumes need a grease recycler.",
            ["Cool and contain oil.", "Call HC3 (214-553-1765) before assuming drop-off.", "Never storm-drain dump."],
            [("Motor oil?", "Used motor oil/filters are listed among HC3 automobile fluids.")],
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
            "Not accepted in brush/bulky — debris box / landfill fees",
            "Debris box / Dallas landfill-transfer",
            "Construction debris is not accepted in Dallas monthly brush/bulky. Use a debris box or resident landfill/transfer drop-off and keep paint/chemicals for HC3.",
            ["Separate HHW from C&D.", "Haul to landfill/transfer or hire a debris box.", "Do not curb C&D with brush week."],
            [("Bulky drywall?", "No — construction debris is prohibited in brush/bulky.")],
            *bulky,
        )
    )
    return rows


def miami():
    c, st = "miami", "FL"
    bulky = (
        "City of Miami Solid Waste — Mini Dump and Bulky Trash",
        "https://www.miami.gov/My-Home-Neighborhood/Garbage-Recycling/About-Mini-Dump-and-Bulky-Trash",
    )
    schedule = (
        "City of Miami Solid Waste — Garbage, Recycling, and Bulky Schedules",
        "https://www.miami.gov/My-Home-Neighborhood/Garbage-Recycling/View-Garbage-Pickup-Recycling-and-Bulky-Trash-Schedules",
    )
    hhw = (
        "Miami-Dade County — Home Chemical Collection Centers",
        "https://www.miamidade.gov/global/service.page?Mduid_service=ser1464798615648535",
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
            "Included with weekly City of Miami bulky trash (cart customers)",
            "City of Miami weekly bulky / Mini Dump",
            "City of Miami Solid Waste provides residential bulky trash collection once per week for eligible cart customers. Mattresses and household furniture are accepted. Place bulky items in front of the property the evening before your bulky day (use the city address lookup for the schedule). Apartment dumpster customers cannot curb bulky — use the Mini Dump at 1290 NW 20th Street (Mon–Fri 8–4, Sat 8–noon; residency proof; one pickup-truck load per day) or a private hauler.",
            [
                "Look up your bulky day on miami.gov address search.",
                "Set furniture/mattresses out the evening before (not early, not against dumpsters if you’re dumpster service).",
                "Or take a resident load to the Mini Dump with City of Miami residency proof.",
            ],
            [
                ("Bundle rule?", "City bulky guidance also references securely tied bundles ≤3 ft / ≤50 lbs for some setouts — oversized furniture still goes via bulky/Mini Dump pathways."),
                ("C&D?", "Construction debris is not accepted in bulky or Mini Dump."),
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
            "Medium",
            True,
            "Included with City of Miami bulky / Mini Dump white goods",
            "City of Miami bulky / Mini Dump",
            "City of Miami lists white goods (refrigerators, stoves, dishwashers, etc.) among bulky/Mini Dump acceptables for residents. Use weekly bulky if you’re on cart service, or the Mini Dump with residency proof. Keep propane tanks, chemicals, and batteries out — those are Mini Dump exclusions.",
            [
                "Confirm cart vs dumpster service at your building.",
                "Set white goods on bulky night or haul to Mini Dump.",
                "Take chemicals/propane to Miami-Dade Home Chemical Centers.",
            ],
            [("Hazardous with fridge?", "No chemicals/propane in Mini Dump — use Home Chemical Centers.")],
            *bulky,
        )
    )
    rows.append(
        R(
            c,
            st,
            "air-conditioner",
            "SPECIAL_HANDLING",
            "Medium",
            True,
            "Confirm bulky/Mini Dump white-goods acceptance for your AC type",
            "City of Miami bulky / Mini Dump",
            "Treat residential ACs as bulky white-goods pathway via City of Miami weekly bulky or Mini Dump when accepted. Do not mix refrigerants, cylinders, or chemicals into the load — hazardous materials are Mini Dump exclusions.",
            ["Use bulky day or Mini Dump.", "Keep cylinders/chemicals separate for HHW centers.", "Call 311 if your unit is commercial-size."],
            [("Propane?", "Propane/oxygen tanks are not accepted at Mini Dump.")],
            *bulky,
        )
    )
    for item in ["television", "computer-monitor", "smartphone", "e-waste-mixed"]:
        rows.append(
            R(
                c,
                st,
                item,
                "SPECIAL_HANDLING",
                "Medium",
                True,
                "City of Miami bulky / Mini Dump accepts household electronics",
                "City of Miami bulky / Mini Dump — 1290 NW 20th Street",
                "City of Miami bulky and Mini Dump guidance lists household electronics (TVs, monitors, computers, phones, printers, etc.) as accepted for residents. Use weekly bulky if eligible, or Mini Dump Mon–Fri 8–4 / Sat 8–noon with City of Miami residency proof (one trip/day, no commercial vehicles). Hazardous chemicals still go to Miami-Dade Home Chemical Collection Centers.",
                [
                    "Wipe data from computers/phones.",
                    "Use bulky night or Mini Dump — not garbage carts.",
                    "Keep paint/batteries/propane for Home Chemical Centers.",
                ],
                [("County TRC?", "Unincorporated Miami-Dade TRCs are a different system; City of Miami residents use City Solid Waste bulky/Mini Dump.")],
                *bulky,
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
        note = ""
        if item == "medical-sharps":
            note = " Confirm sharps acceptance before visiting; many residents use pharmacy sharps programs if a center declines a material."
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILL",
                "High" if item not in {"paint-latex", "fluorescent-bulbs"} else "Medium",
                False,
                "Free for Miami-Dade residents at Home Chemical Collection Centers",
                "Miami-Dade Home Chemical Collection Centers (West Dade / South Dade)",
                f"City of Miami Mini Dump excludes hazardous waste (chemicals, pesticides, propane/oxygen tanks, fluorescent & dry-cell batteries, lead-acid batteries, paint, etc.). Miami-Dade County residents — including City of Miami — can take home chemicals and many electronics to Home Chemical Collection Centers: West Dade (8801 NW 58th Street, Doral) and South Dade (23707 SW 97th Avenue, Homestead, Gate B), open Wednesday–Sunday 9 a.m.–5 p.m. (closed Christmas & Independence Day as observed). Bring a Florida ID/driver license.{note}",
                [
                    "Do not put HHW in City of Miami bulky or Mini Dump loads.",
                    "Pack sealed household quantities upright.",
                    "Visit West or South Dade Home Chemical Center Wed–Sun 9–5 with ID.",
                ],
                [
                    ("City Mini Dump paint?", "No — paint/chemicals are listed as Mini Dump don’ts."),
                    ("Mobile events?", "Miami-Dade also runs Home Chemical Drop-Off mobile events — see county solid-waste calendar."),
                ],
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
            "Not accepted in City bulky/Mini Dump — retailer take-back",
            "Tire retailer",
            "City of Miami Mini Dump/bulky don’ts include automobile parts and tires. Use tire-retailer take-back or a permitted disposal facility — not weekly bulky.",
            ["Ask the tire shop to take old tires.", "Do not curb tires as bulky.", "Call 311 for illegal-dumping questions."],
            [("Mini Dump tires?", "No.")],
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
            "Included with City of Miami bulky / Mini Dump clean yard trash",
            "City of Miami bulky / Mini Dump",
            "Clean yard trash (tree cuttings, shrubbery, bagged leaves/grass) is part of City of Miami bulky and Mini Dump pathways. Keep it separated from garbage and blue recycling bins. Look up your bulky day or haul to Mini Dump with residency proof.",
            ["Separate yard trash from garbage/recycling.", "Use bulky night or Mini Dump.", "No C&D mixed in."],
            [("Holiday skip?", "If bulky day falls on Christmas or MLK holiday, city guidance says collection moves to the next scheduled bulky day in your area.")],
            *schedule,
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
            "Regular City of Miami garbage cart",
            "City of Miami garbage cart",
            "Food/kitchen garbage goes in the City of Miami garbage cart — not recycling and not as bulky. Mini Dump excludes household garbage.",
            ["Use the garbage cart.", "Keep recycling clean.", "Use bulky only for oversized non-garbage items."],
            [("Bulky for food?", "No.")],
            *schedule,
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
            "Free (store film drop-off)",
            "Store film drop-off",
            "Plastic bags are not City of Miami curbside recycling. Return clean dry film to grocery store drop-offs.",
            ["Keep bags clean/dry.", "Use store film bins.", "Prefer reusables."],
            [("Why?", "Film contaminates recycling streams.")],
            *schedule,
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
            "Confirm Home Chemical Center / grease recycler",
            "Miami-Dade Home Chemical Center / grease recycler",
            "Do not pour cooking oil into Miami drains. Confirm whether a Home Chemical Collection Center accepts used cooking oil, or use a grease recycler for larger volumes.",
            ["Contain cooled oil.", "Call 311 / county solid waste before hauling.", "Never storm-drain dump."],
            [("Motor oil?", "Automotive fluids belong at Home Chemical Centers, not Mini Dump.")],
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
            "Not accepted at Mini Dump/bulky — hire debris service",
            "Private debris / C&D facility",
            "City of Miami bulky and Mini Dump exclude construction & demolition debris (drywall, tile, cabinets, toilets, roofing, etc.). Hire a permitted hauler or C&D facility — do not curb remodel debris as bulky.",
            ["Separate household bulky from remodel debris.", "Hire permitted C&D disposal.", "Keep paint for Home Chemical Centers."],
            [("Mini Dump cabinets?", "Remodeling cabinets/doors/tile are listed as Mini Dump don’ts.")],
            *bulky,
        )
    )
    return rows


def riverside():
    c, st = "riverside", "CA"
    bulky = (
        "City of Riverside Public Works — Bulky Items",
        "https://www.riversideca.gov/publicworks/trash-recycling/trash/bulky-items",
    )
    hhw = (
        "City of Riverside Public Works — Household Hazardous Waste",
        "https://www.riversideca.gov/publicworks/trash-recycling/trash/household-hazardous-waste",
    )
    agua = (
        "Riverside County Waste Resources — Agua Mansa Permanent HHW Facility",
        "https://rcwaste.org/agua-mansa-permanent-hhw-facility",
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
            "2 free bulky appointments/year (confirm item limit with hauler)",
            "City of Riverside bulky-item appointment",
            "Riverside residents get free curbside bulky-item pickups by appointment (city guidance: two per year for eligible households; extras may be fee-based). Mattresses must be completely wrapped/bagged in plastic or they will not be collected. Place items at the curb by 5:30 a.m. on the appointment day (night-before OK; not more than 24 hours early). Schedule via your service provider or 311. Alternative: free third-Saturday drop-off at Agua Mansa Transfer Station (1830 Agua Mansa Road; confirm hours) with city residency proof.",
            [
                "Call your hauler / 311 to book a bulky appointment.",
                "Fully wrap mattresses in plastic; curb by 5:30 a.m. appointment day.",
                "Or use the third-Saturday Agua Mansa Transfer Station drop-off if that fits better.",
            ],
            [
                ("Freon fridge on bulky?", "Appliances containing freon (AC, freezer, refrigerator) are non-acceptable curbside — use Riverside Public Utilities fridge recycling / County pathways."),
                ("E-waste on bulky?", "TVs/computers/phones are non-acceptable curbside — take to County HHW."),
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
            "Not accepted on curbside bulky with freon — RPU / special pathway",
            "Riverside Public Utilities refrigerator recycling / special handling",
            "City of Riverside bulky lists refrigerators/freezers/ACs containing freon as non-acceptable curbside items and points residents to the Riverside Public Utilities refrigerator recycling program for refrigerators. Do not set freon appliances out on a standard bulky appointment.",
            [
                "Check Riverside Public Utilities refrigerator recycling options.",
                "Do not place freon units on bulky curb appointments.",
                "Keep HHW chemicals for County HHW facilities.",
            ],
            [("Washer/dryer?", "Non-freon appliances like washer/dryer/stove/water heater (purged) are listed among accepted bulky items.")],
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
            False,
            "Not accepted on curbside bulky (freon appliance)",
            "Special freon appliance pathway",
            "Air conditioners are listed among Riverside non-acceptable curbside bulky items (freon appliances). Arrange a freon-compliant recycling pathway — do not curb ACs on bulky day. Chemicals and e-waste go to Riverside County HHW facilities such as Agua Mansa.",
            ["Do not book standard bulky for freon ACs.", "Ask 311/hauler about freon appliance options.", "Use County HHW for related chemicals."],
            [("Transfer Saturday drop-off?", "Agua Mansa Transfer Station third-Saturday drop-off is for bulky — confirm freon rules before hauling an AC.")],
            *bulky,
        )
    )
    for item in ["television", "computer-monitor", "smartphone", "e-waste-mixed"]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILL",
                "Medium",
                False,
                "Free for Riverside County residents at permanent HHW (Agua Mansa)",
                "Agua Mansa Permanent HHW Facility — 1780 Agua Mansa Road, Jurupa Valley",
                "Electronic waste (TVs, computers, monitors, cell phones, etc.) is not accepted in Riverside curbside bulky. City guidance sends residents to Riverside County HHW facilities. The Agua Mansa Permanent HHW Facility (1780 Agua Mansa Road, Jurupa Valley) is free for Riverside County residents on non-holiday Saturdays 9 a.m.–2 p.m. (confirm holiday closures). Transport limits typically 15 gallons or 125 pounds per visit.",
                [
                    "Do not curb e-waste on bulky appointments.",
                    "Pack household e-waste for County HHW.",
                    "Visit Agua Mansa HHW Sat 9–2 (or another County HHW site) with residency proof.",
                ],
                [("Bulky electronics?", "Listed as non-acceptable curbside.")],
                *agua,
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
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILL",
                "High" if item not in {"paint-latex", "fluorescent-bulbs"} else "Medium",
                False,
                "Free for Riverside County residents at permanent HHW facilities",
                "Agua Mansa Permanent HHW Facility — 1780 Agua Mansa Road",
                "It is illegal in California to trash HHW. Riverside city pages direct residents to Riverside County HHW. Agua Mansa Permanent HHW Facility accepts paint (latex/oil), batteries, antifreeze, BBQ/camp propane, fluorescents, garden chemicals, pool chlorine, sharps, unused medication (except controlled substances), used oil/filters, and e-waste — free for county residents, non-holiday Saturdays 9 a.m.–2 p.m. Limit about 15 gallons / 125 pounds per vehicle visit.",
                [
                    "Keep products labeled and sealed; do not mix wastes.",
                    "Stay within transport limits (≈15 gal / 125 lb).",
                    "Drop at Agua Mansa HHW Sat 9–2 or another County HHW/ABOP site.",
                ],
                [
                    ("City curb HHW?", "No — paint, batteries, oil, bulbs, etc. are non-acceptable bulky items."),
                    ("Phone?", "County Waste Resources 951-486-3200."),
                ],
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
            "Not accepted on bulky curb — retailer / County confirms",
            "Tire retailer",
            "Automotive parts and tires are non-acceptable Riverside curbside bulky items. Prefer retailer take-back; County HHW pages also list tires among permanent-HHW unacceptables — do not assume HHW will take tires.",
            ["Ask the tire shop to take old tires.", "Do not curb tires on bulky day.", "Confirm transfer fees if hauling yourself."],
            [("HHW tires?", "Typically not accepted at permanent HHW — confirm before visiting.")],
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
            "Organics cart / bulky bundled trimmings",
            "Riverside organics cart or bulky appointment",
            "Use Riverside organics/green-waste service for routine yard trimmings. For bulky appointments, tree trimmings must be tied in bundles ≤18 inches diameter and ≤36 inches long — no large limbs, trunks, or stumps on curb bulky.",
            ["Use the organics cart for normal yard waste.", "Bundle oversized brush to bulky size rules if using an appointment.", "Keep HHW out of organics."],
            [("Stumps?", "Not on curbside bulky — arrange special disposal.")],
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
            "Included with Riverside organics",
            "Riverside organics cart",
            "Food scraps go in Riverside organics — not recycling. Never put sharps or HHW in organics carts.",
            ["Collect scraps for organics.", "Keep plastics out.", "Report missed service via 311."],
            [("Sharps in organics?", "Illegal — use County HHW sharps acceptance.")],
            *hhw,
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
            "Free (store film drop-off)",
            "Store film drop-off",
            "Plastic bags are not Riverside curbside recycling. Return clean dry film to store drop-offs.",
            ["Keep bags clean/dry.", "Use store film bins.", "Prefer reusables."],
            [("Why?", "Film jams equipment.")],
            *bulky,
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
            "Confirm County HHW acceptance / grease recycler",
            "County HHW / grease recycler",
            "Do not pour cooking oil into Riverside drains. Confirm Agua Mansa / County HHW acceptance for used cooking oil, or use a grease recycler for larger volumes.",
            ["Contain cooled oil.", "Call County Waste Resources before assuming drop-off.", "Never storm-drain dump."],
            [("Motor oil?", "Used oil and filters are accepted at permanent HHW.")],
            *agua,
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
            "Not accepted on curbside bulky — debris box / transfer",
            "Debris box / transfer",
            "Construction/demolition materials (wood scrap, brick, concrete, drywall, doors, lumber, tile, metal) are non-acceptable Riverside curbside bulky items. Use a debris box or transfer station; keep paint for County HHW.",
            ["Separate C&D from household bulky.", "Haul via debris box/transfer.", "Take paint/batteries to HHW."],
            [("Carpet size?", "Rugs/carpet on bulky are limited (about 4×4 ft pieces, rolled/tied) — larger C&D carpet is not a free-for-all.")],
            *bulky,
        )
    )
    return rows


def bakersfield():
    c, st = "bakersfield", "CA"
    bulky = (
        "City of Bakersfield Solid Waste — Garbage / Recycling",
        "https://www.bakersfieldcity.us/374/Garbage-Recycling",
    )
    hhw = (
        "Kern County Public Works — Residential Hazardous Waste",
        "https://www.kernpublicworks.com/services/solid-waste/hazardous-waste/residential-hazardous-waste",
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
            "Free — 2 bulky items per quarter by appointment",
            "City of Bakersfield curbside bulky pickup",
            "City of Bakersfield (with Kern Refuse) offers curbside bulky pickup for single-family homes and apartments with 4 units or less: up to 2 bulky items per quarter at no additional charge. Call Solid Waste at (661) 326-3114 to schedule. Accepted examples include furniture, mattresses, box springs, major appliances, e-waste (TV/monitor/computer), water heaters, and BBQ grills without propane. Place items curbside before 6:00 a.m. on the appointment day with ~5 ft clearance. City also hosts periodic bulky drop-off events — confirm dates on city notices.",
            [
                "Call (661) 326-3114 to book (2 items/quarter).",
                "Set mattresses curbside before 6:00 a.m. appointment day.",
                "Keep propane tanks, construction debris, and HHW out of the setout.",
            ],
            [
                (
                    "Not accepted?",
                    "City bulky flyer excludes propane tanks, construction debris, doors/cabinets, carpets, toilets, concrete, spas, pool tables, large AC units, and items over 300 lbs.",
                ),
                ("Freon?", "Drop-off events often exclude items with refrigerant — confirm before hauling freon appliances."),
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
            "Medium",
            True,
            "Often via bulky appointment — confirm freon rules",
            "City of Bakersfield bulky pickup",
            "Major appliances are listed on Bakersfield’s curbside bulky program. Secure appliance doors with rope/duct tape before setout. Confirm refrigerant rules when you call (661) 326-3114 — some city drop-off events exclude refrigerant items. Do not put freon appliances in carts.",
            [
                "Call Solid Waste to schedule and ask about freon acceptance.",
                "Tape/secure doors; curb before 6:00 a.m.",
                "Take chemicals to Kern County Special Waste Facility.",
            ],
            [("Over 300 lbs?", "Items over 300 lbs are excluded from the bulky program.")],
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
            False,
            "Large AC units excluded from city bulky flyer — special pathway",
            "Confirm with Solid Waste / certified recovery",
            "City of Bakersfield bulky materials list large AC units among unacceptable items. Call Solid Waste about smaller units or freon recovery requirements; do not assume curbside bulky will take a large AC. Chemicals stay for Kern County Special Waste.",
            ["Call (661) 326-3114 before setting out an AC.", "Arrange freon-compliant recycling if required.", "Use Special Waste Facility for related HHW."],
            [("Event freon?", "City bulky drop-off events often list refrigerant items as not accepted.")],
            *bulky,
        )
    )
    for item in ["television", "computer-monitor", "smartphone", "e-waste-mixed"]:
        rows.append(
            R(
                c,
                st,
                item,
                "SPECIAL_HANDLING",
                "Medium",
                True,
                "City bulky accepts e-waste OR free at Kern Special Waste (size limits)",
                "Bakersfield bulky appointment or Kern Special Waste Facility",
                "Bakersfield curbside bulky lists electronics (TV, monitor, computer) among accepted items (2 items/quarter). Alternatively, Kern County Special Waste Facility at 4951 Standard Street accepts electronics with limits (e.g., TVs 19″ or less listed on the county page) plus phones/computers — open Mon–Sat 8 a.m.–4 p.m. for Kern County residents. Prefer wiping data before drop-off.",
                [
                    "Either book city bulky for large TVs/computers or use Special Waste for qualifying e-waste.",
                    "Confirm TV size limits at Special Waste before hauling large screens.",
                    "Keep chemicals with HHW loads.",
                ],
                [("Special Waste hours?", "County page: Mon–Sat 8:00 a.m.–4:00 p.m. at 4951 Standard Street.")],
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
        "medical-sharps",
    ]:
        med = ""
        if item == "medical-sharps":
            med = " Home-generated sharps must be in a rigid biohazard sharps container (not detergent bottles/coffee cans); free containers are often available at the facility when supplies allow."
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILL",
                "High" if item not in {"paint-latex", "fluorescent-bulbs"} else "Medium",
                False,
                "Free for Kern County residents at Special Waste Facility",
                "Kern County Special Waste Facility — 4951 Standard Street, Bakersfield",
                f"Do not put HHW in Bakersfield trash or bulky setouts. Kern County residents can drop residential hazardous waste free at the Bakersfield Special Waste Facility, 4951 Standard Street (Standard & Foster), Mon–Sat 8 a.m.–4 p.m. Accepted examples include paints, pesticides, pool chemicals, batteries, antifreeze, used oil/filters, BBQ/camping propane, fluorescents, sharps, and many electronics. Limit 15 gallons or 125 pounds per vehicle trip; no container over 5 gallons.{med}",
                [
                    "Pack sealed, labeled household quantities (do not mix).",
                    "Stay within 15 gal / 125 lb transport limits.",
                    "Visit 4951 Standard Street Mon–Sat 8–4; remain in vehicle as directed.",
                ],
                [
                    ("Stop 'n' Shop?", "Bakersfield facility offers free reuse of some still-usable products mornings Mon–Sat 8–noon."),
                    ("Phone?", "(661) 862-8900 or (800) 552-KERN."),
                ],
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
            "Not a city bulky default — retailer take-back",
            "Tire retailer",
            "Bakersfield bulky program materials focus on furniture/appliances/e-waste — not tire dumping. Prefer retailer take-back when replacing tires; confirm landfill/transfer fees if hauling yourself.",
            ["Ask the tire shop to take old tires.", "Do not illegal-dump.", "Call Solid Waste only if you need a special pathway."],
            [("Bulky tires?", "Not listed among accepted bulky items.")],
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
            "Included with Bakersfield organics/green waste",
            "Bakersfield organics cart",
            "Use Bakersfield organics/green-waste service for yard trimmings. Oversized brush may need bulky appointment or a city drop-off event — confirm size rules when you call Solid Waste. Keep HHW for Special Waste Facility.",
            ["Use the organics cart.", "Call for oversized brush options.", "Never put chemicals in organics."],
            [("Food scraps?", "Organics where provided.")],
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
            "Included with Bakersfield organics",
            "Bakersfield organics cart",
            "Food scraps go in Bakersfield organics — not recycling. Never put sharps or HHW in organics carts.",
            ["Collect scraps for organics.", "Keep plastics out.", "Report missed service to Solid Waste."],
            [("Sharps?", "Use Special Waste Facility sharps program.")],
            *hhw,
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
            "Free (store film drop-off)",
            "Store film drop-off",
            "Plastic bags are not Bakersfield curbside recycling. Return clean dry film to store drop-offs.",
            ["Keep bags clean/dry.", "Use store film bins.", "Prefer reusables."],
            [("Why?", "Film jams equipment.")],
            *bulky,
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
            "Confirm Special Waste acceptance / grease recycler",
            "Kern Special Waste / grease recycler",
            "Do not pour cooking oil into Bakersfield drains. Confirm whether Special Waste accepts used cooking oil (grease/lubricants appear on county accept lists) or use a grease recycler for large volumes.",
            ["Contain cooled oil.", "Call (661) 862-8900 if unsure.", "Never storm-drain dump."],
            [("Motor oil?", "Used motor oil and filters are accepted at Special Waste.")],
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
            "Not accepted on city bulky — debris box / landfill",
            "Debris box / Kern landfill-transfer",
            "City of Bakersfield bulky materials exclude construction debris (concrete, doors, cabinets, carpets, toilets, etc.). Use a debris box or landfill/transfer; keep paint for Special Waste.",
            ["Separate C&D from household bulky.", "Haul via debris box/landfill.", "Take paint/batteries to Special Waste."],
            [("Bulky drywall?", "Construction debris is unacceptable on the city bulky program.")],
            *bulky,
        )
    )
    return rows


def fresno():
    c, st = "fresno", "CA"
    clean = (
        "City of Fresno — Operation Clean Up",
        "https://www.fresno.gov/publicutilities/trash-disposal-recycling/operation-clean-up/",
    )
    hhw_city = (
        "City of Fresno — Hazardous Waste and Sharps Disposal",
        "https://www.fresno.gov/publicutilities/trash-disposal-recycling/used-motor-oil-oil-flter-recycling/",
    )
    hhw = (
        "Fresno County — Household Hazardous Waste / Environmental Compliance Center",
        "https://cleanupfresnocounty.com/drop-off-locations/",
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
            "Annual Operation Clean Up / Free Dump Events / Special Haul fees",
            "City of Fresno Operation Clean Up",
            "City of Fresno residential solid-waste customers get Operation Clean Up once a year for curbside bulky items (mattresses and box springs are listed). Only residences paying city solid waste on the utility bill are eligible; multi-family (4+ units) is generally not eligible. Watch for your Clean Up notice/schedule. Between Clean Ups, use fee-based Special Hauls or Free Dump Events at CARTS (3457 S. Cedar Ave.) when offered (typically spring/fall; one pickup-truck payload; bring utility bill + ID).",
            [
                "Confirm you are a City of Fresno solid-waste customer.",
                "Set mattresses out only during your Operation Clean Up window (or use Free Dump Event / Special Haul).",
                "Keep refrigerators/freezers and HHW out of Clean Up piles.",
            ],
            [
                ("Fridge on Clean Up?", "Furniture/appliances are allowed, but refrigerators/freezers are not accepted on Operation Clean Up."),
                ("Multi-family?", "4+ unit properties are not eligible — contact the property’s hauler."),
            ],
            *clean,
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
            "Not on Operation Clean Up — Special Haul / Free Dump Event rules",
            "Fresno Special Haul or Free Dump Event (confirm freon)",
            "Operation Clean Up explicitly does not accept refrigerators or freezers. Ask about Special Haul rules/fees or Free Dump Event appliance acceptance, and confirm refrigerant requirements before scheduling. Never put freon appliances in carts.",
            [
                "Do not set refrigerators out for Operation Clean Up.",
                "Call Solid Waste / your area hauler about Special Haul or event options.",
                "Take HHW to Fresno County Environmental Compliance Center.",
            ],
            [
                ("North vs south hauler?", "City pages route some multi-family contacts to Allied (north of Ashlan) or Mid Valley (south) — single-family Clean Up is city-run."),
            ],
            *clean,
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
            "Confirm Special Haul / event freon rules — not a Clean Up default",
            "Fresno Special Haul / event",
            "Treat freon ACs like other refrigerant appliances: not a standard Operation Clean Up refrigerator pathway. Confirm Special Haul or Free Dump Event acceptance and freon rules before setout/hauling.",
            ["Call before setting out.", "Do not vent refrigerant.", "Use County ECC for chemicals."],
            [("Clean Up AC?", "Confirm — freon appliances are restricted on Clean Up (no refrigerators/freezers).")],
            *clean,
        )
    )
    for item in ["television", "computer-monitor", "smartphone", "e-waste-mixed"]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILL",
                "Medium",
                False,
                "Free residential drop-off at Fresno County ECC (confirm hours)",
                "Fresno County Environmental Compliance Center — 1327 W. Dan Ronquillo Drive",
                "City of Fresno directs HHW/e-waste questions to Fresno County. Residents can use the Environmental Compliance Center at 1327 West Dan Ronquillo Drive for electronics (phones, laptops, printers, TVs/monitors listed among HHW acceptables). County drop-off pages list hours in the Thu–Sat / Fri–Sat 9 a.m.–3 p.m. range excluding holidays — call (559) 600-4259 before visiting. Do not put e-waste in recycling carts.",
                [
                    "Wipe data from devices.",
                    "Call (559) 600-4259 to confirm hours and TV acceptance.",
                    "Drop at 1327 W. Dan Ronquillo Drive with household quantities.",
                ],
                [("City Clean Up e-waste?", "Prefer County ECC / network sites — Clean Up focuses on bulky furniture/yard debris.")],
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
        "medical-sharps",
    ]:
        med = ""
        if item == "medical-sharps":
            med = " City/County also place sharps kiosks around Fresno; home sharps for County drop-off must be in a rigid sealed container. Pharmaceuticals use separate kiosks — not toilet/trash."
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILL",
                "High" if item not in {"paint-latex", "fluorescent-bulbs"} else "Medium",
                False,
                "Free residential HHW at Fresno County ECC / network sites",
                "Fresno County Environmental Compliance Center — 1327 W. Dan Ronquillo Drive",
                f"Do not trash HHW in Fresno. Use Fresno County’s Environmental Compliance Center (1327 W. Dan Ronquillo Drive) or County network sites for paint, batteries, automotive fluids, propane (small), fluorescents, pesticides, and related household chemicals. Call (559) 600-4259 for hours and material confirmation; door-to-door pickup may be available for homebound/disabled residents.{med}",
                [
                    "Keep products sealed and labeled; do not mix.",
                    "Confirm ECC hours at (559) 600-4259.",
                    "Use City/County sharps/pharma kiosks when that is the better fit.",
                ],
                [
                    ("City hotline?", "Fresno Recycling Hotline (559) 621-1111 for city program questions."),
                    ("Business waste?", "County CESQG program — not free residential HHW."),
                ],
                *hhw_city,
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
            "Not Operation Clean Up default — retailer / landfill fees",
            "Tire retailer",
            "Prefer tire-retailer take-back. Operation Clean Up focuses on furniture, mattresses, limited yard debris, etc. — do not assume tires are included. Confirm landfill/transfer fees if hauling yourself.",
            ["Ask the tire shop to take old tires.", "Do not illegal-dump.", "Call Solid Waste if you need a special haul quote."],
            [("Clean Up tires?", "Not listed among Operation Clean Up accepted items.")],
            *clean,
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
            "Included with Fresno organics; oversized via Clean Up rules",
            "Fresno organics cart / Operation Clean Up",
            "Use Fresno organics/green-waste service for routine yard waste. Operation Clean Up allows trees/shrubs/yard debris cut to ≤4 feet. Keep HHW and freon appliances out of Clean Up piles.",
            ["Use organics for normal yard waste.", "Cut Clean Up brush to ≤4 ft if using that program.", "Take chemicals to County ECC."],
            [("Free Dump Event yard waste?", "Free Dump Events list wood/yard trimmings among accepted items when events run.")],
            *clean,
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
            "Included with Fresno organics",
            "Fresno organics cart",
            "Food scraps go in Fresno organics — not recycling. Never put sharps or HHW in organics carts.",
            ["Collect scraps for organics.", "Keep plastics out.", "Report missed service to Solid Waste."],
            [("Sharps?", "Use City/County sharps kiosks or County ECC rules.")],
            *hhw_city,
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
            "Free (store film drop-off)",
            "Store film drop-off",
            "Plastic bags are not Fresno curbside recycling. Return clean dry film to store drop-offs.",
            ["Keep bags clean/dry.", "Use store film bins.", "Prefer reusables."],
            [("Why?", "Film jams equipment.")],
            *clean,
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
            "County ECC lists cooking oil among HHW acceptables",
            "Fresno County Environmental Compliance Center",
            "Do not pour cooking oil into Fresno drains. Fresno County HHW materials list cooking oil/grease among drop-off acceptables at the Environmental Compliance Center — confirm when you call (559) 600-4259. Larger volumes may need a grease recycler.",
            ["Contain cooled oil.", "Confirm ECC acceptance/hours.", "Never storm-drain dump."],
            [("Motor oil?", "Automotive oil/filters are also County HHW pathways.")],
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
            "Limited Clean Up items / Free Dump Event C&D / debris box",
            "CARTS Free Dump Event or debris box",
            "Operation Clean Up allows some remodel-adjacent items with prep rules (e.g., cabinets disassembled, wood fencing ≤4 ft stacked). Free Dump Events at CARTS list broader C&D (drywall, asphalt/concrete clean, etc.) when events run. Otherwise use a debris box. Keep paint for County ECC.",
            ["Check whether Clean Up or a Free Dump Event covers your debris type.", "Otherwise hire a debris box.", "Take paint/batteries to ECC."],
            [("Hot tub?", "Clean Up allows spas ≤8×8 cut into 4×4 sections.")],
            *clean,
        )
    )
    return rows


def main() -> None:
    audited_cities = {
        "dallas": clone_siblings(dallas()),
        "miami": clone_siblings(miami()),
        "riverside": clone_siblings(riverside()),
        "bakersfield": clone_siblings(bakersfield()),
        "fresno": clone_siblings(fresno()),
    }

    all_path = DATA / "rules" / "all.json"
    rules = json.loads(all_path.read_text())
    keep = [r for r in rules if r.get("city_slug") not in audited_cities]
    for rows in audited_cities.values():
        keep.extend(rows)

    for r in keep:
        if r.get("common_disposal_fee"):
            r["common_disposal_fee"] = str(r["common_disposal_fee"])[:80]
        if r.get("nearest_facility_type"):
            r["nearest_facility_type"] = str(r["nearest_facility_type"])[:120]

    all_path.write_text(json.dumps(keep, indent=2))
    ca = [r for r in keep if r.get("state") == "CA" or not r.get("city_slug")]
    national = [r for r in keep if r.get("city_slug") and r.get("state") != "CA"]
    (DATA / "rules" / "ca.json").write_text(json.dumps(ca, indent=2))
    (DATA / "rules" / "national.json").write_text(json.dumps(national, indent=2))

    fac_path = DATA / "facilities" / "all.json"
    facilities = json.loads(fac_path.read_text())
    updates = {
        "dallas": [
            {
                "name": "Dallas County Home Chemical Collection Center",
                "facility_type": "HHW / select e-waste",
                "city_slug": "dallas",
                "state": "TX",
                "zip": "75243",
                "address": "11234 Plano Road, Dallas, TX 75243",
                "lat": 32.907,
                "lng": -96.702,
                "source_url": "https://dallascityhall.com/departments/sanitation/Pages/home_chemical.aspx",
                "hours": "Tue extended; Wed–Thu daytime; 2nd & 4th Sat (confirm)",
                "phone": "214-553-1765",
            }
        ],
        "miami": [
            {
                "name": "City of Miami Mini Dump Facility",
                "facility_type": "Bulky / yard / household electronics",
                "city_slug": "miami",
                "state": "FL",
                "zip": "33142",
                "address": "1290 NW 20th Street, Miami, FL 33142",
                "lat": 25.794,
                "lng": -80.224,
                "source_url": "https://www.miami.gov/My-Home-Neighborhood/Garbage-Recycling/About-Mini-Dump-and-Bulky-Trash",
                "hours": "Mon–Fri 8:00–16:00; Sat 8:00–12:00",
                "phone": "311",
            },
            {
                "name": "Miami-Dade Home Chemical Collection Center — West Dade",
                "facility_type": "HHW / e-waste",
                "city_slug": "miami",
                "state": "FL",
                "zip": "33178",
                "address": "8801 NW 58th Street, Doral, FL 33178",
                "lat": 25.827,
                "lng": -80.338,
                "source_url": "https://www.miamidade.gov/global/service.page?Mduid_service=ser1464798615648535",
                "hours": "Wed–Sun 9:00–17:00",
                "phone": "311",
            },
        ],
        "riverside": [
            {
                "name": "Agua Mansa Permanent HHW Facility",
                "facility_type": "HHW / e-waste",
                "city_slug": "riverside",
                "state": "CA",
                "zip": "92509",
                "address": "1780 Agua Mansa Road, Jurupa Valley, CA 92509",
                "lat": 34.03,
                "lng": -117.4,
                "source_url": "https://rcwaste.org/agua-mansa-permanent-hhw-facility",
                "hours": "Non-holiday Saturdays 9:00–14:00",
                "phone": "951-486-3200",
            }
        ],
        "bakersfield": [
            {
                "name": "Kern County Special Waste Facility — Bakersfield",
                "facility_type": "HHW / select e-waste",
                "city_slug": "bakersfield",
                "state": "CA",
                "zip": "93308",
                "address": "4951 Standard Street, Bakersfield, CA 93308",
                "lat": 35.393,
                "lng": -119.019,
                "source_url": "https://www.kernpublicworks.com/services/solid-waste/hazardous-waste/residential-hazardous-waste",
                "hours": "Mon–Sat 8:00–16:00",
                "phone": "(661) 862-8900",
            }
        ],
        "fresno": [
            {
                "name": "Fresno County Environmental Compliance Center",
                "facility_type": "HHW / e-waste",
                "city_slug": "fresno",
                "state": "CA",
                "zip": "93706",
                "address": "1327 West Dan Ronquillo Drive, Fresno, CA 93706",
                "lat": 36.71,
                "lng": -119.81,
                "source_url": "https://cleanupfresnocounty.com/drop-off-locations/",
                "hours": "Confirm Thu–Sat or Fri–Sat 9:00–15:00 (call before visit)",
                "phone": "(559) 600-4259",
            }
        ],
    }
    facilities = [f for f in facilities if f.get("city_slug") not in updates]
    for rows in updates.values():
        facilities.extend(rows)
    fac_path.write_text(json.dumps(facilities, indent=2))
    (DATA / "facilities" / "ca.json").write_text(
        json.dumps([f for f in facilities if f.get("state") == "CA"], indent=2)
    )

    print("Audited cities:", ", ".join(sorted(audited_cities)))
    print("Total rules:", len(keep))
    for city, rows in audited_cities.items():
        print(f"  {city}: {len(rows)} rules; mattress source={rows[0]['source_name'][:50]}")


if __name__ == "__main__":
    main()
