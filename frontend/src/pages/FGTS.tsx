import { useState } from "react";
import { Panel } from "../components/CrudShell";
import { PageHeader } from "../components/PageHeader";
import { api, formatMoney } from "../lib/api";

type FgtsResult = {
  saldo_estimado: number;
  valor_liberado: number;
  parcelas_antecipaveis: number;
};

export function FGTS() {
  const [cpf, setCpf] = useState("");
  const [result, setResult] = useState<FgtsResult | null>(null);
  async function consult() {
    setResult(await api.get(`/consultas/fgts/${cpf || "000.000.000-00"}`));
  }
  return (
    <>
      <PageHeader title="Consulta FGTS" subtitle="Simulacao de saldo, antecipacao e valor liberado." />
      <div className="grid gap-5 lg:grid-cols-[380px_1fr]">
        <Panel>
          <input className="input" placeholder="CPF" value={cpf} onChange={(e) => setCpf(e.target.value)} />
          <button className="btn mt-3 w-full" onClick={consult}>Simular FGTS</button>
        </Panel>
        <Panel>
          <h3 className="mb-4 font-semibold">Resultado simulado</h3>
          {result ? (
            <div className="grid gap-3 md:grid-cols-3">
              <Info label="Saldo estimado" value={formatMoney(result.saldo_estimado)} />
              <Info label="Valor liberado" value={formatMoney(result.valor_liberado)} />
              <Info label="Parcelas" value={`${result.parcelas_antecipaveis}`} />
            </div>
          ) : <p className="text-sm text-slate-500">Informe um CPF ficticio para simular.</p>}
        </Panel>
      </div>
    </>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return <div className="subtle-card p-4"><p className="text-xs text-slate-500">{label}</p><strong>{value}</strong></div>;
}
