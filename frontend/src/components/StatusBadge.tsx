const tone: Record<string, string> = {
  Aprovado: "border-emerald-200 bg-emerald-50 text-emerald-700",
  Pago: "border-emerald-200 bg-emerald-50 text-emerald-700",
  Concluida: "border-emerald-200 bg-emerald-50 text-emerald-700",
  Pendente: "border-amber-200 bg-amber-50 text-amber-700",
  "Novo lead": "border-blue-200 bg-blue-50 text-lime",
  Perdido: "border-red-200 bg-red-50 text-red-700",
};

export function StatusBadge({ value }: { value: string }) {
  return <span className={`badge ${tone[value] ?? "border-sky-200 bg-sky-50 text-sky-700"}`}>{value}</span>;
}
