import { readFileSync } from "node:fs";
import path from "node:path";
import { isTrueAlias } from "./aliases";
import { dataRoot } from "./paths";
import type { SnippetOverride } from "./snippets";
import type { City, DisposalPage, Facility, Item, ZipHub } from "./types";

function readJson<T>(rel: string): T {
  const full = path.join(dataRoot(), rel);
  return JSON.parse(readFileSync(full, "utf8")) as T;
}

let cache: {
  items?: Item[];
  cities?: City[];
  pages?: DisposalPage[];
  zipHubs?: ZipHub[];
  facilities?: Facility[];
  ctrOverrides?: Record<string, SnippetOverride>;
} = {};

export function getItems(): Item[] {
  cache.items ??= readJson<Item[]>("items.json");
  return cache.items;
}

export function getCities(): City[] {
  if (!cache.cities) {
    try {
      cache.cities = readJson<City[]>("geo/cities.json");
    } catch {
      cache.cities = readJson<City[]>("geo/ca_cities.json");
    }
  }
  return cache.cities;
}

export function getStates() {
  const bySlug = new Map<string, { state_slug: string; state: string; population: number }>();
  for (const c of getCities()) {
    const cur = bySlug.get(c.state_slug);
    if (!cur) {
      bySlug.set(c.state_slug, {
        state_slug: c.state_slug,
        state: c.state,
        population: c.population ?? 0,
      });
    } else {
      cur.population += c.population ?? 0;
    }
  }
  return [...bySlug.values()].sort((a, b) => b.population - a.population);
}

type PagesIndex = {
  all: DisposalPage[];
  citySourced: DisposalPage[];
  indexable: DisposalPage[];
  byKey: Map<string, DisposalPage>;
  byCity: Map<string, DisposalPage[]>;
  byItem: Map<string, DisposalPage[]>;
};

let pagesIndex: PagesIndex | null = null;

export function cityKey(stateSlug: string, citySlug: string) {
  return `${stateSlug}/${citySlug}`;
}

function pageLookupKey(stateSlug: string, citySlug: string, itemSlug: string) {
  return `${stateSlug}/${citySlug}/${itemSlug}`;
}

function isCitySourced(page: DisposalPage) {
  return page.rule_source_level === "city";
}

function getPagesIndex(): PagesIndex {
  if (pagesIndex) return pagesIndex;
  const all = readJson<DisposalPage[]>("resolved/pages.json");
  const byKey = new Map<string, DisposalPage>();
  const byCity = new Map<string, DisposalPage[]>();
  const byItem = new Map<string, DisposalPage[]>();
  const citySourced: DisposalPage[] = [];
  const indexable: DisposalPage[] = [];
  for (const page of all) {
    byKey.set(pageLookupKey(page.state_slug, page.city_slug, page.item_slug), page);
    if (!isCitySourced(page)) continue;
    citySourced.push(page);
    if (page.indexable) indexable.push(page);
    const ck = cityKey(page.state_slug, page.city_slug);
    const cityList = byCity.get(ck);
    if (cityList) cityList.push(page);
    else byCity.set(ck, [page]);
    const itemList = byItem.get(page.item_slug);
    if (itemList) itemList.push(page);
    else byItem.set(page.item_slug, [page]);
  }
  pagesIndex = { all, citySourced, indexable, byKey, byCity, byItem };
  cache.pages = all;
  return pagesIndex;
}

export function getPages(): DisposalPage[] {
  return getPagesIndex().all;
}

export function getZipHubs(): ZipHub[] {
  cache.zipHubs ??= readJson<ZipHub[]>("resolved/zip_hubs.json");
  return cache.zipHubs;
}

export function getFacilities(): Facility[] {
  cache.facilities ??= readJson<Facility[]>("facilities/all.json");
  return cache.facilities;
}

/** City dispose guides that cover a material — for encyclopedia deep links. */
export function getMaterialCityGuides(itemSlug: string, limit = 24): DisposalPage[] {
  const pop = new Map(getCities().map((c) => [c.city_slug, c.population ?? 0]));
  return [...(getPagesIndex().byItem.get(itemSlug) ?? [])]
    .sort(
      (a, b) =>
        (pop.get(b.city_slug) ?? 0) - (pop.get(a.city_slug) ?? 0) || a.city.localeCompare(b.city),
    )
    .slice(0, limit);
}

export function getMaterialGuideCount(itemSlug: string): number {
  return getPagesIndex().byItem.get(itemSlug)?.length ?? 0;
}

export type MaterialOverview = {
  overview: string;
  prep_steps: string[];
  common_mistakes: string[];
};

export function getMaterialOverview(itemSlug: string): MaterialOverview | null {
  try {
    const all = readJson<Record<string, MaterialOverview>>("materials/overviews.json");
    return all[itemSlug] ?? null;
  } catch {
    return null;
  }
}

export function getItem(slug: string) {
  return getItems().find((i) => i.slug === slug);
}

/** GSC CTR rewrites keyed by pathname, e.g. `/texas/austin/dispose/mattress`. */
export function getCtrOverride(pathname: string): SnippetOverride | undefined {
  if (!cache.ctrOverrides) {
    try {
      cache.ctrOverrides = readJson<Record<string, SnippetOverride>>("seo/ctr_overrides.json");
    } catch {
      cache.ctrOverrides = {};
    }
  }
  return cache.ctrOverrides[pathname];
}

export function getCity(stateSlug: string, citySlug: string) {
  return getCities().find((c) => c.state_slug === stateSlug && c.city_slug === citySlug);
}

export function getPage(stateSlug: string, citySlug: string, itemSlug: string) {
  const page = getPagesIndex().byKey.get(pageLookupKey(stateSlug, citySlug, itemSlug));
  if (!page || !isCitySourced(page)) return undefined;
  return page;
}

export function getIndexablePages() {
  return getPagesIndex().indexable;
}

export function getCityPages(stateSlug: string, citySlug: string) {
  return getPagesIndex().byCity.get(cityKey(stateSlug, citySlug)) ?? [];
}

export function getZipHub(stateSlug: string, citySlug: string, zip: string) {
  return getZipHubs().find(
    (z) =>
      z.state_slug === stateSlug &&
      z.city_slug === citySlug &&
      z.zip === zip &&
      z.indexable,
  );
}

/** Cities/items that have at least one verified city guide — for the wizard. */
export function getWizardOptions() {
  const pages = getPagesIndex().citySourced;
  const covered = new Set(pages.map((p) => cityKey(p.state_slug, p.city_slug)));
  const itemSlugs = new Set(pages.map((p) => p.item_slug));
  const cities = getCities()
    .filter((c) => covered.has(cityKey(c.state_slug, c.city_slug)))
    .map((c) => ({
      city_slug: c.city_slug,
      city: c.city,
      state_slug: c.state_slug,
      state: c.state,
      key: cityKey(c.state_slug, c.city_slug),
    }))
    .sort((a, b) => a.city.localeCompare(b.city) || a.state.localeCompare(b.state));
  const items = getItems()
    .filter((i) => itemSlugs.has(i.slug))
    .map((i) => ({ slug: i.slug, name: i.name, category: i.category }));
  const itemsByCity: Record<string, string[]> = {};
  for (const p of pages) {
    const key = cityKey(p.state_slug, p.city_slug);
    itemsByCity[key] ??= [];
    itemsByCity[key].push(p.item_slug);
  }
  return { cities, items, itemsByCity };
}

export function badgeLabel(badge: string) {
  switch (badge) {
    case "BANNED_FROM_LANDFILLS":
      return "Banned from landfills";
    case "ACCEPTED_IN_BLUE_BIN":
      return "Accepted in diversion stream";
    case "SPECIAL_HANDLING":
      return "Special handling required";
    default:
      return badge.replaceAll("_", " ");
  }
}

/** High-intent items — good first clicks for hubs and continue-reading. */
export const HIGH_INTENT_ITEMS = [
  "mattress",
  "construction-debris",
  "concrete",
  "helium-tank",
  "lithium-battery",
  "propane-tank",
  "tires",
  "refrigerator",
  "car-parts",
  "paint-latex",
] as const;

export function getRelatedInCity(page: DisposalPage, limit = 6): DisposalPage[] {
  const others = getCityPages(page.state_slug, page.city_slug).filter(
    (p) => p.item_slug !== page.item_slug,
  );
  const sameCat = others.filter((p) => p.category === page.category);
  const high = others.filter((p) =>
    (HIGH_INTENT_ITEMS as readonly string[]).includes(p.item_slug),
  );
  const seen = new Set<string>();
  const out: DisposalPage[] = [];
  for (const p of [...sameCat, ...high, ...others]) {
    if (seen.has(p.item_slug)) continue;
    seen.add(p.item_slug);
    out.push(p);
    if (out.length >= limit) break;
  }
  return out;
}

export function getSameItemOtherCities(page: DisposalPage, limit = 6): DisposalPage[] {
  return (getPagesIndex().byItem.get(page.item_slug) ?? [])
    .filter((p) => !(p.state_slug === page.state_slug && p.city_slug === page.city_slug))
    .sort((a, b) => a.city.localeCompare(b.city))
    .slice(0, limit);
}

export function getSiblingCities(stateSlug: string, citySlug: string, limit = 8) {
  const idx = getPagesIndex();
  return getCities()
    .filter(
      (c) =>
        c.state_slug === stateSlug &&
        c.city_slug !== citySlug &&
        (idx.byCity.get(cityKey(c.state_slug, c.city_slug))?.length ?? 0) > 0,
    )
    .sort((a, b) => (b.population ?? 0) - (a.population ?? 0))
    .slice(0, limit);
}

/**
 * Build-time dispose paths only. Prerendering all ~21k city×item pages overflows
 * V8's call stack during Next static generation. Remaining URLs still resolve
 * on first request (`dynamicParams = true`) from the same JSON.
 */
const PRERENDER_FULL_CITY_COUNT = 80;

export function getDisposeStaticParams() {
  const highIntent = new Set<string>(HIGH_INTENT_ITEMS);
  const pages = getPagesIndex().citySourced;
  const pop = new Map(getCities().map((c) => [cityKey(c.state_slug, c.city_slug), c.population ?? 0]));
  const rankedCities = [
    ...new Set(pages.map((p) => cityKey(p.state_slug, p.city_slug))),
  ].sort((a, b) => (pop.get(b) ?? 0) - (pop.get(a) ?? 0));
  const fullCities = new Set(rankedCities.slice(0, PRERENDER_FULL_CITY_COUNT));
  return pages
    .filter(
      (p) =>
        !isTrueAlias(p.item_slug) &&
        (fullCities.has(cityKey(p.state_slug, p.city_slug)) || highIntent.has(p.item_slug)),
    )
    .map((p) => ({
      state: p.state_slug,
      city: p.city_slug,
      item: p.item_slug,
    }));
}

/** Largest metros that already have city-sourced guides — for national guide footers. */
export function getTopCoveredCities(limit = 12) {
  const covered = getPagesIndex().byCity;
  return getCities()
    .filter((c) => (covered.get(cityKey(c.state_slug, c.city_slug))?.length ?? 0) > 0)
    .sort((a, b) => (b.population ?? 0) - (a.population ?? 0))
    .slice(0, limit);
}

export function getCityHighIntentGuides(stateSlug: string, citySlug: string, limit = 10) {
  const bySlug = new Map(getCityPages(stateSlug, citySlug).map((p) => [p.item_slug, p]));
  const pinned = HIGH_INTENT_ITEMS.map((slug) => bySlug.get(slug)).filter(Boolean) as DisposalPage[];
  if (pinned.length >= limit) return pinned.slice(0, limit);
  const rest = getCityPages(stateSlug, citySlug).filter(
    (p) => !(HIGH_INTENT_ITEMS as readonly string[]).includes(p.item_slug),
  );
  return [...pinned, ...rest].slice(0, limit);
}

export const CITY_PROGRAMS = [
  {
    key: "bulky",
    label: "Bulky pickup",
    blurb: "Mattresses, furniture, and many appliances — city bulk or drop-off, not the regular cart.",
    pin: ["mattress", "refrigerator", "sofa"],
  },
  {
    key: "hhw",
    label: "HHW",
    blurb: "Household hazardous waste — used oil, paint, propane, batteries, and chemicals.",
    pin: ["motor-oil", "paint-latex", "propane-tank", "lithium-battery", "helium-tank"],
  },
  {
    key: "ewaste",
    label: "E-waste",
    blurb: "TVs, computers, and electronics. Usually banned from trash and the blue bin.",
    pin: ["e-waste-mixed", "television", "hard-drive"],
  },
  {
    key: "dump",
    label: "Dump / C&D",
    blurb: "Construction debris, concrete, and remodel waste — transfer station or roll-off.",
    pin: ["construction-debris", "concrete"],
  },
  {
    key: "organics",
    label: "Yard & organics",
    blurb: "Yard waste, food scraps, and cooking oil where the city has a separate stream.",
    pin: ["yard-waste", "cooking-oil"],
  },
  {
    key: "recycling",
    label: "Recycling & film",
    blurb: "Cart recycling, store film take-back, and foam rules — not a second bulky program.",
    pin: ["styrofoam", "plastic-bags", "cardboard"],
  },
] as const;

export type CityProgramKey = (typeof CITY_PROGRAMS)[number]["key"];

/** Promo / board chips fold true aliases onto the city program section. Human /dispose URLs stay. */
export function cityItemHref(page: {
  state_slug: string;
  city_slug: string;
  item_slug: string;
  category: string;
}): string {
  if (isTrueAlias(page.item_slug)) {
    return `/${page.state_slug}/${page.city_slug}#${cityProgramKey(page.category)}`;
  }
  return `/${page.state_slug}/${page.city_slug}/dispose/${page.item_slug}`;
}

export function cityProgramKey(category: string): CityProgramKey {
  switch (category) {
    case "Bulky":
    case "Appliances":
      return "bulky";
    case "Electronics":
      return "ewaste";
    case "C&D":
      return "dump";
    case "Organics":
      return "organics";
    case "Recycling":
      return "recycling";
    default:
      return "hhw";
  }
}

export type CityProgramGroup = {
  key: CityProgramKey;
  label: string;
  blurb: string;
  pages: DisposalPage[];
  lead: DisposalPage;
  sourceName: string | null;
  sourceUrl: string | null;
};

function pickProgramLead(pages: DisposalPage[], pin: readonly string[]): DisposalPage {
  const bySlug = new Map(pages.map((p) => [p.item_slug, p]));
  for (const slug of pin) {
    const hit = bySlug.get(slug);
    if (hit) return hit;
  }
  const original = pages.find((p) => !/follows the same verified program pathway/i.test(p.answer || ""));
  return original ?? pages[0];
}

export function getCityProgramGroups(stateSlug: string, citySlug: string): CityProgramGroup[] {
  const pages = getCityPages(stateSlug, citySlug);
  const buckets = new Map<CityProgramKey, DisposalPage[]>();
  for (const page of pages) {
    const key = cityProgramKey(page.category);
    const list = buckets.get(key);
    if (list) list.push(page);
    else buckets.set(key, [page]);
  }
  const out: CityProgramGroup[] = [];
  for (const spec of CITY_PROGRAMS) {
    const group = buckets.get(spec.key);
    if (!group?.length) continue;
    const lead = pickProgramLead(group, spec.pin);
    const srcCounts = new Map<string, number>();
    for (const p of group) {
      if (!p.source_url) continue;
      srcCounts.set(p.source_url, (srcCounts.get(p.source_url) ?? 0) + 1);
    }
    const topUrl = [...srcCounts.entries()].sort((a, b) => b[1] - a[1])[0]?.[0] ?? lead.source_url;
    const named = group.find((p) => p.source_url === topUrl);
    const pinSet = new Set<string>(spec.pin);
    const sorted = [...group].sort((a, b) => {
      const ap = pinSet.has(a.item_slug) ? 0 : 1;
      const bp = pinSet.has(b.item_slug) ? 0 : 1;
      return ap - bp || a.item_name.localeCompare(b.item_name);
    });
    out.push({
      key: spec.key,
      label: spec.label,
      blurb: spec.blurb,
      pages: sorted,
      lead,
      sourceName: named?.source_name ?? lead.source_name,
      sourceUrl: topUrl,
    });
  }
  return out;
}
