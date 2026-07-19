import logo from "../../assets/brand/bbb-consig-logo.jpeg";

type BrandLogoProps = {
  compact?: boolean;
  className?: string;
};

export function BrandLogo({ compact = false, className = "" }: BrandLogoProps) {
  return (
    <div className={`flex min-w-0 items-center gap-3 ${className}`}>
      <img
        className={compact ? "h-11 w-11 shrink-0 rounded-xl object-cover" : "h-12 w-12 shrink-0 rounded-2xl object-cover"}
        src={logo}
        alt="BBB Consig"
      />
      {!compact && (
        <div className="min-w-0">
          <div className="truncate text-base font-extrabold text-slate-950">BBB Consig</div>
          <div className="truncate text-xs font-semibold uppercase text-[var(--bbb-blue)]">CRM Operacional</div>
        </div>
      )}
    </div>
  );
}
