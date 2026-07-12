CREATE TABLE IF NOT EXISTS leads (
  id SERIAL PRIMARY KEY,
  nome VARCHAR(140) NOT NULL,
  cpf VARCHAR(14) NOT NULL UNIQUE,
  telefone VARCHAR(30) NOT NULL,
  email VARCHAR(140),
  origem VARCHAR(80) NOT NULL DEFAULT 'Manual',
  produto_interesse VARCHAR(80) NOT NULL DEFAULT 'INSS',
  status VARCHAR(40) NOT NULL DEFAULT 'Novo lead',
  prioridade VARCHAR(20) NOT NULL DEFAULT 'Media',
  responsavel VARCHAR(80) NOT NULL DEFAULT 'Equipe BBB',
  observacoes TEXT,
  data_criacao TIMESTAMPTZ,
  proximo_contato VARCHAR(20),
  deleted_at TIMESTAMPTZ,
  deleted_by INTEGER,
  deletion_reason TEXT,
  cpf_hash VARCHAR(64),
  cpf_encrypted TEXT,
  telefone_encrypted TEXT,
  email_encrypted TEXT,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS clientes (
  id SERIAL PRIMARY KEY,
  nome VARCHAR(140) NOT NULL,
  cpf VARCHAR(14) NOT NULL UNIQUE,
  telefone VARCHAR(30) NOT NULL,
  email VARCHAR(140),
  data_nascimento VARCHAR(20),
  beneficio VARCHAR(40),
  convenio VARCHAR(80) NOT NULL DEFAULT 'INSS',
  banco_pagamento VARCHAR(80),
  observacoes TEXT,
  deleted_at TIMESTAMPTZ,
  deleted_by INTEGER,
  deletion_reason TEXT,
  cpf_hash VARCHAR(64),
  cpf_encrypted TEXT,
  telefone_encrypted TEXT,
  email_encrypted TEXT,
  bank_data_encrypted TEXT,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS propostas (
  id SERIAL PRIMARY KEY,
  cliente_id INTEGER NOT NULL REFERENCES clientes(id),
  produto VARCHAR(80) NOT NULL DEFAULT 'INSS',
  banco VARCHAR(80) NOT NULL DEFAULT 'Banco simulado',
  valor_liberado DOUBLE PRECISION NOT NULL DEFAULT 0,
  parcela DOUBLE PRECISION NOT NULL DEFAULT 0,
  prazo INTEGER NOT NULL DEFAULT 84,
  status VARCHAR(40) NOT NULL DEFAULT 'Em andamento',
  data_criacao TIMESTAMPTZ,
  observacoes TEXT,
  deleted_at TIMESTAMPTZ,
  deleted_by INTEGER,
  deletion_reason TEXT,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS tarefas (
  id SERIAL PRIMARY KEY,
  titulo VARCHAR(160) NOT NULL,
  descricao TEXT,
  status VARCHAR(40) NOT NULL DEFAULT 'Pendente',
  prioridade VARCHAR(20) NOT NULL DEFAULT 'Media',
  responsavel VARCHAR(80) NOT NULL DEFAULT 'Equipe BBB',
  lead_id INTEGER REFERENCES leads(id),
  cliente_id INTEGER REFERENCES clientes(id),
  data_vencimento VARCHAR(20),
  deleted_at TIMESTAMPTZ,
  deleted_by INTEGER,
  deletion_reason TEXT,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS whatsapp_messages (
  id SERIAL PRIMARY KEY,
  destinatario_tipo VARCHAR(20) NOT NULL,
  destinatario_id INTEGER NOT NULL,
  telefone VARCHAR(30) NOT NULL,
  modelo VARCHAR(80) NOT NULL,
  mensagem TEXT NOT NULL,
  status VARCHAR(40) NOT NULL DEFAULT 'Registrada em simulacao',
  criado_em TIMESTAMPTZ,
  deleted_at TIMESTAMPTZ,
  deleted_by INTEGER,
  deletion_reason TEXT,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  nome VARCHAR(140) NOT NULL,
  email VARCHAR(140) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(40) NOT NULL DEFAULT 'admin',
  ativo BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS audit_logs (
  id SERIAL PRIMARY KEY,
  actor_user_id INTEGER,
  actor VARCHAR(140) NOT NULL DEFAULT 'system',
  action VARCHAR(100) NOT NULL,
  entity_type VARCHAR(80) NOT NULL,
  entity_id INTEGER,
  metadata_json TEXT,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS consents (
  id SERIAL PRIMARY KEY,
  customer_id INTEGER NOT NULL REFERENCES clientes(id),
  channel VARCHAR(40) NOT NULL,
  granted BOOLEAN NOT NULL DEFAULT TRUE,
  purpose VARCHAR(120) NOT NULL DEFAULT 'comunicacao',
  status VARCHAR(40) NOT NULL DEFAULT 'active',
  source VARCHAR(120) NOT NULL DEFAULT 'demo',
  ip_address VARCHAR(80),
  created_at TIMESTAMPTZ,
  revoked_at TIMESTAMPTZ,
  revoked_by INTEGER,
  deleted_at TIMESTAMPTZ,
  deleted_by INTEGER,
  deletion_reason TEXT,
  metadata_json TEXT,
  updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS simulations (
  id SERIAL PRIMARY KEY,
  customer_id INTEGER REFERENCES clientes(id),
  cpf_masked VARCHAR(20) NOT NULL,
  produto VARCHAR(80) NOT NULL,
  rule_id VARCHAR(80) NOT NULL,
  input_json TEXT NOT NULL,
  result_json TEXT NOT NULL,
  payload_hash VARCHAR(64) NOT NULL,
  created_at TIMESTAMPTZ,
  deleted_at TIMESTAMPTZ,
  deleted_by INTEGER,
  deletion_reason TEXT,
  updated_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_leads_nome ON leads (nome);
CREATE INDEX IF NOT EXISTS ix_leads_cpf ON leads (cpf);
CREATE INDEX IF NOT EXISTS ix_leads_telefone ON leads (telefone);
CREATE INDEX IF NOT EXISTS ix_leads_status ON leads (status);
CREATE INDEX IF NOT EXISTS ix_leads_prioridade ON leads (prioridade);
CREATE INDEX IF NOT EXISTS ix_leads_cpf_hash ON leads (cpf_hash);

CREATE INDEX IF NOT EXISTS ix_clientes_nome ON clientes (nome);
CREATE INDEX IF NOT EXISTS ix_clientes_cpf ON clientes (cpf);
CREATE INDEX IF NOT EXISTS ix_clientes_cpf_hash ON clientes (cpf_hash);

CREATE INDEX IF NOT EXISTS ix_propostas_status ON propostas (status);
CREATE INDEX IF NOT EXISTS ix_propostas_cliente_id ON propostas (cliente_id);

CREATE INDEX IF NOT EXISTS ix_tarefas_status ON tarefas (status);
CREATE INDEX IF NOT EXISTS ix_tarefas_prioridade ON tarefas (prioridade);
CREATE INDEX IF NOT EXISTS ix_tarefas_lead_id ON tarefas (lead_id);
CREATE INDEX IF NOT EXISTS ix_tarefas_cliente_id ON tarefas (cliente_id);

CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);

CREATE INDEX IF NOT EXISTS ix_audit_logs_action ON audit_logs (action);
CREATE INDEX IF NOT EXISTS ix_audit_logs_entity_type ON audit_logs (entity_type);

CREATE INDEX IF NOT EXISTS ix_consents_customer_id ON consents (customer_id);
CREATE INDEX IF NOT EXISTS ix_consents_channel ON consents (channel);

CREATE INDEX IF NOT EXISTS ix_simulations_produto ON simulations (produto);
CREATE INDEX IF NOT EXISTS ix_simulations_payload_hash ON simulations (payload_hash);
