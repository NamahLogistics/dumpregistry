import Link from "next/link";

export function SiteHeader() {
  return (
    <header className="site-header">
      <div className="official-banner" role="region" aria-label="Site status">
        <div className="shell official-banner-inner">
          <span className="official-banner-flag" aria-hidden="true" />
          <p>
            <strong>Independent public information service.</strong> Not a government website.
            Disposal guidance is researched from official city program sources and dated when verified.
          </p>
        </div>
      </div>
      <div className="site-header-main">
        <div className="shell header-inner">
          <Link href="/" className="brand">
            <span className="brand-mark" aria-hidden="true">
              DR
            </span>
            <span className="brand-text">
              <span className="brand-name">DumpRegistry</span>
              <span className="brand-tag">City-sourced disposal guidance</span>
            </span>
          </Link>
          <nav className="nav" aria-label="Primary">
            <Link href="/cities">Cities</Link>
            <Link href="/methodology">How we verify</Link>
            <Link href="/sources">Sources</Link>
            <Link href="/about">About</Link>
            <Link href="/partners">For haulers</Link>
          </nav>
        </div>
      </div>
    </header>
  );
}
