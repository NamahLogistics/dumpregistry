"use client";

import { FormEvent, useState } from "react";

type Submission = {
  id: number;
  state_slug: string;
  city_slug: string;
  item_slug: string | null;
  message: string;
  source_url: string | null;
  email: string | null;
  status: string;
  created_at: string;
};

export default function AdminReviewPage() {
  const [token, setToken] = useState("");
  const [rows, setRows] = useState<Submission[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [note, setNote] = useState<string | null>(null);

  async function load(e?: FormEvent) {
    e?.preventDefault();
    setError(null);
    setNote(null);
    const res = await fetch("/api/admin/submissions", {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    if (!res.ok) {
      setError(data.error ?? "Failed to load");
      return;
    }
    setRows(data.submissions ?? []);
  }

  async function setStatus(id: number, status: "approved" | "rejected" | "needs_more_info") {
    setError(null);
    setNote(null);
    const res = await fetch("/api/admin/submissions", {
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
      <h1>Submission review queue</h1>
      <p>
        Crowdsourced corrections stay pending until an editor verifies an official source. Approving
        never auto-publishes guides — it only marks the submission for manual rule updates.
      </p>
      <form className="admin-auth" onSubmit={load}>
        <label>
          Admin token
          <input
            type="password"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            autoComplete="off"
            required
          />
        </label>
        <button type="submit">Load pending</button>
      </form>
      {error ? <p className="form-err">{error}</p> : null}
      {note ? <p className="form-ok">{note}</p> : null}
      <ul className="admin-list">
        {rows.map((r) => (
          <li key={r.id}>
            <div>
              <strong>
                {r.city_slug}
                {r.item_slug ? ` / ${r.item_slug}` : ""}
              </strong>
              <span>{new Date(r.created_at).toLocaleString()}</span>
            </div>
            <p>{r.message}</p>
            {r.source_url ? (
              <a href={r.source_url} target="_blank" rel="noopener noreferrer">
                {r.source_url}
              </a>
            ) : (
              <em>Missing source_url — cannot approve</em>
            )}
            <div className="admin-actions">
              <button type="button" onClick={() => setStatus(r.id, "approved")} disabled={!r.source_url}>
                Approve for manual edit
              </button>
              <button type="button" onClick={() => setStatus(r.id, "needs_more_info")}>
                Needs more info
              </button>
              <button type="button" onClick={() => setStatus(r.id, "rejected")}>
                Reject
              </button>
            </div>
          </li>
        ))}
      </ul>
      {rows.length === 0 ? <p>No pending submissions loaded.</p> : null}
    </main>
  );
}
