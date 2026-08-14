"use client";

import { useState } from "react";
import Link from "next/link";
import { trackEvent } from "@/lib/analytics";

export function LeadModule({
  city,
  state,
  itemSlug,
  itemName,
  askLocation = false,
}: {
  city?: string;
  state?: string;
  itemSlug?: string;
  itemName?: string;
  askLocation?: boolean;
}) {
  const [status, setStatus] = useState<"idle" | "ok" | "unmatched" | "err">("idle");
  const item = itemName || "this item";

  async function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const cityVal = String(fd.get("city") ?? city ?? "").trim();
    const stateVal = String(fd.get("state") ?? state ?? "").trim();
    const res = await fetch("/api/leads", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        city: cityVal,
        state: stateVal,
        zip: fd.get("zip"),
        itemSlug,
        name: fd.get("name"),
        email: fd.get("email"),
        phone: fd.get("phone"),
        notes: fd.get("notes"),
      }),
    });
    const data = await res.json().catch(() => ({}));
    if (res.ok) {
      setStatus(data.routed ? "ok" : "unmatched");
      trackEvent("generate_lead", {
        lead_type: "pickup",
        city: cityVal,
        state: stateVal,
        item_slug: itemSlug,
      });
      e.currentTarget.reset();
    } else {
      setStatus("err");
    }
  }

  return (
    <section className="lead-module" aria-labelledby="lead-heading">
      <p className="lead-kicker">Pickup quote</p>
      <h2 id="lead-heading">Can’t take this {item} yourself?</h2>
      <p>
        The official drop-off steps above stay free. If you want someone to haul it, a hauler in our network
        may call with a quote — you pay them, not DumpRegistry.
      </p>
      <form onSubmit={submit} className="lead-form">
        {askLocation ? (
          <div className="lead-form-row">
            <label>
              City
              <input name="city" required maxLength={120} placeholder="Your city" defaultValue={city} />
            </label>
            <label>
              State
              <input name="state" required maxLength={40} placeholder="TX" defaultValue={state} />
            </label>
          </div>
        ) : (
          <>
            <input type="hidden" name="city" value={city} />
            <input type="hidden" name="state" value={state} />
          </>
        )}
        <div className="lead-form-row">
          <label>
            Name
            <input name="name" required maxLength={120} autoComplete="name" />
          </label>
          <label>
            Phone
            <input name="phone" type="tel" required maxLength={40} autoComplete="tel" placeholder="So they can quote you" />
          </label>
        </div>
        <div className="lead-form-row">
          <label>
            Email
            <input name="email" type="email" required maxLength={200} autoComplete="email" />
          </label>
          <label>
            ZIP
            <input
              name="zip"
              required
              inputMode="numeric"
              pattern="[0-9]{5}"
              maxLength={10}
              autoComplete="postal-code"
              placeholder="12345"
            />
          </label>
        </div>
        <label>
          What should they know?
          <textarea name="notes" maxLength={1000} placeholder="Size, stairs, timing, gate code…" />
        </label>
        <button type="submit" className="btn-primary">
          Get a pickup quote
        </button>
        <p className="lead-privacy">
          We’ll share this with at most one hauler whose coverage includes your ZIP. Not a bid war.{" "}
          <Link href="/privacy">Privacy</Link>
        </p>
        {status === "ok" ? (
          <p className="form-ok">Request sent to one hauler who covers your ZIP. They may call with a quote.</p>
        ) : null}
        {status === "unmatched" ? (
          <p className="form-ok">Request received. No hauler in our network covers that ZIP yet — nobody will call until one does.</p>
        ) : null}
        {status === "err" ? <p className="form-err">Something went wrong. Try again.</p> : null}
      </form>
    </section>
  );
}
