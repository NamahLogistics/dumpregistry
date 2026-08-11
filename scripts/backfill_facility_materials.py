#!/usr/bin/env python3
"""Tag facilities with accepted_materials heuristics for the /centers finder.

Conservative: only tags materials we are confident a facility type generally accepts.
Manual audits can override accepted_materials per facility later.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAC_PATH = ROOT / "data" / "facilities" / "all.json"

HHW = [
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

E_WASTE = [
    "television",
    "computer-monitor",
    "laptop",
    "desktop-computer",
    "printer",
    "tablet",
    "smartphone",
    "microwave",
    "hard-drive",
    "e-waste-mixed",
    "ink-toner",
]

BULKY = [
    "mattress",
    "box-spring",
    "sofa",
    "recliner",
    "carpet",
    "yard-waste",
]


def materials_for(facility_type: str) -> list[str]:
    t = (facility_type or "").lower()
    out: list[str] = []
    if "hhw" in t or "hazard" in t or "pollutant" in t or "tox" in t:
        out.extend(HHW)
    if "e-waste" in t or "e-scrap" in t or "electronics" in t or "cyber" in t:
        out.extend(E_WASTE)
    if "bulky" in t or "convenience" in t or "large-item" in t or "transfer" in t:
        out.extend(BULKY)
    if "recycl" in t and "hhw" not in t:
        out.extend(E_WASTE[:6])
    # de-dupe preserve order
    seen: set[str] = set()
    ordered = []
    for m in out:
        if m not in seen:
            seen.add(m)
            ordered.append(m)
    return ordered


def main() -> None:
    facilities = json.loads(FAC_PATH.read_text())
    tagged = 0
    for f in facilities:
        mats = materials_for(str(f.get("facility_type") or ""))
        if mats:
            f["accepted_materials"] = mats
            tagged += 1
        elif "accepted_materials" not in f:
            f["accepted_materials"] = []
    FAC_PATH.write_text(json.dumps(facilities, indent=2) + "\n")
    print(f"Tagged {tagged}/{len(facilities)} facilities with accepted_materials")


if __name__ == "__main__":
    main()
