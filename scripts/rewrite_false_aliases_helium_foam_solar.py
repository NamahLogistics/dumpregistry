#!/usr/bin/env python3
"""Rewrite helium, styrofoam, and solar city rules.

These were cloned from propane / plastic bags / mixed e-waste. The official
source URL stays (it is still the city/county program we verified). The answer
must not claim that program accepts the item unless a researched override says so.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ITEMS = ("helium-tank", "styrofoam", "solar-panel")
REVIEWED = "false-alias-rewrite"


def clip(text: str, n: int) -> str:
    text = " ".join(text.split())
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def faq(pairs: list[tuple[str, str]]) -> list[dict]:
    return [{"q": q, "a": a} for q, a in pairs]


def city_name(cities: dict, slug: str) -> str:
    row = cities.get(slug) or {}
    return row.get("city") or slug.replace("-", " ").title()


def helium(city: str, slug: str, src: str) -> dict:
    overrides = {
        "houston": {
            "answer": (
                f"{city} does not put helium tanks in trash or recycling carts. Disposable retail "
                "party tanks and refillable rental cylinders are different products. Helium is not "
                "flammable; leftover pressure is still a packer hazard. City of Houston SWMD tells "
                "residents that empty disposable helium tanks may follow the maker’s empty-then-puncture "
                "steps, then a recycling center or scrap yard — and Environmental Service Centers handle "
                "household hazardous / special waste. Propane exchange cages and the ESC 5-gallon propane "
                "limit are not a helium path. Return a rental tank to the supplier. Confirm the current "
                f"{src} page before you puncture anything."
            ),
            "fee": "Confirm helium on SWMD/ESC — not the propane fee",
            "facility": "Houston ESC or scrap only if SWMD allows empty-puncture",
            "steps": [
                "Identify disposable party tank vs refillable rental.",
                "Do not put any helium tank in a Houston cart.",
                "Read the current SWMD/ESC page before puncturing a disposable tank.",
                "Return rentals to the supplier; do not use a propane exchange cage.",
            ],
        },
        "new-york": {
            "answer": (
                f"{city} Special Waste Drop-Off (oil, paint, many batteries) does not list propane or "
                "gas cylinders on the core accepted list. Do not haul a party helium tank to that line "
                "expecting it to be taken. Disposable helium is not recycling-cart metal and is not "
                "regular trash. Use DSNY gas-cylinder / SAFE Disposal Event guidance, or return a "
                "refillable tank to the supplier. Helium is not propane — do not follow BBQ-tank advice. "
                f"Confirm on {src} before you drive."
            ),
            "fee": "Confirm DSNY gas-cylinder / SAFE rules",
            "facility": "DSNY SAFE / gas-cylinder guidance — not Special Waste oil/paint",
            "steps": [
                "Do not take helium to a Special Waste oil/paint site.",
                "Keep tanks out of NYC trash and dual-stream recycling.",
                "Use SAFE events or DSNY cylinder guidance; return rentals to the supplier.",
            ],
        },
        "los-angeles": {
            "answer": (
                f"{city} S.A.F.E. Centers list propane tanks among HHW. That is not automatic helium "
                "acceptance. Do not put helium tanks in LASAN trash, recycling, or bulky furniture "
                "pickup. Disposable party tanks and refillable rentals are different — return rentals "
                "to the supplier. Confirm helium (not only propane) on the official S.A.F.E. materials "
                f"list at {src} before you haul. Do not puncture a tank unless that list says to."
            ),
            "fee": "Confirm helium on the S.A.F.E. list",
            "facility": "LA S.A.F.E. Centers — confirm helium, not only propane",
            "steps": [
                "Keep helium off trash, recycling, and bulky set-out.",
                "Check the S.A.F.E. accepted-materials list for helium.",
                "Return refillable cylinders to the supplier.",
            ],
        },
        "san-diego": {
            "answer": (
                f"{city} residents use the Miramar HHW Transfer Facility by appointment for many "
                "pressurized and hazardous items. Helium is not the same as propane. Confirm the "
                f"facility lists helium — not only BBQ tanks — on {src} before you book. Do not put "
                "tanks in trash or recycling carts. Return refillable cylinders to the supplier. Do not "
                "puncture a disposable tank unless the city page allows empty-and-scrap."
            ),
            "fee": "Confirm helium when booking Miramar HHW",
            "facility": "Miramar HHW Transfer Facility — confirm helium",
            "steps": [
                "Do not cart a helium tank.",
                "Ask Miramar HHW whether helium is accepted when you book.",
                "Return rentals to the supplier.",
            ],
        },
        "chicago": {
            "answer": (
                f"{city}’s Household Chemicals & Computer Recycling Facility lists propane BBQ tanks. "
                "Ask whether disposable helium is in that lane before you haul — do not assume the "
                "propane rule covers a party tank. Helium is not flammable; carts are still unsafe. "
                f"Confirm on {src}. Return refillable tanks to the supplier. Do not puncture unless "
                "the city program says empty-and-scrap is allowed."
            ),
            "fee": "Confirm helium at HCCRF — not the propane lane",
            "facility": "Chicago HCCRF — ask about helium, not only BBQ propane",
            "steps": [
                "Call or check HCCRF for helium, not only propane BBQ tanks.",
                "Keep tanks out of Chicago carts.",
                "Return rentals to the supplier.",
            ],
        },
        "burbank": {
            "answer": (
                f"{city} recycling guidance is the opposite of some manufacturer boxes: do not puncture "
                "a helium tank so staff can tell a live cylinder from an emptied one. Take the intact "
                f"tank to HHW / special-waste per {src}. This is not propane exchange and not curbside "
                "metal. Return refillable cylinders to the supplier."
            ),
            "fee": "Confirm HHW / special-waste for intact tanks",
            "facility": "Burbank HHW / special-waste — intact tanks, do not puncture",
            "steps": [
                "Do not puncture the tank.",
                "Take it intact to the HHW / special-waste path on the city page.",
                "Return rentals to the supplier.",
            ],
        },
    }
    spec = overrides.get(slug)
    if spec:
        body = spec
    else:
        body = {
            "answer": (
                f"{city} residents should not put helium tanks in trash or recycling carts. Disposable "
                "party tanks and refillable rental cylinders are different products. Helium is not "
                "flammable, but leftover pressure is still a packer hazard. This is not the propane "
                f"pathway. {src} is the official {city} program we verified — confirm they list helium "
                "(not only BBQ propane) before you drive. If they do not, ask HHW/special-waste staff, "
                "or return a refillable tank to the supplier. Only puncture a disposable retail tank if "
                "that official page allows empty-and-scrap."
            ),
            "fee": "Confirm helium on the official program",
            "facility": f"{city} HHW / special-waste — confirm helium, not propane",
            "steps": [
                "Identify disposable party tank vs refillable rental.",
                "Keep every helium tank out of trash and recycling carts.",
                f"Confirm helium — not only propane — on {src}.",
                "Return rentals to the supplier; do not use a propane exchange cage.",
            ],
        }
    return {
        "answer": body["answer"],
        "steps": body["steps"],
        "faqs": faq(
            [
                ("Same as propane?", "No. Helium is not flammable. Confirm helium on the official list — propane cages and BBQ-tank rules do not apply."),
                ("Can I puncture it?", "Only if the official city/county page allows empty-and-scrap for a disposable retail tank. Many HHW sites want the tank intact."),
                ("Trash or recycling cart?", "No. Residual pressure is a packer hazard even when the gas is inert."),
            ]
        ),
        "common_disposal_fee": clip(body["fee"], 80),
        "nearest_facility_type": clip(body["facility"], 120),
        "badge": "SPECIAL_HANDLING",
        "hazard_rating": "Medium",
        "is_curbside_allowed": False,
    }


def styrofoam(city: str, slug: str, src: str) -> dict:
    overrides = {
        "new-york": {
            "answer": (
                f"{city} dual-stream recycling does not take foam. DSNY lists foam products, including "
                "packing peanuts, as not metal/glass/plastic recycling. Leftover household EPS goes in "
                "garbage, bagged so beads do not blow. Grocery film bins are not a foam drop-off. Food "
                f"trays and cups are trash. Confirm on {src}. This is not the plastic-bag pathway."
            ),
            "fee": "Trash — not recycling",
            "facility": "NYC garbage — foam is not dual-stream recycling",
            "steps": [
                "Keep foam out of NYC recycling.",
                "Bag blocks and peanuts so beads do not scatter.",
                "Do not use a grocery film bin for EPS.",
            ],
        },
        "houston": {
            "answer": (
                f"{city} Environmental Service Centers list plastic grocery bags and plastic film. That "
                "is not expanded polystyrene. Do not put EPS blocks, peanuts, or food trays in the film "
                "drop-off or in curbside recycling. Bag foam for trash unless SWMD names a foam densifier. "
                f"Confirm foam — not film — on {src}."
            ),
            "fee": "Trash unless SWMD names foam",
            "facility": "Houston trash / confirm foam — ESC film bins are not EPS",
            "steps": [
                "Do not use ESC film/bag drop-off for Styrofoam blocks.",
                "Keep foam out of Houston recycling carts.",
                "Bag it for trash unless the official page names a densifier.",
            ],
        },
        "frisco": {
            "answer": (
                f"{city} publishes a resident foam drop-off for clean white packaging EPS (densifier). "
                "Meat trays, foodware, and starch/“biodegradable” peanuts are not that stream. Plastic "
                f"bag / film take-back is a different program. Confirm hours and prep on {src} before "
                "you haul. If you only have dirty food foam, bag it for trash."
            ),
            "fee": "Confirm Frisco foam drop-off hours",
            "facility": "Frisco clean-packaging EPS densifier — not film bins",
            "steps": [
                "Take only clean, dry, white packaging foam if using the city densifier.",
                "Keep meat trays and starch peanuts out of that drop-off.",
                "Film bags stay on the store take-back path — not foam.",
            ],
        },
        "los-angeles": {
            "answer": (
                f"{city} does not put EPS foam in the blue cart. Plastic-bag store drop-off is film only "
                "— not TV-box foam or peanuts. Food trays are trash. Bag clean packing foam for garbage "
                f"unless {src} names a densifier. Do not wishcycle foam because it has a 6."
            ),
            "fee": "Trash unless LASAN names a densifier",
            "facility": "LA trash / confirm foam — not grocery film bins",
            "steps": [
                "Keep foam out of blue carts and bag-store barrels.",
                "Bag it for trash unless the official page names EPS drop-off.",
                "Peanuts may be reused at a shipper if clean and dry.",
            ],
        },
        "san-diego": {
            "answer": (
                f"{city} recycling carts do not want Styrofoam. Store film drop-off is not a foam "
                "densifier. Treat block foam and food trays as bagged trash unless Environmental "
                f"Services names an EPS site on {src}. Clean peanuts can sometimes be reused at a "
                "parcel store — ask first."
            ),
            "fee": "Trash unless the city names EPS drop-off",
            "facility": "San Diego trash / confirm foam — not film take-back",
            "steps": [
                "Do not blue-bin foam.",
                "Do not use grocery film bins for EPS blocks.",
                "Bag foam for trash unless the official page names a densifier.",
            ],
        },
        "chicago": {
            "answer": (
                f"{city} blue carts do not take foam. Recycle by City film/bag guidance is not a "
                "Styrofoam path. Bag EPS for garbage unless the official program names a densifier. "
                f"Confirm on {src}. Food trays stay in trash."
            ),
            "fee": "Trash unless a named densifier exists",
            "facility": "Chicago trash / confirm foam — not store film",
            "steps": [
                "Keep foam out of the blue cart.",
                "Do not mix foam into store film drop-off.",
                "Bag it for trash unless the city names EPS recycling.",
            ],
        },
    }
    spec = overrides.get(slug)
    if spec:
        body = spec
    else:
        body = {
            "answer": (
                f"{city} recycling carts do not want expanded polystyrene (EPS). White block foam, "
                "packing peanuts, and food trays are different streams. Grocery film/bag bins are not "
                f"a foam drop-off. {src} is the official {city} program we verified — if that page only "
                "mentions plastic bags or film, treat block foam and food trays as bagged garbage unless "
                "it names a foam densifier. Clean peanuts may be reused at a shipper; starch peanuts are "
                "not EPS."
            ),
            "fee": "Trash unless the official page names foam",
            "facility": f"{city} trash / confirm EPS densifier — not film bins",
            "steps": [
                "Keep foam out of the recycling cart.",
                "Do not use a grocery bag barrel for EPS blocks.",
                f"Read {src}: densifier if named, otherwise bag for trash.",
            ],
        }
    return {
        "answer": body["answer"],
        "steps": body["steps"],
        "faqs": faq(
            [
                ("Same as plastic bags?", "No. Store film bins want clean bags and wrap, not EPS blocks, peanuts, or food trays."),
                ("Blue cart?", "Almost never. Foam shatters and contaminates paper and containers."),
                ("Food trays?", "Trash at nearly every site, even where clean packaging foam is accepted."),
            ]
        ),
        "common_disposal_fee": clip(body["fee"], 80),
        "nearest_facility_type": clip(body["facility"], 120),
        "badge": "SPECIAL_HANDLING",
        "hazard_rating": "Low",
        "is_curbside_allowed": False,
    }


def solar(city: str, slug: str, src: str) -> dict:
    body = {
        "answer": (
            f"A solar panel is not mixed household e-waste in {city}. TV and computer drop-off usually "
            "will not take a full PV module. Do not put panels in trash or the recycling cart — glass, "
            "laminate, and junction boxes are not MRF material, and a panel still produces voltage in "
            f"light. Ask the installer about take-back. {src} is the official {city} program we verified "
            "— confirm they list solar / PV. If they only list TVs and computers, use a specialty PV "
            "recycler or a transfer/C&D site they name, not the e-waste line."
        ),
        "fee": "Confirm PV recycling — not the e-waste fee",
        "facility": f"{city} specialty PV / installer take-back — confirm, not mixed e-waste",
        "steps": [
            "Do not set panels out as regular e-waste or bulky electronics.",
            "Cover the face and tape leads; panels generate voltage in light.",
            f"Confirm solar / PV on {src}, or ask the installer for take-back.",
        ],
    }
    if slug == "new-york":
        body["answer"] = (
            f"{city} covered-electronics rules (TVs, computers) are not a solar-panel program. Do not "
            "take a PV module to a Special Waste e-waste line expecting it to be accepted. Do not put "
            "panels in DSNY trash or recycling. Ask the installer about take-back, then confirm solar / "
            f"PV on {src} or a named transfer/C&D recycler. Cover the glass; taped leads."
        )
        body["facility"] = "Installer take-back / confirm PV — not DSNY e-waste"
    elif slug == "houston":
        body["answer"] = (
            f"{city} Environmental Service Centers accept computer equipment and electronic scrap. A "
            "rooftop or broken solar panel is not that list. Do not put PV in carts. Ask the installer "
            f"about take-back and confirm solar on {src} before you haul to an ESC. Cover the face; "
            "panels still generate voltage in light."
        )
        body["facility"] = "Houston installer / specialty PV — confirm, not ESC e-scrap"
    elif slug == "los-angeles":
        body["answer"] = (
            f"{city} S.A.F.E. Centers and LASAN bulky e-waste are built for TVs and computers, not PV "
            "modules. Do not assume a solar panel rides on the electronics bulky day. Ask the installer "
            f"for take-back and confirm solar / PV on {src}. Keep panels out of trash and recycling. "
            "Cover the glass in daylight."
        )
        body["facility"] = "LA installer / specialty PV — confirm, not S.A.F.E. e-waste"
    elif slug == "san-diego":
        body["answer"] = (
            f"{city} Miramar HHW/e-waste drop-off is appointment electronics and hazardous waste — not "
            "an automatic solar-panel recycler. Confirm PV on the official list before you book. "
            f"Otherwise use installer take-back or a named C&D/PV recycler. {src}. Do not cart panels."
        )
        body["facility"] = "San Diego installer / confirm PV at Miramar — not default e-waste"
    elif slug == "chicago":
        body["answer"] = (
            f"{city} HCCRF e-cycle is computers, TVs, and related gear under the Illinois electronics "
            "ban. A solar panel is a different product. Ask the installer about take-back and confirm "
            f"PV on {src} before you treat it as HCCRF e-waste. Do not put panels in carts."
        )
        body["facility"] = "Chicago installer / specialty PV — confirm, not HCCRF e-cycle"
    return {
        "answer": body["answer"],
        "steps": body["steps"],
        "faqs": faq(
            [
                ("Same as mixed e-waste?", "No. Household e-waste sites are built for TVs and computers. Confirm solar / PV, or use installer take-back."),
                ("Trash?", "No. Panels are glass/laminate modules and can still be electrically live in light."),
                ("Who takes them?", "Often the installer or a specialty PV recycler. Confirm on the official city/county page before you drive."),
            ]
        ),
        "common_disposal_fee": clip(body["fee"], 80),
        "nearest_facility_type": clip(body["facility"], 120),
        "badge": "SPECIAL_HANDLING",
        "hazard_rating": "Medium",
        "is_curbside_allowed": False,
    }


BUILDERS = {
    "helium-tank": helium,
    "styrofoam": styrofoam,
    "solar-panel": solar,
}


def main() -> None:
    cities = {c["city_slug"]: c for c in json.loads((DATA / "geo" / "cities.json").read_text())}
    path = DATA / "rules" / "all.json"
    rules = json.loads(path.read_text())
    n = 0
    for r in rules:
        item = r.get("item_slug")
        slug = r.get("city_slug")
        if item not in BUILDERS or not slug:
            continue
        built = BUILDERS[item](city_name(cities, slug), slug, r.get("source_name") or "the official program")
        r.update(built)
        r["reviewed_by"] = REVIEWED
        r["needs_review"] = False
        n += 1
    path.write_text(json.dumps(rules, indent=2) + "\n")
    print(f"Rewrote {n} city rules for {', '.join(ITEMS)}")


if __name__ == "__main__":
    main()
