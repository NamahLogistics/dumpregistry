"use client";

import { useMemo, useState } from "react";
import type { LatLng } from "@/lib/geo";

type ZipRef = {
  zip: string;
  lat?: number | null;
  lng?: number | null;
};

export function NearMeBar({
  zipRefs,
  cityCenter,
  onOriginChange,
}: {
  zipRefs: ZipRef[];
  cityCenter?: LatLng | null;
  onOriginChange: (origin: (LatLng & { label: string }) | null) => void;
}) {
  const [zip, setZip] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const byZip = useMemo(() => {
    const m = new Map<string, ZipRef>();
    for (const z of zipRefs) m.set(z.zip, z);
    return m;
  }, [zipRefs]);

  function applyZip(raw: string) {
    const cleaned = raw.replace(/\D/g, "").slice(0, 5);
    setZip(cleaned);
    if (cleaned.length !== 5) {
      onOriginChange(null);
      setStatus(cleaned.length ? "Enter a 5-digit ZIP" : null);
      return;
    }
    const hit = byZip.get(cleaned);
    if (hit?.lat != null && hit?.lng != null) {
      onOriginChange({ lat: hit.lat, lng: hit.lng, label: `ZIP ${cleaned}` });
      setStatus(`Sorting nearest to ZIP ${cleaned}`);
      return;
    }
    if (cityCenter) {
      onOriginChange({ ...cityCenter, label: `ZIP ${cleaned} (city center)` });
      setStatus(`No hub coords for ${cleaned} — using city center`);
      return;
    }
    onOriginChange(null);
    setStatus(`No location for ZIP ${cleaned} yet`);
  }

  function useLocation() {
    if (!navigator.geolocation) {
      setStatus("Location not available in this browser");
      return;
    }
    setStatus("Getting your location…");
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        onOriginChange({
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
          label: "Your location",
        });
        setStatus("Sorting nearest to you");
      },
      () => setStatus("Could not read location — try a ZIP instead"),
      { enableHighAccuracy: false, timeout: 8000 },
    );
  }

  return (
    <div className="near-me-bar">
      <label className="near-me-zip">
        <span>Near me</span>
        <input
          inputMode="numeric"
          pattern="[0-9]*"
          maxLength={5}
          placeholder="ZIP"
          value={zip}
          onChange={(e) => applyZip(e.target.value)}
          aria-label="Sort by ZIP code"
        />
      </label>
      <button type="button" className="facility-action" onClick={useLocation}>
        Use my location
      </button>
      {status ? <span className="near-me-status">{status}</span> : null}
    </div>
  );
}
