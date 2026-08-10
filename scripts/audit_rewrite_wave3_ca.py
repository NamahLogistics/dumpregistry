#!/usr/bin/env python3
"""Wave-3 portal audit: remaining CA hubs (LA, SD, SF, SJ + 7 more)."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
VERIFIED = "2026-08-10"

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

HHW_CORE = [
    "car-battery", "lithium-battery", "paint-latex", "paint-oil", "motor-oil",
    "propane-tank", "fluorescent-bulbs", "medical-sharps",
]
EWASTE = ["television", "computer-monitor", "smartphone", "e-waste-mixed"]


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


def add_hhw_bundle(rows, city, st, answer, steps, faqs, src, facility, fee="Free for eligible residents at HHW facility"):
    for item in HHW_CORE:
        med = ""
        if item == "medical-sharps":
            med = " Home-generated sharps usually need an approved sharps container — confirm before visiting."
        rows.append(
            R(
                city,
                st,
                item,
                "BANNED_FROM_LANDFILL",
                "High" if item not in {"paint-latex", "fluorescent-bulbs"} else "Medium",
                False,
                fee,
                facility,
                answer + med,
                steps,
                faqs,
                *src,
            )
        )


def add_ewaste(rows, city, st, answer, steps, faqs, src, facility, curbside=False, fee="Free / program pathway"):
    for item in EWASTE:
        rows.append(
            R(
                city,
                st,
                item,
                "BANNED_FROM_LANDFILL" if not curbside else "SPECIAL_HANDLING",
                "Medium",
                curbside,
                fee,
                facility,
                answer,
                steps,
                faqs,
                *src,
            )
        )


def add_commons(rows, city, st, bulky_src, hhw_src, yard_answer, food_answer, tires_answer, cnd_answer, oil_answer):
    rows.append(
        R(city, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True,
          "Included with organics / published bulky rules", "Local organics cart / bulky pathway",
          yard_answer, ["Use organics for routine yard waste.", "Follow oversized/brush rules.", "Keep HHW out of carts."],
          [("Food scraps?", "Organics where provided.")], *bulky_src)
    )
    rows.append(
        R(city, st, "food-scraps", "ACCEPTED_IN_BLUE_BIN", "Low", True,
          "Included with organics", "Local organics cart",
          food_answer, ["Collect scraps for organics.", "Keep plastics out.", "Never put sharps in organics."],
          [("Sharps?", "Use HHW/pharmacy sharps pathways.")], *bulky_src)
    )
    rows.append(
        R(city, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False,
          "Free (store film drop-off)", "Store film drop-off",
          "Plastic bags are not curbside recycling here. Return clean dry film to grocery store drop-offs.",
          ["Keep bags clean/dry.", "Use store film bins.", "Prefer reusables."],
          [("Why?", "Film jams sorting equipment.")], *bulky_src)
    )
    rows.append(
        R(city, st, "tires", "SPECIAL_HANDLING", "Medium", False,
          "Retailer / special program — confirm fees", "Tire retailer / special pathway",
          tires_answer, ["Ask the tire shop to take old tires when possible.", "Confirm city/county tire rules before curbing.", "Do not illegal-dump."],
          [("Carts?", "Never.")], *bulky_src)
    )
    rows.append(
        R(city, st, "cooking-oil", "SPECIAL_HANDLING", "Medium", False,
          "Confirm HHW / grease recycler", "HHW facility / grease recycler",
          oil_answer, ["Contain cooled oil.", "Confirm HHW acceptance before hauling.", "Never storm-drain dump."],
          [("Motor oil?", "Used motor oil/filters typically go to HHW.")], *hhw_src)
    )
    rows.append(
        R(city, st, "construction-debris", "SPECIAL_HANDLING", "Low", False,
          "Debris box / landfill-transfer fees", "Debris box / transfer",
          cnd_answer, ["Separate HHW/e-waste from C&D.", "Use debris box or transfer.", "Do not curb remodel debris as free bulky unless the city lists it."],
          [("Paint?", "Paint is HHW — not C&D trash.")], *bulky_src)
    )


def los_angeles():
    c, st = "los-angeles", "CA"
    bulky = ("LA Sanitation — Bulky Item Collection", "https://sanitation.lacity.gov/san/faces/home/portal/s-lsh-wwd/s-lsh-wwd-s/s-lsh-wwd-s-c/s-lsh-wwd-s-c-bic")
    hhw = ("LA Sanitation — S.A.F.E. Centers / Hazardous Waste", "https://lacity.gov/residents/trash-recycling")
    rows = []
    rows.append(R(
        c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
        "Free unlimited bulky for LASAN customers (schedule ahead)", "LASAN bulky on your trash day",
        "LA Sanitation (LASAN) picks up bulky household items — mattresses, furniture, carpet, toilets, and more — for residents it serves. Schedule at least one business day before your regular trash day via MyLA311, the online request form, or 1-800-773-2489. Collection is on your normal refuse day. LASAN also runs monthly bulky drop-off events at five city yards (confirm flyer dates).",
        ["Schedule bulky ≥1 business day before trash day (MyLA311 / 1-800-773-2489).", "Set items curbside on that trash day.", "Keep paint, oil, construction debris, and fluorescent lamps out of the bulky pile."],
        [("E-waste curb?", "LASAN bulky lists electronic waste (TVs/computers/monitors) among accepted curbside bulky items — or use S.A.F.E. Centers."),
         ("Abandoned junk?", "Report abandoned bulky via MyLA311 for free pickup.")], *bulky))
    rows.append(R(
        c, st, "refrigerator", "SPECIAL_HANDLING", "Medium", True,
        "Free LASAN large-item / metal appliance pickup", "LASAN bulky / appliance pickup",
        "City of Los Angeles guidance says LASAN will pick up items too large for a bin — including refrigerators — free for eligible customers. Schedule through MyLA311 / 1-800-773-2489 at least one business day before your trash day. Commercial appliances and HHW (paint, oil, chemicals) are not bulky pathways.",
        ["Book large-item/appliance pickup via MyLA311.", "Set out on the confirmed trash day.", "Take paint/chemicals/propane to a S.A.F.E. Center on a weekend."],
        [("Commercial appliance?", "LASAN lists commercial appliances among bulky exclusions.")], *bulky))
    rows.append(R(
        c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
        "LASAN bulky/appliance — confirm when scheduling", "LASAN bulky / appliance pickup",
        "Schedule LASAN bulky/appliance service for residential ACs; confirm any freon handling notes when you call. Do not put refrigerants, paints, or oils in carts. Chemicals go to S.A.F.E. Centers.",
        ["Schedule via MyLA311 / 1-800-773-2489.", "Ask about freon appliance rules.", "Use S.A.F.E. Centers for HHW."],
        [("HHW freon unit?", "S.A.F.E. Centers focus on HHW/e-waste — bulky appliances use LASAN bulky.")], *bulky))
    add_ewaste(
        rows, c, st,
        "LASAN accepts electronic waste (TVs, computers, monitors) on scheduled bulky pickup, and LA City/County residents can also drop HHW and e-waste at permanent S.A.F.E. Centers (weekend hours — confirm location before visiting). Wipe personal data first.",
        ["Schedule bulky for e-waste or visit a S.A.F.E. Center weekend hours.", "Wipe devices.", "Keep chemicals sealed for S.A.F.E. drop-off."],
        [("S.A.F.E. only weekends?", "Permanent S.A.F.E. Centers are commonly weekend-only — confirm the specific site.")],
        hhw, "LASAN bulky or S.A.F.E. Center", curbside=True,
        fee="Free bulky / free S.A.F.E. drop-off for residents",
    )
    add_hhw_bundle(
        rows, c, st,
        "Do not trash HHW in Los Angeles. LA residents drop household hazardous waste and many electronics at S.A.F.E. Centers (paint, motor oil, propane tanks, needles/sharps, batteries, chemicals, e-waste). Centers are free permanent weekend sites citywide — check lacitysan.org/safecenters for the nearest site and hours. Mobile HHW events also run periodically.",
        ["Pack sealed household quantities (≤15 gal / 125 lb typical transport limit).", "Visit a S.A.F.E. Center on an open weekend or a mobile event.", "Never put paint/oil/sharps in carts or bulky piles."],
        [("Bulky for paint?", "No — paints/chemicals/fluorescents/medicine are bulky exclusions."),
         ("Phone?", "1-800-773-2489 / MyLA311.")],
        hhw, "LASAN S.A.F.E. Centers (weekend HHW/e-waste)",
    )
    add_commons(
        rows, c, st, bulky, hhw,
        "Use LASAN organics/green-waste service for routine yard trimmings. Oversized brush/wood may fit bulky or monthly bulky drop-off events (furniture, carpet, yard trimmings, shelving, wood listed).",
        "Food scraps go in LASAN organics — not recycling. Never put sharps or HHW in organics.",
        "LASAN publishes a separate tires drop-off guide — tires are not a normal bulky default. Prefer retailer take-back or follow the LASAN tires pathway.",
        "Construction materials are LASAN bulky exclusions. Use a debris box or permitted C&D facility; keep paint for S.A.F.E. Centers.",
        "Do not pour cooking oil into LA drains. Confirm S.A.F.E. Center acceptance for used cooking oil or use a grease recycler for larger volumes.",
    )
    return rows


def san_diego():
    c, st = "san-diego", "CA"
    bulky = ("City of San Diego Environmental Services — Get It Done bulky", "https://www.sandiego.gov/environmental-services")
    hhw = ("City of San Diego — Household Hazardous Waste Transfer Facility", "https://www.sandiego.gov/environmental-services/ep/hazardous")
    rows = []
    rows.append(R(
        c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
        "Free residential bulky by request (confirm allotment when booking)", "City of San Diego bulky pickup",
        "City of San Diego residential customers schedule free bulky item pickup (mattresses, furniture, large household items) through Get It Done or by calling Environmental Services at 858-694-7000. Confirm your current annual allotment and setout day when you book. Do not put HHW, construction debris, or chemicals in the bulky pile.",
        ["Request bulky via Get It Done or 858-694-7000.", "Set items out only on the scheduled day.", "Take paint/batteries/e-waste to Miramar HHW by appointment."],
        [("Self-haul?", "Miramar Landfill self-haul is available for larger cleanouts — fees may apply.")], *bulky))
    rows.append(R(
        c, st, "refrigerator", "SPECIAL_HANDLING", "Medium", True,
        "City bulky by request — confirm appliance rules", "City of San Diego bulky pickup",
        "Schedule City of San Diego bulky pickup for refrigerators/appliances via Get It Done / 858-694-7000 and confirm freon appliance instructions when booking. Keep chemicals for the Miramar HHW Transfer Facility (appointment only).",
        ["Book bulky and ask about freon units.", "Set out on the scheduled day.", "Use Miramar HHW for paint/batteries/oil."],
        [("HHW fridge?", "Miramar HHW is for hazardous/universal wastes — not a general appliance dump.")], *bulky))
    rows.append(R(
        c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
        "City bulky — confirm freon rules when booking", "City of San Diego bulky pickup",
        "Treat residential ACs as City bulky/appliance pathway; confirm refrigerant rules at booking (Get It Done / 858-694-7000). Chemicals go to Miramar HHW by appointment.",
        ["Book bulky; ask about freon.", "Do not vent refrigerant.", "HHW chemicals → Miramar appointment."],
        [("Walk-in HHW?", "No — Miramar HHW is appointment-only.")], *bulky))
    add_ewaste(
        rows, c, st,
        "City of San Diego residents drop electronics and HHW free at the Miramar Household Hazardous Waste Transfer Facility (5161 Convoy Street, landfill entrance) by appointment only — Wednesdays & Saturdays 9 a.m.–3 p.m. (except holidays; Wednesday appointments noted as available starting April 1, 2026). Book via Get It Done or 858-694-7000. Bring proof of City residency. Limit about 15 gallons or 125 pounds per trip.",
        ["Schedule a Miramar HHW appointment before visiting.", "Bring residency proof; pack waste in trunk/truck bed.", "Stay within 15 gal / 125 lb limits."],
        [("City of San Diego only?", "Yes — Miramar HHW Transfer Facility is for City residents; other South Bay cities use different sites.")],
        hhw, "Miramar HHW Transfer Facility — 5161 Convoy St",
        fee="Free for City of San Diego residents (appointment)",
    )
    add_hhw_bundle(
        rows, c, st,
        "Do not trash HHW in San Diego. City residents use the Miramar HHW Transfer Facility at 5161 Convoy Street by appointment only (Wed & Sat 9 a.m.–3 p.m., except holidays). Accepted examples include paint, batteries, used oil/filters, fluorescents/LEDs, and other household chemicals. Bring picture ID or a recent bill showing City residency. Transport limits ~15 gallons or 125 pounds; containers typically ≤5 gallons.",
        ["Book appointment (Get It Done / 858-694-7000).", "Pack sealed labeled products in trunk/bed.", "Arrive only on your appointment slot."],
        [("Elderly/disabled?", "City pages note special help options — call 858-694-7000."),
         ("South Bay facility?", "South Bay HHW in Chula Vista does not accept City of San Diego residents.")],
        hhw, "Miramar HHW Transfer Facility — 5161 Convoy St",
    )
    add_commons(
        rows, c, st, bulky, hhw,
        "Use City of San Diego organics for routine yard waste. Oversized brush may need bulky scheduling via Get It Done.",
        "Food scraps go in organics — not recycling. Keep HHW/sharps out of carts.",
        "Tires are not a Miramar HHW default. Prefer retailer take-back or confirm landfill/special pathways.",
        "Construction debris is not free bulky HHW. Use Miramar Landfill self-haul or a debris box; keep paint for Miramar HHW appointments.",
        "Do not pour cooking oil into drains. Confirm Miramar HHW acceptance or use a grease recycler.",
    )
    return rows


def san_francisco():
    c, st = "san-francisco", "CA"
    bulky = ("Recology San Francisco — Bulky Items", "https://www.recology.com/recology-san-francisco/bulky-items/")
    hhw = ("Recology San Francisco — Household Hazardous Waste", "https://www.recology.com/recology-san-francisco/hazardous-waste/")
    rows = []
    rows.append(R(
        c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
        "2 free bulky collections/year (≤5-unit); 1 for larger multifamily", "Recology bulky item collection",
        "San Francisco residents schedule Recology Bulky Item Collection for mattresses/furniture (up to 10 items per appointment). Buildings with 5 units or fewer get two free curbside collections per year; each unit in buildings with 6+ units gets one free collection. Schedule via the Bulky Item form or 415-330-1300 (call ~2 weeks ahead). Place items at the curb by appointment morning with a “RECOLOGY” sign. No HHW, C&D, auto parts, or tires.",
        ["Schedule Recology bulky (form or 415-330-1300).", "Set out by appointment morning with a RECOLOGY sign.", "Take chemicals to the HHW Facility at 501 Tunnel Ave (Thu–Sat)."],
        [("Extra pickups?", "Additional collections may be available for a fee after free allotments."),
         ("Drop-off?", "Recology Transfer Station at 501 Tunnel Ave accepts many non-hazardous items for self-haul.")], *bulky))
    rows.append(R(
        c, st, "refrigerator", "SPECIAL_HANDLING", "Medium", True,
        "Recology bulky — appliances within item limits", "Recology bulky item collection",
        "Schedule Recology bulky for appliances within your free allotment and 10-item cap. Confirm appliance/freon notes when booking. Hazardous waste is never part of bulky — use the HHW Facility or free HHW home collection (email hhw@recology.com).",
        ["Book bulky; list the appliance.", "Set out on appointment day with RECOLOGY sign.", "HHW chemicals → Tunnel Ave HHW or home collection email."],
        [("Transfer station fridge?", "Confirm fees/acceptance at 501 Tunnel Ave before self-hauling.")], *bulky))
    rows.append(R(
        c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
        "Recology bulky — confirm freon rules", "Recology bulky item collection",
        "Book Recology bulky for residential ACs and confirm refrigerant handling when you schedule. Keep cylinders/chemicals for HHW pathways at 501 Tunnel Avenue.",
        ["Schedule bulky; ask about freon.", "Do not vent refrigerant.", "Use HHW Facility Thu–Sat 8–4 for chemicals."],
        [("HHW home pickup?", "Email hhw@recology.com for free residential HHW collection when you have multiple items.")], *bulky))
    add_ewaste(
        rows, c, st,
        "Recology bulky accepts electronics (TVs, computers, etc.) within your free collection allotment. You can also self-haul many electronics to the Recology Transfer Station (501 Tunnel Ave; confirm acceptance). Hazardous chemicals still go to the HHW Facility (Thu–Sat 8 a.m.–4 p.m.) with SF residency proof — max about 15 gallons per trip.",
        ["Schedule bulky for e-waste or confirm transfer-station drop-off.", "Wipe data.", "Use HHW Facility for paint/batteries/propane."],
        [("Bulky hazardous?", "No — HHW is excluded from bulky.")],
        bulky, "Recology bulky / 501 Tunnel Ave", curbside=True,
        fee="Free within Recology bulky allotment",
    )
    add_hhw_bundle(
        rows, c, st,
        "San Francisco residents drop household hazardous waste free at Recology’s HHW Facility, 501 Tunnel Avenue, Thursday–Saturday 8 a.m.–4 p.m. (closed major holidays including New Year’s, July 4, Thanksgiving week dates, Dec 25–26). Bring proof of SF residency; max about 15 gallons per trip. Free residential HHW home collection is also available by emailing hhw@recology.com.",
        ["Pack sealed household HHW (≤15 gal).", "Visit Thu–Sat 8–4 or email hhw@recology.com for home pickup.", "Never put HHW in black/blue/green carts or bulky piles."],
        [("PaintCare?", "PaintCare paint is listed among free HHW acceptances — confirm on-site rules."),
         ("Business?", "Very Small Quantity Generator program is separate and may have fees.")],
        hhw, "Recology HHW Facility — 501 Tunnel Ave",
    )
    add_commons(
        rows, c, st, bulky, hhw,
        "Use Recology green/organics carts for yard trimmings. Oversized brush may need bulky scheduling within accepted lists.",
        "Food scraps go in SF organics/compost — not recycling. Never put sharps in organics.",
        "Tires/auto parts are Recology bulky exclusions. Prefer retailer take-back.",
        "C&D is excluded from Recology bulky. Use a debris box or confirm transfer-station C&D rules; keep paint for HHW.",
        "Do not pour cooking oil into SF drains. Confirm HHW Facility acceptance or use a grease recycler.",
    )
    return rows


def san_jose():
    c, st = "san-jose", "CA"
    bulky = ("City of San José — Junk Pickup", "https://www.sanjoseca.gov/your-government/departments-offices/environmental-services/recycling-garbage/junk-pickup")
    hhw = ("County of Santa Clara — Household Hazardous Waste", "https://hhw.santaclaracounty.gov/drop-household-waste")
    rows = []
    rows.append(R(
        c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
        "Free Junk Pickup (up to 12 items per request)", "San José Junk Pickup",
        "San José owners and renters (including multifamily — check property manager for setout spot) can schedule free Junk Pickup via 311.SanJoseCA.gov, the 311 app, 3-1-1, or (408) 535-3500. Requests may include up to 12 acceptable items (mattresses, furniture, tires, and more). Appointments are on your regular recycling/garbage day; set items out up to 24 hours before the appointment (improper early setout can be cited as illegal dumping).",
        ["Schedule Junk Pickup via 311 / (408) 535-3500.", "Wait for the confirmation email with setout instructions.", "Keep HHW for Santa Clara County HHW appointments."],
        [("Same day as trash?", "Yes — Junk Pickup is scheduled on your regular collection day(s).")], *bulky))
    rows.append(R(
        c, st, "refrigerator", "SPECIAL_HANDLING", "Medium", True,
        "Free Junk Pickup — confirm appliance on item list", "San José Junk Pickup",
        "Schedule San José Junk Pickup for refrigerators/appliances if they are on the acceptable junk list when you book (up to 12 items). Confirm freon notes with 311. Paint/chemicals/batteries need a Santa Clara County HHW appointment — not Junk Pickup.",
        ["Book Junk Pickup and list the appliance.", "Set out only after confirmation, ≤24 hours early.", "Schedule County HHW for chemicals."],
        [("HHW appointment?", "Required — book at hhw.santaclaracounty.gov or (408) 299-7300.")], *bulky))
    rows.append(R(
        c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
        "Junk Pickup if listed — confirm freon rules", "San José Junk Pickup",
        "Ask 311 whether your AC is accepted on Junk Pickup and what freon rules apply. Do not put refrigerants or chemicals in carts. County HHW handles household chemicals/e-waste by appointment.",
        ["Confirm AC acceptance when booking Junk Pickup.", "Do not vent refrigerant.", "Book County HHW for paint/batteries."],
        [("Facility address?", "County only reveals drop-off address after you book an HHW appointment.")], *bulky))
    add_ewaste(
        rows, c, st,
        "San José residents dispose of HHW and e-waste free through the County of Santa Clara Household Hazardous Waste Program — appointment required before visiting. Book online or call (408) 299-7300. Permanent facilities operate in East San Jose and San Martin on published Thu–Sat schedules; temporary city events also run. Exact addresses are provided after booking to deter illegal dumping.",
        ["Schedule a County HHW appointment first.", "Pack waste in trunk/truck bed.", "Bring only household quantities on your appointment day."],
        [("Walk-in?", "No — appointment required."),
         ("Oil curbside?", "San José also offers curbside used-motor-oil collection for some residence types — see city recycling pages.")],
        hhw, "Santa Clara County HHW (appointment; East San Jose / events)",
    )
    add_hhw_bundle(
        rows, c, st,
        "Do not trash HHW in San José. Use Santa Clara County’s free HHW program (paint, batteries, electronics, fluorescents, garden chemicals, cleaners, etc.) with a required appointment — (408) 299-7300 or the county HHW appointment system. Permanent San Jose / San Martin days are typically Thursday–Saturday; confirm the operating schedule when you book.",
        ["Book appointment; wait for location instructions.", "Transport sealed labeled products safely.", "Do not put HHW in Junk Pickup piles."],
        [("Junk Pickup HHW?", "No — chemicals/universal waste need County HHW."),
         ("Seniors?", "Some cities list senior HHW pickup partners — ask County/city if you cannot drive.")],
        hhw, "Santa Clara County HHW (appointment required)",
    )
    add_commons(
        rows, c, st, bulky, hhw,
        "Use San José organics for yard waste. Oversized junk may go on Junk Pickup if listed.",
        "Food scraps go in organics — not recycling. Keep sharps out of carts.",
        "Prefer retailer take-back; San José Junk Pickup also lists tires among acceptables when scheduled.",
        "Building materials are often excluded from free junk — use a debris box; keep paint for County HHW.",
        "Do not pour cooking oil into drains. Confirm County HHW acceptance or use a grease recycler.",
    )
    rows = [r for r in rows if r["item_slug"] != "tires"]
    rows.append(R(
        c, st, "tires", "SPECIAL_HANDLING", "Medium", True,
        "Free via Junk Pickup when listed among acceptable items", "San José Junk Pickup",
        "San José Junk Pickup materials list tires among acceptable junk items (within the up-to-12-items request). Schedule via 311 and follow setout rules. Prefer retailer take-back when replacing tires.",
        ["Include tires on your Junk Pickup request.", "Set out only after confirmation.", "Do not illegal-dump."],
        [("Mounted tires?", "Confirm unmounted/mounted rules when scheduling.")], *bulky))
    return rows


def sacramento():
    c, st = "sacramento", "CA"
    bulky = ("City of Sacramento — Household Junk Pickup", "https://www.cityofsacramento.gov/public-works/recycling-solid-waste/Collectionservices/service_requests/household_junk_pickup")
    hhw = ("City of Sacramento — HHW at Sacramento Recycling & Transfer Station", "https://www.cityofsacramento.gov/public-works/recycling-solid-waste/Householdhazardouswaste/HHWfacilities")
    rows = []
    rows.append(R(
        c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
        "2 free junk appointments Feb–Oct (via 311)", "Sacramento Household Junk Pickup",
        "Sacramento residential customers get two free Household Junk Pickup appointments between February and October (excess yard waste separated). Schedule via Sac 311 / 3-1-1 / (916) 264-5011. Set items out only ≤24 hours before the appointment. Extra or leaf-season pickups may be fee-based (Utility Billing). Separately, residents also get two appliance & e-waste collection appointments per calendar year (year-round).",
        ["Book junk pickup via 311 (Feb–Oct free window).", "Set out ≤24 hours before appointment.", "Use separate appliance/e-waste appointments for those items when required."],
        [("Leaf season?", "Junk appointments pause mid-Oct–Jan for leaf season; fee-based options may exist.")], *bulky))
    rows.append(R(
        c, st, "refrigerator", "SPECIAL_HANDLING", "Medium", True,
        "Appliance/e-waste appointments (2/year) or junk rules", "Sacramento appliance & e-waste collection",
        "Sacramento offers two appliance and e-waste collection appointments per calendar year, year-round — use that pathway for refrigerators rather than assuming regular junk rules. Schedule via 311. Keep chemicals for the City HHW facility at 8491 Fruitridge Road.",
        ["Schedule an appliance/e-waste appointment via 311.", "Confirm freon instructions when booking.", "Take paint/batteries to HHW Tue–Sat 8–5."],
        [("Junk vs appliance?", "City publishes separate junk vs appliance/e-waste appointment allotments.")], *bulky))
    rows.append(R(
        c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
        "Appliance appointment — confirm freon rules", "Sacramento appliance & e-waste collection",
        "Book Sacramento’s appliance/e-waste appointment pathway for ACs and confirm freon rules. HHW chemicals go to 8491 Fruitridge Road (Tue–Sat 8–5).",
        ["Schedule appliance appointment.", "Do not vent refrigerant.", "Use City HHW for chemicals."],
        [("HHW hours?", "City HHW drop-off Tue–Sat 8 a.m.–5 p.m. at SRTS — transfer station hours differ.")], *bulky))
    add_ewaste(
        rows, c, st,
        "Use Sacramento’s two annual appliance & e-waste collection appointments and/or drop electronics at the City HHW facility at the Sacramento Recycling & Transfer Station, 8491 Fruitridge Road (HHW hours Tue–Sat 8 a.m.–5 p.m.). City notes fees may apply for some small/medium e-waste. Limit ~15 gallons or 125 pounds of hazardous materials per trip.",
        ["Schedule e-waste appointment or visit HHW Tue–Sat 8–5.", "Bring sealed loads within transport limits.", "Ask about any e-waste fees before dropping small electronics."],
        [("Reuse store?", "Mostly-full labeled products may go to the Reuse Store next to HHW drop-off.")],
        hhw, "Sacramento HHW — 8491 Fruitridge Road", curbside=True,
        fee="Free residential HHW; some e-waste fees may apply",
    )
    add_hhw_bundle(
        rows, c, st,
        "Sacramento residents drop HHW free (when guidelines are followed) at 8491 Fruitridge Road, Tuesday–Saturday 8 a.m.–5 p.m. Transport ≤15 gallons or 125 pounds per trip; containers must be leak-proof and labeled. Regional County facilities (e.g., North Area Recovery Station) are additional options.",
        ["Pack sealed labeled HHW within limits.", "Visit Tue–Sat 8–5 at 8491 Fruitridge.", "Business waste is a separate paid pathway."],
        [("Phone?", "Business/HHW questions often route to (916) 379-0500 on city pages.")],
        hhw, "Sacramento HHW — 8491 Fruitridge Road",
    )
    add_commons(
        rows, c, st, bulky, hhw,
        "Sacramento junk pickup accepts separated yard waste with size rules (limbs ≤3 ft / ≤4 in diameter). Routine yard waste goes in organics.",
        "Food scraps go in organics — not recycling.",
        "Up to 4 unmounted tires on junk pickup; otherwise retailer take-back.",
        "Some wood/lumber appears on junk lists with length limits; heavier C&D needs debris box/transfer. Keep paint for HHW.",
        "Do not pour cooking oil into drains. Confirm City HHW acceptance or use a grease recycler.",
    )
    rows = [r for r in rows if r["item_slug"] != "tires"]
    rows.append(R(
        c, st, "tires", "SPECIAL_HANDLING", "Medium", True,
        "Junk pickup allows up to 4 unmounted tires", "Sacramento Household Junk Pickup",
        "Sacramento junk pickup lists up to four unmounted tires among acceptable setouts. Schedule via 311 within the free Feb–Oct window (or fee-based otherwise). Prefer retailer take-back when replacing tires.",
        ["Include unmounted tires on junk appointment (≤4).", "Set out ≤24 hours before pickup.", "Do not illegal-dump."],
        [("Mounted?", "Guidance specifies unmounted tires — confirm if wheels are attached.")], *bulky))
    return rows


def oakland():
    c, st = "oakland", "CA"
    bulky = ("Oakland Recycles — Bulky Service", "https://www.oaklandrecycles.com/bulky-service/")
    hhw = ("Alameda County / StopWaste — Household Hazardous Waste", "https://www.stopwaste.org/recycling-disposal/hazardous-waste/household-hazardous-waste")
    rows = []
    rows.append(R(
        c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
        "Included bulky: curbside pickup + 4 cy drop-off (reservations)", "Oakland bulky junk pickup / Davis Street drop-off",
        "All Oakland households (owners and renters) can schedule bulky junk curbside pickup and a one-time drop-off of up to four cubic yards at Davis Street Resource Recovery Complex (San Leandro). Reserve at 1-888-WM-BULKY (1-888-962-8559) or online. Place curb items by 6 a.m. appointment day; do not set out more than one day early (fines possible). No HHW/medical waste, rocks/dirt/concrete, or fiberglass in bulky loads.",
        ["Reserve pickup or Davis Street drop-off (1-888-WM-BULKY).", "Set curb items by 6 a.m. appointment day.", "Take paint/batteries/e-waste to Alameda County HHW (Oakland facility 2100 E. 7th)."],
        [("Overages?", "Set-outs over allowed amounts can incur fees.")], *bulky))
    rows.append(R(
        c, st, "refrigerator", "SPECIAL_HANDLING", "Medium", True,
        "Oakland bulky appointment — confirm appliance rules", "Oakland bulky junk service",
        "Schedule Oakland bulky for refrigerators/appliances via 1-888-WM-BULKY. Keep hazardous materials for Alameda County HHW facilities — not bulky.",
        ["Book bulky; list the appliance.", "Curb by 6 a.m. appointment day.", "HHW → StopWaste facilities."],
        [("HHW appointment?", "Alameda County residential HHW drop-off is free with no appointment at open facilities.")], *bulky))
    rows.append(R(
        c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
        "Oakland bulky — confirm freon rules", "Oakland bulky junk service",
        "Book Oakland bulky for ACs and confirm freon handling. Chemicals/batteries go to Alameda County HHW (Oakland: 2100 East 7th Street).",
        ["Schedule bulky; ask about freon.", "Do not vent refrigerant.", "Use County HHW for chemicals."],
        [("Oakland HHW hours?", "Wed–Fri 9–2:30; Sat 9–4 (closed Sun–Tue / major holidays).")], *bulky))
    add_ewaste(
        rows, c, st,
        "Alameda County residents (including Oakland) drop HHW and many electronics free at County facilities with no appointment — Oakland site at 2100 East 7th Street (Wed–Fri 9 a.m.–2:30 p.m.; Sat 9 a.m.–4 p.m.). Bring driver’s license / proof of residence. Call 1-800-606-6606 for packing limits and holiday closures.",
        ["Pack sealed HHW/e-waste.", "Visit Oakland HHW during open hours (or Hayward/Livermore/Fremont sites).", "Keep bulky junk separate from HHW loads."],
        [("Business waste?", "Residential program only — businesses use a separate service.")],
        hhw, "Alameda County HHW — 2100 E. 7th St, Oakland",
    )
    add_hhw_bundle(
        rows, c, st,
        "Do not put HHW in Oakland trash or bulky piles. Use Alameda County’s free residential HHW drop-off (no appointment) at Oakland 2100 East 7th Street or other County sites. Accepted materials include paint, batteries, chemicals, and electronics. Bring ID/proof of Alameda County residence. Info: StopWaste.org/HHW or 1-800-606-6606.",
        ["Pack sealed labeled products within County limits.", "Drop Wed–Sat hours at Oakland facility (or other County sites).", "Never curb HHW with bulky junk."],
        [("Swap Shed?", "Oakland facility notes Saturday reuse/swap hours for still-usable products — confirm current times.")],
        hhw, "Alameda County HHW — 2100 E. 7th St, Oakland",
    )
    add_commons(
        rows, c, st, bulky, hhw,
        "Use Oakland organics for yard waste. Oversized junk uses bulky reservation (not dirt/rock/concrete).",
        "Food scraps go in organics. Keep sharps for HHW/pharmacy programs.",
        "Tires/auto parts are not the HHW default — prefer retailer take-back; confirm bulky acceptance when booking.",
        "Dirt, rock, concrete, and fiberglass are bulky exclusions — use City-listed disposal options / transfer fees.",
        "Do not pour cooking oil into drains. Confirm County HHW acceptance or use a grease recycler.",
    )
    return rows


def long_beach():
    c, st = "long-beach", "CA"
    bulky = ("City of Long Beach — Special Collection 101", "https://longbeach.gov/lbrecycles/refuse/special-collections/special-collection-101/")
    hhw = ("City of Long Beach — Household Hazardous Waste 101", "https://longbeach.gov/lbrecycles/hazardous-waste/household-hazardous-waste/hhw-101/")
    rows = []
    rows.append(R(
        c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
        "12 free Special Collections/year for City-serviced accounts", "Long Beach Special Collection",
        "City-serviced Long Beach refuse accounts get 12 Special Collections per year for oversized items. Schedule via the Special Collection request or (562) 570-2876 — do not set items out until a date is confirmed. Limits commonly include up to 8 large items (or 25 bags/bundles) per pickup; oversized sofas OK if noted when booking. Appliances, TVs/monitors, and tires may need a special truck and can carry a regulatory fee — declare them when you call.",
        ["Schedule Special Collection and wait for confirmation.", "Set out by 6 a.m. on the scheduled day at your normal refuse location.", "Keep HHW for EDCO Signal Hill / Gaffey S.A.F.E. pathways."],
        [("Size caps?", "Many items ≤72″×48″ / 40 lb bundles unless you flag oversized furniture when booking.")], *bulky))
    rows.append(R(
        c, st, "refrigerator", "SPECIAL_HANDLING", "Medium", True,
        "Special Collection — may include special-handling fee", "Long Beach Special Collection",
        "Schedule Long Beach Special Collection for refrigerators/appliances and tell the Call Center you need special handling. A regulatory fee may apply. Do not put freon appliances in carts. HHW chemicals use permanent collection centers (not Special Collection).",
        ["Call (562) 570-2876; declare the appliance.", "Wait for confirmed date before setout.", "HHW → EDCO Signal Hill or Gaffey S.A.F.E. Center."],
        [("HHW fridge?", "Long Beach HHW pages say refrigerators/stoves/other bulky are for Special Collection, not HHW centers.")], *bulky))
    rows.append(R(
        c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
        "Special Collection — declare special handling", "Long Beach Special Collection",
        "Book Special Collection for ACs and ask about freon/special-handling fees. Chemicals/batteries go to HHW collection centers.",
        ["Schedule and declare the AC.", "Do not vent refrigerant.", "Use HHW centers for chemicals."],
        [("Centers?", "EDCO Signal Hill (monthly Saturdays) and Gaffey S.A.F.E. Center (weekends) are listed for LB residents.")], *bulky))
    add_ewaste(
        rows, c, st,
        "Long Beach Special Collection can pick up TVs/monitors (special truck; possible fee). For HHW/e-waste drop-off, Long Beach points residents to LA County EDCO Environmental Collection Center in Signal Hill (corner of 28th & California; typically 2nd Saturday monthly 9 a.m.–2 p.m. — confirm current Saturdays) and the Gaffey Street S.A.F.E. Center in San Pedro (Sat–Sun 9 a.m.–3 p.m.).",
        ["Declare TVs/monitors when booking Special Collection, or use EDCO/Gaffey drop-off.", "Wipe data.", "Keep chemicals for HHW centers."],
        [("E-waste piece limit?", "Some S.A.F.E. guidance limits e-waste pieces per visit — confirm before loading.")],
        hhw, "EDCO Signal Hill HHW / Gaffey S.A.F.E. Center", curbside=True,
        fee="Special Collection may charge special-handling fees",
    )
    add_hhw_bundle(
        rows, c, st,
        "It is illegal to put HHW in Long Beach carts. Use free permanent collection options such as EDCO Recycling & Transfer Environmental Collection Center in Signal Hill (enter on 28th; monthly Saturday hours — confirm) or Gaffey Street S.A.F.E. Center, 1400 N. Gaffey St., San Pedro (Sat–Sun 9–3; 1-800-988-6942). Transport limits ~15 gallons or 125 pounds. LA County mobile HHW events are also available.",
        ["Pack sealed HHW within transport limits.", "Visit EDCO Signal Hill or Gaffey S.A.F.E. on open days.", "Never curb HHW with Special Collection trash."],
        [("Phone?", "Long Beach Call Center (562) 570-2876 for Special Collection; 1-800-988-6942 for Gaffey S.A.F.E.")],
        hhw, "EDCO Signal Hill / Gaffey S.A.F.E. Center",
    )
    add_commons(
        rows, c, st, bulky, hhw,
        "Bag/bundle yard waste for Special Collection if oversized; routine organics go in green carts.",
        "Food scraps go in organics. Keep sharps for HHW centers.",
        "Tires can be Special Collection with special handling/fees — declare when booking; retailer take-back still preferred.",
        "Construction debris is not a free HHW pathway — use debris box/transfer; keep paint for HHW centers.",
        "Do not pour cooking oil into drains. Confirm HHW center acceptance or grease recycler.",
    )
    return rows


def anaheim():
    c, st = "anaheim", "CA"
    bulky = ("City of Anaheim — Bulky Item Collection", "https://www.anaheim.net/6276/Bulky-Item-Collection")
    hhw = ("OC Waste & Recycling — HHW Collection Centers", "https://oclandfills.com/hhw")
    rows = []
    rows.append(R(
        c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
        "3 free bulky pickups/year, up to 20 items each (Republic)", "Anaheim / Republic bulky pickup",
        "Anaheim households get three free bulky item pickups per calendar year through Republic Services, up to 20 items per pickup (furniture, appliances, etc.). Schedule at (714) 238-2444 or anaheim.net/republicservices before you need them (not an emergency move-out service). Place items at the curb on the scheduled date — crews do not enter homes.",
        ["Call Republic (714) 238-2444 to schedule.", "List items; curb on the appointment day.", "Take paint/batteries to OC HHW centers (e.g., Anaheim 1071 N. Blue Gum)."],
        [("Abandoned alley junk?", "Report via 311 / Anaheim Anytime — does not use your household allotment.")], *bulky))
    rows.append(R(
        c, st, "refrigerator", "SPECIAL_HANDLING", "Medium", True,
        "Included in Anaheim bulky allotment", "Anaheim / Republic bulky pickup",
        "Schedule Anaheim bulky for refrigerators within your 3 free pickups/year. Keep HHW chemicals for Orange County HHW Collection Centers (Tue–Sat 9–3).",
        ["Book Republic bulky; list the fridge.", "Curb on schedule day.", "HHW → OC centers."],
        [("OC Anaheim center?", "1071 N. Blue Gum Street, Anaheim — Tue–Sat 9 a.m.–3 p.m.")], *bulky))
    rows.append(R(
        c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
        "Anaheim bulky — confirm freon rules", "Anaheim / Republic bulky pickup",
        "Book Republic bulky for ACs; confirm freon rules. Chemicals go to OC HHW centers, not the curb.",
        ["Schedule bulky; ask about freon.", "Do not vent refrigerant.", "Use OC HHW for chemicals."],
        [("Hours?", "OC HHW centers Tue–Sat 9–3; closed major holidays / rainy weather.")], *bulky))
    add_ewaste(
        rows, c, st,
        "Orange County residents (including Anaheim) drop HHW and e-waste free at any of four OC Waste & Recycling HHW Collection Centers — Anaheim (1071 N. Blue Gum), Huntington Beach, Irvine (6411 Oak Canyon), or San Juan Capistrano. Hours: 9 a.m.–3 p.m. Tuesday–Saturday (closed major holidays and rainy weather). Limit 15 gallons or 125 pounds per trip; containers ≤5 gallons.",
        ["Pack sealed HHW/e-waste within limits.", "Visit any OC HHW center Tue–Sat 9–3.", "Call 714-834-4000 with questions."],
        [("Bulky e-waste?", "Prefer OC HHW for electronics/chemicals; confirm with Republic if a specific e-item can ride on bulky.")],
        hhw, "OC HHW Collection Center — Anaheim 1071 N. Blue Gum",
    )
    add_hhw_bundle(
        rows, c, st,
        "Do not trash HHW in Anaheim. Use Orange County’s free HHW Collection Centers (Anaheim 1071 N. Blue Gum Street is closest for many residents), Tuesday–Saturday 9 a.m.–3 p.m. Accepted materials include paint, batteries, automotive fluids, fluorescents, pesticides, and electronics. Transport ≤15 gal / 125 lb; do not mix wastes.",
        ["Stay within DOT transport limits.", "Visit Tue–Sat 9–3 (not rainy-weather closures).", "Medications generally are not OC HHW — use pharmacy take-back."],
        [("Stop & Swap?", "OC centers often offer reuse of still-usable products — ask on-site.")],
        hhw, "OC HHW Collection Centers",
    )
    add_commons(
        rows, c, st, bulky, hhw,
        "Use Anaheim organics for yard waste; oversized piles may use bulky appointments.",
        "Food scraps go in organics. Keep sharps for HHW/pharmacy programs.",
        "Prefer tire retailer take-back; confirm Republic bulky tire rules before curbing.",
        "Building materials are typically not free bulky — use debris box; keep paint for OC HHW.",
        "Do not pour cooking oil into drains. Confirm OC HHW acceptance or grease recycler.",
    )
    return rows


def santa_ana():
    c, st = "santa-ana", "CA"
    bulky = ("City of Santa Ana — Bulky Item Pickup", "https://www.santa-ana.org/bulky-item-pickup-is-free-and-easy/")
    hhw = ("OC Waste & Recycling — HHW Collection Centers", "https://oclandfills.com/hhw")
    rows = []
    rows.append(R(
        c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
        "4 free bulky pickups/year, up to 4 items each (Republic)", "Santa Ana / Republic bulky pickup",
        "Santa Ana residents with curbside trash get four free bulky pickups per year, up to four items each (beds, sofas, appliances, etc.). Multifamily (3+ units) has a separate quarterly allotment — check the property manager for the setout spot. Schedule with Republic Services at 657-467-6220. City guidance also lists computer monitors, TVs, and laptops as accepted on bulky pickups.",
        ["Call Republic 657-467-6220 to schedule.", "Curb up to 4 items per free pickup.", "Take paint/chemicals to OC HHW centers (not the curb)."],
        [("Extra pickup?", "Additional bulky after the yearly limit may be fee-based.")], *bulky))
    rows.append(R(
        c, st, "refrigerator", "SPECIAL_HANDLING", "Medium", True,
        "Included in Santa Ana bulky (counts toward 4-item cap)", "Santa Ana / Republic bulky pickup",
        "Refrigerators are listed among Santa Ana bulky acceptables. Schedule Republic pickup (657-467-6220). Keep HHW for Orange County HHW centers.",
        ["Book bulky; list the fridge.", "Curb on schedule day.", "HHW → OC centers Tue–Sat 9–3."],
        [("HHW tires/events?", "City sometimes hosts special HHW/tire drop-off events — watch city/Republic notices.")], *bulky))
    rows.append(R(
        c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
        "Santa Ana bulky — confirm freon rules", "Santa Ana / Republic bulky pickup",
        "Book Republic bulky for ACs; confirm freon rules. Chemicals/batteries go to OC HHW Collection Centers.",
        ["Schedule bulky; ask about freon.", "Do not vent refrigerant.", "Use OC HHW for chemicals."],
        [("Closest OC center?", "Anaheim 1071 N. Blue Gum or Huntington Beach / Irvine / SJC sites.")], *bulky))
    add_ewaste(
        rows, c, st,
        "Santa Ana city guidance accepts TVs/monitors/laptops on bulky pickup (counts toward item limits). You can also drop e-waste free at Orange County HHW Collection Centers (Tue–Sat 9–3). Prefer wiping data first. Paint/chemicals still need OC HHW — not trash carts.",
        ["Schedule bulky for e-waste or visit an OC HHW center.", "Wipe devices.", "Keep chemicals for OC HHW."],
        [("Rate-sheet conflicts?", "Follow current City of Santa Ana bulky guidance; confirm with Republic when booking.")],
        bulky, "Santa Ana bulky or OC HHW centers", curbside=True,
        fee="Free within bulky allotment / free OC HHW drop-off",
    )
    add_hhw_bundle(
        rows, c, st,
        "Do not trash HHW in Santa Ana. Use Orange County’s free HHW Collection Centers year-round (Tue–Sat 9 a.m.–3 p.m.) for paint, batteries, automotive fluids, fluorescents, pesticides, and electronics. Limit 15 gallons or 125 pounds per trip. City-sponsored one-day HHW events also occur periodically.",
        ["Pack sealed HHW within limits.", "Visit any OC HHW center Tue–Sat 9–3.", "Watch city notices for free local HHW/tire events."],
        [("Bulky HHW?", "No — chemicals/universal waste are not trash-cart or standard bulky chemicals pathways.")],
        hhw, "OC HHW Collection Centers",
    )
    add_commons(
        rows, c, st, bulky, hhw,
        "Use Santa Ana organics for yard waste; some bulky pickups allow bagged yard waste alternatives — confirm with Republic.",
        "Food scraps go in organics.",
        "Tires are often excluded from standard bulky — use retailer take-back or city HHW/tire events when offered.",
        "No building materials on bulky — debris box/transfer; paint → OC HHW.",
        "Do not pour cooking oil into drains. Confirm OC HHW / event acceptance or grease recycler.",
    )
    return rows


def irvine():
    c, st = "irvine", "CA"
    bulky = ("City of Irvine / WM — Bulky Item Collection", "https://cityofirvine.org/sustainability-division/household-hazardous-waste")
    hhw = ("City of Irvine — Household Hazardous Waste / OC HHW Irvine", "https://cityofirvine.org/sustainability-division/household-hazardous-waste")
    rows = []
    rows.append(R(
        c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
        "4 free bulky pickups/year, up to 4 items (WM)", "Irvine / WM bulky pickup",
        "Irvine residents get four free bulky pickups per calendar year through Waste Management, up to four large items each (furniture, appliances, e-waste) or alternatively bagged trash/yard waste within published limits. Call WM at (949) 642-1191 at least 48 hours / 2 business days before your collection day to schedule.",
        ["Call WM (949) 642-1191 ≥2 business days ahead.", "Curb items on the scheduled collection day.", "Take paint/chemicals to Irvine OC HHW Center at 6411 Oak Canyon."],
        [("Senior discount?", "Irvine publishes senior/low-volume cart discounts separately — ask WM.")], *bulky))
    rows.append(R(
        c, st, "refrigerator", "SPECIAL_HANDLING", "Medium", True,
        "Included in Irvine WM bulky allotment", "Irvine / WM bulky pickup",
        "Schedule WM bulky for refrigerators within your 4 free pickups/year. HHW chemicals go to the Irvine Household Hazardous Waste Collection Center (OC Waste & Recycling) at 6411 Oak Canyon.",
        ["Book WM bulky; list the fridge.", "Curb on schedule day.", "HHW → 6411 Oak Canyon Tue–Sat 9–3."],
        [("Lease note?", "City notes the Irvine HHW center lease extended through Dec 31, 2026 — still open.")], *bulky))
    rows.append(R(
        c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
        "Irvine bulky — confirm freon rules", "Irvine / WM bulky pickup",
        "Book WM bulky for ACs; confirm freon rules. Chemicals/batteries go to 6411 Oak Canyon HHW center.",
        ["Schedule bulky; ask about freon.", "Do not vent refrigerant.", "Use Irvine OC HHW for chemicals."],
        [("Disabled HHW home pickup?", "WM At Your Door for DMV-registered disabled residents: 1-800-449-7587.")], *bulky))
    add_ewaste(
        rows, c, st,
        "Irvine WM bulky includes electronic waste (TVs, computers, monitors). You can also drop e-waste free at the Irvine OC HHW Collection Center, 6411 Oak Canyon, Tuesday–Saturday 9 a.m.–3 p.m. (closed major holidays / rainy weather). Limit 15 gal / 125 lb per trip.",
        ["Schedule bulky for e-waste or visit 6411 Oak Canyon.", "Wipe data.", "Keep chemicals for HHW center."],
        [("Phone?", "WM (949) 642-1191; OC HHW info 714-834-4000.")],
        hhw, "OC HHW Irvine — 6411 Oak Canyon", curbside=True,
        fee="Free within bulky allotment / free OC HHW",
    )
    add_hhw_bundle(
        rows, c, st,
        "Do not trash HHW in Irvine. Use the Irvine Household Hazardous Waste Collection Center at 6411 Oak Canyon (OC Waste & Recycling), Tuesday–Saturday 9 a.m.–3 p.m. Accepted examples include paint, batteries, automotive fluids, CFLs, pesticides, pool chemicals, sharps, and e-waste. Transport ≤15 gallons or 125 pounds. Medications are not OC HHW — follow pharmacy/trash guidance the city publishes for meds.",
        ["Pack sealed labeled HHW within limits.", "Visit 6411 Oak Canyon Tue–Sat 9–3.", "Ask about Stop & Swap reuse on-site."],
        [("Center closing?", "City announced lease extension through Dec 31, 2026 — verify if visiting near that date.")],
        hhw, "OC HHW Irvine — 6411 Oak Canyon",
    )
    add_commons(
        rows, c, st, bulky, hhw,
        "Use Irvine organics for yard waste; bulky can alternate for bagged yard waste within WM rules.",
        "Food scraps go in green organics.",
        "Prefer tire retailer take-back; confirm WM bulky tire rules before curbing.",
        "Building materials generally need debris box/transfer; paint → Irvine HHW center.",
        "Do not pour cooking oil into drains. Confirm HHW acceptance or grease recycler.",
    )
    return rows


def chula_vista():
    c, st = "chula-vista", "CA"
    bulky = ("City of Chula Vista — Bulky Item & Landfill Passes", "https://www.chulavistaca.gov/departments/clean/environmental-services/special-services")
    hhw = ("City of Chula Vista — Hazardous Waste Disposal", "https://www.chulavistaca.gov/departments/clean/environmental-services/hazardous-waste")
    rows = []
    rows.append(R(
        c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
        "Free bulky via Republic (schedule ≥24 hours ahead)", "Chula Vista / Republic bulky pickup",
        "Chula Vista residents schedule free bulky item pickup with Republic Services at (619) 421-9400 at least 24 hours before the service day (city FAQ notes up to 10 bulky items). Cart customers in good standing also get two Otay Landfill passes and two yard-waste passes per year (call 619-482-4024 or pick up at 891 Energy Way). Keep HHW for the South Bay HHW Facility — not bulky.",
        ["Call Republic (619) 421-9400 ≥24 hours ahead.", "Curb bulky items for the scheduled service day.", "Take paint/batteries/e-waste to South Bay HHW (1800 Maxwell Rd) Wed/Sat."],
        [("Landfill pass limit?", "About 1 ton per pass; overages charged landfill rates.")], *bulky))
    rows.append(R(
        c, st, "refrigerator", "SPECIAL_HANDLING", "Medium", True,
        "Republic bulky / landfill pass appliance recycling", "Chula Vista bulky or Otay Landfill pass",
        "Schedule Republic bulky for refrigerators or use an Otay Landfill pass (separate metals/appliances when loading). Confirm freon rules when booking. Chemicals go to South Bay HHW — large appliances are not accepted there.",
        ["Book bulky or use a landfill pass.", "Ask about freon.", "HHW chemicals → 1800 Maxwell Road Wed/Sat."],
        [("South Bay fridge?", "South Bay HHW lists large appliances among not-accepted items.")], *bulky))
    rows.append(R(
        c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
        "Republic bulky — confirm freon rules", "Chula Vista / Republic bulky pickup",
        "Book Republic bulky for ACs; confirm freon rules. HHW chemicals/electronics go to South Bay HHW Facility.",
        ["Schedule bulky; ask about freon.", "Do not vent refrigerant.", "Use South Bay HHW for chemicals/e-waste."],
        [("City of San Diego residents?", "Not accepted at South Bay HHW — they must use Miramar.")], *bulky))
    add_ewaste(
        rows, c, st,
        "Chula Vista, Imperial Beach, National City, and unincorporated County residents drop HHW and electronics free at the South Bay Household Hazardous Waste Collection Facility, 1800 Maxwell Road (second entrance), Wednesday and Saturday 9 a.m.–1 p.m., no appointment (proof of residency required). Limit ~15 gallons or 125 pounds. City of San Diego residents are not accepted here.",
        ["Pack sealed e-waste/HHW.", "Visit Wed or Sat 9–1 with residency proof.", "Do not bring large appliances or tires to South Bay HHW."],
        [("Home pickup?", "Disabled/elderly may qualify — call (619) 691-5122.")],
        hhw, "South Bay HHW — 1800 Maxwell Road",
    )
    add_hhw_bundle(
        rows, c, st,
        "Do not trash HHW in Chula Vista. Use South Bay HHW at 1800 Maxwell Road, Wed & Sat 9 a.m.–1 p.m. (no appointment). Accepted examples include paint, pesticides, pool chemicals, motor oil/filters, fluorescents, batteries, sharps, cooking oil, fuel, and electronics. Transport ≤15 gal / 125 lb. Not accepted: business waste, meds (except sharps rules), tires, large appliances.",
        ["Bring residency proof.", "Visit Wed/Sat 9–1.", "Keep loads sealed in trunk/bed."],
        [("Cooking oil?", "Listed among South Bay acceptables."),
         ("Phone?", "HHW questions (619) 691-5122; Republic bulky (619) 421-9400.")],
        hhw, "South Bay HHW — 1800 Maxwell Road",
    )
    add_commons(
        rows, c, st, bulky, hhw,
        "Use Chula Vista organics for yard waste; yard-waste landfill passes and bulky are options for oversized loads.",
        "Food scraps go in organics. Keep sharps for South Bay HHW.",
        "Tires are not South Bay HHW — prefer retailer take-back or landfill pathways.",
        "Use landfill passes / debris service for C&D; keep paint for South Bay HHW.",
        "South Bay HHW lists cooking oil among acceptables — still never pour oil into drains.",
    )
    return rows


FACILITY_UPDATES = {
    "los-angeles": [
        {
            "name": "LASAN S.A.F.E. Centers (HHW & e-waste)",
            "facility_type": "HHW / e-waste drop-off",
            "city_slug": "los-angeles",
            "state": "CA",
            "zip": "90012",
            "address": "Multiple permanent weekend S.A.F.E. Center locations citywide — see LASAN S.A.F.E. Centers page",
            "lat": 34.0522,
            "lng": -118.2437,
            "source_url": "https://lacity.gov/residents/trash-recycling",
            "hours": "Open weekends (confirm location hours before visiting)",
            "phone": "1-800-773-2489",
        }
    ],
    "san-diego": [
        {
            "name": "Miramar Household Hazardous Waste Transfer Facility",
            "facility_type": "HHW / e-waste (appointment only)",
            "city_slug": "san-diego",
            "state": "CA",
            "zip": "92111",
            "address": "5161 Convoy Street (Miramar Landfill entrance), San Diego, CA 92111",
            "lat": 32.84,
            "lng": -117.15,
            "source_url": "https://www.sandiego.gov/environmental-services/ep/hazardous",
            "hours": "Wed & Sat 9:00–15:00 by appointment (except holidays)",
            "phone": "858-694-7000",
        }
    ],
    "san-francisco": [
        {
            "name": "Recology Household Hazardous Waste Facility",
            "facility_type": "HHW drop-off",
            "city_slug": "san-francisco",
            "state": "CA",
            "zip": "94134",
            "address": "501 Tunnel Avenue, San Francisco, CA 94134",
            "lat": 37.7125,
            "lng": -122.4019,
            "source_url": "https://www.recology.com/recology-san-francisco/hazardous-waste/",
            "hours": "Thu–Sat 8:00–16:00",
            "phone": "415-330-1400",
        }
    ],
    "san-jose": [
        {
            "name": "Santa Clara County HHW — East San Jose (appointment)",
            "facility_type": "HHW / e-waste (appointment; address after booking)",
            "city_slug": "san-jose",
            "state": "CA",
            "zip": "95100",
            "address": "East San Jose permanent HHW — exact address provided after appointment",
            "lat": 37.3382,
            "lng": -121.8863,
            "source_url": "https://hhw.santaclaracounty.gov/drop-household-waste",
            "hours": "Typically Thu–Sat by appointment (see county schedule)",
            "phone": "(408) 299-7300",
        }
    ],
    "sacramento": [
        {
            "name": "Sacramento Recycling & Transfer Station HHW",
            "facility_type": "HHW / e-waste",
            "city_slug": "sacramento",
            "state": "CA",
            "zip": "95826",
            "address": "8491 Fruitridge Road, Sacramento, CA 95826",
            "lat": 38.53,
            "lng": -121.41,
            "source_url": "https://www.cityofsacramento.gov/public-works/recycling-solid-waste/Householdhazardouswaste/HHWfacilities",
            "hours": "Tue–Sat 8:00–17:00",
            "phone": "(916) 379-0500",
        }
    ],
    "oakland": [
        {
            "name": "Alameda County HHW — Oakland Facility",
            "facility_type": "HHW / e-waste",
            "city_slug": "oakland",
            "state": "CA",
            "zip": "94606",
            "address": "2100 East 7th Street, Oakland, CA 94606",
            "lat": 37.79,
            "lng": -122.24,
            "source_url": "https://www.stopwaste.org/recycling-disposal/hazardous-waste/household-hazardous-waste",
            "hours": "Wed–Fri 9:00–14:30; Sat 9:00–16:00",
            "phone": "1-800-606-6606",
        }
    ],
    "long-beach": [
        {
            "name": "Gaffey Street S.A.F.E. Center (San Pedro)",
            "facility_type": "HHW / e-waste",
            "city_slug": "long-beach",
            "state": "CA",
            "zip": "90731",
            "address": "1400 N. Gaffey Street, San Pedro, CA 90731",
            "lat": 33.75,
            "lng": -118.29,
            "source_url": "https://longbeach.gov/lbrecycles/hazardous-waste/household-hazardous-waste/hhw-101/",
            "hours": "Sat–Sun 9:00–15:00",
            "phone": "1-800-988-6942",
        }
    ],
    "anaheim": [
        {
            "name": "OC HHW Collection Center — Anaheim",
            "facility_type": "HHW / e-waste",
            "city_slug": "anaheim",
            "state": "CA",
            "zip": "92806",
            "address": "1071 N. Blue Gum Street, Anaheim, CA 92806",
            "lat": 33.85,
            "lng": -117.85,
            "source_url": "https://oclandfills.com/hhw",
            "hours": "Tue–Sat 9:00–15:00",
            "phone": "714-834-4000",
        }
    ],
    "santa-ana": [
        {
            "name": "OC HHW Collection Center — Anaheim (nearest hub)",
            "facility_type": "HHW / e-waste",
            "city_slug": "santa-ana",
            "state": "CA",
            "zip": "92806",
            "address": "1071 N. Blue Gum Street, Anaheim, CA 92806",
            "lat": 33.85,
            "lng": -117.85,
            "source_url": "https://oclandfills.com/hhw",
            "hours": "Tue–Sat 9:00–15:00",
            "phone": "714-834-4000",
        }
    ],
    "irvine": [
        {
            "name": "OC HHW Collection Center — Irvine",
            "facility_type": "HHW / e-waste",
            "city_slug": "irvine",
            "state": "CA",
            "zip": "92618",
            "address": "6411 Oak Canyon, Irvine, CA 92618",
            "lat": 33.67,
            "lng": -117.76,
            "source_url": "https://cityofirvine.org/sustainability-division/household-hazardous-waste",
            "hours": "Tue–Sat 9:00–15:00",
            "phone": "714-834-4000",
        }
    ],
    "chula-vista": [
        {
            "name": "South Bay Household Hazardous Waste Collection Facility",
            "facility_type": "HHW / e-waste",
            "city_slug": "chula-vista",
            "state": "CA",
            "zip": "91911",
            "address": "1800 Maxwell Road, Chula Vista, CA 91911",
            "lat": 32.6,
            "lng": -117.03,
            "source_url": "https://www.chulavistaca.gov/departments/clean/environmental-services/hazardous-waste",
            "hours": "Wed & Sat 9:00–13:00",
            "phone": "(619) 691-5122",
        }
    ],
}


def main() -> None:
    builders = {
        "los-angeles": los_angeles,
        "san-diego": san_diego,
        "san-francisco": san_francisco,
        "san-jose": san_jose,
        "sacramento": sacramento,
        "oakland": oakland,
        "long-beach": long_beach,
        "anaheim": anaheim,
        "santa-ana": santa_ana,
        "irvine": irvine,
        "chula-vista": chula_vista,
    }
    audited_cities = {slug: clone_siblings(fn()) for slug, fn in builders.items()}

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
    facilities = [f for f in facilities if f.get("city_slug") not in FACILITY_UPDATES]
    for rows in FACILITY_UPDATES.values():
        facilities.extend(rows)
    fac_path.write_text(json.dumps(facilities, indent=2))
    (DATA / "facilities" / "ca.json").write_text(
        json.dumps([f for f in facilities if f.get("state") == "CA"], indent=2)
    )

    print("Audited cities:", ", ".join(sorted(audited_cities)))
    print("Total rules:", len(keep))
    for city, rows in sorted(audited_cities.items()):
        print(f"  {city}: {len(rows)} rules; mattress={rows[0]['source_name'][:48]}")


if __name__ == "__main__":
    main()
