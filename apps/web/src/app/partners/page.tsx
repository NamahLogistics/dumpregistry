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
          <option value="pilot">Pilot — 10 free leads in one city</option>
          <option value="starter">Starter — pay per shared lead</option>
          <option value="exclusive">Exclusive — sole partner in a city</option>
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
          placeholder="Houston, Dallas, Austin…"
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
          <h1>Pickup leads from people already trying to dispose of something.</h1>
          <p className="partner-hero-lead">
            Residents land on city disposal guides. When they cannot self-haul, they request pickup. Those
            requests go to local haulers — not a marketplace bidding war.
          </p>
          <div className="partner-hero-actions">
            <a className="btn-primary" href="#apply">
              Apply for your cities
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
            <strong>Someone needs help</strong>
            <span>They finish the free disposal answer, then ask for pickup options on that page.</span>
          </li>
          <li>
            <strong>We match by city</strong>
            <span>Active partners covering that city get the request by email.</span>
          </li>
          <li>
            <strong>You close the job</strong>
            <span>You contact the customer, quote, and invoice them directly. No job commission.</span>
          </li>
        </ol>
      </section>

      <section className="shell partner-section">
        <h2>Plans</h2>
        <div className="partner-plans">
          <article>
            <h3>Pilot</h3>
            <p className="partner-price">10 free leads</p>
            <p>One city while we prove match quality. Best if you want to test volume before paying.</p>
          </article>
          <article>
            <h3>Starter</h3>
            <p className="partner-price">Pay per lead</p>
            <p>Shared city coverage. Pricing depends on city and item — sent after you apply.</p>
          </article>
          <article>
            <h3>Exclusive</h3>
            <p className="partner-price">Monthly + per lead</p>
            <p>Sole partner in a city. Limited seats — apply with the metros you can actually cover.</p>
          </article>
        </div>
      </section>

      <section className="shell partner-section partner-why">
        <h2>Why haulers use this</h2>
        <ul>
          <li>Leads come from people who already decided they need disposal help in a specific city.</li>
          <li>No cold call required to join — apply once, onboard by email.</li>
          <li>You keep the customer relationship and the invoice.</li>
        </ul>
      </section>

      <section className="shell partner-section" id="apply" aria-labelledby="apply-heading">
        <h2 id="apply-heading">Apply</h2>
        <p className="partner-apply-lead">Tell us where you work. We’ll reply with onboarding and sample lead format.</p>
        <Suspense fallback={<p>Loading form…</p>}>
          <PartnersForm />
        </Suspense>
      </section>
    </div>
  );
}
