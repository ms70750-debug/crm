CREATE TABLE IF NOT EXISTS leads (
  id INTEGER PRIMARY KEY,
  nome VARCHAR(140) NOT NULL,
  cpf VARCHAR(14) NOT NULL UNIQUE,
  telefone VARCHAR(30) NOT NULL,
  email VARCHAR(140),
  origem VARCHAR(80) NOT NULL DEFAULT 'Manual',
  produto_interesse VARCHAR(80) NOT NULL DEFAULT 'INSS',
  status VARCHAR(40) NOT NULL DEFAULT 'Novo lead',
  responsavel VARCHAR(80) NOT NULL DEFAULT 'Equipe BBB',
  observacoes TEXT,
  data_criacao DATETIME,
  proximo_contato VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS clientes (
  id INTEGER PRIMARY KEY,
  nome VARCHAR(140) NOT NULL,
  cpf VARCHAR(14) NOT NULL UNIQUE,
  telefone VARCHAR(30) NOT NULL,
  email VARCHAR(140),
  data_nascimento VARCHAR(20),
  beneficio VARCHAR(40),
  convenio VARCHAR(80) NOT NULL DEFAULT 'INSS',
  banco_pagamento VARCHAR(80),
  observacoes TEXT
);

CREATE TABLE IF NOT EXISTS propostas (
  id INTEGER PRIMARY KEY,
  cliente_id INTEGER NOT NULL REFERENCES clientes(id),
  produto VARCHAR(80) NOT NULL DEFAULT 'INSS',
  banco VARCHAR(80) NOT NULL DEFAULT 'Banco simulado',
  valor_liberado FLOAT NOT NULL DEFAULT 0,
  parcela FLOAT NOT NULL DEFAULT 0,
  prazo INTEGER NOT NULL DEFAULT 84,
  status VARCHAR(40) NOT NULL DEFAULT 'Em andamento',
  data_criacao DATETIME,
  observacoes TEXT
);

CREATE TABLE IF NOT EXISTS tarefas (
  id INTEGER PRIMARY KEY,
  titulo VARCHAR(160) NOT NULL,
  descricao TEXT,
  status VARCHAR(40) NOT NULL DEFAULT 'Pendente',
  prioridade VARCHAR(20) NOT NULL DEFAULT 'Media',
  responsavel VARCHAR(80) NOT NULL DEFAULT 'Equipe BBB',
  lead_id INTEGER REFERENCES leads(id),
  cliente_id INTEGER REFERENCES clientes(id),
  data_vencimento VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS whatsapp_messages (
  id INTEGER PRIMARY KEY,
  destinatario_tipo VARCHAR(20) NOT NULL,
  destinatario_id INTEGER NOT NULL,
  telefone VARCHAR(30) NOT NULL,
  modelo VARCHAR(80) NOT NULL,
  mensagem TEXT NOT NULL,
  status VARCHAR(40) NOT NULL DEFAULT 'Registrada em simulacao',
  criado_em DATETIME
);
