import type { Metadata } from "next";
import Link from "next/link";
import { listGuides } from "@/lib/markdown";

import { pageMetadata } from "@/lib/seo";

export const metadata: Metadata = pageMetadata({
  title: "Guides to bulky pickup, HHW, and e-waste",
  description:
    "Plain-language DumpRegistry guides on mattresses, paint, lithium batteries, and city disposal programs.",
  path: "/guides",
});

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
