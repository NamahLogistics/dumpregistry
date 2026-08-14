import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { AdSlot } from "@/components/AdSlot";
import { CityItemFinder } from "@/components/CityItemFinder";
import { ContinueReading, pagesToContinueLinks } from "@/components/ContinueReading";
import { CorrectionWidget } from "@/components/CorrectionWidget";
import { DoThisNow } from "@/components/DoThisNow";
import { FaqSection, faqJsonLd, howToJsonLd } from "@/components/FaqSection";
import { FacilityMap } from "@/components/FacilityMap";
import { LeadModule } from "@/components/LeadModule";
import { QuickAnswerBar } from "@/components/QuickAnswerBar";
import { SourceLink } from "@/components/SourceLink";
import { SpecsTable } from "@/components/SpecsTable";
import { StatusBadge } from "@/components/StatusBadge";
import {
  badgeLabel,
  CITY_PROGRAMS,
  cityItemHref,
  cityProgramKey,
  countyHhwHref,
  getCityPages,
  getCountyHhwForCity,
  getCtrOverride,
  getDisposeStaticParams,
  getPage,
  getRelatedInCity,
  getSameItemOtherCities,
  getSiblingCities,
  getZipHubs,
} from "@/lib/data";
import { breadcrumbJsonLd, pageMetadata } from "@/lib/seo";
import { disposeDescription, disposeTitle } from "@/lib/snippets";

type Props = {
  params: Promise<{ state: string; city: string; item: string }>;
};

export const dynamicParams = true;

export async function generateStaticParams() {
  return getDisposeStaticParams();
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { state, city, item } = await params;
  const page = getPage(state, city, item);
  if (!page) return { robots: { index: false, follow: false } };
  const path = `/${page.state_slug}/${page.city_slug}/dispose/${page.item_slug}`;
  const override = getCtrOverride(path);
  return pageMetadata({
    title: disposeTitle(page, override?.title),
    description: disposeDescription(page, override?.description),
    path,
    index: page.indexable,
    follow: true,
  });
}

export default async function DisposeItemPage({ params }: Props) {
  const { state, city, item } = await params;
  const page = getPage(state, city, item);
  if (!page) notFound();

  const cityGuides = getCityPages(state, city).filter((p) => p.item_slug !== item);
  const related = getRelatedInCity(page, 6);
  const otherCities = getSameItemOtherCities(page, 6);
  const siblingCities = getSiblingCities(state, city, 6);
  const zips = getZipHubs().filter(
    (z) => z.state_slug === state && z.city_slug === city && z.indexable,
  );
  const primaryPhone = page.facilities?.find((f) => f.phone)?.phone ?? null;
  const zipRefs = zips.map((z) => ({ zip: z.zip, lat: z.lat, lng: z.lng }));
  const programKey = cityProgramKey(page.category);
  const programLabel = CITY_PROGRAMS.find((p) => p.key === programKey)?.label ?? "city program";
  const countyHhw = programKey === "hhw" ? getCountyHhwForCity(state, city) : undefined;

  return (
    <div className="shell page">
      {page.indexable ? (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd(page.faqs)) }}
        />
      ) : null}
      {page.indexable ? (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify(
              howToJsonLd(
                `How to dispose of ${page.item_name} in ${page.city}`,
                page.answer,
                page.steps,
              ),
            ),
          }}
        />
      ) : null}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(
            breadcrumbJsonLd([
              { name: "Cities", path: "/cities" },
              { name: page.state, path: `/${page.state_slug}` },
              { name: page.city, path: `/${page.state_slug}/${page.city_slug}` },
              {
                name: page.item_name,
                path: `/${page.state_slug}/${page.city_slug}/dispose/${page.item_slug}`,
              },
            ]),
          ),
        }}
      />

      <nav className="crumb-row" aria-label="Breadcrumb">
        <Link href="/cities">Cities</Link>
        <span>/</span>
        <Link href={`/${page.state_slug}`}>{page.state}</Link>
        <span>/</span>
        <Link href={`/${page.state_slug}/${page.city_slug}`}>{page.city}</Link>
        <span>/</span>
        <span>{page.item_name}</span>
      </nav>

      <section className="answer-band">
        <StatusBadge badge={page.badge} />
        <h1>
          How to Dispose of {page.item_name} in {page.city}, {page.state}
        </h1>
        <p className="direct-answer">{page.answer}</p>
        {!page.indexable ? (
          <p>
            {page.item_name} is listed on the{" "}
            <Link href={`/${page.state_slug}/${page.city_slug}#${programKey}`}>
              {page.city} {programLabel} program
            </Link>
            . Same official source as the city {programLabel.toLowerCase()} rules.
          </p>
        ) : null}
        <div className="meta-row">
          <span>Category: {page.category}</span>
          <span>
            <Link href={`/materials/${page.item_slug}`}>
              {page.item_name} disposal near me
            </Link>
          </span>
          <span>
            <Link href={`/${page.state_slug}/${page.city_slug}#${programKey}`}>
              {page.city} {programLabel}
            </Link>
          </span>
          <span>
            City program
            {page.source_name ? ` · ${page.source_name}` : ""}
          </span>
          {page.last_verified_at ? <span>Verified {page.last_verified_at}</span> : null}
          {page.source_url ? (
            <SourceLink url={page.source_url} title={page.source_name}>
              View source
            </SourceLink>
          ) : null}
          {countyHhw ? (
            <span>
              <Link href={countyHhwHref(countyHhw)}>{countyHhw.county} HHW</Link>
            </span>
          ) : null}
        </div>
      </section>

      <QuickAnswerBar
        badgeLabel={badgeLabel(page.badge)}
        fee={page.common_disposal_fee}
        curbside={page.is_curbside_allowed}
        facilityType={page.nearest_facility_type}
        verifiedAt={page.last_verified_at}
        phone={primaryPhone}
        sourceUrl={page.source_url}
      />

      <DoThisNow
        steps={page.steps}
        sourceUrl={page.source_url}
        sourceName={page.source_name}
        phone={primaryPhone}
      />

      <LeadModule
        city={page.city}
        state={page.state}
        itemSlug={page.item_slug}
        itemName={page.item_name}
      />

      <ContinueReading
        id="related-same-city"
        heading={`Also disposing in ${page.city}?`}
        lead={`Related ${page.category.toLowerCase()} and common pickup items — next guide is one tap.`}
        links={pagesToContinueLinks(related, "item").map((l) => ({
          ...l,
          meta: l.meta?.replace(`in ${page.city} · `, "") ?? page.category,
        }))}
      />

      <FacilityMap
        city={page.city}
        lat={page.lat}
        lng={page.lng}
        facilities={page.facilities}
        zipRefs={zipRefs}
      />

      <AdSlot slot="inline" />

      <section>
        <h2>Local specifics</h2>
        <SpecsTable page={page} />
      </section>

      <FaqSection faqs={page.faqs} />

      <ContinueReading
        id="same-item-cities"
        heading={`${page.item_name} in other cities`}
        lead="Same item, different city rules — useful if you moved or are comparing nearby metros."
        links={pagesToContinueLinks(otherCities, "city")}
      />

      {zips.length ? (
        <ContinueReading
          id="zip-continue"
          heading={`ZIP pages near ${page.city}`}
          lead="Facility orientation by ZIP — then jump back into item guides."
          links={zips.slice(0, 6).map((z) => ({
            href: `/${z.state_slug}/${z.city_slug}/${z.zip}`,
            title: `ZIP ${z.zip}`,
            meta: `${page.city} hub context`,
          }))}
        />
      ) : null}

      {siblingCities.length ? (
        <ContinueReading
          id="nearby-cities"
          heading={`More ${page.state} cities`}
          lead="Verified guides in nearby metros — keep browsing on DumpRegistry."
          links={siblingCities.map((c) => ({
            href: `/${c.state_slug}/${c.city_slug}`,
            title: c.city,
            meta: `${getCityPages(c.state_slug, c.city_slug).length} guides`,
          }))}
        />
      ) : null}

      <CityItemFinder
        city={page.city}
        heading={`All guides in ${page.city}`}
        lead={`Browse all ${cityGuides.length} other verified guides (70 total including this page).`}
        hubHref={`/${page.state_slug}/${page.city_slug}`}
        hubLabel={`${page.city} hub`}
        guides={cityGuides.map((p) => ({
          item_slug: p.item_slug,
          item_name: p.item_name,
          category: p.category,
          state_slug: p.state_slug,
          city_slug: p.city_slug,
          badge: p.badge,
          href: cityItemHref(p),
        }))}
      />

      <CorrectionWidget
        city={page.city}
        stateSlug={page.state_slug}
        citySlug={page.city_slug}
        itemSlug={page.item_slug}
      />
      <AdSlot slot="anchor" />
    </div>
  );
}
