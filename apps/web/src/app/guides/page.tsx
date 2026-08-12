import type { Metadata } from "next";
import Link from "next/link";
import { listGuides } from "@/lib/markdown";

import { canonicalMetadata } from "@/lib/seo";

export const metadata: Metadata = {
  ...canonicalMetadata("/guides"),
  title: "Guides",
  description: "Researched DumpRegistry guides on city disposal programs, HHW, and hard-to-trash items.",
};

export default function GuidesIndexPage() {
  const guides = listGuides();

  return (
    <div className="shell page">
      <header className="prose">
        <h1>Guides</h1>
        <p>
          Editorial explainers that link into city-sourced dispose pages and drop-off centers.
          Not filler SEO — each piece is researched against official programs.
        </p>
      </header>

      <ul className="city-guide-list">
        {guides.map((g) => (
          <li key={g.slug}>
            <Link href={`/guides/${g.slug}`}>{g.title}</Link>
            {g.date ? <span className="muted"> · {g.date}</span> : null}
            {g.description ? <div className="muted">{g.description}</div> : null}
          </li>
        ))}
      </ul>
    </div>
  );
}
