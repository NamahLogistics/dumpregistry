"use client";

import { FormEvent, Suspense, useMemo, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { trackEvent } from "@/lib/analytics";

function PartnersForm() {
  const params = useSearchParams();
  const presetCity = params.get("city") ?? "";
  const [status, setStatus] = useState<"idle" | "ok" | "err">("idle");

  const cityDefault = useMemo(() => {
    if (!presetCity) return "";
    return presetCity
      .split("-")
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
      .join(" ");
  }, [presetCity]);

  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const res = await fetch("/api/partners", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        company: fd.get("company"),
        contactName: fd.get("contactName"),
        email: fd.get("email"),
        phone: fd.get("phone"),
        cities: fd.get("cities"),
        services: fd.get("services"),
        notes: fd.get("notes"),
        plan: fd.get("plan"),
      }),
    });
    setStatus(res.ok ? "ok" : "err");
    if (res.ok) {
      trackEvent("generate_lead", {
        lead_type: "partner",
        plan: String(fd.get("plan") ?? ""),
      });
      e.currentTarget.reset();
    }
  }

  return (
    <form className="partner-form" onSubmit={submit}>
      <label>
        Plan
        <select name="plan" defaultValue="pilot" required>
          <option value="pilot">Network trial — 10 free leads in your coverage area</option>
          <option value="starter">Coverage — pay per lead wherever you work</option>
          <option value="exclusive">Exclusive metro — sole partner in one city (later)</option>
        </select>
      </label>
      <label>
        Company
        <input name="company" required maxLength={160} placeholder="Your hauling company" />
      </label>
      <label>
        Contact name
        <input name="contactName" required maxLength={120} />
      </label>
      <div className="partner-form-row">
        <label>
          Work email
          <input name="email" type="email" required maxLength={200} />
        </label>
        <label>
          Phone
          <input name="phone" type="tel" maxLength={40} />
        </label>
      </div>
      <label>
        Cities you cover
        <input
          name="cities"
          required
          maxLength={400}
          defaultValue={cityDefault}
          placeholder="Nationwide, or Texas / Dallas / 50-mile radius…"
        />
      </label>
      <label>
        What you haul
        <input
          name="services"
          required
          maxLength={400}
          placeholder="Junk removal, appliances, mattresses, e-waste…"
        />
      </label>
      <label>
        Anything we should know
        <textarea
          name="notes"
          maxLength={1500}
          placeholder="License, service radius, how many jobs you want per week…"
        />
      </label>
      <button type="submit" className="btn-primary">
        Request partner access
      </button>
      <p className="lead-privacy">
        We’ll use this to evaluate a partnership — not to sell your contact to unrelated lists.{" "}
        <Link href="/privacy">Privacy</Link>
      </p>
      {status === "ok" ? (
        <p className="form-ok">Got it. We’ll email next steps and a sample lead format.</p>
      ) : null}
      {status === "err" ? <p className="form-err">Something went wrong. Try again.</p> : null}
    </form>
  );
}

export default function PartnersPage() {
  return (
    <div className="partner-page">
      <section className="partner-hero">
        <div className="shell partner-hero-inner">
          <p className="partner-brand">DumpRegistry Partners</p>
          <h1>Jobs from 300 cities — you set the coverage, not one metro.</h1>
          <p className="partner-hero-lead">
            People land on disposal guides nationwide. When they cannot self-haul, they request pickup with a
            ZIP. We email you the job if it falls in the area you listed — nationwide, a state, or a radius.
            Not a bidding war. Not “buy Rochester exclusive.”
          </p>
          <div className="partner-hero-actions">
            <a className="btn-primary" href="#apply">
              Apply with your coverage
            </a>
            <Link className="btn-secondary" href="/cities">
              See live cities
            </Link>
          </div>
        </div>
      </section>

      <section className="shell partner-section">
        <h2>How it works</h2>
        <ol className="partner-steps">
          <li>
            <strong>Someone needs haul-away</strong>
            <span>They get the free official answer first, then ask for a pickup quote with name, phone, and ZIP.</span>
          </li>
          <li>
            <strong>We match coverage, not a single city seat</strong>
            <span>
              If you listed nationwide, their state, or their city, you get the email. Write “nationwide” if you
              take jobs anywhere you can legally work.
            </span>
          </li>
          <li>
            <strong>You quote and keep the job</strong>
            <span>You call the customer, quote, and invoice them. No job commission.</span>
          </li>
        </ol>
      </section>

      <section className="shell partner-section">
        <h2>Plans</h2>
        <div className="partner-plans">
          <article>
            <h3>Network trial</h3>
            <p className="partner-price">10 free leads</p>
            <p>Your coverage area — nationwide, a state, or a list of metros. Prove job quality before you pay.</p>
          </article>
          <article>
            <h3>Coverage</h3>
            <p className="partner-price">Pay per lead</p>
            <p>Shared jobs anywhere you said you work. Pricing sent after you apply — not locked to one city.</p>
          </article>
          <article>
            <h3>Exclusive metro</h3>
            <p className="partner-price">Monthly + per lead</p>
            <p>Optional later, only where volume is real. Do not start here — clicks are spread across the country.</p>
          </article>
        </div>
      </section>

      <section className="shell partner-section partner-why">
        <h2>Why haulers use this</h2>
        <ul>
          <li>Leads come from people who already decided they need haul-away — mattress, bulky, C&amp;D, appliances.</li>
          <li>Coverage is yours: nationwide, a state, or named cities. We will not sit on Rochester-only seats.</li>
          <li>You keep the customer and the invoice. Apply once, onboard by email.</li>
        </ul>
      </section>

      <section className="shell partner-section" id="apply" aria-labelledby="apply-heading">
        <h2 id="apply-heading">Apply</h2>
        <p className="partner-apply-lead">
          Tell us where you actually take jobs. “Nationwide” is valid. We’ll email a sample lead format.
        </p>
        <Suspense fallback={<p>Loading form…</p>}>
          <PartnersForm />
        </Suspense>
      </section>
    </div>
  );
}
