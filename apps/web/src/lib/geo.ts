export type LatLng = { lat: number; lng: number };

/** Great-circle distance in miles. */
export function milesBetween(a: LatLng, b: LatLng): number {
  const toRad = (d: number) => (d * Math.PI) / 180;
  const R = 3958.8;
  const dLat = toRad(b.lat - a.lat);
  const dLng = toRad(b.lng - a.lng);
  const lat1 = toRad(a.lat);
  const lat2 = toRad(b.lat);
  const h =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLng / 2) ** 2;
  return 2 * R * Math.asin(Math.min(1, Math.sqrt(h)));
}

export function formatMiles(mi: number): string {
  if (mi < 0.1) return "<0.1 mi";
  if (mi < 10) return `${mi.toFixed(1)} mi`;
  return `${Math.round(mi)} mi`;
}

export function sortByDistance<T>(
  items: T[],
  origin: LatLng,
  coords: (item: T) => LatLng | null | undefined,
): Array<T & { distanceMi: number | null }> {
  return items
    .map((item) => {
      const c = coords(item);
      return {
        ...item,
        distanceMi: c ? milesBetween(origin, c) : null,
      };
    })
    .sort((a, b) => {
      if (a.distanceMi == null && b.distanceMi == null) return 0;
      if (a.distanceMi == null) return 1;
      if (b.distanceMi == null) return -1;
      return a.distanceMi - b.distanceMi;
    });
}
