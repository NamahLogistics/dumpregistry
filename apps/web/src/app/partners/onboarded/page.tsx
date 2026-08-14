import type { Metadata } from "next";
import Link from "next/link";
import { pageMetadata } from "@/lib/seo";

export const metadata: Metadata = pageMetadata({
  title: "Partner onboarding — DumpRegistry",
  description: "Dodo payment return page. Partners go live when payment is confirmed, not when this page loads.",
  path: "/partners/onboarded",
});

export default function PartnerOnboardedPage() {
  return (
    <article className="shell page prose">
      <h1>Thanks — Dodo is confirming payment</h1>
      <p>
        This page does not activate your account. When Dodo confirms the 10-lead pack, we add 10 credits and
        email you. After that we send jobs whose ZIP is in the coverage you submitted.
      </p>
      <p>
        If you chose the trial instead, you are already live and this page is only a return URL.
      </p>
      <p>
        <Link href="/partners">Back to partners</Link>
      </p>
    </article>
  );
}
