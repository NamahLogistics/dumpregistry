import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="shell footer-inner">
        <div className="footer-brand-block">
          <strong className="footer-brand">DumpRegistry</strong>
          <p>
            Independent reference for hard-to-trash items. We publish only city-sourced program guidance with
            named official sources — not statewide filler presented as local advice.
          </p>
          <p className="footer-disclaimer">
            DumpRegistry is <strong>not</strong> an official government website and is not affiliated with any
            city, county, or state agency. Always confirm fees, hours, and acceptance rules with the linked
            official program before you go.
          </p>
        </div>
        <div className="footer-cols">
          <div className="footer-links">
            <h2>Explore</h2>
            <Link href="/cities">Verified cities</Link>
            <Link href="/counties">County HHW</Link>
            <Link href="/materials">Materials</Link>
            <Link href="/centers">Drop-off centers</Link>
            <Link href="/guides">Guides</Link>
            <Link href="/methodology">Verification method</Link>
            <Link href="/sources">Official sources</Link>
            <Link href="/about">About</Link>
            <Link href="/privacy">Privacy</Link>
          </div>
          <div className="footer-links">
            <h2>Partners</h2>
            <Link href="/partners">Hauler partnerships</Link>
          </div>
        </div>
      </div>
      <div className="footer-bar">
        <div className="shell footer-bar-inner">
          <span>© {new Date().getFullYear()} DumpRegistry</span>
          <Link href="/privacy">Privacy</Link>
          <span>Last editorial standard: city-sourced · dated · actionable</span>
        </div>
      </div>
    </footer>
  );
}
