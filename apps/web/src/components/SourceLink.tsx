"use client";

import type { ReactNode } from "react";
import { OfficialLink } from "@/components/OfficialViewer";

export function SourceLink({
  url,
  title,
  children = "View source",
}: {
  url: string;
  title?: string | null;
  children?: ReactNode;
}) {
  return (
    <OfficialLink className="source-inpage-link" url={url} title={title}>
      {children}
    </OfficialLink>
  );
}
