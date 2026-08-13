import type { Metadata } from "next";
import { pageMetadata } from "@/lib/seo";

export const metadata: Metadata = pageMetadata({
  title: "About DumpRegistry",
  description:
    "City-sourced disposal answers for mattresses, paint, TVs, and other hard-to-trash items — with official sources and verification dates.",
  path: "/about",
});

export default function AboutPage() {
  return (
    <article className="shell page prose">
      <h1>About DumpRegistry</h1>
      <p>
        DumpRegistry exists so a person standing next to a mattress, car battery, or can of paint can get a
        clear next step — not a maze of PDFs and conflicting forum posts.
      </p>
      <p>
        We are not a government agency. We compile publicly available guidance, cite sources, show when we
        last verified a fact, and invite corrections when cities change their rules.
      </p>
      <p>
        <strong>Who:</strong> editorial maintainers reviewing sourced rules.
        <br />
        <strong>How:</strong> a structured rules database plus human-readable templates — not mass-generated
        filler.
        <br />
        <strong>Why:</strong> to help people dispose of hard items correctly and avoid illegal dumping.
      </p>
    </article>
  );
}
