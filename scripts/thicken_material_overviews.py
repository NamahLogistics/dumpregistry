#!/usr/bin/env python3
"""Rewrite data/materials/overviews.json with thickened SEO content for all item slugs."""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ITEMS_PATH = ROOT / "data" / "items.json"
OUT_PATH = ROOT / "data" / "materials" / "overviews.json"
HOOKS_PATH = ROOT / "scripts" / "_overview_batches" / "hooks.json"
STEPS_PATH = ROOT / "scripts" / "_overview_batches" / "steps.json"

CATEGORY_BLURB = {
    "Bulky": "bulky or large-item waste rather than ordinary cart trash or blue-bin recycling",
    "Hazardous": "household hazardous waste (HHW) or another banned-from-landfill specialty stream",
    "Electronics": "e-waste / electronics recycling rather than trash or curbside mixed recycling",
    "Appliances": "appliance or bulky-appliance collection, with extra refrigerant rules when Freon is present",
    "Automotive": "automotive specialty disposal rather than household trash carts",
    "Medical": "medical sharps or pharmaceutical take-back pathways, not ordinary garbage or recycling",
    "C&D": "construction and demolition (C&D) or transfer-station debris pricing, not residential carts",
    "Organics": "organics, yard-waste, or food-scrap programs where your city offers them",
    "Recycling": "recycling or specialty recycling rules that vary sharply by city and material form",
    "Household": "ordinary household disposal with important local exceptions you must verify",
}


def compose_overview(slug: str, h: dict, m: dict) -> str:
    name = m["name"]
    cat = m["category"]
    fee = m["fee_band_default"]
    facility = m["facility_type_default"]
    summary = m["summary_default"]
    curbside = m["curbside_default"]
    badge = m["badge_default"]
    hazard = m["hazard_default"]
    angle = h.get("angle", "")
    blurb = CATEGORY_BLURB.get(cat, "special disposal")

    if cat == "Bulky":
        parts = [
            f"When Americans discard {name} ({h['aka']}), the governing category is usually {blurb}. {h['why']} That is why a trash-day curb set-out so often fails: the truck that empties carts is not the crew that is ticketed for oversized furniture and bedding.",
            f"Real-world channels for {name} include {h['channels']}. Facility directories may label the destination like “{facility}.” {summary} {angle}",
            f"Reuse screening matters here: {h['donate']}. If the piece fails that bar, stop shopping for a charity and book disposal instead—rejected donations still become someone else’s landfill problem.",
            f"Safety and code issues to respect: {h['safety']}. Prep that prevents refused pickups looks like this: {h['prep']}.",
            f"Money talk stays local, but national fee bands often land around {fee} ({h['fees_note']}). Ask haulers where the material goes after collection. Failure patterns that keep repeating nationwide: {h['fail']}.",
            f"Because bulky rules are municipal, open your city large-item guide for appointments, zone days, and caps before you stage {name}. Neighboring cities disagree; local staff and posted gate rules win.",
        ]
    elif cat == "Hazardous":
        parts = [
            f"{name} ({h['aka']}) belongs in the hazardous playbook: {blurb}. {h['why']}",
            f"Take-it-here options typically include {h['channels']}. Expect facility language close to “{facility}.” {summary} National badge/hazard defaults may read {badge}/{hazard}, yet the county HHW flyer still controls acceptance.",
            f"{angle} Legal and safety pressure points include {h['safety']}.",
            f"Handling before the trip: {h['prep']}. Fee expectations are often around {fee} ({h['fees_note']}). Donation is usually the wrong instinct: {h['donate']}.",
            f"Do not improvise drains, soil dumping, or trash-cart shortcuts. The mistakes that cause the most harm look like {h['fail']}. Use city/county HHW schedules and retailer take-back locators as primary sources.",
            f"If a private cleanout company offers to “just take it,” confirm they use licensed hazardous pathways for {name}. Cheap disappearance is not the same as legal disposal.",
        ]
    elif cat == "Electronics":
        parts = [
            f"{name} ({h['aka']}) is an electronics end-of-life problem: {blurb}. {h['why']}",
            f"Preferred pathways include {h['channels']}. Locators often describe sites as “{facility}.” {summary} {angle}",
            f"Before you recycle, handle data and batteries deliberately. Safety/legal issues include {h['safety']}. Prep checklist: {h['prep']}.",
            f"Reuse vs recycle: {h['donate']}. Fee bands commonly appear near {fee} ({h['fees_note']}). Badge/hazard defaults ({badge}/{hazard}) are hints, not city law.",
            f"Avoid the classic electronics mistakes: {h['fail']}. Blue bins and dumpsters are the wrong tools for {name} in most U.S. jurisdictions.",
            f"Confirm whether your city runs e-waste events, permanent drop-off, or retailer partnerships. Call about CRTs, batteries, and item limits so the trip counts.",
        ]
    elif cat == "Appliances":
        freonish = slug in {"refrigerator", "freezer", "air-conditioner", "dehumidifier"}
        freon_line = (
            f"Treat {name} as a Freon/refrigerant appliance until a local guide says otherwise—venting is not a disposal method."
            if freonish else
            f"{name} is usually a non-Freon bulky appliance problem focused on haul logistics rather than refrigerant recovery—still not a trash-cart item."
        )
        parts = [
            f"Appliance disposal for {name} ({h['aka']}) falls under {blurb}. {h['why']} {freon_line}",
            f"Channels that actually work: {h['channels']}. Directories may say “{facility}.” {summary} {angle}",
            f"Safety constraints: {h['safety']}. Prep that saves rework: {h['prep']}.",
            f"Reuse screen: {h['donate']}. Budget using {fee} as a planning range ({h['fees_note']}). Retailer haul-away at replacement time is often the cleanest bundle.",
            f"Watch for these failure modes: {h['fail']}. Schedule the correct appliance or Freon ticket—furniture-only bulky days regularly leave {name} behind.",
            f"Utility recycle programs, municipal appliance routes, and licensed haulers all exist in different metros; your city guide names which one applies to {name}.",
        ]
    elif cat == "Automotive":
        parts = [
            f"Automotive discards like {name} ({h['aka']}) are {blurb}. {h['why']}",
            f"Go-to channels: {h['channels']}. Facility labels often resemble “{facility}.” {summary} {angle}",
            f"Hazards and legal tripwires: {h['safety']}. Prep: {h['prep']}. Fees often look like {fee} ({h['fees_note']}).",
            f"Reuse angle: {h['donate']}. The expensive mistakes are {h['fail']}.",
            f"Tire shops, scrap yards, and auto recyclers each accept different slices of the automotive stream—calling first prevents a rejected trunk load of {name}.",
            f"City transfer rules and retailer take-back still beat alley storage. Local pages list caps, rim rules, and residency requirements.",
        ]
    elif cat == "Medical":
        parts = [
            f"For {name} ({h['aka']}), think medical compliance pathways: {blurb}. {h['why']}",
            f"Approved channels include {h['channels']}. Sites may be listed as “{facility}.” {summary} {angle}",
            f"Injury and diversion risks include {h['safety']}. Prep discipline: {h['prep']}.",
            f"Donation rules are strict: {h['donate']}. Cost is usually near {fee} ({h['fees_note']}).",
            f"Never normalize these mistakes: {h['fail']}. Pharmacy kiosks, sharps containers, and DEA take-back events exist to keep {name} out of trash bags and wastewater when avoidable.",
            f"Check health-department and city solid-waste medical pages together—guidance is local even when the hazard is universal.",
        ]
    elif cat == "C&D":
        parts = [
            f"{name} ({h['aka']}) is a construction-debris problem: {blurb}. {h['why']}",
            f"Move it through {h['channels']}. Gates may advertise “{facility}.” {summary} {angle}",
            f"Jobsite safety issues: {h['safety']}. Load prep: {h['prep']}. Expect pricing around {fee} ({h['fees_note']}).",
            f"Salvage first when it makes sense: {h['donate']}. Otherwise pay the C&D rate instead of risking illegal dumping citations tied to {h['fail']}.",
            f"Sorted loads sometimes earn better rates than mixed trashy debris—ask the facility how clean {name} must be.",
            f"Residential carts are the wrong tool. Use city C&D and transfer guides for hours, tarp rules, and prohibited contaminants.",
        ]
    elif cat == "Organics":
        parts = [
            f"{name} ({h['aka']}) belongs in organics thinking: {blurb}. {h['why']}",
            f"Collection options include {h['channels']}. Programs may map to “{facility}.” {summary} {angle}",
            f"Contamination and handling issues: {h['safety']}. Prep that keeps loads accepted: {h['prep']}.",
            f"Edible vs scrap decisions: {h['donate']}. Service pricing often lands near {fee} ({h['fees_note']}).",
            f"Organics programs fail when residents do {h['fail']}. Read the accepted list for meat, dairy, liners, flocking, or brush length—whatever applies to {name}.",
            f"City green-cart and seasonal collection pages are the authority; compost markets differ enough that copying another metro’s rules backfires.",
        ]
    elif cat == "Recycling":
        parts = [
            f"Recycling {name} ({h['aka']}) depends on local MRF rules: {blurb}. {h['why']}",
            f"Correct outlets include {h['channels']}. You may see “{facility}” in directories. {summary} {angle}",
            f"Contamination and safety notes: {h['safety']}. Prep: {h['prep']}. Fees are typically around {fee} ({h['fees_note']}).",
            f"Reuse where useful: {h['donate']}. Wishcycling mistakes to drop: {h['fail']}.",
            f"Single-stream carts are not universal yes/no machines—film, foam, and sometimes glass need specialty paths even when cardboard sails through.",
            f"Follow your city’s recycling flyer and store drop-off maps for {name}; when in doubt, ask rather than contaminating a truck.",
        ]
    else:
        parts = [
            f"{name} ({h['aka']}) is handled as {blurb}. {h['why']} {angle}",
            f"Everyday channels include {h['channels']}. Facility directories may describe the destination like “{facility}.” {summary} Even “simple” household discards vary by city packaging rules and cart policies.",
            f"Safety and handling notes: {h['safety']}. Practical prep before set-out or drop-off: {h['prep']}.",
            f"Fee expectations are usually around {fee} ({h['fees_note']}). Donation or reuse bar: {h['donate']}.",
            f"Common mistakes look like {h['fail']}. Curbside default note: "
            f"{'some curbside acceptance exists in national defaults' if curbside else 'not ordinary curbside in national defaults'}"
            "—verify locally before you toss.",
            f"Use your city solid-waste guide for the final rule set on {name}, including whether glass-like items belong in trash, recycling, or a specialty bulb program.",
        ]

    text = " ".join(parts)
    # Guarantee >=360 words with unique, item-named padding.
    pad_bits = [
        (
            f"Bookmark your municipality’s solid-waste search for “{name}” plus the nearest accepted-materials "
            f"PDF or facility directory so the next cleanup does not rely on memory from a different city."
        ),
        (
            f"Contracts, MRFs, HHW vendors, and e-waste recyclers change over time; rules for {name} can shift "
            f"even when the object in your garage looks identical to last year’s discarded unit."
        ),
        (
            f"If you are comparing self-haul versus on-demand pickup for {name}, factor wait time, vehicle fit, "
            f"gate hours, payment type (card vs cash), and whether residency ID is required at the scale house."
        ),
        (
            f"When a hauler quote for {name} seems too cheap, ask which licensed facility will receive it—"
            f"illegal dumping liability can return to the generator when enforcement traces a load."
        ),
        (
            f"For multi-family buildings, confirm lease and dock rules before staging {name} in a hallway or "
            f"alley; building staff may require timed elevator reservations independent of city tickets."
        ),
        (
            f"Write a one-line plan for {name}: channel, prep steps, fee ceiling, and backup site if the first "
            f"gate refuses the load. That small checklist prevents abandoned piles and repeat trips."
        ),
        (
            f"National guidance on this page is orientation only. Your city-sourced disposal guide and the "
            f"receiving facility’s posted rules are the final authority for {name} in your ZIP code."
        ),
    ]
    i = 0
    while len(text.split()) < 360 and i < len(pad_bits):
        text += " " + pad_bits[i]
        i += 1
    words = text.split()
    if len(words) > 550:
        text = " ".join(words[:530])
    return " ".join(text.split())



def build_content() -> dict[str, dict]:
    hooks = json.loads(HOOKS_PATH.read_text(encoding="utf-8"))
    steps = json.loads(STEPS_PATH.read_text(encoding="utf-8"))
    items = json.loads(ITEMS_PATH.read_text(encoding="utf-8"))
    out: dict[str, dict] = {}
    for item in items:
        slug = item["slug"]
        if slug not in hooks:
            raise SystemExit(f"Missing hooks for {slug}")
        if slug not in steps:
            raise SystemExit(f"Missing steps for {slug}")
        overview = compose_overview(slug, hooks[slug], item)
        prep = steps[slug]["prep_steps"]
        mistakes = steps[slug]["common_mistakes"]
        if not (4 <= len(prep) <= 6):
            raise SystemExit(f"{slug}: prep_steps must be 4–6, got {len(prep)}")
        if not (4 <= len(mistakes) <= 6):
            raise SystemExit(f"{slug}: common_mistakes must be 4–6, got {len(mistakes)}")
        out[slug] = {
            "overview": overview,
            "prep_steps": prep,
            "common_mistakes": mistakes,
        }
    return out


def validate(content: dict[str, dict], items: list[dict]) -> None:
    item_slugs = [i["slug"] for i in items]
    keys = list(content.keys())
    if len(keys) != 70:
        raise SystemExit(f"Expected 70 keys, got {len(keys)}")
    if set(keys) != set(item_slugs):
        missing = sorted(set(item_slugs) - set(keys))
        extra = sorted(set(keys) - set(item_slugs))
        raise SystemExit(f"Slug mismatch. missing={missing} extra={extra}")

    counts = []
    for slug in item_slugs:
        entry = content[slug]
        for field in ("overview", "prep_steps", "common_mistakes"):
            if field not in entry:
                raise SystemExit(f"{slug}: missing {field}")
        wc = len(entry["overview"].split())
        counts.append(wc)
        if wc < 320:
            raise SystemExit(f"{slug}: overview has {wc} words (<320)")
        if not (4 <= len(entry["prep_steps"]) <= 6):
            raise SystemExit(f"{slug}: prep_steps length {len(entry['prep_steps'])}")
        if not (4 <= len(entry["common_mistakes"]) <= 6):
            raise SystemExit(f"{slug}: common_mistakes length {len(entry['common_mistakes'])}")

    counts_sorted = sorted(counts)
    print(f"keys: {len(keys)}/70 match items.json")
    print(
        "overview word counts — "
        f"min={counts_sorted[0]} median={statistics.median(counts_sorted):.0f} "
        f"max={counts_sorted[-1]} avg={statistics.mean(counts_sorted):.1f}"
    )
    under = [s for s, c in zip(item_slugs, counts) if c < 350]
    over = [s for s, c in zip(item_slugs, counts) if c > 550]
    if under:
        print(f"note: {len(under)} below 350 target (but >=320): {under[:8]}{'...' if len(under)>8 else ''}")
    if over:
        print(f"note: {len(over)} above 550 soft target: {over}")


def main() -> int:
    items = json.loads(ITEMS_PATH.read_text(encoding="utf-8"))
    content = build_content()
    # Preserve items.json key order
    ordered = {i["slug"]: content[i["slug"]] for i in items}
    validate(ordered, items)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(ordered, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
