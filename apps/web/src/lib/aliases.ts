import { readFileSync } from "node:fs";
import path from "node:path";
import { dataRoot } from "./paths";

type AliasFile = {
  true_aliases: Record<string, string>;
  false_aliases: Record<string, string>;
};

let cache: AliasFile | null = null;

function loadAliases(): AliasFile {
  if (cache) return cache;
  const raw = JSON.parse(
    readFileSync(path.join(dataRoot(), "seo/item_aliases.json"), "utf8"),
  ) as AliasFile;
  cache = {
    true_aliases: raw.true_aliases ?? {},
    false_aliases: raw.false_aliases ?? {},
  };
  return cache;
}

export function isTrueAlias(itemSlug: string): boolean {
  return itemSlug in loadAliases().true_aliases;
}

export function trueAliasCore(itemSlug: string): string | undefined {
  return loadAliases().true_aliases[itemSlug];
}
