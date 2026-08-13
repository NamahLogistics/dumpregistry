import Link from "next/link";
import { ContinueReading } from "@/components/ContinueReading";
import { DisposalWizard } from "@/components/DisposalWizard";
import {
  getCityPages,
  getIndexablePages,
  getWizardOptions,
  HIGH_INTENT_ITEMS,
} from "@/lib/data";
import { pageMetadata } from "@/lib/seo";
import { site } from "@/lib/site";

export const metadata = pageMetadata({
  title: "DumpRegistry — dispose of bulky items, HHW & e-waste by city",
  description:
    "Verified drop-off and bulky pickup rules for mattresses, paint, TVs, and more — city-sourced, with official links.",
  path: "/",
});

export default function HomePage() {
  const { cities, items, itemsByCity } = getWizardOptions();
  const pages = getIndexablePages();
  const cityCount = new Set(pages.map((p) => `${p.state_slug}/${p.city_slug}`)).size;

  const topCities = [...cities]
    .map((c) => ({
      ...c,
      count: getCityPages(c.state_slug, c.city_slug).length,
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 8);

  const starterLinks = HIGH_INTENT_ITEMS.flatMap((slug) => {
    const hits = pages.filter((p) => p.item_slug === slug).slice(0, 1);
    return hits.map((p) => ({
      href: `/${p.state_slug}/${p.city_slug}/dispose/${p.item_slug}`,
      title: `${p.item_name}`,
      meta: `${p.city}, ${p.state}`,
    }));
  }).slice(0, 8);

  return (
    <>
      <div className="hero-plane">
        <div className="shell hero">
          <p className="hero-brand">DumpRegistry</p>
          <h1>Find the official way to dispose of it</h1>
          <p>
            {site.tagline} {pages.length.toLocaleString()} verified city guides across {cityCount} cities —
            each answer names the local program source and when we last checked it.
          </p>
          <DisposalWizard items={items} cities={cities} itemsByCity={itemsByCity} />
        </div>
      </div>

      <div className="shell page home-engage">
        <ContinueReading
          id="home-starters"
          heading="Common disposal questions"
          lead="Open a verified guide, then continue to related items in the same city."
          links={starterLinks}
        />

        <ContinueReading
          id="home-cities"
          heading="Cities with verified programs"
          lead="Each city hub lists every local guide we have published."
          links={topCities.map((c) => ({
            href: `/${c.state_slug}/${c.city_slug}`,
            title: c.city,
            meta: `${c.count} guides · ${c.state}`,
          }))}
        />

        <p className="home-foot-links">
          <Link href="/cities">All cities</Link>
          {" · "}
          <Link href="/methodology">How we verify</Link>
          {" · "}
          <Link href="/sources">Official sources</Link>
          {" · "}
          <Link href="/partners">For haulers</Link>
        </p>
      </div>
    </>
  );
}
