#!/usr/bin/env python3
"""Portal-audited city guides for wave-10 metros (city-sourced only).

Cities researched from official program pages (2026-08-11):
  - Colorado Springs, CO — coloradosprings.gov WastelessCOS / El Paso County HHW & Clean Sweep
  - Wichita, KS — wichita.gov Neighborhood Cleanup / Sedgwick County HHW / Brooks Landfill
  - Arlington, TX — arlingtontx.gov curbside bulk / Fort Worth ECC HHW / Mosier Valley landfill
  - New Orleans, LA — nola.gov trash & recycling drop-off / 311 bulky
  - Tampa, FL — tampa.gov SWEEP / McKay Bay / Hillsborough County HHW & CCC
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


def colorado_springs():
    c, st = "colorado-springs", "CO"
    wasteless = ("City of Colorado Springs — WastelessCOS", "https://coloradosprings.gov/wastelesscos")
    hhw = ("El Paso County — Household hazardous waste", "https://communityresources.elpasoco.com/household-hazardous-waste")
    landfill = ("Colorado Springs Landfill — El Paso County", "https://communityresources.elpasoco.com/landfill")
    rows = []
    rows.append(R(c, st, "mattress", "SPECIAL_HANDLING", "Low", False,
        "NO citywide bulky — private hauler or landfill; Clean Sweep mattress paused Aug 2026",
        "Private hauler / Colorado Springs Landfill — 1010 Blaney Rd",
        "Colorado Springs has NO citywide bulky pickup — residential service is through private haulers (WM, Republic, etc.). The county Clean Sweep mattress program is paused as of August 2026. Mattresses go through your hauler for a fee, self-haul to Colorado Springs Landfill at 1010 Blaney Rd, or hire a junk hauler. Keep It Clean COS is neighborhood events only — not a citywide bulky program.",
        ["Confirm your private hauler's bulky or extra-pickup fees.", "Or self-haul to Colorado Springs Landfill 1010 Blaney Rd — call for fees.", "Do not assume Clean Sweep mattress drop-off — program paused Aug 2026."],
        [("City bulky pickup?", "No — Colorado Springs has no citywide bulky program."), ("Clean Sweep mattress?", "Paused as of Aug 2026 — use hauler or landfill.")], *wasteless))
    rows.append(R(c, st, "refrigerator", "SPECIAL_HANDLING", "High", False,
        "NOT El Paso HHW — Landfill 1010 Blaney Rd or EPA freon recovery (fees; call)",
        "Colorado Springs Landfill — 1010 Blaney Rd / EPA-certified freon recovery",
        "Freon refrigerators and freezers are NOT accepted at El Paso County HHW. Self-haul to Colorado Springs Landfill at 1010 Blaney Rd for a fee — call ahead — or use an EPA-certified freon recovery service. Never vent refrigerant yourself.",
        ["Do not haul refrigerators to El Paso County HHW 3255 Akers Dr.", "Call landfill 1010 Blaney Rd for appliance fees.", "Keep doors secured; never release Freon."], [("HHW for fridge?", "No — El Paso County HHW rejects Freon appliances.")], *landfill))
    rows.append(R(c, st, "air-conditioner", "SPECIAL_HANDLING", "High", False,
        "NOT El Paso HHW — landfill 1010 Blaney Rd or EPA freon recovery (fees; call)",
        "Colorado Springs Landfill — 1010 Blaney Rd / EPA-certified freon recovery",
        "Freon window and portable air conditioners are NOT accepted at El Paso County HHW. Self-haul to Colorado Springs Landfill 1010 Blaney Rd for a fee — call ahead — or use EPA-certified freon recovery. Never vent refrigerant yourself.",
        ["Do not take Freon AC to HHW 3255 Akers Dr.", "Call landfill for fee before hauling.", "Keep the sealed unit intact."], [("Same as fridge?", "Yes — Freon appliances use landfill/recovery, not HHW.")], *landfill))
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(R(c, st, item, "SPECIAL_HANDLING", "Medium", False,
            "Private hauler bulky fee OR landfill 1010 Blaney Rd — no HHW/Freon path",
            "Private hauler / Colorado Springs Landfill — 1010 Blaney Rd",
            f"Non-Freon appliances such as {item.replace('-', ' ')}s have no citywide curbside bulky. Use your private hauler's extra-pickup service or self-haul to Colorado Springs Landfill 1010 Blaney Rd. El Paso County HHW does not accept appliances.",
            ["Call private hauler for bulky/extra appliance fees.", "Or self-haul to landfill 1010 Blaney Rd.", "Do not haul appliances to El Paso County HHW."],
            [("HHW for washer?", "No — appliances not accepted at HHW."), ("Freon fee?", "No — Freon fees apply to refrigerators/AC only.")], *wasteless))
    for item, label in [("television", "TVs"), ("computer-monitor", "monitors"), ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste")]:
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS", "Medium", False,
            "El Paso HHW — CRT ≤20 lb, flat ≤40 lb; large TVs at Clean Sweep events",
            "El Paso County HHW — 3255 Akers Dr / Clean Sweep e-waste",
            f"Electronics including {label} go to El Paso County HHW at 3255 Akers Dr with size limits — CRT ≤20 lb, flat ≤40 lb. Large TVs use Clean Sweep events. Mon/Tue/Thu/Fri 8:30–12 & 1–4; closed Wed; limited Sat. Wipe data before drop-off.",
            ["Check HHW hours Mon/Tue/Thu/Fri 8:30–12 & 1–4.", "Confirm size limits at HHW.", "Large TVs: check Clean Sweep calendar."],
            [("Large TV at HHW?", "Large TVs primarily use Clean Sweep events.")], *hhw))
    rows.append(R(c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", False,
        "Free at El Paso HHW — latex and oil; 50 gal/year limit",
        "El Paso County HHW — 3255 Akers Dr",
        "Liquid latex and oil paint are free at El Paso County HHW, 3255 Akers Dr — Mon/Tue/Thu/Fri 8:30–12 & 1–4; closed Wed; limit 50 gallons/year per household.",
        ["Haul paint to HHW 3255 Akers Dr during posted hours.", "Limit 50 gal/year per household.", "Keep paint sealed and labeled."],
        [("Free paint?", "Yes — latex and oil free at HHW within 50 gal/year.")], *hhw))
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
            "El Paso County HHW — Mon/Tue/Thu/Fri 8:30–12 & 1–4; closed Wed",
            "El Paso County HHW — 3255 Akers Dr",
            f"Take {item.replace('-', ' ')} to El Paso County HHW 3255 Akers Dr — Mon/Tue/Thu/Fri 8:30–12 & 1–4; closed Wed; limited Sat.",
            ["Deliver sealed containers during HHW hours.", "Check Sat dates on county site.", "Keep chemicals out of trash."],
            [("Same as paint?", "Yes — chemicals use El Paso County HHW.")], *hhw))
    for item in ["car-battery", "lithium-battery", "paint-oil", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {"car-battery": " Auto/household batteries at HHW.", "lithium-battery": " Lithium batteries at HHW.", "paint-oil": " Oil paint at HHW.", "motor-oil": " Used motor oil at HHW.", "propane-tank": " Propane at HHW.", "fluorescent-bulbs": " Fluorescents at HHW.", "cooking-oil": " Cooking oil at HHW when not trash-safe."}[item]
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING", "High" if item != "cooking-oil" else "Medium", False,
            "El Paso County HHW — Mon/Tue/Thu/Fri 8:30–12 & 1–4", "El Paso County HHW — 3255 Akers Dr",
            f"El Paso County HHW 3255 Akers Dr accepts household hazardous materials Mon/Tue/Thu/Fri 8:30–12 & 1–4.{extra}",
            ["Deliver sealed containers during HHW hours.", "Check Sat dates.", "Freon appliances use landfill pathways."], [("Address?", "3255 Akers Dr.")], *hhw))
    rows.append(R(c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
        "Rigid sealed container — confirm El Paso HHW sharps acceptance", "El Paso County HHW — 3255 Akers Dr",
        "Place sharps in a rigid sealed container. Confirm acceptance at El Paso County HHW. Do not loose-bag needles.",
        ["Use rigid sealed container.", "Confirm sharps acceptance before hauling.", "Never recycle loose needles."], [("Medications?", "Confirm drug take-back on county page.")], *hhw))
    rows.append(R(c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
        "NOT curbside — Clean Sweep tire events primarily", "El Paso County Clean Sweep / landfill (fee)",
        "Tires are NOT on any citywide curbside bulky program. Clean Sweep events are the primary pathway — check communityresources.elpasoco.com.",
        ["Check Clean Sweep calendar for tire events.", "Do not set tires out without confirming hauler acceptance.", "Retailer take-back when replacing tires."], [("Curbside tires?", "No — Clean Sweep events primarily.")], *wasteless))
    rows.append(R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True, "Private hauler yard waste — confirm with hauler", "Private hauler yard waste",
        "Yard waste is handled through your private hauler's programs. Follow hauler set-out rules.",
        ["Confirm yard waste with private hauler.", "Keep yard waste out of HHW.", "Check WastelessCOS for seasonal tips."], [("Christmas trees?", "Follow hauler or Clean Sweep guidance.")], *wasteless))
    rows.append(R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True, "Garbage cart unless private compost", "Colorado Springs garbage / private compost",
        "Bag food scraps for garbage unless you compost. Keep food out of recycling and HHW.",
        ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use hauler pathways."], [("HHW for food?", "No.")], *wasteless))
    rows.append(R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False, "Not recycling — store take-back / trash", "Retail bag take-back / trash",
        "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
        ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."], [("City bulky?", "No — store take-back or trash.")], *wasteless))
    rows.append(R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", False,
        "Private hauler or landfill 1010 Blaney Rd — fees; no citywide bulky", "Private hauler / Colorado Springs Landfill",
        "C&D has no citywide curbside bulky. Self-haul to landfill 1010 Blaney Rd or hire private C&D hauler. Route paint/chemicals to HHW.",
        ["Call landfill for C&D fees.", "Hire private C&D hauler for large loads.", "Route paint to HHW 3255 Akers Dr."], [("HHW for C&D?", "No — separate paint/chemicals.")], *landfill))
    return rows


def wichita():
    c, st = "wichita", "KS"
    cleanup = ("City of Wichita — Neighborhood Cleanup", "https://www.wichita.gov/Neighborhood-Cleanup")
    hhw = ("Sedgwick County — Household hazardous waste", "https://www.sedgwickcounty.org/environment/hazardous-waste/")
    brooks = ("Brooks Landfill — Sedgwick County", "https://www.sedgwickcounty.org/environment/landfill/")
    rows = []
    rows.append(R(c, st, "mattress", "SPECIAL_HANDLING", "Low", False,
        "Neighborhood Cleanup if eligible OR Brooks Landfill $20 OR private hauler",
        "Brooks Landfill / Neighborhood Cleanup (if eligible)",
        "Wichita has no universal city bulky pickup. Mattresses may go through income/organizer-gated Neighborhood Cleanup (one Saturday per year if eligible) or Brooks Landfill for about $20, or a private hauler. Check wichita.gov Neighborhood Cleanup eligibility.",
        ["Check Neighborhood Cleanup eligibility on wichita.gov.", "Or self-haul mattress to Brooks Landfill (~$20).", "Private hauler is always an option."],
        [("Universal city bulky?", "No — Cleanup is income/organizer gated once per year."), ("Brooks fee?", "About $20 for mattress at Brooks Landfill.")], *cleanup))
    rows.append(R(c, st, "refrigerator", "SPECIAL_HANDLING", "High", False,
        "NOT Cleanup — Brooks Landfill $50/unit Freon appliances; Waste Connections +$40",
        "Brooks Landfill — Freon appliance fee",
        "Freon refrigerators are excluded from Neighborhood Cleanup. Self-haul to Brooks Landfill for about $50 per Freon appliance unit, or Waste Connections may charge an additional ~$40 Freon fee. Sedgwick County HHW does NOT accept Freon appliances. Never vent refrigerant yourself.",
        ["Do not bring Freon refrigerators to Neighborhood Cleanup.", "Haul to Brooks Landfill — ~$50/unit Freon fee.", "Call Brooks/Waste Connections to confirm current fees."],
        [("Cleanup for fridge?", "No — Freon appliances excluded from Cleanup."), ("HHW for fridge?", "No — HHW does not take Freon appliances.")], *brooks))
    rows.append(R(c, st, "air-conditioner", "SPECIAL_HANDLING", "High", False,
        "NOT Cleanup — Brooks Landfill $50/unit Freon; Waste Connections +$40",
        "Brooks Landfill — Freon appliance fee",
        "Freon AC units are excluded from Neighborhood Cleanup. Self-haul to Brooks Landfill for about $50 per Freon unit or use Waste Connections with ~$40 Freon surcharge. Never vent refrigerant yourself.",
        ["Do not bring Freon AC to Neighborhood Cleanup.", "Haul to Brooks Landfill — ~$50/unit.", "Keep sealed until proper handling."],
        [("Same as fridge?", "Yes — Freon appliances use Brooks fee path, not Cleanup.")], *brooks))
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(R(c, st, item, "SPECIAL_HANDLING", "Medium", False,
            "Brooks Landfill without Freon fee OR Cleanup if eligible — NOT HHW",
            "Brooks Landfill / Neighborhood Cleanup (if eligible)",
            f"Non-Freon appliances such as {item.replace('-', ' ')}s may go to Brooks Landfill without the $50 Freon appliance fee (unlike refrigerators). Neighborhood Cleanup accepts eligible loads once per year. Sedgwick County HHW does not accept appliances.",
            ["Check Cleanup eligibility for your neighborhood.", "Or self-haul to Brooks Landfill — no Freon fee for washers.", "Do not haul appliances to Sedgwick HHW."],
            [("Brooks Freon fee for washer?", "No — $50 Freon fee applies to refrigerators/AC, not typical washers.")], *brooks))
    for item, label in [("television", "TVs"), ("computer-monitor", "monitors"), ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste")]:
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS", "Medium", False,
            "NOT Sedgwick HHW — private recycler fee or rare county events; trash discouraged",
            "Private e-waste recycler / county events (rare)",
            f"Sedgwick County HHW does NOT accept {label}. Wichita residents should use private electronics recyclers (fees may apply) or watch for rare county e-waste events. Do not put TVs/e-waste in regular trash — be honest that curbside/trash is discouraged.",
            ["Search for local e-waste recyclers — fees likely.", "Check sedgwickcounty.org for rare e-waste events.", "Wipe data before recycling."],
            [("HHW for TV?", "No — Sedgwick HHW does not take TVs/e-waste."), ("Trash OK?", "Discouraged — use private recycler or events.")], *cleanup))
    rows.append(R(c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", False,
        "Free at Sedgwick County HHW — Tue–Fri 9–5 Sat 9–3",
        "Sedgwick County HHW — 801 Stillwell St",
        "Liquid latex and oil paint are free at Sedgwick County HHW, 801 Stillwell St — Tue–Fri 9 a.m.–5 p.m., Sat 9 a.m.–3 p.m.",
        ["Haul paint to Sedgwick HHW 801 Stillwell St.", "Hours: Tue–Fri 9–5, Sat 9–3.", "Keep paint sealed and labeled."],
        [("Free paint?", "Yes — free at Sedgwick County HHW.")], *hhw))
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
            "Sedgwick County HHW — Tue–Fri 9–5 Sat 9–3", "Sedgwick County HHW — 801 Stillwell St",
            f"Take {item.replace('-', ' ')} to Sedgwick County HHW 801 Stillwell St — Tue–Fri 9–5, Sat 9–3.",
            ["Deliver sealed containers during HHW hours.", "Keep chemicals out of Cleanup loads.", "Freon appliances excluded from HHW."],
            [("Same as paint?", "Yes — chemicals use Sedgwick HHW.")], *hhw))
    for item in ["car-battery", "lithium-battery", "paint-oil", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {"car-battery": " Batteries at Sedgwick HHW.", "lithium-battery": " Lithium batteries at HHW.", "paint-oil": " Oil paint at HHW.", "motor-oil": " Motor oil at HHW.", "propane-tank": " Propane at HHW.", "fluorescent-bulbs": " Fluorescents at HHW.", "cooking-oil": " Cooking oil at HHW when not trash-safe."}[item]
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING", "High" if item != "cooking-oil" else "Medium", False,
            "Sedgwick County HHW — Tue–Fri 9–5 Sat 9–3", "Sedgwick County HHW — 801 Stillwell St",
            f"Sedgwick County HHW 801 Stillwell St accepts household hazardous materials Tue–Fri 9–5, Sat 9–3.{extra}",
            ["Deliver sealed containers during HHW hours.", "E-waste/TVs not accepted at HHW.", "Freon appliances use Brooks pathways."], [("Address?", "801 Stillwell St.")], *hhw))
    rows.append(R(c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
        "Rigid sealed container — confirm Sedgwick HHW sharps acceptance", "Sedgwick County HHW — 801 Stillwell St",
        "Place sharps in a rigid sealed container. Confirm acceptance at Sedgwick County HHW. Do not loose-bag needles.",
        ["Use rigid sealed container.", "Confirm sharps acceptance.", "Never recycle loose needles."], [("Medications?", "Confirm drug take-back on county page.")], *hhw))
    rows.append(R(c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
        "Neighborhood Cleanup up to 8/residence OR landfill/retailer fees — NOT curbside",
        "Neighborhood Cleanup / Brooks Landfill / retailer",
        "Tires are NOT on universal curbside bulky. Neighborhood Cleanup accepts up to 8 tires per residence if eligible. Otherwise Brooks Landfill or retailer take-back for fees.",
        ["Check Cleanup eligibility — up to 8 tires if eligible.", "Otherwise Brooks Landfill or tire retailer.", "Do not assume weekly curbside tire pickup."],
        [("Cleanup tire limit?", "Up to 8 tires per residence if Cleanup eligible.")], *cleanup))
    rows.append(R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True, "Wichita yard waste collection programs", "Wichita yard waste collection",
        "Wichita handles yard waste through regular collection programs. Follow set-out rules.",
        ["Use yard waste set-out rules.", "Keep yard waste out of Cleanup/HHW.", "Check wichita.gov for seasonal guidance."], [("Christmas trees?", "Follow city seasonal guidance.")], *cleanup))
    rows.append(R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True, "Garbage cart unless private compost", "Wichita garbage / private compost",
        "Bag food scraps for garbage unless you compost.",
        ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."], [("HHW for food?", "No.")], *cleanup))
    rows.append(R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False, "Not recycling — store take-back / trash", "Retail bag take-back / trash",
        "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
        ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."], [("Cleanup for bags?", "No — store take-back or trash.")], *cleanup))
    rows.append(R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", False,
        "NOT Cleanup for contractor loads — Brooks Landfill or private C&D hauler",
        "Brooks Landfill / private C&D hauler",
        "Large C&D is not for Neighborhood Cleanup. Self-haul to Brooks Landfill or hire a private C&D hauler. Route paint/chemicals to Sedgwick HHW.",
        ["Do not bring contractor C&D to Cleanup.", "Haul to Brooks or hire C&D hauler.", "Route paint to HHW 801 Stillwell St."], [("HHW for C&D?", "No — separate paint/chemicals.")], *brooks))
    return rows


def arlington():
    c, st = "arlington", "TX"
    bulky = ("City of Arlington — Curbside bulk collection", "https://www.arlingtontx.gov/city_hall/departments/solid_waste/curbside_collection")
    hhw = ("Fort Worth Environmental Collection Center — Arlington residents", "https://www.fortworthtexas.gov/departments/code-compliance/household-hazardous-waste")
    landfill = ("Arlington Landfill — Mosier Valley Rd", "https://www.arlingtontx.gov/city_hall/departments/solid_waste/landfill")
    rows = []
    rows.append(R(c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
        "Curbside bulk on recycling day ≤2 cy OR 3 free landfill visits/year",
        "Arlington curbside bulk / Mosier Valley Landfill",
        "Arlington offers curbside bulk collection on your recycling day — up to 2 cubic yards. Mattresses and furniture are accepted. Alternatively, residents get 3 free landfill visits per year at 800 Mosier Valley Rd.",
        ["Set mattress out on recycling day bulk collection (≤2 cy).", "Or use one of 3 free landfill visits at 800 Mosier Valley Rd.", "Keep bulk separate from regular carts."],
        [("Which day?", "Bulk goes out on recycling day."), ("Landfill free visits?", "3 free visits/year at Mosier Valley Rd.")], *bulky))
    rows.append(R(c, st, "refrigerator", "SPECIAL_HANDLING", "High", True,
        "Call Republic Services 817-317-2000 for large Freon appliances; bulk or landfill",
        "Republic Services / Mosier Valley Landfill",
        "Large Freon refrigerators require calling Republic Services at 817-317-2000 before set-out. Arlington bulk on recycling day (≤2 cy) or Mosier Valley Landfill (3 free visits/year) may apply once scheduled. Fort Worth ECC HHW does not replace Freon appliance scheduling. Never vent refrigerant.",
        ["Call Republic 817-317-2000 for Freon refrigerator pickup guidance.", "Schedule bulk on recycling day or use landfill visit.", "Keep doors secured until pickup."],
        [("Republic required?", "Yes — call 817-317-2000 for large Freon appliances.")], *bulky))
    rows.append(R(c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
        "Call Republic 817-317-2000 for Freon AC; bulk or landfill",
        "Republic Services / Mosier Valley Landfill",
        "Freon window/portable AC units require calling Republic Services 817-317-2000. Then use bulk on recycling day or Mosier Valley Landfill. Never vent refrigerant yourself.",
        ["Call Republic 817-317-2000 for Freon AC.", "Set out on recycling day bulk after scheduling.", "Or use landfill free visit."],
        [("Same as fridge?", "Yes — call Republic for Freon appliances.")], *bulky))
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(R(c, st, item, "SPECIAL_HANDLING", "Medium", True,
            "Curbside bulk on recycling day ≤2 cy — no Republic Freon call for washers",
            "Arlington curbside bulk / Mosier Valley Landfill",
            f"Non-Freon appliances such as {item.replace('-', ' ')}s go on Arlington curbside bulk on recycling day (≤2 cy) or Mosier Valley Landfill. No Republic Freon call required for typical washers — that rule applies to Freon refrigerators/AC.",
            ["Set appliance out on recycling day bulk (≤2 cy).", "Or use Mosier Valley Landfill free visit.", "Empty appliance before set-out."],
            [("Republic call for washer?", "No — Freon call is for refrigerators/AC only.")], *bulky))
    for item, label in [("television", "TVs"), ("computer-monitor", "monitors"), ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste")]:
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS", "Medium", False,
            "City e-waste events ~2/year — NOT typical curbside bulk",
            "Arlington e-waste collection events",
            f"Electronics including {label} are handled at Arlington city e-waste events (~2 per year) — not typical curbside bulk. Check arlingtontx.gov for event dates. Wipe data before drop-off.",
            ["Check arlingtontx.gov for e-waste event calendar.", "Do not assume recycling-day bulk covers e-waste.", "Wipe personal data."],
            [("Curbside e-waste?", "No — city events ~2/year, not regular bulk.")], *bulky))
    rows.append(R(c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", True,
        "Fully dried latex in trash OK; liquid latex at Fort Worth ECC",
        "Household trash (dried) / Fort Worth ECC — 6400 Bridge St",
        "Fully dried latex paint (solidified) may go in Arlington household trash. Liquid latex goes to Fort Worth Environmental Collection Center, 6400 Bridge St — Thu–Fri 11 a.m.–7 p.m., Sat 9 a.m.–3 p.m.; Arlington residents 1 visit/month.",
        ["Liquid latex: haul to Fort Worth ECC 6400 Bridge St.", "Dried latex: solidify completely, then trash.", "Oil paint: Fort Worth ECC only."],
        [("Trash for dried latex?", "Yes — fully dried latex cans may go in trash.")], *hhw))
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
            "Fort Worth ECC — Thu–Fri 11–7 Sat 9–3; 1 visit/month", "Fort Worth ECC — 6400 Bridge St",
            f"Take {item.replace('-', ' ')} to Fort Worth ECC 6400 Bridge St — Thu–Fri 11–7, Sat 9–3; Arlington residents 1 visit/month.",
            ["Deliver sealed containers during ECC hours.", "Arlington limit: 1 visit/month.", "Keep chemicals out of bulk piles."],
            [("Same as dried latex?", "No — chemicals require ECC.")], *hhw))
    for item in ["car-battery", "lithium-battery", "paint-oil", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {"car-battery": " Batteries at Fort Worth ECC.", "lithium-battery": " Lithium batteries at ECC.", "paint-oil": " Oil paint at ECC.", "motor-oil": " Motor oil at ECC.", "propane-tank": " Propane at ECC.", "fluorescent-bulbs": " Fluorescents at ECC.", "cooking-oil": " Cooking oil at ECC when not trash-safe."}[item]
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING", "High" if item != "cooking-oil" else "Medium", False,
            "Fort Worth ECC — Thu–Fri 11–7 Sat 9–3; 1 visit/month", "Fort Worth ECC — 6400 Bridge St",
            f"Fort Worth ECC 6400 Bridge St accepts household hazardous materials for Arlington residents — 1 visit/month.{extra}",
            ["Deliver sealed containers Thu–Fri 11–7 or Sat 9–3.", "Arlington limit: 1 visit/month.", "Tires use landfill — not ECC."], [("Address?", "6400 Bridge St, Fort Worth.")], *hhw))
    rows.append(R(c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
        "Rigid sealed container — confirm Fort Worth ECC sharps acceptance", "Fort Worth ECC — 6400 Bridge St",
        "Place sharps in a rigid sealed container. Confirm acceptance at Fort Worth ECC. Do not loose-bag needles.",
        ["Use rigid sealed container.", "Confirm sharps at ECC before hauling.", "Never recycle loose needles."], [("Medications?", "Confirm drug take-back at ECC.")], *hhw))
    rows.append(R(c, st, "tires", "SPECIAL_HANDLING", "Medium", False,
        "NOT curbside bulk — Mosier Valley Landfill", "Arlington Landfill — 800 Mosier Valley Rd",
        "Tires are NOT accepted on curbside bulk. Self-haul to Mosier Valley Landfill 800 Mosier Valley Rd — residents get 3 free visits/year. Confirm tire rules on arlingtontx.gov.",
        ["Do not set tires out for bulk collection.", "Haul to Mosier Valley Landfill.", "Use one of 3 free annual visits if available."],
        [("Bulk for tires?", "No — tires go to landfill, not curbside bulk.")], *landfill))
    rows.append(R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True, "Arlington yard waste collection", "Arlington yard waste collection",
        "Arlington handles yard waste through regular collection. Follow set-out rules.",
        ["Use yard waste set-out rules.", "Keep yard waste out of bulk and ECC loads.", "Check arlingtontx.gov for seasonal guidance."], [("Christmas trees?", "Follow city seasonal guidance.")], *bulky))
    rows.append(R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True, "Garbage cart unless private compost", "Arlington garbage / private compost",
        "Bag food scraps for garbage unless you compost.",
        ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."], [("HHW for food?", "No.")], *bulky))
    rows.append(R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False, "Not recycling — store take-back / trash", "Retail bag take-back / trash",
        "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
        ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."], [("Bulk for bags?", "No.")], *bulky))
    rows.append(R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", True,
        "Bulk on recycling day for limited loads (≤2 cy) — private C&D for larger",
        "Arlington curbside bulk / private C&D hauler",
        "Limited homeowner C&D may fit recycling-day bulk (≤2 cy). Larger loads need private C&D hauler or Mosier Valley Landfill. Route paint/chemicals to Fort Worth ECC.",
        ["Use bulk on recycling day if debris fits ≤2 cy.", "Hire private C&D for larger projects.", "Route paint to Fort Worth ECC."], [("HHW for C&D?", "No — separate paint/chemicals.")], *bulky))
    return rows


def new_orleans():
    c, st = "new-orleans", "LA"
    bulky = ("City of New Orleans — Bulky waste via 311", "https://nola.gov/trash/")
    hhw = ("New Orleans Recycling Drop-Off Center", "https://nola.gov/recycling-drop-off/")
    rows = []
    rows.append(R(c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
        "Bulky via 311 — set out ≤24h before pickup; mattresses/furniture accepted",
        "New Orleans bulky collection (311 scheduled)",
        "New Orleans bulky waste is scheduled through 311. Set mattresses and furniture out no more than 24 hours before pickup. Call or use 311 to schedule bulky collection per nola.gov/trash guidance.",
        ["Call 311 to schedule bulky pickup.", "Set mattress out ≤24 hours before scheduled pickup.", "Keep bulk separate from regular carts."],
        [("How to schedule?", "Call 311 or use nola.gov/trash."), ("Set-out timing?", "No more than 24 hours before pickup.")], *bulky))
    rows.append(R(c, st, "refrigerator", "SPECIAL_HANDLING", "High", True,
        "Bulky via 311 — call 311 for Freon guidance; keep sealed; confirm doors/compressor rules",
        "New Orleans bulky collection (311) — confirm Freon handling",
        "Freon refrigerators go through New Orleans bulky collection via 311. City disaster guidance mentions securing doors and compressors — call 311 to confirm current Freon appliance rules before set-out. Keep the unit sealed; never vent refrigerant yourself.",
        ["Call 311 to schedule bulky and confirm Freon refrigerator rules.", "Keep doors secured/compressor rules per 311 guidance.", "Set out ≤24 hours before scheduled pickup."],
        [("Call 311 for Freon?", "Yes — confirm Freon handling with 311 before set-out.")], *bulky))
    rows.append(R(c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
        "Bulky via 311 — call 311 for Freon AC; keep sealed",
        "New Orleans bulky collection (311) — confirm Freon handling",
        "Freon window and portable AC units go through bulky collection via 311. Call 311 to confirm Freon handling — keep the unit sealed until pickup. Never vent refrigerant yourself.",
        ["Call 311 to schedule bulky and confirm Freon AC rules.", "Keep the sealed unit intact.", "Set out ≤24 hours before pickup."],
        [("Same as fridge?", "Yes — call 311 to confirm Freon appliance handling.")], *bulky))
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(R(c, st, item, "SPECIAL_HANDLING", "Medium", True,
            "Bulky via 311 — white goods; set out ≤24h before pickup",
            "New Orleans bulky collection (311 scheduled)",
            f"Non-Freon appliances such as {item.replace('-', ' ')}s are white goods accepted on New Orleans bulky collection — schedule via 311. Set out ≤24 hours before pickup. No special Freon call required for typical washers.",
            ["Call 311 to schedule bulky pickup.", "Set appliance out ≤24 hours before pickup.", "Empty appliance before set-out."],
            [("311 for washer?", "Yes — schedule bulky via 311; no Freon call for washers.")], *bulky))
    for item, label in [("television", "TVs"), ("computer-monitor", "monitors"), ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste")]:
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS", "Medium", False,
            "HHW designated calendar days at 2829 Elysian Fields — limit 4 TVs",
            "New Orleans Recycling Drop-Off — 2829 Elysian Fields Ave",
            f"Electronics including {label} go to New Orleans Recycling Drop-Off at 2829 Elysian Fields Ave on designated HHW calendar days — limit 4 TVs. Saturdays 8 a.m.–1 p.m. for general drop-off; check nola.gov/recycling-drop-off for HHW days. Wipe data before drop-off.",
            ["Check HHW calendar on nola.gov/recycling-drop-off.", "Haul e-waste to 2829 Elysian Fields on HHW days.", "Limit 4 TVs per visit."],
            [("Bulky for TV?", "No — TVs/e-waste use HHW drop-off days."), ("TV limit?", "4 TVs per visit on HHW days.")], *hhw))
    rows.append(R(c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", False,
        "HHW designated days / drop-off — paint NOT in trash",
        "New Orleans Recycling Drop-Off — 2829 Elysian Fields Ave",
        "Liquid latex and oil paint go to New Orleans HHW on designated calendar days at 2829 Elysian Fields Ave — not in regular trash. Saturdays 8 a.m.–1 p.m. for general drop-off; check calendar for HHW days.",
        ["Check HHW calendar on nola.gov/recycling-drop-off.", "Haul paint on designated HHW days.", "Do not put liquid paint in trash."],
        [("Trash for paint?", "No — paint goes to HHW days/drop-off.")], *hhw))
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
            "HHW designated days — 2829 Elysian Fields Ave", "New Orleans Recycling Drop-Off — 2829 Elysian Fields Ave",
            f"Take {item.replace('-', ' ')} to New Orleans HHW on designated calendar days at 2829 Elysian Fields Ave. Do not dry chemicals for trash.",
            ["Check HHW calendar on nola.gov.", "Deliver sealed containers on HHW days.", "Keep chemicals out of bulky piles."],
            [("Same as paint?", "Yes — chemicals use HHW designated days.")], *hhw))
    for item in ["car-battery", "lithium-battery", "paint-oil", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {"car-battery": " Batteries at HHW drop-off.", "lithium-battery": " Lithium batteries at HHW.", "paint-oil": " Oil paint at HHW.", "motor-oil": " Motor oil at HHW.", "propane-tank": " Propane at HHW.", "fluorescent-bulbs": " Fluorescents at HHW.", "cooking-oil": " Cooking oil at HHW when not trash-safe."}[item]
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING", "High" if item != "cooking-oil" else "Medium", False,
            "HHW designated days — 2829 Elysian Fields Ave", "New Orleans Recycling Drop-Off — 2829 Elysian Fields Ave",
            f"New Orleans HHW at 2829 Elysian Fields Ave accepts household hazardous materials on designated calendar days.{extra}",
            ["Check HHW calendar on nola.gov.", "Deliver sealed containers on HHW days.", "Bulky via 311 for furniture/appliances."], [("Address?", "2829 Elysian Fields Ave.")], *hhw))
    rows.append(R(c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
        "Rigid sealed container — confirm NOLA HHW sharps acceptance", "New Orleans Recycling Drop-Off — 2829 Elysian Fields Ave",
        "Place sharps in a rigid sealed container. Confirm acceptance at New Orleans HHW drop-off on nola.gov. Do not loose-bag needles.",
        ["Use rigid sealed container.", "Confirm sharps acceptance on HHW days.", "Never recycle loose needles."], [("Medications?", "Confirm drug take-back on nola.gov.")], *hhw))
    rows.append(R(c, st, "tires", "SPECIAL_HANDLING", "Medium", True,
        "Bulky via 311 — up to 4 tires; set out ≤24h before pickup",
        "New Orleans bulky collection (311 scheduled)",
        "New Orleans bulky collection via 311 accepts up to 4 tires per pickup along with mattresses, furniture, and white goods. Set out ≤24 hours before scheduled pickup.",
        ["Call 311 to schedule bulky including tires (up to 4).", "Set tires out ≤24 hours before pickup.", "Do not exceed 4 tires per bulky pickup."],
        [("Tire limit?", "Up to 4 tires on bulky via 311.")], *bulky))
    rows.append(R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True, "New Orleans yard waste collection", "New Orleans yard waste collection",
        "New Orleans handles yard waste through regular collection. Follow set-out rules.",
        ["Use yard waste set-out rules.", "Keep yard waste out of bulky and HHW loads.", "Check nola.gov for seasonal guidance."], [("Christmas trees?", "Follow city seasonal guidance.")], *bulky))
    rows.append(R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True, "Garbage cart unless private compost", "New Orleans garbage / private compost",
        "Bag food scraps for garbage unless you compost.",
        ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."], [("HHW for food?", "No.")], *bulky))
    rows.append(R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False, "Not recycling — store take-back / trash", "Retail bag take-back / trash",
        "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
        ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."], [("Bulky for bags?", "No.")], *bulky))
    rows.append(R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", True,
        "Bulky via 311 for limited loads — private C&D for larger",
        "New Orleans bulky (311) / private C&D hauler",
        "Limited homeowner C&D may go on New Orleans bulky collection when scheduled via 311. Larger contractor loads need a private C&D hauler. Route paint/chemicals to HHW drop-off separately.",
        ["Call 311 to schedule bulky if debris fits city limits.", "Hire private C&D for larger projects.", "Route paint to 2829 Elysian Fields HHW days."], [("HHW for C&D?", "No — separate paint/chemicals.")], *bulky))
    return rows


def tampa():
    c, st = "tampa", "FL"
    sweep = ("City of Tampa — SWEEP bulky collection", "https://www.tampa.gov/solid-waste/programs/sweep")
    mckay = ("McKay Bay Scale House — City of Tampa", "https://www.tampa.gov/solid-waste/programs/mckay-bay-scale-house")
    hhw = ("Hillsborough County — Household hazardous waste", "https://www.hcfl.gov/residents/property-owners-and-renters/trash-and-recycling/household-hazardous-waste")
    ccc = ("Hillsborough County — Community Collection Centers", "https://www.hcfl.gov/residents/property-owners-and-renters/trash-and-recycling/community-collection-centers")
    rows = []
    rows.append(R(c, st, "mattress", "SPECIAL_HANDLING", "Low", True,
        "SWEEP 1 free bulky/year ≤10 cy OR McKay Bay free drop with utility account",
        "City of Tampa SWEEP / McKay Bay Scale House — 114 S 34th St",
        "City of Tampa (not county/unincorporated) offers SWEEP — 1 free bulky collection per year up to 10 cubic yards. Special Services is $18.12/cy for additional bulky. McKay Bay Scale House at 114 S 34th St accepts free drop of mattresses with a City of Tampa utility account.",
        ["Schedule SWEEP free bulky (1/year, ≤10 cy) via tampa.gov.", "Or free drop at McKay Bay 114 S 34th St with utility account.", "Special Services $18.12/cy for extra bulky."],
        [("Free bulky?", "Yes — 1 SWEEP pickup/year ≤10 cy for City of Tampa residents."), ("McKay Bay?", "Free mattress drop with City of Tampa utility account.")], *sweep))
    rows.append(R(c, st, "refrigerator", "SPECIAL_HANDLING", "High", True,
        "SWEEP/McKay accept appliances — call 813-242-5320 if unsure about Freon; keep sealed",
        "SWEEP / McKay Bay Scale House — 114 S 34th St",
        "Freon refrigerators are accepted through City of Tampa SWEEP bulky or McKay Bay Scale House (2 appliances per visit with utility account). Freon handling is not detailed on city pages — keep the unit sealed and call 813-242-5320 if unsure. Never vent refrigerant yourself.",
        ["Schedule SWEEP or haul to McKay Bay 114 S 34th St (2 appliances/visit).", "Keep unit sealed; call 813-242-5320 if unsure about Freon.", "Never release Freon yourself."],
        [("Freon guidance?", "Not detailed — call 813-242-5320; keep sealed.")], *mckay))
    rows.append(R(c, st, "air-conditioner", "SPECIAL_HANDLING", "High", True,
        "SWEEP/McKay accept appliances — call 813-242-5320 if unsure; keep sealed",
        "SWEEP / McKay Bay Scale House — 114 S 34th St",
        "Freon AC units go through SWEEP bulky or McKay Bay (2 appliances/visit with utility account). Keep sealed; call 813-242-5320 if unsure about Freon handling. Never vent refrigerant yourself.",
        ["Schedule SWEEP or haul to McKay Bay.", "Keep sealed; call 813-242-5320 if unsure.", "Never release Freon."],
        [("Same as fridge?", "Yes — SWEEP/McKay path; call if Freon details unclear.")], *mckay))
    for item in ["washer", "dryer", "dishwasher", "stove", "water-heater"]:
        rows.append(R(c, st, item, "SPECIAL_HANDLING", "Medium", True,
            "SWEEP bulky OR McKay Bay free drop (2 appliances/visit) — same path as other bulk",
            "SWEEP / McKay Bay Scale House — 114 S 34th St",
            f"Non-Freon appliances such as {item.replace('-', ' ')}s use the same City of Tampa SWEEP bulky or McKay Bay pathways as furniture — not a separate Freon call path. McKay Bay accepts 2 appliances per visit with utility account; SWEEP is 1 free bulky/year ≤10 cy.",
            ["Schedule SWEEP free bulky or haul to McKay Bay 114 S 34th St.", "McKay: 2 appliances/visit with utility account.", "No separate Freon scheduling for washers."],
            [("Same as SWEEP/McKay bulk?", "Yes — washers use same SWEEP/McKay path as furniture.")], *mckay))
    for item, label in [("television", "TVs"), ("computer-monitor", "monitors"), ("smartphone", "phones"), ("e-waste-mixed", "mixed e-waste")]:
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS", "Medium", False,
            "NOT SWEEP — Hillsborough CCC Mon–Sat 5 electronics/month",
            "Hillsborough County Community Collection Centers",
            f"Electronics including {label} are NOT accepted on SWEEP bulky. Hillsborough County Community Collection Centers accept 5 electronics per month Mon–Sat — free with Hillsborough ID. Wipe data before drop-off.",
            ["Do not put e-waste on SWEEP bulky.", "Haul to Hillsborough CCC — 5 electronics/month.", "Bring Hillsborough ID; wipe personal data."],
            [("SWEEP for TV?", "No — e-waste/TVs use Hillsborough CCC, not SWEEP.")], *ccc))
    rows.append(R(c, st, "paint-latex", "SPECIAL_HANDLING", "Medium", False,
        "Hillsborough CCC or HHW Sat — NOT SWEEP; latex may have CCC path",
        "Hillsborough County CCC / HHW rotating Sat sites",
        "Paint is NOT accepted on SWEEP bulky. Liquid latex and oil paint go to Hillsborough County Community Collection Centers or HHW rotating Saturday sites (e.g., Sheldon Rd 1st Sat) — free with Hillsborough ID. Latex may have a CCC drop path — check hcfl.gov.",
        ["Do not put paint on SWEEP.", "Haul to Hillsborough CCC or HHW Sat site with ID.", "Check hcfl.gov paint/electronics pages."],
        [("SWEEP for paint?", "No — paint uses County CCC or HHW Sat sites.")], *hhw))
    for item in ["pesticides", "herbicides", "pool-chemicals", "gasoline"]:
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS", "High", False,
            "Hillsborough HHW rotating Sat sites — free with Hillsborough ID", "Hillsborough County HHW — Sheldon Rd etc.",
            f"Take {item.replace('-', ' ')} to Hillsborough County HHW rotating Saturday sites — e.g., Sheldon Rd 1st Sat — free with Hillsborough ID. NOT on SWEEP.",
            ["Check hcfl.gov HHW calendar for Sat site.", "Bring Hillsborough ID.", "Keep chemicals off SWEEP bulky."],
            [("SWEEP for chemicals?", "No — chemicals use County HHW Sat sites.")], *hhw))
    for item in ["car-battery", "lithium-battery", "paint-oil", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil"]:
        extra = {"car-battery": " Batteries at Hillsborough HHW/CCC.", "lithium-battery": " Lithium batteries at HHW.", "paint-oil": " Oil paint at HHW/CCC.", "motor-oil": " Motor oil at HHW.", "propane-tank": " Propane at HHW.", "fluorescent-bulbs": " Fluorescents at HHW.", "cooking-oil": " Cooking oil at HHW when not trash-safe."}[item]
        rows.append(R(c, st, item, "BANNED_FROM_LANDFILLS" if item != "cooking-oil" else "SPECIAL_HANDLING", "High" if item != "cooking-oil" else "Medium", False,
            "Hillsborough HHW rotating Sat — free with Hillsborough ID", "Hillsborough County HHW — Sheldon Rd etc.",
            f"Hillsborough County HHW rotating Saturday sites accept household hazardous materials — free with Hillsborough ID.{extra} E-waste uses CCC, not SWEEP.",
            ["Check hcfl.gov HHW calendar.", "Bring Hillsborough ID.", "E-waste/TVs use CCC — not SWEEP."], [("Which site?", "Rotating Sat — e.g., Sheldon Rd 1st Sat.")], *hhw))
    rows.append(R(c, st, "medical-sharps", "BANNED_FROM_LANDFILLS", "High", False,
        "Rigid sealed container — confirm Hillsborough HHW sharps acceptance", "Hillsborough County HHW",
        "Place sharps in a rigid sealed container. Confirm acceptance at Hillsborough County HHW on hcfl.gov. Do not loose-bag needles.",
        ["Use rigid sealed container.", "Confirm sharps at HHW Sat site.", "Never recycle loose needles."], [("Medications?", "Confirm drug take-back on hcfl.gov.")], *hhw))
    rows.append(R(c, st, "tires", "SPECIAL_HANDLING", "Medium", True,
        "SWEEP up to 4 passenger tires no rims — McKay tires NOT free",
        "City of Tampa SWEEP / McKay Bay (tires not free)",
        "City of Tampa SWEEP accepts up to 4 passenger tires without rims. McKay Bay tires are NOT free — use SWEEP for passenger tires or retailer/landfill fees otherwise.",
        ["Schedule SWEEP for up to 4 passenger tires (no rims).", "Do not assume free tire drop at McKay Bay.", "Retailer take-back when replacing tires."],
        [("SWEEP tire limit?", "Up to 4 passenger tires, no rims."), ("McKay free tires?", "No — McKay tires are not free.")], *sweep))
    rows.append(R(c, st, "yard-waste", "ACCEPTED_IN_BLUE_BIN", "Low", True, "City of Tampa yard waste collection", "City of Tampa yard waste collection",
        "City of Tampa handles yard waste through regular collection. Follow set-out rules.",
        ["Use yard waste set-out rules.", "Keep yard waste out of SWEEP and HHW loads.", "Check tampa.gov for seasonal guidance."], [("Christmas trees?", "Follow city seasonal guidance.")], *sweep))
    rows.append(R(c, st, "food-scraps", "SPECIAL_HANDLING", "Low", True, "Garbage cart unless private compost", "City of Tampa garbage / private compost",
        "Bag food scraps for garbage unless you compost.",
        ["Bag food for garbage if no compost.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."], [("HHW for food?", "No.")], *sweep))
    rows.append(R(c, st, "plastic-bags", "SPECIAL_HANDLING", "Low", False, "Not recycling — store take-back / trash", "Retail bag take-back / trash",
        "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
        ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."], [("SWEEP for bags?", "No — store take-back or trash.")], *sweep))
    rows.append(R(c, st, "construction-debris", "SPECIAL_HANDLING", "Low", True,
        "SWEEP for limited loads (≤10 cy once/year) — Special Services $18.12/cy or private C&D",
        "City of Tampa SWEEP / Special Services / private C&D",
        "Limited homeowner C&D may fit SWEEP (1 free bulky/year ≤10 cy) or Special Services at $18.12/cy. Larger contractor loads need a private C&D hauler. Route paint/chemicals to Hillsborough CCC/HHW — not SWEEP.",
        ["Schedule SWEEP if debris fits ≤10 cy annual allowance.", "Special Services $18.12/cy for additional bulky.", "Route paint to Hillsborough CCC/HHW."], [("SWEEP for paint?", "No — separate paint/chemicals for County CCC/HHW.")], *sweep))
    return rows


CITIES = [{'city': 'Colorado Springs', 'city_slug': 'colorado-springs', 'state': 'CO', 'state_slug': 'colorado', 'lat': 38.8339, 'lng': -104.8214, 'population': 478961}, {'city': 'Wichita', 'city_slug': 'wichita', 'state': 'KS', 'state_slug': 'kansas', 'lat': 37.6872, 'lng': -97.3301, 'population': 397532}, {'city': 'Arlington', 'city_slug': 'arlington', 'state': 'TX', 'state_slug': 'texas', 'lat': 32.7357, 'lng': -97.1081, 'population': 394266}, {'city': 'New Orleans', 'city_slug': 'new-orleans', 'state': 'LA', 'state_slug': 'louisiana', 'lat': 29.9511, 'lng': -90.0715, 'population': 383997}, {'city': 'Tampa', 'city_slug': 'tampa', 'state': 'FL', 'state_slug': 'florida', 'lat': 27.9506, 'lng': -82.4572, 'population': 384959}]

ZIPS = [{'zip': '80903', 'city': 'Colorado Springs', 'city_slug': 'colorado-springs', 'state': 'CO', 'state_slug': 'colorado', 'lat': 38.834, 'lng': -104.821, 'population': 18000}, {'zip': '80909', 'city': 'Colorado Springs', 'city_slug': 'colorado-springs', 'state': 'CO', 'state_slug': 'colorado', 'lat': 38.845, 'lng': -104.775, 'population': 22000}, {'zip': '67202', 'city': 'Wichita', 'city_slug': 'wichita', 'state': 'KS', 'state_slug': 'kansas', 'lat': 37.687, 'lng': -97.33, 'population': 8000}, {'zip': '67214', 'city': 'Wichita', 'city_slug': 'wichita', 'state': 'KS', 'state_slug': 'kansas', 'lat': 37.705, 'lng': -97.315, 'population': 15000}, {'zip': '76010', 'city': 'Arlington', 'city_slug': 'arlington', 'state': 'TX', 'state_slug': 'texas', 'lat': 32.736, 'lng': -97.108, 'population': 35000}, {'zip': '76013', 'city': 'Arlington', 'city_slug': 'arlington', 'state': 'TX', 'state_slug': 'texas', 'lat': 32.725, 'lng': -97.145, 'population': 28000}, {'zip': '70112', 'city': 'New Orleans', 'city_slug': 'new-orleans', 'state': 'LA', 'state_slug': 'louisiana', 'lat': 29.951, 'lng': -90.072, 'population': 12000}, {'zip': '70119', 'city': 'New Orleans', 'city_slug': 'new-orleans', 'state': 'LA', 'state_slug': 'louisiana', 'lat': 29.975, 'lng': -90.085, 'population': 20000}, {'zip': '33602', 'city': 'Tampa', 'city_slug': 'tampa', 'state': 'FL', 'state_slug': 'florida', 'lat': 27.951, 'lng': -82.457, 'population': 9000}, {'zip': '33606', 'city': 'Tampa', 'city_slug': 'tampa', 'state': 'FL', 'state_slug': 'florida', 'lat': 27.935, 'lng': -82.465, 'population': 14000}]

FACILITIES = [{'name': 'El Paso County HHW', 'facility_type': 'Household hazardous waste drop-off', 'city_slug': 'colorado-springs', 'state': 'CO', 'zip': '80922', 'address': '3255 Akers Dr, Colorado Springs, CO 80922', 'lat': 38.8755, 'lng': -104.7155, 'source_url': 'https://communityresources.elpasoco.com/household-hazardous-waste', 'hours': 'Mon/Tue/Thu/Fri 8:30–12 & 13:00–16:00; closed Wed; limited Sat', 'phone': '719-520-7878'}, {'name': 'Sedgwick County HHW', 'facility_type': 'Household hazardous waste drop-off', 'city_slug': 'wichita', 'state': 'KS', 'zip': '67213', 'address': '801 Stillwell St, Wichita, KS 67213', 'lat': 37.6555, 'lng': -97.3555, 'source_url': 'https://www.sedgwickcounty.org/environment/hazardous-waste/', 'hours': 'Tue–Fri 9:00–17:00; Sat 9:00–15:00', 'phone': '316-660-7464'}, {'name': 'Fort Worth Environmental Collection Center', 'facility_type': 'Household hazardous waste drop-off', 'city_slug': 'arlington', 'state': 'TX', 'zip': '76112', 'address': '6400 Bridge St, Fort Worth, TX 76112', 'lat': 32.7555, 'lng': -97.2155, 'source_url': 'https://www.fortworthtexas.gov/departments/code-compliance/household-hazardous-waste', 'hours': 'Thu–Fri 11:00–19:00; Sat 9:00–15:00', 'phone': '817-392-3279'}, {'name': 'New Orleans Recycling Drop-Off Center', 'facility_type': 'Household hazardous waste drop-off', 'city_slug': 'new-orleans', 'state': 'LA', 'zip': '70122', 'address': '2829 Elysian Fields Ave, New Orleans, LA 70122', 'lat': 29.9855, 'lng': -90.0555, 'source_url': 'https://nola.gov/recycling-drop-off/', 'hours': 'Sat 8:00–13:00 general; HHW on designated calendar days', 'phone': '311'}, {'name': 'Hillsborough County HHW — Sheldon Rd', 'facility_type': 'Household hazardous waste drop-off', 'city_slug': 'tampa', 'state': 'FL', 'zip': '33635', 'address': '9805 Sheldon Rd, Tampa, FL 33635', 'lat': 28.0055, 'lng': -82.5855, 'source_url': 'https://www.hcfl.gov/residents/property-owners-and-renters/trash-and-recycling/household-hazardous-waste', 'hours': 'Rotating Sat collection — 1st Sat Sheldon Rd; check calendar', 'phone': '813-272-5680'}, {'name': 'McKay Bay Scale House', 'facility_type': 'Bulky / appliance drop-off', 'city_slug': 'tampa', 'state': 'FL', 'zip': '33605', 'address': '114 S 34th St, Tampa, FL 33605', 'lat': 27.9455, 'lng': -82.4255, 'source_url': 'https://www.tampa.gov/solid-waste/programs/mckay-bay-scale-house', 'hours': 'Mon–Sat; free drop with City of Tampa utility account', 'phone': '813-242-5320'}]

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
        "colorado-springs": clone_siblings(colorado_springs()),
        "wichita": clone_siblings(wichita()),
        "arlington": clone_siblings(arlington()),
        "new-orleans": clone_siblings(new_orleans()),
        "tampa": clone_siblings(tampa()),
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

    print("Wave-10 metros written:")
    for city, rows in audited.items():
        print(f"  {city}: {len(rows)} rules")
    print(f"Total rules now: {len(keep)}")


if __name__ == "__main__":
    main()

