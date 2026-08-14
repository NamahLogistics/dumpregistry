import { coverageIncludes } from "./coverage";
import { createLeadPackCheckout, emailTopUpCheckout, leadPackCredits } from "./dodo";
import { escapeHtml, sendEmail } from "./email";
import type { PartnerRow } from "./marketplace-schema";
import type { getSql } from "./db";

type Db = NonNullable<ReturnType<typeof getSql>>;

export async function grantLeadPack(
  db: Db,
  opts: { paymentId: string; partnerId: number; customerId?: string | null },
) {
  const credits = leadPackCredits();
  const inserted = await db`
    INSERT INTO dodo_payments (payment_id, partner_id, credits_granted)
    VALUES (${opts.paymentId}, ${opts.partnerId}, ${credits})
    ON CONFLICT (payment_id) DO NOTHING
    RETURNING id
  `;
  if (!inserted.length) return { duplicate: true as const, credits };
  await db`
    UPDATE partner_applications
    SET
      lead_credits = COALESCE(lead_credits, 0) + ${credits},
      status = 'active',
      dodo_customer_id = COALESCE(${opts.customerId ?? null}, dodo_customer_id)
    WHERE id = ${opts.partnerId}
  `;
  return { duplicate: false as const, credits };
}

export async function pickPartnerForZip(db: Db, zip: string): Promise<PartnerRow | null> {
  const rows = (await db`
    SELECT id, company, contact_name, email, phone, cities, services, notes, plan, status,
           shop_zip, coverage_zips, radius_miles, dodo_customer_id, lead_credits, leads_routed_count, created_at
    FROM partner_applications
    WHERE status = 'active' AND lead_credits > 0
    LIMIT 200
  `) as PartnerRow[];

  const eligible = rows.filter((p) => coverageIncludes(p.coverage_zips, zip));
  if (!eligible.length) return null;

  const counts = (await db`
    SELECT partner_id, COUNT(*)::int AS n
    FROM lead_requests
    WHERE partner_id IS NOT NULL AND routed_at > NOW() - INTERVAL '30 days'
    GROUP BY partner_id
  `) as Array<{ partner_id: number; n: number }>;
  const byId = new Map(counts.map((c) => [Number(c.partner_id), Number(c.n)]));

  eligible.sort((a, b) => {
    const diff = (byId.get(a.id) ?? 0) - (byId.get(b.id) ?? 0);
    if (diff !== 0) return diff;
    return a.id - b.id;
  });

  for (const candidate of eligible) {
    const claimed = (await db`
      UPDATE partner_applications
      SET lead_credits = lead_credits - 1,
          leads_routed_count = COALESCE(leads_routed_count, 0) + 1
      WHERE id = ${candidate.id} AND status = 'active' AND lead_credits > 0
      RETURNING id, company, contact_name, email, phone, cities, services, notes, plan, status,
                shop_zip, coverage_zips, radius_miles, dodo_customer_id, lead_credits, leads_routed_count, created_at
    `) as PartnerRow[];
    if (claimed.length) return claimed[0];
  }
  return null;
}

export async function maybePauseIfEmpty(db: Db, partner: PartnerRow) {
  if (Number(partner.lead_credits) > 0) return;
  await db`
    UPDATE partner_applications
    SET status = 'paused_payment'
    WHERE id = ${partner.id} AND lead_credits <= 0 AND status = 'active'
  `;
  await emailTopUpCheckout(partner);
}

export async function checkoutOrError(partner: Pick<PartnerRow, "id" | "email" | "contact_name" | "company">) {
  const checkout = await createLeadPackCheckout({
    partnerId: partner.id,
    email: partner.email,
    name: partner.contact_name || partner.company,
  });
  if (!checkout.ok) return checkout;
  await sendEmail({
    to: partner.email,
    subject: "DumpRegistry — complete payment to go live",
    html: `<p>Hi ${escapeHtml(partner.contact_name)},</p>
<p>Finish the 10-lead pack ($250) for <strong>${escapeHtml(partner.company)}</strong>. You go live automatically after Dodo confirms:</p>
<p><a href="${escapeHtml(checkout.checkoutUrl)}">Pay lead pack</a></p>`,
  });
  return checkout;
}
