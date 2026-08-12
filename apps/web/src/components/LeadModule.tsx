"use client";

import { useState } from "react";
import { trackEvent } from "@/lib/analytics";

export function LeadModule({
  city,
  state,
  itemSlug,
}: {
  city: string;
  state: string;
  itemSlug?: string;
}) {
  const [status, setStatus] = useState<"idle" | "ok" | "err">("idle");

  async function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const res = await fetch("/api/leads", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        city,
        state,
        itemSlug,
        name: fd.get("name"),
        email: fd.get("email"),
        phone: fd.get("phone"),
        notes: fd.get("notes"),
      }),
    });
    setStatus(res.ok ? "ok" : "err");
    if (res.ok) {
      trackEvent("generate_lead", {
        lead_type: "pickup",
        city,
        state,
        item_slug: itemSlug,
      });
      e.currentTarget.reset();
    }
  }

  return (
    <section className="lead-module" aria-labelledby="lead-heading">
      <h2 id="lead-heading">Need pickup in {city}?</h2>
      <p>
        If you cannot haul it yourself, request pickup options. We may share this request with vetted local
        haulers in our lead marketplace. Optional — separate from the free disposal answer above.
      </p>
      <form onSubmit={submit} className="lead-form">
        <label>
          Name
          <input name="name" required maxLength={120} />
        </label>
        <label>
          Email
          <input name="email" type="email" required maxLength={200} />
        </label>
        <label>
          Phone
          <input name="phone" type="tel" maxLength={40} />
        </label>
        <label>
          Notes
          <textarea name="notes" maxLength={1000} placeholder="Item size, stairs, timing…" />
        </label>
        <button type="submit" className="btn-secondary">
          Request pickup options
        </button>
        {status === "ok" ? <p className="form-ok">Request received.</p> : null}
        {status === "err" ? <p className="form-err">Something went wrong.</p> : null}
      </form>
    </section>
  );
}
