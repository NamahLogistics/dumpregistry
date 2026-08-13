/** National guide slug → city dispose item to deep-link. */
export const GUIDE_DISPOSE_ITEM: Record<string, string> = {
  "how-to-dispose-of-ewaste": "e-waste-mixed",
  "how-to-dispose-of-a-hard-drive": "hard-drive",
  "how-to-dispose-of-lithium-batteries": "lithium-battery",
  "specialty-battery-disposal": "lithium-battery",
  "how-to-dispose-of-a-car-battery": "car-battery",
  "how-to-recycle-cooking-oil": "cooking-oil",
  "how-to-dispose-of-yard-waste": "yard-waste",
  "how-to-dispose-of-medical-sharps": "medical-sharps",
  "medical-waste-disposal": "medical-sharps",
  "how-to-dispose-of-propane-tanks": "propane-tank",
  "how-to-dispose-of-tires": "tires",
  "how-to-dispose-of-a-mattress": "mattress",
  "how-to-dispose-of-construction-debris": "construction-debris",
  "how-to-dispose-of-a-refrigerator": "refrigerator",
  "freon-appliance-disposal": "refrigerator",
  "how-to-dispose-of-an-air-conditioner": "air-conditioner",
  "how-to-dispose-of-a-dishwasher": "dishwasher",
  "how-to-dispose-of-a-sofa": "sofa",
  "how-to-dispose-of-paint": "paint-latex",
  "how-to-dispose-of-fluorescent-bulbs": "fluorescent-bulbs",
  "how-city-bulk-pickup-works": "mattress",
  "how-to-dispose-of-motor-oil": "motor-oil",
  "how-to-dispose-of-helium-tanks": "helium-tank",
  "how-to-dispose-of-styrofoam": "styrofoam",
  "how-to-dispose-of-solar-panels": "solar-panel",
};

/** Channel explainers — link city hubs, not one item. */
export const GUIDE_CITY_HUBS = new Set([
  "hhw-vs-bulk-vs-ewaste",
  "bulk-trash-drop-off-near-me",
]);
