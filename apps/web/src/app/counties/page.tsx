import type { Metadata } from "next";
import Link from "next/link";
import { countyHhwHref, getCountyHhwHubs } from "@/lib/data";
import { pageMetadata } from "@/lib/seo";

export const metadata: Metadata = pageMetadata({
  title: "County household hazardous waste programs",
  description:
    "Suburban and county HHW programs for the 50 largest U.S. metros — who qualifies, and how that differs from the city drop-off.",
  path: "/counties",
});

export default function CountiesIndexPage() {
  const hubs = getCountyHhwHubs();
  return (
    <div className="shell page">
      <header className="prose">
        <h1>County HHW programs</h1>
        <p>
          City dispose pages own the rule inside city limits. These hubs are the suburban program —
          county, regional, or consolidated city-county HHW — for the 50 largest metros.{" "}
          {hubs.length} programs, covering {hubs.reduce((n, h) => n + h.cities.length, 0)} researched
          cities.
        </p>
        <p>
          <Link href="/cities">City hubs</Link>
          {" · "}
          <Link href="/centers">ZIP finder</Link>
          {" · "}
          <Link href="/guides/hhw-vs-bulk-vs-ewaste">HHW vs bulk vs e-waste</Link>
        </p>
      </header>
      <ul className="city-guide-list">
        {hubs.map((h) => (
          <li key={`${h.state_slug}-${h.county_slug}`}>
            <Link href={countyHhwHref(h)}>
              {h.county}, {h.state}
            </Link>
            <span className="muted">
              {" "}
              · {h.cities.map((c) => c.city).join(", ")}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
