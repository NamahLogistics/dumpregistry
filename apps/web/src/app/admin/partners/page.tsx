"use client";

import { FormEvent, useState } from "react";

type Partner = {
  id: number;
  company: string;
  contact_name: string;
  email: string;
  phone: string | null;
  cities: string;
  services: string;
  notes: string | null;
  plan: string | null;
  status: string;
  shop_zip: string | null;
  coverage_zips: unknown;
  radius_miles: number | null;
  dodo_customer_id: string | null;
  lead_credits: number | null;
  leads_routed_count: number | null;
  created_at: string;
};

const STATUSES = ["active", "paused", "paused_payment", "rejected"] as const;

function zipCount(coverage: unknown) {
  if (Array.isArray(coverage)) return coverage.length;
  return 0;
}

export default function AdminPartnersPage() {
  const [token, setToken] = useState("");
  const [rows, setRows] = useState<Partner[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [note, setNote] = useState<string | null>(null);

  async function load(e?: FormEvent) {
    e?.preventDefault();
    setError(null);
    setNote(null);
    const res = await fetch("/api/admin/partners", {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    if (!res.ok) {
      setError(data.error ?? "Failed to load");
      return;
    }
    setRows(data.partners ?? []);
  }

  async function setStatus(id: number, status: string) {
    setError(null);
    setNote(null);
    const res = await fetch("/api/admin/partners", {
      method: "PATCH",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ id, status }),
    });
    const data = await res.json();
    if (!res.ok) {
      setError(data.error ?? "Update failed");
      return;
    }
    setNote(data.note ?? "Saved");
    await load();
  }

  return (
    <main className="admin-review">
      <h1>Partners</h1>
      <p>
        Emergency pause or reject only. Haulers go live from the partners form (trial) or Dodo payment — do not
        use this page to onboard.
      </p>
      <form className="admin-auth" onSubmit={load}>
        <label>
          Admin token
          <input type="password" value={token} onChange={(e) => setToken(e.target.value)} required />
        </label>
        <button type="submit">Load partners</button>
      </form>
      {error ? <p className="form-err">{error}</p> : null}
      {note ? <p className="form-ok">{note}</p> : null}
      <ul className="admin-list">
        {rows.map((r) => (
          <li key={r.id}>
            <div>
              <strong>
                {r.company} · {r.plan ?? "trial"} · {r.status}
              </strong>
              <span>{new Date(r.created_at).toLocaleString()}</span>
            </div>
            <p>
              {r.contact_name} · {r.email}
              {r.phone ? ` · ${r.phone}` : ""}
            </p>
            <p>
              Credits: {r.lead_credits ?? 0} · routed: {r.leads_routed_count ?? 0} · ZIPs: {zipCount(r.coverage_zips)}
              {r.shop_zip ? ` · shop ${r.shop_zip}` : ""}
              {r.radius_miles ? ` · ${r.radius_miles} mi` : ""}
            </p>
            <p>{r.cities}</p>
            {r.dodo_customer_id ? <p>Dodo customer: {r.dodo_customer_id}</p> : null}
            <p>Services: {r.services}</p>
            {r.notes ? <p>{r.notes}</p> : null}
            <div className="admin-actions">
              {STATUSES.map((s) => (
                <button key={s} type="button" onClick={() => setStatus(r.id, s)} disabled={r.status === s}>
                  {s}
                </button>
              ))}
            </div>
          </li>
        ))}
      </ul>
      {rows.length === 0 ? <p>No partners loaded.</p> : null}
    </main>
  );
}
