export type Lead = {
  id: number;
  nome: string;
  cpf: string;
  telefone: string;
  email?: string;
  origem: string;
  produto_interesse: string;
  status: string;
  prioridade: string;
  responsavel: string;
  observacoes?: string;
  data_criacao: string;
  proximo_contato?: string;
};

export type LeadTimelineEvent = {
  tipo: string;
  titulo: string;
  descricao: string;
  data?: string;
};

export type LeadDetail = Lead & {
  timeline: LeadTimelineEvent[];
  historico: LeadTimelineEvent[];
};

export type Client = {
  id: number;
  nome: string;
  cpf: string;
  telefone: string;
  email?: string;
  data_nascimento?: string;
  beneficio?: string;
  convenio: string;
  banco_pagamento?: string;
  observacoes?: string;
};

export type Proposal = {
  id: number;
  cliente_id: number;
  produto: string;
  banco: string;
  valor_liberado: number;
  parcela: number;
  prazo: number;
  status: string;
  data_criacao: string;
  observacoes?: string;
};

export type DashboardSummary = {
  cards: Record<string, number>;
  propostas_por_status: { status: string; total: number }[];
  leads_por_status: { status: string; total: number }[];
  leads_por_origem: { origem: string; total: number }[];
  proximos_contatos: Lead[];
};

export type Task = {
  id: number;
  titulo: string;
  descricao?: string;
  status: string;
  prioridade: string;
  responsavel: string;
  lead_id?: number;
  cliente_id?: number;
  data_vencimento?: string;
};
