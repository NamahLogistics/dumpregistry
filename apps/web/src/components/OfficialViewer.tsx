"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useId,
  useMemo,
  useState,
  type ReactNode,
} from "react";

type OfficialTarget = {
  url: string;
  title?: string | null;
};

type OfficialViewerContextValue = {
  openOfficial: (target: OfficialTarget) => void;
  closeOfficial: () => void;
};

const OfficialViewerContext = createContext<OfficialViewerContextValue | null>(null);

function frameSrc(url: string) {
  return `/api/official-frame?url=${encodeURIComponent(url)}`;
}

export function useOfficialViewer() {
  const ctx = useContext(OfficialViewerContext);
  if (!ctx) {
    throw new Error("useOfficialViewer must be used within OfficialViewerProvider");
  }
  return ctx;
}

export function OfficialLink({
  url,
  title,
  className,
  children,
}: {
  url: string;
  title?: string | null;
  className?: string;
  children: ReactNode;
}) {
  const { openOfficial } = useOfficialViewer();
  return (
    <button
      type="button"
      className={className}
      onClick={() => openOfficial({ url, title })}
    >
      {children}
    </button>
  );
}

export function OfficialViewerProvider({ children }: { children: ReactNode }) {
  const [target, setTarget] = useState<OfficialTarget | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "blocked">("loading");
  const [copied, setCopied] = useState(false);
  const titleId = useId();

  const openOfficial = useCallback((next: OfficialTarget) => {
    setTarget(next);
    setStatus("loading");
    setCopied(false);
  }, []);

  const closeOfficial = useCallback(() => {
    setTarget(null);
    setStatus("loading");
  }, []);

  useEffect(() => {
    if (!target) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") closeOfficial();
    };
    document.addEventListener("keydown", onKey);
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = prev;
    };
  }, [target, closeOfficial]);

  useEffect(() => {
    if (!target) return;
    const t = window.setTimeout(() => {
      setStatus((s) => (s === "loading" ? "blocked" : s));
    }, 8000);
    return () => window.clearTimeout(t);
  }, [target]);

  const value = useMemo(
    () => ({ openOfficial, closeOfficial }),
    [openOfficial, closeOfficial],
  );

  async function copyUrl() {
    if (!target) return;
    try {
      await navigator.clipboard.writeText(target.url);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1600);
    } catch {
      setCopied(false);
    }
  }

  return (
    <OfficialViewerContext.Provider value={value}>
      {children}
      {target ? (
        <div className="official-overlay" role="presentation" onClick={closeOfficial}>
          <div
            className="official-drawer"
            role="dialog"
            aria-modal="true"
            aria-labelledby={titleId}
            onClick={(e) => e.stopPropagation()}
          >
            <header className="official-drawer-head">
              <div>
                <p className="official-kicker">Official source · stays on DumpRegistry</p>
                <h2 id={titleId}>{target.title || "Official program page"}</h2>
              </div>
              <div className="official-drawer-actions">
                <button type="button" className="facility-action" onClick={copyUrl}>
                  {copied ? "Copied" : "Copy URL"}
                </button>
                <button type="button" className="facility-action" onClick={closeOfficial}>
                  Close
                </button>
              </div>
            </header>
            <p className="official-url-line">{target.url}</p>
            {status === "blocked" ? (
              <div className="official-fallback">
                <p>
                  This official site blocked in-page viewing (common on .gov pages). You are still on
                  DumpRegistry — use the verified answer and steps on this page, or copy the URL for your
                  records.
                </p>
                <button type="button" className="btn-primary" onClick={copyUrl}>
                  {copied ? "URL copied" : "Copy official URL"}
                </button>
              </div>
            ) : null}
            <div className={`official-frame-wrap${status === "blocked" ? " is-blocked" : ""}`}>
              {status === "loading" ? <p className="official-loading">Loading official page…</p> : null}
              <iframe
                key={target.url}
                title={target.title || "Official source"}
                src={frameSrc(target.url)}
                className="official-frame"
                referrerPolicy="no-referrer"
                sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
                onLoad={() => setStatus("ready")}
              />
            </div>
          </div>
        </div>
      ) : null}
    </OfficialViewerContext.Provider>
  );
}
