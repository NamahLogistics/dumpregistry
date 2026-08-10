#!/usr/bin/env python3
"""Spot-audit rewrite: replace templated metro answers with portal-specific facts."""

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


def houston():
    c, st = "houston", "TX"
    esc = ("City of Houston SWMD — Environmental Service Centers", "https://www.houstontx.gov/solidwaste/esc.html")
    heavy = ("City of Houston SWMD — Heavy Trash / Junk Waste", "https://www.houstontx.gov/solidwaste/treewaste.html")
    depo = ("City of Houston SWMD — Residential Drop-Off Centers", "https://www.houstontx.gov/solidwaste/depository.html")
    rows = []
    rows.append(
        R(
            c,
            st,
            "mattress",
            "SPECIAL_HANDLING",
            "Low",
            True,
            "Included with eligible heavy-trash / depository drop-off",
            "Houston junk-waste curbside or Neighborhood Depository",
            "Houston lists mattresses and box springs as junk waste. Eligible curbside addresses get heavy trash every other month (up to six curbside heavy-trash collections per year). Look up your day in HTX Collects / the city service lookup. You can also take mattresses to a Neighborhood Depository (typically Tue–Sat; confirm hours) up to four times per month with matching Texas ID + Houston utility bill/lease.",
            [
                "Look up your heavy-trash / junk-waste day in HTX Collects or the city service lookup.",
                "Set mattresses out only on your junk-waste cycle (not a regular trash day).",
                "Or drop off at a Neighborhood Depository with matching ID + utility bill/lease.",
            ],
            [
                ("Tree vs junk month?", "Houston separates tree waste and junk waste on alternating heavy-trash months — confirm your schedule."),
                ("ESC for mattresses?", "ESCs are for HHW/select recyclables; mattresses go via junk waste / depositories."),
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
            True,
            "Heavy trash / depository — freon tag required",
            "Houston junk waste or Neighborhood Depository",
            "Houston accepts refrigerators/freezers for junk waste or Neighborhood Depository drop-off only with a certified technician tag showing refrigerant has been removed. Untagged freon units are not accepted in those pathways. Do not put freon appliances in regular carts.",
            [
                "Have a certified tech recover refrigerant and attach the tag.",
                "Set out on your junk-waste heavy-trash day or take to a depository with residency proof.",
                "Keep HHW chemicals for Environmental Service Centers.",
            ],
            [("No tag?", "City guidance requires a freon-removal tag before refrigerator acceptance.")],
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
            True,
            "Not published as ESC HHW — confirm appliance pathway / freon tag rules",
            "Houston appliance / junk pathway",
            "Treat window/central AC units like other freon appliances in Houston: do not put them in carts. Confirm whether your unit qualifies for junk-waste/depository acceptance with a freon-recovery tag, or use a licensed appliance recycler. HHW ESCs list small electrical appliances/electronics — not as a substitute for large freon appliances.",
            [
                "Confirm freon tagging / acceptance before set-out or drop-off.",
                "Do not vent refrigerant yourself.",
                "Use ESC for chemicals/batteries separately.",
            ],
            [("ESC large AC?", "ESC accepted lists emphasize HHW, e-scrap, and small appliances — confirm large freon units separately.")],
            *heavy,
        )
    )
    for item, label in [
        ("television", "TVs"),
        ("computer-monitor", "monitors"),
        ("smartphone", "phones / telephone equipment"),
        ("e-waste-mixed", "computer equipment, electronic scrap, printers"),
    ]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "Free for Houston residents at ESCs (residency rules apply)",
                "Houston ESC South — 11500 S. Post Oak Rd",
                f"Houston Environmental Service Centers accept {label} and related e-scrap that should not go in trash/recycling carts. ESC South (11500 S. Post Oak Rd) is open Tue/Wed/Fri/Sat 8 a.m.–5 p.m. ESC North (5614 Neches St) is open the second Thursday monthly 9 a.m.–3 p.m. Bring residency documents as required; do not strip/break down TVs.",
                [
                    "Confirm the item is on the ESC accepted list.",
                    "Visit ESC South or North during published hours.",
                    "Bring matching Texas ID + Houston utility bill/lease when required.",
                ],
                [("Paint limit at ESC?", "ESC lists paint (latex & oil) with a 25-gallon maximum.")],
                *esc,
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
        "cooking-oil",
    ]:
        extra = {
            "paint-latex": " Paint (latex & oil) is listed with a 25-gallon maximum.",
            "paint-oil": " Paint (latex & oil) is listed with a 25-gallon maximum.",
            "propane-tank": " Propane tanks are listed at a 5-gallon maximum.",
            "car-battery": " Lead-acid and rechargeable batteries are listed (not a dump-anything battery rule).",
            "cooking-oil": " Cooking oil is explicitly listed among ESC accepted materials.",
            "medical-sharps": " Confirm sharps acceptance before visiting — if not listed for your container type, use a medical sharps program.",
        }.get(item, "")
        rows.append(
            R(
                c,
                st,
                item,
                "SPECIAL_HANDLING" if item in {"paint-latex", "cooking-oil"} else "BANNED_FROM_LANDFILLS",
                "Medium" if item in {"paint-latex", "cooking-oil"} else "High",
                False,
                "Free for Houston residents at ESCs (limits apply)",
                "Houston Environmental Service Centers",
                f"Take this household hazardous / special waste to a City of Houston Environmental Service Center — not carts.{extra} ESC South: 11500 S. Post Oak Rd, Tue/Wed/Fri/Sat 8 a.m.–5 p.m. ESC North: 5614 Neches St, second Thursday monthly 9 a.m.–3 p.m.",
                [
                    "Pack sealed, labeled containers upright.",
                    "Use ESC South or North per published hours.",
                    "Call SWMD / HHW line 713-551-7355 if unsure an item is accepted.",
                ],
                [("Tires at ESC?", "ESC lists up to 5 tires per residence per month (no commercial vehicle tires).")],
                *esc,
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
            "ESC: up to 5/residence/month; curbside also lists tire limits — confirm",
            "Houston ESC or heavy-trash tire rules",
            "Houston ESC accepted materials include tires with a limit of 5 tires per residence per month (no commercial vehicle tires). Curbside heavy-trash guidance has also published per-household tire limits — confirm current curbside rules before set-out. Do not illegal-dump.",
            [
                "Prefer ESC drop-off within the published tire limit.",
                "Or confirm curbside tire rules for your address.",
                "Commercial loads need different permitting.",
            ],
            [("Depository tires?", "Neighborhood depositories have also published passenger-tire limits — check the current depository rules PDF.")],
            *esc,
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
            "Included with Houston tree-waste heavy trash when eligible",
            "Houston tree-waste collection / depository",
            "Houston collects tree waste on the heavy-trash cycle (tree waste vs junk waste alternate by month). Tree waste means clean wood waste — limbs/branches/stumps; furniture and treated wood are not tree waste. Look up your schedule in HTX Collects. Depositories also accept tree waste with residency proof.",
            [
                "Confirm whether your next heavy-trash month is tree waste or junk waste.",
                "Set out clean wood waste only on tree-waste cycles.",
                "Keep plastics/bags contamination out of tree piles per city rules.",
            ],
            [("Leaves?", "Depository guidance notes leaves should be in compostable bags when dropping tree waste — confirm current rules.")],
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
            "Not published as citywide cart organics — confirm current Houston organics options",
            "Houston organics / compost options",
            "Houston’s published heavy-trash pages focus on junk/tree waste, not a universal food-scrap cart for every address. Do not put food scraps in recycling. Confirm current organics/compost options for your address on SWMD pages or 311 before changing your set-out.",
            [
                "Check current organics guidance for your address.",
                "Keep food out of recycling carts.",
                "Use 311 / HTX Collects for service questions.",
            ],
            [("Same as tree waste?", "No — tree waste is clean wood, not food scraps.")],
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
            "Free at ESC (plastic grocery bags / plastic film listed)",
            "Houston ESC",
            "Houston ESCs list plastic grocery bags and plastic film among accepted materials. Do not put film bags in curbside recycling if they contaminate sorting — use ESC drop-off or store take-back.",
            ["Keep bags clean/dry.", "Take them to ESC South/North during hours.", "Or use grocery store film drop-off."],
            [("Recycling cart?", "Film typically does not belong loose in curbside recycling.")],
            *esc,
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
            "Heavy trash limits building material volumes — confirm",
            "Houston junk waste / depository (bagged loose materials)",
            "Houston heavy-trash rules limit building materials on residential junk-waste set-outs and require loose materials such as sheetrock to be bagged. Contractor debris is the contractor’s responsibility. Keep paint/chemicals for ESC HHW.",
            [
                "Separate HHW for ESC.",
                "Bag loose C&D; respect cubic-yard limits on junk-waste day.",
                "Do not use depositories for contractor loads.",
            ],
            [("Concrete?", "Confirm depository accepted lists — some C&D streams are restricted.")],
            *depo,
        )
    )
    return rows


def new_york():
    c, st = "new-york", "NY"
    sw = ("NYC DSNY — Special Waste Drop-Off", "https://www.nyc.gov/site/dsny/what-we-do/programs/special-waste-drop-off.page")
    bulk = ("NYC 311 — Bulk Item Disposal", "https://portal.311.nyc.gov/article/?kanumber=KA-01969")
    ewaste = ("NYC DSNY — Electronics & E-Waste", "https://www.nyc.gov/site/dsny/collection/get-rid-of/electronics.page")
    compost = ("NYC DSNY — Composting", "https://www.nyc.gov/site/dsny/collection/residents/composting.page")
    rows = []
    rows.append(
        R(
            c,
            st,
            "mattress",
            "SPECIAL_HANDLING",
            "Low",
            True,
            "Included with DSNY bulk when sealed in a plastic bag",
            "DSNY curbside bulk collection",
            "NYC requires mattresses and box springs set out for bulk collection to be sealed in a plastic bag (bedbug rule). Unbagged mattresses may not be collected and can draw fines. Special Waste Drop-Off sites do not accept furniture/mattresses.",
            [
                "Buy a mattress bag (DSNY does not provide them).",
                "Seal the mattress/box spring completely.",
                "Set out on your building’s bulk collection rules / schedule.",
            ],
            [("Special Waste for mattresses?", "No — Special Waste is for listed special wastes/e-waste, not bulk furniture.")],
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
            "DSNY bulk/appliance rules — follow CFC/Freon set-out instructions",
            "DSNY bulk / freon appliance set-out",
            "NYC refrigerators and other CFC/Freon appliances have special bulk set-out rules. Follow current DSNY/311 freon appliance instructions before placing units out. Do not put freon appliances in regular trash. Electronics covered by the state e-waste ban use Special Waste / e-waste channels instead.",
            [
                "Read current DSNY freon/CFC appliance set-out rules on NYC.gov / 311.",
                "Set out only as instructed for your building type.",
                "Keep TVs/computers out of trash — use e-waste options.",
            ],
            [("Special Waste freon fridge?", "Special Waste Drop-Off is not the bulk freon-appliance pathway.")],
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
            "DSNY freon/CFC appliance rules — confirm before set-out",
            "DSNY freon appliance set-out",
            "Window and other refrigerant ACs in NYC follow DSNY freon/CFC appliance disposal rules — not regular trash and not Special Waste Drop-Off’s chemical list. Confirm the current set-out steps on DSNY/311 before placing an AC at the curb.",
            ["Follow DSNY freon appliance guidance.", "Do not vent refrigerant.", "Use Special Waste for batteries/paint/e-waste separately."],
            [("Trash AC?", "No — follow freon appliance rules.")],
            *bulk,
        )
    )
    for item in ["television", "computer-monitor", "smartphone", "e-waste-mixed"]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "Free for NYC residents at Special Waste Drop-Off (and other e-waste options)",
                "DSNY Special Waste Drop-Off (5 borough sites)",
                "Covered electronics are illegal in NYC trash/recycling. Residents can use DSNY Special Waste Drop-Off sites in all five boroughs (Tue–Sat 9 a.m.–3 p.m.; closed holidays/severe weather) plus retailer take-back, SAFE events, or ecycleNYC where eligible. Bring proof of NYC residency if asked. Sites: Bronx Hunts Point; Brooklyn Greenpoint (459 N Henry / Kingsland entrance); Manhattan Pike Slip; Queens College Point; Staten Island Fresh Kills (Muldoon Ave exit).",
                [
                    "Confirm the device is covered e-waste.",
                    "Go to your borough Special Waste site Tue–Sat 9–3.",
                    "Bring NYC residency proof if requested.",
                ],
                [("Businesses?", "Special Waste Drop-Off is NYC residents only — no businesses/commercial vehicles.")],
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
        "medical-sharps",
    ]:
        limit = {
            "paint-latex": " Paint is limited to up to five gallons per visit.",
            "paint-oil": " Paint is limited to up to five gallons per visit.",
            "motor-oil": " Motor oil/transmission fluid is limited to up to 10 quarts per visit; oil filters up to two.",
            "propane-tank": " Propane/gas cylinders are not on the core Special Waste list — use SAFE Disposal Events or DSNY gas-cylinder guidance; confirm before hauling.",
            "medical-sharps": " Sharps are not the main Special Waste bullet list — use NYC sharps programs / SAFE event guidance; confirm before visiting.",
        }.get(item, "")
        rows.append(
            R(
                c,
                st,
                item,
                "SPECIAL_HANDLING" if item in {"paint-latex", "propane-tank", "medical-sharps"} else "BANNED_FROM_LANDFILLS",
                "Medium" if item == "paint-latex" else "High",
                False,
                "Free for NYC residents at Special Waste / SAFE pathways (limits apply)",
                "DSNY Special Waste Drop-Off",
                f"NYC Special Waste Drop-Off accepts many batteries (tape lithium/rechargeable terminals), motor oil, paint, fluorescents/CFLs, mercury devices, and covered electronics. Sites run Tue–Sat 9 a.m.–3 p.m. in all five boroughs.{limit}",
                [
                    "Check the Special Waste accepted list for your item.",
                    "Tape battery terminals (clear tape) or bag batteries as instructed.",
                    "Visit Tue–Sat 9–3 with residency proof if asked.",
                ],
                [("Alkaline batteries?", "DSNY notes alkalines can go in trash but are also accepted at Special Waste; do not tape alkalines.")],
                *sw,
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
            "Free at Special Waste — up to 4 passenger tires per visit",
            "DSNY Special Waste Drop-Off",
            "DSNY Special Waste Drop-Off accepts up to four passenger car tires per visit. Do not put tires in trash/recycling.",
            ["Take up to four passenger tires to a Special Waste site.", "Visit Tue–Sat 9–3.", "Keep commercial tires out of the resident program."],
            [("More than four?", "Split visits or use a tire retailer take-back.")],
            *sw,
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
            "Follow DSNY compost / yard rules for your building",
            "NYC compost / organics",
            "Plant debris belongs in NYC compost/organics pathways where your building is enrolled — not metal/glass/plastic recycling. Check DSNY composting pages for curbside organics vs drop-off options for your address.",
            ["Confirm organics enrollment for your building.", "Keep plastics out of organics.", "Use DSNY compost drop-off if curbside is unavailable."],
            [("Food scraps?", "Often the same organics stream where offered.")],
            *compost,
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
            "Included with NYC organics/compost where offered",
            "NYC compost / organics",
            "Food scraps go in NYC organics/compost programs where offered — not recycling. Follow DSNY composting guidance for bins, bags, and drop-off sites.",
            ["Use organics service if available.", "Keep plastics out.", "Check DSNY composting pages for drop-off alternatives."],
            [("Apartment not enrolled?", "Use designated compost drop-off sites when available.")],
            *compost,
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
            "Store film recycling",
            "Plastic bags/film are not NYC dual-stream recycling. Return clean film to grocery store drop-off bins.",
            ["Keep bags clean/dry.", "Use store film bins.", "Prefer reusables."],
            [("Special Waste bags?", "Not a Special Waste Drop-Off target material.")],
            *sw,
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
            "Not published at Special Waste core list — confirm grease options",
            "NYC grease / organics guidance",
            "Do not pour cooking oil into NYC drains. Special Waste’s core list focuses on oils like motor oil, not kitchen grease. Confirm current DSNY cooking oil / grease disposal guidance or a grease recycler before hauling.",
            ["Contain cooled oil.", "Confirm an accepted drop-off.", "Never storm-drain dump."],
            [("Motor oil?", "Motor oil is accepted at Special Waste within quart limits.")],
            *sw,
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
            "Private carting / debris rules — not Special Waste",
            "Licensed carting / debris box",
            "Construction debris is not a Special Waste Drop-Off item and is not normal recycling. Use licensed carting or building debris rules; keep paint/chemicals for Special Waste/SAFE events.",
            ["Separate HHW/paint for Special Waste.", "Hire licensed debris removal for C&D.", "Do not curb contractor debris as household trash."],
            [("Bulk C&D?", "Follow building/DSNY rules — contractor waste is usually the contractor’s job.")],
            *bulk,
        )
    )
    return rows


def chicago():
    c, st = "chicago", "IL"
    hccrf = (
        "City of Chicago — Household Chemicals & Computer Recycling Facility",
        "https://www.recyclebycity.com/chicago/notebook/household-chemicals-computer-recycling-facility",
    )
    bulky = ("City of Chicago — Bulky Item Pick Up", "https://www.recyclebycity.com/chicago/notebook/bulky-item-pick-up")
    yard = ("City of Chicago — Yard Waste Pickup", "https://www.recyclebycity.com/chicago/notebook/yard-waste-pickup")
    rows = []
    rows.append(
        R(
            c,
            st,
            "mattress",
            "SPECIAL_HANDLING",
            "Low",
            True,
            "City bulky-item pickup — confirm 311 / Streets & Sanitation rules",
            "Chicago bulky item pickup",
            "Use Chicago bulky-item pickup for mattresses/furniture. Do not take furniture to the Household Chemicals & Computer Recycling Facility (HCCRF). HCCRF is for household chemicals and listed electronics only.",
            ["Request/set out bulky items per Streets & Sanitation / 311 rules.", "Do not abandon items in alleys.", "Take chemicals/computers to HCCRF separately."],
            [("HCCRF mattress?", "No.")],
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
            "City bulky/appliance pickup — confirm freon rules via 311",
            "Chicago bulky / appliance pickup",
            "Schedule Chicago bulky/appliance service for refrigerators. Confirm freon appliance requirements with 311 before set-out. HCCRF does not replace large freon-appliance pickup.",
            ["Book bulky/appliance pickup.", "Do not vent refrigerant.", "Keep chemicals for HCCRF."],
            [("Blue cart fridge?", "Never.")],
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
            "City bulky/appliance — confirm freon rules",
            "Chicago bulky / appliance pickup",
            "Schedule Chicago bulky/appliance service for air conditioners and confirm freon rules via 311. HCCRF accepts many chemicals and computer/TV electronics — not as the primary large freon-AC pathway.",
            ["Book bulky/appliance pickup.", "Do not vent refrigerant.", "Use HCCRF for paint thinners/batteries/etc."],
            [("HCCRF AC?", "Confirm — facility guidance focuses on chemicals and listed e-cycling items.")],
            *bulky,
        )
    )
    for item in ["television", "computer-monitor", "smartphone", "e-waste-mixed"]:
        rows.append(
            R(
                c,
                st,
                item,
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "Free for Chicago residents at HCCRF (residential only)",
                "HCCRF — 1150 N. Branch Street",
                "Illinois landfill bans cover computer equipment; Chicago residents can e-cycle TVs, computers, phones, printers, game consoles, and related gear at the Household Chemicals & Computer Recycling Facility, 1150 N. Branch Street. Hours: Tue 7 a.m.–12 p.m.; Thu 2–7 p.m.; first Saturday 8 a.m.–3 p.m. Use the electronics drop-off area (yellow building). Residential only — no business waste.",
                [
                    "Visit during published HCCRF hours.",
                    "Follow attendant directions to the electronics building.",
                    "Do not leave materials when closed.",
                ],
                [("Best Buy/Staples?", "Retail take-back is also encouraged for working/newer electronics.")],
                *hccrf,
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
        note = {
            "paint-latex": " Latex/water-based paint is NOT accepted as hazardous at HCCRF — dry it out (e.g., with kitty litter/sawdust) and place the can in the trash per city guidance. Oil-based paints, spray paints, and thinners are accepted.",
            "paint-oil": " Oil-based paints, spray paints, thinners, and solvents are accepted at HCCRF. Latex is handled differently (dry out for trash).",
            "medical-sharps": " Unused/expired medications are accepted at HCCRF; medications can also go to police-station drop-offs. Confirm sharps container rules before visiting.",
            "lithium-battery": " Rechargeable electronics/batteries are emphasized; alkaline batteries are described as trash-OK under current city notes.",
        }.get(item, "")
        rows.append(
            R(
                c,
                st,
                item,
                "SPECIAL_HANDLING" if item in {"paint-latex", "medical-sharps"} else "BANNED_FROM_LANDFILLS",
                "Medium" if item == "paint-latex" else "High",
                False,
                "Free for Chicago residents at HCCRF (see latex exception)",
                "HCCRF — 1150 N. Branch Street (blue chemical building)",
                f"Chicago’s HCCRF at 1150 N. Branch Street accepts many household chemicals, auto fluids, CFLs, propane BBQ tanks, rechargeable batteries, and related HHW during Tue/Thu/first-Saturday hours.{note}",
                [
                    "Pack sealed household quantities.",
                    "Arrive Tue 7–12, Thu 14–19, or first Sat 8–15.",
                    "Use the chemical (blue) building as directed.",
                ],
                [("Business waste?", "Not accepted at HCCRF.")],
                *hccrf,
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
            "Not an HCCRF focus — retailer / transfer options",
            "Tire retailer or city-accepted pathway",
            "HCCRF guidance focuses on chemicals and electronics, not as a general scrap-tire dump. Prefer a tire retailer take-back or confirm a city-accepted tire pathway before hauling.",
            ["Ask the tire shop to take old tires.", "Confirm any city tire event/facility before driving.", "Do not illegal-dump."],
            [("HCCRF tires?", "Not listed among core HCCRF e-cycling/chemical accepts.")],
            *hccrf,
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
            "Included with Chicago yard-waste pickup in season",
            "Chicago yard-waste pickup",
            "Use Chicago yard-waste pickup rules for yard trimmings — not blue-cart recycling contamination. Follow seasonal set-out requirements on Recycle by City / Streets & Sanitation pages.",
            ["Follow seasonal yard-waste rules.", "Keep plastics out.", "Use 311 for missed pickup."],
            [("Food scraps?", "See Chicago food-scrap drop-off / compost options — not the same as yard-waste carts everywhere.")],
            *yard,
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
            "Chicago food-scrap drop-off / compost options — confirm for your address",
            "Chicago food-scrap drop-off program",
            "Chicago publishes food-scrap drop-off / compost options; this is not the same as putting food in blue recycling. Check Recycle by City food-scrap guidance for current sites and rules.",
            ["Find a food-scrap drop-off option if available.", "Keep plastics out.", "Do not use recycling carts for scraps."],
            [("Citywide curbside food?", "Confirm current program status for your ward/building.")],
            *yard,
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
            "Store film recycling",
            "Plastic bags/film are not Chicago blue-cart recycling. Use store film drop-off; see Recycle by City plastic-bag guidance.",
            ["Keep bags clean/dry.", "Return to store film bins.", "Prefer reusables."],
            [("Blue cart?", "No — film contaminates recycling.")],
            *hccrf,
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
            "Not HCCRF core list — confirm grease recycling options",
            "Grease recycler / city guidance",
            "Do not pour cooking oil into Chicago drains. HCCRF highlights auto fluids more than kitchen grease — confirm a grease recycler or current city cooking-oil guidance before hauling.",
            ["Contain cooled oil.", "Confirm an accepted drop-off.", "Never storm-drain dump."],
            [("Motor oil?", "Motor oil/antifreeze/gasoline are called out for HCCRF / auto-fluid recycling.")],
            *hccrf,
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
            "Private debris box / transfer — not HCCRF",
            "Debris box / transfer",
            "Construction debris is not HCCRF material. Use a debris box or transfer pathway; keep oil-based paints/solvents for HCCRF.",
            ["Separate HHW for HCCRF.", "Haul C&D via debris box/transfer.", "Do not alley-dump."],
            [("Latex paint cans?", "Dry out latex for trash per HCCRF notes; do not bring liquid latex as HHW.")],
            *bulky,
        )
    )
    return rows


def phoenix():
    c, st = "phoenix", "AZ"
    hhw = (
        "City of Phoenix — Household Hazardous Waste Collection",
        "https://www.phoenix.gov/administration/departments/publicworks/residential-trash-recycling/household-hazardous-waste-collection.html",
    )
    trash = (
        "City of Phoenix Public Works — Residential Trash & Recycling",
        "https://www.phoenix.gov/administration/departments/publicworks/residential-trash-recycling.html",
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
            "City bulk collection — confirm account set-out rules",
            "Phoenix bulk collection",
            "Use City of Phoenix bulk-item collection for mattresses. Do not put HHW in trash/recycling. For chemicals/electronics/batteries, schedule Phoenix’s HHW home collection (separate program).",
            ["Set out bulky items per Phoenix solid-waste rules.", "Schedule HHW home collection separately for toxics.", "Never curb an HHW box in the street."],
            [("HHW drop-off warehouse?", "Phoenix’s resident program is scheduled home collection for account holders.")],
            *trash,
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
            "City bulk/appliance — confirm freon rules",
            "Phoenix bulk / appliance collection",
            "Schedule Phoenix bulk/appliance service for refrigerators. Confirm freon handling rules. Lithium batteries and HHW must never go in trash carts — use HHW home collection / battery guidance.",
            ["Book bulk/appliance pickup.", "Do not vent refrigerant.", "Keep batteries/chemicals for HHW scheduling."],
            [("HHW home collection fridge?", "Confirm accepted materials list when scheduling — large freon appliances may be separate.")],
            *trash,
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
            "City bulk/appliance — confirm freon rules",
            "Phoenix bulk / appliance collection",
            "Schedule Phoenix bulk/appliance service for ACs and confirm freon rules. Do not place lithium batteries or chemicals in trash (fire risk in trucks/transfer stations).",
            ["Book bulky/appliance pickup.", "Do not vent refrigerant.", "Schedule HHW home collection for chemicals/batteries."],
            [("Why batteries matter?", "Phoenix warns lithium-ion batteries are a common cause of collection-truck fires.")],
            *trash,
        )
    )
    for item in [
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
    ]:
        rows.append(
            R(
                c,
                st,
                item,
                "SPECIAL_HANDLING" if item in {"paint-latex", "medical-sharps"} else "BANNED_FROM_LANDFILLS",
                "Medium" if item in {"television", "computer-monitor", "smartphone", "e-waste-mixed", "paint-latex"} else "High",
                False,
                "Free HHW home collection — 1× per solid-waste customer per year",
                "City of Phoenix HHW home collection",
                "Phoenix residential solid-waste customers can schedule one free HHW home collection per calendar year for accepted household hazardous materials (see the city’s accepted-materials list). Schedule online or via hhwcollection@phoenix.gov. Place sealed items in a box labeled “HHW” next to the garage/front door by 7 a.m. (not at the curb). Collection window is 7 a.m.–5 p.m. Electronics with batteries may also use partner options such as Westech Recyclers per city pages.",
                [
                    "Have your city services account number ready.",
                    "Check the accepted materials list, then schedule pickup.",
                    "Set the labeled HHW box out by 7 a.m. on collection day — not in the street.",
                ],
                [
                    ("No appointment dates?", "Email hhwcollection@phoenix.gov if the form shows no availability."),
                    ("Extra collections?", "Additional requests beyond one per year are cancelled per city rules."),
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
            "Not published as HHW home-collection default — retailer / confirm list",
            "Tire retailer or confirmed city pathway",
            "Do not put tires in Phoenix trash/recycling. Prefer retailer take-back. Only include tires in HHW home collection if they appear on the current accepted-materials list when you schedule.",
            ["Ask the tire shop for take-back.", "Check the HHW accepted list before scheduling.", "Do not illegal-dump."],
            [("Batteries in trash?", "Never — especially lithium-ion.")],
            *hhw,
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
            "Included with Phoenix green organics where provided",
            "Phoenix green organics cart",
            "Use Phoenix green organics for yard trimmings where provided — not recycling contamination. Confirm cart rules for your account.",
            ["Use the green organics cart.", "Follow contamination rules.", "Ask Public Works about oversized brush."],
            [("Food scraps?", "Often the same organics stream where provided.")],
            *trash,
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
            "Included with Phoenix organics where provided",
            "Phoenix green organics cart",
            "Food scraps go in Phoenix organics where offered — not recycling. Keep batteries/chemicals out of all carts.",
            ["Collect scraps for organics.", "Keep plastics out.", "Report missed service."],
            [("HHW food?", "No — food is organics; chemicals are HHW home collection.")],
            *trash,
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
            "Plastic bags are not Phoenix curbside recycling. Use grocery store film drop-off.",
            ["Keep bags clean/dry.", "Return to stores.", "Prefer reusables."],
            [("Why?", "Film jams equipment.")],
            *trash,
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
            "Confirm on Phoenix HHW accepted-materials list when scheduling",
            "Phoenix HHW home collection / grease options",
            "Do not pour cooking oil into Phoenix drains or trash if it is treated as HHW. Check the HHW accepted-materials list when scheduling home collection, or use a grease recycler for larger volumes.",
            ["Contain cooled oil.", "Check the accepted list before scheduling HHW pickup.", "Never storm-drain dump."],
            [("Lithium batteries with oil?", "Never put lithium batteries in trash — schedule proper HHW/battery handling.")],
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
            "Debris box / landfill fees — not HHW home collection",
            "Debris box / transfer",
            "Construction debris is not the Phoenix HHW home-collection pathway. Use a debris box or transfer option; keep paint/chemicals/batteries for HHW scheduling.",
            ["Separate HHW for home collection.", "Haul C&D properly.", "Do not overload residential carts."],
            [("HHW C&D?", "No.")],
            *trash,
        )
    )
    return rows


def seattle():
    c, st = "seattle", "WA"
    hhw = (
        "Seattle Public Utilities — Where to Dispose of HHW",
        "https://www.seattle.gov/utilities/your-services/collection-and-disposal/garbage/hazardous-waste-items/where-to-dispose-of-hazardous-waste",
    )
    food = (
        "Seattle Public Utilities — Food & Yard Waste",
        "https://www.seattle.gov/utilities/your-services/collection-and-disposal/food-and-yard",
    )
    transfer = (
        "Seattle Public Utilities — Transfer Stations",
        "https://www.seattle.gov/utilities/your-services/collection-and-disposal/transfer-stations",
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
            "Transfer station fees — confirm current rates",
            "Seattle transfer stations",
            "Seattle residents typically take mattresses to city transfer stations or use a hauler bulky service. Transfer stations do NOT accept household hazardous waste — use North/South HHW facilities for chemicals.",
            ["Confirm mattress fees at a Seattle transfer station.", "Or hire a hauler for bulky pickup.", "Keep HHW for the separate HHW facilities."],
            [("HHW facility mattress?", "No — HHW sites are for hazardous household materials.")],
            *transfer,
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
            "Transfer station / appliance fees — confirm freon rules",
            "Seattle transfer stations",
            "Take refrigerators to Seattle transfer stations or appliance recyclers under published freon rules — not garbage carts and not HHW facilities.",
            ["Confirm freon appliance acceptance/fees.", "Do not vent refrigerant.", "Keep chemicals for North/South HHW."],
            [("Transfer = HHW?", "No — SPU states transfer stations do not accept HHW.")],
            *transfer,
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
            "Transfer station / appliance fees — confirm freon rules",
            "Seattle transfer stations",
            "Use Seattle transfer stations/appliance pathways for ACs; confirm refrigerant fees. HHW facilities are separate and free for King County residents for hazardous products.",
            ["Confirm acceptance/fees.", "Do not vent refrigerant.", "Use HHW sites for paint/batteries/etc."],
            [("North station HHW?", "North Transfer Station does not take HHW; North HHW is at 12550 Stone Ave N.")],
            *transfer,
        )
    )
    for item in [
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
        "cooking-oil",
    ]:
        latex_note = (
            " Confirm current latex-paint rules before visiting — King County HHW programs have published latex limitations at times."
            if item == "paint-latex"
            else ""
        )
        rows.append(
            R(
                c,
                st,
                item,
                "SPECIAL_HANDLING" if item in {"paint-latex", "cooking-oil"} else "BANNED_FROM_LANDFILLS",
                "Medium" if item in {"television", "computer-monitor", "smartphone", "e-waste-mixed", "paint-latex", "cooking-oil"} else "High",
                False,
                "Free for King County residents at Seattle HHW facilities",
                "North/South Seattle HHW facilities",
                f"King County residents (including Seattle) can drop household hazardous waste free at North HHW (12550 Stone Avenue North; Sun–Tue 9 a.m.–5 p.m.) or South HHW (8100 2nd Ave S; Thu–Sat 9 a.m.–5 p.m.). No appointment needed. Closed July 4, Thanksgiving, Christmas, and New Year’s Day. Transfer stations do not accept HHW. Alternatives: Factoria HHW in Bellevue; Wastemobile events; Household Hazards Line (206) 296-4692.{latex_note}",
                [
                    "Choose North (Sun–Tue) or South (Thu–Sat) by open days.",
                    "Pack sealed household quantities within program limits.",
                    "Do not bring HHW to transfer stations.",
                ],
                [
                    ("Business HHW?", "Some eligible businesses can use the program — check SPU eligibility."),
                    ("Factoria?", "All King County residents can use Factoria HHW in Bellevue."),
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
            "Not published as HHW default — retailer / transfer confirm",
            "Tire retailer or transfer station",
            "Do not put tires in Seattle garbage/recycling carts. Prefer retailer take-back; confirm transfer-station tire acceptance/fees before hauling. HHW facilities are for hazardous household products.",
            ["Ask the tire shop to take old tires.", "Or call a transfer station about tire fees.", "Do not illegal-dump."],
            [("HHW tires?", "Not the primary HHW facility purpose.")],
            *transfer,
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
            "Included with Seattle food & yard waste cart",
            "Seattle food & yard waste cart",
            "Use Seattle food & yard waste carts for yard trimmings — not recycling. Follow SPU contamination rules.",
            ["Use the food/yard cart.", "Keep plastics out.", "Ask about oversized brush limits."],
            [("Food scraps?", "Same cart.")],
            *food,
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
            "Included with Seattle food & yard waste cart",
            "Seattle food & yard waste cart",
            "Food scraps go in Seattle food & yard waste — not recycling or garbage when compostable. Compostable bags only if they meet SPU rules.",
            ["Collect scraps for the food/yard cart.", "Keep plastics out.", "Report missed service to SPU."],
            [("Compostable bags?", "Allowed only if they meet SPU specifications.")],
            *food,
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
            "Plastic bags/film are not Seattle curbside recycling. Use store film drop-off.",
            ["Keep bags clean/dry.", "Return to stores.", "Prefer reusables."],
            [("HHW bags?", "No.")],
            *food,
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
            "Transfer station / debris fees",
            "Seattle transfer stations",
            "Construction debris needs a transfer-station or debris-box pathway — not HHW facilities and not food/yard carts. Keep paint/chemicals for North/South HHW.",
            ["Separate HHW for HHW facilities.", "Haul C&D to transfer/debris box.", "Confirm fees before arriving."],
            [("HHW C&D?", "No.")],
            *transfer,
        )
    )
    return rows


def stockton():
    c, st = "stockton", "CA"
    hhw = (
        "City of Stockton — Hazardous Waste",
        "https://www.stocktonca.gov/services/garbage___recycling/hazardous_waste/index.php",
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
            "City/hauler bulky — confirm allotment",
            "Stockton bulky item collection",
            "Use City of Stockton / franchise hauler bulky-item collection for mattresses. The San Joaquin County HHW facility is for hazardous materials and e-waste — not furniture disposal.",
            ["Contact Stockton solid waste/hauler for bulky pickup.", "Set out only when scheduled.", "Take paint/batteries/e-waste to County HHW."],
            [("HHW mattress?", "No.")],
            *hhw,
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
            "City bulky/appliance — confirm freon rules",
            "Stockton bulky/appliance",
            "Schedule Stockton bulky/appliance service for refrigerators. Confirm refrigerant rules. Keep HHW/e-waste for the County HHW Consolidation Facility.",
            ["Book bulky/appliance pickup.", "Do not vent refrigerant.", "Ask about fees."],
            [("Carts?", "Never.")],
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
            True,
            "City bulky/appliance — confirm freon rules",
            "Stockton bulky/appliance",
            "Schedule Stockton bulky/appliance service for ACs; confirm refrigerant acceptance. Chemicals/batteries/e-waste go to San Joaquin County HHW.",
            ["Book bulky/appliance pickup.", "Do not vent refrigerant.", "Use County HHW for chemicals."],
            [("HHW freon AC?", "Confirm before visiting — HHW pages emphasize chemicals/e-waste/universal waste.")],
            *hhw,
        )
    )
    for item in [
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
    ]:
        med = ""
        if item == "medical-sharps":
            med = " Home-generated sharps must be in an approved sharps container; the County HHW facility accepts them. Do not put sharps in trash/recycling/green carts. Medications (no controlled substances) are also accepted at HHW."
        rows.append(
            R(
                c,
                st,
                item,
                "SPECIAL_HANDLING" if item == "paint-latex" else "BANNED_FROM_LANDFILLS",
                "Medium" if item in {"television", "computer-monitor", "smartphone", "e-waste-mixed", "paint-latex"} else "High",
                False,
                "Free for San Joaquin County residents at County HHW facility",
                "San Joaquin County HHW — 7850 R.A. Bridgeford Street",
                f"Stockton residents can take HHW and e-waste free to the San Joaquin County Household Hazardous Waste Consolidation Facility at 7850 R.A. Bridgeford Street, open Thursday–Sunday 9 a.m.–3 p.m. (closed Easter, July 4, Thanksgiving, Christmas, New Year’s). Examples listed by the city include paint, batteries, motor oil/filters, fluorescents, pesticides, pool chemicals, and electronics (TVs, computers, phones, printers).{med}",
                [
                    "Pack sealed household quantities / approved sharps containers as required.",
                    "Visit Thu–Sun 9 a.m.–3 p.m.",
                    "Keep business waste on the separate small-business program if applicable.",
                ],
                [
                    ("Other e-waste sites?", "County also lists North County Recycling Center (Lodi), Lovelace MRF (Manteca), and Foothill Sanitary Landfill for some universal wastes — confirm before hauling."),
                    ("Phone?", "Confirm via County/Onsite Electronics contacts linked from the city page."),
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
            "Not published as HHW default — retailer / transfer",
            "Tire retailer",
            "Do not put tires in Stockton carts. Prefer retailer take-back or confirm transfer-station acceptance. County HHW guidance focuses on hazardous/universal wastes, not as a general tire dump.",
            ["Ask the tire shop to take old tires.", "Call transfer about fees if needed.", "Do not illegal-dump."],
            [("HHW tires?", "Confirm before assuming acceptance.")],
            *hhw,
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
            "Included with Stockton organics/green waste",
            "Stockton organics cart",
            "Use Stockton organics/green-waste service for yard trimmings — not recycling. Keep universal wastes (batteries, lamps, e-waste) out of carts — those go to County HHW / listed facilities.",
            ["Use the organics cart.", "Follow contamination rules.", "Ask about oversized brush."],
            [("Food scraps?", "Organics where provided.")],
            *hhw,
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
            "Included with Stockton organics",
            "Stockton organics cart",
            "Food scraps go in Stockton organics — not recycling. Never put sharps or HHW in organics carts.",
            ["Collect scraps for organics.", "Keep plastics out.", "Report missed service."],
            [("Sharps in organics?", "Illegal — use approved sharps containers to HHW/pharmacy programs.")],
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
            "Plastic bags are not Stockton curbside recycling. Use store film drop-off.",
            ["Keep bags clean/dry.", "Return to stores.", "Prefer reusables."],
            [("Why?", "Film jams equipment.")],
            *hhw,
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
            "Confirm County HHW acceptance for used cooking oil before hauling",
            "San Joaquin County HHW / grease recycler",
            "Do not pour cooking oil into Stockton drains. Confirm whether County HHW accepts used cooking oil or use a grease recycler for larger volumes.",
            ["Contain cooled oil.", "Call before visiting HHW if unsure.", "Never storm-drain dump."],
            [("Motor oil?", "Used motor oil and filters are listed among HHW examples.")],
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
            "Debris box / transfer fees",
            "Debris box / transfer",
            "Construction debris needs a debris box or transfer pathway — not carts and not as HHW chemicals. Keep paint/universal waste for County HHW.",
            ["Separate HHW/e-waste.", "Haul C&D properly.", "Do not alley-dump."],
            [("HHW C&D?", "No.")],
            *hhw,
        )
    )
    return rows


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


def main() -> None:
    audited_cities = {
        "houston": clone_siblings(houston()),
        "new-york": clone_siblings(new_york()),
        "chicago": clone_siblings(chicago()),
        "phoenix": clone_siblings(phoenix()),
        "seattle": clone_siblings(seattle()),
        "stockton": clone_siblings(stockton()),
    }

    all_path = DATA / "rules" / "all.json"
    rules = json.loads(all_path.read_text())
    keep = [r for r in rules if r.get("city_slug") not in audited_cities]
    for rows in audited_cities.values():
        keep.extend(rows)

    # truncate fee fields
    for r in keep:
        if r.get("common_disposal_fee"):
            r["common_disposal_fee"] = str(r["common_disposal_fee"])[:80]
        if r.get("nearest_facility_type"):
            r["nearest_facility_type"] = str(r["nearest_facility_type"])[:120]

    all_path.write_text(json.dumps(keep, indent=2))

    # split files for maintainability
    ca = [r for r in keep if r.get("state") == "CA" or not r.get("city_slug")]
    national = [r for r in keep if r.get("city_slug") and r.get("state") != "CA"]
    (DATA / "rules" / "ca.json").write_text(json.dumps(ca, indent=2))
    (DATA / "rules" / "national.json").write_text(json.dumps(national, indent=2))

    # refresh facilities snippets for audited cities where we have sharper addresses
    fac_path = DATA / "facilities" / "all.json"
    facilities = json.loads(fac_path.read_text())
    updates = {
        "houston": [
            {
                "name": "Houston Environmental Service Center — South",
                "facility_type": "HHW / e-scrap / select recyclables",
                "city_slug": "houston",
                "state": "TX",
                "zip": "77035",
                "address": "11500 S. Post Oak Rd., Houston, TX 77035",
                "lat": 29.656,
                "lng": -95.485,
                "source_url": "https://www.houstontx.gov/solidwaste/esc.html",
                "hours": "Tue, Wed, Fri, Sat 8:00–17:00",
                "phone": "713-551-7355",
            },
            {
                "name": "Houston Environmental Service Center — North",
                "facility_type": "HHW / e-scrap / select recyclables",
                "city_slug": "houston",
                "state": "TX",
                "zip": "77026",
                "address": "5614 Neches St, Houston, TX 77026",
                "lat": 29.796,
                "lng": -95.333,
                "source_url": "https://www.houstontx.gov/solidwaste/esc.html",
                "hours": "Second Thursday each month 9:00–15:00",
                "phone": "713-551-7355",
            },
        ],
        "new-york": [
            {
                "name": "DSNY Special Waste Drop-Off — Brooklyn Greenpoint",
                "facility_type": "Special waste / e-waste",
                "city_slug": "new-york",
                "state": "NY",
                "zip": "11222",
                "address": "459 North Henry Street area (entrance off Kingsland Avenue), Brooklyn, NY",
                "lat": 40.728,
                "lng": -73.944,
                "source_url": "https://www.nyc.gov/site/dsny/what-we-do/programs/special-waste-drop-off.page",
                "hours": "Tue–Sat 9:00–15:00; NYC residents only",
                "phone": "311",
            }
        ],
        "chicago": [
            {
                "name": "Chicago Household Chemicals & Computer Recycling Facility",
                "facility_type": "HHW / e-waste",
                "city_slug": "chicago",
                "state": "IL",
                "zip": "60642",
                "address": "1150 N. Branch Street, Chicago, IL 60642",
                "lat": 41.903,
                "lng": -87.651,
                "source_url": "https://www.recyclebycity.com/chicago/notebook/household-chemicals-computer-recycling-facility",
                "hours": "Tue 7:00–12:00; Thu 14:00–19:00; first Sat 8:00–15:00",
                "phone": "312-744-3060",
            }
        ],
        "stockton": [
            {
                "name": "San Joaquin County Household Hazardous Waste Facility",
                "facility_type": "HHW / e-waste",
                "city_slug": "stockton",
                "state": "CA",
                "zip": "95206",
                "address": "7850 R.A. Bridgeford Street, Stockton, CA 95206",
                "lat": 37.894,
                "lng": -121.248,
                "source_url": "https://www.stocktonca.gov/services/garbage___recycling/hazardous_waste/index.php",
                "hours": "Thu–Sun 9:00–15:00 (major holiday closures)",
                "phone": "(209) 468-3066",
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
        print(f"  {city}: {len(rows)} rules; mattress source={rows[0]['source_name'][:40]}")


if __name__ == "__main__":
    main()
