import type { Metadata } from "next";
import { readFileSync, existsSync } from "node:fs";
import path from "node:path";
import { SourceLink } from "@/components/SourceLink";
import { dataRoot } from "@/lib/paths";

import { canonicalMetadata } from "@/lib/seo";

export const metadata: Metadata = {
  title: "Sources",
  description: "Primary sources used for city disposal guidance on DumpRegistry.",
  ...canonicalMetadata("/sources"),
};

type Rule = {
  source_name: string;
  source_url: string;
  city_slug?: string | null;
  item_slug: string;
};

function loadRules(): Rule[] {
  const root = dataRoot();
  const preferred = path.join(root, "rules/all.json");
  if (existsSync(preferred)) return JSON.parse(readFileSync(preferred, "utf8")) as Rule[];
  const rows: Rule[] = [];
  for (const name of ["ca.json", "national.json"]) {
    const p = path.join(root, "rules", name);
    if (existsSync(p)) rows.push(...(JSON.parse(readFileSync(p, "utf8")) as Rule[]));
  }
  return rows;
}

export default function SourcesPage() {
  const rules = loadRules();
  const unique = new Map<string, Rule>();
  for (const r of rules) {
    if (r.city_slug) unique.set(r.source_url, r);
  }

  return (
    <article className="shell page prose">
      <h1>Sources</h1>
      <p>
        Indexable answers cite the city/county sources below. Always confirm hours, fees, and appointment rules
        on the originating site before you haul an item.
      </p>
      <ul>
        {[...unique.values()].map((r) => (
          <li key={r.source_url}>
            <SourceLink url={r.source_url} title={r.source_name}>
              {r.source_name}
            </SourceLink>
          </li>
        ))}
      </ul>
    </article>
  );
}
