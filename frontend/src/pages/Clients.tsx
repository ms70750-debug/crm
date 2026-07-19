import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { CrudShell, Panel } from "../components/CrudShell";
import { PageHeader } from "../components/PageHeader";
import { useAsync } from "../hooks/useAsync";
import { api } from "../lib/api";
import { Client, Consent } from "../types";

const schema = z.object({ nome: z.string().min(3), cpf: z.string().min(11), telefone: z.string().min(10), email: z.string().optional(), data_nascimento: z.string().optional(), beneficio: z.string().optional(), convenio: z.string(), banco_pagamento: z.string().optional(), observacoes: z.string().optional() });
type FormData = z.infer<typeof schema>;

export function Clients() {
  const { data, reload } = useAsync<Client[]>(() => api.get("/clientes"));
  const form = useForm<FormData>({ resolver: zodResolver(schema), defaultValues: { convenio: "INSS" } });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function submit(values: FormData) {
    setError("");
    setMessage("");
    try {
      await api.post("/clientes", values);
      form.reset({ convenio: "INSS" });
      setMessage("Cliente ficticio cadastrado.");
      reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel criar o cliente");
    }
  }

  async function registerConsent(client: Client) {
    setError("");
    setMessage("");
    try {
      await api.post("/consents", {
        customer_id: client.id,
        channel: "whatsapp",
        source: "CRM local",
        notes: "Opt-in ficticio registrado para teste de simulacao.",
      });
      setMessage(`Opt-in de WhatsApp registrado para ${client.nome}.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel registrar opt-in");
    }
  }

  async function revokeConsent(client: Client) {
    setError("");
    setMessage("");
    try {
      const consents = await api.get<Consent[]>(`/consents?customer_id=${client.id}`);
      const active = consents.find((item) => item.channel === "whatsapp" && item.granted && !item.revoked_at);
      if (!active) {
        setMessage(`Nenhum opt-in ativo encontrado para ${client.nome}.`);
        return;
      }
      await api.post(`/consents/${active.id}/revoke`, {});
      setMessage(`Opt-out de WhatsApp registrado para ${client.nome}.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel revogar opt-in");
    }
  }

  return (
    <>
      <PageHeader title="Clientes" subtitle="Cadastro, dados de beneficio e historico operacional simples." />
      <CrudShell>
        <Panel>
          <h3 className="mb-4 section-title">Novo cliente</h3>
          <form className="grid gap-3" onSubmit={form.handleSubmit(submit)}>
            <input className="input" placeholder="Nome" {...form.register("nome")} />
            <input className="input" placeholder="CPF" {...form.register("cpf")} />
            <input className="input" placeholder="Telefone" {...form.register("telefone")} />
            <input className="input" placeholder="E-mail" {...form.register("email")} />
            <input className="input" type="date" {...form.register("data_nascimento")} />
            <input className="input" placeholder="Beneficio" {...form.register("beneficio")} />
            <select className="input" {...form.register("convenio")}><option>INSS</option><option>FGTS</option><option>SIAPE</option></select>
            <input className="input" placeholder="Banco de pagamento" {...form.register("banco_pagamento")} />
            <textarea className="input min-h-24" placeholder="Observacoes" {...form.register("observacoes")} />
            {error && <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm font-semibold text-red-700">{error}</div>}
            {message && <div className="rounded-md border border-emerald-200 bg-emerald-50 p-3 text-sm font-semibold text-emerald-700">{message}</div>}
            <button className="btn" type="submit">Criar cliente</button>
          </form>
        </Panel>
        <Panel>
          <div className="overflow-x-auto">
            <h3 className="mb-4 section-title">Dados do cliente</h3>
            <table className="w-full min-w-[1040px]">
              <thead className="text-slate-400"><tr><th className="table-cell">Cliente</th><th className="table-cell">Contato</th><th className="table-cell">Convenio</th><th className="table-cell">Beneficio</th><th className="table-cell">Banco</th><th className="table-cell">Observacoes</th><th className="table-cell">LGPD</th></tr></thead>
              <tbody>{(data ?? []).map((client) => (
                <tr key={client.id}><td className="table-cell"><strong>{client.nome}</strong><div className="text-xs text-slate-500">CPF {client.cpf}</div></td><td className="table-cell"><div>{client.telefone}</div><div className="text-xs text-slate-500">{client.email || "-"}</div></td><td className="table-cell">{client.convenio}</td><td className="table-cell">{client.beneficio ?? "-"}</td><td className="table-cell">{client.banco_pagamento ?? "-"}</td><td className="table-cell"><span className="line-clamp-2 text-xs text-slate-400">{client.observacoes ?? "-"}</span></td><td className="table-cell"><div className="flex flex-wrap gap-2"><button className="btn-secondary py-1 text-xs" onClick={() => registerConsent(client)}>Opt-in WhatsApp</button><button className="btn-secondary py-1 text-xs" onClick={() => revokeConsent(client)}>Opt-out</button></div></td></tr>
              ))}</tbody>
            </table>
          </div>
        </Panel>
      </CrudShell>
    </>
  );
}
