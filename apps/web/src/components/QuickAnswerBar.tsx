"use client";

import { OfficialLink } from "@/components/OfficialViewer";

type Props = {
  badgeLabel: string;
  fee: string;
  curbside: boolean;
  facilityType: string;
  verifiedAt?: string | null;
  phone?: string | null;
  sourceUrl?: string | null;
};

export function QuickAnswerBar({
  badgeLabel,
  fee,
  curbside,
  facilityType,
  verifiedAt,
  phone,
  sourceUrl,
}: Props) {
  const tel = phone ? `tel:${phone.replace(/[^\d+]/g, "")}` : null;

  return (
    <div className="quick-bar" aria-label="Quick disposal facts">
      <div className="quick-fact">
        <span className="quick-label">Status</span>
        <strong>{badgeLabel}</strong>
      </div>
      <div className="quick-fact">
        <span className="quick-label">Curbside</span>
        <strong>{curbside ? "Possible / program" : "Drop-off / special"}</strong>
      </div>
      <div className="quick-fact">
        <span className="quick-label">Fee note</span>
        <strong>{fee || "See official source"}</strong>
      </div>
      <div className="quick-fact">
        <span className="quick-label">Pathway</span>
        <strong>{facilityType}</strong>
      </div>
      {verifiedAt ? (
        <div className="quick-fact">
          <span className="quick-label">Verified</span>
          <strong>{verifiedAt}</strong>
        </div>
      ) : null}
      <div className="quick-actions">
        {tel ? (
          <a className="quick-action" href={tel}>
            Call now
          </a>
        ) : null}
        {sourceUrl ? (
          <OfficialLink className="quick-action" url={sourceUrl} title="Official rules">
            Official rules
          </OfficialLink>
        ) : null}
        <a className="quick-action" href="#facilities-heading">
          Jump to map
        </a>
      </div>
    </div>
  );
}
