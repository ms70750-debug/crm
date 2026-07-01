import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { CrudShell, Panel } from "../components/CrudShell";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { useAuth } from "../auth/AuthContext";
import { useAsync } from "../hooks/useAsync";
import { api, formatMoney } from "../lib/api";
import { Client, Proposal } from "../types";

const schema = z.object({ cliente_id: z.coerce.number().min(1), produto: z.string(), banco: z.string(), valor_liberado: z.coerce.number(), parcela: z.coerce.number(), prazo: z.coerce.number(), status: z.string(), observacoes: z.string().optional() });
type FormData = z.infer<typeof schema>;

export function Proposals() {
  const { user } = useAuth();
  const canUseClients = user?.role !== "parceiro";
  const proposals = useAsync<Proposal[]>(() => api.get("/propostas"));
  const clients = useAsync<Client[]>(() => canUseClients ? api.get("/clientes") : Promise.resolve([]), [canUseClients]);
  const clientById = new Map((clients.data ?? []).map((client) => [client.id, client]));
  const defaultValues = { produto: "INSS", banco: "Banco simulado", valor_liberado: 0, parcela: 0, prazo: 84, status: "Em andamento" };
  const form = useForm<FormData>({ resolver: zodResolver(schema), defaultValues });
  async function submit(values: FormData) {
    await api.post("/propostas", values);
    form.reset(defaultValues);
    proposals.reload();
  }
  return (
    <>
      <PageHeader title="Propostas" subtitle="Digitacao, acompanhamento e aprovacao de propostas simuladas." />
      <CrudShell>
        {canUseClients && <Panel>
          <h3 className="mb-4 font-semibold">Nova proposta</h3>
          <form className="grid gap-3" onSubmit={form.handleSubmit(submit)}>
            <select className="input" {...form.register("cliente_id")}>
              <option value="">Cliente</option>
              {(clients.data ?? []).map((c) => <option key={c.id} value={c.id}>{c.nome} - {c.cpf} - {c.telefone}</option>)}
            </select>
            <select className="input" {...form.register("produto")}><option>INSS</option><option>FGTS</option></select>
            <input className="input" placeholder="Banco" {...form.register("banco")} />
            <input className="input" type="number" step="0.01" placeholder="Valor liberado" {...form.register("valor_liberado")} />
            <input className="input" type="number" step="0.01" placeholder="Parcela" {...form.register("parcela")} />
            <input className="input" type="number" placeholder="Prazo" {...form.register("prazo")} />
            <select className="input" {...form.register("status")}><option>Em andamento</option><option>Proposta enviada</option><option>Digitado</option><option>Pendente banco</option><option>Aprovado</option><option>Pago</option><option>Perdido</option></select>
            <textarea className="input min-h-24" placeholder="Observacoes" {...form.register("observacoes")} />
            <button className="btn" type="submit">Criar proposta</button>
          </form>
        </Panel>}
        <Panel>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[820px]">
              <thead className="text-slate-400"><tr><th className="table-cell">Cliente</th><th className="table-cell">Produto</th><th className="table-cell">Banco</th><th className="table-cell">Valor</th><th className="table-cell">Parcela</th><th className="table-cell">Status</th></tr></thead>
              <tbody>{(proposals.data ?? []).map((p) => (
                <tr key={p.id}><td className="table-cell">{clientById.get(p.cliente_id)?.nome ?? `Cliente #${p.cliente_id}`}<div className="text-xs text-slate-500">{clientById.get(p.cliente_id)?.cpf ?? ""}</div></td><td className="table-cell">{p.produto}</td><td className="table-cell">{p.banco}</td><td className="table-cell">{formatMoney(p.valor_liberado)}</td><td className="table-cell">{formatMoney(p.parcela)}</td><td className="table-cell"><StatusBadge value={p.status} /></td></tr>
              ))}</tbody>
            </table>
          </div>
        </Panel>
      </CrudShell>
    </>
  );
}
