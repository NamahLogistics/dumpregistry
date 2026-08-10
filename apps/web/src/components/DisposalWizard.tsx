"use client";

import { useEffect, useId, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";

type ItemOpt = { slug: string; name: string; category: string };
type CityOpt = {
  key: string;
  city_slug: string;
  city: string;
  state_slug: string;
  state: string;
};

function cityLabel(c: CityOpt) {
  return `${c.city}, ${c.state}`;
}

export function DisposalWizard({
  items,
  cities,
  itemsByCity,
}: {
  items: ItemOpt[];
  cities: CityOpt[];
  itemsByCity: Record<string, string[]>;
}) {
  const router = useRouter();
  const listId = useId();
  const cityInputRef = useRef<HTMLInputElement>(null);
  const [cityKey, setCityKey] = useState(cities[0]?.key ?? "");
  const [cityQuery, setCityQuery] = useState(cities[0] ? cityLabel(cities[0]) : "");
  const [cityOpen, setCityOpen] = useState(false);
  const [cityHighlight, setCityHighlight] = useState(0);
  const [itemQuery, setItemQuery] = useState("");
  const [item, setItem] = useState("");

  const selectedCity = useMemo(
    () => cities.find((c) => c.key === cityKey) ?? null,
    [cities, cityKey],
  );

  const filteredCities = useMemo(() => {
    const needle = cityQuery.trim().toLowerCase();
    if (!needle) return cities;
    return cities.filter((c) => {
      const hay = `${c.city} ${c.state} ${c.city_slug} ${c.state_slug}`.toLowerCase();
      return hay.includes(needle) || cityLabel(c).toLowerCase().includes(needle);
    });
  }, [cities, cityQuery]);

  const allowedItemSlugs = useMemo(
    () => new Set(itemsByCity[cityKey] ?? []),
    [itemsByCity, cityKey],
  );

  const cityItems = useMemo(() => {
    const base = items.filter((i) => allowedItemSlugs.has(i.slug));
    const needle = itemQuery.trim().toLowerCase();
    if (!needle) return base;
    const slugNeedle = needle.replace(/\s+/g, "-");
    return base.filter(
      (i) =>
        i.name.toLowerCase().includes(needle) ||
        i.slug.includes(slugNeedle) ||
        i.category.toLowerCase().includes(needle),
    );
  }, [items, allowedItemSlugs, itemQuery]);

  useEffect(() => {
    if (!cityItems.length) {
      setItem("");
      return;
    }
    if (!cityItems.some((i) => i.slug === item)) {
      setItem(cityItems[0].slug);
    }
  }, [cityItems, item]);

  useEffect(() => {
    setCityHighlight(0);
  }, [cityQuery]);

  function pickCity(next: CityOpt) {
    setCityKey(next.key);
    setCityQuery(cityLabel(next));
    setCityOpen(false);
    setItemQuery("");
    const nextItems = items.filter((i) => (itemsByCity[next.key] ?? []).includes(i.slug));
    setItem(nextItems[0]?.slug ?? "");
  }

  function onCityInput(value: string) {
    setCityQuery(value);
    setCityOpen(true);
    const exact = cities.find((c) => cityLabel(c).toLowerCase() === value.trim().toLowerCase());
    if (exact) {
      setCityKey(exact.key);
    }
  }

  function onCityKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (!cityOpen && (e.key === "ArrowDown" || e.key === "Enter")) {
      setCityOpen(true);
    }
    if (!filteredCities.length) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setCityOpen(true);
      setCityHighlight((h) => Math.min(h + 1, filteredCities.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setCityHighlight((h) => Math.max(h - 1, 0));
    } else if (e.key === "Enter" && cityOpen) {
      e.preventDefault();
      pickCity(filteredCities[cityHighlight] ?? filteredCities[0]);
    } else if (e.key === "Escape") {
      setCityOpen(false);
      if (selectedCity) setCityQuery(cityLabel(selectedCity));
    }
  }

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    const pick = item || cityItems[0]?.slug;
    if (!selectedCity || !pick) return;
    router.push(`/${selectedCity.state_slug}/${selectedCity.city_slug}/dispose/${pick}`);
  }

  if (!cities.length) {
    return (
      <p className="wizard-empty">
        No verified city guides are published yet. Check back after we finish local research.
      </p>
    );
  }

  return (
    <form className="wizard wizard-expanded" onSubmit={onSubmit}>
      <div className="wizard-city">
        <label htmlFor={`${listId}-city`}>
          <span>City (type to search · {cities.length} verified)</span>
          <input
            id={`${listId}-city`}
            ref={cityInputRef}
            role="combobox"
            aria-expanded={cityOpen}
            aria-controls={`${listId}-city-list`}
            aria-autocomplete="list"
            aria-activedescendant={
              cityOpen && filteredCities[cityHighlight]
                ? `${listId}-opt-${filteredCities[cityHighlight].key}`
                : undefined
            }
            value={cityQuery}
            onChange={(e) => onCityInput(e.target.value)}
            onFocus={() => {
              setCityOpen(true);
              cityInputRef.current?.select();
            }}
            onBlur={() => {
              window.setTimeout(() => setCityOpen(false), 120);
              if (selectedCity) setCityQuery(cityLabel(selectedCity));
            }}
            onKeyDown={onCityKeyDown}
            placeholder="Start typing a city — Houston, Los Angeles…"
            autoComplete="off"
            required
          />
        </label>
        {cityOpen ? (
          <ul id={`${listId}-city-list`} className="wizard-city-list" role="listbox">
            {filteredCities.length ? (
              filteredCities.map((c, idx) => (
                <li key={c.key} role="presentation">
                  <button
                    type="button"
                    id={`${listId}-opt-${c.key}`}
                    role="option"
                    aria-selected={c.key === cityKey}
                    className={
                      idx === cityHighlight || c.key === cityKey
                        ? "wizard-city-option is-active"
                        : "wizard-city-option"
                    }
                    onMouseDown={(e) => e.preventDefault()}
                    onMouseEnter={() => setCityHighlight(idx)}
                    onClick={() => pickCity(c)}
                  >
                    <strong>{c.city}</strong>
                    <span>{c.state}</span>
                  </button>
                </li>
              ))
            ) : (
              <li className="wizard-city-empty">No verified city matches “{cityQuery.trim()}”.</li>
            )}
          </ul>
        ) : null}
        {selectedCity ? (
          <p className="wizard-city-selected">
            Selected: <strong>{cityLabel(selectedCity)}</strong>
            {" · "}
            {(itemsByCity[selectedCity.key] ?? []).length} guides
          </p>
        ) : (
          <p className="wizard-empty">Choose a city from the list.</p>
        )}
      </div>

      <label>
        <span>What are you disposing? (type to filter)</span>
        <input
          value={itemQuery}
          onChange={(e) => setItemQuery(e.target.value)}
          placeholder="mattress, paint, TV, fridge…"
          autoComplete="off"
          disabled={!selectedCity}
        />
      </label>

      <div className="wizard-items">
        <span className="wizard-items-label">
          Matching items{selectedCity ? ` in ${selectedCity.city}` : ""}
          {cityItems.length ? ` · ${cityItems.length}` : ""}
        </span>
        {cityItems.length ? (
          <ul className="wizard-item-list" role="listbox" aria-label="Matching items">
            {cityItems.slice(0, 12).map((i) => (
              <li key={i.slug}>
                <button
                  type="button"
                  role="option"
                  aria-selected={i.slug === item}
                  className={i.slug === item ? "wizard-item-option is-active" : "wizard-item-option"}
                  onClick={() => setItem(i.slug)}
                >
                  <strong>{i.name}</strong>
                  <span>{i.category}</span>
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <p className="wizard-empty">No items match that search in this city.</p>
        )}
        {cityItems.length > 12 ? (
          <p className="wizard-empty">Showing top 12 matches — refine your search to narrow further.</p>
        ) : null}
      </div>

      <button type="submit" className="btn-primary" disabled={!selectedCity || !item}>
        Show me what to do
      </button>
    </form>
  );
}
