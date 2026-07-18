type BrandLogoProps = {
  compact?: boolean;
};

export function BrandLogo({ compact = false }: BrandLogoProps) {
  return (
    <div className="flex min-w-0 items-center gap-3">
      <img
        alt="BBB Consig"
        className={compact ? "h-10 w-10 rounded-md object-cover" : "h-12 w-12 rounded-md object-cover"}
        src="/brand/logo-bbb-consig-oficial.jpeg"
      />
      <div className="min-w-0">
        <div className="truncate text-sm font-semibold text-lime">BBB Consig</div>
        <div className={compact ? "truncate text-base font-bold text-ink" : "truncate text-lg font-bold text-ink"}>CRM</div>
      </div>
    </div>
  );
}
