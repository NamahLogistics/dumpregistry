import type { Metadata } from "next";
import { readFileSync } from "node:fs";
import path from "node:path";
import { dataRoot } from "@/lib/paths";

export const metadata: Metadata = {
  title: "Sources",
  description: "Primary sources used for California disposal guidance on DumpRegistry.",
};

type Rule = {
  source_name: string;
  source_url: string;
  city_slug?: string | null;
  item_slug: string;
};

export default function SourcesPage() {
  const rules = JSON.parse(
    readFileSync(path.join(dataRoot(), "rules/ca.json"), "utf8"),
  ) as Rule[];
  const unique = new Map<string, Rule>();
  for (const r of rules) unique.set(r.source_url, r);

  return (
    <article className="shell page prose">
      <h1>Sources</h1>
      <p>
        Indexable answers cite the sources below. Always confirm hours, fees, and appointment rules on the
        originating site before you haul an item.
      </p>
      <ul>
        {[...unique.values()].map((r) => (
          <li key={r.source_url}>
            <a href={r.source_url} target="_blank" rel="noopener noreferrer">
              {r.source_name}
            </a>
          </li>
        ))}
      </ul>
    </article>
  );
}
