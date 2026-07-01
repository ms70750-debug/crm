import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { CrudShell, Panel } from "../components/CrudShell";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { useAsync } from "../hooks/useAsync";
import { api } from "../lib/api";
import { Lead } from "../types";

const statuses = ["Novo lead", "Qualificado", "Aguardando documentos", "Simulado", "Proposta enviada", "Digitado", "Pendente banco", "Aprovado", "Pago", "Perdido"];
const schema = z.object({
  nome: z.string().min(3),
  cpf: z.string().min(11),
  telefone: z.string().min(10),
  email: z.string().email().optional().or(z.literal("")),
  origem: z.string().min(2),
  produto_interesse: z.string().min(2),
  status: z.string(),
  responsavel: z.string().min(2),
  proximo_contato: z.string().optional(),
  observacoes: z.string().optional(),
});
type FormData = z.infer<typeof schema>;

export function Leads() {
  const [status, setStatus] = useState("");
  const [q, setQ] = useState("");
  const { data, reload } = useAsync<Lead[]>(() => api.get(`/leads?${new URLSearchParams({ ...(status && { status }), ...(q && { q }) })}`), [status, q]);
  const form = useForm<FormData>({ resolver: zodResolver(schema), defaultValues: { origem: "Manual", produto_interesse: "INSS", status: "Novo lead", responsavel: "Equipe BBB" } });

  async function submit(values: FormData) {
    await api.post("/leads", values);
    form.reset({ origem: "Manual", produto_interesse: "INSS", status: "Novo lead", responsavel: "Equipe BBB" });
    reload();
  }

  return (
    <>
      <PageHeader title="Leads" subtitle="Captacao, qualificacao e acompanhamento do pipeline comercial." />
      <CrudShell>
        <Panel>
          <h3 className="mb-4 font-semibold">Novo lead</h3>
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
            <input className="input" placeholder="Responsavel" {...form.register("responsavel")} />
            <input className="input" type="date" {...form.register("proximo_contato")} />
            <textarea className="input min-h-24" placeholder="Observacoes" {...form.register("observacoes")} />
            <button className="btn" type="submit">Criar lead</button>
          </form>
        </Panel>
        <Panel>
          <div className="mb-4 grid gap-3 md:grid-cols-[1fr_220px]">
            <input className="input" placeholder="Buscar por nome, CPF ou telefone" value={q} onChange={(e) => setQ(e.target.value)} />
            <select className="input" value={status} onChange={(e) => setStatus(e.target.value)}>
              <option value="">Todos os status</option>
              {statuses.map((s) => <option key={s}>{s}</option>)}
            </select>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[760px]">
              <thead className="text-slate-400"><tr><th className="table-cell">Nome</th><th className="table-cell">Produto</th><th className="table-cell">Status</th><th className="table-cell">Responsavel</th><th className="table-cell">Proximo contato</th></tr></thead>
              <tbody>{(data ?? []).map((lead) => (
                <tr key={lead.id}><td className="table-cell"><strong>{lead.nome}</strong><div className="text-xs text-slate-500">{lead.cpf} - {lead.telefone}</div></td><td className="table-cell">{lead.produto_interesse}</td><td className="table-cell"><StatusBadge value={lead.status} /></td><td className="table-cell">{lead.responsavel}</td><td className="table-cell">{lead.proximo_contato ?? "-"}</td></tr>
              ))}</tbody>
            </table>
          </div>
        </Panel>
      </CrudShell>
    </>
  );
}
