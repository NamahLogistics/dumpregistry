import Link from "next/link";
import { SourceLink } from "@/components/SourceLink";
import type { CityProgramGroup } from "@/lib/data";

export function CityProgramBoard({
  city,
  groups,
}: {
  city: string;
  groups: CityProgramGroup[];
}) {
  if (!groups.length) return null;
  return (
    <section className="program-board" aria-labelledby="city-programs">
      <div className="continue-head">
        <h2 id="city-programs">{city} disposal programs</h2>
        <p>
          Items that share the same official city or county source are grouped here. Each name is still
          its own sourced guide.
        </p>
      </div>
      <nav className="program-jump" aria-label={`${city} program sections`}>
        {groups.map((g) => (
          <a key={g.key} href={`#${g.key}`}>
            {g.label}
            <span> {g.pages.length}</span>
          </a>
        ))}
      </nav>
      {groups.map((g) => (
        <article key={g.key} id={g.key} className="program-card">
          <h3>
            {g.label} in {city}
          </h3>
          <p className="program-blurb">{g.blurb}</p>
          {g.sourceName && g.sourceUrl ? (
            <p className="program-source">
              Official source:{" "}
              <SourceLink url={g.sourceUrl} title={g.sourceName}>
                {g.sourceName}
              </SourceLink>
            </p>
          ) : null}
          <p className="program-lead">{g.lead.answer}</p>
          <p className="program-lead-link">
            <Link href={`/${g.lead.state_slug}/${g.lead.city_slug}/dispose/${g.lead.item_slug}`}>
              Open {g.lead.item_name} guide
            </Link>
          </p>
          <ul className="program-items">
            {g.pages.map((p) => (
              <li key={p.item_slug}>
                <Link href={`/${p.state_slug}/${p.city_slug}/dispose/${p.item_slug}`}>
                  {p.item_name}
                </Link>
              </li>
            ))}
          </ul>
        </article>
      ))}
    </section>
  );
}
