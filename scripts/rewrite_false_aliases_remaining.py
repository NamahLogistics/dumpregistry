#!/usr/bin/env python3
"""Rewrite remaining false-alias city rules.

cardboard / glass ← plastic bags
fire-extinguisher ← propane
prescription-drugs ← sharps
household-batteries / antifreeze ← car battery
ink-toner ← mixed e-waste
car-parts ← construction debris

Skip rows that are already unique (no pathway-clone prefix). Official source URL stays.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PHRASE = "follows the same verified program pathway"
REVIEWED = "false-alias-rewrite"
ITEMS = (
    "cardboard",
    "glass-bottles",
    "fire-extinguisher",
    "prescription-drugs",
    "household-batteries",
    "antifreeze",
    "ink-toner",
    "car-parts",
)


def clip(text: str, n: int) -> str:
    text = " ".join(text.split())
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def faq(pairs: list[tuple[str, str]]) -> list[dict]:
    return [{"q": q, "a": a} for q, a in pairs]


def city_name(cities: dict, slug: str) -> str:
    row = cities.get(slug) or {}
    return row.get("city") or slug.replace("-", " ").title()


def cardboard(city: str, slug: str, src: str) -> dict:
    overrides = {
        "new-york": {
            "answer": (
                f"{city} dual-stream recycling takes clean, flattened cardboard. That is the opposite of "
                "plastic bags: film is not recycling and goes to grocery drop-off. Break down boxes, keep "
                "them dry, and put them with paper/cardboard recycling — not Special Waste and not a bag "
                f"bin. Greasy pizza boxes are usually trash. Confirm set-out on {src} or DSNY recycling."
            ),
            "fee": "Free curbside recycling when clean/dry",
            "facility": "NYC dual-stream cardboard / paper — not store film",
        },
        "houston": {
            "answer": (
                f"{city} Environmental Service Centers list plastic grocery bags and film. That is not "
                "cardboard. Flatten clean boxes for Houston recycling / cart rules — not the ESC film "
                f"drop-off. Wet or food-soaked cardboard is often trash. Confirm on {src} or SWMD recycling."
            ),
            "fee": "Free recycling when accepted in the cart",
            "facility": "Houston recycling cart — not ESC film bins",
        },
        "los-angeles": {
            "answer": (
                f"{city} blue carts take clean cardboard. Grocery film drop-off is bags and wrap only. "
                "Flatten boxes; keep them out of bulky furniture pickup unless they are a collapsed stack "
                f"the city allows. Confirm set-out on {src} or LASAN recycling. Greasy boxes are trash."
            ),
            "fee": "Free blue-cart recycling when clean",
            "facility": "LA blue cart — not store film drop-off",
        },
        "chicago": {
            "answer": (
                f"{city} blue carts take clean flattened cardboard. Recycle by City film/bag guidance is "
                "a different stream. Do not stuff boxes into a store bag barrel. Confirm on {src} or "
                "Streets & San recycling."
            ),
            "fee": "Free blue-cart recycling when clean",
            "facility": "Chicago blue cart — not store film",
        },
        "seattle": {
            "answer": (
                f"{city} recycling carts take clean cardboard. Store film drop-off is not a box path. "
                f"Flatten and keep dry. Confirm set-out on {src} or SPU recycling — not food/yard carts."
            ),
            "fee": "Free recycling cart when clean",
            "facility": "Seattle recycling cart — not store film",
        },
        "san-diego": {
            "answer": (
                f"{city} recycling takes clean cardboard. Get It Done bulky and grocery film bins are "
                f"not the box path. Flatten; trash greasy pizza boxes. Confirm on {src} or Environmental "
                "Services recycling."
            ),
            "fee": "Free recycling when clean",
            "facility": "San Diego recycling — not film take-back",
        },
    }
    spec = overrides.get(slug) or {
        "answer": (
            f"{city} treats clean cardboard as recycling-cart / paper, not plastic film. Do not use a "
            "grocery bag bin for boxes. Flatten, keep dry, and follow the city’s recycling set-out — "
            f"{src} is the official program we verified; if that page only mentions bags, look at the "
            "recycling cart rules on the same city site. Greasy or wet cardboard is often trash or organics."
        ),
        "fee": "Free recycling when the city accepts it",
        "facility": f"{city} recycling cart / drop-off — not store film",
    }
    return pack(
        spec,
        [
            "Flatten clean, dry boxes.",
            "Do not use a grocery film/bag bin for cardboard.",
            f"Confirm recycling set-out on {src} or the city’s recycling page.",
        ],
        [
            ("Same as plastic bags?", "No. Film bins want clean bags and wrap. Cardboard is paper recycling or trash if wet/greasy."),
            ("Pizza boxes?", "If soaked with grease, they are usually trash or organics — not clean cardboard."),
            ("Blue cart?", "Usually yes when clean and dry. Confirm the city’s recycling list."),
        ],
        badge="ACCEPTED_IN_BLUE_BIN",
        hazard="Low",
        curbside=True,
    )


def glass_bottles(city: str, slug: str, src: str) -> dict:
    overrides = {
        "new-york": {
            "answer": (
                f"{city} dual-stream recycling takes empty glass bottles and jars. Plastic bags are the "
                "opposite stream — film is not recycling. Rinse bottles; metal lids follow DSNY metal "
                "rules. Ceramics, mirrors, and window glass are not bottle recycling. Confirm on DSNY "
                f"recycling, not only {src}."
            ),
            "fee": "Free dual-stream recycling",
            "facility": "NYC dual-stream glass — not store film",
        },
        "houston": {
            "answer": (
                f"{city} ESC film drop-off is grocery bags, not glass. Empty bottles and jars go in "
                f"Houston recycling if the current SWMD list includes glass — confirm on {src} or the "
                "recycling page. Window glass and ceramics are not bottle recycling."
            ),
            "fee": "Free recycling if glass is on the SWMD list",
            "facility": "Houston recycling — not ESC film",
        },
        "los-angeles": {
            "answer": (
                f"{city} blue carts take empty glass bottles and jars. Store film drop-off is not glass. "
                f"Rinse; no ceramics or mirrors. Confirm on {src} or LASAN recycling."
            ),
            "fee": "Free blue-cart recycling",
            "facility": "LA blue cart glass — not film bins",
        },
        "chicago": {
            "answer": (
                f"{city} blue carts take empty glass bottles. Film/bag store drop-off is a different "
                f"stream. Confirm on {src} or Recycle by City. No window glass or ceramics."
            ),
            "fee": "Free blue-cart recycling",
            "facility": "Chicago blue cart — not store film",
        },
        "seattle": {
            "answer": (
                f"{city} has a separate glass recycling stream from mixed recycling in many areas. "
                "That is not store film drop-off. Confirm whether your address uses a glass bin or "
                f"drop-off on SPU recycling — {src} may only mention bags. No ceramics or mirrors."
            ),
            "fee": "Free glass recycling / drop-off",
            "facility": "Seattle glass recycling — not store film",
        },
        "san-diego": {
            "answer": (
                f"{city} recycling takes empty glass bottles when they are on the Environmental "
                f"Services list. Film take-back is not glass. Confirm on {src} or the recycling guide."
            ),
            "fee": "Free recycling when listed",
            "facility": "San Diego recycling — not film take-back",
        },
    }
    spec = overrides.get(slug) or {
        "answer": (
            f"{city} empty glass bottles and jars are a recycling-cart or glass-drop-off item in most "
            "U.S. programs — not plastic bags. Do not put bottles in a grocery film bin. Rinse; keep "
            f"ceramics, mirrors, and window glass out. {src} is the official program we verified; if it "
            "only mentions bags, use the city’s recycling list for glass."
        ),
        "fee": "Free recycling when the city accepts glass",
        "facility": f"{city} recycling / glass drop-off — not store film",
    }
    return pack(
        spec,
        [
            "Rinse empty bottles and jars.",
            "Do not use a grocery bag bin for glass.",
            f"Confirm glass on the city recycling list — not only {src} if that page is about film.",
        ],
        [
            ("Same as plastic bags?", "No. Film bins are for bags and wrap. Glass is recycling or a glass drop-off."),
            ("Window glass?", "No. Bottles and jars only unless the city lists other glass."),
            ("Lids?", "Follow the city’s metal/lid rule — do not bag glass inside plastic film."),
        ],
        badge="ACCEPTED_IN_BLUE_BIN",
        hazard="Low",
        curbside=True,
    )


def fire_extinguisher(city: str, slug: str, src: str) -> dict:
    overrides = {
        "houston": {
            "answer": (
                f"{city} Environmental Service Centers take many household hazardous items. A fire "
                "extinguisher is a pressurized cylinder — not a propane BBQ exchange and not a 5-gallon "
                f"propane limit. Confirm extinguishers on {src} before you haul. Do not put it in a cart "
                "or a Blue Rhino cage. Do not puncture it."
            ),
            "fee": "Confirm extinguishers at Houston ESC",
            "facility": "Houston ESC — confirm extinguishers, not propane exchange",
        },
        "new-york": {
            "answer": (
                f"{city} Special Waste Drop-Off does not list gas cylinders on the core accepted list. "
                "Do not assume a fire extinguisher belongs on the oil/paint line. Keep it out of trash "
                f"and recycling. Confirm DSNY / FDNY or SAFE guidance on {src}. This is not propane exchange."
            ),
            "fee": "Confirm DSNY / FDNY extinguisher rules",
            "facility": "Confirm DSNY/SAFE — not Special Waste oil/paint and not propane cages",
        },
        "los-angeles": {
            "answer": (
                f"{city} S.A.F.E. Centers list many HHW items including propane tanks. Confirm fire "
                f"extinguishers on the official materials list at {src} — do not treat them as BBQ "
                "exchange. Keep them off bulky furniture day and out of carts. Do not puncture."
            ),
            "fee": "Confirm extinguishers on the S.A.F.E. list",
            "facility": "LA S.A.F.E. — confirm extinguishers, not propane exchange",
        },
        "chicago": {
            "answer": (
                f"{city} HCCRF lists propane BBQ tanks and household chemicals. Ask whether fire "
                f"extinguishers are accepted before you haul — {src}. This is not a store propane cage. "
                "Do not put extinguishers in carts."
            ),
            "fee": "Confirm extinguishers at HCCRF",
            "facility": "Chicago HCCRF — ask about extinguishers, not BBQ propane",
        },
        "seattle": {
            "answer": (
                f"{city} / King County HHW sites take many pressurized and chemical items. Confirm fire "
                f"extinguishers at North or South HHW — {src}. Do not use a propane exchange cage or "
                "put the unit in garbage or recycling."
            ),
            "fee": "Free King County HHW if listed",
            "facility": "King County HHW — confirm extinguishers",
        },
        "san-diego": {
            "answer": (
                f"{city} Miramar HHW is appointment-only. Confirm fire extinguishers when you book — "
                f"not only propane. {src}. Keep units out of carts. Do not puncture."
            ),
            "fee": "Confirm extinguishers when booking Miramar",
            "facility": "Miramar HHW — confirm extinguishers, not propane",
        },
    }
    spec = overrides.get(slug) or {
        "answer": (
            f"{city} fire extinguishers are pressurized — never trash, recycling, or bulky furniture. "
            "This is not a propane exchange cage. Confirm HHW, fire-department, or special-waste "
            f"acceptance on {src} before you drive. Do not puncture or vent the cylinder at home."
        ),
        "fee": "Confirm HHW / fire-department rules",
        "facility": f"{city} HHW / fire service — confirm, not propane exchange",
    }
    return pack(
        spec,
        [
            "Keep the extinguisher out of carts and dumpsters.",
            "Do not use a propane exchange cage.",
            f"Confirm extinguishers — not only propane — on {src}.",
        ],
        [
            ("Same as propane?", "No. Exchange cages are for grill tanks. Confirm extinguishers on the official HHW or fire-department list."),
            ("Empty it first?", "Do not puncture or vent at home. Ask the receiving site how they want it."),
            ("Bulky pickup?", "No. Pressurized cylinders are not furniture."),
        ],
        badge="SPECIAL_HANDLING",
        hazard="Medium",
        curbside=False,
    )


def prescription_drugs(city: str, slug: str, src: str) -> dict:
    overrides = {
        "houston": {
            "answer": (
                f"{city} pills and patches are not sharps and are not ESC chemical waste by default. "
                "Use a pharmacy or law-enforcement medication take-back box, or a DEA Take Back event. "
                f"Do not put medicines in a sharps container or flush them unless the drug is on the FDA "
                f"flush list and you have no take-back. Confirm on {src} only if it lists medications — "
                "otherwise use take-back, not the sharps/HHW line."
            ),
            "fee": "Free pharmacy / police take-back",
            "facility": "Pharmacy or law-enforcement take-back — not ESC sharps",
        },
        "new-york": {
            "answer": (
                f"{city} prescription drugs are not Special Waste oil/paint and not sharps. Use NYC "
                "pharmacy or NYPD medication drop boxes, or DEA events. Do not flush except FDA "
                f"flush-list drugs with no take-back. Do not put pills in a sharps tub. {src} is the "
                "program we verified for other special waste — confirm meds separately."
            ),
            "fee": "Free pharmacy / NYPD take-back",
            "facility": "NYC pharmacy or NYPD med drop box — not Special Waste / sharps",
        },
        "los-angeles": {
            "answer": (
                f"{city} unused medicines are a take-back stream, not S.A.F.E. sharps. Use a pharmacy "
                "or law-enforcement drop box, or a DEA event. Do not put pills in a needle container "
                f"and do not flush except FDA flush-list drugs. Confirm medications on {src} only if "
                "listed; otherwise use take-back."
            ),
            "fee": "Free pharmacy / police take-back",
            "facility": "LA pharmacy or sheriff/police drop box — not S.A.F.E. sharps",
        },
        "chicago": {
            "answer": (
                f"{city} HCCRF is household chemicals and e-waste — not a pill take-back. Use a "
                "pharmacy or CPD medication drop box, or a DEA event. Do not mix pills into a sharps "
                f"container. Confirm on {src} only if medications are listed."
            ),
            "fee": "Free pharmacy / police take-back",
            "facility": "Chicago pharmacy or CPD drop box — not HCCRF sharps",
        },
        "seattle": {
            "answer": (
                f"{city} / King County HHW sites are for chemicals, not a default medication bin. Use "
                "a pharmacy or law-enforcement take-back, or a DEA event. Do not put pills with sharps. "
                f"Confirm medications on {src} before you haul them to North/South HHW."
            ),
            "fee": "Free pharmacy / police take-back",
            "facility": "Pharmacy or take-back box — confirm before King County HHW",
        },
        "san-diego": {
            "answer": (
                f"{city} Miramar HHW is appointment chemicals and e-waste. Pills are usually a "
                "pharmacy or law-enforcement take-back, not a sharps load. Confirm medications when "
                f"you book — {src} — or use a DEA event. Do not flush except FDA flush-list drugs."
            ),
            "fee": "Free pharmacy / police take-back",
            "facility": "San Diego pharmacy take-back — confirm before Miramar HHW",
        },
    }
    spec = overrides.get(slug) or {
        "answer": (
            f"{city} prescription drugs are not sharps. Use a pharmacy or law-enforcement medication "
            "take-back box, or a DEA National Prescription Take Back event. Do not put pills in a "
            "needle container, and do not flush unless the specific drug is on the FDA flush list and "
            f"you have no take-back. {src} is the official program we verified — confirm it lists "
            "medications before you treat it as the drop-off."
        ),
        "fee": "Free pharmacy / police take-back",
        "facility": f"{city} pharmacy or police take-back — not sharps",
    }
    return pack(
        spec,
        [
            "Keep pills and patches out of sharps containers.",
            "Use a pharmacy or law-enforcement take-back box, or a DEA event.",
            "Do not flush except FDA flush-list drugs when no take-back exists.",
        ],
        [
            ("Same as sharps?", "No. Needles go in a puncture container. Pills go to medication take-back."),
            ("Flush them?", "Only if the specific drug is on the FDA flush list and you have no take-back option."),
            ("HHW?", "Some HHW sites refuse medications. Confirm before you drive."),
        ],
        badge="SPECIAL_HANDLING",
        hazard="Medium",
        curbside=False,
    )


def household_batteries(city: str, slug: str, src: str) -> dict:
    overrides = {
        "houston": {
            "answer": (
                f"{city} ESC accepts many batteries, but AA/AAA alkalines are not a lead-acid car-battery "
                "core exchange. Tape terminals on lithium and rechargeable packs. Auto-parts stores want "
                f"12V car batteries, not a bag of household cells. Confirm household batteries on {src}. "
                "Do not put loose lithium in a cart."
            ),
            "fee": "Confirm household batteries at ESC",
            "facility": "Houston ESC / retail battery bin — not car-battery core exchange",
        },
        "new-york": {
            "answer": (
                f"{city} Special Waste Drop-Off takes many batteries (tape lithium/rechargeable terminals). "
                "That is not the same as a lead-acid car-battery retailer return. Alkalines may have a "
                f"different rule than lithium. Confirm household batteries on {src}. Keep packs out of "
                "trash and recycling carts."
            ),
            "fee": "Free Special Waste for listed batteries",
            "facility": "DSNY Special Waste — household batteries, not auto core exchange",
        },
        "los-angeles": {
            "answer": (
                f"{city} S.A.F.E. Centers take many batteries. Household AA/AAA, button cells, and "
                "rechargeable packs are not a car-battery core swap. Tape lithium terminals. Confirm "
                f"household batteries on {src}. Do not put loose packs in a blue cart."
            ),
            "fee": "Free S.A.F.E. if listed",
            "facility": "LA S.A.F.E. / retail bin — not auto-parts core exchange",
        },
        "chicago": {
            "answer": (
                f"{city} HCCRF lists rechargeable batteries among HHW. Alkaline AAs may differ. This is "
                f"not a lead-acid car-battery counter. Tape terminals. Confirm on {src}."
            ),
            "fee": "Confirm household batteries at HCCRF",
            "facility": "Chicago HCCRF / retail bin — not car-battery exchange",
        },
        "seattle": {
            "answer": (
                f"{city} / King County HHW takes many household and rechargeable batteries. That is not "
                f"an auto-parts core exchange for 12V lead-acid. Tape lithium terminals. Confirm on {src}."
            ),
            "fee": "Free King County HHW if listed",
            "facility": "King County HHW / retail bin — not car-battery exchange",
        },
        "san-diego": {
            "answer": (
                f"{city} Miramar HHW takes many batteries by appointment. Ask for household / "
                f"rechargeable packs, not a car battery. Tape lithium terminals. {src}."
            ),
            "fee": "Confirm household batteries when booking Miramar",
            "facility": "Miramar HHW / retail bin — not car-battery exchange",
        },
    }
    spec = overrides.get(slug) or {
        "answer": (
            f"{city} household batteries (AA/AAA, 9V, button cells, rechargeable packs) are not car "
            "batteries. Auto-parts core exchange is for 12V lead-acid. Alkaline rules vary — some cities "
            "allow trash, many want HHW or a retail battery bin. Lithium and button cells should be taped "
            f"and kept out of carts. Confirm household batteries on {src}."
        ),
        "fee": "Confirm HHW or retail battery drop-off",
        "facility": f"{city} HHW / retail battery bin — not car-battery exchange",
    }
    return pack(
        spec,
        [
            "Sort alkaline vs lithium/rechargeable vs button cells.",
            "Tape lithium and button-cell terminals.",
            "Do not take a bag of AAs to an auto-parts car-battery counter.",
        ],
        [
            ("Same as a car battery?", "No. Lead-acid cores go to auto parts. Household cells go to HHW or a retail battery bin."),
            ("Trash alkalines?", "Only if the official city page allows it. Lithium and button cells should not go in carts."),
            ("Blue bin?", "No. Batteries are a fire and contamination risk in recycling."),
        ],
        badge="BANNED_FROM_LANDFILLS",
        hazard="Medium",
        curbside=False,
    )


def antifreeze(city: str, slug: str, src: str) -> dict:
    overrides = {
        "houston": {
            "answer": (
                f"{city} ESC takes many automotive fluids. Antifreeze (ethylene glycol) is not a car "
                "battery. Keep it sealed, do not mix it with used oil, and do not pour it in a drain. "
                f"Confirm antifreeze on {src}. Auto-parts take-back, if offered, is a separate counter "
                "from battery cores."
            ),
            "fee": "Confirm antifreeze at Houston ESC",
            "facility": "Houston ESC / auto-parts fluid take-back — not battery cores",
        },
        "new-york": {
            "answer": (
                f"{city} Special Waste lists motor oil and many chemicals. Confirm antifreeze on that "
                "list before you haul — it is not a car battery. Do not pour coolant in a drain or storm "
                f"sewer. {src}."
            ),
            "fee": "Confirm antifreeze at Special Waste",
            "facility": "DSNY Special Waste — antifreeze if listed, not battery cores",
        },
        "los-angeles": {
            "answer": (
                f"{city} S.A.F.E. Centers take many automotive fluids. Confirm antifreeze on the "
                f"materials list — {src}. This is not a lead-acid battery drop. Keep it sealed; never "
                "dump it on soil or in a gutter."
            ),
            "fee": "Confirm antifreeze at S.A.F.E.",
            "facility": "LA S.A.F.E. — antifreeze, not car-battery exchange",
        },
        "chicago": {
            "answer": (
                f"{city} HCCRF lists auto fluids among HHW. Confirm antifreeze (not only batteries) "
                f"on {src}. Do not mix coolant into used oil. Do not pour it down a drain."
            ),
            "fee": "Confirm antifreeze at HCCRF",
            "facility": "Chicago HCCRF — auto fluids, not battery cores",
        },
        "seattle": {
            "answer": (
                f"{city} / King County HHW takes many automotive fluids. Confirm antifreeze at North "
                f"or South HHW — {src}. This is not a car-battery counter. Never storm-drain dump."
            ),
            "fee": "Free King County HHW if listed",
            "facility": "King County HHW — antifreeze, not battery cores",
        },
        "san-diego": {
            "answer": (
                f"{city} Miramar HHW lists used oil and many chemicals. Confirm antifreeze when you "
                f"book — {src}. Do not treat it as a car battery. Keep it sealed."
            ),
            "fee": "Confirm antifreeze when booking Miramar",
            "facility": "Miramar HHW — antifreeze, not battery cores",
        },
    }
    spec = overrides.get(slug) or {
        "answer": (
            f"{city} antifreeze is household hazardous / automotive fluid — not a car battery. Keep it "
            "in a sealed jug, do not mix it with used oil, and never pour it down a drain or onto soil. "
            f"Confirm antifreeze on {src} or an auto-parts fluid take-back. Pets are poisoned by sweet "
            "coolant spills — clean drips."
        ),
        "fee": "Confirm HHW or auto-parts fluid take-back",
        "facility": f"{city} HHW / auto-parts fluids — not car-battery exchange",
    }
    return pack(
        spec,
        [
            "Keep antifreeze sealed and separate from used oil.",
            "Do not pour it down a drain or storm sewer.",
            f"Confirm antifreeze — not car batteries — on {src}.",
        ],
        [
            ("Same as a car battery?", "No. Batteries are lead-acid cores. Antifreeze is a toxic liquid HHW / fluid take-back."),
            ("Mix with oil?", "No. Mixed fluids are often rejected."),
            ("Drain it in the yard?", "No. Coolant poisons pets and contaminates water."),
        ],
        badge="BANNED_FROM_LANDFILLS",
        hazard="High",
        curbside=False,
    )


def ink_toner(city: str, slug: str, src: str) -> dict:
    overrides = {
        "houston": {
            "answer": (
                f"{city} ESC e-scrap is computers and electronics. Ink and toner cartridges are usually "
                "retailer mail-back or store take-back first — not a TV/computer load. Keep powder "
                f"contained. Confirm cartridges on {src} only if listed; otherwise use the maker’s bag "
                "or an office-supply take-back."
            ),
            "fee": "Free retailer mail-back / take-back",
            "facility": "Retailer cartridge take-back — confirm before ESC e-scrap",
        },
        "new-york": {
            "answer": (
                f"{city} covered-electronics rules are TVs and computers. Cartridges are a retailer "
                "mail-back / store take-back item. Do not put loose toner in DSNY trash or mix powder "
                f"into an e-waste crate. Confirm on {src} only if cartridges are listed."
            ),
            "fee": "Free retailer mail-back / take-back",
            "facility": "NYC retailer cartridge take-back — not Special Waste e-waste",
        },
        "los-angeles": {
            "answer": (
                f"{city} S.A.F.E. / bulky e-waste is screens and computers. Use manufacturer or "
                "office-supply cartridge take-back first. Confirm ink/toner on {src} before you add "
                "them to an electronics bulky pile."
            ),
            "fee": "Free retailer mail-back / take-back",
            "facility": "LA retailer cartridge take-back — confirm before S.A.F.E. e-waste",
        },
        "chicago": {
            "answer": (
                f"{city} HCCRF e-cycle is TVs, computers, and printers as devices. Loose ink/toner "
                "is usually store mail-back. Confirm cartridges on {src} before you treat them as "
                "Illinois e-waste."
            ),
            "fee": "Free retailer mail-back / take-back",
            "facility": "Chicago retailer take-back — confirm before HCCRF e-cycle",
        },
        "seattle": {
            "answer": (
                f"{city} / King County HHW and e-waste are not an automatic toner program. Use "
                f"retailer mail-back first; confirm cartridges on {src} before you haul powder to HHW."
            ),
            "fee": "Free retailer mail-back / take-back",
            "facility": "Seattle retailer take-back — confirm before King County HHW",
        },
        "san-diego": {
            "answer": (
                f"{city} Miramar e-waste is appointment electronics. Cartridges are usually store "
                f"mail-back. Confirm ink/toner when you book — {src} — and keep powder bagged."
            ),
            "fee": "Free retailer mail-back / take-back",
            "facility": "San Diego retailer take-back — confirm before Miramar e-waste",
        },
    }
    spec = overrides.get(slug) or {
        "answer": (
            f"{city} ink and toner cartridges are retailer mail-back or store take-back first — not "
            "mixed household e-waste. A TV/computer drop-off may refuse loose cartridges or powder. "
            f"Keep them in a bag or the original box. Confirm cartridges on {src} only if listed; "
            "otherwise use the manufacturer prepaid bag or an office-supply counter."
        ),
        "fee": "Free retailer mail-back / take-back",
        "facility": f"{city} retailer cartridge take-back — not mixed e-waste",
    }
    return pack(
        spec,
        [
            "Keep toner powder contained in a bag or the original cartridge box.",
            "Use manufacturer mail-back or an office-supply take-back first.",
            f"Confirm cartridges on {src} only if the e-waste list names them.",
        ],
        [
            ("Same as mixed e-waste?", "Usually not. E-waste sites are built for TVs and computers. Cartridges are a retail take-back."),
            ("Trash the powder?", "Do not dump loose toner. Bag leaks and use take-back."),
            ("Printer too?", "The printer is e-waste. The cartridge is a separate take-back."),
        ],
        badge="SPECIAL_HANDLING",
        hazard="Low",
        curbside=False,
    )


def car_parts(city: str, slug: str, src: str) -> dict:
    overrides = {
        "houston": {
            "answer": (
                f"{city} junk-waste / Neighborhood Depository rules are for household bulky and limited "
                "building materials — not engines, axles, or oily auto parts. Take car parts to an auto "
                "recycler or scrap yard. Drain fluids; batteries and fuel tanks are separate HHW/retail "
                f"streams. Confirm on {src} only if it lists auto parts — otherwise do not use heavy-trash day."
            ),
            "fee": "Auto recycler / scrap — not heavy trash",
            "facility": "Houston auto recycler / scrap — not junk-waste depository",
        },
        "new-york": {
            "answer": (
                f"{city} bulk and C&D carting are not an auto-parts program. Use a licensed auto recycler "
                "or scrap facility. Fluids, batteries, and air bags stay out of a debris box. Confirm "
                f"on {src} only if it lists auto parts."
            ),
            "fee": "Auto recycler / scrap fees",
            "facility": "NYC auto recycler / scrap — not DSNY bulk or C&D",
        },
        "los-angeles": {
            "answer": (
                f"{city} bulky collection excludes contractor C&D and is not a wrecking-yard stand-in. "
                "Take fenders, engines, and drivetrain parts to an auto recycler. Drain oil; keep the "
                f"car battery on the retailer/HHW path. Confirm on {src} only if auto parts are listed."
            ),
            "fee": "Auto recycler / scrap — not LASAN bulky",
            "facility": "LA auto recycler / scrap — not bulky or C&D debris box",
        },
        "chicago": {
            "answer": (
                f"{city} bulky pickup and debris boxes are not auto scrap. Use a licensed auto recycler. "
                f"Keep fluids and batteries off the load. Confirm on {src} only if it lists car parts."
            ),
            "fee": "Auto recycler / scrap — not city bulky",
            "facility": "Chicago auto recycler — not bulky or HCCRF",
        },
        "seattle": {
            "answer": (
                f"{city} transfer stations may take some scrap metal — confirm auto parts and fluid "
                f"rules before you haul. {src}. A mixed C&D debris box is the wrong default for an engine. "
                "Batteries and gasoline stay on HHW/retail paths."
            ),
            "fee": "Confirm transfer / auto-recycler fees",
            "facility": "Seattle transfer or auto recycler — confirm, not generic C&D",
        },
        "san-diego": {
            "answer": (
                f"{city} Miramar Landfill / debris-box C&D is not an automatic auto-parts recycler. "
                "Use an auto wrecker or scrap yard; drain fluids. Confirm car parts on Environmental "
                f"Services or {src} before you mix them into a remodel load."
            ),
            "fee": "Auto recycler / landfill fees if listed",
            "facility": "San Diego auto recycler — confirm before C&D / landfill",
        },
    }
    spec = overrides.get(slug) or {
        "answer": (
            f"{city} car parts go to an auto recycler or scrap yard — not a household C&D debris box "
            "and not bulky furniture day. Drain oil and coolant; take batteries and fuel tanks on their "
            f"own HHW/retail paths. {src} is the official program we verified; confirm it lists auto "
            "parts before you treat a remodel transfer station as the drop-off."
        ),
        "fee": "Auto recycler / scrap — confirm, not C&D",
        "facility": f"{city} auto recycler / scrap — not construction debris",
    }
    return pack(
        spec,
        [
            "Drain fluids; keep batteries and fuel tanks off the metal load.",
            "Use an auto recycler or scrap yard, not bulky furniture day.",
            f"Confirm auto parts on {src} before mixing them into C&D.",
        ],
        [
            ("Same as construction debris?", "No. Drywall and lumber are C&D. Engines, axles, and body parts are auto scrap."),
            ("Leave oil in it?", "No. Drain fluids. Mixed oily loads get rejected or surcharged."),
            ("Catalytic converter?", "Use a licensed scrap/auto recycler. Do not curbside it."),
        ],
        badge="SPECIAL_HANDLING",
        hazard="Medium",
        curbside=False,
    )


def pack(
    spec: dict,
    steps: list[str],
    faqs: list[tuple[str, str]],
    *,
    badge: str,
    hazard: str,
    curbside: bool,
) -> dict:
    return {
        "answer": spec["answer"],
        "steps": steps,
        "faqs": faq(faqs),
        "common_disposal_fee": clip(spec["fee"], 80),
        "nearest_facility_type": clip(spec["facility"], 120),
        "badge": badge,
        "hazard_rating": hazard,
        "is_curbside_allowed": curbside,
    }


BUILDERS = {
    "cardboard": cardboard,
    "glass-bottles": glass_bottles,
    "fire-extinguisher": fire_extinguisher,
    "prescription-drugs": prescription_drugs,
    "household-batteries": household_batteries,
    "antifreeze": antifreeze,
    "ink-toner": ink_toner,
    "car-parts": car_parts,
}


def main() -> None:
    cities = {c["city_slug"]: c for c in json.loads((DATA / "geo" / "cities.json").read_text())}
    path = DATA / "rules" / "all.json"
    rules = json.loads(path.read_text())
    n = skipped = 0
    for r in rules:
        item = r.get("item_slug")
        slug = r.get("city_slug")
        if item not in BUILDERS or not slug:
            continue
        if PHRASE not in (r.get("answer") or "").lower():
            skipped += 1
            continue
        built = BUILDERS[item](city_name(cities, slug), slug, r.get("source_name") or "the official program")
        r.update(built)
        r["reviewed_by"] = REVIEWED
        r["needs_review"] = False
        n += 1
    path.write_text(json.dumps(rules, indent=2) + "\n")
    print(f"Rewrote {n} clone rules; kept {skipped} already-unique rows")


if __name__ == "__main__":
    main()
