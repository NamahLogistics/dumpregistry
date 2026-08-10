import { NextRequest, NextResponse } from "next/server";
import { isIP } from "node:net";

export const runtime = "nodejs";

const MAX_BYTES = 1_500_000;

function isPrivateHostname(hostname: string): boolean {
  const host = hostname.toLowerCase();
  if (
    host === "localhost" ||
    host.endsWith(".localhost") ||
    host.endsWith(".local") ||
    host.endsWith(".internal")
  ) {
    return true;
  }
  if (!isIP(host)) return false;
  if (host === "0.0.0.0" || host === "127.0.0.1" || host === "::1") return true;
  if (host.startsWith("10.") || host.startsWith("192.168.") || host.startsWith("169.254.")) return true;
  if (/^172\.(1[6-9]|2\d|3[0-1])\./.test(host)) return true;
  return false;
}

function allowedUrl(raw: string): URL | null {
  let u: URL;
  try {
    u = new URL(raw);
  } catch {
    return null;
  }
  if (u.protocol !== "http:" && u.protocol !== "https:") return null;
  if (u.username || u.password) return null;
  if (isPrivateHostname(u.hostname)) return null;
  return u;
}

function injectViewerShell(html: string, baseHref: string, originalUrl: string): string {
  const baseTag = `<base href="${baseHref.replace(/"/g, "&quot;")}">`;
  const guard = `<script>(function(){try{Object.defineProperty(window,"top",{get:function(){return window.self}});}catch(e){}})();</script>`;
  const banner = `<div style="position:sticky;top:0;z-index:99999;padding:8px 12px;font:650 13px/1.3 system-ui,sans-serif;background:#1f4d3a;color:#fff8f2">Official page preview inside DumpRegistry · <a href="${originalUrl.replace(/"/g, "&quot;")}" target="_blank" rel="noopener noreferrer" style="color:#fff8f2">original URL</a></div>`;

  let out = html;
  out = out.replace(/<meta[^>]+http-equiv=["']Content-Security-Policy["'][^>]*>/gi, "");
  out = out.replace(/<meta[^>]+http-equiv=["']X-Frame-Options["'][^>]*>/gi, "");
  if (/<head[^>]*>/i.test(out)) {
    out = out.replace(/<head[^>]*>/i, (m) => `${m}${baseTag}${guard}`);
  } else {
    out = `${baseTag}${guard}${out}`;
  }
  if (/<body[^>]*>/i.test(out)) {
    out = out.replace(/<body[^>]*>/i, (m) => `${m}${banner}`);
  }
  return out;
}

export async function GET(req: NextRequest) {
  const raw = req.nextUrl.searchParams.get("url");
  if (!raw) {
    return NextResponse.json({ error: "Missing url" }, { status: 400 });
  }
  const target = allowedUrl(raw);
  if (!target) {
    return NextResponse.json({ error: "URL not allowed" }, { status: 400 });
  }

  try {
    const upstream = await fetch(target.toString(), {
      redirect: "follow",
      headers: {
        Accept: "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
        "User-Agent":
          "DumpRegistryOfficialPreview/1.0 (+https://www.dumpregistry.org; public disposal guidance)",
      },
      signal: AbortSignal.timeout(12000),
      cache: "no-store",
    });

    const finalUrl = new URL(upstream.url);
    if (isPrivateHostname(finalUrl.hostname)) {
      return NextResponse.json({ error: "Redirect blocked" }, { status: 400 });
    }

    const contentType = upstream.headers.get("content-type") || "";
    if (!contentType.includes("text/html") && !contentType.includes("application/xhtml")) {
      return new NextResponse(
        `<!doctype html><html><body style="font-family:system-ui;padding:1.5rem">
          <p>This official link is not an HTML page, so it cannot be previewed here.</p>
          <p><a href="${finalUrl.toString()}">${finalUrl.toString()}</a></p>
        </body></html>`,
        {
          status: 200,
          headers: {
            "Content-Type": "text/html; charset=utf-8",
            "Cache-Control": "private, max-age=60",
            "X-Frame-Options": "SAMEORIGIN",
          },
        },
      );
    }

    const buf = await upstream.arrayBuffer();
    if (buf.byteLength > MAX_BYTES) {
      return NextResponse.json({ error: "Page too large to preview" }, { status: 413 });
    }
    const html = new TextDecoder("utf-8").decode(buf);
    const baseHref = new URL(".", finalUrl).toString();
    const body = injectViewerShell(html, baseHref, finalUrl.toString());

    return new NextResponse(body, {
      status: 200,
      headers: {
        "Content-Type": "text/html; charset=utf-8",
        "Cache-Control": "private, max-age=120",
        "X-Frame-Options": "SAMEORIGIN",
        "Content-Security-Policy": "frame-ancestors 'self'",
        "Referrer-Policy": "no-referrer",
      },
    });
  } catch {
    return new NextResponse(
      `<!doctype html><html><body style="font-family:system-ui;padding:1.5rem;background:#fff8f2;color:#1c1917">
        <h1 style="font-size:1.1rem">Preview unavailable</h1>
        <p>The official site did not allow fetching for in-page preview. Stay on DumpRegistry and use the verified answer on the guide page.</p>
        <p style="word-break:break-all">${target.toString()}</p>
      </body></html>`,
      {
        status: 200,
        headers: {
          "Content-Type": "text/html; charset=utf-8",
          "X-Frame-Options": "SAMEORIGIN",
          "Cache-Control": "private, max-age=30",
        },
      },
    );
  }
}
