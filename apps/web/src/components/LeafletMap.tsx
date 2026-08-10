"use client";

import { useEffect } from "react";
import { MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

export type MapPin = {
  id: string;
  name: string;
  lat: number;
  lng: number;
  detail?: string;
};

const pinIcon = L.divIcon({
  className: "dr-pin",
  html: `<span class="dr-pin-dot"></span>`,
  iconSize: [22, 22],
  iconAnchor: [11, 11],
  popupAnchor: [0, -10],
});

const activePinIcon = L.divIcon({
  className: "dr-pin dr-pin-active",
  html: `<span class="dr-pin-dot"></span>`,
  iconSize: [28, 28],
  iconAnchor: [14, 14],
  popupAnchor: [0, -12],
});

function FitOrFly({
  pins,
  activeId,
}: {
  pins: MapPin[];
  activeId: string | null;
}) {
  const map = useMap();

  useEffect(() => {
    if (!pins.length) return;
    const active = activeId ? pins.find((p) => p.id === activeId) : null;
    if (active) {
      map.flyTo([active.lat, active.lng], Math.max(map.getZoom(), 13), { duration: 0.45 });
      return;
    }
    if (pins.length === 1) {
      map.setView([pins[0].lat, pins[0].lng], 13);
      return;
    }
    const bounds = L.latLngBounds(pins.map((p) => [p.lat, p.lng] as [number, number]));
    map.fitBounds(bounds.pad(0.2));
  }, [map, pins, activeId]);

  return null;
}

export function LeafletMap({
  pins,
  activeId,
  onSelect,
  fallbackCenter,
}: {
  pins: MapPin[];
  activeId: string | null;
  onSelect?: (id: string) => void;
  fallbackCenter?: { lat: number; lng: number } | null;
}) {
  const center =
    pins[0] != null
      ? { lat: pins[0].lat, lng: pins[0].lng }
      : (fallbackCenter ?? { lat: 39.5, lng: -98.35 });

  return (
    <MapContainer
      center={[center.lat, center.lng]}
      zoom={pins.length ? 12 : 5}
      className="leaflet-host"
      scrollWheelZoom={false}
      attributionControl
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <FitOrFly pins={pins} activeId={activeId} />
      {pins.map((p) => (
        <Marker
          key={p.id}
          position={[p.lat, p.lng]}
          icon={p.id === activeId ? activePinIcon : pinIcon}
          eventHandlers={{
            click: () => onSelect?.(p.id),
          }}
        >
          <Popup>
            <strong>{p.name}</strong>
            {p.detail ? <div>{p.detail}</div> : null}
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
