"use client";

import { FormEvent, useState } from "react";

type Lead = {
  id: number;
  city: string;
  state: string;
  zip: string | null;
  item_slug: string | null;
  name: string;
  email: string;
  phone: string | null;
  notes: string | null;
  partner_id: number | null;
  status: string;
  created_at: string;
};

const STATUSES = ["new", "qualified", "routed", "unmatched", "closed", "spam"] as const;

export default function AdminLeadsPage() {
  const [token, setToken] = useState("");
  const [rows, setRows] = useState<Lead[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [note, setNote] = useState<string | null>(null);

  async function load(e?: FormEvent) {
    e?.preventDefault();
    setError(null);
    setNote(null);
    const res = await fetch("/api/admin/leads", {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    if (!res.ok) {
      setError(data.error ?? "Failed to load");
      return;
    }
    setRows(data.leads ?? []);
  }

  async function setStatus(id: number, status: string) {
    setError(null);
    setNote(null);
    const res = await fetch("/api/admin/leads", {
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
      <h1>Lead marketplace queue</h1>
      <p>
        Qualify pickup requests. Routing and billing are automatic (ZIP match + Dodo credits). Status here is
        an override only.
      </p>
      <form className="admin-auth" onSubmit={load}>
        <label>
          Admin token
          <input type="password" value={token} onChange={(e) => setToken(e.target.value)} required />
        </label>
        <button type="submit">Load leads</button>
      </form>
      {error ? <p className="form-err">{error}</p> : null}
      {note ? <p className="form-ok">{note}</p> : null}
      <ul className="admin-list">
        {rows.map((r) => (
          <li key={r.id}>
            <div>
              <strong>
                {r.city}, {r.state}
                {r.zip ? ` ${r.zip}` : ""}
                {r.item_slug ? ` · ${r.item_slug}` : ""}
                {r.partner_id ? ` · partner #${r.partner_id}` : ""}
              </strong>
              <span>
                {r.status} · {new Date(r.created_at).toLocaleString()}
              </span>
            </div>
            <p>
              {r.name} · {r.email}
              {r.phone ? ` · ${r.phone}` : ""}
            </p>
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
      {rows.length === 0 ? <p>No leads loaded.</p> : null}
    </main>
  );
}
