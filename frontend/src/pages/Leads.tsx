import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";
import { z } from "zod";
import { useAuth } from "../auth/AuthContext";
import { CrudShell, Panel } from "../components/CrudShell";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { useAsync } from "../hooks/useAsync";
import { api } from "../lib/api";
import { Lead } from "../types";

const statuses = ["Novo lead", "Qualificado", "Aguardando documentos", "Simulado", "Proposta enviada", "Digitado", "Pendente banco", "Aprovado", "Pago", "Perdido"];
const prioridades = ["Alta", "Media", "Baixa"];
const schema = z.object({
  nome: z.string().min(3),
  cpf: z.string().min(11),
  telefone: z.string().min(10),
  email: z.string().email().optional().or(z.literal("")),
  origem: z.string().min(2),
  produto_interesse: z.string().min(2),
  status: z.string(),
  prioridade: z.string(),
  responsavel: z.string().min(2),
  proximo_contato: z.string().optional(),
  observacoes: z.string().optional(),
});
type FormData = z.infer<typeof schema>;

export function Leads() {
  const { user } = useAuth();
  const [status, setStatus] = useState("");
  const [origem, setOrigem] = useState("");
  const [produto, setProduto] = useState("");
  const [q, setQ] = useState("");
  const [error, setError] = useState("");
  const { data, reload } = useAsync<Lead[]>(
    () => api.get(`/leads?${new URLSearchParams({ ...(status && { status }), ...(origem && { origem }), ...(produto && { produto_interesse: produto }), ...(q && { q }) })}`),
    [status, origem, produto, q]
  );
  const allLeads = useAsync<Lead[]>(() => api.get("/leads"));
  const origemOptions = Array.from(new Set((allLeads.data ?? []).map((lead) => lead.origem))).filter(Boolean);
  const form = useForm<FormData>({ resolver: zodResolver(schema), defaultValues: { origem: "Manual", produto_interesse: "INSS", status: "Novo lead", prioridade: "Media", responsavel: "Equipe BBB" } });

  async function submit(values: FormData) {
    setError("");
    try {
      await api.post("/leads", values);
      form.reset({ origem: "Manual", produto_interesse: "INSS", status: "Novo lead", prioridade: "Media", responsavel: "Equipe BBB" });
      allLeads.reload();
      reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel criar o lead");
    }
  }

  async function updateStatus(lead: Lead, nextStatus: string) {
    setError("");
    try {
      await api.patch(`/leads/${lead.id}/status`, { status: nextStatus });
      allLeads.reload();
      reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel atualizar o lead");
    }
  }

  async function deleteLead(lead: Lead) {
    setError("");
    try {
      await api.delete(`/leads/${lead.id}`);
      allLeads.reload();
      reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel excluir o lead");
    }
  }

  return (
    <>
      <PageHeader title="Leads" subtitle="Captacao, qualificacao e acompanhamento do pipeline comercial." />
      {error && <Panel className="mb-4 text-red-300">{error}</Panel>}
      <CrudShell>
        <Panel>
          <h3 className="mb-4 section-title">Novo lead</h3>
          <form className="grid gap-3" onSubmit={form.handleSubmit(submit)}>
            <input className="input" placeholder="Nome" {...form.register("nome")} />
            <input className="input" placeholder="CPF" {...form.register("cpf")} />
            <input className="input" placeholder="Telefone" {...form.register("telefone")} />
            <input className="input" placeholder="E-mail" {...form.register("email")} />
            <div className="grid grid-cols-2 gap-3">
              <input className="input" placeholder="Origem" {...form.register("origem")} />
              <select className="input" {...form.register("produto_interesse")}><option>INSS</option><option>FGTS</option></select>
            </div>
            <select className="input" {...form.register("status")}>{statuses.map((s) => <option key={s}>{s}</option>)}</select>
            <select className="input" {...form.register("prioridade")}>{prioridades.map((p) => <option key={p}>{p}</option>)}</select>
            <input className="input" placeholder="Responsavel" {...form.register("responsavel")} />
            <input className="input" type="date" {...form.register("proximo_contato")} />
            <textarea className="input min-h-24" placeholder="Observacoes" {...form.register("observacoes")} />
            <button className="btn" type="submit">Criar lead</button>
          </form>
        </Panel>
        <Panel>
          <div className="mb-4 grid gap-3 md:grid-cols-[1fr_180px_180px_180px]">
            <input className="input" placeholder="Buscar por nome, CPF ou telefone" value={q} onChange={(e) => setQ(e.target.value)} />
            <select className="input" value={status} onChange={(e) => setStatus(e.target.value)}>
              <option value="">Todos os status</option>
              {statuses.map((s) => <option key={s}>{s}</option>)}
            </select>
            <select className="input" value={origem} onChange={(e) => setOrigem(e.target.value)}>
              <option value="">Todas origens</option>
              {origemOptions.map((item) => <option key={item}>{item}</option>)}
            </select>
            <select className="input" value={produto} onChange={(e) => setProduto(e.target.value)}>
              <option value="">Todos produtos</option>
              <option>INSS</option>
              <option>FGTS</option>
            </select>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[1120px]">
              <thead className="text-slate-400"><tr><th className="table-cell">Lead</th><th className="table-cell">Contato</th><th className="table-cell">Origem</th><th className="table-cell">Produto</th><th className="table-cell">Status</th><th className="table-cell">Prioridade</th><th className="table-cell">Responsavel</th><th className="table-cell">Proximo contato</th><th className="table-cell">Acoes</th></tr></thead>
              <tbody>{(data ?? []).map((lead) => (
                <tr key={lead.id}>
                  <td className="table-cell"><strong>{lead.nome}</strong><div className="text-xs text-slate-500">CPF {lead.cpf}</div>{lead.observacoes && <div className="mt-1 max-w-72 truncate text-xs text-slate-500">{lead.observacoes}</div>}</td>
                  <td className="table-cell"><div>{lead.telefone}</div><div className="text-xs text-slate-500">{lead.email || "-"}</div></td>
                  <td className="table-cell">{lead.origem}</td>
                  <td className="table-cell">{lead.produto_interesse}</td>
                  <td className="table-cell">
                    <div className="grid gap-2">
                      <StatusBadge value={lead.status} />
                      {user?.role !== "parceiro" && (
                        <select className="input py-1 text-xs" value={lead.status} onChange={(event) => updateStatus(lead, event.target.value)}>
                          {statuses.map((s) => <option key={s}>{s}</option>)}
                        </select>
                      )}
                    </div>
                  </td>
                  <td className="table-cell"><span className="badge">{lead.prioridade}</span></td>
                  <td className="table-cell">{lead.responsavel}</td>
                  <td className="table-cell">{isOverdue(lead.proximo_contato) ? <span className="badge border-red-400/40 text-red-300">Atrasado - {lead.proximo_contato}</span> : lead.proximo_contato || "-"}</td>
                  <td className="table-cell">
                    <div className="flex flex-wrap gap-2">
                      <Link className="btn-secondary" to={`/leads/${lead.id}`}>Detalhe</Link>
                      {(user?.role === "admin" || user?.role === "supervisor") && <button className="btn-secondary" onClick={() => deleteLead(lead)}>Excluir</button>}
                    </div>
                  </td>
                </tr>
              ))}</tbody>
            </table>
          </div>
        </Panel>
      </CrudShell>
    </>
  );
}

function isOverdue(date?: string) {
  if (!date) return false;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return new Date(`${date}T00:00:00`) < today;
}
