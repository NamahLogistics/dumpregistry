"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { trackEvent } from "@/lib/analytics";

function PartnersForm() {
  const [status, setStatus] = useState<"idle" | "ok" | "err">("idle");
  const [message, setMessage] = useState<string | null>(null);

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
        services: fd.get("services"),
        notes: fd.get("notes"),
        plan: fd.get("plan"),
        shopZip: fd.get("shopZip"),
        coverageZips: fd.get("coverageZips"),
        radiusMiles: fd.get("radiusMiles"),
        attest: fd.get("attest") === "on",
      }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      setStatus("err");
      setMessage(typeof data.error === "string" ? data.error : "Something went wrong.");
      return;
    }
    trackEvent("generate_lead", {
      lead_type: "partner",
      plan: String(fd.get("plan") ?? ""),
    });
    if (typeof data.checkoutUrl === "string" && data.checkoutUrl) {
      window.location.href = data.checkoutUrl;
      return;
    }
    setStatus("ok");
    setMessage(
      data.status === "pending_payment"
        ? (data.error ?? "Coverage saved. We’ll email a Dodo pay link when checkout is configured.")
        : `You’re live for ${data.zipCount ?? "your"} ZIPs with 10 trial leads.`,
    );
    e.currentTarget.reset();
  }

  return (
    <form className="partner-form" onSubmit={submit}>
      <label>
        Start with
        <select name="plan" defaultValue="trial" required>
          <option value="trial">Network trial — 10 free leads in my ZIP coverage</option>
          <option value="pack">Pay now — 10-lead pack ($250) via Dodo</option>
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
        Shop ZIP
        <input
          name="shopZip"
          required
          inputMode="numeric"
          pattern="[0-9]{5}"
          maxLength={10}
          placeholder="14604"
        />
      </label>
      <div className="partner-form-row">
        <label>
          Radius from shop (miles)
          <input
            name="radiusMiles"
            type="number"
            min={1}
            max={150}
            placeholder="Optional, max 150"
          />
        </label>
        <label>
          Extra ZIPs
          <input name="coverageZips" maxLength={2000} placeholder="Optional: 14604, 14620…" />
        </label>
      </div>
      <p className="partner-coverage-hint">
        We expand a radius into real US ZIPs and only send jobs whose ZIP is in that set. Shop ZIP is always
        included. Max radius 150 miles.
      </p>
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
        <textarea name="notes" maxLength={1500} placeholder="License, crew size, items you refuse…" />
      </label>
      <label className="partner-attest">
        <input name="attest" type="checkbox" required />
        <span>
          I legally serve these ZIPs and will quote jobs we send there. DumpRegistry does not check junk
          licenses; coverage is the ZIP set I submit.
        </span>
      </label>
      <button type="submit" className="btn-primary">
        Go live
      </button>
      <p className="lead-privacy">
        Trial starts immediately. Paid packs activate when Dodo confirms payment — no admin step.{" "}
        <Link href="/privacy">Privacy</Link>
      </p>
      {status === "ok" ? <p className="form-ok">{message}</p> : null}
      {status === "err" ? <p className="form-err">{message ?? "Something went wrong. Try again."}</p> : null}
    </form>
  );
}

export default function PartnersPage() {
  return (
    <div className="partner-page">
      <section className="partner-hero">
        <div className="shell partner-hero-inner">
          <p className="partner-brand">DumpRegistry Partners</p>
          <h1>Jobs in the ZIPs you serve — prepaid, one hauler per request.</h1>
          <p className="partner-hero-lead">
            Residents ask for pickup with a ZIP. We match that ZIP to your coverage, email you the job, and
            subtract one prepaid credit. Not a bid war. Not a nationwide blast.
          </p>
          <div className="partner-hero-actions">
            <a className="btn-primary" href="#apply">
              Set coverage and go live
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
            <strong>You declare a service area</strong>
            <span>Shop ZIP plus a radius and/or a ZIP list. We store the ZIP set. That is how we know you serve the area.</span>
          </li>
          <li>
            <strong>Someone requests haul-away</strong>
            <span>They get the free official answer first, then a pickup form with name, phone, and ZIP.</span>
          </li>
          <li>
            <strong>One matching hauler gets the job</strong>
            <span>
              If your ZIP set includes theirs and you have credits, you get the email. You quote and invoice the
              customer. After trial, a 10-lead pack is $250 on Dodo — paid packs refill automatically.
            </span>
          </li>
        </ol>
      </section>

      <section className="shell partner-section">
        <h2>Plans</h2>
        <div className="partner-plans">
          <article>
            <h3>Network trial</h3>
            <p className="partner-price">10 free leads</p>
            <p>Live as soon as you submit coverage. No admin activation.</p>
          </article>
          <article>
            <h3>Lead pack</h3>
            <p className="partner-price">$250 / 10 leads</p>
            <p>Prepaid on Dodo. When credits hit zero we email a new checkout. You go live again on payment.</p>
          </article>
          <article>
            <h3>Exclusive metro</h3>
            <p className="partner-price">Later</p>
            <p>Not in this desk. Shared coverage uses fair rotation among haulers who listed that ZIP.</p>
          </article>
        </div>
      </section>

      <section className="shell partner-section partner-why">
        <h2>Why this is automated</h2>
        <ul>
          <li>Coverage is a ZIP set, not a city-name guess. Unknown ZIPs stay unmatched.</li>
          <li>One hauler per request. You keep the customer invoice.</li>
          <li>Fees are prepaid Dodo packs. No one invoices you by hand.</li>
        </ul>
      </section>

      <section className="shell partner-section" id="apply" aria-labelledby="apply-heading">
        <h2 id="apply-heading">Go live</h2>
        <p className="partner-apply-lead">
          Shop ZIP is required. Add a radius or extra ZIPs so we can match real pickup requests.
        </p>
        <PartnersForm />
      </section>
    </div>
  );
}
