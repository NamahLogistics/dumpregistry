import type { Metadata } from "next";
import { readFileSync, existsSync } from "node:fs";
import path from "node:path";
import { SourceLink } from "@/components/SourceLink";
import { dataRoot } from "@/lib/paths";

import { pageMetadata } from "@/lib/seo";

export const metadata: Metadata = pageMetadata({
  title: "Citation list for DumpRegistry editors",
  description:
    "Named city and county program URLs cited on DumpRegistry pages. Not a disposal how-to — confirm rules on the originating site.",
  path: "/sources",
  index: false,
});

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
      <h1>Citation list</h1>
      <p>
        These are the city and county URLs cited on DumpRegistry pages — a bibliography, not a how-to. Always
        confirm hours, fees, and appointment rules on the originating site before you haul an item.
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
