import type { Metadata } from "next";
import Link from "next/link";
import { getCities, getIndexablePages } from "@/lib/data";

export const metadata: Metadata = {
  title: "California disposal guides",
  description: "Browse verified California city guides for hard-to-dispose items.",
};

export default function CaliforniaHubPage() {
  const pages = getIndexablePages().filter((p) => p.state_slug === "california");
  const covered = new Set(pages.map((p) => p.city_slug));
  const cities = [...getCities()]
    .filter((c) => c.state_slug === "california")
    .sort((a, b) => b.population - a.population);
  const ready = cities.filter((c) => covered.has(c.city_slug));
  const pending = cities.filter((c) => !covered.has(c.city_slug));

  return (
    <div className="shell page">
      <header className="prose">
        <h1>California</h1>
        <p>
          {pages.length} verified city-program guides across {ready.length} cities. We do not publish
          statewide text as local advice.
        </p>
      </header>

      <section>
        <h2>Verified cities</h2>
        <div className="hub-grid">
          {ready.map((c) => (
            <Link key={c.city_slug} className="hub-link" href={`/${c.state_slug}/${c.city_slug}`}>
              <strong>{c.city}</strong>
              <div>
                {pages.filter((p) => p.city_slug === c.city_slug).length} guides
              </div>
            </Link>
          ))}
        </div>
      </section>

      {pending.length ? (
        <section>
          <h2>Research pending</h2>
          <p>These hubs exist so you can request a source — they have no invented local guides.</p>
          <div className="hub-grid">
            {pending.map((c) => (
              <Link key={c.city_slug} className="hub-link" href={`/${c.state_slug}/${c.city_slug}`}>
                <strong>{c.city}</strong>
                <div>Not researched yet</div>
              </Link>
            ))}
          </div>
        </section>
      ) : null}
    </div>
  );
}
