import Link from "next/link";

export function SiteHeader() {
  return (
    <header className="site-header">
      <div className="shell header-inner">
        <Link href="/" className="brand">
          DumpRegistry
        </Link>
        <nav className="nav" aria-label="Primary">
          <Link href="/california">California</Link>
          <Link href="/methodology">Methodology</Link>
          <Link href="/sources">Sources</Link>
          <Link href="/about">About</Link>
        </nav>
      </div>
    </header>
  );
}
