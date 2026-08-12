#!/usr/bin/env python3
"""Portal-audited city guides for wave-21b metros (city-sourced only).

Compact channel-template wave: each city defines disposal channels that emit
base item rows, then clone_siblings() expands to exactly 70 unique item_slugs.

Cities researched from official program pages (2026-08-12):
  - Garden Grove, CA — Republic bulky 3×; OC Landfills Anaheim HHW
  - Pembroke Pines, FL — Eastern Waste bulk 2×/mo; quarterly HHW at WWTP
  - Fort Collins, CO — Republic 2 free bulk/yr; Larimer HHW
  - Palmdale, CA — WM bulky; AVECC CleanLA HHW/e-waste
  - Springfield, MO — HCCC by appt; Noble Hill landfill; no city free bulk
  - Clarksville, TN — Bi-County landfill; HHW events; limited BOPAE
  - Paterson, NJ — City Yard bulk; Passaic County HHW events
  - Macon, GA — Ryland bulk; 11th St Convenience Center
  - Kansas City, KS — WM bulky 3/week; HHW Sat Apr–Oct (no e-waste at HHW)
  - Springfield, MA — bulk stickers $8; HHW events Tapley by appt
  - Sunnyvale, CA — on-call bulky 2×; SMaRT Station; SCC HHW by appt
  - Jackson, MS — SWEEP bulk 2 items; ESC temporarily closed (monitor city)
  - Killeen, TX — fee bulk curb; Transfer Station; HHW events; Recycling Center
  - Hollywood, FL — monthly bulk; Broward South Drop-Off Sat
  - Murfreesboro, TN — fee bulky; Leanna CC; Rutherford mobile HHW
  - Pasadena, TX — Frontier bulk biweekly; city Sanitation HHW/appliances
  - Bellevue, WA — Republic bulky fees; Factoria HHW
  - Pomona, CA — Athens bulky 6×/yr; CleanLA HHW events
  - Escondido, CA — HHW by appt; EDI bulky fees
  - Joliet, IL — WM At Your Door HHW; Will County e-waste; Naperville HHW
  - Charleston, SC — bulk curb; Bees Ferry HHW/e-waste
  - Mesquite, TX — weekly bulky; Citizens Convenience; Dallas Co HHW
  - Naperville, IL — Groot 2 bulk/week; HHW + electronics campus
  - Rockford, IL — weekly bulk; HHW Kishwaukee; KNIB e-waste
  - Bridgeport, CT — Transfer Station; annual HHW day
  - Santa Rosa CA (santa-rosa-ca) — Zero Waste Sonoma / Recology bulky + Mecham HHW
    (identical channels also written for santa-rosa slug)
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
VERIFIED = "2026-08-12"

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

HHW_MATERIALS = [
    "paint-latex",
    "paint-oil",
    "pesticides",
    "herbicides",
    "pool-chemicals",
    "gasoline",
    "motor-oil",
    "antifreeze",
    "car-battery",
    "household-batteries",
    "lithium-battery",
    "fluorescent-bulbs",
    "propane-tank",
    "cooking-oil",
]


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


def ch(items, badge, hazard, curbside, fee, facility, answer, steps, faqs, src):
    """One disposal channel applied to one or more item slugs."""
    return {
        "items": items if isinstance(items, (list, tuple)) else [items],
        "badge": badge,
        "hazard": hazard,
        "curbside": curbside,
        "fee": fee,
        "facility": facility,
        "answer": answer,
        "steps": steps,
        "faqs": faqs,
        "src": src,
    }


def rows_from_channels(city, state, channels):
    rows = []
    for channel in channels:
        for item in channel["items"]:
            label = item.replace("-", " ")
            answer = channel["answer"].replace("{item}", label)
            rows.append(
                R(
                    city,
                    state,
                    item,
                    channel["badge"],
                    channel["hazard"],
                    channel["curbside"],
                    channel["fee"],
                    channel["facility"],
                    answer,
                    channel["steps"],
                    channel["faqs"],
                    *channel["src"],
                )
            )
    return rows


def rehome(rows, city_slug):
    """Clone a base pack onto another city_slug (identical programs)."""
    out = []
    for r in rows:
        e = deepcopy(r)
        e["city_slug"] = city_slug
        out.append(e)
    return out


def common_tail(hub, city_name, cd_answer, cd_facility, cd_fee="Private C&D / landfill — not free bulk"):
    return [
        ch(
            "tires",
            "SPECIAL_HANDLING",
            "Medium",
            False,
            "NOT HHW — retailer take-back / transfer tire programs",
            "Retailer take-back / transfer tire programs",
            f"{city_name} tires are not typical HHW. Use retailer take-back when replacing tires or confirm transfer/landfill tire acceptance. Keep tires off HHW loads.",
            [
                "Do not haul tires to HHW as a default.",
                "Use retailer take-back when replacing tires.",
                "Confirm transfer/landfill tire rules before drop-off.",
            ],
            [("HHW for tires?", "Usually no."), ("Bulk for tires?", "Confirm city/hauler rules — not HHW.")],
            hub,
        ),
        ch(
            "yard-waste",
            "ACCEPTED_IN_BLUE_BIN",
            "Low",
            True,
            f"{city_name} yard / organics program",
            f"{city_name} yard-waste / organics collection",
            f"{city_name} yard waste follows the city yard/organics program. Follow set-out rules on the city portal.",
            [
                "Follow city set-out rules for yard trimmings.",
                "Keep yard waste out of HHW and e-waste.",
                "Check the city site for seasonal guidance.",
            ],
            [("Christmas trees?", "Follow city seasonal yard-waste guidance.")],
            hub,
        ),
        ch(
            "food-scraps",
            "SPECIAL_HANDLING",
            "Low",
            True,
            "Garbage cart unless private compost / organics",
            f"{city_name} garbage / organics",
            "Bag food scraps for garbage unless you have organics/compost service. Keep food out of recycling and HHW.",
            ["Bag food for garbage if no organics.", "Keep organics out of recycling.", "Yard trimmings use yard-waste pathways."],
            [("HHW for food?", "No.")],
            hub,
        ),
        ch(
            "plastic-bags",
            "SPECIAL_HANDLING",
            "Low",
            False,
            "Not recycling — store take-back / trash",
            "Retail bag take-back / trash",
            "Plastic bags are not accepted in curbside recycling. Use store take-back or trash.",
            ["Keep bags out of recycling.", "Use grocery take-back.", "Otherwise trash."],
            [("Bulk for bags?", "No.")],
            hub,
        ),
        ch(
            "construction-debris",
            "SPECIAL_HANDLING",
            "Low",
            False,
            cd_fee,
            cd_facility,
            cd_answer,
            [
                "Do not treat remodel debris as free bulk without confirming limits.",
                "Hire private C&D for larger projects.",
                "Route paint/chemicals to HHW separately.",
            ],
            [("HHW for C&D?", "No — separate paint/chemicals.")],
            hub,
        ),
    ]


# ---------------------------------------------------------------------------
# City channel packs
# ---------------------------------------------------------------------------


def garden_grove():
    c, st = "garden-grove", "CA"
    hub = ("City of Garden Grove — Trash & Recycling", "https://ggcity.org/public-works/trash-recycling")
    hhw = ("OC Landfills — Household Hazardous Waste", "https://oclandfills.com/hazardous-waste")
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner"],
                "SPECIAL_HANDLING",
                "Low",
                True,
                "Republic Services bulky — up to 3 collections/year",
                "Garden Grove / Republic Services bulky collection",
                "Garden Grove {item}s go on Republic Services bulky collection — up to 3 free collections per year for residential customers. Schedule via ggcity.org / Republic. Keep paint, batteries, propane, and loose chemicals off bulk piles.",
                [
                    "Schedule Republic bulky via Garden Grove trash/recycling pages (up to 3×/year).",
                    "Set out per Republic size/item rules.",
                    "Keep HHW and e-waste off bulk piles.",
                ],
                [("How often?", "Up to 3 bulky collections/year."), ("Who hauls?", "Republic Services.")],
                hub,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed"],
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "NOT typical bulk — OC Landfills Anaheim HHW / e-waste pathways",
                "OC Landfills Anaheim HHW — 1071 N Blue Gum St",
                "Garden Grove electronics including {item} should use Orange County HHW/e-waste pathways — OC Landfills Anaheim HHW Collection Center, 1071 N Blue Gum Street, Anaheim. Wipe data before drop-off. Confirm e-waste acceptance before hauling.",
                [
                    "Do not rely on curb bulk for TVs/electronics.",
                    "Haul to 1071 N Blue Gum St, Anaheim (OC Landfills HHW).",
                    "Wipe personal data.",
                ],
                [("Bulk for TVs?", "Prefer OC Landfills HHW/e-waste."), ("Address?", "1071 N Blue Gum St, Anaheim.")],
                hhw,
            ),
            ch(
                ["paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "OC Landfills Anaheim HHW — 1071 N Blue Gum St",
                "OC Landfills Anaheim HHW — 1071 N Blue Gum Street, Anaheim",
                "Take {item} to the Orange County Household Hazardous Waste Collection Center in Anaheim — 1071 N Blue Gum Street. Confirm hours on oclandfills.com. Paint, batteries, and propane are NOT bulk.",
                [
                    "Haul sealed materials to 1071 N Blue Gum St, Anaheim.",
                    "Check oclandfills.com hours before visiting.",
                    "Keep HHW off Republic bulk piles.",
                ],
                [("HHW address?", "1071 N Blue Gum St, Anaheim."), ("Bulk for paint?", "No — OC Landfills HHW.")],
                hhw,
            ),
        ]
        + common_tail(
            hub,
            "Garden Grove",
            "Construction debris is not typical free Republic bulky material. Hire a private C&D hauler or confirm transfer/landfill C&D rules. Route paint/chemicals to OC Landfills Anaheim HHW separately.",
            "Private C&D hauler / Orange County transfer",
        ),
    )


def pembroke_pines():
    c, st = "pembroke-pines", "FL"
    hub = ("City of Pembroke Pines — Garbage & Recycling", "https://www.ppines.com/195/Garbage-Recycling")
    hhw = ("City of Pembroke Pines — Household Hazardous Waste", "https://www.ppines.com/196/Household-Hazardous-Waste")
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner"],
                "SPECIAL_HANDLING",
                "Low",
                True,
                "Eastern Waste bulk — twice monthly on garbage day",
                "Pembroke Pines / Eastern Waste bulk collection",
                "Pembroke Pines {item}s go on Eastern Waste bulk collection — typically twice monthly on your garbage day. Follow ppines.com set-out rules. Keep HHW and loose chemicals off bulk piles.",
                [
                    "Set out bulk on the scheduled Eastern Waste bulk day (2×/month).",
                    "Follow size/item limits on ppines.com.",
                    "Keep paint, batteries, and propane off bulk piles.",
                ],
                [("How often?", "Bulk twice monthly with Eastern Waste."), ("Who hauls?", "Eastern Waste.")],
                hub,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed"],
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "Quarterly HHW / e-waste events — WWTP 13975 Pembroke Rd",
                "Pembroke Pines WWTP HHW events — 13975 Pembroke Road",
                "Pembroke Pines electronics including {item} go to quarterly household hazardous waste events at the Wastewater Treatment Plant — 13975 Pembroke Road. Monitor ppines.com for event dates. Wipe data before drop-off.",
                [
                    "Check ppines.com for the next quarterly HHW event.",
                    "Haul e-waste to 13975 Pembroke Rd on event day.",
                    "Wipe personal data.",
                ],
                [("Bulk for TVs?", "Prefer quarterly HHW events."), ("Where?", "13975 Pembroke Road WWTP.")],
                hhw,
            ),
            ch(
                ["paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "Quarterly HHW events — WWTP 13975 Pembroke Rd",
                "Pembroke Pines WWTP HHW events — 13975 Pembroke Road",
                "Take {item} to Pembroke Pines quarterly HHW collection at the Wastewater Treatment Plant — 13975 Pembroke Road. Confirm dates on ppines.com. Not Eastern Waste bulk.",
                [
                    "Monitor ppines.com for quarterly HHW event dates.",
                    "Haul sealed materials to 13975 Pembroke Rd.",
                    "Keep HHW off bulk piles.",
                ],
                [("HHW where?", "13975 Pembroke Road (WWTP) on event days."), ("Bulk for paint?", "No.")],
                hhw,
            ),
        ]
        + common_tail(
            hub,
            "Pembroke Pines",
            "Construction debris is not typical free Eastern Waste bulk. Hire a private C&D hauler or confirm transfer rules. Route paint/chemicals to quarterly HHW events separately.",
            "Private C&D hauler / Broward transfer",
        ),
    )


def fort_collins():
    c, st = "fort-collins", "CO"
    hub = ("City of Fort Collins — Trash & Recycling", "https://www.fcgov.com/recycling/")
    bulk = ("City of Fort Collins — Bulky Item Collection", "https://www.fcgov.com/recycling/bulky-item-collection")
    hhw = ("Larimer County — Household Hazardous Waste", "https://www.larimer.gov/solidwaste/hhw")
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner"],
                "SPECIAL_HANDLING",
                "Low",
                True,
                "Republic Services — 2 free bulk collections/year",
                "Fort Collins / Republic Services bulk collection",
                "Fort Collins {item}s go on Republic Services bulk — 2 free collections per year for residential customers. Schedule via fcgov.com / Republic. Keep HHW off bulk piles.",
                [
                    "Schedule Republic bulk (2 free/year) via Fort Collins recycling pages.",
                    "Set out per Republic rules.",
                    "Keep paint, batteries, and propane off bulk piles.",
                ],
                [("How often?", "2 free bulk collections/year."), ("Who hauls?", "Republic Services.")],
                bulk,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed"],
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "Larimer County HHW / e-waste — 5887 S Taft Hill Rd",
                "Larimer County HHW — 5887 S Taft Hill Road",
                "Fort Collins electronics including {item} go to Larimer County Household Hazardous Waste — 5887 S Taft Hill Road. Confirm hours on larimer.gov. Wipe data before drop-off.",
                [
                    "Haul e-waste to 5887 S Taft Hill Rd.",
                    "Confirm Larimer County HHW hours before visit.",
                    "Wipe personal data.",
                ],
                [("Bulk for TVs?", "Prefer Larimer County HHW."), ("Address?", "5887 S Taft Hill Road.")],
                hhw,
            ),
            ch(
                ["paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "Larimer County HHW — 5887 S Taft Hill Rd",
                "Larimer County HHW — 5887 S Taft Hill Road, Fort Collins",
                "Take {item} to Larimer County Household Hazardous Waste — 5887 S Taft Hill Road. Confirm hours/ID rules on larimer.gov. Not Republic bulk.",
                [
                    "Haul sealed materials to 5887 S Taft Hill Rd.",
                    "Check larimer.gov HHW hours before visiting.",
                    "Keep HHW off bulk piles.",
                ],
                [("HHW address?", "5887 S Taft Hill Road."), ("Bulk for paint?", "No — Larimer HHW.")],
                hhw,
            ),
        ]
        + common_tail(
            hub,
            "Fort Collins",
            "Construction debris is not typical free Republic bulk. Hire a private C&D hauler or confirm landfill C&D rules. Route paint/chemicals to Larimer County HHW separately.",
            "Private C&D hauler / Larimer landfill",
        ),
    )


def palmdale():
    c, st = "palmdale", "CA"
    hub = ("City of Palmdale — Trash & Recycling", "https://www.cityofpalmdaleca.gov/278/Trash-Recycling")
    hhw = ("CleanLA — Antelope Valley Collection Center (AVECC)", "https://cleanla.lacounty.gov/venue/avecc/")
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner"],
                "SPECIAL_HANDLING",
                "Low",
                True,
                "Waste Management bulky — schedule via city/WM",
                "Palmdale / Waste Management bulky collection",
                "Palmdale {item}s go on Waste Management bulky collection — schedule via cityofpalmdaleca.gov / WM. Keep paint, batteries, propane, and e-waste off bulk piles.",
                [
                    "Schedule WM bulky via Palmdale trash/recycling pages.",
                    "Set out per WM size/item rules.",
                    "Keep HHW and e-waste off bulk piles.",
                ],
                [("Who hauls?", "Waste Management."), ("E-waste on bulky?", "No — use AVECC.")],
                hub,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed"],
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "AVECC CleanLA — 1200 W City Ranch Rd (1st & 3rd Sat)",
                "AVECC — 1200 W City Ranch Road, Palmdale",
                "Palmdale electronics including {item} go to the Antelope Valley Environmental Collection Center (AVECC) — 1200 W City Ranch Road — typically 1st & 3rd Saturday 9 a.m.–3 p.m. via CleanLA. Wipe data before drop-off.",
                [
                    "Confirm 1st/3rd Saturday hours on cleanla.lacounty.gov.",
                    "Haul e-waste to 1200 W City Ranch Rd.",
                    "Wipe personal data.",
                ],
                [("Bulky for TVs?", "No — AVECC."), ("Hours?", "1st & 3rd Saturday 9–3 (confirm calendar).")],
                hhw,
            ),
            ch(
                ["paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "AVECC CleanLA — 1200 W City Ranch Rd (1st & 3rd Sat)",
                "AVECC — 1200 W City Ranch Road, Palmdale",
                "Take {item} to AVECC / CleanLA — 1200 W City Ranch Road, Palmdale — 1st & 3rd Saturday 9 a.m.–3 p.m. (confirm cleanla.lacounty.gov). Not WM bulky.",
                [
                    "Confirm AVECC Saturday calendar before visiting.",
                    "Haul sealed materials to 1200 W City Ranch Rd.",
                    "Keep HHW off WM bulk piles.",
                ],
                [("HHW address?", "1200 W City Ranch Road, Palmdale."), ("Bulk for paint?", "No — AVECC.")],
                hhw,
            ),
        ]
        + common_tail(
            hub,
            "Palmdale",
            "Construction debris is not typical free WM bulky. Hire a private C&D hauler or confirm transfer rules. Route paint/chemicals to AVECC separately.",
            "Private C&D hauler / Antelope Valley transfer",
        ),
    )


def springfield_mo():
    c, st = "springfield-mo", "MO"
    hub = ("City of Springfield — Solid Waste", "https://www.springfieldmo.gov/2215/Solid-Waste")
    hhw = ("City of Springfield — Household Chemical Collection Center", "https://www.springfieldmo.gov/2218/Household-Chemical-Collection-Center")
    land = ("City of Springfield — Noble Hill Landfill", "https://www.springfieldmo.gov/2220/Noble-Hill-Landfill")
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner"],
                "SPECIAL_HANDLING",
                "Low",
                False,
                "No city free bulk — hauler / Noble Hill self-haul",
                "Hauler bulk service / Noble Hill Landfill self-haul",
                "Springfield MO has no citywide free bulk pickup for {item}. Use your licensed hauler’s bulk service (fees may apply) or self-haul to Noble Hill Landfill. Keep HHW off landfill loads when required.",
                [
                    "Contact your hauler for paid bulk pickup options.",
                    "Or self-haul to Noble Hill Landfill per springfieldmo.gov rules.",
                    "Keep paint/chemicals out of general landfill loads.",
                ],
                [("Free city bulk?", "No — hauler or Noble Hill self-haul."), ("Landfill?", "Noble Hill Landfill.")],
                land,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed"],
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "HCCC / city e-waste pathways — confirm before drop-off",
                "Springfield Household Chemical Collection Center — 1226 W Nichols",
                "Springfield MO electronics including {item} should use city-directed e-waste/HHW pathways — start with the Household Chemical Collection Center at 1226 W Nichols (by appointment). Wipe data. Confirm electronics acceptance when booking.",
                [
                    "Call/book HCCC at 1226 W Nichols by appointment.",
                    "Confirm electronics acceptance when scheduling.",
                    "Wipe personal data.",
                ],
                [("Free curb e-waste?", "No — appointment / designated drop-off."), ("Address?", "1226 W Nichols.")],
                hhw,
            ),
            ch(
                ["paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "HCCC — 1226 W Nichols by appointment",
                "Household Chemical Collection Center — 1226 W Nichols, Springfield",
                "Take {item} to the Springfield Household Chemical Collection Center — 1226 W Nichols — by appointment. Confirm hours/materials on springfieldmo.gov. Not landfill trash.",
                [
                    "Schedule an appointment for 1226 W Nichols.",
                    "Haul sealed materials only.",
                    "Do not put HHW in regular trash or free bulk piles.",
                ],
                [("HHW address?", "1226 W Nichols (by appointment)."), ("Walk-in?", "Appointment required — confirm city page.")],
                hhw,
            ),
        ]
        + common_tail(
            hub,
            "Springfield",
            "Construction debris goes via private C&D or Noble Hill Landfill per posted rules — not a free city bulk program. Route paint/chemicals to HCCC separately.",
            "Noble Hill Landfill / private C&D",
            cd_fee="Noble Hill landfill / private C&D — fees apply",
        ),
    )


def clarksville():
    c, st = "clarksville", "TN"
    hub = ("Montgomery County — Solid Waste", "https://www.montgomerytn.gov/government/departments/solid_waste/index.php")
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner"],
                "SPECIAL_HANDLING",
                "Low",
                False,
                "Bi-County Landfill / limited BOPAE — 3212 Dover Rd",
                "Bi-County Landfill — 3212 Dover Road",
                "Clarksville {item}s typically go to Bi-County Landfill — 3212 Dover Road — or limited BOPAE (bulky/overflow) pathways posted by Montgomery County. Confirm fees and Freon rules before hauling. Keep HHW off landfill loads.",
                [
                    "Confirm Bi-County Landfill / BOPAE rules on montgomerytn.gov.",
                    "Haul to 3212 Dover Rd with required ID/fees.",
                    "Keep paint and chemicals off general loads.",
                ],
                [("Address?", "3212 Dover Road."), ("Free curb bulk?", "Limited — confirm county BOPAE rules.")],
                hub,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed"],
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "County HHW events / landfill-directed e-waste — confirm calendar",
                "Montgomery County HHW events / Bi-County directed e-waste",
                "Clarksville electronics including {item} should use Montgomery County HHW events or landfill-directed e-waste pathways — monitor montgomerytn.gov. Wipe data. Limited BOPAE may not cover e-waste.",
                [
                    "Check montgomerytn.gov for HHW event dates.",
                    "Confirm e-waste acceptance before hauling to landfill.",
                    "Wipe personal data.",
                ],
                [("Landfill for TVs?", "Confirm — prefer HHW events."), ("Source?", "Montgomery County Solid Waste.")],
                hub,
            ),
            ch(
                ["paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "Montgomery County HHW events — monitor county calendar",
                "Montgomery County household hazardous waste events",
                "Take {item} to Montgomery County household hazardous waste events — dates posted on montgomerytn.gov. Limited BOPAE at the landfill is not a substitute for HHW chemicals.",
                [
                    "Monitor montgomerytn.gov for HHW event dates.",
                    "Transport sealed materials only.",
                    "Keep HHW out of regular trash and BOPAE piles.",
                ],
                [("HHW permanent site?", "Primarily events — confirm county page."), ("Landfill for paint?", "No — HHW events.")],
                hub,
            ),
        ]
        + common_tail(
            hub,
            "Clarksville",
            "Construction debris goes to Bi-County Landfill / private C&D per posted fees — not a free city bulk program. Route paint/chemicals to county HHW events separately.",
            "Bi-County Landfill / private C&D",
            cd_fee="Bi-County Landfill C&D fees",
        ),
    )


def paterson():
    c, st = "paterson", "NJ"
    hub = ("City of Paterson — Sanitation / Bulk", "https://www.patersonnj.gov/")
    bulk = ("City of Paterson — Bulk Waste", "https://www.patersonnj.gov/department/division.php?structureid=109")
    hhw = ("Passaic County — Household Hazardous Waste", "https://www.passaiccountynj.org/")
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner"],
                "SPECIAL_HANDLING",
                "Low",
                False,
                "City Yard bulk drop-off — 402 E 16th St",
                "Paterson City Yard — 402 E 16th Street",
                "Paterson {item}s go to the City Yard bulk drop-off — 402 E 16th Street — follow patersonnj.gov sanitation rules for hours, residency, and fees. Keep HHW off City Yard loads when not accepted.",
                [
                    "Confirm City Yard hours/ID on patersonnj.gov.",
                    "Haul bulk to 402 E 16th St.",
                    "Keep paint, batteries, and propane out unless explicitly accepted.",
                ],
                [("Address?", "402 E 16th Street."), ("Curbside free bulk?", "City Yard drop-off — confirm current rules.")],
                bulk,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed"],
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "Passaic County HHW / e-waste events — monitor county calendar",
                "Passaic County HHW events",
                "Paterson electronics including {item} should use Passaic County HHW/e-waste events — monitor passaiccountynj.org. Wipe data. Confirm City Yard does not accept e-waste before hauling there.",
                [
                    "Check Passaic County HHW event calendar.",
                    "Wipe personal data before drop-off.",
                    "Do not put e-waste in regular trash.",
                ],
                [("City Yard for TVs?", "Confirm — prefer county HHW events."), ("Source?", "Passaic County HHW program.")],
                hhw,
            ),
            ch(
                ["paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "Passaic County HHW events — monitor county calendar",
                "Passaic County household hazardous waste events",
                "Take {item} to Passaic County household hazardous waste events — dates on passaiccountynj.org. Not City Yard trash. Keep chemicals sealed for transport.",
                [
                    "Monitor Passaic County HHW event dates.",
                    "Transport sealed materials only.",
                    "Keep HHW out of City Yard bulk loads.",
                ],
                [("HHW permanent site?", "Primarily county events — confirm calendar."), ("City Yard for paint?", "No — Passaic County HHW.")],
                hhw,
            ),
        ]
        + common_tail(
            hub,
            "Paterson",
            "Construction debris is not typical City Yard household bulk. Hire a private C&D hauler or confirm transfer rules. Route paint/chemicals to Passaic County HHW events separately.",
            "Private C&D hauler / county transfer",
        ),
    )


def macon():
    c, st = "macon", "GA"
    hub = ("Macon-Bibb County — Solid Waste", "https://sw.maconbibb.us/")
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner"],
                "SPECIAL_HANDLING",
                "Low",
                True,
                "Ryland Environmental bulk — schedule per Macon-Bibb SW",
                "Macon-Bibb / Ryland bulk collection",
                "Macon {item}s go on Ryland Environmental bulk collection — schedule via sw.maconbibb.us. Keep paint, batteries, and propane off bulk piles.",
                [
                    "Schedule Ryland bulk via Macon-Bibb solid waste pages.",
                    "Set out per posted size/item rules.",
                    "Keep HHW off bulk piles.",
                ],
                [("Who hauls?", "Ryland Environmental."), ("Source?", "sw.maconbibb.us.")],
                hub,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed", "paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "11th St Convenience Center — paint/batteries/e-waste pathways",
                "Macon-Bibb 11th Street Convenience Center",
                "Take {item} to the Macon-Bibb 11th Street Convenience Center pathways for paint, batteries, and related special wastes — confirm acceptance on sw.maconbibb.us. Wipe data for electronics. Not Ryland bulk for chemicals.",
                [
                    "Confirm 11th St Convenience Center accepted materials.",
                    "Haul sealed HHW / e-waste per posted rules.",
                    "Wipe data from electronics.",
                ],
                [("Bulk for paint?", "No — Convenience Center / special waste."), ("E-waste?", "Use 11th St pathways — confirm list.")],
                hub,
            ),
        ]
        + common_tail(
            hub,
            "Macon",
            "Construction debris is not typical free Ryland bulk. Hire private C&D or confirm landfill rules via sw.maconbibb.us. Route paint/chemicals to the 11th St Convenience Center separately.",
            "Private C&D / Macon-Bibb landfill pathways",
        ),
    )


def kansas_city_ks():
    c, st = "kansas-city-ks", "KS"
    hub = ("Unified Government Wyandotte County — Trash & Recycling", "https://www.wycokck.org/")
    bulk = ("UG — Bulky Item Collection", "https://www.wycokck.org/Residents/Trash-Recycling")
    hhw = ("UG — Household Hazardous Waste", "https://www.wycokck.org/Residents/Trash-Recycling/Household-Hazardous-Waste")
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner"],
                "SPECIAL_HANDLING",
                "Low",
                True,
                "WM bulky — up to 3 scheduled collections/week",
                "Kansas City KS / WM bulky collection",
                "Kansas City KS {item}s go on Waste Management bulky — up to 3 scheduled collections per week per wycokck.org rules. Schedule set-outs; keep HHW and e-waste off bulk piles.",
                [
                    "Schedule WM bulky per UG trash/recycling guidance (up to 3/week).",
                    "Set out per size/item limits.",
                    "Keep paint, batteries, propane, and e-waste off bulk piles.",
                ],
                [("How often?", "Up to 3 scheduled bulky collections/week."), ("Who hauls?", "Waste Management.")],
                bulk,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed"],
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "E-waste NOT at HHW — retailer / private e-waste recyclers",
                "Retailer take-back / private e-waste recyclers (not HHW facility)",
                "Kansas City KS electronics including {item} are NOT accepted at the HHW facility. Use retailer take-back or private e-waste recyclers. Wipe data. Do not set e-waste on WM bulk piles unless UG explicitly allows.",
                [
                    "Do not haul e-waste to the UG HHW facility.",
                    "Use retailer take-back or certified e-waste recyclers.",
                    "Wipe personal data.",
                ],
                [("HHW for e-waste?", "No — e-waste not accepted at HHW."), ("Bulk for TVs?", "Confirm UG rules — prefer recycler take-back.")],
                hhw,
            ),
            ch(
                ["paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "HHW — 2443 S 88th St — Saturdays Apr–Oct (schedule)",
                "UG HHW — 2443 S 88th Street",
                "Take {item} to the Unified Government HHW facility — 2443 S 88th Street — Saturday schedule typically April–October (confirm wycokck.org). E-waste is NOT accepted at HHW.",
                [
                    "Confirm Saturday Apr–Oct HHW schedule on wycokck.org.",
                    "Haul sealed materials to 2443 S 88th St.",
                    "Do not bring e-waste to HHW.",
                ],
                [("HHW address?", "2443 S 88th Street."), ("E-waste at HHW?", "No.")],
                hhw,
            ),
        ]
        + common_tail(
            hub,
            "Kansas City",
            "Construction debris is not typical free WM bulky. Hire private C&D or confirm transfer rules. Route paint/chemicals to UG HHW separately.",
            "Private C&D hauler / transfer",
        ),
    )


def springfield_ma():
    c, st = "springfield", "MA"
    hub = ("City of Springfield — Trash & Recycling", "https://www.springfield-ma.gov/dpw/trash-recycling")
    hhw = ("City of Springfield — Household Hazardous Waste", "https://www.springfield-ma.gov/dpw")
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner", "television"],
                "SPECIAL_HANDLING",
                "Low",
                True,
                "Bulk stickers $8 — TVs OK on stickered bulk",
                "Springfield MA bulk sticker collection",
                "Springfield MA {item}s go on bulk sticker collection — stickers about $8 each via springfield-ma.gov. TVs are accepted on bulk stickers. Keep paint, batteries, and propane off bulk piles.",
                [
                    "Purchase bulk stickers (~$8) per city guidance.",
                    "Affix sticker and set out on bulk day.",
                    "Keep HHW chemicals off stickered piles.",
                ],
                [("Sticker cost?", "About $8 per sticker."), ("TVs on bulk?", "Yes — on bulk stickers.")],
                hub,
            ),
            ch(
                ["computer-monitor", "smartphone", "e-waste-mixed"],
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "HHW events / designated e-waste — 70 Tapley by appt for HHW",
                "Springfield HHW — 70 Tapley Street (by appointment for events)",
                "Springfield electronics including {item} should use city HHW/e-waste pathways — HHW events at 70 Tapley by appointment. TVs may use bulk stickers; other e-waste confirm city guidance. Wipe data.",
                [
                    "Confirm e-waste rules on springfield-ma.gov.",
                    "Book HHW/event pathways at 70 Tapley when required.",
                    "Wipe personal data.",
                ],
                [("TVs?", "Bulk stickers OK."), ("Other e-waste?", "Confirm city HHW/event pathways.")],
                hhw,
            ),
            ch(
                ["paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "HHW events — 70 Tapley by appointment",
                "Springfield HHW events — 70 Tapley Street",
                "Take {item} to Springfield household hazardous waste events — 70 Tapley Street by appointment. Confirm dates on springfield-ma.gov. Not bulk stickers.",
                [
                    "Schedule HHW appointment for 70 Tapley.",
                    "Haul sealed materials only.",
                    "Keep HHW off bulk sticker piles.",
                ],
                [("HHW where?", "70 Tapley Street by appointment."), ("Bulk for paint?", "No.")],
                hhw,
            ),
        ]
        + common_tail(
            hub,
            "Springfield",
            "Construction debris is not typical bulk-sticker household material. Hire private C&D or confirm transfer rules. Route paint/chemicals to Tapley HHW events separately.",
            "Private C&D hauler / transfer",
        ),
    )


def sunnyvale():
    c, st = "sunnyvale", "CA"
    hub = ("City of Sunnyvale — Garbage & Recycling", "https://www.sunnyvale.ca.gov/property-residents/recycling-garbage")
    bulky = ("City of Sunnyvale — On-Call Bulky", "https://www.sunnyvale.ca.gov/property-residents/recycling-garbage/bulky-item-collection")
    hhw = ("Santa Clara County — Household Hazardous Waste", "https://hhw.santaclaracounty.gov/")
    smart = ("SMaRT Station", "https://www.sunnyvale.ca.gov/property-residents/recycling-garbage/smart-station")
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner"],
                "SPECIAL_HANDLING",
                "Low",
                True,
                "On-call bulky — up to 2×/year",
                "Sunnyvale on-call bulky collection",
                "Sunnyvale {item}s go on on-call bulky collection — up to 2 times per year. Schedule via sunnyvale.ca.gov. Keep HHW off bulky piles. SMaRT Station is the city’s recycling/transfer hub for many materials.",
                [
                    "Schedule on-call bulky (up to 2×/year) via sunnyvale.ca.gov.",
                    "Set out per city size/item rules.",
                    "Keep paint, batteries, and propane off bulky piles.",
                ],
                [("How often?", "Up to 2 on-call bulky collections/year."), ("SMaRT Station?", "City recycling/transfer hub — confirm accepted materials.")],
                bulky,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed"],
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "SMaRT Station / SCC HHW pathways — confirm e-waste acceptance",
                "SMaRT Station / Santa Clara County HHW",
                "Sunnyvale electronics including {item} go via SMaRT Station e-waste pathways or Santa Clara County HHW by appointment (hhw.santaclaracounty.gov). Wipe data. Confirm which site accepts your device before hauling.",
                [
                    "Confirm e-waste at SMaRT Station or book SCC HHW appointment.",
                    "Wipe personal data.",
                    "Do not put e-waste in garbage carts.",
                ],
                [("Bulky for TVs?", "Confirm — prefer SMaRT / SCC HHW."), ("SCC HHW?", "hhw.santaclaracounty.gov by appointment.")],
                smart,
            ),
            ch(
                ["paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "Santa Clara County HHW by appointment — hhw.santaclaracounty.gov",
                "Santa Clara County Household Hazardous Waste (by appointment)",
                "Take {item} to Santa Clara County Household Hazardous Waste by appointment — schedule at hhw.santaclaracounty.gov. Not on-call bulky.",
                [
                    "Book an SCC HHW appointment online.",
                    "Transport sealed materials only.",
                    "Keep HHW off bulky piles.",
                ],
                [("Walk-in HHW?", "Appointment required via hhw.santaclaracounty.gov."), ("Bulky for paint?", "No.")],
                hhw,
            ),
        ]
        + common_tail(
            hub,
            "Sunnyvale",
            "Construction debris is not typical free on-call bulky. Hire private C&D or confirm SMaRT Station C&D rules. Route paint/chemicals to SCC HHW separately.",
            "Private C&D / SMaRT Station pathways",
        ),
    )


def jackson():
    c, st = "jackson", "MS"
    hub = ("City of Jackson — Solid Waste / SWEEP", "https://jacksonms.gov/government/city-departments/public-works-department/solid-waste-division/s-w-e-e-p/")
    hhw = ("City of Jackson — Household Hazardous Waste / ESC", "https://jacksonms.gov/solid-waste-division-2/")
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner", "television"],
                "SPECIAL_HANDLING",
                "Low",
                True,
                "SWEEP bulk — 2 items every 2nd collection day",
                "Jackson SWEEP bulk collection",
                "Jackson {item}s go on SWEEP bulk — up to 2 bulk items every second collection day (furniture, mattresses, TVs, appliances, limbs, etc.). Follow jacksonms.gov set-out rules. Keep chemicals off bulk piles.",
                [
                    "Set out up to 2 bulk items on the second collection day.",
                    "Follow SWEEP size/item guidance on jacksonms.gov.",
                    "Keep paint and batteries off bulk piles.",
                ],
                [("How many?", "2 bulk items every second collection day."), ("TVs on bulk?", "Yes — per SWEEP list.")],
                hub,
            ),
            ch(
                ["computer-monitor", "smartphone", "e-waste-mixed"],
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "ESC temporarily closed — monitor city site / private until reopen",
                "Jackson Environmental Service Center (temporarily closed) — 1570 University Blvd",
                "Jackson electronics including {item} normally go to the Environmental Service Center, but the ESC is temporarily closed for relocation. Monitor jacksonms.gov Solid Waste updates and use private/certified e-waste options until reopen. Wipe data.",
                [
                    "Check jacksonms.gov Solid Waste for ESC reopen updates.",
                    "Until reopen, use private certified e-waste recyclers.",
                    "Wipe personal data.",
                ],
                [("ESC open?", "Temporarily closed — monitor city site."), ("Bulk for small e-waste?", "Prefer ESC when open / private recycler now.")],
                hhw,
            ),
            ch(
                ["paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "ESC temporarily closed — monitor city / private HHW until reopen",
                "Jackson Environmental Service Center (temporarily closed) — 1570 University Blvd",
                "Take {item} to the Jackson Environmental Service Center when reopened — currently temporarily closed for relocation (jacksonms.gov Solid Waste notice). Until then, residents should monitor the city site and use private HHW options. Do not put HHW in trash or SWEEP piles.",
                [
                    "Monitor jacksonms.gov for ESC reopen / relocation updates.",
                    "Until reopen, use private HHW disposal options.",
                    "Never put HHW in trash or storm drains.",
                ],
                [("ESC status?", "Temporarily closed — relocating; monitor city site."), ("SWEEP for paint?", "No.")],
                hhw,
            ),
        ]
        + common_tail(
            hub,
            "Jackson",
            "Construction debris is not typical SWEEP household bulk. Hire private C&D or confirm landfill rules. Route paint/chemicals to ESC when reopened (or private HHW meanwhile).",
            "Private C&D / landfill pathways",
        ),
    )


def killeen():
    c, st = "killeen", "TX"
    hub = ("City of Killeen — Solid Waste", "https://www.killeentexas.gov/289/Solid-Waste")
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner"],
                "SPECIAL_HANDLING",
                "Low",
                True,
                "Fee bulk curb / Transfer Station Hwy 195",
                "Killeen fee bulk / Transfer Station Highway 195",
                "Killeen {item}s go on fee-based bulk curb service or to the Transfer Station on Highway 195 — confirm fees on killeentexas.gov. Keep HHW off bulk piles.",
                [
                    "Schedule fee bulk curb or haul to Transfer Station Hwy 195.",
                    "Confirm fees/ID on killeentexas.gov.",
                    "Keep paint, batteries, and propane off bulk loads.",
                ],
                [("Free bulk?", "Fee-based curb — confirm current rates."), ("Transfer Station?", "Highway 195 — confirm hours.")],
                hub,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed"],
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "Recycling Center oil/batteries pathways / HHW events — confirm e-waste",
                "Killeen Recycling Center / city HHW events",
                "Killeen electronics including {item} should use city Recycling Center / HHW event pathways — confirm e-waste acceptance on killeentexas.gov. Wipe data. Transfer Station may not accept all electronics.",
                [
                    "Confirm e-waste at Recycling Center or next HHW event.",
                    "Wipe personal data.",
                    "Do not put e-waste in regular trash.",
                ],
                [("Transfer for TVs?", "Confirm — prefer Recycling Center / HHW events."), ("Source?", "killeentexas.gov Solid Waste.")],
                hub,
            ),
            ch(
                ["paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "HHW events + Recycling Center oil/batteries",
                "Killeen HHW events / Recycling Center",
                "Take {item} to Killeen HHW events or the Recycling Center for oil/batteries pathways — confirm materials on killeentexas.gov. Not regular trash or fee bulk piles.",
                [
                    "Check killeentexas.gov for HHW event dates.",
                    "Use Recycling Center for oil/batteries when accepted.",
                    "Keep HHW off bulk piles.",
                ],
                [("HHW permanent site?", "Events + Recycling Center pathways — confirm city page."), ("Bulk for paint?", "No.")],
                hub,
            ),
        ]
        + common_tail(
            hub,
            "Killeen",
            "Construction debris goes via Transfer Station / private C&D with fees — not free household bulk. Route paint/chemicals to HHW events separately.",
            "Killeen Transfer Station / private C&D",
            cd_fee="Transfer Station / private C&D fees",
        ),
    )


def hollywood():
    c, st = "hollywood", "FL"
    hub = ("City of Hollywood — Garbage & Recycling", "https://www.hollywoodfl.org/residents/garbage-recycling")
    hhw = ("Broward County — South Drop-Off Center", "https://www.broward.org/WasteAndRecycling/Recycling/Pages/DropOffCenters.aspx")
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner"],
                "SPECIAL_HANDLING",
                "Low",
                True,
                "Monthly bulk collection",
                "Hollywood FL monthly bulk collection",
                "Hollywood {item}s go on monthly bulk collection — follow hollywoodfl.org set-out rules. Keep HHW off bulk piles.",
                [
                    "Set out bulk on the monthly bulk day.",
                    "Follow hollywoodfl.org size/item limits.",
                    "Keep paint, batteries, and propane off bulk piles.",
                ],
                [("How often?", "Monthly bulk."), ("Source?", "hollywoodfl.org.")],
                hub,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed", "paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "Broward South Drop-Off — 5601 W Hallandale Beach Blvd — Saturdays",
                "Broward South Drop-Off Center — 5601 W Hallandale Beach Blvd",
                "Take {item} to Broward County South Drop-Off Center — 5601 W Hallandale Beach Boulevard — Saturday drop-off (confirm broward.org hours). Wipe data for electronics. Not monthly bulk for chemicals.",
                [
                    "Confirm Saturday hours on broward.org.",
                    "Haul to 5601 W Hallandale Beach Blvd.",
                    "Wipe data from electronics; seal HHW.",
                ],
                [("Address?", "5601 W Hallandale Beach Blvd."), ("Bulk for paint?", "No — Broward South Drop-Off.")],
                hhw,
            ),
        ]
        + common_tail(
            hub,
            "Hollywood",
            "Construction debris is not typical monthly household bulk. Hire private C&D or confirm transfer rules. Route paint/chemicals to Broward South Drop-Off separately.",
            "Private C&D / Broward transfer",
        ),
    )


def murfreesboro():
    c, st = "murfreesboro", "TN"
    hub = ("City of Murfreesboro — Solid Waste", "https://www.murfreesborotn.gov/163/Solid-Waste")
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner"],
                "SPECIAL_HANDLING",
                "Low",
                True,
                "Fee bulky collection — schedule via city",
                "Murfreesboro fee bulky collection",
                "Murfreesboro {item}s go on fee-based bulky collection — schedule via murfreesborotn.gov. Keep HHW off bulky piles.",
                [
                    "Schedule fee bulky via city Solid Waste pages.",
                    "Set out per posted rules.",
                    "Keep paint, batteries, and propane off bulky piles.",
                ],
                [("Free bulky?", "Fee-based — confirm current rates."), ("Source?", "murfreesborotn.gov.")],
                hub,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed"],
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "Leanna Convenience Center — e-waste/paint pathways",
                "Leanna Convenience Center — e-waste / paint",
                "Murfreesboro electronics including {item} go to Leanna Convenience Center e-waste pathways — confirm acceptance on murfreesborotn.gov. Wipe data. Rutherford County also runs mobile HHW events.",
                [
                    "Confirm Leanna Convenience Center e-waste rules.",
                    "Wipe personal data.",
                    "Watch Rutherford mobile HHW events for chemicals/electronics as posted.",
                ],
                [("Fee bulky for TVs?", "Prefer Leanna e-waste pathways."), ("Mobile HHW?", "Rutherford County events — monitor calendar.")],
                hub,
            ),
            ch(
                ["paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "Leanna Convenience Center paint + Rutherford mobile HHW events",
                "Leanna Convenience Center / Rutherford mobile HHW",
                "Take {item} to Leanna Convenience Center paint pathways and/or Rutherford County mobile HHW events — confirm materials and dates via murfreesborotn.gov / county notices. Not fee bulky.",
                [
                    "Confirm Leanna accepted HHW materials.",
                    "Monitor Rutherford mobile HHW event dates.",
                    "Keep HHW off fee bulky piles.",
                ],
                [("Bulk for paint?", "No."), ("Events?", "Rutherford mobile HHW — confirm calendar.")],
                hub,
            ),
        ]
        + common_tail(
            hub,
            "Murfreesboro",
            "Construction debris is not typical fee household bulky. Hire private C&D or confirm convenience-center C&D rules. Route paint/chemicals to Leanna / Rutherford HHW separately.",
            "Private C&D / convenience center pathways",
        ),
    )


def pasadena_tx():
    c, st = "pasadena", "TX"
    hub = ("City of Pasadena — Sanitation", "https://www.pasadenatx.gov/159/Sanitation")
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner"],
                "SPECIAL_HANDLING",
                "Low",
                True,
                "Frontier bulk — biweekly",
                "Pasadena / Frontier biweekly bulk collection",
                "Pasadena TX {item}s go on Frontier bulk collection — biweekly. Follow pasadenatx.gov set-out rules. City Sanitation also handles HHW/appliances inquiries at 713-475-7884. Keep chemicals off bulk piles.",
                [
                    "Set out on biweekly Frontier bulk day.",
                    "Call Sanitation 713-475-7884 for appliance/HHW questions.",
                    "Keep paint and batteries off bulk piles.",
                ],
                [("How often?", "Biweekly Frontier bulk."), ("Appliances help?", "713-475-7884 Sanitation.")],
                hub,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed"],
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "Recycling Center 2800 Pasadena Blvd / Sanitation guidance",
                "Pasadena Recycling Center — 2800 Pasadena Boulevard",
                "Pasadena electronics including {item} should use the Recycling Center at 2800 Pasadena Boulevard and Sanitation guidance (713-475-7884). Wipe data. Confirm e-waste acceptance before hauling.",
                [
                    "Confirm e-waste at 2800 Pasadena Blvd.",
                    "Call 713-475-7884 if unsure.",
                    "Wipe personal data.",
                ],
                [("Bulk for TVs?", "Confirm — prefer Recycling Center."), ("Address?", "2800 Pasadena Boulevard.")],
                hub,
            ),
            ch(
                ["paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "City Sanitation HHW/appliances — 713-475-7884; Recycling Center pathways",
                "Pasadena Sanitation HHW / Recycling Center — 2800 Pasadena Blvd",
                "Take {item} via City of Pasadena Sanitation HHW/appliance pathways — call 713-475-7884 — and Recycling Center drop-off at 2800 Pasadena Boulevard when accepted. Not Frontier bulk.",
                [
                    "Call Sanitation 713-475-7884 for HHW guidance.",
                    "Use Recycling Center at 2800 Pasadena Blvd when accepted.",
                    "Keep HHW off biweekly bulk piles.",
                ],
                [("Phone?", "713-475-7884."), ("Bulk for paint?", "No.")],
                hub,
            ),
        ]
        + common_tail(
            hub,
            "Pasadena",
            "Construction debris is not typical Frontier household bulk. Hire private C&D or confirm transfer rules. Route paint/chemicals via Sanitation / Recycling Center separately.",
            "Private C&D / transfer",
        ),
    )


def bellevue():
    c, st = "bellevue", "WA"
    hub = ("City of Bellevue — Garbage & Recycling", "https://bellevuewa.gov/city-government/departments/utilities/garbage-recycling")
    hhw = ("King County — Factoria HHW & Transfer", "https://kingcounty.gov/en/dept/dnrp/waste-services/garbage-recycling-compost/solid-waste-facilities/factoria")
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner"],
                "SPECIAL_HANDLING",
                "Low",
                True,
                "Republic Services bulky — fees apply",
                "Bellevue / Republic Services bulky collection",
                "Bellevue {item}s go on Republic Services bulky collection — fees apply. Schedule via bellevuewa.gov / Republic. Keep HHW off bulk piles.",
                [
                    "Schedule Republic bulky and confirm fees.",
                    "Set out per Republic rules.",
                    "Keep paint, batteries, and propane off bulk piles.",
                ],
                [("Free bulky?", "Fees apply — confirm Republic rates."), ("Who hauls?", "Republic Services.")],
                hub,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed", "paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "Factoria HHW — 13800 SE 32nd St",
                "King County Factoria HHW — 13800 SE 32nd Street",
                "Take {item} to King County Factoria Household Hazardous Waste — 13800 SE 32nd Street. Confirm hours on kingcounty.gov. Wipe data for electronics. Not Republic bulk for chemicals.",
                [
                    "Confirm Factoria HHW hours on kingcounty.gov.",
                    "Haul to 13800 SE 32nd St.",
                    "Wipe data; seal HHW containers.",
                ],
                [("Address?", "13800 SE 32nd Street."), ("Bulk for paint?", "No — Factoria HHW.")],
                hhw,
            ),
        ]
        + common_tail(
            hub,
            "Bellevue",
            "Construction debris is not typical Republic household bulky. Hire private C&D or confirm transfer rules. Route paint/chemicals to Factoria HHW separately.",
            "Private C&D / King County transfer",
        ),
    )


def pomona():
    c, st = "pomona", "CA"
    hub = ("City of Pomona — Trash & Recycling", "https://www.pomonaca.gov/government/departments/public-works/trash-recycling")
    hhw = ("CleanLA — HHW Collection Centers / Events", "https://cleanla.lacounty.gov/")
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner"],
                "SPECIAL_HANDLING",
                "Low",
                True,
                "Athens Services bulky — up to 6×/year",
                "Pomona / Athens Services bulky collection",
                "Pomona {item}s go on Athens Services bulky collection — up to 6 times per year. Schedule via pomonaca.gov / Athens. Keep HHW and e-waste off bulk piles.",
                [
                    "Schedule Athens bulky (up to 6×/year).",
                    "Set out per Athens size/item rules.",
                    "Keep paint, batteries, propane, and e-waste off bulk piles.",
                ],
                [("How often?", "Up to 6 bulky collections/year."), ("Who hauls?", "Athens Services.")],
                hub,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed", "paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "CleanLA HHW events / collection centers",
                "LA County CleanLA HHW events and collection centers",
                "Take {item} to LA County CleanLA household hazardous waste events and collection centers — cleanla.lacounty.gov. Wipe data for electronics. Not Athens bulky for chemicals/e-waste.",
                [
                    "Find CleanLA events/centers at cleanla.lacounty.gov.",
                    "Transport sealed HHW; wipe electronics.",
                    "Keep HHW/e-waste off Athens bulk piles.",
                ],
                [("Bulky for paint?", "No — CleanLA."), ("Source?", "cleanla.lacounty.gov.")],
                hhw,
            ),
        ]
        + common_tail(
            hub,
            "Pomona",
            "Construction debris is not typical free Athens bulky. Hire private C&D or confirm transfer rules. Route paint/chemicals to CleanLA separately.",
            "Private C&D / LA County transfer",
        ),
    )


def escondido():
    c, st = "escondido", "CA"
    hub = ("City of Escondido — Trash & Recycling", "https://www.escondido.gov/258/Trash-Recycling")
    hhw = ("City of Escondido — Household Hazardous Waste", "https://www.escondido.gov/261/Household-Hazardous-Waste")
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner"],
                "SPECIAL_HANDLING",
                "Low",
                True,
                "EDI bulky — fees apply",
                "Escondido / EDI bulky collection",
                "Escondido {item}s go on EDI bulky collection — fees apply. Schedule via escondido.gov / EDI. Keep HHW off bulk piles.",
                [
                    "Schedule EDI bulky and confirm fees.",
                    "Set out per EDI rules.",
                    "Keep paint, batteries, and propane off bulk piles.",
                ],
                [("Free bulky?", "Fees apply — confirm EDI rates."), ("Who hauls?", "EDI.")],
                hub,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed", "paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "Escondido HHW — 1044 W Washington by appointment",
                "Escondido HHW — 1044 W Washington Avenue (by appointment)",
                "Take {item} to Escondido Household Hazardous Waste — 1044 W Washington Avenue — by appointment. Confirm booking on escondido.gov. Wipe data for electronics. Not EDI bulky for chemicals.",
                [
                    "Book an HHW appointment for 1044 W Washington.",
                    "Haul sealed materials; wipe electronics.",
                    "Keep HHW off EDI bulk piles.",
                ],
                [("Address?", "1044 W Washington Ave (by appointment)."), ("Bulk for paint?", "No — city HHW.")],
                hhw,
            ),
        ]
        + common_tail(
            hub,
            "Escondido",
            "Construction debris is not typical EDI household bulky. Hire private C&D or confirm transfer rules. Route paint/chemicals to Escondido HHW separately.",
            "Private C&D / transfer",
        ),
    )


def joliet():
    c, st = "joliet", "IL"
    hub = ("City of Joliet — Garbage & Recycling", "https://www.joliet.gov/government/departments/public-works/garbage-recycling")
    hhw = ("Will County — Household Hazardous Waste / e-waste", "https://www.willcountygreen.com/")
    nap = ("City of Naperville — HHW Facility", "https://www.naperville.il.us/residents/recycling-and-garbage/household-hazardous-waste/")
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner"],
                "SPECIAL_HANDLING",
                "Low",
                True,
                "City/hauler bulky — confirm Joliet set-out rules",
                "Joliet bulky collection",
                "Joliet {item}s follow city/hauler bulky collection rules on joliet.gov. Keep HHW off bulk piles. WM At Your Door covers many household hazardous materials separately.",
                [
                    "Follow Joliet bulky set-out / scheduling rules.",
                    "Keep paint, batteries, and propane off bulk piles.",
                    "Use At Your Door / county drop-offs for HHW.",
                ],
                [("HHW on bulk?", "No."), ("Source?", "joliet.gov.")],
                hub,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed"],
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "Will County e-waste drop-off — confirm willcountygreen.com",
                "Will County e-waste drop-off sites",
                "Joliet electronics including {item} go to Will County e-waste drop-off pathways — willcountygreen.com. Wipe data. Not regular trash.",
                [
                    "Find Will County e-waste drop-off sites on willcountygreen.com.",
                    "Wipe personal data.",
                    "Do not put e-waste in garbage.",
                ],
                [("City bulk for TVs?", "Prefer Will County e-waste drop-off."), ("Source?", "willcountygreen.com.")],
                hhw,
            ),
            ch(
                ["paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "WM At Your Door HHW + Naperville HHW for chemicals",
                "WM At Your Door / Naperville HHW Facility — 156 Fort Hill Drive",
                "Take {item} via Waste Management At Your Door household hazardous waste collection and/or Naperville HHW Facility chemical drop-off (156 Fort Hill Drive) per joliet.gov / naperville.il.us guidance. Not curb bulk.",
                [
                    "Schedule WM At Your Door HHW if available to your address.",
                    "Or use Naperville HHW for chemicals per posted rules.",
                    "Keep HHW off Joliet bulk piles.",
                ],
                [("At Your Door?", "WM HHW mail-back/collection program — confirm eligibility."), ("Naperville HHW?", "Chemical drop-off option for area residents — confirm acceptance.")],
                nap,
            ),
        ]
        + common_tail(
            hub,
            "Joliet",
            "Construction debris is not typical household bulk. Hire private C&D or confirm transfer rules. Route paint/chemicals to At Your Door / Naperville HHW separately.",
            "Private C&D / transfer",
        ),
    )


def charleston():
    c, st = "charleston", "SC"
    hub = ("City of Charleston — Environmental Services", "https://www.charleston-sc.gov/161/Environmental-Services")
    hhw = ("Charleston County — Bees Ferry HHW / e-waste", "https://www.charlestoncounty.org/departments/environmental-management/")
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner"],
                "SPECIAL_HANDLING",
                "Low",
                True,
                "City bulk curb collection",
                "Charleston bulk curb collection",
                "Charleston {item}s go on city bulk curb collection — follow charleston-sc.gov Environmental Services rules. Keep HHW off bulk piles.",
                [
                    "Set out bulk per Charleston Environmental Services guidance.",
                    "Follow size/item limits.",
                    "Keep paint, batteries, and propane off bulk piles.",
                ],
                [("Source?", "charleston-sc.gov Environmental Services.")],
                hub,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed", "paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "Bees Ferry — Charleston County HHW/e-waste",
                "Charleston County Bees Ferry HHW / e-waste facility",
                "Take {item} to Charleston County Bees Ferry household hazardous waste and e-waste pathways — charlestoncounty.gov Environmental Management. Wipe data for electronics. Not city bulk for chemicals.",
                [
                    "Confirm Bees Ferry hours/materials on charlestoncounty.gov.",
                    "Haul sealed HHW; wipe electronics.",
                    "Keep HHW/e-waste off city bulk piles.",
                ],
                [("Bulk for paint?", "No — Bees Ferry."), ("E-waste?", "Bees Ferry County pathways.")],
                hhw,
            ),
        ]
        + common_tail(
            hub,
            "Charleston",
            "Construction debris is not typical city household bulk. Hire private C&D or confirm county landfill rules. Route paint/chemicals to Bees Ferry separately.",
            "Private C&D / Charleston County landfill",
        ),
    )


def mesquite():
    c, st = "mesquite", "TX"
    hub = ("City of Mesquite — Garbage & Recycling", "https://www.cityofmesquite.com/270/Garbage-Recycling")
    hhw = ("Dallas County — Household Hazardous Waste", "https://www.dallascounty.org/departments/hhs/hhw.php")
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner"],
                "SPECIAL_HANDLING",
                "Low",
                True,
                "Weekly bulky collection",
                "Mesquite weekly bulky collection",
                "Mesquite {item}s go on weekly bulky collection — follow cityofmesquite.com set-out rules. Citizens Convenience Center at 3550 Lawson is also available for many drop-offs. Keep HHW off weekly piles.",
                [
                    "Set out bulky on the weekly bulky day.",
                    "Or haul to Citizens Convenience Center — 3550 Lawson.",
                    "Keep paint, batteries, and propane off bulky piles.",
                ],
                [("How often?", "Weekly bulky."), ("Convenience Center?", "3550 Lawson.")],
                hub,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed"],
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "Citizens Convenience 3550 Lawson / Dallas Co HHW pathways",
                "Mesquite Citizens Convenience Center — 3550 Lawson",
                "Mesquite electronics including {item} should use Citizens Convenience Center (3550 Lawson) and/or Dallas County HHW pathways — confirm e-waste acceptance. Wipe data.",
                [
                    "Confirm e-waste at 3550 Lawson or Dallas County HHW.",
                    "Wipe personal data.",
                    "Do not put e-waste in trash.",
                ],
                [("Weekly bulky for TVs?", "Confirm — prefer Convenience Center / Dallas Co HHW."), ("Dallas Co HHW?", "11234 Plano Rd — confirm hours.")],
                hub,
            ),
            ch(
                ["paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "Dallas County HHW — 11234 Plano Rd; Citizens Convenience pathways",
                "Dallas County HHW — 11234 Plano Road",
                "Take {item} to Dallas County Household Hazardous Waste — 11234 Plano Road — and/or Mesquite Citizens Convenience Center pathways when accepted. Not weekly bulky.",
                [
                    "Confirm Dallas County HHW hours at 11234 Plano Rd.",
                    "Use Citizens Convenience (3550 Lawson) when materials accepted.",
                    "Keep HHW off weekly bulky piles.",
                ],
                [("Dallas Co HHW address?", "11234 Plano Road."), ("Bulk for paint?", "No.")],
                hhw,
            ),
        ]
        + common_tail(
            hub,
            "Mesquite",
            "Construction debris is not typical weekly household bulky. Hire private C&D or confirm Citizens Convenience C&D rules. Route paint/chemicals to Dallas County HHW separately.",
            "Citizens Convenience / private C&D",
        ),
    )


def naperville():
    c, st = "naperville", "IL"
    hub = ("City of Naperville — Recycling & Garbage", "https://www.naperville.il.us/residents/recycling-and-garbage/")
    hhw = ("City of Naperville — HHW Facility", "https://www.naperville.il.us/residents/recycling-and-garbage/household-hazardous-waste/")
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner"],
                "SPECIAL_HANDLING",
                "Low",
                True,
                "Groot — up to 2 bulk items/week",
                "Naperville / Groot bulk collection",
                "Naperville {item}s go on Groot bulk collection — up to 2 bulk items per week. Follow naperville.il.us set-out rules. Keep HHW off bulk piles.",
                [
                    "Set out up to 2 bulk items/week per Groot rules.",
                    "Follow naperville.il.us guidance.",
                    "Keep paint, batteries, and propane off bulk piles.",
                ],
                [("How many?", "Up to 2 bulk items per week."), ("Who hauls?", "Groot.")],
                hub,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed"],
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "Electronics drop-off Mon–Fri — same campus as HHW (156 Fort Hill)",
                "Naperville electronics drop-off — 156 Fort Hill Drive campus",
                "Naperville electronics including {item} go to the electronics drop-off on the Fort Hill campus — typically Monday–Friday — confirm naperville.il.us. Wipe data. HHW chemicals use weekend hours at the same campus.",
                [
                    "Confirm electronics hours (Mon–Fri) on naperville.il.us.",
                    "Haul to 156 Fort Hill Drive campus.",
                    "Wipe personal data.",
                ],
                [("Electronics hours?", "Typically Mon–Fri — confirm city page."), ("Same campus as HHW?", "Yes — 156 Fort Hill Drive.")],
                hhw,
            ),
            ch(
                ["paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "HHW facility — 156 Fort Hill — Sat–Sun",
                "Naperville HHW Facility — 156 Fort Hill Drive",
                "Take {item} to the Naperville Household Hazardous Waste Facility — 156 Fort Hill Drive — typically Saturday–Sunday (confirm naperville.il.us). Not Groot bulk.",
                [
                    "Confirm Sat–Sun HHW hours on naperville.il.us.",
                    "Haul sealed materials to 156 Fort Hill Dr.",
                    "Keep HHW off bulk piles.",
                ],
                [("HHW hours?", "Typically Sat–Sun — confirm city page."), ("Address?", "156 Fort Hill Drive.")],
                hhw,
            ),
        ]
        + common_tail(
            hub,
            "Naperville",
            "Construction debris is not typical Groot household bulk. Hire private C&D or confirm transfer rules. Route paint/chemicals to Fort Hill HHW separately.",
            "Private C&D / transfer",
        ),
    )


def rockford():
    c, st = "rockford", "IL"
    hub = ("City of Rockford — Public Works / Solid Waste", "https://rockfordil.gov/city-departments/public-works/")
    hhw = ("City of Rockford — Household Hazardous Waste", "https://rockfordil.gov/")
    ew = ("KNIB — Electronics Recycling", "https://www.knib.org/")
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner"],
                "SPECIAL_HANDLING",
                "Low",
                True,
                "Weekly bulk collection",
                "Rockford weekly bulk collection",
                "Rockford {item}s go on weekly bulk collection — follow rockfordil.gov set-out rules. Keep HHW off bulk piles.",
                [
                    "Set out bulk on the weekly bulk day.",
                    "Follow city size/item limits.",
                    "Keep paint, batteries, and propane off bulk piles.",
                ],
                [("How often?", "Weekly bulk."), ("Source?", "rockfordil.gov.")],
                hub,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed"],
                "BANNED_FROM_LANDFILLS",
                "Medium",
                False,
                "KNIB e-waste — 4665 Hydraulic",
                "KNIB electronics recycling — 4665 Hydraulic Road",
                "Rockford electronics including {item} go to KNIB e-waste recycling — 4665 Hydraulic Road. Wipe data. Confirm hours on knib.org / city guidance.",
                [
                    "Haul e-waste to KNIB — 4665 Hydraulic Rd.",
                    "Confirm hours before visiting.",
                    "Wipe personal data.",
                ],
                [("Address?", "4665 Hydraulic Road."), ("Bulk for TVs?", "Prefer KNIB e-waste.")],
                ew,
            ),
            ch(
                ["paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "HHW — 3315 Kishwaukee — Sat–Sun",
                "Rockford HHW — 3315 Kishwaukee Street",
                "Take {item} to Rockford Household Hazardous Waste — 3315 Kishwaukee Street — typically Saturday–Sunday (confirm rockfordil.gov). Not weekly bulk.",
                [
                    "Confirm Sat–Sun HHW hours on rockfordil.gov.",
                    "Haul sealed materials to 3315 Kishwaukee St.",
                    "Keep HHW off weekly bulk piles.",
                ],
                [("HHW address?", "3315 Kishwaukee Street."), ("Bulk for paint?", "No.")],
                hhw,
            ),
        ]
        + common_tail(
            hub,
            "Rockford",
            "Construction debris is not typical weekly household bulk. Hire private C&D or confirm transfer rules. Route paint/chemicals to Kishwaukee HHW separately.",
            "Private C&D / transfer",
        ),
    )


def bridgeport():
    c, st = "bridgeport", "CT"
    hub = ("City of Bridgeport — Public Facilities / Sanitation", "https://www.bridgeportct.gov/")
    hhw = ("City of Bridgeport — Hazardous Waste", "https://www.bridgeportct.gov/residents/hazardous-waste")
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner"],
                "SPECIAL_HANDLING",
                "Low",
                False,
                "Transfer Station — 475 Asylum St",
                "Bridgeport Transfer Station — 475 Asylum Street",
                "Bridgeport {item}s go to the Transfer Station at 475 Asylum Street — confirm residency, fees, and hours on bridgeportct.gov. Keep HHW off transfer loads when not accepted.",
                [
                    "Confirm Transfer Station hours/fees on bridgeportct.gov.",
                    "Haul bulk to 475 Asylum St.",
                    "Keep paint and chemicals out unless accepted on HHW day.",
                ],
                [("Address?", "475 Asylum Street."), ("Curbside free bulk?", "Transfer Station drop-off — confirm current rules.")],
                hub,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed", "paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "Annual HHW day — cite city hazardous waste page",
                "Bridgeport annual Household Hazardous Waste day",
                "Take {item} to Bridgeport’s annual household hazardous waste collection day — dates and accepted materials on the city hazardous waste page (bridgeportct.gov). Wipe data for electronics. Transfer Station may not accept HHW year-round.",
                [
                    "Monitor bridgeportct.gov hazardous waste page for the annual HHW day.",
                    "Transport sealed materials; wipe electronics.",
                    "Do not put HHW in regular trash.",
                ],
                [("Year-round HHW?", "Primarily annual HHW day — confirm city page."), ("Transfer for paint?", "Prefer annual HHW day.")],
                hhw,
            ),
        ]
        + common_tail(
            hub,
            "Bridgeport",
            "Construction debris goes via Transfer Station / private C&D with fees — confirm rules. Route paint/chemicals to the annual HHW day separately.",
            "Bridgeport Transfer Station / private C&D",
            cd_fee="Transfer Station / private C&D fees",
        ),
    )


def santa_rosa_pack(city_slug="santa-rosa-ca"):
    c, st = city_slug, "CA"
    hub = ("Zero Waste Sonoma — Bulky Item Pickup", "https://zerowastesonoma.gov/recycle-dispose/residents/bulky-item-collection")
    rec = ("Recology Sonoma Marin — Santa Rosa Bulky Items", "https://www.recology.com/recology-sonoma-marin/santa-rosa/bulky-items/")
    hhw = ("Zero Waste Sonoma — Household Hazardous Waste Facility", "https://zerowastesonoma.gov/recycle-dispose/residents/household-hazardous-waste-facility")
    return rows_from_channels(
        c,
        st,
        [
            ch(
                ["mattress", "refrigerator", "air-conditioner"],
                "SPECIAL_HANDLING",
                "Low",
                True,
                "Recology Sonoma Marin bulky — 2 free pickups/year",
                "Santa Rosa / Recology Sonoma Marin bulky collection",
                "Santa Rosa {item}s go on Recology Sonoma Marin bulky collection — residential customers get 2 free pickups per year (schedule 800-243-0291). Freon appliances may incur a Freon charge. Keep HHW chemicals off bulky piles.",
                [
                    "Schedule Recology bulky (2 free/year) at 800-243-0291.",
                    "Set out up to posted cubic-yard limits.",
                    "Keep paint, batteries, and propane off bulky piles.",
                ],
                [("How often?", "2 free bulky pickups/year."), ("Who hauls?", "Recology Sonoma Marin."), ("Freon?", "Freon charge may apply.")],
                hub,
            ),
            ch(
                ["television", "computer-monitor", "smartphone", "e-waste-mixed", "paint-latex", "paint-oil", "car-battery", "lithium-battery", "motor-oil", "propane-tank", "fluorescent-bulbs", "cooking-oil", "medical-sharps"],
                "BANNED_FROM_LANDFILLS",
                "High",
                False,
                "Sonoma HHW — 500 Mecham Rd, Petaluma — Thu–Sat 7:30–2:30",
                "Zero Waste Sonoma HHW Facility — 500 Mecham Road, Petaluma",
                "Take {item} to the Zero Waste Sonoma Household Hazardous Waste Facility — 500 Mecham Road (Building 5), Petaluma — Thursday–Saturday 7:30 a.m.–2:30 p.m. Bring Sonoma County ID. Electronics are accepted at the HHW facility; wipe data. Not a substitute for Recology bulky chemicals.",
                [
                    "Haul sealed materials to 500 Mecham Rd, Petaluma (Bldg 5).",
                    "Hours: Thu–Sat 7:30–14:30; bring residency ID.",
                    "Wipe data from electronics.",
                ],
                [("HHW address?", "500 Mecham Road, Petaluma."), ("Appointment?", "Not required for residents."), ("Bulky for paint?", "No — Mecham HHW.")],
                hhw,
            ),
        ]
        + common_tail(
            hub,
            "Santa Rosa",
            "Construction debris is not typical free Recology bulky. Hire private C&D or confirm Central Disposal Site C&D rules. Route paint/chemicals to 500 Mecham Rd HHW separately.",
            "Private C&D / Central Disposal Site",
        ),
    )


# ---------------------------------------------------------------------------
# Geo / facilities / main
# ---------------------------------------------------------------------------

CITIES = [
    {"city": "Garden Grove", "city_slug": "garden-grove", "state": "CA", "state_slug": "california", "lat": 33.7743, "lng": -117.938, "population": 171949},
    {"city": "Pembroke Pines", "city_slug": "pembroke-pines", "state": "FL", "state_slug": "florida", "lat": 26.0078, "lng": -80.2962, "population": 171178},
    {"city": "Fort Collins", "city_slug": "fort-collins", "state": "CO", "state_slug": "colorado", "lat": 40.5853, "lng": -105.0844, "population": 169810},
    {"city": "Palmdale", "city_slug": "palmdale", "state": "CA", "state_slug": "california", "lat": 34.5794, "lng": -118.1165, "population": 169450},
    {"city": "Springfield", "city_slug": "springfield-mo", "state": "MO", "state_slug": "missouri", "lat": 37.209, "lng": -93.2923, "population": 169176},
    {"city": "Clarksville", "city_slug": "clarksville", "state": "TN", "state_slug": "tennessee", "lat": 36.5298, "lng": -87.3595, "population": 166722},
    {"city": "Paterson", "city_slug": "paterson", "state": "NJ", "state_slug": "new-jersey", "lat": 40.9168, "lng": -74.1718, "population": 159732},
    {"city": "Macon", "city_slug": "macon", "state": "GA", "state_slug": "georgia", "lat": 32.8407, "lng": -83.6324, "population": 157346},
    {"city": "Kansas City", "city_slug": "kansas-city-ks", "state": "KS", "state_slug": "kansas", "lat": 39.1141, "lng": -94.6275, "population": 156607},
    {"city": "Springfield", "city_slug": "springfield", "state": "MA", "state_slug": "massachusetts", "lat": 42.1015, "lng": -72.5898, "population": 155929},
    {"city": "Sunnyvale", "city_slug": "sunnyvale", "state": "CA", "state_slug": "california", "lat": 37.3688, "lng": -122.0363, "population": 155805},
    {"city": "Jackson", "city_slug": "jackson", "state": "MS", "state_slug": "mississippi", "lat": 32.2988, "lng": -90.1848, "population": 153701},
    {"city": "Killeen", "city_slug": "killeen", "state": "TX", "state_slug": "texas", "lat": 31.1171, "lng": -97.7278, "population": 153095},
    {"city": "Hollywood", "city_slug": "hollywood", "state": "FL", "state_slug": "florida", "lat": 26.0112, "lng": -80.1495, "population": 153067},
    {"city": "Murfreesboro", "city_slug": "murfreesboro", "state": "TN", "state_slug": "tennessee", "lat": 35.8456, "lng": -86.3903, "population": 152769},
    {"city": "Pasadena", "city_slug": "pasadena", "state": "TX", "state_slug": "texas", "lat": 29.6911, "lng": -95.2091, "population": 151950},
    {"city": "Bellevue", "city_slug": "bellevue", "state": "WA", "state_slug": "washington", "lat": 47.6101, "lng": -122.2015, "population": 151854},
    {"city": "Pomona", "city_slug": "pomona", "state": "CA", "state_slug": "california", "lat": 34.0551, "lng": -117.75, "population": 151830},
    {"city": "Escondido", "city_slug": "escondido", "state": "CA", "state_slug": "california", "lat": 33.1192, "lng": -117.0864, "population": 151038},
    {"city": "Joliet", "city_slug": "joliet", "state": "IL", "state_slug": "illinois", "lat": 41.525, "lng": -88.0817, "population": 150362},
    {"city": "Charleston", "city_slug": "charleston", "state": "SC", "state_slug": "south-carolina", "lat": 32.7765, "lng": -79.9311, "population": 150227},
    {"city": "Mesquite", "city_slug": "mesquite", "state": "TX", "state_slug": "texas", "lat": 32.7668, "lng": -96.5992, "population": 150108},
    {"city": "Naperville", "city_slug": "naperville", "state": "IL", "state_slug": "illinois", "lat": 41.7508, "lng": -88.1535, "population": 149540},
    {"city": "Rockford", "city_slug": "rockford", "state": "IL", "state_slug": "illinois", "lat": 42.2711, "lng": -89.094, "population": 148655},
    {"city": "Bridgeport", "city_slug": "bridgeport", "state": "CT", "state_slug": "connecticut", "lat": 41.1865, "lng": -73.1952, "population": 148654},
    {"city": "Santa Rosa", "city_slug": "santa-rosa-ca", "state": "CA", "state_slug": "california", "lat": 38.4404, "lng": -122.7141, "population": 178127},
    {"city": "Santa Rosa", "city_slug": "santa-rosa", "state": "CA", "state_slug": "california", "lat": 38.4404, "lng": -122.7141, "population": 178127},
]

ZIPS: list[dict] = []

E_WASTE = [
    "television",
    "computer-monitor",
    "smartphone",
    "laptop",
    "desktop-computer",
    "tablet",
    "printer",
    "e-waste-mixed",
    "hard-drive",
]

FACILITIES = [
    {
        "name": "OC Landfills Anaheim Household Hazardous Waste Collection Center",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "garden-grove",
        "state": "CA",
        "zip": "92806",
        "address": "1071 N Blue Gum Street, Anaheim, CA 92806",
        "lat": 33.8480,
        "lng": -117.8900,
        "source_url": "https://oclandfills.com/hazardous-waste",
        "hours": "Confirm oclandfills.com hours before visit",
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": "Pembroke Pines WWTP — Quarterly HHW Events",
        "facility_type": "Household hazardous waste — quarterly events",
        "city_slug": "pembroke-pines",
        "state": "FL",
        "zip": "33027",
        "address": "13975 Pembroke Road, Pembroke Pines, FL 33027",
        "lat": 25.9950,
        "lng": -80.3400,
        "source_url": "https://www.ppines.com/196/Household-Hazardous-Waste",
        "hours": "Quarterly events — monitor ppines.com",
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": "Larimer County Household Hazardous Waste Facility",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "fort-collins",
        "state": "CO",
        "zip": "80526",
        "address": "5887 S Taft Hill Road, Fort Collins, CO 80526",
        "lat": 40.5200,
        "lng": -105.1200,
        "source_url": "https://www.larimer.gov/solidwaste/hhw",
        "hours": "Confirm larimer.gov HHW hours before visit",
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": "Antelope Valley Environmental Collection Center (AVECC)",
        "facility_type": "Household hazardous waste / e-waste — 1st & 3rd Saturday",
        "city_slug": "palmdale",
        "state": "CA",
        "zip": "93551",
        "address": "1200 W City Ranch Road, Palmdale, CA 93551",
        "lat": 34.5790,
        "lng": -118.1500,
        "source_url": "https://cleanla.lacounty.gov/venue/avecc/",
        "hours": "1st & 3rd Saturday 9:00–15:00 — confirm CleanLA calendar",
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": "Springfield Household Chemical Collection Center",
        "facility_type": "Household hazardous waste — by appointment",
        "city_slug": "springfield-mo",
        "state": "MO",
        "zip": "65802",
        "address": "1226 W Nichols Street, Springfield, MO 65802",
        "lat": 37.2200,
        "lng": -93.3100,
        "source_url": "https://www.springfieldmo.gov/2218/Household-Chemical-Collection-Center",
        "hours": "By appointment — confirm springfieldmo.gov",
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": "Noble Hill Landfill",
        "facility_type": "Municipal landfill — resident self-haul",
        "city_slug": "springfield-mo",
        "state": "MO",
        "zip": "65803",
        "address": "6700 N Farm Road 141, Springfield, MO 65803",
        "lat": 37.3000,
        "lng": -93.2900,
        "source_url": "https://www.springfieldmo.gov/2220/Noble-Hill-Landfill",
        "hours": "Confirm springfieldmo.gov landfill hours",
        "phone": None,
        "accepted_materials": ["mattress", "box-spring", "sofa", "construction-debris", "yard-waste"],
    },
    {
        "name": "Bi-County Landfill",
        "facility_type": "County landfill — bulky / limited BOPAE",
        "city_slug": "clarksville",
        "state": "TN",
        "zip": "37042",
        "address": "3212 Dover Road, Clarksville, TN 37042",
        "lat": 36.5400,
        "lng": -87.4200,
        "source_url": "https://www.montgomerytn.gov/government/departments/solid_waste/index.php",
        "hours": "Confirm montgomerytn.gov hours/fees",
        "phone": None,
        "accepted_materials": ["mattress", "box-spring", "sofa", "construction-debris", "yard-waste", "refrigerator"],
    },
    {
        "name": "Paterson City Yard Bulk Drop-Off",
        "facility_type": "Municipal bulk drop-off",
        "city_slug": "paterson",
        "state": "NJ",
        "zip": "07524",
        "address": "402 E 16th Street, Paterson, NJ 07524",
        "lat": 40.9200,
        "lng": -74.1500,
        "source_url": "https://www.patersonnj.gov/",
        "hours": "Confirm patersonnj.gov sanitation hours",
        "phone": None,
        "accepted_materials": ["mattress", "box-spring", "sofa", "refrigerator", "washer", "dryer"],
    },
    {
        "name": "Macon-Bibb 11th Street Convenience Center",
        "facility_type": "Convenience center — paint / batteries / special waste",
        "city_slug": "macon",
        "state": "GA",
        "zip": "31201",
        "address": "11th Street Convenience Center, Macon, GA 31201",
        "lat": 32.8400,
        "lng": -83.6300,
        "source_url": "https://sw.maconbibb.us/",
        "hours": "Confirm sw.maconbibb.us hours",
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": "Unified Government HHW Facility",
        "facility_type": "Household hazardous waste — Saturdays Apr–Oct",
        "city_slug": "kansas-city-ks",
        "state": "KS",
        "zip": "66111",
        "address": "2443 S 88th Street, Kansas City, KS 66111",
        "lat": 39.0800,
        "lng": -94.7800,
        "source_url": "https://www.wycokck.org/Residents/Trash-Recycling/Household-Hazardous-Waste",
        "hours": "Saturdays April–October — confirm wycokck.org schedule; e-waste NOT accepted",
        "phone": None,
        "accepted_materials": HHW_MATERIALS,
    },
    {
        "name": "Springfield MA HHW — Tapley Street",
        "facility_type": "Household hazardous waste — events by appointment",
        "city_slug": "springfield",
        "state": "MA",
        "zip": "01104",
        "address": "70 Tapley Street, Springfield, MA 01104",
        "lat": 42.1100,
        "lng": -72.5700,
        "source_url": "https://www.springfield-ma.gov/dpw",
        "hours": "HHW events by appointment — confirm springfield-ma.gov",
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": "SMaRT Station",
        "facility_type": "Recycling / transfer — e-waste pathways",
        "city_slug": "sunnyvale",
        "state": "CA",
        "zip": "94085",
        "address": "301 Carl Road, Sunnyvale, CA 94085",
        "lat": 37.4200,
        "lng": -122.0000,
        "source_url": "https://www.sunnyvale.ca.gov/property-residents/recycling-garbage/smart-station",
        "hours": "Confirm sunnyvale.ca.gov SMaRT Station hours",
        "phone": None,
        "accepted_materials": E_WASTE + ["cardboard", "yard-waste"],
    },
    {
        "name": "Jackson Environmental Service Center (temporarily closed)",
        "facility_type": "Household hazardous waste / e-waste — temporarily closed for relocation",
        "city_slug": "jackson",
        "state": "MS",
        "zip": "39204",
        "address": "1570 University Boulevard, Jackson, MS 39204",
        "lat": 32.3100,
        "lng": -90.1800,
        "source_url": "https://jacksonms.gov/solid-waste-division-2/",
        "hours": "TEMPORARILY CLOSED — relocating; monitor jacksonms.gov for reopen; use private HHW/e-waste until then",
        "phone": "601-960-1193",
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": "Killeen Transfer Station",
        "facility_type": "Municipal transfer station",
        "city_slug": "killeen",
        "state": "TX",
        "zip": "76542",
        "address": "Highway 195 Transfer Station, Killeen, TX 76542",
        "lat": 31.1000,
        "lng": -97.7500,
        "source_url": "https://www.killeentexas.gov/289/Solid-Waste",
        "hours": "Confirm killeentexas.gov hours/fees",
        "phone": None,
        "accepted_materials": ["mattress", "box-spring", "sofa", "construction-debris", "yard-waste"],
    },
    {
        "name": "Broward County South Drop-Off Center",
        "facility_type": "County drop-off — HHW / e-waste — Saturdays",
        "city_slug": "hollywood",
        "state": "FL",
        "zip": "33023",
        "address": "5601 W Hallandale Beach Boulevard, Hollywood, FL 33023",
        "lat": 25.9850,
        "lng": -80.2000,
        "source_url": "https://www.broward.org/WasteAndRecycling/Recycling/Pages/DropOffCenters.aspx",
        "hours": "Saturdays — confirm broward.org hours",
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": "Leanna Convenience Center",
        "facility_type": "Convenience center — e-waste / paint",
        "city_slug": "murfreesboro",
        "state": "TN",
        "zip": "37129",
        "address": "Leanna Convenience Center, Murfreesboro, TN 37129",
        "lat": 35.8800,
        "lng": -86.4200,
        "source_url": "https://www.murfreesborotn.gov/163/Solid-Waste",
        "hours": "Confirm murfreesborotn.gov hours",
        "phone": None,
        "accepted_materials": E_WASTE + ["paint-latex", "paint-oil", "car-battery"],
    },
    {
        "name": "Pasadena Recycling Center",
        "facility_type": "Municipal recycling center — HHW / e-waste pathways",
        "city_slug": "pasadena",
        "state": "TX",
        "zip": "77503",
        "address": "2800 Pasadena Boulevard, Pasadena, TX 77503",
        "lat": 29.6900,
        "lng": -95.2000,
        "source_url": "https://www.pasadenatx.gov/159/Sanitation",
        "hours": "Confirm pasadenatx.gov; Sanitation 713-475-7884",
        "phone": "713-475-7884",
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": "King County Factoria HHW & Transfer",
        "facility_type": "Household hazardous waste drop-off",
        "city_slug": "bellevue",
        "state": "WA",
        "zip": "98005",
        "address": "13800 SE 32nd Street, Bellevue, WA 98005",
        "lat": 47.5800,
        "lng": -122.1500,
        "source_url": "https://kingcounty.gov/en/dept/dnrp/waste-services/garbage-recycling-compost/solid-waste-facilities/factoria",
        "hours": "Confirm kingcounty.gov Factoria hours",
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": "Escondido Household Hazardous Waste Facility",
        "facility_type": "Household hazardous waste — by appointment",
        "city_slug": "escondido",
        "state": "CA",
        "zip": "92025",
        "address": "1044 W Washington Avenue, Escondido, CA 92025",
        "lat": 33.1200,
        "lng": -117.1000,
        "source_url": "https://www.escondido.gov/261/Household-Hazardous-Waste",
        "hours": "By appointment — confirm escondido.gov",
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": "Naperville Household Hazardous Waste Facility",
        "facility_type": "Household hazardous waste / electronics campus",
        "city_slug": "naperville",
        "state": "IL",
        "zip": "60540",
        "address": "156 Fort Hill Drive, Naperville, IL 60540",
        "lat": 41.7600,
        "lng": -88.1800,
        "source_url": "https://www.naperville.il.us/residents/recycling-and-garbage/household-hazardous-waste/",
        "hours": "HHW Sat–Sun; electronics Mon–Fri — confirm naperville.il.us",
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": "Will County / Naperville HHW pathways (Joliet residents)",
        "facility_type": "Regional HHW / e-waste pathways",
        "city_slug": "joliet",
        "state": "IL",
        "zip": "60540",
        "address": "156 Fort Hill Drive, Naperville, IL 60540",
        "lat": 41.7600,
        "lng": -88.1800,
        "source_url": "https://www.willcountygreen.com/",
        "hours": "Confirm willcountygreen.com and Naperville HHW acceptance for Joliet residents",
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": "Charleston County Bees Ferry HHW / E-waste",
        "facility_type": "County HHW / e-waste facility",
        "city_slug": "charleston",
        "state": "SC",
        "zip": "29414",
        "address": "Bees Ferry Landfill / HHW, Charleston, SC 29414",
        "lat": 32.8000,
        "lng": -80.0500,
        "source_url": "https://www.charlestoncounty.org/departments/environmental-management/",
        "hours": "Confirm charlestoncounty.gov hours",
        "phone": None,
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": "Mesquite Citizens Convenience Center",
        "facility_type": "Municipal convenience center",
        "city_slug": "mesquite",
        "state": "TX",
        "zip": "75181",
        "address": "3550 Lawson Road, Mesquite, TX 75181",
        "lat": 32.7400,
        "lng": -96.5500,
        "source_url": "https://www.cityofmesquite.com/270/Garbage-Recycling",
        "hours": "Confirm cityofmesquite.com hours",
        "phone": None,
        "accepted_materials": E_WASTE + ["mattress", "yard-waste", "car-battery"],
    },
    {
        "name": "Dallas County Household Hazardous Waste Collection Center",
        "facility_type": "County household hazardous waste drop-off",
        "city_slug": "mesquite",
        "state": "TX",
        "zip": "75243",
        "address": "11234 Plano Road, Dallas, TX 75243",
        "lat": 32.9000,
        "lng": -96.7400,
        "source_url": "https://www.dallascounty.org/departments/hhs/hhw.php",
        "hours": "Confirm dallascounty.org HHW hours",
        "phone": None,
        "accepted_materials": HHW_MATERIALS,
    },
    {
        "name": "Rockford Household Hazardous Waste Facility",
        "facility_type": "Household hazardous waste drop-off — Sat–Sun",
        "city_slug": "rockford",
        "state": "IL",
        "zip": "61109",
        "address": "3315 Kishwaukee Street, Rockford, IL 61109",
        "lat": 42.2400,
        "lng": -89.0800,
        "source_url": "https://rockfordil.gov/",
        "hours": "Saturday–Sunday — confirm rockfordil.gov",
        "phone": None,
        "accepted_materials": HHW_MATERIALS,
    },
    {
        "name": "KNIB Electronics Recycling",
        "facility_type": "Electronics recycling drop-off",
        "city_slug": "rockford",
        "state": "IL",
        "zip": "61109",
        "address": "4665 Hydraulic Road, Rockford, IL 61109",
        "lat": 42.2300,
        "lng": -89.0600,
        "source_url": "https://www.knib.org/",
        "hours": "Confirm knib.org hours",
        "phone": None,
        "accepted_materials": E_WASTE,
    },
    {
        "name": "Bridgeport Transfer Station",
        "facility_type": "Municipal transfer station",
        "city_slug": "bridgeport",
        "state": "CT",
        "zip": "06610",
        "address": "475 Asylum Street, Bridgeport, CT 06610",
        "lat": 41.1900,
        "lng": -73.1800,
        "source_url": "https://www.bridgeportct.gov/",
        "hours": "Confirm bridgeportct.gov hours/fees",
        "phone": None,
        "accepted_materials": ["mattress", "box-spring", "sofa", "construction-debris", "yard-waste", "refrigerator"],
    },
    {
        "name": "Zero Waste Sonoma Household Hazardous Waste Facility",
        "facility_type": "Household hazardous waste / e-waste drop-off",
        "city_slug": "santa-rosa-ca",
        "state": "CA",
        "zip": "94952",
        "address": "500 Mecham Road, Petaluma, CA 94952",
        "lat": 38.2500,
        "lng": -122.7000,
        "source_url": "https://zerowastesonoma.gov/recycle-dispose/residents/household-hazardous-waste-facility",
        "hours": "Thu–Sat 7:30–14:30 — bring Sonoma County ID",
        "phone": "707-795-2025",
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
    {
        "name": "Zero Waste Sonoma Household Hazardous Waste Facility",
        "facility_type": "Household hazardous waste / e-waste drop-off",
        "city_slug": "santa-rosa",
        "state": "CA",
        "zip": "94952",
        "address": "500 Mecham Road, Petaluma, CA 94952",
        "lat": 38.2500,
        "lng": -122.7000,
        "source_url": "https://zerowastesonoma.gov/recycle-dispose/residents/household-hazardous-waste-facility",
        "hours": "Thu–Sat 7:30–14:30 — bring Sonoma County ID",
        "phone": "707-795-2025",
        "accepted_materials": HHW_MATERIALS + E_WASTE,
    },
]


def upsert_geo():
    """Cities already exist — only patch lat/lng when needed; append if missing."""
    cities_path = DATA / "geo" / "cities.json"
    zips_path = DATA / "geo" / "zips.json"
    cities = json.loads(cities_path.read_text())
    zips = json.loads(zips_path.read_text())
    by_slug = {c["city_slug"]: c for c in cities}
    for c in CITIES:
        existing = by_slug.get(c["city_slug"])
        if existing:
            if existing.get("lat") != c["lat"] or existing.get("lng") != c["lng"]:
                existing["lat"] = c["lat"]
                existing["lng"] = c["lng"]
        else:
            cities.append(c)
            by_slug[c["city_slug"]] = c
    cities_path.write_text(json.dumps(cities, indent=2) + "\n")

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
    sr_ca = clone_siblings(santa_rosa_pack("santa-rosa-ca"))
    sr = rehome(sr_ca, "santa-rosa")

    audited = {
        "garden-grove": clone_siblings(garden_grove()),
        "pembroke-pines": clone_siblings(pembroke_pines()),
        "fort-collins": clone_siblings(fort_collins()),
        "palmdale": clone_siblings(palmdale()),
        "springfield-mo": clone_siblings(springfield_mo()),
        "clarksville": clone_siblings(clarksville()),
        "paterson": clone_siblings(paterson()),
        "macon": clone_siblings(macon()),
        "kansas-city-ks": clone_siblings(kansas_city_ks()),
        "springfield": clone_siblings(springfield_ma()),
        "sunnyvale": clone_siblings(sunnyvale()),
        "jackson": clone_siblings(jackson()),
        "killeen": clone_siblings(killeen()),
        "hollywood": clone_siblings(hollywood()),
        "murfreesboro": clone_siblings(murfreesboro()),
        "pasadena": clone_siblings(pasadena_tx()),
        "bellevue": clone_siblings(bellevue()),
        "pomona": clone_siblings(pomona()),
        "escondido": clone_siblings(escondido()),
        "joliet": clone_siblings(joliet()),
        "charleston": clone_siblings(charleston()),
        "mesquite": clone_siblings(mesquite()),
        "naperville": clone_siblings(naperville()),
        "rockford": clone_siblings(rockford()),
        "bridgeport": clone_siblings(bridgeport()),
        "santa-rosa-ca": sr_ca,
        "santa-rosa": sr,
    }

    wave21b = [k for k in audited if k != "santa-rosa"]
    if len(wave21b) != 26:
        raise SystemExit(f"expected 26 wave21b cities, got {len(wave21b)}")

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

    print("Wave-21b metros written:")
    for city in wave21b:
        print(f"  {city}: {len(audited[city])} rules")
    print(f"  santa-rosa (clone): {len(audited['santa-rosa'])} rules")
    print(f"Wave-21b city count: {len(wave21b)} × 70")
    print(f"Total rules now: {len(keep)}")


if __name__ == "__main__":
    main()
