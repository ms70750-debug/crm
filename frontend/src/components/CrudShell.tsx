import type { ReactNode } from "react";

export function CrudShell({ children }: { children: ReactNode }) {
  return <div className="grid min-w-0 gap-5 xl:grid-cols-[360px_minmax(0,1fr)]">{children}</div>;
}

export function Panel({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <section className={`panel min-w-0 p-4 sm:p-5 ${className}`}>{children}</section>;
}
