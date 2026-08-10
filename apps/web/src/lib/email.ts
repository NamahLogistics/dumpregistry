import { Resend } from "resend";

function client() {
  const key = process.env.RESEND_API_KEY;
  if (!key) return null;
  return new Resend(key);
}

function fromAddress() {
  return process.env.EMAIL_FROM ?? "DumpRegistry <onboarding@resend.dev>";
}

export function opsInbox() {
  return process.env.OPS_EMAIL ?? process.env.LEADS_NOTIFY_EMAIL ?? null;
}

export async function sendEmail(opts: {
  to: string | string[];
  subject: string;
  html: string;
  text?: string;
  replyTo?: string;
}) {
  const resend = client();
  if (!resend) {
    console.warn("[email] RESEND_API_KEY missing — skipped send:", opts.subject);
    return { ok: false as const, skipped: true as const };
  }
  const { error } = await resend.emails.send({
    from: fromAddress(),
    to: opts.to,
    subject: opts.subject,
    html: opts.html,
    text: opts.text,
    replyTo: opts.replyTo,
  });
  if (error) {
    console.error("[email] Resend error:", error);
    return { ok: false as const, skipped: false as const, error };
  }
  return { ok: true as const, skipped: false as const };
}

export function escapeHtml(value: string) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}
