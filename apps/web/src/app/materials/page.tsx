import type { Metadata } from "next";
import Link from "next/link";
import { getItems, getMaterialGuideCount } from "@/lib/data";

export const metadata: Metadata = {
  title: "Materials encyclopedia",
  description:
    "Browse disposal materials — national overview plus city-sourced program guides where we have verified local rules.",
};

export default function MaterialsIndexPage() {
  const items = getItems();
  const byCat = new Map<string, typeof items>();
  for (const item of items) {
    const list = byCat.get(item.category) ?? [];
    list.push(item);
    byCat.set(item.category, list);
  }

  return (
    <div className="shell page">
      <header className="prose">
        <h1>Materials encyclopedia</h1>
        <p>
          National starting points for hard-to-trash materials. Every material page links into
          city-sourced dispose guides — the local program is always the source of truth.
        </p>
      </header>

      {[...byCat.entries()].map(([category, list]) => (
        <section key={category} className="cities-state-block">
          <h2>
            <Link href={`/materials#${category.toLowerCase()}`}>{category}</Link>
            <span className="muted"> · {list.length}</span>
          </h2>
          <ul className="city-guide-list">
            {list.map((item) => {
              const n = getMaterialGuideCount(item.slug);
              return (
                <li key={item.slug}>
                  <Link href={`/materials/${item.slug}`}>{item.name}</Link>
                  <span className="muted"> · {n} city guides</span>
                </li>
              );
            })}
          </ul>
        </section>
      ))}
    </div>
  );
}
