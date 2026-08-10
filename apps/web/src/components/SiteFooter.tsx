import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="shell footer-inner">
        <div>
          <strong>DumpRegistry</strong>
          <p>People-first disposal guidance. Not an official government website.</p>
        </div>
        <div className="footer-links">
          <Link href="/methodology">How we verify</Link>
          <Link href="/sources">Sources</Link>
          <Link href="/about">About</Link>
        </div>
      </div>
    </footer>
  );
}
