import type { ReactNode } from "react";

export function CrudShell({ children }: { children: ReactNode }) {
  return <div className="grid gap-5 xl:grid-cols-[360px_1fr]">{children}</div>;
}

export function Panel({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <section className={`panel rounded-lg p-4 ${className}`}>{children}</section>;
}
