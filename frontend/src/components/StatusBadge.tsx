const tone: Record<string, string> = {
  Aprovado: "border-emerald-400/40 text-emerald-300",
  Pago: "border-emerald-400/40 text-emerald-300",
  Concluida: "border-emerald-400/40 text-emerald-300",
  Pendente: "border-amber-400/40 text-amber-300",
  "Novo lead": "border-lime/40 text-lime",
  Perdido: "border-red-400/40 text-red-300",
};

export function StatusBadge({ value }: { value: string }) {
  return <span className={`badge ${tone[value] ?? "border-sky-400/40 text-sky-300"}`}>{value}</span>;
}
