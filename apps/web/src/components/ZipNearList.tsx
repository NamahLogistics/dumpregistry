"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { NearMeBar } from "@/components/NearMeBar";
import { formatMiles, sortByDistance, type LatLng } from "@/lib/geo";

type ZipHubLite = {
  zip: string;
  state_slug: string;
  city_slug: string;
  lat?: number | null;
  lng?: number | null;
};

export function ZipNearList({
  zips,
  cityCenter,
}: {
  zips: ZipHubLite[];
  cityCenter?: LatLng | null;
}) {
  const [origin, setOrigin] = useState<(LatLng & { label: string }) | null>(null);

  const ranked = useMemo(() => {
    if (!origin) return zips.map((z) => ({ ...z, distanceMi: null as number | null }));
    return sortByDistance(zips, origin, (z) =>
      z.lat != null && z.lng != null ? { lat: z.lat, lng: z.lng } : null,
    );
  }, [zips, origin]);

  if (!zips.length) return null;

  return (
    <section className="zip-near" aria-labelledby="zip-near-heading">
      <h2 id="zip-near-heading">ZIP hubs near you</h2>
      <NearMeBar zipRefs={zips} cityCenter={cityCenter} onOriginChange={setOrigin} />
      <div className="hub-grid">
        {ranked.map((z) => (
          <Link
            key={z.zip}
            className="hub-link"
            href={`/${z.state_slug}/${z.city_slug}/${z.zip}`}
          >
            {z.zip}
            {z.distanceMi != null ? (
              <span className="hub-link-meta">{formatMiles(z.distanceMi)} away</span>
            ) : (
              <span className="hub-link-meta">ZIP hub</span>
            )}
          </Link>
        ))}
      </div>
    </section>
  );
}
