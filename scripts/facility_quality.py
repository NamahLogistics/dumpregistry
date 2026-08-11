"""Facility quality bar: hard-to-dispose only (no soft recycling dilution)."""

HARD_MATERIALS = {
    "mattress","box-spring","sofa","recliner","carpet","yard-waste","desk","dining-table",
    "bookshelf","exercise-equipment","hot-tub","piano","christmas-tree",
    "refrigerator","freezer","air-conditioner","washer","dryer","dishwasher","stove",
    "water-heater","dehumidifier","microwave",
    "television","computer-monitor","laptop","desktop-computer","printer","tablet",
    "smartphone","hard-drive","e-waste-mixed","ink-toner","solar-panel",
    "paint-latex","paint-oil","pesticides","herbicides","pool-chemicals","gasoline",
    "motor-oil","antifreeze","car-battery","household-batteries","lithium-battery",
    "fluorescent-bulbs","propane-tank","cooking-oil","fire-extinguisher","medical-sharps",
    "thermometer-mercury","smoke-detector","helium-tank","needles","prescription-drugs",
    "incandescent-bulbs","led-bulbs",
    "tires","tire-rims","construction-debris","lumber","drywall","concrete",
    "asphalt-shingles","car-parts",
}
SOFT_ONLY = {"cardboard","glass-bottles","plastic-bags","food-scraps","styrofoam"}


def is_hard_facility(row: dict) -> bool:
    mats = set(row.get("accepted_materials") or [])
    name = (row.get("name") or "").lower()
    ftype = (row.get("facility_type") or "").lower()
    if mats & HARD_MATERIALS:
        return True
    if mats and mats <= SOFT_ONLY:
        return False
    if any(x in name for x in ("food scrap", "food scraps", "project oscar", "scrap it!", "recycling dumpster")):
        return False
    if not mats and any(
        x in ftype or x in name
        for x in ("transfer", "landfill", "hhw", "hazard", "convenience", "bulky", "safe", "special waste", "drop-off station", "tox", "appliance")
    ):
        return True
    return False
