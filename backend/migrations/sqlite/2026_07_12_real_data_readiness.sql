ALTER TABLE leads ADD COLUMN deleted_at DATETIME;
ALTER TABLE leads ADD COLUMN deleted_by INTEGER;
ALTER TABLE leads ADD COLUMN deletion_reason TEXT;
ALTER TABLE leads ADD COLUMN cpf_hash VARCHAR(64);
ALTER TABLE leads ADD COLUMN cpf_encrypted TEXT;
ALTER TABLE leads ADD COLUMN telefone_encrypted TEXT;
ALTER TABLE leads ADD COLUMN email_encrypted TEXT;

ALTER TABLE clientes ADD COLUMN deleted_by INTEGER;
ALTER TABLE clientes ADD COLUMN deletion_reason TEXT;
ALTER TABLE clientes ADD COLUMN cpf_hash VARCHAR(64);
ALTER TABLE clientes ADD COLUMN cpf_encrypted TEXT;
ALTER TABLE clientes ADD COLUMN telefone_encrypted TEXT;
ALTER TABLE clientes ADD COLUMN email_encrypted TEXT;
ALTER TABLE clientes ADD COLUMN bank_data_encrypted TEXT;

ALTER TABLE propostas ADD COLUMN deleted_at DATETIME;
ALTER TABLE propostas ADD COLUMN deleted_by INTEGER;
ALTER TABLE propostas ADD COLUMN deletion_reason TEXT;

ALTER TABLE tarefas ADD COLUMN deleted_at DATETIME;
ALTER TABLE tarefas ADD COLUMN deleted_by INTEGER;
ALTER TABLE tarefas ADD COLUMN deletion_reason TEXT;

ALTER TABLE whatsapp_messages ADD COLUMN deleted_at DATETIME;
ALTER TABLE whatsapp_messages ADD COLUMN deleted_by INTEGER;
ALTER TABLE whatsapp_messages ADD COLUMN deletion_reason TEXT;

ALTER TABLE consents ADD COLUMN deleted_at DATETIME;
ALTER TABLE consents ADD COLUMN deleted_by INTEGER;
ALTER TABLE consents ADD COLUMN deletion_reason TEXT;
ALTER TABLE consents ADD COLUMN purpose VARCHAR(120);
ALTER TABLE consents ADD COLUMN status VARCHAR(40);
ALTER TABLE consents ADD COLUMN revoked_by INTEGER;
ALTER TABLE consents ADD COLUMN metadata_json TEXT;

ALTER TABLE simulations ADD COLUMN deleted_at DATETIME;
ALTER TABLE simulations ADD COLUMN deleted_by INTEGER;
ALTER TABLE simulations ADD COLUMN deletion_reason TEXT;

CREATE TABLE IF NOT EXISTS backup_audit_logs (
  id INTEGER PRIMARY KEY,
  operation VARCHAR(40) NOT NULL,
  target VARCHAR(160) NOT NULL,
  status VARCHAR(40) NOT NULL,
  checksum VARCHAR(128),
  metadata_json TEXT,
  created_at DATETIME,
  updated_at DATETIME
);
