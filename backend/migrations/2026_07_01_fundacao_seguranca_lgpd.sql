ALTER TABLE clientes ADD COLUMN deleted_at DATETIME;

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY,
  nome VARCHAR(140) NOT NULL,
  email VARCHAR(140) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(40) NOT NULL DEFAULT 'admin',
  ativo BOOLEAN NOT NULL DEFAULT 1,
  created_at DATETIME
);

CREATE TABLE IF NOT EXISTS audit_logs (
  id INTEGER PRIMARY KEY,
  actor_user_id INTEGER,
  actor VARCHAR(140) NOT NULL DEFAULT 'system',
  action VARCHAR(100) NOT NULL,
  entity_type VARCHAR(80) NOT NULL,
  entity_id INTEGER,
  metadata_json TEXT,
  created_at DATETIME
);

CREATE TABLE IF NOT EXISTS consents (
  id INTEGER PRIMARY KEY,
  customer_id INTEGER NOT NULL REFERENCES clientes(id),
  channel VARCHAR(40) NOT NULL,
  granted BOOLEAN NOT NULL DEFAULT 1,
  source VARCHAR(120) NOT NULL DEFAULT 'demo',
  ip_address VARCHAR(80),
  created_at DATETIME,
  revoked_at DATETIME
);

CREATE TABLE IF NOT EXISTS simulations (
  id INTEGER PRIMARY KEY,
  customer_id INTEGER REFERENCES clientes(id),
  cpf_masked VARCHAR(20) NOT NULL,
  produto VARCHAR(80) NOT NULL,
  rule_id VARCHAR(80) NOT NULL,
  input_json TEXT NOT NULL,
  result_json TEXT NOT NULL,
  payload_hash VARCHAR(64) NOT NULL,
  created_at DATETIME
);
