import logo from "../../assets/brand/bbb-consig-logo.jpeg";
import logoWebp from "../../assets/brand/bbb-consig-logo-96.webp";

type BrandLogoProps = {
  compact?: boolean;
  className?: string;
};

export function BrandLogo({ compact = false, className = "" }: BrandLogoProps) {
  return (
    <div className={`flex min-w-0 items-center gap-3 ${className}`}>
      <picture className={compact ? "h-11 w-11 shrink-0" : "h-12 w-12 shrink-0"}>
        <source srcSet={logoWebp} type="image/webp" />
        <img
          className={compact ? "h-11 w-11 rounded-xl object-cover" : "h-12 w-12 rounded-2xl object-cover"}
          src={logo}
          alt="BBB Consig"
          width="96"
          height="96"
        />
      </picture>
      {!compact && (
        <div className="min-w-0">
          <div className="truncate text-base font-extrabold text-slate-950">BBB Consig</div>
          <div className="truncate text-xs font-semibold uppercase text-[var(--bbb-blue)]">CRM Operacional</div>
        </div>
      )}
    </div>
  );
}
