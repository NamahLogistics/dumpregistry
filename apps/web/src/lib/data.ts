import { readFileSync } from "node:fs";
import path from "node:path";
import { dataRoot } from "./paths";
import type { City, DisposalPage, Item, ZipHub } from "./types";

function readJson<T>(rel: string): T {
  const full = path.join(dataRoot(), rel);
  return JSON.parse(readFileSync(full, "utf8")) as T;
}

let cache: {
  items?: Item[];
  cities?: City[];
  pages?: DisposalPage[];
  zipHubs?: ZipHub[];
} = {};

export function getItems(): Item[] {
  cache.items ??= readJson<Item[]>("items.json");
  return cache.items;
}

export function getCities(): City[] {
  cache.cities ??= readJson<City[]>("geo/ca_cities.json");
  return cache.cities;
}

export function getPages(): DisposalPage[] {
  cache.pages ??= readJson<DisposalPage[]>("resolved/pages.json");
  return cache.pages;
}

export function getZipHubs(): ZipHub[] {
  cache.zipHubs ??= readJson<ZipHub[]>("resolved/zip_hubs.json");
  return cache.zipHubs;
}

export function getItem(slug: string) {
  return getItems().find((i) => i.slug === slug);
}

export function getCity(stateSlug: string, citySlug: string) {
  return getCities().find((c) => c.state_slug === stateSlug && c.city_slug === citySlug);
}

export function getPage(stateSlug: string, citySlug: string, itemSlug: string) {
  return getPages().find(
    (p) =>
      p.state_slug === stateSlug &&
      p.city_slug === citySlug &&
      p.item_slug === itemSlug,
  );
}

export function getIndexablePages() {
  return getPages().filter((p) => p.indexable);
}

export function getCityPages(stateSlug: string, citySlug: string) {
  return getPages().filter((p) => p.state_slug === stateSlug && p.city_slug === citySlug);
}

export function getZipHub(stateSlug: string, citySlug: string, zip: string) {
  return getZipHubs().find(
    (z) => z.state_slug === stateSlug && z.city_slug === citySlug && z.zip === zip,
  );
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
