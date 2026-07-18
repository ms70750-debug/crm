import { useMemo, useState } from "react";
import { CrudShell, Panel } from "../components/CrudShell";
import { PageHeader } from "../components/PageHeader";
import { useAsync } from "../hooks/useAsync";
import { api } from "../lib/api";
import { Client, Lead } from "../types";

type History = { id: number; telefone: string; mensagem: string; modelo: string; status: string; criado_em: string };

export function WhatsApp() {
  const leads = useAsync<Lead[]>(() => api.get("/leads"));
  const clients = useAsync<Client[]>(() => api.get("/clientes"));
  const history = useAsync<History[]>(() => api.get("/whatsapp/historico"));
  const [tipo, setTipo] = useState("lead");
  const [id, setId] = useState("");
  const [modelo, setModelo] = useState("primeiro_contato");
  const [mensagem, setMensagem] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const recipients = useMemo(() => tipo === "lead" ? leads.data ?? [] : clients.data ?? [], [tipo, leads.data, clients.data]);

  async function preview() {
    setError("");
    setSuccess("");
    try {
      const data = await api.post<{ mensagem: string }>("/whatsapp/preview", { destinatario_tipo: tipo, destinatario_id: Number(id), modelo });
      setMensagem(data.mensagem);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel gerar previa");
    }
  }

  async function register() {
    setError("");
    setSuccess("");
    try {
      await api.post("/whatsapp/simular-envio", { destinatario_tipo: tipo, destinatario_id: Number(id), modelo, mensagem });
      setMensagem("");
      setSuccess("Simulacao registrada. Nenhuma mensagem real foi enviada.");
      history.reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel registrar simulacao");
    }
  }
  return (
    <>
      <PageHeader title="WhatsApp Simulado" subtitle="Gere previa e registre historico interno sem envio real." />
      <CrudShell>
        <Panel>
          <div className="grid gap-3">
            <select className="input" value={tipo} onChange={(e) => setTipo(e.target.value)}><option value="lead">Lead</option><option value="cliente">Cliente</option></select>
            <select className="input" value={id} onChange={(e) => setId(e.target.value)}>
              <option value="">Selecione</option>
              {recipients.map((r) => <option key={r.id} value={r.id}>{r.nome} - {r.cpf} - {r.telefone}</option>)}
            </select>
            <select className="input" value={modelo} onChange={(e) => setModelo(e.target.value)}>
              <option value="primeiro_contato">Primeiro contato</option>
              <option value="documentos">Documentos</option>
              <option value="proposta">Proposta pronta</option>
            </select>
            <button className="btn-secondary" onClick={preview} disabled={!id}>Gerar previa</button>
            <textarea className="input min-h-40" value={mensagem} onChange={(e) => setMensagem(e.target.value)} />
            {error && <div className="alert-error">{error}</div>}
            {success && <div className="alert-success">{success}</div>}
            <button className="btn" onClick={register} disabled={!mensagem}>Registrar simulacao</button>
          </div>
        </Panel>
        <Panel>
          <h3 className="mb-4 font-semibold">Historico simulado</h3>
          <div className="grid gap-3">
            {(history.data ?? []).map((item) => (
              <div key={item.id} className="subtle-card">
                <div className="flex justify-between gap-3"><strong>{item.modelo}</strong><span className="badge border-emerald-200 bg-emerald-50 text-emerald-700">{item.status}</span></div>
                <p className="mt-2 text-sm text-slate-600">{item.mensagem}</p>
                <p className="mt-2 text-xs text-slate-500">{item.telefone}</p>
              </div>
            ))}
          </div>
        </Panel>
      </CrudShell>
    </>
  );
}
