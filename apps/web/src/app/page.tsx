import { DisposalWizard } from "@/components/DisposalWizard";
import { getCities, getItems } from "@/lib/data";
import { site } from "@/lib/site";
import Link from "next/link";

export default function HomePage() {
  const items = getItems().map((i) => ({
    slug: i.slug,
    name: i.name,
    category: i.category,
  }));
  const cities = getCities().map((c) => ({
    city_slug: c.city_slug,
    city: c.city,
    state_slug: c.state_slug,
    state: c.state,
  }));

  return (
    <div className="shell hero">
      <p className="hero-brand">DumpRegistry</p>
      <h1>Can you dump it here?</h1>
      <p>
        {site.tagline} Pick an item and a city for a plain-language answer, verified sources when we have
        them, and the next step that actually works.
      </p>
      <DisposalWizard items={items} cities={cities} />
      <p>
        Browse <Link href="/california">California city guides</Link> ·{" "}
        <Link href="/methodology">How we verify data</Link>
      </p>
    </div>
  );
}
