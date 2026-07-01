import { useState } from "react";
import { Panel } from "../components/CrudShell";
import { PageHeader } from "../components/PageHeader";
import { api, formatMoney } from "../lib/api";

type InssResult = {
  beneficio: string;
  convenio: string;
  margem_disponivel: number;
  banco_pagamento: string;
};

export function INSS() {
  const [cpf, setCpf] = useState("");
  const [result, setResult] = useState<InssResult | null>(null);
  async function consult() {
    setResult(await api.get(`/consultas/inss/${cpf || "000.000.000-00"}`));
  }
  return (
    <>
      <PageHeader title="Consulta INSS" subtitle="Consulta simulada de margem, beneficio e elegibilidade." />
      <div className="grid gap-5 lg:grid-cols-[380px_1fr]">
        <Panel>
          <input className="input" placeholder="CPF" value={cpf} onChange={(e) => setCpf(e.target.value)} />
          <button className="btn mt-3 w-full" onClick={consult}>Consultar INSS</button>
        </Panel>
        <Panel>
          <h3 className="mb-4 font-semibold">Resultado simulado</h3>
          {result ? (
            <div className="grid gap-3 md:grid-cols-2">
              <Info label="Beneficio" value={result.beneficio} />
              <Info label="Convenio" value={result.convenio} />
              <Info label="Margem disponivel" value={formatMoney(result.margem_disponivel)} />
              <Info label="Banco pagamento" value={result.banco_pagamento} />
            </div>
          ) : <p className="text-sm text-slate-400">Informe um CPF ficticio para simular.</p>}
        </Panel>
      </div>
    </>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return <div className="rounded-md border border-line bg-white/5 p-4"><p className="text-xs text-slate-400">{label}</p><strong>{value}</strong></div>;
}
