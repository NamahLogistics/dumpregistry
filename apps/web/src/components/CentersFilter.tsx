"use client";

import { useRouter } from "next/navigation";
import { useEffect, useId, useMemo, useRef, useState } from "react";

type ItemOpt = { slug: string; name: string };

export function CentersFilter({
  initialZip,
  initialMaterial,
  items,
}: {
  initialZip: string;
  initialMaterial: string;
  items: ItemOpt[];
}) {
  const router = useRouter();
  const listId = useId();
  const inputRef = useRef<HTMLInputElement>(null);

  const [zip, setZip] = useState(initialZip);
  const [material, setMaterial] = useState(initialMaterial);
  const [materialInput, setMaterialInput] = useState("");
  const [open, setOpen] = useState(false);
  const [filterActive, setFilterActive] = useState(false);
  const [highlight, setHighlight] = useState(0);

  const selected = useMemo(
    () => items.find((i) => i.slug === material) ?? null,
    [items, material],
  );

  useEffect(() => {
    setMaterialInput(selected?.name ?? "");
  }, [selected]);

  const filtered = useMemo(() => {
    if (!filterActive) return items;
    const needle = materialInput.trim().toLowerCase();
    if (!needle) return items;
    return items.filter(
      (i) =>
        i.name.toLowerCase().includes(needle) ||
        i.slug.includes(needle.replace(/\s+/g, "-")),
    );
  }, [items, materialInput, filterActive]);

  function commitMaterial(slug: string) {
    setMaterial(slug);
    setMaterialInput(items.find((i) => i.slug === slug)?.name ?? "");
    setOpen(false);
    setFilterActive(false);
  }

  function restoreMaterialInput() {
    setMaterialInput(selected?.name ?? "");
    setFilterActive(false);
  }

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    let next = material;
    if (open || filterActive) {
      const needle = materialInput.trim().toLowerCase();
      if (!needle) {
        next = "";
      } else {
        const match =
          filtered.find((i) => i.name.toLowerCase() === needle) ?? filtered[0];
        next = match?.slug ?? material;
      }
      commitMaterial(next);
    }
    const params = new URLSearchParams();
    if (zip.trim()) params.set("zip", zip.trim());
    if (next) params.set("material", next);
    const qs = params.toString();
    router.push(qs ? `/centers?${qs}` : "/centers");
  }

  return (
    <form className="centers-filter" onSubmit={onSubmit}>
      <label>
        ZIP
        <input
          name="zip"
          type="text"
          inputMode="numeric"
          value={zip}
          onChange={(e) => setZip(e.target.value)}
          placeholder="e.g. 78701"
          maxLength={10}
        />
      </label>

      <div className={`centers-material-field${open ? " is-open" : ""}`}>
        <label htmlFor={listId}>
          What are you disposing?
          <input
            id={listId}
            ref={inputRef}
            role="combobox"
            aria-expanded={open}
            aria-controls={`${listId}-list`}
            aria-autocomplete="list"
            aria-activedescendant={
              open && filtered[highlight]
                ? `${listId}-opt-${filtered[highlight].slug}`
                : undefined
            }
            value={materialInput}
            onChange={(e) => {
              setMaterialInput(e.target.value);
              setFilterActive(true);
              setOpen(true);
              setHighlight(0);
              if (!e.target.value.trim()) setMaterial("");
            }}
            onFocus={() => {
              setOpen(true);
              setFilterActive(false);
              setMaterialInput(selected?.name ?? "");
              requestAnimationFrame(() => inputRef.current?.select());
            }}
            onBlur={() => {
              window.setTimeout(() => {
                setOpen(false);
                restoreMaterialInput();
              }, 180);
            }}
            onKeyDown={(e) => {
              if (e.key === "ArrowDown" || e.key === "ArrowUp") {
                e.preventDefault();
                setOpen(true);
              }
              if (!filtered.length && e.key !== "Enter") return;
              if (e.key === "ArrowDown") {
                setHighlight((h) => Math.min(h + 1, filtered.length - 1));
              } else if (e.key === "ArrowUp") {
                setHighlight((h) => Math.max(h - 1, 0));
              } else if (e.key === "Enter" && open) {
                e.preventDefault();
                const pick = filtered[highlight] ?? filtered[0];
                if (pick) commitMaterial(pick.slug);
                else commitMaterial("");
              } else if (e.key === "Escape") {
                setOpen(false);
                restoreMaterialInput();
              }
            }}
            placeholder="Any material — or type mattress, paint…"
            autoComplete="off"
          />
        </label>
        {open ? (
          <ul id={`${listId}-list`} className="wizard-suggest-list" role="listbox">
            <li role="presentation">
              <button
                type="button"
                role="option"
                aria-selected={!material}
                className={
                  !material && highlight === 0
                    ? "wizard-suggest-option is-active"
                    : "wizard-suggest-option"
                }
                onMouseDown={(e) => e.preventDefault()}
                onClick={() => commitMaterial("")}
              >
                <strong>Any material</strong>
                <span>All centers</span>
              </button>
            </li>
            {filtered.map((i, idx) => (
              <li key={i.slug} role="presentation">
                <button
                  type="button"
                  id={`${listId}-opt-${i.slug}`}
                  role="option"
                  aria-selected={i.slug === material}
                  className={
                    idx === highlight || i.slug === material
                      ? "wizard-suggest-option is-active"
                      : "wizard-suggest-option"
                  }
                  onMouseDown={(e) => e.preventDefault()}
                  onMouseEnter={() => setHighlight(idx)}
                  onClick={() => commitMaterial(i.slug)}
                >
                  <strong>{i.name}</strong>
                  <span>Material</span>
                </button>
              </li>
            ))}
            {!filtered.length ? (
              <li className="wizard-suggest-empty">No materials match that search.</li>
            ) : null}
          </ul>
        ) : null}
        {selected && !open ? (
          <p className="wizard-selected-line">
            Selected: <strong>{selected.name}</strong>
          </p>
        ) : null}
      </div>

      <button type="submit" className="btn-primary">
        Find centers
      </button>
    </form>
  );
}
