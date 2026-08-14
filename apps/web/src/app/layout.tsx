import type { Metadata } from "next";
import { Merriweather, Source_Sans_3 } from "next/font/google";
import { Analytics } from "@/components/Analytics";
import { OfficialViewerProvider } from "@/components/OfficialViewer";
import { ADSENSE_PUB, adsenseClient } from "@/lib/ads";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { site } from "@/lib/site";
import "./globals.css";

const display = Merriweather({
  variable: "--font-display",
  subsets: ["latin"],
  weight: ["700", "900"],
});

const body = Source_Sans_3({
  variable: "--font-body",
  subsets: ["latin"],
  weight: ["400", "600", "700"],
});

const gscVerification = process.env.NEXT_PUBLIC_GSC_VERIFICATION?.trim();

export const metadata: Metadata = {
  metadataBase: new URL(site.url),
  title: {
    default: `${site.name} — ${site.tagline}`,
    template: "%s",
  },
  description: site.description,
  alternates: {
    canonical: site.url,
  },
  openGraph: {
    siteName: site.name,
    type: "website",
    images: [{ url: site.ogImage, width: 1200, height: 630, alt: site.name }],
  },
  twitter: {
    card: "summary_large_image",
    images: [site.ogImage],
  },
  verification: gscVerification
    ? {
        google: gscVerification,
      }
    : undefined,
  other: {
    "google-adsense-account": adsenseClient() ?? ADSENSE_PUB,
  },
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  const orgJsonLd = {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: site.name,
    url: site.url,
    description: site.description,
  };
  const siteJsonLd = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: site.name,
    url: site.url,
    potentialAction: {
      "@type": "SearchAction",
      target: {
        "@type": "EntryPoint",
        urlTemplate: `${site.url}/centers?material={search_term_string}`,
      },
      "query-input": "required name=search_term_string",
    },
  };

  return (
    <html lang="en" className={`${display.variable} ${body.variable} h-full`}>
      <head>
        <script
          async
          src={`https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${adsenseClient() ?? ADSENSE_PUB}`}
          crossOrigin="anonymous"
        />
      </head>
      <body className="min-h-full flex flex-col antialiased">
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(orgJsonLd) }}
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(siteJsonLd) }}
        />
        <OfficialViewerProvider>
          <SiteHeader />
          <main className="flex-1">{children}</main>
          <SiteFooter />
        </OfficialViewerProvider>
        <Analytics />
      </body>
    </html>
  );
}
