"use client";

import dynamic from "next/dynamic";
import { useMemo, useState } from "react";
import { NearMeBar } from "@/components/NearMeBar";
import { OfficialLink } from "@/components/OfficialViewer";
import { formatMiles, sortByDistance, type LatLng } from "@/lib/geo";
import type { Facility } from "@/lib/types";

const LeafletMap = dynamic(
  () => import("@/components/LeafletMap").then((m) => m.LeafletMap),
  {
    ssr: false,
    loading: () => <div className="map-frame live-map map-loading">Loading map…</div>,
  },
);

function telHref(phone: string) {
  const digits = phone.replace(/[^\d+]/g, "");
  return digits ? `tel:${digits}` : null;
}

export function FacilityMap({
  city,
  lat,
  lng,
  facilities = [],
  zipRefs = [],
}: {
  city: string;
  lat?: number | null;
  lng?: number | null;
  facilities?: Facility[];
  zipRefs?: Array<{ zip: string; lat?: number | null; lng?: number | null }>;
}) {
  const cityCenter =
    lat != null && lng != null ? ({ lat, lng } satisfies LatLng) : null;
  const [origin, setOrigin] = useState<(LatLng & { label: string }) | null>(() => {
    const only = zipRefs.length === 1 ? zipRefs[0] : null;
    if (only?.lat != null && only?.lng != null) {
      return { lat: only.lat, lng: only.lng, label: `ZIP ${only.zip}` };
    }
    return null;
  });
  const [activeId, setActiveId] = useState<string | null>(null);
  const [copied, setCopied] = useState<string | null>(null);

  const ranked = useMemo(() => {
    if (!origin) {
      return facilities.map((f) => ({ ...f, distanceMi: null as number | null }));
    }
    return sortByDistance(facilities, origin, (f) =>
      f.lat != null && f.lng != null ? { lat: f.lat, lng: f.lng } : null,
    );
  }, [facilities, origin]);

  const pins = useMemo(
    () =>
      ranked
        .filter((f) => f.lat != null && f.lng != null)
        .map((f) => ({
          id: f.name,
          name: f.name,
          lat: f.lat as number,
          lng: f.lng as number,
          detail: [
            f.address,
            f.distanceMi != null ? formatMiles(f.distanceMi) : null,
          ]
            .filter(Boolean)
            .join(" · "),
        })),
    [ranked],
  );

  const selectedId = activeId && pins.some((p) => p.id === activeId) ? activeId : (pins[0]?.id ?? null);

  async function copyText(label: string, value: string) {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(label);
      window.setTimeout(() => setCopied(null), 1800);
    } catch {
      setCopied(null);
    }
  }

  return (
    <section className="map-block" aria-labelledby="facilities-heading">
      <div className="map-heading-row">
        <h2 id="facilities-heading">Where to take it in {city}</h2>
        {pins.length > 0 ? <span className="map-stay-badge">Map stays on this page</span> : null}
      </div>

      {zipRefs.length || cityCenter ? (
        <NearMeBar
          zipRefs={zipRefs}
          cityCenter={cityCenter}
          onOriginChange={(next) => {
            setOrigin(next);
            setActiveId(null);
          }}
        />
      ) : null}

      {facilities.length === 0 ? (
        <p>
          No verified drop-off locations are listed for this city yet. Follow the steps and official source
          link on this page.
        </p>
      ) : (
        <div className={`facility-layout${pins.length ? " has-map" : ""}`}>
          {pins.length > 0 ? (
            <div className="map-frame live-map">
              <LeafletMap
                pins={pins}
                activeId={selectedId}
                onSelect={setActiveId}
                fallbackCenter={cityCenter}
              />
              <p className="map-active-label">
                {pins.length} pin{pins.length === 1 ? "" : "s"} on map
                {origin ? ` · nearest first from ${origin.label}` : " · tap a pin or list item"}
              </p>
            </div>
          ) : null}

          <ul className="facility-list">
            {ranked.map((f) => {
              const isPinned = f.lat != null && f.lng != null;
              const isActive = isPinned && f.name === selectedId;
              const call = f.phone ? telHref(f.phone) : null;

              return (
                <li key={f.name} className={isActive ? "facility-active" : undefined}>
                  <button
                    type="button"
                    className="facility-select"
                    onClick={() => {
                      if (isPinned) setActiveId(f.name);
                    }}
                    disabled={!isPinned}
                  >
                    <strong>
                      {f.name}
                      {f.distanceMi != null ? (
                        <span className="distance-chip">{formatMiles(f.distanceMi)}</span>
                      ) : null}
                    </strong>
                    <span>
                      {f.facility_type}
                      {f.address ? ` · ${f.address}` : ""}
                    </span>
                    {f.hours ? <span>Hours: {f.hours}</span> : null}
                    {f.phone ? <span>Phone: {f.phone}</span> : null}
                    {isPinned ? (
                      <span className="facility-map-hint">
                        {isActive ? "Shown on map" : "Tap to show on map"}
                      </span>
                    ) : null}
                  </button>

                  <div className="facility-actions">
                    {call ? (
                      <a className="facility-action" href={call}>
                        Call
                      </a>
                    ) : null}
                    {f.address ? (
                      <button
                        type="button"
                        className="facility-action"
                        onClick={() => copyText(f.name, f.address || "")}
                      >
                        {copied === f.name ? "Copied" : "Copy address"}
                      </button>
                    ) : null}
                    {f.source_url ? (
                      <OfficialLink
                        className="facility-action"
                        url={f.source_url}
                        title={f.name}
                      >
                        Official program
                      </OfficialLink>
                    ) : null}
                  </div>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </section>
  );
}
