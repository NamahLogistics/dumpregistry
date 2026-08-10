"use client";

import { useState } from "react";
import { OfficialLink } from "@/components/OfficialViewer";

export function DoThisNow({
  steps,
  sourceUrl,
  sourceName,
  phone,
}: {
  steps: string[];
  sourceUrl?: string | null;
  sourceName?: string | null;
  phone?: string | null;
}) {
  const [done, setDone] = useState<Record<number, boolean>>({});
  const tel = phone ? `tel:${phone.replace(/[^\d+]/g, "")}` : null;
  const completed = Object.values(done).filter(Boolean).length;

  return (
    <section className="do-now" aria-labelledby="do-now-heading">
      <div className="do-now-head">
        <h2 id="do-now-heading">Do this today</h2>
        {steps.length > 0 ? (
          <span className="do-now-progress">
            {completed}/{steps.length} done
          </span>
        ) : null}
      </div>
      <p className="do-now-lead">
        Check off each step as you go. Stay on this page for the map, phone, and official program links.
      </p>
      <ol className="do-now-steps">
        {steps.map((step, i) => (
          <li key={step}>
            <label className={done[i] ? "step-done" : undefined}>
              <input
                type="checkbox"
                checked={Boolean(done[i])}
                onChange={() => setDone((prev) => ({ ...prev, [i]: !prev[i] }))}
              />
              <span>{step}</span>
            </label>
          </li>
        ))}
      </ol>
      <div className="do-now-actions">
        {tel ? (
          <a className="btn-primary" href={tel}>
            Call facility
          </a>
        ) : null}
        {sourceUrl ? (
          <OfficialLink className="btn-secondary" url={sourceUrl} title={sourceName}>
            {sourceName
              ? `View ${sourceName.length > 42 ? "official source" : sourceName}`
              : "View official source"}
          </OfficialLink>
        ) : null}
      </div>
    </section>
  );
}
