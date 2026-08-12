"use client";

import { useEffect, useId, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { trackEvent } from "@/lib/analytics";

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
  const itemInputRef = useRef<HTMLInputElement>(null);

  const initialCity = cities[0] ?? null;
  const initialItemSlug = initialCity
    ? (itemsByCity[initialCity.key] ?? [])[0] ?? ""
    : "";
  const initialItem = initialItemSlug
    ? items.find((i) => i.slug === initialItemSlug) ?? null
    : null;

  const [cityKey, setCityKey] = useState(initialCity?.key ?? "");
  const [cityInput, setCityInput] = useState(initialCity ? cityLabel(initialCity) : "");
  const [cityOpen, setCityOpen] = useState(false);
  const [cityFilter, setCityFilter] = useState(false);
  const [cityHighlight, setCityHighlight] = useState(0);

  const [itemSlug, setItemSlug] = useState(initialItem?.slug ?? "");
  const [itemInput, setItemInput] = useState(initialItem?.name ?? "");
  const [itemOpen, setItemOpen] = useState(false);
  const [itemFilter, setItemFilter] = useState(false);
  const [itemHighlight, setItemHighlight] = useState(0);

  const selectedCity = useMemo(
    () => cities.find((c) => c.key === cityKey) ?? null,
    [cities, cityKey],
  );

  const selectedItem = useMemo(
    () => items.find((i) => i.slug === itemSlug) ?? null,
    [items, itemSlug],
  );

  const filteredCities = useMemo(() => {
    if (!cityFilter) return cities;
    const needle = cityInput.trim().toLowerCase();
    if (!needle) return cities;
    return cities.filter((c) => {
      const hay = `${c.city} ${c.state} ${c.city_slug} ${c.state_slug}`.toLowerCase();
      return hay.includes(needle) || cityLabel(c).toLowerCase().includes(needle);
    });
  }, [cities, cityInput, cityFilter]);

  const allowedItemSlugs = useMemo(
    () => new Set(itemsByCity[cityKey] ?? []),
    [itemsByCity, cityKey],
  );

  const cityItems = useMemo(() => {
    const base = items.filter((i) => allowedItemSlugs.has(i.slug));
    if (!itemFilter) return base;
    const needle = itemInput.trim().toLowerCase();
    if (!needle) return base;
    const slugNeedle = needle.replace(/\s+/g, "-");
    return base.filter(
      (i) =>
        i.name.toLowerCase().includes(needle) ||
        i.slug.includes(slugNeedle) ||
        i.category.toLowerCase().includes(needle),
    );
  }, [items, allowedItemSlugs, itemInput, itemFilter]);

  // Keep item selection valid when city changes / on first paint.
  useEffect(() => {
    if (!selectedCity) return;
    const allowed = itemsByCity[selectedCity.key] ?? [];
    if (!allowed.length) {
      setItemSlug("");
      setItemInput("");
      return;
    }
    if (!allowed.includes(itemSlug)) {
      const first = items.find((i) => i.slug === allowed[0]);
      setItemSlug(first?.slug ?? "");
      setItemInput(first?.name ?? "");
      setItemFilter(false);
      setItemOpen(false);
    }
  }, [selectedCity, itemsByCity, items, itemSlug]);

  useEffect(() => {
    setCityHighlight(0);
  }, [cityInput, cityFilter, cityOpen]);

  useEffect(() => {
    setItemHighlight(0);
  }, [itemInput, itemFilter, itemOpen]);

  function commitCity(next: CityOpt) {
    setCityKey(next.key);
    setCityInput(cityLabel(next));
    setCityOpen(false);
    setCityFilter(false);
    const nextSlugs = itemsByCity[next.key] ?? [];
    const first = items.find((i) => i.slug === nextSlugs[0]);
    setItemSlug(first?.slug ?? "");
    setItemInput(first?.name ?? "");
    setItemFilter(false);
    setItemOpen(false);
  }

  function commitItem(next: ItemOpt) {
    setItemSlug(next.slug);
    setItemInput(next.name);
    setItemOpen(false);
    setItemFilter(false);
  }

  function restoreCityInput() {
    if (selectedCity) setCityInput(cityLabel(selectedCity));
    setCityFilter(false);
  }

  function restoreItemInput() {
    if (selectedItem) setItemInput(selectedItem.name);
    setItemFilter(false);
  }

  function onCityKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      setCityOpen(true);
    }
    if (!filteredCities.length) return;
    if (e.key === "ArrowDown") {
      setCityHighlight((h) => Math.min(h + 1, filteredCities.length - 1));
    } else if (e.key === "ArrowUp") {
      setCityHighlight((h) => Math.max(h - 1, 0));
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (cityOpen) {
        commitCity(filteredCities[cityHighlight] ?? filteredCities[0]);
      }
    } else if (e.key === "Escape") {
      setCityOpen(false);
      restoreCityInput();
    }
  }

  function onItemKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (!selectedCity) return;
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      setItemOpen(true);
    }
    if (!cityItems.length) return;
    if (e.key === "ArrowDown") {
      setItemHighlight((h) => Math.min(h + 1, cityItems.length - 1));
    } else if (e.key === "ArrowUp") {
      setItemHighlight((h) => Math.max(h - 1, 0));
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (itemOpen) {
        commitItem(cityItems[itemHighlight] ?? cityItems[0]);
      }
    } else if (e.key === "Escape") {
      setItemOpen(false);
      restoreItemInput();
    }
  }

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();

    let city = selectedCity;
    if (cityOpen || cityFilter) {
      const exact = filteredCities.find(
        (c) => cityLabel(c).toLowerCase() === cityInput.trim().toLowerCase(),
      );
      city = exact ?? filteredCities[0] ?? city;
      if (city) commitCity(city);
    }
    if (!city) return;

    const allowed = new Set(itemsByCity[city.key] ?? []);
    const pool = items.filter((i) => allowed.has(i.slug));
    const needle = itemInput.trim().toLowerCase();
    const slugNeedle = needle.replace(/\s+/g, "-");
    const matches =
      itemFilter && needle
        ? pool.filter(
            (i) =>
              i.name.toLowerCase().includes(needle) ||
              i.slug.includes(slugNeedle) ||
              i.category.toLowerCase().includes(needle),
          )
        : pool;
    const item =
      matches.find((i) => i.name.toLowerCase() === needle) ??
      matches.find((i) => i.slug === itemSlug) ??
      matches[0];
    if (!item) return;
    commitItem(item);
    trackEvent("wizard_complete", {
      city: city.city,
      state: city.state,
      item_slug: item.slug,
    });
    router.push(`/${city.state_slug}/${city.city_slug}/dispose/${item.slug}`);
  }

  if (!cities.length) {
    return (
      <p className="wizard-empty">
        No verified city guides are published yet. Check back after we finish local research.
      </p>
    );
  }

  const visibleItems = cityItems.slice(0, 40);

  return (
    <form className="wizard wizard-expanded" onSubmit={onSubmit}>
      <div className={`wizard-field${cityOpen ? " is-open" : ""}`}>
        <label htmlFor={`${listId}-city`}>
          <span>Where are you? (type to search · {cities.length} cities)</span>
          <input
            id={`${listId}-city`}
            ref={cityInputRef}
            role="combobox"
            aria-expanded={cityOpen}
            aria-controls={`${listId}-city-list`}
            aria-autocomplete="list"
            aria-activedescendant={
              cityOpen && filteredCities[cityHighlight]
                ? `${listId}-city-opt-${filteredCities[cityHighlight].key}`
                : undefined
            }
            value={cityInput}
            onChange={(e) => {
              setCityInput(e.target.value);
              setCityFilter(true);
              setCityOpen(true);
            }}
            onPointerDown={() => {
              setCityOpen(true);
              setCityFilter(false);
            }}
            onFocus={() => {
              setCityOpen(true);
              setCityFilter(false);
              if (selectedCity) setCityInput(cityLabel(selectedCity));
              requestAnimationFrame(() => cityInputRef.current?.select());
            }}
            onBlur={() => {
              window.setTimeout(() => {
                setCityOpen(false);
                restoreCityInput();
              }, 180);
            }}
            onKeyDown={onCityKeyDown}
            placeholder="Start typing a city — Houston, Los Angeles…"
            autoComplete="off"
            required
          />
        </label>
        {cityOpen ? (
          <ul id={`${listId}-city-list`} className="wizard-suggest-list" role="listbox">
            {filteredCities.length ? (
              filteredCities.map((c, idx) => (
                <li key={c.key} role="presentation">
                  <button
                    type="button"
                    id={`${listId}-city-opt-${c.key}`}
                    role="option"
                    aria-selected={c.key === cityKey}
                    className={
                      idx === cityHighlight || c.key === cityKey
                        ? "wizard-suggest-option is-active"
                        : "wizard-suggest-option"
                    }
                    onMouseDown={(e) => e.preventDefault()}
                    onMouseEnter={() => setCityHighlight(idx)}
                    onClick={() => commitCity(c)}
                  >
                    <strong>{c.city}</strong>
                    <span>{c.state}</span>
                  </button>
                </li>
              ))
            ) : (
              <li className="wizard-suggest-empty">No verified city matches “{cityInput.trim()}”.</li>
            )}
          </ul>
        ) : null}
        {selectedCity && !cityOpen ? (
          <p className="wizard-selected-line">
            Selected: <strong>{cityLabel(selectedCity)}</strong>
            {" · "}
            {(itemsByCity[selectedCity.key] ?? []).length} guides
          </p>
        ) : null}
      </div>

      <div className={`wizard-field${itemOpen ? " is-open" : ""}`}>
        <label htmlFor={`${listId}-item`}>
          <span>What are you disposing? (type to search)</span>
          <input
            id={`${listId}-item`}
            ref={itemInputRef}
            role="combobox"
            aria-expanded={itemOpen}
            aria-controls={`${listId}-item-list`}
            aria-autocomplete="list"
            aria-activedescendant={
              itemOpen && visibleItems[itemHighlight]
                ? `${listId}-item-opt-${visibleItems[itemHighlight].slug}`
                : undefined
            }
            value={itemInput}
            onChange={(e) => {
              setItemInput(e.target.value);
              setItemFilter(true);
              setItemOpen(true);
            }}
            onPointerDown={() => {
              if (!selectedCity) return;
              setItemOpen(true);
              setItemFilter(false);
            }}
            onFocus={() => {
              if (!selectedCity) return;
              setItemOpen(true);
              setItemFilter(false);
              if (selectedItem) setItemInput(selectedItem.name);
              requestAnimationFrame(() => itemInputRef.current?.select());
            }}
            onBlur={() => {
              window.setTimeout(() => {
                setItemOpen(false);
                restoreItemInput();
              }, 180);
            }}
            onKeyDown={onItemKeyDown}
            placeholder={
              selectedCity ? "mattress, paint, TV, fridge…" : "Select a city first"
            }
            autoComplete="off"
            disabled={!selectedCity}
            required
          />
        </label>
        {itemOpen && selectedCity ? (
          <ul id={`${listId}-item-list`} className="wizard-suggest-list" role="listbox">
            {visibleItems.length ? (
              visibleItems.map((i, idx) => (
                <li key={i.slug} role="presentation">
                  <button
                    type="button"
                    id={`${listId}-item-opt-${i.slug}`}
                    role="option"
                    aria-selected={i.slug === itemSlug}
                    className={
                      idx === itemHighlight || i.slug === itemSlug
                        ? "wizard-suggest-option is-active"
                        : "wizard-suggest-option"
                    }
                    onMouseDown={(e) => e.preventDefault()}
                    onMouseEnter={() => setItemHighlight(idx)}
                    onClick={() => commitItem(i)}
                  >
                    <strong>{i.name}</strong>
                    <span>{i.category}</span>
                  </button>
                </li>
              ))
            ) : (
              <li className="wizard-suggest-empty">
                No items match “{itemInput.trim()}” in {selectedCity.city}.
              </li>
            )}
          </ul>
        ) : null}
        {selectedItem && selectedCity && !itemOpen ? (
          <p className="wizard-selected-line">
            Selected: <strong>{selectedItem.name}</strong>
            {" · "}
            {selectedItem.category}
          </p>
        ) : null}
      </div>

      <button type="submit" className="btn-primary" disabled={!selectedCity || !itemSlug}>
        Show me what to do
      </button>
    </form>
  );
}
