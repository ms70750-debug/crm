export function PageHeader({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
      <div>
        <p className="text-xs font-bold uppercase text-[var(--bbb-orange)]">BBB Consig</p>
        <h2 className="mt-1 text-2xl font-extrabold text-slate-950">{title}</h2>
        <p className="mt-1 text-sm leading-6 text-slate-600">{subtitle}</p>
      </div>
    </div>
  );
}
