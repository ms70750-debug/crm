-- Manual rollback for 2026_07_12_backend_only_permissions.sql.
-- Use only after explicit owner approval.
-- This rollback restores only the previously documented Supabase direct roles
-- on the 12 CRM tables. It does not grant privileges to PUBLIC and does not
-- change data.

GRANT USAGE ON SCHEMA public TO anon, authenticated;

GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER
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
TO anon, authenticated;

GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;

