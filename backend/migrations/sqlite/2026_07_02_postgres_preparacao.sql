ALTER TABLE leads ADD COLUMN created_at DATETIME;
ALTER TABLE leads ADD COLUMN updated_at DATETIME;

ALTER TABLE clientes ADD COLUMN created_at DATETIME;
ALTER TABLE clientes ADD COLUMN updated_at DATETIME;

ALTER TABLE propostas ADD COLUMN created_at DATETIME;
ALTER TABLE propostas ADD COLUMN updated_at DATETIME;

ALTER TABLE tarefas ADD COLUMN created_at DATETIME;
ALTER TABLE tarefas ADD COLUMN updated_at DATETIME;

ALTER TABLE whatsapp_messages ADD COLUMN created_at DATETIME;
ALTER TABLE whatsapp_messages ADD COLUMN updated_at DATETIME;

ALTER TABLE users ADD COLUMN updated_at DATETIME;
ALTER TABLE audit_logs ADD COLUMN updated_at DATETIME;
ALTER TABLE consents ADD COLUMN updated_at DATETIME;
ALTER TABLE simulations ADD COLUMN updated_at DATETIME;
