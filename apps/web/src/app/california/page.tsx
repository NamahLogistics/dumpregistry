import type { Metadata } from "next";
import Link from "next/link";
import { getCities, getIndexablePages } from "@/lib/data";

export const metadata: Metadata = {
  title: "California disposal guides",
  description: "Browse verified California city guides for hard-to-dispose items.",
};

export default function CaliforniaHubPage() {
  const cities = [...getCities()].sort((a, b) => b.population - a.population);
  const indexable = getIndexablePages().length;

  return (
    <div className="shell page">
      <header className="prose">
        <h1>California</h1>
        <p>
          We only publish indexable guides when we have a <strong>city-specific</strong> program source — not
          statewide copy pasted as local advice. {indexable} verified city guides are live (starting with Los
          Angeles, San Francisco, and San Diego). Other cities remain wizard-only until researched.
        </p>
      </header>
      <div className="hub-grid">
        {cities.map((c) => (
          <Link key={c.city_slug} className="hub-link" href={`/${c.state_slug}/${c.city_slug}`}>
            <strong>{c.city}</strong>
            <div>Population {c.population.toLocaleString()}</div>
          </Link>
        ))}
      </div>
    </div>
  );
}
