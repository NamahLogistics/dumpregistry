import type { Facility } from "@/lib/types";

export function MapPlaceholder({
  lat,
  lng,
  city,
  facilities = [],
}: {
  lat: number | null;
  lng: number | null;
  city: string;
  facilities?: Facility[];
}) {
  return (
    <section className="map-block" aria-labelledby="map-heading">
      <h2 id="map-heading">Nearby drop-off context</h2>
      <div className="map-frame">
        <div className="map-grid" />
        <p className="map-coords">
          {lat != null && lng != null
            ? `${city} centroid ≈ ${lat.toFixed(4)}, ${lng.toFixed(4)}`
            : `${city} — coordinates unavailable`}
        </p>
        <p className="map-note">
          Facility list below is from city program pages (addresses/hours). Confirm before you haul — programs change.
        </p>
      </div>
      {facilities.length > 0 ? (
        <ul className="facility-list">
          {facilities.map((f) => (
            <li key={f.name}>
              <strong>{f.name}</strong>
              <span>
                {f.facility_type}
                {f.address ? ` · ${f.address}` : ""}
              </span>
              {f.hours ? <span>Hours: {f.hours}</span> : null}
              {f.phone ? <span>Phone: {f.phone}</span> : null}
              {f.source_url ? (
                <a href={f.source_url} rel="noopener noreferrer" target="_blank">
                  Official info
                </a>
              ) : null}
            </li>
          ))}
        </ul>
      ) : (
        <p>
          No city facility rows yet for this location — we only list drop-offs after verifying a city program
          page.
        </p>
      )}
    </section>
  );
}
