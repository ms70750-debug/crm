import { AlertTriangle, CalendarClock, CheckCircle2, FileClock, ListTodo, TrendingUp, Users } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Panel } from "../components/CrudShell";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { api, formatMoney } from "../lib/api";
import type { DashboardSummary } from "../types";
import { useAsync } from "../hooks/useAsync";

const cards = [
  ["total_leads", "Total de leads", Users],
  ["leads_novos", "Leads novos", TrendingUp],
  ["leads_atrasados", "Leads atrasados", AlertTriangle],
  ["propostas_em_andamento", "Propostas em andamento", FileClock],
  ["propostas_aprovadas", "Propostas aprovadas", CheckCircle2],
  ["valor_total_aprovado", "Valor aprovado", TrendingUp],
  ["tarefas_pendentes", "Tarefas pendentes", ListTodo],
] as const;

export function Dashboard() {
  const { data, loading, error } = useAsync<DashboardSummary>(() => api.get("/dashboard/resumo"));
  return (
    <>
      <PageHeader title="Dashboard" subtitle="Resumo executivo da operacao, proximos contatos e esteira comercial." />
      {error && <Panel className="mb-4 text-red-300">{error}</Panel>}
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {cards.map(([key, label, Icon]) => (
          <Panel key={key}>
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">{label}</span>
              <Icon className="text-lime" size={20} />
            </div>
            <div className="mt-3 text-3xl font-semibold">
              {key === "valor_total_aprovado" ? formatMoney(data?.cards[key] ?? 0) : loading ? "..." : data?.cards[key] ?? 0}
            </div>
          </Panel>
        ))}
      </div>
      <div className="mt-5 grid gap-5 xl:grid-cols-2">
        <Panel>
          <h3 className="mb-4 font-semibold">Propostas por status</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data?.propostas_por_status ?? []}>
                <CartesianGrid stroke="#dbe4f0" />
                <XAxis dataKey="status" stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip contentStyle={{ background: "#ffffff", border: "1px solid #dbe4f0", color: "#0f172a" }} />
                <Bar dataKey="total" fill="#0b5ed7" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
        <Panel>
          <h3 className="mb-4 font-semibold">Leads por status</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data?.leads_por_status ?? []}>
                <CartesianGrid stroke="#dbe4f0" />
                <XAxis dataKey="status" stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip contentStyle={{ background: "#ffffff", border: "1px solid #dbe4f0", color: "#0f172a" }} />
                <Bar dataKey="total" fill="#f97316" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
        <Panel>
          <h3 className="mb-4 font-semibold">Leads por origem</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data?.leads_por_origem ?? []}>
                <CartesianGrid stroke="#dbe4f0" />
                <XAxis dataKey="origem" stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip contentStyle={{ background: "#ffffff", border: "1px solid #dbe4f0", color: "#0f172a" }} />
                <Bar dataKey="total" fill="#f7c948" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
        <Panel>
          <h3 className="mb-4 flex items-center gap-2 font-semibold"><CalendarClock size={18} /> Proximos contatos</h3>
          <div className="grid gap-3">
            {(data?.proximos_contatos ?? []).map((lead) => (
              <div key={lead.id} className="rounded-md border border-line bg-white/5 p-3">
                <div className="flex items-center justify-between gap-2">
                  <strong>{lead.nome}</strong>
                  <StatusBadge value={lead.status} />
                </div>
                <p className="mt-1 text-sm text-slate-400">{lead.telefone} - {lead.proximo_contato}</p>
              </div>
            ))}
          </div>
        </Panel>
      </div>
    </>
  );
}
