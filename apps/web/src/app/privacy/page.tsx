import type { Metadata } from "next";
import Link from "next/link";
import { pageMetadata } from "@/lib/seo";
import { site } from "@/lib/site";

export const metadata: Metadata = pageMetadata({
  title: "Privacy — DumpRegistry",
  description:
    "How DumpRegistry handles information you submit on pickup requests, partner applications, and corrections. Reading disposal answers does not require an account.",
  path: "/privacy",
});

export default function PrivacyPage() {
  return (
    <article className="shell page prose">
      <h1>Privacy</h1>
      <p>
        DumpRegistry publishes free, city-sourced disposal guidance. You can read that guidance without creating
        an account or giving us a name, email, or phone number.
      </p>
      <p>Last updated: August 14, 2026.</p>

      <h2>What we collect when you choose to submit</h2>
      <p>
        <strong>Pickup requests</strong> (optional form on city item and material pages): name, email, phone,
        ZIP, city and state, the item, and any notes you write.
      </p>
      <p>
        <strong>Hauler partner applications</strong> on <Link href="/partners">/partners</Link>: company name,
        contact name, work email, phone if you provide one, shop ZIP, coverage ZIPs and/or radius, services, plan,
        and an attestation that you serve that area.
      </p>
      <p>
        <strong>Corrections</strong> (“Did this city change their rules?”): the message, an official source URL,
        and an email only if you add one.
      </p>
      <p>
        We store those submissions in our database (or a fallback file if the database is unavailable) and may
        email a copy to our operations inbox and a confirmation to the address you gave.
      </p>

      <h2>Pickup requests and local haulers</h2>
      <p>
        A pickup request is optional and separate from the free disposal answer on the same page. If you submit
        one, we match your ZIP to haulers who listed that ZIP in their coverage. We send the request to at most
        one matched hauler who has prepaid credits (or trial credits) so they can contact you about a quote. That
        share can include your name, email, phone, ZIP, item, city, and notes.
      </p>
      <p>
        If no hauler covers your ZIP, we store the request and do not send it. We do not blast your details to
        every partner, bulk lead networks, or unrelated advertisers. A hauler who receives a request invoices you
        directly; DumpRegistry is not the hauler. Haulers pay DumpRegistry separately for prepaid lead packs via
        Dodo Payments.
      </p>

      <h2>Analytics and hosting</h2>
      <p>
        The site is hosted on Vercel. Pages may be logged at the host (IP address, user agent, URL) as part of
        running the service. We use Vercel Analytics and, when configured, Google Analytics 4 with IP
        anonymization to see aggregate traffic — not to identify you as a person. These tools may set cookies or
        similar storage.
      </p>

      <h2>Advertising</h2>
      <p>
        We use Google AdSense to show third-party ads. Google and its partners may use cookies or similar
        storage to serve and measure those ads. See{" "}
        <a href="https://policies.google.com/technologies/ads">Google’s advertising privacy</a>. Who is
        authorized to sell ads on this domain is listed in{" "}
        <a href="https://www.dumpregistry.org/ads.txt">ads.txt</a>.
      </p>
      <p>Pickup and partner form fields are not sent to AdSense and are not used to build ad audiences.</p>

      <h2>What we do not do</h2>
      <ul>
        <li>We do not require an account to read disposal answers.</li>
        <li>We do not sell personal information to data brokers.</li>
        <li>We do not use pickup or partner form data to build advertising audiences.</li>
      </ul>

      <h2>How long we keep it</h2>
      <p>
        We keep submissions while we need them to route a request, operate a partnership, review a correction, or
        handle a dispute — then we delete or minimize them when they are no longer needed, or sooner if you ask
        us to delete them and we have no legal reason to keep a record.
      </p>

      <h2>Your requests</h2>
      <p>
        To access or delete information you submitted, email{" "}
        <a href={`mailto:${site.privacyEmail}`}>{site.privacyEmail}</a>
        . If we already emailed you a pickup or partner confirmation, you can reply to that message instead.
        Say which email address you used on the form.
      </p>
      <p>
        If you are in a place with a “do not sell or share” right: we do not sell your information to data
        brokers. Sharing a pickup request with the one matched hauler for your ZIP is the service that form
        provides. Email the same address if you want us to stop sharing a request that has not already been
        sent.
      </p>

      <h2>Children</h2>
      <p>DumpRegistry is not directed at children under 13, and we do not knowingly collect information from them.</p>

      <h2>Changes</h2>
      <p>If this policy changes in a material way, we will update the date at the top of this page.</p>

      <h2>Contact</h2>
      <p>
        DumpRegistry — independent public information, not a government agency. Privacy:{" "}
        <a href={`mailto:${site.privacyEmail}`}>{site.privacyEmail}</a>.{" "}
        <Link href="/about">About the site</Link>.
      </p>
    </article>
  );
}
