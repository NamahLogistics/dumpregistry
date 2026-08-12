import type { Metadata } from "next";
import Link from "next/link";
import { ContinueReading } from "@/components/ContinueReading";
import {
  getCities,
  getCityHighIntentGuides,
  getIndexablePages,
  getStates,
} from "@/lib/data";

import { canonicalMetadata } from "@/lib/seo";

export const metadata: Metadata = {
  ...canonicalMetadata("/cities"),
  title: "Cities with verified guides",
  description: "Browse DumpRegistry cities that have city-sourced disposal guides — no statewide filler.",
};

export default function CitiesHubPage() {
  const pages = getIndexablePages();
  const covered = new Set(pages.map((p) => `${p.state_slug}/${p.city_slug}`));
  const states = getStates().filter((s) =>
    getCities().some((c) => c.state_slug === s.state_slug && covered.has(`${c.state_slug}/${c.city_slug}`)),
  );

  const featured = getCities()
    .filter((c) => covered.has(`${c.state_slug}/${c.city_slug}`))
    .sort((a, b) => (b.population ?? 0) - (a.population ?? 0))
    .slice(0, 6)
    .flatMap((c) => {
      const guides = getCityHighIntentGuides(c.state_slug, c.city_slug, 2);
      return guides.map((p) => ({
        href: `/${p.state_slug}/${p.city_slug}/dispose/${p.item_slug}`,
        title: `${p.item_name} · ${c.city}`,
        meta: p.category,
      }));
    })
    .slice(0, 12);

  return (
    <div className="shell page">
      <header className="prose">
        <h1>Verified cities</h1>
        <p>
          {pages.length} indexable city-program guides across {covered.size} cities. Open a city, then click
          through related items to keep reading.
        </p>
      </header>

      <ContinueReading
        id="cities-featured"
        heading="Popular guides right now"
        lead="High-intent items in large metros — one click into a full answer page."
        links={featured}
      />

      {states.map((s) => {
        const cities = getCities()
          .filter((c) => c.state_slug === s.state_slug && covered.has(`${c.state_slug}/${c.city_slug}`))
          .sort((a, b) => (b.population ?? 0) - (a.population ?? 0));
        return (
          <section key={s.state_slug} className="cities-state-block">
            <h2>
              <Link href={`/${s.state_slug}`}>{s.state_slug.replaceAll("-", " ")}</Link>
            </h2>
            <div className="hub-grid">
              {cities.map((c) => {
                const count = pages.filter(
                  (p) => p.state_slug === c.state_slug && p.city_slug === c.city_slug,
                ).length;
                const teasers = getCityHighIntentGuides(c.state_slug, c.city_slug, 3);
                return (
                  <div key={c.city_slug} className="city-card">
                    <Link className="hub-link city-card-main" href={`/${c.state_slug}/${c.city_slug}`}>
                      <strong>{c.city}</strong>
                      <span className="hub-link-meta">{count} guides</span>
                    </Link>
                    <div className="city-card-teasers">
                      {teasers.map((p) => (
                        <Link
                          key={p.item_slug}
                          href={`/${p.state_slug}/${p.city_slug}/dispose/${p.item_slug}`}
                        >
                          {p.item_name}
                        </Link>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        );
      })}
    </div>
  );
}
