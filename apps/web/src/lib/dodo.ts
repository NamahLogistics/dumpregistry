import DodoPayments from "dodopayments";
import { escapeHtml, sendEmail } from "./email";
import type { PartnerRow } from "./marketplace-schema";

export const TRIAL_CREDITS = 10;

export function leadPackCredits() {
  const n = Number(process.env.LEAD_PACK_CREDITS ?? 10);
  return Number.isFinite(n) && n > 0 ? Math.floor(n) : 10;
}

export function dodoConfigured() {
  return Boolean(process.env.DODO_PAYMENTS_API_KEY && process.env.DODO_PRODUCT_ID_LEAD_PACK);
}

export function siteUrl() {
  return process.env.NEXT_PUBLIC_SITE_URL ?? "https://www.dumpregistry.org";
}

export function dodoClient() {
  const key = process.env.DODO_PAYMENTS_API_KEY;
  if (!key) return null;
  const environment = process.env.DODO_PAYMENTS_ENVIRONMENT === "live_mode" ? "live_mode" : "test_mode";
  return new DodoPayments({
    bearerToken: key,
    environment,
    webhookKey: process.env.DODO_PAYMENTS_WEBHOOK_KEY,
  });
}

export async function createLeadPackCheckout(opts: {
  partnerId: number;
  email: string;
  name: string;
}): Promise<{ ok: true; checkoutUrl: string } | { ok: false; error: string }> {
  const client = dodoClient();
  const productId = process.env.DODO_PRODUCT_ID_LEAD_PACK;
  if (!client || !productId) {
    return { ok: false, error: "Dodo checkout is not configured" };
  }
  const session = await client.checkoutSessions.create({
    product_cart: [{ product_id: productId, quantity: 1 }],
    customer: { email: opts.email, name: opts.name },
    return_url: `${siteUrl()}/partners/onboarded`,
    metadata: { partner_id: String(opts.partnerId) },
  });
  const url = session.checkout_url;
  if (!url) return { ok: false, error: "Dodo did not return a checkout URL" };
  return { ok: true, checkoutUrl: url };
}

export async function emailTopUpCheckout(partner: Pick<PartnerRow, "email" | "contact_name" | "company" | "id">) {
  const checkout = await createLeadPackCheckout({
    partnerId: partner.id,
    email: partner.email,
    name: partner.contact_name || partner.company,
  });
  if (!checkout.ok) {
    console.error("[dodo] top-up checkout failed", checkout.error);
    await sendEmail({
      to: partner.email,
      subject: "DumpRegistry — add a lead pack to keep receiving jobs",
      html: `<p>Hi ${escapeHtml(partner.contact_name)},</p>
<p>Your prepaid lead credits for <strong>${escapeHtml(partner.company)}</strong> are at zero. Reply to this email after Dodo checkout is available, or apply again from <a href="${siteUrl()}/partners">${siteUrl()}/partners</a>.</p>`,
    });
    return checkout;
  }
  await sendEmail({
    to: partner.email,
    subject: "DumpRegistry — buy another 10-lead pack",
    html: `<p>Hi ${escapeHtml(partner.contact_name)},</p>
<p>Your prepaid credits for <strong>${escapeHtml(partner.company)}</strong> are at zero, so we paused new jobs.</p>
<p>Pay the 10-lead pack ($250) and you go live again automatically:</p>
<p><a href="${escapeHtml(checkout.checkoutUrl)}">Pay lead pack</a></p>`,
    text: `Your DumpRegistry lead credits are at zero. Pay the 10-lead pack: ${checkout.checkoutUrl}\n`,
  });
  return checkout;
}
