import { ArrowLeft, FilePlus2, UserCheck } from "lucide-react";
import { Link, useParams } from "react-router-dom";
import { Panel } from "../components/CrudShell";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { useAsync } from "../hooks/useAsync";
import { api } from "../lib/api";
import type { LeadDetail as LeadDetailType, LeadTimelineEvent } from "../types";

type ActionResult = {
  cliente?: { id: number; nome: string };
  proposta?: { id: number; status: string };
  criado?: boolean;
};

export function LeadDetail() {
  const { id } = useParams();
  const detail = useAsync<LeadDetailType>(() => api.get(`/leads/${id}/detalhe`), [id]);
  const lead = detail.data;

  async function convertLead() {
    await api.post<ActionResult>(`/leads/${id}/converter-cliente`, {});
    detail.reload();
  }

  async function createProposal() {
    await api.post<ActionResult>(`/leads/${id}/gerar-proposta`, {});
    detail.reload();
  }

  return (
    <>
      <div className="mb-4">
        <Link className="btn-secondary" to="/leads"><ArrowLeft size={16} /> Voltar</Link>
      </div>
      <PageHeader title={lead?.nome ?? "Detalhe do lead"} subtitle="Historico, timeline e acoes da esteira comercial." />
      {detail.error && <Panel className="mb-4 text-red-300">{detail.error}</Panel>}
      {!lead ? (
        <Panel>Carregando lead...</Panel>
      ) : (
        <div className="grid gap-5 xl:grid-cols-[380px_1fr]">
          <Panel>
            <div className="grid gap-4">
              <div>
                <h3 className="mb-3 font-semibold">Dados operacionais</h3>
                <div className="grid gap-3">
                  <Info label="CPF" value={lead.cpf} />
                  <Info label="Telefone" value={lead.telefone} />
                  <Info label="E-mail" value={lead.email || "-"} />
                  <Info label="Convenio" value={lead.convenio || lead.produto_interesse} />
                  <Info label="Beneficio" value={lead.beneficio || "-"} />
                  <Info label="Matricula" value={lead.matricula || "-"} />
                  <Info label="Banco pagamento" value={lead.banco_pagamento || "-"} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <Info label="Produto" value={lead.produto_interesse} />
                <Info label="Origem" value={lead.origem} />
                <Info label="Prioridade" value={lead.prioridade} />
                <Info label="Responsavel" value={lead.responsavel} />
              </div>
              <div className="flex flex-wrap gap-2">
                <StatusBadge value={lead.status} />
                {isOverdue(lead.proximo_contato) && <span className="badge border-red-400/40 text-red-300">Contato atrasado</span>}
              </div>
              <div>
                <p className="text-xs text-slate-400">Proximo contato</p>
                <strong>{lead.proximo_contato || "-"}</strong>
              </div>
              <div>
                <p className="mb-1 text-xs text-slate-400">Observacoes operacionais</p>
                <p className="rounded-md border border-line bg-white/5 p-3 text-sm text-slate-300">{lead.observacoes || "Sem observacoes."}</p>
              </div>
              <div className="grid gap-2">
                <button className="btn" onClick={convertLead}><UserCheck size={16} /> Converter em cliente</button>
                <button className="btn-secondary" onClick={createProposal}><FilePlus2 size={16} /> Gerar proposta</button>
              </div>
            </div>
          </Panel>
          <div className="grid gap-5">
            <Panel>
              <h3 className="mb-4 font-semibold">Timeline</h3>
              <Timeline items={lead.timeline} />
            </Panel>
            <Panel>
              <h3 className="mb-4 font-semibold">Historico de interacoes</h3>
              <Timeline items={lead.historico} />
            </Panel>
          </div>
        </div>
      )}
    </>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return <div className="rounded-md border border-line bg-white/5 p-3"><p className="text-xs text-slate-400">{label}</p><strong>{value}</strong></div>;
}

function Timeline({ items }: { items: LeadTimelineEvent[] }) {
  return (
    <div className="grid gap-3">
      {items.length === 0 && <p className="text-sm text-slate-400">Nenhum registro ainda.</p>}
      {items.map((item, index) => (
        <div key={`${item.tipo}-${index}`} className="rounded-md border border-line bg-white/5 p-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <strong>{item.titulo}</strong>
            <span className="badge">{item.tipo}</span>
          </div>
          <p className="mt-1 text-sm text-slate-300">{item.descricao}</p>
          {item.data && <p className="mt-2 text-xs text-slate-500">{item.data}</p>}
        </div>
      ))}
    </div>
  );
}

function isOverdue(date?: string) {
  if (!date) return false;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return new Date(`${date}T00:00:00`) < today;
}
