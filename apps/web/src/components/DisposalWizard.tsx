"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";

type ItemOpt = { slug: string; name: string; category: string };
type CityOpt = { city_slug: string; city: string; state_slug: string; state: string };

export function DisposalWizard({
  items,
  cities,
}: {
  items: ItemOpt[];
  cities: CityOpt[];
}) {
  const router = useRouter();
  const [item, setItem] = useState(items[0]?.slug ?? "");
  const [city, setCity] = useState(cities[0]?.city_slug ?? "");
  const [zip, setZip] = useState("");

  const selectedCity = useMemo(
    () => cities.find((c) => c.city_slug === city),
    [cities, city],
  );

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedCity || !item) return;
    if (zip.trim().length === 5) {
      router.push(`/${selectedCity.state_slug}/${selectedCity.city_slug}/${zip.trim()}`);
      return;
    }
    router.push(`/${selectedCity.state_slug}/${selectedCity.city_slug}/dispose/${item}`);
  }

  return (
    <form className="wizard" onSubmit={onSubmit}>
      <label>
        <span>What are you disposing?</span>
        <select value={item} onChange={(e) => setItem(e.target.value)} required>
          {items.map((i) => (
            <option key={i.slug} value={i.slug}>
              {i.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        <span>City</span>
        <select value={city} onChange={(e) => setCity(e.target.value)} required>
          {cities.map((c) => (
            <option key={c.city_slug} value={c.city_slug}>
              {c.city}, {c.state}
            </option>
          ))}
        </select>
      </label>
      <label>
        <span>ZIP (optional)</span>
        <input
          inputMode="numeric"
          pattern="[0-9]{5}"
          maxLength={5}
          placeholder="e.g. 90012"
          value={zip}
          onChange={(e) => setZip(e.target.value.replace(/\D/g, "").slice(0, 5))}
        />
      </label>
      <button type="submit" className="btn-primary">
        Show me what to do
      </button>
    </form>
  );
}
