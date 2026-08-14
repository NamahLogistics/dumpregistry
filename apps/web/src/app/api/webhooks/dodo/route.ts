import { NextResponse } from "next/server";
import { createLeadPackCheckout, dodoClient, siteUrl } from "@/lib/dodo";
import { getSql } from "@/lib/db";
import { escapeHtml, sendEmail } from "@/lib/email";
import { ensureMarketplaceSchema } from "@/lib/marketplace-schema";
import { grantLeadPack } from "@/lib/partner-billing";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  const client = dodoClient();
  if (!client || !process.env.DODO_PAYMENTS_WEBHOOK_KEY) {
    return NextResponse.json({ error: "Dodo webhook is not configured" }, { status: 503 });
  }

  const rawBody = await req.text();
  let event: ReturnType<typeof client.webhooks.unwrap>;
  try {
    event = client.webhooks.unwrap(rawBody, {
      headers: {
        "webhook-id": req.headers.get("webhook-id") ?? "",
        "webhook-signature": req.headers.get("webhook-signature") ?? "",
        "webhook-timestamp": req.headers.get("webhook-timestamp") ?? "",
      },
    });
  } catch (err) {
    console.error("[dodo webhook] verify failed", err);
    return NextResponse.json({ error: "Invalid signature" }, { status: 401 });
  }

  const db = getSql();
  if (!db) return NextResponse.json({ error: "DATABASE_URL required" }, { status: 503 });
  await ensureMarketplaceSchema(db);

  if (event.type === "payment.succeeded") {
    const payment = event.data;
    const partnerId = Number(payment.metadata?.partner_id ?? 0);
    const paymentId = payment.payment_id;
    const customerId = payment.customer?.customer_id ?? null;

    let id = partnerId;
    if (!id && payment.customer?.email) {
      const found = await db`
        SELECT id FROM partner_applications
        WHERE email = ${payment.customer.email}
        ORDER BY created_at DESC
        LIMIT 1
      `;
      id = found.length ? Number(found[0].id) : 0;
    }
    if (!id) {
      console.error("[dodo webhook] payment.succeeded with no partner_id", paymentId);
      return NextResponse.json({ ok: true, skipped: true });
    }

    const result = await grantLeadPack(db, { paymentId, partnerId: id, customerId });
    if (!result.duplicate) {
      const row = await db`
        SELECT email, contact_name, company, lead_credits
        FROM partner_applications WHERE id = ${id} LIMIT 1
      `;
      if (row.length) {
        await sendEmail({
          to: String(row[0].email),
          subject: "You’re live on DumpRegistry leads",
          html: `<p>Hi ${escapeHtml(String(row[0].contact_name))},</p>
<p>Payment received. <strong>${escapeHtml(String(row[0].company))}</strong> now has ${row[0].lead_credits} prepaid leads. We email you a job only when the resident ZIP is in your coverage.</p>
<p><a href="${siteUrl()}/partners">Partners</a></p>`,
        });
      }
    }
    return NextResponse.json({ ok: true, duplicate: result.duplicate });
  }

  if (event.type === "payment.failed") {
    const payment = event.data;
    const partnerId = Number(payment.metadata?.partner_id ?? 0);
    if (partnerId) {
      const row = await db`
        SELECT id, email, contact_name, company FROM partner_applications WHERE id = ${partnerId} LIMIT 1
      `;
      if (row.length) {
        const checkout = await createLeadPackCheckout({
          partnerId,
          email: String(row[0].email),
          name: String(row[0].contact_name || row[0].company),
        });
        await sendEmail({
          to: String(row[0].email),
          subject: "DumpRegistry payment did not go through",
          html: `<p>Hi ${escapeHtml(String(row[0].contact_name))},</p>
<p>The lead-pack payment failed. You are not charged and you will not receive new jobs until a pack succeeds.</p>
${checkout.ok ? `<p><a href="${escapeHtml(checkout.checkoutUrl)}">Try payment again</a></p>` : ""}`,
        });
      }
    }
    return NextResponse.json({ ok: true });
  }

  return NextResponse.json({ ok: true, ignored: event.type });
}
