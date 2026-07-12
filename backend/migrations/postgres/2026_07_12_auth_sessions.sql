CREATE TABLE IF NOT EXISTS auth_sessions (
  id SERIAL PRIMARY KEY,
  session_id_hash VARCHAR(64) NOT NULL UNIQUE,
  user_id INTEGER NOT NULL,
  created_at TIMESTAMPTZ,
  expires_at TIMESTAMPTZ NOT NULL,
  revoked_at TIMESTAMPTZ,
  revocation_reason VARCHAR(120),
  updated_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_auth_sessions_session_id_hash ON auth_sessions (session_id_hash);
CREATE INDEX IF NOT EXISTS ix_auth_sessions_user_id ON auth_sessions (user_id);
CREATE INDEX IF NOT EXISTS ix_auth_sessions_expires_at ON auth_sessions (expires_at);
