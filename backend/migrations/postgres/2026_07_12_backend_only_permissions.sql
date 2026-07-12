-- BACKEND-ONLY permissions hardening for CRM BBB CONSIG.
-- Context: USO PROPRIO. The frontend must not access Supabase tables directly.
-- The backend connection remains the only authorized path to application data.
-- This migration does not create policies, does not enable direct frontend access,
-- and does not remove or mutate data.

REVOKE USAGE, CREATE ON SCHEMA public FROM PUBLIC, anon, authenticated;

REVOKE SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER
ON TABLE
  audit_logs,
  auth_sessions,
  backup_audit_logs,
  clientes,
  consents,
  leads,
  propostas,
  schema_migrations,
  simulations,
  tarefas,
  users,
  whatsapp_messages
FROM PUBLIC, anon, authenticated;

REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM PUBLIC, anon, authenticated;
REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM PUBLIC, anon, authenticated;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
REVOKE ALL ON TABLES FROM PUBLIC, anon, authenticated;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
REVOKE ALL ON SEQUENCES FROM PUBLIC, anon, authenticated;

