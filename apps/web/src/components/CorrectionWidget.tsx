"use client";

import { useState } from "react";

export function CorrectionWidget({
  city,
  stateSlug,
  citySlug,
  itemSlug,
}: {
  city: string;
  stateSlug: string;
  citySlug: string;
  itemSlug?: string;
}) {
  const [open, setOpen] = useState(false);
  const [status, setStatus] = useState<"idle" | "ok" | "err">("idle");
  const [message, setMessage] = useState("");
  const [sourceUrl, setSourceUrl] = useState("");
  const [email, setEmail] = useState("");

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setStatus("idle");
    const res = await fetch("/api/updates", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        stateSlug,
        citySlug,
        itemSlug,
        message,
        sourceUrl,
        email,
      }),
    });
    if (res.ok) {
      setStatus("ok");
      setMessage("");
      setSourceUrl("");
    } else {
      setStatus("err");
    }
  }

  return (
    <div className="correction-widget">
      <button type="button" className="correction-toggle" onClick={() => setOpen((v) => !v)}>
        Did {city} change their recycling rules? Update data here
      </button>
      {open ? (
        <form className="correction-form" onSubmit={submit}>
          <label>
            <span>What changed?</span>
            <textarea
              required
              minLength={20}
              maxLength={2000}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Describe the rule change and who it applies to."
            />
          </label>
          <label>
            <span>Official source URL (.gov preferred)</span>
            <input
              type="url"
              required
              value={sourceUrl}
              onChange={(e) => setSourceUrl(e.target.value)}
              placeholder="https://…"
            />
          </label>
          <label>
            <span>Email (optional)</span>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
          </label>
          <button type="submit" className="btn-secondary">
            Submit for review
          </button>
          {status === "ok" ? <p className="form-ok">Thanks — queued for editorial review.</p> : null}
          {status === "err" ? <p className="form-err">Could not submit. Check the URL and try again.</p> : null}
        </form>
      ) : null}
    </div>
  );
}
